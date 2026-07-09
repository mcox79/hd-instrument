"""selfplay_differentiation_failmask_decorrelation_v1 -- the decisive 4-arm screen for master-map BUILD #2
(internal self-play referential grounding): WHICH minimal differentiation makes a shared-substrate
Speaker/Listener pair have GENUINELY INDEPENDENT failure modes (uncorrelated per-referent failure masks),
and does that differentiation cost the pair its ability to still AGREE (communicative grounding)?

WHY (Director steer 2026-07-09; drill
notes/research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md):
  The POSSIBILITY question is CLOSED (the brain proves a system can be its own independent partner). The
  open question is the MECHANISM: a shared-weight Speaker/Listener differing ONLY in information access is a
  MIRROR that shares its blind spots -- the stacked-corrections failure signature corr(failure_mask_A,
  failure_mask_B) ~ 0.49 on the landed pfc_gate_waypoint_rescue_kb_grounded_check_v1 cell. Three independent
  literatures (SSL collapse theory, emergent-communication, formal ensemble/Neyman-orthogonality) converge:
  info-access asymmetry ALONE is insufficient; at least one further differentiation axis is required. This
  cell tests that convergent prediction on THIS substrate's relational encoder, and screens whether the
  differentiation destroys grounding (differentiation is worthless if the two halves can no longer agree).

MECHANISM UNDER TEST (NOT assumed to work; P_deflated ~0.60 differentiation-required, ~0.25-0.30 cross-fit
  transfers cleanly, ~0.12-0.15 the load-bearing negative that even proven fixes fail):
  A self-play referential naming game on the REUSED teacher-free relational encoder (ProjHead + InfoNCE +
  VICReg over a ConceptNet subgraph; cert 06e5a493d). Referents = subgraph nodes. Speaker has PRIVILEGED
  info access (neighborhood-augmented feature Xn = node feature + mean-neighbor feature); Listener has BARE
  info access (node char-trigram feature X only). A SHARED discrete message channel (K-symbol prototype
  matrix P; K << n_referents; the anti-collapse bottleneck) is the ONLY communication path -- shared in ALL
  arms because the channel is the medium, not the differentiation axis. Speaker emits symbol m(r) =
  argmax_k Enc_S(Xn[r]) . P[k] (straight-through Gumbel at train). Listener decodes m over a candidate set
  {target}+distractors: pick = argmax_c P[m] . Enc_L(X[c]).

FOUR ARMS (differentiation of Speaker vs Listener; B0-B3 per Director task):
  B0 (mirror / MUST-FAIL control): Enc_S and Enc_L are the SAME tied module, live gradients on both, differ
     ONLY in information access. Predicted HIGH failmask-corr (the shared-blind-spot signature). If B0 does
     NOT show high corr at smoke the screen is saturation-vacuous and MUST re-spec (assert_discriminator_fires).
  B1 (disjoint-data cross-fit; the drill's cheapest PROVEN-rho=0 fix): separate Enc_S/Enc_L; Speaker params
     fit ONLY on referent fold A, Listener params ONLY on disjoint fold B (channel P shared).
  B2 (parameter-lag EMA; BYOL/DINO analog): Enc_L is an EMA/stop-gradient-lagged copy of Enc_S.
  B3 (differentiated algorithm-class; cerebellum analog, strongest biological track record): Listener is a
     genuinely different, TRAINABLE computational device -- a 2-layer ReLU MLP (ListenerMLP), a different
     architecture family from the speaker's linear ProjHead. Trained jointly (so grounding is a fair test,
     not a lobotomy); the differentiation is the architecture/algorithm class, not removal of learning.

THE SCREEN (reused VERBATIM from exp_pfc_gate_waypoint_rescue_stacked_corrections_v1.py:failure_mask_corr):
  Per referent r over an eval set, two INDEPENDENT per-half competence outcomes on the SAME decision:
    speaker_correct[r] = argmax_c P[m(r)] . Enc_S(Xn[c]) == r   (speaker self-decode, its privileged view)
    listener_correct[r] = argmax_c P[m(r)] . Enc_L(X[c])  == r  (the actual listener, its bare view;
                                                                  == the JOINT communicative-grounding event)
  failmask_corr(arm) = corr(1-speaker_correct, 1-listener_correct) over referents (phi coefficient).
  Under tied weights (B0) the two decode with the SAME weights but info-asymmetric inputs (rich vs bare
  candidate features) => correlated-but-not-identical errors => high corr (mirror). Under a real
  differentiation axis (B1/B2/B3) Enc_S != Enc_L => errors decorrelate.
  grounding_acc(arm) = mean(listener_correct) = the joint game success (differentiation is void if it
  destroys this; the grounding FLOOR guards it).

PRE-REGISTERED BANDS (BOTH; per drill HARD-PASS / HARD-FAIL(a)/(b) / MIDDLE):
  HARD_PASS (differentiation is the operative ingredient AND it preserves grounding):
    B0 failmask_corr >= 0.40 (screen fires; matches the ~0.49 precedent) AND at least one of B1/B2/B3 has
    failmask_corr <= 0.20 AND (corr(B0) - corr(that arm)) >= 0.20 AND grounding_acc(that arm) >= 0.50 AND
    all arms' message codes non-degenerate (symbol entropy >= 1.0 bit, >=2 symbols used) AND B0 failure
    rates in-band (0.05..0.95 for both halves; the corr is measurable, not degenerate).
  HARD_FAIL variant (b) -- the load-bearing negative (differentiation blocked on this substrate):
    among the arms that RETAIN grounding (>=0.50), NONE achieves failmask_corr <= 0.35
    => even proven differentiation axes fail to decorrelate; common cause lives UPSTREAM of the split (the
       shared relational encoder). Fallback: differentiate the upstream representation (CLS/efference lesson).
  HARD_FAIL variant (grounding-destroyed): the arms that DO decorrelate (corr <= 0.20) ALL have
    grounding_acc < 0.50 => decorrelation only at the cost of destroyed communication (shared-substrate
    self-play grounding genuinely in tension with independence). Flag loudly.
  SATURATION_VACUOUS (screen did not fire): B0 failmask_corr < 0.40 at smoke OR B0 failure-rate degenerate
    => the discriminator is not firing; re-spec (tighten K / augmentation), do NOT trust full.
  CODE_COLLAPSE_VOID: any arm's message code collapsed (entropy < 1.0 bit) => emergent-comm degenerate-code
    artifact; the whole test is void.
  MIDDLE_BAND: partial decorrelation (best grounding-retaining arm corr in (0.20, 0.35]) with grounding
    retained -- sweep differentiation strength before concluding.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): the 4 arms' (speaker,listener) mask-pair vectors hashed;
#   B0 vs B1/B2/B3 must differ (exempt none). Bit-identical arms => arm-implementation bug.
# - final_metrics_atomicity: tmp_replace (write_metrics -> os.replace; crash-diag atomic).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the discriminator is a failure-mask CORRELATION vs a within-cell MUST-FAIL control (B0), not a
#   closed-form noise floor; reachability by construction (B0 fires the high-corr baseline at smoke, the
#   proven-differentiation arms sit inside [0, corr(B0)] -- HP bar corr<=0.20 with margin>=0.20 is inside).
# - baseline_in_band (AG): B0 (the MUST-FAIL mirror) failure rates must be 0.05..0.95 for BOTH halves at
#   smoke (else corr degenerate / task saturated -> re-spec K or distractor difficulty).
# - discriminator survives scale: smoke = FULL branches at smaller n_nodes/epochs/K (option-C preview).
#   SMOKE MUST show B0 failmask_corr >= 0.40 (assert_discriminator_fires) before any FULL dispatch; the
#   must-fail mirror control firing at smoke scale is the scale evidence. Smoke K(=12) < FULL K(=24) so
#   smoke has HIGHER collision pressure -> smoke grounding is a conservative LOWER bound on FULL grounding
#   (differentiation arms that retain grounding at smoke retain it at FULL); the 4-arm corr/grounding spread
#   is the qualitative preview FULL sharpens with 5 seeds + headroom.
# - HARD_PASS strictly above floor: corr(diff)<=0.20 AND margin>=0.20 AND grounding>=0.50 (all strict).
# - HP_SCOPE: decorrelation HP gates apply to {B1,B2,B3} vs B0; screen-fires gate applies to B0; grounding
#   floor applies to whichever diff arm is claimed; anti-collapse applies to ALL arms.
# - cardinality_ok: EXPECTED_N_UNITS = n_arms(4) * n_seeds (no sweep axis; arms x seeds).
# - per-unit failure-class instrumentation (no bare except; per-seed fatal-flag + failure_class).
# - calibration_check: adaptive_with_discriminator_gate (message bottleneck K + Gumbel tau fixed per
#   profile; anti-collapse entropy floor + B0-fires + baseline-in-band recomputed per run, not tuned-for-PASS).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.

Compute architecture: (c) mixed sequential-CPU with justification. Encoders are shallow linear ProjHeads
(feat->code) + a K x code channel; per-step ops are batched matmuls / gumbel-softmax / candidate scoring.
Matches the landed teacher-free relational encoder pipeline (CPU-only, cert 06e5a493d) and grounding_snowball
(CPU FULL). Not GPU-batching-mandatory: nets are small (code_dim<=192, feat_dim<=8192), the cost is the
self-play training loop (sequential over epochs, genuine dependency) and 4 arms x 5 seeds is minutes on CPU.
Storage strategy: no_storage (no PartitionedStore writes; codes are transient encoder outputs).
progress_logging: print_flush_true (line-buffered stdout + flush=True progress lines + per (seed,arm)
heartbeat; FULL timeout_s >= 1800).

Reuses VERBATIM from experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py: load_cn_subgraph,
char_trigram_features, build_adjlist, ProjHead, info_nce, vicreg_repulsion, _l2norm. Reuses VERBATIM from
experiments/exp_pfc_gate_waypoint_rescue_stacked_corrections_v1.py: failure_mask_corr (the load-bearing
per-referent failure-mask phi-correlation screen). NEW (additive): neighborhood_augment, MessageChannel,
build_candidate_sets, train_arm (per-arm differentiation update rules), eval_masks, the 4 arms + the
decorrelation-vs-grounding verdict.
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

ANCHOR_NAME = "selfplay_differentiation_failmask_decorrelation_v1"
SUBGRAPH_BASE_SEED = 1234

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; only scale differs)
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    n_nodes=300, seeds=[7], epochs=12, batch=128,
    code_dim=32, feat_dim=512, temp=0.15, lr=0.01,
    lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05, lambda_ent=0.1,
    K=8, n_dist=5, gumbel_tau=2.0, gumbel_tau_end=0.5, mlp_hidden=64,
    neighbor_weight=0.5, ema_decay=0.9, n_eval=150,
)
SMOKE_CFG = dict(
    n_nodes=2000, seeds=[7, 13], epochs=100, batch=256,
    code_dim=96, feat_dim=4096, temp=0.15, lr=0.01,
    lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05, lambda_ent=0.1,
    K=12, n_dist=7, gumbel_tau=2.0, gumbel_tau_end=0.5, mlp_hidden=128,
    neighbor_weight=0.5, ema_decay=0.95, n_eval=800,
)
FULL_CFG = dict(
    n_nodes=8000, seeds=[7, 13, 17, 23, 29], epochs=220, batch=512,
    code_dim=192, feat_dim=8192, temp=0.12, lr=0.008,
    lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05, lambda_ent=0.1,
    K=24, n_dist=9, gumbel_tau=2.0, gumbel_tau_end=0.4, mlp_hidden=256,
    neighbor_weight=0.5, ema_decay=0.99, n_eval=3000,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (LOCKED; PROSPECTIVE)
# ---------------------------------------------------------------------------
B0_FAILMASK_CORR_MIN = 0.40    # HARD_PASS + assert_discriminator_fires: mirror shows shared-blind-spot corr
DIFF_FAILMASK_CORR_HP = 0.20   # HARD_PASS: a differentiation arm decorrelates below this (research note)
DECORR_MARGIN_HP = 0.20        # HARD_PASS: corr(B0) - corr(diff arm) >= this (well below the mirror)
GROUNDING_FLOOR = 0.50         # HARD_PASS: the decorrelating arm still communicates (>> chance 1/(1+n_dist))
DIFF_FAILMASK_CORR_HF = 0.35   # HARD_FAIL(b): no grounding-retaining arm gets corr <= this
ENTROPY_FLOOR_BITS = 1.0       # anti-collapse: message code entropy floor (>=~2 effective symbols)
MIN_SYMBOLS_USED = 2           # anti-collapse: at least 2 distinct symbols in use
FAILRATE_LO = 0.05             # B0 baseline_in_band lower edge (both halves)
FAILRATE_HI = 0.95             # B0 baseline_in_band upper edge (both halves)

ARM_NAMES = ["B0_mirror", "B1_crossfit", "B2_ema_lag", "B3_diff_algclass"]
DIFF_ARMS = ["B1_crossfit", "B2_ema_lag", "B3_diff_algclass"]
MIRROR_ARM = "B0_mirror"

CONFIG_VERSION = (
    "ANCHOR=%s,arms=%s,B0corr>=%.2f,diffcorr<=%.2f,margin>=%.2f,ground>=%.2f,HFb>%.2f,ent>=%.2f,"
    "failband=[%.2f,%.2f]"
) % (ANCHOR_NAME, ARM_NAMES, B0_FAILMASK_CORR_MIN, DIFF_FAILMASK_CORR_HP, DECORR_MARGIN_HP,
     GROUNDING_FLOOR, DIFF_FAILMASK_CORR_HF, ENTROPY_FLOOR_BITS, FAILRATE_LO, FAILRATE_HI)

_T0 = time.time()


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


RUN_MODE_GLOBAL = "full"


# ---------------------------------------------------------------------------
# REUSED VERBATIM from exp_pfc_gate_waypoint_rescue_stacked_corrections_v1.py
# ---------------------------------------------------------------------------
def failure_mask_corr(kb_correct, sel_correct):
    """THE load-bearing screen: corr(failure_mask_A, failure_mask_B) over per-referent final correctness.
    failure = arm got the referent WRONG. Near-zero => independent failures (genuine differentiation).
    High => shared blind spots (the mirror). Degenerate (an arm all-right or all-wrong) => corr=0 flagged."""
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
# NEW: referent world helpers
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
    """Shared K-symbol prototype matrix P [K, code_dim] -- the communication bottleneck (the medium,
    shared across ALL arms). Speaker logits = z_S @ P.t(); message-vector = onehot(symbol) @ P."""

    def __init__(self, K, code_dim):
        super().__init__()
        self.P = torch.nn.Parameter(torch.randn(K, code_dim) * (1.0 / math.sqrt(code_dim)))


class ListenerMLP(torch.nn.Module):
    """B3 axis-4 device: a genuinely DIFFERENT (trainable) architecture family from the speaker's linear
    ProjHead -- a 2-layer ReLU MLP feat->hidden->code. Different algorithm/architecture class, still learns
    (so a grounding loss is NOT a crippling artifact; the cerebellum analog is a different device, not a
    lobotomized one). Matches ProjHead's forward(x)->raw-code interface (caller L2-normalizes)."""

    def __init__(self, feat_dim, code_dim, hidden):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(feat_dim, hidden, bias=True),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden, code_dim, bias=False),
        )

    def forward(self, x):
        return self.net(x)


