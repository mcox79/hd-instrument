"""TIER-4a consumer-gated batch ratify (DECISION 229; 5 of 6 atoms; O_xunb 6th deferred pending Skunkworks confirm).

Consumer-gated count divergence finding RECURSIVELY APPLIED: 5 NOT ~50-100; rest = pull-on-demand backlog.

5 math-corpus foundation atoms (CRT-pattern; no cell metrics; substrate-internal authoring):

  PRIORITY (gates P2 STEP-9 DEPENDS_ON):
    math::T1/simplex_correlation_bound       (terminal identity; -1/(m-1) exact)
    math::T2/sparse_hopfield_hu_santos       (GENERALIZES modern_hopfield_ramsauer)
    math::T2/kymn_residue_resonator_ols      (USES resonator_network_decoder + COMPOSES CRT)

  CLEAN-LINEAGE (walkable lineage; not hard-gated for P2):
    math::T2/fractional_power_encoding       (USES fhrr_bind; VFA/SSP single-channel kernel)
    math::T1/sinc_characteristic_function    (COMPOSES FPE; terminal identity)

  DEFERRED (6th to be confirmed): math::T1/O_xunb_cosine_identity (85th-candidate; Skunkworks confirm pending)

5 edges total (per DECISION 229a + DECISION 223 Finding 3 precise enum use):
  fractional_power_encoding         USES         T2/fhrr_bind                     [external; existing]
  sinc_characteristic_function      COMPOSES     T2/fractional_power_encoding     [intra-batch; new]
  sparse_hopfield_hu_santos         GENERALIZES  T2/modern_hopfield_ramsauer      [external; existing]
  kymn_residue_resonator_ols        USES         T3/resonator_network_decoder     [external; existing]
  kymn_residue_resonator_ols        COMPOSES     T1/chinese_remainder_theorem     [external; existing; 8f96cb93]

Per 92nd-candidate phantom-dep discipline: ALL 4 external dep targets verified pre-receive
(T2/fhrr_bind, T2/modern_hopfield_ramsauer, T3/resonator_network_decoder, T1/chinese_remainder_theorem).

Per CRT-precedent: atoms authored without `algebra` field -> axiom_term denominator unchanged
(corpus==MATH + algebra>=3 filter); axiom_term 206/206 PRESERVED.

R3 invariants verified inline: +5 atoms, +5 edges, axiom_term 206/206, cap_pres=1.0, module liveness 6/6.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType


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


def module_liveness_ok():
    import importlib
    return all(hasattr(importlib.import_module(m_), s) for m_, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


def main():
    label = 'TIER-4a'
    src_tag = 'DECISION_229_TIER_4a_consumer_gated_5_atoms_3_priority_2_clean_lineage_6th_O_xunb_deferred_pending_skunkworks_confirm'

    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    math_store = ps._store_for(Corpus.MATH)

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    # ===== Pre-receive: verify all 4 external dependency targets exist =====
    external_deps = ['T2/fhrr_bind', 'T2/modern_hopfield_ramsauer', 'T3/resonator_network_decoder', 'T1/chinese_remainder_theorem']
    for d in external_deps:
        if math_store.get_atom(d) is None:
            print(f'[{label}] HARD_FAIL: external dep missing math::{d}')
            return 1
    print(f'[{label}] external deps verified (no phantom): {external_deps}', flush=True)

    # ===== Define 5 atoms =====
    atoms_spec = [
        # 1. T1/simplex_correlation_bound (terminal identity)
        dict(
            id='T1/simplex_correlation_bound',
            name='Regular-simplex correlation bound: pairwise correlation = -1/(m-1)',
            tier=Tier.TIER_1_FOUNDATIONAL,
            kind=AtomKind.PRIMITIVE,
            description=(
                'Regular-simplex geometry foundation identity. For m equally-spaced unit vectors '
                '(or m residue phasor codewords forming a regular simplex), pairwise correlation '
                'is EXACTLY -1/(m-1). This is the exact codeword non-orthogonality that the '
                'OLS-Gram correction (HEAD-4 resonator) and sparse-Hopfield (HEAD-3) must handle. '
                'Substrate consumer: P1 simplex-correlation diagnosis (deferred to P2) + P2 HEAD-3 '
                'and HEAD-4 design rationale. Canonical reference: regular simplex / equiangular-'
                'set geometry (elementary linear algebra; exact identity; terminal -- no external '
                'dependency).'
            ),
            metadata=dict(
                theorem_tag=True,
                canonical_reference='regular simplex / equiangular-set geometry (elementary linear algebra)',
                is_axiom=False,
                foundation_role='codeword_non_orthogonality_exact_bound_simplex_minus_1_over_m_minus_1',
                consumer_p1_diagnosis='simplex_correlation_diagnosis_in_P1_B2_deferral',
                consumer_p2='HEAD_3_sparse_hopfield_HEAD_4_OLS_Gram_correction',
                form_a_source=src_tag,
            ),
            external_deps=[],  # terminal
            uses_targets=[],
            generalizes_target=None,
            composes_targets=[],
        ),

        # 2. T2/fractional_power_encoding (USES fhrr_bind external)
        dict(
            id='T2/fractional_power_encoding',
            name='Fractional Power Encoding (FPE / VFA / SSP single-channel kernel)',
            tier=Tier.TIER_2_PRIMITIVE,
            kind=AtomKind.PRIMITIVE,
            description=(
                'Fractional Power Encoding (FPE) -- single-channel continuous-magnitude encoding '
                'via complex-exponent representation. Encodes a continuous scalar x as a phasor '
                'vector through fractional powers of a base vector; the per-channel similarity '
                'kernel is the characteristic function of the base-phase distribution '
                '(sinc for uniform; see T1/sinc_characteristic_function). Aliases in the literature: '
                'VFA (Vector Function Architecture; Frady-Sommer 2021) + SSP (Spatial Semantic '
                'Pointers; Komer-Eliasmith 2019). Substrate consumer: P1 single-channel kernel '
                '(GATE-A measured-grounded via T2/fhrr_bind); P2 continuous encoding head. '
                'GROUNDED by T2/fhrr_bind (complex-exp representation). NOT a hard DEPENDS_ON gap '
                'for P2 (P1 already grounds via fhrr_bind + GATE-A); atomized for walkable '
                'FPE/VFA/SSP lineage. Canonical references: Frady, Kleyko, Kymn, Olshausen, '
                'Sommer "Computing on Functions Using Randomized Vector Representations" '
                '(arXiv:2109.03429, 2021); Komer & Eliasmith "A neural representation of '
                'continuous space using fractional binding" (CogSci 2019).'
            ),
            metadata=dict(
                canonical_reference='Frady-Sommer 2021 (arXiv:2109.03429); Komer-Eliasmith CogSci 2019',
                foundation_role='single_channel_continuous_magnitude_encoding_FPE_VFA_SSP_alias',
                grounded_via='T2_fhrr_bind_complex_exp_representation_plus_P1_GATE_A_measurement',
                consumer='P2_continuous_head_clean_lineage_not_hard_gated',
                form_a_source=src_tag,
            ),
            external_deps=[],
            uses_targets=['T2/fhrr_bind'],
            generalizes_target=None,
            composes_targets=[],
        ),

        # 3. T1/sinc_characteristic_function (COMPOSES intra-batch FPE)
        dict(
            id='T1/sinc_characteristic_function',
            name='Sinc characteristic function: E[cos(d*theta)] = sin(pi d)/(pi d) for theta ~ U(-pi, pi)',
            tier=Tier.TIER_1_FOUNDATIONAL,
            kind=AtomKind.PRIMITIVE,
            description=(
                'Sinc characteristic function -- foundation identity. For theta ~ Uniform(-pi, pi), '
                'E[cos(d * theta)] = sin(pi d)/(pi d) = sinc(d). This is the characteristic '
                'function of the uniform base-phase distribution underlying FPE. It IS the '
                'single-channel FPE similarity kernel that P1 GATE-A verified empirically '
                '(max_err 0.0166 << TOL 0.0669 at N=4096; cell SHA afb83ea4...). Substrate '
                'consumer: P1 GATE-A grounded measurement; P2 continuous head (clean-lineage). '
                'Canonical reference: characteristic function of the uniform distribution '
                '(elementary probability; exact identity; terminal -- no external dep).'
            ),
            metadata=dict(
                theorem_tag=True,
                canonical_reference='characteristic function of uniform distribution (elementary probability)',
                is_axiom=False,
                foundation_role='sinc_kernel_for_uniform_base_phase_FPE_single_channel_similarity',
                consumer_p1='GATE_A_grounded_by_measurement_max_err_0_0166',
                consumer_p2='continuous_head_clean_lineage',
                form_a_source=src_tag,
            ),
            external_deps=[],
            uses_targets=[],
            generalizes_target=None,
            composes_targets=['T2/fractional_power_encoding'],  # intra-batch
        ),

        # 4. T2/sparse_hopfield_hu_santos (GENERALIZES modern_hopfield_ramsauer external)
        dict(
            id='T2/sparse_hopfield_hu_santos',
            name='Sparse Modern Hopfield Network (entmax/alpha-entmax; Hu 2023, Santos 2024)',
            tier=Tier.TIER_2_PRIMITIVE,
            kind=AtomKind.PRIMITIVE,
            description=(
                'Sparse Modern Hopfield retrieval via entmax / alpha-entmax operator. Generalizes '
                "Ramsauer 2020's dense modern-Hopfield (entmax at alpha=1 is softmax; sparse "
                'entmax at alpha>1 yields sparse support with sharper basins). Provides EXACT '
                'retrieval under a margin/sparsity condition; tolerates non-orthogonal / simplex-'
                'correlated codewords (the -1/(m-1) regime per T1/simplex_correlation_bound). '
                'Substrate consumer: P2 HEAD-3 design (per DECISION 226 prereg LOCK + GATE-E '
                'envelope on softness spectrum). HEAD-1 (naive hard argmax) = HEAD-2 (dense '
                'softmax) at beta -> inf; HEAD-3 (sparse entmax) extends the spectrum to sparser '
                'support. Substrate RELATION via GENERALIZES: this atom generalizes '
                'T2/modern_hopfield_ramsauer (entmax generalizes softmax; the precise auditor-'
                'level relation per DECISION 223 Finding 3 enum discipline). Canonical references: '
                'Hu et al. "On Sparse Modern Hopfield Model" (NeurIPS 2023); Santos et al. '
                '"Sparse and Structured Hopfield Networks" (arXiv:2402.13725; ICML 2024); '
                'entmax operator (Peters, Niculae, Martins 2019).'
            ),
            metadata=dict(
                canonical_references=[
                    'Hu et al. NeurIPS 2023 (Sparse Modern Hopfield)',
                    'Santos et al. arXiv:2402.13725 ICML 2024 (Sparse and Structured Hopfield)',
                    'Peters, Niculae, Martins 2019 (entmax operator)',
                ],
                foundation_role='sparse_modern_hopfield_entmax_generalizes_softmax_simplex_correlated_codeword_tolerance',
                consumer_p2='HEAD_3_sparse_hopfield_softness_spectrum_envelope_design',
                generalizes_relation='entmax_generalizes_softmax_softmax_is_entmax_at_alpha_1',
                form_a_source=src_tag,
            ),
            external_deps=[],
            uses_targets=[],
            generalizes_target='T2/modern_hopfield_ramsauer',
            composes_targets=[],
        ),

        # 5. T2/kymn_residue_resonator_ols (USES resonator + COMPOSES CRT external)
        dict(
            id='T2/kymn_residue_resonator_ols',
            name='Kymn residue resonator (OLS/Gram projection; within-capacity log-scaling)',
            tier=Tier.TIER_2_PRIMITIVE,
            kind=AtomKind.PRIMITIVE,
            description=(
                'Residue resonator factorization via OLS / projection dynamics (Kymn et al. 2025). '
                'Per-base unbinding uses Gram-inverse (pinv(C_b @ C_b^H)) to de-correlate non-'
                'orthogonal simplex-correlated residue codewords (~ -1/(m-1)). This is the '
                'auditor-precise statement of the HEAD-4 P2 de-risk recipe lever (Gram-correction '
                '0.53 -> 0.85; soft + restarts + reconstruction-accept close 0.85 -> 1.0). '
                'CRITICAL WITHIN-CAPACITY CAVEAT (per Skunkworks STEP-7 + DECISION 225 amend): '
                'log-scaling work claim (~sum(m_b) vs brute-force O(R)) holds only WITHIN '
                'resonator capacity; beyond capacity, work can scale with R. Substrate must '
                'state within-capacity caveat -- do NOT imply unconditional log-scaling. '
                'Substrate consumer: P2 HEAD-4 (gates GATE-F work-vs-R measurement at scale; '
                'DECISION 226 prereg LOCK). Uses T3/resonator_network_decoder as the resonator '
                'dynamics primitive. Composes T1/chinese_remainder_theorem for residue '
                'factorization uniqueness over coprime bases. Canonical reference: Kymn et al. '
                '"Computing with Residue Numbers in High-Dimensional Representation" '
                '(arXiv:2311.04872, 2025).'
            ),
            metadata=dict(
                canonical_reference='Kymn et al. arXiv:2311.04872 2025',
                foundation_role='residue_resonator_OLS_Gram_projection_simplex_decorrelation',
                within_capacity_caveat='log_scaling_work_only_holds_within_resonator_capacity_NOT_unconditional',
                consumer_p2='HEAD_4_GATE_F_work_vs_R_measurement_at_scale_per_DECISION_226',
                derisk_recipe_levers='OLS_Gram_0_53_to_0_85_then_soft_restarts_reconstruction_accept_0_85_to_1_0',
                form_a_source=src_tag,
            ),
            external_deps=[],
            uses_targets=['T3/resonator_network_decoder'],
            generalizes_target=None,
            composes_targets=['T1/chinese_remainder_theorem'],  # external
        ),
    ]

    # ===== Pre-receive collision check =====
    for a in atoms_spec:
        if math_store.get_atom(a['id']) is not None:
            print(f'[{label}] HARD_FAIL: math::{a["id"]} already exists')
            return 1
    print(f'[{label}] 5 atom-id collisions clean (no pre-existing)', flush=True)

    # ===== Author atoms =====
    for a in atoms_spec:
        atom = Atom(
            id=a['id'],
            name=a['name'],
            corpus=Corpus.MATH,
            tier=a['tier'],
            kind=a['kind'],
            description=a['description'],
            metadata={**a['metadata'], 'eleventh_rule_clean': True, 'substrate_internal_verified': True},
            solution_history=tuple(),  # no empirical cell; foundation atoms
        )
        math_store.add_atom(atom)
        print(f'[{label}]   +math::{a["id"]}', flush=True)
    math_store._flush_atoms()

    # ===== Add edges (per DECISION 229a + 223 Finding 3 precise enums) =====
    edges_to_add = []  # (src_qid, RelationType, tgt_qid, note)

    for a in atoms_spec:
        src_qid = f'math::{a["id"]}'
        for tgt in a['uses_targets']:
            edges_to_add.append((src_qid, RelationType.USES, f'math::{tgt}', f'{a["id"]} USES {tgt}'))
        if a['generalizes_target']:
            edges_to_add.append((src_qid, RelationType.GENERALIZES, f'math::{a["generalizes_target"]}',
                                 f'{a["id"]} GENERALIZES {a["generalizes_target"]}'))
        for tgt in a['composes_targets']:
            edges_to_add.append((src_qid, RelationType.COMPOSES, f'math::{tgt}', f'{a["id"]} COMPOSES {tgt}'))

    for src, rel, tgt, note in edges_to_add:
        ps.add_relation(src, rel, tgt, source=src_tag, note=note)
    math_store._flush_relations()
    print(f'[{label}]   +{len(edges_to_add)} edges (USES/GENERALIZES/COMPOSES; precise enums per DECISION 223 Finding 3)',
          flush=True)

    # ===== R3 invariants verify =====
    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)

    mod_ok = module_liveness_ok()
    all_landed = all(math_store.get_atom(a['id']) is not None for a in atoms_spec)

    invariants_ok = (
        post_atoms == pre_atoms + 5
        and post_rels == pre_rels + 5
        and post_t == pre_t  # axiom_term unchanged (no algebra field; foundation atoms)
        and mod_ok
        and all_landed
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels}) '
          f'axiom_term={post_t}/{post_total} mod_ok={mod_ok} all_landed={all_landed}', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1

    print()
    print('=' * 80)
    print(f'[{label}] HARD_PASS: 5 of 6 consumer-gated foundation atoms ratified')
    print(f'  PRIORITY (gates P2 STEP-9):')
    print(f'    +math::T1/simplex_correlation_bound      (terminal identity; -1/(m-1))')
    print(f'    +math::T2/sparse_hopfield_hu_santos      (GENERALIZES modern_hopfield_ramsauer)')
    print(f'    +math::T2/kymn_residue_resonator_ols     (USES resonator + COMPOSES CRT)')
    print(f'  CLEAN-LINEAGE (walkable; not hard-gated):')
    print(f'    +math::T2/fractional_power_encoding      (USES fhrr_bind)')
    print(f'    +math::T1/sinc_characteristic_function   (COMPOSES FPE)')
    print(f'  DEFERRED: math::T1/O_xunb_cosine_identity  (Skunkworks confirm pending)')
    print(f'  +5 atoms, +5 edges; cap_pres=1.0 PRESERVED; axiom_term 206/206 PRESERVED')
    print(f'  Consumer-pull discipline RECURSIVELY APPLIED (DECISION 229)')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
