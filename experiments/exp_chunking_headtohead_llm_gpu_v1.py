"""
exp_chunking_headtohead_llm_gpu_v1.py -- CoNLL-2000 chunking head-to-head: substrate vs LLM scale ladder -- GPU.

ROUTING: Research GPU AUTHORIZE (research_to_exp_dev_GPU_AUTHORIZE_3_HEADTOHEAD_PRIORITIZED_2026-06-11) Priority 3 (AFTER richfeat).
  Substrate chunker = PP-364 POS tagger -> rich-feature POS-cascade chunker (structured-perceptron + Viterbi; transfer-validated
  0.923+, richfeat features). LLM = Qwen2.5 Instruct 0.5B + 1.5B (3B optional HDLAB_CHK_3B=1), 5-shot, literature-standard bracketed
  chunking ("[NP the dog] [VP runs]"), parsed by a SEQUENTIAL CURSOR to token spans -> span-F1 (same metric, same 150-sent subset).
  import torch first (PROT-020). Bundled CoNLL-2000.
ROBUST EVAL: bracket groups parsed in order; each phrase matched to the next contiguous token run from a moving cursor (chunking is
  a sequential cover). Phrases that don't match at/after the cursor counted as FP + tracked. SANITY GATE per model: unmatch-rate >
  0.40 -> that model UNKNOWN. All-UNKNOWN -> UNKNOWN.
PRE-REGISTERED (vs 0.5B headline; Research): HARD-PASS substrate-win >= +0.10 / MIDDLE +0.03-0.10 / HARD-FAIL < +0.03.
ASCII-only.
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys, time, json, re
from pathlib import Path
from collections import defaultdict
import numpy as np
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
SMOKE = "--smoke" in sys.argv
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "chunking_headtohead_llm_gpu_v1"))
MODELS = [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B"), ("Qwen/Qwen2.5-1.5B-Instruct", "1.5B")]
if os.environ.get("HDLAB_CHK_3B") == "1":
    MODELS.append(("Qwen/Qwen2.5-3B-Instruct", "3B"))
if SMOKE:
    MODELS = [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B")]
VALID_TYPES = {"NP", "VP", "PP", "ADVP", "ADJP", "SBAR", "PRT", "CONJP", "INTJ", "LST"}


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper(): return "Cap"
    if "-" in w: return "HYP"
    return "low"


def _pos_emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs


def _train_seqperc(train, TAGS, emit_fn, epochs, seed):
    T = len(TAGS); rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "T_%s~%s" % (p, t)

    def vit(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in emit_fn(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt("<S>", TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    for ep in range(epochs):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = vit(words, w)
            if pred != gold:
                pg = "<S>"; pp = "<S>"
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in emit_fn(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in emit_fn(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    return lambda words: vit(words, avg)


def _chunk_emit(words, pos, i, tag):
    n = len(words); w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (2, 3):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    pw = words[i - 1].lower() if i > 0 else "<S>"; nw = words[i + 1].lower() if i + 1 < n else "<E>"
    ppw = words[i - 2].lower() if i > 1 else "<S>"; nnw = words[i + 2].lower() if i + 2 < n else "<E>"
    fs.append("pw_%s~%s" % (pw, tag)); fs.append("nw_%s~%s" % (nw, tag))
    fs.append("ppw_%s~%s" % (ppw, tag)); fs.append("nnw_%s~%s" % (nnw, tag))
    fs.append("psh_%s_%s~%s" % (_shape(words[i - 1]) if i > 0 else "<S>", _shape(w), tag))
    p0 = pos[i]; pm = pos[i - 1] if i > 0 else "<S>"; pn = pos[i + 1] if i + 1 < n else "<E>"
    pmm = pos[i - 2] if i > 1 else "<S>"; pnn = pos[i + 2] if i + 2 < n else "<E>"
    fs.append("pos_%s~%s" % (p0, tag)); fs.append("ppos_%s~%s" % (pm, tag)); fs.append("npos_%s~%s" % (pn, tag))
    fs.append("ppos2_%s~%s" % (pmm, tag)); fs.append("npos2_%s~%s" % (pnn, tag))
    fs.append("posbig_%s_%s~%s" % (pm, p0, tag)); fs.append("posbigN_%s_%s~%s" % (p0, pn, tag))
    fs.append("postri_%s_%s_%s~%s" % (pm, p0, pn, tag))
    return fs


def _spans(tags):
    sp = set(); i = 0; n = len(tags)
    while i < n:
        t = tags[i]
        if t.startswith("B-"):
            ty = t[2:]; j = i + 1
            while j < n and tags[j] == "I-" + ty: j += 1
            sp.add((i, j, ty)); i = j
        else: i += 1
    return sp


def train_chunker(tr_s, seed):
    pos_train = [(e["tokens"], e["pos"]) for e in tr_s if 1 <= len(e["tokens"]) <= 60]
    PTAGS = sorted({t for _w, g in pos_train for t in g})
    tagger = _train_seqperc(pos_train, PTAGS, _pos_emit, 5 if not SMOKE else 2, seed)

    def mk(sents):
        out = []
        for e in sents:
            if not (1 <= len(e["tokens"]) <= 60): continue
            out.append((e["tokens"], e["chunk_bio"], tagger(e["tokens"])))
        return out
    train = mk(tr_s)
    CTAGS = sorted({t for _w, g, _p in train for t in g})
    T = len(CTAGS); rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "CT_%s~%s" % (p, t)

    def cvit(words, pos, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _chunk_emit(words, pos, i, CTAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(CTAGS[j], CTAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt("<S>", CTAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [CTAGS[k] for k in seq]

    for ep in range(6 if not SMOKE else 3):
        for si in rng.permutation(len(train)):
            words, gold, pos = train[si]; pred = cvit(words, pos, w)
            if pred != gold:
                pg = "<S>"; pp = "<S>"
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _chunk_emit(words, pos, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _chunk_emit(words, pos, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    return tagger, (lambda words: cvit(words, tagger(words), avg))


def _f1(gold_sets, pred_sets, extra_fp=0):
    tp = fp = fn = 0
    for gs, ps in zip(gold_sets, pred_sets):
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    fp += extra_fp
    p = tp / (tp + fp + 1e-9); r = tp / (tp + fn + 1e-9); return 2 * p * r / (p + r + 1e-9)


FEWSHOT = ("Sentence: The big dog chased the cat .\nChunks: [NP The big dog] [VP chased] [NP the cat] .\n\n"
           "Sentence: She is in the house .\nChunks: [NP She] [VP is] [PP in] [NP the house] .\n\n"
           "Sentence: They quickly ran away .\nChunks: [NP They] [ADVP quickly] [VP ran] [ADVP away] .\n\n"
           "Sentence: I want to buy a car .\nChunks: [NP I] [VP want to buy] [NP a car] .\n\n"
           "Sentence: He said that it works .\nChunks: [NP He] [VP said] [SBAR that] [NP it] [VP works] .\n\n")
SYS = ("You are a text chunker (shallow parser). Segment the sentence into non-overlapping chunks, each wrapped as "
       "[TYPE words]. Types: NP (noun phrase), VP (verb phrase), PP (preposition), ADVP (adverb phrase), ADJP (adjective phrase), "
       "SBAR, PRT. Keep every word in order; leave punctuation outside brackets. Output ONLY the bracketed sentence.")


def _parse_brackets_to_spans(tokens, text):
    """Cursor-match bracketed phrases to contiguous token spans. Returns (spanset, n_unmatched)."""
    tlc = [w.lower() for w in tokens]; n = len(tlc)
    groups = re.findall(r"\[([A-Za-z]+)\s+([^\]]+)\]", text)
    sp = set(); cur = 0; unmatched = 0
    for ty, phrase in groups:
        ty = ty.upper()
        if ty not in VALID_TYPES: unmatched += 1; continue
        sub = phrase.lower().split()
        if not sub: unmatched += 1; continue
        L = len(sub); found = -1
        for i in range(cur, n - L + 1):
            if tlc[i:i + L] == sub: found = i; break
        if found < 0: unmatched += 1; continue
        sp.add((found, found + L, ty)); cur = found + L
    return sp, unmatched


def eval_llm(model_id, label, test_tokens):
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded", model_id, "on", DEV, flush=True)
    pred_sets = []; unmatched_total = 0; t0 = time.time()
    for tokens in test_tokens:
        user = FEWSHOT + "Sentence: " + " ".join(tokens) + "\nChunks:"
        msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": user}]
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True); ins = tok(p, return_tensors="pt").to(DEV)
        with torch.no_grad():
            o = mdl.generate(**ins, max_new_tokens=len(tokens) * 4 + 24, do_sample=False, pad_token_id=tok.eos_token_id)
        out = tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        sp, un = _parse_brackets_to_spans(tokens, out); pred_sets.append(sp); unmatched_total += un
    lat = (time.time() - t0) / len(test_tokens)
    total_pred = sum(len(s) for s in pred_sets) + unmatched_total
    unmatch_rate = unmatched_total / max(total_pred, 1)
    del mdl
    if DEV == "cuda": torch.cuda.empty_cache()
    return {"label": label, "model": model_id, "pred_sets": pred_sets, "unmatched": unmatched_total,
            "unmatch_rate": round(unmatch_rate, 3), "latency": round(lat, 4), "unknown": unmatch_rate > 0.40}


def main():
    print("[config] chunking head-to-head (substrate rich-cascade vs LLM ladder %s, 5-shot bracketed)" % [m[1] for m in MODELS], flush=True)
    d = json.load(open(REPO / "experiments" / "data" / "conll2000.json", encoding="utf-8"))
    tr_s = d["splits"]["train"]; dv_s = d["splits"]["test"]
    if SMOKE: tr_s = tr_s[:400]; dv_s = dv_s[:200]
    n_test = 6 if SMOKE else 150
    test = [e for e in dv_s if 1 <= len(e["tokens"]) <= 60][:n_test]
    seed = int(os.environ.get("HDLAB_SEED", "1028"))
    t_tr = time.time(); tagger, chunker = train_chunker(tr_s, seed); print("[substrate] trained %.1fs" % (time.time() - t_tr), flush=True)
    test_tokens = [e["tokens"] for e in test]
    gold_sets = [_spans(e["chunk_bio"]) for e in test]
    t_s = time.time(); sub_pred_sets = [_spans(chunker(t)) for t in test_tokens]; sub_lat = (time.time() - t_s) / len(test)
    sub_f1 = _f1(gold_sets, sub_pred_sets)
    print("  substrate chunking: span-F1=%.4f (%.5fs/sent, %d test)" % (sub_f1, sub_lat, len(test)), flush=True)
    results = []
    for mid, lbl in MODELS:
        r = eval_llm(mid, lbl, test_tokens)
        r["f1"] = round(_f1(gold_sets, r["pred_sets"], extra_fp=r["unmatched"]), 4)
        r.pop("pred_sets")
        print("  LLM-%s chunking: span-F1=%.4f (%.4fs/sent) unmatch=%.3f" % (lbl, r["f1"], r["latency"], r["unmatch_rate"]), flush=True)
        results.append(r)
    valid = [r for r in results if not r["unknown"]]
    t0 = time.time()
    if not valid:
        verdict = "UNKNOWN"; msg = "UNKNOWN: all LLM models unmatch-rate>0.40. substrate=%.4f. results=%s" % (sub_f1, results)
    else:
        head = next((r for r in valid if r["label"] == "0.5B"), valid[0]); margin = sub_f1 - head["f1"]
        verdict = "HARD_PASS" if margin >= 0.10 else ("MIDDLE_BAND" if margin >= 0.03 else "HARD_FAIL")
        ladder = " | ".join("%s F1=%.4f unmatch=%.3f%s" % (r["label"], r["f1"], r["unmatch_rate"], "(UNK)" if r["unknown"] else "") for r in results)
        msg = ("%s: substrate chunking span-F1=%.4f (%.5fs/sent) vs Qwen-%s few-shot=%.4f -- margin %+.4f. Ladder: %s. "
               "CoNLL-2000, %d test, ~%dx faster than %s." % (
               verdict, sub_f1, sub_lat, head["label"], head["f1"], margin, ladder, len(test),
               int(head["latency"] / max(sub_lat, 1e-6)), head["label"]))
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "chunking_headtohead_llm_gpu_v1", "verdict": verdict, "verdict_msg": msg, "summary": msg,
               "elapsed_s": time.time() - t0 + (t0 - t_s), "substrate_f1": round(sub_f1, 4), "sub_latency": sub_lat,
               "llm_ladder": results, "n_test": len(test), "shots": 5},
              open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert _spans(["B-NP", "I-NP", "B-VP", "O"]) == {(0, 2, "NP"), (2, 3, "VP")}
    sp, un = _parse_brackets_to_spans(["The", "dog", "runs", "."], "[NP The dog] [VP runs] .")
    assert sp == {(0, 2, "NP"), (2, 3, "VP")} and un == 0
    sp2, un2 = _parse_brackets_to_spans(["a", "b"], "[NP zzz]")
    assert un2 == 1
    assert len(FEWSHOT.split("\n\n")) >= 5
    print("[selftest] PASS: chunking-headtohead", flush=True); sys.exit(0)
main()
