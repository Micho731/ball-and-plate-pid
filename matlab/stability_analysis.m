%% Ball on Plate Stability Analysis and PID Tuning
% This script performs stability analysis for the ball on plate system
% and calculates theoretical PID values.

clear; clc; close all;

%% 1. System Parameters
g = 9.81;           % Gravitational acceleration (m/s^2)
K_plant = 5/7 * g;  % Plant gain for a rolling ball

%% 2. Transfer Function
% G(s) = K_plant / s^2
s = tf('s');
G = K_plant / s^2;

fprintf('Plant Transfer Function G(s):\n');
disp(G);

%% 3. Open-Loop Stability Analysis
% The plant has two poles at the origin (s=0), making it unstable.
figure('Name', 'Open-Loop Analysis');
subplot(2,1,1);
rlocus(G);
title('Root Locus of the Open-Loop Plant');
grid on;

subplot(2,1,2);
bode(G);
title('Bode Plot of the Open-Loop Plant');
grid on;

%% 4. PID Controller Design
% A standard PID controller: C(s) = Kp + Ki/s + Kd*s
% For a double integrator, we need at least a PD controller for stability.

% Theoretical PID values (Initial Guesses)
Kp = 1.5;
Ki = 0.05;
Kd = 0.8;

C = Kp + Ki/s + Kd*s;

fprintf('Controller Transfer Function C(s):\n');
disp(C);

%% 5. Closed-Loop Stability Analysis
% T(s) = (C*G) / (1 + C*G)
L = C * G;          % Open-loop transfer function with controller
T = feedback(L, 1); % Closed-loop transfer function

fprintf('Closed-Loop Transfer Function T(s):\n');
disp(T);

% Step Response
figure('Name', 'Closed-Loop Step Response');
step(T);
title('Step Response of the Controlled System');
grid on;

% Stability Margins
figure('Name', 'Stability Margins');
margin(L);
grid on;

%% 6. Root Locus with Controller
figure('Name', 'Root Locus with PID');
rlocus(L);
title('Root Locus of the Controlled System');
grid on;

%% 7. Summary of Stability
[gm, pm, wcg, wcp] = margin(L);
fprintf('\n--- Stability Summary ---\n');
fprintf('Gain Margin: %.2f dB\n', 20*log10(gm));
fprintf('Phase Margin: %.2f degrees\n', pm);
fprintf('Phase Margin Frequency: %.2f rad/s\n', wcp);

if pm > 0
    fprintf('The system is STABLE.\n');
else
    fprintf('The system is UNSTABLE.\n');
end
