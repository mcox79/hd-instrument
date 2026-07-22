"""Reader image CONTENT-RECOGNITION (keyless): can a glass-box ink-mask content-encoder
RECOGNIZE woodcut content -- retrieve the right referent BY IMAGE CONTENT with NO stored word-key,
not just BIND it? Extends the grounding brick (exp_reader_image_word_grounding_v1, commit 4ab64c095).

THE KEY DISTINCTION: the grounding brick retrieved by WORD-KEY (association; the key does the work,
content-blind is fine). RECOGNITION = retrieve/classify the referent by IMAGE CONTENT with NO key ->
the image's content must determine the answer -> raw-pixel (content-blind, background-dominated)
should be near-chance = the negative control; ink-mask (content-sensitive, offdiag cosine 0.092 vs
raw 0.252 MEASURED@data/exp_reader_image_word_grounding_v1/metrics.json) is the test.

PROTOCOL (both keyless; content determines the answer, no word-key anywhere):
  PRIMARY   NN-SHARED-REFERENT: each image's NEAREST OTHER image by content cosine -> does it share
            a depictable referent class? acc vs permutation-null chance. Robust to tiny per-class N.
  SECONDARY LEAVE-ONE-OUT class prototype (cross-instance held-out): proto_c = bundle(encode(j) for
            j in c, j != i); predict argmax cosine; multi-label acc1/acc3. i never in its own proto.

MUST-FAIL (the discriminator the grounding brick lacked; keyed retrieval survived scramble via the
  key, keyless content-recognition must NOT):
  1. CONTENT-SCRAMBLE: per-image independent pixel/level shuffle (destroys spatial content, keeps
     level multiset). Content-recognition MUST collapse toward chance.
  2. LABEL-SCRAMBLE: shuffle class membership. LOO recognition MUST collapse to chance.

ARMS (ONE variable = image front-end): rung1_raw (content-blind control) / rung2_edge (reference,
  backfired) / rung2b_ink (the test). IDENTICAL Kanerva record encoder + thermometer levels reused
  from the grounding brick -> the ONLY difference is the front-end + the keyless protocol.

CLASS FILTER (fair, specified, glass-box): word is a referent class iff its PRIMARY (most-frequent)
  WordNet sense is a depictable physical object (noun.animal/artifact/food/plant/body). Removes most
  function-word noise; residual OCR-label noise (come/still/back/john) is an HONEST BOUND, not curated
  away. PRIMARY set K_MIN>=2 (43 classes / 56 imgs); SECONDARY K_MIN>=3 and ANIMAL-only (small-N).

HONEST BOUND: woodcut illustrations are multi-object SCENES with noisy labels + tiny per-class N ->
  recognition is genuinely hard. If ink-mask ALSO fails keyless recognition, that is the honest
  signal that glass-box woodcut recognition needs MORE (resonator scene-factoring or a black-box
  extractor = the strategic fork). Reported cleanly EITHER WAY.

LOCAL ONLY. No push, no remote-persist, no production mutation, no atom banking.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (raw/edge/ink codes bit-differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: recognition = NN-shared/LOO vs perm-null chance + scramble collapse, not a noise-floor cap
# - baseline_in_band: raw = content-blind control near chance; perm-null chance is the floor; scramble
#   + label-scramble are the AG-style discriminator-fires gates
# - deterministic seeding: fixed int seeds only; no hash()-seeded RNG, no list(set()) ordering
# - discriminator-fires: self_test asserts ink NN-shared > raw NN-shared on synthetic shared-fg set
#   + per-image scramble collapses synthetic recognition
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - progress_logging = print_flush_true (cell < 90s; flush anyway)
ASCII-only.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import sys
import time
import traceback
import hashlib
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "reader_image_content_recognition_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse the grounding brick's IDENTICAL encoder + front-ends (one variable = front-end + protocol).
import experiments.exp_reader_image_word_grounding_v1 as GB  # noqa: E402
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
STRUCT_JSON = GB.STRUCT_JSON
FIG_DIR = GB.FIG_DIR

# ---- pre-registered bands (HYPOTHESIZED@preregs/2026-07-21_reader_image_content_recognition_v1.md) ----
CHANCE_EPS = 0.03            # within chance+eps => at chance
INK_LIFT_MIN = 0.05         # ink_nn - chance >= this (robust mean-std) for content-sensitivity
INK_OVER_RAW_MIN = 0.03     # ink_nn - raw_nn >= this: ink beats content-blind control
SCR_COLLAPSE_MIN = 0.03     # ink_clean_nn - ink_scramble_nn >= this: content-driven
RAW_CONTENT_BLIND_MAX = 0.05  # raw_nn - chance <= this: raw is the content-blind control
STRONG_RECOG_MIN = 0.30     # ink_nn >= this = STRONG clean recognition (HYPOTHESIZED unlikely)
KMIN_PRIMARY = 2
SEEDS = [0, 1, 2, 3, 4]
NN_NULL_TRIALS = 200

DEP_LEXNAMES = {"noun.animal", "noun.artifact", "noun.food", "noun.plant", "noun.body"}
ANIMAL_LEXNAMES = {"noun.animal"}


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
# referent classes: word whose PRIMARY WordNet sense is a depictable physical object
# --------------------------------------------------------------------------------------
def _primary_depictable_filter(lexset):
    """fn(word)->bool: True iff word's most-frequent WordNet sense is a noun in lexset."""
    from nltk.corpus import wordnet as wn
    cache = {}

    def ok(w):
        if w in cache:
            return cache[w]
        ss = wn.synsets(w)
        r = bool(ss) and ss[0].pos() == "n" and ss[0].lexname() in lexset
        cache[w] = r
        return r
    return ok


