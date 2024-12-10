def turn_right():
    turn_left()
    turn_left()
    turn_left()


## WORTH_LOOKING - check back after day15
# https://www.udemy.com/course/100-days-of-code/learn/lecture/19115662#overview
while front_is_clear():
    move()
turn_left()
### WORTH_LOOKING - why does this work?
    
while not at_goal():
    if right_is_clear():
        turn_right()
        move()
    elif front_is_clear():
        move()
    else:
        turn_left()
################################################################
# WARNING: Do not change this comment.
# Library Code is below.
################################################################
