"""hdlab/word_acquisition_loop.py -- online grounded-word-acquisition loop, increment 1 (2026-08-06).

preregs/2026-08-06_grounded_word_acquisition_increment1_v1.md +
notes/drill_online_grounded_word_acquisition_loop_2026-08-06.md.

Closes audit gap #1 ("FEATURES: supplied vs LEARNED+GROUNDED") for ONE decision-relevant axis:
outcome-verb RESULT_VALENCE (POS/NEG). The substrate PROPOSES, CROSS-CHECKS, GROUNDS, and WRITES BACK
its own candidate outcome-verb polarity for genuinely novel words, with ZERO human seed-authoring for
the target words. This module is the ORCHESTRATION only; every load-bearing primitive is REUSED
verbatim from an already-validated organ (no reinvention):

  PROPOSE trigger        hdlab.predictive_coding.threshold_gate           (OOV residual gate)
  CHANNEL A (structural) hdlab.learner.registry.learn / apply             (MDL construction induction,
                         EXACT frame_induction.py pattern; the verb lemma is NEVER a feature)
  CHANNEL B (affective)  hdlab.goal_typing.goal_congruence_appraisal_type (NEW thin adapter, this arc)
                         -> context_grounded_valence.score_item situation_type path
                         -> FROZEN reward-trained appraisal theta: valence = Q(harm@coh)-Q(help@coh)
  CONSOLIDATE            exp_self_extension_loop_v1's MIN_CONFIRM>=2 signature-match rule
                         + hdlab.self_improving_loop.decide_keep_or_revert abstain-band gate
  WRITE-BACK             hdlab.verb_lexical_similarity.register_acquired_outcome  (Tier-3 overlay)

NO-CORNERS DISCIPLINE (the governing constraint): Channel B's POS/NEG vote is EARNED from the frozen
reward theta, NOT supplied. The adapter decides only the SITUATION STRUCTURE (goal-completing =
RECIPROCITY / goal-thwarting = BLOCK_HIGH) from argument structure + animacy; the VALENCE that turns
that structure into a POS/NEG vote is read from the theta the appraisal simulation EARNED from
simulated reward (no text). The target verb's own lexical identity is NEVER read by either channel; no
text co-occurrence statistic of the target word is read anywhere. Only RESULT_VALENCE is proposed
(domain/root-type are out of scope for increment 1).

Glass-box, no borrowed embedding, no external LLM. Deterministic integer seeds throughout.
"""
from __future__ import annotations

import os
import re
import sys
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# -- REUSED VERBATIM primitives -------------------------------------------------------------------
from hdlab import predictive_coding as _pc                       # PROPOSE trigger (residual gate)
from hdlab.learner import registry as _learner                   # CHANNEL A induction (MDL)
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # consolidation gate
from hdlab.thematic_role_labeler import lemma_verb               # glass-box lemmatizer (shared key)
from hdlab import verb_lexical_similarity as _vls                # Tier-2 base lexicon + Tier-3 write-back
from hdlab.goal_typing import (                                  # CHANNEL B adapter + shared parser
    goal_congruence_appraisal_type, _cb_analyze_outcome_clause,
)

MIN_CONFIRM = 2                     # exp_self_extension_loop_v1 propose-but-verify (>=2 confirmations)
PROPOSE_THRESHOLD = 0.25           # predictive_coding.threshold_gate residual threshold (OOV novelty)

CB_SEED = 0                        # frozen-theta seed (Channel B); deterministic


# =================================================================================================
# PROPOSE trigger -- reuse predictive_coding.threshold_gate as the OOV-novelty gate.
# =================================================================================================
def word_is_novel(lemma: str) -> bool:
    """A word is a mint CANDIDATE iff it is OOV of the Tier-2 base outcome lexicon (Tier-1 exact
    membership is a subset of that check for the outcome axis). Formalized via the SAME residual gate
    the substrate uses for novelty everywhere: observed demands an entry (all-ones); predicted can
    reconstruct it (all-ones) ONLY if the base lexicon already has it, else all-zeros -> residual=1.0
    -> gate fires. An in-lexicon word yields residual 0 -> gate skips -> never re-minted."""
    known = lemma in _vls.OUTCOME_VERB_FEATURES
    observed = np.ones(8, dtype=np.float64)
    predicted = np.ones(8, dtype=np.float64) if known else np.zeros(8, dtype=np.float64)
    decision = _pc.threshold_gate(observed, predicted, threshold=PROPOSE_THRESHOLD)
    return not decision.skipped


