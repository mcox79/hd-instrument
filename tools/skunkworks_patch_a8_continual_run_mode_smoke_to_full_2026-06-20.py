"""Skunkworks 2026-06-20 -- A5-safe METADATA-ONLY patch on the continual-writes cert atom
(T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1 == the CERT 586 pull-up I landed-VET'd 2026-06-19).

RE-VET FINDING (verify-the-referent on the DATA, not the metadata LABEL): the atom's metadata
run_mode='smoke' was a STALE LABEL. The actual cert referent (data/.../metrics.json, reproduced by
data/exp_a8_continual_writes_dryrun_full) is run_mode=FULL, N=1024, n_seeds=5, HARD_PASS, region_std=0.0,
cliff@alpha=0.30 -- ALL 4 of my standing verdict-VET criteria PASS. So the D2 "smoke-cert" flag from the
CERT-592 audit is RESOLVED as a label artifact: it is NOT a smoke-cert -> NO downgrade, CERT stays 592.

This patch makes the atom verify-the-referent-clean (so a future audit won't re-flag the stale label):
  - run_mode: 'smoke' -> 'full'
  - + run_full_N=1024, run_full_n_seeds=5
  - + cert_vet_status records the 2026-06-20 full-run verdict-VET PASS + D2-flag-resolution
A5-safe: pq + relevance_tier UNTOUCHED (no cert re-classification). Single atom. CERT-neutral (stays 592).
Pattern: line-by-line partition rewrite + os.replace (capint Track-A apply pattern). ASCII. Idempotent.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore

ROOT = Path('data/substrate_index')
MATH = ROOT / 'math' / 'atoms.jsonl'
TARGET = 'T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1'

VET_STATUS = ('RE_VET_skunkworks_2026-06-20_full_run_verdict_VET_PASS_all4criteria_'
              'run_mode_smoke_label_was_STALE_actual_referent_FULL_N1024_5seeds_'
              'reproduced_by_dryrun_full_D2_smoke_cert_flag_RESOLVED_no_downgrade_CERT_stays_592')


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


def patch_line(obj):
    """Mutate the target atom's metadata in place. Return (changed, pq_before, pq_after)."""
    md = obj.get('metadata') or {}
    pq_before = md.get('provenance_quality')
    changed = False
    if md.get('run_mode') != 'full':
        md['run_mode'] = 'full'; changed = True
    if md.get('run_full_N') != 1024:
        md['run_full_N'] = 1024; changed = True
    if md.get('run_full_n_seeds') != 5:
        md['run_full_n_seeds'] = 5; changed = True
    if md.get('cert_vet_status') != VET_STATUS:
        md['cert_vet_status'] = VET_STATUS; changed = True
    obj['metadata'] = md
    return changed, pq_before, md.get('provenance_quality')


def main():
    ps = PartitionedStore(ROOT)
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    a = ps.get_atom(TARGET)
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if a is None:
        print(f"HALT: target {TARGET} not in Store."); return 1
    pre_pq = (a.metadata or {}).get('provenance_quality')
    print(f"PRE target: run_mode={(a.metadata or {}).get('run_mode')} pq={pre_pq}")
    if not pre_mod or pre_ax != 206 or pre_cert != 592:
        print(f"PRE-GATE FAIL (axiom={pre_ax}!=206 or cap_pres={pre_mod} or CERT={pre_cert}!=592). HALT."); return 1

    # line-by-line rewrite of math partition (only target atom mutated)
    tmp = MATH.with_suffix('.jsonl.tmp')
    n_patched = n_lines = 0
    with MATH.open(encoding='utf-8') as src, tmp.open('w', encoding='utf-8') as dst:
        for line in src:
            n_lines += 1
            s = line.strip()
            if not s:
                dst.write(line); continue
            obj = json.loads(s)
            if obj.get('id') == TARGET or obj.get('qualified_id', '').endswith(TARGET):
                changed, pqb, pqa = patch_line(obj)
                if pqb != pqa:
                    print("HALT: pq would change -- A5 violation. Aborting, tmp discarded.")
                    dst.close(); tmp.unlink(missing_ok=True); return 1
                if changed:
                    n_patched += 1
                dst.write(json.dumps(obj, ensure_ascii=False) + "\n")
            else:
                dst.write(line)
    os.replace(tmp, MATH)
    print(f"patched {n_patched} atom(s) in {MATH} ({n_lines} lines scanned)")

    # POST verify off a FRESH load (NULL-seam / A5 gate)
    ps2 = PartitionedStore(ROOT)
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    a2 = ps2.get_atom(TARGET)
    post_rm = (a2.metadata or {}).get('run_mode') if a2 else None
    post_pq = (a2.metadata or {}).get('provenance_quality') if a2 else None
    print(f"POST: atoms={post_atoms} (delta {post_atoms-pre_atoms}, expect 0) CERT={post_cert} (expect 592) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod} run_mode={post_rm} pq={post_pq}")
    gate = (post_atoms == pre_atoms and post_cert == 592 and post_ax == 206 and post_mod
            and post_rm == 'full' and post_pq == pre_pq)
    print("GATE:", "OK -- run_mode label fixed, pq untouched, CERT 592 unchanged" if gate else "FAIL")
    return 0 if gate else 2


if __name__ == '__main__':
    raise SystemExit(main())
