"""selfplay_dg_pattern_separation_xfit_v1 -- the brain-grounded FIX for the confirmed self-play
differentiation negative: does an UPSTREAM dentate-gyrus-style PATTERN-SEPARATION stage, layered onto the
disjoint-data cross-fit (B1) Speaker/Listener self-play, drive the two halves' failure masks GENUINELY
INDEPENDENT while RETAINING grounding -- the sweet spot plain downstream differentiation (B1 alone) could
not reach?

WHY (Director steer 2026-07-09; drill
notes/research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md; landed-VET on the differentiation cell
exp_selfplay_differentiation_failmask_decorrelation_v1.py, commit 866f245b):
  The differentiation VET confirmed disjoint-data cross-fit (B1) is the revival axis (naive-mirror
  failmask-corr ~0.77 -> B1 ~0.39, grounding retained ~0.60) BUT insufficient alone (still ~2x the
  independence bar ~0.20). The reconciliation drill established brain-consensus across FOUR independent
  literatures (CLS/hippocampus, predictive-coding/active-inference, precision-weighting/arbitration,
  dentate-gyrus pattern separation + failure modes): the brain fixes a shared-UPSTREAM blind spot by
  DECORRELATING THE CODE BEFORE THE SPLIT (dentate-gyrus pattern separation), NOT by downstream
  reconciliation or precision-weighting (those are CONSUMERS, not PRODUCERS, of independence). The
  load-bearing mechanism is a sparse random-expansion + competitive-sparsification transform applied to the
  shared representation BEFORE it is split -- structurally the DG move on entorhinal input before CA3.

MECHANISM UNDER TEST (P_deflated ~0.30-0.35 the specific translation clears HARD-PASS; mechanism-translation
  risk from biological circuit to this cross-fit setup):
  Onto the B1 disjoint-data cross-fit arm, add a FIXED, INDEPENDENTLY-SEEDED sparse random-projection
  (expansion) + top-k sparsification (DG-style pattern separation) stage PER BRANCH, upstream of the encoder
  split. Zero new learned params -- DG's largely non-plastic, randomly-wired expansion layer. REUSES the
  built + unit-tested hdlab.hippocampal_encoder.DGProjection VERBATIM (random bipolar expansion feat->dg_dim
  + sign-preserving top-K threshold -> ternary sparse code; its own selftest _st_dg_pattern_separation PASSES
  with a measured decorrelation gap code_cos < input_cos - 0.20). The DG codes become the encoder's input
  features; the encoders then train cross-fit (disjoint folds) exactly as B1. DG_XFIT vs B1 differ ONLY by
  the DG stage -> the controlled comparison isolates the DG contribution.

THREE ARMS (per Director task):
  B0_mirror (MUST-FAIL control): Enc_S and Enc_L are the SAME tied module, differ only in info access
     (Speaker: neighborhood-augmented Xn; Listener: bare X). Predicted HIGH failmask-corr (~0.77 -- the
     shared-blind-spot signature). If B0 does NOT fire (>=0.40) at smoke the screen is saturation-vacuous
     and MUST re-spec (assert_discriminator_fires).
  B1_crossfit (the ~0.39 axis being improved): separate Enc_S/Enc_L; Speaker params fit ONLY on referent
     fold A, Listener params ONLY on disjoint fold B (channel P shared). No DG stage.
  DG_XFIT (the TREATMENT): B1 cross-fit + per-branch independently-seeded fixed DG pattern-separation stage
     (P_speaker, P_listener) upstream of the encoder split. Speaker's Xn -> Xn_dg (seed_s); Listener's
     X -> X_dg (seed_l, INDEPENDENT). Encoders take the DG codes as features; train cross-fit as B1.

THE SCREEN (reused VERBATIM from exp_selfplay_differentiation_failmask_decorrelation_v1.py which reused it
  from exp_pfc_gate_waypoint_rescue_stacked_corrections_v1.py:failure_mask_corr):
  Per referent r over a fixed eval set, two INDEPENDENT per-half competence outcomes on the SAME decision:
    speaker_correct[r] = argmax_c P[m(r)] . Enc_S(view_S[c]) == r  (speaker self-decode, privileged view)
    listener_correct[r] = argmax_c P[m(r)] . Enc_L(view_L[c]) == r (actual listener, bare view; == the JOINT
                                                                     communicative-grounding event)
  failmask_corr(arm) = corr(1-speaker_correct, 1-listener_correct) over referents (phi coefficient).
  grounding_acc(arm) = mean(listener_correct) = joint game success (decorrelation is void if it destroys
  this; the grounding FLOOR guards it).

PRE-REGISTERED BANDS (BOTH; LOCKED PROSPECTIVE; per drill S2 falsifiable predictions):
  HARD_PASS (upstream pattern-separation cracks the self-grounding barrier):
    DG_XFIT failmask_corr <= 0.20 (at/below the independence bar) AND grounding_acc >= 0.50 AND
    (B1_crossfit corr - DG_XFIT corr) >= 0.10 (the DG stage MATERIALLY improved over cross-fit alone, not
    seed noise) AND all arms' message codes non-degenerate (entropy >= 1.0 bit, >=2 symbols) AND the DG
    codes non-degenerate (decorrelate raw features + sparse-rate in band + distinct rows) AND B0 fires
    (corr >= 0.40, both halves in failure band [0.05,0.95]).
  HARD_FAIL case (a) -- representation-level fix INSUFFICIENT (the drill's flagged next step):
    DG_XFIT failmask_corr >= 0.35 (no material improvement over B1's own 0.39) WHILE grounding retained
    (>=0.50) => the shared blind spot is very likely DISTRIBUTION/OBJECTIVE-level, not representation-level;
    a per-branch representational transform cannot fix it. REDIRECT to an exogenous-referent / held-out-
    reconstruction mechanism (Thread 2). This HARD_FAIL is itself diagnostic, not a dead end.
  HARD_FAIL case (b) -- over-aggressive sparsification DESTROYS grounding:
    DG_XFIT grounding_acc < 0.40 (even if corr improves) => the DG stage strips referential/semantic content
    along with correlated noise. Fix = restrict pattern separation to a non-semantic subspace (scoped
    variant), not abandonment.
  MIDDLE_BAND: DG_XFIT corr in (0.20, 0.35] with grounding >= 0.50 -> sweep sparsity/expansion before
    concluding (one hyperparameter sweep, not a full re-drill).
  SATURATION_VACUOUS: B0 failmask_corr < 0.40 at smoke OR B0 failure-rate degenerate => discriminator not
    firing; re-spec (tighten K / distractor difficulty). Do NOT trust full.
  CODE_COLLAPSE_VOID: any arm's message code collapsed (entropy < 1.0 bit) => emergent-comm degenerate-code
    artifact; the whole test is void.
  DG_CODE_DEGENERATE_VOID: the DG stage failed to decorrelate (code_cos not below input_cos) OR collapsed
    (sparse-rate out of band / rows not distinct) => the DG mechanism did not fire; re-spec expansion/sparsity.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): the 3 arms' (speaker,listener) mask-pair vectors hashed;
#   B0 vs B1 vs DG_XFIT must all differ (exempt none). Bit-identical arms => arm-implementation bug.
# - final_metrics_atomicity: tmp_replace (write_metrics -> os.replace; crash-diag atomic).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the discriminator is a failure-mask CORRELATION vs a within-cell MUST-FAIL control (B0), not a
#   closed-form noise floor; reachability by construction (B0 fires high corr; the treatment sits in
#   [0, corr(B0)]; HP bar corr<=0.20 with material-improvement margin >=0.10 vs B1 is inside).
# - baseline_in_band (AG): B0 (the MUST-FAIL mirror) failure rates must be 0.05..0.95 for BOTH halves at
#   smoke (else corr degenerate / task saturated -> re-spec K or distractor difficulty).
# - discriminator survives scale: smoke = FULL branches at smaller n_nodes/epochs/K, SAME dg_expansion(2x)
#   + dg_sparsity ratio (mechanism-ratio parity). SMOKE MUST show B0 failmask_corr >= 0.40
#   (assert_discriminator_fires) AND DG codes decorrelate (code_cos < input_cos) before any FULL dispatch.
#   Smoke K(=12) < FULL K(=24) -> higher collision pressure -> smoke grounding is a conservative LOWER bound.
# - multi-seed smoke (3 seeds) for the correlation-discriminator per META_RULE_smoke_single_seed_inflates_AUC.
# - HARD_PASS strictly above floor: corr(DG)<=0.20 AND improvement>=0.10 AND grounding>=0.50 (all strict).
# - HP_SCOPE: decorrelation HP gates apply to {DG_XFIT} vs {B0 fires, B1 reference}; screen-fires gate to B0;
#   grounding floor to DG_XFIT; anti-collapse to ALL arms; DG-code non-degeneracy to DG_XFIT only.
# - cardinality_ok: EXPECTED_N_UNITS = n_arms(3) * n_seeds (no sweep axis; arms x seeds).
# - per-unit failure-class instrumentation (no bare except; per-(seed,arm) fatal-flag + failure_class).
# - calibration_check: adaptive_with_discriminator_gate (K + Gumbel tau + dg_expansion/sparsity fixed per
#   profile; anti-collapse entropy floor + B0-fires + baseline-in-band + DG-fires recomputed per run).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.

Compute architecture: (c) mixed sequential-CPU with justification. Encoders are shallow linear ProjHeads
(feat/dg_dim->code) + a K x code channel; per-step ops are batched matmuls / gumbel-softmax / candidate
scoring. The DG stage is a one-time fixed bipolar-projection matmul + top-k per branch per seed (numpy BLAS).
Not GPU-batching-mandatory: nets small (code_dim<=192, dg_dim<=16384), the cost is the self-play training
loop (sequential over epochs, genuine dependency) and 3 arms x 5 seeds is minutes-to-low-tens-of-minutes on
CPU. Storage strategy: no_storage (no PartitionedStore writes; codes are transient encoder outputs).
progress_logging: print_flush_true (line-buffered stdout + flush=True progress lines + per (seed,arm)
heartbeat; FULL timeout_s >= 1800).

Reuses VERBATIM from experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py: load_cn_subgraph,
char_trigram_features, build_adjlist, ProjHead, info_nce, vicreg_repulsion, _l2norm. Reuses VERBATIM from
experiments/exp_pfc_gate_waypoint_rescue_stacked_corrections_v1.py: failure_mask_corr. Reuses VERBATIM from
hdlab/hippocampal_encoder.py: DGProjection (the DG pattern-separation stage). Structurally adapts the 4-arm
naming-game + anti-collapse bottleneck from exp_selfplay_differentiation_failmask_decorrelation_v1.py. NEW
(additive): the DG_XFIT arm (per-branch DG stage on the cross-fit arm), the DG-code non-degeneracy gate, the
DG-vs-B1 improvement-margin verdict.
"""

