# This problem can be really computational expensive if we simply traverse all
# the possible orderings (50! = 3.0414093e+64)
# Instead, we observe that if two adjacent minions(m[i], m[i+1]) in the ordering
# with property(t[i], t[i+1], t is the time the minion takes to complete the
# task) and (p[i], p[i+1], p is probability that the minion will tell the true
# answer) have the inequality t[i]/p[i] < t[i+1]/p[i+1], then we should swap the
# two minions to minimize the expected time cost. if t[i]/p[i] = t[i+1]/p[i+1],
# then the order doesn't matter, this is where lexicographical order should
# be used.

def compare(m1, m2):
    r1 = m1[0] * m1[2] / float(m1[1])
    r2 = m2[0] * m2[2] / float(m2[1])
    if r1 == r2:
        # lexicographical order
        return m1[3] - m2[3]
    else:
        if r1 > r2:
            return 1
        else:
            return -1

def answer(minions):
    # add index
    minions_aug = [val + [idx] for idx, val in enumerate(minions)]
    return [m[3] for m in sorted(minions_aug, cmp=compare)]
