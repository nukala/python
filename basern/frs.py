#!/usr/bin/env python3
# coding: utf-8

from argparse import ArgumentParser
import sys
from typing import List


###############################################################################
# To calculate the total tax based on values seen in tables that show pct + min
# 
# Values are accurate as seen on NerdWallet for federal - 25oct26
#
# develop a Brak class instead of an array
# fix -v9 for verbosity=9
#     401k, HRA etc.
#     
#
# see also https://taxfoundation.org/data/all/federal/tax-calculator-obbba/
###############################################################################

INFINITY = 999_999_999
TBC = -456_789

class FtbIrsUtils:
  @staticmethod
  def find_row(inc, ary, verbose:int = 0, desc:str = 'IRS'):
    for i in ary:
      min_amt = i[0]
      max_amt = i[1]

      if min_amt <= inc <= max_amt:
        if verbose > 0:
          print(f"   {desc}=${inc}, bracket={i}")
        return i

    return None

  @staticmethod
  def calc_payment(inc, deduct, ary, verbose: int = 0, show_next: bool = False, desc:str = 'IRS'):
    orig_inc = inc
    if verbose > 2:
      print(f"   inc={inc} will be reduced by {deduct}")
    inc -= deduct
    inc = max(inc, 0)

    r = FtbIrsUtils.find_row(inc, ary, verbose, desc)

    if r is None:
      print(f"  ERR> nothing found for inc={inc}")
      return -1

    over = (inc - r[0])
    threshold = r[4]
    fraction = r[3]/100.0
    payment = (fraction*over) + threshold
    calc_str = ''
    if verbose > 1 or show_next:
      calc_str = f"   {desc}={inc}, orig={orig_inc}, over={over}, threshold={threshold}, fraction={fraction:.4f}"
      calc_str += f", payment={payment:.2f}"
 
      next_min = r[1] + 1
      next_row = FtbIrsUtils.find_row(next_min, ary, 0, desc)
      if verbose > 3:
        print(f"   next_min={next_min}, next_row={next_row}")
      calc_str += f"  next={next_row[3]:.2f}%"

      print(f"{calc_str}\n")
    
    return payment

  @staticmethod
  def process_ary(ary, verbose):
    s_ary = sorted(ary, key=lambda x: x[0])
    total = 0.0
    for i in range(len(s_ary)):
      s = s_ary[i]
      s.append(total)
      # amount to charge at this percentage!
      to_charge = s[1] - s[0]
      curr = round(to_charge * (s[3]/100.0), 2)
      if verbose > 5:
        print(f"  s={s}, curr={curr}, old_total={total}")
      total = round(total + curr, 2)

    if verbose > 5:
      import pprint
      pretty_str = pprint.pformat(s_ary, indent=2, underscore_numbers=True)
      print(f"processed = {pretty_str}")

    for s in s_ary:
      typed_threshold = s[2]
      calc_threshold = s[4]
      if typed_threshold != TBC and typed_threshold != calc_threshold:
        print(f"  ERR> ({s[0]}/{s[1]}): typed={typed_threshold}, calc={calc_threshold}")
        return None
    return s_ary

# _nw due to nerdwallet
class FtbIrsNW:
  year = 2024
  irs_std = 29_200
  exempt_irs = 0
  ftb_std = 11_080
  exempt_ftb = 288

  # https://www.nerdwallet.com/article/taxes/california-state-tax
  ftb = [
    [0, 21_512, 0, 1],
    [21_512, 50_998, 215.12, 2],
    [50_998, 80_490, 804.84, 4],
    [80_490, 111_732, 1_984.52, 6],
    [111_732, 141_212, 3_859.04, 8],
    [141_212, 721_318, 6_217.44, 9.3],
    [721_318, 865_574, 60_167.30, 10.3],   # tables say .31
    [865_574, 1_442_628, 75_025.67, 11.3],
    [1442628, INFINITY, 140232.77, 12.3]
  ]

  # https://www.nerdwallet.com/article/taxes/federal-income-tax-brackets#2024-tax-brackets-(taxes-due-april-2025)
  irs = [
    [0, 23_200, 0, 10],
    [23_200, 94_300, 2_320, 12],
    [94_300, 201_050, 10_852, 22],
    [201_050, 383_900, 34_337, 24],
    [383_900, 487_450, 78_221, 32],
    [487_450, 731_200, 111_357, 35],
    [731_200, INFINITY, TBC, 37]
  ]

  def calc_irs(self, inc, parsed):
    return FtbIrsUtils.calc_payment(inc - self.exempt_irs, self.irs_std, self.irs, parsed.verbose, parsed.show_next, 'IRS')

  def calc_ftb(self, inc, parsed):
    return FtbIrsUtils.calc_payment(inc - self.exempt_ftb, self.ftb_std, self.ftb, parsed.verbose, parsed.show_next, 'ftb')

class FtbIrs2023(FtbIrsNW):
  def __init__(self):
    super(FtbIrs2023, self)
    self.year = 2023
    self.irs_std = 27_700
    self.ftb_std = 10_726
    self.exempt_ftb = 298

    # https://www.irs.gov/media/166986 Schedule Y-1
    self.irs = [
      [0, 22_000, 0, 10],
      [22_000,	89_450,	2_200.00, 12],
      [89_450, 190_750, 10_294.00, 22],
      [190_750, 364_200, 32_580.00, 24],
      [364_200, 462_500, 74_208.00, 32],
      [462_500, 693_750, 105_664.00, 35],
      [693_750, INFINITY, 186_601.50, 37]
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
      [1_396_542, INFINITY,  135_752.98, 12.3]
    ]

