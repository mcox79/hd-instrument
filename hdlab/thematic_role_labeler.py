"""hdlab/thematic_role_labeler.py (2026-08-04)

THEMATIC-ROLE LABELER (Component 3, goal-owner pipeline). Brain-faithful cue-integration per
MacWhinney's Competition Model: role = AGENT/PATIENT/EXPERIENCER/RECIPIENT/GOAL/none, assigned by
integrating multiple probabilistic surface cues (word order, animacy, voice) weighted by CUE
VALIDITY, combined with the verb's lexical-semantic selectional frame. Per
notes/thematic_role_labeler_brain_faithful_build_spec.md Sections 2-3.

SUPPLIED (knowledge, glass-box):
  - VERB_FRAMES: hand-authored verb_lemma -> selectional frame dict.
  - hdlab.animacy_lexicon.lookup_animacy (reused verbatim).
  - hdlab.candidate_generator.candidates_from_parse (reused verbatim) for word-order/arc-rule cues.
  - is_passive_clause: NEW ~30-line glass-box passive-voice surface detector (BE-aux + past
    participle, optional by-PP). One boolean CUE, never a hard override.

EARNED (learned, the deliverable):
  - An AVERAGED PERCEPTRON mapping per-(verb,argument) feature-dict -> role label. Training-loop
    pattern reused verbatim from experiments/exp_path1_srl_mwp_cpu_v1.py::_train_role (NOT its
    corpus/role-vocab). The learned (feature,role) weights ARE the cue validities.

Public API:
  is_passive_clause(tokens, pos) -> bool
  lemma_verb(word) -> str
  frame_slot_role(lemma, slot) -> str          # slot in {"subj","obj","iobj"}
  role_feats(tokens, pos, heads, cand_rules, v_idx, a_idx) -> list[str]
  train_perceptron(examples, seed=7, epochs=20) -> (pred_fn, avg_weights, roles)
  scramble_weights(avg_weights, seed) -> dict  # validity-scramble control
  ablate_weights(avg_weights, keep_prefixes) -> dict  # single-cue-ablation control
  is_strictly_intransitive(lemma) -> bool      # frame-ARITY fact (2026-08-06); see below
  ROLES = (AGENT, PATIENT, EXPERIENCER, RECIPIENT, GOAL, NONE)

FRAME-ARITY NOTE (2026-08-06, event-extraction precision fix, hdlab/situation_reader.py
_pick_role_mentions gate): VERB_FRAMES above does NOT encode selectional ARITY (whether a verb
licenses an object slot AT ALL) -- every entry, including DEFAULT_FRAME, maps "obj"->"PATIENT"
for whichever verb reaches that slot; it says nothing about whether an object CAN exist for a
given verb. Checked before writing STRICTLY_INTRANSITIVE_VERBS below: PSYCH_FRAME, DITRANS_FRAME,
and DEFAULT_FRAME all carry an "obj" key, so no frame in this table can answer "does this verb
ever take a direct object." This is therefore a missing-FACT SUPPLY (not VERB_FRAMES-encoded),
per the route-errors-by-flavor discipline.
"""
from __future__ import annotations

import random
import re
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from hdlab.animacy_lexicon import lookup_animacy

ROLES = ("AGENT", "PATIENT", "EXPERIENCER", "RECIPIENT", "GOAL", "none")

# ---------------------------------------------------------------------------------------------
# (a) Verb selectional-frame table (SUPPLIED knowledge, glass-box; ~150-300 narrative lemmas).
#     frame dict maps syntactic slot -> role licensed at that slot for THIS verb.
#     Default (unlisted verb) = plain agent-transitive frame.
# ---------------------------------------------------------------------------------------------
DEFAULT_FRAME = {"subj": "AGENT", "obj": "PATIENT", "iobj": "RECIPIENT"}

