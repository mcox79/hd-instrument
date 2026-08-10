"""Gold-corpus builder for the extraction-quality gate (notes/design_extraction_quality_gate_
neural_foundation_2026-08-10.md). Author-constructed, MODERN (not McGuffey/19th-c.) contemporary
English -- small positive-control gold, same pattern as other islanded-organ cells in this repo
(exp_bridge1_twostage_event_situation used ~20-24 hand-curated items; exp_pun_coherence_alarm_
viability_probe used real lexical resources over curated sentences). OntoNotes/CoNLL-2012 (the
standard SRL/coref benchmark) is not available in this repo/offline and is not fetched here.

Role words (AGENT/PRED/PATIENT) are identified by exact surface-text match against a spaCy-parsed
token, then LEMMATIZED BY SPACY ITSELF (not typed by hand) -- this keeps gold and prediction on the
SAME lemmatizer convention, so SRL-F1 measures genuine role/predicate-selection correctness, not
lemmatizer spelling idiosyncrasy (e.g. spaCy's en_core_web_sm lemmatizes "installing" -> "instal",
single-L; typing "install" by hand would produce a false SRL-F1 penalty unrelated to extraction
quality). TENSE is authored directly by the human (independent ground truth, not derived from the
extractor's own tense heuristic -- that would be circular).

Produces:
  gold_srl_tense_modern_v1.jsonl   -- 30 single-clause sentences, PRED/AGENT/PATIENT/TENSE gold
  gold_coref_modern_v1.jsonl       -- 10 mini coref passages (2-3 entities, 3-4 sentences each)

Run: .venv/Scripts/python.exe data/eval_gold_extraction_quality_gate_v1/build_gold_v1.py
"""
from __future__ import annotations

import json
import os

import spacy

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# (sentence, agent_word, pred_word, patient_word_or_None, tense_bucket)
# tense_bucket in {"past", "pres", "fut"}; PRED word is the INFLECTED verb as it appears (PRED
# is looked up as ROOT/xcomp head; for "will X" sentences the PRED word is the bare verb X, not
# "will" itself).
SRL_ITEMS = [
    # ---- past (10) ----
    ("The engineer fixed the server before the outage spread.", "engineer", "fixed", "server", "past"),
    ("Maria reviewed the contract carefully.", "Maria", "reviewed", "contract", "past"),
    ("The city council approved the new bike lanes.", "council", "approved", "lanes", "past"),
    ("Investors funded the startup after the demo.", "Investors", "funded", "startup", "past"),
    ("The nurse administered the vaccine to the patient.", "nurse", "administered", "vaccine", "past"),
    ("The coach benched the star player.", "coach", "benched", "player", "past"),
    ("The journalist published the report on Friday.", "journalist", "published", "report", "past"),
    ("Workers repaired the bridge over the weekend.", "Workers", "repaired", "bridge", "past"),
    ("The teacher graded the essays last night.", "teacher", "graded", "essays", "past"),
    ("The company recalled the defective batteries.", "company", "recalled", "batteries", "past"),
    # ---- present (10) ----
    ("The engineer reviews the failing build every morning.", "engineer", "reviews", "build", "pres"),
    ("The app collects usage data automatically.", "app", "collects", "data", "pres"),
    ("The manager approves expense reports weekly.", "manager", "approves", "reports", "pres"),
    ("The committee reviews grant applications each spring.", "committee", "reviews", "applications", "pres"),
    ("The chef prepares the sauce fresh daily.", "chef", "prepares", "sauce", "pres"),
    ("The sensor monitors the water level continuously.", "sensor", "monitors", "level", "pres"),
    ("The editor rejects most unsolicited submissions.", "editor", "rejects", "submissions", "pres"),
    ("The pharmacy dispenses the medication after verification.", "pharmacy", "dispenses", "medication", "pres"),
    ("The algorithm ranks the search results by relevance.", "algorithm", "ranks", "results", "pres"),
    ("The landlord inspects the apartment every quarter.", "landlord", "inspects", "apartment", "pres"),
    # ---- future (10) ----
    ("The committee will announce its decision next week.", "committee", "announce", "decision", "fut"),
    ("The airline will cancel the delayed flight.", "airline", "cancel", "flight", "fut"),
    ("The city will replace the aging pipes next year.", "city", "replace", "pipes", "fut"),
    ("The board will review the proposal on Monday.", "board", "review", "proposal", "fut"),
    ("The technician will install the new router tomorrow.", "technician", "install", "router", "fut"),
    ("The union will negotiate the new contract in June.", "union", "negotiate", "contract", "fut"),
    ("The store will restock the shelves overnight.", "store", "restock", "shelves", "fut"),
    ("The agency will investigate the complaint thoroughly.", "agency", "investigate", "complaint", "fut"),
    ("The professor will publish the findings this fall.", "professor", "publish", "findings", "fut"),
    ("The team will launch the product in March.", "team", "launch", "product", "fut"),
]

