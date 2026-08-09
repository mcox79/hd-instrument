"""hdlab/result_type_induction.py (2026-08-09) -- Direction-B M2: LEARNED speech-act/RESULT-TYPE
classification via construction-cue features (hdlab.learner.registry.learn, per
hdlab/frame_induction.py's lemma-exclusion discipline), testing whether the COMMON COMPOSITIONAL
CORE of the DesireDB outcome residual GENERALIZES across surface forms (M1, idiom_grounding.py,
showed a 29-entry hand-authored idiom lexicon recovers 2/8 on the primary cohort but 0/37 on
breadth -- idioms are a non-compositional long-tail). See
notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md M2 +
experiments/exp_direction_b_M2_speechact_result_generalization_v1.py for the pre-registered gates.

RESULT-TYPES (5), each with a GROUNDED CUE-FEATURE definition (never the surface lemma of the
matched token -- this is what lets the induced hypothesis transfer to a HELD-OUT verb never seen
during training):
  REFUSAL -- a refusal-flavored communication/speech verb (say/decline/reply family, or a bare
             discourse-negation reply with no verb at all, "No."/"Uh. No."/"Never.").
  GRANT   -- a giving/granting/permission verb (give/offer/grant family), un-negated.
  BLOCK   -- the SAME giving/permission verb family, but under modal-negation ("would/could not").
  ACHIEVE -- an achievement/completion verb (achieve/finish/succeed family), un-negated.
  FAIL    -- the SAME achievement verb family, negated ("did not finish"), OR an inherently-
             negative failure lexeme (fail/lose family) on its own.

CONSTRUCTION ATOMS (7, boolean, computed over the WHOLE outcome SPAN -- DesireDB outcome text is
often a terse fragment with no clean single governing verb, e.g. "Uh. No.", so this is a span-level
scan, not a per-verb-occurrence episode like frame_induction.py's subject-role task):
  comm_verb, give_verb, achieve_verb, fail_verb -- verb-CLASS membership via a small (2-3 word)
    TRAIN-only exemplar pool, tested with hdlab.goal_achievement._pool_related's already-vetted
    technique (literal membership OR WordNet primary-sense-synonym-set overlap, computed directly
    on the raw inflected surface token -- nltk's wn.synsets()/morphy already normalizes inflection
    internally, MEASURED@this module's build: wn.synsets("told") resolves to tell's synsets without
    any separate lemmatizer). A held-out verb never in the seed pool can still fire the atom via
    genuine WordNet relatedness, not a literal lookup-table hit -- this is the mechanism the GATE-1
    held-out-surface-form test in the M2 cell measures.
  neg_present -- any clausal negator (hdlab.goal_typing.NEGATORS, which includes bare "no") or an
    n't-contraction, anywhere in the span.
  modal_neg   -- a modal auxiliary (would/could/can/will/might/should/must/shall) immediately
    followed (within 2 tokens) by a negator, OR a closed-class modal n't-contraction (wouldn't/
    couldn't/can't/won't/shouldn't/mightn't/mustn't/shan't) -- a single structural cue for
    "would not give"-style BLOCK constructions, distinguishing them from plain do-support negation.
  no_verb_class_cue -- True iff NONE of comm_verb/give_verb/achieve_verb/fail_verb fired. Added as
    an explicit POSITIVE atom (not "the absence of X") because hdlab.learner's ruleind plugin
    (experiments/exp_parser_ruleinduction_cls_ppattach_v1.induce_rules) searches conjunctions of
    PRESENT feature-value strings only -- it has no negated-feature primitive -- so "bare discourse
    negation, no verb at all" ("Uh. No.") needs its own positive marker to be inducible as
    {neg_present, no_verb_class_cue} -> REFUSAL.

CALIBRATION-HONESTY NOTE (measured, not hidden): the verb-class pools have KNOWN partial coverage
(e.g. "objected"/"awarded"/"provided"/"quit" do not fire their intended pool via WordNet primary-
sense overlap -- MEASURED@this session's design probe) and at least one KNOWN cross-pool polysemy
collision ("handed"'s primary WordNet sense pass.v.05 shares the lemma "reach" with achieve.v.01,
so "handed" spuriously also fires achieve_verb) -- consistent with this arc's repeated finding that
first/primary-sense WordNet grounding is noisy. Neither is patched away here (that would risk
p-hacking the atom set to the eval set); both are reported honestly in the M2 cell's metrics, and
decision-list matching (a rule's conjunct only needs to be a SUBSET of the fired features) is
naturally robust to the spurious extra achieve_verb hit alongside a correct give_verb hit.
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

from hdlab import goal_typing as _gt
from hdlab.learner import registry

RESULT_TYPES = ("REFUSAL", "GRANT", "BLOCK", "ACHIEVE", "FAIL")
RESULT_TYPE_POLARITY = {"REFUSAL": "NEG", "BLOCK": "NEG", "FAIL": "NEG", "GRANT": "POS", "ACHIEVE": "POS"}

COMM_POOL = ["say", "decline", "reply"]
GIVE_POOL = ["give", "offer", "grant"]
ACHIEVE_POOL = ["achieve", "finish", "succeed"]
FAIL_POOL = ["fail", "lose"]

MODAL_STEMS = {"would", "could", "can", "will", "might", "should", "must", "shall"}
MODAL_CONTRACTIONS = {"wouldn't", "couldn't", "can't", "won't", "shouldn't", "mightn't", "mustn't", "shan't"}

CONSTRUCTION_ATOMS = ["comm_verb", "give_verb", "achieve_verb", "fail_verb",
                       "neg_present", "modal_neg", "no_verb_class_cue"]


# ---------------------------------------------------------------------------------------------
# Standalone WordNet primary-sense pool-overlap check. Deliberately a SELF-CONTAINED copy of
# hdlab.goal_achievement._pool_related/_primary_synonyms (same technique, same already-vetted
# organ) rather than an import: hdlab.goal_achievement imports THIS module below (to build the
# resulttype-grounded utility channel), so importing goal_achievement from here would be circular.
# ---------------------------------------------------------------------------------------------
def _primary_synonyms(word: str, pos) -> frozenset:
    from nltk.corpus import wordnet as _wn
    syn = {word}
    syns = _wn.synsets(word, pos=pos)
    if syns:
        for l in syns[0].lemmas():
            syn.add(l.name().replace("_", " ").lower())
    return frozenset(syn)


def _pool_related(word: str, pool) -> bool:
    from nltk.corpus import wordnet as _wn
    if word in pool:
        return True
    for pos in (_wn.VERB, _wn.ADJ, _wn.NOUN):
        w_syn = _primary_synonyms(word, pos)
        for cand in pool:
            if w_syn & _primary_synonyms(cand, pos):
                return True
    return False


def _any_pool_hit(toks: List[str], pool: List[str]) -> bool:
    for t in toks:
        if not t.isalpha() or len(t) < 2:
            continue
        if _pool_related(t, pool):
            return True
    return False


def _neg_present(toks: List[str]) -> bool:
    return any(_gt._is_negator(t) for t in toks)


def _modal_neg(toks: List[str]) -> bool:
    for i, t in enumerate(toks):
        if t in MODAL_CONTRACTIONS:
            return True
        if t in MODAL_STEMS:
            for j in range(i + 1, min(len(toks), i + 3)):
                if _gt._is_negator(toks[j]):
                    return True
    return False


def span_feats(outcome: str) -> List[str]:
    """The 7 boolean CONSTRUCTION_ATOMS present in `outcome`. NEVER contains a verb lemma or any
    n-gram containing one -- construction-class + negation-structure shape only, so the induced
    hypothesis transfers to a verb never seen during training (frame_induction's discipline)."""
    toks = _gt._tokens(outcome)
    comm = _any_pool_hit(toks, COMM_POOL)
    give = _any_pool_hit(toks, GIVE_POOL)
    ach = _any_pool_hit(toks, ACHIEVE_POOL)
    fail = _any_pool_hit(toks, FAIL_POOL)
    feats = []
    if comm:
        feats.append("comm_verb")
    if give:
        feats.append("give_verb")
    if ach:
        feats.append("achieve_verb")
    if fail:
        feats.append("fail_verb")
    if _neg_present(toks):
        feats.append("neg_present")
    if _modal_neg(toks):
        feats.append("modal_neg")
    if not (comm or give or ach or fail):
        feats.append("no_verb_class_cue")
    return feats


def build_episode(outcome: str, gold_class: str, tag: str = "") -> dict:
    return {"feats": span_feats(outcome), "gold_class": gold_class, "tag": tag}


# ---------------------------------------------------------------------------------------------
# TRAIN / HELD-OUT surface-form banks. Anti-circular design (per the M2 task pre-reg): every
# HELD-OUT surface form (the 3rd tuple element, `tag`) is a DIFFERENT verb/phrase from every TRAIN
# tag -- verified by the module self-test's disjointness assertion below. TRAIN pool seed words
# (say/decline/reply, give/offer/grant, achieve/finish/succeed, fail/lose) never appear as a
# HELD-OUT tag.
# ---------------------------------------------------------------------------------------------
TRAIN_EXAMPLES: List[Tuple[str, str, str]] = [
    ("She asked him and he said no.", "REFUSAL", "say"),
    ("They asked for help but he said no again.", "REFUSAL", "say"),
    ("He declined immediately.", "REFUSAL", "decline"),
    ("She declined to join them.", "REFUSAL", "decline"),
    ("He replied no to the request.", "REFUSAL", "reply"),
    ("She asked and he simply replied no.", "REFUSAL", "reply"),
    ("No.", "REFUSAL", "bare_no"),
    ("Uh. No.", "REFUSAL", "bare_no"),
    ("She gave him the job.", "GRANT", "give"),
    ("They gave her the money she needed.", "GRANT", "give"),
    ("He offered her the position.", "GRANT", "offer"),
    ("She offered to help him move.", "GRANT", "offer"),
    ("The board granted his request.", "GRANT", "grant"),
    ("They granted her the extra time.", "GRANT", "grant"),
    ("He would not give her the money.", "BLOCK", "give_neg"),
    ("They would not give him a second chance.", "BLOCK", "give_neg"),
    ("She could not offer him the job.", "BLOCK", "offer_neg"),
    ("He would not offer any help.", "BLOCK", "offer_neg"),
    ("The board would not grant the request.", "BLOCK", "grant_neg"),
    ("They could not grant her more time.", "BLOCK", "grant_neg"),
    ("She achieved her goal.", "ACHIEVE", "achieve"),
    ("He finally achieved success.", "ACHIEVE", "achieve"),
    ("He finished the project.", "ACHIEVE", "finish"),
    ("She finished the race first.", "ACHIEVE", "finish"),
    ("They succeeded in the end.", "ACHIEVE", "succeed"),
    ("He succeeded at the task.", "ACHIEVE", "succeed"),
    ("She failed the exam.", "FAIL", "fail"),
    ("He failed to show up.", "FAIL", "fail"),
    ("He lost the game.", "FAIL", "lose"),
    ("She lost the competition.", "FAIL", "lose"),
    ("They did not achieve their goal.", "FAIL", "achieve_neg"),
    ("She did not finish the race.", "FAIL", "finish_neg"),
    ("He did not succeed in the attempt.", "FAIL", "succeed_neg"),
    ("They did not achieve what they wanted.", "FAIL", "achieve_neg"),
]

HELDOUT_EXAMPLES: List[Tuple[str, str, str]] = [
    ("So Jarrad calls and she told him no.", "REFUSAL", "told"),
    ("He asked but she answered no.", "REFUSAL", "answered"),
    ("They objected to the idea.", "REFUSAL", "objected"),
    ("He refused to come.", "REFUSAL", "refused"),
    ("He asked and she responded no.", "REFUSAL", "responded"),
    ("Never.", "REFUSAL", "never"),
    ("They handed her the keys.", "GRANT", "handed"),
    ("He permitted her to stay.", "GRANT", "permitted"),
    ("They allowed him to attend.", "GRANT", "allowed"),
    ("They awarded him the prize.", "GRANT", "awarded"),
    ("She provided him with the funds.", "GRANT", "provided"),
    ("They would not hand it over.", "BLOCK", "handed_neg"),
    ("He could not permit her to stay.", "BLOCK", "permitted_neg"),
    ("They would not allow him to leave.", "BLOCK", "allowed_neg"),
    ("They would not award her the prize.", "BLOCK", "awarded_neg"),
    ("He could not provide the funds.", "BLOCK", "provided_neg"),
    ("He completed the marathon.", "ACHIEVE", "completed"),
    ("She accomplished the task.", "ACHIEVE", "accomplished"),
    ("They won the competition.", "ACHIEVE", "won"),
    ("He reached the summit.", "ACHIEVE", "reached"),
    ("She did not complete the marathon.", "FAIL", "completed_neg"),
    ("They did not win the competition.", "FAIL", "won_neg"),
    ("He did not reach the goal.", "FAIL", "reached_neg"),
    ("She missed the deadline.", "FAIL", "missed"),
    ("He flunked the test.", "FAIL", "flunked"),
    ("He quit the team.", "FAIL", "quit"),
]


def default_spec(classes=RESULT_TYPES, atoms=None, max_nodes: int = 5) -> dict:
    """Hypothesis-space CONFIG: MDL-auto-select across estimation / ruleind / proginduction,
    mirroring hdlab.frame_induction.default_spec's structure exactly. `max_nodes=5` keeps
    proginduction's bounded truth-table enumeration fast at 7 atoms (MEASURED@this session's
    design probe: n_atoms=7,max_nodes=5 -> 0.26s enumeration; n_atoms=9,max_nodes=7 -> 91s -- the
    reason this module uses 7 atoms, not a larger set, per the compute-proportionality gate)."""
    atoms = list(atoms) if atoms is not None else list(CONSTRUCTION_ATOMS)
    classes = list(classes)

    def _key_fn(ep):
        return "|".join(sorted(ep["feats"]))

    return {
        "candidate_plugins": ["estimation", "ruleind", "proginduction"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl", "key_fn": _key_fn,
                           "label_fn": lambda ep: ep["gold_class"], "classes": classes},
            "ruleind": {"max_conjunct": 2, "min_coverage": 2, "purity_thresh": 0.75,
                        "max_rules": 25, "key_fn": _key_fn},
            "proginduction": {"atoms": atoms, "max_nodes": max_nodes,
                              "label_fn": lambda ep: ep["gold_class"], "classes": classes},
        },
    }


