"""Stage-5 CG cell: SUCCESSOR-REPRESENTATION (SR) reachability-routing autonomous traversal -- does hop-selection
by a closed-form SR/resolvent reachability score toward the FINAL goal (the ONE signal that is both MULTI-STEP and
GOAL-CONDITIONED) recover the supplied-waypoint ceiling that BOTH prior autonomous attempts (greedy goal-cosine;
landmark/hub routing) fell short of?

BACKGROUND (two prior autonomous negatives on this exact harness). (1) grounding_multihop_autonomous_subgoal_
greedy_v1 landed MIDDLE_BAND_CG_PARTIAL: greedy goal-cosine (aim continuously at the FINAL goal) reaches
reach@2=0.181 (MEASURED@data/exp_grounding_multihop_autonomous_subgoal_greedy_v1/metrics.json:gates.cg.
autonomous_greedy_reach2), beats memoryless floor 0.121 but only 0.363x the supplied ceiling 0.499 -- a SINGLE-STEP
STATIC-embedding-distance signal, no mechanism for "does this neighbor's real multi-step future pass through G".
(2) landmark/hub routing landed HARD_FAIL reach@2=0.111 (WORSE than greedy) -- degree/centrality hub selection is
GOAL-AGNOSTIC (a hub is well-connected in general, which says nothing about being well-connected TOWARD this goal).

MECHANISM (research notes/research_successor_representation_reachability_autonomous_traversal_2026-07-09.md). The
hippocampal successor representation (SR; Dayan 1993), goal-conditioned value, and personalized PageRank / random-
walk-with-restart are THE SAME resolvent M = (I - gamma*T)^-1 (Millidge 2512.24722 states the equivalence directly).
This single object explains BOTH prior failures: it is (a) MULTI-STEP (aggregates the full discounted walk
distribution over the real transition structure, not a static one-hop embedding distance -> fixes greedy) AND (b)
GOAL-CONDITIONED (rooted at the specific target G, personalized-PageRank not global/centrality -> fixes landmark).
Because the KB graph is STATIC and FULLY KNOWN, no TD-learning is needed: closed-form model-based SR. For each final
goal G solve the sparse linear system (I - gamma*T) x = e_G (NO full inverse in principle; here a dense LU multi-RHS
solve at n~4440 is sub-second, per the note's billion-node PPR precedent) -> x[v] = M[v,G] = expected discounted
occupancy of G starting FROM v = "how strongly candidate v leads TOWARD G", multi-step + goal-conditioned. T =
row-normalized KB adjacency (the SAME symmetric typed subgraph the traversal walks; SR reachability is PURE GRAPH
STRUCTURE, seed-independent). At each hop, among the REAL local-neighborhood candidates (reuse the certified nbr
table VERBATIM), pick the neighbor maximizing x[v] (combined with the memoryless relation-bind base score so the
relation-appropriate direction stays primary and SR breaks the same-relation-sibling tie toward G). Zero new
retrieval primitive; one new scoring function (SR column lookup) + one tunable knob (the discount gamma).

GAMMA / SMEARING RISK (the note's load-bearing risk, given a dedicated knob + sweep). As gamma->1 the resolvent
converges to the GLOBAL stationary distribution -- goal-AGNOSTIC by construction (the same failure mode that sank
landmark routing, reached via gamma pushed too high). So gamma is swept: SR_GAMMA_PRIMARY = 0.85 drives the
verdict arm (pre-registered, not tuned on real data); DIAG_GAMMAS = {0.70, 0.85, 0.95} is a logged diagnostic sweep
(does reach@2 peak at an interior gamma and degrade toward 0.95, consistent with the bias-variance/smearing story?).
The winning gamma is REPORTED; it does NOT retro-drive the verdict.

ARMS (paired: identical learned codes + identical planted general chains + identical seeds across all arms; only
the QUERY/scoring differs). The first four REPRODUCE the greedy-cell / fair-test anchors VERBATIM (Gate-D pos ctrl):
  NO_CLEANUP        : global-cleanup-only chain (must-fail / anti-saturation control; collapses at reach>=2).
  MEMORYLESS        : goal-blind local decoder = the fair-test floor (repro ~0.453 @1 / 0.121 @2).
  SUPPLIED_WAYPOINT : = the fair-test GOAL_WAYPOINT MM ceiling; HANDED the true next waypoint (repro ~0.756 @1 /
                      0.500 @2). The bar the SR arm must approach.
  AUTONOMOUS_GREEDY : the plain-greedy autonomous arm just measured (~0.181 @2). The thing SR_SEEDED must BEAT.
  SR_SEEDED         : THE CG CANDIDATE. Given ONLY the FINAL goal, at each hop score REAL local neighbors by
                      (memoryless relation-bind base + SR_BOOST * normalized-SR-reachability-to-final-goal x[v]),
                      argmax, commit. x = M[:,G] via the closed-form resolvent at SR_GAMMA_PRIMARY. No handed
                      waypoint; derives every intermediate via multi-step goal-conditioned reachability.
  (diagnostic, logged not gated) SR gamma sweep over DIAG_GAMMAS on the general chains (smearing curve).

CG WIN BAR (pre-registered from the research note; verdict on SR_SEEDED reach@2). Anchors: memoryless floor 0.121,
greedy 0.181, landmark 0.111 (HARD_FAIL), supplied ceiling 0.499; gap-to-close = 0.499-0.181 = 0.318.
  HARD_PASS_CG = SR_SEEDED reach@2 >= SR_HARD_PASS (0.40) AND SR_SEEDED reach@2 > AUTONOMOUS_GREEDY reach@2
                 -> reachability recovers >=59% of the gap greedy left; materially > greedy 0.181 AND > landmark
                    0.111 -> autonomous reasoning WORKS via multi-step goal-conditioned reachability.
  HARD_FAIL_CG = SR_SEEDED reach@2 <= SR_HARD_FAIL (0.20) -> no better than greedy/landmark; SR smears (gamma too
                 high) OR the graph's reachability structure is insufficient (diagnose via the gamma-sweep curve +
                 SR non-degeneracy telemetry before pivoting).
  MIDDLE_BAND  = 0.20 < reach@2 < 0.40 -> beats greedy but short of the recover-the-gap bar.
Reported (never gated): SR-vs-greedy delta, SR-vs-supplied ratio, winning gamma, SR column non-degeneracy stats.

CAPABILITY FRAMING (3-part standard; CG claim, verify-able): DIFFERENT CHANNEL = downstream reach@2/@3 (top-1
commit chained); LIVE ALTERNATIVE = greedy goal-cosine AND landmark routing genuinely fall short at multi-hop range
(0.181 / 0.111 vs 0.499); NECESSITY = SR-reachability vs plain-greedy ablation, both paired. Report the SR-vs-
supplied RATIO and SR-vs-greedy DELTA, never an absolute bar above the ceiling.

HONESTY: REAL CG'd teacher-free relational learned codes (char-trigram + InfoNCE binding encoder) over the REAL
ConceptNet typed subgraph; top-1 commit fidelity; NO language understanding claimed. The FINAL goal handed to the
autonomous/SR arms is a legitimate part of any goal-directed traversal's own specification; INTERMEDIATE waypoints
are NOT handed (the MM->CG difference). The SR transition matrix is a one-time closed-form solve over the KNOWN
graph structure (no per-query supervision, no learning). Reuses the greedy-cell / fair-test / perhop-cleanup
VET-landed encoder/chain/nbr/local-scoping primitives VERBATIM (calibration continuity + no drift). Teacher-free,
ASCII-only, device-aware torch (cuda if available, else cpu).

## Compute architecture
class: (c) mixed with justification. Storage strategy: SHARDED (each node its own code vector; no bundling --
compositional multi-hop chaining, per META_STORAGE_STRATEGY). SR reachability = a DENSE closed-form linear solve
(I - gamma*T) x = e_G, batched multi-RHS over all unique goals (LAPACK/cuSOLVER LU factor once per gamma, reused
across seeds because T is graph-only / seed-invariant). Within each hop, all chains + all local candidates are
scored by batched matmul/einsum (cuda when available). ACROSS hops the chain is genuinely SEQUENTIAL (hop h's
candidate set depends on hop h-1's committed node) -- an inherent data dependency, not a batching flaw; same shape
as the greedy/fair-test cells which ran 3 seeds FULL in ~16s on cuda. No Python-loop matmul over independent points.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; SR_SEEDED commit-sig != AUTONOMOUS_GREEDY != SUPPLIED !=
#   MEMORYLESS != NO_CLEANUP; asserted per seed on distinct commit signatures).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0002 at n=5000). Reference points are MEASURED anchors, not a closed-
#   form floor: MEMORYLESS reach@2=0.121, greedy 0.181, landmark 0.111, SUPPLIED 0.499 (MEASURED@greedy-cell +
#   fair-test metrics.json). HARD_PASS bar 0.40 is on the achievable side (SUPPLIED demonstrated 0.499 reachable
#   with a goal signal; the question is whether SR reachability recovers most of it). crlb_reachability: OK.
# - baseline_in_band: MEMORYLESS@1 in (0.05, 0.95) (repro ~0.453). NO_CLEANUP@2 collapses (anti-saturation).
# - discriminator survives scale: the MM discriminator (SUPPLIED >> MEMORYLESS) is graph-structural and FIRES AT
#   SMOKE on the real subgraph (anti-sat gate). Mechanism CAN-fire is proven by the clean planted self-test
#   (SR_SEEDED ~ SUPPLIED and >> memoryless when the graph HAS clean reachability structure; SR column
#   non-degenerate). The CG question (SR vs greedy vs SUPPLIED on the REAL graph) is the MEASUREMENT -- smoke
#   reports it as a preview; FULL (3 seeds) is canonical. NO_CLEANUP collapses AT smoke scale (SATURATION-VACUOUS).
# - HARD_PASS strictly above floor: 0.40 is a clear categorical margin over greedy 0.181 / landmark 0.111 and >
#   HARD_FAIL 0.20 + 5% band-width; not an at-floor result.
# - HP_SCOPE: the CG win gate applies to SR_SEEDED only. SUPPLIED_WAYPOINT / MEMORYLESS / AUTONOMOUS_GREEDY =
#   positive-control reproductions (must reproduce the anchors within tolerance for the discriminator to be valid);
#   NO_CLEANUP = must-fail control (must collapse). SR gamma sweep = diagnostic (reported, not gated).
# - positive_control (Gate D): MEMORYLESS + SUPPLIED_WAYPOINT + AUTONOMOUS_GREEDY reproduce the greedy-cell /
#   fair-test MEASURED anchors AT THE MATCHED FULL regime (same n_nodes/code_dim/feat_dim/epochs/seeds/chains);
#   repro drift > 0.10 -> flag.
# - sweep axis: hop depth d in {1,2,3,4}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms x
#   all depths (arm/depth-cardinality check). Diagnostic gamma sweep on SR_SEEDED (logged, not a cardinality gate).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate. SR_GAMMA_PRIMARY (0.85) and SR_BOOST (=certified GOAL_GAMMA
#   1.5) are PRE-REGISTERED, NOT tuned on real data; the clean planted self-test verifies these let SR_SEEDED
#   recover ~SUPPLIED on a graph with clean reachability structure (signal present) and that the SR column is
#   non-degenerate, so any real-data collapse is a genuine graph-structure/smearing negative, not a mis-set knob.
#   The gamma sweep is diagnostic-only.
# - PAIRED trials (arm-comparison discriminator): all arms share identical codes + roles + seeds + graph + dim +
#   general-chain population.
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-epoch/per-seed/per-gamma flush prints).
"""

