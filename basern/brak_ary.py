import sys

########################################################################
# Takes the initial percentage and threshols to build brackets array 
#  used in frs.py
#
# not all websites list everything that fits the brackets array easily. This
#  is to convert to that format
# 
# ravi> cat inp | python3 basern/brak_ary.py
# ravi> cat inp
# ===
# 1
# 21512
# y
# 2
# 50998
# y
# 4
# 80490
# y
# 6
# 111732
# y
# 8
# 141212
# y
# 9.3
# 721318
# y
# 10.3
# 865574
# n
# ===
########################################################################


class BracketArray:
  prev_threshold = 0
  rate = 0
  start = 0
  end = 0
  lines = []

  def __init__(self, start, end, rate):
    self.rate = rate
    self.start = start
    self.end = end
    # self.tax_amount = self.tax_amount + (end-start)*(rate/100.0)

  # how static factory methods work
  # Setup next bracket its threshold based on `other`
  @classmethod 
  def next_bracket(cls, other):
    nxt = BracketArray(other.end + 1, -1, -1)
    nxt.prev_threshold = other.prev_threshold + (other.end-other.start)*(other.rate/100.0)
    # print(f"other=[{other.start}, {other.end}, {other.prev_threshold}]")
    return nxt

  # perform relevant checks and prepare a line for the `this` bracket
  def append(self):
    if self.end <= 0:
      print(f"bad end {self.end}")
      sys.exit(1)
    elif self.rate <= 0.0:
      print(f"bracket populated incorrectly with rate={self.rate:4.2f}%, exiting")
      sys.exit(2)

    line = f"[{self.start:_}, {self.end:_}, {self.prev_threshold:_.2f}, {self.rate}],"
    self.lines.append(line)
    return line

  # shows all the appended lines!
  def show_lines(self): 
    ret = f" [\n"
    for lne in self.lines:
      ret += f"    {lne}\n"
    ret += " ]\n"
  
    return ret
  
  @staticmethod
  def do_work():
    last = None

    if not last:
      rate = float(input("First tax rate: "))
      end = int(input("First limit: "))
      # else last line will NPE
      brak = BracketArray(0, end, rate)
      print(f" Output array = {brak.append()}")
      last = brak

    while input("more brackets? ").lower().startswith('y'):
      rate = float(input(" next Tax rate: "))
      end = int(input(f" end of {rate:4.1f}% bracket: "))

      brak = BracketArray.next_bracket(last)
      brak.rate = rate
      brak.end = end 
      print(f" Output array = {brak.append()}")
         
      last = brak
    print("")
    print(f"{brak.show_lines()}")


if __name__ == "__main__":
  app = BracketArray(0,0,0)

  sys.exit(app.do_work())
