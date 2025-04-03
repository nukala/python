import os
import sys
from argparse import ArgumentParser

#############################################
# To calculate the total tax based on values seen in tables that show pct + min
#
# Missing 401k contributions
#
#############################################


class FtbIrsUtils:
  @staticmethod
  def find_row(inc, ary, parsed):
    for i in ary:
      min_amt = i[0]
      max_amt = i[1]

      if min_amt <= inc <= max_amt:
        if parsed.verbose > 1:
          print(f"   For ${inc} match={i}")
        return i

    return None

  @staticmethod
  def calc_payment(inc, deduct, ary, parsed):
    orig_inc = inc
    if parsed.verbose > 2:
      print(f"   inc={inc} will be reduced by {deduct}")
    inc -= deduct
    inc = max(inc, 0)

    r = FtbIrsUtils.find_row(inc, ary, parsed)

    if r is None:
      if parsed.verbose > 1:
        print(f"   nothing found for inc={inc}")
      return -1

    over = (inc - r[0])
    threshold = r[2]
    fraction = r[3]/100.0
    payment = (fraction*over) + threshold
    if parsed.verbose > 2:
      print(f"   inc={inc}, over={over}, threshold={threshold}, fraction={fraction:.4f}"
            f", payment={payment:.2f}, orig_inc={orig_inc}\n")
    return payment


# _nw due to nerdwallet
class FtbIrsNW:
  year = 2024
  irs_std = 29_200
  exempt_irs = 0
  ftb_std = 11_080
  exempt_ftb = 288

  # https://www.nerdwallet.com/article/taxes/california-state-tax
  ftb = [
    [0, 21512, 0, 1],
    [21513, 50998, 215.12, 2],
    [50999, 80490, 804.84, 4],
    [80491, 111732, 1985.52, 6],
    [111733, 141212, 3859.04, 8],
    [141213, 721318, 6217.44, 9.3]
  ]

  # https://www.nerdwallet.com/article/taxes/federal-income-tax-brackets#2024-tax-brackets-(taxes-due-april-2025)
  irs = [
    [0, 23200, 0, 10],
    [23201, 94300, 2320, 12],
    [94301, 201050, 10852, 22],
    [201051, 383900, 34337, 24],
    [383901, 487450, 78221, 32],
    [487451, 731200, 111357, 35]
  ]

  def calc_irs(self, inc, parsed):
    return FtbIrsUtils.calc_payment(inc - self.exempt_irs, self.irs_std, self.irs, parsed)

  def calc_ftb(self, inc, parsed):
    return FtbIrsUtils.calc_payment(inc - self.exempt_ftb, self.ftb_std, self.ftb, parsed)


class FtbIrs2025(FtbIrsNW):
  def __init__(self):
    super(FtbIrs2025, self)
    self.year = 2025
    self.irs_std = 29_200
    self.ftb_std = 10_726
    self.exempt_ftb = 298

    # https://www.nerdwallet.com/article/taxes/federal-income-tax-brackets
    self.irs = [
      [0, 23_850, 10, 0],
      [23_851, 96_950, 2385, 12],
      [96_951, 206_700, 11_157, 22],
      [206_701, 394_600, 35_302, 24],
      [394_601, 501_050, 80_398, 32],
      [501_051, 751_600, 114_462, 35],
      [751_601, 99_999_999, 202_154.50, 37]
    ]

    # https://blog.turbotax.intuit.com/income-tax-by-state/california-105369 && inp && brak_ary
    self.ftb =  [
    [0, 21_512, 0.00, 1.0],
    [21_513, 50_998, 215.12, 2.0],
    [50_999, 80_490, 804.82, 4.0],
    [80_491, 111_732, 1_984.46, 6.0],
    [111_733, 141_212, 3_858.92, 8.0],
    [141_213, 721_318, 6_217.24, 9.3],
    [721_319, 865_574, 60_167.01, 10.3],
    [865_575, 1_442_628, 75_025.27, 11.3],
 ]


