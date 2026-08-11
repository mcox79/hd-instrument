# Pre-registration: exp_propara_schema_pattern_completion_v1

**Filed by:** exp_dev, 2026-08-11. **Task source:** director spawn prompt "CONFRONT THE WALL
directly, the brain's actual way" -- build a decisive prototype of SCHEMA PATTERN-COMPLETION
(hippocampal/CA3 attractor completion) for filling UNSTATED participant fates in ProPara process
paragraphs. Direct successor of the frame-activation arc
(`experiments/exp_propara_bridging_frame_activation_v1.py`, commit 459098f52 lineage): that arc's
Option-c (native thematic-role reading) triangulated the residual as an UNMENTIONED-fate
INFERENCE wall -- 61% of oracle-fact participants get NO native effect because their fate is never
locally predicated in text. A reader (however good) structurally cannot read what isn't there.
This cell tests a categorically different mechanism: not READING harder, but COMPLETING a partial
schema instance via VSA attractor pattern-completion, using the process's stored role-filler
structure to source the fate of a participant whose name never appears in the paragraph.

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "schema pattern completion attractor unstated participant fate role
filler binding"` -> top-5 at cosine 0.30-0.35: (1) `pattern_completion` capability_registry entry
(cosine=0.3477, WIRED, path=hdlab/cleanup_family.py+hdlab/iterative_attractor.py, "iterative
noisy->nearest-stored recovery" -- confirms these are the right organs to reuse, not a duplicate
build); (2) a 2026-06-08 sharding note on event-shard retrieval via partial participant cue
(cosine=0.3262, different context: N-ary relation sharding, not process/fate schemas); (3) a
2026-06-11 research-drill section "6.3 Partial Slot Filling (Schema Completion)" (cosine=0.3213) --
a THEORETICAL design note (`bind known slots -> CLEANUP(PARTIAL XOR CODEBOOK) -> schema-guided
completion`) that was NEVER implemented as a cell (no exp_ file, no metrics.json under that name).
**Verdict: novel build, not a rediscovery.** The design note independently converges on the same
algebraic shape this cell implements (partial-bind -> cleanup -> completion), which is corroborating
prior THINKING, not prior MEASUREMENT; nothing on disk has run this mechanism against ProPara or any
real-prose fate-inference task.

## THE MECHANISM (brain-faithful shape, not a task-analog)
A schema (e.g. combustion) = a stored pattern binding ROLE -> FILLER across all its participants
(consumes: {fuel, wood, oxygen, ...}; produces: {ash, co2, heat, ...}; moves: {smoke, heat}). Stored
as an FHRR-family attractor: `Schema_P = bundle(bind(role_vec[r], word_vec[w]) for (r, w) in P)`.
A paragraph activates a PARTIAL query built from what text directly evidences (role-words that
graded-match some paragraph token) -- necessarily a SUBSET of the full schema (some roles/fillers
never textually evidenced). `hdlab.cleanup_family.iterative_attractor` (CA3/DG attractor pattern-
completion, the WIRED organ) completes the partial query to the nearest FULL stored schema. UNBIND
(`hdlab.binding.unbind(completed_schema, role_vec[r])`) recovers the schema's filler-bundle for
EVERY role, including roles/fillers never observed in this paragraph's text. A target participant's
own name-vector is then scored against each recovered role-bundle; if it clears a calibrated
threshold, the participant is assigned that role's fate -- REGARDLESS of whether the participant's
name string ever appeared in the paragraph. This is the crux: fate is sourced from STORED SCHEMA
STRUCTURE via pattern-completion, not from local text evidence.

