function S = get_power_spectrum(sigma2, b, a, w)
% Get ARMA filter power spectral
%
% Usage
% ======
% sigma2: the variance of noise
% b: the estimated filter coefficients b.
% a: the estimated filter coefficients a. For AR(p), a should have p
% elements
% w: the frequency where the power spectral is sampled
% return S: the power spectral of the sampled frequency
%
% Test code
% =========
%
% N = 100;
% w = pi * (-1 : 2/N : 1);
% S = get_power_spectrum(4, 1, [0, 0.81], w);
% plot(w, S)
% 
% REFERENCE: 
% ==========
%   现代数字信号处理，姚天任 孙洪 P124
%
% Copyright (C) 2014 bily Huazhong Unversity of Science and Technology
% Distributed under terms of the MIT license.

%% Check input
assert(iscolumn(a) || isrow(a), 'a should be a row or column vector');
if iscolumn(a)
    a = a';
end
assert(iscolumn(b) || isrow(b), 'b should be a row or column vector');
if iscolumn(b)
    b = b';
end

%% Main logic 
m = 1 : numel(b);
n = 1 : numel(a);
[M, N] = meshgrid(w, m); % avoid for loop by using meshgrid
[X, Y] = meshgrid(w, n); 
wm = M .* N;
wn = X .* Y;

S = sigma2 * (abs(b * exp(-1i * wm))).^2 ./ (abs(a * exp(-1i * wn))).^2;
end