"""Skunkworks 2026-06-20 -- DEMOTE the 3 mis-promoted atoms from the 5MM-batch execution drift.
Paper-trail: my 2026-06-19 per-atom disposition (skunkworks_to_exp_dev_research_5MM_per_atom_disposition)
ruled #1 keep-MEASURED_MECHANISM, #4 rglob-or-rerun, #5 RE-RUN -- but execution promoted ALL to CERT_CHAIN_GRADE.
Verify-the-referent (this session) confirmed: #1 self-declares MM; #4/#5 metrics_path points to a DIFFERENT
experiment (exp_substrate_broad_envelope_*) = broken cert-chain. DEMOTE all 3 out of chain-grade.

Targets:
  #1 T3/EXP_a1_multihop_provenance_cpu_v1      -> MEASURED_MECHANISM (genuine measurement, valid referent, single-seed by-construction control)
  #4 T3/EXP_t3_phaseA2_2level_recovery_cpu_v1  -> RESEARCH_FINDING (referent BROKEN -> points to broad_envelope; uncorroborated; needs re-run)
  #5 T3/EXP_partof_2level_completion_cpu_v1    -> RESEARCH_FINDING (referent BROKEN -> points to broad_envelope; uncorroborated; needs re-run)

A5 gates: PRE CERT=592 -> POST CERT=589 (-3, the declared drop); axiom 206 UNCHANGED (algebra=None on all 3);
cap_pres 6/6; atoms UNCHANGED (+0, in-place pq edit); Store re-loads (no NULL-seam). pq is the ONLY field changed
(+ demote provenance fields). ASCII. Path-scoped commit by caller. Line-by-line partition rewrite + os.replace.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ROOT = Path('data/substrate_index'); MATH = ROOT / 'math' / 'atoms.jsonl'
DEMOTES = {
    'T3/EXP_a1_multihop_provenance_cpu_v1': ('MEASURED_MECHANISM',
        'demoted from CERT_CHAIN_GRADE: my 2026-06-19 5MM disposition #1 ruled keep-MEASURED_MECHANISM (single-seed n=1, 1.0/1.0 by-construction control, no pre-reg band, NOT a HARD_PASS WIN); execution mis-promoted to chain-grade. valid referent -> MM.', False),
    'T3/EXP_t3_phaseA2_2level_recovery_cpu_v1': ('RESEARCH_FINDING',
        'demoted from CERT_CHAIN_GRADE: my 2026-06-19 5MM disposition #4 ruled rglob-or-RERUN (mis-pointer, do-NOT-accept-as-is); metrics_path points to exp_substrate_broad_envelope_rerun_4and5 = a DIFFERENT experiment -> broken cert-chain, uncorroborated. needs re-run for a genuine cert.', True),
    'T3/EXP_partof_2level_completion_cpu_v1': ('RESEARCH_FINDING',
        'demoted from CERT_CHAIN_GRADE: my 2026-06-19 5MM disposition #5 ruled RE-RUN (run-output gone); metrics_path points to exp_substrate_broad_envelope_postreapply1 = a DIFFERENT experiment -> broken cert-chain, uncorroborated. needs re-run for a genuine cert.', True),
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
    if not pre_mod or pre_ax != 206 or pre_cert != 592:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=592). HALT."); return 1
    for tid in DEMOTES:
        a = ps.get_atom(tid)
        if a is None or (a.metadata or {}).get('provenance_quality') != 'CERT_CHAIN_GRADE':
            print(f"PRE-GATE FAIL: {tid} not found or not CERT_CHAIN_GRADE (={(a.metadata or {}).get('provenance_quality') if a else 'MISSING'}). HALT."); return 1
        print(f"  will demote {tid}: CERT_CHAIN_GRADE -> {DEMOTES[tid][0]}")

    tmp = MATH.with_suffix('.jsonl.tmp'); n_done = n_lines = 0
    with MATH.open(encoding='utf-8') as src, tmp.open('w', encoding='utf-8') as dst:
        for line in src:
            n_lines += 1; s = line.strip()
            if not s: dst.write(line); continue
            obj = json.loads(s); oid = obj.get('id')
            if oid in DEMOTES:
                new_pq, note, broken = DEMOTES[oid]
                md = obj.get('metadata') or {}
                if md.get('provenance_quality') != 'CERT_CHAIN_GRADE':
                    print(f"HALT: {oid} pq!=chain-grade mid-write. abort."); dst.close(); tmp.unlink(missing_ok=True); return 1
                md['provenance_quality'] = new_pq
                md['demoted_from'] = 'CERT_CHAIN_GRADE'
                md['demoted_by'] = 'skunkworks_5MM_drift_demote_2026-06-20'
                md['demote_note'] = note
                if broken:
                    md['referent_broken'] = True
                    md['needs_rerun'] = True
                obj['metadata'] = md
                dst.write(json.dumps(obj, ensure_ascii=False) + "\n"); n_done += 1
            else:
                dst.write(line)
    os.replace(tmp, MATH)
    print(f"demoted {n_done}/3 atoms in {MATH} ({n_lines} lines scanned)")

    ps2 = PartitionedStore(ROOT)
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    pqs = {tid: (ps2.get_atom(tid).metadata or {}).get('provenance_quality') for tid in DEMOTES}
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}, expect 0) CERT={post_cert} (expect 589) axiom={post_ax} (expect 206) cap_pres={post_mod}")
    for tid,pq in pqs.items(): print(f"  {tid} -> pq={pq}")
    gate = (post_atoms==pre_atoms and post_cert==589 and post_ax==206 and post_mod and n_done==3
            and all(pqs[t]==DEMOTES[t][0] for t in DEMOTES))
    print("GATE:", "OK -- CERT 592->589 (3 5MM-drift demotes), axiom/cap_pres/atoms intact" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
