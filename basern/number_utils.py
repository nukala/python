import re
from typing import Union
from basern.stack import (get_func_name_with_sys, StackDump)

# /// script
# dependencies = [
# ]
# ///

# --- String Parsing Engine ---
def parse_numeric_string(value: str, desc:str = "", verbose:int=0) -> float:
    """Converts shorthand strings (10k, 1.5M, $10_000) into floats.

    Args:
        value: String whose float value needs to be converted
        verbose: verbosity of logs, default=0 (no logs)

    Returns:
        The floating point number as described above

    Raises:
        ValueError: if not string, empty string or unparse-able string
    """
    # fn_msg=""
    # if desc == "salary":
    #     for i in range(7):
    #         fn_msg = fn_msg + f"({i})={get_func_name_with_sys(i)}, "
    #     print(f"all-indices, func_names: {fn_msg}", flush=True)
    fn = f"{get_func_name_with_sys(StackDump.CALLER)}{"" if len(desc) == 0 else f"-\"{desc}\""} : "
    if not isinstance(value, str):
        raise TypeError(f"Input must be a string")
    if not value or not value.strip():
        return 0.0

    cleaned = re.sub(r'[$,_]', '', value).strip().lower()
    # if verbose>3:
    #     print(f"{' '*verbose} value=[{value}] got cleaned into [{cleaned}]")

    suffixes = {
        'k': 1_000.0,
        'm': 1_000_000.0,
        'b': 1_000_000_000.0,
        't': 1_000_000_000_000.0
    }

    last_char = cleaned[-1]
    if last_char in suffixes:
        multiplier = suffixes[last_char]
        number_part = cleaned[:-1].strip()
        if not number_part:
            raise ValueError(f"Missing numeric prefix before suffix in: '{value}'")
        try:
            ret:float = float(number_part) * multiplier
            if verbose>1:
                print(f"{fn} value={value}, mult={multiplier}, ret={ret}")
            return ret
        except ValueError as e:
            raise ValueError(f"Could not parse numeric part of string: '{value}'") from e

    try:
        ret:float = float(cleaned)
        if verbose>1:
            print(f"{fn} value={value}, ret={ret:,.2f}")
        return ret
    except ValueError as e:
        raise ValueError(f"Invalid numeric string format: '{value}'") from e


def parse_duration_ms(value: str, verbose: int = 0) -> int:
    """Converts shorthand duration strings into milliseconds (int only).

    Supported units (case-insensitive):
        - s  → seconds   (1s  = 1_000 ms)
        - m  → minutes   (1m  = 60_000 ms)
        - h  → hours     (1h  = 3_600_000 ms)

    Bare integers are treated as milliseconds.
    Input is cleaned of spaces and underscores before parsing.

    Args:
        value: String representing a duration (e.g. "1s", "30m", "2h", "5000")
        verbose: Verbosity of logs, default=0 (no logs)

    Returns:
        The duration in milliseconds as an int

    Raises:
        ValueError: if not a string, empty string, or unparseable string
    """
    if not isinstance(value, str):
        raise ValueError(f"Expected str, got {type(value).__name__}")

    original = value
    # Clean: strip whitespace + remove underscores
    cleaned = re.sub(r"[\s_]+", "", value).strip().lower()

    if verbose>2:
        print(f"{' '*verbose}: value=[{value}], cleaned=[{cleaned}]")
    if not cleaned:
        raise ValueError("Empty or whitespace-only string")

    if verbose >= 1:
        print(f"[parse_duration_ms] original={original!r} → cleaned={cleaned!r}")

    # Match: optional sign, digits, optional unit (s/m/h)
    match = re.fullmatch(r"(-?\d+)([smh])?", cleaned)
    if not match:
        raise ValueError(f"Unparseable duration string: {original!r}")

    number_str, unit = match.groups()
    number = int(number_str)

    multipliers = {
        None: 1,          # bare number → milliseconds
        "s": 1_000,
        "m": 60_000,
        "h": 3_600_000,
    }

    result = number * multipliers[unit]

    if verbose >= 1:
        print(f"[parse_duration_ms] {number}{unit or ''} → {result} ms")

    return result