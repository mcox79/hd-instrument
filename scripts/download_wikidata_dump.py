"""
Download Wikidata truthy N-triples dump (~30 GB compressed).

Source: https://dumps.wikimedia.org/wikidatawiki/entities/latest-truthy.nt.bz2

Resumable via HTTP Range header. Writes to data/wikidata_dump/latest-truthy.nt.bz2.
Logs progress every 30 seconds.

Usage:
    .venv-demo\\Scripts\\python.exe scripts\\download_wikidata_dump.py
"""
from __future__ import annotations
import logging
import sys
import time
from pathlib import Path

URL = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-truthy.nt.bz2"
OUTPUT_DIR = Path("data/wikidata_dump")
OUTPUT_PATH = OUTPUT_DIR / "latest-truthy.nt.bz2"


def setup_logging():
    Path("data").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("data/wikidata_download.log", mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"


def download():
    import requests

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger(__name__)

    # HEAD request for total size
    head = requests.head(URL, allow_redirects=True, timeout=30)
    head.raise_for_status()
    total_size = int(head.headers.get("content-length", 0))
    log.info("remote total size: %s (%d bytes)", fmt_bytes(total_size), total_size)

    # Resume: pick up at existing file size
    start_byte = OUTPUT_PATH.stat().st_size if OUTPUT_PATH.exists() else 0
    if start_byte:
        log.info("resuming from %s (%.2f%%)", fmt_bytes(start_byte),
                 100 * start_byte / total_size if total_size else 0)
    if start_byte >= total_size > 0:
        log.info("file already complete: %s", OUTPUT_PATH)
        return 0

    headers = {"Range": f"bytes={start_byte}-"} if start_byte else {}
    r = requests.get(URL, headers=headers, stream=True, timeout=60)
    r.raise_for_status()

    chunk = 1024 * 1024  # 1 MB
    log.info("starting download to %s ...", OUTPUT_PATH)
    t_start = time.time()
    t_last_log = t_start
    bytes_this_session = 0
    with open(OUTPUT_PATH, "ab") as f:
        for data in r.iter_content(chunk_size=chunk):
            if not data:
                continue
            f.write(data)
            bytes_this_session += len(data)
            now = time.time()
            if now - t_last_log >= 30:
                elapsed = now - t_start
                current = start_byte + bytes_this_session
                pct = 100 * current / total_size if total_size else 0
                rate = bytes_this_session / max(0.001, elapsed)
                remaining = (total_size - current) / max(1, rate)
                log.info("progress: %s / %s (%.2f%%) | rate: %s/s | eta: %.0f min",
                         fmt_bytes(current), fmt_bytes(total_size), pct,
                         fmt_bytes(rate), remaining / 60)
                t_last_log = now

    log.info("DONE: %s (%s in %.0f min)", OUTPUT_PATH,
             fmt_bytes(start_byte + bytes_this_session), (time.time() - t_start) / 60)
    return 0


if __name__ == "__main__":
    setup_logging()
    sys.exit(download())
