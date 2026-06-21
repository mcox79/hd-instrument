"""Skunkworks 2026-06-21 -- FOLD the 2x revival-drill outcomes into the two MM atoms (CERT-neutral edit, CERT 588).
Both revival drills (USER standing directive: every negative gets 2x/3x revival drills) RESOLVED by Exp-Dev,
verified, and they SHARPEN the negatives -- recorded as structured negative-knowledge so the closed angles are
not re-attempted:
 - phase4b: the 1op-MultiArith "anomaly" = CONTENT (only 2.7% of MultiArith is 1-op-solvable -> 1op acc ~0.02 is AT
   the intrinsic ceiling); content-normalized, the substrate solves ~95% of genuinely-2-op-solvable problems at 2-op.
 - LEVER 2 PCA: the discardable-null-space rescue hypothesis (skunkworks-proposed) does NOT rescue -- 2x-confirmed
   ROBUST (cosine+raw-dot x all-dim+null-space-only noise; full-N many-dim averaging/LLN beats any dim-reduction).

Adds a structured metadata['revival_drill_2x'] to each; does NOT touch honest_scope/key_metrics/pq (the load-bearing
characterization stays; pq stays MEASURED_MECHANISM). A5: PRE CERT=588 -> POST 588 (edit, atoms UNCHANGED); axiom 206;
cap_pres 6/6; Store re-loads. ASCII. Idempotent (skip if revival_drill_2x already present).
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ROOT = Path('data/substrate_index'); MATH = ROOT / 'math' / 'atoms.jsonl'

REVIVAL = {
  'T3/EXP_phase4b_multistep_pull_up_v2_cpu_v1': {
    'item': '1op-MultiArith acc~0.02 "anomaly" (revival-drill: bug or content?)',
    'resolution': 'CONTENT, not a representation/parsing bug -- VERIFIED by min-solvable-op-depth enumeration (N=600)',
    'one_op_solvable_frac': 0.027,
    'two_op_solvable_frac': 0.715,
    'detail': ('only 16/600 (2.7%) MultiArith problems are 1-op-solvable -> a 1-op evaluation correctly scores ~0; '
               '429/600 (71.5%) are 2-op-solvable (MultiArith IS a 2-op benchmark). The 1op~0.02 result sits AT the '
               '2.7% intrinsic ceiling -- exactly the wrong-op-depth content-mismatch the MM reframe stated.'),
    'content_normalized_2op_solve_rate': 0.95,
    'content_normalized_note': '0.68 raw / 0.715 (2-op-solvable frac) = ~95% of GENUINELY-2-op-solvable problems solved at 2-op depth',
    'oracle_caveat': '24.7% unsolvable<=4 is a LEFT-TO-RIGHT gold-seq enumerator limit (reorder / >4 ops), NOT a substrate limit',
    'outcome': 'negative-knowledge SHARPENED (no anomaly; 1op=ceiling; content-normalized 2-op capability ~95%); MM stands',
    'by': 'exp_dev_verified_2026-06-21_skunkworks_folded', 'date': '2026-06-21'},
  'T3/EXP_pca_dimension_selector_lever_v1_cpu_v1': {
    'item': 'discardable-null-space rescue hypothesis (skunkworks-proposed revival angle for the PCA-negative)',
    'resolution': 'does NOT rescue -- the PCA-negative is 2x-confirmed ROBUST across every tested regime',
    'tested': 'PCA(k=rank+8) vs full-N across {cosine, raw-dot} readout x {all-dims, null-space-only (orthogonal-to-signal)} noise',
    'nullspace_best_case_delta': 'selk-full = -0.00..-0.19 (PCA never helps; WORSE at high noise even in the best-case orthogonal-noise regime)',
    'mechanism': ('full-N recall AVERAGES noise over many dims (law of large numbers) -> robust; PCA-to-k drops to fewer dims '
                  'and LOSES that averaging, so it is net worse even though it reduces TOTAL noise. Many-dim averaging dominates '
                  'noise-reduction. General to nearest-key recall -- not readout- or noise-locality-specific.'),
    'outcome': 'negative-knowledge CONFIRMED-ROBUST + the proposed rescue regime CLOSED (do not re-attempt dim-reduction for KV recall)',
    'by': 'exp_dev_verified_2026-06-21_skunkworks_folded', 'date': '2026-06-21'},
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
    if not pre_mod or pre_ax != 206 or pre_cert != 588:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 / cap_pres={pre_mod} / CERT={pre_cert}!=588). HALT."); return 1
    for tid in REVIVAL:
        a = ps.get_atom(tid)
        if a is None or (a.metadata or {}).get('provenance_quality') != 'MEASURED_MECHANISM':
            print(f"PRE-GATE FAIL: {tid} not MEASURED_MECHANISM (={(a.metadata or {}).get('provenance_quality') if a else 'MISSING'}). HALT."); return 1

    tmp = MATH.with_suffix('.jsonl.tmp'); n_done = 0
    with MATH.open(encoding='utf-8') as src, tmp.open('w', encoding='utf-8') as dst:
        for line in src:
            s = line.strip()
            if not s: dst.write(line); continue
            obj = json.loads(s)
            tid = obj.get('id')
            if tid in REVIVAL:
                md = obj.get('metadata') or {}
                if md.get('provenance_quality') != 'MEASURED_MECHANISM':
                    print(f"HALT: {tid} pq!=MM mid-write."); dst.close(); tmp.unlink(missing_ok=True); return 1
                if 'revival_drill_2x' in md:
                    print(f"  SKIP (already folded): {tid}"); dst.write(line); continue
                md['revival_drill_2x'] = REVIVAL[tid]
                obj['metadata'] = md
                dst.write(json.dumps(obj, ensure_ascii=False) + "\n"); n_done += 1
                print(f"  FOLD: {tid}")
            else:
                dst.write(line)
    os.replace(tmp, MATH)

    ps2 = PartitionedStore(ROOT)
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    ok_pq = all((ps2.get_atom(t).metadata or {}).get('provenance_quality')=='MEASURED_MECHANISM' for t in REVIVAL)
    ok_fold = all('revival_drill_2x' in (ps2.get_atom(t).metadata or {}) for t in REVIVAL)
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}, expect 0) CERT={post_cert} (expect 588) axiom={post_ax} (expect 206) cap_pres={post_mod} pq_MM={ok_pq} folded={ok_fold}")
    gate = (post_atoms==pre_atoms and post_cert==588 and post_ax==206 and post_mod and ok_pq and ok_fold)
    print("GATE:", "OK -- revival-drill 2x outcomes folded into phase4b + LEVER2 MM atoms (CERT 588 unchanged)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