## Representation choice (HRR real, not FHRR complex) -- justified deviation, disclosed
`hdlab.cleanup_family.iterative_attractor` / `hdlab.iterative_attractor.iterative_cleanup` operate
on real-valued numpy float32 arrays (L2-cosine attractor dynamics); scoring via `state @ cb.T` is
NOT Hermitian-correct for complex64 FHRR vectors (would silently truncate the imaginary part via
`.astype(np.float32)`). Reusing the organ AS-IS (not forking/adapting it) requires real vectors, so
this cell uses HRR (`hdlab.binding.bind`/`unbind` dispatch to circular-convolution/-correlation for
real float32 tensors; `hdlab.bundling.bundle`'s real path = sum + L2-normalize). This is a
representation choice, not a mechanism change -- HRR and FHRR are the same VSA algebra family
(Plate 1995); the brain-fidelity claim is about the BIND-THEN-BUNDLE-THEN-CLEANUP shape, not the
specific complex-vs-real encoding. `N = 1024` (CLAUDE.md project default dimensionality constant).

## Organs reused (disk-checked, not assumed)
- `hdlab.cleanup_family.iterative_attractor` (wraps `hdlab.iterative_attractor.iterative_cleanup`,
  capability_registry id `pattern_completion`, WIRED, "iterative noisy->nearest-stored recovery")
  -- THE completion organ, used for genuine schema completion (not mere nearest-neighbor retrieval).
- `hdlab.binding.bind` / `hdlab.binding.unbind` -- role<->filler binding, real-float32 dispatch
  (HRR circular convolution/correlation).
- `hdlab.bundling.bundle` -- schema/partial-query superposition (confirmed default
  `ModulatorState.recency == 0.0` at import time -> plain sum + L2-normalize, no hidden temporal
  weighting; verified in self-test).
- `experiments.exp_propara_bridging_frame_activation_v1._process_convergent` /
  `_graded_frame_score` / `_graded_role_hit` / `_scramble_kb_processes` (+ its pinned thresholds
  FRAME_SIM_THRESH/ROLE_SIM_THRESH/MIN_FRAME_SIG_HITS/CAND_K/MAX_DONORS/MIN_CONVERGENT_ROLES/
  MIN_CONVERGENT_FILLERS) -- IMPORTED ONLY, that cell is NOT edited (owned by another agent per
  director instruction); reused verbatim for the TRIGGER (which schema is cued per paragraph),
  validated 26x per director's spawn prompt. The candidate-selection GLUE loop (rank by
  `_graded_frame_score`, slice CAND_K, filter by `_process_convergent`, slice MAX_DONORS) is
  re-implemented locally (it was inlined in the frame-activation cell, not factored into its own
  function) but calls the SAME imported sub-primitives, so the trigger stays mechanism-identical.
- `experiments.exp_propara_bridging_knowledge_vs_mechanism_v1._paragraph_precompute` / `_grids` /
  `_prior_lesion_grids` / `_unm` -- UNCHANGED downstream retrieve-validate-advance consumption.
  `_grids`'s shared `_assign` internals already implement DEFAULT-OVERRIDE (bridge facts fill gaps
  relative to locally-extracted evidence; never overwrite a stated fact) -- this is EXISTING,
  previously-validated behavior shared by every other arm in this whole arc (oracle/literal/frame),
  not reimplemented here. `_unm(proxy_arm)` slices the per-STEP `mentioned` mask from `steps_df` --
  this IS the "fate not locally stated at that step" population; the decisive test is scored
  directly on this bucket (no new subset-filtering code needed).
- `experiments.exp_propara_decisive_inference_arm1_oracle_v1._load_split`, `_oracle_event_multiset`,
  `_official_corpus_scores`, `_proxy_scores`, `_arms_must_differ`, `_deterministic_perm`.
- `experiments.exp_propara_bridging_real_kb_sourcing_v1._fact_coverage` -- bonus pair-level
  precision/recall diagnostic vs oracle facts (second, independent measurement of the same claim).
- `experiments.exp_propara_arm2_extracted_structure_v1._load_coref`.
- `experiments.exp_propara_bridging_distilled_kb_endtoend_v1._toks`, `_norm_toks`, `_load_kb`,
  `_ROLE_EFFECT` (role->effect->trigger-verb-class mapping table).
- `propara_trap_check.build_step_rows` -- `steps_df` construction (no classifier-fitting machinery
  needed: this cell drops the majority/BOW/bag-of-states baseline arms entirely, out of scope for a
  mechanism-decisive prototype -- compute-proportionality).
