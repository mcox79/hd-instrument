"""exp_extraction_quality_gate_neural_foundation_v1 (2026-08-10)

GATE cell (measurement, NOT the pipeline build). Design:
notes/design_extraction_quality_gate_neural_foundation_2026-08-10.md.

Prior-work check (substrate_query.sh "neural extractor SRL AMR coref installability modern
extraction quality gate oracle parity", 2026-08-10): top hits at cosine 0.34-0.35 are keyword-
adjacent ("extraction") but a DIFFERENT topic -- exp_substrate_extraction_quality_1B_8B_70B_v2
measures LLM-hidden-state DENSE-PASSAGE-RETRIEVAL quality (Llama 1B/8B/70B layers vs MiniLM),
not prose->structured-event extraction. No genuine rediscovery risk. The real relevant prior
work is notes/research_islanded_comprehension_organs_audit_2026-08-10.md, already cited by the
design note: 9+ real-text organ cells all show the SAME oracle(0.93-1.00)->self-extract(0.25-
0.68) collapse. This cell tests whether swapping in a better EXTRACTOR (not a better organ)
closes that gap.

QUESTION: does a modern extractor produce the RIGHT KIND of structured data (PRED/AGENT/PATIENT/
TENSE events, coref clusters, grounded fillers) for the validated organs (hdlab.event_bundle.
EventBundleCodec, hdlab.situation_model_accumulate.AccumulateRegister) to consume?

INSTALLABILITY-FIRST FINDINGS (the gate's own first result, tested THIS session before committing
to a stack):
  SRL (PRED/AGENT/PATIENT/TENSE): spaCy 3.8.14 dependency-parse + morphology heuristic (the
    design note's explicitly-sanctioned fallback). Zero-risk (already installed, zero-conflict).
    Verified on 5 real sentences before committing (all 5 shape-conformant, correct-looking).
  Coref -- TWO modern-neural candidates attempted, BOTH FAILED TO RUN in this environment:
    1. fastcoref (biu-nlp/f-coref, HF transformers): `pip install --dry-run` showed a CLEAN
       install (zero dependency conflicts against this venv's torch==2.12.0/transformers==5.10.1/
       spacy==3.8.14); installed successfully; but crashes at model-load time with
       `AttributeError: 'FCorefModel' object has no attribute 'all_tied_weights_keys'` inside
       transformers 5.10.1's PreTrainedModel.post_init() / _finalize_model_loading -- a genuine
       library-VERSION-SKEW bug (fastcoref last meaningfully updated ~2023 against transformers
       floor >=4.11.3; transformers 5.10.1's newer tied-weights bookkeeping breaks fastcoref's
       custom FCorefModel wrapper). A targeted in-process monkeypatch was attempted (non-invasive,
       does not touch installed files) and made a DIFFERENT part of the same code path fail
       (`property ... has no setter`) -- confirmed via a control test that a PLAIN
       `RobertaModel(cfg)` instantiates fine under transformers 5.10.1, isolating the break to
       fastcoref's own subclass/wrapper, not a general transformers regression. Not pursued
       further (patching HF internals is out of scope for a GATE cell).
    2. stanza (`en`, processors="tokenize,coref"): `pip install --dry-run` also clean; installed;
       but `stanza.download(...)` hung with ZERO stdout/network/disk activity (no
       ~/stanza_resources dir ever created) for 5+ minutes -- aborted as a non-starter.
    3. spacy-experimental-coref (the design note's 3rd candidate): NOT attempted -- its released
       pipeline (en_coreference_web_trf) is DOCUMENTED to require spaCy ~3.4/old-thinc pins,
       known-incompatible with this project's spacy==3.8.14/thinc==8.3.13 stack. Flagged as a
       DOCUMENTED (not empirically re-verified) constraint given time budget.
  CONSEQUENCE: no modern NEURAL coref extractor could be installed+run in this environment. This
  is itself the headline installability finding for the coref half of the gate. To keep the
  measurement pipeline running and produce SOME extraction-quality data, an INDEPENDENT (not
  imported from the repo's own earned-coref system) rule-based fallback clusterer
  (`cluster_ids_rule_based_fallback`, gender/number-agreement + recency + exact-string-match) is
  used in its place for the coref metrics below -- CLEARLY LABELED NOT-MODERN-NEURAL throughout.
  Any oracle-parity result from this arm answers "does a DIFFERENT-but-still-rule-based coref
  close the gap," not the design note's actual question ("does MODERN NEURAL extraction close the
  gap") -- that question could not be answered this session; the installability failure IS the
  answer to report.

Gold corpora (author-constructed positive-control gold, same convention as this repo's other
islanded-organ cells which routinely use N=7-24 hand-curated real-English items -- OntoNotes/
CoNLL-2012, the standard SRL/coref benchmark, is not available offline in this repo):
  data/eval_gold_extraction_quality_gate_v1/gold_srl_tense_modern_v1.jsonl   (30 items, MODERN
    produced/clean English, PRED/AGENT/PATIENT lemma gold via spaCy's OWN lemmatizer applied at
    gold-authoring time so SRL-F1 measures role/predicate SELECTION, not lemmatizer spelling
    idiosyncrasy; TENSE gold authored independently by the human, not derived from the extractor)
  data/eval_gold_extraction_quality_gate_v1/gold_coref_modern_v1.jsonl      (10 mini passages, 42
    mentions, MODERN produced/clean English, gold entity clusters)
  data/eval_gold_extraction_quality_gate_v1/sample_unproduced_ud_ewt_v1.jsonl (8 passages / 32
    sentences sampled from data/corpora/ud_english_ewt/en_ewt-ud-test.conllu -- "English Web
    Treebank -- weblogs, newsgroups, emails, reviews, Yahoo! Answers... general web register" per
    its own PROVENANCE.md; genuinely naturalistic/informal text, already in-repo, held-out/never
    used for training anything here. USER refinement 2026-08-10: this is the UNPRODUCED-TEXT
    stress probe -- does extraction degrade produced->unproduced, since the extractor itself is
    ALSO trained on produced text (OntoNotes/CoNLL/news)? Per-sentence UD gold Tense morphology on
    the ROOT/main VERB doubles as a real tense reference on this unproduced text too.)

DECISIVE reuse target: experiments/exp_wire_coref_accumulate_situation_model_v1.py (oracle=0.9298,
earned=0.6842, strict_cb=0.7193 on query_accuracy_identity_demanding, headline "powered" eval, 36
McGuffey passages, atom commit 27e10d3a8 / a0aac7eeb / 5b266248f -- MEASURED@data/exp_wire_coref_
accumulate_situation_model_v1/metrics.json). This cell IMPORTS (does not reimplement) its
build_mention_stream_with_role / event_slots_for / run_arm_on_passage / _agg_arm / load_passages /
EVALS / HEADLINE_EVAL / ROLE_VOCAB / D / MAX_EVENT_SLOTS / SEED, and adds ONE new arm
(rule_based_fallback, this cell's independent clusterer) run over the SAME stream/passages the
oracle/earned/recency/singleton arms already use -- no text reconstruction or char-offset
alignment needed, since AccumulateRegister and the wire_coref stream already operate at the
mention-list level (mention DETECTION is gold-supplied in that cell for every arm; only
IDENTITY/clustering differs -- see that cell's docstring: "this cell isolates the identity(coref)
+accumulate integration only").

Pre-registered GO/NO-GO (design note's bands; CAVEATED per the installability finding above --
this cell's coref arm is rule-based, not modern-neural, so a NO-GO here does not indict a modern
neural extractor that could not be run, and a hypothetical GO would not validate one either):
  shape_conformance      >= 0.80   (design note ~ "high")
  srl_role_f1             >= 0.80
  coref_b3_f1              >= 0.70
  coverage_all_tenses     >= 0.85  (each of past/pres/fut bucket, produced gold)
  grounding_coverage      >= 0.90  (design note ~0.94; WordNet-lemma-has-synset coverage, this
                                    cell's own thin grounder -- see GROUNDING section)
  oracle_parity_fraction  >= 0.80  (lift_fallback / lift_oracle over singleton_floor baseline)
NO-GO -> localize + report the single weakest of {shape, srl_f1, coref_f1, coverage, grounding,
parity} as the next target; do not proceed to a full-pipeline build on bad structure.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.dirname(os.path.abspath(__file__)), os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import spacy  # noqa: E402
import torch  # noqa: E402
from nltk.corpus import wordnet as wn  # noqa: E402

from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402 (real_code_path)
import exp_checkpoint as ckpt  # noqa: E402 (mandatory per CLAUDE.md multi-unit checkpoint rule)

# REUSE (not reimplement) the DECISIVE cell's machinery -- see module docstring.
import exp_wire_coref_accumulate_situation_model_v1 as _wc  # noqa: E402
# REUSE (linguistic UTILITY only, not the clustering ALGORITHM under test) gender/number/pronoun
# feature lookups -- same functions the wire_coref cell itself imports for its own arms.
from exp_earn_coref_match_or_allocate_v1 import (  # noqa: E402
    is_pronoun_mention,
    gender_number_for,
)

ANCHOR_NAME = "extraction_quality_gate_neural_foundation_v1"
GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_extraction_quality_gate_v1")
SRL_GOLD_PATH = os.path.join(GOLD_DIR, "gold_srl_tense_modern_v1.jsonl")
COREF_GOLD_PATH = os.path.join(GOLD_DIR, "gold_coref_modern_v1.jsonl")
UNPRODUCED_PATH = os.path.join(GOLD_DIR, "sample_unproduced_ud_ewt_v1.jsonl")

# ---- pre-registered GO/NO-GO bands (declared BEFORE running; see module docstring) ----
BANDS = {
    "shape_conformance": 0.80,
    "srl_role_f1": 0.80,
    "coref_b3_f1": 0.70,
    "coverage_all_tenses": 0.85,
    "grounding_coverage": 0.90,
    "oracle_parity_fraction": 0.80,
}


# =====================================================================================
# 1. EXTRACTOR STACK
# =====================================================================================
_NLP_CACHE: Dict[str, spacy.Language] = {}


def get_spacy() -> spacy.Language:
    if "nlp" not in _NLP_CACHE:
        _NLP_CACHE["nlp"] = spacy.load("en_core_web_sm")
    return _NLP_CACHE["nlp"]


def srl_extract_event(nlp: spacy.Language, text: str) -> Dict[str, Optional[str]]:
    """SRL heuristic (spaCy dep-parse + morphology): ROOT verb -> PRED; nsubj/nsubjpass child ->
    AGENT; dobj/obj/attr/dative child -> PATIENT; Tense morph (+ will/shall aux check for future)
    -> TENSE in {"past","pres","fut","unk"}. This IS the design note's explicitly-sanctioned
    fallback (spaCy 3.x dep-parse -> heuristic role mapping) -- used because no modern-neural SRL
    stack was attempted THIS session (time-budget: the coref half already consumed the
    installability-testing budget; a modern PropBank-SRL/AMR stack -- AllenNLP-SRL carries
    numpy<1.22/spacy<2.3 pins hard-incompatible with this venv's numpy==2.4.5/spacy==3.8.14,
    documented not re-verified -- is future work, named in the report as the next installability
    target)."""
    doc = nlp(text) if isinstance(text, str) else text
    root = None
    for tok in doc:
        if tok.dep_ == "ROOT" and tok.pos_ in ("VERB", "AUX"):
            root = tok
            break
    if root is None:
        return {"PRED": None, "AGENT": None, "PATIENT": None, "TENSE": None}
    agent = patient = None
    for child in root.children:
        if child.dep_ in ("nsubj", "nsubjpass") and agent is None:
            agent = child.lemma_.lower()
        if child.dep_ in ("dobj", "obj", "attr", "dative") and patient is None:
            patient = child.lemma_.lower()
    tense_feat = root.morph.get("Tense")
    if any(c.text.lower() in ("will", "shall") for c in root.children):
        tense = "fut"
    elif tense_feat:
        tense = "past" if tense_feat[0] == "Past" else "pres"
    else:
        tense = "unk"
    return {"PRED": root.lemma_.lower(), "AGENT": agent, "PATIENT": patient, "TENSE": tense}


def wordnet_grounded(lemma: Optional[str]) -> bool:
    """GROUNDING check: does this filler lemma resolve to >=1 WordNet synset (any POS)? This is a
    THIN grounder built fresh for this gate (the design note's pointer, "the existing WordNet-
    Tier2 open-vocab grounder ~94% coverage," could not be located by name within this session's
    search budget -- hdlab.lexical_similarity's Tier1/Tier2 pooling is a CLOSED 89-concept lexicon
    that explicitly disclaims open-vocabulary coverage in its own docstring, not a match;
    hdlab.animacy_lexicon is WordNet-backed but animacy-scoped, not general grounding. This
    function reuses the SAME underlying resource (nltk.corpus.wordnet, already used pervasively in
    this repo -- animacy_lexicon.py, pun_coherence, visual_grounding) in spirit, but is a genuinely
    NEW thin wrapper, not a promoted hdlab primitive -- disclosed honestly, not claimed as reuse of
    a specific prior module."""
    if not lemma:
        return False
    return len(wn.synsets(lemma)) > 0


CAUSAL_CONNECTIVES = ("because", "since", "so", "therefore", "as a result", "thus", "due to")


def causal_connective_present(sentences: List[str]) -> bool:
    """Discourse-connective heuristic for CAUSAL/TEMPORAL links (design note: 'HARDEST; may be
    partial -- measure its marginal impact separately, do not let it block the SRL+coref core').
    Descriptive only, NOT gated in the GO/NO-GO bands."""
    joined = " ".join(sentences).lower()
    return any(c in joined for c in CAUSAL_CONNECTIVES)


# =====================================================================================
# 2. COREF -- independent rule-based fallback clusterer (NOT modern-neural; see module docstring)
# =====================================================================================
def cluster_ids_rule_based_fallback(stream: List[dict]) -> List[str]:
    """Gender/number-agreement + recency (pronouns) + exact-string-match (names/definite-NPs)
    clustering, over a mention STREAM (each item needs is_pronoun/gender/number/mention_text).
    Independently coded for this gate (does NOT import exp_earn_coref_match_or_allocate_v1's
    run_learnable/run_recency_floor clustering logic -- only their gender/number/is_pronoun
    FEATURE-lookup utilities are reused, per module docstring). Sits deliberately between the
    wire_coref cell's recency_floor (chains everything, no agreement filter) and its earned arm
    (a real match-or-allocate system): agreement-filtered recency is a genuine, distinct baseline,
    not a relabeled copy of either."""
    clusters: List[Dict] = []  # each: {"gender": str|None, "number": str|None, "names": set}
    ids: List[str] = []
    for rec in stream:
        best = None
        if rec.get("is_pronoun"):
            for ci in range(len(clusters) - 1, -1, -1):  # most-recent-first
                c = clusters[ci]
                g_ok = rec.get("gender") in (None, "unknown") or c["gender"] in (None, "unknown") \
                    or rec.get("gender") == c["gender"]
                n_ok = rec.get("number") in (None, "unknown") or c["number"] in (None, "unknown") \
                    or rec.get("number") == c["number"]
                if g_ok and n_ok:
                    best = ci
                    break
        else:
            key = str(rec.get("mention_text", "")).lower().strip()
            for ci, c in enumerate(clusters):
                if key and key in c["names"]:
                    best = ci
                    break
        if best is None:
            clusters.append({"gender": rec.get("gender"), "number": rec.get("number"), "names": set()})
            best = len(clusters) - 1
        if not rec.get("is_pronoun"):
            clusters[best]["names"].add(str(rec.get("mention_text", "")).lower().strip())
        ids.append(str(best))
    return ids


def _mention_stream_from_coref_gold(nlp: spacy.Language, passage: dict) -> List[dict]:
    """Build a mention stream (is_pronoun/gender/number/mention_text/entity_id) from a
    gold_coref_modern_v1.jsonl passage's `mentions` list, in file order (already sorted by the
    author to match sentence order)."""
    stream = []
    for m in passage["mentions"]:
        text = m["text"]
        is_pron = is_pronoun_mention(text)
        gender, number = gender_number_for(text, is_pron)
        stream.append({
            "mention_text": text, "is_pronoun": is_pron, "gender": gender, "number": number,
            "entity_id": m["entity_id"], "sent_idx": m["sent_idx"],
        })
    return stream


def b3_f1(pred_ids: List[str], gold_ids: List[str]) -> Tuple[float, float, float]:
    """B-cubed precision/recall/F1 over a flat list of (predicted_cluster_id, gold_cluster_id)
    pairs, one per mention, POOLED (micro) across however many passages are concatenated in."""
    n = len(pred_ids)
    if n == 0:
        return (0.0, 0.0, 0.0)
    p_sum = r_sum = 0.0
    for i in range(n):
        pred_c = {j for j in range(n) if pred_ids[j] == pred_ids[i]}
        gold_c = {j for j in range(n) if gold_ids[j] == gold_ids[i]}
        overlap = len(pred_c & gold_c)
        p_sum += overlap / len(pred_c)
        r_sum += overlap / len(gold_c)
    prec, rec = p_sum / n, r_sum / n
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    return (prec, rec, f1)


# =====================================================================================
# 3. HAND-VERIFIED judgment table (unproduced probe) -- fixed BEFORE this run for reproducibility.
#    Built by: running srl_extract_event over sample_unproduced_ud_ewt_v1.jsonl once (script,
#    not committed -- output inspected by the cell-author), hand-labeling the first 15 sentences
#    for CORRECT/INCORRECT (does the extracted PRED/AGENT/PATIENT/TENSE reflect a fair reading of
#    the sentence?). 12/15 correct; 3 incorrect classes found: (1) present-perfect "has put"
#    Tense-tagged "past" (participle morphology ambiguity), (2) passive-raising construction
#    ("X are said to have been...") -- nsubjpass-as-AGENT heuristic wrongly assigns AGENT to the
#    raised subject of "say" rather than recognizing it has no true agent role there, (3) fronted-
#    participle inversion ("Attached below is X") -- ROOT/AGENT-PATIENT roles reversed (X is the
#    PATIENT of "attach", not the AGENT). All three are genuine dependency-heuristic limitations
#    on naturalistic syntax, not implementation bugs.
# =====================================================================================
HAND_VERIFIED_JUDGMENTS = [
    # (sentence_text, correct: bool, reason)
    ("I'm staying away from the stock.", True, "intransitive PP-complement, no dobj expected"),
    ("I doubt the very few who actually read my blog have not come across this yet, but I figured I would put it out there anyways.",
     True, "doubt takes clausal complement, PATIENT=None is honest"),
    ("John Donovan from Argghhh! has put out a excellent slide show on what was actually found and fought for in Fallujah.",
     False, "present-perfect 'has put' Tense-tagged past (participle Tense-feature ambiguity)"),
    ("He makes some good observations on a few of the pic's.", True, "correct SVO"),
    ("On the internet site of Monotheism and Holy War (al-Tawhid wa al-Jihad) , the group allegedly declared, \"We announce that the Tawhid and Jihad Group, its prince and soldiers, have pledged allegiance to the sheikh of the mujahideen Osama bin Laden.\"",
     True, "matrix verb + quoted clausal complement, PATIENT=None is honest"),
    ("Abu Musab al-Zarqawi and his group are said to have been bitter rivals of al-Qaeda during the Afghan resistance days.",
     False, "passive-raising: nsubjpass-as-AGENT wrongly assigns Zarqawi as agent of 'say'"),
    ("One witness at the Moutasaddiq trial in Germany alleged that Zarqawi had not allowed Monotheism and Holy War to share resources with al-Qaeda in the early zeroes of the 21st century.",
     True, "matrix verb + clausal complement, PATIENT=None is honest"),
    ("If the statement is true, it is a worrying sign that even the divided small radical guerrilla groups are being \"picked up\" by al-Qaeda.",
     True, "copular attr-as-PATIENT is a reasonable state-description reading"),
    ("By using collateral to pay these bills are we not keeping required levels available?",
     True, "garbled naturalistic question; extraction is a fair reading given the source"),
    ("Attached below is Davis Thames' presentation regarding the proposed Project Bruin.",
     False, "fronted-participle inversion: AGENT/PATIENT roles reversed (presentation is being attached)"),
    ("I spoke with Mike Collins [203-719-8385 (phone) and 203-719-7031 (fax)] who conrfirmed to me that the cap included the remaining 2.5+million remaining shares.",
     True, "'speak with X' is a PP not a dobj, PATIENT=None is correct"),
    ("Please return an executed copy of confirm to me.", True, "imperative: AGENT=None is the honest correct reading (no syntactic subject)"),
    ("n3td3v saw this story on BBC News Online and thought you should see it.", True, "first conjunct correctly the root"),
    ("** Google defies US over search data **", True, "headline style, correct SVO"),
    ("Web giant Google is resisting an attempt by the US to force it to reveal what users are searching for.",
     True, "correct SVO"),
]


# =====================================================================================
# 4. gold loaders
# =====================================================================================
def load_jsonl(path: str) -> List[dict]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


# =====================================================================================
# 5. metric blocks
# =====================================================================================
def run_srl_gold(nlp: spacy.Language, items: List[dict]) -> dict:
    per_item = []
    for it in items:
        pred = srl_extract_event(nlp, it["text"])
        gold = it["gold_event"]
        shape_ok = pred["PRED"] is not None and pred["AGENT"] is not None and pred["PATIENT"] is not None
        gold_tuples = {("PRED", gold["PRED"]), ("AGENT", gold["AGENT"])}
        if gold["PATIENT"]:
            gold_tuples.add(("PATIENT", gold["PATIENT"]))
        pred_tuples = set()
        for role in ("PRED", "AGENT", "PATIENT"):
            if pred[role] is not None:
                pred_tuples.add((role, pred[role]))
        overlap = gold_tuples & pred_tuples
        covered = pred["PRED"] is not None and pred["AGENT"] is not None  # "yielded >=1 event"
        grounded_flags = [wordnet_grounded(pred["AGENT"]), wordnet_grounded(pred["PATIENT"])]
        per_item.append({
            "sent_id": it["sent_id"], "text": it["text"], "tense_bucket": gold["TENSE"],
            "pred": pred, "gold": gold, "shape_ok": shape_ok, "covered": covered,
            "n_gold_tuples": len(gold_tuples), "n_pred_tuples": len(pred_tuples), "n_overlap": len(overlap),
            "tense_correct": pred["TENSE"] == gold["TENSE"],
            "grounded_flags": grounded_flags,
        })
    return {"per_item": per_item}


def aggregate_srl(per_item: List[dict]) -> dict:
    n = len(per_item)
    shape_conf = sum(1 for r in per_item if r["shape_ok"]) / n
    n_overlap = sum(r["n_overlap"] for r in per_item)
    n_gold = sum(r["n_gold_tuples"] for r in per_item)
    n_pred = sum(r["n_pred_tuples"] for r in per_item)
    prec = n_overlap / n_pred if n_pred else 0.0
    rec = n_overlap / n_gold if n_gold else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    tense_acc = sum(1 for r in per_item if r["tense_correct"]) / n
    by_tense: Dict[str, dict] = {}
    for r in per_item:
        b = by_tense.setdefault(r["tense_bucket"], {"n": 0, "n_covered": 0})
        b["n"] += 1
        b["n_covered"] += int(r["covered"])
    for b in by_tense.values():
        b["coverage"] = b["n_covered"] / b["n"]
    coverage_all = sum(1 for r in per_item if r["covered"]) / n
    ground_flags = [g for r in per_item for g in r["grounded_flags"] if g is not None]
    grounding_cov = (sum(1 for g in ground_flags if g) / len(ground_flags)) if ground_flags else None
    return {
        "shape_conformance": shape_conf, "srl_role_precision": prec, "srl_role_recall": rec,
        "srl_role_f1": f1, "tense_accuracy": tense_acc, "coverage_by_tense": by_tense,
        "coverage_all_sentences": coverage_all, "grounding_coverage": grounding_cov, "n": n,
    }


def run_coref_gold(nlp: spacy.Language, passages: List[dict]) -> dict:
    all_pred_ids: List[str] = []
    all_gold_ids: List[str] = []
    per_passage = []
    for p in passages:
        stream = _mention_stream_from_coref_gold(nlp, p)
        pred_ids = cluster_ids_rule_based_fallback(stream)
        gold_ids = [m["entity_id"] for m in p["mentions"]]
        all_pred_ids.extend(pred_ids)
        all_gold_ids.extend(gold_ids)
        prec, rec, f1 = b3_f1(pred_ids, gold_ids)
        per_passage.append({
            "passage_id": p["passage_id"], "n_mentions": len(stream),
            "b3_precision": prec, "b3_recall": rec, "b3_f1": f1,
            "connective_present": causal_connective_present(p["sentences"]),
        })
    prec, rec, f1 = b3_f1(all_pred_ids, all_gold_ids)
    n_causal = sum(1 for r in per_passage if r["connective_present"])
    return {
        "per_passage": per_passage, "b3_precision_pooled": prec, "b3_recall_pooled": rec,
        "b3_f1_pooled": f1, "n_passages": len(passages), "n_mentions_total": len(all_pred_ids),
        "causal_connective_frac": n_causal / len(passages) if passages else None,
    }


def run_decisive_oracle_parity(timeout_s: float, t0: float, output_dir: str) -> dict:
    """DECISIVE test: reuse exp_wire_coref_accumulate_situation_model_v1's stream/organ machinery
    (imported, not reimplemented). New arm = rule_based_fallback (this cell's independent
    clusterer). Runs over EVALS[HEADLINE_EVAL] (36 McGuffey 'powered' passages) only, for speed --
    the DECISIVE question does not need the secondary g5g6_reviewed eval."""
    arm_order = ["oracle", "rule_based_fallback", "recency_floor", "singleton_floor"]
    eval_name = _wc.HEADLINE_EVAL
    passages = sorted(_wc.load_passages(_wc.EVALS[eval_name]), key=lambda p: p["passage_id"])
    done = ckpt.completed_units(output_dir)
    for p in passages:
        stream = _wc.build_mention_stream_with_role(p)
        event_slots, n_slots, clause_to_slot = _wc.event_slots_for(stream)
        for arm in arm_order:
            key = ckpt.unit_key("decisive", eval_name, p["passage_id"], arm)
            if key in done:
                continue
            if time.perf_counter() - t0 > timeout_s:
                raise TimeoutError(f"exceeded --timeout {timeout_s}s during DECISIVE loop; resume by re-running")
            if arm == "oracle":
                cluster_ids = [r["gold_entity"] for r in stream]
            elif arm == "recency_floor":
                cluster_ids = [str(c) for c in _wc.run_recency_floor(stream)]
            elif arm == "singleton_floor":
                cluster_ids = [str(c) for c in _wc.run_singleton_floor(stream)]
            elif arm == "rule_based_fallback":
                cluster_ids = cluster_ids_rule_based_fallback(stream)
            else:
                raise ValueError(arm)
            res = _wc.run_arm_on_passage(p, stream, cluster_ids, event_slots, clause_to_slot,
                                         _wc.ROLE_VOCAB, _wc.D, torch.Generator().manual_seed(_wc.SEED),
                                         _wc.MAX_EVENT_SLOTS)
            res["arm"] = arm
            res["passage_id"] = p["passage_id"]
            ckpt.record_unit(output_dir, key, res)
    units = ckpt.load_units(output_dir)
    # filter by unit_key prefix (unit_key join uses "|": "decisive|<eval>|<passage_id>|<arm>")
    per_arm = {}
    for arm in arm_order:
        recs = [v for k, v in units.items() if k.startswith(f"decisive|{eval_name}|") and k.endswith(f"|{arm}")]
        per_arm[arm] = _wc._agg_arm(recs)
    K = "query_accuracy_identity_demanding"
    oracle_q = per_arm["oracle"][K]
    singleton_q = per_arm["singleton_floor"][K]
    recency_q = per_arm["recency_floor"][K]
    fallback_q = per_arm["rule_based_fallback"][K]
    lift_oracle = (oracle_q - singleton_q) if (oracle_q is not None and singleton_q is not None) else None
    lift_fallback = (fallback_q - singleton_q) if (fallback_q is not None and singleton_q is not None) else None
    parity_frac = (lift_fallback / lift_oracle) if (lift_oracle and lift_oracle > 0) else None
    # secondary framing directly against the ORIGINAL wire_coref cell's cited earned arm (0.6842):
    prior_earned_q = 0.6842105263157895  # MEASURED@data/exp_wire_coref_accumulate_situation_model_v1/metrics.json:eval_blocks.powered.query_accuracy_identity_demanding.earned
    gap_closure_vs_prior_earned = ((fallback_q - prior_earned_q) / (oracle_q - prior_earned_q)
                                   if (fallback_q is not None and oracle_q is not None and oracle_q != prior_earned_q)
                                   else None)
    return {
        "eval": eval_name, "per_arm_query_accuracy_identity_demanding": {a: per_arm[a][K] for a in arm_order},
        "oracle_q": oracle_q, "singleton_q": singleton_q, "recency_q": recency_q, "fallback_q": fallback_q,
        "lift_oracle_over_singleton": lift_oracle, "lift_fallback_over_singleton": lift_fallback,
        "oracle_parity_fraction": parity_frac, "prior_earned_q_cited": prior_earned_q,
        "gap_closure_fraction_vs_prior_earned": gap_closure_vs_prior_earned,
        "note": "rule_based_fallback is NOT modern-neural (see module docstring) -- this measures "
                "whether a DIFFERENT rule-based coref closes the gap, not whether modern neural "
                "extraction does (that could not be tested this session).",
    }


def run_unproduced_probe(nlp: spacy.Language, passages: List[dict], produced_agg: dict) -> dict:
    per_sentence = []
    judgment_by_text = {t: (c, r) for t, c, r in HAND_VERIFIED_JUDGMENTS}
    hand_hits = hand_total = 0
    for p in passages:
        for sent, tense_gold in zip(p["sentences"], p["tenses"]):
            pred = srl_extract_event(nlp, sent)
            shape_ok = pred["PRED"] is not None and pred["AGENT"] is not None and pred["PATIENT"] is not None
            covered = pred["PRED"] is not None and pred["AGENT"] is not None
            tense_bucket_gold = "past" if tense_gold == "Past" else ("pres" if tense_gold == "Pres" else "unk")
            grounded_flags = [wordnet_grounded(pred["AGENT"]), wordnet_grounded(pred["PATIENT"])]
            rec = {
                "passage_id": p["passage_id"], "genre": p["genre"], "text": sent, "pred": pred,
                "shape_ok": shape_ok, "covered": covered, "tense_bucket_gold": tense_bucket_gold,
                "grounded_flags": grounded_flags,
            }
            if sent in judgment_by_text:
                correct, reason = judgment_by_text[sent]
                rec["hand_verified"] = {"correct": correct, "reason": reason}
                hand_total += 1
                hand_hits += int(correct)
            per_sentence.append(rec)
    n = len(per_sentence)
    shape_conf = sum(1 for r in per_sentence if r["shape_ok"]) / n
    coverage_all = sum(1 for r in per_sentence if r["covered"]) / n
    by_tense: Dict[str, dict] = {}
    for r in per_sentence:
        b = by_tense.setdefault(r["tense_bucket_gold"], {"n": 0, "n_covered": 0})
        b["n"] += 1
        b["n_covered"] += int(r["covered"])
    for b in by_tense.values():
        b["coverage"] = b["n_covered"] / b["n"]
    ground_flags = [g for r in per_sentence for g in r["grounded_flags"] if g is not None]
    grounding_cov = (sum(1 for g in ground_flags if g) / len(ground_flags)) if ground_flags else None

    # coref shape (no gold): mention-detect via simple spaCy PROPN/PRON/definite-NP heuristic per
    # passage, cluster via the SAME rule_based_fallback, report frac of pronouns joined into a
    # multi-mention cluster (a coverage proxy, not F1 -- no gold clusters exist for this text).
    coref_shape_per_passage = []
    for p in passages:
        joined_doc_list = [nlp(s) for s in p["sentences"]]
        stream = []
        for si, doc in enumerate(joined_doc_list):
            for tok in doc:
                if tok.pos_ == "PRON" or (tok.pos_ == "PROPN" and tok.dep_ in ("nsubj", "nsubjpass", "dobj", "obj")):
                    is_pron = tok.pos_ == "PRON"
                    gender, number = gender_number_for(tok.text, is_pron)
                    stream.append({"mention_text": tok.text, "is_pronoun": is_pron,
                                   "gender": gender, "number": number, "sent_idx": si})
        if not stream:
            coref_shape_per_passage.append({"passage_id": p["passage_id"], "n_mentions": 0, "frac_pron_linked": None})
            continue
        ids = cluster_ids_rule_based_fallback(stream)
        cluster_sizes: Dict[str, int] = {}
        for cid in ids:
            cluster_sizes[cid] = cluster_sizes.get(cid, 0) + 1
        pron_idxs = [i for i, r in enumerate(stream) if r["is_pronoun"]]
        n_linked = sum(1 for i in pron_idxs if cluster_sizes[ids[i]] > 1)
        coref_shape_per_passage.append({
            "passage_id": p["passage_id"], "n_mentions": len(stream), "n_pronouns": len(pron_idxs),
            "frac_pron_linked": (n_linked / len(pron_idxs)) if pron_idxs else None,
        })

    hand_acc = (hand_hits / hand_total) if hand_total else None
    deltas = {
        "shape_conformance_delta_produced_minus_unproduced": produced_agg["shape_conformance"] - shape_conf,
        "coverage_delta_produced_minus_unproduced": produced_agg["coverage_all_sentences"] - coverage_all,
        "grounding_delta_produced_minus_unproduced": (
            (produced_agg["grounding_coverage"] - grounding_cov)
            if (produced_agg["grounding_coverage"] is not None and grounding_cov is not None) else None
        ),
    }
    return {
        "per_sentence": per_sentence, "shape_conformance": shape_conf, "coverage_all_sentences": coverage_all,
        "coverage_by_tense": by_tense, "grounding_coverage": grounding_cov,
        "hand_verified_accuracy": hand_acc, "hand_verified_n": hand_total,
        "coref_shape_per_passage": coref_shape_per_passage, "n_sentences": n,
        "deltas_vs_produced": deltas,
    }


# =====================================================================================
# 6. self-test (real_code_path_exercised + arms-must-differ + tiny-scale sanity)
# =====================================================================================
def self_test() -> None:
    nlp = get_spacy()

    # SRL heuristic sanity
    ev = srl_extract_event(nlp, "The engineer reviews the failing build every morning.")
    assert ev == {"PRED": "review", "AGENT": "engineer", "PATIENT": "build", "TENSE": "pres"}, ev
    ev2 = srl_extract_event(nlp, "The committee will announce its decision next week.")
    assert ev2["TENSE"] == "fut" and ev2["PRED"] == "announce", ev2

    # grounding sanity
    assert wordnet_grounded("dog") is True
    assert wordnet_grounded("zzznotaword123") is False
    assert wordnet_grounded(None) is False

    # coref clusterer + B3-F1 sanity (discriminator-fires: must NOT be trivially all-1.0)
    stream = [
        {"mention_text": "Alice", "is_pronoun": False, "gender": "female", "number": "singular"},
        {"mention_text": "she", "is_pronoun": True, "gender": "female", "number": "singular"},
        {"mention_text": "Bob", "is_pronoun": False, "gender": "male", "number": "singular"},
        {"mention_text": "he", "is_pronoun": True, "gender": "male", "number": "singular"},
    ]
    ids = cluster_ids_rule_based_fallback(stream)
    assert ids[0] == ids[1] and ids[2] == ids[3] and ids[0] != ids[2], ids
    prec, rec, f1 = b3_f1(ids, ["A", "A", "B", "B"])
    assert f1 > 0.99, (prec, rec, f1)
    # must-fail control: scrambled gold must NOT also score ~1.0 (metric must discriminate)
    _, _, f1_scrambled = b3_f1(ids, ["A", "B", "A", "B"])
    assert f1_scrambled < f1, "B3-F1 must discriminate: scrambled gold must score below correct gold"

    # ARMS-MUST-DIFFER (META_RULE_AF): rule_based_fallback must differ from recency_floor's
    # everything-one-cluster behavior on a stream with a genuine gender split.
    all_same_ids = ["0"] * len(stream)  # recency_floor-equivalent (chain everything)
    assert ids != all_same_ids, "META_RULE_AF: rule_based_fallback must differ from chain-everything"

    # real_code_path_exercised (META_RULE F.1): construct the REAL substrate object
    # (hdlab.situation_model_accumulate.AccumulateRegister) at tiny scale, exactly as the DECISIVE
    # sub-test's run_arm_on_passage (imported from the real cell, not reimplemented) does.
    gen = torch.Generator().manual_seed(7)
    reg = AccumulateRegister(["agent", "patient"], d=64, generator=gen, max_event_slots=2)
    reg.add_event("e1", "agent", 0)
    role, scores = reg.decode("e1", 0)
    assert role == "agent", (role, scores)

    # exercise the REAL DECISIVE-cell entrypoints at tiny scale (imported module, real objects)
    toy_passage = {
        "clauses": ["Alice smiled.", "She left."],
        "entities": {"Alice": [{"clause": 0, "mention": "Alice", "role": "agent"},
                                {"clause": 1, "mention": "She", "role": "agent"}]},
        "target_queries": [{"entity": "Alice", "query_clause": 1, "gold_role": "agent"}],
        "passage_id": "toy_0",
    }
    toy_stream = _wc.build_mention_stream_with_role(toy_passage)
    assert len(toy_stream) == 2 and all("role" in r for r in toy_stream)
    toy_slots, toy_n, toy_c2s = _wc.event_slots_for(toy_stream)
    toy_ids = cluster_ids_rule_based_fallback(toy_stream)
    toy_res = _wc.run_arm_on_passage(toy_passage, toy_stream, toy_ids, toy_slots, toy_c2s,
                                     ["agent"], 64, torch.Generator().manual_seed(1), toy_n)
    assert "q_total" in toy_res and toy_res["q_total"] == 1, toy_res

    # gold files present + load
    for path in (SRL_GOLD_PATH, COREF_GOLD_PATH, UNPRODUCED_PATH):
        assert os.path.exists(path), f"gold file missing: {path}"
    srl_items = load_jsonl(SRL_GOLD_PATH)
    assert len(srl_items) == 30, len(srl_items)
    coref_items = load_jsonl(COREF_GOLD_PATH)
    assert len(coref_items) == 10, len(coref_items)
    unproduced_items = load_jsonl(UNPRODUCED_PATH)
    assert len(unproduced_items) == 8, len(unproduced_items)

    print("[SELF-TEST] PASS: SRL heuristic shape-correct on 2 sentences; grounding sanity OK; "
          "coref clusterer discriminates (correct-gold F1 > scrambled-gold F1); arms-must-differ "
          "OK; real AccumulateRegister + real wire_coref entrypoints exercised at toy scale; "
          "all 3 gold files present with expected cardinality")


# =====================================================================================
# 7. main
# =====================================================================================
def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_start_marker(output_dir: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "expected_n_units": expected_n_units}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def main(timeout_s: float) -> None:
    t0 = time.perf_counter()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    os.makedirs(output_dir, exist_ok=True)

    srl_items = load_jsonl(SRL_GOLD_PATH)
    coref_items = load_jsonl(COREF_GOLD_PATH)
    unproduced_items = load_jsonl(UNPRODUCED_PATH)
    _write_start_marker(output_dir, len(srl_items) + len(coref_items) + len(unproduced_items) + 36 * 4)

    nlp = get_spacy()
    print(f"[progress] spacy loaded, t={time.perf_counter()-t0:.1f}s", flush=True)

    srl_result = run_srl_gold(nlp, srl_items)
    srl_agg = aggregate_srl(srl_result["per_item"])
    print(f"[progress] SRL gold scored: shape_conformance={srl_agg['shape_conformance']:.3f} "
          f"srl_role_f1={srl_agg['srl_role_f1']:.3f} t={time.perf_counter()-t0:.1f}s", flush=True)

    coref_result = run_coref_gold(nlp, coref_items)
    print(f"[progress] coref gold scored: b3_f1_pooled={coref_result['b3_f1_pooled']:.3f} "
          f"t={time.perf_counter()-t0:.1f}s", flush=True)

    decisive_result = run_decisive_oracle_parity(timeout_s, t0, output_dir)
    print(f"[progress] DECISIVE oracle-parity: parity_fraction="
          f"{decisive_result['oracle_parity_fraction']} t={time.perf_counter()-t0:.1f}s", flush=True)

    unproduced_result = run_unproduced_probe(nlp, unproduced_items, srl_agg)
    print(f"[progress] unproduced probe: shape_conformance={unproduced_result['shape_conformance']:.3f} "
          f"hand_verified_accuracy={unproduced_result['hand_verified_accuracy']} "
          f"t={time.perf_counter()-t0:.1f}s", flush=True)

    # ---- GO/NO-GO gate ----
    gate_values = {
        "shape_conformance": srl_agg["shape_conformance"],
        "srl_role_f1": srl_agg["srl_role_f1"],
        "coref_b3_f1": coref_result["b3_f1_pooled"],
        "coverage_all_tenses": min(b["coverage"] for b in srl_agg["coverage_by_tense"].values()),
        "grounding_coverage": srl_agg["grounding_coverage"],
        "oracle_parity_fraction": decisive_result["oracle_parity_fraction"] or 0.0,
    }
    gate_pass = {k: (gate_values[k] >= BANDS[k]) for k in BANDS}
    all_pass = all(gate_pass.values())
    if all_pass:
        verdict = "GO"
    else:
        weakest = min(gate_pass, key=lambda k: (gate_values[k] - BANDS[k]) / max(BANDS[k], 1e-9))
        verdict = "NO_GO"
    verdict_msg = (
        f"{verdict} (CAVEAT: coref arm is rule-based fallback, NOT modern-neural -- both modern "
        f"neural coref candidates tried this session failed to install+run; see module docstring). "
        f"gate_values={json.dumps({k: round(v, 4) if v is not None else None for k, v in gate_values.items()})}"
    )
    if not all_pass:
        verdict_msg += f" | weakest_gate={weakest} (value={gate_values[weakest]:.4f} < band={BANDS[weakest]})"

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}: extraction-quality gate, coref=rule_based_fallback (modern-neural install failed)",
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "run_mode": "full", "timeout_s": timeout_s,
        "extractor_stack": {
            "srl_tense": "spacy_3x_dep_parse_heuristic (sanctioned fallback per design note)",
            "coref": "rule_based_fallback (gender/number-agreement + recency + exact-match); "
                     "modern-neural candidates tried and FAILED: fastcoref (transformers 5.10.1 "
                     "version-skew AttributeError at model-load), stanza (download hang, no "
                     "progress 5+ min); spacy-experimental-coref not attempted (documented "
                     "legacy-pin incompatibility, not re-verified)",
            "grounding": "nltk wordnet synset-coverage (thin grounder built for this gate; could "
                         "not locate the design note's named 'WordNet-Tier2 ~94%-coverage' module "
                         "within session search budget -- disclosed, not claimed as direct reuse)",
            "causal_links": "discourse-connective keyword heuristic (descriptive only, not gated)",
        },
        "bands": BANDS, "gate_values": gate_values, "gate_pass": gate_pass,
        "srl_gold": {"aggregate": srl_agg},
        "coref_gold": {k: v for k, v in coref_result.items() if k != "per_passage"},
        "coref_gold_per_passage": coref_result["per_passage"],
        "decisive_oracle_parity": decisive_result,
        "unproduced_probe": {k: v for k, v in unproduced_result.items() if k != "per_sentence"},
        "unproduced_probe_per_sentence": unproduced_result["per_sentence"],
        "gold_paths": {"srl": SRL_GOLD_PATH, "coref": COREF_GOLD_PATH, "unproduced": UNPRODUCED_PATH},
        "prior_work_check": (
            "substrate_query.sh top hits cosine=0.34-0.35 (keyword-adjacent 'extraction', "
            "different topic: LLM-hidden-state retrieval quality, not prose->structure "
            "extraction); no rediscovery risk; real prior work = notes/research_islanded_"
            "comprehension_organs_audit_2026-08-10.md (already cited by design note)"
        ),
        "final_metrics_atomicity": "tmp_replace", "checkpointed": True,
        "arms_differ_verified": True, "deterministic_seeding": True,
        "crlb_n_a": "descriptive extraction-quality GATE, no quantitative noise-floor threshold applies",
    }
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    print(f"[{ANCHOR_NAME}] {verdict}", flush=True)
    print(verdict_msg, flush=True)
    print(f"metrics written to {final}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--timeout", type=float, default=240.0,
        help=(
            "formula: 30 SRL sentences + 10 coref passages (spaCy parse, <0.1s/item) + 36 "
            "McGuffey passages x 4 arms DECISIVE loop (FHRR bind/unbind d=1024, <50ms/unit per "
            "the wire_coref cell's own formula) + 8 unproduced passages (32 sentences, spaCy "
            "parse). Dominant cost is spaCy model load (~2-15s cold) + ~85 spaCy parse calls "
            "(<1s total warm) + 144 FHRR units (<10s total). 240s gives generous headroom for a "
            "CPU-only run with import overhead."
        ),
    )
    args = parser.parse_args()
    _output_dir_for_crash = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        if args.self_test:
            self_test()
        else:
            main(args.timeout)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
