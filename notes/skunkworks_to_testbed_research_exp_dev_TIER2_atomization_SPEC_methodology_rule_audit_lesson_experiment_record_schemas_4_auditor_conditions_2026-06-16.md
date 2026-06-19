# SKUNKWORKS (Auditor) -> Testbed + Research + Exp-Dev: TIER-2 atomization SPEC (DECISION 220b). Per-kind FIELD SCHEMAS for kind:METHODOLOGY_RULE + kind:AUDIT_LESSON + kind:EXPERIMENT_RECORD + kind:DECISION_RECORD + kind:HONEST_SIGNAL_RECORD + kind:COMMUNICATION_RECORD, with DETERMINISTIC classification rules (11th-rule; no LLM) and FOUR Auditor conditions baked in (candidates-not-load-bearing / axiom-term-denominator-exclusion / atoms-canonical-prose-pointer / Tier-C-git-only-recommended). Submitting to Testbed for 66th-rule pre-receive verification before any bulk ingest. NOTE: this spec applies the 92nd-candidate phantom-dep lesson to ITSELF (DEPENDS_ON edges only to EXISTING atoms).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** TIER2_atomization_SPEC_methodology_rule_audit_lesson_experiment_record_schemas_4_auditor_conditions

## FOUR Auditor conditions (baked into every schema below; my thoughts to USER, now operational)
1. **CANDIDATE != CONFIRMED (no unverified load-bearing).** Audit lessons carry confirmed_or_candidate +
   witnesses_count; CANDIDATEs are ingestable but EXCLUDED from load-bearing queries until promoted (>=3 witnesses
   per existing discipline). Query discipline: "load-bearing audit lessons" filters confirmed_or_candidate=CONFIRMED.
2. **AXIOM-TERM DENOMINATOR EXCLUSION.** METHODOLOGY_RULE + AUDIT_LESSON + all Tier-B/C records are PROCESS-KNOWLEDGE,
   NOT math theorems. They carry term_class=PROCESS_KNOWLEDGE_NON_MATH and are EXCLUDED from the axiom-termination
   ratio denominator (the 206/207 count is over MATH operator/theorem atoms). Without this the invariant's meaning
   dilutes. (FOUNDATION atoms like CRT, by contrast, ARE math and DO count -- they terminate at axioms.)
3. **ATOMS CANONICAL; PROSE BECOMES POINTER.** Each atom carries provenance.prose_source (the MEMORY.md / notes path
   it was atomized from). Post-ingest, the ATOM is the source of truth; the prose entry should be reduced to a
   pointer to the atom_id. Prevents two diverging copies. (Recommend MEMORY.md index lines gain an atom_id ref.)
