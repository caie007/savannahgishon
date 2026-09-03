"""
Measure the three dataset tiers.

The raw archive is far too large to download for a size check, so we issue an
HTTP HEAD request per monthly file and read Content-Length. This gives an exact
byte count for the full public dataset in about a minute.

Usage:
    python src/sizes.py

Writes:
    output/file_sizes.csv     one row per monthly file
    output/dataset_sizes.csv  one row per tier (raw / working / processing)
"""

import csv
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg  # noqa: E402

GB = 1024 ** 3


def head_size(d):
    """Return (month, url, bytes) for one monthly file, 0 if unavailable."""
    u = cfg.url(d)
    try:
        r = requests.head(u, timeout=30, allow_redirects=True)
        if r.status_code == 200:
            return (d.isoformat()[:7], u, int(r.headers.get("Content-Length", 0)))
        return (d.isoformat()[:7], u, 0)
    except Exception:
        return (d.isoformat()[:7], u, 0)


def main():
    all_months = cfg.months("raw")
    print(f"Measuring {len(all_months)} monthly HVFHV files via HTTP HEAD...")

    with ThreadPoolExecutor(max_workers=12) as pool:
        rows = list(pool.map(head_size, all_months))

    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    with open(f"{cfg.OUTPUT_DIR}/file_sizes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "url", "bytes", "mb"])
        for month, u, b in rows:
            w.writerow([month, u, b, round(b / 1024 / 1024, 1)])

    by_month = {m: b for m, _, b in rows}
    missing = [m for m, b in by_month.items() if b == 0]
    if missing:
        print(f"WARNING: no size returned for {missing} - check availability.")

    summary = []
    for tier in ("raw", "working", "processing"):
        ms = [d.isoformat()[:7] for d in cfg.months(tier)]
        total = sum(by_month.get(m, 0) for m in ms)
        summary.append(
            {
                "tier": tier,
                "n_files": len(ms),
                "first_month": ms[0],
                "last_month": ms[-1],
                "bytes": total,
                "gb_compressed": round(total / GB, 2),
            }
        )

    with open(f"{cfg.OUTPUT_DIR}/dataset_sizes.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)

    print()
    for s in summary:
        print(
            f"{s['tier']:<11} {s['n_files']:>3} files  "
            f"{s['first_month']} to {s['last_month']}  "
            f"{s['gb_compressed']:>7.2f} GB (Parquet, on disk)"
        )
    print("\nWritten to output/dataset_sizes.csv")
    print(
        "NOTE: these are compressed Parquet sizes. Report the uncompressed "
        "logical size alongside them (see notebooks/01_part1_data_and_eda.ipynb)."
    )


if __name__ == "__main__":
    main()
