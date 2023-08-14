from basern.yesno import bool_yesno

import datetime
import os
import subprocess
import sys
import time



def is_empty(string):
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


def is_exists(filename):
    """
    True if filename is not-empty AND file exists
    :param filename:
    :return:
    """
    try:
        return is_not_empty(filename) and os.path.exists(filename)
    except FileNotFoundError:
        return False

def duks(dir = ".", logf = None, show_result = False, show_output = False):
  duks = getoutput_from_run(['du', '-ks', f"{dir}"], logf, show_result= show_result, show_output = show_output)
  sz = int(duks['stdout'].split()[0])
  return sz

def rename(fn, renamed):
  stat = subprocess.run(["mv", fn, renamed], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
  if stat.returncode == 0:
    return True
  else:
    return False

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
      #print(f"counter={i}")
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

def get_long_filename(prefix, suffix = "log"):
  now = datetime.datetime.today()
  # https://strftime.org/
  return f"{prefix}-{now.strftime('%m%d%I%M')}.{suffix}"

def get_mmdd_filename(prefix, suffix = "log"):
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

def tee_log(logf, msg, do_print = True):
  if do_print == True:
    print(msg)
  if logf != None:
    write_log(logf, msg)

def log_started_message(logf, prog = ""):
  tee_log(logf, f"""###
# {prog} started at {datetime.datetime.now().strftime('%I:%M.%S %p on %d %b %Y')}
### """)


def do_nap(ss, log = None):
  tee_log(log, f"Napping for {ss} seconds")
  time.sleep(ss)


def elapsed_seconds(start):
  return f"elapsed={round(time.time() - start, 2)} seconds"


################
# run/exec helpers
################
def getoutput_from_run(cmd, logf, show_cmd = False, show_result = True, show_output = False, show_error = False):
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
    cmdStr = " ".join(cmd)
    useShell = False
    if isinstance(cmd, str):
      useShell = True
      cmdStr = cmd

    proc = subprocess.Popen(cmd, shell = useShell, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    returncode = proc.wait()
    if proc.stdout is not None:
      out = str(proc.stdout.read(), 'utf-8').strip()

    if proc.stderr is not None:
      err = str(proc.stderr.read(), 'utf-8').strip()

    elapsed = time.time() - start
    if show_result == True:
      tee_log(logf, f"[{cmdStr}]={returncode}, elapsed = {round(elapsed, 2)} seconds")
    if show_output == True:
      tee_log(logf, f"===== [{cmdStr}]={returncode} ===== ")
      tee_log(logf, out)
      tee_log(logf, f"----- [{cmdStr}]={returncode} ----- ")
    if show_error == True:
      tee_log(logf, f"===== ERR [{cmdStr}]={returncode} ===== ")
      tee_log(logf, err)
      tee_log(logf, f"----- err [{cmdStr}]={returncode} ----- ")

  except (FileNotFoundError, PermissionError) as e:
    returncode = 1
    excpt = e

  return { 'returncode': returncode, 'stdout': out, 'stderr': err, 'exception': excpt, 'elapsed': round(elapsed, 2) }


###
# For long running commands = https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
###
def do_run(cmd, logf, inpt = None, special_env = None, show_cmd = False, show_result = True):
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
      stat = subprocess.run(cmd, stdout = logf, stderr = logf, text = True, input = inpt, env = env, shell = useShell)
    else:
      stat = subprocess.run(cmd, text = True, input = inpt, env = env, shell = useShell)
  except (FileNotFoundError) as e:
    tee_log(logf, f"{cmdStr} failed: {e}")
    stat = subprocess.CalledProcessError(252, cmd)

  if show_result == True:
    tee_log(logf, f"do_run: Command=[{cmdStr}], ret={stat.returncode}")

  return stat


def ask_then_run(cmd, logf, inpt = None, special_env = None, show_result = True, show_feedback = False):
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

def get_pwd(use_tilda = True):
  pwd = os.getcwd()
  if use_tilda == True:
    return pwd.replace(os.environ['HOME'], '~')

  return pwd

def short_pwd():
  here = get_pwd(False)
  a = os.getcwd().replace("\\", "/").split('/')
  ret=here

  sz = len(a)
  if sz >= 3:
    ret = f"{a[sz-3]}/{a[sz-2]}/{a[sz-1]}"
  elif sz == 2:
    ret = f"{a[sz-2]}/{a[sz-1]}"

  #ret = f"{ret}.{sz}"
  return ret

def get_prog(path):
  if path is not None:
    prog = path
  else:
    prog = __file__

  prog = os.path.basename(prog)
  prog = prog.split('.')[0]
  return prog

def get_tmp_log(name = None):
  if name is None:
    name = get_prog(__file__)

  logdir = os.environ['HOME'] + os.sep + 'tmp' + os.sep + "git"
  os.makedirs(logdir, exist_ok = True)
  fn = logdir + os.sep
  if fn.count(".") > 0:
    fn = fn + name
  else:
    fn = fn + name + ".log"

  #print(f"{name}: fn=[{fn}], exists={is_exists(fn)}")
  return fn

########################
# git stuff
########################

def get_gitroot(logf = None):
  m = getoutput_from_run(['git', 'rev-parse', '--git-dir'], logf, show_result = False)
  root = None
  if m['returncode'] == 0:
    root = m['stdout']
  return root

def get_num_modifications(logf):
  num = 0
  m = getoutput_from_run(['git', 'status', '-s'], logf, show_output = False)
  for i in m['stdout'].split(os.linesep):
    i = i.strip()
    if i.startswith("M"):
      num = num + 1

  return num

def get_gitbranch(logf = None):
  """
  " equivalent to gtbr
  """
  branch = None
  m = getoutput_from_run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], logf, show_result = False, show_cmd = False)
  #print(f"{m}")

  if m['returncode'] == 0:
    branch = m['stdout']

  return branch
