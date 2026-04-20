#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// // WiFi credentials
// const char* ssid = "Airtel_Tush_home";     // Replace with your WiFi name
// const char* password = "Pyqt5uic#"; // Replace with your WiFi password

const char* ssid = "Autocode";
const char* password = "Nova2703";


// Pin definitions
#define DHTPIN 2          // D4 = GPIO2 connected to DHT11
#define DHTTYPE DHT11
#define PIR_PIN 5         // D1 = GPIO5 connected to PIR sensor
#define BUZZER_PIN 4      // D2 = GPIO4 connected to Buzzer

DHT dht(DHTPIN, DHTTYPE);
ESP8266WebServer server(80);

// Variables for motion detection
bool motionDetected = false;
unsigned long lastMotionTime = 0;
unsigned long buzzerOffTime = 0;
bool buzzerActive = false;

void setup() {
  Serial.begin(115200);
  delay(10);
  
  // Initialize pins
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);  // Buzzer off initially
  
  // Connect to WiFi
  connectToWiFi();
  
  // Initialize DHT11
  dht.begin();
  
  // Setup web server endpoints
  server.on("/data", handleData);
  server.on("/motion", handleMotionData);
  server.on("/", handleRoot);
  
  server.begin();
  Serial.println("Server started");
  Serial.print("Access data at: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/data");
  Serial.println("Access motion status at: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/motion");
  
  Serial.println("PIR + DHT11 + Buzzer Ready");
  delay(2000);  // PIR stabilization
}

void loop() {
  server.handleClient();
  handleMotionDetection();
}

void handleMotionDetection() {
  int motion = digitalRead(PIR_PIN);
  
  // Handle buzzer timing
  if (buzzerActive && millis() > buzzerOffTime) {
    digitalWrite(BUZZER_PIN, LOW);
    buzzerActive = false;
    Serial.println("Buzzer OFF");
  }
  
  // Check for motion
  if (motion == HIGH && !motionDetected) {
    // New motion detected
    motionDetected = true;
    lastMotionTime = millis();
    
    Serial.println("Motion detected! Buzzer ON");
    digitalWrite(BUZZER_PIN, HIGH);  // Turn buzzer ON
    buzzerActive = true;
    buzzerOffTime = millis() + 1000;  // Buzzer sounds for 1 second
    
  } else if (motion == LOW && motionDetected) {
    // Motion ended
    motionDetected = false;
    Serial.println("Motion stopped");
  }
  
  // Auto-reset motion detection after 5 seconds of no motion
  if (motionDetected && (millis() - lastMotionTime > 5000)) {
    motionDetected = false;
    Serial.println("Motion timeout - reset");
  }
  
  delay(50);  // Small delay for stability
}

void handleRoot() {
  String html = "<!DOCTYPE html><html>";
  html += "<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<title>NodeMCU Sensor Dashboard</title>";
  html += "<style>";
  html += "body { font-family: Arial; margin: 20px; background: #f0f0f0; }";
  html += ".container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 10px; }";
  html += ".card { background: #f9f9f9; margin: 10px 0; padding: 15px; border-radius: 5px; }";
  html += ".sensor-value { font-size: 24px; font-weight: bold; color: #2c3e50; }";
  html += ".status { display: inline-block; padding: 5px 10px; border-radius: 3px; }";
  html += ".motion-yes { background: #e74c3c; color: white; }";
  html += ".motion-no { background: #2ecc71; color: white; }";
  html += "button { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }";
  html += "button:hover { background: #2980b9; }";
  html += "</style>";
  html += "</head><body>";
  html += "<div class='container'>";
  html += "<h1>NodeMCU Sensor Dashboard</h1>";
  html += "<div class='card'>";
  html += "<h2>DHT11 Sensor</h2>";
  html += "<p>Temperature: <span id='temp' class='sensor-value'>--</span> °C</p>";
  html += "<p>Humidity: <span id='hum' class='sensor-value'>--</span> %</p>";
  html += "</div>";
  html += "<div class='card'>";
  html += "<h2>PIR Motion Sensor</h2>";
  html += "<p>Motion Status: <span id='motion' class='status'>--</span></p>";
  html += "<p>Last Motion: <span id='lastMotion'>--</span></p>";
  html += "<button onclick='testBuzzer()'>Test Buzzer</button>";
  html += "</div>";
  html += "<div class='card'>";
  html += "<h3>API Endpoints</h3>";
  html += "<p><a href='/data'>/data</a> - DHT11 sensor data (JSON)</p>";
  html += "<p><a href='/motion'>/motion</a> - Motion sensor data (JSON)</p>";
  html += "</div>";
  html += "</div>";
  html += "<script>";
  html += "function fetchData() {";
  html += "  fetch('/data').then(r=>r.json()).then(d=>{";
  html += "    document.getElementById('temp').innerText = d.temp;";
  html += "    document.getElementById('hum').innerText = d.humidity;";
  html += "  }).catch(e=>console.log(e));";
  html += "  fetch('/motion').then(r=>r.json()).then(d=>{";
  html += "    let motionSpan = document.getElementById('motion');";
  html += "    if(d.motionDetected) {";
  html += "      motionSpan.innerText = 'MOTION DETECTED';";
  html += "      motionSpan.className = 'status motion-yes';";
  html += "    } else {";
  html += "      motionSpan.innerText = 'No Motion';";
  html += "      motionSpan.className = 'status motion-no';";
  html += "    }";
  html += "    document.getElementById('lastMotion').innerText = d.lastMotion || 'Never';";
  html += "  }).catch(e=>console.log(e));";
  html += "}";
  html += "function testBuzzer() {";
  html += "  fetch('/testbuzzer').then(r=>r.text()).then(d=>console.log(d));";
  html += "}";
  html += "setInterval(fetchData, 2000);";
  html += "fetchData();";
  html += "</script>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleData() {
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();
  
  Serial.print("Temperature: ");
  Serial.print(temp);
  Serial.print(" °C, Humidity: ");
  Serial.println(hum);
  
  if (isnan(temp) || isnan(hum)) {
    server.send(500, "application/json", "{\"error\":\"sensor failed\"}");
    return;
  }
  
  String json = "{\"temp\":" + String(temp) + ",\"humidity\":" + String(hum) + "}";
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

void handleMotionData() {
  String lastMotionStr = "Never";
  if (lastMotionTime > 0) {
    unsigned long secondsAgo = (millis() - lastMotionTime) / 1000;
    lastMotionStr = String(secondsAgo) + " seconds ago";
  }
  
  String json = "{\"motionDetected\":" + String(motionDetected ? "true" : "false") + 
                ",\"lastMotion\":\"" + lastMotionStr + "\"}";
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}