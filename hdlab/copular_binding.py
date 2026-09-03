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
from collections import defaultdict

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the copular solution's OWN validated frontend assets (so the promoted path == the validated experiment)
POS_ASSET = os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_ASSET = os.path.join(_REPO, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
LAB_ASSET = os.path.join(_REPO, "data", "frontend_assets", "arc_labeler_hashed_ud_ewt.json")

# Higgins definiteness cues (verbatim from the validated classifier)
DEF_DET = {"the", "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their"}
INDEF_DET = {"a", "an", "some", "any", "another", "one"}

# robust_cop closed-class lexicons (verbatim from exp_copular_is_a_binding_readout_v1)
BE_LEMMAS = {"be", "is", "are", "was", "were", "been", "being", "am", "'s", "'re", "'m"}
LINK_LEMMAS = {"become", "became", "seem", "seemed", "remain", "remained", "prove", "proved"}
EXPLETIVE = {"there", "here"}


def robust_cop(toks, up, heads, gate=True):
    """THE LABEL-ROBUST detection fix (verbatim from exp_copular_is_a_binding_readout_v1.robust_cop). The dominant
    entity-state capability loss is DETECTION -- the arc labeler's `cop` recall is low (it labels a nominal
    predicate `nsubj`/`root`, worst on the equative identity type). The copula BE is a CLOSED-CLASS functional
    carrier (PINNED), so predication detection should NOT be gated on a fragile dependency label. Fire on each
    copula/linking TOKEN; predicate = its parse-tree head (if a content word) ELSE the next content head; holder =
    the tree nominal-child of that predicate preceding the copula ELSE the nearest preceding nominal. Robust to the
    labeler's `cop` miss; UNION with the label path (extract_entity_states). gate: skip existential expletive
    holders + an intervening main VERB (progressive/passive aux, clefts). Returns a set of (holder_idx, prop_idx)."""
    n = len(toks)
    out = set()
    children = defaultdict(list)
    for d in range(1, n + 1):
        h = heads.get(d, 0)
        if h:
            children[h].append(d - 1)
    for i in range(n):
        lem = toks[i].lower()
        if not (lem in BE_LEMMAS or up[i] == "AUX" or lem in LINK_LEMMAS):
            continue
        ph = heads.get(i + 1, 0) - 1
        p = None
        if 0 <= ph < n and up[ph] in ("NOUN", "PROPN", "ADJ", "PRON"):
            p = ph
        else:
            j = i + 1
            while j < n and up[j] in ("DET", "ADV", "PART", "NUM", "ADJ"):
                j += 1
            if j < n and up[j] in ("NOUN", "PROPN", "PRON"):
                k = j
                while k + 1 < n and up[k + 1] in ("NOUN", "PROPN"):
                    k += 1
                p = k
        if p is None:
            continue
        noms = [c for c in children.get(p + 1, []) if up[c] in ("NOUN", "PROPN", "PRON") and c < i]
        if noms:
            holder = max(noms)
        else:
            holder = None
            for k in range(i - 1, -1, -1):
                if up[k] in ("NOUN", "PROPN", "PRON"):
                    holder = k
                    break
        if holder is None or holder == p:
            continue
        if gate:
            if toks[holder].lower() in EXPLETIVE:
                continue
            if any(up[q] == "VERB" for q in range(holder + 1, p)):
                continue
        out.add((holder, p))
    return out


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