import argparse
import hashlib
import json
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

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    write_metrics,
    write_partial,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    char_trigram_features,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    SUBGRAPH_BASE_SEED,
)
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph,
    make_unitary_roles,
)
# Reuse the VET-landed numeric primitives VERBATIM (calibration continuity + no drift).
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev,
    sample_chains,
    build_typed_diradj,
    _hrr_bind_t,
    _l2t,
)
# Reuse the fair-test nbr table, k_sr, local scoring, and the MEMORYLESS / GOAL_WAYPOINT / NO_CLEANUP arms VERBATIM.
from experiments.exp_grounding_multihop_fair_test_unique_successor_goal_v1 import (  # noqa: E402
    build_nbr_table,
    build_ksr,
    run_chain_arm as ft_run_chain_arm,
    run_no_cleanup as ft_run_no_cleanup,
    MEMORYLESS as FT_MEMORYLESS,
    GOAL_WAYPOINT as FT_GOAL_WAYPOINT,
)
# Reuse the plain-greedy autonomous arm VERBATIM (the anchor SR_SEEDED must beat).
from experiments.exp_grounding_multihop_autonomous_subgoal_greedy_v1 import (  # noqa: E402
    run_autonomous_arm,
    AUTO_GAMMA,
)

ANCHOR_NAME = "grounding_multihop_sr_reachability_routing_v1"

