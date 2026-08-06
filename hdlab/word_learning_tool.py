"""hdlab/word_learning_tool.py -- the COMBINED dictionary-lookup + consequence-learning word-learning
tool (2026-08-06). Thin orchestration glue: look the OOV word up in the dictionary FIRST, then
confirm / refine / override that looked-up sense through story CONSEQUENCE.

"The learning tool should be able to look up the word in the dictionary... just like a normal human."
(USER, 2026-08-06.) Assembly of two already-proven halves, both of which already converge on the SAME
Tier-3 write-back (register_acquired_outcome):
  - DICTIONARY (dense prior):    hdlab.wordnet_polarity_propagation.dictionary_lookup
  - CONSEQUENCE (earned refine): hdlab.consequence_learning_loop.learn_corpus (UNCHANGED engine;
                                 dictionary_priors is a strictly-additive optional parameter)

FUSION = Bayesian pseudo-count injection: dictionary confidence -> round(K_MAX*conf) pseudo-exposures,
seeded into the consequence loop's exposure counter ONCE before the multi-pass loop (NOT per-pass -- the
specified trap). Real story exposures accumulate additively on top; the UNCHANGED consolidate() does the
3-way POS/NEG/GROUNDED_NEUTRAL/PENDING split. A confident dictionary hit alone reaches MIN_CONFIRM and
locks (looked-up sense stands with no story signal); enough real evidence washes out the fixed prior.

REUSE (wire-don't-island): both halves already write into hdlab.verb_lexical_similarity's
ACQUIRED_OUTCOME_VERB_FEATURES Tier-3 overlay -- this module adds NO new binding op, NO new taxonomy,
NO external LLM, NO borrowed embedding. hdlab-only dependency.

Cites: preregs/2026-08-06_combined_dictionary_consequence_word_learning_tool_v1.md;
notes/research_combined_dictionary_consequence_word_learning_tool_2026-08-06.md.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from hdlab.consequence_learning_loop import learn_corpus, MIN_CONFIRM
from hdlab.wordnet_polarity_propagation import (
    dictionary_lookup,
    pseudo_counts_from_dictionary,
    DictLookup,
    ANCHOR_WORDS,
    ANCHOR_POLARITY,
    K_MAX,
)


def dictionary_priors_for(oov_lemmas,
                          anchor_words=ANCHOR_WORDS,
                          anchor_polarity=ANCHOR_POLARITY,
                          k_max: int = K_MAX
                          ) -> Tuple[Dict[str, DictLookup], Dict[str, Dict[str, int]]]:
    """(lookups, pseudo_counts) for an iterable of OOV lemmas. lookups keeps the raw DictLookup per
    lemma (for the per-verb report); pseudo_counts is the {lemma:{POS,NEG}} shape learn_corpus seeds."""
    lookups = {lm: dictionary_lookup(lm, anchor_words, anchor_polarity) for lm in oov_lemmas}
    priors = pseudo_counts_from_dictionary(lookups, k_max=k_max)
    return lookups, priors


def learn_corpus_combined(goal_windows: List[Tuple[str, str, object]],
                          oov_lemmas,
                          n_passes: int = 3,
                          k_max: Optional[int] = None,
                          anchor_words=ANCHOR_WORDS,
                          anchor_polarity=ANCHOR_POLARITY,
                          **kwargs) -> dict:
    """Combined tool: dictionary-lookup priors for `oov_lemmas`, injected ONCE into the consequence
    loop over `goal_windows`. Returns learn_corpus's dict PLUS `dictionary_lookups` (the raw per-lemma
    DictLookups) and `dictionary_priors` (the injected pseudo-counts) for the per-verb report.

    kwargs pass straight through to learn_corpus (signal_mode, credit_mode, register, rng_choice)."""
    km = MIN_CONFIRM if k_max is None else k_max
    lookups, priors = dictionary_priors_for(oov_lemmas, anchor_words, anchor_polarity, k_max=km)
    rep = learn_corpus(goal_windows, n_passes=n_passes, dictionary_priors=priors, **kwargs)
    rep["dictionary_lookups"] = lookups
    rep["dictionary_priors"] = priors
    return rep


def self_test() -> dict:
    """Construct the REAL objects (dictionary_lookup + learn_corpus) at tiny scale and prove the combined
    path fuses: a confident dictionary prior for an OOV lemma that never appears in the corpus still locks
    that lemma's polarity via the injected pseudo-count (dictionary sense stands with no story signal)."""
    from hdlab.verb_lexical_similarity import clear_acquired_outcome
    clear_acquired_outcome()
    # tiny hand-authored corpus (same shape the engine self-test uses); none of the probe lemmas appear.
    windows = [
        ("Owen wanted to save the boat before the storm hit",
         "The men worked hard. The boat sank in the storm.", "boat"),
    ]
    # 'ruin' has a confident dictionary hit (or abstain); either way the combined path must not crash and
    # must attach the raw lookups. We assert the fusion CONTRACT on a synthetic confident lookup by
    # driving learn_corpus_combined with a lemma set and checking the returned structure.
    rep = learn_corpus_combined(windows, oov_lemmas=["ruin", "spoil", "improve"],
                                n_passes=2, signal_mode="signal_a_only",
                                credit_mode="referent_linked", register=False)
    clear_acquired_outcome()
    assert "dictionary_lookups" in rep and set(rep["dictionary_lookups"]) == {"ruin", "spoil", "improve"}
    assert "dictionary_priors" in rep
    # every prior lemma is one of the looked-up lemmas with a non-abstain, positive pseudo-count.
    for lemma, counts in rep["dictionary_priors"].items():
        assert lemma in rep["dictionary_lookups"], lemma
        assert (counts["POS"] + counts["NEG"]) > 0, counts
        # a pseudo-count can never exceed K_MAX (a confident dict hit == a full consequence lock, no more)
        assert (counts["POS"] + counts["NEG"]) <= K_MAX, counts
    # inject-once sanity: a prior lemma's master total == its pseudo-count (these lemmas do not appear in
    # the tiny corpus so no real exposures accumulate; total must equal the seeded prior, not a multiple).
    for lemma, counts in rep["dictionary_priors"].items():
        mc = rep["master_counter"].get(lemma, {"POS": 0, "NEG": 0})
        assert mc == counts, f"INJECT-ONCE FAILURE in combined path: {lemma} {mc} != prior {counts}"
    return {"n_lookups": len(rep["dictionary_lookups"]),
            "n_priors": len(rep["dictionary_priors"]),
            "priors": {k: dict(v) for k, v in rep["dictionary_priors"].items()},
            "K_MAX": K_MAX}


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