# =================================================================================================
# CHANNEL A -- structural / syntactic-bootstrapping construction-cue MDL induction.
# EXACT hdlab.frame_induction.py pattern: declare a boolean CONSTRUCTION-cue atom set, induce a
# construction->{POS,NEG} mapping via the centralized learner (config-only), and TRANSFER it to an
# unseen verb by CONSTRUCTION OVERLAP -- the verb lemma is NEVER a feature. Trained on the EXISTING
# OUTCOME_SEED_POS/OUTCOME_SEED_NEG verbs' OWN corpus sentential contexts (not the target word).
# =================================================================================================
CHANNEL_A_ATOMS = ["has_direct_object", "patient_np_present", "result_particle_present",
                   "subject_is_animate_agent"]


def channel_a_feats(sentence: str, target_word: str) -> Optional[List[str]]:
    """Construction-cue atom list for ONE (verb-occurrence) in `sentence`. Reuses the shared
    glass-box clause parser (goal_typing._cb_analyze_outcome_clause). NEVER contains the verb lemma.
    Returns None if the target verb is absent from the sentence."""
    clause = _cb_analyze_outcome_clause(sentence, lemma_verb(target_word))
    if clause is None:
        return None
    feats: List[str] = []
    if clause["has_direct_object"]:
        feats.append("has_direct_object")
    if clause["has_direct_object"] or clause["passive"]:      # a patient exists (DO or passive-subj)
        feats.append("patient_np_present")
    if clause["result_particle"]:
        feats.append("result_particle_present")
    if clause["animate_agent"]:
        feats.append("subject_is_animate_agent")
    return feats


def _clean_sentences(text: str) -> List[str]:
    parts = re.split(r"[.!?]+[\'\"’”]?", text)
    return [s.strip() for s in parts if s.strip()]


def mine_seed_episodes(corpus_paths: Sequence[str], max_per_seed: int = 6,
                       seed_shuffle: int = 0) -> List[dict]:
    """Mine construction-cue episodes for Channel A from the seed verbs' OWN corpus occurrences.
    For each corpus sentence, every token whose lemma matches a POS/NEG SEED verb yields one episode
    {feats, gold_class}. `max_per_seed` caps occurrences per seed lemma (class balance); order is made
    deterministic via a fixed-seed shuffle of a SORTED occurrence list (no hash()-seeding)."""
    pos_seeds = {lemma_verb(w): "POS" for w in _vls.OUTCOME_SEED_POS}
    neg_seeds = {lemma_verb(w): "NEG" for w in _vls.OUTCOME_SEED_NEG}
    seed_gold = {**pos_seeds, **neg_seeds}
    found: Dict[str, List[dict]] = {k: [] for k in seed_gold}
    for path in corpus_paths:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        for sent in _clean_sentences(text):
            toks = re.findall(r"[a-z']+", sent.lower())
            seen_here: set = set()
            for tok in toks:
                lem = lemma_verb(tok)
                if lem in seed_gold and lem not in seen_here:
                    seen_here.add(lem)
                    feats = channel_a_feats(sent, tok)
                    if feats is not None:
                        found[lem].append({"feats": feats, "gold_class": seed_gold[lem]})
    rng = np.random.default_rng(seed_shuffle)
    episodes: List[dict] = []
    for lem in sorted(found):
        occs = found[lem]
        if len(occs) > max_per_seed:
            idx = rng.permutation(len(occs))[:max_per_seed]
            occs = [occs[int(i)] for i in sorted(idx.tolist())]
        episodes.extend(occs)
    return episodes


def _key_fn(ep):
    return "|".join(sorted(ep["feats"]))


def _feat_fn(ep):
    return ep["feats"]


