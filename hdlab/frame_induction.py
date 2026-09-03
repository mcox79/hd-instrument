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

import hashlib
import json
import os
import pickle
from typing import List, Optional, Sequence, Tuple

from hdlab.learner import registry
from hdlab.thematic_role_labeler import VERB_FRAMES, DEFAULT_FRAME, lemma_verb, frame_slot_role

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
    return tok.lower().strip(".,\"'();:!?")


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


def default_spec(classes, atoms=None):
    """Default hypothesis-space CONFIG: MDL-auto-select across estimation / ruleind /
    proginduction. proginduction included per audit (its total-boolean-function-over-declared-atoms
    design is the strongest defense against a majority-marginal collapsing an unseen combo).
    `atoms` overrides the proginduction atom list (real-data adapter passes REAL_CONSTRUCTION_ATOMS)."""
    atoms = list(atoms) if atoms is not None else list(CONSTRUCTION_ATOMS)
    return {
        "candidate_plugins": ["estimation", "ruleind", "proginduction"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl", "key_fn": _key_fn,
                           "label_fn": lambda ep: ep["gold_class"], "classes": list(classes)},
            "ruleind": {"max_conjunct": 2, "min_coverage": 2, "purity_thresh": 0.75,
                        "max_rules": 25, "key_fn": _key_fn},
            "proginduction": {"atoms": atoms, "max_nodes": 9,
                              "label_fn": lambda ep: ep["gold_class"], "classes": list(classes)},
        },
    }


def induce(episodes, spec=None):
    """Fit + MDL-auto-select over the learner's plugins. Returns (chosen_name, chosen, all_results).
    chosen_name may be a plugin name or hdlab.learner.core.KEEP_EPISODIC."""
    classes = sorted({ep["gold_class"] for ep in episodes})
    spec = spec or default_spec(classes)
    return registry.learn(episodes, _feat_fn, spec)


# ---------------------------------------------------------------------------------------------
# REAL-DATA ADAPTER (2026-08-04): construction cues computed directly from REAL narrative text
# (experiments/data/experiencer_narrative_roles_v1.jsonl), replacing the templated bare/scomp/
# degree/progressive corpus above. Adds PASSIVE-VOICE and ARGUMENT-ANIMACY cues -- both legitimate
# Gleitman/Naigles-style syntactic+semantic bootstrapping signals, observable from surface form
# ALONE. Deliberately NEVER uses: the verb lemma, the gold role, or the dataset's own
# "construction" field (that field WOULD be circular -- it already encodes the subj-exp/obj-exp
# distinction induction is trying to recover; e.g. "transitive" vs "exp_obj_active" is the exact
# semantic ambiguity classic psych-verb pairs like fear/frighten are syntactically IDENTICAL on
# (fixed English SVO order alone -- this is the acknowledged "hard case", not solvable from
# order/scomp/degree/progressive cues; passive + animacy are the two additional surface cues that
# can help without peeking at the answer.
# ---------------------------------------------------------------------------------------------
REAL_CONSTRUCTION_ATOMS = ["has_scomp", "degree_mod", "progressive", "passive", "order_pre", "arg_animate"]

_NOMINATIVE_PRONOUNS = {"i", "he", "she", "we", "they", "you", "who"}
_INANIMATE_PRONOUNS = {"it", "this", "that", "these", "those"}


def is_passive_real(tokens: Sequence[str], v_idx: int, window: int = 3) -> bool:
    """Self-contained passive-voice surface detector (no POS tagger): a BE-aux within `window`
    tokens before v_idx, at most one intervening token (participle morphology not required --
    v_idx itself is the (possibly irregular) participle by construction of the psych-verb data).
    """
    lo = max(0, v_idx - window)
    for i in range(lo, min(v_idx, len(tokens))):   # bound by len(tokens): v_idx may exceed the token list
        if _clean(tokens[i]) in _BE_AUX and (v_idx - i - 1) <= 1:
            return True
    return False


