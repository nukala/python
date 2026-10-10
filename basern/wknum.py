#!uv
# coding: utf-8

from datetime import (date, datetime, timedelta)
from dataclasses import dataclass
from typing import (Annotated, Optional)
import typer
import sys

# /// script
# dependencies = [
#    "typer",
#    "typing",
# ]
# ///

app = typer.Typer(help="Week number calculator",
                  add_completion=False, rich_markup_mode="markdown",
                  context_settings={"help_option_names": ["-h", "--help", "-?"],
                                    "allow_extra_args": True,
                                    "ignore_unknown_options": True, }
                  )



# GROK write me some python code parameterized functions and return types. Small methods 10-20 lines of code:
# to convert string with '-' or '/' or no separator into a datetime.date
# also add as many tests as possible
# Flexible / multi-format strings, Return a default date today, input Strings only
# pls ask questions first
@staticmethod
def parse_date(s: str, default: date = date.today(), verbosity: int = 9,) -> date:
    """
    Convert a string into a datetime.date.

    Supports common formats with '-', '/', or no separator,
    including both 4-digit and 2-digit years:
      YYYY-MM-DD, YY-MM-DD, YYYY/MM/DD, YY/MM/DD, YYYYMMDD, YYMMDD
      DD/MM/YYYY, DD/MM/YY, DD-MM-YYYY, DD-MM-YY, DDMMYYYY, DDMMYY
      MM/DD/YYYY, MM/DD/YY, MM-DD-YYYY, MM-DD-YY, MMDDYYYY, MMDDYY

    On any failure (empty, malformed, impossible date) returns `default`.
    If verbosity > 1, prints a short error message to stdout.
    """
    if not isinstance(s, str) or not s.strip():
        if verbosity > 1:
            print(f"parse_date: empty or non-string input → returning {default}")
        return default

    s = s.strip()

    formats = (
        # 4-digit year – ISO / year-first
        "%Y-%m-%d", "%Y/%m/%d", "%Y%m%d",
        # 4-digit year – day-first (European)
        "%d/%m/%Y", "%d-%m-%Y", "%d%m%Y",
        # 4-digit year – month-first (US)
        "%m/%d/%Y", "%m-%d/%Y", "%m%d%Y",

        # 2-digit year – ISO / year-first
        "%y-%m-%d", "%y/%m/%d", "%y%m%d",
        # 2-digit year – day-first
        "%d/%m/%y", "%d-%m-%y", "%d%m%y",
        # 2-digit year – month-first
        "%m/%d/%y", "%m-%d/%y", "%m%d%y",
    )

    for fmt in formats:
        try:
            dt:date = datetime.strptime(s, fmt).date()
            if verbosity>0:
                print(f"parse_date: s={s}, fmt={fmt}, parsed={dt}")
            return dt
        except ValueError as ve:
            if verbosity>2:
                print(f"parse_date: s=[{s}], failed e={ve}")
            continue

    if verbosity>0:
        typer.secho(f"parse_date: could not parse '{s}' → returning {default}", 
                    fg=typer.colors.RED)
    return default

