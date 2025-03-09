import cv2
import numpy as np

def is_green(color_bgr):
    """Check if a given BGR color is within Wordle's green range."""
    # Convert BGR to HSV for better color detection
    color_hsv = cv2.cvtColor(np.uint8([[color_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
    
    # Define the green color range in HSV
    lower_green = np.array([35, 100, 100])  # Adjust based on Wordle's exact green color
    upper_green = np.array([85, 255, 255])
    
    return np.all(lower_green <= color_hsv) and np.all(color_hsv <= upper_green)

def process_video(video_path):
    """Analyze video frames to detect when a Wordle puzzle is solved."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second

    frame_count = 0
    solved_time = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        timestamp = frame_count / fps  # Convert frame count to time in seconds

        # Convert frame to HSV for color detection
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define Wordle's green color range
        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])

        # Create a mask for detecting green
        mask = cv2.inRange(hsv_frame, lower_green, upper_green)

        # Find contours of green areas
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        green_boxes = [cv2.boundingRect(c) for c in contours]  # Get bounding boxes

        # Assume a Wordle row has 5 green boxes in a horizontal line
        if len(green_boxes) >= 5:  # Simple check, may need refining
            solved_time = timestamp
            print(f"Wordle solved at {solved_time:.2f} seconds")
            break  # Stop once solution is detected

    cap.release()
    return solved_time

if __name__ == "__main__":
    video_file = r"downloads/.mp4"  # Replace with your downloaded video
    result_time = process_video(video_file)

    if result_time:
        print(f"Wordle was solved at {result_time:.2f} seconds")
    else:
        print("Wordle solution not detected in the video")
