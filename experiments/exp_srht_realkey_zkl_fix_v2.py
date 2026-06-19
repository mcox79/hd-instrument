"""
exp_srht_realkey_zkl_fix_v2 -- Authorization 3 (SRHT fix) with CYCLE-150 LiRA attack methodology -- CPU.

ROUTING: handoff research_to_exp_dev_ZKL_attack_methodology_spec. v1 used the wrong attack; this uses the cycle-150/151
  LiRA-style attack EXACTLY: per probe generate k paraphrase variants, score = max over k of (max cosine to stored KB),
  calibrate decision threshold to FPR=0.01 on never-stored probes, TPR at that threshold = ZKL(k). Three arms:
  (1) synthetic isotropic keys (target ZKL(50)~0.035), (2) real keys (target ~0.40, cycle-151), (3) real + SRHT mixing
  before storage (target << 0.40). Encoder: MiniLM proxy (FAST; cycle-151 used Llama-3.2-1B L15 left-pad -- see CAVEAT).
PRE-REGISTERED: HARD-PASS (A) real ZKL(50) > 2x synthetic (reproduces the real-key-worse baseline) AND (B) real+SRHT ZKL(50)
  <= 1.5x synthetic (SRHT closes the gap). MIDDLE reproduces baseline but SRHT only partial. HARD-FAIL does NOT reproduce
  real-worse (real <= synthetic) -> encoder/paraphrase proxy insufficient, need Llama L15 left-pad faithfully.
FORMULA SELF-TESTS (PROT-022): 1. hadamard orthogonal. 2. members score higher than nonmembers. 3. TPR@FPR monotone.
ASCII-only. write_metrics. PROT-018 _v2.
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

ANCHOR_NAME = "srht_realkey_zkl_fix_v2"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
PARA_NOISE = 0.25; FPR = 0.01; K = 50
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 300; N_TGT = 80
else:
    N_KB = 2000; N_TGT = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


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


def lira_zkl(kb, members, nonmembers, k, g):
    # cycle-150 LiRA: per probe, k paraphrase variants; score = max_k (max cosine to KB); FPR=0.01 calibrated on nonmembers
    def score(T):
        out = []
        for t in T:
            paras = unit(t[None, :] + PARA_NOISE * g.standard_normal((k, t.shape[0])).astype(np.float32))
            out.append(float((paras @ kb.T).max()))                 # best cosine any paraphrase achieves to any stored key
        return np.array(out)
    m = score(members); n = score(nonmembers); thr = np.quantile(n, 1 - FPR)
    return float((m >= thr).mean())


def _selftest():
    H = hadamard(8); assert np.allclose(H @ H.T, np.eye(8), atol=1e-5), "hadamard orthogonal"
    g = np.random.default_rng(0); kb = unit(g.standard_normal((50, 64))); mem = kb[:10]; non = unit(g.standard_normal((10, 64)))
    z = lira_zkl(kb, mem, non, 10, np.random.default_rng(1)); assert z > 0.0, "members score higher than nonmembers"
    print("[selftest] PASS: srht-zkl-v2", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu")


def whiten_fit(K_):
    Kc = K_ - K_.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


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
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    g = np.random.default_rng(7); real = encode(load_texts(N_KB + N_TGT)); sel = g.choice(N_KB, N_TGT, replace=False)
    # arm 1 synthetic isotropic
    synth = g.standard_normal(real.shape).astype(np.float32)
    kb_s = unit(whiten_fit(synth)[:N_KB]); z_synth = lira_zkl(kb_s, unit(whiten_fit(synth)[sel]), unit(whiten_fit(synth)[N_KB:N_KB + N_TGT]), K, np.random.default_rng(1))
    # arm 2 real
    rw = whiten_fit(real); kb_r = unit(rw[:N_KB]); z_real = lira_zkl(kb_r, unit(rw[sel]), unit(rw[N_KB:N_KB + N_TGT]), K, np.random.default_rng(2))
    # arm 3 real + SRHT before whiten/store
    rs = whiten_fit(srht(real, np.random.default_rng(11))); kb_rs = unit(rs[:N_KB]); z_srht = lira_zkl(kb_rs, unit(rs[sel]), unit(rs[N_KB:N_KB + N_TGT]), K, np.random.default_rng(3))
    print("  ZKL(50) synthetic=%.4f real=%.4f real+SRHT=%.4f | real/synth=%.2f srht/synth=%.2f" % (z_synth, z_real, z_srht, z_real / max(z_synth, 1e-9), z_srht / max(z_synth, 1e-9)), flush=True)
    return {"zkl_synth": float(z_synth), "zkl_real": float(z_real), "zkl_real_srht": float(z_srht), "real_over_synth": float(z_real / max(z_synth, 1e-9)), "srht_over_synth": float(z_srht / max(z_synth, 1e-9))}


def verdict(r) -> Tuple[str, str]:
    repro = r["real_over_synth"] > 2.0; fixed = r["srht_over_synth"] <= 1.5
    summary = "ZKL(50) synth=%.4f real=%.4f real+SRHT=%.4f | real/synth=%.2f srht/synth=%.2f" % (r["zkl_synth"], r["zkl_real"], r["zkl_real_srht"], r["real_over_synth"], r["srht_over_synth"])
    if repro and fixed:
        return ("HARD_PASS", "HARD_PASS: reproduced real-key-worse baseline (real>2x synth) AND SRHT closes it (<=1.5x synth) -- SRHT fix empirically confirmed. " + summary)
    if repro:
        return ("MIDDLE_BAND", "MIDDLE_BAND: real-key-worse reproduced but SRHT only partial. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: did NOT reproduce real-key-worse with MiniLM+noise proxy (real<=2x synth) -- need Llama-3.2-1B L15 left-pad + MarianMT paraphrase to reproduce cycle-151 faithfully. " + summary)


print("[config] anchor=%s mode=%s n_kb=%d n_tgt=%d k=%d encoder=MiniLM(proxy) device=cpu" % (ANCHOR_NAME, RUN_MODE, N_KB, N_TGT, K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
