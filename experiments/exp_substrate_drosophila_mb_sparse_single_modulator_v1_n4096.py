"""
substrate_drosophila_mb_sparse_single_modulator_v1_n4096 -- Drosophila MB template ablation (Phase 1a).

ROUTING: notes/routing_convergent_brain_architecture_empirical_batch_2026-06-04.md (Research), Phase 1a --
  the CHEAPEST DECISIVE TEST. Gates the Phase 2/3 convergent-architecture decision tree.

CAPABILITY QUESTION:
  Does the Drosophila mushroom-body template -- SPARSE binary {0,1} coding (f=0.05) + a SINGLE
  dopamine-class cf-RPE modulator -- beat the current DENSE bipolar multi-channel (K=8) substrate-as-
  training design at N=4096? (Lit: Aso-Rubin 2014; Cohn 2015 -- sparse coding gives large capacity gain.)

TWO CELLS (3 seeds each; identical char-LM scaffold + identical calibrated readout):
  Cell A (baseline reproduction): DENSE bipolar {+1,-1} codes + cf-RPE delta rule + sparse top-1 gate over
    K=8 semantic channels (the current joint-D+H architecture).
  Cell B (Drosophila MB template): SPARSE binary {0,1} codes at f=0.05 + SINGLE cf-RPE modulator (delta
    rule only; NO multi-channel gating).

SHARED MODEL (substrate-native, NO gradient descent): continuous heteroassociative memory W (N x N) mapping
  a context-char code -> next-char code (bigram LM). Inference: pred = W @ ctx; cosine(pred, vocab) ->
  calibrated-temperature softmax -> per-char loss. Reported in NATS (natural log) to match routing bands.

PRE-REGISTERED BANDS (NATS; gap = loss_A - loss_B, positive => sparse+single is better):
  HARD-PASS: gap_mean > 0.5 nats AND Cell B better on 3/3 seeds AND no instability (Cell B norm
    oscillation < 3x mean).
  MIDDLE: gap_mean in [0.1, 0.5] nats (sparse+single helps but modestly).
  HARD-FAIL: gap_mean < 0.1 nats (sparse + single modulator does NOT help; Cell B >= Cell A).

FORMULA SELF-TESTS (PROT-022):
  1. sparse codebook: row sum ~ f*N ones; values in {0,1}.
  2. bipolar codebook: values in {-1,+1}.
  3. heteroassoc recall (sparse): single-pair write -> cosine(W@ctx, next) > 0.5.
  4. cf-RPE delta shrinks error after a delta-rule write.
  5. uniform loss in nats = ln(V) (e.g. ln(7)=1.9459 within 1e-3).

PROT-018: anchor has _n4096; substrate N MUST = 4096 in full mode.
PROT-021: source=remote CPU, run_mode=full, n_seeds=3; partials keyed seed + run_mode + N.
QUEUE: remote_cpu_queue (CPU; pure numpy). TIMEOUT: 14400s (PROT-019 floor for _n4096). ASCII-only stdout.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, math, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_drosophila_mb_sparse_single_modulator_v1_n4096"
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
SPARSE_F = 0.05
K_CHANNELS = 8
LOG2 = math.log(2.0)
HP_GAP, MID_GAP = 0.5, 0.1     # nats
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

if RUN_MODE == "smoke":
    N_DIM = 256
    SEEDS = [7, 17]
    N_STEPS = 60
    TRAIN_CHARS = 8000
    VAL_CHARS = 2000
    EVAL_EVERY = 20
else:
    N_DIM = N
    SEEDS = [7, 17, 23]
    N_STEPS = 1000
    TRAIN_CHARS = 120000
    VAL_CHARS = 20000
    EVAL_EVERY = 100

# Cell specs: (name, coding, cf_rpe, gating, K)
CELLS = [
    ("A_dense_bipolar_k8", "bipolar", True, True, K_CHANNELS),
    ("B_sparse_single_cfrpe", "sparse", True, False, 1),
]


def build_codebook(vocab: List[str], n_dim: int, seed: int, coding: str) -> np.ndarray:
    """Unit-norm rows so the heteroassociative algebra is well-scaled (same as the joint-D+H baseline).
    Coding differs in STRUCTURE: bipolar = all N dims active (+-1); sparse = only f*N dims active (the
    Drosophila MB property -> low inter-pattern overlap -> capacity gain). Unit-norm preserves support."""
    rng = np.random.default_rng(seed + 101)
    if coding == "bipolar":
        cb = rng.choice([-1.0, 1.0], size=(len(vocab), n_dim)).astype(np.float32)
    else:
        # sparse binary {0,1} support at density f
        cb = np.zeros((len(vocab), n_dim), dtype=np.float32)
        k = max(1, int(round(SPARSE_F * n_dim)))
        for i in range(len(vocab)):
            idx = rng.choice(n_dim, size=k, replace=False)
            cb[i, idx] = 1.0
    cb /= (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)
    return cb


def semantic_channels(K, delta_norm, alpha, drift, erank, rng):
    base = np.array([delta_norm, 1.0 - alpha / ALPHA_C, drift, erank], dtype=np.float32)
    if K <= 4:
        return base[:K]
    phasic = rng.standard_normal(K - 4).astype(np.float32) * 0.3
    return np.concatenate([base, phasic]).astype(np.float32)


def noisy_topk_gate(ch, rng, noise_std=0.5):
    K = ch.shape[0]
    if K == 1:
        return 1.0, LOG2 / LOG2
    logits = ch + rng.standard_normal(K).astype(np.float32) * noise_std
    logits = logits - np.max(logits)
    ez = np.exp(logits); gate = ez / (np.sum(ez) + 1e-30)
    ent = float(-np.sum(gate * np.log(gate + 1e-30)) / LOG2)
    return float(np.max(gate)), ent


def train_cell(cell, code_matrix, train_ids, val_ids, n_dim, rng) -> Dict:
    name, coding, cf_rpe, gating, K = cell
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    distinct_ctx = set(); update_norms: List[float] = []; val_curve = []
    alpha_max = 0.0; prev_W_fro = 0.0

    def eval_loss():
        nb = min(2000, val_ids.shape[0] - 1)
        starts = rng.integers(0, val_ids.shape[0] - 1, size=nb)
        ctx = code_matrix[val_ids[starts]]; nxt = val_ids[starts + 1]
        pred = ctx @ W.T
        pn = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-8)
        cos = pn @ code_matrix.T
        best_nats = float("inf")
        for temp in TEMP_GRID:
            z = cos / temp; z = z - z.max(axis=1, keepdims=True); ez = np.exp(z)
            prob = ez / (ez.sum(axis=1, keepdims=True) + 1e-30)
            pt = np.clip(prob[np.arange(nb), nxt], 1e-12, 1.0)
            nats = float(np.mean(-np.log(pt)))
            best_nats = min(best_nats, nats)
        return best_nats

    for step in range(N_STEPS):
        starts = rng.integers(0, train_ids.shape[0] - 1, size=BATCH)
        c_idx = train_ids[starts]; n_idx = train_ids[starts + 1]
        Ctx = code_matrix[c_idx]; Nxt = code_matrix[n_idx]
        distinct_ctx.update(c_idx.tolist())
        alpha = len(distinct_ctx) / n_dim; alpha_max = max(alpha_max, alpha)
        Vpred = Ctx @ W.T
        Delta = (Nxt - Vpred) if cf_rpe else Nxt
        dW = (Delta.T @ Ctx) / BATCH
        delta_norm = float(np.mean(np.linalg.norm(Delta, axis=1)))
        if gating:
            drift = abs(float(np.linalg.norm(W, "fro")) - prev_W_fro)
            erank = float(np.mean(np.linalg.norm(Vpred, axis=1))) / math.sqrt(n_dim)
            ch = semantic_channels(K, delta_norm, alpha, drift, erank, rng)
            mod, _ = noisy_topk_gate(ch, rng)
            dW = dW * mod
        W += LR * dW
        prev_W_fro = float(np.linalg.norm(W, "fro"))
        update_norms.append(float(np.linalg.norm(LR * dW)))
        if step % EVAL_EVERY == 0 or step == N_STEPS - 1:
            val_curve.append((step, eval_loss()))

    final_nats = val_curve[-1][1] if val_curve else float("inf")
    best_nats = min((b for _, b in val_curve), default=float("inf"))
    mean_norm = float(np.mean(update_norms)) if update_norms else 0.0
    osc = float(np.std(update_norms) / (mean_norm + 1e-12)) if update_norms else 0.0
    return {"cell": name, "coding": coding, "cf_rpe": cf_rpe, "gating": gating, "K": K,
            "final_nats": float(final_nats), "best_nats": float(best_nats),
            "final_bpc_bits": float(final_nats / LOG2), "mean_update_norm": mean_norm,
            "norm_oscillation": osc, "alpha_max": float(alpha_max),
            "val_curve_nats": [[int(s), float(b)] for s, b in val_curve]}


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    train_text = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    val_text = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    vocab = sorted(set(train_text) | set(val_text))
    idx = {c: i for i, c in enumerate(vocab)}
    train_ids = np.array([idx.get(c, 0) for c in train_text], dtype=np.int64)
    val_ids = np.array([idx.get(c, 0) for c in val_text], dtype=np.int64)
    uniform_nats = math.log(len(vocab))
    print(f"  [seed={seed}] N={n_dim} vocab={len(vocab)} uniform_nats={uniform_nats:.4f}", flush=True)
    cells_out = {}
    for cell in CELLS:
        # each cell gets its own codebook (coding differs)
        cb = build_codebook(vocab, n_dim, seed, cell[1])
        r = train_cell(cell, cb, train_ids, val_ids, n_dim, rng)
        cells_out[cell[0]] = r
        print(f"    [{cell[0]}] final_nats={r['final_nats']:.4f} best_nats={r['best_nats']:.4f} "
              f"norm={r['mean_update_norm']:.4f} osc={r['norm_oscillation']:.2f} "
              f"alpha_max={r['alpha_max']:.4f}", flush=True)
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "uniform_nats": float(uniform_nats),
            "cells": cells_out, "elapsed_s": elapsed}


def _selftest():
    n = 256; vocab = list("abcdef ")
    cb_sp = build_codebook(vocab, n, 1, "sparse")
    k = max(1, int(round(SPARSE_F * n)))
    assert int(np.count_nonzero(cb_sp[0])) == k, f"sparse support {np.count_nonzero(cb_sp[0])} vs {k}"
    assert abs(float(np.linalg.norm(cb_sp[0])) - 1.0) < 1e-4, "sparse not unit-norm"
    cb_bp = build_codebook(vocab, n, 1, "bipolar")
    assert int(np.count_nonzero(cb_bp[0])) == n, "bipolar should be dense (all dims active)"
    assert abs(float(np.linalg.norm(cb_bp[0])) - 1.0) < 1e-4, "bipolar not unit-norm"
    W = np.zeros((n, n), dtype=np.float32); ctx, nxt = cb_sp[0], cb_sp[1]
    W += np.outer(nxt, ctx); pred = W @ ctx
    cos = float(pred @ nxt / ((np.linalg.norm(pred) + 1e-8) * (np.linalg.norm(nxt) + 1e-8)))
    assert cos > 0.5, f"sparse heteroassoc recall cos={cos}"
    Wd = np.zeros((n, n), dtype=np.float32); v = Wd @ ctx
    eb = np.linalg.norm(nxt - v); Wd += np.outer(nxt - v, ctx); ea = np.linalg.norm(nxt - Wd @ ctx)
    assert ea < eb, f"cf-RPE did not shrink error {ea} vs {eb}"
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: sparse_density={cb_sp[0].sum():.0f} recall_cos={cos:.3f} "
          f"cfrpe_err {eb:.3f}->{ea:.3f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    gaps, b_better, b_osc = [], 0, []
    for r in results:
        ca = r["cells"].get("A_dense_bipolar_k8"); cb = r["cells"].get("B_sparse_single_cfrpe")
        if not ca or not cb:
            continue
        gap = ca["best_nats"] - cb["best_nats"]   # positive => B (sparse+single) better
        gaps.append(gap); b_osc.append(cb["norm_oscillation"])
        if cb["best_nats"] < ca["best_nats"]:
            b_better += 1
    if not gaps:
        return ("HARD_FAIL", "HARD_FAIL: cells missing.")
    n = len(gaps); gap_mean = float(np.mean(gaps)); max_osc_b = max(b_osc, default=0.0)
    mean_a = float(np.mean([r["cells"]["A_dense_bipolar_k8"]["best_nats"] for r in results]))
    mean_b = float(np.mean([r["cells"]["B_sparse_single_cfrpe"]["best_nats"] for r in results]))
    summary = (f"gap_mean={gap_mean:.3f} nats B_better={b_better}/{n} B_max_osc={max_osc_b:.2f} "
               f"meanA={mean_a:.3f} meanB={mean_b:.3f} nats")
    if gap_mean > HP_GAP and b_better == n and max_osc_b < 3.0:
        return ("HARD_PASS", f"HARD_PASS: Drosophila MB sparse+single beats dense-bipolar-K8 by >{HP_GAP} nats, "
                             f"all seeds, stable -> convergent direction validated. {summary}")
    if gap_mean >= MID_GAP:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: sparse+single helps modestly (gap in [{MID_GAP},{HP_GAP}]). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: sparse+single does not help (gap<{MID_GAP}). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} mode={RUN_MODE} seeds={SEEDS} "
      f"steps={N_STEPS} cells={[c[0] for c in CELLS]} sparse_f={SPARSE_F}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_DIM={N_DIM} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "run_mode": RUN_MODE, "n_steps": N_STEPS, "cells": [c[0] for c in CELLS]}
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
    "sparse_f": SPARSE_F, "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "uniform_nats": r.get("uniform_nats"),
                  "cells": r.get("cells", {}), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
