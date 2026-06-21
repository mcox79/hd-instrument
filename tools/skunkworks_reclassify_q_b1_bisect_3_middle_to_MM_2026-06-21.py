"""Skunkworks 2026-06-21 -- landed-VET reclassify NEW-2: the 3 q_b1_bisect MIDDLE_BAND chain-grades -> MEASURED_MECHANISM
(bisection-by-design transition points). Cluster RECONCILED by me (Research's HP/HF counts were off): FULL cluster = 7
atoms, CLEAN MONOTONE bisection -- PASS d275/d276 (genuine depth-capability, KEEP) -> MIDDLE d277/d278/d281 (transition
zone, reclassify) -> HARD_FAIL d287/d293 (genuine proven-limit, KEEP); max-PASS 276 < min-FAIL 287. The 3 MIDDLE are the
bisection's TRANSITION DATA (not independent chain-grade results) -> counting each as chain-grade over-counts -> MM.
Collective finding (kept in honest_scope): chain-depth onset in transition zone d277-d281, bracketed PASS<=276 / FAIL>=287,
N=16384, n_seeds=5. The PASS (d275/d276) + FAIL (d287/d293) STAY chain-grade (genuine results). CERT 585 -> 582.
A5: PRE CERT=585 -> POST 582 (-3); axiom 206; cap_pres 6/6; atoms +0; reloads. ASCII. line-by-line JSONL rewrite.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ROOT = Path('data/substrate_index'); MATH = ROOT / 'math' / 'atoms.jsonl'
TARGETS = {'T3/EXP_q_b1_bisect_d277_v1_n16384', 'T3/EXP_q_b1_bisect_d278_v1_n16384', 'T3/EXP_q_b1_bisect_d281_v1_n16384'}
SCOPE = ('q_b1 chain-depth bisection TRANSITION point (bisection-by-design): this depth lands in the MIDDLE transition '
         'zone (d277-d281) of a clean MONOTONE depth-bisection -- PASS<=d276 (chain works) -> MIDDLE d277-d281 (transition) '
         '-> HARD_FAIL>=d287 (chain breaks), N=16384, n_seeds=5. NOT an independent chain-grade capability result; it is '
         'transition DATA locating the chain-depth onset. Collective finding: onset bracketed to (276, 287) with transition '
         'd277-d281. MEASURED_MECHANISM (the PASS endpoints d275/d276 + FAIL endpoints d287/d293 stay chain-grade as genuine '
         'depth-capability / proven-limit; the transition points are de-counted from the headline to avoid over-counting one '
         'bisection as 3 separate chain-grades). Composes with q_b1_chain_depth_200 + CERT 592 K_max NESS envelope.')


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
    if not pre_mod or pre_ax != 206 or pre_cert != 585:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=585). HALT."); return 1
    for tid in TARGETS:
        a = ps.get_atom(tid)
        if a is None or (a.metadata or {}).get('provenance_quality') != 'CERT_CHAIN_GRADE' or (a.metadata or {}).get('verdict') != 'MIDDLE_BAND':
            print(f"PRE-GATE FAIL: {tid} not CERT_CHAIN_GRADE/MIDDLE_BAND. HALT."); return 1

    tmp = MATH.with_suffix('.jsonl.tmp'); n=0
    with MATH.open(encoding='utf-8') as src, tmp.open('w', encoding='utf-8') as dst:
        for line in src:
            s=line.strip()
            if not s: dst.write(line); continue
            obj=json.loads(s); tid=obj.get('id')
            if tid in TARGETS:
                md=obj.get('metadata') or {}
                if md.get('provenance_quality')!='CERT_CHAIN_GRADE':
                    print(f"HALT: {tid} pq mismatch mid-write."); dst.close(); tmp.unlink(missing_ok=True); return 1
                md['provenance_quality']='MEASURED_MECHANISM'
                md['demoted_from']='CERT_CHAIN_GRADE_MIDDLE_BAND'
                md['demoted_by']='skunkworks_q_b1_bisect_bisection_by_design_landed_VET_2026-06-21'
                md['verdict']='MEASURED_MECHANISM'
                md['honest_scope']=SCOPE
                md['reclassify_note']='bisection-by-design transition point -> MM (cluster reconciled by Skunkworks: monotone 7-atom bisection PASS<=276/MIDDLE 277-281/FAIL>=287; transition data not independent chain-grade)'
                obj['metadata']=md
                dst.write(json.dumps(obj, ensure_ascii=False)+"\n"); n+=1
                print(f"  RECLASSIFY -> MM: {tid}")
            else:
                dst.write(line)
    os.replace(tmp, MATH)

    ps2 = PartitionedStore(ROOT)
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    ok=all((ps2.get_atom(t).metadata or {}).get('provenance_quality')=='MEASURED_MECHANISM' for t in TARGETS)
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}) CERT={post_cert} (expect 582) axiom={post_ax} (expect 206) cap_pres={post_mod} all_MM={ok} n={n}")
    gate=(post_atoms==pre_atoms and post_cert==582 and post_ax==206 and post_mod and n==3 and ok)
    print("GATE:", "OK -- 3 q_b1_bisect MIDDLE transition-points reclassified -> MM (CERT 585->582)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
