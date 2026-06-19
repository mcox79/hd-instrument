"""
exp_substrate_llm_triples_khop_gpu_v1 -- N2 (HIGHEST): LLM-extracted triples -> discrete substrate KG -> K-hop -- GPU.

ROUTING: iterative_drill / N2 (BridgeRAG-equivalent). R1 proved that GIVEN oracle discrete structure the substrate solves real
  HotpotQA multi-hop (recall@1=1.0). N2 tests the realistic pipeline: Qwen-2.5-1.5B-Instruct extracts (subject|relation|object)
  triples from the question's gold passages; entities are deduped into DISCRETE FHRR symbols; substrate K-hop (<=3 hops,
  enumerate relations per node) traverses from the question entity to recover the answer. Measures (a) extraction coverage
  (answer present as an extracted entity) and (b) K-hop answer recall. The gap below R1's 1.0 quantifies the LLM-extraction
  cost -- the training-free SOTA mechanism (HippoRAG/BridgeRAG). Qwen on GPU. 8GB-safe (1.5B fp16 ~3GB).
PRE-REGISTERED: HARD-PASS K-hop answer recall >= 0.55 (LLM-triples + substrate K-hop clears the fuzzy 0.37 ceiling). MIDDLE
  0.45-0.55. HARD-FAIL < 0.45.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cleanup self. 3. triple parse.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"; os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math, json, re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "n2_pathA_betterprompt_gpu_v1"; N = 8192; MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_Q = 8 if SMOKE else 60


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def norm_ent(s):
    return re.sub(r"\s+", " ", s.strip().lower()).strip(".,;:'\"()")


def parse_triples(text):
    out = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3 and all(parts):
            s, r, o = norm_ent(parts[0]), norm_ent(parts[1]), norm_ent(parts[2])
            if s and r and o and len(s) < 60 and len(o) < 60:
                out.append((s, r, o))
    return out


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind/unbind"
    bk = cphasor(4, 32, g); assert cidx(bk[3], bk) == 3, "cleanup self"
    assert parse_triples("Paris | capital of | France") == [("paris", "capital of", "france")], "triple parse"
    print("[selftest] PASS: n2-pathA-betterprompt", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sents = ctx.get("sentences") or []; sf_titles = set(sf.get("title") or [])
        ans = (r.get("answer") or "").strip()
        if not ans or ans.lower() in ("yes", "no") or len(sf_titles) < 2:
            continue
        passages = []
        for ti, t in enumerate(titles):
            if t in sf_titles:
                passages.append(t + ": " + " ".join(sents[ti] if ti < len(sents) else []))
        if len(passages) < 2:
            continue
        out.append({"q": r.get("question", ""), "passages": passages, "answer": ans})
        if len(out) >= n:
            break
    return out


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def extract_triples(tok, model, passages):
    ctx = "\n".join(passages)[:2400]
    msg = [{"role": "user", "content": "Extract factual relationships from the text as triples, one per line, strictly in the format: subject | relation | object\nUse short entity names. Only use information in the text.\n\nText:\n" + ctx + "\n\nTriples:"}]
    enc = tok.apply_chat_template(msg, add_generation_prompt=True, return_tensors="pt", return_dict=True).to(DEV)
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=320, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot", flush=True); return {"n": 0, "recall": 0.0, "coverage": 0.0}
    tok = AutoTokenizer.from_pretrained(MODEL); model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16).to(DEV).eval()
    g = np.random.default_rng(7); hit = 0; cover = 0; n = 0
    STOP = {"the", "a", "an", "of", "in", "and", "to", "for", "is", "was", "by", "on", "at"}
    def canon_map(raw_ents):
        # merge entities that share a significant content token (>3 chars) so the bridge connects across passages
        toks = {e: set(w for w in re.findall(r"[a-z0-9]+", e) if len(w) > 3 and w not in STOP) for e in raw_ents}
        order = sorted(raw_ents, key=lambda e: -len(e)); cmap = {}
        for e in order:
            best = None
            for c in dict.fromkeys(cmap.values()):
                if toks[e] and toks.get(c) and (toks[e] & toks[c]) and (toks[e] <= toks[c] or toks[c] <= toks[e]):
                    best = c; break
            cmap[e] = best if best else e
        return cmap
    for d in data:
        triples = parse_triples(extract_triples(tok, model, d["passages"]))
        if not triples:
            n += 1; continue
        raw = list(dict.fromkeys([t[0] for t in triples] + [t[2] for t in triples]))
        cm = canon_map(raw); triples = [(cm[s], r, cm[o]) for s, r, o in triples]
        ents = list(dict.fromkeys([t[0] for t in triples] + [t[2] for t in triples]))
        rels = list(dict.fromkeys([t[1] for t in triples]))
        ei = {e: i for i, e in enumerate(ents)}; ri = {r: i for i, r in enumerate(rels)}
        esym = cphasor(len(ents), N, g); rsym = cphasor(max(1, len(rels)), N, g)
        M = np.zeros(N, dtype=np.complex64)
        for s, r, o in triples:
            M = M + esym[ei[s]] * rsym[ri[r]] * esym[ei[o]]
        ans = norm_ent(d["answer"]); ql = d["q"].lower()
        ans_match = next((e for e in ents if e == ans or (len(ans) > 3 and ans in e) or (len(e) > 3 and e in ans)), None)
        cover += int(ans_match is not None)
        qtoks = set(w for w in re.findall(r"[a-z0-9]+", ql) if len(w) > 3 and w not in STOP)
        starts = [e for e in ents if e in ql] or [e for e in ents if set(re.findall(r"[a-z0-9]+", e)) & qtoks]  # exact, else token-overlap
        reached = set()
        frontier = set(starts)
        for _hop in range(3):                                                # substrate K-hop spreading (<=3 hops)
            newf = set()
            for node in frontier:
                nv = esym[ei[node]]
                for r in rels:
                    nb = cidx(M * np.conj(nv * rsym[ri[r]]), esym)
                    if (esym[nb] @ np.conj(nv * rsym[ri[r]])).real / N > 0.30:
                        ne = ents[nb]
                        if ne not in reached:
                            newf.add(ne)
                reached.add(node)
            reached |= newf; frontier = newf
            if not frontier:
                break
        got = ans_match is not None and ans_match in reached
        hit += int(got); n += 1
    rec = hit / max(1, n); cov = cover / max(1, n)
    print("  LLM-triples K-hop: answer-recall=%.3f extraction-coverage=%.3f (n=%d)" % (rec, cov, n), flush=True)
    return {"n": n, "recall": rec, "coverage": cov}


def verdict(r) -> Tuple[str, str]:
    s = "K-hop answer-recall=%.3f extraction-coverage=%.3f (n=%d) vs R1 oracle 1.0 / fuzzy 0.37" % (r["recall"], r["coverage"], r["n"])
    if r["recall"] >= 0.55:
        return ("HARD_PASS", "HARD_PASS: LLM-extracted triples + substrate K-hop clears recall>=0.55 -- training-free BridgeRAG-equivalent works; discrete-structure pipeline viable on real text. " + s)
    if r["recall"] >= 0.45:
        return ("MIDDLE_BAND", "MIDDLE_BAND: LLM-triples K-hop 0.45-0.55 -- extraction is the gating cost (R1 oracle was 1.0). " + s)
    return ("HARD_FAIL", "HARD_FAIL: LLM-triples K-hop <0.45 -- Qwen-1.5B extraction too weak; escalate to a stronger extractor (gap is extraction, not substrate -- R1 oracle=1.0). " + s)


print("[config] anchor=%s mode=%s n_q=%d model=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, MODEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
