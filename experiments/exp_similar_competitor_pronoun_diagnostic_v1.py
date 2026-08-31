"""exp_similar_competitor_pronoun_diagnostic_v1 -- the "COULD IT SUCCEED" ceiling test for the reframed
retrieval-interference problem (retrieval_interference_is_similar_competitor_cue_overload_not_event_count).

WHY THIS CELL EXISTS (discipline: ask whether the experiment COULD have succeeded before asking why it did
not). The gate cell (exp_generalize_retrieval_similar_competitor_gate_v1) reproduced on disk: on the LitBank
who-did-what "which entity did verb V" ambiguous subset, content-only floor = 0.398 and naive recency = 0.402,
NOT CI-separated (band NOT_SEP, P1 preview FAIL). So the SIMPLEST context cue TIES content there. The whole
problem then rests on whether a content x context COMBINATION is COMPLEMENTARY -- each cue right on a distinct
chunk of queries. If the cues mostly AGREE, no combination rule can beat the best single cue by +0.10 and the
memory route is a rigorous NEGATIVE. If they DISAGREE and each is right on its own chunk, there is real headroom.

This cell measures that on the RIGHT, brain-faithful population: REAL PRONOUN RESOLUTION among candidate
antecedents (data/litbank/pronoun_instances.json -- 9,128 instances, each with the pronoun, its sentence, the
gold antecedent entity, and the reconstructed candidate set {entity: [{sent, role}]}). This is exactly the
similar-competitor / partial-cue regime the research drill named (Arnold 2010 accessibility; Van Dyke & McElree
2006 cue-overload) -- a coarse pronoun cue with >=2 compatible antecedents.

Cues (ALL leak-free: only mentions in sentences STRICTLY BEFORE the pronoun sentence are visible):
  - CHANCE        : 1 / n_prior_candidates
  - FREQUENCY     : candidate with the most prior mentions (content/salience floor; = the who-did-what content floor)
  - RECENCY       : candidate whose nearest prior mention is closest (single-timescale TCM reduction)
  - SUBJECT_REC   : most-recent prior mention whose role is SUBJECT (grammatical salience / topicality, Arnold)
  - FIRST_MENTION : candidate introduced earliest (protagonist/topic primacy)
Oracles (ceilings -- right if the named cue is right on that query):
  - ORACLE_rec_freq : recency OR frequency
  - ORACLE_all      : any of the 4 cues
And the complementarity decomposition: when recency and frequency DISAGREE, who is right?

NO external LLM. NO torch (this is the CPU diagnostic; the TCM multi-timescale build follows only if the
ceiling justifies it). Deterministic. ASCII-only.

Run: .venv/Scripts/python.exe experiments/exp_similar_competitor_pronoun_diagnostic_v1.py --self-test
     ...                                                                                --full
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

ANCHOR = "similar_competitor_pronoun_diagnostic_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR)
PRON_PATH = os.path.join(REPO, "data", "litbank", "pronoun_instances.json")


def _log(m):
    print("[%s] %s" % (ANCHOR, m), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_instances():
    return json.load(open(PRON_PATH, encoding="utf-8"))


def prior_view(inst):
    """Return {cand_id: [(sent, role), ...]} keeping ONLY mentions strictly before the pronoun sentence.
    Leak-free: the pronoun's own sentence and anything after is invisible."""
    ps = int(inst["p_sent"])
    out = {}
    for cid, ms in inst["candidates"].items():
        prior = [(int(m["sent"]), str(m.get("role") or "OTHER")) for m in ms if int(m["sent"]) < ps]
        if prior:
            out[int(cid)] = prior
    return out


