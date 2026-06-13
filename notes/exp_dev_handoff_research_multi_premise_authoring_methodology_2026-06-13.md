# exp_dev hand-off — research: multi-premise authoring methodology (LANE B depth-lever correction)

Filed-by: research sub-agent (opus, depth-drill)
Filed-at: 2026-06-13
Trigger: depth-forecast cell found avg-premise-count = 1.00 on post-resync 20820-atom substrate; depth-7+ path blocked at LANE B without multi-premise extraction; research drill confirms parser-fidelity gap is the dominant hypothesis (P_deflated = 0.60).
Source research note: [notes/research_DRILL_multi_premise_authoring_methodology_LANE_B_depth_lever_correction_2026-06-13.md](research_DRILL_multi_premise_authoring_methodology_LANE_B_depth_lever_correction_2026-06-13.md)

## Pause state

Check d:/AI/hd-instrument/data/orchestrator_paused.flag before shipping any cell. If pause is set, file this handoff for next unpause cycle.

Per [[feedback-no-experiment-design-in-prompts]]: handoff names anchors and pointers, NOT cell-specific JSON or parameter sets. exp_dev authors the cells.

## Anchor candidates (rank-ordered)

### A1. CELL MPM (Manual Premise Manual-Gold) -- decisive cheap test, Tier 0

- **Anchor pointer**: research note section "Cheap decisive test"; substrate atom registry; LANE B Mathlib parser tool path.
- **Substrate-product reading**: empirical resolution of "is single-parent structure a parser-fidelity gap or a corpus-structural property?"
- **Tier hint**: Tier 0 -- CPU only, ~1 person-hour, no GPU. Smoke gate trivial.
- **Why-now**: blocks the HARD-PASS bar update; without this signal, exp_dev cannot decide whether parser-v2 work is justified or whether substrate needs a separate T2/T3 composition operator.
- **Predictions wired to research note (a) Falsifiable predictions** section.

### A2. CELL PV2-MATHLIB (Parser-v2 Mathlib, elaborator-shape regex) -- post-MPM if HARD-PASS

- **Anchor pointer**: research note "Pattern 1" code snippet; existing LANE B Mathlib parser path; LeanDojo arxiv 2306.15626.
- **Substrate-product reading**: empirical avg-premise-count >= 2.6 on 100-atom Mathlib re-extraction sample (lit baseline; substrate may land lower due to atom granularity).
- **Tier hint**: Tier 1 -- CPU + parser engineering; no GPU. ~half-day implementation + 30min validation.
- **Why-now**: largest single corpus in LANE B; one fix here delivers the largest premise-count uplift. Apply LeanDojo bracket-list + apply-chain regex pattern.

### A3. CELL PV2-PROOFWIKI (Parser-v2 ProofWiki, wikilink+section filter) -- parallel to A2 if MPM passes

- **Anchor pointer**: research note "Pattern 3" code snippet; existing LANE B ProofWiki parser path; NaturalProofs arxiv 2104.01112.
- **Substrate-product reading**: empirical avg-premise-count >= 1.5 on 100-atom ProofWiki re-extraction.
- **Tier hint**: Tier 1 -- CPU + MediaWiki API; no GPU. ~half-day.
- **Why-now**: ProofWiki is mathematically-broadest corpus and has clean wikilink structure. Cycle tolerance is the critical addition.

### A4. CELL PV2-MIZAR (Parser-v2 Mizar `by`/`from` regex) -- parallel; high upside

- **Anchor pointer**: research note Pattern 1b "Mizar `by`/`from` reference parser" code snippet; mizar-items arxiv 1107.4721.
- **Substrate-product reading**: empirical avg-premise-count >= 5.0 (lit baseline 11.5).
- **Tier hint**: Tier 1 -- CPU regex; no GPU. ~few hours.
- **Why-now**: Mizar premises are EXPLICITLY cited in proof syntax via `by` and `from` keywords; lowest-effort multi-premise extraction.

### A5. CELL PRECNT-METRIC (premise-count + longest-path benchmark instrumentation) -- enabling

- **Anchor pointer**: research note section "Pre-reg HARD-PASS bar update"; substrate atom registry; existing dashboard metrics path.
- **Substrate-product reading**: shift dashboard from single-axis "atoms_authored" to 4-tuple (atoms_authored, avg_premise_count, longest_path, premise_count_histogram) per LANE B parser.
- **Tier hint**: Tier 0 -- instrumentation only; no GPU.
- **Why-now**: makes the new HARD-PASS bar measurable. Without this, A2/A3/A4 cell verdicts cannot be evaluated.

## Context pointers (paths, not summaries)

- d:/AI/hd-instrument/notes/research_DRILL_multi_premise_authoring_methodology_LANE_B_depth_lever_correction_2026-06-13.md (this drill)
- d:/AI/hd-instrument/notes/substrate_L6_PROOF_FINDER_HARD_PASS_20_20_SOUND_axiom_terminating_38pct_genuine_T1_62pct_authoring_gap_USER_goal_deduction_closed_2026-06-13.md (62pct authoring gap that this drill explains)
- d:/AI/hd-instrument/notes/substrate_methodology_rule_12th_universal_operators_field_specific_signal_extractors_first_class_field_partition_routing_H3_HYBRID_first_appearance_2026-06-13.md (composes with parser-as-field-specific-extractor frame)
- d:/AI/hd-instrument/notes/substrate_CHTV1_substrate_as_verifier_HARD_PASS_1p0_precision_LLM_categorical_gap_checkable_ground_truth_2026-06-12.md (2,491-edge generalized typing context that multi-premise feeds)

## Contract

- exp_dev decides which cells ship in what order. A1 is the gate -- without MPM signal, A2/A3/A4 risk wasted parser-engineering effort.
- If A1 HARD-FAIL (substrate atoms are single-parent by granularity), pivot to T2/T3 composition operator design and DO NOT ship A2-A4.
- All cells smoke-gated; ship via queue_add.sh; post-ship REMOTE VERIFY per standard protocol.
- All cells must report the 4-tuple (atoms_authored, avg_premise_count, longest_path, premise_count_histogram) at completion.

## Autonomy declaration

exp_dev owns: cell-level pre-reg JSON, smoke design, ship-or-skip ordering across A1-A5, per-cell HARD-PASS / HARD-FAIL bands within the bounds set by research-note falsifiable-predictions section.

Research declines to author cell JSON per [[feedback-no-experiment-design-in-prompts]].
