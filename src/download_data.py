"""
Download HVFHV monthly Parquet files for a given tier.

Usage:
    python src/download_data.py processing     # 12 files, ~6 GB
    python src/download_data.py working        # ~29 files, ~14 GB

Files land in data/raw/ and are skipped if already present with the expected
size, so the script is safe to re-run after an interrupted download.
"""

import os
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg  # noqa: E402


def download(url, dest):
    if os.path.exists(dest):
        try:
            expected = int(
                requests.head(url, timeout=30, allow_redirects=True).headers[
                    "Content-Length"
                ]
            )
            if os.path.getsize(dest) == expected:
                print(f"  skip (already complete): {os.path.basename(dest)}")
                return
        except Exception:
            pass

    print(f"  downloading {os.path.basename(dest)} ...", end="", flush=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        tmp = dest + ".part"
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
        os.replace(tmp, dest)
    print(f" {os.path.getsize(dest) / 1024 / 1024:.0f} MB")


def main():
    tier = sys.argv[1] if len(sys.argv) > 1 else "processing"
    os.makedirs(cfg.LOCAL_DATA_DIR, exist_ok=True)

    ms = cfg.months(tier)
    print(f"Tier '{tier}': {len(ms)} monthly files "
          f"({ms[0].isoformat()[:7]} to {ms[-1].isoformat()[:7]})")

    for d in ms:
        download(cfg.url(d), os.path.join(cfg.LOCAL_DATA_DIR, cfg.filename(d)))

    # Zone lookup - small, needed for every geographic join.
    zone_dest = os.path.join(cfg.LOCAL_DATA_DIR, "taxi_zone_lookup.csv")
    download(cfg.ZONE_LOOKUP_URL, zone_dest)

    total = sum(
        os.path.getsize(os.path.join(cfg.LOCAL_DATA_DIR, f))
        for f in os.listdir(cfg.LOCAL_DATA_DIR)
    )
    print(f"\nLocal data directory: {total / 1024 ** 3:.2f} GB")


if __name__ == "__main__":
    main()
