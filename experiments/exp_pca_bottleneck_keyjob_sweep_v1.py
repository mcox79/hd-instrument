"""
exp_pca_bottleneck_keyjob_sweep_v1 -- manifold mitigation: substrate KEY-job pinv recovery vs PCA truncation dim -- GPU.

ROUTING: handoff research_to_exp_dev_manifold_bottleneck_sweep (substrate-side half). The manifold diagnostic found Llama-L15
  intrinsic dim ~30. The mitigation idea: truncate embeddings to d dims to kill membership leakage. The risk Research flagged
  is that the substrate KEY job (pinv associative recovery) also lives in those dims, so recovery may collapse. This cell
  measures the KEY-job side: pinv exact-recovery F1 as a function of PCA-truncation dim d in {5,10,20,30,50,100,full}, so we
  know how far we can truncate before the substrate loses its facts. (ZKL/MarianMT half flagged separately -- de-en model
  not cached on runner.) GPU for the Llama encode.
PRE-REGISTERED: HARD-PASS KEY-job F1 stays >= 0.90 at d <= 30 (can truncate to the manifold dim without losing facts; the
  privacy-truncation mitigation has headroom). MIDDLE F1 >= 0.90 only at d >= 50. HARD-FAIL F1 < 0.90 even at d=100.
FORMULA SELF-TESTS (PROT-022): 1. full-dim recovery perfect. 2. PCA orthonormal. 3. truncation reduces dim.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "pca_bottleneck_keyjob_sweep_v1"
MODEL = "meta-llama/Llama-3.2-1B"; LAYER = 15
DIMS = [5, 10, 20, 30, 50, 100]
CORPUS = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FACTS = 200 if RUN_MODE == "smoke" else 1000


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def pca_fit(E, d):
    mu = E.mean(0); Ec = E - mu; U, S, Vt = np.linalg.svd(Ec, full_matrices=False)
    return mu, Vt[:d]   # top-d principal directions


def keyjob_f1(K):
    # pinv hetero-associative recovery: store key->id, recover argmax W k == id. F1 = recovery rate.
    n = K.shape[0]; Kc = unit(K).astype(np.float64)
    G = Kc @ Kc.T + 1e-3 * np.eye(n); Winv = np.linalg.solve(G, Kc)   # (K K^T + r)^-1 K   [n x d]
    scores = Kc @ Winv.T                                              # [n x n], row i recovers id
    return float((np.argmax(scores, axis=1) == np.arange(n)).mean())


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((30, 64)); assert keyjob_f1(K) >= 0.95, "full-dim recovery perfect"
    mu, V = pca_fit(g.standard_normal((50, 20)), 5); assert abs((V @ V.T - np.eye(5)).max()) < 1e-4, "PCA orthonormal"
    assert V.shape[0] == 5, "truncation reduces dim"
    print("[selftest] PASS: pca-bottleneck-keyjob", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def load_texts(n):
    out = []
    if not CORPUS.exists():
        return out
    for l in open(CORPUS, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        t = r.get("long_answer") or r.get("question") or ""
        if isinstance(t, str) and len(t) > 30:
            out.append(t[:400])
        if len(out) >= n:
            break
    return out


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t, output_hidden_states=True)
        out.append(o.hidden_states[LAYER][:, -1, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 1), np.float32)


def run() -> Dict:
    texts = load_texts(N_FACTS)
    if len(texts) < 50:
        print("[FATAL] corpus too small", flush=True); return {"by": {}, "n": 0}
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    E = encode(texts, tok, m); del m; torch.cuda.empty_cache()
    by = {"full": keyjob_f1(E)}
    for d in DIMS:
        mu, V = pca_fit(E, d); Ed = (E - mu) @ V.T; by["d%d" % d] = keyjob_f1(Ed)
    for k in (["full"] + ["d%d" % d for d in DIMS]):
        print("  KEY-job F1 [%s] = %.3f" % (k, by[k]), flush=True)
    return {"by": by, "n": len(E), "f1_d30": by.get("d30", 0.0), "f1_d100": by.get("d100", 0.0)}


def verdict(r) -> Tuple[str, str]:
    summary = "KEY-job pinv F1 by PCA dim: %s (n=%d)" % ({k: round(v, 3) for k, v in r["by"].items()}, r["n"])
    if r["f1_d30"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS: substrate KEY-job F1>=0.90 at d<=30 -- can truncate to the manifold dim without losing facts; privacy-truncation mitigation has headroom (the facts survive; only the membership-leakage dims need to go). " + summary)
    if r["f1_d100"] >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: KEY-job F1>=0.90 only at d>=50 -- truncation to manifold dim costs some recovery; tension with privacy. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: KEY-job F1<0.90 even at d=100 -- pinv recovery needs high dim; truncation mitigation would break the substrate. " + summary)


print("[config] anchor=%s mode=%s n_facts=%d dims=%s model=%s" % (ANCHOR_NAME, RUN_MODE, N_FACTS, DIMS, MODEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
