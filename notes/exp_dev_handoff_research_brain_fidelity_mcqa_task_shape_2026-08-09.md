# exp_dev hand-off -- research: MCScript2.0 MC-QA architecture shape (cluster-prototype-and-score is a DEVIATION)

**Filed-by:** research sub-agent, 2026-08-09.
**Trigger:** `notes/research_brain_fidelity_mcqa_task_shape_2026-08-09.md` -- Director-requested deep-VET
audit of the MCScript2.0 HARD_FAIL (`data/exp_mcscript2_real_benchmark_validation_v1/metrics.json`,
verdict HARD_FAIL, real_final=0.5538 vs baseline=0.5859). Finding: the shipped cell's answer-SCORING stage
(score each MC candidate by cosine against a scenario-CLUSTER's bundled bag-of-words prototype, built from
dozens-to-hundreds of OTHER tellings) is a literature-confirmed DEVIATION from the brain's actual
comprehension-for-QA shape (Kintsch construction-integration; Zwaan event-indexing; Bower/Black/Turner's
explicitly-tested-and-confirmed "Partial Copy" staged model; Baldassano schema-scaffold-not-substitute
neural evidence) -- all converge on "score against the passage's OWN specific content first, generic
schema/script as gap-filling fallback only, never the primary signal." The disk-measured numbers already
confirm the predicted harm: on every pass the mechanism is active, `covered_text_baseline_acc` beats
`covered_system_acc` by 1.5-3.3pp on the identical covered questions, and "degradation with exposure" is
exactly the growing coverage of that per-question-worse signal (pass 1 = 0% coverage = exact baseline
match; pass 5 = 98% coverage = full harm realized).

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed regardless
of pause state per research-role convention -- it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable
bands, context pointers) -- exp_dev owns exact implementation (exact extraction-slot count, exact cell
structure, exact scoring-weight formula for the staged fallback, seeds).

## Anchor candidates (rank-ordered)

### 1. `exp_mcscript2_passage_own_content_rescore_v1` (primary, do this FIRST -- near-zero cost, isolates the variable)

**Anchor pointer:** research note's "Cheap decisive test" section + Prediction 1.

**Substrate-product reading:** this is a pure re-scoring pass over ALREADY-COMPUTED vectors -- no new
corpus read, no re-run of `grow_and_track`/`match_or_spawn`. It isolates the SINGLE variable the theory
predicts matters ("score against the passage's own content" vs "score against the cluster prototype")
while holding keying, coverage-gating, and the guard machinery exactly fixed. If this HARD-PASSes, it
converts the diagnosis from "hypothesis, literature-supported" to "measured, isolated cause" before any
larger rebuild is committed.

**Tier hint:** load-bearing gate -- if this comes back HARD-FAIL (rescoring against passage-own-content
does NOT close most of the gap), the diagnosis in the parent note is wrong or incomplete and the next
drill should look at the coverage-gating logic itself, not the scoring locus.

