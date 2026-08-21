"""WHAT DID THIS CELL SAVE THAT I COULD RE-ANALYSE? -- one command, before you conclude "re-run".

WHY THIS EXISTS. On 2026-08-21 the choice "re-analyse or re-run" came up four times in one night.
THREE TIMES THE ANSWER WAS ALREADY ON DISK, and finding it meant hand-walking a metrics.json each
time:
  - `exp_n11c...`  -> `per_unit[0].shared_feature.per_triple` held the 29 scored triples, which
                      OVERTURNED a claim already written into three planning documents.
  - `exp_capacity_ceiling_near_far_v1` -> `curve_by_dimension` held the whole d-sweep inline.
  - `exp_predictive_coding_write_gate_dissociation_v1` -> `units.jsonl` held per-pair scores, which
                      REFUTED my own suspicion and reversed a board recommendation an hour old.
TWICE IN ONE NIGHT I ASKED THE OWNER TO AUTHORISE PRODUCING A NUMBER THAT WAS ALREADY SAVED. This
tool exists so that check costs one command instead of a hand-walk, because a check that is
expensive is a check that gets skipped.

MEASURED BASE RATE (full enumeration of all 7,905 `data/exp_*` dirs, nothing sampled):
about 31% of cells are re-analysable -- 2,012 via a data-extension sibling file, 435 more via a
population living inside metrics.json itself. The other ~68% kept only their conclusions.
See notes/ONE_THIRD_OF_THE_ARCHIVE_IS_RE_ANALYSABLE_*.md.

THRESHOLD NOTE, AND IT IS A REAL CALIBRATION: that 31% used ">=50 entries" and therefore UNDERCOUNTS.
`n11c`'s `per_triple` -- the population that mattered most tonight -- holds TWENTY-NINE. This tool
defaults to 10 for exactly that reason. A small population is still a population.

Usage:
    python tools/what_did_this_cell_save.py exp_n11c_shared_feature_lexical_similarity_v1
    python tools/what_did_this_cell_save.py <cell> --min 5
    python tools/what_did_this_cell_save.py --self-test
"""
import argparse
import json
import os
import sys

BOILERPLATE = {"metrics.json", "_start_marker.json", "_heartbeat.jsonl", "_pid", "_pid.txt",
               "_done_marker.json"}
DATA_EXT = {".json", ".jsonl", ".npy", ".npz", ".csv", ".tsv", ".parquet", ".pkl", ".pt", ".duckdb"}
MAX_DEPTH = 8


