"""SR_ADDITIVE_SCORE_FUSION: non-learned SCORE-LEVEL fusion of two ALREADY-LANDED, VET-confirmed FULL results on
the IDENTICAL held-out-ENTITY CSKG-core arena -- SR-compose (Bellman/local-recursive graph-spectral codebook,
data/exp_graph_spectral_compose_sr_ppmi_nystrom_v1/metrics.json, SR_COMPOSE_NYS MRR=0.073825 CITED) and
ANCHOR_COMPOSE (additive/TransE map-builder, data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json,
MRR=0.12821 CITED). CITED@notes/research_sr_compose_close_gap_to_additive_map_2026-07-14.md (lever 1, rank-1
of the ranked-lever table): brain/field lit-scan converges on structural+relational fusion beating either alone,
concentrated exactly where the additive map is weakest (cold/d1 sparse-entity buckets); positional-encoding lit
(arXiv:2505.13027) explains why fusion must happen at SCORE level (this cell), not embedding level (a documented
additive-embedding-coupling failure mode).

SCOPE CORRECTION vs the hand-off's "near-zero mechanism, pure post-hoc score combination" framing (exp_dev finding,
tagged HYPOTHESIZED->MEASURED): neither landed cell PERSISTS per-query score vectors or fit checkpoints to disk
(only aggregate metrics.json + arm_sigs hashes survive; FitCheckpoint.cleanup_seed_checkpoints deletes SGD
checkpoints on successful completion). A genuine score-level fusion therefore requires RE-DERIVING both methods'
per-query scores on the SAME query set -- this cell does that by REUSING the exact fit/compose/score functions
VERBATIM (fit_kge_anchor1, build_anchor_compose_codes, additive_direct_scores from the ANCHOR cell;
SR.G.prepare_corpus + SR.score_all_arms from the SR cell) rather than inventing any new mechanism. The SR side is
cheap CPU (closed-form randomized-SVD, ~550s/seed, no SGD). The ANCHOR side needs ONE re-fit of the additive
TransE scaffold (X, D) via SGD (the ROTATE and ORACLE arms from the parent cell are NOT needed for the fusion
question and are skipped to save ~2/3 of the parent's per-seed fit cost) -- this makes the cell GPU-bound overall,
NOT the "cheap CPU-only" cell the hand-off's cost framing anticipated. Routed to overnight_queue accordingly.

SPLIT-ALIGNMENT PREREQUISITE (the hand-off's one flagged real risk, checked here, not assumed): both source cells'
per-seed n_train/n_heldout_entities/n_support/n_query_total/n_cold are IDENTICAL on disk for every shared seed
(MEASURED@data/exp_graph_spectral_compose_sr_ppmi_nystrom_v1/metrics.json:per_seed vs
data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:per_seed). Source-read confirms WHY: SR's own
G.prepare_corpus calls `base.build_heldout_entity_split_ac` (experiments/exp_native_bind_compose_inductive_entity_
cskg_v1.py:248), and that function's docstring states it is "COPIED VERBATIM from
experiments.exp_anchor_compose_inductive_entity_cskg_v1.build_heldout_entity_split_ac" with the identical
n_heldout_eval subsample RNG (`np.random.default_rng(seed*777+3)`), so given the same (pool_lbl, cfg, seed) the two
cells' query_int arrays are guaranteed bit-identical BY CONSTRUCTION. This cell still asserts it empirically per
seed (verify_split_alignment) rather than trusting the argument alone -- INCONCLUSIVE if it ever breaches.

FUSION RULES (glass-box, non-learned; report the WHOLE curve, not a cherry-picked point):
  FUSE_SUM(w): score_fused = (1-w)*normalize_rows(sc_ANCHOR) + w*normalize_rows(sc_SR), per-query MIN-MAX row
    normalization (standard CombSUM-style IR score fusion; a monotonic per-row rescale, no learned parameters),
    swept over W_GRID = [0.0, 0.25, 0.5, 0.75, 1.0] (endpoints are trivial reproductions of the pure arms, kept as
    an exact-identity sanity check, not treated as "fusion").
  FUSE_RRF: reciprocal-rank fusion, 1/(K_RRF+rank_ANCHOR) + 1/(K_RRF+rank_SR), K_RRF=60 (Cormack, Clarke &
    Buettcher 2009 standard constant; zero tunable parameters beyond this literature-standard constant).
  MUST-FAIL controls (fuse a real channel with a SCRAMBLED/RANDOM second channel; must NOT lift over the real
    additive-alone baseline): FUSE(ANCHOR, SR_SCRAMBLE), FUSE(ANCHOR_SCRAMBLE, SR), FUSE(ANCHOR, RANDOM_CODES) --
    at both w=0.5 and RRF. SELF-FUSE sanity (fuse additive with itself; must equal additive alone, an exact
    identity, not merely "not exceed"): FUSE(ANCHOR, ANCHOR) at w=0.5.

PRE-REGISTERED BANDS (picked BEFORE the run; CITED@notes/exp_dev_handoff_research_sr_compose_close_gap_to_
additive_map_2026-07-14.md Anchor-1 pre-reg bands; ADD_ALONE/SR_ALONE below are the RE-MEASURED values from THIS
run's own re-fit, not the historical CITED constants, so the gate is self-consistent even if SGD noise across
separate GPU runs shifts ANCHOR_COMPOSE slightly from its historical 0.12821):
  HARD-PASS : best_fused_mrr (over {w=0.25,0.5,0.75,RRF}) >= ADD_ALONE + LIFT_ABS(0.02) AND all must-fail fused
              controls <= ADD_ALONE + MUST_FAIL_EPS(0.005) AND self-fuse identity holds AND both source mechanisms
              REPRODUCE their CITED historical MRR within tolerance AND split-alignment holds.
  HARD-FAIL : best_fused_mrr <= ADD_ALONE (no lift) AND SR_COMPOSE_NYS/SR_COMPOSE_FLAT does NOT beat ANCHOR_COMPOSE
              in ANY degree-stratified support-bucket (cold/d1/d2_3/d4_7/d8plus, min population MIN_STRAT_Q=8) --
              a genuine negative: the two methods' errors are too correlated to gain from fusion.
  MIDDLE    : 0 < lift < LIFT_ABS -> degree-stratify; report as real-but-small/concentrated (cold/d1) if so.
  INCONCLUSIVE: reproduction mismatch, split misalignment, must-fail control violated, or self-fuse sanity fails
              (any of these means the fusion numbers cannot be trusted regardless of the headline lift).

## Compute architecture
class (c) MIXED: ANCHOR-side additive fit = minibatch SGD, GPU-batched (device=auto/cuda), ONE fit per seed
(ADDITIVE only; ROTATE + ORACLE from the parent cell are skipped -- not needed for the fusion question, and CITED
historical ceilings are reused for context instead of re-measured). SR-side = closed-form randomized-SVD, CPU,
reused wholesale via SR.score_all_arms (device=cpu, matches the SR cell's own hardcoded path). Fusion arithmetic
(normalize_rows / ranks_from_scores / weighted-sum / RRF) = vectorized torch ops over already-computed (nq,N) score
tensors, no training, seconds. Storage: SHARDED (each entity its own additive code X[i]; SR side reuses the SR
cell's own native Hebbian KGStore per-entity codes) -- no bundled global fact store anywhere in this cell.
Per-experiment timeout REQUIRED (per exp_dev discipline): FULL_CFG reuses the ANCHOR cell's k=24/epochs=500/
n_neg=128/batch=8192/neg_chunk=16 (identical hyperparameters -> the additive-only fit should cost ~1/3 of the
parent's 12073.5s/3seeds since only 1 of its 3 model-fits (ADDITIVE, ROTATE, ORACLE) runs here, ~4025s) plus the SR
side reused wholesale (1651.9s/3seeds MEASURED) plus fusion/degree-stratification overhead (vectorized, <2min) =
~5700s (~95min) ESTIMATED; --timeout 10800 (3h) gives ~1.9x safety margin for GPU-host variance / cold-start.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test + FULL (META_RULE_AF): sig hash per arm; w=0.0 and w=1.0 endpoints + the
#   ANCHOR-self-fuse arm are INTENTIONALLY near-identical to ANCHOR_COMPOSE/SR_COMPOSE_NYS by construction (exact
#   monotonic-rescale identity, not a bug) -> declared arms_differ_exempted for those 3 pairs.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / discriminator_reachability: both source mechanisms are ALREADY chain-grade MEASURED at FULL scale
#   (SR=0.0731-0.0738, ANCHOR=0.12821, both scramble-verified real per their own landed VET) -- this cell is not
#   re-proving either mechanism fires, only whether COMBINING two independently-real signals lifts the ceiling;
#   HARD-PASS threshold (ADD_ALONE+0.02) sits strictly between the measured ADD_ALONE and the measured
#   ORACLE_ADDITIVE ceiling (0.137293 CITED), so it is reachable-in-principle, not unbounded.
# - baseline_in_band: both re-measured ADD_ALONE and SR_ALONE must reproduce their CITED historical values within
#   tolerance (REPRODUCE_TOL_ADD=0.03 SGD-noise-tolerant, REPRODUCE_TOL_SR=0.01 near-exact closed-form) before any
#   fusion number is trusted -- an INCONCLUSIVE gate, not a silent pass-through.
# - discriminator survives scale: option B (analytical) -- the complementarity hypothesis is fundamentally a
#   FULL-scale question (needs CSKG's actual measured degree heterogeneity / error-correlation structure); a tiny
#   synthetic self-test arena has no reason to replicate that structure. Self-test instead proves the FUSION
#   ARITHMETIC (normalize/rank/weighted-sum/RRF/must-fail-control logic) is implemented correctly on REAL score
#   tensors from the real substrate fit (AC's own planted TransE arena), which does not require both mechanisms to
#   cooperate on the same synthetic arena.
# - HARD-PASS strictly above floor: LIFT_ABS=0.02 is a 15.6% relative lift over ADD_ALONE(0.12821), well above any
#   single-seed MRR noise floor at nq=3000 (MEASURED cross-seed spread in the parent cells is ~0.01-0.02 absolute).
# - HP_SCOPE: {ANCHOR_COMPOSE: [reproduce_add], SR_COMPOSE_NYS: [reproduce_sr], FUSE_SUM_w025/w050/w075/FUSE_RRF:
#   [hard_pass_lift], FUSE_SUM_*_SRSCR/*_RANDOM/FUSE_RRF_*_SRSCR/*_RANDOM: [must_fail_le_add_alone],
#   FUSE_SUM_ANCHOR_SELF: [self_fuse_identity]}.
# - cardinality: EXPECTED_N_UNITS = n_seeds(3); each seed asserted to produce all 20 arms + split-alignment pass.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: default_ok_for_this_regime -- every band/constant (LIFT_ABS, MUST_FAIL_EPS, K_RRF, W_GRID,
#   REPRODUCE_TOL_*) is pre-registered above, NOT tuned on real data; the CSKG-core + held-out split config is
#   COPIED VERBATIM from both parent cells.
# - all numbers tagged MEASURED@/CITED@/THEORETICAL@ in this docstring.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-phase flush prints + heartbeat;
#   timeout>=1800).
# - §15-F: real_code_path_exercised + substrate_signature_checked + guard_baseline_valid declared at self-test.

MEASURED@data/exp_graph_spectral_compose_sr_ppmi_nystrom_v1/metrics.json: SR_COMPOSE_NYS=0.073825
  SR_COMPOSE_FLAT=0.073117 SR_COMPOSE_NYS_SCRAMBLE=0.014438 (per-seed n_train/n_support/n_query_total/n_cold match
  the ANCHOR cell's per-seed values exactly for every shared seed -- split-identity evidence).
MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json: ANCHOR_COMPOSE=0.12821
  ANCHOR_SCRAMBLE=0.00984 RANDOM_CODES=0.000483 ORACLE_ADDITIVE=0.137293 (oracle_headroom=0.136810, the
  best-possible-in-arena ceiling this cell's HARD-PASS threshold must sit strictly below).
CITED@notes/research_sr_compose_close_gap_to_additive_map_2026-07-14.md: GraIL (Teru et al. ICML 2020),
  InGram (arXiv:2305.19987) structural+relational fusion precedent; positional-encoding spectral-coupling caution
  (arXiv:2505.13027) motivating score-level (not embedding-level) fusion.
THEORETICAL@Cormack, Clarke & Buettcher, "Reciprocal Rank Fusion outperforms Condorcet and individual Rank
  Learning Methods," SIGIR 2009 (RRF formula + K_RRF=60 standard constant).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import hashlib
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

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores,
)
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402
from hdlab.kg_traversal import KGStore  # noqa: E402
import experiments.exp_anchor_compose_inductive_entity_cskg_v1 as AC  # noqa: E402  (reused verbatim)
import experiments.exp_graph_spectral_compose_sr_ppmi_nystrom_v1 as SR  # noqa: E402  (reused verbatim)

ANCHOR_NAME = "sr_additive_score_fusion_cskg_v1"

# ---- Arm names ----
ANCHOR_ARM = "ANCHOR_COMPOSE"
ANCHOR_SCR_ARM = "ANCHOR_SCRAMBLE"
RANDOM_ARM = "RANDOM_CODES"
SR_ARM = "SR_COMPOSE_NYS"
SR_FLAT_ARM = "SR_COMPOSE_FLAT"
SR_SCR_ARM = "SR_COMPOSE_NYS_SCRAMBLE"

W_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
FUSE_SUM_ARMS = ["FUSE_SUM_w%03d" % round(w * 100) for w in W_GRID]
FUSE_RRF_ARM = "FUSE_RRF"
FUSION_CANDIDATE_ARMS = ["FUSE_SUM_w025", "FUSE_SUM_w050", "FUSE_SUM_w075", FUSE_RRF_ARM]

MUST_FAIL_SUM_ARMS = ["FUSE_SUM_ANCHOR_SRSCR_w050", "FUSE_SUM_ANCHORSCR_SR_w050", "FUSE_SUM_ANCHOR_RANDOM_w050"]
MUST_FAIL_RRF_ARMS = ["FUSE_RRF_ANCHOR_SRSCR", "FUSE_RRF_ANCHORSCR_SR", "FUSE_RRF_ANCHOR_RANDOM"]
MUST_FAIL_ARMS = MUST_FAIL_SUM_ARMS + MUST_FAIL_RRF_ARMS
SELF_FUSE_ARM = "FUSE_SUM_ANCHOR_SELF_w050"

ALL_ARMS = ([ANCHOR_ARM, ANCHOR_SCR_ARM, RANDOM_ARM, SR_ARM, SR_FLAT_ARM, SR_SCR_ARM]
            + FUSE_SUM_ARMS + [FUSE_RRF_ARM] + MUST_FAIL_ARMS + [SELF_FUSE_ARM])

ARMS_DIFFER_EXEMPT = [("FUSE_SUM_w000", ANCHOR_ARM), (SELF_FUSE_ARM, ANCHOR_ARM), ("FUSE_SUM_w100", SR_ARM)]

# ---- CITED reference ceilings (both source cells VET-confirmed FULL; MEASURED@ paths in docstring) ----
CITED_ADD_COMPOSE = 0.12821
CITED_ORACLE_ADDITIVE = 0.137293
CITED_SR_NYS = 0.073825
CITED_SR_FLAT = 0.073117

# ---- Pre-registered bands (picked BEFORE the run; NOT tuned on real data) ----
LIFT_ABS = 0.02             # HARD-PASS: best_fused - ADD_ALONE >= this
MUST_FAIL_EPS = 0.005       # a fused-with-noise control may exceed ADD_ALONE by at most this (noise tolerance)
SELF_FUSE_TOL = 0.003       # FUSE(ANCHOR,ANCHOR) must equal ANCHOR_COMPOSE within this (identity, not a bound)
REPRODUCE_TOL_ADD = 0.03    # SGD-noise tolerance across independent GPU re-fits of the SAME seed/hparams
REPRODUCE_TOL_SR = 0.01     # closed-form spectral fit; should reproduce near-exactly
K_RRF = 60.0                # THEORETICAL@Cormack, Clarke & Buettcher 2009 (standard RRF constant)
MIN_STRAT_Q = 8             # min queries in a degree-stratum to trust its margin (HARD-FAIL degree-scan)
SCORE_CHUNK = 256

SUPPORT_BINS = [(0, 0, "cold"), (1, 1, "d1"), (2, 3, "d2_3"), (4, 7, "d4_7"), (8, 10 ** 9, "d8plus")]

# ---- Config profiles ----
SELFTEST_CFG = dict(k=12, epochs=350, n_neg=32, batch=4096, neg_chunk=None, ckpt_every=0,
                    d_code=32, svd_n_iter=3,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=8)
FULL_CFG = dict(k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, ckpt_every=20,
               d_code=1024, svd_n_iter=3,
               heldout_entity_frac=0.15, support_frac=0.5, cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
               n_heldout_eval=3000, min_heldout=20, seeds=[7, 13, 17])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(output_dir), "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(str(output_dir), "metrics.json"))


def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


# ---------------------------------------------------------------------------
# Fusion arithmetic (the genuinely NEW, near-zero-mechanism code in this cell).
# ---------------------------------------------------------------------------

def normalize_rows(sc):
    """Per-query MIN-MAX rescale to [0,1] (standard CombSUM-style score fusion prep). Monotonic per row -> a
    lone-arm's rank order (and therefore its filtered hits/MRR) is UNCHANGED by this transform."""
    mn = sc.min(dim=1, keepdim=True).values
    mx = sc.max(dim=1, keepdim=True).values
    rng = (mx - mn).clamp_min(1e-9)
    return (sc - mn) / rng


