"""
exp_substrate_llama_layer_sweep_capacity_battery_gpu_v1 -- BUNDLED Llama layer-sweep substrate capacity -- GPU.

ROUTING: causal-LM recipe finalization (extends G15 HARD_PASS). G15 locked L=15 by assumption; this SWEEPS all layers of
  Llama-3.2-1B BASE to find which layer gives the best substrate capacity (last-token pool + ZCA whiten, the G15 recipe).
  One model forward captures every layer's hidden states (output_hidden_states); per-layer Hopfield exact-recovery capacity.
  Genuinely GPU-bound (Llama forward over N_enc texts). fp16.
PRE-REGISTERED: HARD-PASS some layer gives >=1.2x the L=15 capacity (a better layer exists; update the recipe). MID best
  within 0.9-1.2x of L=15 (L=15 ~ optimal). HARD-FAIL all layers < 0.9x L=15 (L=15 was already best / something off).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. Hopfield recovers low load. 3. deps.
ASCII-only. write_metrics. PROT-018 no _nN (layer-sweep).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_llama_layer_sweep_capacity_battery_gpu_v1"
ENCODER = "meta-llama/Llama-3.2-1B"; REF_LAYER = 15
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 800; LAYERS = [8, 12, 15]; LOADS = [0.01, 0.03, 0.06, 0.1, 0.2]
else:
    SEEDS = [7, 17, 23]; N_ENC = 4000; LAYERS = [4, 6, 8, 10, 12, 13, 14, 15, 16]; LOADS = [0.005, 0.01, 0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def hop_recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0          # W-free dense Hopfield
    return float(np.mean(np.all(s == P, axis=1)))


def cap(keys, seed):
    sg = np.sign(whiten_fit(keys)).astype(np.float32); sg[sg == 0] = 1.0; D = keys.shape[1]; c = 0
    for load in LOADS:
        M = max(2, int(load * D))
        if M > sg.shape[0]:
            break
        if hop_recall(sg[:M], seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((80, 64)); assert whiten_fit(K).shape == K.shape, "whiten preserves dim"
    P = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall(P, 0) >= 0.95, "hopfield recovers low load"
    print("[selftest] PASS: layer-sweep", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_texts(n):
    out = []
    for f in [MEDQA, PUBMED]:
        if f.exists():
            for l in open(f, encoding="utf-8"):
                r = json.loads(l); out.append((r.get("question") or " ".join(r.get("context", {}).get("contexts", [""])))[:300])
                if len(out) >= n:
                    return out
    return out


def encode_all_layers(texts):
    tok = AutoTokenizer.from_pretrained(ENCODER); tok.pad_token = tok.eos_token
    dt = torch.float16 if DEV.type == "cuda" else torch.float32
    m = AutoModelForCausalLM.from_pretrained(ENCODER, output_hidden_states=True, torch_dtype=dt).to(DEV).eval()
    per_layer = {L: [] for L in LAYERS}
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            hs = m(**t).hidden_states
        mask = t["attention_mask"]; lens = mask.sum(1) - 1
        for L in LAYERS:
            h = hs[L]; per_layer[L].append(h[torch.arange(h.shape[0]), lens].float().cpu().numpy())  # last-token pool
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return {L: np.concatenate(per_layer[L], 0).astype(np.float32) for L in LAYERS}


def run_seed(seed, layer_keys) -> Dict:
    a = {("L%d" % L): cap(layer_keys[L], seed) for L in LAYERS}
    print("  [seed=%d] cap by layer %s" % (seed, a), flush=True); return {"seed": seed, "cap": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {("L%d" % L): float(np.mean([p["cap"]["L%d" % L] for p in ps])) for L in LAYERS}
    ref = agg.get("L%d" % REF_LAYER, max(agg.values())); best_L = max(agg, key=agg.get); best = agg[best_L]; g = best / max(ref, 1e-9)
    summary = "cap by layer %s | best=%s ref(L%d)=%.1f best/ref=%.2fx" % ({k: round(v, 1) for k, v in agg.items()}, best_L, REF_LAYER, ref, g)
    if g >= 1.2 and best_L != ("L%d" % REF_LAYER):
        return ("HARD_PASS", "HARD_PASS: a better layer than L=15 exists (>=1.2x) -- update causal-LM recipe to %s. " % best_L + summary)
    if g >= 0.9:
        return ("MIDDLE_BAND", "MIDDLE_BAND: L=15 ~ optimal (best within 0.9-1.2x). Keep L=15 recipe. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: all layers < 0.9x L=15 (unexpected). " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s layers=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, LAYERS, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); layer_keys = encode_all_layers(load_texts(N_ENC)); print("[encoded] %d layers x %s" % (len(LAYERS), layer_keys[LAYERS[0]].shape), flush=True)
ps = [run_seed(s, layer_keys) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
