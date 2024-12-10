# Banker Roulette and list, day4 task3

import random

friends = ["Alice", "Bob", "Charlie", "David", "Emanuel"]

def who_pays():
    index=random.randint(0, len(friends)-1)
    return friends[index]

def choice_pays():
    return random.choice(friends)

for i in range(20):
    print(f"{i+1}: index={who_pays()}, choice={choice_pays()}")
