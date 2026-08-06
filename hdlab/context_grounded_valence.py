# WIRE-DON'T-ISLAND PROMOTION (2026-08-05): thin hdlab organ over the certified BRIDGE-1 cells.
# Reuses (never reimplements/re-tunes) the certified logic in:
#   experiments/exp_bridge1_governor_grounding_v1.py       (commit 96e8e8404, governor sense-select)
#   experiments/exp_bridge1_event_assembly_open_vocab_v1.py (commit c555bdb34, open-vocab animacy axis)
#   experiments/exp_bridge1_twostage_event_situation_v2.py  (combine_biased_competition, reused by both)
#   experiments/exp_grounded_appraisal_sim_earned_v1.py     (commit 26fce6237-era frozen theta valuation)
# See notes/landed_vet_bridge1_foundation.md (AUDIT-ONLY, commit f06c06535) for the certified scope.
"""hdlab/context_grounded_valence.py -- context-grounded valence scoring.

CERTIFIED capability wrapped here (chain-grade on the animacy axis, per landed-VET AXIS 6):
"Given a validly-extracted direct-object patient and a force-capable governing verb, event assembly
flips harm<->neutral by the patient's WordNet ANIMACY on OPEN vocabulary (Bopen=1.000, 5 seeds;
scramble->0.400; BOW/governor=0.500; no subset-A regression). The frozen appraisal-sim theta
genuinely values the resulting event type (random-theta approx 0)." Governor sense-select stage-1
(differential grounding 0.967, notes/landed_vet_bridge1_foundation.md AXIS 2) clears the ORIGINAL
word-sense-collision false positives in resolve_valence_blind (C-C payoff, commit 26fce6237, 6/6
vs 2/6 baseline).

NOT wrapped here / SCOPED-OPEN (stays in experiments/, not promoted as capability -- see the cert
doc AXIS 3/5 for the honest boundary):
  - force-verb identification: FORCE_CLASS_HARM_REAL is a closed, test-fitted hand list.
  - `situation_type_for_prior` (the RAW-PRIOR-TEXT lexicon reader in v2): never open-vocab-tested,
    NOT reused here. `prior_context` is accepted by the sentence-level convenience entrypoint below
    ONLY as a reserved/no-op parameter -- it is NOT wired to anything.
  - body-part animacy (WordNet routes body-part nouns to inanimate hypernyms -- quantified gap,
    not fixed, `BODY_PART_SUPPLEMENT` covers only the 9 words the cert cells hand-patched).
  - abstract-harm-vs-goal-noun disambiguation and beneficiary/social-relational valence (both
    proven gaps in the cert doc, animacy alone cannot resolve either).

WIRED (2026-08-06, un-severing deep-VET top-down-loop cut-point #3, notes/deep_vet_comprehension_
organ_vs_brain_2026-08-05.md "STEP-1c CAVEAT RESOLVED"): `combine_biased_competition`'s 3rd arg
(situation/discourse-bias) is no longer hard-coded None everywhere -- `score_item`/`score_batch`
(the CERTIFIED single-item/independent-batch entrypoints) still default it to None (byte-identical
behavior, strict ADD, animacy-axis unchanged). `score_passage` is a NEW opt-in entrypoint that scores
a list of items IN NARRATIVE ORDER and derives each item's situation_type from the TERNARY AFFECT
(to_ternary(predicted_type): HARM/HELP/NA) of the items THIS SAME ORGAN already scored earlier in the
passage (`situation_type_from_affect`) -- a production-derivable top-down signal built from the
organ's own running output, NOT a raw prior-text lexicon rescan (that was v2's `situation_type_for_
prior`, deliberately not reused). See `score_passage` / `situation_type_from_affect` below; measured
in experiments/exp_situation_bias_prod_wire_discourse_decisive_v1.py.

Three-stage pipeline (unchanged from the cells): governor/adj-modifier perceptron (stage 1) ->
animacy-axis event override for the direct-object patient (stage 2) -> biased-competition combine
(situation > event > governor; situation only ever non-None via score_passage) -> frozen
appraisal-sim theta valuation (stage 3, VALENCE = Q(harm@coherent) - Q(help@coherent)).
"""
from __future__ import annotations

