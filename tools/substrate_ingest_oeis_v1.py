"""CELL 5 OEIS ingest per Research USER VISION roadmap (2026-06-13).

Downloads OEIS stripped.gz + names.gz; parses; emits substrate atoms.
~370K integer sequences with rigorous definitions + cross-references.

Pre-reg HARD-PASS:
- >=300K sequences ingested within 1 day (full mode)
- Cross-link >=5K to BATCH 01-16 math atoms (post-ingest analysis)
- Substrate sequence recognition: given first 5 terms, identify OEIS A_id >=80pct top-5

SCALE-SAFETY: default to --smoke (1K sequences) first; --full opt-in.
The 370K ingest substantially grows the math partition (1838 -> ~370K atoms ~ 200x growth);
algebra index + benchmark scaling impact unknown. Smoke validates the ingest pipeline first.

Sources:
- https://oeis.org/stripped.gz  (~10MB; A_id + initial terms)
- https://oeis.org/names.gz     (~30MB; A_id + name/description)
"""
from __future__ import annotations
import sys
import gzip
import re
import time
import urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


OEIS_STRIPPED_URL = "https://oeis.org/stripped.gz"
OEIS_NAMES_URL = "https://oeis.org/names.gz"
DOWNLOAD_DIR = Path("data/external/oeis")


def download_if_missing(url, dest_path):
    """Download url to dest_path if not already present (with User-Agent for OEIS)."""
    if dest_path.exists() and dest_path.stat().st_size > 1024:
        print(f"  already have: {dest_path} ({dest_path.stat().st_size // 1024} KB)")
        return
    print(f"  downloading {url} -> {dest_path}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={
        "User-Agent": "substrate-ingest-cell-5-oeis/1.0 (academic research; per Research USER VISION 2026-06-13)"
    })
    with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as out:
        while True:
            chunk = resp.read(1024 * 64)
            if not chunk:
                break
            out.write(chunk)
    print(f"  done: {dest_path} ({dest_path.stat().st_size // 1024} KB)")


