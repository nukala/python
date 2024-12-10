import random


import foo_bar

# day4 intro to random


def range_rand():
  some_int = random.randint(1, 30)
  print(f"int={some_int}, str={foo_bar.random_string(6)}, detail=[{foo_bar.my_detail()}]")


def rand_flt():
  rnd_flt = random.random()
  print(f'float={rnd_flt*100:.2f}')


def coin_toss():
  rnd = random.random() * 100
  val = 'Tails'
  if rnd >= 50.0:
    val = 'Heads'
  print(f"coin_toss: {rnd:.0f}: {val}")


# @WorthLooking("1arg range implies a start at zero")
for _ in range(4):
  coin_toss()
  range_rand()
  rand_flt()
