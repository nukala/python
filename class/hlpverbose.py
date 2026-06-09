# from google search
#  typer how to set the help text of the main program not options 

import typer

#help="inline help"
app = typer.Typer(no_args_is_help=True)

@app.callback()
def foo():
    """
    This is the main program help text.

    You can add multiple lines here, and Typer will
    automatically handle the formatting and indentation.

    After empty line
    """
    pass

@app.command()
def create():
    print("Creating item...")

if __name__ == "__main__":
    app()
