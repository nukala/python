import argparse
import json
import requests
import pandas as pd
import io
import os
import time
import shutil
from typing import Dict, List
from tabulate import tabulate

# --- Constants ---
REGISTRY_FILE = "etf_registry.json"
CACHE_DIR = ".etf_cache"

def load_registry(file_path: str = REGISTRY_FILE) -> Dict:
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)

def get_cached_content(ticker: str, expiry_seconds: int, offline: bool = False) -> str | None:
    """Returns cached CSV content if not expired (or if offline mode is on)."""
    cache_path = os.path.join(CACHE_DIR, f"{ticker}.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            data = json.load(f)
            # If offline, we don't care about the timestamp
            if offline or (time.time() - data['timestamp'] < expiry_seconds):
                return data['content']
    return None

def save_to_cache(ticker: str, content: str) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{ticker}.json")
    with open(cache_path, 'w') as f:
        json.dump({"timestamp": time.time(), "content": content}, f)

def clear_cache() -> None:
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        print("Cache cleared successfully.")
    else:
        print("No cache found to clear.")

def parse_holdings(ticker: str, content: str, registry: Dict) -> Dict[str, float]:
    config = registry.get(ticker)
    if not config or not content: return {}
    try:
        if config["format"] == "ishares":
            df = pd.read_csv(io.StringIO(content), skiprows=9).dropna(subset=['Ticker', 'Weight (%)'])
            return dict(zip(df['Ticker'].str.strip(), df['Weight (%)'].astype(float)))
        else:
            df = pd.read_csv(io.StringIO(content))
            df.columns = [str(c).strip() for c in df.columns]
            t_col = 'Ticker' if 'Ticker' in df.columns else df.columns[0]
            w_col = [c for c in df.columns if 'Weight' in c][0]
            return dict(zip(df[t_col].astype(str).str.strip(), df[w_col].astype(float)))
    except Exception:
        return {}

def csv_list(string: str) -> List[str]:
    return [s.strip().upper() for s in string.split(',') if s.strip()]

def main() -> None:
    parser = argparse.ArgumentParser(description="Hacker-friendly ETF Comparison Tool")
    parser.add_argument("--etfs", type=csv_list, default="SMH,SOXX")
    parser.add_argument("--stocks", type=csv_list, default="AMAT,LRCX,KLAC,MU,WDC,ASML")
    parser.add_argument("--cache-min", type=int, default=60)
    parser.add_argument("--offline", action="store_true", help="Use cache regardless of expiry")
    parser.add_argument("--cache-cleanup", action="store_true", help="Delete all cached data and exit")
    parser.add_argument("--format", choices=["ascii", "csv"], default="ascii")
    args = parser.parse_args()

    if args.cache_cleanup:
        clear_cache()
        return

    registry = load_registry()
    target_etfs = [e for e in args.etfs if e in registry]
    all_holdings: Dict[str, Dict[str, float]] = {}

    for etf in target_etfs:
        content = get_cached_content(etf, args.cache_min * 60, args.offline)
        
        if content is None:
            if args.offline:
                print(f"Offline Error: No cache found for {etf}")
                content = ""
            else:
                try:
                    r = requests.get(registry[etf]["url"], headers={'User-Agent': 'Mozilla/5.0'}, timeout=50)
                    content = r.text
                    save_to_cache(etf, content)
                except Exception as e:
                    print(f"Network error for {etf}: {e}")
                    content = ""
        
        all_holdings[etf] = parse_holdings(etf, content, registry)

    rows, totals = [], {e: 0.0 for e in target_etfs}
    for s in args.stocks:
        row = {"Symbol": s}
        for etf in target_etfs:
            weight = all_holdings[etf].get(s, 0.0)
            row[etf] = f"{weight:.2f}%"
            totals[etf] += weight
        rows.append(row)

    rows.append({"Symbol": "---", **{e: "---" for e in target_etfs}})
    rows.append({"Symbol": "SELECTED TOTAL", **{e: f"{totals[e]:.2f}%" for e in target_etfs}})
    
    df = pd.DataFrame(rows)
    print(df.to_csv(index=False) if args.format == "csv" else tabulate(df, headers="keys", tablefmt="grid"))

if __name__ == "__main__":
    main()
