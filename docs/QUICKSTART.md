# 🚀 Quick Start Guide - Gesture Control Home Automation

## ⚡ 3-Step Setup

### Step 1: Install Dependencies (First time only)
```bash
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
python run_server.py
```

### Step 3: Open Web Interface
Open your browser and go to:
```
http://localhost:8000
```

That's it! You should see the gesture control interface.

---

## 🎮 How to Use

### 1️⃣ **Allow Camera Access**
- Browser will ask for camera permission
- Click "Allow" or "Start Camera" button

### 2️⃣ **Select a Device**
- Show **1 finger** → Select Device 1
- Show **2 fingers** → Select Device 2
- Show **3 fingers** → Select Device 3
- Show **4 fingers** → Select Device 4

### 3️⃣ **Control the Device**
- **Turn ON:** Show open palm ✋ (hold for 1.5 seconds)
- **Turn OFF:** Make a fist ✊ (hold for 1.5 seconds)

---

## 💡 Tips for Best Results

1. **Good Lighting** - Make sure your hand is well-lit
2. **Palm Facing Camera** - Show your palm clearly
3. **Distance** - Keep hand 30-60cm from camera
4. **Hold Steady** - Hold ON/OFF gestures for full 1.5 seconds
5. **Clear Movements** - Make distinct gestures

---

## 🧪 Test Without Web Interface

Want to test gesture detection alone?

```bash
python gesture_detector.py
```

Or test with device simulation:
```bash
python test_gesture.py
```

---

## 🌐 Access from Phone/Tablet

1. Find your computer's IP address:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`

2. On your phone/tablet, open browser and go to:
   ```
   http://YOUR_IP:8000
   ```
   Example: `http://192.168.1.100:8000`

**Note:** Make sure both devices are on the same WiFi network.

---

## 🐛 Common Issues

### Camera Not Working?
- Grant camera permission in browser
- Close other apps using the camera
- Try reloading the page (F5)

### "Disconnected" Status?
- Make sure server is running
- Refresh the page
- Check browser console (F12) for errors

### Gestures Not Detected?
- Check lighting - need good light on your hand
- Show palm clearly to camera
- Keep hand in frame and at right distance

---

## 📊 Test the API

Run automated tests to verify everything works:

```bash
python test_api.py
```

---

## 📁 File Overview

- `server.py` - Main FastAPI server
- `gesture_detector.py` - Hand detection logic
- `run_server.py` - Easy server startup
- `test_gesture.py` - Test gestures without web
- `test_api.py` - Test API endpoints
- `templates/index.html` - Web interface
- `static/app.js` - Frontend JavaScript

---

## 🆘 Need Help?

1. Check `SERVER_SETUP.md` for detailed documentation
2. Check `README.md` for gesture detection details
3. Look at browser console (F12) for errors
4. Check server terminal for error messages

---

## 🎯 Current Features

✅ Real-time hand gesture detection
✅ Web-based control interface  
✅ 4 controllable devices
✅ WebSocket for instant updates
✅ Visual feedback and status
✅ Network access from other devices

---

## 🔜 Coming Next

- [ ] ESP32 device integration
- [ ] Voice control integration
- [ ] More gesture types
- [ ] Database storage
- [ ] User accounts
- [ ] Mobile app

---

## 🎉 Enjoy!

You now have a working gesture control system!

Start the server and have fun controlling devices with your hands! 🖐️✨

```bash
python run_server.py
```