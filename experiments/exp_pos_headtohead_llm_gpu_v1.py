"""
exp_pos_headtohead_llm_gpu_v1.py -- STRUCTURED-PREDICTION head-to-head: substrate POS tagger vs LLM zero-shot -- GPU.

ROUTING: north-star extension to the substrate's STRONGEST capability. Classification head-to-heads done (topic substrate win
  scale-invariant; sentiment boundary). But the substrate is far stronger at STRUCTURED PREDICTION (POS 0.95) than classification.
  Can a comparable-size LLM match the tiny substrate POS tagger zero-shot? Substrate = discriminative structured-perceptron +
  Viterbi on UD-EWT (17 universal tags). LLM = Qwen2.5-1.5B-Instruct few-shot tagging, output space-separated tags aligned to
  tokens. Token accuracy for both. import torch first (PROT-020). Bundled UD-EWT (RESCUE).
ROBUST EVAL: align LLM tag list to gold tokens by position; if count mismatches, count missing/extra as wrong (honest penalty) and
  track per-sentence mismatch rate. SANITY GATE: if LLM token-count-mismatch rate > 0.40 (eval unreliable, can't align), -> UNKNOWN.
PRE-REGISTERED: HARD-PASS substrate >= LLM (tiny substrate matches/beats the LLM on POS). MIDDLE within 0.03. HARD-FAIL substrate <
  LLM - 0.03. UNKNOWN if gate fails or load fails. Report substrate acc, LLM acc, mismatch rate, latency.
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
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "pos_headtohead_llm_gpu_v1"))
MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
UTAGS = ["ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X"]


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


def main():
    print("[config] POS head-to-head (substrate structured-perceptron vs LLM few-shot)", flush=True)
    tr = [s for s in load_conllu("train") if 1 <= len(s) <= 40]
    te = [s for s in load_conllu("test") if 1 <= len(s) <= 30]
    if not SMOKE: tr = tr[:3000]
    else: tr = tr[:300]
    te = te[: (8 if SMOKE else 150)]
    train = [([t[1] for t in s], [t[2] for t in s]) for s in tr]
    test = [([t[1] for t in s], [t[2] for t in s]) for s in te]
    TAGS = sorted({t for _w, g in train for t in g})
    tagger = train_substrate(train, TAGS)
    t_s = time.time(); hit = tot = 0
    for words, gold in test:
        pred = tagger(words)
        for p, g in zip(pred, gold): hit += int(p == g); tot += 1
    sub_acc = hit / tot; sub_lat = (time.time() - t_s) / len(test)
    print("  substrate POS: acc=%.4f (%.5fs/sent, %d test sents)" % (sub_acc, sub_lat, len(test)), flush=True)
    # --- LLM ---
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(MODEL)
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded", MODEL, "on", DEV, flush=True)
    tagset_str = " ".join(UTAGS)
    fewshot = ("Words: The quick dog runs .\nTags: DET ADJ NOUN VERB PUNCT\n\n"
               "Words: She will go to Paris .\nTags: PRON AUX VERB ADP PROPN PUNCT\n\n")
    sysmsg = ("You are a part-of-speech tagger using Universal POS tags. Tagset: " + tagset_str +
              ". Output ONLY the tags separated by single spaces, one tag per word, in the SAME ORDER, exactly as many tags as words. No other text.")
    llm_hit = llm_tot = 0; mismatch_sents = 0; t_l = time.time()
    UPPER = {t.upper(): t for t in UTAGS}
    for words, gold in test:
        user = fewshot + "Words: " + " ".join(words) + "\nTags:"
        msgs = [{"role": "system", "content": sysmsg}, {"role": "user", "content": user}]
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True); ins = tok(p, return_tensors="pt").to(DEV)
        with torch.no_grad():
            o = mdl.generate(**ins, max_new_tokens=len(words) * 4 + 8, do_sample=False, pad_token_id=tok.eos_token_id)
        out = tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        line = out.splitlines()[0] if out else ""
        preds = [UPPER.get(x.strip().upper().strip(".,"), "X") for x in line.split()]
        if len(preds) != len(words): mismatch_sents += 1
        for i, g in enumerate(gold):
            pp = preds[i] if i < len(preds) else "X"
            llm_hit += int(pp == g); llm_tot += 1
    llm_acc = llm_hit / llm_tot; llm_lat = (time.time() - t_l) / len(test); mm_rate = mismatch_sents / len(test)
    print("  LLM POS: acc=%.4f (%.4fs/sent) | token-count-mismatch sents=%.3f" % (llm_acc, llm_lat, mm_rate), flush=True)
    # --- verdict ---
    if mm_rate > 0.40:
        verdict = "UNKNOWN"
        msg = ("UNKNOWN: LLM token-count-mismatch rate %.3f > 0.40 -- cannot reliably align LLM tags to tokens; eval unreliable. "
               "substrate=%.4f, LLM(approx)=%.4f.") % (mm_rate, sub_acc, llm_acc)
    else:
        win = sub_acc >= llm_acc
        verdict = "HARD_PASS" if win else ("MIDDLE_BAND" if sub_acc >= llm_acc - 0.03 else "HARD_FAIL")
        msg = ("%s: substrate POS=%.4f (%.5fs) vs Qwen-1.5B few-shot POS=%.4f (%.4fs) -- %s. Tiny substrate structured-predictor "
               "on the substrate's STRONGEST capability; mismatch-rate=%.3f. UD-EWT 17-tag, %d test, ~%dx faster." % (
               verdict, sub_acc, sub_lat, llm_acc, llm_lat, "SUB>=LLM" if win else "LLM>", mm_rate, len(test), int(llm_lat / max(sub_lat, 1e-6))))
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "pos_headtohead_llm_gpu_v1", "verdict": verdict, "verdict_msg": msg, "summary": msg,
               "elapsed_s": time.time() - t_s, "substrate_acc": round(sub_acc, 4), "llm_acc": round(llm_acc, 4),
               "llm_mismatch_rate": round(mm_rate, 3), "sub_latency": sub_lat, "llm_latency": llm_lat, "model": MODEL},
              open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert _shape("Bob") == "Cap" and len(UTAGS) == 17; print("[selftest] PASS: pos-headtohead-llm", flush=True); sys.exit(0)
main()
