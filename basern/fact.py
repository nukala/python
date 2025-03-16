# To help with unit testing also allow for import

def fact(n):
  if n == 0:
    return 0
  return 1 if n == 1 else n * fact(n-1)


if (__name__ == '__main__'):
  import sys
  print("debug: args=" + str(sys.argv))
  if (len(sys.argv) > 1):
    num = int(sys.argv[1])
    print("fact(" + str(num) + ")=" + str(fact(num)));
  else:
    print("Missing argument ")