# TEST: wknum; wknum -w 50 -d 2; wknum -a 1; wknum -s 1; wknum -of 26/09/29
class DtUtils:
  the_date: date = None
  verbose: int = 0
  # day of week number 7=Sunday, 1=Monday
  dow_num: int = 0
  wk_num: int = 0
  year_num: int = 0

  @dataclass
  class DtUtilsConfig:
    to_add: int = None
    to_sub: int = None
    wk_num: int = None
    day_num: int = None
    asof_day: str = None
    verbosity: int = 0

    def dump(self, message:str="") -> str:
      msg_str = f"{message}-" if len(message or "") > 0 else ""
      ret_str: str = f"{msg_str}DUMP: "
      ret_str = ret_str + f"asof_day={self.asof_day}, add={self.to_add}, sub={self.to_sub}, "
      ret_str = ret_str + f"wk={self.wk_num}, day={self.day_num}, verbosity={self.verbosity}, "
      return ret_str

  # --- Main Command ---
  @staticmethod
  @app.command()
  def entry_point(ctx: typer.Context,
            to_add: Annotated[int, typer.Option("-a", "-add", "--add",
                                                   help="Add weeks to current week number, ONLY ONE of add|sub")] = None,
            to_sub: Annotated[int, typer.Option("-s", "-sub", "--sub", "--subtract",
                                                   help="Subtract weeks to current week number, ONLY ONE of add|sub")] = None,
            week_num: Annotated[int, typer.Option("-w", "-week", "--week", 
                                                   help="Details of the specific week number")] = None,
            day_num: Annotated[int, typer.Option("-d", "-day", "--day_num",
                                                   help="Use the specific day, 1=Monday ... 7=Sunday")] = None,
            asof_day: Annotated[str, typer.Option("-of", "--of", "-with", "--with", 
                                                   help="Calculate with specified WIT date (dash or slash separated), instead of today")] = None,

            verbosity: Annotated[int, typer.Option("-v", count=True,
                                                   help="Set verbosity level. Allows -vvv for more verbosity")] = 0,
            vlevel: Annotated[int, typer.Option("--verbosity", "-vrb",
                                                help="Specify a verbosity level, 1=warning, 2=info,3=debug etc.")] = 0,
  ) -> None:
    if vlevel>0:
      verbosity=vlevel

    # prepare config
    cfg: DtUtils.DtUtilsConfig = DtUtils.DtUtilsConfig(verbosity=verbosity)
    if cfg.verbosity>0:
      print(f"entry_point: add={to_add}, sub={to_sub}")

    # check consistency of params
    if to_sub and to_add:
      typer.secho(f"Both add={to_add} and sub={to_sub}, cannot be specified. ONLY ONE", fg=typer.colors.BRIGHT_RED)
      sys.exit(1)
    
    # prepare and setup other configurations
    cfg.to_add=to_add
    cfg.to_sub=to_sub
    cfg.wk_num=week_num
    cfg.day_num=day_num
    cfg.asof_day=asof_day

    # supply config into context, if there are other commands!
    ctx.obj = cfg

    du: DtUtils = DtUtils()
    du.biz_logic(cfg, ctx.args)


  def biz_logic(self, cfg:DtUtils.DtUtilsConfig, args: list[str]) -> None:
    if cfg.verbosity>1:
      print(f"cfg={cfg.dump(f"args={args}")}")

    if cfg.asof_day:
      self.the_date = parse_date(cfg.asof_day, verbosity=cfg.verbosity)
      self.set_isofields()

    if cfg.to_add or cfg.to_sub:
      dlta: int = 0
      if cfg.to_add:
        dlta = cfg.to_add
      elif cfg.to_sub:
        dlta = -cfg.to_sub
      if dlta:
        self.the_date = self.the_date + timedelta(dlta * 7)
      print(f"{self}")
      return

    if cfg.day_num:
      self.dow_num = cfg.day_num
    if cfg.wk_num:
      self.wk_num = cfg.wk_num

    self.the_date = date.fromisocalendar(self.year_num, self.wk_num, self.dow_num)
    if cfg.verbosity>1:
      print(f" the_date={self.the_date}, cfg.d={cfg.day_num}, cfg.w={cfg.wk_num}")
    print(f"{self}")

  def _parse_arg(self, arg: str) -> None:
        numb:int = int(arg)
        if self.verbose>=2:
          print(f" plain-getwk={arg}/{numb}")
        self.the_date = date.fromisocalendar(self.year_num, numb, self.dow_num)

  def __init__(self, argv: list[str]=None):
    self.the_date = date.today()
    self.set_isofields()

  def set_isofields(self):
    self.year_num = self.the_date.isocalendar()[0]
    self.wk_num = self.the_date.isocalendar()[1]
    self.dow_num = self.the_date.isocalendar()[2]

  # def then(self) -> date:
  #   if not self.the_date:
  #     self.the_date = date.today()

  #   return self.the_date

  # def wknum(self):
  #   return self.then().isocalendar()[1]

  def __str__ (self):
    return f"{self.the_date} is weekNumber: {self.the_date.isocalendar()[1]}"


if __name__ == '__main__':
  # du = DtUtils(sys.argv)
  # print(f"{du}")

  app()

  #min=datetime.datetime.then().minute + 5
  #if min > 60:
  #  min = min - 60;
  #print(f"min={min}")
