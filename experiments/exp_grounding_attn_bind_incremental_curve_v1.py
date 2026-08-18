"""Grounding attention-bind, INCREMENTAL front-end: does the downstream illusory-conjunction binding
show the USER-mandated IMPROVING-WITH-EXPOSURE property when the perceptual front-end is a genuinely
INCREMENTAL learner (running-mean prototype refined per exposure) instead of the sample-efficient k-NN
exemplar store that SATURATED at n=1 (rise +0.042 < 0.06) in the banked cell 29457?

REVIVAL CRITERION (recorded by the 29457 VET, MIDDLE_BAND):
  "The binding win is proven (ATTN 0.815 vs FLAT 0.515 on the Treisman illusory conjunction, margin
   +0.300). The ONLY gap to HARD_PASS was the learning curve: the k-NN front-end is sample-efficient
   (learns fast/flat) -> downstream binding rose only +0.042. A SLOWER-LEARNING front-end whose
   downstream binding shows a MONOTONIC >= +0.06 exposure curve = a SEPARATE clean cell." This is it.

WHAT CHANGES vs 29457 (EXACTLY ONE variable = the front-end LEARNER):
  - REPLACED: train_front_end (k-NN exemplar store over ALL (color,shape) combos; at n_train=1 already
    holds S=6 samples per color -> centroid-dense -> saturated) is replaced by an INCREMENTAL running-mean
    PROTOTYPE classifier -- ONE prototype vector per color and per shape, seeded from a SINGLE noisy
    exposure and REFINED by streaming e exposures per class (running mean). At e=1 the prototype is a
    single jittered sample (genuinely few-shot, noisy); as exposures accumulate the running mean denoises
    (~1/sqrt(e)) -> classification improves -> a genuine downstream exposure curve. Brain-faithful:
    Posner-Keele prototype abstraction; perceptual categories refine with experience.
  - REUSED BIT-IDENTICAL (imported VERBATIM from exp_grounding_attn_bind_illusory_conjunction_v1):
    scene ontology + render (render_object/render_scene, difficulty NOISE/COL_JITTER/ASPECT unchanged),
    the SAME feature extractors (color_feature mean-RGB, shape_feature HOG-29438), the attention spotlight
    + FHRR bind (encode_scene ATTN/FLAT/SCRAM), the illusory-conjunction 2AFC + color-of-shape eval, the
    HARD feature-sharing scene subset (sample_scene force_share), and the anti-cheat SCRAM arm. The ONLY
    thing swapped is prototype-classifier-vs-kNN on top of the identical features -> FAIR.

DISCRIMINATORS (headline = the exposure curve):
  (1) EXPOSURE CURVE (THE headline, the 29457 gap): ATTN illusory-2AFC (and color-of-shape) at M_primary
      as a function of exposures-per-class e in {1,2,4,8,16,32}. HARD_PASS(b) = seed-averaged illusory-2AFC
      curve is MONOTONIC-nondecreasing (tol) AND rises >= +0.06 from e_min to e_max.
  (2) BINDING WIN PRESERVED (the 29457 proven result must survive the front-end swap): ATTN illusory-2AFC
      at e_max >= ILL_HP AND (ATTN - FLAT) >= ILL_MARGIN_HP (~+0.30 in 29457).
  (3) ANTI-CHEAT (all must hold): SCRAM (attention points at wrong locations) collapses to ~FLAT; FLAT sits
      near chance 0.5; LABEL-SHUFFLE front-end (permuted labels) collapses ATTN to ~chance (learned, not
      hand-installed); front-end classification non-degenerate at e_max.

HONEST FAIL/MIDDLE (load-bearing, must be reachable): a PROPER incremental learner can still SATURATE fast
  (downstream rise < 0.06) because the binding 2AFC is robust to modest front-end noise -> the improving
  property is genuinely NOT demonstrable on this easy task -> report MIDDLE_BAND, MM 29457 STANDS, do NOT
  force it. The self-test asserts the MACHINERY (front-end classification improves with exposure; binding
  win fires) but does NOT gate on the >= 0.06 downstream rise -- that magnitude is the empirical question
  the full run answers, and its failure is an honest finding.

FAIR / glass-box: real pixel-derived features (same as 29457); inspectable running-mean prototype vectors
(no autograd at runtime; "learning" = online mean); ONE variable (prototype vs k-NN on identical features);
difficulty-on (same renders); MONOTONIC-curve + LABEL-SHUFFLE must-fail + SCRAM anti-cheat. No CNN; no
external LM. CPU-only, pure numpy. ASCII-only. No emojis. No em dashes.

# CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at self-test (ATTN vs FLAT vs SCRAM scene-rep bit-differ) -- inherited via G0.encode_scene
# - final_metrics_atomicity = tmp + os.replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: discriminators are 2AFC/cleanup accuracies + an exposure curve; none is a closed-form floor
# - baseline_in_band: FLAT illusory-2AFC near chance 0.5 (<=ILL_FLAT_MAX); label-shuffle collapses;
#   front-end non-degenerate at e_max (>=FRONT_ACC_MIN)
# - discriminator survives scale: smoke fires ATTN>>FLAT AND a measurable exposure delta at the SAME
#   M_primary as full; full adds seeds + the full exposure grid + M-robustness. SMOKE = SAME code branches.
# - HARD_PASS strictly above floor: attn e_max >= ILL_HP AND margin >= ILL_MARGIN_HP AND scramble collapses
#   AND label-shuffle collapses AND exposure curve monotonic AND rise >= CURVE_RISE_HP
# - deterministic seeding: fixed int seeds only; no hash()-seeded RNG, no list(set()) ordering
# - all numbers tagged in the pre-reg doc
# - progress_logging = print_flush_true
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

ANCHOR_NAME = "grounding_attn_bind_incremental_curve_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse the 29457 grounding cell VERBATIM: scene gen + features + attention + FHRR bind + illusory eval.
# The ONLY thing this cell overrides is the front-end LEARNER (prototype-incremental vs k-NN).
import experiments.exp_grounding_attn_bind_illusory_conjunction_v1 as G0  # noqa: E402

# bit-identical reuse (names bound locally for readability; all are G0 objects)
C = G0.C
S = G0.S
render_object = G0.render_object
render_scene = G0.render_scene
_window = G0._window
color_feature = G0.color_feature
shape_feature = G0.shape_feature
sample_scene = G0.sample_scene
make_fhrr_codes = G0.make_fhrr_codes
encode_scene = G0.encode_scene
eval_arm_on_scenes = G0.eval_arm_on_scenes
novel_conjunction_free = G0.novel_conjunction_free

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; only scale/coverage differ)
#   expo_curve = exposures-per-class e (running-mean prototype update count per class)
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(seeds=[7], N=768, M_list=[4], M_primary=4,
                    expo_curve=[1, 16], n_scenes=90, n_query=3)
SMOKE_CFG = dict(seeds=[7, 13], N=768, M_list=[4], M_primary=4,
                 expo_curve=[1, 4, 16], n_scenes=170, n_query=4)
FULL_CFG = dict(seeds=[7, 13, 17, 23, 29], N=1024, M_list=[3, 4, 6], M_primary=4,
                expo_curve=[1, 2, 4, 8, 16, 32], n_scenes=300, n_query=4)

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the FULL run; see pre-reg doc)
# ---------------------------------------------------------------------------
ILL_HP = 0.78          # (a) binding win preserved: ATTN illusory-2AFC at M_primary, e_max >= this
ILL_FLAT_MAX = 0.62    # FLAT must sit near chance 0.5 (baseline_in_band)
ILL_MARGIN_HP = 0.18   # (a) (ATTN - FLAT) illusory-2AFC required (29457 had +0.30)
ILL_SCRAMBLE_MAX = 0.66  # ARM_SCRAMBLE must collapse to ~FLAT (attention localization load-bearing)
CURVE_RISE_HP = 0.06   # (b) ATTN illusory-2AFC(e_max) - (e_min): the improving-with-exposure property
CURVE_MONO_TOL = 0.02  # (b) seed-averaged curve must be nondecreasing within this per-step tolerance
LABEL_SHUFFLE_MAX = 0.66  # label-shuffle ATTN illusory-2AFC must collapse to ~chance (front-end learned)
FRONT_ACC_MIN = 0.75   # front-end color AND shape acc (e_max) must be non-degenerate
ILL_HF = 0.62          # HARD_FAIL: ATTN illusory-2AFC at e_max <= this (binding win broken by the swap)
CHANCE_2AFC = 0.5


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ---------------------------------------------------------------------------
# INCREMENTAL running-mean PROTOTYPE front-end (the ONE variable).
#   One prototype per class = online mean of that class's exposure features.
#   glass-box: prototype vectors are directly inspectable; no autograd; "learning" = running mean.
#   Data-slow at low e (single jittered sample) -> denoises ~1/sqrt(e) -> genuine exposure curve.
# ---------------------------------------------------------------------------
class ProtoStore:
    def __init__(self, n_color, n_shape, dc, ds):
        self.csum = np.zeros((n_color, dc), dtype=np.float64)
        self.ccnt = np.zeros(n_color, dtype=np.float64)
        self.ssum = np.zeros((n_shape, ds), dtype=np.float64)
        self.scnt = np.zeros(n_shape, dtype=np.float64)
        self.cmap = np.arange(n_color)   # label map (identity, or permuted for label-shuffle)
        self.smap = np.arange(n_shape)

    def update_color(self, ci, feat):
        self.csum[ci] += feat
        self.ccnt[ci] += 1.0

    def update_shape(self, si, feat):
        self.ssum[si] += feat
        self.scnt[si] += 1.0

    def color_protos(self):
        p = self.csum / np.maximum(self.ccnt[:, None], 1.0)
        return (p / (np.linalg.norm(p, axis=1, keepdims=True) + 1e-9))

    def shape_protos(self):
        p = self.ssum / np.maximum(self.scnt[:, None], 1.0)
        return (p / (np.linalg.norm(p, axis=1, keepdims=True) + 1e-9))


def train_incremental(e, rng, shuffle_labels=False):
    """Stream EXACTLY e single-object labeled exposures per class; running-mean prototype refinement.
    e=1 -> one jittered sample per class (few-shot). shuffle_labels files a class's exposures under a
    permuted label (destroys learned competence = must-fail)."""
    # probe feature dims from one render
    w0 = render_object(0, 0, rng)
    dc = color_feature(w0).shape[0]
    ds = shape_feature(w0).shape[0]
    store = ProtoStore(C, S, dc, ds)
    if shuffle_labels:
        store.cmap = rng.permutation(C)
        store.smap = rng.permutation(S)
    # color prototypes: e exposures of each color (random shape context)
    for ci in range(C):
        tgt = int(store.cmap[ci])
        for _ in range(e):
            si = int(rng.integers(0, S))
            w = render_object(ci, si, rng)
            store.update_color(tgt, color_feature(w))
    # shape prototypes: e exposures of each shape (random color context)
    for si in range(S):
        tgt = int(store.smap[si])
        for _ in range(e):
            ci = int(rng.integers(0, C))
            w = render_object(ci, si, rng)
            store.update_shape(tgt, shape_feature(w))
    return store


def classify_window_incr(window, store, cprot, sprot):
    cf = color_feature(window)
    sf = shape_feature(window)
    pc = int(np.argmax(cprot @ cf))
    ps = int(np.argmax(sprot @ sf))
    return pc, ps


def _classify_scene_incr(objs, rng, store, cprot, sprot):
    canvas, starts = render_scene(objs, rng)
    return [classify_window_incr(_window(canvas, x0), store, cprot, sprot) for x0 in starts]


def front_end_accuracy_incr(store, rng, n=180):
    cprot = store.color_protos()
    sprot = store.shape_protos()
    cc = 0
    sc = 0
    for _ in range(n):
        ci = int(rng.integers(0, C))
        si = int(rng.integers(0, S))
        w = render_object(ci, si, rng)
        pc, ps = classify_window_incr(w, store, cprot, sprot)
        cc += int(pc == ci)
        sc += int(ps == si)
    return cc / n, sc / n


def _render_scenes_incr(M, n, store, seed_base):
    cprot = store.color_protos()
    sprot = store.shape_protos()
    srng = np.random.default_rng(seed_base)
    scenes = []
    for _ in range(n):
        objs = sample_scene(M, srng, force_share=True)
        preds = _classify_scene_incr(objs, srng, store, cprot, sprot)
        scenes.append((objs, preds))
    return scenes


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------
def run_seed(seed, cfg):
    rng = np.random.default_rng(seed + 90210)
    N = cfg["N"]
    color_code = make_fhrr_codes(C, N, rng)
    shape_code = make_fhrr_codes(S, N, rng)
    Mp = cfg["M_primary"]

    # --- EXPOSURE CURVE: incremental front-end at increasing exposures-per-class; eval ATTN at M_primary ---
    curve_ill = {}
    curve_cos = {}
    front_acc_by_e = {}
    stores = {}
    for e in cfg["expo_curve"]:
        st = train_incremental(e, np.random.default_rng(seed + 500 + e))
        stores[e] = st
        front_acc_by_e[e] = front_end_accuracy_incr(st, np.random.default_rng(seed + 600 + e))
        scenes = _render_scenes_incr(Mp, cfg["n_scenes"] // 2, st, seed + 700 + e)
        ill, _, cos, _ = eval_arm_on_scenes(scenes, color_code, shape_code, "ATTN",
                                            np.random.default_rng(seed + 800 + e), cfg["n_query"])
        curve_ill[e] = ill
        curve_cos[e] = cos

    e_max = max(cfg["expo_curve"])
    store = stores[e_max]

    # --- label-shuffle must-fail (front-end at e_max but permuted labels) ---
    store_shuf = train_incremental(e_max, np.random.default_rng(seed + 1234), shuffle_labels=True)
    scenes_shuf = _render_scenes_incr(Mp, cfg["n_scenes"] // 2, store_shuf, seed + 1300)
    shuf_ill, _, shuf_cos, _ = eval_arm_on_scenes(scenes_shuf, color_code, shape_code, "ATTN",
                                                  np.random.default_rng(seed + 1400), cfg["n_query"])

    # --- main comparison at each scale M: ATTN vs FLAT vs SCRAM on HARD feature-sharing scenes (e_max) ---
    by_M = {}
    for M in cfg["M_list"]:
        scenes_hard = _render_scenes_incr(M, cfg["n_scenes"], store, seed + 2000 + M)
        arms = {}
        for arm in ("ATTN", "FLAT", "SCRAM"):
            off = {"ATTN": 0, "FLAT": 11, "SCRAM": 22}[arm]
            ill, illn, cos, cosn = eval_arm_on_scenes(
                scenes_hard, color_code, shape_code, arm,
                np.random.default_rng(seed + 3000 + M + off), cfg["n_query"])
            arms[arm] = dict(illusory_2afc=ill, illusory_n=illn, color_of_shape=cos, color_of_shape_n=cosn)
        by_M[M] = arms

    # --- ARMS-MUST-DIFFER (inherited): scene reps of the three arms must bit-differ ---
    dbg_objs = sample_scene(max(cfg["M_list"]), np.random.default_rng(seed + 424242), force_share=True)
    dbg_preds = _classify_scene_incr(dbg_objs, np.random.default_rng(seed + 424243), store,
                                     store.color_protos(), store.shape_protos())
    reps = {}
    for arm in ("ATTN", "FLAT", "SCRAM"):
        rep = encode_scene(dbg_preds, color_code, shape_code, arm, np.random.default_rng(seed + 55))
        reps[arm] = hashlib.sha256(np.ascontiguousarray(rep).tobytes()).hexdigest()
    assert reps["ATTN"] != reps["FLAT"], "ARMS-DIFFER: ATTN == FLAT scene rep"
    assert reps["ATTN"] != reps["SCRAM"], "ARMS-DIFFER: ATTN == SCRAM scene rep"

    return dict(seed=seed, N=N, M_primary=Mp,
                curve_illusory={str(k): curve_ill[k] for k in curve_ill},
                curve_color_of_shape={str(k): curve_cos[k] for k in curve_cos},
                front_acc_by_e={str(k): front_acc_by_e[k] for k in front_acc_by_e},
                label_shuffle=dict(illusory_2afc=shuf_ill, color_of_shape=shuf_cos),
                by_M={str(M): by_M[M] for M in by_M},
                free_novel_conjunction=novel_conjunction_free(color_code, shape_code),
                rep_digests=reps)


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def _mean(vals):
    a = np.array([v for v in vals if v is not None and v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _seed_avg_curve(per_seed, key, grid):
    return [_mean([m[key][str(e)] for m in per_seed]) for e in grid]


def _is_monotonic(curve, tol):
    return all((curve[i + 1] >= curve[i] - tol) for i in range(len(curve) - 1))


def aggregate_and_verdict(per_seed, cfg):
    Mp = cfg["M_primary"]
    grid = cfg["expo_curve"]
    e_min = grid[0]
    e_max = grid[-1]

    attn_ill = _mean([m["by_M"][str(Mp)]["ATTN"]["illusory_2afc"] for m in per_seed])
    flat_ill = _mean([m["by_M"][str(Mp)]["FLAT"]["illusory_2afc"] for m in per_seed])
    scram_ill = _mean([m["by_M"][str(Mp)]["SCRAM"]["illusory_2afc"] for m in per_seed])
    attn_cos = _mean([m["by_M"][str(Mp)]["ATTN"]["color_of_shape"] for m in per_seed])
    flat_cos = _mean([m["by_M"][str(Mp)]["FLAT"]["color_of_shape"] for m in per_seed])
    margin = attn_ill - flat_ill

    ill_curve = _seed_avg_curve(per_seed, "curve_illusory", grid)
    cos_curve = _seed_avg_curve(per_seed, "curve_color_of_shape", grid)
    ill_rise = ill_curve[-1] - ill_curve[0]
    cos_rise = cos_curve[-1] - cos_curve[0]
    ill_mono = _is_monotonic(ill_curve, CURVE_MONO_TOL)
    cos_mono = _is_monotonic(cos_curve, CURVE_MONO_TOL)
    curve_ok = (ill_rise >= CURVE_RISE_HP) and ill_mono

    fa_c = _mean([m["front_acc_by_e"][str(e_max)][0] for m in per_seed])
    fa_s = _mean([m["front_acc_by_e"][str(e_max)][1] for m in per_seed])
    front_ok = (fa_c >= FRONT_ACC_MIN and fa_s >= FRONT_ACC_MIN)

    shuf_ill = _mean([m["label_shuffle"]["illusory_2afc"] for m in per_seed])
    shuf_cos = _mean([m["label_shuffle"]["color_of_shape"] for m in per_seed])
    label_shuffle_collapsed = shuf_ill <= LABEL_SHUFFLE_MAX

    free_gen = _mean([m["free_novel_conjunction"] for m in per_seed])

    scale = {}
    for M in cfg["M_list"]:
        scale[str(M)] = dict(
            attn_ill=_mean([m["by_M"][str(M)]["ATTN"]["illusory_2afc"] for m in per_seed]),
            flat_ill=_mean([m["by_M"][str(M)]["FLAT"]["illusory_2afc"] for m in per_seed]),
            attn_cos=_mean([m["by_M"][str(M)]["ATTN"]["color_of_shape"] for m in per_seed]))

    flat_in_band = flat_ill <= ILL_FLAT_MAX
    scramble_collapsed = scram_ill <= ILL_SCRAMBLE_MAX
    binding_win = (attn_ill >= ILL_HP and margin >= ILL_MARGIN_HP and scramble_collapsed)

    if not front_ok:
        verdict = "HARD_FAIL_FRONT_END_DEGENERATE"
    elif not flat_in_band:
        verdict = "INCONCLUSIVE_FLAT_NOT_AT_CHANCE"
    elif not label_shuffle_collapsed:
        verdict = "INCONCLUSIVE_FRONT_END_NOT_LEARNED"
    elif binding_win and curve_ok:
        verdict = "HARD_PASS_IMPROVING_EXPOSURE_CURVE"
    elif attn_ill <= ILL_HF:
        verdict = "HARD_FAIL_BINDING_WIN_BROKEN_BY_SWAP"
    elif binding_win and not curve_ok:
        verdict = "MIDDLE_BAND_SATURATES_MM_STANDS"  # binding win preserved but curve too flat / non-mono
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s || EXPOSURE-CURVE ATTN illusory-2AFC @M=%d (e=%s)=%s rise(e%d->e%d)=%.3f mono=%s "
        "(HP: rise>=%.2f & mono) || color-of-shape curve=%s rise=%.3f mono=%s || "
        "BINDING-WIN @M=%d,e_max: ATTN=%.3f FLAT=%.3f SCRAM=%.3f margin=%.3f (win=%s) || "
        "LABEL-SHUFFLE ATTN illusory=%.3f cos=%.3f (collapse<=%.2f) || "
        "FRONT-END@e_max(color=%.3f shape=%.3f floor=%.2f ok=%s) || flat_in_band=%s scramble_collapsed=%s "
        "|| SCALE(ATTN illusory by M)=%s || FREE-BY-CONSTRUCTION novel-conj=%.3f (un-gated)" % (
            verdict, Mp, grid, [round(x, 3) for x in ill_curve], e_min, e_max, ill_rise, ill_mono,
            CURVE_RISE_HP, [round(x, 3) for x in cos_curve], cos_rise, cos_mono,
            Mp, attn_ill, flat_ill, scram_ill, margin, binding_win,
            shuf_ill, shuf_cos, LABEL_SHUFFLE_MAX, fa_c, fa_s, FRONT_ACC_MIN, front_ok,
            flat_in_band, scramble_collapsed,
            {M: round(scale[str(M)]["attn_ill"], 3) for M in cfg["M_list"]}, free_gen))

    gates = dict(
        attn_illusory_2afc=attn_ill, flat_illusory_2afc=flat_ill, scram_illusory_2afc=scram_ill,
        illusory_margin=margin, attn_color_of_shape=attn_cos, flat_color_of_shape=flat_cos,
        exposure_grid=grid, ill_curve=ill_curve, cos_curve=cos_curve,
        ill_curve_rise=ill_rise, cos_curve_rise=cos_rise, ill_curve_mono=ill_mono, cos_curve_mono=cos_mono,
        curve_ok=curve_ok, binding_win=binding_win,
        front_color_acc=fa_c, front_shape_acc=fa_s, front_end_ok=front_ok,
        label_shuffle_illusory=shuf_ill, label_shuffle_cos=shuf_cos,
        label_shuffle_collapsed=label_shuffle_collapsed,
        flat_in_band=flat_in_band, scramble_collapsed=scramble_collapsed,
        free_novel_conjunction=free_gen, scale=scale,
        bands=dict(ILL_HP=ILL_HP, ILL_FLAT_MAX=ILL_FLAT_MAX, ILL_MARGIN_HP=ILL_MARGIN_HP,
                   ILL_SCRAMBLE_MAX=ILL_SCRAMBLE_MAX, CURVE_RISE_HP=CURVE_RISE_HP,
                   CURVE_MONO_TOL=CURVE_MONO_TOL, LABEL_SHUFFLE_MAX=LABEL_SHUFFLE_MAX,
                   FRONT_ACC_MIN=FRONT_ACC_MIN, ILL_HF=ILL_HF))
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs).
#   Asserts the MACHINERY: front-end classification IMPROVES with exposure (running mean denoises);
#   the binding win FIRES (ATTN>>FLAT); label-shuffle + scramble collapse. Does NOT gate on the
#   >= 0.06 downstream RISE magnitude (that is the empirical question; MIDDLE must stay reachable).
# ---------------------------------------------------------------------------
def discriminator_selftest():
    rng = np.random.default_rng(0)
    res = {}
    try:
        import torch
        from hdlab.binding import bind as hb, unbind as hu
        a = make_fhrr_codes(1, 128, rng)[0]
        b = make_fhrr_codes(1, 128, rng)[0]
        rb = hb(torch.from_numpy(a), torch.from_numpy(b)).numpy()
        ru = hu(torch.from_numpy(a), torch.from_numpy(b)).numpy()
        reuse_ok = bool(np.allclose(rb, G0.fhrr_bind(a, b), atol=1e-4)
                        and np.allclose(ru, G0.fhrr_unbind(a, b), atol=1e-4))
    except Exception as e:  # noqa: BLE001  (self-test diagnostic only)
        reuse_ok = False
        res["reuse_err"] = str(e)[:200]

    N = 768
    crng = np.random.default_rng(3)
    color_code = make_fhrr_codes(C, N, crng)
    shape_code = make_fhrr_codes(S, N, crng)

    # MACHINERY: incremental front-end classification improves with exposure (running mean denoises)
    st1 = train_incremental(1, np.random.default_rng(11))
    st16 = train_incremental(16, np.random.default_rng(12))
    fa_c1, fa_s1 = front_end_accuracy_incr(st1, np.random.default_rng(13))
    fa_c16, fa_s16 = front_end_accuracy_incr(st16, np.random.default_rng(14))
    front_learns = (fa_c16 >= FRONT_ACC_MIN and fa_s16 >= FRONT_ACC_MIN
                    and (fa_c16 - fa_c1) + (fa_s16 - fa_s1) >= 0.05)

    sc1 = _render_scenes_incr(4, 100, st1, 21)
    sc16 = _render_scenes_incr(4, 100, st16, 22)
    ill1, _, cos1, _ = eval_arm_on_scenes(sc1, color_code, shape_code, "ATTN", np.random.default_rng(31), 4)
    ill16, _, cos16, _ = eval_arm_on_scenes(sc16, color_code, shape_code, "ATTN", np.random.default_rng(32), 4)

    # BINDING WIN FIRES: ATTN illusory-2AFC >> FLAT (~chance) on HARD feature-sharing scenes at e=16
    flat16, _, _, _ = eval_arm_on_scenes(sc16, color_code, shape_code, "FLAT", np.random.default_rng(33), 4)
    scram16, _, _, _ = eval_arm_on_scenes(sc16, color_code, shape_code, "SCRAM", np.random.default_rng(34), 4)
    fires = (ill16 >= ILL_HP and flat16 <= ILL_FLAT_MAX and (ill16 - flat16) >= ILL_MARGIN_HP)

    # TELEMETRY-SENSITIVE (measurable exposure axis, direction only; magnitude NOT gated):
    # degrading the front-end (e=1 vs e=16) must not INCREASE downstream binding.
    telemetry = (ill16 - ill1) >= -0.01

    # LABEL-SHUFFLE must-fail
    st_shuf = train_incremental(16, np.random.default_rng(41), shuffle_labels=True)
    sc_shuf = _render_scenes_incr(4, 100, st_shuf, 23)
    ill_shuf, _, cos_shuf, _ = eval_arm_on_scenes(sc_shuf, color_code, shape_code, "ATTN",
                                                  np.random.default_rng(42), 4)
    label_shuffle_collapses = (ill16 - ill_shuf) > 0.12 and ill_shuf <= LABEL_SHUFFLE_MAX

    # SCRAMBLE collapses (attention localization load-bearing)
    scramble_collapses = (ill16 - scram16) > 0.10

    ok = bool(reuse_ok and front_learns and fires and telemetry
              and label_shuffle_collapses and scramble_collapses)
    res.update(dict(reuse_ok=reuse_ok, front_learns=bool(front_learns),
                    fa_c1=float(fa_c1), fa_s1=float(fa_s1), fa_c16=float(fa_c16), fa_s16=float(fa_s16),
                    cos1=float(cos1), cos16=float(cos16),
                    attn_ill1=float(ill1), attn_ill16=float(ill16), flat_ill16=float(flat16),
                    scram_ill16=float(scram16), label_shuffle_ill=float(ill_shuf),
                    fires=bool(fires), telemetry=bool(telemetry),
                    label_shuffle_collapses=bool(label_shuffle_collapses),
                    scramble_collapses=bool(scramble_collapses)))
    return ok, res


# ---------------------------------------------------------------------------
# metrics IO
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    os.makedirs(output_dir, exist_ok=True)
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=G0._json_default)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED",
                verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__),
                elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _atomic_write_metrics(output_dir, diag)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(OUTPUT_DIR, run_mode, expected_n_units)
    t_start = time.perf_counter()

    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        _atomic_write_metrics(OUTPUT_DIR, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED: %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            anchor_name=ANCHOR_NAME, discriminator_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        _atomic_write_metrics(OUTPUT_DIR, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS front-end-learns + binding-fires + telemetry + label-shuffle + scramble-collapse",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            anchor_name=ANCHOR_NAME, discriminator_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, cfg)
            per_seed.append(pm)
            _log("seed=%d curve_ill=%s | ATTN@M%d=%.3f FLAT=%.3f SCRAM=%.3f | shuf=%.3f | fa=%s" % (
                seed, pm["curve_illusory"], cfg["M_primary"],
                pm["by_M"][str(cfg["M_primary"])]["ATTN"]["illusory_2afc"],
                pm["by_M"][str(cfg["M_primary"])]["FLAT"]["illusory_2afc"],
                pm["by_M"][str(cfg["M_primary"])]["SCRAM"]["illusory_2afc"],
                pm["label_shuffle"]["illusory_2afc"],
                pm["front_acc_by_e"][str(max(cfg["expo_curve"]))]))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # per-seed failure-class instrumentation
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        _atomic_write_metrics(OUTPUT_DIR, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (
                expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            anchor_name=ANCHOR_NAME, seed_failures=seed_failures))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, cfg)
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg, gates=gates,
        discriminator_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed)
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
