"""Course-C FRONTIER fit-capacity CEILING probe. The oracle-capacity-ladder landed LADDER_FIT_LIMITED and the
DIRECT-DISTANCE readout CLIMBS with capacity (L0 h@10=0.140 -> L5 anchor1 k32/d8192 h@10=0.424
MEASURED@data/exp_course_c_oracle_capacity_ladder_v1/metrics.json) while the FPE bounded-kernel readout stays
flat (~0.000 on the anchor1 rungs, a bandwidth-underflow bug). The DIRECT readout is FIT-limited and STILL
CLIMBING at the ladder top rung. This cell resolves the escalate-to-strategy FORK the ladder left open:

  does the transductive DIRECT-readout ORACLE EVER fire (hits@10 -> 0.90) with enough FIT capacity,
  or does it PLATEAU = a genuine representation wall (additive/translational TransE functional form
  insufficient for the SYNONYM/IS_A CSKG relation mix at N=25752)?

This is COMPLEMENTARY to course_c_strengthened_fit_recipe_extended_ladder_v1 (in flight on remote_cpu_queue),
which isolates WHICH lever (epochs / LR / k) at MODERATE capacity (tops k48/ep450/dim8192). THIS cell pushes
the CEILING far beyond that: a 16x COORDINATE-CAPACITY sweep (k 32 -> 512) at RotatE-comparable epoch counts,
the LR fixed to 5e-3, and n_neg raised toward RotatE's 256 -- as far as capacity feasibly goes on the idle GPU.
If the still-climbing direct curve reaches oracle-fire at some capacity, escalate-capacity is the answer; if it
asymptotes below 0.90 despite the large capacity jumps, that is FRONTIER_FIT_PLATEAU_REPRESENTATION_WALL and
the signal is to change the FUNCTIONAL FORM (a strategy question, not a recipe question).

WHY the oracle-fire gate is on DIRECT (un-confounded by the broken FPE). The FPE readout's exact-0.000 on the
anchor1 rungs is a bandwidth mis-spec (ell=0.55 underflows on the standardized k-dim coords). We fold in the
median-heuristic-recalibrated FPE per rung as a DIAGNOSTIC (does the intended kernel readout recover once the
bandwidth is right), but the fire GATE is the DIRECT readout, which is the one that responds to capacity. This
keeps the ceiling question un-confounded by the readout bug.

CAPACITY LEVERS (highest-leverage first, per the KGE-convergence lit-scan in
notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md Branch 3):
  (1) COORD capacity k -- the demonstrated-strongest single lever the ladder tested (L4 k24 -> L5 k32: +0.052).
      The DIRECT readout dimension IS k, so this is the load-bearing frontier axis. Swept 32 -> 512 (16x).
  (2) EPOCHS / total dataset passes -- RotatE trained ~376-472 passes on a comparable graph; the ladder top was
      only 150. Raised to 300-400 here.
  (3) LEARNING-RATE fix -- A1_LR=0.05 (Adam) is ~1000x RotatE's published ~5e-5; fixed to 5e-3 on the frontier
      rungs (the ladder's own evidence: at lr=0.05 epochs 60->150 barely moved direct, +0.010 -- LR-too-high so
      more steps cannot REFINE).
  (4) n_neg raised 64 -> 256 (RotatE's FB15k-237-scale value).
Note: the FPE readout dim is a DIAGNOSTIC-only axis (it does NOT affect the DIRECT oracle-fire gate, which uses
only the k coordinates). It is DELIBERATELY held at 8192 (NOT pushed higher) because the FPE candidate encoding
S_all=(N,dim) complex64 is the memory OOM driver (1.69GB at dim=8192, 3.4GB at 16384) and pushing it buys the
ceiling question NOTHING -- the direct readout is the gate. This is an intentional OOM-discipline choice, stated.

RUNGS (all anchor1, minibatch adaptive, reciprocal=True, transductive; ordered cheap -> frontier):
  G0_repro_L5   k32  ep150 lr0.05 nneg64   -- Gate-D positive/regime control: MUST reproduce ladder L5 direct
                                              h@10=0.424 (invocation/regime integrity; also the POSITIVE control
                                              proving the direct-readout metric CAN reach a non-trivial value).
  G1_k64_ep300  k64  ep300 lr5e-3 nneg128  -- 2x coord capacity + fixed LR + more epochs + more negatives.
  G2_k128_ep300 k128 ep300 lr5e-3 nneg256  -- 4x coord capacity.
  G3_k256_ep400 k256 ep400 lr5e-3 nneg256  -- 8x coord capacity + RotatE-comparable epochs.
  G4_k512_ep400 k512 ep400 lr5e-3 nneg256  -- 16x coord capacity (the ceiling rung; budget-guarded).
Plus a RANDOM must-fail control (untrained coords -> chance) so the metric is provably NOT structurally frozen
and CAN move (near-0 here, ~0.42 when fit). Direct readout is degree-stratified (LOW/MID/HIGH gold-tail-degree
tertile) to localize WHERE the fit breaks.

VERDICT FORK (explicit; gated on DIRECT):
  FRONTIER_FIT_FIRES                        -- oracle_direct >= 0.90 at SOME rung -> the fit is REACHABLE with
                                               capacity; escalate-capacity is the answer; license the Branch-1
                                               decisive 3-seed re-run at that config (swap the decisive cell's
                                               fit_transe_coords -> fit_kge_anchor1 at the firing (k, epochs)).
  FRONTIER_FIT_PLATEAU_REPRESENTATION_WALL  -- oracle_direct asymptotes below 0.90 (top frontier rung does NOT
                                               improve on the prior best by >= PLATEAU_EPS) despite the 16x
                                               coord-capacity jump, and the core is dense -> a genuine FIT /
                                               REPRESENTATION wall; escalate to STRATEGY (change the functional
                                               form; the additive TransE form may be a poor fit for CSKG's
                                               SYNONYM/IS_A mix), do NOT keep cranking capacity.
  FRONTIER_FIT_CLIMBING_UNDER_CAPACITY      -- not fired yet BUT the highest-capacity rung is still the best and
                                               improved >= PLATEAU_EPS on the prior: capacity is STILL buying
                                               accuracy at the tested ceiling. ONE more capacity rung MAY be
                                               warranted but that is a STRATEGY call (do NOT auto-escalate
                                               forever); report the trajectory.
Integrity gates take precedence: RANDOM control must stay < 0.05 (else HARD_FAIL_CONTROL_METRIC_BROKEN); G0 must
reproduce ladder L5 within tol (else HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH).

## Compute architecture
class: (c) MIXED. CSKG assembly + degree-map = symbolic graph traversal (sequential-CPU correct, same as the VET
+ ladder apparatus, ONE assembly reused across all rungs -> memory FLAT). Coord fit = MINIBATCH SGD (torch,
vectorized -- NOT a numpy Python loop, so the GPU-batching mandate is satisfied); readout = batched/query-chunked
matmul. SINGLE seed by design (this is a capacity-CEILING DIAGNOSTIC, like the ladder + strengthened cell, NOT
the decisive 3-seed re-run; the PLATEAU verdict is a TRAJECTORY across many k, robust to a single seed).
Routing: overnight_queue (GPU). GPU is the honest routing to reach a HIGHER ceiling than CPU feasibly can: the
frontier rungs (k up to 512, epochs up to 400) are a large number of vectorized gradient steps; on CPU each
rung would take many hours (the CPU ladder ran only to k32/ep2400 in 5414s). The fit is device-parameterized
(fit_kge_anchor1 threads `device`), not numpy-bound, so the GPU can actually be fed.
STRICT OOM DISCIPLINE (this family OOM'd 3x historically):
  - Peak drivers bounded and stated: (a) fit negative tensor (batch, n_neg, k) -> ADAPTIVE batch keeps it
    <= ~1.0GB fwd (~2GB with autograd) at every rung; (b) FPE S_all=(N, dim) complex64 -> dim CAPPED at 8192
    (1.69GB, freed between the two FPE readouts). NEVER materializes an [N x N] map (25.7k x 25.7k = 2.6GB fp32
    is AVOIDED; all scoring is (nq=500, N) query-chunked at chunk=256 -> 26MB tiles).
  - Peak estimate at the biggest rung (k512, dim8192): ~1.69GB (FPE) + fit tensors (~160MB) < 2GB, well under
    the 6GB ship ceiling on the 8GB card.
  - PER-RUNG ATOMIC CHECKPOINT: metrics.json is atomically re-written after EVERY rung (tmp + os.replace), so a
    queue-timeout hard-kill preserves all completed rungs (the verdict logic degrades gracefully over whatever
    landed). INTERNAL total-budget guard skips remaining rungs (recorded as SKIPPED_INTERNAL_BUDGET, never
    silent) if elapsed would blow the queue timeout, guaranteeing a clean atomic finalize.
  - MANDATORY >= 2-seed memory smoke BEFORE full: the --smoke mode runs the FRONTIER top-config (highest k) at
    2 seeds on the reduced CSKG slice so peak GPU allocation is exercised ACROSS seeds (catches the single-seed-
    masked OOM class) before the FULL is spent.
Storage strategy: no_storage (KGE coordinate fit, not an associative-memory store).

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity: tmp_replace (write_metrics + os.replace; PLUS per-rung atomic checkpoint).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - start_marker + crash_diagnostic + heartbeat present.
# - cell_chunked: false (single seed by design; the >=2-seed MEMORY smoke is the OOM gate, not a science multi-seed).
# - discriminator: oracle_direct-fires (>=0.90) is the gate; RANDOM control MUST stay < 0.05 (must-fail fires);
#   Gate-D G0 MUST reproduce ladder L5=0.424 (invocation/regime integrity). No vacuous auto-pass.
# - validity preflight DECLARED in self_test() (positive_control / metric_moves / full_gates_exercised /
#   negative_control_margin) via experiments._validity_preflight -- WARN-mode compliant, ENFORCE-ready.
# - progress_logging: print_flush_true (per-rung + per-fit flush; line-buffered stdout; timeout_s >= 1800).
# - no numbers hard-coded as claims; every reported value is MEASURED@this metrics.json at run time. The single
#   reference constant L5_DIRECT_REF=0.424 is tagged MEASURED@the ladder metrics and used ONLY as the Gate-D
#   reproduce target.
"""

