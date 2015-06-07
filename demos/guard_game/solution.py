if __name__ == '__main__':
    def answer(x):
        if x < 10:
            return x
        else:
            digits = []
            while True:
                digits.append(x % 10)
                x /= 10
                if not x:
                    break
            return answer(sum(digits))

    print answer(13)
    print answer(1235)