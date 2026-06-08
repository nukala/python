import typer
from typing import Annotated

# help="Program help inline string"
app = typer.Typer(no_args_is_help=True)
#vbsty = typer.Option("--verbosity", "-v", count=True, default=0)
# could be a config data class later! 
state = { }

######
# For common options among both the commands!
######
@app.callback()
def main(
    verbosity: Annotated[
        int,
        typer.Option("-v", count=True, help="Increase verbosity level use -vvv for 3.")
    ] = 0,
    vlevel: Annotated[
        int,
	typer.Option("--verbosity", help="Specify a verbosity level")
    ] = 0,
):
    """
    Main application entry point
    is this a 
    multi-line help?
    
    Not a multi-line, but this shows up only when help-paramter is removed from Typer ctor
    """
    # 2. Assign the parsed value to the shared state
    state["verbosity"] = verbosity
    if vlevel > 0:
      state["verbosity"] = vlevel
#      state["vlevel"] = vlevel

@app.command(help="show internal configs future dataclass, now a dictionary")
def show():
    print(state)

@app.command(help="say hello the name specified!")
def hello(name: str):
    print(f"Hello {name}")


@app.command(help="Say goodbye, optionally formal")
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
