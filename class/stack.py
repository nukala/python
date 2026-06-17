import inspect

class StackDump:
 
  def a(self) -> None:
    self.b()

  def b(self) -> None:
    self.c()

  def c(self) -> None:
    self.d()

  def d(self) -> None:
    func: str=inspect.currentframe().f_code.co_name
    print(f"In {func}")
    caller: str = inspect.stack()[1][3]
    print(f"Caller = {caller}")
    par: str = inspect.stack()[2][3]
    print(f"parent = {par}")
    gpar: str = inspect.stack()[3][3]
    print(f"grandparent caller = {gpar}")

    print(f"\n\nSo: {gpar} -> {par} -> {caller} -> {func}")
    # save this comment
    #caller: str = inspect.currentframe().f_back.f_code.co_name
    # inspect.stack() for all traces!

if __name__ == "__main__":
    StackDump().a()

