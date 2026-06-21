"""Skunkworks 2026-06-21 -- atomize 1 META discipline (CERT-NEUTRAL): verify-the-referent-arrives applies to DATA paths
(not just atoms). Research-endorsed (data-referent-drift finding: phase05 npz 40k->509 truncation, 10 certs affected).
METHODOLOGY_RULE / META / TIER_METHODOLOGY / algebra=None / pq=None -> does NOT touch CERT 583.
A5: PRE CERT=583 -> POST 583 UNCHANGED; axiom 206 UNCHANGED; cap_pres 6/6; +1 atom; reloads. ASCII. Idempotent.
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


ATOM = Atom(
    id='RULE_verify_referent_arrives_applies_to_data_paths_not_just_atoms',
    name=('Methodology rule: verify-the-referent-ARRIVES applies to DATA paths, not just atoms -- a re-VET / re-run MUST '
          'confirm the data file is the SAME (n_tok / shape / provenance) as the cert recorded, else it verifies against '
          'a DRIFTED referent (truncated/moved/replaced) and can mis-flag a valid cert OR validate against wrong data'),
    description=(
        'A cert atom that hardcodes a DATA path is a reproducibility hazard if that path can be TRUNCATED / MOVED / '
        'REPLACED after the run. A future re-verification (landed-VET re-run, audit, reproduction) reads the CURRENT file '
        'at that path -- which may differ from what the cert recorded -- so it verifies against the WRONG referent. '
        'EVIDENCE (2026-06-21): exp_phase05 llama-1b residuals npz was TRUNCATED from the recorded n_tok=40000 to 509 '
        'tokens (the 40k+ pool moved to data/llama_1b_results/, 106427x2048); 10 CERT_CHAIN_GRADE atoms hardcode the now-'
        '509 path. The certs RAN VALID (results recorded), but any re-VET-from-path would silently get n_tok=509 -> a wrong '
        'result -> mis-flag a valid cert. RULE: (a) a re-VET/re-run MUST first confirm the data file matches the cert-'
        'recorded n_tok/shape (and hash/provenance if available) BEFORE trusting the recompute -- a mismatch means verify-'
        'the-referent FAILED (wrong data), halt + re-point/restore; (b) cells SHOULD record data shape+provenance '
        '(n_tok, shape, content-hash, canonical-path) in metrics so drift is DETECTABLE; (c) canonical data should be '
        'path-stable or provenance-pinned. This is verify-the-referent-arrives (the producer-acted-AND-the-right-thing-'
        'arrived discipline) extended from Store atoms to DATA files. Symmetric: a drifted-data re-VET can FALSE-demote a '
        'valid cert (re-ran on truncated data) as easily as false-validate -- so confirm-the-data-referent is load-bearing '
        'BOTH directions.'),
    kind=AtomKind.METHODOLOGY_RULE, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
    metadata={'extracted_by':'skunkworks','extracted_date':'2026-06-21','term_class':'methodology','eleventh_rule_clean':True,
              'substrate_internal_verified':True,'status':'active','confidence':'high','rule_class':'data_referent_integrity',
              'witnesses':['phase05_llama1b_npz_truncated_40k_to_509_10_certs_hardcode_path_2026-06-21'],
              'composes_with':['RULE_landed_vet_must_check_existing_atom_not_just_rule_result',
                               'feedback_verify_the_referent_arrives_not_just_producer_acted'],
              'research_endorsed':True,'source':'skunkworks_session_2026-06-21_data_referent_drift_finding'})


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 583:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=583). HALT."); return 1
    existed = ps.get_atom(ATOM.qualified_id) is not None
    if existed:
        print(f"  SKIP exists: {ATOM.id}")
    else:
        ps.add_atom(ATOM, source='skunkworks_data_path_referent_drift_discipline_2026_06_21',
                    note='data-referent-drift discipline (CERT-neutral; Research-endorsed; phase05-npz witness)')
        print(f"  ADD: {ATOM.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(ATOM.qualified_id); landed = a2 is not None
    bad = landed and ((a2.algebra is not None) or (a2.metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE')
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 583 UNCHANGED) axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} bad={bad}")
    gate = (post_cert==583 and post_ax==206 and post_mod and landed and not bad and post_atoms==pre_atoms+(0 if existed else 1))
    print("GATE:", "OK -- data-referent-drift discipline atomized, CERT 583 UNCHANGED (CERT-neutral)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
