# coding: utf-8

import typer
import sys

from enum import Enum
from typing import Annotated
from basern.stack import StackDump, get_func_name_with_sys

# /// script
# dependencies = [
#    "typer",
# ]
# ///

app = typer.Typer(
    help="Ask for an answer. interrupt on a read kills the invoking shell",
    add_completion=False,
    rich_markup_mode="markdown",
    context_settings={
        "allow_extra_args": True,
        "help_option_names": ["-h", "--help", "-?"],
        "ignore_unknown_options": True,
    },
)


class YesNo:
  class YN_Values(int, Enum):
    YES = 0
    NO = 1


  def yes_no(self, to_ask:str = None, default_value:int = 1, verbosity:int = 0):
    pmpt = "Yes_or_No ?" if to_ask is None else to_ask
    fn:str = f"{get_func_name_with_sys(StackDump.CURRENT_METHOD)} -" if verbosity>0 else ""

    try:
      v = input(pmpt).upper()
      if verbosity>1:
        print(f" {fn}answer=[{v}].{len(v)}", flush=True)

      if len(v) <= 0:
        return default_value
      if v[0] == 'Y':
        return 0
      else:
        return 1
    except KeyboardInterrupt as e:
      print(f"{e}")
      raise typer.Abort()
      # return default_value


  @staticmethod
  def bool_yesno(to_ask: str):
    ret = YesNo().yes_no(to_ask)
    if ret == 0:
      return True

    return False

  @staticmethod
  @app.command()
  def entry_point(ctx: typer.Context,
            message_str: Annotated[str, typer.Option("--message", "-m", "-q", "--question", show_default=False,
                help="Question to ask",
            )]=None,
            default_yn: Annotated[YN_Values, typer.Option("-d", "-default", "--default", 
                                                          help="YES OR NO default answer")] = YN_Values.NO,

            verbosity: Annotated[int, typer.Option("-v", count=True, show_default=True,
                                                   help="Set verbosity level. Allows -vvv for more verbosity")] = 0,
            vlevel: Annotated[int, typer.Option("--verbosity", "-vrb", show_default=False,
                                                help="Specify a verbosity level, 1=warning, 2=info,3=debug etc.")] = 0,
  ) -> None:
    if vlevel>0:
      verbosity=vlevel

    fn:str = f"{get_func_name_with_sys(StackDump.CURRENT_METHOD)} -" if verbosity>0 else ""

    if verbosity>1:
      print(f"{fn} msg=[{message_str}].{len(message_str or "")}, dflt={default_yn} ")
    if not message_str and len(ctx.args or []) > 0:
      message_str = ctx.args[0]

    if len(message_str or "") == 0:
      if verbosity>0:
        print(f"{fn} message=[{message_str}], using defalt_message")
      message_str = f"yes/no [{default_yn.name[0].lower()}]? "

    ## business logic
    yn:YesNo = YesNo()
    sys.exit(yn.yes_no(message_str, default_value=default_yn, verbosity=verbosity))


############################################################
# Ask for an answer. Again, like in entorint.py, interrupt on a 
#  read kills the invoking shell
############################################################

if __name__ == "__main__" :
  # prompt = None
  # if len(sys.argv) > 1:
  #   prompt = sys.argv[1]

  # ans = yes_no(prompt)
  # if __debug:
  #   print(f"Answer = {ans}, 0 means YES")
  # sys.exit(ans)
  app()
