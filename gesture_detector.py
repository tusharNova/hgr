import cv2
import mediapipe as mp
import time
import math

class GestureDetector:
    """
    Hand gesture detection using MediaPipe and OpenCV
    Detects hand landmarks and recognizes basic gestures
    """
    
    def __init__(self, 
                 static_image_mode=False,
                 max_num_hands=2,
                 min_detection_confidence=0.7,
                 min_tracking_confidence=0.7):
        """
        Initialize the gesture detector
        
        Args:
            static_image_mode: If True, treats images as independent frames
            max_num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # For drawing hand landmarks
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Hand landmark indices (21 points total)
        self.WRIST = 0
        self.THUMB_TIP = 4
        self.INDEX_TIP = 8
        self.MIDDLE_TIP = 12
        self.RING_TIP = 16
        self.PINKY_TIP = 20
        
        # For FPS calculation
        self.prev_time = 0
        self.current_time = 0
        
    
    def find_hands(self, frame, draw=True):
        """
        Detect hands in the frame
        
        Args:
            frame: Input image/frame from camera
            draw: Whether to draw hand landmarks on frame
            
        Returns:
            frame: Frame with drawn landmarks (if draw=True)
            results: MediaPipe hand detection results
        """
        
        # Convert BGR to RGB (MediaPipe uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        # Draw hand landmarks if detected
        if results.multi_hand_landmarks and draw:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        return frame, results
    
    
    def get_hand_landmarks(self, frame, results, hand_number=0):
        """
        Get landmark positions for a specific hand
        
        Args:
            frame: Input frame
            results: MediaPipe detection results
            hand_number: Which hand to get (0 for first hand, 1 for second)
            
        Returns:
            landmarks_list: List of [id, x, y] for each landmark
        """
        
        landmarks_list = []
        
        if results.multi_hand_landmarks:
            if len(results.multi_hand_landmarks) > hand_number:
                hand = results.multi_hand_landmarks[hand_number]
                
                # Get frame dimensions
                h, w, c = frame.shape
                
                # Extract landmark positions
                for id, landmark in enumerate(hand.landmark):
                    # Convert normalized coordinates to pixel coordinates
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    landmarks_list.append([id, cx, cy])
        
        return landmarks_list
    
    
    def count_fingers(self, landmarks_list):
        """
        Count the number of extended fingers
        
        Args:
            landmarks_list: List of hand landmarks
            
        Returns:
            finger_count: Number of fingers extended (0-5)
        """
        
        if len(landmarks_list) == 0:
            return 0
        
        fingers = []
        
        # Thumb (special case - check horizontal distance)
        if landmarks_list[self.THUMB_TIP][1] < landmarks_list[self.THUMB_TIP - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Other 4 fingers (check if tip is above the joint below it)
        finger_tips = [self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]
        
        for tip in finger_tips:
            if landmarks_list[tip][2] < landmarks_list[tip - 2][2]:  # tip.y < joint.y
                fingers.append(1)
            else:
                fingers.append(0)
        
        finger_count = fingers.count(1)
        return finger_count
    
    
    def detect_gesture(self, landmarks_list):
        """
        Detect specific gestures based on hand landmarks
        
        Args:
            landmarks_list: List of hand landmarks
            
        Returns:
            gesture_name: Name of detected gesture
        """
        
        if len(landmarks_list) == 0:
            return "No Hand"
        
        finger_count = self.count_fingers(landmarks_list)
        
        # Define gestures based on finger count
        if finger_count == 0:
            return "FIST (OFF)"
        elif finger_count == 5:
            return "OPEN PALM (ON)"
        elif finger_count == 1:
            return "ONE FINGER"
        elif finger_count == 2:
            return "TWO FINGERS"
        elif finger_count == 3:
            return "THREE FINGERS"
        elif finger_count == 4:
            return "FOUR FINGERS"
        else:
            return "Unknown"
    
    
    def calculate_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points
        
        Args:
            point1: [id, x, y]
            point2: [id, x, y]
            
        Returns:
            distance: Distance between points
        """
        
        x1, y1 = point1[1], point1[2]
        x2, y2 = point2[1], point2[2]
        
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance
    
    
    def calculate_fps(self, frame):
        """
        Calculate and display FPS on frame
        
        Args:
            frame: Input frame
            
        Returns:
            frame: Frame with FPS text
            fps: Current FPS value
        """
        
        self.current_time = time.time()
        fps = 1 / (self.current_time - self.prev_time)
        self.prev_time = self.current_time
        
        # Display FPS on frame
        cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame, fps
    
    
    def close(self):
        """
        Release resources
        """
        self.hands.close()


def main():
    """
    Test the gesture detector with webcam
    """
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)  # Width
    cap.set(4, 720)   # Height
    
    # Initialize gesture detector
    detector = GestureDetector(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    
    print("=" * 50)
    print("GESTURE DETECTION STARTED")
    print("=" * 50)
    print("Controls:")
    print("  - Press 'q' to quit")
    print("  - Press 's' to take screenshot")
    print("\nGestures:")
    print("  - FIST (0 fingers) = OFF")
    print("  - OPEN PALM (5 fingers) = ON")
    print("=" * 50)
    
    while True:
        success, frame = cap.read()
        
        if not success:
            print("Failed to read from camera")
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect hands
        frame, results = detector.find_hands(frame, draw=True)
        
        # Get landmarks for first hand
        landmarks = detector.get_hand_landmarks(frame, results, hand_number=0)
        
        # Detect gesture
        gesture = detector.detect_gesture(landmarks)
        
        # Display gesture name
        cv2.putText(frame, f'Gesture: {gesture}', (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        
        # Display finger count
        if len(landmarks) > 0:
            finger_count = detector.count_fingers(landmarks)
            cv2.putText(frame, f'Fingers: {finger_count}', (10, 110), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Calculate and display FPS
        frame, fps = detector.calculate_fps(frame)
        
        # Show frame
        cv2.imshow('Gesture Detection', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\nExiting...")
            break
        elif key == ord('s'):
            # Save screenshot
            filename = f'iimg/screenshot_{int(time.time())}.jpg'
            cv2.imwrite(filename, frame)
            print(f"Screenshot saved: {filename}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("Gesture detection stopped")


if __name__ == "__main__":
    main()