import cv2
import pytesseract
import numpy as np

# Load video
video_path = r"downloads/January 20, 2025.mp4"
cap = cv2.VideoCapture(video_path)
frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Get video FPS
frame_skip = int(frame_rate * 0.5)  # Process every 0.5 seconds

while cap.isOpened():
    frame_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
    timestamp = frame_pos / frame_rate
    ret, frame = cap.read()
    
    if not ret:
        break  # End of video
    
    if int(frame_pos) % frame_skip == 0:  # Process every 0.5s
        # Convert to grayscale and apply threshold
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # OCR to extract text
        text = pytesseract.image_to_string(thresh, config="--psm 6")
        
        # Debug: Print detected text
        print(f"Time {timestamp:.2f}s - OCR Output:\n{text}")

        # Check if a row is all green (you may need a regex to detect 5-letter words)
        if "SOLVED_WORD" in text:  
            print(f"🎉 Wordle solved at {timestamp:.2f} seconds!")
            break

cap.release()
cv2.destroyAllWindows()
