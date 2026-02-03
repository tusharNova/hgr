#!/usr/bin/env python3
"""
Startup script for Gesture Control Home Automation Server
"""

import uvicorn
import sys
import os

def main():
    print("\n" + "="*70)
    print(" 🖐️  GESTURE CONTROL HOME AUTOMATION")
    print("="*70)
    print("\n📋 Starting server...")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📱 Or access from other devices: http://YOUR_IP:8000")
    print("\n💡 Tips:")
    print("   - Allow camera access when prompted")
    print("   - Use good lighting for better hand detection")
    print("   - Keep your hand 30-60cm from the camera")
    print("\n⚡ Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    try:
        uvicorn.run(
            "server:app",
            host="0.0.0.0",  # Accessible from network
            port=8000,
            reload=True,      # Auto-reload on code changes
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()