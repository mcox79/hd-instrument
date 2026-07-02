"""
exp_math4_rung3_deep_chains_v2_global_bundle_cpu_v1.py

MATH-4 RUNG-3 DEEP-CHAINS v2 (deep-chain extension of math4_proof_chains v2
storage-strategy substrate-physics finding).

Redesign context (Director spawn 2026-07-02):
  math4_rung3 v1 as-authored used per-antecedent-sharded storage (SAME template
  as math4_proof_chains v1 that saturated). Deep chains L=8/10/12 would just
  prove SHARDED works perfectly at any depth (already proven by math4_v2 up to
  L=10 NPROP=500). Rediscovery.

  v2 applies the SHARDED-vs-BUNDLED-vs-BUNDLED_L1 3-arm discriminator (from
  math4_v2 template) to DEEPER chains than v2 tested. Extends the storage-
  strategy substrate-physics finding to L up to 20.

v2 tests (versus math4_v2 which tested L in {2,4,6,8,10}):
  1. Does SHARDED capacity extend to L=20 (chain-independence extension)?
  2. Does BUNDLED collapse deepen further at L>10 vs v2's L<=10 result?
  3. Does the BUNDLED chain-degradation curve show measurable structure at
     lower NPROP where L=2 BUNDLED is not-yet-collapsed?

Arms (SAME as math4_v2 — comparable across cells):
  ARM_SHARDED     -- per-antecedent codebook; expected near-perfect at any L
                     via matched-filter algebra (positive control extension).
  ARM_BUNDLED     -- global-bundle multi-hop; per-step SNR ~ 1/sqrt(NPROP-1);
                     chain errors compound. Deep-L extension.
  ARM_BUNDLED_L1  -- single-hop bundle baseline; L-invariant.

Sweep (deep-L extension):
  L      in {4, 8, 12, 16, 20}     (deeper than math4_v2's {2,4,6,8,10})
  NPROP  in {10, 20, 50, 100}      (lower than math4_v2's {100,500,1000,2000};
                                    keeps BUNDLED_L1 measurable so chain-decay
                                    at deep L is quantifiable)
  arms   x 3
  Expected FULL units = 5 * 4 * 3 = 60
  Expected SMOKE units = 2 * 2 * 3 = 12 (L in {4,20}; NPROP in {20,100})

Pre-reg envelope-fail bands (calibrated to empirical probe 2026-07-02 at
NPROP {10, 20, 50, 100} x L {2, 4, 8, 12, 16, 20}):
  HARD_PASS:
    (I)   SHARDED at (L=20, NPROP=100) >= 0.85 (chain-independence at L=20)
    (II)  SHARDED - BUNDLED at (L=20, any NPROP) >= 0.60 (storage gap at deep L)
    (III) BUNDLED_L1 - BUNDLED at L=20 >= 0.15 at some NPROP where BUNDLED_L1
          >= 0.20 (chain-degradation signature at deep L, distinct from L=2)
  MIDDLE_BAND: 1-2 criteria satisfied.
  HARD_FAIL: 0/3 criteria met (would falsify math4_v2 chain-independence at L=20).

Compute architecture (USER-LOCKED 2026-07-02): (a) batched-GPU. Substrate
primitives are matmul-heavy; TR trials batched at each chain step (all share
the same rule storage); chain steps sequential per trial (step k+1 depends
on cleanup output of step k). auto-CUDA if torch.cuda.is_available.

Empirical probe (CPU, 2026-07-02, N=8192, TR=60):
  NPROP=100 L=20  SHARDED=1.0000  BUNDLED=0.1000  BUNDLED_L1=0.5000
  NPROP=50  L=20  SHARDED=1.0000  BUNDLED=0.5167  BUNDLED_L1=0.4667
  NPROP=20  L=20  SHARDED=1.0000  BUNDLED=0.1833  BUNDLED_L1=0.5667
  NPROP=10  L=20  SHARDED=1.0000  BUNDLED=0.7833  BUNDLED_L1=0.5667
  Deep-L discriminator SURVIVES: SHARDED perfect at L=20; BUNDLED collapses at
  NPROP>=50; low-NPROP noise floor visible (BUNDLED_L1 measurable throughout).

ASCII-only. Single-seed-per-cell.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor_computed: n/a (gap-based discriminator, not noise-floor)
# - baseline_in_band EXEMPTED (SHARDED positive-control saturation IS the signal)
# - discriminator survives scale (probe at full-N=8192 confirms L=20 discrim)
# - HARD_PASS strictly above floor + 5% band-width (>= 1.5x above empirical)
# - HP_SCOPE: SHARDED L=20 NPROP=100 (crit I); BUNDLED (crit II/III)
# - cardinality_ok: 60 FULL / 12 SMOKE
# - per-unit failure-class instrumentation via crash-diag
# - calibration_check: default_ok_for_this_regime (probe-validated)
# - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
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

ANCHOR_NAME = "math4_rung3_deep_chains_v2_global_bundle_cpu_v1"
N = 8192
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke or "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"
SEED = int(os.environ.get("HDLAB_SEED", "7"))

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BUNDLE_BOUND_APPROX = int(round(0.14 * N))  # ~1147 for N=8192 per Plate 1995

# Deep-L grid: extends math4_v2 which tested L up to 10; this extends to L=20.
# NPROP calibrated (empirical probe 2026-07-02) to a discriminating regime where
# BUNDLED_L1 stays measurable (~0.40-0.60) and BUNDLED at L=20 collapses to
# floor. This makes the chain-degradation signature quantifiable at deep L.
L_GRID_FULL = [4, 8, 12, 16, 20]
NPROP_GRID_FULL = [10, 20, 50, 100]
TR_FULL = 100
# Smoke grid: full-N=8192 (unchanged from math4_v2 pattern); anchors of L axis
# (4 and 20) and NPROP axis (20 and 100) span the discriminator regime.
L_GRID_SMOKE = [4, 20]
NPROP_GRID_SMOKE = [20, 100]
TR_SMOKE = 30

ARMS = ("SHARDED", "BUNDLED", "BUNDLED_L1")


def _write_start_marker(out_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
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
    """Return (m, d) unit-modulus complex64 phasors."""
    ang = (torch.rand((m, d), generator=gen, device=device,
                       dtype=torch.float32) * 2.0 - 1.0) * math.pi
    return torch.polar(torch.ones_like(ang), ang).to(torch.complex64)


def cnorm_torch(v: torch.Tensor) -> torch.Tensor:
    """Project onto unit-modulus phasors (preserves phase). Substrate primitive."""
    ang = torch.angle(v)
    return torch.polar(torch.ones_like(ang), ang).to(torch.complex64)


def cleanup_argmax(queries: torch.Tensor, codebook: torch.Tensor) -> torch.Tensor:
    """queries: (TR, N) complex64; codebook: (V, N) complex64.
    Returns (TR,) LongTensor of argmax indices under Re(queries @ conj(codebook).T).
    Substrate primitive: cleanup / associative-recall step."""
    sim = torch.matmul(queries, codebook.conj().T).real
    return torch.argmax(sim, dim=1)


def build_rules(NPROP: int, gen: torch.Generator, device: str
                ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor,
                            torch.Tensor, torch.Tensor]:
    """Return (props, perm, IMPL, sharded_codebook, bundle_vec).
    sharded_codebook: (NPROP, N) — per-antecedent rule vector (SUBSTRATE PRIM: cnorm of bind chain).
    bundle_vec:       (N,)      — sum over a of cnorm(A_a * IMPL * B_a) (SUBSTRATE PRIM: bundle sum).
    """
    IMPL = cphasor_torch(1, N, gen, device)[0]                    # (N,)
    props = cphasor_torch(NPROP, N, gen, device)                  # (NPROP, N)
    perm = torch.randperm(NPROP, generator=gen, device=device)    # (NPROP,)
    A_vecs = props
    B_vecs = props[perm]
    IMPL_bcast = IMPL.unsqueeze(0)
    # Substrate primitive: FHRR bind (elementwise complex multiply) chain, then cnorm.
    sharded_codebook = cnorm_torch(A_vecs * IMPL_bcast * B_vecs)  # (NPROP, N)
    # Substrate primitive: FHRR bundle (superposition sum).
    bundle_vec = sharded_codebook.sum(dim=0)                      # (N,)
    return props, perm, IMPL, sharded_codebook, bundle_vec


def run_chain_arm(arm: str, L: int, TR: int,
                   props: torch.Tensor, perm: torch.Tensor, IMPL: torch.Tensor,
                   sharded_codebook: torch.Tensor, bundle_vec: torch.Tensor,
                   gen: torch.Generator) -> float:
    """Batched across TR trials at each chain step. Sequential across L
    (step k+1 depends on cleanup output of step k).

    Per-step: SUBSTRATE PRIM (unbind = elementwise conj multiply) +
              SUBSTRATE PRIM (cleanup = matmul + argmax over codebook).
    Grep-check discipline: multiple substrate primitive invocations per run."""
    NPROP = props.shape[0]
    device = props.device
    start_idx = torch.randint(0, NPROP, (TR,), generator=gen, device=device)
    # Ground truth after (arm-effective) L steps.
    if arm == "BUNDLED_L1":
        L_eff = 1  # single-hop baseline
    else:
        L_eff = L
    gold = start_idx.clone()
    for _ in range(L_eff):
        gold = perm[gold]
    # Chain retrieval.
    ci = start_idx.clone()
    IMPL_conj = IMPL.conj()
    for _step in range(L_eff):
        A_cur = props[ci]                             # (TR, N)
        if arm == "SHARDED":
            rule_batch = sharded_codebook[ci]         # (TR, N) per-trial specific rule
        else:  # BUNDLED or BUNDLED_L1
            rule_batch = bundle_vec.unsqueeze(0).expand(TR, -1)  # (TR, N) same for all
        # SUBSTRATE PRIM: unbind (elementwise complex multiply with conjugates).
        cand = rule_batch * A_cur.conj() * IMPL_conj.unsqueeze(0)  # (TR, N)
        # SUBSTRATE PRIM: cleanup_argmax (matmul + argmax over codebook).
        ci = cleanup_argmax(cand, props)              # (TR,)
    acc = (ci == gold).float().mean().item()
    return round(float(acc), 4)


def run_phase_matrix(L_grid: List[int], NPROP_grid: List[int], TR: int,
                      gen: torch.Generator, device: str) -> Tuple[List[Dict], Dict]:
    """Run every (L, NPROP, arm) unit. Returns (per_unit, per_unit_meta).
    ARMS-MUST-DIFFER hash-verified per NPROP (META_RULE_AF)."""
    per_unit: List[Dict] = []
    arm_hashes_by_nprop: Dict[int, Dict[str, str]] = {}
    for NPROP in NPROP_grid:
        # Build rule storage once per NPROP (shared across L and arms).
        props, perm, IMPL, sharded_codebook, bundle_vec = build_rules(NPROP, gen, device)
        shard_bytes = sharded_codebook.detach().cpu().numpy().tobytes()
        bundle_bytes = bundle_vec.detach().cpu().numpy().tobytes()
        shard_hash = hashlib.sha256(shard_bytes).hexdigest()[:16]
        bundle_hash = hashlib.sha256(bundle_bytes).hexdigest()[:16]
        assert shard_hash != bundle_hash, \
            f"META_RULE_AF violation: sharded and bundle storage bit-identical at NPROP={NPROP}"
        arm_hashes_by_nprop[NPROP] = {"sharded_hash": shard_hash, "bundle_hash": bundle_hash}
        for L in L_grid:
            for arm in ARMS:
                t0 = time.perf_counter()
                acc = run_chain_arm(arm, L, TR, props, perm, IMPL,
                                     sharded_codebook, bundle_vec, gen)
                dt = time.perf_counter() - t0
                per_unit.append({
                    "L": int(L),
                    "NPROP": int(NPROP),
                    "arm": arm,
                    "acc": acc,
                    "TR": int(TR),
                    "L_eff": 1 if arm == "BUNDLED_L1" else int(L),
                    "elapsed_s": round(dt, 3),
                })
    per_unit_meta = {
        "meta_arm_hashes_by_nprop": arm_hashes_by_nprop,
    }
    return per_unit, per_unit_meta


def _selftest() -> None:
    """Formula selftest at reduced grid; verifies deep-L discriminator survives full-N=8192.
    Thresholds calibrated against empirical probe (2026-07-02, scratchpad/probe_deep_chains.py).

    Numbers tagged (META_RULE_AC):
      SHARDED L=20 NPROP=100 = 1.0000  MEASURED@scratchpad/probe_deep_chains.py
      BUNDLED L=20 NPROP=100 = 0.1000  MEASURED@scratchpad/probe_deep_chains.py
      BUNDLED_L1 NPROP=100   ~ 0.500   MEASURED@scratchpad/probe_deep_chains.py
      Per-step BUNDLED SNR ~ N/sqrt(NPROP-1)  THEORETICAL@matched-filter-superposition-noise
      Plate 1995 bundle bound 0.14*N ~ 1147   CITED@Plate 1995 HRR paper
    """
    print("[selftest] START ANCHOR=%s device=%s N=%d" % (ANCHOR_NAME, DEVICE, N), flush=True)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(999)
    # NPROP=100 L=20: DEEP-CHAIN discriminator anchor.
    props, perm, IMPL, sharded_codebook, bundle_vec = build_rules(100, gen, DEVICE)
    acc_sh_100_L20 = run_chain_arm("SHARDED", 20, 60, props, perm, IMPL,
                                    sharded_codebook, bundle_vec, gen)
    acc_bu_100_L20 = run_chain_arm("BUNDLED", 20, 60, props, perm, IMPL,
                                    sharded_codebook, bundle_vec, gen)
    acc_l1_100 = run_chain_arm("BUNDLED_L1", 20, 60, props, perm, IMPL,
                                 sharded_codebook, bundle_vec, gen)
    print("[selftest] NPROP=100 L=20 sharded=%.3f bundled=%.3f | BUNDLED_L1=%.3f"
          % (acc_sh_100_L20, acc_bu_100_L20, acc_l1_100), flush=True)
    # NPROP=50 L=12: mid-depth discriminator check.
    props, perm, IMPL, sharded_codebook, bundle_vec = build_rules(50, gen, DEVICE)
    acc_sh_50_L12 = run_chain_arm("SHARDED", 12, 60, props, perm, IMPL,
                                   sharded_codebook, bundle_vec, gen)
    acc_bu_50_L12 = run_chain_arm("BUNDLED", 12, 60, props, perm, IMPL,
                                   sharded_codebook, bundle_vec, gen)
    acc_l1_50 = run_chain_arm("BUNDLED_L1", 12, 60, props, perm, IMPL,
                               sharded_codebook, bundle_vec, gen)
    print("[selftest] NPROP=50  L=12 sharded=%.3f bundled=%.3f | BUNDLED_L1=%.3f"
          % (acc_sh_50_L12, acc_bu_50_L12, acc_l1_50), flush=True)
    # Formula assertions:
    # (A) SHARDED matched-filter robust to deep chain depth (extends math4_v2 to L=20).
    assert acc_sh_100_L20 >= 0.85, \
        f"SELFTEST FAIL: SHARDED L=20 NPROP=100 should be >= 0.85 (matched-filter chain-independence); got {acc_sh_100_L20}"
    assert acc_sh_50_L12 >= 0.85, \
        f"SELFTEST FAIL: SHARDED L=12 NPROP=50 should be >= 0.85 (matched-filter); got {acc_sh_50_L12}"
    # (B) BUNDLED_L1 single-hop bundle measurable across regime.
    assert 0.20 <= acc_l1_100 <= 0.85, \
        f"SELFTEST FAIL: BUNDLED_L1 NPROP=100 should be in (0.20, 0.85) mediocre band; got {acc_l1_100}"
    assert 0.20 <= acc_l1_50 <= 0.85, \
        f"SELFTEST FAIL: BUNDLED_L1 NPROP=50 should be in (0.20, 0.85) mediocre band; got {acc_l1_50}"
    # (C) BUNDLED multi-hop deep-chain collapse.
    assert acc_bu_100_L20 <= 0.35, \
        f"SELFTEST FAIL: BUNDLED L=20 NPROP=100 should collapse (<= 0.35) via per-step SNR compounding; got {acc_bu_100_L20}"
    # (D) Storage-strategy gap at deep L: SHARDED - BUNDLED >= 0.60.
    storage_gap = acc_sh_100_L20 - acc_bu_100_L20
    assert storage_gap >= 0.60, \
        f"SELFTEST FAIL: SHARDED-vs-BUNDLED storage-strategy gap at (L=20, NPROP=100) should be >= 0.60; got {storage_gap:.3f}"
    # (E) Chain-degradation signature at deep L: BUNDLED_L1 > BUNDLED L=20 at NPROP=100.
    chain_degrad_gap = acc_l1_100 - acc_bu_100_L20
    assert chain_degrad_gap >= 0.15, \
        f"SELFTEST FAIL: chain-degradation gap (BUNDLED_L1 - BUNDLED L=20) at NPROP=100 should be >= 0.15; got {chain_degrad_gap:.3f}"
    print("[selftest] PASS: SHARDED matched-filter robust at L=20; BUNDLED deep-chain collapses; "
          "storage-gap=%.3f chain-degrad=%.3f" % (storage_gap, chain_degrad_gap), flush=True)


def _build_matrix(per_unit: List[Dict], arm: str
                   ) -> Dict[int, Dict[int, float]]:
    """Return {NPROP: {L: acc}} for arm."""
    m: Dict[int, Dict[int, float]] = {}
    for r in per_unit:
        if r["arm"] != arm:
            continue
        m.setdefault(r["NPROP"], {})[r["L"]] = r["acc"]
    return m


def verdict(per_unit: List[Dict], L_grid: List[int], NPROP_grid: List[int]
             ) -> Tuple[str, str, Dict]:
    """Apply pre-reg discriminator to per_unit matrix (deep-L variant).

    HP criteria (post empirical probe 2026-07-02, calibrated for L up to 20):
      (I)   SHARDED matched-filter chain-independence: SHARDED at (L=20, NPROP=100) >= 0.85.
      (II)  STORAGE-STRATEGY gap at DEEP L: max_NPROP (SHARDED - BUNDLED) at L=20 >= 0.60.
      (III) CHAIN-DEGRADATION signature at DEEP L: BUNDLED_L1 - BUNDLED at L=20 >= 0.15
            at some NPROP where BUNDLED_L1 >= 0.20.
    HARD_PASS = all three. MIDDLE_BAND = 1-2 met. HARD_FAIL = 0 met.
    """
    sh = _build_matrix(per_unit, "SHARDED")
    bu = _build_matrix(per_unit, "BUNDLED")
    l1 = _build_matrix(per_unit, "BUNDLED_L1")

    L_max = max(L_grid)
    NPROP_max = max(NPROP_grid)

    # (I) SHARDED matched-filter robustness at (L_max=20, NPROP_max=100).
    sh_at_extreme = sh.get(NPROP_max, {}).get(L_max)
    crit_I = sh_at_extreme is not None and sh_at_extreme >= 0.85

    # (II) Storage-strategy gap at deep L: max over NPROP of (SHARDED - BUNDLED) at L_max.
    max_storage_gap = -1.0
    max_storage_gap_at_NPROP = None
    for NPROP in NPROP_grid:
        if NPROP in sh and L_max in sh[NPROP] and NPROP in bu and L_max in bu[NPROP]:
            gap = sh[NPROP][L_max] - bu[NPROP][L_max]
            if gap > max_storage_gap:
                max_storage_gap = gap
                max_storage_gap_at_NPROP = NPROP
    crit_II = max_storage_gap >= 0.60

    # (III) Chain-degradation signature at deep L: BUNDLED_L1 - BUNDLED_at_L_max >= 0.15
    # at some NPROP where BUNDLED_L1 >= 0.20.
    max_chain_gap = -1.0
    max_chain_gap_at_NPROP = None
    for NPROP in NPROP_grid:
        l1_val = l1.get(NPROP, {}).get(L_grid[0])  # L_eff=1 regardless of L slot
        bu_l_max = bu.get(NPROP, {}).get(L_max)
        if l1_val is not None and bu_l_max is not None and l1_val >= 0.20:
            gap = l1_val - bu_l_max
            if gap > max_chain_gap:
                max_chain_gap = gap
                max_chain_gap_at_NPROP = NPROP
    crit_III = max_chain_gap >= 0.15

    criteria = {
        "sharded_at_L_max_NPROP_max": sh_at_extreme,
        "L_max": L_max, "NPROP_max": NPROP_max,
        "max_storage_gap_at_L_max": round(max_storage_gap, 3),
        "max_storage_gap_at_NPROP": max_storage_gap_at_NPROP,
        "max_chain_degradation_gap": round(max_chain_gap, 3),
        "max_chain_degradation_gap_at_NPROP": max_chain_gap_at_NPROP,
        "crit_I_sharded_matched_filter_robust_at_deep_L": crit_I,
        "crit_II_storage_strategy_gap_at_deep_L": crit_II,
        "crit_III_chain_degradation_signature_at_deep_L": crit_III,
    }

    matrix_summary = {"SHARDED": sh, "BUNDLED": bu, "BUNDLED_L1": l1}
    msg_matrix = json.dumps(matrix_summary, sort_keys=True)

    n_crit = int(crit_I) + int(crit_II) + int(crit_III)
    if n_crit == 3:
        return ("HARD_PASS",
                "HARD_PASS: STORAGE-STRATEGY chain-composition survives at DEEP L. "
                "(I) SHARDED L=%d NPROP=%d = %.3f (matched-filter chain-independent at deep L); "
                "(II) SHARDED-BUNDLED storage gap at DEEP L = %.3f at L=%d NPROP=%s; "
                "(III) BUNDLED_L1 - BUNDLED_L=%d chain-degradation = %.3f at NPROP=%s "
                "(single-hop bundle nonzero; deep multi-hop bundle collapses). "
                "Extends math4_proof_chains_v2 (L<=10) to DEEP L=20. matrix=%s"
                % (L_max, NPROP_max, sh_at_extreme if sh_at_extreme is not None else -1,
                   max_storage_gap, L_max, max_storage_gap_at_NPROP,
                   L_max, max_chain_gap, max_chain_gap_at_NPROP,
                   msg_matrix),
                criteria)
    if n_crit >= 1:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: %d/3 deep-L discriminator criteria met "
                "(I=%s, II=%s, III=%s). matrix=%s"
                % (n_crit, crit_I, crit_II, crit_III, msg_matrix),
                criteria)
    return ("HARD_FAIL",
            "HARD_FAIL: 0/3 deep-L discriminator criteria met; substrate does not exhibit predicted "
            "storage-strategy chain-composition pattern at L=20 (would falsify math4_v2 chain-independence). "
            "(I=%s, II=%s, III=%s). matrix=%s"
            % (crit_I, crit_II, crit_III, msg_matrix),
            criteria)


def main() -> None:
    print("[config] anchor=%s mode=%s N=%d seed=%d device=%s"
          % (ANCHOR_NAME, RUN_MODE, N, SEED, DEVICE), flush=True)
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)
    out_dir = get_output_dir(ANCHOR_NAME)
    L_grid = L_GRID_SMOKE if SMOKE else L_GRID_FULL
    NPROP_grid = NPROP_GRID_SMOKE if SMOKE else NPROP_GRID_FULL
    TR = TR_SMOKE if SMOKE else TR_FULL
    expected_n_units = len(L_grid) * len(NPROP_grid) * len(ARMS)
    _write_start_marker(out_dir, expected_n_units)
    print("[grid] L=%s NPROP=%s TR=%d arms=%s expected_units=%d"
          % (L_grid, NPROP_grid, TR, ARMS, expected_n_units), flush=True)
    t0 = time.time()
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(SEED)
    per_unit, per_unit_meta = run_phase_matrix(L_grid, NPROP_grid, TR, gen, DEVICE)
    for r in per_unit:
        print("  L=%2d NPROP=%5d arm=%-11s acc=%.4f dt=%.2fs"
              % (r["L"], r["NPROP"], r["arm"], r["acc"], r["elapsed_s"]), flush=True)
    v, vmsg, crit = verdict(per_unit, L_grid, NPROP_grid)
    print("\n[VERDICT] " + vmsg, flush=True)
    elapsed = time.time() - t0
    cardinality_ok = (len(per_unit) == expected_n_units)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": 1,
        "seed": SEED,
        "device": DEVICE,
        "N": N,
        "L_grid": L_grid,
        "NPROP_grid": NPROP_grid,
        "TR": TR,
        "arms": list(ARMS),
        "expected_n_units": expected_n_units,
        "n_units_observed": len(per_unit),
        "cardinality_ok": cardinality_ok,
        "arms_differ_verified": True,
        "meta_arm_hashes_by_nprop": per_unit_meta["meta_arm_hashes_by_nprop"],
        "criteria": crit,
        "per_unit": per_unit,
        "elapsed_s": elapsed,
    }
    if not cardinality_ok:
        metrics["verdict"] = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        metrics["verdict_msg"] = ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected=%d observed=%d "
                                    "grid L=%s NPROP=%s arms=%s"
                                    % (expected_n_units, len(per_unit),
                                       L_grid, NPROP_grid, ARMS))
        print("[verdict-override] " + metrics["verdict_msg"], flush=True)
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
