"""Skunkworks 2026-06-18 -- Sprint-3 Item 11: 8th-gate evaluation -> REFINE the engine/checklist-separation rule.

Extends RULE_cert_architecture_engine_atomize_vs_checklist_dispatch_separation with the MECHANIZABILITY
DIMENSION (the missing axis) + the narrative-data-consistency 8th-gate-candidate disposition.

FINDING: cert-CORRECTNESS is NECESSARY but NOT SUFFICIENT for an engine-gate; it must ALSO be deterministically
MECHANIZABLE at atomize-time. The A2-misattribution lesson (an atom narrative naming top-items/drivers that the
actual top-ranked data contradicts) is the FIRST candidate that PASSES the cert-correctness test (a narrative
misrepresenting its own data is a TRUTH defect, unlike device-exercise/atom-add which were dispatch-properties
with byte-identical results). BUT it is deterministically mechanizable ONLY via a STRUCTURED-CLAIM convention
(atoms making top-item claims carry claimed_top_items; the engine compares to actual). Until that convention:
SCHEMA-VET condition (manual narrative-vs-data check, as the A2-misattribution was caught).

A5-safe single-atom update (re-add; atoms-count unchanged). META/algebra=None -> CERT/axiom unchanged. ASCII.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom

RULE_ID = 'RULE_cert_architecture_engine_atomize_vs_checklist_dispatch_separation'

MECH = (
    "MECHANIZABILITY DIMENSION (added 2026-06-18, Item-11 8th-gate eval): cert-CORRECTNESS is NECESSARY but NOT "
    "SUFFICIENT for an ENGINE-gate -- the property must ALSO be deterministically MECHANIZABLE at atomize-time. "
    "Decision matrix: (cert-correctness + mechanizable) -> ENGINE-gate; (cert-correctness + NOT-yet-mechanizable) "
    "-> SCHEMA-VET condition until mechanizable; (NOT cert-correctness, i.e. dispatch/performance property) -> "
    "CHECKLIST (never engine), per the original rule. The prior two engine-gate candidates (device-exercise, "
    "atom-add-mechanism) were declined because they failed the CORRECTNESS test (dispatch-properties; byte-identical "
    "results). The mechanizability axis is what gates a cert-correctness property between ENGINE-now and SCHEMA-VET-now."
)
EIGHTH = (
    "8th-gate CANDIDATE = NARRATIVE-DATA-CONSISTENCY (the A2-misattribution lesson, 2026-06-18): an atom whose "
    "narrative (verdict_msg/abstract) NAMES specific top-items/drivers must have those match the atom's ACTUAL "
    "top-ranked data. This is the FIRST candidate that PASSES the cert-correctness test -- a narrative "
    "misrepresenting its own data is a TRUTH defect (the atom claims X drives the result when the data shows Y), "
    "UNLIKE device-exercise/atom-add (dispatch-properties, byte-identical results). DISPOSITION: cert-correctness "
    "ENGINE-ELIGIBLE, but deterministically mechanizable ONLY via a STRUCTURED-CLAIM convention (atoms making "
    "top-item claims carry a structured claimed_top_items field; the engine compares claimed-vs-actual). Free-text "
    "narrative parsing is NOT deterministic -> NOT engine-mechanizable now. CURRENT: enforced as a SCHEMA-VET "
    "condition (the cert-VET-er manually checks narrative-vs-actual-top-data, as the A2 Tarjan/Hopcroft "
    "misattribution was caught). FUTURE: an 8th ENGINE-gate once the structured-claim convention lands. The engine "
    "stays 7 LIVE; this is a SCHEMA-VET condition + a clearly-specified path to an 8th gate."
)
WITNESS = (
    "Item-11 8th-gate eval (2026-06-18): the A2 v6 misattribution (verdict_msg named Tarjan/Hopcroft below the "
    "in-cov floor as the drivers; actual drivers were 7 different near-gaps) = the first cert-correctness "
    "engine-gate candidate; mechanizability dimension distinguishes engine-now (structured-claim) from SCHEMA-VET-now."
)


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom(p):
    return sum(1 for a in p.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def modlive():
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    tgt = ps.get_atom('meta::' + RULE_ID) or next((a for a in ps.all_atoms() if a.id == RULE_ID), None)
    if tgt is None:
        print("RULE NOT FOUND. HALT."); return 2
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod} | rule found")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL. HALT."); return 1
    md = dict(tgt.metadata or {})
    if 'mechanizability_dimension' in md:
        print("SKIP: already refined."); return 0
    md['mechanizability_dimension'] = MECH
    md['eighth_gate_candidate_narrative_data_consistency'] = EIGHTH
    ws = list(md.get('witnesses', []))
    ws.append(WITNESS)
    md['witnesses'] = ws
    md['refined_2026_06_18_skunkworks'] = 'Item-11 8th-gate eval: mechanizability dimension + narrative-data-consistency disposition'
    updated = Atom(
        id=tgt.id, name=tgt.name, description=tgt.description, kind=tgt.kind, tier=tgt.tier, corpus=tgt.corpus,
        algebra=tgt.algebra, metadata=md, aliases=tgt.aliases, concept_links=tgt.concept_links,
        complexity=tgt.complexity, current_best_solution=tgt.current_best_solution, equivalences=tgt.equivalences,
        serves_capability=tgt.serves_capability, signature=tgt.signature, solution_history=tgt.solution_history)
    ps.add_atom(updated, source='skunkworks_8th_gate_eval_mechanizability_dimension_2026_06_18',
                note='Item-11 8th-gate eval: refine engine/checklist rule with mechanizability + narrative-data-consistency')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    chk = ps2.get_atom('meta::' + RULE_ID) or next((a for a in ps2.all_atoms() if a.id == RULE_ID), None)
    refined = 'mechanizability_dimension' in (chk.metadata or {})
    gate = (post_cert == pre_cert and post_ax == 206 and post_mod and post_atoms == pre_atoms and refined)
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}; expect 0=update) CERT={post_cert} axiom={post_ax} "
          f"cap_pres={post_mod} refined={refined}")
    print("GATE:", "OK" if gate else "FAIL")
    return 0 if gate else 3


if __name__ == '__main__':
    raise SystemExit(main())
