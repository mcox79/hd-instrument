"""hdlab/low_information_filter.py -- measured LOW-INFORMATION gate for grounding objects.

THE PROBLEM (measured 2026-08-12)
---------------------------------
The reading-grounding loop already refuses CLOSED-CLASS objects (`hdlab.closed_class_lexicon`),
which killed `also` / `say` / `like` / `more` as "meanings". But `people` survived as the meaning
of six unrelated words (fan / risk / recover / rural / danger / fire -> people) because `people`
is an open-class noun. A blacklist entry for `people` would be fitting to the audit; the real
property is that `people` is DISTRIBUTIONALLY FLAT -- it occurs in so many contexts that its
proximity to a word tells you nothing about that word.

THE PRINCIPLE (calibrated to the EXISTING gate, not to a new magic number)
-------------------------------------------------------------------------
The closed-class lexicon is the project's already-accepted operational definition of "a word
with no referential content of its own". So: measure the PMI that a TYPICAL FUNCTION WORD has
with the subjects being grounded, and refuse any object that is NO MORE INFORMATIVE about its
subject than a function word is. The floor is READ OFF the gate that already exists; nothing is
invented and nothing is hand-listed. Measured on the live corpus (32,955 sentences): the
closed-class reference PMI is p50=0.96 / p75=2.10 / p90=3.33, and the p75 floor removes ALL 20
`X -> people` facts while leaving every known-meaningful pair untouched (primer/polymerase 9.1,
aorta/artery 9.8, nephron/kidney 8.7, cholesterol/lipid 6.2).

WHAT WAS TRIED AND REJECTED (kept visible so the gate is auditable, not asserted)
--------------------------------------------------------------------------------
  * "flattest closed-class word by document frequency" -> df_threshold=5 (set by `forty`) and
    refused 7293 open-class lemmas including `nephron`. The closed-class set spans the whole
    frequency range; its MINIMUM carries no information. Caught by the control words.
  * ANY pure document-frequency / IDF rule -> in a corpus about cells, `cell` (df=1439) is both
    frequent and maximally informative, while `people` (df=2019) is frequent and empty. DF alone
    cannot separate them, so DF is REPORTED here and never gated on.
  * PMI as a MEANING-QUALITY score -> measured and REJECTED for that purpose: `shed -> quirky`
    scores PMI 9.9 and `austria -> girlfriend` 8.8, ABOVE every known-meaningful pair. PMI
    rewards rare co-occurrence. It is a valid LOW-INFORMATION gate and NOT a quality signal;
    conflating the two would be the same error this whole exercise is correcting.

Both gates are MEASURED FROM THE CORPUS BEING READ. Nothing is hand-listed.

ASCII-only.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from hdlab.closed_class_lexicon import is_closed_class


@dataclass
class InformationProfile:
    """Corpus-measured lemma statistics + the calibrated flatness threshold."""
    n_docs: int
    df: Dict[str, int]
    pair_df: Dict[Tuple[str, str], int]
    df_threshold: int                      # REPORTED ONLY (99.5th DF pct) -- never a gate
    calibration_lemma: str                 # provenance string for df_threshold
    excluded_open_class: List[str]         # high-DF open-class lemmas, REPORTED for inspection
    pmi_floor: float = 0.0                 # THE gate; calibrated off the closed-class lexicon
    pmi_calibration: Optional[dict] = None # how pmi_floor was derived (auditable)

    # ---------------------------------------------------------------------------------------
    def doc_freq(self, lemma: str) -> int:
        return self.df.get(lemma, 0)

    def is_high_frequency(self, lemma: str) -> bool:
        """REPORTED ONLY. Document frequency alone cannot separate `people` from `cell` (in a
        corpus about cells, `cell` is both frequent and maximally informative), so this is never
        used as a gate. See the calibration comment in build_profile."""
        return self.df.get(lemma, 0) >= self.df_threshold

    def pmi(self, a: str, b: str) -> float:
        """Pointwise mutual information over sentence co-occurrence. Returns -inf when the pair
        never co-occurs (an object that never appears with its subject cannot be its meaning)."""
        key = (a, b) if a <= b else (b, a)
        n_ab = self.pair_df.get(key, 0)
        n_a, n_b = self.df.get(a, 0), self.df.get(b, 0)
        if n_ab == 0 or n_a == 0 or n_b == 0:
            return float("-inf")
        p_ab = n_ab / self.n_docs
        p_a, p_b = n_a / self.n_docs, n_b / self.n_docs
        return math.log(p_ab / (p_a * p_b), 2)

    def eligible_meaning(self, subject: str, obj: str, *, min_pmi: Optional[float] = None
                         ) -> Tuple[bool, Optional[str]]:
        """THE gate. `obj` must be more informative about `subject` than a function word is.
        Returns (ok, refusal_reason_or_None).

        HONEST SCOPE NOTE: this requires the meaning to CO-OCCUR with what it means. That is
        automatic for DEFINITIONAL grounding (a definition sentence contains both words) but is
        a real extra assumption for the DISTRIBUTIONAL path, where second-order similarity
        (`artery`/`vein` are similar without co-occurring) is the whole point. Measured
        consequence on the v2 store: 634 -> 293 facts. Reported both ways, never silently."""
        floor = self.pmi_floor if min_pmi is None else min_pmi
        v = self.pmi(subject, obj)
        if v <= floor:
            return False, ("NEVER_CO_OCCURS" if v == float("-inf") else "LOW_INFORMATION_OBJECT")
        return True, None

    def to_dict(self) -> dict:
        return {"n_docs": self.n_docs, "pmi_floor": round(self.pmi_floor, 4),
                "pmi_calibration": self.pmi_calibration,
                "df_threshold_REPORTED_ONLY": self.df_threshold,
                "n_high_frequency_open_class_REPORTED_ONLY": len(self.excluded_open_class)}


def build_profile(doc_lemmas: Sequence[Sequence[str]], *,
                  track_pairs: bool = True) -> InformationProfile:
    """Measure DF / pair-DF over `doc_lemmas` (one inner sequence per sentence = one 'document')
    and calibrate the flatness threshold off the closed-class lexicon."""
    n_docs = len(doc_lemmas)
    df: Counter = Counter()
    pair_df: Counter = Counter()
    for lemmas in doc_lemmas:
        uniq = sorted(set(lemmas))
        df.update(uniq)
        if track_pairs:
            for i, a in enumerate(uniq):
                for b in uniq[i + 1:]:
                    pair_df[(a, b)] += 1

    # ---- CALIBRATION ------------------------------------------------------------------------
    # FIRST ATTEMPT (recorded because it was WRONG and the controls caught it): take the LEAST
    # frequent closed-class word as the flatness reference. That set df_threshold=5 (on `forty`)
    # and refused 7293 open-class lemmas including `nephron` and `polymerase` -- the closed-class
    # set spans the whole frequency range, so its MINIMUM is meaningless.
    #
    # SECOND PROBLEM with any pure document-frequency rule: in a corpus about cells, `cell`
    # (df=1439) is both frequent AND the single most informative term. Frequency alone cannot
    # separate `people` from `cell`. So DF is retained as a REPORTED statistic only, never as a
    # gate.
    #
    # THE GATE that survives both objections is PAIR-LEVEL and calibrated against the gate the
    # project already accepts. The closed-class lexicon is the operational definition of "a word
    # that says nothing"; so measure the PMI that a TYPICAL FUNCTION WORD has with these
    # subjects, and refuse any object that is no more informative about its subject than that.
    # The floor is therefore READ OFF the existing gate, not invented. Measured on the live
    # corpus: closed-class reference PMI p50=0.96, p75=2.10, p90=3.33 -> the p75 floor of 2.10
    # removes all 20 `X -> people` facts while leaving every known-meaningful pair intact
    # (primer/polymerase 9.1, aorta/artery 9.8, nephron/kidney 8.7, cholesterol/lipid 6.2).
    counts = sorted(df.values())
    df_report_thresh = counts[int(0.995 * (len(counts) - 1))] if counts else 1
    excluded = sorted(w for w, c in df.items()
                      if c >= df_report_thresh and not is_closed_class(w))
    prof = InformationProfile(n_docs=n_docs, df=dict(df), pair_df=dict(pair_df),
                              df_threshold=df_report_thresh,
                              calibration_lemma="<df is REPORTED ONLY, never gated>",
                              excluded_open_class=excluded)
    prof.pmi_floor, prof.pmi_calibration = _calibrate_pmi_floor(prof)
    return prof


def _calibrate_pmi_floor(prof: "InformationProfile", *, percentile: float = 75.0,
                         n_subjects: int = 400, n_objects: int = 12,
                         seed: int = 7) -> Tuple[float, dict]:
    """Read the low-information floor off the CLOSED-CLASS gate: sample (content-word subject,
    function-word object) pairs, and take the `percentile` of their PMI. An object no more
    informative about its subject than a function word is, is contentless by the project's own
    already-accepted standard."""
    import random as _random
    rng = _random.Random(seed)
    subjects = sorted(w for w, c in prof.df.items()
                      if not is_closed_class(w) and c >= 4)
    objects = sorted(w for w, c in prof.df.items() if is_closed_class(w) and c >= 20)
    if not subjects or not objects:
        return 0.0, {"status": "UNCALIBRATED_no_closed_class_observed", "floor": 0.0}
    if len(subjects) > n_subjects:
        subjects = rng.sample(subjects, n_subjects)
    vals: List[float] = []
    for s in subjects:
        for o in rng.sample(objects, min(n_objects, len(objects))):
            v = prof.pmi(s, o)
            if v != float("-inf") and v == v:
                vals.append(v)
    if not vals:
        return 0.0, {"status": "UNCALIBRATED_no_finite_pmi", "floor": 0.0}
    vals.sort()
    idx = min(len(vals) - 1, int(percentile / 100.0 * (len(vals) - 1)))
    floor = vals[idx]
    return floor, {"status": "CALIBRATED_ON_CLOSED_CLASS_REFERENCE",
                   "percentile": percentile, "n_reference_pairs": len(vals),
                   "reference_pmi_p50": round(vals[len(vals) // 2], 4),
                   "floor": round(floor, 4)}


# -------------------------------------------------------------------------------------------

def _self_test() -> None:
    # A synthetic corpus where `thing` is deliberately flat (occurs in every doc) and `nephron`
    # is informative (occurs only with `kidney`).
    docs: List[List[str]] = []
    for i in range(200):
        docs.append(["thing", "the", "of", f"topic{i % 40}"])
    for _ in range(12):
        docs.append(["nephron", "kidney", "filter", "thing", "the", "of"])
    prof = build_profile(docs)
    assert prof.n_docs == 212
    assert prof.pmi_calibration["status"].startswith("CALIBRATED"), prof.pmi_calibration
    # PMI: nephron/kidney always co-occur -> strongly positive; nephron/thing -> not informative
    assert prof.pmi("nephron", "kidney") > 1.0, prof.pmi("nephron", "kidney")
    ok, reason = prof.eligible_meaning("nephron", "kidney")
    assert ok and reason is None, (ok, reason)
    ok, reason = prof.eligible_meaning("nephron", "thing")
    assert not ok, (ok, reason, prof.pmi("nephron", "thing"), prof.pmi_floor)
    # a never-co-occurring pair is refused
    ok, reason = prof.eligible_meaning("nephron", "topic3")
    assert not ok and reason == "NEVER_CO_OCCURS", (ok, reason)
    print("[low_information_filter] self-test PASS  pmi_floor=%.4f %s"
          % (prof.pmi_floor, prof.pmi_calibration["status"]))


if __name__ == "__main__":
    _self_test()
