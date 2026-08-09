"""hdlab/dg_pattern_separation.py -- DG (dentate gyrus) pattern-separation
primitive (2026-08-09), the diagnosed fix for the MCScript2.0
script_grain_acquisition_loop CA3-only over-merge (exp_mcscript2_real_
benchmark_validation_v1, HARD_FAIL, commit 5c1199f87): that cell's keying
step (hdlab.script_grain_acquisition_loop.ScriptLibrary.match_or_spawn) calls
hdlab.cleanup_family.iterative_attractor, a CA3 pattern-COMPLETION mechanism
(soft-attractor settle toward the nearest stored bundled prototype), with NO
upstream pattern-SEPARATION stage. At 195-way scenario cardinality (MCScript2.0
train), similar-but-distinct bag-of-content-words registers collapse into a
handful of catch-all attractor basins whose bundled prototypes keep "blurring"
toward a generic direction as more (wrongly-merged) traces accumulate --
MEASURED@data/exp_mcscript2_real_benchmark_validation_v1/metrics.json:
n_items_spawned_total=35, only 33 reach GROUNDED, mean item_purity ~0.19-0.20
(catch-all buckets; compounding curve DEGRADES with exposure, real_final=0.5538
< baseline 0.5859).

MECHANISM (brain-canonical, causal evidence not just correlational):
  - Leutgeb et al. 2007 Science: DG rate-remapping decorrelates similar
    contexts far more than downstream CA3/CA1 -- DG is the separation stage,
    CA3 is the completion stage, they are NOT the same computation.
  - Guzman et al. 2016 Science: optogenetic silencing of DG granule cells
    impairs behavioral discrimination of similar (but not dissimilar)
    contexts -- causal, not just correlational.
  - McHugh et al. 2007 Science: DG-specific NMDAR knockout mice fail
    pattern-separation behaviorally while CA3 pattern-completion stays intact
    -- a genuine double dissociation.
  - Mechanistically, DG achieves separation via (1) a large sparse EC-II ->
    DG EXPANSION (mossy-fiber divergence; rat EC-II ~200k cells -> DG granule
    cells ~1M, roughly 5x; human estimates larger) and (2) very sparse
    lateral-inhibition-driven ACTIVITY (population sparsity ~1-4% of granule
    cells active per input; Jung & McNaughton 1993; Chawla et al. 2005).
  - A random high-dimensional EXPAND-then-k-winner-take-all code is the
    standard computational-neuroscience / VSA proxy for this expansion-
    recoding model (Marr 1969 cerebellar-cortex expansion-recoding; Albus
    1971; Bogacz & Brown 2003 DG expansion-recoding model; Kanerva 2010
    sparse-distributed-memory framing). Sparse high-dimensional codes also
    have a well-established HIGHER associative-memory storage capacity before
    crosstalk-driven collapse than dense codes (Willshaw et al. 1969;
    Buckingham & Willshaw 1993; Treves & Rolls 1991 sparsity-vs-capacity
    scaling) -- this is the THEORETICAL reason DG-style sparsification should
    specifically help the observed "bundled-prototype blur compounds with
    exposure" failure mode, not merely the single-pair cosine gap: bundling
    many SPARSE near-orthogonal member codes crosstalks far less than
    bundling many DENSE correlated ones.

THIS IS THE DG STAGE ONLY. It does NOT replace CA3 completion
(hdlab.cleanup_family.iterative_attractor / ScriptLibrary.match_or_spawn,
unchanged, reused verbatim downstream of this transform) -- it transforms the
INPUT KEY so completion operates on an already-decorrelated code, mirroring
the brain's EC -> DG -> CA3 (perforant path -> mossy fiber) pathway, not a
competing pattern-completion mechanism. Callers wrap the output exactly like
hdlab.script_grain_acquisition_loop.content_phase_vec / the mcscript cell's
bow_register (a zero-imaginary complex64 FHRR register) so it plugs into
ScriptLibrary.match_or_spawn / calibrate_novelty_threshold / _real2d with ZERO
modification to those modules.

Deterministic (hashlib-seeded projection matrix + RNG throughout, PROT-023/F.5
compliant -- no built-in hash(), no list(set()) ordering). ASCII-only.
"""
from __future__ import annotations

