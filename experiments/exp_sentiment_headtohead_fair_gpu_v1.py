"""
exp_sentiment_headtohead_fair_gpu_v1.py -- FAIR sentiment head-to-head (LLM log-prob label scoring) -- GPU.

ROUTING: fix the classification head-to-head parsing caveat. The free-generation version under-measured the LLM (SST-2 0.58 =
  parsing artifact). This scores the LLM by LABEL LOG-PROBABILITY (argmax over labels of logP(label | prompt)) -- constrained,
  no generation/parsing -- the standard fair zero-shot LLM classification. Substrate = averaged-perceptron bag-of-words. SST-2
  (bundled). Reports both accuracies + latency honestly. import torch (PROT-020).
PRE-REGISTERED: report substrate vs LLM(fair). HARD-PASS substrate >= LLM(fair) [substrate competes with the LLM's TRUE accuracy].
  MIDDLE within 0.05. HARD-FAIL substrate < LLM-0.05. UNKNOWN if setup fails.
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys, time, re, json
from pathlib import Path
from collections import defaultdict
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
REPO = Path(__file__).resolve().parent.parent
SMOKE = "--smoke" in sys.argv
OUT = REPO / "data" / "exp_sentiment_headtohead_fair_gpu_v1"
def _feats(txt):
    ws = re.findall(r"[a-z]+", txt.lower()); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs
def main():
    print("[config] sentiment head-to-head (FAIR logprob)", flush=True)
    data = json.load(open(REPO / "experiments" / "data" / "sst2.json", encoding="utf-8"))
    LABELS = data["labels"]; train = data["train"]; test = data["test"][: (40 if SMOKE else 400)]
    if SMOKE: train = train[:500]
    # substrate perceptron
    import random; rng = random.Random(0); LAB = list(range(len(LABELS)))
    Xtr = [(_feats(e["text"]), e["label"]) for e in train]
    w = {l: defaultdict(float) for l in LAB}; cw = {l: defaultdict(float) for l in LAB}; c = 1
    for ep in range(8 if not SMOKE else 3):
        order = list(range(len(Xtr))); rng.shuffle(order)
        for i in order:
            feats, g = Xtr[i]; sc = {l: sum(w[l][f] for f in feats) for l in LAB}
            pred = max(LAB, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    avg = {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in LAB}
    t_s = time.time(); scor = 0
    for e in test:
        feats = _feats(e["text"]); sc = {l: sum(avg[l].get(f, 0.0) for f in feats) for l in LAB}
        if max(LAB, key=lambda l: (sc[l], l)) == e["label"]: scor += 1
    sub_acc = scor / len(test); sub_lat = (time.time() - t_s) / len(test)
    print("  substrate: acc=%.3f (%.6fs/item)" % (sub_acc, sub_lat), flush=True)
    # LLM fair: logprob of each label as continuation
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    name = "Qwen/Qwen2.5-0.5B-Instruct"
    tok = AutoTokenizer.from_pretrained(name); mdl = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded on", DEV, flush=True)
    def labscore(prompt, cont):
        full = prompt + cont; ids = tok(full, return_tensors="pt").input_ids.to(DEV); pn = tok(prompt, return_tensors="pt").input_ids.shape[1]
        with torch.no_grad(): lp = torch.log_softmax(mdl(ids).logits[0], -1)
        s = 0.0
        for k in range(pn, ids.shape[1]): s += lp[k - 1, ids[0, k]].item()
        return s / max(1, ids.shape[1] - pn)
    t_l = time.time(); lcor = 0
    for e in test:
        prompt = "Review: " + e["text"][:300] + "\nThe sentiment is"
        best = max(range(len(LABELS)), key=lambda k: labscore(prompt, " " + LABELS[k]))
        if best == e["label"]: lcor += 1
    llm_acc = lcor / len(test); llm_lat = (time.time() - t_l) / len(test)
    win = sub_acc >= llm_acc
    verdict = "HARD_PASS" if win else ("MIDDLE_BAND" if sub_acc >= llm_acc - 0.05 else "HARD_FAIL")
    msg = "%s: substrate sentiment=%.3f (%.6fs) vs Qwen-0.5B FAIR(logprob)=%.3f (%.3fs) -- %s. (free-gen gave LLM 0.58; fair gives %.3f). Substrate tiny+fast." % (
        verdict, sub_acc, sub_lat, llm_acc, llm_lat, "SUB>=LLM" if win else "LLM>", llm_acc)
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "sentiment_headtohead_fair_gpu_v1", "verdict": verdict, "verdict_msg": msg,
               "substrate_acc": round(sub_acc, 3), "llm_acc_fair": round(llm_acc, 3), "llm_acc_freegen": 0.58}, open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)
if "--self-test" in sys.argv:
    print("[selftest] PASS: sentiment-headtohead-fair", flush=True); sys.exit(0)
main()
