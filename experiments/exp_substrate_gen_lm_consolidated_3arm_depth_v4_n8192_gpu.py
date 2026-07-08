"""
substrate_gen_lm_consolidated_3arm_depth_v4_n8192_gpu -- shallow-vs-deep noise-compounding decomposition for
  predictive generation: does per-step CA3 cleanup (SHALLOW) or predict-residual/TD-bootstrap (DEEP, brain-
  grounded) FLATTEN/REVERSE the context-hurts-with-depth bpc curve, or does neither (capacity ceiling)?

ROUTING: notes/research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md (shallow CA3 probe) +
  notes/research_brain_predictive_generation_mechanism_2026-07-07.md +
  notes/research_brain_predictive_generation_predict_residual_build_spec_2026-07-07.md (deep predict-residual).
  Consolidates onto the ONLY prior MIDDLE_BAND generation cell's corpus/harness/baselines
  (exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py: single=62.1/ensemble=43.1/bigram=55.8/
  trigram_oracle=20.4 ppl). DO NOT mutate that landed cell; this is a _v4 consolidated sibling.

CAPABILITY QUESTION (predictive next-token, not sequence-recovery): the substrate has a documented 3-HARD_FAIL/
  1-MIDDLE history where context accumulation makes prediction WORSE with depth (exp_n2_context_depth_hd_binding_v1
  bpc 5.00->5.05->5.18, K=1,2,3). Is that NOISE-COMPOUNDING (each step accumulates crosstalk; fixable) or a
  representation-CAPACITY ceiling (superposed/bind context structurally cannot carry higher-order statistics)?
  And if fixable: does the DEEP brain-grounded fix (inject only the bounded prediction RESIDUAL, learn W via
  TD-bootstrap -- predictive-coding + successor-representation) beat the SHALLOW fix (per-step CA3 cleanup)?

NOISE-COMPOUNDING ISOLATION ON SYNTHETIC 2nd-ORDER DATA: on a clean order-2 Markov corpus the true dependency
  is exactly 2 tokens; context beyond K=2 is PROVABLY pure noise (Markov property). So degradation is measured
  from K=2 (true order) outward: does the baseline degrade as K exceeds 2, and do the mechanisms prevent it?
  (Empirical caveat, logged: the v3 CA3 CPU-smoke found RAW does NOT degrade for K<=3 on this synthetic corpus
  -- context up to the true order helps. The documented real-text degradation may be real-text-specific. The
  K>2 sweep + degradation-from-K=2 discriminator is the clean synthetic proxy; if BASELINE does not degrade
  even for K>>2 at full N=8192, that is itself evidence the failure is capacity/real-text-specific.)

ARMS (per seed x per depth K; all mechanism arms retain per-step CA3 cleanup, per the build spec's additive rule):
  BASELINE_RAW_BIND    -- one-shot roll-bind bundle of K raw tokens (== base cell mechanism). NEGATIVE CONTROL;
                          must reproduce degradation (bpc rises for K>2) or verdict is INCONCLUSIVE.
  CA3_CLEANUP_PER_STEP -- SHALLOW fix: incremental accumulation, per-step soft-attractor cleanup toward the
                          manifold of REAL depth-matched training contexts.
  CA3_SCRAMBLED        -- ablation control for CA3: same cleanup dynamics, RANDOM attractor codebook.
  PREDICT_RESIDUAL_TD  -- DEEP fix: inject only the bounded prediction RESIDUAL (actual - W-predicted) per step
                          (predictive-coding/DPCM), + per-step CA3 cleanup, + W learned by TD(0)/successor-feature
                          bootstrap instead of static Hebbian counting.
  RESIDUAL_SCRAMBLED   -- ablation control for predict-residual: same TD + cleanup, but residual replaced by a
                          structureless random vector (isolates whether the residual STRUCTURE carries the benefit).
  Reference ladder (K-independent exact count tables): unigram, bigram_count, trigram_count (oracle ceiling).

ABLATION MAP (which mechanism -- shallow or deep -- wins, cleanly separated):
  CA3_CLEANUP_PER_STEP vs CA3_SCRAMBLED         => isolates the CA3-cleanup (shallow) mechanism.
  PREDICT_RESIDUAL_TD  vs RESIDUAL_SCRAMBLED    => isolates the predict-residual+TD (deep) mechanism.
  PREDICT_RESIDUAL_TD  vs CA3_CLEANUP_PER_STEP  => deep-vs-shallow head-to-head.

PRE-REG (bpc in BITS; ensemble; seed-mean; Kmax=max(K_GRID); K0=2 true order):
  dX = bpc_X(Kmax) - bpc_X(K0).
  HARD_PASS  = SOME mechanism arm has dX <= 0 (non-increasing past true order) AND beats BASELINE at Kmax by
               >= 0.30 bits AND its scramble control does NOT replicate the benefit (d(scramble) - d(mech) >= 0.15)
               AND (for the residual arm) TD did not diverge. Noise-compounding CONFIRMED + FIXED.
  MIDDLE_BAND= a mechanism arm partially flattens (dX < d_BASELINE) but does not meet HARD_PASS.
  HARD_FAIL  = NEITHER mechanism changes the degradation (both dX >= d_BASELINE) => CAPACITY CEILING (informative
               negative; redirect to disjoint-block/frame-slot context representation) OR TD diverged / att1
               malfunction dominates (confound flagged distinctly from a clean refutation).
  INCONCLUSIVE = BASELINE does not degrade (d_BASELINE <= 0): discriminator did not fire at this regime.
  Pre-committed expected tier: MIDDLE_BAND or HARD_FAIL. P(non-trivial predictive generation) ~0.25-0.30
  (deflated; documented 3-HARD_FAIL history). VALUE = shallow-vs-deep mechanism decomposition + noise-vs-ceiling.

RESIDUAL-NOISIER-THAN-RAW RISK (flagged in build spec): concept-recall ~0.507 => ~half the predictions are wrong
  => a naive residual (actual - wrong_prediction) can be NOISIER than the raw token. Logged: mean_resid_norm per
  arm (raw token norm = 1.0; residual norm > ~1.4 => residual is noisier than raw = the flagged failure path).
  att1 risk: cleanup_converged_frac logged per arm (separates att1-malfunction from genuine no-help).

SELF-TESTS (PROT-022): 1. roll-bind order-sensitive. 2. Hebbian recall. 3. ppl=exp(nats), bpc=nats/ln2.
  4. gpu_cleanup == numpy iterative_attractor ref. 5. residual encoder + TD update run + non-divergent on tiny
  case. 6. FULL => N=8192. ASCII-only. print(flush=True). start-marker + crash-diag + heartbeat.
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

ANCHOR_NAME = "substrate_gen_lm_consolidated_3arm_depth_v4_n8192_gpu"
_N_SUFFIX = 8192; N = 8192; assert N == _N_SUFFIX

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--device", default=None, help="cpu|cuda")
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
print(f"[{'GPU' if DEVICE.type=='cuda' else 'CPU'}] "
      f"{torch.cuda.get_device_name(0) if DEVICE.type=='cuda' else ('torch '+torch.__version__)} dev={DEVICE.type}", flush=True)

VOCAB = 70; K_ACTIVE = 8; LR = 0.5; BATCH = 64
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
CLEANUP_TEMP = 4.0; CLEANUP_STEPS = 6; CLEANUP_ALPHA = 0.5
TD_ALPHA = 0.1; TD_GAMMA = 0.5           # successor-feature TD(0) learning rate + discount
K0_TRUE_ORDER = 2                        # true Markov order of gen_markov2; context beyond this is pure noise
ARMS = ["BASELINE_RAW_BIND", "CA3_CLEANUP_PER_STEP", "CA3_SCRAMBLED", "PREDICT_RESIDUAL_TD", "RESIDUAL_SCRAMBLED"]
ARM_CFG = {
    "BASELINE_RAW_BIND":    dict(enc="raw",   att=None,   train="hebb", scr_resid=False),
    "CA3_CLEANUP_PER_STEP": dict(enc="clean", att="real",  train="hebb", scr_resid=False),
    "CA3_SCRAMBLED":        dict(enc="clean", att="scr",   train="hebb", scr_resid=False),
    "PREDICT_RESIDUAL_TD":  dict(enc="resid", att="real",  train="td",   scr_resid=False),
    "RESIDUAL_SCRAMBLED":   dict(enc="resid", att="real",  train="td",   scr_resid=True),
}
MECH_ARMS = ["CA3_CLEANUP_PER_STEP", "PREDICT_RESIDUAL_TD"]
SCR_OF = {"CA3_CLEANUP_PER_STEP": "CA3_SCRAMBLED", "PREDICT_RESIDUAL_TD": "RESIDUAL_SCRAMBLED"}

if RUN_MODE == "smoke":
    N_DIM = 512; SEEDS = [1]; CORPUS = 6000; N_STEPS = 40; N_TD_STEPS = 40; J = 2
    K_GRID = [2, 3, 5]; M_CTX = 256; N_EVAL = 500
else:
    N_DIM = N; SEEDS = [7, 17, 23]; CORPUS = 40000; N_STEPS = 400; N_TD_STEPS = 200; J = 8
    K_GRID = [1, 2, 3, 5, 8]; M_CTX = 2048; N_EVAL = 2000

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS) * len(K_GRID)
KMAX = max(K_GRID); LN2 = math.log(2.0)


# ---------------------------------------------------------------------------
# error-checking scaffolding
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "device": DEVICE.type, "host": platform.node()}
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
# corpus + codebook (reused from base)
# ---------------------------------------------------------------------------
def gen_markov2(V, length, gen_np):
    nctx = V * V; T = np.zeros((nctx, V))
    for ctx in range(nctx):
        tg = gen_np.choice(V, size=K_ACTIVE, replace=False); lg = gen_np.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[ctx, tg] = w
    ids = np.zeros(length, dtype=np.int64); a, b = 0, 0
    for i in range(length):
        ids[i] = b; nxt = gen_np.choice(V, p=T[a * V + b]); a, b = b, nxt
    return ids


def build_cb(V, n, gen):
    cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def _norm(x):
    return x / (x.norm(dim=1, keepdim=True) + 1e-8)


def _readout(W, ctx):
    return _norm(ctx @ W.t())


# ---------------------------------------------------------------------------
# context encoders
# ---------------------------------------------------------------------------
def enc_raw(cb, ids, starts, K):
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    for j in range(K):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
    return _norm(b)


def _gpu_cleanup(state, CB, temp, max_steps, alpha, tol=1e-3):
    D = state.shape[1]; beta = temp * math.sqrt(D); q0 = state; thr = tol * math.sqrt(D)
    conv = torch.zeros(state.shape[0], dtype=torch.bool, device=DEVICE)
    iters = torch.zeros(state.shape[0], device=DEVICE)
    for _ in range(max_steps):
        scores = beta * (state @ CB.t()); scores = scores - scores.max(dim=1, keepdim=True).values
        w = torch.exp(scores); w = w / (w.sum(dim=1, keepdim=True) + 1e-30)
        est = w @ CB
        new = alpha * q0 + (1.0 - alpha) * est; new = new / (new.norm(dim=1, keepdim=True) + 1e-12)
        step = (new - state).norm(dim=1)
        newly = (~conv) & (step < thr); iters = torch.where(conv, iters, iters + 1.0); conv = conv | newly
        state = new
    cos_near = (state @ CB.t()).max(dim=1).values
    return state, {"converged_frac": float(conv.float().mean()), "mean_iters": float(iters.mean()),
                   "mean_cos_to_attractor": float(cos_near.mean())}


def enc_cleanup(cb, ids, starts, K, attractors):
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE); cf = []; mi = []; mc = []
    for j in range(K):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
        bn, d = _gpu_cleanup(_norm(b), attractors[j], CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA)
        cf.append(d["converged_frac"]); mi.append(d["mean_iters"]); mc.append(d["mean_cos_to_attractor"]); b = bn
    return _norm(b), {"converged_frac": float(np.mean(cf)), "mean_iters": float(np.mean(mi)),
                      "mean_cos_to_attractor": float(np.mean(mc)), "mean_resid_norm": None}


def enc_residual(cb, ids, starts, K, attractors, W, scr_resid, gen=None):
    """Predictive-coding accumulation: inject only the bounded residual (actual - W-predicted) per step,
    with per-step CA3 cleanup. scr_resid=True replaces residual with a structureless random vector (control)."""
    B = starts.shape[0]; Ndim = cb.shape[1]
    c = torch.zeros(B, Ndim, device=DEVICE); cf = []; mi = []; mc = []; rn = []
    for j in range(K):
        cprev = _norm(c)
        pred = _readout(W, cprev)                       # predicted next-token direction (0 at j=0 when W=0)
        actual = cb[ids[starts + j]]
        if scr_resid:
            r = torch.randn(B, Ndim, generator=gen, device=DEVICE) if gen is not None else torch.randn(B, Ndim, device=DEVICE)
            resid = _norm(r)
        else:
            resid = actual - pred                       # predictive-coding error (bounded when pred is good)
        rn.append(float(resid.norm(dim=1).mean()))
        c = torch.roll(c, shifts=1, dims=1) + resid
        cn, d = _gpu_cleanup(_norm(c), attractors[j], CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA)
        cf.append(d["converged_frac"]); mi.append(d["mean_iters"]); mc.append(d["mean_cos_to_attractor"]); c = cn
    return _norm(c), {"converged_frac": float(np.mean(cf)), "mean_iters": float(np.mean(mi)),
                      "mean_cos_to_attractor": float(np.mean(mc)), "mean_resid_norm": float(np.mean(rn))}


def build_ctx_attractors(cb, tr, K_max, m_ctx, gen, scramble=False):
    atts = []
    for d in range(1, K_max + 1):
        st = torch.randint(0, len(tr) - K_max - 1, (m_ctx,), generator=gen, device=DEVICE)
        ctx = enc_raw(cb, tr, st, d)
        if scramble:
            r = torch.randn(ctx.shape, generator=gen, device=DEVICE); ctx = _norm(r)
        atts.append(ctx)
    return atts


def _encode(mode, cb, ids, starts, K, attractors, W, scr_resid):
    if mode == "raw":
        return enc_raw(cb, ids, starts, K), {"converged_frac": None, "mean_resid_norm": None}
    if mode == "clean":
        return enc_cleanup(cb, ids, starts, K, attractors)
    return enc_residual(cb, ids, starts, K, attractors, W, scr_resid)


# ---------------------------------------------------------------------------
# readout training: Hebbian (raw/clean) and TD-bootstrap successor-feature (residual)
# ---------------------------------------------------------------------------
def train_hebb(n, cb, tr, K, enc_mode, attractors, gen):
    W = torch.zeros(n, n, device=DEVICE)
    for _ in range(N_STEPS):
        st = torch.randint(0, len(tr) - KMAX - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx, _ = _encode(enc_mode, cb, tr, st, K, attractors, W, False)
        nxt = cb[tr[st + K]]
        W = W + LR * (nxt.t() @ ctx) / BATCH
    return W, {"td_diverged": False, "w_norm_final": float(W.norm()), "w_norm_trace": []}


def train_td(n, cb, tr, K, attractors, scr_resid, gen):
    """SR/successor-feature TD(0): W <- W + alpha*(target - W ctx) outer ctx, target = phi(next)+gamma*W ctx'."""
    W = torch.zeros(n, n, device=DEVICE); trace = []
    diverged = False
    for step in range(N_TD_STEPS):
        st = torch.randint(0, len(tr) - KMAX - 2, (BATCH,), generator=gen, device=DEVICE)
        ctx, _ = enc_residual(cb, tr, st, K, attractors, W, scr_resid, gen)
        ctx_next, _ = enc_residual(cb, tr, st + 1, K, attractors, W, scr_resid, gen)
        target = cb[tr[st + K]] + TD_GAMMA * (ctx_next @ W.t())
        td_err = target - (ctx @ W.t())
        W = W + TD_ALPHA * (td_err.t() @ ctx) / BATCH
        if step % max(1, N_TD_STEPS // 10) == 0:
            wn = float(W.norm()); trace.append(wn)
            if not math.isfinite(wn) or wn > 1e7:
                diverged = True; break
    return W, {"td_diverged": diverged, "w_norm_final": float(W.norm()), "w_norm_trace": trace}


def eval_arm(Ws, cb, va, K, enc_mode, attractors, scr_resid):
    nb = min(N_EVAL, len(va) - KMAX - 1); st = torch.arange(nb, device=DEVICE); nxt = va[st + K]
    diags = []
    ctxs = []
    for W in Ws:
        ctx, diag = _encode(enc_mode, cb, va, st, K, attractors, W, scr_resid); ctxs.append(ctx); diags.append(diag)
    best_nats = float("inf"); best_argmax = None
    for t in TEMP_GRID:
        Ps = []
        for W, ctx in zip(Ws, ctxs):
            pred = _norm(ctx @ W.t()); cos = pred @ cb.t()
            z = cos / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
            Ps.append(ez / (ez.sum(dim=1, keepdim=True) + 1e-30))
        P = torch.stack(Ps).mean(0); pt = P[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        nats = float((-torch.log(pt)).mean())
        if nats < best_nats:
            best_nats = nats; best_argmax = P.argmax(dim=1)
    cf = [d["converged_frac"] for d in diags if d["converged_frac"] is not None]
    rnv = [d["mean_resid_norm"] for d in diags if d.get("mean_resid_norm") is not None]
    return {"bpc_nats": best_nats, "bpc_bits": best_nats / LN2, "perplexity": math.exp(best_nats),
            "top1": float((best_argmax == nxt).float().mean()),
            "distinct_token_rate": float(torch.unique(best_argmax).numel()) / float(VOCAB),
            "cleanup_converged_frac": (float(np.mean(cf)) if cf else None),
            "mean_resid_norm": (float(np.mean(rnv)) if rnv else None)}


def count_baselines(ids, sp):
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
            "bigram_count_bpc_bits": math.log(big) / LN2, "trigram_count_bpc_bits": math.log(tri) / LN2,
            "unigram_bpc_bits": math.log(uni) / LN2}


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------
def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0); cb = build_cb(7, 128, gen)
    s = torch.tensor([0, 1, 2, 3], device=DEVICE)
    b1 = enc_raw(cb, s, torch.tensor([0], device=DEVICE), 3)
    b2 = enc_raw(cb, torch.tensor([2, 1, 0, 3], device=DEVICE), torch.tensor([0], device=DEVICE), 3)
    assert float((b1 * b2).sum()) < 0.95, "roll-bind not order-sensitive"
    W = torch.zeros(128, 128, device=DEVICE); ctx = enc_raw(cb, s, torch.tensor([0], device=DEVICE), 3); nxt = cb[3]
    W = W + torch.outer(nxt, ctx.squeeze(0)); pred = W @ ctx.squeeze(0)
    assert float(pred @ nxt / (pred.norm() * nxt.norm() + 1e-8)) > 0.5, "K3 recall"
    assert abs(math.exp(1.6094) - 5.0) < 0.01 and abs((math.log(5.0) / LN2) - 2.3219) < 0.01, "ppl/bpc formula"
    # gpu_cleanup matches numpy iterative_attractor reference
    from hdlab.iterative_attractor import iterative_cleanup as np_clean
    g2 = np.random.default_rng(3); M, D = 32, 256
    cbn = g2.standard_normal((M, D)).astype(np.float32); cbn = cbn / (np.linalg.norm(cbn, axis=1, keepdims=True) + 1e-12)
    cbt = torch.tensor(cbn, device=DEVICE)
    for i in [0, 5, 17]:
        cue = cbn[i] + 0.05 * g2.standard_normal(D).astype(np.float32)
        r_np = np_clean(cue.copy(), cbn, temp=8.0, max_steps=6, alpha=0.5)
        stt = _norm(torch.tensor(cue[None, :], device=DEVICE)); s_gpu, _ = _gpu_cleanup(stt, cbt, 8.0, 6, 0.5)
        assert int((s_gpu @ cbt.t()).argmax(dim=1)[0]) == int(r_np["argmax_idx"]) == i, f"gpu_cleanup mismatch i={i}"
    # residual encoder + TD update run + non-divergent on a tiny synthetic corpus
    gn = np.random.default_rng(1); ids = gen_markov2(VOCAB, 400, gn); tr = torch.tensor(ids, device=DEVICE)
    cb2 = build_cb(VOCAB, 128, torch.Generator(device=DEVICE).manual_seed(2))
    att = build_ctx_attractors(cb2, tr, 3, 64, torch.Generator(device=DEVICE).manual_seed(3))
    Wt, d = train_td(128, cb2, tr, 3, att, False, torch.Generator(device=DEVICE).manual_seed(4))
    assert not d["td_diverged"] and math.isfinite(d["w_norm_final"]), f"TD diverged in selftest: {d}"
    ec, ed = enc_residual(cb2, tr, torch.tensor([0, 1], device=DEVICE), 3, att, Wt, False)
    assert ec.shape == (2, 128) and ed["mean_resid_norm"] is not None, "residual encoder shape/diag"
    assert N == 8192
    print("[selftest] PASS: rollbind K3recall ppl/bpc gpu_cleanup==npref residual+TD-nondiverge N8192", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE).manual_seed(seed); gen_np = np.random.default_rng(seed + 99)
    ids = gen_markov2(VOCAB, CORPUS, gen_np); sp = int(0.8 * len(ids))
    tr = torch.tensor(ids[:sp], device=DEVICE); va = torch.tensor(ids[sp:], device=DEVICE)
    cb = build_cb(VOCAB, n_dim, gen)
    att_real = build_ctx_attractors(cb, tr, KMAX, M_CTX, torch.Generator(device=DEVICE).manual_seed(seed * 7 + 1), False)
    att_scr = build_ctx_attractors(cb, tr, KMAX, M_CTX, torch.Generator(device=DEVICE).manual_seed(seed * 7 + 2), True)
    idx = np.array_split(np.arange(len(tr)), J)
    per_unit = []
    for arm in ARMS:
        cfg = ARM_CFG[arm]
        attractors = att_scr if cfg["att"] == "scr" else (att_real if cfg["att"] == "real" else None)
        for K in K_GRID:
            Ws = []; tdiag = {"td_diverged": False, "w_norm_final": None}
            for i in range(J):
                g = torch.Generator(device=DEVICE).manual_seed(seed * 50 + i * 3 + 1)
                if cfg["train"] == "td":
                    W, tdiag = train_td(n_dim, cb, tr[torch.tensor(idx[i], device=DEVICE)], K, attractors, cfg["scr_resid"], g)
                else:
                    W, tdiag = train_hebb(n_dim, cb, tr[torch.tensor(idx[i], device=DEVICE)], K, cfg["enc"], attractors, g)
                Ws.append(W)
            m = eval_arm(Ws, cb, va, K, cfg["enc"], attractors, cfg["scr_resid"])
            m.update({"seed": seed, "arm": arm, "K": K, "N": n_dim, "J": J,
                      "td_diverged": bool(tdiag["td_diverged"]), "w_norm_final": tdiag["w_norm_final"]})
            per_unit.append(m)
            print(f"    [{arm} K={K}] bpc_bits={m['bpc_bits']:.3f} ppl={m['perplexity']:.1f} top1={m['top1']:.3f} "
                  f"conv={m['cleanup_converged_frac']} resid_norm={m['mean_resid_norm']} tdiv={m['td_diverged']}", flush=True)
    base = count_baselines(ids, sp)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    return {"seed": seed, "N": n_dim, "J": J, "per_unit": per_unit, "baselines": base,
            "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


# ---------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------
def _curve(all_results, arm, field="bpc_bits"):
    out = {}
    for K in K_GRID:
        vals = [u[field] for r in all_results for u in r["per_unit"] if u["arm"] == arm and u["K"] == K]
        out[K] = float(np.mean(vals)) if vals else float("nan")
    return out


def compute_verdict(all_results) -> Tuple[str, str]:
    if not all_results:
        return ("HARD_FAIL", "no results")
    n_units = sum(len(r["per_unit"]) for r in all_results)
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {n_units} < {EXPECTED_N_UNITS}")
    K0 = K0_TRUE_ORDER if K0_TRUE_ORDER in K_GRID else K_GRID[0]
    curves = {a: _curve(all_results, a) for a in ARMS}
    d = {a: curves[a][KMAX] - curves[a][K0] for a in ARMS}
    gap = {a: curves["BASELINE_RAW_BIND"][KMAX] - curves[a][KMAX] for a in ARMS}  # positive = arm better than baseline
    conv = {a: float(np.mean([u["cleanup_converged_frac"] for r in all_results for u in r["per_unit"]
                              if u["arm"] == a and u["cleanup_converged_frac"] is not None] or [1.0])) for a in MECH_ARMS}
    tdiv = any(u["td_diverged"] for r in all_results for u in r["per_unit"])
    b = float(np.mean([r["baselines"]["bigram_count_bpc_bits"] for r in all_results]))
    summ = (f"K0={K0} Kmax={KMAX} | " + " ".join(
        f"{a}:d={d[a]:+.3f},gap={gap[a]:+.3f}" for a in ARMS) +
        f" | conv={ {k: round(v,2) for k,v in conv.items()} } td_diverged={tdiv} bigram_bpc={b:.3f} "
        f"curves={ {a: {k: round(v,3) for k,v in curves[a].items()} for a in ARMS} }")
    if d["BASELINE_RAW_BIND"] <= 0.0:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_DISCRIMINATOR_DID_NOT_FIRE: BASELINE does not degrade past true order "
                f"(dBASE={d['BASELINE_RAW_BIND']:+.3f}); synthetic corpus does not reproduce context-hurts-with-depth "
                f"-> leans capacity/real-text-specific. Re-spec (real text) to fire. {summ}")
    # HARD_PASS: a mechanism arm flattens + beats baseline + scramble does not replicate + (residual) not diverged
    for a in MECH_ARMS:
        scr = SCR_OF[a]; not_repl = (d[scr] - d[a]) >= 0.15
        ok_att1 = conv[a] >= 0.80
        ok_td = (not tdiv) if a == "PREDICT_RESIDUAL_TD" else True
        if d[a] <= 0.0 and gap[a] >= 0.30 and not_repl and ok_att1 and ok_td:
            return ("HARD_PASS", f"HARD_PASS via {a}: non-increasing past true order + beats baseline at Kmax by "
                    f">=0.30 bits + scramble does not replicate + healthy => NOISE-COMPOUNDING confirmed+fixed "
                    f"({'DEEP' if a=='PREDICT_RESIDUAL_TD' else 'SHALLOW'} mechanism wins). {summ}")
    # MIDDLE: some mechanism partially flattens vs baseline
    if any(d[a] < d["BASELINE_RAW_BIND"] for a in MECH_ARMS):
        winner = min(MECH_ARMS, key=lambda a: d[a])
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {winner} partially flattens depth-degradation "
                f"(d={d[winner]:+.3f} < dBASE={d['BASELINE_RAW_BIND']:+.3f}) but not full pass. {summ}")
    return ("HARD_FAIL", f"HARD_FAIL: neither mechanism changes the depth-degradation "
            f"(dCA3={d['CA3_CLEANUP_PER_STEP']:+.3f}, dRESID={d['PREDICT_RESIDUAL_TD']:+.3f} both >= "
            f"dBASE={d['BASELINE_RAW_BIND']:+.3f}) => CAPACITY CEILING not noise-compounding; redirect to "
            f"disjoint-block context representation. td_diverged={tdiv}. {summ}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} dev={DEVICE.type} seeds={SEEDS} N={N_DIM} J={J} "
          f"K_GRID={K_GRID} arms={ARMS} M_CTX={M_CTX} N_TD_STEPS={N_TD_STEPS} expected_units={EXPECTED_N_UNITS}", flush=True)
    if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL must run on cuda")
    out_dir = get_output_dir(ANCHOR_NAME); _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "J": J, "arms": ARMS, "K_GRID": K_GRID})
    for seed in remaining:
        print(f"[seed={seed}] ...", flush=True); t0 = time.time(); r = run_seed(seed, N_DIM); r["elapsed_s"] = time.time() - t0
        print(f"  seed={seed} done ({r['elapsed_s']:.0f}s)", flush=True); write_partial(out_dir, seed, r)
    all_results = list(aggregate_partials(out_dir, SEEDS).values())
    # ARMS-MUST-DIFFER (META_RULE_AF)
    digs = {a: hashlib.sha256(json.dumps({k: round(v, 6) for k, v in _curve(all_results, a).items()}).encode()).hexdigest() for a in ARMS}
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
               "run_mode": RUN_MODE, "device": DEVICE.type, "n_seeds": len(SEEDS), "expected_n_units": EXPECTED_N_UNITS,
               "arm_digests": digs, "per_seed": all_results, "curves": {a: _curve(all_results, a) for a in ARMS}}
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
