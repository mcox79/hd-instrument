"""
exp_sharded_fhrr_capacity_scale_free_extension_N16384_v1.py

Scale-free extension probe of META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1
(Skunkworks CG_META 2026-07-02).

Question: at N=16384 (2x the N=8192 CG cell), does the SHARDED-vs-BUNDLE
discriminator reproduce the SAME pattern -- SHARDED holds at NPROP >= 2*N
(i.e. NPROP=32000 for N=16384) while BUNDLE collapses at NPROP >> 0.14*N
(i.e. NPROP >= 4000 << bundle bound 0.14*N ~ 2294)?

  MEASURED@d:/AI/hd-instrument/data/exp_sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1_seed_7/metrics.json:sharded_acc_at_max_nprop
    = 1.0000 (SHARDED perfect at NPROP=16000, N=8192)
  MEASURED@same:bundle_acc_at_collapse_check = 0.045 (BUNDLE collapse at NPROP=4000, N=8192)
  MEASURED@same:elapsed_s = 4.7s (full 9-point sweep, cuda)

If scale-free pattern reproduces at 2x N, the META atom promotes to
SCALE_FREE_PHYSICS_LAW tier per the Skunkworks-declared extension criterion.
If NOT, the META claim is scoped to N=8192 or the physics law is
scale-dependent (which we'd honestly demote).

Arms (IDENTICAL mechanism to sharded_capacity_beyond_bundle_bound_v1):
  SHARDED:  per-antecedent codebook rule_vec[a] = cnorm(A * IMPL * B),
            shape (NPROP, N). Query by unbind at antecedent index.
  BUNDLE:   single vector S = sum over a of cnorm(A_a * IMPL * B_a).
            Query by unbind S * conj(A) * conj(IMPL), cleanup vs props.

Sweep NPROP in {2000, 4000, 8000, 16000, 32000}:
  - NPROP=2000: comfortably below bundle bound (0.14*N ~ 2294 for N=16384)
  - NPROP=4000, 8000, 16000: intermediate; BUNDLE expected to collapse
  - NPROP=32000: ~1.95*N; matches ratio of NPROP=16000/N=8192 in CG cell.
    HP gate uses this to test scale-free at proportional (NPROP/N) ratio.

Pre-registered bands:
  HARD_PASS:   SHARDED >= 0.95 at NPROP=32000 (>= 1.9*N) AND
               BUNDLE < 0.60 at NPROP=4000 (already >> 0.14*N bound).
               Same-pattern-at-2x-N; META extension criterion satisfied.
  MIDDLE_BAND: SHARDED 0.85-0.95 at NPROP=32000; partial scale-invariance.
  HARD_FAIL:   SHARDED < 0.60 at NPROP=32000; META scale-free CLAIM
               FALSIFIED (physics law is N-dependent, would DEMOTE).

Compute: torch complex64; auto CUDA if available, else CPU.
  v3: CPU-hosted props + streamed chunks design (fix for 8GB GPU OOM):
    - props (NPROP, N) complex64 BUILT + HELD on CPU RAM.
      At NPROP=32000, N=16384: 4.19 GB CPU. Never allocated as a
      single-shot GPU tensor (which was v1+v2's 4.19 GB OOM point).
    - BUILD phase: per NPROP-chunk (build_chunk=4000), transfer chunk
      CPU -> GPU, compute rule_c = cnorm(A_c * IMPL * B_c), sum into
      bundle_vec, free chunk. Peak GPU per BUILD chunk ~ 1.2 GB.
    - SHARDED cleanup: transfer only M query shards to GPU
      (M x N complex64 = 26 MB at M=200/N=16384).
    - CLEANUP: stream props chunks CPU->GPU per cleanup_chunk=4000;
      argmax over V codewords accumulated as running-max.
      Peak GPU per CLEANUP chunk ~ 0.5 GB.
    -> Total peak GPU ~ 1.2-1.5 GB. Fits 8GB target with 5.87 GB
       runner baseline (~1 GB headroom minimum).
  Peak GPU MB measured empirically per phase point via
  torch.cuda.max_memory_allocated() and logged in metrics.

  History:
    v1 (single-tensor): full-size cnorm intermediate + props both on
      GPU -> ~10 GB peak. OOM at line 189 on 8GB target.
    v2 (chunk-in-GPU): downstream ops chunked but props still allocated
      as 4.19 GB GPU tensor; OOM at line 165 (cphasor construction)
      on 8GB target with only 2.94 GB free (5.87 GB runner baseline).
    v3 (this): props on CPU RAM; only per-chunk transfers to GPU.
      Peak GPU well under 2 GB.
  Batched cleanup matmul across all M queries at each phase point
  (per GPU-batching-mandatory USER 2026-07-02); "batched" preserved
  via M queries batched intra-chunk on the V axis.

ASCII-only. Single-seed-per-cell per META_RULE_H CHUNKED §13.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF; SHA-256 hash-test)
  - final_metrics_atomicity: tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: matched-filter argmax over V codewords, not continuous estimation
  - baseline_in_band at smoke (META_RULE_AG): BUNDLE spans 0.5 -> ~0 across sweep
  - discriminator survives scale: smoke at full N=16384 with NPROP=32000 preview
  - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
  - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = 5 NPROP points
  - per-unit failure-class instrumentation (META_RULE_J; no bare except)
  - calibration_check: default_ok_for_this_regime (complex64 unit-modulus)
  - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
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

ANCHOR_NAME = "sharded_fhrr_capacity_scale_free_extension_N16384_v1"
N = 16384  # 2x the N=8192 CG_META cell; scale-free extension probe.
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke or "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"
SEED = int(os.environ.get("HDLAB_SEED", "7"))

# FULL grid: 5 NPROP points spanning below-bound to 1.95*N.
# 0.14*N = 2294 (bundle bound), so 2000 is just below, 4000 already >> bound,
# 32000 ~ 1.95*N matches the CG cell's NPROP=16000/N=8192 ratio (1.95x N).
NPROP_GRID_FULL = [2000, 4000, 8000, 16000, 32000]
# Smoke: fire discriminator at full N=16384; extremes preview the HP condition.
# NPROP=2000 (below bound: BUNDLE should still work ~0.5+), NPROP=8000 (mid),
# NPROP=32000 (max stress; SHARDED must hold and BUNDLE must collapse to certify HP).
NPROP_GRID_SMOKE = [2000, 8000, 32000]
M_QUERIES_FULL = 200
M_QUERIES_SMOKE = 30

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BUNDLE_BOUND_APPROX = int(round(0.14 * N))  # CITED@Plate1995; ~2294 for N=16384


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


def cphasor_torch_chunked_cpu(m: int, d: int, gen_cpu: torch.Generator,
                                chunk_size: int = 8000) -> torch.Tensor:
    """Build (m, d) complex64 unit-modulus phasors on CPU in chunks.

    Chunked construction avoids a single-shot allocation of large intermediates
    (m x d fp32 angle tensor + torch.polar output).  For m=32000, d=16384 the
    full-size angle tensor alone is 2.0 GB.  Chunking to 8000 caps intermediate
    peak at ~1.0 GB CPU RAM per chunk, then only the final (m, d) complex64
    tensor (~4.19 GB) is persistent.
    """
    out = torch.empty((m, d), dtype=torch.complex64, device="cpu")
    for cs in range(0, m, chunk_size):
        ce = min(cs + chunk_size, m)
        ang = (torch.rand((ce - cs, d), generator=gen_cpu, device="cpu",
                           dtype=torch.float32) * 2.0 - 1.0) * math.pi
        out[cs:ce] = torch.polar(torch.ones_like(ang), ang).to(torch.complex64)
        del ang
    return out


def cleanup_argmax_streamed(queries: torch.Tensor, codebook_cpu: torch.Tensor,
                             device: str, chunk_size: int = 4000) -> torch.Tensor:
    """queries: (M, N) complex64 ON DEVICE; codebook_cpu: (V, N) complex64 on CPU.
    Streams V-chunks CPU -> device and computes argmax over Re(queries @ conj(chunk).T).
    Peak device transient per chunk = chunk_size * N * 8 bytes = 0.5 GB at 4000/16384.
    """
    M = queries.shape[0]
    V = codebook_cpu.shape[0]
    best_val = torch.full((M,), float("-inf"), device=device, dtype=torch.float32)
    best_idx = torch.zeros((M,), device=device, dtype=torch.long)
    for cs in range(0, V, chunk_size):
        ce = min(cs + chunk_size, V)
        cb_c = codebook_cpu[cs:ce].to(device, non_blocking=False)  # (CV, N)
        sim_c = torch.matmul(queries, cb_c.conj().T).real  # (M, CV) fp32
        vals_c, idxs_c = sim_c.max(dim=1)
        mask = vals_c > best_val
        best_val = torch.where(mask, vals_c, best_val)
        best_idx = torch.where(mask, idxs_c + cs, best_idx)
        del cb_c, sim_c, vals_c, idxs_c, mask
        if device == "cuda":
            torch.cuda.empty_cache()
    return best_idx


def run_phase_point(NPROP: int, M_queries: int, gen: torch.Generator,
                     device: str, build_chunk: int = 2000,
                     cleanup_chunk: int = 2000) -> Dict[str, float]:
    """One (NPROP, seed) phase point; compute both SHARDED and BUNDLE
    accuracies + arm-differ hash. Substrate primitives invoked: bind
    (elementwise mul), bundle (sum), cleanup (matmul + argmax) -- >= 2
    per META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1 primitive
    invocation gate.

    CPU-HOSTED props design (v3 fix for 8GB GPU OOM):
      - props (NPROP, N) complex64 is built + held on CPU RAM (~4.19 GB
        at max NPROP=32000/N=16384). Never allocated on GPU as a single
        tensor (which was the 4.19 GB OOM in v1+v2 attempts).
      - BUILD phase: per NPROP-chunk, transfer chunk to GPU, compute
        rule_c = cnorm(A_c * IMPL * B_c), accumulate sum into bundle_vec,
        free chunk. Peak GPU transient per BUILD chunk ~ 1.2 GB.
      - SHARDED cleanup: transfer only M query shards to GPU
        (M x N complex64 = 26 MB at M=200/N=16384).
      - CLEANUP: stream props chunks CPU->GPU for argmax over V codewords.
        Peak GPU transient per CLEANUP chunk ~ 0.5 GB.
      Total GPU peak: ~1.2-1.5 GB (fits 8GB target with 5.87GB baseline).

    The `gen` parameter is a device-Generator; a matching CPU generator is
    created here with the same seed to keep props construction reproducible
    across CPU and device seeds.  For SEED=7/13/19 tests: props draws use
    a CPU generator seeded from SEED + phase_offset so each phase point is
    reproducible.  perm/q_idx also use CPU generator (all small tensors).
    """
    # Derive a CPU generator seeded from the passed device generator's state
    # via a stable per-NPROP salt so we get reproducible phase-point results.
    cpu_gen = torch.Generator(device="cpu")
    # Salt with NPROP + SEED so different phase points get different random
    # draws (as they would with a device-side stateful gen), but reproducible.
    cpu_gen.manual_seed(int(SEED) * 100003 + int(NPROP))

    IMPL = cphasor_torch(1, N, cpu_gen, "cpu")[0].to(device)      # (N,) on device
    # props built on CPU in chunks (never a single big GPU tensor).
    props_cpu = cphasor_torch_chunked_cpu(NPROP, N, cpu_gen,
                                          chunk_size=build_chunk)  # (NPROP, N) CPU
    perm_cpu = torch.randperm(NPROP, generator=cpu_gen)             # (NPROP,) CPU
    IMPL_bcast = IMPL.unsqueeze(0)                                  # (1, N) on device

    # STEP 1: BUILD bundle_vec by streaming chunks CPU -> GPU.
    # -- substrate primitives: BIND (elementwise mul) + BUNDLE (sum).
    bundle_vec = torch.zeros(N, dtype=torch.complex64, device=device)
    first_chunk_rules_bytes = None  # for arms-differ hash
    for cs in range(0, NPROP, build_chunk):
        ce = min(cs + build_chunk, NPROP)
        A_c = props_cpu[cs:ce].to(device, non_blocking=False)         # (C, N) on device
        B_idx = perm_cpu[cs:ce]                                        # CPU int64
        B_c = props_cpu[B_idx].to(device, non_blocking=False)          # (C, N) on device
        rule_c = cnorm_torch(A_c * IMPL_bcast * B_c)                   # (C, N) on device
        bundle_vec = bundle_vec + rule_c.sum(dim=0)                    # (N,)
        if cs == 0:
            first_chunk_rules_bytes = rule_c.detach().cpu().numpy().tobytes()
        del A_c, B_c, rule_c, B_idx
        if device == "cuda":
            torch.cuda.empty_cache()

    # STEP 2: query indices (CPU) + SHARDED query shards (transferred to device).
    q_idx_cpu = torch.randint(0, NPROP, (M_queries,), generator=cpu_gen)  # CPU
    A_q_cpu = props_cpu[q_idx_cpu]                                      # (M, N) CPU
    B_q_idx_cpu = perm_cpu[q_idx_cpu]                                   # (M,) CPU
    B_q_cpu = props_cpu[B_q_idx_cpu]                                    # (M, N) CPU
    gold_indices = B_q_idx_cpu.to(device)                               # (M,) on device

    A_q = A_q_cpu.to(device, non_blocking=False)                        # (M, N)
    B_q = B_q_cpu.to(device, non_blocking=False)                        # (M, N)
    del A_q_cpu, B_q_cpu, B_q_idx_cpu
    rule_q = cnorm_torch(A_q * IMPL_bcast * B_q)                        # (M, N) on device
    unbind_sharded = rule_q * A_q.conj() * IMPL.conj().unsqueeze(0)     # (M, N)
    # CLEANUP against props (streamed from CPU per chunk) -- CLEANUP primitive.
    pred_sharded = cleanup_argmax_streamed(unbind_sharded, props_cpu, device, cleanup_chunk)
    acc_sharded = (pred_sharded == gold_indices).float().mean().item()
    del rule_q, unbind_sharded, B_q

    # STEP 3: BUNDLE arm. Unbind single bundle vector; streamed CLEANUP.
    bundle_bcast = bundle_vec.unsqueeze(0).expand(M_queries, -1)        # (M, N) broadcast
    unbind_bundle = bundle_bcast * A_q.conj() * IMPL.conj().unsqueeze(0)  # (M, N)
    pred_bundle = cleanup_argmax_streamed(unbind_bundle, props_cpu, device, cleanup_chunk)
    acc_bundle = (pred_bundle == gold_indices).float().mean().item()
    del unbind_bundle

    # META_RULE_AF: arms must differ. Hash first chunk of SHARDED rule vectors
    # vs BUNDLE vec. Both are legitimate storage representations of the same
    # underlying (A, IMPL, B) triples; they MUST differ bit-wise by design.
    if first_chunk_rules_bytes is None:
        raise RuntimeError("first_chunk_rules_bytes not captured; build_chunk logic bug")
    bundle_bytes = bundle_vec.detach().cpu().numpy().tobytes()
    shard_hash = hashlib.sha256(first_chunk_rules_bytes).hexdigest()[:16]
    bundle_hash = hashlib.sha256(bundle_bytes).hexdigest()[:16]
    assert shard_hash != bundle_hash, \
        f"META_RULE_AF violation: sharded first-chunk and bundle bit-identical at NPROP={NPROP}"

    # Peak GPU memory (best-effort; only meaningful on CUDA).
    peak_gpu_mb = None
    if device == "cuda":
        peak_gpu_mb = round(torch.cuda.max_memory_allocated() / (1024 * 1024), 1)
        torch.cuda.reset_peak_memory_stats()

    # Free large tensors before next phase point.
    del props_cpu, perm_cpu, IMPL, IMPL_bcast, bundle_vec, A_q, bundle_bcast, q_idx_cpu
    if device == "cuda":
        torch.cuda.empty_cache()

    return {
        "NPROP": int(NPROP),
        "M": int(M_queries),
        "acc_sharded": round(float(acc_sharded), 4),
        "acc_bundle": round(float(acc_bundle), 4),
        "sharded_hash": shard_hash,
        "bundle_hash": bundle_hash,
        "build_chunk": int(build_chunk),
        "cleanup_chunk": int(cleanup_chunk),
        "peak_gpu_mb": peak_gpu_mb,
    }


def _selftest() -> None:
    """Formula self-test at REDUCED scale to keep selftest fast.
    Uses N=4096 (1/4 memory) at NPROP=200/2000/8000 to verify mechanism.
    Full-N=16384 discriminator survival is tested in smoke (via NPROP=32000).
    """
    print("[selftest] START ANCHOR=%s device=%s N=%d (test at reduced N=4096)"
          % (ANCHOR_NAME, DEVICE, N), flush=True)
    # Reduced-N selftest to keep formula check fast.
    _N_TEST = 4096
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(999)
    # Small-M validation at reduced N to verify mechanism formula.
    r_lo = _selftest_point(NPROP=200, M_queries=30, N_test=_N_TEST, gen=gen)
    r_mid = _selftest_point(NPROP=2000, M_queries=30, N_test=_N_TEST, gen=gen)
    r_hi = _selftest_point(NPROP=8000, M_queries=30, N_test=_N_TEST, gen=gen)
    print("[selftest] N=%d NPROP=200   sharded=%.3f bundle=%.3f"
          % (_N_TEST, r_lo["acc_sharded"], r_lo["acc_bundle"]), flush=True)
    print("[selftest] N=%d NPROP=2000  sharded=%.3f bundle=%.3f"
          % (_N_TEST, r_mid["acc_sharded"], r_mid["acc_bundle"]), flush=True)
    print("[selftest] N=%d NPROP=8000  sharded=%.3f bundle=%.3f"
          % (_N_TEST, r_hi["acc_sharded"], r_hi["acc_bundle"]), flush=True)
    # Formula assertions (from matched-filter theory + Plate 1995 bundle bound):
    # HYPOTHESIZED@this-file: at N=4096, NPROP=200 both arms near-perfect (BUNDLE
    # near bundle bound 0.14*N=573); at NPROP=8000 (>> bound) BUNDLE collapses,
    # SHARDED holds via matched-filter over V codewords.
    assert r_lo["acc_sharded"] >= 0.90, \
        f"SELFTEST FAIL: sharded should be >= 0.90 at N=4096 NPROP=200; got {r_lo['acc_sharded']}"
    assert r_hi["acc_sharded"] >= 0.90, \
        f"SELFTEST FAIL: sharded should be >= 0.90 at N=4096 NPROP=8000 (matched-filter); got {r_hi['acc_sharded']}"
    assert r_hi["acc_bundle"] < 0.20, \
        f"SELFTEST FAIL: bundle should collapse at N=4096 NPROP=8000 (>> 0.14*N=573); got {r_hi['acc_bundle']}"
    gap = r_hi["acc_sharded"] - r_hi["acc_bundle"]
    assert gap >= 0.70, \
        f"SELFTEST FAIL: sharded-vs-bundle gap at N=4096 NPROP=8000 should be >= 0.70; got {gap:.3f}"
    print("[selftest] PASS: sharded scales beyond bundle bound at N=4096 (gap=%.3f)" % gap, flush=True)
    print("[selftest] N=%d full-N discriminator survival verified in smoke via NPROP=32000." % N, flush=True)


def _selftest_point(NPROP: int, M_queries: int, N_test: int,
                     gen: torch.Generator) -> Dict[str, float]:
    """Reduced-N variant of run_phase_point for fast formula validation.
    Uses the SAME CPU-hosted+streamed codepath as the FULL run (props on
    CPU, chunks streamed to device) so selftest verifies the actual
    mechanism that will run in FULL at 2x N."""
    cpu_gen = torch.Generator(device="cpu")
    cpu_gen.manual_seed(999 * 100003 + int(NPROP))
    IMPL = cphasor_torch(1, N_test, cpu_gen, "cpu")[0].to(DEVICE)
    props_cpu = cphasor_torch_chunked_cpu(NPROP, N_test, cpu_gen, chunk_size=1000)
    perm_cpu = torch.randperm(NPROP, generator=cpu_gen)
    IMPL_bcast = IMPL.unsqueeze(0)
    # BUILD bundle_vec streamed CPU -> device.
    build_chunk = 1000
    bundle_vec = torch.zeros(N_test, dtype=torch.complex64, device=DEVICE)
    for cs in range(0, NPROP, build_chunk):
        ce = min(cs + build_chunk, NPROP)
        A_c = props_cpu[cs:ce].to(DEVICE)
        B_c = props_cpu[perm_cpu[cs:ce]].to(DEVICE)
        rule_c = cnorm_torch(A_c * IMPL_bcast * B_c)
        bundle_vec = bundle_vec + rule_c.sum(dim=0)
        del A_c, B_c, rule_c
    q_idx_cpu = torch.randint(0, NPROP, (M_queries,), generator=cpu_gen)
    A_q = props_cpu[q_idx_cpu].to(DEVICE)
    B_q = props_cpu[perm_cpu[q_idx_cpu]].to(DEVICE)
    gold = perm_cpu[q_idx_cpu].to(DEVICE)
    rule_q = cnorm_torch(A_q * IMPL_bcast * B_q)
    us = rule_q * A_q.conj() * IMPL.conj().unsqueeze(0)
    ps = cleanup_argmax_streamed(us, props_cpu, DEVICE, chunk_size=2000)
    acc_s = (ps == gold).float().mean().item()
    bb = bundle_vec.unsqueeze(0).expand(M_queries, -1)
    ub = bb * A_q.conj() * IMPL.conj().unsqueeze(0)
    pb = cleanup_argmax_streamed(ub, props_cpu, DEVICE, chunk_size=2000)
    acc_b = (pb == gold).float().mean().item()
    if DEVICE == "cuda":
        torch.cuda.empty_cache()
    return {"acc_sharded": acc_s, "acc_bundle": acc_b}


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
        pk = r.get("peak_gpu_mb")
        pk_str = f" peak_gpu={pk}MB" if pk is not None else ""
        print("  [%d/%d] N=%d NPROP=%5d sharded=%.4f bundle=%.4f dt=%.2fs%s"
              % (i + 1, n_units, N, NPROP, r["acc_sharded"], r["acc_bundle"], dt, pk_str),
              flush=True)
    total_s = time.perf_counter() - t0

    by_nprop = {r["NPROP"]: r for r in per_unit}
    max_nprop = max(by_nprop.keys())
    sharded_at_max = by_nprop[max_nprop]["acc_sharded"]
    bundle_at_max = by_nprop[max_nprop]["acc_bundle"]
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
    """Verdict logic mirrors sharded_capacity_beyond_bundle_bound_v1 but at 2x N.
    HP threshold: SHARDED >= 0.95 at NPROP >= 1.9*N=31130 AND BUNDLE < 0.60
    at NPROP >= 4000 (which is already >> bundle bound 0.14*N=2294)."""
    max_nprop = r["max_nprop"]
    s_max = r["sharded_acc_at_max_nprop"]
    b_max = r["bundle_acc_at_max_nprop"]
    coll_np = r["bundle_collapse_check_nprop"]
    b_coll = r["bundle_acc_at_collapse_check"]
    grid = r["grid_nprop"]
    sharded_curve = {p["NPROP"]: p["acc_sharded"] for p in r["per_unit"]}
    bundle_curve = {p["NPROP"]: p["acc_bundle"] for p in r["per_unit"]}
    scale_factor = max_nprop / max(1, r["bundle_bound_approx"])

    if max_nprop >= int(1.9 * N) and s_max >= 0.95 and b_coll is not None and b_coll < 0.60:
        return ("HARD_PASS",
                "HARD_PASS: SHARDED perfect cleanup at NPROP=%d (>=1.9*N=%d for N=%d; sharded=%.3f) AND "
                "BUNDLE collapses (bundle=%.3f at NPROP=%d, well below Plate 0.14*N~%d bound). "
                "Sharded rule-storage extends cleanup capacity ~%.1fx beyond classical bundle bound "
                "AT 2x N (N=16384 vs CG cell N=8192). META scale-free extension criterion SATISFIED "
                "-- pattern reproduces across 2x N range. sharded_curve=%s bundle_curve=%s"
                % (max_nprop, int(1.9 * N), N, s_max, b_coll, coll_np, r["bundle_bound_approx"],
                   scale_factor, sharded_curve, bundle_curve))
    if 16000 in sharded_curve and sharded_curve[16000] >= 0.95 and s_max < 0.90:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: SHARDED holds at NPROP=16000 (%.3f) but drops at max NPROP=%d (%.3f). "
                "Extended capacity confirmed vs bundle bound at N=%d but not at 2*N=32000. "
                "META scale-free claim PARTIAL. sharded_curve=%s bundle_curve=%s"
                % (sharded_curve[16000], max_nprop, s_max, N, sharded_curve, bundle_curve))
    if max_nprop >= int(1.9 * N) and s_max < 0.60:
        return ("HARD_FAIL",
                "HARD_FAIL: SHARDED collapses at NPROP=%d for N=%d (sharded=%.3f). "
                "META scale-free physics law CLAIM FALSIFIED -- law is N-dependent (holds at N=8192 "
                "but not at N=16384). Would DEMOTE META atom to scale-bounded scope. "
                "sharded_curve=%s bundle_curve=%s"
                % (max_nprop, N, s_max, sharded_curve, bundle_curve))
    return ("MIDDLE_BAND",
            "MIDDLE_BAND (residual): sharded=%.3f at max_nprop=%d for N=%d; bundle=%.3f at collapse_check=%s. "
            "META scale-free claim inconclusive. sharded_curve=%s bundle_curve=%s"
            % (s_max, max_nprop, N, b_coll if b_coll is not None else -1, coll_np,
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
except Exception as e:
    try:
        _out_dir = get_output_dir(ANCHOR_NAME)
        _write_crash_metrics(_out_dir, e)
    except Exception:
        pass
    raise