import argparse
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments._kge_anchor1_fit import fit_kge_anchor1  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import (  # noqa: E402
    Graph, build_ids,
)
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_operator_fix_ssp_phase_rotation_replay_v1 import (  # noqa: E402
    make_fpe_basis,
)
# Reuse the v1 map-builder symbolic + readout apparatus verbatim (identical code path as the decisive run and
# the ladder). Same gate thresholds, same stratification, same filtered-hits math.
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores,
    geom_scores, _standardize, stratify_by_tail_degree, per_stratum_hits,
    FPE_ELL, PRIMARY_K, STRATA,
)

ANCHOR_NAME = "course_c_frontier_fit_capacity_ceiling_v1"

ORACLE_FIRE = 0.90          # oracle_direct hits@10 threshold that makes the reasoning question askable
N_ORACLE_HOLD = 500         # random held-out edges folded into the transductive ORACLE fit + scored for recovery
FPE_SCORE_CHUNK = 256       # query-chunk for the direct + FPE readouts (bounds peak to (chunk, N) tiles)
FPE_DIM = 8192              # FPE readout dim (DIAGNOSTIC only; capped -- S_all=(N,dim) is the OOM driver)

# Gate-D reproduce target + integrity thresholds (MEASURED off the ladder metrics).
L5_DIRECT_REF = 0.424       # MEASURED@data/exp_course_c_oracle_capacity_ladder_v1/metrics.json:ladder[5].oracle_direct_h10
GATE_D_TOL = 0.10           # |G0_direct - L5_DIRECT_REF| > tol => HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH
RANDOM_CTRL_MAX = 0.05      # RANDOM untrained control must stay below this (must-fail fires; metric can move)
PLATEAU_EPS = 0.03          # top frontier rung must improve on the prior best by >= this to count as "still climbing"
DENSE_AVGDEG = 30.0         # core avg-degree >= this rules out data-sparsity (escalation gate)

