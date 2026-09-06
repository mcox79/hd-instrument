"""exp_board_bridging_v1 -- the BRIDGING-INFERENCE board arm (realizes the meaning channel's first live consumer).

WHY: the reader gained its FIRST live read()-time meaning consumer (owner-DONE bridging_inference,
hdlab/bridging_inference.py) -- it infers the unstated part-whole/instrument link between adjacent sentences
by antecedent selection over the ATL semantic hub (Kintsch construction-integration). But the board has NO
meaning/bridging dimension, so this proven win is board-INVISIBLE ("live != scored"). This arm scores it: the
landed organ's referential-PART antecedent selection (WordNet meronymy) vs the no-inference/most-salient
floors + the shuffled-meaning info-free twin -- reshaped into the board's per_dimension row schema so it folds
into exp_situation_model_qa_v1.run() like the patient/goal_hierarchy/wic/common_noun arms.

REUSES `exp_bridging_selection_v2.eval_type` VERBATIM (the RAW_HUB arm IS the landed organ's computation --
per-item byte-identical, proven by verification/test_bridging_inference_landing.py W2), + delta_ci. MODERN /
register-general lexical gold (WordNet), 19c-clean. Glass-box, NO external LLM (PPMI+SVD hub + WordNet). ASCII.
Run: .venv/Scripts/python.exe experiments/exp_board_bridging_v1.py [--full]
"""
from __future__ import annotations
import os, sys, argparse, json, time
from datetime import datetime, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np
import pickle
import experiments.exp_bridging_selection_v2 as B
from experiments._seed_checkpoint import get_output_dir

ANCHOR = "board_bridging_v1"


def board_bridging_dimension(typ="part_wn", smoke=True, n_boot=2000):
    """A per_dimension board row (schema-matched to board_common_noun_coref_dimension) scoring the LANDED
    bridging_inference organ's referential-PART antecedent selection vs the no-inference/most-salient floors +
    the shuffled-meaning twin. smoke=True caps to 250 pairs (fast, the board default); the full number is the
    standalone --full run. Returns (row, detail)."""
    hub = pickle.load(open(B.HUB_PATH, "rb"))["hub"]
    vocab = list(hub.keys())
    mfnd = B.build_mfnd_vec()
    rng0 = np.random.default_rng(7)
    sal_sample = [vocab[i] for i in rng0.choice(len(vocab), size=min(2000, len(vocab)), replace=False)]
    pooled, npairs, ntest, _mc = B.eval_type(typ, hub, mfnd, vocab, sal_sample, smoke)
    model, rand, sal, twin = pooled["RAW_HUB"], pooled["RANDOM"], pooled["SALIENCE"], pooled["TWIN_HUB"]
    _acc = lambda a: round(float(a.mean()), 4)
    m, f_rand, f_sal, f_twin = _acc(model), _acc(rand), _acc(sal), _acc(twin)
    # strongest no-meaning floor = the higher of the no-inference (random) and most-salient floors
    strong_name, strong_arr, strong_acc = ("most_salient", sal, f_sal) if f_sal >= f_rand else ("no_inference", rand, f_rand)
    ds = B.delta_ci(model, strong_arr, B=n_boot)           # (obs, [lo, hi])
    dt = B.delta_ci(model, twin, B=n_boot)
    row = {
        "n": int(len(model)), "model_acc": m,
        "overlap_floor": strong_acc,
        "floor_accs": {"no_inference": f_rand, "most_salient": f_sal, "shuffled_meaning_twin": f_twin},
        "strongest_floor_name": strong_name, "strongest_floor": strong_acc,
        "twin_acc": f_twin,
        "model_minus_strongest": [ds[0], ds[1][0], ds[1][1]],
        "model_minus_twin": [dt[0], dt[1][0], dt[1][1]],
        "ci_sep_over_strongest": bool(ds[1][0] > 0),
        "ci_sep_over_twin": bool(dt[1][0] > 0),
        "population": "held-out referential-PART bridging (WordNet meronymy); the LANDED hdlab.bridging_inference "
                      "organ (argmax meaning-store relatedness over candidate antecedents) vs the no-inference + "
                      "most-salient floors + the shuffled-MEANING info-free twin. The board had NO meaning/bridging "
                      "dim; this scores the meaning channel's FIRST live read()-time consumer. Register-general "
                      "WordNet gold (19c-clean); smoke-capped for the board (full number = the standalone --full run).",
    }
    detail = {"typ": typ, "smoke": smoke, "n_pairs": npairs, "model_raw_hub": m,
              "no_inference": f_rand, "most_salient": f_sal, "shuffled_meaning_twin": f_twin,
              "model_minus_strongest": [ds[0], ds[1][0], ds[1][1]], "model_minus_twin": [dt[0], dt[1][0], dt[1][1]],
              "note": "the RAW_HUB arm is per-item byte-identical to hdlab.bridging_inference.BridgeInference "
                      "(proven in test_bridging_inference_landing.py W2); this arm realizes the bridging win on the board."}
    return row, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="full pairs (default: smoke=250)")
    a = ap.parse_args()
    t0 = time.time()
    row, detail = board_bridging_dimension(smoke=(not a.full))
    out_dir = get_output_dir(ANCHOR)
    os.makedirs(out_dir, exist_ok=True)
    out = {"anchor": ANCHOR, "row": row, "detail": detail,
           "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print("=" * 96)
    print("BRIDGING board arm  n=%d  (%s)" % (row["n"], "full" if a.full else "smoke"))
    print("  model_acc (landed bridging organ) : %.4f" % (row["model_acc"] or 0))
    print("  strongest_floor (%-13s)   : %.4f" % (row["strongest_floor_name"], row["strongest_floor"] or 0))
    print("  twin (shuffled-meaning, info-free): %.4f" % (row["twin_acc"] or 0))
    print("  model - floor : %s  ci_sep=%s" % (row["model_minus_strongest"], row["ci_sep_over_strongest"]))
    print("  model - twin  : %s  ci_sep=%s" % (row["model_minus_twin"], row["ci_sep_over_twin"]))
    print("=" * 96)
    print("[done] %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
