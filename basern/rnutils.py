from basern.yesno import bool_yesno
from pathlib import Path
from typing import IO

import datetime
import os
import subprocess
import sys
import time

######################
# Bunch of utility methods. Some may be excessive - this being python.
# Almost rehash of similarly named java-equivalent
#########

def is_empty(string:str):
    """
    True only if the specified string is empty
    """
    if not string:
        return True
    return len(string) == 0


def is_not_empty(string):
    """
    True only if the specified string is not empty
    """
    return not is_empty(string)

def is_exists(ff: str|Path):
    """
    True if ff is not-empty AND file exists
    :param ff:
    :return:
    """
    filename = str(ff)
    
    try:
        return is_not_empty(filename) and os.path.exists(filename)
    except FileNotFoundError:
        return False


def duks(dir=".", logf=None, show_result=False, show_output=False):
    duks = getoutput_from_run(['du', '-ks', f"{dir}"], logf, show_result=show_result, show_output=show_output)
    sz = int(duks['stdout'].split()[0])
    return sz


def rename(fn, renamed):
    stat = subprocess.run(["mv", fn, renamed], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if stat.returncode == 0:
        return True
    else:
        return False


def log_ts(verbose = False):
    """
    Timestamp for logging
    If verbose - millisecond accuracy upto 3 digits
    """
    fmt = '%Y-%b-%d %H:%M:%S.%f' if verbose else '%Y-%b-%d %H:%M:%S'
    ts=f"{datetime.datetime.today().strftime(fmt)}"
    # print(f"verbose={verbose}, format={fmt}, ts={ts}")
    if verbose:
        ts=ts[:-3]
    return ts

def get_next_logname(fname):
    """
    Tries a few times to find a ## suffixed log that does not exist.
    if nothing is found, return the original requested filename
    """
    basefn = befsub(fname, ".")

    ## see if we can send the un-numbered log
    lfn = f"{basefn}.log"
    if is_exists(lfn) == False:
        return lfn
    elif os.stat(lfn).st_size == 0:
        return lfn

    for i in range(1, 29):
        lfn = f"{basefn}{i}.log"
        if is_exists(lfn):
            # print(f"counter={i}")
            if os.stat(lfn).st_size == 0:
                return lfn
            else:
                continue
        else:
            return lfn

    return fname


def contains(line, part):
    try:
        dex = line.find(part)
        return dex >= 0
    except TypeError:
        return False


# substringBeforeFirst
def befsub(str, sep):
    try:
        dex = str.index(sep)

        if dex > 0:
            return str[:dex]
        else:
            return str
    except ValueError:
        return str


def get_long_filename(prefix, suffix="log"):
    now = datetime.datetime.today()
    # https://strftime.org/
    return f"{prefix}-{now.strftime('%m%d%I%M')}.{suffix}"


def get_mmdd_filename(prefix, suffix="log"):
    now = datetime.datetime.today()
    return f"{prefix}-{now.strftime('%m%d')}.{suffix}"


def write_log(logf, msg):
    ts = datetime.datetime.today().strftime('%Y-%b-%d %H:%M:%S')
    message = f"{ts} ---=== {msg} ===--- "

    if logf == None:
        print(f"{message}")
    else:
        logf.write(f"{message}{os.linesep}")
        logf.flush()


def tee_log(logf, msg, do_print=True):
    if do_print == True:
        print(msg)
    if logf != None:
        write_log(logf, msg)


def log_started_message(logf, prog=""):
    tee_log(logf, f"""###
# {prog} started at {datetime.datetime.now().strftime('%I:%M.%S %p on %d %b %Y')}
### """)


def do_nap(ss, log=None):
    tee_log(log, f"Napping for {ss} seconds")
    time.sleep(ss)


def _parse_num_bytes(num_bytes: int | str) -> int:
    """
    Coerce num_bytes to a non-negative int.

    Accepts plain ints or numeric strings (e.g. '1024').
    Floats are explicitly rejected — bytes are always whole numbers.

    Raises:
        TypeError:  If the value is a float, or cannot be converted at all.
        ValueError: If the value is a valid type but negative, or a
                    non-numeric string (e.g. 'abc').
    """
    if isinstance(num_bytes, float):
        raise TypeError(
            f"num_bytes must be an int or numeric string, not float. "
            f"Use int(value) to truncate if intentional."
        )
    try:
        parsed = int(num_bytes)
    except (ValueError, TypeError) as exc:
        raise type(exc)(
            f"num_bytes must be an int or numeric string, "
            f"got {type(num_bytes).__name__!r} with value {num_bytes!r}"
        ) from exc

    if parsed < 0:
        raise ValueError(f"num_bytes must be >= 0, got {parsed}")

    return parsed


def bytes_to_kb(num_bytes: int | str) -> float:
    """Convert bytes to kilobytes."""
    return _parse_num_bytes(num_bytes) / 1024


def bytes_to_mb(num_bytes: int | str) -> float:
    """Convert bytes to megabytes."""
    return _parse_num_bytes(num_bytes) / (1024 * 1024)


##### Write Python utility functions and unit tests to:
# Convert a byte count (int | str) to a human-readable KB or MB string, switching to MB at a configurable threshold (default 1024 KB). Decimal precision is also configurable.
# Centralise input validation in a private helper: reject floats and non-convertible types with TypeError, negatives and non-numeric strings with ValueError.
# Functions max 10–15 lines, fully typed.
# Tests use unittest only, covering valid int and str inputs, threshold boundaries, all TypeError and ValueError cases, and zero.
def format_bytes(
    num_bytes: int | str,
    mb_threshold_kb: float = 1024.0,
    decimal_places: int = 2,
) -> str:
    """
    Convert a byte count to a human-readable KB or MB string.

    Displays in MB when the KB value meets or exceeds mb_threshold_kb,
    otherwise displays in KB.

    Args:
        num_bytes:        Raw byte count as int or numeric string. Must be >= 0.
        mb_threshold_kb:  KB value at which to switch to MB (default 512 KB).
        decimal_places:   Number of decimal places in the output (default 2).

    Returns:
        Formatted string such as '1.23 MB' or '456.00 KB'.

    Raises:
        TypeError:  If num_bytes is a float or a non-convertible type.
        ValueError: If num_bytes is negative, a non-numeric string,
                    or decimal_places is negative.
    """
    if decimal_places < 0:
        raise ValueError(f"decimal_places must be >= 0, got {decimal_places}")

    parsed = _parse_num_bytes(num_bytes)
    kb_value = bytes_to_kb(parsed)

    if kb_value >= mb_threshold_kb:
        mb_value = bytes_to_mb(parsed)
        return f"{mb_value:.{decimal_places}f} MB"

    return f"{kb_value:.{decimal_places}f} KB"

def elapsed_seconds(start):
    return f"elapsed={round(time.time() - start, 2)} seconds"


################
# run/exec helpers
################
def getoutput_from_run(cmd, logf, show_cmd=False, show_result=True, show_output=False, show_error=False):
    """
    Preferred way to execute shell commands (why?)

    Args:
        cmd: Shell command to execute.
        logf: File to write logs into (None-able)
        show_cmd: Show the command being exected (default False)
        show_result: Show result (default True)
        show_output: Show output (default False)
        show_error: Show error (default False)

    Returns:
        dict:
            returncode: command's execution status
            stdout: output from the command
            stderr: its error if any
            exception: Exception thrown by code if any
            elapsed: rounded to 2 decimals execution duration
    """
    start = time.time()
    out = None
    err = None
    returncode = 252
    excpt = None
    elapsed = 0
    try:
        if show_cmd == True:
            write_log(logf, f"About to start {cmd}")
        # TODO: cat no_exist does not goto out nor err
        # TODO: no special env or other-optional params
        cmd_str = " ".join(cmd)
        use_shell = False
        if isinstance(cmd, str):
            use_shell = True
            cmd_str = cmd

        proc = subprocess.Popen(cmd, shell=use_shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        returncode = proc.wait()
        if proc.stdout is not None:
            out = str(proc.stdout.read(), 'utf-8').strip()

        if proc.stderr is not None:
            err = str(proc.stderr.read(), 'utf-8').strip()

        elapsed = time.time() - start
        if show_result:
            tee_log(logf, f"[{cmd_str}]={returncode}, elapsed={round(elapsed, 2)} seconds")
        if show_output:
            tee_log(logf, f"===== [{cmd_str}]={returncode} ===== ")
            tee_log(logf, out)
            tee_log(logf, f"----- [{cmd_str}]={returncode} ----- ")
        if show_error:
            tee_log(logf, f"===== ERR [{cmd_str}]={returncode} ===== ")
            tee_log(logf, err)
            tee_log(logf, f"----- err [{cmd_str}]={returncode} ----- ")

    except (FileNotFoundError, PermissionError) as e:
        returncode = 1
        excpt = e

    return {'returncode': returncode, 'stdout': out, 'stderr': err, 'exception': excpt, 'elapsed': round(elapsed, 2)}


###
# For long running commands=https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
###
def do_run(cmd, logf, inpt=None, special_env=None, show_cmd=False, show_result=True):
    """
    Runs the specified cmd or list
    grabs all the output (may encounter bufffing challenges) into memory
    """
    if show_cmd == True:
        tee_log(logf, cmd)
    env = None
    if special_env is not None:
        env = {}
        env.update(os.environ)
        env.update(special_env)

    cmdStr = " ".join(cmd)
    useShell = False
    if isinstance(cmd, str):
        useShell = True
        cmdStr = cmd

    try:
        # THERE SHOULD BE A BETTER WAY
        if logf is not None:
            stat = subprocess.run(cmd, stdout=logf, stderr=logf, text=True, input=inpt, env=env, close_fds=True,
                                  shell=useShell)
        else:
            stat = subprocess.run(cmd, text=True, input=inpt, env=env, close_fds=True, shell=useShell)
    except (FileNotFoundError) as e:
        tee_log(logf, f"{cmdStr} failed: {e}")
        stat = subprocess.CalledProcessError(252, cmd)

    if show_result == True:
        tee_log(logf, f"do_run: Command=[{cmdStr}], ret={stat.returncode}")

    # https://stackoverflow.com/questions/66763957 for why yes_no fails after this call!
    # https://docs.python.org/3/library/subprocess.html
    #  macos is OK, win10 both bash and dos fail inside cmder as well cmd
    # stat = close(in_write_pipe_fd)
    # if stat != None:
    #   print(f"close(in_write_pipe_fd) failed={stat}")

    return stat


def ask_then_run(cmd, logf, inpt=None, special_env=None, show_result=True, show_feedback=False):
    write_log(logf, cmd)
    stat = None
    if not bool_yesno(f'Start {cmd}: (y/n) [n] '):
        if show_feedback:
            tee_log(logf, "NOT running as requested!")
        else:
            write_log(logf, "NOT running as requested!")
        stat = subprocess.CalledProcessError(252, cmd)
    else:
        stat = do_run(cmd, logf, inpt, special_env)

    return stat

def open_resolved(path: Path | str, mode: str = "rb", encoding: str = None, verbose: int = 0) -> IO:
  """
  Open a file, resolving Cygwin WSL-format symlinks on Windows/Cygwin
  before opening. On all other platforms, opens directly.

  Args:
      path:     The path to open, as a Path or str.
      mode:     File mode, e.g. "rb", "r", "w". Defaults to "rb".
      encoding: Encoding for text modes. Ignored for binary modes.
      verbose: Verbosity level.

  Returns:
      An open file object (binary or text depending on mode).

  Raises:
      OSError: If the file cannot be found or opened.
      subprocess.CalledProcessError: If cygpath fails (Cygwin only).

  Examples:
      with open_resolved("dir/yy/file.txt", "rb") as f:
          data = f.read()

      with open_resolved("dir/yy/file.txt", "r", encoding="utf-8") as f:
          text = f.read()
  """

  resolved: Path = (
    adjust_winpath(str(path), verbose)
    if sys.platform in ("win32", "cygwin")
    else Path(path)
  )

  if verbose >= 3:
      print(f"Opening {resolved}")

  return open(resolved, mode=mode, encoding=encoding)


def adjust_winpath(file_name:str, verbose:int = 0) -> Path:
    """
    Adjusts file_name into WINDOwS friendly version.
    Seems like `ln -s ` only WORKS when using `CYGWIN=winsymlinks:nativestrict ln -s FROM TO`
    """

    if sys.platform not in ("win32", "cygwin"):
        return Path(file_name)

    adjusted = file_name

    drives = {
        "/c/": "C:/",
        "/cygdrive/c/": "C:/",
        "/mnt/cygdrive/c/": "C:/",
        "/mnt/c/": "C:/",
        "/d/": "D:/",
        "/cygdrive/d/": "D:/",
    }
    for key in drives:
        if file_name.startswith(key):
            repl = drives.get(key)
            if verbose > 1:
                print(f"[{file_name}] replacing={key} with={repl}")
            file_name = file_name.replace(key, repl)

    if verbose >= 1:
        print(f"[{adjusted}] after replacements=[{file_name}]")

    # fn = file_name
    # if os.path.islink(file_name):
    #     fn = os.path.readlink(file_name)
    #     # BROKEN, UNTESTABLE code for links
    #     if verbose > 1:
    #         print(f" file=\"{file_name}\" is a link, resolved to={fn}\n")
    # else:
    #     # from pathlib import Path
    #     # real = Path(file_name).resolve()
    #     rs = os.lstat(file_name)
    #     if verbose > 1:
    #         print(f" resolved={rs}")
    #     fn = os.path.realpath(file_name)
    #     if verbose > 1:
    #         print(f" realpath={fn}, for file={file_name}\n")

    replaced_path = resolve_with_cygpath(file_name, verbose)

    # if not os.path.exists(replaced_path):
    #   raise FileNotFoundError(f"No such file \"{replaced_path}\" \n")

    return replaced_path

def resolve_with_cygpath(path: Path | str, verbose:int = 0) -> Path:
    """
    Resolve a path that may contain Cygwin WSL-format symlinks.

    Attempts os.stat() first — the fast path for regular files/dirs.
    On winerror 1920 (unresolved reparse point), delegates to cygpath.
    All other OSErrors (not found, permission denied) are re-raised.

    Args:
        path: The path to resolve, as a Path or str.

    Returns:
        A resolved absolute Path.

    Raises:
        OSError: If the path doesn't exist or is inaccessible for
                 reasons other than an unresolved reparse point.
        subprocess.CalledProcessError: If cygpath fails.
    """
    p: Path = Path(path)

    try:
        os.stat(p)
        return p
    except OSError as e:
        if e.winerror != 1920:
            raise

        if verbose >= 2:
            print(f"[{path}] failed to stat, e=[{e}], executing cygpath\n")
        raw: str = subprocess.check_output(
            ["cygpath", "-aw", p.as_posix()],
            stderr=subprocess.DEVNULL,
            text=True,                   # decode stdout automatically
        ).strip()

        resolved: Path = Path(raw)
        os.stat(resolved)                # validate — raises OSError if still broken
        return resolved


def get_pwd(use_tilda:bool = True):
    """
    Should be get_pwd_nodrive - this should be marked broken
    """
    pwd = os.getcwd()
    if use_tilda:
        pwd = pwd.replace(os.environ['HOME'], '~')
    pwd = pwd.replace("C:", "").replace("F:", "")
    pwd = pwd.replace("\\", "/").replace("\\\\", "/")

    return pwd


def short_dir(folder:str, num_dirs:int=3, separator:str="/", verbose:int=0, flipped:bool=False):
    pfx = "dbg> "
    # cwd = os.getcwd()
    # pwd = cwd.replace("C:", "").replace("F:", "").replace("\\", "/")
    elems: list[str] = folder.replace("\\", "/").replace("\\\\", "/").split('/')
    if verbose > 1:
        print(f"{pfx}folder={folder}, elems={elems}")
    num = len(elems)

    act_size = num_dirs
    if num_dirs > num:
        act_size = num
    elif num_dirs <= 0:
        act_size = 1
    if verbose >= 1:
        print(f"{pfx}Requested size={num_dirs} is un-handle able. Changed to {act_size}")

    if separator is None:
        if verbose > 1:
            print(f"{pfx}Disallowed separator({separator}), using \"/\"")
        separator = "/"
    if verbose > 1:
        print(f"{pfx}using separator=[{separator}].{len(separator)}")

    if flipped:
        start = num-1
        end = max(start - act_size, 0)
        step = -1
    else:
        start = num-act_size
        end = num
        step = 1

    ary = elems[start:end:step]
    if verbose >= 2:
        print(f"{pfx}flipped={flipped}, start={start}, end={end}, step={step}, sliced={ary}")
    ret = separator.join(ary)

    return ret

def find_recursively(fname, start_path=None, check_folder=False, verbose=False):
    if start_path is None:
        start_path = os.getcwd()
        if verbose: 
            print(f"start_path = [{start_path}]")

    current_dir = start_path
    while True:
        the_path = os.path.join(current_dir, fname)
        if verbose: 
            print(f" checking the_path = [{the_path}]")
        if check_folder and os.path.isdir(the_path):
            return the_path
        elif os.path.isfile(the_path):
            return the_path

        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            # Reached the root directory
            break

        current_dir = parent_dir

    return None

# # Example usage
# filename_to_find = "example.txt"
# found_path = find_file_in_parents(filename_to_find)

# if found_path:
#     print(f"File found at: {found_path}")
# else:
#     print("File not found in current or parent directories.")

#   pass
def get_prog(path):
    if path is not None:
        prog = path
    else:
        prog = __file__

    prog = os.path.basename(prog)
    prog = prog.split('.')[0]
    return prog


def get_tmp_log(name=None):
    if name is None:
        name = get_prog(__file__)

    logdir = os.environ['HOME'] + os.sep + 'tmp' + os.sep + "git"
    os.makedirs(logdir, exist_ok=True)
    fn = logdir + os.sep
    if fn.count(".") > 0:
        fn = fn + name
    else:
        fn = fn + name + ".log"

    # print(f"{name}: fn=[{fn}], exists={is_exists(fn)}")
    return fn


########################
# git stuff
########################


def get_gitroot(logf=None):
    m = getoutput_from_run(['git', 'rev-parse', '--git-dir'], logf, show_result=False)
    root = None
    if m['returncode'] == 0:
        root = m['stdout']
    return root


def get_num_modifications(logf):
    num = 0
    m = getoutput_from_run(['git', 'status', '-s'], logf, show_output=False)
    for i in m['stdout'].split(os.linesep):
        i = i.strip()
        if i.startswith("M"):
            num = num + 1

    return num


def get_gitbranch(logf=None):
    """
    " equivalent to gtbr
    """
    branch = None
    m = getoutput_from_run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], logf, show_result=False, show_cmd=False)
    # print(f"{m}")

    if m['returncode'] == 0:
        branch = m['stdout']

    return branch
