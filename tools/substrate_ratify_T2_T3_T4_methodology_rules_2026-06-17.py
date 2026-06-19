"""Ratify 7 METHODOLOGY_RULE atoms per Director sweep 18:22 USER substrate-build call.

USER directive: "can't skunkworks and testbed be working on the substrate itself?"
Director ACK: substrate-build > process; atomize the discipline into Store-ratified atoms.

T2 (3 atoms): WordNet methodology rules (LEXICON kind + per-synset + LIMITED bears_on)
T3 (1 atom):  13th-rule backstop-to-backstop cadence canonical
T4 (3 atoms): invariant-verify methodologies (C1 + Action A + WordNet)

All atoms: corpus=META, tier=TIER_METHODOLOGY, kind=METHODOLOGY_RULE; structurally
non-load-bearing (no algebra); DECISION 236 atomize-by-NAME with rule_scheme +
rule_number_provenance metadata.

Per per-atom HARD-FAIL gate discipline.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


METHODOLOGY_RULES = [
    # T2 -- WordNet methodology rules (3)
    {
        'slug': 'wordnet_atoms_use_LEXICON_kind_not_research_finding',
        'name': 'Methodology rule (atomization): WordNet synsets use LEXICON kind not RESEARCH_FINDING',
        'description': (
            "WordNet synsets atomize as LEXICON AtomKind (existing 18-count enum slot designed for this) NOT "
            "RESEARCH_FINDING. Reasoning (verify-the-referent at AtomKind semantic intent): synsets are LEXICAL "
            "PRIMITIVES (sense-cluster definitional units), NOT FINDINGS. Miller 1995 / Fellbaum 1998 are "
            "MOTIVATING CITATIONS for the resource itself, not citations OF findings. RESEARCH_FINDING T2_RESEARCH_"
            "SUPPORTED would imply 'literature-supported finding' which a synset is NOT. Both structurally "
            "exclude algebra (cap_pres + axiom_term safe; non-load-bearing); both surface via bge-index. "
            "Distinguishing factor preserves trust-tier T0-T3 clean semantics: LEXICAL substrate (vocabulary) vs "
            "RESEARCH substrate (literature-supported reasoning). Per DECISION 236 atomize-by-NAME."
        ),
        'rule_scheme': 'METHODOLOGY_ATOMIZATION',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': 'cited as WordNet methodology rule per Director sweep 18:22 USER substrate-build call; Testbed cert-discipline input ratified',
    },
    {
        'slug': 'wordnet_atom_granularity_per_synset_not_per_word',
        'name': 'Methodology rule (atomization): WordNet per-synset granularity not per-word',
        'description': (
            "WordNet atoms use PER-SYNSET granularity (canonical semantic unit; synset_offset id like n.02834778) "
            "NOT per-word. Reasoning (verify-the-referent + scaling discipline): the synset IS the semantic unit "
            "(sense-cluster of synonymous words); individual words are polysemic (many words map to multiple "
            "synsets); per-synset matches WordNet canonical data model. Per-word would over-count (~155k unique "
            "words vs ~117k synsets) AND collapse polysemic distinction (loss of sense disambiguation). "
            "Member-words carried as METADATA FIELD (member_words: list-of-str) on each synset atom -- not as "
            "sub-atoms (avoids atom explosion). Aligns with Director's 'start-small top-5k high-frequency noun "
            "synsets' phrasing. Per DECISION 236 atomize-by-NAME."
        ),
        'rule_scheme': 'METHODOLOGY_ATOMIZATION',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': 'cited as WordNet methodology rule per Director sweep 18:22 USER substrate-build call; Testbed cert-discipline input ratified',
    },
    {
        'slug': 'wordnet_bears_on_LIMITED_math_only_internal_relations_metadata',
        'name': 'Methodology rule (atomization): WordNet bears_on LIMITED to math:: explicit; internal relations metadata',
        'description': (
            "WordNet atoms emit bears_on edges to math:: ONLY when synset has explicit mathematical content "
            "(rare for top-5k high-frequency nouns; ~0-10% of atoms). WordNet-INTERNAL relations "
            "(hypernym/hyponym/synonym/meronym) carried as METADATA FIELDS on each synset atom (hypernyms: "
            "list, hyponyms: list, synonyms: list, definition: str) -- NOT as bears_on edges. Reasoning "
            "(substrate-product positioning + DEGENERATE-REGIME at edge-scope avoidance): top-5k nouns are "
            "mostly non-mathematical; lexicon-structure edges add LITTLE to substrate capability (they describe "
            "vocabulary not problem-solving); 50k+ edges from internal relations would SWAMP cert-grade core "
            "(currently 7568 relations; 15x denser than STEP-B's 0.67 edges/atom; 7-8x relation growth). "
            "bge-index retrieves semantically related synsets via embedding similarity (no need for explicit "
            "hypernym edges). Scale to full 117k synsets = ~1.2M edges intractable; metadata-fields keep "
            "integrity-layer tractable. Per DECISION 236 atomize-by-NAME."
        ),
        'rule_scheme': 'METHODOLOGY_ATOMIZATION',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': 'cited as WordNet methodology rule per Director sweep 18:22 USER substrate-build call; Testbed cert-discipline input ratified',
    },
    # T3 -- 13th-rule backstop-to-backstop cadence
    {
        'slug': '13th_rule_backstop_to_backstop_manual_filesystem_cross_check_cadence',
        'name': 'Methodology rule (process): 13th-rule backstop-to-backstop manual filesystem cross-check cadence',
        'description': (
            "All sessions adopt periodic manual filesystem-cross-check as canonical backstop-to-backstop per "
            "Skunkworks's residual coverage caveat ('no monitor validates its own liveness; the ground-truth "
            "find does'). PROPOSED CANONICAL CADENCE: (1) PRIMARY every 30 minutes during active session work "
            "(find notes -maxdepth 1 -name '*.md' -newermt '30 minutes ago' | grep -iE '<SESSION>|to_all|_all_' "
            "| grep -viE '^<SESSION>_'; compare to monitor event log; surface gap as 19th-rule trigger). "
            "(2) SESSION-BOUNDARY at session start (post-compaction; 2h window) + session end (final check). "
            "(3) POST-LIVE-EVENT after any substrate-mutating event (verify no concurrent dispatches missed). "
            "Composes with canonical-v4 filesystem-watch (manual = 1st-order backstop independent of monitor; "
            "watch = LAYER-1 continuous polling; together = defense-in-depth validating watch's own liveness). "
            "Audit-discipline integration: any cross-check finding a gap = audit-discipline witness composing "
            "with monitor-must-watch-authoritative-source CANDIDATE. Per-session honor system + audit-discipline "
            "backstop. Zero implementation cost. Per VERIFY-THE-REFERENT meta-lens at monitoring-discipline layer."
        ),
        'rule_scheme': 'METHODOLOGY_PROCESS',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': 'cited as 13th-rule backstop-to-backstop cadence formalization per Director sweep 18:22 USER substrate-build call; Testbed proposal ratified; composes with USER-LOCKED 13th-rule active state-check',
    },
    # T4 -- 3 invariant-verify methodologies
    {
        'slug': 'C1_cell_author_chain_invariant_verify_methodology_baseline_snapshot_pattern',
        'name': 'Methodology rule (verify): C1 cell-author chain invariant-verify baseline-snapshot pattern',
        'description': (
            "Testbed invariant-verify methodology for substrate-mutating EXPERIMENT_RECORD atomization events "
            "(mirror ARCH-A/B pattern). Procedure: (1) Capture pre-trigger baseline snapshot (atoms, relations, "
            "axiom_term, cap_pres, dup_qids, phantom edges, AtomKind distribution) when cell-author signals "
            "smoke-complete or FULL-queued. (2) On event signal, delta-compare: +1 atom (the EXP_ atom); "
            "axiom_term unchanged; cap_pres unchanged; dup_qids 0; phantoms 0 new; verdict matches pre-registered "
            "band per cert-owner; provenance_quality CERT_CHAIN_GRADE (5-seed full); relevance_tier matches "
            "disposition. (3) WITNESS PASS or HARD_FAIL with specific surface. Composes with verify-the-referent "
            "discipline at atom-level (the atom claimed to land actually IS what's verified). Runs in <30s. "
            "Reactive on cell-author dispatch arrival."
        ),
        'rule_scheme': 'METHODOLOGY_VERIFY',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': 'cited as C1 cell-author chain invariant-verify methodology per Director sweep 18:22 USER substrate-build call; Testbed PRE-STAGE 3-pre-stage methodology atomized to Store',
    },
    {
        'slug': 'Action_A_bge_cache_lands_joint_coverage_VET_named_cert_gate',
        'name': 'Methodology rule (verify): Action A bge-cache-lands joint coverage-VET named cert-gate',
        'description': (
            "Joint named cert-gate at bge-index-refresh cache-land event (cached_indices/bge_large_v2_name_*.npz). "
            "EVENT CLASS: CACHE-WRITE (out-of-Store); ZERO substrate mutation expected. JOINT cert-gate = "
            "Skunkworks (indexed == n_atoms current Store-authoritative count) + Testbed (zero atom/relation "
            "mutation + cap_pres 6/6 + axiom_term 206/206 + math_ops_with_cbs unchanged + dup_qids 0 + new "
            "phantoms 0 + cache file exists at cached_indices/ path + cache filename token matches Store count). "
            "DYNAMIC count handling: delta-compare at event time against current Store-authoritative count, not "
            "fixed pre-cached target (handles race with concurrent ratifies during encode window). PREEMPT-ABLE "
            "per preemption principle: if substrate-mutating event lands during cache-encode, capture fresh post-"
            "mutation baseline FIRST then proceed. Composes with verify-the-referent discipline (the cache I "
            "verify actually IS for the atom-count Store reports)."
        ),
        'rule_scheme': 'METHODOLOGY_VERIFY',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': 'cited as Action A cache-land joint coverage-VET methodology per Director sweep 18:22 USER substrate-build call; Director-named explicit cert-gate ratified to Store',
    },
    {
        'slug': 'STEP_B_WordNet_extension_invariant_verify_methodology_3_watch_items',
        'name': 'Methodology rule (verify): STEP-B WordNet extension invariant-verify 3 watch-items',
        'description': (
            "Testbed invariant-verify methodology for STEP-B language-knowledge extension APPLY (LEXICON atom "
            "batch from WordNet 3.1 top-5k high-frequency noun synsets). Baseline-snapshot pattern mirroring "
            "STEP-B Option A. Expected deltas (5000-atom initial): +5000 LEXICON atoms; +0-500 bears_on math:: "
            "edges (LIMITED scope per RULE_wordnet_bears_on_LIMITED_math_only); axiom_term 206/206 PRESERVED "
            "(structural guard for LEXICON kind); cap_pres 6/6 PRESERVED; dup_qids 0; phantoms NEW concept::"
            "WordNet/* cross-namespace LEGITIMATE target-resolved (distinct from pre-existing element-layer-"
            "scoping). 3 WATCH-ITEMS: (1) cross-namespace edges LEGITIMATE not phantoms (target-resolved token-"
            "set; distinct prefix scheme); (2) structural-guard EMPIRICAL (no algebra on LEXICON; axiom_term "
            "unchanged; cap_pres unchanged; current_best_solution unchanged for math operators); (3) T2 citation "
            "discipline (each LEXICON atom metadata.citations carries Miller 1995 and/or Fellbaum 1998 per "
            "trust-tier; member_words + hypernyms + hyponyms + definition as metadata fields per LIMITED bears_on "
            "rule). Composes with verify-the-referent at lexicon-kind layer."
        ),
        'rule_scheme': 'METHODOLOGY_VERIFY',
        'rule_class': 'SUBSTRATE_DERIVED',
        'rule_number_provenance': 'cited as STEP-B WordNet extension invariant-verify methodology per Director sweep 18:22 USER substrate-build call; Testbed PRE-STAGE 3-pre-stage methodology atomized to Store',
    },
]


def module_liveness_ok() -> bool:
    import importlib
    return all(
        hasattr(importlib.import_module(m), s)
        for m, s in [
            ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
            ('hdlab.perceptron', 'StructuredPerceptron'),
            ('backend.substrate_index.sequence_labeler', 'NERTagger'),
            ('hdlab.bayesian_inference', 'EMMixture'),
            ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
            ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
        ]
    )


def axiom_term_count(ps: PartitionedStore) -> int:
    atoms = list(ps.all_atoms())
    return sum(
        1 for a in atoms
        if str(a.corpus.name) == 'MATH'
        and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
        and a.algebra and len(a.algebra) >= 3
        and 'oeis' not in str(a.id).lower()
        and not str(a.id).startswith('T3/wikidata_')
    )


def build_atom(spec: dict) -> Atom:
    slug = spec['slug']
    metadata = {
        'rule_scheme': spec['rule_scheme'],
        'rule_class': spec['rule_class'],
        'rule_number_provenance': spec['rule_number_provenance'],
        'frozen': True,
        'confirmed': True,
        'term_class': 'PROCESS_KNOWLEDGE_NON_MATH',
        'prose_source': 'testbed_substrate_build_T2_T3_T4_methodology_rules_per_director_sweep_18_22_USER_substrate_build_call_2026-06-17',
        'eleventh_rule_clean': True,
        'substrate_internal_verified': True,
        'source': 'T2_T3_T4_substrate_build_methodology_atomization_USER_substrate_build_call_director_sweep_18_22_testbed_cert_discipline_input_ratified_DECISION_236_atomize_by_NAME',
    }
    return Atom(
        id=f'RULE_{slug}',
        name=spec['name'],
        description=spec['description'],
        kind=AtomKind.METHODOLOGY_RULE,
        tier=Tier.TIER_METHODOLOGY,
        corpus=Corpus.META,
        algebra=None,
        metadata=metadata,
    )


def main() -> int:
    store_dir = Path('data/substrate_index')
    ps = PartitionedStore(store_dir)

    pre_n = sum(1 for _ in ps.all_atoms())
    pre_axiom = axiom_term_count(ps)
    pre_mod = module_liveness_ok()
    print(f'PRE-RATIFY: atoms={pre_n}  axiom_term={pre_axiom}/{pre_axiom}  cap_pres(mod6/6)={pre_mod}')

    if not pre_mod or pre_axiom != 206:
        print('PRE-RATIFY GATE FAIL.')
        return 1

    for spec in METHODOLOGY_RULES:
        atom = build_atom(spec)
        existing = {a.id for a in ps.all_atoms()}
        if atom.id in existing:
            print(f'  SKIP (already present): {atom.id}')
            continue
        ps.add_atom(atom, source='T2_T3_T4_substrate_build_methodology_rules', note=f"{spec['rule_scheme']} {spec['rule_class']}")
        post_n = sum(1 for _ in ps.all_atoms())
        post_axiom = axiom_term_count(ps)
        post_mod = module_liveness_ok()
        gate_ok = post_axiom == 206 and post_mod
        status = 'OK' if gate_ok else 'HARD_FAIL'
        print(f'  + {atom.id}')
        print(f'    atoms_now={post_n}  axiom_term={post_axiom}  cap_pres={post_mod}  -> {status}')
        if not gate_ok:
            print('  HARD_FAIL: halting.')
            return 2

    post_n = sum(1 for _ in ps.all_atoms())
    print('=' * 72)
    print(f'T2+T3+T4 METHODOLOGY ratify COMPLETE: +{post_n - pre_n} atoms')
    print(f'  axiom_term 206/206 PRESERVED  cap_pres 6/6 PRESERVED')
    print('=' * 72)
    return 0


if __name__ == '__main__':
    sys.exit(main())
