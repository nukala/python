# @WorthLooking("3rd arg is step"), does not include 2nd
for n in range(1,20,4):
    print(n)

total = 0
for n in range(1,101):
    total += n
print(f"Total = {total}")

print(f"sum-with-range = {sum(range(1,101))}")


#12
for i in range(1,101):
    msg=''
    if i % 15 == 0:
      msg='FizzBuzz'
    elif i % 3 == 0:
      msg='Fizz'
    elif i % 5 == 0:
      msg='Buzz'
    else:
      msg=str(i)
    print(msg)
#print("FizzBuzz done.")