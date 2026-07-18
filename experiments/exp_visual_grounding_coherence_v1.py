#!/usr/bin/env python
# -*- coding: ascii -*-
"""
exp_visual_grounding_coherence_v1

QUESTION (drill-sharpened; NOT the solved "encode an image" question):
Does a concrete word's PERCEPTUAL grounding (image-derived substrate vector)
COHERE WITH and ADD SIGNAL to its RELATIONAL (dictionary/WordNet) grounding,
or does it merely re-encode it? A pass must BEAT a dictionary-only control;
otherwise vision adds nothing yet -> DEFER vision (a valid, USER-endorsed win
for the control).

GLASS-BOX INVARIANT (load-bearing, stated explicitly):
  INGEST (scaffolding, external tools allowed, like WordNet/LLM per the pivot):
    - CLIP (transformers, openai/clip-vit-base-patch32) is the SENSORY TRANSDUCER.
      It is called ONCE, at ingest, to turn pixels -> a feature vector.
    - WordNet (nltk) supplies the independent RELATIONAL grounding (Wu-Palmer).
    - QuickDraw (CC-BY 4.0) supplies the images.
  RUNTIME (glass-box; numpy/substrate primitives; NO torch/transformers):
    - All recovery/cleanup/coherence/scene-factoring runs on the resulting FHRR
      phasor vectors with elementwise-complex bind/unbind + cosine-argmax cleanup.
    - CLIP is NEVER touched at runtime; every image (incl. held-out queries) is
      transduced to a substrate vector at ingest, then reasoned over in glass.

THREE TESTS
  T1  PICTURE -> WORD recovery (cross-modal): a held-out image, transduced to a
      substrate phasor, recovers the correct WORD atom (CLIP-text anchor) via
      glass-box cosine-argmax cleanup. Above chance AND above a shuffled control.
      This is a channel a dictionary-only grounding STRUCTURALLY LACKS (no pixels).
  T2a COHERENCE (the novel measurement): Spearman rho between the PERCEPTUAL
      pairwise-similarity matrix (FHRR anchors) and the RELATIONAL one (WordNet
      Wu-Palmer). Do the two INDEPENDENT groundings agree? vs a shuffled-label null.
  T2b ADD-DELTA (load-bearing dictionary-only comparison): 2-way forced choice
      within CONFUSABLE pairs (cat/dog, sun/moon, ...). Perceptual can discriminate
      visually-distinct-but-semantically-adjacent concepts; a dictionary-only
      grounding rates them near-identical (Wu-Palmer high) and CANNOT break the tie
      from a picture -> 0.5. Delta = perceptual_2way - 0.5 = signal vision ADDS.
  T3  SCENE-REP (exercises substrate primitives): scene = bind(loc1,obj1) +
      bind(loc2,obj2) over GROUNDED perceptual object vectors; unbind + cleanup
      recovers each. Demonstrates the substrate-native scene layer.

ARMS / BASELINES (design-gate; embody USER stance vision-is-optional):
  (a) CHANCE = 1/K.
  (b) SHUFFLED-grounding control -> MUST collapse to chance (guards leakage/saturation).
  (c) DICTIONARY-ONLY = the no-vision control the perceptual arm MUST BEAT
      (T1 it structurally cannot do -> chance; T2b confusable tie -> 0.5).
  CAN-FAIL: weak sketch-CLIP signal -> T1 ~ chance / T2b ~ 0.5 -> HARD_FAIL -> DEFER.
  ONE VARIABLE: the CLIP-scaffold perceptual arm. HDC-native front-end = HELD for a
  SECOND cell (Frontier-2, optimize-then-nativize). Not built here.

CREDIT (learn-from + build-on): Frady/Kent/Olshausen/Sommer 2020 (Resonator Networks);
Renner et al. 2024 (neuromorphic resonator scene understanding); Hersche et al. 2023
(NVSA, DNN-emb -> FHRR); Radford et al. 2021 (CLIP); Kanerva/Gayler/Plate (VSA
scene-as-binding); scope note notes/scope_visual_grounding_early_reader_words_substrate_native_2026-07-18.md.

BRAIN-CHECK (pre-registered): concrete-noun visual grounding is exactly how children
fast-map early vocab (picture<->word). A T1/T2 failure is presumed an encoder/impl bug
OR a sketch-modality limit (photo upgrade is the follow-up), NOT a structural bound --
localize which before accepting the negative.

RUN MODES
  --self-test : offline, fast (<10s); exercises REAL FHRR/cleanup/scene/Spearman code
                paths + partial-npy parser. No network, no CLIP.
  --smoke     : 6 words, small exemplar counts, FULL-N (discriminator survives scale).
  (default)   : full 21 words. Foreground-to-completion, local, CPU, ~1-2 hr, $0.

NO queue_add / NO push / NO remote-persist. Director-authorized foreground-local cell.
"""

