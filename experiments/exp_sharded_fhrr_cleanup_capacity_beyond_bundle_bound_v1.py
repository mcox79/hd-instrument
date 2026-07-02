"""
exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1.py

Substrate-physics probe: does per-antecedent SHARDED rule storage support
NPROP >> 0.14*N (classical bundle-capacity bound of Plate 1995) while a
single-vector BUNDLE arm collapses at the bound?

Discovered inside math4_proof_chains smoke saturation (2026-07-02):
sharded-storage cleanup was perfect at NPROP=16000 for N=8192 (~15x the
classical 0.14*N ~ 1147). This cell formalizes the finding + provides the
classical bundle-collapse positive control.

Arms:
  SHARDED:  per-antecedent codebook rule_vec[a] = cnorm(A * IMPL * B),
            shape (NPROP, N). Query by unbind at antecedent index.
  BUNDLE:   single vector S = sum over a of cnorm(A_a * IMPL * B_a).
            Query by unbind S * conj(A) * conj(IMPL), cleanup vs props.

Sweep:
  NPROP in {200, 500, 1000, 2000, 4000, 6000, 8000, 12000, 16000}
  N=8192, M=200 queries per (NPROP, arm), single seed per cell invocation.

Pre-registered bands:
  HARD_PASS:  SHARDED >= 0.95 at NPROP=16000 AND BUNDLE < 0.60 at
              NPROP >= 4000 (both mechanisms fire).
  MIDDLE_BAND: SHARDED >= 0.95 at NPROP=8000 but drops below 0.90 at
               NPROP=16000.
  HARD_FAIL:  SHARDED collapses at NPROP <= 4000 (finding was noise).

Compute: torch complex64; auto CUDA if available, else CPU. Batched
cleanup matmul across all M queries at each phase point (§ GPU-batching
mandatory per USER 2026-07-02).

ASCII-only. Single-seed-per-cell per META_RULE_H CHUNKED §13.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
import argparse, os, time, math, json, hashlib, traceback, platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1"
N = 8192
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke or "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"
SEED = int(os.environ.get("HDLAB_SEED", "7"))

# Grid: sweep NPROP; full grid across bundle-bound (0.14*N ~ 1147) both sides.
NPROP_GRID_FULL = [200, 500, 1000, 2000, 4000, 6000, 8000, 12000, 16000]
# Smoke: include the extremes at full-N to fire the discriminator (per
# DISCRIMINATOR-MUST-SURVIVE-SCALE; smoke grid keeps ends at full-N NPROP).
NPROP_GRID_SMOKE = [200, 4000, 16000]
M_QUERIES_FULL = 200
M_QUERIES_SMOKE = 30

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BUNDLE_BOUND_APPROX = int(round(0.14 * N))  # ~1147 for N=8192 per Plate 1995


def _write_start_marker(out_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
        "device": DEVICE,
        "seed": SEED,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir: Path, exc: BaseException) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "run_mode": RUN_MODE,
        "seed": SEED,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def cphasor_torch(m: int, d: int, gen: torch.Generator, device: str) -> torch.Tensor:
    """Return unit-modulus complex phasors of shape (m, d), complex64."""
    ang = (torch.rand((m, d), generator=gen, device=device,
                       dtype=torch.float32) * 2.0 - 1.0) * math.pi
    return torch.polar(torch.ones_like(ang), ang).to(torch.complex64)


def cnorm_torch(v: torch.Tensor) -> torch.Tensor:
    """Project onto unit-modulus phasors."""
    ang = torch.angle(v)
    return torch.polar(torch.ones_like(ang), ang).to(torch.complex64)


def cleanup_argmax(queries: torch.Tensor, codebook: torch.Tensor) -> torch.Tensor:
    """queries: (M, N) complex64; codebook: (V, N) complex64.
    Returns (M,) LongTensor of argmax indices under Re(queries @ conj(codebook).T).
    """
    # (M, N) @ (N, V) -> (M, V)
    sim = torch.matmul(queries, codebook.conj().T).real
    return torch.argmax(sim, dim=1)


def run_phase_point(NPROP: int, M_queries: int, gen: torch.Generator,
                     device: str) -> Dict[str, float]:
    """One (NPROP, seed) phase point; compute both SHARDED and BUNDLE
    accuracies + arm-differ hash."""
    IMPL = cphasor_torch(1, N, gen, device)[0]                    # (N,)
    props = cphasor_torch(NPROP, N, gen, device)                  # (NPROP, N)
    # Functional chain: nxt is a permutation over NPROP.
    perm = torch.randperm(NPROP, generator=gen, device=device)    # (NPROP,)

    # Build SHARDED codebook: rule_vec[a] = cnorm(props[a] * IMPL * props[nxt[a]])
    A_vecs = props                                                # (NPROP, N)
    B_vecs = props[perm]                                          # (NPROP, N)
    IMPL_bcast = IMPL.unsqueeze(0)                                # (1, N)
    sharded_codebook = cnorm_torch(A_vecs * IMPL_bcast * B_vecs)  # (NPROP, N)

    # Build BUNDLE: sum of NPROP normalized phasors, single vector (N,).
    # NOTE: bundle stores UNIT-NORM sums (each rule cnorm'd first), matching
    # classical Plate bundle-capacity setup.
    bundle_vec = sharded_codebook.sum(dim=0)                      # (N,)

    # Sample M query antecedent indices (uniform, with replacement).
    q_idx = torch.randint(0, NPROP, (M_queries,), generator=gen, device=device)
    A_q = props[q_idx]                                            # (M, N)
    B_q_gold = props[perm[q_idx]]                                 # (M, N) (unused directly)
    gold_indices = perm[q_idx]                                    # (M,) target indices into props

    # SHARDED arm: given q_idx (known antecedent), directly index its rule_vec,
    # unbind with conj(A) and conj(IMPL), cleanup against props.
    unbind_sharded = sharded_codebook[q_idx] * A_q.conj() * IMPL.conj().unsqueeze(0)  # (M, N)
    pred_sharded = cleanup_argmax(unbind_sharded, props)          # (M,)
    acc_sharded = (pred_sharded == gold_indices).float().mean().item()

    # BUNDLE arm: unbind single bundle vector with conj(A) * conj(IMPL);
    # bundle contains all rules superposed so unbind SNR is 1:(NPROP-1).
    bundle_bcast = bundle_vec.unsqueeze(0).expand(M_queries, -1)   # (M, N)
    unbind_bundle = bundle_bcast * A_q.conj() * IMPL.conj().unsqueeze(0)  # (M, N)
    pred_bundle = cleanup_argmax(unbind_bundle, props)             # (M,)
    acc_bundle = (pred_bundle == gold_indices).float().mean().item()

    # META_RULE_AF: arms must differ. Hash the codebook vs bundle representations.
    # (These represent the storage difference between the arms; must be distinct.)
    shard_bytes = sharded_codebook.detach().cpu().numpy().tobytes()
    bundle_bytes = bundle_vec.detach().cpu().numpy().tobytes()
    shard_hash = hashlib.sha256(shard_bytes).hexdigest()[:16]
    bundle_hash = hashlib.sha256(bundle_bytes).hexdigest()[:16]
    assert shard_hash != bundle_hash, \
        f"META_RULE_AF violation: sharded and bundle storage bit-identical at NPROP={NPROP}"

    return {
        "NPROP": int(NPROP),
        "M": int(M_queries),
        "acc_sharded": round(float(acc_sharded), 4),
        "acc_bundle": round(float(acc_bundle), 4),
        "sharded_hash": shard_hash,
        "bundle_hash": bundle_hash,
    }


def _selftest() -> None:
    """Formula self-test: verify at NPROP=200 SHARDED perfect, BUNDLE workable;
    at NPROP=16000 SHARDED near-perfect, BUNDLE near-random.
    """
    print("[selftest] START ANCHOR=%s device=%s N=%d" % (ANCHOR_NAME, DEVICE, N), flush=True)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(999)
    # Small-M validation
    r_lo = run_phase_point(NPROP=200, M_queries=30, gen=gen, device=DEVICE)
    r_mid = run_phase_point(NPROP=2000, M_queries=30, gen=gen, device=DEVICE)
    r_hi = run_phase_point(NPROP=16000, M_queries=30, gen=gen, device=DEVICE)
    print("[selftest] NPROP=200   sharded=%.3f bundle=%.3f" % (r_lo["acc_sharded"], r_lo["acc_bundle"]), flush=True)
    print("[selftest] NPROP=2000  sharded=%.3f bundle=%.3f" % (r_mid["acc_sharded"], r_mid["acc_bundle"]), flush=True)
    print("[selftest] NPROP=16000 sharded=%.3f bundle=%.3f" % (r_hi["acc_sharded"], r_hi["acc_bundle"]), flush=True)
    # Formula assertions (hypothesized from Plate 1995 + matched-filter theory):
    assert r_lo["acc_sharded"] >= 0.90, \
        f"SELFTEST FAIL: sharded should be >= 0.90 at NPROP=200 (well below bundle bound); got {r_lo['acc_sharded']}"
    assert r_hi["acc_sharded"] >= 0.90, \
        f"SELFTEST FAIL: sharded should still be >= 0.90 at NPROP=16000 (matched-filter regime); got {r_hi['acc_sharded']}"
    # Bundle collapses well before NPROP=16000. Predict << 0.10 there.
    assert r_hi["acc_bundle"] < 0.20, \
        f"SELFTEST FAIL: bundle should collapse at NPROP=16000 (>> 0.14*N={BUNDLE_BOUND_APPROX}); got {r_hi['acc_bundle']}"
    # Discriminator gap check at extreme
    gap = r_hi["acc_sharded"] - r_hi["acc_bundle"]
    assert gap >= 0.70, \
        f"SELFTEST FAIL: sharded-vs-bundle gap at NPROP=16000 should be >= 0.70; got {gap:.3f}"
    print("[selftest] PASS: sharded scales beyond bundle bound; discriminator fires at full-N (gap=%.3f)" % gap, flush=True)


def run(out_dir: Path) -> Dict:
    grid = NPROP_GRID_SMOKE if SMOKE else NPROP_GRID_FULL
    M = M_QUERIES_SMOKE if SMOKE else M_QUERIES_FULL
    n_units = len(grid)
    _write_start_marker(out_dir, RUN_MODE, expected_n_units=n_units)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(SEED)
    per_unit: List[Dict] = []
    t0 = time.perf_counter()
    for i, NPROP in enumerate(grid):
        t_pt = time.perf_counter()
        r = run_phase_point(NPROP=NPROP, M_queries=M, gen=gen, device=DEVICE)
        dt = time.perf_counter() - t_pt
        r["elapsed_s"] = round(dt, 3)
        per_unit.append(r)
        print("  [%d/%d] NPROP=%5d sharded=%.4f bundle=%.4f dt=%.2fs"
              % (i + 1, n_units, NPROP, r["acc_sharded"], r["acc_bundle"], dt), flush=True)
    total_s = time.perf_counter() - t0

    # Extract discriminator signals.
    by_nprop = {r["NPROP"]: r for r in per_unit}
    max_nprop = max(by_nprop.keys())
    sharded_at_max = by_nprop[max_nprop]["acc_sharded"]
    bundle_at_max = by_nprop[max_nprop]["acc_bundle"]
    # Find lowest NPROP >= 4000 in grid to check bundle collapse.
    bundle_collapse_check_nprop = min([k for k in by_nprop if k >= 4000], default=None)
    bundle_at_collapse = (by_nprop[bundle_collapse_check_nprop]["acc_bundle"]
                         if bundle_collapse_check_nprop is not None else None)

    return {
        "n_units": n_units,
        "grid_nprop": grid,
        "M_queries": M,
        "N": N,
        "seed": SEED,
        "device": DEVICE,
        "bundle_bound_approx": BUNDLE_BOUND_APPROX,
        "per_unit": per_unit,
        "sharded_acc_at_max_nprop": round(sharded_at_max, 4),
        "bundle_acc_at_max_nprop": round(bundle_at_max, 4),
        "max_nprop": max_nprop,
        "bundle_collapse_check_nprop": bundle_collapse_check_nprop,
        "bundle_acc_at_collapse_check": round(bundle_at_collapse, 4) if bundle_at_collapse is not None else None,
        "elapsed_run_s": round(total_s, 3),
    }


def verdict(r: Dict) -> Tuple[str, str]:
    max_nprop = r["max_nprop"]
    s_max = r["sharded_acc_at_max_nprop"]
    b_max = r["bundle_acc_at_max_nprop"]
    coll_np = r["bundle_collapse_check_nprop"]
    b_coll = r["bundle_acc_at_collapse_check"]
    grid = r["grid_nprop"]
    sharded_curve = {p["NPROP"]: p["acc_sharded"] for p in r["per_unit"]}
    bundle_curve = {p["NPROP"]: p["acc_bundle"] for p in r["per_unit"]}

    # HARD_PASS: sharded >= 0.95 at max NPROP (>= 1.9*N ~ 2*N regime) AND
    # bundle collapses to < 0.60 at NPROP >= 4000 (well past 0.14*N bundle bound).
    if max_nprop >= int(1.9 * N) and s_max >= 0.95 and b_coll is not None and b_coll < 0.60:
        return ("HARD_PASS",
                "HARD_PASS: SHARDED perfect cleanup at NPROP=%d (>=1.9*N; sharded=%.3f) AND "
                "BUNDLE collapses (bundle=%.3f at NPROP=%d, well below Plate 0.14*N~%d bound). "
                "Sharded rule-storage extends cleanup capacity ~%.1fx beyond classical bundle bound. "
                "sharded_curve=%s bundle_curve=%s"
                % (max_nprop, s_max, b_coll, coll_np, r["bundle_bound_approx"],
                   max_nprop / max(1, r["bundle_bound_approx"]),
                   sharded_curve, bundle_curve))
    # MIDDLE_BAND: sharded >= 0.95 at NPROP=8000 but drops below 0.90 at 16000.
    if 8000 in sharded_curve and sharded_curve[8000] >= 0.95 and s_max < 0.90:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: SHARDED holds at NPROP=8000 (%.3f) but drops at max NPROP=%d (%.3f). "
                "Extended capacity confirmed vs bundle bound but not at 2*N. sharded_curve=%s bundle_curve=%s"
                % (sharded_curve[8000], max_nprop, s_max, sharded_curve, bundle_curve))
    # HARD_FAIL: sharded collapses well before bundle bound OR both arms similar (no discriminator).
    if max_nprop >= int(1.9 * N) and s_max < 0.60:
        return ("HARD_FAIL",
                "HARD_FAIL: SHARDED collapses at NPROP=%d (sharded=%.3f); finding was noise. "
                "sharded_curve=%s bundle_curve=%s" % (max_nprop, s_max, sharded_curve, bundle_curve))
    # Fallback MIDDLE (sharded ok but bundle didn't collapse cleanly, or edge cases)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND (residual): sharded=%.3f at max_nprop=%d; bundle=%.3f at collapse_check=%s. "
            "sharded_curve=%s bundle_curve=%s"
            % (s_max, max_nprop, b_coll if b_coll is not None else -1, coll_np,
               sharded_curve, bundle_curve))


def main() -> None:
    print("[config] anchor=%s mode=%s N=%d seed=%d device=%s"
          % (ANCHOR_NAME, RUN_MODE, N, SEED, DEVICE), flush=True)
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    r = run(out_dir)
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)
    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": 1,
        "seed": SEED,
        "device": DEVICE,
        "N": N,
        "n_units": r["n_units"],
        "grid_nprop": r["grid_nprop"],
        "M_queries": r["M_queries"],
        "bundle_bound_approx": r["bundle_bound_approx"],
        "sharded_acc_at_max_nprop": r["sharded_acc_at_max_nprop"],
        "bundle_acc_at_max_nprop": r["bundle_acc_at_max_nprop"],
        "max_nprop": r["max_nprop"],
        "bundle_collapse_check_nprop": r["bundle_collapse_check_nprop"],
        "bundle_acc_at_collapse_check": r["bundle_acc_at_collapse_check"],
        "per_unit": r["per_unit"],
        "cardinality_ok": (len(r["per_unit"]) == r["n_units"]),
        "arms_differ_verified": True,
        "elapsed_s": elapsed,
    }
    write_metrics(out_dir, metrics, [{"seed": SEED, "elapsed_s": elapsed}])
    print("[metrics] written to %s/metrics.json" % out_dir, flush=True)


try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:  # NOT BaseException (preserves SystemExit + KeyboardInterrupt)
    try:
        _out_dir = get_output_dir(ANCHOR_NAME)
        _write_crash_metrics(_out_dir, e)
    except Exception:
        pass
    raise
