"""Re-walk data/ and diff against the recorded phase-diagram enumeration.

Provenance for the auditor's 2026-08-17 re-count cited in notes/STATUS_LESSONS.md
("THE PHASE DIAGRAM -- THERE ISN'T ONE") and notes/COMPACTION_HANDOFF_2026-08-17.md 8c(3).
Promoted out of scratch/ per CLAUDE.md: a durable note may not cite a wiped directory.

Run from the repo root:  .venv/Scripts/python.exe tools/phase_diagram_recovery/verify_metrics_enumeration.py

Reports the current directory / metrics.json counts, and the set difference against
data/_phase_diag_metrics_list.txt (the enumeration the phase-diagram recovery was built on),
BOTH WAYS -- a count match alone would not prove the same files were seen.
"""

import os

BS = chr(92)
DATA = "data"
RECORDED = "data/_phase_diag_metrics_list.txt"


def walk():
    """Return (n_subdirs_visited, set_of_metrics_paths) skipping data/foundation."""
    ndirs = 0
    found = set()
    for root, dirs, files in os.walk(DATA):
        norm = root.replace(BS, "/")
        dirs[:] = [d for d in dirs if (norm + "/" + d) != "data/foundation"]
        ndirs += len(dirs)
        if "metrics.json" in files:
            found.add((norm + "/metrics.json").lower())
    return ndirs, found


def main() -> None:
    ndirs, cur = walk()
    print("subdirectories visited (data/foundation skipped):", ndirs)
    print("metrics.json files found:", len(cur))

    if not os.path.exists(RECORDED):
        print("no recorded enumeration at", RECORDED, "-- nothing to diff against")
        return

    old = set()
    for line in open(RECORDED, encoding="utf-8", errors="replace"):
        s = line.strip().replace(BS, "/")
        if s:
            old.add(s.lower())
    print("recorded enumeration:", len(old))

    new = sorted(cur - old)
    gone = sorted(old - cur)
    print("NEW since the recorded walk:", len(new))
    for p in new:
        print("  +", p)
    print("MISSING vs the recorded walk:", len(gone))
    for p in gone:
        print("  -", p)


if __name__ == "__main__":
    main()
