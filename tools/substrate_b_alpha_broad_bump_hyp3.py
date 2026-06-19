"""Q-a ruling (Skunkworks): bump HYP-3 N to resolve the boundary precisely (150-sample 0.400 == FAIL_LO; full-gold
probe 0.368 -> likely HARD_FAIL). Pre-reg bands SACROSANCT -> don't move the band; measure the recall PRECISELY.

Approach (byte-identical preservation of the 4 already-validity-VET'd benchmarks): keep ALL non-HYP-3 lines from v1
VERBATIM; replace HYP-3 POSITIVES with the FULL deterministic true-3-hop gold (ALL pairs, sorted -> EXACT population
recall, zero sampling noise); keep v1's HYP-3 NEGATIVES verbatim (already validity-VET'd). Write v2. Skunkworks
re-validity-VETs ONLY the new HYP-3 positives (the other 4 benchmarks + HYP-3 negatives unchanged).

Run LOCALLY (nltk). Deterministic. ASCII-only. No LLM.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
V1 = REPO / "experiments" / "data" / "b_alpha_broad_qa_v1.jsonl"
V2 = REPO / "experiments" / "data" / "b_alpha_broad_qa_v2.jsonl"
BKEY, REL, DEPTH = "HYPERNYM_3hop", "HYPERNYM", 3


def main():
    from tools.substrate_b_alpha_broad_qa_builder import load_backbone, true_nhop
    from nltk.corpus import wordnet as wn

    names_in5k, _adj = load_backbone()
    sorted_names = sorted(names_in5k)

    v1_lines = [l for l in V1.read_text(encoding="utf-8").splitlines() if l.strip()]
    v1_items = [json.loads(l) for l in v1_lines]
    # keep verbatim: every line whose benchmark != HYP-3 (byte-identical), PLUS v1's HYP-3 NEGATIVES (verbatim)
    keep_lines = []
    old_hyp3_pos = old_hyp3_neg = 0
    for line, it in zip(v1_lines, v1_items):
        if it["benchmark"] != BKEY:
            keep_lines.append(line)                      # other 4 benchmarks, byte-identical
        elif it["type"] == "negative":
            keep_lines.append(line); old_hyp3_neg += 1   # HYP-3 negatives, byte-identical (already validity-VET'd)
        else:
            old_hyp3_pos += 1                            # HYP-3 positives -> DROP, regenerate full

    # regenerate HYP-3 positives: ALL true exactly-3-hop gold pairs (deterministic, sorted) -> exact recall
    pairs = []
    for name in sorted_names:
        for z in true_nhop(wn, names_in5k, REL, name, DEPTH):
            pairs.append((name, z))
    pairs = sorted(set(pairs))                           # deterministic, dedup
    new_pos_lines = [json.dumps({"id": f"BA-BR-{BKEY}-POS-{i:04d}", "benchmark": BKEY, "rel_type": REL,
                                 "depth": DEPTH, "type": "positive", "x": x, "z": z, "gold_nhop": True})
                     for i, (x, z) in enumerate(pairs)]

    out_lines = keep_lines + new_pos_lines
    V2.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"v1: {len(v1_lines)} lines (HYP-3 had {old_hyp3_pos} pos + {old_hyp3_neg} neg)")
    print(f"v2: {len(out_lines)} lines (HYP-3 now {len(new_pos_lines)} FULL pos + {old_hyp3_neg} neg [verbatim]; other 4 benchmarks byte-identical)")
    print(f"wrote {V2.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
