"""Glass-box HOG-shape -> HD keyless content-recognition on CLEAN labeled images.

USER course-correction 2026-07-21: do NOT test on McGuffey woodcuts (OOD worst-case confound +
over-emphasis). Redirect the glass-box HOG->HD recognition test to a CLEAN, LOCAL, labeled image set.

DECOUPLED QUESTION: does a SPECIFIED-shape glass-box front-end (HOG = per-cell histograms of oriented
gradients, NO learned weights) -> HD give REAL keyless content-recognition on CLEAN labeled images,
where raw-pixel-HD (Kanerva position-value record of intensities) is weaker? = validates the glass-box
recognition PIPELINE on a fair testbed, no woodcut handicap, no McGuffey.

TESTBEDS (clean, local, labeled, shape/HOG-appropriate):
  PRIMARY   sklearn fetch_olivetti_faces (cached local): 400 imgs / 40 classes / 10 each / 64x64.
            Real within-class variation (pose/lighting/expression) = where raw-pixel-HD is weaker.
  SECONDARY sklearn load_digits (bundled, no download): 8x8 upscaled to 32x32, first 40/class = 400/10.

ARMS (ONE variable = the front-end; identical HD encoder + protocol reused from the grounding brick):
  rung1_raw  : resize -> gridxgrid intensity -> global quantize -> Kanerva record encode (baseline).
  rung2_edge : Sobel gradient MAGNITUDE (fixed kernels), no orientation binning (ablation).
  rung3_hog  : per-cell oriented-gradient histogram (np.gradient -> unsigned orientation [0,pi) ->
               n_orient bins -> per-cell magnitude-weighted histogram -> per-cell L2 contrast-norm) ->
               global quantize -> Kanerva record encode. THE SHAPE FRONT-END. NO learned weights,
               NO cv2/skimage/kymatio (pure numpy + the grounding brick's encoder).

PROTOCOL (keyless; content determines the answer; NO stored label-key), reused VERBATIM from
exp_reader_image_content_recognition_v1:
  PRIMARY   NN-SHARED-REFERENT: each image's nearest OTHER by content cosine -> shares class? vs perm-null.
  SECONDARY LEAVE-ONE-OUT class prototype (cross-instance held-out): argmax cosine vs 1/n_classes.

MUST-FAIL (multi-seed): (1) content-scramble (per-image pixel/level shuffle) MUST collapse HOG
recognition (content-driven not base-rate). (2) label-scramble MUST collapse LOO. Both on BOTH testbeds.

HONEST READ EITHER WAY: HOG >> raw + scramble collapses = glass-box shape recognition works on clean
images (pipeline validated). HOG ~ raw or at chance = glass-box shape doesn't beat pixel-record -> the
fork favors CLIP/resonator. Reported cleanly.

LOCAL ONLY. No push, no remote-persist, no production mutation, no atom banking.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (raw/edge/hog codes bit-differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: recognition = NN-shared/LOO vs perm-null chance + scramble collapse, not a noise-floor cap
# - baseline_in_band: raw < RAW_SAT_MAX (not saturated) checked at smoke; perm-null chance is the floor
# - deterministic seeding: fixed int seeds only; no hash()-seeded RNG, no list(set()) ordering
# - discriminator-fires: self_test synth orientation set has HOG NN-shared >= raw + 0.20 + scramble collapses
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - progress_logging = print_flush_true (cell < 300s; flush anyway)
ASCII-only.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
import hashlib
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_image_shape_recognition_hog_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse the grounding brick's encoder/front-ends + the content-recognition brick's keyless metrics.
# (Neither reuse touches McGuffey data; only generic encoder + metric functions are imported.)
import experiments.exp_reader_image_word_grounding_v1 as GB  # noqa: E402
import experiments.exp_reader_image_content_recognition_v1 as CR  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bands (HYPOTHESIZED@preregs/2026-07-21_reader_image_shape_recognition_hog_v1.md) ----
CHANCE_EPS = 0.03            # within chance+eps => at chance
HOG_LIFT_MIN = 0.05         # robust hog_nn - chance (mean-1std above chance)
HOG_OVER_RAW_MIN = 0.05     # hog_nn - raw_nn: shape beats pixel-record = the KEY test
SCR_COLLAPSE_MIN = 0.05     # hog_nn - hog_scramble_nn: content-driven
STRONG_RECOG_MIN = 0.30     # hog_nn >= this = STRONG absolute recognition
RAW_SAT_MAX = 0.95          # baseline_in_band: raw_nn >= this at smoke => saturation flag
SEEDS = [0, 1, 2, 3, 4]
NN_NULL_TRIALS = 200
CELL_PX = 8                 # HOG cell size in px (constant; res = grid_hog * CELL_PX)


# --------------------------------------------------------------------------------------
# defensive-error-checking template helpers
# --------------------------------------------------------------------------------------
def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": anchor_name, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": anchor_name}
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)


def _arms_must_differ(arms_outputs):
    digests = {}
    for name, out in arms_outputs.items():
        b = np.ascontiguousarray(out).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical (hash=%s)" % (a, b, digests[a]))
    return digests


# --------------------------------------------------------------------------------------
# HOG front-end (glass-box, specified, deterministic; pure numpy, NO learned weights)
# --------------------------------------------------------------------------------------
def feat_hog(gray, grid_hog, n_orient, cell_px=CELL_PX):
    """Per-cell histogram of oriented gradients. gray in [0,255].

    np.gradient (centered finite diff, specified) -> unsigned orientation [0,pi) -> n_orient bins ->
    per-cell magnitude-weighted histogram over grid_hog x grid_hog cells -> per-cell L2 contrast-norm.
    Returns (grid_hog, grid_hog, n_orient) float32. Captures the SHAPE of the strokes; contrast-norm
    makes it intensity-invariant (shape not brightness).
    """
    res = grid_hog * cell_px
    hi = GB._resize(gray, res)
    gy, gx = np.gradient(hi.astype(np.float64))          # d/row (y), d/col (x)
    mag = np.sqrt(gx * gx + gy * gy)
    ang = np.mod(np.arctan2(gy, gx), np.pi)              # unsigned orientation [0,pi)
    bin_w = np.pi / n_orient
    b = np.minimum((ang / bin_w).astype(np.int64), n_orient - 1)
    S = cell_px
    b_c = b.reshape(grid_hog, S, grid_hog, S)
    m_c = mag.reshape(grid_hog, S, grid_hog, S)
    hist = np.empty((grid_hog, grid_hog, n_orient), dtype=np.float64)
    for o in range(n_orient):
        hist[:, :, o] = np.where(b_c == o, m_c, 0.0).sum(axis=(1, 3))
    norm = np.sqrt((hist * hist).sum(axis=2, keepdims=True)) + 1e-6
    hist = hist / norm                                   # per-cell L2 contrast normalization
    return hist.astype(np.float32)


def _feature_maps(grays, front, p):
    """grays: list of (H,W) float [0,255]. Returns list of feature arrays (front-specific shape)."""
    if front == "rung1_raw":
        return [GB.feat_raw(g, p["grid"]) for g in grays]
    if front == "rung2_edge":
        return [GB.feat_edge(g, p["grid"], edge_scale=p["edge_scale"]) for g in grays]
    if front == "rung3_hog":
        return [feat_hog(g, p["grid_hog"], p["n_orient"], CELL_PX) for g in grays]
    raise ValueError("unknown front-end %r" % front)


def encode_images(grays, front, p, N, seed, scramble=False):
    """Return L2-normalized (n,N) content codes. Same Kanerva record encoder for all fronts; only the
    feature tensor differs. scramble=True => per-image independent permutation of the flat descriptor
    (destroys spatial + orientation structure, keeps level multiset)."""
    maps = _feature_maps(grays, front, p)
    levels = GB.quantize_global(maps, p["Q"])            # (n, ...feature dims...)
    lv = levels.reshape(levels.shape[0], -1)             # (n, n_pos)
    if scramble:
        srng = np.random.default_rng(7000 + seed)
        lv = np.stack([lv[k][srng.permutation(lv.shape[1])] for k in range(lv.shape[0])])
    brng = np.random.default_rng(1000 + seed)
    P = GB.build_position_vectors(lv.shape[1], N, brng)
    L = GB.build_level_codebook(p["Q"], N, brng)
    codes = np.stack([GB.encode_record(lv[k], P, L) for k in range(lv.shape[0])]).astype(np.float32)
    codes /= (np.linalg.norm(codes, axis=1, keepdims=True) + 1e-12)
    return codes


# --------------------------------------------------------------------------------------
# dataset loaders (clean, local, labeled)
# --------------------------------------------------------------------------------------
def load_olivetti(subsample=None):
    """400 imgs / 40 classes / 10 each / 64x64. Returns (grays[list (64,64) float 0..255], labels[list int])."""
    from sklearn.datasets import fetch_olivetti_faces
    o = fetch_olivetti_faces(download_if_missing=True)
    imgs = (o.images * 255.0).astype(np.float32)         # (400,64,64) in [0,255]
    labels = o.target.astype(int).tolist()
    grays = [imgs[i] for i in range(imgs.shape[0])]
    if subsample is not None:
        grays, labels = _subsample_per_class(grays, labels, subsample[0], subsample[1])
    return grays, labels


def load_digits_up(per_class=40, up=32, subsample=None):
    """load_digits (8x8, bundled) upscaled to up x up for HOG. first per_class per digit (deterministic)."""
    from sklearn.datasets import load_digits
    d = load_digits()
    imgs8 = (d.images / 16.0 * 255.0).astype(np.float32)  # (1797,8,8) in [0,255]
    labels_all = d.target.astype(int).tolist()
    by = defaultdict(list)
    for i, y in enumerate(labels_all):
        by[y].append(i)
    grays, labels = [], []
    for y in sorted(by):
        for i in by[y][:per_class]:
            grays.append(GB._resize(imgs8[i], up))        # bilinear upscale to up x up
            labels.append(y)
    if subsample is not None:
        grays, labels = _subsample_per_class(grays, labels, subsample[0], subsample[1])
    return grays, labels


def _subsample_per_class(grays, labels, n_classes, per_class):
    """Deterministic subsample: first n_classes labels, first per_class instances each."""
    by = defaultdict(list)
    for i, y in enumerate(labels):
        by[y].append(i)
    keep_labels = sorted(by)[:n_classes]
    idx = []
    for y in keep_labels:
        idx.extend(by[y][:per_class])
    return [grays[i] for i in idx], [labels[i] for i in idx]


def build_class_structs(labels):
    """labels list[int] -> (imgs[str ids], classes{label:[ids]}, img_classes{id:{label}})."""
    imgs = ["img%04d" % i for i in range(len(labels))]
    classes = defaultdict(list)
    img_classes = {}
    for i, y in enumerate(labels):
        classes[str(y)].append(imgs[i])
        img_classes[imgs[i]] = {str(y)}
    return imgs, {c: v for c, v in classes.items()}, img_classes


# --------------------------------------------------------------------------------------
# evaluate all front-ends on one dataset
# --------------------------------------------------------------------------------------
def eval_dataset(grays, labels, fronts, p, N, seeds):
    imgs, classes, img_classes = build_class_structs(labels)
    chance_nn = CR.nn_shared_chance(imgs, img_classes, NN_NULL_TRIALS, seed=0)
    per_front = {}
    example_codes = {}
    for front in fronts:
        nn_c, nn_s, loo1_c, loo3_c, loo1_lab = [], [], [], [], []
        for s in seeds:
            codes = encode_images(grays, front, p, N, s, scramble=False)
            codes_scr = encode_images(grays, front, p, N, s, scramble=True)
            if front not in example_codes:
                example_codes[front] = codes
            nn_c.append(CR.nn_shared_referent(codes, imgs, img_classes))
            nn_s.append(CR.nn_shared_referent(codes_scr, imgs, img_classes))
            a1, a3 = CR.loo_class_recog(codes, imgs, classes, img_classes)
            a1l, _ = CR.loo_class_recog(codes, imgs, classes, img_classes, label_scramble_seed=s)
            loo1_c.append(a1); loo3_c.append(a3); loo1_lab.append(a1l)
        per_front[front] = {
            "nn_shared_mean": float(np.mean(nn_c)), "nn_shared_std": float(np.std(nn_c)),
            "nn_shared_scramble_mean": float(np.mean(nn_s)),
            "loo_acc1_mean": float(np.mean(loo1_c)), "loo_acc1_std": float(np.std(loo1_c)),
            "loo_acc3_mean": float(np.mean(loo3_c)),
            "loo_acc1_labelscramble_mean": float(np.mean(loo1_lab)),
            "n_seeds": len(seeds),
        }
    return {"n_img": len(imgs), "n_classes": len(classes), "chance_nn_shared": chance_nn,
            "chance_loo_top1_analytic": 1.0 / max(len(classes), 1),
            "fronts": per_front}, example_codes


def _headline_verdict(ds):
    """Compute HOG-vs-raw verdict gates on one dataset's per-front metrics."""
    pf = ds["fronts"]
    chance = ds["chance_nn_shared"]
    hog = pf["rung3_hog"]; raw = pf["rung1_raw"]
    hog_nn = hog["nn_shared_mean"]; hog_std = hog["nn_shared_std"]; raw_nn = raw["nn_shared_mean"]
    hog_lift = hog_nn - chance
    hog_lift_robust = (hog_nn - hog_std) - chance
    hog_over_raw = hog_nn - raw_nn
    scr_collapse = hog_nn - hog["nn_shared_scramble_mean"]
    gates = {
        "chance_nn": chance, "hog_nn": hog_nn, "raw_nn": raw_nn,
        "edge_nn": pf["rung2_edge"]["nn_shared_mean"],
        "hog_scramble_nn": hog["nn_shared_scramble_mean"],
        "hog_lift_over_chance": hog_lift, "hog_lift_robust_mean_minus_std": hog_lift_robust,
        "hog_over_raw": hog_over_raw, "scramble_collapse": scr_collapse,
        "hog_loo_acc1": hog["loo_acc1_mean"], "raw_loo_acc1": raw["loo_acc1_mean"],
        "edge_loo_acc1": pf["rung2_edge"]["loo_acc1_mean"],
        "hog_loo_acc1_labelscramble": hog["loo_acc1_labelscramble_mean"],
    }
    lift_ok = hog_lift_robust >= HOG_LIFT_MIN
    over_raw_ok = hog_over_raw >= HOG_OVER_RAW_MIN
    scr_ok = scr_collapse >= SCR_COLLAPSE_MIN
    if hog_nn >= STRONG_RECOG_MIN and lift_ok and scr_ok:
        verdict = "GLASSBOX_SHAPE_RECOG_STRONG"
    elif over_raw_ok and lift_ok and scr_ok:
        verdict = "SHAPE_BEATS_PIXEL_RECORD"
    elif hog_lift < CHANCE_EPS:
        verdict = "HOG_AT_CHANCE"
    else:
        verdict = "MIDDLE_BAND"
    gates["verdict"] = verdict
    gates["gate_flags"] = {"lift_ok": bool(lift_ok), "over_raw_ok": bool(over_raw_ok),
                           "scr_ok": bool(scr_ok),
                           "strong": bool(hog_nn >= STRONG_RECOG_MIN),
                           "raw_saturated": bool(raw_nn >= RAW_SAT_MAX)}
    return gates