import hashlib
from typing import Optional

import numpy as np


def _seeded_rng(tag: str) -> np.random.Generator:
    """Deterministic numpy Generator seeded via hashlib (PROT-023/F.5 -- never
    Python's built-in salted hash())."""
    seed = int.from_bytes(hashlib.sha256(tag.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
    return np.random.default_rng(seed)


def projection_matrix(input_dim: int, expand_dim: int, proj_seed_tag: str) -> np.ndarray:
    """Fixed dense Gaussian random EXPANSION projection (EC-II -> DG mossy-
    fiber analog), scaled 1/sqrt(input_dim) (standard JL-embedding scaling).
    Deterministic given (input_dim, expand_dim, proj_seed_tag) -- callers
    should build this ONCE per run and pass it to dg_separate's `W` argument
    when calling in a tight per-instance loop (avoids re-deriving + reseeding
    a (expand_dim, input_dim) matrix on every call)."""
    rng = _seeded_rng(f"dg_projection::{proj_seed_tag}::{input_dim}->{expand_dim}")
    return (rng.standard_normal((expand_dim, input_dim)) / np.sqrt(input_dim)).astype(np.float32)


def dg_separate(x: np.ndarray, *, expand_dim: int, sparsity: float,
                proj_seed_tag: str = "default", W: Optional[np.ndarray] = None) -> np.ndarray:
    """DG pattern separation: fixed random EXPANSION projection
    (x: (input_dim,) -> y: (expand_dim,), expand_dim > input_dim) followed by
    k-winner-take-all SPARSIFICATION (keep the top round(sparsity*expand_dim)
    entries by |magnitude|, zero the rest), then L2-normalize.

    Args:
        x: (input_dim,) real vector (e.g. a bag-of-content-words bipolar
           register). Any real dtype; cast to float32 internally.
        expand_dim: output dimensionality; must exceed input_dim for this to
           be an EXPANSION (mossy-fiber-divergence analog).
        sparsity: fraction of expand_dim kept active, in (0, 1]. Biological DG
           granule-cell population sparsity is very low (~1-4%, Jung &
           McNaughton 1993 / Chawla et al. 2005); this parameter is the
           caller's pre-registered choice (see the mcscript purity cell for
           the specific value + citation-grounded rationale).
        proj_seed_tag: identity tag for the fixed random projection matrix
           (deterministic, hashlib-seeded). Use the SAME tag for every call in
           one run/arm so all vectors share one projection; a DIFFERENT tag
           produces an unrelated (but still deterministic) projection.
        W: optional precomputed projection matrix (from projection_matrix) --
           pass this in a tight per-instance loop to avoid rebuilding +
           reseeding W on every call (pure performance, no correctness
           difference from omitting it).

    Returns:
        (expand_dim,) float32 vector, exactly `round(sparsity*expand_dim)`
        nonzero entries (or all nonzero if that count >= expand_dim), L2-norm
        1.0 (or all-zero if the input was all-zero).
    """
    if expand_dim <= x.shape[-1]:
        raise ValueError(f"dg_separate: expand_dim={expand_dim} must exceed input_dim={x.shape[-1]} "
                         f"(this is an EXPANSION-then-sparsify stage, not a compression)")
    if not (0.0 < sparsity <= 1.0):
        raise ValueError(f"dg_separate: sparsity={sparsity} must be in (0, 1]")
    if W is None:
        W = projection_matrix(x.shape[-1], expand_dim, proj_seed_tag)
    y = W @ x.astype(np.float32)
    k = max(1, round(sparsity * expand_dim))
    if k < expand_dim:
        keep_idx = np.argpartition(np.abs(y), -k)[-k:]
        mask = np.zeros_like(y, dtype=bool)
        mask[keep_idx] = True
        y = np.where(mask, y, 0.0).astype(np.float32)
    n = float(np.linalg.norm(y) + 1e-9)
    return (y / n).astype(np.float32)


def _selftest() -> dict:
    """Off-disk gate exercising the REAL code path at tiny scale (per exp_dev
    SCHEMA-VET F.1): determinism, achieved sparsity, self-similarity, and the
    core DECORRELATION property (near-duplicate inputs must show LOWER cosine
    after DG separation than their raw cosine -- the defining signature of
    pattern separation, not just a random hash)."""
    d = 256
    expand = 1024
    sparsity = 0.05
    rng = np.random.default_rng(0)
    base = rng.choice([-1.0, 1.0], size=d).astype(np.float32)

    # (1) determinism: same input + same tag -> byte-identical output.
    a1 = dg_separate(base, expand_dim=expand, sparsity=sparsity, proj_seed_tag="t")
    a2 = dg_separate(base, expand_dim=expand, sparsity=sparsity, proj_seed_tag="t")
    assert np.array_equal(a1, a2), "dg_separate must be deterministic for a fixed (input, tag)"

    # (2) sparsity achieved exactly.
    k_expected = round(sparsity * expand)
    nnz = int(np.count_nonzero(a1))
    assert nnz == k_expected, f"expected {k_expected} nonzero entries, got {nnz}"

    # (3) self-similarity: identical input -> cos=1.0 after separation (sanity: not pure noise).
    cos_self = float(np.dot(a1, a1))
    assert abs(cos_self - 1.0) < 1e-4, f"self-cosine must be ~1.0, got {cos_self}"

    # (4) DECORRELATION signature: a near-duplicate input (90% sign overlap with base,
    # raw cosine ~0.80) must show a LOWER cosine after DG separation than its raw cosine
    # -- pattern separation pushes similar-but-distinct inputs further apart, it does not
    # just preserve or amplify their similarity (a plain random projection alone
    # approximately PRESERVES cosine per Johnson-Lindenstrauss; the kWTA nonlinearity is
    # what adds the decorrelating "sharpening" effect this asserts).
    near = base.copy()
    flip_idx = rng.choice(d, size=int(0.10 * d), replace=False)
    near[flip_idx] *= -1
    raw_cos = float(np.dot(base, near) / d)
    b1 = dg_separate(near, expand_dim=expand, sparsity=sparsity, proj_seed_tag="t")
    dg_cos = float(np.dot(a1, b1))
    assert dg_cos < raw_cos, (
        f"DG separation must decorrelate near-duplicate inputs: raw_cos={raw_cos:.4f} "
        f"dg_cos={dg_cos:.4f} (dg_cos must be strictly lower)")

    # (5) different proj_seed_tag -> different (deterministic) projection, not a global constant.
    c1 = dg_separate(base, expand_dim=expand, sparsity=sparsity, proj_seed_tag="other")
    assert not np.array_equal(a1, c1), "different proj_seed_tag must yield a different projection"

    # (6) precomputed W path matches the implicit-W path (performance path correctness).
    W = projection_matrix(d, expand, "t")
    a1_viaW = dg_separate(base, expand_dim=expand, sparsity=sparsity, proj_seed_tag="t", W=W)
    assert np.array_equal(a1, a1_viaW), "precomputed-W path must match implicit-W path exactly"

    # (7) all-zero input -> all-zero output (no div-by-zero crash).
    zero_out = dg_separate(np.zeros(d, dtype=np.float32), expand_dim=expand, sparsity=sparsity,
                           proj_seed_tag="t")
    assert np.all(zero_out == 0.0), "all-zero input must produce all-zero output, not NaN/crash"

    return {
        "deterministic": True, "sparsity_exact": {"expected": k_expected, "measured": nnz},
        "self_cosine": round(cos_self, 4),
        "decorrelation": {"raw_cos": round(raw_cos, 4), "dg_cos": round(dg_cos, 4)},
        "tag_sensitivity_ok": True, "precomputed_W_matches_ok": True, "zero_input_safe_ok": True,
    }


if __name__ == "__main__":
    import json
    result = _selftest()
    print(json.dumps(result, indent=2))
    print("[hdlab.dg_pattern_separation selftest] PASS: deterministic + exact-sparsity + "
          "self-similarity + decorrelation-signature + tag-sensitivity + W-path-parity + "
          "zero-input-safe", flush=True)