# Experiencer-subject / psych closed class (fear/like/hate/want/know/believe/see/hear/feel...):
# the SUBJECT is the EXPERIENCER, not the AGENT; the object is the stimulus (mapped to PATIENT,
# the closest role in our output vocab).
_PSYCH_FRAME = {"subj": "EXPERIENCER", "obj": "PATIENT"}
PSYCH_VERBS = [
    "fear", "like", "hate", "want", "know", "believe", "see", "hear", "feel", "love", "wish",
    "remember", "forget", "understand", "notice", "wonder", "desire", "dread", "admire", "pity",
    "envy", "doubt", "trust", "suspect", "adore", "distrust", "imagine", "recall", "perceive",
    "regret", "miss", "enjoy", "appreciate", "prefer", "dislike", "long", "yearn", "expect",
    "recognize", "realize", "sense", "smell", "taste", "observe", "think", "consider", "mind",
]

# Ditransitive verbs (subj=AGENT, iobj=RECIPIENT, obj=PATIENT/THEME):
_DITRANS_FRAME = {"subj": "AGENT", "obj": "PATIENT", "iobj": "RECIPIENT"}
DITRANS_VERBS = [
    "give", "tell", "show", "bring", "send", "offer", "hand", "teach", "pay", "promise", "grant",
    "lend", "sell", "read", "write", "buy", "throw", "pass", "hand", "feed", "serve", "leave",
    "owe", "bring", "wish", "assign", "award", "allot", "deny", "refuse", "forgive", "envy",
]

# Plain agent-transitive / motion / general narrative verbs (subj=AGENT; obj=PATIENT if present).
# 2026-08-05 coverage extension (frame-trigger recall fix, drill afddc2807): knock/lay/finish/have
# were FN root causes (novel lemmas, no frame entry) found by the FN-composition test on the
# independent-gold recall eval -- adding them is Component-3 coverage-widening, not a new organ.
_PLAIN_TRANSITIVE = [
    "knock", "lay", "finish", "have",
    "take", "throw", "build", "rub", "fall", "cry", "go", "come", "run", "walk", "sit", "stand",
    "catch", "reach", "spring", "leap", "creep", "swim", "pass", "do", "make", "break", "cut",
    "strike", "hit", "kick", "push", "pull", "carry", "drop", "lift", "open", "close", "shut",
    "burn", "kill", "save", "help", "hurt", "wound", "chase", "hunt", "capture", "find", "lose",
    "keep", "hold", "grab", "seize", "gather", "pick", "plant", "grow", "cook", "bake", "wash",
    "clean", "sweep", "dig", "climb", "jump", "sing", "dance", "shout", "call", "answer", "ask",
    "speak", "talk", "laugh", "smile", "weep", "sob", "sigh", "greet", "meet", "visit", "follow",
    "lead", "guide", "drive", "ride", "sail", "fly", "fight", "attack", "defend", "protect",
    "guard", "watch", "look", "stare", "gaze", "wave", "point", "touch", "kiss", "hug", "embrace",
    "hold", "carry", "drag", "roll", "spin", "turn", "bend", "fold", "tear", "rip", "sew", "knit",
    "paint", "draw", "write", "read", "learn", "teach", "study", "play", "win", "lose", "beat",
    "race", "walk", "march", "travel", "arrive", "depart", "leave", "enter", "exit", "return",
    "stay", "remain", "wait", "rest", "sleep", "wake", "rise", "fall", "sink", "float", "swim",
    "build", "destroy", "repair", "mend", "fix", "break", "shake", "tremble", "shiver", "freeze",
    "melt", "boil", "pour", "spill", "fill", "empty", "cover", "hide", "reveal", "show", "discover",
]

VERB_FRAMES: Dict[str, dict] = {}
for _v in PSYCH_VERBS:
    VERB_FRAMES[_v] = dict(_PSYCH_FRAME)
for _v in DITRANS_VERBS:
    VERB_FRAMES.setdefault(_v, dict(_DITRANS_FRAME))
for _v in _PLAIN_TRANSITIVE:
    VERB_FRAMES.setdefault(_v, dict(DEFAULT_FRAME))


def frame_slot_role(lemma: str, slot: str) -> str:
    """verb lemma + syntactic slot ('subj'/'obj'/'iobj') -> role licensed at that slot."""
    frame = VERB_FRAMES.get(lemma, DEFAULT_FRAME)
    return frame.get(slot, "none")