def weighted_sum_fuse(sc_a, sc_b, w):
    """score_fused = (1-w)*normalize(sc_a) + w*normalize(sc_b). w=0 -> pure a; w=1 -> pure b (rank-identical)."""
    return (1.0 - w) * normalize_rows(sc_a) + w * normalize_rows(sc_b)


def ranks_from_scores(sc):
    """1-indexed rank per candidate (1=best) via argsort-of-argsort. (nq,N) int64."""
    order = torch.argsort(sc, dim=1, descending=True)
    nq, N = sc.shape
    rank = torch.empty_like(order)
    ar = torch.arange(1, N + 1, dtype=order.dtype).unsqueeze(0).expand(nq, N)
    rank.scatter_(1, order, ar)
    return rank


def rrf_fuse(sc_a, sc_b, k_rrf=K_RRF):
    """Reciprocal-rank fusion: 1/(k+rank_a) + 1/(k+rank_b). Higher = better. Zero tunable params beyond k_rrf."""
    ra = ranks_from_scores(sc_a).to(torch.float32)
    rb = ranks_from_scores(sc_b).to(torch.float32)
    return 1.0 / (k_rrf + ra) + 1.0 / (k_rrf + rb)


# ---------------------------------------------------------------------------
# Split-alignment prerequisite check (the hand-off's one flagged real risk).
# ---------------------------------------------------------------------------

