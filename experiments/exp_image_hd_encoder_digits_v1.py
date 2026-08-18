"""Image -> HD encoder proof on real image data (sklearn load_digits, 8x8, 10 classes).

VISION-TRACK FOUNDATION CELL. Answers 3 questions:
  (1) Does the substrate encode real images with STRUCTURE PRESERVED? (same-class HD cosine
      > diff-class HD cosine; 2D position recoverable by unbinding).
  (2) Raw-pixel HDC classification accuracy vs pixel-space baselines (kNN + linear) + chance
      = the HONEST ceiling of raw-pixel HDC.
  (3) Does it wire in cleanly from primitives we already own (bsc_bind/bsc_bundle +
      iterative_attractor cleanup)? = the "encoder was buildable all along" proof.

ADOPTED RECIPE (credit prior art; NOT invented from scratch):
  - Record-based position-value encoding (Kanerva 2009, hyperdimensional computing):
    each grid cell i gets a random bipolar position hypervector P_i; image_hv =
    BSC-bundle_i( bsc_bind(P_i, L_intensity(i)) ) = majority_sign( sum_i P_i * L_i ).
  - LEVEL / thermometer hypervectors for pixel intensity (Rahimi et al. 2016; Rachkovskij;
    Kleyko HDC-vision line): L_0 random bipolar, each successive level flips a fixed disjoint
    block of N/(Q-1) bits, so L_0 vs L_{Q-1} anti-correlated and adjacent levels near-identical
    (MONOTONIC intensity code -> preserves magnitude ordering).
  - Recognition via iterative_attractor cleanup (hdlab.iterative_attractor.iterative_cleanup)
    over the 10 class-prototype codebook = glass-box settling readout.

PRIMITIVES REUSED (no production hdlab mutation; composed in-cell):
  hdlab.binding.bsc_bind (elementwise mul), bsc_bundle (majority sign),
  hdlab.iterative_attractor.iterative_cleanup (soft-attractor cleanup), argmax_cleanup.
  The FULL run uses a vectorized-numpy path that is bit-identical to bsc_bind/bsc_bundle
  (verified in self_test on a sample) for memory/speed; the substrate primitives ARE
  elementwise-mul + majority-sign, so this is the same operation, not a re-implementation.

CAN-FAIL CONTROL (must fire): HD_scramble applies a PER-IMAGE independent random permutation
  of the grid positions before binding. A single GLOBAL fixed permutation is a mathematical
  isomorphism (all images relabelled identically -> classification invariant; verified inline
  as HD_fixed_global ~= HD_record), so it CANNOT be the discriminator. The discriminating
  scramble is PER-IMAGE independence: it destroys position-wise agreement between same-class
  images, so the record encoding's cosine structure collapses toward chance. If per-image
  scramble does NOT drop accuracy, the encoder is not using image structure = artifact.

REFERENCE ARM: HD_value_only = majority_sign( sum_i L_i ) (no position binding) = the
  position-invariant intensity code; isolates how much position binding buys over pure levels.

LOCAL STORE ONLY. No push, no remote-persist. Single deterministic split + encoder seed.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: not a noise-floor cap cell (discriminator = record-vs-scramble accuracy gap)
# - baseline framing: pixel_knn/pixel_linear are REFERENCE CEILINGS (expected ~0.95-0.99);
#   META_RULE_AG 0.95 cap does NOT apply to them. The can-fire discriminator = HD_scramble
#   which MUST collapse toward chance (that is the AG-style "control fires" gate here).
# - discriminator run at FULL scale (full dataset, full N); smoke pre-verifies record>scramble.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
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
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "image_hd_encoder_digits_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bands (HYPOTHESIZED@preregs/2026-07-21_image_hd_encoder_digits_v1.md) ----
CHANCE = 0.10  # THEORETICAL@ 10 roughly-balanced classes
PASS_RECORD_MIN = 0.55        # HD_record well above chance
SCRAMBLE_COLLAPSE_MAX = 0.25  # scramble must fall near chance
SCRAMBLE_DELTA_MIN = 0.30     # record - scramble >= 0.30 => structure genuinely used
STRUCT_GAP_MIN = 0.02         # same-class cosine - diff-class cosine strictly positive


# --------------------------------------------------------------------------------------
# defensive-error-checking template helpers
# --------------------------------------------------------------------------------------
def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
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
    """arms_outputs: dict {arm_name: ndarray}. Assert no two arms bit-identical."""
    digests = {}
    for name, out in arms_outputs.items():
        b = np.ascontiguousarray(out).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical (hash=%s)" % (a, b, digests[a])
            )
    return digests


# --------------------------------------------------------------------------------------
# encoder (record-based position-value; thermometer level code)
# --------------------------------------------------------------------------------------
def build_position_vectors(n_pos, N, rng):
    """(n_pos, N) random bipolar {-1,+1} position hypervectors (Kanerva record encoding)."""
    return (rng.integers(0, 2, size=(n_pos, N)).astype(np.int8) * 2 - 1).astype(np.int8)


def build_level_codebook(Q, N, rng):
    """(Q, N) thermometer level hypervectors: adjacent levels near-identical, extremes anti-correlated.

    L_0 random bipolar; step q flips a disjoint block of N//(Q-1) bits. MONOTONIC magnitude code.
    """
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


def _bipolar_bundle_sign(acc):
    """majority sign of an int accumulator; ties -> +1 (mirrors hdlab.binding.bsc_bundle)."""
    return np.where(acc >= 0, np.int8(1), np.int8(-1)).astype(np.int8)


def encode_record(intensities, P, L):
    """image_hv = majority_sign( sum_i P_i * L_intensity(i) ). intensities: (n_pos,) int in [0,Q).

    P_i * L_v = bsc_bind (elementwise mul); sum + sign = bsc_bundle (majority). Bit-identical to
    hdlab.binding.bsc_bind / bsc_bundle (verified in self_test).
    """
    Lv = L[intensities]                       # (n_pos, N) int8
    bound = P.astype(np.int32) * Lv.astype(np.int32)  # bsc_bind
    acc = bound.sum(axis=0)                    # (N,)
    return _bipolar_bundle_sign(acc)


def encode_value_only(intensities, L):
    """position-invariant reference: majority_sign( sum_i L_intensity(i) ) (no position binding)."""
    Lv = L[intensities].astype(np.int32)
    return _bipolar_bundle_sign(Lv.sum(axis=0))


def encode_dataset(X_levels, P, L, mode="record", scramble_rng=None):
    """Encode all images. mode: record | value_only | scramble_perimage | fixed_global.

    scramble_perimage: independent random position permutation per image (the can-fail control).
    fixed_global: one permutation applied to every image (isomorphism witness).
    """
    n, n_pos = X_levels.shape
    N = P.shape[1]
    out = np.empty((n, N), dtype=np.int8)
    fixed_perm = None
    if mode == "fixed_global":
        # deterministic fixed perm: IDENTICAL across train/test calls (isomorphism witness).
        # Must NOT derive from the shared advancing scramble_rng (that would differ per call).
        fixed_perm = np.random.default_rng(424242).permutation(n_pos)
    for k in range(n):
        inten = X_levels[k]
        if mode == "record":
            out[k] = encode_record(inten, P, L)
        elif mode == "value_only":
            out[k] = encode_value_only(inten, L)
        elif mode == "scramble_perimage":
            perm = scramble_rng.permutation(n_pos)
            out[k] = encode_record(inten, P[perm], L)
        elif mode == "fixed_global":
            out[k] = encode_record(inten, P[fixed_perm], L)
        else:
            raise ValueError("unknown mode %r" % mode)
    return out


def build_prototypes(codes, labels, n_classes):
    """(n_classes, N) bipolar class prototypes via bsc_bundle over each class's training codes."""
    N = codes.shape[1]
    protos = np.empty((n_classes, N), dtype=np.int8)
    for c in range(n_classes):
        member = codes[labels == c]
        acc = member.astype(np.int32).sum(axis=0)
        protos[c] = _bipolar_bundle_sign(acc)
    return protos