import os
import sys
import ast
import json
import time
import argparse
import hashlib
import traceback
import urllib.request
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHOR_NAME = "visual_grounding_coherence_v1"

# --- word set + WordNet sense mapping (concrete QuickDraw sense; validated 2026-07-18) ---
# NOTE: "ball" removed -- not a live QuickDraw category (only compound forms basketball/
# baseball/soccer_ball exist); verified against categories.txt 2026-07-18. Staging MANIFEST
# listed it optimistically. All other 20 words are validated-present.
WORDS_FULL = ["cat", "dog", "hat", "fan", "sun", "duck", "bird", "fish",
              "tree", "star", "moon", "apple", "hand", "book", "key", "cup",
              "house", "car", "horse", "pig"]
WORDS_SMOKE = ["cat", "dog", "sun", "moon", "duck", "bird"]

# QuickDraw-concrete synset per word (all .n.01 except pig -> hog.n.03 animal sense)
SYNSET = {
    "cat": "cat.n.01", "dog": "dog.n.01", "hat": "hat.n.01", "fan": "fan.n.01",
    "ball": "ball.n.01", "sun": "sun.n.01", "duck": "duck.n.01", "bird": "bird.n.01",
    "fish": "fish.n.01", "tree": "tree.n.01", "star": "star.n.01", "moon": "moon.n.01",
    "apple": "apple.n.01", "hand": "hand.n.01", "book": "book.n.01", "key": "key.n.01",
    "cup": "cup.n.01", "house": "house.n.01", "car": "car.n.01", "horse": "horse.n.01",
    "pig": "hog.n.03",
}

# Confusable pairs = HIGH-WordNet-similarity (semantically near, dictionary-only cannot break
# the tie -> pinned 0.5) but VISUALLY discriminable (perceptual arm can separate). This is what
# makes T2b the load-bearing "vision adds what the dictionary lacks" test.
CONFUSABLE_FULL = [("cat", "dog"), ("cat", "horse"), ("duck", "bird"),
                   ("sun", "moon"), ("sun", "star"), ("horse", "pig")]
CONFUSABLE_SMOKE = [("cat", "dog"), ("sun", "moon"), ("duck", "bird")]

QD_URL = "https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/{cat}.npy"
CLIP_MODEL_ID = "openai/clip-vit-base-patch32"
TEXT_PROMPT = "a black and white drawing of a {w}"

MAX_EXEMPLARS = 250   # cached per word; smoke/full slice from this (deterministic order)
SEED = 20260718


# ============================ FHRR substrate primitives (glass-box) =====================
def phasor(theta):
    """Unit-magnitude complex phasor from real phase array. Shape-preserving."""
    return np.exp(1j * theta).astype(np.complex128)


def rand_phasor(rng, shape):
    """Random unit phasor(s), phases ~ U[-pi,pi]."""
    return phasor(rng.uniform(-np.pi, np.pi, size=shape))


def fhrr_cos(a, b):
    """Real cosine between unit-phasor vectors. a:(...,N) b:(...,N) or (K,N)."""
    n = a.shape[-1]
    return np.real(np.tensordot(a, np.conj(b), axes=([-1], [-1]))) / n


def bind(a, b):
    """FHRR bind = elementwise phasor product."""
    return a * b


def unbind(a, b):
    """FHRR unbind = elementwise product with conjugate."""
    return a * np.conj(b)


def bundle(vecs):
    """FHRR bundle = sum then renormalize each component to unit phasor."""
    z = np.sum(vecs, axis=0)
    mag = np.abs(z)
    mag[mag < 1e-12] = 1e-12
    return z / mag


def project_to_fhrr(embs, R):
    """Real embeddings (m,512) -> FHRR phasors (m,N) via fixed random projection R (N,512)."""
    theta = embs @ R.T            # (m, N) real phases
    return phasor(theta)


def cleanup_argmax(query_vecs, codebook):
    """Nearest codebook index by FHRR cosine. query:(m,N) codebook:(K,N) -> (m,) idx."""
    sims = fhrr_cos(query_vecs, codebook)   # (m,K)
    return np.argmax(sims, axis=-1), sims