def _is_animate_head(tokens: Sequence[str], idx: Optional[int]) -> bool:
    """Surface animacy heuristic for the token at idx: nominative/1st/2nd-person pronoun ->
    animate; 'it'/demonstrative -> inanimate; a capitalized NON-sentence-initial token (proper
    noun) -> animate; else unknown -> treated inanimate. Never consults gold roles or the lemma."""
    if idx is None or not (0 <= idx < len(tokens)):
        return False
    raw = tokens[idx]
    w = _clean(raw)
    if w in _NOMINATIVE_PRONOUNS:
        return True
    if w in _INANIMATE_PRONOUNS:
        return False
    if idx > 0 and raw[:1].isupper():
        return True
    return False


def real_construction_feats(tokens: Sequence[str], v_idx: int, arg_idx: Optional[int]) -> List[str]:
    """Construction-cue atom list for ONE (verb-occurrence, argument) pair in REAL text. Extends
    episode_feats() with passive + animacy -- real prose has frequent zero-complementizer finite
    clauses ("I fear his wits were touched", no "that") and exp_obj_passive constructions
    ("was amused by") the templated 4-atom set under-detects."""
    feats: List[str] = []
    if has_sentential_complement(tokens, v_idx):
        feats.append("has_scomp")
    elif (arg_idx is not None and arg_idx > v_idx and
          _clean(tokens[arg_idx]) in _NOMINATIVE_PRONOUNS):
        # Zero-complementizer finite clause: the post-verbal slot is filled by a NOMINATIVE-case
        # pronoun ("I fear HE is right", not "I fear HIM") -- real English case morphology signals
        # an embedded-clause subject, not a direct object. Not a parser; a case-form surface cue.
        feats.append("has_scomp")
    if is_degree_modified(tokens, v_idx):
        feats.append("degree_mod")
    if is_progressive(tokens, v_idx):
        feats.append("progressive")
    if is_passive_real(tokens, v_idx):
        feats.append("passive")
    if arg_idx is not None and arg_idx < v_idx:
        feats.append("order_pre")
    if _is_animate_head(tokens, arg_idx):
        feats.append("arg_animate")
    return feats


def _lemma_candidates(word: str) -> set:
    """Self-contained inflection-candidate generator for verb-token matching against a supplied
    lemma. Deliberately independent of thematic_role_labeler.lemma_verb(), which strips silent-e
    incorrectly for this purpose (e.g. 'loved'->'lov', 'amused'->'amus') -- here we want the FULL
    candidate SET (bare-stripped form AND the +e restore) so an exact-lemma match is reachable."""
    w = _clean(word)
    cands = {w}
    if w.endswith("ing") and len(w) > 4:
        base = w[:-3]
        cands.add(base)
        cands.add(base + "e")
        if len(base) > 2 and base[-1] == base[-2] and base[-1] not in "aeiou":
            cands.add(base[:-1])
    if w.endswith("ied") and len(w) > 4:
        cands.add(w[:-3] + "y")
    if w.endswith("ed") and len(w) > 3:
        base = w[:-2]
        cands.add(base)
        cands.add(base + "e")
        if len(base) > 2 and base[-1] == base[-2] and base[-1] not in "aeiou":
            cands.add(base[:-1])
    if w.endswith("es") and len(w) > 3:
        cands.add(w[:-2])
        cands.add(w[:-1])
    if w.endswith("s") and len(w) > 3 and not w.endswith("ss"):
        cands.add(w[:-1])
    return cands


def locate_verb_idx(tokens: Sequence[str], verb_lemma: str) -> Optional[int]:
    """First token whose inflection-candidate set contains `verb_lemma`. None if absent."""
    for i, t in enumerate(tokens):
        if verb_lemma in _lemma_candidates(t):
            return i
    return None


def locate_head_idx(tokens: Sequence[str], head: str, exclude: Sequence[int] = ()) -> Optional[int]:
    """First token (case-insensitive, punctuation-stripped) matching `head`, skipping `exclude`
    indices. `head` is already lowercased in the dataset. None if absent."""
    exclude = set(exclude)
    for i, t in enumerate(tokens):
        if i in exclude:
            continue
        if _clean(t) == head:
            return i
    return None


