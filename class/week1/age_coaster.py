print("Welcome to the rollercoaster!")
height = int(input("What is your height in cm? "))

if height >= 120:
    print("You can ride the rollercoaster")
    age = int(input("What is your age? "))
    if age > 18:
      print(f"age={age}, Adults pay $12.00")
    elif age <= 12:
      print(f"Children({age}) pay $5.00")
    else:
      print(f"age({age}), you pay $7.00")
else:
    print("Sorry you have to grow taller before you can ride.")
