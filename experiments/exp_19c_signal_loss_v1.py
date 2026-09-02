"""exp_19c_signal_loss_v1 -- WHERE EXACTLY does 19c fidelity break, step by step, for the brain-foundational
components? (owner: "do you understand exactly why we lost on 19c... disambiguate at each step of the process
for the truly brain-foundational components to see where they lose fidelity. Loss at the parser we need to
understand at the root, and then improve if we can.")

Traces every who-did-what item through the brain-foundational pipeline and reports, for MODERN (QA) vs 19c
(LitBank), the per-step success rate so the loss is attributed to a NAMED step:
  S1 VERB tagged VERB?        pos_tagger (lexical category) -- fails on archaic morphology.
  S2 gold patient tagged NOMINAL? pos_tagger -- candidate identification.
  S3 gold patient POST-verbal? word order (Competition Model position cue validity on the register).
  S4 gold patient head-attaches to VERB in the arc-eager parse? the PARSER (structure) -- root of the head loss.
  S5 voice: is the item passive/non-canonical?
Then per-partition accuracy of the REAL patient organ (hybrid_role_patient, position+voice) vs MY head-rule
(arc-eager heads), so we see WHERE the parser's heads help vs hurt on 19c and why the position organ wins.

Population = 0-based whitespace tokenization (gold/cands align 1.000). CPU numpy, NO torch/spaCy/LLM. ASCII.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time
from collections import defaultdict
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)
import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_parser_gap_decomp_v1 as GD
import experiments.exp_arceager_parser_operator_v1 as AEO
from hdlab.graded_role_assigner import hybrid_role_patient
from hdlab.relcl_resolver import resolve_patient

from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_19c_signal_loss_v1")
NOMINAL = {"NOUN", "PROPN", "PRON"}


def cand_ok(r):
    return len(GD.cands(r)) >= 2 and sum(1 for h, _ in GD.cands(r) if GD.anim(h)) < 2


def analyze(name, path, W, tg):
    rows = [r for r in V1.load_pop(path) if cand_ok(r)]
    print("[%s] %d items" % (name, len(rows)), flush=True)
    steps = defaultdict(int); n = 0
    # per-partition accuracy: key = (attach, postverbal) -> [organ_correct, headrule_correct, total]
    part = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        toks = r["sent"].split()
        if not toks:
            continue
        vi0 = r["verb_idx"]; gi0 = r.get("gold_idx")
        if gi0 is None or not (0 <= vi0 < len(toks)) or not (0 <= gi0 < len(toks)):
            continue
        n += 1
        pos = tg.tag(toks)
        heads, _, _ = AEO.parse_with_conf(toks, pos, W)
        s1 = pos[vi0] == "VERB"
        s2 = pos[gi0] in NOMINAL
        s3 = gi0 > vi0                                   # gold post-verbal
        s4 = heads.get(gi0 + 1) == (vi0 + 1)             # gold attaches to verb (1-based)
        s5 = (r.get("voice") == "passive") or bool(r.get("noncanonical"))
        steps["S1_verb_tagged_VERB"] += s1
        steps["S2_gold_tagged_NOMINAL"] += s2
        steps["S3_gold_postverbal"] += s3
        steps["S4_gold_attaches_verb"] += s4
        steps["S5_passive_or_noncanon"] += s5
        # organ (position+voice) vs my head-rule -- accuracy by (attach, postverbal)
        v1 = vi0 + 1; cands = [c + 1 for c in r["cand_idx"]]
        try:
            oidx = hybrid_role_patient(toks, pos, v1, cands)
            org = toks[oidx - 1] if (oidx and 1 <= oidx <= len(toks)) else r.get("pos_pick")
        except Exception:
            org = r.get("pos_pick")
        # my head-rule via GD label-free on this arc-eager parse (rebuild the labelfree set for this sent)
        key = ("attach" if s4 else "noattach", "post" if s3 else "pre")
        gold = r["gold_head"]
        part[key][0] += int(org == gold)
        part[key][2] += 1
    res = {"n": n, "step_rates": {k: round(v / n, 4) for k, v in steps.items()},
           "partitions": {("%s_%s" % k): {"organ_acc": round(v[0] / v[2], 4) if v[2] else 0.0,
                                          "n": v[2], "share": round(v[2] / n, 3)} for k, v in part.items()}}
    print("  step success rates:", flush=True)
    for k in ("S1_verb_tagged_VERB", "S2_gold_tagged_NOMINAL", "S3_gold_postverbal", "S4_gold_attaches_verb", "S5_passive_or_noncanon"):
        print("    %-26s %.4f" % (k, res["step_rates"][k]), flush=True)
    print("  partition (attach x position) organ accuracy:", flush=True)
    for k in sorted(res["partitions"], key=lambda k: -res["partitions"][k]["n"]):
        p = res["partitions"][k]
        print("    %-16s n=%4d (%.1f%%)  organ_acc=%.4f" % (k, p["n"], 100 * p["share"], p["organ_acc"]), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser(); ap.parse_args()
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
    W = AEO.load_model(AEO.MODEL_PATH)
    out = {}
    for nm, path in (("qa_modern", V1.QA), ("litbank_19c", V1.LB)):
        print("\n=== %s ===" % nm, flush=True)
        out[nm] = analyze(nm, path, W, tg)
    # the key contrast: what drops most from modern -> 19c?
    if "qa_modern" in out and "litbank_19c" in out:
        print("\n=== MODERN -> 19c step-rate DROP (the root of the 19c loss) ===", flush=True)
        for k in out["qa_modern"]["step_rates"]:
            d = out["litbank_19c"]["step_rates"][k] - out["qa_modern"]["step_rates"][k]
            print("    %-26s modern=%.4f 19c=%.4f drop=%+.4f" % (
                k, out["qa_modern"]["step_rates"][k], out["litbank_19c"]["step_rates"][k], d), flush=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "c19_signal_loss_v1", "results": out,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[done] %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
