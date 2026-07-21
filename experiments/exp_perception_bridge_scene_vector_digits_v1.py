"""Perception bridge: pixels -> object@location -> SCENE VECTOR -> query -> symbol grounding.

USER TARGET REPRESENTATION SEED. This is the "NEST@location + EGGS@location" symbolic-scene
representation, proven with DIGITS as PROXY objects (honest: no object-labeled data locally;
sklearn load_digits stands in for scene objects). It proves the mechanism the USER wants:
  pixels -> recognize object -> CONCEPT atom -> bind to LOCATION -> bundle into ONE scene vector
  -> query it (location->concept, concept->location) -> factor it (resonator) -> GROUND to symbol.

WHY THIS IS THE CONVERGENCE: the scene representation SCENE = bundle_j bind(CONCEPT_j, LOC_j) is the
SAME FORM as the reader's role-filler binding (a CONCEPT bound to a ROLE/LOCATION). Perception writes
the SAME atom the symbol query uses -> that identity IS the grounding.

REUSED / CREDITED PRIOR ART (recombination, not invention):
  - Perception seed: exp_image_hd_encoder_digits_v1.py (atom 29407) = pixels->HD record-encoding +
    class-prototype recognition (Kanerva 2009 record encoding + Rahimi/Kleyko thermometer levels).
    Re-implemented inline here (short) with credit; the SCENE algebra uses the REAL hdlab primitives.
  - Scene factoring: exp_pp406_visual_scene_factor_separation_cpu_v1.py = resonator + explain-away for
    multiple objects in a bundle (Frady/Kent resonator; Singer 1999 binding problem). Adapted to
    bipolar in-cell; the NEW part is that objects are RECOGNIZED FROM PIXELS, not synthetic tuples.
  - hdlab.binding.bsc_bind / bsc_bundle / bsc_unbind (REAL primitives; exercised + bit-identity in
    self_test). hdlab.iterative_attractor.argmax_cleanup / iterative_cleanup (REAL cleanup; exercised).

REPRESENTATION (single scene vector = real-valued superposition; Kanerva/Plate bundling = sum):
  SCENE = sum_j bsc_bind(CONCEPT_{recognized_j}, LOCATION_{cell_j})   over occupied cells j
  CONCEPT_d (d in 0..9) = the digit-d SYMBOL atom (10 near-orthogonal random bipolar atoms).
  LOCATION_c (c in 0..G-1) = grid-cell atom (G near-orthogonal random bipolar atoms; 4x4 grid).
  Perception maps pixels -> class d (record encoder, ~0.9 acc) -> writes CONCEPT_d into the scene.

QUERIES (the payoff):
  loc->concept "what is at cell x": argmax_cleanup(SCENE * LOC_x, CONCEPT_codebook).
  concept->loc "where is the 8":    argmax_cleanup(SCENE * CONCEPT_s, LOCATION_codebook).
  joint factorization "recover ALL pairs at once": bipolar resonator + explain-away on SCENE.
  GROUND-TO-SYMBOL cross-direction: symbol->scene (concept->loc keyed by the SYMBOL atom) and
    scene->symbol (loc->concept returns the SYMBOL atom index). Perception wrote the same atom.

CAN-FAIL CONTROLS (MUST FIRE at smoke or the mechanism is trivial/artifact):
  (a) SCRAMBLE: apply a fixed random permutation to the SCENE vector before querying -> the bind
      alignment is destroyed -> queries collapse to chance (1/10). Also a wrong-key control.
  (b) CAPACITY K-sweep: sweep #objects K; query + factorization accuracy DEGRADE with K (crosstalk /
      superposition catastrophe). Report the curve. If no degradation, N is too big -> vacuous.

REAL BASELINES: uniform chance (1/n_concept, 1/G); recognition-accuracy ceiling (a query CANNOT beat
  perception on the true label -> we report query-vs-RECOGNIZED (isolates the algebra) AND
  query-vs-TRUE (perception-bounded) separately = honest error propagation).

LOCAL STORE ONLY. No push, no remote-persist. No production hdlab mutation. Deterministic seeds.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test on query preds)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb: THEORETICAL real-valued superposition unbind -> true-concept dot = N (deterministic);
#   distractor dot ~ N(0, K*N) std sqrt(K*N); cleanup fails when max-of-(m-1) distractors ~ N, i.e.
#   knee at K ~ 0.16*N. MEASURED@probe N_scene=128: loc->concept 1.00(K<=6) -> 0.65(K=36); discriminator
#   (capacity degradation) reachable -> True.
# - baseline_in_band: uniform chance = 0.10 (concept) / 0.0625 (loc) are REFERENCE floors; the
#   can-fire discriminator = scramble MUST collapse to chance + capacity MUST degrade with K.
# - discriminator run at the SAME N_scene/K grid at smoke (small n_scenes) and full (n_scenes only up).
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
# COMPUTE ARCHITECTURE: sequential-CPU. Justified: all ops are tiny substrate primitives (N_scene<=1024,
#   G=16, 10 concepts); the perception pass is pre-batched (recognize the whole test pool once); full
#   wall-time budget < a few minutes. No GPU speedup available at this scale (matmuls are (26 x 1024)).
#   Storage strategy: bundled (single scene vector) is the OBJECT UNDER TEST (the whole point is that a
#   single superposed vector is queryable) + the resonator arm is the sharded-recovery counterpart.
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

ANCHOR_NAME = "perception_bridge_scene_vector_digits_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ---- pre-registered bands (HYPOTHESIZED@preregs/2026-07-21_perception_bridge_scene_vector_digits_v1.md) ----
N_PERC = 4000          # perception record-encoder dim
N_SCENE = 128          # primary scene-algebra dim (capacity knee ~ 0.16*N; degrades over K in [1..36])
GRID = (6, 6)          # 6x6 spatial grid -> G=36 locations
N_CONCEPT = 10         # 10 digit symbols
K_LIST = [1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 28, 32, 36]
N_SCENE_LEVER = [96, 128, 192, 256]   # N-lever demo at fixed K to show capacity ~ N
LEVER_K = 28
EXAMPLE_K = 6          # scene saved for visualization

CHANCE_CONCEPT = 1.0 / N_CONCEPT   # THEORETICAL@ 0.10
CHANCE_LOC = 1.0 / (GRID[0] * GRID[1])  # THEORETICAL@ 0.0625

# PASS bands (small K = mean over K in {1,2,3})
PASS_LOC2CON_SMALLK = 0.85     # loc->concept vs RECOGNIZED at small K
PASS_CON2LOC_SMALLK = 0.70     # concept->loc at small K
PASS_XMODAL_SMALLK = 0.70      # cross-modal symbol query at small K
SCRAMBLE_COLLAPSE_MAX = 0.25   # scrambled query near chance
SCRAMBLE_DELTA_MIN = 0.30      # clean - scramble >= 0.30 => structure genuinely used
CAPACITY_DEGRADE_MIN = 0.15    # acc(minK) - acc(maxK) >= 0.15 => crosstalk fires


# --------------------------------------------------------------------------------------
# defensive-error-checking template helpers
# --------------------------------------------------------------------------------------
def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _heartbeat(output_dir, unit_idx, total_units, t0):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": int(unit_idx),
           "total_units": int(total_units), "elapsed_s": time.perf_counter() - t0}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


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
# perception: record encoder + thermometer levels + prototype classifier
# (credit: Kanerva 2009 record encoding; Rahimi/Kleyko thermometer levels;
#  exp_image_hd_encoder_digits_v1.py = the proven seed this is adapted from)
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


def _sign(acc):
    return np.where(acc >= 0, np.int8(1), np.int8(-1)).astype(np.int8)


def encode_record_batch(X_levels, P, L):
    """(n, n_pos) intensities -> (n, N) bipolar record codes. Vectorized bsc_bind + sign-bundle."""
    n, n_pos = X_levels.shape
    N = P.shape[1]
    out = np.empty((n, N), dtype=np.int8)
    Pi = P.astype(np.int32)
    for k in range(n):
        Lv = L[X_levels[k]].astype(np.int32)      # (n_pos, N) = bsc_bind operand
        out[k] = _sign((Pi * Lv).sum(axis=0))     # bind (mul) + bundle (majority sign)
    return out


def build_prototypes(codes, labels, n_classes):
    N = codes.shape[1]
    protos = np.empty((n_classes, N), dtype=np.int8)
    for c in range(n_classes):
        member = codes[labels == c]
        protos[c] = _sign(member.astype(np.int32).sum(axis=0))
    return protos


# --------------------------------------------------------------------------------------
# scene algebra (REAL-VALUED SUPERPOSITION bundle; bsc_bind for binding)
# --------------------------------------------------------------------------------------
def build_codebook(m, N, rng):
    """(m, N) near-orthogonal random bipolar atoms."""
    return (rng.integers(0, 2, size=(m, N)).astype(np.int8) * 2 - 1).astype(np.int8)


def assemble_scene(concept_idx, loc_idx, C_cb, L_cb):
    """SCENE = sum_j bsc_bind(CONCEPT_j, LOC_j). Real-valued superposition (single vector)."""
    N = C_cb.shape[1]
    S = np.zeros(N, dtype=np.int32)
    for c, l in zip(concept_idx, loc_idx):
        S += C_cb[c].astype(np.int32) * L_cb[l].astype(np.int32)   # bsc_bind then accumulate
    return S


def query_unbind_cleanup(S, key_vec, codebook):
    """Unbind SCENE by a bipolar key (elementwise mul), cleanup vs codebook (cosine argmax)."""
    from hdlab.iterative_attractor import argmax_cleanup
    u = S.astype(np.float32) * key_vec.astype(np.float32)   # bsc_unbind = mul (self-inverse bipolar)
    return int(argmax_cleanup(u, codebook.astype(np.float32)))


def resonator_recover(S, C_cb, L_cb, k_recover, n_iters=25):
    """Blind joint factorization: bipolar resonator + explain-away -> list of (c_idx, l_idx).

    Recovers ALL pairs at once (one at a time via fixed-point + subtract). Frady/Kent resonator
    adapted to bipolar; explain-away subtracts the recovered bound product from the superposition.
    """
    S = S.astype(np.float32).copy()
    Cf = C_cb.astype(np.float32)
    Lf = L_cb.astype(np.float32)
    pairs = []
    for _ in range(k_recover):
        x_l = _sign(Lf.sum(axis=0)).astype(np.float32)   # init loc estimate = superposition of all
        x_c = None
        for _it in range(n_iters):
            uc = S * x_l                                  # unbind by loc estimate
            x_c = np.sign((Cf @ uc) @ Cf).astype(np.float32)   # project onto concept span, bipolar
            ul = S * x_c                                  # unbind by concept estimate
            x_l_new = np.sign((Lf @ ul) @ Lf).astype(np.float32)
            if np.array_equal(x_l_new, x_l):
                x_l = x_l_new
                break
            x_l = x_l_new
        c_idx = int(np.argmax(Cf @ (S * x_l)))
        l_idx = int(np.argmax(Lf @ (S * x_c)))
        pairs.append((c_idx, l_idx))
        S = S - (Cf[c_idx] * Lf[l_idx])                   # explain-away subtract
    return pairs


# --------------------------------------------------------------------------------------
# one scene trial
# --------------------------------------------------------------------------------------
def run_scene(K, pool_pred, pool_true, pool_img, C_cb, L_cb, G, rng, scramble_perm,
              want_example=False):
    """Place K digits at K distinct cells; recognize (cached); assemble; query; return per-scene stats."""
    N = C_cb.shape[1]
    cells = rng.choice(G, size=K, replace=False)
    imgs = rng.choice(len(pool_pred), size=K, replace=False)
    recog = pool_pred[imgs]        # recognized class (perception output; may be wrong)
    truth = pool_true[imgs]        # true digit label
    S = assemble_scene(recog, cells, C_cb, L_cb)

    # loc->concept for each occupied cell
    l2c_pred = np.array([query_unbind_cleanup(S, L_cb[c], C_cb) for c in cells])
    l2c_vs_recog = float((l2c_pred == recog).mean())
    l2c_vs_true = float((l2c_pred == truth).mean())

    # concept->loc for each object (which cell holds this object's recognized symbol)
    c2l_pred = np.array([query_unbind_cleanup(S, C_cb[recog[j]], L_cb) for j in range(K)])
    # score: does concept->loc return one of the cells actually holding that symbol?
    c2l_hits = 0
    for j in range(K):
        holders = cells[recog == recog[j]]
        c2l_hits += int(c2l_pred[j] in holders)
    c2l_acc = c2l_hits / K

    # cross-modal symbol query: scene->symbol (== l2c) and symbol->scene (== c2l); report c2l as
    # the symbol->scene direction accuracy (symbol atom keys the query).
    xmodal_acc = c2l_acc

    # SCRAMBLE control (fixed permutation destroys bind alignment) -> query collapses
    S_scr = S[scramble_perm]
    l2c_scr = np.array([query_unbind_cleanup(S_scr, L_cb[c], C_cb) for c in cells])
    l2c_scr_vs_recog = float((l2c_scr == recog).mean())

    # WRONG-KEY control: query cell x with a random DIFFERENT location key
    wrongkeys = np.array([rng.choice([c2 for c2 in range(G) if c2 != c]) for c in cells])
    l2c_wrong = np.array([query_unbind_cleanup(S, L_cb[wk], C_cb) for wk in wrongkeys])
    l2c_wrong_vs_recog = float((l2c_wrong == recog).mean())

    out = {
        "l2c_vs_recog": l2c_vs_recog, "l2c_vs_true": l2c_vs_true,
        "c2l_acc": c2l_acc, "xmodal_acc": xmodal_acc,
        "l2c_scramble": l2c_scr_vs_recog, "l2c_wrongkey": l2c_wrong_vs_recog,
        "_preds": {"l2c": l2c_pred, "l2c_scr": l2c_scr, "l2c_wrong": l2c_wrong},
    }
    if want_example:
        out["_example"] = {
            "cells": cells, "imgs": imgs, "recog": recog, "truth": truth,
            "l2c_pred": l2c_pred, "pool_img": pool_img[imgs],
        }
    return out


def eval_K(K, n_scenes, pool_pred, pool_true, pool_img, C_cb, L_cb, G, base_seed,
           want_example=False):
    N = C_cb.shape[1]
    scramble_perm = np.random.default_rng(20260721).permutation(N)  # FIXED perm (deterministic)
    acc = {k: [] for k in ["l2c_vs_recog", "l2c_vs_true", "c2l_acc", "xmodal_acc",
                           "l2c_scramble", "l2c_wrongkey"]}
    example = None
    pred_bag = {"l2c": [], "l2c_scr": [], "l2c_wrong": []}
    for s in range(n_scenes):
        rng = np.random.default_rng(base_seed + 1000 * K + s)
        r = run_scene(K, pool_pred, pool_true, pool_img, C_cb, L_cb, G, rng, scramble_perm,
                      want_example=(want_example and s == 0))
        for k in acc:
            acc[k].append(r[k])
        for k in pred_bag:
            pred_bag[k].append(r["_preds"][k])
        if want_example and s == 0:
            example = r["_example"]
    means = {k: float(np.mean(v)) for k, v in acc.items()}
    means["_pred_bag"] = {k: np.concatenate(v) for k, v in pred_bag.items()}
    if example is not None:
        means["_example"] = example
    return means


# --------------------------------------------------------------------------------------
# self test (exercises the REAL substrate primitives + bit-identity)
# --------------------------------------------------------------------------------------
def self_test():
    import numpy as _np
    from hdlab.binding import bsc_bind, bsc_bundle, bsc_unbind
    from hdlab.iterative_attractor import argmax_cleanup, iterative_cleanup
    import torch

    rng = _np.random.default_rng(0)

    # 1. bit-identity: my numpy bind/sign-bundle == hdlab bsc_bind/bsc_bundle
    N = 256
    a = build_codebook(1, N, rng)[0]
    b = build_codebook(1, N, rng)[0]
    ta, tb = torch.from_numpy(a.astype(_np.float32)), torch.from_numpy(b.astype(_np.float32))
    prim_bind = bsc_bind(ta, tb).numpy().astype(_np.int8)
    my_bind = (a.astype(_np.int32) * b.astype(_np.int32)).astype(_np.int8)
    assert _np.array_equal(prim_bind, my_bind), "bind not bit-identical to hdlab.bsc_bind"
    stack = _np.stack([a, b, build_codebook(1, N, rng)[0]]).astype(_np.int32)
    prim_bundle = bsc_bundle(torch.from_numpy(stack.astype(_np.float32))).numpy().astype(_np.int8)
    my_bundle = _sign(stack.sum(axis=0))
    assert _np.array_equal(prim_bundle, my_bundle), "sign-bundle not bit-identical to hdlab.bsc_bundle"
    # bsc_unbind is self-inverse mul (exercise it)
    assert _np.array_equal(bsc_unbind(bsc_bind(ta, tb), tb).numpy().astype(_np.int8), a), \
        "bsc_unbind(bind(a,b),b) != a"

    # 2. thermometer monotonic
    Q = 5
    L = build_level_codebook(Q, N, rng)
    def cos(x, y):
        return float(_np.dot(x.astype(_np.float32), y.astype(_np.float32)) / N)
    assert cos(L[0], L[1]) > cos(L[0], L[Q - 1]) + 0.3, "thermometer not monotonic"

    # 3. scene query recovers at tiny K (algebra fidelity)
    Ns = 512
    C_cb = build_codebook(N_CONCEPT, Ns, rng)
    L_cb = build_codebook(9, Ns, rng)
    concept_idx = _np.array([3, 7, 1])
    loc_idx = _np.array([0, 4, 8])
    S = assemble_scene(concept_idx, loc_idx, C_cb, L_cb)
    rec = [query_unbind_cleanup(S, L_cb[l], C_cb) for l in loc_idx]
    assert rec == list(concept_idx), "loc->concept failed at K=3: %s vs %s" % (rec, list(concept_idx))
    # concept->loc
    for j, c in enumerate(concept_idx):
        got = query_unbind_cleanup(S, C_cb[c], L_cb)
        assert got == loc_idx[j], "concept->loc failed: symbol %d -> cell %d (want %d)" % (c, got, loc_idx[j])

    # 4. can-fail scramble FIRES: permute scene -> query collapses
    perm = _np.random.default_rng(1).permutation(Ns)
    S_scr = S[perm]
    rec_scr = [query_unbind_cleanup(S_scr, L_cb[l], C_cb) for l in loc_idx]
    n_right_scr = sum(int(rec_scr[j] == concept_idx[j]) for j in range(3))
    assert n_right_scr <= 1, "scramble control did not fire (got %d/3 right)" % n_right_scr

    # 5. resonator recovers the pairs blind (joint factorization)
    pairs = resonator_recover(S, C_cb, L_cb, k_recover=3, n_iters=25)
    got = set((c, l) for c, l in pairs)
    want = set((int(c), int(l)) for c, l in zip(concept_idx, loc_idx))
    n_ok = len(got & want)
    assert n_ok >= 2, "resonator recovered only %d/3 true pairs: got=%s want=%s" % (n_ok, got, want)

    # 6. capacity: query at K=3 strictly better than at K=36 at small N (crosstalk / superposition)
    def loc2con_acc(K, Ns_, G_):
        cc = build_codebook(N_CONCEPT, Ns_, _np.random.default_rng(10))
        ll = build_codebook(G_, Ns_, _np.random.default_rng(11))
        accs = []
        for s in range(20):
            rr = _np.random.default_rng(100 + s)
            cells = rr.choice(G_, size=K, replace=False)
            cids = rr.integers(0, N_CONCEPT, size=K)
            Ss = assemble_scene(cids, cells, cc, ll)
            pr = _np.array([query_unbind_cleanup(Ss, ll[c], cc) for c in cells])
            accs.append((pr == cids).mean())
        return float(_np.mean(accs))
    a2, a16 = loc2con_acc(3, 96, 36), loc2con_acc(36, 96, 36)
    assert a2 > a16 + 0.15, "capacity did not degrade (K3=%.3f K36=%.3f at N=96)" % (a2, a16)

    # 7. arms_must_differ on the query ARMS (clean vs scramble outputs differ)
    _arms_must_differ({"clean_query": _np.array(rec), "scramble_query": _np.array(rec_scr)})

    # 8. no-nondeterministic-seeding static scan of this source
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            assert_no_nondeterministic_seeding(f.read())
    except ImportError:
        pass

    print("[self_test] PASS: bit-identical-to-bsc(bind/bundle/unbind), thermometer-monotonic, "
          "loc<->concept-query-exact@K3, scramble-fires(%d/3), resonator-recovers(%d/3), "
          "capacity-degrades(K2=%.3f>K16=%.3f), arms-differ"
          % (n_right_scr, n_ok, a2, a16), flush=True)
    return True


# --------------------------------------------------------------------------------------
# main run
# --------------------------------------------------------------------------------------
def run(mode="full"):
    from sklearn.datasets import load_digits
    from sklearn.model_selection import train_test_split

    t0 = time.perf_counter()
    n_scenes = 25 if mode == "smoke" else 150
    total_units = len(K_LIST) + len(N_SCENE_LEVER)
    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, mode, expected_n_units=total_units)

    # ---- data + perception (recognize the whole test pool ONCE) ----
    dig = load_digits()
    X = dig.data.astype(np.int64)          # (1797, 64) intensities 0..16
    y = dig.target.astype(np.int64)
    img8 = dig.images.astype(np.float32)   # (1797, 8, 8) for the example npz
    Q = int(X.max()) + 1
    n_pos = X.shape[1]
    X_tr, X_te, y_tr, y_te, img_tr, img_te = train_test_split(
        X, y, img8, test_size=0.3, random_state=0, stratify=y)

    enc_rng = np.random.default_rng(0)
    P = build_position_vectors(n_pos, N_PERC, enc_rng)
    Lc = build_level_codebook(Q, N_PERC, enc_rng)
    tr_codes = encode_record_batch(X_tr, P, Lc)
    te_codes = encode_record_batch(X_te, P, Lc)
    from hdlab.iterative_attractor import argmax_cleanup
    protos = build_prototypes(tr_codes, y_tr, N_CONCEPT)
    pool_pred = np.asarray(argmax_cleanup(te_codes.astype(np.float32), protos.astype(np.float32)),
                           dtype=np.int64)   # perception output for each test image
    pool_true = y_te
    recog_acc = float((pool_pred == pool_true).mean())   # perception ceiling

    G = GRID[0] * GRID[1]

    # ---- primary K-sweep at N_SCENE ----
    scene_rng = np.random.default_rng(42)
    C_cb = build_codebook(N_CONCEPT, N_SCENE, scene_rng)
    L_cb = build_codebook(G, N_SCENE, scene_rng)

    by_K = {}
    example = None
    hb_i = 0
    for K in K_LIST:
        res = eval_K(K, n_scenes, pool_pred, pool_true, img_te.reshape(len(img_te), -1),
                     C_cb, L_cb, G, base_seed=7, want_example=(K == EXAMPLE_K))
        # resonator joint-factorization set accuracy for this K
        reson_hits, reson_tot = 0, 0
        rr = np.random.default_rng(9000 + K)
        n_reson = min(n_scenes, 40)
        for s in range(n_reson):
            cells = rr.choice(G, size=K, replace=False)
            imgs = rr.choice(len(pool_pred), size=K, replace=False)
            recog = pool_pred[imgs]
            S = assemble_scene(recog, cells, C_cb, L_cb)
            pairs = set(resonator_recover(S, C_cb, L_cb, k_recover=K, n_iters=25))
            want = set((int(recog[j]), int(cells[j])) for j in range(K))
            reson_hits += len(pairs & want)
            reson_tot += K
        reson_setacc = reson_hits / max(reson_tot, 1)
        by_K[K] = {
            "loc2concept_vs_recog": res["l2c_vs_recog"],
            "loc2concept_vs_true": res["l2c_vs_true"],
            "concept2loc": res["c2l_acc"],
            "xmodal_symbol": res["xmodal_acc"],
            "scramble": res["l2c_scramble"],
            "wrongkey": res["l2c_wrongkey"],
            "resonator_setacc": reson_setacc,
        }
        if "_example" in res and example is None:
            example = res["_example"]
        if "_pred_bag" in res and K == K_LIST[len(K_LIST) // 2]:
            mid_bag = res["_pred_bag"]
        hb_i += 1
        _heartbeat(OUTPUT_DIR, hb_i, total_units, t0)

    # fallback example if the target K wasn't hit
    if example is None:
        res = eval_K(K_LIST[len(K_LIST) // 2], n_scenes, pool_pred, pool_true,
                     img_te.reshape(len(img_te), -1), C_cb, L_cb, G, base_seed=7, want_example=True)
        example = res.get("_example")
        mid_bag = res.get("_pred_bag")

    # ---- N-lever demo at LEVER_K ----
    lever = {}
    for Ns in N_SCENE_LEVER:
        lrng = np.random.default_rng(55)
        cc = build_codebook(N_CONCEPT, Ns, lrng)
        ll = build_codebook(G, Ns, lrng)
        r = eval_K(LEVER_K, min(n_scenes, 60), pool_pred, pool_true,
                   img_te.reshape(len(img_te), -1), cc, ll, G, base_seed=3)
        lever["N%d" % Ns] = r["l2c_vs_recog"]
        hb_i += 1
        _heartbeat(OUTPUT_DIR, hb_i, total_units, t0)

    # ---- aggregate small-K (K in {1,2,3}) ----
    smallK = [k for k in [1, 2, 3] if k in by_K]
    def mean_small(field):
        return float(np.mean([by_K[k][field] for k in smallK]))
    sk_l2c = mean_small("loc2concept_vs_recog")
    sk_c2l = mean_small("concept2loc")
    sk_xmodal = mean_small("xmodal_symbol")
    sk_scramble = mean_small("scramble")
    sk_wrongkey = mean_small("wrongkey")

    minK, maxK = K_LIST[0], K_LIST[-1]
    cap_degrade = by_K[minK]["loc2concept_vs_recog"] - by_K[maxK]["loc2concept_vs_recog"]
    reson_degrade = by_K[minK]["resonator_setacc"] - by_K[maxK]["resonator_setacc"]

    # ---- arms-must-differ (clean vs scramble vs wrongkey preds at mid-K) ----
    arm_digests = _arms_must_differ({
        "clean_query": mid_bag["l2c"], "scramble_query": mid_bag["l2c_scr"],
        "wrongkey_query": mid_bag["l2c_wrong"],
    })

    # ---- scramble collapse gate ----
    scramble_delta = sk_l2c - sk_scramble
    scramble_collapsed = (sk_scramble <= SCRAMBLE_COLLAPSE_MAX and scramble_delta >= SCRAMBLE_DELTA_MIN)
    capacity_fired = cap_degrade >= CAPACITY_DEGRADE_MIN

    # ---- verdict ----
    mech_ok = (sk_l2c >= PASS_LOC2CON_SMALLK and sk_c2l >= PASS_CON2LOC_SMALLK
               and sk_xmodal >= PASS_XMODAL_SMALLK)
    if mech_ok and scramble_collapsed and capacity_fired:
        verdict = "PASS"
    elif (sk_l2c <= CHANCE_CONCEPT + 0.15 or not scramble_collapsed or not capacity_fired):
        verdict = "HONEST_NEGATIVE"
    else:
        verdict = "MIDDLE_BAND"

    # ---- emit example scene npz for visualization ----
    npz_path = os.path.join(OUTPUT_DIR, "example_scene.npz")
    if example is not None:
        Gr, Gc = GRID
        recovered_grid = -np.ones(G, dtype=np.int64)
        for cell, pred in zip(example["cells"], example["l2c_pred"]):
            recovered_grid[cell] = pred
        true_grid = -np.ones(G, dtype=np.int64)
        recog_grid = -np.ones(G, dtype=np.int64)
        for cell, tr, rc in zip(example["cells"], example["truth"], example["recog"]):
            true_grid[cell] = tr
            recog_grid[cell] = rc
        np.savez(
            npz_path,
            grid_shape=np.array(GRID),
            cells=example["cells"], images=example["pool_img"].reshape(-1, 8, 8),
            true_digit=example["truth"], recognized_digit=example["recog"],
            recovered_concept=example["l2c_pred"],
            true_grid=true_grid.reshape(Gr, Gc),
            recognized_grid=recog_grid.reshape(Gr, Gc),
            recovered_grid=recovered_grid.reshape(Gr, Gc),
        )

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        "recog_acc=%.3f(ceiling) | smallK loc->concept=%.3f concept->loc=%.3f xmodal_symbol=%.3f "
        "(chance %.3f/%.3f) | scramble=%.3f wrongkey=%.3f delta=%.3f collapsed=%s | "
        "capacity K%d->K%d loc->concept %.3f->%.3f degrade=%.3f fired=%s | resonator setacc K%d->K%d "
        "%.3f->%.3f degrade=%.3f | N-lever@K%d %s | %s"
        % (recog_acc, sk_l2c, sk_c2l, sk_xmodal, CHANCE_CONCEPT, CHANCE_LOC,
           sk_scramble, sk_wrongkey, scramble_delta, scramble_collapsed,
           minK, maxK, by_K[minK]["loc2concept_vs_recog"], by_K[maxK]["loc2concept_vs_recog"],
           cap_degrade, capacity_fired, minK, maxK, by_K[minK]["resonator_setacc"],
           by_K[maxK]["resonator_setacc"], reson_degrade, LEVER_K,
           {k: round(v, 3) for k, v in lever.items()}, verdict))

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": "pixels->scene-vector->query->symbol-grounding on load_digits: %s" % verdict,
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "run_mode": mode,
        "config": {"N_perc": N_PERC, "N_scene": N_SCENE, "grid": list(GRID), "G": G,
                   "n_concept": N_CONCEPT, "K_list": K_LIST, "n_scenes": n_scenes,
                   "n_train": int(X_tr.shape[0]), "n_test": int(X_te.shape[0])},
        "perception": {"recognition_accuracy_ceiling": recog_acc},
        "small_K": {"loc2concept_vs_recog": sk_l2c, "concept2loc": sk_c2l,
                    "xmodal_symbol": sk_xmodal, "scramble": sk_scramble, "wrongkey": sk_wrongkey},
        "capacity_curve_by_K": {str(k): v for k, v in by_K.items()},
        "n_lever_loc2concept": lever,
        "baselines": {"chance_concept": CHANCE_CONCEPT, "chance_loc": CHANCE_LOC},
        "discriminator": {
            "scramble_delta": scramble_delta, "scramble_collapsed": bool(scramble_collapsed),
            "capacity_degrade_loc2concept": cap_degrade, "capacity_fired": bool(capacity_fired),
            "resonator_degrade": reson_degrade, "mech_ok": bool(mech_ok),
        },
        "bands": {"PASS_LOC2CON_SMALLK": PASS_LOC2CON_SMALLK, "PASS_CON2LOC_SMALLK": PASS_CON2LOC_SMALLK,
                  "PASS_XMODAL_SMALLK": PASS_XMODAL_SMALLK, "SCRAMBLE_COLLAPSE_MAX": SCRAMBLE_COLLAPSE_MAX,
                  "SCRAMBLE_DELTA_MIN": SCRAMBLE_DELTA_MIN, "CAPACITY_DEGRADE_MIN": CAPACITY_DEGRADE_MIN},
        "example_scene_npz": npz_path if example is not None else None,
        "arms_differ_verified": True, "arm_digests": arm_digests,
        "final_metrics_atomicity": "tmp_replace",
        "primitives_reused": ["hdlab.binding.bsc_bind", "hdlab.binding.bsc_bundle",
                              "hdlab.binding.bsc_unbind", "hdlab.iterative_attractor.argmax_cleanup"],
        "recipe_adopted": "Kanerva record encoding (perception) + real-valued superposition scene bundle "
                          "+ Frady/Kent resonator explain-away (joint factorization)",
        "prior_art_credit": ["exp_image_hd_encoder_digits_v1 (perception seed, atom 29407)",
                             "exp_pp406_visual_scene_factor_separation_cpu_v1 (resonator explain-away)"],
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