def verify_split_alignment(prep, pool_lbl, cfg, seed):
    """Independently rebuild the held-out-entity split via AC's OWN split builder (a separate code copy from
    SR.G.prepare_corpus's `base.build_heldout_entity_split_ac`) and assert the resulting query_int array is
    BIT-IDENTICAL to prep['query_int']. If this ever breaches, the two mechanisms are NOT scored on the same
    queries and any fusion number is meaningless -> INCONCLUSIVE."""
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    if ent2i != prep["ent2i"] or rel2i != prep["rel2i"]:
        return False, dict(reason="ent2i_or_rel2i_mismatch")
    train_lbl2, support_lbl2, query_lbl2, hold_ids2, n_cold2 = AC.build_heldout_entity_split_ac(
        pool_lbl, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    n_query_total2 = len(query_lbl2)
    if cfg.get("n_heldout_eval") and n_query_total2 > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total2, size=cfg["n_heldout_eval"], replace=False).tolist())
        query_lbl2 = [query_lbl2[i] for i in idx]
    query_int2 = _to_int_edges(query_lbl2, ent2i, rel2i)
    support_int2 = _to_int_edges(support_lbl2, ent2i, rel2i)
    train_int2 = _to_int_edges(train_lbl2, ent2i, rel2i)
    q_ok = bool(query_int2.shape == prep["query_int"].shape and np.array_equal(query_int2, prep["query_int"]))
    s_ok = bool(support_int2.shape == prep["support_int"].shape and np.array_equal(support_int2, prep["support_int"]))
    t_ok = bool(train_int2.shape == prep["train_int"].shape and np.array_equal(train_int2, prep["train_int"]))
    aligned = bool(q_ok and s_ok and t_ok)
    return aligned, dict(query_int_matches=q_ok, support_int_matches=s_ok, train_int_matches=t_ok,
                        n_query_rebuild=int(query_int2.shape[0]), n_query_prep=int(prep["query_int"].shape[0]))


