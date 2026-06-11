"""
exp_classification_headtohead_1p5b_calibrated_gpu_v1.py -- calibrated classification head-to-head vs Qwen-3B (scale test, completes 0.5B/1.5B/3B ladder) -- GPU.

ROUTING: the calibrated classification head-to-head beat Qwen-0.5B (SST-2 0.7765 robust-win; AG-News 0.848 decisive). The MATH
  north-star was SCALE-INVARIANT (substrate beat 0.5B/1.5B/3B). Does the CLASSIFICATION win also hold vs a 3x-larger LLM, or does
  it only beat the smallest? Re-run the SAME calibrated (PMI/contextual) protocol vs Qwen2.5-3B-Instruct on BOTH SST-2 (binary)
  and AG-News (4-class). Substrate = averaged-perceptron bag-of-words (the trained classifier). import torch first (PROT-020).
SANITY GATE: per-task, if calibrated-LLM is implausible (SST-2 <0.65 / AG-News <0.50) -> that task = UNKNOWN, no claim for it.
PRE-REGISTERED per task: HARD_PASS substrate>=cal-LLM | MIDDLE within 0.05 | HARD_FAIL substrate<cal-LLM-0.05. Overall verdict =
  worst-case across the two tasks that have a trustworthy baseline. Reports both tasks' substrate/raw/calibrated + latency.
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
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "classification_headtohead_3b_calibrated_gpu_v1"))
MODEL = "Qwen/Qwen2.5-3B-Instruct"
TASKS = [
    ("sst2", "sst2.json", lambda t: "Review: " + t[:300] + "\nThe sentiment is", 0.65),
    ("agnews", "ag_news.json", lambda t: "Article: " + t[:400] + "\nThe topic is", 0.50),
]


def _feats(txt):
    ws = re.findall(r"[a-z]+", txt.lower()); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs


def _substrate(train, test, LAB):
    import random; rng = random.Random(0)
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
    t0 = time.time(); scor = 0
    for e in test:
        feats = _feats(e["text"]); sc = {l: sum(avg[l].get(f, 0.0) for f in feats) for l in LAB}
        if max(LAB, key=lambda l: (sc[l], l)) == e["label"]: scor += 1
    return scor / len(test), (time.time() - t0) / len(test)


def main():
    print("[config] classification head-to-head vs Qwen-1.5B (CALIBRATED)", flush=True)
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(MODEL)
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded", MODEL, "on", DEV, flush=True)

    def logp_total(prompt, cont):
        full = prompt + cont; ids = tok(full, return_tensors="pt").input_ids.to(DEV)
        pn = tok(prompt, return_tensors="pt").input_ids.shape[1]
        with torch.no_grad(): lp = torch.log_softmax(mdl(ids).logits[0], -1)
        s = 0.0
        for k in range(pn, ids.shape[1]): s += lp[k - 1, ids[0, k]].item()
        return s

    results = {}; t_total = time.time()
    for tname, fn, mk_prompt, gate in TASKS:
        data = json.load(open(REPO / "experiments" / "data" / fn, encoding="utf-8"))
        LABELS = data["labels"]; train = data["train"]; test = data["test"][: (10 if SMOKE else 300)]
        if SMOKE: train = train[:400]
        LAB = list(range(len(LABELS)))
        sub_acc, sub_lat = _substrate(train, test, LAB)
        CF = [mk_prompt(""), mk_prompt("N/A"), mk_prompt("nothing")]
        cf = [sum(logp_total(p, " " + LABELS[k]) for p in CF) / len(CF) for k in range(len(LABELS))]
        t_l = time.time(); raw_cor = cal_cor = 0
        for e in test:
            prompt = mk_prompt(e["text"]); lps = [logp_total(prompt, " " + LABELS[k]) for k in range(len(LABELS))]
            if max(range(len(LABELS)), key=lambda k: lps[k]) == e["label"]: raw_cor += 1
            if max(range(len(LABELS)), key=lambda k: lps[k] - cf[k]) == e["label"]: cal_cor += 1
        llm_raw = raw_cor / len(test); llm_cal = cal_cor / len(test); llm_lat = (time.time() - t_l) / len(test)
        trustworthy = llm_cal >= gate
        if not trustworthy:
            tv = "UNKNOWN"
        else:
            tv = "HARD_PASS" if sub_acc >= llm_cal else ("MIDDLE_BAND" if sub_acc >= llm_cal - 0.05 else "HARD_FAIL")
        results[tname] = {"substrate": round(sub_acc, 3), "llm_raw": round(llm_raw, 3), "llm_cal": round(llm_cal, 3),
                          "trustworthy": trustworthy, "task_verdict": tv, "sub_lat": sub_lat, "llm_lat": llm_lat}
        print("  [%s] substrate=%.3f vs 1.5B-cal=%.3f (raw=%.3f) -> %s%s" % (
            tname, sub_acc, llm_cal, llm_raw, tv, "" if trustworthy else " (LLM baseline implausible)"), flush=True)
    # overall verdict = worst trustworthy task
    order = {"HARD_FAIL": 0, "MIDDLE_BAND": 1, "HARD_PASS": 2}
    trust = [r["task_verdict"] for r in results.values() if r["trustworthy"]]
    if not trust:
        verdict = "UNKNOWN"
    else:
        verdict = min(trust, key=lambda v: order[v])
    parts = ["%s: sub=%.3f vs 1.5B-cal=%.3f [%s]" % (t, r["substrate"], r["llm_cal"], r["task_verdict"]) for t, r in results.items()]
    msg = "%s: classification head-to-head vs Qwen-3B (6x larger) -- %s. Scale test of the calibrated substrate-beats-0.5B result." % (verdict, " | ".join(parts))
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "classification_headtohead_3b_calibrated_gpu_v1", "verdict": verdict, "verdict_msg": msg,
               "summary": msg, "elapsed_s": time.time() - t_total, "model": MODEL, "per_task": results},
              open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert "BIAS" in _feats("hi there"); print("[selftest] PASS: classification-headtohead-3b-calibrated", flush=True); sys.exit(0)
main()
