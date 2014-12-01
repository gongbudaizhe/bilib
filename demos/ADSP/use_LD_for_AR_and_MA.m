clear all; close all; clc

rng(0); % use fixed seed for reproducibility
n_samples = 1000;
sigma = 1;
u = sigma * randn(n_samples, 1); % white noise

%% Use AR(2) model to estimate AR(2) process
% AR(2) process with coefficients b0 = 1, a0 = 1, a1 = 0, a2 = 0.81
p = 2;
b = 1;
a = [1, 0, 0.81];

% Get input data
x = filter(b, a, u);

% Get autocorrelation matrix R
H = corrmtx(x, p + 1);
R = H' * H;

% Estimate AR coefficient
[A, S, G] = AR_LD(R, p);
G % show reflection coefficients
A % show direct form coefficients

% Plot the power spectrum
N = 1000;
w = pi * (-1 : 2/N : 1);
S_t = get_power_spectrum(sigma^2, 1, a, w); % the ground truth
S_e = get_power_spectrum(S(end), 1, A(:, end), w);
figure(1)
plot(w, S_e, 'b', w, S_t, '--r')
xlabel('\omega'); ylabel('S'); 
title('Use AR(2) model to estimate AR(2) process')
legend('estimated', 'ground truth')

%% Use AR(10) model to estimate MA(2) process 
% MA(2) process with coefficients a0 = 1, b0 = 1, b1 = 1, b2 = 1
p = 10; % this is the estimated model order. 
        % It can be different from the acctual order of the process
b = [1, 1, 1];
a = 1;

% Get input data
x = filter(b, a, u);

% Get autocorrelation matrix R
H = corrmtx(x, p + 1);
R = H' * H;

% Estimate AR coefficient
[A, S, G] = AR_LD(R, p);
G % show reflection coefficients
A % show direct form coefficients

% Plot the power spectrum
N = 1000;
w = pi * (-1 : 2/N : 1);
S_t = get_power_spectrum(sigma^2, b, 1, w); % the ground truth
S_e = get_power_spectrum(S(end), 1, A(:, end), w);
figure(2)
plot(w, S_e, 'b', w, S_t, '--r')
xlabel('\omega'); ylabel('S'); 
title('Use AR(10) model to estimate MA(2) process')
legend('estimated', 'ground truth')