"""
RECOVERY launcher: the original chain watcher hit deferred-skip placeholders for
EXTRACT-3 and -4 before they were implemented. This launcher waits for arxiv's keys.npy
then fires EXTRACT-3 Wikidata + EXTRACT-4 PubMed sequentially.

Run detached via wmic.
"""
from __future__ import annotations
import logging
import subprocess
import sys
import time
from pathlib import Path


def setup_logging():
    Path("data").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler("data/extraction_chain_remaining.log", mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def wait_for(signal_path: Path, label: str, poll_s: int = 120, timeout_hr: int = 24) -> bool:
    log = logging.getLogger("chain-rem")
    log.info("waiting for %s signal: %s (poll %ds; timeout %dhr)", label, signal_path, poll_s, timeout_hr)
    deadline = time.time() + timeout_hr * 3600
    while time.time() < deadline:
        if signal_path.exists():
            log.info("signal received for %s: %s", label, signal_path)
            return True
        time.sleep(poll_s)
    log.error("TIMEOUT waiting for %s after %d hr", label, timeout_hr)
    return False


def run_step(module: str, args: list, label: str) -> bool:
    log = logging.getLogger("chain-rem")
    cmd = [sys.executable, "-m", module] + args
    log.info("STARTING %s", label)
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
        log.exception("CRASH %s", label)
        return False


def main():
    setup_logging()
    log = logging.getLogger("chain-rem")
    log.info("=== chain-remaining start ===")

    # Wait for arxiv to finish
    arxiv_keys = Path("data/substrate_state/arxiv_2m/keys.npy")
    if not wait_for(arxiv_keys, "EXTRACT-2 arXiv keys.npy", poll_s=120, timeout_hr=24):
        log.error("arxiv never finished; aborting")
        return 1

    # EXTRACT-3 Wikidata — none of the HF candidates actually exist (all 5 tried 404'd
    # 2026-06-09). Document the skip + move on. Real Wikidata ingest needs a direct dump
    # download (30 GB compressed) + custom parser; deferred.
    log.warning("EXTRACT-3 Wikidata SKIPPED: no HF dataset available (5 candidates tried; all 404'd). "
                "Real Wikidata ingest needs direct dump fallback (~30 GB compressed); deferred.")

    # EXTRACT-4 PubMed
    run_step(
        "backend.kb.pubmed_ingest",
        ["--n-abstracts", "5000000",
         "--output-dir", "data/substrate_state/pubmed_5m"],
        "EXTRACT-4 PubMed 5M (stretch; healthcare PP-209 DDI asset)",
    )

    log.info("=== chain-remaining done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
