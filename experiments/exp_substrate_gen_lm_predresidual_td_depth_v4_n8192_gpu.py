"""
substrate_gen_lm_predresidual_td_depth_v4_n8192_gpu -- PREDICTIVE generation: does the brain's DEEP antidote
  (predict-residual injection + TD/delta self-correcting readout) beat the SHALLOW antidote (per-step CA3
  cleanup) at reversing the context-hurts-with-depth bpc curve -- AND does either work at all?

ROUTING: notes/research_brain_predictive_generation_mechanism_2026-07-07.md (DEEP arm, Section 3) +
  notes/research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md (SHALLOW arm). This is the
  CORRECTED rebuild of exp_substrate_gen_lm_perstep_cleanup_depth_v3 which came back INCONCLUSIVE because its
  2nd-order-Markov corpus does NOT reproduce the documented failure (RAW bpc DECREASED with depth -- context
  HELPED, so there was nothing to fix) and it never built the deep predict-residual arm.

TWO FIXES vs v3 (both mandatory, per Director):
  FIX 1 -- REPRODUCE THE FAILURE FIRST. The 2nd-order-Markov corpus of v3/base cell rewards depth by
    construction (the true dependency IS the last 2 tokens). This cell uses a 1st-ORDER Markov corpus (true
    dependency window = 1 token). ALL context beyond K=1 is provably conditionally-independent noise. The RAW
    roll-bind superposition of K tokens dilutes the single useful (most-recent) token by ~1/sqrt(K) of the
    normalized state -- so bpc RISES monotonically with K by construction (dRAW>0). This dilution is a
    superposition-RATIO effect, dimension-INDEPENDENT, so the degradation survives scale to N=8192
    (DISCRIMINATOR-SURVIVES-SCALE option B: analytical). FIRST GATE in the verdict: if dRAW<=0 the
    discriminator did not fire -> INCONCLUSIVE + re-spec (the v3 trap). A 1st-order corpus is the CLEANEST
    possible PURE noise-compounding testbed: any depth-hurt here is unambiguously noise-injection, not a
    higher-order-structure information deficit, so it cleanly separates the noise-compounding hypothesis from
    the capacity-ceiling hypothesis (which real text confounds).
  FIX 2 -- BUILD ALL THREE ARMS (+2 firing controls). v3 skipped the deep arm.

ARMS (per seed, per depth K in K_GRID):
  RAW_BIND_NO_CLEANUP  -- windowed roll-bind bundle of K tokens (== base cell / all 4 prior failed cells);
                          the in-cell negative control that MUST reproduce depth-degradation (bpc rises w/ K).
  CLEANUP_PER_STEP     -- SHALLOW antidote: after each bound token, CA3 iterative-attractor cleanup pulls the
                          running context toward the manifold of REAL depth-matched training contexts. Hebbian
                          readout (same as RAW). (The already-queued probe's mechanism.)
  CLEANUP_SCRAMBLED    -- SHALLOW firing control: identical cleanup dynamics, RANDOM attractor codebook. Any
                          CLEANUP benefit that also appears here is an iteration/renorm artifact.
  PREDICT_RESIDUAL_TD  -- DEEP antidote (the whole point): at each step PREDICT the current code from the prior
                          context (hetero-assoc readout), inject only the RESIDUAL e = actual - predicted into
                          the accumulator (predictive-coding / DPCM: less novel noise per step), retain CA3
                          cleanup on top, and train the readout W with a self-correcting delta/TD update
                          (successor-representation read: target - own-prediction, NOT static Hebbian sum).
  RESIDUAL_SCRAMBLED   -- DEEP firing control: identical residual+TD dynamics but the PREDICTION is structure-
                          destroyed (fixed random dimension permutation of the predicted code). Any
                          PREDICT_RESIDUAL_TD benefit that also appears here is a subtract-something/renorm
                          artifact, not the predictive structure.
  Reference ladder (K-independent, exact count tables): unigram (floor), bigram_count (ORACLE for a 1st-order
                          corpus -- captures the full true structure), trigram_count (over-parameterized).

SHALLOW-vs-DEEP ABLATION (Director): the per-arm depth curve IS the decomposition.
  - dRAW>0 (gate) : failure reproduced.
  - CLEANUP flattens but RESIDUAL flattens MORE (bigger gap@Kmax) => the brain-grounded deep mechanism wins;
    noise-injection-RATE reduction beats after-the-fact denoising.
  - CLEANUP flattens, RESIDUAL does not (or is worse) => residual carries MORE effective noise than the raw
    token (the flagged 0.507-concept-recall risk: bad predictions inject a wrong-code residual) => shallow wins.
  - Neither flattens => CAPACITY CEILING (not noise-compounding); redirect to disjoint-block context repr.

FLAGGED RISKS (from the notes, not hidden):
  (a) att1 (iterative_attractor) family has its OWN HARD_FAIL history at high-storage/high-noise regimes. A
      CLEANUP/RESIDUAL no-help could be att1 malfunction. Mitigation: log cleanup converged_frac/mean_iters/
      mean_cos per step; conv<0.50 => confounded (flag, do not read as clean refutation).
  (b) residual-noise risk: the substrate's concept-recall is ~0.507 (exp_n1...v3_1) -- if the readout's
      prediction is frequently wrong, e = actual - wrong_pred can inject MORE noise than the raw token. This is
      the primary HARD_FAIL mechanism for the deep arm and is EXPECTED-likely (P_deflated ~0.25-0.30).
  (c) 1st-order adversarial-to-residual risk: for a 1st-order source the useful predictor is the FULL most-
      recent token; residual-encoding partially removes its predicted part. At K=1 RESIDUAL encoding reduces to
      RAW-single-token (c_0=0 -> pred=0 -> e=actual), a logged correctness anchor. So residual can only differ
      from raw at K>=2, which is exactly where the mechanism should act -- fair test, honestly uncertain.

PRE-REG (bpc in BITS; best-temp ensemble; averaged over seeds; K0 = K_GRID[0]=1, Kmax = max(K_GRID)):
  VALID-ONLY-IF dRAW = raw[Kmax]-raw[K0] > 0 (baseline degrades). Else INCONCLUSIVE (re-spec).
  HARD_PASS  = at least one antidote arm A in {CLEANUP_PER_STEP, PREDICT_RESIDUAL_TD} has bpc NON-INCREASING
               with depth (dA = A[Kmax]-A[K0] <= 0) AND beats RAW at Kmax by >= 0.30 bits AND its matched
               firing control does NOT replicate (gap_A - gap_control >= 0.15) AND att1 healthy
               (converged_frac >= 0.80 for cleanup-bearing arms). Noise-compounding CONFIRMED + FIXED. The
               verdict names WHICH arm and whether DEEP beat SHALLOW (gap_res - gap_clean >= 0.15 => deep wins).
  MIDDLE_BAND= some antidote partially flattens (dA < dRAW, degrades less than RAW) but no arm meets HARD_PASS.
  HARD_FAIL  = no antidote flattens (min(dCLEAN,dRES) >= dRAW) => CAPACITY CEILING; redirect disjoint-block.
               (att1 malfunction conv<0.50 across cleanup arms => HARD_FAIL_ATT1_MALFUNCTION, confounded.)
  P_deflated ~0.25-0.30 (documented 3 HARD_FAIL + 1 MIDDLE on this family; MIDDLE/HARD_FAIL likely; value =
  the mechanism decomposition, per Director).

COMPUTE ARCHITECTURE: batched-GPU. All arms matmul-heavy (W@ctx readout, cleanup w@CB, delta W-update outer).
  Sequential dependency (justified): the residual arms' delta/TD readout is an ONLINE self-correcting learner
  -- W at iteration m depends on W at m-1 (genuine sequential dependency, that IS the mechanism). Intra-window
  K-step recurrence is also sequential (K<=5, small). Everything else batched over BATCH windows on GPU.
  STORAGE STRATEGY: no_storage / no_composition (in-memory codebook + W matrices; no PartitionedStore atoms).

FORMULA SELF-TESTS (PROT-022): 1. roll-bind order-sensitive. 2. symmetric-Hebbian recall. 3. bpc_bits=nats/ln2,
  ppl=exp(nats). 4. gpu_cleanup matches numpy iterative_attractor.iterative_cleanup (zero/low-noise recovery).
  5. residual K=1 == raw-single-token (pred=0 when c=0). 6. delta-rule REDUCES prediction error (cos to target
  rises after updates on a fixed pair) whereas one Hebbian step does NOT self-correct. 7. FULL => N=8192.
  ASCII-only. print(flush=True). start-marker + crash-diag + heartbeat.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash of the 5 depth curves)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: perplexity/bpc has no closed-form noise floor at this regime; discriminator = arm-vs-arm dRAW gate
# - baseline_in_band: RAW bpc between unigram(floor) and 0 at K0; degradation checked (dRAW>0) not saturation
# - discriminator survives scale: analytical (1/sqrt(K) superposition dilution is dimension-independent)
# - HARD_PASS strictly above floor: >=0.30 bits gap + >=0.15 control-separation (not at-floor)
# - HP_SCOPE: HARD_PASS gates apply ONLY to {CLEANUP_PER_STEP, PREDICT_RESIDUAL_TD}; RAW + scramble are controls
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID); verdict counts len(per_unit)
# - per-unit failure-class: except Exception (not bare/BaseException); crash-diag writes CELL_CRASHED
# - calibration_check: default_ok_for_this_regime (CLEANUP_TEMP/ALPHA are att1 canonical; conv logged as gate)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math, platform, traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics
try:
    from experiments._cell_heartbeat import emit_heartbeat
except Exception:
    def emit_heartbeat(*a, **k):  # best-effort; never kill a run over a heartbeat
        pass

ANCHOR_NAME = "substrate_gen_lm_predresidual_td_depth_v4_n8192_gpu"
_N_SUFFIX = 8192; N = 8192; assert N == _N_SUFFIX

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--device", default=None, help="cpu|cuda; default cuda for FULL, honors --device for smoke")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# Device: FULL requires cuda (GPU cell); smoke may run on CPU (SMOKE-ONLY-local rule).
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
    print(f"[CPU] torch {torch.__version__} device=cpu (smoke)", flush=True)

VOCAB = 70; K_ACTIVE = 8; LR = 0.5; BATCH = 64
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]   # decode softmax temperature grid (readout)
CLEANUP_TEMP = 4.0        # iterative-attractor inverse-temp multiplier (effective beta = temp*sqrt(D))
CLEANUP_STEPS = 6         # max attractor iterations per accumulation step
CLEANUP_ALPHA = 0.5       # cue re-injection weight (CA3-canonical per iterative_attractor.py)
TD_ALPHA = 0.5            # delta/TD readout learning rate (Widrow-Hoff / successor-features gamma=0)
LOG_EVERY = 20            # W-prediction-accuracy logging cadence over training stream
ARMS = ["RAW_BIND_NO_CLEANUP", "CLEANUP_PER_STEP", "CLEANUP_SCRAMBLED",
        "PREDICT_RESIDUAL_TD", "RESIDUAL_SCRAMBLED"]
ANTIDOTE_ARMS = ["CLEANUP_PER_STEP", "PREDICT_RESIDUAL_TD"]        # HP_SCOPE: HARD_PASS applies only to these
CONTROL_OF = {"CLEANUP_PER_STEP": "CLEANUP_SCRAMBLED", "PREDICT_RESIDUAL_TD": "RESIDUAL_SCRAMBLED"}
CLEANUP_BEARING = {"CLEANUP_PER_STEP", "CLEANUP_SCRAMBLED", "PREDICT_RESIDUAL_TD", "RESIDUAL_SCRAMBLED"}

if RUN_MODE == "smoke":
    N_DIM = 1024; SEEDS = [1]; CORPUS = 6000; N_STEPS = 40; J = 1
    K_GRID = [1, 2, 3]; M_CTX = 256; N_EVAL = 600
else:
    N_DIM = N; SEEDS = [7, 17, 23]; CORPUS = 40000; N_STEPS = 400; J = 4
    K_GRID = [1, 2, 3, 5]; M_CTX = 2048; N_EVAL = 2000

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS) * len(K_GRID)   # cardinality_ok gate (META_RULE_H)
K0 = K_GRID[0]; KMAX = max(K_GRID)
LN2 = math.log(2.0)


# ---------------------------------------------------------------------------
# error-checking scaffolding (start-marker / crash-diag / heartbeat)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# corpus (1st-ORDER Markov -- true dependency window = 1; context beyond K=1 is pure noise) + codebook
# ---------------------------------------------------------------------------
def gen_markov1(V, length, gen_np):
    """1st-order Markov: next token depends ONLY on the current token. Each state -> peaked distribution over
    K_ACTIVE targets (matches the base cell's per-context peakedness, but at order 1)."""
    T = np.zeros((V, V))
    for s in range(V):
        tg = gen_np.choice(V, size=K_ACTIVE, replace=False); lg = gen_np.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[s, tg] = w
    ids = np.zeros(length, dtype=np.int64); b = 0
    for i in range(length):
        ids[i] = b; b = gen_np.choice(V, p=T[b])
    return ids


def build_cb(V, n, gen):
    cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


# ---------------------------------------------------------------------------
# CA3 cleanup (torch port of hdlab.iterative_attractor.iterative_cleanup, scale_by_sqrt_d=True)
# ---------------------------------------------------------------------------
def _gpu_cleanup(state, CB, temp, max_steps, alpha, tol=1e-3):
    D = state.shape[1]; beta = temp * math.sqrt(D); q0 = state; thr = tol * math.sqrt(D)
    conv = torch.zeros(state.shape[0], dtype=torch.bool, device=DEVICE)
    iters = torch.zeros(state.shape[0], device=DEVICE)
    for t in range(max_steps):
        scores = beta * (state @ CB.t())
        scores = scores - scores.max(dim=1, keepdim=True).values
        w = torch.exp(scores); w = w / (w.sum(dim=1, keepdim=True) + 1e-30)
        est = w @ CB
        new = alpha * q0 + (1.0 - alpha) * est
        new = new / (new.norm(dim=1, keepdim=True) + 1e-12)
        step = (new - state).norm(dim=1)
        newly = (~conv) & (step < thr)
        iters = torch.where(conv, iters, iters + 1.0)
        conv = conv | newly
        state = new
    cos_near = (state @ CB.t()).max(dim=1).values
    diag = {"converged_frac": float(conv.float().mean()), "mean_iters": float(iters.mean()),
            "mean_cos_to_attractor": float(cos_near.mean())}
    return state, diag


# ---------------------------------------------------------------------------
# context encoders (windowed; all arms encode the same K-token windows, differ by rule)
# ---------------------------------------------------------------------------
def enc_raw(cb, ids, starts, K):
    """One-shot roll-bind bundle of K tokens (== base/failed-cell mechanism). (B,N) normalized."""
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    for j in range(K):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def enc_cleanup(cb, ids, starts, K, attractors, temp, steps, alpha):
    """Incremental accumulation with per-step CA3 cleanup. attractors: list[d-1]=(M,N) normalized codebook."""
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE); cf = []; mi = []; mc = []
    for j in range(K):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
        bn = b / (b.norm(dim=1, keepdim=True) + 1e-8)
        bn, d = _gpu_cleanup(bn, attractors[j], temp, steps, alpha)
        cf.append(d["converged_frac"]); mi.append(d["mean_iters"]); mc.append(d["mean_cos_to_attractor"]); b = bn
    out = b / (b.norm(dim=1, keepdim=True) + 1e-8)
    return out, {"converged_frac": float(np.mean(cf)), "mean_iters": float(np.mean(mi)),
                 "mean_cos_to_attractor": float(np.mean(mc))}