def _channel_a_spec():
    """MDL-auto-select spec over CHANNEL_A_ATOMS (mirrors frame_induction.default_spec: estimation +
    ruleind + proginduction; proginduction enumerates the boolean truth table over the atoms)."""
    classes = ["NEG", "POS"]
    return {
        "candidate_plugins": ["estimation", "ruleind", "proginduction"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl", "key_fn": _key_fn,
                           "label_fn": lambda ep: ep["gold_class"], "classes": list(classes)},
            "ruleind": {"max_conjunct": 2, "min_coverage": 2, "purity_thresh": 0.70,
                        "max_rules": 25, "key_fn": _key_fn},
            "proginduction": {"atoms": list(CHANNEL_A_ATOMS), "max_nodes": 9,
                              "label_fn": lambda ep: ep["gold_class"], "classes": list(classes)},
        },
    }


def train_channel_a(corpus_paths: Sequence[str], max_per_seed: int = 6, seed_shuffle: int = 0):
    """Induce the construction->polarity hypothesis. Returns (chosen_name, hypothesis, n_episodes)."""
    episodes = mine_seed_episodes(corpus_paths, max_per_seed=max_per_seed, seed_shuffle=seed_shuffle)
    if not episodes:
        return None, None, 0
    chosen_name, chosen, _all = _learner.learn(episodes, _feat_fn, _channel_a_spec())
    # the plugins' apply() consumes the glass-box hypothesis DICT (chosen.hypothesis), not the
    # LearnResult wrapper -- exact frame_induction.py convention (see its L392/L476).
    hypothesis = chosen.hypothesis if chosen is not None else None
    return chosen_name, hypothesis, len(episodes)


def channel_a_vote(chosen_name, hypothesis, feats: Optional[List[str]]) -> Optional[str]:
    """Predict POS/NEG (or None=abstain) for a construction-cue feature list via the induced
    hypothesis. NEVER consults the verb lemma. Abstain when the hypothesis abstains or feats is None
    (unlike frame_induction.predict_subj_role, this returns None rather than a forced default, so
    Channel A can genuinely abstain in the two-channel agreement)."""
    if hypothesis is None or feats is None:
        return None
    key = "|".join(sorted(feats))
    if chosen_name == "proginduction":
        from hdlab.learner.plugins import proginduction_plugin
        pred = proginduction_plugin.apply(hypothesis, list(feats))
    elif chosen_name == "ruleind":
        from hdlab.learner.plugins import ruleind_plugin
        pred = ruleind_plugin.apply(hypothesis, list(feats), key=key, default_class=None)
    elif chosen_name == "estimation":
        from hdlab.learner.plugins import estimation_plugin
        pred = estimation_plugin.apply(hypothesis, key)
    else:
        pred = None
    return pred if pred in ("POS", "NEG") else None


# =================================================================================================
# CHANNEL B -- affective / reward-grounded. situation_type from the goal-congruence adapter ->
# score_item's situation_type path -> valence read from the FROZEN reward-trained appraisal theta.
# =================================================================================================
def channel_b_valence_table(seed: int = CB_SEED, n_train_theta: Optional[int] = None) -> Dict[str, float]:
    """Read valence = Q(harm@coherent) - Q(help@coherent) from the FROZEN reward-trained theta for
    each situation type, THROUGH context_grounded_valence.score_item's situation_type parameter path
    (the pre-reg's named wire). Because combine_biased_competition lets a non-None situation_type
    DOMINATE the governor/event stages, the returned valence for a given type is identical across all
    clauses (clause-invariant) -- so it is computed once here on a canonical clause and reused. Asserts
    the EARNED sign relation (RECIPROCITY is help-valenced -> negative; BLOCK_HIGH is harm-valenced ->
    positive); a random (unearned) theta would NOT produce this separation."""
    import experiments.exp_bridge1_governor_grounding_v1 as _gov
    import hdlab.context_grounded_valence as _cgv
    n_train_theta = n_train_theta if n_train_theta is not None else _gov.FULL_N_TRAIN_THETA
    # canonical clause: content is irrelevant (situation_type dominates); a valid tokenized item only.
    toks = ["she", "held", "the", "cup"]
    pos = ["PRON", "VERB", "DET", "NOUN"]
    table = {}
    for stype in ("RECIPROCITY", "BLOCK_HIGH"):
        r = _cgv.score_item(toks, pos, 3, "cup", seed=seed, n_train_theta=n_train_theta,
                            situation_type=stype)
        assert r["situation_type"] == stype and r["stage"] == "situation", (
            f"situation_type path did not dominate for {stype}: {r}")
        table[stype] = float(r["valence"])
    assert table["RECIPROCITY"] < 0.0 < table["BLOCK_HIGH"], (
        f"EARNED-THETA SIGN VIOLATION: expected valence(RECIPROCITY)<0<valence(BLOCK_HIGH), "
        f"got {table} -- theta is not the reward-earned one (a random theta gives ~0).")
    return table


