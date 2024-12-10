import os, time
print(f"{__file__} modified={time.ctime(os.path.getmtime(__file__))}\n")

print("Welcome to Python Pizza Deliveries!")

cost = 0
msg = ""
size = input("What size pizza do you want? S, M or L: ").upper()
if size == 'L':
    msg += "large "
    cost += 25
elif size == 'M':
    msg += "medium "
    cost += 20
elif size == 'S':
    msg += "small "
    cost += 15
else:
    raise Exception(f"Unknown size({size}) chosen")

pepperoni = input("Do you want pepperoni on your pizza? Y or N: ").lower()
if pepperoni[0] == 'y':
    if size[0].upper() == "M" or size[0].upper() == 'L':
        msg += "lm-ppr "
        cost += 3
    elif size[0].upper() == "S":
        msg += "sm-ppr "
        cost += 2
extra_cheese = input("Do you want extra cheese? Y or N: ")
if extra_cheese[0].upper() == "Y":
    msg += "cheese "
    cost += 1

# print(f"Pizza ({msg}): ")
print(f"Your final bill is: ${cost}.")

