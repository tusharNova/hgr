# # """
# # FastAPI Web Server for Gesture-Based Home Automation
# # Supports real-time gesture detection via WebSocket
# # """

# # from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
# # from fastapi.responses import HTMLResponse, JSONResponse
# # from fastapi.staticfiles import StaticFiles
# # from fastapi.templating import Jinja2Templates
# # import cv2
# # import base64
# # import json
# # import asyncio
# # from datetime import datetime
# # from gesture_detector import GestureDetector
# # import uvicorn
# # from typing import Dict, List
# # import numpy as np

# # # Initialize FastAPI app
# # app = FastAPI(
# #     title="Gesture Control Home Automation",
# #     description="Control your home devices with hand gestures",
# #     version="1.0.0"
# # )

# # # Mount static files (CSS, JS, images)
# # app.mount("/static", StaticFiles(directory="static"), name="static")

# # # Templates for HTML pages
# # templates = Jinja2Templates(directory="templates")

# # # Store connected WebSocket clients
# # active_connections: List[WebSocket] = []

# # # Device states (in-memory storage for now)
# # devices = {
# #     "device_1": {
# #         "name": "Living Room Light",
# #         "state": False,
# #         "type": "light",
# #         "last_updated": None
# #     },
# #     "device_2": {
# #         "name": "Bedroom Fan",
# #         "state": False,
# #         "type": "fan",
# #         "last_updated": None
# #     },
# #     "device_3": {
# #         "name": "Kitchen Light",
# #         "state": False,
# #         "type": "light",
# #         "last_updated": None
# #     },
# #     "device_4": {
# #         "name": "TV",
# #         "state": False,
# #         "type": "tv",
# #         "last_updated": None
# #     }
# # }

# # # Current selected device
# # current_device = "device_1"

# # # Gesture detection settings
# # gesture_settings = {
# #     "enabled": True,
# #     "confidence": 0.7,
# #     "hold_time": 1.5,  # seconds to hold gesture before triggering
# #     "max_hands": 1
# # }

# # # Initialize gesture detector (will be created per connection)
# # gesture_detector = None


# # class ConnectionManager:
# #     """Manage WebSocket connections"""
    
# #     def __init__(self):
# #         self.active_connections: List[WebSocket] = []
    
# #     async def connect(self, websocket: WebSocket):
# #         await websocket.accept()
# #         self.active_connections.append(websocket)
# #         print(f"Client connected. Total connections: {len(self.active_connections)}")
    
# #     def disconnect(self, websocket: WebSocket):
# #         self.active_connections.remove(websocket)
# #         print(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
# #     async def broadcast(self, message: dict):
# #         """Send message to all connected clients"""
# #         for connection in self.active_connections:
# #             try:
# #                 await connection.send_json(message)
# #             except:
# #                 pass


# # manager = ConnectionManager()


# # # ==================== API Routes ====================

# # @app.get("/", response_class=HTMLResponse)
# # async def home(request: Request):
# #     """Serve the main web interface"""
# #     return templates.TemplateResponse("index.html", {"request": request})


# # @app.get("/api/devices")
# # async def get_devices():
# #     """Get all devices and their states"""
# #     return {
# #         "success": True,
# #         "devices": devices,
# #         "current_device": current_device
# #     }


# # @app.get("/api/devices/{device_id}")
# # async def get_device(device_id: str):
# #     """Get specific device information"""
# #     if device_id not in devices:
# #         return JSONResponse(
# #             status_code=404,
# #             content={"success": False, "message": "Device not found"}
# #         )
    
# #     return {
# #         "success": True,
# #         "device": devices[device_id]
# #     }


# # @app.post("/api/devices/{device_id}/toggle")
# # async def toggle_device(device_id: str):
# #     """Toggle device ON/OFF"""
# #     if device_id not in devices:
# #         return JSONResponse(
# #             status_code=404,
# #             content={"success": False, "message": "Device not found"}
# #         )
    
# #     # Toggle state
# #     devices[device_id]["state"] = not devices[device_id]["state"]
# #     devices[device_id]["last_updated"] = datetime.now().isoformat()
    
# #     # Broadcast update to all clients
# #     await manager.broadcast({
# #         "type": "device_update",
# #         "device_id": device_id,
# #         "device": devices[device_id]
# #     })
    
# #     print(f"Device {device_id} toggled to {'ON' if devices[device_id]['state'] else 'OFF'}")
    