def induce(episodes: List[dict], spec: Optional[dict] = None):
    """Fit + MDL-auto-select. Returns (chosen_name, chosen_LearnResult_or_None, all_results)."""
    spec = spec or default_spec()
    return registry.learn(episodes, lambda ep: ep["feats"], spec)


def predict(chosen_name, hypothesis, feats: List[str], key: str, default: Optional[str]) -> Optional[str]:
    """Consult the induced hypothesis. `default` is returned only if the chosen plugin genuinely
    cannot answer (estimation on an unseen key with no hypothesis at all) -- mirrors
    frame_induction.predict_subj_role's honest-degrade-path convention."""
    if hypothesis is None:
        return default
    feats = list(feats)
    if chosen_name == "proginduction":
        from hdlab.learner.plugins import proginduction_plugin
        pred = proginduction_plugin.apply(hypothesis, feats)
    elif chosen_name == "ruleind":
        from hdlab.learner.plugins import ruleind_plugin
        pred = ruleind_plugin.apply(hypothesis, feats, key=key, default_class=default)
    elif chosen_name == "estimation":
        from hdlab.learner.plugins import estimation_plugin
        pred = estimation_plugin.apply(hypothesis, key)
    else:  # KEEP_EPISODIC or unknown
        pred = None
    return pred if pred is not None else default


