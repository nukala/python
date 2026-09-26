import os
import sys
import time
import typer

from basern.number_utils import parse_duration_ms
from basern.stopwatch import Stopwatch
from dataclasses import dataclass
from typing import Annotated

# /// script
# dependencies = [
#    "typer",
# ]
# ///

app = typer.Typer(add_completion=False, rich_markup_mode="markdown", name="md5",
                  context_settings={"help_option_names": ["-h", "--help", "-?"],
                                    "allow_extra_args": True, 
                                    "ignore_unknown_options": True, })


def sleep_with_timing(milliseconds: int) -> Stopwatch:
    """
    Sleeps for the given number of milliseconds and returns timing details.

    Args:
        milliseconds (int): The duration to sleep in milliseconds.

    Returns:
        stopwatch object that encapsulates the napped-duration, useful if printing details 
    """
    timer:Stopwatch = Stopwatch(name="msnap", precision=1)
    timer.start()
    time.sleep(milliseconds / 1000.0)
    return timer.stop()


class MsNap:
    @dataclass
    class MsNapConfig:
        msnap: int = 0
        verbose: int = 0
        fb_str: str = None
        newline: bool = False

        def dump_config(self, message: str="") -> str:
            msg_str = f"{message}-" if len(message or "") > 0 else ""
            return (f"{msg_str}DUMP: msnap={self.msnap}, verbose={self.verbose}," +
                    f" fb_str={self.fb_str}, newline={self.newline}")


    @app.command()
    def entry_point(ctx: typer.Context,
            fb_str: Annotated[str, typer.Option("-fb", "--feedback", 
                                                help = "feedback character to echo after napping")]="",
            newline: Annotated[bool, typer.Option("-nl", "--new_line",
                                                  help = "terminate with a new line")]=False,
            msnap: Annotated[str, typer.Option("-n", '-nap', '--nap', '--ms_nap', help="Millseconds to nap")]="",
                    
            verbosity: Annotated[int, typer.Option("-v", count=True,
                                                       help="Set verbosity level. Use -v for warning, -vv for info, -vvv for debug.")] = 0,
            vlevel: Annotated[int, typer.Option("--verbosity", "-vrb",
                                                    help="Specify a verbosity level, 1=warning, 2=info,3=debug etc.")] = 0,
                    ):
        """
        Nap/sleep for specified amount of time.
        Various CLI options control additional behavior.

        understands durations like 1s, 1_000ms, 1h etc
        """
        if vlevel>0:
            verbosity=vlevel

        if "lsep" in fb_str:
            fb_str=os.linesep


        nap_ms:int = 0
        if msnap:
            nap_ms = parse_duration_ms(msnap, verbosity)
        used:int=0
        if nap_ms <= 0:
            nap_ms = int(ctx.args[used])
            used=+1
            if verbosity>=2:
                print(f" {verbosity} - converted \"{ctx.args[0]}\" into nap_ms={nap_ms}, used={used}")

        cfg: MsNap.MsNapConfig = MsNap.MsNapConfig(nap_ms, verbose=verbosity, fb_str=fb_str, newline=newline)
        ctx.obj = cfg
        
        nap: MsNap = MsNap()
        nap.do_nap(cfg)
        for arg in ctx.args[used:]:
            try:
                cfg.msnap = parse_duration_ms(arg, cfg.verbose)
                nap.do_nap(cfg)
            except ValueError as err:
                if cfg.verbose>0:
                    print(f"err={err}")

    def do_nap(self, cfg: MsNap.MsNapConfig):
        if cfg.verbose>=2:
          print(f"{cfg.verbose} - napping for [{cfg.msnap}] millis")

        sw: Stopwatch = sleep_with_timing(cfg.msnap)
        if cfg.verbose>0:
          print(f"{cfg.verbose} - elapsed={sw}")
        if cfg.fb_str:
            print(f"{cfg.fb_str}", end=os.linesep if cfg.newline else '', flush=True)

    @staticmethod
    def show_error(msg: str):
        pfx = '' if 'ERR>' in msg else 'ERR> '
        sys.stderr.write(f"{pfx}{msg}")

if __name__ == "__main__":
    app()
