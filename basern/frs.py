import sys
from argparse import ArgumentParser

#############################################
# To calculate the total tax based on values seen in tables that show pct + min
#
# https://www.nerdwallet.com/article/taxes/california-state-tax
# https://www.nerdwallet.com/article/taxes/federal-income-tax-brackets#2024-tax-brackets-(taxes-due-april-2025)
#
# Missing 401k contributions
#
#############################################


class FtbIrs:
  ftb = [
    [4, 50999, 80490, 804.84],
    [6, 80491, 111732, 1985.52],
    [8, 111733, 141212, 3859.04],
    [9.3, 141213, 721318, 6217.44]
  ]
  ftb_std = 11_080

  irs = [
    [12, 23201, 94300, 2320],
    [22, 94301, 201050, 10852],
    [24, 201051, 383900, 34337],
    [32, 383901, 487450, 78221],
    [35, 487451, 731200, 111357]
  ]
  irs_std = 29_200

  def __init__(self):
    self.parsed = None
    self.unknown_args = None
    self.verbose = False
    self.use_std = False

  def find_row(self, inc, ary):
    for i in ary:
      min_amt = i[1]
      max_amt = i[2]

      if min_amt <= inc <= max_amt:
        if self.parsed.verbose:
          print(f"  For ${inc} match={i}")
        return i

    return None

  def calc_payment(self, inc, deduct, ary):
    r = self.find_row(inc, ary)

    if r != None:
      pass
    else:
      return -1

    over = (inc - r[1])
    if self.use_std:
      over -= deduct

    threshold = r[3]
    fraction = r[0]/100.0
    payment = (fraction*over) + threshold
    if self.parsed.verbose:
      print(f"  inc={inc}, threshold={threshold}, fraction={fraction:.2f}, over={over}, payment={payment:.2f}")
    return payment

  def parse_args(self, args):
    parser = ArgumentParser(prog="frs",
                            description="To calculate taxes upon AGI (assumes standard-deduction, MFJ, lives in CA)")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest="verbose",
                        help="Enable verbosity")
    parser.add_argument('-std', '--std', '--standard', action='store_true', default=False, dest="use_std",
                        help=f"Use standard deductions. fed={self.irs_std}, CA={self.ftb_std}")
    self.parsed, self.unknown_args = parser.parse_known_args(args)

  def main(self, args):
    self.parse_args(args)
    if len(self.unknown_args) > 1:
      inc = int(self.unknown_args[1])
      if inc < 1000:
        #was = inc
        inc *= 1000
        #print(f"Converted {was} into income of ${inc:.2f}")
    else:
      inc = int(input("Enter income: "))

    fed = self.calc_payment(inc, self.irs_std, self.irs)
    if fed < 0:
      print(f"Income of ${inc:.2f} is outside the scope of this tool (fed)")
      return 1

    ca = self.calc_payment(inc, self.ftb_std, self.ftb)
    if ca < 0:
      print(f"Income of ${inc:.2f} is outside the scope of this tool (CA)")
      return 2

    fed_pct = (fed*100.0)/inc
    ca_pct = (ca*100.0)/inc
    print(f"Your total payment = ${fed+ca:.2f} ({fed:.2f} + {ca:.2f}) ")
    print(f"                        {(fed_pct + ca_pct):.2f}% ({fed_pct:.2f}% + {ca_pct:.2f}%)")
    return 0


if __name__ == "__main__":
  frs = FtbIrs()

  sys.exit(frs.main(sys.argv))
