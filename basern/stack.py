import inspect
import sys
from multipledispatch import dispatch
from typing import Final

#    "typer",
# /// script
# dependencies = [
#    "multipledispatch",
# ]
# ///


###
# Why this complexity around stack, sys etc? 
#   see stk-tmr.sh for timing details!
##
    # fn_msg=""
    # if desc == "salary":
    #     for i in range(7):
    #         fn_msg = fn_msg + f"({i})={get_func_name_with_sys(i, verbosity)}, "
    #     print(f"all-indices, func_names: {fn_msg}", flush=True)
class StackDump:
  CURRENT_METHOD: Final[int] = 1 
  CALLER: Final[int] = 2
  PARENT_CALLER: Final[int] = 3
  GRANDPARENT_CALLER: Final[int] = 4
 
  def a(self) -> None:
    self.b()

  def b(self) -> None:
    self.c()

  def c(self) -> None:
    self.d()

  def d(self) -> None:
    func: str=inspect.currentframe().f_code.co_name
    # print(f"In {func}")

    caller: str = inspect.stack()[1][3]
    # print(f"Caller = {caller}")

    par: str = inspect.stack()[2][3]
    # print(f"parent = {par}")

    gpar: str = inspect.stack()[3][3]
    # print(f"grandparent caller = {gpar}")

    print(f"So: {gpar} -> {par} -> {caller} -> {func}")
    print(f"Depths: {get_func_name(4)} -> {get_func_name(3)} -> {get_func_name(2)} -> {get_func_name(1)}")
    print(f"Sys: {get_func_name_with_sys(4, True)} -> {get_func_name_with_sys(3, True)} -> {get_func_name_with_sys(2, 9)} -> {get_func_name_with_sys(1, 4)}")
    # save this comment
    #caller: str = inspect.currentframe().f_back.f_code.co_name
    # inspect.stack() for all traces!

    # to see what happens
    boundary_conditions(45)

    boundary_conditions(-5)

def boundary_conditions(depth:int = 21):
    impossibly_deep(depth)
    impossibly_deep(depth, use_sys=True)

def impossibly_deep(depth:int = 21, use_sys:bool=False):
  try:
    func:str = "with_sys" if use_sys else "func_name"
    print(f" {func}(depth={depth})", end='', flush=True)
    get_func_name(depth, use_sys=use_sys)
    print("")
  except IndexError:
    print(f", index-error", flush=True)
  except ValueError:
    print(f", value-error", flush=True)
  

def get_func_name(depth:int = 0, use_sys:bool = False):
  if use_sys:
    return get_func_name_with_sys(depth, True)
  return inspect.stack()[depth][3]

@dispatch(int, int)
def get_func_name_with_sys(depth:int = 0, verbosity:int = 0):
  # Added one, to accomodate the decorator 
  func: str = f"{sys._getframe(depth+1).f_code.co_name} -" if verbosity > 0 else ""
  # if verbosity > 0:
    # print(f" func={func}, verbosity={verbosity}, depth={depth}, sys={sys._getframe(depth)}")
  return func

@dispatch(int, bool)
def get_func_name_with_sys(depth:int = 0, verbose:bool = False):
  # Added one, to accomodate the decorator 
  return f"{sys._getframe(depth+1).f_code.co_name} -" if verbose else ""

if __name__ == "__main__":
    StackDump().a()

