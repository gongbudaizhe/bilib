from operator import mul    # or mul=lambda x,y:x*y
from fractions import Fraction

def nCk(n,k):
    try:
        result = nCk.LUT[(n, k)]
    except KeyError as e:
        result = int( reduce(mul, (Fraction(n-i, i+1) for i in range(k)), 1) )
        nCk.LUT[(n, k)] = result
    return result
nCk.LUT = {}

def fact(n):
    try:
        result = fact.LUT[n]
    except KeyError as e:
        if n == 1 or n == 0:
            result = 1
        else:
            result = n * fact(n-1)
        fact.LUT[n] = result
    return result
fact.LUT = {}

def line_up_one_side(x, n):
    if not 1 <= x <= n:
        return 0
    if n == 1:
        return 1
    elif n == 2:
        if x <= 1:
            return 0
        else:
            return 1
    elif x == n:
        return 1
    else:
        # split the line into two part
        nums = []
        for k in xrange(x-1, n):
            try:
                num_one_side = line_up_one_side.LUT[(x-1,k)]
            except KeyError as e:
                num_one_side = line_up_one_side(x-1, k)
            nums.append(fact(n-k-1) * nCk(n - 2, n - k - 1) * num_one_side)
        result = sum(nums)
        line_up_one_side.LUT[(x,n)] = result
        return result
line_up_one_side.LUT = {}

def answer(x, y, n):
    nums = 0
    for k in xrange(x - 1, n - y + 1):
        rabbit_num = nCk(n - 1, k)
        left_line_num = line_up_one_side(x, k + 1)
        right_line_num = line_up_one_side(y, n - k)
        num = rabbit_num * left_line_num * right_line_num
        nums += num

    return str(nums)