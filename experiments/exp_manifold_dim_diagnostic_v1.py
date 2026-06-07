"""
exp_manifold_dim_diagnostic_v1 -- privacy: intrinsic dimensionality of Llama-L15 stored-fact embeddings -- CPU.

ROUTING: handoff research_to_exp_dev_manifold_diagnostic_authorize. Diagnostic-only (classification, not pass/fail). If the
  production Llama-3.2-1B L15 embeddings of stored facts lie on a low-dim manifold (intrinsic dim < 200 of 2048), the ZKL
  leakage may be manifold-confined and a manifold-projection mitigation is the next test. Estimates intrinsic dim three ways:
  PCA participation ratio, PCA 95%-energy dim, and TwoNN (Facco et al.) MLE. Uses the mandated Llama L15 left-pad harness. CPU.
PRE-REGISTERED (classification): manifold-confined if intrinsic dim < 200; diffuse if >= 200. Reports all three estimators
  + ambient dim. No HARD-PASS/FAIL (diagnostic) -- verdict carries the classification for Research to route the mitigation.
FORMULA SELF-TESTS (PROT-022): 1. PR of isotropic ~ d. 2. PR of rank-1 ~ 1. 3. TwoNN positive.
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

ANCHOR_NAME = "manifold_dim_diagnostic_v1"
MODEL = "meta-llama/Llama-3.2-1B"; LAYER = 15
CORPUS = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FACTS = 400 if RUN_MODE == "smoke" else 2000


def participation_ratio(eigs):
    eigs = np.clip(eigs, 0, None); return float((eigs.sum() ** 2) / ((eigs ** 2).sum() + 1e-12))


def energy_dim(eigs, frac=0.95):
    eigs = np.sort(np.clip(eigs, 0, None))[::-1]; c = np.cumsum(eigs) / (eigs.sum() + 1e-12)
    return int(np.searchsorted(c, frac) + 1)


def twonn(X, frac=0.9):
    # Facco et al. TwoNN intrinsic dim MLE via the ratio of 2nd to 1st nearest-neighbor distances.
    from numpy.linalg import norm
    n = X.shape[0]; mu = []
    for i in range(n):
        d = norm(X - X[i], axis=1); d.sort()
        r1, r2 = d[1], d[2]
        if r1 > 1e-9:
            mu.append(r2 / r1)
    mu = np.sort(np.array(mu)); mu = mu[mu > 1.0]
    if len(mu) < 10:
        return 0.0
    k = int(frac * len(mu)); mu = mu[:k]
    F = np.arange(1, len(mu) + 1) / len(mu)
    x = np.log(mu); y = -np.log(1 - F + 1e-12)
    d_est = float((x @ y) / (x @ x + 1e-12))   # slope through origin
    return d_est


def _selftest():
    g = np.random.default_rng(0); X = g.standard_normal((300, 10)); e = np.linalg.eigvalsh(np.cov(X.T))
    assert participation_ratio(e) > 6, "PR of isotropic ~ d"
    r1 = np.outer(g.standard_normal(50), g.standard_normal(10)); e1 = np.linalg.eigvalsh(np.cov(r1.T))
    assert participation_ratio(e1) < 2, "PR of rank-1 ~ 1"
    assert twonn(g.standard_normal((200, 5))) > 0, "TwoNN positive"
    print("[selftest] PASS: manifold-dim", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required (Llama encoder).", flush=True); sys.exit(1)
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
        print("[FATAL] corpus too small", flush=True); return {"n": 0, "pr": 0.0, "energy95": 0, "twonn": 0.0, "ambient": 0}
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    E = encode(texts, tok, m); del m; torch.cuda.empty_cache()
    Ec = E - E.mean(0); cov = (Ec.T @ Ec) / Ec.shape[0]; eigs = np.linalg.eigvalsh(cov)
    pr = participation_ratio(eigs); e95 = energy_dim(eigs, 0.95)
    sub = Ec[np.random.default_rng(0).choice(len(Ec), min(400, len(Ec)), replace=False)]
    tnn = twonn(sub.astype(np.float64))
    print("  ambient=%d PR=%.1f energy95_dim=%d TwoNN=%.1f (n=%d)" % (E.shape[1], pr, e95, tnn, len(E)), flush=True)
    return {"n": len(E), "ambient": int(E.shape[1]), "pr": pr, "energy95": e95, "twonn": tnn}


def verdict(r) -> Tuple[str, str]:
    pr = r["pr"]; e95 = r["energy95"]; tnn = r["twonn"]
    summary = "PR=%.1f energy95_dim=%d TwoNN=%.1f ambient=%d (n=%d)" % (pr, e95, tnn, r["ambient"], r["n"])
    confined = (e95 < 200) or (tnn > 0 and tnn < 200)
    if confined:
        return ("MIDDLE_BAND", "DIAGNOSTIC manifold-CONFINED: Llama-L15 stored-fact embeddings lie on a low-dim manifold (intrinsic dim <200 of %d) -- ZKL leakage may be manifold-confined; next test = manifold-projection mitigation. " % r["ambient"] + summary)
    return ("HARD_FAIL", "DIAGNOSTIC manifold-DIFFUSE: intrinsic dim >=200 -- leakage is not low-dim-confined; manifold projection unlikely to help. " + summary)


print("[config] anchor=%s mode=%s n_facts=%d model=%s layer=%d" % (ANCHOR_NAME, RUN_MODE, N_FACTS, MODEL, LAYER), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
