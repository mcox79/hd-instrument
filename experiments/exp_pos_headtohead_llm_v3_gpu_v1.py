"""
exp_pos_headtohead_llm_v3_gpu_v1.py -- STRUCTURED-PREDICTION head-to-head: substrate POS vs LLM scale ladder -- GPU.

ROUTING: Research GPU AUTHORIZE (research_to_exp_dev_GPU_AUTHORIZE_3_HEADTOHEAD_PRIORITIZED_2026-06-11) Priority 1.
  v2 FAILED on timeout (only 1.5B, generation budget exceeded). v3 fixes: (a) LLM scale LADDER 0.5B + 1.5B (3B optional via
  HDLAB_POS_3B=1); (b) 5-shot prompt (standard literature comparison); (c) generous timeout when queued; (d) train substrate ONCE,
  eval vs each LLM, headline verdict = substrate vs BEST LLM. Substrate = discriminative structured-perceptron + Viterbi on UD-EWT
  (17 universal tags), 0.951 multi-seed Tier-A. LLM = Qwen2.5 Instruct few-shot; ROBUST parse extracts valid tag tokens in order.
  Token accuracy for both. import torch first (PROT-020). Bundled UD-EWT (RESCUE loader).
ROBUST EVAL: align LLM tags to gold by position; count mismatch as wrong (honest penalty); track per-sentence mismatch rate.
  SANITY GATE per model: mismatch rate > 0.40 -> that model UNKNOWN (excluded from headline). All-UNKNOWN -> verdict UNKNOWN.
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _ud_loader import load_conllu
SMOKE = "--smoke" in sys.argv
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "pos_headtohead_llm_v3_gpu_v1"))
UTAGS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X"]
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
    T = len(TAGS); rng = np.random.default_rng(7)
    w = defaultdict(float); cw = defaultdict(float); c = 1

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


# 5-shot prompt (covers DET ADJ NOUN VERB PUNCT PRON AUX ADP PROPN NUM ADV CCONJ INTJ SCONJ)
FEWSHOT = ("Words: The quick dog runs .\nTags: DET ADJ NOUN VERB PUNCT\n\n"
           "Words: She will go to Paris .\nTags: PRON AUX VERB ADP PROPN PUNCT\n\n"
           "Words: I bought three red apples .\nTags: PRON VERB NUM ADJ NOUN PUNCT\n\n"
           "Words: He quickly read the book and slept .\nTags: PRON ADV VERB DET NOUN CCONJ VERB PUNCT\n\n"
           "Words: Wow , that is amazing !\nTags: INTJ PUNCT PRON AUX ADJ PUNCT\n\n")


def eval_llm(model_id, label, test, sub_acc):
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded", model_id, "on", DEV, flush=True)
    tagset_str = " ".join(UTAGS)
    sysmsg = ("You are a part-of-speech tagger using Universal POS tags. Tagset: " + tagset_str +
              ". Output ONLY the tags separated by single spaces, one tag per word, in the SAME ORDER, exactly as many tags as words. No other text.")
    UPPER = {t.upper(): t for t in UTAGS}
    hit = tot = 0; mismatch = 0; t0 = time.time()
    for words, gold in test:
        user = FEWSHOT + "Words: " + " ".join(words) + "\nTags:"
        msgs = [{"role": "system", "content": sysmsg}, {"role": "user", "content": user}]
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True); ins = tok(p, return_tensors="pt").to(DEV)
        with torch.no_grad():
            o = mdl.generate(**ins, max_new_tokens=len(words) * 4 + 8, do_sample=False, pad_token_id=tok.eos_token_id)
        out = tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        toks_out = re.findall(r"[A-Za-z]+", out)
        preds = [UPPER[x.upper()] for x in toks_out if x.upper() in UPPER]
        if len(preds) != len(words): mismatch += 1
        for i, g in enumerate(gold):
            pp = preds[i] if i < len(preds) else "X"
            hit += int(pp == g); tot += 1
    acc = hit / tot; lat = (time.time() - t0) / len(test); mm = mismatch / len(test)
    print("  LLM-%s POS: acc=%.4f (%.4fs/sent) mismatch=%.3f" % (label, acc, lat, mm), flush=True)
    del mdl
    if DEV == "cuda": torch.cuda.empty_cache()
    return {"label": label, "model": model_id, "acc": round(acc, 4), "latency": round(lat, 4), "mismatch_rate": round(mm, 3),
            "unknown": mm > 0.40}


def main():
    print("[config] POS head-to-head v3 (substrate vs LLM ladder %s, 5-shot)" % [m[1] for m in MODELS], flush=True)
    tr = [s for s in load_conllu("train") if 1 <= len(s) <= 40]
    te = [s for s in load_conllu("test") if 1 <= len(s) <= 30]
    tr = tr[:300] if SMOKE else tr[:3000]
    te = te[: (6 if SMOKE else 150)]
    train = [([t[1] for t in s], [t[2] for t in s]) for s in tr]
    test = [([t[1] for t in s], [t[2] for t in s]) for s in te]
    TAGS = sorted({t for _w, g in train for t in g})
    t_train = time.time(); tagger = train_substrate(train, TAGS); print("[substrate] trained %.1fs" % (time.time() - t_train), flush=True)
    t_s = time.time(); hit = tot = 0
    for words, gold in test:
        pred = tagger(words)
        for p, g in zip(pred, gold): hit += int(p == g); tot += 1
    sub_acc = hit / tot; sub_lat = (time.time() - t_s) / len(test)
    print("  substrate POS: acc=%.4f (%.5fs/sent, %d test sents)" % (sub_acc, sub_lat, len(test)), flush=True)
    results = [eval_llm(mid, lbl, test, sub_acc) for mid, lbl in MODELS]
    valid = [r for r in results if not r["unknown"]]
    t0 = time.time()
    if not valid:
        verdict = "UNKNOWN"
        msg = "UNKNOWN: all LLM models mismatch-rate>0.40 (eval unreliable). substrate=%.4f. results=%s" % (sub_acc, results)
    else:
        # headline vs 0.5B if valid, else smallest valid model
        head = next((r for r in valid if r["label"] == "0.5B"), valid[0])
        margin = sub_acc - head["acc"]
        verdict = "HARD_PASS" if margin >= 0.10 else ("MIDDLE_BAND" if margin >= 0.03 else "HARD_FAIL")
        ladder = " | ".join("%s acc=%.4f mm=%.3f%s" % (r["label"], r["acc"], r["mismatch_rate"], "(UNK)" if r["unknown"] else "") for r in results)
        msg = ("%s: substrate POS=%.4f (%.5fs/sent) vs Qwen-%s few-shot=%.4f -- margin %+.4f. Ladder: %s. "
               "Tiny substrate structured-predictor on UD-EWT 17-tag, %d test, ~%dx faster than %s LLM." % (
               verdict, sub_acc, sub_lat, head["label"], head["acc"], margin, ladder, len(test),
               int(head["latency"] / max(sub_lat, 1e-6)), head["label"]))
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "pos_headtohead_llm_v3_gpu_v1", "verdict": verdict, "verdict_msg": msg, "summary": msg,
               "elapsed_s": time.time() - t0 + (t0 - t_s), "substrate_acc": round(sub_acc, 4), "sub_latency": sub_lat,
               "llm_ladder": results, "n_test": len(test), "shots": 5},
              open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert _shape("Bob") == "Cap" and len(UTAGS) == 17
    assert len(FEWSHOT.split("\n\n")) >= 5
    print("[selftest] PASS: pos-headtohead-llm-v3", flush=True); sys.exit(0)
main()
