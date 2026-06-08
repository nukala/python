# from google search
#  typer how to set the help text of the main program not options 

import typer

app = typer.Typer(help="inline help", no_args_is_help=True)

#@app.callback()
def foo():
    """
    This is the main program help text.

    You can add multiple lines here, and Typer will
    automatically handle the formatting and indentation.
    """
    pass

@app.command()
def create():
    print("Creating item...")

if __name__ == "__main__":
    app()