MAX_REACH = 4
HIT_K = 10
SR_BOOST = AUTO_GAMMA        # combine weight on the (normalized [0,1]) SR reachability term; = certified GOAL_GAMMA
                             # 1.5 (pre-registered; NOT tuned on real data). SR-scaled and clamped-cosine share the
                             # [0,1] range so the same 1.5 boost is calibration-continuous with the greedy arm.
SR_GAMMA_PRIMARY = 0.85      # SR/resolvent discount for the VERDICT arm (pre-registered interior value; NOT tuned)
DIAG_GAMMAS = [0.70, 0.85, 0.95]   # diagnostic smearing sweep on SR_SEEDED (logged; does NOT drive the verdict)

# Arm names
NO_CLEANUP = "NO_CLEANUP"
MEMORYLESS = "MEMORYLESS"                        # goal-blind floor (= fair-test MEMORYLESS)
SUPPLIED_WAYPOINT = "SUPPLIED_WAYPOINT"          # MM ceiling (= fair-test GOAL_WAYPOINT); handed the true waypoint
AUTONOMOUS_GREEDY = "AUTONOMOUS_GREEDY"          # plain-greedy autonomous (aim continuously at final goal)
SR_SEEDED = "SR_SEEDED"                          # CG candidate (primary); route by SR reachability x[v]=M[v,G]
ALL_ARMS = [NO_CLEANUP, MEMORYLESS, SUPPLIED_WAYPOINT, AUTONOMOUS_GREEDY, SR_SEEDED]

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the run; from the research note). Reach = TOP-1 COMMIT accuracy.
# ---------------------------------------------------------------------------
SR_HARD_PASS = 0.40         # HARD_PASS: SR_SEEDED reach@2 >= this AND > AUTONOMOUS_GREEDY reach@2
SR_HARD_FAIL = 0.20         # HARD_FAIL: SR_SEEDED reach@2 <= this (indistinguishable from greedy 0.181)

# Anti-saturation / must-fail control (mirrors greedy / landmark cells)
BASE_COLLAPSE_ABS = 0.10
BASE_COLLAPSE_FRAC = 0.50
BASE_IN_BAND_HI = 0.95
HOP1_PRESENT = 0.08
SUPPLIED_FIRES_MIN = 0.10   # MM discriminator: SUPPLIED reach@2 >= MEMORYLESS reach@2 + this (must fire at scale)
SR_DEGEN_STD_MIN = 1e-4     # SR non-degeneracy: mean per-goal std of the normalized SR column >= this (not uniform)

# Gate-D positive-control reproduction anchors (MEASURED@greedy-cell + fair-test metrics.json) + tolerance (FULL)
REPRO_MEM1 = 0.453
REPRO_SUP1 = 0.756
REPRO_SUP2 = 0.500
REPRO_AUTO2 = 0.181
REPRO_TOL = 0.10


