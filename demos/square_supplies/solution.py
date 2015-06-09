def answer(x):
    x_sqrt = x**0.5
    if x_sqrt == int(x_sqrt):
        return 1
    else:
        x_sqrt_int = int(x_sqrt)
        current_best = 1000000
        for i in xrange(x_sqrt_int, 0, -1):
            res = x - x_sqrt_int**2
            res_ans = answer(res)
            combine_ans = 1 + res_ans
            if combine_ans == 2:
                return 2
            else:
                if combine_ans < current_best:
                    current_best = combine_ans
        return current_best