def build_real_episode(tokens: Sequence[str], v_idx: int, arg_idx: Optional[int],
                       gold_role: str) -> dict:
    """One real-data episode. Binary gold_class collapses the 6-way role vocabulary to
    EXPERIENCER vs OTHER (the axis this cell measures)."""
    gc = "EXPERIENCER" if gold_role == "EXPERIENCER" else "OTHER"
    return {"feats": real_construction_feats(tokens, v_idx, arg_idx), "gold_class": gc}


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


# ---------------------------------------------------------------------------------------------
# PRODUCTION WIRE (2026-08-05, WIRE-DON'T-ISLAND): train ONCE (module-level cache) the OOV-subject
# construction->frame hypothesis from the same REAL litbank-mined dataset + TRAIN split
# exp_frame_induction_oov_psych_real_v1 used for its own held-out eval, so a caller (situation_
# reader's frame-primary path) can supply (chosen_name, hypothesis) to frame_primary_role() for
# an OOV verb's subject slot instead of leaving chosen_name/hypothesis=None (which silently
# degrades every OOV psych verb to the AGENT default). Held-out lemmas
# (cherish/crave/dread/loathe/yearn subj-axis; astonish/embarrass/gladden/horrify/terrify obj-axis)
# are NEVER in the TRAIN split (leakage-checked by exp_frame_induction_oov_psych_real_v1's own
# assertion on the same file) -- production callers therefore see the SAME held-out generalization
# quality the cell measured: subj-axis acc=0.833, obj-axis acc=0.455 (both MIDDLE_BAND, data-
# starved, not a ceiling -- see data/exp_frame_induction_oov_psych_real_v1/metrics.json). The
# obj-axis model is deliberately NOT wired into frame_primary_role (unchanged design below: OOV+obj
# always falls to DEFAULT_FRAME) -- this getter only trains the shared subj-axis hypothesis.
# ---------------------------------------------------------------------------------------------
DEFAULT_REAL_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "data", "experiencer_narrative_roles_v1.jsonl")

_INDUCED_SUBJ_HYP_CACHE: dict = {}

# PERSISTENT DISK CACHE for the induced subject hypothesis (2026-09-03 perf fix). The induction is a
# DETERMINISTIC ~130s program-enumeration (612M expression evals) run on the FIRST read() of every
# fresh process -- the in-process cache above only amortizes WITHIN a process, so every witness /
# benchmark / board process re-paid it (this was mis-diagnosed as a disk "cold start"; it is COMPUTE,
# not I/O). The result (chosen_name, hypothesis-dict) is a pure function of (train-file content, spec),
# so we persist it: only the FIRST-EVER build pays ~130s; every process after loads in ~ms. Keyed by a
# content hash of the train file + the spec (atoms/max_nodes/classes) so any data/spec change auto-
# invalidates. Byte-identical to re-inducing (witness: test_frame_induction_cache_speed_organ.py).
_INDUCED_SUBJ_HYP_DISK_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "frame_induction_cache")
_INDUCED_CACHE_VERSION = "proginduction_v1"


def _induced_cache_key(path: str, spec: dict) -> Optional[str]:
    """sha1 over (train-file bytes + the induction-relevant spec fields + a version tag). None if the
    file is unreadable (then we skip the disk cache and fall through to a live induce)."""
    try:
        with open(path, "rb") as fh:
            file_bytes = fh.read()
    except (OSError, IOError):
        return None
    pi = (spec or {}).get("per_plugin", {}).get("proginduction", {})
    spec_sig = json.dumps({"atoms": pi.get("atoms"), "max_nodes": pi.get("max_nodes"),
                           "classes": pi.get("classes"), "v": _INDUCED_CACHE_VERSION},
                          sort_keys=True).encode("utf-8")
    h = hashlib.sha1()
    h.update(file_bytes)
    h.update(b"|")
    h.update(spec_sig)
    return h.hexdigest()


