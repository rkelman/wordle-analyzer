import cv2
import numpy as np
import matplotlib.pyplot as plt

def analyze_video(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video at {video_path}")
        return
    
    # Get video properties
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video Information:")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")
    print(f"Frame Count: {frame_count}")
    print(f"Duration: {frame_count/fps:.2f} seconds")
    
    # Analysis variables
    frame_brightness = []
    motion_scores = []
    prev_frame = None
    sample_interval = max(1, frame_count // 100)  # Sample ~100 frames
    
    # Process video
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Only analyze every nth frame to speed up processing
        if frame_idx % sample_interval == 0:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate average brightness
            brightness = np.mean(gray)
            frame_brightness.append(brightness)
            
            # Calculate motion (difference between consecutive frames)
            if prev_frame is not None:
                motion = np.mean(cv2.absdiff(gray, prev_frame))
                motion_scores.append(motion)
            
            prev_frame = gray
            
            # Optional: Save a sample frame (e.g., at 10 seconds)
            if abs(frame_idx - int(10 * fps)) < 5:
                cv2.imwrite('sample_frame.jpg', frame)
                
        frame_idx += 1
    
    # Release the video file
    cap.release()
    
    # Plot analysis results
    plt.figure(figsize=(12, 6))
    
    # Brightness plot
    plt.subplot(2, 1, 1)
    plt.plot(np.linspace(0, frame_count/fps, len(frame_brightness)), frame_brightness)
    plt.title('Brightness Over Time')
    plt.ylabel('Average Brightness')
    plt.xlabel('Time (seconds)')
    
    # Motion plot
    if motion_scores:
        plt.subplot(2, 1, 2)
        plt.plot(np.linspace(0, frame_count/fps, len(motion_scores)), motion_scores)
        plt.title('Motion Detection')
        plt.ylabel('Motion Score')
        plt.xlabel('Time (seconds)')
    
    plt.tight_layout()
    plt.savefig('video_analysis.png')
    plt.show()
    
    return {
        "resolution": (width, height),
        "fps": fps,
        "frame_count": frame_count,
        "duration": frame_count/fps,
        "avg_brightness": np.mean(frame_brightness) if frame_brightness else 0,
        "max_motion": np.max(motion_scores) if motion_scores else 0
    }

# Example usage:
if __name__ == "__main__":
    video_path = r"downloads\January 20, 2025.mp4"  # Replace with your video path
    results = analyze_video(video_path)
    print(f"\nAnalysis Results Summary:")
    for key, value in results.items():
        print(f"{key}: {value}")