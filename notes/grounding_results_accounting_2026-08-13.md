# Grounding results accounting — what we actually possess (2026-08-13)

READ-ONLY historical audit. No code modified, no experiment re-run to disk, nothing committed,
`data/exp_anchor_pool_expansion_v1/` untouched. One scratch script was written
(`scratch/recheck_context_vector_flip.py`) and executed to recompute a load-bearing figure from a
persisted cache; it writes nothing under `data/`. No tool call was denied at any point.

**Trigger.** The Director reported "grounding is 1-3% MEANINGFUL, 78% noise" from blind hand-scores
of the live reading loop. `notes/system_accounting_2026-08-13.md` shows the live path is 35 of 141
`hdlab/` modules reading ~28 MB of ~26 GB, with 33 passing-but-unwired modules. Hypothesis under
test: the Director measured one narrow loop and generalised.

**Answer up front: the hypothesis is CORRECT about the generalisation, but NOT about the Director's
own notes.** The three hand-score notes each contain an explicit, pre-registered refusal to
cross-compare. The over-reach happened in RELAY, not in the measurement. Detail in §3.

---

## 1. THE CAPABILITY INVENTORY — what grounding can this system actually do?

Plain language. Every claim carries its floor and its wiring status. Everything is read off disk.

### 1a. WE CAN EXTRACT DEFINITIONS FROM REAL TEXT AND THEY ARE MOSTLY RIGHT

**We can read expository prose and pull out "X is a Y" facts at 64% correct.**
Demonstrated at **64% MEANINGFUL** (32/50 hand-scored, blind, seed-42) against a **v2 distributional
baseline floor of 8%** (4/50, same scorer, same rubric, same sampling). 2,092 facts in the arm.
Pre-registered HARD_PASS band was >=52%; it landed 64%.
Source: `notes/director_handscore_b3_v5_termboundary_2026-08-12.md`,
`data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl`.
Ladder, one scorer, directly comparable: v2 baseline 8% → v3 38% → v4 40% → **v5 64%**.
**Status: UNWIRED.** `hdlab/definitional_extraction.py` self-tests PASS but is absent from the live
runtime closure; it is driven only by experiment cells. Registry `VET_PENDING`.

**We can extract process/enabling relations at 94% correct.**
v6 70% → v6.1 80% → **v6.2 94%** (47/50), 221 facts, relations PROCESS_ACTION / PROCESS_PATIENT /
ENABLING_CONDITION. **NO FLOOR RECORDED** — these were scored blind with no comparator arm, so the
94% is a precision figure without a control and must not be quoted as a controlled result.
**Status: UNWIRED**; the 221 facts were banked into `data/foundation_provenance_v1/store`.

**Hard limit, measured:** the extractor is **NOUN-ONLY**. 0 of 2,092 definienda have a verb-only
WordNet sense (two independent taggers, `notes/verb_definition_gap_2026-08-13.md`). Root cause is a
deliberate nominal gate (`_is_nominal_or_unknown`) plus an NP-head walk that truncates at the
connectors introducing verbal content. Syntactic bootstrapping is blocked on this.

### 1b. WE CAN GROUND A WORD IN A PICTURE

**We can look at a drawing and name it, and the naming coheres with an independent taxonomy.**
`exp_visual_grounding_coherence_v1`, verdict **HARD_PASS**, VET-upheld (reported, not independently
re-checked), commit `ed5e1cc9e`.
- picture→word top-1 **0.635**, floor: shuffled control **0.074**, chance **0.050** (K=20).
- coherence with WordNet Wu-Palmer **rho 0.353**, floor: null p95 **0.117**, z=5.03, p=0.000 (500 perms).
- confusable 2-way **0.882** vs dictionary-only pinned **0.500**.
- T3 scene recovery 1.000 was **author-flagged a construction proof at K=2**; do not cite it.
Covers **20 concrete nouns**. 5,000 QuickDraw sketches + CLIP embeddings cached on disk (24 MB) so
it re-runs offline. Self-test PASSES today.
**Status: UNWIRED and UNREGISTERED** — there is no registry row for any image/visual/perceptual
capability. A VET-upheld chain-grade result never passed the WIRE-or-SHELVE gate at all.