def classify_cleanup(query_codes, protos, temp=2.0, max_steps=8):
    """iterative_attractor cleanup readout: argmax settled prototype = predicted class."""
    from hdlab.iterative_attractor import iterative_cleanup
    out = iterative_cleanup(
        query_codes.astype(np.float32), protos.astype(np.float32),
        temp=temp, max_steps=max_steps,
    )
    return np.asarray(out["argmax_idx"], dtype=np.int64)


def cosine_gap_same_vs_diff(codes, labels, rng, max_n=600):
    """same-class mean cosine minus diff-class mean cosine on bipolar codes."""
    n = codes.shape[0]
    if n > max_n:
        sel = rng.choice(n, size=max_n, replace=False)
        codes = codes[sel]
        labels = labels[sel]
        n = max_n
    C = codes.astype(np.float32)
    C /= (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    S = C @ C.T
    same_mask = (labels[:, None] == labels[None, :])
    off = ~np.eye(n, dtype=bool)
    same = S[same_mask & off]
    diff = S[(~same_mask) & off]
    return float(same.mean()), float(diff.mean())


def position_recovery(codes, X_levels, P, L, n_probe=20, rng=None):
    """Unbind each position, cleanup vs level codebook -> recovered intensity; accuracy vs true.

    Glass-box structure witness: if 2D layout is preserved, per-position intensity is recoverable
    above chance despite the lossy bundle.
    """
    from hdlab.iterative_attractor import argmax_cleanup
    n, n_pos = X_levels.shape
    Q = L.shape[0]
    probe_idx = (rng.choice(n, size=min(n_probe, n), replace=False) if rng is not None
                 else np.arange(min(n_probe, n)))
    exact = 0
    total = 0
    abs_err = 0.0
    Lf = L.astype(np.float32)
    for k in probe_idx:
        hv = codes[k].astype(np.float32)
        # unbind all positions at once: P_i * hv (bsc_unbind = mul)
        rec = P.astype(np.float32) * hv[None, :]     # (n_pos, N)
        pred = argmax_cleanup(rec, Lf)               # (n_pos,) recovered level idx
        true = X_levels[k]
        exact += int((pred == true).sum())
        abs_err += float(np.abs(pred - true).sum())
        total += n_pos
    return {
        "exact_level_acc": exact / max(total, 1),
        "chance_level_acc": 1.0 / Q,
        "mean_abs_level_err": abs_err / max(total, 1),
        "n_probe": int(len(probe_idx)),
    }


# --------------------------------------------------------------------------------------
# self test (exercises the REAL substrate primitives + bit-identity check)
# --------------------------------------------------------------------------------------
def self_test():
    import numpy as _np
    from hdlab.binding import bsc_bind, bsc_bundle
    from hdlab.iterative_attractor import iterative_cleanup
    import torch

    rng = _np.random.default_rng(0)
    N = 512
    n_pos = 8
    Q = 5
    P = build_position_vectors(n_pos, N, rng)
    L = build_level_codebook(Q, N, rng)

    # 1. thermometer monotonicity: adjacent levels more similar than extremes
    def cos(a, b):
        return float(_np.dot(a.astype(_np.float32), b.astype(_np.float32)) / N)
    assert cos(L[0], L[1]) > cos(L[0], L[Q - 1]) + 0.3, "thermometer not monotonic"
    assert cos(L[0], L[Q - 1]) < 0.1, "extreme levels should be near-anti-correlated"

    # 2. bit-identity: vectorized encode_record == looped hdlab bsc_bind + bsc_bundle
    inten = rng.integers(0, Q, size=n_pos)
    vec = encode_record(inten, P, L)
    stack = []
    for i in range(n_pos):
        a = torch.from_numpy(P[i].astype(_np.float32))
        b = torch.from_numpy(L[inten[i]].astype(_np.float32))
        stack.append(bsc_bind(a, b))
    prim = bsc_bundle(torch.stack(stack)).numpy().astype(_np.int8)
    assert _np.array_equal(vec, prim), "vectorized encode != hdlab bsc_bind/bsc_bundle (not bit-identical)"

    # 3. real code path: iterative_cleanup recovers the right prototype on a separable toy
    #    two classes of images that differ in intensity layout must be separable.
    n_per = 30
    Xa = _np.tile(_np.array([0, 0, 0, 0, 4, 4, 4, 4]), (n_per, 1))
    Xb = _np.tile(_np.array([4, 4, 4, 4, 0, 0, 0, 0]), (n_per, 1))
    # add small per-image jitter within valid range
    Xa = _np.clip(Xa + rng.integers(-1, 2, size=Xa.shape), 0, Q - 1)
    Xb = _np.clip(Xb + rng.integers(-1, 2, size=Xb.shape), 0, Q - 1)
    Xall = _np.vstack([Xa, Xb])
    yall = _np.array([0] * n_per + [1] * n_per)
    codes = encode_dataset(Xall, P, L, mode="record")
    protos = build_prototypes(codes, yall, 2)
    pred = classify_cleanup(codes, protos, temp=4.0, max_steps=6)
    acc = float((pred == yall).mean())
    assert acc > 0.9, "separable toy record-encoding should classify > 0.9 (got %.3f)" % acc

    # 4. can-fail control FIRES on separable toy: per-image scramble collapses it
    codes_s = encode_dataset(Xall, P, L, mode="scramble_perimage",
                             scramble_rng=_np.random.default_rng(1))
    protos_s = build_prototypes(codes_s, yall, 2)
    pred_s = classify_cleanup(codes_s, protos_s, temp=4.0, max_steps=6)
    acc_s = float((pred_s == yall).mean())
    assert acc_s < acc - 0.15, ("scramble control did not fire on separable toy: "
                                "record=%.3f scramble=%.3f" % (acc, acc_s))

    # 5. fixed-global permutation is an isomorphism (accuracy preserved)
    codes_f = encode_dataset(Xall, P, L, mode="fixed_global",
                             scramble_rng=_np.random.default_rng(2))
    protos_f = build_prototypes(codes_f, yall, 2)
    acc_f = float((classify_cleanup(codes_f, protos_f, temp=4.0, max_steps=6) == yall).mean())
    assert abs(acc_f - acc) < 0.05, ("fixed-global perm should be isomorphism (acc %.3f vs %.3f)"
                                     % (acc_f, acc))

    # 6. arms_must_differ
    _arms_must_differ({"record": codes, "scramble": codes_s, "value_only":
                       encode_dataset(Xall, P, L, mode="value_only")})

    # 7. no-nondeterministic-seeding static scan of this source
    try:
        from experiments._validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            assert_no_nondeterministic_seeding(f.read())
    except ImportError:
        pass

    print("[self_test] PASS: thermometer-monotonic, bit-identical-to-bsc_primitives, "
          "toy-record-acc=%.3f, scramble-fires(%.3f), fixed-global-isomorphism(%.3f), arms-differ"
          % (acc, acc_s, acc_f), flush=True)
    return True


# --------------------------------------------------------------------------------------
# main run
# --------------------------------------------------------------------------------------
def run(mode="full"):
    from sklearn.datasets import load_digits
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.linear_model import LogisticRegression

    t0 = time.perf_counter()
    if mode == "smoke":
        N = 2000
        n_subset = 400
        temp = 3.0
    else:
        N = 10000
        n_subset = None
        temp = 3.0

    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, mode, expected_n_units=1)

    dig = load_digits()
    X = dig.data.astype(np.int64)     # (1797, 64) intensities 0..16
    y = dig.target.astype(np.int64)
    Q = int(X.max()) + 1              # 17 intensity levels
    n_pos = X.shape[1]               # 64
    n_classes = 10

    if n_subset is not None:
        sub_rng = np.random.default_rng(123)
        sel = sub_rng.choice(X.shape[0], size=n_subset, replace=False)
        X, y = X[sel], y[sel]

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, random_state=0, stratify=y)

    enc_rng = np.random.default_rng(0)
    P = build_position_vectors(n_pos, N, enc_rng)
    L = build_level_codebook(Q, N, enc_rng)

    arms = {}
    codes_cache = {}
    for arm, kw in [
        ("HD_record", dict(mode="record")),
        ("HD_scramble", dict(mode="scramble_perimage", scramble_rng=np.random.default_rng(777))),
        ("HD_value_only", dict(mode="value_only")),
        ("HD_fixed_global", dict(mode="fixed_global", scramble_rng=np.random.default_rng(888))),
    ]:
        tr_codes = encode_dataset(X_tr, P, L, **kw)
        te_codes = encode_dataset(X_te, P, L, **kw)
        protos = build_prototypes(tr_codes, y_tr, n_classes)
        pred = classify_cleanup(te_codes, protos, temp=temp, max_steps=8)
        acc = float((pred == y_te).mean())
        arms[arm] = {"test_acc": acc}
        codes_cache[arm] = (tr_codes, te_codes, protos)

    # arms-must-differ on the test-set codes (record vs scramble vs value_only differ)
    arm_digests = _arms_must_differ({
        "HD_record": codes_cache["HD_record"][1],
        "HD_scramble": codes_cache["HD_scramble"][1],
        "HD_value_only": codes_cache["HD_value_only"][1],
    })

    # pixel-space baselines (reference ceilings) on identical split
    knn = KNeighborsClassifier(n_neighbors=3).fit(X_tr, y_tr)
    pixel_knn_acc = float(knn.score(X_te, y_te))
    lin = LogisticRegression(max_iter=3000).fit(X_tr, y_tr)
    pixel_linear_acc = float(lin.score(X_te, y_te))
    # majority-class + uniform chance
    _, counts = np.unique(y_te, return_counts=True)
    majority_chance = float(counts.max() / counts.sum())
    uniform_chance = 1.0 / n_classes

    # structure-preservation probe on HD_record test codes
    same_c, diff_c = cosine_gap_same_vs_diff(
        codes_cache["HD_record"][1], y_te, np.random.default_rng(5))
    struct_gap = same_c - diff_c

    # 2D position recovery (glass-box unbinding witness)
    pos_rec = position_recovery(
        codes_cache["HD_record"][1], X_te, P, L, n_probe=25,
        rng=np.random.default_rng(9))

    # one-step argmax cleanup witness (should agree with iterative)
    from hdlab.iterative_attractor import argmax_cleanup
    argmax_pred = argmax_cleanup(
        codes_cache["HD_record"][1].astype(np.float32),
        codes_cache["HD_record"][2].astype(np.float32))
    argmax_acc = float((np.asarray(argmax_pred) == y_te).mean())

    rec_acc = arms["HD_record"]["test_acc"]
    scr_acc = arms["HD_scramble"]["test_acc"]
    scramble_delta = rec_acc - scr_acc

    # ---- verdict logic ----
    collapsed = scr_acc <= SCRAMBLE_COLLAPSE_MAX and scramble_delta >= SCRAMBLE_DELTA_MIN
    well_above_chance = rec_acc >= PASS_RECORD_MIN
    structure_ok = struct_gap >= STRUCT_GAP_MIN
    if well_above_chance and collapsed and structure_ok:
        verdict = "PASS"
    elif rec_acc <= uniform_chance + 0.10 or scramble_delta < 0.15:
        verdict = "HONEST_NEGATIVE"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        "HD_record=%.3f pixel_kNN=%.3f pixel_linear=%.3f chance=%.3f | scramble=%.3f "
        "delta=%.3f collapsed=%s | struct_gap=%.3f (same=%.3f diff=%.3f) | "
        "value_only=%.3f fixed_global=%.3f (isomorphism_ok=%s) | posrec=%.3f(chance %.3f) | %s"
        % (rec_acc, pixel_knn_acc, pixel_linear_acc, uniform_chance, scr_acc, scramble_delta,
           collapsed, struct_gap, same_c, diff_c, arms["HD_value_only"]["test_acc"],
           arms["HD_fixed_global"]["test_acc"],
           abs(arms["HD_fixed_global"]["test_acc"] - rec_acc) < 0.05,
           pos_rec["exact_level_acc"], pos_rec["chance_level_acc"], verdict))

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "image->HD encoder on load_digits: %s" % verdict,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "run_mode": mode,
        "config": {"N": N, "Q": Q, "n_pos": n_pos, "n_classes": n_classes,
                   "n_train": int(X_tr.shape[0]), "n_test": int(X_te.shape[0]),
                   "temp": temp, "test_size": 0.3, "split_seed": 0, "encoder_seed": 0},
        "arms": {
            "HD_record": {"test_acc": rec_acc},
            "HD_scramble": {"test_acc": scr_acc},
            "HD_value_only": {"test_acc": arms["HD_value_only"]["test_acc"]},
            "HD_fixed_global": {"test_acc": arms["HD_fixed_global"]["test_acc"]},
        },
        "baselines": {
            "pixel_knn_k3": pixel_knn_acc,
            "pixel_linear_logreg": pixel_linear_acc,
            "uniform_chance": uniform_chance,
            "majority_class_chance": majority_chance,
        },
        "structure": {
            "same_class_cosine": same_c,
            "diff_class_cosine": diff_c,
            "struct_gap": struct_gap,
            "position_recovery": pos_rec,
        },
        "witnesses": {
            "iterative_cleanup_acc": rec_acc,
            "argmax_cleanup_acc": argmax_acc,
            "fixed_global_isomorphism_ok": bool(abs(arms["HD_fixed_global"]["test_acc"] - rec_acc) < 0.05),
        },
        "discriminator": {
            "scramble_delta": scramble_delta,
            "collapsed": bool(collapsed),
            "well_above_chance": bool(well_above_chance),
            "structure_ok": bool(structure_ok),
        },
        "bands": {
            "PASS_RECORD_MIN": PASS_RECORD_MIN,
            "SCRAMBLE_COLLAPSE_MAX": SCRAMBLE_COLLAPSE_MAX,
            "SCRAMBLE_DELTA_MIN": SCRAMBLE_DELTA_MIN,
            "STRUCT_GAP_MIN": STRUCT_GAP_MIN,
        },
        "arms_differ_verified": True,
        "arm_digests": arm_digests,
        "final_metrics_atomicity": "tmp_replace",
        "primitives_reused": ["hdlab.binding.bsc_bind", "hdlab.binding.bsc_bundle",
                              "hdlab.iterative_attractor.iterative_cleanup",
                              "hdlab.iterative_attractor.argmax_cleanup"],
        "recipe_adopted": "Kanerva record-based position-value + Rahimi/Kleyko thermometer level code",
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
