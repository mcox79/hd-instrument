"""
exp_textclass_headtohead_calibrated_gpu_v1.py -- CALIBRATED 4-class topic head-to-head (AG-News) -- GPU.

ROUTING: generalize the calibrated classification head-to-head from binary sentiment (SST-2: substrate 0.767 >= calibrated-LLM
  0.748) to 4-class topic classification. Same principled fix: naive zero-shot label log-prob has surface-form bias (model prior
  over the 4 topic words dominates); contextual calibration / PMI (Zhao 2021, Holtzman 2021) subtracts the content-free prior.
  Substrate = averaged-perceptron bag-of-words/bigram (discriminative weighting). AG-News (bundled, World/Sports/Business/Sci-Tech).
  import torch first (PROT-020).
SANITY GATE (honest): if the CALIBRATED LLM is still implausibly low (<0.50 on 4-class AG-News; chance=0.25, real 0.5B is ~0.7+),
  the eval is unreliable -> verdict UNKNOWN, NO substrate-vs-LLM claim.
PRE-REGISTERED: gate first. If llm_cal>=0.50: HARD_PASS substrate>=llm_cal | MIDDLE within 0.05 | HARD_FAIL substrate<llm_cal-0.05.
  Report substrate, llm_raw (diagnostic), llm_cal (calibrated) + latency. UNKNOWN if gate fails or setup fails.
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
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "textclass_headtohead_calibrated_gpu_v1"))


def _feats(txt):
    ws = re.findall(r"[a-z]+", txt.lower()); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs


def main():
    print("[config] textclass head-to-head (CALIBRATED 4-class)", flush=True)
    data = json.load(open(REPO / "experiments" / "data" / "ag_news.json", encoding="utf-8"))
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
        full = prompt + cont; ids = tok(full, return_tensors="pt").input_ids.to(DEV)
        pn = tok(prompt, return_tensors="pt").input_ids.shape[1]
        with torch.no_grad(): lp = torch.log_softmax(mdl(ids).logits[0], -1)
        s = 0.0
        for k in range(pn, ids.shape[1]): s += lp[k - 1, ids[0, k]].item()
        return s

    def mk_prompt(txt): return "Article: " + txt[:400] + "\nThe topic is"
    CF_PROMPTS = [mk_prompt(""), mk_prompt("N/A"), mk_prompt("nothing")]
    cf = [sum(logp_total(p, " " + LABELS[k]) for p in CF_PROMPTS) / len(CF_PROMPTS) for k in range(len(LABELS))]
    print("  content-free label logprob (prior): %s" % ["%.3f" % x for x in cf], flush=True)
    t_l = time.time(); raw_cor = 0; cal_cor = 0
    for e in test:
        prompt = mk_prompt(e["text"])
        lps = [logp_total(prompt, " " + LABELS[k]) for k in range(len(LABELS))]
        if max(range(len(LABELS)), key=lambda k: lps[k]) == e["label"]: raw_cor += 1
        if max(range(len(LABELS)), key=lambda k: lps[k] - cf[k]) == e["label"]: cal_cor += 1
    llm_raw = raw_cor / len(test); llm_cal = cal_cor / len(test); llm_lat = (time.time() - t_l) / len(test)
    print("  LLM: raw(naive)=%.3f  calibrated(PMI)=%.3f  (%.3fs/item)" % (llm_raw, llm_cal, llm_lat), flush=True)
    # --- verdict with sanity gate ---
    if llm_cal < 0.50:
        verdict = "UNKNOWN"
        msg = ("UNKNOWN: LLM baseline implausible after calibration (cal=%.3f < 0.50 on 4-class AG-News; chance=0.25, real "
               "Qwen-0.5B ~0.7+). Eval unreliable -- NO substrate-vs-LLM claim. substrate=%.3f, raw=%.3f, cal=%.3f.") % (
               llm_cal, sub_acc, llm_raw, llm_cal)
    else:
        win = sub_acc >= llm_cal
        verdict = "HARD_PASS" if win else ("MIDDLE_BAND" if sub_acc >= llm_cal - 0.05 else "HARD_FAIL")
        msg = ("%s: substrate topic=%.3f (%.6fs) vs Qwen-0.5B CALIBRATED=%.3f (%.3fs) -- %s. 4-class AG-News; calibration "
               "(naive=%.3f -> cal=%.3f). Substrate tiny+fast, deterministic.") % (
               verdict, sub_acc, sub_lat, llm_cal, llm_lat, "SUB>=LLM" if win else "LLM>", llm_raw, llm_cal)
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "textclass_headtohead_calibrated_gpu_v1", "verdict": verdict, "verdict_msg": msg,
               "summary": msg, "elapsed_s": time.time() - t_s,
               "substrate_acc": round(sub_acc, 3), "llm_acc_raw": round(llm_raw, 3), "llm_acc_calibrated": round(llm_cal, 3),
               "sub_latency": sub_lat, "llm_latency": llm_lat}, open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert "BIAS" in _feats("hi there"); print("[selftest] PASS: textclass-headtohead-calibrated", flush=True); sys.exit(0)
main()
