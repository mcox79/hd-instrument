"""Skunkworks 2026-06-20 -- DEMOTE a1_8a + a1v2 (the 5MM-batch #2/#3 I earlier KEPT) -> MEASURED_MECHANISM.
Completes the 5MM audit. Verify-the-referent on my OWN prior approval: my 2026-06-19 disposition #2/#3 approved
these for chain-grade on a 'referent-survives' criterion -- but that is necessary-not-sufficient (it makes them
CERTIFIABLE-AS-MEASUREMENTS = MEASURED_MECHANISM, NOT a chain-grade WIN). Both are single-seed (n_seeds=1)
verdict=ATTRIBUTION measurements -- the SAME class my disposition #1 (a1_multihop) correctly ruled MM. My #2/#3
approval was INCONSISTENT with my #1 ruling. Correcting: single-seed ATTRIBUTION measurement = MEASURED_MECHANISM.
(a1v2 even self-labels record_class=measured_mechanism.) So ALL 5 of the 5MM batch were single-seed mis-promotions.

Targets -> MEASURED_MECHANISM:
  #2 T3/EXP_a1_8a_4channel_attribution_v1   (n_seeds=1, ATTRIBUTION, by-construction)
  #3 T3/EXP_a1v2_ratio_profile_v1           (n_seeds=1, ATTRIBUTION, record_class=measured_mechanism contradiction)

A5: PRE CERT=589 -> POST CERT=587 (-2); axiom 206 UNCHANGED (algebra=None); cap_pres 6/6; atoms +0; Store re-loads.
pq-only change + demote provenance. ASCII. Line-by-line meta?? -- NO, these are math-partition T3/EXP atoms. Path-scoped commit by caller.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ROOT = Path('data/substrate_index'); MATH = ROOT / 'math' / 'atoms.jsonl'
DEMOTES = {
  'T3/EXP_a1_8a_4channel_attribution_v1': ('MEASURED_MECHANISM',
     'demoted from CERT_CHAIN_GRADE (5MM #2): single-seed (n=1) ATTRIBUTION measurement; my 2026-06-19 disposition approved chain-grade on referent-survives (necessary-not-sufficient = certifiable-as-MEASUREMENT, not a robust WIN). Consistent with my #1 a1_multihop MM ruling. -> MEASURED_MECHANISM.'),
  'T3/EXP_a1v2_ratio_profile_v1': ('MEASURED_MECHANISM',
     'demoted from CERT_CHAIN_GRADE (5MM #3): single-seed (n=1) ATTRIBUTION measurement + record_class=measured_mechanism (self-labeled MM, contradiction with pq=chain-grade). Same class as a1_multihop. -> MEASURED_MECHANISM.'),
}


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
    if not pre_mod or pre_ax != 206 or pre_cert != 589:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=589). HALT."); return 1
    for tid in DEMOTES:
        a = ps.get_atom(tid)
        if a is None or (a.metadata or {}).get('provenance_quality') != 'CERT_CHAIN_GRADE':
            print(f"PRE-GATE FAIL: {tid} not CERT_CHAIN_GRADE (={(a.metadata or {}).get('provenance_quality') if a else 'MISSING'}). HALT."); return 1

    tmp = MATH.with_suffix('.jsonl.tmp'); n_done = n_lines = 0
    with MATH.open(encoding='utf-8') as src, tmp.open('w', encoding='utf-8') as dst:
        for line in src:
            n_lines += 1; s = line.strip()
            if not s: dst.write(line); continue
            obj = json.loads(s)
            if obj.get('id') in DEMOTES:
                new_pq, note = DEMOTES[obj['id']]
                md = obj.get('metadata') or {}
                if md.get('provenance_quality') != 'CERT_CHAIN_GRADE':
                    print(f"HALT: {obj['id']} pq!=chain-grade mid-write."); dst.close(); tmp.unlink(missing_ok=True); return 1
                md['provenance_quality'] = new_pq
                md['demoted_from'] = 'CERT_CHAIN_GRADE'
                md['demoted_by'] = 'skunkworks_5MM_kept_audit_demote_2026-06-20'
                md['demote_note'] = note
                obj['metadata'] = md
                dst.write(json.dumps(obj, ensure_ascii=False) + "\n"); n_done += 1
            else:
                dst.write(line)
    os.replace(tmp, MATH)
    print(f"demoted {n_done}/2 atoms ({n_lines} lines scanned)")

    ps2 = PartitionedStore(ROOT)
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    pqs = {tid: (ps2.get_atom(tid).metadata or {}).get('provenance_quality') for tid in DEMOTES}
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}, expect 0) CERT={post_cert} (expect 587) axiom={post_ax} (expect 206) cap_pres={post_mod}")
    for tid,pq in pqs.items(): print(f"  {tid} -> {pq}")
    gate = (post_atoms==pre_atoms and post_cert==587 and post_ax==206 and post_mod and n_done==2
            and all(pqs[t]=='MEASURED_MECHANISM' for t in DEMOTES))
    print("GATE:", "OK -- CERT 589->587 (5MM #2/#3 demoted, audit complete)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