import argparse
import hashlib
import json
import math
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
    load_cn_subgraph,
    char_trigram_features,
    build_adjlist,
    ProjHead,
    info_nce,
    vicreg_repulsion,
    _l2norm,
)
from hdlab.hippocampal_encoder import DGProjection  # noqa: E402

ANCHOR_NAME = "selfplay_dg_pattern_separation_xfit_v1"
SUBGRAPH_BASE_SEED = 1234

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; scale + mechanism-ratio parity)
# dg_dim = 2 * feat_dim (constant 2x expansion); dg_sparsity constant -> mechanism ratio preserved.
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    n_nodes=300, seeds=[7], epochs=12, batch=128,
    code_dim=32, feat_dim=512, dg_dim=1024, dg_sparsity=0.05,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05, lambda_ent=0.1,
    K=8, n_dist=5, gumbel_tau=2.0, gumbel_tau_end=0.5, neighbor_weight=0.5, n_eval=150,
)
SMOKE_CFG = dict(
    n_nodes=1500, seeds=[7, 13, 17], epochs=80, batch=256,
    code_dim=96, feat_dim=4096, dg_dim=8192, dg_sparsity=0.08,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05, lambda_ent=0.1,
    K=12, n_dist=7, gumbel_tau=2.0, gumbel_tau_end=0.5, neighbor_weight=0.5, n_eval=700,
)
FULL_CFG = dict(
    n_nodes=8000, seeds=[7, 13, 17, 23, 29], epochs=220, batch=512,
    code_dim=192, feat_dim=8192, dg_dim=16384, dg_sparsity=0.08,
    temp=0.12, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05, lambda_ent=0.1,
    K=24, n_dist=9, gumbel_tau=2.0, gumbel_tau_end=0.4, neighbor_weight=0.5, n_eval=3000,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (LOCKED; PROSPECTIVE)
# ---------------------------------------------------------------------------
B0_FAILMASK_CORR_MIN = 0.40    # HARD_PASS gate + assert_discriminator_fires: mirror shows shared-blind-spot
DG_FAILMASK_CORR_HP = 0.20     # HARD_PASS: DG_XFIT decorrelates at/below the independence bar
DG_IMPROVE_MARGIN = 0.10       # HARD_PASS: (B1 corr - DG corr) >= this (DG stage materially beat cross-fit)
GROUNDING_FLOOR = 0.50         # HARD_PASS: DG_XFIT still communicates (>> chance 1/(1+n_dist))
DG_FAILMASK_CORR_HF_A = 0.35   # HARD_FAIL(a): DG corr >= this while grounding retained -> exogenous redirect
GROUNDING_DESTROYED = 0.40     # HARD_FAIL(b): DG grounding < this -> over-aggressive sparsification
ENTROPY_FLOOR_BITS = 1.0       # anti-collapse: message code entropy floor (>=~2 effective symbols)
MIN_SYMBOLS_USED = 2           # anti-collapse: at least 2 distinct symbols in use
FAILRATE_LO = 0.05             # B0 baseline_in_band lower edge (both halves)
FAILRATE_HI = 0.95             # B0 baseline_in_band upper edge (both halves)
# DG-code non-degeneracy gate (DG_XFIT only)
DG_DECORR_MIN_GAP = -0.03      # soft guard: DG must not PATHOLOGICALLY INCREASE within-branch code similarity
                               # (input_cos - code_cos >= this; near-orthogonal text features give small gaps)
DG_DISTINCT_FRAC_MIN = 0.90    # DG rows must be mostly distinct (no mass collision)
DG_SPARSE_RATE_ABS_LO = 0.005  # absolute sparse-rate band: guards EMPTY collapse (near-0 active)
DG_SPARSE_RATE_ABS_HI = 0.30   # guards DENSE collapse (no sparsification, ->1.0). Wide enough to tolerate
                               # the benign top-k tie-inflation on very-sparse bare char-trigram inputs
                               # (DGProjection's mag>=thresh includes ties; distinct_frac is the real
                               # collapse guard). A code with <30% active is still a genuine sparse code.

ARM_NAMES = ["B0_mirror", "B1_crossfit", "DG_XFIT"]
CROSSFIT_ARMS = ["B1_crossfit", "DG_XFIT"]
DG_ARM = "DG_XFIT"
B1_ARM = "B1_crossfit"
MIRROR_ARM = "B0_mirror"

CONFIG_VERSION = (
    "ANCHOR=%s,arms=%s,B0corr>=%.2f,DGcorr<=%.2f,margin>=%.2f,ground>=%.2f,HFa>=%.2f,HFb_ground<%.2f,"
    "ent>=%.2f,failband=[%.2f,%.2f],dg_decorr_gap>=%.2f"
) % (ANCHOR_NAME, ARM_NAMES, B0_FAILMASK_CORR_MIN, DG_FAILMASK_CORR_HP, DG_IMPROVE_MARGIN,
     GROUNDING_FLOOR, DG_FAILMASK_CORR_HF_A, GROUNDING_DESTROYED, ENTROPY_FLOOR_BITS,
     FAILRATE_LO, FAILRATE_HI, DG_DECORR_MIN_GAP)

_T0 = time.time()
RUN_MODE_GLOBAL = "full"


# ---------------------------------------------------------------------------
# Defensive error-checking scaffolding (SCHEMA-VET section 13)
# ---------------------------------------------------------------------------
def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


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
    diag = dict(verdict="CELL_CRASHED",
                verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__),
                elapsed_s=round(time.time() - _T0, 1), traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME, run_mode=RUN_MODE_GLOBAL, config_version=CONFIG_VERSION)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir, unit_idx, total, note=""):
    try:
        row = dict(ts_iso=datetime.now(timezone.utc).isoformat(), unit_idx=unit_idx,
                   total_units=total, elapsed_s=round(time.time() - _T0, 1), note=note)
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# REUSED VERBATIM from exp_pfc_gate_waypoint_rescue_stacked_corrections_v1.py
# ---------------------------------------------------------------------------
def failure_mask_corr(kb_correct, sel_correct):
    """corr(failure_mask_A, failure_mask_B) over per-referent final correctness. Near-zero => independent
    failures. High => shared blind spots. Degenerate (an arm all-right/all-wrong) => corr=0 flagged."""
    fa = (~np.asarray(kb_correct).astype(bool)).astype(np.float64)
    fb = (~np.asarray(sel_correct).astype(bool)).astype(np.float64)
    if fa.std() < 1e-9 or fb.std() < 1e-9:
        return {"failmask_corr": 0.0, "failmask_kb_rate": float(fa.mean()),
                "failmask_sel_rate": float(fb.mean()), "failmask_degenerate": True,
                "n_failmask_units": int(len(fa))}
    corr = float(np.corrcoef(fa, fb)[0, 1])
    return {"failmask_corr": corr, "failmask_kb_rate": float(fa.mean()),
            "failmask_sel_rate": float(fb.mean()), "failmask_degenerate": False,
            "n_failmask_units": int(len(fa))}


