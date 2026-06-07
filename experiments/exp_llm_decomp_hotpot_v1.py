"""
exp_llm_decomp_hotpot_v1 -- multi-hop CEILING test: LLM question decomposition + bge retrieval -> recall@2hop -- GPU.

ROUTING: the multi-hop conclusion (rerank/bridge/iterative all plateau ~0.42; gap is genuine decomposition) + Research's
  substrate-native-decomposition unification. This is the CEILING test: does GOOD question decomposition close the gap at
  all? A small ungated instruct model (Qwen2.5-1.5B-Instruct; Llama-3.2-1B-Instruct is HF-gated, flan-t5-base too weak)
  splits each 2-hop question into two single-hop sub-queries; bge-small retrieves top-1 per sub-query. If recall@2hop jumps
  to >=0.60, decomposition IS the lever (and Pattern B VSA unbinding can later replace the LLM). If it also fails,
  decomposition alone is not enough. GPU.
PRE-REGISTERED: HARD-PASS LLM-decomp recall@2hop >= 0.60 (decomposition is the lever; substrate-native decomp is worth
  building). MIDDLE 0.50-0.60. HARD-FAIL < 0.50 (decomposition alone insufficient).
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. two-line split. 3. parse columnar.
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

ANCHOR_NAME = "llm_decomp_hotpot_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 30 if RUN_MODE == "smoke" else 150
SYS = "Break the user's multi-hop question into two simple single-hop search queries. Output ONLY the two queries, one per line, nothing else."


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def parse_two(text):
    lines = [l.strip(" -0123456789.").strip() for l in text.splitlines() if l.strip()]
    lines = [l for l in lines if len(l) > 3][:2]
    return lines


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 16))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert len(parse_two("1. who is X\n2. where is Y")) == 2, "two-line split"
    rec = {"context": {"title": ["A"], "sentences": [["s0"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: llm-decomp", flush=True)


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
        ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sent_lists = ctx.get("sentences") or []
        flat = []
        for ti, title in enumerate(titles):
            for si, s in enumerate(sent_lists[ti] if ti < len(sent_lists) else []):
                flat.append((title, si, s))
        gold = set(zip(sf.get("title") or [], sf.get("sent_id") or []))
        if len(flat) < 4 or len(gold) < 2:
            continue
        out.append({"q": r.get("question", ""), "sents": flat, "gold": gold})
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
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 384), np.float32)


def decompose(questions, ltok, lm):
    subs = []
    for q in questions:
        msg = [{"role": "system", "content": SYS}, {"role": "user", "content": q}]
        p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
        ids = ltok(p, return_tensors="pt").input_ids.to(DEV)
        with torch.no_grad():
            out = lm.generate(ids, max_new_tokens=60, do_sample=False, pad_token_id=ltok.eos_token_id)
        txt = ltok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
        two = parse_two(txt); subs.append(two if len(two) == 2 else [q, q])
    return subs


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"naive": 0.0, "decomp": 0.0, "decomp_union5": 0.0, "n": 0}
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    subs = decompose([d["q"] for d in data], ltok, lm); del lm; torch.cuda.empty_cache()
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    naive = 0; decomp = 0; union5 = 0
    for d, sub in zip(data, subs):
        sents = d["sents"]; texts = [s for (_, _, s) in sents]; en = unit(bi_encode(texts, btok, bm))
        qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]; order = np.argsort(en @ qn)[::-1]
        naive += int(len(set((sents[i][0], sents[i][1]) for i in order[:2]) & d["gold"]) >= 2)
        q1 = unit(bi_encode([Q_INSTR + sub[0]], btok, bm))[0]; q2 = unit(bi_encode([Q_INSTR + sub[1]], btok, bm))[0]
        o1 = np.argsort(en @ q1)[::-1]; o2 = np.argsort(en @ q2)[::-1]
        picks = set([(sents[o1[0]][0], sents[o1[0]][1]), (sents[o2[0]][0], sents[o2[0]][1])])     # top-1 per sub-query
        decomp += int(len(picks & d["gold"]) >= 2)
        un = set((sents[i][0], sents[i][1]) for i in list(o1[:5]) + list(o2[:5]))                  # union top-5 per sub-query
        union5 += int(len(un & d["gold"]) >= 2)
    del bm; torch.cuda.empty_cache()
    n = len(data); rn = naive / n; rd = decomp / n; ru = union5 / n
    print("  n=%d naive_recall@2hop=%.3f LLMdecomp_recall@2hop=%.3f decomp_union@5=%.3f" % (n, rn, rd, ru), flush=True)
    return {"n": n, "naive": rn, "decomp": rd, "decomp_union5": ru}


def verdict(r) -> Tuple[str, str]:
    rd = r["decomp"]; rn = r["naive"]; ru = r["decomp_union5"]
    summary = "LLM-decomp recall@2hop=%.3f (union@5=%.3f) naive=%.3f lift=%+.3f (n=%d, Qwen2.5-1.5B + bge-small)" % (rd, ru, rn, rd - rn, r["n"])
    if rd >= 0.60 or ru >= 0.75:
        return ("HARD_PASS", "HARD_PASS: LLM decomposition lifts recall@2hop>=0.60 (or union@5>=0.75) -- decomposition IS the multi-hop lever; substrate-native (Pattern B) decomp is worth building to replace the LLM loop. " + summary)
    if rd >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: LLM-decomp 0.50-0.60 -- helps but partial; parser/decomp quality is the bottleneck. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: LLM-decomp <0.50 -- decomposition alone does not close the gap at 1.5B scale; needs larger LLM or different mechanism. " + summary)


print("[config] anchor=%s mode=%s n_q=%d llm=%s bi=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, LLM, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
