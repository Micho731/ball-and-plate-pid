import tkinter as tk
from adafruit_servokit import ServoKit

# --- Initialize servo kit ---
kit = ServoKit(channels=16)
kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)
kit.servo[2].set_pulse_width_range(500, 2500)

# --- Initial angles (adjust if your plate is not level) ---
initial_angle = [129, 122, 129]
kit.servo[0].angle = initial_angle[0]
kit.servo[1].angle = initial_angle[1]
kit.servo[2].angle = initial_angle[2]

# --- Current motor angles ---
current_angle = initial_angle.copy()

# --- Functions to move motors ---
def move_motor(motor, delta):
    """Move motor 0,1,2 by delta degrees (+ or -)"""
    current_angle[motor] += delta
    # Clamp to servo limits
    if motor == 0:
        current_angle[motor] = max(85, min(175, current_angle[motor]))
    elif motor == 1:
        current_angle[motor] = max(85, min(175, current_angle[motor]))
    elif motor == 2:
        current_angle[motor] = max(77, min(165, current_angle[motor]))
    kit.servo[motor].angle = current_angle[motor]
    print(f"Motor {motor} moved to {current_angle[motor]}°")

def reset_motor(motor):
    """Reset motor to initial angle"""
    current_angle[motor] = initial_angle[motor]
    kit.servo[motor].angle = current_angle[motor]
    print(f"Motor {motor} reset to {current_angle[motor]}°")

# --- Tkinter GUI ---
window = tk.Tk()
window.title("Motor Calibration")

# Motor 0
tk.Label(window, text="Motor 0").grid(row=0, column=0)
tk.Button(window, text="+5°", command=lambda: move_motor(0, 5)).grid(row=0, column=1)
tk.Button(window, text="-5°", command=lambda: move_motor(0, -5)).grid(row=0, column=2)
tk.Button(window, text="Reset", command=lambda: reset_motor(0)).grid(row=0, column=3)

# Motor 1
tk.Label(window, text="Motor 1").grid(row=1, column=0)
tk.Button(window, text="+5°", command=lambda: move_motor(1, 5)).grid(row=1, column=1)
tk.Button(window, text="-5°", command=lambda: move_motor(1, -5)).grid(row=1, column=2)
tk.Button(window, text="Reset", command=lambda: reset_motor(1)).grid(row=1, column=3)

# Motor 2
tk.Label(window, text="Motor 2").grid(row=2, column=0)
tk.Button(window, text="+5°", command=lambda: move_motor(2, 5)).grid(row=2, column=1)
tk.Button(window, text="-5°", command=lambda: move_motor(2, -5)).grid(row=2, column=2)
tk.Button(window, text="Reset", command=lambda: reset_motor(2)).grid(row=2, column=3)

tk.Label(window, text="Instructions:").grid(row=3, column=0, columnspan=4)
tk.Label(window, text="1. Place ball on center of plate.").grid(row=4, column=0, columnspan=4)
tk.Label(window, text="2. Press +5° or -5° for each motor and observe ball movement.").grid(row=5, column=0, columnspan=4)
tk.Label(window, text="3. Note the direction ball moves for each motor.").grid(row=6, column=0, columnspan=4)
tk.Label(window, text="4. Use this info to adjust PID signs in your main program.").grid(row=7, column=0, columnspan=4)

window.mainloop()
