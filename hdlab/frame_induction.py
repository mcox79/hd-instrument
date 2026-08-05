"""hdlab/frame_induction.py (2026-08-04)

OOV VERB THEMATIC-FRAME INDUCTION -- FEATURE ENCODER ONLY (config-only EXPAND of hdlab/learner).

WHAT: teach the substrate to INDUCE a novel verb's thematic FRAME (does its SUBJECT fill AGENT or
EXPERIENCER?) from the CONSTRUCTIONS the verb is observed in -- Gleitman (1990) syntactic
bootstrapping. A verb the labeler has never seen (`lemma not in thematic_role_labeler.VERB_FRAMES`)
currently falls to DEFAULT_FRAME -> subj=AGENT, which is WRONG for a novel psych verb
(cherish/loathe/crave/covet). This module supplies the CONSTRUCTION-CUE ENCODER + thin wrappers so
the EXISTING centralized learner (hdlab/learner/registry.learn/apply) can induce the
construction->frame mapping and TRANSFER it to unseen verbs.

CONFIG-ONLY EXPAND (audit notes/research_oov_verb_frame_induction_learner_expand_audit_2026-08-04):
  - ZERO edits to hdlab/learner/core.py, registry.py, or any plugin. This file is the only new code.
  - The learner is invoked exactly through its public (episodes, features, hypothesis_space_spec)
    contract, MDL-auto-selecting across estimation / ruleind / proginduction (proginduction is the
    strongest defense against the marginal-driven cue-conflict failure the re-VET diagnosed).

SUPPLIED (glass-box, honestly): the role vocabulary (AGENT / EXPERIENCER) + the construction-cue
  detector definitions. EARNED (the deliverable): the construction->frame MAPPING, induced by the
  learner from IN-VOCAB verbs' distributions and transferred to unseen verbs by CONSTRUCTION
  OVERLAP. **The verb lemma is NEVER a feature** -- this is what makes the induced hypothesis
  transfer to a held-out novel verb (the direct fix for the shelved perceptron's ~92% feature-leak
  near-memorization).

OOV TRIGGER = plain dict membership (`is_oov(lemma)` == `lemma not in VERB_FRAMES`). Deliberately
  NOT predictive_coding (audit: continuous bipolar-residual novelty is a wrong SHAPE for a discrete
  symbol-table lookup) and NOT self_improving_loop (audit: that is the coref keep/revert router,
  not a mint engine).

Public API:
  is_oov(lemma) -> bool
  CONSTRUCTION_ATOMS  (the declared boolean DSL atom list for proginduction)
  episode_feats(tokens, v_idx, subj_idx, pos=None) -> list[str]   # NEVER contains the lemma
  build_episode(tokens, v_idx, subj_idx, gold_subj_role, pos=None) -> dict
  induce(episodes, spec=None) -> (chosen_name, chosen_LearnResult, all_results)
  predict_subj_role(chosen_name, hypothesis, feats, default="AGENT") -> str
"""
from __future__ import annotations

from typing import List, Optional, Sequence

from hdlab.learner import registry
from hdlab.thematic_role_labeler import VERB_FRAMES, lemma_verb

# The 4 declared boolean construction atoms (per-competence CONFIG; proginduction enumerates over
# these). Small on purpose: proginduction evaluates the full 2**n_atoms truth table.
CONSTRUCTION_ATOMS = ["has_scomp", "degree_mod", "progressive", "order_pre"]

_COMPLEMENTIZERS = {"that", "whether", "if"}
_DEGREE_WORDS = {"very", "much", "greatly", "deeply", "dearly", "really", "sorely"}
_BE_AUX = {"is", "are", "was", "were", "be", "been", "being", "am"}


def is_oov(lemma: str) -> bool:
    """OOV trigger: the verb lemma is NOT in the supplied frame table (=> induce its frame)."""
    return lemma not in VERB_FRAMES


def _clean(tok: str) -> str:
    return tok.lower().strip(".,\"'();:")


