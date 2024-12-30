import os, time

###
# Parantheses, exponent, multiply, divide, add, subtract, left to right
###
print(f"{__file__} modified={time.ctime(os.path.getmtime(__file__))}\n")

print("My age: " + str(12))
print(123 + 456)
print(7-3)
print(3*2)

print(6 / 3)
print(type(6 / 3))
## double slash is an integer division
print(6 // 2 )
# removes all the decimals.
print(type(6 // 5))
# string does not represent an int
#print(int("5.66667"))
# exponent ... power of
print(2 ** 3)

# PEMDASLR -- division turns into float
print(3 * 3 + 3 / 3 - 3)
