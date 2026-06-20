"""Skunkworks 2026-06-20 -- atomize 3 durable META disciplines from this session (CERT-NEUTRAL).
METHODOLOGY_RULE / META / TIER_METHODOLOGY / algebra=None / pq=None -> does NOT touch CERT 589.
A5 gates: PRE CERT=589 -> POST CERT=589 UNCHANGED; axiom 206 UNCHANGED (META not axiom-counted);
cap_pres 6/6; +3 atoms; Store re-loads. ASCII. Idempotent skip-if-exists. Mirrors the cb7e89f1 pattern.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')
def axiom(p):
    return sum(1 for a in p.all_atoms()
               if str(a.corpus.name)=='MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE','TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra)>=3 and 'oeis' not in str(a.id).lower() and not str(a.id).startswith('T3/wikidata_'))
def modlive():
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder','viterbi_decode'),('hdlab.perceptron','StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler','NERTagger'),('hdlab.bayesian_inference','EMMixture'),
        ('backend.substrate_index.intent_classifier','IntentClassifier'),('backend.substrate_index.refuse_gated_retriever','RefuseGatedRetriever')])


def mk(rid, name, desc, rule_class, witnesses):
    return Atom(id=rid, name=name, description=desc,
        kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
        metadata={'extracted_by':'skunkworks','extracted_date':'2026-06-20','term_class':'methodology',
                  'eleventh_rule_clean':True,'substrate_internal_verified':True,'status':'active','confidence':'high',
                  'rule_class':rule_class,'witnesses':witnesses,'composes_with':['RULE_cited_number_must_reproduce_from_the_cell_else_miscite'],
                  'source':'skunkworks_session_2026-06-20_cert_integrity_audit'})


ATOMS = [
  mk('RULE_4_layer_reciprocal_witness_for_high_stakes_ships',
     'Methodology rule: high-stakes chain-grade ships require MULTIPLE INDEPENDENT verification layers (a single verifier misses load-bearing flaws)',
     ('A SINGLE verifier -- even the cell-builder + the cell verdict -- can miss a load-bearing flaw on a high-stakes ship. '
      'Require >=2 INDEPENDENT verification layers that read the CODE/DATA (not the comment/verdict) before landing chain-grade. '
      'EVIDENCE: LEVER #1.5 (capacity_sweet_spot_v1) reported "HARD_PASS chain-grade candidate"; the builder read it as a '
      'working "load-adaptive selector." The flaw -- the selector picks a CONSTANT f=0.01 for ALL loads (a descending-overwrite '
      'loop keeps smallest-viable, not largest, vs the comment) so it is NOT adaptive and merely re-expresses a3f473dd sparse '
      'super-capacity -- surfaced ONLY because 4 independent layers converged: (a) cert-owner landed-VET off per_unit, '
      '(b) an independent selector-logic recompute, (c) Testbed 2nd-witness reading the code, (d) Orchestrator OWNING that its '
      'earlier "4 conditions PASS" verify had checked the COMMENT not the CODE. RULE: for a chain-grade ship, gate on >=2 '
      'independent witnesses that read the actual code/data; a lone pass (or a comment-trusting verify) is insufficient.'),
     'verification_architecture',
     ['LEVER_1_5_capacity_sweet_spot_v1_nonadaptive_selector_caught_by_4_layers_2026-06-20']),
  mk('RULE_label_must_match_aggregation_not_per_aggregate_mean',
     'Methodology rule: a metric LABELED worst/min/max must BE that across units, not a per-aggregate MEAN reported at the worst sub-aggregate',
     ('A metric whose LABEL says "worst"/"min"/"max" must actually BE the worst/min/max ACROSS UNITS -- not a per-aggregate '
      '(per-M, per-config) MEAN reported at the worst sub-aggregate. The cited number can REPRODUCE (as the mean) while the '
      'LABEL misrepresents what it is; a future auditor grepping the label against per_unit data sees a mismatch and false-flags. '
      'EVIDENCE: CERT 591 (kv_learned_projection) verdict "worst=0.827" was actually the M=10000 MEAN; the true worst-per-unit '
      'recall was 0.805 (keysep worst 0.726 vs labeled 0.878). The gates passed either way (non-load-bearing), but the LABEL '
      'was imprecise. RESOLUTION: relabel mean->mean + ADD the true worst_per_unit; pq UNTOUCHED (fidelity, not re-classification). '
      'RULE: verify the label SEMANTICS match the aggregation it reports; this is the label-side of cited-number-must-reproduce.'),
     'label_fidelity',
     ['CERT_591_worst_label_was_per_M_mean_0p827_vs_true_worst_0p805_2026-06-20']),
  mk('RULE_disposition_execution_must_preserve_per_atom_outcomes',
     'Methodology rule: executing a NUANCED per-atom disposition must preserve each per-atom outcome (no flatten); cert-owner verdict-VET gates every pq change',
     ('When a cert-owner issues a NUANCED per-atom disposition (DIFFERENT outcomes per atom -- e.g. promote / keep-tier / re-run), '
      'the EXECUTION must map EACH atom to ITS dispositioned outcome -- NOT flatten the whole batch to a uniform action. And the '
      'cert-owner landed-VET that GATES each pq change must NOT be skipped under batch pressure (it is the safeguard that catches '
      'the flatten at land-time). EVIDENCE: the 5MM batch disposition (2 promote-to-chain-grade / 1 keep-MEASURED_MECHANISM / '
      '2 re-run) was FLATTENED in execution to promote-all-5 -> 3 mis-promotes (a1_multihop should have stayed MM; t3_phaseA2 + '
      'partof_2level had metrics_path pointing to a DIFFERENT experiment = broken cert-chain, ruled re-run). Caught later (CERT '
      '592->589) by verify-the-referent on the DISPOSITION vs the executed Store state. RULE: execution preserves per-atom '
      'outcomes; cert-owner verdict-VET gates every pq change off the referent; verify the executed state against the disposition.'),
     'execution_fidelity',
     ['5MM_batch_flattened_to_promote_all_3_mis_promotes_CERT_592_to_589_2026-06-20']),
]


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 589:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=589). HALT."); return 1
    added = 0
    for at in ATOMS:
        if ps.get_atom(at.qualified_id) is not None:
            print(f"  SKIP exists: {at.id}")
        else:
            ps.add_atom(at, source='skunkworks_3_META_disciplines_2026_06_20', note='session cert-integrity disciplines (CERT-neutral)')
            print(f"  ADD: {at.id}"); added += 1
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = all(ps2.get_atom(at.qualified_id) is not None for at in ATOMS)
    bad_alg = any(ps2.get_atom(at.qualified_id).algebra is not None for at in ATOMS)
    bad_pq = any((ps2.get_atom(at.qualified_id).metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE' for at in ATOMS)
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 589 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} algebra!=None={bad_alg} any_chain_grade={bad_pq}")
    gate = (post_cert==589 and post_ax==206 and post_mod and landed and not bad_alg and not bad_pq
            and post_atoms==pre_atoms+added)
    print("GATE:", "OK -- 3 META disciplines atomized, CERT 589 UNCHANGED (CERT-neutral)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