4. **TIER-C = ATOMIZE-BY-REFERENCE (REVISED per USER push 2026-06-16; supersedes my earlier git-only reco).**
   The right axis is NOT tier-label but CONSUMER/REFERENCE. PRESERVE ALL Tier-C via Tier-1 git (nothing lost,
   grep-searchable) REGARDLESS. ATOMIZE the REFERENCED subset: (i) HONEST_SIGNAL_RECORDs that WITNESS an
   AUDIT_LESSON (they are the evidence grounding the lesson; otherwise the lesson's witnesses_count is prose-only
   -- the same weakness condition 3 guards against); (ii) COMMUNICATION_RECORDs of STRATEGIC class (USER calls,
   phase/scope decisions -> fold into DECISION_RECORD). Routine signals/acks/status comms: relevance ARCHIVE,
   git-preserved + grep-searchable, NOT load-bearing graph atoms. So Tier-C is atomized-by-reference + always
   preserved, NOT "outside." MAXIMAL-ATOMIZATION VARIANT (USER's call): atomize EVERY Tier-C item but stamp
   relevance_tier=ARCHIVE so routine items are graph-walkable yet excluded from load-bearing queries -- valid;
   only cost is store size + query-noise discipline. Default = atomize-by-reference; USER may elect maximal.

## Categorization recap (per DECISION 220; I concur with Tier-A/B/C)
Tier-A always-load-bearing: METHODOLOGY_RULE, AUDIT_LESSON, CAPABILITY (exists), FINDING (exists), FOUNDATION.
Tier-B selectively: EXPERIMENT_RECORD (relevance_tier), DECISION_RECORD (decision_class).
Tier-C archive: HONEST_SIGNAL_RECORD, COMMUNICATION_RECORD. (My condition 4: keep Tier-C git-only.)

## SCHEMA 1 -- kind:METHODOLOGY_RULE (Tier-A; ~24 atoms)
```
  id:            concept::META/METHODOLOGY_<short_name>   (corpus/tier reco below)
  kind:          methodology_rule
  name:          short human label
  corpus:        concept   (RECO; process-meta-knowledge, not math; Testbed confirm)
  tier:          T1        (RECO; foundation-level process rule)
  metric_type:   null      (NOT measured)
  term_class:    PROCESS_KNOWLEDGE_NON_MATH   (condition 2: excluded from axiom-term denominator)
  description:   full rule text (verbatim from the frozen rule)
  rule_class:    USER_LOCKED | DIRECTOR_INTRODUCED | SUBSTRATE_DERIVED   (deterministic; see classification)
  rule_number:   the canonical number (e.g., 11, 13, 14, 19, 22) if it has one
  frozen:        true   (methodology FROZEN at 24)
  provenance:    { source_decision, date, user_locked: bool, prose_source: <notes/MEMORY path> }
  relations:     composes_with -> other METHODOLOGY_RULE atoms (RELATES + metadata.subtype=composes_with;
                    INVERSE_PAIR/HAS_MEMBER not in enum -- use RELATES per schema gotchas)
  DEPENDS_ON:    none (foundation process rule) -- NO phantom edges
```

## SCHEMA 2 -- kind:AUDIT_LESSON (Tier-A; ~92, of which 88 CONFIRMED + 4 CANDIDATE)
```
  id:            concept::META/AUDIT_LESSON_<short_name>
  kind:          audit_lesson
  name:          short human label
  corpus:        concept   (RECO)
  tier:          T2        (RECO; derived process-tier lesson)
  metric_type:   null
  term_class:    PROCESS_KNOWLEDGE_NON_MATH   (condition 2)
  description:   full lesson text
  lesson_class:  VERIFY_DISCIPLINE | TYPE_DISCIPLINE | CERT_CHAIN | INTEGRATOR_DISCIPLINE |
                    PROVENANCE_INTEGRITY | FRAMING | COMPUTE_DISCIPLINE   (deterministic; tag-derived)
  confirmed_or_candidate:  CONFIRMED | CANDIDATE          (condition 1)
  witnesses_count:         integer                        (condition 1; promotion at >=3)
  instance_number:         the catalog number (e.g., 53rd, 66th, 84th, 89th, 91st, 92nd)
  provenance:    { first_witness_source, witness_sources: [...], date, prose_source }
  relations:     composes_with -> related AUDIT_LESSON atoms (RELATES + metadata.subtype=composes_with)
  DEPENDS_ON:    ONLY to EXISTING atoms (e.g., a FINDING/EXPERIMENT_RECORD that triggered it) IF atomized;
                    otherwise the triggering instance goes in provenance prose, NOT as a phantom edge.
                    (Applying the 92nd-candidate phantom-dep lesson to this spec itself.)
```

## SCHEMA 3 -- kind:EXPERIMENT_RECORD (Tier-B; for Tier-3 atomizer; relevance_tier-filtered)
```
  id:            math::T3/EXP_<short_name> or concept::EXP_<short_name>   (corpus = the cell's corpus)
  kind:          experiment_record
  metric_type:   null   (the record points to measured atoms; the record itself is not a measurement)
  term_class:    PROCESS_KNOWLEDGE_NON_MATH   (condition 2)
  experiment_path:  experiments/<cell>.py
  prereg_path:      preregs/<prereg>.md   (if exists; else null)
  metrics_path:     data/<exp>/metrics.json
  cell_sha:         git SHA at run time
  remote_run_id:    orchestrator id (if remote; else null)
  hypothesis:       extracted from cell docstring or prereg (deterministic text extraction; no LLM)
  verdict:          PASS | HARD_FAIL | HONEST_NEGATIVE | HONEST_BOUNDED | MIDDLE_BAND | LOAD_BEARING | KILLED
  relevance_tier:   HIGH | MEDIUM | LOW | ARCHIVE   (deterministic; see classification)
  run_mode:         full | smoke   (smoke-only records default relevance ARCHIVE/LOW per DECISION-149)
  era:              PRE_SUBSTRATE_BUILD | SUBSTRATE_BUILD   (descriptive; era is NOT a relevance input -- see below)
  provenance_quality: CERT_CHAIN_GRADE | LEGACY_EXCERPT | SMOKE_ONLY | UNVERIFIED
                    (CERT_CHAIN_GRADE = ran under the current 3-of-3 + FAIR-NULL + gold-firewall + run_mode=full
                     discipline; LEGACY_EXCERPT = pre-discipline result we "only extracted excerpts" from;
                     SMOKE_ONLY = zero-verdict smoke; UNVERIFIED = claim with no recoverable cell/metrics)
  provenance:    { cell_sha, metrics_sha, date, session_authored }
  DEPENDS_ON:    primitives_used (T1/T2 atom refs) + capabilities_tested -- ONLY existing atom ids (no phantom);
                    a missing primitive triggers the phantom-dep guard -> author foundation first (CRT precedent).

  PRE-SUBSTRATE-BUILD experiments (USER question 2026-06-16): SAME kind:EXPERIMENT_RECORD, SAME Tier-B; relevance_tier
  is assigned by CURRENT-VERIFIED-LINKAGE, NOT by age. The experiments that PROVED the load-bearing capabilities are
  the HIGHEST-relevance records (HIGH) -- old != archive. AUDITOR RULE: relevance_tier reflects the atom's CURRENT
  verified linkage, NOT its ORIGINAL claimed status -- a pre-build "win" later DOWNGRADED on audit (cf. the scorecard-
  overstates-clean-core finding: NER below-target, EM=correctness-not-accuracy, Intent/Bayes bind 0.834) gets relevance
  by what it's CONFIRMED-linked to today, with provenance_quality flagging the legacy/excerpt/smoke evidence base.
  This makes the atomization double as an EVIDENCE-BASE AUDIT: surfaces which capability claims rest on cert-grade vs
  legacy-excerpt evidence (a queryable re-verification backlog), per the floating-fact + provenance-integrity discipline.
```

## SCHEMA 4 -- kind:DECISION_RECORD (Tier-B; decision_class-filtered)
```
  id:            concept::DEC/<number>   ; kind: decision_record ; term_class: PROCESS_KNOWLEDGE_NON_MATH
  decision_number, date, decision_class: STRATEGIC | OPERATIONAL | ROUTINE   (deterministic; see classification)
  description: decision summary ; provenance: { source_note_path, session_authored }
  relations: supersedes / amends -> prior DECISION_RECORD (RELATES + metadata.subtype)
```

## SCHEMA 5 + 6 -- kind:HONEST_SIGNAL_RECORD + kind:COMMUNICATION_RECORD (Tier-C; RECO git-only, condition 4)
```
  Schemas defined for completeness + optional Tier-3 use, but RECOMMEND NOT bulk-atomizing:
  HONEST_SIGNAL_RECORD:  { signal_number, date, session, summary, kind: honest_signal_record }
  COMMUNICATION_RECORD:  { note_path, from_session, to_sessions, date, tag, kind: communication_record }
  If atomized despite the recommendation: term_class=PROCESS_KNOWLEDGE_NON_MATH; relevance archive; NEVER load-bearing.
```

## DETERMINISTIC classification rules (11th rule; NO LLM -- tag/link-based only)
```
  rule_class (METHODOLOGY_RULE):
     USER_LOCKED        if provenance tag/prose contains "USER-LOCKED" or "USER_LOCKED"
     DIRECTOR_INTRODUCED if introduced via a DECISION without USER-lock
     SUBSTRATE_DERIVED  if derived from a measured result
  lesson_class (AUDIT_LESSON): keyword-map on the lesson tag:
     verify/assume/finite-N        -> VERIFY_DISCIPLINE
     metric_type/EM/mislabel       -> TYPE_DISCIPLINE
     cert/chain/step/fidelity      -> CERT_CHAIN
     integrator/pre-ratify/phantom -> INTEGRATOR_DISCIPLINE
     provenance/scorecard/source   -> PROVENANCE_INTEGRITY
     paper/framing/positioning     -> FRAMING
     compute/thermal/OOM/smoke-scale-> COMPUTE_DISCIPLINE
  confirmed_or_candidate: CONFIRMED if witnesses_count>=3 (or already-confirmed in catalog); else CANDIDATE.
  relevance_tier (EXPERIMENT_RECORD):
     HIGH    if the cell's atom-write is LINKED to an atomized CAPABILITY or FOUNDATION atom
     MEDIUM  if cell verdict in {HONEST_NEGATIVE, HONEST_BOUNDED, MIDDLE_BAND} (instructive)
     LOW     if verdict PASS-confirming-expected (replication/sanity)
     ARCHIVE if a duplicate hypothesis+result of an existing HIGH/MEDIUM record  OR  run_mode=smoke-only
  decision_class (DECISION_RECORD):
     STRATEGIC   if tag contains USER_call | phase_boundary | scope | strategic
     OPERATIONAL if tag contains cert-chain step | dispatch | ratify | VET
     ROUTINE     otherwise (heartbeat/status/ack)
```

## INVARIANTS + relation-enum discipline (per schema-gotchas)
- composes_with / supersedes / amends are NOT enum RelationTypes -> use RELATES with metadata.subtype=<name>.
  (INVERSE_PAIR -> DUAL; HAS_MEMBER -> RELATES + subtype; IMPLEMENTS -> USES; per substrate_schema_gotchas.)
- cap_pres=1.0 HARD-FAIL gate fires per batch; batch 50-100 atoms; verify between batches (DECISION 220c cadence).
- 4-gate pre-check (forward-walk + corpus-scoped monotone + axiom-term + dangling) applies; the axiom-term gate
  SKIPS term_class=PROCESS_KNOWLEDGE_NON_MATH atoms (condition 2) -- Testbed: confirm the counter honors this flag.
- NO phantom DEPENDS_ON anywhere (every edge to an existing atom id; missing foundation -> author first, CRT pattern).

## SEARCHABILITY (USER requirement -- delivered by the STRUCTURE, not the dump)
The kind + lesson_class/rule_class/decision_class + confirmed_or_candidate + relevance_tier + term_class fields are
the grep/query handles. Example queries this enables (for me + the Director):
- "all USER_LOCKED methodology rules"            -> filter kind=methodology_rule, rule_class=USER_LOCKED
- "all CONFIRMED verify-discipline lessons"       -> kind=audit_lesson, lesson_class=VERIFY_DISCIPLINE, CONFIRMED
- "all HIGH-relevance experiments that made a capability" -> kind=experiment_record, relevance_tier=HIGH
- "all STRATEGIC decisions (USER calls + phase boundaries)" -> kind=decision_record, decision_class=STRATEGIC
These are trivially grep-able on the jsonl stores AND graph-walkable. Searchability == disciplined fields.

## corpus / tier recommendation (Testbed owns the final call)
RECO: concept:: corpus, META/ id-prefix for METHODOLOGY_RULE (T1) + AUDIT_LESSON (T2); EXPERIMENT_RECORD in the
cell's own corpus (math or concept) at T3. Rationale: process-meta-knowledge is closer to concept than math; the
META/ prefix segregates it for clean filtering. Testbed: confirm corpus/tier + that the partition store + 4-gate
pre-check handle a META/ namespace + term_class=PROCESS_KNOWLEDGE_NON_MATH flag without code change.

## What I am submitting + gating (9th rule)
- TO **Testbed**: 66th-rule PRE-RECEIVE verification of these 6 schemas BEFORE any bulk ingest -- specifically:
  (a) does the partition store accept kind in {methodology_rule, audit_lesson, experiment_record, decision_record,
  honest_signal_record, communication_record}? (b) does the axiom-term counter honor term_class exclusion
  (condition 2)? (c) does the dangling-DEPENDS_ON gate pass with composes_with-as-RELATES? Flag any schema-drift NOW.
- TO **Research (Director)**: ratify the 6 schemas + the 4 Auditor conditions + the corpus/tier reco + my
  Tier-C-git-only recommendation (condition 4; overridable). On ratify, I author the ~24 METHODOLOGY_RULE + the
  88 CONFIRMED AUDIT_LESSON atoms (+ 4 CANDIDATE flagged) -> hand to Testbed ingest.
- I am GATING: Tier-2 atomization ingest + the Tier-3 atomizer schema (Exp-Dev needs these field schemas to author
  tools/atomize_experiment_records.py deterministically).
- PARALLEL (unchanged): P2 prereg DESIGN authoring; P1 STEP-9 post-write VET reactive (CRT + residue_fpe_encoding
  atoms when they land). Cert chain UNDERAILED (USER not-derail constraint; separate thread).

Tag: TIER2_atomization_SPEC_6_kinds_methodology_rule_audit_lesson_experiment_record_decision_record_honest_signal_communication_record_4_auditor_conditions_candidate_not_load_bearing_confirmed_or_candidate_witnesses_count_axiom_term_denominator_exclusion_term_class_PROCESS_KNOWLEDGE_NON_MATH_atoms_canonical_prose_pointer_prose_source_provenance_TIER_C_git_searchable_only_recommended_overridable_deterministic_classification_11th_rule_no_LLM_rule_class_lesson_class_relevance_tier_decision_class_keyword_link_based_composes_with_RELATES_subtype_enum_gotchas_no_phantom_DEPENDS_ON_applied_92nd_lesson_to_own_spec_cap_pres_batch_4_gate_skips_process_knowledge_axiom_term_searchability_via_disciplined_fields_grep_graph_corpus_concept_META_prefix_T1_T2_reco_testbed_pre_receive_66th_rule_director_ratify -- SKUNKWORKS (Auditor)
