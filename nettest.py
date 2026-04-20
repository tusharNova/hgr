import urllib.request
import urllib.error

esp_ip = "192.168.137.41"
endpoints = [
    "/",
    "/stream",
    "/video",
    "/cam-hi.jpg",
    "/cam-lo.jpg",
    "/capture",
    "/photo",
    "/image",
    "/jpeg",
    "/live",
    "/mjpeg",
    "/video_feed",
    "/?action=stream",
    "/html",
    "/index.html",
    "/status",
    "/info"
]

print(f"Testing ESP32-CAM at {esp_ip}")
print("="*50)

for endpoint in endpoints:
    url = f"http://{esp_ip}{endpoint}"
    try:
        req = urllib.request.urlopen(url, timeout=2)
        content_type = req.headers.get('Content-Type', 'unknown')
        print(f"✅ WORKING: {url}")
        print(f"   → Status: {req.status}")
        print(f"   → Type: {content_type}")
        
        # If it's an image, save it
        if 'image' in content_type:
            print(f"   → This is a camera image endpoint!")
            with open(f"test_image.jpg", "wb") as f:
                f.write(req.read())
            print(f"   → Saved image to test_image.jpg")
            print("\n🎯 USE THIS URL in your server.py!")
            print(f"   snapshot_url: '{url}'")
            break
    except urllib.error.HTTPError as e:
        print(f"❌ {url} -> HTTP {e.code}")
    except Exception as e:
        print(f"❌ {url} -> Error")

print("="*50)