class VoiceBot {
    constructor() {
        this.ws = null;
        this.devices = [];
        this.isListening = false;
        this.isTalking = false;
        this.hasUserInteracted = false;  // Track user interaction

        // Web Speech API
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.pendingUtterance = null;

        // Canvas for waveform
        this.canvas = document.getElementById('waveform-canvas');
        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d');
        }
        this.animationFrame = 0;
        this.animationState = 'idle'; // idle, listening, talking

        // Initialize
        this.initWebSocket();
        this.initSpeechRecognition();
        this.initCanvas();
        this.initEventListeners();
        this.startAnimation();

        // Don't auto-speak welcome message - wait for user interaction
        // Welcome message will be shown in UI instead
        this.updateResponseText("Hello! I'm Neo, your AI assistant. Click the microphone button and speak to me!");
    }

    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus(true);
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('WebSocket message:', data);

                if (data.type === 'devices') {
                    this.devices = data.devices;
                    this.renderDevices();
                    console.log('Devices loaded via WebSocket:', this.devices);
                } else if (data.type === 'device_update') {
                    this.updateDevice(data);
                } else if (data.type === 'pong') {
                    console.log('Heartbeat received');
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };

        this.ws.onclose = (event) => {
            console.log('WebSocket closed', event.code, event.reason);
            this.updateConnectionStatus(false);

            if (event.code !== 1000) {
                console.log('Reconnecting in 3 seconds...');
                setTimeout(() => {
                    this.initWebSocket();
                }, 3000);
            }
        };

        // Send heartbeat every 30 seconds
        setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000);
    }

    initSpeechRecognition() {
        // Check for browser support
        const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognitionAPI) {
            this.showToast('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.', 'error');
            this.updateStatus('Speech recognition not supported', '#ef4444');
            return;
        }

        try {
            this.recognition = new SpeechRecognitionAPI();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;

            this.recognition.onstart = () => {
                console.log('Speech recognition started');
                this.isListening = true;
                this.animationState = 'listening';
                this.updateStatus('Listening... Speak now!', '#4ade80');
                const button = document.getElementById('voice-button');
                if (button) button.classList.add('listening');
                this.updateTranscriptText('Listening...');
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                console.log('Transcript:', transcript);
                this.updateTranscriptText(transcript);
                this.processCommand(transcript);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isListening = false;
                this.animationState = 'idle';
                const button = document.getElementById('voice-button');
                if (button) button.classList.remove('listening');

                switch (event.error) {
                    case 'no-speech':
                        this.showToast('No speech detected. Please try again.', 'error');
                        this.updateStatus('No speech detected', '#ef4444');
                        this.updateTranscriptText('No speech detected. Click the button and speak again.');
                        break;
                    case 'not-allowed':
                        this.showToast('Microphone access denied. Please allow microphone access in your browser settings.', 'error');
                        this.updateStatus('Microphone access denied', '#ef4444');
                        this.updateTranscriptText('Please allow microphone access and try again.');
                        break;
                    case 'network':
                        this.showToast('Network error. Please check your internet connection.', 'error');
                        this.updateStatus('Network error', '#ef4444');
                        break;
                    default:
                        this.showToast(`Error: ${event.error}`, 'error');
                        this.updateStatus('Error occurred', '#ef4444');
                }
            };

            this.recognition.onend = () => {
                console.log('Speech recognition ended');
                this.isListening = false;
                if (this.animationState === 'listening') {
                    this.animationState = 'idle';
                }
                const button = document.getElementById('voice-button');
                if (button) button.classList.remove('listening');
                if (this.updateStatus && !this.isTalking) {
                    this.updateStatus('Ready to listen', '#333');
                }
            };
        } catch (error) {
            console.error('Error initializing speech recognition:', error);
            this.showToast('Could not initialize speech recognition', 'error');
        }
    }

    initCanvas() {
        if (this.canvas && this.ctx) {
            this.canvas.width = this.canvas.offsetWidth;
            this.canvas.height = this.canvas.offsetHeight;
        }
    }

    initEventListeners() {
        const voiceButton = document.getElementById('voice-button');
        if (voiceButton) {
            voiceButton.addEventListener('click', () => {
                // Mark that user has interacted
                this.hasUserInteracted = true;

                if (this.isListening) {
                    this.stopListening();
                } else if (this.isTalking) {
                    this.stopTalking();
                } else {
                    this.startListening();
                }
            });
        }

        // Resize canvas
        window.addEventListener('resize', () => {
            this.initCanvas();
        });

        // Request microphone permission on page load (optional)
        this.requestMicrophonePermission();
    }

    async requestMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop()); // Stop the stream immediately
            console.log('Microphone permission granted');
        } catch (error) {
            console.error('Microphone permission denied:', error);
            this.showToast('Please allow microphone access to use voice control', 'info');
        }
    }

    startListening() {
        if (!this.recognition) {
            this.showToast('Speech recognition not available. Please refresh the page.', 'error');
            return;
        }

        // Stop any ongoing speech before listening
        if (this.isTalking) {
            this.stopTalking();
        }

        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            if (error.name === 'InvalidStateError') {
                // Recognition already started, stop and restart
                this.recognition.stop();
                setTimeout(() => {
                    try {
                        this.recognition.start();
                    } catch (e) {
                        this.showToast('Could not start listening. Please try again.', 'error');
                    }
                }, 100);
            } else {
                this.showToast('Could not start listening. Please try again.', 'error');
            }
        }
    }

    stopListening() {
        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (error) {
                console.error('Error stopping recognition:', error);
            }
        }
    }

    stopTalking() {
        if (this.synthesis) {
            this.synthesis.cancel();
        }
        this.isTalking = false;
        this.animationState = 'idle';
        const button = document.getElementById('voice-button');
        if (button) button.classList.remove('talking');
        this.updateStatus('Ready to listen', '#333');
    }

    speak(text) {
        if (!this.synthesis) {
            console.error('Speech synthesis not available');
            this.updateResponseText(text);
            return;
        }

        // Cancel any ongoing speech
        this.synthesis.cancel();

        // Wait for voices to be loaded
        const speakNow = () => {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            // Try to use a good voice
            const voices = this.synthesis.getVoices();
            const preferredVoice = voices.find(voice => voice.lang === 'en-US' && voice.name.includes('Google'));
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }

            utterance.onstart = () => {
                console.log('Speech started:', text);
                this.isTalking = true;
                this.animationState = 'talking';
                this.updateStatus('Speaking...', '#ef4444');
                const button = document.getElementById('voice-button');
                if (button) button.classList.add('talking');
                this.updateResponseText(text);
            };

            utterance.onend = () => {
                console.log('Speech ended');
                this.isTalking = false;
                this.animationState = 'idle';
                if (!this.isListening) {
                    this.updateStatus('Ready to listen', '#333');
                }
                const button = document.getElementById('voice-button');
                if (button) button.classList.remove('talking');
            };

            utterance.onerror = (event) => {
                console.error('Speech synthesis error:', event);
                this.isTalking = false;
                this.animationState = 'idle';
                const button = document.getElementById('voice-button');
                if (button) button.classList.remove('talking');
                this.updateStatus('Ready to listen', '#333');
                // Still show the response text even if speech fails
                this.updateResponseText(text);
            };

            this.synthesis.speak(utterance);
        };

        // Check if voices are loaded
        if (this.synthesis.getVoices().length > 0) {
            speakNow();
        } else {
            // Wait for voices to load
            this.synthesis.addEventListener('voiceschanged', speakNow, { once: true });
            // Fallback timeout
            setTimeout(speakNow, 500);
        }
    }

    async processCommand(command) {
        const lowerCommand = command.toLowerCase();
        this.updateStatus('Processing...', '#667eea');

        // Show thinking indicator
        this.updateResponseText('Thinking...');

        // Small delay to show processing state
        await new Promise(resolve => setTimeout(resolve, 100));

        // Device control commands
        if (lowerCommand.includes('turn on') || lowerCommand.includes('turn off') ||
            lowerCommand.includes('switch on') || lowerCommand.includes('switch off')) {
            const response = await this.handleDeviceControl(lowerCommand);
            this.speak(response);
            return;
        }

        if (lowerCommand.includes('status') || lowerCommand.includes('device status') ||
            lowerCommand.includes('what is the status')) {
            const response = this.getDeviceStatus();
            this.speak(response);
            return;
        }

        // General commands
        const response = this.handleGeneralCommand(lowerCommand);
        this.speak(response);
    }

    async handleDeviceControl(command) {
        try {
            // // Turn on all devices
            // if ((command.includes('all') || command.includes('everything')) && command.includes('on')) {
            //     for (let i = 1; i <= 4; i++) {
            //         await this.sendDeviceCommand(i, 'on');
            //     }
            //     return 'Turning on all devices';
            // }

            if ((command.includes('all') || command.includes('everything')) && command.includes('on')) {
                for (let i = 1; i <= 4; i++) {
                    await this.sendDeviceCommand(i, 'on');
                }
                // Add this to update all devices in UI
                this.devices.forEach(device => {
                    device.state = 'on';
                });
                this.renderDevices();  // This updates UI
                return 'Turning on all devices';
            }

            // Turn off all devices
            if ((command.includes('all') || command.includes('everything')) && command.includes('off')) {
                for (let i = 1; i <= 4; i++) {
                    await this.sendDeviceCommand(i, 'off');
                }
                return 'Turning off all devices';
            }

            // Extract device number using regex
            let deviceNum = null;

            // Try different patterns
            const patterns = [
                /device\s*(\d+)/i,
                /device\s+number\s*(\d+)/i,
                /number\s*(\d+)/i,
                /(\d+)(?:\s*device)?/i
            ];

            for (const pattern of patterns) {
                const match = command.match(pattern);
                if (match && match[1]) {
                    deviceNum = parseInt(match[1]);
                    break;
                }
            }

            // Also check for device names
            if (!deviceNum) {
                if (command.includes('light') && !command.includes('kitchen') && !command.includes('living')) {
                    deviceNum = 1; // Living Room Light
                } else if (command.includes('fan')) {
                    deviceNum = 2; // Bedroom Fan
                } else if (command.includes('kitchen')) {
                    deviceNum = 3; // Kitchen Light
                } else if (command.includes('tv') || command.includes('television')) {
                    deviceNum = 4; // TV
                }
            }

            if (deviceNum && deviceNum >= 1 && deviceNum <= 4) {
                const action = command.includes('on') ? 'on' : 'off';
                await this.sendDeviceCommand(deviceNum, action);

                const deviceName = this.getDeviceName(deviceNum);
                return `${action === 'on' ? 'Turning on' : 'Turning off'} ${deviceName}`;
            }

            return "Sorry, I didn't understand which device you want to control. Please say 'device 1', 'device 2', etc.";
        } catch (error) {
            console.error('Device control error:', error);
            return "Sorry, I couldn't control the device. Please try again.";
        }
    }

    getDeviceName(deviceNum) {
        const names = {
            1: 'Living Room Light',
            2: 'Bedroom Fan',
            3: 'Kitchen Light',
            4: 'TV'
        };
        return names[deviceNum] || `Device ${deviceNum}`;
    }

    //old code ------------------------------------------
    // async sendDeviceCommand(deviceId, action) {
    //     try {
    //         const response = await fetch('/api/control', {
    //             method: 'POST',
    //             headers: {
    //                 'Content-Type': 'application/json'
    //             },
    //             body: JSON.stringify({
    //                 device_id: deviceId,
    //                 action: action
    //             })
    //         });

    //         if (!response.ok) {
    //             throw new Error('Failed to control device');
    //         }

    //         const result = await response.json();
    //         console.log(`Device ${deviceId} turned ${action}:`, result);
    //         return result;
    //     } catch (error) {
    //         console.error('Error sending device command:', error);
    //         throw error;
    //     }
    // }

    //new code ------------------------------------------
    async sendDeviceCommand(deviceId, action) {
        const response = await fetch('/api/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_id: deviceId, action: action })
        });

        const result = await response.json();

        // Add this line to update UI immediately
        const device = this.devices.find(d => d.id === deviceId);
        if (device) {
            device.state = action;
            this.renderDevices();  // This updates the UI without refresh
        }

        return result;
    }

    getDeviceStatus() {
        if (!this.devices || this.devices.length === 0) {
            return 'No devices found. Please refresh the page.';
        }

        const onDevices = this.devices.filter(d => d.state === 'on');
        const offDevices = this.devices.filter(d => d.state === 'off');

        if (onDevices.length === 0) {
            return 'All devices are currently off';
        } else if (offDevices.length === 0) {
            return 'All devices are currently on';
        } else {
            const onNames = onDevices.map(d => d.name).join(', ');
            return `${onDevices.length} device${onDevices.length > 1 ? 's are' : ' is'} on: ${onNames}`;
        }
    }

    handleGeneralCommand(command) {
        // Greeting commands
        if (command.match(/hello|hi|hey|greetings/)) {
            const responses = [
                'Hello there! How can I help you today?',
                'Hi! What can I do for you?',
                'Hey! Ready to control your smart home?'
            ];
            return responses[Math.floor(Math.random() * responses.length)];
        }

        // Time commands
        if (command.includes('time')) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
            return `The current time is ${timeStr}`;
        }

        // Date commands
        if (command.includes('date') || command.includes('today')) {
            const today = new Date();
            const dateStr = today.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            return `Today is ${dateStr}`;
        }

        // Website commands
        if (command.includes('open youtube')) {
            window.open('https://www.youtube.com', '_blank');
            return 'Opening YouTube for you';
        }
        if (command.includes('open google')) {
            window.open('https://www.google.com', '_blank');
            return 'Opening Google';
        }
        if (command.includes('open facebook')) {
            window.open('https://www.facebook.com', '_blank');
            return 'Opening Facebook';
        }
        if (command.includes('open github')) {
            window.open('https://www.github.com', '_blank');
            return 'Opening GitHub';
        }

        // Search commands
        if (command.includes('search for') || command.includes('google')) {
            let query = command.replace(/search for|google/i, '').trim();
            if (query) {
                const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
                window.open(searchUrl, '_blank');
                return `Searching Google for ${query}`;
            }
            return 'What would you like me to search for?';
        }

        // Wikipedia commands
        if (command.includes('tell me about') || command.includes('wikipedia')) {
            let topic = command.replace(/tell me about|wikipedia/i, '').trim();
            if (topic) {
                const wikiUrl = `https://en.wikipedia.org/wiki/${encodeURIComponent(topic.replace(/ /g, '_'))}`;
                window.open(wikiUrl, '_blank');
                return `Opening Wikipedia page about ${topic}`;
            }
            return 'What topic would you like to know about?';
        }

        // Joke commands
        if (command.includes('joke') || command.includes('funny')) {
            const jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the computer go to the doctor? It had a virus!",
                "Why don't robots panic? They have nerves of steel!",
                "What do you call a computer that sings? A Dell!",
                "Why did the smartphone need glasses? It lost all its contacts!",
                "Why don't programmers like nature? It has too many bugs!"
            ];
            return jokes[Math.floor(Math.random() * jokes.length)];
        }

        // Help command
        if (command.includes('help') || command.includes('what can you do')) {
            return "I can help you control your smart home devices. Try saying 'turn on device 1', 'turn off all devices', or ask me for the time, date, or a joke!";
        }

        // Thank you
        if (command.includes('thank')) {
            return "You're very welcome! Is there anything else I can help you with?";
        }

        // Goodbye
        if (command.includes('bye') || command.includes('goodbye') || command.includes('see you')) {
            return "Goodbye! Have a great day!";
        }

        // Unknown command
        const responses = [
            "I'm not sure I understood. Could you please repeat that?",
            "Sorry, I didn't catch that. Try saying something like 'turn on device 1' or 'what time is it?'",
            "I'm still learning. Could you say that differently?",
            "I didn't understand. You can say 'help' to see what I can do."
        ];
        return responses[Math.floor(Math.random() * responses.length)];
    }

    // Animation methods
    startAnimation() {
        this.animate();
    }

    animate() {
        if (!this.ctx || !this.canvas) {
            requestAnimationFrame(() => this.animate());
            return;
        }

        this.animationFrame++;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        if (this.animationState === 'idle') {
            this.drawIdleAnimation();
        } else if (this.animationState === 'listening') {
            this.drawListeningAnimation();
        } else if (this.animationState === 'talking') {
            this.drawTalkingAnimation();
        }

        requestAnimationFrame(() => this.animate());
    }

    drawIdleAnimation() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const pulse = 30 + 10 * Math.sin(this.animationFrame * 0.03);

        // Outer circle
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, pulse, 0, Math.PI * 2);
        this.ctx.strokeStyle = '#667eea';
        this.ctx.lineWidth = 3;
        this.ctx.stroke();

        // Inner circle
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, pulse / 2, 0, Math.PI * 2);
        this.ctx.fillStyle = '#667eea';
        this.ctx.fill();
    }

    drawListeningAnimation() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;

        // Sound waves
        for (let i = 0; i < 5; i++) {
            const radius = 30 + i * 25 + 10 * Math.sin(this.animationFrame * 0.1 + i * 0.5);
            const alpha = Math.max(0, 1 - i * 0.2);

            this.ctx.beginPath();
            this.ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            this.ctx.strokeStyle = `rgba(74, 222, 128, ${alpha})`;
            this.ctx.lineWidth = 3;
            this.ctx.stroke();
        }

        // Center microphone
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, 15, 0, Math.PI * 2);
        this.ctx.fillStyle = '#4ade80';
        this.ctx.fill();
    }

    drawTalkingAnimation() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const barCount = 7;
        const barWidth = 15;
        const spacing = 20;
        const startX = centerX - (barCount * spacing) / 2;

        for (let i = 0; i < barCount; i++) {
            const barHeight = 20 + 40 * Math.abs(Math.sin(this.animationFrame * 0.1 + i * 0.8));
            const x = startX + i * spacing;

            this.ctx.fillStyle = '#ef4444';
            this.ctx.fillRect(x, centerY - barHeight / 2, barWidth, barHeight);
        }
    }

    // UI Update methods
    updateStatus(text, color) {
        const statusElement = document.getElementById('status-text');
        if (statusElement) {
            statusElement.textContent = text;
            statusElement.style.color = color;
        }
    }

    updateTranscriptText(text) {
        const transcriptElement = document.getElementById('transcript');
        if (transcriptElement) {
            transcriptElement.textContent = text;
        }
    }

    updateResponseText(text) {
        const responseElement = document.getElementById('response');
        if (responseElement) {
            responseElement.textContent = text;
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            if (connected) {
                statusElement.textContent = 'Connected';
                statusElement.className = 'connection-status status-connected';
            } else {
                statusElement.textContent = 'Disconnected';
                statusElement.className = 'connection-status status-disconnected';
            }
        }
    }

    getDeviceIcon(type) {
        const icons = {
            'light': '💡',
            'fan': '🌀',
            'tv': '📺',
            'ac': '❄️'
        };
        return icons[type?.toLowerCase()] || '🔌';
    }

    renderDevices() {
        const container = document.getElementById('devices-container');
        if (!container) return;

        container.innerHTML = '';

        this.devices.forEach(device => {
            const deviceCard = document.createElement('div');
            deviceCard.className = 'device-card';
            deviceCard.innerHTML = `
                <div class="device-icon">${device.icon || this.getDeviceIcon(device.type)}</div>
                <div class="device-name">${device.name}</div>
                <div class="device-type">${device.type || 'Device'}</div>
                <div class="device-state ${device.state === 'on' ? 'device-on' : 'device-off'}">
                    ${(device.state || 'off').toUpperCase()}
                </div>
            `;
            container.appendChild(deviceCard);
        });
    }
    // old code
    // updateDevice(data) {
    //     try {
    //         const deviceId = parseInt(data.device_id);
    //         const device = this.devices.find(d => d.id === deviceId);

    //         if (device) {
    //             device.state = data.state;
    //             this.renderDevices();
    //             console.log(`Device ${deviceId} updated to ${data.state}`);
    //         }
    //     } catch (error) {
    //         console.error('Error updating device:', error);
    //     }
    // }

    // new one 
    updateDevice(data) {
        // data.device_id comes as "device_1" or just number
        let deviceId;
        if (typeof data.device_id === 'string') {
            deviceId = parseInt(data.device_id.split('_')[1]);
        } else {
            deviceId = parseInt(data.device_id);
        }

        const device = this.devices.find(d => d.id === deviceId);
        if (device) {
            device.state = data.state || (data.device?.state ? 'on' : 'off');
            this.renderDevices();  // This updates the UI
            console.log(`Device ${deviceId} updated to ${device.state}`);
        }
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        if (toast) {
            toast.textContent = message;
            toast.className = `toast ${type}`;
            toast.style.display = 'block';

            setTimeout(() => {
                toast.style.display = 'none';
            }, 4000);
        }
    }
}

// Initialize the voice bot
document.addEventListener('DOMContentLoaded', () => {
    new VoiceBot();
});