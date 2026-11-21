import json
import numpy as np
import tkinter as tk
from adafruit_servokit import ServoKit

# ===================== SERVO SETUP =====================
kit = ServoKit(channels=16)
for i in range(3):
    kit.servo[i].set_pulse_width_range(500, 2500)

# ===================== SAFE LIMITS (YOUR VALUES) =====================
SERVO_MIN = [133, 126, 128]   # do NOT go below
SERVO_MAX = [85, 85, 77]      # do NOT go above

# ===================== STORAGE =====================
calibration = {
    "LEVEL": [129, 121, 129],
    "TOP":   None,
    "BOTTOM":None,
    "LEFT":  None,
    "RIGHT": None
}

current_mode = "LEVEL"

# ===================== SERVO CONTROL =====================
def set_servos(a0, a1, a2):
    vals = [a0, a1, a2]
    for i in range(3):
        angle = max(SERVO_MAX[i], min(SERVO_MIN[i], vals[i]))
        kit.servo[i].angle = int(angle)

def update_servos(_=None):
    set_servos(s0.get(), s1.get(), s2.get())

# ===================== SAVE =====================
def save_position():
    calibration[current_mode] = [s0.get(), s1.get(), s2.get()]
    print(f"{current_mode} saved:", calibration[current_mode])

# ===================== MODE SWITCH =====================
def set_mode(mode):
    global current_mode
    current_mode = mode
    label.config(text=f"Adjust plate for: {mode}")

    if calibration[mode]:
        s0.set(calibration[mode][0])
        s1.set(calibration[mode][1])
        s2.set(calibration[mode][2])

# ===================== EXPORT =====================
def export_data():
    with open("plate_calibration.json", "w") as f:
        json.dump(calibration, f, indent=4)

    print("\n===== FINAL CALIBRATION =====")
    for k, v in calibration.items():
        print(k, ":", v)

    print("\nSaved to plate_calibration.json")

# ===================== GUI =====================
root = tk.Tk()
root.title("Ball & Plate – Manual Servo Calibration")
root.geometry("520x420")

label = tk.Label(root, text="Adjust plate for: LEVEL",
                 font=("Arial", 14, "bold"))
label.pack(pady=10)

# ---------- Sliders ----------
s0 = tk.Scale(root, from_=SERVO_MAX[0], to=SERVO_MIN[0],
              label="Servo 0", orient="horizontal", length=400,
              command=update_servos)
s0.set(calibration["LEVEL"][0])
s0.pack()

s1 = tk.Scale(root, from_=SERVO_MAX[1], to=SERVO_MIN[1],
              label="Servo 1", orient="horizontal", length=400,
              command=update_servos)
s1.set(calibration["LEVEL"][1])
s1.pack()

s2 = tk.Scale(root, from_=SERVO_MAX[2], to=SERVO_MIN[2],
              label="Servo 2", orient="horizontal", length=400,
              command=update_servos)
s2.set(calibration["LEVEL"][2])
s2.pack()

# ---------- Buttons ----------
frame = tk.Frame(root)
frame.pack(pady=10)

for m in ["LEVEL", "TOP", "BOTTOM", "LEFT", "RIGHT"]:
    tk.Button(frame, text=m, width=8,
              command=lambda x=m: set_mode(x)).pack(side="left", padx=3)

tk.Button(root, text="SAVE CURRENT POSITION",
          bg="lightblue", width=25,
          command=save_position).pack(pady=10)

tk.Button(root, text="EXPORT & PRINT RESULTS",
          bg="lightgreen", width=25,
          command=export_data).pack(pady=10)

# ===================== START =====================
update_servos()
root.mainloop()
