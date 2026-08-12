"""tools/measure_threshold_and_lowinfo_v1.py -- STEP-2 faults (b) and (c).

(b) LOW-INFORMATION OBJECTS: measure hdlab.low_information_filter on the real corpus. Does the
    closed-class-calibrated flatness gate catch `people` (which survived 6 times as a "meaning")
    WITHOUT swallowing informative words? Emits the full excluded set for inspection.

(c) SENSE_MATCH_THRESH=0.45 CLUSTERING: the accepted best_cos values pile up at 0.45-0.48. Two
    rival explanations, and they have opposite implications:
      H_tail   the underlying best-cos distribution is smooth and DECREASING through 0.45, so any
               threshold produces a pile just above it. Then the accepted set is the upper TAIL OF
               A NOISE DISTRIBUTION, raising the threshold buys a smaller slice of the same noise,
               and the threshold is not the problem -- the ABSENCE OF A SIGNAL MODE is.
      H_mode   there is a separate, higher-cosine population of TRUE sense-matches, and 0.45 is
               set too low, admitting noise that a better-placed threshold would exclude.
    Discriminated against a real NULL: re-run the SAME argmax-cosine operation with the anchor
    identities randomly PERMUTED. If real and null best-cos distributions coincide around 0.45,
    the accepted mass is noise and H_tail holds.

    THE THRESHOLD IS NOT CHANGED BY THIS SCRIPT. Measuring the sensitivity is not licence to tune
    it to the audit -- that would be fitting to the test.

Writes data/analysis_threshold_lowinfo_v1/metrics.json.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class          # noqa: E402
from hdlab.low_information_filter import build_profile           # noqa: E402
from hdlab.thematic_role_labeler import lemma_word               # noqa: E402
from tools.measure_definitional_pattern_association_v2 import load_corpus  # noqa: E402

FOUND = os.path.join(REPO_ROOT, "data", "foundation", "reading_grounding_v2_qualityfix")
OUT_DIR = os.path.join(REPO_ROOT, "data", "analysis_threshold_lowinfo_v1")
TOK = re.compile(r"[A-Za-z][A-Za-z'-]*")


def main() -> None:
    out: dict = {}

    # ------------------------------------------------------------------ (b) low-information
    corpus = load_corpus()
    doc_lemmas = [[lemma_word(t) for t in TOK.findall(s)] for _seg, s in corpus]
    prof = build_profile(doc_lemmas)

    prov = [json.loads(l) for l in open(os.path.join(FOUND, "grounding_provenance.jsonl"),
                                        encoding="utf-8") if l.strip()]
    obj_counts = Counter(r["object"] for r in prov)
    # NOTE: v2 objects are OLD-stemmer strings ("statu"); map them through the corpus vocabulary
    # by exact match where possible. `people` is unaffected by the stemmer, which is why it is
    # the clean test case.
    refused_objects = {o: n for o, n in obj_counts.items() if prof.is_low_information(o)}
    n_facts_refused = sum(refused_objects.values())

    pmi_refused = []
    for r in prov:
        ok, reason = prof.eligible_meaning(r["subject"], r["object"])
        if not ok:
            pmi_refused.append({"subject": r["subject"], "object": r["object"],
                                "reason": reason, "pmi": prof.pmi(r["subject"], r["object"])})

    out["b_low_information"] = {
        "profile": prof.to_dict(),
        "people_df": prof.doc_freq("people"),
        "people_is_low_information": prof.is_low_information("people"),
        "n_v2_facts": len(prov),
        "objects_refused_by_df_gate": refused_objects,
        "n_v2_facts_refused_by_df_gate": n_facts_refused,
        "n_v2_facts_refused_by_either_gate": len(pmi_refused),
        "refusal_reason_counts": dict(Counter(x["reason"] for x in pmi_refused)),
        "sample_refusals": pmi_refused[:30],
        # sanity: informative technical words MUST survive the gate
        "control_informative_words_survive": {
            w: (not prof.is_low_information(w), prof.doc_freq(w))
            for w in ["nephron", "polymerase", "organelle", "cytoplasm", "haploid",
                      "phylogenetic", "artery", "kidney", "gene"]},
    }

    # ------------------------------------------------------------------ (c) threshold
    z = np.load(os.path.join(FOUND, "concept_space.npz"), allow_pickle=True)
    lemmas = [str(x) for x in z["lemmas"]]
    sums = np.array(z["sums"], dtype=np.float64)
    sign = np.sign(sums)
    norms = np.linalg.norm(sign, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    unit = sign / norms
    cos = unit @ unit.T
    np.fill_diagonal(cos, -np.inf)
    real_best = cos.max(axis=1)

    # ---- NULL (corrected). A LABEL PERMUTATION is vacuous here: relabelling the anchors does
    # not change the geometry, so every row still finds its own vector and the null max is 1.0
    # by construction (that was the first attempt; it is recorded in the notes as a caught bug).
    # The right null for "does clearing 0.45 mean anything?" is an EXTREME-VALUE null: the
    # mechanism takes an ARGMAX over ~1415 anchors, and an argmax over many draws is large even
    # when every draw is unrelated. So: for each lemma, resample 1414 cosines from the GLOBAL
    # pool of pairwise cosines (i.e. from UNRELATED word pairs) and take their max. If the real
    # argmax distribution sits on top of this, clearing 0.45 is what an unrelated word does.
    iu = np.triu_indices(cos.shape[0], k=1)
    pool = (unit @ unit.T)[iu]
    out_pairwise = {
        "n_pairs": int(pool.size),
        "percentiles": {f"p{p}": round(float(np.percentile(pool, p)), 4)
                        for p in (5, 25, 50, 75, 90, 95, 99, 99.9)},
    }
    rng = np.random.default_rng(20260812)
    n_anchor = unit.shape[0]
    null_best = rng.choice(pool, size=(3 * n_anchor, n_anchor - 1), replace=True).max(axis=1)
    # ...and this iid null is ALSO invalid (recorded, not hidden): a lemma's 1414 cosines are not
    # independent draws from the global pool -- each row has its own scale -- so resampling from
    # a pool that pools every row's upper tail overstates the max (null p50=0.79 EXCEEDS the real
    # p50=0.54, which is the tell). Both naive nulls fail, so the question is settled WITHOUT a
    # null, by measuring how DISCRIMINATING the threshold is directly:
    #   (i) how many anchors clear 0.45 for a typical lemma? If many, "the argmax cleared 0.45"
    #       says almost nothing -- the pick among them is close to arbitrary.
    #   (ii) what is the MARGIN between the top-1 and top-2 anchor? A near-zero margin means the
    #        identity of the winner is decided by noise, whatever the threshold is set to.
    n_above = {}
    margins = {}
    part = np.partition(cos, -2, axis=1)
    top1 = part[:, -1]
    top2 = part[:, -2]
    margin = top1 - top2
    for t in (0.45, 0.50, 0.55, 0.60):
        cnt = (cos >= t).sum(axis=1)
        n_above[f"thresh_{t:.2f}"] = {
            "median_anchors_clearing": int(np.median(cnt)),
            "mean_anchors_clearing": round(float(cnt.mean()), 1),
            "frac_lemmas_with_>=10_candidates": round(float((cnt >= 10).mean()), 4)}
    margins = {
        "top1_minus_top2_percentiles": {f"p{p}": round(float(np.percentile(margin, p)), 4)
                                        for p in (5, 25, 50, 75, 95)},
        "frac_margin_below_0.02": round(float((margin < 0.02).mean()), 4),
        "frac_margin_below_0.05": round(float((margin < 0.05).mean()), 4),
    }

    accepted = np.array([r["best_cos"] for r in prov], dtype=np.float64)
    refusals = [json.loads(l) for l in open(os.path.join(FOUND, "grounding_refusals.jsonl"),
                                            encoding="utf-8") if l.strip()]
    refused_cos = np.array([r["best_cos"] for r in refusals if r.get("best_cos") is not None])

    def pct(a, ps=(5, 25, 50, 75, 90, 95, 99)):
        return {f"p{p}": round(float(np.percentile(a, p)), 4) for p in ps}

    bins = [0.0, 0.35, 0.40, 0.45, 0.48, 0.50, 0.55, 0.60, 0.70, 1.01]

    def hist(a):
        h, _ = np.histogram(a, bins=bins)
        return {f"[{bins[i]:.2f},{bins[i+1]:.2f})": int(h[i]) for i in range(len(h))}

    sens = {}
    for t in (0.45, 0.48, 0.50, 0.55, 0.60, 0.65):
        n_real = int((accepted >= t).sum())
        sens[f"thresh_{t:.2f}"] = {
            "n_accepted_facts_retained": n_real,
            "frac_of_current_634": round(n_real / len(accepted), 4),
            "null_frac_clearing_t": round(float((null_best >= t).mean()), 4),
            }

    out["c_threshold"] = {
        "n_anchors_in_concept_space": len(lemmas),
        "SENSE_MATCH_THRESH_in_code": 0.45,
        "accepted_best_cos_percentiles": pct(accepted),
        "accepted_best_cos_hist": hist(accepted),
        "refused_best_cos_percentiles": pct(refused_cos),
        "real_argmax_cos_percentiles": pct(real_best),
        "pairwise_cosine_pool": out_pairwise,
        "null_extremevalue_argmax_cos_percentiles": pct(null_best),
        "null_extremevalue_argmax_cos_hist": hist(null_best),
        "frac_null_anchors_above_0.45": round(float((null_best >= 0.45).mean()), 4),
        "frac_real_anchors_above_0.45": round(float((real_best >= 0.45).mean()), 4),
        "threshold_sensitivity": sens,
        "how_discriminating_is_the_threshold": n_above,
        "argmax_top1_top2_margin": margins,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))

    b = out["b_low_information"]
    print("--- (b) low-information gate ---")
    print("df_threshold=%d calibrated on %r; excludes %d open-class lemmas"
          % (b["profile"]["df_threshold"], b["profile"]["calibration_lemma"],
             b["profile"]["n_excluded_open_class"]))
    print("people df=%d low_info=%s" % (b["people_df"], b["people_is_low_information"]))
    print("excluded open-class sample:", b["profile"]["excluded_open_class"][:60])
    print("v2 facts refused by df gate: %d ; by either gate: %d %s"
          % (b["n_v2_facts_refused_by_df_gate"], b["n_v2_facts_refused_by_either_gate"],
             b["refusal_reason_counts"]))
    print("controls (must all be True):", b["control_informative_words_survive"])
    print("--- (c) threshold ---")
    print(json.dumps(out["c_threshold"], indent=2))


if __name__ == "__main__":
    main()