- `propara_process_physics_kb_v1.json` -- UNCHANGED KB content, reused verbatim as the schema
  library's SEED CONTENT (18 hand-vetted process types).

**NOT reused (disclosed):** `hdlab.script_grain_acquisition_loop` (FHRR/complex, 4 fixed
TRIGGER/CONSEQUENT/AGENT/PATIENT roles, not this KB's 3 consumes/produces/moves roles over raw KB
vocabulary) -- the BIND-THEN-BUNDLE PATTERN is ported (same shape: role_vec bound to
content-style filler vector, bundled into an instance/schema register), consistent with that
module's own "PORTS ... the PATTERN, not the bipolar/complex code" precedent for cross-algebra
reuse; `content_phase_vec`/`_seeded_generator` are FHRR-only (complex) so a small real-valued
analogue (`_real_unit_vec`, hashlib-seeded torch.Generator, same PROT-023/F.5 determinism
discipline) is written here rather than importing the complex version and discarding its imaginary
part.

## THE ONE VARIABLE vs the frame-activation / native-roles arms
Per-participant fate sourcing swaps from (a) promiscuous participant-name-vs-role-word graded match
(frame-activation) or (b) text-read thematic-undergoer role (native-roles, Option-c) to (c) VSA
schema PATTERN-COMPLETION: partial query built from PARAGRAPH TEXT tokens (not participant names) ->
attractor completion over the 18-schema codebook -> UNBIND readout scored against the TARGET
PARTICIPANT's own name-vector. The trigger (which process is cued) is the SAME reused
convergence-gated selection; only the per-participant slot-fate sourcing mechanism changes.

## Thresholds and calibration (adaptive_with_discriminator_gate; self-test MEASURES then pins)
`ROLE_SIM_THRESH` (reused from frame-activation, 0.70) gates which text tokens count as "observed"
evidence for the partial query. `COMPLETION_THRESH` is NEW -- self-test empirically measures, on the
REAL KB at N=1024, the cosine-similarity separation between (a) a TRUE (schema, role, filler) triple
recovered via unbind (e.g. unbind(Schema_combustion, consumes_role) vs word_vec("wood")) and (b) two
negative controls: WRONG-ROLE-SAME-SCHEMA (unbind(Schema_combustion, produces_role) vs
word_vec("wood")) and WRONG-SCHEMA (unbind(Schema_photosynthesis, consumes_role) vs
word_vec("wood")). `COMPLETION_THRESH` is pinned strictly between the measured true-triple score and
the higher of the two negative-control scores (values MEASURED@self-test, logged in metrics, not
guessed). If self-test cannot find a clean separation (true score does not exceed both negatives),
this is reported as a mechanism-level finding (HRR capacity/noise at this regime), not silently
worked around.

## Bands (pre-registered BEFORE running smoke; genuinely novel mechanism, first attempt -- modest
ceiling is explicitly fine per director's framing, the point is demonstrating the mechanism fires)
- `SCHEMA_SURVIVAL_HARD_PASS = 0.15` -- schema-completion recovers >=15% of the oracle's per-step
  unmentioned-bucket lift (`(schema_f1 - without_f1) / (oracle_f1 - without_f1)`).
- `SCHEMA_SURVIVAL_HARD_FAIL = 0.05` -- at-or-near-zero recovered fraction -> mechanism does not fire
  above noise.
- `SCRAMBLE_MAX_RETAINED_FRACTION = 0.50` (reused bar from frame-activation) -- scramble-schema arm
  (independent double-permutation decoupling signature-donor from role-word-donor, reusing
  `_scramble_kb_processes` verbatim) must retain <= 50% of the real arm's lift. This is the single
  most important control: if scramble survives, the win is a generic-threshold artifact, not
  genuine schema-content completion.
- `ABLATION_COLLAPSE_MARGIN = 0.02` -- the "observed-only, no completion" ablation arm (unbind/
  cleanup step disabled; a participant only gets a fact if its OWN name is textually mentioned AND
  directly graded-role-matches, i.e. no inference for unmentioned participants) must land within
  0.02 F1 of `without_knowledge` on the unmentioned bucket -- completion is the load-bearing step.
