"""Skunkworks 2026-06-19 at-bandwidth: (a) reconcile the 3 duplicate audit_lesson instance_numbers (S1->0) +
(b) atomize the stale-canonical-doc AUDIT_LESSON (Research-routed candidate; witness 0f184fea).

(a) DUP-RECONCILE (my lane per Research accept): instance_number must be UNIQUE per kind. 3 collisions
    (92/236/237, x2 each). Policy: the LEXICOGRAPHICALLY-FIRST atom-id keeps the number; the SECOND gets the
    next-available MAIN-sequence number (canonical direction; not a new high-number scheme). The existing 234-238
    batch's NON-dup members stay (Director catalog-audit's holistic scheme-canonicalization, separately).
(b) STALE-CANONICAL-DOC: a canonical doc (CLAUDE.md) can lag a USER directive; verify-the-referent on the DOC
    itself. Witness = the 2026-06-18 CLAUDE.md catch (Orchestrator about-to-kill notes_monitor.sh per stale doc;
    USER v5 directive had superseded; flag-don't-act; Research updated CLAUDE.md 0f184fea). Composes verify-referent
    PARENT + the result-narrative-vs-actual-data layer (doc-narrative vs latest-directive = same structural pattern).

META / TIER_METHODOLOGY / algebra=None. A5-safe: snapshot -> 1 add + 3 updates -> verify (S1=0 + atoms +1 + CERT
572 + axiom 206 + read-back). ASCII; apostrophe-free.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

VTR_PARENT = 'AUDIT_verify_the_referent_check_passed_on_wrong_object_verify_referent_reaches_consumer'
STALE_ID = 'AUDIT_canonical_doc_can_lag_user_directive_verify_referent_on_doc'


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


def kname(a):
    return a.kind.value if hasattr(a.kind, 'value') else str(a.kind)


def renum(a, new_inst, src):
    md = dict(a.metadata or {})
    old = md.get('instance_number')
    md['instance_number'] = new_inst
    md.setdefault('instance_number_history', []).append({'old': old, 'new': new_inst, 'reason': 'dup-reconcile S1', 'by': src})
    return Atom(id=a.id, name=a.name, description=a.description, kind=a.kind, tier=a.tier, corpus=a.corpus,
                algebra=a.algebra, metadata=md, aliases=a.aliases, concept_links=a.concept_links,
                complexity=a.complexity, current_best_solution=a.current_best_solution, equivalences=a.equivalences,
                serves_capability=a.serves_capability, signature=a.signature, solution_history=a.solution_history)


STALE_DESC = (
    "A CANONICAL doc (CLAUDE.md, a process-spec, a README) can LAG a USER directive: the doc text says X while a "
    "more-recent USER-LOCKED directive has made Y canonical. When discipline-APPLYING a canonical doc, verify-the-"
    "referent on the DOC ITSELF -- check whether a later USER directive / Skunkworks BROADCAST / cert-architecture "
    "rule SUPERSEDES the doc text. The discipline-application of a stale doc is correct in FORM but wrong in "
    "CONCLUSION; the catch is in the FLAG-DONT-ACT step. Witness (2026-06-18): Orchestrator was about to kill 5 "
    "notes_monitor.sh processes flagged as deprecated-cruft per CLAUDE.md, but the USER v5 directive ~12h earlier had "
    "made notes_monitor.sh CANONICAL -- the CLAUDE.md text was STALE; Orchestrator flagged-not-acted (verify-before-"
    "asserting), Research updated CLAUDE.md (commit 0f184fea). STRUCTURAL PARALLEL to result-narrative-vs-actual-data "
    "(the verify-referent layer): the DOC is a NARRATIVE about expected state; the latest USER directive is the "
    "authoritative DATA; the narrative drifts, the data is authoritative. CANDIDATE (w=1; the CLAUDE.md catch); NOT "
    "load-bearing until 3 witnesses."
)
STALE_WITNESS = (
    "2026-06-18 CLAUDE.md stale-doc catch: Orchestrator about-to-kill notes_monitor.sh per CLAUDE.md "
    "deprecated-watcher text; USER v5 directive ~00:25 had made notes_monitor.sh CANONICAL (event-bus-tail "
    "superseded); Orchestrator FLAGGED-not-acted; USER surfaced the conflict; Research updated CLAUDE.md (0f184fea). "
    "The doc-referent was stale relative to the latest USER directive."
)


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    al = [a for a in ps.all_atoms() if kname(a) == 'audit_lesson']
    insts = [a.metadata.get('instance_number') for a in al if isinstance(a.metadata.get('instance_number'), int)]
    main_max = max(n for n in insts if n < 200)
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod} main_max={main_max}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL. HALT."); return 1

    # (a) dup-reconcile: for 92/236/237, keep lexicographically-first, renumber the second
    from collections import defaultdict
    by_inst = defaultdict(list)
    for a in al:
        n = a.metadata.get('instance_number')
        if isinstance(n, int):
            by_inst[n].append(a)
    next_inst = main_max + 1  # stale-doc takes main_max+1; renumbers take the following
    stale_inst = next_inst
    next_inst += 1
    renum_plan = []
    for dup_n in sorted(d for d, lst in by_inst.items() if len(lst) > 1):
        second = sorted(by_inst[dup_n], key=lambda a: a.id)[1]  # lexicographically-second
        renum_plan.append((second, dup_n, next_inst))
        next_inst += 1

    # (b) stale-doc atom
    if ps.get_atom('meta::' + STALE_ID) is None and not any(a.id == STALE_ID for a in ps.all_atoms()):
        stale = Atom(
            id=STALE_ID,
            name=('Audit lesson (CANDIDATE; verify): a canonical doc (CLAUDE.md) can LAG a USER directive -- '
                  'verify-the-referent on the DOC itself; flag-dont-act if the doc-referent is stale'),
            description=STALE_DESC, kind=AtomKind.AUDIT_LESSON, tier=Tier.TIER_METHODOLOGY, corpus=Corpus.META,
            algebra=None,
            metadata={
                'lesson_class': 'verify', 'confirmed_or_candidate': 'CANDIDATE', 'witnesses_count': 1,
                'witnesses': [STALE_WITNESS], 'NOT_load_bearing_until_3_witnesses': True,
                'instance_number': stale_inst,
                'instance_number_provenance': 'Skunkworks 2026-06-19 Research-routed stale-canonical-doc candidate (CLAUDE.md catch)',
                'term_class': 'PROCESS_KNOWLEDGE_NON_MATH', 'witness_commit': '0f184fea',
                'composes_with': [VTR_PARENT], 'verify_the_referent_family': True, 'verify_the_referent_parent': VTR_PARENT,
                'structural_parallel': 'result-narrative-vs-actual-data layer (doc-narrative vs latest-USER-directive)',
                'eleventh_rule_clean': True, 'substrate_internal_verified': True,
                'source': 'stale_canonical_doc_claude_md_catch_skunkworks_2026_06_19',
            })
        ps.add_atom(stale, source='skunkworks_stale_canonical_doc_2026_06_19', note=f'stale-canonical-doc AUDIT_LESSON inst {stale_inst}')
        added = 1
    else:
        print("stale-doc exists; skip add."); added = 0

    for atom, old_n, new_n in renum_plan:
        ps.add_atom(renum(atom, new_n, 'skunkworks_dup_reconcile_2026_06_19'),
                    source='skunkworks_dup_reconcile_2026_06_19', note=f'dup-reconcile inst {old_n}->{new_n}')

    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    al2 = [a for a in ps2.all_atoms() if kname(a) == 'audit_lesson']
    insts2 = [a.metadata.get('instance_number') for a in al2 if isinstance(a.metadata.get('instance_number'), int)]
    from collections import Counter
    dups2 = {n: c for n, c in Counter(insts2).items() if c > 1}
    stale_ok = any(a.id == STALE_ID for a in al2)
    gate = (post_cert == pre_cert and post_ax == 206 and post_mod and post_atoms == pre_atoms + added
            and not dups2 and stale_ok)
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}; expect +{added}) CERT={post_cert} axiom={post_ax} cap_pres={post_mod}")
    print(f"  stale-doc inst={stale_inst} present={stale_ok} | renum_plan={[(a.id[:40],o,n) for a,o,n in renum_plan]}")
    print(f"  S1 duplicate instance_numbers now: {dups2 or 'NONE (0 dups)'}")
    print("GATE:", "OK" if gate else "FAIL")
    return 0 if gate else 3


if __name__ == '__main__':
    raise SystemExit(main())
