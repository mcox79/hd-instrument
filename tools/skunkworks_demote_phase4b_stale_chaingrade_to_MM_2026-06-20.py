"""Skunkworks 2026-06-20 -- DEMOTE the STALE phase4b chain-grade atom -> MEASURED_MECHANISM (CERT 589 -> 588).
Inflation catch: T3/EXP_phase4b_multistep_pull_up_v2_cpu_v1 is pq=CERT_CHAIN_GRADE / verdict=HARD_PASS with the OLD
honest_scope ('40x over the 1-op baseline' = the div-by-near-zero ratio I flagged), atomized when phase4b v2 FIRST
HARD_PASSed -- BEFORE my landed-VET ruled it NOT-chain-grade + Exp-Dev reframed the CELL to MEASURED_MECHANISM
(commit 40c88971, ratio dropped). The atom is STALE chain-grade for a NOT-chain-grade result -> inflation.
My phase4b landed-VET ruled the RESULT but didn't check the ATOM already existed (verify-the-referent-arrives gap).

Demote: pq CERT_CHAIN_GRADE -> MEASURED_MECHANISM + honest_scope fixed (drop 40x ratio; native-op-depth claim).
A5: PRE CERT=589 -> POST 588 (-1); axiom 206 UNCHANGED (algebra=None); cap_pres 6/6; atoms +0; Store re-loads. ASCII.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ROOT = Path('data/substrate_index'); MATH = ROOT / 'math' / 'atoms.jsonl'
TARGET = 'T3/EXP_phase4b_multistep_pull_up_v2_cpu_v1'
NEW_SCOPE = ('substrate solves each benchmark at its NATIVE op-depth (op-count-SPECIFIC solver: sharp peak at native depth, '
             'off-depth collapse); MultiArith 2-op composition genuine (acc 0.692, ~11x above chance, seed-stable max_std 0.015); '
             'NO cross-benchmark 2-op generalization (ASDiv/MAWPS peak at 1-op = CONTENT, not composition-failure); the prior '
             '2op/1op ratio (0.68/0.02=40x) was a native-depth/wrong-depth DIVIDE-BY-NEAR-ZERO artifact -- DROPPED, do not cite. '
             'MEASURED_MECHANISM (Skunkworks landed-VET + Exp-Dev reframe 40c88971; "composition generalizes" framing retired).')
NOTE = ('demoted from STALE CERT_CHAIN_GRADE (verdict=HARD_PASS, old 40x-ratio honest_scope): atomized when phase4b v2 first '
        'HARD_PASSed; my landed-VET ruled the RESULT NOT-chain-grade (div-by-near-zero ratio + 2op-only-MultiArith) + Exp-Dev '
        'reframed cell->MEASURED_MECHANISM (40c88971); the atom was stale chain-grade -> inflation. -> MEASURED_MECHANISM.')


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
    a = ps.get_atom(TARGET)
    if a is None or (a.metadata or {}).get('provenance_quality') != 'CERT_CHAIN_GRADE':
        print(f"PRE-GATE FAIL: {TARGET} not CERT_CHAIN_GRADE (={(a.metadata or {}).get('provenance_quality') if a else 'MISSING'}). HALT."); return 1
    if not pre_mod or pre_ax != 206 or pre_cert != 589:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=589). HALT."); return 1

    tmp = MATH.with_suffix('.jsonl.tmp'); n_done = 0
    with MATH.open(encoding='utf-8') as src, tmp.open('w', encoding='utf-8') as dst:
        for line in src:
            s = line.strip()
            if not s: dst.write(line); continue
            obj = json.loads(s)
            if obj.get('id') == TARGET:
                md = obj.get('metadata') or {}
                if md.get('provenance_quality') != 'CERT_CHAIN_GRADE':
                    print("HALT: pq!=chain-grade mid-write."); dst.close(); tmp.unlink(missing_ok=True); return 1
                md['provenance_quality'] = 'MEASURED_MECHANISM'
                md['demoted_from'] = 'CERT_CHAIN_GRADE'
                md['demoted_by'] = 'skunkworks_phase4b_stale_chaingrade_demote_2026-06-20'
                md['demote_note'] = NOTE
                md['honest_scope'] = NEW_SCOPE
                md['verdict'] = 'MEASURED_MECHANISM'
                md['record_class'] = 'measured_mechanism'
                obj['metadata'] = md
                dst.write(json.dumps(obj, ensure_ascii=False) + "\n"); n_done += 1
            else:
                dst.write(line)
    os.replace(tmp, MATH)
    print(f"demoted {n_done}/1")

    ps2 = PartitionedStore(ROOT)
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    pq = (ps2.get_atom(TARGET).metadata or {}).get('provenance_quality')
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}, expect 0) CERT={post_cert} (expect 588) axiom={post_ax} (expect 206) cap_pres={post_mod} phase4b_pq={pq}")
    gate = (post_atoms==pre_atoms and post_cert==588 and post_ax==206 and post_mod and n_done==1 and pq=='MEASURED_MECHANISM')
    print("GATE:", "OK -- phase4b stale chain-grade demoted -> MM (CERT 589->588)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
