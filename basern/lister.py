import os
import sys
from pathlib import Path

# Read the directory path directly
class Lister:
    # js files seem to live in "lib" folder, so dont exclude
    EXCLUDED_DIRS: list[str] = ["venv", ".venv", ".git", ".svn", "__pycache__", "target", "build", "out", ".idea"
        , ".pytest_cache", "classes", "Cache" ]
    EXCLUDED_EXTS: list[str] = [".pyc", ".pyo", ".gitignore", ".ghsvd", ".class", ".ear", ".tar", ".war", ".o", ".obj"]

    @staticmethod
    def is_dir_excluded(dir_path: Path, exclude_dirs: list[str], verbose:int=0) -> bool:
        dir_name = dir_path.name
        for bad_dir in exclude_dirs:
            # exact match, else Cache will exclude redis/cache/src
            if bad_dir == dir_name:
                if verbose > 5:
                    print(f">>> excluding dir='{dir_path}({dir_name})' due to {bad_dir}")
                return True

        return False

    @staticmethod
    def is_file_excluded(file_path: Path, exclude_exts: list[str], verbose:int=0) -> bool:
        file_name = str(file_path)
        for bad_ext in exclude_exts:
            if file_name.endswith(bad_ext):
                if verbose > 5:
                    print(f">>> excluding file '{file_name}', due to {bad_ext}")
                return True

        return False

    @staticmethod
    def deep_search(dir_name: str, exclude_dirs=None, exclude_exts=None, verbose:int=0
                    , posix_path: bool = False) -> list[Path]:
        """
        """
        if exclude_exts is None:
            exclude_exts = []
        if exclude_dirs is None:
            exclude_dirs = []
        dir_path: Path = Path(dir_name)
        the_dirs = [dir_path]

        items: list[Path] = []
        try:
            for dir_path in the_dirs:
                for file_path in dir_path.iterdir():
                    try:
                        if file_path.is_file():
                            # Process files safely here
                            if Lister.is_file_excluded(file_path, exclude_exts, verbose):
                                continue

                            if posix_path:
                                items.append(file_path.absolute().resolve())
                            else:
                                items.append(file_path)
                        elif file_path.is_dir():
                            if Lister.is_dir_excluded(file_path, exclude_dirs, verbose):
                                continue

                            the_dirs.append(file_path)
                            if verbose>1:
                                print(f"Appended directory {file_path}")
                    except Exception as e:
                        sys.stderr.write(f"while iterating e={e}.{type(e).__name__}\n")

        except FileNotFoundError as fnfe:
            sys.stderr.write(f"Directory '{dir_path}' not found. fnfe={str(fnfe)}\n")
        except PermissionError:
            sys.stderr.write(f"Permission denied accessing '{dir_path}'.\n")
        except Exception as e:
            sys.stderr.write(f"An error occurred: {str(e)}.{type(e).__name__}\n")

        return items

    @staticmethod
    def deep_search_strs(dir_name: str, exclude_dirs=None, exclude_exts=None, verbose:int=0
                    , posix_path: bool = False) -> list[str]:
        file_paths: list[Path] = Lister.deep_search(dir_name, exclude_dirs, exclude_exts, verbose, posix_path)
        files: list[str] = [] * len(file_paths)
        for fp in file_paths:
            files.append(str(fp))
        return files


if __name__ == "__main__":
    #for files with unprintable names
    # Forces your console output to safely use UTF-8 encoding
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    verbose: int = 9
    dir2:str = '.' if len(sys.argv) == 1 else sys.argv[1]
    items: list[Path] = Lister().deep_search(dir2, exclude_dirs=Lister.EXCLUDED_DIRS, verbose=verbose
                                             , exclude_exts=Lister.EXCLUDED_EXTS)
    for item in items:
        print(f"{item}")
    if verbose>0:
        print(f"num_items={len(items)}")
