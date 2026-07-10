"""PAYOFF cell: does the substrate's ACTUAL held-out reasoning reach RISE on DENSER knowledge -- and is the rise a
RELATIONAL gain (the substrate's own learned codes) rather than a pure DEGREE/popularity artifact? This is the direct
payoff test of the session's resolved conclusion (5-hypothesis elimination): the reasoning wall is KNOWLEDGE-THINNESS,
not machinery. Test #4 (graph_inductive_ceiling_v1, HARD_FAIL_KNOWLEDGE_IS_THE_LIMIT) showed the graph's inductive
CEILING (best held-out link-prediction AUC) RISES +0.078 with density (5-core, mean-deg 5.6->8.7,
MEASURED@data/exp_graph_inductive_ceiling_v1_smoke/metrics.json:gates.density_delta_relational_GATE). That is a
CEILING. This cell tests whether the substrate's OWN learned-SR HELD-OUT routing reach FOLLOWS the ceiling up.

MECHANISM (reuse the certified learned-SR held-out harness VERBATIM; add a density ladder + a degree-only confound
control). We reuse the held-out-subgraph construction + code-space-smoothing arms from
exp_grounding_learned_sr_heldout_reasoning_v1 (LEARNED_HELDOUT / HELDOUT_MEMCTRL / HELDOUT_CODEALIAS + KNOWN_T_FULL +
MEMORYLESS + SUPPLIED anchors) VERBATIM, and run the whole thing on graphs of INCREASING DENSITY:
  SPARSE = the full ConceptNet typed subgraph (mean-deg ~5.6-6.6).
  DENSE  = the k-core (largest k with >= MIN_CORE_NODES nodes) = a high-degree-induced subgraph (mean-deg ~9-12).
A disjoint contiguous BFS-ball of non-goal nodes is WITHHELD from BOTH the transition matrix AND the encoder at each
density level; held-out chains are those whose hop-1 correct successor is a withheld node (the first routing decision
requires estimating a withheld candidate's reachability). LEARNED re-estimates withheld reachability by code-space
smoothing over the VISIBLE-trained codes; CODEALIAS uses random codes; MEMCTRL leaves the hole. Identical seeds /
chains / graph / withheld split per density level; only the density (which subgraph) and the reachability signal differ.

CRITICAL CONFOUND CONTROL (the #4 agent flagged it: a denser subgraph of high-degree hubs can look 'easier' via pure
DEGREE/popularity = preferential-attachment, NOT via richer RELATIONAL structure). So we add a DEGREE_ONLY arm: an
identical routing arm whose reachability column is the FULL-graph node DEGREE (popularity), not the SR resolvent or
the learned codes. Within run_sr_arm's within-candidate normalization this is exactly PA-routing (route toward the
highest-degree local neighbor). The number that COUNTS is the RELATIONAL GAIN = LEARNED_HELDOUT reach - DEGREE_ONLY
reach at each density level; the density payoff that counts = whether the RELATIONAL GAIN RISES with density (dense
minus sparse), NOT whether raw reach rises (raw reach can rise on pure popularity). We ALSO track the codes-beat-random
margin = LEARNED - CODEALIAS and whether IT rises with density (the substrate's own codes benefiting, degree-blind).

DISCRIMINATOR (pre-registered; primary = LEARNED_HELDOUT reach@2 on held-out chains, per density level).
  HARD_PASS_RICHER_KNOWLEDGE_ENABLES_REASONING = the RELATIONAL gain on the dense graph materially exceeds sparse:
     rel_gain_rise (= rel_gain_dense - rel_gain_sparse) >= REL_GAIN_RISE_HP (0.10)
     OR the codes-beat-random margin crosses up: codes_margin_rise >= CODES_MARGIN_RISE_HP (0.05) with
        codes_margin_sparse <= CODES_MARGIN_NEAR_ZERO (0.05, i.e. sparse was ~0)
     -> richer knowledge measurably enables the substrate to reason inductively (RELATIONAL, degree-independent).
  HARD_FAIL_DENSITY_ALONE_NOT_THE_ENABLER = dense relational reach ~= sparse: rel_gain_rise <= REL_GAIN_RISE_FLAT
     (0.03) AND codes_margin_rise <= CODES_MARGIN_RISE_FLAT (0.02) -> density does NOT help the substrate reason
     relationally (either it does not help at all, OR the raw gain is a pure-degree artifact captured by DEGREE_ONLY).
     The knowledge-density-alone story is not the enabler; the wall is deeper.
  MIDDLE_BAND_PARTIAL_DENSITY_PAYOFF = otherwise (0.03 < rel_gain_rise < 0.10 and no codes-margin crossing) -> density
     helps the relational gain partially but not to the material bar.
Reported (never gated): per-density LEARNED/DEGREE/MEMCTRL/CODEALIAS/MEMORYLESS/KNOWN_T reach@1/@2, raw reach_rise,
degree_rise (how much is pure popularity), rel_gain per level, codes_margin per level, mean-degree + k-core per level,
held-out chain counts.

SELF-TEST (mechanism; proves the RELATIONAL gain is DEGREE-INDEPENDENT and the discriminator separates relational from
pure-degree density). One planted graph carrying TWO held-out chain families, all hop-1 successors withheld:
  REL family: the true withheld successor's CODE is planted near a VISIBLE onward node that genuinely reaches the goal
    (code-smoothing recoverable); ALL same-relation siblings have IDENTICAL degree (so DEGREE cannot separate them).
    => LEARNED recovers hop-1 (routes to the true successor); DEGREE ties ~1/KSR. rel_gain HIGH (degree-independent).
  DEG family: the true withheld successor is a HUB (high full-graph degree) with a RANDOM code (no recoverable
    relational signal); off-siblings are low-degree dead-ends. => DEGREE recovers hop-1 (routes to the hub); LEARNED
    (code-smoothing on a random code) ties ~1/KSR. rel_gain ~0 (the 'win' here is pure degree; our metric shows it).
  Gate: rel_gain(REL) >= 0.20 AND rel_gain(DEG) <= 0.05 AND gap(REL - DEG) >= 0.15. If the metric cannot separate a
  relational density signal from a pure-degree one, the confound control is meaningless -> BLOCK_DISPATCH. Also
  NO_CLEANUP collapses; the four held-out reachability arms differ (arms-must-differ).

## Compute architecture
class: (c) mixed with justification. Storage strategy: SHARDED (each node its own code vector; no bundling --
multi-hop compositional chaining, per META_STORAGE_STRATEGY). GPU-heavy: two InfoNCE binding encoders (full + visible)
are retrained PER DENSITY LEVEL PER SEED (2 densities x 2 encoders x n_seeds), each a batched matmul-heavy train ->
routes to overnight_queue (GPU). Two resolvent solves per level (full T + visible T) are dense closed-form LU
multi-RHS solves over unique goals (LAPACK/cuSOLVER, factored once per gamma). Code-smoothing is one [W,V] cosine
matmul + top-k + a [W,V]x[V,U] matmul per condition (batched). Within a hop all chains + candidates are scored by
batched einsum. ACROSS hops the chain is inherently SEQUENTIAL (hop h candidate set depends on h-1 commit) -- a data
dependency, not a batching flaw; same shape as the certified SR/learned-SR cells. No Python-loop matmul over
independent points. Device-aware torch (cuda if available, else cpu).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): LEARNED_HELDOUT / HELDOUT_MEMCTRL / HELDOUT_CODEALIAS /
#   DEGREE_ONLY produce distinct commit signatures on the held-out subset (asserted per seed per density level).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes. RELATIONAL GAIN is a DIFFERENCE of two paired reach@2 values on the same
#   held-out chains -> chance floor of the difference is 0.0. HARD_PASS rel_gain_rise 0.10 is strictly above the
#   HARD_FAIL flat band 0.03 + 5% band-width. Reference anchors MEASURED@learned-SR/fair-test metrics. crlb: OK.
# - baseline_in_band: MEMORYLESS@1 in (0.05,0.95) on the SPARSE real graph; NO_CLEANUP@2 collapses (anti-saturation).
# - discriminator survives scale: the RELATIONAL-vs-DEGREE discriminator is proven degree-INDEPENDENT by the planted
#   self-test (rel_gain fires on the REL family and is null on the DEG family). Smoke previews the real sparse/dense
#   gain; FULL (3 seeds) canonical. The self-test runs at every mode (fires at self-test scale, SATURATION-safe).
# - HARD_PASS strictly above floor: 0.10 clears the 0.03 flat band + 5% band-width; codes-margin alt-path adds an
#   independent crossing condition.
# - HP_SCOPE: the density-payoff gate applies to the RELATIONAL GAIN (LEARNED minus DEGREE) rise. LEARNED_HELDOUT is
#   the mechanism arm; DEGREE_ONLY is the confound control; CODEALIAS/MEMCTRL are necessity controls; KNOWN_T_FULL/
#   MEMORYLESS/SUPPLIED = positive-control reproductions (SPARSE FULL only); NO_CLEANUP = must-fail.
# - positive_control (Gate D): MEMORYLESS + SUPPLIED + KNOWN_T_FULL reproduce the certified anchors AT the matched
#   FULL sparse regime (n=5000, code_dim=2048); repro drift > 0.10 -> flag. Not applied to the DENSE level (a
#   different graph). CODE-smoothing knobs (WITHHELD_FRAC/SMOOTH_K/SMOOTH_TEMP/SR_GAMMA/SR_BOOST) are imported
#   VERBATIM from the certified learned-SR cell (no re-tuning).
# - sweep axis: density regime in {SPARSE, DENSE}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce both
#   regimes x all held-out arms x depths (regime/arm/depth cardinality).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate. WITHHELD_FRAC/SMOOTH_K/SMOOTH_TEMP/SR_GAMMA/SR_BOOST are
#   PRE-REGISTERED (imported from the certified cell), NOT tuned on real data; the k-core threshold is a fixed
#   MIN_CORE_NODES rule, not tuned for the density verdict; the planted self-test verifies the metric is
#   degree-independent so any real result is a genuine relational/degree signal, not a mis-set knob.
# - PAIRED trials: per density level all arms share identical codes-per-condition + roles + seeds + graph + chain
#   population + withheld split; sparse and dense computed per seed on the same loaded subgraph.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-regime/per-arm flush prints).
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

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import char_trigram_features  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph, make_unitary_roles,
)
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev, sample_chains, build_typed_diradj, _hrr_bind_t, _l2t,
)
from experiments.exp_grounding_multihop_fair_test_unique_successor_goal_v1 import (  # noqa: E402
    build_nbr_table, run_chain_arm as ft_run_chain_arm, run_no_cleanup as ft_run_no_cleanup,
    MEMORYLESS as FT_MEMORYLESS, GOAL_WAYPOINT as FT_GOAL_WAYPOINT,
)
# Reuse the certified SR harness VERBATIM (routing loop + resolvent machinery).
from experiments.exp_grounding_multihop_sr_reachability_routing_v1 import (  # noqa: E402
    build_transition_dense, SRSolver, run_sr_arm, MAX_REACH, SR_GAMMA_PRIMARY, SR_BOOST,
)
# Reuse the certified learned-SR held-out construction + code-smoothing arms VERBATIM.
from experiments.exp_grounding_learned_sr_heldout_reasoning_v1 import (  # noqa: E402
    pick_withheld_ball, visible_edges, build_undirected_adj_simple,
    build_visible_and_smoothed_columns, _norm_columns_to_sr_p,
    WITHHELD_FRAC, SMOOTH_K, SMOOTH_TEMP,
    REPRO_MEM1, REPRO_SUP1, REPRO_SUP2, REPRO_KNOWNT2, REPRO_TOL,
)
# Reuse the density-ladder k-core construction VERBATIM from test #4.
from experiments.exp_graph_inductive_ceiling_v1 import (  # noqa: E402
    build_adj_sets, select_kcore, subgraph_reindex,
)

ANCHOR_NAME = "grounding_density_payoff_relational_reasoning_v1"

# Arm names (held-out reachability arms + general-population anchors)
NO_CLEANUP = "NO_CLEANUP"
MEMORYLESS = "MEMORYLESS"
SUPPLIED_WAYPOINT = "SUPPLIED_WAYPOINT"
KNOWN_T_FULL = "KNOWN_T_FULL"
LEARNED_HELDOUT = "LEARNED_HELDOUT"       # code-smoothed visible-T resolvent (the mechanism arm)
HELDOUT_MEMCTRL = "HELDOUT_MEMCTRL"       # necessity ctrl: visible-T, hole (no smoothing)
HELDOUT_CODEALIAS = "HELDOUT_CODEALIAS"   # necessity ctrl: random-code smoothing
DEGREE_ONLY = "DEGREE_ONLY"               # CONFOUND control: PA / full-graph-degree routing (popularity)
HELDOUT_ARMS = [LEARNED_HELDOUT, HELDOUT_MEMCTRL, HELDOUT_CODEALIAS, DEGREE_ONLY]
ANCHOR_ARMS = [NO_CLEANUP, MEMORYLESS, SUPPLIED_WAYPOINT, KNOWN_T_FULL]

# ---- Pre-registered bands (picked BEFORE the run) ----
REL_GAIN_RISE_HP = 0.10        # HARD_PASS: rel_gain_dense - rel_gain_sparse >= this (relational payoff of density)
CODES_MARGIN_RISE_HP = 0.05    # HARD_PASS alt: codes-beat-random margin rises by this...
CODES_MARGIN_NEAR_ZERO = 0.05  # ...where the sparse margin was ~0 (crossing from ~0)
REL_GAIN_RISE_FLAT = 0.03      # HARD_FAIL: rel_gain rise at/below this...
CODES_MARGIN_RISE_FLAT = 0.02  # ...AND codes-margin rise at/below this -> density is not the relational enabler
NEC_MARGIN = 0.05              # necessity margin (reported): LEARNED beats CODEALIAS / DEGREE by this
MIN_HELDOUT_CHAINS = 25        # minimum held-out chains PER density level for a valid discriminator

# Anti-saturation / must-fail control (on the SPARSE real graph; mirrors the certified learned-SR cell)
BASE_COLLAPSE_ABS = 0.10
BASE_COLLAPSE_FRAC = 0.50
BASE_IN_BAND_HI = 0.95
HOP1_PRESENT = 0.08
SUPPLIED_FIRES_MIN = 0.10

# Self-test bands (planted degree-independence check)
ST_REL_GAIN_MIN = 0.20         # LEARNED beats DEGREE on the REL family (relational signal, degree-blind)
ST_DEG_GAIN_MAX = 0.05         # LEARNED does NOT beat DEGREE on the DEG family (pure-degree; metric shows ~0)
ST_GAP_MIN = 0.15              # separation between the two families

# ---------------------------------------------------------------------------
# Config profiles. SMOKE exercises the SAME arms / code path as FULL; only scale differs.
# FULL matches the certified learned-SR FULL_CFG so the SPARSE anchors reproduce (Gate-D positive control).
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(seeds=[7], n_nodes=400, epochs=10, batch=256, code_dim=128, feat_dim=1024,
                    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                    n_chains=400, chain_chunk=256, min_core=80)
SMOKE_CFG = dict(seeds=[7, 13], n_nodes=1400, epochs=40, batch=256, code_dim=384, feat_dim=2048,
                 temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                 n_chains=1800, chain_chunk=256, min_core=100)
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=5000, epochs=140, batch=512, code_dim=2048, feat_dim=8192,
                temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                n_chains=4000, chain_chunk=256, min_core=250)


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
# DEGREE_ONLY reachability column (the confound control). X[w, j] = full-graph degree of w (popularity), broadcast
# over all goals j. After _norm_columns_to_sr_p (per-column min-max) + run_sr_arm's within-candidate normalization,
# this is exactly PA-routing: among a node's local out-neighbors, prefer the highest-degree (most popular) one. Using
# FULL-graph degree (withheld edges included) makes DEGREE_ONLY a STRONG baseline: withheld hub successors keep their
# true popularity, so the relational gain (LEARNED minus DEGREE) is a CONSERVATIVE measure of code/structure benefit
# beyond popularity.
# ---------------------------------------------------------------------------

def build_degree_columns(deg_full, n_uniq, device):
    deg_t = torch.tensor(np.asarray(deg_full, dtype=np.float64), dtype=torch.float32, device=device)
    return deg_t[:, None].repeat(1, int(n_uniq))     # [n, U]


def _reach_dict(r):
    return {d: r[d] for d in range(1, MAX_REACH + 1)}


# ---------------------------------------------------------------------------
# Run ONE density level (a graph = edges + rels + node_words) end-to-end: held-out split, encoders (full + visible),
# reachability columns (learned / memctrl / codealias / degree / known-T), held-out routing per arm + anchors.
# ---------------------------------------------------------------------------

def run_density_level(level_name, node_words, edges, rels, roles_t, cfg, seed, device, out_dir=None,
                      do_anchors=True):
    n_nodes = len(node_words)
    d = cfg["code_dim"]
    chunk = cfg["chain_chunk"]
    edges = np.asarray(edges, dtype=np.int64)
    rels = np.asarray(rels)

    dir_adj = build_typed_diradj(edges, rels, n_nodes)
    nbr_idx, nbr_rel, nbr_mask, Dmax, mean_out_deg = build_nbr_table(dir_adj, n_nodes, device)
    mean_degree = float(2.0 * edges.shape[0] / max(n_nodes, 1))

    X = char_trigram_features(node_words, cfg["feat_dim"])
    Z_full = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir,
                                       tag="BIND_full_%s" % level_name)
    Zp_full = torch.cat([Z_full, torch.zeros(1, d, device=device)], dim=0)

    # general chains (identical rng offset/sampler as certified cell -> paired anchor reproduction on SPARSE)
    gen_rng = np.random.default_rng(seed + 909)
    g_start, g_targets, g_role = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, gen_rng)
    goals = g_targets[MAX_REACH - 1]

    # held-out split: withhold a contiguous BFS-ball (disjoint subgraph); held-out chains = hop-1 target withheld,
    # goal visible (the first routing decision needs a withheld-candidate reachability estimate).
    adj_u = build_undirected_adj_simple(dir_adj, n_nodes)
    deg_full = np.array([len(adj_u[u]) for u in range(n_nodes)], dtype=np.float64)
    split_rng = np.random.default_rng(seed + 4242)
    withheld_mask = pick_withheld_ball(adj_u, n_nodes, WITHHELD_FRAC, set(), split_rng)
    n_withheld = int(withheld_mask.sum())
    hop1_tgt = g_targets[0]
    heldout_chain_mask = withheld_mask[hop1_tgt] & (~withheld_mask[goals])
    ho_idx = np.where(heldout_chain_mask)[0]
    n_heldout = int(ho_idx.shape[0])

    # visible graph (leakage-safe) -> visible T + visible-trained codes
    e_vis, r_vis = visible_edges(edges, rels, withheld_mask)
    dir_adj_vis = build_typed_diradj(e_vis, r_vis, n_nodes)
    T_vis = build_transition_dense(dir_adj_vis, n_nodes, device)
    sr_solver_vis = SRSolver(T_vis, device)
    Z_vis = train_binding_encoder_dev(X, e_vis, r_vis, roles_t, cfg, seed, device, out_dir=out_dir,
                                      tag="BIND_vis_%s" % level_name)
    Zp_vis = torch.cat([Z_vis, torch.zeros(1, d, device=device)], dim=0)
    Zn_vis = torch.nn.functional.normalize(Z_vis, dim=1)
    alias_gen = torch.Generator(device="cpu").manual_seed(seed + 31337)
    Zn_alias = torch.nn.functional.normalize(
        torch.randn(n_nodes, d, generator=alias_gen).to(device), dim=1)

    # full-T solver + known-T columns
    T_full = build_transition_dense(dir_adj, n_nodes, device)
    sr_solver_full = SRSolver(T_full, device)
    uniq_goals = np.unique(np.asarray(goals, dtype=np.int64))
    Xfull = sr_solver_full.columns(uniq_goals, SR_GAMMA_PRIMARY)
    sr_p_knownT, _u, _c = _norm_columns_to_sr_p(Xfull, goals, n_nodes, device)

    # held-out condition columns on visible-T (learned / memctrl / codealias) + degree column
    cols = build_visible_and_smoothed_columns(sr_solver_vis, uniq_goals, SR_GAMMA_PRIMARY, withheld_mask,
                                              Zn_vis, Zn_alias, SMOOTH_K, SMOOTH_TEMP, n_nodes, device)
    sr_p_learned, _, _ = _norm_columns_to_sr_p(cols["learned"], goals, n_nodes, device)
    sr_p_memctrl, _, _ = _norm_columns_to_sr_p(cols["memctrl"], goals, n_nodes, device)
    sr_p_codealias, _, _ = _norm_columns_to_sr_p(cols["codealias"], goals, n_nodes, device)
    deg_cols = build_degree_columns(deg_full, uniq_goals.shape[0], device)
    sr_p_degree, _, _ = _norm_columns_to_sr_p(deg_cols, goals, n_nodes, device)

    arms = {}
    sigs = {}

    # ---- general-population anchors (Gate-D + anti-sat), SPARSE level only for the positive control ----
    if do_anchors:
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
    heldout_refs = {}
    if n_heldout >= 1:
        gs = g_start[ho_idx]
        gt = [g_targets[hh][ho_idx] for hh in range(MAX_REACH)]
        gr = [g_role[hh][ho_idx] for hh in range(MAX_REACH)]
        srp = dict(learned=sr_p_learned[ho_idx], memctrl=sr_p_memctrl[ho_idx],
                   codealias=sr_p_codealias[ho_idx], degree=sr_p_degree[ho_idx], knownT=sr_p_knownT[ho_idx])
        arm_col = {LEARNED_HELDOUT: "learned", HELDOUT_MEMCTRL: "memctrl",
                   HELDOUT_CODEALIAS: "codealias", DEGREE_ONLY: "degree"}
        for arm, key in arm_col.items():
            r, h, sig = run_sr_arm(Z_vis, Zp_vis, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                                   device, chunk, n_nodes, srp[key], SR_BOOST)
            arms[arm] = dict(reach=r); sigs[arm] = sig
        r_mho, _h, _sa, _s = ft_run_chain_arm(FT_MEMORYLESS, Z_vis, Zp_vis, roles_t, nbr_idx, nbr_rel, nbr_mask,
                                              None, gs, gt, gr, device, chunk, n_nodes)
        r_kho, _h2, _s2 = run_sr_arm(Z_full, Zp_full, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                                     device, chunk, n_nodes, srp["knownT"], SR_BOOST)
        heldout_refs = dict(memoryless=_reach_dict(r_mho), known_t_full=_reach_dict(r_kho))
    else:
        for a in HELDOUT_ARMS:
            arms[a] = dict(reach={dd: float("nan") for dd in range(1, MAX_REACH + 1)})
            sigs[a] = "nan_%s" % a

    present_arms = (ANCHOR_ARMS if do_anchors else []) + HELDOUT_ARMS
    for arm in present_arms:
        _log("  seed=%d level=%s %-18s reach=%s" % (
            seed, level_name, arm, {dd: round(arms[arm]["reach"][dd], 3) for dd in range(1, MAX_REACH + 1)}))
    _log("  seed=%d level=%s mean_deg=%.2f n_nodes=%d n_edges=%d withheld=%d(%.1f%%) heldout_chains=%d/%d" % (
        seed, level_name, mean_degree, n_nodes, int(edges.shape[0]), n_withheld,
        100.0 * n_withheld / max(n_nodes, 1), n_heldout, int(g_start.shape[0])))

    return dict(level=level_name, arms={a: dict(reach=arms[a]["reach"]) for a in present_arms},
                arm_sigs=sigs, heldout_refs=heldout_refs, n_withheld=n_withheld,
                withheld_frac_actual=n_withheld / max(n_nodes, 1), n_heldout_chains=n_heldout,
                n_general=int(g_start.shape[0]), mean_degree=mean_degree, n_nodes=int(n_nodes),
                n_edges=int(edges.shape[0]), code_dim=d)


# ---------------------------------------------------------------------------
# Per-seed: SPARSE (full subgraph) + DENSE (k-core).
# ---------------------------------------------------------------------------

def run_seed(seed, edges, rels, node_words, roles_t, cfg, device, out_dir=None):
    n_nodes = len(node_words)
    edges_np = np.asarray(edges, dtype=np.int64)
    adj_full, _ = build_adj_sets(edges_np, n_nodes)

    sparse = run_density_level("SPARSE", node_words, edges_np, rels, roles_t, cfg, seed, device,
                               out_dir=out_dir, do_anchors=True)

    k, mask = select_kcore(adj_full, n_nodes, cfg["min_core"])
    e2, r2, nw2, _old = subgraph_reindex(edges_np, rels, node_words, mask)
    dense = run_density_level("DENSE", nw2, e2, r2, roles_t, cfg, seed, device,
                              out_dir=out_dir, do_anchors=False)
    dense["kcore_k"] = int(k)

    return dict(seed=seed, sparse=sparse, dense=dense, kcore_k=int(k))


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, meta, cfg):
    def LR(level, arm, dd):
        return _nm([m[level]["arms"][arm]["reach"][dd] for m in per_seed if arm in m[level]["arms"]])

    def HR(level, key, dd):
        return _nm([m[level]["heldout_refs"][key][dd] for m in per_seed if key in m[level].get("heldout_refs", {})])

    # SPARSE anchors (general population) for anti-sat + Gate-D
    base1 = LR("sparse", NO_CLEANUP, 1); base2 = LR("sparse", NO_CLEANUP, 2)
    mem1 = LR("sparse", MEMORYLESS, 1); mem2 = LR("sparse", MEMORYLESS, 2)
    sup1 = LR("sparse", SUPPLIED_WAYPOINT, 1); sup2 = LR("sparse", SUPPLIED_WAYPOINT, 2)
    knownT2 = LR("sparse", KNOWN_T_FULL, 2)

    # per-level held-out reach@2 (primary) + reach@1
    def level_block(level):
        learned2 = LR(level, LEARNED_HELDOUT, 2); learned1 = LR(level, LEARNED_HELDOUT, 1)
        memctrl2 = LR(level, HELDOUT_MEMCTRL, 2)
        codealias2 = LR(level, HELDOUT_CODEALIAS, 2)
        degree2 = LR(level, DEGREE_ONLY, 2); degree1 = LR(level, DEGREE_ONLY, 1)
        ho_mem2 = HR(level, "memoryless", 2); ho_knownT2 = HR(level, "known_t_full", 2)
        rel_gain = (learned2 - degree2) if (learned2 == learned2 and degree2 == degree2) else float("nan")
        codes_margin = (learned2 - codealias2) if (learned2 == learned2 and codealias2 == codealias2) else float("nan")
        n_ho = int(_nm([m[level]["n_heldout_chains"] for m in per_seed]))
        mdeg = _nm([m[level]["mean_degree"] for m in per_seed])
        return dict(learned1=learned1, learned2=learned2, memctrl2=memctrl2, codealias2=codealias2,
                    degree1=degree1, degree2=degree2, ho_mem2=ho_mem2, ho_knownT2=ho_knownT2,
                    rel_gain=rel_gain, codes_margin=codes_margin, n_heldout=n_ho, mean_degree=mdeg)

    S = level_block("sparse")
    D = level_block("dense")
    kcore_k = int(_nm([m["kcore_k"] for m in per_seed]))

    # headline density-payoff deltas
    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")
    rel_gain_rise = _sub(D["rel_gain"], S["rel_gain"])
    codes_margin_rise = _sub(D["codes_margin"], S["codes_margin"])
    reach_rise = _sub(D["learned2"], S["learned2"])             # raw reach rise (reported)
    degree_rise = _sub(D["degree2"], S["degree2"])              # pure-popularity rise (reported)

    # necessity flags (reported)
    codes_necessary_dense = bool(D["learned2"] == D["learned2"] and D["codealias2"] == D["codealias2"]
                                 and D["learned2"] >= D["codealias2"] + NEC_MARGIN)
    relational_over_degree_dense = bool(D["learned2"] == D["learned2"] and D["degree2"] == D["degree2"]
                                        and D["learned2"] >= D["degree2"] + NEC_MARGIN)

    # anti-saturation + baseline-in-band + MM discriminator (on SPARSE real graph)
    hop1_present = bool(mem1 == mem1 and mem1 >= HOP1_PRESENT)
    baseline_in_band = bool(mem1 == mem1 and 0.05 < mem1 < BASE_IN_BAND_HI)
    baseline_collapses = bool(base2 == base2 and base1 == base1
                              and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))
    supplied_fires = bool(sup2 == sup2 and mem2 == mem2 and sup2 >= mem2 + SUPPLIED_FIRES_MIN)
    enough_heldout = bool(S["n_heldout"] >= MIN_HELDOUT_CHAINS and D["n_heldout"] >= MIN_HELDOUT_CHAINS)

    # density-payoff gates (on the RELATIONAL GAIN rise + codes-margin crossing)
    codes_margin_crosses = bool(codes_margin_rise == codes_margin_rise and S["codes_margin"] == S["codes_margin"]
                                and codes_margin_rise >= CODES_MARGIN_RISE_HP
                                and S["codes_margin"] <= CODES_MARGIN_NEAR_ZERO)
    rel_gain_rises = bool(rel_gain_rise == rel_gain_rise and rel_gain_rise >= REL_GAIN_RISE_HP)
    richer_enables = bool(rel_gain_rises or codes_margin_crosses)
    density_no_help = bool(rel_gain_rise == rel_gain_rise and codes_margin_rise == codes_margin_rise
                           and rel_gain_rise <= REL_GAIN_RISE_FLAT and codes_margin_rise <= CODES_MARGIN_RISE_FLAT)

    # Gate-D reproduction (FULL sparse only)
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
    elif richer_enables:
        verdict = "HARD_PASS_RICHER_KNOWLEDGE_ENABLES_REASONING"
    elif density_no_help:
        verdict = "HARD_FAIL_DENSITY_ALONE_NOT_THE_ENABLER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_DENSITY_PAYOFF"

    verdict_msg = (
        "%s || SPARSE(deg=%.2f n_ho=%d): NO_CLEANUP@2=%.3f(collapses=%s) MEMORYLESS@1=%.3f(in_band=%s)@2=%.3f "
        "SUPPLIED@2=%.3f(fires=%s) KNOWN_T@2=%.3f | LEARNED@1=%.3f@2=%.3f DEGREE@1=%.3f@2=%.3f MEMCTRL@2=%.3f "
        "CODEALIAS@2=%.3f | rel_gain=%s codes_margin=%s || DENSE(k=%d deg=%.2f n_ho=%d): LEARNED@1=%.3f@2=%.3f "
        "DEGREE@1=%.3f@2=%.3f MEMCTRL@2=%.3f CODEALIAS@2=%.3f | rel_gain=%s codes_margin=%s "
        "(codes_nec=%s rel>deg=%s) || PAYOFF: rel_gain_rise(GATE)=%s reach_rise=%s degree_rise=%s "
        "codes_margin_rise=%s || HARD_PASS(rel_rise>=%.2f OR codes_cross)=%s HARD_FAIL(rel_rise<=%.2f AND "
        "codes_rise<=%.2f)=%s || repro(full=%s): mem1=%s sup1=%s sup2=%s knownT2=%s || nodes=%d E=%d seeds=%d "
        "run=%s" % (
            verdict, S["mean_degree"], S["n_heldout"], base2, baseline_collapses, mem1, baseline_in_band, mem2,
            sup2, supplied_fires, knownT2, S["learned1"], S["learned2"], S["degree1"], S["degree2"], S["memctrl2"],
            S["codealias2"], _fmt(S["rel_gain"]), _fmt(S["codes_margin"]),
            kcore_k, D["mean_degree"], D["n_heldout"], D["learned1"], D["learned2"], D["degree1"], D["degree2"],
            D["memctrl2"], D["codealias2"], _fmt(D["rel_gain"]), _fmt(D["codes_margin"]),
            codes_necessary_dense, relational_over_degree_dense,
            _fmt(rel_gain_rise), _fmt(reach_rise), _fmt(degree_rise), _fmt(codes_margin_rise),
            REL_GAIN_RISE_HP, richer_enables, REL_GAIN_RISE_FLAT, CODES_MARGIN_RISE_FLAT, density_no_help,
            is_full, repro_mem1_ok, repro_sup1_ok, repro_sup2_ok, repro_knownt2_ok,
            meta["n_nodes"], meta["n_edges"], len(per_seed), "full" if is_full else "smoke"))

    gates = dict(
        verdict=verdict,
        sparse=S, dense=D, kcore_k=kcore_k,
        payoff=dict(rel_gain_sparse=S["rel_gain"], rel_gain_dense=D["rel_gain"], rel_gain_rise_GATE=rel_gain_rise,
                    codes_margin_sparse=S["codes_margin"], codes_margin_dense=D["codes_margin"],
                    codes_margin_rise=codes_margin_rise, reach_rise=reach_rise, degree_rise=degree_rise,
                    rel_gain_rises=rel_gain_rises, codes_margin_crosses=codes_margin_crosses,
                    richer_enables=richer_enables, density_no_help=density_no_help,
                    codes_necessary_dense=codes_necessary_dense, relational_over_degree_dense=relational_over_degree_dense),
        anti_sat=dict(hop1_present=hop1_present, baseline_in_band=baseline_in_band,
                      baseline_collapses=baseline_collapses, supplied_fires=supplied_fires,
                      enough_heldout=enough_heldout),
        positive_control=dict(is_full=is_full, repro_mem1=mem1, repro_sup1=sup1, repro_sup2=sup2,
                              repro_knownt2=knownT2, repro_mem1_ok=repro_mem1_ok, repro_sup1_ok=repro_sup1_ok,
                              repro_sup2_ok=repro_sup2_ok, repro_knownt2_ok=repro_knownt2_ok, repro_ok=repro_ok,
                              anchors=dict(mem1=REPRO_MEM1, sup1=REPRO_SUP1, sup2=REPRO_SUP2,
                                           knownT2=REPRO_KNOWNT2, tol=REPRO_TOL)),
        bands=dict(REL_GAIN_RISE_HP=REL_GAIN_RISE_HP, CODES_MARGIN_RISE_HP=CODES_MARGIN_RISE_HP,
                   CODES_MARGIN_NEAR_ZERO=CODES_MARGIN_NEAR_ZERO, REL_GAIN_RISE_FLAT=REL_GAIN_RISE_FLAT,
                   CODES_MARGIN_RISE_FLAT=CODES_MARGIN_RISE_FLAT, NEC_MARGIN=NEC_MARGIN,
                   MIN_HELDOUT_CHAINS=MIN_HELDOUT_CHAINS, WITHHELD_FRAC=WITHHELD_FRAC, SMOOTH_K=SMOOTH_K,
                   SMOOTH_TEMP=SMOOTH_TEMP, SR_GAMMA_PRIMARY=SR_GAMMA_PRIMARY, SR_BOOST=SR_BOOST),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test. One planted graph, two held-out chain families. REL family: relational signal recoverable by
# code-smoothing, all siblings equal-degree -> LEARNED beats DEGREE (degree-independent). DEG family: true successor
# is a HUB (high degree) with a random code -> DEGREE beats LEARNED (pure popularity). rel_gain(REL) HIGH,
# rel_gain(DEG) ~0. This proves the RELATIONAL GAIN metric is degree-independent (cannot be a pure-degree artifact).
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    device = torch.device("cpu")
    torch.manual_seed(0); np.random.seed(0)
    rng = np.random.default_rng(0)
    d = 96
    Tr = 4
    KSR = 4
    N_HUB_FILL = 8      # visible filler edges that make a DEG-family true successor a high-degree hub
    roles_t = torch.from_numpy(make_unitary_roles(Tr, d, np.random.default_rng(11))).to(device)

    n_cap = 16000
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
    chain_type = []
    n_chains_plant = 260
    budget = MAX_REACH * KSR + N_HUB_FILL + KSR * 2 + 16
    for c in range(n_chains_plant):
        if next_id >= n_cap - budget:
            break
        is_rel = (c % 2 == 0)
        S = _new(_l2t(torch.randn(1, d))[0])                    # start (visible)
        # VISIBLE onward tail tail0 -> tail1 -> ... -> G (all visible; G = tail[MAX_REACH-2])
        tail = []
        prev = None
        for hh in range(MAX_REACH - 1):
            tv = _new(_l2t(torch.randn(1, d))[0])
            tail.append(tv)
            if prev is not None:
                rr = int(rng.integers(0, Tr))
                dir_adj[prev].append((tv, rr)); dir_adj[tv].append((prev, rr))
            prev = tv
        r0 = int(rng.integers(0, Tr))
        if is_rel:
            # REL family: true successor T1 (withheld) code planted NEAR tail0 (visible onward node reaching G);
            # off-siblings (withheld) code near distinct visible dead-ends. ALL siblings have degree 2 (edge to S +
            # edge to their own target) -> DEGREE cannot separate them; LEARNED recovers via code-smoothing.
            true_code = _l2t(Zc[tail[0]:tail[0] + 1])[0] + 0.15 * _l2t(torch.randn(1, d))[0]
            T1 = _new(true_code, hide=True)
            dir_adj[S].append((T1, r0)); dir_adj[T1].append((S, r0))
            dir_adj[T1].append((tail[0], r0)); dir_adj[tail[0]].append((T1, r0))
            for _k in range(KSR - 1):
                dead = _new(_l2t(torch.randn(1, d))[0])
                off_code = _l2t(Zc[dead:dead + 1])[0] + 0.15 * _l2t(torch.randn(1, d))[0]
                off = _new(off_code, hide=True)
                dir_adj[S].append((off, r0)); dir_adj[off].append((S, r0))
                dir_adj[off].append((dead, r0)); dir_adj[dead].append((off, r0))
            true_v = T1
        else:
            # DEG family: true successor H1 (withheld) is a HUB (many visible filler edges -> high full-graph degree)
            # with a RANDOM code (no recoverable relational signal); off-siblings (withheld) are low-degree dead-ends.
            # DEGREE routes to H1 (highest degree); LEARNED (code-smoothing on random code) ties ~1/KSR.
            H1 = _new(_l2t(torch.randn(1, d))[0], hide=True)
            dir_adj[S].append((H1, r0)); dir_adj[H1].append((S, r0))
            dir_adj[H1].append((tail[0], r0)); dir_adj[tail[0]].append((H1, r0))
            for _f in range(N_HUB_FILL):
                fill = _new(_l2t(torch.randn(1, d))[0])         # visible filler (raises H1 full-degree)
                rr = int(rng.integers(0, Tr))
                dir_adj[H1].append((fill, rr)); dir_adj[fill].append((H1, rr))
            for _k in range(KSR - 1):
                off = _new(_l2t(torch.randn(1, d))[0], hide=True)   # low-degree dead-end (edge to S only)
                dir_adj[S].append((off, r0)); dir_adj[off].append((S, r0))
            true_v = H1
        br_tgt[0].append(true_v); br_rid[0].append(r0)
        for hh in range(1, MAX_REACH):
            br_tgt[hh].append(tail[hh - 1]); br_rid[hh].append(int(rng.integers(0, Tr)))
        br_start.append(S); chain_type.append("rel" if is_rel else "deg")

    g_start = np.asarray(br_start, dtype=np.int64)
    g_tgt = [np.asarray(t, dtype=np.int64) for t in br_tgt]
    g_role = [np.asarray(r, dtype=np.int64) for r in br_rid]
    ct = np.asarray(chain_type)

    n = next_id
    Zc = Zc[:n]; dir_adj = dir_adj[:n]; withheld = withheld[:n]
    Z = _l2t(Zc)
    Zp = torch.cat([Z, torch.zeros(1, d, device=device)], dim=0)
    Zn = torch.nn.functional.normalize(Z, dim=1)
    Zn_alias = torch.nn.functional.normalize(torch.randn(n, d, generator=torch.Generator().manual_seed(7)), dim=1)
    nbr_idx, nbr_rel, nbr_mask, Dmax, _mod = build_nbr_table(dir_adj, n, device)

    adj_u = build_undirected_adj_simple(dir_adj, n)
    deg_full = np.array([len(adj_u[u]) for u in range(n)], dtype=np.float64)

    goals = g_tgt[MAX_REACH - 1]
    uniq_goals = np.unique(np.asarray(goals, dtype=np.int64))

    # full-T known
    T_full = build_transition_dense(dir_adj, n, device)
    Xfull = SRSolver(T_full, device).columns(uniq_goals, SR_GAMMA_PRIMARY)
    sr_p_known, _, _ = _norm_columns_to_sr_p(Xfull, goals, n, device)

    # visible graph (edges touching withheld removed)
    e_list, r_list = [], []
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
    deg_cols = build_degree_columns(deg_full, uniq_goals.shape[0], device)
    sr_p_degree, _, _ = _norm_columns_to_sr_p(deg_cols, goals, n, device)

    # held-out chains: hop-1 target withheld, goal visible
    hop1 = g_tgt[0]
    ho_all = np.where(withheld[hop1] & (~withheld[goals]))[0]
    ho_rel = ho_all[ct[ho_all] == "rel"]
    ho_deg = ho_all[ct[ho_all] == "deg"]

    def _run(arm_srp, idx):
        gs = g_start[idx]
        gt = [g_tgt[hh][idx] for hh in range(MAX_REACH)]
        gr = [g_role[hh][idx] for hh in range(MAX_REACH)]
        r, _h, sig = run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr, device, 256, n, arm_srp[idx], SR_BOOST)
        return r, sig

    r_no, _h, _sa, s_no = ft_run_no_cleanup(Z, roles_t, g_start, g_tgt, g_role, device, n)
    # arms-differ on the full held-out set
    _rl, s_learned = _run(sr_p_learned, ho_all)
    _rm, s_memctrl = _run(sr_p_memctrl, ho_all)
    _ra, s_alias = _run(sr_p_alias, ho_all)
    _rd, s_degree = _run(sr_p_degree, ho_all)

    rel_learned, _ = _run(sr_p_learned, ho_rel)
    rel_degree, _ = _run(sr_p_degree, ho_rel)
    deg_learned, _ = _run(sr_p_learned, ho_deg)
    deg_degree, _ = _run(sr_p_degree, ho_deg)

    rel_gain_rel = float(rel_learned[1] - rel_degree[1])
    rel_gain_deg = float(deg_learned[1] - deg_degree[1])
    gap = rel_gain_rel - rel_gain_deg

    nocleanup_ran = bool(r_no[1] == r_no[1])
    learned_recovers_rel = bool(rel_learned[1] == rel_learned[1] and rel_learned[1] >= 0.45)
    degree_recovers_deg = bool(deg_degree[1] == deg_degree[1] and deg_degree[1] >= 0.45)
    rel_gain_fires = bool(rel_gain_rel == rel_gain_rel and rel_gain_rel >= ST_REL_GAIN_MIN)
    deg_gain_null = bool(rel_gain_deg == rel_gain_deg and rel_gain_deg <= ST_DEG_GAIN_MAX)
    gap_ok = bool(gap == gap and gap >= ST_GAP_MIN)
    arms_differ = bool(len({s_learned, s_memctrl, s_alias, s_degree, s_no}) >= 4)
    enough = bool(ho_rel.shape[0] >= 10 and ho_deg.shape[0] >= 10)

    res = dict(n_synth=int(n), n_ho_rel=int(ho_rel.shape[0]), n_ho_deg=int(ho_deg.shape[0]),
               rel_learned1=round(float(rel_learned[1]), 4), rel_degree1=round(float(rel_degree[1]), 4),
               deg_learned1=round(float(deg_learned[1]), 4), deg_degree1=round(float(deg_degree[1]), 4),
               rel_gain_rel=round(rel_gain_rel, 4), rel_gain_deg=round(rel_gain_deg, 4), gap=round(gap, 4),
               nocleanup_ran=nocleanup_ran, learned_recovers_rel=learned_recovers_rel,
               degree_recovers_deg=degree_recovers_deg, rel_gain_fires=rel_gain_fires,
               deg_gain_null=deg_gain_null, gap_ok=gap_ok, arms_differ=arms_differ)
    ok = bool(nocleanup_ran and learned_recovers_rel and degree_recovers_deg and rel_gain_fires
              and deg_gain_null and gap_ok and arms_differ and enough)
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
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (relational-gain not degree-independent): %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS density-payoff: relational gain (LEARNED minus DEGREE) FIRES on the "
                        "relational-signal family and is NULL on the pure-degree family (gap>=0.15); NO_CLEANUP "
                        "collapses; held-out reachability arms differ; k-core + held-out split + code-smoothing + "
                        "degree confound control exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    edges = np.asarray(edges, dtype=np.int64)
    _log("subgraph: n_nodes=%d n_edges=%d rel_types=%d median_degree=%s"
         % (len(node_ids), edges.shape[0], T, meta.get("median_degree")))
    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, edges, rels, node_words, roles_t, cfg, device, out_dir=out_dir_path)
            # regime/arm/depth cardinality + arms-must-differ (META_RULE_AF) per density level
            for level in ("sparse", "dense"):
                lv = pm[level]
                for a in HELDOUT_ARMS:
                    missing = [dd for dd in range(1, MAX_REACH + 1)
                               if a not in lv["arms"] or dd not in lv["arms"][a]["reach"]]
                    if missing:
                        raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d level=%s arm=%s missing=%s"
                                           % (seed, level, a, missing))
                if lv["n_heldout_chains"] >= 1:
                    hs = [lv["arm_sigs"][a] for a in HELDOUT_ARMS]
                    if len(set(hs)) < len(hs):
                        raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d level=%s sigs=%s"
                                           % (seed, level, hs))
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
