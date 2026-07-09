"""Stage-5 CG cell: does the substrate AUTONOMOUSLY derive its own intermediate hops toward a stated final goal
-- turning the certified goal-conditioning MM (SUPPLIED waypoint) into autonomous goal-directed chaining (CG
candidate) with NO new primitive?

BACKGROUND (the MM this builds on). The fair-test cert (exp_grounding_multihop_fair_test_unique_successor_goal_v1,
MEASURED@data/exp_grounding_multihop_fair_test_unique_successor_goal_v1/metrics.json): handing the query a
ground-truth next waypoint lifts hop-1 reach 0.453 -> 0.756 and reach@2 0.121 -> 0.500 (delta +0.303 @1). That
is MM-tier because the waypoint is SUPPLIED (externally handed). The open, higher-value question: can the
substrate derive each hop ITSELF, given only (start, relation-sequence, FINAL goal), never the intermediate
waypoints?

MECHANISM (brain-ground drill notes/research_autonomous_subgoal_derivation_goal_directed_traversal_CG_path_
2026-07-09.md). No system (brain or ML) invents a waypoint from nothing. The convergent, best-precedented
mechanism is greedy goal-directed SELECTION among REAL local neighbors (Gupta 2010 replay SPLICES real
experienced fragments; ML generate-and-verify): at each hop, score the actual local-neighborhood candidate
nodes by cosine of each candidate's code toward the FINAL-goal code, argmax-select, and (verify variant) commit
only if the selected hop's goal-cosine improves. This REUSES two already-certified/already-built primitives --
local-neighborhood scoping (the nbr table) gives the candidate set; goal-cosine biasing (the certified
goal-conditioning combine) gives the guidance -- and invents NO new operator. It does NOT algebraically
synthesize a waypoint code from nothing (the lit-scan's weakest-precedented option, negative external result).

ARMS (paired: identical learned codes + identical planted general chains + identical seeds across all arms;
only the QUERY differs). The first three REPRODUCE the fair-test anchors VERBATIM (Gate-D positive control):
  NO_CLEANUP        : global-cleanup-only chain (must-fail / anti-saturation control; collapses at reach>=2).
  MEMORYLESS        : goal-blind local decoder = the fair-test floor (repro ~0.453 @1 / 0.121 @2).
  SUPPLIED_WAYPOINT : = the fair-test GOAL_WAYPOINT MM ceiling; HANDED the true next waypoint each hop
                      (repro ~0.756 @1 / 0.500 @2). The bar autonomous must match.
  AUTONOMOUS_GREEDY : THE CG CANDIDATE. Given ONLY the FINAL goal (chain terminal node), at each hop score the
                      REAL local neighbors by (memoryless-local score + AUTO_GAMMA * goal-cosine-toward-final),
                      argmax, commit. No handed waypoint; derives every intermediate itself.
  AUTONOMOUS_VERIFY : the generate-and-verify wrapper. Same as GREEDY but restrict the argmax to candidates
                      whose goal-cosine strictly EXCEEDS the current node's goal-cosine (moving closer to goal);
                      fall back to the memoryless pick if no real neighbor improves. Secondary variant.

CG WIN BAR (pre-registered BEFORE the run; verdict on AUTONOMOUS_GREEDY = the conservative primary; VERIFY is a
secondary reported wrapper -- it can only be noted as "helps/hurts", never swapped in to rescue a verdict):
  HARD_PASS_CG = AUTONOMOUS_GREEDY reach@2 >= CG_RATIO_HP (0.85) * SUPPLIED_WAYPOINT reach@2  AND
                 AUTONOMOUS_GREEDY reach@2 >= MEMORYLESS reach@2 + AUTO_MATERIAL_DELTA (0.10)
                 -> autonomous derivation ~matches the supplied ceiling: autonomous goal-directed reasoning WORKS.
  HARD_FAIL_CG = AUTONOMOUS_GREEDY reach@2 <= MEMORYLESS reach@2 + AUTO_FAIL_SMALL (0.03)
                 -> goal-cosine too weak at multi-hop distance; derivation collapses to the goal-blind floor
                    (next mechanism = landmark/betweenness precompute or resonator full-chain factorization).
  MIDDLE_BAND  = autonomous beats memoryless materially but sits well below the supplied ceiling.

CAPABILITY FRAMING (3-part standard; this is a CG claim, verify-able): DIFFERENT CHANNEL = downstream reach@2/@3
(top-1 commit chained); LIVE ALTERNATIVE = the memoryless (goal-blind) query genuinely fails on same-relation
branch points; NECESSITY = autonomous goal-selection vs no-goal (MEMORYLESS) ablation, both paired. We report the
autonomous-vs-supplied RATIO and the autonomous-vs-memoryless DELTA, never an absolute bar above the ceiling.

HONESTY: REAL CG'd teacher-free relational learned codes (char-trigram + InfoNCE binding encoder) over the REAL
ConceptNet typed subgraph; top-1 commit fidelity; NO language understanding claimed. The FINAL goal handed to the
autonomous arms is a legitimate part of any goal-directed traversal's own specification (you always know where you
want to end up); the INTERMEDIATE waypoints are NOT handed -- that is exactly the MM->CG difference under test.
Reuses the fair-test / perhop-cleanup VET-landed encoder/chain/nbr/local-scoping primitives VERBATIM (calibration
continuity + no drift). Teacher-free, ASCII-only, device-aware torch (cuda if available, else cpu).

## Compute architecture
class: (c) mixed with justification. Storage strategy: SHARDED (each node its own code vector; no bundling --
compositional multi-hop chaining, per META_STORAGE_STRATEGY). Within each hop, all chains + all local candidates
are scored by batched matmul/einsum on GPU (cuda when available). ACROSS hops the chain is genuinely SEQUENTIAL
(hop h's candidate set depends on hop h-1's committed node) -- an inherent data dependency, not a batching flaw;
this is the same shape as the fair-test cell which ran 3 seeds FULL in 16.4s on cuda. No Python-loop matmul over
independent phase points.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; AUTONOMOUS_GREEDY commit-sig != SUPPLIED != MEMORYLESS !=
#   NO_CLEANUP; asserted per seed on distinct commit signatures).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0002 at n=5000). The reference points are MEASURED anchors, not a
#   closed-form floor: MEMORYLESS reach@2=0.121 and SUPPLIED reach@2=0.500 (MEASURED@fair-test metrics.json).
#   HARD_PASS bar 0.85*SUPPLIED is on the achievable side (SUPPLIED already demonstrated 0.500 is reachable with a
#   goal signal; the question is whether the autonomously-derived goal signal is as good). crlb_reachability: OK.
# - baseline_in_band: MEMORYLESS@1 in (0.05, 0.95) (repro ~0.453). NO_CLEANUP@2 collapses (anti-saturation).
# - discriminator survives scale: the MM discriminator (SUPPLIED >> MEMORYLESS) is graph-structural and FIRES AT
#   SMOKE on the real subgraph; asserted at smoke. The CG question (AUTONOMOUS vs SUPPLIED ratio) is the
#   MEASUREMENT -- smoke reports it as a preview; FULL (3 seeds) is canonical. The must-fail control NO_CLEANUP
#   collapses AT smoke scale (SATURATION-VACUOUS guard).
# - HARD_PASS strictly above floor: ratio bar 0.85*SUPPLIED AND +0.10 over MEMORYLESS is a clear categorical
#   margin over the goal-blind floor, not an at-floor result.
# - HP_SCOPE: the CG win gate applies to AUTONOMOUS_GREEDY only. SUPPLIED_WAYPOINT / MEMORYLESS = positive-control
#   reproductions of the fair-test MM (must reproduce within tolerance for the MM discriminator to be valid);
#   NO_CLEANUP = must-fail control (must collapse). VERIFY = secondary wrapper (reported, not gated).
# - positive_control (Gate D): MEMORYLESS + SUPPLIED_WAYPOINT reproduce the fair-test MEASURED anchors AT THE
#   MATCHED FULL regime (same n_nodes/code_dim/feat_dim/epochs/seeds/chains); repro drift > 0.10 -> flag.
# - sweep axis: hop depth d in {1,2,3,4}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms x
#   all depths (arm/depth-cardinality check).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate. AUTO_GAMMA is PRE-REGISTERED (= the certified
#   GOAL_GAMMA 1.5), NOT tuned on real data; the mechanism self-test verifies gamma=1.5 lets AUTONOMOUS recover
#   ~SUPPLIED on clean planted codes (signal present), so any real-data collapse is a genuine signal-weakness
#   negative, not a mis-set knob. A diagnostic gamma sweep is logged but does NOT drive the verdict.
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
# Reuse the fair-test nbr table, k_sr, local scoring, and the MEMORYLESS / GOAL_WAYPOINT / NO_CLEANUP arms VERBATIM
# so the first three arms REPRODUCE the fair-test MM bit-for-bit at the matched config (Gate-D positive control).
from experiments.exp_grounding_multihop_fair_test_unique_successor_goal_v1 import (  # noqa: E402
    build_nbr_table,
    build_ksr,
    run_chain_arm as ft_run_chain_arm,
    run_no_cleanup as ft_run_no_cleanup,
    MEMORYLESS as FT_MEMORYLESS,
    GOAL_WAYPOINT as FT_GOAL_WAYPOINT,
)

ANCHOR_NAME = "grounding_multihop_autonomous_subgoal_greedy_v1"

MAX_REACH = 4
HIT_K = 10
AUTO_GAMMA = 1.5   # goal-cosine boost weight; PRE-REGISTERED = certified GOAL_GAMMA 1.5 (not tuned on real data)

# Arm names
NO_CLEANUP = "NO_CLEANUP"
MEMORYLESS = "MEMORYLESS"                       # goal-blind floor (= fair-test MEMORYLESS)
SUPPLIED_WAYPOINT = "SUPPLIED_WAYPOINT"         # MM ceiling (= fair-test GOAL_WAYPOINT); handed the true waypoint
AUTONOMOUS_GREEDY = "AUTONOMOUS_GREEDY"         # CG candidate (primary); goal-cosine argmax among real neighbors
AUTONOMOUS_VERIFY = "AUTONOMOUS_VERIFY"         # CG candidate (secondary); + verify-before-commit gate
ALL_ARMS = [NO_CLEANUP, MEMORYLESS, SUPPLIED_WAYPOINT, AUTONOMOUS_GREEDY, AUTONOMOUS_VERIFY]

# ---------------------------------------------------------------------------
# Pre-registered CG bands (picked BEFORE the run). Reach = TOP-1 COMMIT accuracy. Reference anchors are MEASURED
# from the fair-test cert, not closed-form. The ratio bar self-calibrates to the SUPPLIED reach@2 measured in
# THIS run (so it is robust to any small config drift).
# ---------------------------------------------------------------------------
CG_RATIO_HP = 0.85          # HARD_PASS: AUTONOMOUS_GREEDY reach@2 >= this * SUPPLIED_WAYPOINT reach@2
AUTO_MATERIAL_DELTA = 0.10  # HARD_PASS also requires reach@2 >= MEMORYLESS reach@2 + this (materially over floor)
AUTO_FAIL_SMALL = 0.03      # HARD_FAIL: reach@2 <= MEMORYLESS reach@2 + this (collapsed to goal-blind floor)
VERIFY_HELP_MIN = 0.05      # report threshold: VERIFY "helps" if reach@2 >= GREEDY reach@2 + this

# Anti-saturation / must-fail control (mirrors fair-test)
BASE_COLLAPSE_ABS = 0.10
BASE_COLLAPSE_FRAC = 0.50
BASE_IN_BAND_HI = 0.95
HOP1_PRESENT = 0.08
SUPPLIED_FIRES_MIN = 0.10   # MM discriminator: SUPPLIED reach@2 >= MEMORYLESS reach@2 + this (must fire at scale)

# Gate-D positive-control reproduction anchors (MEASURED@fair-test metrics.json) + tolerance (FULL config only)
REPRO_MEM1 = 0.453
REPRO_SUP1 = 0.756
REPRO_SUP2 = 0.500
REPRO_TOL = 0.10

DIAG_GAMMAS = [0.5, 1.0, 1.5, 2.5]   # diagnostic-only gamma sweep (logged; does NOT drive verdict)


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
# FULL config is IDENTICAL to the fair-test cell's FULL_CFG so MEMORYLESS + SUPPLIED reproduce the MM anchors.
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
# AUTONOMOUS arm: greedy goal-directed selection among REAL local neighbors toward the FINAL goal.
# score(candidate) = <l2(pred_memoryless), Z[candidate]> + gamma * max(0, cos(Z[candidate], Z[final_goal])).
# The memoryless bind-score keeps the relation-appropriate direction primary; the goal-cosine term breaks the tie
# among the same-relation siblings toward the final goal (the certified goal-conditioning combine, applied to a
# self-generated real-neighbor candidate set instead of an externally-handed waypoint).
# verify=True: restrict argmax to candidates whose goal-cosine strictly exceeds the current node's goal-cosine
# (generate-and-verify: only commit a hop that moves closer to the goal); fall back to the memoryless argmax when
# no real neighbor improves (a clean, honest failure mode rather than a wrong-direction step).
# ---------------------------------------------------------------------------

def run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, start, targets, role_ids,
                       device, chunk, n_nodes, gamma, verify):
    L = len(targets)
    C = start.shape[0]
    cur = torch.from_numpy(start).to(device)
    goal = torch.from_numpy(targets[L - 1]).to(device)   # FINAL goal = chain terminal node (same across hops)
    reach = {}
    hit10 = {}
    commit_sig = []
    n_improve = 0
    n_fallback = 0
    n_scored = 0
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
            goal_blk = goal[b0:b1]
            cand = nbr_idx[cur_blk]                     # [b, Dmax] real local out-neighbors
            mask = nbr_mask[cur_blk]                    # [b, Dmax]
            Zc = Zp[cand]                               # [b, Dmax, d]
            p = _l2t(pred_blk)
            base = torch.einsum("bd,bkd->bk", p, Zc)    # memoryless local score
            zg = Z[goal_blk.clamp(max=n_nodes - 1)]     # [b, d] final-goal code
            gcos = torch.einsum("bkd,bd->bk", Zc, zg)   # [b, Dmax] candidate->final-goal cosine (codes L2-normed)
            s = base + gamma * gcos.clamp(min=0.0)
            s = s.masked_fill(~mask, float("-inf"))
            nonempty = mask.any(dim=1)
            base_masked = base.masked_fill(~mask, float("-inf"))
            if verify:
                g_cur = (Z[cur_blk.clamp(max=n_nodes - 1)] * zg).sum(dim=1)   # [b] current node -> goal cosine
                improves = (gcos > g_cur[:, None]) & mask
                has_improve = improves.any(dim=1)
                s_v = s.masked_fill(~improves, float("-inf"))
                la_v = s_v.argmax(dim=1)
                la_f = base_masked.argmax(dim=1)        # fallback: memoryless pick when no neighbor improves
                la = torch.where(has_improve, la_v, la_f)
                n_improve += int((has_improve & nonempty).sum().item())
                n_fallback += int((~has_improve & nonempty).sum().item())
                n_scored += int(nonempty.sum().item())
            else:
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
    verify_stats = dict(n_improve=n_improve, n_fallback=n_fallback, n_scored=n_scored,
                        fallback_frac=(n_fallback / n_scored) if n_scored > 0 else float("nan"))
    return reach, hit10, sig, verify_stats


# ---------------------------------------------------------------------------
# Per-seed run: all arms on the identical general-chain population + identical learned codes (paired).
# The general-chain population is sampled IDENTICALLY to the fair-test cell (same rng seed offset + sampler) so
# MEMORYLESS + SUPPLIED reproduce the MM anchors bit-for-bit at the matched config.
# ---------------------------------------------------------------------------

def run_seed(seed, node_words, edges, rels, dir_adj, ksr_map, has_rel, roles_t,
             nbr_idx, nbr_rel, nbr_mask, mean_out_deg, T, cfg, device, out_dir=None):
    n_nodes = len(node_words)
    chunk = cfg["chain_chunk"]
    X = char_trigram_features(node_words, cfg["feat_dim"])
    Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_auto")
    enc_dig = hashlib.sha256(Z.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()
    Zp = torch.cat([Z, torch.zeros(1, cfg["code_dim"], device=device)], dim=0)

    # general chains (IDENTICAL rng offset + sampler as the fair-test cell -> paired reproduction)
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
    # AUTONOMOUS_GREEDY (primary CG candidate) + AUTONOMOUS_VERIFY (secondary wrapper)
    r, h, sig, vg = run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                       device, chunk, n_nodes, AUTO_GAMMA, verify=False)
    arms[AUTONOMOUS_GREEDY] = dict(reach=r, hit10=h, verify_stats=vg)
    sigs[AUTONOMOUS_GREEDY] = sig
    r, h, sig, vv = run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                       device, chunk, n_nodes, AUTO_GAMMA, verify=True)
    arms[AUTONOMOUS_VERIFY] = dict(reach=r, hit10=h, verify_stats=vv)
    sigs[AUTONOMOUS_VERIFY] = sig

    # diagnostic gamma sweep on AUTONOMOUS_GREEDY (logged only; does NOT drive the verdict)
    gamma_sweep = {}
    for gg in DIAG_GAMMAS:
        rr, _hh, _ss, _vv = run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                                               device, chunk, n_nodes, gg, verify=False)
        gamma_sweep["%.2f" % gg] = {dd: rr[dd] for dd in range(1, MAX_REACH + 1)}

    for arm in ALL_ARMS:
        _log("  seed=%d %-18s reach@[1..%d]=%s" % (
            seed, arm, MAX_REACH, {dd: round(arms[arm]["reach"][dd], 3) for dd in range(1, MAX_REACH + 1)}))

    return dict(seed=seed, arms=arms, arm_sigs=sigs, encoder_digest=enc_dig, n_general=Cg,
                gamma_sweep=gamma_sweep, code_dim=cfg["code_dim"], mean_out_deg=mean_out_deg)


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
    av1 = R(AUTONOMOUS_VERIFY, 1); av2 = R(AUTONOMOUS_VERIFY, 2); av3 = R(AUTONOMOUS_VERIFY, 3)

    # CG headline metrics (primary = AUTONOMOUS_GREEDY)
    ratio2 = (auto2 / sup2) if (sup2 == sup2 and sup2 > 1e-9) else float("nan")
    ratio3 = (auto3 / sup3) if (sup3 == sup3 and sup3 > 1e-9) else float("nan")
    delta2 = (auto2 - mem2) if (auto2 == auto2 and mem2 == mem2) else float("nan")
    delta1 = (auto1 - mem1) if (auto1 == auto1 and mem1 == mem1) else float("nan")
    verify_delta2 = (av2 - auto2) if (av2 == av2 and auto2 == auto2) else float("nan")
    verify_helps = bool(verify_delta2 == verify_delta2 and verify_delta2 >= VERIFY_HELP_MIN)

    # anti-saturation + baseline-in-band + MM-discriminator-fires
    hop1_present = bool(mem1 == mem1 and mem1 >= HOP1_PRESENT)
    baseline_in_band = bool(mem1 == mem1 and 0.05 < mem1 < BASE_IN_BAND_HI)
    baseline_collapses = bool(base2 == base2 and base1 == base1
                              and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))
    supplied_fires = bool(sup2 == sup2 and mem2 == mem2 and sup2 >= mem2 + SUPPLIED_FIRES_MIN)

    # CG gates (on AUTONOMOUS_GREEDY)
    cg_hard_pass = bool(auto2 == auto2 and sup2 == sup2 and mem2 == mem2
                        and auto2 >= CG_RATIO_HP * sup2 and delta2 == delta2 and delta2 >= AUTO_MATERIAL_DELTA)
    cg_hard_fail = bool(delta2 == delta2 and delta2 <= AUTO_FAIL_SMALL)

    # Gate-D reproduction audit (only meaningful at FULL config == fair-test regime)
    is_full = bool(len(cfg["seeds"]) == 3 and cfg["n_nodes"] == 5000 and cfg["code_dim"] == 2048)
    repro_mem1_ok = bool(mem1 == mem1 and abs(mem1 - REPRO_MEM1) <= REPRO_TOL)
    repro_sup1_ok = bool(sup1 == sup1 and abs(sup1 - REPRO_SUP1) <= REPRO_TOL)
    repro_sup2_ok = bool(sup2 == sup2 and abs(sup2 - REPRO_SUP2) <= REPRO_TOL)
    repro_ok = bool(repro_mem1_ok and repro_sup1_ok and repro_sup2_ok)

    # ---- overall verdict ----
    if not hop1_present:
        verdict = "INCONCLUSIVE_HOP1_ABSENT"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif not supplied_fires:
        verdict = "INCONCLUSIVE_SUPPLIED_MM_DID_NOT_FIRE"
    elif is_full and not repro_ok:
        verdict = "INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT"
    elif cg_hard_pass:
        verdict = "HARD_PASS_CG_AUTONOMOUS"
    elif cg_hard_fail:
        verdict = "HARD_FAIL_CG_AUTONOMOUS_COLLAPSE"
    else:
        verdict = "MIDDLE_BAND_CG_PARTIAL"

    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f @2=%.3f(collapses=%s) || MEMORYLESS @1=%.3f(in_band=%s) @2=%.3f @3=%.3f || "
        "SUPPLIED_WAYPOINT @1=%.3f @2=%.3f @3=%.3f (fires=%s) || AUTONOMOUS_GREEDY @1=%.3f @2=%.3f @3=%.3f || "
        "AUTONOMOUS_VERIFY @1=%.3f @2=%.3f @3=%.3f (helps=%s d=%s) || CG: ratio@2(auto/sup)=%s ratio@3=%s "
        "delta@2(auto-mem)=%s delta@1=%s || HARD_PASS=(auto2>=%.2f*sup2 AND auto2>=mem2+%.2f)=%s "
        "HARD_FAIL=(auto2<=mem2+%.2f)=%s || repro(full=%s): mem1_ok=%s sup1_ok=%s sup2_ok=%s || "
        "gamma=%.2f n_gen=%d nodes=%d E=%d rel=%d seeds=%d run=%s" % (
            verdict, base1, base2, baseline_collapses, mem1, baseline_in_band, mem2, mem3,
            sup1, sup2, sup3, supplied_fires, auto1, auto2, auto3,
            av1, av2, av3, verify_helps, _fmt(verify_delta2), _fmt(ratio2), _fmt(ratio3),
            _fmt(delta2), _fmt(delta1), CG_RATIO_HP, AUTO_MATERIAL_DELTA, cg_hard_pass,
            AUTO_FAIL_SMALL, cg_hard_fail, is_full, repro_mem1_ok, repro_sup1_ok, repro_sup2_ok,
            AUTO_GAMMA, per_seed[0]["n_general"], meta["n_nodes"], meta["n_edges"],
            meta.get("n_relation_types", -1), len(per_seed), "full" if is_full else "smoke"))

    gates = dict(
        verdict=verdict,
        reach={a: {d: R(a, d) for d in range(1, MAX_REACH + 1)} for a in ALL_ARMS},
        cg=dict(memoryless_reach2=mem2, supplied_reach2=sup2, autonomous_greedy_reach2=auto2,
                autonomous_verify_reach2=av2, ratio2=ratio2, ratio3=ratio3, delta2=delta2, delta1=delta1,
                autonomous_greedy_reach1=auto1, autonomous_greedy_reach3=auto3,
                cg_hard_pass=cg_hard_pass, cg_hard_fail=cg_hard_fail,
                verify_delta2=verify_delta2, verify_helps=verify_helps),
        anti_sat=dict(hop1_present=hop1_present, baseline_in_band=baseline_in_band,
                      baseline_collapses=baseline_collapses, supplied_fires=supplied_fires),
        positive_control=dict(is_full=is_full, repro_mem1=mem1, repro_sup1=sup1, repro_sup2=sup2,
                              repro_mem1_ok=repro_mem1_ok, repro_sup1_ok=repro_sup1_ok,
                              repro_sup2_ok=repro_sup2_ok, repro_ok=repro_ok,
                              anchors=dict(mem1=REPRO_MEM1, sup1=REPRO_SUP1, sup2=REPRO_SUP2, tol=REPRO_TOL)),
        bands=dict(CG_RATIO_HP=CG_RATIO_HP, AUTO_MATERIAL_DELTA=AUTO_MATERIAL_DELTA, AUTO_FAIL_SMALL=AUTO_FAIL_SMALL,
                   VERIFY_HELP_MIN=VERIFY_HELP_MIN, SUPPLIED_FIRES_MIN=SUPPLIED_FIRES_MIN,
                   BASE_COLLAPSE_ABS=BASE_COLLAPSE_ABS, HOP1_PRESENT=HOP1_PRESENT, AUTO_GAMMA=AUTO_GAMMA),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test (planted codes + real local graph). Proves: chain machinery works;
# NO_CLEANUP collapses; MEMORYLESS is aliased (~1/k) on branch chains; SUPPLIED recovers; and -- the load-bearing
# positive control for THIS cell -- when the goal-ward signal IS present in the codes, AUTONOMOUS_GREEDY (raw
# goal-cosine, gamma=1.5) recovers ~SUPPLIED autonomously. So a real-data collapse is a genuine signal-weakness
# negative, not a mis-set gamma or broken mechanism. arms differ; verify variant runs.
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    device = torch.device("cpu")
    rng = np.random.default_rng(0)
    d = 96
    T = 4
    KSR = 3
    n_cap = 3000
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

    # BRANCH chains with a planted GOAL-WARD signal. Each chain has a per-chain goal direction g_c. Along the true
    # path, each true node code carries a component toward g_c (so its goal-cosine to the terminal true node =
    # goal rises); the KSR-1 off-path siblings at each hop share the same relation-bind direction (aliased) but
    # carry NO goal component -> lower goal-cosine. MEMORYLESS (goal-blind) cannot separate the siblings;
    # AUTONOMOUS goal-cosine can; SUPPLIED (waypoint) can via one-step lookahead.
    br_start, br_tgt, br_rid = [], [[] for _ in range(MAX_REACH)], [[] for _ in range(MAX_REACH)]
    for _c in range(120):
        if next_id >= n_cap - (MAX_REACH * KSR + 6):
            break
        g_c = _l2t(torch.randn(1, d))[0]                      # per-chain goal direction
        cur = _new(_l2t(torch.randn(1, d))[0])               # start (no goal component)
        start_node = cur
        for h in range(MAX_REACH):
            r = int(rng.integers(0, T))
            pred = _l2t(_hrr_bind_t(roles_t[r:r + 1], _l2t(Z2[cur:cur + 1])))[0]
            # true on-path sibling: relation-bind direction + strong goal-ward component
            true_v = _new(pred + 1.5 * g_c + 0.3 * _l2t(torch.randn(1, d))[0])
            dir_adj[cur].append((true_v, r))
            # KSR-1 aliased off-path siblings: same relation-bind direction, NO goal component
            for _k in range(KSR - 1):
                off = _new(pred + 0.6 * _l2t(torch.randn(1, d))[0])
                dir_adj[cur].append((off, r))
            br_tgt[h].append(true_v); br_rid[h].append(r)
            cur = true_v
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

    r_no, _h, _sa, s_no = ft_run_no_cleanup(Z, roles_t, g_start, g_tgt, g_role, device, n)
    r_mem, _h, _sa, s_mem = ft_run_chain_arm(FT_MEMORYLESS, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                             g_start, g_tgt, g_role, device, 256, n)
    r_sup, _h, _sa, s_sup = ft_run_chain_arm(FT_GOAL_WAYPOINT, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                             g_start, g_tgt, g_role, device, 256, n)
    r_auto, _h, s_auto, _vg = run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_tgt, g_role,
                                                 device, 256, n, AUTO_GAMMA, verify=False)
    r_av, _h, s_av, _vv = run_autonomous_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, g_start, g_tgt, g_role,
                                             device, 256, n, AUTO_GAMMA, verify=True)

    nocleanup_ran = bool(r_no[1] == r_no[1])
    memoryless_aliased = bool(r_mem[1] == r_mem[1] and r_mem[1] < 0.70)          # goal-blind underdetermined (~1/k)
    supplied_reaches = bool(r_sup[2] == r_sup[2] and r_sup[2] >= 0.55)           # waypoint ceiling reachable
    auto_recovers = bool(r_auto[1] == r_auto[1] and r_mem[1] == r_mem[1]
                         and r_auto[1] >= r_mem[1] + 0.20 and r_auto[2] >= 0.50)  # autonomous derivation works
    auto_near_supplied = bool(r_auto[2] == r_auto[2] and r_sup[2] == r_sup[2]
                              and r_sup[2] > 1e-9 and r_auto[2] >= 0.70 * r_sup[2])  # ~matches supplied (pos ctrl)
    verify_runs = bool(r_av[1] == r_av[1] and r_av[2] == r_av[2])
    arms_differ = bool(len({s_no, s_mem, s_sup, s_auto, s_av}) >= 4)

    res = dict(
        reach_no_cleanup={dd: round(r_no[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_memoryless={dd: round(r_mem[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_supplied={dd: round(r_sup[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_autonomous_greedy={dd: round(r_auto[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_autonomous_verify={dd: round(r_av[dd], 4) for dd in range(1, MAX_REACH + 1)},
        nocleanup_ran=nocleanup_ran, memoryless_aliased=memoryless_aliased, supplied_reaches=supplied_reaches,
        auto_recovers=auto_recovers, auto_near_supplied=auto_near_supplied, verify_runs=verify_runs,
        arms_differ=arms_differ, Dmax=int(Dmax), n_synth=int(n),
    )
    ok = bool(nocleanup_ran and memoryless_aliased and supplied_reaches and auto_recovers
              and auto_near_supplied and verify_runs and arms_differ)
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

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS autonomous-subgoal machinery: NO_CLEANUP collapses; MEMORYLESS aliased; "
                        "SUPPLIED recovers; AUTONOMOUS_GREEDY recovers ~SUPPLIED on goal-ward planted codes; "
                        "verify variant runs; arms differ; typed subgraph + nbr table + k_sr exercised",
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
                          nbr_idx, nbr_rel, nbr_mask, mean_out_deg, T, cfg, device, out_dir=out_dir_path)
            for a in ALL_ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1)
                           if a not in pm["arms"] or dd not in pm["arms"][a]["reach"]]
                if missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            # arms must differ (META_RULE_AF)
            if pm["arm_sigs"][AUTONOMOUS_GREEDY] == pm["arm_sigs"][MEMORYLESS]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d AUTONOMOUS_GREEDY == MEMORYLESS" % seed)
            if pm["arm_sigs"][AUTONOMOUS_GREEDY] == pm["arm_sigs"][SUPPLIED_WAYPOINT]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d AUTONOMOUS_GREEDY == SUPPLIED" % seed)
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