# ---------------------------------------------------------------------------------------------
# STRICTLY-INTRANSITIVE verbs (SUPPLY, hand-authored, 2026-08-06): verbs that NEVER license a
# direct-object/PATIENT slot in ordinary narrative usage. Used ONLY to gate the PATIENT slot in
# hdlab/situation_reader.py::_pick_role_mentions (frame-ARITY gate) -- never touches AGENT/subject
# selection. CONSERVATIVE by design: a verb is excluded from this set (left ungated, i.e. keeps
# the current positional-object behavior) whenever it has a plausible transitive OR ambitransitive
# sense in narrative prose, even an idiomatic/homonymous one, per the "over-gating a real patient
# is worse than under-gating a rare one" instruction. Two verbs from the illustrative example list
# are DELIBERATELY EXCLUDED for this reason (documented, not an oversight):
#   - "stand": excluded -- common transitive STATIVE-EXPERIENCER homonym "cannot stand it/him"
#     (tolerate) is frequent in narrative English; gating would strip a real patient.
#   - "wait": excluded -- "wait one's turn" / "wait tables" are real (if less frequent) transitive
#     uses; conservative exclusion.
# Everything below is checked against no such common transitive/ambitransitive sense:
#   arrive/depart/vanish/disappear/arise/faint/collapse/expire/perish: no direct-object sense at
#     all in ordinary English. die: "die a death/die a hero's death" is a marginal, archaic
#     cognate-object idiom (semantically near-vacuous, does not license a genuine distinct
#     PATIENT) -- included. go/come/fall/rise: the "go/come/fall/rise it" idiomatic transitive
#     uses are archaic/marginal; the self-motion sense (the dominant sense this gate targets) never
#     takes a direct object -- included. kneel: no transitive sense -- included. sit/sleep: "sit an
#     exam"/"sit a horse" (chiefly British/archaic) and the cognate-object "sleep the sleep of the
#     just" are rare/literary; included per the conservative-but-not-absolute reading of the
#     instruction (both verbs were named in the illustrative example list and their transitive
#     senses are markedly rarer than "stand"=tolerate).
# ---------------------------------------------------------------------------------------------
STRICTLY_INTRANSITIVE_VERBS = frozenset({
    "arrive", "depart", "vanish", "disappear", "arise", "faint", "collapse", "expire", "perish",
    "die", "go", "come", "fall", "rise", "kneel", "sit", "sleep",
})


def is_strictly_intransitive(lemma: str) -> bool:
    """True iff `lemma` never licenses a direct-object/PATIENT slot (SUPPLIED conservative set;
    see STRICTLY_INTRANSITIVE_VERBS above + its exclusion rationale). AMBITRANSITIVE verbs
    (eat/read/sing/...) are deliberately NOT in this set -- they keep the current positional
    object-selection behavior unconditionally."""
    return lemma in STRICTLY_INTRANSITIVE_VERBS


# ---------------------------------------------------------------------------------------------
# Small glass-box lemmatizer (hand irregular table + suffix-stripping fallback). Needed to key
# into VERB_FRAMES from inflected surface verb tokens ("building" -> "build", "took" -> "take").
# ---------------------------------------------------------------------------------------------
_IRREGULAR_LEMMA = {
    "took": "take", "threw": "throw", "gave": "give", "saw": "see", "knew": "know", "felt": "feel",
    "heard": "hear", "went": "go", "came": "come", "was": "be", "were": "be", "is": "be", "are": "be",
    "am": "be", "been": "be", "being": "be", "had": "have", "has": "have", "did": "do", "does": "do",
    "told": "tell", "brought": "bring", "sent": "send", "thought": "think", "said": "say", "ran": "run",
    "sat": "sit", "stood": "stand", "fell": "fall", "sprang": "spring", "sprung": "spring",
    "crept": "creep", "swam": "swim", "meant": "mean", "wished": "wish", "grew": "grow", "made": "make",
    "broke": "break", "cut": "cut", "struck": "strike", "hit": "hit", "kept": "keep", "held": "hold",
    "caught": "catch", "found": "find", "lost": "lose", "wrote": "write", "read": "read", "spoke": "speak",
    "won": "win", "beat": "beat", "left": "leave", "slept": "sleep", "woke": "wake", "rose": "rise",
    "sank": "sink", "sold": "sell", "bought": "buy", "paid": "pay", "taught": "teach", "understood": "understand",
    "forgot": "forget", "chose": "choose", "drove": "drive", "flew": "fly", "fought": "fight",
    "built": "build", "began": "begin", "drew": "draw", "wore": "wear", "bore": "bear", "bit": "bite",
    "hid": "hide", "shook": "shake", "froze": "freeze", "spent": "spend", "sang": "sing", "rang": "ring",
    "rode": "ride", "shone": "shine", "shot": "shoot", "sought": "seek", "sold": "sell",
}


