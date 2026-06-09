"""
Final chain step: wait for BOTH (a) PubMed ingest done AND (b) Wikidata dump fully
downloaded, then run wikidata_dump_ingest.py.

Signals:
  PubMed done:        data/substrate_state/pubmed_5m/keys.npy exists
  Wikidata download:  data/wikidata_dump/latest-truthy.nt.bz2 size matches HTTP HEAD
                      content-length, OR no growth for 5 minutes (download_completed)

Run detached via wmic.
"""
from __future__ import annotations
import logging
import subprocess
import sys
import time
from pathlib import Path


LOG_FILE = Path("data/extraction_chain_wikidata.log")
PUBMED_SIGNAL = Path("data/substrate_state/pubmed_5m/keys.npy")
WIKIDATA_DUMP = Path("data/wikidata_dump/latest-truthy.nt.bz2")
WIKIDATA_URL = "https://dumps.wikimedia.org/wikidatawiki/entities/latest-truthy.nt.bz2"


def setup_logging():
    Path("data").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def wait_for_pubmed(timeout_hr: int = 24) -> bool:
    log = logging.getLogger("wikidata-chain")
    log.info("waiting for PubMed keys.npy: %s (poll 120s; timeout %dhr)", PUBMED_SIGNAL, timeout_hr)
    deadline = time.time() + timeout_hr * 3600
    while time.time() < deadline:
        if PUBMED_SIGNAL.exists():
            log.info("PubMed signal received")
            return True
        time.sleep(120)
    log.error("PubMed signal never arrived after %d hr", timeout_hr)
    return False


def get_expected_dump_size() -> int:
    """Query the Wikidata mirror for the truthy dump's total content-length."""
    try:
        import requests
        r = requests.head(WIKIDATA_URL, allow_redirects=True, timeout=30)
        r.raise_for_status()
        return int(r.headers.get("content-length", 0))
    except Exception as e:
        logging.getLogger("wikidata-chain").warning("HEAD failed: %s", e)
        return 0


def wait_for_dump_complete(timeout_hr: int = 24) -> bool:
    """Wait for the .bz2 file size to (a) match expected content-length OR (b) stop growing
    for >=5 minutes (heuristic for download_completed)."""
    log = logging.getLogger("wikidata-chain")
    if not WIKIDATA_DUMP.exists():
        log.warning("dump file not present yet: %s", WIKIDATA_DUMP)

    expected = get_expected_dump_size()
    log.info("waiting for dump complete; expected size: %d bytes (%.2f GB)",
             expected, expected / (1024 ** 3))

    deadline = time.time() + timeout_hr * 3600
    last_size = -1
    last_change_t = time.time()
    while time.time() < deadline:
        current_size = WIKIDATA_DUMP.stat().st_size if WIKIDATA_DUMP.exists() else 0
        if expected > 0 and current_size >= expected:
            log.info("dump complete: %d / %d bytes", current_size, expected)
            return True
        if current_size != last_size:
            last_change_t = time.time()
            last_size = current_size
            pct = (100 * current_size / expected) if expected > 0 else 0
            log.info("dump growing: %.2f GB (%.2f%%)", current_size / (1024 ** 3), pct)
        else:
            # No growth - has it been stalled long enough to call it complete?
            stall_min = (time.time() - last_change_t) / 60
            if stall_min >= 5:
                log.warning("dump size has not changed for %.0f min; assuming complete at %.2f GB",
                            stall_min, current_size / (1024 ** 3))
                return True
        time.sleep(120)
    log.error("dump did not complete within %d hr", timeout_hr)
    return False


def run_ingest() -> bool:
    log = logging.getLogger("wikidata-chain")
    cmd = [
        sys.executable, "-m", "backend.kb.wikidata_dump_ingest",
        "--dump", str(WIKIDATA_DUMP),
        "--n-triples", "50000000",
        "--output-dir", "data/substrate_state/wikidata_truthy_50m",
    ]
    log.info("STARTING EXTRACT-3 Wikidata truthy ingest: %s", " ".join(cmd))
    t0 = time.time()
    try:
        result = subprocess.run(cmd, check=False, capture_output=False)
        elapsed = time.time() - t0
        if result.returncode == 0:
            log.info("DONE EXTRACT-3 Wikidata truthy in %.0fs (%.1f hr)", elapsed, elapsed / 3600)
            return True
        log.error("FAILED EXTRACT-3 Wikidata truthy exit=%d after %.0fs", result.returncode, elapsed)
        return False
    except Exception:
        log.exception("CRASH EXTRACT-3 Wikidata truthy")
        return False


def main():
    setup_logging()
    log = logging.getLogger("wikidata-chain")
    log.info("=== wikidata-chain start ===")

    if not wait_for_pubmed():
        log.error("PubMed never finished; aborting")
        return 1
    if not wait_for_dump_complete():
        log.error("Wikidata dump never finished; aborting")
        return 1

    run_ingest()
    log.info("=== wikidata-chain done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
