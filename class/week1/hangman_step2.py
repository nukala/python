import random
from idlelib.debugobj import dispatch


def do_replace(word, guess2=None):
    ret = ''
    for ch in word:
        if ch != guess2:
            ret += '_'
        else:
            ret += guess2
    return ret

word_list = ["aardvark", "baboon", "camel"]

chosen_word = random.choice(word_list)
print(chosen_word)

# TODO-1: Create a "placeholder" with the same number of blanks as the chosen_word
placeholder = do_replace(chosen_word)
print(placeholder)

guess = input("Guess a letter: ")[0].lower()
print(f"  guess={guess}")

display = ""
for letter in chosen_word:
    if letter == guess:
        display += guess
    else:
        display += "-"
print(display)

