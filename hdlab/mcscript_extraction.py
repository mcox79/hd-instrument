"""hdlab/mcscript_extraction.py -- MCScript2.0 XML parsing + glass-box parse-
structure role extraction (2026-08-09, real-benchmark validation of the
script-grain self-growing acquisition loop, hdlab/script_grain_acquisition_loop.py).

STAGE 0/1 FINDINGS (see preregs/2026-08-09_mcscript2_real_benchmark_validation_v1.md
for full detail; summarized here since this module's design is a direct
consequence of them):

  Stage 0: MCScript2.0 (Ostermann/Roth/Pinkal 2019, SFB1102 Saarland,
  http://hdl.handle.net/21.11119/0000-000A-3606-3) downloaded from
  https://fedora.clarin-d.uni-saarland.de/sfb1102/MCScript-2.0.zip. train=2500
  instances/195 scenarios/14191 questions, dev=355 instances/162 scenarios/
  2020 questions (all 162 dev scenarios also occur in train), test=632
  instances (present in this download despite the task's "test is private"
  framing -- honored anyway: this module and the cell never read test-data.xml
  for anything but a headline count). Every question has exactly 2 answers,
  exactly 1 correct. question type in {"commonsense" (script-based, where
  grounding should help), "text" (answer literal in the narrative), "positive-
  merged" (a third crowdsourcing category, reported separately, not assumed).

  Stage 1 (extraction feasibility): running the owned dependency-parse front
  end (hdlab.candidate_generator.CandidateGenerator, persisted UPOS-tagger +
  arc-parser checkpoints) sentence-by-sentence over real MCScript narratives
  and pulling (first-sentence ROOT-verb lemma, last-sentence ROOT-verb lemma,
  most-frequent SUBJ filler, most-frequent OBJ filler) via
  hdlab.thematic_role_labeler.frame_slot_role FIRES on 150/150 sampled DEV
  instances (100%) -- does NOT reproduce the DesireDB extraction wall.

  Stage 1b (a DEEPER check the capstone's own mandatory precheck (a) demands):
  does this narrow 4-slot reduction, run through
  hdlab.script_grain_acquisition_loop.build_instance_register (FHRR bind-
  bundle) and compared via real-2D cosine, actually DISCRIMINATE same-scenario
  from different-scenario TRAIN instances? Measured on 72 registers / 12
  sampled scenarios: matched-pair mean cosine 0.1555 vs wrong-pair mean 0.1275
  -- a real but WEAK gap (0.028), heavy distributional overlap (p10(matched)=
  -0.010 < p90(wrong)=0.228). Real crowd-sourced retellings of a scenario are
  far more lexically/structurally diverse than the synthetic capstone's clean
  per-type templates, so compressing a whole narrative to one dominant
  agent/patient vote loses too much.

  Stage 1c (design fix, before committing to Stage 2): does the EXISTING,
  already-validated hdlab.grounding_acquisition_loop.context_vector (bag-of-
  content-words bipolar bundle over the WHOLE narrative, already wired
  elsewhere in this pipeline for the reliability/MDL signal) discriminate
  better? Measured on the SAME 72-instance / 12-scenario sample: matched-pair
  mean cosine 0.1905 vs wrong-pair mean 0.0379 -- a 5.5x larger gap (0.153).

  AMENDMENT (found empirically, disclosed, not hidden -- same discipline the
  capstone's own Amendments 1-3 used): the experiment cell (exp_mcscript2_
  real_benchmark_validation_v1.py) uses context_vector(full_narrative_text) as
  BOTH the CA3/DG keying prototype (correction #3 unchanged -- iterative_
  attractor + calibrated novelty threshold) AND the content/MDL signal
  (correction #2's reliability check + the MDL gate), wrapped as a zero-
  imaginary complex64 tensor so it plugs into hdlab.script_grain_acquisition_
  loop.ScriptLibrary/_real2d UNMODIFIED (cosine on [Re,Im]=[bow,0] reduces
  EXACTLY to cosine on bow -- an exact, lossless embedding, not an
  approximation). The narrow FHRR 4-role register (build_instance_register,
  correction #4) this module extracts is RETAINED for glass-box audit-trail
  reporting only (a handful of example tuples per run) -- per the measured
  discrimination gap it is NOT the scoring/keying signal for Stage 2. This is
  a disclosed downgrade of correction #4's role, not a silent drop: the
  structure/content role-vocabulary FACTORIZATION correction #4 claims
  foundational (TEM; Baldassano/Hasson/Norman 2018) is still exercised and
  reported, just not load-bearing for the accuracy numbers.

REUSE (wire-don't-island): hdlab.candidate_generator.CandidateGenerator /
candidates_from_parse / NOMINAL (persisted front end, unmodified);
hdlab.thematic_role_labeler.lemma_verb / frame_slot_role (unmodified).

GENUINELY-NEW code in this file: parse_mcscript_xml (dataset reader),
split_sentences, extract_root_verb, extract_args, extract_instance_tuple
(the 4-slot reduction itself).

ASCII-only. Deterministic (no RNG in this module at all -- parsing + a
persisted, frozen perceptron/arc-parser checkpoint are both deterministic).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter
from typing import Dict, List, Optional, Tuple

from hdlab.candidate_generator import CandidateGenerator, NOMINAL, CandResult
from hdlab.thematic_role_labeler import lemma_verb, frame_slot_role

_SENT_SPLIT_RE = re.compile(r"\s*\.\s+")

_PRONOUN_AGENTS = frozenset({"i", "we", "he", "she", "they", "it", "you"})


def split_sentences(text: str) -> List[str]:
    """Split MCScript narrative text into sentences. MCScript text is already
    UD-style space-padded around punctuation ("... family , so we started
    ... place . We searched ..."), so splitting on ' . ' (period as its own
    token) is a clean, deterministic sentence boundary -- no abbreviation
    ambiguity in this corpus's simple declarative narrative style."""
    text = (text or "").strip()
    if not text:
        return []
    return [p.strip() for p in _SENT_SPLIT_RE.split(text) if p.strip()]