def lemma_verb(word: str) -> str:
    """Glass-box surface-form -> lemma for verb lookup (irregular table + suffix strip)."""
    w = word.lower().strip(".,\"'();:")
    if w in _IRREGULAR_LEMMA:
        return _IRREGULAR_LEMMA[w]
    if w.endswith("ing") and len(w) > 5:
        base = w[:-3]
        if len(base) > 2 and base[-1] == base[-2] and base[-1] not in "aeiou":  # running -> run
            return base[:-1]
        return base
    if w.endswith("ied") and len(w) > 4:  # cried -> cry
        return w[:-3] + "y"
    if w.endswith("ed") and len(w) > 3:
        base = w[:-2]
        if len(base) > 2 and base[-1] == base[-2] and base[-1] not in "aeiou":  # stopped -> stop
            return base[:-1]
        return base
    if w.endswith("es") and len(w) > 3:
        return w[:-2]
    if w.endswith("s") and len(w) > 3 and not w.endswith("ss"):
        return w[:-1]
    return w


# ---------------------------------------------------------------------------------------------
# (d) NEW: passive-voice surface detector. Symbolic pattern-match, no learning. ~30 lines.
#     BE-aux (is/was/were/be/been/being/am/are) immediately-or-near-adjacent to a past-participle-
#     tagged verb, optional trailing "by"-PP. ONE boolean feature fed into integration, never an
#     override (per the exp_read_events_supply_parse_nsubj CLEAN_NEGATIVE net_fix=-182 lesson).
# ---------------------------------------------------------------------------------------------
_BE_AUX = {"is", "are", "was", "were", "be", "been", "being", "am"}
_PARTICIPLE_IRREGULAR = {
    "taken", "thrown", "given", "seen", "known", "felt", "heard", "gone", "come", "been", "had",
    "done", "told", "brought", "sent", "thought", "said", "run", "sat", "stood", "fallen", "sprung",
    "crept", "swum", "meant", "grown", "made", "broken", "cut", "struck", "hit", "kept", "held",
    "caught", "found", "lost", "written", "read", "spoken", "won", "beaten", "left", "slept",
    "woken", "risen", "sunk", "sold", "bought", "paid", "taught", "understood", "forgotten",
    "chosen", "driven", "flown", "fought", "built", "begun", "drawn", "worn", "borne", "bitten",
    "hidden", "shaken", "frozen", "spent", "sung", "rung", "ridden", "shone", "shot", "sought",
}


def _is_participle(word: str, pos_tag: Optional[str] = None) -> bool:
    w = word.lower().strip(".,\"'();:")
    if w in _PARTICIPLE_IRREGULAR:
        return True
    if w.endswith("ed") and len(w) > 3:
        return True
    if pos_tag == "VERB" and w.endswith("en") and len(w) > 3:
        return True
    return False


def is_passive_clause(tokens: Sequence[str], pos: Sequence[str], window: int = 3) -> bool:
    """BE-aux followed within `window` tokens (allowing an intervening adverb) by a past-participle.
    Optional trailing 'by' PP strengthens but is not required. Deliberately self-contained regex/
    POS-pattern (glass-box, in-repo, no external parser dependency) -- a boolean CUE VALUE, not a
    hard override on downstream role assignment.
    """
    n = len(tokens)
    for i in range(n):
        if tokens[i].lower() not in _BE_AUX:
            continue
        for j in range(i + 1, min(n, i + 1 + window)):
            ptag = pos[j] if j < len(pos) else None
            if ptag == "ADV":
                continue
            if _is_participle(tokens[j], ptag):
                return True
            break  # first non-adverb token after aux must be the participle or this site fails
    return False


