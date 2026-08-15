# STATUS_LESSONS -- the uncapped half of STATUS

Companion to `notes/STATUS.md`, governed by `notes/STATUS_SPEC.md` sec 7.

**Why this file exists.** `STATUS.md` is hard-capped (6144 B when this file was split off;
8192 B since, per `STATUS_SPEC.md` sec 7) so a cold session can read it in one pass. The
never-trim material -- eliminated routes, refuted hypotheses, revival criteria,
and disciplines bought with failed experiments -- grows monotonically and by nature is never
retired, so it will breach any fixed cap eventually. It breached 6144 on 2026-08-13. Rather
than trim it (the failure this whole spec exists to prevent), it lives here, uncapped.

**Contract.** `STATUS.md` sections DO NOT REDO and STANDING DISCIPLINES carry a **one-line stub
naming every entry here** plus a link to this file. A cold session can therefore see that a
route is closed without opening this file; only the *reasoning and the evidence* live here.
Nothing may appear here that is not stubbed in `STATUS.md`.

**Trim rules.** None. Entries leave only when the underlying claim is retracted or superseded on
disk, and then the superseding pointer replaces it in place. Append-mostly.

---

## DO NOT REDO

Each entry: the route, why it is closed, and the evidence that closed it.

1. **Intersection-over-argmax.** Refuted; argmax is already propose-then-verify shaped.

2. **The "40% ceiling".** Was term corruption, not a structural limit. The v5 term-boundary fix
   took it to 64% MEANINGFUL (trajectory 8 -> 38 -> 40 -> 64 on 2092 facts against a >=52% bar)
   -- `notes/director_handscore_b3_v5_termboundary_2026-08-12.md`.

3. **Syntactic bootstrapping as a NEXT STEP.** Blocked, not wrong: there are 0 verb definitions
   in 2092 extracted facts and all 5 extractor patterns are NP-headed, so there is nothing for
   it to bootstrap from -- `notes/verb_definition_gap_2026-08-13.md`. Reopens only after the
   extractor produces genuine verb definitions.

4. **F2, the frequency-corrected pool.** REFUTED as a retention artifact and SHELVED (+0.032
   HURTS GROWING). **Revival criterion:** a retention-matched arm showing a residual >= 0.05
   with a paired CI excluding 0. Measured to date: -0.004 (FIXED), +0.032 (GROWING) --
   `notes/landed_vet_readout_fix_v1_2026-08-12.md:136`.

5. **Same-sentence cosine / PMI as a grounding-quality signal.** Closed.

6. **FHRR superposition to move the 50-pair audit.** The audit is invariant to storage
   representation.

7. **PBV (propose-before-verify hypothesis revision).** Settled HARD_FAIL: P1 0.286 against a
   required >= 0.60, P3 0.071 against >= 0.30 --
   `notes/landed_vet_pbv_hypothesis_v1_2026-08-12.md`, a28cf3b45.

8. **Scoring a read-out cell against v5's 64%.** Refused in the cell's own prereg; the
   comparator figure is 8%. The two measure different things.

9. **Read-out stabilisation (F1+F3) as a route to better meanings.** NULL and floor-limited.
   Grounding quality is the binding constraint, not read-out stability --
   `notes/director_handscore_readout_v1_2026-08-13.md`. F1 is a stability selector only, never
   informativeness (AUC 0.5067); F3 is genuinely stronger than first claimed (-0.168 at matched
   retention, moves `flip_all` -0.0603) but licenses **no quality claim**. Both WIRED default-OFF
   (192521a7f / 8e6c574c5 / 7a708eff3, the last closing an F3 memory leak) --
   `notes/landed_vet_readout_fix_v1_2026-08-12.md`, 8de3a9a20.

10. **Corpus swap news -> textbook as a route to grounded-meaning quality.** REFUTED. Prereg
    matched-N blind (20,394 sentences/arm, 50 rows/arm): TEXTBOOK 0% MEANINGFUL / 30% RELATED vs
    NEWS 4% / 20% -> band MECHANISM_IS_BINDING. The prior post-hoc n=17 claim (bio 52.9% M+R vs
    news 16.1%, p=0.0024) did NOT replicate: 30.0% vs 24.0%, p=0.6529, OR 1.36. Better text buys
    adjacency, not meaning -- `notes/director_handscore_text_vs_mechanism_2026-08-13.md`.

11. **Sensorimotor norms as a filter on the meaning read-out.** SHELVED -- a filter cannot create
    meaning and coverage was never the blocker. Revival criteria in
    `notes/sensorimotor_anchoring_scope_2026-08-13.md`.

12. **Context-conditioned sense selection v2.** HARD_FAIL on both indexes (0.4809 against a floor
    of 0.4634; 0.4449 against 0.4401) -- `notes/context_conditioned_sense_selection_v2_2026-08-12.md`,
    dd58dcf69.

13. **The minimum-grounded-basis derivation.** REFUTED by its own falsification test: once
    controlled for corpus frequency the derived basis is not more concrete, not more sensorimotor
    and not earlier-acquired than the corpus at large -- it is a frequency + topology artefact.
    Independently, the covering problem has no good solution: the definitional graph reaches only
    14% of corpus vocabulary at any number of anchors (graph is flat, max out-degree 54, 917 of
    1,357 source nodes have out-degree 1, 960 of 2,595 nodes have no incoming edge) --
    `notes/minimum_grounded_basis_derivation_and_refutation_2026-08-13.md`.

14. **`genuine_cross_source_corroboration_v1`.** HARD_FAIL was SOURCE THINNESS, not mechanism:
    max 3 sources per gap against `MIN_CONFIRM=4`. Reopens with more sources, not with a
    different mechanism -- `notes/multisource_lookup_wiring_audit_2026-08-13.md`.

15. **`exp_combined_dictionary_consequence_word_learning_tool_v1`.** HARD_FAIL, 0.1944 against
    0.6389, dictionary coverage 6/33.

16. **"The context vector is noise."** REFUTED -- flip 0.7830 vs scramble 0.9984, D = +0.2155
    (79c7521cd, 59479cf82). The defect is downstream in the READ-OUT, which is why that arc
    exists at all. Do not re-litigate the representation as the primary suspect.

17. **Plain co-occurrence AS THE EXPLANATION of the read-out's output.** Refuted: `either_top1`
    is only 0.04 (textbook) / 0.12 (news) -> bands COOC_DOES_NOT_EXPLAIN / COOC_PARTIAL. The
    read-out is meaning-free, but it is NOT a sentence-window PMI table, so "it's just
    co-occurrence" is not the diagnosis --
    `notes/director_handscore_text_vs_mechanism_2026-08-13.md`, RECONCILIATION section.

18. **Role-bound dependency structure ALONE as a route to meaning.** NULL on quality (0% vs 2%
    MEANINGFUL, delta -0.02) -- but it DID bind mechanically, which is why the negative is
    informative rather than a smoke failure: argmax disagreement 97.80%, co-occurrence agreement
    at top5 fell 0.2552 -> 0.0749, band DIVERGED. The structure was really imposed and the
    quality did not move --
    `notes/director_handscore_structured_comparator_2026-08-13.md`, 0db7cfdaa.

19. **Agent frontmatter keys `isolation:` and `background:`.** `isolation:` is ignored.
    `background:` is worse than ignored -- it fails the WHOLE agent definition to load (all five
    `hdi_*` agents vanished, and returned when it was removed). Full detail in `CLAUDE.md`,
    "Agent-teams / frontmatter findings (2026-08-12 night)".

20. **Wiring the voting mechanism.** It scores **0.0248**, below the blind union at **0.0413**
    AND below **its own scramble floor at 0.0496** -- i.e. it is beneath the level its own null
    control reaches, so there is nothing to wire. Compounding this: **no correctness measure
    exists in its cells at all**, so even the 0.0248 is not a quality number. Ranked and rejected
    in `notes/opportunity_map_2026-08-13.md`. Reopens only with (i) a correctness measure defined
    in-cell and (ii) a score clearing its own scramble floor.

21. **Hand-scoring any MEANINGFUL delta while the generator sits at 1-3%** -- and specifically
    the blind sample sitting in `data/exp_anchor_pool_expansion_v1/blind_sample.json`, which the
    cell itself labels `QUALITY_CLAIM: NONE`. This is STANDING DISCIPLINE 1 applied to a live
    artifact: the sample is present, scoreable, and tempting, and scoring it would buy a third
    underpowered-by-floor result. The cell's verdict is read off the RELATION-MATCHED
    known-answer key, never off that sample. Do not score it until the generator clears ~10% M.

22. **The 2-hop bridges.** Ceiling is approximately the scramble floor -- the mechanism's best
    case is indistinguishable from its own null. Ranked and rejected in
    `notes/opportunity_map_2026-08-13.md`.