def build_referent_classes(struct_json_path, kmin, lexset):
    """Parse structured JSON -> multi-instance referent classes (deterministic).

    Returns (imgs, classes{word:[imgs]}, img_classes{img:set(words)}). imgs = images covered by
    >= 1 kept class. Uses the grounding brick's STOPWORDS + HEADER_PAT for consistency.
    """
    ok = _primary_depictable_filter(lexset)
    d = json.load(open(struct_json_path, encoding="utf-8"))
    figs = [f for p in d["pages"] for f in p.get("figures", []) if f.get("kind") == "illustration"]
    iw = {}
    for f in figs:
        ws = set()
        for nt in f.get("nearby_text", []):
            if nt.get("rel") not in ("below", "above", "overlap"):
                continue
            for ln in nt.get("text", "").split("\n"):
                if GB.HEADER_PAT.search(ln):
                    continue
                for w in re.findall(r"[A-Za-z]+", ln.lower()):
                    if len(w) >= 3 and w not in GB.STOPWORDS and ok(w):
                        ws.add(w)
        if ws:
            iw[f["img_path"]] = sorted(ws)
    w2i = defaultdict(list)
    for img in sorted(iw):
        for w in iw[img]:
            w2i[w].append(img)
    classes = {w: sorted(v) for w, v in w2i.items() if len(v) >= kmin}
    imgs = sorted(set(i for v in classes.values() for i in v))
    img_classes = {img: set() for img in imgs}
    for w, v in classes.items():
        for img in v:
            img_classes[img].add(w)
    return imgs, classes, img_classes


# --------------------------------------------------------------------------------------
# encode a set of images with a chosen front-end (reuses grounding-brick encoder verbatim)
# --------------------------------------------------------------------------------------
def _feature_maps(grays, front, grid, edge_scale):
    if front == "rung1_raw":
        return [GB.feat_raw(g, grid) for g in grays]
    if front == "rung2_edge":
        return [GB.feat_edge(g, grid, edge_scale=edge_scale) for g in grays]
    if front == "rung2b_ink":
        inv_all = np.concatenate(
            [(255.0 - GB._resize(g, grid * edge_scale)).reshape(-1) for g in grays])
        thr = GB._otsu_threshold(inv_all)
        return [GB.feat_ink(thr, g, grid, edge_scale=edge_scale) for g in grays]
    raise ValueError("unknown front-end %r" % front)


