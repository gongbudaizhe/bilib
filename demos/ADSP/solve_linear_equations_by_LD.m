function x = solve_linear_equations_by_LD(T, y)
% Solve linear equations y = Tx using Levinson-Durbin algorithm
%
% Usage
% ======
% T: T should be a N by N Toeplitz matrix with nonzero main diagonal
% y: a vector which has N elements 
% return x: the solution of the linear equation
%
% Test code
% =========
%
% c = [1  2  3  4  5];
% r = [1.5  2.5  3.5  4.5  5.5];
% T1 = toeplitz(c, r);
% T2 = toeplitz(c);
% x = rand(5, 1)
% y1 = T1 * x;
% y2 = T2 * x;
% x - solve_linear_equations_by_LD(T, y1)
% x - solve_linear_equations_by_LD(T, y2)
% 
% REFERENCE: 
% ==========
%   http://en.wikipedia.org/wiki/Levinson_recursion
%
% Copyright (C) 2014 bily Huazhong Unversity of Science and Technology
% Distributed under terms of the MIT license.

%% Check input

N = numel(y);
assert(T(1,1) ~= 0, 'T''s diagnoal should contain nonzero elements');
assert(size(T, 1) == N, 'T''s  height should be equal to y''s height');
assert(check_toeplitz_matrix(T), 'T should be Toeplitz matrix');

% if T is a symmetric matrix we can save some extra computation, since 
% forward vector and backward vector are row-reversals of each other.
if all(T' == T)
    is_symmetric = true;
else
    is_symmetric = false;
end
%% Compute forward and backward matrix
F = zeros(N); % the forward matrix, 
              % the n-th column is the n-th forward vector
              % with additional positions tilted by zeros
B = zeros(N); % the backward matrix, like forward matrix

F(:, 1) = [1 / T(1, 1); zeros(N - 1, 1)]; 
B(:, 1) = [zeros(N - 1, 1); 1 / T(1, 1)];

for ii = 2 : N
    f_pre = F(1 : ii, ii - 1);
    b_pre = B(end - ii + 1 : end, ii - 1);
    e_f = T(ii, 1 : ii) * f_pre;
    if is_symmetric
        e_b = e_f;
    else
        e_b = T(end - ii + 1, end - ii + 1: end) * b_pre;    
    end
    f = f_pre / (1 - e_b * e_f) - b_pre * e_f / (1 - e_b * e_f);
    if is_symmetric
        b = f(end : -1 : 1);
    else
        b = b_pre / (1 - e_b * e_f) - f_pre * e_b / (1 - e_b * e_f);
    end
    F(1 : ii, ii) = f;
    B(end - ii + 1 : end, ii) = b;
end

%% Solve the equation recursively
x = zeros(N, 1);
x(1) = y(1) / T(1,1);
for ii = 2 : N
    x_pre = x(1 : ii);
    b = B(end - ii + 1 : end, ii);
    e_x = T(ii, 1 : ii) * x_pre;
    x(1 : ii) = x_pre + (y(ii) - e_x) * b;
end

end

function is_toeplitz = check_toeplitz_matrix(A)
% check that if matrix A is Toeplitz matrix
is_toeplitz = false;
N = size(A, 1);
if size(A, 1) ~= size(A, 2)
    return 
end
if ~check_diagnoal_equal(A)
    return
end
for ii = 1 : N -1
    if ~check_diagnoal_equal(A(end - ii + 1 : end, 1 : ii))
        return
    end
    if ~check_diagnoal_equal(A(1 : ii, end - ii + 1 : end))
        return
    end
end
is_toeplitz = true;
end

function is_equal = check_diagnoal_equal(A)
    diagonal = diag(A);
    if any(diagonal(1) ~= diagonal)
        is_equal = false;
    else
        is_equal = true;
    end
end