def has_sentential_complement(tokens: Sequence[str], v_idx: int, window: int = 4) -> bool:
    """Gleitman/Fisher cue: psych/cognition verbs (know/believe/want/fear) disproportionately
    license a CP/that-complement or a to-infinitive; agentive-transitive verbs rarely do.
    Surface detector: a complementizer, OR a `to`+word infinitive, within `window` tokens after
    the verb. Glass-box, no external parser."""
    n = len(tokens)
    for j in range(v_idx + 1, min(n, v_idx + 1 + window)):
        w = _clean(tokens[j])
        if w in _COMPLEMENTIZERS:
            return True
        if w == "to" and j + 1 < n:  # to-infinitive complement
            return True
    return False


def is_degree_modified(tokens: Sequence[str], v_idx: int, window: int = 4) -> bool:
    """Experiencer-verb diagnostic: gradable psych verbs accept degree modification
    (`love very much`, `deeply regret`); agentive-manner verbs resist it. Detector: a degree word
    within `window` tokens on EITHER side of the verb."""
    n = len(tokens)
    lo = max(0, v_idx - window)
    hi = min(n, v_idx + 1 + window)
    for j in range(lo, hi):
        if j == v_idx:
            continue
        if _clean(tokens[j]) in _DEGREE_WORDS:
            return True
    return False


def is_progressive(tokens: Sequence[str], v_idx: int, window: int = 2) -> bool:
    """Eventive/agentive cue (the NEGATIVE of the classic stative diagnostic): the verb appears in
    the progressive (BE-aux + V-ing). Stative psych verbs resist the progressive. Detector: a
    BE-aux within `window` tokens before the verb AND the verb surface ends in -ing."""
    vw = _clean(tokens[v_idx]) if 0 <= v_idx < len(tokens) else ""
    if not vw.endswith("ing"):
        return False
    lo = max(0, v_idx - window)
    for j in range(lo, v_idx):
        if _clean(tokens[j]) in _BE_AUX:
            return True
    return False


def episode_feats(tokens: Sequence[str], v_idx: int, subj_idx: int,
                  pos: Optional[Sequence[str]] = None) -> List[str]:
    """Build the construction-cue atom list for ONE (verb, subject) occurrence. 0-based indices.
    CRITICAL: NEVER includes the verb lemma or any n-gram containing it -- construction shape only,
    so the induced hypothesis transfers to an unseen verb."""
    feats: List[str] = []
    if has_sentential_complement(tokens, v_idx):
        feats.append("has_scomp")
    if is_degree_modified(tokens, v_idx):
        feats.append("degree_mod")
    if is_progressive(tokens, v_idx):
        feats.append("progressive")
    if subj_idx < v_idx:
        feats.append("order_pre")
    return feats


def build_episode(tokens: Sequence[str], v_idx: int, subj_idx: int, gold_subj_role: str,
                  pos: Optional[Sequence[str]] = None) -> dict:
    """One weak-supervision training/eval episode. gold_subj_role is the SUPPLIED gold subject
    role for THIS occurrence (from the in-vocab frame table at train time; the held-out lexical
    truth at eval time). The prediction path uses ONLY `feats`, never the lemma."""
    return {"feats": list(episode_feats(tokens, v_idx, subj_idx, pos)), "gold_class": gold_subj_role}


def _feat_fn(ep):
    return ep["feats"]


def _key_fn(ep):
    return "|".join(sorted(ep["feats"]))


def default_spec(classes):
    """Default hypothesis-space CONFIG: MDL-auto-select across estimation / ruleind /
    proginduction. proginduction included per audit (its total-boolean-function-over-declared-atoms
    design is the strongest defense against a majority-marginal collapsing an unseen combo)."""
    return {
        "candidate_plugins": ["estimation", "ruleind", "proginduction"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl", "key_fn": _key_fn,
                           "label_fn": lambda ep: ep["gold_class"], "classes": list(classes)},
            "ruleind": {"max_conjunct": 2, "min_coverage": 2, "purity_thresh": 0.75,
                        "max_rules": 25, "key_fn": _key_fn},
            "proginduction": {"atoms": list(CONSTRUCTION_ATOMS), "max_nodes": 9,
                              "label_fn": lambda ep: ep["gold_class"], "classes": list(classes)},
        },
    }


