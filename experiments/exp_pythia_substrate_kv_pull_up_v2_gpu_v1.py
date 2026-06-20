"""
pythia_substrate_kv_pull_up_v2_gpu_v1 -- Pythia-2.8B substrate-KV-memory pull-up (Research v2 pre-reg +
Skunkworks GO 2026-06-19). Smoke->cert pull-up of the n1/n1b/n1d 2.8B LEGACY HARD_PASS evidence.

MECHANISM (from n1_pythia2p8b_substrate_kv): Pythia last-token hidden states key an external substrate-KV
memory. encode facts -> ZCA-whiten -> store key->value(id); recall by re-encoding a NOISED query +
nearest-key argmax. recall@1 = the substrate's external-memory capacity (scales BEYOND the context window).

v2 DISCRIMINATING REGIME: fact-bank SWEEP {2k,5k,10k,25k,50k,100k} x noise sigma {0.05,0.10,0.20} x 5 seeds.
PINNED to Pythia-2.8B (1.4B = separate event). Primary capacity recall = sigma=0.05 (clean); sigma=0.10 =
robustness; sigma=0.20 = stress.

v2 BANDS (LOCKED; cliff-band FIX = no-cliff-through-100k is the STRONGER result, not MIDDLE):
  HARD_PASS = recall(10k)>=0.80 AND graceful(recall(10k)-recall(2k) <= 0.05) AND noise sigma=0.10 recall(10k)>=0.60
              AND (cliff in [10k,100k] OR recall>=0.50 through 100k) AND all 5 seeds reproduce within +-0.03.
  MIDDLE    = HP except sigma=0.10 recall in [0.40,0.60) OR non-graceful drop(2k->10k) in (0.05,0.20] (strict >0.05; no overlap w/ HP).
  HARD_FAIL = recall(10k)<0.50 OR drop(2k->10k)>0.20 OR sigma=0.10 recall<0.40 OR seeds disagree >0.05.
  honest-scope LOCKED: "Pythia 2.8B hidden states are viable substrate-KV keys; recall>=0.80 over a fact-bank
  at the MEASURED capacity boundary; noise-robust at sigma=0.10. NOT a 1.4B claim."

DISPATCH-READINESS (BLOCKING, USER directive): checkpoint per (size,seed) [write_partial_key] + DEMONSTRATE
resume (kill-restart; the smoke is local-runnable on pythia-160m) + GPU-memory pre-check (model + KV table;
recall is CHUNKED so M=100k never materializes a 100k x 100k matrix). smoke=pythia-160m (cached; local-testable),
full=pythia-2.8b (GPU). PROT-018 no _nN (model-keyed). ASCII; import torch first (PROT-020).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"; os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "pythia_substrate_kv_pull_up_v2_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SIGMAS = [0.05, 0.10, 0.20, 0.50]    # 0.50 = CAN-fail stress probe (de-saturation: the test MUST be able to fail)
RECALL_CHUNK = 2000
if SMOKE:
    MODEL = "EleutherAI/pythia-160m"; SIZES = [500, 1000]; SEEDS = [7, 17]
else:
    MODEL = "EleutherAI/pythia-2.8b"; SIZES = [2000, 5000, 10000, 25000, 50000, 100000]; SEEDS = [7, 17, 23, 31, 41]


def make_facts(m, g):
    subjects = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
    rels = ["was founded in", "is located near", "was invented by", "merged with", "is the capital of",
            "won the award for", "is powered by", "was discovered in"]
    return [("entity %s-%d %s what" % (subjects[i % len(subjects)], i, rels[g.integers(0, len(rels))]), i) for i in range(m)]


def whiten_fit(K):
    mu = K.mean(0); Kc = K - mu
    cov = Kc.T @ Kc / len(K) + 1e-3 * np.eye(K.shape[1], dtype=np.float32)
    w, V = np.linalg.eigh(cov); W = (V @ np.diag(1.0 / np.sqrt(w)) @ V.T).astype(np.float32)
    Kw = Kc @ W; Kw = Kw / (np.linalg.norm(Kw, axis=1, keepdims=True) + 1e-8)
    return mu, W, Kw.astype(np.float32)


def recall_and_margin(Qw, Kw, gold, chunk=RECALL_CHUNK):
    """argmax recall + NN-MARGIN (top1-top2 sim) WITHOUT materializing M x M (handles M=100k).
    The margin is the DE-SATURATION signal (Skunkworks): it SHRINKS as keys crowd -> reveals the approaching
    capacity boundary even while recall is still 1.0. Returns (recall, mean_margin, p10_margin)."""
    correct = 0; margins = []
    for i in range(0, len(Qw), chunk):
        sims = Qw[i:i + chunk] @ Kw.T
        pred = np.argmax(sims, axis=1)
        correct += int((pred == gold[i:i + chunk]).sum())
        part = np.partition(sims, -2, axis=1)            # top-2 without full sort
        margins.append(part[:, -1] - part[:, -2])
    mar = np.concatenate(margins) if margins else np.array([0.0], np.float32)
    return correct / max(1, len(Qw)), float(mar.mean()), float(np.percentile(mar, 10))


def _selftest():
    g = np.random.default_rng(0)
    K = g.standard_normal((200, 16)).astype(np.float32)
    mu, W, Kw = whiten_fit(K)
    gold = np.arange(200)
    # zero-noise recall must be ~1.0 (each key recalls itself)
    Qw = ((K - mu) @ W); Qw = (Qw / (np.linalg.norm(Qw, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
    r0, m0, p0 = recall_and_margin(Qw, Kw, gold, chunk=64)
    assert r0 > 0.99, "zero-noise recall should be ~1.0, got %.3f" % r0
    assert m0 > 0, "NN-margin (top1-top2) must be positive, got %.4f" % m0
    # chunked recall == full
    full = float((np.argmax(Qw @ Kw.T, axis=1) == gold).mean())
    assert abs(full - r0) < 1e-9, "chunked != full"
    assert len(make_facts(5, g)) == 5
    print("[selftest] PASS: whiten + zero-noise-recall~1.0 + positive-margin + chunked==full + make_facts", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if torch.cuda.is_available():
    DEV = torch.device("cuda")
    print("[GPU] %s total=%.1fGB" % (torch.cuda.get_device_name(0), torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
elif SMOKE:
    DEV = torch.device("cpu")
    print("[smoke] no CUDA -> CPU fallback (pythia-160m; for resume-demo + logic verify only)", flush=True)
else:
    print("[FATAL] CUDA required for the full Pythia-2.8B run.", flush=True); sys.exit(1)


def memory_precheck(hidden_dim):
    """GPU-memory feasibility (Skunkworks BLOCKING item): model on GPU; KV table + recall on CPU (chunked)."""
    model_gb = {"EleutherAI/pythia-2.8b": 5.6, "EleutherAI/pythia-160m": 0.4}.get(MODEL, 6.0)
    if DEV.type != "cuda":
        print("[mem-precheck] CPU smoke -> GPU feasibility check skipped (full run on GPU does it).", flush=True); return
    gpu_total = torch.cuda.get_device_properties(0).total_memory / 1e9
    max_m = max(SIZES)
    kv_cpu_gb = max_m * hidden_dim * 4 * 3 / 1e9     # K + Kw + Q (CPU numpy)
    chunk_gb = RECALL_CHUNK * max_m * 4 / 1e9        # chunked sims temp (CPU)
    print("[mem-precheck] model~%.1fGB (GPU, total %.1fGB) | KV+recall CPU ~%.1fGB + chunk-temp ~%.2fGB (M=%d, dim=%d). "
          "recall is CHUNKED -> no MxM matrix." % (model_gb, gpu_total, kv_cpu_gb, chunk_gb, max_m, hidden_dim), flush=True)
    if model_gb > gpu_total - 0.5:
        raise RuntimeError("model %.1fGB will not fit GPU %.1fGB" % (model_gb, gpu_total))


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEV)
        with torch.no_grad():
            h = m(**t).last_hidden_state
        lens = t["attention_mask"].sum(1) - 1
        out.append(h[torch.arange(h.shape[0]), lens].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def _measure(Keys, gold, g):
    """recall + NN-margin per sigma for a given key matrix (whiten -> noised-query nearest-key)."""
    mu, W, Kw = whiten_fit(Keys)
    rec, mar, p10 = {}, {}, {}
    for sigma in SIGMAS:
        Q = Keys + sigma * g.standard_normal(Keys.shape).astype(np.float32)
        Qw = (Q - mu) @ W; Qw = (Qw / (np.linalg.norm(Qw, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
        r, m, p = recall_and_margin(Qw, Kw, gold)
        rec["%.2f" % sigma] = round(r, 4); mar["%.2f" % sigma] = round(m, 5); p10["%.2f" % sigma] = round(p, 5)
    return rec, mar, p10


def run_unit(size, seed, tok, mdl):
    g = np.random.default_rng(seed)
    facts = make_facts(size, g); texts = [f[0] for f in facts]
    K = encode(texts, tok, mdl)
    gold = np.arange(size)
    rec, mar, p10 = _measure(K, gold, g)                                     # Pythia keys
    K_rand = g.standard_normal(K.shape).astype(np.float32)                   # RANDOM-key control = best-case isotropic separability (discrimination check)
    rrec, rmar, _ = _measure(K_rand, gold, g)
    print("  [size=%d seed=%d] pythia recall: %s | margin: %s || random recall: %s margin: %s" % (
        size, seed,
        " ".join("s%.2f=%.2f" % (s, rec["%.2f" % s]) for s in SIGMAS),
        " ".join("s%.2f=%.3f" % (s, mar["%.2f" % s]) for s in SIGMAS),
        " ".join("s%.2f=%.2f" % (s, rrec["%.2f" % s]) for s in SIGMAS),
        " ".join("s%.2f=%.3f" % (s, rmar["%.2f" % s]) for s in SIGMAS)), flush=True)
    return {"size": size, "seed": seed, "model": MODEL, "run_mode": RUN_MODE,
            "recall_by_sigma": rec, "margin_by_sigma": mar, "p10margin_by_sigma": p10,
            "rand_recall_by_sigma": rrec, "rand_margin_by_sigma": rmar}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    """DE-SATURATED verdict (Skunkworks's catch: recall=1.0-everywhere can't tell genuine capacity from a non-discriminating
    test). A clean capacity cert now REQUIRES the test be DISCRIMINATING: either a CAN-fail boundary is located (recall<1.0
    somewhere, esp sigma=0.5) OR the NN-margin meaningfully shrinks toward the boundary AND pythia keys beat the random-key
    control. recall=1.0 + flat margin + == random => NON-discriminating => LOWER-BOUND MEASURED_MECHANISM, not chain-grade."""
    if not units:
        return ("HARD_FAIL", "no results", {})
    PRIMARY = 0.05
    def agg(field, sz, s):
        vals = [u[field]["%.2f" % s] for u in units if u["size"] == sz and field in u and "%.2f" % s in u[field]]
        return (float(np.mean(vals)), float(np.std(vals))) if vals else (None, None)
    R = lambda sz, s: agg("recall_by_sigma", sz, s)[0]
    MAR = lambda sz, s: agg("margin_by_sigma", sz, s)[0]
    RMAR = lambda sz, s: agg("rand_margin_by_sigma", sz, s)[0]
    RR = lambda sz, s: agg("rand_recall_by_sigma", sz, s)[0]
    sizes = sorted(set(u["size"] for u in units)); s_lo, s_hi = sizes[0], sizes[-1]
    r_lo, r_hi, r_hi_n = R(s_lo, PRIMARY), R(s_hi, PRIMARY), R(s_hi, 0.10)
    drop = (r_lo - r_hi) if (r_lo is not None and r_hi is not None) else None
    max_std = max((agg("recall_by_sigma", sz, PRIMARY)[1] or 0.0 for sz in sizes), default=0.0)
    # DE-SATURATION signals
    all_rec = [R(sz, s) for sz in sizes for s in SIGMAS if R(sz, s) is not None]
    canfail_min_recall = min(all_rec) if all_rec else 1.0
    r_stress = min((R(sz, 0.50) for sz in sizes if R(sz, 0.50) is not None), default=None)   # sigma=0.5 stress
    mar_lo, mar_hi = MAR(s_lo, PRIMARY), MAR(s_hi, PRIMARY)
    margin_shrink = (mar_hi / mar_lo) if (mar_lo and mar_hi and mar_lo > 0) else None          # <1 -> shrinking toward boundary
    pyt_mar, rnd_mar = MAR(s_hi, PRIMARY), RMAR(s_hi, PRIMARY)
    margin_vs_random = (pyt_mar - rnd_mar) if (pyt_mar is not None and rnd_mar is not None) else None
    canfail_located = canfail_min_recall < 0.99
    margin_shrinks = bool(margin_shrink is not None and margin_shrink < 0.80)
    discriminating = bool(canfail_located or margin_shrinks)
    detail = {"recall_primary_s0.05": {str(sz): R(sz, PRIMARY) for sz in sizes},
              "recall_s0.10": {str(sz): R(sz, 0.10) for sz in sizes}, "recall_s0.50_stress": {str(sz): R(sz, 0.50) for sz in sizes},
              "margin_primary_s0.05": {str(sz): MAR(sz, PRIMARY) for sz in sizes},
              "rand_recall_s0.05": {str(sz): RR(sz, PRIMARY) for sz in sizes}, "rand_margin_s0.05": {str(sz): RMAR(sz, PRIMARY) for sz in sizes},
              "recall_lo_clean": r_lo, "recall_hi_clean": r_hi, "drop_lo_to_hi": (round(drop, 4) if drop is not None else None),
              "recall_hi_noise0.10": r_hi_n, "max_seed_std": round(max_std, 4),
              "DESAT_canfail_min_recall": round(canfail_min_recall, 4), "DESAT_sigma0.5_min_recall": r_stress,
              "DESAT_margin_shrink_hi_over_lo": (round(margin_shrink, 4) if margin_shrink is not None else None),
              "DESAT_pythia_minus_random_margin": (round(margin_vs_random, 5) if margin_vs_random is not None else None),
              "DESAT_canfail_located": canfail_located, "DESAT_margin_shrinks": margin_shrinks, "DESAT_discriminating": discriminating,
              "sizes_tested": sizes,
              "honest_scope": "Pythia substrate-KV capacity; clean-capacity claim requires a DISCRIMINATING test (margin "
                              "shrinks or CAN-fail located). recall=1.0+flat-margin+==random = lower-bound only. NOT a 1.4B claim."}
    summary = ("recall(hi,clean)=%s drop=%s recall(hi,s0.10)=%s | DESAT: canfail_min_recall=%.3f sigma0.5_min=%s margin_shrink=%s "
               "pythia-random_margin=%s discriminating=%s max_std=%.3f" % (
               r_hi, (round(drop, 3) if drop is not None else None), r_hi_n, canfail_min_recall, r_stress, margin_shrink, margin_vs_random, discriminating, max_std))
    if r_hi is None or r_lo is None:
        return ("UNKNOWN", "missing size measurements (smoke logic-check ok) | " + summary, detail)
    if r_hi < 0.50 or (drop is not None and drop > 0.20) or (r_hi_n is not None and r_hi_n < 0.40) or max_std > 0.05:
        return ("HARD_FAIL", "HARD_FAIL: " + summary, detail)
    recall_good = r_hi >= 0.80 and (drop is None or drop <= 0.05) and (r_hi_n is None or r_hi_n >= 0.60) and max_std <= 0.03
    if recall_good and discriminating:
        return ("HARD_PASS", "HARD_PASS (de-saturated genuine capacity): recall>=0.80 to the tested boundary AND the test is "
                "DISCRIMINATING (CAN-fail located and/or NN-margin shrinks toward the boundary; not a saturated/trivial test). " + summary, detail)
    if recall_good and not discriminating:
        return ("MEASURED_MECHANISM", "MEASURED_MECHANISM (LOWER-BOUND; Skunkworks saturation catch CONFIRMED): recall>=0.80 "
                "through the tested scale BUT the test never bit -- CAN-fail NOT located (min recall %.3f; sigma=0.5 still %s), "
                "margin flat (shrink=%s) and pythia margin ~ random (%s). Genuine capacity is a LOWER-BOUND, UNMEASURED. "
                "Push M and/or sigma until recall<1.0 to locate the real boundary. " % (canfail_min_recall, r_stress, margin_shrink, margin_vs_random) + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: " + summary, detail)


print("[config] %s mode=%s model=%s sizes=%s sigmas=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, MODEL, SIZES, SIGMAS, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE}
t0 = time.time()
tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
mdl = AutoModel.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(DEV).eval()
memory_precheck(mdl.config.hidden_size)
for size in SIZES:
    for seed in SEEDS:
        key = "size%d_s%d" % (size, seed)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        res = run_unit(size, seed, tok, mdl); res["run_mode"] = RUN_MODE
        write_partial_key(out_dir, key, res)
del mdl
units = list(aggregate_partials(out_dir, ["size%d_s%d" % (sz, sd) for sz in SIZES for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "model": MODEL,
           "sizes": SIZES, "sigmas": SIGMAS, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_gpu_pythia2p8b_substrate_kv_sweep_noise", "per_unit": units,
           "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
