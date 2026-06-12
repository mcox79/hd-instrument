"""
exp_phase_6_1_h3_distractor_relevance_cpu_v1.py -- Phase 6.1 H3 distractor-relevance discriminator (Research drill rank-1).

USER directive (methodical, real end-task): pause synthetic Tier-5 mechanism cells; attack the operand-selection corpus deficiency
(the 6-deep MWP comprehension wall) with substrate structure. H3: a discriminative perceptron that tags each quantity in an ASDiv
problem as RELEVANT (in the gold equation) vs DISTRACTOR, using cheap heuristic features. Filtering distractors before operand
selection should lift ASDiv -- especially the distractor subset (currently ~0.135). Uses the substrate discriminative-perceptron
universal lever (makes it 12/12 capabilities).

Auto-label: a quantity is relevant=1 iff its numeric value appears among the gold-formula operands.
Features (heuristic, no spaCy): in_question_sentence, shares_content_word_with_question, nearest_verb_polarity (+1 gain / -1 loss /
0 stative via a small arithmetic-verb lexicon), value_distinctness (is the value unique among the problem's quantities), is_in_body,
magnitude_bucket. Averaged perceptron over these -> relevance.

Metrics: (a) relevance classification accuracy + F1 (held-out, multi-seed); (b) downstream operand-selection accuracy = does the
2-quantity problem whose relevant quantities match the gold-operand set get solved -- full set vs DISTRACTOR subset (problems with >=1
distractor quantity), vs an all-quantities baseline (no filtering, = the 0.39/0.135 status quo).

Pre-reg (Research): HP full-ASDiv >= 0.46 + distractor subset >= 0.31 + lift > +0.07 over 0.39 baseline. MIDDLE 0.42-0.46 / +0.03-0.07.
HARD_FAIL lift < +0.03 (NEG-3 architectural-ceiling branch -> consult NEG-1/NEG-2).

CPU. --self-test + --smoke + write_metrics. Multi-seed n=5. Deterministic. No LLM-judge. Route via local_cpu_queue (dashboard-visible).
"""
from __future__ import annotations
import json, os, re, sys, time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "phase_6_1_h3_distractor_relevance_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SELF_TEST = "--self-test" in sys.argv
SMOKE = RUN_MODE == "smoke"
SEEDS = [1, 2, 3, 4, 5]

_NUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
        "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
        "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
        "dozen": 12, "couple": 2, "pair": 2}
_GAIN = {"buy", "bought", "get", "got", "gain", "gained", "add", "added", "find", "found", "pick", "picked",
         "receive", "received", "earn", "earned", "collect", "collected", "plant", "planted", "more", "born"}
_LOSS = {"lose", "lost", "give", "gave", "sell", "sold", "eat", "ate", "spend", "spent", "use", "used",
         "remove", "removed", "drop", "dropped", "take", "took", "fewer", "less", "left", "away", "broke"}
_STOP = {"the", "a", "an", "of", "in", "on", "and", "are", "is", "to", "how", "many", "much", "there",
         "many", "does", "do", "did", "has", "have", "had", "were", "was", "be", "with", "for"}


def _words_to_num(tok):
    if tok in _NUM:
        return _NUM[tok]
    if re.fullmatch(r"\d+(\.\d+)?", tok):
        return float(tok) if "." in tok else int(tok)
    return None


def _quantities(text):
    """list of (value, token_index, sentence_index)."""
    sents = re.split(r"(?<=[.!?])\s+", text)
    out = []
    ti = 0
    for si, s in enumerate(sents):
        for w in re.findall(r"[A-Za-z]+|\d+\.?\d*", s):
            v = _words_to_num(w.lower())
            if v is not None and not (isinstance(v, int) and v == 0 and w.lower() not in _NUM):
                out.append({"value": v, "tok": ti, "sent": si, "word": w})
            ti += 1
    return out, sents


def _formula_operands(formula):
    lhs = formula.split("=")[0]
    return [float(x) if "." in x else int(x) for x in re.findall(r"\d+\.?\d*", lhs)]


def _content_words(text):
    return {w for w in re.findall(r"[a-z]+", text.lower()) if w not in _STOP and len(w) > 2}


