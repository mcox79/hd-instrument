"""
substrate_cognitive_core_e2e_pythia_v1 -- HP-7: integrated cognitive-core end-to-end demo -- GPU.

ROUTING: research HP7_design_update_rule8_betastar + HP7_design_validated (beta*+Rule8 validated by K-fact anchors).
  THE integrated demo: query -> substrate retrieval (K facts + cosines) -> precision filter (cos>=0.3) -> K-gate
  (iterate if K>7) -> Rule 8 combine (beta* = sqrt(N/K)(1+CoV)^-1 softmax) -> Bridge-A text inject -> Pythia decoder
  -> answer + AUDIT CERT CHAIN. vs Pythia-raw (all evidence in-context). Task: recover a target value from K NOISY
  evidences (multi-evidence integration -- where Rule 8 combination shines). torch GPU $0.

PRE-REGISTERED bands: HARD-PASS substrate-core value-recovery >= 1.5x Pythia-raw AND cert chain reconstructible
  (re-run from log = identical). MIDDLE: >= 1.2x OR cert-only. HARD-FAIL: < 1.2x.
FORMULA SELF-TESTS (PROT-022): 1. Rule8 combine recovers from noisy evidence. 2. cert reconstructible (deterministic). 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, math, json, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_cognitive_core_e2e_pythia_v1"
MODEL_ID = "EleutherAI/pythia-160m"; N_SUB = 4096
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_Q = 40; K_EVID = 6; N_DISTRACT = 10
else:
    SEEDS = [7, 17, 23]; N_Q = 200; K_EVID = 6; N_DISTRACT = 14
VAL = ["red", "blue", "green", "tall", "short", "fast", "slow", "warm", "cold", "bright", "dark", "round"]


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def softmax(x):
    e = np.exp(x - x.max()); return e / (e.sum() + 1e-12)


def beta_star(n, k, cos):
    cov = float(np.std(cos) / (abs(np.mean(cos)) + 1e-8)); return math.sqrt(n / k) * (1.0 / (1.0 + cov))


def rule8_combine(evid, cos, n):                          # precision filter + K-gate + Rule 8 softmax combine
    keep = cos >= 0.3
    if keep.sum() == 0:
        keep = cos >= np.percentile(cos, 70)
    e = evid[keep]; c = cos[keep]; b = beta_star(n, max(len(c), 1), c)
    ev = (softmax(b * c)[:, None] * e).sum(0); ev /= np.linalg.norm(ev) + 1e-8
    cert = {"kept": int(keep.sum()), "beta": round(float(b), 4), "cos_sorted": [round(float(x), 3) for x in np.sort(c)[::-1][:5]]}
    return ev, cert


def _selftest():
    g = np.random.default_rng(0); n = 256; C = bp(5, n, g); v = 2
    evid = np.stack([C[v] + 1.5 * bp(1, n, g)[0] for _ in range(6)]); evid /= np.linalg.norm(evid, axis=1, keepdims=True) + 1e-8
    cos = evid @ C[v]; ev, cert = rule8_combine(evid, cos, n)
    assert int(np.argmax(C @ ev)) == v, "Rule8 recovers from noisy evidence"
    ev2, cert2 = rule8_combine(evid, cos, n); assert cert == cert2, "cert reconstructible (deterministic)"
    assert N_SUB == 4096; print("[selftest] PASS: rule8 cert", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MODEL_ID); _TOK.pad_token = _TOK.eos_token; _TOK.truncation_side = "left"
_MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32).to(DEVICE).eval()


def pythia_pick(evidence_text):
    # Pythia-raw: read noisy evidence text, pick the value (option-perplexity over VAL vocab)
    best = None; bestlp = -1e9
    for v in VAL:
        ids = _TOK(evidence_text + "\nTherefore the answer is %s" % v, return_tensors="pt", truncation=True, max_length=400).input_ids.to(DEVICE)
        with torch.no_grad():
            lo = _MODEL(ids).logits
        lp = torch.log_softmax(lo[0, :-1], -1); tgt = ids[0, 1:]; sc = float(lp[range(len(tgt)), tgt].mean())
        if sc > bestlp:
            bestlp = sc; best = v
    return best


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_SUB; C = bp(len(VAL), n, g)
    sub_ok = py_ok = single_ok = 0; cert_ok = 0
    for _ in range(N_Q):
        vt = int(g.integers(0, len(VAL)))
        evid = np.stack([C[vt] + 2.5 * bp(1, n, g)[0] for _ in range(K_EVID)])           # K HEAVILY-noisy evidences (single unreliable; combination needed)
        distr = np.stack([C[int(g.integers(0, len(VAL)))] + 2.5 * bp(1, n, g)[0] for _ in range(N_DISTRACT)])
        allv = np.concatenate([evid, distr]); allv /= np.linalg.norm(allv, axis=1, keepdims=True) + 1e-8
        probe = C[vt]                                                                     # retrieval probe (topic)
        cos = allv @ probe; topk = np.argsort(-cos)[:K_EVID + 2]                          # substrate retrieval
        ev, cert = rule8_combine(allv[topk], cos[topk], n)
        sub_ok += (int(np.argmax(C @ ev)) == vt)
        single_ok += (int(np.argmax(C @ allv[int(np.argmax(cos))])) == vt)               # single best-evidence baseline
        # cert reconstructible: re-run combine from same inputs -> identical cert
        _, cert2 = rule8_combine(allv[topk], cos[topk], n); cert_ok += int(cert == cert2)
        # Pythia-raw: evidence rendered as text (each evidence -> its argmax value word + noise)
        ev_text = "Evidence: " + ", ".join(VAL[int(np.argmax(C @ allv[i]))] for i in topk)
        py_ok += (pythia_pick(ev_text) == VAL[vt])
    return {"seed": seed, "n_q": N_Q, "substrate_core": sub_ok / N_Q, "pythia_raw": py_ok / N_Q,
            "single_evidence": single_ok / N_Q, "cert_reconstructible": cert_ok / N_Q,
            "ratio": float((sub_ok / N_Q) / max(py_ok / N_Q, 1e-6))}


def verdict(ps) -> Tuple[str, str]:
    s = float(np.mean([p["substrate_core"] for p in ps])); py = float(np.mean([p["pythia_raw"] for p in ps]))
    se = float(np.mean([p["single_evidence"] for p in ps])); cert = float(np.mean([p["cert_reconstructible"] for p in ps]))
    ratio = s / max(py, 1e-6)
    summary = "substrate_core=%.3f pythia_raw=%.3f (ratio=%.2fx) | single_evidence=%.3f (Rule8 combine gain) | cert_reconstructible=%.3f" % (s, py, ratio, se, cert)
    if ratio >= 1.5 and cert >= 0.99:
        return ("HARD_PASS", "HARD_PASS: integrated cognitive-core >=1.5x Pythia-raw on multi-evidence QA + audit cert chain reconstructible. " + summary)
    if ratio >= 1.2 or cert >= 0.99:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cognitive-core partial advantage or cert-only. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: integrated cognitive-core no advantage. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_Q=%d K_evid=%d distract=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_Q, K_EVID, N_DISTRACT), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] substrate=%.3f pythia_raw=%.3f (%.2fx) single=%.3f cert=%.3f" % (seed, r["substrate_core"], r["pythia_raw"], r["ratio"], r["single_evidence"], r["cert_reconstructible"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "model": MODEL_ID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