# ---------------------------------------------------------------------------
# ANCHOR-side: ADDITIVE-only fit + score (ROTATE + ORACLE from the parent cell are skipped -- not needed here).
# ---------------------------------------------------------------------------

def _mk_ckpt(ckpt_dir, ckpt_every, tag, seed):
    if ckpt_dir is None or not ckpt_every:
        return None
    return FitCheckpoint(ckpt_dir, "%s_seed%d" % (tag, seed), ckpt_every)


def fit_and_score_anchor_side(train_int, support_int, query_int, N, n_rel, cfg, device, seed, ckpt_dir=None):
    Xa, Da = fit_kge_anchor1(train_int, N, n_rel, cfg["k"], device, seed, cfg["epochs"], reciprocal=True,
                             lr=A1_LR, n_neg=cfg["n_neg"], batch_size=cfg["batch"], neg_chunk=cfg.get("neg_chunk"),
                             ckpt=_mk_ckpt(ckpt_dir, cfg.get("ckpt_every"), "additive", seed))
    Xac, support_deg = AC.build_anchor_compose_codes(Xa, Da, support_int, device)
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)   # SAME scramble scheme as parent cell
    Xscr, _ = AC.build_anchor_compose_codes(Xa, Da, support_int, device, rel_perm=rel_perm)
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)         # SAME RANDOM scheme as parent cell
    Xr = (torch.randn(N, cfg["k"], generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, cfg["k"], generator=gR) * 0.1).to(device)
    sc_anchor = additive_direct_scores(Xac, Da, query_int, device, chunk=SCORE_CHUNK)
    sc_anchor_scr = additive_direct_scores(Xscr, Da, query_int, device, chunk=SCORE_CHUNK)
    sc_random = additive_direct_scores(Xr, Dr, query_int, device, chunk=SCORE_CHUNK)
    finite = bool(torch.isfinite(sc_anchor).all().item() and torch.isfinite(sc_anchor_scr).all().item()
                 and torch.isfinite(sc_random).all().item())
    del Xa, Da, Xac, Xscr, Xr, Dr
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return dict(sc_anchor=sc_anchor, sc_anchor_scr=sc_anchor_scr, sc_random=sc_random,
               support_deg=support_deg, finite=finite)


# ---------------------------------------------------------------------------
# Degree-stratified localization (reused bin scheme from the ANCHOR cell's own weak-point localization).
# ---------------------------------------------------------------------------

def _hits_subset(scores, query_int, all_true, mask):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return dict(hits=float("nan"), mrr=float("nan"), n=0)
    sub = filtered_hits_from_scores(scores[idx], query_int[idx], all_true, ks=(10,))
    return dict(hits=round(sub["hits@10"], 5), mrr=round(sub["mrr"], 6), n=int(idx.size))


def localize_by_support_degree(arm_scores, query_int, all_true, support_deg):
    nq = query_int.shape[0]
    gold = query_int[:, 2]
    q_support = np.array([support_deg[int(g)] for g in gold], dtype=np.int64)
    out = {}
    for lo, hi, name in SUPPORT_BINS:
        mask = (q_support >= lo) & (q_support <= hi)
        out[name] = {a: _hits_subset(sc, query_int, all_true, mask) for a, sc in arm_scores.items()}
    return out


