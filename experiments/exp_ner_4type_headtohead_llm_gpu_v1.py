"""
exp_ner_4type_headtohead_llm_gpu_v1.py -- NER 4-type head-to-head: substrate vs LLM scale ladder -- GPU.

ROUTING: Research GPU AUTHORIZE (research_to_exp_dev_GPU_AUTHORIZE_3_HEADTOHEAD_PRIORITIZED_2026-06-11) Priority 2.
  Substrate NER 4-type (structured-perceptron + Viterbi, OntoNotes->CoNLL-coarse, multi-seed Tier-A 0.6502) vs LLM few-shot NER.
  LLM = Qwen2.5 Instruct 0.5B + 1.5B (3B optional HDLAB_NER_3B=1), 5-shot, literature-standard entity-extraction format
  ("TYPE: text" per line), parsed back to token spans by contiguous case-insensitive token match -> span-F1 (SAME metric as
  substrate). Both scored on the SAME 150-sentence test subset for a fair comparison. import torch first (PROT-020). Bundled OntoNotes.
ROBUST EVAL: predicted entity text matched to a token run -> (i,j,coarse). Hallucinated (unmatched) predictions counted as FP
  (honest penalty) + tracked. SANITY GATE per model: unmatch-rate > 0.40 -> that model UNKNOWN (excluded from headline). All-UNKNOWN -> UNKNOWN.
PRE-REGISTERED (vs 0.5B headline; Research): HARD-PASS substrate-win >= +0.05 / MIDDLE -0.05 to +0.05 / HARD-FAIL < -0.05.
  If HARD-FAIL: substrate-only NER 4-type honest scope; LLM advantage from pre-training (no ceiling claim, per brain-can-do-it inventory).
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
SMOKE = "--smoke" in sys.argv
OUT = REPO / "data" / ("exp_" + os.environ.get("HDLAB_EXP_NAME", "ner_4type_headtohead_llm_gpu_v1"))
MODELS = [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B"), ("Qwen/Qwen2.5-1.5B-Instruct", "1.5B")]
if os.environ.get("HDLAB_NER_3B") == "1":
    MODELS.append(("Qwen/Qwen2.5-3B-Instruct", "3B"))
if SMOKE:
    MODELS = [("Qwen/Qwen2.5-0.5B-Instruct", "0.5B")]
# coarse: 0=PER,1=ORG,2=LOC,3=MISC. OntoNotes type_id -> coarse (type_id=(tag-1)//2).
COARSE = {0: 0, 3: 1, 4: 2, 5: 2, 2: 2, 1: 3, 6: 3, 14: 3, 15: 3, 16: 3, 17: 3}
CNAME = {0: "PER", 1: "ORG", 2: "LOC", 3: "MISC"}
NAME2C = {"PER": 0, "ORG": 1, "LOC": 2, "MISC": 3, "PERSON": 0, "ORGANIZATION": 1, "LOCATION": 2}


def _collapse4(tags):
    out = []
    for t in tags:
        if t == 0: out.append(0); continue
        tid = (t - 1) // 2; is_B = (t % 2 == 1)
        cz = COARSE.get(tid)
        if cz is None: out.append(0)
        else: out.append((1 + 2 * cz) if is_B else (2 + 2 * cz))
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


def train_substrate(train, TAGS, seed=7):
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


# ---------- LLM few-shot NER ----------
FEWSHOT = ("Sentence: Barack Obama visited Google in California .\nEntities:\nPER: Barack Obama\nORG: Google\nLOC: California\n\n"
           "Sentence: The French team won the World Cup .\nEntities:\nMISC: French\nMISC: World Cup\n\n"
           "Sentence: Microsoft released Windows in Seattle .\nEntities:\nORG: Microsoft\nMISC: Windows\nLOC: Seattle\n\n"
           "Sentence: She moved to Paris last year .\nEntities:\nLOC: Paris\n\n"
           "Sentence: Einstein taught at Princeton University .\nEntities:\nPER: Einstein\nORG: Princeton University\n\n")
SYS = ("You are a named-entity recognizer. Entity types: PER (person), ORG (organization/company/institution), "
       "LOC (location/country/city), MISC (other proper nouns: nationalities, products, events, works of art, laws, languages). "
       "List each entity on its own line as 'TYPE: exact text from the sentence'. If there are no entities, output exactly 'NONE'. "
       "Output ONLY the entity lines, nothing else.")


def _match_span(tokens_lc, ent_lc):
    sub = ent_lc.split()
    if not sub: return None
    L = len(sub)
    for i in range(0, len(tokens_lc) - L + 1):
        if tokens_lc[i:i + L] == sub: return (i, i + L)
    return None


def eval_llm(model_id, label, test_tokens):
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded", model_id, "on", DEV, flush=True)
    pred_sets = []; unmatched_total = 0; pred_total = 0; t0 = time.time()
    for tokens in test_tokens:
        tlc = [w.lower() for w in tokens]
        user = FEWSHOT + "Sentence: " + " ".join(tokens) + "\nEntities:"
        msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": user}]
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True); ins = tok(p, return_tensors="pt").to(DEV)
        with torch.no_grad():
            o = mdl.generate(**ins, max_new_tokens=len(tokens) * 3 + 16, do_sample=False, pad_token_id=tok.eos_token_id)
        out = tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        ps = set()
        for line in out.splitlines():
            m = re.match(r"\s*([A-Za-z]+)\s*:\s*(.+?)\s*$", line)
            if not m: continue
            ty = m.group(1).upper(); txt = m.group(2).strip()
            if ty not in NAME2C: continue
            cz = NAME2C[ty]; pred_total += 1
            sp = _match_span(tlc, txt.lower())
            if sp is None: unmatched_total += 1
            else: ps.add((sp[0], sp[1], cz))
        pred_sets.append(ps)
    lat = (time.time() - t0) / len(test_tokens)
    unmatch_rate = unmatched_total / max(pred_total, 1)
    del mdl
    if DEV == "cuda": torch.cuda.empty_cache()
    return {"label": label, "model": model_id, "pred_sets": pred_sets, "unmatched": unmatched_total,
            "pred_total": pred_total, "unmatch_rate": round(unmatch_rate, 3), "latency": round(lat, 4),
            "unknown": unmatch_rate > 0.40}


def main():
    print("[config] NER 4-type head-to-head (substrate vs LLM ladder %s, 5-shot)" % [m[1] for m in MODELS], flush=True)
    data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    train = [(t, _collapse4(g)) for t, g in data["train"] if t and len(t) <= 60]
    test_all = [(t, _collapse4(g)) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]
    n_test = 6 if SMOKE else 150
    test = test_all[:n_test]
    TAGS = sorted({tg for _w, g in train for tg in g})
    t_tr = time.time(); tagger = train_substrate(train, TAGS); print("[substrate] trained %.1fs" % (time.time() - t_tr), flush=True)
    # substrate span-F1 on the SAME test subset
    test_tokens = [t for t, _g in test]
    gold_sets = [_spans(g) for _t, g in test]
    t_s = time.time()
    sub_pred_sets = [_spans(tagger(t)) for t in test_tokens]
    sub_lat = (time.time() - t_s) / len(test)
    sub_f1 = _f1_from_spans(gold_sets, sub_pred_sets)
    print("  substrate NER-4type: span-F1=%.4f (%.5fs/sent, %d test)" % (sub_f1, sub_lat, len(test)), flush=True)
    results = []
    for mid, lbl in MODELS:
        r = eval_llm(mid, lbl, test_tokens)
        r["f1"] = round(_f1_from_spans(gold_sets, r["pred_sets"], extra_fp=r["unmatched"]), 4)
        r.pop("pred_sets")
        print("  LLM-%s NER: span-F1=%.4f (%.4fs/sent) unmatch=%.3f (preds=%d)" % (lbl, r["f1"], r["latency"], r["unmatch_rate"], r["pred_total"]), flush=True)
        results.append(r)
    valid = [r for r in results if not r["unknown"]]
    if not valid:
        verdict = "UNKNOWN"
        msg = "UNKNOWN: all LLM models unmatch-rate>0.40 (cannot align entities). substrate=%.4f. results=%s" % (sub_f1, results)
    else:
        head = next((r for r in valid if r["label"] == "0.5B"), valid[0])
        margin = sub_f1 - head["f1"]
        verdict = "HARD_PASS" if margin >= 0.05 else ("MIDDLE_BAND" if margin >= -0.05 else "HARD_FAIL")
        ladder = " | ".join("%s F1=%.4f unmatch=%.3f%s" % (r["label"], r["f1"], r["unmatch_rate"], "(UNK)" if r["unknown"] else "") for r in results)
        tail = "" if margin >= -0.05 else " -- honest substrate-only scope; LLM advantage from pre-training (no ceiling claim; substrate-only path inventory remains open)."
        msg = ("%s: substrate NER-4type span-F1=%.4f (%.5fs/sent) vs Qwen-%s few-shot=%.4f -- margin %+.4f. Ladder: %s. "
               "OntoNotes->CoNLL-coarse, %d test, ~%dx faster than %s.%s" % (
               verdict, sub_f1, sub_lat, head["label"], head["f1"], margin, ladder, len(test),
               int(head["latency"] / max(sub_lat, 1e-6)), head["label"], tail))
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "ner_4type_headtohead_llm_gpu_v1", "verdict": verdict, "verdict_msg": msg, "summary": msg,
               "elapsed_s": time.time() - t_tr, "substrate_f1": round(sub_f1, 4), "sub_latency": sub_lat,
               "llm_ladder": results, "n_test": len(test), "shots": 5},
              open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)


if "--self-test" in sys.argv:
    assert _collapse4([1, 2, 0, 15, 7, 8]) == [1, 2, 0, 0, 3, 4]
    assert _spans([1, 2, 0]) == {(0, 2, 0)}
    assert _match_span(["barack", "obama", "ran"], "barack obama") == (0, 2)
    assert _match_span(["a", "b"], "c") is None
    assert len(FEWSHOT.split("\n\n")) >= 5
    print("[selftest] PASS: ner-4type-headtohead", flush=True); sys.exit(0)
main()
