import cv2
import numpy as np

def is_tile_color(tile, color):
    """Check if a tile is green or yellow in Wordle (HSV-based)."""
    hsv_tile = cv2.cvtColor(tile, cv2.COLOR_BGR2HSV)

    if color == "green":
        #Dark mode green (approximate)
        lower_green = np.array([35, 40, 20])  # Adjust as needed
        upper_green = np.array([85, 255, 120])
    elif color == "yellow":
        # Dark mode yellow (approximate)
        lower_yellow = np.array([20, 40, 100]) 
        upper_yellow = np.array([35, 255, 180])
    else:
        return

    mask = cv2.inRange(hsv_tile, lower_bound, upper_bound)
    color_ratio = np.sum(mask) / (mask.shape[0] * mask.shape[1])  

    return color_ratio > 0.7  # At least 70% of the tile is this color

def extract_tiles(frame):
    """Detect and extract Wordle tiles dynamically."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tiles = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 40 < w < 100 and 40 < h < 100:  
            tiles.append((x, y, w, h))

    tiles = sorted(tiles, key=lambda t: (t[1], t[0]))  
    return tiles

def process_video(video_path, start_delay=1.0):
    """Analyze video, logging tile colors whenever a row changes."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    last_row_colors = {}

    # Skip first N seconds (default: 1 second)
    skip_frames = int(start_delay * fps)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count < skip_frames:
            continue  # Skip initial frames

        timestamp = frame_count / fps  

        # Detect and extract tiles
        tiles = extract_tiles(frame)
        if len(tiles) < 30:  # Ensure at least 6 rows × 5 columns
            continue  

        # Group tiles into rows (5 per row)
        rows = [tiles[i:i+5] for i in range(0, len(tiles), 5)]
        row_colors = {}

        for i, row in enumerate(rows):
            green_tiles = sum(1 for (x, y, w, h) in row if is_tile_color(frame[y:y+h, x:x+w], "green"))
            yellow_tiles = sum(1 for (x, y, w, h) in row if is_tile_color(frame[y:y+h, x:x+w], "yellow"))

            row_colors[i] = (green_tiles, yellow_tiles)

            # Log if row state has changed
            if i not in last_row_colors or last_row_colors[i] != row_colors[i]:
                print(f"Time {timestamp:.2f}s - Row {i+1}: {green_tiles} green, {yellow_tiles} yellow")

                # If all tiles in a row are green, Wordle is solved
                if green_tiles == 5:
                    print(f"✅ Wordle solved at {timestamp:.2f} seconds!")
                    cap.release()
                    return timestamp

        last_row_colors = row_colors  # Update last known row state

    cap.release()
    return None

if __name__ == "__main__":
    video_file = r"downloads/January 20, 2025.mp4"  # Replace with your downloaded video
    print("Analyzing video for Wordle solution...")  
    result_time = process_video(video_file, start_delay=1.5)  # Adjust delay as needed

    if result_time:
        print(f"✅ Wordle solved at {result_time:.2f} seconds!")
    else:
        print("No fully green row detected")
