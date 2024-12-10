# day5 last exercise - password generator

import random

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
#symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']
symbols = ['!', '#', '$', '%', '&', '+']

print("Welcome to the PyPassword Generator!")
nr_letters = int(input("How many letters would you like in your password?\n"))
nr_symbols = int(input(f"How many symbols would you like?\n"))
nr_numbers = int(input(f"How many numbers would you like?\n"))


# hard level 1443, end=1504, hint2=use shuffle. Actually sample in py3.12+
__debug=False
ans=''
for i in range(0, nr_letters):
    ans += random.choice(letters)
if __debug:
    print(f"letters={ans}")
for i in range(0, nr_symbols):
    ans += random.choice(symbols)
if __debug:
    print(f"after letters,symbols={ans}")
for i in range(0, nr_numbers):
    ans += random.choice(numbers)
if __debug:
    print(f"after letters,symbols,numbers={ans}")

#@WorthLooking("shuffle is in place, sample returns a new list")
ans_list = list(ans)
res=''.join(random.sample(ans_list, len(ans)))
random.shuffle(ans_list)
res_list = ''.join(ans_list)
if __debug:
    print(f"ans={ans}, sampled={res}, ans_list{ans_list}, res_list={res_list}")

if random.randint(0,100) > 50:
    print(f"Your shuffled password is: {res_list}")
else:
    print(f"You sampled password is: {res}")