**Design (from the research note; exp_dev owns implementation details):** In `experiments/exp_mcscript2_
real_benchmark_validation_v1.py`, `eval_dev_accuracy` currently calls `script_decide_cached(inst_id, q_id,
q["answers"], proto, dev_answer_cache)` where `proto = item_context_prototype(library.items[item_id])`
(the matched cluster's bundled prototype, `item_context_prototype` at line ~292). Add a SECOND scoring
pass, gated identically (same `use_script` boolean, same covered-subset membership -- do not change which
questions are diverted), that instead scores with `proto = _bow_np(dev_key_cache[inst["id"]])` (the
CURRENT passage's own bag-of-words vector, already computed by `precompute_dev_caches`, zero extra
compute). Report both `covered_system_acc` (existing) and a new `covered_passage_own_acc` per pass,
per type, alongside the existing `covered_text_baseline_acc` already in the metrics schema.

**Pre-registered bands (Prediction 1, verbatim):**
- **HARD-PASS**: `covered_passage_own_acc` closes >=80% of the measured gap
  (`covered_text_baseline_acc - covered_system_acc`) at every pass 2-5.
- **HARD-FAIL**: closes <50% of the gap at any pass 2-5 -- redirect the follow-up drill toward
  coverage-gating logic, not scoring locus.

### 2. `exp_mcscript2_per_sentence_situation_model_v1` (do after #1 passes -- the real rebuild)

**Anchor pointer:** research note's "Rescue architecture" section, steps 1+4 + Prediction 2.

**Substrate-product reading:** replaces the single whole-narrative bag-of-words keying vector with a
genuine per-passage situation model (Kintsch textbase / Zwaan event-indexing shape): every sentence's
(root-verb, subj, obj) bound as an event into `hdlab.situation_model_accumulate.AccumulateRegister`,
not just the current first+last-sentence 2-slot reduction. This is the direct prerequisite for anchor #3
(script-based inference needs a real per-passage event CHAIN to seed from, not a 2-point summary).

**Tier hint:** MEDIUM-HIGH -- depends on anchor #1 confirming the scoring-locus diagnosis first. If #1
HARD-PASSes, this is the natural next build (mostly REUSE, see Context pointers).

**Design:** extend `hdlab.mcscript_extraction.extract_instance_tuple` (or add a sibling function) to
extract EVERY sentence's (root_verb, subj, obj) via the SAME already-100%-firing `CandidateGenerator` +
`frame_slot_role` front end (Stage 1's own measurement: 150/150 fire rate), not just first+last sentence.
Bind each sentence's event into an `AccumulateRegister` instance per DEV/TRAIN passage (`max_event_slots=8`
already covers MCScript's ~5-7-sentence narratives). Use THIS register (or its bag-of-role-fillers
projection) as the passage-own-content scoring signal from anchor #1, and separately as the seed for
anchor #3's chain-prediction query.

**Pre-registered bands (Prediction 2, verbatim):**
- **HARD-PASS** (MIDDLE_BAND-or-better read): covered-subset accuracy reaches >= `covered_text_baseline_
  acc` parity at every pass (recovers the demonstrated active harm) AND (fix compounds with anchor #4
  below) `n_items_spawned_total` falls within 20% of `n_dev_scenarios`/`n_train_scenarios` (162/195).
- **HARD-FAIL**: fails to reach parity even with the richer per-sentence register -- would mean a deeper
  problem than the coarse-extraction diagnosis (e.g. bag-of-role-fillers still can't out-discriminate
  bag-of-words on this corpus).

### 3. `exp_mcscript2_script_chain_predict_gap_fill_v1` (do after #2 -- tests the harder, genuinely open claim)

**Anchor pointer:** research note's "Rescue architecture" step 3 + "Honest read" section + Prediction 3.

**Substrate-product reading:** this is the anchor that tests whether script-based INFERENCE (not just
passage-grounded scoring) can add INCREMENTAL value beyond what the passage's own text already gives
`TEXT_OVERLAP` -- the genuinely open, harder claim. Uses `hdlab.sequence_memory.SequenceMatrix.
chain_predict` (already chain-grade-certified at depths [1,3,5,7,10], commit a27939c5; already precedented
in a QA context by `experiments/exp_substrate_native_qa_hotpotqa_v1.py`/`v2` -- not a fresh mechanism,
a proven reusable primitive applied to a new content domain).

**Tier hint:** the SPECULATIVE tier of this 3-anchor sequence -- deflated P~0.30-0.35 per the research
note's adversarial read (TEXT_OVERLAP is unusually strong on this specific lexically-grounded corpus;
whether chain-predicted script expectations add signal beyond passage-grounding on the actual 2-way
answer discrimination is genuinely untested). Do NOT skip anchors #1-#2 to jump here -- the honest read
in the parent note is explicit that this is the hardest and least-certain of the three.

