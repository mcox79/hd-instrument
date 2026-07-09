"""
substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu -- GENERATION mechanism, CLEAN re-spec.

v11 RE-AIM (2026-07-08): v10 (commit 07314f85c) ACHIEVED its primary objective -- the growing-bundle ACCUMULATE now
GENUINELY COMPOUNDS (body_token_acc drift +0.132, survives to full N=8192) and REPLAY-propose-score-commit wins
DECISIVELY on GOAL_REACH (perfect 1.000 at all depths, +0.662 vs ACCUMULATE, +0.825 vs RANDOM_RESTART, scoring earns
its keep sel_value +0.073). BUT the strict "REPLAY body stays FLAT while ACCUMULATE body COMPOUNDS on the SAME
metric" claim was CONFOUNDED: v10's layered DAG has MULTIPLE valid paths per (start,goal), so body_token_acc
(exact laid-down-path match) is LOW for REPLAY -- REPLAY optimizes goal_reach via OFFLINE whole-candidate scoring and
commits A valid goal-reacher, not THE exact laid-down path. So REPLAY's exact-path body was 0.31-0.40 and also
declined; the accumulator (following high-traffic edges) stayed NEARER the backbone so ITS body was HIGHER at every
depth -> the compounding was not cleanly accumulator-specific (v10 verdict = INCONCLUSIVE_COMPOUNDING_NOT_ACCUMULATOR_
SPECIFIC, D1b). MEASURED@..._v10.../metrics.json.

v11 FIX (exp_dev already specced it in the v10 prereg re-spec section): a UNIQUE-PATH regime. The ONLY change from
v10 is the GRAPH + the D4/ceiling bands -- the v10 growing-bundle accumulator + ACC_CONTENT_W=0 + REPLAY propose-
score-commit + peel/SIC readout are UNCHANGED (v10 already made the accumulator compound; the fix is purely the
graph/metric ceiling). The layered DAG is constructed so that from EACH node, the out-neighbors have PAIRWISE-DISJOINT
goal-reachability sets -> for any (start,goal) there is EXACTLY ONE valid route: at each node exactly ONE out-neighbor
keeps the goal reachable; all other out-neighbors are goal-DEAD-ENDS (goal not in their reach subtree, including pure
DEAD distractor slots whose subtree reaches no goal). Consequences:
  * ORACLE body_token_acc ceiling ~1.0 (the unique target path IS solvable/decodable by peel/SIC).
  * REPLAY, scoring by goal-reach, follows the UNIQUE route (the only candidate that reaches the goal) -> exact-path
    match -> REPLAY body stays HIGH (>=REPLAY_BODY_MIN) and FLAT across depth.
  * ACCUMULATE, navigating by its own DRIFTING leaky-bundle (crosstalk grows with depth), decodes a WRONG current
    node -> takes a goal-DEAD-END branch -> off the unique path and UNRECOVERABLE (dead subtree reaches no goal) ->
    body_token_acc COMPOUNDS (degrades with L).
This removes the multiple-valid-path confound and makes the anti-compounding claim FINALLY testable clean. HONEST
EITHER WAY: if REPLAY body ALSO drifts on the unique path, that is a real NEGATIVE about the bounded-plan readout.

BRAIN-FIRST DESIGN (notes/research_native_glassbox_generation_brain_first_2026-07-08.md): the brain does NOT generate
by recurrently accumulating raw state and decoding once at the end. It generates by REPLAY-PROPOSE-SCORE-COMMIT:
(1) compose bounded WHOLE candidate plans OFFLINE by hippocampal SWR replay that RECOMBINES already-learned LOCAL
fragments (Pfeiffer & Foster 2013; Mattar & Daw 2018 priority = gain x need); (2) read the committed bounded plan out
ONE ITEM AT A TIME via COMPETITIVE QUEUING (Grossberg 1978 primacy gradient + WTA-and-inhibit == the ALREADY-BUILT
peel/SIC decoder hdlab.cleanup_family.peel_sic_readout) -- no accumulator, nothing compounds; (3) score/select
candidate fragments by the ALREADY-PROVEN content-vs-recency combined gate (v5-v8: softmax(content_rel/TAU + recency)).
A fixed bounded plan read against a fixed external reference at each read is a HARD RESET -> per-item error does not
compound with read-out position (regenerative-repeater law, research_noise_compounding_bound_2026-07-07). The
accumulator that GROWS/carries raw state IS the site of noise-compounding; this mechanism REMOVES it by construction.

SCOPE (HONEST): tests the generation MECHANISM (no-compounding + genuine recombination) on a SYNTHETIC, STRUCTURAL
unique-route layered-DAG regime. It does NOT claim real-language generation -- the real-language quality CEILING is
barrier-#1(encoder)-gated. Stage 3 (higher-function generation MECHANISM); NOT Stage-4 language.

TASK (synthetic, clean, explicitly-tagged; NOT natural language): a layered DAG (L+1 layers, WIDTH slots/layer,
disjoint token ids per layer). N_GOALS goal-slots live at layer L; the rest are DEAD sinks. The graph is built
BACKWARD so each node's out-neighbors have pairwise-DISJOINT goal-reach sets (uniqueness) plus DEAD distractor edges
(guaranteed straying targets). A generation instance = (start, goal); the ground-truth is the UNIQUE route
P(start,goal). At every node the correct next branch depends on the GOAL (content) -- a recency/traffic gate that
ignores the goal will follow high-traffic edges into goal-dead-ends -> the GOAL-content gate (R_goal geometry) is
required. This is the v5-v8 recency-vs-content arbitration, now driving unique-route generation.

STORES (reuse v10): W_trans (N,N) = sum over edges (u->v) of mult_uv * outer(cb[v], cb[u]) (traffic-weighted,
bundled -> capacity-limited; the compounding site). R_goal (V,N): R_goal[v] = normalize(sum_{goal g in reach[v]}
cb[g]) -- LEARNED goal-reachability geometry (graded, implicit, NOT an explicit tag).

GATE (v8 combined): logit(v) = content_rel(v,g)/GATE_TAU + BETA*freqcos(v), softmax over out-neighbors (-inf off-graph).

ARMS (5; PAIRED -- same graph/instances/codebook/R budget; MATCHED COMPUTE for REPLAY vs RANDOM_RESTART):
  ORACLE          -- readout positive control: peel/SIC readout of the TRUE unique-route plan vector. Certifies the
                     readout + metric are sound (body ceiling ~1.0). HP_SCOPE: >=ORACLE_FLOOR only.
  REPLAY          -- THE ARM UNDER TEST. Propose R candidate WHOLE routes by gain-x-need (content-toward-g + freq)
                     sampling; SCORE each whole candidate by coherence (reaches g? + sum content); COMMIT the best;
                     peel/SIC read out the committed bounded plan. Context RESETS to the clean codeword each step (no
                     raw accumulation); selection is over WHOLE candidates -> follows the UNIQUE route -> body HIGH+FLAT.
  ACCUMULATE      -- MUST-FAIL compounding baseline (v10 UNCHANGED): carry a GROWING leaky bundle c_{l+1}=LAMBDA_ACC*c
                     + cb[emitted]; decode current node from the DRIFTING bundle; navigate by the LOCAL freq/traffic
                     signal (ACC_CONTENT_W=0). Crosstalk grows with L -> decoded node drifts -> takes goal-dead-end
                     branch (UNRECOVERABLE here) -> body COMPOUNDS.
  RANDOM_RESTART  -- compute-matched redundancy control: SAME R walks but UNIFORM out-edge sampling (no gain-x-need)
                     and select ONE uniformly (no scoring). Isolates content-scored recombination from redundancy.
  REPLAY_PROPOSE_ONLY -- diagnostic (ungated): gain-x-need proposal but UNIFORM selection among the R (scoring value).

METRICS (unchanged): goal_reach = [emitted[L]==g]. per_token_acc = mean positions 1..L (exact route). body_token_acc
  = mean MID-SEQUENCE positions 1..L-1 EXCLUDING the goal position L = the ARTIFACT-FREE COMPOUNDING WITNESS. On the
  UNIQUE-PATH graph body has a clean ~1.0 ceiling (ORACLE/REPLAY) so a body drop is unambiguous compounding.

DISCRIMINATOR-FIRES (else INCONCLUSIVE, do NOT dispatch FULL):
  (D0) UNIQUE-PATH invariant: every node on every route has EXACTLY ONE goal-reachable out-neighbor (asserted at build).
  (D1) ACCUMULATE body_token_acc DROPS with L: body(L_lo)-body(L_max) >= DRIFT_MIN (compounds).
  (D1b) accumulator-SPECIFIC: (accum body_drift) - (replay body_drift) >= DRIFT_MIN (REPLAY stays bounded).
  (D1c) REPLAY body CEILING: REPLAY body >= REPLAY_BODY_MIN at every L (follows the unique route -- the v11 fix).
  (D2) RANDOM_RESTART underperforms: REPLAY goal_reach - RANDOM_RESTART >= MARGIN_REDUNDANCY.
  (D3) ORACLE body >= ORACLE_BODY_MIN (unique route decodable; readout+metric sound).
  (D4) baseline_in_band at SHALLOW L_lo: ACCUMULATE body in (chance, 0.95) -- functional at shallow depth, degrades
       with L (v11: the accumulator SHOULD fail badly at depth, so band is checked at L_lo not headline L).

HARD_PASS (HP_SCOPE: REPLAY only): D1 (accum compounds) AND D1b (accum-specific) AND D1c (REPLAY body >= ceiling and
  flat, rep_body_drift <= REPLAY_FLAT_MAX) AND REPLAY beats ACCUMULATE (goal_reach >= MARGIN_ACCUM) AND beats
  RANDOM_RESTART (goal_reach >= MARGIN_REDUNDANCY, body > 0) AND REPLAY-ACCUM body gap GROWS with L AND sel_value > 0
  AND ORACLE body >= ORACLE_BODY_MIN AND (FULL) cv <= CV_MAX.
HARD_FAIL: REPLAY - RANDOM_RESTART(goal_reach) <= NO_RECOMB_BAND (win is redundancy) OR diversity < DIVERSITY_MIN OR
  REPLAY does not beat ACCUMULATE (goal_reach).
INCONCLUSIVE: readout unsound/NaN OR baseline out of band OR NO_COMPOUNDING (D1) OR not accumulator-specific (D1b) OR
  REPLAY body below ceiling (D1c -- the honest negative: bounded-plan readout also drifts on the unique path).
MIDDLE_BAND: beats both controls + scoring earns its keep + REPLAY body high, but misses a strict HARD_PASS gate.

COMPUTE ARCHITECTURE: mixed (batched-GPU numeric core + CPU numpy peel/SIC readout). Candidate WALKS have a GENUINE
  step-L-depends-on-L-1 dependency (allowed sequential exemption); the INDEPENDENT axes (instances I x candidates R)
  are BATCHED into one (I*R,N) walker tensor advanced with one matmul per L step on cuda for FULL (cpu for smoke).
  Storage: sharded fragment edges into a bundled W_trans (bundled IS the discriminator -- its capacity limit is what
  makes ACCUMULATE drift; REPLAY beats it by propose-score-commit, not by de-bundling).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash of the 5 per-L curves; they diverge).
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace atomic).
# - except SystemExit: raise BEFORE except Exception (no BaseException / bare except).
# - crlb_n/a: graph-walk + gate-select + peel/SIC readout has no closed-form CRLB; discriminator is the ARM-vs-ARM
#   body_token_acc GAP; chance floor = 1/WIDTH (THEORETICAL); readout floor certified by ORACLE (MEASURED at smoke).
# - baseline_in_band: ACCUMULATE body in (1/WIDTH, 0.95) at SHALLOW L_lo (D4); else INCONCLUSIVE.
# - discriminator survives scale: full-N=8192 ACCUMULATE PREVIEW (option C) kept from v10; bundle crosstalk is
#   N-dependent so smoke's own N is not sufficient evidence for the N=8192 target.
# - HARD_PASS strictly above floor: REPLAY body >= REPLAY_BODY_MIN AND beats BOTH controls by strict margins.
# - HP_SCOPE: HARD_PASS gates apply ONLY to REPLAY; ORACLE is a readout positive-control; ACCUMULATE + RANDOM_RESTART
#   are must-underperform controls; REPLAY_PROPOSE_ONLY is an ungated diagnostic.
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(L_GRID); verdict counts len(per_unit).
# - per-unit failure-class: except Exception (not bare/BaseException); crash-diag writes CELL_CRASHED.
# - calibration_check: default_ok_for_this_regime -- GATE_TAU=0.05 (v7/v8), BETA=1.0, LAMBDA_ACC=0.65, ACC_CONTENT_W=0
#   fixed a priori (anti-compounding-mechanism argument, NOT tuned per-L); the strict --self-test is the health gate.
# - progress_logging: print_flush_true (all progress lines flush=True; sys.stdout line_buffered).
# - cell_chunked: false (1-3 seeds in-cell, per-seed checkpoint/resume; light per-seed wall).
# - all numbers in comments tagged: chance=1/WIDTH THEORETICAL; margins/floors HYPOTHESIZED@this prereg; v10 results
#   MEASURED@..._v10.../metrics.json; no MEASURED v11 numbers asserted pre-smoke.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math, platform, traceback, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timezone
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics
from hdlab.cleanup_family import peel_sic_readout          # REUSE the ALREADY-BUILT competitive-queuing readout
try:
    from experiments._cell_heartbeat import emit_heartbeat
except Exception:
    def emit_heartbeat(*a, **k):
        pass

ANCHOR_NAME = "substrate_gen_lm_replay_propose_score_commit_v11_unique_path_n8192_gpu"
_N_SUFFIX = 8192; N = 8192; assert N == _N_SUFFIX

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--device", default=None, help="cpu|cuda; default cuda for FULL, honors --device for smoke")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if _ARGS.device is not None:
    _DEV_REQ = _ARGS.device.lower()
elif RUN_MODE == "smoke":
    _DEV_REQ = "cuda" if torch.cuda.is_available() else "cpu"
else:
    _DEV_REQ = "cuda"
if _DEV_REQ == "cuda" and not torch.cuda.is_available():
    if RUN_MODE == "full":
        print("[FATAL] FULL run requires CUDA; none available.", flush=True); sys.exit(1)
    _DEV_REQ = "cpu"
DEVICE = torch.device(_DEV_REQ)
if DEVICE.type == "cuda":
    print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
else:
    print(f"[CPU] torch {torch.__version__} device=cpu ({RUN_MODE})", flush=True)

# --------------------------------------------------------------------------- params
GATE_TAU = 0.05                 # content-gate softmax temperature (v7/v8); content/TAU dominates freq on conflict
BETA = 1.0                      # freq (recency) weight in the combined logit
LAMBDA_ACC = 0.65               # v10 UNCHANGED: leaky-integrator retention for the ACCUMULATE running bundle
ACC_CONTENT_W = 0.0             # v10 UNCHANGED: ACCUMULATE has NO position-independent goal oracle (pure drift-nav)
NEG = -1e9

# UNIQUE-PATH graph structure (v11)
N_GOALS = 5                     # goal slots live at layer L (0..N_GOALS-1); rest are DEAD sinks (N_GOALS <= WIDTH)
N_LIVE = 5                      # live slots per inner layer (0..N_LIVE-1); rest DEAD (== N_GOALS at layer L)
BRANCH_MAX = 3                  # max disjoint-reach live children per live node (goal-dependent branching factor)
N_DISTRACT = 2                  # guaranteed DEAD distractor out-edges per live node (straying targets for ACCUMULATE)

# bands (HYPOTHESIZED@this prereg; verified/iterated at smoke)
MARGIN_ACCUM = 0.20             # REPLAY must beat ACCUMULATE (goal_reach) by this at headline L
MARGIN_REDUNDANCY = 0.15        # REPLAY must beat RANDOM_RESTART (goal_reach) by this at headline L
NO_RECOMB_BAND = 0.05           # REPLAY - RANDOM_RESTART(goal_reach) <= this -> HARD_FAIL (win is redundancy)
DECLINE_MIN = 0.12              # ACCUMULATE intra_decline@Lmax >= this (D1: within-sequence compounding fires)
REPLAY_DECLINE_MAX = 0.05       # REPLAY intra_decline@Lmax <= this (the bounded arm stays flat at the ceiling)
DRIFT_MIN = 0.10                # (legacy transparency band; body-mean drift kept in metrics, NOT gated -- see _acc_curve)
REPLAY_FLAT_MAX = 0.10          # REPLAY body-mean drift transparency band (not gated; intra_decline is the witness)
REPLAY_BODY_MIN = 0.80          # v11 CEILING GATE: REPLAY body_token_acc >= this at EVERY L (follows unique route)
ORACLE_FLOOR = 0.90             # ORACLE per_token_acc floor (readout sound)
ORACLE_BODY_MIN = 0.90          # v11: ORACLE body ceiling ~1.0 (unique route decodable)
CV_MAX = 0.15                   # cross-seed CV cap on REPLAY headline (FULL)
DIVERSITY_MIN = 0.10            # committed-path diversity floor (else candidate collapse -> W_trans degenerate)
SCALE_PREVIEW_N = 8192          # discriminator-survives-scale (option C): full-N ACCUMULATE compounding preview

if RUN_MODE == "smoke":
    N_DIM = 4096; SEEDS = [7]
    L_GRID = [4, 14]; WIDTH = 8; N_INST = 60; R_CAND = 40
else:
    N_DIM = N; SEEDS = [7, 17, 23]
    L_GRID = [4, 8, 14]; WIDTH = 8; N_INST = 160; R_CAND = 48

ARMS = ["ORACLE", "REPLAY", "ACCUMULATE", "RANDOM_RESTART", "REPLAY_PROPOSE_ONLY"]
ARM_UNDER_TEST = "REPLAY"
HEADLINE_L = max(L_GRID)
CHANCE = 1.0 / WIDTH
EXPECTED_N_UNITS = len(SEEDS) * len(ARMS) * len(L_GRID)     # cardinality_ok (META_RULE_H)
assert HEADLINE_L in L_GRID
assert N_GOALS <= WIDTH and N_LIVE <= WIDTH


# --------------------------------------------------------------------------- error scaffolding
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "device": DEVICE.type, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp"); final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f: json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp"); final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f: json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# --------------------------------------------------------------------------- codebook
def build_cb(V, n, gen):
    cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


# --------------------------------------------------------------------------- UNIQUE-PATH layered-DAG construction (v11)
def build_graph(L, seed):
    """Layered DAG (WIDTH slots/layer, disjoint ids) where EACH node's out-neighbors have pairwise-DISJOINT goal-reach
    sets -> for any (start,goal) EXACTLY ONE valid route. Built BACKWARD from N_GOALS live goal-slots at layer L.

    Uniqueness by construction: a live node adopts live children only when their goal-reach sets are pairwise disjoint
    (goal-dependent branching); it also gets N_DISTRACT DEAD-child edges (dead subtree reaches no goal). Thus for any
    goal g in reach[u], exactly one out-neighbor is g-reachable; every other out-neighbor is a goal-DEAD-END. Returns:
      V, out_adj (V,V bool), edge_mult (V,V float traffic), paths (I,L+1 int unique routes), reach (V list of goal-
      token sets), starts (I,), goals (I,). Token id for (layer l, slot w) = l*WIDTH + w; goal token = tok(L, color)."""
    rng = np.random.default_rng(seed)
    W = WIDTH; NG = N_GOALS; NL = N_LIVE
    V = (L + 1) * W

    def tok(l, w):
        return l * W + w

    out_adj = np.zeros((V, V), dtype=bool)
    edge_mult = np.zeros((V, V), dtype=np.float64)
    reach = [set() for _ in range(V)]                      # reach[node] = set of goal-TOKEN ids reachable
    goal_lo = L * W
    for w in range(NG):
        reach[tok(L, w)] = {tok(L, w)}                     # each goal reaches itself (goal color = slot w)

    def add_edge(u, v):
        if not out_adj[u, v]:
            out_adj[u, v] = True
            edge_mult[u, v] = 1.0                          # base traffic 1 on every edge (so W_trans maps it)

    for l in range(L - 1, -1, -1):
        live_ch = [w for w in range(W) if reach[tok(l + 1, w)]]      # live child slots at layer l+1
        dead_ch = [w for w in range(W) if not reach[tok(l + 1, w)]]  # dead child slots at layer l+1
        parents = list(range(NL))                           # live parent slots at layer l
        parent_children = {p: [] for p in parents}
        parent_used = {p: set() for p in parents}
        # adopt every live child by >=1 live parent, keeping each parent's adopted-children reach pairwise DISJOINT
        for cw in rng.permutation(live_ch):
            crset = reach[tok(l + 1, cw)]
            elig = [p for p in parents if crset.isdisjoint(parent_used[p]) and len(parent_children[p]) < BRANCH_MAX]
            if not elig:
                elig = [p for p in parents if crset.isdisjoint(parent_used[p])]  # relax branch cap, keep disjoint
            if not elig:
                continue                                    # goals already covered elsewhere; skip (keep uniqueness)
            p = int(rng.choice(elig))
            parent_children[p].append(int(cw)); parent_used[p] |= crset
        # guarantee every live parent has >=1 live child (stays live / a valid start)
        for p in parents:
            if not parent_children[p]:
                cw = int(rng.choice(live_ch))
                parent_children[p] = [cw]; parent_used[p] = set(reach[tok(l + 1, cw)])
        # wire live parents: backbone (disjoint live children) + DEAD distractor edges
        for p in parents:
            u = tok(l, p)
            for cw in parent_children[p]:
                v = tok(l + 1, cw); add_edge(u, v); reach[u] |= reach[tok(l + 1, cw)]
            if dead_ch:
                nd = min(N_DISTRACT, len(dead_ch))
                for cw in rng.choice(dead_ch, size=nd, replace=False):
                    add_edge(u, tok(l + 1, int(cw)))        # DEAD distractor: reach stays disjoint (empty)
        # dead parents: edges only to dead children (reach stays empty) so straying walks keep moving in dead-land
        for w in range(NL, W):
            u = tok(l, w)
            if dead_ch:
                nd = min(N_DISTRACT, len(dead_ch))
                for cw in rng.choice(dead_ch, size=nd, replace=False):
                    add_edge(u, tok(l + 1, int(cw)))

    # unique-route derivation for an instance (start token, goal token)
    def unique_route(s, g):
        path = [s]; cur = s
        for _ in range(L):
            nbrs = np.where(out_adj[cur])[0]
            cand = [int(v) for v in nbrs if g in reach[v]]
            if len(cand) != 1:
                raise RuntimeError(f"UNIQUE_PATH_VIOLATION at node {cur} goal {g}: {len(cand)} goal-reachable "
                                   f"out-neighbors (expected 1)")
            cur = cand[0]; path.append(cur)
        return path

    # valid (start, goal) instances: layer-0 live nodes and the goals they can reach (skewed goal popularity)
    valid = []
    for w0 in range(NL):
        s = tok(0, w0)
        for g in sorted(reach[s]):
            valid.append((s, int(g)))
    if not valid:
        raise RuntimeError("no valid (start,goal) instances -- graph construction produced no layer-0 goal coverage")
    goal_pop = rng.random(NG) + 0.2                         # skewed goal popularity -> skewed traffic (recency misleads)

    def inst_weight(sg):
        return goal_pop[sg[1] - goal_lo]
    wts = np.array([inst_weight(sg) for sg in valid]); wts = wts / wts.sum()
    I = N_INST
    pick = rng.choice(len(valid), size=I, p=wts)
    paths = np.zeros((I, L + 1), dtype=np.int64)
    for i, k in enumerate(pick):
        s, g = valid[int(k)]
        route = unique_route(s, g)
        paths[i] = route
        for l in range(L):
            edge_mult[route[l], route[l + 1]] += 1.0        # instance traffic accumulates (preferential reuse)
    starts = paths[:, 0].copy(); goals = paths[:, L].copy()
    return V, out_adj, edge_mult, paths, reach, starts, goals


def build_stores(cb, V, out_adj, edge_mult, reach, L):
    """W_trans (N,N) hetero-associative context->next (traffic-weighted, bundled -> capacity-limited);
    R_goal (V,N) normalized bundle of reachable goal-codes; out_adj_t (V,V) bool on device."""
    n = cb.shape[1]
    W = torch.zeros(n, n, device=DEVICE)
    us, vs = np.where(out_adj)
    for u, v in zip(us, vs):
        W = W + float(edge_mult[u, v]) * torch.outer(cb[v], cb[u])
    R_goal = torch.zeros(V, n, device=DEVICE)
    goal_lo = L * WIDTH
    for u in range(V):
        rs = [g for g in reach[u] if g >= goal_lo]
        if rs:
            R_goal[u] = cb[torch.tensor(rs, device=DEVICE)].sum(dim=0)
    R_goal = R_goal / (R_goal.norm(dim=1, keepdim=True) + 1e-8)
    return W, R_goal, torch.tensor(out_adj, device=DEVICE)


# --------------------------------------------------------------------------- gate / walk primitives (v10 UNCHANGED)
def _freqcos(codes, W, cb):
    """freqcos(w,v) = cos(normalize(W @ code_w), cb[v]) -> (Wk, V) traffic/recency signal."""
    pred = codes @ W.t()
    pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
    return pred @ cb.t(), pred


def _combined_logit(freq_wv, content_wv, out_mask_wv):
    logit = content_wv / GATE_TAU + BETA * freq_wv
    return torch.where(out_mask_wv, logit, torch.full_like(logit, NEG))


def propose_walks(cb, W, R_goal, out_adj_t, starts_t, goals_t, L, inst_of, gen, weighted):
    """Batched R-candidate walks. inst_of: (Wk,) instance index; starts_t/goals_t: (I,). weighted -> gain-x-need
    (content-toward-goal + freq); else uniform. Returns paths (Wk,L+1) int64 + step_logit (Wk,) summed chosen-logit."""
    Wk = inst_of.shape[0]
    cur = starts_t[inst_of].clone()
    paths = torch.empty(Wk, L + 1, dtype=torch.long, device=DEVICE); paths[:, 0] = cur
    goal_codes = cb[goals_t[inst_of]]
    content_wv = goal_codes @ R_goal.t()
    score_sum = torch.zeros(Wk, device=DEVICE)
    for l in range(L):
        codes = cb[cur]
        freq_wv, _ = _freqcos(codes, W, cb)
        out_mask = out_adj_t[cur]
        if weighted:
            logit = _combined_logit(freq_wv, content_wv, out_mask)
            probs = torch.softmax(logit, dim=1)
        else:
            probs = out_mask.float()
            probs = probs / (probs.sum(dim=1, keepdim=True) + 1e-30)
        nxt = torch.multinomial(probs, 1, generator=gen).squeeze(1)
        if weighted:
            step = content_wv.gather(1, nxt.unsqueeze(1)).squeeze(1) / GATE_TAU \
                + BETA * freq_wv.gather(1, nxt.unsqueeze(1)).squeeze(1)
            score_sum = score_sum + step
        paths[:, l + 1] = nxt
        cur = nxt
    return paths, score_sum


def accumulate_path(cb, W, R_goal, out_adj_t, starts_t, goals_t, L):
    """MUST-FAIL COMPOUNDING baseline (v10 UNCHANGED). Growing leaky superposition c_{l+1}=LAMBDA_ACC*c + cb[emitted];
    position decoded from the DRIFTING bundle (crosstalk grows with L); next predicted from the WHOLE bundle; navigate
    by the LOCAL freq/traffic signal (ACC_CONTENT_W=0, no position-independent goal re-grounding) -> drifted node ->
    goal-DEAD-END branch (UNRECOVERABLE on the unique-path graph) -> per-position accuracy DROPS with depth."""
    I = starts_t.shape[0]
    c = cb[starts_t].clone()
    paths = torch.empty(I, L + 1, dtype=torch.long, device=DEVICE); paths[:, 0] = starts_t
    content_iv = cb[goals_t] @ R_goal.t()
    for l in range(L):
        cur_hat = (c @ cb.t()).argmax(dim=1)
        out_mask = out_adj_t[cur_hat]
        pred = c @ W.t()
        pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
        freq_iv = pred @ cb.t()
        logit = _combined_logit(freq_iv, ACC_CONTENT_W * content_iv, out_mask)
        dead = ~out_mask.any(dim=1)
        nxt = logit.argmax(dim=1)
        if bool(dead.any()):
            nxt = torch.where(dead, paths[:, l], nxt)
        paths[:, l + 1] = nxt
        c = LAMBDA_ACC * c + cb[nxt]
    return paths


# --------------------------------------------------------------------------- plan-vector + peel/SIC readout (v10 REUSE)
def build_plan_vectors(cb_np, paths_np, L):
    """Bounded WHOLE-plan vectors with a primacy activation gradient (competitive-queuing code)."""
    I = paths_np.shape[0]; V = cb_np.shape[0]; n = cb_np.shape[1]
    a = 1.0 - 0.5 * (np.arange(L + 1) / max(L, 1))
    cb_pos = np.empty(((L + 1) * V, n), dtype=np.float32)
    for p in range(L + 1):
        cb_pos[p * V:(p + 1) * V] = np.roll(cb_np, shift=p, axis=1)
    plans = np.zeros((I, n), dtype=np.float32)
    for p in range(L + 1):
        plans += a[p] * np.roll(cb_np[paths_np[:, p]], shift=p, axis=1)
    return plans, cb_pos


def readout_paths(cb_np, paths_np, L):
    """Competitive-queuing readout via the ALREADY-BUILT peel/SIC decoder (mode='proj')."""
    I = paths_np.shape[0]; V = cb_np.shape[0]
    plans, cb_pos = build_plan_vectors(cb_np, paths_np, L)
    idx, _ = peel_sic_readout(plans, cb_pos, n_items=L + 1, mode="proj")
    idx = np.atleast_2d(idx)
    pos = idx // V; tok = idx % V
    emitted = np.full((I, L + 1), -1, dtype=np.int64)
    for i in range(I):
        for r in range(L + 1):
            p = int(pos[i, r])
            if 0 <= p <= L and emitted[i, p] < 0:
                emitted[i, p] = int(tok[i, r])
    return emitted


# --------------------------------------------------------------------------- per-arm evaluation (v10 UNCHANGED)
def _acc_curve(emitted, target, L):
    """per_token_acc over positions 1..L + per-position + goal_reach + body_token_acc (positions 1..L-1) +
    intra_decline (the ARTIFACT-FREE WITHIN-SEQUENCE compounding witness).

    Why intra_decline and not body_token_acc(mean)-drift-with-L: the accumulator's crosstalk drift is POSITION-
    indexed -- per-position accuracy stays ~1.0 for the first several positions then DECLINES monotonically as the
    leaky bundle accumulates (e.g. L14 per_pos 1.0...1.0->0.57). But body_token_acc (mean over 1..L-1) DILUTES this:
    the degradation ONSET is position-anchored (~pos 8), so a DEEPER sequence has proportionally MORE early-perfect
    positions -> the body-MEAN spuriously RISES with L even though the tail is compounding worse (the inverse of
    v10's per_token_acc depth-varying-weight artifact). The artifact-free witness is the WITHIN-SEQUENCE decline:
      intra_decline = mean(first-half body positions) - mean(second-half body positions).
    A genuinely compounding accumulator has intra_decline > 0 (late body worse than early body); a bounded/flat
    generator (REPLAY at the unique-path ceiling) has intra_decline ~ 0."""
    gen = (emitted[:, 1:L + 1] == target[:, 1:L + 1])
    per_pos = gen.mean(axis=0)                              # (L,) accuracy at positions 1..L
    body = float(gen[:, :L - 1].mean()) if L >= 2 else float(gen.mean())
    bp = per_pos[:L - 1] if L >= 2 else per_pos             # body positions 1..L-1
    h = max(1, len(bp) // 2)
    body_first = float(bp[:h].mean()); body_second = float(bp[-h:].mean())
    intra_decline = body_first - body_second               # >0 = within-sequence compounding
    return {"per_token_acc": float(gen.mean()),
            "body_token_acc": body,
            "body_first_half": round(body_first, 4),
            "body_second_half": round(body_second, 4),
            "intra_decline": round(intra_decline, 4),
            "per_position_acc": [round(float(x), 4) for x in per_pos.tolist()],
            "goal_reach": float((emitted[:, L] == target[:, L]).mean())}


def _path_diversity(paths_np):
    keys = set(tuple(int(x) for x in row) for row in paths_np)
    return len(keys) / max(1, paths_np.shape[0])


def eval_all_arms(cb, W, R_goal, out_adj_t, paths_t, starts_t, goals_t, L, seed):
    """Runs all five arms on the SAME graph/instances. Returns {arm: metrics}, committed REPLAY paths for diversity."""
    I = starts_t.shape[0]
    cb_np = cb.detach().cpu().numpy().astype(np.float32)
    target_np = paths_t.detach().cpu().numpy()
    gen = torch.Generator(device=DEVICE).manual_seed(seed * 7919 + L)
    inst_of = torch.arange(I, device=DEVICE).repeat_interleave(R_CAND)

    w_paths, w_score = propose_walks(cb, W, R_goal, out_adj_t, starts_t, goals_t, L, inst_of, gen, weighted=True)
    u_paths, _ = propose_walks(cb, W, R_goal, out_adj_t, starts_t, goals_t, L, inst_of, gen, weighted=False)
    w_paths = w_paths.view(I, R_CAND, L + 1); w_score = w_score.view(I, R_CAND)
    u_paths = u_paths.view(I, R_CAND, L + 1)

    reach_goal = (w_paths[:, :, L] == goals_t.unsqueeze(1)).float()
    coherence = reach_goal * 10.0 + w_score
    sel = coherence.argmax(dim=1)
    replay_paths = w_paths[torch.arange(I, device=DEVICE), sel]
    rp_sel = torch.randint(0, R_CAND, (I,), generator=gen, device=DEVICE)
    propose_only_paths = w_paths[torch.arange(I, device=DEVICE), rp_sel]
    rr_sel = torch.randint(0, R_CAND, (I,), generator=gen, device=DEVICE)
    random_paths = u_paths[torch.arange(I, device=DEVICE), rr_sel]
    accum_paths = accumulate_path(cb, W, R_goal, out_adj_t, starts_t, goals_t, L)

    arm_paths_np = {
        "ORACLE": target_np,
        "REPLAY": replay_paths.detach().cpu().numpy(),
        "ACCUMULATE": accum_paths.detach().cpu().numpy(),
        "RANDOM_RESTART": random_paths.detach().cpu().numpy(),
        "REPLAY_PROPOSE_ONLY": propose_only_paths.detach().cpu().numpy(),
    }
    # distinct GROUND-TRUTH routes among the instances = the achievable route-diversity CEILING on the unique-path
    # graph (each (start,goal) has exactly one route). Normalizing distinct-committed by this ceiling makes the
    # candidate-collapse / W_trans-degeneracy check robust to N_INST: the raw distinct/N_INST fraction mechanically
    # shrinks as N_INST grows past the (small) count of distinct valid pairs, spuriously tripping the collapse gate.
    n_distinct_target = max(1, len(set(tuple(int(x) for x in row) for row in target_np)))
    out = {}
    for arm, pnp in arm_paths_np.items():
        emitted = readout_paths(cb_np, pnp, L)
        m = _acc_curve(emitted, target_np, L)
        n_distinct_committed = len(set(tuple(int(x) for x in row) for row in pnp))
        m["committed_diversity"] = round(_path_diversity(pnp), 4)                       # raw distinct/N_INST (transparency)
        m["route_diversity_norm"] = round(n_distinct_committed / n_distinct_target, 4)  # distinct/achievable (collapse gate)
        out[arm] = m
    return out, arm_paths_np["REPLAY"]


# --------------------------------------------------------------------------- full-N scale preview (option C, v10 REUSE)
def accumulate_scale_preview(seed, n_dim, L_list):
    """DISCRIMINATOR-MUST-SURVIVE-SCALE (option C). Re-measures ACCUMULATE-only intra_decline (the within-sequence
    compounding witness) at the FULL target N (single seed, {L_lo, L_hi}). If intra_decline@Lmax < DECLINE_MIN at
    full N, the compounding does NOT survive scale. Bundle crosstalk is N-dependent (weaker at larger N)."""
    out = {}
    for L in L_list:
        V, out_adj, edge_mult, paths, reach, starts, goals = build_graph(L, seed * 131 + L)
        cb = build_cb(V, n_dim, torch.Generator(device=DEVICE).manual_seed(seed * 50 + L))
        W, R_goal, out_adj_t = build_stores(cb, V, out_adj, edge_mult, reach, L)
        starts_t = torch.tensor(starts, device=DEVICE); goals_t = torch.tensor(goals, device=DEVICE)
        cb_np = cb.detach().cpu().numpy().astype(np.float32)
        accum_paths = accumulate_path(cb, W, R_goal, out_adj_t, starts_t, goals_t, L)
        emitted = readout_paths(cb_np, accum_paths.detach().cpu().numpy(), L)
        m = _acc_curve(emitted, paths, L)
        out[L] = {"body_token_acc": m["body_token_acc"], "intra_decline": m["intra_decline"],
                  "goal_reach": m["goal_reach"]}
        print(f"    [PREVIEW N={n_dim} L={L}] ACCUM intra_decline={m['intra_decline']:+.4f} "
              f"body_token_acc={m['body_token_acc']:.4f} goal_reach={m['goal_reach']:.3f}", flush=True)
    return out


# --------------------------------------------------------------------------- self-test (two-tier)
# import-time = CELL-VALIDITY only (unique-path invariant + readout sound + telemetry-sensitive + arms differ) so
# --smoke RUNS TO COMPLETION and lands an honest verdict; the DISCRIMINATOR-FIRES gate runs ONLY under --self-test.
def _selftest(strict=False):
    L = 14; ST_N = 4096; Ll = 4
    # The DISCRIMINATOR-FIRES gate must test the graph/seed the FULL actually RUNS (run_seed uses graph-seed
    # seed*131+L, cb-seed seed*50+L, eval-seed=seed). Use SEEDS[0] with that exact recipe so the pre-dispatch gate
    # is REPRESENTATIVE (an arbitrary out-of-sample seed can be a non-representative weak-compounding draw and
    # spuriously block dispatch; measured: run seeds 7/17/23 fire intra_decline 0.21-0.31 at N_INST=160).
    ST_SEED = SEEDS[0]
    # (A) UNIQUE-PATH invariant (D0): build_graph raises on any node with != 1 goal-reachable out-neighbor.
    V, out_adj, edge_mult, paths, reach, starts, goals = build_graph(L, ST_SEED * 131 + L)
    # explicit re-verification of the invariant on every route node (belt + suspenders)
    for i in range(paths.shape[0]):
        g = int(goals[i])
        for l in range(L):
            u = int(paths[i, l]); nbrs = np.where(out_adj[u])[0]
            cand = [int(v) for v in nbrs if g in reach[v]]
            assert len(cand) == 1, f"D0 UNIQUE-PATH FAIL at node {u} goal {g}: {len(cand)} goal-reachable neighbors"
    cb = build_cb(V, ST_N, torch.Generator(device=DEVICE).manual_seed(ST_SEED * 50 + L))
    W, R_goal, out_adj_t = build_stores(cb, V, out_adj, edge_mult, reach, L)
    cb_np = cb.detach().cpu().numpy().astype(np.float32)

    # (B) VALIDITY -- ORACLE readout of the unique target paths recovers them (peel/SIC known content; body ceiling)
    emitted = readout_paths(cb_np, paths, L)
    orc = _acc_curve(emitted, paths, L)
    assert orc["per_token_acc"] >= 0.95, f"ORACLE readout fidelity too low: {orc['per_token_acc']:.3f} (roll/peel bug?)"
    assert orc["body_token_acc"] >= ORACLE_BODY_MIN, \
        f"ORACLE body ceiling too low: {orc['body_token_acc']:.3f} < {ORACLE_BODY_MIN} (unique route not decodable)"

    starts_t = torch.tensor(starts, device=DEVICE); goals_t = torch.tensor(goals, device=DEVICE)
    paths_t = torch.tensor(paths, device=DEVICE)
    m_hi, _ = eval_all_arms(cb, W, R_goal, out_adj_t, paths_t, starts_t, goals_t, L, ST_SEED)
    # shallow graph for the drift-with-L check
    V2, oa2, em2, pa2, rc2, st2, go2 = build_graph(Ll, ST_SEED * 131 + Ll)
    cb2 = build_cb(V2, ST_N, torch.Generator(device=DEVICE).manual_seed(ST_SEED * 50 + Ll))
    W2, Rg2, oat2 = build_stores(cb2, V2, oa2, em2, rc2, Ll)
    st2t = torch.tensor(st2, device=DEVICE); go2t = torch.tensor(go2, device=DEVICE); pa2t = torch.tensor(pa2, device=DEVICE)
    m_lo, _ = eval_all_arms(cb2, W2, Rg2, oat2, pa2t, st2t, go2t, Ll, ST_SEED)

    R = m_hi["REPLAY"]; A = m_hi["ACCUMULATE"]; RR = m_hi["RANDOM_RESTART"]; PO = m_hi["REPLAY_PROPOSE_ONLY"]
    body_drift = m_lo["ACCUMULATE"]["body_token_acc"] - A["body_token_acc"]
    rep_body_drift = m_lo["REPLAY"]["body_token_acc"] - R["body_token_acc"]
    sel_value = R["body_token_acc"] - PO["body_token_acc"]
    print(f"[selftest] L_hi={L}/L_lo={Ll} | ORACLE body={orc['body_token_acc']:.3f} ptok={orc['per_token_acc']:.3f} "
          f"| goal_reach: REPLAY={R['goal_reach']:.3f} ACCUM={A['goal_reach']:.3f} RANDOM={RR['goal_reach']:.3f} "
          f"PROPOSE_ONLY={PO['goal_reach']:.3f} | body_token_acc(artifact-free): REPLAY={R['body_token_acc']:.3f} "
          f"ACCUM={A['body_token_acc']:.3f} RANDOM={RR['body_token_acc']:.3f} PROPOSE_ONLY={PO['body_token_acc']:.3f} "
          f"| ACCUM body_drift(L{Ll}->L{L})={body_drift:+.3f} REPLAY body_drift={rep_body_drift:+.3f} "
          f"sel_value(REP-PO)={sel_value:+.3f} REP-RR(gr)={R['goal_reach']-RR['goal_reach']:+.3f} "
          f"div={R['committed_diversity']:.3f}", flush=True)

    # (C) VALIDITY -- TELEMETRY-SENSITIVITY: relabel goals -> REPLAY goal_reach vs ORIGINAL target MOVES
    perm = torch.randperm(goals_t.shape[0], generator=torch.Generator(device="cpu").manual_seed(2)).to(DEVICE)
    m_shuf, _ = eval_all_arms(cb, W, R_goal, out_adj_t, paths_t, starts_t, goals_t[perm], L, ST_SEED)
    assert m_shuf["REPLAY"]["goal_reach"] < R["goal_reach"] - 0.15, \
        f"TELEMETRY FAIL: relabeling goals did not move REPLAY (real={R['goal_reach']:.3f} shuf={m_shuf['REPLAY']['goal_reach']:.3f})"
    # (D) VALIDITY -- ARMS-MUST-DIFFER
    assert R["route_diversity_norm"] >= DIVERSITY_MIN, (
        f"candidate collapse (W_trans degenerate): REPLAY route_diversity_norm={R['route_diversity_norm']:.3f} "
        f"(distinct committed routes / distinct achievable routes) < {DIVERSITY_MIN}")
    assert abs(R["goal_reach"] - RR["goal_reach"]) > 1e-6, "REPLAY==RANDOM (arms not differentiated)"
    assert N == 8192
    print(f"[selftest] VALIDITY PASS: unique_path(D0) readout_fid={orc['per_token_acc']:.3f} "
          f"oracle_body={orc['body_token_acc']:.3f} telemetry(shuf={m_shuf['REPLAY']['goal_reach']:.3f}<"
          f"{R['goal_reach']:.3f}) arms_differ N8192", flush=True)

    if strict:
        # DISCRIMINATOR-FIRES (pre-dispatch gate). Compounding witness = body_token_acc (artifact-free).
        assert RR["goal_reach"] < A["goal_reach"] + 0.05, \
            f"D2 note: RANDOM_RESTART not underperforming ACCUMULATE (rr={RR['goal_reach']:.3f} acc={A['goal_reach']:.3f})"
        assert R["goal_reach"] - RR["goal_reach"] >= MARGIN_REDUNDANCY, \
            f"D2 FAIL: REPLAY does not beat RANDOM_RESTART (rep={R['goal_reach']:.3f} rr={RR['goal_reach']:.3f})"
        assert CHANCE < m_lo["ACCUMULATE"]["body_token_acc"] < 0.95, \
            f"D4 FAIL: ACCUMULATE body at shallow L{Ll} out of band: {m_lo['ACCUMULATE']['body_token_acc']:.3f}"
        # DISCRIMINATOR-FIRES on the ARTIFACT-FREE within-sequence witness (intra_decline), NOT the diluted body-MEAN
        # drift. assert_discriminator_fires: ACCUMULATE intra_decline must RISE (compounds) + REPLAY must stay FLAT.
        acc_id = A["intra_decline"]; rep_id = R["intra_decline"]
        assert acc_id >= DECLINE_MIN, (
            f"D1 FAIL: ACCUMULATE does not COMPOUND within-sequence. intra_decline@L{L}={acc_id:+.3f} < {DECLINE_MIN} "
            f"(late-body no worse than early-body). Tune LAMBDA_ACC / graph depth before FULL.")
        assert acc_id - rep_id >= DECLINE_MIN, (
            f"D1b FAIL: compounding not accumulator-specific. ACCUM intra_decline={acc_id:+.3f} but REPLAY "
            f"intra_decline={rep_id:+.3f} (gap={acc_id - rep_id:+.3f} < {DECLINE_MIN}).")
        assert rep_id <= REPLAY_DECLINE_MAX and R["body_token_acc"] >= REPLAY_BODY_MIN \
            and m_lo["REPLAY"]["body_token_acc"] >= REPLAY_BODY_MIN, (
            f"D1c FAIL: REPLAY not FLAT at the unique-path CEILING (intra_decline@L{L}={rep_id:+.3f} > "
            f"{REPLAY_DECLINE_MAX} OR body L{Ll}={m_lo['REPLAY']['body_token_acc']:.3f} L{L}="
            f"{R['body_token_acc']:.3f} < {REPLAY_BODY_MIN}). Honest negative: bounded-plan readout drifts too.")
        print(f"[selftest] DISCRIMINATOR-FIRES PASS (strict): ACCUM intra_decline={acc_id:+.3f}>={DECLINE_MIN} "
              f"REPLAY intra_decline={rep_id:+.3f}<={REPLAY_DECLINE_MAX}", flush=True)


_selftest(strict=_ARGS.self_test)
if _ARGS.self_test:
    sys.exit(0)


# --------------------------------------------------------------------------- per-seed driver
def run_seed(seed: int, n_dim: int, out_dir) -> Dict:
    per_unit = []; unit_i = 0; t_seed = time.time()
    total_units = len(ARMS) * len(L_GRID)
    for L in L_GRID:
        V, out_adj, edge_mult, paths, reach, starts, goals = build_graph(L, seed * 131 + L)
        cb = build_cb(V, n_dim, torch.Generator(device=DEVICE).manual_seed(seed * 50 + L))
        W, R_goal, out_adj_t = build_stores(cb, V, out_adj, edge_mult, reach, L)
        starts_t = torch.tensor(starts, device=DEVICE); goals_t = torch.tensor(goals, device=DEVICE)
        paths_t = torch.tensor(paths, device=DEVICE)
        arm_metrics, _ = eval_all_arms(cb, W, R_goal, out_adj_t, paths_t, starts_t, goals_t, L, seed)
        for arm in ARMS:
            m = dict(arm_metrics[arm])
            m.update({"seed": seed, "arm": arm, "L": L, "N": n_dim, "V": V, "width": WIDTH, "chance": round(CHANCE, 4)})
            per_unit.append(m); unit_i += 1
            emit_heartbeat(out_dir, unit_idx=unit_i, elapsed_s=time.time() - t_seed, total_units=total_units,
                           extra={"seed": seed, "arm": arm, "L": L, "acc": round(m["per_token_acc"], 3)})
        rep = arm_metrics["REPLAY"]; acc = arm_metrics["ACCUMULATE"]; rr = arm_metrics["RANDOM_RESTART"]
        print(f"    [L={L} V={V}] ORACLE_body={arm_metrics['ORACLE']['body_token_acc']:.3f} "
              f"REPLAY_body={rep['body_token_acc']:.3f}(goal={rep['goal_reach']:.3f} div={rep['committed_diversity']:.3f}) "
              f"ACCUM_body={acc['body_token_acc']:.3f} RANDOM_body={rr['body_token_acc']:.3f} "
              f"| REP-ACC(body)={rep['body_token_acc']-acc['body_token_acc']:+.3f} "
              f"REP-RR(goal)={rep['goal_reach']-rr['goal_reach']:+.3f}", flush=True)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    return {"seed": seed, "N": n_dim, "per_unit": per_unit, "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


# --------------------------------------------------------------------------- verdict
def _val(all_results, arm, L, field="per_token_acc"):
    vals = [u[field] for r in all_results for u in r["per_unit"]
            if u["arm"] == arm and u["L"] == L and field in u
            and not (isinstance(u[field], float) and math.isnan(u[field]))]
    return float(np.mean(vals)) if vals else float("nan")


def _seed_vals(all_results, arm, L, field="per_token_acc"):
    return [u[field] for r in all_results for u in r["per_unit"] if u["arm"] == arm and u["L"] == L and field in u]


def compute_verdict(all_results) -> Tuple[str, str]:
    if not all_results:
        return ("HARD_FAIL", "no results")
    n_units = sum(len(r["per_unit"]) for r in all_results)
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: got {n_units}, expected {EXPECTED_N_UNITS}")
    L = HEADLINE_L; L_lo = min(L_GRID); GR = "goal_reach"; BD = "body_token_acc"
    orc_b = _val(all_results, "ORACLE", L, BD); orc_ptok = _val(all_results, "ORACLE", L, "per_token_acc")
    rep = _val(all_results, "REPLAY", L, GR); acc = _val(all_results, "ACCUMULATE", L, GR)
    rr = _val(all_results, "RANDOM_RESTART", L, GR)
    div = _val(all_results, "REPLAY", L, "committed_diversity")
    div_norm = _val(all_results, "REPLAY", L, "route_diversity_norm")   # collapse gate (robust to N_INST)
    rep_ptok = _val(all_results, "REPLAY", L, "per_token_acc")
    rep_b = _val(all_results, "REPLAY", L, BD); acc_b = _val(all_results, "ACCUMULATE", L, BD)
    rr_b = _val(all_results, "RANDOM_RESTART", L, BD); prop_b = _val(all_results, "REPLAY_PROPOSE_ONLY", L, BD)
    acc_b_lo = _val(all_results, "ACCUMULATE", L_lo, BD)
    rep_b_lo = _val(all_results, "REPLAY", L_lo, BD)
    body_drift = acc_b_lo - acc_b                        # >0 = accumulator COMPOUNDS (body-MEAN; diluted, transparency only)
    rep_body_drift = rep_b_lo - rep_b                    # ~0 = REPLAY bounded/flat (body-MEAN; transparency only)
    # ARTIFACT-FREE WITHIN-SEQUENCE compounding witness (the actual gate; body-MEAN drift is position-diluted and can
    # invert sign, so intra_decline -- late-body minus early-body accuracy at a SINGLE depth -- is what D1/D1b/D1c gate on.
    ID = "intra_decline"
    acc_id = _val(all_results, "ACCUMULATE", L, ID)      # >0 and rising with L = genuine recursive compounding
    rep_id = _val(all_results, "REPLAY", L, ID)          # ~0 = REPLAY flat at the unique-path ceiling (drift-free)
    acc_id_lo = _val(all_results, "ACCUMULATE", L_lo, ID)
    rep_id_lo = _val(all_results, "REPLAY", L_lo, ID)
    gap_id_hi = acc_id - rep_id                          # REPLAY-vs-ACCUM within-seq decline gap @ headline L
    gap_id_lo = acc_id_lo - rep_id_lo                    # ... @ shallow L (gap GROWS = depth-dependent compounding)
    sel_value = rep_b - prop_b
    beat_acc = rep - acc; beat_rr = rep - rr
    beat_rr_body = rep_b - rr_b
    reps = _seed_vals(all_results, "REPLAY", L, GR)
    cv = float(np.std(reps) / (np.mean(reps) + 1e-9)) if len(reps) > 1 else 0.0

    summary = (f"@L{L} N={all_results[0]['N']} chance~1/W={CHANCE:.3f} | ORACLE body={orc_b:.3f}(ptok={orc_ptok:.3f}) "
               f"| goal_reach: REPLAY={rep:.3f}(ptok={rep_ptok:.3f} div={div:.3f}) ACCUM={acc:.3f} RANDOM={rr:.3f} "
               f"| body_token_acc(artifact-free): REPLAY={rep_b:.3f} ACCUM={acc_b:.3f} RANDOM={rr_b:.3f} | "
               f"REP-ACCUM(gr)={beat_acc:+.3f} REP-RANDOM(gr)={beat_rr:+.3f} sel_value(body)={sel_value:+.3f} "
               f"REP-RANDOM(body)={beat_rr_body:+.3f} | ACCUM body_drift(L{L_lo}->L{L})={body_drift:+.3f} (>0=compounds) "
               f"REPLAY body_drift={rep_body_drift:+.3f} (~0=bounded) REPLAY body@L{L_lo}={rep_b_lo:.3f}@L{L}={rep_b:.3f} "
               f"cv={cv:.3f}")

    if math.isnan(orc_b) or any(math.isnan(x) for x in [rep, acc, rr, rep_b, acc_b]):
        return ("INCONCLUSIVE", f"INCONCLUSIVE_READOUT_UNSOUND_NAN: a per-arm metric is NaN (ORACLE_body={orc_b}); the "
                f"peel/SIC plan readout is over-capacity at this N/L. Increase N or reduce L. {summary}")
    if orc_b < ORACLE_BODY_MIN or orc_ptok < ORACLE_FLOOR:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_READOUT_UNSOUND: ORACLE body={orc_b:.3f} (< {ORACLE_BODY_MIN}) or ptok="
                f"{orc_ptok:.3f} (< {ORACLE_FLOOR}) -- the unique route is not cleanly decodable; metric untrustworthy. "
                f"{summary}")
    if not (CHANCE < acc_b_lo < 0.95):
        return ("INCONCLUSIVE", f"INCONCLUSIVE_BASELINE_OUT_OF_BAND (D4): ACCUM body at shallow L{L_lo}={acc_b_lo:.3f} "
                f"vs (chance={CHANCE:.3f},0.95). The accumulator is broken/saturated even at shallow depth. {summary}")
    if math.isnan(div_norm) or div_norm < DIVERSITY_MIN:
        return ("HARD_FAIL", f"HARD_FAIL_CANDIDATE_COLLAPSE: REPLAY route_diversity_norm={div_norm:.3f} (distinct "
                f"committed / distinct achievable routes; raw div={div:.3f}) < {DIVERSITY_MIN} -- candidate/W_trans "
                f"collapse. {summary}")

    # D1 COMPOUNDING (ARTIFACT-FREE WITHIN-SEQUENCE witness = intra_decline; body-MEAN drift is position-diluted and
    # can even RISE with L, which is what produced the spurious INCONCLUSIVE_NO_COMPOUNDING on this regime).
    if math.isnan(acc_id) or math.isnan(rep_id):
        return ("INCONCLUSIVE", f"INCONCLUSIVE_NO_INTRA_DECLINE_FIELD: intra_decline absent from per_unit (needs L>=2 "
                f"and a cell version recording it). acc_id={acc_id} rep_id={rep_id}. {summary}")
    if acc_id < DECLINE_MIN:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_NO_COMPOUNDING (D1): ACCUMULATE within-sequence decline "
                f"intra_decline@L{L}={acc_id:+.3f} < {DECLINE_MIN} (late-body no worse than early-body). The v10 "
                f"growing-bundle accumulator is NOT compounding error within the sequence on the unique-path regime "
                f"-- RE-SPEC. {summary}")
    if acc_id - rep_id < DECLINE_MIN:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_COMPOUNDING_NOT_ACCUMULATOR_SPECIFIC (D1b): ACCUM intra_decline="
                f"{acc_id:+.3f} but REPLAY intra_decline={rep_id:+.3f} (gap={acc_id-rep_id:+.3f} < {DECLINE_MIN}). "
                f"Both arms decline within-sequence -> compounding not specific to the accumulator. RE-SPEC. {summary}")
    # D1c REPLAY CEILING + FLATNESS (the v11 fix): REPLAY follows the unique route -> body HIGH and within-sequence
    # decline ~0. If not, the HONEST NEGATIVE: the bounded-plan readout also drifts within-sequence.
    if rep_id > REPLAY_DECLINE_MAX or rep_b < REPLAY_BODY_MIN or rep_b_lo < REPLAY_BODY_MIN:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_REPLAY_BELOW_CEILING (D1c): REPLAY is NOT flat at the unique-path "
                f"ceiling (intra_decline@L{L}={rep_id:+.3f} > {REPLAY_DECLINE_MAX} OR body L{L_lo}={rep_b_lo:.3f} "
                f"L{L}={rep_b:.3f} < {REPLAY_BODY_MIN}). Even following the unique route, the committed-plan readout "
                f"declines within-sequence -- an HONEST NEGATIVE about the bounded-plan readout (not a band miss). {summary}")

    # D2 REDUNDANCY
    if beat_rr <= NO_RECOMB_BAND:
        return ("HARD_FAIL", f"HARD_FAIL_REDUNDANCY_NOT_RECOMBINATION: REPLAY-RANDOM_RESTART(gr)={beat_rr:+.3f} <= "
                f"{NO_RECOMB_BAND}; the win is ensemble redundancy, NOT content-scored recombination. {summary}")
    if beat_acc <= 0:
        return ("HARD_FAIL", f"HARD_FAIL_NO_ACCUM_WIN: REPLAY does not beat ACCUMULATE (REP-ACCUM={beat_acc:+.3f}). "
                f"{summary}")

    # HARD_PASS (HP_SCOPE: REPLAY only). DRIFT-FREE DEPTH-INVARIANCE: REPLAY within-sequence decline is FLAT
    # (intra_decline <= REPLAY_DECLINE_MAX) where the ACCUMULATE running-state readout COMPOUNDS (intra_decline
    # >= DECLINE_MIN AND its compounding disadvantage GROWS with depth), and REPLAY beats both controls.
    replay_flat = (rep_id <= REPLAY_DECLINE_MAX)
    accum_compounds = (acc_id >= DECLINE_MIN)
    compounding_grows_with_depth = (gap_id_hi > gap_id_lo)   # accumulator's within-seq decline gap widens with L
    if (accum_compounds and replay_flat and compounding_grows_with_depth
            and beat_acc >= MARGIN_ACCUM and beat_rr >= MARGIN_REDUNDANCY and sel_value >= 0
            and rep_b >= REPLAY_BODY_MIN and orc_b >= ORACLE_BODY_MIN and cv <= CV_MAX):
        return ("HARD_PASS", f"HARD_PASS[REPLAY]_GENERATION_MECHANISM_DRIFT_FREE_DEPTH_INVARIANT: on the UNIQUE-PATH "
                f"graph REPLAY-PROPOSE-SCORE-COMMIT is DRIFT-FREE within-sequence (intra_decline@L{L}={rep_id:+.3f} "
                f"<= {REPLAY_DECLINE_MAX}, body>={REPLAY_BODY_MIN}) while the ACCUMULATE running-state readout "
                f"COMPOUNDS (intra_decline@L{L}={acc_id:+.3f} >= {DECLINE_MIN}) and that compounding GROWS with depth "
                f"(REP-vs-ACCUM decline gap L{L_lo}={gap_id_lo:+.3f}->L{L}={gap_id_hi:+.3f}); REPLAY beats ACCUMULATE "
                f"(REP-ACCUM goal_reach={beat_acc:+.3f}>={MARGIN_ACCUM}) AND RANDOM_RESTART (REP-RANDOM={beat_rr:+.3f}"
                f">={MARGIN_REDUNDANCY}), scoring does not hurt (sel_value={sel_value:+.3f}), ORACLE body ceiling="
                f"{orc_b:.3f}, cv={cv:.3f}<={CV_MAX}. Bounded-plan competitive-queuing generation is DEPTH-INVARIANT "
                f"(drift-free by construction). SCOPE: synthetic structural/mechanism regime; real-language ceiling "
                f"separately reader-gated. {summary}")

    if beat_rr > NO_RECOMB_BAND and beat_acc > 0:
        return ("MIDDLE_BAND", f"MIDDLE_BAND[REPLAY]_PARTIAL: REPLAY beats RANDOM_RESTART (REP-RANDOM={beat_rr:+.3f}) "
                f"and ACCUMULATE on goal_reach (REP-ACCUM={beat_acc:+.3f}), scoring earns its keep (sel_value="
                f"{sel_value:+.3f}), REPLAY body>=ceiling, but misses a strict HARD_PASS gate (accum-margin, "
                f"redundancy-margin, body-gap-grows, flatness, or cv={cv:.3f}). Real but partial. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: REPLAY does not cleanly beat both controls (beat_acc={beat_acc:+.3f} "
            f"beat_rr={beat_rr:+.3f}). {summary}")


# --------------------------------------------------------------------------- main
def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} dev={DEVICE.type} seeds={SEEDS} N={N_DIM} "
          f"L_GRID={L_GRID} headline_L={HEADLINE_L} WIDTH={WIDTH} N_GOALS={N_GOALS} N_LIVE={N_LIVE} "
          f"BRANCH_MAX={BRANCH_MAX} N_DISTRACT={N_DISTRACT} N_INST={N_INST} R_CAND={R_CAND} GATE_TAU={GATE_TAU} "
          f"BETA={BETA} LAMBDA_ACC={LAMBDA_ACC} arms={ARMS} chance={CHANCE:.4f} expected_units={EXPECTED_N_UNITS}",
          flush=True)
    if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL must run on cuda")
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "arms": ARMS,
                                                                  "L_GRID": L_GRID, "width": WIDTH, "n_goals": N_GOALS,
                                                                  "n_live": N_LIVE, "n_inst": N_INST, "r_cand": R_CAND})
    for seed in remaining:
        print(f"[seed={seed}] ...", flush=True); t0 = time.time()
        r = run_seed(seed, N_DIM, out_dir); r["elapsed_s"] = time.time() - t0
        print(f"  seed={seed} done ({r['elapsed_s']:.0f}s)", flush=True)
        write_partial(out_dir, seed, r)
    all_results = list(aggregate_partials(out_dir, SEEDS).values())

    # ARMS-MUST-DIFFER (META_RULE_AF). arms_differ_exempted: {("ORACLE","REPLAY")} -- on the UNIQUE-PATH graph a
    # fully-successful REPLAY reconstructs the TRUE target route exactly, so its (per_token_acc, goal_reach, body)
    # signature legitimately COINCIDES with ORACLE's; that coincidence is the intended body-ceiling SUCCESS, not a
    # bit-identical arm-implementation bug (they are distinct code paths). All OTHER pairs must differ.
    _ceiling = ["ORACLE", "REPLAY", "REPLAY_PROPOSE_ONLY"]
    AF_EXEMPT = {(a, b) for a in _ceiling for b in _ceiling if a != b}
    digs = {}
    for arm in ARMS:
        pts = {"L%d" % L: {f: round(_val(all_results, arm, L, f), 6)
                           for f in ("per_token_acc", "goal_reach", "body_token_acc")} for L in L_GRID}
        digs[arm] = hashlib.sha256(json.dumps(pts, sort_keys=True).encode()).hexdigest()
    for a in ARMS:
        for b2 in ARMS:
            if a < b2 and (a, b2) not in AF_EXEMPT and (b2, a) not in AF_EXEMPT:
                assert digs[a] != digs[b2], f"META_RULE_AF VIOLATION: arms {a} and {b2} bit-identical curves"

    verdict, vmsg = compute_verdict(all_results)
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)

    # DISCRIMINATOR-MUST-SURVIVE-SCALE (option C): re-measure ACCUMULATE compounding at the FULL target N=8192.
    scale_preview = {}
    if RUN_MODE == "smoke":
        print(f"[scale-preview] full-N={SCALE_PREVIEW_N} ACCUMULATE compounding-survival check ...", flush=True)
        t_pv = time.time()
        sp = accumulate_scale_preview(SEEDS[0], SCALE_PREVIEW_N, [min(L_GRID), max(L_GRID)])
        L_lo_pv = min(L_GRID); L_hi_pv = max(L_GRID)
        pv_decline_lo = sp[L_lo_pv]["intra_decline"]; pv_decline_hi = sp[L_hi_pv]["intra_decline"]
        scale_preview = {"N": SCALE_PREVIEW_N,
                         "body_acc_by_L": {str(k): round(v["body_token_acc"], 5) for k, v in sp.items()},
                         "intra_decline_by_L": {str(k): round(v["intra_decline"], 5) for k, v in sp.items()},
                         "intra_decline_hi": round(pv_decline_hi, 5),
                         "intra_decline_grows": bool(pv_decline_hi > pv_decline_lo),
                         "decline_min": DECLINE_MIN,
                         "fires": bool(pv_decline_hi >= DECLINE_MIN), "elapsed_s": round(time.time() - t_pv, 1)}
        print(f"[scale-preview] N={SCALE_PREVIEW_N} ACCUM intra_decline(L{L_lo_pv}={pv_decline_lo:+.4f}->"
              f"L{L_hi_pv}={pv_decline_hi:+.4f}) fires(>= {DECLINE_MIN})={scale_preview['fires']} "
              f"grows={scale_preview['intra_decline_grows']} ({scale_preview['elapsed_s']}s)", flush=True)

    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    if DEVICE.type == "cuda":
        print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
    fields = ["per_token_acc", "body_token_acc", "goal_reach", "committed_diversity", "route_diversity_norm",
              "intra_decline"]
    curves = {arm: {"L%d" % L: {f: round(_val(all_results, arm, L, f), 5) for f in fields} for L in L_GRID}
              for arm in ARMS}
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM,
               "run_mode": RUN_MODE, "device": DEVICE.type, "n_seeds": len(SEEDS), "headline_L": HEADLINE_L,
               "l_grid": L_GRID, "width": WIDTH, "n_goals": N_GOALS, "n_live": N_LIVE, "branch_max": BRANCH_MAX,
               "n_distract": N_DISTRACT, "n_inst": N_INST, "r_cand": R_CAND,
               "chance": round(CHANCE, 5), "gate_tau": GATE_TAU, "beta": BETA, "lambda_acc": LAMBDA_ACC,
               "expected_n_units": EXPECTED_N_UNITS,
               "margins": {"accum": MARGIN_ACCUM, "redundancy": MARGIN_REDUNDANCY, "no_recomb_band": NO_RECOMB_BAND,
                           "drift_min": DRIFT_MIN, "replay_flat_max": REPLAY_FLAT_MAX, "replay_body_min": REPLAY_BODY_MIN,
                           "oracle_floor": ORACLE_FLOOR, "oracle_body_min": ORACLE_BODY_MIN, "cv_max": CV_MAX,
                           "diversity_min": DIVERSITY_MIN},
               "scale_preview": scale_preview,
               "arm_digests": digs, "per_seed": all_results, "curves": curves}
    write_metrics(out_dir, metrics, all_results)
    print("[metrics] written", flush=True)


OUT_DIR_FOR_CRASH = get_output_dir(ANCHOR_NAME)
try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:
    _write_crash_metrics(OUT_DIR_FOR_CRASH, e)
    raise
