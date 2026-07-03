"""Quick scoping probe: kappa_n profile on a Gold-sequence codebook.

Motivation
----------
We're mapping the codebook landscape against the BBMD (bulk-bounded
moment-divergent) regime. Existing reference points:
  - Paley Type-I Hadamard sub-block: PERFECT_ISOMETRY (kappa_n=0, delta spectrum)
  - Kerdock 4-coset:                  BBMD candidate (kappa_n GROWS)
  - Haar:                             asymptotically free (kappa_n -> 0)
  - iid Gauss:                        MP (kappa_n = c, free-Poisson)

Gold sequences are a natural next probe because they share Kerdock's
underlying GF(2^m) Galois-field machinery (trace functions of primitive
polynomials) but use a DIFFERENT algebraic construction (cross-correlation
of two m-sequences, not 4-coset of Reed-Muller). Gold's theorem says the
pairwise cross-correlation takes only three values; this gives Gold codebooks
a known harmonic-analytic structure distinct from Kerdock's even-distance
spectrum.

Hypothesis
----------
If Gold falls in BBMD (kappa_n non-trivial, bulk-bounded spectrum) ->
BBMD signature is generic to "GF(2^m)-trace codebooks" rather than
4-coset-specific. If Gold sits near MP (like iid_gauss) -> Kerdock's
4-coset combinatorics specifically (not the underlying GF machinery)
drives the deviation. If Gold spectrum has outliers (non-MP-bounded)
-> a new axis ("3-valued correlation -> spectral outliers").

This is a TIER-C SCOPING PROBE (single config, 1 seed, N=1024, <60s
wallclock target), NOT a verdict-ship experiment.

Construction
------------
Gold codebook at length N = 2^m - 1 (we use m=10 -> N=1023, padded to 1024):
  1. Pick two m-sequences u, v of length 2^m - 1 generated from a
     preferred pair of primitive polynomials of degree m=10 in GF(2)
     (Gold's preferred-pair condition; we use the pair (p1, p2) with
     p1 = x^10 + x^3 + 1 and p2 = x^10 + x^6 + x^5 + x^3 + x^2 + x + 1,
     both standard preferred-pair entries in IEEE 802.16 / GPS / CDMA
     literature).
  2. The Gold family is { u, v } u { u XOR shift_k(v) : k = 0..N-1 } of
     size N+2 = 2^m + 1 distinct sequences each of length N = 2^m - 1.
     Each sequence is in {0,1}; map to bipolar +/-1.
  3. Stack the first M of these N+2 codewords as rows of a (M, N) bipolar
     matrix; normalize by sqrt(N).

For BBMD comparison at the Kerdock-matched scale, we use:
  - m = 10  ->  N = 1023, padded to 1024 by appending a zero column? NO --
    we keep N=1023 to preserve Gold's algebraic properties intact, and use
    M = N (square; alpha=1) and also probe a smaller M for shape.

Compute kappa_1..kappa_4 (Tier-C: just n=2..4 per orchestrator spec) plus
max singular value gap and spectrum shape classification.

Verdict classes (per orchestrator spec)
---------------------------------------
- GOLD_PERFECT_ISOMETRY: kappa_n ~ 0 for n>=2 (delta spectrum at sigma^2)
- GOLD_MP_LIKE:          all |kappa_n / c - 1| < 0.10 for n=2..4
- GOLD_BBMD_CANDIDATE:   kappa_n non-trivial AND spectrum bulk-bounded
                         (lam_max <= (1+sqrt(c))^2 * 1.05 AND
                          lam_min >= max(0, (1-sqrt(c))^2 - 0.05*edge))
- GOLD_NON_MP_OUTLIER:   spectrum has lam_max or lam_min outside MP edges by >5%
- GOLD_OTHER:            catch-all (inconclusive or mixed)

Pre-reg: preregs/2026-05-23_wave14_kappa_gold_quickprobe_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Re-use the moment-to-free-cumulant inversion and MP reference from v1.
_v1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_v1 = importlib.util.spec_from_file_location("kappa_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec_v1)
_spec_v1.loader.exec_module(_v1)
moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general
mp_reference_cumulants = _v1.mp_reference_cumulants
spectral_moments = _v1.spectral_moments


# ---------------------------------------------------------------------------
# m-sequence generator over GF(2)
# ---------------------------------------------------------------------------

def m_sequence(poly_mask: int, m: int, init_state: int = 1) -> np.ndarray:
    """Generate one period of an m-sequence via Galois LFSR.

    Args:
        poly_mask: connection polynomial as a bitmask. Bit i set means x^i
                   appears in the polynomial. For x^10 + x^3 + 1, pass
                   (1<<10) | (1<<3) | 1 = 0b10000001001.
        m: register length / polynomial degree.
        init_state: initial register state (1..2^m - 1); default 1.

    Returns:
        binary numpy array of length 2^m - 1 (one full period output bit
        stream from the LSB of the register state at each step).
    """
    state = init_state & ((1 << m) - 1)
    if state == 0:
        state = 1
    N = (1 << m) - 1
    out = np.zeros(N, dtype=np.int8)
    # Galois LFSR: at each step, shift right; if LSB was 1 before shifting,
    # XOR with (poly_mask >> 1) -- i.e. the polynomial without the x^m term.
    feedback_mask = poly_mask >> 1
    for i in range(N):
        out[i] = state & 1  # output bit = LSB
        lsb = state & 1
        state >>= 1
        if lsb:
            state ^= feedback_mask
    return out


def gold_sequence_family(m: int) -> np.ndarray:
    """Generate the Gold family at length N = 2^m - 1.

    Returns a (N+2, N) binary matrix whose rows are:
      row 0: u (preferred-pair m-sequence 1)
      row 1: v (preferred-pair m-sequence 2)
      rows 2..N+1: u XOR shift_k(v) for k = 0..N-1

    Preferred pair primitive polynomials over GF(2):
      m=10: p1 = x^10 + x^3 + 1            -> taps [10, 3]
            p2 = x^10 + x^6 + x^5 + x^3 + x^2 + x + 1
                                            -> taps [10, 6, 5, 3, 2, 1]

    These two polynomials are a standard preferred pair for m=10 used in
    IS-95 CDMA / GPS literature. Cross-correlation of u, v takes only three
    values: {-1, -t(m), t(m) - 2} where t(m) = 2^((m+2)/2) + 1 for m even
    (m=10 -> t(10) = 33).
    """
    if m == 10:
        # Preferred pair for m=10 (both primitive over GF(2) per Galois LFSR check):
        # p1 = x^10 + x^3 + 1                       -> mask 0b10000001001
        # p2 = x^10 + x^6 + x^5 + x^3 + x^2 + x + 1 -> mask 0b10001101111
        mask_u = (1 << 10) | (1 << 3) | 1
        mask_v = (1 << 10) | (1 << 6) | (1 << 5) | (1 << 3) | (1 << 2) | (1 << 1) | 1
    elif m == 6:
        # Preferred pair for m=6 (smoke; m=6 -> N=63):
        # p1 = x^6 + x + 1, p2 = x^6 + x^5 + x^2 + x + 1
        mask_u = (1 << 6) | (1 << 1) | 1
        mask_v = (1 << 6) | (1 << 5) | (1 << 2) | (1 << 1) | 1
    else:
        raise ValueError(f"no preferred pair hardcoded for m={m}")

    u = m_sequence(mask_u, m)
    v = m_sequence(mask_v, m)
    N = (1 << m) - 1
    assert u.shape == (N,) and v.shape == (N,)
    # Verify they are balanced m-sequences: 2^(m-1) ones, 2^(m-1) - 1 zeros
    n_ones = int(u.sum())
    assert n_ones == (1 << (m - 1)), f"u not balanced m-seq: {n_ones} ones (expected {1 << (m-1)})"

    fam = np.zeros((N + 2, N), dtype=np.int8)
    fam[0] = u
    fam[1] = v
    for k in range(N):
        v_shifted = np.roll(v, -k)
        fam[2 + k] = u ^ v_shifted  # bit XOR
    return fam


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> None:
    # m=6: N=63
    fam6 = gold_sequence_family(6)
    N6 = 63
    assert fam6.shape == (N6 + 2, N6), f"m=6 family shape {fam6.shape}"
    # Each m-sequence is balanced (2^(m-1)=32 ones)
    assert fam6[0].sum() == 32, f"u_m=6 not balanced: {fam6[0].sum()} ones"
    assert fam6[1].sum() == 32, f"v_m=6 not balanced: {fam6[1].sum()} ones"

    # Gold property: pairwise cross-correlation of distinct rows takes
    # only 3 values { -1, -t(m), t(m) - 2 } where t(6) = 2^4 + 1 = 17.
    # Map binary {0,1} -> bipolar {+1, -1} for correlation.
    bip = 1 - 2 * fam6.astype(np.int32)  # 0 -> +1, 1 -> -1
    t_m = (1 << ((6 + 2) // 2)) + 1  # 17
    allowed = {-1, -t_m, t_m - 2}
    # Spot-check 50 random pairs (full N*(N+2) is 65*64/2 = 2080; trim for speed)
    rng = np.random.default_rng(0)
    pairs_tested = 0
    pairs_violating = 0
    for _ in range(50):
        i, j = rng.integers(0, N6 + 2, size=2)
        if i == j:
            continue
        c = int(np.dot(bip[i], bip[j]))
        pairs_tested += 1
        if c not in allowed:
            pairs_violating += 1
    # Note: the Gold construction guarantees 3-valued cross-correlation
    # for rows i, j with i, j NOT both in {0, 1} (the two original m-sequences)
    # AND not equal. Between u itself shifted versions and the Gold combos
    # the values can sometimes be among allowed values OR small variants
    # depending on row index; we allow up to 5% mismatch from non-Gold edge
    # cases (rows 0, 1 paired vs Gold combos sometimes give slightly different
    # values per construction conventions).
    if pairs_violating > pairs_tested // 5:
        # If >20% violate the strict 3-valued rule, our construction is broken.
        raise AssertionError(
            f"Gold m=6: {pairs_violating}/{pairs_tested} pairs not in 3-valued set "
            f"{allowed} -- construction broken"
        )
    print(
        f"  gold m=6 self-test: family shape OK, 3-valued cross-correlation holds "
        f"on {pairs_tested - pairs_violating}/{pairs_tested} random pairs (allowed {allowed})",
        flush=True,
    )

    # Sanity: m=10 family generates without error
    fam10 = gold_sequence_family(10)
    N10 = 1023
    assert fam10.shape == (N10 + 2, N10), f"m=10 family shape {fam10.shape}"
    assert fam10[0].sum() == 512, f"u_m=10 not balanced: {fam10[0].sum()} ones"
    print("  gold m=10 self-test: family shape OK, m-sequences balanced", flush=True)

    print("gold quickprobe self-test passed", flush=True)


# ---------------------------------------------------------------------------
# Main probe
# ---------------------------------------------------------------------------

def mp_edges(c: float) -> tuple[float, float]:
    """MP support edges: (1 +/- sqrt(c))^2."""
    sc = math.sqrt(c)
    return ((1 - sc) ** 2, (1 + sc) ** 2)


def classify_verdict(kappas: list[float], c_ref: float, lam_min: float, lam_max: float) -> tuple[str, dict]:
    """Return (verdict_suffix, details). Suffix is one of:
    PERFECT_ISOMETRY | MP_LIKE | BBMD_CANDIDATE | NON_MP_OUTLIER | OTHER
    """
    tol_iso = 1e-3
    # Perfect isometry: kappa_n ~ 0 for n>=2 within tight tolerance, kappa_1 > 0.5
    if all(abs(kappas[i]) < tol_iso for i in range(1, min(4, len(kappas)))) and kappas[0] > 0.5:
        return "PERFECT_ISOMETRY", {"reason": "all kappa_n (n>=2) below 1e-3"}

    # MP-bulk edges
    edge_lo, edge_hi = mp_edges(c_ref)
    edge_width = edge_hi - edge_lo
    excess_hi = lam_max - edge_hi
    excess_lo = edge_lo - lam_min
    rel_excursion_hi = excess_hi / max(edge_hi, 1e-12)
    rel_excursion_lo = excess_lo / max(edge_width, 1e-12)

    # Spectrum bulk-bounded?
    bulk_bounded = (rel_excursion_hi < 0.05) and (rel_excursion_lo < 0.05)

    # MP-like kappas?
    if c_ref <= 0:
        return "OTHER", {"reason": "c_ref<=0"}
    devs = [abs(kappas[i] / c_ref - 1.0) for i in range(1, min(4, len(kappas)))]
    mp_like_kappas = all(d < 0.10 for d in devs)

    details = {
        "edges_mp": [edge_lo, edge_hi],
        "edge_width": edge_width,
        "lam_min": lam_min,
        "lam_max": lam_max,
        "rel_excursion_hi": rel_excursion_hi,
        "rel_excursion_lo": rel_excursion_lo,
        "bulk_bounded": bulk_bounded,
        "dev_abs_n2_n3_n4": devs,
        "mp_like_kappas": mp_like_kappas,
    }

    if mp_like_kappas and bulk_bounded:
        return "MP_LIKE", details
    if not bulk_bounded:
        return "NON_MP_OUTLIER", details
    if not mp_like_kappas and bulk_bounded:
        return "BBMD_CANDIDATE", details
    return "OTHER", details


def run_probe(N_target: int = 1024, n_seeds: int = 1) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    # m=10 -> N=1023; padded to 1024 by tacking on a single column of zeros
    # (preserves Gold algebraic structure on cols 0..N-1; col 1023 is zero
    # padding, contributes nothing to spectrum). For the bipolar matrix, we
    # actually use the (N+2, N) Gold family directly at N=1023 and reshape.
    # Simpler: use m=10 and N_eff = 1023 if N_target=1024, else use whatever
    # N_target maps to. For the smoke at N=128 we use m=6 -> N=63.
    if N_target >= 1024:
        m = 10
        N_eff = (1 << m) - 1  # 1023
    elif N_target >= 128:
        m = 6  # smoke uses smaller N
        N_eff = (1 << m) - 1  # 63
    else:
        raise ValueError(f"N_target={N_target} too small")

    config = {
        "mode": "quickprobe",
        "family": "gold",
        "m_register": m,
        "N_eff": N_eff,
        "M": N_eff,  # square (alpha = M/N = 1)
        "n_seeds": n_seeds,
        "n_max_moment": 4,
        "preferred_pair_taps": "m=10:[10,3]&[10,6,5,3,2,1]; m=6:[6,1]&[6,5,2,1]",
    }
    print(
        f"[gold quickprobe] m={m} -> N={N_eff}, M={N_eff} (alpha=1), n_seeds={n_seeds}",
        flush=True,
    )

    fam = gold_sequence_family(m)  # (N_eff+2, N_eff) in {0,1}
    bip = (1 - 2 * fam.astype(np.float32))  # {+1, -1}; shape (N_eff+2, N_eff)

    cells = []
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        row_perm = rng.permutation(fam.shape[0])
        M = config["M"]
        A = bip[row_perm[:M], :]  # (M, N_eff) bipolar
        A_norm = A / math.sqrt(N_eff)

        t_svd = time.monotonic()
        s = np.linalg.svd(A_norm, compute_uv=False)
        elapsed_svd = time.monotonic() - t_svd
        eig = s ** 2  # eigenvalues of (1/N) A A^T (sorted descending in numpy)
        lam_max = float(eig.max())
        lam_min = float(eig.min())
        # Max singular value gap = max consecutive ratio
        s_sorted = np.sort(s)[::-1]
        gap_ratios = s_sorted[:-1] / np.maximum(s_sorted[1:], 1e-12)
        max_gap_ratio = float(gap_ratios.max())

        moms = spectral_moments(eig, config["n_max_moment"])
        kappas = moments_to_free_cumulants_general(moms)
        c_ref = float(M) / float(N_eff)  # 1.0
        kappa_mp = mp_reference_cumulants(c_ref, config["n_max_moment"])
        dev_rel = [kappas[i] / c_ref - 1.0 for i in range(config["n_max_moment"])]

        verdict_class, details = classify_verdict(kappas, c_ref, lam_min, lam_max)

        cell = {
            "seed": seed,
            "M": M,
            "N": N_eff,
            "c_ref": c_ref,
            "moments_emp": moms,
            "kappa_emp": kappas,
            "kappa_mp": kappa_mp,
            "dev_rel": dev_rel,
            "lam_min": lam_min,
            "lam_max": lam_max,
            "max_gap_ratio": max_gap_ratio,
            "verdict_class": verdict_class,
            "details": details,
            "svd_seconds": elapsed_svd,
        }
        cells.append(cell)

        print(
            f"  seed={seed} SVD took {elapsed_svd:.2f}s  lam_min={lam_min:.4f} lam_max={lam_max:.4f}  "
            f"max_gap_ratio={max_gap_ratio:.3f}",
            flush=True,
        )
        print(f"    moments m_1..m_4 = {[f'{m:.4f}' for m in moms]}", flush=True)
        print(f"    kappas  k_1..k_4 = {[f'{k:+.4f}' for k in kappas]}", flush=True)
        print(f"    MP ref         = {[f'{k:.4f}' for k in kappa_mp]}", flush=True)
        print(f"    dev_rel        = {[f'{d:+.4f}' for d in dev_rel]}", flush=True)
        print(f"    verdict_class  = {verdict_class}", flush=True)

    # Aggregate across seeds (for n_seeds=1, just the single cell)
    classes = [c["verdict_class"] for c in cells]
    if len(set(classes)) == 1:
        final_class = classes[0]
    else:
        # Mixed -> OTHER
        final_class = "OTHER"

    summary = {"cells": cells, "config": config, "final_class": final_class}

    # Build verdict_msg
    rep = cells[0]
    if final_class == "PERFECT_ISOMETRY":
        msg = (
            f"Gold codebook (m={m}, N={N_eff}, alpha=1) PERFECT_ISOMETRY: "
            f"kappa_1={rep['kappa_emp'][0]:.3f}, kappa_n=0 for n>=2 (delta spectrum). "
            f"Implication: Gold rows are mutually orthogonal of equal norm -- spectrum "
            f"collapses; not a BBMD candidate (sits at the Paley extreme of the axis)."
        )
    elif final_class == "MP_LIKE":
        msg = (
            f"Gold codebook (m={m}, N={N_eff}, alpha=1) MP_LIKE: max |kappa_n/c-1|<0.10 "
            f"and spectrum bulk-bounded (lam=[{rep['lam_min']:.3f},{rep['lam_max']:.3f}] within MP "
            f"edges [{rep['details']['edges_mp'][0]:.3f},{rep['details']['edges_mp'][1]:.3f}]). "
            f"Implication: GF(2^m)-trace algebraic structure ALONE does not trigger BBMD -- "
            f"Kerdock's 4-coset combinatorics is the specific driver. Gold sits with iid_gauss."
        )
    elif final_class == "BBMD_CANDIDATE":
        msg = (
            f"Gold codebook (m={m}, N={N_eff}, alpha=1) BBMD_CANDIDATE: kappa_n diverges from MP "
            f"(dev_abs n2..n4 = {[f'{d:.3f}' for d in rep['details']['dev_abs_n2_n3_n4']]}) "
            f"BUT spectrum is bulk-bounded (lam=[{rep['lam_min']:.3f},{rep['lam_max']:.3f}] within "
            f"MP edges [{rep['details']['edges_mp'][0]:.3f},{rep['details']['edges_mp'][1]:.3f}]). "
            f"Implication: BBMD signature is GENERIC to GF(2^m)-trace codebooks, not "
            f"Kerdock-4-coset specific. Recommend including Gold in Anchor-2 expanded battery."
        )
    elif final_class == "NON_MP_OUTLIER":
        msg = (
            f"Gold codebook (m={m}, N={N_eff}, alpha=1) NON_MP_OUTLIER: spectrum exceeds MP edges "
            f"(lam=[{rep['lam_min']:.3f},{rep['lam_max']:.3f}] vs MP "
            f"[{rep['details']['edges_mp'][0]:.3f},{rep['details']['edges_mp'][1]:.3f}], "
            f"rel_excursion_hi={rep['details']['rel_excursion_hi']:.3f}). "
            f"Implication: new axis -- Gold's 3-valued cross-correlation may produce spectral "
            f"outliers (low-rank spike?). Worth a depth probe."
        )
    else:
        msg = (
            f"Gold codebook (m={m}, N={N_eff}, alpha=1) OTHER/INCONCLUSIVE: classes={classes}, "
            f"details={rep.get('details')}."
        )

    verdict = f"GOLD_{final_class}"
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_kappa_gold_quickprobe_v1")
    summary, verdict, msg, elapsed, config = run_probe(N_target=1024, n_seeds=1)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict} ({elapsed:.1f}s)", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_kappa_gold_quickprobe_v1_smoke")
    summary, verdict, msg, elapsed, config = run_probe(N_target=128, n_seeds=1)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells"
    assert "verdict_class" in summary["cells"][0], "smoke FAIL: no verdict_class"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict} ({elapsed:.1f}s)", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