def _resolve_device(arg_device):
    if arg_device == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics (SCHEMA-VET section 13)
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(
        pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode,
        expected_n_units=expected_n_units, host=platform.node(),
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(
        verdict="CELL_CRASHED",
        verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
        summary=("CELL_CRASHED: %s" % type(exc).__name__),
        elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME,
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Config profiles. SMOKE exercises the SAME arms / same code path as FULL; only scale differs.
# FULL config is IDENTICAL to the greedy/fair-test FULL_CFG so anchors reproduce (Gate-D positive control).
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(seeds=[7], n_nodes=400, epochs=10, batch=256, code_dim=128, feat_dim=1024,
                    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                    n_chains=200, chain_chunk=256)
SMOKE_CFG = dict(seeds=[7, 13], n_nodes=1800, epochs=60, batch=256, code_dim=512, feat_dim=4096,
                 temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                 n_chains=700, chain_chunk=256)
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=5000, epochs=140, batch=512, code_dim=2048, feat_dim=8192,
                temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                n_chains=1200, chain_chunk=256)


# ---------------------------------------------------------------------------
# SR / resolvent machinery. T = row-normalized adjacency of the SAME dir_adj the traversal walks (symmetric typed
# subgraph). SR reachability x = M[:,G] = (I - gamma*T)^-1 e_G, x[v] = expected discounted occupancy of G from v.
# Because T >= 0 and gamma < 1, M = sum_t gamma^t T^t >= 0 elementwise (no negative SR values). Dense LU factored
# once per gamma (T is graph-only / seed-invariant), reused across seeds; batched multi-RHS solve over unique goals.
# ---------------------------------------------------------------------------

def build_transition_dense(dir_adj, n_nodes, device, dtype=torch.float32):
    """T [n,n] row-stochastic: T[u,v] = (#edges u->v) / out_degree(u). Dangling rows (deg 0) stay all-zero
    (a node with no out-edges never leaves -> M[dangling, G] = 0 for G != dangling; PPR-standard dangling handling
    without teleport, which is correct for a strict reachability score)."""
    rows = []
    cols = []
    for u in range(n_nodes):
        for (v, _r) in dir_adj[u]:
            rows.append(u)
            cols.append(int(v))
    A = np.zeros((n_nodes, n_nodes), dtype=np.float64)
    if rows:
        np.add.at(A, (np.asarray(rows, dtype=np.int64), np.asarray(cols, dtype=np.int64)), 1.0)
    deg = A.sum(axis=1, keepdims=True)
    deg[deg == 0.0] = 1.0
    T = (A / deg).astype(np.float32)
    return torch.from_numpy(T).to(device=device, dtype=dtype)


class SRSolver:
    """Closed-form SR column solver. LU-factors (I - gamma*T) once per gamma (cached across seeds), then solves
    (I - gamma*T) X = E for the unique-goal one-hot RHS matrix E. Falls back to torch.linalg.solve if lu_* absent."""

    def __init__(self, T_dense, device):
        self.T = T_dense
        self.n = int(T_dense.shape[0])
        self.device = device
        self.dtype = T_dense.dtype
        self._lu = {}

    def _factor(self, gamma):
        key = round(float(gamma), 6)
        if key not in self._lu:
            A = torch.eye(self.n, device=self.device, dtype=self.dtype) - float(gamma) * self.T
            try:
                self._lu[key] = ("lu", torch.linalg.lu_factor(A))
            except Exception:
                self._lu[key] = ("A", A)   # fallback: keep A, solve per call
        return self._lu[key]

    def columns(self, goals_unique, gamma):
        """Returns X [n, U] with X[:,j] = M[:, goals_unique[j]] at the given gamma."""
        goals_unique = np.asarray(goals_unique, dtype=np.int64)
        U = int(goals_unique.shape[0])
        E = torch.zeros(self.n, U, device=self.device, dtype=self.dtype)
        gj = torch.from_numpy(goals_unique).to(self.device)
        E[gj, torch.arange(U, device=self.device)] = 1.0
        kind, obj = self._factor(gamma)
        if kind == "lu":
            LU, piv = obj
            X = torch.linalg.lu_solve(LU, piv, E)
        else:
            X = torch.linalg.solve(obj, E)
        return X   # [n, U], >= 0


def sr_boost_by_chain(sr_solver, goals, gamma, n_nodes, device):
    """Per-chain normalized SR reachability toward that chain's FINAL goal, padded with a zero column at index n.
    Returns (sr_p [C, n+1], stats). sr_p[c, v] = M[v, goal_c] / max_w M[w, goal_c] in [0,1] (goal itself ~1.0;
    graph-unreachable-from ~0.0). The pad column (index n) is 0 so gather at the nbr-table pad index yields 0."""
    goals = np.asarray(goals, dtype=np.int64)
    uniq, inv = np.unique(goals, return_inverse=True)
    X = sr_solver.columns(uniq, gamma)                       # [n, U] >= 0
    colmax = X.max(dim=0).values.clamp(min=1e-12)            # [U] ~ self-occupancy of each goal
    Xn = X / colmax[None, :]                                 # [n, U] in [0,1]
    inv_t = torch.from_numpy(inv.astype(np.int64)).to(device)
    sr_by_chain = Xn.index_select(dim=1, index=inv_t).t().contiguous()   # [C, n]
    C = sr_by_chain.shape[0]
    pad = torch.zeros(C, 1, device=device, dtype=sr_by_chain.dtype)
    sr_p = torch.cat([sr_by_chain, pad], dim=1)              # [C, n+1]
    # non-degeneracy telemetry: per-goal std of the normalized column (uniform column -> std 0 -> smeared/useless)
    col_std = Xn.std(dim=0)                                  # [U]
    col_peak = (X.max(dim=0).values / X.mean(dim=0).clamp(min=1e-12))    # [U] peakedness (uniform -> ~1)
    stats = dict(gamma=float(gamma), n_unique_goals=int(uniq.shape[0]),
                 sr_col_std_mean=float(col_std.mean().item()),
                 sr_col_peak_mean=float(col_peak.mean().item()),
                 sr_col_max_mean=float(X.max(dim=0).values.mean().item()))
    return sr_p, stats


# ---------------------------------------------------------------------------
# SR-SEEDED arm: greedy hop-selection by SR reachability toward the FINAL goal. score(candidate v) =
# <l2(pred_memoryless), Z[v]> + SR_BOOST * sr_scaled[v], where sr_scaled[v] = normalized M[v, final_goal]. The base
# memoryless bind-score keeps the relation-appropriate direction primary; the SR term breaks the same-relation
# sibling tie toward the neighbor whose real multi-step future best passes through the goal. Reuses local-
# neighborhood scoping (nbr_idx) VERBATIM; only the boost (SR reachability instead of goal-cosine) differs from the
# plain-greedy arm.
# ---------------------------------------------------------------------------

def run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, start, targets, role_ids,
               device, chunk, n_nodes, sr_p, boost_weight):
    L = len(targets)
    C = start.shape[0]
    cur = torch.from_numpy(start).to(device)
    reach = {}
    hit10 = {}
    commit_sig = []
    for h in range(L):
        role = roles_t[torch.from_numpy(role_ids[h]).to(device)]
        cue = Z[cur.clamp(max=n_nodes - 1)]
        pred = _hrr_bind_t(role, cue)
        tgt = torch.from_numpy(targets[h]).to(device)
        committed = torch.full((C,), n_nodes, dtype=torch.long, device=device)
        hitk = torch.zeros(C, dtype=torch.bool, device=device)
        for b0 in range(0, C, chunk):
            b1 = min(C, b0 + chunk)
            cur_blk = cur[b0:b1]
            pred_blk = pred[b0:b1]
            cand = nbr_idx[cur_blk]                          # [b, Dmax] real local out-neighbors
            mask = nbr_mask[cur_blk]                         # [b, Dmax]
            Zc = Zp[cand]                                    # [b, Dmax, d]
            p = _l2t(pred_blk)
            base = torch.einsum("bd,bkd->bk", p, Zc)         # memoryless local score
            srb = torch.gather(sr_p[b0:b1], 1, cand)         # [b, Dmax] raw SR reachability of each candidate to goal
            # WITHIN-CANDIDATE min-max normalization: "pick the neighbor maximizing x[v]" -- the reachability-best
            # local candidate gets the full +boost, the worst gets +0, ties broken by the memoryless base score.
            # Scale-robust across hop depth (the raw resolvent value decays as (gamma/deg)^depth); if the SR values
            # are uninformative/uniform over the candidates (smeared), the range collapses -> srn ~ 0 -> the arm
            # degrades gracefully toward the memoryless floor (never below it) rather than steering on amplified
            # noise beyond what the [0,1] cap allows.
            srb_hi = srb.masked_fill(~mask, float("-inf")).max(dim=1, keepdim=True).values   # [b,1] over valid cands
            srb_lo = srb.masked_fill(~mask, float("inf")).min(dim=1, keepdim=True).values    # [b,1]
            srn = (srb - srb_lo) / (srb_hi - srb_lo).clamp(min=1e-12)
            srn = srn.masked_fill(~mask, 0.0)
            s = base + boost_weight * srn
            s = s.masked_fill(~mask, float("-inf"))
            nonempty = mask.any(dim=1)
            la = s.argmax(dim=1)
            b_ids = torch.arange(cur_blk.shape[0], device=device)
            picked = cand[b_ids, la]
            committed[b0:b1] = torch.where(nonempty, picked, torch.full_like(picked, n_nodes))
            topk = s.topk(min(HIT_K, s.shape[1]), dim=1).indices
            topk_ids = torch.gather(cand, 1, topk)
            hitk[b0:b1] = (topk_ids == tgt[b0:b1, None]).any(dim=1) & nonempty
        reach[h + 1] = float((committed == tgt).float().mean().item())
        hit10[h + 1] = float(hitk.float().mean().item())
        commit_sig.append(committed.detach().to("cpu").numpy().astype(np.int64))
        cur = committed
    sig = hashlib.sha256(np.concatenate(commit_sig).tobytes()).hexdigest()
    return reach, hit10, sig