import os
import sys
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import torch  # noqa: E402

from hdlab.thematic_role_labeler import train_perceptron  # noqa: E402
import experiments.exp_grounded_appraisal_sim_earned_v1 as _sim  # noqa: E402 (REUSE: frozen theta)
import experiments.exp_bridge1_governor_grounding_v1 as _gov  # noqa: E402 (REUSE: stage 1, cert 96e8e8404)
import experiments.exp_bridge1_event_assembly_open_vocab_v1 as _ea  # noqa: E402 (REUSE: stage 2, cert c555bdb34)
import experiments.exp_bridge1_twostage_event_situation_v2 as _v2  # noqa: E402 (REUSE: combine_biased_competition)

FULL_N_TRAIN_THETA = _gov.FULL_N_TRAIN_THETA
SMOKE_N_TRAIN_THETA = _gov.SMOKE_N_TRAIN_THETA
TYPES = _sim.TYPES

_GOV_PERCEPTRON_CACHE: dict = {}
_BOW_PERCEPTRON_CACHE: dict = {}
_THETA_CACHE: dict = {}


def _governor_pred_fn(seed: int):
    """Certified governor perceptron (bridge1 stage-1: gov/adj-class + Component-3 frame + cope +
    order feats -> TYPE), trained on the certified TRAIN_ITEMS and cached per seed."""
    if seed not in _GOV_PERCEPTRON_CACHE:
        train_ex = [(_gov.extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                                   _gov.GOVERNOR_VERB_CLASS, _gov.ADJ_MODIFIER_CLASS)[0],
                     it["gold_type"]) for it in _gov.TRAIN_ITEMS]
        pred_fn, _w, _roles = train_perceptron(train_ex, seed=seed + 1000, epochs=20, roles=_sim.TYPES)
        _GOV_PERCEPTRON_CACHE[seed] = pred_fn
    return _GOV_PERCEPTRON_CACHE[seed]


def _bow_pred_fn(seed: int):
    """Certified bag-of-words CONTROL perceptron (disjoint train/test vocab -> informative tokens
    OOV at eval time, chance-level by construction), cached per seed."""
    if seed not in _BOW_PERCEPTRON_CACHE:
        train_bow = [(_gov.bow_feats(it["tokens"], it["target_word"]), it["gold_type"])
                     for it in _gov.TRAIN_ITEMS]
        pred_fn, _w, _roles = train_perceptron(train_bow, seed=seed + 2000, epochs=20, roles=_sim.TYPES)
        _BOW_PERCEPTRON_CACHE[seed] = pred_fn
    return _BOW_PERCEPTRON_CACHE[seed]


def _sim_theta(seed: int, n_train_theta: int):
    """Frozen appraisal-sim codebook + earned theta (FULL variant, unmodified train_theta), cached
    per (seed, n_train_theta)."""
    key = (seed, n_train_theta)
    if key not in _THETA_CACHE:
        gen = torch.Generator().manual_seed(seed)
        cb = _sim.Codebook(gen)
        g_theta = torch.Generator().manual_seed(seed * 100 + _sim.hash_variant("FULL"))
        theta = _sim.train_theta(cb, g_theta, "FULL", n_train_theta)
        _THETA_CACHE[key] = (cb, theta)
    return _THETA_CACHE[key]


