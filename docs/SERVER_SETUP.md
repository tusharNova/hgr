# FastAPI Web Server - Setup Guide

## 📁 Project Structure

```
gesture-control-automation/
├── server.py              # Main FastAPI server
├── gesture_detector.py    # Gesture detection module
├── run_server.py         # Server startup script
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── static/
│   └── app.js           # Frontend JavaScript
├── test_gesture.py      # Testing scripts
└── README.md            # This file
```

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Server

**Option A - Using startup script (Recommended):**
```bash
python run_server.py
```

**Option B - Direct uvicorn:**
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Access the Web Interface

Open your browser and go to:
- **Local:** http://localhost:8000
- **From network:** http://YOUR_IP:8000

## 🌐 API Endpoints

### Device Management

#### Get All Devices
```
GET /api/devices
```

**Response:**
```json
{
  "success": true,
  "devices": {
    "device_1": {
      "name": "Living Room Light",
      "state": false,
      "type": "light",
      "last_updated": null
    }
  },
  "current_device": "device_1"
}
```

#### Get Single Device
```
GET /api/devices/{device_id}
```

#### Toggle Device
```
POST /api/devices/{device_id}/toggle
```

#### Set Device State
```
POST /api/devices/{device_id}/state
Content-Type: application/json

{
  "state": true
}
```

#### Select Device
```
POST /api/select-device/{device_id}
```

### Settings

#### Get Settings
```
GET /api/settings
```

#### Update Settings
```
POST /api/settings
Content-Type: application/json

{
  "enabled": true,
  "confidence": 0.7,
  "hold_time": 1.5
}
```

### Health Check
```
GET /api/health
```

## 🔌 WebSocket Connection

### Endpoint
```
ws://localhost:8000/ws/gesture
```

### Usage Flow

1. **Client → Server (Send Frame):**
```javascript
{
  "type": "frame",
  "data": "data:image/jpeg;base64,..."
}
```

2. **Server → Client (Gesture Result):**
```javascript
{
  "type": "gesture_result",
  "gesture": "OPEN PALM (ON)",
  "finger_count": 5,
  "hand_detected": true,
  "timestamp": "2026-02-03T12:00:00",
  "hold_duration": 1.2,
  "action_triggered": "turned_on",
  "device_id": "device_1"
}
```

3. **Server → Client (Device Update Broadcast):**
```javascript
{
  "type": "device_update",
  "device_id": "device_1",
  "device": {
    "name": "Living Room Light",
    "state": true,
    "type": "light",
    "last_updated": "2026-02-03T12:00:00"
  }
}
```

## 🎮 Gesture Controls

### Current Gestures

| Gesture | Action | Hold Time |
|---------|--------|-----------|
| ✋ Open Palm (5 fingers) | Turn ON device | 1.5s |
| ✊ Fist (0 fingers) | Turn OFF device | 1.5s |
| ☝️ One Finger | Select Device 1 | Instant |
| ✌️ Two Fingers | Select Device 2 | Instant |
| 🤟 Three Fingers | Select Device 3 | Instant |
| 🖖 Four Fingers | Select Device 4 | Instant |

## 💻 Web Interface Features

### Camera Feed
- Real-time video display
- Gesture detection overlay
- Connection status indicator
- Current gesture display

### Device Control
- Visual device cards
- Click to select device
- Double-click to toggle
- Real-time state updates

### Gesture Guide
- Visual reference for all gestures
- Action descriptions
- Easy to understand icons

## 🔧 Configuration

### Gesture Detection Settings

Edit in `server.py`:

```python
gesture_settings = {
    "enabled": True,
    "confidence": 0.7,        # Detection confidence (0.0-1.0)
    "hold_time": 1.5,         # Seconds to hold gesture
    "max_hands": 1            # Maximum hands to detect
}
```

### Adding New Devices

Edit the `devices` dictionary in `server.py`:

```python
devices = {
    "device_5": {
        "name": "Garden Light",
        "state": False,
        "type": "light",
        "last_updated": None
    }
}
```