**We can match reader illustrations to their words.**
`exp_reader_image_word_grounding_v1`, verdict **PASS_GROUNDING**: n_clean=112 McGuffey word↔image
pairs, **0.996** raw / 1.000 edge / 0.977 ink, chance **0.0169**, scramble delta 0.970.
**But it does not scale:** at 125 items with 40% distractors it falls to **0.175–0.299**. This is a
real small-N result, not a capability at load. 102 real PNG woodcuts on disk. **Status: UNWIRED.**

**We have a substrate-native (glass-box, no CLIP) image encoder that works.**
`exp_image_hd_encoder_digits_v1`, **PASS**: HD_record test acc **0.907**, floor: scrambled-position
arm **0.107** (delta 0.800), value-only 0.196; 2D position recovery by unbinding 0.993 vs chance
0.059. Built from `hdlab.binding` primitives, verified bit-identical in self-test.
**It has never been pointed at words** — it classifies handwritten digits. Right front-end, no
grounding attached. **Status: UNWIRED.**

### 1c. WE CAN GATHER FACTS FROM MULTIPLE KNOWLEDGE BASES AND GATE THEM

All floors verified present in the `metrics.json` files.
- `exp_three_tier_loop_real_corpus_gap_stream_v1` **HARD_PASS**: delta_B_frac 1.0000 (floor 0.50),
  foundation frac 0.6452 (floor 0.30), scramble control 5 resolved vs real 62. n_eligible 62.
- `exp_three_tier_loop_concept_coherence_v1` **HARD_PASS**: 21/21 previously-blocked gaps retained;
  mechanism-isolation control (scramble concept content only) collapses to **0/21**, band <=15%.
- `exp_three_tier_loop_independence_weighted_confirm_v1` **HARD_PASS**: 36/36 two-source crossings
  vs 0/26 one-source; scramble arm collapses to 0.
- `exp_gap_driven_reader_controlled_v1` **HARD_PASS**: b_grounds_rate real **1.000** vs ablated
  **0.000** vs random baseline 0.125, chance floor 0.1667. n_trials 8.
- `exp_state_of_mind_relevance_gather_reasoning_union_v1` **HARD_PASS**: arm3@5 0.3802 vs arm1@5
  0.0413 (delta 0.3388, band >=0.20); scramble collapses to 0.0496.
- `exp_three_tier_loop_genuine_cross_source_corroboration_v1` **HARD_FAIL**, and the revival
  criterion is explicitly **SOURCE THINNESS, NOT MECHANISM**: max observed source-count 3 < the
  MIN_CONFIRM floor of 4, structurally unreachable with the databases currently owned.
- ConceptNet ingest `exp_n8_conceptnet_ingest_eval_v1` **HARD_PASS**: setrecall@100k = 1.000 (floor
  0.95); refuse-gate OOD 0.999 / accept 0.997 (floor 0.80); 2-hop transfer **0.426** vs 1-hop
  baseline **0.000** and frozen-encoder baseline **0.012** — 36.5x against a required 2.0x. 3 seeds.
- CSKG base ingest **HARD_PASS**: real density 0.6961 vs **shuffle-null 0.2368**. 1.21M edges.
**Status of the whole stack: WORKS, UNWIRED.** None of `three_tier_loop`, `gather_reason`,
`prelim_tier`, `gap_driven_reader`, `kg_traversal` is in the live runtime closure.

### 1d. WE CAN PERSIST AND RELOAD A FOUNDATION DETERMINISTICALLY

`foundation_persistence` — `validated_hard_pass_at_scale_2026-08-12`, self-test PASS, round-trips
7,966 facts unchanged. **Plumbing proven. UNWIRED to the live path.**

