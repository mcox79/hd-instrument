"""Encoder-level LATENT PREDICTIVE CODING (JEPA-style) pretraining on ARC -- rep-quality lever #1.

WHY (notes/encoder_representation_lever_ranking_2026-07-29.md lever #1;
     notes/brain_foundational_component_analysis.md components 1+2):
  The founding-diagnosis objective gap: every prior encoder objective aligned to a STATIC target
  (MLM = bidirectional reconstruction of a masked token against a fixed vocab). The brain's cortex
  is FORWARD/latent-PREDICTIVE (Rao&Ballard 1999; Friston 2005). This cell builds the ENCODER-LEVEL,
  STANDALONE version of that fix (I-JEPA/V-JEPA, Assran 2023 / Bardes 2024; LeCun 2022): mask target
  SPANS and predict the TARGET-span LATENT from the CONTEXT latent via a predictor head, entirely in
  d-dim latent space -- NO token/pixel reconstruction, NO full-vocab logits. This is categorically
  OOM-free (no [B,L,vocab] tensor ANYWHERE), avoiding the v5 causal-LM OOM class.

  This is DISTINCT from the WM-coupled forward-predictive objective
  (notes/forward_predictive_objective_from_wm_state_design_2026-07-29.md): that predicts the next
  CLAUSE latent from a maintained SLOT STATE and is judged on the WM gate (MES/KD). THIS cell has
  NO working-memory module, NO slot state -- it is judged PURELY on representation quality (section 3
  of the ranking note), on a FROZEN encoder snapshot, so the two workstreams never confound.

WHAT (the run): four encoder objectives, MATCHED training budget (same tokens/steps/architecture),
  each frozen and scored on the SAME independent rep-quality battery:
    ARM_LPC     : latent-PC (JEPA) alone. EMA/stop-grad target encoder (SimSiam-style) + VICReg
                  variance-floor + covariance/decorrelation term (collapse guard, REQUIRED per lit).
    ARM_LPC_TC  : latent-PC + temporal-contiguity aux loss (Foldiak slow-feature). Wires the ALREADY
                  BANKED hdlab/temporal_trace.py primitive as a one-variable ABLATION arm.
    ARM_MLM     : the CURRENT MLM v2 encoder (imported from exp_scale_meaning_learn_arc_heldout_v2),
                  same architecture/steps/tokens -> the known-good reference (29591 baseline).
    ARM_RANDOM  : random-init encoder (same architecture, untrained) -> the floor.

REP-QUALITY BATTERY (frozen encoder; KB used READ-ONLY as a probe, NEVER a training target ->
  this is the exact distinction from the failed relObj contrastive-align-to-KB objective):
    1. graded_geometry_spearman : Spearman(encoder cosine, KB graded proximity {1-hop/2-hop/far})
                                  over held-out-NEW concepts. THE HEADLINE metric.
    2. heldout_probe_acc        : frozen closed-form ridge linear probe (lexname supersense) trained
                                  on TRAIN concepts, tested on held-out-NEW -> generalization, head
                                  can't cheat (linear, frozen).
    3. relational_auc           : per-query neighborhood AUC (reuses v2.relational_eval) -- leak-proof.
    4. rep_dispersion + collapse: per-dim concept-rep std + mean pairwise cosine (collapse witness)
                                  + training-time min target-embedding std (VICReg guard telemetry).

THE PRE-REGISTERED BANDS (deflated per lit-scan calibration; section 3 of the ranking note):
  HARD_PASS  = ARM_LPC graded_geometry beats ARM_MLM by >= +0.10 AND beats ARM_RANDOM by >= +0.15,
               in >= 1 of 2 seeds with the OTHER seed non-negative, AND held-out probe does NOT
               regress (>= MLM - 0.01), AND NO collapse (rep_std + target_std above floors).
  HARD_FAIL_NO_EFFECT = ARM_LPC ties BOTH ARM_MLM and ARM_RANDOM within +/-0.03 on graded_geometry.
  FAIL_BY_COLLAPSE    = geometry metrics move but variance collapses (rep_std < floor OR training
                        target_std < floor) -> distinct diagnosis (mechanism class NOT refuted).
  MIDDLE_BAND         = anything else (real-but-below-band gain).
  ARM_LPC_TC is reported as an ABLATION (does temporal-contiguity add over LPC alone?).

CAPACITY-RATIO WATCH (SimSiam small-scale sensitivity finding, SCAN 1): collapse risk is
  capacity/data-ratio dependent, not simply "small data fails". FULL uses d_model=512 over ~130M
  tokens; a co-scaled SMALLER variant (--co-scaled: d_model=256, n_layers=4) is pre-registered as an
  optional follow-up if FULL shows collapse or over-capacity. The training-time target_std telemetry
  is the early-warning signal.

HARD INVARIANTS (project locks): TEACHER-FREE. NO GloVe/BGE/transformer WEIGHTS/borrowed vector
  ANYWHERE (token emb + Transformer learned FROM SCRATCH; BPE vocab built FROM ARC -- all inherited
  from the imported v2 pipeline). INDUCTIVE + LEAK-PROOF (held-out placed from its own text; KB read
  only as a diagnostic probe, never a training target; v2's concept-level scrub + zero-overlap witness
  reused verbatim). ASCII-only. AI2 ARC Corpus: INTERNAL research use only.

CUDA-DEVICE-SAFE (recurring bug class this session: WM.to(device) then cpu-Generator-used-with-cuda):
  every module (online/target/predictor) .to(device); EVERY torch.rand/randint/randperm/arange on the
  RUN device (from ids.device); NO torch.Generator in the hot path (numpy default_rng only for host-side
  window-index selection into a numpy array, then .to(device)); the ONLY host<->device crossing is the
  temporal_trace numpy primitive, done via explicit .detach().cpu().numpy() out and torch.from_numpy().to(device)
  back. A tiny end-to-end cuda sanity runs in --self-test WHEN cuda is present; when absent the identical
  device-routed step runs on cpu and a static device-parity audit is recorded (see _cuda_safety_audit).

BUILD-PLAN FIXES 2026-07-30 (notes/forward_predictive_second_encoder_build_plan_2026-07-30.md sec 2):
  Fix A  data-prep progress logging inside count/collect/tokenize passes (in v2, imported) -- every
         500k lines log n_read/rate/ETA + _heartbeat.jsonl (silent->visibly-alive).
  Fix B  (single-pass merge) NOT APPLIED -- FLAGGED. The pipeline is count_pass -> build_split ->
         collect_pass: collect's held/train line routing needs the SPLIT, which needs the full COUNTS.
         A correctness-preserving merge would need to buffer >cap_mentions postings for ALL concepts
         (unbounded memory at FULL) to survive post-hoc split routing; the cap-in-corpus-order posting
         semantics cannot be reproduced from a pre-split single pass. The actual failure (silent 5h
         death) is fully addressed by Fix A (visibility) + Fix D (cache: crash never repeats data-prep)
         + Fix C (headroom gate detects a too-slow env before FULL). Kept 3 correct passes.
  Fix C  --smoke data-prep-headroom gate: measure REAL lines/sec on a 2M-line slice, project to FULL,
         REFUSE FULL if projected > DATA_PREP_TIME_CEILING_S (4h). Prints DATA_PREP_OK|DATA_PREP_TOO_SLOW.
  Fix D  torch.save the prepare_data() bundle keyed by a sha256 digest of (data-cfg subset, corpus
         mtime); main() reuses it before re-running data-prep.
  Fix 2b OOM tripwire: _assert_no_vocab_dim on the loss-path latents (last-dim==d_model, != vocab).
  Fix 2c (seed, arm) checkpoint/resume via tools/exp_checkpoint.py (crash keeps completed arms' GPU-hrs).
  Fix 2d per-arm reusable ckpt (state_dict+model_cfg+tokenizer_json) = FrozenV2Encoder-shape, for sec 3.
  Fix 4  ARM_MLM reuses V2 ckpt_seed_{7,13}.pt at FULL (no retrain); FULL mlm_steps bumped 40000->60000
         to MATCH V2 FULL so the reused MLM arm and the fresh LPC arms share the step budget (flagged).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; hash of the 4 arms' held-out rep matrices)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace + per-seed partials)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: this is a representation-geometry comparison (Spearman/probe-acc), not a noise-floor
#     estimator; discriminator floor witnessed empirically by ARM_RANDOM (~chance geometry) + no-effect band
# - baseline_in_band at run: ARM_MLM graded_geometry in (0.05,0.95) (cited 0.56-0.63); ARM_RANDOM near floor
# - discriminator survives scale: analytical (objective gap is architectural; battery NOT saturated -- MLM
#     ~0.56-0.63 leaves >0.10 headroom, RANDOM near 0 gives >0.15 headroom) + smoke previews arm ordering
# - HARD_PASS strictly above floor: >= +0.10 over MLM AND >= +0.15 over RANDOM (both well above no-effect 0.03)
# - HP_SCOPE: HP gates apply to ARM_LPC (primary). ARM_LPC_TC = ablation (reported, not gated for HP).
#     ARM_MLM/ARM_RANDOM = reference/floor (NOT gated).
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except; specific classes -> metrics)
# - calibration_check: default_ok_for_this_regime (VICReg gamma=1.0 std floor + off-diag cov are the
#     literature-standard defaults; collapse telemetry logged so the guard is observable, not assumed)
# - deterministic seeding: fixed int seeds + numpy default_rng(seed+k) + torch.manual_seed(seed); no hash()/list(set())
# - real_code_path: --self-test constructs the REAL objects (v2 BPE build + prepare_data + TinyTransformer +
#     lpc_train + mlm_train + full battery) at N~16 (SELFTEST_CFG IS the real pipeline at tiny scale)
# - progress_logging: print_flush_true (train step logs flush=True) + _heartbeat.jsonl (timeout_s >> 1800)
# - device-agnostic: cuda+AMP on the GPU box, cpu for local self-test; no hard device assumption
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
    get_output_dir, record_gate, write_metrics, write_partial, aggregate_partials,
)
# Reuse the PROVEN v2 data pipeline + encoder + MLM baseline verbatim (guarantees matched data /
# architecture across arms; the ONLY new machinery here is the LPC objective + the rep battery).
from experiments.exp_scale_meaning_learn_arc_heldout_v2 import (  # noqa: E402
    TinyTransformer, mlm_train, load_concept_universe, prepare_data, count_pass,
    encode_concept_text_reps, relational_eval, ARC_CORPUS,
    FULL_CFG as V2_FULL_CFG,  # noqa: F401  (to audit MLM-reuse budget parity)
    RAW_ARM as V2_RAW_ARM,  # noqa: F401  (imported to assert module wiring in self-test)
)
from hdlab.temporal_trace import TemporalTrace  # noqa: E402  (banked Foldiak slow-feature primitive)

# (seed, arm) per-unit checkpoint/resume (CLAUDE.md mandate; Fix 2c). Same path convention every cell
# uses: tools/ on sys.path, then `import exp_checkpoint`.
sys.path.insert(0, os.path.join(_REPO, "tools"))
import exp_checkpoint as ckpt  # noqa: E402

ANCHOR_NAME = "encoder_latent_pc_arc_v1"

# Reuse of V2's already-trained MLM checkpoints for ARM_MLM at FULL (section 4 cost fix; Fix 4): the
# MLM baseline arm is architecturally + data + BUDGET identical to V2's FULL MLM (see FULL_CFG note
# below), so we load V2's ckpt_seed_{7,13}.pt instead of retraining ~2 GPU-hr/seed. Graceful fallback
# to a fresh matched-budget MLM train when a seed's ckpt is absent (smoke/self-test/other seeds).
V2_CKPT_DIR = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2")

# Data-prep-headroom smoke gate (Fix C) + resumable data-prep cache (Fix D).
DATA_PREP_SMOKE_LINES = 2_000_000        # real-corpus probe slice (measure lines/sec, extrapolate)
DATA_PREP_TIME_CEILING_S = 14400         # 4h ceiling on projected FULL data-prep (fail loud above)
N_DATA_PASSES = 3                        # count_pass + collect_pass + tokenize_train_stream (see Fix B flag)
_DATA_CFG_KEYS = ("min_deg", "cap_eval_concepts", "heldout_count", "min_mentions_eval", "max_lines",
                  "dedup_cap", "bpe_sample_lines", "cap_mentions", "vocab", "max_len",
                  "train_token_budget", "max_shards", "n_freq_buckets")

# Arms
ARM_LPC = "ARM_LPC"                # latent-PC (JEPA) alone -- PRIMARY
ARM_LPC_TC = "ARM_LPC_TC"         # latent-PC + temporal-contiguity -- ABLATION
ARM_MLM = "ARM_MLM"               # current MLM baseline (matched budget) -- reference
ARM_RANDOM = "ARM_RANDOM"         # random-init -- floor
ARMS = [ARM_LPC, ARM_LPC_TC, ARM_MLM, ARM_RANDOM]
OBJECTIVE_ARMS = [ARM_LPC, ARM_LPC_TC]   # arms that carry training-time collapse telemetry

# Pre-reg bands (headline = graded_geometry_spearman; deflated per lit-scan calibration)
HP_GG_OVER_MLM = 0.10            # ARM_LPC - ARM_MLM graded-geometry (break the reference)
HP_GG_OVER_RANDOM = 0.15         # ARM_LPC - ARM_RANDOM (learning is real, not vacuous)
PROBE_NOREGRESS_EPS = 0.01       # held-out probe must not regress below MLM by more than this
NO_EFFECT_EPS = 0.03             # |LPC - MLM| and |LPC - RANDOM| both under this = FAIL_BY_NO_EFFECT
COLLAPSE_REP_STD_FLOOR = 0.02    # frozen concept-rep per-dim std floor (below = representational collapse)
COLLAPSE_TARGET_STD_FLOOR = 0.05  # training-time target-embedding std floor (VICReg guard must hold)
MIN_QUERY_TASKS = 40             # power floor for the geometry/probe evals to be trustworthy

# LPC / VICReg defaults (literature-standard; calibration_check=default_ok_for_this_regime)
# VICReg (Bardes 2022): variance hinge gamma=1.0, covariance off-diag decorrelation.
# EMA target momentum 0.996 (BYOL/I-JEPA range). Predictor = 2-layer MLP (I-JEPA predictor is small).

# ---------------------------------------------------------------------------
# Config profiles (mirror v2's keys so prepare_data works verbatim; add LPC keys)
# ---------------------------------------------------------------------------
_LPC_COMMON = dict(
    lpc_mask_frac=0.20, lpc_ema_m=0.996, lpc_var_coef=1.0, lpc_cov_coef=0.04,
    lpc_pred_hidden_mult=2, lpc_tc_coef=0.5, lpc_tc_alpha=0.1,
)

SELFTEST_CFG = dict(
    run_mode="selftest", seeds=[7],
    min_deg=2, cap_eval_concepts=1500, heldout_count=60, min_mentions_eval=1,
    max_lines=120000, dedup_cap=160000, bpe_sample_lines=40000, cap_mentions=6,
    vocab=512, max_len=24, train_token_budget=600000, max_shards=6,
    d_model=32, n_layers=1, n_heads=2, ffn_mult=2,
    mlm_steps=40, mlm_batch=8, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=64, n_freq_buckets=4,
    **_LPC_COMMON,
)
SMOKE_CFG = dict(
    run_mode="smoke", seeds=[7],
    min_deg=2, cap_eval_concepts=2500, heldout_count=250, min_mentions_eval=2,
    max_lines=150000, dedup_cap=200000, bpe_sample_lines=80000, cap_mentions=16,
    vocab=4096, max_len=48, train_token_budget=4000000, max_shards=6,
    d_model=128, n_layers=2, n_heads=4, ffn_mult=2,
    mlm_steps=400, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3,
    encode_batch=256, n_freq_buckets=5,
    **_LPC_COMMON,
)
FULL_CFG = dict(
    run_mode="full", seeds=[7, 13],
    min_deg=2, cap_eval_concepts=None, heldout_count=800, min_mentions_eval=20,
    max_lines=10000000, dedup_cap=6000000, bpe_sample_lines=400000, cap_mentions=128,
    vocab=16000, max_len=128, train_token_budget=130000000, max_shards=16,
    d_model=512, n_layers=6, n_heads=8, ffn_mult=4,
    # mlm_steps=60000 MATCHES V2 FULL (exp_scale_meaning_learn_arc_heldout_v2.FULL_CFG.mlm_steps=60000).
    # This is the ONE scientific-parameter change vs the cell's prior 40000, made so ARM_MLM (now REUSED
    # from V2's 60000-step ckpt, Fix 4) and the fresh-trained ARM_LPC/ARM_LPC_TC share an IDENTICAL step
    # budget -> the one-variable (objective) comparison stays budget-matched. Flagged for Director
    # sign-off. A runtime parity assert (see _load_mlm_baseline_encoder use) guards against silent drift.
    mlm_steps=60000, mlm_batch=128, mlm_mask_frac=0.15, mlm_lr=3e-4,
    encode_batch=256, n_freq_buckets=8,
    **_LPC_COMMON,
)
# Co-scaled follow-up variant (capacity-ratio watch): smaller encoder over the same ~130M tokens.
FULL_COSCALED_OVERRIDE = dict(d_model=256, n_layers=4, n_heads=8, ffn_mult=4)


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics / logging / heartbeat
# ---------------------------------------------------------------------------
def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node(),
                  cuda=bool(torch.cuda.is_available()))
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
                elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=datetime.now(timezone.utc).isoformat(),
               unit_idx=int(unit_idx), total_units=int(total_units),
               elapsed_s=float(elapsed_s))
    if extra:
        row["extra"] = extra
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Latent predictor (I-JEPA-style small MLP; predicts target latent from context latent)
# ---------------------------------------------------------------------------
def _assert_no_vocab_dim(tensors, d_model, vocab_size):
    """OOM regression tripwire (Fix 2b): the latent-PC loss path is bounded by d_model and must NEVER
    materialize a vocab-sized [.,vocab] tensor (the v5 causal-LM OOM class). Verification-only guard."""
    for t in tensors:
        last = int(t.shape[-1])
        assert last == d_model, ("OOM_TRIPWIRE: loss-path latent last-dim=%d != d_model=%d" % (last, d_model))
        assert last != vocab_size, ("OOM_TRIPWIRE: loss-path tensor has vocab-sized last-dim=%d" % last)


class LatentPredictor(torch.nn.Module):
    def __init__(self, d_model, hidden_mult):
        super().__init__()
        h = max(d_model, hidden_mult * d_model)
        self.net = torch.nn.Sequential(
            torch.nn.Linear(d_model, h), torch.nn.GELU(), torch.nn.Linear(h, d_model))

    def forward(self, z):  # [T, d] -> [T, d]
        return self.net(z)


# ---------------------------------------------------------------------------
# VICReg collapse-guard terms (computed in float32; safe under AMP)
# ---------------------------------------------------------------------------
def _vicreg_variance(z, gamma=1.0, eps=1e-4):
    """Hinge on per-dim std >= gamma. z: [N, d] float32. Returns scalar tensor."""
    if z.shape[0] < 2:
        return z.new_zeros(())
    std = torch.sqrt(z.var(dim=0, unbiased=False) + eps)
    return torch.relu(gamma - std).mean()


def _vicreg_covariance(z):
    """Sum of squared off-diagonal covariances / d. z: [N, d] float32. Returns scalar tensor."""
    n, d = z.shape
    if n < 2:
        return z.new_zeros(())
    zc = z - z.mean(dim=0, keepdim=True)
    cov = (zc.T @ zc) / (n - 1)
    off = cov - torch.diag(torch.diag(cov))
    return (off.pow(2).sum()) / d


# ---------------------------------------------------------------------------
# Latent-predictive-coding (JEPA) training. CUDA-device-safe throughout.
# ---------------------------------------------------------------------------
def lpc_train(stream, spec, cfg, device, seed, out_dir, hb_total, temporal_contiguity=False):
    """Train the online encoder by masked-span latent prediction against an EMA target encoder.

    Collapse guard = EMA/stop-grad target (SimSiam-style) + VICReg variance floor + covariance term.
    Optional temporal-contiguity aux loss wires hdlab.temporal_trace (Foldiak slow-feature).
    Returns (online_encoder: TinyTransformer, diag: dict). OOM-free: no vocab-sized tensor anywhere.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    max_len = cfg["max_len"]

    def _mk():
        return TinyTransformer(spec["size"], max_len, cfg["d_model"], cfg["n_layers"],
                               cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)

    online = _mk()
    target = _mk()
    target.load_state_dict(online.state_dict())
    for p in target.parameters():
        p.requires_grad_(False)
    target.eval()
    predictor = LatentPredictor(cfg["d_model"], cfg["lpc_pred_hidden_mult"]).to(device)

    params = list(online.parameters()) + list(predictor.parameters())
    n_enc_params = sum(p.numel() for p in online.parameters())
    _log("  LPC%s online-encoder params=%.2fM predictor=%.3fM device=%s d=%d L=%d"
         % ("+TC" if temporal_contiguity else "", n_enc_params / 1e6,
            sum(p.numel() for p in predictor.parameters()) / 1e6,
            device.type, cfg["d_model"], cfg["n_layers"]))
    opt = torch.optim.AdamW(params, lr=cfg["mlm_lr"])
    use_amp = (device.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    n_win = stream.shape[0] // max_len
    if n_win < 4:
        raise RuntimeError("train stream too short: %d tokens, %d windows" % (stream.shape[0], n_win))
    windows = stream[:n_win * max_len].reshape(n_win, max_len)
    g = np.random.default_rng(seed + 5)
    bs = min(cfg["mlm_batch"], n_win)
    steps = cfg["mlm_steps"]                     # matched budget: LPC steps == MLM steps
    mask_frac = cfg["lpc_mask_frac"]
    ema_m = cfg["lpc_ema_m"]
    var_coef, cov_coef = cfg["lpc_var_coef"], cfg["lpc_cov_coef"]
    tc_coef = cfg["lpc_tc_coef"] if temporal_contiguity else 0.0
    mask_id, pad_id = spec["mask"], spec["pad"]
    trace = TemporalTrace(alpha=cfg["lpc_tc_alpha"], n_dim=cfg["d_model"]) if temporal_contiguity else None

    log_every = max(1, steps // 10)
    pred_hist, tgtstd_hist, tc_hist = [], [], []
    t0 = time.perf_counter()
    online.train()
    predictor.train()
    for step in range(steps):
        if temporal_contiguity:
            # contiguous run of windows (in corpus/stream order) = a temporally-contiguous pseudo-document
            start = int(g.integers(0, max(1, n_win - bs)))
            sel = (np.arange(start, start + bs) % n_win)
            trace.reset()                         # document-boundary reset (scope-honest: designer-supplied contiguity)
        else:
            sel = g.integers(0, n_win, size=bs)
        ids = torch.from_numpy(windows[sel].astype(np.int64)).to(device)
        B, L = ids.shape
        pad = (ids == pad_id)
        span = max(1, int(round(mask_frac * L)))
        # per-row contiguous target span; ALL device tensors (cuda-safe: no torch.Generator, no cpu tensor)
        starts = torch.randint(0, max(1, L - span + 1), (B,), device=device)
        ar = torch.arange(L, device=device).unsqueeze(0)
        tgt_mask = (ar >= starts.unsqueeze(1)) & (ar < (starts.unsqueeze(1) + span))
        tgt_mask = tgt_mask & (~pad)
        none_rows = ~tgt_mask.any(dim=1)
        if bool(none_rows.any()):
            first_nonpad = (~pad).float().argmax(dim=1)
            tgt_mask[none_rows, first_nonpad[none_rows]] = True

        ctx_ids = ids.clone()
        ctx_ids[tgt_mask] = mask_id

        opt.zero_grad(set_to_none=True)
        with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
            h_ctx, _ = online._contextual(ctx_ids)          # [B,L,d]
            with torch.no_grad():
                h_tgt, _ = target._contextual(ids)          # [B,L,d] stop-grad EMA target
            zc = h_ctx[tgt_mask]                             # [T,d] context latents at target positions
            zt = h_tgt[tgt_mask].detach()                   # [T,d] target latents (stop-grad)
            zp = predictor(zc)                              # [T,d] predicted target latents
            if step == 0:
                _assert_no_vocab_dim((zc, zt, zp), cfg["d_model"], spec["size"])
            pred_loss = torch.nn.functional.smooth_l1_loss(zp, zt)
            zp32, zt32 = zp.float(), zt.float()
            var_loss = _vicreg_variance(zp32) + _vicreg_variance(zt32)
            cov_loss = _vicreg_covariance(zp32) + _vicreg_covariance(zt32)
            loss = pred_loss + var_coef * var_loss + cov_coef * cov_loss

            tc_val = 0.0
            if temporal_contiguity:
                pooled = online.pooled(ids)                 # [B,d] grad-carrying
                pooled_np = pooled.detach().cpu().numpy()   # explicit host crossing (cuda-safe)
                tc_targets, valid = [], []
                for b in range(B):
                    prev = trace.state                      # slow trace of PRIOR windows (None on step 0)
                    if prev is not None:
                        tc_targets.append(prev)
                        valid.append(b)
                    trace.update(pooled_np[b])
                if valid:
                    tgt_t = torch.from_numpy(np.stack(tc_targets)).to(device)   # back to run device
                    cur = pooled[valid]
                    tc_loss = torch.nn.functional.smooth_l1_loss(cur, tgt_t)
                    loss = loss + tc_coef * tc_loss
                    tc_val = float(tc_loss.detach())

        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite LPC loss step=%d seed=%d (pred=%.4f)"
                                     % (step, seed, float(pred_loss.detach())))
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        # EMA target update (no_grad; buffers copied so LayerNorm running-state tracks)
        with torch.no_grad():
            for pt, po in zip(target.parameters(), online.parameters()):
                pt.mul_(ema_m).add_(po.detach(), alpha=1.0 - ema_m)
            for bt, bo in zip(target.buffers(), online.buffers()):
                bt.copy_(bo)

        tgt_std = float(zt32.std().detach())
        pred_hist.append(float(pred_loss.detach()))
        tgtstd_hist.append(tgt_std)
        tc_hist.append(tc_val)
        if (step % log_every == 0) or (step == steps - 1):
            el = time.perf_counter() - t0
            _log("  LPC%s seed=%d step=%d/%d pred=%.4f var=%.4f cov=%.4f tc=%.4f tgt_std=%.4f (%.1fs)"
                 % ("+TC" if temporal_contiguity else "", seed, step, steps,
                    float(pred_loss.detach()), float(var_loss.detach()), float(cov_loss.detach()),
                    tc_val, tgt_std, el))
            _heartbeat(out_dir, step, hb_total, el,
                       extra={"pred_loss": float(pred_loss.detach()), "tgt_std": tgt_std, "seed": seed})

    online.eval()
    k = max(1, len(pred_hist) // 5)
    diag = dict(
        init_pred_loss=float(np.mean(pred_hist[:k])),
        final_pred_loss=float(np.mean(pred_hist[-k:])),
        min_target_std=float(np.min(tgtstd_hist)) if tgtstd_hist else 0.0,
        final_target_std=float(np.mean(tgtstd_hist[-k:])) if tgtstd_hist else 0.0,
        mean_tc_loss=float(np.mean(tc_hist)) if temporal_contiguity else None,
        n_steps=steps,
    )
    return online, diag


# ---------------------------------------------------------------------------
# Rep-quality battery (all on FROZEN concept reps; KB read-only)
# ---------------------------------------------------------------------------
def _rankdata(x):
    """Average ranks (tie-corrected)."""
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=np.float64)
    sx = x[order]
    i = 0
    n = len(x)
    while i < n:
        j = i
        while j + 1 < n and sx[j + 1] == sx[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def _spearman(a, b):
    if len(a) < 3:
        return None
    ra, rb = _rankdata(np.asarray(a, dtype=np.float64)), _rankdata(np.asarray(b, dtype=np.float64))
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    if denom < 1e-12:
        return None
    return float((ra * rb).sum() / denom)


def graded_geometry_eval(reps, split, adj, seed, n_far=8, max_q=None):
    """Spearman(encoder cosine, KB graded proximity {1-hop=3, 2-hop=2, far=1}) over held-out concepts.
    Leak-proof: held-out reps carry ZERO relational input; KB proximity is a READ-ONLY probe."""
    held = split["held_idx"]
    train_set = set(int(x) for x in split["train_eval_idx"].tolist())
    have = np.linalg.norm(reps, axis=1) > 1e-8
    rng = np.random.default_rng(seed + 41)
    train_pool = sorted(i for i in train_set if have[i])
    if len(train_pool) < 20:
        return None, 0
    train_pool_arr = np.array(train_pool, dtype=np.int64)
    sp = []
    q_list = [int(h) for h in held.tolist() if have[h]]
    if max_q is not None and len(q_list) > max_q:
        q_list = sorted(rng.choice(np.array(q_list), size=max_q, replace=False).tolist())
    for h in q_list:
        nb1 = sorted(j for j in adj[h] if j in train_set and have[j] and j != h)
        if len(nb1) < 1:
            continue
        nb2set = set()
        for j in nb1:
            nb2set |= adj[j]
        nb1set = set(nb1)
        nb2 = sorted(j for j in nb2set if j in train_set and have[j] and j != h and j not in nb1set)
        excl = nb1set | set(nb2) | set(adj[h]) | {h}
        far_cands = [j for j in train_pool if j not in excl]
        if not far_cands or (len(nb1) + len(nb2)) < 2:
            continue
        take2 = nb2[:max(2, len(nb1))]
        n_far_take = min(n_far, len(far_cands))
        far = rng.choice(np.array(far_cands), size=n_far_take, replace=False).tolist()
        cand = list(nb1) + list(take2) + list(far)
        prox = ([3] * len(nb1)) + ([2] * len(take2)) + ([1] * len(far))
        if len(set(prox)) < 2 or len(cand) < 4:
            continue
        cos = reps[h] @ reps[np.array(cand, dtype=np.int64)].T
        s = _spearman(cos, np.array(prox, dtype=np.float64))
        if s is not None:
            sp.append(s)
    return (float(np.mean(sp)) if sp else None), len(sp)


def heldout_probe_eval(reps, universe, split, ridge=1.0):
    """Frozen closed-form ridge linear probe: lexname (supersense) trained on TRAIN concepts,
    tested on held-out-NEW. Head is linear + frozen -> gains attributable to rep quality only."""
    lex = universe["lexnames"]
    have = np.linalg.norm(reps, axis=1) > 1e-8
    tr = [int(i) for i in split["train_eval_idx"].tolist() if have[i] and lex[i] is not None]
    if len(tr) < 30:
        return None, 0
    classes = sorted(set(lex[i] for i in tr))
    cls_idx = {c: k for k, c in enumerate(classes)}
    if len(classes) < 2:
        return None, 0
    he = [int(i) for i in split["held_idx"].tolist()
          if have[i] and lex[i] is not None and lex[i] in cls_idx]
    if len(he) < 10:
        return None, 0
    Xtr = reps[np.array(tr, dtype=np.int64)].astype(np.float64)
    Ytr = np.zeros((len(tr), len(classes)), dtype=np.float64)
    for r, i in enumerate(tr):
        Ytr[r, cls_idx[lex[i]]] = 1.0
    d = Xtr.shape[1]
    W = np.linalg.solve(Xtr.T @ Xtr + ridge * np.eye(d), Xtr.T @ Ytr)   # closed-form ridge
    Xhe = reps[np.array(he, dtype=np.int64)].astype(np.float64)
    pred = np.argmax(Xhe @ W, axis=1)
    true = np.array([cls_idx[lex[i]] for i in he], dtype=np.int64)
    return float((pred == true).mean()), len(he)


def collapse_diag(reps, split, seed, max_pairs=4000):
    """Frozen-rep collapse witness: per-dim std across held-out concepts + mean pairwise abs cosine."""
    held = split["held_idx"]
    have = np.linalg.norm(reps, axis=1) > 1e-8
    idx = np.array([int(h) for h in held.tolist() if have[h]], dtype=np.int64)
    if idx.shape[0] < 3:
        return dict(rep_std=None, mean_pairwise_cos=None, n=int(idx.shape[0]))
    R = reps[idx]
    rep_std = float(R.std(axis=0).mean())
    rng = np.random.default_rng(seed + 61)
    n = R.shape[0]
    m = min(max_pairs, n * (n - 1) // 2)
    a = rng.integers(0, n, size=m)
    b = rng.integers(0, n, size=m)
    ok = a != b
    cos = np.abs((R[a[ok]] * R[b[ok]]).sum(axis=1))
    return dict(rep_std=rep_std, mean_pairwise_cos=float(cos.mean()), n=int(n))


# ---------------------------------------------------------------------------
# ARMS-MUST-DIFFER (META_RULE_AF)
# ---------------------------------------------------------------------------
def _arms_differ(rep_dict):
    dig = {}
    for name, arr in rep_dict.items():
        dig[name] = hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
    names = sorted(dig)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            assert dig[names[a]] != dig[names[b]], \
                "META_RULE_AF VIOLATION: %s and %s bit-identical" % (names[a], names[b])
    return dig


# ---------------------------------------------------------------------------
# MLM-baseline reuse (Fix 4): reuse V2's already-trained ckpt instead of retraining ARM_MLM.
# Returns (model, tok, spec, source) or (None,...,"fresh") when the seed's ckpt is absent.
# ---------------------------------------------------------------------------
def _load_mlm_baseline_encoder(seed, device):
    ckpt_path = os.path.join(V2_CKPT_DIR, "ckpt_seed_%d.pt" % seed)
    if not os.path.exists(ckpt_path):
        return None, None, None, "fresh_no_v2_ckpt"
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    mc = ck["model_cfg"]
    model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                            mc["n_heads"], mc["ffn_mult"], mc["pad_id"]).to(device)
    model.load_state_dict(ck["state_dict"])
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    from tokenizers import Tokenizer
    tok = Tokenizer.from_str(ck["tokenizer_json"])
    return model, tok, ck["spec"], "reused_v2_ckpt"


# ---------------------------------------------------------------------------
# Per-arm reusable checkpoint (Fix 2d): bit-identical dict shape to what FrozenV2Encoder loads
# (state_dict + model_cfg + tokenizer_json), so the downstream binding-compare cell needs zero new
# loader code -- only a path change. Saved for the arms section 3 consumes (ARM_LPC, ARM_MLM) plus
# ARM_LPC_TC for completeness (ARM_RANDOM skipped -- untrained, nothing to reuse).
# ---------------------------------------------------------------------------
def _save_arm_ckpt(out_dir, seed, arm, model, tok, spec, cfg):
    if arm == ARM_RANDOM:
        return None
    try:
        ck = dict(
            state_dict={k: v.detach().cpu() for k, v in model.state_dict().items()},
            spec=spec,
            model_cfg=dict(vocab=int(spec["size"]), max_len=int(cfg["max_len"]),
                           d_model=int(cfg["d_model"]), n_layers=int(cfg["n_layers"]),
                           n_heads=int(cfg["n_heads"]), ffn_mult=int(cfg["ffn_mult"]),
                           pad_id=int(spec["pad"])),
            tokenizer_json=tok.to_str(),
            seed=int(seed), run_mode=cfg["run_mode"], anchor=ANCHOR_NAME, arm=arm)
        path = os.path.join(out_dir, "ckpt_seed_%d_%s.pt" % (seed, arm))
        tmp = path + ".tmp"
        torch.save(ck, tmp)
        os.replace(tmp, path)
    except (OSError, RuntimeError, ValueError) as e:
        _log("  WARN arm-ckpt save failed (%s/%s): %s" % (arm, seed, str(e)[:200]))
        return None
    try:
        return os.path.relpath(path, _REPO)          # repo-relative in production
    except ValueError:
        return os.path.abspath(path)                 # cross-drive (self-test temp on another mount)


# ---------------------------------------------------------------------------
# Data-prep bundle cache (Fix D): torch.save the seed-independent prepare_data() bundle keyed by a hash
# of (data-affecting cfg subset, corpus mtime) so a crash DURING arm training does not repeat the
# ~2-3h data-prep on resume. Tokenizer serialized via to_str()/from_str() (numpy/python-native rest).
# ---------------------------------------------------------------------------
def _dataprep_cache_key(cfg):
    corpus_mtime = os.path.getmtime(ARC_CORPUS) if os.path.exists(ARC_CORPUS) else 0.0
    payload = dict(cfg_subset={k: cfg.get(k) for k in _DATA_CFG_KEYS},
                   corpus_mtime=round(float(corpus_mtime), 3), run_mode=cfg["run_mode"])
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _bundle_cache_path(out_dir, cfg):
    return os.path.join(out_dir, "dataprep_bundle_%s.pt" % _dataprep_cache_key(cfg))


def _save_bundle_cache(path, bundle):
    b = dict(bundle)
    b["tok_json"] = b["tok"].to_str()
    b.pop("tok", None)
    tmp = path + ".tmp"
    torch.save(b, tmp)
    os.replace(tmp, path)


def _load_bundle_cache(path):
    from tokenizers import Tokenizer
    b = torch.load(path, map_location="cpu", weights_only=False)
    b["tok"] = Tokenizer.from_str(b.pop("tok_json"))
    return b


# ---------------------------------------------------------------------------
# Data-prep-headroom gate (Fix C): measure the REAL per-line rate on a bounded corpus slice, extrapolate
# to the full data-prep cost, and REFUSE FULL if the projected ETA exceeds the ceiling. Fails loud.
# ---------------------------------------------------------------------------
def _headroom_projection(measured_rate, full_lines, n_passes, ceiling_s):
    proj = ((full_lines / measured_rate) * n_passes) if measured_rate > 0 else float("inf")
    return dict(measured_lines_per_sec=float(measured_rate), projected_full_dataprep_s=float(proj),
                n_passes=int(n_passes), ceiling_s=int(ceiling_s), full_lines=int(full_lines),
                verdict=("DATA_PREP_OK" if proj <= ceiling_s else "DATA_PREP_TOO_SLOW"))


def _data_prep_headroom(out_dir):
    """Run count_pass over DATA_PREP_SMOKE_LINES of the REAL corpus at FULL cfg, measure lines/sec, and
    project the full data-prep ETA (n_passes single-line passes over FULL max_lines)."""
    full_uni = load_concept_universe(FULL_CFG)
    probe = dict(FULL_CFG)
    probe["max_lines"] = DATA_PREP_SMOKE_LINES
    _log("data-prep headroom probe: count_pass over %d REAL corpus lines (FULL cfg)..."
         % DATA_PREP_SMOKE_LINES)
    t0 = time.perf_counter()
    _counts, stats = count_pass(probe, full_uni["surf_to_idx"], out_dir=out_dir)
    el = time.perf_counter() - t0
    rate = (stats["n_read"] / el) if el > 0 else 0.0
    full_lines = FULL_CFG["max_lines"] or stats["n_read"]
    h = _headroom_projection(rate, full_lines, N_DATA_PASSES, DATA_PREP_TIME_CEILING_S)
    h.update(probe_lines=int(stats["n_read"]), probe_elapsed_s=float(el))
    return h


# ---------------------------------------------------------------------------
# Encoder builders per arm (each returns a frozen TinyTransformer + training diag + optional tok/spec
# override for the reused-MLM arm, which must encode with ITS OWN ckpt tokenizer).
# ---------------------------------------------------------------------------
def _build_encoder(arm, cfg, spec, device, seed, stream, out_dir, hb_total):
    if arm == ARM_MLM:
        if cfg["run_mode"] == "full":
            m, mtok, mspec, src = _load_mlm_baseline_encoder(seed, device)
            if m is not None:
                _log("  ARM_MLM: reused V2 ckpt_seed_%d.pt (no retrain; budget-matched at 60000 steps)"
                     % seed)
                return m, dict(reused_v2_ckpt=True, baseline_source=src), mtok, mspec
            _log("  ARM_MLM: V2 ckpt_seed_%d.pt ABSENT -> fresh matched-budget MLM train (fallback)"
                 % seed)
        model, final_loss = mlm_train(stream, spec, cfg, device, seed, out_dir, hb_total)
        return model, dict(final_mlm_loss=float(final_loss), reused_v2_ckpt=False), None, None
    if arm == ARM_RANDOM:
        torch.manual_seed(seed + 999)
        model = TinyTransformer(spec["size"], cfg["max_len"], cfg["d_model"], cfg["n_layers"],
                                cfg["n_heads"], cfg["ffn_mult"], spec["pad"]).to(device)
        model.eval()
        return model, dict(untrained=True), None, None
    if arm == ARM_LPC:
        m, d = lpc_train(stream, spec, cfg, device, seed, out_dir, hb_total, temporal_contiguity=False)
        return m, d, None, None
    if arm == ARM_LPC_TC:
        m, d = lpc_train(stream, spec, cfg, device, seed, out_dir, hb_total, temporal_contiguity=True)
        return m, d, None, None
    raise ValueError("unknown arm %s" % arm)


def run_one_seed(seed, cfg, device, out_dir, universe, bundle):
    t0 = time.perf_counter()
    split = bundle["split"]
    counts = bundle["counts"]
    tok = bundle["tok"]
    spec = bundle["spec"]
    postings = bundle["postings"]
    ground = bundle["ground"]           # noqa: F841  (grounding not scored here; encoder-only battery)
    adj, deg, n_shards = bundle["adj"], bundle["deg"], bundle["n_shards"]
    hb_total = cfg["mlm_steps"] * len(OBJECTIVE_ARMS)

    arm_results = {}
    arm_digests = {}
    ckpt_paths = {}
    # (seed, arm) unit checkpoint/resume (Fix 2c): a crash in a later arm keeps every already-complete
    # arm's ~2.8-3.2 GPU-hr of work. Resume skips units already recorded in units.jsonl.
    done = ckpt.completed_units(out_dir)
    prior = ckpt.load_units(out_dir) if done else {}
    for arm in ARMS:
        key = ckpt.unit_key(seed, arm)
        if key in done:
            u = prior[key]                            # load_units already unwraps to the result dict
            arm_results[arm] = u["arm_result"]
            arm_digests[arm] = u["held_rep_digest"]
            ckpt_paths[arm] = u.get("ckpt_path")
            _log("seed=%d ARM=%s: RESUMED (already in units.jsonl; skip retrain)" % (seed, arm))
            continue
        _log("seed=%d ARM=%s: build encoder..." % (seed, arm))
        model, tdiag, enc_tok, enc_spec = _build_encoder(
            arm, cfg, spec, device, seed, bundle["stream"], out_dir, hb_total)
        use_tok = enc_tok if enc_tok is not None else tok
        use_spec = enc_spec if enc_spec is not None else spec
        # persist the reusable encoder ckpt BEFORE the (potentially long) rep battery, so a crash mid-
        # battery still leaves the trained weights on disk (Fix 2d).
        ckpt_paths[arm] = _save_arm_ckpt(out_dir, seed, arm, model, use_tok, use_spec, cfg)
        _log("seed=%d ARM=%s: encode concept reps..." % (seed, arm))
        reps, mrep_cnt = encode_concept_text_reps(model, use_tok, postings, cfg, device, use_spec)
        held = reps[split["held_idx"]].copy()
        digest = hashlib.sha256(np.ascontiguousarray(held).tobytes()).hexdigest()

        gg, gg_nq = graded_geometry_eval(reps, split, adj, seed, max_q=cfg.get("gg_max_q"))
        probe, probe_nq = heldout_probe_eval(reps, universe, split)
        rel = relational_eval(ground, reps, counts, universe, split, adj, deg, n_shards, seed, w_star=1.0)
        rel_auc = rel.get("ARM_RAW_TEXT") if rel else None   # text-alone neighborhood AUC = THIS encoder
        rel_nq = rel.get("_n_query", 0) if rel else 0
        cdiag = collapse_diag(reps, split, seed)

        arm_results[arm] = dict(
            graded_geometry=gg, graded_geometry_nq=gg_nq,
            heldout_probe=probe, heldout_probe_nq=probe_nq,
            relational_auc=rel_auc, relational_nq=rel_nq,
            rep_std=cdiag["rep_std"], mean_pairwise_cos=cdiag["mean_pairwise_cos"],
            mention_rep_coverage=float((mrep_cnt[split["held_idx"]] > 0).mean()),
            train_diag=tdiag,
        )
        arm_digests[arm] = digest
        ckpt.record_unit(out_dir, key, dict(arm_result=arm_results[arm], held_rep_digest=digest,
                                             ckpt_path=ckpt_paths[arm]))
        _log("seed=%d ARM=%s: gg=%s probe=%s rel=%s rep_std=%s (gg_nq=%d)"
             % (seed, arm, _fmt(gg), _fmt(probe), _fmt(rel_auc), _fmt(cdiag["rep_std"]), gg_nq))

    # ARMS-MUST-DIFFER (META_RULE_AF) from the recorded per-arm held-rep digests (resume-safe).
    _names = sorted(arm_digests)
    for _i in range(len(_names)):
        for _j in range(_i + 1, len(_names)):
            assert arm_digests[_names[_i]] != arm_digests[_names[_j]], \
                "META_RULE_AF VIOLATION: %s and %s bit-identical" % (_names[_i], _names[_j])
    return dict(seed=int(seed), run_mode=cfg["run_mode"], elapsed_s=float(time.perf_counter() - t0),
                ckpt_paths=ckpt_paths,
                arms=arm_results, arm_digests=arm_digests,
                matched_budget=dict(steps=cfg["mlm_steps"], batch=cfg["mlm_batch"],
                                    train_token_budget=cfg["train_token_budget"],
                                    d_model=cfg["d_model"], n_layers=cfg["n_layers"],
                                    matched_encoder_params=True,
                                    note="LPC adds a small predictor + non-trained EMA target; "
                                         "base-encoder architecture/params/steps/tokens matched across arms"))


def _fmt(x):
    return ("%.4f" % x) if isinstance(x, float) else str(x)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def build_verdict(per_seed, cfg):
    seeds = sorted(per_seed.keys(), key=lambda k: int(k))

    def by_seed(arm, key):
        out = []
        for k in seeds:
            a = per_seed[k].get("arms", {}).get(arm, {})
            out.append(a.get(key))
        return out

    def mean(v):
        vv = [x for x in v if x is not None]
        return float(np.mean(vv)) if vv else None

    gg = {a: by_seed(a, "graded_geometry") for a in ARMS}
    probe = {a: by_seed(a, "heldout_probe") for a in ARMS}
    rel = {a: by_seed(a, "relational_auc") for a in ARMS}
    rep_std = {a: by_seed(a, "rep_std") for a in ARMS}
    min_tgt_std = {a: [((per_seed[k]["arms"][a].get("train_diag") or {}).get("min_target_std"))
                       for k in seeds] for a in OBJECTIVE_ARMS}

    m_gg = {a: mean(gg[a]) for a in ARMS}
    m_probe = {a: mean(probe[a]) for a in ARMS}
    m_rel = {a: mean(rel[a]) for a in ARMS}
    m_repstd = {a: mean(rep_std[a]) for a in ARMS}

    # per-seed deltas for the "1 of 2 seeds with other non-negative" rule (ARM_LPC primary)
    def deltas(arm, ref):
        out = []
        for i in range(len(seeds)):
            va, vr = gg[arm][i], gg[ref][i]
            out.append((va - vr) if (va is not None and vr is not None) else None)
        return out

    d_mlm = deltas(ARM_LPC, ARM_MLM)
    d_rand = deltas(ARM_LPC, ARM_RANDOM)
    valid_pairs = [i for i in range(len(seeds)) if d_mlm[i] is not None and d_rand[i] is not None]

    def _one_of_n(dm, dr):
        if not valid_pairs:
            return False
        any_pass = any((dm[i] >= HP_GG_OVER_MLM and dr[i] >= HP_GG_OVER_RANDOM) for i in valid_pairs)
        others_nonneg = all((dm[i] >= 0.0 and dr[i] >= 0.0) for i in valid_pairs)
        return any_pass and others_nonneg

    lpc_hp_geometry = _one_of_n(d_mlm, d_rand)
    probe_no_regress = (m_probe[ARM_LPC] is not None and m_probe[ARM_MLM] is not None
                        and m_probe[ARM_LPC] >= m_probe[ARM_MLM] - PROBE_NOREGRESS_EPS)
    # collapse guard: frozen rep dispersion + training-time target std both above floor
    no_collapse_reps = (m_repstd[ARM_LPC] is not None and m_repstd[ARM_LPC] >= COLLAPSE_REP_STD_FLOOR)
    m_mintgt_lpc = mean(min_tgt_std.get(ARM_LPC, []))
    no_collapse_train = (m_mintgt_lpc is not None and m_mintgt_lpc >= COLLAPSE_TARGET_STD_FLOOR)
    collapsed = (not no_collapse_reps) or (not no_collapse_train)

    # no-effect: LPC ties BOTH MLM and RANDOM within eps on graded geometry
    no_effect = False
    if m_gg[ARM_LPC] is not None and m_gg[ARM_MLM] is not None and m_gg[ARM_RANDOM] is not None:
        no_effect = (abs(m_gg[ARM_LPC] - m_gg[ARM_MLM]) < NO_EFFECT_EPS
                     and abs(m_gg[ARM_LPC] - m_gg[ARM_RANDOM]) < NO_EFFECT_EPS)

    # power
    min_gg_nq = min([per_seed[k]["arms"][ARM_LPC].get("graded_geometry_nq", 0) for k in seeds] or [0])

    # ablation: does temporal-contiguity add over LPC alone?
    tc_delta = (m_gg[ARM_LPC_TC] - m_gg[ARM_LPC]) if (m_gg[ARM_LPC_TC] is not None and m_gg[ARM_LPC] is not None) else None

    gates = []
    gates.append(record_gate("lpc_gg_over_mlm", (m_gg[ARM_LPC] - m_gg[ARM_MLM]) if (m_gg[ARM_LPC] is not None and m_gg[ARM_MLM] is not None) else -9.0,
                             HP_GG_OVER_MLM, ">=", note="ARM_LPC-ARM_MLM graded geometry (mean)"))
    gates.append(record_gate("lpc_gg_over_random", (m_gg[ARM_LPC] - m_gg[ARM_RANDOM]) if (m_gg[ARM_LPC] is not None and m_gg[ARM_RANDOM] is not None) else -9.0,
                             HP_GG_OVER_RANDOM, ">=", note="ARM_LPC-ARM_RANDOM graded geometry (mean)"))
    gates.append(record_gate("probe_no_regress", 1.0 if probe_no_regress else 0.0, 1.0, "==",
                             note="held-out probe >= MLM - %.2f" % PROBE_NOREGRESS_EPS))
    gates.append(record_gate("no_collapse_reps", m_repstd[ARM_LPC] if m_repstd[ARM_LPC] is not None else -1.0,
                             COLLAPSE_REP_STD_FLOOR, ">=", note="frozen rep per-dim std floor"))
    gates.append(record_gate("no_collapse_train", m_mintgt_lpc if m_mintgt_lpc is not None else -1.0,
                             COLLAPSE_TARGET_STD_FLOOR, ">=", note="training min target-embedding std floor"))
    gates.append(record_gate("power_min_gg_query", float(min_gg_nq), float(MIN_QUERY_TASKS), ">=",
                             note="graded-geometry query power floor"))

    run_mode = cfg["run_mode"]
    if run_mode in ("selftest", "smoke"):
        ran_ok = all(m_gg[a] is not None for a in ARMS) and all(m_repstd[a] is not None for a in ARMS)
        verdict = "SMOKE_PASS" if ran_ok else "SMOKE_INCOMPLETE"
        vmsg = ("SMOKE run_mode=%s gg[LPC=%s TC=%s MLM=%s RAND=%s] probe[LPC=%s MLM=%s] "
                "rel[LPC=%s MLM=%s] rep_std[LPC=%s RAND=%s] min_tgt_std_LPC=%s tc_delta=%s gg_nq_min=%d"
                % (run_mode, _fmt(m_gg[ARM_LPC]), _fmt(m_gg[ARM_LPC_TC]), _fmt(m_gg[ARM_MLM]), _fmt(m_gg[ARM_RANDOM]),
                   _fmt(m_probe[ARM_LPC]), _fmt(m_probe[ARM_MLM]), _fmt(m_rel[ARM_LPC]), _fmt(m_rel[ARM_MLM]),
                   _fmt(m_repstd[ARM_LPC]), _fmt(m_repstd[ARM_RANDOM]), _fmt(m_mintgt_lpc), _fmt(tc_delta), min_gg_nq))
    else:
        if collapsed:
            verdict = "FAIL_BY_COLLAPSE"
            vmsg = ("FAIL_BY_COLLAPSE: ARM_LPC variance collapsed (rep_std=%s floor=%.3f; "
                    "min_target_std=%s floor=%.3f). Mechanism class NOT refuted; retune VICReg/EMA "
                    "or use --co-scaled (capacity-ratio). gg[LPC=%s MLM=%s RAND=%s]"
                    % (_fmt(m_repstd[ARM_LPC]), COLLAPSE_REP_STD_FLOOR, _fmt(m_mintgt_lpc),
                       COLLAPSE_TARGET_STD_FLOOR, _fmt(m_gg[ARM_LPC]), _fmt(m_gg[ARM_MLM]), _fmt(m_gg[ARM_RANDOM])))
        elif min_gg_nq < MIN_QUERY_TASKS:
            verdict = "HARD_FAIL_UNDERPOWERED"
            vmsg = ("UNDERPOWERED: graded-geometry min query count %d < %d." % (min_gg_nq, MIN_QUERY_TASKS))
        elif lpc_hp_geometry and probe_no_regress:
            verdict = "HARD_PASS"
            vmsg = ("HARD_PASS: latent-PC encoder BEATS MLM by >=+%.2f AND random-init by >=+%.2f on "
                    "graded-geometry (>=1/2 seeds, other non-negative), probe no-regress. "
                    "gg[LPC=%s TC=%s MLM=%s RAND=%s] probe[LPC=%s MLM=%s RAND=%s] rel[LPC=%s MLM=%s] "
                    "d_mlm=%s d_rand=%s tc_ablation_delta=%s rep_std_LPC=%s"
                    % (HP_GG_OVER_MLM, HP_GG_OVER_RANDOM, _fmt(m_gg[ARM_LPC]), _fmt(m_gg[ARM_LPC_TC]),
                       _fmt(m_gg[ARM_MLM]), _fmt(m_gg[ARM_RANDOM]), _fmt(m_probe[ARM_LPC]), _fmt(m_probe[ARM_MLM]),
                       _fmt(m_probe[ARM_RANDOM]), _fmt(m_rel[ARM_LPC]), _fmt(m_rel[ARM_MLM]),
                       str([_fmt(x) for x in d_mlm]), str([_fmt(x) for x in d_rand]), _fmt(tc_delta),
                       _fmt(m_repstd[ARM_LPC])))
        elif no_effect:
            verdict = "HARD_FAIL_NO_EFFECT"
            vmsg = ("HARD_FAIL_NO_EFFECT: latent-PC ties BOTH MLM and random-init within +/-%.2f on "
                    "graded-geometry. Objective change did not improve representation richness at this "
                    "regime. gg[LPC=%s MLM=%s RAND=%s] probe[LPC=%s MLM=%s]"
                    % (NO_EFFECT_EPS, _fmt(m_gg[ARM_LPC]), _fmt(m_gg[ARM_MLM]), _fmt(m_gg[ARM_RANDOM]),
                       _fmt(m_probe[ARM_LPC]), _fmt(m_probe[ARM_MLM])))
        else:
            verdict = "MIDDLE_BAND"
            vmsg = ("MIDDLE_BAND: real-but-below-band. gg[LPC=%s TC=%s MLM=%s RAND=%s] d_mlm=%s d_rand=%s "
                    "probe[LPC=%s MLM=%s] tc_delta=%s (HP needs LPC-MLM>=%.2f AND LPC-RAND>=%.2f, 1/2 seeds)"
                    % (_fmt(m_gg[ARM_LPC]), _fmt(m_gg[ARM_LPC_TC]), _fmt(m_gg[ARM_MLM]), _fmt(m_gg[ARM_RANDOM]),
                       str([_fmt(x) for x in d_mlm]), str([_fmt(x) for x in d_rand]),
                       _fmt(m_probe[ARM_LPC]), _fmt(m_probe[ARM_MLM]), _fmt(tc_delta),
                       HP_GG_OVER_MLM, HP_GG_OVER_RANDOM))

    summary = dict(
        graded_geometry={a: m_gg[a] for a in ARMS},
        heldout_probe={a: m_probe[a] for a in ARMS},
        relational_auc={a: m_rel[a] for a in ARMS},
        rep_std={a: m_repstd[a] for a in ARMS},
        min_target_std_lpc=m_mintgt_lpc,
        min_target_std_lpc_tc=mean(min_tgt_std.get(ARM_LPC_TC, [])),
        lpc_gg_minus_mlm=(m_gg[ARM_LPC] - m_gg[ARM_MLM]) if (m_gg[ARM_LPC] is not None and m_gg[ARM_MLM] is not None) else None,
        lpc_gg_minus_random=(m_gg[ARM_LPC] - m_gg[ARM_RANDOM]) if (m_gg[ARM_LPC] is not None and m_gg[ARM_RANDOM] is not None) else None,
        tc_ablation_delta=tc_delta,
        per_seed_d_mlm=d_mlm, per_seed_d_rand=d_rand,
        collapsed=collapsed, no_effect=no_effect, min_gg_query=int(min_gg_nq),
    )
    return verdict, vmsg, summary, gates


# ---------------------------------------------------------------------------
# CUDA device-safety audit (runs the identical device-routed step; cuda when present)
# ---------------------------------------------------------------------------
def _cuda_safety_audit(device):
    """Run 2 end-to-end LPC steps on `device` with a tiny synthetic stream; assert finite + on-device.
    On cuda this catches the exact device bug class (cpu-tensor/Generator used with cuda). On cpu it
    exercises the identical device-routed code path (all tensors created with device=...)."""
    spec = dict(size=64, pad=0, mask=2, unk=1)
    cfg = dict(max_len=16, d_model=16, n_layers=1, n_heads=2, ffn_mult=2, mlm_steps=2, mlm_batch=8,
               mlm_lr=1e-3, lpc_mask_frac=0.25, lpc_ema_m=0.99, lpc_var_coef=1.0, lpc_cov_coef=0.04,
               lpc_pred_hidden_mult=2, lpc_tc_coef=0.5, lpc_tc_alpha=0.1)
    rng = np.random.default_rng(0)
    stream = rng.integers(3, 64, size=16 * 40).astype(np.int64)
    tmp = os.path.join(get_output_dir(ANCHOR_NAME), "_cuda_audit_tmp")
    os.makedirs(tmp, exist_ok=True)
    # temporal-contiguity path is the one with a host<->device crossing -> exercise it explicitly
    model, diag = lpc_train(stream, spec, cfg, device, seed=0, out_dir=tmp, hb_total=2, temporal_contiguity=True)
    dev_ok = all(p.device.type == device.type for p in model.parameters())
    assert dev_ok, "device audit: model params not on run device %s" % device
    assert np.isfinite(diag["final_pred_loss"]), "device audit: non-finite pred loss on %s" % device
    return dict(device=device.type, cuda_tested=(device.type == "cuda"),
                final_pred_loss=diag["final_pred_loss"], params_on_device=dev_ok)


def _selftest_assertions(per_seed, summary, verdict, out_dir, audit):
    assert len(per_seed) >= 1, "no seed completed"
    sk = sorted(per_seed.keys())[0]
    r = per_seed[sk]
    for arm in ARMS:
        assert arm in r["arms"], "arm missing: %s" % arm
        a = r["arms"][arm]
        assert a["graded_geometry"] is not None, "graded_geometry missing for %s" % arm
        assert a["rep_std"] is not None, "rep_std missing for %s" % arm
    # loss DESCENDS on the tiny overfit (both LPC arms)
    for arm in OBJECTIVE_ARMS:
        td = r["arms"][arm]["train_diag"]
        assert td["final_pred_loss"] < td["init_pred_loss"], \
            "%s pred loss did not descend: init=%.4f final=%.4f" % (arm, td["init_pred_loss"], td["final_pred_loss"])
        # NO COLLAPSE on the tiny overfit (variance floor holds)
        assert td["min_target_std"] >= COLLAPSE_TARGET_STD_FLOOR, \
            "%s target embedding collapsed: min_target_std=%.4f < %.3f" % (arm, td["min_target_std"], COLLAPSE_TARGET_STD_FLOOR)
    # temporal-contiguity actually fired (aux loss computed)
    assert r["arms"][ARM_LPC_TC]["train_diag"].get("mean_tc_loss") is not None, "TC aux loss did not fire"
    # arms differ (bit-level)
    assert len(set(r["arm_digests"].values())) == len(ARMS), "arms not all distinct"
    # cuda-safety audit ran
    assert audit["params_on_device"], "cuda-safety audit failed device parity"
    assert verdict == "SMOKE_PASS", "selftest did not complete arms (%s)" % verdict


# ---------------------------------------------------------------------------
# Plumbing self-tests (fast, no corpus): headroom projection + arm-ckpt round-trip + (seed,arm) resume
# ---------------------------------------------------------------------------
def _selftest_plumbing():
    import shutil
    import tempfile
    from tokenizers import Tokenizer, models, pre_tokenizers, trainers

    # (a) Fix C headroom projection branch logic
    fast = _headroom_projection(20000.0, 10_000_000, N_DATA_PASSES, DATA_PREP_TIME_CEILING_S)
    assert fast["verdict"] == "DATA_PREP_OK", fast
    slow = _headroom_projection(500.0, 10_000_000, N_DATA_PASSES, DATA_PREP_TIME_CEILING_S)
    assert slow["verdict"] == "DATA_PREP_TOO_SLOW", slow
    edge_rate = (10_000_000 * N_DATA_PASSES) / float(DATA_PREP_TIME_CEILING_S)   # projected == ceiling
    assert _headroom_projection(edge_rate, 10_000_000, N_DATA_PASSES,
                                DATA_PREP_TIME_CEILING_S)["verdict"] == "DATA_PREP_OK"

    # (b) Fix 2d arm-ckpt round-trips into a fresh TinyTransformer (FrozenV2Encoder-shape loader)
    tmp = tempfile.mkdtemp(prefix="lpc_ckpt_selftest_")
    try:
        spec = dict(size=64, pad=0, unk=1, mask=2)
        cfg = dict(max_len=8, d_model=16, n_layers=1, n_heads=2, ffn_mult=2, run_mode="selftest")
        m = TinyTransformer(spec["size"], cfg["max_len"], cfg["d_model"], cfg["n_layers"],
                            cfg["n_heads"], cfg["ffn_mult"], spec["pad"])
        tok = Tokenizer(models.BPE(unk_token="[UNK]"))
        tok.pre_tokenizer = pre_tokenizers.Whitespace()
        tr = trainers.BpeTrainer(vocab_size=64, special_tokens=["[PAD]", "[UNK]", "[MASK]"],
                                 show_progress=False)
        tok.train_from_iterator(["red cat sat", "blue dog ran", "green fish swam"], trainer=tr)
        path = _save_arm_ckpt(tmp, 7, ARM_LPC, m, tok, spec, cfg)
        assert path is not None, "arm-ckpt save returned None"
        ck = torch.load(os.path.join(_REPO, path), map_location="cpu", weights_only=False)
        for kk in ("state_dict", "spec", "model_cfg", "tokenizer_json", "seed", "arm"):
            assert kk in ck, "arm-ckpt missing key %s" % kk
        mc = ck["model_cfg"]
        for kk in ("vocab", "max_len", "d_model", "n_layers", "n_heads", "ffn_mult", "pad_id"):
            assert kk in mc, "model_cfg missing %s" % kk
        m2 = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                             mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
        m2.load_state_dict(ck["state_dict"])            # bit-identical to what FrozenV2Encoder does
        _ = Tokenizer.from_str(ck["tokenizer_json"])
        assert ck["arm"] == ARM_LPC and int(ck["seed"]) == 7
        assert _save_arm_ckpt(tmp, 7, ARM_RANDOM, m, tok, spec, cfg) is None, "ARM_RANDOM must save nothing"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # (c) Fix 2c (seed, arm) checkpoint/resume: crash after 2 arms -> resume skips exactly those 2
    tmp2 = tempfile.mkdtemp(prefix="lpc_resume_selftest_")
    try:
        def _fake(a):
            return dict(arm_result={"graded_geometry": 0.5}, held_rep_digest="dg_" + a, ckpt_path=None)
        for a in ARMS[:2]:
            ckpt.record_unit(tmp2, ckpt.unit_key(7, a), _fake(a))
        done = ckpt.completed_units(tmp2)
        assert done == {ckpt.unit_key(7, a) for a in ARMS[:2]}, done
        n_skip = 0
        for a in ARMS:
            if ckpt.unit_key(7, a) in done:
                n_skip += 1
                continue
            ckpt.record_unit(tmp2, ckpt.unit_key(7, a), _fake(a))
        assert n_skip == 2, "resume did not skip exactly 2 completed arms (%d)" % n_skip
        assert len(ckpt.load_units(tmp2)) == len(ARMS), "resume did not complete remaining arms"
        assert ckpt.unit_key(7, ARM_LPC) != ckpt.unit_key(13, ARM_LPC), "seed-scoped keys collide"
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)
    _log("PLUMBING SELF-TEST PASS (headroom projection + arm-ckpt round-trip + (seed,arm) resume)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _select_device():
    return torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--co-scaled", action="store_true",
                    help="capacity-ratio follow-up: smaller encoder (d=256,L=4) over the same tokens")
    ap.add_argument("--device", default=None)
    args = ap.parse_args()

    if args.self_test:
        cfg = dict(SELFTEST_CFG)
    elif args.smoke:
        cfg = dict(SMOKE_CFG)
    else:
        cfg = dict(FULL_CFG)
    if args.co_scaled:
        cfg.update(FULL_COSCALED_OVERRIDE)

    out_dir = get_output_dir(ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    _write_start_marker(out_dir, cfg["run_mode"], len(cfg["seeds"]))

    if args.self_test:
        _selftest_plumbing()

    device = torch.device(args.device) if args.device else _select_device()
    _log("run_mode=%s device=%s seeds=%s cuda=%s co_scaled=%s"
         % (cfg["run_mode"], device.type, cfg["seeds"], torch.cuda.is_available(), args.co_scaled))

    audit = _cuda_safety_audit(device)
    _log("cuda-safety audit: device=%s cuda_tested=%s final_pred_loss=%.4f params_on_device=%s"
         % (audit["device"], audit["cuda_tested"], audit["final_pred_loss"], audit["params_on_device"]))

    if not os.path.exists(ARC_CORPUS):
        raise FileNotFoundError("ARC corpus not found at %s (remote staging?)" % ARC_CORPUS)

    # ---- data-prep-headroom gate (Fix C): fail loud BEFORE any full data-prep/dispatch if too slow ----
    headroom = None
    if args.smoke:
        headroom = _data_prep_headroom(out_dir)
        _log("data_prep_headroom: %s | measured=%.0f lines/s | projected_full_dataprep=%.0fs "
             "(%.1fh) ceiling=%ds n_passes=%d (probe %d lines in %.1fs)"
             % (headroom["verdict"], headroom["measured_lines_per_sec"],
                headroom["projected_full_dataprep_s"], headroom["projected_full_dataprep_s"] / 3600.0,
                headroom["ceiling_s"], headroom["n_passes"], headroom["probe_lines"],
                headroom["probe_elapsed_s"]))
        if headroom["verdict"] == "DATA_PREP_TOO_SLOW":
            raise RuntimeError(
                "DATA_PREP_TOO_SLOW: projected full data-prep %.0fs (%.1fh) > ceiling %ds at measured "
                "%.0f lines/s -- REFUSING to green-light FULL GPU dispatch (env too slow / a per-line "
                "regression). Investigate before FULL."
                % (headroom["projected_full_dataprep_s"], headroom["projected_full_dataprep_s"] / 3600.0,
                   headroom["ceiling_s"], headroom["measured_lines_per_sec"]))

    _log("loading concept universe...")
    universe = load_concept_universe(cfg)
    _log("concept universe: K=%d single-token grounded+lexname concepts" % universe["K"])

    # ---- data-prep bundle cache (Fix D): reuse across crash/resume so arm-training crashes never
    # repeat the ~2-3h data-prep ----
    cache_path = _bundle_cache_path(out_dir, cfg)
    if os.path.exists(cache_path):
        _log("data-prep bundle cache HIT: %s (skip re-prep)" % os.path.basename(cache_path))
        bundle = _load_bundle_cache(cache_path)
    else:
        _log("preparing shared data (seed-independent: split, tokenizer, postings, stream, graph)...")
        bundle = prepare_data(cfg, universe, out_dir=out_dir)
        try:
            _save_bundle_cache(cache_path, bundle)
            _log("data-prep bundle cached: %s" % os.path.basename(cache_path))
        except (OSError, RuntimeError, ValueError) as e:
            _log("WARN bundle cache save failed (%s): %s" % (type(e).__name__, str(e)[:200]))

    for seed in cfg["seeds"]:
        res = run_one_seed(seed, cfg, device, out_dir, universe, bundle)
        write_partial(out_dir, seed, res)
        _log("seed=%d done in %.1fs" % (seed, res["elapsed_s"]))

    per_seed = aggregate_partials(out_dir, cfg["seeds"])
    verdict, vmsg, summary, gates = build_verdict(per_seed, cfg)
    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg,
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        device=device.type, cuda=bool(torch.cuda.is_available()), co_scaled=bool(args.co_scaled),
        n_seeds=len(cfg["seeds"]),
        results_summary=summary, per_seed={k: per_seed[k] for k in per_seed},
        cuda_safety_audit=audit,
        bands=dict(hp_gg_over_mlm=HP_GG_OVER_MLM, hp_gg_over_random=HP_GG_OVER_RANDOM,
                   probe_noregress_eps=PROBE_NOREGRESS_EPS, no_effect_eps=NO_EFFECT_EPS,
                   collapse_rep_std_floor=COLLAPSE_REP_STD_FLOOR,
                   collapse_target_std_floor=COLLAPSE_TARGET_STD_FLOOR, min_query=MIN_QUERY_TASKS),
        cardinality_ok=(len(per_seed) == len(cfg["seeds"])),
        expected_n_units=len(cfg["seeds"]),
        data_prep_headroom=headroom,
        mlm_reuse=dict(v2_ckpt_dir=os.path.relpath(V2_CKPT_DIR, _REPO),
                       budget_matched_steps=int(cfg["mlm_steps"]),
                       note="ARM_MLM reuses V2 ckpt at FULL (mlm_steps matched to V2 FULL=60000)"),
        checkpoint=dict(unit_granularity="(seed, arm)", helper="tools/exp_checkpoint.py",
                        dataprep_bundle_cache=os.path.basename(cache_path),
                        per_arm_ckpts={str(s): per_seed[s].get("ckpt_paths") for s in per_seed}),
        progress_logging="print_flush_true",
        start_marker_written=True, crash_diagnostic_present=True,
        final_metrics_atomicity="tmp_replace", defensive_error_checking="passed_all_4_patterns",
    )
    write_metrics(out_dir, metrics, results=list(per_seed.values()), gate_claims=gates)

    if args.self_test:
        _selftest_assertions(per_seed, summary, verdict, out_dir, audit)
        _log("SELF-TEST PASS")


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