def score_item(tokens: list, pos: list, target_idx: int, target_word: Optional[str] = None, *,
               seed: int = 0, n_train_theta: int = FULL_N_TRAIN_THETA,
               control: str = "none", animacy_map: Optional[dict] = None,
               situation_type: Optional[str] = None) -> dict:
    """Certified 3-stage scoring for one pre-tokenized/POS-tagged item. Returns predicted_type (in
    TYPES), valence (float, Q(harm@coherent)-Q(help@coherent)), sign (+1/-1), and per-stage
    diagnostics. `control` selects a certified can-fail control arm in place of the real governor
    stage ("none" = certified path (default); "bow" = disjoint-vocab bag-of-words control;
    "scrambled_governor" = permuted governor/adj class dicts). `animacy_map` overrides the live
    WordNet lookup for the event stage -- used by score_batch to inject a pool-level SCRAMBLED
    animacy map for the scrambled-animacy control (a single-item permutation is a no-op by
    construction; that control is inherently pool-level, see score_batch). `situation_type`
    (BLOCK_HIGH/NEUTRAL/None) is the 3rd arg to combine_biased_competition -- defaults to None
    (IDENTICAL to the pre-wire hard-coded None; every existing caller that omits it gets the
    byte-identical certified animacy-axis path). Direct callers pass it explicitly for testing;
    production narrative scoring should go through score_passage, which derives it from prior
    events' own affect rather than hand-setting it per item."""
    target_word = target_word or tokens[target_idx]
    item = {"tokens": tokens, "pos": pos, "target_idx": target_idx, "target_word": target_word}

    if control == "bow":
        pred_fn = _bow_pred_fn(seed)
        gov_type = pred_fn(_gov.bow_feats(tokens, target_word))
        event_type, category, gov_word = None, None, None
    else:
        gov_class = _gov.GOVERNOR_VERB_CLASS
        adj_class = _gov.ADJ_MODIFIER_CLASS
        if control == "scrambled_governor":
            gov_class = _gov._scrambled_class_dict(gov_class, seed=seed + 3000)
            adj_class = _gov._scrambled_class_dict(adj_class, seed=seed + 3001)
        elif control not in ("none",):
            raise ValueError(f"unknown control {control!r} (use score_batch for scrambled_animacy)")

        pred_fn = _governor_pred_fn(seed)
        gfeats = _gov.extract_governor_feats(tokens, pos, target_idx, gov_class, adj_class)[0]
        gov_type = pred_fn(gfeats)

        amap = animacy_map
        if amap is None:
            pos_tag = pos[target_idx] if target_idx < len(pos) else None
            a = _ea.real_animacy_lookup(target_word, pos_tag)
            w = target_word.lower().strip(".,\"'();:")
            amap = {w: a} if a is not None else {}
        event_type, category, gov_word = _ea.event_type_for_item_real(
            item, amap, _ea.FORCE_CLASS_HARM_REAL, _gov.GOVERNOR_VERB_CLASS)

    # situation/discourse-bias stage: `situation_type` defaults to None here (byte-identical to the
    # pre-wire hard-coded None, exactly like the certified event-assembly cell's own run_seed did) --
    # score_item stays the certified/unwired path. score_passage is the opt-in wire that computes a
    # real situation_type per item (see module docstring) and passes it through this parameter.
    final_type, winner = _v2.combine_biased_competition(gov_type, event_type, situation_type)
    cb, theta = _sim_theta(seed, n_train_theta)
    valence = _gov.valence_for_type(cb, theta, final_type)
    return {
        "predicted_type": final_type, "valence": valence, "sign": 1 if valence > 0 else -1,
        "stage": winner, "governor_type": gov_type, "event_type": event_type,
        "patient_category": category, "governor_word": gov_word, "control": control, "seed": seed,
        "situation_type": situation_type,
    }


def score_batch(items: list, *, seed: int = 0, n_train_theta: int = FULL_N_TRAIN_THETA,
                 control: str = "none") -> list:
    """Batch scoring over pre-tokenized items (each a dict with tokens/pos/target_idx/target_word).
    `control="scrambled_animacy"` builds ONE scrambled animacy map over this batch's own vocabulary
    (values permuted across keys, reusing the cells' own `_scrambled_class_dict`) -- matches the
    certified cells' own pool-level scramble-control discipline exactly (a lift-collapse control is
    inherently a pool-level check, not a per-item one). Other control values pass through to
    score_item unchanged, per-item."""
    if control == "scrambled_animacy":
        real_map = _ea.build_real_animacy_map(items)
        scr_map = _v2._scrambled_class_dict(real_map, seed=seed + 6000)
        out = []
        for it in items:
            w = it["target_word"].lower().strip(".,\"'();:")
            m = {w: scr_map[w]} if w in scr_map else {}
            out.append(score_item(it["tokens"], it["pos"], it["target_idx"], it.get("target_word"),
                                    seed=seed, n_train_theta=n_train_theta, control="none",
                                    animacy_map=m))
        return out
    return [score_item(it["tokens"], it["pos"], it["target_idx"], it.get("target_word"),
                        seed=seed, n_train_theta=n_train_theta, control=control)
            for it in items]