# OOM budget for the fit negative tensor (batch, n_neg, k): adaptive batch keeps it <= this many bytes (fwd).
NEG_TENSOR_BUDGET_BYTES = 1.0e9
MAX_BATCH = 8192
MIN_BATCH = 256
# Internal wall-budget: skip remaining rungs (recorded, not silent) if elapsed would blow the queue timeout,
# so the cell always reaches a clean atomic finalize before a hard kill. Sized under the FULL queue --timeout.
INTERNAL_TOTAL_BUDGET_S = 13000.0

# Frontier ladder (all anchor1, reciprocal=True, transductive). (label, k, fpe_dim, epochs, lr, n_neg).
# dim = FPE readout dim (DIAGNOSTIC only; does NOT affect the primary DIRECT readout nor the fit).
FULL_LADDER = [
    ("G0_repro_L5",   32,  FPE_DIM, 150, 0.05,  64),   # Gate-D + positive control: reproduce ladder L5 direct=0.424
    ("G1_k64_ep300",  64,  FPE_DIM, 300, 5e-3, 128),   # 2x coord capacity, fixed LR, more epochs+negatives
    ("G2_k128_ep300", 128, FPE_DIM, 300, 5e-3, 256),   # 4x coord capacity
    ("G3_k256_ep400", 256, FPE_DIM, 400, 5e-3, 256),   # 8x coord capacity, RotatE-comparable epochs
    ("G4_k512_ep400", 512, FPE_DIM, 400, 5e-3, 256),   # 16x coord capacity (ceiling rung; budget-guarded)
]
# Reduced REMOTE MEMORY smoke: FRONTIER top-config (highest k) at 2 SEEDS on a tiny CSKG slice so peak GPU
# allocation is exercised ACROSS seeds (catches the single-seed-masked OOM class) before the FULL is spent.
SMOKE_LADDER = [
    ("G4s_k512_seed7",  512, 1024, 8, 5e-3, 256),
    ("G4s_k512_seed17", 512, 1024, 8, 5e-3, 256),
]

FULL_CFG = dict(seed=7, cskg_max_lines=0, k_core=12, cskg_max_nodes=0, min_support=10, min_conf=0.10,
                ladder="full")
SMOKE_CFG = dict(seed=7, cskg_max_lines=800000, k_core=3, cskg_max_nodes=3000, min_support=2, min_conf=0.05,
                 ladder="smoke")


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _adaptive_batch(k, n_neg):
    """Batch that keeps the fit negative tensor (batch, n_neg, k) fp32 forward footprint <= NEG_TENSOR_BUDGET_BYTES.
    Clamped to [MIN_BATCH, MAX_BATCH]. Larger k / n_neg -> smaller batch -> more steps but bounded peak memory."""
    b = int(NEG_TENSOR_BUDGET_BYTES / (float(n_neg) * float(k) * 4.0))
    return max(MIN_BATCH, min(MAX_BATCH, b))


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_checkpoint(output_dir, payload):
    """Atomically (re)write metrics.json so a hard-kill preserves whatever rungs have completed (OOM discipline)."""
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def _fit_anchor1(train_int, N, n_rel, k, epochs, lr, n_neg, batch, device, seed, hold=None):
    """Transductive anchor1 fit threading the frontier levers (k / epochs / lr / n_neg / adaptive batch)."""
    return fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold,
                           reciprocal=True, lr=lr, n_neg=n_neg, batch_size=batch)