def enc_residual(cb, W, ids, starts, K, attractors, temp, steps, alpha, pred_perm=None):
    """DEEP encoder: accumulate only the prediction RESIDUAL e=actual-predicted (predictive-coding/DPCM), with
    per-step CA3 cleanup retained. W: (N,N) hetero-assoc readout (predict current code from prior context).
    pred_perm: if given (N,) int perm, the predicted code's dims are permuted BEFORE subtraction (firing
    control: structure-destroyed prediction). At j=0 the state is zero so pred=0 and e=actual (== raw single
    token) -- the logged correctness anchor; residual only diverges from raw at K>=2."""
    B = starts.shape[0]; n = cb.shape[1]
    c = torch.zeros(B, n, device=DEVICE); cf = []; mi = []; mc = []
    for j in range(K):
        a = cb[ids[starts + j]]                                  # (B,N) actual current code
        pred = c @ W.t()                                          # (B,N) predicted current code from prior ctx
        if pred_perm is not None:
            pred = pred[:, pred_perm]                             # structure-destroy (firing control)
        pnorm = pred.norm(dim=1, keepdim=True)
        pred = torch.where(pnorm > 1e-8, pred / (pnorm + 1e-8), pred)   # normalize non-zero predictions
        e = a - pred                                              # residual (surprise); at j=0 pred==0 -> e==a
        c = torch.roll(c, shifts=1, dims=1) + e
        c = c / (c.norm(dim=1, keepdim=True) + 1e-8)
        if attractors is not None:
            c, d = _gpu_cleanup(c, attractors[j], temp, steps, alpha)
            cf.append(d["converged_frac"]); mi.append(d["mean_iters"]); mc.append(d["mean_cos_to_attractor"])
    out = c / (c.norm(dim=1, keepdim=True) + 1e-8)
    diag = ({"converged_frac": float(np.mean(cf)), "mean_iters": float(np.mean(mi)),
             "mean_cos_to_attractor": float(np.mean(mc))} if cf else
            {"converged_frac": None, "mean_iters": None, "mean_cos_to_attractor": None})
    return out, diag