# 10 mini coref passages, modern content, 2-3 entities each, mention text + owning entity_id +
# sentence index (mentions may repeat verbatim in different sentences; sentence index disambiguates).
COREF_PASSAGES = [
    {
        "passage_id": "modern_coref_001",
        "sentences": [
            "Maria fixed the leaking pipe before the plumber arrived.",
            "She had noticed the leak the night before.",
            "The plumber thanked her for catching it early.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "Maria", "entity_id": "e1"},
            {"sent_idx": 0, "text": "the plumber", "entity_id": "e2"},
            {"sent_idx": 1, "text": "She", "entity_id": "e1"},
            {"sent_idx": 2, "text": "The plumber", "entity_id": "e2"},
            {"sent_idx": 2, "text": "her", "entity_id": "e1"},
        ],
    },
    {
        "passage_id": "modern_coref_002",
        "sentences": [
            "The manager reviewed Tom's proposal on Tuesday.",
            "He found two errors in the budget section.",
            "Tom corrected them before the next meeting.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "The manager", "entity_id": "e1"},
            {"sent_idx": 0, "text": "Tom", "entity_id": "e2"},
            {"sent_idx": 1, "text": "He", "entity_id": "e1"},
            {"sent_idx": 2, "text": "Tom", "entity_id": "e2"},
        ],
    },
    {
        "passage_id": "modern_coref_003",
        "sentences": [
            "The startup hired a new engineer named Priya.",
            "She had worked at a larger firm for six years.",
            "The founders were impressed by her portfolio.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "Priya", "entity_id": "e1"},
            {"sent_idx": 0, "text": "The startup", "entity_id": "e2"},
            {"sent_idx": 1, "text": "She", "entity_id": "e1"},
            {"sent_idx": 2, "text": "The founders", "entity_id": "e2"},
            {"sent_idx": 2, "text": "her", "entity_id": "e1"},
        ],
    },
    {
        "passage_id": "modern_coref_004",
        "sentences": [
            "The airline delayed the flight because of the storm.",
            "It finally departed three hours late.",
            "Passengers complained about the delay online.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "The airline", "entity_id": "e1"},
            {"sent_idx": 0, "text": "the flight", "entity_id": "e2"},
            {"sent_idx": 1, "text": "It", "entity_id": "e2"},
        ],
    },
    {
        "passage_id": "modern_coref_005",
        "sentences": [
            "Diego submitted the grant application last week.",
            "He had spent months preparing the budget.",
            "The committee will review his application in April.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "Diego", "entity_id": "e1"},
            {"sent_idx": 0, "text": "the grant application", "entity_id": "e2"},
            {"sent_idx": 1, "text": "He", "entity_id": "e1"},
            {"sent_idx": 2, "text": "The committee", "entity_id": "e3"},
            {"sent_idx": 2, "text": "his application", "entity_id": "e2"},
        ],
    },
    {
        "passage_id": "modern_coref_006",
        "sentences": [
            "The city council approved a new park downtown.",
            "It will open to the public next summer.",
            "Residents have already started planning events there.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "The city council", "entity_id": "e1"},
            {"sent_idx": 0, "text": "a new park", "entity_id": "e2"},
            {"sent_idx": 1, "text": "It", "entity_id": "e2"},
        ],
    },
    {
        "passage_id": "modern_coref_007",
        "sentences": [
            "Sam and his sister Lily opened a bakery together.",
            "He handles the finances while she bakes every morning.",
            "Customers say her sourdough is the best in town.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "Sam", "entity_id": "e1"},
            {"sent_idx": 0, "text": "Lily", "entity_id": "e2"},
            {"sent_idx": 1, "text": "He", "entity_id": "e1"},
            {"sent_idx": 1, "text": "she", "entity_id": "e2"},
            {"sent_idx": 2, "text": "her", "entity_id": "e2"},
        ],
    },
    {
        "passage_id": "modern_coref_008",
        "sentences": [
            "The pharmacy received a shipment of vaccines on Monday.",
            "It stored them in a refrigerated unit overnight.",
            "Nurses administered the vaccines the next morning.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "The pharmacy", "entity_id": "e1"},
            {"sent_idx": 0, "text": "a shipment of vaccines", "entity_id": "e2"},
            {"sent_idx": 1, "text": "It", "entity_id": "e1"},
            {"sent_idx": 1, "text": "them", "entity_id": "e2"},
            {"sent_idx": 2, "text": "the vaccines", "entity_id": "e2"},
        ],
    },
    {
        "passage_id": "modern_coref_009",
        "sentences": [
            "Elena launched a podcast about local history.",
            "She interviews a new guest every week.",
            "Listeners praised her first episode online.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "Elena", "entity_id": "e1"},
            {"sent_idx": 0, "text": "a podcast", "entity_id": "e2"},
            {"sent_idx": 1, "text": "She", "entity_id": "e1"},
            {"sent_idx": 2, "text": "her", "entity_id": "e1"},
        ],
    },
    {
        "passage_id": "modern_coref_010",
        "sentences": [
            "The technician installed a new router for the office.",
            "It doubled the wireless speed immediately.",
            "Employees noticed the improvement within a day.",
        ],
        "mentions": [
            {"sent_idx": 0, "text": "The technician", "entity_id": "e1"},
            {"sent_idx": 0, "text": "a new router", "entity_id": "e2"},
            {"sent_idx": 1, "text": "It", "entity_id": "e2"},
        ],
    },
]