# ---------------------------------------------------------------------------
# Referent world helpers
# ---------------------------------------------------------------------------
def neighborhood_augment(X, adj, neighbor_weight):
    """Speaker's PRIVILEGED info access: node feature + neighbor_weight * mean-neighbor feature,
    L2-normalized. Nodes with no neighbors keep the bare feature. Shape [n, feat_dim]."""
    n, d = X.shape
    Xn = X.copy().astype(np.float64)
    for i in range(n):
        nb = adj[i]
        if len(nb) == 0:
            continue
        Xn[i] = X[i] + neighbor_weight * X[np.asarray(nb, dtype=np.int64)].mean(axis=0)
    norms = np.linalg.norm(Xn, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return (Xn / norms).astype(np.float32)


def build_candidate_sets(eval_idx, n_nodes, n_dist, rng):
    """Fixed random distractor sets. Returns cand [M, 1+n_dist] int64 with col0 = target."""
    m = eval_idx.shape[0]
    cand = np.zeros((m, 1 + n_dist), dtype=np.int64)
    cand[:, 0] = eval_idx
    for i in range(m):
        tgt = int(eval_idx[i])
        picks = set()
        while len(picks) < n_dist:
            c = int(rng.integers(0, n_nodes))
            if c != tgt:
                picks.add(c)
        cand[i, 1:] = np.asarray(sorted(picks), dtype=np.int64)
    return cand


class MessageChannel(torch.nn.Module):
    """Shared K-symbol prototype matrix P [K, code_dim] -- the communication bottleneck (shared across ALL
    arms). Speaker logits = z_S @ P.t(); message-vector = onehot(symbol) @ P."""

    def __init__(self, K, code_dim):
        super().__init__()
        self.P = torch.nn.Parameter(torch.randn(K, code_dim) * (1.0 / math.sqrt(code_dim)))


def _make_encoder(feat_dim, code_dim, seed):
    torch.manual_seed(seed)
    return ProjHead(feat_dim, code_dim)


def _symbol_entropy_bits(symbols, K):
    """Marginal message-symbol entropy in bits + number of distinct symbols used."""
    counts = np.bincount(np.asarray(symbols, dtype=np.int64), minlength=K).astype(np.float64)
    p = counts / max(counts.sum(), 1.0)
    nz = p[p > 0]
    ent = float(-(nz * np.log2(nz)).sum()) if nz.size else 0.0
    return ent, int((counts > 0).sum())


def _mean_pairwise_cos(A, rng, n_pairs=2000):
    """Mean absolute pairwise cosine over random row-pairs of A [n, d]. DG diagnostics."""
    n = A.shape[0]
    if n < 2:
        return 0.0
    i = rng.integers(0, n, size=n_pairs)
    j = rng.integers(0, n, size=n_pairs)
    keep = i != j
    i, j = i[keep], j[keep]
    a = A[i].astype(np.float64)
    b = A[j].astype(np.float64)
    na = np.linalg.norm(a, axis=1) + 1e-12
    nb = np.linalg.norm(b, axis=1) + 1e-12
    cos = (a * b).sum(axis=1) / (na * nb)
    return float(np.mean(np.abs(cos)))


def build_dg_features(X, Xn, cfg, seed):
    """Per-branch INDEPENDENTLY-SEEDED fixed DG pattern-separation (DGProjection) upstream of the split.
    Speaker: Xn -> Xn_dg (seed_s); Listener: X -> X_dg (seed_l, independent). Returns (Xn_dg, X_dg, diag)."""
    feat_dim = X.shape[1]
    dg_dim = cfg["dg_dim"]
    sp = cfg["dg_sparsity"]
    dg_s = DGProjection(input_dim=feat_dim, dg_dim=dg_dim, sparsity=sp, seed=seed * 13 + 5001)
    dg_l = DGProjection(input_dim=feat_dim, dg_dim=dg_dim, sparsity=sp, seed=seed * 13 + 6001)
    Xn_dg = dg_s.encode_batch(Xn).astype(np.float32)
    X_dg = dg_l.encode_batch(X).astype(np.float32)
    rng = np.random.default_rng(seed + 4242)
    # DG-fires diagnostics: pattern separation should REDUCE pairwise similarity vs raw features
    input_cos_s = _mean_pairwise_cos(Xn, rng)
    code_cos_s = _mean_pairwise_cos(Xn_dg, rng)
    input_cos_l = _mean_pairwise_cos(X, rng)
    code_cos_l = _mean_pairwise_cos(X_dg, rng)
    sparse_rate_s = float(np.count_nonzero(Xn_dg)) / float(Xn_dg.size)
    sparse_rate_l = float(np.count_nonzero(X_dg)) / float(X_dg.size)
    distinct_frac_s = float(len(np.unique(Xn_dg, axis=0))) / float(Xn_dg.shape[0])
    distinct_frac_l = float(len(np.unique(X_dg, axis=0))) / float(X_dg.shape[0])
    diag = dict(
        dg_dim=int(dg_dim), dg_sparsity_target=float(sp),
        input_cos_speaker=input_cos_s, code_cos_speaker=code_cos_s,
        input_cos_listener=input_cos_l, code_cos_listener=code_cos_l,
        decorr_gap_speaker=input_cos_s - code_cos_s, decorr_gap_listener=input_cos_l - code_cos_l,
        sparse_rate_speaker=sparse_rate_s, sparse_rate_listener=sparse_rate_l,
        distinct_frac_speaker=distinct_frac_s, distinct_frac_listener=distinct_frac_l,
    )
    return Xn_dg, X_dg, diag


def _dg_nondegenerate(diag, cfg):
    """DG-fires gate (the task's explicit 'DG must NOT collapse codes' guard). ConceptNet referents are
    distinct words -> char-trigram features are already near-orthogonal, so DG's classic 'separate SIMILAR
    inputs' role is NOT the active ingredient here (the active ingredient is the INDEPENDENT per-branch
    coding transform giving the two encoders decorrelated inductive biases -- the CLS coding-statistics
    move). Therefore this gate checks CODE NON-DEGENERACY (not within-branch separation): sparse-rate in
    band (not saturated / not empty) AND rows mostly distinct (no mass collision). The within-branch
    decorr_gap is retained as a LOGGED diagnostic, and a soft guard rejects only PATHOLOGICAL correlation
    INCREASE (DG making codes more similar than raw features). Returns (ok, reasons)."""
    lo, hi = DG_SPARSE_RATE_ABS_LO, DG_SPARSE_RATE_ABS_HI
    reasons = []
    if not (lo <= diag["sparse_rate_speaker"] <= hi):
        reasons.append("speaker_sparse_rate_oob(%.4f not in [%.4f,%.4f])" % (diag["sparse_rate_speaker"], lo, hi))
    if not (lo <= diag["sparse_rate_listener"] <= hi):
        reasons.append("listener_sparse_rate_oob(%.4f not in [%.4f,%.4f])" % (diag["sparse_rate_listener"], lo, hi))
    if diag["distinct_frac_speaker"] < DG_DISTINCT_FRAC_MIN:
        reasons.append("speaker_rows_collide(%.3f)" % diag["distinct_frac_speaker"])
    if diag["distinct_frac_listener"] < DG_DISTINCT_FRAC_MIN:
        reasons.append("listener_rows_collide(%.3f)" % diag["distinct_frac_listener"])
    # soft guard: DG must not PATHOLOGICALLY INCREASE within-branch similarity (gap must not be strongly neg)
    if diag["decorr_gap_speaker"] < DG_DECORR_MIN_GAP:
        reasons.append("speaker_dg_increases_corr(gap=%.3f<%.2f)" % (diag["decorr_gap_speaker"], DG_DECORR_MIN_GAP))
    if diag["decorr_gap_listener"] < DG_DECORR_MIN_GAP:
        reasons.append("listener_dg_increases_corr(gap=%.3f<%.2f)" % (diag["decorr_gap_listener"], DG_DECORR_MIN_GAP))
    return (len(reasons) == 0), reasons


# ---------------------------------------------------------------------------
# Per-arm self-play training + evaluation
# ---------------------------------------------------------------------------
def _relational_positive_batch(adj_pool, adj, rng, batch):
    """Sample anchors (with a neighbor) + one random neighbor -> (a_idx, p_idx) for the InfoNCE reg."""
    a_idx = rng.choice(adj_pool, size=min(batch, adj_pool.shape[0]), replace=False)
    p_idx = np.array([adj[a][rng.integers(0, len(adj[a]))] for a in a_idx], dtype=np.int64)
    return a_idx.astype(np.int64), p_idx


def _forward_game(enc_s, enc_l, chan, Xn_t, X_t, tgt_idx, cand_idx, tau, s_grad, l_grad):
    """One referential episode forward. tgt_idx [B]; cand_idx [B, 1+ND] (col0=target). Returns
    (ref_loss, msg_soft [B,K]). s_grad/l_grad toggle which side accumulates gradient (cross-fit)."""
    B, C = cand_idx.shape
    zt = enc_s(Xn_t[tgt_idx])
    if not s_grad:
        zt = zt.detach()
    zt = _l2norm(zt)
    logits = zt @ chan.P.t()                                   # [B, K]
    msg = torch.nn.functional.gumbel_softmax(logits, tau=tau, hard=True)  # [B, K] straight-through
    msg_vec = msg @ chan.P                                     # [B, d]
    cand_flat = cand_idx.reshape(-1)
    zc = enc_l(X_t[cand_flat])
    if not l_grad:
        zc = zc.detach()
    zc = _l2norm(zc).reshape(B, C, -1)                         # [B, C, d]
    scores = (msg_vec.unsqueeze(1) * zc).sum(dim=-1)           # [B, C]
    labels = torch.zeros(B, dtype=torch.long)                  # target is col 0
    ref_loss = torch.nn.functional.cross_entropy(scores, labels)
    return ref_loss, msg


def _ent_reg(msg_soft, eps=1e-9):
    """Anti-collapse: maximize marginal symbol entropy (return NEGATIVE entropy to add to loss)."""
    marg = msg_soft.mean(dim=0)
    ent = -(marg * (marg + eps).log()).sum()
    return -ent


def train_arm(arm, cfg, X, Xn, adj, seed, n_nodes, out_dir, tag):
    """Train one arm's self-play game. Returns (enc_s, enc_l, chan). For DG_XFIT the caller passes DG-
    projected X/Xn (feat_dim = dg_dim); DG_XFIT routes through the cross-fit (disjoint-fold) path as B1."""
    feat_dim = X.shape[1]
    code_dim = cfg["code_dim"]
    Xn_t = torch.from_numpy(Xn)
    X_t = torch.from_numpy(X)
    rng = np.random.default_rng(seed + 101)

    all_idx = np.arange(n_nodes)
    rng.shuffle(all_idx)
    fold_a = np.sort(all_idx[: n_nodes // 2])
    fold_b = np.sort(all_idx[n_nodes // 2:])
    has_nb = np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool)

    chan = MessageChannel(cfg["K"], code_dim)
    is_crossfit = arm in CROSSFIT_ARMS
    if arm == MIRROR_ARM:
        enc_s = _make_encoder(feat_dim, code_dim, seed)
        enc_l = enc_s                                        # TIED (shared weights)
    else:  # B1_crossfit, DG_XFIT: separate encoders, cross-fit
        enc_s = _make_encoder(feat_dim, code_dim, seed)
        enc_l = _make_encoder(feat_dim, code_dim, seed + 333)

    s_params = list(enc_s.parameters()) + list(chan.parameters())
    opt_s = torch.optim.Adam(s_params, lr=cfg["lr"])
    if is_crossfit:
        opt_l = torch.optim.Adam(list(enc_l.parameters()), lr=cfg["lr"])
    else:
        opt_l = None

    log_every = max(1, cfg["epochs"] // 5)
    tau0 = cfg["gumbel_tau"]
    tau1 = cfg.get("gumbel_tau_end", cfg["gumbel_tau"])
    t_ep = time.perf_counter()
    for ep in range(cfg["epochs"]):
        tau_ep = tau0 + (tau1 - tau0) * (ep / max(1, cfg["epochs"] - 1))
        if is_crossfit:
            # Speaker step on fold A (updates enc_s + P; enc_l detached);
            # Listener step on fold B (updates enc_l + P; enc_s detached). Disjoint data per role.
            for (pool, opt, sg, lg) in ((fold_a, opt_s, True, False), (fold_b, opt_l, False, True)):
                if opt is None:
                    continue
                tgt = torch.from_numpy(rng.choice(pool, size=min(cfg["batch"], pool.shape[0]),
                                                   replace=False).astype(np.int64))
                cand = torch.from_numpy(build_candidate_sets(tgt.numpy(), n_nodes, cfg["n_dist"], rng))
                ref_loss, msg = _forward_game(enc_s, enc_l, chan, Xn_t, X_t, tgt, cand,
                                              tau_ep, s_grad=sg, l_grad=lg)
                loss = ref_loss + cfg["lambda_ent"] * _ent_reg(msg)
                opt.zero_grad()
                loss.backward()
                opt.step()
            loss_val = float(ref_loss.detach())
        else:  # B0_mirror: tied encoder, joint step + relational regularizer on raw features
            tgt_pool = np.nonzero(has_nb)[0]
            tgt = torch.from_numpy(rng.choice(tgt_pool, size=min(cfg["batch"], tgt_pool.shape[0]),
                                              replace=False).astype(np.int64))
            cand = torch.from_numpy(build_candidate_sets(tgt.numpy(), n_nodes, cfg["n_dist"], rng))
            ref_loss, msg = _forward_game(enc_s, enc_l, chan, Xn_t, X_t, tgt, cand,
                                          tau_ep, s_grad=True, l_grad=True)
            a_idx, p_idx = _relational_positive_batch(np.nonzero(has_nb)[0], adj, rng, cfg["batch"])
            za = enc_s(Xn_t[torch.from_numpy(a_idx)])
            zp = enc_s(Xn_t[torch.from_numpy(p_idx)])
            rel = info_nce(za, zp, cfg["temp"]) + vicreg_repulsion(
                torch.cat([za, zp], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
            loss = ref_loss + cfg["lambda_ent"] * _ent_reg(msg) + cfg["lambda_rel"] * rel
            opt_s.zero_grad()
            loss.backward()
            opt_s.step()
            loss_val = float(ref_loss.detach())

        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  train seed=%d %s ep=%d/%d ref_loss=%.4f (%.1fs)" % (
                seed, tag, ep, cfg["epochs"], loss_val, time.perf_counter() - t_ep))
            _heartbeat(out_dir, ep, cfg["epochs"], note="%s ref_loss=%.3f" % (tag, loss_val))
    return enc_s, enc_l, chan


def eval_masks(enc_s, enc_l, chan, Xn, X, eval_idx, cand_idx, K):
    """Per-referent independent competence of each half on the SAME decision. Returns dict with
    speaker_correct [M] bool, listener_correct [M] bool, symbols [M], grounding_acc, entropy."""
    Xn_t = torch.from_numpy(Xn)
    X_t = torch.from_numpy(X)
    eidx = torch.from_numpy(eval_idx.astype(np.int64))
    cand = torch.from_numpy(cand_idx.astype(np.int64))
    M, C = cand_idx.shape
    with torch.no_grad():
        zt = _l2norm(enc_s(Xn_t[eidx]))
        symbols = (zt @ chan.P.t()).argmax(dim=1)             # [M] hard message symbol
        Ps = chan.P[symbols]                                  # [M, d]
        cand_flat = cand.reshape(-1)
        zc_rich = _l2norm(enc_s(Xn_t[cand_flat])).reshape(M, C, -1)
        sp_pick = (Ps.unsqueeze(1) * zc_rich).sum(dim=-1).argmax(dim=1)
        speaker_correct = (sp_pick == 0)
        zc_bare = _l2norm(enc_l(X_t[cand_flat])).reshape(M, C, -1)
        li_pick = (Ps.unsqueeze(1) * zc_bare).sum(dim=-1).argmax(dim=1)
        listener_correct = (li_pick == 0)
    sc = speaker_correct.numpy().astype(bool)
    lc = listener_correct.numpy().astype(bool)
    syms = symbols.numpy()
    ent, n_sym = _symbol_entropy_bits(syms, K)
    return dict(speaker_correct=sc, listener_correct=lc, symbols=syms,
                grounding_acc=float(lc.mean()),
                speaker_fail_rate=float((~sc).mean()), listener_fail_rate=float((~lc).mean()),
                symbol_entropy_bits=ent, n_symbols_used=n_sym)


def run_arm(arm, cfg, X, Xn, adj, seed, n_nodes, eval_idx, cand_idx, out_dir):
    dg_diag = None
    if arm == DG_ARM:
        Xn_use, X_use, dg_diag = build_dg_features(X, Xn, cfg, seed)
        _log("  DG stage seed=%d decorr_gap(spk=%.3f lis=%.3f) sparse(spk=%.4f lis=%.4f) "
             "distinct(spk=%.3f lis=%.3f)" % (
                 seed, dg_diag["decorr_gap_speaker"], dg_diag["decorr_gap_listener"],
                 dg_diag["sparse_rate_speaker"], dg_diag["sparse_rate_listener"],
                 dg_diag["distinct_frac_speaker"], dg_diag["distinct_frac_listener"]))
    else:
        Xn_use, X_use = Xn, X
    enc_s, enc_l, chan = train_arm(arm, cfg, X_use, Xn_use, adj, seed, n_nodes, out_dir, tag=arm)
    ev = eval_masks(enc_s, enc_l, chan, Xn_use, X_use, eval_idx, cand_idx, cfg["K"])
    fm = failure_mask_corr(ev["speaker_correct"], ev["listener_correct"])
    return dict(
        arm=arm, seed=seed,
        failmask_corr=fm["failmask_corr"], failmask_degenerate=fm["failmask_degenerate"],
        grounding_acc=ev["grounding_acc"],
        speaker_fail_rate=ev["speaker_fail_rate"], listener_fail_rate=ev["listener_fail_rate"],
        symbol_entropy_bits=ev["symbol_entropy_bits"], n_symbols_used=ev["n_symbols_used"],
        n_eval=int(eval_idx.shape[0]), dg_diag=dg_diag,
        _mask_digest=hashlib.sha256(
            np.concatenate([ev["speaker_correct"], ev["listener_correct"]]).tobytes()).hexdigest(),
    )


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def _mean(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.size else float("nan")


def aggregate_and_verdict(per_seed_arm, cfg, subgraph_meta, run_mode):
    """per_seed_arm: list of dicts (one per (seed,arm)). Aggregate per arm across seeds -> verdict."""
    by_arm = {a: [r for r in per_seed_arm if r["arm"] == a] for a in ARM_NAMES}
    agg = {}
    for a in ARM_NAMES:
        rows = by_arm[a]
        agg[a] = dict(
            failmask_corr=_mean([r["failmask_corr"] for r in rows]),
            grounding_acc=_mean([r["grounding_acc"] for r in rows]),
            speaker_fail_rate=_mean([r["speaker_fail_rate"] for r in rows]),
            listener_fail_rate=_mean([r["listener_fail_rate"] for r in rows]),
            symbol_entropy_bits=_mean([r["symbol_entropy_bits"] for r in rows]),
            n_symbols_used=_mean([r["n_symbols_used"] for r in rows]),
            any_degenerate=any(r["failmask_degenerate"] for r in rows),
        )

    corr0 = agg[MIRROR_ARM]["failmask_corr"]
    corr_b1 = agg[B1_ARM]["failmask_corr"]
    corr_dg = agg[DG_ARM]["failmask_corr"]
    ground_dg = agg[DG_ARM]["grounding_acc"]
    improve = corr_b1 - corr_dg

    # anti-collapse gate (ALL arms)
    codes_ok = all((agg[a]["symbol_entropy_bits"] >= ENTROPY_FLOOR_BITS)
                   and (agg[a]["n_symbols_used"] >= MIN_SYMBOLS_USED) for a in ARM_NAMES)

    # DG-fires gate: every DG_XFIT seed's DG stage must be non-degenerate
    dg_rows = by_arm[DG_ARM]
    dg_all_ok, dg_reason_agg = True, []
    for r in dg_rows:
        if r.get("dg_diag") is None:
            dg_all_ok = False
            dg_reason_agg.append("seed%d:no_dg_diag" % r["seed"])
            continue
        ok, reasons = _dg_nondegenerate(r["dg_diag"], cfg)
        if not ok:
            dg_all_ok = False
            dg_reason_agg.append("seed%d:%s" % (r["seed"], ";".join(reasons)))

    # assert_discriminator_fires: B0 must show high corr + be in a measurable failure band
    b0_in_band = (FAILRATE_LO <= agg[MIRROR_ARM]["speaker_fail_rate"] <= FAILRATE_HI) and \
                 (FAILRATE_LO <= agg[MIRROR_ARM]["listener_fail_rate"] <= FAILRATE_HI) and \
                 (not agg[MIRROR_ARM]["any_degenerate"])
    screen_fires = (corr0 >= B0_FAILMASK_CORR_MIN) and b0_in_band

    hard_pass = (corr_dg <= DG_FAILMASK_CORR_HP) and (ground_dg >= GROUNDING_FLOOR) and \
                (improve >= DG_IMPROVE_MARGIN)

    if not codes_ok:
        verdict = "CODE_COLLAPSE_VOID"
    elif not dg_all_ok:
        verdict = "DG_CODE_DEGENERATE_VOID"
    elif not screen_fires:
        verdict = "SATURATION_VACUOUS_SCREEN_DID_NOT_FIRE"
    elif ground_dg < GROUNDING_DESTROYED:
        verdict = "HARD_FAIL_DG_DESTROYS_GROUNDING"          # case (b)
    elif hard_pass:
        verdict = "HARD_PASS"
    elif (corr_dg >= DG_FAILMASK_CORR_HF_A) and (ground_dg >= GROUNDING_FLOOR):
        verdict = "HARD_FAIL_REPRESENTATION_INSUFFICIENT_REDIRECT_EXOGENOUS"   # case (a)
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | mode=%s | B0_mirror corr=%.3f (fires=%s spk_fail=%.3f lis_fail=%.3f) | "
        "B1_crossfit corr=%.3f ground=%.3f | DG_XFIT corr=%.3f ground=%.3f | improve(B1-DG)=%.3f | "
        "dg_fires=%s | codes_ok=%s ent(B0/B1/DG)=[%.2f,%.2f,%.2f] | subgraph n=%d E=%d" % (
            verdict, run_mode, corr0, screen_fires,
            agg[MIRROR_ARM]["speaker_fail_rate"], agg[MIRROR_ARM]["listener_fail_rate"],
            corr_b1, agg[B1_ARM]["grounding_acc"], corr_dg, ground_dg, improve,
            dg_all_ok, codes_ok,
            agg[MIRROR_ARM]["symbol_entropy_bits"], agg[B1_ARM]["symbol_entropy_bits"],
            agg[DG_ARM]["symbol_entropy_bits"],
            subgraph_meta.get("n_nodes", -1), subgraph_meta.get("n_edges", -1)))

    gates = dict(
        b0_failmask_corr=corr0, b1_failmask_corr=corr_b1, dg_failmask_corr=corr_dg,
        dg_grounding=ground_dg, dg_improvement_over_b1=improve,
        screen_fires=screen_fires, b0_in_band=b0_in_band, codes_ok=codes_ok,
        dg_fires=dg_all_ok, dg_degenerate_reasons=dg_reason_agg,
        hard_pass=hard_pass, per_arm=agg,
        bands=dict(B0_FAILMASK_CORR_MIN=B0_FAILMASK_CORR_MIN, DG_FAILMASK_CORR_HP=DG_FAILMASK_CORR_HP,
                   DG_IMPROVE_MARGIN=DG_IMPROVE_MARGIN, GROUNDING_FLOOR=GROUNDING_FLOOR,
                   DG_FAILMASK_CORR_HF_A=DG_FAILMASK_CORR_HF_A, GROUNDING_DESTROYED=GROUNDING_DESTROYED,
                   ENTROPY_FLOOR_BITS=ENTROPY_FLOOR_BITS, DG_DECORR_MIN_GAP=DG_DECORR_MIN_GAP),
    )
    return verdict, verdict_msg, gates, agg


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs)
# ---------------------------------------------------------------------------
def discriminator_selftest():
    """(1) failure_mask_corr is telemetry-sensitive (planted correlated -> high; independent -> ~0; a
    shared vs independent perturbation MOVES it; tied vs separated toy encoder reproduces high vs low corr).
    (2) DGProjection decorrelates: code_cos < input_cos on a toy batch (the DG-fires primitive works)."""
    rng = np.random.default_rng(0)
    n = 500
    base = rng.random(n) < 0.6
    a_corr = base.copy(); b_corr = base.copy()
    a_corr[rng.random(n) < 0.05] ^= True
    b_corr[rng.random(n) < 0.05] ^= True
    c_high = failure_mask_corr(a_corr, b_corr)["failmask_corr"]
    a_ind = rng.random(n) < 0.4
    b_ind = rng.random(n) < 0.4
    c_low = failure_mask_corr(a_ind, b_ind)["failmask_corr"]

    d_feat, d_code, K, M, ND = 128, 24, 6, 200, 5
    Wshared = rng.standard_normal((d_feat, d_code)).astype(np.float32)
    Wsep = rng.standard_normal((d_feat, d_code)).astype(np.float32)
    P = rng.standard_normal((K, d_code)).astype(np.float32)
    feats = rng.standard_normal((M + M * ND, d_feat)).astype(np.float32)

    def _l2(z):
        return z / (np.linalg.norm(z, axis=-1, keepdims=True) + 1e-8)

    def decode(Wenc, Wlist):
        tgt_feat = feats[:M]
        zt = _l2(tgt_feat @ Wenc)
        sym = (zt @ P.T).argmax(1)
        Ps = P[sym]
        cand = np.zeros((M, 1 + ND), dtype=np.int64)
        cand[:, 0] = np.arange(M)
        for i in range(M):
            cand[i, 1:] = rng.integers(0, M, size=ND)
        s_correct = np.zeros(M, dtype=bool)
        l_correct = np.zeros(M, dtype=bool)
        for i in range(M):
            cfeat = feats[cand[i]]
            zs = _l2(cfeat @ Wenc)
            zl = _l2(cfeat @ Wlist)
            s_correct[i] = int((Ps[i] * zs).sum(1).argmax()) == 0
            l_correct[i] = int((Ps[i] * zl).sum(1).argmax()) == 0
        return failure_mask_corr(s_correct, l_correct)["failmask_corr"]

    tied_corr = decode(Wshared, Wshared)
    sep_corr = decode(Wshared, Wsep)

    # DG decorrelation primitive check: on GENUINELY-CORRELATED inputs (shared base component), the DG
    # random-expansion + top-k must REDUCE mean pairwise cosine (pattern separation). Directional check.
    dg_in = 256
    shared_base = rng.standard_normal((dg_in,)).astype(np.float32)
    indep = rng.standard_normal((200, dg_in)).astype(np.float32)
    Xtoy = (0.7 * shared_base[None, :] + 0.7 * indep).astype(np.float32)  # pairwise cos ~0.5
    dg = DGProjection(input_dim=dg_in, dg_dim=1024, sparsity=0.04, seed=29)
    codes = dg.encode_batch(Xtoy)
    dg_rng = np.random.default_rng(1)
    in_cos = _mean_pairwise_cos(Xtoy, dg_rng)
    code_cos = _mean_pairwise_cos(codes, dg_rng)
    dg_decorr = in_cos - code_cos

    ok = (c_high >= 0.5) and (abs(c_low) < 0.2) and (tied_corr > sep_corr + 0.1) and (dg_decorr > 0.05)
    return bool(ok), dict(corr_planted_high=float(c_high), corr_planted_indep=float(c_low),
                          e2e_tied_corr=float(tied_corr), e2e_separated_corr=float(sep_corr),
                          dg_input_cos=float(in_cos), dg_code_cos=float(code_cos),
                          dg_decorr_gap=float(dg_decorr))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    global RUN_MODE_GLOBAL
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode
    if "_smoke" in os.environ.get("HDLAB_EXP_NAME", "").lower():
        run_mode = "smoke"
    RUN_MODE_GLOBAL = run_mode

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"]) * len(ARM_NAMES)
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (not telemetry-sensitive OR DG no-decorr): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res))
        raise SystemExit(1)

    _log("loading ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, meta = load_cn_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    n_nodes = len(node_ids)
    _log("subgraph: %s" % meta)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, n_nodes)
    Xn = neighborhood_augment(X, adj, cfg["neighbor_weight"])

    eval_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 999)
    has_nb = np.nonzero(np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool))[0]
    n_eval = int(min(cfg["n_eval"], has_nb.shape[0]))
    eval_idx = np.sort(eval_rng.choice(has_nb, size=n_eval, replace=False))
    cand_idx = build_candidate_sets(eval_idx, n_nodes, cfg["n_dist"], eval_rng)
    _log("eval referents=%d candidate_set_size=%d" % (n_eval, 1 + cfg["n_dist"]))

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator telemetry-sensitive + DG decorrelates + pipeline exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, subgraph_meta=meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed_arm = []
    unit_failures = []
    total_units = len(cfg["seeds"]) * len(ARM_NAMES)
    u = 0
    for seed in cfg["seeds"]:
        for arm in ARM_NAMES:
            u += 1
            try:
                r = run_arm(arm, cfg, X, Xn, adj, seed, n_nodes, eval_idx, cand_idx, out_dir_path)
                per_seed_arm.append(r)
                write_partial(out_dir_path, "%s_seed%d" % (arm, seed),
                              dict(seed=seed, arm=arm, metrics={k: v for k, v in r.items()
                                                                if not k.startswith("_")}))
                _log("[%d/%d] seed=%d %s failmask_corr=%.3f ground=%.3f spk_fail=%.3f lis_fail=%.3f "
                     "ent=%.2f nsym=%d" % (u, total_units, seed, arm, r["failmask_corr"],
                                           r["grounding_acc"], r["speaker_fail_rate"],
                                           r["listener_fail_rate"], r["symbol_entropy_bits"],
                                           r["n_symbols_used"]))
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J)
                fc = type(e).__name__
                unit_failures.append(dict(seed=seed, arm=arm, failure_class=fc, msg=str(e)[:300]))
                _log("UNIT_FAILED seed=%d arm=%s class=%s: %s" % (seed, arm, fc, str(e)[:200]))

    if len(per_seed_arm) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d units, got %d (failures=%s)" % (
                expected_n_units, len(per_seed_arm), unit_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            unit_failures=unit_failures, subgraph_meta=meta))
        raise SystemExit(1)

    # ARMS-MUST-DIFFER (META_RULE_AF): all 3 arms' mask-pairs must differ per seed
    for seed in cfg["seeds"]:
        digs = {r["arm"]: r["_mask_digest"] for r in per_seed_arm if r["seed"] == seed}
        arms_present = [a for a in ARM_NAMES if a in digs]
        for i in range(len(arms_present)):
            for j in range(i + 1, len(arms_present)):
                a, b = arms_present[i], arms_present[j]
                assert digs[a] != digs[b], (
                    "META_RULE_AF VIOLATION: arms %s and %s bit-identical at seed %d" % (a, b, seed))

    subgraph_meta = dict(n_nodes=meta.get("n_nodes", n_nodes), n_edges=meta.get("n_edges", len(edges)),
                         median_degree=meta.get("median_degree", -1))
    verdict, verdict_msg, gates, agg = aggregate_and_verdict(per_seed_arm, cfg, subgraph_meta, run_mode)

    per_persist = [{k: v for k, v in r.items() if not k.startswith("_")} for r in per_seed_arm]
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(cfg["seeds"]), seeds=cfg["seeds"], config=cfg, config_version=CONFIG_VERSION,
        subgraph_meta=subgraph_meta, gates=gates, per_arm_agg=agg,
        discriminator_selftest=st_res, unit_failures=unit_failures, per_unit=per_persist,
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