# --------------------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------------------
def self_test():
    from hdlab.binding import bsc_bind, bsc_bundle
    import torch
    N, Q = 3000, 9
    p = {"grid": 12, "edge_scale": 4, "grid_hog": 6, "n_orient": 9, "Q": Q}

    # 1. HOG deterministic + specified (two calls bit-identical)
    r0 = np.random.default_rng(0)
    g0 = r0.integers(0, 256, size=(48, 48)).astype(np.float32)
    assert np.array_equal(feat_hog(g0, 6, 9), feat_hog(g0, 6, 9)), "HOG not deterministic"

    # 2. HOG is SHAPE (orientation) not COVERAGE: two images with MATCHED ink coverage but different
    #    stroke orientation give DIFFERENT HOG descriptors; a coverage-only feature (ink fraction) does not.
    def stripes(theta_deg, size=48, period=8.0, phase=0.0):
        yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
        th = np.deg2rad(theta_deg)
        coord = xx * np.cos(th) + yy * np.sin(th)
        return (128.0 + 100.0 * np.sign(np.sin(2 * np.pi * coord / period + phase))).astype(np.float32)
    h_horiz = feat_hog(stripes(0.0), 6, 9)     # gradient orientation ~0
    h_vert = feat_hog(stripes(90.0), 6, 9)     # gradient orientation ~pi/2
    cos_hog = float((h_horiz.reshape(-1) @ h_vert.reshape(-1)) /
                    (np.linalg.norm(h_horiz) * np.linalg.norm(h_vert) + 1e-9))
    # coverage-only: ink fraction per cell of the two (both ~50% dark -> near-identical)
    def ink_frac(g, grid=6):
        return GB.feat_ink(GB._otsu_threshold((255.0 - g).reshape(-1)), g, grid, edge_scale=8)
    cov0 = ink_frac(stripes(0.0)); cov90 = ink_frac(stripes(90.0))
    cos_cov = float((cov0.reshape(-1) @ cov90.reshape(-1)) /
                    (np.linalg.norm(cov0) * np.linalg.norm(cov90) + 1e-9))
    assert cos_hog < cos_cov - 0.2, ("HOG must separate orientation more than coverage does "
                                     "(cos_hog=%.3f cos_cov=%.3f)" % (cos_hog, cos_cov))

    # 3. encode_record bit-identical to hdlab bsc primitives (encoder reused; no drift)
    rng = np.random.default_rng(1)
    n_pos = 36
    P = GB.build_position_vectors(n_pos, N, rng)
    Lc = GB.build_level_codebook(Q, N, rng)
    inten = rng.integers(0, Q, size=n_pos)
    vec = GB.encode_record(inten, P, Lc)
    stack = [bsc_bind(torch.from_numpy(P[i].astype(np.float32)),
                      torch.from_numpy(Lc[inten[i]].astype(np.float32))) for i in range(n_pos)]
    prim = bsc_bundle(torch.stack(stack)).numpy().astype(np.int8)
    assert np.array_equal(vec, prim), "encode_record != hdlab bsc primitives"

    # 4a. HOG BEATS RAW-PIXEL where ORIENTATION is the class signal: full-image oriented textures
    #     (stripes at theta in {0,45,90}; matched ~50% coverage; random phase/period/noise). HOG
    #     (orientation-sensitive, contrast-normalized) recovers the grouping position-invariantly; raw-
    #     pixel (position-value record of a phase-shifted stripe pattern) does far worse. This is the
    #     SHAPE-vs-pixel-record mechanism. (Uniform texture => scramble preserves the orientation multiset,
    #     so the scramble must-fail is tested on the LOCALIZED-shape set in 4b, not here.)
    def synth_orient(seed):
        r = np.random.default_rng(seed)
        thetas = [0.0, 45.0, 90.0]
        grays, labels = [], []
        for ci, th in enumerate(thetas):
            for _ in range(5):
                per = float(r.uniform(6.0, 10.0)); ph = float(r.uniform(0, 2 * np.pi))
                g = stripes(th, size=48, period=per, phase=ph) + r.normal(0, 8.0, size=(48, 48))
                grays.append(np.clip(g, 0, 255).astype(np.float32)); labels.append(ci)
        return grays, labels
    sg, sl = synth_orient(2)
    imgs_o, classes_o, imgc_o = build_class_structs(sl)
    c_hog_o = encode_images(sg, "rung3_hog", p, N, 0)
    c_raw_o = encode_images(sg, "rung1_raw", p, N, 0)
    nn_hog = CR.nn_shared_referent(c_hog_o, imgs_o, imgc_o)
    nn_raw = CR.nn_shared_referent(c_raw_o, imgs_o, imgc_o)
    assert nn_hog >= 0.90, "HOG must recover orientation grouping (nn=%.3f)" % nn_hog
    assert nn_hog >= nn_raw + 0.20, ("HOG must beat raw-pixel where orientation IS the class signal "
                                     "(hog=%.3f raw=%.3f)" % (nn_hog, nn_raw))

    # 4b. MUST-FAILS FIRE on a SPATIALLY-LOCALIZED distinct-shape set (class = an oriented stroke at a
    #     fixed location: horizontal bar top / vertical bar left / center block, + position jitter+noise).
    #     HOG recovers the grouping; content-scramble (permute cells) destroys the spatial localization
    #     -> collapse; LOO label-scramble -> collapse.
    def synth_local(seed):
        r = np.random.default_rng(seed)
        grays, labels = [], []
        for ci in range(3):
            for _ in range(5):
                g = r.integers(200, 235, size=(48, 48)).astype(np.float32)  # bright noisy bg
                dy, dx = int(r.integers(-2, 3)), int(r.integers(-2, 3))
                if ci == 0:
                    g[10 + dy:14 + dy, 6 + dx:42 + dx] = 25.0    # horizontal bar, top
                elif ci == 1:
                    g[6 + dy:42 + dy, 10 + dx:14 + dx] = 25.0    # vertical bar, left
                else:
                    g[20 + dy:28 + dy, 20 + dx:28 + dx] = 25.0   # center block
                grays.append(np.clip(g, 0, 255).astype(np.float32)); labels.append(ci)
        return grays, labels
    lg, ll = synth_local(3)
    imgs, classes, img_classes = build_class_structs(ll)
    c_hog = encode_images(lg, "rung3_hog", p, N, 0)
    c_raw = encode_images(lg, "rung1_raw", p, N, 0)
    c_edge = encode_images(lg, "rung2_edge", p, N, 0)
    nn_hog_l = CR.nn_shared_referent(c_hog, imgs, img_classes)
    assert nn_hog_l >= 0.90, "HOG must recover localized-shape grouping (nn=%.3f)" % nn_hog_l
    c_hog_scr = encode_images(lg, "rung3_hog", p, N, 0, scramble=True)
    nn_hog_scr = CR.nn_shared_referent(c_hog_scr, imgs, img_classes)
    assert nn_hog_scr <= nn_hog_l - 0.30, ("content-scramble must collapse HOG recognition "
                                           "(clean %.3f scramble %.3f)" % (nn_hog_l, nn_hog_scr))
    a1, _ = CR.loo_class_recog(c_hog, imgs, classes, img_classes)
    a1s, _ = CR.loo_class_recog(c_hog, imgs, classes, img_classes, label_scramble_seed=0)
    assert a1 >= 0.90 and a1s <= a1 - 0.30, ("LOO label-scramble must collapse recognition "
                                             "(clean %.3f labelscr %.3f)" % (a1, a1s))

    # 5. arms differ (raw / edge / hog codes bit-differ)
    _arms_must_differ({"raw": c_raw, "edge": c_edge, "hog": c_hog})

    # 6. no-nondeterministic-seeding static scan
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as fh:
            assert_no_nondeterministic_seeding(fh.read())
    except ImportError:
        pass

    print("[self_test] PASS: hog-deterministic, hog-is-shape-not-coverage(cos_hog=%.3f<cos_cov=%.3f), "
          "bsc-identical-encoder, HOG-beats-raw-on-orientation(hog nn=%.3f > raw nn=%.3f), "
          "content-scramble-collapses(%.3f->%.3f), LOO-label-scramble-fires(%.3f->%.3f), arms-differ"
          % (cos_hog, cos_cov, nn_hog, nn_raw, nn_hog_l, nn_hog_scr, a1, a1s), flush=True)
    return True