def parse_oeis(stripped_path, names_path, limit=None):
    """Parse OEIS stripped + names into {A_id: {terms, name}}."""
    sequences = {}
    n_seen = 0

    # First pass: stripped (sequence terms)
    print(f"  parsing stripped: {stripped_path}")
    with gzip.open(stripped_path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",", 1)
            if len(parts) != 2:
                continue
            seq_id = parts[0].strip()
            terms_str = parts[1].strip().rstrip(",")
            terms = []
            for t in terms_str.split(","):
                t = t.strip()
                if t and (t.lstrip("-").isdigit()):
                    terms.append(t)  # keep as str to avoid bigint overflow
                if len(terms) >= 30:
                    break
            sequences[seq_id] = {"terms": terms}
            n_seen += 1
            if limit and n_seen >= limit:
                break
    print(f"  parsed {n_seen} sequences from stripped")

    # Second pass: names (descriptions)
    print(f"  parsing names: {names_path}")
    n_named = 0
    name_re = re.compile(r"^(A\d+)\s+(.+)$")
    with gzip.open(names_path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = name_re.match(line)
            if not m:
                continue
            seq_id, name = m.group(1), m.group(2)
            if seq_id in sequences:
                sequences[seq_id]["name"] = name
                n_named += 1
    print(f"  named {n_named} of {len(sequences)} sequences")

    return sequences


def ingest_sequences(ps, sequences, batch_size=500):
    """Ingest sequences into substrate as math::T2/oeis_A* atoms."""
    pre_count = len(ps.all_atoms())
    print(f"  pre-ingest atoms: {pre_count}")

    created = 0
    skipped = 0
    failed = 0
    t0 = time.time()

    items = list(sequences.items())
    for i, (seq_id, data) in enumerate(items):
        atom_id = f"T2/oeis_{seq_id}"
        qid = f"math::{atom_id}"
        if ps.has_atom(qid):
            skipped += 1
            continue
        name = data.get("name", seq_id)[:300]
        terms = data.get("terms", [])
        terms_preview = ", ".join(terms[:10]) + ("..." if len(terms) > 10 else "")
        try:
            atom = Atom(
                id=atom_id,
                name=name,
                corpus=Corpus.MATH,
                tier=Tier.TIER_2_PRIMITIVE,
                description=f"OEIS {seq_id}: {name}. Initial terms: {terms_preview}",
                kind=AtomKind.PRIMITIVE,
                aliases=(seq_id, name.lower().replace(" ", "_")[:100]),
                metadata={
                    "oeis_id": seq_id,
                    "name": name,
                    "initial_terms": terms,
                    "science_algebra_category": "math_foundation::integer_sequences::oeis",
                    "signature_hint": "integer_sequence",
                    "batch_origin": "cell_5_oeis_v1",
                },
                serves_capability=("integer_sequence_recognition", "math_primitive_cross_reference", "OEIS_lookup_substrate"),
            )
            ps.add_atom(atom, source="cell_5_oeis_v1_ingest",
                        note=f"OEIS sequence {seq_id}")
            created += 1
        except Exception as e:
            failed += 1
            if failed <= 5:
                print(f"  FAIL {seq_id}: {str(e)[:80]}")

        if (i + 1) % batch_size == 0:
            elapsed = time.time() - t0
            rate = created / max(elapsed, 0.001)
            print(f"  [{i+1}/{len(items)}] created={created} skipped={skipped} failed={failed} ({rate:.0f}/s)")

    elapsed = time.time() - t0
    post_count = len(ps.all_atoms())
    print(f"\n=== INGEST SUMMARY ===")
    print(f"  elapsed: {elapsed:.1f}s")
    print(f"  pre-ingest: {pre_count} atoms")
    print(f"  post-ingest: {post_count} atoms ({post_count - pre_count:+d})")
    print(f"  created: {created}")
    print(f"  skipped (already present): {skipped}")
    print(f"  failed: {failed}")
    return created, skipped, failed


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="smoke mode: 1000 sequences only (default)")
    ap.add_argument("--full", action="store_true", help="full mode: all ~370K sequences")
    ap.add_argument("--limit", type=int, default=None, help="explicit sequence limit")
    args = ap.parse_args()

    if args.full and args.smoke:
        print("ERROR: --smoke and --full are mutually exclusive")
        sys.exit(2)

    if args.limit is not None:
        limit = args.limit
        mode = f"limit={limit}"
    elif args.full:
        limit = None
        mode = "FULL (~370K sequences)"
    else:
        limit = 1000
        mode = "SMOKE (1000 sequences)"

    print(f"=== CELL 5 OEIS INGEST ({mode}) ===\n")

    # Step 1: download
    print("Step 1: download OEIS data")
    stripped_path = DOWNLOAD_DIR / "stripped.gz"
    names_path = DOWNLOAD_DIR / "names.gz"
    download_if_missing(OEIS_STRIPPED_URL, stripped_path)
    download_if_missing(OEIS_NAMES_URL, names_path)

    # Step 2: parse
    print("\nStep 2: parse OEIS data")
    sequences = parse_oeis(stripped_path, names_path, limit=limit)

    # Step 3: ingest into substrate
    print("\nStep 3: ingest into substrate")
    DATA_ROOT = Path("data/substrate_index")
    ps = PartitionedStore(DATA_ROOT)
    created, skipped, failed = ingest_sequences(ps, sequences)

    # Pre-reg verdict
    print(f"\n=== PRE-REG VERDICT ===")
    if limit is None:
        threshold = 300000
        if created >= threshold:
            print(f"  HARD_PASS: created {created} >= {threshold}")
        else:
            print(f"  HARD_FAIL: created {created} < {threshold}")
    else:
        target = limit
        if created >= target * 0.9:
            print(f"  SMOKE_PASS: created {created} >= 90% of {target}")
        else:
            print(f"  SMOKE_FAIL: created {created} < 90% of {target}")


if __name__ == "__main__":
    main()
