import argparse
import os
import subprocess
import traceback
import zipfile
from pathlib import Path
from types import NoneType
from typing import List, Literal, Optional


class BackupUtils:
    @staticmethod
    def popen_based_run_command(command: str, timeout: int = 30, log_file: Optional[str] = None) -> str:
        """Execute a shell command using Popen (unused alternative implementation)."""
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()  # Clean up
                error = f"Command '{command}' timed out after {timeout} seconds"
                if log_file:
                    with open(log_file, "a") as f:
                        f.write(f"Error: {error}\n\n")
                raise TimeoutError(error)

            if process.returncode != 0:
                error = f"Command '{command}' failed with error: {stderr}"
                if log_file:
                    with open(log_file, "a") as f:
                        f.write(f"Error: {error}\n\n")
                raise RuntimeError(error)

            output = stdout.strip()
            if log_file:
                with open(log_file, "a") as f:
                    f.write(f"Command: {command}\nOutput: {output}\n\n")
            return output
        except Exception as e:
            error = f"Command '{command}' failed with unexpected error: {str(e)}"
            if log_file:
                with open(log_file, "a") as f:
                    f.write(f"Error: {error}\n\n")
            raise


# jun09 - refined from heic_jpg
def dbgln(msg: str, level: int = 0, verbosity: int = 0):
    if level < 0:
        return
    if level <= verbosity:
        pfx: str = ' ' * level
        msg = msg.replace("\n", "\n" + pfx).replace(os.linesep, os.linesep+pfx)

        eol = os.linesep if '\n' not in msg else ''
        # # RNTODO - use one line style
        # nl = '\n'
        # if nl in msg:
        #     nl = ""
        print(f"{pfx}{msg}", end=eol)