**Design:** bind TRAIN per-scenario event sequences (from anchor #2's per-sentence registers) into a
`SequenceMatrix` per recognized script TYPE (or one shared matrix keyed by type-tag, exp_dev's call);
at DEV-scoring time, for candidates the passage's own register (anchor #1/#2 signal) does NOT resolve
(a genuine gap -- exp_dev defines the "does not resolve" threshold), query `chain_predict` seeded from
the PASSAGE's OWN last-known event (not a cluster average) and use the predicted continuation as a
FALLBACK scoring signal, weighted lower than the primary passage-own signal (staged, per Bower/Black/
Turner -- do not let the fallback override a confident primary-signal decision).

**Pre-registered bands (Prediction 3, verbatim):**
- **HARD-PASS**: SYSTEM commonsense accuracy on FULL DEV strictly beats `TEXT_OVERLAP` (0.5859),
  non-decreasing curve across 5 passes, real-edge > scramble-edge (same 3-part gate as the original
  pre-reg).
- **HARD-FAIL**: system accuracy remains <= 0.5859 despite anchor #2 clearing its own HARD-PASS -- this
  would mean script-inference gap-filling adds negligible signal over passage-grounded scoring alone on
  THIS corpus specifically (a different, harder finding than the shape bug anchors #1-2 fix -- report as
  "corpus's lexical-groundedness caps script-inference's marginal value here," not as "mechanism doesn't
  work" generally).

### 4. `exp_mcscript2_keying_capacity_pattern_separation_v1` (parallel-track, independent of #1-3, fixes the SECOND diagnosed deviation)

**Anchor pointer:** research note's "Verdict" section, second paragraph ("There is also a SECOND, related
but separable, deviation...") + the disk numbers (`n_items_spawned_total=35` vs `n_train_scenarios=195`,
mean `item_purity.majority_frac` ~0.20, e.g. `SITEM_0002`: 281 traces, 2.8% plurality-scenario share).

**Substrate-product reading:** independent of the scoring-locus fix -- even a perfect passage-own-content
scorer needs a meaningful "which script type" recognition to know when to invoke schema-level fallback at
all (anchor #3). Currently the CA3/DG keying collapses 195 true scenarios into 35 clusters at full scale,
despite `precheck_a` (a small stratified 2-per-scenario sample) reporting a clean gap=0.1448/auc=0.8818 --
the precheck does not reflect full-corpus RUNNING-cluster dynamics (a cluster's bundled prototype grows
ever-more-generic as more traces accumulate, with no bounded-capacity/pattern-separation constraint
forcing new attractors to spawn once interference gets too high -- an unbounded-superposition pathology,
distinct from the brain's DG-pattern-separated, bounded-capacity attractor dynamics).

**Tier hint:** MEDIUM -- can run in parallel with anchors #1-3; needed before anchor #3's script-type
recognition is meaningful at full scale, but does not block anchor #1 (which needs no keying fix at all)
or anchor #2 (extraction richness is orthogonal to keying capacity).

**Design:** exp_dev's call on mechanism -- options include (a) capping a cluster's `max_traces` before
forcing a new spawn regardless of cosine score (a hard capacity bound), (b) renormalizing/decaying older
traces' contribution to the prototype as new ones accumulate (prevents unbounded genericization), or
(c) recalibrating `novelty_thresh` against a FULL-corpus simulation of the running-cluster dynamics
instead of the current small stratified precheck sample. Measure `n_items_spawned_total` vs
`n_train_scenarios` and mean `item_purity.majority_frac` before/after.

**Pre-registered bands:**
- **HARD-PASS**: `n_items_spawned_total` after the fix falls within 20% of `n_train_scenarios` (i.e.
  156-234 items for 195 true scenarios), AND mean `majority_frac` across GROUNDED items exceeds 0.60.
- **HARD-FAIL**: still collapses >3x past the true scenario count, OR mean `majority_frac` stays below
  0.35 -- would mean the bag-of-words keying signal itself is fundamentally too coarse for 195-way
  discrimination at this scale, regardless of the capacity fix, forcing a richer keying representation
  (e.g. anchor #2's per-sentence register used for keying too, not just scoring).

## Context pointers (files, not summaries)

- `notes/research_brain_fidelity_mcqa_task_shape_2026-08-09.md` -- full synthesis: the brain's actual
  comprehension-for-QA shape (Kintsch CI, Zwaan event-indexing, Bower/Black/Turner staged "Partial Copy"
  model, Baldassano neural scaffold-not-substitute evidence), the FOUNDATIONAL/COMPATIBLE/DEVIATION
  verdict, the disk-measured evidence table, and the honest adversarial read on clearing `TEXT_OVERLAP`.
- `data/exp_mcscript2_real_benchmark_validation_v1/metrics.json` -- the landed HARD_FAIL, including
  `real_arm.dev_accuracy_curve` (per-pass `covered_system_acc`/`covered_text_baseline_acc` breakdown) and
  `real_arm.item_purity` (the keying-degeneracy numbers).
- `experiments/exp_mcscript2_real_benchmark_validation_v1.py` -- `eval_dev_accuracy` (line ~538),
  `script_decide_cached` (line ~528), `item_context_prototype` (line ~292), `precompute_dev_caches`
  (line ~430) -- anchor #1's exact edit points.
- `hdlab/mcscript_extraction.py` -- `extract_instance_tuple` (currently first+last-sentence-only
  reduction, the thing anchor #2 extends), `split_sentences`, `extract_root_verb`, `extract_args` (all
  reusable per-sentence, already firing at 100%).
- `hdlab/situation_model_accumulate.py` -- `AccumulateRegister` (anchor #2's per-passage register,
  already VET-confirmed, atom 29609, `capability_registry` id `situation_model_accumulate_register_organ`
  -- REUSE, do not rebuild).
- `hdlab/sequence_memory.py` -- `SequenceMatrix`, `chain_predict`, `bind_sequence` (anchor #3, already
  chain-grade certified commit a27939c5, already precedented for QA in
  `experiments/exp_substrate_native_qa_hotpotqa_v1.py`/`v2` -- read those two cells before designing
  anchor #3's exact query pattern).
- `hdlab/script_grain_acquisition_loop.py` -- `ScriptLibrary.match_or_spawn`, `_prototype`,
  `calibrate_novelty_threshold` (anchor #4's edit points; `iterative_attractor` import from
  `hdlab.cleanup_family`).
- `data/capability_registry.jsonl` -- query before building; `situation_model_accumulate_register_organ`
  and `sequence_binding` (status `WIRED`, `used_by` includes the two hotpotqa cells) are already
  registered and should be consulted, not reinvented.
- `notes/research_vsa_script_representation_chaining_2026-08-09.md` +
  `notes/exp_dev_handoff_research_vsa_script_representation_chaining_2026-08-09.md` -- same-day sibling
  drill that independently identified `SequenceMatrix.chain_predict` and `AccumulateRegister`/
  `RelationRegister` as the reusable script-chaining substrate; this hand-off supplies WHERE they need to
  sit in the MC-QA pipeline (staged, passage-first) that the sibling drill left open.
- `notes/research_psych_bridging_inference_situation_models_2026-08-09.md` -- Trabasso & van den Broek
  causal-network findings (independent literature lane converging on the same "score against the
  passage's own structure" shape).

## Contract section

- exp_dev owns: exact re-scoring implementation for anchor #1 (single cell vs. added arm to the existing
  cell), exact per-sentence extraction slot count and edge-case handling for anchor #2 (narratives with
  <2 or >8 sentences), exact staged-fallback weighting formula for anchor #3, exact capacity-bound
  mechanism for anchor #4 (hard cap vs. decay vs. recalibration), exact cell/file naming, whether anchors
  ship as separate cells or combined arms of extended cells.
- Research (this hand-off + parent note) fixes: the falsifiable HARD-PASS/HARD-FAIL bands for all 4
  anchors, the mandatory ordering (anchor #1 MUST run and be read before committing to anchor #2's larger
  rebuild -- it is the near-zero-cost isolating test the whole rescue direction hinges on), the staged
  (passage-specific-first, schema-fallback-second, lower-confidence-on-fallback) scoring principle for
  anchor #3 (not exp_dev's to loosen -- letting the fallback override a confident primary signal would
  reproduce the exact "Full Copy" pattern Bower/Black/Turner's 1979 result rules out), and the glass-box/
  no-LLM-at-inference invariant.
- Honest scope note (carry into the pre-reg): anchor #3's HARD-FAIL band explicitly does NOT mean
  "script-based inference doesn't work" -- the research note's adversarial read flags real reasons
  (TEXT_OVERLAP's unusual strength on this specific lexically-grounded corpus) it might fail to clear the
  full gate even after anchors #1-2 and #4 all HARD-PASS. Report a #3 HARD-FAIL as corpus-specific, not as
  a refutation of chain-based script inference generally (which has independent precedent in the hotpotqa
  cells).

## Autonomy declaration

exp_dev decides exact implementation details for all 4 anchors as scoped above. The falsifiable bands,
the mandatory anchor-#1-before-#2 ordering, the staged (not override-capable) fallback principle for
anchor #3, and the glass-box/no-LLM invariant are NOT exp_dev's to loosen or drop without flagging the
change explicitly in the pre-reg.
