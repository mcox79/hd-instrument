"""
pythia_kv_recall_reality_v3_1_gpu_v1 -- substrate-KV RECALL-REALITY: do VALUE-CUE queries (omitting the entity-id)
retrieve the right stored fact via MEAN-CENTERED cosine over Pythia-2.8B hidden-state keys? GPU(encode)+CPU(recall).
TIER-2 re-run of the by-construction-SATURATED pythia-KV v2 (Skunkworks SCHEMA-VET GO v3.1).

DESIGN FINDINGS baked in (diagnosed on pythia-160m this build):
  - pythia embeddings are strongly ANISOTROPIC (raw cos(any,any)~1.0) -> raw-cosine + ZCA-whitening both FAIL to
    separate keys. FIX = MEAN-CENTERING (subtract key-mean) -> keys separable (max-cos-to-other 1.000->0.726) and
    query aligns to own key (cos 0.003->0.387). [corroborates the effrank isotropy finding: anisotropic LM embeddings
    are poor substrate-KV keys without centering.]
  - templated facts with number-suffix ids (alpha-N) collapse; use DIVERSE real-token content + a UNIQUE value (year)
    per fact so keys are distinct and the value-cue has a unique retrieval target.

SCOPE (Sharpening 2): RECALL-REALITY (semantic cue -> right fact), NOT a capacity cliff (NN/cosine has no crosstalk;
separability-limited). Crosstalk CAPACITY = separate future Hebbian-superposition cert (effrank instrument).

CUES per fact "the {adj} {noun} was {prop} {valword} {year}":
  - VALUE-CUE (LOAD-BEARING): "Which one was {prop} {valword} {year}?" -- OMITS the entity -> semantic value->entity.
  - PARAPHRASE / DIFFERENT-RELATION (REPORTED only): contain the entity tokens.

GATES (v3.1):
  PRE-FLIGHT A (HARD): median cos(value-query, own-key) NOT > 0.98 (else surface-dominated -> abort).
  PRE-FLIGHT B (HARD, KEY-SEPARABILITY): median max-cos(key, OTHER key) < 0.95 (else keys non-separable -> construction
    broken -> abort). [the missing guard that v3.1-draft lacked; anisotropy/template-collapse is caught here.]
  SELF-TEST CAN-FAIL (HARD): decoupled random query MUST return recall < 0.5.
  HARD_PASS: value-cue recall >= 0.80 at M in {2k,10k} AND noise-scaled(0.5*NN-dist) recall >= 0.80 AND 5-seed std in
    (0, 0.05) (reproducible, NOT zero) AND both pre-flights pass.
  MIDDLE: value-cue recall in [0.5,0.8). HARD_FAIL: recall<0.5 OR std==0 OR a pre-flight fails. cliff REPORTED.

NOTE: pythia-160m (smoke) is too weak for value->entity recall (smoke validates CONSTRUCTION: separable keys + aligned
queries + can-fail; the recall NUMBER is the full Pythia-2.8B run's verdict). import torch first. checkpoint per (M,seed). ASCII.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, itertools
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "pythia_kv_recall_reality_v3_1_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
ENCODER = "EleutherAI/pythia-160m" if SMOKE else "EleutherAI/pythia-2.8b"
M_SWEEP = [200, 500] if SMOKE else [2000, 10000]
SEEDS = [0, 1] if SMOKE else [0, 1, 2, 3, 4]
NOISE_FRAC = 0.5

_ADJ = "red blue swift quiet ancient modern silver golden hidden northern rapid silent hollow bright frozen molten crimson azure verdant amber".split()
_NOUN = "falcon river engine archive bridge reactor delta harbor summit forge canyon beacon orchard meadow glacier tower lagoon prairie quarry vault".split()
_VALW = "helium cobalt basalt cedar quartz copper marble willow granite saffron indigo cypress bronze jasper walnut".split()
_PROPS = ["founded in", "powered by", "located near", "awarded for", "merged with"]


def make_facts(M, g):
    """DIVERSE real-token facts; UNIQUE value (valword + unique year) per fact -> distinct keys + unique value-cue target."""
    keys, val_cue, para_cue, rel_cue = [], [], [], []
    order = g.permutation(M)
    for j in range(M):
        i = int(order[j])
        ent = "the %s %s" % (_ADJ[i % len(_ADJ)], _NOUN[(i // len(_ADJ)) % len(_NOUN)])
        prop = _PROPS[i % len(_PROPS)]; value = "%s %d" % (_VALW[i % len(_VALW)], 1000 + i)   # unique year 1000+i
        keys.append("%s was %s %s." % (ent, prop, value))
        val_cue.append("Which one was %s %s?" % (prop, value))      # OMITS entity; unique value target
        para_cue.append("%s has a recorded %s detail." % (ent, prop))
        rel_cue.append("Tell me about %s." % ent)
    return keys, val_cue, para_cue, rel_cue


def center_fit(K):
    """anisotropy fix: subtract the key-mean (removes the dominant common direction), unit-normalize. NOT ZCA whitening."""
    K = K.astype(np.float32); mu = K.mean(0)
    Kc = K - mu; Kc = (Kc / (np.linalg.norm(Kc, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
    return mu, Kc


def project(Q, mu):
    Qc = Q.astype(np.float32) - mu
    return (Qc / (np.linalg.norm(Qc, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def recall_at(Qc, Kc, chunk=256):
    cor = 0
    for i in range(0, len(Qc), chunk):
        pred = np.argmax(Qc[i:i + chunk] @ Kc.T, axis=1)
        cor += int((pred == np.arange(i, min(i + chunk, len(Qc)))).sum())
    return cor / len(Qc)


def max_cos_other(Kc, sample=512, g=None):
    n = len(Kc); idx = (g.permutation(n)[:min(sample, n)] if g is not None else np.arange(min(sample, n)))
    S = Kc[idx]; G = S @ Kc.T
    for r, j in enumerate(idx): G[r, j] = -2.0
    return float(np.median(G.max(1)))


def median_nn_dist(Kc, sample=512, g=None):
    n = len(Kc); idx = (g.permutation(n)[:min(sample, n)] if g is not None else np.arange(min(sample, n)))
    S = Kc[idx]; D = 1.0 - (S @ Kc.T)
    for r, j in enumerate(idx): D[r, j] = 2.0
    return float(np.median(D.min(axis=1)))


def cos_own(Qc, Kc):
    return float(np.median((Qc * Kc).sum(1)))


def _selftest():
    g = np.random.default_rng(0)
    keys, vc, pc, rc = make_facts(30, g)
    assert "Which one was" in vc[0] and "the " not in vc[0].replace("Which", "X"), "value-cue omits entity: %s" % vc[0]
    K = g.standard_normal((60, 24)).astype(np.float32); mu, Kc = center_fit(K)
    assert recall_at(project(K, mu), Kc) > 0.95, "clean self-recall ~1"
    Rq = project(g.standard_normal((60, 24)).astype(np.float32), mu)
    assert recall_at(Rq, Kc) < 0.5, "CAN-FAIL: decoupled random query -> recall<0.5"
    print("[selftest] PASS: value-cue-omits-entity + mean-center recall + CAN-FAIL(decoupled<0.5)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)

try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if torch.cuda.is_available():
    DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
elif SMOKE:
    DEV = torch.device("cpu"); print("[smoke] CPU (pythia-160m; CONSTRUCTION test only -- recall needs 2.8b)", flush=True)
else:
    print("[FATAL] CUDA required for full run (Pythia-2.8B).", flush=True); sys.exit(1)


def encode(texts):
    tok = AutoTokenizer.from_pretrained(ENCODER)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    mdl = AutoModel.from_pretrained(ENCODER, torch_dtype=(torch.float16 if DEV.type == "cuda" else torch.float32)).to(DEV).eval()
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=48).to(DEV)
        with torch.no_grad():
            h = mdl(**t).last_hidden_state
        mask = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).float().cpu().numpy())
    del mdl
    if DEV.type == "cuda": torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def run_unit(M, seed):
    g = np.random.default_rng(seed); keys, vc, pc, rc = make_facts(M, g)
    mu, Kc = center_fit(encode(keys))
    Qv = project(encode(vc), mu); Qp = project(encode(pc), mu); Qr = project(encode(rc), mu)
    r_val = recall_at(Qv, Kc); r_para = recall_at(Qp, Kc); r_rel = recall_at(Qr, Kc)
    cv = cos_own(Qv, Kc); ksep = max_cos_other(Kc, g=g)
    nn = median_nn_dist(Kc, g=g); Qvn = Qv + (NOISE_FRAC * nn) * g.standard_normal(Qv.shape).astype(np.float32)
    Qvn = (Qvn / (np.linalg.norm(Qvn, axis=1, keepdims=True) + 1e-8)).astype(np.float32)
    r_val_noise = recall_at(Qvn, Kc)
    print("  [M=%d seed=%d] value=%.4f (cos_own=%.3f) noise=%.4f | key_sep(max-cos-other)=%.3f | paraphrase=%.4f diffrel=%.4f" %
          (M, seed, r_val, cv, r_val_noise, ksep, r_para, r_rel), flush=True)
    return {"M": M, "seed": seed, "recall_value": round(r_val, 4), "recall_value_noise": round(r_val_noise, 4),
            "cos_value_own_key": round(cv, 4), "key_max_cos_other": round(ksep, 4),
            "recall_paraphrase": round(r_para, 4), "recall_diffrel": round(r_rel, 4), "nn_dist": round(nn, 4)}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    by_M = {}
    for M in M_SWEEP:
        us = [u for u in units if u["M"] == M]
        if not us: continue
        vv = [u["recall_value"] for u in us]
        by_M[M] = {"value_mean": float(np.mean(vv)), "value_std": float(np.std(vv)),
                   "value_noise_mean": float(np.mean([u["recall_value_noise"] for u in us])),
                   "cos_value_own_key": float(np.mean([u["cos_value_own_key"] for u in us])),
                   "key_max_cos_other": float(np.mean([u["key_max_cos_other"] for u in us])),
                   "paraphrase_mean": float(np.mean([u["recall_paraphrase"] for u in us])),
                   "diffrel_mean": float(np.mean([u["recall_diffrel"] for u in us]))}
    Ms = sorted(by_M)
    if not Ms: return ("UNKNOWN", "no M points", {})
    worst_val = min(by_M[M]["value_mean"] for M in Ms); worst_noise = min(by_M[M]["value_noise_mean"] for M in Ms)
    max_std = max(by_M[M]["value_std"] for M in Ms); min_std = min(by_M[M]["value_std"] for M in Ms)
    max_cos = max(by_M[M]["cos_value_own_key"] for M in Ms); worst_ksep = max(by_M[M]["key_max_cos_other"] for M in Ms)
    cliff = next((M for M in Ms if by_M[M]["value_mean"] < 0.80), None)
    detail = {"by_M": by_M, "worst_value_recall": round(worst_val, 4), "worst_noise_recall": round(worst_noise, 4),
              "max_seed_std": round(max_std, 4), "min_seed_std": round(min_std, 4), "max_cos_value_own_key": round(max_cos, 4),
              "worst_key_separability_max_cos_other": round(worst_ksep, 4), "value_recall_cliff_M": cliff,
              "honest_scope": "RECALL-REALITY: value-cue (omits entity) retrieves the right fact via MEAN-CENTERED cosine "
                              "over Pythia-2.8B keys at recall>=0.80 up to M in {2k,10k}; NOT a capacity cliff (cosine has no "
                              "crosstalk). Mean-centering required (LM anisotropy). paraphrase/diffrel REPORTED."}
    summary = ("value_recall worst=%.3f | noise worst=%.3f | seed-std [%.4f,%.4f] | cos(value,own)=%.3f | "
               "key_sep(max-cos-other)=%.3f | paraphrase=%.3f diffrel=%.3f (REPORTED) | cliff_M=%s" % (
               worst_val, worst_noise, min_std, max_std, max_cos, worst_ksep, by_M[Ms[0]]["paraphrase_mean"], by_M[Ms[0]]["diffrel_mean"], cliff))
    if worst_ksep >= 0.95:
        return ("HARD_FAIL", "HARD_FAIL[pre-flight B]: keys NON-SEPARABLE (max-cos-other=%.3f>=0.95) -> construction broken "
                "(anisotropy/template-collapse). " % worst_ksep + summary, detail)
    if max_cos > 0.98:
        return ("HARD_FAIL", "HARD_FAIL[pre-flight A]: value-cue cos(query,own)=%.3f>0.98 -> surface-dominated. " % max_cos + summary, detail)
    if worst_val < 0.50 or max_std == 0.0:
        return ("HARD_FAIL", "HARD_FAIL: value-cue does NOT retrieve (recall<0.5) OR zero-variance (re-saturated). " + summary, detail)
    if worst_val >= 0.80 and worst_noise >= 0.80 and 0.0 < max_std < 0.05:
        return ("HARD_PASS", "HARD_PASS: substrate-KV value-cue (semantic, no entity shortcut) retrieves the right fact at "
                "recall>=0.80 through M={2k,10k} + noise-robust + seed-reproducible. RECALL-REALITY (not capacity). " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: value-cue retrieves in [0.5,0.8) or noise/repro marginal. " + summary, detail)


print("[config] %s mode=%s encoder=%s M=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, ENCODER, M_SWEEP, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for M in M_SWEEP:
    for seed in SEEDS:
        key = "M%d_s%d" % (M, seed)
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        res = run_unit(M, seed); res["run_mode"] = RUN_MODE
        write_partial_key(out_dir, key, res)
units = list(aggregate_partials(out_dir, ["M%d_s%d" % (M, sd) for M in M_SWEEP for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
           "encoder": ENCODER, "M_sweep": M_SWEEP, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_gpu_pythia2p8b_kv_recall_reality_value_cue_centered", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
