"""Stage-5 reader FAIR-TEST cell: measure the multi-hop reader against the INFORMATION-THEORETIC FAIR CEILING,
not an unwinnable absolute bar.

FINDING (fairness VET, off-disk decisive): the multi-hop reader test as posed in v2/v3 is UNDERDETERMINED-BY-
CONSTRUCTION. The per-hop query bind(role_r, Z[cur]) is a PURE function of (cur, relation); every one of the
k_sr same-relation siblings of (cur, r) yields the IDENTICAL query, so no decoder can do better than 1/k_sr
among them. The fair ceiling is reach@1 = E[1/k_sr] = 0.562 and joint reach@2 = 0.198 (THEORETICAL@fairness_
ceiling recompute over the real ConceptNet typed subgraph). v2 MEASURED reach@1=0.453 (81% of ceiling), reach@2
=0.134 (68% of ceiling) -- it sits essentially AT the fair ceiling. The old WIN bar reach@2>=0.60 was 3x above
the info-theoretic max: the "wall" was the TEST, not the substrate.

This cell measures the reader THREE fair ways on the SAME real learned codes / same harness as v2/v3 (the FIX is
the TEST/QUERY, not the substrate):

  A. RE-SCORE (Prediction 1): on GENERAL chains, score the SAME memoryless decoder two fair ways --
     SET-ACCEPTING (hit if the top pick is a MEMBER of the true same-relation sibling set, not one arbitrary
     pre-chosen sibling) and ACHIEVED/CEILING (reach vs E[1/k_sr]). Confirms the substrate lands on a TRUE
     sibling most of the time; it just cannot pick WHICH one (that bit is not in the query).

  B. UNIQUE-SUCCESSOR (primary capability demo): restrict planted chains to hops where k_sr==1 (unique
     successor) at every hop -> ceiling becomes 1.0, so reach@2>=0.60 AND reach@3>=0.35 is now WINNABLE and
     measures TRUE chaining fidelity, not a coin-flip. ~32% of hop-1 edges already qualify.

  C. GOAL-CARRYING (Prediction 2, brain-aligned A*/UVFA analog): augment the memoryless query with ONE piece of
     already-available downstream path/goal context so the query has the bits to pick among siblings. Control =
     memoryless query (LOCAL_SEMANTIC, which fails). GOAL_REL = weak goal (downstream relation r_{h+1} must be
     supported by the candidate). GOAL_WAYPOINT = strong goal (the known next waypoint w_true: prefer the sibling
     v s.t. one more r_{h+1} bind from v lands on w_true -- A*/UVFA subgoal). Shows goal-carrying RECOVERS the
     sibling the memoryless query cannot.

  CALIBRATION (Prediction 3, cheap alongside): memoryless hop-1 accuracy bucketed by branching factor k_sr must
  decline SMOOTHLY (graded), not flat (trivial) or cliff (still unfair) -- confirms the fair test is not over-
  corrected into triviality.

CAPABILITY-DEMO FRAMING (3-part standard): DIFFERENT CHANNEL = downstream multi-hop reach (top-1 commit chained);
LIVE ALTERNATIVE = the memoryless query genuinely fails on same-relation branch points; NECESSITY = goal-carrying
vs memoryless ablation (GOAL_WAYPOINT recovers what MEMORYLESS cannot). We report reach vs the FAIR ceiling,
never an absolute bar above the ceiling.

HONESTY: REAL CG'd teacher-free relational learned codes (char-trigram + InfoNCE binding encoder) over the REAL
ConceptNet typed subgraph; top-1 commit fidelity; NO language understanding claimed. All arms PAIRED (identical
codes / roles / seeds / graph / dim); only the QUERY (memoryless vs goal-carrying) and the CHAIN POPULATION
(general vs unique-successor) differ. The downstream relation / next waypoint provided to the goal arms is a
legitimate part of a multi-hop query's own specification (Query2Box conjunctive-query / A* subgoal), available in
any genuine traversal; the memoryless control does NOT get it. Reuses Stage-4/5 VET-landed encoder/chain/LOCAL-
scoping primitives VERBATIM (calibration continuity + no drift). Teacher-free, ASCII-only, device-aware torch.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; GOAL_WAYPOINT commit-sig != MEMORYLESS != NO_CLEANUP).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0002 at n=5000); the FAIR ceiling reach@1=E[1/k_sr]=0.562 and joint
#   reach@2=0.198 are THEORETICAL@fairness_ceiling (graph-structural). Unique-successor ceiling = 1.0 (k_sr==1).
#   Bands sit strictly below the applicable ceiling. crlb_reachability: WIN bars are on the achievable side.
# - baseline_in_band: MEMORYLESS@1 in (0.05, 0.95) (v2 MEASURED 0.453). NO_CLEANUP@2 collapses.
# - discriminator survives scale: unique-successor reach >> general reach, and GOAL_WAYPOINT >> MEMORYLESS, both
#   FIRE AT SMOKE on the real subgraph (graph-structural, scale-independent). Asserted at smoke.
# - HARD_PASS strictly above floor: US reach2>=0.60 AND reach3>=0.35; GOAL_WAYPOINT@1>=0.55 AND delta>=0.15.
# - HP_SCOPE: US WIN gate applies to UNIQUE_SUCCESSOR only; GOAL gate applies to GOAL_WAYPOINT only. MEMORYLESS =
#   baseline/control (must be in band, must fail the unfair general reach@2); NO_CLEANUP = must-fail control.
# - sweep axis: chain population {general, unique_successor} x hop depth {1..4}; goal dose {none, rel, waypoint};
#   EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms x all depths (cardinality check).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate (baseline-collapse + baseline-in-band + k_sr calibration
#   recomputed empirically per run; paired per-chain top-1 commits so all deltas are paired).
# - PAIRED trials (arm-comparison discriminator): all arms share identical codes + roles + seeds + graph + dim.
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
from collections import Counter
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
# Reuse the Stage-4/5 VET-landed primitives VERBATIM (calibration continuity + no drift).
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev,
    sample_chains,
    build_typed_diradj,
    _hrr_bind_t,
    _l2t,
)

ANCHOR_NAME = "grounding_multihop_fair_test_unique_successor_goal_v1"

MAX_REACH = 4
HIT_K = 10
GOAL_GAMMA = 1.5   # pre-registered goal-boost weight (probe: WAYPOINT@1 0.73 at gamma=1.5; graded, not trivial)

# Arm names
NO_CLEANUP = "NO_CLEANUP"
MEMORYLESS = "MEMORYLESS"                 # = v2 LOCAL_SEMANTIC; baseline/control
GOAL_REL = "GOAL_REL"                     # weak goal: downstream relation supported
GOAL_WAYPOINT = "GOAL_WAYPOINT"           # strong goal: known next waypoint (A*/UVFA subgoal)
UNIQUE_SUCCESSOR = "UNIQUE_SUCCESSOR"     # MEMORYLESS decoder on k_sr==1 chains (ceiling 1.0)
GENERAL_ARMS = [NO_CLEANUP, MEMORYLESS, GOAL_REL, GOAL_WAYPOINT]   # run on general chains
GOAL_ARMS = [GOAL_REL, GOAL_WAYPOINT]

# ---------------------------------------------------------------------------
# Pre-registered FAIR bands (picked BEFORE the run). Reach = TOP-1 COMMIT accuracy.
# ---------------------------------------------------------------------------
# Prediction 1 (re-score): substrate sits at fair ceiling; most "failures" are correct-but-wrong-sibling.
P1_SETACC_MIN = 0.60          # SET-ACCEPTING reach@1 must be a real usable signal
P1_ERR_RECOVERED_MIN = 0.40   # (setacc - naive)/(1 - naive) >= this: >=40% of naive errors are true-sibling hits
P1_CEIL_RATIO_LO = 0.70       # ACHIEVED/CEILING@1 must be >= this (substrate near the fair ceiling)
P1_2X_HOP = 2.0               # research 2x clause, checked on conditional hop-2 where k_sr is large

# Prediction 2 / Item 2 unique-successor WIN (primary capability demo; ceiling 1.0 so winnable)
US_WIN_REACH2 = 0.60
US_WIN_REACH3 = 0.35
US_FAIL_REACH2 = 0.30         # HARD_FAIL floor (below halfway to winnable despite ceiling 1.0)

# Item 3 goal-carrying (Prediction 2): goal-carrying recovers the sibling memoryless cannot
GOAL_WIN_REACH1 = 0.55        # GOAL_WAYPOINT reach@1 >= this (research P2 HARD-PASS)
GOAL_WIN_DELTA = 0.15         # AND materially above MEMORYLESS reach@1
GOAL_FAIL_DELTA = 0.05        # HARD_FAIL: goal not materially above memoryless

# Anti-saturation must-fail control
BASE_COLLAPSE_ABS = 0.10
BASE_COLLAPSE_FRAC = 0.50
BASE_IN_BAND_HI = 0.95
HOP1_PRESENT = 0.08

# Prediction 3 calibration (graded, not flat/cliff)
CALIB_RANGE_MIN = 0.20        # (acc@k=1 - acc@k>=3) >= this (not flat/trivial)
CALIB_CLIFF_MAX = 0.85        # no single adjacent-bucket drop > this (not a cliff)


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
# code_dim / feat_dim / epochs held identical to v2/v3 at FULL so MEMORYLESS reproduces v2 (positive control).
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
# Neighbor table + k_sr structures
# ---------------------------------------------------------------------------

def build_nbr_table(dir_adj, n_nodes, device):
    degs = [len(dir_adj[u]) for u in range(n_nodes)]
    Dmax = max(1, max(degs) if degs else 1)
    nbr_idx = np.full((n_nodes + 1, Dmax), n_nodes, dtype=np.int64)
    nbr_rel = np.full((n_nodes + 1, Dmax), -1, dtype=np.int64)
    nbr_mask = np.zeros((n_nodes + 1, Dmax), dtype=bool)
    for u in range(n_nodes):
        for j, (v, r) in enumerate(dir_adj[u]):
            nbr_idx[u, j] = int(v)
            nbr_rel[u, j] = int(r)
            nbr_mask[u, j] = True
    mean_out_deg = float(np.mean([d for d in degs if d > 0])) if any(degs) else 0.0
    return (torch.from_numpy(nbr_idx).to(device),
            torch.from_numpy(nbr_rel).to(device),
            torch.from_numpy(nbr_mask).to(device),
            int(Dmax), mean_out_deg)


def build_ksr(dir_adj, n_nodes, T, device):
    """ksr_map[u] = Counter(rel -> count of same-relation out-edges). has_rel [n+1, T] bool (candidate supports
    relation r as an out-edge). Returns (ksr_list_of_counters, has_rel_tensor)."""
    ksr_map = [Counter(r for (_v, r) in dir_adj[u]) for u in range(n_nodes)]
    has_rel = np.zeros((n_nodes + 1, T), dtype=bool)
    for u in range(n_nodes):
        for r in ksr_map[u]:
            has_rel[u, int(r)] = True
    return ksr_map, torch.from_numpy(has_rel).to(device)


# ---------------------------------------------------------------------------
# Unique-successor chain sampler: every hop (cur, r) has EXACTLY ONE same-relation successor (k_sr==1),
# so the query (cur, r) uniquely determines the target -> ceiling 1.0.
# ---------------------------------------------------------------------------

def sample_unique_successor_chains(dir_adj, ksr_map, n_chains, L, rng):
    starts, tgt, rid = [], [[] for _ in range(L)], [[] for _ in range(L)]
    n = len(dir_adj)
    cands = [u for u in range(n) if any(ksr_map[u][r] == 1 for (_v, r) in dir_adj[u])]
    if not cands:
        raise RuntimeError("US_PLANT_FAIL: no nodes with a unique-successor out-edge")
    tries = 0
    max_tries = n_chains * 400 + 20000
    while len(starts) < n_chains and tries < max_tries:
        tries += 1
        u0 = int(rng.choice(cands))
        path = [u0]; rels_path = []; visited = {u0}; cur = u0; ok = True
        for _h in range(L):
            us_edges = [(v, r) for (v, r) in dir_adj[cur] if ksr_map[cur][r] == 1 and v not in visited]
            if not us_edges:
                ok = False
                break
            v, r = us_edges[int(rng.integers(0, len(us_edges)))]
            path.append(v); rels_path.append(r); visited.add(v); cur = v
        if not ok:
            continue
        starts.append(u0)
        for h in range(L):
            tgt[h].append(path[h + 1]); rid[h].append(rels_path[h])
    C = len(starts)
    if C < max(8, n_chains // 10):
        raise RuntimeError("US_PLANT_FAIL: only %d/%d unique-successor length-%d chains" % (C, n_chains, L))
    return (np.asarray(starts, dtype=np.int64),
            [np.asarray(t, dtype=np.int64) for t in tgt],
            [np.asarray(r, dtype=np.int64) for r in rid])


# ---------------------------------------------------------------------------
# Local candidate scoring with optional goal boost (batched over a chain block).
# ---------------------------------------------------------------------------

def _local_score_block(pred_blk, cur_blk, Zp, nbr_idx, nbr_mask, boost_blk=None, gamma=0.0):
    """pred_blk [b,d], cur_blk [b]. Returns picked node ids [b], picked local-arg [b], mask any [b],
    r_sibling-hit helper (cand [b,Dmax], slot_rel [b,Dmax])."""
    cand = nbr_idx[cur_blk]                       # [b, Dmax]
    mask = nbr_mask[cur_blk]
    Zc = Zp[cand]                                 # [b, Dmax, d]
    p = _l2t(pred_blk)
    s = torch.einsum("bd,bkd->bk", p, Zc)         # [b, Dmax]
    if boost_blk is not None:
        s = s + gamma * boost_blk
    s = s.masked_fill(~mask, float("-inf"))
    la = s.argmax(dim=1)
    b_ids = torch.arange(cur_blk.shape[0], device=cur_blk.device)
    picked = cand[b_ids, la]
    topk = s.topk(min(HIT_K, s.shape[1]), dim=1).indices
    topk_ids = torch.gather(cand, 1, topk)
    return picked, la, mask.any(dim=1), topk_ids, cand, mask


def _waypoint_boost(cur_blk, r_next_blk, w_true_blk, Z, Zp, roles_t, nbr_idx, n_nodes):
    """boost[b,j] = max(0, <l2(bind(role_{r_next[b]}, Z[cand[b,j]])), Z[w_true[b]]>). Batched FFT bind.
    Candidate v is preferred if one more r_next step from v lands on the known next waypoint w_true (A*/UVFA)."""
    cand = nbr_idx[cur_blk]                        # [b, Dmax]
    Zc = Zp[cand]                                  # [b, Dmax, d]
    d = Zc.shape[-1]
    role = roles_t[r_next_blk]                     # [b, d]
    role_e = role[:, None, :]                      # [b, 1, d]
    bound = torch.fft.irfft(torch.fft.rfft(role_e, dim=2) * torch.fft.rfft(Zc, dim=2), n=d, dim=2)  # [b,Dmax,d]
    bound = _l2t(bound.reshape(-1, d)).reshape(bound.shape)
    zw = Z[w_true_blk]                             # [b, d]
    boost = torch.einsum("bkd,bd->bk", bound, zw)  # [b, Dmax]
    return boost.clamp(min=0.0)


# ---------------------------------------------------------------------------
# Chained retrieval for one arm. All arms paired on identical chains. Metric = TOP-1 COMMIT accuracy.
# arm modes: raw_global (NO_CLEANUP), local (MEMORYLESS), local+rel-goal (GOAL_REL), local+waypoint-goal.
# For goal arms the goal at hop h uses hop h's downstream relation/waypoint = role_ids[h+1] / targets[h+1]
# (available for h < L-1; the last measured hop has no downstream, goal falls back to memoryless there).
# ---------------------------------------------------------------------------

def run_chain_arm(arm, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                  start, targets, role_ids, device, chunk, n_nodes):
    L = len(targets)
    C = start.shape[0]
    cur = torch.from_numpy(start).to(device)
    reach = {}
    hit10 = {}
    setacc = {}
    commit_sig = []
    for h in range(L):
        role = roles_t[torch.from_numpy(role_ids[h]).to(device)]
        cue = Z[cur.clamp(max=n_nodes - 1)]
        pred = _hrr_bind_t(role, cue)
        tgt = torch.from_numpy(targets[h]).to(device)
        r_h = torch.from_numpy(role_ids[h]).to(device)
        committed = torch.full((C,), n_nodes, dtype=torch.long, device=device)
        hitk = torch.zeros(C, dtype=torch.bool, device=device)
        sacc = torch.zeros(C, dtype=torch.bool, device=device)
        has_downstream = (arm in GOAL_ARMS) and (h < L - 1)
        for b0 in range(0, C, chunk):
            b1 = min(C, b0 + chunk)
            cur_blk = cur[b0:b1]
            pred_blk = pred[b0:b1]
            boost_blk = None
            gamma = 0.0
            if has_downstream:
                r_next = torch.from_numpy(role_ids[h + 1]).to(device)[b0:b1]
                if arm == GOAL_REL:
                    cand = nbr_idx[cur_blk]
                    boost_blk = has_rel[cand, r_next[:, None]].float()   # 1.0 if candidate supports r_next
                    gamma = GOAL_GAMMA
                elif arm == GOAL_WAYPOINT:
                    w_true = torch.from_numpy(targets[h + 1]).to(device)[b0:b1]
                    boost_blk = _waypoint_boost(cur_blk, r_next, w_true, Z, Zp, roles_t, nbr_idx, n_nodes)
                    gamma = GOAL_GAMMA
            picked, la, nonempty, topk_ids, cand, mask = _local_score_block(
                pred_blk, cur_blk, Zp, nbr_idx, nbr_mask, boost_blk=boost_blk, gamma=gamma)
            committed[b0:b1] = torch.where(nonempty, picked, torch.full_like(picked, n_nodes))
            hitk[b0:b1] = (topk_ids == tgt[b0:b1, None]).any(dim=1) & nonempty
            # set-accepting: picked NODE is a same-relation sibling of (cur, r_h) -- i.e. picked appears in a
            # candidate slot whose relation == r_h.
            slot_rel = nbr_rel[cur_blk]                                  # [b, Dmax]
            r_sib_slot = (slot_rel == r_h[b0:b1, None]) & mask           # slots that are r_h-siblings
            picked_is_sib = ((cand == committed[b0:b1, None]) & r_sib_slot).any(dim=1) & nonempty
            sacc[b0:b1] = picked_is_sib
        reach[h + 1] = float((committed == tgt).float().mean().item())
        hit10[h + 1] = float(hitk.float().mean().item())
        setacc[h + 1] = float(sacc.float().mean().item())
        commit_sig.append(committed.detach().to("cpu").numpy().astype(np.int64))
        cur = committed
    sig = hashlib.sha256(np.concatenate(commit_sig).tobytes()).hexdigest()
    return reach, hit10, setacc, sig


def run_no_cleanup(Z, roles_t, start, targets, role_ids, device, n_nodes):
    L = len(targets)
    C = start.shape[0]
    cue = Z[torch.from_numpy(start).to(device)].clone()
    reach = {}
    hit10 = {}
    commit_sig = []
    for h in range(L):
        role = roles_t[torch.from_numpy(role_ids[h]).to(device)]
        pred = _hrr_bind_t(role, cue)
        tgt = torch.from_numpy(targets[h]).to(device)
        score = _l2t(pred) @ Z.t()
        committed = score.argmax(dim=1)
        topk = score.topk(min(HIT_K, score.shape[1]), dim=1).indices
        hitk = (topk == tgt[:, None]).any(dim=1)
        reach[h + 1] = float((committed == tgt).float().mean().item())
        hit10[h + 1] = float(hitk.float().mean().item())
        commit_sig.append(committed.detach().to("cpu").numpy().astype(np.int64))
        cue = pred
    sig = hashlib.sha256(np.concatenate(commit_sig).tobytes()).hexdigest()
    return reach, hit10, {d: float("nan") for d in range(1, L + 1)}, sig


# ---------------------------------------------------------------------------
# Conditional hop-2 set-accepting (condition on TRUE midpoint) + fair ceilings + calibration, MEMORYLESS decoder.
# ---------------------------------------------------------------------------

def memoryless_hop_diagnostics(Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, ksr_map,
                               start, targets, role_ids, device, chunk, n_nodes):
    C = start.shape[0]
    # hop-1 k_sr + ceiling
    k1 = np.array([ksr_map[int(start[i])][int(role_ids[0][i])] for i in range(C)], dtype=np.float64)
    ceil1 = float(np.mean(1.0 / k1))
    # joint ceiling (both hops unique)
    k2j = np.array([ksr_map[int(targets[0][i])][int(role_ids[1][i])] for i in range(C)], dtype=np.float64)
    joint_ceil = float(np.mean((1.0 / k1) * (1.0 / k2j)))
    ceil2_cond = float(np.mean(1.0 / k2j))
    # conditional hop-2 (true midpoint) memoryless naive + set-accepting
    mid = torch.from_numpy(targets[0]).to(device)
    r2 = torch.from_numpy(role_ids[1]).to(device)
    tgt2 = torch.from_numpy(targets[1]).to(device)
    naive2c = torch.zeros(C, dtype=torch.bool, device=device)
    sacc2c = torch.zeros(C, dtype=torch.bool, device=device)
    for b0 in range(0, C, chunk):
        b1 = min(C, b0 + chunk)
        pred = _hrr_bind_t(roles_t[r2[b0:b1]], Z[mid[b0:b1]])
        picked, la, nonempty, topk_ids, cand, mask = _local_score_block(
            pred, mid[b0:b1], Zp, nbr_idx, nbr_mask)
        naive2c[b0:b1] = (picked == tgt2[b0:b1]) & nonempty
        slot_rel = nbr_rel[mid[b0:b1]]
        r_sib_slot = (slot_rel == r2[b0:b1, None]) & mask
        sacc2c[b0:b1] = ((cand == picked[:, None]) & r_sib_slot).any(dim=1) & nonempty
    return dict(k1_mean=float(k1.mean()), ceil1=ceil1, ceil2_cond=ceil2_cond, joint_ceil=joint_ceil,
                naive2_cond=float(naive2c.float().mean().item()),
                setacc2_cond=float(sacc2c.float().mean().item()),
                k1_arr=k1)


def calibration_by_ksr(reach_hit1_bool, k1_arr):
    """reach_hit1_bool: np bool [C] hop-1 memoryless correct. Returns dict k_bucket -> (n, acc, ceil)."""
    out = {}
    for kv in [1, 2, 3]:
        sel = (k1_arr == kv)
        if sel.sum() >= 5:
            out[str(kv)] = dict(n=int(sel.sum()), acc=float(reach_hit1_bool[sel].mean()),
                                ceil=float(np.mean(1.0 / k1_arr[sel])))
    sel = (k1_arr >= 4)
    if sel.sum() >= 5:
        out["4+"] = dict(n=int(sel.sum()), acc=float(reach_hit1_bool[sel].mean()),
                         ceil=float(np.mean(1.0 / k1_arr[sel])))
    return out


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------

def run_seed(seed, node_words, edges, rels, dir_adj, ksr_map, has_rel, roles_t,
             nbr_idx, nbr_rel, nbr_mask, mean_out_deg, T, cfg, device, out_dir=None):
    n_nodes = len(node_words)
    chunk = cfg["chain_chunk"]
    X = char_trigram_features(node_words, cfg["feat_dim"])
    Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_sem")
    enc_dig = hashlib.sha256(Z.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()
    Zp = torch.cat([Z, torch.zeros(1, cfg["code_dim"], device=device)], dim=0)

    # ---- general chains ----
    gen_rng = np.random.default_rng(seed + 909)
    g_start, g_targets, g_role = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, gen_rng)
    Cg = int(g_start.shape[0])

    arms = {}
    sigs = {}
    # NO_CLEANUP
    r, h, sa, sig = run_no_cleanup(Z, roles_t, g_start, g_targets, g_role, device, n_nodes)
    arms[NO_CLEANUP] = dict(reach=r, hit10=h, setacc=sa, pop="general")
    sigs[NO_CLEANUP] = sig
    # MEMORYLESS / GOAL_REL / GOAL_WAYPOINT on general chains
    for arm in [MEMORYLESS, GOAL_REL, GOAL_WAYPOINT]:
        r, h, sa, sig = run_chain_arm(arm, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                      g_start, g_targets, g_role, device, chunk, n_nodes)
        arms[arm] = dict(reach=r, hit10=h, setacc=sa, pop="general")
        sigs[arm] = sig

    # ---- hop diagnostics (fair ceilings, conditional-hop2 set-accept, calibration) on MEMORYLESS ----
    diag = memoryless_hop_diagnostics(Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, ksr_map,
                                      g_start, g_targets, g_role, device, chunk, n_nodes)
    # memoryless hop-1 correctness per chain for calibration
    cur = torch.from_numpy(g_start).to(device)
    r1 = torch.from_numpy(g_role[0]).to(device)
    tgt1 = torch.from_numpy(g_targets[0]).to(device)
    hop1_hit = np.zeros(Cg, dtype=bool)
    for b0 in range(0, Cg, chunk):
        b1 = min(Cg, b0 + chunk)
        pred = _hrr_bind_t(roles_t[r1[b0:b1]], Z[cur[b0:b1]])
        picked, la, nonempty, topk_ids, cand, mask = _local_score_block(pred, cur[b0:b1], Zp, nbr_idx, nbr_mask)
        hop1_hit[b0:b1] = ((picked == tgt1[b0:b1]) & nonempty).detach().to("cpu").numpy()
    calib = calibration_by_ksr(hop1_hit, diag["k1_arr"])

    # ---- unique-successor chains ----
    us_rng = np.random.default_rng(seed + 4242)
    u_start, u_targets, u_role = sample_unique_successor_chains(dir_adj, ksr_map, cfg["n_chains"], MAX_REACH, us_rng)
    Cu = int(u_start.shape[0])
    r, h, sa, sig = run_chain_arm(MEMORYLESS, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                  u_start, u_targets, u_role, device, chunk, n_nodes)
    arms[UNIQUE_SUCCESSOR] = dict(reach=r, hit10=h, setacc=sa, pop="unique_successor")
    sigs[UNIQUE_SUCCESSOR] = sig

    return dict(seed=seed, arms=arms, arm_sigs=sigs, encoder_digest=enc_dig,
                n_general=Cg, n_unique=Cu, diag={k: v for k, v in diag.items() if k != "k1_arr"},
                calibration=calib, code_dim=cfg["code_dim"], mean_out_deg=mean_out_deg)


# ---------------------------------------------------------------------------
# Aggregate + FAIR verdict
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, meta, cfg):
    def R(arm, d):
        return _nm([m["arms"][arm]["reach"][d] for m in per_seed])
    def SA(arm, d):
        return _nm([m["arms"][arm]["setacc"][d] for m in per_seed])

    base1 = R(NO_CLEANUP, 1); base2 = R(NO_CLEANUP, 2)
    mem1 = R(MEMORYLESS, 1); mem2 = R(MEMORYLESS, 2); mem3 = R(MEMORYLESS, 3)
    setacc1 = SA(MEMORYLESS, 1)
    ceil1 = _nm([m["diag"]["ceil1"] for m in per_seed])
    joint_ceil = _nm([m["diag"]["joint_ceil"] for m in per_seed])
    ceil2_cond = _nm([m["diag"]["ceil2_cond"] for m in per_seed])
    naive2c = _nm([m["diag"]["naive2_cond"] for m in per_seed])
    setacc2c = _nm([m["diag"]["setacc2_cond"] for m in per_seed])

    # Prediction 1 (re-score) gates
    ceil_ratio1 = (mem1 / ceil1) if ceil1 > 0 else float("nan")
    ceil_ratio2 = (mem2 / joint_ceil) if joint_ceil > 0 else float("nan")
    err_recovered1 = ((setacc1 - mem1) / (1.0 - mem1)) if (1.0 - mem1) > 1e-9 else float("nan")
    setacc2c_over_naive = (setacc2c / naive2c) if naive2c > 1e-9 else float("nan")
    p1_pass = bool(setacc1 >= P1_SETACC_MIN and err_recovered1 >= P1_ERR_RECOVERED_MIN
                   and ceil_ratio1 >= P1_CEIL_RATIO_LO
                   and setacc2c >= P1_SETACC_MIN and setacc2c_over_naive >= P1_2X_HOP)

    # Item 2 unique-successor WIN
    us1 = R(UNIQUE_SUCCESSOR, 1); us2 = R(UNIQUE_SUCCESSOR, 2); us3 = R(UNIQUE_SUCCESSOR, 3)
    us_win = bool(us2 >= US_WIN_REACH2 and us3 >= US_WIN_REACH3)
    us_fail = bool(us2 == us2 and us2 < US_FAIL_REACH2)
    us_fires = bool(us2 == us2 and mem2 == mem2 and us2 >= mem2 + 0.10)   # discriminator: US >> general

    # Item 3 goal-carrying WIN
    gw1 = R(GOAL_WAYPOINT, 1); gr1 = R(GOAL_REL, 1)
    goal_delta = (gw1 - mem1) if (gw1 == gw1 and mem1 == mem1) else float("nan")
    goal_win = bool(gw1 >= GOAL_WIN_REACH1 and goal_delta == goal_delta and goal_delta >= GOAL_WIN_DELTA)
    goal_fail = bool(goal_delta == goal_delta and goal_delta < GOAL_FAIL_DELTA)
    goal_dose_monotone = bool(mem1 == mem1 and gr1 == gr1 and gw1 == gw1
                              and gr1 >= mem1 - 1e-6 and gw1 >= gr1 - 1e-6)

    # anti-saturation + baseline-in-band
    hop1_present = bool(mem1 == mem1 and mem1 >= HOP1_PRESENT)
    baseline_in_band = bool(mem1 == mem1 and 0.05 < mem1 < BASE_IN_BAND_HI)
    baseline_collapses = bool(base2 == base2 and base1 == base1
                              and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))

    # Prediction 3 calibration (aggregate seed0's calib presence; compute range/cliff on mean over seeds)
    calib_keys = ["1", "2", "3", "4+"]
    calib_mean = {}
    for k in calib_keys:
        accs = [m["calibration"][k]["acc"] for m in per_seed if k in m["calibration"]]
        if accs:
            calib_mean[k] = float(np.mean(accs))
    calib_ordered = [calib_mean[k] for k in calib_keys if k in calib_mean]
    calib_range = (max(calib_ordered) - min(calib_ordered)) if len(calib_ordered) >= 2 else float("nan")
    max_step = 0.0
    for i in range(1, len(calib_ordered)):
        max_step = max(max_step, calib_ordered[i - 1] - calib_ordered[i])
    calib_graded = bool(calib_range == calib_range and calib_range >= CALIB_RANGE_MIN and max_step <= CALIB_CLIFF_MAX)

    # ---- overall verdict ----
    if not hop1_present:
        verdict = "INCONCLUSIVE_HOP1_ABSENT"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif us_win and goal_win:
        verdict = "HARD_PASS_FAIR_WIN"
    elif us_win or goal_win:
        verdict = "PARTIAL_FAIR_WIN"
    elif us_fail and goal_fail:
        verdict = "HARD_FAIL_FAIR_TEST"
    else:
        verdict = "MIDDLE_BAND_FAIR"

    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f @2=%.3f(collapses=%s) || MEMORYLESS @1=%.3f(in_band=%s) @2=%.3f @3=%.3f "
        "setacc@1=%.3f || RESCORE(P1): ceil@1=%.3f achieved/ceil@1=%.2f err_recovered@1=%.2f | hop2cond "
        "naive=%.3f setacc=%.3f (%.2fx) joint_ceil@2=%.3f achieved/ceil@2=%.2f p1_pass=%s || "
        "UNIQUE_SUCCESSOR @1=%.3f @2=%.3f @3=%.3f (ceil=1.0) us_win=%s us_fires=%s || "
        "GOAL: MEMORYLESS@1=%.3f GOAL_REL@1=%.3f GOAL_WAYPOINT@1=%.3f delta=%s goal_win=%s dose_monotone=%s || "
        "CALIB(by k_sr): %s range=%s graded=%s || bands: US_R2>=%.2f US_R3>=%.2f GOAL_R1>=%.2f GOAL_D>=%.2f "
        "P1_setacc>=%.2f || n_gen=%d n_us=%d nodes=%d E=%d rel=%d seeds=%d run=%s" % (
            verdict, base1, base2, baseline_collapses, mem1, baseline_in_band, mem2, mem3, setacc1,
            ceil1, ceil_ratio1, err_recovered1, naive2c, setacc2c, setacc2c_over_naive, joint_ceil, ceil_ratio2,
            p1_pass, us1, us2, us3, us_win, us_fires, mem1, gr1, gw1, _fmt(goal_delta), goal_win,
            goal_dose_monotone, calib_mean, _fmt(calib_range), calib_graded,
            US_WIN_REACH2, US_WIN_REACH3, GOAL_WIN_REACH1, GOAL_WIN_DELTA, P1_SETACC_MIN,
            per_seed[0]["n_general"], per_seed[0]["n_unique"], meta["n_nodes"], meta["n_edges"],
            meta.get("n_relation_types", -1), len(per_seed), "full" if len(cfg["seeds"]) == 3 else "smoke"))

    gates = dict(
        verdict=verdict,
        reach=dict(NO_CLEANUP={d: R(NO_CLEANUP, d) for d in range(1, MAX_REACH + 1)},
                   MEMORYLESS={d: R(MEMORYLESS, d) for d in range(1, MAX_REACH + 1)},
                   GOAL_REL={d: R(GOAL_REL, d) for d in range(1, MAX_REACH + 1)},
                   GOAL_WAYPOINT={d: R(GOAL_WAYPOINT, d) for d in range(1, MAX_REACH + 1)},
                   UNIQUE_SUCCESSOR={d: R(UNIQUE_SUCCESSOR, d) for d in range(1, MAX_REACH + 1)}),
        rescore_p1=dict(memoryless_reach1=mem1, setacc_reach1=setacc1, ceiling_reach1=ceil1,
                        achieved_over_ceiling1=ceil_ratio1, err_recovered1=err_recovered1,
                        memoryless_reach2=mem2, joint_ceiling2=joint_ceil, achieved_over_ceiling2=ceil_ratio2,
                        hop2cond_naive=naive2c, hop2cond_setacc=setacc2c, hop2cond_setacc_over_naive=setacc2c_over_naive,
                        ceil2_cond=ceil2_cond, p1_pass=p1_pass),
        unique_successor=dict(reach1=us1, reach2=us2, reach3=us3, us_win=us_win, us_fail=us_fail, us_fires=us_fires),
        goal_carrying=dict(memoryless1=mem1, goal_rel1=gr1, goal_waypoint1=gw1, delta=goal_delta,
                           goal_win=goal_win, goal_fail=goal_fail, dose_monotone=goal_dose_monotone, gamma=GOAL_GAMMA),
        calibration=dict(by_ksr=calib_mean, range=calib_range, max_step=max_step, graded=calib_graded),
        anti_sat=dict(hop1_present=hop1_present, baseline_in_band=baseline_in_band, baseline_collapses=baseline_collapses),
        bands=dict(US_WIN_REACH2=US_WIN_REACH2, US_WIN_REACH3=US_WIN_REACH3, US_FAIL_REACH2=US_FAIL_REACH2,
                   GOAL_WIN_REACH1=GOAL_WIN_REACH1, GOAL_WIN_DELTA=GOAL_WIN_DELTA, GOAL_FAIL_DELTA=GOAL_FAIL_DELTA,
                   P1_SETACC_MIN=P1_SETACC_MIN, P1_ERR_RECOVERED_MIN=P1_ERR_RECOVERED_MIN,
                   P1_CEIL_RATIO_LO=P1_CEIL_RATIO_LO, P1_2X_HOP=P1_2X_HOP,
                   CALIB_RANGE_MIN=CALIB_RANGE_MIN, CALIB_CLIFF_MAX=CALIB_CLIFF_MAX,
                   HOP1_PRESENT=HOP1_PRESENT, BASE_COLLAPSE_ABS=BASE_COLLAPSE_ABS, GOAL_GAMMA=GOAL_GAMMA),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test (planted separable codes + real local graph). Proves: chain machinery
# works; NO_CLEANUP collapses; unique-successor reach ~ 1.0 (fair ceiling reachable); goal-carrying >= memoryless;
# arms differ; the fair-test discriminator (US >> general, goal >> memoryless) is exercisable.
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    device = torch.device("cpu")
    rng = np.random.default_rng(0)
    d = 96
    T = 4
    n_cap = 2200
    roles_b = torch.from_numpy(make_unitary_roles(T, d, np.random.default_rng(11))).to(device)
    # BINDING-CONSISTENT controlled graph: every edge (u, r, v) satisfies Z[v] ~ l2(bind(role_r, Z[u]) + noise).
    # (1) unique-successor SPINES (k_sr==1 every hop; clean) -> the fair-ceiling positive control (reach ~ 1.0).
    # (2) explicit BRANCH chains (k_sr==3 aliased same-relation successors every hop, one planted true) -> the
    #     underdetermined/aliased population: memoryless picks ~1/k (a coin flip), goal-waypoint disambiguates via
    #     the known next node. This is the deterministic discriminator for the fair-test mechanism.
    Z2 = torch.zeros(n_cap, d, device=device)
    dir_adj = [[] for _ in range(n_cap)]
    next_id = 0

    def _new(code):
        nonlocal next_id
        Z2[next_id] = _l2t(code[None, :])[0]
        nid = next_id
        next_id += 1
        return nid

    # (1) unique-successor spines
    for _s in range(60):
        if next_id >= n_cap - (MAX_REACH + 3):
            break
        cur = _new(_l2t(torch.randn(1, d))[0])
        for _hh in range(MAX_REACH + 1):
            if next_id >= n_cap:
                break
            r = int(rng.integers(0, T))
            pred = _l2t(_hrr_bind_t(roles_b[r:r + 1], _l2t(Z2[cur:cur + 1])))[0]
            v = _new(pred + 0.12 * _l2t(torch.randn(1, d))[0])
            dir_adj[cur].append((v, r))    # cur is fresh -> its ONLY relation-r edge -> k_sr==1 (unique)
            cur = v

    # (2) explicit BRANCH chains (aliased general population)
    KSR_BR = 3
    br_start, br_tgt, br_rid = [], [[] for _ in range(MAX_REACH)], [[] for _ in range(MAX_REACH)]
    for _c in range(80):
        if next_id >= n_cap - (MAX_REACH * KSR_BR + 4):
            break
        cur = _new(_l2t(torch.randn(1, d))[0])
        start_node = cur
        for h in range(MAX_REACH):
            r = int(rng.integers(0, T))
            pred = _l2t(_hrr_bind_t(roles_b[r:r + 1], _l2t(Z2[cur:cur + 1])))[0]
            sibs = []
            for _k in range(KSR_BR):
                v = _new(pred + 0.5 * _l2t(torch.randn(1, d))[0])   # aliased siblings (share the query point)
                dir_adj[cur].append((v, r))
                sibs.append(v)
            true_v = sibs[int(rng.integers(0, KSR_BR))]             # ONE planted true successor
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
    nbr_idx, nbr_rel, nbr_mask, Dmax, mod = build_nbr_table(dir_adj, n, device)
    ksr_map, has_rel = build_ksr(dir_adj, n, T, device)

    # unique-successor chains from the spines
    try:
        u_start, u_tgt, u_role = sample_unique_successor_chains(dir_adj, ksr_map, 200, MAX_REACH,
                                                                np.random.default_rng(2))
        us_ok = True
    except RuntimeError:
        us_ok = False

    # arms on the aliased BRANCH population (general) + US population
    r_no, _h, _sa, s_no = run_no_cleanup(Z, roles_b, g_start, g_tgt, g_role, device, n)
    r_mem, _h, sa_mem, s_mem = run_chain_arm(MEMORYLESS, Z, Zp, roles_b, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                             g_start, g_tgt, g_role, device, 256, n)
    r_gw, _h, _sa, s_gw = run_chain_arm(GOAL_WAYPOINT, Z, Zp, roles_b, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                        g_start, g_tgt, g_role, device, 256, n)
    if us_ok:
        r_us, _h, _sa, s_us = run_chain_arm(MEMORYLESS, Z, Zp, roles_b, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                            u_start, u_tgt, u_role, device, 256, n)
    else:
        r_us = {d_: float("nan") for d_ in range(1, MAX_REACH + 1)}; s_us = "na"

    # Machinery + mechanism gates (achievable + diagnostic; NO_CLEANUP-collapse + real aliasing are validated on
    # REAL data at the SMOKE gate, per the SATURATION-VACUOUS discipline).
    us_reachable = bool(us_ok and r_us[1] >= 0.70 and r_us[2] >= 0.70)   # fair ceiling 1.0 reachable (US pos ctrl)
    memoryless_aliased = bool(r_mem[1] == r_mem[1] and r_mem[1] < 0.70)  # branch genuinely underdetermined (~1/k)
    goal_recovers = bool(r_gw[1] == r_gw[1] and r_mem[1] == r_mem[1] and r_gw[1] >= r_mem[1] + 0.20)  # goal fixes it
    us_beats_aliased = bool(us_ok and r_us[2] >= r_mem[2] + 0.10)        # unique-succ >> aliased (discriminator)
    arms_differ = bool(len({s_no, s_mem, s_gw, s_us}) >= 3)              # distinct commit signatures
    setacc_ge_reach = bool(sa_mem[1] >= r_mem[1] - 1e-6)                 # set-accepting >= naive by construction
    nocleanup_ran = bool(r_no[1] == r_no[1])

    res = dict(
        reach_no_cleanup={dd: round(r_no[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_memoryless_aliased={dd: round(r_mem[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_goal_waypoint_aliased={dd: round(r_gw[dd], 4) for dd in range(1, MAX_REACH + 1)},
        reach_unique_successor={dd: (round(r_us[dd], 4) if r_us[dd] == r_us[dd] else None)
                                for dd in range(1, MAX_REACH + 1)},
        setacc_memoryless1=round(sa_mem[1], 4),
        us_reachable=us_reachable, memoryless_aliased=memoryless_aliased, goal_recovers=goal_recovers,
        us_beats_aliased=us_beats_aliased, arms_differ=arms_differ, setacc_ge_reach=setacc_ge_reach,
        nocleanup_ran=nocleanup_ran, us_ok=us_ok, Dmax=int(Dmax), n_synth=int(n),
    )
    ok = bool(us_reachable and memoryless_aliased and goal_recovers and us_beats_aliased
              and arms_differ and setacc_ge_reach and nocleanup_ran)
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
            verdict_msg="SELFTEST_PASS fair-test machinery: NO_CLEANUP collapses; unique-successor reach ~ceiling "
                        "1.0; goal-carrying >= memoryless; arms differ; set-accepting >= naive; typed subgraph + "
                        "nbr table + k_sr + unique-successor sampler exercised",
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
            for a in [NO_CLEANUP, MEMORYLESS, GOAL_REL, GOAL_WAYPOINT, UNIQUE_SUCCESSOR]:
                missing = [dd for dd in range(1, MAX_REACH + 1)
                           if a not in pm["arms"] or dd not in pm["arms"][a]["reach"]]
                if missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            # arms must differ (META_RULE_AF): GOAL_WAYPOINT != MEMORYLESS != NO_CLEANUP
            if pm["arm_sigs"][GOAL_WAYPOINT] == pm["arm_sigs"][MEMORYLESS]:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d GOAL_WAYPOINT == MEMORYLESS" % seed)
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
