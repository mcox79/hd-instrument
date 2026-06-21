"""Skunkworks 2026-06-21 -- RELEVANCE-promote 2 atoms recognizing the genuine 2-level-ingest composed-reasoning lift
(buried-positive from sub-audit batch 1; Research lineage ruling concurred + verified). COUNT-NEUTRAL: relevance_tier
ARCHIVE -> SUPPORTING; provenance_quality UNTOUCHED (CERT 588 UNCHANGED -- relevance != pq).
 - T3/EXP_b_alpha_broad_v3_2level: 2-level ingest lifts composed-reasoning 3HP/2M/0HF vs envelope's 0HP/3M/2HF;
   path_provenance_self_check sound (0 unverifiable edges) = GENUINE coverage, not by-construction. Distinct finding.
 - T3/EXP_partof_broad_before: same 3HP/2M/0HF lift pattern (paired with partof_broad_after PASS endpoint). Distinct.
A5: PRE CERT=588 -> POST 588 (relevance edit, atoms UNCHANGED); axiom 206; cap_pres 6/6; Store re-loads. ASCII. Idempotent.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ROOT = Path('data/substrate_index'); MATH = ROOT / 'math' / 'atoms.jsonl'
TARGETS = {'T3/EXP_b_alpha_broad_v3_2level', 'T3/EXP_partof_broad_before'}
NEW_REL = 'SUPPORTING'
NOTE = ('relevance-promote ARCHIVE->SUPPORTING: genuine 2-level-ingest composed-reasoning LIFT (3HP/2M/0HF vs canonical '
        'envelope 0HP/3M/2HF), path_provenance_self_check sound (0 unverifiable edges = real-edge coverage gain, NOT '
        'by-construction). Distinct finding (the envelope caveat "denser ingest untested" made testable+positive), not a '
        'superseded preview. Sub-audit batch 1 buried-positive; Research lineage ruling concurred. pq/CERT UNCHANGED.')


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


def main():
    ps = PartitionedStore(ROOT)
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206 or pre_cert != 588:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=588). HALT."); return 1
    for tid in TARGETS:
        a = ps.get_atom(tid)
        if a is None or (a.metadata or {}).get('provenance_quality') != 'CERT_CHAIN_GRADE':
            print(f"PRE-GATE FAIL: {tid} not CERT_CHAIN_GRADE. HALT."); return 1

    tmp = MATH.with_suffix('.jsonl.tmp'); n_done = 0
    with MATH.open(encoding='utf-8') as src, tmp.open('w', encoding='utf-8') as dst:
        for line in src:
            s = line.strip()
            if not s: dst.write(line); continue
            obj = json.loads(s)
            if obj.get('id') in TARGETS:
                md = obj.get('metadata') or {}
                if md.get('provenance_quality') != 'CERT_CHAIN_GRADE':
                    print("HALT: pq!=chain-grade mid-write."); dst.close(); tmp.unlink(missing_ok=True); return 1
                md['relevance_tier'] = NEW_REL
                md['relevance_promoted_from'] = 'ARCHIVE'
                md['relevance_promote_by'] = 'skunkworks_2level_ingest_lift_2026-06-21'
                md['relevance_promote_note'] = NOTE
                obj['metadata'] = md
                dst.write(json.dumps(obj, ensure_ascii=False) + "\n"); n_done += 1
                print(f"  PROMOTE relevance->{NEW_REL}: {obj.get('id')}")
            else:
                dst.write(line)
    os.replace(tmp, MATH)

    ps2 = PartitionedStore(ROOT)
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    ok_rel = all((ps2.get_atom(t).metadata or {}).get('relevance_tier')==NEW_REL for t in TARGETS)
    ok_pq = all((ps2.get_atom(t).metadata or {}).get('provenance_quality')=='CERT_CHAIN_GRADE' for t in TARGETS)
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}, expect 0) CERT={post_cert} (expect 588) axiom={post_ax} (expect 206) cap_pres={post_mod} rel_ok={ok_rel} pq_kept={ok_pq}")
    gate = (post_atoms==pre_atoms and post_cert==588 and post_ax==206 and post_mod and n_done==len(TARGETS) and ok_rel and ok_pq)
    print("GATE:", "OK -- 2 relevance-promotes (ARCHIVE->SUPPORTING), CERT 588 UNCHANGED (count-neutral)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms} (count-neutral, low-stakes)")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
