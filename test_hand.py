"""
Simple test script to demonstrate gesture detection
This shows how to use the GestureDetector class
"""

from gesture_detector import GestureDetector
import cv2
import time


def simple_test():
    """
    Simple test - just detect and display gestures
    """
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Cannot open camera!")
        return
    
    # Initialize detector
    detector = GestureDetector()
    
    print("\n" + "="*60)
    print("SIMPLE GESTURE TEST")
    print("="*60)
    print("\nTry these gestures:")
    print("  ✊ FIST (close all fingers) - This will be 'OFF' command")
    print("  ✋ OPEN PALM (all fingers open) - This will be 'ON' command")
    print("\nPress 'q' to quit")
    print("="*60 + "\n")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Mirror the frame
        frame = cv2.flip(frame, 1)
        
        # Detect hands and get results
        frame, results = detector.find_hands(frame, draw=True)
        
        # Get hand landmarks
        landmarks = detector.get_hand_landmarks(frame, results)
        
        # Detect gesture
        gesture = detector.detect_gesture(landmarks)
        
        # Get finger count
        finger_count = 0
        if len(landmarks) > 0:
            finger_count = detector.count_fingers(landmarks)
        
        # Display information
        cv2.putText(frame, f'Gesture: {gesture}', (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)
        
        cv2.putText(frame, f'Fingers: {finger_count}', (10, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Add FPS
        frame, fps = detector.calculate_fps(frame)
        
        # Show frame
        cv2.imshow('Gesture Test', frame)
        
        # Print to console when gesture changes
        if gesture in ["FIST (OFF)", "OPEN PALM (ON)"]:
            print(f"Detected: {gesture}")
        
        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("\nTest completed!")


def device_control_simulation():
    """
    Simulate device control based on gestures
    This shows how gestures will control devices
    """
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Cannot open camera!")
        return
    
    # Initialize detector
    detector = GestureDetector()
    
    # Simulated device states
    devices = {
        "Device 1": False,  # OFF
        "Device 2": False,  # OFF
        "Device 3": False,  # OFF
    }
    
    current_device = "Device 1"
    last_gesture = None
    gesture_start_time = 0
    gesture_hold_time = 1.5  # Hold gesture for 1.5 seconds to trigger
    
    print("\n" + "="*60)
    print("DEVICE CONTROL SIMULATION")
    print("="*60)
    print("\nGestures:")
    print("  ✋ OPEN PALM (hold 1.5s) - Turn ON current device")
    print("  ✊ FIST (hold 1.5s) - Turn OFF current device")
    print("  1️⃣ ONE FINGER - Select Device 1")
    print("  2️⃣ TWO FINGERS - Select Device 2")
    print("  3️⃣ THREE FINGERS - Select Device 3")
    print("\nPress 'q' to quit")
    print("="*60 + "\n")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Mirror the frame
        frame = cv2.flip(frame, 1)
        
        # Detect hands
        frame, results = detector.find_hands(frame, draw=True)
        landmarks = detector.get_hand_landmarks(frame, results)
        gesture = detector.detect_gesture(landmarks)
        
        # Check if gesture is held
        if gesture == last_gesture and gesture in ["FIST (OFF)", "OPEN PALM (ON)"]:
            hold_duration = time.time() - gesture_start_time
            
            if hold_duration >= gesture_hold_time:
                # Execute command
                if gesture == "OPEN PALM (ON)":
                    devices[current_device] = True
                    print(f"✓ {current_device} turned ON")
                elif gesture == "FIST (OFF)":
                    devices[current_device] = False
                    print(f"✗ {current_device} turned OFF")
                
                # Reset timer
                gesture_start_time = time.time()
        else:
            gesture_start_time = time.time()
            last_gesture = gesture
        
        # Device selection based on finger count
        if len(landmarks) > 0:
            finger_count = detector.count_fingers(landmarks)
            if finger_count == 1:
                current_device = "Device 1"
            elif finger_count == 2:
                current_device = "Device 2"
            elif finger_count == 3:
                current_device = "Device 3"
        
        # Display information
        y_offset = 50
        cv2.putText(frame, f'Gesture: {gesture}', (10, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        
        y_offset += 50
        cv2.putText(frame, f'Selected: {current_device}', (10, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display device states
        y_offset += 60
        for device_name, state in devices.items():
            status = "ON" if state else "OFF"
            color = (0, 255, 0) if state else (0, 0, 255)
            highlight = ">>>" if device_name == current_device else "   "
            
            cv2.putText(frame, f'{highlight} {device_name}: {status}', (10, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 35
        
        # Add FPS
        frame, fps = detector.calculate_fps(frame)
        
        # Show frame
        cv2.imshow('Device Control Simulation', frame)
        
        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("\nSimulation completed!")
    print("\nFinal Device States:")
    for device_name, state in devices.items():
        print(f"  {device_name}: {'ON' if state else 'OFF'}")


if __name__ == "__main__":
    print("\nChoose test mode:")
    print("1. Simple Gesture Test")
    print("2. Device Control Simulation")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        simple_test()
    elif choice == "2":
        device_control_simulation()
    else:
        print("Invalid choice!")