def channel_b_vote(goal_sentences, sentence: str, target_word: str,
                   valence_table: Dict[str, float]) -> Optional[str]:
    """Channel B's POS/NEG vote (or None=abstain). The situation TYPE is a structural goal-congruence
    judgment (goal_congruence_appraisal_type, no verb identity); the VALENCE that signs it into POS/NEG
    is EARNED from the frozen reward theta (valence_table). POS iff the earned valence is help-valenced
    (< 0), NEG iff harm-valenced (> 0)."""
    stype = goal_congruence_appraisal_type(goal_sentences, sentence, target_word)
    if stype is None:
        return None
    valence = valence_table[stype]
    return "POS" if valence < 0 else "NEG"


# =================================================================================================
# COMBINE + CONSOLIDATE (propose-but-verify, MIN_CONFIRM>=2 + abstain-band gate).
# =================================================================================================
def combine_votes(a: Optional[str], b: Optional[str]) -> Optional[str]:
    """STRICT two-channel agreement (the COMBINED/production rule, per the pre-reg anti-drift gate):
    both channels must produce the SAME NON-ABSTAIN vote, else None. A single channel abstaining ->
    None (it does NOT let the other channel drive the write-back -- that is what makes the two-channel
    agreement a genuine anti-drift gate). The ablation arms do NOT use this function; run_acquisition
    selects the single-channel vote directly for channel_A_only / channel_B_only."""
    if a is not None and a == b:
        return a
    return None


def consolidate(word_votes: Dict[str, List[Optional[str]]],
                min_confirm: int = MIN_CONFIRM) -> Dict[str, dict]:
    """Promote a word's polarity iff (1) the word is a novel mint candidate (predictive_coding OOV
    gate), (2) the SAME polarity recurs across >= min_confirm occurrences, and (3) the abstain-band
    controller (self_improving_loop.decide_keep_or_revert) adopts the aggregate agreement margin.
    Returns {lemma: {"polarity", "n_confirm", "margin"}} for the consolidated words only."""
    acquired: Dict[str, dict] = {}
    for lemma in sorted(word_votes):
        if not word_is_novel(lemma):
            continue
        votes = word_votes[lemma]
        counts = {"POS": 0, "NEG": 0}
        for v in votes:
            if v in counts:
                counts[v] += 1
        top = "POS" if counts["POS"] >= counts["NEG"] else "NEG"
        other = "NEG" if top == "POS" else "POS"
        if counts[top] < min_confirm:
            continue
        margin = (counts[top] - counts[other]) / max(1, len(votes))   # net agreement margin
        adopt = decide_keep_or_revert({top: margin}, abstain_band=ABSTAIN_BAND_DEFAULT)
        if adopt == top:
            acquired[lemma] = {"polarity": top, "n_confirm": counts[top], "margin": round(margin, 4)}
    return acquired