def _load_induced_disk_cache(path: str, spec: dict):
    """Return the cached (chosen_name, hypothesis) tuple, or None on any miss/corruption (never raises)."""
    key = _induced_cache_key(path, spec)
    if key is None:
        return None
    fp = os.path.join(_INDUCED_SUBJ_HYP_DISK_DIR, "subj_hyp_" + key + ".pkl")
    if not os.path.exists(fp):
        return None
    try:
        with open(fp, "rb") as fh:
            obj = pickle.load(fh)
        if isinstance(obj, tuple) and len(obj) == 2:
            return obj
    except Exception:
        return None
    return None


def _save_induced_disk_cache(path: str, spec: dict, result) -> None:
    """Persist (chosen_name, hypothesis) atomically. Best-effort -- a write failure just means the next
    process re-induces (correct, only slower)."""
    key = _induced_cache_key(path, spec)
    if key is None:
        return
    try:
        os.makedirs(_INDUCED_SUBJ_HYP_DISK_DIR, exist_ok=True)
        fp = os.path.join(_INDUCED_SUBJ_HYP_DISK_DIR, "subj_hyp_" + key + ".pkl")
        tmp = fp + ".tmp"
        with open(tmp, "wb") as fh:
            pickle.dump(result, fh, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, fp)
    except Exception:
        pass


def _load_real_train_episodes(data_path: str) -> List[dict]:
    """TRAIN-split-only episodes from the real litbank-mined psych-verb dataset, built with the
    SAME real_construction_feats/build_real_episode adapter exp_frame_induction_oov_psych_real_v1
    uses for its own train corpus (mirrors that cell's build_corpus() train branch; held-out
    records are intentionally excluded here -- production must never train on the eval lemmas)."""
    recs = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    eps: List[dict] = []
    for r in recs:
        if r.get("split_recommendation") != "train":
            continue
        tokens = r["text"].split()
        v_idx = locate_verb_idx(tokens, r["verb_lemma"])
        if v_idx is None:
            continue
        for a in r["args"]:
            a_idx = locate_head_idx(tokens, a["head"])
            if a_idx is None:
                continue
            eps.append(build_real_episode(tokens, v_idx, a_idx, a["role"]))
    return eps


def get_induced_subj_hypothesis(data_path: Optional[str] = None,
                                 use_cache: bool = True) -> Tuple[Optional[str], Optional[object]]:
    """Return the cached (chosen_name, hypothesis) trained on the real TRAIN-split psych-verb data,
    for use as frame_primary_role's chosen_name/hypothesis args on an OOV verb's subject slot.
    Trains at most once per process (module-level cache keyed by data_path) -- callers on a hot
    labeling path must NOT re-induce per call. Returns (None, None) (an honest degrade, identical
    to leaving chosen_name/hypothesis unset) if the training file is missing/unreadable or
    induction abstains -- this must never raise on a production read() call."""
    path = data_path or DEFAULT_REAL_DATA_PATH
    if use_cache and path in _INDUCED_SUBJ_HYP_CACHE:
        return _INDUCED_SUBJ_HYP_CACHE[path]
    result: Tuple[Optional[str], Optional[object]] = (None, None)
    try:
        train_eps = _load_real_train_episodes(path)
        if train_eps:
            classes = sorted({ep["gold_class"] for ep in train_eps})
            spec = default_spec(classes, atoms=REAL_CONSTRUCTION_ATOMS)
            # DISK CACHE: skip the ~130s deterministic induction if a prior process already built it.
            disk = _load_induced_disk_cache(path, spec) if use_cache else None
            if disk is not None:
                result = disk
            else:
                chosen_name, chosen, _all = induce(train_eps, spec=spec)
                if chosen is not None:
                    result = (chosen_name, chosen.hypothesis)
                    if use_cache:
                        _save_induced_disk_cache(path, spec, result)
    except (OSError, IOError, ValueError, KeyError):
        result = (None, None)
    if use_cache:
        _INDUCED_SUBJ_HYP_CACHE[path] = result
    return result


