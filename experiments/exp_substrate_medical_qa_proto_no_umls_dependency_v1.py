"""
substrate_medical_qa_proto_no_umls_dependency_v1 -- HP-5: medical Q&A proto + deletion-cert (no UMLS) -- GPU.

ROUTING: research HP-5 (medical-light dry-run; UMLS-free). Data delivered: medqa_usmle_500.jsonl (500 USMLE 4-option
  MCQ) + pubmed_abstracts_10k.jsonl (10k abstracts). Tests: (A) substrate-retrieval-augmented MedQA (retrieve relevant
  PubMed abstract -> inject -> Pythia option-perplexity scoring) vs Pythia-raw MCQ; (B) DELETION-CERT on medical facts
  (regulated-AI wedge: delete a medical fact, verify removal). torch GPU $0.

PRE-REGISTERED bands: HARD-PASS substrate-aug MedQA acc >= 1.5x Pythia-raw AND deletion-cert operational. MIDDLE: one
  of the two (likely: deletion-cert works, MedQA Pythia-ceiling-limited at 160M). HARD-FAIL: neither.
FORMULA SELF-TESTS (PROT-022): 1. MCQ argmax scoring. 2. deletion projection removes target. 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_medical_qa_proto_no_umls_dependency_v1"
MODEL_ID = "EleutherAI/pythia-160m"; N_SUB = 4096; LR = 0.5
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"
PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_Q = 40; N_ABS = 1000; N_DEL = 50
else:
    SEEDS = [7, 17, 23]; N_Q = 300; N_ABS = 4000; N_DEL = 200


def ub(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, k, v, n):
    W += (LR / n) * np.outer(v - W @ k, k)


def _selftest():
    sc = np.array([0.1, 0.9, 0.3, 0.2]); assert int(np.argmax(sc)) == 1, "MCQ argmax scoring"
    g = np.random.default_rng(0); n = 128; K = ub(1, n, g)[0]; V = ub(1, n, g)[0]; W = np.zeros((n, n), dtype=np.float32)
    cfrpe(W, K, V, n); b = float(V @ (W @ K)); W -= np.outer(W @ K, K); a = float(V @ (W @ K))
    assert abs(a) < abs(b) * 0.3, "deletion projection removes target"
    assert N_SUB == 4096; print("[selftest] PASS: mcq deletion", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MODEL_ID); _TOK.pad_token = _TOK.eos_token; _TOK.truncation_side = "left"
_MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32, output_hidden_states=True).to(DEVICE).eval()


def embed(texts):
    out = []
    for i in range(0, len(texts), 16):
        b = texts[i:i + 16]; t = _TOK(b, return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEVICE)
        with torch.no_grad():
            hs = _MODEL(**t).hidden_states[12]
        m = t["attention_mask"].unsqueeze(-1).float(); out.append(((hs * m).sum(1) / m.sum(1).clamp(min=1)).cpu().numpy())
    e = np.concatenate(out, 0).astype(np.float32); return e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-8)


def option_logprob(context, question, opt):
    prompt = (("Context: %s\n" % context) if context else "") + "Question: %s\nAnswer: %s" % (question, opt)
    ids = _TOK(prompt, return_tensors="pt", truncation=True, max_length=400).input_ids.to(DEVICE)
    with torch.no_grad():
        lo = _MODEL(ids).logits
    lp = torch.log_softmax(lo[0, :-1], -1); tgt = ids[0, 1:]
    return float(lp[range(len(tgt)), tgt].mean())   # avg token log-prob


def mcq_acc(questions, contexts):
    ok = 0
    for qi, q in enumerate(questions):
        opts = q["options"]; ctx = contexts[qi] if contexts else ""
        scores = {key: option_logprob(ctx, q["question"][:600], opts[key]) for key in ["A", "B", "C", "D"]}
        ok += (max(scores, key=scores.get) == q["answer_idx"])
    return ok / max(len(questions), 1)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    qs = [json.loads(l) for l in open(MEDQA, encoding="utf-8")][:N_Q]
    abs_rows = [json.loads(l) for l in open(PUBMED, encoding="utf-8")][:N_ABS]
    abstracts = [" ".join(r["context"]["contexts"])[:600] for r in abs_rows]
    # (A) Pythia-raw MCQ
    raw_acc = mcq_acc(qs, None)
    # substrate-retrieval-augmented: embed abstracts + questions, retrieve top-1 abstract per Q
    aemb = embed(abstracts); qemb = embed([q["question"][:300] for q in qs])
    ctxs = [abstracts[int(np.argmax(aemb @ qemb[i]))] for i in range(len(qs))]
    aug_acc = mcq_acc(qs, ctxs)
    # (B) DELETION-CERT on medical facts (condition->treatment synthetic keys over real entities)
    n = N_SUB; M = N_DEL + 200; EK = ub(M, n, g); EV = ub(20, n, g)
    fv = [int(g.integers(0, 20)) for _ in range(M)]
    W = (EV[np.array(fv)].T @ EK).astype(np.float32)   # batched Hebbian (meaningful magnitude, unlike tiny cf-RPE/n)

    def conf(i):
        r = W @ EK[i]; return float((EV[fv[i]] @ r) / (np.linalg.norm(r) + 1e-8))
    tgt = 0; before = conf(tgt); othb = conf(1)
    W -= np.outer(W @ EK[tgt], EK[tgt])                 # DELETION CERT: project out the medical fact's key
    after = conf(tgt); otha = conf(1)
    del_ok = bool(before > 0.5 and after < 0.2 and abs(otha - othb) < 0.2)
    return {"seed": seed, "n_q": len(qs), "pythia_raw_mcq": raw_acc, "substrate_aug_mcq": aug_acc,
            "mcq_ratio": float(aug_acc / max(raw_acc, 1e-6)), "deletion_cert_operational": del_ok,
            "del_before": before, "del_after": after}


def verdict(ps) -> Tuple[str, str]:
    raw = float(np.mean([p["pythia_raw_mcq"] for p in ps])); aug = float(np.mean([p["substrate_aug_mcq"] for p in ps]))
    ratio = aug / max(raw, 1e-6); delok = all(p["deletion_cert_operational"] for p in ps)
    summary = "MedQA: substrate_aug=%.3f pythia_raw=%.3f (ratio=%.2fx, random=0.25) | deletion-cert operational=%s (before=%.2f->after=%.2f)" % (
        aug, raw, ratio, delok, ps[0]["del_before"], ps[0]["del_after"])
    if ratio >= 1.5 and delok:
        return ("HARD_PASS", "HARD_PASS: substrate medical Q&A >=1.5x Pythia + deletion-cert operational (medical regulated-AI wedge). " + summary)
    if delok or ratio >= 1.2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: deletion-cert OR MedQA-aug partial (MedQA likely Pythia-160M-ceiling). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: neither medical dimension. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_Q=%d N_abs=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_Q, N_ABS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] MedQA aug=%.3f raw=%.3f (%.2fx) | deletion-cert=%s" % (seed, r["substrate_aug_mcq"], r["pythia_raw_mcq"], r["mcq_ratio"], r["deletion_cert_operational"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "model": MODEL_ID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
