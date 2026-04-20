// ESP32-CAM Gesture Control - Frontend JavaScript
// Fetches MJPEG stream from ESP32-CAM and sends frames to WebSocket

class ESP32GestureControlApp {
    constructor() {
        this.videoImg = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.ws = null;
        this.isStreaming = false;
        this.devices = {};
        this.currentDevice = null;
        this.streamActive = false;
        this.frameInterval = null;
        this.esp32StreamUrl = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.init();
    }

    init() {
        console.log('Initializing ESP32-CAM Gesture Control App...');
        
        // Get ESP32 stream URL from sessionStorage
        this.esp32StreamUrl = sessionStorage.getItem('esp32_stream_url');
        const esp32Ip = sessionStorage.getItem('esp32_ip');
        
        if (!this.esp32StreamUrl) {
            this.showToast('No ESP32-CAM configured. Redirecting...', 'error');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
            return;
        }
        
        // Update badge with IP
        const badge = document.getElementById('esp32-badge');
        if (badge && esp32Ip) {
            badge.textContent = esp32Ip;
        }
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load devices
        this.loadDevices();
        
        // Auto-start camera
        setTimeout(() => {
            this.startCamera();
        }, 500);
    }

    setupEventListeners() {
        document.getElementById('start-camera').addEventListener('click', () => this.startCamera());
        document.getElementById('stop-camera').addEventListener('click', () => this.stopCamera());
        document.getElementById('refresh-devices').addEventListener('click', () => this.loadDevices());
        document.getElementById('reconnect-esp32').addEventListener('click', () => this.reconfigureESP32());
        
        const reconnectBar = document.getElementById('reconnect-bar');
        if (reconnectBar) {
            reconnectBar.addEventListener('click', () => this.reconfigureESP32());
        }
        
        // Handle page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopStreaming();
            } else if (this.streamActive) {
                this.startStreaming();
            }
        });
    }

    reconfigureESP32() {
        const newIp = prompt('Enter ESP32-CAM IP address:', sessionStorage.getItem('esp32_ip') || '192.168.1.100');
        if (newIp && newIp.trim()) {
            const ip = newIp.trim().replace('http://', '').replace('/stream', '');
            const streamUrl = `http://${ip}:81/stream`;
            sessionStorage.setItem('esp32_stream_url', streamUrl);
            sessionStorage.setItem('esp32_ip', ip);
            this.esp32StreamUrl = streamUrl;
            
            // Update badge
            const badge = document.getElementById('esp32-badge');
            if (badge) badge.textContent = ip;
            
            // Restart camera
            this.stopCamera();
            setTimeout(() => this.startCamera(), 500);
        }
    }

    async startCamera() {
        try {
            console.log('Starting ESP32-CAM stream from:', this.esp32StreamUrl);
            
            // Test connection to ESP32
            const testResponse = await fetch(this.esp32StreamUrl, { method: 'HEAD', mode: 'no-cors' });
            
            // Set video image source
            this.videoImg.src = this.esp32StreamUrl;
            this.streamActive = true;
            
            // Wait for image to load
            this.videoImg.onload = () => {
                document.getElementById('camera-status').textContent = 'ESP32-CAM Active';
                this.showToast('ESP32-CAM stream started', 'success');
                
                // Setup canvas dimensions (will be set when we get first frame)
                if (this.videoImg.naturalWidth > 0) {
                    this.canvas.width = this.videoImg.naturalWidth;
                    this.canvas.height = this.videoImg.naturalHeight;
                } else {
                    // Default dimensions
                    this.canvas.width = 640;
                    this.canvas.height = 480;
                }
                
                // Connect WebSocket and start streaming
                this.connectWebSocket();
            };
            
            this.videoImg.onerror = () => {
                console.error('Failed to load ESP32 stream');
                document.getElementById('camera-status').textContent = 'ESP32 Connection Failed';
                this.showToast('Failed to connect to ESP32-CAM. Check IP address.', 'error');
                this.streamActive = false;
                
                const reconnectBar = document.getElementById('reconnect-bar');
                if (reconnectBar) reconnectBar.style.display = 'block';
            };
            
        } catch (error) {
            console.error('Error starting ESP32 stream:', error);
            document.getElementById('camera-status').textContent = 'Connection Error';
            this.showToast('Failed to connect to ESP32-CAM', 'error');
            this.streamActive = false;
            
            const reconnectBar = document.getElementById('reconnect-bar');
            if (reconnectBar) reconnectBar.style.display = 'block';
        }
    }

    stopCamera() {
        console.log('Stopping ESP32-CAM stream...');
        
        this.stopStreaming();
        this.closeWebSocket();
        this.streamActive = false;
        this.videoImg.src = '';
        
        document.getElementById('camera-status').textContent = 'Stream Stopped';
        this.showToast('ESP32-CAM stream stopped', 'info');
        
        const reconnectBar = document.getElementById('reconnect-bar');
        if (reconnectBar) reconnectBar.style.display = 'none';
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/gesture`;
        
        console.log('Connecting to WebSocket:', wsUrl);
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            document.getElementById('ws-status').textContent = 'Connected';
            document.getElementById('ws-status').className = 'connection-status status-connected';
            this.showToast('Connected to server', 'success');
            this.reconnectAttempts = 0;
            
            // Start streaming frames
            this.startStreaming();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showToast('WebSocket error', 'error');
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            document.getElementById('ws-status').textContent = 'Disconnected';
            document.getElementById('ws-status').className = 'connection-status status-disconnected';
            this.stopStreaming();
            
            // Attempt to reconnect
            if (this.streamActive && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                setTimeout(() => {
                    if (this.streamActive && !this.ws) {
                        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                        this.connectWebSocket();
                    }
                }, 3000);
            }
        };
    }

    closeWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    startStreaming() {
        if (this.isStreaming) return;
        
        this.isStreaming = true;
        console.log('Started streaming frames from ESP32');
        
        this.streamFrame();
    }

    stopStreaming() {
        this.isStreaming = false;
        if (this.frameInterval) {
            clearTimeout(this.frameInterval);
            this.frameInterval = null;
        }
        console.log('Stopped streaming frames');
    }

    streamFrame() {
        if (!this.isStreaming || !this.ws || this.ws.readyState !== WebSocket.OPEN || !this.streamActive) {
            if (this.isStreaming) {
                setTimeout(() => this.streamFrame(), 100);
            }
            return;
        }
        
        // Wait for image to be loaded
        if (!this.videoImg.complete || this.videoImg.naturalWidth === 0) {
            setTimeout(() => this.streamFrame(), 50);
            return;
        }
        
        // Update canvas dimensions if needed
        if (this.canvas.width !== this.videoImg.naturalWidth && this.videoImg.naturalWidth > 0) {
            this.canvas.width = this.videoImg.naturalWidth;
            this.canvas.height = this.videoImg.naturalHeight;
        }
        
        // Draw current video frame to canvas
        try {
            this.ctx.drawImage(this.videoImg, 0, 0, this.canvas.width, this.canvas.height);
            
            // Convert canvas to base64 image
            const imageData = this.canvas.toDataURL('image/jpeg', 0.7);
            
            // Send frame to server
            this.ws.send(JSON.stringify({
                type: 'frame',
                data: imageData
            }));
        } catch (e) {
            console.error('Error capturing frame:', e);
        }
        
        // Request next frame (20 FPS for ESP32 to reduce load)
        this.frameInterval = setTimeout(() => this.streamFrame(), 50);
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'gesture_result':
                this.updateGestureDisplay(data);
                break;
            
            case 'device_update':
                this.updateDeviceState(data.device_id, data.device);
                break;
            
            case 'device_selected':
                this.updateSelectedDevice(data.device_id);
                break;
            
            case 'pong':
                break;
            
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    updateGestureDisplay(data) {
        const gestureElement = document.getElementById('detected-gesture');
        gestureElement.textContent = data.gesture || 'None';
        
        document.getElementById('finger-count').textContent = data.finger_count || 0;
        
        if (data.device_selected) {
            this.updateSelectedDevice(data.device_selected);
        }
        
        if (data.action_triggered) {
            const deviceName = this.devices[data.device_id]?.name || data.device_id;
            const action = data.action_triggered === 'turned_on' ? 'ON' : 'OFF';
            this.showToast(`${deviceName} turned ${action}`, 'success');
        }
    }

    async loadDevices() {
        try {
            const response = await fetch('/api/devices');
            const data = await response.json();
            
            if (data.success) {
                this.devices = data.devices;
                this.currentDevice = data.current_device;
                this.renderDevices();
                this.updateSelectedDevice(this.currentDevice);
            }
        } catch (error) {
            console.error('Error loading devices:', error);
            this.showToast('Failed to load devices', 'error');
        }
    }

    renderDevices() {
        const container = document.getElementById('devices-container');
        container.innerHTML = '';
        
        Object.entries(this.devices).forEach(([deviceId, device]) => {
            const deviceCard = document.createElement('div');
            deviceCard.className = 'device-card';
            deviceCard.id = `device-${deviceId}`;
            
            if (deviceId === this.currentDevice) {
                deviceCard.classList.add('selected');
            }
            
            const icons = {
                'light': '💡',
                'fan': '🌀',
                'tv': '📺',
                'ac': '❄️'
            };
            const icon = icons[device.type] || '🔌';
            
            deviceCard.innerHTML = `
                <div class="device-icon">${icon}</div>
                <div class="device-name">${device.name}</div>
                <div class="device-type">${device.type}</div>
                <span class="device-state ${device.state ? 'device-on' : 'device-off'}">
                    ${device.state ? 'ON' : 'OFF'}
                </span>
            `;
            
            deviceCard.addEventListener('click', () => this.selectDevice(deviceId));
            deviceCard.addEventListener('dblclick', () => this.toggleDevice(deviceId));
            
            container.appendChild(deviceCard);
        });
    }

    async selectDevice(deviceId) {
        try {
            const response = await fetch(`/api/select-device/${deviceId}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateSelectedDevice(deviceId);
            }
        } catch (error) {
            console.error('Error selecting device:', error);
        }
    }

    updateSelectedDevice(deviceId) {
        this.currentDevice = deviceId;
        
        document.querySelectorAll('.device-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        const selectedCard = document.getElementById(`device-${deviceId}`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }
        
        const deviceName = this.devices[deviceId]?.name || 'None';
        document.getElementById('selected-device-name').textContent = deviceName;
    }

    async toggleDevice(deviceId) {
        try {
            const response = await fetch(`/api/devices/${deviceId}/toggle`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateDeviceState(deviceId, data.device);
                const action = data.device.state ? 'ON' : 'OFF';
                this.showToast(`${data.device.name} turned ${action}`, 'success');
            }
        } catch (error) {
            console.error('Error toggling device:', error);
            this.showToast('Failed to toggle device', 'error');
        }
    }

    updateDeviceState(deviceId, device) {
        if (this.devices[deviceId]) {
            this.devices[deviceId] = device;
        }
        
        const deviceCard = document.getElementById(`device-${deviceId}`);
        if (deviceCard) {
            const stateElement = deviceCard.querySelector('.device-state');
            if (stateElement) {
                stateElement.textContent = device.state ? 'ON' : 'OFF';
                stateElement.className = `device-state ${device.state ? 'device-on' : 'device-off'}`;
            }
        }
    }

    showToast(message, type = 'info') {
        document.querySelectorAll('.toast').forEach(toast => toast.remove());
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ESP32GestureControlApp();
});