"""test_audit_live_standins -- scaffold-free WITNESS for the breadth audit
`audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements`.

It is a PURE DISK witness (reads hdlab source as text; no torch/nltk import, no read() run, no
network) that reproduces the catalog's load-bearing LIVE-vs-DORMANT + already-remediated claims,
so the catalog cannot be a stale keyword-grep list. Every assertion is a can-fail check on the
current bytes of hdlab/. Run:  .venv/Scripts/python.exe verification/test_audit_live_standins.py

Controls baked in (a control that excludes nothing is not one):
  * POSITIVE control (W11): the enumeration recovers EVERY CONT-28-named component (no silent miss).
  * NEGATIVE / do-not-over-fire control (W12): the two WordNet-landed lexicon fallbacks + the spaCy
    purge are confirmed, so they are NOT flagged as live defects (excludes false positives).
  * LIVE-vs-DORMANT control (W3/W6/W7/W9/W10): grep situation_reader's import closure -- landed != live.
"""
from __future__ import annotations

import os
import re
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HDLAB = os.path.join(_REPO, "hdlab")


def _read(rel):
    with open(os.path.join(_REPO, rel), encoding="utf-8") as f:
        return f.read()


def _hdlab_pyfiles():
    out = []
    for dp, _dn, fn in os.walk(_HDLAB):
        if "__pycache__" in dp:
            continue
        for f in fn:
            if f.endswith(".py"):
                out.append(os.path.join(dp, f))
    return out


SR = _read("hdlab/situation_reader.py")
PASSED = []
SUPERSEDED = []

# 2026-09-16 (strategy, LOCATED item 16 from pri 137): this witness pinned the AUDIT CATALOG'S SNAPSHOT of the live
# tree (gold-coref leak present, gate default ON, arceager default ON, the fitted parse_confidence live, experiments/*
# imported at inference...). Those were the DEFECTS the catalog named, and the landings since remediated them
# (pri 109 gold-free rows; the 09-11 gate retirement; the 09-13 BF heads default; pri 129 NOT_BF readouts off the
# default read; pri 127 no library at read time; pri 137 one space reader). A witness that asserts a defect is
# PRESENT turns red exactly when the defect is fixed. The claims that describe the REMEDIATED state (W10: zero
# spaCy in hdlab; W12: the WordNet-landed fallbacks are real, not live defects) stay ASSERTED; every snapshot claim
# is REPORTED (holds / no longer holds) when the tree is detected as remediated (the gate default is False).
_REMEDIATED = re.search(r"commonnoun_situation_gate:\s*bool\s*=\s*False", SR) is not None
_STILL_ASSERTED = ("W10", "W12")


def _ok(tag, cond, detail=""):
    if _REMEDIATED and not tag.startswith(_STILL_ASSERTED):
        SUPERSEDED.append((tag, bool(cond)))
        print("  [SNAPSHOT %s] %s %s" % ("holds" if cond else "no longer holds (remediated)", tag, detail))
        return
    assert cond, "%s FAILED %s" % (tag, detail)
    PASSED.append(tag)
    print("  [OK] %s %s" % (tag, detail))


# W1 -- the GOLD-COREF-INHERITANCE leak is present + LIVE (C1, #1 blast).
_ok("W1a gold read",
    'anchored = {m["cluster"] for m in (self._coref_mentions' in SR)
_ok("W1b gold majority-vote",
    "Counter(gold).most_common(1)[0][0]" in SR)
_ok("W1c gold overwrite",
    re.search(r'm\["cluster"\]\s*=\s*lab_to_cluster\[lab\]', SR) is not None)
_ok("W1d gate default ON (stale 'default OFF' docstring notwithstanding)",
    re.search(r"commonnoun_situation_gate:\s*bool\s*=\s*True", SR) is not None)
_ok("W1e gate is called before sm.entities is built",
    "if self.commonnoun_situation_gate:" in SR and "sm.entities = _build_entities(role_mentions)" in SR)

# W2 -- commonnoun_binder.situation_predict is the LIVE clustering (C2); entity_kb_resolver default OFF -> else-branch.
_ok("W2a situation_predict live else-branch (window=16 hardcoded)",
    "_CN.situation_predict(role_mentions, self.gaz, window=16" in SR)
_ok("W2b entity_kb_resolver default OFF (so the else-branch runs)",
    re.search(r"entity_kb_resolver:\s*bool\s*=\s*False", SR) is not None)

# W3 -- arceager surface-feature scorer is LIVE (C3); incremental_parser built-but-DORMANT replacement.
_ok("W3a arceager parser default ON",
    re.search(r"parser_arceager:\s*bool\s*=\s*True", SR) is not None)
_ok("W3b arceager imported at the live head source",
    "from hdlab.arceager_parser import" in SR)
_ok("W3c the built brain-faithful replacement incremental_build is NOT wired (dormant)",
    "incremental_build" not in SR)
_ok("W3d the globally-normalized graded_parser marginals are NOT wired (dormant)",
    "graded_parser" not in SR)

# W4 -- parse_confidence: LIVE-computed fitted logistic + PURE-DEFER that never fires (C5).
_ok("W4a precision_weight_roles ON (the logistic runs every event)",
    re.search(r"precision_weight_roles:\s*bool\s*=\s*True", SR) is not None)
_ok("W4b precision_weight_tau default None => defer dead",
    re.search(r"precision_weight_tau:\s*Optional\[float\]\s*=\s*None", SR) is not None)
