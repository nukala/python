# @WorthLooking("use __file__ extract modified time")
import os, time
print(f"{__file__} modified={time.ctime(os.path.getmtime(__file__))}\n")

number = int(input("Please enter a number:"))

print(f"{number}: is an ", end = '')
if number % 2 == 0:
  print(f"Even number.")
else:
  print(f"Odd number.")