# ---------------------------------------------------------------------------
# One corpus run (one seed): builds the shared split, scores both mechanisms, fuses, localizes.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, device, seed, corpus_name, ckpt_dir=None):
    prep = SR.G.prepare_corpus(pool_lbl, cfg, seed)
    N = prep["N"]; n_rel = prep["n_rel"]
    train_int = prep["train_int"]; support_int = prep["support_int"]; query_int = prep["query_int"]
    all_true = prep["all_true"]

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(prep["hold_ids"]), n_support=int(support_int.shape[0]),
                  n_query_total=prep["n_query_total"], n_query_scored=int(query_int.shape[0]),
                  n_cold=int(prep["n_cold"]))
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    aligned, align_diag = verify_split_alignment(prep, pool_lbl, cfg, seed)
    result["split_alignment"] = dict(aligned=aligned, **align_diag)
    if not aligned:
        result["split_misaligned"] = True
        return result

    anc = fit_and_score_anchor_side(train_int, support_int, query_int, N, n_rel, cfg, device, seed, ckpt_dir=ckpt_dir)
    sr_fs = SR.score_all_arms(prep, cfg, seed)
    sc_sr = sr_fs["arm_scores"][SR.SR_COMPOSE_NYS]
    sc_sr_scr = sr_fs["arm_scores"][SR.SR_COMPOSE_NYS_SCRAMBLE]
    sc_sr_flat = sr_fs["arm_scores"][SR.SR_COMPOSE_FLAT]
    sr_finite = bool(sr_fs["diag"]["finite"])
    sr_leak = sr_fs["diag"]["leak"]

    sc_anchor = anc["sc_anchor"]; sc_anchor_scr = anc["sc_anchor_scr"]; sc_random = anc["sc_random"]

    arm_scores = {
        ANCHOR_ARM: sc_anchor, ANCHOR_SCR_ARM: sc_anchor_scr, RANDOM_ARM: sc_random,
        SR_ARM: sc_sr, SR_FLAT_ARM: sc_sr_flat, SR_SCR_ARM: sc_sr_scr,
    }
    for w in W_GRID:
        arm_scores["FUSE_SUM_w%03d" % round(w * 100)] = weighted_sum_fuse(sc_anchor, sc_sr, w)
    arm_scores[FUSE_RRF_ARM] = rrf_fuse(sc_anchor, sc_sr)
    arm_scores["FUSE_SUM_ANCHOR_SRSCR_w050"] = weighted_sum_fuse(sc_anchor, sc_sr_scr, 0.5)
    arm_scores["FUSE_SUM_ANCHORSCR_SR_w050"] = weighted_sum_fuse(sc_anchor_scr, sc_sr, 0.5)
    arm_scores["FUSE_SUM_ANCHOR_RANDOM_w050"] = weighted_sum_fuse(sc_anchor, sc_random, 0.5)
    arm_scores[SELF_FUSE_ARM] = weighted_sum_fuse(sc_anchor, sc_anchor, 0.5)
    arm_scores["FUSE_RRF_ANCHOR_SRSCR"] = rrf_fuse(sc_anchor, sc_sr_scr)
    arm_scores["FUSE_RRF_ANCHORSCR_SR"] = rrf_fuse(sc_anchor_scr, sc_sr)
    arm_scores["FUSE_RRF_ANCHOR_RANDOM"] = rrf_fuse(sc_anchor, sc_random)

    arm_metric, arm_sig = {}, {}
    for name, sc in arm_scores.items():
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=(1, 3, 10, 100))
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())

    finite = bool(anc["finite"] and sr_finite
                 and all(torch.isfinite(sc).all().item() for sc in arm_scores.values()))

    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in arm_metric[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: arm_metric[a]["n"] for a in ALL_ARMS},
        arm_sigs={a: arm_sig[a] for a in ALL_ARMS},
        localization=localize_by_support_degree(
            {ANCHOR_ARM: sc_anchor, SR_ARM: sc_sr, SR_FLAT_ARM: sc_sr_flat,
             "FUSE_SUM_w050": arm_scores["FUSE_SUM_w050"], FUSE_RRF_ARM: arm_scores[FUSE_RRF_ARM]},
            query_int, all_true, anc["support_deg"]),
        diag=dict(finite=finite, sr_finite=sr_finite, sr_leak_free=bool(sr_leak.get("leak_free", False)),
                  sr_leak=sr_leak),
    )
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps.get("arm_hits", {}).get(arm, {}).get("mrr", float("nan"))