# ---------------------------------------------------------------------------------------------
# EARNED cue-integration: feature-dict builder for a (verb_idx, arg_idx) candidate pair.
# ---------------------------------------------------------------------------------------------
def _dist_bucket(d: int) -> str:
    if d <= 1:
        return "0"
    if d <= 3:
        return "1"
    if d <= 6:
        return "2"
    return "3"


def role_feats(tokens: Sequence[str], pos: Sequence[str], v_idx: int, a_idx: int,
               rule_tag: str, voice_passive: bool, pos_full: Optional[Sequence[str]] = None) -> List[str]:
    """Build the feature-dict for candidate (verb_idx, arg_idx), 1-based indices into tokens/pos.
    Matches spec Section 3 feature list verbatim (word-order, animacy, verb-frame-slot, voice,
    voice_x_order interaction).
    """
    order = "pre" if a_idx < v_idx else "post"
    dist = _dist_bucket(abs(a_idx - v_idx))
    lemma = lemma_verb(tokens[v_idx - 1])
    slot = "subj" if order == "pre" else "obj"
    frame_role = frame_slot_role(lemma, slot)
    arg_tok = tokens[a_idx - 1]
    arg_pos = pos[a_idx - 1] if a_idx - 1 < len(pos) else None
    anim = lookup_animacy(arg_tok, arg_pos)
    anim_val = anim["animacy"] if anim is not None else "unk"
    voice = "passive" if voice_passive else "active"
    feats = [
        "order:" + order,
        "dist_bucket:" + dist,
        "arc_rule:" + rule_tag,
        "animacy:" + anim_val,
        "frame_slot:" + frame_role,
        "voice:" + voice,
        "vxo:" + voice + "_" + order,
        "BIAS",
    ]
    return feats


# ---------------------------------------------------------------------------------------------
# EARNED: averaged perceptron. Training-loop pattern reused VERBATIM from
# experiments/exp_path1_srl_mwp_cpu_v1.py::_train_role (same feature-dict-in, weighted-vote-out,
# argmax pattern). NOT its corpus/role-vocab.
# ---------------------------------------------------------------------------------------------
def train_perceptron(examples: List[Tuple[List[str], str]], seed: int = 7, epochs: int = 20,
                     roles: Optional[Sequence[str]] = None):
    """examples: list of (feats, gold_role). Returns (pred_fn, avg_weights, roles)."""
    import numpy as np
    role_set = tuple(sorted(roles)) if roles is not None else tuple(sorted({r for _f, r in examples}))
    rng = np.random.default_rng(seed)
    w: Dict[Tuple[str, str], float] = defaultdict(float)
    cw: Dict[Tuple[str, str], float] = defaultdict(float)
    c = 1
    for _ in range(epochs):
        for i in rng.permutation(len(examples)):
            feats, gold = examples[int(i)]
            scores = {r: sum(w[(f, r)] for f in feats) for r in role_set}
            pred = max(scores, key=scores.get)
            if pred != gold:
                for f in feats:
                    w[(f, gold)] += 1
                    cw[(f, gold)] += c
                    w[(f, pred)] -= 1
                    cw[(f, pred)] -= c
            c += 1
    avg = {k: w[k] - cw[k] / c for k in w}

    def pred_fn(feats: List[str], weights: Optional[dict] = None) -> str:
        wts = weights if weights is not None else avg
        scores = {r: sum(wts.get((f, r), 0.0) for f in feats) for r in role_set}
        return max(scores, key=scores.get)

    return pred_fn, avg, role_set


