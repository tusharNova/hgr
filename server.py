"""
FastAPI Web Server for Gesture-Based Home Automation + Voice Assistant
Supports real-time gesture detection and voice control
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request,Response
from fastapi.responses import HTMLResponse, JSONResponse ,Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import cv2
import base64
import json
import asyncio
from datetime import datetime
from gesture_detector import GestureDetector
import uvicorn
from typing import Dict, List
import numpy as np
from queue import Queue
import urllib.request
import threading
import urllib.request
import time

# Initialize FastAPI app
app = FastAPI(
    title="Neo Smart Home Control",
    description="Control your home devices with hand gestures or voice",
    version="2.0.0"
)

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates for HTML pages
templates = Jinja2Templates(directory="templates")

# Device states (in-memory storage - SAME structure as old code)
devices = {
    "device_1": {
        "name": "Living Room Light",
        "state": False,
        "type": "light",
        "last_updated": None
    },
    "device_2": {
        "name": "Bedroom Fan",
        "state": False,
        "type": "fan",
        "last_updated": None
    },
    "device_3": {
        "name": "Kitchen Light",
        "state": False,
        "type": "light",
        "last_updated": None
    },
    "device_4": {
        "name": "TV",
        "state": False,
        "type": "tv",
        "last_updated": None
    }
}

# Current selected device
current_device = "device_1"

# Gesture detection settings
gesture_settings = {
    "enabled": True,
    "confidence": 0.7,
    "hold_time": 1.5,  # seconds to hold gesture before triggering
    "max_hands": 1
}

esp32_frame_queue = Queue(maxsize=2)
esp32_stream_active = False
esp32_stream_thread = None
esp32_stream_url = None

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()

# ==================== esp32-cam code ====================
def fetch_esp32_frames():
    """Background thread to continuously fetch frames from ESP32-CAM"""
    global esp32_stream_active, esp32_frame_queue
    
    while esp32_stream_active:
        try:
            # Open connection to ESP32-CAM MJPEG stream
            stream = urllib.request.urlopen(esp32_stream_url, timeout=5)
            bytes_data = b''
            
            while esp32_stream_active:
                bytes_data += stream.read(1024)
                a = bytes_data.find(b'\xff\xd8')  # JPEG start
                b = bytes_data.find(b'\xff\xd9')  # JPEG end
                
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    # Decode JPEG to OpenCV frame
                    nparr = np.frombuffer(jpg, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        # Queue the frame (drop old if full)
                        if esp32_frame_queue.full():
                            try:
                                esp32_frame_queue.get_nowait()
                            except:
                                pass
                        esp32_frame_queue.put(frame)
                        
        except Exception as e:
            print(f"ESP32-CAM fetch error: {e}")
            time.sleep(2)
        finally:
            try:
                stream.close()
            except:
                pass

@app.post("/api/esp32/start")
async def start_esp32_stream(request: Request):
    """Start fetching frames from ESP32-CAM"""
    global esp32_stream_active, esp32_stream_thread, esp32_stream_url
    
    data = await request.json()
    esp32_ip = data.get("ip")
    esp32_stream_url = f"http://{esp32_ip}:81/stream"
    
    if esp32_stream_active:
        esp32_stream_active = False
        if esp32_stream_thread:
            esp32_stream_thread.join(timeout=2)
    
    esp32_stream_active = True
    esp32_stream_thread = threading.Thread(target=fetch_esp32_frames)
    esp32_stream_thread.daemon = True
    esp32_stream_thread.start()
    
    return {"success": True, "message": f"ESP32-CAM stream started at {esp32_stream_url}"}

@app.post("/api/esp32/stop")
async def stop_esp32_stream():
    """Stop fetching frames from ESP32-CAM"""
    global esp32_stream_active
    esp32_stream_active = False
    return {"success": True, "message": "ESP32-CAM stream stopped"}

@app.get("/api/esp32/frame")
async def get_esp32_frame():
    """Get latest frame from ESP32-CAM"""
    global esp32_frame_queue
    
    if not esp32_frame_queue.empty():
        frame = esp32_frame_queue.get_nowait()
        _, buffer = cv2.imencode('.jpg', frame)
        return Response(buffer.tobytes(), media_type='image/jpeg')
    
    return Response(status=204)

# ==================== Web Page Routes ====================

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Landing page - choose between gesture and voice control"""
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/gesture", response_class=HTMLResponse)
async def gesture_control(request: Request):
    """Serve the gesture control interface"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/voice", response_class=HTMLResponse)
async def voice_control(request: Request):
    """Serve the voice bot interface"""
    return templates.TemplateResponse("voice_bot.html", {"request": request})


# ==================== API Routes (Original Gesture Control) ====================

# Add these routes after your existing route definitions (around line 250)

@app.get("/temperature", response_class=HTMLResponse)
async def temperature_display(request: Request):
    """Serve the temperature display page from nodeMCU/tp1.html"""
    # Read the HTML file from nodeMCU directory
    html_path = "nodeMCU/tp1.html"
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: tp1.html not found</h1>", status_code=404)

@app.get("/motion-detection", response_class=HTMLResponse)
async def motion_detection(request: Request):
    """Serve the motion detection page from nodeMCU/new_motion_code.html"""
    # Read the HTML file from nodeMCU directory
    html_path = "nodeMCU/new_motion_code.html"
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: new_motion_code.html not found</h1>", status_code=404)

@app.get("/api/devices")
async def get_devices():
    """Get all devices and their states"""
    return {
        "success": True,
        "devices": devices,
        "current_device": current_device
    }


@app.get("/api/devices/{device_id}")
async def get_device(device_id: str):
    """Get specific device information"""
    if device_id not in devices:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Device not found"}
        )
    
    return {
        "success": True,
        "device": devices[device_id]
    }


@app.post("/api/devices/{device_id}/toggle")
async def toggle_device(device_id: str):
    """Toggle device ON/OFF"""
    if device_id not in devices:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Device not found"}
        )
    
    # Toggle state
    devices[device_id]["state"] = not devices[device_id]["state"]
    devices[device_id]["last_updated"] = datetime.now().isoformat()
    
    # Broadcast update to all clients
    await manager.broadcast({
        "type": "device_update",
        "device_id": device_id,
        "device": devices[device_id]
    })
    
    print(f"Device {device_id} toggled to {'ON' if devices[device_id]['state'] else 'OFF'}")
    
    return {
        "success": True,
        "device": devices[device_id]
    }


@app.post("/api/devices/{device_id}/state")
async def set_device_state(device_id: str, request: Request):
    """Set device state (ON/OFF)"""
    if device_id not in devices:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Device not found"}
        )
    
    data = await request.json()
    state = data.get("state", False)
    
    devices[device_id]["state"] = state
    devices[device_id]["last_updated"] = datetime.now().isoformat()
    
    # Broadcast update to all clients
    await manager.broadcast({
        "type": "device_update",
        "device_id": device_id,
        "device": devices[device_id]
    })
    
    return {
        "success": True,
        "device": devices[device_id]
    }


@app.post("/api/select-device/{device_id}")
async def select_device(device_id: str):
    """Select which device to control"""
    global current_device
    
    if device_id not in devices:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "Device not found"}
        )
    
    current_device = device_id
    
    # Broadcast selection to all clients
    await manager.broadcast({
        "type": "device_selected",
        "device_id": device_id
    })
    
    return {
        "success": True,
        "current_device": current_device
    }


@app.get("/api/settings")
async def get_settings():
    """Get gesture detection settings"""
    return {
        "success": True,
        "settings": gesture_settings
    }


@app.post("/api/settings")
async def update_settings(request: Request):
    """Update gesture detection settings"""
    data = await request.json()
    
    if "enabled" in data:
        gesture_settings["enabled"] = data["enabled"]
    if "confidence" in data:
        gesture_settings["confidence"] = data["confidence"]
    if "hold_time" in data:
        gesture_settings["hold_time"] = data["hold_time"]
    
    return {
        "success": True,
        "settings": gesture_settings
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_devices": len(devices),
        "active_connections": len(manager.active_connections)
    }


# ==================== NEW API Routes for Voice Bot ====================

@app.post("/api/control")
async def control_device_voice(request: Request):
    """Control device via voice (new endpoint for voice bot)"""
    data = await request.json()
    device_num = data.get("device_id")  # 1, 2, 3, 4
    action = data.get("action")  # "on" or "off"
    
    device_id = f"device_{device_num}"
    
    if device_id not in devices:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Device not found"}
        )
    
    # Set device state
    new_state = (action == "on")
    devices[device_id]["state"] = new_state
    devices[device_id]["last_updated"] = datetime.now().isoformat()
    
    # Broadcast update to all clients
    await manager.broadcast({
        "type": "device_update",
        "device_id": device_id,
        "device": devices[device_id]
    })
    
    print(f"Voice command: Device {device_num} turned {action}")
    
    return {
        "success": True,
        "device_id": device_num,
        "state": action,
        "message": f"Device {device_num} turned {action}"
    }


# ==================== WebSocket for Gesture Detection (ORIGINAL) ====================

@app.websocket("/ws/gesture")
async def websocket_gesture_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time gesture detection
    Receives video frames from client and sends back detection results
    """
    await manager.connect(websocket)
    
    # Initialize gesture detector for this connection
    detector = GestureDetector(
        max_num_hands=gesture_settings["max_hands"],
        min_detection_confidence=gesture_settings["confidence"],
        min_tracking_confidence=gesture_settings["confidence"]
    )
    
    last_gesture = None
    gesture_start_time = None
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "frame":
                # Decode base64 image
                image_data = base64.b64decode(message["data"].split(",")[1])
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Detect hands
                    frame, results = detector.find_hands(frame, draw=False)
                    landmarks = detector.get_hand_landmarks(frame, results, hand_number=0)
                    
                    # Detect gesture
                    gesture = detector.detect_gesture(landmarks)
                    finger_count = detector.count_fingers(landmarks) if len(landmarks) > 0 else 0
                    
                    # Prepare response
                    response = {
                        "type": "gesture_result",
                        "gesture": gesture,
                        "finger_count": finger_count,
                        "hand_detected": len(landmarks) > 0,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Handle device selection (1-4 fingers)
                    global current_device
                    if finger_count in [1, 2, 3, 4]:
                        device_key = f"device_{finger_count}"
                        if device_key in devices and current_device != device_key:
                            current_device = device_key
                            response["device_selected"] = current_device
                            
                            # Broadcast to all clients
                            await manager.broadcast({
                                "type": "device_selected",
                                "device_id": current_device
                            })
                    
                    # Handle gesture hold for ON/OFF commands
                    if gesture in ["FIST (OFF)", "OPEN PALM (ON)"]:
                        if gesture == last_gesture:
                            # Calculate hold duration
                            hold_duration = (datetime.now() - gesture_start_time).total_seconds()
                            response["hold_duration"] = hold_duration
                            
                            # Trigger action if held long enough
                            if hold_duration >= gesture_settings["hold_time"]:
                                if gesture == "OPEN PALM (ON)":
                                    devices[current_device]["state"] = True
                                    action = "turned_on"
                                elif gesture == "FIST (OFF)":
                                    devices[current_device]["state"] = False
                                    action = "turned_off"
                                
                                devices[current_device]["last_updated"] = datetime.now().isoformat()
                                
                                response["action_triggered"] = action
                                response["device_id"] = current_device
                                
                                # Broadcast device update
                                await manager.broadcast({
                                    "type": "device_update",
                                    "device_id": current_device,
                                    "device": devices[current_device]
                                })
                                
                                # Reset gesture
                                gesture_start_time = datetime.now()
                        else:
                            # New gesture detected
                            last_gesture = gesture
                            gesture_start_time = datetime.now()
                    else:
                        last_gesture = None
                        gesture_start_time = None
                    
                    # Send response back to client
                    await websocket.send_json(response)
            
            elif message["type"] == "ping":
                # Keep-alive ping
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        detector.close()
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        detector.close()
#=======================for Esp32-cam ==================================

@app.get("/gesture-esp32", response_class=HTMLResponse)
async def gesture_control_esp32(request: Request):
    """Serve the ESP32-CAM gesture control interface"""
    return templates.TemplateResponse("gesture_esp32.html", {"request": request})

# ==================== WebSocket for Voice Bot (NEW) ====================

@app.websocket("/ws")
async def websocket_voice_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for voice bot
    Sends device updates in real-time
    """
    await manager.connect(websocket)
    
    try:
        # Send current device states to voice bot client
        device_list = [
            {
                "id": int(key.split("_")[1]),
                "name": value["name"],
                "type": value["type"].capitalize(),
                "icon": {"light": "💡", "fan": "🌀", "tv": "📺"}.get(value["type"], "🔌"),
                "state": "on" if value["state"] else "off"
            }
            for key, value in devices.items()
        ]
        
        await websocket.send_json({
            "type": "devices",
            "devices": device_list
        })
        print(f"Sent {len(device_list)} devices to voice bot client")
        
        # Main message loop
        while True:
            try:
                # Receive data from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "control":
                    # Voice bot sent a control command
                    device_num = message["device_id"]
                    device_id = f"device_{device_num}"
                    action = message["action"]
                    
                    if device_id in devices:
                        devices[device_id]["state"] = (action == "on")
                        devices[device_id]["last_updated"] = datetime.now().isoformat()
                        
                        print(f"Voice control: Device {device_num} → {action}")
                        
                        # Broadcast update to all clients
                        await manager.broadcast({
                            "type": "device_update",
                            "device_id": device_num,
                            "state": action
                        })
                        
                        await websocket.send_json({
                            "success": True,
                            "device_id": device_num,
                            "state": action
                        })
                    else:
                        await websocket.send_json({
                            "success": False,
                            "error": f"Device {device_num} not found"
                        })
                    
                elif message.get("type") == "ping":
                    # Keep-alive ping
                    await websocket.send_json({"type": "pong"})
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                continue
    
    except WebSocketDisconnect:
        print("Voice bot WebSocket disconnected normally")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Voice bot WebSocket error: {e}")
        manager.disconnect(websocket)


# ==================== Startup Event ====================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("\n" + "="*60)
    print("🚀 NEO SMART HOME CONTROL SERVER")
    print("="*60)
    print(f"📡 Server starting...")
    print(f"🏠 Total devices: {len(devices)}")
    print(f"⚙️  Gesture detection: {'Enabled' if gesture_settings['enabled'] else 'Disabled'}")
    print(f"🎤 Voice assistant: Enabled")
    print("\n📱 Access Points:")
    print(f"   Landing Page:     http://localhost:8000")
    print(f"   Gesture Control:  http://localhost:8000/gesture")
    print(f"   Voice Assistant:  http://localhost:8000/voice")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\n" + "="*60)
    print("🛑 Server shutting down...")
    print("="*60 + "\n")


# ==================== Run Server ====================

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )