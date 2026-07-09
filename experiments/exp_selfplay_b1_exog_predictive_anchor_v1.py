"""selfplay_b1_exog_predictive_anchor_v1 -- the EXOGENOUS-referent grounding cell (B1+EXOG).

Does adding an EXOGENOUS predictive anchor -- where BOTH self-play halves must independently PREDICT the
REAL ingest data (reconstruct the referent's real char-trigram content through the code bottleneck) --
break the shared-upstream self-grounding blind spot that internal decorrelation (B1 cross-fit, DG pattern
separation) could NOT? The 5x negative drill confirmed all internal revival angles are dead: internal
methods decorrelate NOISE not the shared BIAS (residual corr(failmask)=0.377 is bias, MEASURED@
data/exp_selfplay_dg_pattern_separation_xfit_v1/metrics.json:gates.dg_failmask_corr). Exogenous ground
truth is the only remaining known lever.

WHY (Director steer 2026-07-09; drills notes/research_exogenous_referent_grounding_predictive_coding_
2026-07-09.md [B1+EXOG design] + notes/research_dg_selfgrounding_5x_remaining_internal_angles_2026-07-09.md
[bias-confirmed -> exogenous-required]):
  B1 (disjoint-data cross-fit) splits WHICH data each branch sees; it decorrelated the naive-mirror blind
  spot 0.788 -> 0.393 but stalled ~2x above the independence bar (0.20). DG pattern separation (a
  representation-level fix) added +0.015 (0.393 -> 0.377): representation-level decorrelation is INSUFFICIENT
  because the blind spot lives in the shared training signal/distribution both branches ultimately chase
  (both fit against the same self-generated notion of "correct" -> folie a deux). The exogenous anchor
  constrains WHAT BOTH branches are checked against: a shared, REAL, outside-the-loop reconstruction target
  that neither branch's game objective directly optimizes. Because the target is caused by a process outside
  the self-play loop (the real ConceptNet words' real char-trigram signatures), it can inject genuine
  external mutual information a closed loop cannot manufacture (Pezzulo/Parr/Cisek/Clark/Friston 2023;
  Pu et al. 2026 exogenous-vs-endogenous). REUSES hdlab/predictive_coding.py precision-weighting
  (residual_magnitude/proportional_gate) as the Rao-Ballard write-strength gate concentrating anchor
  learning on surprising (poorly-reconstructed) real referents.

HONEST FRAMING (mandatory, NOT "grounding solved"): this tests the PARTIAL exogenous anchor -- PASSIVE
  prediction of real data. Full referential grounding is NOT expected (lit P~0.12: Pezzulo 2023 argues
  passive prediction is insufficient for genuine understanding; active embodied intervention is the missing
  ingredient; Coelho Mollo & Milliere 2023 teleosemantic condition unmet). The realistic win is "the
  exogenous anchor materially decorrelates the failure masks where internal decorrelation could not, AND
  shows causal grounding (the representation causally tracks the real referent)." A HARD_FAIL here is the
  honest bound: passive prediction alone may be insufficient -> redirect to ACTIVE-INTERVENTION (the
  causal-representation-learning intervention axis, NOT more passive machinery).

THREE ARMS:
  B0_mirror (MUST-FAIL control): tied encoder, differ only by info-access asymmetry (speaker: neighborhood-
     augmented Xn; listener: bare X). Predicted HIGH failmask corr (~0.77, the shared-blind-spot signature).
     assert_discriminator_fires: if B0 corr < 0.40 at smoke the screen is saturation-vacuous -> re-spec.
  B1_crossfit (CONTRAST FLOOR, MUST reproduce ~0.39): separate enc_s/enc_l, cross-fit on disjoint folds,
     shared channel P. No anchor. This is the axis B1+EXOG must beat; it MUST reproduce ~0.39 (band
     [0.30,0.50]) or the whole contrast is void.
  B1_EXOG (TREATMENT): B1 cross-fit + a shared EXOGENOUS predictive anchor. Each branch gets its OWN
     W_pred decoder (Linear code_dim->feat_dim) trained (precision-weighted) to reconstruct the referent's
     REAL content X[r] from that branch's code -- SAME real target, both must independently hit it. The
     speaker must recover pure content from relation-augmented input Xn; the listener from bare X. The
     shared real target pins both branches to the outside world rather than to each other.

DISCRIMINATORS (all reused verbatim where possible):
  failure_mask_corr (from exp_pfc_gate_waypoint_rescue via the DG cell): corr(1-speaker_correct,
     1-listener_correct) over referents. grounding_acc = mean(listener_correct) = joint game success.
  CAUSAL-PERTURBATION SCREEN (Prediction C, normalized directional-sensitivity ratio): on the trained
     speaker encoder, per referent, SWAP the real content x for another node's real content (grounded
     perturbation) vs SWAP the neighbor-aggregate g for another node's (relation-only perturbation), each
     normalized by its input-space delta -> sensitivity_content / sensitivity_relation. A representation
     that CAUSALLY tracks the real referent moves >= 2x more per unit real-content change than per unit
     relation change. B1 (game-only, no anchor) is the non-grounded contrast (~1).
  TRANSITIVE-SPREAD COMPANION (reuses snowball label_propagation, DIAGNOSTIC not a gate): propagate the
     validated graph-smooth attribute over the frozen codes; reports whether the EXOG anchor RETAINS B1's
     relational transitive-spread (near-decay) capability -- a regression check, not a HARD_PASS gate.

PRE-REGISTERED BANDS (BOTH; LOCKED PROSPECTIVE):
  HARD_PASS (exogenous anchor breaks the shared-bias blind spot):
     B1_EXOG failmask_corr <= 0.20 AND grounding_acc >= 0.50 AND (B1 corr - EXOG corr) >= 0.10 (material
     improvement over cross-fit, not seed noise) AND perturb_ratio >= 2.0 (causal grounding) AND B0 fires
     (corr >= 0.40, in failure band) AND B1 reproduces (corr in [0.30,0.50]) AND all arms' codes
     non-degenerate (entropy >= 1.0 bit, >=2 symbols) AND the anchor fired (recon better than untrained).
  HARD_FAIL (a) -- PASSIVE exogenous anchor INSUFFICIENT (redirect to ACTIVE-INTERVENTION):
     B1_EXOG failmask_corr >= 0.35 (no material improvement over DG's 0.377) WHILE grounding retained
     (>=0.50) OR perturb_ratio < 1.3 (no causal grounding: the anchor is a hollow correlate / added noise
     that did not causally ground the representation). The honest bound: passive prediction alone may be
     insufficient; active inference is the missing ingredient.
  HARD_FAIL (b) -- anchor DESTROYS grounding: B1_EXOG grounding_acc < 0.40 (even if corr improves) =>
     the anchor over-constrained the code and stripped referential/game content. Fix = lower lambda_exog.
  MIDDLE_BAND: EXOG corr in (0.20,0.35] with grounding >= 0.50, OR perturb_ratio in [1.3,2.0) -> sweep
     lambda_exog before concluding.
  SATURATION_VACUOUS: B0 corr < 0.40 at smoke OR B0 failure-rate degenerate => discriminator not firing.
  CODE_COLLAPSE_VOID: any arm's message code collapsed (entropy < 1.0 bit) => degenerate-code artifact.
  ANCHOR_INERT_VOID: the EXOG anchor did not reduce reconstruction error vs untrained (mechanism did not
     fire) => re-spec lambda_exog / anchor wiring.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): the 3 arms' (speaker,listener) mask-pairs hashed; all differ.
# - final_metrics_atomicity: tmp_replace (write_metrics -> os.replace; crash-diag atomic).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the discriminator is a failure-mask CORRELATION vs a within-cell MUST-FAIL control (B0) +
#   a normalized directional-sensitivity RATIO, not a closed-form noise floor; reachability by construction
#   (B0 fires high corr; treatment sits in [0, corr(B0)]; HP bar corr<=0.20 with margin>=0.10 vs B1 inside;
#   perturb ratio in [0, inf), gate 2.0 with a planted-encoder self-test proving the screen is sensitive).
# - baseline_in_band (AG): B0 failure rates 0.05..0.95 both halves at smoke (else corr degenerate).
# - discriminator survives scale: smoke = FULL branches at smaller n_nodes/epochs/K, SAME anchor ratio
#   (lambda_exog fixed). SMOKE MUST show B0 corr >= 0.40 (assert_discriminator_fires), B1 corr in
#   [0.30,0.50] (contrast reproduces), arms differ, anchor fires (recon > untrained), perturb-screen
#   telemetry-sensitive (self-test planted encoders). The corr<=0.20 HP decision is for FULL.
# - multi-seed smoke (3 seeds) for the correlation-discriminator per META_RULE_smoke_single_seed_inflates_AUC.
# - HARD_PASS strictly above floor: corr(EXOG)<=0.20 AND improve>=0.10 AND grounding>=0.50 AND ratio>=2.0.
# - HP_SCOPE: decorrelation gates -> {B1_EXOG}; screen-fires -> {B0}; contrast-reproduce -> {B1_crossfit};
#   anti-collapse -> ALL arms; anchor-fires + perturb-ratio -> {B1_EXOG} (B1 ratio reported as contrast).
# - cardinality_ok: EXPECTED_N_UNITS = n_arms(3) * n_seeds (no sweep axis).
# - per-unit failure-class instrumentation (no bare except; per-(seed,arm) failure_class).
# - calibration_check: adaptive_with_discriminator_gate (lambda_exog/K/tau fixed per profile; anti-collapse
#   entropy floor + B0-fires + baseline-in-band + anchor-fires + perturb-sensitivity self-test per run).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.

Compute architecture: (c) mixed sequential-CPU with justification. Encoders shallow linear ProjHeads +
per-branch W_pred decoders; per-step ops are batched matmuls / gumbel-softmax / candidate scoring / anchor
MSE. Cost is the self-play training loop (sequential over epochs, genuine dependency); 3 arms x 3-5 seeds is
minutes-to-tens-of-minutes on CPU. Storage strategy: no_storage (codes are transient encoder outputs; no
PartitionedStore writes). progress_logging: print_flush_true (line-buffered stdout + flush=True + per
(seed,arm) heartbeat; FULL timeout_s >= 1800).

Reuses VERBATIM from experiments/exp_selfplay_dg_pattern_separation_xfit_v1.py: failure_mask_corr,
neighborhood_augment, build_candidate_sets, MessageChannel, _make_encoder, _symbol_entropy_bits,
_forward_game, _ent_reg, eval_masks, _relational_positive_batch. From
experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py: load_cn_subgraph, char_trigram_features,
build_adjlist, ProjHead, info_nce, vicreg_repulsion, _l2norm. From
experiments/exp_grounding_snowball_transitive_inheritance_v1.py: make_smooth_attribute,
attribute_assortativity, label_propagation, ordering_accuracy, multi_source_bfs, distance_bins. From
hdlab/predictive_coding.py: residual_magnitude, proportional_gate (precision-weighting gate). NEW (additive):
the W_pred predictive anchor (per-branch reconstruction of real content, precision-weighted), the causal-
perturbation directional-sensitivity screen, the B1_EXOG arm + verdict.
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
from experiments.exp_selfplay_dg_pattern_separation_xfit_v1 import (  # noqa: E402
    failure_mask_corr,
    neighborhood_augment,
    build_candidate_sets,
    MessageChannel,
    _make_encoder,
    _symbol_entropy_bits,
    _forward_game,
    _ent_reg,
    eval_masks,
    _relational_positive_batch,
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
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    make_smooth_attribute,
    attribute_assortativity,
    label_propagation,
    ordering_accuracy,
    multi_source_bfs,
    distance_bins,
)
from hdlab.predictive_coding import residual_magnitude, proportional_gate  # noqa: E402

ANCHOR_NAME = "selfplay_b1_exog_predictive_anchor_v1"
SUBGRAPH_BASE_SEED = 1234

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; scale + mechanism parity)
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    n_nodes=300, seeds=[7], epochs=12, batch=128,
    code_dim=32, feat_dim=512,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05, lambda_ent=0.1,
    lambda_exog=0.5, exog_batch=128,
    K=8, n_dist=5, gumbel_tau=2.0, gumbel_tau_end=0.5, neighbor_weight=0.5, n_eval=150,
    n_perturb_eval=100, n_ground_seeds=15, diffuse_steps=8, n_sources=6,
    ridge_lambda=1.0, k_labelprop=7, n_pairs_per_bin=1500,
)
SMOKE_CFG = dict(
    n_nodes=1500, seeds=[7, 13, 17], epochs=80, batch=256,
    code_dim=96, feat_dim=4096,
    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05, lambda_ent=0.1,
    lambda_exog=0.5, exog_batch=256,
    K=12, n_dist=7, gumbel_tau=2.0, gumbel_tau_end=0.5, neighbor_weight=0.5, n_eval=700,
    n_perturb_eval=400, n_ground_seeds=30, diffuse_steps=10, n_sources=25,
    ridge_lambda=1.0, k_labelprop=7, n_pairs_per_bin=4000,
)
FULL_CFG = dict(
    n_nodes=8000, seeds=[7, 13, 17, 23, 29], epochs=220, batch=512,
    code_dim=192, feat_dim=8192,
    temp=0.12, lr=0.008, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05, lambda_ent=0.1,
    lambda_exog=0.5, exog_batch=512,
    K=24, n_dist=9, gumbel_tau=2.0, gumbel_tau_end=0.4, neighbor_weight=0.5, n_eval=3000,
    n_perturb_eval=1500, n_ground_seeds=120, diffuse_steps=12, n_sources=80,
    ridge_lambda=1.0, k_labelprop=7, n_pairs_per_bin=6000,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (LOCKED; PROSPECTIVE)
# ---------------------------------------------------------------------------
B0_FAILMASK_CORR_MIN = 0.40    # assert_discriminator_fires: mirror shows shared-blind-spot
EXOG_FAILMASK_CORR_HP = 0.20   # HARD_PASS: EXOG decorrelates at/below the independence bar
EXOG_IMPROVE_MARGIN = 0.10     # HARD_PASS: (B1 corr - EXOG corr) >= this (material vs cross-fit)
GROUNDING_FLOOR = 0.50         # HARD_PASS: EXOG still communicates (>> chance 1/(1+n_dist))
PERTURB_RATIO_HP = 2.0         # HARD_PASS: causal grounding (real-content sensitivity >= 2x relation)
EXOG_FAILMASK_CORR_HF_A = 0.35 # HARD_FAIL(a): EXOG corr >= this while grounding retained -> active-interv
PERTURB_RATIO_HF = 1.3         # HARD_FAIL(a): perturb ratio < this -> no causal grounding (hollow anchor)
GROUNDING_DESTROYED = 0.40     # HARD_FAIL(b): EXOG grounding < this -> anchor over-constrained
B1_CONTRAST_LO = 0.30          # B1 must reproduce the ~0.39 cross-fit contrast floor
B1_CONTRAST_HI = 0.50
ENTROPY_FLOOR_BITS = 1.0       # anti-collapse: message code entropy floor
MIN_SYMBOLS_USED = 2
FAILRATE_LO = 0.05             # B0 baseline_in_band edges
FAILRATE_HI = 0.95
ANCHOR_FIRE_MIN_GAIN = 0.03    # anchor-fires: recon_cos(EXOG) - recon_cos(untrained) >= this

ARM_NAMES = ["B0_mirror", "B1_crossfit", "B1_EXOG"]
CROSSFIT_ARMS = ["B1_crossfit", "B1_EXOG"]
EXOG_ARM = "B1_EXOG"
B1_ARM = "B1_crossfit"
MIRROR_ARM = "B0_mirror"

CONFIG_VERSION = (
    "ANCHOR=%s,arms=%s,B0corr>=%.2f,EXOGcorr<=%.2f,margin>=%.2f,ground>=%.2f,ratio>=%.2f,HFa>=%.2f,"
    "HFratio<%.2f,HFb_ground<%.2f,B1contrast=[%.2f,%.2f],ent>=%.2f,failband=[%.2f,%.2f]"
) % (ANCHOR_NAME, ARM_NAMES, B0_FAILMASK_CORR_MIN, EXOG_FAILMASK_CORR_HP, EXOG_IMPROVE_MARGIN,
     GROUNDING_FLOOR, PERTURB_RATIO_HP, EXOG_FAILMASK_CORR_HF_A, PERTURB_RATIO_HF, GROUNDING_DESTROYED,
     B1_CONTRAST_LO, B1_CONTRAST_HI, ENTROPY_FLOOR_BITS, FAILRATE_LO, FAILRATE_HI)

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
# EXOGENOUS predictive anchor: precision-weighted reconstruction of REAL content.
# ---------------------------------------------------------------------------
def _bipolar_sign(v):
    """Bipolar {-1,+1} sign of a centered vector (0 -> +1)."""
    s = np.sign(v)
    s[s == 0] = 1.0
    return s


def precision_gate_weights(pred_np, target_np):
    """Rao-Ballard precision weight per sample = proportional_gate(residual_magnitude) on the SIGN pattern
    of (centered) prediction vs (centered) real target. Vectorized; verified equivalent to the library
    residual_magnitude / proportional_gate in discriminator_selftest (faithful reuse of hdlab.predictive_
    coding precision-weighting). Returns (weights[B] in [0,1], mean_residual_mag)."""
    pc = pred_np - pred_np.mean(axis=1, keepdims=True)
    tc = target_np - target_np.mean(axis=1, keepdims=True)
    ps = _bipolar_sign(pc)
    ts = _bipolar_sign(tc)
    # residual_magnitude for bipolar = 0.5*(1 - cos); cos = mean(ps*ts) since |ps|=|ts|=1
    cos = (ps * ts).mean(axis=1)
    cos = np.clip(cos, -1.0, 1.0)
    mag = 0.5 * (1.0 - cos)                      # matches residual_magnitude(observed, predicted)
    strength = np.clip(mag, 0.0, 1.0)            # proportional_gate(min=0,max=1) -> strength == mag
    return strength.astype(np.float32), float(mag.mean())


class ExogAnchor(torch.nn.Module):
    """W_pred decoder: code -> predicted real content (feat_dim). One per branch."""

    def __init__(self, code_dim, feat_dim):
        super().__init__()
        self.dec = torch.nn.Linear(code_dim, feat_dim, bias=False)

    def forward(self, z):
        return self.dec(z)


def _anchor_loss(anchor, enc, X_t, idx_np, target_t):
    """Precision-weighted MSE reconstructing REAL content target_t[idx] from enc(X_t[idx]) code.
    Precision weights come from residual_magnitude (detached; a modulation, not differentiated)."""
    idx_t = torch.from_numpy(idx_np.astype(np.int64))
    z = _l2norm(enc(X_t[idx_t]))
    pred = anchor(z)                              # [B, feat_dim]
    tgt = target_t[idx_t]
    with torch.no_grad():
        w_np, mean_mag = precision_gate_weights(pred.detach().numpy(), tgt.detach().numpy())
        w_t = torch.from_numpy(w_np)              # [B]
    se = ((pred - tgt) ** 2).mean(dim=1)          # [B] per-sample MSE
    loss = (w_t * se).sum() / (w_t.sum() + 1e-8)  # precision-weighted mean
    return loss, mean_mag


def _recon_cos(anchor, enc, X_t, idx_np, target_np):
    """Mean cosine between reconstructed and real content over idx (anchor-fires diagnostic)."""
    idx_t = torch.from_numpy(idx_np.astype(np.int64))
    with torch.no_grad():
        z = _l2norm(enc(X_t[idx_t]))
        pred = anchor(z).numpy()
    tgt = target_np[idx_np]
    pn = np.linalg.norm(pred, axis=1) + 1e-12
    tn = np.linalg.norm(tgt, axis=1) + 1e-12
    return float(((pred * tgt).sum(axis=1) / (pn * tn)).mean())


# ---------------------------------------------------------------------------
# CAUSAL-PERTURBATION SCREEN (Prediction C): normalized directional-sensitivity ratio.
# ---------------------------------------------------------------------------
def neighbor_aggregate(X, adj):
    """g[i] = mean of neighbor features (zeros if no neighbors). Shape [n, feat_dim] float32."""
    n, d = X.shape
    g = np.zeros((n, d), dtype=np.float32)
    for i in range(n):
        nb = adj[i]
        if len(nb):
            g[i] = X[np.asarray(nb, dtype=np.int64)].mean(axis=0)
    return g


def _l2n_np(v):
    nv = np.linalg.norm(v, axis=-1, keepdims=True)
    nv[nv == 0.0] = 1.0
    return v / nv


def causal_perturbation_ratio(enc_s, X, g, nbr_weight, eval_idx, has_nb_idx, rng, n_perturb):
    """Per referent (speaker encoder, input Xn = normalize(x + w*g)): SWAP real content x for another
    node's x (grounded perturbation) vs SWAP neighbor-aggregate g for another node's g (relation-only
    perturbation). Each code-shift is normalized by its INPUT-space delta -> a matched directional
    sensitivity. ratio = mean(sens_content) / mean(sens_relation). Causal grounding => >= 2 (the code
    moves more per unit real-content change than per unit relation change)."""
    idx = eval_idx if eval_idx.shape[0] <= n_perturb else \
        np.sort(rng.choice(eval_idx, size=n_perturb, replace=False))
    x = X[idx].astype(np.float32)                                  # [M, d]
    gi = g[idx].astype(np.float32)
    w = float(nbr_weight)
    Xn = _l2n_np(x + w * gi)

    # donors for content swap (any node) and relation swap (nodes WITH neighbors)
    o_c = rng.integers(0, X.shape[0], size=idx.shape[0])
    o_r = has_nb_idx[rng.integers(0, has_nb_idx.shape[0], size=idx.shape[0])]
    x_o = X[o_c].astype(np.float32)
    g_o = g[o_r].astype(np.float32)

    Xn_c = _l2n_np(x_o + w * gi)                                   # content swapped, relation kept
    Xn_r = _l2n_np(x + w * g_o)                                    # content kept, relation swapped
    din_c = np.linalg.norm(Xn_c - Xn, axis=1)                      # input-space delta
    din_r = np.linalg.norm(Xn_r - Xn, axis=1)

    with torch.no_grad():
        z = _l2norm(enc_s(torch.from_numpy(Xn))).numpy()
        z_c = _l2norm(enc_s(torch.from_numpy(Xn_c))).numpy()
        z_r = _l2norm(enc_s(torch.from_numpy(Xn_r))).numpy()
    shift_c = 1.0 - (z * z_c).sum(axis=1)                          # 1 - cos (codes are unit)
    shift_r = 1.0 - (z * z_r).sum(axis=1)

    keep = (din_c > 1e-6) & (din_r > 1e-6)
    sens_c = shift_c[keep] / din_c[keep]
    sens_r = shift_r[keep] / din_r[keep]
    mean_c = float(sens_c.mean()) if sens_c.size else float("nan")
    mean_r = float(sens_r.mean()) if sens_r.size else float("nan")
    ratio = float(mean_c / mean_r) if (mean_r == mean_r and mean_r > 1e-9) else float("nan")
    return dict(perturb_ratio=ratio, sens_content=mean_c, sens_relation=mean_r,
                n_perturb=int(keep.sum()))


# ---------------------------------------------------------------------------
# Per-arm self-play training (adds the EXOG anchor to the cross-fit path for B1_EXOG)
# ---------------------------------------------------------------------------
def _make_channel(K, code_dim):
    return MessageChannel(K, code_dim)


def train_arm(arm, cfg, X, Xn, adj, target_t, seed, n_nodes, out_dir, tag):
    """Train one arm. B0_mirror: tied encoder joint step. B1_crossfit: disjoint-fold cross-fit.
    B1_EXOG: cross-fit + per-branch EXOG anchor (precision-weighted real-content reconstruction).
    Returns (enc_s, enc_l, chan, anchors, anchor_diag)."""
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

    chan = _make_channel(cfg["K"], code_dim)
    is_crossfit = arm in CROSSFIT_ARMS
    use_exog = arm == EXOG_ARM
    if arm == MIRROR_ARM:
        enc_s = _make_encoder(feat_dim, code_dim, seed)
        enc_l = enc_s
    else:
        enc_s = _make_encoder(feat_dim, code_dim, seed)
        enc_l = _make_encoder(feat_dim, code_dim, seed + 333)

    anchors = None
    recon_untrained = None
    if use_exog:
        torch.manual_seed(seed + 909)
        anchor_s = ExogAnchor(code_dim, feat_dim)
        anchor_l = ExogAnchor(code_dim, feat_dim)
        anchors = dict(speaker=anchor_s, listener=anchor_l)
        # untrained recon baseline (anchor-fires denominator), measured on a fixed probe set
        probe = np.sort(rng.choice(n_nodes, size=min(400, n_nodes), replace=False))
        recon_untrained = 0.5 * (_recon_cos(anchor_s, enc_s, Xn_t, probe, target_np=X)
                                 + _recon_cos(anchor_l, enc_l, X_t, probe, target_np=X))

    s_params = list(enc_s.parameters()) + list(chan.parameters())
    if use_exog:
        s_params = s_params + list(anchors["speaker"].parameters())
    opt_s = torch.optim.Adam(s_params, lr=cfg["lr"])
    if is_crossfit:
        l_params = list(enc_l.parameters())
        if use_exog:
            l_params = l_params + list(anchors["listener"].parameters())
        opt_l = torch.optim.Adam(l_params, lr=cfg["lr"])
    else:
        opt_l = None

    log_every = max(1, cfg["epochs"] // 5)
    tau0 = cfg["gumbel_tau"]
    tau1 = cfg.get("gumbel_tau_end", cfg["gumbel_tau"])
    lam_exog = cfg["lambda_exog"]
    exog_bs = cfg["exog_batch"]
    last_recon_mag = float("nan")
    t_ep = time.perf_counter()
    for ep in range(cfg["epochs"]):
        tau_ep = tau0 + (tau1 - tau0) * (ep / max(1, cfg["epochs"] - 1))
        if is_crossfit:
            for (pool, opt, sg, lg, side_enc, side_inp) in (
                    (fold_a, opt_s, True, False, enc_s, Xn_t),
                    (fold_b, opt_l, False, True, enc_l, X_t)):
                if opt is None:
                    continue
                tgt = torch.from_numpy(rng.choice(pool, size=min(cfg["batch"], pool.shape[0]),
                                                   replace=False).astype(np.int64))
                cand = torch.from_numpy(build_candidate_sets(tgt.numpy(), n_nodes, cfg["n_dist"], rng))
                ref_loss, msg = _forward_game(enc_s, enc_l, chan, Xn_t, X_t, tgt, cand,
                                              tau_ep, s_grad=sg, l_grad=lg)
                loss = ref_loss + cfg["lambda_ent"] * _ent_reg(msg)
                if use_exog:
                    # each side's OWN anchor reconstructs the SAME real content target from disjoint fold
                    a_idx = rng.choice(pool, size=min(exog_bs, pool.shape[0]), replace=False)
                    which = "speaker" if sg else "listener"
                    a_loss, last_recon_mag = _anchor_loss(anchors[which], side_enc, side_inp,
                                                          a_idx, target_t)
                    loss = loss + lam_exog * a_loss
                opt.zero_grad()
                loss.backward()
                opt.step()
            loss_val = float(ref_loss.detach())
        else:  # B0_mirror
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
            _log("  train seed=%d %s ep=%d/%d ref_loss=%.4f recon_mag=%.3f (%.1fs)" % (
                seed, tag, ep, cfg["epochs"], loss_val, last_recon_mag, time.perf_counter() - t_ep))
            _heartbeat(out_dir, ep, cfg["epochs"], note="%s ref_loss=%.3f" % (tag, loss_val))

    anchor_diag = None
    if use_exog:
        probe = np.sort(rng.choice(n_nodes, size=min(400, n_nodes), replace=False))
        recon_trained = 0.5 * (_recon_cos(anchors["speaker"], enc_s, Xn_t, probe, target_np=X)
                               + _recon_cos(anchors["listener"], enc_l, X_t, probe, target_np=X))
        anchor_diag = dict(recon_cos_trained=recon_trained, recon_cos_untrained=recon_untrained,
                           anchor_gain=recon_trained - recon_untrained)
    return enc_s, enc_l, chan, anchors, anchor_diag


# ---------------------------------------------------------------------------
# Per-arm run
# ---------------------------------------------------------------------------
def run_arm(arm, cfg, X, Xn, g, target_t, adj, seed, n_nodes, eval_idx, cand_idx,
            has_nb_idx, out_dir):
    enc_s, enc_l, chan, anchors, anchor_diag = train_arm(
        arm, cfg, X, Xn, adj, target_t, seed, n_nodes, out_dir, tag=arm)
    ev = eval_masks(enc_s, enc_l, chan, Xn, X, eval_idx, cand_idx, cfg["K"])
    fm = failure_mask_corr(ev["speaker_correct"], ev["listener_correct"])

    # causal-perturbation screen (speaker encoder) -- reported for ALL arms; gated only on EXOG
    prng = np.random.default_rng(seed + 7777)
    pert = causal_perturbation_ratio(enc_s, X, g, cfg["neighbor_weight"], eval_idx, has_nb_idx,
                                     prng, cfg["n_perturb_eval"])

    return dict(
        arm=arm, seed=seed,
        failmask_corr=fm["failmask_corr"], failmask_degenerate=fm["failmask_degenerate"],
        grounding_acc=ev["grounding_acc"],
        speaker_fail_rate=ev["speaker_fail_rate"], listener_fail_rate=ev["listener_fail_rate"],
        symbol_entropy_bits=ev["symbol_entropy_bits"], n_symbols_used=ev["n_symbols_used"],
        n_eval=int(eval_idx.shape[0]),
        perturb_ratio=pert["perturb_ratio"], sens_content=pert["sens_content"],
        sens_relation=pert["sens_relation"], n_perturb=pert["n_perturb"],
        anchor_diag=anchor_diag,
        _enc_s=enc_s, _enc_l=enc_l,
        _mask_digest=hashlib.sha256(
            np.concatenate([ev["speaker_correct"], ev["listener_correct"]]).tobytes()).hexdigest(),
    )


# ---------------------------------------------------------------------------
# Transitive-spread COMPANION (diagnostic; reuses snowball label-prop) -- retention check.
# ---------------------------------------------------------------------------
def transitive_spread_companion(enc, X_input, a_smooth, ground_seeds, bins, cfg, rng, tag):
    """Propagate the validated graph-smooth attribute over the FROZEN codes; near-vs-far ordering acc.
    A RETENTION check (does the arm preserve relational transitive spread) -- NOT a HARD_PASS gate."""
    with torch.no_grad():
        codes = _l2norm(enc(torch.from_numpy(X_input))).numpy().astype(np.float32)
    gs = np.asarray(ground_seeds, dtype=np.int64)
    pred = label_propagation(codes, gs, a_smooth, cfg["k_labelprop"])
    out = {}
    for b in range(4):
        idx = bins[b]
        if idx.shape[0] < 15:
            out[b] = float("nan")
        else:
            acc, _ = ordering_accuracy(pred, a_smooth, idx, rng, cfg["n_pairs_per_bin"])
            out[b] = acc
    near = out[0]
    far = float("nan")
    for b in (3, 2):
        if out[b] == out[b]:
            far = out[b]
            break
    decay = near - far if (near == near and far == far) else float("nan")
    return dict(tag=tag, near_acc=near, far_acc=far, decay=decay, by_bin=out)


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def _mean(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.size else float("nan")


def aggregate_and_verdict(per_seed_arm, cfg, subgraph_meta, run_mode, companion_agg):
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
            perturb_ratio=_mean([r["perturb_ratio"] for r in rows]),
            sens_content=_mean([r["sens_content"] for r in rows]),
            sens_relation=_mean([r["sens_relation"] for r in rows]),
            any_degenerate=any(r["failmask_degenerate"] for r in rows),
        )

    corr0 = agg[MIRROR_ARM]["failmask_corr"]
    corr_b1 = agg[B1_ARM]["failmask_corr"]
    corr_ex = agg[EXOG_ARM]["failmask_corr"]
    ground_ex = agg[EXOG_ARM]["grounding_acc"]
    ratio_ex = agg[EXOG_ARM]["perturb_ratio"]
    improve = corr_b1 - corr_ex

    codes_ok = all((agg[a]["symbol_entropy_bits"] >= ENTROPY_FLOOR_BITS)
                   and (agg[a]["n_symbols_used"] >= MIN_SYMBOLS_USED) for a in ARM_NAMES)

    # anchor-fires: every EXOG seed's anchor beat its untrained recon baseline
    anchor_gains = [r["anchor_diag"]["anchor_gain"] for r in by_arm[EXOG_ARM]
                    if r.get("anchor_diag") is not None]
    anchor_fired = (len(anchor_gains) == len(by_arm[EXOG_ARM])) and \
        all(gn >= ANCHOR_FIRE_MIN_GAIN for gn in anchor_gains)
    anchor_gain_mean = _mean(anchor_gains)

    b0_in_band = (FAILRATE_LO <= agg[MIRROR_ARM]["speaker_fail_rate"] <= FAILRATE_HI) and \
                 (FAILRATE_LO <= agg[MIRROR_ARM]["listener_fail_rate"] <= FAILRATE_HI) and \
                 (not agg[MIRROR_ARM]["any_degenerate"])
    screen_fires = (corr0 >= B0_FAILMASK_CORR_MIN) and b0_in_band
    b1_reproduces = (B1_CONTRAST_LO <= corr_b1 <= B1_CONTRAST_HI)

    hard_pass = (corr_ex <= EXOG_FAILMASK_CORR_HP) and (ground_ex >= GROUNDING_FLOOR) and \
                (improve >= EXOG_IMPROVE_MARGIN) and (ratio_ex >= PERTURB_RATIO_HP)

    if not codes_ok:
        verdict = "CODE_COLLAPSE_VOID"
    elif not anchor_fired:
        verdict = "ANCHOR_INERT_VOID"
    elif not screen_fires:
        verdict = "SATURATION_VACUOUS_SCREEN_DID_NOT_FIRE"
    elif ground_ex < GROUNDING_DESTROYED:
        verdict = "HARD_FAIL_ANCHOR_DESTROYS_GROUNDING"        # case (b)
    elif hard_pass:
        verdict = "HARD_PASS"
    elif ((corr_ex >= EXOG_FAILMASK_CORR_HF_A) or (ratio_ex < PERTURB_RATIO_HF)) and \
            (ground_ex >= GROUNDING_FLOOR):
        verdict = "HARD_FAIL_PASSIVE_EXOG_INSUFFICIENT_REDIRECT_ACTIVE_INTERVENTION"   # case (a)
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | mode=%s | B0_mirror corr=%.3f (fires=%s spk_fail=%.3f lis_fail=%.3f) | "
        "B1_crossfit corr=%.3f ground=%.3f (reproduces=%s) | B1_EXOG corr=%.3f ground=%.3f | "
        "improve(B1-EXOG)=%.3f | perturb_ratio(EXOG=%.2f B1=%.2f) | anchor_fired=%s gain=%.3f | "
        "codes_ok=%s ent(B0/B1/EXOG)=[%.2f,%.2f,%.2f] | subgraph n=%d E=%d" % (
            verdict, run_mode, corr0, screen_fires,
            agg[MIRROR_ARM]["speaker_fail_rate"], agg[MIRROR_ARM]["listener_fail_rate"],
            corr_b1, agg[B1_ARM]["grounding_acc"], b1_reproduces, corr_ex, ground_ex, improve,
            ratio_ex, agg[B1_ARM]["perturb_ratio"], anchor_fired, anchor_gain_mean, codes_ok,
            agg[MIRROR_ARM]["symbol_entropy_bits"], agg[B1_ARM]["symbol_entropy_bits"],
            agg[EXOG_ARM]["symbol_entropy_bits"],
            subgraph_meta.get("n_nodes", -1), subgraph_meta.get("n_edges", -1)))

    gates = dict(
        b0_failmask_corr=corr0, b1_failmask_corr=corr_b1, exog_failmask_corr=corr_ex,
        exog_grounding=ground_ex, exog_improvement_over_b1=improve,
        exog_perturb_ratio=ratio_ex, b1_perturb_ratio=agg[B1_ARM]["perturb_ratio"],
        screen_fires=screen_fires, b0_in_band=b0_in_band, b1_reproduces=b1_reproduces,
        codes_ok=codes_ok, anchor_fired=anchor_fired, anchor_gain_mean=anchor_gain_mean,
        hard_pass=hard_pass, per_arm=agg, transitive_companion=companion_agg,
        bands=dict(B0_FAILMASK_CORR_MIN=B0_FAILMASK_CORR_MIN, EXOG_FAILMASK_CORR_HP=EXOG_FAILMASK_CORR_HP,
                   EXOG_IMPROVE_MARGIN=EXOG_IMPROVE_MARGIN, GROUNDING_FLOOR=GROUNDING_FLOOR,
                   PERTURB_RATIO_HP=PERTURB_RATIO_HP, EXOG_FAILMASK_CORR_HF_A=EXOG_FAILMASK_CORR_HF_A,
                   PERTURB_RATIO_HF=PERTURB_RATIO_HF, GROUNDING_DESTROYED=GROUNDING_DESTROYED,
                   B1_CONTRAST_LO=B1_CONTRAST_LO, B1_CONTRAST_HI=B1_CONTRAST_HI,
                   ANCHOR_FIRE_MIN_GAIN=ANCHOR_FIRE_MIN_GAIN),
    )
    return verdict, verdict_msg, gates, agg


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs)
# ---------------------------------------------------------------------------
def discriminator_selftest():
    """(1) failure_mask_corr telemetry-sensitive (tied vs separated toy encoder -> high vs low corr).
    (2) precision_gate_weights matches the library residual_magnitude/proportional_gate elementwise.
    (3) causal-perturbation directional-sensitivity ratio is telemetry-sensitive: a content-grounded
    planted encoder shows ratio >> 1; a relation-grounded planted encoder shows ratio << 1."""
    rng = np.random.default_rng(0)

    # (1) failmask telemetry (reuse of failure_mask_corr)
    n = 400
    base = rng.random(n) < 0.6
    a = base.copy(); b = base.copy()
    a[rng.random(n) < 0.05] ^= True
    b[rng.random(n) < 0.05] ^= True
    c_high = failure_mask_corr(a, b)["failmask_corr"]
    c_low = failure_mask_corr(rng.random(n) < 0.4, rng.random(n) < 0.4)["failmask_corr"]

    # (2) precision-gate reuse fidelity vs library functions
    d = 96
    predm = rng.standard_normal((32, d)).astype(np.float32)
    tgtm = rng.standard_normal((32, d)).astype(np.float32)
    w_vec, _ = precision_gate_weights(predm, tgtm)
    lib_ok = True
    for i in range(8):
        pc = predm[i] - predm[i].mean()
        tc = tgtm[i] - tgtm[i].mean()
        ps = np.sign(pc); ps[ps == 0] = 1.0
        ts = np.sign(tc); ts[ts == 0] = 1.0
        mag = residual_magnitude(ts, ps)                       # library (order-invariant cos)
        dec = proportional_gate(ts, ps)                        # library gate
        if abs(dec.write_strength - w_vec[i]) > 1e-4 or abs(mag - w_vec[i]) > 1e-4:
            lib_ok = False
            break

    # (3) perturbation-screen sensitivity with planted encoders on orthogonal content/relation subspaces
    feat = 128; code = 24; M = 300
    Xt = np.abs(rng.standard_normal((M, feat))).astype(np.float32)   # nonneg content (like trigrams)
    Xt = _l2n_np(Xt)
    adj_toy = [list(rng.integers(0, M, size=3)) for _ in range(M)]
    g_toy = neighbor_aggregate(Xt, adj_toy)
    # content subspace = first half dims; relation subspace = second half dims
    Wc = np.zeros((code, feat), dtype=np.float32); Wr = np.zeros((code, feat), dtype=np.float32)
    Wc[:, :feat // 2] = rng.standard_normal((code, feat // 2)) * 0.1
    Wr[:, feat // 2:] = rng.standard_normal((code, feat // 2)) * 0.1
    # bias content vs relation info into disjoint dims so swaps land in the right subspace
    Xc = Xt.copy(); Xc[:, feat // 2:] *= 0.05                        # content lives in first half
    gc = g_toy.copy(); gc[:, :feat // 2] *= 0.05                     # relation lives in second half

    class _Lin(torch.nn.Module):
        def __init__(self, Wnp):
            super().__init__()
            self.lin = torch.nn.Linear(Wnp.shape[1], Wnp.shape[0], bias=False)
            with torch.no_grad():
                self.lin.weight.copy_(torch.from_numpy(Wnp))

        def forward(self, x):
            return self.lin(x)

    eval_idx = np.arange(M)
    has_nb_idx = np.arange(M)
    enc_content = _Lin(Wc)   # reads content subspace -> content-sensitive
    enc_relation = _Lin(Wr)  # reads relation subspace -> relation-sensitive
    r_c = causal_perturbation_ratio(enc_content, Xc, gc, 0.5, eval_idx, has_nb_idx,
                                    np.random.default_rng(1), M)["perturb_ratio"]
    r_r = causal_perturbation_ratio(enc_relation, Xc, gc, 0.5, eval_idx, has_nb_idx,
                                    np.random.default_rng(1), M)["perturb_ratio"]

    ok = (c_high >= 0.5) and (abs(c_low) < 0.2) and lib_ok and \
        (r_c >= 2.0) and (r_r <= 0.6)
    return bool(ok), dict(corr_planted_high=float(c_high), corr_planted_indep=float(c_low),
                          precision_gate_lib_match=bool(lib_ok),
                          perturb_ratio_content_encoder=float(r_c),
                          perturb_ratio_relation_encoder=float(r_r))


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
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (failmask/precision-gate/perturb not sensitive): %s" % st_res,
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
    g = neighbor_aggregate(X, adj)                    # for the perturbation screen
    target_t = torch.from_numpy(X.astype(np.float32))  # REAL content = exogenous reconstruction target

    eval_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 999)
    has_nb_idx = np.nonzero(np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool))[0]
    n_eval = int(min(cfg["n_eval"], has_nb_idx.shape[0]))
    eval_idx = np.sort(eval_rng.choice(has_nb_idx, size=n_eval, replace=False))
    cand_idx = build_candidate_sets(eval_idx, n_nodes, cfg["n_dist"], eval_rng)
    _log("eval referents=%d candidate_set_size=%d" % (n_eval, 1 + cfg["n_dist"]))

    # transitive-spread companion apparatus (validated graph-smooth attribute + seeds + distance bins)
    attr_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 555)
    a_smooth = make_smooth_attribute(edges, degrees, n_nodes, attr_rng, cfg["n_sources"], cfg["diffuse_steps"])
    assort_smooth = attribute_assortativity(a_smooth, edges)
    n_gs = int(min(cfg["n_ground_seeds"], n_nodes // 4))
    ground_seeds = attr_rng.choice(n_nodes, size=n_gs, replace=False)
    seed_set = set(int(x) for x in ground_seeds)
    dist = multi_source_bfs(adj, [int(x) for x in ground_seeds], n_nodes)
    comp_bins, _n_unreach = distance_bins(dist, seed_set)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator telemetry-sensitive (failmask + precision-gate reuse + "
                        "perturb-screen) + pipeline exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, subgraph_meta=meta))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed_arm = []
    unit_failures = []
    companion_rows = []
    total_units = len(cfg["seeds"]) * len(ARM_NAMES)
    u = 0
    for seed in cfg["seeds"]:
        for arm in ARM_NAMES:
            u += 1
            try:
                r = run_arm(arm, cfg, X, Xn, g, target_t, adj, seed, n_nodes, eval_idx, cand_idx,
                            has_nb_idx, out_dir_path)
                # transitive-spread companion (speaker encoder, frozen) -- diagnostic, guarded
                try:
                    comp_rng = np.random.default_rng(seed + 31337)
                    comp = transitive_spread_companion(r["_enc_s"], Xn, a_smooth, ground_seeds,
                                                       comp_bins, cfg, comp_rng, tag=arm)
                    companion_rows.append(dict(seed=seed, arm=arm, **{k: comp[k] for k in
                                              ("near_acc", "far_acc", "decay")}))
                except Exception as ce:  # companion is diagnostic; record but do not kill the unit
                    companion_rows.append(dict(seed=seed, arm=arm, companion_error=type(ce).__name__))
                    _log("COMPANION_FAILED seed=%d arm=%s class=%s: %s" % (
                        seed, arm, type(ce).__name__, str(ce)[:150]))
                r.pop("_enc_s", None); r.pop("_enc_l", None)
                per_seed_arm.append(r)
                write_partial(out_dir_path, "%s_seed%d" % (arm, seed),
                              dict(seed=seed, arm=arm, metrics={k: v for k, v in r.items()
                                                                if not k.startswith("_")}))
                _log("[%d/%d] seed=%d %s corr=%.3f ground=%.3f perturb_ratio=%.2f (c=%.4f r=%.4f) "
                     "ent=%.2f nsym=%d" % (u, total_units, seed, arm, r["failmask_corr"],
                                           r["grounding_acc"], r["perturb_ratio"], r["sens_content"],
                                           r["sens_relation"], r["symbol_entropy_bits"],
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
        present = [a for a in ARM_NAMES if a in digs]
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                a, b = present[i], present[j]
                assert digs[a] != digs[b], (
                    "META_RULE_AF VIOLATION: arms %s and %s bit-identical at seed %d" % (a, b, seed))

    # companion aggregate (per arm, mean near/far/decay across seeds)
    companion_agg = {}
    for a in ARM_NAMES:
        rows = [c for c in companion_rows if c["arm"] == a and "companion_error" not in c]
        if rows:
            companion_agg[a] = dict(
                near_acc=_mean([c["near_acc"] for c in rows]),
                far_acc=_mean([c["far_acc"] for c in rows]),
                decay=_mean([c["decay"] for c in rows]))
    companion_agg["attr_assort_smooth"] = float(assort_smooth)
    companion_agg["n_ground_seeds"] = int(n_gs)

    subgraph_meta = dict(n_nodes=meta.get("n_nodes", n_nodes), n_edges=meta.get("n_edges", len(edges)),
                         median_degree=meta.get("median_degree", -1))
    verdict, verdict_msg, gates, agg = aggregate_and_verdict(
        per_seed_arm, cfg, subgraph_meta, run_mode, companion_agg)

    per_persist = [{k: v for k, v in r.items() if not k.startswith("_")} for r in per_seed_arm]
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(cfg["seeds"]), seeds=cfg["seeds"], config=cfg, config_version=CONFIG_VERSION,
        subgraph_meta=subgraph_meta, gates=gates, per_arm_agg=agg,
        discriminator_selftest=st_res, unit_failures=unit_failures, per_unit=per_persist,
        transitive_companion_rows=companion_rows,
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