# #     return {
# #         "success": True,
# #         "device": devices[device_id]
# #     }


# # @app.post("/api/devices/{device_id}/state")
# # async def set_device_state(device_id: str, request: Request):
# #     """Set device state (ON/OFF)"""
# #     if device_id not in devices:
# #         return JSONResponse(
# #             status_code=404,
# #             content={"success": False, "message": "Device not found"}
# #         )
    
# #     data = await request.json()
# #     state = data.get("state", False)
    
# #     devices[device_id]["state"] = state
# #     devices[device_id]["last_updated"] = datetime.now().isoformat()
    
# #     # Broadcast update to all clients
# #     await manager.broadcast({
# #         "type": "device_update",
# #         "device_id": device_id,
# #         "device": devices[device_id]
# #     })
    
# #     return {
# #         "success": True,
# #         "device": devices[device_id]
# #     }


# # @app.post("/api/select-device/{device_id}")
# # async def select_device(device_id: str):
# #     """Select which device to control"""
# #     global current_device
    
# #     if device_id not in devices:
# #         return JSONResponse(
# #             status_code=404,
# #             content={"success": False, "message": "Device not found"}
# #         )
    
# #     current_device = device_id
    
# #     # Broadcast selection to all clients
# #     await manager.broadcast({
# #         "type": "device_selected",
# #         "device_id": device_id
# #     })
    
# #     return {
# #         "success": True,
# #         "current_device": current_device
# #     }


# # @app.get("/api/settings")
# # async def get_settings():
# #     """Get gesture detection settings"""
# #     return {
# #         "success": True,
# #         "settings": gesture_settings
# #     }


# # @app.post("/api/settings")
# # async def update_settings(request: Request):
# #     """Update gesture detection settings"""
# #     data = await request.json()
    
# #     if "enabled" in data:
# #         gesture_settings["enabled"] = data["enabled"]
# #     if "confidence" in data:
# #         gesture_settings["confidence"] = data["confidence"]
# #     if "hold_time" in data:
# #         gesture_settings["hold_time"] = data["hold_time"]
    
# #     return {
# #         "success": True,
# #         "settings": gesture_settings
# #     }


# # @app.get("/api/health")
# # async def health_check():
# #     """Health check endpoint"""
# #     return {
# #         "status": "healthy",
# #         "timestamp": datetime.now().isoformat(),
# #         "total_devices": len(devices),
# #         "active_connections": len(manager.active_connections)
# #     }


# # # ==================== WebSocket for Real-time Gesture Detection ====================

# # @app.websocket("/ws/gesture")
# # async def websocket_gesture_endpoint(websocket: WebSocket):
# #     """
# #     WebSocket endpoint for real-time gesture detection
# #     Receives video frames from client and sends back detection results
# #     """
# #     await manager.connect(websocket)
    
# #     # Initialize gesture detector for this connection
# #     detector = GestureDetector(
# #         max_num_hands=gesture_settings["max_hands"],
# #         min_detection_confidence=gesture_settings["confidence"],
# #         min_tracking_confidence=gesture_settings["confidence"]
# #     )
    
# #     last_gesture = None
# #     gesture_start_time = None
    
# #     try:
# #         while True:
# #             # Receive data from client
# #             data = await websocket.receive_text()
# #             message = json.loads(data)
            
# #             if message["type"] == "frame":
# #                 # Decode base64 image
# #                 image_data = base64.b64decode(message["data"].split(",")[1])
# #                 nparr = np.frombuffer(image_data, np.uint8)
# #                 frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
# #                 if frame is not None:
# #                     # Detect hands
# #                     frame, results = detector.find_hands(frame, draw=False)
# #                     landmarks = detector.get_hand_landmarks(frame, results, hand_number=0)
                    
# #                     # Detect gesture
# #                     gesture = detector.detect_gesture(landmarks)
# #                     finger_count = detector.count_fingers(landmarks) if len(landmarks) > 0 else 0
                    
# #                     # Prepare response
# #                     response = {
# #                         "type": "gesture_result",
# #                         "gesture": gesture,
# #                         "finger_count": finger_count,
# #                         "hand_detected": len(landmarks) > 0,
# #                         "timestamp": datetime.now().isoformat()
# #                     }
                    
# #                     # Handle device selection (1-4 fingers)
# #                     global current_device
# #                     if finger_count in [1, 2, 3, 4]:
# #                         device_key = f"device_{finger_count}"
# #                         if device_key in devices and current_device != device_key:
# #                             current_device = device_key
# #                             response["device_selected"] = current_device
                            
