"""exp_srn_predict_scale_sweep_v1 -- does the predictive-reader order-sensitivity ADVANTAGE GROW WITH CORPUS SCALE?

DECISIVE QUESTION
  The VET-confirmed predictive-reader cell (exp_srn_predict_category_v1; VET af1fce7c) showed an
  order-sensitive prediction learner beats a static PPMI count baseline at POS-category induction by
  ~+0.060 AMI at 100k tokens (3/3 seeds, capacity-controlled). Modest, window-contingent. The make-or-break
  question for "real language ENGINE vs fixed modest trick": does that advantage GROW WITH SCALE (the
  Elman 1990 / LLM data-scaling signature) or stay FLAT?

  ONE VARIABLE = number of training tokens (corpus scale). Architecture / gold word set / metric / seeds
  are FIXED across scales. We sweep #tokens and report the TREND with seed error bars.

TWO DECISIVE CURVES (both reported explicitly)
  (1) ORDER-SENSITIVITY AMI MARGIN vs #tokens:  delta_ami(scale) = AMI(LEARNER_POS) - AMI(STATIC_PPMI),
      per seed, at each scale. Does mean(delta_ami) GROW monotonically with log10(tokens), above seed noise?
  (2) NEXT-WORD LM GAP vs #tokens:  gap(scale) = learner_top1 - bigram_top1 (currently NEGATIVE ~ -0.033
      at 100k). Does scaling CLOSE the gap (gap becomes less negative / crosses 0)?
  Plus SECONDARY: k-WINDOW map at a subset of scales -- does the BEST-k margin grow with scale (the VET
  found the margin flips negative at k=3 at 100k)?

ARMS (reused VERBATIM from exp_srn_predict_category_v1 -- imported, not re-implemented)
  LEARNER_POS  : order-sensitive prediction learner (fixed +/-1 position-role bind before bundle). MECHANISM.
  LEARNER_BAG  : order-blind ablation (same learner, no position bind). CONTROL for "is it order that scales".
  STATIC_PPMI  : REAL baseline. Directional causal-window PPMI -> truncated SVD. Levy-Goldberg count analog
                 of word2vec. Recomputed AT EACH SCALE (the margin is learner-minus-static AT THAT SCALE).
  RANDOM_CODE  : must-fail floor / metric-fires control. AMI ~ 0.
  bigram-MLE   : REAL baseline for the LM gap (next-word top-1).

CONFOUND CONTROL (design-gate item 4: ONE variable differs)
  The vocab + POS gold set are built ONCE from the SMALLEST-scale slice, then held FIXED across all scales.
  So every evaluated word has >= min_count occurrences at EVERY scale (fixed coverage, fixed clustering
  target) and the ONLY thing that grows is training EVIDENCE PER WORD. This isolates evidence-scaling from
  vocab-coverage growth. Epochs are FIXED across scales, so compute grows proportionally with data -- the
  standard data-scaling regime (Elman/LLM). Documented honestly; the alternative (per-scale vocab) would
  make the AMI numbers non-comparable across scales (different word sets, different difficulty).

DISCRIMINATOR / CAN-FAIL (design-gate item 2)
  HARD_PASS  = the AMI margin GROWS with scale (>= 2/3 seeds positive slope AND top-minus-bottom mean margin
               >= GROWTH_MARGIN_MIN and above endpoint seed-std)  OR  the LM gap CLOSES with scale.
  HARD_FAIL  = FLAT or SHRINKING margin (top-minus-bottom <= 0) AND LM gap does not close. This is the honest
               'fixed modest trick, NOT a scaling language engine' verdict -- FIRST-CLASS, we do NOT torture
               toward a growth trend.
  MIDDLE_BAND= positive but within seed noise / mixed across seeds.
  The margin discriminator is empirically sensitive: at 100k the VET'd cell had seed-std ~0.005 on delta_ami,
  so even a modest slope is resolvable. A saturated-at-smallest-scale representation would show a flat curve.

GLASS-BOX: numpy / torch(cpu) / sklearn / nltk. NO runtime LLM. ASCII-only. Seeded generators + fixed ints.
CLAIM-VET-pending: this cell does NOT self-declare chain-grade; it reports the curves + a raw trend verdict.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash-test)
  - final_metrics_atomicity = tmp_replace (os.replace)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - baseline_in_band + metric-fires checked AT EACH SCALE (0.03 < AMI_static < 0.95; |AMI_random| < 0.03)
  - cardinality_ok: EXPECTED_N_UNITS = n_scales * n_seeds; verdict HARD_FAILs on breach (META_RULE_H)
  - per-unit failure-class instrumentation; no bare except (META_RULE_J)
  - no hash()-derived seeds / no list(set()) ordering (F.5) -> fixed int seeds + sorted(set())
  - start marker + crash metrics + heartbeat (defensive_error_checking all 4 patterns)
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

# repo root on sys.path so the sibling-experiment import resolves under direct invocation + runner
_REPO_BOOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_BOOT not in sys.path:
    sys.path.insert(0, _REPO_BOOT)

# REUSE the VET'd arm code VERBATIM (imported, not re-implemented) -- guarantees identical mechanism.
from experiments.exp_srn_predict_category_v1 import (  # noqa: E402
    GOLD_CATS,
    arm_learner,
    arm_random,
    arm_static_ppmi,
    arms_must_differ,
    build_vocab_and_gold,
    eval_category_structure,
    load_brown_slice,
    secondary_nextword_topk,
    tokenize_ids,
)

ANCHOR_NAME = "srn_predict_scale_sweep_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --------------------------------------------------------------------------- IO / diagnostics
def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _emit_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = {"ts_iso": _now_iso(), "unit_idx": int(unit_idx), "total_units": int(total_units),
           "elapsed_s": round(elapsed_s, 2)}
    if extra:
        row["extra"] = extra
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic per META_RULE_AH


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


# --------------------------------------------------------------------------- fixed vocab/gold from smallest slice
def build_fixed_vocab_gold(smallest_sents, vocab_size, min_count, min_members):
    """Build the FIXED vocab + remapped POS gold ONCE from the smallest-scale slice.

    Returns (word2id, id2word, gold2 [V] int (-1 = no gold / dropped cat), n_cats, cats_used2)."""
    word2id, id2word, gold, cats_used, _purity = build_vocab_and_gold(
        smallest_sents, vocab_size, min_count)
    present = np.array([g for g in gold if g >= 0])
    cat_counts = Counter(present.tolist())
    keep_cats = sorted([c for c, n in cat_counts.items() if n >= min_members])
    remap = {c: i for i, c in enumerate(keep_cats)}
    gold2 = np.array([remap.get(g, -1) if g >= 0 else -1 for g in gold], dtype=np.int64)
    n_cats = len(keep_cats)
    cats_used2 = [cats_used[c] for c in keep_cats]
    return word2id, id2word, gold2, n_cats, cats_used2, cat_counts, keep_cats


# --------------------------------------------------------------------------- one scale point
def run_scale_point(seqs, V, gold2, n_cats, cfg, static_vec, random_vec):
    """Train POS (all seeds) + BAG (control seed) learners on this scale's seqs; eval AMI vs FIXED gold.

    Returns dict with per-seed AMI + margins. static_vec/random_vec precomputed for this scale."""
    d, k = cfg["d"], cfg["k"]
    epochs, batch, lr = cfg["epochs"], cfg["batch"], cfg["lr"]
    ami_static, _, _, _, _, _, _ = eval_category_structure(static_vec, gold2, n_cats, cfg["kmeans_seeds"][0])
    ami_random, _, _, _, _, _, _ = eval_category_structure(random_vec, gold2, n_cats, cfg["kmeans_seeds"][0])
    per_seed = []
    pos_digest = None
    for si, seed in enumerate(cfg["seeds"]):
        posE, posW, pos_ce = arm_learner(seqs, V, d, k, epochs, batch, lr, seed, order_sensitive=True)
        kseed = cfg["kmeans_seeds"][si % len(cfg["kmeans_seeds"])]
        ami_p, nmi_p, _, pur_p, _, _, _ = eval_category_structure(posE, gold2, n_cats, kseed)
        # STATIC recomputed per kmeans seed too, for a fair per-seed margin
        ami_s, _, _, _, _, _, _ = eval_category_structure(static_vec, gold2, n_cats, kseed)
        row = {"seed": seed, "kmeans_seed": kseed, "pos_ce": round(pos_ce, 4),
               "ami_learner_pos": round(ami_p, 4), "ami_static": round(ami_s, 4),
               "nmi_learner_pos": round(nmi_p, 4), "purity_learner_pos": round(pur_p, 4),
               "delta_ami": round(ami_p - ami_s, 4)}
        per_seed.append(row)
        if si == 0:
            pos_digest = hashlib.sha256(np.ascontiguousarray(posE).tobytes()).hexdigest()
    # BAG control (order-blind) at the control seed only
    bag_rows = []
    for seed in cfg["bag_seeds"]:
        bagE, _bagW, bag_ce = arm_learner(seqs, V, d, k, epochs, batch, lr, seed, order_sensitive=False)
        ami_b, _, _, _, _, _, _ = eval_category_structure(bagE, gold2, n_cats, cfg["kmeans_seeds"][0])
        ami_s0, _, _, _, _, _, _ = eval_category_structure(static_vec, gold2, n_cats, cfg["kmeans_seeds"][0])
        bag_rows.append({"seed": seed, "bag_ce": round(bag_ce, 4), "ami_learner_bag": round(ami_b, 4),
                         "delta_ami_bag": round(ami_b - ami_s0, 4)})
    return {"per_seed": per_seed, "bag": bag_rows,
            "ami_static_kseed0": round(ami_static, 4), "ami_random_kseed0": round(ami_random, 4),
            "delta_ami_mean": round(float(np.mean([r["delta_ami"] for r in per_seed])), 4),
            "delta_ami_std": round(float(np.std([r["delta_ami"] for r in per_seed])), 4),
            "ami_pos_mean": round(float(np.mean([r["ami_learner_pos"] for r in per_seed])), 4),
            "pos_digest_seed0": pos_digest}


# --------------------------------------------------------------------------- k-window map (secondary, 1 seed)
def kmap_at_scale(seqs, V, gold2, n_cats, cfg, ks):
    """For a subset of scales, sweep k in ks for 1 seed: best-k margin (learner_pos - static) at that k."""
    d = cfg["d"]
    seed = cfg["seeds"][0]
    kseed = cfg["kmeans_seeds"][0]
    out = []
    for k in ks:
        static_k = arm_static_ppmi(seqs, V, d, k, seed=0)
        posE, _W, _ce = arm_learner(seqs, V, d, k, cfg["epochs"], cfg["batch"], cfg["lr"], seed,
                                    order_sensitive=True)
        ami_p, _, _, _, _, _, _ = eval_category_structure(posE, gold2, n_cats, kseed)
        ami_s, _, _, _, _, _, _ = eval_category_structure(static_k, gold2, n_cats, kseed)
        out.append({"k": k, "ami_pos": round(ami_p, 4), "ami_static": round(ami_s, 4),
                    "delta_ami": round(ami_p - ami_s, 4)})
    best = max(out, key=lambda r: r["delta_ami"]) if out else None
    return {"per_k": out, "best_k": best["k"] if best else None,
            "best_delta_ami": best["delta_ami"] if best else None}


# --------------------------------------------------------------------------- config
def cfg_for(mode):
    if mode == "smoke":
        # 2 small scales just to exercise the trend machinery + arms-differ + gates; fast.
        return dict(scale_sents=[400, 1200], vocab_size=160, min_count=3, d=64, k=4, epochs=4,
                    batch=512, lr=0.01, seeds=[7, 13], kmeans_seeds=[0, 1], min_members=5,
                    bag_seeds=[7], kmap_ks=[3, 4], kmap_scale_idx=[0, 1], do_lm=True)
    if mode == "full":
        # 4 token scales via n_sents (~25k/50k/100k/200k tokens); counts measured + reported.
        # epochs FIXED across scales (standard data-scaling regime: compute grows with data). k-map at the
        # smallest + largest scale answers 'does best-k margin grow with scale' cheaply (1 seed).
        return dict(scale_sents=[2000, 4000, 8000, 16000], vocab_size=800, min_count=5,
                    d=128, k=5, epochs=12, batch=512, lr=0.01, seeds=[7, 13, 19],
                    kmeans_seeds=[0, 1, 2], min_members=8, bag_seeds=[7],
                    kmap_ks=[2, 3, 5], kmap_scale_idx=[0, 3], do_lm=True)
    raise ValueError("mode must be smoke|full")


# --------------------------------------------------------------------------- verdict (the TREND)
def compute_verdict(scale_rows, lm_rows, n_seeds, n_scales, expected_units, actual_units):
    """The discriminator is the TREND across scales. HARD_PASS = margin grows OR LM gap closes."""
    GROWTH_MARGIN_MIN = 0.02   # AMI is chance-corrected; top-minus-bottom mean margin must clear this
    LM_CLOSE_MIN = 0.010       # LM gap (learner-bigram) must increase (close) by at least this
    maj = (n_seeds // 2) + 1

    # cardinality gate first (META_RULE_H)
    if actual_units < expected_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "cardinality breach: %d/%d (scale,seed) units present" % (actual_units, expected_units),
                {})

    # per-scale metric-fires + baseline-in-band (every scale)
    bad = []
    for r in scale_rows:
        if abs(r["ami_random_kseed0"]) >= 0.03:
            bad.append("scale=%d ami_random=%.3f" % (r["n_tokens"], r["ami_random_kseed0"]))
        if not (0.03 < r["ami_static_kseed0"] < 0.95):
            bad.append("scale=%d ami_static=%.3f OOB" % (r["n_tokens"], r["ami_static_kseed0"]))
    if bad:
        return ("INVALID_REGIME", "regime gates failed at: " + "; ".join(bad), {})

    toks = np.array([r["n_tokens"] for r in scale_rows], dtype=np.float64)
    logt = np.log10(toks)
    # per-seed delta trajectory across scales -> slope of delta_ami vs log10(tokens)
    seeds = [row["seed"] for row in scale_rows[0]["per_seed"]]
    per_seed_slope = {}
    per_seed_traj = {}
    for sd in seeds:
        traj = []
        for r in scale_rows:
            v = [x["delta_ami"] for x in r["per_seed"] if x["seed"] == sd][0]
            traj.append(v)
        traj = np.array(traj, dtype=np.float64)
        per_seed_traj[sd] = [round(float(x), 4) for x in traj]
        slope = float(np.polyfit(logt, traj, 1)[0]) if len(logt) >= 2 else 0.0
        per_seed_slope[sd] = round(slope, 4)
    n_pos_slope = sum(1 for sd in seeds if per_seed_slope[sd] > 0)

    mean_delta = np.array([r["delta_ami_mean"] for r in scale_rows], dtype=np.float64)
    std_delta = np.array([r["delta_ami_std"] for r in scale_rows], dtype=np.float64)
    growth_margin = float(mean_delta[-1] - mean_delta[0])
    endpoint_std = float(np.sqrt((std_delta[0] ** 2 + std_delta[-1] ** 2) / 2.0))
    above_noise = growth_margin > max(endpoint_std, 1e-9)

    grows = (n_pos_slope >= maj) and (growth_margin >= GROWTH_MARGIN_MIN) and above_noise

    # LM gap trend
    lm_close = False
    lm_detail = {}
    if lm_rows:
        gaps = np.array([r["learner_top1"] - r["bigram_top1"] for r in lm_rows], dtype=np.float64)
        lm_gap_delta = float(gaps[-1] - gaps[0])
        lm_close = lm_gap_delta >= LM_CLOSE_MIN
        lm_detail = {"gap_bottom": round(float(gaps[0]), 4), "gap_top": round(float(gaps[-1]), 4),
                     "gap_delta_top_minus_bottom": round(lm_gap_delta, 4), "lm_close": lm_close}

    detail = {"per_seed_slope": per_seed_slope, "per_seed_delta_trajectory": per_seed_traj,
              "n_positive_slope": n_pos_slope, "maj_needed": maj,
              "mean_delta_by_scale": [round(float(x), 4) for x in mean_delta],
              "growth_margin_top_minus_bottom": round(growth_margin, 4),
              "endpoint_std": round(endpoint_std, 4), "above_seed_noise": above_noise,
              "growth_margin_min": GROWTH_MARGIN_MIN, "grows": grows, "lm": lm_detail}

    if grows or lm_close:
        verdict = "HARD_PASS"
        why = []
        if grows:
            why.append("AMI margin GROWS: %d/%d seeds positive slope, top-bottom=+%.3f (endpoint_std=%.3f)"
                       % (n_pos_slope, n_seeds, growth_margin, endpoint_std))
        if lm_close:
            why.append("LM gap CLOSES: gap %.3f -> %.3f (delta=+%.3f)"
                       % (lm_detail["gap_bottom"], lm_detail["gap_top"], lm_detail["gap_delta_top_minus_bottom"]))
        msg = "predictive-reader SCALES toward language capability: " + "; ".join(why)
    elif (growth_margin <= 0.0) and (not lm_close):
        verdict = "HARD_FAIL"
        msg = ("FIXED MODEST TRICK, not a scaling engine (FIRST-CLASS negative): AMI margin FLAT/SHRINKING "
               "top-bottom=%+.3f (%d/%d seeds pos slope); LM gap does not close. Advantage does NOT grow with scale."
               % (growth_margin, n_pos_slope, n_seeds))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("marginal: AMI margin top-bottom=%+.3f (min +%.2f, endpoint_std=%.3f, %d/%d seeds pos slope); "
               "LM gap close=%s -- growth present but within noise / mixed"
               % (growth_margin, GROWTH_MARGIN_MIN, endpoint_std, n_pos_slope, n_seeds, lm_close))
    return (verdict, msg, detail)


# --------------------------------------------------------------------------- run
def run(mode):
    t0 = time.perf_counter()
    cfg = cfg_for(mode)
    output_dir = os.path.join(REPO, "data", "exp_%s%s" % (ANCHOR_NAME, "_smoke" if mode == "smoke" else ""))
    n_scales = len(cfg["scale_sents"])
    n_seeds = len(cfg["seeds"])
    expected_units = n_scales * n_seeds
    _write_start_marker(output_dir, mode, expected_units)

    # load the LARGEST slice once; smaller scales are prefixes (nested corpora)
    max_sents = max(cfg["scale_sents"])
    all_sents = load_brown_slice(max_sents)
    smallest = min(cfg["scale_sents"])

    # FIXED vocab + gold from the SMALLEST slice (confound control: same gold + coverage at every scale)
    word2id, id2word, gold2, n_cats, cats_used2, cat_counts, keep_cats = build_fixed_vocab_gold(
        all_sents[:smallest], cfg["vocab_size"], cfg["min_count"], cfg["min_members"])
    V = len(id2word)
    n_gold_words = int((gold2 >= 0).sum())

    scale_rows = []
    lm_rows = []
    kmap_rows = []
    arms_digests = None
    failures = []
    unit_count = 0
    for scale_idx, ns in enumerate(cfg["scale_sents"]):
        sents = all_sents[:ns]
        seqs = tokenize_ids(sents, word2id)            # FIXED vocab -> OOV dropped
        n_tokens = int(sum(len(s) for s in seqs))
        # per-scale STATIC (deterministic) + RANDOM (scale-independent, metric-fires floor)
        static_vec = arm_static_ppmi(seqs, V, cfg["d"], cfg["k"], seed=0)
        random_vec = arm_random(V, cfg["d"], seed=0)
        try:
            res = run_scale_point(seqs, V, gold2, n_cats, cfg, static_vec, random_vec)
        except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J); NOT bare
            failures.append({"scale_sents": ns, "failure_class": type(e).__name__, "msg": str(e)[:300]})
            _emit_heartbeat(output_dir, scale_idx, n_scales, time.perf_counter() - t0,
                            extra={"scale_sents": ns, "FAILED": type(e).__name__})
            continue
        unit_count += len(res["per_seed"])
        row = {"scale_idx": scale_idx, "scale_sents": ns, "n_tokens": n_tokens, "vocab_size": V,
               "n_gold_words": n_gold_words, "n_categories": n_cats}
        row.update(res)
        # arms-differ at the first scale (POS/BAG/STATIC/RANDOM at seed 0)
        if arms_digests is None:
            bag0E, _bw, _bce = arm_learner(seqs, V, cfg["d"], cfg["k"], cfg["epochs"], cfg["batch"],
                                           cfg["lr"], cfg["seeds"][0], order_sensitive=True)
            bagBagE, _b2, _b3 = arm_learner(seqs, V, cfg["d"], cfg["k"], cfg["epochs"], cfg["batch"],
                                            cfg["lr"], cfg["seeds"][0], order_sensitive=False)
            arms_digests = arms_must_differ({"LEARNER_POS": bag0E, "LEARNER_BAG": bagBagE,
                                             "STATIC_PPMI": static_vec, "RANDOM_CODE": random_vec})
        scale_rows.append(row)
        _emit_heartbeat(output_dir, scale_idx, n_scales, time.perf_counter() - t0,
                        extra={"scale_sents": ns, "n_tokens": n_tokens,
                               "delta_ami_mean": row["delta_ami_mean"]})
        # LM gap at this scale
        if cfg["do_lm"]:
            try:
                lm = secondary_nextword_topk(seqs, V, cfg["k"], seed=cfg["seeds"][0], d=cfg["d"])
                lm["scale_sents"] = ns
                lm["n_tokens"] = n_tokens
                lm_rows.append(lm)
            except Exception as e:  # LM is secondary; record but never fatal
                lm_rows.append({"scale_sents": ns, "n_tokens": n_tokens,
                                "error": "%s: %s" % (type(e).__name__, str(e)[:200])})
        # k-window map at selected scales (secondary, 1 seed)
        if scale_idx in cfg["kmap_scale_idx"]:
            try:
                km = kmap_at_scale(seqs, V, gold2, n_cats, cfg, cfg["kmap_ks"])
                km["scale_sents"] = ns
                km["n_tokens"] = n_tokens
                kmap_rows.append(km)
            except Exception as e:
                kmap_rows.append({"scale_sents": ns, "n_tokens": n_tokens,
                                  "error": "%s: %s" % (type(e).__name__, str(e)[:200])})

    verdict, msg, detail = compute_verdict(scale_rows, [r for r in lm_rows if "error" not in r],
                                           n_seeds, n_scales, expected_units, unit_count)

    # LM curve summary
    lm_curve = [{"n_tokens": r["n_tokens"], "bigram_top1": r.get("bigram_top1"),
                 "learner_top1": r.get("learner_top1"),
                 "gap": (round(r["learner_top1"] - r["bigram_top1"], 4)
                         if ("learner_top1" in r and "bigram_top1" in r) else None)}
                for r in lm_rows]
    margin_curve = [{"n_tokens": r["n_tokens"], "delta_ami_mean": r["delta_ami_mean"],
                     "delta_ami_std": r["delta_ami_std"], "ami_pos_mean": r["ami_pos_mean"],
                     "ami_static_kseed0": r["ami_static_kseed0"]} for r in scale_rows]

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": "%s: %s" % (verdict, msg[:110]),
        "elapsed_s": round(elapsed, 2), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "mode": mode,
        "config": cfg,
        "fixed_gold": {"vocab_size": V, "n_gold_words": n_gold_words, "n_categories": n_cats,
                       "categories": cats_used2,
                       "note": "vocab+gold built ONCE from smallest slice; fixed across scales (confound control)"},
        "arms": ["LEARNER_POS", "LEARNER_BAG", "STATIC_PPMI", "RANDOM_CODE", "bigram_MLE"],
        "MARGIN_CURVE": margin_curve,          # (1) order-sensitivity AMI margin vs #tokens
        "LM_CURVE": lm_curve,                  # (2) next-word LM gap vs #tokens
        "KMAP": kmap_rows,                     # secondary: best-k margin vs scale
        "trend": detail,
        "per_scale_full": scale_rows,
        "expected_units": expected_units, "actual_units": unit_count,
        "cardinality_ok": unit_count >= expected_units,
        "failures": failures,
        "gates": {"arms_differ_verified": arms_digests is not None,
                  "cardinality_ok": unit_count >= expected_units},
    }
    _write_metrics(output_dir, metrics)
    print("[%s] verdict=%s" % (ANCHOR_NAME, verdict))
    print(msg)
    print("MARGIN_CURVE:", json.dumps(margin_curve, indent=2))
    print("LM_CURVE:", json.dumps(lm_curve, indent=2))
    print("trend:", json.dumps(detail, indent=2))
    print("metrics ->", os.path.join(output_dir, "metrics.json"))
    return metrics


# --------------------------------------------------------------------------- self-test (real code path)
def self_test():
    """Exercise the REAL scale-sweep machinery on 2 tiny scales; assert trend logic + gates fire."""
    print("[self-test] tiny 2-scale synthetic sweep...")
    cfg = dict(scale_sents=[200, 500], vocab_size=40, min_count=1, d=32, k=2, epochs=4, batch=128,
               lr=0.02, seeds=[7, 13], kmeans_seeds=[0, 1], min_members=3, bag_seeds=[7],
               kmap_ks=[2], kmap_scale_idx=[0], do_lm=False)
    # synthetic DET NOUN VERB grammar so category structure is present
    dets = ["the", "a", "this", "that"]
    nouns = ["dog", "cat", "man", "car", "tree", "house", "bird", "road"]
    verbs = ["runs", "sees", "eats", "moves", "finds", "holds", "keeps", "makes"]
    tagmap = {}
    for w in dets:
        tagmap[w] = "DET"
    for w in nouns:
        tagmap[w] = "NOUN"
    for w in verbs:
        tagmap[w] = "VERB"
    rng = np.random.default_rng(0)
    all_sents = []
    for _ in range(max(cfg["scale_sents"])):
        dd = rng.choice(dets); nn = rng.choice(nouns); vv = rng.choice(verbs)
        all_sents.append([(dd, tagmap[dd]), (nn, tagmap[nn]), (vv, tagmap[vv])])
    smallest = min(cfg["scale_sents"])
    word2id, id2word, gold2, n_cats, cats_used2, _cc, _kc = build_fixed_vocab_gold(
        all_sents[:smallest], cfg["vocab_size"], cfg["min_count"], cfg["min_members"])
    V = len(id2word)
    assert V == len(dets) + len(nouns) + len(verbs), "vocab %d unexpected" % V
    assert n_cats == 3, "expected 3 gold cats, got %d" % n_cats

    scale_rows = []
    for scale_idx, ns in enumerate(cfg["scale_sents"]):
        seqs = tokenize_ids(all_sents[:ns], word2id)
        n_tokens = int(sum(len(s) for s in seqs))
        static_vec = arm_static_ppmi(seqs, V, cfg["d"], cfg["k"], seed=0)
        random_vec = arm_random(V, cfg["d"], seed=0)
        res = run_scale_point(seqs, V, gold2, n_cats, cfg, static_vec, random_vec)
        row = {"scale_idx": scale_idx, "scale_sents": ns, "n_tokens": n_tokens}
        row.update(res)
        scale_rows.append(row)
        # arms-differ check on the real objects
        posE, _w, _c = arm_learner(seqs, V, cfg["d"], cfg["k"], cfg["epochs"], cfg["batch"], cfg["lr"],
                                   cfg["seeds"][0], order_sensitive=True)
        bagE, _w2, _c2 = arm_learner(seqs, V, cfg["d"], cfg["k"], cfg["epochs"], cfg["batch"], cfg["lr"],
                                     cfg["seeds"][0], order_sensitive=False)
        dg = arms_must_differ({"LEARNER_POS": posE, "LEARNER_BAG": bagE, "STATIC_PPMI": static_vec,
                               "RANDOM_CODE": random_vec})
        assert len(set(dg.values())) == 4, "arms must be distinct"
    # exercise the verdict trend logic
    verdict, msg, detail = compute_verdict(scale_rows, [], len(cfg["seeds"]), len(cfg["scale_sents"]),
                                           len(cfg["scale_sents"]) * len(cfg["seeds"]),
                                           len(cfg["scale_sents"]) * len(cfg["seeds"]))
    assert verdict in ("HARD_PASS", "HARD_FAIL", "MIDDLE_BAND", "INVALID_REGIME"), "bad verdict %s" % verdict
    assert "per_seed_slope" in detail or verdict == "INVALID_REGIME", "trend detail missing"
    # cardinality gate must HARD_FAIL when actual < expected
    v2, _m2, _d2 = compute_verdict(scale_rows, [], len(cfg["seeds"]), 2, 6, 3)
    assert v2 == "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", "cardinality gate did not fire: %s" % v2
    # F.5 determinism: static arm bit-identical on re-run
    s1 = arm_static_ppmi(tokenize_ids(all_sents[:cfg["scale_sents"][0]], word2id), V, cfg["d"], cfg["k"], 0)
    s2 = arm_static_ppmi(tokenize_ids(all_sents[:cfg["scale_sents"][0]], word2id), V, cfg["d"], cfg["k"], 0)
    assert np.array_equal(s1, s2), "static arm nondeterministic"
    print("[self-test] verdict=%s | margins=%s" % (verdict, [r["delta_ami_mean"] for r in scale_rows]))
    print("[self-test] PASS: real scale-sweep path exercised; arms differ; trend + cardinality gates fire.")
    return True


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(args.mode)


if __name__ == "__main__":
    output_dir_guess = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(output_dir_guess, e)
        raise
