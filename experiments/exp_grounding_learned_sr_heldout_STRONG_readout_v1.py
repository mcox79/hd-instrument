"""Stage-5 CG cell: READOUT-vs-ENCODER separation on the LEARNED-SR HELD-OUT reasoning task. The audit of
grounding_learned_sr_heldout_reasoning_v1 (HARD_FAIL_CG_MEMORIZED_SEARCH, LEARNED reach@2=0.115, codes_necessary=
False) found the "it's the encoder" attribution OVER-ATTRIBUTED: the proven negative is that the CURRENT learned
codes + a WEAK kNN-softmax smoothing READOUT fail TOGETHER, yet the codes DO carry weak-but-real held-out structure
(Phase-0 M5 held-out edge AUC ~0.69-0.73, MEASURED@data/phase0_code_structure_precheck_result.json). The weak
readout cannot convert that signal. This cell HOLDS THE CURRENT CODES FIXED (does NOT retrain the encoder -- that is
a235164e's job) and swaps the WEAK readout for a STRONG code->reachability readout, then re-runs the reciprocal-
necessity test (learned codes vs random codes) on held-out. THE QUESTION: does a STRONG readout on the SAME current
codes rescue held-out reasoning?

This instantiates the meta-discipline META_residual_gap_decomposition (cosine 0.333 @substrate KB, 2026-07-07):
decompose a residual capability gap into AGGREGATION-LOSS (recoverable by a smarter READ-OUT) vs REACHABILITY-CEILING
(needs new dynamics / a better ENCODER) BEFORE calling the bound fundamental. Here: readout-was-the-limit vs
encoder-is-the-wall.

CODES HELD FIXED. The visible-trained learned codes (Z_vis) are reproduced DETERMINISTICALLY (same seed + same
train_binding_encoder_dev code path + same cfg as the anchor) -- identical codes, no encoder change. Every readout
consumes the SAME Z_vis; only the reachability-column construction for the WITHHELD nodes differs across arms.

READOUTS (all keep VISIBLE rows = the true visible-T resolvent reachability Xvis; only WITHHELD rows are re-estimated):
  WEAK      : the anchor's kNN-softmax smoothing (top-SMOOTH_K visible code-neighbors, softmax cosine, SMOOTH_TEMP).
              Reproduces the anchor LEARNED_HELDOUT (~0.115 @2 / 0.362 @1) and CODEALIAS (~0.104 @2 / 0.332 @1),
              codes_necessary=False. THE ANCHOR the strong readout must beat.
  RIDGE     : primal LINEAR ridge regression -- a LEARNED readout W=(Zv^T Zv + lam I)^-1 Zv^T Yvis trained on VISIBLE
              (code -> visible reachability) pairs, applied to withheld codes Yhat_W = Zw @ W. Global, calibrated.
  KERNEL    : dual RBF-cosine KERNEL ridge -- Yhat_W = Kwv (Kvv + lam I)^-1 Yvis, K(a,b)=exp((cos(a,b)-1)/ELL). The
              most expressive principled readout (nonlinear, full visible support). PRE-REGISTERED PRIMARY strong
              readout for the discriminator; RIDGE reported as the secondary strong readout ("which one won").
Each strong/weak readout is run on LEARNED codes AND on RANDOM (aliased) codes -> reciprocal necessity. The RANDOM-
code arm is the structure-blind control: with codes carrying no graph structure, no readout (however strong) can
convert -> ties.

FAIR-TEST REFINEMENTS (baked in per the audit): (i) reach@1 (UN-COMPOUNDED, the direct hop-1 readout test) is the
PRIMARY metric; reach@2 secondary. (ii) The learned/random margins are computed on the DETERMINATE COMPLETABLE
subset -- held-out chains the full-map KNOWN_T_FULL ceiling actually solves at hop-1 (removes intrinsically
unsolvable chains from the denominator). Full-held-out-subset margins are also reported. (iii) reciprocal-necessity
margin = strong-readout(learned) - strong-readout(random) at reach@1.

DECISIVE DISCRIMINATOR (pre-registered; strong_margin1 = best over {KERNEL,RIDGE} of learned-vs-random reach@1 on the
completable subset; weak_margin1 = WEAK learned-vs-random reach@1 on the completable subset):
  HARD_PASS_READOUT_WAS_THE_LIMIT = strong_margin1 >= READOUT_MARGIN_HP (0.05) AND weak_margin1 < WEAK_MARGIN_MAX
                                    (0.05, the anchor codes_necessary=False reproduced) AND strong_margin1 >=
                                    weak_margin1 + STRONG_OVER_WEAK_MIN (0.03) AND readout_adds_signal (best strong-
                                    learned reach@1 beats the punched-hole HELDOUT_MEMCTRL floor by NEC_MARGIN)
                                    -> under a STRONG readout learned codes BEAT random by a material margin the WEAK
                                       readout did NOT show: it was the READOUT; the codes carry usable routing
                                       structure; the encoder is NOT the (sole) wall.
  HARD_FAIL_ENCODER_CONFIRMED     = strong_margin1 < READOUT_MARGIN_MID (0.02): even the BEST strong readout leaves
                                    learned tied to random -> the codes genuinely lack usable routing structure ->
                                    it IS the encoder (supports the encoder-sharpening path a235164e).
  MIDDLE_BAND_PARTIAL_READOUT     = 0.02 <= strong_margin1 < 0.05: partial rescue (codes help under a strong readout
                                    but do not clear the material bar).
  MIDDLE_BAND_WEAK_ALREADY_SEP    = weak_margin1 >= 0.05 on the completable subset: the completable RESTRICTION alone
                                    surfaced usable codes even for the weak readout -> the readout was not the sole
                                    issue (report; do not credit the strong readout).
Reported (never gated): kernel_margin1, ridge_margin1, which_won, reach@2 margins, strong-vs-weak deltas, completable
count, full-held-out-subset numbers, KNOWN_T ceiling and MEMORYLESS/MEMCTRL floors on the held-out subset.

HONESTY: REAL teacher-free relational learned codes (char-trigram + InfoNCE binding) over the REAL ConceptNet typed
subgraph; the held-out split withholds a disjoint node-ball from BOTH the transition matrix AND the encoder (genuine
train/test split; the STRONG readout is trained ONLY on VISIBLE reachability -- withheld nodes never appear in
training -> no leakage). No language understanding claimed. Reuses the anchor's held-out construction + weak readout
+ the certified SR routing loop VERBATIM (calibration continuity + no drift). Teacher-free, ASCII-only, device-aware
torch.

## Compute architecture
class: (c) mixed with justification. Storage strategy: SHARDED (each node its own code vector; no bundling --
multi-hop compositional chaining, per META_STORAGE_STRATEGY). The strong readouts are closed-form dense solves:
RIDGE = one [d,d] LU solve (multi-RHS over unique goals); KERNEL = one [V,V] LU solve (multi-RHS). Both factored
once per seed, batched over goals (LAPACK/cuSOLVER). Visible/full resolvents are dense multi-RHS LU solves reused
from the anchor. Within a hop all chains + candidates scored by batched einsum. ACROSS hops the chain is inherently
SEQUENTIAL (hop h candidate set depends on h-1 commit) -- a data dependency, not a batching flaw; same shape as the
certified SR cell. No Python-loop matmul over independent points. Routes remote (matmul/solve heavy; anchor ran
cuda 35s FULL); local = smoke only.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): WEAK_LEARNED/WEAK_RANDOM/KERNEL_LEARNED/KERNEL_RANDOM/
#   RIDGE_LEARNED/RIDGE_RANDOM produce distinct commit signatures on the held-out subset (asserted per seed);
#   KERNEL_LEARNED also != WEAK_LEARNED (strong readout differs from weak).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0002). Reference points MEASURED: anchor LEARNED reach@2=0.115,
#   CODEALIAS 0.104, ho_knownT 0.462 (MEASURED@data/exp_grounding_learned_sr_heldout_reasoning_v1/metrics.json).
#   The discriminator is a MARGIN (learned-random); the 0.05 bar clears the FAIL 0.02 side; crlb_reachability: OK.
# - baseline_in_band: MEMORYLESS@1 in (0.05,0.95). NO_CLEANUP@2 collapses (anti-saturation).
# - discriminator survives scale: the readout-separation discriminator is proven on a planted graph where codes
#   carry RECOVERABLE structure (strong readout makes learned >> random; RANDOM codes tie). Smoke previews on the
#   real graph; FULL (3 seeds) canonical. The must-fail control (RANDOM codes) fails at the self-test's scale.
# - HARD_PASS strictly above floor: strong_margin1 >= 0.05 clears FAIL 0.02 + margin; strong >= weak+0.03 adds
#   strictness (META_RULE_L).
# - HP_SCOPE: the readout-was-the-limit gate applies to the strong readouts (KERNEL primary, RIDGE secondary) vs
#   their own random-code controls. WEAK arms reproduce the anchor codes_necessary=False. NO_CLEANUP=must-fail;
#   MEMORYLESS/SUPPLIED/KNOWN_T_FULL=positive-control reproductions; HELDOUT_MEMCTRL=hole floor.
# - positive_control (Gate D): MEMORYLESS + SUPPLIED + KNOWN_T_FULL reproduce the anchor AT the matched FULL regime;
#   AND WEAK_LEARNED reach@2 ~0.115 / WEAK_RANDOM ~0.104 reproduce the anchor readout; drift > 0.10 -> flag.
# - sweep axis: hop depth d in {1,2,3,4}; EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms.
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate. KRR_ELL/KRR_LAM/RIDGE_LAM/WITHHELD_FRAC/SMOOTH_K/
#   SMOOTH_TEMP/SR_GAMMA/SR_BOOST are PRE-REGISTERED, NOT tuned on real data; the planted self-test verifies both
#   strong readouts recover on recoverable structure and collapse on random codes.
# - PAIRED trials: all arms share identical Z_vis base + roles + seeds + graph + chain population + held-out split;
#   only the withheld-row reachability estimate differs.
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
# Certified SR routing loop + resolvent machinery (VERBATIM).
from experiments.exp_grounding_multihop_sr_reachability_routing_v1 import (  # noqa: E402
    build_transition_dense, SRSolver, run_sr_arm, MAX_REACH, SR_GAMMA_PRIMARY, SR_BOOST,
)
# Anchor held-out construction + WEAK readout (VERBATIM reuse -> guarantees anchor reproduction).
from experiments.exp_grounding_learned_sr_heldout_reasoning_v1 import (  # noqa: E402
    build_undirected_adj_simple, pick_withheld_ball, visible_edges,
    build_visible_and_smoothed_columns, _norm_columns_to_sr_p,
    WITHHELD_FRAC, SMOOTH_K, SMOOTH_TEMP,
)

ANCHOR_NAME = "grounding_learned_sr_heldout_STRONG_readout_v1"

# ---- Arm names ----
NO_CLEANUP = "NO_CLEANUP"
MEMORYLESS = "MEMORYLESS"
SUPPLIED_WAYPOINT = "SUPPLIED_WAYPOINT"
KNOWN_T_FULL = "KNOWN_T_FULL"
# held-out readout arms (paired: learned vs random code set)
WEAK_LEARNED = "WEAK_LEARNED"
WEAK_RANDOM = "WEAK_RANDOM"
KERNEL_LEARNED = "KERNEL_LEARNED"
KERNEL_RANDOM = "KERNEL_RANDOM"
RIDGE_LEARNED = "RIDGE_LEARNED"
RIDGE_RANDOM = "RIDGE_RANDOM"
HELDOUT_MEMCTRL = "HELDOUT_MEMCTRL"      # punched-hole floor (no re-estimation)
GENERAL_ARMS = [NO_CLEANUP, MEMORYLESS, SUPPLIED_WAYPOINT, KNOWN_T_FULL]
HELDOUT_ARMS = [WEAK_LEARNED, WEAK_RANDOM, KERNEL_LEARNED, KERNEL_RANDOM, RIDGE_LEARNED, RIDGE_RANDOM,
                HELDOUT_MEMCTRL]

# ---- Pre-registered bands (picked BEFORE the run) ----
READOUT_MARGIN_HP = 0.05      # HARD_PASS: strong-readout learned-vs-random reach@1 margin >= this (material)
READOUT_MARGIN_MID = 0.02     # HARD_FAIL floor: even best strong readout margin < this -> encoder confirmed
WEAK_MARGIN_MAX = 0.05        # weak readout must stay below this (reproduce anchor codes_necessary=False)
STRONG_OVER_WEAK_MIN = 0.03   # strong margin must beat weak margin by at least this (strictness)
NEC_MARGIN = 0.05             # readout_adds_signal: strong-learned reach@1 beats the hole floor by this
MIN_COMPLETABLE_CHAINS = 40   # minimum determinate-completable held-out chains for a valid discriminator

# ---- Strong-readout knobs (PRE-REGISTERED; NOT tuned on real data; validated on the planted self-test) ----
KRR_ELL = 0.25               # RBF-cosine bandwidth for the dual kernel ridge readout
KRR_LAM = 0.1                # ridge regularization (dual kernel)
RIDGE_LAM = 1.0              # ridge regularization (primal linear)

# ---- Anti-saturation / must-fail control ----
BASE_COLLAPSE_ABS = 0.10
BASE_COLLAPSE_FRAC = 0.50
BASE_IN_BAND_HI = 0.95
HOP1_PRESENT = 0.08
SUPPLIED_FIRES_MIN = 0.10

# ---- Gate-D positive-control reproduction anchors (MEASURED@anchor metrics) + tolerance (FULL only) ----
REPRO_MEM1 = 0.453
REPRO_SUP1 = 0.756
REPRO_SUP2 = 0.500
REPRO_KNOWNT2 = 0.434
REPRO_WEAK_LEARNED2 = 0.115   # anchor LEARNED_HELDOUT reach@2 (full held-out subset)
REPRO_WEAK_RANDOM2 = 0.104    # anchor CODEALIAS reach@2 (full held-out subset)
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
# FULL matches the anchor FULL_CFG so codes + anchors reproduce (Gate-D positive control).
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
# run_sr_arm_capture: VERBATIM copy of the certified run_sr_arm PLUS per-hop committed capture (needed for the
# determinate-completable-subset restriction). Self-test asserts bit-identical (reach + sig) to run_sr_arm.
# ---------------------------------------------------------------------------

def run_sr_arm_capture(Z, Zp, roles_t, nbr_idx, nbr_mask, start, targets, role_ids,
                       device, chunk, n_nodes, sr_p, boost_weight):
    from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import _hrr_bind_t  # local (VERBATIM parity)
    HIT_K = 10
    L = len(targets)
    C = start.shape[0]
    cur = torch.from_numpy(start).to(device)
    reach = {}
    hit10 = {}
    commit_sig = []
    committed_hops = []
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
            cand = nbr_idx[cur_blk]
            mask = nbr_mask[cur_blk]
            Zc = Zp[cand]
            p = _l2t(pred_blk)
            base = torch.einsum("bd,bkd->bk", p, Zc)
            srb = torch.gather(sr_p[b0:b1], 1, cand)
            srb_hi = srb.masked_fill(~mask, float("-inf")).max(dim=1, keepdim=True).values
            srb_lo = srb.masked_fill(~mask, float("inf")).min(dim=1, keepdim=True).values
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
        cc = committed.detach().to("cpu").numpy().astype(np.int64)
        commit_sig.append(cc)
        committed_hops.append(cc)
        cur = committed
    sig = hashlib.sha256(np.concatenate(commit_sig).tobytes()).hexdigest()
    return dict(reach=reach, hit10=hit10, sig=sig, committed=committed_hops)


# ---------------------------------------------------------------------------
# STRONG readouts. Both keep visible rows = Xvis (true visible-T reachability) and re-estimate ONLY withheld rows
# from a readout trained on VISIBLE (code -> visible reachability) pairs. No withheld node appears in training.
# ---------------------------------------------------------------------------

def _wv_indices(withheld_mask, device):
    w_idx = torch.from_numpy(np.where(withheld_mask)[0].astype(np.int64)).to(device)
    v_idx = torch.from_numpy(np.where(~withheld_mask)[0].astype(np.int64)).to(device)
    return w_idx, v_idx


def strong_linear_ridge_columns(Zn, withheld_mask, Xvis, lam, device):
    """Primal LINEAR ridge: W = (Zv^T Zv + lam I_d)^-1 Zv^T Yvis [d,U]; Yhat_W = Zw @ W. Xvis [n,U] -> Xstrong."""
    w_idx, v_idx = _wv_indices(withheld_mask, device)
    if w_idx.shape[0] == 0 or v_idx.shape[0] == 0:
        return Xvis.clone()
    Zv = Zn[v_idx]
    Zw = Zn[w_idx]
    Yv = Xvis[v_idx]
    d = Zv.shape[1]
    G = Zv.t() @ Zv
    A = G + lam * torch.eye(d, device=device, dtype=G.dtype)
    W = torch.linalg.solve(A, Zv.t() @ Yv)          # [d, U]
    Yhat = (Zw @ W).clamp(min=0.0)                  # [W, U]
    Xstrong = Xvis.clone()
    Xstrong[w_idx] = Yhat
    return Xstrong


def strong_kernel_ridge_columns(Zn, withheld_mask, Xvis, ell, lam, device):
    """Dual RBF-cosine KERNEL ridge: K(a,b)=exp((cos-1)/ell); A=(Kvv+lam I)^-1 Yvis; Yhat_W = Kwv A. Xvis->Xstrong."""
    w_idx, v_idx = _wv_indices(withheld_mask, device)
    if w_idx.shape[0] == 0 or v_idx.shape[0] == 0:
        return Xvis.clone()
    Zv = Zn[v_idx]
    Zw = Zn[w_idx]
    Yv = Xvis[v_idx]
    V = Zv.shape[0]
    inv_ell = 1.0 / max(ell, 1e-6)
    sim_vv = (Zv @ Zv.t()).clamp(-1.0, 1.0)
    Kvv = torch.exp((sim_vv - 1.0) * inv_ell)
    A = torch.linalg.solve(Kvv + lam * torch.eye(V, device=device, dtype=Kvv.dtype), Yv)   # [V, U]
    sim_wv = (Zw @ Zv.t()).clamp(-1.0, 1.0)
    Kwv = torch.exp((sim_wv - 1.0) * inv_ell)
    Yhat = (Kwv @ A).clamp(min=0.0)                 # [W, U]
    Xstrong = Xvis.clone()
    Xstrong[w_idx] = Yhat
    return Xstrong


# ---------------------------------------------------------------------------
# reach helpers
# ---------------------------------------------------------------------------

def _subset_reach(committed_hops, tgt_list, mask):
    """committed_hops: list[np int64 [C]]; tgt_list: list[np int64 [C]]; mask: np bool [C]. Returns {hop: reach}."""
    out = {}
    msum = int(mask.sum())
    for hh in range(len(committed_hops)):
        if msum > 0:
            out[hh + 1] = float((committed_hops[hh][mask] == tgt_list[hh][mask]).mean())
        else:
            out[hh + 1] = float("nan")
    return out


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------

def run_seed(seed, node_words, edges, rels, dir_adj, roles_t, nbr_idx, nbr_rel, nbr_mask, cfg, device, out_dir):
    n_nodes = len(node_words)
    chunk = cfg["chain_chunk"]
    d = cfg["code_dim"]

    X = char_trigram_features(node_words, cfg["feat_dim"])
    # FULL codes (all edges) -> KNOWN_T_FULL + general anchors
    Z_full = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_full")
    Zp_full = torch.cat([Z_full, torch.zeros(1, d, device=device)], dim=0)

    # general chains (identical rng offset/sampler as anchor -> paired anchor reproduction)
    gen_rng = np.random.default_rng(seed + 909)
    g_start, g_targets, g_role = sample_chains(dir_adj, cfg["n_chains"], MAX_REACH, gen_rng)
    goals = g_targets[MAX_REACH - 1]

    # held-out split (IDENTICAL construction to the anchor: same seed offsets + same pick_withheld_ball)
    adj_u = build_undirected_adj_simple(dir_adj, n_nodes)
    split_rng = np.random.default_rng(seed + 4242)
    withheld_mask = pick_withheld_ball(adj_u, n_nodes, WITHHELD_FRAC, set(), split_rng)
    n_withheld = int(withheld_mask.sum())
    hop1_tgt = g_targets[0]
    heldout_chain_mask = withheld_mask[hop1_tgt] & (~withheld_mask[goals])
    ho_idx = np.where(heldout_chain_mask)[0]
    n_heldout = int(ho_idx.shape[0])

    # visible graph (leakage-safe) -> visible T + visible-trained codes (the CURRENT codes, held fixed)
    e_vis, r_vis = visible_edges(edges, rels, withheld_mask)
    dir_adj_vis = build_typed_diradj(e_vis, r_vis, n_nodes)
    T_vis = build_transition_dense(dir_adj_vis, n_nodes, device)
    sr_solver_vis = SRSolver(T_vis, device)
    Z_vis = train_binding_encoder_dev(X, e_vis, r_vis, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_vis")
    Zp_vis = torch.cat([Z_vis, torch.zeros(1, d, device=device)], dim=0)
    Zn_vis = torch.nn.functional.normalize(Z_vis, dim=1)
    # aliased random codes for reciprocal-necessity (structure-blind control)
    alias_gen = torch.Generator(device="cpu").manual_seed(seed + 31337)
    Zn_alias = torch.nn.functional.normalize(
        torch.randn(n_nodes, d, generator=alias_gen).to(device), dim=1)

    # full-T known columns
    T_full = build_transition_dense(dir_adj, n_nodes, device)
    sr_solver_full = SRSolver(T_full, device)
    uniq_goals = np.unique(np.asarray(goals, dtype=np.int64))
    Xfull = sr_solver_full.columns(uniq_goals, SR_GAMMA_PRIMARY)
    sr_p_knownT, _, _ = _norm_columns_to_sr_p(Xfull, goals, n_nodes, device)

    # WEAK readout columns (anchor VERBATIM) + Xvis target for the strong readouts
    cols = build_visible_and_smoothed_columns(sr_solver_vis, uniq_goals, SR_GAMMA_PRIMARY, withheld_mask,
                                              Zn_vis, Zn_alias, SMOOTH_K, SMOOTH_TEMP, n_nodes, device)
    Xvis = cols["Xvis"]
    sr_p_weak_l, _, _ = _norm_columns_to_sr_p(cols["learned"], goals, n_nodes, device)
    sr_p_weak_r, _, _ = _norm_columns_to_sr_p(cols["codealias"], goals, n_nodes, device)
    sr_p_memctrl, _, _ = _norm_columns_to_sr_p(cols["memctrl"], goals, n_nodes, device)

    # STRONG readout columns (learned codes + random codes)
    Xk_l = strong_kernel_ridge_columns(Zn_vis, withheld_mask, Xvis, KRR_ELL, KRR_LAM, device)
    Xk_r = strong_kernel_ridge_columns(Zn_alias, withheld_mask, Xvis, KRR_ELL, KRR_LAM, device)
    Xr_l = strong_linear_ridge_columns(Zn_vis, withheld_mask, Xvis, RIDGE_LAM, device)
    Xr_r = strong_linear_ridge_columns(Zn_alias, withheld_mask, Xvis, RIDGE_LAM, device)
    sr_p_k_l, _, _ = _norm_columns_to_sr_p(Xk_l, goals, n_nodes, device)
    sr_p_k_r, _, _ = _norm_columns_to_sr_p(Xk_r, goals, n_nodes, device)
    sr_p_r_l, _, _ = _norm_columns_to_sr_p(Xr_l, goals, n_nodes, device)
    sr_p_r_r, _, _ = _norm_columns_to_sr_p(Xr_r, goals, n_nodes, device)

    arms_general = {}
    sigs = {}
    # ---- general-population anchors (Gate-D + anti-sat) ----
    r, h, _sa, sig = ft_run_no_cleanup(Z_full, roles_t, g_start, g_targets, g_role, device, n_nodes)
    arms_general[NO_CLEANUP] = r; sigs[NO_CLEANUP] = sig
    r, h, _sa, sig = ft_run_chain_arm(FT_MEMORYLESS, Z_full, Zp_full, roles_t, nbr_idx, nbr_rel, nbr_mask,
                                      None, g_start, g_targets, g_role, device, chunk, n_nodes)
    arms_general[MEMORYLESS] = r; sigs[MEMORYLESS] = sig
    r, h, _sa, sig = ft_run_chain_arm(FT_GOAL_WAYPOINT, Z_full, Zp_full, roles_t, nbr_idx, nbr_rel, nbr_mask,
                                      None, g_start, g_targets, g_role, device, chunk, n_nodes)
    arms_general[SUPPLIED_WAYPOINT] = r; sigs[SUPPLIED_WAYPOINT] = sig
    r, h, sig = run_sr_arm(Z_full, Zp_full, roles_t, nbr_idx, nbr_mask, g_start, g_targets, g_role,
                           device, chunk, n_nodes, sr_p_knownT, SR_BOOST)
    arms_general[KNOWN_T_FULL] = r; sigs[KNOWN_T_FULL] = sig

    ho_full = {}
    ho_comp = {}
    ho_refs = {}
    n_completable = 0
    if n_heldout >= 1:
        gs = g_start[ho_idx]
        gt = [g_targets[hh][ho_idx] for hh in range(MAX_REACH)]
        gr = [g_role[hh][ho_idx] for hh in range(MAX_REACH)]

        def cap(srp, Zc, Zpc):
            return run_sr_arm_capture(Zc, Zpc, roles_t, nbr_idx, nbr_mask, gs, gt, gr,
                                      device, chunk, n_nodes, srp[ho_idx], SR_BOOST)

        res = {
            WEAK_LEARNED: cap(sr_p_weak_l, Z_vis, Zp_vis),
            WEAK_RANDOM: cap(sr_p_weak_r, Z_vis, Zp_vis),
            KERNEL_LEARNED: cap(sr_p_k_l, Z_vis, Zp_vis),
            KERNEL_RANDOM: cap(sr_p_k_r, Z_vis, Zp_vis),
            RIDGE_LEARNED: cap(sr_p_r_l, Z_vis, Zp_vis),
            RIDGE_RANDOM: cap(sr_p_r_r, Z_vis, Zp_vis),
            HELDOUT_MEMCTRL: cap(sr_p_memctrl, Z_vis, Zp_vis),
        }
        known_ho = cap(sr_p_knownT, Z_full, Zp_full)   # KNOWN_T on held-out: completable mask + ceiling

        # determinate-completable subset: KNOWN_T_FULL solves the chain at hop-1
        completable_mask = (known_ho["committed"][0] == gt[0])
        n_completable = int(completable_mask.sum())
        all_mask = np.ones(n_heldout, dtype=bool)

        for a in HELDOUT_ARMS:
            ho_full[a] = res[a]["reach"]
            sigs[a] = res[a]["sig"]
            ho_comp[a] = _subset_reach(res[a]["committed"], gt, completable_mask)

        # references (memoryless floor + known-T ceiling) on both full + completable subsets
        r_mho, _h, _sa, _s = ft_run_chain_arm(FT_MEMORYLESS, Z_vis, Zp_vis, roles_t, nbr_idx, nbr_rel, nbr_mask,
                                              None, gs, gt, gr, device, chunk, n_nodes)
        ho_refs = dict(
            memoryless_full={dd: r_mho[dd] for dd in range(1, MAX_REACH + 1)},
            known_t_full_full=known_ho["reach"],
            known_t_full_comp=_subset_reach(known_ho["committed"], gt, completable_mask),
        )
    else:
        for a in HELDOUT_ARMS:
            ho_full[a] = {dd: float("nan") for dd in range(1, MAX_REACH + 1)}
            ho_comp[a] = {dd: float("nan") for dd in range(1, MAX_REACH + 1)}
            sigs[a] = "nan_%s" % a

    for a in GENERAL_ARMS:
        _log("  seed=%d %-18s reach=%s" % (
            seed, a, {dd: round(arms_general[a][dd], 3) for dd in range(1, MAX_REACH + 1)}))
    for a in HELDOUT_ARMS:
        _log("  seed=%d %-18s ho_full@1=%s @2=%s | comp@1=%s @2=%s" % (
            seed, a, _fmt(ho_full[a][1]), _fmt(ho_full[a][2]), _fmt(ho_comp[a][1]), _fmt(ho_comp[a][2])))
    _log("  seed=%d n_withheld=%d (%.1f%%) n_heldout=%d n_completable=%d/%d" % (
        seed, n_withheld, 100.0 * n_withheld / max(n_nodes, 1), n_heldout, n_completable, n_heldout))

    return dict(seed=seed, arms_general=arms_general, ho_full=ho_full, ho_comp=ho_comp, ho_refs=ho_refs,
                arm_sigs=sigs, n_withheld=n_withheld, withheld_frac_actual=n_withheld / max(n_nodes, 1),
                n_heldout_chains=n_heldout, n_completable=n_completable, n_general=int(g_start.shape[0]),
                code_dim=d)


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, meta, cfg):
    def G(arm, dd):
        return _nm([m["arms_general"][arm][dd] for m in per_seed])

    def HF(arm, dd):
        return _nm([m["ho_full"][arm][dd] for m in per_seed])

    def HC(arm, dd):
        return _nm([m["ho_comp"][arm][dd] for m in per_seed])

    def HR(key, dd):
        return _nm([m["ho_refs"][key][dd] for m in per_seed if key in m.get("ho_refs", {})])

    base1 = G(NO_CLEANUP, 1); base2 = G(NO_CLEANUP, 2)
    mem1 = G(MEMORYLESS, 1); mem2 = G(MEMORYLESS, 2)
    sup1 = G(SUPPLIED_WAYPOINT, 1); sup2 = G(SUPPLIED_WAYPOINT, 2)
    knownT1 = G(KNOWN_T_FULL, 1); knownT2 = G(KNOWN_T_FULL, 2)

    # ---- reach@1 margins on the COMPLETABLE subset (PRIMARY) ----
    wl1 = HC(WEAK_LEARNED, 1); wr1 = HC(WEAK_RANDOM, 1)
    kl1 = HC(KERNEL_LEARNED, 1); kr1 = HC(KERNEL_RANDOM, 1)
    rl1 = HC(RIDGE_LEARNED, 1); rr1 = HC(RIDGE_RANDOM, 1)
    memctrl_c1 = HC(HELDOUT_MEMCTRL, 1)
    weak_margin1 = (wl1 - wr1) if (wl1 == wl1 and wr1 == wr1) else float("nan")
    kernel_margin1 = (kl1 - kr1) if (kl1 == kl1 and kr1 == kr1) else float("nan")
    ridge_margin1 = (rl1 - rr1) if (rl1 == rl1 and rr1 == rr1) else float("nan")
    strong_margins1 = [x for x in (kernel_margin1, ridge_margin1) if x == x]
    best_strong_margin1 = max(strong_margins1) if strong_margins1 else float("nan")
    which_won = "nan"
    if kernel_margin1 == kernel_margin1 or ridge_margin1 == ridge_margin1:
        which_won = "KERNEL" if (kernel_margin1 == kernel_margin1
                                 and (ridge_margin1 != ridge_margin1 or kernel_margin1 >= ridge_margin1)) else "RIDGE"
    best_strong_learned1 = _nm([kl1 if which_won == "KERNEL" else rl1])

    # ---- reach@2 margins on the completable subset (secondary) ----
    kl2 = HC(KERNEL_LEARNED, 2); kr2 = HC(KERNEL_RANDOM, 2)
    rl2 = HC(RIDGE_LEARNED, 2); rr2 = HC(RIDGE_RANDOM, 2)
    wl2c = HC(WEAK_LEARNED, 2); wr2c = HC(WEAK_RANDOM, 2)
    kernel_margin2 = (kl2 - kr2) if (kl2 == kl2 and kr2 == kr2) else float("nan")
    ridge_margin2 = (rl2 - rr2) if (rl2 == rl2 and rr2 == rr2) else float("nan")
    weak_margin2 = (wl2c - wr2c) if (wl2c == wl2c and wr2c == wr2c) else float("nan")
    strong_margins2 = [x for x in (kernel_margin2, ridge_margin2) if x == x]
    best_strong_margin2 = max(strong_margins2) if strong_margins2 else float("nan")

    # ---- full-held-out-subset numbers (reported; also anchor reproduction) ----
    wl_full2 = HF(WEAK_LEARNED, 2); wr_full2 = HF(WEAK_RANDOM, 2)
    wl_full1 = HF(WEAK_LEARNED, 1); wr_full1 = HF(WEAK_RANDOM, 1)
    ho_mem2 = HR("memoryless_full", 2)
    ho_knownT2 = HR("known_t_full_full", 2)

    n_completable = int(_nm([m["n_completable"] for m in per_seed]))
    n_heldout = int(_nm([m["n_heldout_chains"] for m in per_seed]))

    # ---- anti-saturation + baseline-in-band + MM discriminator ----
    hop1_present = bool(mem1 == mem1 and mem1 >= HOP1_PRESENT)
    baseline_in_band = bool(mem1 == mem1 and 0.05 < mem1 < BASE_IN_BAND_HI)
    baseline_collapses = bool(base2 == base2 and base1 == base1
                              and base2 <= BASE_COLLAPSE_ABS and base2 <= BASE_COLLAPSE_FRAC * max(base1, 1e-9))
    supplied_fires = bool(sup2 == sup2 and mem2 == mem2 and sup2 >= mem2 + SUPPLIED_FIRES_MIN)
    enough_completable = bool(n_completable >= MIN_COMPLETABLE_CHAINS)

    # ---- discriminator gates ----
    readout_adds_signal = bool(best_strong_learned1 == best_strong_learned1 and memctrl_c1 == memctrl_c1
                               and best_strong_learned1 >= memctrl_c1 + NEC_MARGIN)
    weak_already_separates = bool(weak_margin1 == weak_margin1 and weak_margin1 >= WEAK_MARGIN_MAX)
    hp = bool(best_strong_margin1 == best_strong_margin1 and best_strong_margin1 >= READOUT_MARGIN_HP
              and weak_margin1 == weak_margin1 and weak_margin1 < WEAK_MARGIN_MAX
              and best_strong_margin1 >= weak_margin1 + STRONG_OVER_WEAK_MIN
              and readout_adds_signal)
    hf = bool(best_strong_margin1 == best_strong_margin1 and best_strong_margin1 < READOUT_MARGIN_MID)

    # ---- Gate-D reproduction (FULL only) ----
    is_full = bool(len(cfg["seeds"]) == 3 and cfg["n_nodes"] == 5000 and cfg["code_dim"] == 2048)
    repro_mem1_ok = bool(mem1 == mem1 and abs(mem1 - REPRO_MEM1) <= REPRO_TOL)
    repro_sup1_ok = bool(sup1 == sup1 and abs(sup1 - REPRO_SUP1) <= REPRO_TOL)
    repro_sup2_ok = bool(sup2 == sup2 and abs(sup2 - REPRO_SUP2) <= REPRO_TOL)
    repro_knownt2_ok = bool(knownT2 == knownT2 and abs(knownT2 - REPRO_KNOWNT2) <= REPRO_TOL)
    repro_weakl2_ok = bool(wl_full2 == wl_full2 and abs(wl_full2 - REPRO_WEAK_LEARNED2) <= REPRO_TOL)
    repro_weakr2_ok = bool(wr_full2 == wr_full2 and abs(wr_full2 - REPRO_WEAK_RANDOM2) <= REPRO_TOL)
    repro_ok = bool(repro_mem1_ok and repro_sup1_ok and repro_sup2_ok and repro_knownt2_ok
                    and repro_weakl2_ok and repro_weakr2_ok)

    if not hop1_present:
        verdict = "INCONCLUSIVE_HOP1_ABSENT"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif not supplied_fires:
        verdict = "INCONCLUSIVE_SUPPLIED_MM_DID_NOT_FIRE"
    elif not enough_completable:
        verdict = "INCONCLUSIVE_TOO_FEW_COMPLETABLE_CHAINS"
    elif is_full and not repro_ok:
        verdict = "INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT"
    elif weak_already_separates:
        verdict = "MIDDLE_BAND_WEAK_ALREADY_SEPARATES"
    elif hp:
        verdict = "HARD_PASS_READOUT_WAS_THE_LIMIT"
    elif hf:
        verdict = "HARD_FAIL_ENCODER_CONFIRMED"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_READOUT_RESCUE"

    verdict_msg = (
        "%s || NO_CLEANUP @1=%.3f @2=%.3f(collapses=%s) || MEMORYLESS @1=%.3f(in_band=%s) @2=%.3f || "
        "SUPPLIED @1=%.3f @2=%.3f(fires=%s) || KNOWN_T_FULL @1=%.3f @2=%.3f || COMPLETABLE[n=%d/%d]: "
        "WEAK L@1=%.3f R@1=%.3f (margin=%s) | KERNEL L@1=%.3f R@1=%.3f (margin=%s) | RIDGE L@1=%.3f R@1=%.3f "
        "(margin=%s) | MEMCTRL@1=%.3f || KEY: best_strong_margin@1=%s (won=%s) weak_margin@1=%s "
        "strong-weak=%s readout_adds_signal=%s || @2: kernel_margin=%s ridge_margin=%s weak_margin=%s "
        "best_strong=%s || FULL-HELDOUT: WEAK L@2=%.3f R@2=%.3f ho_mem@2=%.3f ho_knownT@2=%.3f || "
        "HARD_PASS(strong>=%.2f AND weak<%.2f AND strong>=weak+%.2f AND adds_signal)=%s "
        "HARD_FAIL(best_strong<%.2f)=%s || repro(full=%s): mem1=%s sup1=%s sup2=%s knownT2=%s weakL2=%s weakR2=%s "
        "|| withheld=%.1f%% nodes=%d E=%d seeds=%d run=%s" % (
            verdict, base1, base2, baseline_collapses, mem1, baseline_in_band, mem2,
            sup1, sup2, supplied_fires, knownT1, knownT2, n_completable, n_heldout,
            wl1, wr1, _fmt(weak_margin1), kl1, kr1, _fmt(kernel_margin1), rl1, rr1, _fmt(ridge_margin1),
            memctrl_c1, _fmt(best_strong_margin1), which_won, _fmt(weak_margin1),
            _fmt(best_strong_margin1 - weak_margin1 if (best_strong_margin1 == best_strong_margin1
                 and weak_margin1 == weak_margin1) else float("nan")), readout_adds_signal,
            _fmt(kernel_margin2), _fmt(ridge_margin2), _fmt(weak_margin2), _fmt(best_strong_margin2),
            wl_full2, wr_full2, ho_mem2, ho_knownT2,
            READOUT_MARGIN_HP, WEAK_MARGIN_MAX, STRONG_OVER_WEAK_MIN, hp, READOUT_MARGIN_MID, hf,
            is_full, repro_mem1_ok, repro_sup1_ok, repro_sup2_ok, repro_knownt2_ok, repro_weakl2_ok, repro_weakr2_ok,
            100.0 * _nm([m["withheld_frac_actual"] for m in per_seed]), meta["n_nodes"], meta["n_edges"],
            len(per_seed), "full" if is_full else "smoke"))

    gates = dict(
        verdict=verdict,
        reach_general={a: {dd: G(a, dd) for dd in range(1, MAX_REACH + 1)} for a in GENERAL_ARMS},
        completable={a: {dd: HC(a, dd) for dd in range(1, MAX_REACH + 1)} for a in HELDOUT_ARMS},
        heldout_full={a: {dd: HF(a, dd) for dd in range(1, MAX_REACH + 1)} for a in HELDOUT_ARMS},
        key=dict(weak_margin_reach1=weak_margin1, kernel_margin_reach1=kernel_margin1,
                 ridge_margin_reach1=ridge_margin1, best_strong_margin_reach1=best_strong_margin1,
                 which_won=which_won, best_strong_learned_reach1=best_strong_learned1,
                 memctrl_completable_reach1=memctrl_c1, readout_adds_signal=readout_adds_signal,
                 strong_minus_weak_reach1=(best_strong_margin1 - weak_margin1
                                           if (best_strong_margin1 == best_strong_margin1
                                               and weak_margin1 == weak_margin1) else float("nan")),
                 weak_margin_reach2=weak_margin2, kernel_margin_reach2=kernel_margin2,
                 ridge_margin_reach2=ridge_margin2, best_strong_margin_reach2=best_strong_margin2,
                 hp_readout_was_the_limit=hp, hf_encoder_confirmed=hf,
                 weak_already_separates=weak_already_separates,
                 n_completable=n_completable, n_heldout=n_heldout,
                 weak_learned_full_reach1=wl_full1, weak_random_full_reach1=wr_full1,
                 weak_learned_full_reach2=wl_full2, weak_random_full_reach2=wr_full2,
                 heldout_memoryless_reach2=ho_mem2, heldout_known_t_full_reach2=ho_knownT2),
        anti_sat=dict(hop1_present=hop1_present, baseline_in_band=baseline_in_band,
                      baseline_collapses=baseline_collapses, supplied_fires=supplied_fires,
                      enough_completable=enough_completable),
        positive_control=dict(is_full=is_full, repro_mem1=mem1, repro_sup1=sup1, repro_sup2=sup2,
                              repro_knownt2=knownT2, repro_weak_learned2=wl_full2, repro_weak_random2=wr_full2,
                              repro_mem1_ok=repro_mem1_ok, repro_sup1_ok=repro_sup1_ok, repro_sup2_ok=repro_sup2_ok,
                              repro_knownt2_ok=repro_knownt2_ok, repro_weakl2_ok=repro_weakl2_ok,
                              repro_weakr2_ok=repro_weakr2_ok, repro_ok=repro_ok,
                              anchors=dict(mem1=REPRO_MEM1, sup1=REPRO_SUP1, sup2=REPRO_SUP2, knownT2=REPRO_KNOWNT2,
                                           weak_learned2=REPRO_WEAK_LEARNED2, weak_random2=REPRO_WEAK_RANDOM2,
                                           tol=REPRO_TOL)),
        bands=dict(READOUT_MARGIN_HP=READOUT_MARGIN_HP, READOUT_MARGIN_MID=READOUT_MARGIN_MID,
                   WEAK_MARGIN_MAX=WEAK_MARGIN_MAX, STRONG_OVER_WEAK_MIN=STRONG_OVER_WEAK_MIN,
                   NEC_MARGIN=NEC_MARGIN, MIN_COMPLETABLE_CHAINS=MIN_COMPLETABLE_CHAINS,
                   KRR_ELL=KRR_ELL, KRR_LAM=KRR_LAM, RIDGE_LAM=RIDGE_LAM, WITHHELD_FRAC=WITHHELD_FRAC,
                   SMOOTH_K=SMOOTH_K, SMOOTH_TEMP=SMOOTH_TEMP, SR_GAMMA_PRIMARY=SR_GAMMA_PRIMARY, SR_BOOST=SR_BOOST),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test. Planted BRANCH graph with a WITHHELD hop-1 decision whose reachability IS
# recoverable from code-near VISIBLE nodes: the true withheld successor's code is planted near its visible onward
# neighbor (which reaches G); off-siblings' codes near visible dead-ends (M_visible ~ 0). A STRONG readout (kernel /
# ridge) trained on VISIBLE (code -> reachability) predicts M_hat[true,G] >> M_hat[off,G] -> LEARNED picks the true
# successor (reach@1 high); with RANDOM codes the readout has no structure -> ties (~1/KSR). Also asserts
# run_sr_arm_capture is bit-identical to the certified run_sr_arm; NO_CLEANUP collapses; arms differ.
# ---------------------------------------------------------------------------

def _mechanism_selftest():
    device = torch.device("cpu")
    torch.manual_seed(0); np.random.seed(0)
    rng = np.random.default_rng(0)
    d = 96
    Tr = 4
    roles_t = torch.from_numpy(make_unitary_roles(Tr, d, np.random.default_rng(11))).to(device)

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
        S = _new(_l2t(torch.randn(1, d))[0])
        r0 = int(rng.integers(0, Tr))
        tail = []
        prev = None
        for hh in range(MAX_REACH - 1):
            tv = _new(_l2t(torch.randn(1, d))[0])
            tail.append(tv)
            if prev is not None:
                rr = int(rng.integers(0, Tr))
                dir_adj[prev].append((tv, rr)); dir_adj[tv].append((prev, rr))
            prev = tv
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
    sr_solver_vis = SRSolver(T_vis, device)
    Xvis = sr_solver_vis.columns(uniq_goals, SR_GAMMA_PRIMARY)

    # STRONG readouts (learned codes vs random codes) on the planted structure
    Xk_l = strong_kernel_ridge_columns(Zn, withheld, Xvis, KRR_ELL, KRR_LAM, device)
    Xk_r = strong_kernel_ridge_columns(Zn_alias, withheld, Xvis, KRR_ELL, KRR_LAM, device)
    Xr_l = strong_linear_ridge_columns(Zn, withheld, Xvis, RIDGE_LAM, device)
    Xr_r = strong_linear_ridge_columns(Zn_alias, withheld, Xvis, RIDGE_LAM, device)
    sr_p_k_l, _, _ = _norm_columns_to_sr_p(Xk_l, goals, n, device)
    sr_p_k_r, _, _ = _norm_columns_to_sr_p(Xk_r, goals, n, device)
    sr_p_r_l, _, _ = _norm_columns_to_sr_p(Xr_l, goals, n, device)
    sr_p_r_r, _, _ = _norm_columns_to_sr_p(Xr_r, goals, n, device)

    # held-out chains: hop-1 target withheld
    hop1 = g_tgt[0]
    ho = np.where(withheld[hop1] & (~withheld[goals]))[0]
    gs = g_start[ho]
    gt = [g_tgt[hh][ho] for hh in range(MAX_REACH)]
    gr = [g_role[hh][ho] for hh in range(MAX_REACH)]

    r_no, _h, _sa, s_no = ft_run_no_cleanup(Z, roles_t, g_start, g_tgt, g_role, device, n)

    kl = run_sr_arm_capture(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr, device, 256, n, sr_p_k_l[ho], SR_BOOST)
    kr = run_sr_arm_capture(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr, device, 256, n, sr_p_k_r[ho], SR_BOOST)
    rl = run_sr_arm_capture(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr, device, 256, n, sr_p_r_l[ho], SR_BOOST)
    rr = run_sr_arm_capture(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr, device, 256, n, sr_p_r_r[ho], SR_BOOST)

    # capture-equivalence: run_sr_arm_capture must be bit-identical to the certified run_sr_arm
    v_reach, _vh, v_sig = run_sr_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, gs, gt, gr, device, 256, n, sr_p_k_l[ho],
                                     SR_BOOST)
    capture_matches = bool(v_sig == kl["sig"] and all(abs(v_reach[dd] - kl["reach"][dd]) < 1e-9
                                                       for dd in range(1, MAX_REACH + 1)))

    n_ho = int(ho.shape[0])
    nocleanup_ran = bool(r_no[1] == r_no[1])
    kernel_recovers = bool(kl["reach"][1] == kl["reach"][1] and kl["reach"][1] >= 0.45)
    ridge_recovers = bool(rl["reach"][1] == rl["reach"][1] and rl["reach"][1] >= 0.45)
    kernel_codes_necessary = bool(kl["reach"][1] == kl["reach"][1] and kr["reach"][1] == kr["reach"][1]
                                  and kl["reach"][1] >= kr["reach"][1] + 0.15)
    ridge_codes_necessary = bool(rl["reach"][1] == rl["reach"][1] and rr["reach"][1] == rr["reach"][1]
                                 and rl["reach"][1] >= rr["reach"][1] + 0.15)
    arms_differ = bool(len({kl["sig"], kr["sig"], rl["sig"], rr["sig"], s_no}) >= 4)

    res = dict(n_synth=int(n), n_heldout=n_ho, n_withheld=int(withheld.sum()),
               reach_no_cleanup={dd: round(r_no[dd], 4) for dd in range(1, MAX_REACH + 1)},
               reach_kernel_learned={dd: round(kl["reach"][dd], 4) for dd in range(1, MAX_REACH + 1)},
               reach_kernel_random={dd: round(kr["reach"][dd], 4) for dd in range(1, MAX_REACH + 1)},
               reach_ridge_learned={dd: round(rl["reach"][dd], 4) for dd in range(1, MAX_REACH + 1)},
               reach_ridge_random={dd: round(rr["reach"][dd], 4) for dd in range(1, MAX_REACH + 1)},
               nocleanup_ran=nocleanup_ran, capture_matches=capture_matches,
               kernel_recovers=kernel_recovers, ridge_recovers=ridge_recovers,
               kernel_codes_necessary=kernel_codes_necessary, ridge_codes_necessary=ridge_codes_necessary,
               arms_differ=arms_differ, Dmax=int(Dmax))
    ok = bool(nocleanup_ran and capture_matches and kernel_recovers and ridge_recovers
              and kernel_codes_necessary and ridge_codes_necessary and arms_differ and n_ho >= 10)
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
            verdict_msg="SELFTEST_PASS readout-vs-encoder machinery: NO_CLEANUP collapses; run_sr_arm_capture bit-"
                        "identical to certified run_sr_arm; STRONG kernel + ridge readouts recover held-out hop-1 on "
                        "planted recoverable structure with LEARNED codes and collapse with RANDOM codes (codes "
                        "necessary under a strong readout); arms differ",
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
                          cfg, device, out_dir_path)
            for a in GENERAL_ARMS:
                missing = [dd for dd in range(1, MAX_REACH + 1) if dd not in pm["arms_general"].get(a, {})]
                if missing:
                    raise RuntimeError("ARM_DEPTH_CARDINALITY_BREACH seed=%d arm=%s missing=%s" % (seed, a, missing))
            if pm["n_heldout_chains"] >= 1:
                s = pm["arm_sigs"]
                for pair in [(WEAK_LEARNED, WEAK_RANDOM), (KERNEL_LEARNED, KERNEL_RANDOM),
                             (RIDGE_LEARNED, RIDGE_RANDOM), (KERNEL_LEARNED, WEAK_LEARNED)]:
                    if s[pair[0]] == s[pair[1]]:
                        raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d %s==%s" % (seed, pair[0], pair[1]))
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