# #                             # Broadcast to all clients
# #                             await manager.broadcast({
# #                                 "type": "device_selected",
# #                                 "device_id": current_device
# #                             })
                    
# #                     # Handle gesture hold for ON/OFF commands
# #                     if gesture in ["FIST (OFF)", "OPEN PALM (ON)"]:
# #                         if gesture == last_gesture:
# #                             # Calculate hold duration
# #                             hold_duration = (datetime.now() - gesture_start_time).total_seconds()
# #                             response["hold_duration"] = hold_duration
                            
# #                             # Trigger action if held long enough
# #                             if hold_duration >= gesture_settings["hold_time"]:
# #                                 if gesture == "OPEN PALM (ON)":
# #                                     devices[current_device]["state"] = True
# #                                     action = "turned_on"
# #                                 elif gesture == "FIST (OFF)":
# #                                     devices[current_device]["state"] = False
# #                                     action = "turned_off"
                                
# #                                 devices[current_device]["last_updated"] = datetime.now().isoformat()
                                
# #                                 response["action_triggered"] = action
# #                                 response["device_id"] = current_device
                                
# #                                 # Broadcast device update
# #                                 await manager.broadcast({
# #                                     "type": "device_update",
# #                                     "device_id": current_device,
# #                                     "device": devices[current_device]
# #                                 })
                                
# #                                 # Reset gesture
# #                                 gesture_start_time = datetime.now()
# #                         else:
# #                             # New gesture detected
# #                             last_gesture = gesture
# #                             gesture_start_time = datetime.now()
# #                     else:
# #                         last_gesture = None
# #                         gesture_start_time = None
                    
# #                     # Send response back to client
# #                     await websocket.send_json(response)
            
# #             elif message["type"] == "ping":
# #                 # Keep-alive ping
# #                 await websocket.send_json({"type": "pong"})
    
# #     except WebSocketDisconnect:
# #         manager.disconnect(websocket)
# #         detector.close()
# #     except Exception as e:
# #         print(f"WebSocket error: {e}")
# #         manager.disconnect(websocket)
# #         detector.close()


# # # ==================== Startup Event ====================

# # @app.on_event("startup")
# # async def startup_event():
# #     """Run on application startup"""
# #     print("\n" + "="*60)
# #     print("🚀 GESTURE CONTROL HOME AUTOMATION SERVER")
# #     print("="*60)
# #     print(f"📡 Server starting...")
# #     print(f"🏠 Total devices: {len(devices)}")
# #     print(f"⚙️  Gesture detection: {'Enabled' if gesture_settings['enabled'] else 'Disabled'}")
# #     print("="*60 + "\n")


# # @app.on_event("shutdown")
# # async def shutdown_event():
# #     """Run on application shutdown"""
# #     print("\n" + "="*60)
# #     print("🛑 Server shutting down...")
# #     print("="*60 + "\n")


# # # ==================== Run Server ====================

# # if __name__ == "__main__":
# #     uvicorn.run(
# #         "server:app",
# #         host="0.0.0.0",
# #         port=8000,
# #         reload=True,  # Auto-reload on code changes
# #         log_level="info"
# #     )

# """
# FastAPI Web Server for Gesture-Based Home Automation + Voice Assistant
# Supports real-time gesture detection and voice control
# """

# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# import cv2
# import base64
# import json
# import asyncio
# from datetime import datetime
# from gesture_detector import GestureDetector
# import uvicorn
# from typing import Dict, List
# import numpy as np

# # Initialize FastAPI app
# app = FastAPI(
#     title="Neo Smart Home Control",
#     description="Control your home devices with hand gestures or voice",
#     version="2.0.0"
# )

# # Mount static files (CSS, JS, images)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Templates for HTML pages
# templates = Jinja2Templates(directory="templates")

# # Device states (in-memory storage - SAME structure as old code)
# devices = {
#     "device_1": {
#         "name": "Living Room Light",
#         "state": False,
#         "type": "light",
#         "last_updated": None
#     },
#     "device_2": {
#         "name": "Bedroom Fan",
#         "state": False,
#         "type": "fan",
#         "last_updated": None
#     },
#     "device_3": {
#         "name": "Kitchen Light",
#         "state": False,
#         "type": "light",
#         "last_updated": None
#     },
#     "device_4": {
#         "name": "TV",
#         "state": False,
#         "type": "tv",
#         "last_updated": None
#     }
# }