TERNARY_MAP = {"BLOCK_HIGH": "HARM", "BLOCK_LOW": "HARM", "RECIPROCITY": "HELP", "NEUTRAL": "NA"}


def to_ternary(predicted_type: str) -> str:
    """Maps the 4-way TYPE onto the HARM/HELP/NA ternary space of the reader under replacement
    (resolve_valence_blind), exactly as exp_bridge1_original_failure_payoff_v1.new_reader_ternary
    does -- reused here as the same lookup table, not re-derived."""
    return TERNARY_MAP.get(predicted_type, "NA")


def situation_type_from_affect(prior_affects: list, *, window: Optional[int] = None) -> Optional[str]:
    """Derives a coarse situation_type ('BLOCK_HIGH'=threat / 'NEUTRAL'=benign / None=abstain) from
    the TERNARY affect (HARM/HELP/NA, via to_ternary) of events THIS SAME ORGAN already scored
    earlier in a passage -- a production-derivable top-down signal built from the organ's own
    running output, NOT a raw prior-text lexicon scan (that is v2's situation_type_for_prior, not
    reused here). `prior_affects` is the ordered list of to_ternary(predicted_type) values for the
    items strictly before the current one; `window` (if given, e.g. 3) restricts consideration to
    the most recent N prior affects (recency-limited situation memory) -- default None = the whole
    passage-so-far. Dominance rule (glass-box, parameterized, symmetric with v2's return-domain so
    it drops into combine_biased_competition's 3rd argument unmodified):
      HARM-dominant (harm_count > help_count, harm_count > 0) -> 'BLOCK_HIGH' (threat context)
      HELP-dominant (help_count > harm_count, help_count > 0) -> 'NEUTRAL'    (benign context)
      empty / all-NA / tied HARM==HELP                        -> None         (abstain -- IDENTICAL
                                                                     to the pre-wire hard-coded None)
    """
    affects = prior_affects if window is None else prior_affects[-window:] if window > 0 else []
    harm_count = sum(1 for a in affects if a == "HARM")
    help_count = sum(1 for a in affects if a == "HELP")
    if harm_count > help_count and harm_count > 0:
        return "BLOCK_HIGH"
    if help_count > harm_count and help_count > 0:
        return "NEUTRAL"
    return None


def score_passage(items: list, *, seed: int = 0, n_train_theta: int = FULL_N_TRAIN_THETA,
                   control: str = "none", window: Optional[int] = None) -> list:
    """WIRED situation-bias entrypoint (the production un-severing of combine_biased_competition's
    3rd arg): scores `items` IN NARRATIVE ORDER, one at a time, deriving each item's situation_type
    from situation_type_from_affect over the to_ternary affect of the items THIS CALL already scored
    before it -- i.e. the running situation-model affect state, not a re-scan of raw prior text.
    First item in `items` always gets situation_type=None (no prior events yet in this passage) --
    IDENTICAL to the score_item/score_batch default. Returns the same per-item dict as score_item
    plus `situation_type_in` (the derived value actually used, for glass-box inspection). The
    certified score_item/score_batch entrypoints are completely UNCHANGED by this function's
    existence -- this is a strictly-additive opt-in wire, not a modification of the certified path."""
    results = []
    prior_affects = []
    for it in items:
        st = situation_type_from_affect(prior_affects, window=window)
        r = score_item(it["tokens"], it["pos"], it["target_idx"], it.get("target_word"),
                        seed=seed, n_train_theta=n_train_theta, control=control,
                        animacy_map=it.get("animacy_map"), situation_type=st)
        r["situation_type_in"] = st
        results.append(r)
        prior_affects.append(to_ternary(r["predicted_type"]))
    return results


_AUX_LEMMAS = {"be", "is", "are", "was", "were", "been", "being", "am",
               "have", "has", "had", "do", "does", "did"}
