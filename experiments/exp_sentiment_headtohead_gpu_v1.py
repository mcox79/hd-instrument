"""
exp_sentiment_headtohead_gpu_v1.py -- text-classification head-to-head: substrate vs LLM on AG-News -- GPU.

ROUTING: net-new capability probe (text/document classification, a new task TYPE beyond sequence labeling) + north-star dim.
  Substrate = averaged-perceptron bag-of-words/bigram classifier (discriminative weighting, the universal lever). LLM =
  Qwen2.5-0.5B-Instruct zero-shot picking 1 of 4 topics. AG-News (bundled, World/Sports/Business/Sci-Tech). Reports both
  accuracies + LLM latency. Substrate-classical, no LLM in the substrate path. import torch (PROT-020).
PRE-REGISTERED: HARD-PASS substrate >= LLM (tiny substrate matches/beats the 0.5B LLM on topic classification). MIDDLE within 0.05.
  HARD-FAIL substrate < LLM - 0.05. UNKNOWN if setup fails.
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
OUT = REPO / "data" / "exp_sentiment_headtohead_gpu_v1"
def _feats(txt):
    ws = re.findall(r"[a-z]+", txt.lower()); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs
def main():
    print("[config] textclass head-to-head", flush=True)
    data = json.load(open(REPO / "experiments" / "data" / "sst2.json", encoding="utf-8"))
    LABELS = data["labels"]; train = data["train"]; test = data["test"][: (40 if SMOKE else 400)]
    if SMOKE: train = train[:500]
    # substrate: averaged perceptron over bag-of-words/bigram
    import random
    rng = random.Random(0)
    LAB = list(range(len(LABELS)))
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
    scor = 0
    t_s = time.time()
    for e in test:
        feats = _feats(e["text"]); sc = {l: sum(avg[l].get(f, 0.0) for f in feats) for l in LAB}
        if max(LAB, key=lambda l: (sc[l], l)) == e["label"]: scor += 1
    sub_acc = scor / len(test); sub_lat = (time.time() - t_s) / len(test)
    print("  substrate: acc=%.3f (%.5fs/item)" % (sub_acc, sub_lat), flush=True)
    # LLM
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    name = "Qwen/Qwen2.5-0.5B-Instruct"
    tok = AutoTokenizer.from_pretrained(name); mdl = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded on", DEV, flush=True)
    lcor = 0; t_l = time.time()
    for e in test:
        msgs = [{"role": "user", "content": "Sentiment of this sentence (positive or negative)? " + e["text"][:400] + "\nAnswer with exactly one: " + ", ".join(LABELS) + "."}]
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True); ins = tok(p, return_tensors="pt").to(DEV)
        with torch.no_grad():
            o = mdl.generate(**ins, max_new_tokens=8, do_sample=False, pad_token_id=tok.eos_token_id)
        txt = tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True).lower()
        pred = -1
        for k, lb in enumerate(LABELS):
            if lb.lower().split("/")[0] in txt: pred = k; break
        if pred == e["label"]: lcor += 1
    llm_acc = lcor / len(test); llm_lat = (time.time() - t_l) / len(test)
    win = sub_acc >= llm_acc
    verdict = "HARD_PASS" if win else ("MIDDLE_BAND" if sub_acc >= llm_acc - 0.05 else "HARD_FAIL")
    msg = "%s: substrate text-classifier acc=%.3f (%.5fs/item) vs Qwen-0.5B acc=%.3f (%.3fs/item) -- %s. Substrate %dx faster, tiny. SST-2 sentiment." % (
        verdict, sub_acc, sub_lat, llm_acc, llm_lat, "SUBSTRATE>=LLM" if win else "LLM>", int(llm_lat / max(sub_lat, 1e-6)))
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "sentiment_headtohead_gpu_v1", "verdict": verdict, "verdict_msg": msg,
               "substrate_acc": round(sub_acc, 3), "llm_acc": round(llm_acc, 3), "sub_latency": sub_lat, "llm_latency": llm_lat}, open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)
if "--self-test" in sys.argv:
    assert "BIAS" in _feats("hi there"); print("[selftest] PASS: sentiment-headtohead", flush=True); sys.exit(0)
main()