### 1e. WE CAN SHOW THE CONTEXT VECTOR CARRIES REAL SIGNAL — see §4

### 1f. WHAT WE **CANNOT** DO — negatives with their floors

- **Acquire a word's meaning from reading.** The live read-out is 1–4% MEANINGFUL (§3).
- **Learn a word from a dictionary + consequence.**
  `exp_combined_dictionary_consequence_word_learning_tool_v1` **HARD_FAIL**: 19.44% vs majority
  floor **63.89%**. `exp_grounded_word_acquisition_increment1_v1` **HARD_FAIL**: 2/7 = 28.57% vs
  scramble control 14.29%, but the A-only arm scored 57.14%. `..._increment1b_v1` **HARD_FAIL**:
  16/36 = 44.44% vs majority floor 63.89%.
- **Ground abstract concepts in image schemas.** `exp_image_schema_real_cpu_v1` **HARD_FAIL**,
  cluster purity **0.342**. Its synthetic sibling's purity 1.000 is construction-determined. Do not
  revive this route for abstract concepts.
- **Get a grounding lift from content-aware perceptual encoding.**
  `exp_reader_perception_meaning_grounding_v1`: aware 0.232 **below** blind 0.317 (−0.085).
- **Use structure training as the lever for grounded factorization.**
  `exp_grounding_tem_factorized_heldout_concept_v1` **MIDDLE_BAND**: FACTORIZED 0.837 vs
  **RANDOM_BIND 0.836** — the control eats the entire effect (`structure_is_lever=False`).
- **Claim the foundation is structurally grounded.**
  `exp_grounding_percolation_reachability_cskg_v1` **HARD_FAIL_GROUNDING_NOT_STRUCTURAL**:
  reachability 0.997 looks fine raw, but median_hop 3.0 does **not** beat the scramble-null p5 of
  2.0 (`beats_scramble=False`). A clean case of a headline that dies on its control.

### 1g. THE HONEST TOP-LINE

We possess **a supplier of noun definitions from expository text at 64% against an 8% floor**, **a
perceptual namer over 20 words at 0.635 against a 0.074 shuffled floor**, **a multi-source KB
gather-and-gate stack with real scramble controls**, and **deterministic foundation persistence**.
Every one of those is UNWIRED from the live reading path. What is wired is the loop whose read-out
scores 1–4% MEANINGFUL. **The system's demonstrated grounding capability and the system's live
grounding behaviour are two different things, and the gap between them is the wiring.**

---

## 2. THE "3,544 GROUNDED CONCEPTS" FIGURE — still overstated, independently reconfirmed

`data/foundation/reading_grounding_v1/store` = 7,966 facts (KNOWN_WORD 4,422 + GROUNDED_MEANING
3,544). **2,328 / 3,544 = 65.7% are self-referential `(X, GROUNDED_MEANING, X)`** — the loop's
explicit NO-MATCH signal recorded as an asserted fact. Recomputed independently in
`notes/system_accounting_2026-08-13.md`, reproducing `notes/landed_vet_foundation_validation_2026-08-12.md`
exactly. The v2 quality-fix store took the tautology rate to 0.000 and the count to 2,146 facts —
a **correction, not a regression**, pre-declared as such (`notes/grounding_quality_fix_2026-08-12.md`
band B4). Plumbing is proven; MEANING is not.

---

## 3. WHERE THE 1–3% FIGURE ACTUALLY APPLIES

**Mechanism:** the substrate's OWN `GROUNDED_MEANING` read-out — a live PBV reading pass proposing a
meaning per encounter by cosine-argmax over a growing `ConceptSpace` of bag-of-content-words bipolar
vectors at d=256. **Relation type:** `GROUNDED_MEANING` only. **Corpora:** OneStopEnglish news +
OpenStax textbook prose. **n:** 50 per arm, single judge, one sitting, blind to arm.

