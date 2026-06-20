#!/usr/bin/env python3
"""Reconstruct the NER v3 metrics.json from the GENUINE remote run-log numbers (Orchestrator preserved
them in orchestrator_to_expdev_skunkworks_NER_v3_SUCCEEDED..._2026-06-19.md after the v3 output was
clobbered by the remote `git reset --hard origin/main` reconcile, which restored the committed v1).

The v3 run SUCCEEDED (MIDDLE_BAND); only the on-disk metrics was lost. This rebuilds it MARKER-COMPLETE
(matches exp_ner_4type_headtohead_llm_gpu_v1.py's schema: metrics_source / n_seeds / detail.substrate_4type
/ bench_4type.llm[].variants) so the version-marker discipline recognizes it as the genuine v3, and commits
it so origin=v3 (the next remote reset RESTORES v3 instead of clobbering it). TRANSPARENT: reconstructed_from
provenance recorded; numbers cross-checkable against the run log. ASCII; no GPU re-spend.

Usage: python tools/ner_v3_reconstruct_metrics_from_log_2026-06-19.py [--write]
"""
import argparse
import json
import os
from pathlib import Path

OUT = Path("data/exp_ner_4type_headtohead_llm_gpu_v1/metrics.json")
SRC_NOTE = "notes/orchestrator_to_expdev_skunkworks_NER_v3_SUCCEEDED_but_metrics_CLOBBERED_by_remote_reset_hard_plus_I1_durable_qb1_landed_2026-06-19.md"

# --- GENUINE v3 run-log numbers (Orchestrator-preserved) ---
SUB4_SEEDS = [0.7106, 0.7681, 0.7033, 0.7709, 0.7544]   # 4type per-seed (7/17/23/31/41)
SUB18_SEEDS = [0.7449, 0.7300, 0.7353, 0.7294, 0.7219]  # 18type per-seed
SUB4_MEAN, SUB4_STD = 0.7415, 0.0288
SUB18_MEAN = 0.7323
# Qwen ladder, 2-prompt fairness (the cert-crux): (promptA_f1, promptB_f1) per (model, benchmark)
LADDER = {
    "4type": {"0.5B": (0.1985, 0.1952), "1.5B": (0.0676, 0.4673)},
    "18type": {"0.5B": (0.1522, 0.3131), "1.5B": (0.0753, 0.4882)},
}
BEST_05B_4, BEST_15B_4 = 0.1985, 0.4673   # best-prompted 4type
MARGIN_05B, MARGIN_15B = round(SUB4_MEAN - BEST_05B_4, 4), round(SUB4_MEAN - BEST_15B_4, 4)


def _llm(label, bench):
    a, b = LADDER[bench][label]
    best_f1 = max(a, b); best_prompt = "A" if a >= b else "B"
    return {"label": label, "model": "Qwen/Qwen2.5-%s-Instruct" % label, "best_f1": best_f1,
            "best_prompt": best_prompt, "all_unknown": False,
            "variants": [{"prompt": "A", "f1": a}, {"prompt": "B", "f1": b}]}


def build():
    detail = {
        "substrate_4type": SUB4_MEAN, "substrate_4type_std": SUB4_STD, "substrate_18type": SUB18_MEAN,
        "best_05B_4type": BEST_05B_4, "best_15B_4type": BEST_15B_4,
        "margin_vs_05B": MARGIN_05B, "margin_vs_best15B": MARGIN_15B,
        "seeds_reproduce": SUB4_STD <= 0.03,
    }
    bench4 = {"benchmark": "4type", "substrate_f1_mean": SUB4_MEAN, "substrate_f1_std": SUB4_STD,
              "substrate_f1_seeds": SUB4_SEEDS, "n_test": 150, "llm": [_llm("0.5B", "4type"), _llm("1.5B", "4type")]}
    bench18 = {"benchmark": "18type", "substrate_f1_mean": SUB18_MEAN, "substrate_f1_std": round(float(__import__("statistics").pstdev(SUB18_SEEDS)), 4),
               "substrate_f1_seeds": SUB18_SEEDS, "n_test": 150, "llm": [_llm("0.5B", "18type"), _llm("1.5B", "18type")]}
    msg = ("MIDDLE_BAND: substrate NER 4-type=%.4f (+-%.4f) vs BEST-prompted Qwen-0.5B=%.4f (m %+.4f) / "
           "1.5B=%.4f (m %+.4f); 18-type substrate=%.4f. Honest-scope: beats best-prompted 0.5B+1.5B at "
           "OntoNotes->CoNLL-coarse; 18-type handled at F1=%.4f; NOT beats-all-LLM; Qwen-7B separate follow-up." % (
           SUB4_MEAN, SUB4_STD, BEST_05B_4, MARGIN_05B, BEST_15B_4, MARGIN_15B, SUB18_MEAN, SUB18_MEAN))
    return {
        "anchor_name": "ner_4type_headtohead_llm_gpu_v1", "verdict": "MIDDLE_BAND", "verdict_msg": msg,
        "summary": msg[:200], "elapsed_s": None, "detail": detail,
        "metrics_source": "measured_gpu_substrate_vs_qwen_ladder_promptfair_4type_18type",
        "bench_4type": bench4, "bench_18type": bench18, "n_seeds": 5, "shots": 5,
        "reconstructed_from": ("remote run log (genuine v3 run SUCCEEDED 2026-06-19 ~17:34; on-disk metrics "
                               "CLOBBERED by remote `git reset --hard origin/main` reconcile restoring committed v1). "
                               "Numbers Orchestrator-preserved in %s; cross-checkable against the run log. "
                               "Reconstruction = no GPU re-spend; result fully in hand." % SRC_NOTE),
    }


def marker_ok(m):
    return (m.get("metrics_source") == "measured_gpu_substrate_vs_qwen_ladder_promptfair_4type_18type"
            and m.get("n_seeds") == 5 and m.get("detail", {}).get("substrate_4type") is not None
            and bool(m.get("bench_4type", {}).get("llm")))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true")
    write = ap.parse_args().write
    m = build()
    print("v3-MARKER complete:", marker_ok(m))
    print("verdict:", m["verdict"], "| margin vs 0.5B:", MARGIN_05B, "| margin vs best-1.5B:", MARGIN_15B,
          "(< 0.30 HARD_PASS bar -> MIDDLE_BAND; prompt-fairness lifted crippled 1.5B 0.0676->0.4673)")
    if not marker_ok(m):
        print("REFUSE: reconstruction is not marker-complete."); return 3
    if not write:
        print("\nDRY-RUN. Re-run --write to write %s + (then) commit by explicit path." % OUT); return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".json.tmp.%d" % os.getpid())
    tmp.write_text(json.dumps(m, indent=2), encoding="utf-8")
    os.replace(tmp, OUT)
    print("\nWROTE %s (marker-complete v3). Commit by explicit path so origin=v3 (survives remote reset)." % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