def scramble_weights(avg_weights: dict, seed: int = 20260804) -> dict:
    """Validity-scramble control: permute the learned (feature,role) weight VALUES across keys,
    same discipline as animacy_lexicon.scrambled_lookup_factory. If a discriminating scramble
    doesn't collapse performance, the weights are decorative."""
    keys_sorted = sorted(avg_weights.keys())
    values_sorted = [avg_weights[k] for k in keys_sorted]
    rng = random.Random(seed)
    permuted = values_sorted[:]
    rng.shuffle(permuted)
    return dict(zip(keys_sorted, permuted))


def ablate_weights(avg_weights: dict, keep_prefix: str) -> dict:
    """Single-cue ablation control: zero out every weight whose feature does NOT start with
    keep_prefix (keeps BIAS always). e.g. keep_prefix='animacy:' isolates the animacy-only arm."""
    out = {}
    for (f, r), v in avg_weights.items():
        if f.startswith(keep_prefix) or f == "BIAS":
            out[(f, r)] = v
    return out


# ---------------------------------------------------------------------------------------------
# Drop-in replacement I/O contract for hdlab/situation_reader.py::_assign_roles. Consumes the same
# style of nominal-mention dicts (list with 'text'/'idx' style fields upstream), extended to emit
# EXPERIENCER/RECIPIENT/GOAL/none in addition to AGENT/PATIENT.
# ---------------------------------------------------------------------------------------------
def label_roles(pred_fn: Callable, tokens: Sequence[str], pos: Sequence[str], v_idx: int,
                cand_pairs, cand_rules: dict, is_passive: bool) -> Dict[int, str]:
    """For a predicate at v_idx with candidate arg indices cand_pairs (set of (v,a) for this v),
    return {arg_idx: role_label}."""
    out: Dict[int, str] = {}
    for (vv, a) in cand_pairs:
        if vv != v_idx:
            continue
        rule_tag = cand_rules.get((vv, a), "core_dep")
        feats = role_feats(tokens, pos, vv, a, rule_tag, is_passive)
        out[a] = pred_fn(feats)
    return out


def _selftest() -> None:
    assert frame_slot_role("fear", "subj") == "EXPERIENCER"
    assert frame_slot_role("kick", "subj") == "AGENT"
    assert frame_slot_role("give", "iobj") == "RECIPIENT"
    assert lemma_verb("building") == "build"
    assert lemma_verb("took") == "take"
    assert lemma_verb("cried") == "cry"
    assert is_passive_clause(["it", "was", "built", "by", "him"], ["PRON", "AUX", "VERB", "ADP", "PRON"]) is True
    assert is_passive_clause(["he", "built", "it"], ["PRON", "VERB", "PRON"]) is False
    feats = role_feats(["it", "was", "built"], ["PRON", "AUX", "VERB"], 3, 1, "core_dep", True)
    assert "order:pre" in feats and "voice:passive" in feats and "vxo:passive_pre" in feats
    ex = [(["order:pre", "animacy:animate", "BIAS"], "AGENT"),
          (["order:post", "animacy:inanimate", "BIAS"], "PATIENT")] * 5
    pred_fn, avg, roles = train_perceptron(ex, seed=1, epochs=10)
    assert pred_fn(["order:pre", "animacy:animate", "BIAS"]) == "AGENT"
    scr = scramble_weights(avg, seed=1)
    assert set(scr.keys()) == set(avg.keys())
    abl = ablate_weights(avg, "animacy:")
    assert all(f.startswith("animacy:") or f == "BIAS" for (f, _r) in abl.keys())
    # frame-ARITY fact (2026-08-06): strictly-intransitive membership + conservative exclusions.
    assert is_strictly_intransitive("go") and is_strictly_intransitive("arrive")
    assert is_strictly_intransitive("sit") and is_strictly_intransitive("die")
    assert not is_strictly_intransitive("stand"), "stand must stay ungated (tolerate homonym)"
    assert not is_strictly_intransitive("wait"), "wait must stay ungated (wait-one's-turn)"
    assert not is_strictly_intransitive("eat"), "ambitransitive verbs must never be gated"
    assert not is_strictly_intransitive("build"), "plain transitive verbs must never be gated"
    print("[selftest] PASS: thematic_role_labeler", flush=True)


if __name__ == "__main__":
    _selftest()