def predictions(inst):
    """Compute each cue's predicted antecedent id from the leak-free prior view, or None if undecidable.
    Deterministic tie-breaks: prefer the more-recent mention, then the lower entity id."""
    ps = int(inst["p_sent"])
    pv = prior_view(inst)
    if len(pv) < 2:
        return None  # not a similar-competitor query: 0 or 1 prior-mentioned candidate
    cands = sorted(pv.keys())

    def nearest(cid):  # smallest sentence gap to the pronoun (recency); larger sent = more recent
        return ps - max(s for s, _ in pv[cid])

    def freq(cid):
        return len(pv[cid])

    def first_mention(cid):
        return min(s for s, _ in pv[cid])

    def subj_recency(cid):
        subj = [s for s, r in pv[cid] if r == "SUBJECT"]
        return (ps - max(subj)) if subj else 10 ** 9

    freq_pred = max(cands, key=lambda c: (freq(c), -nearest(c), -c))            # most mentions
    rec_pred = min(cands, key=lambda c: (nearest(c), c))                        # closest prior mention
    first_pred = min(cands, key=lambda c: (first_mention(c), c))               # earliest introduced
    has_subj = any(subj_recency(c) < 10 ** 9 for c in cands)
    subj_pred = min(cands, key=lambda c: (subj_recency(c), c)) if has_subj else rec_pred

    gold = int(inst["gold"])
    gold_prior = gold in pv
    return {
        "gold": gold, "gold_prior": gold_prior, "n_cand": len(cands), "pronoun": inst["pronoun"].lower(),
        "FREQUENCY": freq_pred, "RECENCY": rec_pred, "FIRST_MENTION": first_pred, "SUBJECT_REC": subj_pred,
    }


CUES = ["FREQUENCY", "RECENCY", "SUBJECT_REC", "FIRST_MENTION"]


def acc(rows, cue, mask=None):
    r = rows if mask is None else [x for x, m in zip(rows, mask) if m]
    if not r:
        return float("nan")
    return float(np.mean([int(x[cue] == x["gold"]) for x in r]))


