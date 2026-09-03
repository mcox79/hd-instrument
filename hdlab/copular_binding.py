"""copular_binding.py -- the COPULAR is-a/attribute binding primitives, promoted VERBATIM (2026-09-03) from the
owner-DONE `the_reader_has_no_copular_is_a_binding_schema` (core 10/10 + improvements 6/6).

The copula BE is a near-empty functional carrier; the MEANING is the predication relation binding the complement
to the subject ENTITY node (Higgins 1979; Mikkelsen 2011; Maienborn 2005 Kimian states; Bemis & Pylkkanen 2011
LATL property-attribution). Two pure, glass-box functions (NO LLM, NO spaCy):
  - extract_entity_states(toks, up, arc, lab): the labeled `cop`-arc HOLDER+PROPERTY binding (high-precision path;
    read-back recall 0.672 CI-separated over the most-recent-noun floor, shuffle twin loses).
  - predicted_type(toks, up, holder, prop): the glass-box Higgins classifier -- predicational (property/is-a:
    pred_adj / pred_nom) vs identificational (identity: ident), from surface referential-status cues (0.969 coarse).

Promoted here so hdlab.situation_reader (bind_entity_states flag) does not depend on the experiments/ cell at
inference. Byte-faithful to experiments._copular_nominal_events.extract_entity_states +
experiments.exp_copular_is_a_binding_readout_v1.predicted_type (witness: test_copular_is_a_binding_landing_organ.py).
"""
from __future__ import annotations

import os

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the copular solution's OWN validated frontend assets (so the promoted path == the validated experiment)
POS_ASSET = os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_ASSET = os.path.join(_REPO, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
LAB_ASSET = os.path.join(_REPO, "data", "frontend_assets", "arc_labeler_hashed_ud_ewt.json")

# Higgins definiteness cues (verbatim from the validated classifier)
DEF_DET = {"the", "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their"}
INDEF_DET = {"a", "an", "some", "any", "another", "one"}


def extract_entity_states(toks, up, arc, lab):
    """[(holder_idx, property_idx)] 0-based, from the labeled parse: for each `cop` arc, PROPERTY = its head,
    HOLDER = the nsubj/nsubj:pass/csubj dependent of that same head. Brain-faithful HOLDER+PROPERTY binding."""
    try:
        heads = arc.parse(toks, up).heads
        labels = lab.label(toks, up, heads)
    except Exception:
        return []
    cop_preds = set()
    for dep_i, rel in labels.items():
        if rel == "cop":
            h = heads.get(dep_i, 0)
            if h and 1 <= h <= len(toks):
                cop_preds.add(h)                        # 1-based predicate id
    subj_of = {}
    for dep_i, rel in labels.items():
        if rel in ("nsubj", "nsubj:pass", "csubj"):
            h = heads.get(dep_i, 0)
            if h in cop_preds and h not in subj_of:
                subj_of[h] = dep_i                      # 1-based holder id
    out = []
    for pred in sorted(cop_preds):
        if pred in subj_of:
            out.append((subj_of[pred] - 1, pred - 1))   # (holder_idx, property_idx) 0-based
    return out


def predicted_type(toks, up, holder, prop):
    """GLASS-BOX Higgins classifier from surface referential-status cues (no gold deprels, no LLM).
    predicational (property/is-a) vs identificational (identity)."""
    u = up[prop]
    if u == "ADJ":
        return "pred_adj"
    if u == "PROPN":
        return "ident"
    # look left of the property for its determiner (skip adjectives/nouns in the NP)
    det = None
    for k in range(prop - 1, max(-1, prop - 5), -1):
        w = toks[k].lower()
        if up[k] == "DET" or w in DEF_DET or w in INDEF_DET:
            det = w
            break
        if up[k] in ("PUNCT", "VERB", "AUX"):
            break
    if det in DEF_DET:
        return "ident"
    return "pred_nom"