# # Current selected device
# current_device = "device_1"

# # Gesture detection settings
# gesture_settings = {
#     "enabled": True,
#     "confidence": 0.7,
#     "hold_time": 1.5,  # seconds to hold gesture before triggering
#     "max_hands": 1
# }


# class ConnectionManager:
#     """Manage WebSocket connections"""
    
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []
    
#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)
#         print(f"Client connected. Total connections: {len(self.active_connections)}")
    
#     def disconnect(self, websocket: WebSocket):
#         if websocket in self.active_connections:
#             self.active_connections.remove(websocket)
#         print(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
#     async def broadcast(self, message: dict):
#         """Send message to all connected clients"""
#         for connection in self.active_connections:
#             try:
#                 await connection.send_json(message)
#             except:
#                 pass


# manager = ConnectionManager()


# # ==================== Web Page Routes ====================

# @app.get("/", response_class=HTMLResponse)
# async def landing_page(request: Request):
#     """Landing page - choose between gesture and voice control"""
#     return templates.TemplateResponse("landing.html", {"request": request})


# @app.get("/gesture", response_class=HTMLResponse)
# async def gesture_control(request: Request):
#     """Serve the gesture control interface"""
#     return templates.TemplateResponse("index.html", {"request": request})


# @app.get("/voice", response_class=HTMLResponse)
# async def voice_control(request: Request):
#     """Serve the voice bot interface"""
#     return templates.TemplateResponse("voice_bot.html", {"request": request})


# # ==================== API Routes (Original Gesture Control) ====================

# @app.get("/api/devices")
# async def get_devices():
#     """Get all devices and their states"""
#     return {
#         "success": True,
#         "devices": devices,
#         "current_device": current_device
#     }


# @app.get("/api/devices/{device_id}")
# async def get_device(device_id: str):
#     """Get specific device information"""
#     if device_id not in devices:
#         return JSONResponse(
#             status_code=404,
#             content={"success": False, "message": "Device not found"}
#         )
    
#     return {
#         "success": True,
#         "device": devices[device_id]
#     }


# @app.post("/api/devices/{device_id}/toggle")
# async def toggle_device(device_id: str):
#     """Toggle device ON/OFF"""
#     if device_id not in devices:
#         return JSONResponse(
#             status_code=404,
#             content={"success": False, "message": "Device not found"}
#         )
    
#     # Toggle state
#     devices[device_id]["state"] = not devices[device_id]["state"]
#     devices[device_id]["last_updated"] = datetime.now().isoformat()
    
#     # Broadcast update to all clients
#     await manager.broadcast({
#         "type": "device_update",
#         "device_id": device_id,
#         "device": devices[device_id]
#     })
    
#     print(f"Device {device_id} toggled to {'ON' if devices[device_id]['state'] else 'OFF'}")
    
#     return {
#         "success": True,
#         "device": devices[device_id]
#     }


# @app.post("/api/devices/{device_id}/state")
# async def set_device_state(device_id: str, request: Request):
#     """Set device state (ON/OFF)"""
#     if device_id not in devices:
#         return JSONResponse(
#             status_code=404,
#             content={"success": False, "message": "Device not found"}
#         )
    
#     data = await request.json()
#     state = data.get("state", False)
    
#     devices[device_id]["state"] = state
#     devices[device_id]["last_updated"] = datetime.now().isoformat()
    
#     # Broadcast update to all clients
#     await manager.broadcast({
#         "type": "device_update",
#         "device_id": device_id,
#         "device": devices[device_id]
#     })
    
#     return {
#         "success": True,
#         "device": devices[device_id]
#     }


# @app.post("/api/select-device/{device_id}")
# async def select_device(device_id: str):
#     """Select which device to control"""
#     global current_device
    
#     if device_id not in devices:
#         return JSONResponse(
#             status_code=404,
#             content={"success": False, "message": "Device not found"}
#         )
    
#     current_device = device_id
    
#     # Broadcast selection to all clients
#     await manager.broadcast({
#         "type": "device_selected",
#         "device_id": device_id
#     })
    
#     return {
#         "success": True,
#         "current_device": current_device
#     }


# @app.get("/api/settings")
# async def get_settings():
#     """Get gesture detection settings"""
#     return {
#         "success": True,
#         "settings": gesture_settings
#     }