def _direct_scores(X, D, hold_edges, device, chunk=FPE_SCORE_CHUNK):
    """Direct-distance readout: score = -||x_hat - X_c|| on standardized coords (the fit-limited reference readout;
    the readout that RESPONDS to capacity per the ladder; the oracle-fire GATE). Query-chunked; never (N x N)."""
    Xn, Dn = _standardize(X, D)
    h = torch.from_numpy(hold_edges[:, 0]).long().to(device)
    r = torch.from_numpy(hold_edges[:, 1]).long().to(device)
    x_hat = Xn[h] + Dn[r]
    nq = x_hat.shape[0]
    n_ent = Xn.shape[0]
    out = torch.empty((nq, n_ent), dtype=torch.float32)
    for s in range(0, nq, chunk):
        e = min(s + chunk, nq)
        d = torch.cdist(x_hat[s:e], Xn)
        out[s:e] = (-d).detach().to("cpu")
        del d
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return out


def _median_heuristic_ell(X, D, sample_n=2000, seed=0):
    """Median-heuristic RBF bandwidth on the STANDARDIZED coords geom_scores uses (Garreau et al. 2017). The
    pre-registered FPE_ELL=0.55 is mis-scaled: after _standardize, typical pairwise distance in k dims is
    ~sqrt(2k), so exp(-||x-y||^2 / (2*0.55^2)) UNDERFLOWS to ~0 for nearly all pairs -> degenerate (exactly-0.000)
    FPE ranking. Returns ell = median pairwise distance so the kernel is informative (Branch-2 readout-fix)."""
    Xn, _ = _standardize(X, D)
    n = Xn.shape[0]
    g = torch.Generator(device="cpu").manual_seed(seed * 333 + 1)
    idx = torch.randperm(n, generator=g)[:min(sample_n, n)]
    S = Xn[idx].detach().float().cpu()
    d = torch.pdist(S)
    ell = float(torch.median(d).item())
    return max(ell, 1e-6)


def _fpe_health(scores):
    """Structural-bug detector for the FPE readout: near-zero std / range or non-finite scores means the kernel
    collapsed to a constant (bandwidth underflow) or NaN -- degenerate, NOT merely under-capacity."""
    sc = scores.detach().float()
    finite = bool(torch.isfinite(sc).all().item())
    std = float(sc.std().item()) if finite else float("nan")
    rng = float((sc.max() - sc.min()).item()) if finite else float("nan")
    return dict(finite=finite, std=round(std, 8), rng=round(rng, 8))


def _random_control(N, n_rel, k, hold_edges, all_true, device, seed):
    """Must-fail control: UNTRAINED random coords (anchor1's own init distribution, no fit) -> chance ranking.
    Proves the direct-readout metric is NOT structurally frozen and CAN move (near-0 here, ~0.42 when fit)."""
    g = torch.Generator(device="cpu").manual_seed(seed * 911 + 3)
    X = (torch.randn(N, k, generator=g) * 0.1).to(device)
    D = (torch.randn(n_rel, k, generator=g) * 0.1).to(device)
    direct = _direct_scores(X, D, hold_edges, device)
    dm = filtered_hits_from_scores(direct, hold_edges, all_true)
    del X, D, direct
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return round(float(dm["hits@%d" % PRIMARY_K]), 4), round(float(dm["mrr"]), 4)


def _score_one_rung(label, k, dim, epochs, lr, n_neg, train_int, N, n_rel,
                    hold_oracle, strat, all_true, device, seed):
    """Fit the transductive anchor1 ORACLE at this rung's capacity, read it under DIRECT (the fire gate) + FPE
    (prereg ell=0.55 AND median-heuristic, diagnostic). Returns a fully-populated row dict."""
    tp = time.perf_counter()
    batch = _adaptive_batch(k, n_neg)
    X_or, D_or = _fit_anchor1(train_int, N, n_rel, k, epochs, lr, n_neg, batch, device, seed, hold=hold_oracle)

    # DIRECT-DISTANCE readout (primary; the fire gate; the readout that responds to capacity).
    direct = _direct_scores(X_or, D_or, hold_oracle, device)
    direct_m = filtered_hits_from_scores(direct, hold_oracle, all_true)
    direct_strat = per_stratum_hits(direct, hold_oracle, strat, all_true)

    # FPE readout at the PRE-REGISTERED bandwidth (ell=0.55) -- the intended geometric readout, diagnostic.
    W0 = make_fpe_basis(k, dim, FPE_ELL, device, seed)
    fpe = geom_scores(X_or, D_or, W0, hold_oracle, device)
    fpe_m = filtered_hits_from_scores(fpe, hold_oracle, all_true)
    fpe_hlth = _fpe_health(fpe)

    # READOUT-FIX diagnostic: FPE at the MEDIAN-HEURISTIC bandwidth on THIS rung's standardized coords.
    ell_mh = _median_heuristic_ell(X_or, D_or, seed=seed)
    W1 = make_fpe_basis(k, dim, ell_mh, device, seed)
    fpe_mh = geom_scores(X_or, D_or, W1, hold_oracle, device)
    fpe_mh_m = filtered_hits_from_scores(fpe_mh, hold_oracle, all_true)
    fpe_mh_hlth = _fpe_health(fpe_mh)

    elapsed = round(time.perf_counter() - tp, 1)
    row = dict(label=label, fit_kind="anchor1", k=int(k), fpe_dim=int(dim), epochs=int(epochs), lr=float(lr),
               n_neg=int(n_neg), batch=int(batch), n_coord_params=int(N * k),
               oracle_direct_h10=round(direct_m["hits@%d" % PRIMARY_K], 4),
               oracle_direct_h1=round(direct_m["hits@1"], 4), oracle_direct_mrr=round(direct_m["mrr"], 4),
               oracle_direct_strat={s: direct_strat[s] for s in STRATA},
               oracle_fpe_h10=round(fpe_m["hits@%d" % PRIMARY_K], 4),
               oracle_fpe_h1=round(fpe_m["hits@1"], 4), oracle_fpe_mrr=round(fpe_m["mrr"], 4),
               oracle_fpe_medht_h10=round(fpe_mh_m["hits@%d" % PRIMARY_K], 4),
               oracle_fpe_medht_mrr=round(fpe_mh_m["mrr"], 4),
               ell_prereg=FPE_ELL, ell_medht=round(ell_mh, 4),
               fpe_prereg_health=fpe_hlth, fpe_medht_health=fpe_mh_hlth,
               fires_direct=bool(direct_m["hits@%d" % PRIMARY_K] >= ORACLE_FIRE),
               fires_fpe=bool(fpe_m["hits@%d" % PRIMARY_K] >= ORACLE_FIRE),
               fires_fpe_medht=bool(fpe_mh_m["hits@%d" % PRIMARY_K] >= ORACLE_FIRE),
               elapsed_s=elapsed)
    _log("RUNG %s: k=%d ep=%d lr=%g nneg=%d batch=%d | DIRECT h@10=%.3f (low/mid/high=%.3f/%.3f/%.3f) | "
         "FPE(0.55) h@10=%.3f std=%.2e | FPE(medht=%.2f) h@10=%.3f | fires_direct=%s (%.1fs)"
         % (label, k, epochs, lr, n_neg, batch, row["oracle_direct_h10"], direct_strat["low"]["hits"],
            direct_strat["mid"]["hits"], direct_strat["high"]["hits"], row["oracle_fpe_h10"],
            fpe_hlth["std"], ell_mh, row["oracle_fpe_medht_h10"], row["fires_direct"], elapsed))
    del W0, W1, X_or, D_or, fpe, fpe_mh, direct
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return row


