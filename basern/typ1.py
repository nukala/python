import typer

app = typer.Typer(help="some inline help string", no_args_is_help=True)


@app.command()
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
