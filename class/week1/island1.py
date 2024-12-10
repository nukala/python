import sys, os, time
print(f"{__file__} modified={time.ctime(os.path.getmtime(__file__))}\n")


print(r'''
*******************************************************************************
          |                   |                  |                     |
 _________|________________.=""_;=.______________|_____________________|_______
|                   |  ,-"_,=""     `"=.|                  |
|___________________|__"=._o`"-._        `"=.______________|___________________
          |                `"=._o`"=._      _`"=._                     |
 _________|_____________________:=._o "=._."_.-="'"=.__________________|_______
|                   |    __.--" , ; `"=._o." ,-"""-._ ".   |
|___________________|_._"  ,. .` ` `` ,  `"-._"-._   ". '__|___________________
          |           |o`"=._` , "` `; .". ,  "-._"-._; ;              |
 _________|___________| ;`-.o`"=._; ." ` '`."\ ` . "-._ /_______________|_______
|                   | |o ;    `"-.o`"=._``  '` " ,__.--o;   |
|___________________|_| ;     (#) `-.o `"=.`_.--"_o.-; ;___|___________________
____/______/______/___|o;._    "      `".o|o_.--"    ;o;____/______/______/____
/______/______/______/_"=._o--._        ; | ;        ; ;/______/______/______/_
____/______/______/______/__"=._o--._   ;o|o;     _._;o;____/______/______/____
/______/______/______/______/____"=._o._; | ;_.--"o.--"_/______/______/______/_
____/______/______/______/______/_____"=.o|o_.--""___/______/______/______/____
/______/______/______/______/______/______/______/______/______/______/_____ /
*******************************************************************************

Welcome to Treasure Island.
Your mission is to find the treasure.
''')

left_or_right = input("You\'re at a decision point. type left or right?\n")
if left_or_right.upper() == "LEFT":
  print('Congratulations ... you reached a beautiful lake with an island in the middle. '
        'On the island there\'s a grand castle. wait for a boat or swim? ')
else:
  print("You fell into a black-hole... Game Over")
  sys.exit(1)

swim = 'swim'
# @WorthLooking("f-strings are applicable for single-quote")
wait_or_swim = input(f'type wait or "{swim}"? \n').lower()
if wait_or_swim == "wait":
  print(f'''{wait_or_swim}: Nice job.
    You reached a grand palace with three colorful doors
    A "red" door, a "green" door and finally a "yellow" door''')
else:
  print("Attacked by Godzilla ... Game Over")
  sys.exit(1)

door_color = input("Which door: red or green or yellow? \n").lower()
if door_color == "red":
  print(f"{door_color}: door throws into a bottomless pit ... Game Over")
  sys.exit(1)
elif door_color == "yellow":
  print(f"{door_color}: took you over a water fall ... Game Over")
  sys.exit(1)
elif door_color == "green":
  # @WorthLooking("f-strings are triple-quotes also.")
  print(f'''{door_color}: you win a Grand Prize 
    ONE dollar $$$$ YAY!
    ''')
else:
  print(f"Facing a lit cannon ... Game Over")
  sys.exit(1)