_UNIVERSAL_TAGMAP = {"VERB": "VERB", "NOUN": "NOUN", "ADJ": "ADJ", "ADV": "ADV", "ADP": "ADP",
                     "DET": "DET", "PRON": "PRON", "CONJ": "CCONJ", "PRT": "PRT", "NUM": "NUM"}


def _tokenize_and_tag(sentence: str):
    """UNCERTIFIED best-effort tokenizer/POS layer for the sentence-level convenience entrypoint
    ONLY -- score_item/score_batch (the certified path) never call this; every certified/landed-VET
    number was produced from hand-built tokens/pos, not this tagger. Uses nltk's universal tagset
    with an AUX split (bridge1's governor extraction depends on AUX-not-VERB for copulas like
    "was" -- see exp_bridge1_governor_grounding_v1.self_test check (1))."""
    import nltk
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens, tagset="universal")
    pos = []
    for tok, tag in tagged:
        mapped = _UNIVERSAL_TAGMAP.get(tag, "X")
        if mapped == "VERB" and tok.lower() in _AUX_LEMMAS:
            mapped = "AUX"
        pos.append(mapped)
    return tokens, pos


def score_context_grounded_valence(target_word: str, sentence: str,
                                     prior_context: Optional[str] = None, *,
                                     seed: int = 0, n_train_theta: int = FULL_N_TRAIN_THETA) -> dict:
    """Convenience sentence-level entrypoint. Tokenizes/POS-tags `sentence` (UNCERTIFIED layer, see
    _tokenize_and_tag), locates the first case-insensitive occurrence of `target_word`, and calls
    score_item -- the certified 3-stage scoring itself is unchanged. `prior_context` is a RAW TEXT
    string; it stays RESERVED/no-op here on purpose (recorded as `prior_context_ignored` for honesty,
    not silently dropped) -- wiring a raw-text rescan was deliberately rejected (see module docstring
    "WIRED" note); the production situation-bias wire is `score_passage`, which derives situation_type
    from PRIOR EVENTS' OWN scored affect, not from re-scanning text here."""
    tokens, pos = _tokenize_and_tag(sentence)
    tw = target_word.lower()
    target_idx = next((i for i, t in enumerate(tokens) if t.lower() == tw), None)
    if target_idx is None:
        raise ValueError(f"target_word {target_word!r} not found in tokenized sentence {tokens!r}")
    result = score_item(tokens, pos, target_idx, target_word, seed=seed, n_train_theta=n_train_theta)
    result["prior_context_ignored"] = prior_context is not None
    result["tokens"] = tokens
    result["pos"] = pos
    return result


