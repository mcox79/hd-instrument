# exp_dev hand-off — research: language-ingest glass-box scoping

**Filed-by:** research (Sonnet, research role)
**Filed-at:** 2026-07-05
**Trigger:** USER-directed scoping task ("scope the LANGUAGE INGESTION required for the glass-box-LM language
capstone"). Source research note `notes/research_language_ingest_glassbox_scoping_2026-07-05.md`. Directly reuses
and does not redesign the cell already scoped by the sibling note
`notes/research_substrate_native_language_path_5x_angle5_2026-07-05.md` (`exp_generation_grounded_fact_utterance_v1`,
Section 3 of that note) -- this hand-off promotes it to a formally-ranked anchor plus adds a SECOND anchor (the
morphology-rule-set expansion) surfaced by this drill's own scoping work.

**Pause state:** check `data/orchestrator_paused.flag` per standard exp_dev contract.

**Per [[feedback-no-experiment-design-in-prompts]]** — this hand-off ranks anchor candidates and points at the
research notes for math + mechanism + bands. It does NOT design cells inline; exp_dev authors cells per autonomy
declaration below. Per `feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
and the 2026-06-26 strategic pivot: both anchors are STRUCTURED/glass-box (retrieval + algebraic rule-transform +
lookup-table glue), never raw-text statistical-LM ingest, never BPC/bigram discriminators.

---

## Source research note

`notes/research_language_ingest_glassbox_scoping_2026-07-05.md`

Read it FIRST for: the 4-layer language-ingest decomposition (vocabulary/lexicon, morphology, syntax, phrasings)
with verified rough-scale numbers per layer; the glass-box inspectable-representation argument (lexicon table +
algebraic morphology transforms + bound-factor frame templates + resonator search, none of it opaque statistics);
the dependency table proving neither the HELD re-encode nor the cortex-layer (Cortex-1/Cortex-2) gates this work;
the staged build sequence; developmental-acquisition cross-validation of the staging order; and the pre-registered
HARD-PASS/HARD-FAIL bands for both anchors below (this hand-off's bands are copied verbatim from that note's
"Falsifiable predictions" section -- do not re-derive).

---

## Anchor candidates — rank-ordered

### ANCHOR_1 (TOP — cheapest, every load-bearing piece already CG/HARD_PASS): exp_generation_grounded_fact_utterance_v1

- **Anchor pointer:** `notes/research_substrate_native_language_path_5x_angle5_2026-07-05.md` Section 3 (full cell
  spec, pre-registered bands) + `notes/research_language_ingest_glassbox_scoping_2026-07-05.md` Section 1 Layer A/D
  (the common-word-filter + relation-verb-table scale numbers this cell's curation step needs) and "Falsifiable
  predictions" (bands reaffirmed here verbatim).
- **Substrate-product reading:** ships the first end-to-end, human-legible "the substrate speaks a real grounded
  fact" milestone -- retrieve a real KG fact via the CG multi-hop primitive, compose it via the HARD_PASS
  Integration reason-generate bridge, decode it via the LANDED native block-local decoder
  (`exp_generation_decoder_gsbc_native_blocklocal_v1`), and print the recovered token strings via the EXISTING
  `id_order_json` name lookup (177,899 real ConceptNet/taxonomy names, already verified off-disk). The only genuinely
  NEW piece is the string-print step (instrumentation) plus a one-time common-word frequency/regex filter and a
  ~20-30-row ConceptNet-relation-to-verb-phrase lookup table (both glue, not research). This is glass-box BY
  CONSTRUCTION: every emitted token traces to one unbind operation on one specific bound structure, auditable
  (which unbind produced which token, its cleanup cosine).
- **Tier hint:** every component reused is independently already CG or HARD_PASS/MM_STANDARD (VET-scoped). Expect
  this composed cell to land at MEASURED_MECHANISM-to-CHAIN_GRADE depending on whether the untested JOINT
  (retrieve->bridge->decode->print) holds when chained -- that is the one genuinely open question this cell answers,
  per the source note.
- **Why now:** near-zero cost (~100-150 lines of glue + a manual curation pass, CPU-local, minutes, no GPU, no new
  training). Every dependency (encoder, narrow KG ingest, bind/unbind algebra, multi-hop retrieval, the
  reason-generate bridge, the decoder) is already done -- verified in the source note's dependency table. Nothing
  blocks it.
- **Pre-registered bands (copied verbatim from source note, do not re-derive):**
  - HARD-PASS: end-to-end exact-ordered token match >= 0.70 on >= 20 curated common-word ConceptNet S/V/O facts;
    zero garbled/obscure-to-a-human decodes; shuffled-fact control collapses (discriminator fires).
  - HARD-FAIL: exact-ordered match < 0.30 (an undiagnosed integration-joint bug between three otherwise-proven
    primitives), OR >= 20% non-legible decodes (mechanism sound, vocabulary curation the real gap).
  - MIDDLE: 0.30-0.70, OR mechanism clears but legibility fails -- diagnostic, not a wall; the fix in either case is
    curation/filtering, not new architecture.
  - **HARD-FAIL (over-claim guard, applies regardless of numeric result):** if this cell's result, if it passes, is
    represented as "the substrate speaks English" or "language is solved" -- that framing is itself the failure
    condition. The honest scope is: telegraphic (no morphology, no function words, no grammar beyond fixed-slot
    content-word order), drawn from a narrow pre-ingested KG, not general knowledge.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.55 / 0.30 / 0.15** (lit-scan-calibration-penalized from the source
  note's pre-penalty ~0.65-0.70 minimum-ingest-sufficiency estimate; every component independently proven, but the
  specific 4-stage CHAIN has never been run end-to-end).

### ANCHOR_2 (cheap, mechanism already proven in isolation, extends the WUG-test cell): morphology_ruleset_expansion_wug_v2

- **Anchor pointer:** `notes/research_language_ingest_glassbox_scoping_2026-07-05.md` Section 1 Layer B (the
  verified 8-core-inflectional-rule count + ~150-200 irregular-verb exception-list scale) and "Falsifiable
  predictions" (morphology-wiring band, reaffirmed here verbatim). Existing proven cell to extend:
  `data/exp_lex_wug_test_cpu_v1/metrics.json` (HARD_PASS, 3-shot=1.000, 1-shot=1.000, ONE rule: present->past).
- **Substrate-product reading:** ships the SECOND glass-box language layer -- expand the already-HARD_PASS
  "infer a rule from a few examples, generalize to a novel stem" mechanism (a literal algebraic transform per rule,
  auditable, dual-route Pinker/Prince-style) from 1 rule to the field's own well-established count of the ~8 core
  English productive inflectional rules (plural -s, possessive -'s, 3rd-person-singular -s, past -ed, past
  participle -en/-ed, progressive -ing, comparative -er, superlative -est), each independently tested the same
  few-shot way. This is the CHEAPEST of the three real (non-glue) language layers -- a handful of algebraic rules,
  not a corpus -- and is a direct, low-risk extension of an existing HARD_PASS, not new research.
- **Tier hint:** MEASURED_MECHANISM if >= 5 of 8 rules individually clear >= 0.85 novel-stem generalization;
  promotes toward CHAIN_GRADE if all 8 clear with cv <= 0.05 across seeds. Does NOT require wiring into the
  generation decoder to be discriminable on its own (wiring into Stage C is a follow-on, separately scoped in the
  source note's Section 3 staging table, item 2).
- **Why now:** the mechanism is already HARD_PASS on ONE rule; this is a width extension (more rules, same proven
  procedure), not a new mechanism bet. Cheap, CPU-local, no GPU. Independent of ANCHOR_1 -- can run in parallel.
- **Pre-registered bands (copied verbatim from source note, do not re-derive):**
  - HARD-PASS: each of >= 5 of the ~8 core English inflectional rules, tested via few-shot rule inference (same
    procedure as the existing WUG cell), holds novel-stem generalization >= 0.85.
  - HARD-FAIL: any individual rule's novel-stem generalization < 0.60 -- would indicate the existing WUG HARD_PASS
    was rule-specific (present->past may be an easier transform than, e.g., plural formation with its 3 allomorphs
    -s/-z/-Iz) rather than evidence of a general dual-route capability -- a genuine, useful negative result.
  - MIDDLE: 0.60-0.85 on one or more rules -- diagnostic of which specific rule classes generalize vs. need a richer
    transform (e.g. allomorph-conditioned rules), not a wall.
- **P_HARD-PASS / P_MIDDLE / P_HARD-FAIL = 0.50 / 0.35 / 0.15** (existing single-rule mechanism is HARD_PASS at
  1.000; deflated per lit-scan-calibration since allomorph-conditioned rules like plural -s/-z/-Iz are plausibly
  harder than the tested present->past transform and this is genuinely untested at width > 1).

---

## Recommended dispatch order

1. **ANCHOR_1 (grounded-fact-utterance)** FIRST — cheapest, highest product-visibility, zero new mechanism risk
   (pure composition of already-proven pieces); local_cpu_queue; ~minutes.
2. **ANCHOR_2 (morphology-ruleset width extension)** in parallel — independent cell, different file, no shared
   state with ANCHOR_1; local_cpu_queue; ~minutes.

Both are cheap enough to ship together in the same cycle; there is no dependency between them (ANCHOR_1 does not
need ANCHOR_2's rules to speak an unconjugated/citation-form fact; ANCHOR_2 does not need ANCHOR_1's retrieval
pipeline to test rule generalization in isolation, matching the existing WUG cell's own isolated-test methodology).

---

## Context pointers

- Primary source note (full 4-layer decomposition, glass-box argument, dependency table, developmental-acquisition
  cross-check, citations): `notes/research_language_ingest_glassbox_scoping_2026-07-05.md`
- Sibling note (ANCHOR_1's original cell spec, Section 3): `notes/research_substrate_native_language_path_5x_angle5_2026-07-05.md`
- Generation mechanism spec + brain-convergence lit (Levelt/Dell/Garrett/resonator networks/competitive queuing/
  theta-gamma): `notes/research_5x_drill_generation_spec_and_brain_mechanism_2026-07-05.md`
- Decoder design + pre-registered envelope (F=2 hard wall, V<=1024 cliff, D<=26 slots): `notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md`
- VET-scoped tiers (decoder MM_STANDARD not HARD_PASS; envelope CHAIN_GRADE): `notes/integrated_short_term_spec_sheet_5x_drills_what_we_want_how_brain_does_it_2026-07-05.md`
- Existing HARD_PASS cell ANCHOR_2 extends: `data/exp_lex_wug_test_cpu_v1/metrics.json` + `experiments/exp_lex_wug_test_cpu_v1.py`
- Existing HARD_PASS/MIDDLE_BAND cells informing curation/legibility (POS tagger, dep-parser, lexicon emission,
  frame-slot planner): `data/exp_pos_tagger_ptb_substrate_cpu_v1/metrics.json`,
  `data/exp_depparse_discriminative_cpu_v1/metrics.json`, `data/exp_comm_lex_emission_cpu_v1/metrics.json`,
  `data/exp_substrate_response_planner_frame_slot_composition_v1/metrics.json`
- ConceptNet ingest tool (relation-type enumeration for ANCHOR_1's relation-verb table): `tools/substrate_conceptnet_ingest_v1.py`
- Vocabulary source table (177,899 real names, verified off-disk): `data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz`
  (`id_order_json` field) via `data/gen_decoder_gsbc_fillers/gsbc_expand2x_pool_v1.npz`
- Why the OLD statistical-LM ingest track is CLOSED and must not be revived: `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`
  + `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`

---

## Contract section

- Pre-reg discipline per `[[feedback-envelope-expansion-fail-bands]]`: HARD-PASS + HARD-FAIL bands above are
  pre-registered HERE (copied verbatim from the source note); exp_dev MUST lift them into each cell's prereg note
  verbatim before dispatch.
- Self-test per `[[feedback-formula-selftests]]`.
- Multi-seed FULL on smoke clearance (ANCHOR_2 especially -- per-rule cv matters, not just mean).
- Queue routing: both anchors are CPU-local, near-zero compute (per the source note's effort estimate) --
  local_cpu_queue for both, no GPU/remote needed.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- Per-arm metrics-read per Fix #28 -- DO NOT trust verdict_msg framing; read metrics.json per-arm/per-rule before
  any cross-cell convergence claim, especially for ANCHOR_2's per-rule breakdown.
- Post-ship REMOTE VERIFY per Fix #11 pipeline template (if either lands on a queue with remote verification;
  local_cpu_queue may not require it -- follow standard exp_dev contract).
- Default tier MIDDLE per Fix #28; let cert-owner tier UP from observed metrics.
- No-smoke discipline: rate honestly; do NOT let either cell's pass, if it passes, be narrated as "language solved"
  -- both source notes are explicit that this is telegraphic/narrow-lexicon, not conversational fluency. Any
  verdict_msg or downstream framing that over-claims fluency is itself a HARD-FAIL condition (see ANCHOR_1's bands
  above) independent of the numeric result.
- Common-word curation filter (ANCHOR_1) and the exact ~20-30-row relation-verb table are exp_dev's implementation
  choice (see autonomy declaration) but MUST be checked into the cell's own repo artifacts (not hand-picked
  per-run) so the curation is inspectable/reproducible, consistent with the glass-box argument in the source note.

---

## Autonomy declaration

exp_dev decides:
- Cell author (manual vs spawn cell-author sub-agent)
- Smoke seed + smoke timeout for both anchors
- Exact common-word frequency/regex filter threshold for ANCHOR_1 (recommend: filter the 177,899-name pool to
  entries matching a common-English-word list, e.g. reject multi-token Latin-binomial CN_ nodes and entries with
  document-frequency below a chosen floor -- exact floor is exp_dev's call, guided by the source note's
  General-Service-List-class coverage numbers, ~2,000 word families for ~80-90% coverage, as a sizing anchor, not a
  hard requirement)
- Exact relation-to-verb-phrase mapping table content for ANCHOR_1 (the ~20-30 ConceptNet relation types already
  enumerated in `tools/substrate_conceptnet_ingest_v1.py` -- exp_dev picks the canonical verb-phrase gloss per
  relation)
- N >= 20 fact count for ANCHOR_1's test set (source note recommends >= 20 curated common-word S/V/O triples;
  exp_dev may scale up if cheap)
- Which >= 5 of the 8 core English inflectional rules to prioritize for ANCHOR_2's first pass (recommend starting
  with the 4 highest-frequency/simplest: plural -s, past -ed, progressive -ing, 3rd-person -s, since these have the
  fewest allomorph/spelling-rule complications; comparative -er/superlative -est and possessive -'s as the next
  tier; the source note flags plural -s/-z/-Iz allomorphy specifically as the likely-hardest test case)
- Whether ANCHOR_2 tests each rule on synthetic stems (matching the existing WUG cell's methodology exactly, for
  apples-to-apples comparison) or on real dictionary stems (source note does not mandate either; synthetic
  matches the existing proven cell's design and is the lower-risk choice)
- Whether to bundle ANCHOR_1 + ANCHOR_2 into one dispatch cycle or ship sequentially (recommend parallel -- no
  shared state, independent bands)
- Whether ANCHOR_2's decoder-wiring follow-on (Stage C integration, staging item 2 in the source note) is scoped as
  part of this cycle or deferred to a THIRD hand-off after ANCHOR_2 lands (recommend: defer -- wiring is a distinct,
  larger-scope follow-on that should be scoped fresh once the rule-width-extension result is in hand)

Research's authority ends at the anchor list + bands + brain-mechanism math + scale numbers. exp_dev is the
cell-design authority.

Recommended FIRST dispatch: ANCHOR_1 + ANCHOR_2 in parallel, both on local_cpu_queue.

---

-- research
