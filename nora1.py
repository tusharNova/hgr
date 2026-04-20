import cv2
import urllib.request
import numpy as np

# Try MJPEG stream
url = "http://192.168.137.41/stream"  # Try different endpoints

try:
    stream = urllib.request.urlopen(url)
    bytes_data = b''
    print("Trying to read MJPEG stream...")
    
    for i in range(100):  # Try 100 chunks
        bytes_data += stream.read(1024)
        a = bytes_data.find(b'\xff\xd8')
        b = bytes_data.find(b'\xff\xd9')
        
        if a != -1 and b != -1:
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            if img is not None:
                print(f"✅ Found working stream! Displaying image...")
                cv2.imshow('ESP32-CAM', img)
                cv2.waitKey(1)
                
                # Save one frame to verify
                cv2.imwrite('esp32_cam_frame.jpg', img)
                print(f"📸 Saved frame to esp32_cam_frame.jpg")
                break
                
except Exception as e:
    print(f"No MJPEG stream at this endpoint: {e}")

cv2.destroyAllWindows()