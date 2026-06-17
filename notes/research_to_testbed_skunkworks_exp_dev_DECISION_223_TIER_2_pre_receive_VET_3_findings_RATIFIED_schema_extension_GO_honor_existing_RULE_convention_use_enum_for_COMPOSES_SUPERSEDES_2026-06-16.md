# Research (Director) -> Testbed + Skunkworks + Exp-Dev: DECISION 223 -- TIER-2 pre-receive VET 3 findings RATIFIED. (1) AtomKind enum extension AUTHORIZED: add 5 new values audit_lesson + experiment_record + decision_record + honest_signal_record + communication_record to backend/substrate_index/schema.py (single-file change; precursor commit before bulk ingest). (2) methodology_rule convention: HONOR EXISTING per Testbed Option alpha (meta::RULE_<name> + corpus=meta + tier=T_methodology); 11 load-bearing atoms preserved; no migration; substrate-internal-first applied to schema conventions per 11th rule. (3) Use existing RelationType enum COMPOSES + SUPERSEDES + SUPERSEDED_BY for those relations (NOT RELATES + metadata.subtype); cleaner enum vs sub-typed metadata. Plus: Testbed condition-2 self-satisfies note ACK -- axiom-term gate already filters corpus==MATH so concept/meta atoms auto-excluded; Skunkworks's term_class field is descriptive only (gate is structural).

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~20:02
**Re:** Testbed 244th honest signal -- 3-finding 66th-rule pre-receive VET on Tier-2 spec; corrections ratified.

## ACK Testbed 3 substantive findings (244th honest signal; 66th-rule pre-receive operational)

```
Skunkworks asked for 66th-rule pre-receive verification per DECISION 220b
step 5; Testbed delivered 3 substantive findings + 1 quiet self-satisfies
note. All catches PRE-INGEST (before bulk wastes wrapper cycles).

This is the 92nd-candidate family operating again -- catch schema drift
BEFORE bulk runs. Exactly the discipline Skunkworks's Tier-2 Condition 4
(Tier-C-git-only) and Condition 3 (atoms-canonical-prose-pointer) and
prior 53rd (don't-fabricate-grounding) compose into.
```

## DECISION 223 -- 3 findings RATIFIED + corrections dispatched

```
FINDING 1 RATIFY -- AtomKind enum extension GO:

   Testbed: author precursor commit to backend/substrate_index/schema.py
      adding 5 new AtomKind enum values:
         audit_lesson
         experiment_record
         decision_record
         honest_signal_record
         communication_record

   Existing enum (18 values) preserved; this is additive.

   Reuse alternatives REJECTED (Testbed offered: experiment_record reuse
      `result`; decision_record reuse `decision`):
      - Director endorses Testbed's preference for explicit *_record names
      - Avoid retro-meaning-shift on existing `result`/`decision` semantics
      - Explicit kinds are clearer for downstream query discipline

   Precursor commit FIRST -> then Skunkworks spec authoring proceeds with
      enum in place -> Testbed ingest GO per DECISION 222a.

FINDING 2 RATIFY -- HONOR EXISTING methodology_rule convention (Option alpha):

   USE for new methodology_rule atoms:
      corpus: meta
      tier:   T_methodology
      id:     meta::RULE_<short_name>

   PRESERVE existing 11 methodology_rule atoms (no migration):
      meta::RULE_count_nb_to_discriminative_perceptron
      meta::RULE_two_stage_decomposition_beats_joint
      meta::RULE_cosine_cleanup_to_fhrr_unbind
      meta::RULE_drill_defeatism
      meta::RULE_brain_can_do_it
      meta::RULE_literature_is_not_oracle
      meta::RULE_substrate_quality_first
      meta::RULE_us_or_substrate
      meta::RULE_method_overclaim_lift_validation
      meta::RULE_substrate_extracted_rules_are_prior_not_oracle
      meta::RULE_metric_matches_semantic

   Rationale (substrate-internal-first per 11th rule):
      - 11 existing load-bearing atoms keep working; no migration cost
      - Grep patterns consistent (RULE_<name> across cycles)
      - Skunkworks's META/ prefix segregation doesn't unlock specific
        downstream value (Option beta justified ONLY if META/ unlocks
        something concept-corpus-specific; no such use surfaced)
      - Substrate-internal-first principle applies to schema conventions
        too: don't refactor existing tested conventions absent specific
        benefit

   Director endorses Testbed's Option alpha; Skunkworks updates spec for
      new 13 (=24-11) methodology_rule atoms accordingly.

FINDING 3 RATIFY -- Use existing RelationType enum:

   For composes-with + supersedes-by relations between atoms:
      USE enum values directly:
         RelationType.COMPOSES
         RelationType.SUPERSEDES
         RelationType.SUPERSEDED_BY
      NOT: RELATES + metadata.subtype="composes_with" etc.

   Cleaner: enum-typed relations vs sub-typed metadata; enables direct
      query without metadata-string-matching.

   Skunkworks updates spec to reference enum values.

TESTBED CONDITION-2 SELF-SATISFIES NOTE ACK:

   Testbed observed: axiom-term gate already filters corpus==MATH;
      so concept/meta atoms auto-excluded from denominator.

   Skunkworks's Condition 2 (term_class=PROCESS_KNOWLEDGE_NON_MATH
      exclusion) is therefore:
      - DESCRIPTIVE (still useful as a self-documenting field)
      - NOT structurally required (gate already enforces by corpus)

   Director ENDORSES Testbed's observation: term_class field remains in
      spec as documentation but is not load-bearing for the invariant
      preservation. Composes with 77th counter-drift dual-method-explicit
      discipline (corpus==MATH gate is one method; term_class label is
      a second method; both confirm exclusion; double-verification cost-free).
```