def load_any(path):
    """Read a file that may be JSON *or* JSONL, and say which. Returns (obj, note).

    THIS EXISTS BECAUSE MY OWN READER WAS THE DEFECT TWICE IN ONE NIGHT (2026-08-21):
      - `_survivors_for_handcheck.json` was recorded in a committed note as "0 parseable rows".
        It parses perfectly. I had read a JSON dict line-by-line as JSONL.
      - An earlier scan read only the first 2 MB of sibling JSONs, declared them unparseable, and
        produced a "96.5% of cells saved nothing" claim that had to be voided.
    Both times "unparseable" was a statement about the reader, not the file. So: try both formats,
    and if both fail say UNKNOWN rather than absent -- an absence claim needs an enumeration.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), "json"
    except Exception:                                     # noqa: BLE001 -- fall through to JSONL
        pass
    try:
        rows = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        if rows:
            return rows, "jsonl (%d lines)" % len(rows)
    except Exception as exc:                              # noqa: BLE001
        return None, "UNREADABLE as json or jsonl (%s) -- UNKNOWN, not absent" % type(exc).__name__
    return None, "empty"


def sample_tell(obj):
    """Is this file a SAMPLE of a population it did not keep? Returns a note or None.

    The 2026-08-21 case that motivates it, exactly: `{"n_survivors": 1414, "sample": [100 rows]}`.
    That file looks like saved data and IS saved data -- but it cannot answer a question about the
    other 1,314. Deliberately narrow: an integer field whose value EXCEEDS the longest list in the
    same dict by more than 2x. A file that kept everything has count == length and stays quiet.
    """
    if not isinstance(obj, dict):
        return None
    longest = max([len(v) for v in obj.values() if isinstance(v, list)] or [0])
    if not longest:
        return None
    for k, v in obj.items():
        if isinstance(v, int) and not isinstance(v, bool) and v > 2 * longest:
            return (f"SAMPLE, NOT THE POPULATION: '{k}' = {v:,} but the longest list here holds "
                    f"{longest:,}. It cannot answer a question about the other {v - longest:,}.")
    return None


def _populations(obj, min_entries, path="", depth=0, out=None):
    """Every path in the JSON holding a list OR dict of >= min_entries.

    Dicts count because populations are routinely stored KEYED BY ITEM -- `COMPOSITION_PER_ARM`,
    `feature_provenance`. Counting only lists undercounted the archive census by 35%.
    """
    if out is None:
        out = []
    if depth > MAX_DEPTH:
        return out
    if isinstance(obj, list):
        if len(obj) >= min_entries:
            out.append((path or "<root>", "list", len(obj)))
        for i, v in enumerate(obj[:3]):          # first few only; sibling entries repeat shape
            _populations(v, min_entries, f"{path}[{i}]", depth + 1, out)
    elif isinstance(obj, dict):
        if len(obj) >= min_entries:
            out.append((path or "<root>", "dict", len(obj)))
        for k, v in obj.items():
            _populations(v, min_entries, f"{path}.{k}" if path else str(k), depth + 1, out)
    return out


def inspect(cell, min_entries=10, data_root="data"):
    d = cell if os.path.isdir(cell) else os.path.join(data_root, cell)
    if not os.path.isdir(d):
        print(f"NO SUCH CELL: {d}\n  (that is not evidence it never ran -- check the name against "
              f"`python tools/experiment_index.py query \"<kw>\"`)")
        return 2

    print("=" * 78)
    print(f"WHAT {os.path.basename(d)} SAVED")
    print("=" * 78)

    files = sorted(f for f in os.listdir(d) if f not in BOILERPLATE)
    data_files = [f for f in files if os.path.splitext(f)[1].lower() in DATA_EXT]
    if files:
        print("\n--- sibling files ---")
        for f in files:
            size = os.path.getsize(os.path.join(d, f))
            tag = "  <-- DATA" if f in data_files else ""
            print(f"  {f:<52}{size:>12,} B{tag}")
            # OPEN IT. Listing a filename is not the same as knowing what is in it -- on 2026-08-21
            # a file listed as data turned out to hold 100 rows of a 1,414-row population, and that
            # distinction is the whole re-analysable question.
            if f not in data_files or size > 200_000_000:
                continue
            obj, note = load_any(os.path.join(d, f))
            if obj is None:
                print(f"      {note}")
                continue
            for p2, kind, n2 in sorted(_populations(obj, min_entries), key=lambda r: -r[2])[:4]:
                print(f"      {n2:>7,}  {kind:<5} {p2}   [{note}]")
            tell = sample_tell(obj)
            if tell:
                print(f"      !! {tell}")
    else:
        print("\n--- sibling files ---\n  (none -- metrics.json only)")

    pops, note = [], ""
    mp = os.path.join(d, "metrics.json")
    if os.path.exists(mp):
        try:
            with open(mp, encoding="utf-8") as fh:
                pops = _populations(json.load(fh), min_entries)
        except Exception as exc:                  # noqa: BLE001 -- report, never crash the caller
            note = f"  metrics.json did not parse ({type(exc).__name__}) -- UNKNOWN, not absent"
    else:
        note = "  no metrics.json"

    print(f"\n--- populations INSIDE metrics.json (>= {min_entries} entries) ---")
    if note:
        print(note)
    elif pops:
        for path, kind, n in sorted(pops, key=lambda r: -r[2])[:25]:
            print(f"  {n:>7,}  {kind:<5} {path}")
        if len(pops) > 25:
            print(f"  ... and {len(pops) - 25} more")
        # HONEST LIMIT, stated here rather than left for the reader to discover: a config block with
        # many keys (`detail`, `<root>`) is STRUCTURE, not a scored population, and is listed too.
        # Not filtered, because the values-are-homogeneous test that would separate them is exactly
        # the kind of clever heuristic that has produced false confidence here before. Largest-first
        # ordering does the useful work: real populations sort to the top.
        print("  NOTE: rows are sorted largest-first. Config blocks with many keys (`detail`,")
        print("        `<root>`) are STRUCTURE, not scored data -- read the path, not just the count.")
    else:
        print("  (none -- summaries only)")

    print()
    if data_files or pops:
        print(">>> RE-ANALYSABLE. Open it before concluding you must re-run.")
    else:
        print(">>> SUMMARY-ONLY. A new question about this cell needs a RE-RUN.")
        print("    (~68% of cells are in this state -- it is the normal case, not a defect report.)")
    return 0


def _self_test():
    """Both directions. A detector that only ever says yes is not a detector."""
    import tempfile
    ok = True

    # KNOWN-PRESENT, and deliberately the 29-entry case that a >=50 threshold would MISS.
    cell = "exp_n11c_shared_feature_lexical_similarity_v1"
    mp = os.path.join("data", cell, "metrics.json")
    if os.path.exists(mp):
        with open(mp, encoding="utf-8") as fh:
            pops = _populations(json.load(fh), 10)
        hit = [p for p in pops if p[0].endswith("per_triple")]
        if hit and hit[0][2] == 29:
            print(f"[self-test] PASS known-present: found per_triple with {hit[0][2]} entries "
                  "(a >=50 threshold would have MISSED this one)")
        else:
            print(f"[self-test] FAIL known-present: per_triple not found at 29; got {hit}")
            ok = False
        if not _populations(json.load(open(mp, encoding="utf-8")), 100000):
            print("[self-test] PASS an absurd threshold finds nothing (the walker is not "
                  "hallucinating populations)")
        else:
            print("[self-test] FAIL: found a population at threshold 100000")
            ok = False
    else:
        print(f"[self-test] SKIP known-present: {mp} absent")

    # KNOWN-ABSENT: a summary-only fixture must be reported as such, or the tool is cry-wolf.
    with tempfile.TemporaryDirectory() as td:
        fx = os.path.join(td, "exp_fixture_summary_only")
        os.makedirs(fx)
        with open(os.path.join(fx, "metrics.json"), "w", encoding="utf-8") as fh:
            json.dump({"verdict": "HARD_PASS", "auc": 0.42, "n": 240}, fh)
        if not _populations(json.load(open(os.path.join(fx, "metrics.json"), encoding="utf-8")), 10):
            print("[self-test] PASS known-absent: a summary-only fixture reports NO population")
        else:
            print("[self-test] FAIL known-absent: found a population in a summary-only fixture")
            ok = False

    # THE SAMPLE TELL, both directions. The real 2026-08-21 case must fire; a file that kept
    # everything must stay silent, or the flag is cry-wolf and gets ignored.
    if sample_tell({"n_survivors": 1414, "sample": [0] * 100}):
        print("[self-test] PASS sample-tell fires on {n_survivors:1414, sample:[100]}")
    else:
        print("[self-test] FAIL sample-tell did NOT fire on the real 2026-08-21 case")
        ok = False
    if sample_tell({"n_rows": 4015, "rows": [0] * 4015}) is None:
        print("[self-test] PASS sample-tell stays SILENT when the file kept everything")
    else:
        print("[self-test] FAIL sample-tell fired on a complete file (cry-wolf)")
        ok = False

    # load_any must read BOTH formats -- reading JSON as JSONL is what produced a false
    # "0 parseable rows" in a committed note.
    with tempfile.TemporaryDirectory() as td:
        j = os.path.join(td, "a.json")
        with open(j, "w", encoding="utf-8") as fh:
            json.dump({"n_survivors": 7, "sample": [1, 2]}, fh)
        l = os.path.join(td, "b.jsonl")
        with open(l, "w", encoding="utf-8") as fh:
            fh.write('{"a":1}\n{"a":2}\n')
        oj, nj = load_any(j)
        ol, nl = load_any(l)
        if isinstance(oj, dict) and nj == "json" and isinstance(ol, list) and len(ol) == 2:
            print("[self-test] PASS load_any reads JSON as JSON and JSONL as JSONL")
        else:
            print(f"[self-test] FAIL load_any: {nj} / {nl}")
            ok = False
        bad = os.path.join(td, "c.json")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("{not json at all")
        if load_any(bad)[0] is None and "UNKNOWN" in load_any(bad)[1]:
            print("[self-test] PASS a genuinely unreadable file says UNKNOWN, not absent")
        else:
            print("[self-test] FAIL unreadable file did not report UNKNOWN")
            ok = False

    # DICTS MUST COUNT -- counting only lists undercounted the archive census by 35%.
    if _populations({"by_word": {str(i): i for i in range(12)}}, 10):
        print("[self-test] PASS a dict keyed by item counts as a population")
    else:
        print("[self-test] FAIL: dict-keyed population not detected")
        ok = False

    print("[self-test] " + ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cell", nargs="?", help="cell name or path under data/")
    ap.add_argument("--min", type=int, default=10,
                    help="minimum entries to call something a population (default 10; the archive "
                         "census used 50 and MISSED n11c's 29-entry per_triple)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return _self_test()
    if not a.cell:
        ap.error("give a cell name, or --self-test")
    return inspect(a.cell, a.min)


if __name__ == "__main__":
    sys.exit(main())
