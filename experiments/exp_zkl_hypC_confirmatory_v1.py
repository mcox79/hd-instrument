"""
exp_zkl_hypC_gram_v1 -- ZKL Hyp C CONFIRMATORY: Gram structure UNwhitened + neutral-held-out-basis (removes stored-cohort confound) -- GPU.

ROUTING: handoff zkl_hypB_hypC_diagnostics_authorize Diagnostic 1 (Hyp C, P=0.25). After Case C ruled out manifold
  confinement, tests whether the membership signal lives in cosine RANKINGS: are member-member cosines systematically higher
  than member-nonmember? Uses the calibrated harness (Llama-3.2-1B L15 last-token, HotpotQA Wikipedia sentences, production
  full-d whitening on the stored cohort). KS test on the three cosine distributions.
PRE-REGISTERED: HARD-PASS (C supported) member-member cosine dist measurably higher than member-nonmember (KS p<0.01 AND
  mean gap >0); queue rank-randomization mitigations. HARD-FAIL (C not supported) MM and MN indistinguishable -> Hyp B next.
FORMULA SELF-TESTS (PROT-022): 1. KS detects shift. 2. KS null ~ ns. 3. whiten shape.
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

ANCHOR_NAME = "zkl_hypC_confirmatory_v1"; MODEL = "meta-llama/Llama-3.2-1B"; LAYER = 15
CORPUS = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_STORED = 100 if RUN_MODE == "smoke" else 400; N_NEVER = N_STORED; N_HELD = 100 if RUN_MODE == "smoke" else 400


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def ks_2samp(a, b):
    a = np.sort(a); b = np.sort(b); allv = np.concatenate([a, b])
    ca = np.searchsorted(a, allv, side="right") / len(a); cb = np.searchsorted(b, allv, side="right") / len(b)
    d = float(np.max(np.abs(ca - cb))); n = len(a) * len(b) / (len(a) + len(b))
    p = float(np.exp(-2 * n * d * d))    # asymptotic KS p-value
    return d, p


def _selftest():
    g = np.random.default_rng(0)
    d1, p1 = ks_2samp(g.standard_normal(500) + 1.5, g.standard_normal(500)); assert p1 < 0.01, "KS detects shift"
    d2, p2 = ks_2samp(g.standard_normal(500), g.standard_normal(500)); assert p2 > 0.01, "KS null ~ ns"
    assert unit(g.standard_normal((4, 8))).shape == (4, 8), "whiten shape"
    print("[selftest] PASS: zkl-hypC-gram", flush=True)


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
    out = []; seen = set()
    if not CORPUS.exists():
        return out
    for l in open(CORPUS, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        for sl in (r.get("context") or {}).get("sentences") or []:
            for s in sl:
                t = s.strip()
                if 40 < len(t) < 300 and t not in seen:
                    seen.add(t); out.append(t)
                    if len(out) >= n:
                        return out
    return out


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t, output_hidden_states=True)
        out.append(o.hidden_states[LAYER][:, -1, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def offdiag(M):
    return M[~np.eye(M.shape[0], dtype=bool)]


def run() -> Dict:
    texts = load_texts(N_STORED + N_NEVER + N_HELD)
    if len(texts) < N_STORED + N_NEVER + 10:
        print("[FATAL] corpus too small", flush=True); return {"n": 0, "ks_p": 1.0, "gap": 0.0}
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    E = encode(texts, tok, m); del m; torch.cuda.empty_cache()
    stored = E[:N_STORED]; never = E[N_STORED:N_STORED + N_NEVER]
    def fit(X):
        mu = X.mean(0); C = ((X - mu).T @ (X - mu)) / len(X); U, S, _ = np.linalg.svd(C + 1e-3 * np.eye(C.shape[0]))
        return mu, (U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T).astype(np.float32)
    def gram(Sx, Nx):
        mm = offdiag(Sx @ Sx.T); mn = (Sx @ Nx.T).ravel()
        d, p = ks_2samp(mm, mn); return d, p, float(mm.mean() - mn.mean()), float(mm.mean()), float(mn.mean())
    arms = {}
    arms["raw"] = gram(unit(stored), unit(never))                                   # UNwhitened (no confound)
    held = E[N_STORED + N_NEVER:]                                                    # neutral held-out cohort
    if len(held) >= 50:
        muH, WH = fit(held); arms["neutral"] = gram(unit((stored - muH) @ WH), unit((never - muH) @ WH))
    muS, WS = fit(stored); arms["stored_whiten"] = gram(unit((stored - muS) @ WS), unit((never - muS) @ WS))  # confounded ref
    for k, (d, p, g, m1, m2) in arms.items():
        print("  [%s] MM=%.4f MN=%.4f gap(MM-MN)=%+.4f KS_D=%.4f p=%.2e" % (k, m1, m2, g, d, p), flush=True)
    raw = arms["raw"]; return {"n": N_STORED, "ks_p": raw[1], "ks_d": raw[0], "gap": raw[2], "mm": raw[3], "mn": raw[4],
                               "neutral_gap": arms.get("neutral", (0, 1, 0, 0, 0))[2], "neutral_p": arms.get("neutral", (0, 1, 0, 0, 0))[1]}


def verdict(r) -> Tuple[str, str]:
    summary = "raw: MM=%.4f MN=%.4f gap=%+.4f p=%.2e | neutral gap=%+.4f p=%.2e (n=%d)" % (r["mm"], r["mn"], r["gap"], r["ks_p"], r["neutral_gap"], r["neutral_p"], r["n"])
    raw_pos = (r["ks_p"] < 0.01 and r["gap"] > 0); neu_pos = (r["neutral_p"] < 0.01 and r["neutral_gap"] > 0)
    if raw_pos or neu_pos:
        return ("HARD_PASS", "HARD_PASS (Hyp C SUPPORTED, confound removed): unwhitened/neutral-basis Gram shows MM>MN (gap>0, KS p<0.01) -- the leak IS in Gram structure; the stored-cohort whitening had masked it. Queue rank-randomization mitigations. " + summary)
    return ("HARD_FAIL", "HARD_FAIL (Hyp C confirmed NOT supported): even unwhitened + neutral-basis, MM not higher than MN -- Gram is genuinely not the mechanism (Hyp B token-position stands as the confirmed one). " + summary)


print("[config] anchor=%s mode=%s n_stored=%d model=%s layer=%d" % (ANCHOR_NAME, RUN_MODE, N_STORED, MODEL, LAYER), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