def boot_ci(vals, gen, n_boot=2000):
    v = np.asarray(vals, dtype=np.float64)
    n = len(v)
    if n == 0:
        return (float("nan"), float("nan"))
    idx = gen.integers(0, n, size=(n_boot, n))
    b = v[idx].mean(axis=1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def run(n_boot=2000):
    t0 = time.perf_counter()
    insts = load_instances()
    rows = [p for p in (predictions(i) for i in insts) if p is not None]
    gold_prior = [r for r in rows if r["gold_prior"]]  # the resolvable regime (gold has a prior mention)
    gen = np.random.default_rng(20260830)

    # accuracies on the ambiguous (>=2 prior candidates) subset, and on the resolvable subset
    def block(rs, label):
        chance = float(np.mean([1.0 / r["n_cand"] for r in rs])) if rs else float("nan")
        accs = {c: acc(rs, c) for c in CUES}
        # oracle ceilings
        orc_rf = float(np.mean([int(r["RECENCY"] == r["gold"] or r["FREQUENCY"] == r["gold"]) for r in rs]))
        orc_all = float(np.mean([int(any(r[c] == r["gold"] for c in CUES)) for r in rs]))
        # complementarity when recency and frequency DISAGREE
        disagree = [r for r in rs if r["RECENCY"] != r["FREQUENCY"]]
        d_n = len(disagree)
        d_rec_right = float(np.mean([int(r["RECENCY"] == r["gold"]) for r in disagree])) if d_n else float("nan")
        d_freq_right = float(np.mean([int(r["FREQUENCY"] == r["gold"]) for r in disagree])) if d_n else float("nan")
        best_single = max(accs, key=lambda c: accs[c])
        return {
            "label": label, "n": len(rs), "chance": chance, "acc": accs,
            "best_single_cue": best_single, "best_single_acc": accs[best_single],
            "ORACLE_rec_freq": orc_rf, "ORACLE_all": orc_all,
            "headroom_oracle_all_minus_best": orc_all - accs[best_single],
            "disagree_frac": d_n / len(rs) if rs else float("nan"),
            "when_disagree_recency_right": d_rec_right, "when_disagree_frequency_right": d_freq_right,
        }

    all_block = block(rows, "ambiguous_all")
    gp_block = block(gold_prior, "gold_has_prior_mention")

    # per-competitor-count strata on the resolvable subset
    strata = {}
    for lo, hi, lbl in [(2, 2, "2"), (3, 4, "3-4"), (5, 999, "5+")]:
        rs = [r for r in gold_prior if lo <= r["n_cand"] <= hi]
        strata[lbl] = block(rs, "ncand_" + lbl) if rs else {"n": 0}

    res = {"anchor": ANCHOR, "ts_iso": _now_iso(), "elapsed_s": time.perf_counter() - t0,
           "n_instances_total": len(insts), "n_ambiguous_queries": len(rows),
           "n_resolvable_gold_prior": len(gold_prior),
           "frac_gold_has_prior": len(gold_prior) / len(rows) if rows else float("nan"),
           "ambiguous_all": all_block, "resolvable": gp_block, "strata": strata}

    _log("instances=%d  ambiguous(>=2 prior cand)=%d  resolvable(gold has prior)=%d (%.1f%%)"
         % (len(insts), len(rows), len(gold_prior), 100.0 * res["frac_gold_has_prior"]))
    for b in (all_block, gp_block):
        _log("[%s] n=%d chance=%.3f | freq=%.3f rec=%.3f subjrec=%.3f first=%.3f"
             % (b["label"], b["n"], b["chance"], b["acc"]["FREQUENCY"], b["acc"]["RECENCY"],
                b["acc"]["SUBJECT_REC"], b["acc"]["FIRST_MENTION"]))
        _log("     best single=%s %.3f | ORACLE rec|freq=%.3f  ORACLE all=%.3f  HEADROOM(all-best)=%+.3f"
             % (b["best_single_cue"], b["best_single_acc"], b["ORACLE_rec_freq"], b["ORACLE_all"],
                b["headroom_oracle_all_minus_best"]))
        _log("     recency/freq DISAGREE on %.1f%% | when they disagree: recency right=%.3f freq right=%.3f"
             % (100.0 * b["disagree_frac"], b["when_disagree_recency_right"], b["when_disagree_frequency_right"]))
    for lbl, sv in strata.items():
        if sv.get("n"):
            _log("  competitors=%s n=%d best=%s %.3f ORACLE_all=%.3f headroom=%+.3f"
                 % (lbl, sv["n"], sv["best_single_cue"], sv["best_single_acc"], sv["ORACLE_all"],
                    sv["headroom_oracle_all_minus_best"]))
    # the decisive read
    hr = gp_block["headroom_oracle_all_minus_best"]
    verdict = ("HEADROOM_EXISTS_BUILD" if hr >= 0.10 else
               ("MARGINAL_HEADROOM" if hr >= 0.05 else "NO_HEADROOM_CUES_AGREE"))
    res["CEILING_VERDICT"] = verdict
    _log("CEILING VERDICT: %s (oracle-all beats best single cue by %+.3f on the resolvable subset)" % (verdict, hr))
    return res


def self_test():
    _log("SELF-TEST: cache loads; ambiguous subset non-empty; leak-free (pronoun-sentence mentions invisible)")
    insts = load_instances()
    assert isinstance(insts, list) and len(insts) > 1000, "expected many instances, got %r" % (len(insts),)
    rows = [p for p in (predictions(i) for i in insts) if p is not None]
    assert len(rows) > 500, "ambiguous subset too small: %d" % len(rows)
    for r in rows[:100]:
        assert r["n_cand"] >= 2
    # leak-free unit: a candidate mentioned ONLY at/after the pronoun sentence must be invisible
    toy = {"doc": "t", "pronoun": "she", "p_sent": 5, "gold": 9,
           "candidates": {"1": [{"sent": 0, "role": "SUBJECT"}, {"sent": 4, "role": "OBJECT"}],
                          "2": [{"sent": 2, "role": "SUBJECT"}],
                          "9": [{"sent": 5, "role": "SUBJECT"}]}}  # gold only at p_sent -> invisible
    pv = prior_view(toy)
    assert 9 not in pv, "a mention at the pronoun sentence must be invisible (leak): %r" % pv
    p = predictions(toy)
    assert p is not None and p["gold_prior"] is False, "gold has no prior mention here"
    # recency: entity 1 (sent 4) is nearer than entity 2 (sent 2) -> RECENCY picks 1
    assert p["RECENCY"] == 1, "recency should pick the nearer prior mention: %r" % p
    # frequency: entity 1 has 2 prior mentions vs entity 2 has 1 -> FREQUENCY picks 1
    assert p["FREQUENCY"] == 1, "frequency should pick the more-mentioned candidate: %r" % p
    _log("  ambiguous queries=%d" % len(rows))
    _log("SELF-TEST PASS")
    return {"n_instances": len(insts), "n_ambiguous": len(rows)}


def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    if args.self_test or not args.full:
        st = self_test()
        _atomic_write(os.path.join(OUTPUT_DIR, "_self_test", "metrics.json"),
                      {"verdict": "SELFTEST_PASS", "selftest": st, "ts_iso": _now_iso()})
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return
    res = run()
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), res)
    _log("DONE full in %.1fs -> %s" % (time.perf_counter() - t0, OUTPUT_DIR))


if __name__ == "__main__":
    main()
