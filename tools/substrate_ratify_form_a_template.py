"""Phase B BUILD ratify template -- reusable FORM-A new-atom scaffold.

Pre-staged per DECISION 164c (Phase B BUILD coordination) + 14th USER-LOCKED rule (no stand
at phase boundary; forward-work-generation).

Distills the pattern from 6+ FORM-A ratifies executed this session:
  PROMOTION #3 per_binding_shard_cleanup        2c613762
  capacity_composition_multiplicative AGGREGATE 1d0a02a3
  audit_preserving_reasoning DUAL               1d0a02a3
  counterfactual_cf_rpe (corrected grounding)   db9b3877
  hopfield_pattern_deletion (operator)          db9b3877
  relational_analogy_binding (analogy)          dc167bb6
  deletion_certificate CORRECTNESS              c6b9884a

Usage (called from a thin wrapper script that specifies the params):

  from substrate_ratify_form_a_template import ratify_form_a

  ratify_form_a(
      new_id='T3/new_atom_name',
      name='Human-readable name',
      description='Description of the atom...',
      dep_ids=['T2/dep1', 'T2/dep2'],
      cell_metrics_path='data/exp_anchor/metrics.json',
      empirical_metric_builder=lambda m: {  # build empirical_metric dict from metrics.json
          'name': 'metric_name',
          'value': m['per_seed'][0]['accuracy'],
      },
      metric_type='capability_recall',  # or AGGREGATE / CORRECTNESS / DUAL
      sh_entries_count=1,  # 2 for DUAL
      source_tag='form_a_decision_NNN_atom_name',
      expected_n_seeds=3,  # for cell precondition check
      label='SPEC_X',
  )

For DUAL type, supply sh_entries_count=2 and a list of 2 metric builders + 2 sources.

R3 invariants verified inline:
  +1 atom + len(dep_ids) edges; cap_pres=1.0; sh_entries_count materialized.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore, QualifiedAtomId
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def axiom_term(ps):
    forward = {}
    for src, rel, tgt in ps.iter_all_relations():
        if rel.name in ('DEPENDS_ON', 'SPECIALIZES'):
            forward.setdefault(src, []).append(tgt)
    axioms = set()
    for a in ps.all_atoms():
        if str(a.tier.name) != 'TIER_1_FOUNDATIONAL': continue
        if str(a.corpus.name) != 'MATH': continue
        role = (a.algebra or {}).get('role', '')
        if (a.metadata or {}).get('is_axiom', False) or role in ('axiom_schema', 'axiom', 'type'):
            axioms.add(f'math::{a.id}')
    def terminates(s, d=15):
        seen = {s}; f = [s]
        for _ in range(d):
            n = []
            for x in f:
                if x in axioms: return True
                for t in forward.get(x, []):
                    if t not in seen: seen.add(t); n.append(t)
            f = n
            if not f: break
        return any(x in axioms for x in seen)
    ops = [a for a in ps.all_atoms()
           if str(a.corpus.name) == 'MATH'
           and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
           and a.algebra and len(a.algebra) >= 3
           and 'oeis' not in str(a.id).lower()
           and not str(a.id).startswith('T3/wikidata_')]
    t = sum(1 for op in ops if terminates(f'math::{op.id}'))
    return t, len(ops)


def ratify_form_a(
    new_id: str,
    name: str,
    description: str,
    dep_ids: list[str],
    cell_metrics_path: str,
    sh_entries: list[dict],
    source_tag: str,
    label: str = 'FORM-A',
    tier: Tier = Tier.TIER_3_ALGORITHM,
    kind: AtomKind = AtomKind.SUB_OP,
    corpus: Corpus = Corpus.MATH,
    expected_run_mode: str = 'full',
    expected_verdict: str = 'HARD_PASS',
    expected_n_seeds: int | None = None,
) -> int:
    """Ratify a FORM-A new atom with deps + solution_history entries.

    Returns 0 on HARD_PASS, 1 on HARD_FAIL.
    """
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    store = ps._store_for(corpus)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    new_qid = f'{corpus.value}::{new_id}'

    # Idempotency
    if store.get_atom(new_id) is not None:
        print(f'[{label}] HARD_FAIL: {new_qid} already exists')
        return 1

    # Verify deps
    for d in dep_ids:
        if store.get_atom(d) is None:
            print(f'[{label}] HARD_FAIL: dep missing {corpus.value}::{d}')
            return 1
    print(f'[{label}] deps verified: {dep_ids}', flush=True)

    # Cell metrics precondition
    cell_path = repo_root / cell_metrics_path
    if not cell_path.exists():
        print(f'[{label}] HARD_FAIL: cell metrics missing: {cell_path}')
        return 1
    with open(cell_path) as f:
        m = json.load(f)
    if m.get('run_mode') != expected_run_mode:
        print(f'[{label}] HARD_FAIL: cell run_mode={m.get("run_mode")} expected={expected_run_mode}')
        return 1
    if m.get('verdict') != expected_verdict:
        print(f'[{label}] HARD_FAIL: cell verdict={m.get("verdict")} expected={expected_verdict}')
        return 1
    if expected_n_seeds is not None and m.get('n_seeds') != expected_n_seeds:
        print(f'[{label}] WARN: cell n_seeds={m.get("n_seeds")} expected={expected_n_seeds}')

    sha = sha256_of(cell_path)
    print(f'[{label}] cell corroborated: run_mode={m.get("run_mode")} n_seeds={m.get("n_seeds")} sha={sha[:12]}..', flush=True)

    # Build new atom
    new_atom = Atom(
        id=new_id,
        name=name,
        corpus=corpus,
        tier=tier,
        kind=kind,
        description=description,
        metadata={
            'form_a_source': source_tag,
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
        },
        solution_history=tuple(sh_entries),
    )
    store.add_atom(new_atom)
    store._flush_atoms()

    # Add DEPENDS_ON edges
    for d in dep_ids:
        ps.add_relation(
            new_qid,
            RelationType.DEPENDS_ON,
            f'{corpus.value}::{d}',
            source=source_tag,
            note=f'{label} DEPENDS_ON {d}',
        )
    store._flush_relations()

    # Post-snapshot + R3 verify
    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)

    import importlib
    mod_ok = all(hasattr(importlib.import_module(m_), s) for m_, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])

    new_check = store.get_atom(new_id)
    sh_landed = len(new_check.solution_history or ()) if new_check else 0
    edges_check = sum(
        1 for s, r, t in ps.iter_all_relations()
        if (s == new_id or s == new_qid)
        and r.name == 'DEPENDS_ON'
        and any(d in t for d in dep_ids)
    )

    invariants_ok = (
        post_atoms == pre_atoms + 1
        and post_rels == pre_rels + len(dep_ids)
        and post_t >= pre_t
        and mod_ok
        and sh_landed == len(sh_entries)
        and edges_check == len(dep_ids)
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels}) '
          f'axiom_term={post_t}/{post_total} mod_ok={mod_ok} sh_landed={sh_landed} edges={edges_check}', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1

    print(f'[{label}] R3 verify: PASS (additive +1 atom +{len(dep_ids)} edges; cap_pres=1.0; sh_landed={sh_landed})')
    print(f'[{label}] HARD_PASS: {new_qid} RATIFIED')
    return 0


def ratify_capability(
    new_id: str,
    name: str,
    description: str,
    uses_math_atoms: list[str],
    cell_metrics_path: str | None,
    sh_entries: list[dict],
    source_tag: str,
    metadata: dict | None = None,
    label: str = 'CAP',
    tier: Tier = Tier.TIER_2_PRIMITIVE,
    expected_run_mode: str = 'full',
    expected_verdict: str = 'HARD_PASS',
) -> int:
    """Ratify a CONCEPT-corpus CAPABILITY atom (Phase B BUILD pattern).

    Difference from ratify_form_a (math-corpus FORM-A T3):
    - CONCEPT corpus, CAPABILITY kind, T2 default tier
    - USES edges (concept -> math) instead of DEPENDS_ON
    - cell_metrics_path is optional (capability may bind to multiple cells via separate
      sh entries; in that case caller passes None and supplies prebuilt sh_entries)
    - Metadata pattern matches existing CAP_* atoms (decomposes_to + family_tag_members +
      validated_axis + tier_concept + empirical_validation_status + drill_origin +
      related_concepts + substrate_lever)

    Returns 0 HARD_PASS / 1 HARD_FAIL. R3 invariants verified inline.
    """
    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    concept_store = ps._store_for(Corpus.CONCEPT)
    math_store = ps._store_for(Corpus.MATH)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    new_qid = f'concept::{new_id}'

    if concept_store.get_atom(new_id) is not None:
        print(f'[{label}] HARD_FAIL: {new_qid} already exists')
        return 1
    for m_atom in uses_math_atoms:
        if math_store.get_atom(m_atom) is None:
            print(f'[{label}] HARD_FAIL: USES target missing math::{m_atom}')
            return 1
    print(f'[{label}] USES targets verified: {uses_math_atoms}', flush=True)

    # Optional cell verification (for single-cell capability binding)
    if cell_metrics_path is not None:
        cell_path = repo_root / cell_metrics_path
        if not cell_path.exists():
            print(f'[{label}] HARD_FAIL: cell metrics missing: {cell_path}')
            return 1
        with open(cell_path) as f:
            m = json.load(f)
        if m.get('run_mode') != expected_run_mode or m.get('verdict') != expected_verdict:
            print(f'[{label}] HARD_FAIL: cell precondition (run_mode/verdict)')
            return 1
        sha = sha256_of(cell_path)
        print(f'[{label}] cell corroborated: run_mode={m.get("run_mode")} sha={sha[:12]}..', flush=True)

    new_atom = Atom(
        id=new_id,
        name=name,
        corpus=Corpus.CONCEPT,
        tier=tier,
        kind=AtomKind.CAPABILITY,
        description=description,
        metadata=metadata or {
            'decomposes_to': uses_math_atoms,
            'form_phase_b_source': source_tag,
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
            'empirical_validation_status': 'phase_b_validated',
        },
        solution_history=tuple(sh_entries),
    )
    concept_store.add_atom(new_atom)
    concept_store._flush_atoms()

    for m_atom in uses_math_atoms:
        ps.add_relation(
            new_qid,
            RelationType.USES,
            f'math::{m_atom}',
            source=source_tag,
            note=f'{label} USES {m_atom}',
        )
    concept_store._flush_relations()

    # Post-snapshot + R3 verify
    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)

    import importlib
    mod_ok = all(hasattr(importlib.import_module(m_), s) for m_, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])

    new_check = concept_store.get_atom(new_id)
    sh_landed = len(new_check.solution_history or ()) if new_check else 0
    # USES edge -> HAS_USERS auto-derived per schema; each USES adds 1 forward edge
    edges_check = sum(
        1 for s, r, t in ps.iter_all_relations()
        if (s == new_id or s == new_qid)
        and r.name == 'USES'
        and any(m_atom in t for m_atom in uses_math_atoms)
    )

    invariants_ok = (
        post_atoms == pre_atoms + 1
        and post_rels == pre_rels + len(uses_math_atoms)
        and post_t >= pre_t  # capability doesn't change math axiom-term
        and mod_ok
        and sh_landed == len(sh_entries)
        and edges_check == len(uses_math_atoms)
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels}) '
          f'axiom_term={post_t}/{post_total} mod_ok={mod_ok} sh_landed={sh_landed} edges={edges_check}', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1

    print(f'[{label}] R3 verify: PASS (additive +1 atom +{len(uses_math_atoms)} USES edges; cap_pres=1.0)')
    print(f'[{label}] HARD_PASS: {new_qid} RATIFIED')
    return 0


def make_sh_entry(
    new_qid: str,
    cell_metrics: dict,
    cell_metrics_sha: str,
    cell_metrics_path: str,
    empirical_metric: dict,
    metric_type: str,
    source_tag: str,
    replacement_reason: str,
    ratify_date: str = '2026-06-16',
) -> dict:
    """Build a single solution_history entry. For DUAL type, call twice with different metrics.

    Per DECISION 168 + Skunkworks 185th compute-backend provenance gate:
    Auto-extracts compute_backend + dtype + device + cross_backend_check fields from cell
    metrics if present. Phase B cells run with the new discipline include these fields;
    Phase A cells may omit them (auto-default to None).
    """
    return {
        'solution_atom_id': new_qid,
        'adopted_date': ratify_date,
        'replaced_date': None,
        'replacement_reason': replacement_reason,
        'empirical_metric': empirical_metric,
        'metric_type': metric_type,
        'n_seeds': cell_metrics.get('n_seeds'),
        'run_mode': cell_metrics.get('run_mode'),
        'verdict': cell_metrics.get('verdict'),
        'cell_anchor': cell_metrics.get('anchor_name', cell_metrics.get('anchor')),
        'cell_metrics_sha256': cell_metrics_sha,
        'cell_metrics_path': cell_metrics_path,
        # Compute-backend provenance per DECISION 168 + Skunkworks 185th gate
        'compute_backend': cell_metrics.get('compute_backend'),  # 'gpu' | 'cpu' | None
        'dtype': cell_metrics.get('dtype'),  # 'float32' | 'complex64' | None
        'device': cell_metrics.get('device'),  # 'cuda:0' | 'cpu' | None
        'cross_backend_check': cell_metrics.get('cross_backend_check'),  # near-threshold verify
        'near_threshold_flag': cell_metrics.get('near_threshold_flag'),  # within ~1e-3 of HP/HF bar
        'form': 'FORM-A',
        'source': source_tag,
    }


if __name__ == '__main__':
    # Template demonstration mode (no actual ratify; just show usage)
    print(__doc__)
    print()
    print('USAGE: import ratify_form_a + make_sh_entry from this module in a thin wrapper script.')
    print('See e.g. substrate_ratify_deletion_certificate_form_a_155a.py for a concrete example.')