def _nearest_verb_polarity(sent):
    toks = re.findall(r"[a-z]+", sent.lower())
    pol = 0
    for t in toks:
        if t in _GAIN:
            pol = 1
        elif t in _LOSS:
            pol = -1
    return pol


def _features(q, prob, all_vals, qwords):
    sents = prob["_sents"]
    sent_text = sents[q["sent"]] if q["sent"] < len(sents) else ""
    in_q = 1.0 if q["sent"] == prob["_qsent"] else 0.0
    swords = _content_words(sent_text)
    shares = 1.0 if (swords & qwords) else 0.0
    pol = _nearest_verb_polarity(sent_text)
    distinct = 1.0 if all_vals.count(q["value"]) == 1 else 0.0
    mag = min(q["value"] / 20.0, 2.0) if isinstance(q["value"], (int, float)) else 0.0
    return {"bias": 1.0, "in_q": in_q, "shares": shares, "pol_pos": 1.0 if pol > 0 else 0.0,
            "pol_neg": 1.0 if pol < 0 else 0.0, "distinct": distinct, "mag": mag}


def _load():
    data = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    probs = []
    for d in data:
        body = d.get("body", ""); question = d.get("question", ""); formula = d.get("formula", "")
        if "=" not in formula:
            continue
        text = body + " " + question
        qs, sents = _quantities(text)
        if len(qs) < 2:
            continue
        ops = _formula_operands(formula)
        # qsent = index of the sentence containing the question (last sentence usually)
        qsent = len(re.split(r"(?<=[.!?])\s+", body))  # question is appended after body sentences
        prob = {"qs": qs, "_sents": sents, "_qsent": qsent, "ops": ops, "question": question}
        # label each quantity: relevant if its value is a gold operand (consume one operand per match)
        remaining = list(ops)
        for q in qs:
            if q["value"] in remaining:
                q["rel"] = 1; remaining.remove(q["value"])
            else:
                q["rel"] = 0
        prob["has_distractor"] = any(q["rel"] == 0 for q in qs)
        probs.append(prob)
    return probs


def _train_perceptron(train, feat_keys, epochs, seed):
    import random
    rng = random.Random(seed)
    w = defaultdict(float); cw = defaultdict(float); c = 1
    examples = []
    for prob in train:
        all_vals = [q["value"] for q in prob["qs"]]; qwords = _content_words(prob["question"])
        for q in prob["qs"]:
            examples.append((_features(q, prob, all_vals, qwords), q["rel"]))
    for _ in range(epochs):
        rng.shuffle(examples)
        for feats, y in examples:
            score = sum(w[k] * v for k, v in feats.items())
            pred = 1 if score > 0 else 0
            if pred != y:
                sign = 1 if y == 1 else -1
                for k, v in feats.items():
                    w[k] += sign * v; cw[k] += sign * v * c
            c += 1
    return {k: w[k] - cw[k] / c for k in w}


def _predict(w, feats):
    return 1 if sum(w.get(k, 0.0) * v for k, v in feats.items()) > 0 else 0


def _eval_seed(probs, seed):
    n = len(probs)
    split = int(n * 0.7)
    import random
    idx = list(range(n)); random.Random(seed).shuffle(idx)
    train = [probs[i] for i in idx[:split]]; test = [probs[i] for i in idx[split:]]
    w = _train_perceptron(train, None, 2 if SMOKE else 10, seed)
    # relevance classification + downstream operand-selection
    tp = fp = fn = tn = 0
    sel_correct = sel_total = 0
    dsel_correct = dsel_total = 0
    base_correct = 0  # no-filter baseline: use ALL quantities (wrong if distractors present)
    for prob in test:
        all_vals = [q["value"] for q in prob["qs"]]; qwords = _content_words(prob["question"])
        pred_rel = []
        for q in prob["qs"]:
            p = _predict(w, _features(q, prob, all_vals, qwords)); pred_rel.append(p)
            if p == 1 and q["rel"] == 1: tp += 1
            elif p == 1 and q["rel"] == 0: fp += 1
            elif p == 0 and q["rel"] == 1: fn += 1
            else: tn += 1
        # operand-selection: did predicted-relevant value-multiset match gold operands?
        pred_vals = sorted(q["value"] for q, p in zip(prob["qs"], pred_rel) if p == 1)
        gold_vals = sorted(prob["ops"])
        all_q_vals = sorted(q["value"] for q in prob["qs"])
        ok = (pred_vals == gold_vals)
        sel_total += 1; sel_correct += int(ok)
        base_correct += int(all_q_vals == gold_vals)  # baseline correct only if no distractors
        if prob["has_distractor"]:
            dsel_total += 1; dsel_correct += int(ok)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    acc = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0.0
    return {"rel_acc": acc, "rel_f1": f1, "sel_acc": sel_correct / sel_total if sel_total else 0.0,
            "distractor_sel_acc": dsel_correct / dsel_total if dsel_total else 0.0,
            "baseline_sel_acc": base_correct / sel_total if sel_total else 0.0,
            "n_test": sel_total, "n_distractor": dsel_total}


