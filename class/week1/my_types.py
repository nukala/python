# Python does not seem to have a declaration. Can't say int x = 1234
print(len(str(12345)))

# types supported!
sep = ","
print(f"int={type(123)}{sep} str={type("foo")}{sep} float={type(123_456.55)}{sep} bool={type(True)}")
# print("float=" + str(type(123_45.67)) + " Boolean=" + str(type(True)))
# print("int=" + str(type(123)) + " str=" + str(type("hello")))
# print("float=" + str(type(123_45.67)) + " Boolean=" + str(type(True)))