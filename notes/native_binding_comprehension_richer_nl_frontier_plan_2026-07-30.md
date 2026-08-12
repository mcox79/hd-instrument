# Frontier build: native-binding comprehension -> richer/naturalistic NL

**Date:** 2026-07-30
**Filed by:** research sub-agent (build-ready design, KB-checked, no child dispatched -- design work only)
**Trigger:** tonight's 3 VET-confirmed native-binding positives (novel-filler-to-known-role 0.97-0.99;
native-VSA zero-shot novel-role, clean 0.65/encoder 0.29; native-VSA cross-slot relational composition
0.855/0.815, swap-gen 0.73-0.77) -- the unifying finding that the substrate's NATIVE algebraic FHRR
bind/unbind, not a learned slot-WM/reader, is the comprehension binder. This note designs the next build
that pushes that binder from templated synthetic sentences toward genuinely naturalistic text.
**Calibration:** P estimates deflated 0.15-0.25 per lit-scan calibration penalty; novel-synthesis P capped
at 0.50 (applied below).

---

## KB-check (what's already known, not re-derived)

- `notes/research_native_binding_compositional_generalization_2026-07-25.md`: TPR/LISA/Smolensky/NVSA
  theory for WHY fixed-bind + linear-readout restores systematicity where a flat MLP hub fails (already
  confirmed empirically tonight in the cross-slot cell). The Lake-Linzen-Baroni MLC counter-datapoint
  (systematicity via training-regime/meta-learning, not architecture) remains the live alternative if
  native binding hits a wall below -- kept as a fallback hypothesis, not re-derived here.
- `notes/WHERE_WE_ARE_NOW.md`: full derivation chain (encoder-fine -> WM-dynamics-collapse ->
  read-conditioning proof -> native-VSA reframe) is CURRENT and load-bearing; this note picks up exactly
  where it stops ("push the native-binding comprehension story onto richer/longer NL").
- Three cells inspected directly (not re-summarized from memory):
  `experiments/exp_selective_overwrite_recall_nl_wm_novel_filler_composition_v1.py` (read-conditioning WM,
  novel-filler-to-known-role), `experiments/exp_vsa_native_bind_zeroshot_role_v1.py` (closed-form FHRR
  bind/unbind, zero-shot novel role, CLEAN vs ENCODER key arms, measured `encoder_key_cosine_mean=0.35`),
  `experiments/exp_cross_slot_relational_binding_v1.py` (2-role AGENT/PATIENT cross-slot relational QBF
  task, `ARM_NATIVE_VSA_COMPOSITIONAL` with role-typed asymmetric bind + threshold-gated cosine match).
- `hdlab/binding.py`: `bind`/`unbind` dtype-dispatch (complex64 -> FHRR elementwise mul; float32 real ->
  HRR circular convolution via FFT); this is the ONLY native-algebra surface, reused unchanged below.
- `substrate_query.sh` generic-term query returned only shallow WordNet-adjacent hits (cosine ~0.36,
  nothing substrate-novel) -- confirms this is genuinely frontier territory, not a rediscovery.
- `python tools/inflight_monitor.py`: all three queues idle (overnight/remote_cpu/local_cpu all
  `running=[-]`, recent terminals are unrelated `failed`/`killed` runs from other threads); NO
  orthogonalizing-projection cell currently in flight anywhere. The "fix is being tested now" mentioned
  in the spawn prompt has NOT yet been filed as a cell -- this note's Step 0 IS that fix, not a
  duplicate of work already running.

---

## 1. THE GAP TO THE NORTH STAR (named precisely)

Reading all three confirmed cells' actual sentence templates (not paraphrase):

```
EVENT_TEMPLATES = ["the {role} was {ent} .", "someone said the {role} was {ent} .",
                    "it seems the {role} was {ent} ."]
QUERY_AGENT/PATIENT = "who is the agent ?" / "who is the patient ?"
PROBE templates    = "is {ent} the agent ?" / "is {ent} the patient ?"
```