# @app.post("/api/settings")
# async def update_settings(request: Request):
#     """Update gesture detection settings"""
#     data = await request.json()
    
#     if "enabled" in data:
#         gesture_settings["enabled"] = data["enabled"]
#     if "confidence" in data:
#         gesture_settings["confidence"] = data["confidence"]
#     if "hold_time" in data:
#         gesture_settings["hold_time"] = data["hold_time"]
    
#     return {
#         "success": True,
#         "settings": gesture_settings
#     }


# @app.get("/api/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "timestamp": datetime.now().isoformat(),
#         "total_devices": len(devices),
#         "active_connections": len(manager.active_connections)
#     }


# # ==================== NEW API Routes for Voice Bot ====================

# @app.post("/api/control")
# async def control_device_voice(request: Request):
#     """Control device via voice (new endpoint for voice bot)"""
#     data = await request.json()
#     device_num = data.get("device_id")  # 1, 2, 3, 4
#     action = data.get("action")  # "on" or "off"
    
#     device_id = f"device_{device_num}"
    
#     if device_id not in devices:
#         return JSONResponse(
#             status_code=404,
#             content={"success": False, "error": "Device not found"}
#         )
    
#     # Set device state
#     new_state = (action == "on")
#     devices[device_id]["state"] = new_state
#     devices[device_id]["last_updated"] = datetime.now().isoformat()
    
#     # Broadcast update to all clients
#     await manager.broadcast({
#         "type": "device_update",
#         "device_id": device_id,
#         "device": devices[device_id]
#     })
    
#     print(f"Voice command: Device {device_num} turned {action}")
    
#     return {
#         "success": True,
#         "device_id": device_num,
#         "state": action,
#         "message": f"Device {device_num} turned {action}"
#     }


# # ==================== WebSocket for Gesture Detection (ORIGINAL) ====================

# @app.websocket("/ws/gesture")
# async def websocket_gesture_endpoint(websocket: WebSocket):
#     """
#     WebSocket endpoint for real-time gesture detection
#     Receives video frames from client and sends back detection results
#     """
#     await manager.connect(websocket)
    
#     # Initialize gesture detector for this connection
#     detector = GestureDetector(
#         max_num_hands=gesture_settings["max_hands"],
#         min_detection_confidence=gesture_settings["confidence"],
#         min_tracking_confidence=gesture_settings["confidence"]
#     )
    
#     last_gesture = None
#     gesture_start_time = None
    
#     try:
#         while True:
#             # Receive data from client
#             data = await websocket.receive_text()
#             message = json.loads(data)
            
#             if message["type"] == "frame":
#                 # Decode base64 image
#                 image_data = base64.b64decode(message["data"].split(",")[1])
#                 nparr = np.frombuffer(image_data, np.uint8)
#                 frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
#                 if frame is not None:
#                     # Detect hands
#                     frame, results = detector.find_hands(frame, draw=False)
#                     landmarks = detector.get_hand_landmarks(frame, results, hand_number=0)
                    
#                     # Detect gesture
#                     gesture = detector.detect_gesture(landmarks)
#                     finger_count = detector.count_fingers(landmarks) if len(landmarks) > 0 else 0
                    
#                     # Prepare response
#                     response = {
#                         "type": "gesture_result",
#                         "gesture": gesture,
#                         "finger_count": finger_count,
#                         "hand_detected": len(landmarks) > 0,
#                         "timestamp": datetime.now().isoformat()
#                     }
                    
#                     # Handle device selection (1-4 fingers)
#                     global current_device
#                     if finger_count in [1, 2, 3, 4]:
#                         device_key = f"device_{finger_count}"
#                         if device_key in devices and current_device != device_key:
#                             current_device = device_key
#                             response["device_selected"] = current_device
                            
#                             # Broadcast to all clients
#                             await manager.broadcast({
#                                 "type": "device_selected",
#                                 "device_id": current_device
#                             })
                    
#                     # Handle gesture hold for ON/OFF commands
#                     if gesture in ["FIST (OFF)", "OPEN PALM (ON)"]:
#                         if gesture == last_gesture:
#                             # Calculate hold duration
#                             hold_duration = (datetime.now() - gesture_start_time).total_seconds()
#                             response["hold_duration"] = hold_duration
                            