_ok("W4c defer is gated on tau is not None (so it never fires by default)",
    "if p_conf is not None and tau is not None:" in SR)

# W5 -- SELF-CONTAINMENT debt: experiments/* imported AT INFERENCE on the live path (C4).
cgv = _read("hdlab/context_grounded_valence.py")
_ok("W5a context_grounded_valence imports experiments/* at MODULE level",
    re.search(r"^import experiments\.", cgv, re.M) is not None)
_ok("W5b reader's DIRECT _space_reader/_belief_reader imports PROMOTED (strategy CONT-29 2026-09-09); residual is now transitive via context_grounded_valence + temporal_reasoner",
    "from experiments import _space_reader" not in SR and "from experiments import _belief_reader" not in SR)
tr = _read("hdlab/temporal_reasoner.py")
_ok("W5c temporal_reasoner imports experiments/* at MODULE level (live: track_temporal_reasoning default ON)",
    re.search(r"^from experiments import", tr, re.M) is not None
    and re.search(r"track_temporal_reasoning:\s*bool\s*=\s*True", SR) is not None)

# W6 -- context_grounded_valence governor PERCEPTRON is cert-fit (C6) but decision-dead behind _assign_affect.
_ok("W6a cert-fit governor perceptron present",
    "train_perceptron(" in cgv and "_governor_pred_fn" in cgv)
_ok("W6b reader discards non-event affect stages (perceptron output never reaches sm.events)",
    'result["stage"] != "event"' in SR)

# W7 -- cleanup_family / hd_fact_store are DORMANT wrt situation_reader.read() (CORRECTS CONT-28 'live via gap_detector').
for dead in ("cleanup_family", "gap_detector", "hd_fact_store", "GapDetector"):
    _ok("W7 %s NOT in the reader import closure (dormant wrt read())" % dead, dead not in SR)

# W8 -- coref name-Jaccard is MISATTRIBUTED: the Jaccard matcher lives in coreference_resolver.py, DORMANT wrt reader.
cref = _read("hdlab/coreference_resolver.py")
_ok("W8a the token-Jaccard matcher is in coreference_resolver.py (not coref.py)",
    re.search(r"&\s*e\.tokens", cref) is not None or "Jaccard" in cref or "jaccard" in cref)
_ok("W8b coreference_resolver is DORMANT wrt the live reader",
    "coreference_resolver" not in SR)

# W9 -- scene_segment fixed window: the cue-detector is DORMANT (only parse_conll_sentences imported).
_ok("W9 scene_segment.detect_scene_boundaries is NOT wired (only parse_conll_sentences is)",
    "detect_scene_boundaries" not in SR and "from hdlab.scene_segment import parse_conll_sentences" in SR)

# W10 -- ZERO spaCy anywhere in hdlab (perceptual_access_ledger + causation_typing purge CONFIRMED).
spacy_hits = []
for p in _hdlab_pyfiles():
    with open(p, encoding="utf-8") as f:
        t = f.read()
    if re.search(r"^\s*import spacy|spacy\.load\(", t, re.M):
        spacy_hits.append(os.path.relpath(p, _REPO))
_ok("W10 no spaCy-at-inference anywhere in hdlab/", not spacy_hits, str(spacy_hits))

# W11 -- POSITIVE CONTROL: the enumeration recovers EVERY CONT-28-named component (files exist on disk).
cont28 = ["situation_reader.py", "commonnoun_binder.py", "arceager_parser.py", "parse_confidence.py",
          "context_grounded_valence.py", "perceptual_access_ledger.py", "causation_typing.py",
          "cleanup_family.py", "hd_fact_store.py", "state_register.py", "location_register.py",
          "coref.py", "lexical_similarity.py", "grounded_similarity.py", "scene_segment.py"]
missing = [f for f in cont28 if not os.path.exists(os.path.join(_HDLAB, f))]
_ok("W11 positive control: all CONT-28-named components enumerated (present on disk)", not missing, str(missing))

# W12 -- NEGATIVE / do-not-over-fire CONTROL: the WordNet-landed fallbacks are real (so NOT flagged).
sreg = _read("hdlab/state_register.py")
loc = _read("hdlab/location_register.py")
_ok("W12a state_register.incompatible() has a WordNet antonymy fallback (LANDED -> not a live defect)",
    "_wn_adj_antonyms" in sreg)
_ok("W12b location_register region taxonomy has a WordNet fallback (LANDED -> not a live defect)",
    ("wordnet" in loc.lower()) and ("holonym" in loc.lower() or "hypernym" in loc.lower()))

print("\n%d/%d witnesses passed." % (len(PASSED), len(PASSED)))
if _REMEDIATED:
    _gone = [t for t, c in SUPERSEDED if not c]
    print("AUDIT WITNESS GREEN (remediated tree): %d snapshot claims reported, %d no longer hold = defects fixed since "
          "the catalog (%s); the remediated-state claims (W10, W12) are asserted." % (len(SUPERSEDED), len(_gone),
          ", ".join(t.split()[0] for t in _gone)))
else:
    print("AUDIT WITNESS GREEN -- the catalog's live/dormant/remediated claims reproduce on the current hdlab/ bytes.")


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
# This file's checks run unconditionally at module import (no `if __name__ ==
# "__main__":` guard) -- already during pytest's COLLECTION, before any test runs.
# A failure already surfaces as a pytest COLLECTION ERROR; this function exists only
# so the discovery gate sees a witness ran here, and does not re-run the checks.
import pytest as _pri128_pytest


@_pri128_pytest.mark.fast
def test_witness():
    assert True
