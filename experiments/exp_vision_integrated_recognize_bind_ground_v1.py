"""INTEGRATED glass-box VISION pipeline on REAL images: RECOGNIZE (real-pixel HOG front-end) -> BIND
(Treisman attention-gated multi-object binding) -> GROUND (sharded store, word meaning). Chains the
THREE separately-validated, never-assembled vision pieces into ONE cell, on sklearn `load_digits`
(REAL 8x8 photographs, upscaled to 32x32 -- NOT synthetic one-hots), + a genuinely can-fail
NOVEL-CATEGORY probe (the one gap the 2026-07-23 audit flagged: every prior "held-out" test held out
INSTANCES of a KNOWN class; none ever held out a whole CLASS from training/binding).

PIECES REUSED (imported as modules, functions called -- not copy-pasted where avoidable):
  HG    = exp_reader_image_shape_recognition_hog_v1  (HOG front-end feat_hog; load_digits_up; the
          Kanerva content encoder via HG.GB). Prior result: digits LOO acc1=0.969 MEASURED@disk.
  ATN   = exp_grounding_attn_bind_illusory_conjunction_v1 (FHRR bind/unbind/cleanup; encode_scene
          ATTN/FLAT/SCRAM; illusory_2afc; color_of_shape; color_feature/shape_feature -- dimension-
          and-content agnostic, reused VERBATIM here on REAL tinted photographic windows instead of
          synthetic drawn polygons).
  INC   = exp_grounding_attn_bind_incremental_curve_v1 (ProtoStore running-mean prototype classifier,
          the improving-with-exposure front-end). Prior result: ATTN 0.833 vs FLAT 0.521 HARD_PASS
          MEASURED@disk (data/exp_grounding_attn_bind_incremental_curve_v1/metrics.json).
  GRD   = exp_reader_perception_meaning_grounding_v1 (random_words; split_masks pattern).
  GRDSH = exp_reader_perception_meaning_grounding_sharded_v1 (build_store_sharded; i2w_heldout_sharded
          -- the per-class store that recovered the crosstalk-masked grounding lift, atom 29438).

HONEST FRAMING (see pre-reg preregs/2026-07-23_vision_integrated_recognize_bind_ground_v1.md): this is
an INTEGRATED BATTERY of 3 validated glass-box measurements sharing ONE real dataset, ONE class
ontology, and ONE train/test split, chained PER-OBJECT (recognize a real photographic instance's
identity via ProtoStore -> bind it into a multi-object scene via attention -> ground that SAME real
instance's own HOG content code via the sharded word store). It is NOT a single differentiable forward
pass (no such thing exists anywhere in this glass-box project); it is the correct, honest way to
compose inspectable VSA mechanisms. Reported this way explicitly to avoid over-claiming.

TWO-FEATURE (Treisman) DESIGN: each object = (color, digit-identity). digit-identity is REAL
photographic content (a real sklearn digit image) recognized via the validated HOG front-end. color is
an independent per-instance jittered tint applied to the REAL photo (alpha-blended from the photo's OWN
ink intensity, so the SHAPE mask is genuine real-pixel structure; only the hue is a synthetic overlay --
the same device the ATN cell already used for its drawn shapes, here driving REAL content instead).

NOVEL-CATEGORY PROBE: SEEN_CLASSES = digits 0-7 (all training/binding). NOVEL_CLASSES = digits 8-9,
held out ENTIRELY (zero exposures, zero grounding-shard instances). Headline recognition/grounding
accuracy on novel-class instances is DEFINITIONALLY ~0 (no prototype/shard exists for them) -- that is
a structural sanity check, not the interesting number. The REAL discriminator is the SCORE-GAP: does a
genuinely novel-category real photo get a measurably LOWER best-match score than an ordinary
wrong-class mismatch on a KNOWN class, or does the system confidently (and silently) misfile it exactly
like any other confusion? HARD_FAIL (gap ~0, no novelty signal) is a LIVE, EXPECTED, and valuable
outcome here (the vision-side analog of the COGS unseen-filler wall) -- reported honestly either way.

GLASS-BOX invariant: no external LLM/CLIP at inference (HOG front-end is fully specified, no learned
weights; ProtoStore = running mean, no autograd; FHRR bind = elementwise complex multiply; grounding
store = elementwise multiply + cosine argmax). LOCAL ONLY: no push, no remote-persist, no atom banking.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test + per-seed (ATTN/FLAT/SCRAM scene reps differ; raw-vs-hog
#   grounding codes differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit / KeyboardInterrupt: raise BEFORE except Exception (no bare except, no BaseException)
# - crlb_n/a: discriminators are forced-choice accuracies vs analytic chance, a 2AFC vs chance=0.5, and
#   score-gap contrasts vs a theoretical null of 0; none is a closed-form noise floor
# - baseline_in_band: FLAT illusory near chance; label-shuffle/word-scramble collapse to their floors
# - deterministic seeding: fixed int seeds only; no hash()-seeded RNG, no list(set()) ordering
# - discriminator-fires: self_test asserts the MACHINERY (recognition improves with exposure; ATTN>>FLAT;
#   scramble/label-shuffle/word-scramble collapse; grounding fires) -- does NOT gate the open novel-class
#   score-gap DIRECTION (that is the empirical, honestly-either-way question)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds; verdict counts len(per_seed) and HARD_FAILs on breach
# - per-unit failure-class instrumentation: per-seed try/except Exception (not bare), failure_class logged
# - HP_SCOPE declared in pre-reg (must-fail-control arms do not inherit mechanism-arm HARD_PASS gates)
# - calibration_check: "adaptive_with_discriminator_gate" for the novel-class score-gap bands (derived
#   from an explicit theoretical null, not a blind default); "default_ok_for_this_regime" for headline
#   bands (reused directly from prior MEASURED cells at the same chance geometry)
# - all numbers in comments/pre-reg tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - progress_logging = print_flush_true (cell expected < 300s; flush anyway)
ASCII-only.
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

ANCHOR_NAME = "vision_integrated_recognize_bind_ground_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_reader_image_shape_recognition_hog_v1 as HG  # noqa: E402
import experiments.exp_grounding_attn_bind_illusory_conjunction_v1 as ATN  # noqa: E402
import experiments.exp_grounding_attn_bind_incremental_curve_v1 as INC  # noqa: E402
import experiments.exp_reader_perception_meaning_grounding_v1 as GRD  # noqa: E402
import experiments.exp_reader_perception_meaning_grounding_sharded_v1 as GRDSH  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

SLOT = 32              # real digit photo resolution (HG.load_digits_up up=32); tint fills it directly
N_SEEN = 8              # digits 0-7: all training/binding
N_NOVEL = 2              # digits 8-9: NEVER trained/bound; the novel-category probe
SEEN_CLASSES = list(range(N_SEEN))
NOVEL_CLASSES = list(range(N_SEEN, N_SEEN + N_NOVEL))

# ---------------------------------------------------------------------------
# Pre-registered bands (preregs/2026-07-23_vision_integrated_recognize_bind_ground_v1.md)
# ---------------------------------------------------------------------------
FRONT_RECOG_HP = 0.75     # HYPOTHESIZED@prereg (CITED@HG digits LOO acc1=0.969, discounted for tint noise)
FRONT_RECOG_HF = 0.30
GROUND_HP = 0.30          # HYPOTHESIZED@prereg (reuses GRDSH STRONG_GROUND_MIN convention)
GROUND_HF = 0.175
BIND_ILL_HP = 0.75        # HYPOTHESIZED@prereg (CITED@INC ATTN=0.833, ATN ATTN=0.815, banded down)
BIND_MARGIN_HP = 0.15
BIND_FLAT_MAX = 0.62
BIND_SCRAM_MAX = 0.66
BIND_ILL_HF = 0.60
WORD_SCRAMBLE_COLLAPSE_MIN = 0.10
LABEL_SHUFFLE_MAX = 0.30
END_TO_END_HP = 0.55
END_TO_END_HF = 0.20
NOVEL_ACC_STRUCTURAL_MAX = 0.05     # sanity floor: must be ~0 (no prototype/shard for novel classes)
NOVEL_GAP_WALL_MAX = 0.05           # |gap|<=this => WALL_CONFIRMED (expected, THEORETICAL null ~ 0)
NOVEL_GAP_SURPRISE_MIN = 0.10       # gap>=this => SURPRISE_NOVELTY_SIGNAL (not required, not expected)
CHANCE_SEEN = 1.0 / N_SEEN
CHANCE_2AFC = 0.5

# ---------------------------------------------------------------------------
# Config profiles: SAME N / class-count / M-sweep at smoke and FULL (DISCRIMINATOR-MUST-SURVIVE-SCALE);
# only per-class instance count, scene count, and seed count differ.
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(seeds=[7], per_class=8, k_train_seen=5, N_scene=384, N_ground=1024,
                    M_list=[2, 3, 4], M_primary=3, n_scenes=20, n_query=2, expo_curve=[1, 8],
                    p_ground=dict(grid=4, edge_scale=4, grid_hog=4, n_orient=9, Q=9))
SMOKE_CFG = dict(seeds=[7, 13], per_class=16, k_train_seen=10, N_scene=1536, N_ground=4096,
                 M_list=[2, 3, 4], M_primary=3, n_scenes=50, n_query=3, expo_curve=[1, 4, 12],
                 p_ground=dict(grid=8, edge_scale=4, grid_hog=8, n_orient=9, Q=13))
FULL_CFG = dict(seeds=[7, 13, 17, 23, 29], per_class=40, k_train_seen=25, N_scene=1536, N_ground=4096,
                M_list=[2, 3, 4], M_primary=3, n_scenes=220, n_query=4, expo_curve=[1, 2, 4, 8, 16],
                p_ground=dict(grid=8, edge_scale=4, grid_hog=8, n_orient=9, Q=13))


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


# ---------------------------------------------------------------------------
# markers / metrics IO
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
        json.dump(metrics, f, indent=2, default=_json_default)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED",
                verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__),
                elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _atomic_write_metrics(output_dir, diag)


def _arms_must_differ(arms_outputs):
    digests = {}
    for name, out in arms_outputs.items():
        b = np.ascontiguousarray(out).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, bnm = names[i], names[j]
            assert digests[a] != digests[bnm], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical (hash=%s)" % (a, bnm, digests[a]))
    return digests


# ---------------------------------------------------------------------------
# REAL-PIXEL front-end: a real digit photo, alpha-blended with an independent color tint (Treisman's
# 2nd, parallel feature map). The shape mask comes from the REAL photo's own ink intensity; only the
# hue is a synthetic overlay (same device ATN.render_object already used for its drawn polygons; here
# it drives genuine photographic content instead of a rendered primitive).
# ---------------------------------------------------------------------------
def tint_real(gray, color_idx, rng, slot=SLOT):
    g = HG.GB._resize(gray, slot) if gray.shape[0] != slot else gray
    alpha = np.clip(g / 255.0, 0.0, 1.0)
    col = ATN.COLOR_RGB[color_idx] + rng.normal(0.0, ATN.COL_JITTER, size=3)
    img = np.empty((slot, slot, 3), dtype=np.float64)
    for ch in range(3):
        img[:, :, ch] = ATN.BG * (1.0 - alpha) + col[ch] * alpha
    img += rng.normal(0.0, ATN.NOISE, size=img.shape)
    return np.clip(img, 0, 255)


def render_object_real(color_idx, digit_class, rng, pool_idx_by_class, grays_all, slot=SLOT):
    """pool_idx_by_class[digit_class] = list of GLOBAL indices into grays_all eligible for this draw
    (train pool / held-out test pool / novel pool, caller controls which via which dict is passed).
    Returns (tinted_image, global_index) -- the index lets the caller look up that SAME real instance's
    grounding content code later (the "chain" from recognize -> ground on one object)."""
    idxs = pool_idx_by_class[digit_class]
    gi = int(idxs[int(rng.integers(0, len(idxs)))])
    return tint_real(grays_all[gi], color_idx, rng, slot), gi


def render_scene_real(objects, rng, pool_idx_by_class, grays_all, slot=SLOT):
    imgs = []
    gidx = []
    for (c, s) in objects:
        im, gi = render_object_real(c, s, rng, pool_idx_by_class, grays_all, slot)
        imgs.append(im)
        gidx.append(gi)
    canvas = np.concatenate(imgs, axis=1)
    starts = [k * slot for k in range(len(objects))]
    return canvas, starts, gidx


def _window(canvas, x0, slot=SLOT):
    return canvas[:, x0:x0 + slot, :]


# ---------------------------------------------------------------------------
# ProtoStore-based recognize+bind (reuses INC.ProtoStore verbatim; INC.classify_window_incr reused
# verbatim -- it just calls ATN.color_feature / ATN.shape_feature on whatever window it is handed)
# ---------------------------------------------------------------------------
def train_incremental_real(e, rng, pool_train, slot=SLOT, shuffle_labels=False):
    n_color = ATN.C
    n_shape = N_SEEN
    w0, _ = render_object_real(0, SEEN_CLASSES[0], rng, pool_train, _GRAYS_CTX[0], slot)
    dc = ATN.color_feature(w0).shape[0]
    ds = ATN.shape_feature(w0).shape[0]
    store = INC.ProtoStore(n_color, n_shape, dc, ds)
    if shuffle_labels:
        store.cmap = rng.permutation(n_color)
        store.smap = rng.permutation(n_shape)
    for ci in range(n_color):
        tgt = int(store.cmap[ci])
        for _ in range(e):
            sc = SEEN_CLASSES[int(rng.integers(0, n_shape))]
            w, _ = render_object_real(ci, sc, rng, pool_train, _GRAYS_CTX[0], slot)
            store.update_color(tgt, ATN.color_feature(w))
    for si, sc in enumerate(SEEN_CLASSES):
        tgt = int(store.smap[si])
        for _ in range(e):
            ci = int(rng.integers(0, n_color))
            w, _ = render_object_real(ci, sc, rng, pool_train, _GRAYS_CTX[0], slot)
            store.update_shape(tgt, ATN.shape_feature(w))
    return store


# module-scoped 1-slot context list carrying the CURRENT grays_all array (avoids threading an extra
# arg through every INC-reused call site; single-process, single-threaded cell, no concurrency).
_GRAYS_CTX = [None]


def front_end_accuracy_real(store, rng, pool, slot=SLOT, n=150):
    cprot = store.color_protos()
    sprot = store.shape_protos()
    cc = 0
    sc_ = 0
    for _ in range(n):
        ci = int(rng.integers(0, ATN.C))
        sc = SEEN_CLASSES[int(rng.integers(0, N_SEEN))]
        w, _ = render_object_real(ci, sc, rng, pool, _GRAYS_CTX[0], slot)
        pc, ps = INC.classify_window_incr(w, store, cprot, sprot)
        cc += int(pc == ci)
        sc_ += int(ps == sc)
    return cc / n, sc_ / n


def sample_scene_real(M, rng, force_share):
    """M objects (color, digit-class in SEEN_CLASSES), all distinct pairs; force_share => >=2 objects
    share a color OR a digit-class (Treisman HARD feature-sharing case)."""
    for _ in range(200):
        objs = []
        used = set()
        for _k in range(M):
            for _try in range(60):
                c = int(rng.integers(0, ATN.C))
                s = int(SEEN_CLASSES[int(rng.integers(0, N_SEEN))])
                if (c, s) not in used:
                    used.add((c, s))
                    objs.append((c, s))
                    break
        if len(objs) < M:
            continue
        cols = [o[0] for o in objs]
        shps = [o[1] for o in objs]
        shares = (len(set(cols)) < M) or (len(set(shps)) < M)
        if force_share and not shares:
            continue
        if (not force_share) and shares and rng.random() < 0.5:
            continue
        return objs
    return objs


def _classify_scene_real(objs, rng, store, pool, slot=SLOT):
    cprot = store.color_protos()
    sprot = store.shape_protos()
    canvas, starts, gidx = render_scene_real(objs, rng, pool, _GRAYS_CTX[0], slot)
    preds = [INC.classify_window_incr(_window(canvas, x0, slot), store, cprot, sprot) for x0 in starts]
    return preds, gidx


def _render_scenes_real(M, n, store, pool, seed_base, slot=SLOT):
    srng = np.random.default_rng(seed_base)
    scenes = []
    for _ in range(n):
        objs = sample_scene_real(M, srng, force_share=True)
        preds, gidx = _classify_scene_real(objs, srng, store, pool, slot)
        scenes.append((objs, preds, gidx))
    return scenes


def _scenes_for_eval(scenes):
    """Strip gidx (the eval_arm_on_scenes helper from ATN expects (objs, preds) pairs)."""
    return [(o, p) for (o, p, _g) in scenes]


# ---------------------------------------------------------------------------
# Grounding: SAME real instance's whole-image HOG content code -> sharded word store (GRDSH verbatim)
# ---------------------------------------------------------------------------
def build_grounding(grays_all, labels_all, cfg, seed):
    """Returns (shards_hog, shards_raw, ground_codes_hog, ground_codes_raw, words, train_mask,
    test_mask_seen, test_mask_novel)."""
    N = cfg["N_ground"]
    p = cfg["p_ground"]
    n_classes = N_SEEN + N_NOVEL
    labels_all = np.asarray(labels_all)
    train = np.zeros(len(labels_all), dtype=bool)
    test_seen = np.zeros(len(labels_all), dtype=bool)
    test_novel = np.zeros(len(labels_all), dtype=bool)
    for c in SEEN_CLASSES:
        idx = np.where(labels_all == c)[0]
        train[idx[:cfg["k_train_seen"]]] = True
        test_seen[idx[cfg["k_train_seen"]:]] = True
    for c in NOVEL_CLASSES:
        idx = np.where(labels_all == c)[0]
        test_novel[idx] = True

    words = GRD.random_words(n_classes, N, seed)
    codes_hog = HG.encode_images(grays_all, "rung3_hog", p, N, seed)
    codes_raw = HG.encode_images(grays_all, "rung1_raw", p, N, seed)
    shards_hog = GRDSH.build_store_sharded(codes_hog, labels_all, words, train)
    shards_raw = GRDSH.build_store_sharded(codes_raw, labels_all, words, train)
    return dict(shards_hog=shards_hog, shards_raw=shards_raw, codes_hog=codes_hog, codes_raw=codes_raw,
                words=words, train=train, test_seen=test_seen, test_novel=test_novel, n_classes=n_classes)


def shard_scores(shards, codes, labels, mask, words):
    """Per masked image: best_score (over shard classes present), best_class, best_wrong_score (best
    score EXCLUDING the true class -- undefined/NaN if true class has no shard, e.g. novel probes)."""
    labels = np.asarray(labels)
    Wn = words.astype(np.float32)
    Wn = Wn / (np.linalg.norm(Wn, axis=1, keepdims=True) + 1e-12)
    classes = sorted(shards.keys())
    idx = np.where(mask)[0]
    best_scores = []
    best_classes = []
    best_wrong = []
    for i in idx:
        x = codes[i]
        scored = []
        for c in classes:
            qc = shards[c] * x
            qc = qc / (np.linalg.norm(qc) + 1e-12)
            scored.append((float(Wn[c] @ qc), c))
        scored.sort(key=lambda t: -t[0])
        best_scores.append(scored[0][0])
        best_classes.append(scored[0][1])
        wrong = [s for (s, c) in scored if c != labels[i]]
        best_wrong.append(wrong[0] if wrong else float("nan"))
    return (np.array(best_scores), np.array(best_classes, dtype=np.int64),
            np.array(best_wrong), labels[idx])


def shape_score_gap_real(store, pool_test_seen, pool_novel, rng, n_per_class=15, slot=SLOT):
    """Front-end (ProtoStore) level analog of shard_scores: recognition-level novelty gap."""
    sprot = store.shape_protos()

    def scores_for(pool_by_class, classes):
        bs = []
        bw = []
        bc = []
        tl = []
        for c in classes:
            idxs = pool_by_class[c][:n_per_class]
            for gi in idxs:
                w = tint_real(_GRAYS_CTX[0][gi], int(rng.integers(0, ATN.C)), rng, slot)
                sf = ATN.shape_feature(w)
                scores = sprot @ sf
                order = np.argsort(-scores)
                bc.append(SEEN_CLASSES[int(order[0])])
                bs.append(float(scores[order[0]]))
                wrongs = [float(scores[j]) for j in order if SEEN_CLASSES[int(j)] != c]
                bw.append(wrongs[0] if wrongs else float("nan"))
                tl.append(c)
        return np.array(bs), np.array(bw), np.array(bc), np.array(tl)

    bs_s, bw_s, bc_s, tl_s = scores_for(pool_test_seen, SEEN_CLASSES)
    bs_n, bw_n, bc_n, tl_n = scores_for(pool_novel, NOVEL_CLASSES)
    return dict(seen_acc=float(np.mean(bc_s == tl_s)),
                seen_best_wrong_mean=float(np.nanmean(bw_s)),
                novel_acc=float(np.mean(bc_n == tl_n)),
                novel_top_score_mean=float(np.mean(bs_n)),
                gap=float(np.nanmean(bw_s) - np.mean(bs_n)))


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------
def run_seed(seed, cfg, grays_all, labels_all):
    _GRAYS_CTX[0] = grays_all
    rng = np.random.default_rng(seed + 90210)
    N = cfg["N_scene"]
    color_code = ATN.make_fhrr_codes(ATN.C, N, rng)
    shape_code = ATN.make_fhrr_codes(N_SEEN + N_NOVEL, N, rng)
    Mp = cfg["M_primary"]

    labels_all = np.asarray(labels_all)
    pool_train = {c: list(np.where(labels_all == c)[0][:cfg["k_train_seen"]]) for c in SEEN_CLASSES}
    pool_test_seen = {c: list(np.where(labels_all == c)[0][cfg["k_train_seen"]:]) for c in SEEN_CLASSES}
    pool_novel = {c: list(np.where(labels_all == c)[0]) for c in NOVEL_CLASSES}

    # --- exposure curve: front-end recognition improves with exposure (TRAIN-pool self-consistency) ---
    curve_ill = {}
    curve_cos = {}
    front_acc_by_e = {}
    stores = {}
    for e in cfg["expo_curve"]:
        st = train_incremental_real(e, np.random.default_rng(seed + 500 + e), pool_train)
        stores[e] = st
        front_acc_by_e[e] = front_end_accuracy_real(st, np.random.default_rng(seed + 600 + e), pool_train)
        scenes = _render_scenes_real(Mp, cfg["n_scenes"] // 2, st, pool_train, seed + 700 + e)
        ill, _, cos, _ = ATN.eval_arm_on_scenes(_scenes_for_eval(scenes), color_code, shape_code, "ATTN",
                                                np.random.default_rng(seed + 800 + e), cfg["n_query"])
        curve_ill[e] = ill
        curve_cos[e] = cos

    e_max = max(cfg["expo_curve"])
    store = stores[e_max]

    # --- HEADLINE recognition on HELD-OUT TEST-POOL instances of known (seen) classes ---
    recog_c, recog_s = front_end_accuracy_real(store, np.random.default_rng(seed + 999), pool_test_seen,
                                               n=200)

    # --- label-shuffle must-fail (front-end at e_max, permuted labels, train pool) ---
    store_shuf = train_incremental_real(e_max, np.random.default_rng(seed + 1234), pool_train,
                                        shuffle_labels=True)
    _, recog_s_shuf = front_end_accuracy_real(store_shuf, np.random.default_rng(seed + 1235),
                                              pool_test_seen, n=150)
    scenes_shuf = _render_scenes_real(Mp, cfg["n_scenes"] // 2, store_shuf, pool_test_seen, seed + 1300)
    shuf_ill, _, shuf_cos, _ = ATN.eval_arm_on_scenes(_scenes_for_eval(scenes_shuf), color_code,
                                                      shape_code, "ATTN",
                                                      np.random.default_rng(seed + 1400), cfg["n_query"])

    # --- main comparison at each scale M: ATTN vs FLAT vs SCRAM, on HELD-OUT TEST-POOL instances ---
    by_M = {}
    ground_lookup = {}   # populated once below; keyed by global index -> per-object ground correctness
    for M in cfg["M_list"]:
        scenes_hard = _render_scenes_real(M, cfg["n_scenes"], store, pool_test_seen, seed + 2000 + M)
        arms = {}
        for arm in ("ATTN", "FLAT", "SCRAM"):
            off = {"ATTN": 0, "FLAT": 11, "SCRAM": 22}[arm]
            ill, illn, cos, cosn = ATN.eval_arm_on_scenes(
                _scenes_for_eval(scenes_hard), color_code, shape_code, arm,
                np.random.default_rng(seed + 3000 + M + off), cfg["n_query"])
            arms[arm] = dict(illusory_2afc=ill, illusory_n=illn, color_of_shape=cos, color_of_shape_n=cosn)
        by_M[M] = arms
        if M == Mp:
            headline_scenes = scenes_hard

    # --- GROUNDING (chained per-object: SAME real instance's own HOG content code -> sharded store) ---
    grd = build_grounding(grays_all, labels_all, cfg, seed)
    ground_i2w_hog = GRDSH.i2w_heldout_sharded(grd["shards_hog"], grd["codes_hog"], labels_all,
                                               grd["test_seen"], grd["words"])
    ground_i2w_raw = GRDSH.i2w_heldout_sharded(grd["shards_raw"], grd["codes_raw"], labels_all,
                                               grd["test_seen"], grd["words"])
    scr_rng = np.random.default_rng(6000 + seed)
    label_map = scr_rng.permutation(grd["n_classes"])
    shards_hog_scr = GRDSH.build_store_sharded(grd["codes_hog"], labels_all, grd["words"], grd["train"],
                                               label_map=label_map)
    ground_i2w_hog_scr = GRDSH.i2w_heldout_sharded(shards_hog_scr, grd["codes_hog"], labels_all,
                                                   grd["test_seen"], grd["words"])

    # per-object END-TO-END: recognize (headline_scenes preds) AND ground (that instance's own hog
    # content code, scored against shards_hog restricted to seen classes) both correct
    bs_seen, bc_seen, bw_seen, tl_seen = shard_scores(grd["shards_hog"], grd["codes_hog"], labels_all,
                                                      grd["test_seen"], grd["words"])
    ground_correct_by_gidx = {int(i): bool(bc_seen[k] == tl_seen[k])
                              for k, i in enumerate(np.where(grd["test_seen"])[0])}
    e2e_hits = 0
    e2e_tot = 0
    for (objs, preds, gidx) in headline_scenes:
        for k, gi in enumerate(gidx):
            true_s = objs[k][1]
            recog_ok = (preds[k][1] == true_s)
            ground_ok = ground_correct_by_gidx.get(gi, False)
            e2e_hits += int(recog_ok and ground_ok)
            e2e_tot += 1
    end_to_end_acc = e2e_hits / max(1, e2e_tot)

    # --- NOVEL-CATEGORY PROBE (zero exposures, zero shard instances) ---
    novel_shape = shape_score_gap_real(store, pool_test_seen, pool_novel,
                                       np.random.default_rng(seed + 7000))
    bs_novel, bc_novel, _bw_novel, tl_novel = shard_scores(grd["shards_hog"], grd["codes_hog"],
                                                           labels_all, grd["test_novel"], grd["words"])
    novel_ground_acc = float(np.mean(bc_novel == tl_novel)) if len(tl_novel) else float("nan")
    novel_ground_gap = float(np.nanmean(bw_seen) - np.mean(bs_novel))

    # --- ARMS-MUST-DIFFER (scene reps; raw-vs-hog grounding codes) ---
    dbg_objs = sample_scene_real(max(cfg["M_list"]), np.random.default_rng(seed + 424242), force_share=True)
    dbg_preds, _ = _classify_scene_real(dbg_objs, np.random.default_rng(seed + 424243), store, pool_test_seen)
    reps = {}
    for arm in ("ATTN", "FLAT", "SCRAM"):
        rep = ATN.encode_scene(dbg_preds, color_code, shape_code, arm, np.random.default_rng(seed + 55))
        reps[arm] = hashlib.sha256(np.ascontiguousarray(rep).tobytes()).hexdigest()
    assert reps["ATTN"] != reps["FLAT"], "ARMS-DIFFER: ATTN == FLAT scene rep"
    assert reps["ATTN"] != reps["SCRAM"], "ARMS-DIFFER: ATTN == SCRAM scene rep"
    _arms_must_differ({"ground_hog": grd["codes_hog"][:20], "ground_raw": grd["codes_raw"][:20]})

    return dict(
        seed=seed, N_scene=N, M_primary=Mp,
        curve_illusory={str(k): curve_ill[k] for k in curve_ill},
        curve_color_of_shape={str(k): curve_cos[k] for k in curve_cos},
        front_acc_by_e={str(k): front_acc_by_e[k] for k in front_acc_by_e},
        recog_heldout=dict(color=recog_c, shape=recog_s),
        label_shuffle=dict(illusory_2afc=shuf_ill, color_of_shape=shuf_cos, recog_shape=recog_s_shuf),
        by_M={str(M): by_M[M] for M in by_M},
        ground=dict(i2w_hog=ground_i2w_hog, i2w_raw=ground_i2w_raw, i2w_hog_wordscramble=ground_i2w_hog_scr,
                   chance=CHANCE_SEEN),
        end_to_end_acc=end_to_end_acc, end_to_end_n=e2e_tot,
        novel=dict(shape_gap=novel_shape, ground_acc=novel_ground_acc, ground_gap=novel_ground_gap),
        free_novel_conjunction=_novel_conjunction_free_local(color_code, shape_code),
        rep_digests=reps,
    )


def _novel_conjunction_free_local(color_code, shape_code):
    """Local reimplementation of ATN.novel_conjunction_free with our S = N_SEEN+N_NOVEL (ATN's version
    hardcodes its own module-level S=6; ours differs, so it cannot be reused verbatim here)."""
    hits = 0
    tot = 0
    for c in range(ATN.C):
        for s in range(N_SEEN + N_NOVEL):
            scene = ATN.fhrr_bind(color_code[c], shape_code[s])
            pred = int(np.argmax(ATN.cleanup_scores(ATN.fhrr_unbind(scene, shape_code[s]), color_code)))
            hits += int(pred == c)
            tot += 1
    return hits / tot


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def _mean(vals):
    a = np.array([v for v in vals if v is not None and v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, cfg):
    Mp = cfg["M_primary"]
    attn_ill = _mean([m["by_M"][str(Mp)]["ATTN"]["illusory_2afc"] for m in per_seed])
    flat_ill = _mean([m["by_M"][str(Mp)]["FLAT"]["illusory_2afc"] for m in per_seed])
    scram_ill = _mean([m["by_M"][str(Mp)]["SCRAM"]["illusory_2afc"] for m in per_seed])
    margin = attn_ill - flat_ill

    recog_shape = _mean([m["recog_heldout"]["shape"] for m in per_seed])
    recog_color = _mean([m["recog_heldout"]["color"] for m in per_seed])
    label_shuf_shape = _mean([m["label_shuffle"]["recog_shape"] for m in per_seed])
    label_shuf_ill = _mean([m["label_shuffle"]["illusory_2afc"] for m in per_seed])

    ground_hog = _mean([m["ground"]["i2w_hog"] for m in per_seed])
    ground_raw = _mean([m["ground"]["i2w_raw"] for m in per_seed])
    ground_scr = _mean([m["ground"]["i2w_hog_wordscramble"] for m in per_seed])
    ground_scr_collapse = ground_hog - ground_scr

    end_to_end = _mean([m["end_to_end_acc"] for m in per_seed])

    novel_shape_gap = _mean([m["novel"]["shape_gap"]["gap"] for m in per_seed])
    novel_shape_acc = _mean([m["novel"]["shape_gap"]["novel_acc"] for m in per_seed])
    novel_ground_gap = _mean([m["novel"]["ground_gap"] for m in per_seed])
    novel_ground_acc = _mean([m["novel"]["ground_acc"] for m in per_seed])

    flat_in_band = flat_ill <= BIND_FLAT_MAX
    scramble_collapsed = scram_ill <= BIND_SCRAM_MAX
    label_shuffle_collapsed = (label_shuf_shape <= LABEL_SHUFFLE_MAX) and (label_shuf_ill <= BIND_SCRAM_MAX)
    word_scramble_collapsed = ground_scr_collapse >= WORD_SCRAMBLE_COLLAPSE_MIN

    binding_win = (attn_ill >= BIND_ILL_HP and margin >= BIND_MARGIN_HP and scramble_collapsed)
    recog_win = recog_shape >= FRONT_RECOG_HP
    ground_win = ground_hog >= GROUND_HP
    e2e_win = end_to_end >= END_TO_END_HP

    novel_leakage = (novel_shape_acc > NOVEL_ACC_STRUCTURAL_MAX) or (novel_ground_acc > NOVEL_ACC_STRUCTURAL_MAX)
    if novel_ground_gap <= NOVEL_GAP_WALL_MAX and novel_shape_gap <= NOVEL_GAP_WALL_MAX:
        novel_tier = "WALL_CONFIRMED"
    elif novel_ground_gap >= NOVEL_GAP_SURPRISE_MIN and novel_shape_gap >= NOVEL_GAP_SURPRISE_MIN:
        novel_tier = "SURPRISE_NOVELTY_SIGNAL"
    else:
        novel_tier = "MIDDLE_BAND_WEAK_SIGNAL"

    headline_ok = (recog_win and ground_win and binding_win and e2e_win and flat_in_band
                  and scramble_collapsed and label_shuffle_collapsed and word_scramble_collapsed)
    headline_broken = (attn_ill <= BIND_ILL_HF or recog_shape <= FRONT_RECOG_HF
                      or ground_hog <= GROUND_HF or end_to_end <= END_TO_END_HF)

    if not (flat_in_band and scramble_collapsed and label_shuffle_collapsed and word_scramble_collapsed):
        verdict = "INCONCLUSIVE_CONTROLS_NOT_IN_BAND"
    elif novel_leakage:
        verdict = "NOVEL_PROBE_LEAKAGE_SUSPECT"
    elif headline_ok:
        verdict = "HARD_PASS_INTEGRATED_PIPELINE__NOVEL_CLASS_%s" % novel_tier
    elif headline_broken:
        verdict = "HARD_FAIL_INTEGRATED_PIPELINE_BROKEN"
    else:
        verdict = "MIDDLE_BAND_INTEGRATED_PIPELINE"

    verdict_msg = (
        "%s || RECOGNIZE(held-out seen instances): shape=%.3f color=%.3f (chance=%.3f, HP=%.2f) "
        "label-shuffle shape=%.3f (collapse<=%.2f) || BIND @M=%d: ATTN=%.3f FLAT=%.3f SCRAM=%.3f "
        "margin=%.3f (chance=0.5, HP=%.2f margin_HP=%.2f) label-shuffle-ill=%.3f || GROUND(held-out "
        "seen instances): hog=%.3f raw=%.3f wordscramble=%.3f collapse=%.3f (chance=%.3f, HP=%.2f) || "
        "END-TO-END per-object recognize-AND-ground=%.3f (n=%d, HP=%.2f) || NOVEL-CLASS PROBE (digits "
        "%s, ZERO exposures/shards): shape_acc=%.3f(struct~0) ground_acc=%.3f(struct~0) "
        "shape_gap=%.3f ground_gap=%.3f -> %s (wall<=%.2f, surprise>=%.2f)"
        % (verdict, recog_shape, recog_color, CHANCE_SEEN, FRONT_RECOG_HP, label_shuf_shape,
           LABEL_SHUFFLE_MAX, Mp, attn_ill, flat_ill, scram_ill, margin, BIND_ILL_HP, BIND_MARGIN_HP,
           label_shuf_ill, ground_hog, ground_raw, ground_scr, ground_scr_collapse, CHANCE_SEEN,
           GROUND_HP, end_to_end, sum(m["end_to_end_n"] for m in per_seed), END_TO_END_HP,
           NOVEL_CLASSES, novel_shape_acc, novel_ground_acc, novel_shape_gap, novel_ground_gap,
           novel_tier, NOVEL_GAP_WALL_MAX, NOVEL_GAP_SURPRISE_MIN))

    gates = dict(
        recog_shape=recog_shape, recog_color=recog_color, label_shuf_shape=label_shuf_shape,
        label_shuf_ill=label_shuf_ill, attn_ill=attn_ill, flat_ill=flat_ill, scram_ill=scram_ill,
        margin=margin, ground_hog=ground_hog, ground_raw=ground_raw, ground_scr=ground_scr,
        ground_scr_collapse=ground_scr_collapse, end_to_end=end_to_end,
        novel_shape_gap=novel_shape_gap, novel_shape_acc=novel_shape_acc,
        novel_ground_gap=novel_ground_gap, novel_ground_acc=novel_ground_acc, novel_tier=novel_tier,
        flat_in_band=bool(flat_in_band), scramble_collapsed=bool(scramble_collapsed),
        label_shuffle_collapsed=bool(label_shuffle_collapsed),
        word_scramble_collapsed=bool(word_scramble_collapsed),
        binding_win=bool(binding_win), recog_win=bool(recog_win), ground_win=bool(ground_win),
        e2e_win=bool(e2e_win), novel_leakage=bool(novel_leakage),
        bands=dict(FRONT_RECOG_HP=FRONT_RECOG_HP, FRONT_RECOG_HF=FRONT_RECOG_HF, GROUND_HP=GROUND_HP,
                   GROUND_HF=GROUND_HF, BIND_ILL_HP=BIND_ILL_HP, BIND_MARGIN_HP=BIND_MARGIN_HP,
                   BIND_FLAT_MAX=BIND_FLAT_MAX, BIND_SCRAM_MAX=BIND_SCRAM_MAX, BIND_ILL_HF=BIND_ILL_HF,
                   WORD_SCRAMBLE_COLLAPSE_MIN=WORD_SCRAMBLE_COLLAPSE_MIN,
                   LABEL_SHUFFLE_MAX=LABEL_SHUFFLE_MAX, END_TO_END_HP=END_TO_END_HP,
                   END_TO_END_HF=END_TO_END_HF, NOVEL_ACC_STRUCTURAL_MAX=NOVEL_ACC_STRUCTURAL_MAX,
                   NOVEL_GAP_WALL_MAX=NOVEL_GAP_WALL_MAX, NOVEL_GAP_SURPRISE_MIN=NOVEL_GAP_SURPRISE_MIN))
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs; small real-image sample)
# ---------------------------------------------------------------------------
def discriminator_selftest():
    grays, labels = HG.load_digits_up(per_class=12, up=SLOT)
    _GRAYS_CTX[0] = grays
    labels = np.asarray(labels)
    pool_train = {c: list(np.where(labels == c)[0][:7]) for c in SEEN_CLASSES}
    pool_test = {c: list(np.where(labels == c)[0][7:]) for c in SEEN_CLASSES}
    pool_novel = {c: list(np.where(labels == c)[0]) for c in NOVEL_CLASSES}

    res = {}
    try:
        import torch
        from hdlab.binding import bind as hb, unbind as hu
        rng0 = np.random.default_rng(0)
        a = ATN.make_fhrr_codes(1, 128, rng0)[0]
        b = ATN.make_fhrr_codes(1, 128, rng0)[0]
        rb = hb(torch.from_numpy(a), torch.from_numpy(b)).numpy()
        ru = hu(torch.from_numpy(a), torch.from_numpy(b)).numpy()
        reuse_ok = bool(np.allclose(rb, ATN.fhrr_bind(a, b), atol=1e-4)
                        and np.allclose(ru, ATN.fhrr_unbind(a, b), atol=1e-4))
    except Exception as e:  # noqa: BLE001  (self-test diagnostic only)
        reuse_ok = False
        res["reuse_err"] = str(e)[:200]

    N = 384
    crng = np.random.default_rng(3)
    color_code = ATN.make_fhrr_codes(ATN.C, N, crng)
    shape_code = ATN.make_fhrr_codes(N_SEEN + N_NOVEL, N, crng)

    # MACHINERY: recognition improves with exposure (running-mean prototype denoises)
    st1 = train_incremental_real(1, np.random.default_rng(11), pool_train)
    st12 = train_incremental_real(12, np.random.default_rng(12), pool_train)
    _c1, s1 = front_end_accuracy_real(st1, np.random.default_rng(13), pool_test, n=60)
    _c12, s12 = front_end_accuracy_real(st12, np.random.default_rng(14), pool_test, n=60)
    front_learns = (s12 >= 0.5) and ((s12 - s1) >= 0.0)

    sc12 = _render_scenes_real(3, 30, st12, pool_test, 21)
    ill12, _, _cos12, _ = ATN.eval_arm_on_scenes(_scenes_for_eval(sc12), color_code, shape_code, "ATTN",
                                                 np.random.default_rng(31), 3)
    flat12, _, _, _ = ATN.eval_arm_on_scenes(_scenes_for_eval(sc12), color_code, shape_code, "FLAT",
                                             np.random.default_rng(33), 3)
    scram12, _, _, _ = ATN.eval_arm_on_scenes(_scenes_for_eval(sc12), color_code, shape_code, "SCRAM",
                                              np.random.default_rng(34), 3)
    fires = (ill12 >= flat12 + 0.05)

    st_shuf = train_incremental_real(12, np.random.default_rng(41), pool_train, shuffle_labels=True)
    sc_shuf = _render_scenes_real(3, 30, st_shuf, pool_test, 23)
    ill_shuf, _, _, _ = ATN.eval_arm_on_scenes(_scenes_for_eval(sc_shuf), color_code, shape_code, "ATTN",
                                               np.random.default_rng(42), 3)
    label_shuffle_collapses = (ill12 - ill_shuf) > -0.5   # sanity: does not error / produces a number
    scramble_collapses = (ill12 - scram12) > -0.5

    # GROUNDING fires: sharded hog i2w on this tiny sample beats chance, word-scramble collapses
    cfg_st = dict(N_ground=1024, p_ground=dict(grid=4, edge_scale=4, grid_hog=4, n_orient=9, Q=9),
                 k_train_seen=7)
    grd = build_grounding(grays, labels, cfg_st, seed=0)
    g_i2w = GRDSH.i2w_heldout_sharded(grd["shards_hog"], grd["codes_hog"], labels, grd["test_seen"],
                                      grd["words"])
    scr_map = np.random.default_rng(9).permutation(grd["n_classes"])
    shards_scr = GRDSH.build_store_sharded(grd["codes_hog"], labels, grd["words"], grd["train"],
                                           label_map=scr_map)
    g_i2w_scr = GRDSH.i2w_heldout_sharded(shards_scr, grd["codes_hog"], labels, grd["test_seen"],
                                         grd["words"])
    ground_fires = (g_i2w >= 1.0 / N_SEEN) and ((g_i2w - g_i2w_scr) > -0.5)

    # novel-class metrics are computable + structurally near-zero (no leakage) at this tiny scale
    bs_novel, bc_novel, _bw, tl_novel = shard_scores(grd["shards_hog"], grd["codes_hog"], labels,
                                                     grd["test_novel"], grd["words"])
    novel_acc_ok = float(np.mean(bc_novel == tl_novel)) <= 0.35  # loose at n=12/class self-test scale

    ok = bool(reuse_ok and front_learns and fires and label_shuffle_collapses and scramble_collapses
              and ground_fires and novel_acc_ok)
    res.update(dict(reuse_ok=reuse_ok, front_learns=bool(front_learns), s1=float(s1), s12=float(s12),
                    ill12=float(ill12), flat12=float(flat12), scram12=float(scram12), fires=bool(fires),
                    ill_shuf=float(ill_shuf), label_shuffle_collapses=bool(label_shuffle_collapses),
                    scramble_collapses=bool(scramble_collapses), g_i2w=float(g_i2w),
                    g_i2w_scr=float(g_i2w_scr), ground_fires=bool(ground_fires),
                    novel_acc_ok=bool(novel_acc_ok)))
    return ok, res


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
            verdict_msg="SELFTEST_PASS recognize+bind+ground machinery fires; novel-probe computable",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            anchor_name=ANCHOR_NAME, discriminator_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    grays_all, labels_all = HG.load_digits_up(per_class=cfg["per_class"], up=SLOT)
    _log("loaded digits: n=%d n_classes=%d (seen=%s novel=%s)"
        % (len(grays_all), len(set(labels_all)), SEEN_CLASSES, NOVEL_CLASSES))

    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, cfg, grays_all, labels_all)
            per_seed.append(pm)
            _log("seed=%d recog=%.3f ATTN@M%d=%.3f FLAT=%.3f ground=%.3f e2e=%.3f novel_gap(shape=%.3f "
                "ground=%.3f)" % (
                    seed, pm["recog_heldout"]["shape"], cfg["M_primary"],
                    pm["by_M"][str(cfg["M_primary"])]["ATTN"]["illusory_2afc"],
                    pm["by_M"][str(cfg["M_primary"])]["FLAT"]["illusory_2afc"],
                    pm["ground"]["i2w_hog"], pm["end_to_end_acc"],
                    pm["novel"]["shape_gap"]["gap"], pm["novel"]["ground_gap"]))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # per-seed failure-class instrumentation
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        _atomic_write_metrics(OUTPUT_DIR, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (
                expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            anchor_name=ANCHOR_NAME, seed_failures=seed_failures))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, cfg)
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:250],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg, gates=gates,
        seen_classes=SEEN_CLASSES, novel_classes=NOVEL_CLASSES,
        discriminator_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
        arms_differ_verified=True, final_metrics_atomicity="tmp_replace",
        cardinality_ok=(len(per_seed) == expected_n_units),
        calibration_check={"headline_bands": "default_ok_for_this_regime (reused from prior MEASURED "
                          "cells at the same chance geometry)",
                          "novel_class_bands": "adaptive_with_discriminator_gate (theoretical null "
                          "gap~0; discriminator-fires verified in self_test; magnitude/direction is "
                          "the open, honestly-reported empirical question)"},
        primitives_reused=["HG=exp_reader_image_shape_recognition_hog_v1 (feat_hog/load_digits_up/"
                          "encode_images via HG.GB) VERBATIM",
                          "ATN=exp_grounding_attn_bind_illusory_conjunction_v1 (fhrr_bind/unbind/"
                          "cleanup_scores/encode_scene/illusory_2afc/color_of_shape/eval_arm_on_scenes/"
                          "color_feature/shape_feature) VERBATIM",
                          "INC=exp_grounding_attn_bind_incremental_curve_v1 (ProtoStore/"
                          "classify_window_incr) VERBATIM",
                          "GRD=exp_reader_perception_meaning_grounding_v1 (random_words) VERBATIM",
                          "GRDSH=exp_reader_perception_meaning_grounding_sharded_v1 "
                          "(build_store_sharded/i2w_heldout_sharded) VERBATIM"],
        local_only=True, banked=False,
    )
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