def _finalize_verdict(rows, skipped, rand_direct, rand_mrr, core_avgdeg, prov, N, n_rel, run_mode, t0, device, seed):
    """Compute the FIRES vs PLATEAU vs CLIMBING verdict over whatever rungs completed (degrades gracefully)."""
    core_dense = bool(core_avgdeg >= DENSE_AVGDEG)
    control_ok = bool(rand_direct < RANDOM_CTRL_MAX)
    g0 = next((r for r in rows if r["label"] == "G0_repro_L5"), None)
    gate_d_ok = bool(g0 is not None and abs(g0["oracle_direct_h10"] - L5_DIRECT_REF) <= GATE_D_TOL)

    best = max(rows, key=lambda r: r["oracle_direct_h10"]) if rows else None
    firing = next((r for r in rows if r["fires_direct"]), None)

    # frontier trajectory (exclude the G0 reproduce control).
    frontier = [r for r in rows if r["label"] != "G0_repro_L5"]
    climbing = False
    if len(frontier) >= 2:
        top = max(frontier, key=lambda r: r["oracle_direct_h10"])
        last = frontier[-1]
        prev_best = max([r["oracle_direct_h10"] for r in frontier if r is not last], default=0.0)
        climbing = bool(top is last and (last["oracle_direct_h10"] - prev_best) >= PLATEAU_EPS)

    # capacity curve for the report (k vs coord-params vs direct hits@10).
    capacity_curve = [dict(label=r["label"], k=r["k"], n_coord_params=r["n_coord_params"],
                           oracle_direct_h10=r["oracle_direct_h10"]) for r in rows]

    if not rows:
        verdict = "HARD_FAIL_NO_RUNGS_COMPLETED"
        vm = "No rungs completed before the budget/timeout; nothing to interpret."
    elif not control_ok:
        verdict = "HARD_FAIL_CONTROL_METRIC_BROKEN"
        vm = ("MUST-FAIL CONTROL FIRED: RANDOM untrained coords scored oracle_direct h@10=%.4f (>= %.2f). The "
              "direct-readout metric is leaking / structurally frozen-high; no rung result is trustworthy."
              % (rand_direct, RANDOM_CTRL_MAX))
    elif not gate_d_ok:
        verdict = "HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH"
        vm = ("GATE-D FAILED: G0_repro_L5 (config identical to ladder L5) scored oracle_direct h@10=%.4f but L5 "
              "measured %.3f (tol %.2f). The anchor1 fit invocation drifted from the ladder; frontier rungs are "
              "suspect. Reconcile before trusting the ceiling read."
              % (g0["oracle_direct_h10"] if g0 else -1.0, L5_DIRECT_REF, GATE_D_TOL))
    elif firing is not None:
        verdict = "FRONTIER_FIT_FIRES"
        vm = ("FIT FIRES: oracle_direct h@10=%.3f >= %.2f at %s (k=%d ep=%d lr=%g nneg=%d, %.1fs). The transductive "
              "ORACLE memorizes its held-out edges at sufficient capacity -> the fit is REACHABLE and ESCALATE-"
              "CAPACITY is the answer. License the Branch-1 decisive 3-seed re-run at this config (SWAP the "
              "decisive cell fit_transe_coords -> fit_kge_anchor1 at k=%d ep=%d). FPE at this rung: prereg(0.55)="
              "%.3f, median-heuristic=%.3f (fires_medht=%s) -- use median-heuristic FPE (or direct) as the "
              "production readout."
              % (firing["oracle_direct_h10"], ORACLE_FIRE, firing["label"], firing["k"], firing["epochs"],
                 firing["lr"], firing["n_neg"], firing["elapsed_s"], firing["k"], firing["epochs"],
                 firing["oracle_fpe_h10"], firing["oracle_fpe_medht_h10"], firing["fires_fpe_medht"]))
    elif climbing and core_dense:
        verdict = "FRONTIER_FIT_CLIMBING_UNDER_CAPACITY"
        vm = ("STILL CLIMBING, NOT fired: best oracle_direct h@10=%.3f at %s (< %.2f); the HIGHEST-capacity "
              "frontier rung is the best and improved >= %.2f on the prior, so capacity is STILL buying direct-"
              "readout accuracy at the tested ceiling (k up to %d). Core dense (avgdeg=%.1f). ONE more capacity "
              "rung MAY be warranted but this is a STRATEGY call -- do NOT auto-escalate forever; report the "
              "trajectory (functional-form-change vs more-capacity is the open question)."
              % (best["oracle_direct_h10"], best["label"], ORACLE_FIRE, PLATEAU_EPS,
                 max(r["k"] for r in frontier), core_avgdeg))
    else:
        verdict = "FRONTIER_FIT_PLATEAU_REPRESENTATION_WALL"
        vm = ("PLATEAU / REPRESENTATION WALL: across a %dx coordinate-capacity jump (k=%d -> k=%d) at RotatE-"
              "comparable epochs + fixed LR + n_neg up to 256, the transductive DIRECT-readout oracle ASYMPTOTES "
              "at oracle_direct h@10=%.3f (best %s) << %.2f -- the top frontier rung did NOT improve on the prior "
              "best by >= %.2f. Core is dense (avgdeg=%.1f -> 'not enough data' ruled out). Un-confounded by the "
              "FPE readout (the fire gate is the WORKING direct readout, not the broken FPE). This is a genuine "
              "FIT / REPRESENTATION wall: the additive/translational TransE functional form may be a poor fit for "
              "CSKG's SYNONYM/IS_A relation mix, or a genuine k-dim coord-capacity ceiling at N=%d. ESCALATE TO "
              "STRATEGY (change the FUNCTIONAL FORM, not the recipe) -- do NOT keep cranking capacity."
              % (int(round(max(r["k"] for r in frontier) / min(r["k"] for r in frontier))) if frontier else 1,
                 min(r["k"] for r in rows), max(r["k"] for r in rows), best["oracle_direct_h10"], best["label"],
                 ORACLE_FIRE, PLATEAU_EPS, core_avgdeg, N))

    return dict(verdict=verdict, verdict_msg=vm, summary=vm[:200], run_mode=run_mode,
                elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), seed=seed,
                N=int(N), n_rel=int(n_rel), oracle_fire_threshold=ORACLE_FIRE,
                cskg_provenance=prov, core_avgdeg=core_avgdeg, core_dense=core_dense,
                ladder=rows, skipped_rungs=skipped, n_rungs_completed=len(rows),
                n_rungs_planned=len(FULL_LADDER), capacity_curve=capacity_curve,
                random_control=dict(oracle_direct_h10=rand_direct, oracle_direct_mrr=rand_mrr,
                                    max_allowed=RANDOM_CTRL_MAX, control_ok=control_ok),
                gate_d=dict(l5_direct_ref=L5_DIRECT_REF, g0_direct=(g0["oracle_direct_h10"] if g0 else None),
                            tol=GATE_D_TOL, gate_d_ok=gate_d_ok),
                firing_config=firing, best_config=best, climbing=climbing,
                neg_tensor_budget_bytes=NEG_TENSOR_BUDGET_BYTES,
                internal_total_budget_s=INTERNAL_TOTAL_BUDGET_S)