## 🌐 Network Access

### Find Your IP Address

**Windows:**
```cmd
ipconfig
```

**Linux/Mac:**
```bash
ifconfig
# or
ip addr show
```

### Access from Other Devices

1. Find your computer's IP (e.g., `192.168.1.100`)
2. Open browser on another device
3. Go to: `http://192.168.1.100:8000`

**Note:** Make sure devices are on the same WiFi network.

## 🔐 Firewall Configuration

If you can't access from other devices, you may need to allow port 8000:

**Windows:**
```cmd
netsh advfirewall firewall add rule name="Gesture Control" dir=in action=allow protocol=TCP localport=8000
```

**Linux (ufw):**
```bash
sudo ufw allow 8000/tcp
```

**Mac:**
System Preferences → Security & Privacy → Firewall → Allow incoming connections

## 🐛 Troubleshooting

### Camera Not Working

**Issue:** Camera doesn't start
**Solution:**
1. Check if camera is being used by another app
2. Try accessing with `https://` instead of `http://` (some browsers require HTTPS for camera)
3. Grant camera permissions in browser settings

### WebSocket Connection Failed

**Issue:** Shows "Disconnected" status
**Solution:**
1. Check if server is running
2. Check browser console for errors
3. Try refreshing the page
4. Check firewall settings

### Low FPS / Laggy

**Issue:** Video feed is slow
**Solution:**
1. Reduce camera resolution in `app.js`:
```javascript
video: {
    width: { ideal: 640 },
    height: { ideal: 480 }
}
```
2. Increase frame delay in `streamFrame()`:
```javascript
setTimeout(() => this.streamFrame(), 50); // 50ms instead of 33ms
```

### Gestures Not Detected

**Issue:** Hand is visible but gestures not detected
**Solution:**
1. Ensure good lighting
2. Show your palm clearly to camera
3. Keep hand 30-60cm from camera
4. Try adjusting confidence settings

## 📊 Performance Tips

### Optimize for Production

1. **Reduce Frame Rate:**
   - Edit `app.js` → Change frame delay to 50-100ms

2. **Lower Resolution:**
   - Edit camera constraints in `app.js`

3. **Disable Auto-reload:**
   ```python
   uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
   ```

## 🔜 Next Steps

### Phase 1 ✅ (Completed)
- [x] Gesture detection module
- [x] FastAPI server setup
- [x] Web interface with camera feed
- [x] Real-time WebSocket communication
- [x] Device control simulation

### Phase 2 (Coming Next)
- [ ] Connect to real ESP32 devices via WiFi
- [ ] Add more gesture types
- [ ] Database for device persistence
- [ ] User authentication
- [ ] Mobile responsive design
- [ ] Voice control integration

## 📝 Testing Checklist

- [ ] Server starts without errors
- [ ] Web page loads at localhost:8000
- [ ] Camera permission granted
- [ ] Video feed displays
- [ ] WebSocket connects (shows "Connected")
- [ ] Hand is detected in video
- [ ] Gestures are recognized
- [ ] Device selection works (1-4 fingers)
- [ ] ON/OFF commands work (hold gesture)
- [ ] Device states update in real-time
- [ ] Multiple browser tabs work simultaneously

## 💡 Usage Tips

1. **Good Lighting:** Ensure your hand is well-lit
2. **Clear Background:** Plain background works best
3. **Hand Position:** 30-60cm from camera, palm facing forward
4. **Hold Gestures:** Hold ON/OFF gestures for full 1.5 seconds
5. **Single Hand:** Use one hand for better accuracy
6. **Clear Movements:** Make distinct, deliberate gestures

## 🆘 Support

If you encounter issues:
1. Check the browser console (F12) for errors
2. Check server terminal for error messages
3. Review the troubleshooting section above
4. Test with `test_gesture.py` first to verify gesture detection works

---

## 🎉 Ready to Test!

Start the server and try controlling devices with gestures!

```bash
python run_server.py
```

Then open: http://localhost:8000

Enjoy your gesture-controlled home automation! 🖐️✨