def _make_encoder(feat_dim, code_dim, seed, trainable):
    torch.manual_seed(seed)
    enc = ProjHead(feat_dim, code_dim)
    if not trainable:
        for p in enc.parameters():
            p.requires_grad_(False)
    return enc


def _symbol_entropy_bits(symbols, K):
    """Marginal message-symbol entropy in bits + number of distinct symbols used."""
    counts = np.bincount(np.asarray(symbols, dtype=np.int64), minlength=K).astype(np.float64)
    p = counts / max(counts.sum(), 1.0)
    nz = p[p > 0]
    ent = float(-(nz * np.log2(nz)).sum()) if nz.size else 0.0
    return ent, int((counts > 0).sum())


# ---------------------------------------------------------------------------
# NEW: per-arm self-play training + evaluation
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
    """Train one differentiation arm's self-play game. Returns (enc_s, enc_l, chan)."""
    feat_dim = X.shape[1]
    code_dim = cfg["code_dim"]
    Xn_t = torch.from_numpy(Xn)
    X_t = torch.from_numpy(X)
    rng = np.random.default_rng(seed + 101)

    # fold split for cross-fit (B1); all-nodes pool otherwise
    all_idx = np.arange(n_nodes)
    rng.shuffle(all_idx)
    fold_a = np.sort(all_idx[: n_nodes // 2])
    fold_b = np.sort(all_idx[n_nodes // 2:])

    has_nb = np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool)

    chan = MessageChannel(cfg["K"], code_dim)
    if arm == "B0_mirror":
        enc_s = _make_encoder(feat_dim, code_dim, seed, trainable=True)
        enc_l = enc_s                                        # TIED (shared weights)
    elif arm == "B3_diff_algclass":
        enc_s = _make_encoder(feat_dim, code_dim, seed, trainable=True)
        torch.manual_seed(seed + 777)
        enc_l = ListenerMLP(feat_dim, code_dim, cfg["mlp_hidden"])  # trainable DIFFERENT architecture class
    else:  # B1 cross-fit, B2 ema-lag
        enc_s = _make_encoder(feat_dim, code_dim, seed, trainable=True)
        enc_l = _make_encoder(feat_dim, code_dim, seed + 333, trainable=True)

    if arm == "B2_ema_lag":
        # initialize EMA target = speaker weights, no grad
        with torch.no_grad():
            enc_l.lin.weight.copy_(enc_s.lin.weight)
        for p in enc_l.parameters():
            p.requires_grad_(False)

    # optimizers
    s_params = list(enc_s.parameters()) + list(chan.parameters())
    opt_s = torch.optim.Adam(s_params, lr=cfg["lr"])
    if arm in ("B1_crossfit", "B2_ema_lag", "B3_diff_algclass"):
        l_params = [p for p in enc_l.parameters() if p.requires_grad]
        opt_l = torch.optim.Adam(l_params, lr=cfg["lr"]) if l_params else None
    else:
        opt_l = None

    log_every = max(1, cfg["epochs"] // 5)
    tau0 = cfg["gumbel_tau"]
    tau1 = cfg.get("gumbel_tau_end", cfg["gumbel_tau"])
    t_ep = time.perf_counter()
    for ep in range(cfg["epochs"]):
        tau_ep = tau0 + (tau1 - tau0) * (ep / max(1, cfg["epochs"] - 1))  # anneal high->low for ST-Gumbel
        if arm == "B1_crossfit":
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
        else:
            tgt_pool = np.nonzero(has_nb)[0]
            tgt = torch.from_numpy(rng.choice(tgt_pool, size=min(cfg["batch"], tgt_pool.shape[0]),
                                              replace=False).astype(np.int64))
            cand = torch.from_numpy(build_candidate_sets(tgt.numpy(), n_nodes, cfg["n_dist"], rng))
            l_grad = (opt_l is not None)
            ref_loss, msg = _forward_game(enc_s, enc_l, chan, Xn_t, X_t, tgt, cand,
                                          tau_ep, s_grad=True, l_grad=l_grad)
            # relational regularizer keeps the speaker encoder on the substrate's relational manifold
            a_idx, p_idx = _relational_positive_batch(np.nonzero(has_nb)[0], adj, rng, cfg["batch"])
            za = enc_s(Xn_t[torch.from_numpy(a_idx)])
            zp = enc_s(Xn_t[torch.from_numpy(p_idx)])
            rel = info_nce(za, zp, cfg["temp"]) + vicreg_repulsion(
                torch.cat([za, zp], dim=0), cfg["lambda_cov"], cfg["lambda_var"])
            loss = ref_loss + cfg["lambda_ent"] * _ent_reg(msg) + cfg["lambda_rel"] * rel
            opt_s.zero_grad()
            if opt_l is not None:
                opt_l.zero_grad()
            loss.backward()
            opt_s.step()
            if opt_l is not None:
                opt_l.step()
            if arm == "B2_ema_lag":
                with torch.no_grad():
                    d = cfg["ema_decay"]
                    enc_l.lin.weight.mul_(d).add_(enc_s.lin.weight.detach(), alpha=1.0 - d)
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
        # speaker self-decode over candidates with its PRIVILEGED (augmented) view
        zc_rich = _l2norm(enc_s(Xn_t[cand_flat])).reshape(M, C, -1)
        sp_pick = (Ps.unsqueeze(1) * zc_rich).sum(dim=-1).argmax(dim=1)
        speaker_correct = (sp_pick == 0)
        # listener decode over candidates with its BARE view (== the joint grounding event)
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
    enc_s, enc_l, chan = train_arm(arm, cfg, X, Xn, adj, seed, n_nodes, out_dir, tag=arm)
    ev = eval_masks(enc_s, enc_l, chan, Xn, X, eval_idx, cand_idx, cfg["K"])
    fm = failure_mask_corr(ev["speaker_correct"], ev["listener_correct"])
    return dict(
        arm=arm, seed=seed,
        failmask_corr=fm["failmask_corr"], failmask_degenerate=fm["failmask_degenerate"],
        grounding_acc=ev["grounding_acc"],
        speaker_fail_rate=ev["speaker_fail_rate"], listener_fail_rate=ev["listener_fail_rate"],
        symbol_entropy_bits=ev["symbol_entropy_bits"], n_symbols_used=ev["n_symbols_used"],
        n_eval=int(eval_idx.shape[0]),
        _mask_digest=hashlib.sha256(
            np.concatenate([ev["speaker_correct"], ev["listener_correct"]]).tobytes()).hexdigest(),
    )


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def _mean(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.size else float("nan")


def aggregate_and_verdict(per_seed_arm, subgraph_meta, run_mode):
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

    # anti-collapse gate (ALL arms)
    codes_ok = all((agg[a]["symbol_entropy_bits"] >= ENTROPY_FLOOR_BITS)
                   and (agg[a]["n_symbols_used"] >= MIN_SYMBOLS_USED) for a in ARM_NAMES)

    # assert_discriminator_fires: B0 must show high corr + be in a measurable failure band
    b0_in_band = (FAILRATE_LO <= agg[MIRROR_ARM]["speaker_fail_rate"] <= FAILRATE_HI) and \
                 (FAILRATE_LO <= agg[MIRROR_ARM]["listener_fail_rate"] <= FAILRATE_HI) and \
                 (not agg[MIRROR_ARM]["any_degenerate"])
    screen_fires = (corr0 >= B0_FAILMASK_CORR_MIN) and b0_in_band

    # differentiation-arm classification
    retain = [a for a in DIFF_ARMS if agg[a]["grounding_acc"] >= GROUNDING_FLOOR]
    decorr = [a for a in DIFF_ARMS if agg[a]["failmask_corr"] <= DIFF_FAILMASK_CORR_HP]
    qualified = [a for a in DIFF_ARMS
                 if (agg[a]["failmask_corr"] <= DIFF_FAILMASK_CORR_HP)
                 and (agg[a]["grounding_acc"] >= GROUNDING_FLOOR)
                 and ((corr0 - agg[a]["failmask_corr"]) >= DECORR_MARGIN_HP)]
    min_corr_retain = min((agg[a]["failmask_corr"] for a in retain), default=float("nan"))
    best_diff = min(DIFF_ARMS, key=lambda a: agg[a]["failmask_corr"])

    if not codes_ok:
        verdict = "CODE_COLLAPSE_VOID"
    elif not screen_fires:
        verdict = "SATURATION_VACUOUS_SCREEN_DID_NOT_FIRE"
    elif qualified:
        verdict = "HARD_PASS"
    elif decorr and not any(agg[a]["grounding_acc"] >= GROUNDING_FLOOR for a in decorr):
        verdict = "HARD_FAIL_DECORR_DESTROYS_GROUNDING"
    elif retain and (min_corr_retain > DIFF_FAILMASK_CORR_HF):
        verdict = "HARD_FAIL_NO_DECORRELATION"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | mode=%s | B0_mirror corr=%.3f (fires=%s spk_fail=%.3f lis_fail=%.3f) | "
        "B1_crossfit corr=%.3f ground=%.3f | B2_ema corr=%.3f ground=%.3f | "
        "B3_diffalg corr=%.3f ground=%.3f | best_diff=%s qualified=%s | codes_ok=%s ent(B0/B1/B2/B3)="
        "[%.2f,%.2f,%.2f,%.2f] | subgraph n=%d E=%d" % (
            verdict, run_mode, corr0, screen_fires,
            agg[MIRROR_ARM]["speaker_fail_rate"], agg[MIRROR_ARM]["listener_fail_rate"],
            agg["B1_crossfit"]["failmask_corr"], agg["B1_crossfit"]["grounding_acc"],
            agg["B2_ema_lag"]["failmask_corr"], agg["B2_ema_lag"]["grounding_acc"],
            agg["B3_diff_algclass"]["failmask_corr"], agg["B3_diff_algclass"]["grounding_acc"],
            best_diff, qualified, codes_ok,
            agg["B0_mirror"]["symbol_entropy_bits"], agg["B1_crossfit"]["symbol_entropy_bits"],
            agg["B2_ema_lag"]["symbol_entropy_bits"], agg["B3_diff_algclass"]["symbol_entropy_bits"],
            subgraph_meta.get("n_nodes", -1), subgraph_meta.get("n_edges", -1)))

    gates = dict(
        b0_failmask_corr=corr0, screen_fires=screen_fires, b0_in_band=b0_in_band, codes_ok=codes_ok,
        qualified_arms=qualified, retain_arms=retain, decorr_arms=decorr,
        best_diff_arm=best_diff, min_corr_retaining=min_corr_retain,
        per_arm=agg,
        bands=dict(B0_FAILMASK_CORR_MIN=B0_FAILMASK_CORR_MIN, DIFF_FAILMASK_CORR_HP=DIFF_FAILMASK_CORR_HP,
                   DECORR_MARGIN_HP=DECORR_MARGIN_HP, GROUNDING_FLOOR=GROUNDING_FLOOR,
                   DIFF_FAILMASK_CORR_HF=DIFF_FAILMASK_CORR_HF, ENTROPY_FLOOR_BITS=ENTROPY_FLOOR_BITS),
    )
    return verdict, verdict_msg, gates, agg


# ---------------------------------------------------------------------------
# Discriminator telemetry-sensitivity self-test (ALWAYS runs)
# ---------------------------------------------------------------------------
def discriminator_selftest():
    """Prove the failure_mask_corr screen is telemetry-sensitive (not analytically pinned): planted
    correlated masks -> high corr; planted independent masks -> ~0; and a shared vs independent perturbation
    MOVES the metric. Also verify a tied vs separated toy encoder reproduces high vs low corr end-to-end."""
    rng = np.random.default_rng(0)
    n = 500
    base = rng.random(n) < 0.6  # 40% failure base
    # correlated masks: both = base with a little independent flip
    a_corr = base.copy(); b_corr = base.copy()
    a_corr[rng.random(n) < 0.05] ^= True
    b_corr[rng.random(n) < 0.05] ^= True
    c_high = failure_mask_corr(a_corr, b_corr)["failmask_corr"]
    # independent masks
    a_ind = rng.random(n) < 0.4
    b_ind = rng.random(n) < 0.4
    c_low = failure_mask_corr(a_ind, b_ind)["failmask_corr"]

    # end-to-end toy: shared linear map (tied) -> high corr; independent maps -> low corr
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

    ok = (c_high >= 0.5) and (abs(c_low) < 0.2) and (tied_corr > sep_corr + 0.1)
    return bool(ok), dict(corr_planted_high=float(c_high), corr_planted_indep=float(c_low),
                          e2e_tied_corr=float(tied_corr), e2e_separated_corr=float(sep_corr))


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

    # ---- discriminator telemetry-sensitivity self-test (ALWAYS) ----
    st_ok, st_res = discriminator_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DISCRIMINATOR_SELFTEST_FAILED (not telemetry-sensitive): %s" % st_res,
            summary="discriminator selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res))
        raise SystemExit(1)

    # ---- load referent world (REUSED ConceptNet subgraph + char-trigram encoder inputs) ----
    _log("loading ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, meta = load_cn_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    n_nodes = len(node_ids)
    _log("subgraph: %s" % meta)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, n_nodes)
    Xn = neighborhood_augment(X, adj, cfg["neighbor_weight"])

    # fixed eval referents (prefer nodes with neighbors so speaker's augmented view is meaningful) + candidates
    eval_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 999)
    has_nb = np.nonzero(np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool))[0]
    n_eval = int(min(cfg["n_eval"], has_nb.shape[0]))
    eval_idx = np.sort(eval_rng.choice(has_nb, size=n_eval, replace=False))
    cand_idx = build_candidate_sets(eval_idx, n_nodes, cfg["n_dist"], eval_rng)
    _log("eval referents=%d candidate_set_size=%d" % (n_eval, 1 + cfg["n_dist"]))

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS discriminator telemetry-sensitive + subgraph/encoder pipeline exercised",
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
                              dict(seed=seed, arm=arm, metrics=r))
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

    # ARMS-MUST-DIFFER (META_RULE_AF): B0 mask-pair must differ from each differentiation arm (per seed)
    for seed in cfg["seeds"]:
        digs = {r["arm"]: r["_mask_digest"] for r in per_seed_arm if r["seed"] == seed}
        for a in DIFF_ARMS:
            if a in digs and MIRROR_ARM in digs:
                assert digs[a] != digs[MIRROR_ARM], (
                    "META_RULE_AF VIOLATION: arm %s bit-identical to %s at seed %d" % (a, MIRROR_ARM, seed))

    subgraph_meta = dict(n_nodes=meta.get("n_nodes", n_nodes), n_edges=meta.get("n_edges", len(edges)),
                         median_degree=meta.get("median_degree", -1))
    verdict, verdict_msg, gates, agg = aggregate_and_verdict(per_seed_arm, subgraph_meta, run_mode)

    # strip large arrays from persisted per-unit
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
