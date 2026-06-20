"""
exp_sentiment_headtohead_calibrated_multiseed_gpu_v1.py -- firm the narrow SST-2 calibrated edge -- GPU.

ROUTING: the calibrated SST-2 head-to-head was substrate 0.767 vs calibrated-LLM 0.748 -- a NARROW 0.019 edge on a single
  substrate seed. Honesty check: is the edge real or within substrate seed-noise? Run the substrate perceptron over 5 seeds
  (mean +/- std); the calibrated LLM is deterministic (greedy logprob) so compute it ONCE. Decide robust-win vs match honestly.
  Substrate = averaged-perceptron bag-of-words. Qwen2.5-0.5B calibrated (PMI). SST-2 (bundled). import torch first (PROT-020).
PRE-REGISTERED: compute llm_cal once + substrate over 5 seeds. ROBUST_WIN (HARD_PASS) if substrate (mean - std) >= llm_cal.
  MATCH (MIDDLE_BAND) if mean >= llm_cal but mean-std < llm_cal (edge within noise). HARD_FAIL if mean < llm_cal - 0.02.
  Sanity gate: llm_cal < 0.65 -> UNKNOWN. Reports substrate mean/std/vals, llm_cal, llm_raw.
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
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "sentiment_headtohead_calibrated_multiseed_gpu_v1"))


def _feats(txt):
    ws = re.findall(r"[a-z]+", txt.lower()); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs


def _train_eval_substrate(train, test, LAB, seed):
    import random; rng = random.Random(seed)
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
    scor = 0; t_ev = time.time()
    for e in test:
        feats = _feats(e["text"]); sc = {l: sum(avg[l].get(f, 0.0) for f in feats) for l in LAB}
        if max(LAB, key=lambda l: (sc[l], l)) == e["label"]: scor += 1
    sub_per_ex = (time.time() - t_ev) / max(1, len(test))
    return scor / len(test), sub_per_ex


def main():
    print("[config] sentiment calibrated MULTI-SEED", flush=True)
    data = json.load(open(REPO / "experiments" / "data" / "sst2.json", encoding="utf-8"))
    LABELS = data["labels"]; train = data["train"]; test = data["test"][: (12 if SMOKE else 400)]
    if SMOKE: train = train[:500]
    LAB = list(range(len(LABELS)))
    SEEDS = [0, 1, 2] if SMOKE else [0, 1, 2, 3, 4]
    t_s = time.time()
    res = [_train_eval_substrate(train, test, LAB, sd) for sd in SEEDS]
    vals = [round(a, 4) for a, _ in res]; sub_per_ex = sum(t for _, t in res) / len(res)
    mean = sum(vals) / len(vals); std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
    seed_spread = max(vals) - min(vals)
    print("  substrate n=%d: mean=%.4f std=%.4f spread=%.4f vals=%s | sub_per_ex=%.2eus" % (
        len(vals), mean, std, seed_spread, vals, sub_per_ex * 1e6), flush=True)
    # --- calibrated LLM (deterministic, once) ---
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

    def mk_prompt(txt): return "Review: " + txt[:300] + "\nThe sentiment is"
    CF = [mk_prompt(""), mk_prompt("N/A"), mk_prompt("nothing")]
    cf = [sum(logp_total(p, " " + LABELS[k]) for p in CF) / len(CF) for k in range(len(LABELS))]
    raw_cor = cal_cor = 0; t_llm = time.time()
    for e in test:
        prompt = mk_prompt(e["text"]); lps = [logp_total(prompt, " " + LABELS[k]) for k in range(len(LABELS))]
        if max(range(len(LABELS)), key=lambda k: lps[k]) == e["label"]: raw_cor += 1
        if max(range(len(LABELS)), key=lambda k: lps[k] - cf[k]) == e["label"]: cal_cor += 1
    llm_per_ex = (time.time() - t_llm) / max(1, len(test))
    llm_raw = raw_cor / len(test); llm_cal = cal_cor / len(test)
    speed_up = llm_per_ex / max(1e-12, sub_per_ex)
    print("  LLM: raw=%.3f calibrated=%.3f | llm_per_ex=%.2fms speed_up=%.0fx" % (
        llm_raw, llm_cal, llm_per_ex * 1e3, speed_up), flush=True)
    # --- verdict (v2 pre-reg: 4-condition HARD_PASS w/ prompt-fairness calibrated baseline + speed + seed-reproduce) ---
    c_margin = mean >= llm_cal + 0.01            # cond1: beats best-prompted (calibrated) LLM with margin
    c_robust = mean - std >= llm_cal             # cond2: seed-robust margin (mean-std over the fair baseline)
    c_speed = speed_up >= 100.0                   # cond3: latency-dimensionality WIN (reported + gated)
    c_repro = seed_spread <= 0.04                 # cond4: all seeds reproduce within +-0.02 of mean (spread<=0.04)
    tail = ("substrate mean=%.4f std=%.4f spread=%.4f vs CALIBRATED-LLM=%.3f (fair baseline; raw=%.3f) | speed_up=%.0fx | "
            "vals=%s | conds[margin=%s robust=%s speed=%s repro=%s]" % (
            mean, std, seed_spread, llm_cal, llm_raw, speed_up, vals, c_margin, c_robust, c_speed, c_repro))
    if llm_cal < 0.65:
        verdict = "UNKNOWN"; msg = "UNKNOWN: calibrated LLM %.3f < 0.65, eval unreliable. " % llm_cal + tail
    elif mean < llm_cal or seed_spread > 0.04:
        verdict = "HARD_FAIL"; msg = ("HARD_FAIL: substrate does NOT robustly beat the best-prompted (calibrated) LLM "
            "(win was prompt-artifact) OR seeds disagree >0.04. " + tail)
    elif c_margin and c_robust and c_speed and c_repro:
        verdict = "HARD_PASS"; msg = ("HARD_PASS: substrate beats BEST-PROMPTED (PMI-calibrated, multi-seed-robust) Qwen2.5-0.5B "
            "on SST-2 with margin + >=100x speed-up + seed-robust. " + tail)
    else:
        verdict = "MIDDLE_BAND"; msg = ("MIDDLE_BAND: substrate matches/edges calibrated-LLM but not all 4 cert conds met "
            "(edge within seed-noise or sub-margin). " + tail)
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "sentiment_headtohead_calibrated_multiseed_gpu_v1", "verdict": verdict, "verdict_msg": msg,
               "summary": msg, "elapsed_s": time.time() - t_s, "run_mode": ("smoke" if SMOKE else "full"),
               "metrics_source": "measured_gpu_sentiment_headtohead_calibrated_multiseed_sst2", "n_seeds": len(SEEDS),
               "substrate_mean": round(mean, 4), "substrate_std": round(std, 4), "substrate_seed_spread": round(seed_spread, 4),
               "substrate_vals": vals, "llm_acc_calibrated": round(llm_cal, 3), "llm_acc_raw": round(llm_raw, 3),
               "substrate_per_ex_s": sub_per_ex, "llm_per_ex_s": llm_per_ex, "speed_up_factor": round(speed_up, 1),
               "conds": {"margin": c_margin, "robust": c_robust, "speed": c_speed, "repro": c_repro}},
              open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert "BIAS" in _feats("hi there"); print("[selftest] PASS: sentiment-calibrated-multiseed", flush=True); sys.exit(0)
main()