def memorization_baseline_predict(train_examples: List[Tuple[str, str, str]], tag: str,
                                   default: str) -> str:
    """The GATE-1 memorization-baseline control: an EXACT surface-form-tag lookup table built from
    TRAIN_EXAMPLES only. By construction every HELDOUT_EXAMPLES tag is absent from this table (see
    the module self-test's disjointness assertion), so this baseline can only ever return `default`
    on held-out items -- exactly the "a system that can only recall exact forms it has seen cannot
    generalize to a new one" comparison GATE-1 is designed to measure."""
    lookup: Dict[str, str] = {}
    for _text, gold, tag_ in train_examples:
        lookup.setdefault(tag_, gold)
    return lookup.get(tag, default)


_INDUCED_HYP_CACHE: Optional[Tuple[Optional[str], Optional[object]]] = None


def get_induced_hypothesis(use_cache: bool = True) -> Tuple[Optional[str], Optional[object]]:
    """(chosen_name, hypothesis) trained ONCE on TRAIN_EXAMPLES only (module-level cache) -- the
    SAME hypothesis GATE-1's held-out eval uses, reused unmodified for GATE-2's DesireDB scoring.
    NEVER trains on DesireDB -- this is what keeps the DesireDB recovery measurement (GATE-2)
    non-circular per the M2 task's anti-circular design mandate #4."""
    global _INDUCED_HYP_CACHE
    if use_cache and _INDUCED_HYP_CACHE is not None:
        return _INDUCED_HYP_CACHE
    train_eps = [build_episode(t, c, tag) for t, c, tag in TRAIN_EXAMPLES]
    chosen_name, chosen, _all = induce(train_eps)
    result = (chosen_name, chosen.hypothesis) if chosen is not None else (None, None)
    if use_cache:
        _INDUCED_HYP_CACHE = result
    return result