def encode_images(grays, front, grid, Q, N, edge_scale, seed, scramble=False):
    """Return L2-normalized (n,N) content codes. scramble=True => per-image pixel/level shuffle
    (independent permutation per image; destroys spatial content, keeps level multiset)."""
    maps = _feature_maps(grays, front, grid, edge_scale)
    levels = GB.quantize_global(maps, Q)  # (n,grid,grid)
    lv = levels.reshape(levels.shape[0], -1)
    if scramble:
        srng = np.random.default_rng(7000 + seed)
        lv = np.stack([lv[k][srng.permutation(lv.shape[1])] for k in range(lv.shape[0])])
    brng = np.random.default_rng(1000 + seed)
    P = GB.build_position_vectors(lv.shape[1], N, brng)
    L = GB.build_level_codebook(Q, N, brng)
    codes = np.stack([GB.encode_record(lv[k], P, L) for k in range(lv.shape[0])]).astype(np.float32)
    codes /= (np.linalg.norm(codes, axis=1, keepdims=True) + 1e-12)
    return codes


# --------------------------------------------------------------------------------------
# keyless recognition metrics
# --------------------------------------------------------------------------------------
def nn_shared_referent(codes, imgs, img_classes):
    """Fraction of images whose NEAREST OTHER image (content cosine) shares >=1 referent class."""
    n = len(imgs)
    if n < 2:
        return 0.0
    S = codes @ codes.T
    np.fill_diagonal(S, -2.0)
    nn = S.argmax(axis=1)
    hit = 0
    for i in range(n):
        if img_classes[imgs[i]] & img_classes[imgs[nn[i]]]:
            hit += 1
    return hit / n


def nn_shared_chance(imgs, img_classes, trials, seed):
    """Permutation-null: random other-image neighbor, mean shared-referent rate."""
    n = len(imgs)
    if n < 2:
        return 0.0
    rng = np.random.default_rng(999 + seed)
    tot = 0
    for _ in range(trials):
        perm = rng.permutation(n)
        for i in range(n):
            j = perm[i] if perm[i] != i else (perm[i] + 1) % n
            if img_classes[imgs[i]] & img_classes[imgs[j]]:
                tot += 1
    return tot / (trials * n)


def loo_class_recog(codes, imgs, classes, img_classes, label_scramble_seed=None):
    """Leave-one-out cross-instance recognition. label_scramble_seed != None => shuffle class
    membership (must-fail control). Returns (acc1, acc3)."""
    idx = {im: i for i, im in enumerate(imgs)}
    clist = sorted(classes)
    cidx = {c: k for k, c in enumerate(clist)}
    members = {c: [idx[m] for m in classes[c]] for c in clist}
    truth = {im: set(img_classes[im]) for im in imgs}
    if label_scramble_seed is not None:
        # reassign each class's members to a random image-set of the SAME size (structure-preserving
        # null): flatten (img,class) instances and permute the class labels deterministically.
        rng = np.random.default_rng(6000 + label_scramble_seed)
        inst = [(im, c) for c in clist for im in classes[c]]
        labels = [c for (_, c) in inst]
        perm = rng.permutation(len(labels))
        members = {c: [] for c in clist}
        truth = {im: set() for im in imgs}
        for (im, _), pl in zip(inst, [labels[p] for p in perm]):
            members[pl].append(idx[im])
            truth[im].add(pl)
    n = len(imgs)
    acc1 = acc3 = 0
    N = codes.shape[1]
    for i, im in enumerate(imgs):
        protos = np.zeros((len(clist), N), dtype=np.float32)
        valid = []
        for c in clist:
            mem = [m for m in members[c] if m != i]
            if not mem:
                continue
            protos[cidx[c]] = np.sign(codes[mem].sum(axis=0))
            valid.append(cidx[c])
        if not valid:
            continue
        valid = np.array(valid)
        pn = protos / (np.linalg.norm(protos, axis=1, keepdims=True) + 1e-12)
        sims = np.full(len(clist), -2.0)
        sims[valid] = pn[valid] @ codes[i]
        order = np.argsort(-sims)
        true = {cidx[c] for c in truth[im] if c in cidx}
        if not true:
            continue
        if order[0] in true:
            acc1 += 1
        if true & set(order[:3].tolist()):
            acc3 += 1
    return acc1 / n, acc3 / n


