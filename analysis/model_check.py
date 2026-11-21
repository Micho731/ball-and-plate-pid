"""Compare the two plant models of the ball-and-plate under the same PID gains,
in continuous time and at the real 10 Hz camera loop.  Requires: pip install control numpy
"""
import numpy as np
import control as ct

g, m, r = 9.81, 0.0027, 0.020   # gravity, ping-pong ball mass (kg) and radius (m)
d, L = 0.05, 0.30                # servo arm length, plate length (m)
Ts = 0.1                         # control loop period on the hardware (s)

models = {
    "solid ball, plate tilt input": 5 / 7 * g,                                  # J = 2/5 m r^2
    "hollow ball, servo angle input": m * g * d * r**2 / (L * (m * r**2 + 2 / 3 * m * r**2)),  # J = 2/3 m r^2
}
kp, ki, kd = 2.5, 0.1, 1.2
s = ct.tf("s")
z = ct.tf([1, 0], [1], Ts)

for name, K in models.items():
    G = K / s**2
    C = kp + ki / s + kd * s
    T = ct.feedback(C * G, 1)
    info = ct.step_info(T)
    _, pm, _, _ = ct.margin(C * G)
    Gd = ct.c2d(G, Ts, "zoh")
    Cd = kp + kd * (1 - z**-1) / Ts
    _, pm_d, _, _ = ct.margin(Cd * Gd * z**-1)      # PD, one frame of camera delay
    stable = max(abs(ct.poles(ct.feedback(Cd * Gd * z**-1, 1)))) < 1
    print(f"{name}: G(s) = {K:.3f}/s^2")
    print(f"  continuous PID: overshoot {info['Overshoot']:.0f}%, settling {info['SettlingTime']:.1f} s, phase margin {pm:.0f} deg")
    print(f"  10 Hz + 1-frame delay (PD): phase margin {pm_d:.0f} deg, {'stable' if stable else 'UNSTABLE'}")
