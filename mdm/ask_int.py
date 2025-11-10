######################################################
# Generate fake names and email from:
#   python.plainenglish.io/7-python-libraries-that-made-my-friends-think-i-was-a-hacker-7da1a22550a9
######################################################

import pyinputplus as pyip
# input with validation
age = pyip.inputInt("Enter your age: ", min=1, max=100)
print("You entered:", age)