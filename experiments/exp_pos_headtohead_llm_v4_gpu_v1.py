"""
exp_pos_headtohead_llm_v4_gpu_v1.py -- POS head-to-head, ROBUST word/TAG format -- GPU.

ROUTING: Research GPU AUTHORIZE Priority 1. v3 completed but verdict UNKNOWN: LLMs emit bare-tag sequences that don't align to gold
  (token-count mismatch >0.96 -> sanity gate UNKNOWN). v4 fixes the LLM FORMAT: ask for "word/TAG" pairs (self-aligning -- each tag
  tied to its word), parse by splitting each output token on the LAST '/', then CURSOR-ALIGN parsed (word,tag) pairs to the gold
  words (robust to a dropped/added word). Substrate = same structured-perceptron+Viterbi POS tagger (UD-EWT 17-tag, 0.951 Tier-A).
  LLM = Qwen2.5 Instruct 0.5B + 1.5B (3B optional HDLAB_POS_3B=1), 5-shot. import torch first (PROT-020). Bundled UD-EWT.
ROBUST EVAL: gold word with no matching parsed pair -> counted wrong + tracked as unaligned. SANITY GATE per model: per-word
  unaligned-rate > 0.40 -> that model UNKNOWN (excluded from headline). All-UNKNOWN -> UNKNOWN.
PRE-REGISTERED (vs 0.5B headline; Research): HARD-PASS substrate-win >= +0.10 / MIDDLE +0.03-0.10 / HARD-FAIL < +0.03.
ASCII-only.
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys, time, json
from pathlib import Path
from collections import defaultdict
import numpy as np
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _ud_loader import load_conllu
SMOKE = "--smoke" in sys.argv
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "pos_headtohead_llm_v4_gpu_v1"))
UTAGS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X"]
UPPER = {t.upper(): t for t in UTAGS}
MODELS = [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B"), ("Qwen/Qwen2.5-1.5B-Instruct", "1.5B")]
if os.environ.get("HDLAB_POS_3B") == "1":
    MODELS.append(("Qwen/Qwen2.5-3B-Instruct", "3B"))
if SMOKE:
    MODELS = [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B")]


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs


def train_substrate(train, TAGS):
    T = len(TAGS); rng = np.random.default_rng(7); w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "tt_%s~%s" % (p, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt("<S>", TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    for ep in range(6 if not SMOKE else 2):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = viterbi(words, w)
            if pred != gold:
                pg = "<S>"; pp = "<S>"
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _emit(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    return lambda words: viterbi(words, avg)


# word/TAG few-shot (self-aligning)
FEWSHOT = ("Words: The quick dog runs .\nTagged: The/DET quick/ADJ dog/NOUN runs/VERB ./PUNCT\n\n"
           "Words: She will go to Paris .\nTagged: She/PRON will/AUX go/VERB to/ADP Paris/PROPN ./PUNCT\n\n"
           "Words: I bought three red apples .\nTagged: I/PRON bought/VERB three/NUM red/ADJ apples/NOUN ./PUNCT\n\n"
           "Words: He quickly read the book and slept .\nTagged: He/PRON quickly/ADV read/VERB the/DET book/NOUN and/CCONJ slept/VERB ./PUNCT\n\n"
           "Words: Wow , that is amazing !\nTagged: Wow/INTJ ,/PUNCT that/PRON is/AUX amazing/ADJ !/PUNCT\n\n")
SYS = ("You are a part-of-speech tagger using Universal POS tags (" + " ".join(UTAGS) + "). For EACH word output the word followed "
       "by a slash and its tag, like word/TAG, separated by single spaces, in the SAME ORDER, one per word. Output ONLY the tagged words.")


def _parse_aligned(out, words):
    """Parse 'word/TAG' pairs and cursor-align to gold words. Returns (pred_tags list len=len(words), n_unaligned)."""
    pairs = []
    for tokn in out.split():
        if "/" in tokn:
            wpart, _, tpart = tokn.rpartition("/")
            T = tpart.upper()
            if T in UPPER and wpart: pairs.append((wpart.lower(), UPPER[T]))
    pred_tags = []; unaligned = 0; cur = 0
    for gw in (w.lower() for w in words):
        hit = None
        for k in range(cur, min(len(pairs), cur + 6)):  # bounded look-ahead to resync on drops/insertions
            if pairs[k][0] == gw: hit = pairs[k][1]; cur = k + 1; break
        if hit is None:
            hit = "X"; unaligned += 1  # no match in window -> wrong, but do NOT consume a pair (keep cursor to resync)
        pred_tags.append(hit)
    return pred_tags, unaligned


def eval_llm(model_id, label, test):
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded", model_id, "on", DEV, flush=True)
    hit = tot = 0; unaligned_total = 0; t0 = time.time()
    for words, gold in test:
        user = FEWSHOT + "Words: " + " ".join(words) + "\nTagged:"
        msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": user}]
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True); ins = tok(p, return_tensors="pt").to(DEV)
        with torch.no_grad():
            o = mdl.generate(**ins, max_new_tokens=len(words) * 6 + 16, do_sample=False, pad_token_id=tok.eos_token_id)
        out = tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        pred, un = _parse_aligned(out, words); unaligned_total += un
        for p_, g in zip(pred, gold): hit += int(p_ == g); tot += 1
    acc = hit / tot; lat = (time.time() - t0) / len(test); un_rate = unaligned_total / max(tot, 1)
    print("  LLM-%s POS: acc=%.4f (%.4fs/sent) unaligned=%.3f" % (label, acc, lat, un_rate), flush=True)
    del mdl
    if DEV == "cuda": torch.cuda.empty_cache()
    return {"label": label, "model": model_id, "acc": round(acc, 4), "latency": round(lat, 4),
            "unaligned_rate": round(un_rate, 3), "unknown": un_rate > 0.40}


def main():
    print("[config] POS head-to-head v4 (word/TAG format; ladder %s, 5-shot)" % [m[1] for m in MODELS], flush=True)
    tr = [s for s in load_conllu("train") if 1 <= len(s) <= 40]
    te = [s for s in load_conllu("test") if 1 <= len(s) <= 30]
    tr = tr[:300] if SMOKE else tr[:3000]
    te = te[: (6 if SMOKE else 150)]
    train = [([t[1] for t in s], [t[2] for t in s]) for s in tr]
    test = [([t[1] for t in s], [t[2] for t in s]) for s in te]
    TAGS = sorted({t for _w, g in train for t in g})
    t_tr = time.time(); tagger = train_substrate(train, TAGS); print("[substrate] trained %.1fs" % (time.time() - t_tr), flush=True)
    t_s = time.time(); hit = tot = 0
    for words, gold in test:
        pred = tagger(words)
        for p, g in zip(pred, gold): hit += int(p == g); tot += 1
    sub_acc = hit / tot; sub_lat = (time.time() - t_s) / len(test)
    print("  substrate POS: acc=%.4f (%.5fs/sent, %d test)" % (sub_acc, sub_lat, len(test)), flush=True)
    results = [eval_llm(mid, lbl, test) for mid, lbl in MODELS]
    valid = [r for r in results if not r["unknown"]]
    t0 = time.time()
    if not valid:
        verdict = "UNKNOWN"; msg = "UNKNOWN: all LLM models unaligned-rate>0.40. substrate=%.4f. results=%s" % (sub_acc, results)
    else:
        head = next((r for r in valid if r["label"] == "0.5B"), valid[0]); margin = sub_acc - head["acc"]
        verdict = "HARD_PASS" if margin >= 0.10 else ("MIDDLE_BAND" if margin >= 0.03 else "HARD_FAIL")
        ladder = " | ".join("%s acc=%.4f unaligned=%.3f%s" % (r["label"], r["acc"], r["unaligned_rate"], "(UNK)" if r["unknown"] else "") for r in results)
        msg = ("%s: substrate POS=%.4f (%.5fs/sent) vs Qwen-%s few-shot=%.4f -- margin %+.4f. Ladder: %s. "
               "UD-EWT 17-tag, %d test, ~%dx faster than %s." % (
               verdict, sub_acc, sub_lat, head["label"], head["acc"], margin, ladder, len(test),
               int(head["latency"] / max(sub_lat, 1e-6)), head["label"]))
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "pos_headtohead_llm_v4_gpu_v1", "verdict": verdict, "verdict_msg": msg, "summary": msg,
               "elapsed_s": time.time() - t0 + (t0 - t_s), "substrate_acc": round(sub_acc, 4), "sub_latency": sub_lat,
               "llm_ladder": results, "n_test": len(test), "shots": 5},
              open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    pred, un = _parse_aligned("The/DET quick/ADJ dog/NOUN runs/VERB ./PUNCT", ["The", "quick", "dog", "runs", "."])
    assert pred == ["DET", "ADJ", "NOUN", "VERB", "PUNCT"] and un == 0
    pred2, un2 = _parse_aligned("The/DET dog/NOUN", ["The", "big", "dog"])  # dropped 'big'
    assert pred2[0] == "DET" and pred2[2] == "NOUN" and un2 >= 1
    assert len(FEWSHOT.split("\n\n")) >= 5
    print("[selftest] PASS: pos-headtohead-llm-v4", flush=True); sys.exit(0)
main()