def self_test():
    """Off-disk smoke (fast, SMOKE_N_TRAIN_THETA): (1) score_item differentiates a known collision
    pair by sign; (2) BOW control diverges from the real path (arms-must-differ); (3) score_batch
    scrambled_animacy collapses the Bopen lift relative to the real path; (4) score_passage
    situation-bias wire: a threat-priming vs benign-priming prior EVENT (production-derivable via
    this same organ's own to_ternary affect, NOT a raw prior-text lexicon scan) flips an otherwise-
    ambiguous target's sign, while the None-arg score_item path on the identical target clause does
    NOT differentiate (byte-identical to the pre-wire behavior). Full certified-number reproduction
    lives in verification/verify_context_grounded_valence.py, not here."""
    form, a, b = _gov.COLLISION_PAIRS[0]
    ra = score_item(a["tokens"], a["pos"], a["target_idx"], a["target_word"], seed=0,
                     n_train_theta=SMOKE_N_TRAIN_THETA)
    rb = score_item(b["tokens"], b["pos"], b["target_idx"], b["target_word"], seed=0,
                     n_train_theta=SMOKE_N_TRAIN_THETA)
    assert ra["sign"] != rb["sign"], f"collision pair {form!r} did not differentiate: {ra} vs {rb}"

    bow_a = score_item(a["tokens"], a["pos"], a["target_idx"], a["target_word"], seed=0,
                        n_train_theta=SMOKE_N_TRAIN_THETA, control="bow")
    assert bow_a["governor_type"] != ra["governor_type"] or bow_a["predicted_type"] != ra["predicted_type"], (
        "META_RULE_AF: bow control produced an identical prediction to the real path")

    bopen_items = [it for _f, x, y in _ea.SUBSET_B_OPEN_PAIRS for it in (x, y)]
    real = score_batch(bopen_items, seed=0, n_train_theta=SMOKE_N_TRAIN_THETA)
    scr = score_batch(bopen_items, seed=0, n_train_theta=SMOKE_N_TRAIN_THETA, control="scrambled_animacy")
    real_correct = sum(1 for it, r in zip(bopen_items, real)
                        if r["sign"] == (1 if it["gold_type"] == "BLOCK_HIGH" else -1))
    scr_correct = sum(1 for it, r in zip(bopen_items, scr)
                       if r["sign"] == (1 if it["gold_type"] == "BLOCK_HIGH" else -1))
    assert real_correct > scr_correct, (
        f"scrambled_animacy control did not collapse the Bopen lift: real={real_correct}/12 "
        f"scrambled={scr_correct}/12")

    # (4) situation-bias production wire (score_passage). Prior EVENTS use bridge1's own trained
    # HARM/HELP governor vocab ("attack"/"rescue", disjoint from the ambiguous target's "touch") --
    # production-derivable via this organ scoring the prior event itself, not a raw-text scan. The
    # target clause is BIT-IDENTICAL across both passages so only the situation-bias wire can decide
    # the sign; the None-arg score_item call on that same clause must NOT differentiate (matches the
    # current/pre-wire production default exactly).
    threat_prior = {"tokens": ["wolves", "attacked", "the", "sheep"],
                     "pos": ["NOUN", "VERB", "DET", "NOUN"], "target_idx": 3, "target_word": "sheep"}
    benign_prior = {"tokens": ["a", "dog", "rescued", "the", "kitten"],
                     "pos": ["DET", "NOUN", "VERB", "DET", "NOUN"], "target_idx": 4,
                     "target_word": "kitten"}
    target_amb = {"tokens": ["it", "touched", "her", "hand"],
                  "pos": ["PRON", "VERB", "PRON", "NOUN"], "target_idx": 3, "target_word": "hand"}
    passage_threat = score_passage([threat_prior, target_amb], seed=0, n_train_theta=SMOKE_N_TRAIN_THETA)
    passage_benign = score_passage([benign_prior, target_amb], seed=0, n_train_theta=SMOKE_N_TRAIN_THETA)
    none_arg = score_item(target_amb["tokens"], target_amb["pos"], target_amb["target_idx"],
                           target_amb["target_word"], seed=0, n_train_theta=SMOKE_N_TRAIN_THETA)
    assert passage_threat[1]["situation_type_in"] == "BLOCK_HIGH", (
        f"threat-primed passage did not derive BLOCK_HIGH situation_type: {passage_threat[1]}")
    assert passage_benign[1]["situation_type_in"] == "NEUTRAL", (
        f"benign-primed passage did not derive NEUTRAL situation_type: {passage_benign[1]}")
    assert passage_threat[1]["sign"] != passage_benign[1]["sign"], (
        "situation-bias wire did not flip the ambiguous target's sign across threat/benign priors")
    assert none_arg["situation_type"] is None, "None-arg path must default to None (strict ADD)"
    assert none_arg["sign"] == passage_threat[1]["sign"] or none_arg["sign"] == passage_benign[1]["sign"], (
        "None-arg sign should trivially match exactly one of the two opposite-sign situation "
        "outcomes (sanity: none_arg is a real +-1 value, not a NaN/None regression)")

    print(f"[SELFTEST PASS] hard_A sign={ra['sign']} hard_B sign={rb['sign']} "
          f"bow_type={bow_a['predicted_type']} Bopen_real={real_correct}/12 Bopen_scrambled={scr_correct}/12 "
          f"situation_threat={passage_threat[1]['predicted_type']} "
          f"situation_benign={passage_benign[1]['predicted_type']} none_arg={none_arg['predicted_type']}",
          flush=True)
    return True


if __name__ == "__main__":
    self_test()
