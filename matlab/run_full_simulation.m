%% Ball on Plate: Full Simulation and 3D Animation
% This script simulates the ball on plate system and provides a 3D visualization.
clear; clc; close all;

%% 1. Physical Parameters
g = 9.81;               % Gravity (m/s^2)
K = 5/7 * g;            % Plant gain
plate_size = 0.25;      % 25cm plate
ball_radius = 0.02;     % 20mm radius

%% 2. PID Controller Parameters (Tuned for "Fast but not Aggressive")
Kp = 2.5;
Ki = 0.1;
Kd = 1.2;

%% 3. Simulation Setup
t_end = 10;             % Simulation time (seconds)
dt = 0.02;              % Time step (50Hz)
t = 0:dt:t_end;
n = length(t);

% State vectors: [position; velocity]
x = zeros(2, n); 
y = zeros(2, n);
tilt_x = zeros(1, n);
tilt_y = zeros(1, n);

% Setpoints (Target position)
ref_x = 0.05 * sin(t);  % Moving target for demo
ref_y = 0.05 * cos(t);

% PID Variables
error_sum_x = 0; error_prev_x = 0;
error_sum_y = 0; error_prev_y = 0;

%% 4. Run Simulation Loop
for i = 2:n
    % --- X-Axis Control ---
    err_x = ref_x(i) - x(1, i-1);
    error_sum_x = error_sum_x + err_x * dt;
    der_x = (err_x - error_prev_x) / dt;
    tilt_x(i) = Kp*err_x + Ki*error_sum_x + Kd*der_x;
    tilt_x(i) = max(min(tilt_x(i), 0.3), -0.3); % Limit tilt to ~17 degrees
    error_prev_x = err_x;
    
    % --- Y-Axis Control ---
    err_y = ref_y(i) - y(1, i-1);
    error_sum_y = error_sum_y + err_y * dt;
    der_y = (err_y - error_prev_y) / dt;
    tilt_y(i) = Kp*err_y + Ki*error_sum_y + Kd*der_y;
    tilt_y(i) = max(min(tilt_y(i), 0.3), -0.3);
    error_prev_y = err_y;
    
    % --- Physics Update (Double Integrator) ---
    % x_accel = K * tilt
    x_accel = K * tilt_x(i);
    x(2, i) = x(2, i-1) + x_accel * dt; % Velocity
    x(1, i) = x(1, i-1) + x(2, i) * dt;   % Position
    
    y_accel = K * tilt_y(i);
    y(2, i) = y(2, i-1) + y_accel * dt;
    y(1, i) = y(1, i-1) + y(2, i) * dt;
end

%% 5. 3D Visualization
figure('Color', 'w', 'Name', '3D Ball on Plate Simulation');
view(3); grid on; axis equal;
axis([-0.2 0.2 -0.2 0.2 -0.1 0.1]);
xlabel('X (m)'); ylabel('Y (m)'); zlabel('Z (m)');
hold on;

% Create Plate Graphic
[px, py] = meshgrid([-plate_size/2, plate_size/2]);
pz = zeros(2,2);
h_plate = surf(px, py, pz, 'FaceColor', [0.8 0.8 0.8], 'FaceAlpha', 0.8);

% Create Ball Graphic
[bx, by, bz] = sphere(20);
h_ball = surf(bx*ball_radius, by*ball_radius, bz*ball_radius + ball_radius, ...
              'FaceColor', [1 0.5 0], 'EdgeColor', 'none');
camlight; lighting gouraud;

% Animation Loop
for i = 1:5:n
    % Update Plate Rotation
    % Simplified rotation matrix for small angles
    R = [1 0 tilt_y(i); 0 1 -tilt_x(i); -tilt_y(i) tilt_x(i) 1];
    
    % Rotate plate vertices
    new_pz = px * tilt_y(i) - py * tilt_x(i);
    set(h_plate, 'ZData', new_pz);
    
    % Update Ball Position
    set(h_ball, 'XData', bx*ball_radius + x(1, i), ...
                'YData', by*ball_radius + y(1, i), ...
                'ZData', bz*ball_radius + ball_radius + (x(1, i)*tilt_y(i) - y(1, i)*tilt_x(i)));
    
    title(sprintf('Time: %.2fs | Pos: (%.2f, %.2f)', t(i), x(1, i), y(1, i)));
    drawnow;
end
