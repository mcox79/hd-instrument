"""selfplay_message_channel_ablation_v1 -- INTERVENTIONAL test of the shared discrete MessageChannel as the
CAUSE of the corr~0.38 structural-ceiling in Speaker/Listener self-play differentiation.

WHY (Director task 2026-07-09; triggers notes/research_active_intervention_query_selection_grounding_
2026-07-09.md [S3 sharpest-residual-question: shared discrete-channel/game architecture as the next-mechanism
class], plus the three consecutive independent decorrelation mechanisms that ALL plateaued at ~0.38:
DG pattern-separation 0.377 MEASURED@data/exp_selfplay_dg_pattern_separation_xfit_v1/metrics.json:
gates.dg_failmask_corr; B1 disjoint-fold cross-fit 0.393 MEASURED@same:gates.b1_failmask_corr; B1+EXOG
shared-reconstruction-target 0.382 MEASURED@data/exp_selfplay_b1_exog_predictive_anchor_v1/metrics.json:
gates.exog_failmask_corr). A suspiciously stable floor across theoretically distinct upstream interventions
-> the active-intervention drill flagged the shared discrete MessageChannel (both self-play halves funnel
through the SAME K-symbol channel P) as the prime suspect. This cell tests it INTERVENTIONALLY: VARY the
channel, observe whether corr(failmask) MOVES. Direct causal test (perturb the suspected cause, measure the
effect), NOT a wait-and-infer.

WHAT IS ABLATED: the reference self-play game (exp_selfplay_dg_pattern_separation_xfit_v1.py /
exp_selfplay_b1_exog_predictive_anchor_v1.py) has a SINGLE shared MessageChannel: prototype matrix P
[K, code_dim]. Speaker: logits = z_S @ P.t(); message symbol = hard-gumbel argmax; message-vector =
onehot(symbol) @ P. Listener scores candidates against the SAME message-vector. Both halves are coupled by
the identical discrete K-symbol P. The four PROBE arms (A0..A3) are the SAME cross-fit self-play (separate
Enc_S/Enc_L, disjoint referent folds, speaker=neighborhood-augmented Xn, listener=bare X -- the B1_crossfit
setup that lands ~0.39) and DIFFER ONLY in the channel (one factor at a time around A0):

SIX ARMS:
  A0_shared    (BASELINE / contrast anchor): current shared discrete K-symbol channel (== B1_crossfit).
               MUST reproduce ~0.38 (band [0.30,0.46]) or the whole contrast is void.
  A1_wide      (CAPACITY up): shared discrete channel with K widened 8x (K_wide = 8*K_base). Isolates
               channel CAPACITY (collision pressure), discreteness + sharedness fixed. Does corr drop?
  A2_separate  (UN-SHARE): speaker codebook P_s and listener codebook P_l are SEPARATE matrices (same
               symbol alphabet K -- the discrete index is the wire protocol, but the code GEOMETRY is not
               shared). Speaker picks + self-decodes via P_s; listener interprets via P_l. Most direct probe
               of the sharedness hypothesis. Does corr drop?
  A3_continuous (REMOVE DISCRETENESS): the hard-gumbel one-hot is replaced by a SOFT softmax mixture over
               the SAME K prototypes P -> a continuous message vector (convex combination), no hard
               quantization. Isolates DISCRETENESS, K + sharedness fixed. Does corr drop?
  A4_mirror    (MUST-RISE CONTROL == assert_discriminator_fires): tied encoder (Enc_S == Enc_L), shared
               discrete channel; the two halves differ ONLY by info access (speaker Xn, listener bare X).
               This is the reference B0_mirror (corr ~0.77-0.79 in all three prior cells) -- the PROVEN
               high-corr control that verifies the screen CAN fire high, so a low reading on A1/A2/A3 is
               meaningful (not a universally-pinned-at-zero artifact). If A4 does NOT rise materially above
               A0, the screen is saturation-vacuous and nothing is trusted.
  A5_cap1      (CHANNEL-DESTRUCTION DIAGNOSTIC; reported, not a verdict gate): capacity-1 channel (K=1) ->
               constant message, zero channel information. Empirically (smoke) capacity-1 DROPS corr toward
               0 while collapsing grounding to chance -- because destroying the shared channel REMOVES the
               shared coupling (each half then fails independently). This is the direct complement to the
               must-rise mirror: it demonstrates the coupling is carried by the CHANNEL, and it is why the
               task's original "degraded channel RAISES corr" guess does not hold in a cross-fit regime with
               genuinely different encoders/views (documented finding, not a gate).

DISCRIMINATOR (the whole test): does corr(failmask) RESPOND to channel manipulation?
  failmask_corr(arm) = corr(1-speaker_correct, 1-listener_correct) over eval referents (phi; reused
    VERBATIM as failure_mask_corr from the DG/EXOG cells). grounding_acc = mean(listener_correct).

PRE-REGISTERED BANDS (BOTH; LOCKED PROSPECTIVE):
  HARD_PASS (the channel IS the bottleneck -- a fixable, specific target):
    A0 reproduces ~0.38 (corr in [0.30,0.46]) AND A4_mirror control fires (corr(A4)-corr(A0) >= 0.15 AND
    corr(A4) >= 0.50) AND at least ONE of {A1_wide, A2_separate, A3_continuous} DROPS MATERIALLY (arm corr
    <= 0.30 AND (corr(A0) - arm corr) >= 0.10, ideally toward ~0.20) with NON-DEGENERATE codes AND both
    load-bearing arms' (A0, A2) codes non-degenerate. => widen / separate / de-discretize the channel is
    the lever.
  HARD_FAIL (the channel is NOT the bottleneck -- a deeper, more fundamental finding):
    A0 reproduces AND A4 fires AND ALL well-measured (non-degenerate, codes-ok) probes among
    {A1_wide, A2_separate, A3_continuous} stay PINNED (|arm corr - corr(A0)| < 0.05), with the sharedness
    probe A2_separate among the valid pinned arms and >= 2 valid probes. => the shared bias is MORE
    FUNDAMENTAL than the channel; redirect to the shared ENCODER/representation both halves inherit, or the
    shared TASK/game objective itself (the 4th-consecutive-plateau redirect pre-registered in the drill S3).
  MIDDLE_BAND: partial / single-arm movement clearing neither the material-drop bar nor the all-pinned bar
    (e.g. one arm drifts 0.05-0.10 but not <=0.30) -> sweep the moved axis before concluding.
  SATURATION_VACUOUS_CONTROL_DID_NOT_FIRE: A4_mirror does not rise above A0 by the control margin => the
    screen cannot fire high; do NOT trust any arm.
  ANCHOR_NOT_REPRODUCED_VOID: A0 corr out of [0.30,0.46] => the contrast anchor is not the ~0.38 floor;
    the whole comparison is void.
  CODE_COLLAPSE_VOID: the anchor A0 or the sharedness probe A2 has collapsed message codes (entropy
    < 1.0 bit) => degenerate-code artifact; the load-bearing arms are void.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): all 6 arms' (speaker,listener) mask-pair vectors hashed;
#   A0/A1/A2/A3/A4/A5 must all differ. Bit-identical arms => channel/encoder-build bug.
# - final_metrics_atomicity: tmp_replace (write_metrics -> os.replace; crash-diag atomic).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the discriminator is a failure-mask CORRELATION vs a within-cell tied-encoder MUST-RISE
#   control (A4_mirror), not a closed-form noise floor. Reachability by construction: A4 fires high
#   (~0.77-0.79 proven in 3 prior cells), the ablated arms sit in [0, corr(A0)]; the material-drop bar
#   corr<=0.30 with margin>=0.10 vs A0 is inside; a channel-manipulation self-test proves failmask_corr
#   is telemetry-sensitive to the channel.
# - baseline_in_band (AG): A0 (the anchor) failure rates must be 0.05..0.95 for BOTH halves at smoke (else
#   corr degenerate / task saturated -> re-spec K or distractor difficulty).
# - discriminator survives scale: smoke = FULL branches at smaller n_nodes/epochs/K, SAME channel-variant
#   RATIOS (K_wide = 8*K_base; A5 K=1; A3 soft; A4 tied). SMOKE MUST show A4_mirror control fires (corr(A4)
#   materially > corr(A0)) + A0 in a measurable failure band + all arms' masks differ + core codes
#   non-degenerate. The material-drop HARD_PASS decision (corr<=0.30) is for FULL. Smoke K(=12) < FULL K(=24).
# - multi-seed smoke (3 seeds) for the correlation-discriminator per META_RULE_smoke_single_seed_inflates_AUC.
# - HARD_PASS strictly above floor: >=1 arm corr<=0.30 AND margin>=0.10 (strict) with non-degenerate codes.
# - HP_SCOPE: anchor-reproduce -> {A0}; control-fires -> {A4_mirror}; material-drop HP -> {A1,A2,A3};
#   all-pinned HF -> {A1,A2,A3} (A2 required valid); anti-collapse -> {A0,A1,A2,A3} (A4 shared K>1 OK,
#   A5 EXEMPT: capacity-1 is by-construction 1-symbol; its whole purpose is zero channel capacity).
# - cardinality_ok: EXPECTED_N_UNITS = n_arms(6) * n_seeds (no sweep axis; arms x seeds).
# - per-unit failure-class instrumentation (no bare except; per-(seed,arm) failure_class).
# - calibration_check: adaptive_with_discriminator_gate (K / K_wide / Gumbel-tau / soft-temp fixed per
#   profile; anti-collapse entropy floor + A4-control-fires + A0-in-band + channel-sensitivity self-test).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in this docstring / pre-reg.

Compute architecture: (c) mixed sequential-CPU with justification. Encoders are shallow linear ProjHeads
(feat->code) + a K x code channel matrix; per-step ops are batched matmuls / gumbel-softmax / softmax /
candidate scoring. Cost is the self-play training loop (sequential over epochs, genuine dependency); 6 arms
x 5 seeds = 30 units, but A5 (capacity-1) is nearly free and A3 (continuous) / A4 (tied, single optimizer)
are cheap. Not GPU-batching-mandatory (nets small: code_dim<=192; loop sequential-dependent). Storage
strategy: no_storage (no PartitionedStore writes; codes are transient encoder outputs). progress_logging:
print_flush_true (line-buffered stdout + flush=True progress lines + per (seed,arm) heartbeat; FULL
timeout_s >= 1800).

Reuses VERBATIM from experiments/exp_selfplay_dg_pattern_separation_xfit_v1.py: failure_mask_corr,
neighborhood_augment, build_candidate_sets, _make_encoder, _symbol_entropy_bits, _ent_reg,
_mean_pairwise_cos, _relational_positive_batch. From
experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py: load_cn_subgraph, char_trigram_features,
build_adjlist, _l2norm, info_nce, vicreg_repulsion. NEW (additive; this is the ablation): the
mode-parameterized Channel (shared / wide / separate / continuous / mirror / capacity1), the mode-dispatch
forward_game + eval_masks (each half self-decodes through its OWN codebook), the channel-sensitivity
self-test, the 6-arm channel-response verdict.
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
    _make_encoder,
    _symbol_entropy_bits,
    _ent_reg,
    _mean_pairwise_cos,
    _relational_positive_batch,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    load_cn_subgraph,
    char_trigram_features,
    build_adjlist,
    _l2norm,
    info_nce,
    vicreg_repulsion,
)

ANCHOR_NAME = "selfplay_message_channel_ablation_v1"
SUBGRAPH_BASE_SEED = 1234

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; scale + channel-variant-RATIO parity)
# K_wide = 8 * K_base in every profile; A5 K=1; A3 soft temp = the gumbel-tau schedule value.
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    n_nodes=300, seeds=[7], epochs=12, batch=128,
    code_dim=32, feat_dim=512,
    lr=0.01, lambda_ent=0.1, temp=0.15, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05,
    K=8, K_wide=64, n_dist=5, gumbel_tau=2.0, gumbel_tau_end=0.5, neighbor_weight=0.5, n_eval=150,
)
SMOKE_CFG = dict(
    n_nodes=1500, seeds=[7, 13, 17], epochs=80, batch=256,
    code_dim=96, feat_dim=4096,
    lr=0.01, lambda_ent=0.1, temp=0.15, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05,
    K=12, K_wide=96, n_dist=7, gumbel_tau=2.0, gumbel_tau_end=0.5, neighbor_weight=0.5, n_eval=700,
)
FULL_CFG = dict(
    n_nodes=8000, seeds=[7, 13, 17, 23, 29], epochs=220, batch=512,
    code_dim=192, feat_dim=8192,
    lr=0.008, lambda_ent=0.1, temp=0.12, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05,
    K=24, K_wide=192, n_dist=9, gumbel_tau=2.0, gumbel_tau_end=0.4, neighbor_weight=0.5, n_eval=3000,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (LOCKED; PROSPECTIVE)
# ---------------------------------------------------------------------------
A0_ANCHOR_LO = 0.30            # A0 must reproduce the ~0.38 cross-fit floor
A0_ANCHOR_HI = 0.46
MATERIAL_DROP_ABS = 0.30       # an ablated arm "drops materially" if corr <= this ...
MATERIAL_DROP_MARGIN = 0.10    # ... AND (corr(A0) - arm corr) >= this
PINNED_TOL = 0.05             # an arm is "pinned" if |arm corr - corr(A0)| < this
CONTROL_RISE_MARGIN = 0.15     # A4_mirror must raise corr by >= this over A0 (assert_discriminator_fires)
CONTROL_MIN_CORR = 0.50        # ... AND land at >= this absolute corr
ENTROPY_FLOOR_BITS = 1.0       # anti-collapse: discrete message symbol entropy floor
MIN_SYMBOLS_USED = 2           # anti-collapse: >= 2 distinct symbols used
A3_MSG_COS_MAX = 0.90          # A3 continuous non-degeneracy: mean pairwise cos of msg-vecs must be < this
FAILRATE_LO = 0.05             # A0 baseline_in_band lower edge (both halves)
FAILRATE_HI = 0.95             # A0 baseline_in_band upper edge (both halves)

ARM_NAMES = ["A0_shared", "A1_wide", "A2_separate", "A3_continuous", "A4_mirror", "A5_cap1"]
ARM_MODE = {
    "A0_shared": "shared_discrete",
    "A1_wide": "wide_discrete",
    "A2_separate": "separate_discrete",
    "A3_continuous": "continuous",
    "A4_mirror": "mirror",
    "A5_cap1": "capacity1",
}
A0_ARM = "A0_shared"
ABLATED_ARMS = ["A1_wide", "A2_separate", "A3_continuous"]
SHARED_PROBE = "A2_separate"          # the load-bearing sharedness probe
CONTROL_ARM = "A4_mirror"             # the must-rise (screen-can-fire-high) control
DIAG_ARM = "A5_cap1"                  # channel-destruction diagnostic (reported, not gated)
EXEMPT_CODE_ARMS = ["A5_cap1"]        # capacity-1 exempt from the entropy floor (1 symbol by construction)

CONFIG_VERSION = (
    "ANCHOR=%s,arms=%s,A0anchor=[%.2f,%.2f],dropABS<=%.2f,dropMARGIN>=%.2f,pinnedTOL<%.2f,"
    "ctrlRISE>=%.2f,ctrlMIN>=%.2f,ent>=%.2f,A3cos<%.2f,failband=[%.2f,%.2f]"
) % (ANCHOR_NAME, ARM_NAMES, A0_ANCHOR_LO, A0_ANCHOR_HI, MATERIAL_DROP_ABS, MATERIAL_DROP_MARGIN,
     PINNED_TOL, CONTROL_RISE_MARGIN, CONTROL_MIN_CORR, ENTROPY_FLOOR_BITS, A3_MSG_COS_MAX,
     FAILRATE_LO, FAILRATE_HI)

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
# The ablated MessageChannel (mode-parameterized). This IS the intervention.
# ---------------------------------------------------------------------------
def _arm_K(mode, cfg):
    if mode == "wide_discrete":
        return int(cfg["K_wide"])
    if mode == "capacity1":
        return 1
    return int(cfg["K"])


class Channel(torch.nn.Module):
    """Mode-parameterized communication channel.
      shared_discrete / wide_discrete / capacity1 / mirror: single shared prototype matrix P [K, code_dim];
        speaker logits = z@P.t(); hard-gumbel one-hot symbol; message-vec = onehot @ P.
      separate_discrete: P (speaker codebook) + P_l (listener codebook); the discrete symbol INDEX is the
        shared wire protocol, the code GEOMETRY is un-shared (each half self-decodes through its own P).
      continuous: soft softmax mixture over the SAME K prototypes P (no hard quantization); message-vec is a
        continuous convex combination -> discreteness removed, K + sharedness held fixed.
    """

    def __init__(self, mode, K, code_dim, seed):
        super().__init__()
        self.mode = mode
        self.K = K
        g = torch.Generator().manual_seed(int(seed))
        scale = 1.0 / math.sqrt(code_dim)
        self.P = torch.nn.Parameter(torch.randn(K, code_dim, generator=g) * scale)
        if mode == "separate_discrete":
            g2 = torch.Generator().manual_seed(int(seed) + 1)
            self.P_l = torch.nn.Parameter(torch.randn(K, code_dim, generator=g2) * scale)
        else:
            self.P_l = None

    def listener_P(self):
        return self.P_l if self.P_l is not None else self.P


def _channel_message(chan, z_s, tau):
    """Speaker code z_s [B, code_dim] (L2-normed) -> (msg_vec_listener [B, code_dim], msg_dist [B, K]).
    The message the LISTENER receives (used in the game loss). For the separate arm this is P_l[symbol]."""
    logits = z_s @ chan.P.t()                                    # [B, K]
    if chan.mode == "continuous":
        w = torch.softmax(logits / max(float(tau), 1e-3), dim=1)  # [B, K] soft (continuous message)
        msg_vec = w @ chan.P                                     # [B, code_dim] convex combination
        return msg_vec, w
    msg = torch.nn.functional.gumbel_softmax(logits, tau=tau, hard=True)  # [B, K] straight-through onehot
    msg_vec = msg @ chan.listener_P()                           # listener's message vector
    return msg_vec, msg


def forward_game(enc_s, enc_l, chan, Xn_t, X_t, tgt_idx, cand_idx, tau, s_grad, l_grad):
    """One referential episode. tgt_idx [B]; cand_idx [B, 1+ND] (col0=target). Returns (ref_loss, msg_dist).
    s_grad/l_grad toggle which side accumulates gradient (cross-fit / tied joint)."""
    B, C = cand_idx.shape
    zt = enc_s(Xn_t[tgt_idx])
    if not s_grad:
        zt = zt.detach()
    zt = _l2norm(zt)
    msg_vec, msg_dist = _channel_message(chan, zt, tau)
    cand_flat = cand_idx.reshape(-1)
    zc = enc_l(X_t[cand_flat])
    if not l_grad:
        zc = zc.detach()
    zc = _l2norm(zc).reshape(B, C, -1)                          # [B, C, d]
    scores = (msg_vec.unsqueeze(1) * zc).sum(dim=-1)            # [B, C]
    labels = torch.zeros(B, dtype=torch.long)                  # target is col 0
    ref_loss = torch.nn.functional.cross_entropy(scores, labels)
    return ref_loss, msg_dist


def train_arm(arm, cfg, X, Xn, adj, seed, n_nodes, out_dir, tag):
    """Train one arm's self-play game. A0/A1/A2/A3/A5: cross-fit (separate Enc_S/Enc_L, disjoint folds,
    speaker updates enc_s+P, listener updates enc_l[+P_l]); differ ONLY by channel mode. A4_mirror: tied
    encoder (Enc_L == Enc_S), joint step + relational regularizer (the reference B0). Returns
    (enc_s, enc_l, chan)."""
    mode = ARM_MODE[arm]
    feat_dim = X.shape[1]
    code_dim = cfg["code_dim"]
    Xn_t = torch.from_numpy(Xn)
    X_t = torch.from_numpy(X)
    rng = np.random.default_rng(seed + 101)
    has_nb = np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool)

    K = _arm_K(mode, cfg)
    chan = Channel("shared_discrete" if mode == "mirror" else mode, K, code_dim, seed=seed + 555)

    log_every = max(1, cfg["epochs"] // 5)
    tau0 = cfg["gumbel_tau"]
    tau1 = cfg.get("gumbel_tau_end", cfg["gumbel_tau"])
    t_ep = time.perf_counter()

    if mode == "mirror":
        # B0 mirror: tied encoder, shared channel, joint step + relational regularizer on raw features.
        enc_s = _make_encoder(feat_dim, code_dim, seed)
        enc_l = enc_s
        opt_s = torch.optim.Adam(list(enc_s.parameters()) + [chan.P], lr=cfg["lr"])
        tgt_pool = np.nonzero(has_nb)[0]
        for ep in range(cfg["epochs"]):
            tau_ep = tau0 + (tau1 - tau0) * (ep / max(1, cfg["epochs"] - 1))
            tgt = torch.from_numpy(rng.choice(tgt_pool, size=min(cfg["batch"], tgt_pool.shape[0]),
                                              replace=False).astype(np.int64))
            cand = torch.from_numpy(build_candidate_sets(tgt.numpy(), n_nodes, cfg["n_dist"], rng))
            ref_loss, msg = forward_game(enc_s, enc_l, chan, Xn_t, X_t, tgt, cand,
                                         tau_ep, s_grad=True, l_grad=True)
            a_idx, p_idx = _relational_positive_batch(tgt_pool, adj, rng, cfg["batch"])
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
                _log("  train seed=%d %s(tied,K=%d) ep=%d/%d ref_loss=%.4f (%.1fs)" % (
                    seed, tag, K, ep, cfg["epochs"], loss_val, time.perf_counter() - t_ep))
                _heartbeat(out_dir, ep, cfg["epochs"], note="%s ref_loss=%.3f" % (tag, loss_val))
        return enc_s, enc_l, chan

    # cross-fit arms (A0/A1/A2/A3/A5)
    all_idx = np.arange(n_nodes)
    rng.shuffle(all_idx)
    fold_a = np.sort(all_idx[: n_nodes // 2])
    fold_b = np.sort(all_idx[n_nodes // 2:])
    enc_s = _make_encoder(feat_dim, code_dim, seed)
    enc_l = _make_encoder(feat_dim, code_dim, seed + 333)
    s_params = list(enc_s.parameters()) + [chan.P]
    opt_s = torch.optim.Adam(s_params, lr=cfg["lr"])
    l_params = list(enc_l.parameters())
    if chan.P_l is not None:
        l_params = l_params + [chan.P_l]
    opt_l = torch.optim.Adam(l_params, lr=cfg["lr"])

    for ep in range(cfg["epochs"]):
        tau_ep = tau0 + (tau1 - tau0) * (ep / max(1, cfg["epochs"] - 1))
        for (pool, opt, sg, lg) in ((fold_a, opt_s, True, False), (fold_b, opt_l, False, True)):
            tgt = torch.from_numpy(rng.choice(pool, size=min(cfg["batch"], pool.shape[0]),
                                              replace=False).astype(np.int64))
            cand = torch.from_numpy(build_candidate_sets(tgt.numpy(), n_nodes, cfg["n_dist"], rng))
            ref_loss, msg = forward_game(enc_s, enc_l, chan, Xn_t, X_t, tgt, cand,
                                         tau_ep, s_grad=sg, l_grad=lg)
            loss = ref_loss + cfg["lambda_ent"] * _ent_reg(msg)
            opt.zero_grad()
            loss.backward()
            opt.step()
        loss_val = float(ref_loss.detach())
        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  train seed=%d %s(K=%d) ep=%d/%d ref_loss=%.4f (%.1fs)" % (
                seed, tag, K, ep, cfg["epochs"], loss_val, time.perf_counter() - t_ep))
            _heartbeat(out_dir, ep, cfg["epochs"], note="%s ref_loss=%.3f" % (tag, loss_val))
    return enc_s, enc_l, chan


def eval_masks(enc_s, enc_l, chan, Xn, X, eval_idx, cand_idx, K, tau):
    """Per-referent independent competence of each half. Each half self-decodes through its OWN codebook:
    speaker scores against P_s[symbol] (its own message vector), listener against P_l[symbol]. For the
    shared arms P_s == P_l. Returns masks + grounding + symbol entropy + (continuous) msg-vec pairwise cos."""
    Xn_t = torch.from_numpy(Xn)
    X_t = torch.from_numpy(X)
    eidx = torch.from_numpy(eval_idx.astype(np.int64))
    cand = torch.from_numpy(cand_idx.astype(np.int64))
    M, C = cand_idx.shape
    with torch.no_grad():
        zt = _l2norm(enc_s(Xn_t[eidx]))
        logits = zt @ chan.P.t()                                # [M, K]
        if chan.mode == "continuous":
            w = torch.softmax(logits / max(float(tau), 1e-3), dim=1)
            msg_s = w @ chan.P                                  # [M, d] continuous (shared)
            msg_l = msg_s
            symbols = w.argmax(dim=1)                           # dominant symbol (entropy logging)
            msg_np = msg_s.numpy().astype(np.float32)
            msg_cos = _mean_pairwise_cos(msg_np, np.random.default_rng(7), n_pairs=min(4000, M * 8))
        else:
            symbols = logits.argmax(dim=1)                      # [M] hard symbol
            msg_s = chan.P[symbols]                             # speaker's own message vector
            msg_l = chan.listener_P()[symbols]                 # listener's message vector
            msg_cos = float("nan")
        cand_flat = cand.reshape(-1)
        zc_rich = _l2norm(enc_s(Xn_t[cand_flat])).reshape(M, C, -1)
        sp_pick = (msg_s.unsqueeze(1) * zc_rich).sum(dim=-1).argmax(dim=1)
        speaker_correct = (sp_pick == 0)
        zc_bare = _l2norm(enc_l(X_t[cand_flat])).reshape(M, C, -1)
        li_pick = (msg_l.unsqueeze(1) * zc_bare).sum(dim=-1).argmax(dim=1)
        listener_correct = (li_pick == 0)
    sc = speaker_correct.numpy().astype(bool)
    lc = listener_correct.numpy().astype(bool)
    syms = symbols.numpy()
    ent, n_sym = _symbol_entropy_bits(syms, K)
    return dict(speaker_correct=sc, listener_correct=lc, symbols=syms,
                grounding_acc=float(lc.mean()),
                speaker_fail_rate=float((~sc).mean()), listener_fail_rate=float((~lc).mean()),
                symbol_entropy_bits=ent, n_symbols_used=n_sym, msg_pairwise_cos=msg_cos)


def run_arm(arm, cfg, X, Xn, adj, seed, n_nodes, eval_idx, cand_idx, out_dir):
    mode = ARM_MODE[arm]
    K = _arm_K(mode, cfg)
    enc_s, enc_l, chan = train_arm(arm, cfg, X, Xn, adj, seed, n_nodes, out_dir, tag=arm)
    tau_final = cfg.get("gumbel_tau_end", cfg["gumbel_tau"])
    ev = eval_masks(enc_s, enc_l, chan, Xn, X, eval_idx, cand_idx, K, tau_final)
    fm = failure_mask_corr(ev["speaker_correct"], ev["listener_correct"])
    return dict(
        arm=arm, seed=seed, mode=mode, K=int(K),
        failmask_corr=fm["failmask_corr"], failmask_degenerate=fm["failmask_degenerate"],
        grounding_acc=ev["grounding_acc"],
        speaker_fail_rate=ev["speaker_fail_rate"], listener_fail_rate=ev["listener_fail_rate"],
        symbol_entropy_bits=ev["symbol_entropy_bits"], n_symbols_used=ev["n_symbols_used"],
        msg_pairwise_cos=ev["msg_pairwise_cos"], n_eval=int(eval_idx.shape[0]),
        _mask_digest=hashlib.sha256(
            np.concatenate([ev["speaker_correct"], ev["listener_correct"]]).tobytes()).hexdigest(),
    )


# ---------------------------------------------------------------------------
# Per-arm code non-degeneracy (anti-collapse). A5 (capacity-1) is EXEMPT by construction.
# ---------------------------------------------------------------------------
def _arm_codes_ok(arm, a):
    """a: aggregated arm dict. Returns (ok, reason). Discrete K>1 arms: entropy + symbols. Continuous:
    dominant-symbol entropy + message-vector non-collapse (mean pairwise cos < ceiling). A5: exempt."""
    if arm in EXEMPT_CODE_ARMS:
        return True, "exempt_capacity1"
    if a["failmask_corr"] != a["failmask_corr"]:  # NaN guard
        return False, "corr_nan"
    if arm == "A3_continuous":
        ent_ok = a["symbol_entropy_bits"] >= ENTROPY_FLOOR_BITS
        cos = a["msg_pairwise_cos"]
        cos_ok = (cos == cos) and (cos <= A3_MSG_COS_MAX)   # not collapsed to one direction
        if ent_ok and cos_ok:
            return True, "ok"
        return False, "cont_degenerate(ent=%.2f,msg_cos=%.3f)" % (a["symbol_entropy_bits"], cos)
    ok = (a["symbol_entropy_bits"] >= ENTROPY_FLOOR_BITS) and (a["n_symbols_used"] >= MIN_SYMBOLS_USED)
    return (ok, "ok" if ok else "code_collapse(ent=%.2f,nsym=%.1f)" % (
        a["symbol_entropy_bits"], a["n_symbols_used"]))


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def _mean(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.size else float("nan")


def aggregate_and_verdict(per_seed_arm, cfg, subgraph_meta, run_mode):
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
            msg_pairwise_cos=_mean([r["msg_pairwise_cos"] for r in rows]),
            K=int(rows[0]["K"]) if rows else -1,
            any_degenerate=any(r["failmask_degenerate"] for r in rows),
        )

    corr0 = agg[A0_ARM]["failmask_corr"]
    corr_ctrl = agg[CONTROL_ARM]["failmask_corr"]

    codes_reason = {}
    codes_ok_map = {}
    for a in ARM_NAMES:
        ok, reason = _arm_codes_ok(a, agg[a])
        codes_ok_map[a] = ok
        codes_reason[a] = reason

    def _valid(a):
        return codes_ok_map[a] and (not agg[a]["any_degenerate"])

    def _dropped(a):
        if not _valid(a):
            return False
        c = agg[a]["failmask_corr"]
        return (c <= MATERIAL_DROP_ABS) and ((corr0 - c) >= MATERIAL_DROP_MARGIN)

    def _pinned(a):
        if not _valid(a):
            return False
        return abs(agg[a]["failmask_corr"] - corr0) < PINNED_TOL

    moved_arms = [a for a in ABLATED_ARMS if _dropped(a)]
    valid_arms = [a for a in ABLATED_ARMS if _valid(a)]
    pinned_arms = [a for a in ABLATED_ARMS if _pinned(a)]
    unpinned_valid = [a for a in valid_arms if a not in pinned_arms]

    a0_reproduces = (A0_ANCHOR_LO <= corr0 <= A0_ANCHOR_HI) and _valid(A0_ARM)
    control_fires = ((corr_ctrl - corr0) >= CONTROL_RISE_MARGIN) and (corr_ctrl >= CONTROL_MIN_CORR)
    core_codes_ok = codes_ok_map[A0_ARM] and codes_ok_map[SHARED_PROBE]

    all_valid_pinned = (SHARED_PROBE in valid_arms) and (len(valid_arms) >= 2) and \
                       (len(unpinned_valid) == 0) and (len(moved_arms) == 0)

    if not core_codes_ok:
        verdict = "CODE_COLLAPSE_VOID"
    elif not control_fires:
        verdict = "SATURATION_VACUOUS_CONTROL_DID_NOT_FIRE"
    elif not a0_reproduces:
        verdict = "ANCHOR_NOT_REPRODUCED_VOID"
    elif len(moved_arms) >= 1:
        verdict = "HARD_PASS_CHANNEL_IS_BOTTLENECK"
    elif all_valid_pinned:
        verdict = "HARD_FAIL_CHANNEL_NOT_BOTTLENECK_REDIRECT_ENCODER_OR_TASK"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_CHANNEL_MOVEMENT"

    corr_move = {a: (agg[a]["failmask_corr"] - corr0) for a in ABLATED_ARMS}
    verdict_msg = (
        "%s | mode=%s | A0_shared corr=%.3f ground=%.3f (repro=%s spk_fail=%.3f lis_fail=%.3f) | "
        "A1_wide(K=%d) corr=%.3f (d=%+.3f) | A2_separate corr=%.3f (d=%+.3f spk_fail=%.3f) | "
        "A3_continuous corr=%.3f (d=%+.3f msg_cos=%.3f) | A4_mirror corr=%.3f (rise=%+.3f fires=%s) | "
        "A5_cap1 corr=%.3f ground=%.3f [diag] | moved=%s pinned=%s | codes=%s | subgraph n=%d E=%d" % (
            verdict, run_mode, corr0, agg[A0_ARM]["grounding_acc"], a0_reproduces,
            agg[A0_ARM]["speaker_fail_rate"], agg[A0_ARM]["listener_fail_rate"],
            agg["A1_wide"]["K"], agg["A1_wide"]["failmask_corr"], corr_move["A1_wide"],
            agg["A2_separate"]["failmask_corr"], corr_move["A2_separate"],
            agg["A2_separate"]["speaker_fail_rate"],
            agg["A3_continuous"]["failmask_corr"], corr_move["A3_continuous"],
            agg["A3_continuous"]["msg_pairwise_cos"],
            corr_ctrl, corr_ctrl - corr0, control_fires,
            agg[DIAG_ARM]["failmask_corr"], agg[DIAG_ARM]["grounding_acc"],
            moved_arms, pinned_arms,
            {a: codes_reason[a] for a in ARM_NAMES},
            subgraph_meta.get("n_nodes", -1), subgraph_meta.get("n_edges", -1)))

    gates = dict(
        a0_failmask_corr=corr0, a4_mirror_failmask_corr=corr_ctrl,
        a1_failmask_corr=agg["A1_wide"]["failmask_corr"],
        a2_failmask_corr=agg["A2_separate"]["failmask_corr"],
        a3_failmask_corr=agg["A3_continuous"]["failmask_corr"],
        a5_cap1_failmask_corr=agg[DIAG_ARM]["failmask_corr"],
        a5_cap1_grounding=agg[DIAG_ARM]["grounding_acc"],
        corr_move=corr_move, control_rise=corr_ctrl - corr0,
        a0_reproduces=a0_reproduces, control_fires=control_fires, core_codes_ok=core_codes_ok,
        moved_arms=moved_arms, valid_arms=valid_arms, pinned_arms=pinned_arms,
        codes_ok_map=codes_ok_map, codes_reason=codes_reason,
        a0_grounding=agg[A0_ARM]["grounding_acc"], per_arm=agg,
        bands=dict(A0_ANCHOR_LO=A0_ANCHOR_LO, A0_ANCHOR_HI=A0_ANCHOR_HI,
                   MATERIAL_DROP_ABS=MATERIAL_DROP_ABS, MATERIAL_DROP_MARGIN=MATERIAL_DROP_MARGIN,
                   PINNED_TOL=PINNED_TOL, CONTROL_RISE_MARGIN=CONTROL_RISE_MARGIN,
                   CONTROL_MIN_CORR=CONTROL_MIN_CORR, ENTROPY_FLOOR_BITS=ENTROPY_FLOOR_BITS,
                   A3_MSG_COS_MAX=A3_MSG_COS_MAX),
    )
    return verdict, verdict_msg, gates, agg


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs)
# ---------------------------------------------------------------------------
def _toy_channel_corr(mode, feats, Wenc, Wlist, K, M, ND, rng):
    """Tiny synthetic self-play decode with a given channel mode; returns failmask_corr. Metric-sensitivity
    probe: on shared-ish toy encoders a capacity-1 (constant-message) channel raises failmask_corr vs a wide
    informative channel -> the metric MOVES with a channel manipulation."""
    d_code = Wenc.shape[1]

    def _l2(z):
        return z / (np.linalg.norm(z, axis=-1, keepdims=True) + 1e-8)

    P = rng.standard_normal((K, d_code)).astype(np.float32) / math.sqrt(d_code)
    tgt_feat = feats[:M]
    zt = _l2(tgt_feat @ Wenc)                                   # [M, d_code]
    if mode == "capacity1":
        msg_vec = np.repeat((P[0])[None, :], M, axis=0)         # constant message (zero information)
    else:
        sym = (zt @ P.T).argmax(1)
        msg_vec = P[sym]                                        # informative discrete message
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
        s_correct[i] = int((msg_vec[i] * zs).sum(1).argmax()) == 0
        l_correct[i] = int((msg_vec[i] * zl).sum(1).argmax()) == 0
    return failure_mask_corr(s_correct, l_correct)["failmask_corr"]


def discriminator_selftest():
    """(1) failure_mask_corr is telemetry-sensitive (planted correlated -> high; independent -> ~0).
    (2) CHANNEL-sensitivity: on shared-ish toy encoders a capacity-1 (constant-message) channel raises
    failmask_corr vs a wide informative channel on the SAME encoders -> the metric RESPONDS to a channel
    manipulation. Averaged over donor seeds; asserts cap1_mean > wide_mean + margin AND cap1_mean high.
    (NOTE: in the real cross-fit regime with genuinely-different encoders/views, capacity-1 instead DROPS
    corr because it removes the shared coupling -- an empirical finding, not a metric property.)"""
    rng = np.random.default_rng(0)
    n = 500
    base = rng.random(n) < 0.6
    a_corr = base.copy(); b_corr = base.copy()
    a_corr[rng.random(n) < 0.05] ^= True
    b_corr[rng.random(n) < 0.05] ^= True
    c_high = failure_mask_corr(a_corr, b_corr)["failmask_corr"]
    c_low = failure_mask_corr(rng.random(n) < 0.4, rng.random(n) < 0.4)["failmask_corr"]

    d_feat, d_code, M, ND = 128, 24, 600, 5
    Wenc = rng.standard_normal((d_feat, d_code)).astype(np.float32)
    Wlist = (Wenc + 0.35 * rng.standard_normal((d_feat, d_code)).astype(np.float32))  # lightly different
    feats = rng.standard_normal((M, d_feat)).astype(np.float32)
    wide_vals, cap1_vals = [], []
    for ds in (11, 12, 13, 14, 15):
        wide_vals.append(_toy_channel_corr("wide", feats, Wenc, Wlist, 64, M, ND, np.random.default_rng(ds)))
        cap1_vals.append(_toy_channel_corr("capacity1", feats, Wenc, Wlist, 1, M, ND,
                                           np.random.default_rng(ds)))
    corr_wide = float(np.mean(wide_vals))
    corr_cap1 = float(np.mean(cap1_vals))
    channel_sensitive = (corr_cap1 > corr_wide + 0.08) and (corr_cap1 >= 0.5)

    ok = (c_high >= 0.5) and (abs(c_low) < 0.2) and channel_sensitive
    return bool(ok), dict(corr_planted_high=float(c_high), corr_planted_indep=float(c_low),
                          toy_corr_wide_channel=float(corr_wide), toy_corr_cap1_channel=float(corr_cap1),
                          metric_responds_to_channel=bool(channel_sensitive))


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
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (failmask/channel not sensitive): %s" % st_res,
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
            verdict_msg="SELFTEST_PASS discriminator telemetry-sensitive (failmask + channel) + pipeline "
                        "exercised",
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
                     "ent=%.2f nsym=%d msg_cos=%.3f" % (
                         u, total_units, seed, arm, r["failmask_corr"], r["grounding_acc"],
                         r["speaker_fail_rate"], r["listener_fail_rate"], r["symbol_entropy_bits"],
                         r["n_symbols_used"], r["msg_pairwise_cos"]))
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

    # ARMS-MUST-DIFFER (META_RULE_AF): all 6 arms' mask-pairs must differ per seed
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