def build_ctx_attractors(cb, tr, K_max, m_ctx, gen, scramble=False):
    """For each depth d=1..K_max, m_ctx real depth-d training contexts as attractors (or random if scramble)."""
    atts = []
    for d in range(1, K_max + 1):
        st = torch.randint(0, len(tr) - K_max - 1, (m_ctx,), generator=gen, device=DEVICE)
        ctx = enc_raw(cb, tr, st, d)
        if scramble:
            r = torch.randn(ctx.shape, generator=gen, device=DEVICE)
            ctx = r / (r.norm(dim=1, keepdim=True) + 1e-8)
        atts.append(ctx)
    return atts


# ---------------------------------------------------------------------------
# readout training: Hebbian (static) for RAW/CLEANUP; delta/TD (self-correcting) for RESIDUAL arms
# ---------------------------------------------------------------------------
def train_hebb(n, cb, tr, K, mode, attractors, gen):
    """Static Hebbian W = mean over windows of outer(next_code, ctx). (Base-cell rule; RAW/CLEANUP arms.)"""
    W = torch.zeros(n, n, device=DEVICE)
    for _ in range(N_STEPS):
        st = torch.randint(0, len(tr) - KMAX - 1, (BATCH,), generator=gen, device=DEVICE)
        if mode == "RAW_BIND_NO_CLEANUP":
            ctx = enc_raw(cb, tr, st, K)
        else:
            ctx, _ = enc_cleanup(cb, tr, st, K, attractors, CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA)
        nxt = cb[tr[st + K]]
        W = W + LR * (nxt.t() @ ctx) / BATCH
    return W