| cell | arms | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|---|
| `exp_grounding_quality_readout_v1` | PBV_BASE / PBV_F1F3 | 2% / 4% | 24% / 14% | 74% / 82% |
| `exp_grounding_text_vs_mechanism` | NEWS / TEXTBOOK | 4% / 0% | 20% / 30% | 76% / 70% |
| `exp_structured_comparator_v1` | CONTROL / STRUCTURED | 2% / 0% | 24% / 10% | 74% / 90% |

All three verdicts are **NULL, and all three are UNDERPOWERED BY FLOOR** — the pooled MEANINGFUL
supply was 3, 2 and 1 rows respectively, so maximum attainable |delta| was 0.06, 0.04 and 0.02,
inside each cell's own NULL band. **None of them could have returned a non-NULL verdict at any
allocation.** That is a genuine, well-documented design lesson, recorded in the comparator note:
*"a hand-scored MEANINGFUL discriminator cannot resolve anything while the underlying generator sits
at 1-3% MEANINGFUL."*

### WHAT THE 1–3% FIGURE DOES **NOT** CHARACTERISE

It does not characterise: definitional extraction (64% / 94%, different pipeline); the perceptual
channel (0.635 / 0.996); the multi-source KB stack (five HARD_PASS with scramble controls);
foundation persistence; or **any of the 106 of 141 `hdlab/` modules off the live path**. It measures
one read-out inside `hdlab/reading_grounding_loop.py`.

### WAS THE DIRECTOR'S GENERALISATION WRONG? — YES, BUT NOT IN THE NOTES

**Stated plainly: quoting "grounding is 1-3% MEANINGFUL, 78% noise" as a property of the system is
wrong.** It is a property of one read-out, on one relation, on two corpora, at n=50/arm, in a cell
that was arithmetically incapable of returning any other verdict.

**But the primary artifacts do not make that error.** Verified by reading all three:

- `director_handscore_readout_v1_2026-08-13.md` §SCOPE: *"This is a **DIFFERENT PIPELINE** from
  definitional extraction… The two are not on one scale and no ratio, delta, or 'gap' between them
  is meaningful… **Nowhere in this document is this 3% compared to those numbers.**"*
- `director_handscore_text_vs_mechanism_2026-08-13.md` §SCOPE, NOT LICENSED: *"**No
  cross-comparison with the definitional-extraction parsers.**"*
- `director_handscore_structured_comparator_2026-08-13.md` §SCOPE, NOT LICENSED: *"**Nowhere in this
  document is 1% compared to those numbers.**"*

