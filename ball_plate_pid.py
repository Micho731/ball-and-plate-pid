import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

import cv2 as cv
import numpy as np
import time
import tkinter as tk
from adafruit_servokit import ServoKit

# ===================== SERVO SETUP =====================
kit = ServoKit(channels=16)
for i in range(3):
    kit.servo[i].set_pulse_width_range(500, 2500)

initial_angle = np.array([121, 111, 108], dtype=float)
min_motor = np.array([126, 116, 114])  # lowest safe position
max_motor = np.array([116, 106, 104])  # highest safe position

def initialPos():
    for i in range(3):
        kit.servo[i].angle = int(initial_angle[i])

# ===================== CAMERA =====================
cap = cv.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Camera not detected")

# ===================== HSV =====================
LOWER_HSV = np.array([0, 0, 227])
UPPER_HSV = np.array([171, 255, 255])

# ===================== GLOBAL =====================
edges = {}
manual_crop = None
center_x, center_y = 0, 0
started = False
prev_error = np.zeros(3)
integral = np.zeros(3)
last_time = time.time()

# ===================== BALL FINDER =====================
def ballFinder():
    ret, frame = cap.read()
    if not ret or manual_crop is None:
        return None, None, None

    x1, y1, x2, y2 = manual_crop
    plate = frame[y1:y2, x1:x2]

    hsv = cv.cvtColor(plate, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, LOWER_HSV, UPPER_HSV)
    mask = cv.medianBlur(mask, 5)

    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return plate, mask, None

    cnt = max(contours, key=cv.contourArea)
    if cv.contourArea(cnt) < 400:
        return plate, mask, None

    (x, y), r = cv.minEnclosingCircle(cnt)
    return plate, mask, (int(x + x1), int(y + y1))

# ===================== CALIBRATION =====================
def run_calibration():
    global edges, center_x, center_y, manual_crop

    points = []

    def click(event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN and len(points) < 5:
            points.append((x, y))

    cv.namedWindow("Calibration")
    cv.setMouseCallback("Calibration", click)
    print("Click: Center, Top, Bottom, Left, Right")

    while len(points) < 5:
        ret, frame = cap.read()
        if not ret:
            continue
        for p in points:
            cv.circle(frame, p, 5, (0, 255, 0), -1)
        cv.imshow("Calibration", frame)
        cv.waitKey(1)

    cv.destroyWindow("Calibration")

    center_x, center_y = points[0]
    edges = {
        "top": points[1],
        "bottom": points[2],
        "left": points[3],
        "right": points[4],
    }

    print("Draw manual crop rectangle (ENTER to confirm)")
    crop_start, crop_end = None, None
    drawing = False

    def crop_mouse(event, x, y, flags, param):
        nonlocal crop_start, crop_end, drawing
        if event == cv.EVENT_LBUTTONDOWN:
            crop_start = (x, y)
            drawing = True
        elif event == cv.EVENT_MOUSEMOVE and drawing:
            crop_end = (x, y)
        elif event == cv.EVENT_LBUTTONUP:
            crop_end = (x, y)
            drawing = False

    cv.namedWindow("Manual Crop")
    cv.setMouseCallback("Manual Crop", crop_mouse)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        if crop_start and crop_end:
            cv.rectangle(frame, crop_start, crop_end, (255, 0, 0), 2)
        cv.imshow("Manual Crop", frame)
        if cv.waitKey(1) == 13 and crop_start and crop_end:
            break

    cv.destroyWindow("Manual Crop")
    x1 = min(crop_start[0], crop_end[0])
    y1 = min(crop_start[1], crop_end[1])
    x2 = max(crop_start[0], crop_end[0])
    y2 = max(crop_start[1], crop_end[1])
    manual_crop = (x1, y1, x2, y2)
    print("Manual crop set:", manual_crop)

# ===================== PID =====================
Kp = np.array([0.25, 0.25, 0.25])
Ki = np.array([0.0, 0.0, 0.0])
Kd = np.array([0.08, 0.08, 0.08])

def pid_controller(dx, dy, dt):
    global prev_error, integral

    # ===== Correct mapping for your table (⬆ decrease angle, ⬇ increase angle) =====
    e0 = -dx + dy  # Servo 0 (top-right)
    e1 =  dx + dy  # Servo 1 (top-left)
    e2 = -dy       # Servo 2 (bottom)

    error = np.array([e0, e1, e2], dtype=float)

    integral += error * dt
    derivative = (error - prev_error) / dt if dt > 0 else 0
    prev_error = error

    return Kp * error + Ki * integral + Kd * derivative

# ===================== MOTOR =====================
def move_motors(pid_values):
    for i in range(3):
        angle = initial_angle[i] + pid_values[i]
        angle = np.clip(angle, max_motor[i], min_motor[i])
        kit.servo[i].angle = int(angle)

def reset_servos():
    initialPos()
    print("Servos reset")

# ===================== PREVIEW =====================
def preview_loop():
    plate, mask, ball = ballFinder()
    if plate is not None:
        if ball:
            cv.circle(plate,
                      (ball[0] - manual_crop[0], ball[1] - manual_crop[1]),
                      8, (0, 0, 255), 2)
        cv.imshow("Ball Preview", plate)
        cv.imshow("Mask", mask)
    cv.waitKey(1)
    window.after(30, preview_loop)

# ===================== MAIN =====================
def main_loop():
    global last_time
    now = time.time()
    dt = now - last_time
    last_time = now

    if started:
        _, _, ball = ballFinder()
        if ball:
            dx = ball[0] - center_x
            dy = ball[1] - center_y
            pid = pid_controller(dx, dy, dt)
            move_motors(pid)
        else:
            initialPos()

    window.after(100, main_loop)

# ===================== GUI =====================
window = tk.Tk()
window.title("Ball & Plate PID")

def start_pid():
    global started
    started = not started
    start_btn.config(text="Stop" if started else "Start")

start_btn = tk.Button(window, text="Start", command=start_pid, width=12)
start_btn.pack(pady=10)

reset_btn = tk.Button(window, text="Reset Servos", command=reset_servos, width=12)
reset_btn.pack(pady=5)

def update_pid(_=None):
    Kp[:] = kp_slider.get()
    Ki[:] = ki_slider.get()
    Kd[:] = kd_slider.get()

kp_slider = tk.Scale(window, from_=0.05, to=10.0, resolution=0.01,
                     orient="horizontal", label="Kp", length=300, command=update_pid)
kp_slider.set(0.25)
kp_slider.pack()

ki_slider = tk.Scale(window, from_=0.0, to=10.0, resolution=0.001,
                     orient="horizontal", label="Ki", length=300, command=update_pid)
ki_slider.pack()

kd_slider = tk.Scale(window, from_=0.0, to=10.0, resolution=0.001,
                     orient="horizontal", label="Kd", length=300, command=update_pid)
kd_slider.set(0.08)
kd_slider.pack()

# ===================== START =====================
initialPos()
run_calibration()
preview_loop()
main_loop()
window.mainloop()
