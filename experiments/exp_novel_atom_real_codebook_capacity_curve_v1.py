"""Novel-atom real-codebook D_FEAT CAPACITY CURVE -- the VET-named revival of atom 29381 (v1).

THE VET (atom 29381, math::MEASURED_MECHANISM_novel_atom_real_codebook_generalization_v1_RETIERED):
v1 (exp_novel_atom_real_codebook_generalization_v1, commit ec8232880) showed composition of REAL
induced novel-atom codes GENUINELY SURVIVES (codebook_derived=0.314 = 52x random_code=0.006, real
dense-HRR FFT bind/bundle/unbind/cleanup mechanics, ceiling_check=1.000) -- but the specific ridge-
INDUCTION map did NOT beat naive nearest-neighbor prototype matching at D_FEAT=256 (margin -0.026,
consistently negative all 3 seeds). An INDEPENDENT RECOMPUTE during the VET showed this is D_FEAT-
CAPACITY-CONTINGENT, not a settled bound: the cheat-case (full, non-partial held-out features) ridge-
recovered cosine-to-true rose from 0.557 at D_FEAT=256 to 0.671 at D_FEAT=1024 (4x capacity). The VET
named the decisive revival: re-run the SAME pipeline at higher D_FEAT (headline=1024) plus a capacity
curve (256/512/1024) and ask whether the codebook_derived-vs-memorize_prototype margin FLIPS positive.

THIS CELL: reuses exp_novel_atom_real_codebook_generalization_v1's REAL text8 PPMI/SVD codebook world-
builders, ridge-induction map, real dense-HRR decode pipeline, and all 4 arms UNCHANGED (import, not
reimplementation -- same code path as the credited/VET'd cell). The ONLY new axis is D_FEAT itself:
build_real_world() (text8 tokenize/vocab/cooc/ppmi/SVD-codebook), the held/seen/candidate split, the
unitary-HRR role codes, and the ceiling_check mechanics sanity are computed ONCE (D_FEAT-independent)
and shared across all three D_FEAT curve points -- only R_feat / feat_full_all / the ridge induction map
W are rebuilt per D_FEAT point (D_FEAT changes the OBSERVABLE FEATURE dimension only; N=1024 HRR dim,
RIDGE_ALPHA=10.0, seeds, corpus, role codes, and candidate table are held IDENTICAL across the curve --
ONE variable differs per sweep point, per the experiment-design gate).

ARMS (identical definitions to v1; see exp_novel_atom_real_codebook_generalization_v1 docstring):
  codebook_derived   : ridge induction map W (fit on SEEN words only) applied to a fresh partial/noisy
                       real feature draw of the held-out word [genuine].
  handed_ceiling     : the held-out word's TRUE ppmi_svd code, handed directly [ceiling-only control].
  random_code        : independent unit-norm random Gaussian vector [format-only content-control].
  memorize_prototype : 1-NN over SEEN words' FULL features vs the held-out word's PARTIAL feature draw
                       [naive-similarity baseline -- carries REAL non-zero signal on real data, see v1's
                       calibration note; this is the comparison that matters for this cell].

CAPACITY-CURVE QUESTION (make-or-break for this revival): does codebook_derived - memorize_prototype
(the induction-vs-naive-NN margin) FLIP from negative (v1's D_FEAT=256 result: -0.026) to positive as
D_FEAT rises to 512 then 1024? Both curves (codebook_derived accuracy AND memorize_prototype accuracy
vs D_FEAT) are reported, because the naive-NN baseline ALSO uses feat_full_all (D_FEAT-dependent) for
its distance computation -- if both curves rise together with no narrowing/crossing gap, there is no
flip and the cell reports that honestly (similarity-placement is D_FEAT-invariant relative ceiling).
The cheat-case ridge-recovered cosine-to-true (full, non-partial held-out features, matching the VET's
independent-recompute diagnostic that produced 0.557->0.671) is also tracked per D_FEAT point.

Pre-reg: preregs/2026-07-20_novel_atom_real_codebook_capacity_curve_v1.md

CELL-TEMPLATE MANDATORY: arms_differ hash-test per D_FEAT point; tmp_replace atomic metrics; except
SystemExit: raise BEFORE except Exception (no BaseException); crlb_n/a declared; baseline_in_band
(ceiling-check mechanics sanity, shared across D_FEAT points, computed once); discriminator survives
scale (smoke = reduced corpus, explicit pre-FULL check); HARD_PASS strictly above floor; cardinality
gate (n_seeds x n_arms x n_dfeat); per-unit failure-class; fixed arithmetic seeds (no hash()/
list(set())); numbers tagged MEASURED/HYPOTHESIZED/THEORETICAL.

PRIOR ART (credit; learn-from/build-on, never steal): see exp_novel_atom_real_codebook_generalization_v1
docstring (Levy & Goldberg 2015; Church & Hanks 1990; Kanerva 1988 / Sahlgren 2005; Khodak et al. ACL
2018 a-la-carte embeddings -- the capacity-vs-linear-induction-quality relationship this curve directly
probes; Snell et al. 2017 ProtoNet; Plate 1995 HRR unitary vectors; McClelland, McNaughton & O'Reilly
1995 CLS; Greff, van Steenkiste & Schmidhuber 2020 construction-determinism critique). This cell adds no
new mechanism -- it is the VET's own named parameter-capacity revival of an already-credited pipeline.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

ANCHOR_NAME = "exp_novel_atom_real_codebook_capacity_curve_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_novel_atom_real_codebook_generalization_v1 as v1  # noqa: E402

# --------------------------------------------------------------------------- config
# All non-D_FEAT parameters IDENTICAL to v1's FULL regime (atom 29381 lineage) for direct comparability.
N = v1.N                             # 1024, HRR dim (unchanged across curve)
RI_SPARSITY = v1.RI_SPARSITY
FEAT_PROJ_SEED = v1.FEAT_PROJ_SEED
CODE_SEED = v1.CODE_SEED
RIDGE_ALPHA = v1.RIDGE_ALPHA         # 10.0, fixed across curve (isolates D_FEAT as the ONLY swept var)
ROLE_SEED = v1.ROLE_SEED
DISTRACTOR_SEED = v1.DISTRACTOR_SEED
R_ROLES = v1.R_ROLES
ALPHA_FRAC = v1.ALPHA_FRAC
MIN_OCC_PER_DRAW = v1.MIN_OCC_PER_DRAW

ARMS = list(v1.ARMS)
SEEDS = [7, 13, 19]

DFEAT_CURVE_FULL = [256, 512, 1024]      # headline = last point (1024)
DFEAT_CURVE_SMOKE = [256, 1024]          # smoke: endpoints only (cheaper; discriminator-preview per §DISCRIMINATOR-MUST-SURVIVE-SCALE)

FULL_CFG = dict(v1.FULL_CFG)             # identical world regime to v1's FULL (V=10000, 8M tokens)
SMOKE_CFG = dict(v1.SMOKE_CFG)

CEIL_CHECK_SCENES = v1.CEIL_CHECK_SCENES

# Pre-registered bands (HEADLINE = D_FEAT=1024; declared BEFORE this run per the VET's contract).
HP_MARGIN_MIN = 0.03            # codebook_derived - memorize_prototype must clear this at D_FEAT=1024
HP_MARGIN_ALL_SEEDS_POSITIVE = True   # ALL 3 seeds' margins must be > 0 at D_FEAT=1024 (multi-seed flip)
HP_RANDOM_MARGIN_MIN = 0.05     # codebook_derived must still clear random_code by this much (content-survives sanity)
HF_MARGIN_MAX = 0.00            # margin <= 0 at D_FEAT=1024 = HARD_FAIL (similarity-placement ceiling holds)
CEIL_CHECK_MIN = 0.90           # mechanics sanity floor, shared across D_FEAT points


# --------------------------------------------------------------------------- infra guards (same pattern as v1)
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(marker, fh)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- per-D_FEAT-point evaluation
def run_dfeat_point(dfeat, V, ids, true_codes, true_codes_np, ppmi, seen_idx, held_idx, cand_idx, cand_pos,
                     role_codes, cand_table, positions, window, k_eval, seeds, output_dir, col_stats):
    """Rebuilds ONLY the D_FEAT-dependent pieces (R_feat, feat_full_all, ridge induction map W), then runs
    v1.run_one_seed UNCHANGED (imported) for each seed. Sets v1's module-level _R_FEAT / _COL_STATS globals
    because run_one_seed / feat_from_raw_row reference them as module globals (same code path as v1's own
    run(), not a reimplementation)."""
    R_feat = v1.sparse_ternary_projection(V, dfeat, RI_SPARSITY, FEAT_PROJ_SEED)
    feat_full_all = (ppmi @ R_feat).toarray().astype(np.float64)
    nrm = np.linalg.norm(feat_full_all, axis=1, keepdims=True)
    nrm[nrm < 1e-12] = 1.0
    feat_full_all = feat_full_all / nrm

    v1._R_FEAT = R_feat
    v1._COL_STATS = col_stats

    X_train = feat_full_all[seen_idx]
    Y_train = true_codes_np[seen_idx]
    W_ridge = v1.ridge_fit(X_train, Y_train, RIDGE_ALPHA)

    # cheat-case diagnostic (matches the VET's independent-recompute measurement: full, non-partial
    # held-out features through the ridge map -> cosine-to-true; deterministic, no seed loop needed)
    cheat_feats = feat_full_all[held_idx]
    cheat_pred = v1.ridge_predict(W_ridge, cheat_feats)
    cheat_predn = cheat_pred / np.linalg.norm(cheat_pred, axis=1, keepdims=True)
    cheat_cosine_mean = float((cheat_predn * true_codes_np[held_idx]).sum(axis=1).mean())

    per_unit = {}
    per_seed_results = {}
    seed_pred_hashes = {}
    n_units_done = 0
    for seed in seeds:
        try:
            res = v1.run_one_seed(seed, V, ids, true_codes, feat_full_all, W_ridge, seen_idx, held_idx,
                                   cand_idx, cand_pos, role_codes, cand_table, positions, window, k_eval,
                                   output_dir)
            per_seed_results[seed] = res
            seed_pred_hashes[seed] = res["per_arm_preds_hash"]
            for arm in ARMS:
                unit_key = f"{arm}__seed{seed}__dfeat{dfeat}"
                per_unit[unit_key] = {"arm": arm, "seed": seed, "dfeat": dfeat,
                                       "novel_query_acc": res["per_arm_acc"][arm], "failure_class": None}
                n_units_done += 1
            _hb(output_dir, f"dfeat={dfeat} seed={seed}: "
                             f"{ {a: round(v, 3) for a, v in res['per_arm_acc'].items()} }")
        except Exception as e:  # NOT BaseException; per-unit failure-class (META_RULE_J)
            for arm in ARMS:
                unit_key = f"{arm}__seed{seed}__dfeat{dfeat}"
                per_unit[unit_key] = {"arm": arm, "seed": seed, "dfeat": dfeat,
                                       "failure_class": f"{type(e).__name__}: {str(e)[:200]}"}
            _hb(output_dir, f"dfeat={dfeat} seed={seed}: FAILED {type(e).__name__}: {e}")

    def _m(vals):
        return float(np.mean(vals)) if vals else float("nan")

    arm_summary = {}
    for arm in ARMS:
        vals = [per_seed_results[s]["per_arm_acc"][arm] for s in seeds if s in per_seed_results]
        arm_summary[arm] = {"acc_mean": _m(vals), "acc_std": float(np.std(vals)) if len(vals) > 1 else 0.0,
                             "acc_per_seed": {str(s): per_seed_results[s]["per_arm_acc"][arm]
                                              for s in seeds if s in per_seed_results},
                             "n_seeds": len(vals)}

    per_seed_margin = {}
    for s in seeds:
        if s in per_seed_results:
            per_seed_margin[str(s)] = (per_seed_results[s]["per_arm_acc"]["codebook_derived"]
                                        - per_seed_results[s]["per_arm_acc"]["memorize_prototype"])

    arms_differ = True
    arms_differ_detail = {}
    arms_differ_exempted = []
    for seed, hd in seed_pred_hashes.items():
        pairs = [(a, b) for a in ARMS for b in ARMS if a < b]
        for a, b in pairs:
            key = f"seed{seed}__{a}_vs_{b}"
            same = hd[a] == hd[b]
            arms_differ_detail[key] = not same
            if same:
                acc_a = per_seed_results[seed]["per_arm_acc"][a]
                acc_b = per_seed_results[seed]["per_arm_acc"][b]
                if acc_a > 0.95 and acc_b > 0.95:
                    arms_differ_exempted.append({"seed": seed, "dfeat": dfeat, "pair": [a, b],
                                                  "rationale": "both near-ceiling; identical predictions "
                                                                "indicates ceiling-matching, not a bug",
                                                  "acc_a": acc_a, "acc_b": acc_b})
                else:
                    arms_differ = False

    return {
        "dfeat": dfeat,
        "arm_summary": arm_summary,
        "cheat_cosine_mean": cheat_cosine_mean,
        "margin_codebook_vs_memorize_mean": arm_summary["codebook_derived"]["acc_mean"]
                                             - arm_summary["memorize_prototype"]["acc_mean"],
        "margin_codebook_vs_random_mean": arm_summary["codebook_derived"]["acc_mean"]
                                           - arm_summary["random_code"]["acc_mean"],
        "per_seed_margin_codebook_vs_memorize": per_seed_margin,
        "per_unit": per_unit,
        "n_units_done": n_units_done,
        "arms_differ_verified": arms_differ,
        "arms_differ_detail": arms_differ_detail,
        "arms_differ_exempted": arms_differ_exempted,
    }


# --------------------------------------------------------------------------- runner
def run(output_dir, cfg, dfeat_curve, seeds, run_mode):
    t0 = time.perf_counter()
    expected_n_units = len(seeds) * len(ARMS) * len(dfeat_curve)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    _hb(output_dir, f"building real world (SHARED across D_FEAT curve): n_tokens={cfg['n_tokens']} "
                     f"vocab_size={cfg['vocab_size']}")
    V, ids, cooc, ppmi, true_codes_np, counts = v1.build_real_world(
        cfg["n_tokens"], cfg["vocab_size"], cfg["window"], cfg["min_count"])
    true_codes = torch.from_numpy(true_codes_np).float()
    col_stats = v1.compute_ppmi_col_stats(cooc)
    _hb(output_dir, f"world built: V={V}")

    rank_lo, rank_hi, f_novel = cfg["rank_lo"], cfg["rank_hi"], cfg["f_novel"]
    stride = (rank_hi - rank_lo) // f_novel
    held_ranks = [rank_lo + i * stride for i in range(f_novel)]
    held_idx = np.array(held_ranks)
    held_set = set(held_ranks)
    seen_idx = np.array([i for i in range(V) if i not in held_set])
    held_counts = [float(counts[r]) for r in held_ranks]
    _hb(output_dir, f"held-out F_NOVEL={f_novel} rank[{rank_lo}:{rank_hi}] counts_range="
                    f"[{min(held_counts):.0f},{max(held_counts):.0f}]")

    distractor_rng = np.random.default_rng(DISTRACTOR_SEED)
    distractor_idx = distractor_rng.choice(seen_idx, size=cfg["n_distractor"], replace=False)
    cand_idx = np.concatenate([held_idx, distractor_idx])
    cand_table = true_codes[torch.from_numpy(cand_idx)]
    cand_pos = {int(idx): pos for pos, idx in enumerate(cand_idx)}
    chance_floor = 1.0 / len(cand_idx)
    _hb(output_dir, f"candidate table size={len(cand_idx)} chance_floor={chance_floor:.5f} "
                     f"(SHARED across D_FEAT curve)")

    positions = {i: np.where(ids == i)[0] for i in held_idx}
    role_codes = v1.unitary_hrr(R_ROLES, N, seed=ROLE_SEED)

    ceil_vals = [v1.ceiling_check(s, true_codes, seen_idx, distractor_idx, cand_pos, role_codes, cand_table,
                                   n_scenes=CEIL_CHECK_SCENES) for s in seeds]
    ceiling_check_mean = float(np.mean(ceil_vals))
    baseline_in_band = ceiling_check_mean >= CEIL_CHECK_MIN
    _hb(output_dir, f"ceiling_check (mechanics sanity, D_FEAT-independent) mean={ceiling_check_mean:.4f}")

    by_dfeat = {}
    n_units_done_total = 0
    for dfeat in dfeat_curve:
        _hb(output_dir, f"=== D_FEAT={dfeat} ===")
        pt = run_dfeat_point(dfeat, V, ids, true_codes, true_codes_np, ppmi, seen_idx, held_idx, cand_idx,
                              cand_pos, role_codes, cand_table, positions, cfg["window"], cfg["k_eval"],
                              seeds, output_dir, col_stats)
        by_dfeat[str(dfeat)] = pt
        n_units_done_total += pt["n_units_done"]

    cardinality_ok = (n_units_done_total == expected_n_units)
    arms_differ_all = all(by_dfeat[str(d)]["arms_differ_verified"] for d in dfeat_curve)

    headline_dfeat = dfeat_curve[-1]  # 1024 in FULL; 1024 in SMOKE (last point of the curve, by design)
    hp = by_dfeat[str(headline_dfeat)]
    headline_margin_mean = hp["margin_codebook_vs_memorize_mean"]
    headline_margin_vs_random = hp["margin_codebook_vs_random_mean"]
    headline_per_seed_margins = list(hp["per_seed_margin_codebook_vs_memorize"].values())
    headline_all_seeds_positive = all(m > 0 for m in headline_per_seed_margins) if headline_per_seed_margins else False

    # curve trend classification (both directions reported honestly)
    margins_by_point = [by_dfeat[str(d)]["margin_codebook_vs_memorize_mean"] for d in dfeat_curve]
    if margins_by_point[0] > 0 and margins_by_point[-1] > 0:
        flip_classification = "POSITIVE_THROUGHOUT_CURVE"
    elif margins_by_point[0] <= 0 and margins_by_point[-1] > HF_MARGIN_MAX:
        flip_classification = "FLIPS_POSITIVE_WITH_CAPACITY"
    elif margins_by_point[0] <= 0 and margins_by_point[-1] <= 0 and margins_by_point[-1] > margins_by_point[0]:
        flip_classification = "CONVERGES_TOWARD_ZERO_BUT_DOES_NOT_BEAT"
    elif margins_by_point[0] <= 0 and margins_by_point[-1] <= margins_by_point[0]:
        flip_classification = "NEGATIVE_THROUGHOUT_NO_IMPROVEMENT_WITH_CAPACITY"
    else:
        flip_classification = "NEGATIVE_THROUGHOUT_NONMONOTONIC"

    codebook_curve = [round(by_dfeat[str(d)]["arm_summary"]["codebook_derived"]["acc_mean"], 4) for d in dfeat_curve]
    memorize_curve = [round(by_dfeat[str(d)]["arm_summary"]["memorize_prototype"]["acc_mean"], 4) for d in dfeat_curve]
    random_curve = [round(by_dfeat[str(d)]["arm_summary"]["random_code"]["acc_mean"], 4) for d in dfeat_curve]
    cheat_cosine_curve = [round(by_dfeat[str(d)]["cheat_cosine_mean"], 4) for d in dfeat_curve]
    margin_curve = [round(m, 4) for m in margins_by_point]

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ_all:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not baseline_in_band:
        verdict = "HARD_FAIL_MECHANICS_SANITY_CEILING_CHECK_BELOW_BAND"
    elif headline_margin_mean <= HF_MARGIN_MAX:
        verdict = "HARD_FAIL_INDUCTION_DOES_NOT_BEAT_NAIVE_NN_AT_D_FEAT_1024"
    elif (headline_margin_mean >= HP_MARGIN_MIN
          and headline_all_seeds_positive
          and headline_margin_vs_random >= HP_RANDOM_MARGIN_MIN):
        verdict = "HARD_PASS_INDUCTION_BEATS_NAIVE_NN_AT_D_FEAT_1024"
    else:
        verdict = "MIDDLE_BAND_MARGIN_POSITIVE_BUT_NOT_DECISIVE"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        f"HEADLINE D_FEAT={headline_dfeat}: margin(codebook_derived-memorize_prototype)={headline_margin_mean:.4f} "
        f"all_seeds_positive={headline_all_seeds_positive} per_seed_margins={[round(m,4) for m in headline_per_seed_margins]} "
        f"vs_random_margin={headline_margin_vs_random:.4f} | "
        f"CURVE D_FEAT={list(dfeat_curve)}: codebook_derived={codebook_curve} memorize_prototype={memorize_curve} "
        f"random_code={random_curve} margin={margin_curve} cheat_cosine_to_true={cheat_cosine_curve} | "
        f"flip_classification={flip_classification} | ceiling_check(mechanics)={ceiling_check_mean:.3f} | "
        f"cardinality_ok={cardinality_ok} ({n_units_done_total}/{expected_n_units}) arms_differ={arms_differ_all}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:220]}", "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {**cfg, "N": N, "RI_SPARSITY": RI_SPARSITY, "RIDGE_ALPHA": RIDGE_ALPHA, "R_ROLES": R_ROLES,
                   "ALPHA_FRAC": ALPHA_FRAC, "MIN_OCC_PER_DRAW": MIN_OCC_PER_DRAW, "seeds": seeds,
                   "dfeat_curve": list(dfeat_curve), "V": V, "held_ranks": held_ranks,
                   "held_counts": held_counts, "n_seen": int(len(seen_idx)), "n_candidates": int(len(cand_idx))},
        "by_dfeat": by_dfeat,
        "headline_dfeat": headline_dfeat,
        "headline_margin_mean": headline_margin_mean,
        "headline_all_seeds_positive": headline_all_seeds_positive,
        "headline_per_seed_margins": headline_per_seed_margins,
        "flip_classification": flip_classification,
        "codebook_curve": codebook_curve, "memorize_prototype_curve": memorize_curve,
        "random_code_curve": random_curve, "cheat_cosine_curve": cheat_cosine_curve, "margin_curve": margin_curve,
        "ceiling_check_mechanics_acc_mean": ceiling_check_mean,
        "bands": {"HP_MARGIN_MIN": HP_MARGIN_MIN, "HP_MARGIN_ALL_SEEDS_POSITIVE": HP_MARGIN_ALL_SEEDS_POSITIVE,
                  "HP_RANDOM_MARGIN_MIN": HP_RANDOM_MARGIN_MIN, "HF_MARGIN_MAX": HF_MARGIN_MAX,
                  "CEIL_CHECK_MIN": CEIL_CHECK_MIN, "CHANCE_FLOOR": chance_floor},
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_n_units,
        "n_units_done": n_units_done_total, "arms_differ_verified": arms_differ_all,
        "baseline_in_band": baseline_in_band,
        "crlb_n/a": f"classification-accuracy generalization over C={len(cand_idx)} discrete candidates; "
                    f"closed-form chance floor = 1/C = {chance_floor:.5f} (THEORETICAL); not a CRLB regime",
        "prior_art": "LevyGoldberg2015 PPMI-SVD; ChurchHanks1990 PMI; Kanerva1988/Sahlgren2005 RI; "
                     "Khodak2018 a-la-carte (capacity-vs-linear-induction); Snell2017 ProtoNet; "
                     "Plate1995 HRR unitary vectors; McClelland1995 CLS; GreffVanSteenkisteSchmidhuber2020",
        "integration_of": ["exp_novel_atom_real_codebook_generalization_v1 (atom 29381, VET-named revival "
                           "target; D_FEAT=256 margin=-0.026)",
                           "exp_learned_codebook_generalization_gate_v1 (real codebook CG, atom 29368, "
                           "AUC=0.927)"],
        "revival_of_atom": "math::MEASURED_MECHANISM_novel_atom_real_codebook_generalization_v1_RETIERED...(29381)",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test at tiny scale: exercises the REAL builders (v1.build_vocab / build_cooc
    / build_ppmi / build_codebook / sparse_ternary_projection / ridge_fit / run_one_seed) through THIS
    cell's own multi-D_FEAT orchestration (run_dfeat_point), not a synthetic-only branch (Gate F.1)."""
    print("[self-test] real_code_path: building tiny toy world via v1's real builders", flush=True)
    base = (["cat", "pet", "feline", "purr", "whiskers"] * 8
            + ["dog", "pet", "canine", "bark", "loyal"] * 8
            + ["car", "road", "engine", "wheel", "drive"] * 8
            + ["king", "queen", "royal", "crown", "throne"] * 8
            + ["ship", "sail", "ocean", "captain", "anchor"] * 8)
    rng = np.random.default_rng(0)
    tokens = list(rng.permutation(base * 6))
    w2i, counts = v1.build_vocab(tokens, vocab_size=50, min_count=1)
    V = len(w2i)
    assert V >= 15, f"toy vocab too small V={V}"
    ids = np.fromiter((w2i.get(t, -1) for t in tokens), dtype=np.int64, count=len(tokens))
    cooc = v1.build_cooc(tokens, w2i, window=3)
    ppmi = v1.build_ppmi(cooc)
    tiny_N = 64
    true_codes_np = v1.build_codebook("ppmi_svd", cooc, ppmi, V, tiny_N, CODE_SEED, ri_sparsity=4)
    true_codes = torch.from_numpy(true_codes_np).float()
    col_stats = v1.compute_ppmi_col_stats(cooc)

    held_idx = np.array([0, 1])  # 2 tiny held-out "words" (most-frequent indices)
    held_set = set(held_idx.tolist())
    seen_idx = np.array([i for i in range(V) if i not in held_set])
    distractor_idx = np.array([i for i in range(V) if i not in held_set][:6])
    cand_idx = np.concatenate([held_idx, distractor_idx])
    cand_table = true_codes[torch.from_numpy(cand_idx)]
    cand_pos = {int(idx): pos for pos, idx in enumerate(cand_idx)}
    positions = {int(i): np.where(ids == i)[0] for i in held_idx}
    for i in held_idx:
        assert len(positions[int(i)]) > 5, f"toy corpus too small for held word {i}"

    # role_codes MUST have R_ROLES rows -- v1.run_one_seed references the module-level R_ROLES constant
    # (imported unchanged, =6) when drawing other-role fillers, regardless of how many roles this self-test
    # "needs" -- shape mismatch here is exactly the kind of bug Gate F.1 (real code path) is meant to catch.
    role_codes = v1.unitary_hrr(R_ROLES, tiny_N, seed=ROLE_SEED)

    print("[self-test] real_code_path: exercising run_dfeat_point (THIS cell's orchestration) at 2 tiny "
          "D_FEAT curve points", flush=True)
    tiny_dfeat_curve = [16, 32]  # must be >= RI_SPARSITY (10 nonzeros/row, sampled without replacement)
    scratch_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest_scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    by_dfeat = {}
    # v1.run_one_seed / v1.ceiling_check reference v1's own module-level N (=1024, the HRR dim) directly
    # (not passed as a parameter) for tensor .expand() calls -- this is the REAL production behavior (found
    # by this self-test itself, exercising the real code path per Gate F.1), so this self-test must run at
    # v1.N == tiny_N to keep TruncatedSVD/HRR dims consistent at toy V. Monkeypatch-and-restore v1.N for the
    # duration of this call only.
    _orig_v1_N = v1.N
    v1.N = tiny_N
    try:
        for dfeat in tiny_dfeat_curve:
            pt = run_dfeat_point(dfeat, V, ids, true_codes, true_codes_np, ppmi, seen_idx, held_idx, cand_idx,
                                  cand_pos, role_codes, cand_table, positions, window=3, k_eval=4,
                                  seeds=[0, 1], output_dir=scratch_dir, col_stats=col_stats)
            by_dfeat[dfeat] = pt
            assert pt["n_units_done"] == 2 * len(ARMS), f"cardinality mismatch at tiny dfeat={dfeat}"
            for arm in ARMS:
                acc = pt["arm_summary"][arm]["acc_mean"]
                assert np.isfinite(acc), f"non-finite acc for arm={arm} dfeat={dfeat}: {acc}"
            assert np.isfinite(pt["cheat_cosine_mean"]), "non-finite cheat_cosine_mean"
    finally:
        v1.N = _orig_v1_N

    margins = [by_dfeat[d]["margin_codebook_vs_memorize_mean"] for d in tiny_dfeat_curve]
    print(f"[self-test] toy margins by dfeat={tiny_dfeat_curve}: {[round(m,4) for m in margins]}", flush=True)

    print("[self-test] real_code_path: exercising ceiling_check (shared mechanics-sanity path)", flush=True)
    cc = v1.ceiling_check(7, true_codes, seen_idx, distractor_idx, cand_pos, role_codes, cand_table,
                           n_scenes=10)
    assert 0.0 <= cc <= 1.0

    print("[self-test] PASS: real tokenizer/vocab/cooc/ppmi/codebook/ridge/run_one_seed all exercised "
          "through run_dfeat_point at 2 tiny D_FEAT points; cardinality + finite-value guards held.",
          flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, SMOKE_CFG, DFEAT_CURVE_SMOKE, SEEDS, run_mode="smoke")
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, FULL_CFG, DFEAT_CURVE_FULL, SEEDS, run_mode="full")
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
