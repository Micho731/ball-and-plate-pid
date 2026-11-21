import cv2 as cv
import numpy as np

# --- Open camera ---
cap = None
for i in range(0, 6):
    temp_cap = cv.VideoCapture(i)
    if temp_cap.isOpened():
        cap = temp_cap
        print(f"Camera opened at index {i}")
        break

if cap is None:
    raise RuntimeError("No camera found.")

cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

# --- Callback for trackbars ---
def nothing(x):
    pass

# --- Create window and trackbars ---
cv.namedWindow("HSV Mask")
cv.createTrackbar("H Low", "HSV Mask", 5, 179, nothing)
cv.createTrackbar("H High", "HSV Mask", 25, 179, nothing)
cv.createTrackbar("S Low", "HSV Mask", 120, 255, nothing)
cv.createTrackbar("S High", "HSV Mask", 255, 255, nothing)
cv.createTrackbar("V Low", "HSV Mask", 120, 255, nothing)
cv.createTrackbar("V High", "HSV Mask", 255, 255, nothing)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Convert to HSV
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # Get trackbar positions
    h_low = cv.getTrackbarPos("H Low", "HSV Mask")
    h_high = cv.getTrackbarPos("H High", "HSV Mask")
    s_low = cv.getTrackbarPos("S Low", "HSV Mask")
    s_high = cv.getTrackbarPos("S High", "HSV Mask")
    v_low = cv.getTrackbarPos("V Low", "HSV Mask")
    v_high = cv.getTrackbarPos("V High", "HSV Mask")

    lower = np.array([h_low, s_low, v_low])
    upper = np.array([h_high, s_high, v_high])
    mask = cv.inRange(hsv, lower, upper)

    # Show frames
    cv.imshow("Original", frame)
    cv.imshow("HSV Mask", mask)

    key = cv.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break

cap.release()
cv.destroyAllWindows()