def extract_root_verb(cr: CandResult) -> Optional[Tuple[int, str]]:
    """Return (1-based token idx, lemma) of the sentence's ROOT verb (heads[v]
    == 0); falls back to the first VERB-tagged token if the arc-parser found
    no root verb (parser-noise robustness, matches parse_goal_extraction's own
    fallback philosophy). Returns None if the sentence has no verb at all."""
    verbs = [i for i in range(1, len(cr.tokens) + 1) if cr.pos[i - 1] == "VERB"]
    if not verbs:
        return None
    roots = [v for v in verbs if cr.heads.get(v) == 0]
    v = roots[0] if roots else verbs[0]
    return v, lemma_verb(cr.tokens[v - 1])


def extract_args(cr: CandResult, v_idx: int, lemma: str) -> Tuple[Optional[str], Optional[str]]:
    """Positional SUBJ/OBJ split (pre-verbal nominal dependent = subject,
    post-verbal = object -- matches parse_goal_extraction's own "voice-
    appropriate positional filtering" convention) + frame_slot_role gate (a
    verb's frame must actually license the slot; STRICTLY_INTRANSITIVE_VERBS-
    class verbs return "none" for obj and are excluded). Ties broken by
    closest-to-the-verb (subj: last pre-verbal candidate; obj: first post-
    verbal candidate)."""
    nominals = [i for i in range(1, len(cr.tokens) + 1) if cr.pos[i - 1] in NOMINAL]
    subj_cands = [a for a in nominals if cr.heads.get(a) == v_idx and a < v_idx]
    obj_cands = [a for a in nominals if cr.heads.get(a) == v_idx and a > v_idx]
    subj_role = frame_slot_role(lemma, "subj")
    obj_role = frame_slot_role(lemma, "obj")
    subj_tok = cr.tokens[subj_cands[-1] - 1].lower() if subj_cands and subj_role != "none" else None
    obj_tok = cr.tokens[obj_cands[0] - 1].lower() if obj_cands and obj_role != "none" else None
    return subj_tok, obj_tok


def extract_instance_tuple(
    text: str, gen: CandidateGenerator
) -> Tuple[Optional[Tuple[str, str, str, str]], Dict]:
    """Per-narrative (trigger, consequent, agent, patient) 4-slot extraction:
    trigger = first sentence's ROOT-verb lemma, consequent = last sentence's
    ROOT-verb lemma, agent = most-frequent SUBJ filler across all sentences,
    patient = most-frequent OBJ filler across all sentences. GLASS-BOX AUDIT
    SIGNAL ONLY in the Stage-2 cell (see module docstring Amendment) -- kept
    for reporting/interpretability, not the scoring mechanism. Returns
    (tuple_or_None, diag_dict); diag always populated for glass-box reporting."""
    sents = split_sentences(text)
    if len(sents) < 2:
        return None, {"reason": "too_few_sentences", "n_sents": len(sents)}
    agent_votes: Counter = Counter()
    patient_votes: Counter = Counter()
    verb_lemmas: List[str] = []
    n_root_found = 0
    for s in sents:
        cr = gen.generate(s)
        rv = extract_root_verb(cr)
        if rv is None:
            continue
        v_idx, lemma = rv
        n_root_found += 1
        verb_lemmas.append(lemma)
        subj_tok, obj_tok = extract_args(cr, v_idx, lemma)
        if subj_tok:
            agent_votes[subj_tok] += 1
        if obj_tok:
            patient_votes[obj_tok] += 1
    diag = {
        "n_sents": len(sents),
        "n_root_found": n_root_found,
        "root_fire_rate": (n_root_found / len(sents)) if sents else 0.0,
    }
    if not verb_lemmas:
        diag["reason"] = "no_root_verbs_found"
        return None, diag
    if not agent_votes or not patient_votes:
        diag["reason"] = "missing_agent_or_patient"
        diag["trigger"] = verb_lemmas[0]
        diag["consequent"] = verb_lemmas[-1]
        return None, diag
    trigger = verb_lemmas[0]
    consequent = verb_lemmas[-1]
    agent = agent_votes.most_common(1)[0][0]
    patient = patient_votes.most_common(1)[0][0]
    diag["agent_votes"] = dict(agent_votes.most_common(3))
    diag["patient_votes"] = dict(patient_votes.most_common(3))
    diag["agent_is_pronoun"] = agent in _PRONOUN_AGENTS
    return (trigger, consequent, agent, patient), diag


