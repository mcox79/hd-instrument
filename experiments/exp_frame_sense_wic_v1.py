"""exp_frame_sense_wic_v1 -- does the glass-box construction cue predict HUMAN same-sense judgements on WiC?

WHY WiC (not SemCor lexname): the SemCor eval (exp_frame_sense_semcor_v1) found that WordNet's LEXNAME taxonomy
FIGHTS the event-frame reading ('leave behind' = verb.cognition; 'time passed' = verb.motion; 'put' =
verb.contact), so a construction/event-frame disambiguator cannot beat MFS on a lexname gold -- a GOLD-mechanism
taxonomy mismatch, not a mechanism failure. WiC sidesteps this entirely: it is a balanced, HUMAN-judged binary
("do these two uses of the same word carry the SAME sense?"), with NO commitment to any sense inventory. The
floor is the majority class (~0.5, balanced), so there is real headroom.

MECHANISM: parse each context, disambiguate the target VERB -> event frame; predict SAME iff frame1 == frame2.
When neither context realises a diagnostic construction, both default to MFS -> SAME (underspecification). The
disambiguator earns its keep on the FIRES subset (>=1 context diagnostic) -- where a construction actually
discriminates the two uses.

ARMS: DISAMBIG (same iff same frame) vs MAJORITY / ALWAYS_SAME / ALWAYS_DIFF floors; TWIN (shuffled construction
per context -> random frames -> random same/diff). Populations: ALL verb pairs, and the FIRES subset (blind).

spaCy-bound -> INLINE. Parses cached to a pkl. Writes ONLY to data/exp_frame_sense_wic_v1[/ _smoke]. NO hdlab. ASCII.
"""
from __future__ import annotations
import argparse, json, os, pickle, sys, time
from collections import Counter
from datetime import datetime, timezone
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.frame_sense_disambiguator import (
    FrameSenseDisambiguator, extract_frame, candidate_frames, strong_construction, verb_confusions)
from tools.load_wsd_benchmarks import load_wic

ANCHOR = "frame_sense_wic_v1"


def _find_verb(doc, idx, lemma):
    """Locate the target verb token: prefer the token at word position `idx`, else nearest verb by lemma."""
    toks = [t for t in doc]
    if 0 <= idx < len(toks) and toks[idx].pos_ in ("VERB", "AUX"):
        return toks[idx]
    # WiC idx is a WORD index; spaCy tokenization is close but can drift -> match by lemma nearest idx
    best, bestd = None, 1e9
    for t in toks:
        if t.pos_ in ("VERB", "AUX") and (t.lemma_.lower() == lemma or t.text.lower().startswith(lemma[:4])):
            d = abs(t.i - idx)
            if d < bestd:
                best, bestd = t, d
    return best


def build_pairs(splits, smoke=False):
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    rows = []
    for sp in splits:
        for r in load_wic(sp):
            if r["pos"] != "V" or r["gold"] is None:
                continue
            rows.append(r)
    if smoke:
        rows = rows[:200]
    pairs = []
    dropped = Counter()
    for r in rows:
        lemma = r["lemma"].lower()
        cands = candidate_frames(lemma)
        if len(cands) < 2:
            dropped["monosemous"] += 1
            continue
        d1, d2 = nlp(r["sent1"]), nlp(r["sent2"])
        t1 = _find_verb(d1, r["idx1"], lemma)
        t2 = _find_verb(d2, r["idx2"], lemma)
        if t1 is None or t2 is None:
            dropped["no_verb"] += 1
            continue
        rf1, rf2 = extract_frame(t1.sent, t1), extract_frame(t2.sent, t2)
        conf = verb_confusions(cands)
        fires = bool(strong_construction(rf1, conf) or strong_construction(rf2, conf))
        pairs.append({"lemma": lemma, "cands": cands, "gold": bool(r["gold"]),
                      "rf1": rf1, "rf2": rf2, "fires": fires})
    return pairs, dict(dropped)


class _FakeTok:
    def __init__(self, lemma):
        self.lemma_ = lemma
        self.pos_ = "VERB"


def predict_same(dis, p, joint=True, shuf1=None, shuf2=None):
    v1 = dis.disambiguate_token(None, _FakeTok(p["lemma"]), cand=p["cands"], frame_feats=p["rf1"],
                                joint=joint, shuffle_frame=shuf1)
    v2 = dis.disambiguate_token(None, _FakeTok(p["lemma"]), cand=p["cands"], frame_feats=p["rf2"],
                                joint=joint, shuffle_frame=shuf2)
    return v1.frame == v2.frame


