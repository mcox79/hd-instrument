"""
exp_sentiment_headtohead_calibrated_gpu_v1.py -- CALIBRATED sentiment head-to-head (resolves the broken-eval caveat) -- GPU.

ROUTING: resolve the OPEN classification-head-to-head caveat. The brief flagged BOTH prior LLM-eval paths as broken: free-gen
  parsing gave Qwen-0.5B SST-2 = 0.58 and naive length-normalized label-logprob gave 0.485 -- both ~chance, implausible for a
  0.5B instruct model (real zero-shot SST-2 is ~0.8+). The known cause is SURFACE-FORM BIAS: naive label-logprob is dominated by
  the model's prior P(" positive") vs P(" negative"), not by the review. The standard fix is CONTEXTUAL CALIBRATION (Zhao 2021) /
  PMI (Holtzman 2021): score(label) = logP(label | prompt) - logP(label | content-free prompt), which subtracts the surface-form
  prior. Substrate = averaged-perceptron bag-of-words (discriminative weighting). SST-2 (bundled). import torch first (PROT-020).
SANITY GATE (honest): if the CALIBRATED LLM is STILL implausibly low (<0.65 on SST-2), the eval is unreliable -> verdict UNKNOWN,
  NO substrate-beats-LLM claim. Only if the calibrated LLM lands in a plausible band do we trust the comparison.
PRE-REGISTERED: gate first. If llm_cal>=0.65: HARD_PASS substrate>=llm_cal | MIDDLE within 0.05 | HARD_FAIL substrate<llm_cal-0.05.
  Report substrate, llm_raw (naive logprob, diagnostic), llm_cal (calibrated) + latency. UNKNOWN if gate fails or setup fails.
ASCII-only.
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
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "sentiment_headtohead_calibrated_gpu_v1"))


def _feats(txt):
    ws = re.findall(r"[a-z]+", txt.lower()); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs


def main():
    print("[config] sentiment head-to-head (CALIBRATED)", flush=True)
    data = json.load(open(REPO / "experiments" / "data" / "sst2.json", encoding="utf-8"))
    LABELS = data["labels"]; train = data["train"]; test = data["test"][: (12 if SMOKE else 400)]
    if SMOKE: train = train[:500]
    # --- substrate: averaged perceptron over bag-of-words/bigram ---
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
    # --- LLM ---
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    name = "Qwen/Qwen2.5-0.5B-Instruct"
    tok = AutoTokenizer.from_pretrained(name)
    mdl = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded on", DEV, flush=True)

    def logp_total(prompt, cont):
        """Total (un-normalized) log-prob of cont tokens given prompt. Un-normalized so PMI subtraction cancels surface-form."""
        full = prompt + cont; ids = tok(full, return_tensors="pt").input_ids.to(DEV)
        pn = tok(prompt, return_tensors="pt").input_ids.shape[1]
        with torch.no_grad(): lp = torch.log_softmax(mdl(ids).logits[0], -1)
        s = 0.0
        for k in range(pn, ids.shape[1]): s += lp[k - 1, ids[0, k]].item()
        return s

    def mk_prompt(txt): return "Review: " + txt[:300] + "\nThe sentiment is"
    CF_PROMPTS = [mk_prompt(""), mk_prompt("N/A"), mk_prompt("nothing")]   # content-free baselines (Zhao 2021)
    # content-free label log-prob = surface-form prior to subtract
    cf = [sum(logp_total(p, " " + LABELS[k]) for p in CF_PROMPTS) / len(CF_PROMPTS) for k in range(len(LABELS))]
    print("  content-free label logprob (prior): %s" % ["%.3f" % x for x in cf], flush=True)
    t_l = time.time(); raw_cor = 0; cal_cor = 0
    for e in test:
        prompt = mk_prompt(e["text"])
        lps = [logp_total(prompt, " " + LABELS[k]) for k in range(len(LABELS))]
        raw_best = max(range(len(LABELS)), key=lambda k: lps[k])              # naive (surface-form biased)
        cal_best = max(range(len(LABELS)), key=lambda k: lps[k] - cf[k])      # calibrated / PMI
        if raw_best == e["label"]: raw_cor += 1
        if cal_best == e["label"]: cal_cor += 1
    llm_raw = raw_cor / len(test); llm_cal = cal_cor / len(test); llm_lat = (time.time() - t_l) / len(test)
    print("  LLM: raw(naive logprob)=%.3f  calibrated(PMI)=%.3f  (%.3fs/item)" % (llm_raw, llm_cal, llm_lat), flush=True)
    # --- verdict with sanity gate ---
    if llm_cal < 0.65:
        verdict = "UNKNOWN"
        msg = ("UNKNOWN: LLM baseline STILL implausible after contextual calibration (cal=%.3f < 0.65 on SST-2; real Qwen-0.5B "
               "zero-shot is ~0.8+). The LLM classification eval remains unreliable -- NO substrate-vs-LLM claim. substrate=%.3f, "
               "llm_raw=%.3f, llm_cal=%.3f.") % (llm_cal, sub_acc, llm_raw, llm_cal)
    else:
        win = sub_acc >= llm_cal
        verdict = "HARD_PASS" if win else ("MIDDLE_BAND" if sub_acc >= llm_cal - 0.05 else "HARD_FAIL")
        msg = ("%s: substrate sentiment=%.3f (%.6fs) vs Qwen-0.5B CALIBRATED=%.3f (%.3fs) -- %s. Calibration fixed the eval "
               "(naive logprob was %.3f ~chance; PMI-calibrated=%.3f is plausible). Substrate tiny+fast, deterministic.") % (
               verdict, sub_acc, sub_lat, llm_cal, llm_lat, "SUB>=LLM" if win else "LLM>", llm_raw, llm_cal)
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "sentiment_headtohead_calibrated_gpu_v1", "verdict": verdict, "verdict_msg": msg,
               "summary": msg, "elapsed_s": time.time() - t_s,
               "substrate_acc": round(sub_acc, 3), "llm_acc_raw": round(llm_raw, 3), "llm_acc_calibrated": round(llm_cal, 3),
               "sub_latency": sub_lat, "llm_latency": llm_lat}, open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert "BIAS" in _feats("hi there"); print("[selftest] PASS: sentiment-headtohead-calibrated", flush=True); sys.exit(0)
main()