# --------------------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------------------
def self_test():
    from hdlab.binding import bsc_bind, bsc_bundle
    import torch
    rng = np.random.default_rng(0)
    N, Q, grid = 2000, 9, 8

    # 1. encode_record bit-identical to hdlab bsc primitives (encoder reused; no drift)
    n_pos = grid * grid
    P = GB.build_position_vectors(n_pos, N, rng)
    L = GB.build_level_codebook(Q, N, rng)
    inten = rng.integers(0, Q, size=n_pos)
    vec = GB.encode_record(inten, P, L)
    stack = [bsc_bind(torch.from_numpy(P[i].astype(np.float32)),
                      torch.from_numpy(L[inten[i]].astype(np.float32))) for i in range(n_pos)]
    prim = bsc_bundle(torch.stack(stack)).numpy().astype(np.int8)
    assert np.array_equal(vec, prim), "encode_record != hdlab bsc primitives"

    # 2. DISCRIMINATOR FIRES (keyless recognition mechanics): a separable synthetic (class = a
    #    position-locked dark shape) -> ink NN-shared recovers the grouping; per-image content-scramble
    #    MUST collapse it (the discriminator the grounding brick lacked: keyed retrieval survived
    #    scramble via the key, keyless content-recognition must NOT); LOO label-scramble MUST collapse.
    def synth_sep(seed):
        r = np.random.default_rng(seed)
        shapes = [np.zeros((32, 32), np.float32) for _ in range(3)]
        shapes[0][8:11, 4:28] = 1.0     # top bar
        shapes[1][4:28, 8:11] = 1.0     # left bar
        shapes[2][14:22, 12:20] = 1.0   # center block
        names = ["cA", "cB", "cC"]
        grays, imgs, img_classes = [], [], {}
        classes = {n: [] for n in names}
        k = 0
        for ci, sh in enumerate(shapes):
            for _ in range(4):
                bg = r.integers(150, 230, size=(32, 32)).astype(np.float32)  # bright noisy bg
                g = bg.copy()
                g[sh > 0] = 25.0            # dark class foreground (ink isolates)
                nm = "img%d" % k
                grays.append(g); imgs.append(nm)
                img_classes[nm] = {names[ci]}; classes[names[ci]].append(nm); k += 1
        return grays, imgs, classes, img_classes
    grays, imgs, classes, img_classes = synth_sep(1)
    c_ink = encode_images(grays, "rung2b_ink", 16, Q, 4000, 4, 0)
    c_raw = encode_images(grays, "rung1_raw", 16, Q, 4000, 4, 0)
    c_edge = encode_images(grays, "rung2_edge", 16, Q, 4000, 4, 0)
    nn_ink = nn_shared_referent(c_ink, imgs, img_classes)
    assert nn_ink >= 0.99, "ink should recover the position-locked grouping (nn=%.3f)" % nn_ink
    c_ink_scr = encode_images(grays, "rung2b_ink", 16, Q, 4000, 4, 0, scramble=True)
    nn_ink_scr = nn_shared_referent(c_ink_scr, imgs, img_classes)
    assert nn_ink_scr <= nn_ink - 0.3, ("content-scramble did not collapse ink recognition "
                                        "(clean %.3f scramble %.3f)" % (nn_ink, nn_ink_scr))
    a1, _ = loo_class_recog(c_ink, imgs, classes, img_classes)
    a1s, _ = loo_class_recog(c_ink, imgs, classes, img_classes, label_scramble_seed=0)
    assert a1 >= 0.99 and a1s <= a1 - 0.3, ("LOO label-scramble must collapse recognition "
                                            "(clean %.3f labelscr %.3f)" % (a1, a1s))

    # 3. RAW IS THE CONTENT-BLIND CONTROL (the mechanism): with a SHARED strong background common to
    #    all images (as woodcut hatching/borders are), raw feature maps carry that shared similarity
    #    (high between-class cosine -> content-blind for cross-instance) while the Otsu ink mask
    #    removes it (low between-class cosine -> separable). This is the grounding brick's measured
    #    offcos raw=0.252 > ink=0.092 mechanism (CITED@data/exp_reader_image_word_grounding_v1/metrics.json).
    def _between_offdiag(maps, labels):
        F = np.stack([m.reshape(-1) for m in maps]).astype(np.float32)
        F = F / (np.linalg.norm(F, axis=1, keepdims=True) + 1e-12)
        Sm = F @ F.T
        diff = labels[:, None] != labels[None, :]
        return float(Sm[diff].mean())
    rr = np.random.default_rng(3)
    shared_bg = rr.integers(150, 255, size=(32, 32)).astype(np.float32)  # identical across all imgs
    shp = [np.zeros((32, 32), np.float32) for _ in range(3)]
    shp[0][8:11, 4:28] = 1; shp[1][4:28, 8:11] = 1; shp[2][14:22, 10:22] = 1
    sg, slab = [], []
    for ci in range(3):
        for _ in range(4):
            g = shared_bg.copy()
            y, x = rr.integers(0, 26), rr.integers(0, 26)
            g[y:y + 8, x:x + 8] = rr.integers(150, 255)   # per-image bright noise (uninformative)
            g[shp[ci] > 0] = 30.0
            sg.append(g); slab.append(ci)
    slab = np.array(slab)
    raw_maps = [GB.feat_raw(g, 16) for g in sg]
    inv = np.concatenate([(255.0 - GB._resize(g, 16 * 4)).reshape(-1) for g in sg])
    thr = GB._otsu_threshold(inv)
    ink_maps = [GB.feat_ink(thr, g, 16, edge_scale=4) for g in sg]
    off_raw = _between_offdiag(raw_maps, slab)
    off_ink = _between_offdiag(ink_maps, slab)
    assert off_raw > off_ink + 0.2, ("content-blindness mechanism not shown: raw between-class "
                                     "offcos %.3f should exceed ink %.3f (raw carries shared bg)"
                                     % (off_raw, off_ink))

    # 4. arms differ (raw vs edge vs ink front-ends produce different codes)
    _arms_must_differ({"raw": c_raw, "edge": c_edge, "ink": c_ink})

    # 5. class filter is SPECIFIED + glass-box: 'dog' (primary=noun.animal) is a referent word,
    #    'the'/'come' handling -> at least a concrete depictable word passes and a stopword does not.
    f = _primary_depictable_filter(DEP_LEXNAMES)
    assert f("dog") and f("hat") and f("basket"), "depictable concrete nouns must pass filter"
    assert not f("the") and not f("and"), "stopword-like tokens must not pass filter"

    # 6. no-nondeterministic-seeding static scan
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as fh:
            assert_no_nondeterministic_seeding(fh.read())
    except ImportError:
        pass

    print("[self_test] PASS: bsc-identical-encoder, discriminator-fires(ink nn=%.3f), "
          "content-scramble-collapses(%.3f->%.3f), LOO-label-scramble-fires(%.3f->%.3f), "
          "raw-content-blind-mechanism(between-class offcos raw=%.3f>ink=%.3f), arms-differ, "
          "specified-class-filter" % (nn_ink, nn_ink, nn_ink_scr, a1, a1s, off_raw, off_ink),
          flush=True)
    return True


