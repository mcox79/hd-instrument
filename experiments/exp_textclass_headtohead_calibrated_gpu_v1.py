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


def _train_eval_substrate(train, test, LAB, seed):
    """averaged-perceptron bag-of-words/bigram; returns (acc, per_ex_s, per_class_correct, per_class_total)."""
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
    scor = 0; pc_cor = defaultdict(int); pc_tot = defaultdict(int); t_ev = time.time()
    for e in test:
        feats = _feats(e["text"]); sc = {l: sum(avg[l].get(f, 0.0) for f in feats) for l in LAB}
        pred = max(LAB, key=lambda l: (sc[l], l)); pc_tot[e["label"]] += 1
        if pred == e["label"]: scor += 1; pc_cor[e["label"]] += 1
    return scor / len(test), (time.time() - t_ev) / max(1, len(test)), dict(pc_cor), dict(pc_tot)


def main():
    print("[config] textclass head-to-head (CALIBRATED 4-class) MULTI-SEED", flush=True)
    data = json.load(open(REPO / "experiments" / "data" / "ag_news.json", encoding="utf-8"))
    LABELS = data["labels"]; train = data["train"]; test = data["test"][: (12 if SMOKE else 400)]
    if SMOKE: train = train[:500]
    LAB = list(range(len(LABELS)))
    SEEDS = [0, 1, 2] if SMOKE else [0, 1, 2, 3, 4]
    t_s = time.time()
    res = [_train_eval_substrate(train, test, LAB, sd) for sd in SEEDS]
    vals = [round(a, 4) for a, _, _, _ in res]; sub_per_ex = sum(t for _, t, _, _ in res) / len(res)
    mean = sum(vals) / len(vals); std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
    seed_spread = max(vals) - min(vals)
    pc_cor, pc_tot = res[0][2], res[0][3]  # per-class on seed-0 (reported)
    sub_per_class = {LABELS[k]: round(pc_cor.get(k, 0) / max(1, pc_tot.get(k, 0)), 3) for k in LAB}
    print("  substrate n=%d: mean=%.4f std=%.4f spread=%.4f vals=%s | sub_per_ex=%.2eus per_class=%s" % (
        len(vals), mean, std, seed_spread, vals, sub_per_ex * 1e6, sub_per_class), flush=True)
    # --- LLM (deterministic; once) ---
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
    t_l = time.time(); raw_cor = 0; cal_cor = 0; llm_pc_cor = defaultdict(int)
    for e in test:
        prompt = mk_prompt(e["text"])
        lps = [logp_total(prompt, " " + LABELS[k]) for k in range(len(LABELS))]
        if max(range(len(LABELS)), key=lambda k: lps[k]) == e["label"]: raw_cor += 1
        cal_pred = max(range(len(LABELS)), key=lambda k: lps[k] - cf[k])
        if cal_pred == e["label"]: cal_cor += 1; llm_pc_cor[e["label"]] += 1
    llm_raw = raw_cor / len(test); llm_cal = cal_cor / len(test)
    llm_per_ex = (time.time() - t_l) / max(1, len(test)); speed_up = llm_per_ex / max(1e-12, sub_per_ex)
    llm_per_class = {LABELS[k]: round(llm_pc_cor.get(k, 0) / max(1, pc_tot.get(k, 0)), 3) for k in LAB}
    print("  LLM: raw(naive)=%.3f  calibrated(PMI)=%.3f | llm_per_ex=%.2fms speed_up=%.0fx per_class=%s" % (
        llm_raw, llm_cal, llm_per_ex * 1e3, speed_up, llm_per_class), flush=True)
    # --- verdict (v2 pre-reg: 3-condition HARD_PASS w/ +0.05 margin, +-0.03 repro, 100x speed) ---
    c_margin = mean >= llm_cal + 0.05; c_speed = speed_up >= 100.0; c_repro = seed_spread <= 0.05
    tail = ("substrate mean=%.4f std=%.4f spread=%.4f vs CALIBRATED-Qwen2.5-0.5B=%.3f (raw=%.3f) | speed_up=%.0fx | "
            "vals=%s | per_class sub=%s llm=%s | conds[margin=%s speed=%s repro=%s]" % (
            mean, std, seed_spread, llm_cal, llm_raw, speed_up, vals, sub_per_class, llm_per_class, c_margin, c_speed, c_repro))
    if llm_cal < 0.50:
        verdict = "UNKNOWN"; msg = ("UNKNOWN: calibrated LLM %.3f < 0.50 on 4-class AG-News (chance=0.25); eval unreliable. " % llm_cal) + tail
    elif mean < llm_cal or seed_spread > 0.05:
        verdict = "HARD_FAIL"; msg = ("HARD_FAIL: substrate does NOT beat the best-prompted (calibrated) LLM OR seeds disagree >0.05. " + tail)
    elif c_margin and c_speed and c_repro:
        verdict = "HARD_PASS"; msg = ("HARD_PASS: substrate beats BEST-PROMPTED (PMI-calibrated) Qwen2.5-0.5B on AG-News 4-class topic "
            "with >=+0.05 margin + >=100x speed-up + seed-reproduce. " + tail)
    else:
        verdict = "MIDDLE_BAND"; msg = ("MIDDLE_BAND: substrate matches/edges calibrated-LLM but margin <+0.05 (not all cert conds). " + tail)
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "textclass_headtohead_calibrated_gpu_v1", "verdict": verdict, "verdict_msg": msg,
               "summary": msg, "elapsed_s": time.time() - t_s, "run_mode": ("smoke" if SMOKE else "full"),
               "metrics_source": "measured_gpu_textclass_headtohead_calibrated_agnews", "n_seeds": len(SEEDS),
               "substrate_mean": round(mean, 4), "substrate_std": round(std, 4), "substrate_seed_spread": round(seed_spread, 4),
               "substrate_vals": vals, "llm_acc_calibrated": round(llm_cal, 3), "llm_acc_raw": round(llm_raw, 3),
               "substrate_per_ex_s": sub_per_ex, "llm_per_ex_s": llm_per_ex, "speed_up_factor": round(speed_up, 1),
               "substrate_per_class": sub_per_class, "llm_per_class": llm_per_class,
               "conds": {"margin": c_margin, "speed": c_speed, "repro": c_repro}},
              open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert "BIAS" in _feats("hi there"); print("[selftest] PASS: textclass-headtohead-calibrated", flush=True); sys.exit(0)
main()