# ---------------------------------------------------------------------------
# Per-seed run: all arms on the identical general-chain population + identical learned codes (paired). SR columns
# depend ONLY on the graph (seed-invariant): the LU factorization is cached inside sr_solver across seeds; only the
# per-seed chain goals differ, so per seed we solve for that seed's unique goals via the cached factor.
# ---------------------------------------------------------------------------

def run_seed(seed, node_words, edges, rels, dir_adj, ksr_map, has_rel, roles_t,
             nbr_idx, nbr_rel, nbr_mask, mean_out_deg, sr_solver, T, cfg, device, out_dir=None):
    n_nodes = len(node_words)
    chunk = cfg["chain_chunk"]
    X = char_trigram_features(node_words, cfg["feat_dim"])
    Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_sr")
    enc_dig = hashlib.sha256(Z.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()
    Zp = torch.cat([Z, torch.zeros(1, cfg["code_dim"], device=device)], dim=0)

    # general chains (IDENTICAL rng offset + sampler as the greedy/fair-test cell -> paired reproduction)
    gen_rng = np.random.default_rng(seed + 909)
    g_start, g_targets, g_role = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, gen_rng)
    Cg = int(g_start.shape[0])
    goals = g_targets[MAX_REACH - 1]            # final goal per chain = chain terminal node

    arms = {}
    sigs = {}
    # NO_CLEANUP (fair-test verbatim)
    r, h, _sa, sig = ft_run_no_cleanup(Z, roles_t, g_start, g_targets, g_role, device, n_nodes)
    arms[NO_CLEANUP] = dict(reach=r, hit10=h)
    sigs[NO_CLEANUP] = sig
    # MEMORYLESS + SUPPLIED_WAYPOINT (fair-test verbatim -> Gate-D positive-control reproduction)
    r, h, _sa, sig = ft_run_chain_arm(FT_MEMORYLESS, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                      g_start, g_targets, g_role, device, chunk, n_nodes)
    arms[MEMORYLESS] = dict(reach=r, hit10=h)
    sigs[MEMORYLESS] = sig
    r, h, _sa, sig = ft_run_chain_arm(FT_GOAL_WAYPOINT, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                      g_start, g_targets, g_role, device, chunk, n_nodes)
    arms[SUPPLIED_WAYPOINT] = dict(reach=r, hit10=h)
    sigs[SUPPLIED_WAYPOINT] = sig
    # AUTONOMOUS_GREEDY (plain-greedy autonomous anchor -> the thing SR must beat)
    r, h, sig, vg = run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                       device, chunk, n_nodes, AUTO_GAMMA, verify=False)
    arms[AUTONOMOUS_GREEDY] = dict(reach=r, hit10=h, greedy_stats=vg)
    sigs[AUTONOMOUS_GREEDY] = sig
    # SR_SEEDED (primary CG candidate; SR reachability at SR_GAMMA_PRIMARY)
    sr_p, sr_stats = sr_boost_by_chain(sr_solver, goals, SR_GAMMA_PRIMARY, n_nodes, device)
    _log("  seed=%d SR columns @gamma=%.2f: uniq_goals=%d col_std_mean=%.4g col_peak_mean=%.2f" % (
        seed, SR_GAMMA_PRIMARY, sr_stats["n_unique_goals"], sr_stats["sr_col_std_mean"],
        sr_stats["sr_col_peak_mean"]))
    r, h, sig = run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                           device, chunk, n_nodes, sr_p, SR_BOOST)
    arms[SR_SEEDED] = dict(reach=r, hit10=h, sr_stats=sr_stats)
    sigs[SR_SEEDED] = sig

    # diagnostic gamma sweep on SR_SEEDED (logged only; does NOT drive the verdict) -- the smearing curve
    gamma_sweep = {}
    for gg in DIAG_GAMMAS:
        sr_pg, sr_sg = sr_boost_by_chain(sr_solver, goals, gg, n_nodes, device)
        rr, _hh, _ss = run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                  device, chunk, n_nodes, sr_pg, SR_BOOST)
        gamma_sweep["%.2f" % gg] = dict(reach={dd: rr[dd] for dd in range(1, MAX_REACH + 1)},
                                        sr_col_std_mean=sr_sg["sr_col_std_mean"],
                                        sr_col_peak_mean=sr_sg["sr_col_peak_mean"])

    for arm in ALL_ARMS:
        _log("  seed=%d %-18s reach@[1..%d]=%s" % (
            seed, arm, MAX_REACH, {dd: round(arms[arm]["reach"][dd], 3) for dd in range(1, MAX_REACH + 1)}))

    return dict(seed=seed, arms=arms, arm_sigs=sigs, encoder_digest=enc_dig, n_general=Cg,
                gamma_sweep=gamma_sweep, sr_gamma_primary=SR_GAMMA_PRIMARY, sr_boost=SR_BOOST,
                code_dim=cfg["code_dim"], mean_out_deg=mean_out_deg)