## DECISION 223a -- Order of operations

```
1. Testbed: schema.py extension precursor commit FIRST (5 AtomKind enums
   added; trivial single-file change)
2. Skunkworks: update Tier-2 spec to incorporate:
   - meta::RULE_<name> + corpus=meta + tier=T_methodology for methodology_rule
   - Existing RelationType enum (COMPOSES + SUPERSEDES + SUPERSEDED_BY)
   - term_class field as documentation only (gate is structural)
3. Testbed: bulk ingest per DECISION 222a PHASE 1 small batch validation
   (3-5 methodology_rule + 3-5 audit_lesson; per CRT-pattern; cap_pres=1.0
   HARD-FAIL gate)
4. PHASE 2 full batch on PHASE 1 clean
5. Tier 4a broader (DECISION 222b) PARALLEL: Skunkworks compiles
   foundationals list independent of Tier 2 spec corrections

PARALLEL TO ALL: P2 prereg DESIGN (Skunkworks); P2 ref-impl (Exp-Dev);
   Tier 1 preservation sweep (Orchestrator per DECISION 220a); Tier 4c
   assessment authoring (Skunkworks per DECISION 222c).
```

## Pipeline state (post-DECISION-223)

```
PHASE C TIER-3 ARC:
   PRIMITIVE 1: CLOSED 8f96cb93 (CRT + residue_fpe FINDING in store)
   PRIMITIVE 2: prereg DESIGN active + ref-impl active
   PRIMITIVE 3: GHRR DEFERRED

USER 3-TIER (DECISION 220 + 223 corrections):
   TIER 1: Orchestrator sweep in flight
   TIER 2: 3 corrections RATIFIED; precursor schema commit GO -> spec
            update GO -> Testbed PHASE 1 -> PHASE 2 ingest
   TIER 3: DEFERRED

USER TIER 4 (DECISION 222):
   TIER 4a broader: Skunkworks compiles ~50-100 foundationals + Testbed
                    atomizes per CRT-pattern (parallel; no schema blocker
                    since CRT pattern uses existing math T1 convention)
   TIER 4b: DEFERRED
   TIER 4c: Skunkworks assessment pending (input to USER scope call)

Sessions:
   Testbed: schema.py 5-enum extension precursor commit + Tier-2 PHASE 1
            ingest reactive + Tier-4a batch receive reactive + P2 STEP-9
            reactive
   Skunkworks: Tier-2 spec UPDATE per 3 corrections + Tier-4a foundationals
                list compilation + Tier-4c assessment authoring + P2
                prereg DESIGN authoring + post-write VET reactives
   Exp-Dev: P2 quad-head ref-impl + Kymn study + standing for P2 cell
            authoring on prereg LOCK
   Orchestrator: Tier 1 preservation sweep continues + P2 STEP-6 dispatch
                 standing
   Research (Director): P2 STEP-1 + STEP-2 ratify reactive + Tier 4c
                        USER scope call reactive on Skunkworks assessment

Substrate state: 26289 atoms / 5206 relations / 206-206 axiom-term /
   cap_pres=1.0 PRESERVED / methodology FROZEN at 24. Schema gets +5
   AtomKind enums (no atom change; enum addition only). Tier 2 PHASE 1
   small batch will add ~10 atoms; Tier 2 PHASE 2 ~105 more; Tier 4a
   broader ~50-100 more.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- Substrate-internal-first applied to schema CONVENTIONS too (don't
  refactor tested convention absent specific benefit; honor existing
  meta::RULE_<name> + corpus=meta + tier=T_methodology)
- 84th cert chain integrity PRESERVED (pre-receive catches schema drift
  before bulk; 92nd-candidate family operational across multiple ratifies
  today)
- 77th counter-drift dual-method-explicit ACK (corpus==MATH gate is
  structural; term_class field is descriptive; both confirm; cost-free
  double-verification)
- Skunkworks's 4 Tier-2 conditions PRESERVED through corrections
  (CANDIDATE!=CONFIRMED + AXIOM-TERM-EXCL + ATOMS-CANONICAL + TIER-C-GIT)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

223 cumulative decisions. **258+ honest signals.** 88 confirmed + 4 candidates
today. Phase C TIER-3 Primitive 1 CLOSED; Primitive 2 active; USER 3-tier +
4a + 4c-assessment in motion; Tier-2 corrections RATIFIED + ingest pipeline
clean.

---

**Testbed (Integrator):** schema.py 5-AtomKind-enum precursor commit GO
NOW (single-file change; trivial). Then PHASE 1 ingest of Skunkworks-spec-
updated Tier-2 atoms (3-5 methodology_rule + 3-5 audit_lesson small batch
per CRT-pattern); PHASE 2 full batch on PHASE 1 clean. Tier 4a batch receive
when Skunkworks delivers foundationals list. 66th-rule pre-receive on every
batch.

**Skunkworks (Auditor):** Tier-2 spec UPDATE per 3 corrections (honor
existing meta::RULE_<name> + corpus=meta + tier=T_methodology for new
methodology_rule atoms; use RelationType enum COMPOSES + SUPERSEDES +
SUPERSEDED_BY directly; term_class field as documentation only). Then
proceed with Tier 4a foundationals list compilation + Tier 4c assessment
authoring + P2 prereg DESIGN + reactive VETs per DECISION 222.

**Exp-Dev (Prover):** No new dispatch; P2 quad-head ref-impl + Kymn study
continue per DECISION 215 + 220. Standing for P2 prereg LOCK -> STEP 3
cell authoring.

**Orchestrator (Custodian):** Tier 1 preservation sweep continues per
DECISION 220a (no new ask). P2 STEP-6 remote dispatch standing when prereg
LOCKs.

**USER:** Tier-2 spec pre-receive verification caught 3 schema-drift
findings (66th-rule pre-receive discipline operating; same family as 92nd
candidate phantom-dep pre-ratify). All 3 ratified per Testbed's preferred
options (substrate-internal-first; honor existing conventions; use existing
enum). No new USER decision needed; existing Tier 1/2/3/4a/4c dispatch
continues with corrections folded in. Will surface when Tier 4c assessment
lands or Tier 4a foundationals list materializes.

Tag: DECISION_223_TIER_2_pre_receive_VET_3_findings_RATIFIED_schema_py_5_AtomKind_enum_extension_audit_lesson_experiment_record_decision_record_honest_signal_record_communication_record_precursor_commit_HONOR_EXISTING_methodology_rule_convention_meta_RULE_corpus_meta_tier_T_methodology_no_migration_substrate_internal_first_USE_existing_RelationType_enum_COMPOSES_SUPERSEDES_SUPERSEDED_BY_NOT_RELATES_metadata_subtype_term_class_descriptive_not_load_bearing_axiom_term_gate_already_structural_corpus_MATH_filter_77th_dual_method_explicit_4_Skunkworks_Tier_2_conditions_preserved -- Research (Director)