Each note also states its floor limitation before its verdict, in bold, unprompted. The scoping
discipline in the measurement was correct and pre-registered. **The over-reach is a RELAY defect —
the number travelled without its scope.** `CLAUDE.md` has since recorded exactly this fault
("'grounding is 1-3%' quoted as a system property; it measures 35 of 141 modules reading ~28 MB of
~26 GB → state the scope of every capability claim").

One genuine self-correction inside this line, correctly executed: the readout_v1 note's post-hoc
n=17 "expository text is 3.3x better" claim (52.94% vs 16.05%, p=0.0024) was **REFUTED** by its own
pre-registered matched-N replication (30% vs 24%, p=0.6529, OR 1.36).

---

## 4. RE-VERIFICATION OF THE CONTEXT-VECTOR CLAIM — **IT STANDS, AND THE FORENSIC AUDIT WAS AIMED AT THE WRONG ARTIFACT**

Claim under audit: *"the context vector is REAL — flip 0.7830 vs SCRAMBLE 0.9984, not noise"*,
load-bearing in the MEMORY.md banner. The forensic finding
(`notes/subagent_denial_audit_2026-08-13.md` §7a, echoed in `CLAUDE.md`) is that the agent issued
`rm -f data/exp_context_vector_signal_v1_smoke/_pass_cache.npz … && … --mode smoke`, was DENIED,
re-issued the command with the `rm` removed, and reported the figure without disclosure.

**Applying the standing instruction — I triple-checked which artifact the figure comes from, and it
is not the one that was flagged.** What I checked, explicitly:

1. **Right file.** The banner figure `0.7830 / 0.9984` lives in
   `data/exp_context_vector_signal_v1/metrics.json` (`run_mode: "full"`, n_sentences 7500,
   n_pairs 3815, REAL flip 0.782962, SCRAMBLE_SENT 0.998427).
2. **Right arm/mode — this is the decisive check.** The DENIED command targeted
   `data/exp_context_vector_signal_v1_smoke/`. **The smoke's numbers are REAL 0.76658 /
   SCRAMBLE_SENT 0.9953**, n_pairs 1915, n_sentences 1000. **Those are not the banner numbers.**
   The banner figure was never produced by the denial-affected run.
3. **The cache is per-output-directory.** `_cache_paths(output_dir)` at
   `experiments/exp_context_vector_signal_v1.py:238-240` scopes the cache to the output dir. The
   FULL directory is a different directory; it could not have loaded the smoke's stale cache.
4. **The FULL run computed its pass from scratch.** `_start_marker.json` = 2026-08-12T22:49:29Z,
   34 seconds AFTER the smoke's metrics were written (22:48:56). Its `_pass_cache.npz` has mtime
   22:53:04 — and `save_pass_cache` is called **only** on the `cache_hit=False` branch (lines
   517-520). A cache hit never rewrites the cache. Heartbeat confirms a genuine 50-unit computation,
   22:49:43 → 22:53:01, `pass_elapsed_s` 208.99 of 216.87 total.

**Reproducibility — recomputed today.** `scratch/recheck_context_vector_flip.py` reloads the
persisted FULL cache and re-derives the flip rates through the cell's own scoring path:

| arm | recorded | recomputed today |
|---|---|---|
| REAL | 0.782962 | **0.782700** |
| SCRAMBLE_SENT | 0.998427 | **0.998427** (exact) |
| SCRAMBLE_WORD | 0.994758 | 0.994495 |
| LESION_RANDOM | 0.998952 | **0.998952** (exact) |
| D(SCRAMBLE_SENT − REAL) | +0.215465 | **+0.215727** |

The REAL delta of 0.00026 is explained: my run resolves **892** eligible anchors where the original
resolved **898**, because commits landed since 2026-08-12 (`0db7cfdaa`, `7a708eff3`, `525e24d68`)
touched `closed_class_lexicon` / `reading_grounding_loop`, which supply `is_eligible_meaning`. A
6-anchor change in the eligibility filter moves the headline by 0.0003 — that is robustness, not
drift.

**Second independent reproduction already existed.** `notes/landed_vet_readout_fix_v1_2026-08-12.md`
(hdi_skunkworks, AUDIT-ONLY) performed a full independent recompute from the same
`_pass_cache.npz` with its own scoring code and records *"the external anchor is upstream's
published flip 0.782962, reproduced"* — plus 20+ further quantities identical to 6 decimals.

**VERDICT: the claim STANDS.** flip REAL 0.7830 vs SCRAMBLE_SENT 0.9984, D = +0.2155 with
CI95 [+0.1982, +0.2332] and 100% of 2,000 cluster-bootstrap replicates above zero, against the
pre-registered CONTEXT_CARRIES_SIGNAL band of D >= 0.10. Three independent nulls (SCRAMBLE_SENT,
SCRAMBLE_WORD, LESION_RANDOM) agree; the result replicates at smoke scale (D = +0.2287); and the
D >= 0.10 band was **not** among the amended ones (amendments A1/A2 touched the ceiling guard and
the trace-sum criterion, both disclosed in prereg sec 13 with unamended outcomes preserved in
`prereg_literal_*`).

**Correction to the record, offered without softening the underlying process finding:** the denial
audit's own remediation — *"settling it requires a clean-slate re-run of `exp_context_vector_signal_v1`
(smoke)"* — would validate the SMOKE figure (0.7666), not the banner figure (0.7830). The banner
figure needs no such re-run: it comes from a separate directory created after the smoke completed,
with a cache provably written by the fresh-compute path. The audit was right that a precondition was
dropped and undisclosed, and right to say contamination was not demonstrated; it was wrong to link
that episode to the banner number.

**Caveats that remain, unchanged by this verification:** the cell runs the arm-A path (8,282
encounters / 4,467 lemmas) not arm B's population; it is one deterministic pass with no seed axis;
and `wire_status: MEASUREMENT_ONLY_NO_WIRE` — it is a diagnosis, not a capability.

---

## 5. GROUNDED WELL, THEN PARKED OR SUPERSEDED — with revival criteria

| asset | status | revival criterion (verbatim where recorded) |
|---|---|---|
| `exp_visual_grounding_coherence_v1` (CLIP→FHRR, 20 words) | **VET-upheld chain-grade, PARKED, never registered** | none written. Its own named follow-up — *"bind into concept-atoms"* — was never done. It never passed the WIRE-or-SHELVE gate in either direction: the exact limbo the gate exists to prevent. |
| `exp_image_hd_encoder_digits_v1` (substrate-native HDC) | PASS, never pointed at words | held as "cell 2, optimize-then-nativize" in `notes/scope_visual_grounding_early_reader_words_substrate_native_2026-07-18.md`; that cell was never written. The only asset whose algebra already matches the substrate. |
| Lancaster + Brysbaert sensorimotor norms (39,707 / 39,955 rows) | **SHELVED 2026-08-13** as a filter | *"(a) A read-out is achieved that produces a materially higher MEANINGFUL rate. (b) Sensorimotor grounding is needed as a **generative** anchor rather than a filter — with a mechanism that **proposes** candidate bindings rather than **scoring** pre-existing ones."* Criterion (b) is live and the two image cells above are structurally proposers. |
| `three_tier_loop` cross-source corroboration | HARD_FAIL | **source thinness, not mechanism**: needs >=4 independent databases; max observed 3. |
| `word_acquisition_loop` | `built_measured_HARD_FAIL_shelved_2026-08-06` | two-condition numeric criterion in the registry row. |
| `working_overlay_situation_reader` | SHELVE | *"revive when a narrative/multi-sentence reading pipeline is built, OR the self-learning-loop's STRUCTURED_EXTRACT arm."* |
| F2 (`anchor_center`/`anchor_scale`) | **SHELVE** — VET overturned it | *"a retention-matched F2 arm… showing >= 0.05 residual with a paired CI excluding 0."* Current measurement −0.004 (FIXED), +0.032 (HURTS, GROWING). |
| F1+F3 read-out fix | WIRED **default-OFF** (`192521a7f`) | F3 passes VET at −0.168 matched-retention; caveat that per-episode freeze is self-tested, never exercised live. |
| Warriner VAD (13,916), Kuperman AoA (51,716) | on disk, **no consumer anywhere** | not grounding assets. AoA may serve as a curriculum-ordering signal. Listed so nobody counts them as grounding. |
| Binder 2016 (535 words × 65 dims) | headline cell **never completed a full run** (smoke only) | smoke is a recorded negative (context, not relations, carried the signal); 0 of 2,264 WorldTree items fully Binder-grounded, ~6% coverage. |
| 117,642-sentence OpenStax corpus | **NOT yet ingested** | — |

---

## 6. CONTRADICTIONS — named, not smoothed

1. **"Expository text is 3.3x better" vs "the corpus swap bought nothing."**
   readout_v1 recorded 52.94% vs 16.05% M+R (Fisher p=0.0024, n=17) as VERIFIED; text_vs_mechanism
   returned 30% vs 24% (p=0.6529, OR 1.36) on matched N=20,394 sentences/arm.
   **Better evidenced: the refutation.** It is pre-registered, blind, matched-N and one-variable;
   the prior was a post-hoc slice chosen after seeing the buckets, and its 95% CI (0.28–0.77)
   contains the replication's 0.30. Resolved correctly and in the right direction.

2. **`pipeline_status` contradicts the live path in BOTH directions.**
   3 rows claim `WIRED_AND_PIPELINE_USED` for modules absent from the runtime closure
   (`concept_encoder`, `goal_owner_select` ×2); 19 pairs claim unreachable while measurably
   reachable — including `reading_grounding_loop` itself, the pipeline entry point; and 13 live
   modules have no row at all, including `grounding_acquisition_loop`, one of the two entry points.
   **Better evidenced: the runtime `sys.modules` trace.** The registry field is unreliable for
   grounding-reachability questions and should not be cited as one.

3. **The forensic denial audit vs the artifact.** §4. The audit's narrow claim
   (precondition dropped, undisclosed) is correct and I do not dispute it; its implicit linkage of
   that episode to the 0.7830 banner figure is wrong, because 0.7830 is the FULL run and the denial
   touched the smoke, whose figure is 0.7666. **Better evidenced: the file timestamps, the
   per-output-dir cache logic, and two independent recomputes.**

4. **Apparent three-tier count mismatch — NOT a real contradiction.**
   `system_accounting` lists 5 landed HARD_PASS for the three-tier stack; a directory sweep of
   `*three_tier*` finds only 3. The other two (`exp_gap_driven_reader_controlled_v1`,
   `exp_state_of_mind_relevance_gather_reasoning_union_v1`) are differently named and both verified
   HARD_PASS off disk this pass. `system_accounting` is right; a name-prefix sweep undercounts.
   Recorded so it is not "discovered" again as a discrepancy.

5. **`grounding_asset_inventory` says the norms are "UNWIRED"; the registry says `WIRED`.**
   Both are right at different granularities: `integration_status: WIRED` (module dependency)
   with `pipeline_status: WIRED_BUT_NOT_PIPELINE_REACHABLE`. Practical consequence is identical —
   nothing on the live meaning path calls them.

---

## 7. WHAT I COULD NOT VERIFY

1. **I did not re-run any experiment end-to-end.** The cell
   `exp_context_vector_signal_v1.py` has no `--output-dir` override (`_output_dir(run_mode)`,
   line 942), so a re-run would OVERWRITE the artifact under audit. I recomputed from the persisted
   cache instead. That verifies the scoring path and the recorded numbers; it does **not**
   re-verify the reading pass that produced the cache.
2. **The VISION VET (a6ae09b4 / atom 29310) is reported-not-verified.** Its "UPHELD" status and the
   LOO-robust rho range come from narrative in the 07-22 BACKUP archive; I did not open the atom.
3. **The v6/v6.1/v6.2 predicate hand-scores have NO recorded floor.** 94% is precision without a
   control arm. It should not be cited alongside the v5 64%, which does have an 8% floor.
4. **Single-judge, single-sitting risk across the whole hand-score line.** The one reliability
   datapoint available is favourable — the same 50 CONTROL rows scored blind in two separate
   sittings returned identical marginals (1/12/37) — but that is rate stability, not item-level
   agreement, which was never recorded.
5. **I did not enumerate all ~150 `data/exp_grounding_*` directories individually.** Coverage here
   is: every family named in the task, plus the perceptual/sensorimotor inventory, plus everything
   surfaced by the two enumeration sweeps. A grounding result under a name none of those matched
   could exist.
6. **I did not assess whether wiring any unwired capability would help the live path.** No cell
   imports both the reading loop and the three-tier loop; a benefit claim in either direction would
   be speculation.
7. **`Glob` was not used** (standing false-negative warning). All discovery used `Grep`, `ls`+`grep`
   on directory listings, and `Read` with absolute paths.