def aggregate_and_verdict(per_seed):
    m = {a: _nm([_m(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    add_alone = m[ANCHOR_ARM]; sr_alone = m[SR_ARM]

    reproduce_add = bool(add_alone == add_alone and abs(add_alone - CITED_ADD_COMPOSE) <= REPRODUCE_TOL_ADD)
    reproduce_sr = bool(sr_alone == sr_alone and abs(sr_alone - CITED_SR_NYS) <= REPRODUCE_TOL_SR)
    split_aligned = all(bool(ps.get("split_alignment", {}).get("aligned", False)) for ps in per_seed)
    finite = all(bool(ps.get("diag", {}).get("finite", False)) for ps in per_seed)

    self_fuse_ok = bool(m[SELF_FUSE_ARM] == m[SELF_FUSE_ARM] and add_alone == add_alone
                        and abs(m[SELF_FUSE_ARM] - add_alone) <= SELF_FUSE_TOL)
    must_fail_ok = all(bool(m[a] == m[a] and m[a] <= add_alone + MUST_FAIL_EPS) for a in MUST_FAIL_ARMS)

    pos_controls_ok = bool(reproduce_add and reproduce_sr and split_aligned and finite
                           and self_fuse_ok and must_fail_ok)

    best_fusion_arm = max(FUSION_CANDIDATE_ARMS, key=lambda a: (m[a] if m[a] == m[a] else float("-inf")))
    best_fused = m[best_fusion_arm]
    lift = (best_fused - add_alone) if (best_fused == best_fused and add_alone == add_alone) else float("nan")

    # degree-scan for the HARD-FAIL clause: does SR beat ANCHOR in ANY support-degree bucket?
    bucket_sr_wins = {}
    for lo, hi, name in SUPPORT_BINS:
        cells = [ps.get("localization", {}).get(name, {}) for ps in per_seed]
        n_tot = sum(int(c.get(ANCHOR_ARM, {}).get("n", 0)) for c in cells)
        a_mrr = _nm([c.get(ANCHOR_ARM, {}).get("mrr", float("nan")) for c in cells])
        s_mrr = _nm([c.get(SR_ARM, {}).get("mrr", float("nan")) for c in cells])
        sf_mrr = _nm([c.get(SR_FLAT_ARM, {}).get("mrr", float("nan")) for c in cells])
        wins = bool(n_tot >= MIN_STRAT_Q and a_mrr == a_mrr
                   and ((s_mrr == s_mrr and s_mrr > a_mrr) or (sf_mrr == sf_mrr and sf_mrr > a_mrr)))
        bucket_sr_wins[name] = dict(n=n_tot, anchor_mrr=_r(a_mrr), sr_nys_mrr=_r(s_mrr), sr_flat_mrr=_r(sf_mrr),
                                    sr_wins=wins)
    any_bucket_sr_wins = any(v["sr_wins"] for v in bucket_sr_wins.values())

    if not pos_controls_ok:
        verdict = "INCONCLUSIVE_FUSION_PRECONDITION_FAILED"
    elif lift == lift and lift >= LIFT_ABS:
        verdict = "HARD_PASS_SR_ADDITIVE_FUSION"
    elif lift == lift and lift <= 0.0 and not any_bucket_sr_wins:
        verdict = "HARD_FAIL_FUSION_ADDS_NOTHING_CORRELATED_ERRORS"
    else:
        verdict = "MIDDLE_BAND_FUSION_SMALL_OR_CONCENTRATED"

    verdict_msg = (
        "%s || ADD_ALONE=%s(cited%.5f,repro=%s) SR_ALONE=%s(cited%.5f,repro=%s) || best_fusion=%s=%s lift=%s "
        "(need>=%.3f) || must_fail_ok=%s self_fuse_ok=%s split_aligned=%s finite=%s pos_controls=%s "
        "|| any_bucket_sr_wins=%s buckets=%s || seeds=%d"
        % (verdict, _fmt(add_alone), CITED_ADD_COMPOSE, reproduce_add, _fmt(sr_alone), CITED_SR_NYS, reproduce_sr,
           best_fusion_arm, _fmt(best_fused), _fmt(lift), LIFT_ABS, must_fail_ok, self_fuse_ok, split_aligned,
           finite, pos_controls_ok, any_bucket_sr_wins,
           {k: v["sr_wins"] for k, v in bucket_sr_wins.items()}, len(per_seed)))

    gates = dict(
        verdict=verdict, heldout_mrr={a: _r(m[a]) for a in ALL_ARMS},
        add_alone=_r(add_alone), sr_alone=_r(sr_alone), best_fusion_arm=best_fusion_arm, best_fused_mrr=_r(best_fused),
        lift=_r(lift), reproduce_add=reproduce_add, reproduce_sr=reproduce_sr, split_aligned=split_aligned,
        finite=finite, self_fuse_ok=self_fuse_ok, must_fail_ok=must_fail_ok, pos_controls_ok=pos_controls_ok,
        bucket_sr_wins=bucket_sr_wins, any_bucket_sr_wins=any_bucket_sr_wins,
        must_fail_arm_mrr={a: _r(m[a]) for a in MUST_FAIL_ARMS}, self_fuse_mrr=_r(m[SELF_FUSE_ARM]),
        bands=dict(LIFT_ABS=LIFT_ABS, MUST_FAIL_EPS=MUST_FAIL_EPS, SELF_FUSE_TOL=SELF_FUSE_TOL,
                   REPRODUCE_TOL_ADD=REPRODUCE_TOL_ADD, REPRODUCE_TOL_SR=REPRODUCE_TOL_SR, K_RRF=K_RRF,
                   CITED_ADD_COMPOSE=CITED_ADD_COMPOSE, CITED_ORACLE_ADDITIVE=CITED_ORACLE_ADDITIVE,
                   CITED_SR_NYS=CITED_SR_NYS, CITED_SR_FLAT=CITED_SR_FLAT, MIN_STRAT_Q=MIN_STRAT_Q),
    )
    return verdict, verdict_msg, gates


def _r(x, nd=6):
    return round(x, nd) if (x == x) else None


# ---------------------------------------------------------------------------
# Mechanism self-test (planted TransE arena, reused from AC; proves the FUSION ARITHMETIC on REAL score tensors --
# see docstring "discriminator survives scale: option B" for why joint-arena discriminator-firing is deferred to
# FULL rather than reproduced here).
# ---------------------------------------------------------------------------

def _selftest_real_code_path(cfg, device):
    """Gate F.1: construct the REAL fit + compose + score objects at tiny scale; populate exercised set."""
    exercised = set()
    pool = AC.build_planted_transe_arena(7, n_ent=60, n_rel=4, k_lat=6, deg=3)
    ent2i, rel2i = build_ids(pool, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = AC.build_heldout_entity_split_ac(
        pool, ent2i, 0.2, 0.5, 7)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    if query_int.shape[0] < 4:
        return exercised, False, None
    Xa, Da = fit_kge_anchor1(train_int, N, n_rel, 8, device, 7, 40, reciprocal=True, lr=A1_LR,
                             n_neg=8, batch_size=256)
    exercised.add("fit_kge_anchor1")
    Xac, support_deg = AC.build_anchor_compose_codes(Xa, Da, support_int, device)
    exercised.add("build_anchor_compose_codes")
    sc = additive_direct_scores(Xac, Da, query_int, device, chunk=SCORE_CHUNK)
    exercised.add("additive_direct_scores")
    # KGStore + ingest_triples (F.1 for the SR side's real substrate object, tiny scale)
    tri = np.array([[0, 0, 1], [1, 0, 2], [2, 1, 0], [3, 1, 0]], dtype=np.int64)
    store, fin = SR.G.build_store_with_codes(4, 2, 16, 7, torch.randn(4, 16), tri, fold_in=None)
    exercised.add("KGStore")
    exercised.add("build_store_with_codes")
    if store._n_triples_ingested > 0:
        exercised.add("ingest_triples")
    all_true = build_true_by_hr_int(train_int, support_int, query_int)
    m = filtered_hits_from_scores(sc, query_int, all_true, ks=(1, 10))
    fused = weighted_sum_fuse(sc, sc, 0.5)
    exercised.add("weighted_sum_fuse")
    rrf = rrf_fuse(sc, sc)
    exercised.add("rrf_fuse")
    return exercised, bool(torch.isfinite(sc).all().item() and m["n"] > 0), dict(
        n_query=int(query_int.shape[0]), N=N, sc_shape=list(sc.shape))


def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body(device):
    out = {}
    exercised, real_ok, real_diag = _selftest_real_code_path(SELFTEST_CFG, device)
    out["real_code_path_ok"] = bool(real_ok)
    out["real_diag"] = real_diag
    if not real_ok:
        out["fail"] = "real-code-path smoke did not produce finite scored queries"
        return False, out

    # Fusion-arithmetic proof: run the SAME planted TransE arena AC's own self-test uses (proven to make
    # ANCHOR_COMPOSE beat RANDOM and ANCHOR_SCRAMBLE fail), then exercise every fusion combinator on REAL scores.
    pool = AC.build_planted_transe_arena(7, n_ent=300, n_rel=6, k_lat=8, deg=3)
    cfg = dict(SELFTEST_CFG)
    prep_ent2i, prep_rel2i = build_ids(pool, [], [])
    N = len(prep_ent2i); n_rel = len(prep_rel2i)
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = AC.build_heldout_entity_split_ac(
        pool, prep_ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], 7)
    train_int = _to_int_edges(train_lbl, prep_ent2i, prep_rel2i)
    support_int = _to_int_edges(support_lbl, prep_ent2i, prep_rel2i)
    query_int = _to_int_edges(query_lbl, prep_ent2i, prep_rel2i)
    if query_int.shape[0] < cfg["min_heldout"]:
        out["fail"] = "planted TransE arena produced too few held-out queries (%d)" % query_int.shape[0]
        return False, out
    all_true = build_true_by_hr_int(train_int, support_int, query_int)

    anc = fit_and_score_anchor_side(train_int, support_int, query_int, N, n_rel, cfg, device, 7, ckpt_dir=None)
    sc_a = anc["sc_anchor"]; sc_a_scr = anc["sc_anchor_scr"]; sc_rand = anc["sc_random"]

    m_a = filtered_hits_from_scores(sc_a, query_int, all_true, ks=(10,))["mrr"]
    m_scr = filtered_hits_from_scores(sc_a_scr, query_int, all_true, ks=(10,))["mrr"]
    m_rand = filtered_hits_from_scores(sc_rand, query_int, all_true, ks=(10,))["mrr"]
    anchor_beats_random = bool(m_a - m_rand >= 0.05)
    scramble_fails = bool(m_a - m_scr >= 0.03)

    # SELF-FUSE identity: FUSE(ANCHOR,ANCHOR) at w=0.5 must equal ANCHOR alone (exact monotonic-rescale identity).
    sc_self = weighted_sum_fuse(sc_a, sc_a, 0.5)
    m_self = filtered_hits_from_scores(sc_self, query_int, all_true, ks=(10,))["mrr"]
    self_fuse_ok = bool(abs(m_self - m_a) <= SELF_FUSE_TOL)

    # MUST-FAIL: fusing ANCHOR with RANDOM (a pure-noise second channel) must not exceed ANCHOR alone by more
    # than MUST_FAIL_EPS.
    sc_fuse_rand = weighted_sum_fuse(sc_a, sc_rand, 0.5)
    m_fuse_rand = filtered_hits_from_scores(sc_fuse_rand, query_int, all_true, ks=(10,))["mrr"]
    must_fail_ok = bool(m_fuse_rand <= m_a + MUST_FAIL_EPS)
    rrf_fuse_rand = rrf_fuse(sc_a, sc_rand)
    m_rrf_rand = filtered_hits_from_scores(rrf_fuse_rand, query_int, all_true, ks=(10,))["mrr"]
    must_fail_rrf_ok = bool(m_rrf_rand <= m_a + MUST_FAIL_EPS)

    # VACUOUS-SMOKE guard: RANDOM must not reach ANCHOR on this planted arena (the fusion arithmetic proof needs a
    # real, non-trivial ANCHOR signal to fuse against).
    random_reached_anchor = bool((m_a - m_rand) <= 0.05)
    assert_discriminator_fires(random_reached_anchor, control_name=RANDOM_ARM,
                               headline_name="anchor_compose_beats_random_heldout", run_mode="self_test",
                               extra="RANDOM reached ANCHOR_COMPOSE on the planted arena -> fusion-arithmetic "
                                     "self-test has no real signal to exercise the combinators against")

    vp_ok = run_validity_preflight([
        {"kind": "positive_control", "positive_control_passed_headline_gate": bool(anchor_beats_random),
         "control_name": "ANCHOR_COMPOSE", "headline_name": "anchor_beats_random_on_planted_transe_arena",
         "extra": "the additive-only re-fit (skipping ROTATE/ORACLE) still recovers held-out tails on the "
                  "planted TransE arena, proving the re-derived scoring path is not degraded by the skip"},
        {"kind": "metric_moves", "metric_name": "fused_mrr",
         "values": [m_rand, m_scr, m_a, m_self],
         "extra": "MRR RANDOM=%.3f SCRAMBLE=%.3f ANCHOR=%.3f SELF_FUSE=%.3f: fusion arithmetic responds to real "
                  "vs null input, not frozen" % (m_rand, m_scr, m_a, m_self)},
        {"kind": "negative_control_margin", "control_scores": [m_fuse_rand, m_rrf_rand, m_rand, m_scr],
         "headline_threshold": m_a, "higher_is_pass": True, "margin": MUST_FAIL_EPS, "n_repeats_min": 3,
         "control_name": "fuse_with_noise_does_not_lift",
         "extra": "fusing ANCHOR with a pure-noise second channel (RANDOM_CODES) via weighted-sum AND RRF must not "
                  "exceed ANCHOR alone by more than MUST_FAIL_EPS"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["split_alignment", "reproduce_add", "reproduce_sr", "self_fuse_identity",
                                    "must_fail_controls", "degree_stratified_hard_fail_scan"],
         "exercised_gates": ["self_fuse_identity", "must_fail_controls"],
         "extra": "split_alignment/reproduce_add/reproduce_sr/degree-scan are FULL-only (need the real CSKG graph "
                  "+ the SR mechanism's own already-verified spectral fit); self_fuse_identity and "
                  "must_fail_controls -- the two gates that do NOT depend on the real graph -- are exercised here"},
        {"kind": "real_code_path", "full_substrate_entrypoints": exercised.union(
            {"fit_kge_anchor1", "build_anchor_compose_codes", "additive_direct_scores", "KGStore",
             "build_store_with_codes", "ingest_triples", "weighted_sum_fuse", "rrf_fuse"}),
         "exercised_entrypoints": exercised,
         "extra": "self-test constructs the REAL additive fit + compose + score objects AND the REAL KGStore, "
                  "then exercises both fusion combinators on the resulting real score tensors"},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "args_count": 7, "kwargs": {"reciprocal": True, "lr": A1_LR, "n_neg": 128, "batch_size": 8192,
                                      "neg_chunk": 16, "ckpt": None},
         "extra": "portable fit_kge_anchor1 call signature (train_edges,N,n_rel,k,device,seed,epochs positional)"},
        {"kind": "substrate_signature", "callable_obj": AC.build_anchor_compose_codes,
         "callable_name": "build_anchor_compose_codes", "args_count": 4, "kwargs": {"rel_perm": None}},
        {"kind": "substrate_signature", "callable_obj": additive_direct_scores, "callable_name": "additive_direct_scores",
         "args_count": 4, "kwargs": {"chunk": SCORE_CHUNK}},
        {"kind": "substrate_signature", "callable_obj": KGStore, "callable_name": "KGStore",
         "kwargs": {"n_ent": 1, "n_rel": 1, "n_dim": 16, "generator": None},
         "extra": "base/portable KGStore kwargs only (n_ent,n_rel,n_dim,generator); no optional init_entities"},
    ], run_mode="self_test")

    arms_differ = len(set([_sig(sc_a.numpy().ravel()), _sig(sc_a_scr.numpy().ravel()), _sig(sc_rand.numpy().ravel()),
                           _sig(sc_fuse_rand.numpy().ravel())])) >= 4

    out.update(
        n_grid_entities=N, n_query=int(query_int.shape[0]), anchor_mrr=round(m_a, 5), random_mrr=round(m_rand, 5),
        scramble_mrr=round(m_scr, 5), self_fuse_mrr=round(m_self, 5), fuse_with_random_mrr=round(m_fuse_rand, 5),
        rrf_with_random_mrr=round(m_rrf_rand, 5), anchor_beats_random=anchor_beats_random,
        scramble_fails=scramble_fails, self_fuse_ok=self_fuse_ok, must_fail_ok=must_fail_ok,
        must_fail_rrf_ok=must_fail_rrf_ok, arms_differ=arms_differ, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest",
                                     "real_code_path_F1", "substrate_signature_F2_F3"],
        arms_differ_exempted=ARMS_DIFFER_EXEMPT,
    )
    # NOTE: vp_ok is NOT included in the pass/fail gate below (matches the source cells' own convention, e.g.
    # exp_anchor_compose_inductive_entity_cskg_v1.py / exp_graph_spectral_compose_sr_ppmi_nystrom_v1.py). The
    # classes-1-4 validity-preflight checks default to WARN (bake period) and are EXPECTED to warn here for
    # full_gates_exercised (split_alignment/reproduce_add/reproduce_sr/degree-scan are FULL-only by declared
    # design, since they need the real CSKG graph -- see the full_gates_exercised extra= string above). The F.1/
    # F.2 ENFORCE-mode checks (real_code_path, substrate_signature) already RAISE ValidityPreflightError above if
    # they fail, so reaching this line means those hard gates passed; vp_ok is still reported for visibility.
    ok = bool(anchor_beats_random and scramble_fails and self_fuse_ok and must_fail_ok and must_fail_rrf_ok
              and arms_differ)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s epochs=%s d_code=%s" %
         (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["epochs"], cfg["d_code"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s anchor_beats_random=%s scramble_fails=%s self_fuse_ok=%s must_fail_ok=%s "
         "vp_ok=%s" % (st_ok, st_res.get("anchor_beats_random"), st_res.get("scramble_fails"),
                       st_res.get("self_fuse_ok"), st_res.get("must_fail_ok"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res.get("fail", st_res),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS SR_ADDITIVE_SCORE_FUSION: real fit+compose+score+KGStore objects "
                        "exercised; fusion combinators (weighted-sum, RRF) proven on real planted-arena scores; "
                        "self-fuse identity holds; fuse-with-random must-fail holds; 8 validity-preflight checks "
                        "declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"], len(pool)))
            res = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_ENTITY", ckpt_dir=out_dir)
            res["cskg_provenance"] = prov
            if res.get("empty") or res.get("split_misaligned"):
                raise RuntimeError("empty query set or SPLIT_MISALIGNMENT_BREACH seed=%d: %s"
                                  % (seed, res.get("split_alignment")))
            if res["n_query_scored"] < cfg.get("min_heldout", 20):
                raise RuntimeError("held-out query edges too few (%d)" % res["n_query_scored"])
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < (len(ALL_ARMS) - len(ARMS_DIFFER_EXEMPT)):
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs (exempted=%s)"
                                  % (seed, len(sigset), ARMS_DIFFER_EXEMPT))
            if not res["diag"]["finite"]:
                raise RuntimeError("non-finite score tensor seed=%d" % seed)
            if not res["diag"]["sr_leak_free"]:
                raise RuntimeError("SR_LEAK_AUDIT_BREACH seed=%d %s" % (seed, res["diag"]["sr_leak"]))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            ah = res["arm_hits"]
            _log("seed=%d nq=%d n_sup=%d n_cold=%d | ANCHOR=%s SR_NYS=%s SR_FLAT=%s | FUSE w050=%s RRF=%s | "
                 "must_fail[srscr=%s anchscr=%s rand=%s] self_fuse=%s (%.1fs)" %
                 (seed, res["n_query_scored"], res["n_support"], res["n_cold"],
                  _fmt(ah[ANCHOR_ARM]["mrr"]), _fmt(ah[SR_ARM]["mrr"]), _fmt(ah[SR_FLAT_ARM]["mrr"]),
                  _fmt(ah["FUSE_SUM_w050"]["mrr"]), _fmt(ah[FUSE_RRF_ARM]["mrr"]),
                  _fmt(ah["FUSE_SUM_ANCHOR_SRSCR_w050"]["mrr"]), _fmt(ah["FUSE_SUM_ANCHORSCR_SR_w050"]["mrr"]),
                  _fmt(ah["FUSE_SUM_ANCHOR_RANDOM_w050"]["mrr"]), _fmt(ah[SELF_FUSE_ARM]["mrr"]),
                  time.time() - ts))
            _hb("cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "full"):
            run_mode = _env_mode
    device = _resolve_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
