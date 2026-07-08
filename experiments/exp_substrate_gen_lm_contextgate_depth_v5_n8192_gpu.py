"""
substrate_gen_lm_contextgate_depth_v5_n8192_gpu -- CONTEXT-GATING arm added to the confirmed noise-compounding
  regime. The v4 cell CONFIRMED (skunkworks-VET) a genuine noise-compounding failure in a 1st-order Markov
  corpus (dRAW=+0.362: per-step reasoning degrades with depth) and CONFIRMED that neither shallow CA3-cleanup
  (dCLEAN=+0.500, WORSE) nor deep predict-residual-TD (dRES=+1.266, WORST) fixes it. The UNTESTED brain lever is
  CONTEXT-SELECTION / GATING: none of the v4 arms GATE context; a 1st-order regime is exactly the regime gating
  rewards -- all context beyond K=1 is PROVABLY conditionally-independent noise, so the optimal policy DISCARDS
  it. The brain does NOT denoise-all-then-average; it GATES which context is admitted (thalamic relay gating,
  basal-ganglia/PFC working-memory input-gating, selective attention -- the SELECTIVE-ADMISSION fix, not
  cleanup). This is our named Stage-4 attention-routing / action-selection gap, so this arm doubles as a first
  probe of that gap.

WHAT'S NEW vs v4 (base = exp_substrate_gen_lm_predresidual_td_depth_v4_n8192_gpu.py, commit 0dd45e89e):
  Keep the corpus + RAW / CLEANUP / CLEANUP_SCRAMBLED / PREDICT_RESIDUAL_TD / RESIDUAL_SCRAMBLED arms BIT-FOR-BIT
  intact (same 1st-order Markov corpus, same codebook, same Hebbian/TD readouts, same K_GRID/N/J/M_CTX). ADD:
    CONTEXT_GATE          -- relevance-gated admission over the K roll-bind context slots BEFORE binding/readout.
                             A per-slot gate g_j (learned from data by per-slot predictiveness of that slot for
                             the next token) multiplicatively admits each of the K slots: gated = sum_j
                             g_j * roll(cb[tok_j], j+1), normalized, then the SAME Hebbian readout as RAW. The
                             ONLY delta vs RAW is the multiplicative admission gate g (isolated selection test).
                             For a 1st-order source the gate concentrates on the most-recent slot (gap-1) and
                             starves the older noise slots -> should FLATTEN the depth-degradation (dGATE ~= 0).
    CONTEXT_GATE_SCRAMBLED -- firing control: identical gate-weight spectrum, admission STRUCTURE-DESTROYED
                             (slot order permuted so the dominant admission weight leaves the most-recent slot).
                             A scrambled gate admits the WRONG (older/noise) slots and must NOT flatten. Any
                             CONTEXT_GATE benefit that also appears here is a magnitude/renorm artifact, not
                             selection. At K=1 the permutation is identity so scramble==gate==RAW-single-token
                             (correctness anchor); the arms only diverge at K>=2 where selection can act.

BRAIN-GROUNDED HYPOTHESIS (why gate should win where cleanup+residual failed):
  cleanup denoises the already-diluted superposition (the noise is already mixed in -> can't unmix); residual
  injection assumes context carries predictive signal to subtract (in a 1st-order source, context beyond gap-1
  is pure noise, so the residual re-injects wrong-code noise). Gating acts EARLIER: it discards the noise slots
  BEFORE they enter the superposition, so they never dilute the useful slot. Selective ADMISSION, not cleanup.

VERDICT (bpc in BITS; best-temp ensemble; seed-averaged; K0=K_GRID[0]=1, Kmax=max(K_GRID)):
  VALID-ONLY-IF dRAW = raw[Kmax]-raw[K0] > 0 (baseline still degrades; else INCONCLUSIVE -- the v3 trap).
  HARD_PASS  = CONTEXT_GATE has bpc NON-INCREASING with depth (dGATE = GATE[Kmax]-GATE[K0] <= 0) AND beats RAW
               at Kmax by >= 0.30 bits (gap_gate >= 0.30) AND its firing control does NOT replicate
               (gap_gate - gap_scramble >= 0.15). SELECTION IS THE LEVER: noise-compounding fixed by admission-
               gating where denoise/residual failed. (The same per-antidote gate is applied uniformly to
               CLEANUP/RESIDUAL for the paired comparison; they are expected to HARD_FAIL as in v4.)
  MIDDLE_BAND= CONTEXT_GATE partially flattens (dGATE < dRAW, degrades less than RAW) but no full HARD_PASS.
  HARD_FAIL  = no antidote (including CONTEXT_GATE) flattens (min over antidotes of d >= dRAW) => selection is
               NOT the lever either; escalate to next drill (disjoint-block context representation).
  P: selection is the theoretically-correct lever for a 1st-order source (all older context is provable noise),
     so P(gate flattens) is genuinely higher than the failed denoise arms -- but honestly uncertain: the gate is
     SOFT (softmax never fully zeroes the noise slots) and learned from finite data, so residual leakage of the
     older slots may keep dGATE > 0. Value = the mechanism verdict (is admission-gating the noise-compounding
     fix), per Director.

FLAGGED RISKS (honest):
  (a) Soft-gate leakage: softmax(r/GATE_TAU) leaves nonzero weight on noise slots; if leakage is large the gate
      only partially flattens (MIDDLE_BAND). GATE_TAU chosen so the most-recent slot dominates; g logged.
  (b) Gate-learning miscalibration: if per-slot relevance r_j is mis-estimated (finite data), the gate may not
      concentrate on the most-recent slot. SELF-TEST + logged g/r per (seed,K) gate its health; a gate that does
      NOT concentrate on the most-recent slot for this 1st-order corpus is a learning failure, logged.
  (c) K=1 anchor: at K=1 gate/scramble reduce to RAW-single-token (single slot, g=[1]); the arms can only differ
      at K>=2 (exactly where selection should act). Fair test, honestly uncertain.

COMPUTE ARCHITECTURE: batched-GPU. Gate learning = K lightweight per-slot Hebbian readouts (transient W_j, one
  at a time) + fresh-batch cosine; gated encode = elementwise-scaled roll-bind bundle. All matmul-heavy, batched
  over BATCH windows. Sequential dependency (justified, inherited from v4): residual arms' delta/TD readout is an
  online self-correcting learner (W_m depends on W_{m-1}). Storage: no_storage / no_composition.

FORMULA SELF-TESTS (PROT-022, v4 set + gate additions): 1. roll-bind order-sensitive. 2. symmetric-Hebbian
  recall. 3. bpc_bits=nats/ln2, ppl=exp(nats). 4. gpu_cleanup matches numpy iterative_attractor. 5. residual K=1
  == raw-single-token. 6. delta-rule self-corrects. 7. FULL => N=8192. 8. GATE: enc_gate at K=1 (g=[1]) ==
  raw-single-token. 9. GATE: learned gate concentrates on the most-recent slot (argmax g == K-1, g[K-1] > 0.5)
  for the 1st-order corpus. 10. GATE_SCRAMBLED differs from GATE for K>=2 (admission moved off most-recent slot).
  ASCII-only. print(flush=True). start-marker + crash-diag + heartbeat.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash of the 7 depth curves)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: perplexity/bpc has no closed-form noise floor at this regime; discriminator = arm-vs-arm dRAW gate
# - baseline_in_band: RAW bpc between unigram(floor) and 0 at K0; degradation checked (dRAW>0) not saturation
# - discriminator survives scale: analytical (1/sqrt(K) superposition dilution is dimension-independent; the
#   gate's selection benefit is a slot-count / signal-ratio effect, also dimension-independent -> survives N=8192)
# - HARD_PASS strictly above floor: >=0.30 bits gap + >=0.15 control-separation (not at-floor)
# - HP_SCOPE: HARD_PASS gates apply ONLY to {CLEANUP_PER_STEP, PREDICT_RESIDUAL_TD, CONTEXT_GATE}; RAW + all
#   scramble arms are controls
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID); verdict counts len(per_unit)
# - per-unit failure-class: except Exception (not bare/BaseException); crash-diag writes CELL_CRASHED
# - calibration_check: default_ok_for_this_regime (CLEANUP_TEMP/ALPHA att1-canonical; GATE_TAU logged w/ gate
#   concentration self-test as the gate-health gate)
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

ANCHOR_NAME = "substrate_gen_lm_contextgate_depth_v5_n8192_gpu"
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
GATE_TAU = 0.1            # softmax temperature for the per-slot relevance gate (lower = sharper admission)
LOG_EVERY = 20            # W-prediction-accuracy logging cadence over training stream
ARMS = ["RAW_BIND_NO_CLEANUP", "CLEANUP_PER_STEP", "CLEANUP_SCRAMBLED",
        "PREDICT_RESIDUAL_TD", "RESIDUAL_SCRAMBLED",
        "CONTEXT_GATE", "CONTEXT_GATE_SCRAMBLED"]
ANTIDOTE_ARMS = ["CLEANUP_PER_STEP", "PREDICT_RESIDUAL_TD", "CONTEXT_GATE"]   # HP_SCOPE: HARD_PASS applies here
CONTROL_OF = {"CLEANUP_PER_STEP": "CLEANUP_SCRAMBLED", "PREDICT_RESIDUAL_TD": "RESIDUAL_SCRAMBLED",
              "CONTEXT_GATE": "CONTEXT_GATE_SCRAMBLED"}
CLEANUP_BEARING = {"CLEANUP_PER_STEP", "CLEANUP_SCRAMBLED", "PREDICT_RESIDUAL_TD", "RESIDUAL_SCRAMBLED"}
GATE_ARMS = {"CONTEXT_GATE", "CONTEXT_GATE_SCRAMBLED"}

if RUN_MODE == "smoke":
    N_DIM = 1024; SEEDS = [1]; CORPUS = 6000; N_STEPS = 40; J = 1
    K_GRID = [1, 2, 3]; M_CTX = 256; N_EVAL = 600; N_GATE_STEPS = 20
else:
    N_DIM = N; SEEDS = [7, 17, 23]; CORPUS = 40000; N_STEPS = 400; J = 4
    K_GRID = [1, 2, 3, 5]; M_CTX = 2048; N_EVAL = 2000; N_GATE_STEPS = 80

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


def enc_gate(cb, ids, starts, K, gate):
    """GATED roll-bind bundle: each of the K slots is multiplicatively admitted by the per-slot gate weight
    g_j (relevance-gated admission). gate: (K,) tensor. The ONLY delta vs enc_raw is the gate multiplier.
    At K=1 with g=[1] this is identical to enc_raw at K=1 (single-slot anchor)."""
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    for j in range(K):
        b = b + gate[j] * torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
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
# CONTEXT-GATE learning: per-slot relevance-gated admission over the K roll-bind slots
# ---------------------------------------------------------------------------
def learn_gate(cb, tr, K, gen, n_dim):
    """Learn the per-slot admission gate g (K,) by measuring each slot's predictiveness for the next token.
    For slot j: train a lightweight per-slot Hebbian readout W_j from the single roll-bound slot-j code to the
    next-token code, then relevance r_j = mean cos(W_j @ ctx_j, next_code) on a fresh batch. g = softmax(r/tau).
    Brain-grounded relevance-gated admission: predictive slots are admitted, noise slots starved. For a
    1st-order corpus the most-recent slot (j=K-1, gap 1) is maximally predictive so g concentrates there.
    Returns (g (K,), r (K,) raw relevances)."""
    if K == 1:
        return torch.ones(1, device=DEVICE), torch.zeros(1, device=DEVICE)  # single slot admitted fully
    r = torch.zeros(K, device=DEVICE)
    hi = len(tr) - KMAX - 1
    for j in range(K):
        Wj = torch.zeros(n_dim, n_dim, device=DEVICE)
        for _ in range(N_GATE_STEPS):
            st = torch.randint(0, hi, (BATCH,), generator=gen, device=DEVICE)
            ctxj = torch.roll(cb[tr[st + j]], shifts=j + 1, dims=1)
            ctxj = ctxj / (ctxj.norm(dim=1, keepdim=True) + 1e-8)
            nxt = cb[tr[st + K]]
            Wj = Wj + LR * (nxt.t() @ ctxj) / BATCH
        st = torch.randint(0, hi, (BATCH,), generator=gen, device=DEVICE)
        ctxj = torch.roll(cb[tr[st + j]], shifts=j + 1, dims=1)
        ctxj = ctxj / (ctxj.norm(dim=1, keepdim=True) + 1e-8)
        nxt = cb[tr[st + K]]
        pred = ctxj @ Wj.t(); pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
        r[j] = (pred * nxt).sum(dim=1).mean()
        del Wj
    g = torch.softmax(r / GATE_TAU, dim=0)
    return g, r


def scramble_gate(g, seed_val):
    """Firing control: permute the gate-weight spectrum across slots so the dominant admission weight LEAVES the
    most-recent slot (structure-destroyed admission ordering). Same magnitude spectrum, wrong slot assignment.
    K=1 -> identity (anchor). Rejection-samples a derangement whose result moves the max weight off slot K-1;
    falls back to slot-order reversal (deterministically starves the most-recent slot)."""
    K = g.shape[0]
    if K == 1:
        return g.clone(), torch.tensor([0], device=DEVICE)
    ggen = torch.Generator(device=DEVICE).manual_seed(int(seed_val))
    for _ in range(40):
        perm = torch.randperm(K, generator=ggen, device=DEVICE)
        gs = g[perm]
        # require: derangement (no slot keeps its own weight) AND most-recent slot (K-1) is not the argmax
        if int((perm == torch.arange(K, device=DEVICE)).sum()) == 0 and int(gs.argmax()) != (K - 1):
            return gs, perm
    perm = torch.arange(K - 1, -1, -1, device=DEVICE)   # reversal fallback
    return g[perm], perm


# ---------------------------------------------------------------------------
# readout training: Hebbian (static) for RAW/CLEANUP/GATE; delta/TD (self-correcting) for RESIDUAL arms
# ---------------------------------------------------------------------------
def train_hebb(n, cb, tr, K, mode, attractors, gen, gate=None):
    """Static Hebbian W = mean over windows of outer(next_code, ctx). (Base-cell rule; RAW/CLEANUP/GATE arms.)
    GATE arms encode with the learned admission gate; everything else identical to RAW/CLEANUP."""
    W = torch.zeros(n, n, device=DEVICE)
    for _ in range(N_STEPS):
        st = torch.randint(0, len(tr) - KMAX - 1, (BATCH,), generator=gen, device=DEVICE)
        if mode == "RAW_BIND_NO_CLEANUP":
            ctx = enc_raw(cb, tr, st, K)
        elif mode in GATE_ARMS:
            ctx = enc_gate(cb, tr, st, K, gate)
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


def _encode_eval(mode, cb, W, va, st, K, attractors, pred_perm, gate):
    if mode == "RAW_BIND_NO_CLEANUP":
        return enc_raw(cb, va, st, K), {"converged_frac": None, "mean_iters": None, "mean_cos_to_attractor": None}
    if mode in GATE_ARMS:
        return enc_gate(cb, va, st, K, gate), {"converged_frac": None, "mean_iters": None,
                                               "mean_cos_to_attractor": None}
    if mode in ("CLEANUP_PER_STEP", "CLEANUP_SCRAMBLED"):
        return enc_cleanup(cb, va, st, K, attractors, CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA)
    return enc_residual(cb, W, va, st, K, attractors, CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA, pred_perm)


def eval_arm(Ws, cb, va, K, mode, attractors, pred_perm, gate):
    """Best-temp ensemble bpc + top1 + distinct-token-rate + cleanup diag on held-out."""
    nb = min(N_EVAL, len(va) - KMAX - 1); st = torch.arange(nb, device=DEVICE); nxt = va[st + K]
    best_nats = float("inf"); best_argmax = None; diag = None
    for t in TEMP_GRID:
        Ps = []
        for W in Ws:
            ctx, d = _encode_eval(mode, cb, W, va, st, K, attractors, pred_perm, gate)
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
    # GATE K=1 (g=[1]) == enc_raw K=1 (single-slot admission anchor; both roll-shift the single token by 1)
    gate_k1 = enc_gate(cb2, ids_t, st0, 1, torch.ones(1, device=DEVICE))
    raw_k1 = enc_raw(cb2, ids_t, st0, 1)
    assert float((gate_k1 * raw_k1).sum()) > 0.999, "enc_gate K=1 g=[1] != enc_raw K=1"
    # GATE K=3 with uniform g==enc_raw (gate reduces to raw when uniform: sum of equal-weighted slots, normalized)
    gate_uni = enc_gate(cb2, ids_t, st0, 3, torch.ones(3, device=DEVICE))
    raw3 = enc_raw(cb2, ids_t, st0, 3)
    assert float((gate_uni * raw3).sum()) > 0.999, "enc_gate uniform-g != enc_raw at K=3"
    # delta-rule SELF-CORRECTS: prediction ERROR ||tgt-pred|| shrinks geometrically toward 0 (vs static Hebbian
    # which accumulates and overshoots). Measure err BEFORE each update.
    torch.manual_seed(0)
    ctxv = torch.randn(1, 256, device=DEVICE); ctxv = ctxv / ctxv.norm()
    tgt = torch.randn(1, 256, device=DEVICE); tgt = tgt / tgt.norm()
    Wd = torch.zeros(256, 256, device=DEVICE); errs = []
    for _ in range(15):
        pr = ctxv @ Wd.t(); errs.append(float((tgt - pr).norm())); Wd = Wd + 0.5 * ((tgt - pr).t() @ ctxv)
    assert errs[0] > 0.9 and errs[-1] < 0.1 * errs[0], f"delta-rule did not self-correct: err {errs[0]:.3f}->{errs[-1]:.3f}"
    # GATE learning concentrates on the most-recent slot for a 1st-order corpus (gap-1 = slot K-1 is predictive)
    gtest = np.random.default_rng(11)
    ids_1o = gen_markov1(VOCAB, 4000, gtest)
    tr_1o = torch.tensor(ids_1o, device=DEVICE)
    cb3 = build_cb(VOCAB, 512, torch.Generator(device=DEVICE).manual_seed(5))
    g3, r3 = learn_gate(cb3, tr_1o, 3, torch.Generator(device=DEVICE).manual_seed(7), 512)
    assert int(g3.argmax()) == 2, f"gate did not concentrate on most-recent slot (argmax={int(g3.argmax())}, want 2); r={r3.tolist()}"
    assert float(g3[2]) > 0.5, f"gate weight on most-recent slot too low ({float(g3[2]):.3f} <= 0.5); r={r3.tolist()}"
    # GATE_SCRAMBLED moves the dominant admission off the most-recent slot for K>=2
    gs3, perm3 = scramble_gate(g3, 99)
    assert int(gs3.argmax()) != 2, f"scrambled gate still admits most-recent slot (argmax={int(gs3.argmax())})"
    assert float((gs3 - g3).abs().sum()) > 1e-4, "scrambled gate identical to gate for K=3"
    assert N == 8192
    print("[selftest] PASS: rollbind K3recall bpc gpu_cleanup==npref residual_K1==raw delta_selfcorrects "
          "gate_K1==raw gate_uniform==raw gate_concentrates_recent scramble_moves_off_recent N8192", flush=True)


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
    # learn the per-slot admission gate + its scramble per K (relevance-gated admission over K roll-bind slots)
    gates = {}; gates_scr = {}; gate_log = {}
    for K in K_GRID:
        g, r = learn_gate(cb, tr, K, torch.Generator(device=DEVICE).manual_seed(seed * 13 + K), n_dim)
        gs, perm = scramble_gate(g, seed * 17 + K)
        gates[K] = g; gates_scr[K] = gs
        gate_log["K%d" % K] = {"gate": [round(float(x), 4) for x in g.tolist()],
                               "relevance": [round(float(x), 4) for x in r.tolist()],
                               "gate_scrambled": [round(float(x), 4) for x in gs.tolist()],
                               "scramble_perm": [int(x) for x in perm.tolist()]}
        print(f"    [gate K={K}] g={[round(float(x),3) for x in g.tolist()]} "
              f"r={[round(float(x),3) for x in r.tolist()]} scr={[round(float(x),3) for x in gs.tolist()]}", flush=True)
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
        elif mode == "RESIDUAL_SCRAMBLED":
            attractors = att_real; perm = pred_perm
        else:  # CONTEXT_GATE / CONTEXT_GATE_SCRAMBLED
            attractors = None; perm = None
        for K in K_GRID:
            gate_vec = (gates[K] if mode == "CONTEXT_GATE" else
                        (gates_scr[K] if mode == "CONTEXT_GATE_SCRAMBLED" else None))
            if mode in ("PREDICT_RESIDUAL_TD", "RESIDUAL_SCRAMBLED"):
                Ws = []; hists = []
                for i in range(J):
                    Wi, hi = train_residual_td(n_dim, cb, tr[torch.tensor(idx[i], device=DEVICE)], K, attractors,
                                               torch.Generator(device=DEVICE).manual_seed(seed * 50 + i), perm)
                    Ws.append(Wi); hists.append(hi)
                w_acc_hist["%s_K%d" % (mode, K)] = [float(np.mean(x)) for x in zip(*hists)] if hists and hists[0] else []
            else:
                Ws = [train_hebb(n_dim, cb, tr[torch.tensor(idx[i], device=DEVICE)], K, mode, attractors,
                                 torch.Generator(device=DEVICE).manual_seed(seed * 50 + i), gate_vec) for i in range(J)]
            m = eval_arm(Ws, cb, va, K, mode, attractors, perm, gate_vec)
            m.update({"seed": seed, "arm": mode, "K": K, "N": n_dim, "J": J})
            per_unit.append(m); unit_i += 1
            emit_heartbeat(out_dir, unit_idx=unit_i, elapsed_s=time.time() - t_seed, total_units=len(ARMS) * len(K_GRID),
                           extra={"seed": seed, "arm": mode, "K": K, "bpc_bits": round(m["bpc_bits"], 3)})
            print(f"    [{mode} K={K}] bpc_bits={m['bpc_bits']:.3f} ppl={m['perplexity']:.1f} top1={m['top1']:.3f} "
                  f"distinct={m['distinct_token_rate']:.2f} conv={m['cleanup_converged_frac']}", flush=True)
    base = count_baselines(ids, sp)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    return {"seed": seed, "N": n_dim, "J": J, "per_unit": per_unit, "baselines": base,
            "w_acc_hist": w_acc_hist, "gate_log": gate_log, "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


# ---------------------------------------------------------------------------
# verdict (depth-curve discriminator; selection-vs-denoise ablation)
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
    dstr = " ".join(f"d[{a}]={d[a]:+.3f}" for a in ARMS)
    summary = (f"curves: {curstr} | {dstr} | gap@Kmax clean={gap['CLEANUP_PER_STEP']:+.3f} "
               f"res={gap['PREDICT_RESIDUAL_TD']:+.3f} gate={gap['CONTEXT_GATE']:+.3f} "
               f"gate_scr={gap['CONTEXT_GATE_SCRAMBLED']:+.3f} clean_scr={gap['CLEANUP_SCRAMBLED']:+.3f} "
               f"res_scr={gap['RESIDUAL_SCRAMBLED']:+.3f} | conv_clean={conv.get('CLEANUP_PER_STEP')} "
               f"conv_res={conv.get('PREDICT_RESIDUAL_TD')} | bigram_bpc(oracle)={b:.3f} unigram_bpc={u:.3f}")

    d_raw = d["RAW_BIND_NO_CLEANUP"]
    # FIRST GATE (discriminator-fires, META_RULE_K/AG): RAW must reproduce the documented degradation
    if d_raw <= 0.0:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_DISCRIMINATOR_DID_NOT_FIRE: RAW does not degrade with depth "
                f"(dRAW={d_raw:+.3f}<=0). The v3 trap -- re-spec corpus/order/K until RAW degrades. {summary}")

    # att1 malfunction across cleanup-bearing antidotes => confounded (does not gate the pure-selection gate arm)
    cc = conv.get("CLEANUP_PER_STEP"); cr = conv.get("PREDICT_RESIDUAL_TD")
    att1_confounded = (cc is not None and cc < 0.50) and (cr is not None and cr < 0.50)

    # per-antidote HARD_PASS test (HP_SCOPE: CLEANUP_PER_STEP + PREDICT_RESIDUAL_TD + CONTEXT_GATE)
    passers = []
    for arm in ANTIDOTE_ARMS:
        ctrl = CONTROL_OF[arm]
        sep = gap[arm] - gap[ctrl]                 # control-separation (firing control must not replicate)
        att_ok = True
        if arm in conv and conv[arm] is not None:  # only cleanup-bearing antidotes carry the att1 health gate
            att_ok = conv[arm] >= 0.80
        if d[arm] <= 0.0 and gap[arm] >= 0.30 and sep >= 0.15 and att_ok:
            passers.append(arm)

    if passers:
        gate_wins = "CONTEXT_GATE" in passers
        who = "+".join(passers)
        note = ("SELECTION(context-gate) IS THE LEVER" if gate_wins else
                "an antidote passed but CONTEXT_GATE did NOT (unexpected -- read the curves)")
        return ("HARD_PASS", f"HARD_PASS[{who}]: antidote makes bpc NON-INCREASING with depth + beats RAW@Kmax "
                f">=0.30 bits + firing-control does NOT replicate. {note}. Noise-compounding confirmed "
                f"(dRAW={d_raw:+.3f}) + FIXED by {who}. {summary}")

    # MIDDLE: some antidote partially flattens (degrades less than RAW)
    partial = [a for a in ANTIDOTE_ARMS if d[a] < d_raw]
    if partial:
        conf = " (att1-confounded for cleanup arms)" if att1_confounded else ""
        return ("MIDDLE_BAND", f"MIDDLE_BAND[{'+'.join(partial)}]: antidote(s) partially flatten depth-degradation "
                f"(d < dRAW={d_raw:+.3f}) but no full HARD_PASS. Partial fix{conf}. {summary}")

    conf = " att1-confounded(conv<0.50 both cleanup arms)" if att1_confounded else ""
    return ("HARD_FAIL", f"HARD_FAIL: no antidote flattens -- CONTEXT_GATE dGATE={d['CONTEXT_GATE']:+.3f}, "
            f"dCLEAN={d['CLEANUP_PER_STEP']:+.3f}, dRES={d['PREDICT_RESIDUAL_TD']:+.3f} all >= dRAW={d_raw:+.3f} "
            f"=> selection is NOT the lever either; escalate to next drill (disjoint-block context repr).{conf} "
            f"{summary}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} dev={DEVICE.type} seeds={SEEDS} N={N_DIM} J={J} "
          f"K_GRID={K_GRID} arms={ARMS} M_CTX={M_CTX} GATE_TAU={GATE_TAU} N_GATE_STEPS={N_GATE_STEPS} "
          f"corpus_order=1 expected_units={EXPECTED_N_UNITS}", flush=True)
    if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL must run on cuda")
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "J": J,
                                                                  "arms": ARMS, "K_GRID": K_GRID, "corpus_order": 1,
                                                                  "gate_tau": GATE_TAU})
    for seed in remaining:
        print(f"[seed={seed}] ...", flush=True); t0 = time.time()
        r = run_seed(seed, N_DIM, out_dir); r["elapsed_s"] = time.time() - t0
        print(f"  seed={seed} done ({r['elapsed_s']:.0f}s)", flush=True)
        write_partial(out_dir, seed, r)
    all_results = list(aggregate_partials(out_dir, SEEDS).values())
    # ARMS-MUST-DIFFER (META_RULE_AF): the 7 depth curves must not be bit-identical
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
               "gate_tau": GATE_TAU, "expected_n_units": EXPECTED_N_UNITS, "arm_digests": digs,
               "per_seed": all_results, "curves": {arm: _arm_curve(all_results, arm) for arm in ARMS}}
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