class FtbIrs2025(FtbIrsNW):
  def __init__(self):
    super(FtbIrs2025, self)
    self.year = 2025
    self.irs_std = 31_500 # Ob3a
    self.ftb_std = 10_726
    self.exempt_ftb = 298

    # https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill#:~:text=24%25%20for%20incomes%20over%20%24105%2C700,for%20married%20couples%20filing%20jointly
    self.irs = [
      [0, 23_850, 0, 10],
      [23_850, 96_950, 2385, 12],
      [96_950, 206_700, 11_157, 22],
      [206_700, 394_600, 35_302, 24],
      [394_600, 501_050, 80_398, 32],
      [501_050, 751_600, 114_462, 35],
      [751_600, INFINITY, 202_154.50, 37]
    ]

    # https://www.ftb.ca.gov/about-ftb/newsroom/tax-news/index.html
    self.ftb =  [
      [0, 22_158, 0.00, 1.0],
      [22_158, 52_528, 221.58, 2.0],
      [52_528, 82_904, 828.98, 4],
      [82_904, 115_084, 2_044.02, 6],
      [115_084,	145_448, 3_974.82, 8],
      [145_448, 742_958, 6_403.94, 9.3],
      [742_958, 891_542, 61_972.37, 10.3],
      [891_542, 1_485_906, 77_276.52, 11.3],
      [1_485_906, INFINITY, 144_439.65, 12.3]
    ]

#### once fully populated, use root parent class
class FtbIrs2026(FtbIrs2025):

  def __init__(self):
    super(FtbIrs2026, self)
    super().__init__()
    self.year = 2026
    self.irs_std = 32_200

    # https://www.msn.com/en-us/money/taxes/the-new-irs-tax-brackets-for-2026-are-here-see-where-you-fit-in/ar-AA1Oa7ms
    self.irs = [
        [0, 24_800, 0, 10],
        [24_800, 100_800, 2_480, 12],
        [100_800, 211_400, 11_600, 22],
        [211_400, 403_550, 35_932, 24],
        [403_550, 512_450, 82_048, 32],
        [512_450, 768_700, 116_896, 35],
        [768_700, INFINITY, 206_583.50, 37]
    ]


class FrsApp:

  def __init__(self):
    self.frs = None
    self.parsed = None
    self.unknown_args = None

  def parse_args(self, args):
    parser = ArgumentParser(prog="frs",
                            description="To calculate taxes upon AGI (assumes standard-deduction, MFJ, lives in CA,"
                            " no 401k, no HRA, no FSA)")
    parser.add_argument('-v', '--verbose', action='count', default=0, dest="verbose",
                        help="Enable verbosity (more logging with -vv etc.)")
    parser.add_argument('-q', type=int, default=0, dest="verbose",
                        help="Enable verbosity (more logging with -vv etc.)")                        
    parser.add_argument('-23', '--2023', '--use_23', '--use_2023', action='store_true', default=False
                        , dest="use_23", help=f"Use 2023 values")
    parser.add_argument('-24', '--2024', '--use_24', '--use_2024', action='store_true', default=False
                        , dest="use_24", help=f"Use 2024 values")
    parser.add_argument('-25', '--2025', '--use_25', '--use_2025', action='store_true', default=False
                        , dest="use_25", help=f"Use 2025 values")
    parser.add_argument('-26', '--2026', '--use_26', '--use_2026', action='store_true', default=False
                        , dest="use_26", help=f"Use 2026 values")
    parser.add_argument('-sn', '--show_next', action='store_true', default=False
                        , dest="show_next", help=f"show next bracket pct, requires -vv or more")                        
    self.parsed, self.unknown_args = parser.parse_known_args(args)

  @staticmethod
  def parse_income_from_args(unknown_args: List[str], verbose: bool = False) -> int:
    """Converts 5 into 5000; 5k into 5000; .5 to 500 etc."""
    has_k = False
    try:
      has_k = unknown_args[1].capitalize().index("K") >= 0
    except ValueError:
      pass

    ua = unknown_args[1].replace('K', 'k').replace('k', '')
    if has_k:
      inc = float(ua)*1000
    else:
      inc = float(ua)
    if inc < 1000.0:
      inc *= 1000
      if verbose > 0:
        print(f"  Converted {unknown_args[1]} into income of ${inc:.2f}")

    return int(inc)

  def main(self, args):
    self.parse_args(args)
    if len(self.unknown_args) > 1:
      inc = FrsApp.parse_income_from_args(self.unknown_args, self.parsed.verbose)
    else:
      inc = int(float(input("Enter income: ")))

    if self.parsed.use_26:
      self.frs = FtbIrs2026()
      if self.parsed.verbose >= 8:
        print(f"  inited 26, yr={self.frs.year}")
    elif self.parsed.use_23:
      self.frs = FtbIrs2023()
    elif self.parsed.use_24:
      self.frs = FtbIrsNW()
      if self.parsed.verbose >= 8:
        print(f"  inited NW")
    else:
      self.frs = FtbIrs2025()
      if self.parsed.verbose >= 8:
        print(f"  inited 25")

    self.frs.irs = FtbIrsUtils.process_ary(self.frs.irs, self.parsed.verbose)
    self.frs.ftb = FtbIrsUtils.process_ary(self.frs.ftb, self.parsed.verbose)
    if self.parsed.verbose > 3:
      print(f"  parsed={str(self.parsed)}")
      print(f"  frs={str(self.frs)}, yr={self.frs.year}, std={self.frs.irs_std:,}/{self.frs.ftb_std:,}")

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


if __name__ == "__main__":
  app = FrsApp()

  sys.exit(app.main(sys.argv))