23. **Wiring definitional extraction as a DIRECT-BANK (opportunity #1).** CLOSED by its own
    pre-registered control. `data/exp_wire_definitional_v1/metrics.json`, `run_mode: full`,
    written 2026-08-13T19:23:33Z, band **`MASS_NOT_CONTENT`**. On held-out B (n=661) the ON arm
    clears its bar -- recall@1 **0.037821** vs OFF **0.007564**, delta **+0.030257** against a
    +0.03 floor -- **but the SHUFFLE arm is IDENTICAL to ON to six decimal places on every
    held-out metric**: availability 0.751891, recall@1 0.037821, recall@5 0.104387,
    availability-conditioned recall@1 0.050302. FREQMATCH delta is **+0.0015** (nothing).
    Band definition, from the cell: "delta >= +0.03 but ON does not beat BOTH controls by >= 0.02".
    **This is a valid control, not a smoke failure**: the manipulation demonstrably worked -- the
    injected-A circularity witness shows ON `live_banked` **394/394 correct** vs SHUFFLE
    **0/394** at identical banked counts, and the OFF regression check passed exactly
    (`observed_n_grounded` 386 == `expected` 386, reference
    `data/exp_anchor_pool_expansion_v1/units.jsonl arm_done|SMALL`).
    **INTERPRETATION: the gain is fact MASS, not fact CONTENT.** Banking 394 definitional facts
    raises availability by +0.53 and drags recall along with it, and banking 394 facts whose
    subject-object pairings have been SHUFFLED does exactly the same thing to six decimals. Nothing
    the definitions actually SAY is being used. This closes the one route that promised to go
    AROUND the comparator by supplying pre-formed facts. **Reopens only if** a mechanism is shown
    that consumes fact CONTENT (a measurable ON-vs-SHUFFLE separation), not fact count. Prereg:
    `preregs/2026-08-13_wire_definitional.md`. The cell makes no quality claim: its own
    `NO_QUALITY_CLAIM` field records that no hand-scoring was performed (correctly -- STANDING
    DISCIPLINE 1).

24. **Distinctiveness WEIGHTING of composed features, as implemented (log-IDF).** REFUTED --
    `exp_distinctiveness_weighted_composition_v1`, `HARD_FAIL_SHAPE`, dbac1ae9c. Held-out
    SimLex-999: weighted-minus-uniform **-0.0175** on B_CSKG (coverage **1.000**, n=999) and
    **-0.0004** on C_CSKG_NOLEXREL (n=639), against a **+0.08** pass bar. Not instrumentation: the
    zero-noise **analytic** arms reproduce the null (B 0.6545 weighted vs 0.6443 uniform; C 0.0826
    vs 0.0790 -- an order of magnitude under the bar, and the sign is not stable across supplies,
    A being -0.0152). Supply A was VOID by construction (coverage 0.035).
    **SCOPE, which must travel:** this refutes the log-IDF WEIGHTING TRANSFORM, **not** every
    distinctiveness transform -- PMI is also logarithmic, and the realised weights span only
    ~1.5-1.75x across shared features (`weight_shared_ratio_p95_p05` 1.5421 / 1.7481 / 1.6346), so
    the manipulation had almost no dynamic range. Reopens with a transform that produces a real
    spread, on a comparator that is not the lookup table of CORRECTION C8.

25. **Extractor-derived DIFFERENTIA (or GENUS) features as the route to word-pair similarity, and
    FEATURE SUPPLY as the binding constraint.** BOTH clauses HARD_FAIL --
    `exp_differentia_feature_supply_v1`, 9825510bf. Stage 1 failed its own coverage gate at **29**
    usable SimLex pairs (bar 50) and correctly diagnosed **DOMAIN, not volume** (the biology
    segment: 1,111 terms -> 3 pairs). Prereg amendment A1 (`64a4ea4c2`, filed BEFORE extraction and
    BEFORE any arm) authorised the supply fix: **169,982** COPULA/GLOSSARY facts from simplewiki in
    ~5 minutes took coverage of SimLex-999 from **2.9% to 35.0%** and 29 pairs to **350**.
    **Supply is therefore no longer the binding constraint and the answer is still no:**
    A_DIFFERENTIA **0.0247**, B_GENUS_ONLY **0.0179**, B_STRICT_GENUS **-0.0464**, D_CSKG_NOLEXREL
    **0.0751**, E_SCRAMBLE **-0.0235**, C_GROUNDED_RAW **0.2759**; A-B **+0.0068** with CI
    **[-0.1179, +0.1395]** (includes 0), and **A <= D**.
    The negative is informative, not a null run: **positive control** arm D reproduced the
    predecessor exactly (rho_weighted **0.0804** at n=639 vs prior 0.0804, `abs_deviation` **0.0**,
    `reproduced: true`); **leak controls excluded 216 of 566** covered pairs before the primary
    (L1 direct leak 145, L2 synonym-statement 113, L3 same-source-sentence 8); and
    `forbidden_conceptnet_edges_in_treatment_arms` / `pattern_restriction_frozen_in_advance` both
    PASS. Do not re-propose "extract more/better features" for this task.

26. **`sign()` as the destroyer of the forgetting kernel -- REFUTED.**
    `exp_forgetting_kernel_signreadout_v1`: prereg+cell `d0c5c906e`, control amendment `a55638a63`,
    results `41da8e454`, metrics `data/exp_forgetting_kernel_signreadout_v1/metrics.json`.
    PRIMARY stream (real, 60 lemmas, simplewiki, live `context_vector_masked`, d=256, t to 1024):
    graded slope **-0.2939** CI [-0.3527, -0.2443]; binarised **-0.3261** CI [-0.3925, -0.2729];
    **CIs overlap**, |dslope| 0.0322 and never above 0.063 on any of the four streams. Power law
    wins on all four (dAIC power-over-exponential **+38 to +94**); exponential never competitive.
    MECHANISM, derived in the prereg BEFORE the run: Benna-Fusi's bound destroys information at
    **WRITE** time, which is what costs an exponent; our `sign()` is a **READ-OUT quantiser on an
    unbounded stored sum**, so it costs a constant factor `sqrt(2/pi)` and no exponent.
    **THE SCRAMBLE CONTROL FIRED AND IT IS THE REAL FINDING:** shuffling ingest order moves the
    slope by **0.0115 (graded) / 0.0106 (binarised)**, i.e. the accumulator is order-invariant, so
    **the curve measures INTERFERENCE and DILUTION, not CONSOLIDATION.** There is no temporal
    structure in the accumulator to consolidate. Real data is flatter than theory (-0.29 vs the
    analytic -0.49) because real contexts are correlated and the shared component does not decay;
    that was pre-registered as the one thing the derivation could not settle.
    **CONSEQUENCE -- the D8 cascade / Benna-Fusi organ is ruled out TWICE:** already
    PARKED-BY-SCALE (crossover ~1e6 synapses against our d = 256..4096) and now **unnecessary**,
    because the exponent it would have supplied is already present in both arms. Do not queue it as
    a capacity win, and do not re-propose "un-`sign()` the read-out to recover the forgetting
    kernel" -- the kernel was never lost.

27. **Rank-1 common-mode removal on the near-neighbour read-out (organ G3).**
    HARD_FAIL_NO_EFFECT -- prereg `32ca72e9c`, cell `917dad83f`, metrics `34b94e8bc`
    (`data/exp_rank1_common_mode_removal_v1/metrics.json`), n=4000, d=256, 2377 anchors.
    **The operation WORKED and the task did not care.** Removal verified: shared-direction energy
    fraction **0.1535 -> 0.0270**, mean pairwise cosine **0.1427 -> -0.0004**. Accuracy
    **0.6980 -> 0.6985**, d = +0.0005 CI **[-0.0043, +0.0053]**, includes 0.
    **The control is what closes it:** removing a RANDOM rank-1 direction gives mu **+0.0005** with
    between-draw sd **0.0012** (K=20) -- statistically IDENTICAL to the treatment, so the treatment
    is perturbation, not decorrelation-that-helps. Sister-term errors unchanged
    (**0.0220 -> 0.0220**, **zero** converted), which is the diagnostic that matters: the arm that
    should have moved did not. Literal mean subtraction HURTS (P5 **0.6767**, -0.0213, CI excludes
    0). The top-PC arm is labelled NOT-BRAIN-LICENSED in the cell and carries no verdict weight
    (cortical top PCs are MEANINGFUL -- Huth 2012 *Neuron* 76:1210).
    **SCOPE:** full-covariance whitening stays PARKED-BY-SAMPLE-SIZE at `O(d^2)` = 65k-16M samples.
    This null does NOT close it in either direction; the cell says so explicitly.

28. **FORAGE_REFUSAL -- tightening the refusal gate as a foraging gain.** The amendment arm of
    `exp_information_foraging_reading_v1` (`3d4761f69`) underperformed the plain FORAGE arm on its
    own metrics: held-out coverage **0.0253** vs 0.0617, grounded facts **383** vs 604, and its
    dominant-source share ROSE to 0.4151 (vs 0.2467). Refusing more does not forage better.

---

## CORRECTIONS TO PRIOR CLAIMS

A correction is a refutation of something this project asserted, so it is never-trim under
`STATUS_SPEC.md` sec 4.3: deleted, the wrong claim becomes attractive again within one session.

**C1. "Availability binds first" is WRONG.** The reading taken from the e2e trace -- that the
candidate set is the binding constraint -- was refuted by the pre-registered
`exp_anchor_pool_expansion_v1`, verdict **`COMPARATOR_IS_BINDING`**. One variable, anchor pool
size. Availability rose **0.199 -> 0.953** (4.8x) and recall@1 moved only **0.0081 -> 0.0333**,
BELOW the pre-declared +0.03 floor. Decisively, **availability-conditioned recall@1 is -0.0060**:
conditioned on the candidate being available, the comparator got slightly WORSE, so the extra
candidates bought nothing the comparator could use. Co-occurrence agreement ROSE **0.075 ->
0.102**, i.e. the larger pool moved the read-out TOWARD the co-occurrence baseline, not away.
**Candidate supply is eliminated as the explanation.** The 386 -> 600 fact count that motivated
the original reading is VOLUME, not CORRECTNESS -- more facts at the same badness. The binding
constraint is the COMPARATOR, and routes that feed it better candidates do not act on it.

**C2. CLIP visual grounding is NOT a glass-box violation.** The invariant bars an external LLM
from OPERATIONAL INFERENCE at runtime. It does not bar external tools from BUILDING the
seed/foundation -- that is exactly the sanctioned FOUNDATION path (MEMORY.md PIVOT: "FOUNDATION =
any external tool, FULL + VETTED; RUNTIME REASONING = glass-box, NO external LLM at inference").
A prohibition asserted here would have closed a legitimate channel for free.

**C3. The 94% predicate score has NO RECORDED FLOOR.** No null/scramble/random-baseline arm was
run against it. It licenses exactly "the parser hands the store a correct fact about 94% of the
time on this arm, blind single-judge, n=50 of 221" and NOTHING comparative -- it is not a
read-out score, and it is not evidence of a margin over chance, because chance was never measured
for it. Do not quote it as a head-to-head number.

**C4. `DGProjection` does NOT fix equidistance.** It fixes INTERFERENCE. The two are routinely
conflated and the conflation makes an already-owned module look like a solution to an open
problem. Removing equidistance requires a channel that is INDEPENDENT IN KIND from the one that
produced the basis (opportunity #2, `notes/opportunity_map_2026-08-13.md`).

**C5. "No final landed encoder exists -- the line was abandoned, not won" is WRONG.** Full
evidence: `notes/encoder_landed_correction_2026-08-13.md`. `hdlab/encoder_retrain_persist.py`
landed at `367a42729` (2026-07-31), is clean at HEAD, and carries registry `gate_decision: WIRE` /
`integration_status: WIRED`; its assets `data/exp_encoder_retrain_persist_v1/ckpt_seed_{7,13,19}.pt`
(3 x ~109 MB, untracked BY DESIGN) all load at runtime and
`experiments/verify_encoder_retrain_persist_loader_v1.py` returns OVERALL PASS. It is the v2
TinyTransformer plus a **minimal top-1-layer unfreeze** (3,153,408 trainable params, 220 steps);
14 of 76 state-dict tensors differ from v2, `tok_emb` byte-identical. It **HAS floors**, contrary
to the prior claim: `exp_encoder_alltype_transfer_v1` (HARD_PASS 08-01, 3/3 types, +0.192 /
+0.150 / +0.320, shortcut controls `global_last` 0.007-0.011 and `most_frequent` 0.057-0.070);
`exp_encoder_alltype_transfer_stress_v1` (HARD_PASS 08-01, +0.050 to +0.231, includes an
INDEPENDENT entity-file harness); `exp_coref_encoder_transfer_v1` (HARD_PASS 08-01, `stage_ENT`
0.724 -> 0.858, all 3 seeds); and the recipe cert
`exp_situation_model_assembly_encoder_retrain_scale_v1` (CLEAN_PASS 07-31, chance 0.05, frozen wall
0.47-0.52 -> 0.830, must-fail full-unfreeze control craters to 0.2916).
**SCOPE CAVEAT THAT TRAVELS WITH EVERY CITATION:** the base is real ARC text but the DELTA and all
transfer evals are the **SYNTHETIC situation-model harness**; naturalistic validation is PENDING;
coref absolute is **0.652 (< 0.70)**. A proven LEVER for entity-addressed comprehension, NOT solved
comprehension. It is **OPT-IN BY DESIGN, not an island**: its docstring states it does not change
any cell's default encoder and callers use `load_improved_encoder()`; the live plug point already
exists at `hdlab/reading_grounding_loop.py` `process_sentence(..., encoder=None)` (def `:1006`,
param `:1011`, default-off selftest `:1945`). The "40 hdlab modules, 0 encoders" runtime trace was
CORRECT about the DEFAULT path and was wrongly reported as measuring EXISTENCE.
Relatedly: **`exp_scale_meaning_learn_arc_heldout_v2` is NOT superseded by `v3_relobj`.** v3's own
prereg (`preregs/2026-07-27_..._v3_relobj.md:76-83`) states the one variable is the training
OBJECTIVE (`L_rel` added to `L_mlm`) and that v2's checkpoint is RELOADED, never retrained, as the
baseline -- so v3's HARD_FAIL means the added objective did not beat v2. **v2 stands:** semantic
AUC 0.6356 vs raw 0.5968, random-init 0.5322, collapse-shuffle 0.4964, popularity 0.4968.

**C6. The synonym-vs-sibling "wall" has NO evidence behind it.** Two independent defects, both in
`notes/encoder_landed_correction_2026-08-13.md`.
(i) **WRONG ARM.** `experiments/exp_diag_learned_encoder_synonym_sibling_deep_wall_v1.py:104-105`
hardcodes `CKPT_PATH` to `data/exp_scale_meaning_learn_arc_heldout_v3_relobj/ckpt_seed_7.pt` --
the `HARD_FAIL_ARCHITECTURE_BOUND` weights. Distinctness proven, not assumed: sha256 differs from
v2 and **all 76 of 76 tensors differ**, max |delta| 0.539. So "trained 0.7064 vs random-init
0.7452" tested neither the v2 HARD_PASS encoder nor the landed asset.
(ii) **SUPERSEDED ANYWAY.** `exp_diag_synonym_sibling_confound_removed_v1` (2026-08-12T03:54Z, 43
minutes after the cell it supersedes) balances concreteness (`conc_z_gap` 1.6022 -> 0.0406) and
reports, at n_syn=26 / n_sib=26: `main_trained` **0.5888**, `main_randinit` **0.4615**,
`main_scramble` **0.5074**. The trained model DOES beat its random-init twin (+0.127). The 0.71-0.75
separation was the concreteness confound the first cell had itself flagged.
Therefore the **"the pooling interface separates synonyms from siblings" framing does not
survive**, and any statement that the successor encoder "learns but loses its edge to a random-init
twin" is WRONG. Honest residual: that cell's headline verdict is
`MIDDLE_BAND_HELDOUT_UNDERPOWERED` -- its DECISIVE (balanced AND held-out) set is n=5/5 against a
declared floor of 8 and does not gate (it runs the same direction: 0.72 / 0.60 / 0.64). So
synonym-vs-sibling is **OPEN and unmeasured at power**, not WALLED. Do not restate it as a wall.

**C7. Two opportunity-map items rest on WRONG NUMBERS** (`notes/opportunity_map_2026-08-13.md`).
Item **#5** (wire `dg_pattern_separation` into `script_grain_acquisition_loop`) quotes the numbers
of the DEFECT it is meant to fix; the fix's own cell **on that task**,
`exp_dg_pattern_separation_mcscript_purity_v1`, is **HARD_FAIL** -- mean purity **0.1013** against
a ~**0.1999** baseline, i.e. below the baseline it was supposed to beat. Item **#6**
(`cls_discrete_budget_consolidate`) is `VET_PENDING` / ISLAND with a **HARD_FAIL wiring smoke, gap
0.000**; it also carries two mutually contradictory registry rows (`VET_PENDING` vs
`ALREADY_WIRED`). Neither is a ranked opportunity as written; re-rank before acting on that map.

**C8. THE COMPARATOR WAS AN EMBEDDED SIMILARITY LOOKUP TABLE.** Unplanned finding of
`exp_distinctiveness_weighted_composition_v1` (dbac1ae9c), and more important than its planned one.
Deleting ConceptNet's **synonym / relatedness (lexical-relation) edges** collapses the comparator
from rho **0.5361** (B_CSKG, n=999) to **0.0804** (C_CSKG_NOLEXREL) on the identical construction,
while **raw sensorimotor** scores **0.3003** on those same 639 pairs. So the comparator's apparent
competence was carried by edges that STATE the answer, not by composed features -- and on the
stripped supply it is beaten nearly 4x by a norm table it does not use. Every future "the
comparator scores X" claim must state whether lexical-relation edges were in the supply.
Corroborated the same night by `exp_near_vs_far_diagnostic_v1`: CSKG-minus-lexrel goes
**significantly NEGATIVE** on the NEAR half (D **-0.2146**, CI [-0.4027, -0.0038], excludes 0).

**C9. EXPERIMENT RESULTS *ARE* SEARCHABLE -- an earlier same-day Director claim that they might
not be is WRONG.** The director_kb's last ingest discovered **7,501 `metrics` sources** (with 9,197
notes and 3,689 preregs), per `data/director_kb_continuous_state.json`
(`last_ingest_per_class_n_discovered`). The KB's own retrieval encoder is **`char_trigram_v1`**
(`tools/director_kb_query.py:87`) -- relevant when judging what a KB miss means: a trigram index
misses paraphrase, so "not found in the KB" is not evidence a result does not exist (this is
STANDING DISCIPLINE 4's sub-rule -- an absence claim requires an enumeration, not a search).

**C10. THE 65.7% TAUTOLOGY RATE WAS AN ELIGIBILITY BUG, NOT A MEANING FAILURE.** The claim that
two thirds of grounded concepts are self-referential `(X, GROUNDED_MEANING, X)` -- carried since
2026-08-12, quoted in `MEMORY.md`, in `SUBSTRATE_STRATEGY.md` PART 1 (C3) and in
`notes/foundation_contents_audit_2026-08-13.md` -- described a **degenerate argmax**, not a
property of the meanings. When the lemma's OWN anchor is left eligible in the open-vocabulary
argmax, the read-out returns it **100% of the time**: this is ANALYTICALLY PINNED, not a
measurement (`data/exp_grounding_readout_known_answer_v1/metrics.json`,
`stage_b.open_vocabulary_readout.tautology_rate_when_self_eligible` = 1.0, with the note stating
the reasoning). That is the whole mechanism behind the legacy store's 2328/3544 = 0.6569 in
`data/foundation/reading_grounding_v1`.
**The current path excludes the pending lemma and emits ZERO tautologies in every arm measured:**
0/384 and 0/369 on the banked arms, `tautology_rate` 0.0 on the 4000-item open-vocabulary arm, and
0.0 in the FORAGE arm of `exp_information_foraging_reading_v1` as well. Fix landed `1b2022522`,
measured `204eba1a0`.
**CONSEQUENCE for the C3 revival criterion (">= 0.10 MEANINGFUL against a recorded floor,
tautologies < 0.10"): the TAUTOLOGY HALF NOW PASSES.** Only the quality half fails, and it fails
by 5.2pp, not by two thirds. Do not re-quote 65.7% as a live number; cite it only as the legacy
store's figure with this cause attached.

**C11. THE "58% COMMON MODE" DOES NOT REPRODUCE, AND 0.5841 WAS A NORM RATIO QUOTED AS A VARIANCE
FRACTION.** `ORGAN_MAP.md` B3 and G3 asserted "more than half the variance is a single shared
direction", and that premise is what motivated build STEP 3. Measured on the live anchor field
(n=2377, d=256, `data/exp_rank1_common_mode_removal_v1/metrics.json` `common_mode_measured`):
- Using ORGAN_MAP's OWN definition `||mean_i a_i|| / mean_i ||a_i||`: **0.3650 GRADED / 0.2997
  SIGN**. The graded figure is close to ORGAN_MAP's own 0.3545; the SIGN figure is **half** its
  claimed 0.5841, on the same definition.
- That definition is a **NORM RATIO, not a variance fraction.** The actual shared-direction energy
  fraction (`mean_i (a_i_hat . u_hat)^2`) is **0.1535**, and **PC1 holds 0.0350** of the centred
  field's variance. So "more than half the variance in one direction" overstates the measured
  quantity by roughly **4x**, and the two numbers were never the same quantity.
The 0.5841 came from `experiments/diag_anchor_field_geometry_v1.py` on 400 concepts x 70 held-out
sentences -- a different, smaller field -- so the discrepancy is partly scope and partly the
definition swap. State which quantity you mean whenever you quote it. `ORGAN_MAP.md` B3 and G3
corrected in place, 2026-08-14.

---

## DIAGNOSTIC READS AND THE CAVEATS THAT TRAVEL WITH THEM (2026-08-13)

Never-trim under `STATUS_SPEC.md` sec 4.7: a read quoted without its caveat becomes a stronger
claim than the data supports, and the strengthened version is what the next session acts on.

**D1. `exp_near_vs_far_diagnostic_v1` (804b02246) reads `NEAR_COLLAPSE`. The honest shape is
MONOTONE DEGRADATION, not a clean collapse.** Read source SPLIT1_TAXONOMIC. Sensorimotor arm C:
pooled **0.2759** [0.1727, 0.3798] -> FAR (n=272) **0.3042** [0.1828, 0.4155] -> NEAR (strict
shared-synset / shared-direct-hypernym siblings, n=78) **0.1245** [-0.0926, 0.3315], null. Symbolic
arms are at chance in BOTH halves (on FAR: A **0.0308**, B **0.0137**, D **0.0992**, none excluding
zero). **Caveat 1: at n=78 the MDE is 0.2116**, so the NEAR null means COULD NOT DETECT, not proven
zero. **Caveat 2: the balanced co-primary split does NOT show collapse** -- SPLIT1B_WN_PATH_MEDIAN
NEAR_G (n=218) is **0.2185** [0.0787, 0.3520], still significant, against FAR_G **0.2559**.
Also from the same run: **no dual-coding separation** (CONCRETE **0.3123** [0.1933, 0.4234] vs
ABSTRACT **0.2612** [0.0257, 0.4688], CIs overlap heavily).

**D2. `exp_encoder_swap_behind_fixed_brain_stack_v1` is HARD_PASS / `REFUTES_USER_CLAIM`, and it
does NOT settle the trained-vs-simple question.** A_tuned **0.6386** vs B_char_trigram **0.0873**,
delta_AB **+0.5513**. But the cell ran on **the encoder's OWN TUNING HARNESS**:
`experiments/exp_encoder_swap_behind_fixed_brain_stack_v1.py:93` imports
`exp_continuous_curriculum_learn_as_you_go_v1 as base_loop` -- the same base loop as the 08-01
transfer cluster -- and takes the assembly loop, the `role_attn` readout and the held-out split from
it. A **neutral-ground test is owed**. Its own **span control** argues the same way: when
localization is GIVEN, all five encoder arms tie at **1.000** (A_tuned, A0_frozen_base,
B_char_trigram, C_ppmi, D_random_init_twin), only E_scramble_floor at 0.0497 -- i.e. what the tuned
encoder buys on this harness is localization, which is what the harness supplies.
**Its results are UNCOMMITTED:** `data/exp_encoder_swap_behind_fixed_brain_stack_v1/metrics.json`
is untracked; only the prereg and cell are committed (`f36ba7626`).

**D3. `exp_information_foraging_reading_v1` is HARD_PASS (`3d4761f69`), and TWO NON-VERDICT ARMS
BEAT FORAGE ON THE SAME METRICS.** Each declared check named its own comparator before the run, so
neither reversal breaks the prereg -- but neither licenses "foraging is the best reader".
- **D2, held-out coverage.** FORAGE **0.0617** vs RANDOM **0.0127** (+3.868 relative; this is the
  declared, load-bearing test and it passes cleanly). **FROZEN scores 0.0743 -- HIGHER than
  FORAGE.**
- **D3, WordNet agreement.** FORAGE **0.3511** vs FROZEN **0.2920** (the declared non-inferiority
  test). **RANDOM scores 0.3864 -- HIGHER than FORAGE.**
- **D4 FAILED outright:** oracle ratio **0.5344** against its 0.70-1.00 band. The organ leaves
  patches EARLY relative to the marginal-value-theorem optimum. Labelled "mechanism check only" in
  the cell, so it carries no verdict weight -- but it is the specific thing to fix next if this
  organ is worked on.
- **Scale, corrected:** the shelf holds **28** readable corpora (`n_readable_corpora`). FORAGE read
  **19** of them and banked from **16**; RANDOM read 28; FROZEN read 4. Any restatement using a
  larger corpus count is wrong.

**D4. THE FROZEN ARM DID NOT REPRODUCE THE 63.9% BIOLOGY SKEW, SO THE H2 LINKAGE IS UNCONFIRMED BY
THIS CELL.** FROZEN read only four corpora (`adv_new`, `bio_new`, `ele_cont`, `int_cont`) and its
dominant DOMAIN is **news at 0.8822**, with biology at **82 of 696** banked facts. It is therefore
not a reproduction of the skewed baseline it was meant to stand in for. What the cell DOES show is
that foraging **diversifies sources** (16 banked-from vs 4; dominant-source-share drop 0.1585).
What it does NOT show is that foraging fixes the biology skew -- FORAGE's own dominant domain is
`textbook_biology` at **0.6325**. Do not cite this cell as evidence on H2.

---

## STANDING DISCIPLINES

Each is a rule bought with a specific failure. The failure count is part of the argument.

### 1. Do not gate a cell on a hand-scored MEANINGFUL delta while the generator sits at 1-3%

**Cost: two complete experiments, both UNDERPOWERED BY FLOOR.**

- `exp_grounding_quality_readout_v1` -- 3 MEANINGFUL rows in the entire 100-row sample. Even the
  most extreme allocation (all 3 in one arm) reaches only 3/50 - 0/50 = 0.06, which is INSIDE
  its own NULL band. It could not have produced a non-NULL verdict at any allocation --
  `notes/director_handscore_readout_v1_2026-08-13.md:31-44`.
- `exp_structured_comparator_v1` -- 1 MEANINGFUL row, max `abs(delta)` 0.02, **5.5x below the
  cell's own declared minimum detectable delta**. Its prereg (sec 4.1) had explicitly claimed to
  have FIXED the previous cell's floor defect. It recurred, and worse --
  `notes/director_handscore_structured_comparator_2026-08-13.md:56-81`.

**The reasoning error to recognise:** "only CONTROL is floor-pinned, so TREATMENT is free to
rise" is not a power argument -- it is a restatement of the hypothesis. If H1 is false the
treatment arm floors too, and the discriminator has no range. *A discriminator whose resolution
is contingent on the hypothesis being true cannot adjudicate that hypothesis.*

**What to do instead.** Until the generator clears roughly 10% MEANINGFUL, do not gate on a
MEANINGFUL delta at all. Gate on **known-answer recall**, or on a **mechanistic discriminator
that has range by construction** (as sec 5 of the comparator prereg did, correctly). At n=50/arm
the MEANINGFUL supply, not the mechanism, sets the measurable range.

**Deletion history.** This entry was deleted from `STATUS.md` on 2026-08-13 during an ad-hoc
byte-shave, on the stated grounds that it carried no file pointer -- while both citations above
already existed on disk. That deletion is the reason `notes/STATUS_SPEC.md` and this file exist.

### 2. Serialize measurement against code change

Happened **2x**. Never dispatch an audit, witness-run or experiment while another agent may
write code it depends on, **including transitive dependencies**. A measurement racing a
concurrent edit describes no single repo state, so its result is not attributable to any
version of the system -- `notes/measurement_layer_drift_2026-08-13.md` sec.8.

### 3. A checker that shares a flaw with the thing it checks makes the flaw invisible

**4 instances in one night:** propose and verify shared one metric; the store and the classifier
shared one stemmer; certification and the code shared one bug; the test suite and the witnesses
shared a naming blind spot. **Consistency is not evidence.** Practices P1-P6 in
`notes/shared_flaw_invisibility_2026-08-13.md`.

### 4. Establish the final landed version before evaluating any subsystem

**SIX instances now, not three** -- and instances 4-6 (2026-08-13, evidence in
`notes/encoder_landed_correction_2026-08-13.md`) are the most expensive to date, because they did
not merely misrate a subsystem: they wrote "this line was abandoned" into the steering docs about a
capability that had LANDED, WIRED, with four HARD_PASS/CLEAN_PASS floors.

**4. An audit declared a whole capability line "abandoned, not won" without ever enumerating the
2026-08-01 cells.** Grep `notes/encoder_lineage_final_2026-08-13.md` for `alltype`,
`coref_encoder_transfer` or `load_improved_encoder`: **zero matches, all three.** The landed module
`hdlab/encoder_retrain_persist.py` (`367a42729`, registry WIRE/WIRED) is OPT-IN by design, so the
audit's runtime `sys.modules` trace -- correct as a measurement of the DEFAULT path -- was reported
as a measurement of EXISTENCE.
**5. A diagnostic measured a checkpoint from a different, FAILED cell.**
`exp_diag_learned_encoder_synonym_sibling_deep_wall_v1.py:104-105` hardcodes the
`v3_relobj` HARD_FAIL weights (76/76 tensors differ from v2), and its result was carried into
STATUS.md as a "wall".
**6. That same diagnostic had already been superseded 43 minutes later** by
`exp_diag_synonym_sibling_confound_removed_v1`, which reverses the sign (trained 0.5888 vs
random-init 0.4615). Nobody checked for a successor before citing it.

**NEW SUB-RULE, because it is the generative cause of all three: AN ABSENCE CLAIM REQUIRES AN
ENUMERATION, NOT A SEARCH.** "I looked and did not find it" is not evidence of absence when the
naming convention is unknown. Every miss above, and every asset in the FLOORED ASSETS section
below, was invisible to a reasonable search: a `_fulldev` directory suffix, 105 MB `.pt` assets
untracked by design, an opt-in module absent from a default-path trace, an implementation filed in
the registry under a different module's name. **Before writing that something does not exist, state
HOW you enumerated and what naming variants that enumeration would have caught** -- `os.walk` over
`data/` and `hdlab/` and assign every entry, per `CLAUDE.md` Evidence discipline sec 2
(enumerate from the filesystem, then reconcile to the registry, never the reverse) and sec 6
(`Glob` returns empty SILENTLY on a bad path -- never trust an empty result).

**The original 3 audits in one day (08-13)**, all inside
`notes/encoder_lineage_final_2026-08-13.md`, judged a superseded or wrong artifact instead of the
final one:

- The S8 brain-fidelity audit dissected `hdlab/concept_encoder.py` (1 commit, 2026-07-02, zero
  hdlab importers, not in the runtime closure) and generalised its inert `learning_rate` to "the
  encoders" as a class. The actual successor, TinyTransformer v2, does learn
  (+0.1034 held-out semantic AUC over a random-init same-architecture twin).
- The capability registry's `scale_win_tinytransformer_encoder` row carries `status:
  validated_chain_grade_best_encoder` / `gate_decision: WIRE`, with its `current_best_for`
  numbers taken from `exp_scale_meaning_learn_arc_heldout_v2.py` (2026-07-27, HARD_PASS) -- but
  its `path` field points at `exp_scale_meaning_learn_arc_heldout_v3_relobj.py`, whose own
  `metrics.json` is `HARD_FAIL_ARCHITECTURE_BOUND` (2026-07-28). The row's status was measured on
  one cell, its path names a different, failed one.
- `hippocampal_encoder` is rated FAITHFUL / `ALREADY_WIRED` (~20 consumers) in the registry, and
  quoted that way without its own retrieval verdict:
  `exp_substrate_spoke3_hippocampal_encoder_smoke_2026-07-03` is `HARD_FAIL_MECHANISM_LOSES`,
  r@5 0.1460 against a char-trigram reference of 0.854 (bar 0.8240) -- it lost to a trivial
  trigram bag by 0.71.

**Rule:** before evaluating any subsystem (fidelity, quality, wire-readiness), first establish
which artifact on disk is the *final landed* one for that subsystem -- check the registry's
`path` against its own `status`/numbers, check the cited cell's own `metrics.json` verdict, and
check for a successor. A rating attached to the wrong version is not wrong reasoning, it is a
wrong target.

### 5. Before gating on a benchmark, check that the BRAIN performs the operation it scores

**Cost: FOUR cells in ONE day**, all optimising **context-free word-pair similarity** --
`exp_wire_definitional_v1` (MASS_NOT_CONTENT), `exp_distinctiveness_weighted_composition_v1`
(HARD_FAIL_SHAPE), `exp_differentia_feature_supply_v1` (HARD_FAIL both clauses), and
`exp_near_vs_far_diagnostic_v1` (NEAR degradation). All four were well-controlled: pre-registered
bands, scramble floors, leak controls, positive controls that reproduced their predecessors
exactly. They failed anyway, and the same day's brain drill
(`notes/brain_drill_encoder_lexical_semantics_2026-08-13.md`, `471798502`) says why: **the brain
never computes a context-free word-word similarity.** Lexical semantics is read out under a
semantic-control system that applies GAIN to context-relevant features; the operation SimLex scores
is not an operation the reference system performs.

**The rule:** before adopting a benchmark as a gate, name the brain operation it corresponds to. If
there is none, the benchmark can be standard, well-controlled, well-powered and STILL measure a
function the reference system never computes -- and a clean answer to that question is worth little.

**Distinct from DISCIPLINE 1, and the distinction is the useful part.** Discipline 1 is about
POWER: those cells could not RESOLVE an answer (the discriminator had no range). These four
RESOLVED cleanly -- for a question that should not have been asked. A power check would have passed
all four. The two failure modes need separate checks: *can this cell answer its question?* and
*does the reference system perform this operation at all?*

Narrative and the full per-cell numbers: `notes/director_evening_digest_2026-08-13.md`.

### 6. Run a POSITIVE / KNOWN-ANSWER arm: it catches measurement defects no arm of interest can

**Cost: two cells in one night would have shipped confident wrong numbers without one. Both were
saved by an arm that was not the arm anyone cared about.**

- **`exp_forgetting_kernel_signreadout_v1` -- the estimator was wrong and only the known-answer arm
  could show it.** The SYNTHETIC arm has an exactly computable curve, so its fitted slope can be
  checked against the truth on the same finite grid. That check exposed **two** defects, disclosed
  as prereg amendments 2 and 3 (`preregs/2026-08-14_forgetting_kernel_signreadout_v1.md:126-150`):
  (i) **SURVIVORSHIP BIAS** -- logging before averaging silently dropped **96 of 1140** synth
  points, all at the large-`t` end that sets the slope; (ii) **PSEUDO-REPLICATION** -- 19 t-points
  x 60 lemmas counted as `n = 1140` independent observations, inflating AIC. **The first run
  returned a confident CI that EXCLUDED the truth.** Neither real-data arm could have revealed
  either defect: on real data there is no truth to compare against, and both arms carry the same
  estimator, so they agree with each other while being jointly wrong (this is STANDING DISCIPLINE 3
  in a new costume -- a checker sharing a flaw with what it checks). The first run's numbers are
  retained under a separate unit-key namespace, not deleted.
- **`exp_grounding_readout_known_answer_v1` -- the positive control is what makes the null
  interpretable.** SELF_RETRIEVAL scored **0.786** (n=299, floor 0.70, `ok: true`), proving the
  retrieval machinery runs end to end on this harness. That is the evidence licensing attribution
  of the AT_FLOOR stage-A result to **MEANING** rather than to plumbing. Without it, "the banked
  meanings are indistinguishable from a random re-pairing" is equally consistent with a broken
  loader, and the cell resolves nothing.

**DISTINCT FROM THE FLOOR DISCIPLINE, and the distinction is the whole point.**
**A FLOOR tells you whether the EFFECT is real. A KNOWN-ANSWER ARM tells you whether the INSTRUMENT
is.** They are independent failures: a cell can have an impeccable scramble floor and a broken
estimator, and the forgetting-kernel cell had exactly that -- its floors and bands were all in
order while its slope estimator was biased. So run BOTH, and say which is which: a floor arm
(*what would a stupid method score?*) and an arm whose answer is already known
(*what does this harness report when the answer is certain?*).

**Also distinct from DISCIPLINE 1 (power) and DISCIPLINE 5 (is this the right question).** The
three checks are: *can this cell resolve an answer?* (power), *does the reference system perform
this operation?* (question), *does this harness report the truth when the truth is known?*
(instrument). Passing any two says nothing about the third.

---

## ENCODER LINEAGE (2026-08-13)

Full investigation: `notes/encoder_lineage_final_2026-08-13.md` (read-only, no code changed).
Stubbed from `STATUS.md` "ENCODER PATH" and STANDING DISCIPLINE 4 above.

> **REFUTED IN PART, 2026-08-13 (later same day) -- see CORRECTIONS C5 and C6 above and
> `notes/encoder_landed_correction_2026-08-13.md`.** A final landed encoder DOES exist
> (`hdlab/encoder_retrain_persist.py`, `367a42729`, WIRE/WIRED, four floors), and the
> synonym-vs-sibling "wall" measured the wrong checkpoint and was superseded 43 min later. The two
> paragraphs below are kept for the record of what was believed and why; do not cite them as
> current. What still stands in them: the DEFAULT live path really does serve similarity from
> `lexical_similarity` + `grounded_similarity` (no learned encoder is wired ON by default), the S8
> severity verdict, and the CLIP finding.

**[REFUTED -- see C5] "No final landed encoder exists -- the line was abandoned, not won."**
Runtime `sys.modules` trace of `hdlab.reading_grounding_loop` +
`hdlab.grounding_acquisition_loop` loads 40 hdlab modules, of which zero are encoders (no vwfa, ppmi, composed_v3, concept_encoder,
encoder_retrain_persist, random_indexing, hippocampal_encoder). Live concept similarity is
served by `hdlab/lexical_similarity.py::concept_similarity()` (hand-typed lexicon) with
`hdlab/grounded_similarity.py` (Lancaster sensorimotor + Brysbaert concreteness, hard-capped
0.45) as the OOV fallback -- neither is a learned encoder. `grounded_similarity.py`'s own
docstring (`:19-20`) records that the from-scratch learned encoder
(`scale_win_tinytransformer_encoder`) was "evaluated ahead of ... as the primary asset to wire"
and passed over on 2026-08-11.

**The S8 architectural-fault verdict SURVIVES, its stated reason was wrong.** "`learning_rate`
provably cancels" is mechanically correct at `hdlab/concept_encoder.py:495-505` but applies only
to that dead module (1 commit, 2026-07-02, zero importers). "Nothing is learned" is FALSE for
the successor: TinyTransformer v2 (from-scratch 6-layer/d512/8-head TransformerEncoder,
from-scratch 16k BPE, 121,082,196 real ARC tokens/seed) clears its own random-init
same-architecture floor by +0.1034 (text AUC 0.6356 vs random_init 0.5322, shuffle-collapse
0.4964). **[REFUTED -- see C6]** the passage that followed here cited
`exp_diag_learned_encoder_synonym_sibling_deep_wall_v1` (trained 0.7064 vs random-init 0.7452) as
a better control overturning it. That cell loaded the `v3_relobj` HARD_FAIL checkpoint and was
superseded by `exp_diag_synonym_sibling_confound_removed_v1` (trained 0.5888 vs random-init
0.4615, concreteness balanced). Net as of the correction: S8's severity (ARCHITECTURAL-FAULT) and
wire verdict (NO) still stand **for `hdlab/concept_encoder.py`, the module S8 examined**; they do
not transfer to the successor line, and the "pooling interface" headline reason is withdrawn.

**Correction, enriching C2: CLIP visual grounding was ruled out in error.**
`data/exp_visual_grounding_coherence_v1/metrics.json` (2026-07-18) is `HARD_PASS`, all gates
true, and its `glass_box_note` states CLIP+WordNet+QuickDraw are used at INGEST only -- all
recovery runs on FHRR phasors with numpy bind/unbind/cleanup, no torch/transformers at runtime.
This is permitted by the glass-box rule (external tools may build the seed, may not run at
inference) and is the **best-floored positive result in the encoder-adjacent corpus**: T1
picture->word top-1 0.635 vs shuffled 0.074 vs chance 0.050; T1 image-to-image anchor 0.756; T2a
WordNet-coherence rho 0.3532 vs null p95 0.1173 (z=5.03, empirical p=0.000); T2b confusable
2-way 0.8817 vs dictionary-only 0.500 (+0.382); T3 scene recovery 1.000 vs shuffled 0.045.
Caveat that must travel with every citation: 20 words, K=20, QuickDraw line drawings only; the
`CLAIM-VET-pending` tag in the cell's own verdict message is still open. Given the synonym-vs-
sibling wall finding above and `grounded_similarity`'s measured inability to separate synonyms
from siblings, this is the strongest un-cashed asset on disk and should be re-ranked, not left
aside.

**18 pass-vs-conflicting-data cases found**, full list in
`notes/encoder_lineage_final_2026-08-13.md` sec.5, ordered by load-bearing. Beyond the two named
in STANDING DISCIPLINE 4 (`scale_win_tinytransformer_encoder` path/status mismatch,
`hippocampal_encoder` FAITHFUL-vs-HARD_FAIL): the `composition` registry row is 2/3 true
(binding+bundling live, `concept_encoder.py` is not and has zero importers); census confirms 3
false `WIRED_AND_PIPELINE_USED` claims and, worse, 19 rows falsely claim
`WIRED_BUT_NOT_PIPELINE_REACHABLE` while measurably live (including the pipeline entry point
itself) with 62 of 141 modules unregistered; S5 goal-achievement registry wording claims "WIRED
into production" while its own `pipeline_status` says otherwise and its own coverage caveat
records a HARD_FAIL; `working_memory_multibank_K_capacity`'s registry row is filed against
`hdlab/working_memory.py` (116 lines, no working memory in it) instead of the real
implementation `hdlab/situation_model_multibank.py` (no registry row at all);
`cls_discrete_budget_consolidate` has two registry rows that contradict each other
(`VET_PENDING` vs `ALREADY_WIRED`); the definitional-extraction "clearest wire case" (64% vs 8%)
is anchored to an uncommitted `reading_grounding_loop.py`, 2 module versions behind the registry
row it is compared against; G5 "MDL gate never invoked" is stale and was already false the day
it was written, and is still repeated uncorrected in a second note the same day; two "landed"
gated-fusion text-grounding numbers (seed7 +0.0030/+0.0239, seed13 +0.0055/+0.0282) exist only
as registry prose, with no `metrics.json` on disk and no chance/scramble floor quoted at all;
`concept_encoder`'s HARD_PASS (cat/kitten cos 0.492) is overturned by its own stress test, where
a plain softmax control scores 0.461 (MIDDLE_BAND); `ppmi_sparse_encoder`'s smoke-scale win
(+0.052 over trigram) sign-flips at 20x scale (-0.0239 below trigram); five encoders in active
use (`char_positional_encoder`, `token_vocab`, `late_combine`, `whitening`,
`gsbc_graded_encoder`) have no registry row at all.

---

## FLOORED ASSETS MISSING FROM THE STEERING DOCS (2026-08-13)

Five HARD_PASS results with real control floors that were absent from `STATUS.md` entirely. Each
was invisible to a reasonable search, which is why they are the worked examples for STANDING
DISCIPLINE 4's sub-rule (an absence claim requires an ENUMERATION, not a search). Verdicts and
numbers below are read off each cell's own `metrics.json` at HEAD.

1. **MAVEN-ERE causal + subevent, both HARD-PASS on the FULL DEV split** -- hidden by a `_fulldev`
   directory suffix that no search for the base anchor name would match.
   `data/exp_maven_ere_convergence_gated_causal_v2_fulldev`: floor 5.93 -> `full_v2` **14.78**,
   scramble 3.48, `best_base` 0.73, climbs=True, levers load-bearing, scramble collapses.
   `data/exp_maven_ere_convergence_gated_subevent_v1_fulldev`: floor 2.86 -> **13.63**, scramble
   2.78, bag-majority **0.03**, transferred=True.
2. **Multi-bank working memory** -- `exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1`
   HARD_PASS (chain-grade K=4096): recall **0.9927** random / **0.9801** adversarial against a naive
   control of **0.0172 / 0.0045**. **Registry defect:** the row
   `working_memory_multibank_K_capacity` points at `hdlab/working_memory.py` (116 lines, contains
   no working memory); the real implementation is `hdlab/situation_model_multibank.py` (148 lines),
   which has **no registry row of its own** -- it appears only inside that row's `used_by` and
   `gate_decision_target` prose. A registry-first search finds the wrong file; a filesystem
   enumeration finds both.
3. **DG pattern separation at WRITE time** --
   `exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1` HARD_PASS: `dg_full` **0.942** vs
   `no_presep` **0.083** (and whiten 0.103), effective-rank lift **10.08x**, std 0.004, knn
   sentinel 1.000 at M=10000, off-diagonal mass 0.179 -> 0.012. Note the scope boundary against
   CORRECTION C7: this is pre-write separation on real Pythia keys, NOT the MCScript purity task,
   where the same mechanism HARD_FAILs.
4. **CLIP visual grounding** -- `exp_visual_grounding_coherence_v1` HARD_PASS: T1 picture->word
   top-1 **0.635** vs shuffled 0.074 vs chance 0.050; T2a WordNet-coherence rho **0.353** vs null
   p95 **0.117** (p=0.000); T2b confusable 2-way **0.882** vs dictionary-only 0.500; T3 scene
   recovery **1.000** vs shuffled 0.045. **It has NO registry row at all** (0 of 123 rows mention
   it), so the WIRE-or-SHELVE gate has never seen it -- the gate cannot fire on what was never
   enumerated. Per CORRECTION C2, CLIP at INGEST is NOT a glass-box violation: the rule bars
   external LLMs from RUNTIME INFERENCE, not from building the seed. Its own
   `CLAIM-VET-pending` tag is still open, and its scope is 20 words / K=20 / QuickDraw line
   drawings.
5. **Teacher-free relational encoder on a ConceptNet subgraph** --
   `exp_teacher_free_relational_encoder_cn_subgraph_v1` (2026-07-08, full, 5 seeds) HARD_PASS:
   `ARM_GRAPH_REPULSION` Z **497.90** (per-seed min 453.21) against random-init floor **148.97** and
   control **21.42**; ablation collapses; subgraph n=10,577, E=34,659.

---

## THE PHASE DIAGRAM -- THE STORE'S POSITION IS A CHOICE, AND IT HAS TWO UNSPENT CASH-INS

**Never-trim under `STATUS_SPEC.md` sec 4.7.** The project owner said in as many words "we should
not forget this", and it has already been forgotten once: on 2026-08-14 the `d=256 -> 1024` step was
written into the build plan as *a priced capacity upgrade worth about +0.05*. That framing is WRONG
and is corrected at the end of this section.

**The freedom.** Four knobs are tunable at will, each with a known capacity peak / cliff:
sparse-vs-dense codes; **superposition load** (how many facts are bundled into one vector); `K`;
and `n_dim`. The theory is already banked, not hypothetical -- `notes/week8_scaling_summary.md`:
FHRR capacity `k_50%(N) ~ N^1.003` (`k_50% ~= N/4.84` at pool=200, R^2 0.99999734) and nesting
depth `depth_50%(N) = 0.717*log2(N) - 0.629` (pool=100, R^2 0.973, SUB-linear; HRR by contrast is
super-linear in depth). Primary sources: `notes/exp_scaling_capacity.md`, `notes/exp_scaling_depth.md`.

**Where the store sits, and why.** The store deliberately occupies the **maximally conservative
corner: dense bipolar, SHARDED at ONE FACT PER VECTOR**. At a load of one there is no inter-item
crosstalk, so recovery is exact and every read is inspectable. That is **OPTING OUT of the capacity
phase diagram entirely**, and it is bought deliberately -- it is what makes the glass-box invariant
hold at the storage layer. **A CHOICE, NOT A LIMITATION.** Anyone reading "1 fact per vector" as a
capacity defect has the sign backwards.

**Cash-in trigger 1 -- RAM CEILING -> CONTROLLED SUPERPOSITION.** When memory (not accuracy) is the
binding constraint, bundle `B` facts per vector at a capacity-SAFE load read off the banked
capacity-vs-load curve, as the substrate-native alternative to going on-disk. `B` is a dial and the
curve says what it costs.

**Cash-in trigger 2 -- BUILDING REASONING / GOING MORE BRAIN-FAITHFUL -> SPARSE CODES.** Biological
codes run ~1-5% active: cheaper memory, cleaner cleanup, their own capacity peaks -- plus the
composition-depth regime (how many bindings compose before a multi-hop chain degrades), which is
exactly what a reasoning layer spends.

**NEITHER TRIGGER HAS BEEN HIT.** Quality -- not RAM, not reasoning depth -- is the current binding
constraint (`STATUS.md` TOP ITEM).

**THE CORRECTION, recorded so the same error cannot recur.** `d=256 -> 1024` is **a move along a
known curve whose present position is deliberate**, NOT a purchased upgrade. `ORGAN_MAP.md:338`
already has the whole curve measured on the live comparator: QUANT `[0.6395, 0.7030, 0.7380]` and
GRAD `[0.6980, 0.7495, 0.78225]` at `d = 256 / 1024 / 4096`. The "+0.05" is simply the
`d=256 -> 1024` segment of GRAD, and `0.7495` is the **d=1024 GRADED arm, never shipped** -- the
live path is `0.6980` at `d=256`. Quoting `0.7495` as the live number is the specific mistake this
paragraph exists to prevent. Raising `d` also rewrites every persisted anchor store, which is why
it is gated (`STATUS.md` WHAT IS RUNNING).

---

## DO NOT REDO -- entries added 2026-08-14 (continuing the numbering at the top of this file)

29. **The composed five-stage read-out chain (whitening -> pseudoinverse write -> coarse-to-fine).**
    `exp_composed_chain_readout_v1`, full run, verdict **HARD_FAIL_EVERY_STAGE_HURTS**
    (`data/exp_composed_chain_readout_v1/metrics.json`, `ts_iso` 2026-08-14T17:38Z, n=600 items,
    647 anchors, d=256). **Every arm is worse than the untouched baseline on hit@1 and on rank:**
    A0_BASELINE median_rank **84**/647, top50 **0.400**, hit@1 **0.09833**, 2AFC **0.7083**;
    A1_WHITEN 240.5 / 0.145 / **0.00667** / 0.6083; A2_PINV 153.5 / 0.3117 / 0.08167 / 0.665;
    A3_C2F **647** / 0.3117 / 0.095 / 0.7083; **A4_FULL (the whole chain) 647 / 0.1083 / 0.00667 /
    0.6117**. Floors in the same run: F_FREQUENCY hit@1 **0.00667**, F_SCRAMBLE hit@1 **0.00167**
    (2AFC 0.45). **Precision that matters:** A4_FULL lands **exactly on the FREQUENCY floor** on
    hit@1 and 4x ABOVE the scramble floor -- do not restate it as "at the scramble floor", which
    overstates the collapse. The cell records that none of the three stages was live beforehand, so
    this is a rejected ADDITION, not a regression. **SCOPE, in the cell's own words:** this is the
    **647-anchor** space and its baseline hit@1 0.0983 is NOT comparable to the 5491-anchor live
    figure of 0.0480.

30. **Near-duplicate anchors as the explanation for the read-out defect.**
    `exp_codebook_geometry_precheck_v1`, full run, verdict **NEAR_DUPLICATES_NOT_THE_DEFECT**
    (2026-08-14T17:16Z; live codebook n=5491, d=256, 34,169 sentences, overcompleteness 21.4x).
    `frac(NN >= 0.99) = 0.0000` against a random null of `0.0000` -- **zero** near-duplicates, so a
    dedup/merge pass has nothing to remove. What IS real is **semantic crowding**: median
    nearest-neighbour cosine **0.4637** vs null **0.2264** (excess +0.2373), max 0.8567; ZCA
    whitening moves the median only to 0.3526. **Read the top pairs honestly:** they are a MIX of
    genuine paradigmatic sisters (`sympathetic`/`parasympathetic` 0.857, `radial`/`bilateral` 0.835,
    `innate`/`adaptive` 0.821, `guanine`/`cytosine` 0.810) AND of junk with no semantic relation at
    all (`anal`/`notochord` 0.846, `garcia`/`moreno` 0.841, `chocolate`/`fraudulent` 0.789,
    `vuitton`/`louis` 0.797). Quoting only the first group makes the crowding look purely taxonomic,
    and it is not.

---

## CAVEATS THAT TRAVEL -- added 2026-08-14

**D5. The sharpening / dense-Hopfield attack has NO full run and NO SNR-wall verdict.**
`exp_sharpening_readout_sister_separation_v1` exists on disk as **SELFTEST + three SMOKE dirs only**
(enumerated by globbing `data/exp_sharpening*/metrics.json`: `_SELFTEST`, `_SMOKE` which is
`CELL_CRASHED` on a META_RULE_AF assertion, `_SMOKE_n150`, `_SMOKE_n600`). The two that ran read
**MIDDLE_BAND**, and the n600 `verdict_msg` says in terms: "neither the HARD_PASS conjunction nor
the **SNR-wall** conjunction is met". What it DOES show at n=600 / 647 anchors: best beta=512 gives
`dS` **-0.0367** (CI [-0.0800, +0.0084], includes 0), **median target rank 84/647** with **60%
outside the top 50**, **22 sister errors and ZERO converted** (content-blind control also 0),
self-retrieval 0.9067. So sharpening did not help and the SNR headroom is genuinely small -- but
"sharpening hit an SNR wall" is a STRONGER, DIFFERENT claim than the cell licenses. The honest
label is **UNPINNED / smoke-scale**, not CLOSED, and it is deliberately NOT in the DO NOT REDO list.

---

## CORRECTIONS TO PRIOR CLAIMS -- added 2026-08-14

**C12. The sub-linear gap-index design doc is dated 2026-08-12, not 2026-08-14.** The real path is
`notes/research_sublinear_gap_detector_cleanup_shard_dg_ca3_design_2026-08-12.md`. The `..._08-14`
filename cited in `notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md` sec 7 and sec 11
**does not exist**. Enumerated, not searched: listed all 9,912 entries of `notes/` and filtered on
`sublinear|gap_detector|gap_index|shard`, which returns exactly one design doc -- the 08-12 one. Its
build target `hdlab/sharded_gap_index.py` does not exist either, so the build is genuinely NOT DONE.

**C13. "The grounding-quality validation harness FULL run never reported" is WRONG as stated.**
`data/exp_foundation_validation_harness_v1/metrics.json` holds a **`run_mode: full`** run, `ts_iso`
**2026-08-12T14:27:19Z**, verdict **`HARD_PASS_foundation_validated`**, `verdict_msg`
`claim1=HARD_PASS(gap=0.2533) claim2=HARD_PASS(cohesion=0.4765,contra=0)
claim3=HARD_PASS(mech=1.0,scr=0.0,abl=0.0) smoke_controls_discriminate=True`. It reported. The
standing objection to it is a DIFFERENT one and still holds: that validation was judged
**OVERSTATED** on 2026-08-12, and the live read-out measured two days later sits at 4.80%. So what
is owed is a **re-run against the current foundation with floor arms**, not a first run. Say it that
way -- "never reported" invites someone to rebuild a harness that already exists.

---

## OPEN THREADS (older) -- moved out of `STATUS.md` 2026-08-14 to make room

Stubbed there as "(d) four older threads". None is closed; each is a thing someone must still do.

1. **The encoder-swap results are UNCOMMITTED.**
   `data/exp_encoder_swap_behind_fixed_brain_stack_v1/metrics.json` is untracked; only the prereg
   and the cell are committed (`f36ba7626`). See CAVEAT D2 for why the result is also owed a
   neutral-ground re-test.
2. **The live parser loads RICH-TRAINED weights into the BASE class and its UAS is UNMEASURED.**
   Nobody has scored the parser actually used on the live reading path.
3. **42% of the glass-box trail is UNRECOVERABLE** -- the audit trail cannot be reconstructed for
   that fraction of the run history.
4. **Nothing enforces a post-landing import check.** `38f7a0d5c` left the C1 testbed UNIMPORTABLE
   at HEAD and only a later cell noticed (repair `df149251f`). A landing gate that imports every
   touched module would have caught it at land time.

---

## STANDING DISCIPLINES -- entry added 2026-08-14

### 7. No demotion without a fresh on-disk re-check

**Bought with ~11 wrongly-demoted results and 17 corrections-of-a-correction inside 48 hours**
(`notes/vscode_week_results_validity_audit_2026-08-14.md`). Over that window the AUDIT layer was
less reliable than the measurements it audited. A demotion is itself a claim and gets the scrutiny
of the positive it attacks: re-open the metrics file at HEAD, in `.venv`, on the right arm, before
writing "this does not hold".

**The generative fault is discipline 4's sub-rule in a new costume:** each of these began as an
ABSENCE CLAIM FROM A NAME SEARCH rather than an enumeration. Traps measured: verdict strings drift
(`HARD_PASS` / `HARD-PASS` / 88 bespoke strings, so a literal grep undercounts); `_fulldev` and
`_smoke` suffixes hide real passes; file mtime and git dates lie, so key on `ts_iso` INSIDE
`metrics.json` (some assets are untracked by design); and a runtime trace of the DEFAULT path
measures REACHABILITY, never EXISTENCE, so it cannot refute an opt-in module. Keep
**EXISTS / IS-REACHED / IS-GOOD** as three separate questions and answer them separately.

---

## THE ORTHOGRAPHIC-FLOOR VET (2026-08-14) -- stubbed in `STATUS.md` as "THE FLOOR VET"

Full note: `notes/orthographic_floor_vet_and_rebaseline_2026-08-14.md` (`9ca1cffa2`). Summary of the
parts that must not be re-derived:

**The comparison IS fair.** `exp_meaning_supply_separation_v1` does not have its own corpus or item
builder -- it IMPORTS `exp_grounding_readout_known_answer_v1` and calls its `build_corpus`,
`build_buckets`, `build_space`, `build_items`, `gold_meaning_set`, `MAX_ITEMS` and `MASTER_SEED`
(lines 69, 382-391, 447). Confirmed by four bit-identical statistics: `A1_BASE` == `B5_OPEN_REAL` =
0.048, CI [0.04125, 0.05475], sd 0.003414134660129855; `F_SCRAMBLE` == `B6_OPEN_SCRAMBLE` = 0.008,
CI [0.00525, 0.011], sd 0.001430965936002671; n=4000; 5491 anchors; identical removals (404 not in
WordNet, 484 no gold anchor, 53 foil fallback). All six triple-checks run (right file / version at
HEAD, both sources and both metrics unmodified in the working tree / `.venv` / corpus identical by
construction / same metric definition and denominator / same arm, proven not assumed).

**But the arm was misidentified, and this is the finding.** `arm_scores(base, aux, w)` returns
`z(base) + w*sum(z(aux))` (lines 235-240) and `A5_STRINGCTRL`'s aux list is `[aux_t]` (line 469).
The arm therefore carries the FULL substrate signal plus spelling. Its docstring (151-160) says it
was built to compare two ADD-ON channels, never to be a standalone floor. **"A method with zero
understanding scores 0.1027" is FALSE. "We underperform a spell-checker" is NOT ESTABLISHED and must
not be propagated.** The orthography-ONLY number does not exist in any metrics file on disk.

**What is established, and indicts the METRIC.** At the pre-declared `w=0.50`: spelling as an add-on
buys **+0.0425** hit@1, the trained encoder only **+0.0270**; the cell's own conclusion fields read
`encoder_gain_exceeds_string_control: false`, `encoder_gain_attributable_to_string_similarity:
true`. Roughly half the movable range on this score needs no understanding, so a raw hit@1 gain is
not evidence of a meaning gain unless a standalone string control was run and beaten.

**The shortcut signature (this is what HG3 exists to catch).** `A5_STRINGCTRL` across w --
hit@1 0.0693 / 0.0905 / 0.1027 climbs, while median rank 28.0 / 25.0 / **31.0** and top-50 0.6068 /
0.6118 / **0.5867** (below base's 0.5565 at w=1.00) and separation margin (median) -2.278 / -3.178 /
**-5.537** all degrade. `A4_BOTH` by contrast improves on all four at once (0.0940 / 18.0 / 0.6823 /
-1.886). A shortcut lifts the winner without moving the distribution.

**`F_PROJDRAW` is misnamed and should be renamed.** Built at line 506 by `build_salted_space(...,
"PROJDRAW_%d|" % r, ...)`, it re-runs the BASE arm with a different random-projection salt: a
run-to-run reliability estimate, NOT a no-understanding baseline. All three draws (0.05025, 0.0515,
0.0525) land ABOVE the 4.80% headline. Treat 4.80% as one draw of a quantity with ~0.005 of seed
noise; do not compare anything at finer resolution than 0.001.

**`char_trigram_encoder`: EXISTS, NOT REACHED -- measured, not assumed.** Module
`hdlab/char_trigram_encoder.py`, class `CharTrigramEncoder(n_dim=4096, pad_char=SPACE)` with
`.encode` / `.encode_batch` / `.nearest`. Runtime trace (`scratch/ortho_trace_char_trigram.py`):
recorder on BOTH `builtins.__import__` and `importlib.import_module`; eager closure of the live path
= 40 `hdlab` modules, absent; `process_sentence(state, sentence, episode_id, pass_idx)` EXECUTED on
three real definitional sentences (returned 5, 6, 5) pulling in ZERO further modules and logging
ZERO `char_trigram` events. **POSITIVE CONTROL: `StructuralEncoder._load()` -- whose imports sit
inside a function body at `hdlab/reading_grounding_loop.py:343-345` -- pulled in `arc_labeler`,
`arc_parser`, `perceptron`, `pos_tagger`, proving the trace sees lazy imports.** Corroboration: an
AST scan of every function-body import in `hdlab/` lists 26 lazy targets; `char_trigram_encoder` is
not one, so there is no lazy call site the trace could have missed. Its registry row claims
`wired_load_bearing` / `WIRED`; runtime overrules it.

**What using it would mean, concretely.** Call site =
`experiments/exp_grounding_readout_known_answer_v1.py:560-562`, the
`canonicalize_fast("__slot__", qL, space, thresh=-1.0, eligible_mask=open_base)` open-vocabulary
argmax -- the one place a spelling channel enters or is removed. Arms it makes possible, none of
which exist: `F_ORTHO_ONLY` (the missing floor; decides the spell-checker question),
`F_ORTHO_MAX` (that floor tuned over a grid -- legitimate for a FLOOR, since a floor should be the
strongest available attack, though NOT for a treatment arm), `A_BASE_ORTHO_RESIDUALIZED` (substrate
score with the trigram direction projected out -- what does the substrate know that spelling does
not?), and `SPLIT_LOW_OVERLAP` (hit@1 restricted to items whose gold answer has low string overlap
with the cue -- the cheapest honest fix, because it removes the confound from the METRIC rather than
adding another arm, and it is computable from the existing item list).

**`w=0.50` vs `w=1.00`.** The cell pre-declares `headline_w: "w_0.50"` and
`max_over_w_is_an_optimistic_upper_bound: true`. Use `w=0.50` for arm-vs-arm. The asymmetry worth
remembering: for a FLOOR, max-over-grid is the RIGHT choice; for a TREATMENT it is cherry-picking.
Moot here twice over -- A5 is not a floor, and at `w=1.00` the meaning arm `A4_BOTH` (0.1190) is
above A5 (0.1027) anyway.

**Open, in priority order:** O1 spelling-alone floor (`scratch/ortho_floor_vet_trigram_only.py`,
drafted, NOT RUN, ~10 min, pool-identical by construction -- blocks every floor claim); O2
`A_BASE_ORTHO_RESIDUALIZED`; O3 `SPLIT_LOW_OVERLAP`; O4 rename `F_PROJDRAW`; O5 reconcile the
`char_trigram_encoder` registry row against the runtime trace.

---

## RECOVERY TRIAGE RESIDUE (2026-08-14) -- stubbed in `STATUS.md` as "RECOVERY TRIAGE"

968 cells have rows across two ledgers not yet merged into `RECOVERY_PROGRAM.md`:
`notes/recovery_ledger_chaingraded_tier_2026-08-14.md` (565/565 terminal cells; `51b6f247a`,
`40997bf85`, `da7fe14d4`, `b4e90942a`) and `notes/recovery_ledger_reading_tier_2026-08-14.md` (403;
`63d5cccd2`). **Until the merge lands, every count must run over all three files** --
`grep -oE 'STATE:[A-Z_]+'` over the three gives 1063 rows = 946 VERIFIED / 69 REFUTED / 45 FOUND /
2 SHELVED / 1 WIRED (the single WIRED row is in `RECOVERY_PROGRAM.md`; **0 of the 968 new rows are
wired**). A count over `RECOVERY_PROGRAM.md` alone returns 95 and is wrong by an order of magnitude.

Deflations that must travel with the headline number:
- **280 of 565 chain-graded rows (50%) are ONE auto-generated saturation grid**
  (`exp_q_a3_l<N>_cross_layer_composition_v1_n<N>` / `exp_pp48_nkt_depth_*`), reporting EXACT-1.0 at
  every level with no comparison arm because the result is construction-determined. "574
  chain-graded cells" is **~286 distinct investigations**, not 574.
- **Only 172 (30%) have a real floor** (control / reference / prose). 124 have a contrast arm but no
  reference arm; 251 have no floor shape at all.
- A `scramble`-keyed lexical sweep finds **11** floored cells in that tier and MISSES **161** -- the
  June convention names floors `hebb_alpha_c`, `cap_unwhitened`, `last_token_raw`, `HA_ONLY`,
  `NO_CX`, `FREQ_NULL`, or states them only in prose. Verdict-string and floor-name drift is why an
  absence claim needs an enumeration.
- **Still NOT-YET-TRIAGED: ~1,180 ledger atoms and ~7,150 of the repo's 7,660 `metrics.json`.**

---

## DO NOT REDO -- entries added 2026-08-14 (late)

**31. MEANING SUPPLY AS THE C3 CONSTRAINT -- REFUTED.** The earlier 08-14 TOP ITEM claimed the
read-out was starved of meaning content. `exp_meaning_supply_separation_v1` (`c0e6ec0da`) wired in
the 39,707-word norms island and the 237.7M-token encoder and measured the result: hit@1 4.80% ->
9.40% (`A4_BOTH` at the declared w=0.50), **but the string-form control reaches 9.05% through the
identical blending mechanism**, crowding never fell (median NN 0.4553 -> 0.4493 against a null of
0.2265), and sister conversions numbered 1-3 out of 4000. Supplying meaning does not close
within-neighbourhood separation. Revival: only alongside a representation change, never as a supply
fix on its own.

**32. DG / PATTERN-SEPARATION AS THE GROUNDING ROUTE -- ALREADY BEATEN, IN JULY.**
`exp_dg_pattern_separation_mcscript_purity_v1`, HARD_FAIL: DG separation at sparsity 0.05 gives
`mean_purity_multi = 0.1013` against a **~0.1999 baseline -- BELOW it**. Its own words: "the
substrate cannot discriminate 195-way online with this keying signal even with DG-style
separation". Do not re-propose DG as the separation fix without a different keying signal.

**33. CROWDING AS A GATE CRITERION -- worse than useless.** Measured across all 12 arm-by-w cells,
crowding FALLS for the trigram attacker and RISES for the genuine meaning arms, so gating on it
would pass the attacker and fail the real result. Report it; never gate on it.
(`notes/c3_gate_hardening_2026-08-14.md` sec 1a.2, 2a.)

---

## CORRECTIONS TO PRIOR CLAIMS -- added 2026-08-14 (late)

**C14. "No cell tests the whiten+pinv chain end-to-end" is WRONG.**
`exp_pb_production_recipe_integration_v1`, verdict HARD_PASS, 3 seeds:
`naive(raw+hebb)=3, full(whiten+pinv)=172, lift 57.3x`. The end-to-end composition was measured. An
absence claim again failed for want of an enumeration.

**C15. One stage of that same chain is CONTRADICTED from inside its own tier.**
`exp_substrate_expansion_method_battery_gpu_v1` (full, 2026-06-06): "expansion cannot beat rank
(rp_x4 ~ native) while whitening helps via decorrelation", `native=0.0065 rp_x4=0.0065
zca_whiten=0.0517`. Neither cell cites the other. **Resolve this before running the chain
end-to-end -- it is cheaper than the chain and it may DELETE the dimensional-expansion stage.**

**C16. `A5_STRINGCTRL` is NOT a zero-meaning arm.** `notes/c3_gate_hardening_2026-08-14.md` describes
it as "a pure character-trigram control containing no meaning at all". It is `z(base) + w*z(trigram)`
and carries the full substrate signal. The gate-hardening note's CONCLUSION is unaffected -- an arm
differing from the failing base ONLY by a spelling channel cleared the old criterion, which is the
gameability demonstration -- but its WORDING overstates, and any restatement must use the corrected
description. See the orthographic-floor VET above.

---

## STANDING DISCIPLINES -- entry added 2026-08-14 (late)

### 8. A gate is a MARGIN above the strongest non-understanding baseline, never a bare number

**Bought with the entire ">=10% hit@1 against a recorded floor" C3 criterion**, which a spelling
channel bolted onto the failing base arm cleared at 0.10275 (`c0e6ec0da`), and with the weeks of
"5.2pp short of the gate" framing that criterion produced.

> A gate must be a **confidence-interval-separated MARGIN above max(ORTHOGRAPHIC, FREQUENCY,
> SCRAMBLE)**, every baseline measured on the **identical scorer, n, candidate pool and gold set**.
> Never a bare absolute number.

Two sub-rules, each with its own incident:

- **The baseline must be STANDALONE.** An arm that adds a shortcut channel ON TOP of the system
  under test is a DECOMPOSITION, not a floor; quoting it as one produces the mirror-image error
  ("we lose to a spell-checker") out of the same metrics file. **Read what is IN the arm -- open the
  scoring function -- before quoting any arm as a floor.**
- **The weakest available baseline is not "the" baseline.** Scramble controls only for random
  re-pairing. It was being used alone while a frequency floor (0.0185) sat in the same file and an
  orthographic floor was never measured at all. Enumerate the baselines the metric admits, then
  take the maximum.


---

## CAP PRESSURE MEASURED 2026-08-14 (for the next STATUS maintainer)

`STATUS.md` rebuilt to spec this session lands at **8183 B against the 8192 B cap -- 9 B of
headroom**, versus the ~830 B the spec anticipated when it set 8192 (sec 7). The cause is
structural and was predicted by the spec itself: **the never-trim class only grows.** Sections 5
and 6 now carry 33 DO-NOT-REDO stubs + 5 caveats + 16 corrections + 8 standing disciplines = **62
named items in ~3,600 B**, against their combined 2,400 B allocation. Every one is already a
NAME-ONLY stub with its reasoning in this file, so escalation step 1 (move reasoning out) is
EXHAUSTED. Tiers 1-4 were cut hard to fit: the PHASE DIAGRAM subsection was retired to a pointer
(escalation step 2), and finished-work numbers, the OPEN-thread paths and the 2AFC / banked-arm
figures were dropped as tier-1/tier-3 re-derivable.

**Next over-cap event should go to escalation step 3 (a measured cap raise), not to another
byte-shave** -- there is nothing left in tiers 1-4 worth 200 B. The alternative, if the cap is to
hold, is to retire DO-NOT-REDO entries whose routes are dead beyond any revival (candidates: 6, 15,
19), which is a deliberate judgement call for a maintenance pass and must NOT be made by an agent
that merely needs room (spec sec 6).

## DO NOT REDO -- entries added 2026-08-15 (auditor, off-data)

Stubbed in `STATUS.md` as entries **34** and **35**. Full analysis:
`notes/graded_path_does_not_clear_the_orthographic_floor_2026-08-14.md`.

**34. FLIPPING THE GRADED SWITCH EXPECTING A C3 GAIN -- MEASURED AND NULL.**
`exp_graded_path_vs_orthographic_floor_v1` (n=4000, 5491 anchors, positive control
`a1_graded_on_reproduces_c3_headline_0480_exactly = true`): `A1_GRADED_ON` **0.0480** vs
`A9_GRADED_OFF` **0.0465**, d = **+0.0015**, CI **[-0.0055, +0.00825]**, `ci_excludes_zero =
false`, against between-projection-draw sd 0.0009 (ON) / 0.0024 (OFF) -- the delta is at
draw-noise scale. Verdict `DOES_NOT_CLEAR_ORTHOGRAPHIC_FLOOR`; `on_clears=False off_clears=False
graded_helps=False graded_hurts=False`. Neither arm clears spelling: `A5_STRINGCTRL` **0.0870**,
ON-minus-spelling **-0.0390** CI [-0.0500, -0.02825], CI EXCLUDES ZERO; `A7_PREFIX_ONLY` 0.05875
also beats both. `median_rank` ON **37.0**, OFF 45.0, spelling 37.0, prefix 33.5 -- the ON arm
only TIES the spelling control on rank and LOSES to prefix.
**\* Revival criterion:** the projection-draw ensemble disagrees with the canonical projection
(draw-mean delta +0.0092, 3 draws/arm; the canonical projection is worst-of-four for ON and
best-of-four for OFF), so `graded_helps=False` is NOT settled -- a re-run with >=10 independent
projection draws per arm could legitimately overturn it. It could NOT overturn the floor verdict:
+0.0092 still leaves the read-out 0.0356 below spelling. **Do NOT turn the switch off** -- every
point estimate is positive and self-retrieval is better with it on (0.7860 vs 0.7358, floor 0.70).
**Integrity flag recorded rather than waved through:** `arms_must_differ.ok = false` --
`F_SCRAMBLE_ON` and `F_SCRAMBLE_OFF` share digest `4596b30dc13e9692` (bit-identical per-item hit
vectors). The collision is confined to the two scramble floors; the two treatment arms have
distinct digests (`9ee2af8d9ece6c2b` / `f3402395402fee12`), so the load-bearing comparison is
unaffected -- but the cell's own gate did not pass and that is not silently adopted.

**35. QUOTING +0.0602 (OR 0.6395 -> 0.6980 / 0.69975 / 0.7495) AS A C3 NUMBER -- WRONG CURRENCY.**
Those are **near-neighbour 2AFC** accuracies from `data/exp_graded_divisive_comparator_v1`
(verified off disk: `chance = 0.5`, `n_anchors = 2377`, verdict_msg `LIVE(A_SSN)=0.6395
PRIMARY(A_GGZ)=0.69975 | d=0.0602 CI=[0.0440,0.0762]`). C3 is **open-vocabulary hit@1** -- chance
~1/5491, pool **5491**. A gain measured on one scorer was carried across to another where it does
not exist; the same manipulation in C3's own currency is **+0.0015, null** (entry 34). The source
cell's HARD_PASS **stands on its own scorer and is NOT demoted** -- only the carry-across is
refuted. **Revival criterion: none. This is a units error, not a hypothesis.** General form, and
the reason it earns a slot: **a gain on one scorer is not a gain on another; carry a metric's
identity with its number.**

## CORRECTIONS TO PRIOR CLAIMS -- added 2026-08-15 (auditor, off-data)

**C17. THE SCRAMBLE FLOOR IS DONOR-RULE DEPENDENT; 0.0080 AND 0.01375 ARE BOTH RIGHT.**
`STATUS.md` quoted **0.0080** bare. Traced: 0.0080 is
`exp_grounding_readout_known_answer_v1` -> `stage_b.open_vocabulary_readout.hit_at_1.
B6_OPEN_SCRAMBLE` (CI [0.00525, 0.01100]); 0.01375 is `exp_graded_path_vs_orthographic_floor_v1`
-> `F_SCRAMBLE_{ON,OFF}` (CI [0.01050, 0.01725]). Harness, n (4000), pool (5491), gold, metric and
query format (BOTH graded -- the known-answer run had `HD_GRADED_COMPARATOR_env = 1`, and
`reading_grounding_loop.py:504` returns the graded sum when the switch is on) are IDENTICAL. The
**donor rule** is the whole difference: the known-answer cell uses a CONFLICT-AVOIDING DERANGEMENT
(`:503`, a donor sharing any of `{L, G, F}` with the item is excluded); the graded-path cell uses a
plain `rng.permutation(n)` (`:357`) with no conflict avoidance, so donors whose gold set overlaps
the item's remain and score structural hits. Ruled out as the cause: that permutation has **zero
fixed points** at `MASTER_SEED + 21 = 20260835` (independently re-drawn and counted). Neither
number is retired and **neither may be quoted bare** -- quote the donor rule with the number. The
looser rule gives the higher, more conservative floor, which is what a floor should do.
Cross-check on scope: `exp_orthographic_floor_vet_v1` has NO scramble arm at all (`per_arm` =
`A1_BASE`, `A6_TRIGRAM_ONLY`, `A7_PREFIX_ONLY`, `A8_MAXORTHO`), so 0.0080 was never sourced from
the floor-VET cell despite sitting beside its numbers in the same paragraph.

**C18. THE TOP ITEM'S CONJUNCTIVE-CODING LEAN IS QUALIFIED, NOT REFUTED.** Four orphaned
perirhinal literature scans were rescued from sub-agent transcripts and persisted verbatim with
their per-claim evidence tags intact (`notes/lit_scan_perirhinal_conjunctive_coding_operation_
2026-08-14.md`, `..._feature_ambiguity_hypothesis_lesion_evidence_...`,
`..._perirhinal_purely_mnemonic_counter_position_...`,
`..._vvs_to_mtl_representational_hierarchy_interference_...`). They establish two qualifications.
(a) The conjunction OPERATION is **UNPINNED**: no measured superadditivity coefficient exists for
real perirhinal neurons, and the one verifiable model (Cowell, Bussey & Saksida 2006, J Neurosci
26(47):12186-12197) uses a **Kohonen self-organising map with Euclidean-distance readout that its
own authors flag as an abstraction, not a biophysical claim**. (b) The feature-ambiguity account
is **actively CONTESTED with genuine FAILED REPLICATIONS** -- Clark et al. 2011 (Neuron), null in
rats at every ambiguity level **with a memory-task positive control in the same animals**; Levy /
Shrager / Squire null in humans. Consequence for the TOP ITEM: our own floored results (factored
1.000 vs flat 0.003; conjunctive 1.000 vs additive 0.273; permutation 1.000 vs FHRR 0.0629) are
UNAFFECTED and remain the reason to give the comparator a structured code. What may NOT be claimed
is that this is PINNED BRAIN FIDELITY. Pursue it as OUR engineering choice on OUR measurements.
