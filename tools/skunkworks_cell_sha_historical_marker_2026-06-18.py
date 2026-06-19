"""Skunkworks 2026-06-18 -- push-fix loop-closer: 1 AUDIT_LESSON marking the cell_sha traceability caveat.

After the 2026-06-18 tar-purge HISTORY-REWRITE (a95b47b4 -> c4451230), the 3487 atoms carrying a `cell_sha`
field reference PRE-REWRITE commit SHAs. This records: that is TRACEABILITY-degradation, NOT a cert-break
(content is path-recoverable; the multi-hop-provenance gate resolves atom->atom links, not git-SHAs); MITIGATION
= the preserved commit-map (old->new SHA). Makes the caveat QUERYABLE (a future reader who finds a stale cell_sha
learns: predates the rewrite; remap via the map; content path-recoverable).

META / TIER_METHODOLOGY / algebra=None (process-knowledge -> NOT cert-counted -> CERT 571 unchanged; NOT axiom).
A5-safe: snapshot CERT/axiom/cap_pres -> add (single guarded) -> verify + read-back. ASCII; apostrophe-free.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

VTR_PARENT = 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer'
MARKER_ID = 'AUDIT_history_rewrite_stales_commit_sha_refs_preserve_commit_map_traceability_not_cert'


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


DESC = (
    "A git HISTORY-REWRITE (e.g. git-filter-branch/filter-repo purging a large blob) re-hashes every commit, so "
    "ALL commit-SHA references stored INSIDE atoms go stale. On 2026-06-18 the tar-purge rewrite (origin/main "
    "a95b47b4 -> c4451230, removing the 1.7GB data_remote_pull.tar) re-hashed 85 commits; the 3487 atoms carrying "
    "a cell_sha field now reference pre-rewrite SHAs. This is TRACEABILITY-degradation, NOT a cert-break: the cell "
    "CONTENT is preserved (path-recoverable) and the cert-claims are content-based (the multi-hop-provenance gate "
    "resolves atom->atom links, not git-SHAs); CERT/axiom/cap_pres were verified byte-identical across the rewrite. "
    "MITIGATION (applied): the filter-branch commit-map (old<TAB>new SHA, 85 lines) was preserved at "
    "data/push_fix_2026-06-18_tar_purge_commit_map.txt -- any stale cell_sha is remappable. Do NOT mass-remap the "
    "3487 (cert is fine); keep the map. GENERAL LESSON: before a history-rewrite, snapshot cert-state (verify "
    "byte-identical after) AND preserve the commit-map for any in-atom SHA references. CANDIDATE (w=1; the "
    "2026-06-18 tar-purge); NOT load-bearing until 3 witnesses."
)
WITNESS = (
    "2026-06-18 tar-purge history-rewrite (push-fix priority-0): a95b47b4 -> c4451230; 1.7GB data_remote_pull.tar "
    "purged to resolve GH001; 3487 cell_sha atoms staled; cert-state verified byte-identical (atoms 43899 / CERT "
    "571 / axiom 206 / cap_pres 6/6 pre==post via the invariant-check); commit-map preserved; Skunkworks "
    "cert-safety AGREE + post-rewrite PASS + UNFREEZE."
)


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    al_inst = [a.metadata.get('instance_number') for a in ps.all_atoms()
               if (a.kind.value if hasattr(a.kind, 'value') else a.kind) == 'audit_lesson'
               and isinstance(a.metadata.get('instance_number'), int)]
    next_inst = max([n for n in al_inst if n < 200] or [0]) + 1
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod} next_inst={next_inst}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL. HALT."); return 1
    if ps.get_atom('meta::' + MARKER_ID) is not None or any(a.id == MARKER_ID for a in ps.all_atoms()):
        print("SKIP exists."); return 0
    atom = Atom(
        id=MARKER_ID,
        name=('Audit lesson (CANDIDATE; durability): a git history-rewrite stales ALL in-atom commit-SHA refs '
              '(cell_sha) -- traceability-degradation NOT cert-break (content path-recoverable); preserve the commit-map'),
        description=DESC, kind=AtomKind.AUDIT_LESSON, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META, algebra=None,
        metadata={
            'lesson_class': 'durability', 'confirmed_or_candidate': 'CANDIDATE', 'witnesses_count': 1,
            'witnesses': [WITNESS], 'NOT_load_bearing_until_3_witnesses': True, 'instance_number': next_inst,
            'instance_number_provenance': ('Skunkworks 2026-06-18 push-fix loop-closer: the cell_sha traceability '
                                           'caveat from the tar-purge rewrite; promote on 3 witnesses'),
            'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
            'commit_map_path': 'data/push_fix_2026-06-18_tar_purge_commit_map.txt',
            'n_cell_sha_atoms_staled': 3487, 'rewrite': 'a95b47b4->c4451230',
            'not_cert_break_reason': 'content path-recoverable; multi-hop-provenance resolves atom->atom not git-sha; cert-state byte-identical pre==post',
            'composes_with': [VTR_PARENT, 'AUDIT_gpu_routed_not_gpu_exercised_full_run_0_util_cpu_default_device'],
            'verify_the_referent_family': True, 'verify_the_referent_parent': VTR_PARENT,
            'eleventh_rule_clean': True, 'substrate_internal_verified': True,
            'source': 'cell_sha_historical_marker_tar_purge_rewrite_skunkworks_2026_06_18',
        })
    ps.add_atom(atom, source='skunkworks_cell_sha_historical_marker_2026_06_18', note='push-fix loop-closer: cell_sha traceability caveat marker')
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    chk = ps2.get_atom('meta::' + MARKER_ID) or next((a for a in ps2.all_atoms() if a.id == MARKER_ID), None)
    gate = (post_cert == pre_cert and post_ax == 206 and post_mod and post_atoms == pre_atoms + 1
            and chk is not None and chk.algebra is None)
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect {pre_cert}) axiom={post_ax} "
          f"cap_pres={post_mod} present={chk is not None} algebra={getattr(chk,'algebra','MISSING')} inst={next_inst}")
    print("GATE:", "OK" if gate else "FAIL")
    return 0 if gate else 3


if __name__ == '__main__':
    raise SystemExit(main())
