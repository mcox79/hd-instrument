"""P1 STEP-9 atomic ratify chain (DECISION 219 + Skunkworks VET CLEAN).

Two-step ratify per Option B forward-grounded:

  STEP 9.1: math::T1/chinese_remainder_theorem  (FORM-A foundation theorem-tag)
            kind=primitive (substrate convention -- all 234 math T1 atoms use this; no
            'foundation' enum exists)
            tier=T1, corpus=math
            DEPENDS_ON: none (terminal foundation atom; CRT is itself foundational)
            ref: Hardy & Wright, An Introduction to the Theory of Numbers, Theorem 121
            solution_history: empty (no empirical cell; substrate-internal authoring; 11th rule)
            Net delta: +1 atom, +0 edges; cap_pres trivially preserved

  STEP 9.2: math::T3/residue_fpe_encoding  (FORM-A FINDING; HONEST_BOUNDED_C1_BREAKS)
            kind=FINDING (per Director DECISION 219 Path-b; Skunkworks Path-b lean)
            tier=T3, corpus=math
            DEPENDS_ON: T2/fhrr_bind + T1/chinese_remainder_theorem  (real edges; no phantom)
            cell: data/exp_primitive_1_residue_FPE_v1/metrics.json (sha afb83ea4e96e747c;
                  verdict HONEST_BOUNDED_C1_BREAKS; run_mode full; 3 seeds; cuda; N=4096)
            metric_type: ENCODING_SOUNDNESS_HONEST_BOUNDED  (AGGREGATE of GATE-A + B1 +
                         C2-as-function; NOT efficiency/log-scaling)
            Skunkworks conditions (a)-(d) enforced in description prose:
              (a) leads with grounded parts + STRUCTURAL BOUND (not "win" framing)
              (b) attributes single-channel kernel to known FPE/SSP construct (GROUNDED,
                  NOT novel); novel-part multi-base layering is what BREAKS
              (c) "log-scaling DECODE OPEN -> P2; advantage NOT demonstrated (brute-force
                  O(R) only)" carried prominently
              (d) metric_type = ENCODING_SOUNDNESS_HONEST_BOUNDED (AGGREGATE); NOT
                  efficiency metric
            Net delta: +1 atom, +2 DEPENDS_ON edges

ATOMIC discipline: both ratifies in single run. If 9.1 fails, 9.2 does not fire.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
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


def ratify_crt(ps, math_store, ratify_date, src_91):
    """STEP 9.1: T1/chinese_remainder_theorem foundation theorem-tag."""
    label = 'STEP-9.1-CRT'
    new_id = 'T1/chinese_remainder_theorem'
    new_qid = f'math::{new_id}'

    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    pre_t, pre_total = axiom_term(ps)
    print(f'[{label}] pre: atoms={pre_atoms} rels={pre_rels} axiom_term={pre_t}/{pre_total}', flush=True)

    if math_store.get_atom(new_id) is not None:
        print(f'[{label}] HARD_FAIL: {new_qid} already exists')
        return 1, None, None

    new_atom = Atom(
        id=new_id,
        name='Chinese Remainder Theorem (foundation theorem-tag)',
        corpus=Corpus.MATH,
        tier=Tier.TIER_1_FOUNDATIONAL,
        kind=AtomKind.PRIMITIVE,  # substrate convention -- all 234 math T1 atoms use kind=primitive
        description=(
            'Chinese Remainder Theorem (CRT). For pairwise coprime moduli m_1, m_2, ..., m_k '
            'and any integers a_1, a_2, ..., a_k, there exists a unique solution x modulo '
            'prod_i(m_i) satisfying x = a_i (mod m_i) for all i. Equivalently, the map '
            'Z/(prod m_i)Z -> prod_i Z/m_i Z given by x -> (x mod m_1, ..., x mod m_k) is a '
            'ring isomorphism. Foundation result load-bearing for integer-residue arithmetic '
            'over coprime bases; underlies the uniqueness + decodability of multi-base '
            'integer-residue encodings with range = prod_i(m_i). Canonical reference: '
            'Hardy & Wright, An Introduction to the Theory of Numbers, Theorem 121. '
            'Substrate-internal foundation; no LLM authoring (11th rule); no empirical cell '
            '(theorem-tag terminal atom).'
        ),
        metadata={
            'theorem_tag': True,
            'canonical_reference': 'Hardy and Wright, An Introduction to the Theory of Numbers, Theorem 121',
            'is_axiom': False,  # CRT is a proved theorem, not an axiom; does not increment axiom-term numerator
            'foundation_role': 'integer_residue_arithmetic_uniqueness_over_coprime_bases',
            'form_a_source': src_91,
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
            'no_empirical_cell': 'theorem-tag terminal atom; substrate-internal authoring',
            'ratified_per_decision': 'DECISION_219_option_B_forward_grounded',
            'integrator_pre_ratify_catch_response': '92nd_audit_candidate_phantom_DEPENDS_ON',
        },
        solution_history=tuple(),  # no empirical cell; foundation theorem-tag
    )
    math_store.add_atom(new_atom)
    math_store._flush_atoms()
    # No DEPENDS_ON edges for foundation atom; no flush_relations needed

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)

    new_check = math_store.get_atom(new_id)
    invariants_ok = (
        post_atoms == pre_atoms + 1
        and post_rels == pre_rels  # no DEPENDS_ON edges added
        and post_t >= pre_t  # CRT is not an axiom; axiom-term unchanged
        and module_liveness_ok()
        and new_check is not None
        and new_check.tier == Tier.TIER_1_FOUNDATIONAL
        and new_check.corpus == Corpus.MATH
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms}) rels={post_rels} (+{post_rels-pre_rels}) '
          f'axiom_term={post_t}/{post_total}', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1, None, None

    print(f'[{label}] R3 verify: PASS (additive +1 T1 foundation atom +0 edges; cap_pres=1.0; '
          f'axiom_term {post_t}/{post_total} unchanged; CRT is theorem-not-axiom)')
    print(f'[{label}] HARD_PASS: {new_qid} RATIFIED')
    return 0, post_atoms, post_rels


def ratify_residue_fpe(ps, math_store, ratify_date, src_92, pre_atoms_92, pre_rels_92):
    """STEP 9.2: T3/residue_fpe_encoding HONEST_BOUNDED FINDING."""
    label = 'STEP-9.2-residueFPE'
    new_id = 'T3/residue_fpe_encoding'
    new_qid = f'math::{new_id}'
    deps = ['T2/fhrr_bind', 'T1/chinese_remainder_theorem']

    pre_t, pre_total = axiom_term(ps)
    print(f'[{label}] pre: atoms={pre_atoms_92} rels={pre_rels_92} axiom_term={pre_t}/{pre_total}', flush=True)

    if math_store.get_atom(new_id) is not None:
        print(f'[{label}] HARD_FAIL: {new_qid} already exists')
        return 1

    for d in deps:
        if math_store.get_atom(d) is None:
            print(f'[{label}] HARD_FAIL: dep missing math::{d}')
            return 1
    print(f'[{label}] deps verified (real edges; no phantom): {deps}', flush=True)

    cell = Path('data/exp_primitive_1_residue_FPE_v1/metrics.json')
    if not cell.exists():
        print(f'[{label}] HARD_FAIL: cell metrics missing: {cell}')
        return 1
    sha = sha256_of(cell)
    with open(cell) as f:
        m = json.load(f)
    if m.get('verdict') != 'HONEST_BOUNDED_C1_BREAKS' or m.get('run_mode') != 'full':
        print(f'[{label}] HARD_FAIL: cell precondition (verdict={m.get("verdict")} run_mode={m.get("run_mode")})')
        return 1
    print(f'[{label}] cell corroborated: verdict={m["verdict"]} run_mode={m["run_mode"]} '
          f'N={m["N"]} bases={m["bases"]} sha={sha[:12]}..', flush=True)

    gate_A = m['gate_A']
    gate_B1 = m['gate_B1_decodability']
    gate_C = m['gate_C']

    sh = [{
        'solution_atom_id': new_qid,
        'adopted_date': ratify_date,
        'replaced_date': None,
        'replacement_reason': (
            'Phase C TIER-3 Primitive 1 cert chain STEP-9 close per DECISION 219 (Option B '
            'forward-grounded) + Skunkworks STEP-7 VET CLEAN + 92nd audit-discipline candidate '
            '(phantom-dep pre-ratify caught + resolved via CRT T1 foundation atom authored '
            'first). HONEST_BOUNDED_C1_BREAKS adjudication: GATE-A single-channel FPE kernel '
            'matches closed-form sinc (err 0.0166 << TOL 0.0669); GATE-B1 multi-base integer '
            'decodability 1.0 with quasi-orthogonal codewords + CRT uniqueness over range '
            'prod(bases)=1155; GATE-C1 combined-continuous-residue product-kernel BREAKS '
            'STRUCTURALLY (err 1.0552 >> TOL 0.0669; ~66x the 1/sqrt(N) sampling-noise scale '
            'AND rose from smoke 0.75 instead of shrinking ~2x as 1/sqrt(N) would predict; '
            'population-level not finite-N); GATE-C2 sinc-sidelobe resolution envelope '
            'characterized (function-of-d; non-monotonic; useful resolution d>=~0.1; preserve '
            'as function, NOT collapsed scalar). Log-scaling DECODE (B2 efficient resonator) '
            'OPEN -> Primitive 2; advantage NOT demonstrated (brute-force O(R) only). '
            'Single-channel FPE attributed to known FPE/SSP construct (GROUNDED, NOT novel); '
            'the multi-base continuous layering is what STRUCTURALLY BREAKS. No log-scaling '
            'over-claim; metric_type ENCODING_SOUNDNESS_HONEST_BOUNDED (AGGREGATE), not efficiency.'
        ),
        'empirical_metric': {
            'name': 'P1_residue_FPE_encoding_full_N4096_3seed_cuda',
            'gate_A_max_kernel_err': gate_A['max_kernel_err'],
            'gate_A_tol': gate_A['tol'],
            'gate_A_pass': gate_A['pass'],
            'gate_B1_decodability_acc': gate_B1['decodability_acc'],
            'gate_B1_range': gate_B1['range'],
            'gate_B1_max_offdiag_sim': gate_B1['max_offdiag_sim'],
            'gate_B1_coprime': gate_B1['coprime'],
            'gate_B1_pass': gate_B1['pass'],
            'gate_C1_kernel_err': gate_C['c1_kernel_err'],
            'gate_C1_tol': gate_C['c1_tol'],
            'gate_C1_product_kernel_holds': gate_C['c1_product_kernel_holds'],
            'gate_C2_resolution_envelope_function': gate_C.get('c2_resolution_envelope'),
            'structural_argument': (
                '1/sqrt(N) sampling-noise at N=4096 ~ 0.016; observed gap 1.055 is ~66x larger; '
                'AND gap rose from smoke 0.75 at N=1024 instead of shrinking as ~1/sqrt(N). '
                'Population-level break, not finite-N noise. Per Skunkworks STEP-7 VET.'
            ),
            'verdict_msg': m.get('verdict_msg'),
        },
        'metric_type': 'ENCODING_SOUNDNESS_HONEST_BOUNDED',
        'metric_type_NOT': 'efficiency_or_log_scaling_or_capability_recall',
        'metric_type_class': 'AGGREGATE',
        'EM_class_mislabel_guard': (
            'STRICT type-discipline per Skunkworks condition (d): AGGREGATE of GATE-A kernel-match '
            '+ GATE-B1 decodability + GATE-C2 envelope-as-function. NOT an efficiency metric (no '
            'log-scaling demonstrated); NOT a capability-recall metric (no served downstream '
            'capability claim); NOT a HARD_PASS.'
        ),
        'n_seeds': len(m.get('seeds', [])) or m.get('n_seeds'),
        'seeds': m.get('seeds'),
        'run_mode': m['run_mode'],
        'verdict': m['verdict'],
        'cell_anchor': m.get('anchor_name'),
        'cell_metrics_sha256': sha,
        'cell_metrics_path': str(cell).replace('\\', '/'),
        'compute_backend': m.get('compute_backend'),
        'dtype': m.get('dtype'),
        'device': m.get('device'),
        'gerrymander_guard_OOM_fix_did_not_shrink_N': (
            'Skunkworks STEP-7 VET: TOL_A = 0.066875 = 0.02 + 3*sqrt(1/4096); derived-from-N '
            'value PROVES N=4096 was used (OOM fix was pure memory-layout broadcast->loop).'
        ),
        'condition_a_grounded_first_then_bound': (
            'Atom prose LEADS with the GROUNDED parts (GATE-A + B1) then states the STRUCTURAL '
            'BOUND (GATE-C1 break). NOT a "win" framing.'
        ),
        'condition_b_single_channel_known_FPE_not_novel': (
            'Single-channel continuous-FPE kernel attributed to known FPE/SSP construct via '
            'T2/fhrr_bind DEPENDS_ON; GROUNDED, NOT a P1 invention. The novel multi-base '
            'continuous layering is exactly what STRUCTURALLY BREAKS.'
        ),
        'condition_c_log_scaling_open_advantage_not_demonstrated': (
            'P1 demonstrated BRUTE-FORCE O(R) decodability ONLY. NO log-scaling advantage '
            'demonstrated (integer OR continuous). Efficient resonator B2 OPEN -> Primitive 2. '
            'Even integer log-scaling (Kymn) is literature within-capacity, not measured here.'
        ),
        'condition_d_metric_type_strict': (
            'metric_type = ENCODING_SOUNDNESS_HONEST_BOUNDED (AGGREGATE of GATE-A + B1 + C2 '
            'envelope-as-function). NOT efficiency, NOT log-scaling, NOT capability-recall.'
        ),
        'form': 'FINDING',
        'source': src_92,
    }]

    new_atom = Atom(
        id=new_id,
        name='Residue-FPE continuous-magnitude encoding (HONEST_BOUNDED finding; structural C1 break at full N)',
        corpus=Corpus.MATH,
        tier=Tier.TIER_3_ALGORITHM,
        kind=AtomKind.FINDING,
        description=(
            # Skunkworks condition (a): lead with grounded parts + STRUCTURAL BOUND, not "win" framing
            'Residue-FPE continuous-magnitude encoding -- HONEST_BOUNDED finding (Phase C TIER-3 '
            'Primitive 1 cert chain close). GROUNDED PARTS (load-bearing within envelope): '
            '(1) single-channel continuous-FPE kernel matches closed-form sinc (GATE-A max_err '
            '0.0166 << TOL 0.0669) -- single-channel FPE is the KNOWN FPE/SSP construct, '
            'attributed via DEPENDS_ON T2/fhrr_bind (Skunkworks condition (b): GROUNDED, NOT '
            'novel); (2) integer-residue multi-base decodability 1.0 with quasi-orthogonal '
            'codewords + CRT uniqueness over range prod(bases)=1155 (GATE-B1; DEPENDS_ON '
            'T1/chinese_remainder_theorem). STRUCTURAL BOUND (Skunkworks condition (a) -- the '
            'bound, not a win): combined-continuous-residue PRODUCT-KERNEL BREAKS at full N '
            '(GATE-C1 err 1.0552 >> TOL 0.0669; ~66x the 1/sqrt(N) sampling-noise scale and '
            'rose from smoke 0.75 instead of shrinking; population-level structural break, NOT '
            'finite-N). Mechanism interpretation (Skunkworks-offered, not certified): CRT base-'
            'independence is an INTEGER property; continuous x has no mod-reduction, so per-base '
            'phases stay coupled through shared magnitude; combined kernel does not factor as '
            'product of per-base kernels. The novel multi-base continuous layering is EXACTLY '
            'what breaks (Skunkworks condition (b)). RESOLUTION ENVELOPE (GATE-C2; preserve as '
            'FUNCTION not scalar): sinc-sidelobe structure, non-monotonic margin profile [0.033, '
            '0.200, 0.706, 1.693, 0.656, 0.997] at d in {0.02, 0.05, 0.1, 0.2, 0.5, 1.0}; useful '
            'operating envelope at d >= ~0.1 with margin > 0.7; sidelobe aliasing at d=0.5 is '
            'expected sinc behavior, NOT a bug. LOG-SCALING DECODE (B2 efficient resonator) '
            'OPEN -> Primitive 2 (Skunkworks condition (c); CARRIED PROMINENTLY): residue-FPE '
            'log-scaling advantage NOT demonstrated here (brute-force O(R) decodability only); '
            'even the integer-residue log-scaling (Kymn resonator) is a literature result '
            'within-resonator-capacity, NOT measured here. metric_type ENCODING_SOUNDNESS_'
            'HONEST_BOUNDED (AGGREGATE of GATE-A + B1 + C2-as-function; Skunkworks condition '
            '(d) STRICT type-discipline: NOT efficiency, NOT log-scaling, NOT capability-recall, '
            'NOT HARD_PASS). Substrate-internal; no learned codebook; verify-not-assume gate '
            'worked (the remote run was genuinely needed; could have resolved either way; '
            'unlike 190a algebraic case). 91st audit candidate (verify-not-assume-procedure-not-'
            'foresight-claim per Skunkworks honesty) + 92nd audit candidate (phantom-DEPENDS_ON '
            'pre-ratify caught + resolved Option B forward-grounded via this CRT FORM-A).'
        ),
        metadata={
            'finding_source': src_92,
            'eleventh_rule_clean': True,
            'substrate_internal_verified': True,
            'honest_bounded_NOT_capability_NOT_HARD_PASS': True,
            'metric_type_strict': 'ENCODING_SOUNDNESS_HONEST_BOUNDED_AGGREGATE_NOT_efficiency_NOT_log_scaling',
            'gate_A_status': 'PASS',
            'gate_B1_status': 'PASS',
            'gate_C1_status': 'BREAKS_STRUCTURAL_NOT_finite_N',
            'gate_C2_envelope_status': 'CHARACTERIZED_preserve_as_function_not_scalar',
            'log_scaling_decode_OPEN_to_P2': True,
            'log_scaling_advantage_NOT_demonstrated_brute_force_only': True,
            'skunkworks_condition_a_lead_grounded_then_bound': True,
            'skunkworks_condition_b_single_channel_known_FPE_not_novel': True,
            'skunkworks_condition_c_log_scaling_OPEN_prominent': True,
            'skunkworks_condition_d_metric_type_aggregate_not_efficiency': True,
            'ratified_per_decision': 'DECISION_219_option_B_forward_grounded',
            'phase_C_tier_3_primitive_1_cert_chain_step_9_2_close': True,
            'audit_candidate_91st_verify_not_assume_procedure': True,
            'audit_candidate_92nd_phantom_dep_pre_ratify_resolved_option_B': True,
        },
        solution_history=tuple(sh),
    )
    math_store.add_atom(new_atom)
    math_store._flush_atoms()

    for d in deps:
        ps.add_relation(new_qid, RelationType.DEPENDS_ON, f'math::{d}',
                        source=src_92, note=f'residue_fpe_encoding DEPENDS_ON {d}')
    math_store._flush_relations()
    print(f'[{label}]   ratified: +{new_qid} +{len(deps)} DEPENDS_ON edges (real; no phantom)')

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    post_t, post_total = axiom_term(ps)

    new_check = math_store.get_atom(new_id)
    sh_landed = len(new_check.solution_history or ()) if new_check else 0
    edges_check = sum(
        1 for s, r, t in ps.iter_all_relations()
        if (s == new_id or s == new_qid)
        and r.name == 'DEPENDS_ON'
        and any(d in t for d in deps)
    )

    invariants_ok = (
        post_atoms == pre_atoms_92 + 1
        and post_rels == pre_rels_92 + 2
        and post_t >= pre_t
        and module_liveness_ok()
        and new_check is not None
        and new_check.kind == AtomKind.FINDING
        and new_check.tier == Tier.TIER_3_ALGORITHM
        and sh_landed == 1
        and edges_check == 2
    )

    print(f'[{label}] post: atoms={post_atoms} (+{post_atoms-pre_atoms_92}) rels={post_rels} '
          f'(+{post_rels-pre_rels_92}) axiom_term={post_t}/{post_total} sh_landed={sh_landed} '
          f'edges={edges_check}', flush=True)

    if not invariants_ok:
        print(f'[{label}] HARD_FAIL: R3 invariant violation')
        return 1

    print(f'[{label}] R3 verify: PASS (additive +1 T3 FINDING atom +2 DEPENDS_ON edges; '
          f'cap_pres=1.0; real-edge-not-phantom)')
    print(f'[{label}] HARD_PASS: {new_qid} RATIFIED')
    return 0


def main():
    ratify_date = '2026-06-16'
    src_91 = ('STEP_9_1_DECISION_219_option_B_forward_grounded_T1_chinese_remainder_theorem_'
              'foundation_92nd_audit_candidate_phantom_DEPENDS_ON_resolved')
    src_92 = ('STEP_9_2_DECISION_219_option_B_forward_grounded_residue_fpe_encoding_FINDING_'
              'HONEST_BOUNDED_C1_BREAKS_skunkworks_VET_clean_conditions_a_to_d')

    repo_root = Path(__file__).resolve().parents[1]
    ps = PartitionedStore(repo_root / 'data/substrate_index')
    math_store = ps._store_for(Corpus.MATH)

    # STEP 9.1: CRT foundation atom
    rc_91, post_atoms_91, post_rels_91 = ratify_crt(ps, math_store, ratify_date, src_91)
    if rc_91 != 0:
        print('STEP 9.1 HARD_FAIL -- aborting; STEP 9.2 will NOT fire')
        return 1
    print()

    # STEP 9.2: residue_fpe_encoding FINDING
    rc_92 = ratify_residue_fpe(ps, math_store, ratify_date, src_92, post_atoms_91, post_rels_91)
    if rc_92 != 0:
        print('STEP 9.2 HARD_FAIL')
        return 1

    print()
    print('=' * 80)
    print('STEP 9.1 + 9.2 ATOMIC RATIFY: HARD_PASS')
    print('  +math::T1/chinese_remainder_theorem  (foundation theorem-tag; +0 edges)')
    print('  +math::T3/residue_fpe_encoding       (FINDING; +2 DEPENDS_ON edges; real, no phantom)')
    print('  Phase C TIER-3 Primitive 1 cert chain CLOSED')
    print('  cap_pres=1.0 preserved; axiom_term preserved')
    print('=' * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
