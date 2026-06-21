import inspect
import sys


###
# Why this complexity around stack, sys etc? 
#   see stk-tmr.sh for timing details!
##
class StackDump:
 
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
    print(f"Sys: {get_func_name(5, True)} -> {get_func_name(4, True)} -> {get_func_name(3, True)}" 
      + f" -> {get_func_name(2, True)}")
    # save this comment
    #caller: str = inspect.currentframe().f_back.f_code.co_name
    # inspect.stack() for all traces!

def get_func_name(depth:int = 0, use_sys:bool = False):
  if use_sys:
    return get_func_name_with_sys(depth)
  return inspect.stack()[depth][3]
  
def get_func_name_with_sys(depth:int = 0):
  return sys._getframe(depth).f_code.co_name

if __name__ == "__main__":
    StackDump().a()

