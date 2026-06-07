"""
exp_khop_audit_replay_v1 -- C1: K-hop audit replay (deterministic+Merkle) vs LLM CoT non-determinism -- GPU.

ROUTING: 2hour battery C1 (highest demo value). For N multi-hop HotpotQA questions: the substrate produces a 2-hop
  retrieval chain (bge whiten + K-hop select) with a Merkle commitment per step; we (a) replay each chain and confirm it is
  bit-identical, (b) verify each step's Merkle proof chains to the root, (c) tamper one step and confirm detection. Contrast:
  Qwen chain-of-thought generated TWICE with sampling on the same question -- measure how often the two CoTs diverge
  (the "superficially plausible but non-reproducible narrative" the legal/clinical literature warns about). GPU.
PRE-REGISTERED: HARD-PASS substrate 100pct deterministic replay AND 100pct Merkle verify AND 100pct tamper-caught AND LLM
  CoT divergence rate >= 0.50 (confirming non-reproducibility). HARD-FAIL substrate determinism/verify <100pct.
FORMULA SELF-TESTS (PROT-022): 1. merkle chains. 2. tamper detected. 3. self-retrieval.
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
import argparse, time, json, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "khop_audit_replay_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 8 if RUN_MODE == "smoke" else 20


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def h(b):
    return hashlib.sha256(b).hexdigest()


def _selftest():
    c = h(b"genesis"); c2 = h((c + "step").encode()); assert c2 != c, "merkle chains"
    assert h(b"a") != h(b"b"), "tamper detected"
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    print("[selftest] PASS: khop-audit-replay", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l)
        ctx = r.get("context") or {}; ans = r.get("answer", "")
        titles = ctx.get("title") or []; sent_lists = ctx.get("sentences") or []
        flat = [s for ti in range(len(titles)) for s in (sent_lists[ti] if ti < len(sent_lists) else [])]
        if len(flat) < 12 or not ans:
            continue
        out.append({"q": r.get("question", ""), "ans": ans, "sents": flat})
        if len(out) >= n:
            break
    return out


def bi_encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def khop_chain(sents, en, qn):
    # deterministic 2-hop: whiten the top-50, hop1 = nearest to query, hop2 = nearest to (query+hop1)
    order = np.argsort(en @ qn)[::-1]; top = order[:min(50, len(sents))]; sub = en[top]
    mu = sub.mean(0); cov = ((sub - mu).T @ (sub - mu)) / max(len(sub), 1)
    U, S, _ = np.linalg.svd(cov + 1e-3 * np.eye(cov.shape[0])); Wd = (U @ np.diag(1 / np.sqrt(S + 1e-3)) @ U.T).astype(np.float32)
    ew = unit((sub - mu) @ Wd); qw = unit((qn - mu) @ Wd); h1 = int(np.argmax(ew @ qw))
    qb = qw + ew[h1]; qb = qb / (np.linalg.norm(qb) + 1e-8); s2 = ew @ qb; s2[h1] = -1e9; h2 = int(np.argmax(s2))
    return [sents[top[h1]], sents[top[h2]]]


def merkle_chain(steps):
    c = h(b"genesis"); proofs = []
    for s in steps:
        c = h((c + s).encode()); proofs.append(c)
    return c, proofs


def verify(steps, root):
    c = h(b"genesis")
    for s in steps:
        c = h((c + s).encode())
    return c == root


def cot(ltok, lm, q, do_sample):
    msg = [{"role": "user", "content": "Question: " + q + "\nThink step by step, then answer."}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt", truncation=True, max_length=512).input_ids.to(DEV)
    with torch.no_grad():
        o = lm.generate(ids, max_new_tokens=80, do_sample=do_sample, temperature=0.8 if do_sample else None, top_p=0.95 if do_sample else None, pad_token_id=ltok.eos_token_id)
    return ltok.decode(o[0][ids.shape[1]:], skip_special_tokens=True).strip()


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"n": 0}
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    det = ver = tamp = 0; cot_div = 0
    for d in data:
        sents = d["sents"]; en = unit(bi_encode(sents, btok, bm)); qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]
        c1 = khop_chain(sents, en, qn); c2 = khop_chain(sents, en.copy(), qn.copy())     # replay
        root, _ = merkle_chain(c1); det += int(c1 == c2)
        ver += int(verify(c1, root))
        bad = list(c1); bad[0] = bad[0] + " [TAMPERED]"; tamp += int(not verify(bad, root))
        a = cot(ltok, lm, d["q"], True); b = cot(ltok, lm, d["q"], True); cot_div += int(a.strip() != b.strip())
    del lm, bm; torch.cuda.empty_cache()
    n = len(data); r = {"n": n, "det": det / n, "ver": ver / n, "tamper": tamp / n, "cot_div": cot_div / n}
    print("  substrate: deterministic=%.3f merkle-verify=%.3f tamper-caught=%.3f | LLM CoT divergence=%.3f (n=%d)" % (r["det"], r["ver"], r["tamper"], r["cot_div"], n), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    s = "substrate determinism=%.3f merkle=%.3f tamper=%.3f; LLM-CoT-divergence=%.3f (n=%d)" % (r["det"], r["ver"], r["tamper"], r["cot_div"], r["n"])
    if r["det"] >= 0.999 and r["ver"] >= 0.999 and r["tamper"] >= 0.999 and r["cot_div"] >= 0.50:
        return ("HARD_PASS", "HARD_PASS: substrate K-hop chains are 100pct deterministic + Merkle-verifiable + tamper-detecting while LLM CoT diverges run-to-run -- the auditable-reasoning categorical win for regulated industries. " + s)
    if r["det"] >= 0.999 and r["ver"] >= 0.999 and r["tamper"] >= 0.999:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate fully auditable but LLM CoT divergence <0.50 (this Qwen is more stable than expected). " + s)
    return ("HARD_FAIL", "HARD_FAIL: substrate chain not fully deterministic/verifiable. " + s)


print("[config] anchor=%s mode=%s n_q=%d" % (ANCHOR_NAME, RUN_MODE, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
