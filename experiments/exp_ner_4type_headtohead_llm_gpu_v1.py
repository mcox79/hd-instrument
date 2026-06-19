"""
exp_ner_4type_headtohead_llm_gpu_v1.py -- NER head-to-head: substrate vs Qwen LLM ladder -- GPU. v3.

v3 (research_PREREG_ner_4type_v3_QWEN7B_DROPPED_PROMPT_FAIRNESS_PRECISE + Skunkworks v3 SCHEMA-VET +
quick-confirm GO, 2026-06-19). Two discriminating regimes; Qwen-7B DROPPED (separate follow-up when cached):
  (1) PROMPT-FAIRNESS (the cert-CRUX): the suspicious Qwen-1.5B F1<0.5B is likely a crippled prompt.
      Each LLM is run with TWO prompt styles (A line-format + B extraction-format); take the BEST F1 per
      model. HARD_PASS requires substrate beats the BEST-prompted 1.5B (never a crippled baseline).
  (2) FINE-GRAINED: OntoNotes 18-type (PERSON..LANGUAGE) alongside CoNLL-coarse 4-type; substrate's
      structured-perceptron may struggle on 18-type -> built-in discriminating regime.
  n_seeds=5 (substrate; LLM greedy-decode is deterministic so scored once per (model,prompt,benchmark)).

OntoNotes 18-type id->name VERIFIED from the data (most-common token per type_id):
  0 PERSON 1 NORP 2 FAC 3 ORG 4 GPE 5 LOC 6 PRODUCT 7 DATE 8 TIME 9 PERCENT 10 MONEY 11 QUANTITY
  12 ORDINAL 13 CARDINAL 14 EVENT 15 WORK_OF_ART 16 LAW 17 LANGUAGE.

PRE-REGISTERED BANDS v3 (honest-scope; substrate vs BEST-prompted LLM):
  HARD_PASS  4-type: margin >= +0.30 vs Qwen-0.5B AND vs BEST-prompted-Qwen-1.5B AND substrate F1 >= 0.65
             AND 18-type substrate F1 >= 0.45 AND substrate seeds reproduce within +-0.03 F1.
  MIDDLE     margin >= +0.10 vs both AND substrate F1 >= 0.50 (wins 4-type; weaker on 18-type).
  HARD_FAIL  margin < +0.10 vs 0.5B OR substrate F1 < 0.50 OR seeds disagree > 0.05 F1
             OR substrate loses to the BEST-prompted-1.5B (the original 1.5B-win was a prompt artifact).
  Honest-scope: "substrate NER 4-type beats Qwen-0.5B AND best-prompted-Qwen-1.5B at OntoNotes->CoNLL-coarse
  + handles OntoNotes-18type (F1>=X); NOT a general beats-all-LLM; Qwen-7B = separate follow-up when cached."
ROBUST EVAL: predicted entity text matched to a token run; hallucinated (unmatched) preds = FP (honest
  penalty) + tracked. Per (model,prompt): unmatch-rate > 0.40 -> that prompt-variant UNKNOWN. import torch
  first (PROT-020). ASCII-only. Bundled OntoNotes.
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
SMOKE = "--smoke" in sys.argv
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "ner_4type_headtohead_llm_gpu_v1"))
MODELS = [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B"), ("Qwen/Qwen2.5-1.5B-Instruct", "1.5B")]
if SMOKE:
    MODELS = [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B")]
SEEDS = [7, 17, 23, 31, 41] if not SMOKE else [7, 17]

# ---- 4-type (CoNLL-coarse) ----
COARSE = {0: 0, 3: 1, 4: 2, 5: 2, 2: 2, 1: 3, 6: 3, 14: 3, 15: 3, 16: 3, 17: 3}
C4_NAME = ["PER", "ORG", "LOC", "MISC"]
C4_DEF = ("PER (person), ORG (organization/company/institution), LOC (location/country/city), "
          "MISC (other proper nouns: nationalities, products, events, works of art, laws, languages)")
NAME2C4 = {"PER": 0, "ORG": 1, "LOC": 2, "MISC": 3, "PERSON": 0, "ORGANIZATION": 1, "LOCATION": 2, "GPE": 2}
# ---- 18-type (OntoNotes fine-grained; id order VERIFIED from data) ----
ONTO18 = ["PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", "DATE", "TIME", "PERCENT", "MONEY",
          "QUANTITY", "ORDINAL", "CARDINAL", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"]
O18_DEF = ("PERSON, NORP (nationality/religious/political group), FAC (facility), ORG (organization), "
           "GPE (country/city/state), LOC (non-GPE location), PRODUCT, DATE, TIME, PERCENT, MONEY, "
           "QUANTITY, ORDINAL, CARDINAL, EVENT, WORK_OF_ART, LAW, LANGUAGE")
NAME2O18 = {n: i for i, n in enumerate(ONTO18)}
NAME2O18.update({"ORGANIZATION": 3, "LOCATION": 5, "PER": 0})


def _collapse4(tags):
    out = []
    for t in tags:
        if t == 0: out.append(0); continue
        tid = (t - 1) // 2; is_B = (t % 2 == 1)
        cz = COARSE.get(tid)
        out.append(0 if cz is None else ((1 + 2 * cz) if is_B else (2 + 2 * cz)))
    return out


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _emit_feats(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    return fs


def _spans(tags):
    sp = set(); i = 0; n = len(tags)
    while i < n:
        t = tags[i]
        if t > 0 and t % 2 == 1:
            j = i + 1
            while j < n and tags[j] == t + 1: j += 1
            sp.add((i, j, (t - 1) // 2)); i = j
        else: i += 1
    return sp


def train_substrate(train, TAGS, seed):
    T = len(TAGS); rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(pt, t): return "tt_%d~%d" % (pt, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt(-1, TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    EP = 6 if not SMOKE else 2
    for ep in range(EP):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = viterbi(words, w)
            if pred != gold:
                pg = -1; pp = -1
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit_feats(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _emit_feats(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    return lambda words: viterbi(words, avg)


def _f1_from_spans(gold_sets, pred_sets, extra_fp=0):
    tp = fp = fn = 0
    for gs, ps in zip(gold_sets, pred_sets):
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    fp += extra_fp
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9)
    return 2 * prec * rec / (prec + rec + 1e-9)


# ---------- LLM few-shot NER: TWO prompt styles for the fairness gate ----------
def _fewshot_A(type_def):
    return ("Sentence: Barack Obama visited Google in California .\nEntities:\nPER: Barack Obama\nORG: Google\nLOC: California\n\n"
            "Sentence: The French team won the World Cup .\nEntities:\nMISC: French\nMISC: World Cup\n\n"
            "Sentence: Microsoft released Windows in Seattle .\nEntities:\nORG: Microsoft\nMISC: Windows\nLOC: Seattle\n\n"
            "Sentence: She moved to Paris last year .\nEntities:\nLOC: Paris\n\n"
            "Sentence: Einstein taught at Princeton University .\nEntities:\nPER: Einstein\nORG: Princeton University\n\n")


def _sys_A(type_def):
    return ("You are a named-entity recognizer. Entity types: " + type_def + ". "
            "List each entity on its own line as 'TYPE: exact text from the sentence'. If there are no entities, "
            "output exactly 'NONE'. Output ONLY the entity lines, nothing else.")


def _fewshot_B(type_def):
    return ("Example 1\nText: Barack Obama visited Google in California .\nNamed entities:\nBarack Obama | PER\nGoogle | ORG\nCalifornia | LOC\n\n"
            "Example 2\nText: Microsoft released Windows in Seattle .\nNamed entities:\nMicrosoft | ORG\nWindows | MISC\nSeattle | LOC\n\n"
            "Example 3\nText: Einstein taught at Princeton University .\nNamed entities:\nEinstein | PER\nPrinceton University | ORG\n\n")


def _sys_B(type_def):
    return ("Task: extract every named entity from the text and classify it. Allowed types: " + type_def + ". "
            "Write one entity per line in the exact format 'entity text | TYPE'. Copy the entity text verbatim from "
            "the input. If the text has no named entities, write 'NONE'. Do not add any commentary.")


PROMPTS = {"A": (_sys_A, _fewshot_A, "Sentence: %s\nEntities:"),
           "B": (_sys_B, _fewshot_B, "Text: %s\nNamed entities:")}


def _parse_lines(out, name2id, tlc):
    """Parse 'TYPE: text' OR 'text | TYPE' lines -> (pred_span_set, n_pred, n_unmatched)."""
    ps = set(); n_pred = 0; n_unmatch = 0
    for line in out.splitlines():
        ln = line.strip()
        if not ln or ln.upper() == "NONE":
            continue
        ty = None; txt = None
        if "|" in ln:                                   # style B: text | TYPE
            a, b = ln.rsplit("|", 1); ty = b.strip().upper(); txt = a.strip()
        else:
            m = re.match(r"\s*([A-Za-z_]+)\s*:\s*(.+?)\s*$", ln)   # style A: TYPE: text
            if m: ty = m.group(1).upper(); txt = m.group(2).strip()
        if ty is None or ty not in name2id or not txt:
            continue
        n_pred += 1
        sub = txt.lower().split()
        sp = None
        if sub:
            for i in range(0, len(tlc) - len(sub) + 1):
                if tlc[i:i + len(sub)] == sub: sp = (i, i + len(sub)); break
        if sp is None: n_unmatch += 1
        else: ps.add((sp[0], sp[1], name2id[ty]))
    return ps, n_pred, n_unmatch


def eval_llm_prompt(model, tok, dev, label, prompt_key, type_def, name2id, test_tokens):
    sysf, fewf, userfmt = PROMPTS[prompt_key]
    sys_p = sysf(type_def); few = fewf(type_def)
    pred_sets = []; unmatched = 0; pred_total = 0; t0 = time.time()
    for tokens in test_tokens:
        tlc = [w.lower() for w in tokens]
        user = few + (userfmt % " ".join(tokens))
        msgs = [{"role": "system", "content": sys_p}, {"role": "user", "content": user}]
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        ins = tok(p, return_tensors="pt").to(dev)
        with torch.no_grad():
            o = model.generate(**ins, max_new_tokens=len(tokens) * 4 + 24, do_sample=False, pad_token_id=tok.eos_token_id)
        out = tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        ps, npred, nun = _parse_lines(out, name2id, tlc)
        pred_sets.append(ps); pred_total += npred; unmatched += nun
    lat = (time.time() - t0) / max(1, len(test_tokens))
    unmatch_rate = unmatched / max(pred_total, 1)
    return {"prompt": prompt_key, "pred_sets": pred_sets, "unmatch_rate": round(unmatch_rate, 3),
            "pred_total": pred_total, "latency": round(lat, 4), "unknown": unmatch_rate > 0.40}


def eval_llm_best(model_id, label, type_def, name2id, test_tokens, gold_sets):
    """Prompt-fairness: run BOTH prompt styles, return the BEST-prompted F1 (never the crippled one)."""
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16 if dev == "cuda" else torch.float32).to(dev); mdl.eval()
    print("[model] loaded %s on %s" % (model_id, dev), flush=True)
    variants = []
    for pk in PROMPTS:
        r = eval_llm_prompt(mdl, tok, dev, label, pk, type_def, name2id, test_tokens)
        r["f1"] = round(_f1_from_spans(gold_sets, r["pred_sets"], extra_fp=int(r["unmatch_rate"] * r["pred_total"])), 4)
        r.pop("pred_sets")
        print("    %s prompt=%s F1=%.4f unmatch=%.3f%s" % (label, pk, r["f1"], r["unmatch_rate"], " (UNK)" if r["unknown"] else ""), flush=True)
        variants.append(r)
    del mdl
    if dev == "cuda": torch.cuda.empty_cache()
    valid = [v for v in variants if not v["unknown"]]
    best = max(valid, key=lambda v: v["f1"]) if valid else max(variants, key=lambda v: v["f1"])
    return {"label": label, "model": model_id, "best_f1": best["f1"], "best_prompt": best["prompt"],
            "all_unknown": not valid, "variants": variants}


def run_benchmark(name, train, test, TAGS, type_def, name2id):
    """One benchmark (4-type or 18-type): substrate (n_seeds) vs LLMs (best-prompted)."""
    test_tokens = [t for t, _g in test]
    gold_sets = [_spans(g) for _t, g in test]
    sub_f1s = []
    for seed in SEEDS:
        tagger = train_substrate(train, TAGS, seed)
        f1 = _f1_from_spans(gold_sets, [_spans(tagger(t)) for t in test_tokens])
        sub_f1s.append(f1)
        print("  [%s substrate seed=%d] span-F1=%.4f" % (name, seed, f1), flush=True)
    sub_mean = float(np.mean(sub_f1s)); sub_std = float(np.std(sub_f1s))
    llm = [eval_llm_best(mid, lbl, type_def, name2id, test_tokens, gold_sets) for mid, lbl in MODELS]
    return {"benchmark": name, "substrate_f1_mean": round(sub_mean, 4), "substrate_f1_std": round(sub_std, 4),
            "substrate_f1_seeds": [round(x, 4) for x in sub_f1s], "n_test": len(test), "llm": llm}


def compute_verdict(bench4, bench18):
    s4 = bench4["substrate_f1_mean"]; s4_std = bench4["substrate_f1_std"]
    s18 = bench18["substrate_f1_mean"]

    def best(b, lbl):
        r = next((x for x in b["llm"] if x["label"] == lbl), None)
        return r["best_f1"] if r and not r["all_unknown"] else None

    f05 = best(bench4, "0.5B"); f15 = best(bench4, "1.5B")
    detail = {"substrate_4type": s4, "substrate_4type_std": s4_std, "substrate_18type": s18,
              "best_05B_4type": f05, "best_15B_4type": f15,
              "margin_vs_05B": (round(s4 - f05, 4) if f05 is not None else None),
              "margin_vs_best15B": (round(s4 - f15, 4) if f15 is not None else None),
              "seeds_reproduce": s4_std <= 0.03}
    if f05 is None:
        return ("UNKNOWN", "UNKNOWN: 0.5B all prompt-variants unmatch>0.40. " + json.dumps(detail), detail)
    m05 = s4 - f05; m15 = (s4 - f15) if f15 is not None else 1.0
    scope = ("substrate NER 4-type=%.4f (+-%.4f) vs BEST-prompted Qwen-0.5B=%.4f (m %+.4f) / 1.5B=%s (m %s); "
             "18-type substrate=%.4f. Honest-scope: beats best-prompted 0.5B+1.5B at OntoNotes->CoNLL-coarse; "
             "18-type handled at F1=%.4f; NOT beats-all-LLM; Qwen-7B separate follow-up." % (
             s4, s4_std, f05, m05, ("%.4f" % f15 if f15 is not None else "NA"),
             ("%+.4f" % m15 if f15 is not None else "NA"), s18, s18))
    if m05 < 0.10 or s4 < 0.50 or s4_std > 0.05 or (f15 is not None and m15 < 0):
        v = "HARD_FAIL"
    elif m05 >= 0.30 and m15 >= 0.30 and s4 >= 0.65 and s18 >= 0.45 and s4_std <= 0.03:
        v = "HARD_PASS"
    else:
        v = "MIDDLE_BAND"
    return (v, v + ": " + scope, detail)


def main():
    print("[config] NER v3: substrate(%d seeds) vs Qwen %s; 2-prompt fairness; 4-type + 18-type" % (
        len(SEEDS), [m[1] for m in MODELS]), flush=True)
    data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    raw_train = [(t, g) for t, g in data["train"] if t and len(t) <= 60]
    raw_test = [(t, g) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: raw_train = raw_train[:200]
    n_test = 6 if SMOKE else 150
    raw_test = raw_test[:n_test]
    t0 = time.time()
    tr4 = [(t, _collapse4(g)) for t, g in raw_train]; te4 = [(t, _collapse4(g)) for t, g in raw_test]
    TAGS4 = sorted({tg for _w, g in tr4 for tg in g})
    bench4 = run_benchmark("4type", tr4, te4, TAGS4, C4_DEF, NAME2C4)
    TAGS18 = sorted({tg for _w, g in raw_train for tg in g})
    bench18 = run_benchmark("18type", raw_train, raw_test, TAGS18, O18_DEF, NAME2O18)
    verdict, msg, detail = compute_verdict(bench4, bench18)
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "ner_4type_headtohead_llm_gpu_v1", "verdict": verdict, "verdict_msg": msg,
               "summary": msg[:200], "elapsed_s": time.time() - t0, "detail": detail,
               "metrics_source": "measured_gpu_substrate_vs_qwen_ladder_promptfair_4type_18type",
               "bench_4type": bench4, "bench_18type": bench18, "n_seeds": len(SEEDS), "shots": 5},
              open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert _collapse4([1, 2, 0, 15, 7, 8]) == [1, 2, 0, 0, 3, 4]
    assert _spans([1, 2, 0]) == {(0, 2, 0)}
    assert ONTO18[0] == "PERSON" and ONTO18[7] == "DATE" and ONTO18[17] == "LANGUAGE"
    ps, npred, nun = _parse_lines("PER: Barack Obama\nORG: Google", NAME2C4, ["barack", "obama", "ran", "google"])
    assert (0, 2, 0) in ps and (3, 4, 1) in ps, ps
    ps2, _, _ = _parse_lines("Barack Obama | PER", NAME2C4, ["barack", "obama"])
    assert (0, 2, 0) in ps2, ps2
    _ps3, _, n3 = _parse_lines("LOC: Atlantis", NAME2C4, ["barack", "obama"])
    assert n3 == 1, "hallucinated (unmatched) prediction must be counted"
    assert len(PROMPTS) == 2
    print("[selftest] PASS: ner v3 (collapse4, spans, 18-type-map, dual-format parse, hallucination-count)", flush=True)
    sys.exit(0)
main()
