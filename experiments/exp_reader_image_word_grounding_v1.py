"""Reader image<->word grounding brick: encode McGuffey First Reader illustrations,
bind them to their lesson referent-words, and HONESTLY MEASURE whether it grounds.

THE QUESTION (not an assertion): can encoded illustrations be told apart enough to
ground DIFFERENT words to DIFFERENT images? Round-trip through an additive-superposition
associative memory + retrieval-accuracy discrimination vs chance, RUNG-1 (raw-pixel HD)
vs RUNG-2 (glass-box Sobel edge/contour) vs RUNG-2b (glass-box Otsu ink-mask). The recon
(_probe_hd_encoder_woodcuts.json) found raw-pixel HD PRESERVES structure (unbind recovers
per-position intensity ~0.80) but DISCRIMINATES woodcut CONTENT poorly (inter-image cosine
0.34-0.53 vs random ~0) = background-domination. Rung-2 isolates contours to suppress the
shared flat background. This cell measures which rung (if any) grounds, and reports the
honest bound EITHER WAY.

PAIRING (image<->referent-words):
  data/exp_textbook_extract_mcguffey_v1/mcguffey_first_structured.json pages[].figures[]
  kind=='illustration' (wordlist_strip EXCLUDED). nearby_text (rel above/below/overlap)
  -> content words -> concrete-object nouns via WordNet lexname (glass-box specified filter:
  noun.animal/artifact/food/plant/body/object/shape/substance). e.g. p009 -> dog, p010 -> cat.
  CLEAN pairs = words appearing in exactly ONE image (unambiguous single-referent grounding).

ENCODE (both glass-box, no learned CNN):
  RUNG-1 raw   : resize grayscale to gridxgrid, global [0,255]->[0,Q-1] -> record encoder.
  RUNG-2 edge  : Sobel gradient magnitude (fixed kernels) at grid*S res, pool to gridxgrid,
                 GLOBAL dataset min-max -> [0,Q-1] -> record encoder. Flat bg -> grad ~0 ->
                 level 0 (background SUPPRESSED); contours carry the signal.
  RUNG-2b ink  : global-Otsu binary ink mask (fixed threshold rule), pool, quantize.
  All three reuse the SAME Kanerva record-based position-value encoder + Rahimi/Kleyko
  thermometer level code as exp_image_hd_encoder_digits_v1 (atom 29407). ONE variable
  across rungs = the image front-end; positions/levels/words/store/retrieval identical.

ASSOCIATE (additive map = the grounding store):
  M = sum_p bsc_bind(word_p, image_p) over clean pairs (unsigned additive superposition;
  bsc_bind = elementwise mul). This IS the additive-map grounding store composed from
  primitives (no production hdlab mutation).

MEASURE (the HONEST TEST):
  (a) ROUND-TRIP: word -> bind(M, word) -> cleanup vs image codebook (word->image);
      image -> bind(M, image) -> cleanup vs word codebook (image->word). Does it retrieve?
  (b) DISCRIMINATION: retrieval acc@1 / acc@3 vs chance (1/N_img, 1/N_word). RUNG-1 vs
      RUNG-2 vs RUNG-2b. Plus a LOAD SWEEP (bundle P pairs, P in {8,16,32,64,all}) that
      SEPARATES capacity (crosstalk grows with P) from separability (fails even at P=8 =
      pure encoder bound). Plus the mechanistic explainer: image-codebook mean off-diagonal
      cosine per rung (lower = more separable; recon measured rung-1 ~0.4).
  (c) HONEST BOUND: report acc vs chance. Do NOT claim grounding works if at chance.

MUST-FAIL (the discipline that PREVENTS a false PASS): SCRAMBLE permutes the word<->image
  assignment before building M. A rung that only 'works' via base-rate keeps its accuracy
  under scramble; a rung that uses the REAL association collapses toward chance. A 'works'
  claim REQUIRES (acc >> chance) AND (true_acc - scramble_acc >= SCR_DELTA_MIN).

DESIGN GATE (pre-registered): real baseline = chance retrieval + scramble control;
  can-fail = discrimination at chance is an HONEST NEGATIVE (raw-pixel grounding does not
  work -> rung-2 / better encoder needed); one-variable = image front-end across rungs;
  multi-seed over (encoder base seed, word-HD seed). GLASS-BOX + deterministic.

LOCAL ONLY. No push, no remote-persist, no production mutation, no atom banking.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; rungs bit-differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: discrimination = retrieval-vs-chance + scramble delta, not a noise-floor cap
# - baseline_in_band: chance=1/N_img=~0.017 (floor); scramble control is the AG-style fire gate
# - deterministic seeding: fixed int seeds only; no hash()-seeded RNG, no list(set()) ordering
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - progress_logging = print_flush_true (cell is < 60s; flush anyway)
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

ANCHOR_NAME = "reader_image_word_grounding_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
STRUCT_JSON = os.path.join(REPO_ROOT, "data", "exp_textbook_extract_mcguffey_v1",
                           "mcguffey_first_structured.json")
FIG_DIR = os.path.join(REPO_ROOT, "data", "exp_textbook_extract_mcguffey_v1")

# ---- pre-registered bands (HYPOTHESIZED@preregs/2026-07-21_reader_image_word_grounding_v1.md) ----
GROUND_ACC1_MIN = 0.20   # word->image acc@1 for a rung to count as "grounding works" (>11x chance)
GROUND_ACC3_MIN = 0.35   # word->image acc@3 companion
SCR_DELTA_MIN = 0.10     # true acc@1 - scramble acc@1 required (proves real association, not base-rate)
CHANCE_EPS = 0.05        # within chance+eps => at chance
SEP_COS_TARGET = 0.20    # image-codebook mean off-diag cosine target for "separable" (recon rung-1 ~0.4)
LOAD_SWEEP = [8, 16, 32, 64]  # + "all" appended at run time
FLIP_FRACS = [0.15, 0.25, 0.35, 0.45]  # keyless image-discrimination corruption sweep (at full N)
STRESS_N = [125, 250, 500, 1000]  # dimensionality-stress: where separability (offdiag cosine) bites
STRESS_F = 0.40                    # corruption applied during the N-stress discrimination
STRESS_SEEDS = [0, 1, 2]
SEEDS = [0, 1, 2, 3, 4]

STOPWORDS = set(
    "the a an is on in of and to it he she they can do you we as at be by his her its him "
    "them this that these those i my me was are for with not no yes so up down out here there "
    "where what who when then than has have had will shall may said say says one two".split())
HEADER_PAT = re.compile(r"(ECLECTIC|READER|SERIES|LESSON|EDITION|McGuffey|MCGUFFEY|Colophon|"
                        r"Trademark|REVISED)", re.I)
OK_LEXNAMES = {"noun.animal", "noun.artifact", "noun.food", "noun.plant",
               "noun.body", "noun.object", "noun.shape", "noun.substance"}


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
# PAIRING: image <-> concrete referent words
# --------------------------------------------------------------------------------------
def _concrete_noun_filter():
    """Return fn(word)->bool using WordNet lexnames (glass-box specified concrete-object filter)."""
    from nltk.corpus import wordnet as wn
    cache = {}

    def is_concrete(w):
        if w in cache:
            return cache[w]
        ok = False
        for s in wn.synsets(w, pos="n"):
            if s.lexname() in OK_LEXNAMES:
                ok = True
                break
        cache[w] = ok
        return ok
    return is_concrete


def build_pairs(struct_json_path, max_images=None):
    """Parse structured JSON -> {img_path: sorted[concrete referent words]}. Deterministic."""
    is_concrete = _concrete_noun_filter()
    d = json.load(open(struct_json_path, encoding="utf-8"))
    figs = [f for p in d["pages"] for f in p.get("figures", [])
            if f.get("kind") == "illustration"]
    img_words = {}
    for f in figs:
        ws = set()
        for nt in f.get("nearby_text", []):
            if nt.get("rel") not in ("below", "above", "overlap"):
                continue
            for ln in nt.get("text", "").split("\n"):
                if HEADER_PAT.search(ln):
                    continue
                for w in re.findall(r"[A-Za-z]+", ln.lower()):
                    if len(w) >= 3 and w not in STOPWORDS and is_concrete(w):
                        ws.add(w)
        if ws:
            img_words[f["img_path"]] = sorted(ws)
    # deterministic ordering by img_path
    imgs = sorted(img_words)
    if max_images is not None:
        imgs = imgs[:max_images]
        img_words = {k: img_words[k] for k in imgs}
    # clean single-referent pairs: word appears in exactly one (retained) image
    w2i = defaultdict(list)
    for img in imgs:
        for w in img_words[img]:
            w2i[w].append(img)
    clean = sorted([w for w in w2i if len(w2i[w]) == 1])  # sorted -> deterministic
    clean_pairs = [(w, w2i[w][0]) for w in clean]
    return imgs, img_words, clean_pairs, dict(w2i)


# --------------------------------------------------------------------------------------
# IMAGE FEATURE FRONT-ENDS (glass-box, specified, deterministic)
# --------------------------------------------------------------------------------------
def load_gray(path):
    from PIL import Image
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32)


def _resize(gray, size):
    from PIL import Image
    im = Image.fromarray(np.clip(gray, 0, 255).astype(np.uint8))
    return np.asarray(im.resize((size, size), Image.BILINEAR), dtype=np.float32)


def feat_raw(gray, grid):
    """RUNG-1: raw grayscale resized to gridxgrid (float in [0,255])."""
    return _resize(gray, grid)


def feat_edge(gray, grid, edge_scale=6):
    """RUNG-2: Sobel gradient magnitude (fixed kernels) pooled to gridxgrid. Flat bg -> ~0."""
    from scipy import ndimage
    hi = _resize(gray, grid * edge_scale)
    gx = ndimage.sobel(hi, axis=1, mode="reflect")
    gy = ndimage.sobel(hi, axis=0, mode="reflect")
    mag = np.sqrt(gx * gx + gy * gy)
    # average-pool grid*S -> grid
    mag = mag.reshape(grid, edge_scale, grid, edge_scale).mean(axis=(1, 3))
    return mag.astype(np.float32)


def _otsu_threshold(vals):
    """Global Otsu threshold over a 1D array of intensities (fixed histogram rule)."""
    hist, edges = np.histogram(vals, bins=256, range=(0.0, 255.0))
    hist = hist.astype(np.float64)
    total = hist.sum()
    if total <= 0:
        return 127.5
    w = np.cumsum(hist)
    centers = (edges[:-1] + edges[1:]) / 2.0
    csum = np.cumsum(hist * centers)
    mu_t = csum[-1]
    best_t, best_var = 127.5, -1.0
    for i in range(1, 256):
        wb = w[i - 1]
        wf = total - wb
        if wb <= 0 or wf <= 0:
            continue
        mb = csum[i - 1] / wb
        mf = (mu_t - csum[i - 1]) / wf
        var_between = wb * wf * (mb - mf) ** 2
        if var_between > best_var:
            best_var = var_between
            best_t = centers[i - 1]
    return best_t


def feat_ink(gray_stack_thresh, gray, grid, edge_scale=6):
    """RUNG-2b: binary ink mask (inverted grayscale above global-Otsu ink threshold), pooled.

    gray_stack_thresh: global Otsu threshold on inverted intensities (fixed across dataset).
    """
    hi = _resize(gray, grid * edge_scale)
    ink = (255.0 - hi)  # dark pixels -> high ink
    mask = (ink >= gray_stack_thresh).astype(np.float32)
    frac = mask.reshape(grid, edge_scale, grid, edge_scale).mean(axis=(1, 3))
    return frac.astype(np.float32)


def quantize_global(feat_maps, Q):
    """Global dataset min-max -> integer levels [0,Q-1]. Specified affine map (glass-box)."""
    stack = np.stack(feat_maps, axis=0)
    lo, hi = float(stack.min()), float(stack.max())
    if hi <= lo:
        hi = lo + 1.0
    levels = np.round((stack - lo) / (hi - lo) * (Q - 1)).astype(np.int64)
    return np.clip(levels, 0, Q - 1)  # (n_img, grid, grid)


# --------------------------------------------------------------------------------------
# HD record encoder (Kanerva record-based position-value + thermometer levels; reused recipe)
# --------------------------------------------------------------------------------------
def build_position_vectors(n_pos, N, rng):
    return (rng.integers(0, 2, size=(n_pos, N)).astype(np.int8) * 2 - 1).astype(np.int8)


def build_level_codebook(Q, N, rng):
    L = np.empty((Q, N), dtype=np.int8)
    base = (rng.integers(0, 2, size=N).astype(np.int8) * 2 - 1).astype(np.int8)
    L[0] = base
    order = rng.permutation(N)
    per = N // (Q - 1)
    cur = base.copy()
    for q in range(1, Q):
        flip_idx = order[(q - 1) * per: q * per]
        cur = cur.copy()
        cur[flip_idx] = (-cur[flip_idx]).astype(np.int8)
        L[q] = cur
    return L


def _bundle_sign(acc):
    return np.where(acc >= 0, np.int8(1), np.int8(-1)).astype(np.int8)


def encode_record(intensities_flat, P, L):
    """image_hv = majority_sign( sum_i P_i * L_intensity(i) ). bsc_bind + bsc_bundle."""
    Lv = L[intensities_flat]
    bound = P.astype(np.int32) * Lv.astype(np.int32)
    return _bundle_sign(bound.sum(axis=0))


def encode_codebook(level_grids, P, L):
    """(n_img, grid, grid) int levels -> (n_img, N) bipolar image codebook."""
    n = level_grids.shape[0]
    N = P.shape[1]
    out = np.empty((n, N), dtype=np.int8)
    for k in range(n):
        out[k] = encode_record(level_grids[k].reshape(-1), P, L)
    return out


def random_word_codebook(words, N, rng):
    """{word: index} + (n_word, N) random bipolar word hypervectors."""
    w2idx = {w: i for i, w in enumerate(words)}
    W = (rng.integers(0, 2, size=(len(words), N)).astype(np.int8) * 2 - 1).astype(np.int8)
    return w2idx, W


# --------------------------------------------------------------------------------------
# grounding store + retrieval
# --------------------------------------------------------------------------------------
def build_store(pairs_idx, W, img_codes):
    """M = sum_p bind(word_p, image_p) (unsigned additive superposition). pairs_idx: list[(wi, ii)]."""
    N = W.shape[1]
    M = np.zeros(N, dtype=np.float32)
    for wi, ii in pairs_idx:
        M += W[wi].astype(np.float32) * img_codes[ii].astype(np.float32)
    return M


def _cosine_topk(q, codebook, k):
    """indices of top-k codebook rows by cosine with q. q:(N,), codebook:(n,N)."""
    qn = q / (np.linalg.norm(q) + 1e-12)
    C = codebook.astype(np.float32)
    C = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    sims = C @ qn
    k = min(k, sims.shape[0])
    top = np.argpartition(-sims, k - 1)[:k]
    return top[np.argsort(-sims[top])]


def retrieve_acc(pairs_idx, M, W, img_codes, direction, kset=(1, 3)):
    """direction 'w2i': query word -> image codebook; 'i2w': query image -> word codebook."""
    hits = {k: 0 for k in kset}
    n = len(pairs_idx)
    for wi, ii in pairs_idx:
        if direction == "w2i":
            q = M * W[wi].astype(np.float32)
            top = _cosine_topk(q, img_codes.astype(np.float32), max(kset))
            gold = ii
        else:
            q = M * img_codes[ii].astype(np.float32)
            top = _cosine_topk(q, W.astype(np.float32), max(kset))
            gold = wi
        for k in kset:
            if gold in top[:k]:
                hits[k] += 1
    return {("acc%d" % k): hits[k] / max(n, 1) for k in kset}


def offdiag_cosine(codes):
    """mean off-diagonal cosine of a bipolar codebook (separability diagnostic; lower=better)."""
    C = codes.astype(np.float32)
    C = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    S = C @ C.T
    n = S.shape[0]
    off = S[~np.eye(n, dtype=bool)]
    return float(off.mean())


def image_discrim_under_noise(codes, flip_fracs, rng):
    """KEYLESS 'can illustrations be told apart' discriminator: corrupt each image HD by flipping
    f fraction of bits, retrieve top-1 among the full codebook. Confusable (high inter-image cosine)
    images break first -> this is where encoder separability (unlike keyed retrieval) actually bites.
    Returns {f: top1_acc}. chance = 1/n_img. Vectorized flip mask (no per-image Python loop).
    """
    n, N = codes.shape
    Cn = codes.astype(np.float32)
    Cn = Cn / (np.linalg.norm(Cn, axis=1, keepdims=True) + 1e-12)
    out = {}
    for f in flip_fracs:
        nflip = int(round(f * N))
        r = rng.random((n, N))
        # per-row: flip the nflip smallest-random positions (exactly nflip via kth-order threshold)
        if nflip <= 0:
            mask = np.zeros((n, N), dtype=bool)
        elif nflip >= N:
            mask = np.ones((n, N), dtype=bool)
        else:
            kth = np.partition(r, nflip - 1, axis=1)[:, nflip - 1][:, None]
            mask = r <= kth
        probes = codes.astype(np.float32).copy()
        probes[mask] *= -1.0
        Pn = probes / (np.linalg.norm(probes, axis=1, keepdims=True) + 1e-12)
        S = Pn @ Cn.T
        top1 = S.argmax(axis=1)
        out[f] = float((top1 == np.arange(n)).mean())
    return out


# --------------------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------------------
def self_test():
    from hdlab.binding import bsc_bind, bsc_bundle
    import torch
    rng = np.random.default_rng(0)
    N, Q = 512, 9

    # 1. bind/unbind involution (bsc self-inverse): bind(bind(a,b),a) == b
    a = (rng.integers(0, 2, size=N).astype(np.int8) * 2 - 1)
    b = (rng.integers(0, 2, size=N).astype(np.int8) * 2 - 1)
    ab = (a.astype(np.int32) * b.astype(np.int32))
    back = (ab * a.astype(np.int32))
    assert np.array_equal(back.astype(np.int8), b.astype(np.int8)), "bind/unbind not involutive"

    # 2. encode_record bit-identical to hdlab bsc_bind/bsc_bundle
    n_pos = 16
    P = build_position_vectors(n_pos, N, rng)
    L = build_level_codebook(Q, N, rng)
    inten = rng.integers(0, Q, size=n_pos)
    vec = encode_record(inten, P, L)
    stack = [bsc_bind(torch.from_numpy(P[i].astype(np.float32)),
                      torch.from_numpy(L[inten[i]].astype(np.float32))) for i in range(n_pos)]
    prim = bsc_bundle(torch.stack(stack)).numpy().astype(np.int8)
    assert np.array_equal(vec, prim), "encode_record != hdlab bsc primitives"

    # 3. rung-2 edge front-end is SPECIFIED (not learned) and SUPPRESSES flat background.
    #    flat image -> Sobel magnitude ~0 everywhere; a bright square -> energy on its BORDER.
    grid = 8
    flat = np.full((64, 64), 200.0, dtype=np.float32)
    e_flat = feat_edge(flat, grid, edge_scale=4)
    assert float(e_flat.max()) < 1e-3, "edge front-end did not suppress flat background (%.4f)" % e_flat.max()
    sq = np.full((64, 64), 30.0, dtype=np.float32)
    sq[20:44, 20:44] = 230.0
    e_sq = feat_edge(sq, grid, edge_scale=4)
    r_sq = feat_raw(sq, grid)
    # edge energy concentrates on border ring; raw energy concentrates on filled interior
    center = e_sq[3:5, 3:5].mean()
    border = np.concatenate([e_sq[2, 2:6], e_sq[5, 2:6]]).mean()
    assert border > center + 1e-6, "edge map not contour-concentrated (border %.3f center %.3f)" % (border, center)
    assert r_sq[4, 4] > r_sq[0, 0], "raw map should be bright in the filled square interior"
    # determinism: two calls identical
    assert np.array_equal(feat_edge(sq, grid, edge_scale=4), e_sq), "edge front-end not deterministic"

    # 4. round-trip grounding works on a SEPARABLE synthetic set + SCRAMBLE fires.
    #    3 distinct patterns -> distinct codes -> store binds distinct words -> retrieval recovers.
    pats = [np.zeros((grid, grid)), np.zeros((grid, grid)), np.zeros((grid, grid))]
    pats[0][:grid // 2, :] = 8
    pats[1][:, :grid // 2] = 8
    pats[2][grid // 4:3 * grid // 4, grid // 4:3 * grid // 4] = 8
    lv = np.stack(pats).astype(np.int64)
    P2 = build_position_vectors(grid * grid, N, np.random.default_rng(1))
    L2 = build_level_codebook(Q, N, np.random.default_rng(2))
    codes = encode_codebook(lv, P2, L2)
    words = ["alpha", "beta", "gamma"]
    w2idx, W = random_word_codebook(words, N, np.random.default_rng(3))
    pairs = [(0, 0), (1, 1), (2, 2)]
    M = build_store(pairs, W, codes)
    acc = retrieve_acc(pairs, M, W, codes, "w2i")["acc1"]
    assert acc >= 0.99, "separable-synthetic grounding round-trip failed (acc %.3f)" % acc
    # scramble the pairing -> must collapse (gold no longer bound to its word)
    scr_pairs = [(0, 1), (1, 2), (2, 0)]
    Ms = build_store(scr_pairs, W, codes)
    acc_s = retrieve_acc(pairs, Ms, W, codes, "w2i")["acc1"]  # score against TRUE gold
    assert acc_s <= acc - 0.3, "scramble control did not fire (true %.3f scramble %.3f)" % (acc, acc_s)

    # 4b. keyless image-discrimination fires: clean probe retrieves self; heavy corruption degrades.
    nd = image_discrim_under_noise(codes, [0.05, 0.45], np.random.default_rng(7))
    assert nd[0.05] >= nd[0.45], "noise-discrim should not improve with more corruption"

    # 5. arms differ (raw vs edge front-ends produce different level grids on the square)
    _arms_must_differ({"raw": feat_raw(sq, grid), "edge": feat_edge(sq, grid, edge_scale=4)})

    # 6. no-nondeterministic-seeding static scan
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            assert_no_nondeterministic_seeding(f.read())
    except ImportError:
        pass

    print("[self_test] PASS: involution, bit-identical-bsc, edge-suppresses-bg+contour-concentrated, "
          "round-trip(acc=%.3f), scramble-fires(%.3f), arms-differ" % (acc, acc_s), flush=True)
    return True


# --------------------------------------------------------------------------------------
# main run
# --------------------------------------------------------------------------------------
def run(mode="full"):
    t0 = time.perf_counter()
    if mode == "smoke":
        grid, Q, N, edge_scale = 12, 9, 2500, 4
        max_images, seeds = 24, [0, 1]
    else:
        grid, Q, N, edge_scale = 16, 17, 10000, 6
        max_images, seeds = None, SEEDS

    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, mode, expected_n_units=len(seeds))

    imgs, img_words, clean_pairs, w2i = build_pairs(STRUCT_JSON, max_images=max_images)
    n_img = len(imgs)
    img_idx = {img: i for i, img in enumerate(imgs)}
    # words = union of concrete referents (word codebook space)
    words = sorted({w for ws in img_words.values() for w in ws})
    n_word = len(words)
    chance_w2i = 1.0 / n_img
    chance_i2w = 1.0 / n_word
    print("[pairs] n_img=%d n_word=%d n_clean_pairs=%d chance_w2i=%.4f"
          % (n_img, n_word, len(clean_pairs), chance_w2i), flush=True)

    # ---- image feature maps (deterministic; seed-independent) ----
    grays = [load_gray(os.path.join(FIG_DIR, img)) for img in imgs]
    raw_maps = [feat_raw(g, grid) for g in grays]
    edge_maps = [feat_edge(g, grid, edge_scale=edge_scale) for g in grays]
    # global Otsu ink threshold over inverted intensities of all resized images
    inv_all = np.concatenate([(255.0 - _resize(g, grid * edge_scale)).reshape(-1) for g in grays])
    ink_thr = _otsu_threshold(inv_all)
    ink_maps = [feat_ink(ink_thr, g, grid, edge_scale=edge_scale) for g in grays]

    rung_levels = {
        "rung1_raw": quantize_global(raw_maps, Q),
        "rung2_edge": quantize_global(edge_maps, Q),
        "rung2b_ink": quantize_global(ink_maps, Q),
    }

    # clean pairs as (word_idx, img_idx)
    clean_idx_all = [(words.index(w), img_idx[img]) for (w, img) in clean_pairs]
    load_sweep = list(LOAD_SWEEP) + [len(clean_idx_all)]  # + "all"

    per_rung = {}
    example_codes = {}
    for rung, levels in rung_levels.items():
        seed_true1, seed_true3, seed_i2w1, seed_scr1, seed_sep = [], [], [], [], []
        load_acc = {p: [] for p in load_sweep}
        noise_acc = {f: [] for f in FLIP_FRACS}
        for s in seeds:
            base_rng = np.random.default_rng(1000 + s)
            P = build_position_vectors(grid * grid, N, base_rng)
            L = build_level_codebook(Q, N, base_rng)
            codes = encode_codebook(levels, P, L)
            _, W = random_word_codebook(words, N, np.random.default_rng(2000 + s))
            if rung not in example_codes:
                example_codes[rung] = codes  # for arms-differ across rungs (seed 0)

            M = build_store(clean_idx_all, W, codes)
            a_w2i = retrieve_acc(clean_idx_all, M, W, codes, "w2i", kset=(1, 3))
            a_i2w = retrieve_acc(clean_idx_all, M, W, codes, "i2w", kset=(1, 3))
            seed_true1.append(a_w2i["acc1"]); seed_true3.append(a_w2i["acc3"])
            seed_i2w1.append(a_i2w["acc1"])
            seed_sep.append(offdiag_cosine(codes))

            # scramble must-fail: permute image assignment (fixed deterministic roll per seed)
            ii_list = [ii for (_, ii) in clean_idx_all]
            roll = (s + 1) % len(ii_list) if len(ii_list) > 1 else 0
            ii_scr = ii_list[roll:] + ii_list[:roll]
            scr_pairs = [(wi, ii_scr[j]) for j, (wi, _) in enumerate(clean_idx_all)]
            Ms = build_store(scr_pairs, W, codes)
            seed_scr1.append(retrieve_acc(clean_idx_all, Ms, W, codes, "w2i", kset=(1,))["acc1"])

            # load sweep: bundle first P clean pairs, retrieve those P (deterministic prefix)
            for p in load_sweep:
                sub = clean_idx_all[:p]
                Mp = build_store(sub, W, codes)
                load_acc[p].append(retrieve_acc(sub, Mp, W, codes, "w2i", kset=(1,))["acc1"])

            # KEYLESS image-discrimination under corruption (where separability actually bites)
            nd = image_discrim_under_noise(codes, FLIP_FRACS, np.random.default_rng(3000 + s))
            for f in FLIP_FRACS:
                noise_acc[f].append(nd[f])

        noise_mean = {f: float(np.mean(noise_acc[f])) for f in FLIP_FRACS}
        per_rung[rung] = {
            "w2i_acc1_mean": float(np.mean(seed_true1)), "w2i_acc1_std": float(np.std(seed_true1)),
            "w2i_acc3_mean": float(np.mean(seed_true3)),
            "i2w_acc1_mean": float(np.mean(seed_i2w1)),
            "scramble_acc1_mean": float(np.mean(seed_scr1)),
            "scramble_delta": float(np.mean(seed_true1) - np.mean(seed_scr1)),
            "img_offdiag_cosine_mean": float(np.mean(seed_sep)),
            "load_sweep_acc1": {str(p): float(np.mean(load_acc[p])) for p in load_sweep},
            "noise_discrim_acc1": {str(f): noise_mean[f] for f in FLIP_FRACS},
            "noise_discrim_auc": float(np.mean([noise_mean[f] for f in FLIP_FRACS])),
            "n_seeds": len(seeds),
        }

    # ---- N-STRESS discrimination sweep: where separability actually bites (the fire gate) ----
    # At full N=10000 both keyed retrieval and keyless noise-discrim saturate for all rungs
    # (offdiag cosine <= ~0.5 is still ~50-sigma separable). Shrinking N raises confusion so the
    # rung with the LOWEST off-diagonal cosine sustains the lowest N -> ranks true separability.
    stress = {r: {} for r in rung_levels}
    for rung, levels in rung_levels.items():
        for Ns in STRESS_N:
            accs = []
            for s in STRESS_SEEDS:
                brng = np.random.default_rng(4000 + s)
                Ps = build_position_vectors(grid * grid, Ns, brng)
                Ls = build_level_codebook(Q, Ns, brng)
                cds = encode_codebook(levels, Ps, Ls)
                nd = image_discrim_under_noise(cds, [STRESS_F], np.random.default_rng(5000 + s))
                accs.append(nd[STRESS_F])
            stress[rung][str(Ns)] = float(np.mean(accs))
        per_rung[rung]["noise_stress_by_N_f%02d" % int(STRESS_F * 100)] = stress[rung]

    # arms-differ across rung image codebooks (seed 0)
    arm_digests = _arms_must_differ({r: example_codes[r] for r in example_codes})

    # ---- verdict logic ----
    def rung_works(r):
        m = per_rung[r]
        return (m["w2i_acc1_mean"] >= GROUND_ACC1_MIN and
                m["scramble_delta"] >= SCR_DELTA_MIN)
    works = [r for r in per_rung if rung_works(r)]
    all_at_chance = all(per_rung[r]["w2i_acc1_mean"] <= chance_w2i + CHANCE_EPS for r in per_rung)
    best_rung = max(per_rung, key=lambda r: per_rung[r]["w2i_acc1_mean"])
    rung2_minus_rung1 = per_rung["rung2_edge"]["w2i_acc1_mean"] - per_rung["rung1_raw"]["w2i_acc1_mean"]

    # keyless discrimination ("told apart") at full N: rank rungs by noise-robust image AUC
    best_discrim_rung = max(per_rung, key=lambda r: per_rung[r]["noise_discrim_auc"])
    edge_minus_raw_discrim = (per_rung["rung2_edge"]["noise_discrim_auc"]
                              - per_rung["rung1_raw"]["noise_discrim_auc"])
    ink_minus_raw_discrim = (per_rung["rung2b_ink"]["noise_discrim_auc"]
                             - per_rung["rung1_raw"]["noise_discrim_auc"])

    # N-STRESS: mean discrimination across STRESS_N (the fire gate + true-separability ranking)
    skey = "noise_stress_by_N_f%02d" % int(STRESS_F * 100)
    stress_auc = {r: float(np.mean(list(per_rung[r][skey].values()))) for r in per_rung}
    best_stress_rung = max(stress_auc, key=lambda r: stress_auc[r])
    lowN = str(min(STRESS_N))
    stress_lowN = {r: per_rung[r][skey][lowN] for r in per_rung}
    discriminator_fired = (max(stress_lowN.values()) - min(stress_lowN.values())) >= 0.05

    # verdict: keyed grounding round-trip (does the store recall?) is the headline gate;
    # keyless discrimination is reported separately (which encoder tells woodcuts apart best).
    if works:
        verdict = "PASS_GROUNDING"
    elif all_at_chance:
        verdict = "HONEST_NEGATIVE_AT_CHANCE"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        "grounding(keyed w2i): n_clean=%d chance=%.4f | rung1_raw=%.3f rung2_edge=%.3f "
        "rung2b_ink=%.3f (scr d=%.3f) [works=%s -> %s] || "
        "SEPARABILITY offcos raw=%.3f edge=%.3f ink=%.3f || "
        "N-STRESS(f=%.2f) acc@N=%s: raw=%.3f edge=%.3f ink=%.3f | fired=%s best_sep=%s"
        % (len(clean_idx_all), chance_w2i,
           per_rung["rung1_raw"]["w2i_acc1_mean"], per_rung["rung2_edge"]["w2i_acc1_mean"],
           per_rung["rung2b_ink"]["w2i_acc1_mean"], per_rung["rung1_raw"]["scramble_delta"],
           works, verdict,
           per_rung["rung1_raw"]["img_offdiag_cosine_mean"],
           per_rung["rung2_edge"]["img_offdiag_cosine_mean"],
           per_rung["rung2b_ink"]["img_offdiag_cosine_mean"],
           STRESS_F, lowN,
           stress_lowN["rung1_raw"], stress_lowN["rung2_edge"], stress_lowN["rung2b_ink"],
           discriminator_fired, best_stress_rung))

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "reader image<->word grounding (McGuffey First): %s" % verdict,
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "run_mode": mode,
        "config": {"grid": grid, "Q": Q, "N": N, "edge_scale": edge_scale,
                   "n_img": n_img, "n_word": n_word, "n_clean_pairs": len(clean_idx_all),
                   "seeds": seeds, "ink_otsu_threshold": float(ink_thr)},
        "chance": {"w2i": chance_w2i, "i2w": chance_i2w},
        "rungs": per_rung,
        "verdict_detail": {"rungs_that_work": works, "best_rung_keyed": best_rung,
                           "rung2_edge_minus_rung1_raw_w2i_acc1": rung2_minus_rung1,
                           "all_rungs_at_chance": bool(all_at_chance),
                           "best_rung_keyless_discrim_fullN": best_discrim_rung,
                           "edge_minus_raw_noise_auc_fullN": edge_minus_raw_discrim,
                           "ink_minus_raw_noise_auc_fullN": ink_minus_raw_discrim,
                           "stress_auc_by_rung": stress_auc,
                           "stress_lowN_acc_by_rung": stress_lowN,
                           "best_rung_under_N_stress": best_stress_rung,
                           "discriminator_fired_under_stress": bool(discriminator_fired),
                           "note": "keyed word->image grounding saturates at full N (encoder-"
                                   "insensitive: orthogonal word-keys isolate). Full-N keyless noise-"
                                   "discrim also saturates (offdiag cosine <=~0.5 is ~50-sigma at "
                                   "N=10000). The N-stress sweep is the fire gate: shrinking N ranks "
                                   "true separability (lower offdiag cosine sustains lower N)."},
        "bands": {"GROUND_ACC1_MIN": GROUND_ACC1_MIN, "GROUND_ACC3_MIN": GROUND_ACC3_MIN,
                  "SCR_DELTA_MIN": SCR_DELTA_MIN, "CHANCE_EPS": CHANCE_EPS,
                  "SEP_COS_TARGET": SEP_COS_TARGET},
        "sample_clean_pairs": [(w, img.split("/")[-1]) for (w, img) in clean_pairs[:20]],
        "arms_differ_verified": True, "arm_digests": arm_digests,
        "final_metrics_atomicity": "tmp_replace",
        "primitives_reused": ["hdlab.binding.bsc_bind (elementwise mul, in-cell vectorized)",
                              "hdlab.binding.bsc_bundle (majority sign, in-cell)",
                              "additive superposition memory (sum of binds; composed in-cell)"],
        "recipe_adopted": "Kanerva record encoder + Rahimi/Kleyko thermometer levels + "
                          "Sobel edge / Otsu ink front-ends (all specified, glass-box)",
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
