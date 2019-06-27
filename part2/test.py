import HC

def f1():
    a = 4
    def f2():
        # b = a
        a = 5
        return a
    b = f2()
    print(a)
    print(b)


def f4():
    a = list()
    a.append(4)
    def f2():
        a.append(5)
        # a = list()
        # a = 5
        return a
    b = f2()
    print(a)
    print(b)

f1()