def _lemma_of(doc, word: str) -> str:
    for tok in doc:
        if tok.text == word:
            return tok.lemma_.lower()
    raise AssertionError(f"word {word!r} not found as a token in {doc.text!r}")


def main() -> None:
    nlp = spacy.load("en_core_web_sm")

    srl_out = os.path.join(OUT_DIR, "gold_srl_tense_modern_v1.jsonl")
    with open(srl_out, "w", encoding="utf-8") as f:
        for i, (sent, agent_w, pred_w, patient_w, tense) in enumerate(SRL_ITEMS):
            doc = nlp(sent)
            rec = {
                "sent_id": f"modern_srl_{i:03d}",
                "text": sent,
                "gold_event": {
                    "PRED": _lemma_of(doc, pred_w),
                    "AGENT": _lemma_of(doc, agent_w),
                    "PATIENT": _lemma_of(doc, patient_w) if patient_w else None,
                    "TENSE": tense,
                },
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(SRL_ITEMS)} SRL/tense gold items -> {srl_out}")

    coref_out = os.path.join(OUT_DIR, "gold_coref_modern_v1.jsonl")
    with open(coref_out, "w", encoding="utf-8") as f:
        for p in COREF_PASSAGES:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"wrote {len(COREF_PASSAGES)} coref gold passages -> {coref_out}")

    # sanity: every mention text must literally occur in its sentence
    n_mentions = 0
    for p in COREF_PASSAGES:
        for m in p["mentions"]:
            sent = p["sentences"][m["sent_idx"]]
            assert m["text"] in sent, f"{p['passage_id']}: mention {m['text']!r} not in {sent!r}"
            n_mentions += 1
    print(f"sanity OK: all {n_mentions} coref mentions found verbatim in their sentence")


if __name__ == "__main__":
    main()