def result_type_votes(outcome: str, chosen_name, hypothesis) -> dict:
    """{'POS': int, 'NEG': int, 'matched': [result_type]} -- SAME return shape as
    hdlab.idiom_grounding.idiom_votes so a caller (hdlab.goal_achievement's resulttype-grounded
    channel) can combine it with the existing per-token WordNet vote the identical way M1 combined
    idiom_votes. Honest ABSTAIN (all-zero, empty matched) when `span_feats` found NOTHING
    informative at all (feats == ['no_verb_class_cue'] exactly, i.e. not even a bare negator) --
    this precheck exists so the induced hypothesis's own catch-all/residual-default rule (which,
    once induced, always answers SOMETHING for a genuinely uninformative span) does not inject a
    constant, outcome-content-independent bias vote into DesireDB scoring; the mechanism must only
    vote when a real construction cue fired. A bare discourse-negation span ('Uh. No.', feats ==
    ['neg_present','no_verb_class_cue']) is NOT uninformative by this test and proceeds to the
    model normally."""
    feats = span_feats(outcome)
    if feats == ["no_verb_class_cue"]:
        return {"POS": 0, "NEG": 0, "matched": []}
    key = "|".join(sorted(feats))
    pred = predict(chosen_name, hypothesis, feats, key, default=None)
    if pred is None:
        return {"POS": 0, "NEG": 0, "matched": []}
    pol = RESULT_TYPE_POLARITY[pred]
    return {"POS": 1 if pol == "POS" else 0, "NEG": 1 if pol == "NEG" else 0, "matched": [pred]}


