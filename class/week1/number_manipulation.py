import os, time
print(f"{__file__} -> {time.ctime(os.path.getmtime(__file__))}")
bmi = 84 / 1.65 ** 2
print(f"Raw bmi={bmi}")

# flooring by removing all_and decimal_point
print(f"Floors the number (convert into int) {int(bmi)}")

print(f"Rounded.2 = {round(bmi, 2)}")

# assignment operator += etc
num = 85
print(f"num={num}, ", end="")
num //= 7
print(f"//= 7 is={num}")
