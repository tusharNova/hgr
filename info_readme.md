# 🏠 Neo Smart Home: Multi-Modal IoT Home Automation System

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![ESP32](https://img.shields.io/badge/ESP32-CAM-red.svg)
![NodeMCU](https://img.shields.io/badge/NodeMCU-ESP8266-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Voice](https://img.shields.io/badge/Voice-Assistant-purple.svg)
![Gesture](https://img.shields.io/badge/Gesture-Control-orange.svg)

---

## 📌 Project Overview

**Neo Smart Home** is a unified, multi-modal home automation platform that redefines human-computer interaction in living spaces. Unlike traditional systems that rely solely on mobile apps, Neo Smart Home integrates:

| Feature | Technology | Benefit |
|:--------|:-----------|:--------|
| 🌡️ **Environmental Monitoring** | DHT11 + PIR Sensor | Automatic climate control + intrusion detection |
| ✋ **Dual Gesture Recognition** | ESP32-CAM + Laptop Webcam | Hands-free control from anywhere in the room |
| 🎤 **Voice Assistant** | Offline Speech Recognition | Privacy-focused, no cloud dependency |
| 🌐 **Centralized Web Dashboard** | Python Flask + SocketIO | Real-time graphs, logs, and manual override |
| 🔔 **Smart Alerts** | Motion + Temperature thresholds | Proactive notifications (email/SMS ready) |

**The Vision:** A home that understands you through **voice, gesture, and environment** — without forcing you to pick up your phone.

---

## 🧠 Why This Architecture? (Problem → Solution)

| Problem | Traditional Approach | Neo Smart Home Solution |
|:--------|:---------------------|:------------------------|
| Single point of failure | One hub controls everything | **Decoupled sensing + vision** — if camera lags, temperature still updates every 2 seconds |
| Internet dependency | Cloud-based Alexa/Google Home | **Offline-first** — voice and gesture work without internet |
| High latency | Polling-based updates | **MQTT + WebSockets** — sub-100ms response for critical actions |
| Accessibility gap | Only app-based control | **Voice + Gesture + Web UI** — multiple input methods for all users |
| Privacy concerns | Always-listening cloud devices | **Local processing** — no audio/video leaves your network |

---

## 📡 Hardware Devices & Specifications

### Device Inventory

| Device | Model | Quantity | Purpose | Why This Device? |
|:-------|:------|:---------|:--------|:------------------|
| **NodeMCU** | ESP8266 (CP2102) | 2 units | Data acquisition & relay control | Low power (always on), built-in WiFi, 5V tolerant, Arduino/C++/MicroPython support |
| **DHT11** | Temperature & Humidity Sensor | 2 units | Room climate monitoring | Cheap (±2°C accuracy is sufficient for home automation), 3-pin simple interface |
| **PIR Sensor** | HC-SR501 | 2 units | Motion / Intrusion detection | Passive IR — detects human body heat (7m range), adjustable sensitivity & delay |
| **ESP32-CAM** | ESP32-S (OV2640 camera) | 1 unit | Gesture recognition + video streaming | Built-in camera + processor for on-device AI (TensorFlow Lite), no external server |
| **Relay Module** | 5V 1-Channel | 4 units | Appliance control (Lights/Fan/AC) | Opto-isolated, protects NodeMCU from high voltage spikes |
| **Laptop Webcam** | Built-in or USB | 1 unit | Secondary gesture control | Zero additional cost, higher resolution for desk-based interaction |

### Where Each Device is Used

| Location | Device | Function |
|:---------|:-------|:----------|
| **Living Room** | NodeMCU #1 + DHT11 + PIR | Temperature monitoring, motion detection, ceiling fan control |
| **Bedroom** | NodeMCU #2 + DHT11 + PIR | Night-time climate control + security alert |
| **Main Hallway** | ESP32-CAM | Gesture recognition for entryway lights |
| **Work Desk** | Laptop Webcam | Personal workspace gesture control (desk lamp, monitor brightness) |

---

## 🔌 Pin Mapping & Wiring Guide

### NodeMCU #1 (Living Room)

| NodeMCU Pin | Connected To | Purpose |
|:------------|:-------------|:--------|
| **D4 (GPIO2)** | DHT11 (Data pin) | Temperature & Humidity reading |
| **D3 (GPIO0)** | PIR Sensor (Output) | Motion detection (HIGH = motion detected) |
| **D1 (GPIO5)** | Relay 1 (IN1) | Living Room Light |
| **D2 (GPIO4)** | Relay 2 (IN2) | Ceiling Fan |
| **D5 (GPIO14)** | Relay 3 (IN3) | TV Power (via IR blaster optional) |
| **3.3V** | DHT11 VCC + PIR VCC | Power supply |
| **GND** | All devices common ground | Complete circuit |
| **Vin (5V)** | Relay Module VCC | Relay needs 5V, NodeMCU provides via USB |

### NodeMCU #2 (Bedroom)

| NodeMCU Pin | Connected To | Purpose |
|:------------|:-------------|:--------|
| **D4 (GPIO2)** | DHT11 | Bedroom temperature |
| **D3 (GPIO0)** | PIR Sensor | Night motion (2 AM alerts) |
| **D1 (GPIO5)** | Relay 1 | Bedroom Light |
| **D2 (GPIO4)** | Relay 2 | Bedroom Fan |
| **D6 (GPIO12)** | Buzzer (optional) | Audio alert on motion |

### ESP32-CAM (Hallway)

| ESP32-CAM Pin | Connected To | Purpose |
|:--------------|:-------------|:--------|
| **GPIO0** | Push button (optional) | Flash programming mode |
| **GPIO4** | Built-in Flash LED | Illumination for night gesture |
| **3.3V** | FTDI programmer (VCC) | Power during programming |
| **GND** | FTDI programmer GND | Ground |
| **U0T (GPIO1)** | FTDI RX | Serial communication |
| **U0R (GPIO3)** | FTDI TX | Serial communication |
| **5V pin** | External 5V supply (after programming) | Standalone operation |

---

## 💻 Software Stack & Technologies

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| **Backend Framework** | Python Flask 2.3+ | Web server, REST APIs, template rendering |
| **Real-time Communication** | Flask-SocketIO | Live sensor updates, bidirectional events |
| **Database** | SQLite (or PostgreSQL) | Store sensor logs, events, user preferences |
| **MQTT Broker** | Mosquitto (local) | Lightweight pub/sub for NodeMCU → Python |
| **Gesture Recognition** | OpenCV + MediaPipe | Hand landmark detection (21 keypoints) |
| **ESP32-CAM Firmware** | Arduino/C++ with Edge Impulse | On-device gesture classification |
| **Voice Assistant** | SpeechRecognition + pyttsx3 | Offline speech-to-text + text-to-speech |
| **Data Visualization** | Chart.js + Plotly | Real-time temperature graphs |
| **Serial Communication** | PySerial | Direct USB communication with NodeMCU (fallback) |

---

## 🏗️ System Architecture Diagram (Text Version)
─────────────────────────────────────────────────────────────────────────┐
│ NEO SMART HOME SYSTEM │
├─────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ MQTT/Serial ┌──────────────────────────────┐ │
│ │ NodeMCU │ ◄────────────────► │ │ │
│ │ (Living) │ │ Python Flask Backend │ │
│ │ - DHT11 │ │ (Web Server) │ │
│ │ - PIR │ │ │ │
│ │ - Relays │ │ ┌────────────────────────┐ │ │
│ └──────────────┘ │ │ • SocketIO Server │ │ │
│ │ │ │ • MQTT Subscriber │ │ │
│ │ │ │ • Gesture Processor │ │ │
│ ┌──────────────┐ │ │ • Voice Engine │ │ │
│ │ NodeMCU │ │ │ • SQLite Database │ │ │
│ │ (Bedroom) │ ◄────────────────► │ └────────────────────────┘ │ │
│ │ - DHT11 │ └──────────────┬───────────────┘ │
│ │ - PIR │ │ │
│ │ - Relays │ │ WebSocket/HTTP │
│ └──────────────┘ ▼ │
│ ┌──────────────┐ │
│ ┌──────────────┐ WebSocket │ Web Browser │ │
│ │ ESP32-CAM │ ◄────────────────────────► │ Dashboard │ │
│ │ (Hallway) │ │ - Live Graph │ │
│ │ - Gesture │ │ - Motion Log │ │
│ │ - Streaming │ │ - Voice Cmds │ │
│ └──────────────┘ │ - Manual Ctrl│ │
│ └──────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────┐ │
│ │Laptop Webcam │ ─────► OpenCV/MediaPipe ─────► Gesture Events │
│ │ (Desk) │ │
│ └──────────────┘ │
│ │
│ ┌──────────────┐ │
│ │ Microphone │ ─────► SpeechRecognition ────► Voice Commands │
│ │ (Voice) │ │
│ └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘

text

---

## 🔄 Data Flow & Communication Protocols

### Protocol Decision Matrix

| Data Type | Protocol | Why |
|:----------|:---------|:----|
| Temperature/Humidity (DHT11) | MQTT (QoS 1) | Lightweight, guarantees delivery even if Python server restarts |
| Motion Detection (PIR) | MQTT (QoS 0) | Speed > reliability — duplicate alerts are fine |
| Gesture Commands (ESP32-CAM) | WebSocket | Bi-directional, low latency for real-time control |
| Video Streaming (ESP32-CAM) | HTTP MJPEG Stream | Standard format, works in any browser |
| Voice Commands | Local API call | No network roundtrip, instant response |
| Web Dashboard Updates | SocketIO | Push notifications without page refresh |

### Message Format (JSON)

```json
// Sensor Data from NodeMCU
{
  "device_id": "living_nodemcu",
  "sensor_type": "dht11",
  "temperature": 28.5,
  "humidity": 62.0,
  "timestamp": "2026-04-21T10:30:00Z"
}

// Motion Alert
{
  "device_id": "bedroom_nodemcu",
  "event": "motion_detected",
  "location": "Bedroom",
  "timestamp": "2026-04-21T02:15:00Z"
}

// Gesture Command
{
  "source": "esp32_cam",
  "gesture": "swipe_right",
  "action": "toggle_light",
  "confidence": 0.92
}
```
## 🎮 Gesture Control Details
Recognized Gestures & Mappings
Gesture	ESP32-CAM (Hallway)	Laptop Webcam (Desk)
- ✋ Palm (Open Hand)	Toggle all lights	Pause/Resume media
- ✊ Fist	Turn OFF everything	Mute microphone
- 👆 Point Up	Increase fan speed	Increase volume
- 👇 Point Down	Decrease fan speed	Decrease volume
- 👈 Swipe Left	Previous scene	Previous track
- 👉 Swipe Right	Next scene	Next track
- 🤏 Pinch	Toggle AC	Toggle desk lamp
Gesture Recognition Pipeline
text
Camera Frame → Preprocessing (resize, normalize) → Hand Detection (MediaPipe)
     ↓
Landmark Extraction (21 keypoints)
     ↓
Gesture Classification (LSTM / Random Forest)
     ↓
Confidence > 0.7? → Execute Action → Log to Database
🎤 Voice Assistant Details
Wake Words & Commands
Wake Word	Command Example	Action
"Hey Neo"	"turn on living room light"	Relay 1 ON
"Hey Neo"	"what's the temperature?"	TTS: "28.5 degrees"
"Hey Neo"	"fan speed 3"	Adjust fan PWM
"Hey Neo"	"show me motion log"	Web dashboard opens logs
"Hey Neo"	"good night"	All lights OFF, bedroom fan ON
Voice Pipeline (Offline)
text
Microphone Input → SpeechRecognition (Google/CMU Sphinx offline)
     ↓
Keyword Spotting (Porcupine or custom)
   ↓
Intent Parsing (regex + fuzzy matching)
     ↓
Action Execution → TTS Response (pyttsx3)
🌐 Web Dashboard Features
Page/Component	Real-time Data	User Action
Home	Live temp/humidity gauges	View summary
Temperature Graph	24-hour history (Chart.js)	Select date range
Motion Log	Timestamped events table	Filter by location
Gesture Console	Last recognized gesture	Calibrate sensitivity
Voice Console	Command history	Train new commands
Manual Control	Current relay states	Toggle buttons
Settings	MQTT broker config	Change thresholds
📁 Project Structure
text
neo_smart_home/
│
├── backend/
│   ├── app.py                 # Flask main application
│   ├── mqtt_client.py         # MQTT subscriber for NodeMCU data
│   ├── gesture_processor.py   # MediaPipe + gesture classification
│   ├── voice_assistant.py     # Speech recognition + TTS
│   ├── database.py            # SQLite models & queries
│   └── socket_events.py       # SocketIO event handlers
│
├── firmware/
│   ├── nodemcu_dht11_pir/     # Arduino sketch for NodeMCU
│   │   ├── nodemcu_dht11_pir.ino
│   │   └── config.h
│   └── esp32_cam_gesture/     # Arduino sketch for ESP32-CAM
│       ├── esp32_cam_gesture.ino
│       └── gesture_model.tflite
│
├── frontend/
│   ├── templates/
│   │   ├── index.html         # Main dashboard
│   │   ├── logs.html
│   │   └── settings.html
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/dashboard.js
│   │   └── js/gesture_viewer.js
│   └── assets/
│
├── scripts/
│   ├── start.sh               # Launch all services
│   ├── install_dependencies.sh
│   └── mock_sensor_data.py    # Testing without hardware
│
├── logs/
│   ├── sensor_data.db
│   └── events.log
│
├── requirements.txt
├── README.md
└── LICENSE
🚀 Setup & Installation
Prerequisites
Python 3.9+

NodeMCU ESP8266 with Arduino IDE

ESP32-CAM with ESP32 board package

Mosquitto MQTT broker (optional, can use serial fallback)

Step 1: Clone Repository
bash
git clone https://github.com/yourusername/neo-smart-home.git
cd neo-smart-home
Step 2: Install Python Dependencies
bash
pip install -r requirements.txt
requirements.txt content:

text
flask==2.3.3
flask-socketio==5.3.4
paho-mqtt==1.6.1
pyserial==3.5
opencv-python==4.8.1
mediapipe==0.10.7
speechrecognition==3.10.0
pyttsx3==2.90
plotly==5.17.0
pandas==2.1.0
Step 3: Flash NodeMCU Firmware
Open firmware/nodemcu_dht11_pir/nodemcu_dht11_pir.ino in Arduino IDE

Install libraries: DHT sensor library, PubSubClient (MQTT)

Update WiFi credentials in config.h:

cpp
#define WIFI_SSID "your_wifi"
#define WIFI_PASSWORD "your_password"
#define MQTT_SERVER "192.168.1.100"  // Your Python server IP
Select board: NodeMCU 1.0 (ESP-12E Module)

Upload to NodeMCU

Step 4: Flash ESP32-CAM Firmware
Open firmware/esp32_cam_gesture/esp32_cam_gesture.ino

Install ESP32 board package (if not already)

Select board: AI Thinker ESP32-CAM

Connect FTDI programmer (GPIO0 to GND for programming mode)

Upload code

Remove GPIO0-GND jumper, press reset

Step 5: Run Backend Server
bash
cd backend
python app.py
Server runs at: http://localhost:5000

Step 6: Access Web Dashboard
Open browser → http://localhost:5000

🧪 Testing Without Hardware (Simulation Mode)
If hardware is not available, run the mock sensor script:

bash
python scripts/mock_sensor_data.py
This simulates:

Random temperature (20°C - 35°C)

Random humidity (40% - 80%)

Occasional motion events (every 30-60 seconds)

📊 API Endpoints
Method	Endpoint	Description
GET	/api/sensors/latest	Latest temperature, humidity, motion
GET	/api/sensors/history?hours=24	Historical sensor data (JSON)
POST	/api/relay/control	Control relay: {"relay_id": 1, "state": "on"}
GET	/api/gesture/latest	Last recognized gesture
POST	/api/voice/command	Send voice command: {"text": "turn on light"}
GET	/api/motion/logs	All motion detection events
GET	/video_feed	ESP32-CAM MJPEG stream