"""
exp_lb_llm05b_ft_fewshot_gpu_v1.py -- L-B LLM-0.5B fine-tuned few-shot NER comparison (the crossover follow-on, Research-approved).

Completes the L-B substrate-product positioning claim. Substrate-classical NER (L-B) reached 0.40 F1 at 5% data. This cell fine-tunes
Qwen2.5-0.5B as a token classifier on the SAME 4-type NER, at the SAME data fractions + seeds + eval set, so the curves are directly
comparable. Decisive test (Research pre-reg): if LLM-0.5B-FT < 0.30 at 5% data, substrate (0.40) WINS the low-data regime by >+0.10.

Method: AutoModelForTokenClassification(Qwen2.5-0.5B, 9 BIO-4type labels). Word->subword label alignment (label first subword, -100
rest). Manual AdamW fine-tune (more epochs for small fractions). Eval: subword logits -> first-subword word tags -> spans -> span-F1
(SAME _spans metric as substrate). Fractions {1,5,10,50,100}% (smoke: {5,100}).

Pre-reg (Research): HARD-PASS-DECISIVE LLM-0.5B-FT < 0.30 at 5% (substrate wins +0.10) / MIDDLE 0.30-0.40 / HARD-FAIL >= 0.40 (low-data
regime claim refuted). Headline = LLM-FT F1 at 5% vs substrate 0.40.

GPU (Qwen-0.5B FT; ~2-3 GPU-hrs). import torch first (PROT-020). Env-gated if transformers/torch absent (laptop gate). write_metrics.
"""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "lb_llm05b_ft_fewshot_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SELF_TEST = "--self-test" in sys.argv
SMOKE = RUN_MODE == "smoke"
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
FRACTIONS = [0.01, 0.05, 0.10, 0.50, 1.0]
SEED = 1028
# substrate L-B reference curve (exp_lb_ner_fewshot_curve_cpu_v1, 3-seed means) for side-by-side
SUBSTRATE_CURVE = {0.01: 0.2032, 0.05: 0.4039, 0.10: 0.5009, 0.50: 0.5711, 1.0: 0.6441}


from experiments.exp_ner_4type_conll_cpu_v1 import _collapse4  # noqa: E402  -- integer conll2012 tag-id -> 4-type BIO string


def _spans(tags):
    sp = set(); i = 0; n = len(tags)
    while i < n:
        if tags[i].startswith("B-"):
            ty = tags[i][2:]; j = i + 1
            while j < n and tags[j] == "I-" + ty:
                j += 1
            sp.add((i, j, ty)); i = j
        else:
            i += 1
    return sp


def _f1(gold_sets, pred_sets):
    tp = fp = fn = 0
    for g, p in zip(gold_sets, pred_sets):
        tp += len(g & p); fp += len(p - g); fn += len(g - p)
    pr = tp / (tp + fp + 1e-9); rc = tp / (tp + fn + 1e-9)
    return 2 * pr * rc / (pr + rc + 1e-9)


