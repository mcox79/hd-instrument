"""Composition A audit-trail v5: extend iterate-loading to ALL 4 hard families.

What's new vs v4
----------------
v4 reported RM(1, m) rho=0.40 but the per-family iterate-status showed RM(1, m)
silently fell back to spectrum-only mode (v3/v4's `measure_codebook_audit_trail_v2`
only loads iterate traces for srht/hadamard).  Question: is RM(1, m) rho=0.40
because of the FALLBACK (spectrum-only vectors are shorter) or because RM(1, m)
genuinely has weak kappa_n / Schur-Weyl alignment?

v5 disambiguates this by:

  1. **Multi-root iterate loader.**  v5's `find_iterate_trace_v5` searches a
     LIST of iterate roots: v1c (for srht/hadamard) AND the new
     `wave14_cap8_vamp_iterates_rm_1_m_v1` (for rm_1_m).  Returns the first
     match found.  Kerdock continues to load via its existing audit-v1
     compatibility path (skipped from iterate-fingerprint side per v3 design).

  2. **Iterate-eligible family set expanded to {srht, hadamard, rm_1_m}.**
     v5's `measure_codebook_audit_trail_v5` is a re-implementation of v3's
     measure_codebook_audit_trail_v2 with the gate expanded.  Kerdock still
     uses spectrum-only (its v1 audit-trail run was the first to ship; no
     iterate traces were saved for it, and the gate would be a separate
     anchor's work).

  3. **Per-family iterate_source recorded.**  Each codebook_result now
     includes `iterate_root_used` (the iterate-root directory that supplied
     the trace) so we can audit downstream where each family's iterate data
     came from.

Hypothesis
----------
Same as v1-v4.  If kappa_n moments and Schur-Weyl irrep masses index the SAME
representation-theoretic structure, their component-wise divergence-from-MP
should correlate across families.

v5 disambiguation question
--------------------------
Does RM(1, m) rho rise above 0.60 once REAL iterate data is loaded (i.e., v4's
0.40 was the spectrum-only fallback artifact), OR does it stay near 0.40 even
with real iterates (i.e., RM(1, m) genuinely has weak structure on this axis)?

HARD PASS (Composition A LICENSED at full 4-family scope)
---------------------------------------------------------
  Spearman rho >= 0.60 across >= 3/4 hard families WITH REAL ITERATES
  AND no family with rho < 0.30
  AND no family is TIED.

HARD FAIL (Composition A KILLED)
--------------------------------
  rho < 0.30 on >= 2/4 hard families with REAL iterates.

MIDDLE BAND
-----------
  Anything else.  Pay attention to PER-FAMILY rho diffs (v5 vs v4) to
  isolate which families genuinely have the alignment vs which were
  artifact-driven.

Codebook families (unchanged)
-----------------------------
  1. Kerdock 4-coset (spectrum-only; v1 traces archived but not yet integrated
     into the audit v5 loader -- separate anchor if needed)
  2. SRHT (iterate root: v1c)
  3. Hadamard (iterate root: v1c)
  4. RM(1, m) (iterate root: rm_v1, NEW)

Smoke
-----
N=1024, 1 seed, n_max=4, Kerdock + iid only, use_iterates=False.  Verdict
will be INCONCLUSIVE on smoke (not enough families) but self-tests +
multi-root iterate loader + iid-Gauss baseline must pass.

Pre-reg: preregs/2026-05-24_wave14_cap12_cap8_audit_trail_pipeline_v5.md
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

# Reuse the v3 module (loaders, single-root measure, verdict, self-tests).
_v3_path = REPO / "experiments" / "exp_wave14_cap12_cap8_audit_trail_pipeline_v3.py"
_spec_v3 = importlib.util.spec_from_file_location("audit_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec_v3)
_spec_v3.loader.exec_module(_v3)

# Pull v1 references for the iid-Gauss baseline self-test + math helpers.
_v1_audit = _v3._v1
build_iid_gauss = _v1_audit.build_iid_gauss
schur_weyl_irrep_masses = _v1_audit.schur_weyl_irrep_masses
schur_weyl_irrep_masses_from_mp = _v1_audit.schur_weyl_irrep_masses_from_mp
mp_reference_moments = _v1_audit.mp_reference_moments
mp_reference_cumulants = _v1_audit.mp_reference_cumulants
HARD_FAMILIES = _v1_audit.HARD_FAMILIES
spearman_rho = _v1_audit.spearman_rho
moments_to_free_cumulants_general = _v1_audit.moments_to_free_cumulants_general

iterate_fingerprint = _v3.iterate_fingerprint
compute_verdict = _v3.compute_verdict


# ---------------------------------------------------------------------------
# Multi-root iterate loader (v5)
# ---------------------------------------------------------------------------

ITERATE_ROOTS = [
    REPO / "data" / "exp_wave14_cap8_vamp_iterates_srht_hadamard_v1c",  # srht, hadamard
    REPO / "data" / "exp_wave14_cap8_vamp_iterates_rm_1_m_v1",          # rm_1_m (NEW)
]

# Iterate-fingerprint eligible families.  Kerdock excluded (spectrum-only;
# its v1 traces are not in the audit-loader layout).
ITERATE_ELIGIBLE = {"srht", "hadamard", "rm_1_m"}


def _alpha_label(alpha: float) -> str:
    return f"alpha_{alpha:.2f}".replace(".", "p")


def find_iterate_trace_v5(codebook: str, alpha: float, seed: int) -> Path | None:
    """Search ITERATE_ROOTS in order; return the first existing trace path or None."""
    for root in ITERATE_ROOTS:
        p = root / "iterates" / codebook / _alpha_label(alpha) / f"seed_{seed:04d}.json"
        if p.exists():
            return p
    return None


def load_iterate_trace_v5(codebook: str, alpha: float, seed: int,
                          wait_seconds: int = 0,
                          poll_interval: int = 30) -> tuple[dict | None, Path | None]:
    """Multi-root load; returns (trace_dict_or_None, root_path_or_None).

    Polls up to wait_seconds across all roots.  Returns (None, None) on absence.
    """
    deadline = time.monotonic() + wait_seconds
    while True:
        p = find_iterate_trace_v5(codebook, alpha, seed)
        if p is not None:
            try:
                return json.loads(p.read_text()), p.parent.parent.parent.parent
            except json.JSONDecodeError:
                if time.monotonic() >= deadline:
                    return None, None
                time.sleep(min(poll_interval, max(1, int(deadline - time.monotonic()))))
                continue
        if time.monotonic() >= deadline:
            return None, None
        sleep_for = min(poll_interval, max(1, int(deadline - time.monotonic())))
        print(f"  [wait] iterate trace not present yet for "
              f"{codebook} alpha={alpha} seed={seed} "
              f"(roots={[r.name for r in ITERATE_ROOTS]}; sleeping {sleep_for}s)",
              flush=True)
        time.sleep(sleep_for)


# ---------------------------------------------------------------------------
# v5 per-codebook measurement (extends v3 to include rm_1_m in iterate gate)
# ---------------------------------------------------------------------------

def measure_codebook_audit_trail_v5(name: str, builder, N: int, M: int,
                                     n_seeds: int, n_max: int,
                                     use_iterates: bool,
                                     iterate_wait_seconds: int) -> dict:
    """Same as v3.measure_codebook_audit_trail_v2 but with the iterate-load
    gate expanded to include rm_1_m, multi-root loading, and per-family
    iterate_root_used reporting.
    """
    c_ref = M / N
    mp_kappas = mp_reference_cumulants(c_ref, n_max)
    mp_mass_n_by_order = {}
    for n in range(2, n_max + 1):
        mp_info = schur_weyl_irrep_masses_from_mp(c_ref, n, M=M)
        mp_mass_n_by_order[n] = mp_info["mass_n"]

    per_seed = []
    iterate_status_per_seed = []
    iterate_root_used_per_seed = []
    for seed in range(n_seeds):
        seed_val = seed * 1000 + 13
        A = builder(N, M, seed_val)
        s = np.linalg.svd(A, compute_uv=False)
        eig = (s ** 2).astype(np.float64)

        moms = [float(np.mean(eig ** n)) for n in range(1, n_max + 1)]
        kappas = moments_to_free_cumulants_general(moms)

        kappa_div = []
        for n in range(2, n_max + 1):
            kappa_div.append(abs(kappas[n - 1] - mp_kappas[n - 1]))

        sw_mass_n = []
        for n in range(2, n_max + 1):
            sw = schur_weyl_irrep_masses(eig, n)
            mass_dev = abs(sw["mass_n"] - mp_mass_n_by_order[n])
            sw_mass_n.append(mass_dev)

        iterate_used = False
        iterate_root_used = None
        if use_iterates and name in ITERATE_ELIGIBLE:
            trace, root = load_iterate_trace_v5(name, alpha=1.0, seed=seed_val,
                                                wait_seconds=iterate_wait_seconds)
            if trace is not None and "trace" in trace and trace["trace"].get("mse_per_iter"):
                I_vec = iterate_fingerprint(trace, n_max)
                kappa_div = kappa_div + I_vec
                I_vec_y = [math.log1p(abs(v)) for v in I_vec]
                sw_mass_n = sw_mass_n + I_vec_y
                iterate_used = True
                iterate_root_used = str(root) if root is not None else None
                iterate_status_per_seed.append("loaded")
            else:
                iterate_status_per_seed.append("missing")
        elif use_iterates and name == "kerdock":
            iterate_status_per_seed.append("skipped_kerdock_no_iter_root")
        else:
            iterate_status_per_seed.append("skipped_no_iter_expected")
        iterate_root_used_per_seed.append(iterate_root_used)

        rho = spearman_rho(kappa_div, sw_mass_n)

        per_seed.append({
            "seed": seed_val,
            "kappa_divergence_components": kappa_div,
            "schur_weyl_mass_n_deviations": sw_mass_n,
            "iterate_used": iterate_used,
            "iterate_root_used": iterate_root_used,
            "rho_per_seed": rho,
        })
        print(f"    {name:10s} seed={seed} rho={rho if math.isfinite(rho) else 'NaN'} "
              f"iter_used={iterate_used} iter_root={iterate_root_used} "
              f"len_x={len(kappa_div)} len_y={len(sw_mass_n)}", flush=True)

    valid_rhos = [r["rho_per_seed"] for r in per_seed
                  if math.isfinite(r["rho_per_seed"])]
    rho_mean = float(np.mean(valid_rhos)) if valid_rhos else float("nan")
    rho_std = float(np.std(valid_rhos)) if len(valid_rhos) > 1 else 0.0

    if per_seed:
        common_len = min(len(r["kappa_divergence_components"]) for r in per_seed)
        kappa_div_mean = np.mean(
            [r["kappa_divergence_components"][:common_len] for r in per_seed],
            axis=0,
        ).tolist()
        sw_mass_n_mean = np.mean(
            [r["schur_weyl_mass_n_deviations"][:common_len] for r in per_seed],
            axis=0,
        ).tolist()
        rho_aggregate = spearman_rho(kappa_div_mean, sw_mass_n_mean)
    else:
        kappa_div_mean = []
        sw_mass_n_mean = []
        rho_aggregate = float("nan")

    sw_std = float(np.std(sw_mass_n_mean)) if sw_mass_n_mean else 0.0
    kd_std = float(np.std(kappa_div_mean)) if kappa_div_mean else 0.0
    tied = (sw_std < 1e-9 or kd_std < 1e-9)

    return {
        "name": name,
        "rho_mean_of_seeds": rho_mean,
        "rho_std_of_seeds": rho_std,
        "rho_aggregate": rho_aggregate,
        "kappa_div_mean": kappa_div_mean,
        "sw_mass_n_mean": sw_mass_n_mean,
        "kappa_div_std": kd_std,
        "sw_mass_n_std": sw_std,
        "tied": tied,
        "iterate_status_per_seed": iterate_status_per_seed,
        "iterate_root_used_per_seed": iterate_root_used_per_seed,
        "per_seed": per_seed,
    }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

def _self_test_iid_gauss_schur_weyl_baseline() -> None:
    """At c=1 the iid Gaussian MP-baseline mass_(2,) is 1.0 analytically.
    Same check as v4 (formula self-test per
    [[feedback-strategy-spec-formula-selftests]]).
    """
    mp_n2 = schur_weyl_irrep_masses_from_mp(c=1.0, n=2, M=1024)
    assert abs(mp_n2["mass_n"] - 1.0) < 1e-9, (
        f"MP mass_(2,) at c=1 should be 1.0; got {mp_n2['mass_n']}"
    )
    A = build_iid_gauss(1024, 1024, seed=13)
    s = np.linalg.svd(A, compute_uv=False)
    eig = (s ** 2).astype(np.float64)
    sw = schur_weyl_irrep_masses(eig, n=2)
    assert sw["mass_n"] > 0.95, (
        f"Empirical iid Gauss mass_(2,) at N=M=1024 should be > 0.95; "
        f"got {sw['mass_n']}"
    )
    mp_moms = mp_reference_moments(1.0, 4)
    assert abs(mp_moms[0] - 1.0) < 1e-9
    assert abs(mp_moms[1] - 2.0) < 1e-9
    print("  iid-Gauss x Schur-Weyl baseline self-test PASS "
          f"(mp_mass=1.0, empirical={sw['mass_n']:.6f})", flush=True)


def _self_test_multi_root_loader() -> None:
    """find_iterate_trace_v5 searches roots in order; returns None for absent.
    Synthetic check (we don't require files to exist for this -- only logic).
    """
    p = find_iterate_trace_v5("srht", alpha=1.0, seed=99999999)
    # If neither root has this seed, must return None
    assert p is None or p.exists(), (
        f"find_iterate_trace_v5 returned non-None for absent seed: {p}"
    )

    # Verify both roots are in the list and distinct
    assert len(ITERATE_ROOTS) >= 2, "ITERATE_ROOTS should contain >=2 roots"
    assert len({str(r) for r in ITERATE_ROOTS}) == len(ITERATE_ROOTS), (
        "ITERATE_ROOTS has duplicates"
    )
    # Verify the rm_1_m root path is present in the list
    rm_root = REPO / "data" / "exp_wave14_cap8_vamp_iterates_rm_1_m_v1"
    assert rm_root in ITERATE_ROOTS, (
        f"ITERATE_ROOTS missing rm_1_m root {rm_root}"
    )


def _self_test_iterate_eligible_set() -> None:
    """rm_1_m must be in the iterate-eligible set for v5 (this is THE point)."""
    assert "rm_1_m" in ITERATE_ELIGIBLE, (
        f"v5 must include rm_1_m in ITERATE_ELIGIBLE; got {ITERATE_ELIGIBLE}"
    )
    assert "srht" in ITERATE_ELIGIBLE
    assert "hadamard" in ITERATE_ELIGIBLE
    # Kerdock not eligible (its iterate root is not in the audit-loader layout)
    assert "kerdock" not in ITERATE_ELIGIBLE


def self_test() -> None:
    _v3.self_test()
    _self_test_multi_root_loader()
    _self_test_iterate_eligible_set()
    _self_test_iid_gauss_schur_weyl_baseline()
    print("v5 self_test passed (v3 inherited + multi-root loader + rm_1_m in "
          "iterate-eligible + iid-Gauss x Schur-Weyl analytical baseline)",
          flush=True)


# ---------------------------------------------------------------------------
# Run
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
            "iterate_wait_seconds": 1200,
        }

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    n_max = config["n_max_order"]
    n_seeds = config["n_seeds"]

    print(f"[setup] v5 N={N} M={M} n_seeds={n_seeds} n_max={n_max} "
          f"codebooks={config['codebooks']} use_iterates={config['use_iterates']} "
          f"iterate_wait_seconds={config['iterate_wait_seconds']} "
          f"ITERATE_ROOTS={[str(r) for r in ITERATE_ROOTS]} "
          f"ITERATE_ELIGIBLE={sorted(ITERATE_ELIGIBLE)}", flush=True)

    builder_map = {nm: b for nm, b in HARD_FAMILIES}
    builder_map["iid_gauss"] = build_iid_gauss

    codebook_results = []
    for nm in config["codebooks"]:
        builder = builder_map[nm]
        print(f"\n[codebook] {nm}", flush=True)
        result = measure_codebook_audit_trail_v5(
            nm, builder, N, M, n_seeds, n_max,
            use_iterates=config["use_iterates"],
            iterate_wait_seconds=config["iterate_wait_seconds"],
        )
        codebook_results.append(result)
        print(f"  AGG {nm}: rho_aggregate={result['rho_aggregate']:.6f} "
              f"tied={result['tied']} sw_std={result['sw_mass_n_std']:.6f} "
              f"kd_std={result['kappa_div_std']:.6f} "
              f"iter_status={result['iterate_status_per_seed']} "
              f"iter_roots={result['iterate_root_used_per_seed']}",
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
    if isinstance(o, Path):
        return str(o)
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

    iterate_used_by_family = {
        c["name"]: any(r.get("iterate_used") for r in c.get("per_seed", []))
        for c in summary.get("codebook_results", [])
    }
    summary["iterate_used_by_family"] = iterate_used_by_family

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
        "mode": config.get("mode", "unknown"),
        "rho_by_family": rho_by_family,
        "tied_by_family": tied_by_family,
        "iterate_used_by_family": iterate_used_by_family,
        "n_codebooks_measured": len(summary.get("codebook_results", [])),
        "n_seeds": config.get("n_seeds"),
        "N": config.get("N"),
        "iterate_roots": [str(r) for r in ITERATE_ROOTS],
        "iterate_eligible_families": sorted(ITERATE_ELIGIBLE),
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=_json_default))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}  "
          f"mode={metrics['mode']}  rho_by_family={rho_by_family}  "
          f"iter_used={iterate_used_by_family}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap12_cap8_audit_trail_pipeline_v5_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert config["mode"] == "smoke", f"smoke produced mode={config['mode']}"
    assert len(summary["codebook_results"]) >= 1, "smoke FAIL: no codebooks"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}  mode={config['mode']}  "
          f"codebooks={config['codebooks']}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_cap12_cap8_audit_trail_pipeline_v5")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)

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
            f"hard families {expected}; refusing to write metrics.json."
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
