"""One-off backfill: replace placeholder wikidata 'name' with aliases[0] real label.

Root cause: substrate_mapper_to_atom_dict_adapter_v1.humanize_name() previously
ignored aliases and returned the underscore-humanized canonical_name, so
'wikidata_Q182505' became name='wikidata Q182505' even though aliases[0] held
"Bayes' theorem".

Fix (a): adapter now prefers aliases[0] when not a bare Q-id (see
tools/substrate_mapper_to_atom_dict_adapter_v1.py).

Fix (b): this script backfills already-emitted atoms.jsonl in place.

Discipline:
  - Atomic: writes to <path>.new then os.replace (POSIX/Windows-safe rename).
  - Byte-preserving: only 'name' field is rewritten; all other fields kept
    verbatim by re-serializing via json.dumps with same-order dict (Python 3.7+
    preserves insertion order).
  - Idempotent: rows whose name is NOT the 'wikidata Q\\d+' placeholder are
    passed through untouched.
  - Cardinality-preserving: exact row count checked at end.

Run:
  python tools/backfill_atoms_jsonl_wikidata_name_from_aliases_v1.py \
      --path data/substrate_index/math/atoms.jsonl
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"^wikidata Q\d+$")
BARE_QID_RE = re.compile(r"^Q\d+$")


def backfill(path: Path) -> dict:
    """Stream path -> path.new, rewrite placeholder names, atomic rename.

    Returns stats dict.
    """
    tmp = path.with_suffix(path.suffix + ".new")
    stats = {
        "input_rows": 0,
        "changed": 0,
        "unchanged": 0,
        "unfixable_bare_qid_alias": 0,
        "unfixable_no_aliases": 0,
    }
    with path.open("r", encoding="utf-8") as fin, \
         tmp.open("w", encoding="utf-8", newline="\n") as fout:
        for line in fin:
            raw = line.rstrip("\n")
            if not raw:
                # preserve blank lines verbatim (should not occur but be safe)
                fout.write("\n")
                continue
            stats["input_rows"] += 1
            rec = json.loads(raw)
            name = rec.get("name", "")
            if PLACEHOLDER_RE.match(name):
                aliases = rec.get("aliases") or []
                if not aliases:
                    stats["unfixable_no_aliases"] += 1
                    stats["unchanged"] += 1
                else:
                    first = aliases[0]
                    if isinstance(first, str) and first and not BARE_QID_RE.match(first):
                        rec["name"] = first[:120]
                        stats["changed"] += 1
                    else:
                        stats["unfixable_bare_qid_alias"] += 1
                        stats["unchanged"] += 1
            else:
                stats["unchanged"] += 1
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Row-count sanity check
    with tmp.open("r", encoding="utf-8") as f:
        tmp_rows = sum(1 for L in f if L.strip())
    if tmp_rows != stats["input_rows"]:
        tmp.unlink()
        raise RuntimeError(
            f"Row count mismatch: input={stats['input_rows']} tmp={tmp_rows} "
            f"(aborted; original preserved)"
        )

    # Atomic rename
    os.replace(tmp, path)
    return stats


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--path", required=True,
                    help="Path to atoms.jsonl to backfill (in place, atomic).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Only report what would change; do not write.")
    args = ap.parse_args()

    p = Path(args.path)
    if not p.exists():
        print(f"ERROR: {p} does not exist", file=sys.stderr)
        sys.exit(2)

    if args.dry_run:
        # Just tally without writing
        input_rows = changed = unfixable_bare = unfixable_none = 0
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                input_rows += 1
                rec = json.loads(line)
                name = rec.get("name", "")
                if PLACEHOLDER_RE.match(name):
                    aliases = rec.get("aliases") or []
                    if not aliases:
                        unfixable_none += 1
                    else:
                        first = aliases[0]
                        if isinstance(first, str) and first and not BARE_QID_RE.match(first):
                            changed += 1
                        else:
                            unfixable_bare += 1
        print(f"[DRY-RUN] input_rows={input_rows} would_change={changed} "
              f"unfixable_bare_qid_alias={unfixable_bare} "
              f"unfixable_no_aliases={unfixable_none}")
        return

    stats = backfill(p)
    print("=== BACKFILL SUMMARY ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