# ---------------------------------------------------------------------------
# Aggregate + CG verdict
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, meta, cfg):
    def R(arm, d):
        return _nm([m["arms"][arm]["reach"][d] for m in per_seed])

    base1 = R(NO_CLEANUP, 1); base2 = R(NO_CLEANUP, 2)
    mem1 = R(MEMORYLESS, 1); mem2 = R(MEMORYLESS, 2); mem3 = R(MEMORYLESS, 3)
    sup1 = R(SUPPLIED_WAYPOINT, 1); sup2 = R(SUPPLIED_WAYPOINT, 2); sup3 = R(SUPPLIED_WAYPOINT, 3)
    auto1 = R(AUTONOMOUS_GREEDY, 1); auto2 = R(AUTONOMOUS_GREEDY, 2); auto3 = R(AUTONOMOUS_GREEDY, 3)
    sr1 = R(SR_SEEDED, 1); sr2 = R(SR_SEEDED, 2); sr3 = R(SR_SEEDED, 3)

    # CG headline metrics (primary = SR_SEEDED)
    ratio2 = (sr2 / sup2) if (sup2 == sup2 and sup2 > 1e-9) else float("nan")
    ratio3 = (sr3 / sup3) if (sup3 == sup3 and sup3 > 1e-9) else float("nan")
    delta2_vs_greedy = (sr2 - auto2) if (sr2 == sr2 and auto2 == auto2) else float("nan")
    delta2_vs_mem = (sr2 - mem2) if (sr2 == sr2 and mem2 == mem2) else float("nan")

    # SR non-degeneracy (mean over seeds of the primary-gamma column std)
    sr_col_std = _nm([m["arms"][SR_SEEDED]["sr_stats"]["sr_col_std_mean"] for m in per_seed])
    sr_col_peak = _nm([m["arms"][SR_SEEDED]["sr_stats"]["sr_col_peak_mean"] for m in per_seed])
    sr_not_degenerate = bool(sr_col_std == sr_col_std and sr_col_std >= SR_DEGEN_STD_MIN)

    # winning gamma from the diagnostic sweep (reach@2 mean over seeds)
    gamma_reach2 = {}
    for gk in ["%.2f" % gg for gg in DIAG_GAMMAS]:
        gamma_reach2[gk] = _nm([m["gamma_sweep"][gk]["reach"][2] for m in per_seed
                                if gk in m.get("gamma_sweep", {})])
    valid_g = {k: v for k, v in gamma_reach2.items() if v == v}
    winning_gamma = max(valid_g, key=valid_g.get) if valid_g else "nan"

    # anti-saturation + baseline-in-band + MM-discriminator-fires
    hop1_present = bool(mem1 == mem1 and mem1 >= HOP1_PRESENT)
    baseline_in_band = bool(mem1 == mem1 and 0.05 < mem1 < BASE_IN_BAND_HI)
    baseline_collapses = bool(base2 == base2 and base1 == base1
                              and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))
    supplied_fires = bool(sup2 == sup2 and mem2 == mem2 and sup2 >= mem2 + SUPPLIED_FIRES_MIN)

    # CG gates (on SR_SEEDED reach@2)
    sr_hard_pass = bool(sr2 == sr2 and auto2 == auto2 and sr2 >= SR_HARD_PASS and sr2 > auto2)
    sr_hard_fail = bool(sr2 == sr2 and sr2 <= SR_HARD_FAIL)

    # Gate-D reproduction audit (only meaningful at FULL config == anchor regime)
    is_full = bool(len(cfg["seeds"]) == 3 and cfg["n_nodes"] == 5000 and cfg["code_dim"] == 2048)
    repro_mem1_ok = bool(mem1 == mem1 and abs(mem1 - REPRO_MEM1) <= REPRO_TOL)
    repro_sup1_ok = bool(sup1 == sup1 and abs(sup1 - REPRO_SUP1) <= REPRO_TOL)
    repro_sup2_ok = bool(sup2 == sup2 and abs(sup2 - REPRO_SUP2) <= REPRO_TOL)
    repro_auto2_ok = bool(auto2 == auto2 and abs(auto2 - REPRO_AUTO2) <= REPRO_TOL)
    repro_ok = bool(repro_mem1_ok and repro_sup1_ok and repro_sup2_ok and repro_auto2_ok)

    # ---- overall verdict ----
    if not hop1_present:
        verdict = "INCONCLUSIVE_HOP1_ABSENT"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif not supplied_fires:
        verdict = "INCONCLUSIVE_SUPPLIED_MM_DID_NOT_FIRE"
    elif not sr_not_degenerate:
        verdict = "INCONCLUSIVE_SR_COLUMN_DEGENERATE"
    elif is_full and not repro_ok:
        verdict = "INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT"
    elif sr_hard_pass:
        verdict = "HARD_PASS_CG_SR_REACHABILITY"
    elif sr_hard_fail:
        verdict = "HARD_FAIL_CG_SR_VACUOUS"
    else:
        verdict = "MIDDLE_BAND_CG_SR_PARTIAL"

    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f @2=%.3f(collapses=%s) || MEMORYLESS @1=%.3f(in_band=%s) @2=%.3f @3=%.3f || "
        "SUPPLIED_WAYPOINT @1=%.3f @2=%.3f @3=%.3f (fires=%s) || AUTONOMOUS_GREEDY @1=%.3f @2=%.3f @3=%.3f || "
        "SR_SEEDED @1=%.3f @2=%.3f @3=%.3f || CG: ratio@2(sr/sup)=%s ratio@3=%s delta@2(sr-greedy)=%s "
        "delta@2(sr-mem)=%s || SR: gamma_primary=%.2f boost=%.2f col_std=%.4g col_peak=%.2f nondegen=%s "
        "sweep_reach2=%s winning_gamma=%s || HARD_PASS=(sr2>=%.2f AND sr2>greedy2)=%s HARD_FAIL=(sr2<=%.2f)=%s || "
        "repro(full=%s): mem1=%s sup1=%s sup2=%s auto2=%s || n_gen=%d nodes=%d E=%d rel=%d seeds=%d run=%s" % (
            verdict, base1, base2, baseline_collapses, mem1, baseline_in_band, mem2, mem3,
            sup1, sup2, sup3, supplied_fires, auto1, auto2, auto3, sr1, sr2, sr3,
            _fmt(ratio2), _fmt(ratio3), _fmt(delta2_vs_greedy), _fmt(delta2_vs_mem),
            SR_GAMMA_PRIMARY, SR_BOOST, sr_col_std, sr_col_peak, sr_not_degenerate,
            {k: round(v, 3) for k, v in gamma_reach2.items()}, winning_gamma,
            SR_HARD_PASS, sr_hard_pass, SR_HARD_FAIL, sr_hard_fail, is_full,
            repro_mem1_ok, repro_sup1_ok, repro_sup2_ok, repro_auto2_ok,
            per_seed[0]["n_general"], meta["n_nodes"], meta["n_edges"],
            meta.get("n_relation_types", -1), len(per_seed), "full" if is_full else "smoke"))

    gates = dict(
        verdict=verdict,
        reach={a: {d: R(a, d) for d in range(1, MAX_REACH + 1)} for a in ALL_ARMS},
        cg=dict(memoryless_reach2=mem2, supplied_reach2=sup2, autonomous_greedy_reach2=auto2,
                sr_seeded_reach1=sr1, sr_seeded_reach2=sr2, sr_seeded_reach3=sr3,
                ratio2=ratio2, ratio3=ratio3, delta2_vs_greedy=delta2_vs_greedy, delta2_vs_mem=delta2_vs_mem,
                sr_hard_pass=sr_hard_pass, sr_hard_fail=sr_hard_fail,
                sr_col_std_mean=sr_col_std, sr_col_peak_mean=sr_col_peak, sr_not_degenerate=sr_not_degenerate,
                gamma_sweep_reach2=gamma_reach2, winning_gamma=winning_gamma),
        anti_sat=dict(hop1_present=hop1_present, baseline_in_band=baseline_in_band,
                      baseline_collapses=baseline_collapses, supplied_fires=supplied_fires,
                      sr_not_degenerate=sr_not_degenerate),
        positive_control=dict(is_full=is_full, repro_mem1=mem1, repro_sup1=sup1, repro_sup2=sup2, repro_auto2=auto2,
                              repro_mem1_ok=repro_mem1_ok, repro_sup1_ok=repro_sup1_ok, repro_sup2_ok=repro_sup2_ok,
                              repro_auto2_ok=repro_auto2_ok, repro_ok=repro_ok,
                              anchors=dict(mem1=REPRO_MEM1, sup1=REPRO_SUP1, sup2=REPRO_SUP2, auto2=REPRO_AUTO2,
                                           tol=REPRO_TOL)),
        bands=dict(SR_HARD_PASS=SR_HARD_PASS, SR_HARD_FAIL=SR_HARD_FAIL, SUPPLIED_FIRES_MIN=SUPPLIED_FIRES_MIN,
                   SR_DEGEN_STD_MIN=SR_DEGEN_STD_MIN, BASE_COLLAPSE_ABS=BASE_COLLAPSE_ABS,
                   HOP1_PRESENT=HOP1_PRESENT, SR_GAMMA_PRIMARY=SR_GAMMA_PRIMARY, SR_BOOST=SR_BOOST,
                   DIAG_GAMMAS=DIAG_GAMMAS),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test (planted BRANCH graph with clean reachability structure + real local scoping).
# Proves: chain machinery works; NO_CLEANUP collapses; MEMORYLESS aliased (~1/k on same-relation branch points);
# SUPPLIED recovers via one-step waypoint lookahead; and -- the load-bearing positive control for THIS cell -- when
# the graph HAS clean reachability structure (the on-path true successor is forward-connected to the goal, the KSR-1
# off-path siblings are structural dead-ends), SR_SEEDED recovers ~SUPPLIED and >> MEMORYLESS because M[on_path,G]
# >> M[off_path,G] ~ 0. Also asserts the SR column is NON-DEGENERATE (not smeared to a uniform / useless vector).
# So a real-data collapse would be a genuine graph-structure / smearing negative, not a broken mechanism or a
# mis-set gamma. arms differ.
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    device = torch.device("cpu")
    torch.manual_seed(0)
    np.random.seed(0)
    rng = np.random.default_rng(0)
    d = 96
    T = 4
    KSR = 3
    n_cap = 3200
    roles_t = torch.from_numpy(make_unitary_roles(T, d, np.random.default_rng(11))).to(device)

    Z2 = torch.zeros(n_cap, d, device=device)
    dir_adj = [[] for _ in range(n_cap)]
    next_id = 0

    def _new(code):
        nonlocal next_id
        Z2[next_id] = _l2t(code[None, :])[0]
        nid = next_id
        next_id += 1
        return nid

    # BRANCH chains with CLEAN REACHABILITY STRUCTURE. At each hop the true successor (relation-consistent code =
    # pred + small noise) is forward-connected to the next hop and thus to the terminal goal G; the KSR-1 off-path
    # siblings (relation-consistent code = pred + noise, so the memoryless base term CANNOT separate them) get NO
    # onward edges -> they are structural dead-ends -> M[off, G] ~ 0 while M[true, G] > 0. MEMORYLESS is aliased
    # (~1/k); SUPPLIED recovers via one-step lookahead onto the known next waypoint; SR_SEEDED recovers via graph
    # reachability (the resolvent ranks the on-path forward node above the dead-end siblings). No planted CODE goal
    # component is needed -- SR reads GRAPH STRUCTURE, not the embedding.
    # All KSR same-relation siblings share an IDENTICAL code distribution (pred + 0.5*noise) so the memoryless base
    # term CANNOT separate them (aliased ~1/KSR); the true successor is chosen at RANDOM among them, then ONLY the
    # true successor is forward-connected to the next hop (the off-path siblings get no onward edges -> structural
    # dead-ends -> M[off, G] = 0). SUPPLIED recovers via one-step lookahead onto the known next waypoint; SR_SEEDED
    # recovers via graph reachability (only the on-path forward node reaches G). No planted CODE goal component.
    br_start, br_tgt, br_rid = [], [[] for _ in range(MAX_REACH)], [[] for _ in range(MAX_REACH)]
    for _c in range(110):
        if next_id >= n_cap - (MAX_REACH * KSR + 6):
            break
        cur = _new(_l2t(torch.randn(1, d))[0])               # chain start
        start_node = cur
        for h in range(MAX_REACH):
            r = int(rng.integers(0, T))
            pred = _l2t(_hrr_bind_t(roles_t[r:r + 1], _l2t(Z2[cur:cur + 1])))[0]
            sibs = []
            for _k in range(KSR):
                v = _new(pred + 0.5 * _l2t(torch.randn(1, d))[0])   # aliased sibling (shares the query point)
                dir_adj[cur].append((v, r))
                sibs.append(v)
            true_v = sibs[int(rng.integers(0, KSR))]         # ONE planted true successor (random among siblings)
            br_tgt[h].append(true_v); br_rid[h].append(r)
            cur = true_v                                     # only the true successor continues -> path reaches G
        br_start.append(start_node)
    g_start = np.asarray(br_start, dtype=np.int64)
    g_tgt = [np.asarray(t, dtype=np.int64) for t in br_tgt]
    g_role = [np.asarray(r, dtype=np.int64) for r in br_rid]

    n = next_id
    Z2 = Z2[:n]
    dir_adj = dir_adj[:n]
    Z = _l2t(Z2)
    Zp = torch.cat([Z, torch.zeros(1, d, device=device)], dim=0)
    nbr_idx, nbr_rel, nbr_mask, Dmax, _mod = build_nbr_table(dir_adj, n, device)
    _ksr_map, has_rel = build_ksr(dir_adj, n, T, device)

    # SR solver over the planted graph; goals = chain terminals
    T_dense = build_transition_dense(dir_adj, n, device)
    sr_solver = SRSolver(T_dense, device)
    goals = g_tgt[MAX_REACH - 1]
    sr_p, sr_stats = sr_boost_by_chain(sr_solver, goals, SR_GAMMA_PRIMARY, n, device)

    # direct reachability discrimination stat: for each chain, at hop-1 branch, M[true_hop1, G] vs max off-sibling.
    # We recover it from the normalized column via the nbr table of each start node.
    uniq, inv = np.unique(np.asarray(goals, dtype=np.int64), return_inverse=True)
    Xcol = sr_solver.columns(uniq, SR_GAMMA_PRIMARY)                 # [n, U]
    true_gt_off = []
    for ci in range(g_start.shape[0]):
        s0 = int(g_start[ci]); col = int(inv[ci])
        nbrs = [int(v) for (v, _r) in dir_adj[s0]]
        true1 = int(g_tgt[0][ci])
        offs = [v for v in nbrs if v != true1]
        if not offs:
            continue
        m_true = float(Xcol[true1, col].item())
        m_off = max(float(Xcol[v, col].item()) for v in offs)
        true_gt_off.append(1.0 if m_true > m_off else 0.0)      # resolvent ranks on-path above off-path?
    disc_frac = float(np.mean(true_gt_off)) if true_gt_off else float("nan")

    r_no, _h, _sa, s_no = ft_run_no_cleanup(Z, roles_t, g_start, g_tgt, g_role, device, n)
    r_mem, _h, _sa, s_mem = ft_run_chain_arm(FT_MEMORYLESS, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                             g_start, g_tgt, g_role, device, 256, n)
    r_sup, _h, _sa, s_sup = ft_run_chain_arm(FT_GOAL_WAYPOINT, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                             g_start, g_tgt, g_role, device, 256, n)
    r_auto, _h, s_auto, _vg = run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_tgt, g_role,
                                                 device, 256, n, AUTO_GAMMA, verify=False)
    r_sr, _h, s_sr = run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_tgt, g_role,
                                device, 256, n, sr_p, SR_BOOST)

    nocleanup_ran = bool(r_no[1] == r_no[1])
    memoryless_aliased = bool(r_mem[1] == r_mem[1] and r_mem[1] < 0.70)          # goal-blind underdetermined (~1/k)
    supplied_reaches = bool(r_sup[2] == r_sup[2] and r_sup[2] >= 0.55)           # waypoint ceiling reachable
    sr_recovers = bool(r_sr[1] == r_sr[1] and r_mem[1] == r_mem[1]
                       and r_sr[1] >= r_mem[1] + 0.20 and r_sr[2] >= 0.50)       # SR derivation works
    sr_near_supplied = bool(r_sr[2] == r_sr[2] and r_sup[2] == r_sup[2]
                            and r_sup[2] > 1e-9 and r_sr[2] >= 0.70 * r_sup[2])  # ~matches supplied (positive ctrl)
    sr_discriminates = bool(disc_frac == disc_frac and disc_frac >= 0.90)       # resolvent ranks on-path > off-path
    sr_not_degenerate = bool(sr_stats["sr_col_std_mean"] >= SR_DEGEN_STD_MIN     # column not uniform / smeared
                             and sr_stats["sr_col_peak_mean"] >= 2.0)
    arms_differ = bool(len({s_no, s_mem, s_sup, s_auto, s_sr}) >= 4)

    res = dict(
        reach_no_cleanup={dd: round(r_no[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_memoryless={dd: round(r_mem[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_supplied={dd: round(r_sup[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_autonomous_greedy={dd: round(r_auto[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_sr_seeded={dd: round(r_sr[dd], 4) for dd in range(1, MAX_REACH + 1)},
        sr_stats=sr_stats, sr_disc_frac=disc_frac,
        nocleanup_ran=nocleanup_ran, memoryless_aliased=memoryless_aliased, supplied_reaches=supplied_reaches,
        sr_recovers=sr_recovers, sr_near_supplied=sr_near_supplied, sr_discriminates=sr_discriminates,
        sr_not_degenerate=sr_not_degenerate, arms_differ=arms_differ, Dmax=int(Dmax), n_synth=int(n),
    )
    ok = bool(nocleanup_ran and memoryless_aliased and supplied_reaches and sr_recovers
              and sr_near_supplied and sr_discriminates and sr_not_degenerate and arms_differ)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    device = _resolve_device(args.device)
    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    _log("device=%s cuda_available=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))

    st_ok, st_res = _mechanism_selftest()
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d" % ({k: meta[k] for k in ("n_nodes", "n_edges", "median_degree")}, T))
    n_nodes = len(node_ids)
    dir_adj = build_typed_diradj(edges, rels, n_nodes)
    nbr_idx, nbr_rel, nbr_mask, Dmax, mean_out_deg = build_nbr_table(dir_adj, n_nodes, device)
    ksr_map, has_rel = build_ksr(dir_adj, n_nodes, T, device)
    _log("nbr table: Dmax=%d mean_out_deg=%.3f" % (Dmax, mean_out_deg))

    t_sr = time.perf_counter()
    T_dense = build_transition_dense(dir_adj, n_nodes, device)
    sr_solver = SRSolver(T_dense, device)
    _log("SR transition matrix built (n=%d dense) in %.1fs; LU factors cached per gamma across seeds"
         % (n_nodes, time.perf_counter() - t_sr))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS SR-reachability machinery: NO_CLEANUP collapses; MEMORYLESS aliased; "
                        "SUPPLIED recovers; SR_SEEDED recovers ~SUPPLIED and >> memoryless on a clean-reachability "
                        "planted graph (M[on-path,G] >> M[off-path,G]); SR column non-degenerate; arms differ; "
                        "typed subgraph + nbr table + k_sr + SR resolvent solve exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res, subgraph_meta=meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, node_words, edges, rels, dir_adj, ksr_map, has_rel, roles_t,
                          nbr_idx, nbr_rel, nbr_mask, mean_out_deg, sr_solver, T, cfg, device,
                          out_dir=out_dir_path)
            for a in ALL_ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1)
                           if a not in pm["arms"] or dd not in pm["arms"][a]["reach"]]
                if missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            # arms must differ (META_RULE_AF)
            if pm["arm_sigs"][SR_SEEDED] == pm["arm_sigs"][AUTONOMOUS_GREEDY]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d SR_SEEDED == AUTONOMOUS_GREEDY" % seed)
            if pm["arm_sigs"][SR_SEEDED] == pm["arm_sigs"][SUPPLIED_WAYPOINT]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d SR_SEEDED == SUPPLIED" % seed)
            if pm["arm_sigs"][AUTONOMOUS_GREEDY] == pm["arm_sigs"][MEMORYLESS]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d AUTONOMOUS_GREEDY == MEMORYLESS" % seed)
            if pm["arm_sigs"][MEMORYLESS] == pm["arm_sigs"][NO_CLEANUP]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d MEMORYLESS == NO_CLEANUP" % seed)
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # per-seed failure-class instrumentation (META_RULE_J)
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (
                expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, meta, cfg)
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        device=str(device), n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        subgraph_meta=meta, gates=gates,
        mechanism_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
    )
    write_metrics(out_dir_path, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


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
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
