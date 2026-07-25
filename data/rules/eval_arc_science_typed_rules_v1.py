"""eval_arc_science_typed_rules_v1 -- HONEST coverage + selectivity self-assessment of the authored
typed-rule base, using the REAL composed reasoner (hdlab/reasoner.py) end-to-end over the REAL
SemanticHDEncoder (GloVe+WordNet). This is the exact wiring exp_dev will use, so the numbers are the
real derive-coverage% + selectivity, not a proxy.

Run: python data/rules/eval_arc_science_typed_rules_v1.py --n 80
"""
from __future__ import annotations
import os, sys, json, argparse
import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.reasoner import DerivationReasoner, evaluate, _print_traces
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=80)
    ap.add_argument("--seed", type=int, default=20260725)
    ap.add_argument("--rules", type=str,
                    default=os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json"))
    args = ap.parse_args()

    rows = json.load(open(args.rules, encoding="utf-8"))["rules"]
    print(f"[eval] loaded {len(rows)} authored rules from {args.rules}", flush=True)

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon
    base = SemanticHDEncoder()
    pol = PolarityLexicon()
    wn = base._wn
    print("[eval] encoder ready; building graph over authored rules ...", flush=True)
    reasoner = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, rows=rows, seed=args.seed)
    print(f"[eval] graph: n_nodes={reasoner.g['n_nodes']} n_typed_edges={reasoner.g['n_typed_edges']} "
          f"max_typed_deg={reasoner.g['max_typed_node_degree']} "
          f"(label={reasoner.g['max_degree_node_label']}) n_merges={reasoner.g['n_merges']} "
          f"per_relation={reasoner.per_relation}", flush=True)

    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    rng = np.random.default_rng(args.seed)
    idx = sorted(rng.permutation(len(all_q))[:args.n].tolist())
    qs = [all_q[i] for i in idx]
    print(f"[eval] evaluating {len(qs)} ARC-Challenge questions ...", flush=True)

    out_dir = os.path.join(_REPO, "data", "rules", "_eval_scratch")
    report = evaluate(reasoner, qs, out_dir)
    cs = report["covered_subset"]

    print("\n===== SELF-ASSESSMENT (real reasoner, authored rules) =====", flush=True)
    print(f"n_questions              = {report['n_questions']}", flush=True)
    print(f"chance                   = {report['chance']}", flush=True)
    print(f"coverage_fraction        = {report['coverage_fraction']}  "
          f"(>=1 candidate derivable; n_covered={report['n_covered']})", flush=True)
    print(f"correct_reachable_frac   = {report['correct_reachable_fraction']}  "
          f"(gold answer derivable; n={report['n_correct_reachable']})", flush=True)
    print(f"whole_set typed_acc      = {report['typed_whole_set_acc']}  "
          f"baseline={report['baseline_whole_set_acc']}", flush=True)
    print(f"COVERED-SUBSET n={cs['n']}:", flush=True)
    print(f"   typed_acc             = {cs['typed_acc']}", flush=True)
    print(f"   baseline_acc          = {cs['baseline_acc']}   (typed-baseline={cs['typed_minus_baseline']:+})", flush=True)
    print(f"   shuffle_direction_acc = {cs['shuffle_direction_acc']} (typed-shuffle={cs['typed_minus_shuffle']:+})", flush=True)
    print(f"   untyped_null_acc      = {cs['untyped_null_acc']}   (typed-null={cs['typed_minus_untyped_null']:+})", flush=True)

    # SELECTIVITY: among covered questions, is the GOLD chain present while distractor chains are NOT?
    per_q = report["per_q"]
    n_gold_deriv = 0
    n_gold_deriv_and_selective = 0
    wrong_deriv_hits = 0
    wrong_deriv_total = 0
    for r in per_q:
        ci = r["correct_index"]
        pcs = r["typed"]["per_choice"]
        if ci < len(pcs) and pcs[ci]["derivable"]:
            n_gold_deriv += 1
            others_deriv = [c for c in pcs if c["choice_index"] != ci and c["derivable"]]
            if not others_deriv:
                n_gold_deriv_and_selective += 1
        for c in pcs:
            if c["choice_index"] == ci:
                continue
            wrong_deriv_total += 1
            if c["derivable"]:
                wrong_deriv_hits += 1
    sel = (n_gold_deriv_and_selective / n_gold_deriv) if n_gold_deriv else 0.0
    print(f"\nSELECTIVITY:", flush=True)
    print(f"   gold-derivable Qs                 = {n_gold_deriv}", flush=True)
    print(f"   of those, ONLY gold derivable     = {n_gold_deriv_and_selective}  "
          f"(clean-selective frac = {sel:.3f})", flush=True)
    print(f"   distractor derive-rate            = {wrong_deriv_hits}/{wrong_deriv_total} = "
          f"{(wrong_deriv_hits/wrong_deriv_total if wrong_deriv_total else 0):.3f}", flush=True)

    _print_traces(report["traces"])

    summary = {
        "n_rules": len(rows), "n_questions": report["n_questions"],
        "coverage_fraction": report["coverage_fraction"], "n_covered": report["n_covered"],
        "correct_reachable_fraction": report["correct_reachable_fraction"],
        "covered_subset": cs, "chance": report["chance"],
        "whole_set": {"typed": report["typed_whole_set_acc"], "baseline": report["baseline_whole_set_acc"]},
        "selectivity": {"gold_derivable": n_gold_deriv, "only_gold_derivable": n_gold_deriv_and_selective,
                        "clean_selective_frac": round(sel, 4),
                        "distractor_derive_rate": round(wrong_deriv_hits / wrong_deriv_total, 4) if wrong_deriv_total else 0.0},
        "graph": {"n_nodes": reasoner.g["n_nodes"], "n_typed_edges": reasoner.g["n_typed_edges"],
                  "max_typed_node_degree": reasoner.g["max_typed_node_degree"],
                  "max_degree_node_label": reasoner.g["max_degree_node_label"],
                  "n_merges": reasoner.g["n_merges"]},
    }
    with open(os.path.join(_REPO, "data", "rules", "eval_summary_v1.json"), "w", encoding="utf-8", newline="") as f:
        json.dump(summary, f, indent=2)
    print("\n[eval] wrote data/rules/eval_summary_v1.json", flush=True)


if __name__ == "__main__":
    main()
