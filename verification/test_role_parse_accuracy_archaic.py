"""Scaffold-free witness for role_assignment_is_untested_on_archaic_literary_prose.

Asserts the load-bearing claims (fast, spaCy LOCAL for the mechanism checks; landed metrics for the
CI-separated aggregates):
  1. spaCy identifies the SUBJECT on canonical prose (modern AND archaic) -> the confound is NOT
     wholesale (the brief's 'systematically degraded on archaic prose' is not supported).
  2. spaCy FAILS on subject-verb INVERSION ('Said he' -> tags 'he' as a non-subject) -- the real locus.
  3. A NOMINATIVE pronoun labeled OBJECT is a parse error a human never makes (the CASE cue).
  4. The brain-faithful cue-repair RECOVERS a clean inversion and does NOT regress canonical sentences.
  5. Landed aggregates: (A) natural archaic subject-acc >= modern (wholesale null); (B) downstream coref
     delta ~0 while the shuffled positive control moves; (C) cue-repair beats the spaCy floor CI-sep on
     real dialogue inversion with the info-free twin LOSING.

Run: .venv/Scripts/python.exe verification/test_role_parse_accuracy_archaic.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_role_parse_accuracy_probe_v1 as A
import experiments.exp_role_cue_repair_inversion_v1 as R
import experiments.exp_role_confound_downstream_coref_v1 as B

nlp = A._load_spacy()
PASS = 0


def check(name, cond):
    global PASS
    assert cond, f"FAIL: {name}"
    PASS += 1
    print(f"  ok: {name}")


def subj_ok(text, subj_tok, verb_tok, mode="raw"):
    doc = nlp(text)
    sp = R.repaired_subject_span(doc, A._tok_span(text, verb_tok), mode=mode)
    return bool(sp) and A._overlap(sp, A._tok_span(text, subj_tok))


def _metrics(anchor):
    with open(os.path.join(_REPO, "data", "exp_" + anchor, "metrics.json"), encoding="utf-8") as f:
        return json.load(f)


print("[1] spaCy handles CANONICAL subjects (modern + archaic) -- confound is NOT wholesale")
check("canonical modern 'The enzyme breaks the bond'", subj_ok("The enzyme breaks the bond.", 1, 2, "raw"))
check("canonical archaic 'He made a violent thrust'", subj_ok("He made a violent thrust with the ruler.", 0, 1, "raw"))
check("long archaic full-NP subject", subj_ok("The astonishment of the ladies was exactly what he wished.", 1, 5, "raw"))

print("[2] spaCy FAILS on subject-verb INVERSION (the real locus)")
check("'Said he to the crowd' inversion raw FAILS", not subj_ok("Said he to the crowd.", 1, 0, "raw"))
check("'Down came the rain' inversion raw FAILS", not subj_ok("Down came the heavy rain.", 3, 1, "raw"))

print("[3] a NOMINATIVE pronoun labeled OBJECT is a parse error the CASE cue fixes")
st = [{"doc": "t", "stream": [{"sent": 0, "gold": 1, "role": "OBJECT", "head_text": "he", "gov_verb": "say"},
                              {"sent": 1, "gold": 2, "role": "OBJECT", "head_text": "him", "gov_verb": "hit"}]}]
corrected, n_case, n_frame = B.correct_roles(st)
check("nominative 'he'+reporting -> SUBJECT (frame fix)", corrected[0]["stream"][0]["role"] == "SUBJECT" and n_frame == 1)
check("accusative 'him' stays OBJECT (case cue is specific)", corrected[0]["stream"][1]["role"] == "OBJECT")

print("[4] brain-faithful cue-repair RECOVERS a clean inversion, no canonical regression")
check("'Said he to the crowd' repaired -> SUBJECT recovered", subj_ok("Said he to the crowd.", 1, 0, "cue"))
check("canonical modern unchanged under repair", subj_ok("The enzyme breaks the bond.", 1, 2, "cue"))
check("canonical archaic unchanged under repair", subj_ok("He made a violent thrust with the ruler.", 0, 1, "cue"))

print("[5] landed aggregates reproduce the headline")
mA = _metrics("role_parse_accuracy_probe_v1")
check("natural archaic subject-acc >= modern (wholesale NULL)",
      mA["arms"]["archaic_hand"]["subject_acc_lenient"] >= mA["arms"]["modern_hand"]["subject_acc_lenient"])
mB = _metrics("role_confound_downstream_coref_v1")
cb = mB["coref_strict_cb_accuracy"]
check("downstream coref delta ~0 (|delta| < 0.01)", abs(cb["delta_corrected_minus_spacy"]) < 0.01)
check("positive control: shuffled roles MOVE the coref metric",
      cb["shuffled_roles_POSITIVE_CONTROL"] < cb["spacy_roles"] - 0.03)
mC = _metrics("role_cue_repair_inversion_v1")
inv = mC["arms"]["litbank_real_dialogue_inversion"]
check("cue-repair beats spaCy floor CI-sep on real dialogue inversion", inv["repair_beats_raw_ci_sep"])
check("info-free twin LOSES to cue-repair CI-sep", inv["repair_beats_twin_ci_sep"])
check("register-invariance after repair (gap < 0.10)",
      abs(mC["register_invariance_after_repair"]["register_gap_after_repair"]) < 0.10)

print("[6] architecture: position-dominant+override beats cue-first-replacement; incremental fails inversion")
mD = _metrics("role_cue_first_subject_v1")
inv2 = mD["sets"]["litbank_dialogue_inversion"]
mod2 = mD["sets"]["modern_hand_REGRESSION"]
check("incremental_parser FAILS dialogue inversion (< 0.20)", inv2["incremental"]["acc"] < 0.20)
check("cue-first REPLACEMENT regresses modern below post-hoc (override architecture is right)",
      mod2["cue_first"]["acc"] < mod2["posthoc"]["acc"])
check("post-hoc override recovers archaic morphology where spaCy raw = 0",
      mD["sets"]["archaic_morphology_hard"]["posthoc"]["acc"] >= 0.8
      and mD["sets"]["archaic_morphology_hard"]["spacy_raw"]["acc"] < 0.2)

print("[7] the full brain-faithful cue cascade (position-dominant + all PINNED cue overrides)")
cf = mD["sets"]
check("full cascade recovers collapsed full-NP inversion (>= 0.75, vs raw < 0.6)",
      cf["collapsed_parse_hard"]["cue_override_full"]["acc"] >= 0.75
      and cf["collapsed_parse_hard"]["spacy_raw"]["acc"] < 0.6)
check("full cascade beats spaCy floor on real dialogue inversion (>= 0.8 vs ~0.47)",
      cf["litbank_dialogue_inversion"]["cue_override_full"]["acc"] >= 0.8)
check("full cascade does NOT regress modern (>= spaCy raw)",
      cf["modern_hand_REGRESSION"]["cue_override_full"]["acc"] >= cf["modern_hand_REGRESSION"]["spacy_raw"]["acc"])

print("[8] register-invariance at the EME extreme (Shakespeare) + POS-layer collapse")
mE = _metrics("role_shakespeare_eme_v1")
th = mE["thou_subject"]
check("EME POS layer collapses (spaCy tags 'thou' PRON < 5%)", th["spacy_pos_tags_PRON"] < 0.05)
check("spaCy subject accuracy COLLAPSES on EME (< 0.20)", th["spacy_raw_subject"] < 0.20)
check("brain-faithful cascade+lexicon RECOVERS EME 'thou'-subject (>= 0.6 vs raw < 0.2)",
      th["cascade_morph"] >= 0.6)
check("case control: cascade does NOT subject-ify accusative 'thee' (>= 0.6 correct)",
      mE["thee_object_control"]["cascade_morph"] >= 0.6)

print(f"\n[witness] {PASS}/26 PASS")