This is the actual current "naturalistic" text: 3 syntactic frames, closed 20-entity vocabulary
(`calib.COLORS`), closed 12-word role vocabulary, no coreference, no multi-clause sentences, no
passages longer than one flat event stream. Every confirmed result lives entirely inside this envelope.
Four concrete, independently-named gaps stand between this and "read genuinely naturalistic text ->
bind entities/roles/relations -> answer/converse":

**(a) Templated -> varied NL.** Real sentences vary syntax (active/passive), use pronouns/coreference
("he gave it to her" resolving to named entities from prior context), embed relative clauses, and
express MULTIPLE relations per sentence ("Alice, who gave the book to Bob, then borrowed it from
Carol" = 2-3 role-tuples in one sentence). None of the confirmed cells test any of this.

**(b) Key-orthogonality at scale.** `exp_vsa_native_bind_zeroshot_role_v1` MEASURED
`encoder_key_cosine_mean=0.35` at S_TARGET_TOTAL=15 roles -- the real frozen-v2-encoder role keys are
already far from orthogonal at just 15 roles, which is why `ARM_ENCODER_KEYS` held-out recall = 0.29
(PARTIAL, bounded) vs `ARM_CLEAN_KEYS` = 0.65 (clean synthetic keys). A "many entities/relations"
naturalistic corpus needs dozens of role/relation types plus a much larger open-class entity/filler
vocabulary -- if cosine interference *grows* with vocabulary size (the generic expectation for
un-orthogonalized reps drawn from a shared encoder), this bottleneck gets WORSE, not better, exactly
where richness is needed most.

**(c) Integration -- no pipeline exists.** Each confirmed capability lives in its own standalone cell
with its own bespoke encoder subclass (`RelEncoder`, `base.FrozenV2Encoder`), its own key tables, its
own accumulate/decode loop. There is no single `hdlab`-registered module that: reads a passage -> derives
role/filler keys from it -> binds via native FHRR -> answers an arbitrary entity/relational query. This
is the "wire don't island" gate (capability_registry) not yet passed for ANY of the three confirmed
mechanisms.

**(d) Longer passages / multiple facts.** All three cells track at most 2 named roles (AGENT/PATIENT)
or a single overwrite-slot family; none test a passage carrying >=4-5 independent facts that must be
superposed into ONE FHRR accumulator and later disambiguated without destructive crosstalk (Plate 1995
capacity bounds), nor multi-hop queries chaining two unbind steps.

**Priority ranking (why this order):** (b) is upstream of everything -- it is the one gap already
partially measured (`0.35` cosine, `0.29` recall) and it is a cheap, closed-form, no-retrain fix to test
directly. (a) and (d) are corpus/task-construction work, buildable in parallel with (b) using existing
generator machinery. (c) is the integration step that should happen AFTER (a)+(b)+(d) land individually,
per the "prove text -> shore -> expand" roadmap discipline (don't wire a capability before it's proven at
the harder scale).

---

## 2. STEP 0 (ENABLER, run FIRST, cheap): fixed orthogonalizing projection on encoder role keys

**Why first:** `exp_vsa_native_bind_zeroshot_role_v1` already isolated the exact gap
(`VSA_NEEDS_CLEAN_KEYS` reading if a future run repeats this verdict) -- key-orthogonality, not the
bind/unbind mechanism itself, which is proven. This is a closed-form linear-algebra fix over an existing,
already-measured table (`oc.build_oracle_table`'s context-invariant per-role averaged reps), NOT a
retrain, NOT a new corpus. It should be resolved before spending build effort on richer NL, because if
it fails, the richer-NL frontier experiment's query pipeline (which needs MANY roles/relations, not just
2) inherits a known, already-worse bottleneck.

**Mechanism (fixed, unlearned, deployable without retraining):** Symmetric (Lowdin) orthogonalization of
the role-key MATRIX, not the individual encoder representations. Given the existing S_TARGET_TOTAL x d
matrix `K` of context-invariant oracle-averaged role reps (already built by `oc.build_oracle_table` and
already phase-encoded into FHRR-unitary vectors by `vsa_native_bind_zeroshot_role_v1`'s
`phase_encode_real`), compute:

```
K_orth = K @ (K^T K)^(-1/2)          # symmetric orthogonalization, closed-form eigendecomposition
```

This is the UNIQUE orthogonal matrix minimizing Frobenius distance to the original `K` (Lowdin 1950,
standard in quantum chemistry for orthogonalizing atomic-orbital bases -- exactly the same problem: a set
of correlated basis vectors that need to become orthogonal while staying maximally similar to the
originals, so role-identity structure is preserved, not scrambled). Zero learned parameters; a single
fixed linear map applied once per role-key table. Re-phase-encode `K_orth` rows into complex64 FHRR
unitary vectors the same way the cell already does (z-score + `phase_encode_real`), OR apply the
orthogonalization directly on the phase-angle domain if the complex-unitary constraint fights the matrix
square root (diagnostic to check in the self-test: does `K_orth` retain unit-magnitude-per-component
after re-normalization; if not, orthogonalize the pre-phase-encoding REAL oracle table, then phase-encode
the result -- this is the construction order to build first and unit-test before the full run).

**Cell design (extends `exp_vsa_native_bind_zeroshot_role_v1` in place, ONE new arm, ONE new axis):**

- New arm `ARM_ORTHOGONALIZED_ENCODER_KEYS`: identical to `ARM_ENCODER_KEYS` except the role-key table is
  `K_orth` instead of raw `oc.build_oracle_table` output. All other machinery (gamma tuning, distractor
  table, filler codebook, floors) reused byte-identical.
- New scaling axis (directly tests gap (b)'s "does interference grow with vocabulary size" question):
  re-run the full arm battery (CLEAN / ENCODER / ORTHOGONALIZED / 3 floors) at S_TARGET_TOTAL in
  {15 (existing), 30, 60} roles, by extending `oc`'s role-pool generation (widen `ALL_ROLES` /
  `TRAIN_ROLES_V2`/`HELD_OUT_ROLES_V2` split proportionally, same 2:1 train:held ratio). Report
  `encoder_key_cosine_mean` AND `orthogonalized_key_cosine_mean` at each scale -- this is the single
  measurement that tells us whether the fix survives the scale gap (b) actually worries about.

**Pre-registered bands:**
- HARD-PASS: `ARM_ORTHOGONALIZED_ENCODER_KEYS` `recall_heldout_acc >= ORACLE_MIN(0.50)` on ALL seeds at
  15 roles AND `orthogonalized_key_cosine_mean < 0.15` (near-orthogonal) at 15 roles, AND the cosine
  stays `< 0.25` at 60 roles (degrades gracefully, not catastrophically) -> key-orthogonality is FIXED by
  a cheap fixed projection; the richer-NL frontier experiment (Step 2 below) can scale role/relation
  count freely.
- MIDDLE: orthogonalization helps at 15 roles (`recall_heldout_acc` improves over the un-orthogonalized
  0.29 baseline, e.g. into [0.35, 0.50)) but does not fully clear ORACLE_MIN, OR cosine degrades sharply
  by 60 roles (`>= 0.35`, i.e. no better than today at more roles) -> partial fix, informative; report
  the degradation curve and consider whether the frontier experiment should cap role/relation count at
  whatever scale still clears (interpolate from the 15/30/60 curve).
- HARD-FAIL: `recall_heldout_acc < 0.35` (no real improvement over the un-orthogonalized 0.29) at 15
  roles -> the encoder's role reps carry LESS distinguishing information than their raw cosine suggests
  (the orthogonalization exposes noise, not signal) -> key-orthogonality is not fixable by a fixed
  projection alone; escalate to the deprioritized forward-predictive encoder objective specifically for
  ROLE-KEY separability (a narrower, cheaper ask than the full encoder-objective pivot already ruled out
  for MES).
- INVALID (existing floors apply unchanged): any of `FLOOR_CONTEXTVARYING` / `FLOOR_WRONGKEY` /
  `FLOOR_SHUFFLED_CODEBOOK` fails to collapse -- unchanged construction, already self-tested.

**Cost:** closed-form, no gradient steps, reuses the entire existing cell; new work is ~30-50 lines
(the `K_orth` computation + the 30/60-role pool widening) + one extra arm x 3 scales x 3 seeds. Est.
<15 min CPU wall time (same budget class as the existing cell, which the docstring already bounds at
"<10 minutes" for a smaller arm x seed grid).

---

## 3. STEP 1 (parallel, corpus/task construction): naturalistic multi-relation micro-stories

Buildable in parallel with Step 0 (different files, no shared state) using existing generator machinery
(`exp_selective_overwrite_recall_nl_calib_v1.COLORS` entity vocab, `exp_cross_slot_relational_binding_v1`'s
event-stream + distractor + forbidden-pair-holdout pattern, `exp_selective_overwrite_recall_nl_wm_
roleseparated_v1.FrozenV2Encoder`).

**Corpus design -- "Naturalistic Case-Role Micro-Stories":**

- **Role set:** widen from 2 (AGENT/PATIENT) to a Fillmorean case-grammar set of 5:
  AGENT, PATIENT, RECIPIENT, INSTRUMENT, LOCATION (a standard, well-studied semantic-role inventory --
  not an arbitrary widening; this also directly feeds Step 0's 30-role scaling test if combined with
  multiple relation TYPES, e.g. give/take/move/build each with their own 5 case-roles = up to ~25-30
  distinct role-slots, matching Step 0's 30-role scale point).
- **Syntactic variety (the actual "richer NL" lever, gap (a)):** for EACH (relation-type, role) pair,
  author 4-6 template FRAMES spanning real syntactic variation, not just lexical synonyms:
  - Active SVO: "{agent} gave {patient} to {recipient} using {instrument} at {location} ."
  - Passive: "{patient} was given to {recipient} by {agent} ."
  - Relative-clause: "{agent}, who was at {location}, gave {patient} to {recipient} ."
  - Pronoun/coreference: introduce entity by name in sentence 1, refer to it via he/she/it/they in
    sentence 2-3 within the same passage (resolved by nearest-antecedent -- a real, if simplified,
    coreference phenomenon; this is the single biggest novel-to-this-KB linguistic feature and should be
    built + unit-tested FIRST as its own micro-check: given a 2-sentence passage with a pronoun, does the
    query pipeline correctly bind the pronoun's referent, not a nearby distractor).
  - Cleft/topicalized: "it was {instrument} that {agent} used to give {patient} to {recipient} ."
  This is 4-6x the syntactic surface area of the current 3 near-identical templates, while staying
  entirely closed-vocabulary and generator-constructible (no external LLM, no bolt-on parser -- every
  template is a hand-authored string format, same discipline as the existing `EVENT_TEMPLATES`).
- **Multiple facts per passage (gap (d)):** a passage = 3-6 sentences, each instantiating one
  relation-type with its role-fillers, interleaved with distractor sentences (reusing the
  `N_DISTRACT_EVENTS` pattern) and, for a subset of entities, an OVERWRITE (the same entity plays a role
  in an EARLIER sentence, then a role-filler is updated later -- reusing the proven Selective-Overwrite-
  Recall "most-recent-wins" construction, now embedded in multi-sentence prose instead of a bare event
  stream).
- **Reuse, not rebuild:** entity vocab = `calib.COLORS` (20, extendable to 40 for the higher-vocab arm);
  encoder = `base.FrozenV2Encoder` subclassed with this cell's own closed-sentence set (same pattern as
  `RelEncoder` in `exp_cross_slot_relational_binding_v1`); forbidden-pair held-out-combination scrubbing
  = reuse `gen_stream_train`'s `forbid_pairs` rejection-sampling pattern verbatim.

**Construction self-check (build + unit-test before any binding logic):** a coreference-resolution
ORACLE (ground-truth antecedent index, known by construction since the generator wrote the pronoun) must
be threaded through the batch builder alongside the surface sentence -- this is NOT solved by the model,
it is SUPPLIED as part of the task's known structure (per the "supplying knowledge/data is OK, supplying
the reading MECHANISM is forbidden" invariant: the antecedent-resolution ANSWER is task metadata for
scoring, exactly as `ex["final_agent"]` already is in the cross-slot cell; the model still has to bind
the PRONOUN's token position to the right entity vector using its own reps, it is just not additionally
asked to invent coreference-resolution from scratch on this first pass).

---

## 4. STEP 2 (THE HIGHEST-VALUE NEXT EXPERIMENT, gated on Step 0's verdict): richer-NL binding + query cell

**Design: `exp_native_binding_naturalistic_multirelation_v1`** (build-ready name; sequence AFTER Step 0
lands, using whichever key table Step 0's verdict selects -- orthogonalized if HARD-PASS/MIDDLE,
un-orthogonalized encoder keys with an explicit smaller role-count cap if Step 0 HARD-FAILs).

**Pipeline (the integration piece, gap (c), built as the reusable module this time):**

```
passage (Step 1 corpus) --frozen v2 encoder (base.FrozenV2Encoder, UNCHANGED)--> token reps
  --pca_whiten conditioning (rc.Conditioner, proven necessary lever from the read-conditioning result)-->
  conditioned reps
  --role-key derivation: context-invariant oracle-averaging (oc.build_oracle_table pattern) PER
    (relation-type, case-role) pair, THEN Step 0's orthogonalizing projection K_orth-->
  role-key table (30-ish keys)
  --for each event sentence in the passage: extract filler vector (read-conditioning's proven
    role_query attention-over-tokens extraction, OR pooled entity-mention rep -- ablate both as a
    one-variable arm, since read-conditioning proved token-level extraction generalizes ITEMS while
    pooling does not (WM_NL_CANT_LEARN finding) -- use the WINNING extraction method, do not re-litigate)
  --native FHRR bind(role_key, filler_vec), recency-weighted superposition into ONE passage accumulator
    (hdlab.binding.bind, gamma tuned per Step 0's convention, TRAIN-only, zero held-out leakage)-->
  passage memory vector h
  --query dispatch by query TYPE (three types, testing three separate confirmed capabilities at once):
    (1) NOVEL-FILLER query: "who is the {role} of {relation}?" where the correct filler is an entity
        introduced ONLY via a pronoun/paraphrase never seen in that surface form during training
        (extends the PROVEN read-conditioning novel-filler result into the native-VSA accumulator
        instead of the learned WM -- this is a genuinely new combination, not yet tested: does
        UNBIND-then-decode also handle an entity whose SURFACE FORM at binding time was a pronoun, not
        the entity's name-token?).
    (2) RELATIONAL query (who-did-what-to-whom, extended from 2 roles to 5): unbind(h, role_key) then
        threshold-gated cosine match against a probe entity, exactly the cross-slot cell's proven
        mechanism, now over 5 case-roles and multiple relation-types superposed in the SAME accumulator
        (tests crosstalk/capacity, gap (d), directly).
    (3) MULTI-HOP query ("who received the item that {agent} gave using {instrument}?"): TWO chained
        unbind steps -- unbind(h, INSTRUMENT_key) to confirm which relation-instance is being asked
        about (disambiguation if instrument is reused across relation-types), then unbind(h,
        RECIPIENT_key) for that same relation-instance's recipient. This is the genuinely novel
        capability this cell adds beyond tonight's three confirmed results -- chained/compositional
        retrieval was previously only characterized for STORAGE (Probe 10, 07-25 note), never for
        multi-hop QUERY over a naturalistic passage.
```

**CAN-FAIL floors / fair baselines (mandatory, not optional):**
- `PER_SLOT_BASELINE` / `MAJORITY_NONE_BASELINE`: reused verbatim from the cross-slot cell's construction
  (predict ground truth ignoring the probe; always predict NONE) -- must land near the construction-
  determined ~50% (or 1/N_ROLE) ceiling, never near the genuinely-relational target.
- **Pooled-reader baseline (the MES-lesson control, mandatory given tonight's whole-sentence-attention
  scare):** a frozen linear probe over the WHOLE-PASSAGE pooled encoder rep (mirrors the MES calibration's
  BGE-whole-sentence reader). Per the `notes/WHERE_WE_ARE_NOW.md` MES finding (`random-init whole-sentence
  = 0.80 >= trained` -- reservoir-decodable via position-embeddings/attention for SHORT in-window text),
  THIS floor must be checked BEFORE trusting any positive result: if the pooled reader ALSO clears the
  relational/multi-hop query types, the corpus is reservoir-decodable and not actually testing binding
  (same trap that hit MES). Build this floor FIRST, same order-of-operations lesson as MES's calibration
  (`db39c1082`), and only proceed to the native-VSA arm once the pooled reader is confirmed to fail on
  relational/multi-hop (it may still pass on simple single-relation queries, which is fine and expected --
  the discriminating queries are specifically (2) and (3) above with >=2 superposed relation-instances).
- `FLOOR_WRONGROLE` / `FLOOR_SHUFFLED_CODEBOOK`: reused verbatim from both existing native-VSA cells.
- **NEW floor for the coreference feature specifically:** `FLOOR_RANDOM_ANTECEDENT` -- bind the pronoun
  occurrence's filler using a RANDOM other entity from the passage instead of the true (construction-
  known) antecedent; if this floor does NOT collapse relative to the true-antecedent arm, the pipeline is
  not actually using the pronoun-to-entity binding at all (the query answer might be reachable some other
  way, e.g. via the entity's most-recent OTHER mention) -- report and fix the construction before
  interpreting main results.

**Pre-registered bands (mirrors the cross-slot cell's convention, all fixed before running):**
- HARD-PASS: native-VSA arm clears `PROVEN_MIN(0.80)` on (1) novel-filler-via-pronoun, (2) relational
  (5-role), AND (3) multi-hop query types, on BOTH seeds, WHILE the pooled-reader baseline and all
  can-fail floors stay at/below their respective chance-adjacent bands on the SAME query types -> native
  binding demonstrably comprehends genuinely-varied NL across all three confirmed-capability axes at
  once -- the frontier claim is earned.
- MIDDLE: (1) and (2) clear but (3) multi-hop does not (or vice versa) -> report which capability
  survives richer NL and which does not; this is itself a valuable, precisely-localized finding (e.g.
  "single-hop native binding survives naturalistic variation; multi-hop chaining does not" would name
  the NEXT gap precisely, rather than a vague "richer NL is hard").
- HARD-FAIL: native-VSA arm stays at/below `GAP_MAX(0.55)` on ALL THREE query types (floors correctly
  collapsing, task valid) -> the syntactic-variety + pronoun-coreference load defeats native binding even
  with orthogonalized keys; report which specific NEW feature (pronoun binding vs passive-voice role
  extraction vs 5-role capacity vs multi-hop chaining) drove the failure via the floor/ablation battery,
  do not report a single undifferentiated "richer NL failed."
- INVALID: pooled-reader baseline ALSO clears PROVEN_MIN on the relational/multi-hop query types (the
  reservoir-decodable trap recurring) -> fix construction (add more distractors / lengthen passages /
  widen role-set) before interpreting the native-VSA arm at all.

---

## 5. HONEST RISK (where this most likely breaks)

**Most likely failure point: role-key derivation from genuinely varied sentences (gap (b) meets gap
(a)).** The context-invariant role key is built today by AVERAGING a probe sentence's rep across a small,
fixed set of near-identical TEMPLATE occurrences (`oc.build_oracle_table`'s `n_ctx_per_role` construction
-- currently ~3 templates x role). Averaging over 5-6 SYNTACTICALLY DIFFERENT frames (active, passive,
relative-clause, cleft, pronoun-mention) is a much harder ask for the frozen MLM encoder: this is exactly
the encoder's already-measured weakness (`WHERE_WE_ARE_NOW`'s "frozen v2 MLM encoder produces GLOBALLY-
ENTANGLED token reps" finding, cross-leak ~0.99 in the earlier NL binding thread) applied to a NEW axis --
not slot-vs-filler entanglement this time, but role-identity-across-syntactic-frame entanglement. If the
per-role averaged rep's WITHIN-role variance (across the 5-6 syntactic frames) is large relative to its
BETWEEN-role separation, Step 0's orthogonalizing projection (which operates on the averaged table, not
on individual occurrences) will orthogonalize an increasingly noisy centroid -- the projection can make
already-separable roles MORE separable, but it cannot manufacture separability that averaging destroyed.
This is a real, not hypothetical, risk: it is the SAME mechanism-class problem that forced the
read-conditioning pivot (whitening exposes signal, it does not create it) and the SAME literature caveat
already on file (Lake-Linzen-Baroni: architecture-level fixes are not guaranteed sufficient; a
training-regime lever may be needed). Concrete mitigation staged in the design above: build the
coreference micro-check and a "within-role-variance-across-frames" diagnostic FIRST, cheaply, on a small
n, before the full Step 2 run -- if within-role variance already swamps between-role separation at the
diagnostic stage, that is the signal to stop and re-scope (fewer syntactic frames per role, or escalate
to the deprioritized forward-predictive encoder objective, narrowly scoped to role-key separability
rather than the full MES-style objective already ruled out).

**Secondary risk:** capacity/crosstalk at 5 roles x multiple relation-types superposed in one FHRR
accumulator (gap (d)) -- Plate's HRR capacity bounds predict recovery degrades as more items are bundled
into one vector at fixed dimensionality; this is measurable directly (vary passage fact-count 3/4/5/6 as
a swept axis in Step 2, same discipline as the generalization-curve lesson learned on MES) and is a
CHEAPER, better-understood risk than the encoder-representation risk above (mitigable by raising `d` if
needed, unlike the representation-entanglement risk which raising dimensionality does not fix).

**P_deflated:** naive P (Step 2 clears HARD-PASS on all three query types) ~ 0.55 given three independent
already-confirmed component capabilities being COMPOSED (not invented fresh) plus a theory-grounded fixed
projection for the one already-measured bottleneck. Deflated 0.20 for uncharted regime (composing three
mechanisms simultaneously under genuinely varied syntax has no direct precedent in this KB, and the
coreference feature is entirely novel-to-KB) and novel-synthesis cap applied.

**P_deflated = 0.35** for Step 2 (full HARD-PASS across all 3 query types) conditional on Step 0 landing
HARD-PASS or MIDDLE. If Step 0 HARD-FAILs, Step 2's P for the relational/multi-hop query types specifically
drops further (role-count would need to stay capped near 15, undercutting the "many entities/relations"
richness goal) -- **P_deflated = 0.20** for full-richness Step 2 conditional on Step 0 HARD-FAIL (Step 2
would still be worth running in a role-capped form to isolate the syntax-variety axis alone, decoupled
from the scale axis).

**P_deflated for Step 0 alone (the enabler, cheaper/narrower claim):** naive P ~0.55 (closed-form,
theory-grounded Lowdin orthogonalization, reuses fully-built cell). Deflated 0.15 (well-understood
linear-algebra technique, lower uncertainty than Step 2's novel synthesis). **P_deflated = 0.40.**

---

## 6. SEQUENCING (dependency-ordered, build-ready)

1. **Step 0 (fire first, ~15 min CPU, no dependency):** orthogonalizing-projection arm added to
   `exp_vsa_native_bind_zeroshot_role_v1`, 15/30/60-role scaling curve. Gates whether Step 2 can use
   >15 roles / how many role-slots the richer corpus should target.
2. **Step 1 corpus + pipeline module (parallel with Step 0, independent files):** author the
   naturalistic multi-relation micro-story generator + the coreference oracle-threading + the
   pooled-reader floor infrastructure. Build the small coreference micro-check and the within-role-
   variance-across-frames diagnostic (Section 5's mitigation) as the FIRST thing run once the frozen v2
   encoder is loaded against this new sentence set -- before any binding/query logic is trusted.
3. **Decision point:** if Step 0 = HARD-PASS/MIDDLE -> Step 2 uses orthogonalized keys at up to the scale
   Step 0's curve supports. If Step 0 = HARD-FAIL -> Step 2 runs role-capped (<=15 roles, matching
   today's proven regime) so the FIRST richer-NL result isolates the syntax-variety/coreference axis
   cleanly, without confounding it with an already-known key-orthogonality failure.
4. **Step 2 full cell**, gated on (3), with the pooled-reader floor and coreference-antecedent floor
   run and confirmed-collapsing BEFORE the native-VSA main arm is interpreted (same order-of-operations
   discipline the MES calibration thread already had to learn the hard way).
5. **Integration/wire decision (gap (c), capability_registry gate):** ONLY after Step 2 lands a verdict
   (any of HARD-PASS/MIDDLE/HARD-FAIL, all are wire-worthy findings) -- promote the pipeline module
   (encoder -> conditioner -> role-key-derivation -> bind/accumulate -> query-dispatch) into `hdlab/` as
   a registered, reusable comprehension-binding module, not before (avoid wiring an unproven pipeline).

---

## Cross-thread synthesis

Ties together three previously-separate confirmed threads (novel-filler read-conditioning, native-VSA
zero-shot-role, native-VSA cross-slot-relational) into ONE pipeline and ONE corpus, converting three
component proofs into a single integrated comprehension demonstration -- the literal next step the
`WHERE_WE_ARE_NOW.md` synthesis names ("push the native-binding comprehension story onto richer/longer
NL"). Also reopens, in a narrowly-scoped and now-testable form, the `research_native_binding_
compositional_generalization_2026-07-25.md` note's flagged fallback (Lake-Linzen-Baroni training-regime
lever) as the next-drill candidate IF Step 0 and/or Step 2's mitigation both fail on role-key
separability -- not re-derived here, but the fallback path is now concretely wired to a specific failure
signature (within-role variance across syntactic frames swamping between-role separation) rather than a
vague architecture-vs-training-regime dichotomy.

## Substrate-product implications

If Step 2 clears HARD-PASS: the substrate can read a short naturalistic passage with real syntactic
variety and pronoun reference, and correctly answer entity/relational/multi-hop questions about it via
glass-box algebraic binding -- no external LLM, no bolt-on reader, no borrowed embeddings -- which is the
concrete, demoable milestone on the path to "a substrate you can converse with." If HARD-FAIL localizes to
coreference/syntax-variety specifically (with role-orthogonality and capacity both holding), the product
framing narrows honestly to "structured/templated input works today; free-text natural language needs the
[named specific fix]" -- still valuable as a scoped, honest capability boundary rather than a vague gap.

## Citations (verified: reused from 07-25 note, not re-verified here -- generic terms only per
query-privacy discipline, no new external search performed this drill)

1. Fodor & Pylyshyn (1988), Smolensky (1990), Hummel & Holyoak LISA (1997), Hersche et al. NVSA (2023) --
   all already verified in `notes/research_native_binding_compositional_generalization_2026-07-25.md`.
2. Lowdin, P.-O. (1950). "On the Non-Orthogonality Problem Connected with the Use of Atomic Wave
   Functions in the Theory of Molecules." *J. Chem. Phys.* 18, 365. (symmetric/Lowdin orthogonalization,
   K(K^T K)^(-1/2) -- standard closed-form nearest-orthogonal-matrix construction, generic linear
   algebra, no substrate-specific terms used in verifying this citation.)
3. Plate, T. (1995). "Holographic Reduced Representations." *IEEE Trans. Neural Networks* 6(3):623-641.
   (capacity bounds for superposed bind-pairs -- already cited in the wave14e hierarchical-composition
   note, reused not re-verified.)
4. Lake, Linzen, Baroni (2023) *Nature* MLC -- already verified in the 07-25 note, reused as the
   standing fallback hypothesis.

## P_deflated summary

Step 0 (enabler) = 0.40. Step 2 (full richer-NL frontier, conditional on Step 0 landing) = 0.35 (Step 0
HARD-PASS/MIDDLE) or 0.20 (Step 0 HARD-FAIL, role-capped Step 2).

Next-drill candidate if Step 0 HARD-FAILs on role separability even after orthogonalization: narrow,
role-key-specific forward-predictive encoder objective (distinct from and cheaper than the full MES-scale
encoder pivot already deprioritized) -- OR Lake-Linzen-Baroni meta-learning-for-compositionality as a
training-regime-level lever, per the 07-25 note's standing fallback.