# --------------------------------------------------------------------------------------
# main run
# --------------------------------------------------------------------------------------
def run(mode="full"):
    t0 = time.perf_counter()
    fronts = ["rung1_raw", "rung2_edge", "rung3_hog"]
    if mode == "smoke":
        p = {"grid": 12, "edge_scale": 4, "grid_hog": 6, "n_orient": 9, "Q": 9}
        N, seeds = 3000, [0, 1]
        subsample = (8, 6)     # 8 classes x 6 imgs
    else:
        p = {"grid": 16, "edge_scale": 4, "grid_hog": 8, "n_orient": 9, "Q": 17}
        N, seeds = 8192, SEEDS
        subsample = None

    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, mode,
                        expected_n_units=len(seeds) * len(fronts) * 2)

    # PRIMARY: olivetti faces (clean, local, 64x64, real within-class variation)
    grays_o, labels_o = load_olivetti(subsample=subsample)
    print("[olivetti] n_img=%d n_classes=%d" % (len(grays_o), len(set(labels_o))), flush=True)
    olivetti, ex_codes = eval_dataset(grays_o, labels_o, fronts, p, N, seeds)

    # SECONDARY: digits upscaled (clean, bundled, confirmation on a 2nd set)
    dsub = subsample if subsample is not None else (10, 40)  # full: 10 classes x 40/class
    grays_d, labels_d = load_digits_up(per_class=40, up=32, subsample=(dsub[0], dsub[1]))
    print("[digits] n_img=%d n_classes=%d" % (len(grays_d), len(set(labels_d))), flush=True)
    p_d = dict(p)  # digits upscaled to 32; hog res = grid_hog*CELL_PX works on 32-res grays
    digits, _ = eval_dataset(grays_d, labels_d, fronts, p_d, N, seeds)

    arm_digests = _arms_must_differ({f: ex_codes[f] for f in ex_codes})

    g_oli = _headline_verdict(olivetti)     # headline
    g_dig = _headline_verdict(digits)

    # headline verdict = olivetti (primary clean testbed)
    verdict = g_oli["verdict"]
    raw_sat = g_oli["gate_flags"]["raw_saturated"]

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        "GLASS-BOX HOG-shape -> HD keyless recognition on CLEAN images (no McGuffey). "
        "PRIMARY olivetti (n=%d, %d-class): NN-shared chance=%.3f | raw=%.3f edge=%.3f hog=%.3f "
        "(hog_scr=%.3f) | hog_lift=%.3f(robust=%.3f) hog-raw=%.3f scr_collapse=%.3f || "
        "LOO acc1: raw=%.3f edge=%.3f hog=%.3f (hog labelscr=%.3f) "
        "|| SECONDARY digits(%d-class): NN chance=%.3f raw=%.3f hog=%.3f(scr=%.3f) hog-raw=%.3f "
        "| LOO hog=%.3f raw=%.3f -> %s%s"
        % (olivetti["n_img"], olivetti["n_classes"], g_oli["chance_nn"],
           g_oli["raw_nn"], g_oli["edge_nn"], g_oli["hog_nn"], g_oli["hog_scramble_nn"],
           g_oli["hog_lift_over_chance"], g_oli["hog_lift_robust_mean_minus_std"],
           g_oli["hog_over_raw"], g_oli["scramble_collapse"],
           g_oli["raw_loo_acc1"], g_oli["edge_loo_acc1"], g_oli["hog_loo_acc1"],
           g_oli["hog_loo_acc1_labelscramble"],
           digits["n_classes"], g_dig["chance_nn"], g_dig["raw_nn"], g_dig["hog_nn"],
           g_dig["hog_scramble_nn"], g_dig["hog_over_raw"],
           g_dig["hog_loo_acc1"], g_dig["raw_loo_acc1"],
           verdict, "  [RAW_SATURATED_FLAG]" if raw_sat else ""))

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "glass-box HOG-shape -> HD keyless recognition on clean images: %s" % verdict,
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "run_mode": mode,
        "config": {"params": p, "N": N, "seeds": seeds, "cell_px": CELL_PX,
                   "nn_null_trials": NN_NULL_TRIALS, "fronts": fronts,
                   "primary_dataset": "sklearn_fetch_olivetti_faces_64x64_40class",
                   "secondary_dataset": "sklearn_load_digits_8x8_upscaled32_10class",
                   "note_mcguffey": "NOT USED (USER course-correction: OOD woodcut confound dropped)"},
        "primary_olivetti": olivetti,
        "secondary_digits": digits,
        "verdict_detail": {
            "headline_metric": "nn_shared_referent (keyless: nearest content-neighbor shares class)",
            "olivetti_gates": g_oli, "digits_gates": g_dig,
            "note": "RECOGNITION (keyless, no label-key). raw-pixel-HD = the baseline (Kanerva position-"
                    "value record of intensities); HOG = specified oriented-gradient shape front-end "
                    "(NO learned weights). SHAPE_BEATS_PIXEL_RECORD = HOG robustly > chance AND > raw AND "
                    "content-scramble collapses = glass-box shape front-end gives real recognition where "
                    "pixel-record is weaker (pipeline validated on a fair clean testbed). HOG_AT_CHANCE / "
                    "no-lift-over-raw = glass-box shape does NOT beat pixel-record here -> the fork favors "
                    "CLIP/resonator. LOO is the harder cross-instance held-out generalization."},
        "bands": {"CHANCE_EPS": CHANCE_EPS, "HOG_LIFT_MIN": HOG_LIFT_MIN,
                  "HOG_OVER_RAW_MIN": HOG_OVER_RAW_MIN, "SCR_COLLAPSE_MIN": SCR_COLLAPSE_MIN,
                  "STRONG_RECOG_MIN": STRONG_RECOG_MIN, "RAW_SAT_MAX": RAW_SAT_MAX},
        "must_fail_controls": {"content_scramble": "per-image pixel/level shuffle (spatial + orientation "
                               "destroyed)", "label_scramble": "class membership shuffled (LOO only)"},
        "raw_saturated_flag": bool(raw_sat),
        "arms_differ_verified": True, "arm_digests": arm_digests,
        "final_metrics_atomicity": "tmp_replace",
        "primitives_reused": ["exp_reader_image_word_grounding_v1 encoder (encode_record / "
                              "build_position_vectors / build_level_codebook / feat_raw / feat_edge / "
                              "quantize_global / _resize) VERBATIM",
                              "exp_reader_image_content_recognition_v1 keyless metrics (nn_shared_referent "
                              "/ nn_shared_chance / loo_class_recog) VERBATIM"],
        "recipe_adopted": "specified HOG (np.gradient -> unsigned orientation bins -> per-cell "
                          "contrast-normalized histogram) -> Kanerva record encoder; keyless NN-shared + "
                          "LOO class prototypes; content + label scramble must-fails; clean local datasets",
        "local_only": True, "banked": False,
    }
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    print(verdict_msg, flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(mode="smoke" if args.smoke else "full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