# ---------------------------------------------------------------------------------------------
# FRAME-PRIMARY role assignment (2026-08-05, Component-3 goal-owner fix): the VERB FRAME is the
# role-determining signal for a known lemma -- ALWAYS, never re-ranked or overridden by a learned
# position/animacy prior. This is the direct fix for the shelved flat-perceptron
# (exp_thematic_role_labeler_cue_integration_v1, notes/skunkworks_reVET_thematic_role_labeler_
# cue_integration_v1.md): that perceptron learned "order:pre -> AGENT" from a canonical-dominated
# training distribution and OVERRODE the correct frame signal for pre-verbal experiencer subjects
# (experiencer-axis acc 0.614 vs frame_only 0.857, a -0.24 EARNED-MECHANISM-HURTS regression).
# Here there is no re-ranking layer: KNOWN verb -> frame_slot_role() answers directly and
# UNCONDITIONALLY (position/animacy are never even consulted). OOV verb -> the induced
# construction->frame hypothesis (this module) supplies the subject-slot answer, falling back to
# `default` only when the hypothesis abstains. Position/animacy are used ONLY inside the induced
# hypothesis's own feature set (as construction cues among several, per Gleitman/Naigles
# bootstrapping), never as a hard override on a frame-determined role.
# ---------------------------------------------------------------------------------------------
def frame_primary_role(lemma: str, tokens: Sequence[str], v_idx: int, arg_idx: Optional[int],
                       slot: str, chosen_name: Optional[str] = None, hypothesis=None,
                       default: str = "AGENT") -> str:
    """FRAME-PRIMARY role assigner for ONE (verb, argument) pair. `slot` in {"subj","obj"}.

    KNOWN verb (lemma in VERB_FRAMES): return frame_slot_role(lemma, slot) UNCONDITIONALLY --
    this is the fix; no learned component ever sees or re-ranks this answer.

    OOV verb, slot=="subj": consult the induced construction-cue hypothesis
    (chosen_name/hypothesis, from `induce()` over REAL_CONSTRUCTION_ATOMS); returns EXPERIENCER
    if the hypothesis predicts EXPERIENCER, else `default` (an honest, measurable degrade path,
    same semantics as predict_subj_role's own default handling).

    OOV verb, slot=="obj" (or any slot besides "subj"): no induced obj-frame model exists yet
    (deferred affect axis per the goal-owner scoping decision); returns DEFAULT_FRAME's role for
    that slot (position-only fallback -- honestly the current known-bad behavior for this slot,
    not silently disguised as earned).
    """
    if lemma in VERB_FRAMES:
        return frame_slot_role(lemma, slot)
    if slot != "subj":
        return DEFAULT_FRAME.get(slot, default)
    if chosen_name is None or hypothesis is None or arg_idx is None:
        return default
    feats = real_construction_feats(tokens, v_idx, arg_idx)
    pred = predict_subj_role(chosen_name, hypothesis, feats, default="OTHER")
    return "EXPERIENCER" if pred == "EXPERIENCER" else default


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


