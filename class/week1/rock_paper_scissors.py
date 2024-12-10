import sys
import random

rock = '''
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
'''

paper = '''
    _______
---'   ____)____
          ______)
          _______)
         _______)
---.__________)
'''

scissors = '''
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
'''
#constants
choices = [ rock, paper, scissors ]
names = ['rock', 'paper', 'scissors']
print('What do you choose? Type 0 for Rock, 1 for Paper or 2 for Scissors.')

user = int(input())
if user < 0 or user > 2:
    print(f'{user} is not allowed. Choose 0/1/2')
    sys.exit(1)
print("You chose:"+choices[user])
comp = random.randint(0, len(choices) - 1)
print("Computer chose:"+choices[comp])

##########################################
#https://wrpsa.com/the-official-rules-of-rock-paper-scissors/
#   Rock wins against scissors.
#   Scissors win against paper.
#   Paper wins against rock.
##########################################

msg = ""
if user == comp:
    msg = "It\'s a draw!"
elif user == 0 and comp == 2:
    msg = "You win!"
elif comp == 0 and user == 2:
    msg = "You lose"
elif comp > user:
    msg = "You lose"
elif user > comp:
    msg = "You win!"

print(f'user={names[user]}, comp={names[comp]}, {msg}')
