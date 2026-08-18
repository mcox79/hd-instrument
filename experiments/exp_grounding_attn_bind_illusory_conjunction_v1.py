"""Attention-gated MULTI-OBJECT feature binding (the Treisman binding problem): does an ATTENTION
spotlight + VSA bind solve illusory conjunctions in cluttered / feature-sharing visual scenes where a
bag-of-free-floating-features (pre-attentive parallel maps) fails?

SCIENCE (per notes/grounding_cg_multiobject_attention_binding_illusory_conjunction_2026-07-23.md):
  Barsalou perceptual symbols: meaning = re-simulation, convergence zones bind distributed attributes
  (color, shape). Treisman Feature Integration Theory: (1) PRE-ATTENTIVE stage registers features in
  PARALLEL, INDEPENDENT feature maps (free-floating: which colors present, which shapes present);
  (2) a SPOTLIGHT OF ATTENTION selects a location and BINDS that object's features into an object file.
  Attention is the brain's solution to the binding problem; without it features mis-combine = ILLUSORY
  CONJUNCTIONS (report a "red square" when the scene had a red circle + a blue square). Artificial vision
  / VLMs are markedly worse at multi-object binding than the brain, esp. cluttered/feature-sharing scenes.

  FAIRNESS (USER 2026-07-23): replicate ALL the brain's components -- (a) parallel independent feature
  maps: a LEARNED glass-box front-end classifies each window's COLOR (mean-RGB k-NN exemplars) and SHAPE
  (the 29438 HOG oriented-gradient descriptor, k-NN exemplars), both from real pixels; (b) an ATTENTION
  spotlight that serially selects each object's location; (c) the VSA bind. ARM_FLAT (no attention) is the
  pre-attentive-only failure mode, NOT a strawman -- it uses the SAME learned per-window classifications;
  the ONLY variable is whether attention BINDS them (correct pairing preserved) or the parallel maps form
  all cross-conjunctions (illusory conjunctions).

  Learned front-end = EXEMPLAR (k=1 nearest-neighbour) categorization (Nosofsky) -- data-hungry, so more
  training exemplars -> denser coverage of the noisy render manifold -> better classification -> a rising
  downstream LEARNING CURVE. LABEL-SHUFFLE (train exemplars on permuted labels) is the rigorous must-fail:
  it destroys the learned color/shape competence -> ATTN binding collapses to chance = the front-end's
  competence is LEARNED FROM DATA, not hand-installed.

  ONE BUILD, separable numbers:
  (1) ILLUSORY-CONJUNCTION 2AFC (headline, chance=0.5, no threshold). A >=2-object scene has (c,s) and
      (c',s') with c!=c', s!=s'. Probe: is (c,s) [TRUE] or (c',s) [ILLUSORY: c' present, s present, but
      (c',s) never conjoined] in the scene? score = Re<scene_norm, (color (x) shape)_norm>. ARM_ATTN_BIND:
      scene = sum_k color_k (x) shape_k -> (c,s) is a real term (high), (c',s) is not (~0) -> picks true.
      ARM_FLAT: scene = sum_{c in Cset} sum_{s in Sset} color_c (x) shape_s -> BOTH terms present -> chance.
  (2) COLOR-OF-SHAPE cleanup (secondary, chance=1/#present_colors). unbind(scene, shape_s), cleanup over
      the color codebook -> color of the object with shape s. ATTN recovers; FLAT returns the superposition
      of all present colors -> ambiguous.
  (3) SCALE sweep over M (#objects): more objects -> more front-end classifications per scene + additive
      superposition crosstalk (~sqrt(M/N)); locates any wall where attention stops rescuing binding.

HONESTY (load-bearing, USER 2026-07-23): the NOVEL-CONJUNCTION generalization (bind any (c,s) once codes
exist) is FREE-BY-CONSTRUCTION -- reported separately, un-gated, NOT the headline. The CG claim rests on
the NON-free part: multi-object binding WITHOUT illusory conjunctions in feature-sharing scenes where
attention is load-bearing (metric 1 + scale). ARM_SCRAMBLE (attention points at wrong locations: bind
color_k with shape_perm(k)) is the anti-cheat -- must collapse to FLAT-level (localization load-bearing).

FAIR / glass-box: real pixel-derived features (HOG shape 29438 + learned color exemplars; NO synthetic
one-hots); bit-exact codebooks per seed; ONE variable (attention-gated binding: same per-window
classifications feed all arms); difficulty-on (noisy/jittered/deformed renders, feature-sharing HARD
scenes, scale sweep); LEARNING CURVE + LABEL-SHUFFLE must-fail. No CNN; no autograd at runtime (exemplars
are stored features). No external LM. CPU-only. ASCII-only. No emojis. No em dashes.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (ATTN vs FLAT vs SCRAM scene-rep bit-differ)
# - final_metrics_atomicity = tmp + os.replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: discriminators are (i) illusory-2AFC ATTN vs FLAT vs chance 0.5, (ii) color-of-shape
#   cleanup vs chance, (iii) learning-curve + label-shuffle collapse; none is a closed-form noise floor
# - baseline_in_band: FLAT illusory-2AFC must sit near chance 0.5 (<=ILL_FLAT_MAX) at smoke; front-end
#   non-degenerate at max-train (>=FRONT_ACC_MIN); label-shuffle collapses
# - discriminator survives scale: smoke fires ATTN>>FLAT at the SAME primary M as full; full adds the
#   M-sweep + full learning curve + seeds. SMOKE exercises the SAME code branches as FULL.
# - HARD_PASS strictly above floor: ATTN illusory-2afc >= ILL_HP AND (ATTN-FLAT) >= ILL_MARGIN_HP AND
#   scramble collapses AND learning-curve rises AND label-shuffle collapses
# - deterministic seeding: fixed int seeds only; no hash()-seeded RNG, no list(set()) ordering
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg
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

ANCHOR_NAME = "grounding_attn_bind_illusory_conjunction_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse the 29438 content-aware HOG shape front-end VERBATIM (feat_hog); GB._resize for windows.
import experiments.exp_reader_image_shape_recognition_hog_v1 as HG  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---------------------------------------------------------------------------
# Scene ontology + render difficulty (difficulty is a fixed property of the TASK, same smoke/full)
# ---------------------------------------------------------------------------
COLOR_NAMES = ["red", "green", "blue", "yellow", "magenta", "cyan"]
COLOR_RGB = np.array([[220, 40, 40], [40, 180, 40], [50, 50, 220], [230, 210, 40],
                      [210, 50, 200], [40, 200, 200]], dtype=np.float64)
SHAPE_NAMES = ["circle", "square", "triangle", "diamond", "cross", "bar"]
C = len(COLOR_NAMES)
S = len(SHAPE_NAMES)
SLOT = 24            # px per object slot (square)
BG = 235.0           # light-gray background level
GRID_HOG = 3         # HOG cells per window side -> HOG res = GRID_HOG*CELL_PX (=24) matches SLOT
N_ORIENT = 9

# difficulty-on: pixel noise + per-instance color jitter + shape size/aspect deformation -> the learned
# k-NN front-end has a genuine learning curve (data-hungry) and can misclassify (real can-fail path).
NOISE = 38.0         # gaussian pixel noise std
COL_JITTER = 46.0    # per-instance RGB color jitter std (makes red/magenta, blue/cyan confusable)
RAD_FRAC = 0.27      # shape radius as fraction of SLOT
ASPECT = 0.24        # anisotropic size jitter (deforms shapes -> HOG variance)

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; only scale/coverage differ)
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(seeds=[7], N=768, M_list=[4], M_primary=4,
                    n_train_curve=[1, 8], n_scenes=80, n_query=3)
SMOKE_CFG = dict(seeds=[7, 13], N=768, M_list=[4], M_primary=4,
                 n_train_curve=[1, 4, 24], n_scenes=150, n_query=4)
FULL_CFG = dict(seeds=[7, 13, 17], N=1024, M_list=[2, 3, 4, 6], M_primary=4,
                n_train_curve=[1, 2, 4, 8, 24], n_scenes=220, n_query=4)

# ---------------------------------------------------------------------------
# Pre-registered bands (picked at smoke, BEFORE the FULL run)
# ---------------------------------------------------------------------------
ILL_HP = 0.78          # HARD_PASS: ATTN illusory-2AFC at primary M, max-train >= this (few illusory conj.)
ILL_FLAT_MAX = 0.62    # FLAT must sit near chance 0.5 (baseline_in_band / must-fail control)
ILL_MARGIN_HP = 0.18   # (ATTN - FLAT) illusory-2AFC required for HARD_PASS
ILL_SCRAMBLE_MAX = 0.66  # ARM_SCRAMBLE must collapse to ~FLAT (attention localization load-bearing)
LEARN_RISE_HP = 0.06   # ATTN color-of-shape(max-train) - ATTN color-of-shape(min-train): learned front-end
LABEL_SHUFFLE_MAX = 0.66  # label-shuffle ATTN illusory-2AFC must collapse to ~chance (front-end is learned)
FRONT_ACC_MIN = 0.75   # front-end color AND shape classification acc (max-train) must be non-degenerate
ILL_HF = 0.62          # HARD_FAIL: ATTN illusory-2AFC at primary M <= this (attention cannot bind)
CHANCE_2AFC = 0.5


# ---------------------------------------------------------------------------
# markers / metrics IO
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# FHRR (unit-modulus complex) primitives. bind = elementwise multiply, unbind = multiply by conj.
# Bit-identical to hdlab.binding on the complex dtype path (verified in self_test).
# ---------------------------------------------------------------------------
def make_fhrr_codes(m, n, rng):
    theta = rng.uniform(0.0, 2.0 * np.pi, size=(m, n))
    return np.exp(1j * theta).astype(np.complex64)


def fhrr_bind(a, b):
    return a * b


def fhrr_unbind(c, b):
    return c * np.conj(b)


def _cnorm(x):
    return x / (np.linalg.norm(x) + 1e-12)


def cleanup_scores(x, codebook):
    return np.real(x @ np.conj(codebook).T)


# ---------------------------------------------------------------------------
# Scene rendering (real colored-shape pixels; NOT synthetic one-hots)
# ---------------------------------------------------------------------------
def render_object(color_idx, shape_idx, rng):
    """Render a single (color, shape) object into a SLOT x SLOT x 3 float image with position/size/
    aspect jitter, per-instance color jitter, and background pixel noise (difficulty-on)."""
    img = np.full((SLOT, SLOT, 3), BG, dtype=np.float64)
    img += rng.normal(0.0, NOISE, size=img.shape)
    cy = SLOT / 2.0 + rng.uniform(-3.0, 3.0)
    cx = SLOT / 2.0 + rng.uniform(-3.0, 3.0)
    r = SLOT * RAD_FRAC + rng.uniform(-2.0, 2.0)
    ry = r * rng.uniform(1.0 - ASPECT, 1.0 + ASPECT)
    rx = r * rng.uniform(1.0 - ASPECT, 1.0 + ASPECT)
    col = COLOR_RGB[color_idx] + rng.normal(0.0, COL_JITTER, size=3)
    yy, xx = np.mgrid[0:SLOT, 0:SLOT].astype(np.float64)
    dy = (yy - cy) / ry
    dx = (xx - cx) / rx
    name = SHAPE_NAMES[shape_idx]
    if name == "circle":
        mask = dy * dy + dx * dx <= 1.0
    elif name == "square":
        mask = (np.abs(dy) <= 1.0) & (np.abs(dx) <= 1.0)
    elif name == "triangle":  # apex up
        base_y = cy + ry
        halfw = np.maximum(1.0 - ((base_y - yy) / (2.0 * ry)), 0.0) * 1.15
        mask = (np.abs(dx) <= halfw) & (yy <= base_y) & (yy >= cy - ry)
    elif name == "diamond":
        mask = (np.abs(dy) + np.abs(dx)) <= 1.3
    elif name == "cross":
        mask = ((np.abs(dy) <= 0.38) | (np.abs(dx) <= 0.38)) & (np.abs(dy) <= 1.0) & (np.abs(dx) <= 1.0)
    else:  # bar (tall thin vertical rectangle)
        mask = (np.abs(dx) <= 0.42) & (np.abs(dy) <= 1.15)
    for ch in range(3):
        img[:, :, ch] = np.where(mask, col[ch], img[:, :, ch])
    return np.clip(img, 0, 255)


def render_scene(objects, rng):
    slots = [render_object(c, s, rng) for (c, s) in objects]
    canvas = np.concatenate(slots, axis=1)
    starts = [k * SLOT for k in range(len(objects))]
    return canvas, starts


def _window(canvas, x0):
    return canvas[:, x0:x0 + SLOT, :]


# ---------------------------------------------------------------------------
# LEARNED glass-box front-end = EXEMPLAR (k=1 NN) parallel feature maps
#   color: mean RGB over foreground pixels -> nearest stored color exemplar
#   shape: HOG (29438 front-end) of the window grayscale -> nearest stored shape exemplar
# Data-hungry -> learning curve. LABEL-SHUFFLE control permutes exemplar labels (must-fail).
# No autograd at runtime; the "learning" is exemplar storage (build-time).
# ---------------------------------------------------------------------------
def color_feature(window):
    gray = window.mean(axis=2)
    spread = window.max(axis=2) - window.min(axis=2)
    fg = (spread > 35.0) | (np.abs(gray - BG) > 35.0)
    if fg.sum() < 4:
        fg = np.ones_like(gray, dtype=bool)
    feat = window[fg].mean(axis=0)
    return (feat / (np.linalg.norm(feat) + 1e-9)).astype(np.float32)


def shape_feature(window):
    gray = window.mean(axis=2)
    h = HG.feat_hog(gray, GRID_HOG, N_ORIENT).reshape(-1)
    return (h / (np.linalg.norm(h) + 1e-9)).astype(np.float32)


def train_front_end(n_train, rng, shuffle_labels=False):
    """Store n_train labeled single-object exemplars per (color) and per (shape). shuffle_labels =>
    exemplars are filed under a permuted label (destroys learned competence = must-fail)."""
    cmap = np.arange(C)
    smap = np.arange(S)
    if shuffle_labels:
        cmap = rng.permutation(C)
        smap = rng.permutation(S)
    CX = []; CY = []; SX = []; SY = []
    for ci in range(C):
        for si in range(S):
            for _ in range(n_train):
                w = render_object(ci, si, rng)
                CX.append(color_feature(w)); CY.append(int(cmap[ci]))
                SX.append(shape_feature(w)); SY.append(int(smap[si]))
    return dict(CX=np.stack(CX), CY=np.array(CY, dtype=np.int64),
                SX=np.stack(SX), SY=np.array(SY, dtype=np.int64))


def classify_window(window, store):
    cf = color_feature(window)
    sf = shape_feature(window)
    pc = int(store["CY"][int(np.argmax(store["CX"] @ cf))])
    ps = int(store["SY"][int(np.argmax(store["SX"] @ sf))])
    return pc, ps


def front_end_accuracy(store, rng, n=150):
    cc = 0; sc = 0
    for _ in range(n):
        ci = int(rng.integers(0, C)); si = int(rng.integers(0, S))
        w = render_object(ci, si, rng)
        pc, ps = classify_window(w, store)
        cc += int(pc == ci); sc += int(ps == si)
    return cc / n, sc / n


# ---------------------------------------------------------------------------
# Scene encoding under each arm (ONE variable = attention-gated binding; SAME per-window classifications)
#   ATTN : scene = sum_k color[k] (x) shape[k]                     (spotlight binds each object's features)
#   FLAT : scene = sum_{c in Cset} sum_{s in Sset} color[c] (x) shape[s]
#          (pre-attentive parallel maps: registers WHICH colors + WHICH shapes present, no pairing =>
#           all cross-conjunctions => illusory conjunctions; presence-based => illusory 2AFC = TRUE chance)
#   SCRAM: scene = sum_k color[k] (x) shape[perm[k]]               (attention points at wrong locations)
# ---------------------------------------------------------------------------
def _derangement(m, rng):
    while True:
        p = rng.permutation(m)
        if not np.any(p == np.arange(m)):
            return p


def encode_scene(preds, color_code, shape_code, arm, rng):
    M = len(preds)
    N = color_code.shape[1]
    acc = np.zeros(N, dtype=np.complex64)
    if arm == "ATTN":
        for (pc, ps) in preds:
            acc = acc + fhrr_bind(color_code[pc], shape_code[ps])
    elif arm == "FLAT":
        cset = sorted({pc for (pc, _ps) in preds})
        sset = sorted({ps for (_pc, ps) in preds})
        for c in cset:
            for s in sset:
                acc = acc + fhrr_bind(color_code[c], shape_code[s])
    elif arm == "SCRAM":
        perm = _derangement(M, rng) if M >= 2 else np.arange(M)
        for k in range(M):
            acc = acc + fhrr_bind(color_code[preds[k][0]], shape_code[preds[perm[k]][1]])
    else:
        raise ValueError("unknown arm %r" % arm)
    return acc


# ---------------------------------------------------------------------------
# Scene sampling with a controlled feature-sharing HARD subset + illusory probe
# ---------------------------------------------------------------------------
def sample_scene(M, rng, force_share):
    """M objects, all distinct (color,shape) pairs. force_share => >=2 objects share a color OR a shape
    (the HARD feature-sharing difficulty). Returns list of (c,s)."""
    objs = []
    for _ in range(200):
        objs = []
        used = set()
        for _k in range(M):
            for _try in range(60):
                c = int(rng.integers(0, C)); s = int(rng.integers(0, S))
                if (c, s) not in used:
                    used.add((c, s)); objs.append((c, s)); break
        if len(objs) < M:
            continue
        cols = [o[0] for o in objs]; shps = [o[1] for o in objs]
        shares = (len(set(cols)) < M) or (len(set(shps)) < M)
        if force_share and not shares:
            continue
        if (not force_share) and shares and rng.random() < 0.5:
            continue
        return objs
    return objs


def make_illusory_probe(objs, rng):
    """TRUE conjunction (c,s) present on some object + ILLUSORY (c',s): c' present (other object), s
    present, but (c',s) not an object. Returns (c_true, s, c_ill) or None."""
    present = set(objs)
    cols = list({o[0] for o in objs})
    for oi in rng.permutation(len(objs)):
        c, s = objs[int(oi)]
        for cp in rng.permutation(cols):
            cp = int(cp)
            if cp != c and (cp, s) not in present:
                return c, s, cp
    return None


def _classify_scene(objs, rng, store):
    canvas, starts = render_scene(objs, rng)
    return [classify_window(_window(canvas, x0), store) for x0 in starts]


def illusory_2afc(objs, preds, color_code, shape_code, arm, rng):
    probe = make_illusory_probe(objs, rng)
    if probe is None:
        return None
    c_true, s, c_ill = probe
    scene = encode_scene(preds, color_code, shape_code, arm, rng)
    sn = _cnorm(scene)
    st = float(np.real(np.vdot(_cnorm(fhrr_bind(color_code[c_true], shape_code[s])), sn)))
    si = float(np.real(np.vdot(_cnorm(fhrr_bind(color_code[c_ill], shape_code[s])), sn)))
    return int(st > si)


def color_of_shape(objs, preds, color_code, shape_code, arm, rng):
    shps = [o[1] for o in objs]
    uniq = [i for i in range(len(objs)) if shps.count(objs[i][1]) == 1]
    if not uniq:
        return None
    oi = int(rng.choice(uniq))
    c_true, s = objs[oi]
    scene = encode_scene(preds, color_code, shape_code, arm, rng)
    pred_c = int(np.argmax(cleanup_scores(fhrr_unbind(scene, shape_code[s]), color_code)))
    return int(pred_c == c_true)


def novel_conjunction_free(color_code, shape_code):
    """FREE-BY-CONSTRUCTION control (reported, NOT headline): a single bound pair is always recoverable."""
    hits = 0; tot = 0
    for c in range(C):
        for s in range(S):
            scene = fhrr_bind(color_code[c], shape_code[s])
            pred = int(np.argmax(cleanup_scores(fhrr_unbind(scene, shape_code[s]), color_code)))
            hits += int(pred == c); tot += 1
    return hits / tot


def eval_arm_on_scenes(scenes_preds, color_code, shape_code, arm, rng, n_query):
    ill_hits = 0; ill_tot = 0; cos_hits = 0; cos_tot = 0
    for (objs, preds) in scenes_preds:
        for _q in range(n_query):
            r = illusory_2afc(objs, preds, color_code, shape_code, arm, rng)
            if r is not None:
                ill_hits += r; ill_tot += 1
            r2 = color_of_shape(objs, preds, color_code, shape_code, arm, rng)
            if r2 is not None:
                cos_hits += r2; cos_tot += 1
    return (ill_hits / max(1, ill_tot), ill_tot, cos_hits / max(1, cos_tot), cos_tot)


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------
def _render_scenes(M, n, store, seed_base):
    srng = np.random.default_rng(seed_base)
    scenes = []
    for _ in range(n):
        objs = sample_scene(M, srng, force_share=True)
        preds = _classify_scene(objs, srng, store)
        scenes.append((objs, preds))
    return scenes


def run_seed(seed, cfg):
    rng = np.random.default_rng(seed + 90210)
    N = cfg["N"]
    color_code = make_fhrr_codes(C, N, rng)
    shape_code = make_fhrr_codes(S, N, rng)
    Mp = cfg["M_primary"]

    # --- learning curve: front-end trained on increasing #exemplars; eval ATTN at primary M ---
    curve_ill = {}
    curve_cos = {}
    front_acc_by_train = {}
    stores = {}
    for nt in cfg["n_train_curve"]:
        st = train_front_end(nt, np.random.default_rng(seed + 500 + nt))
        stores[nt] = st
        front_acc_by_train[nt] = front_end_accuracy(st, np.random.default_rng(seed + 600 + nt))
        scenes = _render_scenes(Mp, cfg["n_scenes"] // 2, st, seed + 700 + nt)
        ill, _, cos, _ = eval_arm_on_scenes(scenes, color_code, shape_code, "ATTN",
                                            np.random.default_rng(seed + 800 + nt), cfg["n_query"])
        curve_ill[nt] = ill; curve_cos[nt] = cos

    nt_max = max(cfg["n_train_curve"])
    store = stores[nt_max]

    # --- label-shuffle must-fail (front-end trained on permuted labels, same max exemplars) ---
    store_shuf = train_front_end(nt_max, np.random.default_rng(seed + 1234), shuffle_labels=True)
    scenes_shuf = _render_scenes(Mp, cfg["n_scenes"] // 2, store_shuf, seed + 1300)
    shuf_ill, _, shuf_cos, _ = eval_arm_on_scenes(scenes_shuf, color_code, shape_code, "ATTN",
                                                  np.random.default_rng(seed + 1400), cfg["n_query"])

    # --- main comparison at each scale M: ATTN vs FLAT vs SCRAM on HARD feature-sharing scenes ---
    by_M = {}
    for M in cfg["M_list"]:
        scenes_hard = _render_scenes(M, cfg["n_scenes"], store, seed + 2000 + M)
        arms = {}
        for arm in ("ATTN", "FLAT", "SCRAM"):
            off = {"ATTN": 0, "FLAT": 11, "SCRAM": 22}[arm]
            ill, illn, cos, cosn = eval_arm_on_scenes(
                scenes_hard, color_code, shape_code, arm, np.random.default_rng(seed + 3000 + M + off), cfg["n_query"])
            arms[arm] = dict(illusory_2afc=ill, illusory_n=illn, color_of_shape=cos, color_of_shape_n=cosn)
        by_M[M] = arms

    # --- ARMS-MUST-DIFFER (META_RULE_AF): scene reps of the three arms must bit-differ ---
    dbg_objs = sample_scene(max(cfg["M_list"]), np.random.default_rng(seed + 424242), force_share=True)
    dbg_preds = _classify_scene(dbg_objs, np.random.default_rng(seed + 424243), store)
    reps = {}
    for arm in ("ATTN", "FLAT", "SCRAM"):
        rep = encode_scene(dbg_preds, color_code, shape_code, arm, np.random.default_rng(seed + 55))
        reps[arm] = hashlib.sha256(np.ascontiguousarray(rep).tobytes()).hexdigest()
    assert reps["ATTN"] != reps["FLAT"], "META_RULE_AF: ATTN == FLAT scene rep"
    assert reps["ATTN"] != reps["SCRAM"], "META_RULE_AF: ATTN == SCRAM scene rep"

    return dict(seed=seed, N=N, M_primary=Mp,
                curve_illusory={str(k): curve_ill[k] for k in curve_ill},
                curve_color_of_shape={str(k): curve_cos[k] for k in curve_cos},
                front_acc_by_train={str(k): front_acc_by_train[k] for k in front_acc_by_train},
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


def aggregate_and_verdict(per_seed, cfg):
    Mp = cfg["M_primary"]
    attn_ill = _mean([m["by_M"][str(Mp)]["ATTN"]["illusory_2afc"] for m in per_seed])
    flat_ill = _mean([m["by_M"][str(Mp)]["FLAT"]["illusory_2afc"] for m in per_seed])
    scram_ill = _mean([m["by_M"][str(Mp)]["SCRAM"]["illusory_2afc"] for m in per_seed])
    attn_cos = _mean([m["by_M"][str(Mp)]["ATTN"]["color_of_shape"] for m in per_seed])
    flat_cos = _mean([m["by_M"][str(Mp)]["FLAT"]["color_of_shape"] for m in per_seed])
    margin = attn_ill - flat_ill

    nt_min = str(min(cfg["n_train_curve"])); nt_max = str(max(cfg["n_train_curve"]))
    cos_lo = _mean([m["curve_color_of_shape"][nt_min] for m in per_seed])
    cos_hi = _mean([m["curve_color_of_shape"][nt_max] for m in per_seed])
    ill_lo = _mean([m["curve_illusory"][nt_min] for m in per_seed])
    ill_hi = _mean([m["curve_illusory"][nt_max] for m in per_seed])
    learn_rise = cos_hi - cos_lo  # color-of-shape is the crosstalk/front-end-sensitive learning signal

    fa_c = _mean([m["front_acc_by_train"][nt_max][0] for m in per_seed])
    fa_s = _mean([m["front_acc_by_train"][nt_max][1] for m in per_seed])
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
    learn_ok = learn_rise >= LEARN_RISE_HP

    if not front_ok:
        verdict = "HARD_FAIL_FRONT_END_DEGENERATE"
    elif not flat_in_band:
        verdict = "INCONCLUSIVE_FLAT_NOT_AT_CHANCE"  # illusory probe not actually illusory / test trivial
    elif not label_shuffle_collapsed:
        verdict = "INCONCLUSIVE_FRONT_END_NOT_LEARNED"  # shuffled-label front-end did not collapse
    elif (attn_ill >= ILL_HP and margin >= ILL_MARGIN_HP and scramble_collapsed and learn_ok):
        verdict = "HARD_PASS_ATTENTION_BEATS_FLAT"
    elif attn_ill <= ILL_HF:
        verdict = "HARD_FAIL_CROSSTALK_BEATS_ATTENTION"  # earned bound: attention cannot bind at scale
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s || ILLUSORY-2AFC @M=%d: ATTN=%.3f FLAT=%.3f SCRAM=%.3f margin=%.3f (chance=0.5) || "
        "COLOR-OF-SHAPE @M=%d: ATTN=%.3f FLAT=%.3f (chance~1/present-colors) || "
        "LEARNING-CURVE color-of-shape(train %s->%s)=%.3f->%.3f rise=%.3f ; illusory=%.3f->%.3f || "
        "LABEL-SHUFFLE ATTN illusory=%.3f cos=%.3f (collapse<=%.2f => front-end learned) || "
        "FRONT-END(color=%.3f shape=%.3f floor=%.2f ok=%s) || flat_in_band=%s scramble_collapsed=%s "
        "|| SCALE(ATTN illusory by M)=%s || FREE-BY-CONSTRUCTION novel-conjunction=%.3f (un-gated, NOT headline)" % (
            verdict, Mp, attn_ill, flat_ill, scram_ill, margin, Mp, attn_cos, flat_cos,
            nt_min, nt_max, cos_lo, cos_hi, learn_rise, ill_lo, ill_hi,
            shuf_ill, shuf_cos, LABEL_SHUFFLE_MAX, fa_c, fa_s, FRONT_ACC_MIN, front_ok,
            flat_in_band, scramble_collapsed,
            {M: round(scale[str(M)]["attn_ill"], 3) for M in cfg["M_list"]}, free_gen))

    gates = dict(
        attn_illusory_2afc=attn_ill, flat_illusory_2afc=flat_ill, scram_illusory_2afc=scram_ill,
        illusory_margin=margin, attn_color_of_shape=attn_cos, flat_color_of_shape=flat_cos,
        curve_cos_lo=cos_lo, curve_cos_hi=cos_hi, learn_rise=learn_rise,
        curve_ill_lo=ill_lo, curve_ill_hi=ill_hi,
        front_color_acc=fa_c, front_shape_acc=fa_s, front_end_ok=front_ok,
        label_shuffle_illusory=shuf_ill, label_shuffle_cos=shuf_cos, label_shuffle_collapsed=label_shuffle_collapsed,
        flat_in_band=flat_in_band, scramble_collapsed=scramble_collapsed, learn_ok=learn_ok,
        free_novel_conjunction=free_gen, scale=scale,
        bands=dict(ILL_HP=ILL_HP, ILL_FLAT_MAX=ILL_FLAT_MAX, ILL_MARGIN_HP=ILL_MARGIN_HP,
                   ILL_SCRAMBLE_MAX=ILL_SCRAMBLE_MAX, LEARN_RISE_HP=LEARN_RISE_HP,
                   LABEL_SHUFFLE_MAX=LABEL_SHUFFLE_MAX, FRONT_ACC_MIN=FRONT_ACC_MIN, ILL_HF=ILL_HF))
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs)
# ---------------------------------------------------------------------------
def discriminator_selftest():
    rng = np.random.default_rng(0)
    res = {}
    try:
        import torch
        from hdlab.binding import bind as hb, unbind as hu
        a = make_fhrr_codes(1, 128, rng)[0]; b = make_fhrr_codes(1, 128, rng)[0]
        rb = hb(torch.from_numpy(a), torch.from_numpy(b)).numpy()
        ru = hu(torch.from_numpy(a), torch.from_numpy(b)).numpy()
        reuse_ok = bool(np.allclose(rb, fhrr_bind(a, b), atol=1e-4) and np.allclose(ru, fhrr_unbind(a, b), atol=1e-4))
    except Exception as e:  # noqa: BLE001  (self-test diagnostic only)
        reuse_ok = False
        res["reuse_err"] = str(e)[:200]

    N = 768
    crng = np.random.default_rng(3)
    color_code = make_fhrr_codes(C, N, crng); shape_code = make_fhrr_codes(S, N, crng)

    # front-end LEARNS: more exemplars -> better held-out classification (downstream, color-of-shape)
    st1 = train_front_end(1, np.random.default_rng(11))
    st24 = train_front_end(24, np.random.default_rng(12))
    fa_c24, fa_s24 = front_end_accuracy(st24, np.random.default_rng(13))
    sc1 = _render_scenes(4, 90, st1, 21)
    sc24 = _render_scenes(4, 90, st24, 21)
    ill1, _, cos1, _ = eval_arm_on_scenes(sc1, color_code, shape_code, "ATTN", np.random.default_rng(31), 4)
    ill24, _, cos24, _ = eval_arm_on_scenes(sc24, color_code, shape_code, "ATTN", np.random.default_rng(32), 4)
    front_learns = (fa_c24 >= FRONT_ACC_MIN and fa_s24 >= FRONT_ACC_MIN and (cos24 - cos1) >= 0.05)

    # THE discriminator FIRES: ATTN illusory-2AFC >> FLAT (~chance) on HARD feature-sharing scenes
    flat24, _, _, _ = eval_arm_on_scenes(sc24, color_code, shape_code, "FLAT", np.random.default_rng(33), 4)
    scram24, _, _, _ = eval_arm_on_scenes(sc24, color_code, shape_code, "SCRAM", np.random.default_rng(34), 4)
    fires = (ill24 >= 0.78 and flat24 <= 0.62 and (ill24 - flat24) >= 0.18)

    # TELEMETRY-SENSITIVE: degrading the front-end (fewer exemplars) moves ATTN illusory-2AFC DOWN
    telemetry = (ill24 - ill1) > 0.03

    # LABEL-SHUFFLE must-fail: shuffled-label front-end collapses ATTN to ~chance
    st_shuf = train_front_end(24, np.random.default_rng(41), shuffle_labels=True)
    sc_shuf = _render_scenes(4, 90, st_shuf, 21)
    ill_shuf, _, cos_shuf, _ = eval_arm_on_scenes(sc_shuf, color_code, shape_code, "ATTN", np.random.default_rng(42), 4)
    label_shuffle_collapses = (ill24 - ill_shuf) > 0.12 and ill_shuf <= LABEL_SHUFFLE_MAX

    # scramble collapses (attention localization load-bearing)
    scramble_collapses = (ill24 - scram24) > 0.10

    ok = bool(reuse_ok and front_learns and fires and telemetry and label_shuffle_collapses and scramble_collapses)
    res.update(dict(reuse_ok=reuse_ok, front_learns=bool(front_learns),
                    fa_c24=float(fa_c24), fa_s24=float(fa_s24), cos1=float(cos1), cos24=float(cos24),
                    attn_ill1=float(ill1), attn_ill24=float(ill24), flat_ill24=float(flat24),
                    scram_ill24=float(scram24), label_shuffle_ill=float(ill_shuf),
                    fires=bool(fires), telemetry=bool(telemetry),
                    label_shuffle_collapses=bool(label_shuffle_collapses),
                    scramble_collapses=bool(scramble_collapses)))
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
            verdict_msg="SELFTEST_PASS reuse + front-end-learns + fires + telemetry + label-shuffle + scramble-collapse",
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
            _log("seed=%d ATTN_ill@M%d=%.3f FLAT=%.3f SCRAM=%.3f | curve_cos=%s | shuf_ill=%.3f" % (
                seed, cfg["M_primary"],
                pm["by_M"][str(cfg["M_primary"])]["ATTN"]["illusory_2afc"],
                pm["by_M"][str(cfg["M_primary"])]["FLAT"]["illusory_2afc"],
                pm["by_M"][str(cfg["M_primary"])]["SCRAM"]["illusory_2afc"],
                pm["curve_color_of_shape"], pm["label_shuffle"]["illusory_2afc"]))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # per-seed failure-class instrumentation
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        _atomic_write_metrics(OUTPUT_DIR, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
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