def train_residual_td(n, cb, tr, K, attractors, gen, pred_perm=None):
    """DEEP readout: online delta/TD (successor-features gamma=0) update. W bootstraps its OWN residual encoding:
    each iteration encodes windows with the CURRENT W (residual injection depends on W), predicts the next code,
    and self-corrects W += alpha*(target - own_prediction)*ctx -- NOT a static Hebbian sum. Returns (W, acc_hist)
    where acc_hist is the running cos(pred_next, true_next) over the training stream (HARD_PASS diagnostic:
    must improve, not diverge)."""
    W = torch.zeros(n, n, device=DEVICE); acc_hist = []
    for it in range(N_STEPS):
        st = torch.randint(0, len(tr) - KMAX - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx, _ = enc_residual(cb, W, tr, st, K, attractors, CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA, pred_perm)
        nxt = cb[tr[st + K]]                                     # (B,N) true next code
        pred_nxt = ctx @ W.t()                                   # (B,N) current prediction of next code
        # delta/TD(0) self-correcting update (Widrow-Hoff; SR gamma=0 => next-code target)
        W = W + TD_ALPHA * ((nxt - pred_nxt).t() @ ctx) / BATCH
        if it % LOG_EVERY == 0:
            pn = pred_nxt / (pred_nxt.norm(dim=1, keepdim=True) + 1e-8)
            acc_hist.append(float((pn * nxt).sum(dim=1).mean()))
    return W, acc_hist


def _encode_eval(mode, cb, W, va, st, K, attractors, pred_perm):
    if mode == "RAW_BIND_NO_CLEANUP":
        return enc_raw(cb, va, st, K), {"converged_frac": None, "mean_iters": None, "mean_cos_to_attractor": None}
    if mode in ("CLEANUP_PER_STEP", "CLEANUP_SCRAMBLED"):
        return enc_cleanup(cb, va, st, K, attractors, CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA)
    return enc_residual(cb, W, va, st, K, attractors, CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA, pred_perm)


def eval_arm(Ws, cb, va, K, mode, attractors, pred_perm):
    """Best-temp ensemble bpc + top1 + distinct-token-rate + cleanup diag on held-out."""
    nb = min(N_EVAL, len(va) - KMAX - 1); st = torch.arange(nb, device=DEVICE); nxt = va[st + K]
    # encode eval contexts once per ensemble member (residual encoding is W-specific -> per-W)
    best_nats = float("inf"); best_argmax = None; diag = None
    for t in TEMP_GRID:
        Ps = []
        for W in Ws:
            ctx, d = _encode_eval(mode, cb, W, va, st, K, attractors, pred_perm)
            if diag is None:
                diag = d
            pred = ctx @ W.t(); pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
            cos = pred @ cb.t(); z = cos / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
            Ps.append(ez / (ez.sum(dim=1, keepdim=True) + 1e-30))
        P = torch.stack(Ps).mean(0); pt = P[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        nats = float((-torch.log(pt)).mean())
        if nats < best_nats:
            best_nats = nats; best_argmax = P.argmax(dim=1)
    top1 = float((best_argmax == nxt).float().mean())
    distinct = float(torch.unique(best_argmax).numel()) / float(VOCAB)
    return {"bpc_nats": best_nats, "bpc_bits": best_nats / LN2, "perplexity": math.exp(best_nats),
            "top1": top1, "distinct_token_rate": distinct,
            "cleanup_converged_frac": diag["converged_frac"], "cleanup_mean_iters": diag["mean_iters"],
            "cleanup_mean_cos_to_attractor": diag["mean_cos_to_attractor"]}


def count_baselines(ids, sp):
    """Exact unigram / bigram(ORACLE for 1st-order) / trigram perplexity + bpc ladder (numpy; K-independent)."""
    tn = ids[:sp]
    c1 = np.ones(VOCAB)
    for i in range(len(tn)): c1[tn[i]] += 1
    Pu = c1 / c1.sum()
    c2 = np.ones((VOCAB, VOCAB))
    for i in range(len(tn) - 1): c2[tn[i], tn[i + 1]] += 1
    Pb = c2 / c2.sum(axis=1, keepdims=True)
    c3 = np.ones((VOCAB * VOCAB, VOCAB))
    for i in range(len(tn) - 2): c3[tn[i] * VOCAB + tn[i + 1], tn[i + 2]] += 1
    Pt = c3 / c3.sum(axis=1, keepdims=True)
    ve = ids[sp:]; nb = min(N_EVAL, len(ve) - 2)
    uni = math.exp(-np.mean([math.log(max(Pu[ve[i + 2]], 1e-12)) for i in range(nb)]))
    big = math.exp(-np.mean([math.log(max(Pb[ve[i + 1], ve[i + 2]], 1e-12)) for i in range(nb)]))
    tri = math.exp(-np.mean([math.log(max(Pt[ve[i] * VOCAB + ve[i + 1], ve[i + 2]], 1e-12)) for i in range(nb)]))
    return {"unigram_ppl": float(uni), "bigram_count_ppl": float(big), "trigram_count_ppl": float(tri),
            "unigram_bpc_bits": math.log(uni) / LN2, "bigram_count_bpc_bits": math.log(big) / LN2,
            "trigram_count_bpc_bits": math.log(tri) / LN2}


# ---------------------------------------------------------------------------
# self-test (PROT-022): runs on import; blocks dispatch if any assert fails
# ---------------------------------------------------------------------------
def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0); cb = build_cb(7, 128, gen)
    s = torch.tensor([0, 1, 2, 3], device=DEVICE)
    b1 = enc_raw(cb, s, torch.tensor([0], device=DEVICE), 3)
    b2 = enc_raw(cb, torch.tensor([2, 1, 0, 3], device=DEVICE), torch.tensor([0], device=DEVICE), 3)
    assert float((b1 * b2).sum()) < 0.95, "roll-bind not order-sensitive"
    # symmetric-Hebbian recall
    W = torch.zeros(128, 128, device=DEVICE); ctx = enc_raw(cb, s, torch.tensor([0], device=DEVICE), 3); nxt = cb[3]
    W = W + torch.outer(nxt, ctx.squeeze(0)); pred = W @ ctx.squeeze(0)
    assert float(pred @ nxt / (pred.norm() * nxt.norm() + 1e-8)) > 0.5, "K3 recall"
    # bpc/ppl formula
    assert abs(math.exp(1.6094) - 5.0) < 0.01 and abs((math.log(5.0) / LN2) - 2.3219) < 0.01, "bpc/ppl formula"
    # gpu_cleanup MUST match numpy iterative_attractor reference
    from hdlab.iterative_attractor import iterative_cleanup as np_clean
    g2 = np.random.default_rng(3); M, D = 32, 256
    cbn = g2.standard_normal((M, D)).astype(np.float32); cbn = cbn / (np.linalg.norm(cbn, axis=1, keepdims=True) + 1e-12)
    cbt = torch.tensor(cbn, device=DEVICE)
    for i in [0, 5, 17]:
        cue = cbn[i] + 0.05 * g2.standard_normal(D).astype(np.float32)
        r_np = np_clean(cue.copy(), cbn, temp=8.0, max_steps=6, alpha=0.5)
        stt = torch.tensor(cue[None, :], device=DEVICE); stt = stt / (stt.norm(dim=1, keepdim=True) + 1e-12)
        s_gpu, _ = _gpu_cleanup(stt, cbt, 8.0, 6, 0.5)
        idx_gpu = int((s_gpu @ cbt.t()).argmax(dim=1)[0])
        assert idx_gpu == int(r_np["argmax_idx"]) == i, f"gpu_cleanup mismatch numpy ref at i={i}"
    # residual K=1 == raw single-token (c_0=0 -> pred=0 -> e=actual); verify state matches encode of single tok
    cb2 = build_cb(VOCAB, 256, torch.Generator(device=DEVICE).manual_seed(1))
    W0 = torch.zeros(256, 256, device=DEVICE)
    ids_t = torch.tensor([3, 5, 9, 2, 7], device=DEVICE); st0 = torch.tensor([0], device=DEVICE)
    res_k1, _ = enc_residual(cb2, W0, ids_t, st0, 1, None, CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA)
    exp_k1 = cb2[3:4] / (cb2[3:4].norm(dim=1, keepdim=True) + 1e-8)
    assert float((res_k1 * exp_k1).sum()) > 0.999, "residual K=1 != raw single-token (pred should be 0 at c=0)"
    # delta-rule SELF-CORRECTS: prediction ERROR ||tgt-pred|| shrinks geometrically toward 0 (vs static Hebbian
    # which accumulates and overshoots). Measure err BEFORE each update.
    torch.manual_seed(0)
    ctxv = torch.randn(1, 256, device=DEVICE); ctxv = ctxv / ctxv.norm()
    tgt = torch.randn(1, 256, device=DEVICE); tgt = tgt / tgt.norm()
    Wd = torch.zeros(256, 256, device=DEVICE); errs = []
    for _ in range(15):
        pr = ctxv @ Wd.t(); errs.append(float((tgt - pr).norm())); Wd = Wd + 0.5 * ((tgt - pr).t() @ ctxv)
    assert errs[0] > 0.9 and errs[-1] < 0.1 * errs[0], f"delta-rule did not self-correct: err {errs[0]:.3f}->{errs[-1]:.3f}"
    assert N == 8192
    print("[selftest] PASS: rollbind_order K3_recall bpc gpu_cleanup==npref residual_K1==raw delta_selfcorrects N8192", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, n_dim: int, out_dir) -> Dict:
    gen = torch.Generator(device=DEVICE).manual_seed(seed); gen_np = np.random.default_rng(seed + 99)
    ids = gen_markov1(VOCAB, CORPUS, gen_np); sp = int(0.8 * len(ids))
    tr = torch.tensor(ids[:sp], device=DEVICE); va = torch.tensor(ids[sp:], device=DEVICE)
    cb = build_cb(VOCAB, n_dim, gen)
    att_real = build_ctx_attractors(cb, tr, KMAX, M_CTX, torch.Generator(device=DEVICE).manual_seed(seed * 7 + 1), scramble=False)
    att_scr = build_ctx_attractors(cb, tr, KMAX, M_CTX, torch.Generator(device=DEVICE).manual_seed(seed * 7 + 2), scramble=True)
    # fixed prediction-scramble permutation (firing control for the deep arm)
    pred_perm = torch.randperm(n_dim, generator=torch.Generator(device=DEVICE).manual_seed(seed * 7 + 3), device=DEVICE)
    idx = np.array_split(np.arange(len(tr)), J)
    per_unit = []; w_acc_hist = {}
    unit_i = 0; t_seed = time.time()
    for mode in ARMS:
        if mode in ("RAW_BIND_NO_CLEANUP",):
            attractors = None; perm = None
        elif mode == "CLEANUP_PER_STEP":
            attractors = att_real; perm = None
        elif mode == "CLEANUP_SCRAMBLED":
            attractors = att_scr; perm = None
        elif mode == "PREDICT_RESIDUAL_TD":
            attractors = att_real; perm = None
        else:  # RESIDUAL_SCRAMBLED
            attractors = att_real; perm = pred_perm
        for K in K_GRID:
            if mode in ("PREDICT_RESIDUAL_TD", "RESIDUAL_SCRAMBLED"):
                Ws = []; hists = []
                for i in range(J):
                    Wi, hi = train_residual_td(n_dim, cb, tr[torch.tensor(idx[i], device=DEVICE)], K, attractors,
                                               torch.Generator(device=DEVICE).manual_seed(seed * 50 + i), perm)
                    Ws.append(Wi); hists.append(hi)
                w_acc_hist["%s_K%d" % (mode, K)] = [float(np.mean(x)) for x in zip(*hists)] if hists and hists[0] else []
            else:
                Ws = [train_hebb(n_dim, cb, tr[torch.tensor(idx[i], device=DEVICE)], K, mode, attractors,
                                 torch.Generator(device=DEVICE).manual_seed(seed * 50 + i)) for i in range(J)]
            m = eval_arm(Ws, cb, va, K, mode, attractors, perm)
            m.update({"seed": seed, "arm": mode, "K": K, "N": n_dim, "J": J})
            per_unit.append(m); unit_i += 1
            emit_heartbeat(out_dir, unit_idx=unit_i, elapsed_s=time.time() - t_seed, total_units=len(ARMS) * len(K_GRID),
                           extra={"seed": seed, "arm": mode, "K": K, "bpc_bits": round(m["bpc_bits"], 3)})
            print(f"    [{mode} K={K}] bpc_bits={m['bpc_bits']:.3f} ppl={m['perplexity']:.1f} top1={m['top1']:.3f} "
                  f"distinct={m['distinct_token_rate']:.2f} conv={m['cleanup_converged_frac']}", flush=True)
    base = count_baselines(ids, sp)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    return {"seed": seed, "N": n_dim, "J": J, "per_unit": per_unit, "baselines": base,
            "w_acc_hist": w_acc_hist, "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


# ---------------------------------------------------------------------------
# verdict (depth-curve discriminator; shallow-vs-deep ablation)
# ---------------------------------------------------------------------------
def _arm_curve(all_results, arm, field="bpc_bits"):
    out = {}
    for K in K_GRID:
        vals = [u[field] for r in all_results for u in r["per_unit"] if u["arm"] == arm and u["K"] == K]
        out[K] = float(np.mean(vals)) if vals else float("nan")
    return out


def _conv_for(all_results, arm):
    vals = [u["cleanup_converged_frac"] for r in all_results for u in r["per_unit"]
            if u["arm"] == arm and u["cleanup_converged_frac"] is not None]
    return float(np.mean(vals)) if vals else None


def compute_verdict(all_results) -> Tuple[str, str]:
    if not all_results:
        return ("HARD_FAIL", "no results")
    n_units = sum(len(r["per_unit"]) for r in all_results)
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: got {n_units} units, expected {EXPECTED_N_UNITS}")
    cur = {arm: _arm_curve(all_results, arm) for arm in ARMS}
    d = {arm: cur[arm][KMAX] - cur[arm][K0] for arm in ARMS}       # depth-degradation per arm (positive = worse)
    gap = {arm: cur["RAW_BIND_NO_CLEANUP"][KMAX] - cur[arm][KMAX] for arm in ARMS}  # vs RAW at Kmax
    conv = {arm: _conv_for(all_results, arm) for arm in CLEANUP_BEARING}
    b = float(np.mean([r["baselines"]["bigram_count_bpc_bits"] for r in all_results]))
    u = float(np.mean([r["baselines"]["unigram_bpc_bits"] for r in all_results]))
    curstr = " ".join(f"{a}={ {k: round(v,3) for k,v in cur[a].items()} }" for a in ARMS)
    dstr = " ".join(f"d{a.split('_')[0]}={d[a]:+.3f}" for a in ARMS)
    summary = (f"curves: {curstr} | {dstr} | gap@Kmax clean={gap['CLEANUP_PER_STEP']:+.3f} "
               f"res={gap['PREDICT_RESIDUAL_TD']:+.3f} clean_scr={gap['CLEANUP_SCRAMBLED']:+.3f} "
               f"res_scr={gap['RESIDUAL_SCRAMBLED']:+.3f} | conv_clean={conv.get('CLEANUP_PER_STEP')} "
               f"conv_res={conv.get('PREDICT_RESIDUAL_TD')} | bigram_bpc(oracle)={b:.3f} unigram_bpc={u:.3f}")

    d_raw = d["RAW_BIND_NO_CLEANUP"]
    # FIRST GATE (discriminator-fires, META_RULE_K/AG): RAW must reproduce the documented degradation
    if d_raw <= 0.0:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_DISCRIMINATOR_DID_NOT_FIRE: RAW does not degrade with depth "
                f"(dRAW={d_raw:+.3f}<=0). The v3 trap -- re-spec corpus/order/K until RAW degrades. {summary}")

    # att1 malfunction across cleanup-bearing antidotes => confounded
    cc = conv.get("CLEANUP_PER_STEP"); cr = conv.get("PREDICT_RESIDUAL_TD")
    if (cc is not None and cc < 0.50) and (cr is not None and cr < 0.50):
        return ("HARD_FAIL", f"HARD_FAIL_ATT1_MALFUNCTION: cleanup attractor out of working regime "
                f"(conv_clean={cc:.2f} conv_res={cr:.2f} <0.50); result confounded, not a clean refutation. {summary}")

    # per-antidote HARD_PASS test (HP_SCOPE: only CLEANUP_PER_STEP + PREDICT_RESIDUAL_TD)
    passers = []
    for arm in ANTIDOTE_ARMS:
        ctrl = CONTROL_OF[arm]
        sep = gap[arm] - gap[ctrl]                 # control-separation (firing control must not replicate)
        att_ok = True
        if arm in conv and conv[arm] is not None:
            att_ok = conv[arm] >= 0.80
        if d[arm] <= 0.0 and gap[arm] >= 0.30 and sep >= 0.15 and att_ok:
            passers.append(arm)

    if passers:
        deep_wins = ("PREDICT_RESIDUAL_TD" in passers and
                     gap["PREDICT_RESIDUAL_TD"] - gap["CLEANUP_PER_STEP"] >= 0.15)
        who = "+".join(passers)
        depth_note = ("DEEP(predict-residual) BEATS SHALLOW(cleanup)" if deep_wins else
                      ("SHALLOW(cleanup) wins or ties" if "CLEANUP_PER_STEP" in passers else "DEEP-only"))
        return ("HARD_PASS", f"HARD_PASS[{who}]: antidote makes bpc NON-INCREASING with depth + beats RAW@Kmax "
                f">=0.30 bits + firing-control does NOT replicate + att1 healthy => NOISE-COMPOUNDING confirmed+fixed. "
                f"{depth_note}. {summary}")

    # MIDDLE: some antidote partially flattens (degrades less than RAW)
    partial = [a for a in ANTIDOTE_ARMS if d[a] < d_raw]
    if partial:
        return ("MIDDLE_BAND", f"MIDDLE_BAND[{'+'.join(partial)}]: antidote(s) partially flatten depth-degradation "
                f"(d<{d_raw:+.3f}=dRAW) but no full HARD_PASS. Partial noise-compounding. {summary}")

    return ("HARD_FAIL", f"HARD_FAIL: no antidote flattens (dCLEAN={d['CLEANUP_PER_STEP']:+.3f} "
            f"dRES={d['PREDICT_RESIDUAL_TD']:+.3f} both >= dRAW={d_raw:+.3f}) => CAPACITY CEILING not "
            f"noise-compounding; redirect to disjoint-block context representation. {summary}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} dev={DEVICE.type} seeds={SEEDS} N={N_DIM} J={J} "
          f"K_GRID={K_GRID} arms={ARMS} M_CTX={M_CTX} corpus_order=1 expected_units={EXPECTED_N_UNITS}", flush=True)
    if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL must run on cuda")
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "J": J,
                                                                  "arms": ARMS, "K_GRID": K_GRID, "corpus_order": 1})
    for seed in remaining:
        print(f"[seed={seed}] ...", flush=True); t0 = time.time()
        r = run_seed(seed, N_DIM, out_dir); r["elapsed_s"] = time.time() - t0
        print(f"  seed={seed} done ({r['elapsed_s']:.0f}s)", flush=True)
        write_partial(out_dir, seed, r)
    all_results = list(aggregate_partials(out_dir, SEEDS).values())
    # ARMS-MUST-DIFFER (META_RULE_AF): the 5 depth curves must not be bit-identical
    import hashlib
    digs = {}
    for arm in ARMS:
        c = _arm_curve(all_results, arm)
        digs[arm] = hashlib.sha256(json.dumps({k: round(v, 6) for k, v in c.items()}).encode()).hexdigest()
    for a in ARMS:
        for b2 in ARMS:
            if a < b2:
                assert digs[a] != digs[b2], f"META_RULE_AF VIOLATION: arms {a} and {b2} bit-identical curves"
    verdict, vmsg = compute_verdict(all_results)
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    if DEVICE.type == "cuda":
        print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM, "J": J,
               "run_mode": RUN_MODE, "device": DEVICE.type, "n_seeds": len(SEEDS), "corpus_order": 1,
               "expected_n_units": EXPECTED_N_UNITS, "arm_digests": digs, "per_seed": all_results,
               "curves": {arm: _arm_curve(all_results, arm) for arm in ARMS}}
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