def _selftest_real_adapter() -> None:
    # Zero-complementizer finite clause ("I began to fear his wits were touched"): no overt "that",
    # locate_verb_idx must find "fear" (not "began" or "touched"), and the nominative-pronoun cue
    # must fire for a post-verbal embedded-clause subject NOUN is absent here (wits is a noun, not
    # a pronoun) so has_scomp relies on the base complementizer/to-infinitive detector instead --
    # verify locate + order_pre + animacy behave correctly regardless.
    toks = "I began to fear his wits were touched .".split()
    v = locate_verb_idx(toks, "fear")
    assert v is not None and _clean(toks[v]) == "fear", "locate_verb_idx failed on 'fear': %r" % (toks[v] if v is not None else None)
    wi = locate_head_idx(toks, "wits")
    assert wi is not None and wi > v
    f_theme = real_construction_feats(toks, v, wi)
    assert "order_pre" not in f_theme  # wits is post-verbal
    ii = locate_head_idx(toks, "i")
    assert ii is not None and ii < v
    f_subj = real_construction_feats(toks, v, ii)
    assert "order_pre" in f_subj and "arg_animate" in f_subj  # "I" is pre-verbal + nominative

    # Nominative-case zero-complementizer cue: "I fear he is right" (not "him") -> has_scomp fires
    # on the post-verbal argument via case-form, not an overt complementizer.
    toks_case = "I fear he is right .".split()
    vc = locate_verb_idx(toks_case, "fear")
    hei = locate_head_idx(toks_case, "he")
    f_case = real_construction_feats(toks_case, vc, hei)
    assert "has_scomp" in f_case

    # Passive + silent-e lemma matching: "He was amused by her conversation." verb_lemma="amuse".
    toks2 = "He was amused by her conversation .".split()
    v2 = locate_verb_idx(toks2, "amuse")
    assert v2 is not None and _clean(toks2[v2]) == "amused"
    hi2 = locate_head_idx(toks2, "he")
    f2 = real_construction_feats(toks2, v2, hi2)
    assert "passive" in f2 and "order_pre" in f2 and "arg_animate" in f2

    # Active exp_obj construction: "It frightened the child." subject "it" pre-verbal + inanimate.
    toks3 = "It frightened the child .".split()
    v3 = locate_verb_idx(toks3, "frighten")
    assert v3 is not None
    it_i = locate_head_idx(toks3, "it")
    f3 = real_construction_feats(toks3, v3, it_i)
    assert "order_pre" in f3 and "arg_animate" not in f3  # "it" is the inanimate-pronoun cue
    child_i = locate_head_idx(toks3, "child")
    f3b = real_construction_feats(toks3, v3, child_i)
    assert "order_pre" not in f3b  # child is post-verbal (object)

    # Silent-e past tense not in the standard lemma_verb() table: 'loved'->lemma_verb gives 'lov'
    # (wrong for exact-match lookup), but locate_verb_idx's candidate set must still find "love".
    toks4 = "He loved her deeply .".split()
    v4 = locate_verb_idx(toks4, "love")
    assert v4 is not None and _clean(toks4[v4]) == "loved"

    # build_real_episode never leaks the lemma into feats.
    ep = build_real_episode(toks2, v2, hi2, "EXPERIENCER")
    assert ep["gold_class"] == "EXPERIENCER"
    assert "amuse" not in " ".join(ep["feats"])
    print("[selftest] PASS: frame_induction real-adapter", flush=True)


def _selftest_frame_primary() -> None:
    # KNOWN verb, pre-verbal ANIMATE subject (the exact configuration the shelved perceptron
    # overrode to AGENT via its order:pre cue): frame-primary MUST stay EXPERIENCER, unconditionally,
    # regardless of any position/animacy signal -- no re-ranking layer exists for known verbs.
    toks = "He dreaded the interview .".split()
    assert frame_primary_role("dread", toks, 1, 0, "subj") == "EXPERIENCER"
    # Known agentive verb: subj = AGENT (frame table, unconditional).
    toks2 = "He kicked the ball .".split()
    assert frame_primary_role("kick", toks2, 1, 0, "subj") == "AGENT"
    # OOV verb, no induced hypothesis supplied (chosen_name/hypothesis=None) -> honest default.
    toks3 = "He cherished the ring .".split()
    assert frame_primary_role("cherish", toks3, 1, 0, "subj") == "AGENT"
    # OOV verb, obj slot -> DEFAULT_FRAME fallback (deferred axis), not silently upgraded.
    assert frame_primary_role("frighten", ["it", "frightened", "him"], 1, 2, "obj") == "PATIENT"
    # OOV verb, subj slot, WITH an induced hypothesis that fires EXPERIENCER on scomp -> obeys it.
    eps = []
    for _ in range(6):
        eps.append(build_episode(["x", "verb", "that", "y", "z"], 1, 0, "EXPERIENCER"))
        eps.append(build_episode(["x", "verb", "the", "y"], 1, 0, "AGENT"))
    name, chosen, _ = induce(eps)
    toks4 = "novelsubj novelverb that the storm".split()
    assert frame_primary_role("novelverb", toks4, 1, 0, "subj",
                              chosen_name=name, hypothesis=chosen.hypothesis) == "EXPERIENCER"
    print("[selftest] PASS: frame_induction frame_primary_role", flush=True)


if __name__ == "__main__":
    _selftest()
    _selftest_real_adapter()
    _selftest_frame_primary()
