"""MES gate hardening (2026-07-29): gate-B robustness across 5 random-init seeds + gate-A
eval-resample robustness, on the two candidate difficulties (distE4/distEv6, distE5/distEv8).
Eval-only, CPU. Reuses experiments.diag_order_critical_comprehension_calib_v1 verbatim.
Writes data/diag_order_critical_comprehension_calib_v1/hardening.json."""
import json
import os
import sys
import time

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import numpy as np

_REPO = "d:/AI/hd-instrument"
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.diag_order_critical_comprehension_calib_v1 as M
import experiments.exp_unified_self_learning_loop_v2 as LOOP2

OUT = os.path.join(_REPO, "data", "diag_order_critical_comprehension_calib_v1", "hardening.json")

VARIANTS = [
    dict(n_distractor_entities=4, n_distractor_events=6),
    dict(n_distractor_entities=5, n_distractor_events=8),
]
RANDOM_INIT_SEEDS = [20260729, 7, 13, 101, 20250101]
EVAL_RESAMPLE_SEEDS = [M.SEED + 555, 424242, 987654]   # 3 independent data draws (gen + scramble)
MES_MAX_LEN = 96
SCORE_SEED = M.SEED   # probe-fit seed, held fixed so only the encoder/data varies


def _build(variant, data_seed):
    rng = np.random.default_rng(data_seed)
    srng = np.random.default_rng(data_seed + 1)
    mc = M.gen_multi_entity_state(rng, **variant)
    M._self_test_constructions([mc], rng)
    train_sents = [it["sent"] for it in mc["train"]]
    eval_sents = [it["sent"] for it in mc["eval"]]
    eval_scr = [LOOP2._scramble_words(it["sent"], srng) for it in mc["eval"]]
    y_train = np.array([it["label"] for it in mc["train"]], dtype=np.int64)
    y_eval = np.array([it["label"] for it in mc["eval"]], dtype=np.int64)
    return mc, train_sents, eval_sents, eval_scr, y_train, y_eval


