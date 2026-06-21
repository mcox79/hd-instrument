"""Skunkworks 2026-06-21 -- landed-VET reclassify 3 WRONG-BAR-preempted MIDDLE_BAND chain-grades -> MEASURED_MECHANISM.
Research's 5-hidden-positives drill (negatives-drill v2); I landed-VET'd off the cell verdict_msg (load-bearing numbers
reproduce) + symmetric guard (these are WRONG-BAR i.e. aspirational/unachievable bar preempted measurement, NOT honest
pre-reg-band misses -> data-decides-tier -> MM). 3 of 5 CONFIRMED here; NEW-2 (bisect cluster counts mismatch) + NEW-4
(random-control not in local metrics) HELD pending verification.
  NEW-1 continual_learning_empirical_10e9x: 1000x was large-LLM-aspiration; genuine = 27x speedup + zero-forget (Pythia-160M, 3-seed).
  NEW-3 drosophila_mb_sparsity_sweep: best-f=0.01 only 2/3 caused MIDDLE; genuine ROBUST arm = f=0.05 +0.142 (3/3 seeds). f=0.01 stays honest-miss.
  NEW-5 data_attribution_counterfactual_rpe: HP rho>=0.8 UNACHIEVABLE (TracIn baseline ALSO 0.693) = wrong-bar; genuine = CPE matches TracIn (0.694) at 4.16x speedup, 5-seed.
This is a DEMOTE-for-honesty (chain-grade MIDDLE -> MM CERT-neutral); CERT 588 -> 585. Symmetric (I don't resist a downward correction).
A5: PRE CERT=588 -> POST 585 (-3); axiom 206 (algebra=None, untouched); cap_pres 6/6; atoms +0; reloads. ASCII. line-by-line JSONL rewrite.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ROOT = Path('data/substrate_index'); MATH = ROOT / 'math' / 'atoms.jsonl'
RECLASS = {
  'T3/EXP_substrate_continual_learning_empirical_10e9x_v1': (
    'substrate continual learning 27x faster than LLM + ZERO forgetting (Pythia-160M, 3-seed, n_train_streams=2); '
    'genuine measured win. The MIDDLE_BAND was the 1000x LARGE-LLM-SCALE ASPIRATION preempting measurement (wrong-bar, '
    'NOT a pre-reg miss) -- 1000x is large-LLM-scale; Pythia-160M conservative. MEASURED_MECHANISM (the 27x+no-forget is '
    'the genuine characterization; composes as the Pythia-LLM cross-axis no-forget referent for the continual-write lever).'),
  'T3/EXP_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu': (
    'fly-LSH sparse encoding lifts N=512 capacity by +0.142 at f=0.05 (3/3 seeds, ROBUST) -- the genuine measured lift. '
    'The MIDDLE_BAND was anchored on best-f=0.01 which was only 2/3 seeds (borderline); per symmetric guard the f=0.05 arm '
    'is the robust positive, f=0.01 STAYS an honest miss. MEASURED_MECHANISM (PARTIAL; composes with a3f473dd sparse super-capacity).'),
  'T3/EXP_substrate_data_attribution_counterfactual_rpe_v1_n4096': (
    'substrate-native CPE data-attribution MATCHES TracIn (CPE rho=0.694 vs TracIn baseline rho=0.693) at 4.16x speedup '
    '(n=4096, 5-seed) -- genuine parity-at-speedup. The MIDDLE_BAND was the pre-reg HP rho>=0.8 which is UNACHIEVABLE BY '
    'EITHER method (TracIn baseline also caps ~0.69) = wrong-bar (mis-set target), NOT an honest substrate-specific miss. '
    'The within-cell TracIn control is the symmetric verifier (7315be3c controls discipline). MEASURED_MECHANISM (parity-at-4.16x-speedup).'),
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
    for tid in RECLASS:
        a = ps.get_atom(tid)
        if a is None or (a.metadata or {}).get('provenance_quality') != 'CERT_CHAIN_GRADE':
            print(f"PRE-GATE FAIL: {tid} not CERT_CHAIN_GRADE. HALT."); return 1

    tmp = MATH.with_suffix('.jsonl.tmp'); n=0
    with MATH.open(encoding='utf-8') as src, tmp.open('w', encoding='utf-8') as dst:
        for line in src:
            s=line.strip()
            if not s: dst.write(line); continue
            obj=json.loads(s)
            tid=obj.get('id')
            if tid in RECLASS:
                md=obj.get('metadata') or {}
                if md.get('provenance_quality') != 'CERT_CHAIN_GRADE':
                    print(f"HALT: {tid} pq!=chain-grade mid-write."); dst.close(); tmp.unlink(missing_ok=True); return 1
                md['provenance_quality']='MEASURED_MECHANISM'
                md['demoted_from']='CERT_CHAIN_GRADE_MIDDLE_BAND'
                md['demoted_by']='skunkworks_wrongbar_hidden_positive_landed_VET_2026-06-21'
                md['verdict']='MEASURED_MECHANISM'
                md['honest_scope']=RECLASS[tid]
                md['reclassify_note']=('wrong-bar-preempted MIDDLE_BAND -> MM (Research 5-hidden-positives drill v2; '
                                       'Skunkworks landed-VET off cell verdict_msg, load-bearing numbers reproduce; symmetric '
                                       'guard: wrong/unachievable-bar not honest-pre-reg-miss -> data-decides-tier -> MM)')
                obj['metadata']=md
                dst.write(json.dumps(obj, ensure_ascii=False)+"\n"); n+=1
                print(f"  RECLASSIFY -> MM: {tid}")
            else:
                dst.write(line)
    os.replace(tmp, MATH)

    ps2 = PartitionedStore(ROOT)
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    ok_pq = all((ps2.get_atom(t).metadata or {}).get('provenance_quality')=='MEASURED_MECHANISM' for t in RECLASS)
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}, expect 0) CERT={post_cert} (expect 585) axiom={post_ax} (expect 206) cap_pres={post_mod} all_MM={ok_pq} n={n}")
    gate=(post_atoms==pre_atoms and post_cert==585 and post_ax==206 and post_mod and n==len(RECLASS) and ok_pq)
    print("GATE:", "OK -- 3 wrong-bar hidden-positives reclassified MIDDLE-chain-grade -> MM (CERT 588->585)" if gate else "FAIL")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms}")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
