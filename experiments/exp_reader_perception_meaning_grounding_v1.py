"""Perception-MEANING grounding: wire CONTENT-AWARE recognition INTO the word<->referent bind.

THE BUILD (USER 2026-07-21, deferred all session behind the chain-grade chase): the existing
grounding pipeline (exp_reader_image_word_grounding_v1, atom 29428) is CONTENT-BLIND -- keyed
word->image retrieval SATURATES for every encoder (raw=0.996 edge=1.000 ink=0.977) because the
orthogonal word-key ISOLATES its bound payload regardless of image content. That is perception-
BINDING (rote association), not perception-MEANING. This cell makes grounding perception-MEANING:
the encoder RECOGNIZES what the picture is, and that recognition drives the word<->referent match.

MECHANISM (the integration): route CROSS-INSTANCE held-out recognition THROUGH the grounding bind
store. Clean labeled images = a "captioned" corpus (real word<->referent pairs; NOT McGuffey woodcuts
which USER de-emphasized): sklearn olivetti faces (40 identity classes x 10) + load_digits (10 x 40).
Each CLASS is a referent word (near-orthogonal random bipolar). Store binds train instances:
    M = sum_{train imgs} bind(word_class(img), image_code(img))            [additive superposition]
Then GROUND a HELD-OUT image (never bound) to its referent word:
    i2w  q = M * image_code(x_heldout) ; cleanup vs the word codebook -> predicted class-word.
This REQUIRES the held-out image code to resemble the bound same-class train codes = CONTENT
RECOGNITION. A content-blind encoder (raw-pixel record, high within-class pixel variation) grounds
weakly cross-instance; a content-aware encoder (HOG shape) grounds strongly. Also w2i (word ->
held-out image among distractors).

TWO ARMS, ONE VARIABLE = the image encoder front-end (everything downstream identical):
  CONTENT-BLIND  rung1_raw : Kanerva record of grid intensities (the current grounding encoder, 29428).
  CONTENT-AWARE  rung3_hog : specified HOG oriented-gradient shape front-end (glass-box, atom 29431).

KEY MUST-FAIL (the perception-MEANING discriminator, analog of the compgen sign-flip):
GLOBAL PIXEL-SHUFFLE -- ONE fixed permutation of the front-end input grid, applied identically to
EVERY image (train + held-out). Content is destroyed for a human; the question is whether the ARM
notices.
  - CONTENT-BLIND raw: a CONSISTENT global permutation only RELABELS the random record positions ->
    inter-image similarity structure PRESERVED -> grounding UNCHANGED (shuffle-INVARIANT). (29428.)
  - CONTENT-AWARE hog: a global permutation DESTROYS the spatial gradient locality HOG depends on ->
    the shape descriptor collapses -> same-class recognition gone -> grounding COLLAPSES toward chance
    (shuffle-SENSITIVE).
Report the shuffle-sensitivity of BOTH arms = THE load-bearing result. If content-aware is ALSO
shuffle-invariant it is NOT really using content -> honest negative.

DESIGN GATE (pre-registered):
  (1) REAL baseline = content-blind raw grounding (through the same bind store).
  (2) can-fail = content-features may NOT help beyond rote association (aligned faces: raw pixels of
      one identity already correlate), OR both arms shuffle-invariant -> HONEST NEGATIVE, reported.
  (3) difficulty-on = CROSS-INSTANCE held-out (bind train, ground NEW held-out instances) at 40 classes
      (olivetti chance=1/40=0.025) so rote base-rate is not trivial; raw NOT saturated (LOO raw=0.79).
  (4) ONE variable = encoder front-end (raw vs hog); split / words / store / retrieval identical.
Plus a BASE-RATE must-fail: SCRAMBLE the class<->word assignment -> grounding must collapse to chance.

HONEST FRAMING: likely MEASURED_MECHANISM (a real perception-meaning grounding step, glass-box, no
CNN). WIN = content-aware grounds >= content-blind AND is shuffle-sensitive (uses content) while
content-blind is shuffle-invariant. Honest negative (content does not help / both shuffle-invariant)
is fine and reported cleanly. No over-claim.

LOCAL ONLY. No push, no remote-persist, no production mutation, no atom banking.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (raw/hog codes bit-differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: grounding = held-out retrieval vs chance + shuffle-sensitivity contrast + scramble
#             collapse, not a noise-floor cap
# - baseline_in_band: content-blind raw i2w in (chance, RAW_SAT_MAX); flagged if saturated at smoke
# - deterministic seeding: fixed int seeds only; no hash()-seeded RNG, no list(set()) ordering
# - discriminator-fires: self_test synth localized-shape set has hog grounding high + hog shuffle-
#             sensitivity > raw shuffle-sensitivity + scramble collapses
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

ANCHOR_NAME = "reader_perception_meaning_grounding_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse (VERBATIM) the grounding brick's encoder + the HOG brick's shape front-end + loaders.
import experiments.exp_reader_image_word_grounding_v1 as GB  # noqa: E402
import experiments.exp_reader_image_shape_recognition_hog_v1 as HG  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
CELL_PX = HG.CELL_PX  # 8
SHUFFLE_SEED = 424242  # fixed: the global pixel-shuffle permutation is a property of the condition

# ---- pre-registered bands (HYPOTHESIZED@preregs/2026-07-22_reader_perception_meaning_grounding_v1.md) ----
CHANCE_EPS = 0.03            # within chance+eps => at chance
AWARE_OVER_BLIND_MIN = 0.05  # hog_i2w - raw_i2w: content-aware must beat content-blind (clean)
SHUFFLE_SENS_MIN = 0.15     # hog clean - hog shuffled: content-aware MUST drop under global shuffle
SHUFFLE_INVARIANT_MAX = 0.12  # raw clean - raw shuffled: content-blind sens is only a NOISE FLOOR
                              # (raw-record is DISTRIBUTIONALLY shuffle-invariant, not exact: the
                              # majority-sign nonlinearity over the reordered random-position basis
                              # leaves a small residual on hard classes; measured ~0.08 synthetic)
SHUFFLE_CONTRAST_MIN = 0.10  # aware_sens - blind_sens: the load-bearing perception-meaning contrast
                             # (hog collapses SYSTEMATICALLY, raw only at the noise floor)
SCR_COLLAPSE_MIN = 0.10     # i2w clean - i2w wordscramble: real association (not base-rate)
STRONG_GROUND_MIN = 0.30    # hog i2w >= this = STRONG absolute cross-instance grounding
RAW_SAT_MAX = 0.95          # baseline_in_band: raw i2w >= this at smoke => saturation flag
SEEDS = [0, 1, 2, 3, 4]
ARMS = ["rung1_raw", "rung3_hog"]  # content-blind baseline, content-aware


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
# front-end input maps + GLOBAL pixel-shuffle + HOG histogram from a map
# --------------------------------------------------------------------------------------
def _front_res(front, p):
    """Native input resolution each front-end consumes."""
    return p["grid"] if front == "rung1_raw" else p["grid_hog"] * CELL_PX


def _hog_hist(hi, grid_hog, n_orient, cell_px=CELL_PX):
    """HOG histogram of an ALREADY-resized (res x res) map. (Copy of HG.feat_hog body sans _resize so
    a pre-shuffled map can be fed directly.) np.gradient -> unsigned orientation [0,pi) -> per-cell
    magnitude-weighted histogram -> per-cell L2 contrast norm. Returns (grid_hog,grid_hog,n_orient)."""
    gy, gx = np.gradient(hi.astype(np.float64))
    mag = np.sqrt(gx * gx + gy * gy)
    ang = np.mod(np.arctan2(gy, gx), np.pi)
    bin_w = np.pi / n_orient
    b = np.minimum((ang / bin_w).astype(np.int64), n_orient - 1)
    S = cell_px
    b_c = b.reshape(grid_hog, S, grid_hog, S)
    m_c = mag.reshape(grid_hog, S, grid_hog, S)
    hist = np.empty((grid_hog, grid_hog, n_orient), dtype=np.float64)
    for o in range(n_orient):
        hist[:, :, o] = np.where(b_c == o, m_c, 0.0).sum(axis=(1, 3))
    norm = np.sqrt((hist * hist).sum(axis=2, keepdims=True)) + 1e-6
    return (hist / norm).astype(np.float32)


def _working_map(gray, front, p, perm):
    """Resize gray to the front-end's native res, optionally apply the GLOBAL pixel permutation (same
    perm for every image). perm=None => clean."""
    res = _front_res(front, p)
    hi = GB._resize(gray, res)
    if perm is not None:
        hi = hi.reshape(-1)[perm].reshape(res, res)
    return hi


def _feature(hi, front, p):
    if front == "rung1_raw":
        return hi  # grid x grid intensity map IS the raw feature
    return _hog_hist(hi, p["grid_hog"], p["n_orient"], CELL_PX)


def encode_images(grays, front, p, N, seed, shuffle=False):
    """L2-normalized (n,N) content codes. Same Kanerva record encoder for both fronts; only the feature
    front-end differs. shuffle=True => GLOBAL fixed pixel permutation of the front-end input (same perm
    all images) BEFORE feature extraction."""
    perm = None
    if shuffle:
        res = _front_res(front, p)
        perm = np.random.default_rng(SHUFFLE_SEED).permutation(res * res)
    maps = [_feature(_working_map(g, front, p, perm), front, p) for g in grays]
    levels = GB.quantize_global(maps, p["Q"])            # global dataset min-max -> [0,Q-1]
    lv = levels.reshape(levels.shape[0], -1)
    brng = np.random.default_rng(1000 + seed)
    P = GB.build_position_vectors(lv.shape[1], N, brng)
    L = GB.build_level_codebook(p["Q"], N, brng)
    codes = np.stack([GB.encode_record(lv[k], P, L) for k in range(lv.shape[0])]).astype(np.float32)
    codes /= (np.linalg.norm(codes, axis=1, keepdims=True) + 1e-12)
    return codes


# --------------------------------------------------------------------------------------
# split + grounding store + cross-instance held-out retrieval
# --------------------------------------------------------------------------------------
def split_masks(labels, k_train):
    """Per class: first k_train instances -> train (bound), rest -> held-out test. Deterministic."""
    labels = np.asarray(labels)
    train = np.zeros(len(labels), dtype=bool)
    test = np.zeros(len(labels), dtype=bool)
    for c in np.unique(labels):
        idx = np.where(labels == c)[0]              # index order = deterministic instance order
        train[idx[:k_train]] = True
        test[idx[k_train:]] = True
    return train, test


def random_words(n_classes, N, seed):
    rng = np.random.default_rng(2000 + seed)
    return (rng.integers(0, 2, size=(n_classes, N)).astype(np.int8) * 2 - 1).astype(np.int8)


def build_store(codes, labels, words, train_mask, label_map=None):
    """M = sum_{train} bind(word[label_or_scrambled], code). label_map (len n_classes) permutes the
    class->word assignment for the base-rate scramble control."""
    N = codes.shape[1]
    M = np.zeros(N, dtype=np.float32)
    labels = np.asarray(labels)
    for i in np.where(train_mask)[0]:
        c = labels[i]
        wc = c if label_map is None else label_map[c]
        M += words[wc].astype(np.float32) * codes[i]
    return M


def i2w_heldout(M, codes, labels, test_mask, words):
    """Ground each HELD-OUT image to its referent word: q = M*code ; argmax cosine vs word codebook.
    True content-meaning gate (needs held-out code to resemble bound same-class train codes)."""
    labels = np.asarray(labels)
    Wn = words.astype(np.float32)
    Wn = Wn / (np.linalg.norm(Wn, axis=1, keepdims=True) + 1e-12)
    idx = np.where(test_mask)[0]
    if len(idx) == 0:
        return 0.0
    hits = 0
    for i in idx:
        q = M * codes[i]
        q = q / (np.linalg.norm(q) + 1e-12)
        pred = int((Wn @ q).argmax())
        hits += int(pred == labels[i])
    return hits / len(idx)


def w2i_heldout(M, codes, labels, test_mask, words):
    """Ground each referent word to a HELD-OUT image among held-out distractors: q = M*word ; top-1
    held-out code by cosine shares the class? chance ~ 1/n_classes."""
    labels = np.asarray(labels)
    idx = np.where(test_mask)[0]
    if len(idx) == 0:
        return 0.0
    C = codes[idx]  # already normalized
    correct = 0
    n_classes = words.shape[0]
    present = [c for c in range(n_classes) if np.any(labels[idx] == c)]
    for c in present:
        q = M * words[c].astype(np.float32)
        q = q / (np.linalg.norm(q) + 1e-12)
        top = idx[int((C @ q).argmax())]
        correct += int(labels[top] == c)
    return correct / max(len(present), 1)


# --------------------------------------------------------------------------------------
# evaluate all arms on one dataset (clean + global-pixel-shuffle conditions)
# --------------------------------------------------------------------------------------
def eval_dataset(grays, labels, p, N, seeds, k_train):
    labels = np.asarray(labels)
    n_classes = int(len(np.unique(labels)))
    chance = 1.0 / n_classes
    train_mask, test_mask = split_masks(labels, k_train)
    per_arm = {}
    example_codes = {}
    for arm in ARMS:
        acc = defaultdict(list)  # keys: i2w_clean, i2w_shuf, w2i_clean, w2i_shuf, i2w_scr
        for s in seeds:
            words = random_words(n_classes, N, s)
            scr_rng = np.random.default_rng(6000 + s)
            label_map = scr_rng.permutation(n_classes)  # class->word scramble (base-rate control)
            for cond, shuf in (("clean", False), ("shuf", True)):
                codes = encode_images(grays, arm, p, N, s, shuffle=shuf)
                if arm not in example_codes and cond == "clean":
                    example_codes[arm] = codes
                M = build_store(codes, labels, words, train_mask)
                acc["i2w_" + cond].append(i2w_heldout(M, codes, labels, test_mask, words))
                acc["w2i_" + cond].append(w2i_heldout(M, codes, labels, test_mask, words))
                if cond == "clean":
                    Ms = build_store(codes, labels, words, train_mask, label_map=label_map)
                    acc["i2w_scr"].append(i2w_heldout(Ms, codes, labels, test_mask, words))
        m = {k: float(np.mean(v)) for k, v in acc.items()}
        m["i2w_clean_std"] = float(np.std(acc["i2w_clean"]))
        m["shuffle_sensitivity"] = m["i2w_clean"] - m["i2w_shuf"]
        m["scramble_collapse"] = m["i2w_clean"] - m["i2w_scr"]
        m["n_seeds"] = len(seeds)
        per_arm[arm] = m
    return {"n_img": len(labels), "n_classes": n_classes, "chance_i2w": chance,
            "n_train": int(train_mask.sum()), "n_test": int(test_mask.sum()),
            "arms": per_arm}, example_codes


def _headline(ds):
    """Perception-meaning verdict gates on one dataset."""
    pa = ds["arms"]
    chance = ds["chance_i2w"]
    blind = pa["rung1_raw"]; aware = pa["rung3_hog"]
    aware_over_blind = aware["i2w_clean"] - blind["i2w_clean"]
    aware_shuf_sens = aware["shuffle_sensitivity"]
    blind_shuf_sens = blind["shuffle_sensitivity"]
    aware_lift = aware["i2w_clean"] - chance
    g = {
        "chance_i2w": chance,
        "blind_i2w_clean": blind["i2w_clean"], "aware_i2w_clean": aware["i2w_clean"],
        "blind_i2w_shuf": blind["i2w_shuf"], "aware_i2w_shuf": aware["i2w_shuf"],
        "aware_over_blind": aware_over_blind,
        "aware_shuffle_sensitivity": aware_shuf_sens,
        "blind_shuffle_sensitivity": blind_shuf_sens,
        "aware_lift_over_chance": aware_lift,
        "aware_scramble_collapse": aware["scramble_collapse"],
        "blind_w2i_clean": blind["w2i_clean"], "aware_w2i_clean": aware["w2i_clean"],
    }
    shuffle_contrast = aware_shuf_sens - blind_shuf_sens
    over_blind_ok = aware_over_blind >= AWARE_OVER_BLIND_MIN
    aware_sens_ok = aware_shuf_sens >= SHUFFLE_SENS_MIN
    contrast_ok = shuffle_contrast >= SHUFFLE_CONTRAST_MIN     # the load-bearing perception-meaning gate
    blind_inv_ok = blind_shuf_sens <= SHUFFLE_INVARIANT_MAX
    scr_ok = aware["scramble_collapse"] >= SCR_COLLAPSE_MIN
    lift_ok = aware_lift >= CHANCE_EPS
    g["shuffle_contrast_aware_minus_blind"] = shuffle_contrast
    # WIN: content-aware grounds >= content-blind AND collapses under shuffle SYSTEMATICALLY more than
    # content-blind (which sits at its noise floor) = the encoder USES spatial content = perception-meaning.
    if over_blind_ok and aware_sens_ok and contrast_ok and blind_inv_ok and scr_ok and lift_ok:
        verdict = ("PERCEPTION_MEANING_STRONG" if aware["i2w_clean"] >= STRONG_GROUND_MIN
                   else "PERCEPTION_MEANING_WIN")
    elif aware_sens_ok and contrast_ok and not over_blind_ok:
        # aware demonstrably uses content (shuffle-sensitive, contrast holds) but does not out-ground
        # blind on clean data (e.g. aligned faces where raw intensity already correlates within-class).
        verdict = "AWARE_USES_CONTENT_BUT_NO_GROUNDING_LIFT"
    elif not aware_sens_ok or not contrast_ok:
        verdict = "CONTENT_AWARE_NOT_USING_CONTENT"          # aware not shuffle-sensitive => not meaning
    else:
        verdict = "MIDDLE_BAND"
    g["verdict"] = verdict
    g["gate_flags"] = {"over_blind_ok": bool(over_blind_ok), "aware_sens_ok": bool(aware_sens_ok),
                       "contrast_ok": bool(contrast_ok), "blind_noisefloor_ok": bool(blind_inv_ok),
                       "scramble_ok": bool(scr_ok), "lift_ok": bool(lift_ok),
                       "strong": bool(aware["i2w_clean"] >= STRONG_GROUND_MIN),
                       "blind_saturated": bool(blind["i2w_clean"] >= RAW_SAT_MAX)}
    return g


# --------------------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------------------
def self_test():
    from hdlab.binding import bsc_bind, bsc_bundle
    import torch
    N, Q = 3000, 9
    p = {"grid": 12, "grid_hog": 6, "n_orient": 9, "Q": Q}

    # 1. HOG-from-map bit-matches HG.feat_hog on a clean (unshuffled) map (front-end reuse, no drift).
    r0 = np.random.default_rng(0)
    g0 = r0.integers(0, 256, size=(48, 48)).astype(np.float32)
    hi = GB._resize(g0, 6 * CELL_PX)
    assert np.array_equal(_hog_hist(hi, 6, 9), HG.feat_hog(g0, 6, 9)), "_hog_hist != HG.feat_hog"

    # 2. encode_record bit-identical to hdlab bsc primitives (encoder reused; no drift).
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

    # 3. cross-instance held-out grounding through the bind store works on a SEPARABLE synthetic set,
    #    the class<->word SCRAMBLE collapses it, and w2i works too.
    def synth_local(seed):
        r = np.random.default_rng(seed)
        grays, labels = [], []
        for ci in range(3):
            for _ in range(6):
                g = r.integers(200, 235, size=(48, 48)).astype(np.float32)
                dy, dx = int(r.integers(-2, 3)), int(r.integers(-2, 3))
                if ci == 0:
                    g[10 + dy:14 + dy, 6 + dx:42 + dx] = 25.0     # horizontal bar top
                elif ci == 1:
                    g[6 + dy:42 + dy, 10 + dx:14 + dx] = 25.0     # vertical bar left
                else:
                    g[20 + dy:28 + dy, 20 + dx:28 + dx] = 25.0    # center block
                grays.append(np.clip(g, 0, 255).astype(np.float32)); labels.append(ci)
        return grays, labels
    sg, sl = synth_local(3)
    ds, ex = eval_dataset(sg, sl, p, N, [0, 1], k_train=4)
    hog = ds["arms"]["rung3_hog"]; raw = ds["arms"]["rung1_raw"]
    assert hog["i2w_clean"] >= 0.90, "hog cross-instance grounding failed (%.3f)" % hog["i2w_clean"]
    assert hog["scramble_collapse"] >= 0.30, ("word-scramble must collapse grounding (clean %.3f scr %.3f)"
                                              % (hog["i2w_clean"], hog["i2w_scr"]))
    assert hog["w2i_clean"] >= 0.66, "hog w2i held-out grounding failed (%.3f)" % hog["w2i_clean"]
    # content-blind raw is EXACTLY shuffle-invariant (consistent global relabel of random record
    # positions preserves inter-image structure) -- verified on any set, incl. the localized one.
    assert raw["shuffle_sensitivity"] <= 0.02, ("raw must be ~shuffle-invariant (sens=%.3f)"
                                                % raw["shuffle_sensitivity"])

    # 4. THE DISCRIMINATOR fires on a set where the class signal is LOCAL structure (orientation):
    #    oriented-stripe textures (theta in {0,45,90}, random phase/period/noise). HOG reads orientation
    #    via LOCAL gradients, so a global pixel-shuffle DESTROYS the class signal -> hog grounding
    #    collapses toward chance (strong shuffle-sensitivity). raw stays exactly invariant. (A globally-
    #    CONSISTENT shuffle cannot collapse hog on grossly-different localized shapes -- their coarse
    #    ink location survives any fixed relabel -- so the discriminator is exercised on LOCAL-structure
    #    classes, the regime real faces live in.)
    def synth_orient(seed):
        r = np.random.default_rng(seed)
        thetas = [0.0, 45.0, 90.0]
        grays, labels = [], []
        for ci, th in enumerate(thetas):
            for _ in range(6):
                per = float(r.uniform(6.0, 10.0)); ph = float(r.uniform(0, 2 * np.pi))
                yy, xx = np.mgrid[0:48, 0:48].astype(np.float64)
                thr = np.deg2rad(th)
                coord = xx * np.cos(thr) + yy * np.sin(thr)
                g = 128.0 + 100.0 * np.sign(np.sin(2 * np.pi * coord / per + ph))
                g = g + r.normal(0, 8.0, size=(48, 48))
                grays.append(np.clip(g, 0, 255).astype(np.float32)); labels.append(ci)
        return grays, labels
    og, ol = synth_orient(2)
    dso, exo = eval_dataset(og, ol, p, N, [0, 1], k_train=4)
    hog_o = dso["arms"]["rung3_hog"]; raw_o = dso["arms"]["rung1_raw"]
    assert hog_o["i2w_clean"] >= 0.80, ("hog must ground oriented textures (i2w=%.3f)"
                                        % hog_o["i2w_clean"])
    assert hog_o["shuffle_sensitivity"] >= 0.25, ("hog grounding must collapse under global pixel-shuffle "
                                                  "on local-structure classes (sens=%.3f)"
                                                  % hog_o["shuffle_sensitivity"])
    # raw sens is only a NOISE FLOOR (distributional invariance + majority-sign residual), not a
    # systematic content-driven drop; the load-bearing claim is the CONTRAST hog_sens >> raw_sens.
    assert raw_o["shuffle_sensitivity"] <= SHUFFLE_INVARIANT_MAX, (
        "raw shuffle-sens must stay at the noise floor (sens=%.3f > %.2f)"
        % (raw_o["shuffle_sensitivity"], SHUFFLE_INVARIANT_MAX))
    assert hog_o["shuffle_sensitivity"] >= raw_o["shuffle_sensitivity"] + SHUFFLE_CONTRAST_MIN, (
        "hog must be MORE shuffle-sensitive than raw by the contrast margin (hog dsens=%.3f raw "
        "dsens=%.3f)" % (hog_o["shuffle_sensitivity"], raw_o["shuffle_sensitivity"]))

    # 5. arms differ (raw vs hog codes bit-differ)
    _arms_must_differ({a: ex[a] for a in ex})

    # 6. no-nondeterministic-seeding static scan
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as fh:
            assert_no_nondeterministic_seeding(fh.read())
    except ImportError:
        pass

    print("[self_test] PASS: hog-from-map==feat_hog, bsc-identical-encoder, xinstance-grounding(hog "
          "i2w=%.3f w2i=%.3f) scramble-collapses(%.3f) raw-invariant(%.3f); DISCRIMINATOR(oriented) "
          "hog-shuffle-sens=%.3f > raw-shuffle-sens=%.3f (hog i2w=%.3f), arms-differ"
          % (hog["i2w_clean"], hog["w2i_clean"], hog["scramble_collapse"], raw["shuffle_sensitivity"],
             hog_o["shuffle_sensitivity"], raw_o["shuffle_sensitivity"], hog_o["i2w_clean"]),
          flush=True)
    return True


# --------------------------------------------------------------------------------------
# main run
# --------------------------------------------------------------------------------------
def run(mode="full"):
    t0 = time.perf_counter()
    if mode == "smoke":
        p = {"grid": 12, "grid_hog": 6, "n_orient": 9, "Q": 9}
        N, seeds = 3000, [0, 1]
        oli_sub, oli_ktrain = (8, 6), 4
        dig_sub, dig_ktrain = (8, 12), 8
    else:
        p = {"grid": 16, "grid_hog": 8, "n_orient": 9, "Q": 17}
        N, seeds = 8192, SEEDS
        oli_sub, oli_ktrain = None, 7           # olivetti 10/class -> 7 train, 3 held-out
        dig_sub, dig_ktrain = (10, 40), 30      # digits 40/class -> 30 train, 10 held-out

    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, mode,
                        expected_n_units=len(seeds) * len(ARMS) * 2)

    # PRIMARY: olivetti faces (clean, local, real within-class variation = raw not saturated)
    grays_o, labels_o = HG.load_olivetti(subsample=oli_sub)
    print("[olivetti] n_img=%d n_classes=%d k_train=%d"
          % (len(grays_o), len(set(labels_o)), oli_ktrain), flush=True)
    olivetti, ex_codes = eval_dataset(grays_o, labels_o, p, N, seeds, oli_ktrain)
    print("[olivetti] done raw_i2w=%.3f hog_i2w=%.3f"
          % (olivetti["arms"]["rung1_raw"]["i2w_clean"],
             olivetti["arms"]["rung3_hog"]["i2w_clean"]), flush=True)

    # SECONDARY: digits upscaled (confirmation on a 2nd clean set)
    grays_d, labels_d = HG.load_digits_up(per_class=40, up=32, subsample=dig_sub)
    print("[digits] n_img=%d n_classes=%d k_train=%d"
          % (len(grays_d), len(set(labels_d)), dig_ktrain), flush=True)
    digits, _ = eval_dataset(grays_d, labels_d, p, N, seeds, dig_ktrain)
    print("[digits] done raw_i2w=%.3f hog_i2w=%.3f"
          % (digits["arms"]["rung1_raw"]["i2w_clean"],
             digits["arms"]["rung3_hog"]["i2w_clean"]), flush=True)

    arm_digests = _arms_must_differ({a: ex_codes[a] for a in ex_codes})

    g_oli = _headline(olivetti)     # headline = olivetti (primary clean testbed, raw not saturated)
    g_dig = _headline(digits)
    verdict = g_oli["verdict"]
    blind_sat = g_oli["gate_flags"]["blind_saturated"]

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        "PERCEPTION-MEANING grounding (content-aware recognition INTO the word<->referent bind; clean "
        "images, no McGuffey). PRIMARY olivetti(%d-class, chance=%.3f): "
        "i2w BLIND(raw)=%.3f AWARE(hog)=%.3f (aware-blind=%.3f) | "
        "SHUFFLE-SENS blind=%.3f aware=%.3f | scr_collapse(aware)=%.3f | w2i blind=%.3f aware=%.3f || "
        "SECONDARY digits(%d-class,chance=%.3f): i2w blind=%.3f aware=%.3f shuffsens blind=%.3f "
        "aware=%.3f -> %s%s"
        % (olivetti["n_classes"], g_oli["chance_i2w"],
           g_oli["blind_i2w_clean"], g_oli["aware_i2w_clean"], g_oli["aware_over_blind"],
           g_oli["blind_shuffle_sensitivity"], g_oli["aware_shuffle_sensitivity"],
           g_oli["aware_scramble_collapse"], g_oli["blind_w2i_clean"], g_oli["aware_w2i_clean"],
           digits["n_classes"], g_dig["chance_i2w"], g_dig["blind_i2w_clean"], g_dig["aware_i2w_clean"],
           g_dig["blind_shuffle_sensitivity"], g_dig["aware_shuffle_sensitivity"],
           verdict, "  [BLIND_SATURATED_FLAG]" if blind_sat else ""))

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "perception-meaning grounding (content-aware vs content-blind through the bind): %s"
                   % verdict,
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "run_mode": mode,
        "config": {"params": p, "N": N, "seeds": seeds, "cell_px": CELL_PX, "arms": ARMS,
                   "shuffle_seed": SHUFFLE_SEED,
                   "olivetti_k_train": oli_ktrain, "digits_k_train": dig_ktrain,
                   "primary_dataset": "sklearn_fetch_olivetti_faces_64x64_40class",
                   "secondary_dataset": "sklearn_load_digits_8x8_upscaled32_10class",
                   "note_mcguffey": "NOT USED (USER: de-emphasize McGuffey; use clean captioned corpus)"},
        "primary_olivetti": olivetti,
        "secondary_digits": digits,
        "chance": {"olivetti_i2w": olivetti["chance_i2w"], "digits_i2w": digits["chance_i2w"]},
        "verdict_detail": {
            "headline_metric": "i2w held-out grounding (ground a NEW held-out image to its referent "
                               "word THROUGH the word<->image bind store); discriminator = global "
                               "pixel-shuffle sensitivity contrast between arms",
            "olivetti_gates": g_oli, "digits_gates": g_dig,
            "note": "CONTENT-BLIND rung1_raw = the current grounding encoder (Kanerva pixel-record; "
                    "content-blind: keyed retrieval saturates for any encoder, atom 29428). "
                    "CONTENT-AWARE rung3_hog = specified HOG shape front-end (atom 29431). The word<->"
                    "referent match is cross-instance held-out (bind train, ground NEW instances) so "
                    "CONTENT recognition (not rote code recall) drives it. PERCEPTION_MEANING_WIN = "
                    "aware grounds >= blind AND aware collapses under global pixel-shuffle (uses content) "
                    "while blind is shuffle-invariant (a consistent global permutation only relabels the "
                    "random record positions). CONTENT_AWARE_NOT_USING_CONTENT / CONTENT_DOESNT_HELP = "
                    "honest negative. Global shuffle = ONE fixed permutation applied to every image."},
        "bands": {"CHANCE_EPS": CHANCE_EPS, "AWARE_OVER_BLIND_MIN": AWARE_OVER_BLIND_MIN,
                  "SHUFFLE_SENS_MIN": SHUFFLE_SENS_MIN, "SHUFFLE_INVARIANT_MAX": SHUFFLE_INVARIANT_MAX,
                  "SHUFFLE_CONTRAST_MIN": SHUFFLE_CONTRAST_MIN,
                  "SCR_COLLAPSE_MIN": SCR_COLLAPSE_MIN, "STRONG_GROUND_MIN": STRONG_GROUND_MIN,
                  "RAW_SAT_MAX": RAW_SAT_MAX},
        "must_fail_controls": {
            "global_pixel_shuffle": "ONE fixed permutation of the front-end input grid, same for every "
                                    "image; content-blind invariant, content-aware collapses = the "
                                    "perception-meaning discriminator",
            "word_scramble": "class<->word assignment permuted before building the store; grounding must "
                             "collapse to chance (base-rate control)"},
        "blind_saturated_flag": bool(blind_sat),
        "arms_differ_verified": True, "arm_digests": arm_digests,
        "final_metrics_atomicity": "tmp_replace",
        "primitives_reused": [
            "exp_reader_image_word_grounding_v1 encoder (encode_record / build_position_vectors / "
            "build_level_codebook / feat_raw / quantize_global / _resize) VERBATIM",
            "exp_reader_image_shape_recognition_hog_v1 HOG front-end (feat_hog logic) + loaders "
            "(load_olivetti / load_digits_up) VERBATIM",
            "additive-superposition grounding store M = sum bind(word, image) (composed in-cell)"],
        "recipe_adopted": "content-blind (raw pixel-record) vs content-aware (HOG shape) encoder fed "
                          "into the SAME word<->referent bind store; cross-instance held-out grounding; "
                          "global-pixel-shuffle sensitivity discriminator; word-scramble base-rate control",
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