- `LEAK_CEILING = 0.95`, `LEAK_ORACLE_MARGIN = 0.02` (reused from the shared arc constants) --
  schema_f1 must stay below both, else the KB/query construction leaked gold answers.
- `WITHOUT_COLLAPSE_CEILING = 0.60` (reused) -- the ablation/without-knowledge floor must itself be
  a real floor (< 0.60), else there was nothing to bridge in the first place (infra sanity).
- `DEFAULT-OVERRIDE` sanity (not a hard gate, reported): schema-completion's macro_f1 on the
  MENTIONED bucket (`proxy_arm["mentioned"]`) should stay close to `without_knowledge`'s mentioned-
  bucket score, since `_grids`'s shared `_assign` defers to locally-extracted evidence over bridge
  facts (existing, previously-validated behavior, not reimplemented) -- reported as a coherence
  check, not a pass/fail gate (scope of this cell is the unmentioned bucket).

## Controls (all load-bearing, per director's decisive-test spec)
- `prior_lesion`, `without_knowledge` (ablation/floor), `with_oracle` (ceiling) -- unchanged, reused.
- `with_schema_completion` -- the mechanism arm.
- `with_schema_completion_scramble_kb` -- SCRAMBLE-SCHEMA control (decoupled double-permutation,
  applied to BOTH the trigger's candidate-selection signatures AND the schema-vector role-word
  content, mirroring frame-activation's own scramble methodology exactly).
- `with_schema_completion_ablation` -- ABLATION (no completion; observed-only).
- NO-LEAK: the schema codebook, partial-query construction, and unbind readout functions take only
  `paragraphs` (text + participant list) and `kb`/scrambled-kb as arguments -- `para["states"]`
  (gold) and `oracle_facts` are never passed in; structurally cannot leak (same posture as every
  sibling arm in this arc).

## Cell-template mandates (declared)
- `arms_differ_verified`: prior_lesion/without_knowledge/with_oracle/with_schema_completion/
  with_schema_completion_scramble_kb/with_schema_completion_ablation all differ (hash-checked).
- `final_metrics_atomicity: tmp_replace`.
- `except SystemExit: raise` before `except Exception` (no bare except, no BaseException).
- `crlb_n/a`: F1-comparison over a fixed real corpus (ProPara EMNLP18) with an 18-item fixed
  codebook at N=1024 -- capacity is not the limiting factor at this scale (Plate-classical
  N >> 10x*n_items margin); no noise-floor sweep threshold applies. HRR unbind SNR is instead
  empirically measured in self-test (see calibration section) as the load-bearing feasibility check.
- `HP_SCOPE`: {with_schema_completion: [survival_beats_floor, scramble_collapses, ablation_collapses,
  no_leak, arms_differ, decode_ok]}.
- `cardinality_ok`: single split (DEV at smoke, TEST at full -- this run STOPS at smoke per director
  instruction, no full dispatch), one pass; EXPECTED arms fixed at 6.
- per-unit failure-class instrumentation: no bare except anywhere in the cell.
- `calibration_check: adaptive_with_discriminator_gate` (COMPLETION_THRESH self-test-measured, see
  above).
- All numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@.
- self-test constructs the REAL schema codebook (all 18 real KB processes) at N=1024 and runs a real
  `iterative_attractor` completion + unbind readout -- not a synthetic-only branch.
- `progress_logging: print_flush_true`.
- `deterministic_seeding: true` -- all new vectors hashlib-seeded (`_real_unit_vec` via
  `int.from_bytes(hashlib.sha256(...).digest()[:8], "big")`), never Python's built-in `hash()`;
  scramble reuses the already-F.5-compliant `_scramble_kb_processes`.

## Scope discipline (director instruction, honored)
Minimal decisive prototype. Self-test -> SMOKE (DEV split) -> STOP + report. Do NOT dispatch --full
even if smoke HARD_PASSes; that is a follow-up decision for the director, not automatic from this
cell. No edits to `experiments/exp_propara_bridging_frame_activation_v1.py` (owned by another
agent) -- import only.
