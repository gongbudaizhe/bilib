def answer(x):
    N = sum(x)
    k = len(x)
    if N >= k:
        if N % k == 0:
            return k
        else:
            return k - 1
    else:
        return N