"""
exp_r3_encoder_anisotropy_diagnostic_v1 -- Authorization 2 (R3 diagnostic; gates SRHT engineering) -- CPU.

ROUTING: handoff research_to_orchestrator_exp_dev_8_authorizations #2. Cycle 151 showed real-key ZKL is ~11x worse than
  synthetic; the suspected cause is encoder ANISOTROPY (keys concentrate energy in few directions, so sign-quantization +
  whitening leak more on real keys). This diagnoses anisotropy on real MiniLM keys: participation ratio (effective dim
  fraction), mean off-diagonal correlation, top-component energy concentration. Confirms/refutes anisotropy as the ZKL root
  cause and scopes the 3-5 day SRHT fix (Authorization 3, conditional on this). Real MiniLM. CPU.
PRE-REGISTERED: HARD-PASS anisotropy CONFIRMED (PR/D < 0.50 AND mean|corr| > 0.05 AND top-10pct components hold > 0.50
  energy) -> SRHT justified. MIDDLE partial. HARD-FAIL near-isotropic (PR/D > 0.70) -> anisotropy is NOT the cause, SRHT
  won't fix ZKL, re-scope.
FORMULA SELF-TESTS (PROT-022): 1. isotropic PR ~ D. 2. anisotropic PR small. 3. corr bound.
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
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "r3_encoder_anisotropy_diagnostic_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_ENC = 600 if RUN_MODE == "smoke" else 3000


def participation_ratio(emb):
    Xc = emb - emb.mean(0); s = np.linalg.svd(Xc, compute_uv=False); s2 = s ** 2
    return float((s2.sum() ** 2) / (np.sum(s2 ** 2) + 1e-12))


def mean_abs_corr(emb):
    e = emb / (emb.std(0, keepdims=True) + 1e-8); C = np.corrcoef(e.T); iu = np.triu_indices(C.shape[0], 1)
    return float(np.mean(np.abs(C[iu])))


def top_energy(emb, frac=0.10):
    Xc = emb - emb.mean(0); s = np.linalg.svd(Xc, compute_uv=False); s2 = s ** 2; k = max(1, int(frac * len(s2)))
    return float(s2[:k].sum() / (s2.sum() + 1e-12))


def _selftest():
    g = np.random.default_rng(0); iso = g.standard_normal((400, 64)); assert participation_ratio(iso) > 40, "isotropic PR ~ D"
    aniso = g.standard_normal((400, 1)) @ g.standard_normal((1, 64)) + 0.01 * g.standard_normal((400, 64)); assert participation_ratio(aniso) < 10, "anisotropic PR small"
    assert 0 <= mean_abs_corr(iso) <= 1, "corr bound"
    print("[selftest] PASS: r3-anisotropy", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu")


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
    emb = encode(load_texts(N_ENC)); D = emb.shape[1]
    pr = participation_ratio(emb); corr = mean_abs_corr(emb); te = top_energy(emb, 0.10)
    print("  D=%d PR=%.1f PR/D=%.3f mean|corr|=%.4f top10pct_energy=%.3f" % (D, pr, pr / D, corr, te), flush=True)
    return {"D": int(D), "PR": pr, "PR_over_D": pr / D, "mean_abs_corr": corr, "top10pct_energy": te}


def verdict(r) -> Tuple[str, str]:
    prd = r["PR_over_D"]; corr = r["mean_abs_corr"]; te = r["top10pct_energy"]
    summary = "PR/D=%.3f mean|corr|=%.4f top10pct_energy=%.3f (D=%d, PR=%.1f)" % (prd, corr, te, r["D"], r["PR"])
    if prd < 0.50 and corr > 0.05 and te > 0.50:
        return ("HARD_PASS", "HARD_PASS: encoder is ANISOTROPIC (PR/D<0.50, correlated dims, top-10pct hold >50pct energy) -- confirms anisotropy as the real-key ZKL root cause; SRHT engineering (Auth 3) justified. " + summary)
    if prd < 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial anisotropy -- SRHT may help but ZKL gap not fully explained by anisotropy. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: encoder near-isotropic (PR/D>0.70) -- anisotropy is NOT the ZKL cause; SRHT won't fix it, re-scope the real-key ZKL gap. " + summary)


print("[config] anchor=%s mode=%s n_enc=%d device=cpu" % (ANCHOR_NAME, RUN_MODE, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