def run_shell_command(command: str, timeout: int = 30, verbosity: int = 0,
                      show_output = False, log_file: Optional[str] = None) -> str:
    """Execute a shell command with error handling, timeout, and optional logging."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        dbgln(f"ret={result.returncode}", 1, verbosity)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, command, result.stderr
            )
        output = result.stdout.strip()
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"Command: {command}\nOutput: {output}\n\n")
        if show_output:
            print(f"{output}")

        return output
    except subprocess.TimeoutExpired:
        error = f"Command '{command}' timed out after {timeout} seconds"
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"Error: {error}\n\n")
        raise TimeoutError(error)
    except subprocess.CalledProcessError as e:
        error = f"Command '{command}' failed with error: {e.stderr}"
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"Error: {error}\n\n")
        raise RuntimeError(error)


def get_uncommitted_files(source_dir: str,
                          log_file: Optional[str] = None,
                          verbosity: int = 0) -> List[str]:
    """Get list of uncommitted files in a git repository."""
    os.chdir(source_dir)
    try:
        modified = run_shell_command("git diff --name-only", log_file=log_file)
        modified_cached = run_shell_command("git diff --name-only --cached", log_file=log_file)
        untracked = run_shell_command("git ls-files --others --exclude-standard", log_file=log_file)
        files = set()
        for output in [modified, modified_cached, untracked]:
            if output:
                files.update(output.splitlines())
        return [os.path.join(source_dir, f) for f in files]
    except RuntimeError as e:
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"Error checking git status: {e}\n\n")
        return []


def collect_full_backup(source_dir: str,
                        verbosity: int = 0) -> List[str]:
    """Collect all files including hidden and ignored files."""
    # files: List[str] = []
    # for root, _, filenames in os.walk(source_dir):
    #     for fname in filenames:
    #         files.append(os.path.join(root, fname))
    cmd = "fd -H -tf -E venv -E target -E __pycache__ -E '.idea' -E '.pytest*' -E '*.zip' -E '*.env'  "
    return run_shell_command(cmd, verbosity=verbosity).split('\n')

def bad_start(fname: str, verbosity:int = 0) -> bool:
    bad_begins=[ ".", "__pycache__", "venv"]
    reject=False
    for bb in bad_begins:
        if fname.startswith(bb):
            reject=True
            if verbosity > 2:
                print(f"{' ' * verbosity}rejecting {fname}, bb={bb}")
            break

    return reject

def collect_visible_non_ignored(source_dir: str,
                                verbosity: int = 0) -> List[str]:
    """Collect visible files, excluding .git and hidden files."""
    # files: List[str] = []
    # git_dir = os.path.join(source_dir, ".git")
    # for root, _, filenames in os.walk(source_dir):
    #     if root == git_dir or root.startswith(git_dir + os.sep):
    #         continue
    #     for fname in filenames:
    #         if not bad_start(fname):
    #             files.append(os.path.join(root, fname))

    cmd="fd -tf -E target -E __pycache__ -E venv -E '*.zip' -E out -E '*.env' "
    return run_shell_command(cmd, verbosity=verbosity).split('\n')

def build_zipfn_name(source_dir: str, output_dir: str = ".") -> str:
    """Create a zip backup based on the specified mode."""
    source_path = Path(source_dir).resolve()
    parts = str(source_path).split(os.sep)
    dirname = parts[-1]
    parent_dirname = parts[-2]
    #timestamp = datetime.now().strftime("%y%b%d").lower()
    zip_name = f"{dirname}__{parent_dirname}-{os.getenv('CMPNY', 'rn')}.zip"
    zip_path = os.path.join(output_dir, zip_name)
    return zip_path

def delete_zipfn(zip_fn: str, verbosity: int = 0):
    if Path(zip_fn).exists():
        cmd=f"rm -f {zip_fn}"
        dbgln(f"executing [{cmd}]")
        run_shell_command(cmd, verbosity=verbosity)    

def create_backup_zip(
        source_dir: str,
        backup_mode: Literal["full", "visible", "uncommitted"],
        output_dir: str,
        verbosity: int = 0,
        log_file: Optional[str] = None
) -> Optional[str]:
    """Create a zip backup based on the specified mode."""
    zip_fn = build_zipfn_name(source_dir, output_dir)

    dbgln(f"zip={zip_fn}, mode={backup_mode}", 2, verbosity)
    if backup_mode == "full":
        files = collect_full_backup(source_dir, verbosity)
    elif backup_mode == "visible":
        files = collect_visible_non_ignored(source_dir, verbosity)
    elif backup_mode == "uncommitted":
        files = get_uncommitted_files(source_dir, log_file, verbosity)
    else:
        raise ValueError("Invalid backup mode")

    if not files:
        print("No files to backup.")
        return None

    dbgln(f"Backing up {len(files)} files. ", 1, verbosity)
    dbgln(f"files = {files}.{len(files)}", 2, verbosity)

    delete_zipfn(zip_fn, verbosity)
    ctr:int = 0
    with zipfile.ZipFile(zip_fn, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            ctr += 1
            dbgln(f"{ctr:3d} writing into zip file={file}", 3, verbosity)
            zf.write(file)
    return zip_fn


def copy_to_dbxdir(zip_path: str, verbosity: int = 0) -> bool :
    if not zip_path:
        dbgln(f"empty zip_path, cannot archive")
        return False

    dbx_bak = delete_dbxzip(zip_path, verbosity)
    if dbx_bak is not None:
        # copy zip_path into DBXDIR/dt/ghsv
        run_shell_command(f"cp {zip_path} {dbx_bak}", verbosity=verbosity)
        dbgln(f"Archived into {dbx_bak}")
        run_shell_command(f"ls -ltrd {dbx_bak}", verbosity=verbosity, show_output = True)

    return True

def delete_dbxzip(zip_path: str, verbosity: int = 0) -> Optional[Path] :
    dbgln(f"delete_dbxzip: deleting {zip_path}", 2, verbosity)
    if not zip_path:
        dbgln(f"delete_dbxzip: empty zip_path, cannot archive")
        return None

    # check env
    dbx_env="DBXDIR"
    dbx_dir=os.getenv(dbx_env, "None")
    if dbx_dir.casefold() == "None".casefold():
        dbgln(f"delete_dbxzip: Missing {dbx_env} environment var. ")
        return None

    # check dir DBXDIR/dt/ghsv
    ghsv_dir=Path(dbx_dir, "dt/ghsv")
    if not ghsv_dir.exists():
        dbgln(f"delete_dbxzip: Missing ghsv_dir={ghsv_dir}")
        return None

    # if exists
    #  ls -ltrd -> then rm -f
    dbx_bak=Path(ghsv_dir, zip_path)
    dbgln(f"delete_dbxzip: dbx_bak={dbx_bak}", 5, verbosity)
    if dbx_bak.exists():
        run_shell_command(f"ls -ltrd {dbx_bak}", verbosity=verbosity, show_output = True)
        #print(f"Please remove manually. \nrm - {dbx_bak}")
        cmd=f"rm -f {dbx_bak}"
        dbgln(f"executing [{cmd}]")
        run_shell_command(cmd, verbosity=verbosity)

    return dbx_bak


def setup_parser():
    parser = argparse.ArgumentParser(description="Backup a folder with specified mode.")
    parser.add_argument("-s", "--src", "--source-dir", required=False,
                        dest="source_dir",
                        default=".",
                        help="Source folder to backup")
    parser.add_argument("-o", "--out", "--output-dir", required=False,
                        dest="output_dir",
                        default=".",
                        help="Output directory for zip file")
    parser.add_argument(
        "-m", "--mode", "--backup-mode",
        choices=["full", "visible", "uncommitted"],
        required=False,
        dest="mode",
        help="Backup mode",
        default="uncommitted"
    )
    parser.add_argument("-v", action="count", default=0
                        , help="verbosity, supports -vv for more verbosity"
                        , dest="verbosity")
    parser.add_argument('--verbosity', type=int, default=0, dest="verbosity",
                        help="Enable verbosity by specifying a number")

    parser.add_argument("--log-file", help="Optional log file for shell command outputs")
    parser.add_argument("-nodbx", "--no-dbxdir",
        action="store_true", default=False, dest="no_dbx",
        help="Do not copy into $DBXDIR/dt/ghsv folder")

    return parser


def main() -> None:
    parser = setup_parser()
    args = parser.parse_args()
    dbgln(f"parsed args={args}", 2, args.verbosity)

    try:
        zip_path = create_backup_zip(args.source_dir, args.mode, args.output_dir, args.verbosity, args.log_file)
        if zip_path:
            print(f"Backup created: {zip_path}")
        else:
             zip_fn = build_zipfn_name(args.source_dir, args.output_dir)
             dbgln(f"deleting {zip_fn} in local as well as dbxdir", 1, args.verbosity)
             delete_zipfn(zip_fn, args.verbosity)
             # RNTODO - delete this zip name and arrange for dbx-zip-deletion if allowed
             delete_dbxzip(zip_fn, args.verbosity)

        if args.no_dbx:
            dbgln(f"NOT backing up to $DBXDIR")
        else:
            copy_to_dbxdir(zip_path, args.verbosity)
    except Exception as e:
        print(f"Backup failed: {e}")
        print(f"\nStack Trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
