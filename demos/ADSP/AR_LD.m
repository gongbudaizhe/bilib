function [A, S, G] = AR_LD(R, p)
% Provided the autocorrelation R, get AR(p) model parameters 
% using Levinson-Durbin algorithm
%
% Usage
% ======
% R: R should be a p+1 by p+1 Toeplitz matrix with nonzero main diagonal
% p: the AR order
% return A: the history of filter coefficient a
% return S: the history of noise variance
% return G: the history of reflection coefficent
%
% Test code
% =========
% n_samples = 1000;
% 
% rng(0); % use fixed seed for reproducibility
% 
% % AR(2), b0 = 1, a1 = 0, a2 = 0.81
% p = 2;
% b = 1;
% a = [1, 0, 0.81];
% 
% % Get input data
% sigma = 2;
% u = sigma * randn(n_samples, 1); % white noise
% x = filter(b, a, u);
% 
% % Get autocorrelation matrix R
% H = corrmtx(x, p + 1);
% R = H' * H;
% 
% [A, S, G] = AR_LD(R, p);
% REFERENCE: 
% ==========
%   现代数字信号处理，姚天任 孙洪 P126
%
% Copyright (C) 2014 bily Huazhong Unversity of Science and Technology
% Distributed under terms of the MIT license.

% Initialization
S = zeros(p + 1, 1); % history of noise variance 
A = zeros(p + 1); % history of filter coefficent a
G = zeros(p, 1); % history of reflection coefficent
S(1) = R(1, 1);
A(1, 1) = 1;

for k = 2 : p + 1
    sigma2 = S(k - 1);
    a = A(1 : k, k - 1);
    r = R(k, 1 : k);
    D = r * a; % k multiplication, k - 1 addition
    gamma = D / sigma2; % 1 multiplication
    A(1 : k, k) = a - gamma * a(end : -1 : 1); % k multiplication, k addition
    S(k) = sigma2 * (1 - gamma^2); % 2 multiplication, 2 addition
    G(k - 1) = gamma;
end

end