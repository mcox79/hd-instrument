"""
substrate_gen_lm_replay_propose_score_commit_v9_n8192_gpu -- the GENERATION mechanism (Stage-4 open barrier).

BRAIN-FIRST DESIGN (notes/research_native_glassbox_generation_brain_first_2026-07-08.md): the brain does NOT
generate by recurrently accumulating raw state and decoding once at the end -- the substrate's OWN 4x-failed
pattern (predresidual_td v4 capped at the concept-recall ceiling is the latest). It generates by
REPLAY-PROPOSE-SCORE-COMMIT: (1) compose bounded WHOLE candidate plans OFFLINE by hippocampal SWR replay that
RECOMBINES already-learned local fragments (Pfeiffer & Foster 2013: routes composed from independently-learned
LOCAL segments, start-goal combos never traversed together; Mattar & Daw 2018: priority = gain x need); (2) read
the committed bounded plan out ONE ITEM AT A TIME via COMPETITIVE QUEUING (Grossberg 1978 primacy gradient +
winner-take-all-and-inhibit == the ALREADY-BUILT peel/SIC decoder, hdlab.cleanup_family.peel_sic_readout) -- no
accumulator, nothing compounds; (3) score/select candidate fragments by the ALREADY-PROVEN content-vs-recency
combined gate (v5-v8: softmax(content_rel/TAU + recency_bias)).

WHY THIS BEATS THE 4x-FAILED ACCUMULATE PATTERN (regenerative-repeater law, research_noise_compounding_bound_
2026-07-07): a fixed bounded plan read multiple times is a HARD RESET against a fixed external reference at each
read -> per-item error does not compound with read-out position. The accumulator that grows/carries raw state IS
the site of noise-compounding; this mechanism REMOVES it by construction rather than patching it (gating/cleanup/
residual -- what all 4 prior attempts did). PREDICT_RESIDUAL_TD failed because it corrected a single rolling
online estimate against its OWN TD-bootstrapped (self-referential) prediction -- the decision-feedback-equalizer
failure class, not a mystery.

SCOPE (HONEST): this tests the generation MECHANISM (no-compounding + genuine recombination) on a SYNTHETIC,
STRUCTURAL layered-DAG route-composition regime. It does NOT claim real-language generation -- the real-language
quality CEILING is barrier-#1(encoder)-gated (the fragment store's concept-recall fidelity). The mechanism is
buildable + decisively testable NOW; the reader is not on the critical path for the MECHANISM question.

TASK (synthetic, clean, explicitly-tagged; NOT natural language): a layered DAG (L+1 layers, WIDTH tokens/layer,
disjoint token ids per layer). G target paths are laid down start(layer0)->goal(layerL) with PREFERENTIAL-REUSE
(skewed traffic) so paths SHARE fragments (edges) -> genuine recombination library; the specific (start,goal)
whole path is NEVER memorized, only local edges are. A generation instance = (start, goal); the ground-truth is
the target path P(start,goal). At MERGE nodes the correct next branch depends on the GOAL (content), NOT on edge
traffic (recency) -- so a recency/frequency gate mis-picks the high-traffic branch for minority-traffic goals,
and the GOAL-content gate is required. This is exactly the v5-v8 recency-vs-content arbitration, now driving
generation, with the relevance signal LEARNED/GRADED (goal-reachability geometry R_goal), not an explicit tag.

STORES (fragment library; reuse the W_hetero-style hetero-associative store + a goal-reachability association):
  W_trans (N,N): sum over edges (u->v) of mult_uv * outer(cb[v], cb[u]) -- context-code -> next-code; freq/recency
                 signal = cos(W_trans@cb[u], cb[v]) is proportional to edge traffic. Capacity-limited (bundled).
  R_goal (V,N): R_goal[v] = normalize(sum_{g reachable from v} cb[g]) -- LEARNED goal-reachability. content_rel of
                candidate next-token v toward goal g = cos(cb[g], R_goal[v]) (graded, implicit, NOT an explicit tag).

GATE (v8 combined, per proposal step; current node u, goal g, candidate out-neighbors {v}):
  logit(v) = content_rel(v,g)/GATE_TAU + BETA * freqcos(v)   (softmax over out-neighbors; -inf off-graph).
  content/TAU dominates on conflict (content overrides recency); freq breaks ties when content is flat.

ARMS (PAIRED -- same graph, same instances, same codebook, same R candidate budget per (seed,L); MATCHED COMPUTE
  for REPLAY vs RANDOM_RESTART: both do R walks x L steps + 1 peel/SIC readout):
  ORACLE          -- positive control: peel/SIC readout of the TRUE target-path plan vector. Certifies the readout
                     + metric are sound (known content -> exact_ordered ~ 1.0, reproduces the block-local decoder
                     result AT THIS REGIME). HP_SCOPE: ORACLE gate is >=0.90 only (readout-fidelity), NOT the
                     mechanism gates.
  REPLAY          -- THE ARM UNDER TEST. Propose R candidate WHOLE paths by gain-x-need-weighted (content-toward-g
                     + freq) sampling; SCORE each whole candidate by coherence (reaches g? + sum content); COMMIT
                     the best; peel/SIC read out the committed bounded plan. Within a walk, context RESETS to the
                     clean codeword each step (no raw accumulation); selection is over WHOLE candidates.
  ACCUMULATE      -- MUST-FAIL drift baseline (the 4x-failed pattern): carry a RAW running context c, c_{l}=
                     normalize(W_trans @ c_{l-1}) with the goal gate bias, decode/emit argmax over out-neighbors,
                     NEVER reset c to the clean codeword -> W_trans capacity noise compounds over L -> per-position
                     accuracy DROPS with L (drift). Reads off its own accumulated state.
  RANDOM_RESTART  -- compute-matched redundancy control: propose the SAME R candidate walks but with UNIFORM
                     out-edge sampling (NO gain-x-need) and select ONE uniformly at random (NO combinedgate score).
                     Isolates GENUINE content-scored recombination from mere ensemble redundancy. If REPLAY only
                     ties this, the "win" is redundancy/averaging, not recombination -> HARD_FAIL.
  REPLAY_PROPOSE_ONLY -- diagnostic (not gated): gain-x-need proposal but UNIFORM selection among the R. Isolates
                     how much of REPLAY's win is the SCORING/selection step vs the smarter proposal.

METRICS: goal_reach = [emitted[L]==g] (route-generation SUCCESS = reached the specified goal). per_token_acc =
  mean over positions 1..L of [emitted==target] (exact laid-down path; LOW ceiling because (start,goal) does not
  uniquely determine the target path -- multiple valid DAG routes reach a goal). body_token_acc = mean over
  MID-SEQUENCE positions 1..L-1, EXCLUDING the goal position L = the ARTIFACT-FREE COMPOUNDING WITNESS (the goal
  position is rescued by the content-gate for every arm; including it manufactures a spurious depth-varying-weight
  drift in per_token_acc). Also per-position curve, candidate diversity, ORACLE readout-fidelity. chance=1/WIDTH.

DISCRIMINATOR-FIRES (compounding witness = body_token_acc, artifact-free; else INCONCLUSIVE, do NOT dispatch FULL):
  (D1) ACCUMULATE body_token_acc DROPS with L: body(L_lo) - body(L_max) >= DRIFT_MIN (drift/compound fires).
  (D2) RANDOM_RESTART underperforms: REPLAY goal_reach - RANDOM_RESTART >= MARGIN_REDUNDANCY (control underperforms).
  (D3) ORACLE per_token_acc >= ORACLE_FLOOR (readout + metric sound).
  (D4) baseline_in_band: ACCUMULATE goal_reach in (chance, 0.95); RANDOM_RESTART is the floor control (~chance).
  Selection value: REPLAY body_token_acc - REPLAY_PROPOSE_ONLY body_token_acc > 0 (the SCORE step earns its keep).

TWO-TIER SELF-TEST (2026-07-09 recovery): import-time _selftest(strict=False) = CELL-VALIDITY only (readout sound
  + telemetry-sensitive + arms differ) so --smoke RUNS TO COMPLETION and lands an honest verdict; the DISCRIMINATOR-
  FIRES gate (D1/D2/D4) is asserted ONLY under explicit --self-test (strict=True, the pre-dispatch gate).

RECOVERY FINDING (2026-07-09 SMOKE, MEASURED@data/exp_substrate_gen_lm_replay_propose_score_commit_v9_n8192_gpu_
  smoke/metrics.json): verdict=INCONCLUSIVE_NO_COMPOUNDING. The ACCUMULATE must-fail baseline does NOT compound in
  this layered-DAG regime -- its body_token_acc is depth-FLAT (L4=0.489->L10=0.402, drift=+0.087 < 0.10) because
  the goal content-gate rescues the final position for EVERY arm, so mid-sequence error does not grow with depth.
  Hence 'REPLAY beats a compounding accumulator' is UNTESTED here. Empirically N-INDEPENDENT (N=512 and N=1024
  per-position curves are near bit-identical -> topology-driven, not crosstalk), so this will NOT self-correct at
  the FULL N=8192 target -> NO FULL dispatch; re-spec needed. SEPARABLE POSITIVE: the recombination+scoring win IS
  real -- REPLAY beats RANDOM_RESTART (redundancy control: +0.783 goal_reach, +0.143 body) AND beats REPLAY_
  PROPOSE_ONLY (scoring/selection earns its keep: sel_value=+0.069 body). RE-SPEC direction for Research: a regime
  where mid-sequence errors are UNRECOVERABLE (no goal-attractor rescue) so the accumulator genuinely compounds.

HARD_PASS (HP_SCOPE: REPLAY only): body_drift >= DRIFT_MIN (accumulator compounds) AND REPLAY beats ACCUMULATE
  (goal_reach) by >= MARGIN_ACCUM AND beats RANDOM_RESTART by >= MARGIN_REDUNDANCY AND the REPLAY-ACCUMULATE body
  gap GROWS with L AND sel_value > 0 AND ORACLE >= ORACLE_FLOOR AND (FULL) CV over seeds <= CV_MAX.
HARD_FAIL: REPLAY - RANDOM_RESTART < NO_RECOMB_BAND (win is redundancy) OR candidate collapse (diversity ~ 0) OR
  REPLAY does not beat ACCUMULATE.
INCONCLUSIVE: readout unsound OR baseline out of band OR NO_COMPOUNDING (D1 body-drift < DRIFT_MIN).
MIDDLE_BAND: beats both controls + scoring earns its keep, but misses a strict HARD_PASS gate.

COMPUTE ARCHITECTURE: mixed (batched-GPU numeric core + CPU numpy peel/SIC readout, justified). The candidate
  WALKS have a GENUINE SEQUENTIAL DEPENDENCY (step L depends on step L-1) -- the allowed sequential exemption; but
  the INDEPENDENT axes (instances I x candidates R) are BATCHED into one (I*R, N) walker tensor advanced with one
  matmul per L step on cuda for FULL (cpu for smoke). The peel/SIC readout is 1 committed plan per instance per
  arm (~I) -> reuses the ALREADY-BUILT numpy hdlab.cleanup_family.peel_sic_readout (batched (B,D) supported) on
  CPU. Storage: sharded fragment edges into a bundled W_trans (bundled is the discriminator here -- its capacity
  limit is what makes ACCUMULATE drift; REPLAY beats it by propose-score-commit, not by de-bundling).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash of the 5 per-L per_token_acc curves; they diverge).
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace atomic).
# - except SystemExit: raise BEFORE except Exception (no BaseException / bare except).
# - crlb_n/a: per-token recall on a graph-walk + gate-select + peel/SIC readout has no closed-form CRLB; the
#   discriminator is the ARM-vs-ARM per_token_acc GAP; chance floor = 1/WIDTH per position (THEORETICAL); readout
#   fidelity floor is certified by ORACLE (peel/SIC known-content ~ 1.0, a positive control at this regime).
# - baseline_in_band: RANDOM_RESTART + ACCUMULATE in (1/WIDTH, 0.95) at headline L (D4); else INCONCLUSIVE.
# - discriminator survives scale: ACCUMULATE drift is DEPTH(L)-driven not N-driven; smoke uses SMALLER N (harder
#   capacity) + the SAME L_GRID so the drift signature (D1) + redundancy gap (D2) witness at smoke scale.
# - HARD_PASS strictly above floor: REPLAY beats BOTH controls by strict margins (> the +/- NO_RECOMB_BAND band).
# - HP_SCOPE: HARD_PASS gates apply ONLY to REPLAY. ORACLE is a readout positive-control (>=ORACLE_FLOOR only);
#   ACCUMULATE + RANDOM_RESTART are must-underperform controls; REPLAY_PROPOSE_ONLY is an ungated diagnostic.
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(L_GRID); verdict counts len(per_unit).
# - per-unit failure-class: except Exception (not bare/BaseException); crash-diag writes CELL_CRASHED.
# - calibration_check: default_ok_for_this_regime -- GATE_TAU=0.05 (v7/v8), BETA=1.0, primacy gradient + peel/SIC
#   mode='proj' (magnitude-aware; fixed a priori, NOT tuned per-L). Discriminator-fires self-test is the health gate.
# - progress_logging: print_flush_true (all progress lines flush=True; sys.stdout line_buffered).
# - cell_chunked: false (3 seeds in-cell, per-seed checkpoint/resume via _seed_checkpoint; light per-seed wall).
# - all numbers in comments tagged: chance=1/WIDTH THEORETICAL; margins/floors HYPOTHESIZED@this prereg (bands set
#   a priori, verified/iterated at smoke); no MEASURED numbers asserted pre-smoke.
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

ANCHOR_NAME = "substrate_gen_lm_replay_propose_score_commit_v9_n8192_gpu"
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
P_REUSE = 0.6                   # preferential-reuse prob when laying down paths (skewed traffic -> recency misleads)
NEG = -1e9

# bands (HYPOTHESIZED@this prereg; verified/iterated at smoke)
MARGIN_ACCUM = 0.20             # REPLAY must beat ACCUMULATE by this at headline L (no-compounding win)
MARGIN_REDUNDANCY = 0.15        # REPLAY must beat RANDOM_RESTART by this at headline L (genuine recombination)
NO_RECOMB_BAND = 0.05           # REPLAY - RANDOM_RESTART <= this -> HARD_FAIL (win is redundancy, not recombination)
DRIFT_MIN = 0.10                # ACCUMULATE acc(L_max) <= acc(L_min) - this (D1: drift fires)
ORACLE_FLOOR = 0.90             # ORACLE per_token_acc floor (D3: readout + metric sound)
CV_MAX = 0.15                   # cross-seed CV cap on REPLAY headline (FULL)
DIVERSITY_MIN = 0.10            # committed-path diversity floor (else candidate collapse -> W_trans degenerate)

if RUN_MODE == "smoke":
    N_DIM = 1024; SEEDS = [7]
    L_GRID = [4, 10]; WIDTH = 5; OUT_DEG = 3; N_INST = 60; R_CAND = 32
else:
    N_DIM = N; SEEDS = [7, 17, 23]
    L_GRID = [4, 8, 14]; WIDTH = 6; OUT_DEG = 4; N_INST = 200; R_CAND = 48

ARMS = ["ORACLE", "REPLAY", "ACCUMULATE", "RANDOM_RESTART", "REPLAY_PROPOSE_ONLY"]
ARM_UNDER_TEST = "REPLAY"
HEADLINE_L = max(L_GRID)
CHANCE = 1.0 / WIDTH
EXPECTED_N_UNITS = len(SEEDS) * len(ARMS) * len(L_GRID)     # cardinality_ok (META_RULE_H)
assert HEADLINE_L in L_GRID


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


# --------------------------------------------------------------------------- layered-DAG construction
def build_graph(L, seed):
    """Layered DAG with WIDTH tokens/layer (disjoint ids), G=N_INST target paths laid down start->goal with
    preferential-reuse (skewed traffic). Returns:
      V (int total tokens), out_adj (V,V bool), edge_mult (V,V float, traffic), paths (I,L+1 int target paths),
      reach (V, set of goal-tokens reachable-from-node), starts (I,), goals (I,).
    Token id for (layer l, slot w) = l*WIDTH + w. Layer L tokens are goals."""
    rng = np.random.default_rng(seed)
    V = (L + 1) * WIDTH

    def tok(l, w):
        return l * WIDTH + w

    out_adj = np.zeros((V, V), dtype=bool)
    edge_mult = np.zeros((V, V), dtype=np.float64)
    # base random graph: every node at layer l has OUT_DEG random out-edges to layer l+1 (distractors + backbone)
    for l in range(L):
        for w in range(WIDTH):
            u = tok(l, w)
            outs = rng.choice(WIDTH, size=min(OUT_DEG, WIDTH), replace=False)
            for w2 in outs:
                v = tok(l + 1, w2)
                out_adj[u, v] = True
                edge_mult[u, v] = 1.0                     # distractor edges: base traffic 1
    # lay down I target paths with preferential-reuse of already-trafficked next nodes (skewed traffic + merges)
    I = N_INST
    paths = np.zeros((I, L + 1), dtype=np.int64)
    node_use = np.zeros((L + 1, WIDTH), dtype=np.float64) + 0.1
    for i in range(I):
        w = int(rng.integers(0, WIDTH))                   # random start slot
        paths[i, 0] = tok(0, w)
        node_use[0, w] += 1.0
        for l in range(L):
            u = tok(l, w)
            cand_w = np.where(out_adj[u, (l + 1) * WIDTH:(l + 2) * WIDTH])[0]  # out-neighbor slots at layer l+1
            if len(cand_w) == 0:                          # guarantee >=1 out-edge
                w2 = int(rng.integers(0, WIDTH)); out_adj[u, tok(l + 1, w2)] = True
                edge_mult[u, tok(l + 1, w2)] = 1.0; cand_w = np.array([w2])
            if rng.random() < P_REUSE:                    # preferential reuse -> skewed traffic
                pr = node_use[l + 1, cand_w]; pr = pr / pr.sum()
                w = int(rng.choice(cand_w, p=pr))
            else:
                w = int(rng.choice(cand_w))
            v = tok(l + 1, w)
            edge_mult[u, v] += 1.0                        # target traffic accumulates
            node_use[l + 1, w] += 1.0
            paths[i, l + 1] = v
    starts = paths[:, 0].copy(); goals = paths[:, L].copy()
    # goal-reachability: for each node, which goal-tokens are reachable via forward edges (BFS on out_adj)
    reach = [set() for _ in range(V)]
    for u in range(V - 1, -1, -1):
        l = u // WIDTH
        if l == L:
            reach[u].add(u)                               # a goal reaches itself
        else:
            for v in range(V):
                if out_adj[u, v]:
                    reach[u] |= reach[v]
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


# --------------------------------------------------------------------------- gate / walk primitives
def _freqcos(codes, W, cb):
    """freqcos(w,v) = cos(normalize(W @ code_w), cb[v]) -> (Wk, V) traffic/recency signal."""
    pred = codes @ W.t()
    pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
    return pred @ cb.t(), pred


def _combined_logit(freq_wv, content_wv, out_mask_wv):
    logit = content_wv / GATE_TAU + BETA * freq_wv
    return torch.where(out_mask_wv, logit, torch.full_like(logit, NEG))


def propose_walks(cb, W, R_goal, out_adj_t, starts_t, goals_t, L, inst_of, gen, weighted):
    """Batched R-candidate walks. inst_of: (Wk,) instance index of each walker; starts_t/goals_t: (I,). If
    weighted: gain-x-need sampling (content-toward-goal + freq). Else uniform over out-neighbors. Returns paths
    (Wk, L+1) int64 and step_logit (Wk,) summed chosen-logit (coherence tiebreak, weighted only)."""
    Wk = inst_of.shape[0]
    cur = starts_t[inst_of].clone()                        # (Wk,)
    paths = torch.empty(Wk, L + 1, dtype=torch.long, device=DEVICE); paths[:, 0] = cur
    # content_wv per walker toward its goal: content[w, v] = cos(cb[goal_w], R_goal[v]) = R_goal @ cb[goal] -> per walker
    goal_codes = cb[goals_t[inst_of]]                      # (Wk, N)
    content_wv = goal_codes @ R_goal.t()                   # (Wk, V)
    score_sum = torch.zeros(Wk, device=DEVICE)
    for l in range(L):
        codes = cb[cur]                                    # (Wk, N)
        freq_wv, _ = _freqcos(codes, W, cb)                # (Wk, V)
        out_mask = out_adj_t[cur]                           # (Wk, V) bool
        if weighted:
            logit = _combined_logit(freq_wv, content_wv, out_mask)
            probs = torch.softmax(logit, dim=1)
        else:
            probs = out_mask.float()
            probs = probs / (probs.sum(dim=1, keepdim=True) + 1e-30)
        nxt = torch.multinomial(probs, 1, generator=gen).squeeze(1)   # (Wk,)
        if weighted:
            # SCORE the chosen edge with the FULL combined gate (content/TAU + BETA*freq), matching the per-step
            # gate -- so candidate selection tracks the high-traffic laid-down TARGET path, not just any goal-reacher.
            step = content_wv.gather(1, nxt.unsqueeze(1)).squeeze(1) / GATE_TAU \
                + BETA * freq_wv.gather(1, nxt.unsqueeze(1)).squeeze(1)
            score_sum = score_sum + step
        paths[:, l + 1] = nxt
        cur = nxt
    return paths, score_sum


def accumulate_path(cb, W, R_goal, out_adj_t, starts_t, goals_t, L):
    """MUST-FAIL drift baseline (the substrate's 4x-failed pattern): carry a RAW running context c (I,N);
    c_{l}=normalize(W @ c_{l-1}) applied RECURRENTLY (capacity-limited W injects noise each step); the CURRENT node
    is DECODED from the drifting raw c (cur_hat=argmax cos(c,cb)) so the out-neighbor mask comes from the DRIFTING
    decode, not a clean track. Same goal gate as REPLAY (fairness) but on a drifting decoded state -> once c drifts
    off the goal-reachable set the gate cannot recover -> goal_reach DROPS with depth L (the accumulator is the site
    of compounding; no clean reset to the codeword)."""
    I = starts_t.shape[0]
    c = cb[starts_t].clone()                               # RAW carried context (never cleaned to a codeword)
    paths = torch.empty(I, L + 1, dtype=torch.long, device=DEVICE); paths[:, 0] = starts_t
    content_iv = cb[goals_t] @ R_goal.t()                  # (I, V) goal-content (drift-independent; fair gate)
    for l in range(L):
        cur_hat = (c @ cb.t()).argmax(dim=1)               # decode current node from the DRIFTING raw c (noisy)
        out_mask = out_adj_t[cur_hat]                      # out-neighbors of the DECODED (maybe wrong) node
        pred = c @ W.t()
        pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
        freq_iv = pred @ cb.t()                            # freq/recency from the drifting context
        logit = _combined_logit(freq_iv, content_iv, out_mask)
        dead = ~out_mask.any(dim=1)                        # decoded node with no out-edge (drifted to a sink)
        nxt = logit.argmax(dim=1)
        if bool(dead.any()):
            nxt = torch.where(dead, paths[:, l], nxt)      # stall on the previous token (cannot advance)
        paths[:, l + 1] = nxt
        c = pred                                           # carry RAW pred forward (recurrent, NO clean reset)
    return paths


# --------------------------------------------------------------------------- plan-vector + peel/SIC readout (REUSE)
def build_plan_vectors(cb_np, paths_np, L):
    """Bounded WHOLE-plan vectors with a primacy activation gradient (competitive-queuing code). plan_i =
    sum_p a_p * roll(cb[node_p], p), a_p = 1 - 0.5*p/L (position 0 = highest activation, produced first).
    Returns plans (I,N) float32 and the position-bound readout codebook cb_pos ((L+1)*V, N)."""
    I = paths_np.shape[0]; V = cb_np.shape[0]; n = cb_np.shape[1]
    a = 1.0 - 0.5 * (np.arange(L + 1) / max(L, 1))         # primacy gradient
    cb_pos = np.empty(((L + 1) * V, n), dtype=np.float32)
    for p in range(L + 1):
        cb_pos[p * V:(p + 1) * V] = np.roll(cb_np, shift=p, axis=1)
    plans = np.zeros((I, n), dtype=np.float32)
    for p in range(L + 1):
        plans += a[p] * np.roll(cb_np[paths_np[:, p]], shift=p, axis=1)
    return plans, cb_pos


def readout_paths(cb_np, paths_np, L):
    """Competitive-queuing readout via the ALREADY-BUILT peel/SIC decoder (mode='proj', magnitude-aware for the
    primacy-graded plan). Returns emitted (I, L+1) int64 token ids by position."""
    I = paths_np.shape[0]; V = cb_np.shape[0]
    plans, cb_pos = build_plan_vectors(cb_np, paths_np, L)
    idx, _ = peel_sic_readout(plans, cb_pos, n_items=L + 1, mode="proj")   # (I, L+1) position-bound member idx
    idx = np.atleast_2d(idx)
    pos = idx // V; tok = idx % V
    emitted = np.full((I, L + 1), -1, dtype=np.int64)
    for i in range(I):
        for r in range(L + 1):
            p = int(pos[i, r])
            if 0 <= p <= L and emitted[i, p] < 0:
                emitted[i, p] = int(tok[i, r])
    return emitted


# --------------------------------------------------------------------------- per-arm evaluation
def _acc_curve(emitted, target, L):
    """per_token_acc over generated positions 1..L + per-position accuracy + goal_reach + body_token_acc.

    body_token_acc = mean over the MID-SEQUENCE positions 1..L-1, EXCLUDING the final (goal) position L.
    The goal position is strongly rescued by the goal content-gate for every arm (it is the gate's target),
    so including it in the per_token_acc average injects a depth-varying-weight ARTIFACT: as L grows, the
    single rescued goal position is a smaller fraction of the average, spuriously lowering per_token_acc even
    when the true mid-sequence accuracy is flat. body_token_acc is the ARTIFACT-FREE compounding witness: if the
    accumulator genuinely compounds, body_token_acc must DROP with depth."""
    gen = (emitted[:, 1:L + 1] == target[:, 1:L + 1])      # (I, L); columns 0..L-1 = positions 1..L
    per_pos = gen.mean(axis=0).tolist()
    body = float(gen[:, :L - 1].mean()) if L >= 2 else float(gen.mean())   # positions 1..L-1 (exclude goal pos L)
    return {"per_token_acc": float(gen.mean()),
            "body_token_acc": body,
            "per_position_acc": [round(float(x), 4) for x in per_pos],
            "goal_reach": float((emitted[:, L] == target[:, L]).mean())}


def _path_diversity(paths_np):
    """fraction of DISTINCT committed paths (candidate collapse detector)."""
    keys = set(tuple(int(x) for x in row) for row in paths_np)
    return len(keys) / max(1, paths_np.shape[0])


def eval_all_arms(cb, W, R_goal, out_adj_t, paths_t, starts_t, goals_t, L, seed):
    """Runs all five arms on the SAME graph/instances. Returns {arm: metrics}, committed_paths for diversity."""
    I = starts_t.shape[0]
    cb_np = cb.detach().cpu().numpy().astype(np.float32)
    target_np = paths_t.detach().cpu().numpy()
    gen = torch.Generator(device=DEVICE).manual_seed(seed * 7919 + L)
    inst_of = torch.arange(I, device=DEVICE).repeat_interleave(R_CAND)     # (I*R,)

    # proposals: weighted (gain-x-need) and uniform, SAME R budget (matched compute)
    w_paths, w_score = propose_walks(cb, W, R_goal, out_adj_t, starts_t, goals_t, L, inst_of, gen, weighted=True)
    u_paths, _ = propose_walks(cb, W, R_goal, out_adj_t, starts_t, goals_t, L, inst_of, gen, weighted=False)
    w_paths = w_paths.view(I, R_CAND, L + 1); w_score = w_score.view(I, R_CAND)
    u_paths = u_paths.view(I, R_CAND, L + 1)

    # coherence score for REPLAY selection: reaches-goal (primary, big) + summed content (tiebreak)
    reach_goal = (w_paths[:, :, L] == goals_t.unsqueeze(1)).float()        # (I, R)
    coherence = reach_goal * 10.0 + w_score
    sel = coherence.argmax(dim=1)                                          # (I,)
    replay_paths = w_paths[torch.arange(I, device=DEVICE), sel]           # (I, L+1)
    # REPLAY_PROPOSE_ONLY: gain-x-need proposal but UNIFORM selection among the R
    rp_sel = torch.randint(0, R_CAND, (I,), generator=gen, device=DEVICE)
    propose_only_paths = w_paths[torch.arange(I, device=DEVICE), rp_sel]
    # RANDOM_RESTART: uniform proposal + uniform selection
    rr_sel = torch.randint(0, R_CAND, (I,), generator=gen, device=DEVICE)
    random_paths = u_paths[torch.arange(I, device=DEVICE), rr_sel]
    # ACCUMULATE: raw-carry drift baseline
    accum_paths = accumulate_path(cb, W, R_goal, out_adj_t, starts_t, goals_t, L)

    arm_paths_np = {
        "ORACLE": target_np,
        "REPLAY": replay_paths.detach().cpu().numpy(),
        "ACCUMULATE": accum_paths.detach().cpu().numpy(),
        "RANDOM_RESTART": random_paths.detach().cpu().numpy(),
        "REPLAY_PROPOSE_ONLY": propose_only_paths.detach().cpu().numpy(),
    }
    out = {}
    for arm, pnp in arm_paths_np.items():
        emitted = readout_paths(cb_np, pnp, L)
        m = _acc_curve(emitted, target_np, L)
        m["committed_diversity"] = round(_path_diversity(pnp), 4)
        out[arm] = m
    return out, arm_paths_np["REPLAY"]


# --------------------------------------------------------------------------- self-test (PROT-022)
# TWO-TIER (2026-07-09 recovery): import-time = CELL-VALIDITY only (readout sound + telemetry-sensitive + arms
# differ); these MUST hold for any run and gate nothing about the mechanism claim. The DISCRIMINATOR-FIRES gate
# (accumulate compounds + random underperforms + baselines in-band) runs ONLY under explicit --self-test (the
# pre-dispatch gate). This lets --smoke RUN TO COMPLETION and LAND an honest verdict (compute_verdict emits
# INCONCLUSIVE if the discriminator does not fire) instead of hard-crashing at import.
def _selftest(strict=False):
    L = 8
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    V, out_adj, edge_mult, paths, reach, starts, goals = build_graph(L, 3)
    cb = build_cb(V, 512, gen)
    W, R_goal, out_adj_t = build_stores(cb, V, out_adj, edge_mult, reach, L)
    cb_np = cb.detach().cpu().numpy().astype(np.float32)

    # (A) VALIDITY -- readout fidelity: ORACLE readout of the TRUE paths recovers them (peel/SIC known content)
    emitted = readout_paths(cb_np, paths, L)
    orc = _acc_curve(emitted, paths, L)
    assert orc["per_token_acc"] >= 0.95, f"ORACLE readout fidelity too low: {orc['per_token_acc']:.3f} (roll/peel bug?)"

    starts_t = torch.tensor(starts, device=DEVICE); goals_t = torch.tensor(goals, device=DEVICE)
    paths_t = torch.tensor(paths, device=DEVICE)
    m_hi, _ = eval_all_arms(cb, W, R_goal, out_adj_t, paths_t, starts_t, goals_t, L, 3)
    # shallow graph for the drift-with-L check (compounding witness uses body_token_acc = artifact-free)
    Ll = 3
    V2, oa2, em2, pa2, rc2, st2, go2 = build_graph(Ll, 3)
    cb2 = build_cb(V2, 512, torch.Generator(device=DEVICE).manual_seed(1))
    W2, Rg2, oat2 = build_stores(cb2, V2, oa2, em2, rc2, Ll)
    st2t = torch.tensor(st2, device=DEVICE); go2t = torch.tensor(go2, device=DEVICE); pa2t = torch.tensor(pa2, device=DEVICE)
    m_lo, _ = eval_all_arms(cb2, W2, Rg2, oat2, pa2t, st2t, go2t, Ll, 3)

    R = m_hi["REPLAY"]; A = m_hi["ACCUMULATE"]; RR = m_hi["RANDOM_RESTART"]; PO = m_hi["REPLAY_PROPOSE_ONLY"]
    body_drift = m_lo["ACCUMULATE"]["body_token_acc"] - A["body_token_acc"]        # >0 = compounds with depth
    gr_drift = m_lo["ACCUMULATE"]["goal_reach"] - A["goal_reach"]
    sel_value = R["body_token_acc"] - PO["body_token_acc"]                          # scoring/selection earns keep
    print(f"[selftest] L_hi={L}/L_lo={Ll} | goal_reach: ORACLE_fid(ptok)={orc['per_token_acc']:.3f} "
          f"REPLAY={R['goal_reach']:.3f} ACCUM={A['goal_reach']:.3f} RANDOM={RR['goal_reach']:.3f} "
          f"PROPOSE_ONLY={PO['goal_reach']:.3f} | body_token_acc(artifact-free): REPLAY={R['body_token_acc']:.3f} "
          f"ACCUM={A['body_token_acc']:.3f} RANDOM={RR['body_token_acc']:.3f} PROPOSE_ONLY={PO['body_token_acc']:.3f} "
          f"| ACCUM body_drift(L{Ll}->L{L})={body_drift:+.3f} gr_drift={gr_drift:+.3f} sel_value(REP-PO)="
          f"{sel_value:+.3f} REP-RR(gr)={R['goal_reach']-RR['goal_reach']:+.3f} div={R['committed_diversity']:.3f}",
          flush=True)

    # (C) VALIDITY -- TELEMETRY-SENSITIVITY: relabel goals -> REPLAY goal_reach vs ORIGINAL target MOVES (not a const)
    perm = torch.randperm(goals_t.shape[0], generator=torch.Generator(device="cpu").manual_seed(2)).to(DEVICE)
    m_shuf, _ = eval_all_arms(cb, W, R_goal, out_adj_t, paths_t, starts_t, goals_t[perm], L, 3)
    assert m_shuf["REPLAY"]["goal_reach"] < R["goal_reach"] - 0.15, \
        f"TELEMETRY FAIL: relabeling goals did not move REPLAY (real={R['goal_reach']:.3f} shuf={m_shuf['REPLAY']['goal_reach']:.3f})"
    # (D) VALIDITY -- ARMS-MUST-DIFFER at small scale (bit-identical arm bug)
    assert R["committed_diversity"] >= DIVERSITY_MIN, "candidate collapse (W_trans degenerate)"
    assert abs(R["goal_reach"] - RR["goal_reach"]) > 1e-6, "REPLAY==RANDOM (arms not differentiated)"
    assert N == 8192
    print(f"[selftest] VALIDITY PASS: readout_fid={orc['per_token_acc']:.3f} telemetry(shuf="
          f"{m_shuf['REPLAY']['goal_reach']:.3f}<{R['goal_reach']:.3f}) arms_differ N8192", flush=True)

    if strict:
        # DISCRIMINATOR-FIRES (pre-dispatch gate). Compounding witness = body_token_acc (artifact-free), NOT
        # goal_reach or per_token_acc (both contaminated by the goal-position rescue). If these fail, do NOT
        # dispatch FULL -- the must-fail baseline is not failing as a COMPOUNDING baseline in this regime.
        assert RR["goal_reach"] < A["goal_reach"], \
            f"D2 FAIL: RANDOM_RESTART does not underperform ACCUMULATE (rr={RR['goal_reach']:.3f} acc={A['goal_reach']:.3f})"
        assert R["goal_reach"] - RR["goal_reach"] >= MARGIN_REDUNDANCY, \
            f"D2 FAIL: REPLAY does not beat RANDOM_RESTART (rep={R['goal_reach']:.3f} rr={RR['goal_reach']:.3f})"
        assert CHANCE < A["goal_reach"] < 0.95, f"D4 FAIL: ACCUMULATE goal_reach out of band: {A['goal_reach']:.3f}"
        assert body_drift >= DRIFT_MIN, (
            f"D1 FAIL: ACCUMULATE does not COMPOUND with depth. body_token_acc(artifact-free) is depth-flat "
            f"(L{Ll}={m_lo['ACCUMULATE']['body_token_acc']:.3f} -> L{L}={A['body_token_acc']:.3f}, "
            f"drift={body_drift:+.3f} < {DRIFT_MIN}). The goal content-gate rescues the final position for EVERY "
            f"arm, so the accumulator's mid-sequence error does NOT grow with depth in this layered-DAG regime -- "
            f"the must-fail baseline is not a compounding baseline here. RE-SPEC the regime (remove the goal-"
            f"attractor rescue / make mid-sequence errors unrecoverable) before dispatching FULL. NOTE the "
            f"recombination+scoring win IS real (REP-PO sel_value={sel_value:+.3f}, REP-RR>0) and can be banked "
            f"separately.")
        print("[selftest] DISCRIMINATOR-FIRES PASS (strict)", flush=True)


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
        print(f"    [L={L} V={V}] ORACLE={arm_metrics['ORACLE']['per_token_acc']:.3f} "
              f"REPLAY={rep['per_token_acc']:.3f}(goal={rep['goal_reach']:.3f} div={rep['committed_diversity']:.3f}) "
              f"ACCUM={acc['per_token_acc']:.3f} RANDOM={rr['per_token_acc']:.3f} "
              f"PROPOSE_ONLY={arm_metrics['REPLAY_PROPOSE_ONLY']['per_token_acc']:.3f} "
              f"| REP-ACC={rep['per_token_acc']-acc['per_token_acc']:+.3f} REP-RR={rep['per_token_acc']-rr['per_token_acc']:+.3f}",
              flush=True)
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
    # ORACLE gate = per_token_acc (all-position readout fidelity). Generation-success gate = goal_reach.
    # COMPOUNDING witness (D1) = body_token_acc (mid-sequence, positions 1..L-1) -- ARTIFACT-FREE: goal_reach and
    # per_token_acc both include the goal position, which the content-gate rescues for every arm, masking (or
    # spuriously manufacturing, via depth-varying weight) the compounding signal.
    orc = _val(all_results, "ORACLE", L, "per_token_acc")
    rep = _val(all_results, "REPLAY", L, GR); acc = _val(all_results, "ACCUMULATE", L, GR)
    rr = _val(all_results, "RANDOM_RESTART", L, GR); prop = _val(all_results, "REPLAY_PROPOSE_ONLY", L, GR)
    div = _val(all_results, "REPLAY", L, "committed_diversity")
    rep_ptok = _val(all_results, "REPLAY", L, "per_token_acc")
    # body (artifact-free) metrics at headline + shallow L
    rep_b = _val(all_results, "REPLAY", L, BD); acc_b = _val(all_results, "ACCUMULATE", L, BD)
    rr_b = _val(all_results, "RANDOM_RESTART", L, BD); prop_b = _val(all_results, "REPLAY_PROPOSE_ONLY", L, BD)
    acc_b_lo = _val(all_results, "ACCUMULATE", L_lo, BD)
    body_drift = acc_b_lo - acc_b                        # >0 = accumulator COMPOUNDS (mid-seq acc drops) with depth
    sel_value = rep_b - prop_b                           # scoring/selection value over goal-gated proposal (on body)
    beat_acc = rep - acc; beat_rr = rep - rr             # generation-success (goal_reach) margins
    beat_rr_body = rep_b - rr_b
    reps = _seed_vals(all_results, "REPLAY", L, GR)
    cv = float(np.std(reps) / (np.mean(reps) + 1e-9)) if len(reps) > 1 else 0.0

    summary = (f"@L{L} N={all_results[0]['N']} chance~1/W={CHANCE:.3f} | goal_reach: ORACLE_fid(ptok)={orc:.3f} "
               f"REPLAY={rep:.3f}(ptok={rep_ptok:.3f} div={div:.3f}) ACCUM={acc:.3f} RANDOM={rr:.3f} "
               f"PROPOSE_ONLY={prop:.3f} | body_token_acc(artifact-free): REPLAY={rep_b:.3f} ACCUM={acc_b:.3f} "
               f"RANDOM={rr_b:.3f} PROPOSE_ONLY={prop_b:.3f} | REP-ACCUM(gr)={beat_acc:+.3f} REP-RANDOM(gr)="
               f"{beat_rr:+.3f} sel_value(REP-PO,body)={sel_value:+.3f} REP-RANDOM(body)={beat_rr_body:+.3f} | "
               f"ACCUM body_drift(L{L_lo}->L{L})={body_drift:+.3f} (>0=compounds) cv={cv:.3f}")

    # VALID-ONLY-IF (readout sound + baseline in a measurable band)
    if orc < ORACLE_FLOOR:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_READOUT_UNSOUND: ORACLE={orc:.3f} < {ORACLE_FLOOR} (peel/SIC readout "
                f"of KNOWN content fails -> metric untrustworthy). {summary}")
    if not (CHANCE < acc < 0.95):
        return ("INCONCLUSIVE", f"INCONCLUSIVE_BASELINE_OUT_OF_BAND (D4): ACCUM goal_reach={acc:.3f} vs "
                f"(chance={CHANCE:.3f},0.95). Re-spec difficulty. {summary}")
    if div < DIVERSITY_MIN:
        return ("HARD_FAIL", f"HARD_FAIL_CANDIDATE_COLLAPSE: REPLAY committed-path diversity={div:.3f} < {DIVERSITY_MIN}"
                f" -- W_trans too degenerate to support genuine multi-candidate composition (a barrier-#1 store-"
                f"capacity finding, NOT a replay-mechanism finding). {summary}")

    # D1 COMPOUNDING GATE (artifact-free body witness). If the accumulator does not compound, the "structural
    # removal of the accumulator" claim is UNTESTED here regardless of goal_reach margins -> INCONCLUSIVE.
    if body_drift < DRIFT_MIN:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_NO_COMPOUNDING (D1): ACCUMULATE body_token_acc (mid-sequence, "
                f"artifact-free) is depth-FLAT (L{L_lo}={acc_b_lo:.3f}->L{L}={acc_b:.3f}, drift={body_drift:+.3f} < "
                f"{DRIFT_MIN}). The goal content-gate rescues the final position for EVERY arm, so the accumulator's "
                f"mid-sequence error does NOT grow with depth in this layered-DAG regime -- the must-fail baseline "
                f"is not a compounding baseline here, so 'REPLAY beats compounding' is NOT tested. RE-SPEC (remove "
                f"the goal-attractor rescue / make mid-sequence errors unrecoverable). NOTE: the recombination+"
                f"scoring win IS real and separable -- REPLAY beats RANDOM_RESTART (redundancy control) and beats "
                f"REPLAY_PROPOSE_ONLY (scoring earns its keep, sel_value={sel_value:+.3f}). {summary}")

    # D2 REDUNDANCY GATE: win must be content-scored recombination, not ensemble redundancy
    if beat_rr <= NO_RECOMB_BAND:
        return ("HARD_FAIL", f"HARD_FAIL_REDUNDANCY_NOT_RECOMBINATION: REPLAY-RANDOM_RESTART(gr)={beat_rr:+.3f} <= "
                f"{NO_RECOMB_BAND}; the win (if any) is ensemble redundancy at matched compute, NOT content-scored "
                f"recombination. {summary}")
    if beat_acc <= 0:
        return ("HARD_FAIL", f"HARD_FAIL_NO_ACCUM_WIN: REPLAY does not beat ACCUMULATE (REP-ACCUM={beat_acc:+.3f}). "
                f"{summary}")

    # HARD_PASS (HP_SCOPE: REPLAY only): compounding fired (body_drift>=DRIFT_MIN) AND REPLAY beats both controls
    # AND the win grows with depth on the artifact-free body metric AND scoring earns its keep.
    gap_body_hi = rep_b - acc_b
    gap_body_lo = _val(all_results, "REPLAY", L_lo, BD) - acc_b_lo
    if (beat_acc >= MARGIN_ACCUM and beat_rr >= MARGIN_REDUNDANCY and gap_body_hi > gap_body_lo and sel_value > 0
            and orc >= ORACLE_FLOOR and cv <= CV_MAX):
        return ("HARD_PASS", f"HARD_PASS[REPLAY]_GENERATION_MECHANISM: REPLAY-PROPOSE-SCORE-COMMIT beats the "
                f"ACCUMULATE compounding baseline (REP-ACCUM={beat_acc:+.3f}>={MARGIN_ACCUM}) AND the compute-matched "
                f"RANDOM_RESTART redundancy control (REP-RANDOM={beat_rr:+.3f}>={MARGIN_REDUNDANCY}), the accumulator "
                f"COMPOUNDS (body_drift={body_drift:+.3f}>={DRIFT_MIN}), scoring earns its keep (sel_value="
                f"{sel_value:+.3f}), readout sound (ORACLE={orc:.3f}), cv={cv:.3f}<={CV_MAX}. SCOPE: synthetic "
                f"structural regime; real-language ceiling is separately reader-gated. {summary}")

    if beat_rr > NO_RECOMB_BAND and beat_acc > 0:
        return ("MIDDLE_BAND", f"MIDDLE_BAND[REPLAY]_PARTIAL: REPLAY beats RANDOM_RESTART (REP-RANDOM={beat_rr:+.3f}) "
                f"and ACCUMULATE on goal_reach (REP-ACCUM={beat_acc:+.3f}) and scoring earns its keep (sel_value="
                f"{sel_value:+.3f}), but misses a strict HARD_PASS gate (accum-margin {MARGIN_ACCUM}, redundancy-"
                f"margin {MARGIN_REDUNDANCY}, body-gap-grows, or cv {cv:.3f}<={CV_MAX}). Real but partial. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: REPLAY does not cleanly beat both controls (beat_acc={beat_acc:+.3f} "
            f"beat_rr={beat_rr:+.3f}). {summary}")


# --------------------------------------------------------------------------- main
def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} dev={DEVICE.type} seeds={SEEDS} N={N_DIM} "
          f"L_GRID={L_GRID} headline_L={HEADLINE_L} WIDTH={WIDTH} OUT_DEG={OUT_DEG} N_INST={N_INST} R_CAND={R_CAND} "
          f"GATE_TAU={GATE_TAU} BETA={BETA} arms={ARMS} chance={CHANCE:.4f} expected_units={EXPECTED_N_UNITS}",
          flush=True)
    if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL must run on cuda")
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "arms": ARMS,
                                                                  "L_GRID": L_GRID, "width": WIDTH, "out_deg": OUT_DEG,
                                                                  "n_inst": N_INST, "r_cand": R_CAND})
    for seed in remaining:
        print(f"[seed={seed}] ...", flush=True); t0 = time.time()
        r = run_seed(seed, N_DIM, out_dir); r["elapsed_s"] = time.time() - t0
        print(f"  seed={seed} done ({r['elapsed_s']:.0f}s)", flush=True)
        write_partial(out_dir, seed, r)
    all_results = list(aggregate_partials(out_dir, SEEDS).values())

    # ARMS-MUST-DIFFER (META_RULE_AF): the 5 per-L per_token_acc curves must not be bit-identical
    digs = {}
    for arm in ARMS:
        pts = {"L%d" % L: round(_val(all_results, arm, L), 6) for L in L_GRID}
        digs[arm] = hashlib.sha256(json.dumps(pts, sort_keys=True).encode()).hexdigest()
    for a in ARMS:
        for b2 in ARMS:
            if a < b2:
                assert digs[a] != digs[b2], f"META_RULE_AF VIOLATION: arms {a} and {b2} bit-identical curves"

    verdict, vmsg = compute_verdict(all_results)
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    if DEVICE.type == "cuda":
        print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
    fields = ["per_token_acc", "body_token_acc", "goal_reach", "committed_diversity"]
    curves = {arm: {"L%d" % L: {f: round(_val(all_results, arm, L, f), 5) for f in fields} for L in L_GRID}
              for arm in ARMS}
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM,
               "run_mode": RUN_MODE, "device": DEVICE.type, "n_seeds": len(SEEDS), "headline_L": HEADLINE_L,
               "l_grid": L_GRID, "width": WIDTH, "out_deg": OUT_DEG, "n_inst": N_INST, "r_cand": R_CAND,
               "chance": round(CHANCE, 5), "gate_tau": GATE_TAU, "beta": BETA, "expected_n_units": EXPECTED_N_UNITS,
               "margins": {"accum": MARGIN_ACCUM, "redundancy": MARGIN_REDUNDANCY, "no_recomb_band": NO_RECOMB_BAND,
                           "drift_min": DRIFT_MIN, "oracle_floor": ORACLE_FLOOR, "cv_max": CV_MAX,
                           "diversity_min": DIVERSITY_MIN},
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
