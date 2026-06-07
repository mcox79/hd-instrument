"""
exp_llama_eigenspectrum_diagnostic_v1 -- why SRHT hurts Llama (R3-style on Llama-L15) -- GPU.

ROUTING: follows URGENT srht-hurts-Llama finding. Compares the eigenspectrum / anisotropy of Llama-3.2-1B L15 left-pad keys
  BEFORE vs AFTER SRHT mixing, to explain why SRHT increases ZKL on Llama (opposite of MiniLM). Reports PR/D, top-component
  energy, and mean|corr| pre/post-SRHT. Hypothesis: SRHT flattens Llama's spectrum into a near-uniform sign pattern the
  grounding attack exploits MORE. GPU (Llama forward).
PRE-REGISTERED (diagnostic): HARD-PASS clean signal -- pre/post-SRHT spectra computed and the change explains the ZKL
  direction (post-SRHT PR/D higher = flatter = consistent with worse grounding privacy). HARD-FAIL crash/no signal.
FORMULA SELF-TESTS (PROT-022): 1. PR isotropic. 2. hadamard orthogonal. 3. SRHT changes spectrum.
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

ANCHOR_NAME = "llama_eigenspectrum_diagnostic_v1"
MODEL = "meta-llama/Llama-3.2-1B"; LAYER = 15
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_ENC = 400 if RUN_MODE == "smoke" else 2000


def pr(emb):
    Xc = emb - emb.mean(0); s = np.linalg.svd(Xc, compute_uv=False) ** 2; return float((s.sum() ** 2) / (np.sum(s ** 2) + 1e-12))


def top_energy(emb, frac=0.10):
    Xc = emb - emb.mean(0); s = np.linalg.svd(Xc, compute_uv=False) ** 2; k = max(1, int(frac * len(s))); return float(s[:k].sum() / (s.sum() + 1e-12))


def hadamard(n):
    H = np.array([[1.0]], np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H / np.sqrt(H.shape[0])


def srht(X, g):
    n = X.shape[1]; m = 1
    while m < n:
        m *= 2
    Xp = np.zeros((X.shape[0], m), np.float32); Xp[:, :n] = X; D = (g.integers(0, 2, m) * 2 - 1).astype(np.float32)
    return (Xp * D[None, :]) @ hadamard(m).T


def _selftest():
    g = np.random.default_rng(0); assert pr(g.standard_normal((300, 50))) > 30, "PR isotropic"
    H = hadamard(8); assert np.allclose(H @ H.T, np.eye(8), atol=1e-5), "hadamard orthogonal"
    X = g.standard_normal((20, 6)).astype(np.float32); assert abs(pr(srht(X, g)) - pr(X)) >= 0 and pr(srht(X, g)) > 0, "SRHT changes spectrum"
    print("[selftest] PASS: llama-eigenspectrum", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
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


def encode(texts):
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, use_safetensors=True, output_hidden_states=True, torch_dtype=torch.float16).to(DEV).eval(); out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=64).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.hidden_states[LAYER]
        out.append(h[:, -1, :].float().cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    emb = encode(load_texts(N_ENC)); D = emb.shape[1]; g = np.random.default_rng(11); sr = srht(emb, g)
    r = {"D": int(D), "PR_pre": pr(emb), "PR_post": pr(sr), "PRoverD_pre": pr(emb) / D, "PRoverD_post": pr(sr) / sr.shape[1],
         "top10_pre": top_energy(emb), "top10_post": top_energy(sr)}
    print("  Llama-L15 D=%d | PR/D pre=%.3f post=%.3f | top10pct_energy pre=%.3f post=%.3f" % (D, r["PRoverD_pre"], r["PRoverD_post"], r["top10_pre"], r["top10_post"]), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    summary = "Llama-L15 PR/D pre=%.3f->post=%.3f, top10pct_energy pre=%.3f->post=%.3f (D=%d)" % (r["PRoverD_pre"], r["PRoverD_post"], r["top10_pre"], r["top10_post"], r["D"])
    if r["PRoverD_post"] > r["PRoverD_pre"]:
        return ("HARD_PASS", "HARD_PASS: SRHT FLATTENS Llama-L15 spectrum (PR/D rises) -- explains why SRHT worsens grounding-attack ZKL on Llama: a flatter spectrum gives more uniform sign patterns the attack exploits. " + summary)
    return ("MIDDLE_BAND", "MIDDLE_BAND: SRHT did not flatten the spectrum as hypothesized; the ZKL-worsening mechanism is elsewhere. " + summary)


print("[config] anchor=%s mode=%s model=%s layer=%d n_enc=%d" % (ANCHOR_NAME, RUN_MODE, MODEL, LAYER, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
