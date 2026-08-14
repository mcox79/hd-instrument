"""tools/segment_skew_report.py -- surface the reading loop's SOURCE SKEW from any persisted
foundation. 2026-08-14.

The data was always there. `grounding_refusals.jsonl` and `grounding_provenance.jsonl` both carry
a `segment` field, 100% populated, and nothing on disk ever grouped by it -- so "64.5% of every
definitional fact we have ever banked came from one biology textbook" was derivable for 16 days
and never derived (notes/gap_driven_learning_loop_audit_2026-08-13.md sec 5).

`hdlab.reading_grounding_loop.checkpoint` now emits `grounded_by_segment` / `refused_by_segment`
on every growth-curve row, so FUTURE runs carry the skew in their manifest. This tool is the
RETROSPECTIVE half: it applies the same group-by to foundations that were written before the
detector existed.

Read-only. Writes nothing. ASCII-only.

    python tools/segment_skew_report.py                       # every foundation on disk
    python tools/segment_skew_report.py --dir <foundation>    # one
    python tools/segment_skew_report.py --json                # machine-readable
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter
from typing import Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOUNDATION_ROOT = os.path.join(REPO_ROOT, "data", "foundation")


def _read_jsonl(path: str) -> List[dict]:
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            out.append(json.loads(ln))
    return out


def _skew(counter: Counter) -> dict:
    tot = sum(counter.values())
    if tot == 0:
        return {"n": 0, "n_segments": 0, "dominant": None, "dominant_share": 0.0,
                "normalised_entropy": 0.0, "by_segment": {}}
    items = sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0])))
    ent = 0.0
    for _k, v in items:
        p = v / tot
        if p > 0:
            ent -= p * math.log(p)
    max_ent = math.log(len(items)) if len(items) > 1 else 1.0
    return {"n": tot, "n_segments": len(items), "dominant": items[0][0],
            "dominant_share": round(items[0][1] / tot, 4),
            "normalised_entropy": round(ent / max_ent, 4) if max_ent > 0 else 0.0,
            "by_segment": {str(k): v for k, v in items}}


def report_foundation(dir_path: str) -> dict:
    prov = _read_jsonl(os.path.join(dir_path, "grounding_provenance.jsonl"))
    # definitional_facts*.jsonl carry the same `segment` field and are the artifact the
    # "64.5% biology" claim is actually about; fold them in so the tool covers both ledgers.
    for f in sorted(os.listdir(dir_path)) if os.path.isdir(dir_path) else []:
        if f.startswith("definitional_facts") and f.endswith(".jsonl"):
            prov = prov + _read_jsonl(os.path.join(dir_path, f))
    refu = _read_jsonl(os.path.join(dir_path, "grounding_refusals.jsonl"))
    manifest_path = os.path.join(dir_path, "manifest.json")
    manifest: Dict = {}
    if os.path.isfile(manifest_path):
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    # distinct SUBJECTS per segment, not raw rows: a term banked twice must not count twice
    banked_terms: Dict[str, str] = {}
    for row in prov:
        subj = row.get("subject")
        if subj is not None and subj not in banked_terms:
            banked_terms[subj] = row.get("segment")
    return {
        "dir": dir_path,
        "n_provenance_rows": len(prov),
        "n_refusal_rows": len(refu),
        "n_distinct_banked_terms": len(banked_terms),
        "grounded_by_segment_rows": _skew(Counter(r.get("segment") for r in prov)),
        "grounded_by_segment_distinct_terms": _skew(Counter(banked_terms.values())),
        "refused_by_segment": _skew(Counter(r.get("segment") for r in refu)),
        "refusal_reasons": dict(sorted(Counter(r.get("reason") for r in refu).items(),
                                       key=lambda kv: (-kv[1], str(kv[0])))),
        "manifest_cumulative_grounded": manifest.get("growth_curve_all", [{}])[-1].get("cumulative_grounded")
        if manifest.get("growth_curve_all") else None,
        "detector_present_in_manifest": bool(
            manifest.get("growth_curve_all") and
            "grounded_by_segment" in (manifest["growth_curve_all"][-1] or {})),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None, help="one foundation dir (default: all under data/foundation)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    dirs = [args.dir] if args.dir else [
        os.path.join(FOUNDATION_ROOT, d) for d in sorted(os.listdir(FOUNDATION_ROOT))
        if os.path.isdir(os.path.join(FOUNDATION_ROOT, d))]
    reports = [report_foundation(d) for d in dirs]
    reports = [r for r in reports if r["n_provenance_rows"] or r["n_refusal_rows"]]

    if args.json:
        print(json.dumps(reports, indent=2))
        return 0
    for r in reports:
        name = os.path.basename(r["dir"])
        g = r["grounded_by_segment_distinct_terms"]
        f = r["refused_by_segment"]
        print(f"=== {name}")
        print(f"    banked terms {r['n_distinct_banked_terms']:>6}  refusals {r['n_refusal_rows']:>6}"
              f"  detector_in_manifest={r['detector_present_in_manifest']}")
        if g["n"]:
            print(f"    GROUNDED  dominant={g['dominant']!r} share={g['dominant_share']:.3f}"
                  f"  balance(entropy)={g['normalised_entropy']:.3f}  {g['by_segment']}")
        if f["n"]:
            print(f"    REFUSED   dominant={f['dominant']!r} share={f['dominant_share']:.3f}"
                  f"  balance(entropy)={f['normalised_entropy']:.3f}  {f['by_segment']}")
        if r["refusal_reasons"]:
            print(f"    reasons   {r['refusal_reasons']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