#                             # Trigger action if held long enough
#                             if hold_duration >= gesture_settings["hold_time"]:
#                                 if gesture == "OPEN PALM (ON)":
#                                     devices[current_device]["state"] = True
#                                     action = "turned_on"
#                                 elif gesture == "FIST (OFF)":
#                                     devices[current_device]["state"] = False
#                                     action = "turned_off"
                                
#                                 devices[current_device]["last_updated"] = datetime.now().isoformat()
                                
#                                 response["action_triggered"] = action
#                                 response["device_id"] = current_device
                                
#                                 # Broadcast device update
#                                 await manager.broadcast({
#                                     "type": "device_update",
#                                     "device_id": current_device,
#                                     "device": devices[current_device]
#                                 })
                                
#                                 # Reset gesture
#                                 gesture_start_time = datetime.now()
#                         else:
#                             # New gesture detected
#                             last_gesture = gesture
#                             gesture_start_time = datetime.now()
#                     else:
#                         last_gesture = None
#                         gesture_start_time = None
                    
#                     # Send response back to client
#                     await websocket.send_json(response)
            
#             elif message["type"] == "ping":
#                 # Keep-alive ping
#                 await websocket.send_json({"type": "pong"})
    
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         detector.close()
#     except Exception as e:
#         print(f"WebSocket error: {e}")
#         manager.disconnect(websocket)
#         detector.close()


# # ==================== WebSocket for Voice Bot (NEW) ====================

# @app.websocket("/ws")
# async def websocket_voice_endpoint(websocket: WebSocket):
#     """
#     WebSocket endpoint for voice bot
#     Sends device updates in real-time
#     """
#     await manager.connect(websocket)
    
#     # Send current device states to voice bot client
#     await websocket.send_json({
#         "type": "devices",
#         "devices": [
#             {
#                 "id": int(key.split("_")[1]),
#                 "name": f"Device {key.split('_')[1]}",
#                 "type": value["type"].capitalize(),
#                 "icon": {"light": "💡", "fan": "🌀", "tv": "📺"}.get(value["type"], "🔌"),
#                 "state": "on" if value["state"] else "off"
#             }
#             for key, value in devices.items()
#         ]
#     })
    
#     try:
#         while True:
#             # Receive data from client
#             data = await websocket.receive_text()
#             message = json.loads(data)
            
#             # Handle different message types
#             if message.get("type") == "control":
#                 # Voice bot sent a control command
#                 device_num = message["device_id"]
#                 device_id = f"device_{device_num}"
#                 action = message["action"]
                
#                 if device_id in devices:
#                     devices[device_id]["state"] = (action == "on")
#                     devices[device_id]["last_updated"] = datetime.now().isoformat()
                    
#                     # Broadcast update
#                     await manager.broadcast({
#                         "type": "device_update",
#                         "device_id": device_num,
#                         "state": action
#                     })
                    
#                     await websocket.send_json({
#                         "success": True,
#                         "device_id": device_num,
#                         "state": action
#                     })
                
#             elif message.get("type") == "ping":
#                 # Keep-alive ping
#                 await websocket.send_json({"type": "pong"})
    
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#     except Exception as e:
#         print(f"WebSocket error: {e}")
#         manager.disconnect(websocket)


# # ==================== Startup Event ====================

# @app.on_event("startup")
# async def startup_event():
#     """Run on application startup"""
#     print("\n" + "="*60)
#     print("🚀 NEO SMART HOME CONTROL SERVER")
#     print("="*60)
#     print(f"📡 Server starting...")
#     print(f"🏠 Total devices: {len(devices)}")
#     print(f"⚙️  Gesture detection: {'Enabled' if gesture_settings['enabled'] else 'Disabled'}")
#     print(f"🎤 Voice assistant: Enabled")
#     print("\n📱 Access Points:")
#     print(f"   Landing Page:     http://localhost:8000")
#     print(f"   Gesture Control:  http://localhost:8000/gesture")
#     print(f"   Voice Assistant:  http://localhost:8000/voice")
#     print("="*60 + "\n")


# @app.on_event("shutdown")
# async def shutdown_event():
#     """Run on application shutdown"""
#     print("\n" + "="*60)
#     print("🛑 Server shutting down...")
#     print("="*60 + "\n")


# # ==================== Run Server ====================

# if __name__ == "__main__":
#     uvicorn.run(
#         "server:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,  # Auto-reload on code changes
#         log_level="info"
#     )

"""
FastAPI Web Server for Gesture-Based Home Automation + Voice Assistant
Supports real-time gesture detection and voice control
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
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