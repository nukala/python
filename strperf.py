#!/usr/bin/env python3 

# from: https://stackoverflow.com/questions/43123408/f-strings-vs-str-format

# t = timeit.Timer('f1()', 'from strperf import f1')
#>>> t.timeit()
# t.repeat()
# https://docs.python.org/3/library/timeit.html#timeit-examples

########################
# ravi (master) python 08:53:28> p3 -m timeit -r11  -s 'import strperf' 'strperf.f2()'
# 1000000 loops, best of 11: 217 nsec per loop
# ravi (master) python 08:53:44> p3 -m timeit -r11  -s 'import strperf' 'strperf.f1()'
# 5000000 loops, best of 11: 74 nsec per loop
# ravi (master) python 08:53:55> p3 -m timeit -r11  -s 'import strperf' 'strperf.f3()'
# 5000000 loops, best of 11: 87 nsec per loop
########################


import dis
# TODO - figure out how to use this as a method import timeit

#def __init__(self):
#    pass

def f1():
    a = "test"
    return f"{a}"

def f2():
    return "{a}".format(a='test')

def f3():
    return "%s" % 'test'
    
if __name__ == "__main__":
    #timeit.timeit('f1()', 'from __main__ import f1', number = 1000*1000)

    print(dis.dis(f1))
    print(f"=====")
    print(dis.dis(f2))
    print(f"=====")
    print(dis.dis(f3))