def boot(v, seed, nb=2000):
    a = np.asarray(v, float)
    if len(a) == 0:
        return 0.0, 0.0, 0.0
    r = np.random.default_rng(seed)
    m = a[r.integers(0, len(a), size=(nb, len(a)))].mean(1)
    return float(a.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def eval_pop(pairs, dis, seed, name):
    if name == "fires":
        pairs = [p for p in pairs if p["fires"]]
    rng = np.random.default_rng(seed + 5)
    dis_ok, maj_ok, same_ok, diff_ok, twin_ok = [], [], [], [], []
    golds = [p["gold"] for p in pairs]
    maj = (sum(golds) >= len(golds) / 2) if golds else True    # majority label
    for p in pairs:
        g = p["gold"]
        pr = predict_same(dis, p, joint=True)
        n = len(p["cands"])
        s1 = rng.permutation(n); s2 = rng.permutation(n)
        tw = predict_same(dis, p, joint=True, shuf1=s1, shuf2=s2)
        dis_ok.append(int(pr == g)); twin_ok.append(int(tw == g))
        maj_ok.append(int(maj == g)); same_ok.append(int(True == g)); diff_ok.append(int(False == g))
    out = {"n": len(pairs), "pct_same_gold": float(np.mean(golds)) if golds else 0.0}
    for i, (k, v) in enumerate((("DISAMBIG", dis_ok), ("MAJORITY", maj_ok), ("ALWAYS_SAME", same_ok),
                                ("ALWAYS_DIFF", diff_ok), ("TWIN", twin_ok))):
        out[k] = list(boot(v, seed + 101 * (i + 1)))
    # McNemar DISAMBIG vs the strongest floor (max of the three floors)
    floor_name = max(("MAJORITY", "ALWAYS_SAME", "ALWAYS_DIFF"), key=lambda k: out[k][0])
    fl = {"MAJORITY": maj_ok, "ALWAYS_SAME": same_ok, "ALWAYS_DIFF": diff_ok}[floor_name]
    b = sum(1 for i in range(len(pairs)) if fl[i] and not dis_ok[i])
    c = sum(1 for i in range(len(pairs)) if dis_ok[i] and not fl[i])
    import math
    nn = b + c
    out["mcnemar_vs_floor"] = {"floor": floor_name, "b_floor_only": b, "c_disambig_only": c,
                               "p": (min(1.0, sum(math.comb(nn, i) for i in range(min(b, c) + 1)) * 0.5 ** nn * 2)
                                     if nn else 1.0)}
    return out


def run(smoke=False, seed=20260828):
    t0 = time.time()
    cache = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""), "pairs_v1.pkl")
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    splits = ["dev"] if smoke else ["train", "dev", "test"]
    if os.path.exists(cache):
        pairs, dropped = pickle.load(open(cache, "rb"))
    else:
        pairs, dropped = build_pairs(splits, smoke=smoke)
        pickle.dump((pairs, dropped), open(cache, "wb"))
    dis = FrameSenseDisambiguator(nlp="cached")
    res = {"all": eval_pop(pairs, dis, seed, "all"), "fires": eval_pop(pairs, dis, seed, "fires")}
    fr = res["fires"]
    strongest = max(fr["MAJORITY"][0], fr["ALWAYS_SAME"][0], fr["ALWAYS_DIFF"][0])
    strongest_hi = max(fr["MAJORITY"][2], fr["ALWAYS_SAME"][2], fr["ALWAYS_DIFF"][2])
    gates = {
        "disambig_beats_floor_ci_fires": bool(fr["DISAMBIG"][1] > strongest_hi),
        "twin_loses_ci_fires": bool(fr["DISAMBIG"][1] > fr["TWIN"][2]),
        "mcnemar_sig_fires": bool(fr["mcnemar_vs_floor"]["p"] < 0.05
                                  and fr["mcnemar_vs_floor"]["c_disambig_only"] > fr["mcnemar_vs_floor"]["b_floor_only"]),
    }
    verdict = "HARD_PASS" if (gates["disambig_beats_floor_ci_fires"] and gates["twin_loses_ci_fires"]) else \
              ("MIDDLE_BAND" if fr["DISAMBIG"][0] > strongest else "HARD_FAIL")
    return {"anchor_name": ANCHOR, "verdict": verdict, "run_mode": "smoke" if smoke else "full",
            "seed": seed, "n_pairs": len(pairs), "dropped": dropped, "results": res, "gates": gates,
            "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full"); ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    smoke = bool(args.smoke) or args.self_test or args.mode == "smoke"
    out_dir = os.path.join(REPO, "data", f"exp_{ANCHOR}" + ("_smoke" if smoke else ""))
    os.makedirs(out_dir, exist_ok=True)
    m = run(smoke=smoke, seed=args.seed)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    json.dump(m, open(tmp, "w", encoding="ascii"), indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(f"=== {ANCHOR} ({m['run_mode']}) {m['elapsed_s']}s n_pairs={m['n_pairs']} dropped={m['dropped']} ===")
    for pop in ("all", "fires"):
        r = m["results"][pop]
        print(f"[{pop}] n={r['n']} pct_same_gold={r['pct_same_gold']:.3f}")
        for k in ("DISAMBIG", "MAJORITY", "ALWAYS_SAME", "ALWAYS_DIFF", "TWIN"):
            print(f"    {k:13s} {r[k][0]:.3f} [{r[k][1]:.3f},{r[k][2]:.3f}]")
        mc = r["mcnemar_vs_floor"]
        print(f"    McNemar vs {mc['floor']}: p={mc['p']:.2e} (b={mc['b_floor_only']} c={mc['c_disambig_only']})")
    print("VERDICT:", m["verdict"], "GATES:", m["gates"])
    print("wrote", out_dir)


if __name__ == "__main__":
    main()
