if __name__ == '__main__':
    def answer(x):
        differset = set()
        differnum = 0
        for word in x:
            if word not in differset:
                differset.add(word)
                differset.add(word[::-1])
                differnum += 1
        return differnum

    x = ["foo", "bar", "oof", "bar"]
    assert answer(x) == 2

    x = ["x", "y", "xy", "yy", "", "yx"]
    assert answer(x) == 5