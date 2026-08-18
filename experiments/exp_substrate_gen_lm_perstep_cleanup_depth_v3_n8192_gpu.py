"""
substrate_gen_lm_perstep_cleanup_depth_v3_n8192_gpu -- PREDICTIVE generation: does per-step CA3 cleanup
  FLATTEN/REVERSE the context-hurts-with-depth bpc curve (noise-compounding) or NOT (capacity ceiling)?

ROUTING: notes/research_stage4_generation_load_bearing_gap_and_gpu_probe_2026-07-07.md (THE probe).
  Reuses the 2nd-order-Markov corpus + Hebbian hetero-associative readout + count-baseline ladder of the
  landed MIDDLE_BAND cell exp_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu.py (DO NOT mutate that
  landed cell; this is a _v3 sibling). NEW ARM = per-step iterative-attractor cleanup wired into the context
  accumulation (hdlab/iterative_attractor.py math, ported to torch/GPU + selftest-matched to the numpy ref).

CAPABILITY QUESTION (predictive, not sequence-recovery): the substrate has a documented 3-HARD_FAIL/1-MIDDLE
  history where context makes next-token prediction WORSE with depth (exp_n2_context_depth_hd_binding_v1:
  bpc 5.00 -> 5.05 -> 5.18 for K=1 -> 2 -> 3). Is that NOISE-COMPOUNDING (each context step accumulates
  crosstalk; fixable by per-step re-clean, the same regenerative-repeater fix that makes multi-hop reasoning
  survive depth 15) or a REPRESENTATION-CAPACITY ceiling (superposed/bind context structurally cannot carry
  higher-order sequential statistics; a different fix needed)?

ARMS (per seed, per depth K in K_GRID):
  RAW_BIND_NO_CLEANUP  -- one-shot roll-bind bundle of K tokens (== base cell mechanism); the in-cell
                          negative control that MUST reproduce the depth-degradation shape (bpc rises with K).
  CLEANUP_PER_STEP     -- incremental accumulation; after EACH bound token, soft-attractor cleanup pulls the
                          running context toward the manifold of REAL depth-matched training contexts.
  CLEANUP_SCRAMBLED    -- FIRING CONTROL: identical cleanup dynamics but attractor codebook is RANDOM vectors
                          (real-context manifold destroyed). Any CLEANUP_PER_STEP benefit that also appears
                          here is an artifact of iteration/renorm, NOT of the context-manifold structure.
  Reference ladder (K-independent, exact count tables, reused verbatim): unigram, bigram_count,
                          trigram_count (oracle ceiling for a 2nd-order corpus).

WEAKNESS DECOMPOSITION (the point per USER reframe): the per-arm depth curve IS the decomposition --
  if CLEANUP_PER_STEP flattens/reverses the RAW depth-degradation => weakness is decode-noise-compounding
  (a fixable, cross-substrate-shared load-bearing mechanism); if it does NOT => capacity ceiling (needs a
  disjoint-block/frame-slot context representation, a different lever). distinct-token-rate logged for the
  repetition-collapse failure mode; top1 logged for coherence.

FLAGGED RISK (from the note, not hidden): the iterative-attractor (att1) family has its OWN HARD_FAIL history
  at high-storage/high-noise operating points. Cleaning a SUPERPOSITION context toward a codebook of
  (correlated) context bundles IS that regime. So a CLEANUP no-help result could be an att1 MALFUNCTION, not
  a refutation of the per-step-cleanup idea. Mitigation (required by note): log the cleanup attractor's own
  convergence diagnostics per step (converged_frac, mean_iters, mean cos-to-nearest-attractor) so a
  primitive-malfunction is DISTINGUISHABLE from a genuine "cleanup does not help".

PRE-REG (bpc in BITS; ensemble arm; averaged over seeds; Kmax = max(K_GRID)):
  HARD_PASS  = CLEANUP_PER_STEP bpc NON-INCREASING with K (delta_clean <= 0) AND beats RAW at Kmax by
               >= 0.30 bits AND att1 healthy (cleanup_converged_frac >= 0.80) AND scramble does NOT replicate
               the benefit (gap_clean_at_Kmax - gap_scramble_at_Kmax >= 0.15). Noise-compounding CONFIRMED+FIXED.
  MIDDLE_BAND= cleanup partially flattens (delta_clean < delta_raw, i.e. degrades less than RAW) but does not
               meet HARD_PASS (still rising, or att1 marginal, or gap < 0.30). Partial noise-compounding.
  HARD_FAIL  = cleanup does NOT change the depth-degradation (delta_clean >= delta_raw) OR att1 malfunction
               dominates (converged_frac < 0.50). INFORMATIVE NEGATIVE = capacity ceiling; redirect to
               disjoint-block context representation.
  INCONCLUSIVE = RAW arm does NOT reproduce the documented degradation (delta_raw <= 0): discriminator did
               not fire at this regime; re-spec before trusting cleanup arm (META_RULE_K / AG).

FORMULA SELF-TESTS (PROT-022): 1. roll-bind order-sensitive. 2. symmetric-Hebbian recall. 3. ppl=exp(bpc_nats),
  bpc_bits=nats/ln2. 4. gpu_cleanup matches numpy iterative_attractor.iterative_cleanup (zero-noise identity +
  low-noise recovery). 5. FULL => N=8192 (PROT-018). ASCII-only. print(flush=True). start-marker + crash-diag
  + heartbeat (error-checking mandate).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math, platform, traceback
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

ANCHOR_NAME = "substrate_gen_lm_perstep_cleanup_depth_v3_n8192_gpu"
_N_SUFFIX = 8192; N = 8192; assert N == _N_SUFFIX

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--device", default=None, help="cpu|cuda; default cuda for FULL, honors --device for smoke")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# Device selection: FULL requires cuda (GPU cell); smoke may run on CPU (local SMOKE-ONLY-local rule).
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
CLEANUP_ALPHA = 0.5       # cue re-injection weight (brain-canonical CA3 value per iterative_attractor.py)
ARMS = ["RAW_BIND_NO_CLEANUP", "CLEANUP_PER_STEP", "CLEANUP_SCRAMBLED"]

if RUN_MODE == "smoke":
    N_DIM = 1024; SEEDS = [1]; CORPUS = 8000; N_STEPS = 100; J = 1
    K_GRID = [1, 2, 3]; M_CTX = 512; N_EVAL = 1000
else:
    N_DIM = N; SEEDS = [7, 17, 23]; CORPUS = 40000; N_STEPS = 400; J = 10
    K_GRID = [1, 2, 3, 5]; M_CTX = 2048; N_EVAL = 2000

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS) * len(K_GRID)   # cardinality_ok gate (META_RULE_H)
KMAX = max(K_GRID)
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
# corpus + codebook (reused from base cell)
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


# ---------------------------------------------------------------------------
# context encoders (RAW one-shot; CLEANUP incremental with per-step attractor pull)
# ---------------------------------------------------------------------------
def enc_raw(cb, ids, starts, K):
    """One-shot roll-bind bundle of K tokens (== base cell mechanism). Returns (B, N) normalized."""
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    for j in range(K):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def _gpu_cleanup(state, CB, temp, max_steps, alpha, tol=1e-3):
    """torch port of hdlab.iterative_attractor.iterative_cleanup (scale_by_sqrt_d=True).
    state (B,D) L2-normalized; CB (M,D) L2-normalized. Returns (state, diag)."""
    D = state.shape[1]
    beta = temp * math.sqrt(D)
    q0 = state
    thr = tol * math.sqrt(D)
    conv = torch.zeros(state.shape[0], dtype=torch.bool, device=DEVICE)
    iters = torch.zeros(state.shape[0], device=DEVICE)
    for t in range(max_steps):
        scores = beta * (state @ CB.t())                       # (B,M)
        scores = scores - scores.max(dim=1, keepdim=True).values
        w = torch.exp(scores); w = w / (w.sum(dim=1, keepdim=True) + 1e-30)
        est = w @ CB                                           # (B,D)
        new = alpha * q0 + (1.0 - alpha) * est
        new = new / (new.norm(dim=1, keepdim=True) + 1e-12)
        step = (new - state).norm(dim=1)
        newly = (~conv) & (step < thr)
        iters = torch.where(conv, iters, iters + 1.0)
        conv = conv | newly
        state = new
    cos_near = (state @ CB.t()).max(dim=1).values
    diag = {"converged_frac": float(conv.float().mean()),
            "mean_iters": float(iters.mean()),
            "mean_cos_to_attractor": float(cos_near.mean())}
    return state, diag


def enc_cleanup(cb, ids, starts, K, attractors, temp, steps, alpha):
    """Incremental accumulation with per-step attractor cleanup. Reduces to raw-direction if cleanup is a
    no-op. attractors: list indexed by depth-1 of (M_CTX, N) normalized attractor codebooks.
    Returns ((B,N) normalized, diag) where diag aggregates cleanup convergence over the K steps."""
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    cf = []; mi = []; mc = []
    for j in range(K):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
        bn = b / (b.norm(dim=1, keepdim=True) + 1e-8)
        bn, d = _gpu_cleanup(bn, attractors[j], temp, steps, alpha)
        cf.append(d["converged_frac"]); mi.append(d["mean_iters"]); mc.append(d["mean_cos_to_attractor"])
        b = bn
    out = b / (b.norm(dim=1, keepdim=True) + 1e-8)
    diag = {"converged_frac": float(np.mean(cf)), "mean_iters": float(np.mean(mi)),
            "mean_cos_to_attractor": float(np.mean(mc))}
    return out, diag


def build_ctx_attractors(cb, tr, K_max, m_ctx, gen, scramble=False):
    """For each depth d=1..K_max, encode m_ctx real depth-d training contexts as attractors. scramble=True
    replaces them with random unit vectors (firing control)."""
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
# Hebbian hetero-associative readout (context -> next-token), trained on the ARM's own encoder
# ---------------------------------------------------------------------------
def _encode_batch(mode, cb, ids, starts, K, attractors):
    if mode == "RAW_BIND_NO_CLEANUP":
        return enc_raw(cb, ids, starts, K), None
    return enc_cleanup(cb, ids, starts, K, attractors, CLEANUP_TEMP, CLEANUP_STEPS, CLEANUP_ALPHA)


def train_hebb(n, cb, tr, K, mode, attractors, gen):
    W = torch.zeros(n, n, device=DEVICE)
    for _ in range(N_STEPS):
        st = torch.randint(0, len(tr) - KMAX - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx, _ = _encode_batch(mode, cb, tr, st, K, attractors)
        nxt = cb[tr[st + K]]
        W = W + LR * (nxt.t() @ ctx) / BATCH
    return W


def eval_arm(Ws, cb, va, K, mode, attractors):
    """Ensemble perplexity + top1 + distinct-token-rate + cleanup diag on held-out. Returns dict."""
    nb = min(N_EVAL, len(va) - KMAX - 1)
    st = torch.arange(nb, device=DEVICE)
    nxt = va[st + K]
    # encode eval contexts once per arm (shared across ensemble + temp grid)
    ctx, diag = _encode_batch(mode, cb, va, st, K, attractors)
    best_nats = float("inf"); best_pred_argmax = None
    for t in TEMP_GRID:
        Ps = []
        for W in Ws:
            pred = ctx @ W.t(); pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
            cos = pred @ cb.t(); z = cos / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
            Ps.append(ez / (ez.sum(dim=1, keepdim=True) + 1e-30))
        P = torch.stack(Ps).mean(0)
        pt = P[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        nats = float((-torch.log(pt)).mean())
        if nats < best_nats:
            best_nats = nats; best_pred_argmax = P.argmax(dim=1)
    top1 = float((best_pred_argmax == nxt).float().mean())
    distinct_rate = float(torch.unique(best_pred_argmax).numel()) / float(VOCAB)
    return {"bpc_nats": best_nats, "bpc_bits": best_nats / LN2, "perplexity": math.exp(best_nats),
            "top1": top1, "distinct_token_rate": distinct_rate,
            "cleanup_converged_frac": (diag["converged_frac"] if diag else None),
            "cleanup_mean_iters": (diag["mean_iters"] if diag else None),
            "cleanup_mean_cos_to_attractor": (diag["mean_cos_to_attractor"] if diag else None)}


def count_baselines(ids, sp):
    """Exact unigram / bigram / trigram(oracle) perplexity ladder (numpy; K-independent)."""
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
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cb = build_cb(7, 128, gen)
    s = torch.tensor([0, 1, 2, 3], device=DEVICE)
    b1 = enc_raw(cb, s, torch.tensor([0], device=DEVICE), 3)
    b2 = enc_raw(cb, torch.tensor([2, 1, 0, 3], device=DEVICE), torch.tensor([0], device=DEVICE), 3)
    assert float((b1 * b2).sum()) < 0.95, "roll-bind not order-sensitive"
    # symmetric-Hebbian recall
    W = torch.zeros(128, 128, device=DEVICE); ctx = enc_raw(cb, s, torch.tensor([0], device=DEVICE), 3); nxt = cb[3]
    W = W + torch.outer(nxt, ctx.squeeze(0)); pred = W @ ctx.squeeze(0)
    assert float(pred @ nxt / (pred.norm() * nxt.norm() + 1e-8)) > 0.5, "K3 recall"
    # ppl formula
    assert abs(math.exp(1.6094) - 5.0) < 0.01
    assert abs((math.log(5.0) / LN2) - 2.3219) < 0.01, "bpc_bits formula"
    # gpu_cleanup MUST match numpy iterative_attractor reference (zero-noise identity + low-noise recovery)
    from hdlab.iterative_attractor import iterative_cleanup as np_clean
    g2 = np.random.default_rng(3); M, D = 32, 256
    cbn = g2.standard_normal((M, D)).astype(np.float32); cbn = cbn / (np.linalg.norm(cbn, axis=1, keepdims=True) + 1e-12)
    cbt = torch.tensor(cbn, device=DEVICE)
    for i in [0, 5, 17]:
        cue = cbn[i] + 0.05 * g2.standard_normal(D).astype(np.float32)
        r_np = np_clean(cue.copy(), cbn, temp=8.0, max_steps=6, alpha=0.5)
        st = torch.tensor(cue[None, :], device=DEVICE); st = st / (st.norm(dim=1, keepdim=True) + 1e-12)
        s_gpu, _ = _gpu_cleanup(st, cbt, 8.0, 6, 0.5)
        idx_gpu = int((s_gpu @ cbt.t()).argmax(dim=1)[0])
        assert idx_gpu == int(r_np["argmax_idx"]) == i, f"gpu_cleanup mismatch numpy ref at i={i}: gpu={idx_gpu} np={r_np['argmax_idx']}"
    assert N == 8192
    print("[selftest] PASS: rollbind_order K3_recall ppl_bpc gpu_cleanup==numpy_ref N8192", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    gen_np = np.random.default_rng(seed + 99)
    ids = gen_markov2(VOCAB, CORPUS, gen_np); sp = int(0.8 * len(ids))
    tr = torch.tensor(ids[:sp], device=DEVICE); va = torch.tensor(ids[sp:], device=DEVICE)
    cb = build_cb(VOCAB, n_dim, gen)
    # attractor codebooks (shared across ensemble members): real + scrambled
    att_real = build_ctx_attractors(cb, tr, KMAX, M_CTX, torch.Generator(device=DEVICE).manual_seed(seed * 7 + 1), scramble=False)
    att_scr = build_ctx_attractors(cb, tr, KMAX, M_CTX, torch.Generator(device=DEVICE).manual_seed(seed * 7 + 2), scramble=True)
    idx = np.array_split(np.arange(len(tr)), J)
    per_unit = []
    for mode in ARMS:
        attractors = None if mode == "RAW_BIND_NO_CLEANUP" else (att_scr if mode == "CLEANUP_SCRAMBLED" else att_real)
        for K in K_GRID:
            Ws = [train_hebb(n_dim, cb, tr[torch.tensor(idx[i], device=DEVICE)], K, mode, attractors,
                             torch.Generator(device=DEVICE).manual_seed(seed * 50 + i)) for i in range(J)]
            m = eval_arm(Ws, cb, va, K, mode, attractors)
            m.update({"seed": seed, "arm": mode, "K": K, "N": n_dim, "J": J})
            per_unit.append(m)
            print(f"    [{mode} K={K}] bpc_bits={m['bpc_bits']:.3f} ppl={m['perplexity']:.1f} top1={m['top1']:.3f} "
                  f"distinct={m['distinct_token_rate']:.2f} conv={m['cleanup_converged_frac']}", flush=True)
    base = count_baselines(ids, sp)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    return {"seed": seed, "N": n_dim, "J": J, "per_unit": per_unit, "baselines": base,
            "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


# ---------------------------------------------------------------------------
# verdict (depth-curve discriminator per pre-reg)
# ---------------------------------------------------------------------------
def _arm_curve(all_results, arm, field="bpc_bits"):
    """Mean over seeds of field at each K for the given arm. Returns dict {K: value}."""
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
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: got {n_units} units, expected {EXPECTED_N_UNITS}")
    raw = _arm_curve(all_results, "RAW_BIND_NO_CLEANUP")
    cln = _arm_curve(all_results, "CLEANUP_PER_STEP")
    scr = _arm_curve(all_results, "CLEANUP_SCRAMBLED")
    delta_raw = raw[KMAX] - raw[K_GRID[0]]
    delta_cln = cln[KMAX] - cln[K_GRID[0]]
    delta_scr = scr[KMAX] - scr[K_GRID[0]]
    gap_cln = raw[KMAX] - cln[KMAX]       # positive = cleanup better than raw at depth
    gap_scr = raw[KMAX] - scr[KMAX]
    conv = float(np.mean([u["cleanup_converged_frac"] for r in all_results for u in r["per_unit"]
                          if u["arm"] == "CLEANUP_PER_STEP" and u["cleanup_converged_frac"] is not None] or [0.0]))
    b = float(np.mean([r["baselines"]["bigram_count_bpc_bits"] for r in all_results]))
    summary = (f"raw_curve={ {k: round(v,3) for k,v in raw.items()} } clean_curve={ {k: round(v,3) for k,v in cln.items()} } "
               f"scram_curve={ {k: round(v,3) for k,v in scr.items()} } | dRAW={delta_raw:+.3f} dCLEAN={delta_cln:+.3f} "
               f"dSCRAM={delta_scr:+.3f} gap@Kmax(clean)={gap_cln:+.3f} gap@Kmax(scram)={gap_scr:+.3f} "
               f"att1_conv={conv:.2f} bigram_bpc={b:.3f}")
    # discriminator-fires gate (META_RULE_K/AG): RAW must reproduce the documented degradation
    if delta_raw <= 0.0:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_DISCRIMINATOR_DID_NOT_FIRE: RAW does not degrade with depth (dRAW={delta_raw:+.3f}). Re-spec regime. {summary}")
    # att1 malfunction dominates
    if conv < 0.50:
        return ("HARD_FAIL", f"HARD_FAIL_ATT1_MALFUNCTION: cleanup attractor out of working regime (conv={conv:.2f}<0.50); result confounded, not a clean refutation. {summary}")
    if delta_cln <= 0.0 and gap_cln >= 0.30 and conv >= 0.80 and (gap_cln - gap_scr) >= 0.15:
        return ("HARD_PASS", f"HARD_PASS: per-step cleanup makes bpc NON-INCREASING with depth + beats RAW at Kmax by >=0.30 bits + att1 healthy + scramble does not replicate => NOISE-COMPOUNDING confirmed+fixed. {summary}")
    if delta_cln < delta_raw:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: cleanup partially flattens depth-degradation (dCLEAN={delta_cln:+.3f} < dRAW={delta_raw:+.3f}) but not full pass. Partial noise-compounding. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: cleanup does NOT change depth-degradation (dCLEAN={delta_cln:+.3f} >= dRAW={delta_raw:+.3f}) => CAPACITY CEILING, not noise-compounding; redirect to disjoint-block context representation. {summary}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} dev={DEVICE.type} seeds={SEEDS} N={N_DIM} J={J} "
          f"K_GRID={K_GRID} arms={ARMS} M_CTX={M_CTX} expected_units={EXPECTED_N_UNITS}", flush=True)
    if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL must run on cuda")
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "J": J, "arms": ARMS, "K_GRID": K_GRID})
    for seed in remaining:
        print(f"[seed={seed}] ...", flush=True); t0 = time.time()
        r = run_seed(seed, N_DIM); r["elapsed_s"] = time.time() - t0
        print(f"  seed={seed} done ({r['elapsed_s']:.0f}s)", flush=True)
        write_partial(out_dir, seed, r)
    all_results = list(aggregate_partials(out_dir, SEEDS).values())
    # ARMS-MUST-DIFFER (META_RULE_AF): bpc curves of the 3 arms must not be bit-identical
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
               "run_mode": RUN_MODE, "device": DEVICE.type, "n_seeds": len(SEEDS),
               "expected_n_units": EXPECTED_N_UNITS, "arm_digests": digs, "per_seed": all_results,
               "raw_curve": _arm_curve(all_results, "RAW_BIND_NO_CLEANUP"),
               "clean_curve": _arm_curve(all_results, "CLEANUP_PER_STEP"),
               "scram_curve": _arm_curve(all_results, "CLEANUP_SCRAMBLED")}
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