def main():
    t0 = time.perf_counter()
    results = {}
    for variant in VARIANTS:
        vname = "distE%d_distEv%d" % (variant["n_distractor_entities"], variant["n_distractor_events"])
        print("\n=== VARIANT %s (n_total_entities=%d) ===" % (vname, variant["n_distractor_entities"] + 1), flush=True)
        vres = dict(variant=variant, n_total_entities=variant["n_distractor_entities"] + 1,
                    gate_a_resamples=[], gate_b_seeds=[])

        # ---- Gate A robustness: BGE_SMALL + MiniLM across eval resamples ----
        best_readout_for_gate_b = None   # (model_name_hf, readout) of the strongest gate-A winner on the primary draw
        for ri, dseed in enumerate(EVAL_RESAMPLE_SEEDS):
            mc, tr, ev, evs, ytr, yev = _build(variant, dseed)
            draw = dict(data_seed=dseed, n_eval=len(yev), per_model={})
            best_this_draw = None
            for model_name, short in M.CALIBRATION_MODELS:
                G_tr = M._raw_hf_encode(model_name, tr, max_length=MES_MAX_LEN)
                G_ec = M._raw_hf_encode(model_name, ev, max_length=MES_MAX_LEN)
                G_es = M._raw_hf_encode(model_name, evs, max_length=MES_MAX_LEN)
                per_ro = {}
                for ro in ("MEAN_POOL", "CLS_TOKEN", "LAST_TOKEN"):
                    r = M.score_readout_arm(ro, G_tr[ro], ytr, G_ec[ro], G_es[ro], yev, SCORE_SEED)
                    per_ro[ro] = dict(coherent=r["coherent_acc"], scrambled=r["scrambled_acc"],
                                      margin=r["margin"], pass_gate_a=r["comprehension_specific"])
                    if r["comprehension_specific"] and (best_this_draw is None or r["margin"] > best_this_draw["margin"]):
                        best_this_draw = dict(model=short, model_hf=model_name, readout=ro, margin=r["margin"],
                                              coherent=r["coherent_acc"])
                draw["per_model"][short] = per_ro
            draw["best_gate_a"] = best_this_draw
            vres["gate_a_resamples"].append(draw)
            print("  gate-A draw seed=%d best=%s" % (dseed, best_this_draw), flush=True)
            if ri == 0:
                best_readout_for_gate_b = best_this_draw

        # ---- Gate B robustness: 5 random-init seeds on the PRIMARY draw ----
        # Use the matched readout of the primary-draw gate-A winner (MEAN_POOL for MEAN/CLS).
        mc, tr, ev, evs, ytr, yev = _build(variant, EVAL_RESAMPLE_SEEDS[0])
        if best_readout_for_gate_b is None:
            matched = "MEAN_POOL"
        else:
            matched = "MEAN_POOL" if best_readout_for_gate_b["readout"] in ("MEAN_POOL", "CLS_TOKEN") else "LAST_TOKEN"
        for rs in RANDOM_INIT_SEEDS:
            ri_ro, _ = M._random_init_readouts(M.BASELINE_CKPT, tr, ev, evs, rs, max_len=MES_MAX_LEN)
            G_tr, G_ec, G_es = ri_ro[matched]
            r = M.score_readout_arm(matched + "_RI", G_tr, ytr, G_ec, G_es, yev, SCORE_SEED)
            fails = bool(r["margin"] < M.RANDOM_INIT_MARGIN_FAIL_THRESH)
            vres["gate_b_seeds"].append(dict(seed=rs, readout=matched, margin=r["margin"],
                                             coherent=r["coherent_acc"], scrambled=r["scrambled_acc"],
                                             random_init_fails=fails))
            print("  gate-B seed=%d readout=%s margin=%+.4f fails(<%.2f)=%s"
                  % (rs, matched, r["margin"], M.RANDOM_INIT_MARGIN_FAIL_THRESH, fails), flush=True)

        gb = vres["gate_b_seeds"]
        vres["gate_b_all_fail"] = all(s["random_init_fails"] for s in gb)
        vres["gate_b_n_fail"] = sum(1 for s in gb if s["random_init_fails"])
        vres["gate_b_max_margin"] = max(s["margin"] for s in gb)
        vres["gate_b_mean_margin"] = float(np.mean([s["margin"] for s in gb]))
        ga = [d["best_gate_a"] for d in vres["gate_a_resamples"]]
        vres["gate_a_all_pass"] = all(g is not None and g["margin"] >= M.MARGIN_THRESH
                                      and g["coherent"] >= M.COHERENT_FLOOR for g in ga)
        vres["gate_a_min_margin"] = min((g["margin"] for g in ga if g is not None), default=None)
        vres["bulletproof"] = bool(vres["gate_b_all_fail"] and vres["gate_a_all_pass"])
        results[vname] = vres
        print("  SUMMARY %s: gate_b_all_fail=%s (n_fail=%d/%d max_margin=%+.4f) gate_a_all_pass=%s (min=%s) BULLETPROOF=%s"
              % (vname, vres["gate_b_all_fail"], vres["gate_b_n_fail"], len(gb), vres["gate_b_max_margin"],
                 vres["gate_a_all_pass"], vres["gate_a_min_margin"], vres["bulletproof"]), flush=True)

    # choose FINAL: bulletproof variant with the DEEPEST random-init failure margin (lowest max gate-B
    # margin, i.e. random-init fails hardest) while gate A robustly passes.
    candidates = [(v, r) for v, r in results.items() if r["bulletproof"]]
    if candidates:
        final_v, final_r = min(candidates, key=lambda kv: kv[1]["gate_b_max_margin"])
        final_choice = dict(variant_name=final_v, reason="bulletproof + deepest random-init-failure (lowest gate_b_max_margin)")
    else:
        # none bulletproof: pick the one with lowest gate_b_max_margin among gate-A-passing ones
        gp = [(v, r) for v, r in results.items() if r["gate_a_all_pass"]]
        pool = gp if gp else list(results.items())
        final_v, final_r = min(pool, key=lambda kv: kv[1]["gate_b_max_margin"])
        final_choice = dict(variant_name=final_v, reason="NOT bulletproof; least-fragile gate-A-passing variant")
    final_choice.update(variant=final_r["variant"], n_total_entities=final_r["n_total_entities"],
                        gate_a_min_margin=final_r["gate_a_min_margin"], gate_a_all_pass=final_r["gate_a_all_pass"],
                        gate_b_all_fail=final_r["gate_b_all_fail"], gate_b_n_fail=final_r["gate_b_n_fail"],
                        gate_b_max_margin=final_r["gate_b_max_margin"], gate_b_mean_margin=final_r["gate_b_mean_margin"],
                        bulletproof=final_r["bulletproof"])

    payload = dict(ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   margin_thresh=M.MARGIN_THRESH, coherent_floor=M.COHERENT_FLOOR,
                   random_init_margin_fail_thresh=M.RANDOM_INIT_MARGIN_FAIL_THRESH,
                   random_init_seeds=RANDOM_INIT_SEEDS, eval_resample_seeds=EVAL_RESAMPLE_SEEDS,
                   mes_max_len=MES_MAX_LEN, results=results, final_choice=final_choice,
                   elapsed_s=time.perf_counter() - t0)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, OUT)
    print("\nFINAL_CHOICE:", json.dumps(final_choice, default=str), flush=True)
    print("wrote", OUT, "elapsed %.1fs" % payload["elapsed_s"], flush=True)


if __name__ == "__main__":
    main()