def run_ladder(run_mode, device):
    cfg = FULL_CFG if run_mode == "full" else SMOKE_CFG
    ladder = FULL_LADDER if cfg["ladder"] == "full" else SMOKE_LADDER
    seed = cfg["seed"]
    t0 = time.perf_counter()
    out_dir = get_output_dir(ANCHOR_NAME)

    if not _ensure_cskg():
        return dict(verdict="HARD_FAIL", verdict_msg="CSKG data absent and self-acquire failed",
                    summary="cskg missing", elapsed_s=time.perf_counter() - t0)

    train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
        cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
    core_avgdeg = float(prov["core_avgdeg"])
    _log("cskg core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d train=%d test=%d"
         % (prov["n_core_nodes"], prov["n_core_edges"], core_avgdeg, prov["n_rel_tokens"],
            prov["n_train"], prov["n_test"]))

    ent2i, rel2i = build_ids(train_lbl, valid_lbl, test_lbl)
    N = len(ent2i)
    n_rel = len(rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    valid_int = _to_int_edges(valid_lbl, ent2i, rel2i)
    test_int = _to_int_edges(test_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, valid_int, test_int)

    gd = Graph(train_lbl, ent2i, rel2i)  # degree map for weak-point-localization stratification

    rng = np.random.default_rng(seed * 100057 + 7)
    sel = rng.permutation(test_int.shape[0])[:min(N_ORACLE_HOLD, test_int.shape[0])]
    hold_oracle = test_int[sel].copy()
    strat, tert = stratify_by_tail_degree(hold_oracle, gd.node_degree)
    _log("oracle held-out n=%d (of %d test); N_candidates=%d; deg-tertile bounds=%s"
         % (hold_oracle.shape[0], test_int.shape[0], N, str(tert)))

    # Must-fail control FIRST (cheap; establishes the metric floor + that it can move).
    rand_direct, rand_mrr = _random_control(N, n_rel, 32, hold_oracle, all_true, device, seed)
    _log("RANDOM control: oracle_direct h@10=%.4f (must stay < %.2f); mrr=%.4f"
         % (rand_direct, RANDOM_CTRL_MAX, rand_mrr))

    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag,
                                "elapsed_s": time.perf_counter() - t0}) + "\n")

    rows = []
    skipped = []
    for (label, k, dim, epochs, lr, n_neg) in ladder:
        # Internal wall-budget guard: never enter a rung that would risk a hard-kill before the atomic finalize.
        if (time.perf_counter() - t0) >= INTERNAL_TOTAL_BUDGET_S:
            skipped.append(dict(label=label, k=int(k), epochs=int(epochs), failure_class="SKIPPED_INTERNAL_BUDGET"))
            _log("SKIP %s: internal budget %.0fs exceeded (elapsed=%.0fs); recorded, not silent."
                 % (label, INTERNAL_TOTAL_BUDGET_S, time.perf_counter() - t0))
            continue
        row = _score_one_rung(label, k, dim, epochs, lr, n_neg, train_int, N, n_rel,
                              hold_oracle, strat, all_true, device, seed)
        rows.append(row)
        _hb(label)
        # PER-RUNG ATOMIC CHECKPOINT: preserve completed rungs against a queue-timeout hard-kill.
        ckpt = _finalize_verdict(rows, skipped, rand_direct, rand_mrr, core_avgdeg, prov, N, n_rel,
                                 run_mode, t0, device, seed)
        ckpt["verdict_provisional"] = True
        _atomic_checkpoint(out_dir, ckpt)

    final = _finalize_verdict(rows, skipped, rand_direct, rand_mrr, core_avgdeg, prov, N, n_rel,
                             run_mode, t0, device, seed)
    final["deg_tertile_bounds"] = tert
    return final


