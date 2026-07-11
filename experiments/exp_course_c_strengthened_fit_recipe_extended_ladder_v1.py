"""Course-C Branch-3 escalation: STRENGTHENED-FIT extended ladder. The oracle-capacity-ladder landed
LADDER_FIT_LIMITED -- the transductive ORACLE did NOT fire at any of 6 rungs, and it is FIT-limited not
readout-limited: the DIRECT-DISTANCE readout CLIMBS with capacity (L0 h@10=0.140 -> L5 anchor1 k32/d8192
h@10=0.424 MEASURED@data/exp_course_c_oracle_capacity_ladder_v1/metrics.json), while the FPE bounded-kernel
readout stays FLAT ~0.03 (worse, ~0.000, on the anchor1 rungs). The FPE kernel is clearly the WRONG readout
here; the DIRECT-DISTANCE readout is the one that responds to capacity.

WHAT THIS CELL DOES. Push the cheapest high-leverage FIT levers -- ranked by the KGE-convergence lit-scan in
notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md (Branch 3) -- to move the
DIRECT-READOUT transductive ORACLE toward firing (hits@10 -> 0.90). Levers, highest-leverage first:
  (1) EPOCHS / total dataset passes. RotatE trained ~376-472 passes on a comparable graph; our L5 top rung is
      only 150. TOP lever per the lit-scan.
  (2) LEARNING-RATE mismatch. A1_LR=0.05 (Adam) is ~1000x RotatE's published ~5e-5 at comparable scale. And
      the ladder's OWN evidence localizes this: on anchor1, epochs 60->150 barely moved direct
      (L3=0.362 -> L4=0.372, +0.010) while k 24->32 moved it (+0.052) -- consistent with LR-too-high so more
      steps cannot REFINE. Fixing LR is what LETS epochs matter. Checked ALONGSIDE lever 1 (isolated by E1 vs
      E2 below).
  (3) COORD capacity k. Demonstrably the strongest single lever the ladder tested (L4 k24 -> L5 k32: +0.052).

The ladder rungs (E0..E3) ISOLATE these levers so we can localize the weak point, not just crank blindly:
  E0_repro_L5   k32 ep150 lr0.05 nneg64   -- Gate-D positive control: MUST reproduce L5 direct h@10=0.424.
  E1_ep450_hiLR k32 ep450 lr0.05 nneg64   -- epochs lever AT the high LR (isolates: does more epochs help
                                             while LR stays 0.05? ladder evidence predicts ~no).
  E2_lrfix_ep450 k32 ep450 lr5e-3 nneg64  -- LR-fix AT ep450 (isolates the LR lever: E2 vs E1).
  E3_kcap_ep300  k48 ep300 lr5e-3 nneg64  -- + coord capacity (the demonstrated-strongest lever) on the fixed
                                             LR, epochs trimmed to 300 to hold each rung <= 4x L5 elapsed.
Plus a RANDOM must-fail control (untrained coords -> chance) so the metric is provably NOT structurally frozen
and CAN move. Dual readout (direct + fpe) kept every rung so we can still see if fpe ever catches up. Direct
readout is degree-stratified (LOW/MID/HIGH gold-tail-degree tertile) to localize WHERE the fit breaks.

ESCALATE-TO-STRATEGY TRIGGER (Branch-3, MANDATORY explicit). If this strengthened fit (levers 1-3) still
plateaus materially below oracle_direct>=0.90, that is the signal the REPRESENTATION may need to change (the
additive/translational TransE functional form may be a poor fit for CSKG's SYNONYM/IS_A relation mix, or a
genuine k-dim coordinate-capacity ceiling at N=25752). The cell reports this as EXTENDED_LADDER_FIT_LIMITED_
ESCALATE_STRATEGY and DOES NOT silently keep cranking capacity forever. Density is already confirmed dense
(core avg-degree ~39.7, FB15k-237-comparable) so 'not enough data' is ruled out per the density-ceiling note.

BANDS (lifted from Branch 3; not invented here):
  HARD-PASS (fit closed, licenses the Branch-1 decisive re-run): some rung gets oracle_direct >= 0.90 within
    <= 4x the L5 rung's elapsed (per-rung budget). oracle_fpe is re-checked at that rung.
  HARD-FAIL / escalation: best oracle_direct < 0.90 AND core dense -> escalate to strategy with the
    functional-form / representational-capacity framing; do NOT keep sweeping recipe knobs.

## Compute architecture
class: (c) MIXED. CSKG assembly + degree-map = symbolic graph traversal (sequential-CPU correct, same as the
VET + ladder apparatus). Coord fit = MINIBATCH SGD (torch, vectorized); readout = batched/query-chunked matmul.
SINGLE seed, SINGLE CSKG assembly reused across all rungs -> memory FLAT (no multi-seed accumulation; the OOM
driver is absent by construction). device=cpu on remote_cpu_queue: CPU is memory-UNBOUNDED, so the deliberate
epoch-escalation (the #1 lever) carries ZERO OOM-kill risk on the reasoning-critical path -- a GPU OOM mid-rung
would waste hours and delay the decisive re-run MORE than CPU's slower wall. This matches the ladder's own
proven-safe routing (ladder ran 6 rungs in 5414s on remote_cpu_queue). The fit is vectorized torch either way
(NOT a numpy Python-loop), so the GPU-batching mandate's core concern does not apply. LOCAL = NEVER (no-local-
smokes lock; authored for remote_cpu_queue only; the remote --self-test is the ship gate).
Storage strategy: no_storage (KGE coordinate fit, not an associative-memory store).

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - start_marker + crash_diagnostic + heartbeat present.
# - cell_chunked: false (single seed by design -> no cross-seed accumulation; memory-safe without subprocess).
# - discriminator: oracle_direct-fires (>=0.90) is the gate; RANDOM control MUST stay < 0.05 (must-fail fires);
#   Gate-D E0 MUST reproduce L5=0.424 (invocation/regime integrity). No vacuous auto-pass.
# - progress_logging: print_flush_true (per-rung + per-fit flush; line-buffered stdout).
# - no numbers hard-coded as claims; every reported value is MEASURED@this metrics.json at run time. The single
#   reference constant L5_DIRECT_REF=0.424 is tagged MEASURED@the ladder metrics and used ONLY as the Gate-D
#   reproduce target.
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
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
# Reuse the v1 map-builder symbolic + readout apparatus verbatim (identical code path as the decisive run
# and the ladder). Same gate thresholds, same stratification, same filtered-hits math.
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores,
    geom_scores, _standardize, stratify_by_tail_degree, per_stratum_hits,
    FPE_ELL, PRIMARY_K, STRATA,
)

ANCHOR_NAME = "course_c_strengthened_fit_recipe_extended_ladder_v1"

ORACLE_FIRE = 0.90          # oracle_direct hits@10 threshold that makes the reasoning question askable (Branch 3)
N_ORACLE_HOLD = 500         # random held-out edges folded into the transductive ORACLE fit + scored for recovery
FPE_SCORE_CHUNK = 256

# Branch-3 per-rung compute bound + Gate-D reproduce target (MEASURED off the ladder).
L5_ELAPSED_REF = 1329.3     # MEASURED@data/exp_course_c_oracle_capacity_ladder_v1/metrics.json:ladder[5].elapsed_s
MAX_RUNG_BUDGET_S = 4.0 * L5_ELAPSED_REF   # Branch-3: each extended rung <= 4x the L5 rung's elapsed (~5317s)
L5_DIRECT_REF = 0.424       # MEASURED@same:ladder[5].oracle_direct_h10 (E0 must reproduce within GATE_D_TOL)
GATE_D_TOL = 0.10           # |E0_direct - L5_DIRECT_REF| > tol => HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH
PLATEAU_EPS = 0.03          # top escalated rung must improve on the prior by >= this to count as "still climbing"
RANDOM_CTRL_MAX = 0.05      # RANDOM untrained control must stay below this (must-fail fires; metric can move)
DENSE_AVGDEG = 30.0         # core avg-degree >= this rules out data-sparsity (Branch-3 escalation gate)

# Extended ladder rungs (all anchor1, minibatch=8192, reciprocal=True, transductive). Each ISOLATES a lever;
# ordered by escalation (E0 control -> E3 strongest). dim = FPE readout dim (affects the fpe DIAGNOSTIC only,
# NOT the primary direct readout nor the fit). (label, k, fpe_dim, epochs, lr, n_neg)
FULL_LADDER = [
    ("E0_repro_L5",    32, 8192, 150, 0.05,  64),   # Gate-D control: reproduce L5 direct h@10=0.424
    ("E1_ep450_hiLR",  32, 8192, 450, 0.05,  64),   # epochs lever AT the high LR (isolates epochs@0.05)
    ("E2_lrfix_ep450", 32, 8192, 450, 5e-3,  64),   # LR-fix AT ep450 (isolates the LR lever: E2 vs E1)
    ("E3_kcap_ep300",  48, 8192, 300, 5e-3,  64),   # + coord capacity on the fixed LR (ep trimmed for budget)
]
# Reduced REMOTE pre-check ladder (tiny CSKG slice) -- optional small remote validation before the full ladder.
SMOKE_LADDER = [
    ("E0s", 16, 1024, 60,  0.05, 64),
    ("E2s", 16, 1024, 120, 5e-3, 64),
]

FULL_CFG = dict(seed=7, cskg_max_lines=0, k_core=12, cskg_max_nodes=0, min_support=10, min_conf=0.10,
                ladder="full")
SMOKE_CFG = dict(seed=7, cskg_max_lines=800000, k_core=3, cskg_max_nodes=3000, min_support=2, min_conf=0.05,
                 ladder="smoke")


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


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


def _fit_anchor1(train_int, N, n_rel, k, epochs, lr, n_neg, batch, device, seed, hold=None):
    """Transductive anchor1 fit threading the extended-ladder levers (lr / n_neg) into fit_kge_anchor1.
    hold != None => fold the held-out edges into the fit (the ORACLE memorization probe)."""
    return fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold,
                           reciprocal=True, lr=lr, n_neg=n_neg, batch_size=batch)


def _direct_scores(X, D, hold_edges, device, chunk=FPE_SCORE_CHUNK):
    """Direct-distance readout: score = -||x_hat - X_c|| on standardized coords (the fit-limited reference
    readout; this is the readout that RESPONDS to capacity per the ladder). Query-chunked to bound memory."""
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
    return out


def _median_heuristic_ell(X, D, sample_n=2000, seed=0):
    """Median-heuristic RBF bandwidth on the STANDARDIZED coords geom_scores actually uses (Garreau et al.
    2017). The pre-registered FPE_ELL=0.55 is mis-scaled for these coords: after _standardize (per-coord std
    ~1), typical pairwise distance in k dims is ~sqrt(2k) ~ 7-8, so exp(-||x-y||^2 / (2*0.55^2)) UNDERFLOWS to
    ~0 for nearly all candidate pairs -> degenerate (exactly-0.000) FPE ranking. This returns ell = median
    pairwise distance so the kernel is actually informative. Readout-fix lever (Branch-2 candidate 2)."""
    Xn, _ = _standardize(X, D)
    n = Xn.shape[0]
    g = torch.Generator(device="cpu").manual_seed(seed * 333 + 1)
    idx = torch.randperm(n, generator=g)[:min(sample_n, n)]
    S = Xn[idx].detach().float().cpu()
    d = torch.pdist(S)                                    # (m*(m-1)/2,) pairwise L2 distances
    ell = float(torch.median(d).item())
    return max(ell, 1e-6)


def _fpe_health(scores):
    """Structural-bug detector for the FPE readout: a near-zero std / range or non-finite scores means the
    kernel collapsed to a constant (bandwidth underflow) or NaN, i.e. the readout is degenerate, NOT merely
    under-capacity. Sampled cheaply off the already-on-CPU (nq, N) score tensor."""
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
    return round(float(dm["hits@%d" % PRIMARY_K]), 4), round(float(dm["mrr"]), 4)


def run_ladder(run_mode, device):
    cfg = FULL_CFG if run_mode == "full" else SMOKE_CFG
    ladder = FULL_LADDER if cfg["ladder"] == "full" else SMOKE_LADDER
    seed = cfg["seed"]
    t0 = time.perf_counter()

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

    # Degree map for the weak-point-localization stratification of the ORACLE held-out (LOW/MID/HIGH tail deg).
    gd = Graph(train_lbl, ent2i, rel2i)

    # ORACLE held-out: random test edges (transductive memorization-capacity probe; L2-genuineness irrelevant).
    rng = np.random.default_rng(seed * 100057 + 7)
    sel = rng.permutation(test_int.shape[0])[:min(N_ORACLE_HOLD, test_int.shape[0])]
    hold_oracle = test_int[sel].copy()
    strat, tert = stratify_by_tail_degree(hold_oracle, gd.node_degree)
    _log("oracle held-out n=%d (of %d test); N_candidates=%d; deg-tertile bounds=%s"
         % (hold_oracle.shape[0], test_int.shape[0], N, str(tert)))

    # Must-fail control FIRST (cheap; establishes the metric floor + that it can move).
    rand_direct, rand_mrr = _random_control(N, n_rel, 32, hold_oracle, all_true, device, seed)
    _log("RANDOM control: oracle_direct h@10=%.4f (must stay < %.2f); mrr=%.4f" % (rand_direct, RANDOM_CTRL_MAX, rand_mrr))

    hb_path = os.path.join(str(get_output_dir(ANCHOR_NAME)), "_heartbeat.jsonl")

    def _hb(tag):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag,
                                "elapsed_s": time.perf_counter() - t0}) + "\n")

    rows = []
    for (label, k, dim, epochs, lr, n_neg) in ladder:
        tp = time.perf_counter()
        X_or, D_or = _fit_anchor1(train_int, N, n_rel, k, epochs, lr, n_neg, 8192, device, seed, hold=hold_oracle)
        # DIRECT-DISTANCE readout (the primary; the one that RESPONDS to capacity; the oracle-fire gate).
        direct = _direct_scores(X_or, D_or, hold_oracle, device)
        direct_m = filtered_hits_from_scores(direct, hold_oracle, all_true)
        direct_strat = per_stratum_hits(direct, hold_oracle, strat, all_true)
        # FPE readout at the PRE-REGISTERED bandwidth (ell=0.55) -- the intended geometric readout, diagnostic.
        W0 = make_fpe_basis(k, dim, FPE_ELL, device, seed)
        fpe = geom_scores(X_or, D_or, W0, hold_oracle, device)
        fpe_m = filtered_hits_from_scores(fpe, hold_oracle, all_true)
        fpe_hlth = _fpe_health(fpe)
        # READOUT-FIX lever: FPE at the MEDIAN-HEURISTIC bandwidth on THIS rung's standardized coords. Tests
        # whether the FPE exact-0.000 is a cheap bandwidth mis-spec (structural/config) vs genuinely broken.
        ell_mh = _median_heuristic_ell(X_or, D_or, seed=seed)
        W1 = make_fpe_basis(k, dim, ell_mh, device, seed)
        fpe_mh = geom_scores(X_or, D_or, W1, hold_oracle, device)
        fpe_mh_m = filtered_hits_from_scores(fpe_mh, hold_oracle, all_true)
        fpe_mh_hlth = _fpe_health(fpe_mh)
        elapsed = round(time.perf_counter() - tp, 1)
        row = dict(label=label, fit_kind="anchor1", k=k, fpe_dim=dim, epochs=epochs, lr=lr, n_neg=n_neg,
                   batch=8192,
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
                   within_budget=bool(elapsed <= MAX_RUNG_BUDGET_S),
                   elapsed_s=elapsed)
        rows.append(row)
        _log("LADDER %s: DIRECT h@10=%.3f (low/mid/high=%.3f/%.3f/%.3f) | FPE(ell=0.55) h@10=%.3f std=%.2e | "
             "FPE(medht ell=%.2f) h@10=%.3f | fires_direct=%s within_budget=%s (%.1fs)"
             % (label, row["oracle_direct_h10"], direct_strat["low"]["hits"], direct_strat["mid"]["hits"],
                direct_strat["high"]["hits"], row["oracle_fpe_h10"], fpe_hlth["std"], ell_mh,
                row["oracle_fpe_medht_h10"], row["fires_direct"], row["within_budget"], elapsed))
        _hb(label)
        del W0, W1, X_or, D_or, fpe, fpe_mh, direct
        if getattr(device, "type", "") == "cuda":
            torch.cuda.empty_cache()

    # ---- FPE readout diagnosis (coordinator flag: FPE exact-0.000 at L2-L5 -- config bug vs capacity?) -------
    best = max(rows, key=lambda r: r["oracle_direct_h10"])
    best_fpe = max(rows, key=lambda r: r["oracle_fpe_h10"])
    best_fpe_mh = max(rows, key=lambda r: r["oracle_fpe_medht_h10"])
    best_direct_v = best["oracle_direct_h10"]
    best_fpe_v = best_fpe["oracle_fpe_h10"]
    best_fpe_mh_v = best_fpe_mh["oracle_fpe_medht_h10"]
    # degenerate pre-registered FPE: near-constant scores (bandwidth underflow) on the best-fit rung.
    fpe_prereg_degenerate = bool(best["fpe_prereg_health"]["std"] < 1e-4)
    # median-heuristic recovers FPE to ~ the direct readout => the exact-0.000 was a bandwidth mis-spec (fixable).
    if best_direct_v > 1e-6 and best_fpe_v < 0.5 * best_direct_v and best_fpe_mh_v >= 0.7 * best_direct_v:
        fpe_diag = "FPE_BANDWIDTH_BUG_CONFIRMED"
    elif best_fpe_mh_v < 0.5 * max(best_direct_v, 1e-6):
        fpe_diag = "FPE_STRUCTURAL_DEEPER_USE_DIRECT"
    else:
        fpe_diag = "FPE_OK"
    e0r = next((r for r in rows if r["label"] == "E0_repro_L5"), None)
    e0_direct_v = e0r["oracle_direct_h10"] if e0r else 0.0
    lever_attribution = dict(
        fit_escalation_direct_gain=round(best_direct_v - e0_direct_v, 4),      # what epochs+LR+k bought (direct)
        readout_fix_fpe_gain=round(best_fpe_mh_v - best_fpe_v, 4),             # what the bandwidth fix bought FPE
        best_direct=best_direct_v, best_fpe_prereg=best_fpe_v, best_fpe_medht=best_fpe_mh_v,
        ell_prereg=FPE_ELL, ell_medht_best_rung=best_fpe_mh["ell_medht"])

    # ---- verdict logic (Branch-3 bands; oracle-fire gated on DIRECT per coordinator; escalate explicit) ------
    fires = [r for r in rows if r["fires_direct"]]
    firing = fires[0] if fires else None

    # escalated rungs (exclude the E0 reproduce control) for the climbing-vs-plateau trajectory read.
    escalated = [r for r in rows if r["label"] != "E0_repro_L5"]
    climbing = False
    if len(escalated) >= 2:
        top = max(escalated, key=lambda r: r["oracle_direct_h10"])
        last = escalated[-1]  # highest-escalation rung
        prev_best = max([r["oracle_direct_h10"] for r in escalated if r is not last], default=0.0)
        climbing = bool(top is last and (last["oracle_direct_h10"] - prev_best) >= PLATEAU_EPS)
    core_dense = bool(core_avgdeg >= DENSE_AVGDEG)

    # integrity gates (take precedence over the fire/escalate verdict).
    e0 = next((r for r in rows if r["label"] == "E0_repro_L5"), None)
    gate_d_ok = bool(e0 is not None and abs(e0["oracle_direct_h10"] - L5_DIRECT_REF) <= GATE_D_TOL)
    control_ok = bool(rand_direct < RANDOM_CTRL_MAX)

    if not control_ok:
        verdict = "HARD_FAIL_CONTROL_METRIC_BROKEN"
        vm = ("MUST-FAIL CONTROL FIRED: RANDOM untrained coords scored oracle_direct h@10=%.4f (>= %.2f). The "
              "direct-readout metric is leaking / structurally frozen-high; no rung result is trustworthy. Fix "
              "the readout/metric before interpreting the ladder." % (rand_direct, RANDOM_CTRL_MAX))
    elif not gate_d_ok:
        verdict = "HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH"
        vm = ("GATE-D FAILED: E0_repro_L5 (identical config to ladder L5) scored oracle_direct h@10=%.4f but "
              "L5 measured %.3f (tol %.2f). The anchor1 fit invocation drifted from the ladder; downstream rungs "
              "are suspect. Reconcile before trusting any escalated rung."
              % (e0["oracle_direct_h10"] if e0 else -1.0, L5_DIRECT_REF, GATE_D_TOL))
    elif firing is not None:
        verdict = "EXTENDED_LADDER_FIT_FIRES"
        vm = ("FIT FIRES: oracle_direct h@10=%.3f >= %.2f at %s (k=%d ep=%d lr=%g nneg=%d, %.1fs, within_budget=%s). "
              "The transductive ORACLE now memorizes its held-out edges; the FIT is closed and the Branch-1 "
              "decisive 3-seed re-run is licensed (SWAP the decisive cell fit_transe_coords -> fit_kge_anchor1 at "
              "this config). Intended FPE readout at this rung: prereg(ell=0.55)=%.3f, median-heuristic=%.3f "
              "(fires_medht=%s); FPE diagnosis=%s -- use the median-heuristic-recalibrated FPE (or direct) as the "
              "production readout for the re-run."
              % (firing["oracle_direct_h10"], ORACLE_FIRE, firing["label"], firing["k"], firing["epochs"],
                 firing["lr"], firing["n_neg"], firing["elapsed_s"], firing["within_budget"],
                 firing["oracle_fpe_h10"], firing["oracle_fpe_medht_h10"], firing["fires_fpe_medht"], fpe_diag))
    elif climbing and core_dense:
        verdict = "EXTENDED_LADDER_FIT_CLIMBING_UNDER_BUDGET"
        vm = ("FIT STILL CLIMBING but NOT fired: best oracle_direct h@10=%.3f at %s (< %.2f); the highest-"
              "escalation rung is the best and improved >= %.2f on the prior, so capacity is still buying "
              "direct-readout accuracy. Core is dense (avgdeg=%.1f). ONE more capacity rung MAY be warranted but "
              "this is a STRATEGY call, not an auto keep-cranking -- do NOT silently escalate capacity forever; "
              "flag the trajectory to strategy (epochs/k vs representation-change)."
              % (best["oracle_direct_h10"], best["label"], ORACLE_FIRE, PLATEAU_EPS, core_avgdeg))
    else:
        verdict = "EXTENDED_LADDER_FIT_LIMITED_ESCALATE_STRATEGY"
        vm = ("ESCALATION TRIGGER: strengthened fit (epochs 3x + LR-fix + coord-cap, levers 1-3) still PLATEAUS "
              "at oracle_direct h@10=%.3f (best %s) << %.2f, and the core is dense (avgdeg=%.1f -> 'not enough "
              "data' ruled out). This is UN-CONFOUNDED by the FPE readout: the FPE exact-0.000 was diagnosed "
              "[%s] and the median-heuristic-recalibrated FPE reached %.3f (vs prereg %.3f) -- yet the WORKING "
              "direct readout STILL does not fire, so this is a genuine FIT/REPRESENTATION wall, not a masked "
              "readout bug. Signal: the additive/translational TransE functional form may be a poor fit for "
              "CSKG's SYNONYM/IS_A relation mix, or a genuine k-dim coord-capacity ceiling at N=%d. Escalate to "
              "strategy with THIS framing (functional-form / representational-capacity, NOT recipe-tuning) -- do "
              "NOT keep sweeping recipe knobs."
              % (best["oracle_direct_h10"], best["label"], ORACLE_FIRE, core_avgdeg, fpe_diag,
                 best_fpe_mh_v, best_fpe_v, N))

    return dict(verdict=verdict, verdict_msg=vm, summary=vm[:200], run_mode=run_mode,
                elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), seed=seed,
                N=int(N), n_rel=int(n_rel), oracle_fire_threshold=ORACLE_FIRE,
                cskg_provenance=prov, core_avgdeg=core_avgdeg, core_dense=core_dense,
                deg_tertile_bounds=tert, ladder=rows,
                fpe_diagnosis=fpe_diag, lever_attribution=lever_attribution,
                random_control=dict(oracle_direct_h10=rand_direct, oracle_direct_mrr=rand_mrr,
                                    max_allowed=RANDOM_CTRL_MAX, control_ok=control_ok),
                gate_d=dict(l5_direct_ref=L5_DIRECT_REF, e0_direct=(e0["oracle_direct_h10"] if e0 else None),
                            tol=GATE_D_TOL, gate_d_ok=gate_d_ok),
                firing_config=firing, best_config=best, best_fpe_config=best_fpe,
                best_fpe_medht_config=best_fpe_mh,
                climbing=climbing, per_rung_budget_s=round(MAX_RUNG_BUDGET_S, 1))


def _run_selftest(device):
    """LIGHTWEIGHT ship-gate self-test: exercises the EXACT extended-ladder code path (_fit_anchor1 threading
    lr/n_neg -> geom_scores FPE readout + _direct_scores + per_stratum_hits + _random_control) on a TINY
    SYNTHETIC functional graph -- NO CSKG data, seconds, exits 0/1. A clean functional relation t=(h+off_r)%N
    is trivially memorizable, so the transductive ORACLE must recover it under the direct readout (a real
    discriminator with margin), AND the RANDOM control must stay near chance (proves the metric can move)."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(0)
    N = 120
    n_rel = 4
    k = 8
    dim = 256
    epochs = 100
    batch = 128
    offs = rng.integers(1, N, size=n_rel)
    h = rng.integers(0, N, size=400)
    r = rng.integers(0, n_rel, size=400)
    t = (h + offs[r]) % N
    edges = np.stack([h, r, t], axis=1).astype(np.int64)
    hold = edges[-40:].copy()
    train_int = edges[:-40].copy()
    all_true = build_true_by_hr_int(edges)
    strat, _tert = stratify_by_tail_degree(hold, {i: 1 for i in range(N)})
    W = make_fpe_basis(k, dim, FPE_ELL, device, 7)
    X, D = _fit_anchor1(train_int, N, n_rel, k, epochs, 5e-3, 32, batch, device, 7, hold=hold)
    fpe_m = filtered_hits_from_scores(geom_scores(X, D, W, hold, device), hold, all_true)
    # exercise the median-heuristic FPE readout-fix code path (bandwidth recalibration + health).
    ell_mh = _median_heuristic_ell(X, D, seed=7)
    _ = _fpe_health(geom_scores(X, D, make_fpe_basis(k, dim, ell_mh, device, 7), hold, device))
    direct = _direct_scores(X, D, hold, device)
    direct_m = filtered_hits_from_scores(direct, hold, all_true)
    _ = per_stratum_hits(direct, hold, strat, all_true)
    rand_direct, _rm = _random_control(N, n_rel, k, hold, all_true, device, 7)
    fpe_h10 = float(fpe_m["hits@%d" % PRIMARY_K])
    direct_h10 = float(direct_m["hits@%d" % PRIMARY_K])
    finite = bool(direct_h10 == direct_h10 and fpe_h10 == fpe_h10 and rand_direct == rand_direct)
    fires = bool(direct_h10 >= 0.5)             # transductive memorization on a tiny clean functional graph
    control_low = bool(rand_direct < 0.30)      # RANDOM must be far below the trained direct readout
    ok = bool(finite and fires and control_low)
    verdict = "SELFTEST_PASS" if ok else "SELFTEST_FAIL"
    vm = ("SELFTEST synthetic functional graph N=%d: oracle_direct h@10=%.3f (>=0.50 req), RANDOM direct=%.3f "
          "(<0.30 req), oracle_fpe h@10=%.3f; _fit_anchor1(lr/nneg) + FPE/direct/stratify/control code path "
          "runs; ok=%s" % (N, direct_h10, rand_direct, fpe_h10, ok))
    _log(vm)
    return dict(verdict=verdict, verdict_msg=vm, summary=vm[:200], run_mode="self_test",
                elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device),
                selftest=dict(oracle_direct_h10=round(direct_h10, 4), oracle_fpe_h10=round(fpe_h10, 4),
                              random_direct_h10=round(rand_direct, 4), finite=finite, fires=fires,
                              control_low=control_low))


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
    _write_start_marker(out_dir, run_mode, 1)
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
