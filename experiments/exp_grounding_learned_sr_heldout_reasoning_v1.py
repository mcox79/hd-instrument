"""Stage-5 CG cell: LEARNED-SR HELD-OUT-SUBGRAPH reasoning -- does routing by a reachability signal DERIVED FROM THE
SUBSTRATE'S OWN LEARNED CODES (code-space-smoothed successor representation), with a disjoint subgraph WITHHELD from
both the transition matrix AND the encoder, GENERALIZE to route through structure it never saw (= REASONING) -- or
does it only work on visited structure and collapse on held-out (= memorized SEARCH)?

BACKGROUND (VET-settled). The certified SR-reachability cell (exp_grounding_multihop_sr_reachability_routing_v1,
commit c855fe88d) landed HARD_PASS reach@2=0.434 -- BUT a reciprocal-necessity self-test proved it is CLOSED-FORM
GRAPH SEARCH over the FULLY-KNOWN transition matrix T: x=(I-gamma*T)^-1 e_G is computed from the whole handed map;
aliasing the learned-code term leaves routing unchanged. That is PageRank on a handed map (MM), not substrate
reasoning (CG). The CG prize (research notes/research_learned_partial_graph_SR_reasoning_vs_search_CG_path_2026-07-09
.md + Phase-0 pre-check data/phase0_code_structure_precheck_result.json) is LEARNED reachability that GENERALIZES to
UNVISITED structure via SMOOTHNESS in the substrate's OWN learned code space.

PHASE-0 GATE (PASSED, judgment call). data/phase0_code_structure_precheck_result.json: learned codes carry graph
structure at all sizes -- 1-hop edge-detection AUC=0.818-0.980; code-kNN neighbors 8-16x enriched for graph-proximity
vs random; leakage-safe HELD-OUT edge AUC=0.681-0.731 (codes generalize proximity to edges the encoder never saw).
Size axis: held-out AUC is FLAT across n=1237->7895 (deltaM5=-0.050) => "substrate too small" is NOT the blocker; the
signal is present at every size (mild decline at large n tracks fixed code_dim capacity, not too-little-graph).
Honest caveat: seen-edge AUC (0.842-0.990) >> held-out (0.681-0.731) => generalization is PARTIAL; a MIDDLE_BAND
held-out routing result is the realistic expectation, not a runaway HARD_PASS.

MECHANISM (the disanalogy fix). Same argmax hop-selection loop as the certified cell (run_sr_arm VERBATIM); ONLY the
construction of the per-goal reachability column M[:,G] changes across arms:
  * KNOWN_T_FULL   : M from the resolvent over the FULL known T (= the certified 0.434 SEARCH baseline). Full map.
  * LEARNED_HELDOUT: a disjoint contiguous BFS-ball W of NON-goal nodes is WITHHELD from T-construction AND from the
                     encoder's training (leakage-safe: codes for withheld nodes exist -- the ProjHead maps any node's
                     char-trigram features -- but were shaped only by VISIBLE edges). M is the resolvent over VISIBLE
                     T; withheld-candidate rows M[w,:] (undefined -> ~0 in visible T, since W's edges are removed) are
                     RE-ESTIMATED by code-space smoothing: M_hat[w,G] = sum_u S[w,u] M_visible[u,G] over w's top-k
                     VISIBLE-node code-neighbors (softmax cosine weights in the VISIBLE-trained code space). Route by
                     M_hat. This is the Nystrom/heat-kernel/node2vec code-space extension.
  * HELDOUT_MEMCTRL: identical VISIBLE-T resolvent but NO smoothing (withheld-candidate rows stay ~0). "MM with a hole
                     punched in the map" -- the memorization control. If routing needs withheld candidates, this
                     collapses toward the memoryless floor. LEARNED must BEAT this (necessity of smoothing).
  * HELDOUT_CODEALIAS: identical to LEARNED_HELDOUT but the smoothing weights S are built from RANDOM codes (reciprocal
                     necessity). If held-out reach is UNCHANGED vs LEARNED, the codes are NOT doing the generalizing
                     work (leakage/artifact); if it COLLAPSES toward MEMCTRL, the codes ARE necessary (=reasoning).
Anchors reproduced VERBATIM for anti-saturation / Gate-D: NO_CLEANUP (must-fail), MEMORYLESS (floor), SUPPLIED
(MM ceiling). Every arm shares identical seeds/chains/nbr-table/graph; only the reachability signal differs (PAIRED).

DECISIVE DISCRIMINATOR (pre-registered; reach = TOP-1 COMMIT accuracy on the HELD-OUT chain subset -- chains whose
hop-1 correct successor is a WITHHELD node, so the FIRST routing decision requires estimating a withheld candidate's
reachability). learned2 = LEARNED_HELDOUT reach@2 on held-out chains; memctrl2 / codealias2 likewise; mem2 =
MEMORYLESS floor on the same subset; knownT2 = KNOWN_T_FULL on the same subset (the full-map within-subset ceiling).
  HARD_PASS_CG_REASONING = learned2 >= CG_HARD_PASS (0.32, ~80% of the certified full-graph 0.434) AND
                           learned2 >= memctrl2 + NEC_MARGIN (smoothing necessary: beats the hole-in-map control) AND
                           learned2 >= codealias2 + NEC_MARGIN (codes necessary: beats random-code smoothing)
                           -> routing GENERALIZES to held-out structure via the substrate's own codes = REASONING.
  HARD_FAIL_CG          = learned2 <= CG_HARD_FAIL (0.20; collapses toward the memoryless/hole floor) OR
                           abs(learned2 - codealias2) < NEC_MARGIN (codes not doing the work; leakage/artifact) OR
                           learned2 <= memctrl2 (smoothing adds nothing beyond the punched-hole map).
  MIDDLE_BAND           = 0.20 < learned2 < 0.32 with learned2 > memctrl2 and > codealias2 -> partial generalization
                           (the realistic Phase-0-predicted outcome): codes help but do not recover the full-map bar.
Reported (never gated): learned-vs-knownT ratio (held-out vs full-map), learned-vs-memctrl delta (necessity of
smoothing), learned-vs-codealias delta (necessity of codes), held-out chain count, withheld fraction.

CAPABILITY FRAMING (3-part CG standard, verify-able): DIFFERENT CHANNEL = held-out reach@2 (routing through withheld
structure). LIVE ALTERNATIVE = HELDOUT_MEMCTRL (punched-hole map) genuinely falls short on held-out chains. NECESSITY
= two ablations (smoothing off = MEMCTRL; codes randomized = CODEALIAS), both paired. Report RATIO to the full-map
KNOWN_T ceiling and DELTAS to the two controls, never an absolute bar above the ceiling.

HONESTY: REAL teacher-free relational learned codes (char-trigram + InfoNCE binding) over the REAL ConceptNet typed
subgraph; the held-out split withholds a disjoint node-ball from BOTH T and the encoder (genuine train/test split, no
leakage). The FINAL goal is a legitimate part of any goal-directed traversal spec; INTERMEDIATE reachability of
withheld candidates is DERIVED (code-smoothed), never handed. No language understanding claimed. Reuses the certified
SR harness (run_sr_arm / SRSolver / build_transition_dense / fair-test arms) VERBATIM. Teacher-free, ASCII-only,
device-aware torch.

## Compute architecture
class: (c) mixed with justification. Storage strategy: SHARDED (each node its own code vector; no bundling --
multi-hop compositional chaining, per META_STORAGE_STRATEGY). Two resolvent solves (full T + visible T) are dense
closed-form LU multi-RHS solves over unique goals (LAPACK/cuSOLVER, factored once per gamma). Code-smoothing is one
[|W|, |V|] cosine matmul + top-k + a [|W|, |V|]x[|V|, U] matmul per condition (batched). Within a hop all chains +
candidates scored by batched einsum. ACROSS hops the chain is inherently SEQUENTIAL (hop h candidate set depends on
h-1 commit) -- a data dependency, not a batching flaw; same shape as the certified SR cell (3 seeds FULL ~16s cuda).
No Python-loop matmul over independent points. CPU on the laptop; routes to remote_cpu_queue for FULL.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): KNOWN_T_FULL / LEARNED_HELDOUT / HELDOUT_MEMCTRL /
#   HELDOUT_CODEALIAS produce distinct commit signatures on the held-out subset (asserted per seed).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0002). Reference points MEASURED: certified full-map SR reach@2=0.434
#   (MEASURED@data/exp_grounding_multihop_sr_reachability_routing_v1/metrics.json). HARD_PASS 0.32 is on the
#   achievable side (0.434 demonstrated with full T; the question is retention under held-out). crlb_reachability: OK.
# - baseline_in_band: MEMORYLESS@1 in (0.05,0.95). NO_CLEANUP@2 collapses (anti-saturation).
# - discriminator survives scale: the SEARCH-vs-REASONING discriminator is HELDOUT_MEMCTRL (punched-hole) vs
#   LEARNED_HELDOUT; the planted self-test proves LEARNED >> MEMCTRL when codes carry recoverable structure and
#   LEARNED ~ MEMCTRL when codes are random (CODEALIAS). Smoke previews on real graph; FULL (3 seeds) canonical.
# - HARD_PASS strictly above floor: 0.32 clears HARD_FAIL 0.20 + 5% band-width; necessity margins add strictness.
# - HP_SCOPE: the CG win gate applies to LEARNED_HELDOUT only. KNOWN_T_FULL/MEMORYLESS/SUPPLIED = positive-control
#   reproductions; NO_CLEANUP = must-fail; MEMCTRL/CODEALIAS = necessity controls (LEARNED must beat both).
# - positive_control (Gate D): MEMORYLESS + SUPPLIED + KNOWN_T_FULL reproduce the certified anchors AT the matched
#   FULL regime; repro drift > 0.10 -> flag.
# - sweep axis: hop depth d in {1,2,3,4}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms x all
#   depths (arm/depth-cardinality). withheld_frac is a fixed condition, not a swept axis in v1.
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate. WITHHELD_FRAC (0.30), SMOOTH_K (8), SMOOTH_TEMP (0.10),
#   SR_GAMMA (0.85), SR_BOOST (1.5) are PRE-REGISTERED, NOT tuned on real data; the planted self-test verifies these
#   let LEARNED recover on a graph with clean recoverable structure and NOT when codes are random.
# - PAIRED trials: all arms share identical codes-per-condition + roles + seeds + graph + chain population.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import deque
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import char_trigram_features  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph, make_unitary_roles,
)
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev, sample_chains, build_typed_diradj, _l2t,
)
from experiments.exp_grounding_multihop_fair_test_unique_successor_goal_v1 import (  # noqa: E402
    build_nbr_table, build_ksr, run_chain_arm as ft_run_chain_arm, run_no_cleanup as ft_run_no_cleanup,
    MEMORYLESS as FT_MEMORYLESS, GOAL_WAYPOINT as FT_GOAL_WAYPOINT,
)
# Reuse the certified SR harness VERBATIM (routing loop + resolvent machinery).
from experiments.exp_grounding_multihop_sr_reachability_routing_v1 import (  # noqa: E402
    build_transition_dense, SRSolver, run_sr_arm, MAX_REACH, SR_GAMMA_PRIMARY, SR_BOOST,
)

ANCHOR_NAME = "grounding_learned_sr_heldout_reasoning_v1"

# Arm names
NO_CLEANUP = "NO_CLEANUP"
MEMORYLESS = "MEMORYLESS"
SUPPLIED_WAYPOINT = "SUPPLIED_WAYPOINT"
KNOWN_T_FULL = "KNOWN_T_FULL"                 # certified full-map SR (the SEARCH baseline; 0.434 anchor)
LEARNED_HELDOUT = "LEARNED_HELDOUT"           # CG candidate: visible-T resolvent + code-space smoothing of withheld
HELDOUT_MEMCTRL = "HELDOUT_MEMCTRL"           # necessity ctrl: visible-T, no smoothing (hole-in-map)
HELDOUT_CODEALIAS = "HELDOUT_CODEALIAS"       # necessity ctrl: smoothing weights from RANDOM codes (codes aliased)
ALL_ARMS = [NO_CLEANUP, MEMORYLESS, SUPPLIED_WAYPOINT, KNOWN_T_FULL,
            LEARNED_HELDOUT, HELDOUT_MEMCTRL, HELDOUT_CODEALIAS]

# ---- Pre-registered bands (picked BEFORE the run; from the research note) ----
CG_HARD_PASS = 0.32     # HARD_PASS: LEARNED_HELDOUT reach@2 >= this AND > both necessity controls (by NEC_MARGIN)
CG_HARD_FAIL = 0.20     # HARD_FAIL: LEARNED_HELDOUT reach@2 <= this (collapses toward hole/memoryless floor)
NEC_MARGIN = 0.05       # necessity margin: LEARNED must beat MEMCTRL and CODEALIAS by at least this

# Held-out construction knobs (PRE-REGISTERED; NOT tuned on real data)
WITHHELD_FRAC = 0.30    # target fraction of NON-goal nodes withheld as a contiguous BFS-ball (disjoint subgraph)
SMOOTH_K = 8            # code-kNN neighbors used for code-space smoothing of a withheld candidate's reachability
SMOOTH_TEMP = 0.10      # softmax temperature over cosine weights in the code-space smoothing
MIN_HELDOUT_CHAINS = 40 # minimum held-out chains for a valid discriminator (else INCONCLUSIVE_TOO_FEW_HELDOUT)

# Anti-saturation / must-fail control
BASE_COLLAPSE_ABS = 0.10
BASE_COLLAPSE_FRAC = 0.50
BASE_IN_BAND_HI = 0.95
HOP1_PRESENT = 0.08
SUPPLIED_FIRES_MIN = 0.10

# Gate-D positive-control reproduction anchors (MEASURED@certified SR/fair-test metrics) + tolerance (FULL only)
REPRO_MEM1 = 0.453
REPRO_SUP1 = 0.756
REPRO_SUP2 = 0.500
REPRO_KNOWNT2 = 0.434   # certified SR reach@2 (full map) on the general population
REPRO_TOL = 0.10


def _resolve_device(a):
    if a == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Config profiles. SMOKE exercises the SAME arms / code path as FULL; only scale differs.
# FULL matches the certified SR FULL_CFG so KNOWN_T_FULL reproduces the 0.434 anchor (Gate-D positive control).
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(seeds=[7], n_nodes=400, epochs=10, batch=256, code_dim=128, feat_dim=1024,
                    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                    n_chains=400, chain_chunk=256)
SMOKE_CFG = dict(seeds=[7, 13], n_nodes=1800, epochs=60, batch=256, code_dim=512, feat_dim=4096,
                 temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                 n_chains=2400, chain_chunk=256)
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=5000, epochs=140, batch=512, code_dim=2048, feat_dim=8192,
                temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                n_chains=4000, chain_chunk=256)


# ---------------------------------------------------------------------------
# Held-out split: a contiguous BFS-ball of NON-goal nodes withheld from BOTH T and the encoder.
# ---------------------------------------------------------------------------

def build_undirected_adj_simple(dir_adj, n_nodes):
    adj = [set() for _ in range(n_nodes)]
    for u in range(n_nodes):
        for (v, _r) in dir_adj[u]:
            adj[u].add(int(v))
            adj[int(v)].add(u)
    return adj


def pick_withheld_ball(adj, n_nodes, frac, forbid, rng):
    """Grow a BFS-ball from a random seed (avoiding forbidden=goal nodes) until it covers ~frac of nodes.
    Returns a boolean mask [n] of withheld nodes (all NON-goal)."""
    target = int(frac * n_nodes)
    cand = [u for u in range(n_nodes) if u not in forbid and len(adj[u]) > 0]
    if not cand:
        return np.zeros(n_nodes, dtype=bool)
    seed = int(rng.choice(cand))
    withheld = set()
    dq = deque([seed])
    seen = set([seed])
    while dq and len(withheld) < target:
        u = dq.popleft()
        if u in forbid:
            continue
        withheld.add(u)
        for v in sorted(adj[u]):
            if v not in seen:
                seen.add(v)
                dq.append(v)
    mask = np.zeros(n_nodes, dtype=bool)
    for u in withheld:
        mask[u] = True
    return mask


def visible_edges(edges, rels, withheld_mask):
    """Edges with NEITHER endpoint withheld (leakage-safe for both T and encoder)."""
    keep = ~(withheld_mask[edges[:, 0]] | withheld_mask[edges[:, 1]])
    return edges[keep], np.asarray(rels)[keep]


# ---------------------------------------------------------------------------
# Reachability-column construction. All arms feed run_sr_arm the SAME shape [C, n+1] normalized reachability sr_p;
# only the underlying M columns differ. We replicate sr_boost_by_chain's normalization exactly.
# ---------------------------------------------------------------------------

def _norm_columns_to_sr_p(Xcols, goals, n_nodes, device):
    """Xcols [n, U] (>=0 or estimated); goals [C]; returns sr_p [C, n+1] normalized to [0,1] per goal-column + pad."""
    goals = np.asarray(goals, dtype=np.int64)
    uniq, inv = np.unique(goals, return_inverse=True)
    colmax = Xcols.max(dim=0).values.clamp(min=1e-12)
    Xn = (Xcols / colmax[None, :]).clamp(min=0.0)
    inv_t = torch.from_numpy(inv.astype(np.int64)).to(device)
    sr_by_chain = Xn.index_select(dim=1, index=inv_t).t().contiguous()   # [C, n]
    C = sr_by_chain.shape[0]
    pad = torch.zeros(C, 1, device=device, dtype=sr_by_chain.dtype)
    return torch.cat([sr_by_chain, pad], dim=1), uniq, colmax


def code_smoothing_matrix(Zn, withheld_idx, visible_idx, k, temp, device):
    """S [|W|, n] with S[w, u] = softmax cosine weight of withheld node w onto its top-k VISIBLE code-neighbors u
    (zeros elsewhere). Zn must be L2-normalized codes [n, d]."""
    W = withheld_idx.shape[0]
    n = Zn.shape[0]
    if W == 0 or visible_idx.shape[0] == 0:
        return torch.zeros(W, n, device=device, dtype=Zn.dtype)
    Zw = Zn[withheld_idx]                       # [W, d]
    Zv = Zn[visible_idx]                         # [V, d]
    sims = Zw @ Zv.t()                           # [W, V] cosine (unit-norm)
    kk = min(k, visible_idx.shape[0])
    topv, topi = torch.topk(sims, kk, dim=1)     # [W, kk]
    wts = torch.softmax(topv / max(temp, 1e-6), dim=1)   # [W, kk]
    S = torch.zeros(W, n, device=device, dtype=Zn.dtype)
    cols = visible_idx[topi]                      # [W, kk] global node ids
    S.scatter_(1, cols, wts)
    return S


def build_visible_and_smoothed_columns(sr_solver_vis, goals_uniq, gamma, withheld_mask, Zn_vis, Zn_alias,
                                        k, temp, n_nodes, device):
    """Returns dict of Xcols [n, U] for the three held-out conditions on the VISIBLE-T resolvent:
       memctrl  = visible-T columns unmodified (withheld rows ~0 -> hole in the map)
       learned  = withheld rows replaced by code-smoothed estimate using VISIBLE-trained codes
       codealias= withheld rows replaced by code-smoothed estimate using RANDOM (aliased) codes
    """
    Xvis = sr_solver_vis.columns(goals_uniq, gamma)              # [n, U] >= 0 (visible T)
    withheld_idx = torch.from_numpy(np.where(withheld_mask)[0].astype(np.int64)).to(device)
    visible_idx = torch.from_numpy(np.where(~withheld_mask)[0].astype(np.int64)).to(device)

    memctrl = Xvis
    # learned smoothing
    S = code_smoothing_matrix(Zn_vis, withheld_idx, visible_idx, k, temp, device)    # [W, n]
    Xlearned = Xvis.clone()
    if withheld_idx.shape[0] > 0:
        Xlearned[withheld_idx] = S @ Xvis                       # [W, n] x [n, U] -> [W, U]
    # codealias smoothing (random codes)
    Sa = code_smoothing_matrix(Zn_alias, withheld_idx, visible_idx, k, temp, device)
    Xalias = Xvis.clone()
    if withheld_idx.shape[0] > 0:
        Xalias[withheld_idx] = Sa @ Xvis
    return dict(memctrl=memctrl, learned=Xlearned, codealias=Xalias, Xvis=Xvis)


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------

def _reach_on_subset(reach_dict):
    return {d: reach_dict[d] for d in range(1, MAX_REACH + 1)}


def run_seed(seed, node_words, edges, rels, dir_adj, roles_t, nbr_idx, nbr_rel, nbr_mask,
             cfg, device, out_dir=None):
    n_nodes = len(node_words)
    chunk = cfg["chain_chunk"]
    d = cfg["code_dim"]

    # FULL codes (all edges) -> KNOWN_T_FULL + anchors
    X = char_trigram_features(node_words, cfg["feat_dim"])
    Z_full = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_full")
    Zp_full = torch.cat([Z_full, torch.zeros(1, d, device=device)], dim=0)
    Zn_full = torch.nn.functional.normalize(Z_full, dim=1)

    # general chains (identical rng offset/sampler as certified cell -> paired anchor reproduction)
    gen_rng = np.random.default_rng(seed + 909)
    g_start, g_targets, g_role = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, gen_rng)
    goals = g_targets[MAX_REACH - 1]

    # ---- held-out split: withhold a contiguous BFS-ball (disjoint subgraph). The invariant is PER-CHAIN, not
    # global: a held-out chain's OWN goal must stay visible (else its resolvent column is degenerate). With ~n_chains
    # goals spread over n_nodes, a global goal-forbid would starve the ball; instead we withhold freely and select
    # held-out chains as {hop-1 target withheld AND goal visible} below. ----
    adj_u = build_undirected_adj_simple(dir_adj, n_nodes)
    split_rng = np.random.default_rng(seed + 4242)
    withheld_mask = pick_withheld_ball(adj_u, n_nodes, WITHHELD_FRAC, set(), split_rng)
    n_withheld = int(withheld_mask.sum())

    # held-out chains: hop-1 correct successor is a withheld node (first routing decision needs a smoothed estimate)
    hop1_tgt = g_targets[0]
    heldout_chain_mask = withheld_mask[hop1_tgt] & (~withheld_mask[goals])   # goal visible, hop1 withheld
    ho_idx = np.where(heldout_chain_mask)[0]
    n_heldout = int(ho_idx.shape[0])

    # visible graph (leakage-safe) -> visible T + visible-trained codes
    e_vis, r_vis = visible_edges(edges, rels, withheld_mask)
    dir_adj_vis = build_typed_diradj(e_vis, r_vis, n_nodes)
    T_vis = build_transition_dense(dir_adj_vis, n_nodes, device)
    sr_solver_vis = SRSolver(T_vis, device)
    Z_vis = train_binding_encoder_dev(X, e_vis, r_vis, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_vis")
    Zp_vis = torch.cat([Z_vis, torch.zeros(1, d, device=device)], dim=0)
    Zn_vis = torch.nn.functional.normalize(Z_vis, dim=1)
    # aliased random codes for reciprocal-necessity
    alias_gen = torch.Generator(device="cpu").manual_seed(seed + 31337)
    Zn_alias = torch.nn.functional.normalize(
        torch.randn(n_nodes, d, generator=alias_gen).to(device), dim=1)

    # full-T solver + columns
    T_full = build_transition_dense(dir_adj, n_nodes, device)
    sr_solver_full = SRSolver(T_full, device)
    uniq_goals = np.unique(np.asarray(goals, dtype=np.int64))
    Xfull = sr_solver_full.columns(uniq_goals, SR_GAMMA_PRIMARY)
    sr_p_knownT, _uq2, _cm2 = _norm_columns_to_sr_p(Xfull, goals, n_nodes, device)

    # held-out condition columns on visible-T
    cols = build_visible_and_smoothed_columns(sr_solver_vis, uniq_goals, SR_GAMMA_PRIMARY, withheld_mask,
                                              Zn_vis, Zn_alias, SMOOTH_K, SMOOTH_TEMP, n_nodes, device)
    sr_p_learned, _, _ = _norm_columns_to_sr_p(cols["learned"], goals, n_nodes, device)
    sr_p_memctrl, _, _ = _norm_columns_to_sr_p(cols["memctrl"], goals, n_nodes, device)
    sr_p_codealias, _, _ = _norm_columns_to_sr_p(cols["codealias"], goals, n_nodes, device)

    arms = {}
    sigs = {}

    # ---- anchors on the GENERAL population (Gate-D + anti-sat) ----
    r, h, _sa, sig = ft_run_no_cleanup(Z_full, roles_t, g_start, g_targets, g_role, device, n_nodes)
    arms[NO_CLEANUP] = dict(reach=r); sigs[NO_CLEANUP] = sig
    r, h, _sa, sig = ft_run_chain_arm(FT_MEMORYLESS, Z_full, Zp_full, roles_t, nbr_idx, nbr_rel, nbr_mask,
                                      None, g_start, g_targets, g_role, device, chunk, n_nodes)
    arms[MEMORYLESS] = dict(reach=r); sigs[MEMORYLESS] = sig
    r, h, _sa, sig = ft_run_chain_arm(FT_GOAL_WAYPOINT, Z_full, Zp_full, roles_t, nbr_idx, nbr_rel, nbr_mask,
                                      None, g_start, g_targets, g_role, device, chunk, n_nodes)
    arms[SUPPLIED_WAYPOINT] = dict(reach=r); sigs[SUPPLIED_WAYPOINT] = sig
    r, h, sig = run_sr_arm(Z_full, Zp_full, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                           device, chunk, n_nodes, sr_p_knownT, SR_BOOST)
    arms[KNOWN_T_FULL] = dict(reach=r); sigs[KNOWN_T_FULL] = sig

    # ---- held-out discriminator: evaluate reachability arms ON THE HELD-OUT CHAIN SUBSET ----
    heldout = {}
    if n_heldout >= 1:
        gs = g_start[ho_idx]
        gt = [g_targets[hh][ho_idx] for hh in range(MAX_REACH)]
        gr = [g_role[hh][ho_idx] for hh in range(MAX_REACH)]
        srp_ho_learned = sr_p_learned[ho_idx]
        srp_ho_memctrl = sr_p_memctrl[ho_idx]
        srp_ho_codealias = sr_p_codealias[ho_idx]
        srp_ho_knownT = sr_p_knownT[ho_idx]

        # LEARNED_HELDOUT + controls use VISIBLE codes for the base memoryless score (paired); KNOWN_T uses full codes.
        r, h, sig = run_sr_arm(Z_vis, Zp_vis, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                               device, chunk, n_nodes, srp_ho_learned, SR_BOOST)
        arms[LEARNED_HELDOUT] = dict(reach=r); sigs[LEARNED_HELDOUT] = sig
        r, h, sig = run_sr_arm(Z_vis, Zp_vis, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                               device, chunk, n_nodes, srp_ho_memctrl, SR_BOOST)
        arms[HELDOUT_MEMCTRL] = dict(reach=r); sigs[HELDOUT_MEMCTRL] = sig
        r, h, sig = run_sr_arm(Z_vis, Zp_vis, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                               device, chunk, n_nodes, srp_ho_codealias, SR_BOOST)
        arms[HELDOUT_CODEALIAS] = dict(reach=r); sigs[HELDOUT_CODEALIAS] = sig
        # memoryless + known-T restricted to the held-out subset (floor + within-subset full-map ceiling)
        r_mho, _h, _sa, _s = ft_run_chain_arm(FT_MEMORYLESS, Z_vis, Zp_vis, roles_t, nbr_idx, nbr_rel, nbr_mask,
                                              None, gs, gt, gr, device, chunk, n_nodes)
        r_kho, _h2, _s2 = run_sr_arm(Z_full, Zp_full, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                                     device, chunk, n_nodes, srp_ho_knownT, SR_BOOST)
        heldout = dict(memoryless=_reach_on_subset(r_mho), known_t_full=_reach_on_subset(r_kho))
    else:
        for a in (LEARNED_HELDOUT, HELDOUT_MEMCTRL, HELDOUT_CODEALIAS):
            arms[a] = dict(reach={dd: float("nan") for dd in range(1, MAX_REACH + 1)})
            sigs[a] = "nan_%s" % a

    for arm in ALL_ARMS:
        _log("  seed=%d %-18s reach=%s" % (
            seed, arm, {dd: round(arms[arm]["reach"][dd], 3) for dd in range(1, MAX_REACH + 1)}))
    _log("  seed=%d n_withheld=%d (%.1f%%) n_heldout_chains=%d/%d" % (
        seed, n_withheld, 100.0 * n_withheld / max(n_nodes, 1), n_heldout, int(g_start.shape[0])))

    return dict(seed=seed, arms={a: dict(reach=arms[a]["reach"]) for a in ALL_ARMS}, arm_sigs=sigs,
                heldout_refs=heldout, n_withheld=n_withheld, withheld_frac_actual=n_withheld / max(n_nodes, 1),
                n_heldout_chains=n_heldout, n_general=int(g_start.shape[0]), code_dim=d)


# ---------------------------------------------------------------------------
# Aggregate + CG verdict
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, meta, cfg):
    def R(arm, dd):
        return _nm([m["arms"][arm]["reach"][dd] for m in per_seed])

    def HR(key, dd):
        return _nm([m["heldout_refs"][key][dd] for m in per_seed if key in m.get("heldout_refs", {})])

    base1 = R(NO_CLEANUP, 1); base2 = R(NO_CLEANUP, 2)
    mem1 = R(MEMORYLESS, 1); mem2 = R(MEMORYLESS, 2)
    sup1 = R(SUPPLIED_WAYPOINT, 1); sup2 = R(SUPPLIED_WAYPOINT, 2)
    knownT1 = R(KNOWN_T_FULL, 1); knownT2 = R(KNOWN_T_FULL, 2)
    learned2 = R(LEARNED_HELDOUT, 2); learned1 = R(LEARNED_HELDOUT, 1)
    memctrl2 = R(HELDOUT_MEMCTRL, 2)
    codealias2 = R(HELDOUT_CODEALIAS, 2)
    ho_mem2 = HR("memoryless", 2)
    ho_knownT2 = HR("known_t_full", 2)
    n_heldout = int(_nm([m["n_heldout_chains"] for m in per_seed]))

    # CG headline metrics (primary = LEARNED_HELDOUT reach@2 on held-out chains)
    ratio_vs_knownT_ho = (learned2 / ho_knownT2) if (ho_knownT2 == ho_knownT2 and ho_knownT2 > 1e-9) else float("nan")
    delta_vs_memctrl = (learned2 - memctrl2) if (learned2 == learned2 and memctrl2 == memctrl2) else float("nan")
    delta_vs_codealias = (learned2 - codealias2) if (learned2 == learned2 and codealias2 == codealias2) else float("nan")
    delta_vs_ho_mem = (learned2 - ho_mem2) if (learned2 == learned2 and ho_mem2 == ho_mem2) else float("nan")

    # anti-sat + baseline-in-band + MM discriminator
    hop1_present = bool(mem1 == mem1 and mem1 >= HOP1_PRESENT)
    baseline_in_band = bool(mem1 == mem1 and 0.05 < mem1 < BASE_IN_BAND_HI)
    baseline_collapses = bool(base2 == base2 and base1 == base1
                              and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))
    supplied_fires = bool(sup2 == sup2 and mem2 == mem2 and sup2 >= mem2 + SUPPLIED_FIRES_MIN)
    enough_heldout = bool(n_heldout >= MIN_HELDOUT_CHAINS)

    # CG gates (on LEARNED_HELDOUT reach@2)
    codes_necessary = bool(learned2 == learned2 and codealias2 == codealias2
                           and learned2 >= codealias2 + NEC_MARGIN)
    smoothing_necessary = bool(learned2 == learned2 and memctrl2 == memctrl2
                               and learned2 >= memctrl2 + NEC_MARGIN)
    cg_hard_pass = bool(learned2 == learned2 and learned2 >= CG_HARD_PASS
                        and codes_necessary and smoothing_necessary)
    codes_do_nothing = bool(learned2 == learned2 and codealias2 == codealias2
                            and abs(learned2 - codealias2) < NEC_MARGIN)
    cg_hard_fail = bool(learned2 == learned2 and (learned2 <= CG_HARD_FAIL or codes_do_nothing
                        or (memctrl2 == memctrl2 and learned2 <= memctrl2)))

    # Gate-D reproduction (FULL only)
    is_full = bool(len(cfg["seeds"]) == 3 and cfg["n_nodes"] == 5000 and cfg["code_dim"] == 2048)
    repro_mem1_ok = bool(mem1 == mem1 and abs(mem1 - REPRO_MEM1) <= REPRO_TOL)
    repro_sup1_ok = bool(sup1 == sup1 and abs(sup1 - REPRO_SUP1) <= REPRO_TOL)
    repro_sup2_ok = bool(sup2 == sup2 and abs(sup2 - REPRO_SUP2) <= REPRO_TOL)
    repro_knownt2_ok = bool(knownT2 == knownT2 and abs(knownT2 - REPRO_KNOWNT2) <= REPRO_TOL)
    repro_ok = bool(repro_mem1_ok and repro_sup1_ok and repro_sup2_ok and repro_knownt2_ok)

    if not hop1_present:
        verdict = "INCONCLUSIVE_HOP1_ABSENT"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif not supplied_fires:
        verdict = "INCONCLUSIVE_SUPPLIED_MM_DID_NOT_FIRE"
    elif not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT_CHAINS"
    elif is_full and not repro_ok:
        verdict = "INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT"
    elif cg_hard_pass:
        verdict = "HARD_PASS_CG_LEARNED_SR_REASONING"
    elif cg_hard_fail:
        verdict = "HARD_FAIL_CG_MEMORIZED_SEARCH"
    else:
        verdict = "MIDDLE_BAND_CG_PARTIAL_GENERALIZATION"

    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f @2=%.3f(collapses=%s) || MEMORYLESS @1=%.3f(in_band=%s) @2=%.3f || "
        "SUPPLIED @1=%.3f @2=%.3f(fires=%s) || KNOWN_T_FULL @1=%.3f @2=%.3f(SEARCH-baseline) || "
        "HELD-OUT[n=%d]: LEARNED @1=%.3f @2=%.3f | MEMCTRL @2=%.3f | CODEALIAS @2=%.3f | ho_mem @2=%.3f | "
        "ho_knownT @2=%.3f || CG: ratio(learned/ho_knownT)=%s d(learned-memctrl)=%s d(learned-codealias)=%s "
        "d(learned-ho_mem)=%s codes_necessary=%s smoothing_necessary=%s || "
        "HARD_PASS(learned2>=%.2f AND beats both ctrls)=%s HARD_FAIL(learned2<=%.2f OR codes_do_nothing OR "
        "learned<=memctrl)=%s || repro(full=%s): mem1=%s sup1=%s sup2=%s knownT2=%s || withheld=%.1f%% nodes=%d "
        "E=%d seeds=%d run=%s" % (
            verdict, base1, base2, baseline_collapses, mem1, baseline_in_band, mem2,
            sup1, sup2, supplied_fires, knownT1, knownT2, n_heldout, learned1, learned2, memctrl2, codealias2,
            ho_mem2, ho_knownT2, _fmt(ratio_vs_knownT_ho), _fmt(delta_vs_memctrl), _fmt(delta_vs_codealias),
            _fmt(delta_vs_ho_mem), codes_necessary, smoothing_necessary,
            CG_HARD_PASS, cg_hard_pass, CG_HARD_FAIL, cg_hard_fail, is_full,
            repro_mem1_ok, repro_sup1_ok, repro_sup2_ok, repro_knownt2_ok,
            100.0 * _nm([m["withheld_frac_actual"] for m in per_seed]), meta["n_nodes"], meta["n_edges"],
            len(per_seed), "full" if is_full else "smoke"))

    gates = dict(
        verdict=verdict,
        reach={a: {dd: R(a, dd) for dd in range(1, MAX_REACH + 1)} for a in ALL_ARMS},
        cg=dict(learned_heldout_reach1=learned1, learned_heldout_reach2=learned2,
                memctrl_reach2=memctrl2, codealias_reach2=codealias2,
                heldout_memoryless_reach2=ho_mem2, heldout_known_t_full_reach2=ho_knownT2,
                known_t_full_reach2_general=knownT2,
                ratio_vs_knownT_heldout=ratio_vs_knownT_ho, delta_vs_memctrl=delta_vs_memctrl,
                delta_vs_codealias=delta_vs_codealias, delta_vs_heldout_mem=delta_vs_ho_mem,
                codes_necessary=codes_necessary, smoothing_necessary=smoothing_necessary,
                cg_hard_pass=cg_hard_pass, cg_hard_fail=cg_hard_fail, n_heldout_chains=n_heldout),
        anti_sat=dict(hop1_present=hop1_present, baseline_in_band=baseline_in_band,
                      baseline_collapses=baseline_collapses, supplied_fires=supplied_fires,
                      enough_heldout=enough_heldout),
        positive_control=dict(is_full=is_full, repro_mem1=mem1, repro_sup1=sup1, repro_sup2=sup2,
                              repro_knownt2=knownT2, repro_mem1_ok=repro_mem1_ok, repro_sup1_ok=repro_sup1_ok,
                              repro_sup2_ok=repro_sup2_ok, repro_knownt2_ok=repro_knownt2_ok, repro_ok=repro_ok,
                              anchors=dict(mem1=REPRO_MEM1, sup1=REPRO_SUP1, sup2=REPRO_SUP2,
                                           knownT2=REPRO_KNOWNT2, tol=REPRO_TOL)),
        bands=dict(CG_HARD_PASS=CG_HARD_PASS, CG_HARD_FAIL=CG_HARD_FAIL, NEC_MARGIN=NEC_MARGIN,
                   WITHHELD_FRAC=WITHHELD_FRAC, SMOOTH_K=SMOOTH_K, SMOOTH_TEMP=SMOOTH_TEMP,
                   SR_GAMMA_PRIMARY=SR_GAMMA_PRIMARY, SR_BOOST=SR_BOOST, MIN_HELDOUT_CHAINS=MIN_HELDOUT_CHAINS),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test. Planted graph with a WITHHELD region whose reachability IS recoverable from
# code-near VISIBLE nodes: LEARNED (code-smoothed) recovers held-out routing >> MEMCTRL (hole); CODEALIAS (random
# codes) collapses toward MEMCTRL (codes are necessary). Also NO_CLEANUP collapses; arms differ.
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    device = torch.device("cpu")
    torch.manual_seed(0); np.random.seed(0)
    rng = np.random.default_rng(0)
    d = 96
    Tr = 4
    roles_t = torch.from_numpy(make_unitary_roles(Tr, d, np.random.default_rng(11))).to(device)

    # Planted BRANCH chains with a WITHHELD hop-1 decision. At the start S, KSR same-relation siblings compete; ONE
    # is the true successor T1 (WITHHELD), the KSR-1 off-siblings are dead-ends (WITHHELD). Every candidate code is
    # ~ORTHOGONAL to the memoryless bind(r0, code_S) direction (random codes anchored elsewhere), so the memoryless
    # BASE score cannot separate them (aliased ~1/KSR) -- routing MUST come from the reachability term. The onward
    # path T1 -> tail0 -> tail1 -> G is VISIBLE (only hop-1 nodes withheld); the true T1's CODE is planted NEAR its
    # visible onward neighbor tail0 (which genuinely reaches G in visible T), while each off-sibling's CODE is planted
    # near a distinct VISIBLE dead-end (M_visible ~ 0). => code-smoothing recovers M_hat[T1,G] high, off ~0 (LEARNED
    # picks T1); MEMCTRL (no smoothing, withheld M=0) ties ~1/KSR; CODEALIAS (random codes) smooths noise ~1/KSR.
    KSR = 4
    n_cap = 6000
    Zc = torch.zeros(n_cap, d, device=device)
    dir_adj = [[] for _ in range(n_cap)]
    next_id = 0
    withheld = np.zeros(n_cap, dtype=bool)

    def _new(code, hide=False):
        nonlocal next_id
        Zc[next_id] = _l2t(code[None, :])[0]
        nid = next_id
        withheld[nid] = hide
        next_id += 1
        return nid

    br_start, br_tgt, br_rid = [], [[] for _ in range(MAX_REACH)], [[] for _ in range(MAX_REACH)]
    n_chains_plant = 140
    for c in range(n_chains_plant):
        if next_id >= n_cap - (MAX_REACH * KSR + KSR * 2 + 12):
            break
        S = _new(_l2t(torch.randn(1, d))[0])          # start (visible)
        r0 = int(rng.integers(0, Tr))
        # VISIBLE onward tail tail0 -> tail1 -> ... -> G (all visible; G = tail[MAX_REACH-2])
        tail = []
        prev = None
        for hh in range(MAX_REACH - 1):
            tv = _new(_l2t(torch.randn(1, d))[0])     # visible tail node
            tail.append(tv)
            if prev is not None:
                rr = int(rng.integers(0, Tr))
                dir_adj[prev].append((tv, rr)); dir_adj[tv].append((prev, rr))
            prev = tv
        # true hop-1 successor T1 (WITHHELD): code planted near tail0 (its visible onward neighbor) but kept
        # ~orthogonal to bind(r0, code_S) so the memoryless base cannot favor it.
        true_code = _l2t(Zc[tail[0]:tail[0] + 1])[0] + 0.15 * _l2t(torch.randn(1, d))[0]
        T1 = _new(true_code, hide=True)
        dir_adj[S].append((T1, r0)); dir_adj[T1].append((S, r0))
        dir_adj[T1].append((tail[0], r0)); dir_adj[tail[0]].append((T1, r0))   # withheld edge (T1 hidden)
        # off-siblings (WITHHELD dead-ends): each code near a distinct VISIBLE dead-end node
        for _k in range(KSR - 1):
            dead = _new(_l2t(torch.randn(1, d))[0])   # visible dead-end (no path to G)
            off_code = _l2t(Zc[dead:dead + 1])[0] + 0.15 * _l2t(torch.randn(1, d))[0]
            off = _new(off_code, hide=True)
            dir_adj[S].append((off, r0)); dir_adj[off].append((S, r0))
            dir_adj[off].append((dead, r0)); dir_adj[dead].append((off, r0))
        # targets: hop1 = T1, hop2.. = tail0, tail1, ... (goal = tail[MAX_REACH-2])
        br_tgt[0].append(T1); br_rid[0].append(r0)
        for hh in range(1, MAX_REACH):
            br_tgt[hh].append(tail[hh - 1]); br_rid[hh].append(int(rng.integers(0, Tr)))
        br_start.append(S)
    g_start = np.asarray(br_start, dtype=np.int64)
    g_tgt = [np.asarray(t, dtype=np.int64) for t in br_tgt]
    g_role = [np.asarray(r, dtype=np.int64) for r in br_rid]

    n = next_id
    Zc = Zc[:n]; dir_adj = dir_adj[:n]; withheld = withheld[:n]
    Z = _l2t(Zc)
    Zp = torch.cat([Z, torch.zeros(1, d, device=device)], dim=0)
    Zn = torch.nn.functional.normalize(Z, dim=1)
    Zn_alias = torch.nn.functional.normalize(torch.randn(n, d, generator=torch.Generator().manual_seed(7)), dim=1)
    nbr_idx, nbr_rel, nbr_mask, Dmax, _mod = build_nbr_table(dir_adj, n, device)

    goals = g_tgt[MAX_REACH - 1]
    uniq_goals = np.unique(np.asarray(goals, dtype=np.int64))

    # full-T known
    T_full = build_transition_dense(dir_adj, n, device)
    Xfull = SRSolver(T_full, device).columns(uniq_goals, SR_GAMMA_PRIMARY)
    sr_p_known, _, _ = _norm_columns_to_sr_p(Xfull, goals, n, device)

    # visible graph (edges touching withheld removed)
    e_list = []
    r_list = []
    for u in range(n):
        for (v, rr) in dir_adj[u]:
            if u < v:
                e_list.append((u, v)); r_list.append(rr)
    e_all = np.asarray(e_list, dtype=np.int64)
    r_all = np.asarray(r_list, dtype=np.int64)
    keep = ~(withheld[e_all[:, 0]] | withheld[e_all[:, 1]])
    dir_adj_vis = build_typed_diradj(e_all[keep], r_all[keep], n)
    T_vis = build_transition_dense(dir_adj_vis, n, device)
    cols = build_visible_and_smoothed_columns(SRSolver(T_vis, device), uniq_goals, SR_GAMMA_PRIMARY, withheld,
                                              Zn, Zn_alias, SMOOTH_K, SMOOTH_TEMP, n, device)
    sr_p_learned, _, _ = _norm_columns_to_sr_p(cols["learned"], goals, n, device)
    sr_p_memctrl, _, _ = _norm_columns_to_sr_p(cols["memctrl"], goals, n, device)
    sr_p_alias, _, _ = _norm_columns_to_sr_p(cols["codealias"], goals, n, device)

    # held-out chains: hop-1 target withheld
    hop1 = g_tgt[0]
    ho = np.where(withheld[hop1] & (~withheld[goals]))[0]
    gs = g_start[ho]
    gt = [g_tgt[hh][ho] for hh in range(MAX_REACH)]
    gr = [g_role[hh][ho] for hh in range(MAX_REACH)]

    r_no, _h, _sa, s_no = ft_run_no_cleanup(Z, roles_t, g_start, g_tgt, g_role, device, n)
    r_learned, _h, s_learned = run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                                          device, 256, n, sr_p_learned[ho], SR_BOOST)
    r_memctrl, _h, s_memctrl = run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                                          device, 256, n, sr_p_memctrl[ho], SR_BOOST)
    r_alias, _h, s_alias = run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                                      device, 256, n, sr_p_alias[ho], SR_BOOST)
    r_known, _h, s_known = run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                                      device, 256, n, sr_p_known[ho], SR_BOOST)

    nocleanup_ran = bool(r_no[1] == r_no[1])
    n_ho = int(ho.shape[0])
    known_recovers = bool(r_known[1] == r_known[1] and r_known[1] >= 0.55)         # full map routes held-out chains
    learned_recovers = bool(r_learned[1] == r_learned[1] and r_learned[1] >= 0.45) # code-smoothing recovers hop-1
    learned_beats_memctrl = bool(r_learned[1] == r_learned[1] and r_memctrl[1] == r_memctrl[1]
                                 and r_learned[1] >= r_memctrl[1] + 0.15)          # smoothing necessary
    codes_necessary = bool(r_learned[1] == r_learned[1] and r_alias[1] == r_alias[1]
                           and r_learned[1] >= r_alias[1] + 0.15)                  # random codes collapse
    arms_differ = bool(len({s_learned, s_memctrl, s_alias, s_known, s_no}) >= 4)

    res = dict(n_synth=int(n), n_heldout=n_ho, n_withheld=int(withheld.sum()),
               reach_no_cleanup={dd: round(r_no[dd], 4) for dd in range(1, MAX_REACH + 1)},
               reach_known_full={dd: round(r_known[dd], 4) for dd in range(1, MAX_REACH + 1)},
               reach_learned={dd: round(r_learned[dd], 4) for dd in range(1, MAX_REACH + 1)},
               reach_memctrl={dd: round(r_memctrl[dd], 4) for dd in range(1, MAX_REACH + 1)},
               reach_codealias={dd: round(r_alias[dd], 4) for dd in range(1, MAX_REACH + 1)},
               nocleanup_ran=nocleanup_ran, known_recovers=known_recovers, learned_recovers=learned_recovers,
               learned_beats_memctrl=learned_beats_memctrl, codes_necessary=codes_necessary,
               arms_differ=arms_differ, Dmax=int(Dmax))
    ok = bool(nocleanup_ran and known_recovers and learned_recovers and learned_beats_memctrl
              and codes_necessary and arms_differ and n_ho >= 10)
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
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)

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
            verdict="HARD_FAIL", run_mode=run_mode, verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d" % ({k: meta[k] for k in ("n_nodes", "n_edges", "median_degree")}, T))
    n_nodes = len(node_ids)
    edges = np.asarray(edges, dtype=np.int64)
    dir_adj = build_typed_diradj(edges, rels, n_nodes)
    nbr_idx, nbr_rel, nbr_mask, Dmax, mean_out_deg = build_nbr_table(dir_adj, n_nodes, device)
    _log("nbr table: Dmax=%d mean_out_deg=%.3f" % (Dmax, mean_out_deg))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS learned-SR held-out machinery: NO_CLEANUP collapses; KNOWN_T_FULL routes "
                        "held-out chains; LEARNED (code-smoothed visible-T) recovers held-out hop-1 >> MEMCTRL "
                        "(hole-in-map); CODEALIAS (random codes) collapses toward MEMCTRL (codes necessary); arms "
                        "differ; subgraph + nbr table + visible/full resolvent + code-smoothing exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res, subgraph_meta=meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, node_words, edges, rels, dir_adj, roles_t, nbr_idx, nbr_rel, nbr_mask,
                          cfg, device, out_dir=out_dir_path)
            for a in ALL_ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1)
                           if a not in pm["arms"] or dd not in pm["arms"][a]["reach"]]
                if missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            # arms must differ (META_RULE_AF): the held-out reachability arms must not be bit-identical
            if pm["n_heldout_chains"] >= 1:
                if pm["arm_sigs"][LEARNED_HELDOUT] == pm["arm_sigs"][HELDOUT_MEMCTRL]:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d LEARNED==MEMCTRL" % seed)
                if pm["arm_sigs"][LEARNED_HELDOUT] == pm["arm_sigs"][HELDOUT_CODEALIAS]:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d LEARNED==CODEALIAS" % seed)
            if pm["arm_sigs"][KNOWN_T_FULL] == pm["arm_sigs"][MEMORYLESS]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d KNOWN_T==MEMORYLESS" % seed)
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, meta, cfg)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=cfg["seeds"], config=cfg, subgraph_meta=meta, gates=gates,
                   mechanism_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed)
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
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
