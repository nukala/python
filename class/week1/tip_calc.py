import os, time
print(f"{__file__} modified={time.ctime(os.path.getmtime(__file__))}\n")
print("Welcome to the tip calculator!")
bill = float(input("What was the total bill? $"))
tip = int(input("What percentage tip would you like to give? 10 12 15 "))
people = int(input("How many people to split the bill? "))

total = (bill * (1+tip/100))
each = total / people
print(f"total=[{total}], each={each}")
print(f"Each person should pay: ${round(each, 4):.2f}")