# --------------------------------------------------------------------------------------
# main run
# --------------------------------------------------------------------------------------
def _eval_class_set(grays, imgs_all, imgs, classes, img_classes, fronts, grid, Q, N, edge_scale,
                    seeds, is_headline):
    """Evaluate all front-ends on one class set. Returns per-front metrics dict + example codes."""
    sub = [imgs_all.index(im) for im in imgs]  # index into the full encoded stack
    chance_nn = nn_shared_chance(imgs, img_classes, NN_NULL_TRIALS, seed=0)
    per_front = {}
    example_codes = {}
    for front in fronts:
        nn_c, nn_s = [], []
        loo1_c, loo3_c, loo1_lab = [], [], []
        for s in seeds:
            codes_all = encode_images(grays, front, grid, Q, N, edge_scale, s, scramble=False)
            codes = codes_all[sub]
            codes_scr = encode_images(grays, front, grid, Q, N, edge_scale, s, scramble=True)[sub]
            if front not in example_codes:
                example_codes[front] = codes
            nn_c.append(nn_shared_referent(codes, imgs, img_classes))
            nn_s.append(nn_shared_referent(codes_scr, imgs, img_classes))
            a1, a3 = loo_class_recog(codes, imgs, classes, img_classes)
            a1l, _ = loo_class_recog(codes, imgs, classes, img_classes, label_scramble_seed=s)
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
            "chance_loo_top1_analytic": 1.0 / max(len(classes), 1), "fronts": per_front}, example_codes


