"""Stage-5 CG cell: LANDMARK-ROUTING autonomous traversal -- does routing a long goal-directed walk through a
precomputed hub/landmark waypoint (instead of aiming continuously at the distant final goal) recover the
supplied-waypoint ceiling the plain-greedy autonomous arm fell short of?

BACKGROUND. grounding_multihop_autonomous_subgoal_greedy_v1 landed MIDDLE_BAND_CG_PARTIAL: plain-greedy autonomous
hop-selection (aim continuously at the FINAL goal) reaches reach@2=0.181 (beats memoryless floor 0.121, but only
0.363x the supplied-waypoint ceiling 0.499 -- distant-goal signal too weak at multi-hop range). This cell tests
the SECOND-stage upgrade (research notes/research_landmark_subgoal_hub_routing_autonomous_traversal_2026-07-09.md +
exp_dev_handoff_research_landmark_subgoal_hub_routing_2026-07-09.md): precompute a landmark set once, per query
route via a landmark waypoint (goal-condition on the LANDMARK, walk there, then fall back to direct
goal-conditioning on the true goal). Zero new primitive: reuses local-neighborhood-scoping (nbr table) +
goal-conditioning cosine-argmax (the certified MM) verbatim, just re-targeted onto a landmark then chained.

PHASE-0 PRE-CHECK (ran BEFORE this cell; see report). The reader-cell KB subgraph (n=4440, 14767 edges) is NOT
expander-like: betweenness gini=0.866 (top-1% of nodes hold 38% of all betweenness), degree max/mean=50.7x
(gini=0.504), clustering=0.146. Clean hub/bottleneck structure present. Landmarks are ~1-hop reachable for the
majority of path nodes (K=256 degree/betweenness landmarks: median nearest-landmark hop=1, 87% within 1 hop).
The reachability TAIL (~13-24% of path nodes still >1 hop from nearest landmark, maxhop=3) is the pre-registered
primary risk carried into this cell -- for those nodes the distant-target pathology can recur inside the leg.

MECHANISM. LANDMARK_SEEDED per query (current node C0, final goal G): (1) landmark set = top-K nodes by degree
(degree-proxy default per handoff; one-time offline). (2) select waypoint L1 = argmax over landmarks of
[cos(Z[C0],Z[l]) + cos(Z[l],Z[G])] -- the ALT triangle pattern: a landmark that is both reachable-from-start AND
goal-ward (a genuine midpoint), reusing only the certified cosine primitive. (3) walk C->L1 using the certified
goal-conditioned local argmax (base memoryless relation-bind score + gamma * cos(candidate, ACTIVE goal)), where
the ACTIVE goal per chain per hop is L1 while the goal is still farther than the landmark, switching to G once
cos(cur,G) >= cos(cur,L1) or L1 is reached (the note's "fall back to direct goal-conditioning" step). Flat,
single-landmark 2-leg skeleton (start -> L1 -> goal); no recursive multi-level landmark skeleton (deferred).

ARMS (paired: identical learned codes + identical planted general chains + identical seeds across all arms; only
the QUERY differs). The first four REPRODUCE the greedy-cell / fair-test anchors VERBATIM (Gate-D positive control):
  NO_CLEANUP        : global-cleanup-only chain (must-fail / anti-saturation control; collapses at reach>=2).
  MEMORYLESS        : goal-blind local decoder = the fair-test floor (repro ~0.453 @1 / 0.121 @2).
  SUPPLIED_WAYPOINT : = the fair-test GOAL_WAYPOINT MM ceiling; HANDED the true next waypoint (repro ~0.756 @1 /
                      0.500 @2). The bar the landmark arm must approach.
  AUTONOMOUS_GREEDY : the plain-greedy autonomous arm just measured (aim continuously at final goal; ~0.181 @2).
                      The thing LANDMARK_SEEDED must BEAT.
  LANDMARK_SEEDED   : THE CG CANDIDATE. Route via a precomputed degree-proxy landmark waypoint (above).
  (secondary, logged not gated) LANDMARK_GOAL_ONLY: same but L1 selected by goal-cosine only (the note's literal
                      step-2 default), to see whether midpoint vs goal-only selection matters.

CG WIN BAR (pre-registered from the research note; verdict on LANDMARK_SEEDED reach@2). Anchors: memoryless floor
0.121, plain-greedy 0.181, supplied ceiling 0.499; gap-to-close = 0.499-0.181 = 0.318.
  HARD_PASS_LM = LANDMARK_SEEDED reach@2 >= LM_HARD_PASS (0.40) AND LANDMARK_SEEDED reach@2 > AUTONOMOUS_GREEDY
                 reach@2 (bought something over plain greedy) -> landmark routing recovers >=69% of the gap.
  HARD_FAIL_LM = LANDMARK_SEEDED reach@2 <= LM_HARD_FAIL (0.20) -> indistinguishable from plain-greedy 0.181;
                 landmark precompute bought nothing (diagnose via Phase-0 graph structure before pivoting).
  MIDDLE_BAND  = 0.20 < reach@2 < 0.40 -> beats greedy but short of the recover-the-gap bar.
Reported (never gated): landmark-vs-greedy delta, landmark-vs-supplied ratio, delta-vs-dimension (smoke vs full).

CAPABILITY FRAMING (3-part standard; CG claim, verify-able): DIFFERENT CHANNEL = downstream reach@2/@3 (top-1
commit chained); LIVE ALTERNATIVE = plain-greedy autonomous genuinely falls short at multi-hop range (0.181 vs
0.499); NECESSITY = landmark-routing vs plain-greedy ablation, both paired. Report the landmark-vs-supplied RATIO
and landmark-vs-greedy DELTA, never an absolute bar above the ceiling.

HONESTY: REAL CG'd teacher-free relational learned codes (char-trigram + InfoNCE binding encoder) over the REAL
ConceptNet typed subgraph; top-1 commit fidelity; NO language understanding claimed. The FINAL goal handed to the
autonomous/landmark arms is a legitimate part of any goal-directed traversal's own specification; INTERMEDIATE
waypoints are NOT handed (that is the MM->CG difference). The landmark set is a one-time degree precompute over the
graph structure (no per-query supervision). Reuses the greedy-cell / fair-test / perhop-cleanup VET-landed
encoder/chain/nbr/local-scoping primitives VERBATIM (calibration continuity + no drift). Teacher-free, ASCII-only,
device-aware torch (cuda if available, else cpu).

## Compute architecture
class: (c) mixed with justification. Storage strategy: SHARDED (each node its own code vector; no bundling --
compositional multi-hop chaining, per META_STORAGE_STRATEGY). Within each hop, all chains + all local candidates
are scored by batched matmul/einsum (cuda when available). Landmark selection is a batched [C,K] cosine matmul.
ACROSS hops the chain is genuinely SEQUENTIAL (hop h's candidate set depends on hop h-1's committed node) -- an
inherent data dependency, not a batching flaw; same shape as the greedy/fair-test cells which ran 3 seeds FULL in
~16s on cuda. No Python-loop matmul over independent phase points.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; LANDMARK_SEEDED commit-sig != AUTONOMOUS_GREEDY != SUPPLIED
#   != MEMORYLESS != NO_CLEANUP; asserted per seed on distinct commit signatures).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0002 at n=5000). Reference points are MEASURED anchors, not a
#   closed-form floor: MEMORYLESS reach@2=0.121, plain-greedy 0.181, SUPPLIED 0.499 (MEASURED@greedy-cell +
#   fair-test metrics.json). HARD_PASS bar 0.40 is on the achievable side (SUPPLIED already demonstrated 0.499 is
#   reachable with a goal signal; the question is whether landmark-mediated routing recovers most of that).
#   crlb_reachability: OK (0.40 < 0.499 ceiling).
# - baseline_in_band: MEMORYLESS@1 in (0.05, 0.95) (repro ~0.453). NO_CLEANUP@2 collapses (anti-saturation).
# - discriminator survives scale: the MM discriminator (SUPPLIED >> MEMORYLESS) is graph-structural and FIRES AT
#   SMOKE on the real subgraph; asserted at smoke (anti-sat gate). The CG question (LANDMARK vs greedy vs SUPPLIED)
#   is the MEASUREMENT -- smoke reports it as a preview; FULL (3 seeds) is canonical. The must-fail control
#   NO_CLEANUP collapses AT smoke scale (SATURATION-VACUOUS guard). Mechanism CAN-fire proven by the clean-hub
#   planted self-test (LANDMARK_SEEDED ~ SUPPLIED and >> greedy when the graph HAS hub structure).
# - HARD_PASS strictly above floor: 0.40 is a clear categorical margin over plain-greedy 0.181 and > HARD_FAIL
#   0.20 + 5% band-width; not an at-floor result.
# - HP_SCOPE: the CG win gate applies to LANDMARK_SEEDED only. SUPPLIED_WAYPOINT / MEMORYLESS / AUTONOMOUS_GREEDY =
#   positive-control reproductions (must reproduce the anchors within tolerance for the discriminator to be valid);
#   NO_CLEANUP = must-fail control (must collapse). LANDMARK_GOAL_ONLY = secondary (reported, not gated).
# - positive_control (Gate D): MEMORYLESS + SUPPLIED_WAYPOINT + AUTONOMOUS_GREEDY reproduce the greedy-cell /
#   fair-test MEASURED anchors AT THE MATCHED FULL regime (same n_nodes/code_dim/feat_dim/epochs/seeds/chains);
#   repro drift > 0.10 -> flag.
# - sweep axis: hop depth d in {1,2,3,4}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms x
#   all depths (arm/depth-cardinality check).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate. GAMMA is PRE-REGISTERED (= certified GOAL_GAMMA 1.5),
#   NOT tuned on real data; the clean-hub self-test verifies gamma=1.5 lets LANDMARK_SEEDED recover ~SUPPLIED on a
#   planted hub graph (signal present), so any real-data collapse is a genuine graph-structure/signal-weakness
#   negative, not a mis-set knob. Landmark count K is a graph-structure param (Phase-0-informed, K~5% of nodes),
#   NOT tuned to maximize the discriminator.
# - PAIRED trials (arm-comparison discriminator): all arms share identical codes + roles + seeds + graph + dim +
#   general-chain population.
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-epoch/per-seed flush prints + heartbeat).
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
# Reuse the plain-greedy autonomous arm VERBATIM (the anchor LANDMARK_SEEDED must beat).
from experiments.exp_grounding_multihop_autonomous_subgoal_greedy_v1 import (  # noqa: E402
    run_autonomous_arm,
    AUTO_GAMMA,
)

ANCHOR_NAME = "grounding_multihop_landmark_routing_v1"

MAX_REACH = 4
HIT_K = 10
GAMMA = AUTO_GAMMA   # = certified GOAL_GAMMA 1.5 (pre-registered; NOT tuned on real data)

# Arm names
NO_CLEANUP = "NO_CLEANUP"
MEMORYLESS = "MEMORYLESS"                        # goal-blind floor (= fair-test MEMORYLESS)
SUPPLIED_WAYPOINT = "SUPPLIED_WAYPOINT"          # MM ceiling (= fair-test GOAL_WAYPOINT); handed the true waypoint
AUTONOMOUS_GREEDY = "AUTONOMOUS_GREEDY"          # plain-greedy autonomous (aim continuously at final goal)
LANDMARK_SEEDED = "LANDMARK_SEEDED"             # CG candidate (primary); route via degree-proxy landmark (midpoint)
LANDMARK_GOAL_ONLY = "LANDMARK_GOAL_ONLY"       # secondary; landmark selected by goal-cosine only (note default)
ALL_ARMS = [NO_CLEANUP, MEMORYLESS, SUPPLIED_WAYPOINT, AUTONOMOUS_GREEDY, LANDMARK_SEEDED, LANDMARK_GOAL_ONLY]

# ---------------------------------------------------------------------------
# Pre-registered bands (picked BEFORE the run; from the research note). Reach = TOP-1 COMMIT accuracy.
# ---------------------------------------------------------------------------
LM_HARD_PASS = 0.40         # HARD_PASS: LANDMARK_SEEDED reach@2 >= this AND > AUTONOMOUS_GREEDY reach@2
LM_HARD_FAIL = 0.20         # HARD_FAIL: LANDMARK_SEEDED reach@2 <= this (indistinguishable from plain-greedy 0.181)

# Anti-saturation / must-fail control (mirrors greedy cell)
BASE_COLLAPSE_ABS = 0.10
BASE_COLLAPSE_FRAC = 0.50
BASE_IN_BAND_HI = 0.95
HOP1_PRESENT = 0.08
SUPPLIED_FIRES_MIN = 0.10   # MM discriminator: SUPPLIED reach@2 >= MEMORYLESS reach@2 + this (must fire at scale)

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
# FULL config is IDENTICAL to the greedy/fair-test FULL_CFG so anchors reproduce. n_landmarks ~ 5% of nodes
# (Phase-0-informed: at K=256/n=4440, 87% of path nodes within 1 hop of a landmark).
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(seeds=[7], n_nodes=400, epochs=10, batch=256, code_dim=128, feat_dim=1024,
                    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                    n_chains=200, chain_chunk=256, n_landmarks=32)
SMOKE_CFG = dict(seeds=[7, 13], n_nodes=1800, epochs=60, batch=256, code_dim=512, feat_dim=4096,
                 temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                 n_chains=700, chain_chunk=256, n_landmarks=100)
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=5000, epochs=140, batch=512, code_dim=2048, feat_dim=8192,
                temp=0.10, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                n_chains=1200, chain_chunk=256, n_landmarks=256)


def select_landmarks(dir_adj, n_nodes, k):
    """Degree-proxy landmark set: top-k nodes by out-degree (dir_adj symmetric -> undirected degree)."""
    deg = np.array([len(dir_adj[u]) for u in range(n_nodes)], dtype=np.int64)
    k = int(min(k, n_nodes))
    idx = np.argsort(-deg)[:k]
    return idx.astype(np.int64), deg


# ---------------------------------------------------------------------------
# LANDMARK-ROUTING arm. Per chain: pick waypoint L1 among the landmark set (midpoint = start-similar AND
# goal-similar, the ALT triangle pattern; or goal-only if selection='goal'); then per hop score real neighbors by
# base memoryless relation-bind score + gamma * cos(candidate, ACTIVE goal), where ACTIVE goal = L1 while the goal
# is still farther than the landmark, switching to the final goal G once cos(cur,G) >= cos(cur,L1) or L1 reached.
# Reuses local-neighborhood scoping (nbr_idx) + goal-conditioning cosine-argmax VERBATIM; only the ACTIVE-goal code
# per chain per hop differs from the plain-greedy arm. Flat single-landmark 2-leg skeleton (start -> L1 -> goal).
# ---------------------------------------------------------------------------

def run_landmark_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, start, targets, role_ids,
                     device, chunk, n_nodes, gamma, landmark_ids, selection="midpoint"):
    L = len(targets)
    C = start.shape[0]
    cur = torch.from_numpy(start).to(device)
    goal = torch.from_numpy(targets[L - 1]).to(device)      # FINAL goal = chain terminal node (same across hops)
    lm = torch.as_tensor(landmark_ids, dtype=torch.long, device=device)   # [K]
    Zlm = Z[lm]                                             # [K, d] (codes L2-normed)
    zg = Z[goal.clamp(max=n_nodes - 1)]                    # [C, d] final-goal code
    zc0 = Z[cur.clamp(max=n_nodes - 1)]                    # [C, d] start-node code
    sim_lg = zg @ Zlm.t()                                  # [C, K] landmark<->goal cosine
    if selection == "midpoint":
        sim_cl = zc0 @ Zlm.t()                             # [C, K] landmark<->start cosine
        score_lm = sim_lg + sim_cl                          # ALT triangle: reachable-from-start AND goal-ward
    else:                                                   # 'goal' = the note's literal step-2 default
        score_lm = sim_lg
    l1_local = score_lm.argmax(dim=1)                       # [C]
    L1 = lm[l1_local]                                       # [C] chosen landmark node id per chain
    zL1 = Z[L1]                                             # [C, d]

    reach = {}
    hit10 = {}
    commit_sig = []
    n_aim_L1 = 0
    n_aim_G = 0
    n_total = 0
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
            zg_blk = zg[b0:b1]
            zL1_blk = zL1[b0:b1]
            L1_blk = L1[b0:b1]
            cand = nbr_idx[cur_blk]                          # [b, Dmax] real local out-neighbors
            mask = nbr_mask[cur_blk]                         # [b, Dmax]
            Zc = Zp[cand]                                    # [b, Dmax, d]
            p = _l2t(pred_blk)
            base = torch.einsum("bd,bkd->bk", p, Zc)         # memoryless local score
            zcur = Z[cur_blk.clamp(max=n_nodes - 1)]         # [b, d]
            gG = (zcur * zg_blk).sum(dim=1)                  # [b] cur -> final-goal cosine
            gL1 = (zcur * zL1_blk).sum(dim=1)                # [b] cur -> landmark cosine
            reached = (cur_blk == L1_blk)
            aim_G = (gG >= gL1) | reached                    # [b] switch to direct goal-conditioning
            active = torch.where(aim_G[:, None], zg_blk, zL1_blk)   # [b, d] ACTIVE goal code
            gcos = torch.einsum("bkd,bd->bk", Zc, active)    # [b, Dmax] candidate -> ACTIVE-goal cosine
            s = base + gamma * gcos.clamp(min=0.0)
            s = s.masked_fill(~mask, float("-inf"))
            nonempty = mask.any(dim=1)
            la = s.argmax(dim=1)
            b_ids = torch.arange(cur_blk.shape[0], device=device)
            picked = cand[b_ids, la]
            committed[b0:b1] = torch.where(nonempty, picked, torch.full_like(picked, n_nodes))
            topk = s.topk(min(HIT_K, s.shape[1]), dim=1).indices
            topk_ids = torch.gather(cand, 1, topk)
            hitk[b0:b1] = (topk_ids == tgt[b0:b1, None]).any(dim=1) & nonempty
            n_aim_G += int((aim_G & nonempty).sum().item())
            n_aim_L1 += int((~aim_G & nonempty).sum().item())
            n_total += int(nonempty.sum().item())
        reach[h + 1] = float((committed == tgt).float().mean().item())
        hit10[h + 1] = float(hitk.float().mean().item())
        commit_sig.append(committed.detach().to("cpu").numpy().astype(np.int64))
        cur = committed
    sig = hashlib.sha256(np.concatenate(commit_sig).tobytes()).hexdigest()
    stats = dict(n_aim_L1=n_aim_L1, n_aim_G=n_aim_G, n_total=n_total,
                 aim_L1_frac=(n_aim_L1 / n_total) if n_total > 0 else float("nan"),
                 n_landmarks=int(len(landmark_ids)), selection=selection)
    return reach, hit10, sig, stats


# ---------------------------------------------------------------------------
# Per-seed run: all arms on the identical general-chain population + identical learned codes (paired).
# ---------------------------------------------------------------------------

def run_seed(seed, node_words, edges, rels, dir_adj, ksr_map, has_rel, roles_t,
             nbr_idx, nbr_rel, nbr_mask, mean_out_deg, landmark_ids, T, cfg, device, out_dir=None):
    n_nodes = len(node_words)
    chunk = cfg["chain_chunk"]
    X = char_trigram_features(node_words, cfg["feat_dim"])
    Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_lm")
    enc_dig = hashlib.sha256(Z.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()
    Zp = torch.cat([Z, torch.zeros(1, cfg["code_dim"], device=device)], dim=0)

    # general chains (IDENTICAL rng offset + sampler as the greedy/fair-test cell -> paired reproduction)
    gen_rng = np.random.default_rng(seed + 909)
    g_start, g_targets, g_role = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, gen_rng)
    Cg = int(g_start.shape[0])

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
    # AUTONOMOUS_GREEDY (plain-greedy autonomous anchor -> the thing landmark must beat)
    r, h, sig, vg = run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                       device, chunk, n_nodes, GAMMA, verify=False)
    arms[AUTONOMOUS_GREEDY] = dict(reach=r, hit10=h, greedy_stats=vg)
    sigs[AUTONOMOUS_GREEDY] = sig
    # LANDMARK_SEEDED (primary CG candidate; midpoint selection)
    r, h, sig, ls = run_landmark_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                     device, chunk, n_nodes, GAMMA, landmark_ids, selection="midpoint")
    arms[LANDMARK_SEEDED] = dict(reach=r, hit10=h, landmark_stats=ls)
    sigs[LANDMARK_SEEDED] = sig
    # LANDMARK_GOAL_ONLY (secondary; goal-cosine selection = note default)
    r, h, sig, lg = run_landmark_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                     device, chunk, n_nodes, GAMMA, landmark_ids, selection="goal")
    arms[LANDMARK_GOAL_ONLY] = dict(reach=r, hit10=h, landmark_stats=lg)
    sigs[LANDMARK_GOAL_ONLY] = sig

    for arm in ALL_ARMS:
        _log("  seed=%d %-18s reach@[1..%d]=%s" % (
            seed, arm, MAX_REACH, {dd: round(arms[arm]["reach"][dd], 3) for dd in range(1, MAX_REACH + 1)}))

    return dict(seed=seed, arms=arms, arm_sigs=sigs, encoder_digest=enc_dig, n_general=Cg,
                code_dim=cfg["code_dim"], mean_out_deg=mean_out_deg, n_landmarks=int(len(landmark_ids)))


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
    lm1 = R(LANDMARK_SEEDED, 1); lm2 = R(LANDMARK_SEEDED, 2); lm3 = R(LANDMARK_SEEDED, 3)
    lg1 = R(LANDMARK_GOAL_ONLY, 1); lg2 = R(LANDMARK_GOAL_ONLY, 2); lg3 = R(LANDMARK_GOAL_ONLY, 3)

    # CG headline metrics (primary = LANDMARK_SEEDED)
    ratio2 = (lm2 / sup2) if (sup2 == sup2 and sup2 > 1e-9) else float("nan")
    ratio3 = (lm3 / sup3) if (sup3 == sup3 and sup3 > 1e-9) else float("nan")
    delta2_vs_greedy = (lm2 - auto2) if (lm2 == lm2 and auto2 == auto2) else float("nan")
    delta2_vs_mem = (lm2 - mem2) if (lm2 == lm2 and mem2 == mem2) else float("nan")
    goalonly_delta2 = (lg2 - lm2) if (lg2 == lg2 and lm2 == lm2) else float("nan")

    # anti-saturation + baseline-in-band + MM-discriminator-fires
    hop1_present = bool(mem1 == mem1 and mem1 >= HOP1_PRESENT)
    baseline_in_band = bool(mem1 == mem1 and 0.05 < mem1 < BASE_IN_BAND_HI)
    baseline_collapses = bool(base2 == base2 and base1 == base1
                              and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))
    supplied_fires = bool(sup2 == sup2 and mem2 == mem2 and sup2 >= mem2 + SUPPLIED_FIRES_MIN)

    # CG gates (on LANDMARK_SEEDED reach@2)
    lm_hard_pass = bool(lm2 == lm2 and auto2 == auto2 and lm2 >= LM_HARD_PASS and lm2 > auto2)
    lm_hard_fail = bool(lm2 == lm2 and lm2 <= LM_HARD_FAIL)

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
    elif is_full and not repro_ok:
        verdict = "INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT"
    elif lm_hard_pass:
        verdict = "HARD_PASS_CG_LANDMARK"
    elif lm_hard_fail:
        verdict = "HARD_FAIL_CG_LANDMARK_VACUOUS"
    else:
        verdict = "MIDDLE_BAND_CG_LANDMARK_PARTIAL"

    lm_stats = per_seed[0]["arms"][LANDMARK_SEEDED].get("landmark_stats", {})
    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f @2=%.3f(collapses=%s) || MEMORYLESS @1=%.3f(in_band=%s) @2=%.3f @3=%.3f || "
        "SUPPLIED_WAYPOINT @1=%.3f @2=%.3f @3=%.3f (fires=%s) || AUTONOMOUS_GREEDY @1=%.3f @2=%.3f @3=%.3f || "
        "LANDMARK_SEEDED @1=%.3f @2=%.3f @3=%.3f || LANDMARK_GOAL_ONLY @2=%.3f (d_vs_mid=%s) || CG: "
        "ratio@2(lm/sup)=%s ratio@3=%s delta@2(lm-greedy)=%s delta@2(lm-mem)=%s aim_L1_frac=%s K=%d || "
        "HARD_PASS=(lm2>=%.2f AND lm2>greedy2)=%s HARD_FAIL=(lm2<=%.2f)=%s || repro(full=%s): mem1=%s sup1=%s "
        "sup2=%s auto2=%s || gamma=%.2f n_gen=%d nodes=%d E=%d rel=%d seeds=%d run=%s" % (
            verdict, base1, base2, baseline_collapses, mem1, baseline_in_band, mem2, mem3,
            sup1, sup2, sup3, supplied_fires, auto1, auto2, auto3, lm1, lm2, lm3,
            lg2, _fmt(goalonly_delta2), _fmt(ratio2), _fmt(ratio3), _fmt(delta2_vs_greedy), _fmt(delta2_vs_mem),
            _fmt(lm_stats.get("aim_L1_frac", float("nan"))), int(lm_stats.get("n_landmarks", -1)),
            LM_HARD_PASS, lm_hard_pass, LM_HARD_FAIL, lm_hard_fail, is_full,
            repro_mem1_ok, repro_sup1_ok, repro_sup2_ok, repro_auto2_ok,
            GAMMA, per_seed[0]["n_general"], meta["n_nodes"], meta["n_edges"],
            meta.get("n_relation_types", -1), len(per_seed), "full" if is_full else "smoke"))

    gates = dict(
        verdict=verdict,
        reach={a: {d: R(a, d) for d in range(1, MAX_REACH + 1)} for a in ALL_ARMS},
        cg=dict(memoryless_reach2=mem2, supplied_reach2=sup2, autonomous_greedy_reach2=auto2,
                landmark_seeded_reach2=lm2, landmark_goal_only_reach2=lg2,
                landmark_seeded_reach1=lm1, landmark_seeded_reach3=lm3,
                ratio2=ratio2, ratio3=ratio3, delta2_vs_greedy=delta2_vs_greedy, delta2_vs_mem=delta2_vs_mem,
                goalonly_delta2=goalonly_delta2, lm_hard_pass=lm_hard_pass, lm_hard_fail=lm_hard_fail,
                landmark_stats=lm_stats),
        anti_sat=dict(hop1_present=hop1_present, baseline_in_band=baseline_in_band,
                      baseline_collapses=baseline_collapses, supplied_fires=supplied_fires),
        positive_control=dict(is_full=is_full, repro_mem1=mem1, repro_sup1=sup1, repro_sup2=sup2, repro_auto2=auto2,
                              repro_mem1_ok=repro_mem1_ok, repro_sup1_ok=repro_sup1_ok, repro_sup2_ok=repro_sup2_ok,
                              repro_auto2_ok=repro_auto2_ok, repro_ok=repro_ok,
                              anchors=dict(mem1=REPRO_MEM1, sup1=REPRO_SUP1, sup2=REPRO_SUP2, auto2=REPRO_AUTO2,
                                           tol=REPRO_TOL)),
        bands=dict(LM_HARD_PASS=LM_HARD_PASS, LM_HARD_FAIL=LM_HARD_FAIL, SUPPLIED_FIRES_MIN=SUPPLIED_FIRES_MIN,
                   BASE_COLLAPSE_ABS=BASE_COLLAPSE_ABS, HOP1_PRESENT=HOP1_PRESENT, GAMMA=GAMMA,
                   n_landmarks=cfg["n_landmarks"]),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test (planted CLEAN-HUB graph + real local scoping). Proves: chain machinery
# works; NO_CLEANUP collapses; MEMORYLESS aliased; SUPPLIED recovers; plain-greedy (aim distant goal) FAILS because
# the goal signal is absent on pre-hub nodes; and -- the load-bearing positive control for THIS cell -- when the
# graph HAS a hub on the path (pre-hub nodes carry a signal toward the HUB, the hub carries the goal signal),
# LANDMARK_SEEDED recovers ~SUPPLIED and >> plain-greedy. So a real-data collapse is a genuine graph-structure /
# signal-weakness negative, not a broken mechanism or mis-set gamma. arms differ.
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    device = torch.device("cpu")
    torch.manual_seed(0)            # deterministic planted-graph codes (torch.randn below) -> stable self-test
    np.random.seed(0)
    rng = np.random.default_rng(0)
    d = 96
    T = 4
    KSR = 3
    n_cap = 6000
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

    # CLEAN-HUB BRANCH chains, depth MAX_REACH. Each chain routes THROUGH a per-chain hub node placed at hop index
    # HUB_HOP. Two INDEPENDENT random directions per chain: g_c (goal) and h_c (hub-routing). EVERY on-path node is
    # relation-bind-consistent with its predecessor (contains pred) so MEMORYLESS / SUPPLIED / the base term can
    # identify the r-typed successor; the extra planted component is what the goal-cosine term keys on:
    #   pre-hub on-path  = pred + strong h_c (route-toward-hub signal), NO goal component
    #                      -> plain-greedy (aim distant goal G) is aliased on pre-hub branch points (cos to G ~0);
    #                         landmark-routing (aim hub) picks it (cos to hub via the shared h_c channel).
    #   hub on-path      = pred + strong g_c + strong h_c  -> reachable via h_c AND carries the goal signal + high
    #                      degree (dummy neighbors) so degree-proxy selects it as a landmark; L1 midpoint selection
    #                      keys on cos(start,hub) (h_c) + cos(hub,goal) (g_c).
    #   post-hub on-path = pred + strong g_c  -> after the hub, aiming at the goal works.
    #   KSR-1 siblings   = pred + small noise (aliased; relation direction only, no hub/goal component).
    HUB_HOP = 1
    HUB_EXTRA_DEG = 30
    br_start, br_tgt, br_rid = [], [[] for _ in range(MAX_REACH)], [[] for _ in range(MAX_REACH)]
    hub_ids = []
    for _c in range(90):
        if next_id >= n_cap - (MAX_REACH * KSR + HUB_EXTRA_DEG + 12):
            break
        g_c = _l2t(torch.randn(1, d))[0]                      # per-chain goal direction
        h_c = _l2t(torch.randn(1, d))[0]                      # per-chain hub-routing direction (independent of g_c)
        cur = _new(_l2t(torch.randn(1, d))[0] + 1.4 * h_c)   # start: carries HUB-routing component, NO goal
        start_node = cur
        chain_hub = None
        for h in range(MAX_REACH):
            r = int(rng.integers(0, T))
            pred = _l2t(_hrr_bind_t(roles_t[r:r + 1], _l2t(Z2[cur:cur + 1])))[0]
            if h == HUB_HOP:
                # the HUB node: relation-consistent (pred) + goal + hub-routing channel (the pivot). Component
                # magnitude kept MODERATE so SUPPLIED's one-step lookahead onto the hub is not over-diluted.
                true_v = _new(pred + 1.0 * g_c + 1.3 * h_c + 0.2 * _l2t(torch.randn(1, d))[0])
                chain_hub = true_v
                # inflate hub degree so degree-proxy selects it as a landmark
                for _e in range(HUB_EXTRA_DEG):
                    if next_id >= n_cap - 4:
                        break
                    dummy = _new(_l2t(torch.randn(1, d))[0])
                    dir_adj[true_v].append((dummy, int(rng.integers(0, T))))
                    dir_adj[dummy].append((true_v, int(rng.integers(0, T))))
            elif h < HUB_HOP:
                # pre-hub on-path: relation-consistent (pred) + hub-routing channel, NO goal signal
                true_v = _new(pred + 1.5 * h_c + 0.3 * _l2t(torch.randn(1, d))[0])
            else:
                # post-hub on-path: relation-consistent (pred) + GOAL component (goal signal now present)
                true_v = _new(pred + 1.4 * g_c + 0.3 * _l2t(torch.randn(1, d))[0])
            dir_adj[cur].append((true_v, r))
            for _k in range(KSR - 1):
                off = _new(pred + 0.6 * _l2t(torch.randn(1, d))[0])   # aliased sibling (relation only)
                dir_adj[cur].append((off, r))
            br_tgt[h].append(true_v); br_rid[h].append(r)
            cur = true_v
        if chain_hub is not None:
            hub_ids.append(chain_hub)
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
    # degree-proxy landmark set: hubs (high degree) must be captured
    landmark_ids, deg = select_landmarks(dir_adj, n, k=max(64, len(hub_ids) + 16))
    lm_set = set(int(x) for x in landmark_ids.tolist())
    hubs_captured = float(np.mean([1.0 if int(hh) in lm_set else 0.0 for hh in hub_ids])) if hub_ids else 0.0

    r_no, _h, _sa, s_no = ft_run_no_cleanup(Z, roles_t, g_start, g_tgt, g_role, device, n)
    r_mem, _h, _sa, s_mem = ft_run_chain_arm(FT_MEMORYLESS, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                             g_start, g_tgt, g_role, device, 256, n)
    r_sup, _h, _sa, s_sup = ft_run_chain_arm(FT_GOAL_WAYPOINT, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                             g_start, g_tgt, g_role, device, 256, n)
    r_auto, _h, s_auto, _vg = run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_tgt, g_role,
                                                 device, 256, n, GAMMA, verify=False)
    r_lm, _h, s_lm, ls = run_landmark_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_tgt, g_role,
                                          device, 256, n, GAMMA, landmark_ids, selection="midpoint")

    nocleanup_ran = bool(r_no[1] == r_no[1])
    memoryless_aliased = bool(r_mem[1] == r_mem[1] and r_mem[1] < 0.70)          # goal-blind underdetermined (~1/k)
    supplied_reaches = bool(r_sup[2] == r_sup[2] and r_sup[2] >= 0.45)           # waypoint supervision >> ~0 floor
    greedy_fails = bool(r_auto[2] == r_auto[2] and r_sup[2] == r_sup[2]
                        and r_auto[2] <= 0.70 * r_sup[2])                        # plain-greedy short of ceiling
    hubs_are_landmarks = bool(hubs_captured >= 0.80)                            # degree-proxy captured the hubs
    landmark_recovers = bool(r_lm[2] == r_lm[2] and r_sup[2] == r_sup[2]
                             and r_sup[2] > 1e-9 and r_lm[2] >= 0.70 * r_sup[2])  # ~matches supplied (pos ctrl)
    landmark_beats_greedy = bool(r_lm[2] == r_lm[2] and r_auto[2] == r_auto[2]
                                 and r_lm[2] >= r_auto[2] + 0.15)               # the whole point: lm >> greedy
    arms_differ = bool(len({s_no, s_mem, s_sup, s_auto, s_lm}) >= 4)

    res = dict(
        reach_no_cleanup={dd: round(r_no[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_memoryless={dd: round(r_mem[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_supplied={dd: round(r_sup[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_autonomous_greedy={dd: round(r_auto[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_landmark_seeded={dd: round(r_lm[dd], 4) for dd in range(1, MAX_REACH + 1)},
        landmark_stats=ls, hubs_captured=hubs_captured, n_hubs=len(hub_ids),
        nocleanup_ran=nocleanup_ran, memoryless_aliased=memoryless_aliased, supplied_reaches=supplied_reaches,
        greedy_fails=greedy_fails, hubs_are_landmarks=hubs_are_landmarks, landmark_recovers=landmark_recovers,
        landmark_beats_greedy=landmark_beats_greedy, arms_differ=arms_differ, Dmax=int(Dmax), n_synth=int(n),
    )
    ok = bool(nocleanup_ran and memoryless_aliased and supplied_reaches and greedy_fails
              and hubs_are_landmarks and landmark_recovers and landmark_beats_greedy and arms_differ)
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
    landmark_ids, deg = select_landmarks(dir_adj, n_nodes, cfg["n_landmarks"])
    _log("nbr table: Dmax=%d mean_out_deg=%.3f | landmarks K=%d (max_deg=%d median_deg=%.1f)"
         % (Dmax, mean_out_deg, len(landmark_ids), int(deg.max()), float(np.median(deg[deg > 0]))))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS landmark-routing machinery: NO_CLEANUP collapses; MEMORYLESS aliased; "
                        "SUPPLIED recovers; plain-greedy FAILS on pre-hub nodes; LANDMARK_SEEDED recovers "
                        "~SUPPLIED and >> greedy on a clean-hub planted graph; hubs captured as landmarks; "
                        "arms differ; typed subgraph + nbr table + k_sr + landmark select exercised",
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
                          nbr_idx, nbr_rel, nbr_mask, mean_out_deg, landmark_ids, T, cfg, device,
                          out_dir=out_dir_path)
            for a in ALL_ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1)
                           if a not in pm["arms"] or dd not in pm["arms"][a]["reach"]]
                if missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            # arms must differ (META_RULE_AF)
            if pm["arm_sigs"][LANDMARK_SEEDED] == pm["arm_sigs"][AUTONOMOUS_GREEDY]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d LANDMARK_SEEDED == AUTONOMOUS_GREEDY" % seed)
            if pm["arm_sigs"][LANDMARK_SEEDED] == pm["arm_sigs"][SUPPLIED_WAYPOINT]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d LANDMARK_SEEDED == SUPPLIED" % seed)
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
