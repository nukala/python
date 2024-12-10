import os, time
print(f"{__file__} modified={time.ctime(os.path.getmtime(__file__))}\n")

print("Welcome to the rollercoaster!")
height = int(float(input("What is your height in cm? ")))

if height >= 120:
  print("You can ride the rollercoaster")
else:
  print(f"Sorry you({height}) have to grow taller before you can ride.")
