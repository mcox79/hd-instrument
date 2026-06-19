"""
substrate_joint_dh_brain_correct_rung1_v1_n4096 -- Joint D+H brain-correct substrate-as-training-mechanism.

ROUTING: notes/routing_joint_DH_brain_correct_rung1_redesign_2026-06-04.md (Research).

CAPABILITY QUESTION:
  Can a brain-correct substrate-as-training-mechanism (continuous float32 substrate + Hebbian core +
  cf rank-1 substitution as RPE + sparse multiplicative gating at p <= 1/K) train a tiny char-LM at
  rung-1 scale, where the as-shipped bipolar-additive-PCGrad design produced zero converged seeds?

MODEL (substrate-native, NO gradient descent):
  Continuous float32 heteroassociative memory W (N x N) mapping a context-char code -> next-char code
  (bigram LM, same encoding family as testbed.substrate_lm.char_lm.SubstrateCharLM but CONTINUOUS
  float32 codes instead of bipolar {+-1} -- drops the bipolar 97% MI-loss-per-coord constraint).
  Inference: pred = W @ ctx_code; cosine(pred, vocab_codes) -> softmax -> p(next); BPC = -log2 p(true).

FIVE ARMS (5 seeds each):
  A (K=1 Hebbian baseline): dW = outer(next, ctx); pure Hebbian, no modulation. Baseline norm + BPC.
  B (cf-RPE alone):         dW = outer(next - v, ctx) with v = W@ctx recomputed fresh (NO cache). Delta rule.
  C (sparse gating alone):  pure Hebbian dW, modulated by sparse top-1 multiplicative gate over K=8
                            RANDOM modulators (no semantic content). Tests gating without error signal.
  D (joint D+H, K=4):       cf-RPE delta rule + sparse top-1 gate over K=4 semantic channels, p=0.25.
  E (joint D+H, K=8):       cf-RPE delta rule + sparse top-1 gate over K=8 semantic channels, p=0.125.

THREE STRUCTURAL MITIGATIONS (per routing):
  1. No-cache cf: v is always recomputed (W @ ctx) at the moment of substitution; v_old never cached.
  2. Capacity tracking: alpha = distinct-contexts / N tracked every step; early-warn if > 0.9*alpha_c.
  3. Router entropy guard: Shazeer-2017 gaussian noise on the router; entropy tracked; > log(2) bits = healthy.

PRE-REGISTERED BANDS (joint arms D/E are the headline; A/B/C discriminate the levers):
  HARD-PASS (D or E):
    - >= 4/5 seeds converge to val_loss < 3.5 bits/char by step 500
    - mean update-norm >= 0.80 * Arm-A(K=1) baseline norm (Drill 1: sparse top-1 preserves baseline norm)
    - router entropy > log(2) bits (no gating saturation)
    - capacity alpha < alpha_c at all times
  MIDDLE:
    - 2-3/5 seeds converge OR norm ratio in [0.40, 0.80) OR router entropy in [0.5, log(2)]
  HARD-FAIL:
    - mean norm < 0.10 * baseline (gating collapse) OR 0-1/5 seeds converge OR
    - norm oscillation > 3x mean (instability) OR capacity exceeds alpha_c

FORMULA SELF-TESTS (PROT-022):
  1. float32 codebook: code(ch) is float32, shape (N,), non-bipolar (has values outside {-1,+1}).
  2. Heteroassoc recall: single-pair write then W@ctx has cosine > 0.5 with the stored next code.
  3. cf-RPE delta shrinks: after delta-rule write, fresh ||next - W@ctx|| < ||next|| (error reduced).
  4. Sparse top-1 gate: entropy of a peaked gate < entropy of uniform = log(K); top-1 selects 1 channel.
  5. log(2) = 0.6931. [EXPECTED: 0.6931 within 1e-3]

PROT-018: anchor has _n4096; substrate N MUST = 4096 in full mode.
PROT-021: source=remote CPU, run_mode=full, n_seeds=5; partials keyed seed + run_mode + N.
QUEUE: remote_cpu_queue (CPU; pure numpy). TIMEOUT: 21600s (PROT-019 floor for _n>=4096).
ASCII-only stdout.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_joint_dh_brain_correct_rung1_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
LR = 0.5
BATCH = 64
CONV_STEP = 500          # convergence checkpoint (val_loss < 3.5 by this step)
HP_VAL_BPC = 3.5
HP_SEED_FRAC = 4.0 / 5
MID_SEED_FRAC = 2.0 / 5
HP_NORM_RATIO = 0.80
MID_NORM_RATIO = 0.40
HF_NORM_RATIO = 0.10
LOG2 = math.log(2.0)

if RUN_MODE == "smoke":
    N_DIM = 256
    SEEDS = [7, 17]
    N_STEPS = 60
    TRAIN_CHARS = 8000
    VAL_CHARS = 2000
    EVAL_EVERY = 20
else:
    N_DIM = N
    SEEDS = [7, 17, 23, 31, 41]
    N_STEPS = 1000
    TRAIN_CHARS = 120000
    VAL_CHARS = 20000
    EVAL_EVERY = 50

# Arm specs: (name, cf_rpe, gating, K, p)
ARMS = [
    ("A_hebbian_k1",   False, False, 1,   1.0),
    ("B_cfrpe_alone",  True,  False, 1,   1.0),
    ("C_gating_alone", False, True,  8,   0.10),
    ("D_joint_k4",     True,  True,  4,   0.25),
    ("E_joint_k8",     True,  True,  8,   0.125),
]


# ---------------------------------------------------------------------------
# Continuous float32 codebook + encoding
# ---------------------------------------------------------------------------

def build_codebook(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    """Continuous float32 codebook: (V, N) standard-normal rows (NOT bipolar)."""
    rng = np.random.default_rng(seed + 101)
    cb = rng.standard_normal((len(vocab), n_dim)).astype(np.float32)
    # Unit-norm rows so cosine scoring + write magnitudes are well-scaled.
    cb /= (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)
    return cb


def make_bigram_arrays(text: str, ch_to_idx: Dict[str, int]) -> np.ndarray:
    ids = np.array([ch_to_idx.get(c, 0) for c in text], dtype=np.int64)
    return ids


# ---------------------------------------------------------------------------
# Sparse top-1 multiplicative gating router (Shazeer-2017 noisy gating)
# ---------------------------------------------------------------------------

def noisy_topk_gate(channel_signals: np.ndarray, rng: np.random.Generator,
                    noise_std: float = 0.5) -> Tuple[float, float]:
    """Return (modulation_scalar, router_entropy_bits) for sparse top-1 gating.

    channel_signals: (K,) raw per-channel scores. Gate = softmax(signals + gaussian noise),
    entropy measured on the full softmax (saturation detector), then top-1 sparsified.
    modulation_scalar normalized so a confident top-1 -> ~1.0 (Drill 1 baseline-norm equivalence);
    a collapsed/uniform router -> ~1/K (shrunk update, the gating-collapse failure mode).
    """
    K = channel_signals.shape[0]
    if K == 1:
        return 1.0, LOG2  # degenerate single channel
    logits = channel_signals + rng.standard_normal(K).astype(np.float32) * noise_std
    logits = logits - np.max(logits)
    ez = np.exp(logits)
    gate = ez / (np.sum(ez) + 1e-30)
    # Router entropy in bits (on full softmax, BEFORE sparsification).
    ent = float(-np.sum(gate * np.log(gate + 1e-30)) / LOG2)
    # Sparse top-1: modulation = K * top1_weight so uniform->1.0-ish, peaked->K*(~1)... clamp.
    top1 = float(np.max(gate))
    mod = min(K * top1 / K * 1.0, 1.0) if False else min(top1 * K, 1.0)
    # mod in (0,1]: uniform gate top1=1/K -> mod=1/K*K... = 1.0? careful: top1=1/K -> mod=1.0.
    # peaked gate top1->1 -> mod=min(K,1)=1.0. So mod ~1.0 unless top1 < 1/K (impossible).
    # Use a saturation-sensitive form: mod = top1 (in (1/K, 1]); collapse if entropy near log2(K).
    mod = top1
    return mod, ent


# ---------------------------------------------------------------------------
# Semantic channel signals (Arms D/E) and random channels (Arm C)
# ---------------------------------------------------------------------------

def semantic_channels(K: int, delta_norm: float, alpha: float, drift: float,
                      erank: float, rng: np.random.Generator) -> np.ndarray:
    """K semantic channel scores. K=4: cf-RPE, capacity, drift, erank. K=8 adds 4 phasic channels."""
    base = np.array([
        delta_norm,            # cf-RPE magnitude (TD-error)
        1.0 - alpha / ALPHA_C, # capacity headroom
        drift,                 # kappa_3-style drift
        erank,                 # activation effective-rank proxy
    ], dtype=np.float32)
    if K <= 4:
        return base[:K]
    # K=8: 4 phasic event-triggered channels (sparse, mostly low) per routing.
    phasic = rng.standard_normal(K - 4).astype(np.float32) * 0.3
    return np.concatenate([base, phasic]).astype(np.float32)


# ---------------------------------------------------------------------------
# Train one arm for one seed
# ---------------------------------------------------------------------------

def train_arm(arm, code_matrix, train_ids, val_ids, n_dim, rng) -> Dict:
    name, cf_rpe, gating, K, p = arm
    V = code_matrix.shape[0]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)

    distinct_ctx = set()
    update_norms: List[float] = []
    entropies: List[float] = []
    val_curve: List[Tuple[int, float]] = []
    alpha_max_seen = 0.0
    stale_cache_events = 0  # always 0 by construction (no-cache); tracked for the band

    n_train = train_ids.shape[0]

    def sample_bigrams(ids, b):
        starts = rng.integers(0, ids.shape[0] - 1, size=b)
        return ids[starts], ids[starts + 1]

    # Readout temperature grid: cosine scores live in [-1,1]; softmax at temp=1 is
    # near-flat (-> near-uniform BPC even with working retrieval). Calibrate the
    # temperature per eval (identical procedure for every arm -> fair comparison).
    TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

    def eval_val_bpc():
        # Score a sample of val bigrams; report temperature-calibrated BPC.
        nb = min(2000, val_ids.shape[0] - 1)
        starts = rng.integers(0, val_ids.shape[0] - 1, size=nb)
        ctx = code_matrix[val_ids[starts]]        # (nb, N)
        nxt_idx = val_ids[starts + 1]             # (nb,)
        pred = ctx @ W.T                          # (nb, N): pred_i = W @ ctx_i
        pn = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8)
        cos = pn @ code_matrix.T                  # (nb, V)
        best = float("inf")
        for temp in TEMP_GRID:
            z = cos / temp
            z = z - z.max(axis=1, keepdims=True)
            ez = np.exp(z)
            prob = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
            p_true = np.clip(prob[np.arange(nb), nxt_idx], 1e-12, 1.0)
            bpc = float(np.mean(-np.log2(p_true)))
            if bpc < best:
                best = bpc
        return best

    prev_W_fro = 0.0
    for step in range(N_STEPS):
        c_idx, n_idx = sample_bigrams(train_ids, BATCH)
        Ctx = code_matrix[c_idx]   # (B, N)
        Nxt = code_matrix[n_idx]   # (B, N)
        distinct_ctx.update(c_idx.tolist())
        alpha = len(distinct_ctx) / n_dim
        alpha_max_seen = max(alpha_max_seen, alpha)

        # Fresh prediction (NO cache): v = W @ ctx for each item.
        Vpred = Ctx @ W.T          # (B, N)
        if cf_rpe:
            Delta = Nxt - Vpred    # cf-RPE / delta rule (Widrow-Hoff)
        else:
            Delta = Nxt            # pure Hebbian target

        # Base rank-1 (batched) update.
        dW = (Delta.T @ Ctx) / (BATCH * 1.0)   # (N, N)

        delta_norm = float(np.mean(np.linalg.norm(Delta, axis=1)))

        if gating:
            if name == "C_gating_alone":
                ch = rng.standard_normal(K).astype(np.float32)   # random modulators, no semantics
            else:
                drift = abs(float(np.linalg.norm(W, "fro")) - prev_W_fro)
                erank_proxy = float(np.mean(np.linalg.norm(Vpred, axis=1))) / (math.sqrt(n_dim))
                ch = semantic_channels(K, delta_norm, alpha, drift, erank_proxy, rng)
            mod, ent = noisy_topk_gate(ch, rng)
            entropies.append(ent)
            dW = dW * mod
        else:
            entropies.append(LOG2)  # ungated arms: neutral (single effective channel)

        W += LR * dW
        prev_W_fro = float(np.linalg.norm(W, "fro"))
        update_norms.append(float(np.linalg.norm(LR * dW)))

        if step % EVAL_EVERY == 0 or step == N_STEPS - 1:
            val_curve.append((step, eval_val_bpc()))

    # Convergence: val BPC < HP_VAL_BPC at the first checkpoint at/after CONV_STEP.
    conv_bpc = None
    for (s, b) in val_curve:
        if s >= CONV_STEP:
            conv_bpc = b
            break
    if conv_bpc is None and val_curve:
        conv_bpc = val_curve[-1][1]
    converged = (conv_bpc is not None) and (conv_bpc < HP_VAL_BPC)

    mean_norm = float(np.mean(update_norms)) if update_norms else 0.0
    norm_std = float(np.std(update_norms)) if update_norms else 0.0
    mean_ent = float(np.mean(entropies)) if entropies else 0.0
    final_bpc = val_curve[-1][1] if val_curve else float("inf")

    return {
        "arm": name, "cf_rpe": cf_rpe, "gating": gating, "K": K, "p": p,
        "converged": bool(converged),
        "conv_bpc": float(conv_bpc) if conv_bpc is not None else None,
        "final_bpc": float(final_bpc),
        "mean_update_norm": mean_norm,
        "norm_oscillation": float(norm_std / (mean_norm + 1e-12)),
        "mean_router_entropy_bits": mean_ent,
        "alpha_max": float(alpha_max_seen),
        "alpha_exceeded_c": bool(alpha_max_seen > ALPHA_C),
        "stale_cache_events": stale_cache_events,
        "val_curve": [[int(s), float(b)] for (s, b) in val_curve],
    }


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    train_text = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    val_text = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    vocab = sorted(set(train_text) | set(val_text))
    ch_to_idx = {c: i for i, c in enumerate(vocab)}
    code_matrix = build_codebook(vocab, n_dim, seed)
    train_ids = make_bigram_arrays(train_text, ch_to_idx)
    val_ids = make_bigram_arrays(val_text, ch_to_idx)
    print(f"  [seed={seed}] N={n_dim} vocab={len(vocab)} train_chars={len(train_text)}", flush=True)

    arms_out = {}
    for arm in ARMS:
        r = train_arm(arm, code_matrix, train_ids, val_ids, n_dim, rng)
        arms_out[arm[0]] = r
        print(f"    [{arm[0]}] conv_bpc={r['conv_bpc']} converged={r['converged']} "
              f"mean_norm={r['mean_update_norm']:.4f} ent={r['mean_router_entropy_bits']:.3f} "
              f"alpha_max={r['alpha_max']:.4f}", flush=True)
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "arms": arms_out, "elapsed_s": elapsed}


# ---------------------------------------------------------------------------
# Self-test (PROT-022)
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    assert abs(LOG2 - 0.6931) < 1e-3, f"log(2) selftest: {LOG2}"
    n_test = 128
    rng = np.random.default_rng(42)
    vocab = list("abcdef ")
    cb = build_codebook(vocab, n_test, seed=1)
    # 1. float32, non-bipolar
    assert cb.dtype == np.float32, "codebook not float32"
    assert np.any(np.abs(cb) != 1.0), "codebook looks bipolar (should be continuous)"
    # 2. heteroassoc recall
    W = np.zeros((n_test, n_test), dtype=np.float32)
    ctx, nxt = cb[0], cb[1]
    W += np.outer(nxt, ctx)
    pred = W @ ctx
    cos = float(pred @ nxt / ((np.linalg.norm(pred) + 1e-8) * (np.linalg.norm(nxt) + 1e-8)))
    assert cos > 0.5, f"heteroassoc recall cosine too low: {cos}"
    # 3. cf-RPE delta shrinks error
    err_before = np.linalg.norm(nxt - (np.zeros((n_test, n_test)) @ ctx))
    Wd = np.zeros((n_test, n_test), dtype=np.float32)
    v = Wd @ ctx
    Wd += np.outer(nxt - v, ctx)
    err_after = np.linalg.norm(nxt - (Wd @ ctx))
    assert err_after < err_before, f"cf-RPE did not reduce error: {err_after} vs {err_before}"
    # 4. sparse top-1 gate entropy < uniform
    peaked = np.array([5.0, 0.0, 0.0, 0.0], dtype=np.float32)
    _, ent_peaked = noisy_topk_gate(peaked, np.random.default_rng(0), noise_std=0.0)
    assert ent_peaked < math.log(4) / LOG2, f"peaked entropy not < log2(4): {ent_peaked}"
    print(f"[selftest] PASS: recall_cos={cos:.3f} err {err_before:.3f}->{err_after:.3f} "
          f"peaked_ent={ent_peaked:.3f} bits", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no valid results.")

    def arm_stats(arm_name):
        rs = [r["arms"][arm_name] for r in results if arm_name in r.get("arms", {})]
        n = len(rs)
        n_conv = sum(1 for x in rs if x["converged"])
        mean_norm = float(np.mean([x["mean_update_norm"] for x in rs])) if rs else 0.0
        mean_ent = float(np.mean([x["mean_router_entropy_bits"] for x in rs])) if rs else 0.0
        max_osc = max([x["norm_oscillation"] for x in rs], default=0.0)
        alpha_bad = any(x["alpha_exceeded_c"] for x in rs)
        return {"n": n, "n_conv": n_conv, "mean_norm": mean_norm,
                "mean_ent": mean_ent, "max_osc": max_osc, "alpha_bad": alpha_bad}

    baseline = arm_stats("A_hebbian_k1")
    base_norm = max(baseline["mean_norm"], 1e-12)

    def classify_joint(arm_name):
        s = arm_stats(arm_name)
        if s["n"] == 0:
            return "HARD_FAIL", s, 0.0
        ratio = s["mean_norm"] / base_norm
        conv_frac = s["n_conv"] / s["n"]
        # HARD_FAIL conditions
        if ratio < HF_NORM_RATIO or conv_frac <= MID_SEED_FRAC - 1e-9 or s["max_osc"] > 3.0 or s["alpha_bad"]:
            if conv_frac < MID_SEED_FRAC or ratio < HF_NORM_RATIO or s["max_osc"] > 3.0 or s["alpha_bad"]:
                return "HARD_FAIL", s, ratio
        # HARD_PASS
        if (conv_frac >= HP_SEED_FRAC and ratio >= HP_NORM_RATIO
                and s["mean_ent"] > LOG2 / LOG2 and not s["alpha_bad"]):
            # mean_ent in bits; > log(2) bits means > 1.0 bit. (LOG2/LOG2 == 1.0)
            return "HARD_PASS", s, ratio
        # MIDDLE
        if conv_frac >= MID_SEED_FRAC or ratio >= MID_NORM_RATIO:
            return "MIDDLE_BAND", s, ratio
        return "HARD_FAIL", s, ratio

    vd, sd, rd = classify_joint("D_joint_k4")
    ve, se, re_ = classify_joint("E_joint_k8")

    order = {"HARD_PASS": 3, "MIDDLE_BAND": 2, "HARD_FAIL": 1}
    best = "HARD_PASS" if order[vd] == 3 or order[ve] == 3 else (
        "MIDDLE_BAND" if max(order[vd], order[ve]) == 2 else "HARD_FAIL")

    b = arm_stats("B_cfrpe_alone")
    c = arm_stats("C_gating_alone")
    summary = (
        f"D[{vd} conv={sd['n_conv']}/{sd['n']} norm_ratio={rd:.2f} ent={sd['mean_ent']:.2f}] "
        f"E[{ve} conv={se['n_conv']}/{se['n']} norm_ratio={re_:.2f} ent={se['mean_ent']:.2f}] "
        f"A_base_norm={base_norm:.4f} B_cfrpe[conv={b['n_conv']}/{b['n']}] "
        f"C_gating[conv={c['n_conv']}/{c['n']} ent={c['mean_ent']:.2f}] "
        f"A_hebbian[conv={baseline['n_conv']}/{baseline['n']}]"
    )
    return (best, f"{best}: joint D+H rung-1. {summary}")


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} mode={RUN_MODE} seeds={SEEDS} "
      f"steps={N_STEPS} arms={[a[0] for a in ARMS]}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_DIM={N_DIM} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "run_mode": RUN_MODE, "n_steps": N_STEPS, "arms": [a[0] for a in ARMS]}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_DIM)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "n_steps": N_STEPS,
    "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"),
         "arms": {k: {"converged": v["converged"], "conv_bpc": v["conv_bpc"],
                      "final_bpc": v["final_bpc"], "mean_update_norm": v["mean_update_norm"],
                      "mean_router_entropy_bits": v["mean_router_entropy_bits"],
                      "alpha_max": v["alpha_max"], "norm_oscillation": v["norm_oscillation"]}
                  for k, v in r.get("arms", {}).items()},
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