def _run_selftest(device):
    """LIGHTWEIGHT ship-gate self-test: exercises the EXACT frontier code path (_fit_anchor1 threading k/lr/n_neg
    + adaptive batch -> _direct_scores fire gate + FPE prereg/median-heuristic diagnostic + per_stratum_hits +
    _random_control) on a TINY SYNTHETIC functional graph -- NO CSKG, seconds, exits 0/1. A clean functional
    relation t=(h+off_r)%N is trivially memorizable, so the transductive ORACLE must recover it under DIRECT
    (a real discriminator with margin), AND the RANDOM control must stay near chance over >=3 seeds (metric can
    move + must-fail is deterministic). DECLARES the 4 validity-preflight checks (WARN-mode; ENFORCE-ready)."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(0)
    N = 120
    n_rel = 4
    k = 8
    dim = 256
    epochs = 200          # memorizing regime for the tiny graph (the LR/k levers are tested in the FULL ladder,
    # not the ship gate; the gate only proves the code path + that the fit CAN memorize + the controls fire)
    offs = rng.integers(1, N, size=n_rel)
    h = rng.integers(0, N, size=400)
    r = rng.integers(0, n_rel, size=400)
    t = (h + offs[r]) % N
    edges = np.stack([h, r, t], axis=1).astype(np.int64)
    hold = edges[-40:].copy()
    train_int = edges[:-40].copy()
    all_true = build_true_by_hr_int(edges)
    strat, _tert = stratify_by_tail_degree(hold, {i: 1 for i in range(N)})

    batch = _adaptive_batch(k, 64)
    X, D = _fit_anchor1(train_int, N, n_rel, k, epochs, 0.05, 64, batch, device, 7, hold=hold)
    direct = _direct_scores(X, D, hold, device)
    direct_m = filtered_hits_from_scores(direct, hold, all_true)
    _ = per_stratum_hits(direct, hold, strat, all_true)          # exercise stratification code path
    direct_h10 = float(direct_m["hits@%d" % PRIMARY_K])

    # FPE readouts (prereg + median-heuristic recalibration) -- exercise both readout paths + health.
    W = make_fpe_basis(k, dim, FPE_ELL, device, 7)
    fpe_m = filtered_hits_from_scores(geom_scores(X, D, W, hold, device), hold, all_true)
    fpe_h10 = float(fpe_m["hits@%d" % PRIMARY_K])
    ell_mh = _median_heuristic_ell(X, D, seed=7)
    fpe_mh_sc = geom_scores(X, D, make_fpe_basis(k, dim, ell_mh, device, 7), hold, device)
    _ = _fpe_health(fpe_mh_sc)
    fpe_mh_h10 = float(filtered_hits_from_scores(fpe_mh_sc, hold, all_true)["hits@%d" % PRIMARY_K])

    # RANDOM must-fail control over >=3 seeds (determinism + margin). Also the metric-moves null anchor.
    rand_scores = [_random_control(N, n_rel, k, hold, all_true, device, s)[0] for s in (7, 17, 23)]
    rand_direct = rand_scores[0]

    finite = bool(direct_h10 == direct_h10 and fpe_h10 == fpe_h10 and fpe_mh_h10 == fpe_mh_h10
                  and all(rs == rs for rs in rand_scores))
    fires = bool(direct_h10 >= 0.5)            # transductive memorization on a tiny clean functional graph
    control_low = bool(max(rand_scores) < 0.30)
    SELFTEST_FIRE_BAR = 0.5

    # Exercise the FULL fail-closed gates at self-test scale (Gate-D reproduce-consistency + RANDOM must-fail).
    exercised_gates = set()
    #   RANDOM must-fail gate (analog of the FULL random_control gate).
    exercised_gates.add("random_control_mustfail")
    #   Gate-D reproduce logic: refit with the SAME seed/config, assert reproducibility within tol (invocation
    #   integrity -- the same fail-closed comparison the FULL runs against ladder L5, exercised on tiny inputs).
    X2, D2 = _fit_anchor1(train_int, N, n_rel, k, epochs, 0.05, 64, batch, device, 7, hold=hold)
    direct2_h10 = float(filtered_hits_from_scores(_direct_scores(X2, D2, hold, device), hold, all_true)["hits@%d" % PRIMARY_K])
    gate_d_reproduces = bool(abs(direct2_h10 - direct_h10) <= GATE_D_TOL)
    exercised_gates.add("gate_d_regime_reproduce")

    ok_pre = run_validity_preflight([
        # 1. HARD-PASS bar achievable: the transductive ORACLE (positive control) clears the self-test fire bar.
        {"kind": "positive_control", "positive_control_passed_headline_gate": fires,
         "control_name": "transductive_oracle_direct", "headline_name": "oracle_direct_fire_bar_0.5"},
        # 2. DIRECT readout MOVES from the null (untrained RANDOM) to the known-good (trained ORACLE).
        {"kind": "metric_moves", "metric_name": "oracle_direct_h10",
         "before": rand_direct, "after": direct_h10},
        # 2b. The median-heuristic-recalibrated FPE readout MOVES vs the untrained null too (readout not frozen).
        {"kind": "metric_moves", "metric_name": "oracle_fpe_medht_h10",
         "before": 0.0, "after": fpe_mh_h10, "flag_exact_zero": True},
        # 3. Every FULL fail-closed gate fires at tiny self-test scale.
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["random_control_mustfail", "gate_d_regime_reproduce"],
         "exercised_gates": exercised_gates},
        # 4. Must-fail RANDOM control fails DETERMINISTICALLY over >=3 seeds with margin.
        {"kind": "negative_control_margin", "control_scores": rand_scores,
         "headline_threshold": SELFTEST_FIRE_BAR, "higher_is_pass": True, "margin": 0.05,
         "control_name": "random_untrained_coords"},
    ], run_mode="self_test")

    ok = bool(finite and fires and control_low and gate_d_reproduces)
    verdict = "SELFTEST_PASS" if ok else "SELFTEST_FAIL"
    vm = ("SELFTEST synthetic functional graph N=%d: oracle_direct h@10=%.3f (>=0.50 req), RANDOM direct (3 "
          "seeds)=%s (<0.30 req), FPE(0.55)=%.3f FPE(medht)=%.3f; gate_d_reproduces=%s; validity_preflight_ok=%s; "
          "_fit_anchor1(k/lr/nneg)+adaptive_batch + direct/FPE/stratify/control code path runs; ok=%s"
          % (N, direct_h10, str(rand_scores), fpe_h10, fpe_mh_h10, gate_d_reproduces, ok_pre, ok))
    _log(vm)
    return dict(verdict=verdict, verdict_msg=vm, summary=vm[:200], run_mode="self_test",
                elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device),
                selftest=dict(oracle_direct_h10=round(direct_h10, 4), oracle_fpe_h10=round(fpe_h10, 4),
                              oracle_fpe_medht_h10=round(fpe_mh_h10, 4), random_direct_seeds=rand_scores,
                              gate_d_reproduces=gate_d_reproduces, validity_preflight_ok=bool(ok_pre),
                              finite=finite, fires=fires, control_low=control_low))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if (args.self_test or args.run_mode == "self_test") else (
        "smoke" if args.smoke else args.run_mode)
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (args.device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        device = torch.device("cpu")
    else:
        want_cuda = (args.device in ("auto", "cuda")) or (env_dev == "cuda")
        device = torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, run_mode, len(FULL_LADDER) if run_mode == "full" else len(SMOKE_LADDER))
    _log("device=%s cuda=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))
    if run_mode == "self_test":
        metrics = _run_selftest(device)                     # tiny synthetic; NO CSKG; seconds; ship-gate path
        write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics.get("elapsed_s", 0.0)}])
        _log("VERDICT: %s" % metrics.get("verdict_msg", ""))
        if metrics.get("verdict") != "SELFTEST_PASS":
            raise SystemExit(1)
        return
    metrics = run_ladder(run_mode, device)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics.get("elapsed_s", 0.0)}])
    _log("VERDICT: %s" % metrics.get("verdict_msg", ""))
    _log("done (%.1fs)" % metrics.get("elapsed_s", 0.0))


if __name__ == "__main__":
    _od = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