# ============================================================================ self-test
def self_test() -> dict:
    """MECHANISM-FIRES + GENERALIZATION + anti-circular-design sanity checks. Real construction-cue
    extraction + real registry.learn() fit (estimation/ruleind/proginduction), no DesireDB needed."""
    # (1) TRAIN/HELD-OUT surface-form disjointness (the anti-circular design's load-bearing
    # invariant -- if this ever breaks, GATE-1 "generalization" would silently become memorization).
    train_tags = {tag for _t, _c, tag in TRAIN_EXAMPLES}
    held_tags = {tag for _t, _c, tag in HELDOUT_EXAMPLES}
    assert not (train_tags & held_tags), f"TRAIN/HELD-OUT tag overlap: {train_tags & held_tags}"

    # (2) span_feats never leaks a verb lemma as a feature name (frame_induction's discipline).
    f = span_feats("He declined immediately.")
    assert all(a in CONSTRUCTION_ATOMS for a in f), f
    assert "decline" not in " ".join(f)

    # (3) mechanism-fires: comm_verb / give_verb / achieve_verb / fail_verb / modal_neg / bare
    # discourse-negation atoms all actually fire on their intended TRAIN construction.
    assert "comm_verb" in span_feats("She asked him and he said no.")
    assert "give_verb" in span_feats("She gave him the job.")
    assert "achieve_verb" in span_feats("She achieved her goal.")
    assert "fail_verb" in span_feats("She failed the exam.")
    assert "modal_neg" in span_feats("He would not give her the money.")
    assert set(span_feats("Uh. No.")) == {"neg_present", "no_verb_class_cue"}

    # (4) end-to-end induction + held-out generalization + memorization/scramble controls.
    train_eps = [build_episode(t, c, tag) for t, c, tag in TRAIN_EXAMPLES]
    held_eps = [build_episode(t, c, tag) for t, c, tag in HELDOUT_EXAMPLES]
    chosen_name, chosen, all_results = induce(train_eps)
    assert chosen is not None, "induction abstained on the TRAIN set entirely"
    majority_train = max(RESULT_TYPES, key=lambda c: sum(1 for e in train_eps if e["gold_class"] == c))

    def _eval(name, hyp, eps):
        n_ok = 0
        for e in eps:
            key = "|".join(sorted(e["feats"]))
            pred = predict(name, hyp, e["feats"], key, default=majority_train)
            n_ok += (pred == e["gold_class"])
        return n_ok / len(eps)

    held_acc = _eval(chosen_name, chosen.hypothesis, held_eps)
    mem_correct = sum(1 for t, c, tag in HELDOUT_EXAMPLES
                       if memorization_baseline_predict(TRAIN_EXAMPLES, tag, majority_train) == c)
    mem_acc = mem_correct / len(HELDOUT_EXAMPLES)

    rng = random.Random(20260809)
    scrambled_labels = [e["gold_class"] for e in train_eps]
    rng.shuffle(scrambled_labels)
    scr_train_eps = [{"feats": e["feats"], "gold_class": scrambled_labels[i], "tag": e["tag"]}
                      for i, e in enumerate(train_eps)]
    scr_name, scr_chosen, _ = induce(scr_train_eps)
    scr_acc = _eval(scr_name, scr_chosen.hypothesis if scr_chosen else None, held_eps)

    assert held_acc > mem_acc, f"held_acc={held_acc} did not beat mem_acc={mem_acc}"
    assert held_acc > scr_acc, f"held_acc={held_acc} did not beat scr_acc={scr_acc}"

    # (5) result_type_votes: honest abstain on a truly-uninformative span; a real vote on an
    # informative one; POS/NEG polarity matches RESULT_TYPE_POLARITY.
    abstain = result_type_votes("The weather was nice today.", chosen_name, chosen.hypothesis)
    assert abstain == {"POS": 0, "NEG": 0, "matched": []}, abstain
    fires = result_type_votes("So Jarrad calls and she told him no.", chosen_name, chosen.hypothesis)
    assert fires["matched"] == ["REFUSAL"] and fires["NEG"] == 1 and fires["POS"] == 0, fires

    return {"chosen_plugin": chosen_name, "n_train": len(train_eps), "n_heldout": len(held_eps),
            "held_out_acc": round(held_acc, 4), "memorization_baseline_acc": round(mem_acc, 4),
            "scramble_control_acc": round(scr_acc, 4), "majority_train_class": majority_train,
            "all_plugin_description_bits": {k: round(v.description_bits, 3) for k, v in all_results.items()}}


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2, default=str))