def spearman_rho(x, y):
    """Spearman rank correlation (no scipy dependency)."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    rx = _rankdata(x)
    ry = _rankdata(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    if denom < 1e-12:
        return 0.0
    return float((rx * ry).sum() / denom)


def _rankdata(a):
    """Average-rank of a 1-D array (ties averaged)."""
    a = np.asarray(a, dtype=np.float64)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=np.float64)
    ranks[order] = np.arange(1, len(a) + 1, dtype=np.float64)
    # average ties
    sa = a[order]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sa[j + 1] == sa[i]:
            j += 1
        if j > i:
            avg = (ranks[order[i]] + ranks[order[j]]) / 2.0
            for k in range(i, j + 1):
                ranks[order[k]] = avg
        i = j + 1
    return ranks


def _arms_must_differ(arms_outputs):
    """META_RULE_AF: assert no two arm outputs are bit-identical."""
    digests = {}
    for name, out in arms_outputs.items():
        arr = np.asarray(out)
        digests[name] = hashlib.sha256(arr.tobytes()).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b))
    return digests


# ============================ QuickDraw partial-npy reader ==============================
def _parse_npy_header(hdr_bytes):
    """Return (data_offset, shape, descr) from leading bytes of a .npy file."""
    assert hdr_bytes[:6] == b"\x93NUMPY", "not a .npy file"
    ver = (hdr_bytes[6], hdr_bytes[7])
    if ver[0] == 1:
        hlen = int.from_bytes(hdr_bytes[8:10], "little")
        pre = 10
    else:
        hlen = int.from_bytes(hdr_bytes[8:12], "little")
        pre = 12
    hdict = ast.literal_eval(hdr_bytes[pre:pre + hlen].decode("latin1"))
    return pre + hlen, hdict["shape"], hdict["descr"]


def fetch_quickdraw(word, n, cache_dir, timeout=60):
    """Download first n exemplars of a QuickDraw category via HTTP Range; cache locally.

    Returns uint8 array (n,28,28). Cache stores MAX_EXEMPLARS; slices to n.
    """
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "qd_%s.npy" % word)
    if os.path.exists(cache_path):
        arr = np.load(cache_path)
        if arr.shape[0] >= n:
            return arr[:n]
    url = QD_URL.format(cat=word.replace(" ", "%20"))
    req = urllib.request.Request(url, headers={"Range": "bytes=0-255"})
    hdr = urllib.request.urlopen(req, timeout=timeout).read()
    data_off, shape, descr = _parse_npy_header(hdr)
    assert descr == "|u1", "unexpected dtype %s" % descr
    row = int(np.prod(shape[1:]))          # 784
    want = min(MAX_EXEMPLARS, shape[0])
    end = data_off + want * row - 1
    req2 = urllib.request.Request(url, headers={"Range": "bytes=%d-%d" % (data_off, end)})
    raw = urllib.request.urlopen(req2, timeout=timeout).read()
    arr = np.frombuffer(raw, dtype=np.uint8)[:want * row].reshape(want, 28, 28).copy()
    np.save(cache_path, arr)
    return arr[:n]


# ============================ CLIP ingest (scaffolding only) ============================
def clip_encode_images(word, arr, cache_dir):
    """CLIP-transduce (n,28,28) uint8 sketches -> (n,512) L2-normalized embeddings.

    Cached per word. torch/transformers used HERE ONLY (ingest transducer).
    """
    cache_path = os.path.join(cache_dir, "clip_%s.npy" % word)
    if os.path.exists(cache_path):
        emb = np.load(cache_path)
        if emb.shape[0] >= arr.shape[0]:
            return emb[:arr.shape[0]]
    import torch
    from PIL import Image
    from transformers import CLIPModel, CLIPProcessor
    global _CLIP_MODEL, _CLIP_PROC
    if "_CLIP_MODEL" not in globals() or _CLIP_MODEL is None:
        _CLIP_MODEL = CLIPModel.from_pretrained(CLIP_MODEL_ID)
        _CLIP_PROC = CLIPProcessor.from_pretrained(CLIP_MODEL_ID)
        _CLIP_MODEL.eval()
    embs = []
    bs = 128
    with torch.no_grad():
        for s in range(0, arr.shape[0], bs):
            chunk = arr[s:s + bs]
            pil = [Image.fromarray(np.stack([im] * 3, axis=-1)).resize((224, 224))
                   for im in chunk]
            inp = _CLIP_PROC(images=pil, return_tensors="pt")
            out = _CLIP_MODEL.get_image_features(pixel_values=inp["pixel_values"])
            vec = out if hasattr(out, "shape") else out.pooler_output
            embs.append(vec.cpu().numpy().astype(np.float64))
    emb = np.concatenate(embs, axis=0)
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)
    np.save(cache_path, emb)
    return emb


def clip_encode_text(words):
    """CLIP-transduce word prompts -> (K,512) L2-normalized text embeddings (ingest)."""
    import torch
    from transformers import CLIPModel, CLIPProcessor
    global _CLIP_MODEL, _CLIP_PROC
    if "_CLIP_MODEL" not in globals() or _CLIP_MODEL is None:
        _CLIP_MODEL = CLIPModel.from_pretrained(CLIP_MODEL_ID)
        _CLIP_PROC = CLIPProcessor.from_pretrained(CLIP_MODEL_ID)
        _CLIP_MODEL.eval()
    prompts = [TEXT_PROMPT.format(w=w) for w in words]
    with torch.no_grad():
        inp = _CLIP_PROC(text=prompts, return_tensors="pt", padding=True)
        out = _CLIP_MODEL.get_text_features(input_ids=inp["input_ids"],
                                            attention_mask=inp["attention_mask"])
        vec = out if hasattr(out, "shape") else out.pooler_output
        emb = vec.cpu().numpy().astype(np.float64)
    return emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)


# ============================ relational grounding (WordNet) ============================
def wordnet_simmat(words):
    """Symmetric Wu-Palmer similarity matrix over the mapped synsets. (K,K) in [0,1]."""
    from nltk.corpus import wordnet as wn
    syns = [wn.synset(SYNSET[w]) for w in words]
    K = len(words)
    S = np.zeros((K, K), dtype=np.float64)
    for i in range(K):
        for j in range(K):
            v = syns[i].wup_similarity(syns[j])
            S[i, j] = float(v) if v is not None else 0.0
    return S


# ============================ metrics write (atomic) ====================================
def write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)      # META_RULE_AH atomic


def write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
    }
    write_metrics(output_dir, diag)


# ============================ the experiment ===========================================
def upper_offdiag(M):
    """Flatten strictly-upper-triangular entries of a square matrix."""
    K = M.shape[0]
    iu = np.triu_indices(K, k=1)
    return M[iu]


def run_experiment(mode):
    """mode in {'smoke','full'}. Returns metrics dict. Foreground-to-completion."""
    t0 = time.time()
    rng = np.random.default_rng(SEED)

    if mode == "smoke":
        words = WORDS_SMOKE
        confusable = CONFUSABLE_SMOKE
        n_train, n_test = 40, 15
        N = 4096                      # FULL-N in smoke (discriminator-survives-scale, option A)
        out_dir = os.path.join(REPO, "data", "exp_%s_smoke" % ANCHOR_NAME)
    else:
        words = WORDS_FULL
        confusable = CONFUSABLE_FULL
        n_train, n_test = 200, 50
        N = 4096
        out_dir = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)

    cache_dir = os.path.join(REPO, "data", "exp_%s_cache" % ANCHOR_NAME)
    K = len(words)
    widx = {w: i for i, w in enumerate(words)}
    chance = 1.0 / K

    # ---------------- INGEST (scaffolding) ----------------
    # images -> CLIP embeddings (512-d shared space). Robust to QuickDraw category drift:
    # a 404 (category absent) drops the word + logs it; the word set / confusable pairs /
    # widx / chance are rebuilt from survivors so downstream stays consistent.
    train_emb = {}   # word -> (n_train,512)
    test_emb = {}    # word -> (n_test,512)
    dropped_words = []
    import urllib.error
    for w in words:
        try:
            arr = fetch_quickdraw(w, n_train + n_test, cache_dir)
        except urllib.error.HTTPError as he:
            if he.code == 404:
                dropped_words.append(w)
                continue
            raise
        emb = clip_encode_images(w, arr, cache_dir)
        train_emb[w] = emb[:n_train]
        test_emb[w] = emb[n_train:n_train + n_test]
    if dropped_words:
        words = [w for w in words if w not in dropped_words]
        confusable = [(a, b) for (a, b) in confusable
                      if a not in dropped_words and b not in dropped_words]
        K = len(words)
        widx = {w: i for i, w in enumerate(words)}
        chance = 1.0 / K
        assert K >= 4, "too many QuickDraw categories dropped (%s); cannot run" % dropped_words

    text_emb = clip_encode_text(words)                    # (K,512) shared space

    # perceptual anchor (CLIP space) = mean of train exemplars, renormalized
    anc_emb = np.stack([train_emb[w].mean(axis=0) for w in words], axis=0)
    anc_emb = anc_emb / (np.linalg.norm(anc_emb, axis=1, keepdims=True) + 1e-12)

    # ---------------- modality-gap centering (Liang et al. 2022, "Mind the Gap") ----------
    # CLIP image and text embeddings occupy offset cones; cross-modal distances (image->text)
    # are ~7x within-image distances. A single RFF bandwidth cannot resolve both -> the large
    # cross-modal distances saturate to ~0 and image->text recovery collapses to noise (a
    # projection artifact; raw-CLIP image->text is ~0.73). Removing the per-modality mean puts
    # both modalities in one cone so a single gamma resolves both channels (verified: cross-modal
    # 0.13->0.77, within-modality preserved). Linear ingest-time op; glass-box invariant intact.
    img_mean = np.mean(np.concatenate([train_emb[w] for w in words], axis=0), axis=0)
    txt_mean = np.mean(text_emb, axis=0)

    def _center(x, m):
        y = x - m
        return y / (np.linalg.norm(y, axis=-1, keepdims=True) + 1e-12)

    anc_emb = _center(anc_emb, img_mean)
    text_emb = _center(text_emb, txt_mean)
    test_emb = {w: _center(test_emb[w], img_mean) for w in words}

    # ---------------- ingest -> FHRR (fixed random projection; adaptive bandwidth) -------
    # bandwidth gamma from median pairwise distance of anchors (principled, logged)
    d2 = []
    for i in range(K):
        for j in range(i + 1, K):
            d2.append(np.sum((anc_emb[i] - anc_emb[j]) ** 2))
    med_d2 = float(np.median(d2)) if d2 else 1.0
    gamma = 1.0 / np.sqrt(max(med_d2, 1e-6))              # RFF-style bandwidth
    R = (gamma * rng.standard_normal((N, 512))).astype(np.float64)

    p_anc = project_to_fhrr(anc_emb, R)                   # (K,N) perceptual anchors
    p_text = project_to_fhrr(text_emb, R)                 # (K,N) word (text) anchors
    q_test = {w: project_to_fhrr(test_emb[w], R) for w in words}  # held-out queries

    # RUNTIME from here: glass-box FHRR only. CLIP not touched again.

    # ---------------- T1 picture -> word (cross-modal, glass-box cleanup) ----------------
    # each held-out image query -> nearest TEXT anchor (word atom)
    t1_correct = 0
    t1_total = 0
    # SHUFFLED-label control: score each word's queries against a RANDOM (wrong) target label.
    # Queries still argmax against the TRUE anchors, but "correct" is a shuffled word -> this
    # destroys the image<->word correspondence and MUST collapse to chance (guards leakage).
    perm = rng.permutation(K)          # perm[i] = shuffled (wrong) label for word i
    shuf_correct = 0
    # T1a reference: query -> nearest PERCEPTUAL image-anchor (image->image)
    t1a_correct = 0
    for w in words:
        Q = q_test[w]                                      # (n_test,N)
        idx, _ = cleanup_argmax(Q, p_text)                 # cross-modal
        t1_correct += int(np.sum(idx == widx[w]))
        t1_total += Q.shape[0]
        idxa, _ = cleanup_argmax(Q, p_anc)                 # image->image ref
        t1a_correct += int(np.sum(idxa == widx[w]))
        shuf_target = int(perm[widx[w]])                   # random wrong label
        shuf_correct += int(np.sum(idx == shuf_target))
    t1_acc = t1_correct / t1_total
    t1a_acc = t1a_correct / t1_total
    t1_shuf = shuf_correct / t1_total

    # ---------------- T2a coherence (perceptual FHRR vs WordNet Wu-Palmer) ---------------
    S_perc = fhrr_cos(p_anc, p_anc)                        # (K,K) FHRR anchor sims
    S_rel = wordnet_simmat(words)                          # (K,K) Wu-Palmer
    # CLIP-space perceptual sim (reference; verifies FHRR projection preserved structure)
    S_perc_clip = anc_emb @ anc_emb.T
    v_perc = upper_offdiag(S_perc)
    v_rel = upper_offdiag(S_rel)
    v_perc_clip = upper_offdiag(S_perc_clip)
    rho = spearman_rho(v_perc, v_rel)
    rho_clip = spearman_rho(v_perc_clip, v_rel)
    proj_preserve = spearman_rho(v_perc, v_perc_clip)     # FHRR vs CLIP ranking preservation
    # shuffled-label null: permute rows/cols of S_perc, recompute rho
    n_null = 500
    null_rhos = []
    for _ in range(n_null):
        pp = rng.permutation(K)
        vp = upper_offdiag(S_perc[np.ix_(pp, pp)])
        null_rhos.append(spearman_rho(vp, v_rel))
    null_rhos = np.asarray(null_rhos)
    null_mean = float(null_rhos.mean())
    null_std = float(null_rhos.std())
    null_p95 = float(np.percentile(null_rhos, 95))
    rho_z = (rho - null_mean) / (null_std + 1e-12)
    rho_emp_p = float(np.mean(null_rhos >= rho))          # empirical p (one-sided)

    # ---------------- T2b ADD-delta (confusable 2-way; vision vs dictionary-only) --------
    pair_correct = 0
    pair_total = 0
    for (a, b) in confusable:
        ia, ib = widx[a], widx[b]
        for src, truth in ((a, ia), (b, ib)):
            Q = q_test[src]
            sim_a = fhrr_cos(Q, p_anc[ia])                 # (n_test,)
            sim_b = fhrr_cos(Q, p_anc[ib])
            pick = np.where(sim_a >= sim_b, ia, ib)
            pair_correct += int(np.sum(pick == truth))
            pair_total += Q.shape[0]
    t2b_perc = pair_correct / pair_total
    # dictionary-only on this task: no pixel access + WordNet rates the pair near-identical
    #   -> cannot break the tie from a picture -> 0.5 (analytically pinned). We also log the
    #   mean WordNet within-pair similarity to SHOW why dictionary-only cannot separate them.
    dict_only_2way = 0.5
    pair_wn_sims = [float(S_rel[widx[a], widx[b]]) for (a, b) in confusable]
    t2b_delta = t2b_perc - dict_only_2way

    # ---------------- T3 scene-rep (substrate-native, grounded object vectors) -----------
    n_scene = 400 if mode == "full" else 120
    scene_correct = 0
    scene_total = 0
    scene_shuf_correct = 0
    for _ in range(n_scene):
        a, b = rng.choice(K, size=2, replace=False)
        loc1 = rand_phasor(rng, N)
        loc2 = rand_phasor(rng, N)
        scene = bundle(np.stack([bind(loc1, p_anc[a]), bind(loc2, p_anc[b])], axis=0))
        r1 = unbind(scene, loc1)
        r2 = unbind(scene, loc2)
        i1 = int(np.argmax(fhrr_cos(r1[None, :], p_anc)[0]))
        i2 = int(np.argmax(fhrr_cos(r2[None, :], p_anc)[0]))
        scene_correct += int(i1 == a) + int(i2 == b)
        scene_total += 2
        # shuffled control: unbind with a WRONG (fresh) location -> chance
        wrong = rand_phasor(rng, N)
        rw = unbind(scene, wrong)
        iw = int(np.argmax(fhrr_cos(rw[None, :], p_anc)[0]))
        scene_shuf_correct += int(iw == a)
    t3_acc = scene_correct / scene_total
    t3_shuf = scene_shuf_correct / n_scene

    # ---------------- arms-must-differ (META_RULE_AF) ----------------
    arm_digests = _arms_must_differ({
        "perceptual_anchors": p_anc,
        "text_anchors": p_text,
        "wordnet_relmat": S_rel,
    })

    # ---------------- discriminator-fires / baseline-in-band gates ----------------
    # SHUFFLED must collapse (guards leakage): T1 shuffled ~ chance
    shuffled_collapsed = t1_shuf <= max(2.0 * chance, chance + 0.05)
    # baseline (chance) in measurable band: chance is not >=0.95 nor <=0.05 for K>=6 -> ok
    baseline_in_band = 0.05 < chance < 0.95 or K >= 6

    # ---------------- verdict (pre-registered bands) ----------------
    # T1: perceptual cross-modal recovery must beat chance and shuffled
    t1_pass = (t1_acc >= max(0.30, 3.0 * chance)) and (t1_acc > t1_shuf + 0.10) and shuffled_collapsed
    # T2a: coherence positive AND beyond shuffled null 95th pct
    t2a_pass = (rho >= 0.30) and (rho > null_p95) and (rho_emp_p < 0.05)
    # T2b: vision adds discriminative signal dictionary-only lacks
    t2b_pass = (t2b_perc >= 0.65)
    # T3: substrate primitive sanity (must hold; not the novel claim)
    t3_pass = (t3_acc >= 0.85) and (t3_shuf <= 2.0 * chance + 0.05)

    novel_pass = t1_pass and t2a_pass and t2b_pass
    if novel_pass and t3_pass:
        verdict = "HARD_PASS"
        vmsg = ("perceptual grounding recovers words (T1=%.3f>chance %.3f, shuf %.3f), "
                "coheres with WordNet (T2a rho=%.3f, null95=%.3f, p=%.3f), and ADDS "
                "confusable-discrimination dictionary-only lacks (T2b=%.3f, delta=%+.3f). "
                "Scene-rep T3=%.3f. Vision-grounding genuinely helps the foundation "
                "(CLAIM-VET-pending)." % (t1_acc, chance, t1_shuf, rho, null_p95,
                                          rho_emp_p, t2b_perc, t2b_delta, t3_acc))
    elif (not t1_pass) or (not t2a_pass) or (not t2b_pass):
        verdict = "HARD_FAIL"
        vmsg = ("perceptual grounding does NOT clear the bar: T1=%.3f (chance %.3f, shuf %.3f, "
                "pass=%s), T2a rho=%.3f (null95=%.3f, p=%.3f, pass=%s), T2b=%.3f delta=%+.3f "
                "(pass=%s). Vision-via-sketches adds nothing yet -> DEFER vision, advance "
                "text-first. Localize: sketch-modality vs approach (photo upgrade is the "
                "follow-up)." % (t1_acc, chance, t1_shuf, t1_pass, rho, null_p95, rho_emp_p,
                                 t2a_pass, t2b_perc, t2b_delta, t2b_pass))
    else:
        verdict = "MIDDLE_BAND"
        vmsg = ("mixed: T1=%.3f(pass=%s) T2a rho=%.3f(pass=%s) T2b=%.3f(pass=%s) "
                "T3=%.3f(pass=%s). Inconclusive; investigate before claim." % (
                    t1_acc, t1_pass, rho, t2a_pass, t2b_perc, t2b_pass, t3_acc, t3_pass))

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": "%s | T1=%.3f T2a_rho=%.3f T2b=%.3f T3=%.3f" % (
            verdict, t1_acc, rho, t2b_perc, t3_acc),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "mode": mode,
        "config": {
            "words": words, "K": K, "n_train": n_train, "n_test": n_test,
            "N_fhrr": N, "chance": chance, "seed": SEED, "gamma": float(gamma),
            "med_pairwise_d2": med_d2, "clip_model": CLIP_MODEL_ID,
            "text_prompt": TEXT_PROMPT, "confusable_pairs": confusable,
            "modality_gap_centering": True,
            "img_mean_norm": float(np.linalg.norm(img_mean)),
            "txt_mean_norm": float(np.linalg.norm(txt_mean)),
            "dropped_words_404": dropped_words,
        },
        "arms": {
            "T1_perceptual_crossmodal_top1": t1_acc,
            "T1_image_to_image_anchor_top1": t1a_acc,
            "T1_shuffled_control_top1": t1_shuf,
            "T1_chance": chance,
            "T2a_coherence_rho_fhrr": rho,
            "T2a_coherence_rho_clip_ref": rho_clip,
            "T2a_null_mean": null_mean,
            "T2a_null_std": null_std,
            "T2a_null_p95": null_p95,
            "T2a_rho_zscore": rho_z,
            "T2a_rho_empirical_p": rho_emp_p,
            "T2a_fhrr_projection_preservation_rho": proj_preserve,
            "T2b_perceptual_2way": t2b_perc,
            "T2b_dictionary_only_2way": dict_only_2way,
            "T2b_add_delta": t2b_delta,
            "T2b_confusable_wordnet_sims": pair_wn_sims,
            "T3_scene_recovery": t3_acc,
            "T3_shuffled_control": t3_shuf,
        },
        "gates": {
            "t1_pass": bool(t1_pass), "t2a_pass": bool(t2a_pass),
            "t2b_pass": bool(t2b_pass), "t3_pass": bool(t3_pass),
            "novel_pass": bool(novel_pass),
            "shuffled_collapsed": bool(shuffled_collapsed),
            "baseline_in_band": bool(baseline_in_band),
            "arms_differ_verified": True,
        },
        "arm_digests": arm_digests,
        "glass_box_note": ("CLIP+WordNet+QuickDraw at INGEST only; all T1/T2/T3 recovery "
                           "runs on FHRR phasors with numpy bind/unbind/cleanup (runtime "
                           "glass-box, no torch/transformers)."),
        "final_metrics_atomicity": "tmp_replace",
        "calibration_check": "adaptive_with_gate: gamma=1/sqrt(median_pairwise_d2) after "
                             "modality-gap centering (robust across gamma post-centering), logged; "
                             "shuffled+null controls verify discriminator fires",
    }
    write_metrics(out_dir, metrics)
    return metrics, out_dir


# ============================ self-test (offline, real code paths) ======================
def self_test():
    """Exercise REAL FHRR/cleanup/scene/Spearman/npy-parse paths at tiny scale. Offline."""
    t0 = time.time()
    rng = np.random.default_rng(1)
    N = 256

    # 1. bind/unbind recovers (cos ~ 1 for exact unbind, ~0 for wrong key)
    a = rand_phasor(rng, N)
    k = rand_phasor(rng, N)
    bound = bind(k, a)
    rec = unbind(bound, k)
    c_ok = fhrr_cos(rec[None, :], a[None, :])[0, 0]
    c_bad = fhrr_cos(unbind(bound, rand_phasor(rng, N))[None, :], a[None, :])[0, 0]
    assert c_ok > 0.99, "unbind recovery failed: %.4f" % c_ok
    assert abs(c_bad) < 0.3, "wrong-key not near-zero: %.4f" % c_bad

    # 2. cleanup argmax picks the true codebook entry
    cb = rand_phasor(rng, (5, N))
    noisy = bundle(np.stack([cb[2], 0.15 * rand_phasor(rng, N)], axis=0))
    idx, _ = cleanup_argmax(noisy[None, :], cb)
    assert idx[0] == 2, "cleanup argmax wrong: %d" % idx[0]

    # 3. scene bind+unbind 2-object recovery (the T3 primitive)
    o1, o2 = cb[1], cb[3]
    l1, l2 = rand_phasor(rng, N), rand_phasor(rng, N)
    scene = bundle(np.stack([bind(l1, o1), bind(l2, o2)], axis=0))
    r1 = unbind(scene, l1)
    assert int(np.argmax(fhrr_cos(r1[None, :], cb)[0])) == 1, "scene recover obj1 failed"

    # 4. Spearman: monotone -> 1.0, anti -> -1.0, ties handled
    assert abs(spearman_rho([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-9
    assert abs(spearman_rho([1, 2, 3, 4], [40, 30, 20, 10]) + 1.0) < 1e-9
    assert abs(spearman_rho([1, 1, 2, 2], [1, 1, 2, 2]) - 1.0) < 1e-9

    # 5. FHRR projection preserves similarity ranking (RFF property, real project fn).
    # Use STRUCTURED embeddings (two clusters) so there is a real similarity range to
    # preserve; random unit vectors in 512-d are all near-orthogonal (no structure).
    # Use the SAME adaptive-gamma formula + a larger N as the real cell (proj improves with N).
    Np = 1024
    c1 = rng.standard_normal(512); c1 /= np.linalg.norm(c1)
    c2 = rng.standard_normal(512); c2 /= np.linalg.norm(c2)
    embs = np.stack([c1 + 0.15 * rng.standard_normal(512) for _ in range(4)] +
                    [c2 + 0.15 * rng.standard_normal(512) for _ in range(4)], axis=0)
    embs = embs / np.linalg.norm(embs, axis=1, keepdims=True)
    d2 = [np.sum((embs[i] - embs[j]) ** 2) for i in range(8) for j in range(i + 1, 8)]
    gp = 1.0 / np.sqrt(max(float(np.median(d2)), 1e-6))
    Rp = (gp * rng.standard_normal((Np, 512)))
    P = project_to_fhrr(embs, Rp)
    Sf = upper_offdiag(fhrr_cos(P, P))
    Sc = upper_offdiag(embs @ embs.T)
    assert spearman_rho(Sf, Sc) > 0.6, ("projection did not preserve ranking: %.3f"
                                        % spearman_rho(Sf, Sc))

    # 6. partial-npy header parser on a synthetic in-memory .npy
    import io
    buf = io.BytesIO()
    np.save(buf, np.arange(3 * 784, dtype=np.uint8).reshape(3, 784))
    raw = buf.getvalue()
    off, shape, descr = _parse_npy_header(raw[:200])
    assert shape[1] == 784 and descr == "|u1", "npy parse failed: %s %s" % (shape, descr)
    dec = np.frombuffer(raw[off:off + 3 * 784], dtype=np.uint8).reshape(3, 784)
    assert dec[1, 0] == np.uint8(784 % 256), "npy data offset wrong"

    # 7. arms-differ raises on identical, passes on distinct
    _arms_must_differ({"x": cb[0], "y": cb[1]})
    try:
        _arms_must_differ({"x": cb[0], "y": cb[0].copy()})
        raise AssertionError("arms-differ did not fire on identical")
    except AssertionError as e:
        assert "META_RULE_AF" in str(e), "wrong assertion: %s" % e

    # 8. WordNet + synset map load (relational grounding source)
    from nltk.corpus import wordnet as wn
    for w in WORDS_SMOKE:
        assert wn.synset(SYNSET[w]) is not None, "synset missing for %s" % w
    wn.synset(SYNSET["cat"]).wup_similarity(wn.synset(SYNSET["dog"]))

    print("SELF-TEST PASS (%.2fs): fhrr bind/unbind/cleanup/scene, spearman, "
          "projection-preserve, npy-parse, arms-differ, wordnet map" % (time.time() - t0))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    mode = "smoke" if args.smoke else "full"
    out_dir = os.path.join(REPO, "data", "exp_%s%s" % (ANCHOR_NAME,
                                                       "_smoke" if args.smoke else ""))
    try:
        metrics, od = run_experiment(mode)
    except Exception as e:
        write_crash_metrics(out_dir, e)
        raise
    print("[%s] %s" % (mode.upper(), metrics["summary"]))
    print("  verdict_msg:", metrics["verdict_msg"])
    print("  metrics ->", os.path.join(od, "metrics.json"))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
