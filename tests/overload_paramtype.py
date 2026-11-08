from functools import singledispatchmethod
import os
from multipledispatch import dispatch
from basern.stack import (get_func_name_with_sys, StackDump)

# /// script
# dependencies = [
#    "multipledispatch",
# ]
# ///

class ProcessData:
    @singledispatchmethod
    def process(self, data):
        raise TypeError("Unsupported type")

    # Overload for integers
    @process.register
    def _(self, data: int):
        fn:str = f"{get_func_name_with_sys(StackDump.CURRENT_METHOD)}-int -"
        print(f"{fn} Processing an integer: {data * 2}")

    # Overload for strings
    @process.register
    def _(self, data: str):
        fn:str = f"{get_func_name_with_sys(StackDump.CURRENT_METHOD)}-str -"
        print(f"{fn} Processing a string: {data.upper()}")

class OverloadedCalculator:
    """
    Does not support default values in parameters. Hence we have to send
     in all the values even if signature says default
    Parameter types are allowed 
    """
    # Overload 1: Two integers
    @dispatch(int, int)
    def add(self, x, y):
        # fn:str = f"{get_func_name_with_sys(StackDump.CURRENT_METHOD)}-ints -"
        # print(f" {fn} adding ints ")
        return x + y

    # Overload 2: Two strings
    @dispatch(str, str)
    def add(self, x, y):
        # fn:str = f"{get_func_name_with_sys(StackDump.CURRENT_METHOD)}-strs -"
        # print(f" {fn} adding strs ")
        return x + " " + y

    @dispatch(int, str)
    def add(self, x: int, y: str = "") -> str:
        fn:str = f"{get_func_name_with_sys(StackDump.CURRENT_METHOD)}-int+def_str -"
        if len(y) > 0:
            print(f" {fn} adding int and non-default str ")
            return str(x) + " " + y

        print(f" {fn} adding int and default str, hence like 2x ")
        return x + x



if __name__ == "__main__":
    # Usage
    p = ProcessData()
    p.process(10)      # Output: Processing an integer: 20
    p.process("hello") # Output: Processing a string: HELLO

    print(f"{os.linesep}====== CALCULATOR =====")
    # Usage
    calc: OverloadedCalculator = OverloadedCalculator()
    print(f"calc-ints = [{calc.add(5, 10)}]")       # Output: 15
    print(f"calc-strs = [{calc.add("Hi", "User")}]")  # Output: Hi User
    #print(f"calc-strs_verbose = [{calc.add("Hello", "World", True)}]")  # runtime failure
    #print(f"def-str = [{calc.add(9)}]") # default parameter does not resolve!
    print(f"calc-int_specifed_emptystr = [{calc.add(9, "")}]") 
    print(f"calc-int_somestr = [{calc.add(9, "some")}]")