def run(mode="full"):
    t0 = time.perf_counter()
    if mode == "smoke":
        grid, Q, N, edge_scale = 12, 9, 3000, 4
        seeds = [0, 1]
    else:
        grid, Q, N, edge_scale = 16, 17, 10000, 6
        seeds = SEEDS
    fronts = ["rung1_raw", "rung2_edge", "rung2b_ink"]

    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, mode, expected_n_units=len(seeds) * len(fronts))

    # PRIMARY class set defines the image universe; encode ALL covered images once per (front,seed).
    imgs_all, classes_p, imgc_p = build_referent_classes(STRUCT_JSON, KMIN_PRIMARY, DEP_LEXNAMES)
    grays = [GB.load_gray(os.path.join(FIG_DIR, im)) for im in imgs_all]
    print("[classes] PRIMARY depictable K>=%d: n_img=%d n_classes=%d chance_nn=%.4f"
          % (KMIN_PRIMARY, len(imgs_all), len(classes_p),
             nn_shared_chance(imgs_all, imgc_p, NN_NULL_TRIALS, 0)), flush=True)

    # secondary sets (subsets of the same image universe where possible)
    imgs3, classes3, imgc3 = build_referent_classes(STRUCT_JSON, 3, DEP_LEXNAMES)
    imgsA, classesA, imgcA = build_referent_classes(STRUCT_JSON, 2, ANIMAL_LEXNAMES)

    # ensure secondary imgs are within the encoded universe (they are: subsets of depictable K>=2)
    def _within(imgs):
        return [im for im in imgs if im in imgs_all]
    imgs3 = _within(imgs3); imgsA = _within(imgsA)
    imgc3 = {im: imgc3[im] for im in imgs3}; imgcA = {im: imgcA[im] for im in imgsA}
    classes3 = {c: [m for m in v if m in imgs_all] for c, v in classes3.items()}
    classes3 = {c: v for c, v in classes3.items() if len(v) >= 3}
    classesA = {c: [m for m in v if m in imgs_all] for c, v in classesA.items()}
    classesA = {c: v for c, v in classesA.items() if len(v) >= 2}

    primary, ex_codes = _eval_class_set(grays, imgs_all, imgs_all, classes_p, imgc_p, fronts,
                                        grid, Q, N, edge_scale, seeds, is_headline=True)
    sec_k3, _ = _eval_class_set(grays, imgs_all, imgs3, classes3, imgc3, fronts,
                                grid, Q, N, edge_scale, seeds, is_headline=False)
    sec_an, _ = _eval_class_set(grays, imgs_all, imgsA, classesA, imgcA, fronts,
                                grid, Q, N, edge_scale, seeds, is_headline=False)

    arm_digests = _arms_must_differ({f: ex_codes[f] for f in ex_codes})

    # ---- verdict on the PRIMARY set, NN-shared headline ----
    chance = primary["chance_nn_shared"]
    pf = primary["fronts"]
    ink = pf["rung2b_ink"]; raw = pf["rung1_raw"]
    ink_nn = ink["nn_shared_mean"]; ink_std = ink["nn_shared_std"]
    raw_nn = raw["nn_shared_mean"]
    ink_lift = ink_nn - chance
    ink_lift_robust = (ink_nn - ink_std) - chance          # robust (mean-1std above chance)
    ink_over_raw = ink_nn - raw_nn
    scr_collapse = ink_nn - ink["nn_shared_scramble_mean"]
    raw_over_chance = raw_nn - chance

    content_sensitive = (ink_lift_robust >= INK_LIFT_MIN and
                         ink_over_raw >= INK_OVER_RAW_MIN and
                         scr_collapse >= SCR_COLLAPSE_MIN and
                         raw_over_chance <= RAW_CONTENT_BLIND_MAX)

    if ink_nn >= STRONG_RECOG_MIN and content_sensitive:
        verdict = "GLASSBOX_RECOG_STRONG"
    elif ink_lift < CHANCE_EPS and (raw_nn - chance) < CHANCE_EPS:
        verdict = "RECOG_AT_CHANCE"
    elif content_sensitive:
        verdict = "GLASSBOX_RECOG_CONTENT_SENSITIVE"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        "KEYLESS content-recognition (McGuffey woodcuts, PRIMARY depictable K>=%d, "
        "n_img=%d n_cls=%d): NN-shared chance=%.3f | raw=%.3f(scr=%.3f) edge=%.3f ink=%.3f(scr=%.3f) "
        "| ink_lift=%.3f(robust=%.3f) ink-raw=%.3f scr_collapse=%.3f raw-chance=%.3f "
        "|| LOO acc1: raw=%.3f edge=%.3f ink=%.3f (ink labelscr=%.3f) -> %s"
        % (KMIN_PRIMARY, primary["n_img"], primary["n_classes"], chance,
           raw_nn, raw["nn_shared_scramble_mean"], pf["rung2_edge"]["nn_shared_mean"],
           ink_nn, ink["nn_shared_scramble_mean"],
           ink_lift, ink_lift_robust, ink_over_raw, scr_collapse, raw_over_chance,
           raw["loo_acc1_mean"], pf["rung2_edge"]["loo_acc1_mean"], ink["loo_acc1_mean"],
           ink["loo_acc1_labelscramble_mean"], verdict))

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "reader image keyless content-recognition (McGuffey woodcuts): %s" % verdict,
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "run_mode": mode,
        "config": {"grid": grid, "Q": Q, "N": N, "edge_scale": edge_scale,
                   "seeds": seeds, "kmin_primary": KMIN_PRIMARY, "nn_null_trials": NN_NULL_TRIALS,
                   "class_filter": "primary_wordnet_sense_in_depictable_lexnames",
                   "depictable_lexnames": sorted(DEP_LEXNAMES)},
        "primary_depictable_kge2": primary,
        "secondary_depictable_kge3": sec_k3,
        "secondary_animal_only_kge2_SMALL_N_NOISY": sec_an,
        "verdict_detail": {
            "headline_metric": "nn_shared_referent (keyless: nearest content-neighbor shares referent)",
            "ink_lift_over_chance": ink_lift, "ink_lift_robust_mean_minus_std": ink_lift_robust,
            "ink_over_raw": ink_over_raw, "scramble_collapse": scr_collapse,
            "raw_over_chance_content_blind_check": raw_over_chance,
            "content_sensitive_all_gates": bool(content_sensitive),
            "note": "RECOGNITION (keyless, no word-key) vs the grounding brick's keyed retrieval. "
                    "raw-pixel is the content-blind negative control (background-dominated); ink-mask "
                    "is the content-sensitive test. NN-shared-referent is robust to tiny per-class N; "
                    "LOO is the harder cross-instance held-out generalization (1-2 image prototypes on "
                    "multi-object woodcut scenes = genuinely hard). Label noise from OCR nearby-text is "
                    "an intrinsic honest bound (specified primary-sense filter reduces but cannot remove "
                    "it). CONTENT_SENSITIVE = ink robustly > chance AND > raw AND scramble collapses = "
                    "un-stalls direction but weak absolute recognition -> STRONG needs resonator "
                    "scene-factoring or a black-box extractor (the strategic fork)."},
        "bands": {"CHANCE_EPS": CHANCE_EPS, "INK_LIFT_MIN": INK_LIFT_MIN,
                  "INK_OVER_RAW_MIN": INK_OVER_RAW_MIN, "SCR_COLLAPSE_MIN": SCR_COLLAPSE_MIN,
                  "RAW_CONTENT_BLIND_MAX": RAW_CONTENT_BLIND_MAX, "STRONG_RECOG_MIN": STRONG_RECOG_MIN},
        "must_fail_controls": {"content_scramble": "per-image pixel/level shuffle (spatial content "
                               "destroyed)", "label_scramble": "class membership shuffled (LOO only)"},
        "arms_differ_verified": True, "arm_digests": arm_digests,
        "final_metrics_atomicity": "tmp_replace",
        "primitives_reused": ["exp_reader_image_word_grounding_v1 encoder (encode_record / "
                              "build_position_vectors / build_level_codebook / feat_raw / feat_edge / "
                              "feat_ink / _otsu_threshold / quantize_global) VERBATIM"],
        "recipe_adopted": "Kanerva record encoder + thermometer levels + Otsu ink / Sobel edge "
                          "front-ends (glass-box, specified); keyless NN-shared + LOO class prototypes",
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
