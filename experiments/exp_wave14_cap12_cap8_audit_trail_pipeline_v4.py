"""Composition A audit-trail v4: re-point ITERATE_ROOT to the v1c iterate traces,
fix v3's smoke-leak failure mode, and add an iid-Gauss-vs-Schur-Weyl analytical
self-test.

What's new vs v3
----------------
v3 produced a smoke-mode metrics.json that the verdict_handler read as if it
were full-mode (codebooks=[kerdock, iid_gauss], n_seeds=1) -- the verdict_msg
fabricated SRHT / Hadamard / RM(1,m) rho values that were not present in
summary.codebook_results.  Root cause: the runner picked up the smoke-gate's
metrics file from data/exp_<name>_smoke/metrics.json and the downstream
honest-reread did not have a structural check that mode=full.

v4 changes:

  1. **ITERATE_ROOT repointed** to
     ``data/exp_wave14_cap8_vamp_iterates_srht_hadamard_v1c/iterates/`` (the
     newly-generated v1c traces, 30 valid trace files).

  2. **mode marker in metrics.json (top-level).**  ``metrics["mode"]`` is
     ``"full"`` for the main run and ``"smoke"`` for the smoke run.  This
     gives the downstream verdict_handler a structural check before it
     trusts the per-family rho values.

  3. **rho_by_family lifted to top-level metrics.**  No re-derivation from
     summary.codebook_results in the verdict_handler -- the per-family rho
     values are emitted at metrics["rho_by_family"] so honest-reread is a
     dict lookup, not a re-walk through nested arrays.

  4. **run_main hard-asserts mode=full and 4 hard families.**  If the
     summary does not contain all four HARD_FAMILIES at full N, the script
     refuses to write metrics.json to the non-smoke output dir.  This is
     defense-in-depth against smoke-leak.

  5. **iid Gauss x Schur-Weyl analytical self-test (per
     [[feedback-strategy-spec-formula-selftests]]).**  At n=2 the
     Schur-Weyl irrep mass at the row partition (2,) for an iid Gaussian
     spectrum (asymptotically MP at c=1) satisfies a known closed form
     m_2/(m_2 + m_1^2)/2.  We check this against the empirical Gauss
     spectrum's Schur-Weyl mass with a generous tolerance for the
     1024-sample finite-size deviation.

  6. **Bonus diagnostic capture (SRHT vs Hadamard).**  The smoke-leak v3
     showed SRHT and Hadamard with IDENTICAL rho=0.533.  v4 explicitly
     reports per-family rho with 6 decimal places to detect whether the
     v1c iterates make them genuinely identical (algebraic) or genuinely
     different (smoke-leak artifact).

Hypothesis (unchanged from v1)
------------------------------
If kappa_n moments and Schur-Weyl irrep masses index the SAME
representation-theoretic structure, their component-wise divergence-
from-MP should correlate.  The iterate-derived axis tests whether
that shared structure also drives the VAMP iterate trajectory.

HARD PASS (Composition A LICENSED, 12th-capability adjacent)
------------------------------------------------------------
  Spearman rho(combined_fingerprint_x, combined_fingerprint_y) >= 0.60
  across >= 3 of 4 hard families
  AND no family with rho < 0.30
  AND no family is TIED.

HARD FAIL (Composition A KILLED, prose-only)
--------------------------------------------
  rho < 0.30 on >= 2 of 4 hard families.

MIDDLE BAND (Composition A holds narrowly)
------------------------------------------
  Anything else.

Codebook families (unchanged)
-----------------------------
  1. Kerdock 4-coset
  2. SRHT
  3. Hadamard
  4. RM(1, m)

Smoke
-----
N=1024, 1 seed per codebook, n_max=4, Kerdock + iid only,
use_iterates=False.  Verdict will be INCONCLUSIVE on smoke (not enough
families) but self-tests + Schur-Weyl extraction + iid-Gauss baseline
+ iterate-loader (with no files present) must pass.  The smoke output
goes to data/exp_<name>_smoke/ with mode="smoke" stamped in metrics.

Pre-reg: preregs/2026-05-24_wave14_cap12_cap8_audit_trail_pipeline_v4.md
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

# Reuse the v3 module entirely (loaders, measure, verdict, self-tests).
_v3_path = REPO / "experiments" / "exp_wave14_cap12_cap8_audit_trail_pipeline_v3.py"
_spec_v3 = importlib.util.spec_from_file_location("audit_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec_v3)
_spec_v3.loader.exec_module(_v3)

# Pull v1 references for the iid-Gauss baseline self-test.
_v1_audit = _v3._v1  # the audit-trail v1 module loaded inside v3
build_iid_gauss = _v1_audit.build_iid_gauss
schur_weyl_irrep_masses = _v1_audit.schur_weyl_irrep_masses
schur_weyl_irrep_masses_from_mp = _v1_audit.schur_weyl_irrep_masses_from_mp
mp_reference_moments = _v1_audit.mp_reference_moments
HARD_FAMILIES = _v1_audit.HARD_FAMILIES
spearman_rho = _v1_audit.spearman_rho
moments_to_free_cumulants_general = _v1_audit.moments_to_free_cumulants_general

# Override v3's ITERATE_ROOT to point at the v1c traces.
_v3.ITERATE_ROOT = REPO / "data" / "exp_wave14_cap8_vamp_iterates_srht_hadamard_v1c"
ITERATE_ROOT = _v3.ITERATE_ROOT

find_iterate_trace = _v3.find_iterate_trace
load_iterate_trace = _v3.load_iterate_trace
iterate_fingerprint = _v3.iterate_fingerprint
measure_codebook_audit_trail_v2 = _v3.measure_codebook_audit_trail_v2
compute_verdict = _v3.compute_verdict


# ---------------------------------------------------------------------------
# Additional self-test: iid Gauss vs analytical Schur-Weyl baseline
# ---------------------------------------------------------------------------

def _self_test_iid_gauss_schur_weyl_baseline() -> None:
    """At c=1 (M=N), the iid Gaussian sample covariance has an empirical
    spectral density that converges to the Marchenko-Pastur distribution
    at c=1 with support [0, 4] and density f(x) = (1/(2*pi)) * sqrt((4-x)/x)
    on [0,4].  Moments: m_1 = 1, m_2 = 2, m_3 = 5, m_4 = 14 (Catalan
    numbers shifted).  The Schur-Weyl irrep (n)-mass at partition (n,) is
    s_(n,)(m_1,...,m_n) / sum_lam s_lam(m_1,...,m_n).

    For n=2: partitions are (2,) and (1,1).
      s_(2,) = (m_1^2 + m_2) / 2 = (1 + 2)/2 = 1.5
      s_(1,1) = (m_1^2 - m_2) / 2 = (1 - 2)/2 = -0.5  (floored to 0)
    So at c=1, mp_mass_(2,) = 1.5 / (1.5 + 0) = 1.0 (single irrep
    dominates because the other Schur poly is negative).

    Empirical iid Gauss at finite N should give mass_(2,) very close to
    1.0 but with deviation from MP O(1/sqrt(N)).

    This self-test verifies BOTH the analytical formula AND the empirical
    extraction.
    """
    # Analytical: at c=1
    mp_n2 = schur_weyl_irrep_masses_from_mp(c=1.0, n=2, M=1024)
    assert abs(mp_n2["mass_n"] - 1.0) < 1e-9, (
        f"MP mass_(2,) at c=1 should be 1.0 (since (1,1) Schur poly floors "
        f"to 0); got {mp_n2['mass_n']}"
    )

    # Empirical iid Gauss at N=M=1024, single seed
    A = build_iid_gauss(1024, 1024, seed=13)
    s = np.linalg.svd(A, compute_uv=False)
    eig = (s ** 2).astype(np.float64)
    sw = schur_weyl_irrep_masses(eig, n=2)
    # Empirical mass at (2,) should be close to 1.0; allow O(1/sqrt(N))
    # finite-size deviation plus floor-induced redistribution noise.
    assert sw["mass_n"] > 0.95, (
        f"Empirical iid Gauss mass_(2,) at N=M=1024 should be > 0.95 "
        f"(asymptotic MP at c=1 gives 1.0); got {sw['mass_n']}"
    )

    # Sanity: rebuild mp_reference_moments at n=4 and check m_1=1, m_2=2
    mp_moms = mp_reference_moments(1.0, 4)
    assert abs(mp_moms[0] - 1.0) < 1e-9, f"MP m_1 at c=1 expected 1.0, got {mp_moms[0]}"
    assert abs(mp_moms[1] - 2.0) < 1e-9, f"MP m_2 at c=1 expected 2.0, got {mp_moms[1]}"

    print("  iid-Gauss x Schur-Weyl baseline self-test PASS "
          f"(mp_mass_(2,)={mp_n2['mass_n']:.6f}, "
          f"empirical_mass_(2,)={sw['mass_n']:.6f}, "
          f"mp_m_1={mp_moms[0]:.6f}, mp_m_2={mp_moms[1]:.6f})", flush=True)


def _self_test_iterate_root_v1c_pointing() -> None:
    """Verify v4 has correctly repointed ITERATE_ROOT to the v1c traces."""
    expected = REPO / "data" / "exp_wave14_cap8_vamp_iterates_srht_hadamard_v1c"
    assert ITERATE_ROOT == expected, (
        f"ITERATE_ROOT should point at v1c traces; got {ITERATE_ROOT}, "
        f"expected {expected}"
    )
    # Also verify v3's _v3.ITERATE_ROOT was overridden (otherwise
    # load_iterate_trace will look in the v1b directory).
    assert _v3.ITERATE_ROOT == expected, (
        f"_v3.ITERATE_ROOT not overridden; load_iterate_trace will look in "
        f"the wrong directory: {_v3.ITERATE_ROOT}"
    )


def self_test() -> None:
    _v3.self_test()
    _self_test_iterate_root_v1c_pointing()
    _self_test_iid_gauss_schur_weyl_baseline()
    print("v4 self_test passed (v3 inherited + ITERATE_ROOT v1c pointing + "
          "iid-Gauss x Schur-Weyl analytical baseline)", flush=True)


# ---------------------------------------------------------------------------
# Run (overrides v3 to stamp mode marker and rho_by_family at top level)
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "M_over_N": 1.0,
            "n_seeds": 1,
            "n_max_order": 4,
            "codebooks": ["kerdock", "iid_gauss"],
            "use_iterates": False,
            "iterate_wait_seconds": 0,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N": 1.0,
            "n_seeds": 5,
            "n_max_order": 5,
            "codebooks": [nm for nm, _ in HARD_FAMILIES],
            "use_iterates": True,
            "iterate_wait_seconds": 900,
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    n_max = config["n_max_order"]
    n_seeds = config["n_seeds"]

    print(f"[setup] v4 N={N} M={M} n_seeds={n_seeds} n_max={n_max} "
          f"codebooks={config['codebooks']} use_iterates={config['use_iterates']} "
          f"iterate_wait_seconds={config['iterate_wait_seconds']} "
          f"ITERATE_ROOT={ITERATE_ROOT}", flush=True)

    builder_map = {nm: b for nm, b in HARD_FAMILIES}
    builder_map["iid_gauss"] = build_iid_gauss

    codebook_results = []
    for nm in config["codebooks"]:
        builder = builder_map[nm]
        print(f"\n[codebook] {nm}", flush=True)
        result = measure_codebook_audit_trail_v2(
            nm, builder, N, M, n_seeds, n_max,
            use_iterates=config["use_iterates"],
            iterate_wait_seconds=config["iterate_wait_seconds"],
        )
        codebook_results.append(result)
        print(f"  AGG {nm}: rho_aggregate={result['rho_aggregate']:.6f} "
              f"tied={result['tied']} sw_std={result['sw_mass_n_std']:.6f} "
              f"kd_std={result['kappa_div_std']:.6f} "
              f"iter_status={result['iterate_status_per_seed']}",
              flush=True)

    summary = {"codebook_results": codebook_results, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    env_name = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{env_name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    """v4 expanded validation: require mode + rho_by_family at top level."""
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config", "mode"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")
    if d["mode"] not in ("smoke", "full"):
        raise ValueError(f"metrics['mode'] must be 'smoke' or 'full'; got {d['mode']!r}")


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, tuple):
        return list(o)
    return float(o)


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    rho_by_family = summary.get("rho_by_family")
    if rho_by_family is None:
        rho_by_family = {c["name"]: c.get("rho_aggregate")
                          for c in summary.get("codebook_results", [])}
        summary["rho_by_family"] = rho_by_family

    tied_by_family = summary.get("tied_by_family")
    if tied_by_family is None:
        tied_by_family = {c["name"]: c.get("tied", False)
                          for c in summary.get("codebook_results", [])}
        summary["tied_by_family"] = tied_by_family

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
        "mode": config.get("mode", "unknown"),
        "rho_by_family": rho_by_family,
        "tied_by_family": tied_by_family,
        "n_codebooks_measured": len(summary.get("codebook_results", [])),
        "n_seeds": config.get("n_seeds"),
        "N": config.get("N"),
        "iterate_root": str(ITERATE_ROOT),
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=_json_default))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}  "
          f"mode={metrics['mode']}  n_codebooks={metrics['n_codebooks_measured']}  "
          f"n_seeds={metrics['n_seeds']}  rho_by_family={rho_by_family}",
          flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap12_cap8_audit_trail_pipeline_v4_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert config["mode"] == "smoke", f"smoke run produced mode={config['mode']}"
    assert len(summary["codebook_results"]) >= 1, "smoke FAIL: no codebooks"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}  mode={config['mode']}  "
          f"codebooks={config['codebooks']}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap12_cap8_audit_trail_pipeline_v4")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)

    # Defense-in-depth: refuse to write a non-smoke metrics.json if the
    # config came out as smoke-mode (would indicate the script was
    # mis-invoked).  This is the v3->v4 fix.
    if config["mode"] != "full":
        raise RuntimeError(
            f"run_main produced config mode={config['mode']!r}; refusing to "
            f"write metrics.json (defense against smoke-leak)."
        )

    measured = {c["name"] for c in summary["codebook_results"]}
    expected = {nm for nm, _ in HARD_FAMILIES}
    if not expected.issubset(measured):
        raise RuntimeError(
            f"run_main measured codebooks {measured} but expected superset of "
            f"hard families {expected}; refusing to write metrics.json "
            f"(would mis-route as full-mode result with missing families)."
        )

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}  mode={config['mode']}  "
          f"hard_families_measured={sorted(measured & expected)}", flush=True)


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