def induce(episodes, spec=None):
    """Fit + MDL-auto-select over the learner's plugins. Returns (chosen_name, chosen, all_results).
    chosen_name may be a plugin name or hdlab.learner.core.KEEP_EPISODIC."""
    classes = sorted({ep["gold_class"] for ep in episodes})
    spec = spec or default_spec(classes)
    return registry.learn(episodes, _feat_fn, spec)


def predict_subj_role(chosen_name, hypothesis, feats, default="AGENT"):
    """Consult the induced hypothesis via the chosen plugin's apply(). Falls back to `default`
    (the current known-bad DEFAULT_FRAME behavior) ONLY when the plugin abstains -- an honest,
    measurable degrade path, not a silent override."""
    if hypothesis is None:
        return default
    feats = list(feats)
    key = "|".join(sorted(feats))
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


def _selftest() -> None:
    # OOV trigger: novel psych verbs are absent from the supplied table; known ones are present.
    assert is_oov("cherish") and is_oov("loathe") and is_oov("crave") and is_oov("covet")
    assert not is_oov("fear") and not is_oov("kick")
    assert lemma_verb("cherished") == "cherish"

    # Detectors on real token strings.
    assert has_sentential_complement(["she", "knew", "that", "he", "left"], 1) is True
    assert has_sentential_complement(["she", "kicked", "the", "ball"], 1) is False
    assert is_degree_modified(["he", "loved", "her", "very", "much"], 1) is True
    assert is_degree_modified(["he", "built", "the", "house"], 1) is False
    assert is_progressive(["he", "was", "building", "it"], 2) is True
    assert is_progressive(["he", "feared", "it"], 1) is False

    # episode_feats NEVER leaks the lemma.
    f = episode_feats(["she", "cherished", "that", "old", "ring"], 1, 0)
    assert "has_scomp" in f and "order_pre" in f
    assert all(":" not in a or a in CONSTRUCTION_ATOMS for a in f)
    assert "cherish" not in " ".join(f)

    # Tiny end-to-end induction: scomp/degree -> EXPERIENCER, bare/progressive -> AGENT.
    eps = []
    for _ in range(6):
        eps.append(build_episode(["x", "verb", "that", "y", "z"], 1, 0, "EXPERIENCER"))
        eps.append(build_episode(["x", "verb", "y", "very", "much"], 1, 0, "EXPERIENCER"))
        eps.append(build_episode(["x", "verb", "the", "y"], 1, 0, "AGENT"))
        eps.append(build_episode(["x", "verb", "the", "y"], 1, 0, "AGENT"))  # bare majority = AGENT
        eps.append(build_episode(["x", "was", "verbing", "the", "y"], 2, 0, "AGENT"))
    name, chosen, allr = induce(eps)
    assert chosen is not None, "induction abstained on a clearly-separable toy"
    # Held-out-style scomp occurrence -> EXPERIENCER via construction, not lemma.
    held = episode_feats(["novelsubj", "novelverb", "that", "the", "storm"], 1, 0)
    assert predict_subj_role(name, chosen.hypothesis, held) == "EXPERIENCER"
    # Bare occurrence -> AGENT (uninformative frame, honest Gleitman behavior).
    bare = episode_feats(["novelsubj", "novelverb", "the", "ring"], 1, 0)
    assert predict_subj_role(name, chosen.hypothesis, bare) == "AGENT"
    print("[selftest] PASS: frame_induction (chosen=%s)" % name, flush=True)


if __name__ == "__main__":
    _selftest()
