import time
import numpy as np
from adafruit_servokit import ServoKit
import tkinter as tk

# ====== Servo Setup ======
kit = ServoKit(channels=16)
for i in range(3):
    kit.servo[i].set_pulse_width_range(500, 2500)

initial_angle = np.array([129, 121, 129], dtype=float)
min_motor = np.array([85, 85, 77])
max_motor = np.array([175, 175, 165])

def set_servo(servo_id, angle):
    angle = np.clip(angle, min_motor[servo_id], max_motor[servo_id])
    kit.servo[servo_id].angle = int(angle)

def move_servo(servo_id, delta):
    new_angle = initial_angle[servo_id] + delta
    set_servo(servo_id, new_angle)

def reset_servos():
    for i in range(3):
        kit.servo[i].angle = int(initial_angle[i])

# ====== GUI ======
window = tk.Tk()
window.title("Servo Test Plate")

servo_vars = [tk.DoubleVar(value=initial_angle[i]) for i in range(3)]

def update_servo(i, var):
    set_servo(i, var.get())

for i in range(3):
    tk.Label(window, text=f"Servo {i}").pack()
    s = tk.Scale(window, from_=min_motor[i], to=max_motor[i],
                 orient="horizontal", variable=servo_vars[i],
                 length=400, command=lambda val, idx=i: update_servo(idx, servo_vars[idx]))
    s.pack()

tk.Button(window, text="Reset Servos", command=reset_servos).pack(pady=10)
tk.Button(window, text="Quit", command=window.destroy).pack(pady=5)

reset_servos()
window.mainloop()