def run():
    import torch  # PROT-020 GPU job
    try:
        from transformers import AutoTokenizer, AutoModelForTokenClassification
    except Exception:
        return {"error": "transformers_unavailable_env_gated", "note": "needs transformers + torch + Qwen-0.5B (home GPU); harness ready"}
    import numpy as np
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    train = [(t, _collapse4(g)) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, _collapse4(g)) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE:
        train = train[:200]; test = test[:80]
    LABELS = sorted({tg for _w, g in train for tg in g})
    lab2id = {l: i for i, l in enumerate(LABELS)}
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    def encode(batch_words, batch_tags=None, max_len=128):
        enc = tok(batch_words, is_split_into_words=True, truncation=True, max_length=max_len,
                  padding=True, return_tensors="pt")
        word_ids_list = [enc.word_ids(b) for b in range(len(batch_words))]
        labels = None
        if batch_tags is not None:
            labels = []
            for b, tags in enumerate(batch_tags):
                wids = word_ids_list[b]; prev = None; row = []
                for wid in wids:
                    if wid is None:
                        row.append(-100)
                    elif wid != prev:
                        row.append(lab2id.get(tags[wid], lab2id["O"]))
                    else:
                        row.append(-100)
                    prev = wid
                labels.append(row)
            labels = torch.tensor(labels)
        return enc, word_ids_list, labels

    gold_sets = [_spans(g) for _t, g in test]
    test_words = [t for t, _g in test]
    rng = np.random.default_rng(SEED)
    fracs = ([0.05, 1.0] if SMOKE else FRACTIONS)
    curve = []
    for frac in fracs:
        # subset train (seed-shuffled)
        idx = rng.permutation(len(train))[:max(5, int(len(train) * frac))]
        sub = [train[i] for i in idx]
        n = len(sub)
        mdl = AutoModelForTokenClassification.from_pretrained(
            MODEL_ID, num_labels=len(LABELS),
            dtype=torch.float32).to(DEV)
        mdl.config.pad_token_id = tok.pad_token_id
        opt = torch.optim.AdamW(mdl.parameters(), lr=2e-5)
        epochs = 2 if SMOKE else (30 if n < 200 else (15 if n < 1000 else 5))
        bs = 8
        mdl.train()
        for ep in range(epochs):
            order = rng.permutation(n)
            for s in range(0, n, bs):
                bidx = order[s:s + bs]
                bw = [sub[i][0] for i in bidx]; bt = [sub[i][1] for i in bidx]
                enc, _wids, labels = encode(bw, bt)
                enc = {k: v.to(DEV) for k, v in enc.items()}; labels = labels.to(DEV)
                out = mdl(**enc, labels=labels)
                out.loss.backward(); opt.step(); opt.zero_grad()
        # eval
        mdl.eval(); pred_sets = []
        with torch.no_grad():
            for s in range(0, len(test_words), bs):
                bw = test_words[s:s + bs]
                enc, wids, _ = encode(bw)
                enc2 = {k: v.to(DEV) for k, v in enc.items()}
                logits = mdl(**enc2).logits.cpu()
                preds = logits.argmax(-1)
                for b in range(len(bw)):
                    wtags = []; prev = None
                    for ti, wid in enumerate(wids[b]):
                        if wid is None or wid == prev:
                            prev = wid; continue
                        wtags.append(LABELS[int(preds[b][ti])]); prev = wid
                    # pad/truncate to word count
                    nw = len(bw[b])
                    wtags = (wtags + ["O"] * nw)[:nw]
                    pred_sets.append(_spans(wtags))
        f1 = round(_f1(gold_sets, pred_sets), 4)
        curve.append({"frac": frac, "n_train": n, "llm_ft_f1": f1, "substrate_f1": SUBSTRATE_CURVE.get(frac)})
        print("  frac=%.2f n=%-5d LLM-0.5B-FT F1=%.4f | substrate=%.4f" % (frac, n, f1, SUBSTRATE_CURVE.get(frac, -1)), flush=True)
        del mdl
        if DEV == "cuda":
            torch.cuda.empty_cache()
    by = {r["frac"]: r["llm_ft_f1"] for r in curve}
    llm_5 = by.get(0.05, 0.0); sub_5 = SUBSTRATE_CURVE[0.05]
    return {"curve": curve, "llm_ft_5pct": llm_5, "substrate_5pct": sub_5,
            "low_data_gap": round(sub_5 - llm_5, 4), "device": DEV, "n_test": len(test)}


def verdict(r):
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    llm5 = r["llm_ft_5pct"]; sub5 = r["substrate_5pct"]; gap = sub5 - llm5
    s = ("LLM-0.5B-FT @5%%=%.4f vs substrate @5%%=%.4f (substrate-gap %+.4f) | full curve %s | n_test=%d"
         % (llm5, sub5, gap, {c["frac"]: (c["llm_ft_f1"], c["substrate_f1"]) for c in r["curve"]}, r["n_test"]))
    if llm5 < 0.30:
        return ("HARD_PASS", "HARD_PASS DECISIVE: substrate WINS the low-data regime -- LLM-0.5B-FT %.4f < 0.30 at 5%% data while substrate-classical NER reaches %.4f (+%.4f). LLMs need far more data to match substrate at 5%%. " % (llm5, sub5, gap) + s)
    if llm5 < 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate competitive at low data (LLM-0.5B-FT %.4f in [0.30,0.40), substrate %.4f) -- no decisive win. " % (llm5, sub5) + s)
    return ("HARD_FAIL", "HARD_FAIL: LLM-0.5B-FT %.4f >= 0.40 at 5%% -- low-data-regime win REFUTED; LLM-FT matches/beats substrate. " % llm5 + s)


def _self_test():
    assert _spans(["B-PER", "I-PER", "O", "B-ORG"]) == {(0, 2, "PER"), (3, 4, "ORG")}
    assert _collapse4([1, 2, 0]) and all(isinstance(x, str) for x in _collapse4([1, 2, 0]))  # integer tag-ids -> str BIO
    g = [{(0, 2, "PER")}]; p = [{(0, 2, "PER")}]
    assert abs(_f1(g, p) - 1.0) < 1e-6
    print("[self-test] PASS: spans + collapse4(int-tags) + span-F1")


if __name__ == "__main__":
    if SELF_TEST:
        _self_test(); sys.exit(0)
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
               "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r])
    print("[metrics] written", flush=True)
