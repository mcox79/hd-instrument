"""
Overnight extraction chain watcher per Research OVERNIGHT_EXTRACTION_QUEUE.

Waits for the current Wikipedia 100K ingest to finish (detected by presence of
data/substrate_state/wikipedia_100k/keys.npy), then runs EXTRACT-1, -2, -3 sequentially.
EXTRACT-4 PubMed is a stretch (handled if extract_pubmed is True).

Each extract:
  - Has its own ingest module in backend/kb/
  - Writes its own data/substrate_state/<source>/ directory
  - Has its own progress.json + stats.json
  - Logs to a shared chain.log

This script is the "cron" — it runs in detached process via wmic; survives SSH disconnect.

Usage:
    .venv-demo\\Scripts\\python.exe scripts\\extraction_chain.py

Or with custom targets:
    --conceptnet-n 8000000
    --arxiv-n 2000000
    --wikidata-n 50000000
    --skip-pubmed
"""
from __future__ import annotations
import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOG_FILE = Path("data/extraction_chain.log")


def setup_logging():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def wait_for_signal(signal_path: Path, label: str, poll_s: int = 60, timeout_hr: int = 24) -> bool:
    """Wait for a file to appear (signal of prior step completion). Returns True if found."""
    log = logging.getLogger("chain")
    log.info("waiting for signal: %s (label=%s; poll %ds; timeout %dhr)",
             signal_path, label, poll_s, timeout_hr)
    deadline = time.time() + timeout_hr * 3600
    while time.time() < deadline:
        if signal_path.exists():
            log.info("signal received for %s: %s", label, signal_path)
            return True
        time.sleep(poll_s)
    log.error("TIMEOUT waiting for %s after %dhr", label, timeout_hr)
    return False


def run_step(module: str, args: list, label: str) -> bool:
    """Run an extraction module as a subprocess; return True on success."""
    log = logging.getLogger("chain")
    cmd = [sys.executable, "-m", module] + args
    log.info("STARTING %s: %s", label, " ".join(cmd))
    t0 = time.time()
    try:
        result = subprocess.run(cmd, check=False, capture_output=False)
        elapsed = time.time() - t0
        if result.returncode == 0:
            log.info("DONE %s in %.0f s (%.1f hr)", label, elapsed, elapsed / 3600)
            return True
        log.error("FAILED %s exit=%d after %.0fs", label, result.returncode, elapsed)
        return False
    except Exception as e:
        log.exception("CRASH %s: %s", label, e)
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--wikipedia-keys", type=Path,
                   default=Path("data/substrate_state/wikipedia_100k/keys.npy"),
                   help="signal that Q2 Wikipedia ingest is done")
    p.add_argument("--conceptnet-n", type=int, default=8_000_000)
    p.add_argument("--arxiv-n", type=int, default=2_000_000)
    p.add_argument("--wikidata-n", type=int, default=50_000_000)
    p.add_argument("--skip-pubmed", action="store_true", default=False,
                   help="skip EXTRACT-4 (PubMed; stretch)")
    p.add_argument("--skip-wikidata", action="store_true", default=False,
                   help="skip EXTRACT-3 (Wikidata; longest)")
    p.add_argument("--skip-arxiv", action="store_true", default=False)
    p.add_argument("--skip-conceptnet", action="store_true", default=False)
    p.add_argument("--no-wait", action="store_true", default=False,
                   help="don't wait for Wikipedia keys.npy; start immediately")
    args = p.parse_args()

    setup_logging()
    log = logging.getLogger("chain")
    log.info("=== extraction_chain start ===")
    log.info("config: conceptnet_n=%d arxiv_n=%d wikidata_n=%d skip_pubmed=%s",
             args.conceptnet_n, args.arxiv_n, args.wikidata_n, args.skip_pubmed)

    # Step 0: wait for Wikipedia ingest to land its keys.npy
    if not args.no_wait:
        ok = wait_for_signal(args.wikipedia_keys, "Q2 Wikipedia 100K", poll_s=120, timeout_hr=24)
        if not ok:
            log.error("Wikipedia signal never arrived; aborting chain")
            return 1
    else:
        log.info("--no-wait; starting immediately without checking Wikipedia signal")

    # Step 1: EXTRACT-1 ConceptNet
    if not args.skip_conceptnet:
        if run_step(
            "backend.kb.conceptnet_ingest",
            ["--n-triples", str(args.conceptnet_n),
             "--output-dir", "data/substrate_state/conceptnet_8m"],
            "EXTRACT-1 ConceptNet 8M",
        ):
            log.info("EXTRACT-1 successful")
        else:
            log.warning("EXTRACT-1 failed; continuing to next step")
    else:
        log.info("EXTRACT-1 skipped (--skip-conceptnet)")

    # Step 2: EXTRACT-2 arXiv
    if not args.skip_arxiv:
        if run_step(
            "backend.kb.arxiv_ingest",
            ["--n-papers", str(args.arxiv_n),
             "--output-dir", "data/substrate_state/arxiv_2m"],
            "EXTRACT-2 arXiv abstracts",
        ):
            log.info("EXTRACT-2 successful")
        else:
            log.warning("EXTRACT-2 failed; continuing")
    else:
        log.info("EXTRACT-2 skipped (--skip-arxiv)")

    # Step 3: EXTRACT-3 Wikidata
    if not args.skip_wikidata:
        if run_step(
            "backend.kb.wikidata_ingest",
            ["--n-triples", str(args.wikidata_n),
             "--output-dir", "data/substrate_state/wikidata_50m"],
            "EXTRACT-3 Wikidata 50M+",
        ):
            log.info("EXTRACT-3 successful")
        else:
            log.warning("EXTRACT-3 failed; continuing")
    else:
        log.info("EXTRACT-3 skipped (--skip-wikidata)")

    # Step 4: EXTRACT-4 PubMed (stretch; healthcare vertical asset)
    if not args.skip_pubmed:
        if run_step(
            "backend.kb.pubmed_ingest",
            ["--n-abstracts", "5000000",
             "--output-dir", "data/substrate_state/pubmed_5m"],
            "EXTRACT-4 PubMed biomedical (stretch)",
        ):
            log.info("EXTRACT-4 successful")
        else:
            log.warning("EXTRACT-4 failed; chain ends")
    else:
        log.info("EXTRACT-4 skipped (--skip-pubmed)")

    log.info("=== extraction_chain done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
