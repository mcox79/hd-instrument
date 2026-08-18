"""Does this metric move at all under a NULL input? Run this before a ceiling score is believed.

Promoted from scratch/_iam_saturation.py (2026-08-15,
.claude/scan-out/identical-across-models.json, GROUP_f9db26aa72937aec). Incident: five cells
named for five different models (pythia-160m/1.4b/2.8b, qwen2.5-1.5b) all reported
recall@1 = 1.0000, bit-identical. The instinct "different models can't produce identical
floats" does not apply here because the ONLY per-run quantity metrics.json ever wrote was a
SATURATED INTEGER RATIO (2000/2000) plus two config constants -- never a model identity, never
anything that could register a difference below the ceiling. The agent's own negative control
proved the ceiling is reachable with NO MODEL AT ALL: iid Gaussian keys, at all 4 real
hidden-state dims, at both NOISE values used, still score 1.0000. "1.000 was reachable by
random numbers, and nobody had ever checked." That is the point of this module: check, BEFORE
trusting a ceiling score as evidence the thing under test works.

Relationship to tools/skunkworks_saturation_canfail_check_v1.py: that tool is a STATIC
detector -- it flags CANDIDATE saturation from the SHAPE of an already-written metrics.json
(pinned at an extreme, zero spread, no cliff reached). This module is the thing that actually
ANSWERS the question that flags: it EXECUTES the metric's own arithmetic against synthetic
null input and reports whether the ceiling is reached without the thing under test. Use the
static tool to triage a backlog of landed results; use this one to settle a specific PASS
before cert-grading it.

THE REUSABLE PIPELINE. Several cells in this repo (the five-model group above, and others
sharing its template) score retrieval with the SAME construction: whiten a key matrix K,
L2-normalise, corrupt a query with additive Gaussian noise, whiten+normalise the query the same
way, and take argmax cosine similarity as the prediction. `nn_recall_at_1` below is a verbatim
transcription of that block (verified against experiments/exp_n1c_qwen1p5b_substrate_kv_gpu_v1.py
lines 84-91) so a null-input run of it is testing the SAME arithmetic the real cells ran, not a
lookalike.

Usage:
    .venv/Scripts/python.exe tools/saturation_negative_control.py --self-test
    .venv/Scripts/python.exe tools/saturation_negative_control.py --dims 768,1536,2048,2560 \\
        --noise 0.1,0.3 --M 2000
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np


def nn_recall_at_1(K, noise, seed=7):
    """Verbatim transcription of the cell's whiten+recall block (recall@1 nearest-neighbour
    retrieval of a noise-corrupted query against its own whitened key). Returns a float in
    [0, 1]. This is a PURE function of K and noise -- pass synthetic K (e.g. iid_gaussian_keys
    below) to run it as a negative control with no model anywhere in the path."""
    g = np.random.default_rng(seed)
    K = K.astype(np.float32)
    mu = K.mean(0)
    Kc = K - mu
    cov = Kc.T @ Kc / len(K) + 1e-3 * np.eye(K.shape[1])
    w, V = np.linalg.eigh(cov)
    W = V @ np.diag(1.0 / np.sqrt(w)) @ V.T
    Kw = Kc @ W
    Kw = Kw / (np.linalg.norm(Kw, axis=1, keepdims=True) + 1e-8)
    Q = K + noise * g.standard_normal(K.shape).astype(np.float32)
    Qw = (Q - mu) @ W
    Qw = Qw / (np.linalg.norm(Qw, axis=1, keepdims=True) + 1e-8)
    pred = np.argmax(Qw @ Kw.T, axis=1)
    gold = np.arange(len(K))
    return float((pred == gold).mean())


def iid_gaussian_keys(M, d, seed):
    """The null input: M keys of dimension d, no model, no structure -- iid standard normal."""
    rng = np.random.default_rng(seed)
    return rng.standard_normal((M, d)).astype(np.float32)


def negative_control_report(dims, noise_values, M=2000, seed=11, pipeline=nn_recall_at_1):
    """Run `pipeline` on iid Gaussian keys (NO model, NO real data) across every (dim, noise)
    combination. Returns {(d, noise): recall}. If ANY value reaches 1.0, the metric is reachable
    by random numbers under that configuration -- a same-scored real result is UNINFORMATIVE
    (not necessarily wrong) unless something else in the record distinguishes it from this null."""
    out = {}
    for d in dims:
        K = iid_gaussian_keys(M, d, seed)
        for nz in noise_values:
            out[(d, nz)] = pipeline(K, nz)
    return out


def first_noise_that_moves_it(d, M=2000, seed=11, start=0.1, growth=3.0, max_steps=12,
                                pipeline=nn_recall_at_1):
    """How hard do you have to corrupt the query before the metric drops off 1.0? Returns
    (noise, recall) for the first tested noise where recall < 1.0, or (None, None) if it never
    moves within max_steps geometric growth steps from `start`."""
    K = iid_gaussian_keys(M, d, seed)
    nz = start
    for _ in range(max_steps):
        r = pipeline(K, nz)
        if r < 1.0:
            return nz, r
        nz *= growth
    return None, None


def _selftest():
    # POSITIVE: well-separated keys, tiny noise -> recall must be 1.0 (the pipeline itself works).
    rng = np.random.default_rng(0)
    Kpos = rng.standard_normal((200, 128)) * 5.0
    rp = nn_recall_at_1(Kpos, 0.01)
    assert rp == 1.0, "known-positive FAILED: %r" % rp

    # NEGATIVE 1: 100 duplicated key pairs -- retrieval MUST break (ambiguous nearest neighbour).
    base = rng.standard_normal((100, 128))
    Kneg = np.repeat(base, 2, axis=0)
    rn = nn_recall_at_1(Kneg, 0.5)
    assert rn < 0.9, "known-negative (duplicated keys) FAILED to break: %r" % rn

    # NEGATIVE 2: overwhelming noise must break it regardless of key structure.
    rn2 = nn_recall_at_1(rng.standard_normal((200, 128)), 500.0)
    assert rn2 < 0.9, "known-negative (huge noise) FAILED to break: %r" % rn2

    print("nn_recall_at_1 selftest: 3/3 PASS (1 positive, 2 negatives) "
          "pos=%.3f dup=%.3f hugenoise=%.3f" % (rp, rn, rn2))

    # Reproduce the actual incident finding as a regression guard: at real hidden-state dims,
    # NOISE=0.10 (used by 4 of 5 real cells) and NOISE=0.30 (the "robustness" arm) both saturate
    # under a pure null input. If this ever stops reproducing 1.0, either numpy's RNG/eigh
    # changed behaviour or this transcription has drifted from the source cell -- investigate,
    # don't just update the assertion.
    report = negative_control_report(dims=[768, 1536, 2048, 2560], noise_values=[0.10, 0.30])
    for (d, nz), r in report.items():
        assert r == 1.0, ("regression: null-input recall no longer saturates at d=%d noise=%s "
                           "(got %r) -- re-verify the incident finding" % (d, nz, r))
    print("regression guard (real dims x {0.10, 0.30}) PASS: all %d combinations reach 1.0000 "
          "under a null (no-model) input -- reproduces the incident finding" % len(report))

    # The metric SHOULD move eventually -- prove first_noise_that_moves_it is not a tautology
    # that always returns None.
    nz, r = first_noise_that_moves_it(2048, start=0.1, growth=3.0, max_steps=6)
    assert nz is not None and r is not None and r < 1.0, (
        "first_noise_that_moves_it found no drop-off within range -- helper may be broken")
    print("first_noise_that_moves_it(d=2048): metric first drops below 1.0 at NOISE=%.3g -> %.4f"
          % (nz, r))

    print("\nsaturation_negative_control selftest: ALL PASS")


def _cli():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--dims", default="768,1536,2048,2560")
    ap.add_argument("--noise", default="0.1,0.3")
    ap.add_argument("--M", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    if args.self_test:
        _selftest()
        return

    dims = [int(x) for x in args.dims.split(",")]
    noises = [float(x) for x in args.noise.split(",")]
    report = negative_control_report(dims, noises, M=args.M, seed=args.seed)
    print("=== negative control: recall@1 with NO MODEL IN THE PATH, M=%d ===" % args.M)
    print("%8s %8s %10s" % ("dim", "noise", "recall"))
    for (d, nz), r in report.items():
        flag = "  <-- SATURATES UNDER NULL INPUT" if r >= 0.999 else ""
        print("%8d %8.3g %10.4f%s" % (d, nz, r, flag))
    if any(r >= 0.999 for r in report.values()):
        print("\nWARNING: at least one configuration reaches the ceiling with NO real signal. "
              "A real result at this ceiling is UNINFORMATIVE about model/key quality unless "
              "something else in the record distinguishes it from this null.")


if __name__ == "__main__":
    _cli()