def run():
    probs = _load()
    if SMOKE:
        probs = probs[:200]
    rows = [_eval_seed(probs, s) for s in (SEEDS[:2] if SMOKE else SEEDS)]
    def agg(k):
        xs = [r[k] for r in rows]; mu = sum(xs) / len(xs)
        sd = (sum((x - mu) ** 2 for x in xs) / len(xs)) ** 0.5
        return round(mu, 4), round(sd, 4)
    rel_acc, rel_acc_sd = agg("rel_acc"); rel_f1, _ = agg("rel_f1")
    sel, sel_sd = agg("sel_acc"); dsel, dsel_sd = agg("distractor_sel_acc"); base, _ = agg("baseline_sel_acc")
    return {"rel_acc": rel_acc, "rel_acc_sd": rel_acc_sd, "rel_f1": rel_f1, "sel_acc": sel, "sel_sd": sel_sd,
            "distractor_sel_acc": dsel, "distractor_sel_sd": dsel_sd, "baseline_sel_acc": base,
            "lift_over_baseline": round(sel - base, 4), "n_problems": len(probs), "n_test": rows[0]["n_test"],
            "n_distractor": rows[0]["n_distractor"]}


def verdict(r):
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    sel = r["sel_acc"]; dsel = r["distractor_sel_acc"]; base = r["baseline_sel_acc"]; lift = sel - base
    s = ("relevance disc acc=%.4f F1=%.4f | operand-sel full=%.4f distractor-subset=%.4f vs no-filter baseline=%.4f (lift %+.4f) | "
         "n=%d distractor-n=%d, multi-seed" % (r["rel_acc"], r["rel_f1"], sel, dsel, base, lift, r["n_test"], r["n_distractor"]))
    if sel >= 0.46 and dsel >= 0.31 and lift > 0.07:
        return ("HARD_PASS", "HARD_PASS: distractor-relevance discriminator lifts ASDiv operand-selection to >=0.46 (distractor >=0.31) -- substrate discriminative perceptron suppresses task-irrelevant quantities (PFC top-down attention analogue). " + s)
    if sel >= 0.42 and lift > 0.03:
        return ("MIDDLE_BAND", "MIDDLE_BAND: distractor-relevance adds +0.03-0.07 operand-selection. " + s)
    return ("HARD_FAIL", "HARD_FAIL: distractor-relevance lift <+0.03 (NEG-3 branch: consult H2 world-model / LEX_T-only). " + s)


def _self_test():
    assert _words_to_num("seven") == 7 and _words_to_num("dozen") == 12 and _words_to_num("3") == 3
    qs, _ = _quantities("Seven red apples and two green apples are in the basket.")
    assert sorted(q["value"] for q in qs) == [2, 7], [q["value"] for q in qs]
    assert _formula_operands("7+2=9") == [7, 2]
    assert _nearest_verb_polarity("He gave away 3 apples") == -1
    print("[self-test] PASS: num parse + quantity extract + formula operands + verb polarity")


if __name__ == "__main__":
    if SELF_TEST:
        _self_test(); sys.exit(0)
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
               "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r])
    print("[metrics] written", flush=True)