# =================================================================================================
# End-to-end per-arm acquisition. `occurrences` = list of dicts:
#   {"word": <target surface>, "goal_sentences": [...], "sentence": <str>}   (>=1 per target word)
# `arm` in {"combined", "channel_A_only", "channel_B_only"}.
# =================================================================================================
def run_acquisition(occurrences: List[dict], chosen_name, hypothesis,
                    valence_table: Dict[str, float], arm: str = "combined",
                    vote_override=None) -> Tuple[Dict[str, dict], List[dict]]:
    """Run PROPOSE/vote for every occurrence, group by lemma, and CONSOLIDATE. `vote_override`, if
    given, is a callable(lemma, occ_index) -> (a_vote, b_vote) used ONLY by the scramble control to
    inject permuted per-word votes. Returns (acquired dict, per-occurrence trace)."""
    per_lemma: Dict[str, List[Optional[str]]] = {}
    trace: List[dict] = []
    lemma_occ_counter: Dict[str, int] = {}
    for occ in occurrences:
        word = occ["word"]
        lemma = lemma_verb(word)
        gs = occ.get("goal_sentences", [])
        sent = occ["sentence"]
        oi = lemma_occ_counter.get(lemma, 0)
        lemma_occ_counter[lemma] = oi + 1
        if vote_override is not None:
            a_vote, b_vote = vote_override(lemma, oi)
        else:
            a_vote = channel_a_vote(chosen_name, hypothesis, channel_a_feats(sent, word))
            b_vote = channel_b_vote(gs, sent, word, valence_table)
        if arm == "channel_A_only":
            combined = a_vote
        elif arm == "channel_B_only":
            combined = b_vote
        else:
            combined = combine_votes(a_vote, b_vote)   # STRICT agreement (production write-back)
        per_lemma.setdefault(lemma, []).append(combined)
        trace.append({"word": word, "lemma": lemma, "channel_a": a_vote, "channel_b": b_vote,
                      "combined": combined, "arm": arm})
    acquired = consolidate(per_lemma)
    return acquired, trace


def apply_acquired(acquired: Dict[str, dict]) -> None:
    """Write consolidated entries into the Tier-3 overlay (production write-back). Clears first so a
    re-run is idempotent."""
    _vls.clear_acquired_outcome()
    for lemma, info in acquired.items():
        _vls.register_acquired_outcome(lemma, info["polarity"])


def self_test() -> dict:
    """Fast off-disk gate: (1) PROPOSE gate fires on OOV, skips on in-lexicon; (2) Channel B earned
    sign relation holds (RECIPROCITY<0<BLOCK_HIGH); (3) combine_votes agreement/ablation semantics;
    (4) consolidate needs MIN_CONFIRM agreeing votes; (5) end-to-end catch acquisition writes a Tier-3
    entry that types MET, and clears cleanly (strict-ADD hygiene)."""
    assert word_is_novel("catch") and word_is_novel("wast")
    assert not word_is_novel("win") and not word_is_novel("fall")   # base-lexicon members
    vt = channel_b_valence_table()
    assert vt["RECIPROCITY"] < 0.0 < vt["BLOCK_HIGH"]
    assert combine_votes("POS", "POS") == "POS"
    assert combine_votes("POS", "NEG") is None
    assert combine_votes("POS", None) is None and combine_votes(None, "NEG") is None  # STRICT agree
    assert consolidate({"catch": ["POS", "POS"]}) == {
        "catch": {"polarity": "POS", "n_confirm": 2, "margin": 1.0}}
    assert consolidate({"catch": ["POS", None]}) == {}       # < MIN_CONFIRM
    assert consolidate({"catch": ["POS", "NEG"]}) == {}       # disagreement -> None each -> no confirm
    # end-to-end write-back + production typing
    _vls.clear_acquired_outcome()
    _vls.register_acquired_outcome("catch", "POS")
    from hdlab.goal_typing import lexicon_predict
    verdict = lexicon_predict("The rat stole out, and she jumped at it and caught it.")
    _vls.clear_acquired_outcome()
    assert verdict == "MET", f"acquired catch did not type MET via production lexicon_predict: {verdict}"
    assert lexicon_predict("The rat stole out, and she jumped at it and caught it.") == "NONE", (
        "clear_acquired_outcome did not restore the fall-through NONE baseline")
    return {"channel_b_valence_table": {k: round(v, 4) for k, v in vt.items()},
            "propose_gate_ok": True, "consolidate_ok": True, "end_to_end_catch_met": True}


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2))
    print("ALL SELF-TESTS PASSED")