def parse_mcscript_xml(path: str) -> List[Dict]:
    """Parse an MCScript2.0 XML file (train-data.xml / dev-data.xml / test-
    data.xml) into a list of instance dicts:
      {id, scenario, text, questions: [{id, text, type,
        answers: [{id, text, correct}]}]}
    Raises (does not silently skip) on any instance missing a text element or
    any question without exactly 2 answers / exactly 1 correct answer --
    schema breaches must be loud, not swallowed."""
    tree = ET.parse(path)
    root = tree.getroot()
    out: List[Dict] = []
    for inst in root.findall("instance"):
        text_el = inst.find("text")
        if text_el is None or text_el.text is None:
            raise ValueError(f"instance id={inst.get('id')!r} in {path} has no <text>")
        questions = []
        qs_el = inst.find("questions")
        if qs_el is not None:
            for q in qs_el.findall("question"):
                answers = []
                for a in q.findall("answer"):
                    answers.append({
                        "id": a.get("id"),
                        "text": a.get("text", ""),
                        "correct": a.get("correct") == "True",
                    })
                if len(answers) != 2:
                    raise ValueError(
                        f"question id={q.get('id')!r} instance={inst.get('id')!r} in {path} "
                        f"has {len(answers)} answers, expected 2")
                if sum(1 for a in answers if a["correct"]) != 1:
                    raise ValueError(
                        f"question id={q.get('id')!r} instance={inst.get('id')!r} in {path} "
                        f"does not have exactly 1 correct answer")
                questions.append({
                    "id": q.get("id"), "text": q.get("text", ""),
                    "type": q.get("type"), "answers": answers,
                })
        out.append({
            "id": inst.get("id"), "scenario": inst.get("scenario"),
            "text": text_el.text, "questions": questions,
        })
    return out


# ---------------------------------------------------------------------------
# Self-test (real code path, per exp_dev SCHEMA-VET F.1)
# ---------------------------------------------------------------------------
def self_test(pos_ckpt: str, arc_ckpt: str) -> Dict:
    """Off-disk gate exercising the REAL code path: loads the real persisted
    CandidateGenerator checkpoints, parses a tiny hand-built XML instance,
    and extracts a real 4-slot tuple from real narrative-shaped text."""
    gen = CandidateGenerator.load(pos_ckpt, arc_ckpt)

    text = (
        "I wanted to make breakfast . I got the eggs out of the fridge . "
        "I cracked the eggs into a bowl . I added some salt and pepper . "
        "I poured the mixture into the hot pan . I flipped the omelette over . "
        "I served the omelette on a plate ."
    )
    tup, diag = extract_instance_tuple(text, gen)
    assert tup is not None, f"self_test extraction must fire on a clean narrative: {diag}"
    trigger, consequent, agent, patient = tup
    assert isinstance(trigger, str) and isinstance(consequent, str)
    assert isinstance(agent, str) and isinstance(patient, str)
    assert diag["root_fire_rate"] > 0.5, f"root_fire_rate too low on clean text: {diag}"

    # parse_mcscript_xml real code path: hand-built minimal XML with the real schema.
    import tempfile, os
    xml_text = (
        "<data><instance id=\"0\" scenario=\"test scenario\"><text>"
        + text +
        "</text><questions><question id=\"0\" text=\"What did they make?\" type=\"commonsense\">"
        "<answer correct=\"True\" id=\"0\" text=\"an omelette\" />"
        "<answer correct=\"False\" id=\"1\" text=\"a sandwich\" /></question>"
        "</questions></instance></data>"
    )
    fd, tmp_path = tempfile.mkstemp(suffix=".xml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(xml_text)
        parsed = parse_mcscript_xml(tmp_path)
    finally:
        os.remove(tmp_path)
    assert len(parsed) == 1, f"expected 1 parsed instance, got {len(parsed)}"
    assert parsed[0]["scenario"] == "test scenario"
    assert len(parsed[0]["questions"]) == 1
    assert len(parsed[0]["questions"][0]["answers"]) == 2

    return {
        "extraction_fires_on_clean_narrative": True,
        "extracted_tuple": tup,
        "diag": diag,
        "xml_parse_ok": True,
        "real_code_path_exercised": ["CandidateGenerator", "parse_mcscript_xml", "extract_instance_tuple"],
    }


if __name__ == "__main__":
    import json
    import os as _os
    _repo = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
    _pos = _os.path.join(_repo, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
    _arc = _os.path.join(_repo, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
    print(json.dumps(self_test(_pos, _arc), indent=2))
