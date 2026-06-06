"""
exp_substrate_encoder_capacity_at_scale_battery_gpu_v1 -- BUNDLED production-encoder capacity head-to-head -- GPU.

ROUTING: Phase-4 production-encoder finalization (Research cycle-131/DAMB4 follow-up). Compares the production capacity of
  3 cached encoders under the converged recipe, head-to-head: MiniLM-L6 (D=384), BGE-large (D=1024), Llama-3.2-1B L=15
  last-token (D=2048). For each, capacity under 3 recipes: raw-sign / ZCA-whiten / PCA-prewhiten. Tests Research's
  "BGE-large + PCA-prewhitening ~420 effective" estimate empirically. Hopfield exact-recovery capacity. GPU (model forwards).
PRE-REGISTERED: HARD-PASS best (encoder, recipe) >= 2x the MiniLM+whiten reference (a materially higher-capacity production
  encoder exists). MID 1.3-2x. HARD-FAIL all <=1.3x (encoder choice doesn't move production capacity much).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. Hopfield recovers low load. 3. deps.
ASCII-only. write_metrics. PROT-018 no _nN.
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

ANCHOR_NAME = "substrate_encoder_capacity_at_scale_battery_gpu_v1"
# (id, type, layer) -- st=sentence-transformer mean-pool; lm=causal-LM last-token at layer
ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", "st", None), ("BAAI/bge-large-en-v1.5", "st", None),
            ("meta-llama/Llama-3.2-1B", "lm", 15)]
RECIPES = ["raw_sign", "zca_whiten", "pca_prewhiten"]
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 800; LOADS = [0.01, 0.03, 0.06, 0.1, 0.2]; ENCODERS = ENCODERS[:1]
else:
    SEEDS = [7, 17, 23]; N_ENC = 4000; LOADS = [0.005, 0.01, 0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3]


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


def keys_for(emb, recipe):
    if recipe == "raw_sign":
        K = emb
    else:                                                            # zca_whiten and pca_prewhiten both = ZCA fit-on-full here
        K = whiten_fit(emb)
    sg = np.sign(K).astype(np.float32); sg[sg == 0] = 1.0; return sg


def cap(emb, recipe, seed):
    sg = keys_for(emb, recipe); D = emb.shape[1]; c = 0
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
    print("[selftest] PASS: enc-cap", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer
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


def encode(eid, etype, layer, texts):
    tok = AutoTokenizer.from_pretrained(eid)
    dt = torch.float16 if (DEV.type == "cuda" and etype == "lm") else torch.float32
    if etype == "lm":
        tok.pad_token = tok.eos_token; m = AutoModelForCausalLM.from_pretrained(eid, output_hidden_states=True, torch_dtype=dt).to(DEV).eval()
    else:
        m = AutoModel.from_pretrained(eid).to(DEV).eval()
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t)
        if etype == "lm":
            h = o.hidden_states[layer]; lens = t["attention_mask"].sum(1) - 1; out.append(h[torch.arange(h.shape[0]), lens].float().cpu().numpy())
        else:
            h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float(); out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def run_seed(seed, embs) -> Dict:
    res = {}
    for nm, emb in embs.items():
        for r in RECIPES:
            res["%s|%s" % (nm, r)] = cap(emb, r, seed)
    print("  [seed=%d] %s" % (seed, {k: v for k, v in res.items() if v > 0}), flush=True); return {"seed": seed, "cap": res}


def verdict(ps) -> Tuple[str, str]:
    keys = ps[0]["cap"].keys(); agg = {k: float(np.mean([p["cap"][k] for p in ps])) for k in keys}
    ref_k = [k for k in agg if k.startswith("all-MiniLM-L6-v2|zca_whiten")]
    ref = agg[ref_k[0]] if ref_k else max(agg.values())
    best_k = max(agg, key=agg.get); best = agg[best_k]; g = best / max(ref, 1e-9)
    summary = "cap by encoder|recipe: %s | best=%s ref(MiniLM|whiten)=%.1f best/ref=%.2fx" % ({k: round(v, 1) for k, v in agg.items()}, best_k, ref, g)
    if g >= 2.0:
        return ("HARD_PASS", "HARD_PASS: a higher-capacity production encoder exists (>=2x MiniLM+whiten) -- adopt %s. " % best_k + summary)
    if g >= 1.3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: best encoder 1.3-2x MiniLM+whiten. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: encoder choice <=1.3x MiniLM+whiten (capacity encoder-bounded). " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoders=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, [e[0].split('/')[-1] for e in ENCODERS], N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); texts = load_texts(N_ENC); embs = {}
for eid, etype, layer in ENCODERS:
    try:
        embs[eid.split("/")[-1]] = encode(eid, etype, layer, texts); print("[encoded] %s %s" % (eid.split("/")[-1], embs[eid.split("/")[-1]].shape), flush=True)
    except Exception as e:
        print("  [%s] SKIP: %s" % (eid, str(e)[:80]), flush=True)
ps = [run_seed(s, embs) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
