// Gesture Control - Frontend JavaScript

class GestureControlApp {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.ws = null;
        this.stream = null;
        this.devices = {};
        this.currentDevice = null;
        this.isStreaming = false;
        
        this.init();
    }

    init() {
        console.log('Initializing Gesture Control App...');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load devices
        this.loadDevices();
        
        // Start camera automatically
        setTimeout(() => {
            this.startCamera();
        }, 500);
    }

    setupEventListeners() {
        // Camera controls
        document.getElementById('start-camera').addEventListener('click', () => this.startCamera());
        document.getElementById('stop-camera').addEventListener('click', () => this.stopCamera());
        
        // Refresh devices
        document.getElementById('refresh-devices').addEventListener('click', () => this.loadDevices());
        
        // Handle page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopStreaming();
            }
        });
    }

    async startCamera() {
        try {
            console.log('Starting camera...');
            
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            });

            this.video.srcObject = this.stream;
            
            // Wait for video to be ready
            await new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    resolve();
                };
            });

            await this.video.play();
            
            // Setup canvas dimensions
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            
            document.getElementById('camera-status').textContent = 'Camera Active';
            this.showToast('Camera started successfully', 'success');
            
            // Connect WebSocket and start streaming
            this.connectWebSocket();
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            document.getElementById('camera-status').textContent = 'Camera Error';
            this.showToast('Failed to access camera: ' + error.message, 'error');
        }
    }

    stopCamera() {
        console.log('Stopping camera...');
        
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        if (this.video.srcObject) {
            this.video.srcObject = null;
        }
        
        this.stopStreaming();
        this.closeWebSocket();
        
        document.getElementById('camera-status').textContent = 'Camera Stopped';
        this.showToast('Camera stopped', 'info');
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
            
            // Start streaming frames
            this.startStreaming();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);
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
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                if (this.stream && !this.ws) {
                    console.log('Attempting to reconnect...');
                    this.connectWebSocket();
                }
            }, 3000);
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
        console.log('Started streaming frames');
        
        this.streamFrame();
    }

    stopStreaming() {
        this.isStreaming = false;
        console.log('Stopped streaming frames');
    }

    streamFrame() {
        if (!this.isStreaming || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }
        
        // Draw current video frame to canvas
        this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        
        // Convert canvas to base64 image
        const imageData = this.canvas.toDataURL('image/jpeg', 0.8);
        
        // Send frame to server
        this.ws.send(JSON.stringify({
            type: 'frame',
            data: imageData
        }));
        
        // Request next frame (30 FPS)
        setTimeout(() => this.streamFrame(), 33);
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
                // Keep-alive response
                break;
            
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    updateGestureDisplay(data) {
        // Update gesture name
        const gestureElement = document.getElementById('detected-gesture');
        gestureElement.textContent = data.gesture || 'None';
        
        // Update finger count
        document.getElementById('finger-count').textContent = data.finger_count || 0;
        
        // Update selected device name if changed
        if (data.device_selected) {
            this.updateSelectedDevice(data.device_selected);
        }
        
        // Show action feedback
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
            
            // Get icon based on device type
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
            
            // Click to select device
            deviceCard.addEventListener('click', () => this.selectDevice(deviceId));
            
            // Double-click to toggle
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
        
        // Update UI
        document.querySelectorAll('.device-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        const selectedCard = document.getElementById(`device-${deviceId}`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }
        
        // Update selected device name in video overlay
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
        // Update local state
        if (this.devices[deviceId]) {
            this.devices[deviceId] = device;
        }
        
        // Update UI
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
        // Remove existing toasts
        document.querySelectorAll('.toast').forEach(toast => toast.remove());
        
        // Create new toast
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new GestureControlApp();
});


