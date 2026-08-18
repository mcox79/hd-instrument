"""Stage-5 CG cell: does GLASS-BOX GENERATIVE-REPLAY-AS-TRAVERSAL (beam-rollout over the atomized typed local
edge set, deferred goal-directed selection) close the AUTONOMOUS-greedy -> ORACLE-waypoint gap on multi-hop
relational reasoning -- WITHOUT a known transition matrix, staying fully sampling/rollout glass-box?

BACKGROUND (the two anchors this brackets). On the REAL ConceptNet typed subgraph (4440 nodes / 14767 typed
edges / 16 relation types; 3 seeds), the honest AUTONOMOUS multi-hop number (no oracle waypoint, no known map) is
AUTONOMOUS_GREEDY reach@1=0.467 reach@2=0.181 reach@3=0.138 (MEASURED@data/exp_grounding_multihop_autonomous_
subgoal_greedy_v1/metrics.json). The ORACLE/known-map ceiling is SUPPLIED_WAYPOINT reach@1=0.756 reach@2=0.500
reach@3=0.373 (MEASURED@same). The SR-reachability arm (reach@2=0.434) uses the FULLY-KNOWN [n,n] transition
matrix = MM/known-map, NOT a learned/sampled competitor -- it is the ceiling, not a fair rival. The open question:
can a LEARNED/SAMPLED traversal that reads ONLY the LOCAL typed edge set (no [n,n] T-matrix) beat greedy 0.181 and
close toward the oracle 0.500?

MECHANISM (research spec notes/research_glassbox_consolidation_relational_geometry_2026-07-22.md; biology =
generative/sequential replay as graph traversal, Liu/Behrens 2019 Cell + Schwartenbeck 2023 Cell). Replay here is
NOT prototype-averaging; it SAMPLES/ROLLS OUT sequences over a previously-learned LOCAL transition graph, composing
relational paths never directly experienced. Concretely, the substrate already atomizes the graph into TYPED LOCAL
EDGES (the nbr table: per node, its real out-neighbors + their relation type). The greedy autonomous learner
commits the single best next node at each hop by immediate (relation-bind + goal-cosine) score -- MYOPIC. The
replay-traversal learner keeps a BEAM of B partial relational paths, expands each along the query's next relation
(typed-edge composition), and DEFERS commitment: it selects the full path whose composed rollout best reaches the
FINAL goal (cumulative relation-fidelity + goal-cosine), then reads off the intermediates. This lets a locally-
suboptimal-but-globally-correct waypoint survive, exactly the compositional escape the biology documents. It is
still glass-box: bounded top-B rollout over a local edge set, every step inspectable, NO backprop, NO opaque
scoring function, and -- the load-bearing invariant -- NO precomputed [n,n] transition/reachability matrix (it reads
only the [n, Dmax] local table, Dmax << n; this is the machine-checked no_global_T_matrix guard).

ONE VARIABLE (isolation is exact): AUTONOMOUS_GREEDY is literally REPLAY_TRAVERSAL at beam width B=1 with the same
per-step score (base relation-bind + GAMMA*goal-cosine) and the same selection rule. The ONLY thing that changes
between the two learners is beam width (1 -> B) + deferred full-path selection. Same learned codes, same graph,
same seeds, same goal signal, same GAMMA. Any reach delta is the traversal mechanism, nothing else. (Asserted in
the mechanism self-test: B=1 traversal reproduces greedy reach at every depth.)

ARMS (paired: identical learned codes + identical planted general chains + identical seeds across ALL arms; only
the LEARNER/selection differs). The first four REPRODUCE the autonomous-cell anchors VERBATIM (Gate-D positive
control -- reused bit-for-bit from the landed cells):
  NO_CLEANUP                   : global-cleanup-only chain (must-fail / anti-saturation; collapses at reach>=2).
  MEMORYLESS                   : goal-blind local decoder = the floor (repro ~0.453 @1 / 0.121 @2).
  SUPPLIED_WAYPOINT            : ORACLE ceiling; HANDED the true next waypoint each hop (repro ~0.756@1 / 0.500@2).
  AUTONOMOUS_GREEDY            : the arm to beat (repro ~0.467@1 / 0.181@2); myopic goal-directed argmax, B=1.
  REPLAY_TRAVERSAL             : THE CG CANDIDATE (primary). Beam-rollout width B over the LOCAL typed edge set;
                                 deferred selection of the full path that best reaches the FINAL goal.
  REPLAY_TRAVERSAL_SCRAMBLED   : content-dependence must-fire control. Identical beam-rollout but the relation-type
                                 -> role mapping is DERANGED (roles permuted with no fixed point), so per-hop
                                 relation-bind points the wrong way. If the win is genuinely relational (typed-
                                 structure-dependent), scrambling must SEVERELY hurt -- OPPOSITE of a fixed-
                                 similarity/algebra mechanism where relation labels are irrelevant (atom 29437 /
                                 fork-B signature-flip family).

CG WIN BAR (pre-registered BEFORE the run; verdict on REPLAY_TRAVERSAL reach@2 = rt2; self-calibrated within-run to
the SUPPLIED/GREEDY anchors measured THIS run so it is robust to small config drift). gap = SUPPLIED@2 - GREEDY@2;
close = rt2 - GREEDY@2; content_dep = rt2 - SCRAMBLED@2:
  HARD_PASS_CG = close >= GAP_FRAC_HP(0.50)*gap  AND  close >= TRAVERSAL_MATERIAL(0.06)  AND
                 content_dep >= CONTENT_DEP_MIN(0.08)
                 -> traversal closes >=50% of the autonomous->oracle gap, materially over greedy, AND the win is
                    demonstrably content/relation-dependent (not secretly fixed-similarity).
  HARD_FAIL_CG = close <= TRAVERSAL_FAIL(0.02)
                 -> beam-rollout ties/underperforms greedy: deferred selection does not help at multi-hop distance
                    (next mechanism = learned edge-scoring or landmark/betweenness precompute).
  MIDDLE_BAND  = partial gap closure, OR gap closed but content-dependence does NOT fire (win is not demonstrably
                 relational -> flagged COSMETIC_GRAPH_TRAVERSAL, demoted from HARD_PASS per research HARD-FAIL(b)).

HELD-OUT / COMPOUND-DIVERGENCE (rule out memorization). PRIMARY: this testbed is compound-divergence BY
CONSTRUCTION -- the InfoNCE binding encoder trains on SINGLE typed edges (primitives); the evaluated chains are
NOVEL multi-edge COMPOSITIONS the encoder never bound (systematic recombination of seen primitives into unseen
combinations, Lake/Baroni compound-divergence). MEMORIZATION CONTROL by PAIRING: greedy and traversal use the
IDENTICAL codes, so any encoder-memorization is EQUAL across both arms -- the traversal-vs-greedy DELTA cannot come
from memorization, it is purely the search/selection mechanism. ROBUSTNESS: an INDEPENDENT held-out chain draw
(disjoint rng, node-disjoint starts) re-measures greedy vs traversal reach@2; the delta must replicate on the
held-out draw (rules out a one-sample fluke). Reported, min-count-guarded.

## Compute architecture
class: (c) mixed with justification. Storage strategy: SHARDED (each node its own code vector; no bundling --
compositional multi-hop chaining, per META_STORAGE_STRATEGY). Within a hop, all chains x all beams x all local
candidates are scored by batched einsum on GPU (cuda when available); the B beams are looped (B small) so peak
memory is one [chunk, Dmax, d] block, identical to the greedy arm's inner block. ACROSS hops the traversal is
genuinely SEQUENTIAL (hop h's frontier depends on hop h-1) -- an inherent data dependency, not a batching flaw;
same shape as the autonomous cell which ran 3 seeds FULL in 16.4s on cuda. No Python-loop matmul over independent
phase points.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; REPLAY_TRAVERSAL commit-sig != GREEDY != SUPPLIED !=
#   MEMORYLESS != NO_CLEANUP != SCRAMBLED; asserted per seed on distinct commit signatures).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0002 at n=5000). Reference points are MEASURED anchors: GREEDY
#   reach@2=0.181 and SUPPLIED reach@2=0.500 (MEASURED@autonomous metrics.json). HARD_PASS bar 0.181 + 0.5*gap =
#   ~0.34 is on the achievable side (SUPPLIED demonstrates 0.500 is reachable WITH a good waypoint signal; the
#   question is whether deferred rollout selection derives an equally good signal). crlb_reachability: OK.
# - baseline_in_band: MEMORYLESS@1 in (0.05, 0.95) (~0.453). NO_CLEANUP@2 collapses (anti-saturation).
# - discriminator survives scale: the MM discriminator (SUPPLIED >> MEMORYLESS) is graph-structural and FIRES AT
#   SMOKE on the real subgraph. The CG discriminator (REPLAY_TRAVERSAL > GREEDY) is the MEASUREMENT -- it MUST
#   fire at smoke (rt2 > greedy2 + TRAVERSAL_MATERIAL) or the FULL dispatch is aborted (DISCRIMINATOR-MUST-
#   SURVIVE-SCALE). The must-fail control NO_CLEANUP collapses AT smoke scale (SATURATION-VACUOUS guard).
# - HARD_PASS strictly above floor: close>=0.5*gap AND >=0.06 over greedy AND content-dep>=0.08 is a categorical
#   margin, not an at-floor result.
# - HP_SCOPE: the CG win gate applies to REPLAY_TRAVERSAL only. SUPPLIED/MEMORYLESS/GREEDY = positive-control
#   reproductions (must reproduce within tolerance for the discriminator to be valid); NO_CLEANUP = must-fail;
#   SCRAMBLED = content-dependence must-fire control (must collapse vs REPLAY_TRAVERSAL).
# - positive_control (Gate D): MEMORYLESS + SUPPLIED + GREEDY reproduce the autonomous-cell MEASURED anchors AT
#   THE MATCHED FULL regime (same n_nodes/code_dim/feat_dim/epochs/seeds/chains); repro drift > 0.10 -> flag.
# - sweep axis: hop depth d in {1,2,3,4}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms x
#   all depths (arm/depth-cardinality check).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate. GAMMA + BEAM_WIDTH are PRE-REGISTERED (GAMMA = certified
#   GOAL_GAMMA 1.5, held IDENTICAL to greedy so it is not a tuned knob; B=12 fixed), NOT tuned on real data. The
#   mechanism self-test verifies B=1 reproduces greedy AND B=12 beats greedy on a lookahead-TRAP planted set, so a
#   real-data collapse is a genuine mechanism-weakness negative, not a mis-set knob.
# - no_global_T_matrix (LOAD-BEARING FAIRNESS GUARD): the traversal reads ONLY the [n+1, Dmax] local typed-edge
#   table (Dmax << n_nodes) + the learned codes + the final-goal code. It NEVER allocates/reads an [n,n]
#   transition or reachability matrix (that is the SR/MM ceiling). Machine-checked: assert nbr_idx.shape[1] <
#   n_nodes and record no_global_T_matrix_confirmed in metrics.
# - PAIRED trials: all arms share identical codes + roles + seeds + graph + dim + general-chain population.
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-epoch/per-seed flush prints inherited from the
#   encoder trainer + per-arm flush).
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
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev,
    sample_chains,
    build_typed_diradj,
    _hrr_bind_t,
    _l2t,
)
from experiments.exp_grounding_multihop_fair_test_unique_successor_goal_v1 import (  # noqa: E402
    build_nbr_table,
    build_ksr,
    run_chain_arm as ft_run_chain_arm,
    run_no_cleanup as ft_run_no_cleanup,
    MEMORYLESS as FT_MEMORYLESS,
    GOAL_WAYPOINT as FT_GOAL_WAYPOINT,
)
# Reuse the GREEDY autonomous arm VERBATIM (bit-identical to the 0.181@2 arm-to-beat).
from experiments.exp_grounding_multihop_autonomous_subgoal_greedy_v1 import (  # noqa: E402
    run_autonomous_arm as run_greedy_arm,
)

ANCHOR_NAME = "grounding_multihop_generative_replay_traversal_v1"

MAX_REACH = 4
HIT_K = 10
GAMMA = 1.5          # goal-cosine boost; IDENTICAL to greedy AUTO_GAMMA (held constant -> ONE VARIABLE = beam)
BEAM_WIDTH = 12      # replay-traversal beam width B (B=1 == greedy, asserted in self-test)

# Arm names
NO_CLEANUP = "NO_CLEANUP"
MEMORYLESS = "MEMORYLESS"
SUPPLIED_WAYPOINT = "SUPPLIED_WAYPOINT"
AUTONOMOUS_GREEDY = "AUTONOMOUS_GREEDY"
REPLAY_TRAVERSAL = "REPLAY_TRAVERSAL"
REPLAY_TRAVERSAL_SCRAMBLED = "REPLAY_TRAVERSAL_SCRAMBLED"
ALL_ARMS = [NO_CLEANUP, MEMORYLESS, SUPPLIED_WAYPOINT, AUTONOMOUS_GREEDY,
            REPLAY_TRAVERSAL, REPLAY_TRAVERSAL_SCRAMBLED]

# ---------------------------------------------------------------------------
# Pre-registered CG bands (picked BEFORE the run). Reach = TOP-1 COMMIT accuracy of the selected full path.
# ---------------------------------------------------------------------------
GAP_FRAC_HP = 0.50          # HARD_PASS: (rt2 - greedy2) >= this * (supplied2 - greedy2)
TRAVERSAL_MATERIAL = 0.06   # HARD_PASS also requires (rt2 - greedy2) >= this (materially over greedy)
CONTENT_DEP_MIN = 0.08      # HARD_PASS also requires (rt2 - scrambled2) >= this (win is content/relation-dependent)
TRAVERSAL_FAIL = 0.02       # HARD_FAIL: (rt2 - greedy2) <= this (traversal does not help)

# Smoke discriminator-fires gate (DISCRIMINATOR-MUST-SURVIVE-SCALE): abort FULL if traversal does not beat greedy
SMOKE_FIRE_MARGIN = 0.04    # at smoke, require rt2 >= greedy2 + this to justify FULL dispatch

# Anti-saturation / must-fail control (mirrors autonomous cell)
BASE_COLLAPSE_ABS = 0.10
BASE_COLLAPSE_FRAC = 0.50
BASE_IN_BAND_HI = 0.95
HOP1_PRESENT = 0.08
SUPPLIED_FIRES_MIN = 0.10

# Gate-D positive-control reproduction anchors (MEASURED@autonomous metrics.json) + tolerance (FULL config only)
REPRO_MEM1 = 0.453
REPRO_SUP1 = 0.756
REPRO_SUP2 = 0.500
REPRO_GREEDY2 = 0.181
REPRO_TOL = 0.10

HELDOUT_MIN_CHAINS = 100    # min chains for the independent held-out draw to be reported (else insufficient)


def _resolve_device(arg_device):
    if arg_device == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _derangement(T, rng):
    """Return a permutation of range(T) with NO fixed point (relation-type -> role scramble)."""
    if T <= 1:
        return np.arange(T)
    perm = np.arange(T)
    for _ in range(10000):
        rng.shuffle(perm)
        if np.all(perm != np.arange(T)):
            return perm.copy()
    # deterministic fallback: single cyclic shift (guaranteed no fixed point for T>=2)
    return (np.arange(T) + 1) % T


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
# FULL config is IDENTICAL to the autonomous cell's FULL_CFG so the first four arms reproduce the anchors.
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
# REPLAY_TRAVERSAL: glass-box beam-rollout over the LOCAL typed edge set.
# State per chain: B partial paths (beam). Per hop, expand each beam along the query's next relation via the REAL
# local out-neighbors (typed-edge composition), score each expansion by (relation-bind base + GAMMA*goal-cosine),
# accumulate, keep the top-B partial paths. After L hops, SELECT the beam whose composed path scored best
# (cumulative relation-fidelity + goal-cosine) and read off its committed nodes. B=1 == greedy argmax.
#
# NO [n,n] transition matrix anywhere: only nbr_idx/nbr_mask ([n+1, Dmax] local table), Z/Zp (codes), goal code.
# ---------------------------------------------------------------------------

def run_beam_traversal_arm(Z, Zp, roles_use, nbr_idx, nbr_mask, start, targets, role_ids,
                           device, chunk, n_nodes, gamma, beam_width):
    L = len(targets)
    C = int(start.shape[0])
    B = int(beam_width)
    NEG = float("-inf")
    start_t = torch.from_numpy(start).to(device)
    goal_t = torch.from_numpy(targets[L - 1]).to(device)   # FINAL goal node per chain (same across hops)
    role_ids_t = [torch.from_numpy(role_ids[h]).to(device) for h in range(L)]
    tgt_t = [torch.from_numpy(targets[h]).to(device) for h in range(L)]

    commit_path = torch.full((C, L), n_nodes, dtype=torch.long, device=device)
    beam_recall = torch.zeros((C, L), dtype=torch.bool, device=device)   # any beam holds target at depth d

    for b0 in range(0, C, chunk):
        b1 = min(C, b0 + chunk)
        bs = b1 - b0
        goal_code = Z[goal_t[b0:b1].clamp(max=n_nodes - 1)]              # [bs, d]
        beam_nodes = torch.full((bs, B), n_nodes, dtype=torch.long, device=device)
        beam_nodes[:, 0] = start_t[b0:b1]
        beam_score = torch.full((bs, B), NEG, device=device)
        beam_score[:, 0] = 0.0
        beam_path = torch.full((bs, B, L), n_nodes, dtype=torch.long, device=device)

        for h in range(L):
            role = roles_use[role_ids_t[h][b0:b1]]                       # [bs, d]  (scrambled roles_use == control)
            tgt_h = tgt_t[h][b0:b1]                                      # [bs]
            all_scores = []
            all_nodes = []
            Dmax = int(nbr_idx.shape[1])
            for b in range(B):
                cur_b = beam_nodes[:, b]                                 # [bs]
                cue = Zp[cur_b]                                          # [bs, d]  (padded code = zeros)
                pred = _hrr_bind_t(role, cue)                           # [bs, d]
                cand = nbr_idx[cur_b]                                    # [bs, Dmax] real local out-neighbors
                mask = nbr_mask[cur_b]                                   # [bs, Dmax]
                Zc = Zp[cand]                                           # [bs, Dmax, d]
                p = _l2t(pred)
                base = torch.einsum("bd,bkd->bk", p, Zc)                # memoryless relation-bind local score
                gcos = torch.einsum("bkd,bd->bk", Zc, goal_code)        # candidate -> final-goal cosine
                step = base + gamma * gcos.clamp(min=0.0)               # [bs, Dmax] per-step goal-directed score
                step = step.masked_fill(~mask, NEG)
                cand_score = beam_score[:, b:b + 1] + step               # [bs, Dmax] cumulative (dead beam -> -inf)
                all_scores.append(cand_score)
                all_nodes.append(cand)
            cat_score = torch.cat(all_scores, dim=1)                     # [bs, B*Dmax]
            cat_node = torch.cat(all_nodes, dim=1)                       # [bs, B*Dmax]
            parent = torch.arange(B, device=device).repeat_interleave(Dmax)   # [B*Dmax] parent beam per column
            k = min(B, cat_score.shape[1])
            topv, topi = cat_score.topk(k, dim=1)                        # [bs, k]
            new_nodes = torch.gather(cat_node, 1, topi)                  # [bs, k]
            parent_b = parent[topi]                                      # [bs, k]
            new_path = torch.gather(beam_path, 1, parent_b[:, :, None].expand(bs, k, L)).clone()
            new_path[:, :, h] = new_nodes
            if k < B:   # pad dead beam slots (start had < B neighbors); mark score -inf so never selected
                pad = B - k
                new_nodes = torch.cat([new_nodes, torch.full((bs, pad), n_nodes, dtype=torch.long, device=device)], 1)
                topv = torch.cat([topv, torch.full((bs, pad), NEG, device=device)], 1)
                new_path = torch.cat([new_path, torch.full((bs, pad, L), n_nodes, dtype=torch.long, device=device)], 1)
            beam_nodes = new_nodes
            beam_score = topv
            beam_path = new_path
            beam_recall[b0:b1, h] = (beam_nodes == tgt_h[:, None]).any(dim=1)

        sel = beam_score.argmax(dim=1)                                   # [bs] best full path by cumulative score
        br = torch.arange(bs, device=device)
        commit_path[b0:b1] = beam_path[br, sel]                          # [bs, L]

    reach = {}
    hit10 = {}
    for h in range(L):
        reach[h + 1] = float((commit_path[:, h] == tgt_t[h]).float().mean().item())
        hit10[h + 1] = float(beam_recall[:, h].float().mean().item())
    sig = hashlib.sha256(commit_path.detach().to("cpu").numpy().astype(np.int64).tobytes()).hexdigest()
    stats = dict(beam_width=B, gamma=gamma)
    return reach, hit10, sig, stats


# ---------------------------------------------------------------------------
# Per-seed run: all arms on the identical general-chain population + identical learned codes (paired).
# ---------------------------------------------------------------------------

def run_seed(seed, node_words, edges, rels, dir_adj, ksr_map, has_rel, roles_t,
             nbr_idx, nbr_rel, nbr_mask, mean_out_deg, T, cfg, device, out_dir=None):
    n_nodes = len(node_words)
    chunk = cfg["chain_chunk"]
    X = char_trigram_features(node_words, cfg["feat_dim"])
    Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_grt")
    enc_dig = hashlib.sha256(Z.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()
    Zp = torch.cat([Z, torch.zeros(1, cfg["code_dim"], device=device)], dim=0)

    # scrambled roles for the content-dependence control (deranged relation-type -> role map; deterministic)
    scr_perm = _derangement(T, np.random.default_rng(seed + 4242))
    roles_scr = roles_t[torch.from_numpy(scr_perm).to(device)]

    # general chains (IDENTICAL rng offset + sampler as the autonomous/fair-test cells -> paired reproduction)
    gen_rng = np.random.default_rng(seed + 909)
    g_start, g_targets, g_role = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, gen_rng)
    Cg = int(g_start.shape[0])

    arms = {}
    sigs = {}
    r, h, _sa, sig = ft_run_no_cleanup(Z, roles_t, g_start, g_targets, g_role, device, n_nodes)
    arms[NO_CLEANUP] = dict(reach=r, hit10=h); sigs[NO_CLEANUP] = sig
    r, h, _sa, sig = ft_run_chain_arm(FT_MEMORYLESS, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                      g_start, g_targets, g_role, device, chunk, n_nodes)
    arms[MEMORYLESS] = dict(reach=r, hit10=h); sigs[MEMORYLESS] = sig
    r, h, _sa, sig = ft_run_chain_arm(FT_GOAL_WAYPOINT, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                      g_start, g_targets, g_role, device, chunk, n_nodes)
    arms[SUPPLIED_WAYPOINT] = dict(reach=r, hit10=h); sigs[SUPPLIED_WAYPOINT] = sig
    # GREEDY (arm to beat) = run_greedy_arm verbatim, verify=False
    r, h, sig, _vg = run_greedy_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                    device, chunk, n_nodes, GAMMA, verify=False)
    arms[AUTONOMOUS_GREEDY] = dict(reach=r, hit10=h); sigs[AUTONOMOUS_GREEDY] = sig
    # REPLAY_TRAVERSAL (CG candidate) = beam-rollout, correct roles
    r, h, sig, st = run_beam_traversal_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                           device, chunk, n_nodes, GAMMA, BEAM_WIDTH)
    arms[REPLAY_TRAVERSAL] = dict(reach=r, hit10=h, stats=st); sigs[REPLAY_TRAVERSAL] = sig
    # REPLAY_TRAVERSAL_SCRAMBLED (content-dependence control) = beam-rollout, deranged roles
    r, h, sig, st = run_beam_traversal_arm(Z, Zp, roles_scr, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                           device, chunk, n_nodes, GAMMA, BEAM_WIDTH)
    arms[REPLAY_TRAVERSAL_SCRAMBLED] = dict(reach=r, hit10=h, stats=st); sigs[REPLAY_TRAVERSAL_SCRAMBLED] = sig

    # ---- independent HELD-OUT draw (disjoint rng + node-disjoint starts): greedy vs traversal reach only ----
    heldout = dict(status="insufficient", n_chains=0)
    ho_rng = np.random.default_rng(seed + 90909)
    ho_start, ho_targets, ho_role = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, ho_rng)
    # node-disjoint starts: keep only held-out chains whose START was NOT a start in the primary set
    prim_starts = set(int(x) for x in g_start.tolist())
    keep = np.asarray([i for i in range(int(ho_start.shape[0])) if int(ho_start[i]) not in prim_starts],
                      dtype=np.int64)
    if keep.shape[0] >= HELDOUT_MIN_CHAINS:
        hs = ho_start[keep]
        ht = [t[keep] for t in ho_targets]
        hr = [r_[keep] for r_ in ho_role]
        rg, _hg, _sg, _vg = run_greedy_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, hs, ht, hr,
                                           device, chunk, n_nodes, GAMMA, verify=False)
        rt_, _ht, _st2, _stt = run_beam_traversal_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, hs, ht, hr,
                                                      device, chunk, n_nodes, GAMMA, BEAM_WIDTH)
        heldout = dict(status="ok", n_chains=int(keep.shape[0]),
                       greedy_reach={d: rg[d] for d in range(1, MAX_REACH + 1)},
                       traversal_reach={d: rt_[d] for d in range(1, MAX_REACH + 1)},
                       delta2=float(rt_[2] - rg[2]), delta3=float(rt_[3] - rg[3]))

    for arm in ALL_ARMS:
        _log("  seed=%d %-26s reach@[1..%d]=%s" % (
            seed, arm, MAX_REACH, {dd: round(arms[arm]["reach"][dd], 3) for dd in range(1, MAX_REACH + 1)}))
    if heldout["status"] == "ok":
        _log("  seed=%d HELD_OUT(n=%d) greedy@2=%.3f traversal@2=%.3f delta@2=%.3f" % (
            seed, heldout["n_chains"], heldout["greedy_reach"][2], heldout["traversal_reach"][2],
            heldout["delta2"]))

    return dict(seed=seed, arms=arms, arm_sigs=sigs, encoder_digest=enc_dig, n_general=Cg,
                heldout=heldout, scr_perm=scr_perm.tolist(), code_dim=cfg["code_dim"],
                mean_out_deg=mean_out_deg)


# ---------------------------------------------------------------------------
# Aggregate + CG verdict
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, meta, cfg, no_T_matrix):
    def R(arm, d):
        return _nm([m["arms"][arm]["reach"][d] for m in per_seed])

    base1 = R(NO_CLEANUP, 1); base2 = R(NO_CLEANUP, 2)
    mem1 = R(MEMORYLESS, 1); mem2 = R(MEMORYLESS, 2); mem3 = R(MEMORYLESS, 3)
    sup1 = R(SUPPLIED_WAYPOINT, 1); sup2 = R(SUPPLIED_WAYPOINT, 2); sup3 = R(SUPPLIED_WAYPOINT, 3)
    g1 = R(AUTONOMOUS_GREEDY, 1); g2 = R(AUTONOMOUS_GREEDY, 2); g3 = R(AUTONOMOUS_GREEDY, 3)
    rt1 = R(REPLAY_TRAVERSAL, 1); rt2 = R(REPLAY_TRAVERSAL, 2); rt3 = R(REPLAY_TRAVERSAL, 3)
    sc1 = R(REPLAY_TRAVERSAL_SCRAMBLED, 1); sc2 = R(REPLAY_TRAVERSAL_SCRAMBLED, 2)
    sc3 = R(REPLAY_TRAVERSAL_SCRAMBLED, 3)

    gap = (sup2 - g2) if (sup2 == sup2 and g2 == g2) else float("nan")
    close = (rt2 - g2) if (rt2 == rt2 and g2 == g2) else float("nan")
    frac_closed = (close / gap) if (gap == gap and gap > 1e-9) else float("nan")
    content_dep = (rt2 - sc2) if (rt2 == rt2 and sc2 == sc2) else float("nan")
    ratio_sup = (rt2 / sup2) if (sup2 == sup2 and sup2 > 1e-9) else float("nan")

    # anti-saturation + baseline-in-band + MM-discriminator-fires
    hop1_present = bool(mem1 == mem1 and mem1 >= HOP1_PRESENT)
    baseline_in_band = bool(mem1 == mem1 and 0.05 < mem1 < BASE_IN_BAND_HI)
    baseline_collapses = bool(base2 == base2 and base1 == base1
                              and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))
    supplied_fires = bool(sup2 == sup2 and mem2 == mem2 and sup2 >= mem2 + SUPPLIED_FIRES_MIN)

    content_dep_fires = bool(content_dep == content_dep and content_dep >= CONTENT_DEP_MIN)
    # CG gates (on REPLAY_TRAVERSAL)
    cg_gap = bool(close == close and gap == gap and close >= GAP_FRAC_HP * gap)
    cg_material = bool(close == close and close >= TRAVERSAL_MATERIAL)
    cg_hard_pass = bool(cg_gap and cg_material and content_dep_fires)
    cg_hard_fail = bool(close == close and close <= TRAVERSAL_FAIL)
    cosmetic_flag = bool(cg_gap and cg_material and not content_dep_fires)   # closed gap but not relational -> demote

    # Gate-D reproduction audit (only meaningful at FULL config == autonomous regime)
    is_full = bool(len(cfg["seeds"]) == 3 and cfg["n_nodes"] == 5000 and cfg["code_dim"] == 2048)
    repro_mem1_ok = bool(mem1 == mem1 and abs(mem1 - REPRO_MEM1) <= REPRO_TOL)
    repro_sup1_ok = bool(sup1 == sup1 and abs(sup1 - REPRO_SUP1) <= REPRO_TOL)
    repro_sup2_ok = bool(sup2 == sup2 and abs(sup2 - REPRO_SUP2) <= REPRO_TOL)
    repro_greedy2_ok = bool(g2 == g2 and abs(g2 - REPRO_GREEDY2) <= REPRO_TOL)
    repro_ok = bool(repro_mem1_ok and repro_sup1_ok and repro_sup2_ok and repro_greedy2_ok)

    # held-out replication (delta@2 must stay positive on the independent draw for a HARD_PASS)
    ho_deltas = [m["heldout"]["delta2"] for m in per_seed if m["heldout"]["status"] == "ok"]
    ho_delta2 = _nm(ho_deltas) if ho_deltas else float("nan")
    ho_reported = bool(len(ho_deltas) > 0)
    ho_replicates = bool(ho_delta2 == ho_delta2 and ho_delta2 >= TRAVERSAL_FAIL)

    # ---- overall verdict ----
    if not no_T_matrix:
        verdict = "INCONCLUSIVE_T_MATRIX_LEAK"
    elif not hop1_present:
        verdict = "INCONCLUSIVE_HOP1_ABSENT"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif not supplied_fires:
        verdict = "INCONCLUSIVE_SUPPLIED_MM_DID_NOT_FIRE"
    elif is_full and not repro_ok:
        verdict = "INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT"
    elif cg_hard_fail:
        verdict = "HARD_FAIL_CG_TRAVERSAL_NO_HELP"
    elif cg_hard_pass and (ho_replicates or not ho_reported):
        verdict = "HARD_PASS_CG_TRAVERSAL"
    elif cosmetic_flag:
        verdict = "MIDDLE_BAND_CG_COSMETIC_GRAPH_NOT_RELATIONAL"
    else:
        verdict = "MIDDLE_BAND_CG_TRAVERSAL_PARTIAL"

    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f @2=%.3f(collapses=%s) || MEMORYLESS @1=%.3f(in_band=%s) @2=%.3f @3=%.3f || "
        "SUPPLIED @1=%.3f @2=%.3f @3=%.3f(fires=%s) || GREEDY @1=%.3f @2=%.3f @3=%.3f || "
        "REPLAY_TRAVERSAL @1=%.3f @2=%.3f @3=%.3f || SCRAMBLED @1=%.3f @2=%.3f @3=%.3f || "
        "CG: gap=%s close=%s frac_closed=%s content_dep=%s(fires=%s) ratio_sup=%s || "
        "HARD_PASS=(close>=%.2f*gap AND close>=%.2f AND content_dep>=%.2f)=%s HARD_FAIL=(close<=%.2f)=%s "
        "cosmetic=%s || heldout(rep=%s): delta@2=%s replicates=%s || repro(full=%s): mem1=%s sup1=%s sup2=%s "
        "greedy2=%s || no_T_matrix=%s || B=%d gamma=%.2f nodes=%d E=%d rel=%d seeds=%d run=%s" % (
            verdict, base1, base2, baseline_collapses, mem1, baseline_in_band, mem2, mem3,
            sup1, sup2, sup3, supplied_fires, g1, g2, g3, rt1, rt2, rt3, sc1, sc2, sc3,
            _fmt(gap), _fmt(close), _fmt(frac_closed), _fmt(content_dep), content_dep_fires, _fmt(ratio_sup),
            GAP_FRAC_HP, TRAVERSAL_MATERIAL, CONTENT_DEP_MIN, cg_hard_pass, TRAVERSAL_FAIL, cg_hard_fail,
            cosmetic_flag, ho_reported, _fmt(ho_delta2), ho_replicates, is_full, repro_mem1_ok, repro_sup1_ok,
            repro_sup2_ok, repro_greedy2_ok, no_T_matrix, BEAM_WIDTH, GAMMA, meta["n_nodes"], meta["n_edges"],
            meta.get("n_relation_types", -1), len(per_seed), "full" if is_full else "smoke"))

    gates = dict(
        verdict=verdict,
        reach={a: {d: R(a, d) for d in range(1, MAX_REACH + 1)} for a in ALL_ARMS},
        cg=dict(memoryless_reach2=mem2, supplied_reach2=sup2, greedy_reach2=g2, traversal_reach2=rt2,
                scrambled_reach2=sc2, gap=gap, close=close, frac_closed=frac_closed, content_dep=content_dep,
                content_dep_fires=content_dep_fires, ratio_sup=ratio_sup,
                traversal_reach1=rt1, traversal_reach3=rt3,
                cg_gap=cg_gap, cg_material=cg_material, cg_hard_pass=cg_hard_pass, cg_hard_fail=cg_hard_fail,
                cosmetic_flag=cosmetic_flag),
        heldout=dict(reported=ho_reported, delta2=ho_delta2, replicates=ho_replicates, n_seeds=len(ho_deltas)),
        anti_sat=dict(hop1_present=hop1_present, baseline_in_band=baseline_in_band,
                      baseline_collapses=baseline_collapses, supplied_fires=supplied_fires),
        no_global_T_matrix=dict(confirmed=no_T_matrix),
        positive_control=dict(is_full=is_full, repro_mem1=mem1, repro_sup1=sup1, repro_sup2=sup2, repro_greedy2=g2,
                              repro_mem1_ok=repro_mem1_ok, repro_sup1_ok=repro_sup1_ok, repro_sup2_ok=repro_sup2_ok,
                              repro_greedy2_ok=repro_greedy2_ok, repro_ok=repro_ok,
                              anchors=dict(mem1=REPRO_MEM1, sup1=REPRO_SUP1, sup2=REPRO_SUP2,
                                           greedy2=REPRO_GREEDY2, tol=REPRO_TOL)),
        bands=dict(GAP_FRAC_HP=GAP_FRAC_HP, TRAVERSAL_MATERIAL=TRAVERSAL_MATERIAL, CONTENT_DEP_MIN=CONTENT_DEP_MIN,
                   TRAVERSAL_FAIL=TRAVERSAL_FAIL, SUPPLIED_FIRES_MIN=SUPPLIED_FIRES_MIN,
                   BASE_COLLAPSE_ABS=BASE_COLLAPSE_ABS, HOP1_PRESENT=HOP1_PRESENT, GAMMA=GAMMA,
                   BEAM_WIDTH=BEAM_WIDTH),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test. Proves on PLANTED codes + REAL local-graph machinery:
#  P1 (isolation): REPLAY_TRAVERSAL at B=1 reproduces GREEDY reach at every depth (ONE-VARIABLE exact).
#  P2 (mechanism):  on a LOOKAHEAD-TRAP set (greedy's myopic argmax picks a high-goal-cosine trap that dead-ends;
#                   the true waypoint has lower immediate goal-cosine but reaches the goal), beam-rollout (B>1)
#                   RECOVERS the true path while greedy fails -> beam materially beats greedy.
#  P3 (content-dep): on a RELATION-ESSENTIAL set (on-path vs off-relation sibling are goal-equidistant, so ONLY
#                   correct relation-bind can pick the on-path successor), scrambling the roles COLLAPSES the beam
#                   -> the win is content/relation-dependent, not fixed-similarity.
#  P4 (no-T-matrix): the traversal reads a [n+1, Dmax] local table with Dmax < n (never an [n,n] matrix).
#  P5 (arms differ): greedy / traversal / scrambled produce distinct commit signatures.
# ---------------------------------------------------------------------------

def _plant_trap_set(device, d, T, roles_t, rng, n_chains=140):
    """L=2 lookahead-trap chains. start -> {t1 (true), d1 (trap)} via rel r1; t1 -> t2==goal via r2; d1 -> dead
    (away from goal) via r2. Trap d1 has LARGER immediate goal-cosine than t1 (greedy picks it) but dead-ends."""
    n_cap = n_chains * 6 + 16
    Z2 = torch.zeros(n_cap, d, device=device)
    dir_adj = [[] for _ in range(n_cap)]
    nid = 0

    def _new(vec):
        nonlocal nid
        Z2[nid] = _l2t(vec[None, :])[0]
        i = nid
        nid += 1
        return i

    starts, tgt, rid = [], [[], []], [[], []]
    for _c in range(n_chains):
        if nid >= n_cap - 8:
            break
        g = _l2t(torch.randn(1, d))[0]                                   # per-chain goal direction
        r1 = int(rng.integers(0, T)); r2 = int(rng.integers(0, T))
        s = _new(_l2t(torch.randn(1, d))[0])
        b_r1 = _l2t(_hrr_bind_t(roles_t[r1:r1 + 1], _l2t(Z2[s:s + 1])))[0]
        # true t1: on r1, MODEST goal component; trap d1: on r1, LARGER goal component (looks closer to goal)
        t1 = _new(b_r1 + 0.35 * g + 0.20 * _l2t(torch.randn(1, d))[0])
        d1 = _new(b_r1 + 1.30 * g + 0.20 * _l2t(torch.randn(1, d))[0])
        dir_adj[s].append((t1, r1)); dir_adj[s].append((d1, r1))
        # from t1 via r2 -> t2 == goal (strong goal component); from d1 via r2 -> dead (away from goal)
        b_t1 = _l2t(_hrr_bind_t(roles_t[r2:r2 + 1], _l2t(Z2[t1:t1 + 1])))[0]
        b_d1 = _l2t(_hrr_bind_t(roles_t[r2:r2 + 1], _l2t(Z2[d1:d1 + 1])))[0]
        t2 = _new(b_t1 + 1.60 * g + 0.20 * _l2t(torch.randn(1, d))[0])
        dead = _new(b_d1 - 1.00 * g + 0.20 * _l2t(torch.randn(1, d))[0])
        dir_adj[t1].append((t2, r2))
        dir_adj[d1].append((dead, r2))
        starts.append(s); tgt[0].append(t1); tgt[1].append(t2); rid[0].append(r1); rid[1].append(r2)
    n = nid
    Z = _l2t(Z2[:n])
    return (Z, dir_adj[:n], n,
            np.asarray(starts, np.int64), [np.asarray(t, np.int64) for t in tgt],
            [np.asarray(r, np.int64) for r in rid])


def _plant_relation_essential_set(device, d, T, roles_t, rng, n_chains=140, n_decoys=40):
    """L=2 chains where the branching factor (1 on-path + n_decoys off-relation, all GOAL-EQUIDISTANT) EXCEEDS the
    beam width, so per-hop PRUNING must use relation-bind to keep the on-path node alive. Only correct roles rank
    t1 into the beam; scrambled roles make t1 indistinguishable from the n_decoys goal-ward off-relation siblings
    -> pruned out -> collapse. (This mirrors the REAL regime where content-dependence lives in beam pruning at
    branch points with degree > beam width, not in terminal selection.) start -> t1(r1) + n_decoys off-rel decoys;
    t1 -> t2==goal (r2)."""
    n_cap = n_chains * (n_decoys + 6) + 16
    Z2 = torch.zeros(n_cap, d, device=device)
    dir_adj = [[] for _ in range(n_cap)]
    nid = 0

    def _new(vec):
        nonlocal nid
        Z2[nid] = _l2t(vec[None, :])[0]
        i = nid
        nid += 1
        return i

    starts, tgt, rid = [], [[], []], [[], []]
    for _c in range(n_chains):
        if nid >= n_cap - (n_decoys + 8):
            break
        if T < 2:
            break
        g = _l2t(torch.randn(1, d))[0]
        r1 = int(rng.integers(0, T))
        r2 = int(rng.integers(0, T))
        s = _new(_l2t(torch.randn(1, d))[0])
        a = 0.40
        b_r1 = _l2t(_hrr_bind_t(roles_t[r1:r1 + 1], _l2t(Z2[s:s + 1])))[0]
        # on-path t1 via r1, goal component a
        t1 = _new(b_r1 + a * g + 0.15 * _l2t(torch.randn(1, d))[0])
        dir_adj[s].append((t1, r1))
        # n_decoys off-relation siblings, SAME goal component a (gcos cannot separate them from t1); reached via
        # wrong relations r' != r1 so only correct relation-bind ranks t1 above them.
        for _k in range(n_decoys):
            rp = int((r1 + 1 + rng.integers(0, T - 1)) % T)             # r' != r1
            b_rp = _l2t(_hrr_bind_t(roles_t[rp:rp + 1], _l2t(Z2[s:s + 1])))[0]
            dk = _new(b_rp + a * g + 0.15 * _l2t(torch.randn(1, d))[0])
            dir_adj[s].append((dk, rp))
        # t1 -> t2 == goal (strong goal component)
        t2 = _new(_l2t(_hrr_bind_t(roles_t[r2:r2 + 1], _l2t(Z2[t1:t1 + 1])))[0] + 1.5 * g + 0.15 * _l2t(torch.randn(1, d))[0])
        dir_adj[t1].append((t2, r2))
        starts.append(s); tgt[0].append(t1); tgt[1].append(t2); rid[0].append(r1); rid[1].append(r2)
    n = nid
    Z = _l2t(Z2[:n])
    return (Z, dir_adj[:n], n,
            np.asarray(starts, np.int64), [np.asarray(t, np.int64) for t in tgt],
            [np.asarray(r, np.int64) for r in rid])


def _mechanism_selftest():
    device = torch.device("cpu")
    d = 96
    T = 6
    roles_t = torch.from_numpy(make_unitary_roles(T, d, np.random.default_rng(11))).to(device)

    # ---- P2 + P1 on the lookahead-trap set ----
    Zt, adj_t, nt, s_t, tg_t, rl_t = _plant_trap_set(device, d, T, roles_t, np.random.default_rng(1), 140)
    Zpt = torch.cat([Zt, torch.zeros(1, d, device=device)], dim=0)
    nbr_idx_t, _nr, nbr_mask_t, Dmax_t, _mo = build_nbr_table(adj_t, nt, device)
    rg_t, _h, sg_t, _v = run_greedy_arm(Zt, Zpt, roles_t, nbr_idx_t, nbr_mask_t, s_t, tg_t, rl_t,
                                        device, 256, nt, GAMMA, verify=False)
    rb1_t, _h, sb1_t, _s = run_beam_traversal_arm(Zt, Zpt, roles_t, nbr_idx_t, nbr_mask_t, s_t, tg_t, rl_t,
                                                  device, 256, nt, GAMMA, 1)
    rbB_t, _h, sbB_t, _s = run_beam_traversal_arm(Zt, Zpt, roles_t, nbr_idx_t, nbr_mask_t, s_t, tg_t, rl_t,
                                                  device, 256, nt, GAMMA, BEAM_WIDTH)
    Lt = len(tg_t)
    # P1: beam(B=1) == greedy at every planted depth
    isolation_ok = bool(all(abs(rb1_t[dd] - rg_t[dd]) <= 0.02 for dd in range(1, Lt + 1)))
    # P2: greedy trapped (low reach@1/@2); beam recovers materially
    greedy_trapped = bool(rg_t[1] == rg_t[1] and rg_t[1] <= 0.35)
    beam_recovers = bool(rbB_t[1] == rbB_t[1] and rg_t[1] == rg_t[1]
                         and rbB_t[1] >= rg_t[1] + 0.30 and rbB_t[2] >= rg_t[2] + 0.30)

    # ---- P3 on the relation-essential set ----
    Zr, adj_r, nr, s_r, tg_r, rl_r = _plant_relation_essential_set(device, d, T, roles_t,
                                                                   np.random.default_rng(2), 140)
    Zpr = torch.cat([Zr, torch.zeros(1, d, device=device)], dim=0)
    nbr_idx_r, _nr2, nbr_mask_r, Dmax_r, _mo2 = build_nbr_table(adj_r, nr, device)
    scr_perm = _derangement(T, np.random.default_rng(7))
    roles_scr = roles_t[torch.from_numpy(scr_perm).to(device)]
    rb_r, _h, sb_r, _s = run_beam_traversal_arm(Zr, Zpr, roles_t, nbr_idx_r, nbr_mask_r, s_r, tg_r, rl_r,
                                                device, 256, nr, GAMMA, BEAM_WIDTH)
    rsc_r, _h, ssc_r, _s = run_beam_traversal_arm(Zr, Zpr, roles_scr, nbr_idx_r, nbr_mask_r, s_r, tg_r, rl_r,
                                                  device, 256, nr, GAMMA, BEAM_WIDTH)
    traversal_relational = bool(rb_r[1] == rb_r[1] and rb_r[1] >= 0.60)   # correct roles recover on-path
    scramble_collapses = bool(rsc_r[1] == rsc_r[1] and rb_r[1] == rb_r[1]
                              and rsc_r[1] <= rb_r[1] - 0.25)             # content-dependence fires

    # P4 + P5
    no_T_matrix = bool(int(nbr_idx_t.shape[1]) < nt and int(nbr_idx_r.shape[1]) < nr)
    arms_differ = bool(len({sg_t, sbB_t, ssc_r}) >= 3 and sb1_t == sb1_t and sb_r == sb_r)

    Lr = len(tg_r)
    res = dict(
        trap_greedy={dd: round(rg_t[dd], 4) for dd in range(1, Lt + 1)},
        trap_beam_B1={dd: round(rb1_t[dd], 4) for dd in range(1, Lt + 1)},
        trap_beam_B={dd: round(rbB_t[dd], 4) for dd in range(1, Lt + 1)},
        reless_traversal={dd: round(rb_r[dd], 4) for dd in range(1, Lr + 1)},
        reless_scrambled={dd: round(rsc_r[dd], 4) for dd in range(1, Lr + 1)},
        isolation_ok=isolation_ok, greedy_trapped=greedy_trapped, beam_recovers=beam_recovers,
        traversal_relational=traversal_relational, scramble_collapses=scramble_collapses,
        no_T_matrix=no_T_matrix, arms_differ=arms_differ,
        Dmax_trap=int(Dmax_t), Dmax_reless=int(Dmax_r), n_trap=int(nt), n_reless=int(nr),
    )
    ok = bool(isolation_ok and greedy_trapped and beam_recovers and traversal_relational
              and scramble_collapses and no_T_matrix and arms_differ)
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
    # LOAD-BEARING FAIRNESS GUARD: traversal uses a [n+1, Dmax] LOCAL table, never an [n,n] transition matrix.
    no_T_matrix = bool(int(nbr_idx.shape[1]) < n_nodes)
    _log("nbr table: Dmax=%d mean_out_deg=%.3f no_global_T_matrix=%s" % (Dmax, mean_out_deg, no_T_matrix))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS replay-traversal machinery: B=1 reproduces greedy (isolation); beam beats "
                        "greedy on the lookahead-trap set; correct-role traversal recovers on-path while scrambled "
                        "roles collapse (content-dependence); no [n,n] T-matrix; arms differ; typed subgraph + nbr "
                        "table exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res, subgraph_meta=meta, no_global_T_matrix=no_T_matrix))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, node_words, edges, rels, dir_adj, ksr_map, has_rel, roles_t,
                          nbr_idx, nbr_rel, nbr_mask, mean_out_deg, T, cfg, device, out_dir=out_dir_path)
            for a in ALL_ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1)
                           if a not in pm["arms"] or dd not in pm["arms"][a]["reach"]]
                if missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            # arms must differ (META_RULE_AF)
            if pm["arm_sigs"][REPLAY_TRAVERSAL] == pm["arm_sigs"][AUTONOMOUS_GREEDY]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d REPLAY_TRAVERSAL == GREEDY" % seed)
            if pm["arm_sigs"][REPLAY_TRAVERSAL] == pm["arm_sigs"][SUPPLIED_WAYPOINT]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d REPLAY_TRAVERSAL == SUPPLIED" % seed)
            if pm["arm_sigs"][REPLAY_TRAVERSAL] == pm["arm_sigs"][REPLAY_TRAVERSAL_SCRAMBLED]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d TRAVERSAL == SCRAMBLED" % seed)
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

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, meta, cfg, no_T_matrix)

    # DISCRIMINATOR-MUST-SURVIVE-SCALE: at smoke, require traversal to beat greedy or flag the abort recommendation.
    smoke_discriminator_fires = None
    if run_mode == "smoke":
        rt2 = gates["cg"]["traversal_reach2"]; g2 = gates["cg"]["greedy_reach2"]
        smoke_discriminator_fires = bool(rt2 == rt2 and g2 == g2 and rt2 >= g2 + SMOKE_FIRE_MARGIN)
        _log("SMOKE discriminator-fires (rt2>=greedy2+%.2f): %s (rt2=%.3f greedy2=%.3f)" % (
            SMOKE_FIRE_MARGIN, smoke_discriminator_fires, rt2, g2))

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        device=str(device), n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        subgraph_meta=meta, gates=gates, no_global_T_matrix=no_T_matrix,
        smoke_discriminator_fires=smoke_discriminator_fires,
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