class FtbIrs2023(FtbIrsNW):
  def __init__(self):
    super(FtbIrs2023, self)
    self.year = 2023
    self.irs_std = 27_700
    self.ftb_std = 10_726
    self.exempt_ftb = 298

    # https://www.irs.gov/media/166986 Schedule Y-1
    self.irs = [
      [0, 21_999, 0, 10],
      [22_000,	89_450,	2_200.00, 12],
      [89_450, 190_750, 10_294.00, 22],
      [190_750, 364_200, 32_580.00, 24],
      [364_200, 462_500, 74_208.00, 32],
      [462_500, 693_750, 105_664.00, 35],
      [693_750, 99_000_000, 186_601.50, 37]
    ]

    # https://www.ftb.ca.gov/forms/2023/2023-540-tax-rate-schedules.pdf Schedule Y
    self.ftb = [
      [0, 20_824, 0, 1],
      [20_824, 49_368, 208.24, 2],
      [49_368, 77_918, 779.12, 4],
      [77_918, 108_162, 1_921.12, 6],
      [108_162, 136_700, 3_735.76, 8],
      [136_700, 698_274, 6_018.80, 9.3],
      [698_274, 837_922,  58_245.18, 10.3],
      [837_922, 1_396_542, 72_628.92, 11.3],
      [1_396_542, 99_000_000,  135_752.98, 12.3]
    ]


class FrsApp:

  def __init__(self):
    self.frs = FtbIrs2025()
    self.parsed = None
    self.unknown_args = None

  def parse_args(self, args):
    parser = ArgumentParser(prog="frs",
                            description="To calculate taxes upon AGI (assumes standard-deduction, MFJ, lives in CA)")
    parser.add_argument('-v', '--verbose', action='count', default=0, dest="verbose",
                        help="Enable verbosity (more logging with -vv etc.)")
    parser.add_argument('-23', '--2023', '--use_23', '--use_2023', action='store_true', default=False
                        , dest="use_23", help=f"Use 2023 values")
    parser.add_argument('-24', '--2024', '--use_24', '--use_2024', action='store_true', default=False
                        , dest="use_24", help=f"Use 2024 values")
    self.parsed, self.unknown_args = parser.parse_known_args(args)

  def main(self, args):
    self.parse_args(args)
    if len(self.unknown_args) > 1:
      ua = self.unknown_args[1].replace('K', 'k').replace('k', '')
      inc = int(ua)
      if inc < 1000:
        was = inc
        inc *= 1000
        if self.parsed.verbose > 0:
          print(f"  Converted {was} into income of ${inc:.2f}")
    else:
      inc = int(input("Enter income: "))

    if self.parsed.use_23:
      self.frs = FtbIrs2023()
    elif self.parsed.use_24:
      self.frs = FtbIrsNW()
    if self.parsed.verbose > 2:
      print(f"  using {self.frs.year} values std={self.frs.irs_std}/{self.frs.ftb_std}")

    if self.parsed.verbose > 3:
      print(f"  parsed={str(self.parsed)}\n")

    fed = self.frs.calc_irs(inc, self.parsed)

    if fed < 0:
      print(f"Income of ${inc:.2f} is outside the scope of this tool (fed)")
      return 1

    ca = self.frs.calc_ftb(inc, self.parsed)
    if ca < 0:
      print(f"Income of ${inc:.2f} is outside the scope of this tool (CA)")
      return 2

    fed_pct = (fed*100.0)/inc
    ca_pct = (ca*100.0)/inc
    rem_pct = 100.0 - fed_pct - ca_pct
    rem_amt = inc - fed - ca
    print(f"Your {self.frs.year} payment = ${fed+ca:,.2f} ({fed:,.2f} + {ca:,.2f}) ${rem_amt:,.2f}")
    print(f"                        {(fed_pct + ca_pct):.2f}% ({fed_pct:.2f}% + {ca_pct:.2f}%) {rem_pct:.2f}%")
    return 0

@staticmethod
def activate_venv():
  # try venv, env, myenv
  envdir=os.path.join(os.path.dirname(__file__), "venv")
  print(f"venv={envdir}.exists={os.path.isdir(envdir)}")
  print("")
  pass

if __name__ == "__main__":
  activate_venv()
  app = FrsApp()

  sys.exit(app.main(sys.argv))
