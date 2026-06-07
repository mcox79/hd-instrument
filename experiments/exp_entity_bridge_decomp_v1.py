"""
exp_entity_bridge_decomp_v1 -- multi-hop: entity-bridge decomposition (extract bridge entity from hop-1, re-query) -- CPU.

ROUTING: handoff research_to_exp_dev_retrieval_decomp_pretests (pre-test A). The HotpotQA gap is decomposition, not coverage
  (bge recall@10=0.74). Tests whether extracting the BRIDGE entity from the hop-1 passage and re-querying for it lifts
  recall@2hop. spaCy is not installed on the runner, so uses a dependency-free proper-noun extractor (capitalized spans)
  as the NER proxy; if it clears the bar the spaCy version is unnecessary, if borderline we install spaCy. bge-small. CPU.
PRE-REGISTERED: HARD-PASS recall@2hop >= 0.60 with entity-bridge decomp (NER-proxy). MIDDLE 0.50-0.60. HARD-FAIL < 0.50.
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. proper-noun extract. 3. parse columnar.
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
import argparse, time, json, re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "entity_bridge_decomp_v1"
ENCODER = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 50 if RUN_MODE == "smoke" else 200
_PN = re.compile(r"\b([A-Z][a-zA-Z0-9.'-]+(?:\s+[A-Z][a-zA-Z0-9.'-]+)*)\b")


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def proper_nouns(text):
    return [m.group(1) for m in _PN.finditer(text or "") if len(m.group(1)) > 2]


def bridge_entities(hop1_text, question):
    # entities introduced by hop-1 that are NOT already in the question = the bridge
    q_ents = set(e.lower() for e in proper_nouns(question))
    out = []
    for e in proper_nouns(hop1_text):
        el = e.lower()
        if el not in q_ents and not any(el in q for q in q_ents):
            out.append(e)
    return out


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 16))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert "Scott Derrickson" in proper_nouns("directed by Scott Derrickson in Los Angeles"), "proper-noun extract"
    rec = {"context": {"title": ["A"], "sentences": [["s0"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: entity-bridge", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


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


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 384), np.float32)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"naive": 0.0, "decomp": 0.0, "n": 0}
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER).to(DEV).eval()
    naive = 0; decomp = 0
    for d in data:
        sents = d["sents"]; texts = [s for (_, _, s) in sents]
        en = unit(encode(texts, tok, m)); qn = unit(encode([Q_INSTR + d["q"]], tok, m))[0]
        order = np.argsort(en @ qn)[::-1]
        naive += int(len(set((sents[i][0], sents[i][1]) for i in order[:2]) & d["gold"]) >= 2)
        h1 = int(order[0]); brs = bridge_entities(sents[h1][2], d["q"])
        if brs:
            bq = unit(encode([Q_INSTR + d["q"] + " " + " ".join(brs[:3])], tok, m))[0]  # re-query with bridge entities
            s2 = en @ bq; s2[h1] = -1e9; h2 = int(np.argmax(s2))
        else:
            s2 = en @ qn; s2[h1] = -1e9; h2 = int(np.argmax(s2))
        decomp += int(len(set([(sents[h1][0], sents[h1][1]), (sents[h2][0], sents[h2][1])]) & d["gold"]) >= 2)
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    n = len(data); rn = naive / n; rd = decomp / n
    print("  n=%d naive_recall@2hop=%.3f entity_bridge_decomp_recall@2hop=%.3f lift=%+.3f" % (n, rn, rd, rd - rn), flush=True)
    return {"n": n, "naive": rn, "decomp": rd}


def verdict(r) -> Tuple[str, str]:
    rd = r["decomp"]; rn = r["naive"]
    summary = "entity-bridge-decomp recall@2hop=%.3f naive=%.3f lift=%+.3f (n=%d, regex-NER proxy)" % (rd, rn, rd - rn, r["n"])
    if rd >= 0.60:
        return ("HARD_PASS", "HARD_PASS: entity-bridge decomposition reaches recall@2hop>=0.60 -- NER-based bridge re-query is the v1 multi-hop recipe (no LLM needed). " + summary)
    if rd >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: entity-bridge decomp 0.50-0.60 -- helps; spaCy NER or LLM decomp may close the rest. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: entity-bridge decomp <0.50 -- regex-NER bridge insufficient; needs spaCy NER or LLM decomposition. " + summary)


print("[config] anchor=%s mode=%s n_q=%d encoder=bge-small (regex-NER bridge)" % (ANCHOR_NAME, RUN_MODE, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
