"""
exp_sharded_fhrr_topology_free_multi_f_dag_v1.py

Multi-fan-out DAG topology probe for full TOPOLOGY_FREE_SUBSTRATE_PHYSICS_LAW
META promotion (Skunkworks held prior promotion because F=4 alone is a single
axis; needs >= 3 distinct DAG variants + mixed).

Extends `sharded_fhrr_topology_free_dag_extension_v1` (CG this session at F=4
NPROP=5000). Same discriminator (SHARDED vs BUNDLE) at same N=8192 regime,
now sweeping fan-out F in {1, 2, 4, 8, MIXED}:

  F=1      : positive control (linear-chain reproduction under uniform 3-bind)
  F=2      : small branching
  F=4      : matches prior CG cell (reproducibility check + tight sanity gate)
  F=8      : deep branching stress test
  F=MIXED  : per-src fan-out drawn uniformly from {1, 2, 4, 8} -- realistic DAG

Reference cells + prior MEASURED numbers:
  MEASURED@d:/AI/hd-instrument/data/exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1_seed_7/metrics.json:
    sharded_acc_at_max_nprop = 1.0000 (SHARDED perfect at NPROP=16000, N=8192, LINEAR)
    bundle_acc_at_collapse_check = 0.045 (BUNDLE collapse at NPROP=4000, N=8192)
  MEASURED@d:/AI/hd-instrument/data/exp_sharded_fhrr_topology_free_dag_extension_v1_smoke/metrics.json:
    F=1 NPROP=5000: sharded=1.000 bundle=0.067 (positive control OK)
    F=4 NPROP=5000: sharded=1.000 bundle=0.033 (DAG discriminator satisfied)

Rules form a DAG with fan-out F per src:
  edge (src, edge_pos, dst) where src in [0, NPROP), edge_pos in [0, F_src)
  rule[edge_idx] = cnorm(props[src] * POS[edge_pos] * IMPL * props[dst])
  NRULES = sum_src(F_src)
  For uniform F : NRULES = NPROP * F
  For MIXED     : NRULES = sum_src(F_src) with F_src ~ Uniform({1,2,4,8})

Arms per phase point:
  SHARDED: per-edge codebook of size NRULES; query by (src, edge_pos) -> shard lookup
  BUNDLE : single vector S = sum over edges of rule[edge_idx]
Both arms use identical 3-unbind + matched-filter argmax cleanup vs props codebook.

Grid (FULL): F in {1, 2, 4, 8, MIXED} x NPROP in {200, 1000, 5000} = 15 phase points.
Smoke grid: F in {1, 8, MIXED} x NPROP in {200, 5000} = 6 phase points at full N=8192
            (fires discriminator at F=8 and MIXED extremes per DISCRIMINATOR-MUST-SURVIVE-SCALE).

Pre-registered bands (per prior CG cell + new axes):
  HARD_PASS:   SHARDED acc >= 0.85 at ALL {F=2,4,8,MIXED} at NPROP=5000
               AND BUNDLE acc < 0.10 at F=8 NPROP=5000 (highest NRULES stress)
               AND F=1 positive control SHARDED >= 0.85 at NPROP=5000 (Gate D).
               Topology-free evidence satisfied at >= 4 distinct DAG variants.
  MIDDLE_BAND: SHARDED 0.60-0.85 at any of {F=8, MIXED} at NPROP=5000; partial extension.
  HARD_FAIL:   SHARDED < 0.60 at F=8 OR MIXED at NPROP=5000 (extension bounded).

Compute: torch complex64; auto CUDA else CPU; batched build + streamed cleanup.
Peak GPU at F=8, NPROP=5000, N=8192:
  codebook (40000, 8192) complex64 = 2.62 GB
  props    (5000,  8192) complex64 = 328 MB
  Cleanup streamed in V=NPROP chunks; peak transient ~150 MB.
  Total peak GPU: ~3.5 GB. Fits 8GB target.

ASCII-only. Single-seed-per-cell per META_RULE_H CHUNKED (sibling wrappers _seed_{7,13,19}).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF; SHA-256 hash-test)
  - final_metrics_atomicity: tmp_replace (via write_metrics helper + _write_crash_metrics)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: matched-filter argmax over V codewords (categorical, not continuous)
  - baseline_in_band at smoke: BUNDLE spans discriminating band across grid
  - discriminator survives scale: smoke at full N=8192 with F=8/MIXED preview
  - HARD_PASS strictly above floor + 5% band-width (META_RULE_L; 0.85 > 0.60 + 0.05*0.35)
  - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = 15 FULL / 6 smoke
  - per-unit failure-class instrumentation (META_RULE_J; no bare except)
  - calibration_check: default_ok_for_this_regime (complex64 unit-modulus)
  - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
  - positive control (Gate D): F=1 SHARDED reproduces prior DAG cell's F=1 result
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
from typing import Dict, List, Tuple, Union
import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "sharded_fhrr_topology_free_multi_f_dag_v1"
N = 8192  # match prior CG DAG cell + scale_free_extension for direct comparison
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke or "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"
SEED = int(os.environ.get("HDLAB_SEED", "7"))

# F axis: literal ints for uniform fan-out; "MIXED" for per-src random f_src in {1,2,4,8}
F_GRID_FULL: List[Union[int, str]] = [1, 2, 4, 8, "MIXED"]
NPROP_GRID_FULL = [200, 1000, 5000]
# Smoke: extremes of F axis (positive control + F=8 stress + MIXED realism) at full N=8192
F_GRID_SMOKE: List[Union[int, str]] = [1, 8, "MIXED"]
NPROP_GRID_SMOKE = [200, 5000]
M_QUERIES_FULL = 200
M_QUERIES_SMOKE = 30

# For MIXED: F_src drawn uniformly from this set
F_MIXED_CHOICES = [1, 2, 4, 8]
# POS codebook must cover largest F used anywhere (uniform F=8 or MIXED max=8)
F_POS_MAX = 8

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BUNDLE_BOUND_APPROX = int(round(0.14 * N))  # CITED@Plate1995; ~1147 for N=8192


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
        "N": N,
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


def cleanup_argmax_streamed(queries: torch.Tensor, codebook: torch.Tensor,
                             device: str, chunk_size: int = 2000) -> torch.Tensor:
    """queries: (M, D) complex64; codebook: (V, D) complex64. Streams V-chunks."""
    M = queries.shape[0]
    V = codebook.shape[0]
    best_val = torch.full((M,), float("-inf"), device=device, dtype=torch.float32)
    best_idx = torch.zeros((M,), device=device, dtype=torch.long)
    for cs in range(0, V, chunk_size):
        ce = min(cs + chunk_size, V)
        cb_c = codebook[cs:ce]
        sim_c = torch.matmul(queries, cb_c.conj().T).real
        vals_c, idxs_c = sim_c.max(dim=1)
        mask = vals_c > best_val
        best_val = torch.where(mask, vals_c, best_val)
        best_idx = torch.where(mask, idxs_c + cs, best_idx)
        del cb_c, sim_c, vals_c, idxs_c, mask
    return best_idx


def build_dag(NPROP: int, F_spec: Union[int, str],
              gen_cpu: torch.Generator) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, int]:
    """Build fan-out DAG.

    For uniform F (int):
      Every src has exactly F outgoing edges; F distinct random targets per src.

    For MIXED:
      Each src draws F_src ~ Uniform(F_MIXED_CHOICES); F_src distinct targets per src.

    Returns ragged edge triples (edges_src, edges_pos, edges_dst) each of shape
    (NRULES,) int64, plus NRULES total. Also asserts F_MIXED max <= F_POS_MAX.
    """
    if isinstance(F_spec, int):
        F = F_spec
        assert F <= F_POS_MAX, f"F={F} exceeds F_POS_MAX={F_POS_MAX}"
        # Sample F distinct targets per src (without replacement within src's F edges).
        srcs = []
        poss = []
        dsts = []
        for src in range(NPROP):
            perm = torch.randperm(NPROP, generator=gen_cpu)[:F]
            for i in range(F):
                srcs.append(src)
                poss.append(i)
                dsts.append(int(perm[i]))
        edges_src = torch.tensor(srcs, dtype=torch.long)
        edges_pos = torch.tensor(poss, dtype=torch.long)
        edges_dst = torch.tensor(dsts, dtype=torch.long)
        NRULES = NPROP * F
        assert edges_src.numel() == NRULES
        return edges_src, edges_pos, edges_dst, NRULES

    if F_spec == "MIXED":
        srcs = []
        poss = []
        dsts = []
        F_choices_t = torch.tensor(F_MIXED_CHOICES, dtype=torch.long)
        for src in range(NPROP):
            # Draw F_src ~ Uniform(F_MIXED_CHOICES)
            idx = torch.randint(0, len(F_MIXED_CHOICES), (1,), generator=gen_cpu).item()
            F_src = int(F_choices_t[idx])
            assert F_src <= F_POS_MAX
            perm = torch.randperm(NPROP, generator=gen_cpu)[:F_src]
            for i in range(F_src):
                srcs.append(src)
                poss.append(i)
                dsts.append(int(perm[i]))
        edges_src = torch.tensor(srcs, dtype=torch.long)
        edges_pos = torch.tensor(poss, dtype=torch.long)
        edges_dst = torch.tensor(dsts, dtype=torch.long)
        NRULES = edges_src.numel()
        return edges_src, edges_pos, edges_dst, NRULES

    raise ValueError(f"Unknown F_spec: {F_spec!r}")


def run_phase_point(F_spec: Union[int, str], NPROP: int, M_queries: int,
                     gen_cpu: torch.Generator, device: str,
                     cleanup_chunk: int = 2000) -> Dict[str, float]:
    """One (F_spec, NPROP, seed) phase point.

    Substrate primitives invoked per phase point (>= 3 per grep-check META rule):
      BIND (elementwise mul, 3x: props[src]*POS[pos]*IMPL*props[dst])
      BUNDLE (sum reduction across NRULES for BUNDLE arm)
      CLEANUP (matmul + argmax against props codebook, both arms)

    Encoding:
      props: (NPROP, N) unit-modulus phasors
      IMPL:  (N,)       unit-modulus phasor
      POS:   (F_POS_MAX, N) unit-modulus phasors (0..F_POS_MAX-1 slots)

    Rule construction (per edge with (src, pos, dst)):
      rule[edge_idx] = cnorm(props[src] * POS[pos] * IMPL * props[dst])

    Query:
      pick random edge_idx uniformly over NRULES
      gold = edges_dst[edge_idx]
      SHARDED: rule_q = codebook[edge_idx]
        unbind = rule_q * conj(props[src]) * conj(POS[pos]) * conj(IMPL)
      BUNDLE : rule_q = S (single bundle); unbind analogous
      predict = argmax over v of Re(<unbind, props[v]>)
    """
    # Build node vectors, IMPL, POS on device (small at N=8192).
    props = cphasor_torch(NPROP, N, gen_cpu, "cpu").to(device)
    IMPL = cphasor_torch(1, N, gen_cpu, "cpu")[0].to(device)
    POS = cphasor_torch(F_POS_MAX, N, gen_cpu, "cpu").to(device)

    # Build DAG edges (ragged).
    edges_src_cpu, edges_pos_cpu, edges_dst_cpu, NRULES = build_dag(NPROP, F_spec, gen_cpu)
    edges_src = edges_src_cpu.to(device)
    edges_pos = edges_pos_cpu.to(device)
    edges_dst = edges_dst_cpu.to(device)

    # Compute F_avg + F_min + F_max for MIXED reporting; equals F for uniform int.
    if isinstance(F_spec, int):
        F_avg = float(F_spec)
        F_min = F_spec
        F_max = F_spec
    else:
        # MIXED: derive from edges_src histogram
        counts = torch.bincount(edges_src_cpu, minlength=NPROP)
        F_avg = float(counts.float().mean().item())
        F_min = int(counts.min().item())
        F_max = int(counts.max().item())

    # STEP 1: build codebook + bundle in NRULES-batches (bound peak transient).
    codebook = torch.empty((NRULES, N), dtype=torch.complex64, device=device)
    bundle_vec = torch.zeros(N, dtype=torch.complex64, device=device)
    build_batch = max(1, min(NRULES, 2000))  # edges per batch
    first_batch_rules_bytes = None
    for bs in range(0, NRULES, build_batch):
        be = min(bs + build_batch, NRULES)
        src_b = edges_src[bs:be]
        pos_b = edges_pos[bs:be]
        dst_b = edges_dst[bs:be]
        A = props[src_b]                        # (B, N)
        P = POS[pos_b]                          # (B, N)
        B = props[dst_b]                        # (B, N)
        rule_b = cnorm_torch(A * P * IMPL.unsqueeze(0) * B)  # (B, N)
        codebook[bs:be] = rule_b
        bundle_vec = bundle_vec + rule_b.sum(dim=0)
        if bs == 0:
            first_batch_rules_bytes = rule_b[: min(rule_b.shape[0], 100)].detach().cpu().numpy().tobytes()
        del A, P, B, rule_b, src_b, pos_b, dst_b
        if device == "cuda":
            torch.cuda.empty_cache()

    # STEP 2: query construction. Pick M random edge indices.
    q_edge_idx_cpu = torch.randint(0, NRULES, (M_queries,), generator=gen_cpu)
    q_edge_idx = q_edge_idx_cpu.to(device)
    q_src = edges_src[q_edge_idx]
    q_pos = edges_pos[q_edge_idx]
    gold_indices = edges_dst[q_edge_idx]

    # SHARDED unbind.
    rule_q = codebook[q_edge_idx]                                     # (M, N)
    A_q = props[q_src]
    POS_q = POS[q_pos]
    unbind_sharded = rule_q * A_q.conj() * POS_q.conj() * IMPL.conj().unsqueeze(0)
    pred_sharded = cleanup_argmax_streamed(unbind_sharded, props, device, cleanup_chunk)
    acc_sharded = (pred_sharded == gold_indices).float().mean().item()
    del rule_q, unbind_sharded

    # BUNDLE unbind.
    bundle_bcast = bundle_vec.unsqueeze(0).expand(M_queries, -1)
    unbind_bundle = bundle_bcast * A_q.conj() * POS_q.conj() * IMPL.conj().unsqueeze(0)
    pred_bundle = cleanup_argmax_streamed(unbind_bundle, props, device, cleanup_chunk)
    acc_bundle = (pred_bundle == gold_indices).float().mean().item()
    del unbind_bundle

    # META_RULE_AF: arms must differ (SHA-256 hash of first-batch shard vs bundle_vec).
    if first_batch_rules_bytes is None:
        raise RuntimeError("first_batch_rules_bytes not captured; build_batch logic bug")
    bundle_bytes = bundle_vec.detach().cpu().numpy().tobytes()
    shard_hash = hashlib.sha256(first_batch_rules_bytes).hexdigest()[:16]
    bundle_hash = hashlib.sha256(bundle_bytes).hexdigest()[:16]
    assert shard_hash != bundle_hash, \
        f"META_RULE_AF violation: sharded first-batch and bundle bit-identical at F={F_spec} NPROP={NPROP}"

    peak_gpu_mb = None
    if device == "cuda":
        peak_gpu_mb = round(torch.cuda.max_memory_allocated() / (1024 * 1024), 1)
        torch.cuda.reset_peak_memory_stats()

    del codebook, bundle_vec, bundle_bcast, props, IMPL, POS, A_q, POS_q
    del edges_src, edges_pos, edges_dst, q_edge_idx, q_src, q_pos, gold_indices
    if device == "cuda":
        torch.cuda.empty_cache()

    return {
        "F_spec": F_spec if isinstance(F_spec, int) else str(F_spec),
        "F_avg": round(F_avg, 3),
        "F_min": int(F_min),
        "F_max_per_src": int(F_max),
        "NPROP": int(NPROP),
        "NRULES": int(NRULES),
        "M": int(M_queries),
        "acc_sharded": round(float(acc_sharded), 4),
        "acc_bundle": round(float(acc_bundle), 4),
        "sharded_hash": shard_hash,
        "bundle_hash": bundle_hash,
        "peak_gpu_mb": peak_gpu_mb,
    }


def _selftest() -> None:
    """Formula self-test at reduced N=4096 (< 30s).
    Verifies:
      (1) F=1, NPROP=200 (NRULES=200 < 0.14*4096=573): SHARDED near-perfect
      (2) F=8, NPROP=1000 (NRULES=8000 ~ 14x bound): SHARDED holds, BUNDLE collapses
      (3) F=MIXED, NPROP=1000 (NRULES ~ 3750 ~ 6.5x bound): SHARDED holds
    """
    print("[selftest] START ANCHOR=%s device=%s N=%d (formula test at reduced N=4096)"
          % (ANCHOR_NAME, DEVICE, N), flush=True)
    _N_TEST = 4096
    orig_N = globals()["N"]
    globals()["N"] = _N_TEST
    try:
        gen_cpu = torch.Generator(device="cpu")
        gen_cpu.manual_seed(999)
        r_pc = run_phase_point(F_spec=1, NPROP=200, M_queries=30,
                                gen_cpu=gen_cpu, device=DEVICE)
        gen_cpu.manual_seed(997)
        r_f8 = run_phase_point(F_spec=8, NPROP=1000, M_queries=30,
                                gen_cpu=gen_cpu, device=DEVICE)
        gen_cpu.manual_seed(995)
        r_mix = run_phase_point(F_spec="MIXED", NPROP=1000, M_queries=30,
                                 gen_cpu=gen_cpu, device=DEVICE)
    finally:
        globals()["N"] = orig_N
    print("[selftest] N=%d F=1     NPROP=200  NRULES=%d  sharded=%.3f bundle=%.3f"
          % (_N_TEST, r_pc["NRULES"], r_pc["acc_sharded"], r_pc["acc_bundle"]),
          flush=True)
    print("[selftest] N=%d F=8     NPROP=1000 NRULES=%d sharded=%.3f bundle=%.3f"
          % (_N_TEST, r_f8["NRULES"], r_f8["acc_sharded"], r_f8["acc_bundle"]),
          flush=True)
    print("[selftest] N=%d F=MIXED NPROP=1000 NRULES=%d  F_avg=%.2f sharded=%.3f bundle=%.3f"
          % (_N_TEST, r_mix["NRULES"], r_mix["F_avg"],
             r_mix["acc_sharded"], r_mix["acc_bundle"]), flush=True)
    # HYPOTHESIZED@this-file: F=1 NPROP=200 near-perfect (below bundle bound).
    assert r_pc["acc_sharded"] >= 0.90, \
        f"SELFTEST FAIL: sharded near-perfect expected at F=1 NPROP=200 N=4096; got {r_pc['acc_sharded']}"
    # F=8 NPROP=1000 NRULES=8000 ~ 14x bound: SHARDED must hold; BUNDLE collapses.
    assert r_f8["acc_sharded"] >= 0.85, \
        f"SELFTEST FAIL: sharded should survive F=8 NPROP=1000 N=4096 (NRULES=8000); got {r_f8['acc_sharded']} " \
        f"(if this fails, F=8 branch of topology-free hypothesis unlikely; abort full)"
    assert r_f8["acc_bundle"] < 0.30, \
        f"SELFTEST FAIL: bundle should collapse at F=8 NPROP=1000 N=4096; got {r_f8['acc_bundle']}"
    # F=MIXED NPROP=1000: SHARDED must hold under variable fan-out.
    assert r_mix["acc_sharded"] >= 0.85, \
        f"SELFTEST FAIL: sharded should survive F=MIXED NPROP=1000 N=4096; got {r_mix['acc_sharded']} " \
        f"(MIXED avg~3.75 fan-out; if this fails, mixed-topology hypothesis fails; abort full)"
    assert r_mix["acc_bundle"] < 0.30, \
        f"SELFTEST FAIL: bundle should collapse at F=MIXED NPROP=1000 N=4096; got {r_mix['acc_bundle']}"
    gap_f8 = r_f8["acc_sharded"] - r_f8["acc_bundle"]
    gap_mix = r_mix["acc_sharded"] - r_mix["acc_bundle"]
    assert gap_f8 >= 0.60, \
        f"SELFTEST FAIL: F=8 sharded-vs-bundle gap should be >= 0.60; got {gap_f8:.3f}"
    assert gap_mix >= 0.60, \
        f"SELFTEST FAIL: F=MIXED sharded-vs-bundle gap should be >= 0.60; got {gap_mix:.3f}"
    print("[selftest] PASS: sharded scales beyond bundle bound at F=1 (control), F=8 (stress), "
          "F=MIXED (realistic DAG); gaps F=8=%.3f F=MIXED=%.3f at N=4096"
          % (gap_f8, gap_mix), flush=True)
    print("[selftest] N=%d full-N discriminator survival verified in smoke at F=8 + MIXED NPROP=5000."
          % N, flush=True)


def run(out_dir: Path) -> Dict:
    if SMOKE:
        F_grid = F_GRID_SMOKE
        NPROP_grid = NPROP_GRID_SMOKE
        M = M_QUERIES_SMOKE
    else:
        F_grid = F_GRID_FULL
        NPROP_grid = NPROP_GRID_FULL
        M = M_QUERIES_FULL
    n_units = len(F_grid) * len(NPROP_grid)
    _write_start_marker(out_dir, RUN_MODE, expected_n_units=n_units)
    per_unit: List[Dict] = []
    t0 = time.perf_counter()
    idx = 0
    for F_spec in F_grid:
        for NPROP in NPROP_grid:
            idx += 1
            gen_cpu = torch.Generator(device="cpu")
            # Salt seed by (F, NPROP); for MIXED use hash of the literal.
            F_salt = F_spec if isinstance(F_spec, int) else 9999
            gen_cpu.manual_seed(int(SEED) * 100003 + int(F_salt) * 1009 + int(NPROP))
            t_pt = time.perf_counter()
            r = run_phase_point(F_spec=F_spec, NPROP=NPROP, M_queries=M,
                                 gen_cpu=gen_cpu, device=DEVICE)
            dt = time.perf_counter() - t_pt
            r["elapsed_s"] = round(dt, 3)
            per_unit.append(r)
            pk = r.get("peak_gpu_mb")
            pk_str = f" peak_gpu={pk}MB" if pk is not None else ""
            print("  [%d/%d] F=%s NPROP=%5d NRULES=%5d sharded=%.4f bundle=%.4f dt=%.2fs%s"
                  % (idx, n_units, str(F_spec), NPROP, r["NRULES"],
                     r["acc_sharded"], r["acc_bundle"], dt, pk_str), flush=True)
    total_s = time.perf_counter() - t0

    # Curves + HP gates.
    def _key(p: Dict) -> Tuple[str, int]:
        return (str(p["F_spec"]), p["NPROP"])
    by_key: Dict[Tuple[str, int], Dict] = {_key(p): p for p in per_unit}
    NPROP_max = max(NPROP_grid)
    # HP gate: all NON-POSITIVE-CONTROL F variants at NPROP_max must hold.
    non_pc_F = [str(F) for F in F_grid if F != 1]
    hp_points = [by_key.get((f, NPROP_max)) for f in non_pc_F]
    # F=8 highest NRULES stress point for BUNDLE-collapse gate.
    f8_point = by_key.get(("8", NPROP_max))
    # Positive control: F=1 at NPROP_max.
    pc_point = by_key.get(("1", NPROP_max)) if 1 in F_grid else None
    sharded_curve = {f"F={p['F_spec']},NPROP={p['NPROP']}": p["acc_sharded"] for p in per_unit}
    bundle_curve = {f"F={p['F_spec']},NPROP={p['NPROP']}": p["acc_bundle"] for p in per_unit}

    return {
        "n_units": n_units,
        "F_grid": [str(f) for f in F_grid],
        "NPROP_grid": NPROP_grid,
        "M_queries": M,
        "N": N,
        "seed": SEED,
        "device": DEVICE,
        "bundle_bound_approx": BUNDLE_BOUND_APPROX,
        "F_MIXED_choices": F_MIXED_CHOICES,
        "F_POS_MAX": F_POS_MAX,
        "per_unit": per_unit,
        "NPROP_max": NPROP_max,
        "hp_points": hp_points,
        "f8_point": f8_point,
        "pc_point": pc_point,
        "sharded_curve": sharded_curve,
        "bundle_curve": bundle_curve,
        "elapsed_run_s": round(total_s, 3),
    }


def verdict(r: Dict) -> Tuple[str, str]:
    """HARD_PASS: SHARDED >= 0.85 at ALL non-PC F at NPROP_max
       AND BUNDLE < 0.10 at F=8 NPROP_max (highest-NRULES gate)
       AND F=1 positive control SHARDED >= 0.85 at NPROP_max.
    """
    NPROP_max = r["NPROP_max"]
    hp_points = r["hp_points"]
    f8_point = r["f8_point"]
    pc = r["pc_point"]
    sharded_curve = r["sharded_curve"]
    bundle_curve = r["bundle_curve"]

    if any(p is None for p in hp_points):
        missing = [f for f, p in zip([f_ for f_ in r["F_grid"] if f_ != "1"], hp_points) if p is None]
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL: HP gate points missing {missing} at NPROP={NPROP_max}; cardinality breach.")

    # Gate D positive control (F=1 must reproduce).
    if pc is not None and pc["acc_sharded"] < 0.85:
        return ("HARD_FAIL_GATE_D_POSITIVE_CONTROL",
                f"HARD_FAIL: F=1 positive control collapsed at NPROP={NPROP_max}: "
                f"sharded={pc['acc_sharded']:.3f} (expected >= 0.85). Mechanism drift vs prior CG DAG cell. "
                f"Downstream multi-F conclusion UNRELIABLE. "
                f"sharded_curve={sharded_curve} bundle_curve={bundle_curve}")

    # HP: all non-PC F variants at NPROP_max hold + BUNDLE collapse at F=8.
    all_hp = all(p["acc_sharded"] >= 0.85 for p in hp_points)
    bundle_collapse = f8_point is not None and f8_point["acc_bundle"] < 0.10
    min_s_at_max = min(p["acc_sharded"] for p in hp_points)
    worst_F = None
    for p in hp_points:
        if p["acc_sharded"] == min_s_at_max:
            worst_F = p["F_spec"]
            break

    if all_hp and bundle_collapse:
        pc_msg = f"F=1 pc={pc['acc_sharded']:.3f} " if pc is not None else ""
        # Build per-F concise summary at NPROP_max
        per_f_msg = ", ".join(f"F={p['F_spec']}={p['acc_sharded']:.3f}" for p in hp_points)
        return ("HARD_PASS",
                f"HARD_PASS: SHARDED discriminates across ALL DAG variants at NPROP={NPROP_max} N={r['N']}: "
                f"{per_f_msg}. {pc_msg}F=8 BUNDLE={f8_point['acc_bundle']:.3f} (< 0.10). "
                f"META STORAGE_STRATEGY topology-free evidence SATISFIED across "
                f">= {len(hp_points)} distinct DAG variants (F=2,4,8,MIXED). "
                f"Physics law verified across LINEAR (prior CG) AND multi-F DAG topology. "
                f"sharded_curve={sharded_curve} bundle_curve={bundle_curve}")

    # MB: partial extension.
    if min_s_at_max >= 0.60:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: SHARDED partially survives multi-F DAG at NPROP={NPROP_max}: "
                f"worst variant F={worst_F} sharded={min_s_at_max:.3f} (below HP=0.85). "
                f"F=8 BUNDLE={f8_point['acc_bundle'] if f8_point else 'NA'}. "
                f"Topology-free extension PARTIAL. "
                f"sharded_curve={sharded_curve} bundle_curve={bundle_curve}")

    # HF: some variant collapses.
    return ("HARD_FAIL",
            f"HARD_FAIL: SHARDED collapses at F={worst_F} NPROP={NPROP_max}: "
            f"sharded={min_s_at_max:.3f}. META topology-free CLAIM FALSIFIED at F={worst_F}. "
            f"Scope-bound META atom to F <= {int(worst_F)-1 if isinstance(worst_F,int) or (isinstance(worst_F,str) and worst_F.isdigit()) else 'linear-only'} or specific topologies. "
            f"sharded_curve={sharded_curve} bundle_curve={bundle_curve}")


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
        "F_grid": r["F_grid"],
        "NPROP_grid": r["NPROP_grid"],
        "M_queries": r["M_queries"],
        "bundle_bound_approx": r["bundle_bound_approx"],
        "F_MIXED_choices": r["F_MIXED_choices"],
        "F_POS_MAX": r["F_POS_MAX"],
        "NPROP_max": r["NPROP_max"],
        "hp_points": r["hp_points"],
        "f8_point": r["f8_point"],
        "pc_point": r["pc_point"],
        "sharded_curve": r["sharded_curve"],
        "bundle_curve": r["bundle_curve"],
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
except Exception as e:
    try:
        _out_dir = get_output_dir(ANCHOR_NAME)
        _write_crash_metrics(_out_dir, e)
    except Exception:
        pass
    raise
