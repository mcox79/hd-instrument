<!-- CORRECTION 2026-08-18 -- READ BEFORE THE TEXT BELOW -->
> **⛔ THE FIGURE "3,544 GROUNDED CONCEPTS / 9.87x THE HAND LEXICON" IS RETIRED. DO NOT QUOTE IT.**
> This project refuted it ON ITS OWN DISK and the correction never propagated:
> `exp_reading_grounding_loop_cycle3_groundingfix_v1` records `B1_taut 0.656885 -> 0.0` and
> `B4_grounded 3544 -> 634`. Independently recomputed 2026-08-18 from
> `data/foundation/reading_grounding_v1/store/store_facts.json`: **2,328 of the 3,544
> GROUNDED_MEANING facts are SELF-ANCHORED -- 67% of the "grounded concepts" have THEMSELVES as
> their meaning.** Of the 1,216 real links the commonest anchors are `also` (31), `say` (15) and
> `people` (10), with entries like `web -> polar`; and 121 stem/full-form pairs (`cigarett` /
> `cigarette`) are counted as two concepts. **The surviving number is 634, and it has not been
> re-vetted.** Evidence: vetting pass 3, commit `d91fbbc2c`.

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

18. **Role-bound dependency structure ALONE as a route to meaning.**
    **RE-CLOSED 2026-08-15 ON A VALID RULER, AND THE DIRECTION IS NOW KNOWN: STRUCTURE HURTS.**

    *The 2026-08-13 entry, preserved verbatim, superseded-by the 2026-08-15 result below:*
    > NULL on quality (0% vs 2% MEANINGFUL, delta -0.02) -- but it DID bind mechanically, which is
    > why the negative is informative rather than a smoke failure: argmax disagreement 97.80%,
    > co-occurrence agreement at top5 fell 0.2552 -> 0.0749, band DIVERGED. The structure was
    > really imposed and the quality did not move --
    > `notes/director_handscore_structured_comparator_2026-08-13.md`, 0db7cfdaa.

    **Why the old judgement could not stand.** That NULL was a HAND-SCORED MEANINGFUL delta on
    `exp_structured_comparator_v1` -- 1 MEANINGFUL row in 100, max attainable |delta| 0.02 against
    its own declared minimum detectable 0.11. STANDING DISCIPLINE 1 in this file names that cell
    explicitly as underpowered by floor and prescribes gating on KNOWN-ANSWER RECALL instead. So
    entry 18 was closed by an instrument since ruled invalid, and until 2026-08-15 the honest label
    was *UNTESTED WITH A WORKING RULER, NOT REFUTED*.

    **The licensed result that replaces it.** `data/exp_structured_code_vs_flat_bag_c3_v1/metrics.json`
    (banked 2026-08-16 at `15d94cf67`; it was untracked until then). Verified off disk for this
    entry, all six checks stated: right FILE (that absolute path, no `_scratch_` neighbour); right
    VERSION (the 2026-08-15T16:05Z graded-fix RE-RUN, which replaced a 2026-08-14 run VOIDED by its
    own positive control at `SR_STRUCT=0.6712`); right ENV (`.venv`); right CORPUS (C3 harness
    imported wholesale from `exp_grounding_readout_known_answer_v1`, `MASTER_SEED=20260814`,
    `n_items=4000`, 5491 anchors); right METRIC (open-vocabulary hit@1, the same scorer that gives
    the 4.80% headline -- `a1_base_reproduces_c3_headline_0480_exactly: true`); right ARM (`A1_BASE`
    vs `A2_STRUCTURED`, distinct arm digests `9ee2af8d9ece6c2b` / `621add21502d6669`).
    - **verdict `STRUCTURE_HURTS`.** `A2_STRUCTURED` **0.03675** [0.03100, 0.04275] vs `A1_BASE`
      **0.04800** [0.04125, 0.05475]. Paired delta **-0.01125, CI [-0.01950, -0.00300]**, excludes
      zero. Between-projection-draw sd 0.0015 (STRUCT) / 0.0009 (BASE), so the effect is larger
      than the shared-randomness noise.
    - **BOTH known-answer arms clear their pre-registered floor**: self-retrieval BASE **0.7860**
      (n=299) and STRUCT **0.7637** (n=292) against `SELF_RETRIEVAL_FLOOR=0.70`. That is what makes
      this a licensed negative rather than a plumbing failure, and it is exactly the gate the
      2026-08-14 run failed.
    - **Neither arm clears the spelling floor**: `A5_STRINGCTRL` **0.0870**, `A7_PREFIX_ONLY`
      **0.05875**. `base_clears_floor=false`, `struct_clears_floor=false`.
    - The organ is unchanged and was reused, not rebuilt: `StructuralEncoder` /
      `structural_vector_masked` in `hdlab/reading_grounding_loop.py`, i.e.
      `sign(sum(bind(REL_vec, filler_vec)))` over 1-hop dependency relations, mean 2.82 features per
      encoding. Pre-reg `preregs/2026-08-14_exp_structured_code_vs_flat_bag_c3_v1.md` plus the
      addendum `preregs/2026-08-15_..._graded_fix_rerun.md`.

    **Disclosed defect in the artifact, not patched and not hidden.** `arms_must_differ.ok = false`:
    `F_SCRAMBLE_BASE` and `F_SCRAMBLE_STRUCT` share digest `4596b30dc13e9692`, so ONE scramble floor
    serves both arms rather than one per arm. It does not touch the BASE-vs-STRUCT head-to-head
    (which is what this entry turns on) but it does mean the two scramble columns are one number
    reported twice, and nobody may quote them as independent per-arm floors.

    **What is closed and what is NOT.** Closed: *this* structured code, as a drop-in swap for the
    flat bag, on the live open-vocabulary read-out, with nothing in front of it -- it is worse than
    the flat bag, CI-separated. NOT closed, and the distinction is the whole point: the code was
    measured **with no completer in front of it**. Per PLAN R13 and the 2026-08-16 CA3 correction in
    `notes/PLAN.md` section 5, separation and completion are a matched pair, and a structured or
    conjunctive code with no CA3-shaped completion stage is being asked to do its partner organ's
    job. **REVIVAL CRITERION (brain-framed, never performance-framed): re-run this exact arm, on
    this exact harness, once a CA3-style pattern-completion stage exists and sits between the query
    and the code.** A better hit@1 on its own is NOT a revival criterion.

    *Adjacent, do not merge with this entry:* DO-NOT-REDO 32 (DG / pattern separation) is a
    different organ and was NOT re-tested on 2026-08-15. It remains where it was.

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

> 🔴 **ENTRY 31 NARROWED 2026-08-15 (auditor, off-data) -- NOT DELETED, NOT WEAKENED IN ITS OWN
> SCOPE. Corrected text, which supersedes the paragraph above:**
>
> **31. MEANING SUPPLY AS AN ADDITIVE SIMILARITY CHANNEL ON THE FLAT-BAG C3 READ-OUT -- REFUTED**
> (argmax-only; string control matches; encoder ties spelling-alone 0.0870). **NOT refuted: a
> native word-level or in-distribution encoder, or meaning as separately-addressed structure.**
>
> **Why the narrowing is required, not a courtesy.** The refutation was obtained by improvising an
> interface the artifact does not have, and **a negative obtained by improvising a missing
> interface bounds THAT improvisation.** Left unscoped it silently upgrades into the strictly
> larger claim "meaning supply cannot help", which the cell did not test. Verified at runtime by
> the propagating auditor: `load_improved_encoder(seed=7)` returns an `EncoderExtractor` (d=512)
> whose public attributes are `['CUES','build','conditioning','cue_vec','d','decode_dataset_slots',
> 'model','oracle','pad_id','tok']` -- `hasattr` is **False** for every one of `embed_word`,
> `embed`, `encode_word`, `word_vector`, `get_word_embedding`. **No encoder artifact exposes a
> word-embedding interface at all**, which is why the cell had to mean-pool contextual token
> representations, and the cell says so in its own `encoder.note`.
> **Correcting a correction that is already circulating: it is FALSE that "the cell did not test
> the large encoder."** `experiments/exp_meaning_supply_separation_v1.py:183-185` calls
> `load_improved_encoder(seed=ENC_SEED)` -- the real landed artifact, `d_model` 512,
> `tokenizer_vocab_size` 16000. The `USE_IS_OUT_OF_DISTRIBUTION: true` flag describes **how it was
> used** (mean-pooled to fake an absent word-level API), **not which artifact was used.** Do not
> let "the big encoder was never tested" propagate.
> **The optimistic reading, recomputed:** `A3_ENCODER` best-over-w is **0.0880** [0.07925, 0.09700]
> at w=1.00 (the cell's own `max_over_w_is_an_optimistic_upper_bound: true`), against standalone
> spelling **0.0870** [0.07825, 0.09600]. **0.0880 sits inside the spelling CI: at its most
> optimistic the encoder TIES a zero-meaning control.** The cell's own field already reads
> `encoder_gain_exceeds_string_control: false`.
> **This is a RE-GATE OBLIGATION, NOT AUTHOR ERROR.** The cell's floors were `F_SCRAMBLE` 0.0080
> and `F_FREQUENCY` 0.0185 -- the weakest on the shelf -- because the orthographic floor did not
> exist when it ran: `exp_meaning_supply_separation_v1` `ts_iso` **2026-08-14T18:48:21Z**,
> `exp_orthographic_floor_vet_v1` `ts_iso` **2026-08-14T21:30:09Z**, i.e. the stronger floor landed
> **2h41m48s AFTER** the cell it re-gates. The author used the best floor available at run time.
> Read the row that way.

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

---

## DO NOT REDO -- entries added 2026-08-15 (auditor, 15-claim VET propagation)

Source: a 15-claim VET (`.claude/scan-out/vet-claims.json`). **Every number below was
independently re-verified off disk by the propagating auditor before being written here**, and two
of the VET's own statements did NOT survive that re-check -- both are recorded as corrections C19
and C22 rather than propagated. Stubbed in `STATUS.md` as entries **36** and **37**.

**36. TREATING `k_eff ~= 50` AS A MEASURED DISCRIMINABILITY LIMIT -- IT IS THE CONFIGURED
SHORTLIST SIZE.** `SHORTLIST_K = 50` is a hard-coded config line at
`experiments/exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1.py:118`, inherited verbatim by
`stage2e:160` and `stage2g:137` (`SHORTLIST_K = S2B_SHORTLIST_K`). Where the symbol `k_eff` does
occur in code it is a **clamp, not a measurement**: `k_eff = min(shortlist_k_eff, scores.shape[1])`
(`stage2d:446`, `stage2f:185`), i.e. the configured K reduced to the number of available entities.
**Had `SHORTLIST_K` been 20, the identical evidence would have read "k_eff ~= 20."** Nobody has ever
swept K at any of the three sites, so the size of the confusion set is UNMEASURED.
**What is real and is NOT retracted:** `exp_focus_pullin_causal_stage2g_deeper_leaf_split_v1`
verdict `HARD_FAIL`, `wrong_argmax_frac_1213912` = **0.7077 / 0.7656 / 0.7121 / 0.7500** across
leaf sizes 25000 / 15000 / 10000 / (4th) -- **flat**, which falsifies within-leaf crosstalk as the
cause. That is a clean, well-controlled negative and it stands on its own. Only the *interpretation*
("the confusion set has ~50 members") is withdrawn.
**\* Revival criterion:** a genuine K-sweep -- report recall@K and argmax accuracy CONDITIONAL on
in-set over K in {5,10,20,50,100,500,full}. A knee at ~50 that survives varying `SHORTLIST_K` would
earn the phrase. Note the counter-evidence to a *fixed* k_eff already on disk: conditional argmax
accuracy is 0.5333/0.9467 = **56% at 100K** but 0.1867/0.8533 = **22% at 1.21M** at the SAME leaf
size, i.e. the failure is scale-dependent.

**37. "RIGHT NEIGHBOURHOOD, WRONG MEMBER" / WITHIN-NEIGHBOURHOOD SEPARATION AS THE C3 DIAGNOSIS --
NOT SUPPORTED, ON TWO INDEPENDENT GROUNDS.** Recomputed off
`data/exp_orthographic_floor_vet_v1/metrics.json` (identical items/pool/gold, n_items=4000,
n_anchors=5491):
(i) **A zero-substrate spelling channel reproduces the rank profile exactly.**
`per_arm.A1_BASE.median_rank` = **37.0**; `per_arm.A6_TRIGRAM_ONLY.median_rank` = **37.0** --
identical, from `t_mat[sel] @ tq` with no substrate signal at all; `A7_PREFIX_ONLY` = **33.5**,
BETTER than the substrate; `A8_MAXORTHO` = 43.0. Accuracies: A1_BASE 0.0480 [0.04125, 0.05475],
A6_TRIGRAM_ONLY 0.0870 [0.07825, 0.09600]. "Landing in the right neighbourhood" is a claim about
semantic geometry, and a channel with no semantics lands in the same place.
(ii) **The actual error population is not co-hyponyms.** `stage_b.open_vocabulary_readout.
example_picks` off `data/exp_grounding_readout_known_answer_v1/metrics.json`, verbatim and in order:
`abandon->palm`, `abbey->highclere`, `ability->work`, `able->might`, `abnormality->chromosomal`,
`about->more`, `above->metre`, `abroad->gain`, `absence->presence`, `absent->limitation`,
`absolutely->farm`, `absorb->pigment`, `absorption->fold`, `abundance->endemic`, `abuse->mouse`,
`academic->findings`, `academy->proceedings`, `accelerate->tness`, `acceptor->nad`,
`accept->donate`, `accessory->louis`. `abuse->mouse` is an ORTHOGRAPHIC rhyme; `accelerate->tness`
is a broken token; only a minority (`absence->presence`, `accept->donate`) fit the paradigmatic
story. The hand-picked `axon->dendrite` / `artery->vessel` pairs describe a SUB-POPULATION, not the
95.2% of misses.
**What is NOT refuted and must not be over-corrected away:** retrieval is genuinely healthy --
`stage_b.self_retrieval` = `{"acc": 0.785953, "n": 299, "floor": 0.7, "ok": true}`. Supply is still
closed (DO-NOT-REDO 31). The read-out is still below the spelling floor (C12/entry 34). What
changed is only the *mechanism story* for WHY, and therefore what to build next.
**\* Revival criterion:** a same-harness measurement showing the miss population is
disproportionately co-hyponymic RELATIVE TO the trigram/prefix arms' own miss populations -- i.e.
the neighbourhood claim has to beat the orthographic control, not merely be illustrated by
cherry-picked pairs. `exp_meaning_supply_separation_v1.py:463` already ships an `_is_sister()`
WordNet-hypernym predicate, so the measurement is cheap; it has simply never been run as a
*contrast against the spelling arms*.

## CORRECTIONS TO PRIOR CLAIMS -- added 2026-08-15 (auditor, 15-claim VET propagation)

**C19. CORRECTION TO THE CORRECTION: "`k_eff` appears in NO metrics.json and NO source file" is
FALSE.** The VET asserted this absence; enumeration refutes it. Method: `git grep` over all
**28,338 tracked files** (7,637 of them `metrics.json`), substring then word-bounded. `k_eff` occurs
as a local variable in `experiments/exp_focus_pullin_causal_stage2d_...py:446` and
`...stage2f_...py:185-187`, and the literal string `k_eff=50` occurs **once inside
`data/exp_focus_pullin_causal_stage2g_deeper_leaf_split_v1/metrics.json`**, in the `crlb_n/a` prose
field ("comparison-set-size-restricted (k_eff=50) discriminability vs per-leaf write count").
**This does not rescue the phrase -- it sharpens entry 36**: the on-disk `k_eff` *is* the configured
shortlist size (`min(shortlist_k, n_ent)`), which is exactly why it cannot be cited as a measured
limit. Recorded because STANDING DISCIPLINE 4's sub-rule ("an absence claim requires an
enumeration, not a search") binds corrections too, and an overstated refutation is the mechanism
that produced 17 corrections-of-a-correction in 48h.

**C20. THE EXTRACTOR'S "~0.90 PRECISION ON CLEAN EXPLICIT SENTENCES" HAS NO SOURCE ON DISK.**
Against INDEPENDENT gold (`data/exp_coherence_gate_extraction_correctness_independent_gold_v1/
metrics.json`, verdict **MIDDLE_BAND**, `n_gold` = **34**), triple precision is **0.222-0.250** and
primary precision **0.244-0.278**; `verdict_msg` reads `UNGATED P=0.180 ... FULL P=0.275 F1=0.297`.
The three cells that would have supplied a precision number --
`exp_definitional_predicate_v6`, `_v61`, `_v62` -- all landed verdict
**`STRUCTURAL_PASS_PENDING_HANDSCORE`**; **the hand-score was never done.**
Worse, `data/exp_wire_definitional_v1/metrics.json` `primary_HELDOUT_B` is **bit-identical between
the ON arm and the SHUFFLE control on all eight fields** (availability 0.751891, recall_at_1
0.037821, recall_at_5 0.104387, availability_conditioned_recall_at_1 0.050302,
n_availability_conditioned 497, n_probe_subjects 661, live_banked_recall 0.097561,
n_banked_correct 4 -- verified by direct dict comparison, `True`); its own band is
**`MASS_NOT_CONTENT`** ("delta >= +0.03 but ON does not beat BOTH controls by >= +0.02").
**NOT an indictment of the cells:** `exp_wire_definitional_v1` carries explicit
`NO_QUALITY_CLAIM` ("No hand-scoring was performed and no quality claim is made") and a
`CIRCULARITY` disclosure. The cells were honest; the **0.90 is a documentation-layer number with no
experiment behind it.** Do not quote it.

**C21. THE THEMATIC-ROLE LABELER'S "0.95 HELD-OUT" IS PARSE COVERAGE, AND THE MODERN-PROSE
REVALIDATION IS A HARD_FAIL.** Provenance traced: the only on-disk source is
`notes/research_next_benchmark_after_propara_trap_check_2026-08-10.md:11` and `:301`, both of which
read "native LOCAL thematic-role reading at **0.95 parse coverage**".
`notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md:158` restates it as "local thematic-
role reading (0.95 held-out)" -- **a coverage number transcribed into an accuracy number.**
Off disk: `exp_thematic_role_labeler_qasrl_modern_revalidation_v1` verdict **`HARD_FAIL`**,
`mean_qasrl_noncanon` = **0.7442**, `n_noncanon` = **3937**, `n_canon` = 9820, 5 seeds, and its own
`verdict_msg` states the reason: *"single-cue ablation (animacy_only) reproduces full model within
0.05 ... disguised single-cue rule on modern prose too"* (`animacy_only` 0.7203 vs full 0.7442 on
that slice; 0.8623 vs 0.8666 on the MCGuffey repro slice).
**What stands:** `exp_thematic_role_labeler_cue_integration_v1` is a genuine **HARD_PASS** at
`mean_full_acc` **0.8666** vs `positional_baseline` 0.6032, 5 seeds -- **but n_test = 63**, and its
own `best_single_cue` was `frame_only@0.6984 (matches_full=False)`. The honest statement is: the
labeler passes on a 63-item curated set and FAILS at n=3937 on modern prose because one cue does its
work. **This cell family is the one place the strongest floor (single-cue ablation) was actually
run -- and at scale it beat the system.** That is a model for the discipline, not a scandal.

**C22. CORRECTION TO THE CORRECTION: `A5_STRINGCTRL` IS STILL NOT A ZERO-MEANING ARM -- C16
STANDS.** The VET describes `exp_meaning_supply_separation_v1`'s `A5_STRINGCTRL` as "a pure
zero-meaning string control". Re-verified in source, independently of C16:
`experiments/exp_meaning_supply_separation_v1.py:235-240` defines
`arm_scores(base, aux, w) = _z(base) + w * sum(_z(aux))`, and `:469` sets
`"A5_STRINGCTRL": [aux_t]` where `aux_t = t_mat[sel] @ tq`. The arm is therefore
**`z(base) + w*z(trigram)` -- it carries the FULL substrate signal plus spelling**, exactly as C16
recorded. Any restatement must use the corrected description ("a spelling channel added to the base
arm"), never "zero-meaning control". The **standalone** zero-substrate arm is a different object in
a different cell: `exp_orthographic_floor_vet_v1`'s `A6_TRIGRAM_ONLY` (see entry 37), and that one
IS `t_mat[sel] @ tq` with no base term.

**C23. THE "237.7M-TOKEN ENCODER" IS A 121.1M-TOKEN ENCODER TRAINED ON A 237.7M-TOKEN CORPUS, AND
WIRING IT INTO C3 WAS ALREADY TESTED AND BEATEN.**
`data/exp_scale_meaning_learn_arc_heldout_v2/metrics.json` `results_summary.trained_tokens` =
**[121082196, 121082196]** -- **121.08M, not 237.7M.**
**ORIGIN OF THE ERROR, FOUND:** both training cells' docstrings read
`ARC_Corpus (data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt: 237.7M alpha tokens, 14.62M
sentences)` -- `exp_scale_meaning_learn_arc_heldout_v2.py:21` and
`exp_scale_meaning_learn_arc_heldout_v3_relobj.py:60`. **237.7M is the size of the CORPUS the
sampler drew from; it is not the training budget.** The two were conflated in restatement.
**HONEST FORM, to be used everywhere: "a 121.1M-token encoder trained on a 237.7M-token corpus."**
The mislabel also sits in `experiments/exp_meaning_supply_separation_v1.py:180` ("the 237.7M-token
lineage") and in the `scale_win_tinytransformer_encoder` row of `data/capability_registry.jsonl`
(**not corrected here -- that file is owned by another pass; flagged, not edited**).
*Scope note on this correction: the auditor verified the two docstring sites and the
`trained_tokens` field directly. A full enumeration of every metrics.json for a token count in
[200M, 300M] was attempted and did NOT complete within the time budget, so no absence claim of that
form is made here -- cf. C19.*
**The encoder's own-task win is REAL and is NOT demoted:** that cell's verdict is
**`HARD_PASS_CLEAN_WIN`**.
**What is refuted is the TRANSFER, and it was already measured** (`exp_meaning_supply_separation_v1`,
`c0e6ec0da`, verdict **`MIDDLE_BAND_ARGMAX_ONLY_SUSPECT`**). At the pre-declared w=0.50, off disk:
`A1_BASE` **0.0480**, `A2_NORMS` **0.07125**, `A3_ENCODER` **0.0750**, `A4_BOTH` **0.0940**,
`A5_STRINGCTRL` **0.0905**. The spelling-add-on arm reaches **96% of A4_BOTH's score and 92% of its
gain over base** ((0.0905-0.0480)/(0.0940-0.0480)). The cell's own conclusion fields read
`encoder_gain_exceeds_string_control: false` and
`encoder_gain_attributable_to_string_similarity: true`.
**Therefore: the encoder is not an untapped asset for C3. It is a measured, floored, already-beaten
one.** Treating "supply the encoder" as the next move re-runs `c0e6ec0da`. See DO-NOT-REDO 31.

**C24. THE 39,707-WORD SENSORIMOTOR NORMS ARE NOT AN UNUSED ASSET -- STALE IN BOTH DIRECTIONS.**
(a) NOT unwired: `hdlab/lexical_similarity.py:599` has
`concept_similarity(word_a, word_b, use_grounded_fallback: bool = True)` -- the norms have been a
**default-ON fallback since 2026-08-11**. What is true is narrower: the live reading loop never
calls `concept_similarity`.
(b) NOT unmeasured: on 124 both-covered blind pairs the NOISE class sits **ON** the random-word-pair
Lancaster floor (**0.8071 vs 0.8060**) while non-NOISE sits at 0.8834, AUC 0.685 **in-sample**
(`notes/grounding_asset_inventory_2026-08-13.md:248-249`).
(c) Structurally inert by construction: `hdlab/grounded_similarity.py:96` `GROUNDED_CAP = 0.45`,
and the module's own docstring (`:41-42`, `:94`) states it sits **below**
`lexical_similarity.SIMILARITY_LINK_THRESHOLD` (0.50) -- so it can never flip a same-idea decision.
(d) Wired into the C3 harness it gives `A2_NORMS` **0.07125** at w=0.50, **below** the 0.0870
spelling floor.
This is DO-NOT-REDO 11 ("sensorimotor norms as FILTER") in a new costume; it was shelved with
revival criteria, not overlooked.

**C25. THE STORE'S "SHORTLIST-HIT 0.853 @ 1.2M" IS ARITHMETICALLY RIGHT AND OUT OF SCOPE.**
Recomputed off `data/exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1/metrics.json`:
`per_scale.1213912.hierarchical_sparse.relevant_in_shortlist_rate` = **0.8533** = 64/75
(`n_relevant_queried` = 75, so the third digit is noise). But the cell's `verdict` is
**`MIDDLE_BAND`**, and its declared `hp_scope.hierarchical_sparse` =
`["relevant_recall", "false_pull_in_rate", "scramble_margin"]` -- **`relevant_in_shortlist_rate` is
not in scope.** The in-scope headline at full cardinality is `relevant_recall` = **0.2133** against
`HP_RECALL_MIN` = 0.50; `checks.recall_ok_both` = **false**, `checks.margin_ok_both` = **false**,
`checks.margin_1213912` = 0.1333 against `HP_MARGIN_MIN` = 0.30.
**FLOOR INVENTORY, enumerated over the per-scale arm keys of stage2b/2e/2f/2g rather than searched:
the only floor arm that exists anywhere in the store arc is `scrambled_tier2`** -- a label-scramble,
the weakest baseline there is. There is **no node-degree, popularity, or relation-conditioned-
frequency floor anywhere in the arc**, and CSKG object distributions are heavily skewed, so
"return the 50 highest-degree objects for this relation from this leaf" is a plausibly strong and
completely unmeasured baseline for exactly the quoted metric. **This is the single highest-value
missing floor currently identified** and it is the reason "the store solved candidate retrieval"
may not be stated unqualified.

**C26. FHRR "SELF-CONSISTENCY 0.956" IS EXACT, AND ITS CELL IS A HARD_FAIL SCORED AGAINST A BARE
ABSOLUTE.** Recomputed: `capacity.retrieval_self_consistency` = **0.9556** = **215/225**
(`fhrr_dim` 4096, `n_registers` 15, `mean_load` 15.0, `max_load` 30). The cell's `verdict` is
**`HARD_FAIL_no_rise+no_fade_lesion_gap+scramble_no_collapse`**. Its band was
`bands.SEPARATES_MIN_SELFCONSIST = 0.85` -- **a bare absolute number, the exact pattern retired by
STANDING DISCIPLINE 8**; a majority-fate floor was never run. Its scramble control **inverted**:
`scramble.retained_fraction` = **1.1663** (>1, the scramble arm scored HIGHER), waved through in
`diagnosis.scramble_caveat` as small-N noise.
**What survives, precisely:** the cell's own `final_verdict` is
`HARD_FAIL_PARTIAL_BOOTSTRAP_but_superposition_separates_rules_out_averaging`. The FHRR
bind/bundle/unbind algebra demonstrably separates 225 conjunctive keys over 15 registers at d=4096
rather than averaging them -- **that refutation of the averaging hypothesis stands**. What may NOT
be claimed is "storage solved + brain-faithful": the retrieval is a 3-way argmax over
`EFFECTS = ('CREATE','MOVE','DESTROY')` (chance 0.333) at a load ~2 orders of magnitude below what
the store arc runs at.

**C27. WHAT THE 15-CLAIM VET LEFT STANDING (recorded so the propagation is not read as blanket
demotion).** Re-verified off disk by the propagating auditor:
- **MAVEN-ERE stands, and is the reference case.**
  `data/exp_maven_ere_convergence_gated_causal_v2_fulldev/metrics.json` verdict **`HARD-PASS`**,
  `official_micro_f1_positive_only.f1` = **14.7834** (P 11.489 / R 20.728) against
  `order_majority_floor` **5.9305** -- and **four** floors were run, not one (majority **0.0**,
  `bag_of_event_types` **0.6375**, `adjacent_sentence_heuristic` **0.7270**, order_majority 5.9305).
  **The strongest available floor is the one quoted and it was cleared, 2.49x.** Two scope
  qualifiers travel with it: accuracy_pct is a trap (positives are 2.2% of pairs, so scramble scores
  HIGHER accuracy than the system), and the lift is carried by the learner plugin, not the
  convergence gate the cell is named for (`gate_learned_noentity` f1 **14.860** exceeds full_v2's
  14.783).
- **4.80% < 8.70% stands, CI-separated** (entry 34 / C12).
- **The 359-word hand lexicon is exact** -- `data/exp_reading_grounding_loop_cycle2_v1/metrics.json`
  `hand_lexicon_baseline` = **359**, `progress_toward_hand_lexicon` = 9.8719.
- **Growth cleanliness stands** -- same cell: `no_leak_ok` true, `scramble_ratio` **0.07705**,
  `monotone_growth_ok` true, persistence round-trip ok.
- **The graded comparator is a scoring layer, not the store** -- unchanged; its HARD_PASS stands on
  its own 2AFC scorer, and only the carry-across to C3 is refuted (entry 35).
**A refuted FRAMING is not a refuted RESULT.** Six of the eight items above are framing/scope
corrections sitting on numbers that reproduce exactly.

---

## STANDING DISCIPLINES -- entries added 2026-08-15 (auditor, atom-triage residue)

Stubbed in `STATUS.md` as standing disciplines **9** and **10**.

### 9. A KEYWORD DETECTOR READS A SCOPE DISCLOSURE AS THE OVERCLAIM -- so hand-adjudicate every large flag class before believing it

**Bought with the atom-triage misstatement pass**, whose flags did not survive contact with the
files they were about.

> **Our detectors fire on honesty.** A cell that names the scale it did not reach is behaving
> exactly as this project's discipline demands. A keyword detector reads that disclosure as the
> overclaim. The audit is therefore **biased against the most careful cells**, and no large flag
> class may be believed until it is hand-adjudicated.

**The measured incident.** All **7** misstatement flags that two hand-reading passes overturned
were triggered by cells *explicitly disclosing their own scope*:

- one says `REGIME SCOPE (honest): N=512` and was flagged **for naming the `N=4096+` it stated it
  had NOT tested**;
- another's only mention of a large scale sits inside a field named **`open_followup_cells`** -- a
  proposal for future work, not a claim about work done;
- the rest fire on **prior-landing reference values** (`SPARSITY-NEUTRAL at N=2048 (replicate of
  the N=1024 finding)` -- N=1024 is a back-reference) and on **a file legitimately citing itself**.

**The adjudication record, which is the argument.** Three passes triaged overlapping atom
populations. Two hand-read; one ran detectors at scale. There were **11 disagreements. All 11
resolved against the scaled detector** -- 10 against pass C, 1 against pass A, 0 against pass B.
The two passes that hand-read agreed with each other.

**Confirmed independently on the residue (2026-08-15).** The uncovered residue was triaged on the
same five defect classes, with every detector self-tested on a known positive AND a known negative
first. They produced **30 candidates; hand-reading overturned 30 of 30.** Across three passes this
detector class now stands at **49 candidates, 49 false positives, 0 survivors.**

**Two false-positive mechanisms, both worth recognising by shape:**

1. **The arm exists under a different name.** The detector asserts "the atom names a comparison
   arm absent from the artifact". Worked example:
   `exp_conceptnet_rerank_parity_multiseed_v1` was flagged for naming oracle + control + ceiling.
   Its metrics file carries `closure_hits10` = 1.0 (*that is* the oracle) and `random_floor_hits10`
   = 0.0515 (*that is* the control). Atom prose and metrics keys are two vocabularies for the same
   arms.
2. **A derived number is absent from the file BY CONSTRUCTION.** Demanding that every cited number
   appear verbatim in the artifact fires hardest on the atoms that did the **most** independent
   recomputation. Of 61 such "missing" numbers, **60 are a difference, mean or ratio of the file's
   own values**, and the 61st is a Poisson chance-floor statistic that recomputes exactly
   (mu = 304/1024 = 0.2969, P(0) = exp(-mu) = 0.7431, P(0)^3 = **0.4104**, cited as 0.41).
   Verified by hand against named keys: per-seed lift `0.047` = `SEM_RERANK_RRF_hits10` 0.5708154
   minus `RANDOM_BEAM_hits10` 0.5236051.

**The discriminator that does work is REPRODUCTION, not vocabulary.**
`exp_kf2_isolation_proof_v2_n8192` is a true positive because its config N is **1024** while its
verdict asserts `PROVED N=8192 ... at production scale` -- the scale does not reproduce. Two
residue atoms of apparently identical shape both CLEAR:
`EXP_metric_dependence_top_k_semantic_v1_seed_7_smoke` claims `N_c=8192, N_h=4096, sparsity=0.1,
load=[0.1,0.2,0.3]` and the file carries exactly those; and
`EXP_substrate_relation_type_binding_cross_domain_analogy_v1` claims `3-seed smoke [7,13,19] at
V=1024 N=8192 K=10` against a file with `N_DIM=8192, V_ENTITIES=1024, K_SHOTS=10,
seeds=[7,13,19]`.

**Corollary, and the reason both cleared: in this codebase `smoke` means REDUCED SEEDS, not
reduced N.** A smoke run at N=8192 is honest and ordinary. "Smoke + a large N in the text" is NOT
a defect signature; a detector built on that premise flags the disclosure and misses the real
thing.

**Report the DENOMINATOR with every zero.** A class that fires 0 times against 0 applicable atoms
is an INAPPLICABLE test, not a clean result, and reporting it as "0 defects" is the same overclaim
the audit exists to catch. Residue example: class 3 (directory name contradicting config) found 0
defects against a denominator of **0** -- no residue artifact directory carries an N token at all.
Class 5 also found 0, but against a denominator of **128**, with the detector self-testing PASS on
a known positive pair -- a *meaningful* zero. The two zeros are not the same claim.

### 10. A JOIN THAT SILENTLY FAILS TO MATCH FABRICATES BOTH REASSURANCE AND ALARM

The single most dangerous tool defect found in this audit, and the companion to discipline 9: the
same class of silent mis-reading, running in **both** directions at once.

> A join that does not match does not error. It returns a smaller set, and the smaller set reads
> as a *result*. **Never report a join-derived count without first proving the join matches on a
> known-present pair.**

**Incident A -- false GREEN.** Dropped id prefixes left **314 of 400 atoms silently unjoined**
inside one pass, which read as a clean population rather than as a broken join.

**Incident B -- false RED, from the same defect.** "Only **812 of 1,925** ledger ids exist as
atoms" was the most alarming number in the whole triage. It is a raw-id artifact: ledger rows are
written `math::T3/EXP_...` while most store partitions write `T3/EXP_...`. Normalised on both
sides the figure is **1,893 of 1,925** -- so **32 absent, not 1,113**. The reconciliation gap was
overstated **35-fold**.

**The canonical key that fixes it:** strip a leading `<corpus>::`, then strip ONE leading tier
segment (`T<n>/`, `T_<word>/`, `META/`). Measured effect of getting this wrong: a raw-id merge
**invents 341 phantom atoms** (union 5,176 vs 4,835) and reports one pass-intersection as **22
instead of 307**.

**Incident C -- normalising the VALUE does not save you if you assume the FIELD NAME.** Found
2026-08-15 while re-deriving the above. The merge's ledger enumeration reads the field `atom_id`;
**4 of 2,031 ledger rows carry their id under `id` instead** (schemas
`['id','seq','anchor_name','tier','cert_status']` x3 and
`['id','anchor','tier','cert_status','author_verdict']` x1). Those rows sat silently outside the
triageable universe. Corrected: distinct ledger ids **1,929** not 1,925; triageable union **5,098**
not 5,095; uncovered residue **263** not 260; ledger ids present as an atom **1,896 of 1,929**;
genuinely absent **33** not 32. Small in size, exact in shape: **value-normalisation and
key-presence are two separate failures, and fixing one does not fix the other.**

**Sub-rule: the truncation family, which bit the audit tool itself.** A hand-adjudication table
keyed on **truncated** atom names printed to screen (`n[:70]` / `n[:75]`) silently failed to join
**7 of 11 rulings**, leaving 5 already-cleared false positives still counted as defects. Elsewhere
the same family split `N=8192` into `N=81` and manufactured roughly **700 false positives**. It
recurred on 2026-08-15 in the residue pass: extracting cited numbers from a 700-character
**excerpt** rather than the full atom text manufactured 19 spurious "partial / none reproduce"
rows, all of which dissolved when the full text was used.

**How it was caught, and the rule that follows: ASSERT, THEN COUNT THE JOINED ROWS.** The merge
asserted "all 11 adjudicated", then printed the join result and counted ADJ-OK rows: **4**. **The
assertion caught what the eye did not.** So: after any join, assert the expected cardinality and
print the residue. Self-test every pattern against a known positive AND a known negative before
trusting a count -- the residue pass's own canonicaliser was validated on 6 positives and 5
negatives, and its class-2 detector **failed its own known positive on first run** because the
self-test read the field `claim` while templated atoms carry their text in `description`. That
failure was the tool being wrong in exactly the way this discipline predicts, caught only because
a known positive was run through it.

**Prefer withdrawal to accumulation.** The merge withdrew its own reading of the wave14 family
after finding those files contain no numeric results outside prose, so payload identity merely
restates config identity. An artifact whose only numbers are its config collides with every
sibling under a numeric-payload comparator whether or not anything was double-banked.

---

## CAVEATS THAT TRAVEL -- added 2026-08-15 (residue audit); CARRY VERBATIM

These two are being misread downstream. Quote them as written.

**CT1. The scope limit on the largest triage bucket.**

> **Consistent on checked axes means an atom does not contradict its artifact on mode, scale,
> seeds, name or independence. It does NOT mean the result is good.**

`CONSISTENT_ON_CHECKED_AXES` is the largest bucket in the merge at **3,654** atoms. It is a
**citation-safety** result, not a **quality** result: it says the atom's words match its file, and
says nothing about whether the experiment was worth running. The worked example that proves it:
**one atom so labelled is a smoke pass at 1.000 with no comparison arm.** Never let this bucket be
paraphrased into a clean bill of health.

**CT2. `run_mode` in templated atoms is an ingestion constant, not a measurement.**

> **All 162 say `full`. Four contradict their file; the other 158 agree by coincidence. Never gate
> or certify on it. Read the mode from inside the `metrics.json`.**

Confirmed on a fourth independent population 2026-08-15: across the 263 residue atoms the
`run_mode` field takes exactly two non-null values -- `full` (22) and
`full_config_independently_recomputed` (1). It is **never** written as `smoke`, even though 8 of
the residue's resolved artifacts *are* smoke -- and every one of those 8 has no `run_mode` field at
all. This matters more than the "0 inversions" headline suggests: 0 inversions reads as *the field
is trustworthy*, when the truth is that **the field is only ever populated when the answer is
`full`**, so its agreement carries no information. `tools/skunkworks_cert_integrity_audit_v1.py`
D2 already checks `run_mode == smoke AND provenance_quality == CERT_CHAIN_GRADE`; that check is
reading the ingestion default, not the run.

---

## DO NOT REDO -- entries added 2026-08-16 (auditor, off-data recompute)

Continuing the numbering. Stubbed in `STATUS.md` as entries **38-42**. Every number below was
recomputed by the auditor off the artifact named beside it, not read from a report.

**38. BRIDGING GROUNDING ACROSS A RELATION GRAPH, WITH THE THEMATIC HUB SUPPLIED -- MEASURED
NULL.** `data/exp_thematic_relation_supply_bridged_grounding_v2_smoke/metrics.json` (SMOKE:
N_BOOT=2000, N_PERM=400; the FULL is still running and may move the CI widths, not the point
estimates). Verdict `BRIDGED_CODES_DO_NOT_CLEAR_THE_FLOOR_ON_OUR_GRAPH`. Primary stratum
PRIMARY_DEF_THEMATIC_CORE, n=394, mean in-CORE bridge degree 3.573, `ADDITIVITY_EXERCISED=true`:
`B1_BRIDGE_MEAN` rho **0.0270** [-0.0736,+0.1267]; the best of the five additive transformations is
`B5_BRIDGE_TOP3_PMI` at **0.0406**. Floors recomputed on the identical stratum/scorer/gold:
F_ORTHOGRAPHIC 0.0412, F_FREQUENCY_HARDENED 0.0209, F_SCRAMBLE_PERM_P95 0.0900 (higher of row- and
gold-permutation p95, not a max-of-draws). Margin over the strongest floor **-0.0615
[-0.2109,+0.0869] NOT_SEPARATED**, permutation p=0.2768. Holds on all four control configs
(MORPHBLOCK 0.0288, C6a partner-context-excluded 0.0220, C6b never-co-occur 0.0159, HUBCENSOR
0.0029). **The instrument is alive:** K1_OWN_NORMS 0.3301 [0.2305,0.4254] ABOVE and K2_ORACLE_BRIDGE
0.2893 [0.1888,0.3822] ABOVE, so G0 passes on every whole-stratum config and this is a REAL null,
not a dead ruler. **Revival criterion (brain-framed, not performance-framed):** edge TYPING -- the
thematic edges here are UNTYPED co-participation, whereas the brain's thematic relations are
role-structured (agent / patient / location / instrument). We own `extract_predicates_v62`
(`hdlab/definitional_predicate_v61.py`) and have never run it at scale. Re-open when a role-typed
graph exists, not before.

**39. SPARSIFYING THE READING ANCHOR (the high-rank object) -- COLLAPSES ON THE REAL TASK.**
`scratch/sparse_code_real_task/real.json` + `mechanism.json`. hit@1 is MONOTONE INCREASING in
active fraction over a 250x range and in BOTH architectures (in-place d256: 0.0130 at f=0.002 ->
0.0483 at f=0.50; expand-then-cap: 0.0120 -> 0.0428), i.e. every sparsification makes it worse, and
the densest point merely returns to the dense incumbent 0.0481. All 18 arms are CI-separated BELOW
the spelling floor 0.0866. Under a PARTIAL cue the expand-then-cap family falls below its own
scrambled null. **Mechanism, hypothesis written before the measurement:** a k-cap keeps the
largest-drive coordinates, which is signal-preserving only on a LOW-EFFECTIVE-RANK source. Measured
participation ratio: reading anchors **88.74 of ambient 256** (34.7%); the lifted grounded norms
**9.15 of ambient 1024** (0.89%) -- a 39x difference as a fraction of ambient. At f=0.002, 99.55% of
reading-anchor pair cosines are EXACTLY ZERO: the code stops being a similarity space and becomes a
near-orthogonal hash. **Revival criterion:** sparsify the LOW-RANK GROUNDED asset, not the anchor.
That object is where the same operator wins (see "SPARSE CODE" below).

**40. QUOTING +0.2285 AS THE BRIDGING CELL'S TREATMENT MARGIN.** See correction C28.

**41. QUOTING A "0.073 LIFT GAP" / "a quarter of the signal lost to SimHash".** See correction C29.

**42. USING `grounded_similarity()` AS A SCORER, EVER.** `hdlab/grounded_similarity.py`. Measured
and RE-EARNED BY RUNTIME in every probe that touches it: over 999 SimLex pairs it returns 229
distinct values, with **654 pairs at exactly 0.45 (the GROUNDED_CAP) and 107 at exactly 0.0 --
76.18% of all pairs on two values**. Any rho computed through it is a rank statistic over a
two-valued variable. Cells that need a grounded score use the raw 12-dim vector, L2-normalised,
plain cosine. `exp_thematic_relation_supply_bridged_grounding_v2` asserts the saturation in its own
selftest and aborts if it ever stops being true. This is not a style preference; it is a trap that
has been re-armed rather than removed. **No revival criterion** -- the function is fine for its own
gating job; it is a SCORER that it must never be.

---

## CORRECTIONS TO PRIOR CLAIMS -- added 2026-08-16 (auditor, off-data recompute)

Stubbed in `STATUS.md` as **C28-C31**. Each preserves the superseded claim verbatim and names what
replaced it; none is a silent rewrite.

**C28. THE "+0.2285 CI-SEPARATED MARGIN OVER THE SPELLING FLOOR" IS NOT A RESULT ON THE INSTRUMENT
THAT MATTERS.**

> SUPERSEDED CLAIM: "the thematic channel clears the spelling floor by +0.2285 [+0.1861,+0.2717]
> even after morphology blocking."

That number is real and its own author labelled it correctly: it is the relation-supply scan's
NEIGHBOUR-CHOICE diagnostic -- cosine between the mean of a held-out word's d=1 CORE neighbour codes
and that word's own hidden 12-dim code, against a floor in which SPELLING chooses the neighbour
(`.claude/scan-out/relation-supply.json` STEP_4, which says verbatim "A SUPPLY DIAGNOSTIC ON A
DIFFERENT QUANTITY FROM THE PHASE-2 VERDICT, and it must never be quoted as that cell's result").
**On the bridging cell's own instrument -- SimLex rho, same stratum -- the bridged arm's margin over
the orthographic floor is -0.0142 [-0.1636,+0.1397], NOT_SEPARATED**
(`data/exp_thematic_relation_supply_bridged_grounding_v2_smoke/metrics.json`,
`PRIMARY_DEF_THEMATIC_CORE.arms.B1_BRIDGE_MEAN.DECOMPOSED_per_floor.F_ORTHOGRAPHIC`). SUPERSEDED-BY:
this entry. The supply diagnostic still supports what it was built to support -- that our edges
point at genuinely-related words -- and supports nothing about transported meaning.

**C29. THE "0.073 LIFT LOSS / a quarter of the signal" IS 0.0034.**

> SUPERSEDED CLAIM: "SimHash quantisation costs ~0.073 rho, about a quarter of the signal."

`data/exp_meaning_lift_population_code_v1/metrics.json`: the incumbent SimHash, re-implemented
bit-identically through `hdlab.hub_spoke_word.bipolar_quantize`, scores **0.2667 at d=256** and
0.2680 at d=1024 against a ceiling of **0.2701**. The gap is **0.0034** (d=256) and 0.0021 (d=1024)
-- 3% and 2% of the assumed 0.073. The 0.073 came from comparing this ruler's number against
`exp_hub_spoke_word_g3_cleanup_rescore_v1`'s landed 0.1977, which used a different projection seed
and a different OOV policy: a number carried between populations. **Consequence that must travel
with it:** every closure fraction in that cell divides by ~0.003, so the closure values -110.28,
-102.12 and +31.15 are arithmetic on a degenerate denominator and MUST NOT be quoted as effect
sizes; gate G0 was unreachable by arithmetic and its failure is NOT evidence against the candidates.
The cell's pre-registered mechanism prediction (Goemans-Williamson: a signed random projection
should cost ~zero rho, and the loss should shrink with d) is CONFIRMED: 0.003402 at d=256 ->
0.002137 at d=1024.

**C30. "RETRIEVAL IS FINE, WE TIE SPELLING" IS AN EXACT-KEY, OPTIMISTIC-TIE STATEMENT, AND BOTH
QUALIFIERS ARE LOAD-BEARING.**

> SUPERSEDED CLAIM: "retrieval FINE -- top-50 55.65% vs spelling 54.55%, CI NOT separable;
> SELECTION FAILS."

Recomputed off `scratch/sparse_code_real_task/real.json`, 3,994 scored items, identical pool and
gold. Three things are true at once and the standing claim states only the first:

1. **TIE CONVENTION.** The trigram floor has 15.27% of the eligible pool tied with the gold; our
   dense read-out has 0.0%. Under the OPTIMISTIC convention our top-50 margin over spelling is
   +0.0105 [-0.0080,+0.0290] NOT_SEPARATED (the standing claim, and it reproduces exactly). Under
   the CONSERVATIVE convention it is **+0.0641 [+0.0456,+0.0829] ABOVE**. Note the DIRECTION: the
   conservative convention penalises the arm holding the tie mass, which is the FLOOR, so this
   correction runs in OUR favour, not against us. Any relay saying "spelling is above us by
   +0.0641" has the sign backwards. Neither convention is obviously right; what is established is
   that the comparison hinges on a choice nobody had stated.
2. **THE FLOOR IT NEVER FACED.** PURE CORPUS POPULARITY -- always answer with the commonest
   permitted word, reading nothing -- reaches top-50 **0.5235** [0.5078,0.5388] against our 0.5566.
   Our margin over it is +0.0331 [+0.0155,+0.0508]: CI-separated, and small. A top-50 metric on a
   5,491-anchor pool is largely a popularity measurement.
3. **THE REGIME.** All of the above is the EXACT-KEY operating point. Under a PARTIAL cue (a single
   held-out sentence, which is the regime the brain actually operates in) our top-50 falls to
   **0.3758** while spelling holds 0.5461 (optimistic) / 0.4925 (conservative) and popularity holds
   0.5235: we are **CI-separated BELOW spelling (-0.1167 [-0.1352,-0.0981] conservative; -0.1702
   optimistic) and BELOW popularity (-0.1477 [-0.1650,-0.1304])**, and above only the scrambled
   null (+0.0693). hit@1 falls 0.0481 -> 0.0223, BELOW spelling by -0.0644 [-0.0741,-0.0546] and
   NOT separated from the frequency floor.

SUPERSEDED-BY: this entry. What SURVIVES unchanged: at hit@1 (single convention, no tie mass on the
dense arm) spelling still beats us 0.0866 vs 0.0481, in both regimes. What must STOP: quoting
"retrieval is fine" without naming the regime and the tie convention.

**C31. `tools/verdict_bar_check.py` HAD A FALSE-PASS DEFECT, AND IT WAS THREE DEFECTS, NOT ONE.**

The scanner at `c0802fc36` could select a PLANTED-ANSWER validity arm as a cell's claim-carrying
arm and return MEETS_BAR off it (+0.9044 on `S_INPLACE_d256_f0.020__KA`, an arm whose own node reads
hit@1 = 1.0 with zero bootstrap variance). Reproduced exactly off disk before any edit. The three
defects: (D1) the path walker joined segments with `.`, and arm names contain literal dots
(`f0.020__KA`), so a name lost its boundary; (D2) the selector classified only the LAST path
segment, which was the CONTAINER `MARGIN_per_floor` -- this made the role classifier's CORRECT
answers irrelevant and let through 9 `__KA` and 9 `__NULL` arms, so a lexicon fix alone would have
excluded none of them; (D3) the role lexicon did not know `__KA` / `KA_QUERY_IS_GOLD_VECTOR` /
`PLANTED`. Now fail-closed: if no arm is ELIGIBLE the status is **NO_EVIDENCE**, never MEETS_BAR and
never FAILS_BAR (the first cut returned FAILS_BAR, which pooled the deliberately-losing null arms
and reported their negative bound as a measured refutation of an arm that does not exist -- the
exact conflation behind the 17 corrections-of-a-correction). Exclusions are now REPORTED, never
silent. **The defect is ANTI-CORRELATED WITH RIGOUR:** only a cell that ships planted-answer
validity arms can trip it, so the better-instrumented the cell, the more exposed it was. **Until the
full re-scan lands on the fixed code, a MEETS_BAR from this tool is not evidence.** A named,
unpatched SCOPE limit remains: the tool scores a cell on its best arm ANYWHERE in the cell, so a
cell shipping two instruments can have an encoding-side clearance reported beside a reading-task
verdict string.

---

## STANDING DISCIPLINES -- entries added 2026-08-16 (auditor)

Stubbed in `STATUS.md` as standing disciplines **11-13**. All three are one failure mode seen from
three angles: a number is only meaningful together with the ruler that produced it.

### 11. A NUMBER MAY NOT BE CARRIED BETWEEN SCORERS OR POPULATIONS

> **A margin, a rho, a hit-rate or a lift belongs to the scorer, the item population, the pool and
> the gold set it was computed on. Moving it to another one is fabrication, even when both numbers
> are individually correct and even when the same word names both quantities.**

Cost, in one night, three times: the +0.2285 neighbour-choice diagnostic quoted as a bridging
treatment margin, where the same cell's own instrument reads -0.0142 (C28); the 0.073 "lift gap"
that is 0.0034 once both sides are computed on one ruler (C29); and the "retrieval is fine" tie that
depends on a convention and a regime nobody named (C30). The tell is a comparison whose two sides
come from different files. **Before quoting a margin, name the scorer, the n, the pool and the gold
-- if you cannot name all four for BOTH sides, you do not have a comparison.**

### 12. A CLAIM MEASURED AT THE EXACT-KEY OPERATING POINT DOES NOT TRANSFER TO THE PARTIAL-CUE REGIME, WHICH IS THE REAL ONE

> **Exact-key retrieval and partial-cue completion are different capabilities. A number measured
> with the whole key in hand says nothing about the regime the system will actually be used in, and
> the gap is large enough to reverse a conclusion.**

Measured (C30 item 3): top-50 0.5566 at the exact key, **0.3758** under a single held-out-sentence
cue -- from "ties spelling" to CI-separated below both spelling and pure popularity. Independently,
the storage instrument shows the same shape structurally: `HDFactStore` is genuinely ADDRESSED
(key-sensitivity 2.0) and degrades gracefully to 62.5% cue overlap, but its LIVE read path is an
exact content-hash index that returns 1.0 at full overlap and **0.0 at the first flipped bit**, and
its shipped cosine threshold 0.75 cliff-edges at 87.5% overlap -- the partial-cue tolerance of the
shipped path is a config constant. This is the same fault that shelved `perirhinal_conjunctive` on
"exact-key retrieval only" and hid the missing CA3 completer. **State the cue regime beside every
retrieval number.**

### 13. REPORT TIE CONVENTIONS BOTH WAYS, NEVER SILENTLY PICK THE FLATTERING ONE

> **Any rank or top-k metric over a scorer that can produce ties has TWO answers. Publish both, or
> the comparison is a choice presented as a measurement.**

Cost: the whole "we tie spelling at top-50" reading (C30 item 1), which flips from NOT_SEPARATED to
+0.0641 ABOVE depending on how a tie is counted, because the floor holds 15.27% tie mass and we hold
0.0%. Prefix-only is worse still (29.37% tie mass: top-50 0.5771 optimistic vs 0.3485 conservative,
median rank 33 vs 155.5). `tools/verdict_bar_check.py` now APPENDS the convention to the floor name
(`F2_PREFIX_ONLY|optimistic_ties`) and takes the min across conventions, so the flattering one can
no longer be picked silently by the bar machinery. **Residual, named and unsolved:** a cell that
publishes only ONE convention still has an unstated choice, and the tool reads
`tie_conventions_present = []` for it.

---

## THE TWO RELATIONAL HUBS (2026-08-16) -- stubbed in `STATUS.md` as "TWO HUBS"

**We had built one of the brain's two relational systems.** TAXONOMIC relations (shared features;
anterior temporal lobe) we had: all 5,799 rows of our definitional fact files are
`GROUNDED_MEANING`, 100% taxonomic-definitional (COPULA 2006, APPOSITIVE 1521, CALLED 1303,
GLOSSARY_COLON 944, REFERS_TO 25). THEMATIC relations (co-participation in an event; a SEPARATE
temporo-parietal system -- pMTG and angular gyrus) we had not. The dissociation is PINNED and
causal, not a cognitive-theory label: lesion location predicts which error type a patient makes
(Schwartz et al. 2011 PNAS, voxel-based lesion-symptom mapping; Mirman, Landrigan & Britt 2017
Psych Bull). Thematic organisation is developmentally PRIOR (Nelson/Lucariello slot-filler
programme) -- and the honest counterweight, recorded because it cuts against the headline: a WORD
CUE is exactly what recruits the TAXONOMIC system (Markman & Hutchinson 1984), so the fix is
ADDITIVE, never a replacement.

**The organ was already on disk with no callers.**
`hdlab/definitional_extraction.py::extract_predicates` and
`hdlab/definitional_predicate_v61.py::extract_predicates_v62` produce role-typed thematic facts
(ENABLING_CONDITION 69, ENABLING_CONDITION_AGENT 49, PROCESS_ACTION 48, PROCESS_PATIENT 39,
ENABLING_CONDITION_PATIENT 16 in the 221-row v62 bank) and are called by nothing but their own
self-tests. A prereg deviation had recorded the ATL-vs-AG contrast as NOT CONSTRUCTIBLE; that was
true of the FILES and false of the SUBSTRATE.

**What supplying the missing hub bought, measured** (event co-participation over the identical
64,000,000-byte simplewiki budget the frequency floor is computed on, PMI>=2.0, count>=5, top-k 24,
sources = AoA<=6.0 CORE): mean in-CORE bridge degree **1.216 -> 3.573**, median 1 -> 3, primary
stratum **47 -> 394** pairs, both-endpoints stratum **4 -> 138**, verb stratum **0 -> 86** (the
Hills 2009 noun-specific falsifier became runnable on our own graph for the first time), adjectives
6 -> 49. It is NOT a spelling channel in disguise: the morphology blocker deletes 7 of 1,472 edges
(0.48%) and the score goes UP, not down.

**And it did not rescue bridging** -- DO-NOT-REDO 38. **Audit correction to the cell's own
`dissociation` block, which reads "OUR RELATIONS ARE STILL THE LIMITER":** that is not supported by
this cell's own arms. The EXTERNAL, hand-curated CSKG ceiling arm ALSO fails to clear
(`CEILING_CSKG_NOLEXREL_CORE_EXTERNAL_REFERENCE`, n=243, B1 0.0457, margin -0.0713
[-0.2499,+0.0953] NOT_SEPARATED) while ITS known-answer arms pass (K1 0.3256, K2 0.2934). So a
better relation set OF THE SAME KIND does not rescue it either; what clears is ORACLE NEIGHBOUR
CHOICE, which uses no graph at all. The evidence supports "neighbour CHOICE and/or the target space
is the limiter", not "our relation supply is the limiter". Recorded as a framing correction, not a
demotion: the cell's VERDICT is correct and stands.

---

## THE TARGET SPACE IS MISSING CHANNELS, NOT DIMENSIONS (2026-08-16) -- stubbed as "TARGET SPACE"

`notes/drill_target_space_dimensionality_semantic_representation_verbs_2026-08-16.md`, `03055c7fa`.
Our 12-dim landing space (11 Lancaster sensorimotor means + Brysbaert concreteness) covers **two of
the seven** attribute blocks the brain's semantic systems use, plus one scalar. Missing: AFFECT,
SOCIAL, SPATIAL/TEMPORAL/CAUSAL -- and taxonomic/thematic structure we carry only as a graph, never
as dimensions of the space a word lands in.

**Measured, paired, identical 977-pair stratum, 4000 bootstrap draws with a shared resample index,
plain cosine on the L2-normalised concatenation:** adding the three Warriner VAD columns lifts
Spearman rho vs SimLex from 0.3130 to 0.4143, **paired delta +0.1013 [+0.0615,+0.1419],
CI-SEPARATED**. Per POS: nouns +0.0253 (NOT separated), verbs **+0.1228** [+0.0150,+0.2314],
adjectives **+0.3399** [+0.1919,+0.4978]. **The gain profile mirrors the failure profile** -- the
word classes our bridging cannot carry are the ones the missing channel serves. Survives z-scoring
(+0.1344), so it is not a scale artefact.

**The negative control FIRED, and it is what makes this a channel claim rather than a width claim:**
adding 11 MORE columns from the SAME file (the Lancaster rater-SD columns, 23 dims) scores 0.3035,
and 6 derived nonlinear summaries of the same 11 dims (18 dims) score 0.3025 -- both BELOW the
12-dim incumbent's 0.3130. Widening without a new channel buys NOTHING.

**Scope, stated because it is easy to over-read:** this is a CEILING diagnostic in the K1 condition
(the word's own hand-rated code, no graph, no bridging). NO floors, NO null arm, NOT a cell, NOT a
verdict. It decides which spaces are worth putting into a can-fail cell; it clears nothing.
Independent sanity check that the scorer is not broken: our 11-dim Lancaster-only arm measures
0.3186 on 999 pairs against Wingfield & Connell's published |r| = 0.32 on 993 pairs.

**Two independent gates had excluded this channel, neither on a brain-framed criterion, and that is
the reusable lesson.** (i) `hdlab/grounded_similarity.py` lines 51-56 exclude Warriner because
affect is "not an identity-content signal" -- a cognitive-theory assertion never measured on the
meaning axis. (ii) `exp_grounding_multiattribute_fusion_v1` pruned valence/arousal/dominance on a
`MIN_TARGET_R = 0.20` gate whose TARGET is held-out CONCRETENESS; valence correlates with
concreteness at r = 0.025. Since the biology says affect is the grounding channel for ABSTRACT
concepts, an affect channel MUST be near-orthogonal to concreteness -- so that gate prunes it BY
CONSTRUCTION, every time, precisely by working correctly. The prior cell was NOT wrong for its own
task (predicting concreteness); carrying its pruning decision onto the MEANING axis would be the
cross-task carry of discipline 11. **What stands:** the zero-fill warning in `grounded_similarity.py`
is CORRECT and zero-fill REMAINS BARRED -- the fix is intersection-stratum evaluation.

---

## THE STORAGE INSTRUMENT NOW EXISTS (2026-08-16) -- stubbed as "STORAGE"

Supersedes the standing line "STORAGE has NO ISOLATED INSTRUMENT = step 1". Probes:
`scratch/storage_instrument_premise_probe_v1.py` / `scratch/storage_instrument_factstore_probe_v1.py`
(+ their `.json` results). **These are in `scratch/` and are now cited by a durable doc, so per the
CLAUDE.md scratch corollary they must be PROMOTED to `experiments/` or the citation dangles.**

**The flat store is ADDRESS_ABSENT, not address-degraded, and the distinction decides the repair.**
Replicating the shipped default line byte-faithfully (`acc += symbol_vector(filler)`, no key, using
the shipped codebook): key-sensitivity **0.0**, facet addressability **exactly 0.2500** = chance,
**sd 0.0 across 5 seeds**, invariant across M in {16,64,256} and cue overlap in {1.0 ... 0.5} -- all
15 cells read 0.2500 with zero variance and return BIT-IDENTICAL content for every query. A DEGRADED
address scores between chance and ceiling and FALLS with load; an ABSENT address is not repaired by
any amount of capacity, because there is no channel to widen. Independently corroborated by a
different route: `.claude/scan-out/wall2-wire-perirhinal.json` PART 4 measured 0.2534 for the same
store.

**`HDFactStore` IS addressed** (key-sensitivity 2.0; `_sr_key` verified bit-exactly) **and its read
paths throw the address away**: the live exact content-hash index returns 1.0 at full overlap and
0.0 at 93.75%; the shipped cosine scan cliff-edges at 87.5% because bipolar cosine at overlap p is
(2p-1) and the threshold is the config constant 0.75. The representation tolerates a partial cue to
62.5% overlap; the shipped path does not use that tolerance. See standing discipline 12.

---

## THE ONE ARM THAT CARRIES MEANING, AND WHY IT DOES NOT TRANSFER (2026-08-16) -- stubbed as "SPARSE CODE"

`data/exp_meaning_lift_population_code_v1/metrics.json`, arm `C1_KCAP_GRD_f005_BOOST` at d=1024,
3 seeds, 322 pairs: SimLex rho **0.2801** [0.1737,0.3806], `CLEARS_ALL_THREE_FLOORS_CI_SEPARATED =
true` -- A_ORTHOGRAPHIC 0.0150 (margin +0.2651 [+0.1125,+0.4171]), HARDENED_FREQUENCY_FREQ_MIN
0.0797 (+0.2004 [+0.0555,+0.3396]), OWN_SCRAMBLE_PERM_P95 0.0961 (+0.1839 [+0.0702,+0.2917]);
permutation p = 0.0005 on every seed. AND it survives the sum: **3.5264 of the 7.000-bit ceiling**
retained after bundling, against a pre-registered 0.5-bit criterion. The sparsity sweep's knee is
**f=0.02** (5.05 bits, still clearing all three floors), not the landed f=0.05.

**Three things that must travel with it.** (1) The CELL as a whole reads `FAILS_BAR` and its own
verdict is `BUNDLING_SURVIVED_BUT_NO_MEANING_GAIN`; the base rate stays 0 of 7,769. (2) It is a
SimLex-rho encoding ruler, not the reading task -- and on the reading task the same operator
collapses (DO-NOT-REDO 39). (3) The two results are NOT in tension: they are one operator on two
sources that differ 39x in effective rank. **The unresolved half, stated by its own author:**
geometry preservation explains where the k-cap is SAFE (0.6455 of dense pair-cosine structure
preserved on the norms at f=0.05) but NOT where it HELPS -- it scores 0.2801 against the dense
incumbent's 0.2680, so the cap CHANGES the geometry favourably on that source, and nobody has
explained why.

---

## THE BANKED-EVIDENCE BASE RATE (2026-08-16) -- stubbed as "VERDICT BAR"

`tools/verdict_bar_check.py` (`c0802fc36`), enumerated by `os.walk` over the absolute data dir --
every directory visited, every `metrics.json` opened, no glob, no name filter, no registry input.
**7,769 metrics.json found and scanned; 0 MEET the bar; 7,762 FAIL; 7 NO_EVIDENCE.** Disagreement
classes: NO_FLOOR 2,966 (a PASS-shaped string with at least one of orthographic/frequency/scramble
absent, so max(...) cannot be formed at all), SATURATED_CEILING 264 (headline numbers pinned at
1.000 across every arm), NO_CI 4, **STRING_PASSES_BAR_FAILS 1** (a PASS-shaped string whose margin is
not CI-separated from a floor the cell ITSELF recorded), AGREES 4,318, NO_VERDICT 216.
Reconciliation, filesystem first: 2,031 cert-ledger rows citing 592 cells and 200 registry rows
citing 52; 633 cited cells are on disk, 9 cited cells are NOT on disk, **7,127 cells on disk are
cited by no index**, and **238 flagged cells ARE cited by an index** -- i.e. their overstatement has
already propagated into the ledger or the registry. **That 238-cell list is an OPEN OPERATOR
DECISION and has NOT been taken.** The tool changed nothing
(`test_scan_never_mutates_anything`). Read `AGREES` as "the string does not lie", NEVER as "the cell
is good" -- most AGREES cells claim nothing at all. And see C31: this scan predates the false-pass
fix.

---

## THE SKIPPED-FULLS RECOVERY (2026-08-16) -- stubbed as "SKIPPED FULLS"

Checkpoint-collision fix `ee7c42c0f` (config-fingerprinted keys, so a smoke can never be reloaded by
a full). ~128 runs are collision-affected; the 30 MEDIUM+LOW ones were audited. **Forensic proof
they are smokes wearing a full's name: 23 of 29 comparable banked "full" metrics are BIT-IDENTICAL
to a freshly-run smoke after stripping volatile fields; 29 of 29 match on verdict string;** several
self-label (`KF45_SMOKE_PASS`, `KF5_PHASE_SMOKE_ONLY`, `KF4_V4_SMOKE_FAIL`, and `seeds=1 N=512`
written inside a directory named `_n16384`). An independent scale test confirms all 30 (elapsed
< 1.5 s, actual N on disk below the declared N, smoke flag present). Outcome so far: 7 re-run, 1
recovered from a sibling that was already a clean full (so recoveries are 9, not 8), 1 local
timeout, 2 killed mid-run, 19 ready. **1 DEMOTION:** `exp_kf45_pre_argmax_joint_probe_v1_n4096`
banked PASS -> `KF45_JOINT_MIDDLE_BAND` on a real N=4096 / 3-seed run (1 of 3 sub-gates passes).
2 upgrades (`exp_alpha1_cleanup_sweep_n4096`, `exp_bid_m_normalized_v5_n8192`). **0 of the 30 meet
the standing bar, in EITHER direction** -- 23 gate on a bare threshold, 6 have a floor but no CI, 1
has CI but no floor, and NONE has both, so none CAN produce a CI-separated margin even in principle.
The most dangerous shape found kept its label and lost its claim:
`exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384` reads `4WC_HARD_PASS` before AND
after, but its ratios go 1.000/1.000/1.000/1.000 (seeds=1, N=512, 0.09 s) ->
0.951/0.966/0.942/0.980 (seeds=5, N=16384, 1015 s). **Blocked, and it is an operator decision:** 4
cells cannot be dispatched because their prereg is absent and `preregs/` is do-not-touch; and 98
ARCHIVE-tier cells are untouched under a standing DO-NOT-RE-RUN default.

---

# 2026-08-17 ADDITIONS -- THE UNDERPOWERED-NULL NIGHT

Stubbed in `notes/STATUS.md` as DO-NOT-REDO 43, CORRECTIONS C32-C34, STANDING DISCIPLINE 14.
Every number below was recomputed off disk on 2026-08-17 by the pass that wrote
`notes/plan_status_compaction_report_2026-08-17.md`, which carries the full verification table and
names the two handoff figures it could NOT reproduce.

## THE ERROR PATTERN THAT PRODUCED C32-C34 -- read this before believing any negative here

**An UNDERPOWERED NULL was read as a CAPABILITY STATEMENT three times in one session.** The three
are unrelated in subject and identical in shape: a margin was compared with a floor without anyone
asking whether the sample could separate ANY effect at that n, or whether the floor was itself a
width rather than a level.

**The rule that closes it (STANDING DISCIPLINE 14): report the CI HALF-WIDTH and the NULL p95 at
that n BESIDE every margin. A WIDTH IS NOT AN EFFECT.** A scramble/permutation p95 of 0.18 at n=86
is not a strong competitor -- it is the null distribution's own spread, and any arm whose CI is
wider than the gap it must clear cannot separate regardless of how good the underlying thing is.

### C32 -- "0 of 7,769 banked cells meet the bar" is RETRACTED

- **SUPERSEDED CLAIM, preserved verbatim:** *"7,769 banked cells scanned (`verdict_bar_check.py`,
  `c0802fc36`): 0 MEET the bar"* (`notes/STATUS.md`, 2026-08-16 revision, POSITION and TOOLING
  STATE). Also retired on the way: the intermediate **"2 of 7,772"**.
- **SUPERSEDED BY:** `data/verdict_bar_reports/verdict-bar-20260817T002627Z.json` -- 7,789
  metrics.json enumerated by `os.walk` over an absolute data dir; **MEETS_BAR 1**, FAILS_BAR 7,770,
  NO_EVIDENCE 18. The one pass is `exp_cue_to_store_translation_v1`.
- **AND THE SURVIVOR IS ITSELF REJECTED**, on grounds recorded in `notes/PLAN_NEXT_24H.md`: its
  matched pool admits a fitted constant at 0.7354 against chance 0.0625; it is the EXACT-KEY regime,
  not the operating point (the same cell reads -0.0295 / -0.0776 / -0.0931 / -0.0809 elsewhere); the
  cell declines a cell-level verdict (`verdict = "COMPUTED"`); and its margin was overstated 4.20x
  once its own declared orthographic floor stopped classifying as a non-floor.
- **WHY IT WAS WRONG BOTH WAYS:** stale twice over. The count was taken before the constant-floor
  role was wired in AND before claim-arm selection was made allowlist-based. **"0 of N" was never a
  statement about the corpus; it was a statement about the checker.**

### C33 -- "our instrument cannot resolve verbs even when handed the right answer" is SUSPENDED, probably FALSE

- **SUPERSEDED CLAIM:** that the 12-dim target space cannot order verb pairs even for a known-answer
  arm, used to motivate building a new channel.
- **THE MEASUREMENT IT RESTED ON, verified on disk**
  (`data/exp_thematic_relation_supply_bridged_grounding_v2/metrics.json`,
  `HILLS_2009_NOUN_VERB_FALSIFIER.known_answer_K1.V`): n=**86**, rho 0.2576 [0.0401,0.4524], floor
  (scramble p95) **0.1776**, margin **+0.0801 NOT_SEPARATED**.
- **WHY IT PROVES NOTHING:** at n=86 the margin's own CI spans roughly +/-0.30, and the floor it had
  to clear, 0.1776-0.1814, is **1.645/sqrt(85) = 0.1784** -- i.e. THE FLOOR IS THE NULL
  DISTRIBUTION'S WIDTH AT THAT n. No arm of any quality separates there. The verb stratum was
  power-starved by construction, and the cell says so itself
  (`pos_stratified_note`, `G0_power_gate`).
- **THE TEST THAT SETTLES IT, and it needs no new asset:** `data/encoder_eval_benchmarks/simlex999.txt`
  holds **222 verb pairs** (counted: N 666, V 222, A 111). The bridged stratum used 86 because
  bridging requires one endpoint held out; **K1_OWN_NORMS needs no bridge and can run on all 222.**
  Floors must be recomputed on that population -- it is NOT the bridged stratum.

### C34 -- "the constant/prototype floor is the binding one" is FALSE AS A GENERAL CLAIM

- **SUPERSEDED CLAIM:** that the constant/prototype floor, having been the strongest member on the
  open read-out pool (0.1382 / 0.1390), is the binding floor generally.
- **SUPERSEDED BY two populations where it is the WEAKEST member:**
  - bridging stratum n=394: **-0.1959** (optimistic tie; midrank -0.1977, pessimistic -0.1996; tie
    mass 0.287) -- *AGENT MEASUREMENT*, `.claude/scan-out/collect-completed-runs.json`, computed by
    that agent's own script `.claude/scan-out/constfloor/const_floor_bridging.py`, which reproduced
    the n=394 / 412-bridged stratum exactly.
  - selectional-bridge stratum n=308: **-0.2253** -- READ ON DISK,
    `data/exp_selectional_constraint_bridge_v1/metrics.json`, `floors.F_CONSTANT_PROTOTYPE`. That is
    an independent instance, on a different stratum, of the same reversal.
- **THE MECHANISM, and it is obvious in hindsight:** on a hit@1 instrument a constant ranking still
  wins whenever the gold is a popular item, so it is strong; on a PAIR-CORRELATION instrument giving
  every bridged word the SAME code makes the pair ordering ANTI-correlated with the gold, so it is
  weak. **The floor's strength is a property of the SCORER, not of the floor.**
- **STANDING CONSEQUENCE:** compute all four floors on the item's own population every time.
  **Never import 0.1382, 0.2070 or -0.1959.**

## DO NOT REDO 43 -- SELECTIONAL-CONSTRAINT BRIDGING. A SECOND MEASURED NULL, AND IT IS WORSE THAN THE FIRST

`data/exp_selectional_constraint_bridge_v1/metrics.json`, **run_mode `full`, elapsed 5330 s**,
verdict `SELECTIONAL_CONSTRAINT_BRIDGE_DOES_NOT_CLEAR_THE_FLOOR`, mtime 2026-08-17T00:32.
**Caveat carried deliberately: no `.pid` file on disk names the process the operator described as
live, and none was modified on 08-17; the file read is a COMPLETE full with a verdict. If a live
process later rewrites it, re-check the mtime before quoting any of this.**

The cell implements the owner's own answer to "how does a new word get its meaning" -- bridge by the
**selectional restrictions of the verbs the word is an argument of** ("ran implies legs implies
animal"), rather than by copying a co-occurring neighbour's code, which is what we had built.

**On the common stratum (n=308; N 259 / V 27 / A 22; Spearman CI half-width 0.1122):**
- **It is CI-separated BELOW the neighbour-copy incumbent it was meant to beat:** head-to-head
  paired margin **-0.1049 [-0.2041,-0.0057] BELOW**. Three of four selectional variants are BELOW
  (S2 -0.1176, S3 -0.1422); the fourth (S4, subject-slot only) is -0.0195 NOT_SEPARATED.
- **It is indistinguishable from a random target:** S1 vs `N2_NULL_RANDOM_TARGET`
  **-0.0015 [-0.1391,+0.1361] NOT_SEPARATED**. It does beat the slot-rewire null (+0.1139 ABOVE),
  which says the slots carry SOMETHING, and the random-target comparison says that something does
  not identify the word.
- **The instrument was alive:** K1_OWN_NORMS on the same stratum reads **rho 0.3311**.
- **Meaning retention is negative:** -0.1224 against the incumbent's 0.0819.
- **The mechanism was genuinely different, not a re-run of the incumbent:** source-set Jaccard
  overlap with the incumbent's bridge sources is 0.0133 mean, and 38.6% of words share no source at
  all; `G3_passed` true; supply is real (8.6 slots and 145 fillers per word on average).
- **Evidence gap, stated rather than papered over:** this cell records THREE floor roles
  (orthographic 0.0503, hardened frequency ~0.0000, constant/prototype -0.2253) and no scramble
  floor; the two seeded null arms carry that role instead. Its bar decision is therefore not
  four-role complete.
- **REVIVAL CRITERION (brain-framed, never performance-framed):** the owner's account has THREE
  stages -- selectional constraint, then EPISODIC recall of instances ("rabbits and deer which I
  have SEEN cross roads"), then a DISTRIBUTION over categories. **We built stage one only, and
  scored it with a single point estimate.** Revive when the episodic-recall stage exists and the
  read-out is a distribution rather than a mean, i.e. when the thing being tested is the mechanism
  the owner described rather than its first third.

## THE PARTIAL-CUE STRUCTURAL CAP -- stubbed as the TOP ITEM

`data/exp_foundation_neighbourhood_purity_v1/metrics.json`, grid `full`, 47 foundations, population
n=2358, ruler-mode gate PASS, **KA 0.9807-1.0000 on 47 of 47**.

| | exact key | partial cue |
|---|---|---|
| purity predicts retrieval at | rho **0.961** (n=45) | rho **-0.0167** (n=40) |
| range across the 47 foundations | 0.0129-0.8787, a **68.1x** span | 0.0064-0.0365 |
| circular WordNet ORACLE, allowed to cheat | **0.8787** | **0.0365** |

**The oracle's 0.0365 is the single best partial-cue reading anywhere in the grid.** A foundation
built by consulting the answer key cannot beat 3.7% under the operating cue. That is not a supply
problem, not a purity problem and not a mechanism problem -- **something structural makes the
partial cue uninformative**, and every downstream build is aimed at the wrong object until it is
diagnosed. The only thing that moves it at all is a two-stage cue, from 0.0225 to **0.0322** at
best, which is a rounding error against the exact key.

**Two measured facts that constrain the diagnosis:** the partial cue's cosine to its OWN stored row
is **0.1621** (`exp_cue_to_store_translation_v1`), and addressing is **1.0000 exact / 0.0325
partial** in the same pipeline. A sparsifier keeping the top few per cent of an expansion turns a
0.16 alignment into a near-random active set, so the address stage never gets close enough for the
key to matter.

## THE WRITE/READ ASYMMETRY -- the one live positive, stated in its recomputed form

`data/exp_sparse_address_dense_value_v1/metrics.json`, n=3994 addressable items, partial-cue regime.
The cell computes every rung itself and explicitly refuses to import
`exp_cue_to_store_translation_v1`'s 0.0325 as a comparator, because that is a different population.

- **Best partial-cue addressing anywhere in the grid: 0.0719 [0.0638,0.0796], at a DENSE address**
  (D=2048, `a_write`=1.0). **Sparsifying the address never beats dense outright.**
- **But at 1% occupancy it MATCHES dense, if you expand first and read with a dense cue:**
  D=8192, `a_write`=0.01 (82 active units of 8192), `a_read`=1.0 -> **0.0699 [0.0621,0.0779]**,
  CIs heavily overlapping with the dense best. **A 100x sparser address for no measured loss.**
- **The asymmetry itself:** the same config read SYMMETRICALLY (sparse cue against sparse key) reads
  0.0483 [0.0418,0.0548] -- **1.45x worse**. Across all matched pairs (same regime, D, `a_write`,
  code type, projection seed; sparse writes only) **the dense read wins 18 of 24, ties 5, loses 1
  (0.99x), and the largest gain is 6.27x** (D=2048, `a_write`=0.002).
- **This is the owner's per-process regime ruling showing up as a measured effect**, and it is the
  one place where three independent lines agree: the computational-theory drill (sparsify the
  ADDRESS, keep the VALUE dense), the owner's answer (set the regime per organ, not globally), and
  this grid.
- **The honest ceiling beside it:** every rung of this grid sits at or below ~0.072 addressing under
  a partial cue. The asymmetry is real and the LEVEL is still the structural cap above.

## THE CLEANUP MEMORY -- it works, and it makes five banked nulls STRONGER

`hdlab/vsa_cleanup_memory.py`, scored in `data/exp_cleanup_memory_capability_v1/metrics.json`.

- **The organ is not inert and this was the standing doubt:** stored symbols are fixed points at
  **1.0000**, the map is idempotent, recovery is monotone in cue quality (0.9987 at tau=0.45 against
  chance 0.00018), and the theory capacity scale `d/log d` is reported (46.17 at d=256, M=5491).
  Known-answer and null arms break independently.
- **It produces the first cleanup lift this programme has measured**, over no-cleanup, partial cue:
  **+0.0033 [+0.0013,+0.0055] ABOVE** on the open pool and **+0.0078 [+0.0008,+0.0150] ABOVE** on
  the K49 balanced pool; the K15 pool is +0.0046 NOT_SEPARATED. **CI-separated in 2 of 3 pools.**
- **And every arm remains far below the binding floor:** on the open pool the binding floor is the
  CONSTANT/PROTOTYPE at 0.1390 and the best cleanup arm sits at **-0.1135 [-0.1249,-0.1019] BELOW**.
- **Why this matters more than the lift:** it removes the "the load-bearing half of VSA was missing"
  defence. The five banked cleanup nulls were not measuring a broken organ. **They are stronger
  negatives now, not weaker ones.**

## SURPRISE-WEIGHTED UPDATE -- a clean null with a named cause

`data/exp_surprise_weighted_update_v1/metrics.json`.

- **The surprise signal is DEGENERATE:** sampled surprise has median **0.875** and mean 0.853 where
  1.0 is exact orthogonality (p10 0.6525, p90 1.0128). There is no informative tail to select from.
- **Selection therefore does not beat reading the same number of tokens at random:** across 6
  conditions x 3 selection rates, `T2_TOPSURPRISE` beats its token-matched `C1_RANDOM_SUBSET` in
  only **4 of 18** point comparisons and never by more than +0.0035. **Reading fewer occurrences is
  a different corpus, not a better rule, and the matched control is what says so.**
- **The residual rule is a near-no-op and the cell pre-registered why:** `mean_cos_to_A0_rows` is
  **0.9771** at every eta, i.e. the prediction comes from the store being criticised, so early in
  training the residual IS the observation. **That is the BOOTSTRAPPING PROBLEM, not a refutation of
  surprise weighting.** The stronger brain-faithful version is a SEPARATE predictor or a warm start.

## CORRECTIONS TO PRIOR CLAIMS -- added 2026-08-17 (auditor, docs-reconciliation pass)

### C33 UPDATE -- "our instrument cannot resolve verbs even when handed the answer": SUSPENDED -> MEASURED

C33 was filed as SUSPENDED because at n=86 the floor it had to clear WAS the null distribution's own
width, so no arm of any quality could separate. **ITEM 2 has now measured it at n=222 and the entry
closes in the MEASURED direction -- not confirmed, not withdrawn.**

- **THE MEASUREMENT, recomputed off `data/exp_verb_target_space_n222_v1/metrics.json` (run_mode
  `full`, N_PERM 2000, N_BOOT 10000, elapsed 652.8 s), commit `0652e20a5`:**
  - Verbs n=222, `K1_OWN_NORMS` rho **0.2607** [0.1282, 0.3841], bootstrap half-width **0.128**.
  - Floors recomputed on these 222 pairs and on no other population: orthographic **0.0183**,
    frequency-hardened **0.0341**, constant/prototype **0.0536**, **scramble p95 0.1152**
    (strongest, and therefore the binding one).
  - Margin over the strongest floor **+0.1452 [-0.0496, +0.3379], NOT_SEPARATED**. It clears the
    other three CI-separated (+0.2424 / +0.2266 / +0.2070).
  - Row-permutation **p = 0.001** over 2,000 draws (null mean 0.0014, sd 0.0666).
- **WHY THIS IS NOT THE n=86 ARTIFACT REPEATING, which is the entire point of re-running it:** the
  plan predicted the null width would fall to 1.645/sqrt(221) = **0.1107**, and the measured scramble
  p95 came in at **0.1152**, a ratio of 1.04. **The null genuinely tightened with n.** At n=86 the
  floor was 0.1776 against a predicted 0.1784 -- the same ratio, but at a width so wide that nothing
  could separate under it. The instrument is now as powered as this benchmark can make it, and the
  negative is a property of the 12-dim space rather than of the sample.
- **TWO STATISTICS THAT DISAGREE, BOTH REPORTED:** the permutation test says the verb correlation is
  real; the paired bootstrap on the MARGIN says its interval still crosses zero. The declared bar is
  the bootstrap, so the arm does not clear. Reporting only the first would be picking the flattering
  construct.
- **CONSEQUENCE:** a verb-channel build is licensed by the plan's own stop-if (ii) wording, after the
  brain-framed question ("which experiential block is missing?"). **It must cite this n=222
  measurement. The n=86 number is RETIRED and may not be quoted again.**
- Contrast strata, own floors, never crossed: nouns n=666 **+0.2065 [+0.1015, +0.3102] ABOVE**;
  adjectives n=111 **-0.0074 [-0.2666, +0.2479] NOT_SEPARATED**, permutation p 0.060.

### C35 -- "THE BINDING-OPERATOR CHOICE IS EMPIRICALLY NULL AT FULL MODE ACROSS TWO CELLS AND SIX OPERATORS" IS PART-WRONG, IN THREE PLACES

**This is a correction to the Director's own compaction handoff and it is not softened.**

- **SUPERSEDED CLAIM, PRESERVED VERBATIM** (`notes/COMPACTION_HANDOFF_2026-08-17.md` section 8b(D),
  commit `0d147399b`):
  > **The binding-operator choice is EMPIRICALLY NULL at full mode** across two cells and six
  > operators (`K_cliff` 750/750/750 for Hadamard/HRR/FHRR with 0.0 shift; `K*` 500/500/500 for
  > cyclic-shift / permutation / phase-rotation with **0.000 separation**).
- **HOW IT WAS CHECKED:** every one of the eleven relevant `metrics.json` files was opened with
  `.venv` python and its phase map read point by point. No verdict string was trusted; the verdict
  strings are in fact where the error lives.

**(a) The `750/750/750` half reproduces exactly -- on a THREE-BIN INSTRUMENT.**
`data/exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}`, all `run_mode: full`, all
`HARD_FAIL_BINDING_OP_CAPACITY_INVARIANT`, `K_cliff` 750 with shift 0.0 for Hadamard,
circular-convolution HRR and FHRR. **But `M_per_bank` was swept over only [150, 750, 1350].** All
three operators landing on 750 means all three landed in the same middle bucket of a three-bucket
instrument. **An instrument with three bins cannot report a difference smaller than a bin. That is
a resolution limit, not a measured equality.**

**(b) And the same files' own per-point data contradict the word "invariant".** Top-1 at the middle
grid point, by seed:

| operator | seed 7 | seed 13 | seed 19 | mean |
|---|---|---|---|---|
| FHRR complex multiply | 0.8667 | 0.7333 | 0.8000 | **0.8000** |
| circular convolution (HRR) | 0.3667 | 0.2000 | 0.3333 | 0.3000 |
| Hadamard | 0.2667 | 0.2667 | 0.3333 | **0.2889** |

At the top grid point (1350) it is FHRR 0.4444 against Hadamard 0.1000. **FHRR is 2.77x Hadamard at
the identical point, on all three seeds, inside the very bin that produced the word "invariant".**
The cell reports no interval of any kind; an approximate two-proportion check by this pass (three
seeds x 30 queries pooled as n=90, normal approximation, queries treated as independent -- an
optimistic assumption, since queries within a seed share one bundle) puts the middle-point gap at
**+0.5111, approximate 95% half-width 0.1249, CI [+0.3862, +0.6360]**. **The "null" is the `K_cliff`
summary quantising a large per-point difference into one bucket.**

**(c) The `K* 500/500/500 with 0.000 separation` half DOES reproduce -- in a cell that neither the
handoff nor the phase-diagram note opened -- and is SUPERSEDED rather than absent.**
`data/exp_substrate_order_binding_family_v1_seed_{13,19}`, `run_mode: full`, verdict
`HARD_FAIL_ORDER_BINDING_INVARIANT`, `K_star_per_op` = 500 for cyclic-shift, random-permutation and
phase-rotation, `max_sep=0.000`. Again a **three-value grid, K in [50, 500, 2000]**, 50 queries per
point, and **only 2 of 3 seeds landed** -- seed 7's `metrics.json` carries no phase map and records
`RUNNING` at 0.15 s elapsed. The later cell of the same family,
`exp_substrate_order_binding_family_v2_seed_{7,13,19}` (also full, a discriminator-targeted load
sweep at 60 queries per point), returns `MIDDLE_BAND_PARTIAL` with **the winner changing by seed**:
cyclic-shift / random-permutation / phase-rotation = 0.2667 / 0.1833 / 0.2167 (seed 7), 0.2333 /
0.2000 / 0.2333 (13), 0.2167 / 0.2500 / 0.2000 (19).

**THIS ALSO CORRECTS THE CORRECTION.**
`notes/substrate_phase_diagram_recovered_from_experimental_history_2026-08-17.md` states that this
half *"does not reproduce"* and *"is not what is on disk"*. **That is too strong: it reproduces in
the v1 cell and is superseded by the v2 cell.** The note enumerated the v2 family and not the v1
family. This is standing discipline 7 -- no demotion without a fresh on-disk re-check -- firing on
a CORRECTION rather than on a result, which is the reason discipline 7 exists.

**(d) The summary omitted that two of the six operators COLLAPSE.** In
`data/exp_substrate_seqbind_binding_op_family_v2_seed_7` (`run_mode: full`), per-operator mean top-1
over its five sequence-length points: Hadamard **0.8160**, circular-convolution HRR **0.8360**,
tensor product **0.7720**, XOR-on-binary **0.0720**, sum-modulo-N **0.0000**. That cell's own
separation metric is `max_log2_sep = 3.322`, which is log2(500/50) -- **a tenfold gap, not 0.000** --
and its `K_cliff` is 500 for the three algebraic operators against **50** for the other two.
"Six operators, null" hides about as separated a result as this project owns. The handoff also named
the wrong three operators for this cell: it is Hadamard / HRR / tensor product, not cyclic-shift /
permutation / phase-rotation.

**THE STANDING FACT THAT MATTERS MORE THAN ANY OF THE ABOVE: the binding operator -- our core
operation, the multiply that binds a role to a filler -- has never been varied on ANY operation this
programme currently runs on.** All four binding-operator cell families score top-1 retrieval from a
bundle on a SYNTHETIC corpus (every `corpus_provenance` string begins `synthetic_substrate_`), at
**30 / 50 / 50 / 60 queries per point** respectively -- *the "50 queries per point" figure in
circulation is right for two of the four and does not reproduce as a blanket statement* -- and **not
one of the eleven files contains a confidence interval, a bootstrap, or a permutation test.** Zero
binding cells score on the comparator, zero on addressing, zero on open-vocabulary read-out.

**THE CORRECT STATEMENT, and it should replace the old one wherever it appears:** among the three
standard algebraic operators the difference is smaller than any instrument we have built could see,
and at the one grid point where the others are not saturated FHRR is visibly better; two
non-algebraic operators are decisively worse. **"We tested it and it does not matter" and "we have
never been able to tell" are different claims, and only the second is supported. Here, "unfalsified"
means "never tested", not "confirmed".**

## STANDING DISCIPLINES -- entry added 2026-08-17 (auditor)

**15. A GRID'S RESOLUTION IS PART OF ITS VERDICT. An equality reported on a three-value grid is a
BIN, not a measurement.** C35 is the incident: two separate cells reported "all operators identical"
because a three-point sweep put every operator in the same bucket, and one of those cells' own
per-point data showed a 2.77x difference inside that bucket. This is the same family of error as
discipline 14 (a width is not an effect) one level up: there, the SAMPLE could not resolve the
effect; here, the GRID cannot. **State the swept values and the number of queries per point beside
every claim of "no difference", and read the per-point table before quoting a summary field.**

## THE PHASE DIAGRAM -- THERE ISN'T ONE (2026-08-17) -- stubbed in `STATUS.md` as "PHASE DIAGRAM"

`notes/substrate_phase_diagram_recovered_from_experimental_history_2026-08-17.md`, commit
`32cc8ce71`. Enumerated from the filesystem, never from a registry, index or KB query.

- **8,661 directories walked, 7,804 `metrics.json` found.** Re-walked by the auditor on the same day:
  **8,662 and 7,807**, the difference being exactly the three files this session added
  (`exp_cue_information_audit_v1`, its smoke, `exp_verb_target_space_n222_v1`). **Nothing in the
  original enumeration is missing** -- the two sets were diffed by path, not by count.
  *(Re-run a few minutes later while promoting the script: **8,663 and 7,808**, the fourth new file
  being `exp_sparse_address_regime_switch_uncompressed_v1_smoke` -- the ITEM 3 agent's first smoke,
  landing live. The count moves; quote it with a timestamp or re-run the script.)*
  **Provenance, promoted out of `scratch/` so this note does not cite a wiped directory:**
  `tools/phase_diagram_recovery/verify_metrics_enumeration.py`, which prints both set differences
  rather than only the counts.
- Of those files, about **59 vary dimensionality**, about **21 vary sparsity**, **2 cells vary the
  expansion factor**. The same axis is stored under at least 12 different key names for
  dimensionality and 14 for sparsity, which is why every keyword-first audit of this corpus has
  failed.
- The note's own classification: **23 of 42 parameter-by-operation squares NEVER MEASURED**, 13
  usable, and **six separate diagrams on six scorers that may not be merged** under this project's
  own no-crossing rule. (That tally is a judgement classification, not a recomputable count; the
  file counts above are recomputable and were recomputed.)
- **THE RECOLLECTION HAS A TRACEABLE SOURCE AND IT DOES NOT SUPPORT ITSELF.** "We have a phase
  diagram, 55-65% covered" most likely traces to
  `notes/director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md`, whose headline reads *"~55-60% ->
  60-65%"* while **its own line items say dimensionality "Outer ~10%" and sparsity "<5%"** -- the two
  axes the recollection is used to settle.
- **A CITATION INTO A DIRECTORY THAT GETS WIPED.** The sparsity sweep the owner's Q13 note leans on
  has **no cell under `data/` and no `metrics.json`**; it lives in `scratch/sparsify_right_object/`,
  excluded by `.gitignore` line 83 and periodically cleared by `tools/clear_scratch.py`. Per the
  repo's own rule, promote it to `experiments/` before the next clear.
- **THE ONE CASH-IN:** the same knob has OPPOSITE optima on two different jobs, which proves the
  owner's per-process claim as measurement rather than assertion -- and makes `d=256 -> 1024`
  justified for the comparison job and NOT for the addressing job.

## THE CUE INFORMATION AUDIT (2026-08-17) -- stubbed in `STATUS.md` as "CUE INFORMATION AUDIT"

`data/exp_cue_information_audit_v1/metrics.json`, commit `eec21487d`, findings note
`notes/cue_information_audit_v1_findings_2026-08-17.md`. All figures below re-derived from the
metrics file by the auditor.

- **THE ANSWER: the information IS in the cue, and our own compression is discarding part of it.**
  On one identical store / cue / pool / gold (n=3,994; 5,491 candidate addresses; chance 0.000182),
  addressing accuracy is **0.0849** for raw uncompressed count vectors against **0.0711** for the
  live 256-dim projection: **+0.0138 [+0.0083, +0.0195], half-width 0.0056, CI-SEPARATED**. Exact
  key **1.0000** on both regimes; random key **0.0003**. The cell's stop-if (iii) fired.
- **DEFLATION THAT MUST TRAVEL WITH IT:** 0.0849 is about eight percent. The read-out ceiling is
  untouched -- both regimes are CI-separated BELOW their own binding floors at hit@1 (C0 -0.1167
  [-0.1284,-0.1054] against the constant/prototype floor 0.1390; U0 -0.0631 [-0.0727,-0.0536]
  against the trigram floor 0.0871).
- **THE PRECONDITION IS NO LONGER AN UNADOPTED AGENT MEASUREMENT.** Exact recoverability of the
  held-out sentence reproduced on **all 3,994 eligible items** (`max_abs_error 0.0`,
  `ALL_EXACT True`), not the 400-item sample the earlier fragment used, and the run added a
  store-side encoder identity `H^T P_a == mat[a]` that is **bit-exact on all 5,491 anchors** and that
  the fragment never ran.
- **THE CUE-KIND SPLIT IS THE PART THAT SHOULD CHANGE A BUILD.** The owner's Q4 introspection named
  TWO parts to a half-remembered word and we serve one: same-meaning words **+0.0113 [+0.0080,
  +0.0148] ABOVE**, starting sound **0.0 [-0.0013, +0.0013] NOT_SEPARATED** with both onset arms at
  0.0008 against a random key at 0.0003-0.0005. **The cause is structural: our only onset channel is
  the word's first four characters hashed as one whole symbol (`ONSET_LEN = 4`), which cannot
  resemble anything unless a stored word IS that four-character string.** *(The findings note
  describes it as a "single-character-prefix" cue; that is wrong -- the source uses four. Corrected
  here off `experiments/exp_cue_information_audit_v1.py` lines 61 and 146.)*
- **A CAUTION THAT PREDATES THIS CELL AND SURVIVES IT:** an earlier agent fragment measured that
  narrowing the candidate set by word onset lifts self-recovery 0.0711 -> 0.5734, **but a
  size-matched random set does it marginally better** -- so that lift was the SET SIZE, not the
  sound. Any onset-channel build must carry a size-matched control from the start. *(AGENT
  MEASUREMENT, attributed, never adopted.)*

---

## THE CUE SIDE, CLOSED IN FOUR CELLS (2026-08-17, second docs-reconciliation pass) -- stubbed in `STATUS.md` as "CUE SIDE CLOSED"

Written by an audit/docs-only pass. **Every number below was re-derived from the named
`metrics.json` with `.venv` python by that pass**; none was taken from a verdict string, a findings
note or another actor's summary. That pass authored no experiment, ran none, dispatched nobody, and
opened neither `experiments/` nor `hdlab/` for writing.

**PLAIN LANGUAGE FIRST.** The store is a filing cabinet. All four cells below change the QUESTION we
hand it -- how the cue is written down, how the address is written down, how much of either we keep.
Three of the four moved the *filing* step and none of them moved the *reading* step. One other cell
(the write rule, in the section after this) changed what is IN the cabinet instead, and that one
moved reading for the first time. That contrast is the finding.

### (A) SPARSE ADDRESS / REGIME SWITCH, ON THE UNCOMPRESSED BASE -- A CLEAN NULL
`data/exp_sparse_address_regime_switch_uncompressed_v1/metrics.json`, commit `2e5a467ae`, findings
`notes/sparse_address_regime_switch_uncompressed_v1_findings_2026-08-17.md`. This is PLAN ITEM 3,
and it is DONE.

Primary measure, addressing accuracy, partial cue, n=3,994 items over 5,491 anchors,
chance 1/5,491 = 0.000182. All values RECOMPUTED off the metrics file:

| arm | K_WRITE / K_READ | addressing |
|---|---|---|
| `A0_FLAT` (incumbent, nothing truncated) | ALL / ALL | **0.0849** |
| `T1_SPARSE_KEY_DENSE_VALUE` | 32 / ALL | 0.0704 |
| `T2_REGIME_SWITCH` | ALL / 8 | **0.0886** -- the grid's raw maximum |
| `C1_SPARSE_BOTH` | 32 / 32 | 0.0704 |
| `K1_ORACLE_ADDRESS` | -- | **1.0000** (gate 0.999, PASS) |
| `N1_RANDOM_ADDRESS` | -- | **0.0000** against chance 0.000182 |

- `A0_FLAT` reproduces ITEM 1's `U0_UNCOMPRESSED` target **exactly**: `REGRESSION_GATE_U0_TARGET`
  measured 0.0849, expected 0.0849, tol 0.006, **PASS**. The population gate also reproduces the
  landed C0 read-out number (0.0223 vs 0.0223, tol 5e-4, n=3,994, PASS), so this cell is scoring the
  identical population.
- **`T1` vs `A0_FLAT`: -0.0145 [-0.0203, -0.0088], CI half-width 0.0057, BELOW.** Sparsifying the
  stored KEY costs real accuracy.
- **`T2` vs `A0_FLAT`: +0.0037 [-0.0013, +0.0088], half-width 0.0051, NOT_SEPARATED.** The grid's
  raw maximum (0.0886 against 0.0849) looks like a win as a bare point estimate and **is not one**
  under the paired bootstrap. That is standing discipline 14 doing its job inside a cell.
- **`T2` vs `T1`: +0.0182 [+0.0118, +0.0248], half-width 0.0065, ABOVE.** Sparsifying the CUE is
  reliably better than sparsifying the KEY -- a direction, not a win.
- **`C1` vs `T1`: 0.0000 [0.0000, 0.0000], bit-identical.** **CONSTRUCTION CAVEAT, CARRY IT
  ALWAYS:** T1's chosen K_WRITE=32 sits ABOVE the cue's own median nnz of **12.0** words
  (`NNZ_PER_ROW.cue_median`), so truncating the cue at K=32 is a **no-op for at least half the
  items**. This tie is therefore **partly a construction artifact and is NOT evidence that the
  key/value distinction is inert.** The cleaner read of the same question is T1 vs T2, which move in
  OPPOSITE directions. The cell records this itself in `C1_CONSTRUCTION_CAVEAT`; anyone quoting the
  0.0 must quote the caveat with it.
- Secondary, hit@1 vs WordNet gold on the same population, tie-corrected: every arm is CI-separated
  BELOW the binding trigram floor 0.0871 (`A0_FLAT` 0.0240, margin -0.0631 [-0.0727, -0.0536]).
- **STOP-IF (i) FIRED:** `i_ADDRESS_NOT_ARCHITECTURE_IS_THE_LIMIT_for_T1`, with both validity arms
  passing independently.
- **THE VERDICT IN THE CELL'S OWN WORDS, quoted because it is the honest one:** *"Neither, cleanly.
  This item did not buy a second capability win beyond item 1's (T2 vs A0_FLAT is NOT_SEPARATED, not
  a beat) and it did not buy a clean efficiency win either (T1/C1, the genuinely sparsified-key arms,
  LOSE accuracy CI-separated rather than matching it at lower cost)."* **No arm beat the flat store,
  and the sparsified arms lost accuracy rather than matching it more cheaply.**

### (B) THE BASIN EXPLANATION IS REFUTED, AND THE RUN THAT REFUTES IT SAT UNREAD FOR 14 HOURS
`data/exp_cleanup_basin_conditional_v1/metrics.json`, landed **2026-08-16T22:41** and **read by
nobody until 2026-08-17**, first by the ITEM 3 cell author and independently here.

The theory being tested: the cleanup organ works (its own recovery axis reads 0.0000 / 0.0000 /
0.0013 / 0.0667 / 0.9493 / 1.0000 at tau = 0.05 / 0.10 / 0.15 / 0.20 / 0.30 / 0.45, so **its basin
cliff is between tau 0.20 and 0.30**), and the reason it never lifts read-out is that our cues land
OUTSIDE that basin. If that were true the lift would grow as tau rises and appear where the organ is
healthy. **It does the opposite.** Lift of `T1_CLEANUP_SETTLED_b64` over `A0_NO_CLEANUP`,
tie-corrected hit@1, six tau strata each with its own recomputed floors, RECOMPUTED here:

| stratum | n | mean tau | lift vs no-cleanup | band |
|---|---|---|---|---|
| tau [-1.00, 0.05) | 1112 | -0.0111 | **+0.0036 [+0.0009, +0.0072]** | **ABOVE** |
| tau [0.05, 0.10) | 616 | 0.0740 | +0.0016 [0.0000, +0.0049] | NOT_SEPARATED |
| tau [0.10, 0.20) | 911 | 0.1473 | +0.0022 [0.0000, +0.0055] | NOT_SEPARATED |
| tau [0.20, 0.30) | 589 | 0.2443 | -0.0000 [-0.0051, +0.0051] | NOT_SEPARATED |
| tau [0.30, 0.45) | 507 | 0.3630 | +0.0040 [-0.0059, +0.0138] | NOT_SEPARATED |
| tau [0.45, 1.01) | 259 | 0.5427 | +0.0154 [-0.0039, +0.0347] | NOT_SEPARATED |

The strata sum to 3,994. The known-answer arm `KA_QUERY_IS_GOLD_VECTOR` reads **1.0000 in every
stratum**, so the instrument is alive everywhere, and the cell's own `PREREGISTERED_READ.how_to_read`
says in advance what each pattern would mean: *"positive and CI-separated ONLY in the high-tau strata
CONFIRMS the basin explanation ... Flat everywhere, including where the organ's own recovery axis
reads 1.0000, REFUTES it and is the more interesting result."* **The one CI-separated lift is in the
LOWEST-tau stratum -- the farthest point from any basin -- and the highest stratum, where the organ
recovers perfectly on its own axis, is NOT_SEPARATED.** The basin explanation is refuted for this
organ on this population.

**WHAT IT LICENSED:** not building an elaborate settle mechanism. The one cheap settle check that was
armed anyway (`T1_SETTLED`, score-space centring, in cell (A)) landed exactly where this predicted:
**-0.0010 [-0.0025, +0.0003], NOT_SEPARATED**. A refutation that then predicts a later null correctly
is worth more than the settle machinery would have been.

**THE PROCESS LESSON, and it is the second instance in two days: AN UNREAD RUN IS A RUN THAT DID NOT
HAPPEN.** This file landed at 22:41 on 08-16, was flagged in `PLAN_NEXT_24H.md` section 3 as "NOT YET
READ by anyone", and stayed unread for about fourteen hours while a plan item that depended on it was
being designed. The 47-foundation grid did the same thing hours earlier and carried the session's
biggest finding. **Reading landed artifacts is not a chore that follows the work; on this evidence it
IS the work, and it is cheaper than every alternative.**

### (C) WHAT THE 256-DIM PROJECTION DESTROYS: PRESENCE BEATS COUNTS
`data/exp_cue_compression_property_diagnosis_v1/metrics.json`, commit `201776cc9`, findings
`notes/cue_compression_property_diagnosis_v1_findings_2026-08-17.md`. Same population, n=3,994 /
5,491, addressing accuracy, all RECOMPUTED:

| arm | value | vs incumbent `C0_PROJECTED_256` (0.0711) | vs `U0_UNCOMPRESSED` (0.0846 here) |
|---|---|---|---|
| **`B1_BINARIZED_RAW`** (presence/absence, no projection) | **0.1094** | **+0.0383 [+0.0293, +0.0476] ABOVE** | **+0.0248 [+0.0160, +0.0338] ABOVE** |
| `S1_SPARSE_HASH_PROJ` (keep exact zeros) | 0.0611 | -0.0100 [-0.0160, -0.0040] BELOW | -0.0235 BELOW |
| `N1_NONNEG_PROJ` (keep non-negativity) | 0.0709 | -0.0003 [-0.0068, +0.0060] NOT_SEPARATED | -0.0138 BELOW |

- Both regression gates PASS (C0 0.0711 exact; U0 0.0846 against the landed 0.0849, inside tol
  5e-4). Every arm carries `K1_EXACT_KEY` 1.0000 and a near-chance random key.
- Between-projection-draw SD over 3 draws: S1 0.0019, N1 0.0009 -- both well inside their own CI
  half-widths, so the BELOW / NOT_SEPARATED verdicts are not draw noise.
- **THE FINDING: it is not sparsity and not non-negativity. It is MAGNITUDE.** Counting how often a
  word occurred is actively harmful; recording only THAT it occurred beats both the compressed
  incumbent and the full uncompressed counts, recovering 284% of the original gap
  (`fraction_of_U0_minus_C0_gap_recovered` 2.837). **This is a design constraint for the next
  encoder, NOT a capability claim** -- the cell says so itself.
- **THE LOSS IS CONCENTRATED, NOT DIFFUSE.** Buckets: 245 items both regimes hit, 3,617 both miss,
  **93 lost by the projection**, 39 gained; net 54/3,994 = 0.0135, which reconciles with the
  aggregate margin. Those 93 items have **shorter cues** (10.80 vs 12.48 distinct words, margin
  -1.69 [-2.73, -0.65], CI-separated) and **much sparser store profiles** (106.4 vs 210.8 distinct
  words, margin -104.4 [-119.9, -88.4], CI-separated). Item-level word collision is NOT separated
  (0.0521 vs 0.0498, [-0.0004, +0.0059]).
- **A FLAG THE CELL RAISES AGAINST ITSELF, verified here:** its own boolean
  `ITEM_LEVEL_LOSS_IS_CONCENTRATED` reads **`false`** while two of three item features ARE
  CI-separated, because the boolean only recognises separations in the ABOVE direction and both real
  ones are BELOW. **The boolean under-reports; the per-feature margins are the source of truth.**
  Anyone reading that field alone would draw the opposite conclusion.

### (D) THE ADDRESSING GAIN DOES NOT REACH THE READING. THE TWO ARE SEPARATELY CAPPED.
`data/exp_cue_binarised_readout_transfer_v1/metrics.json`, commit `1e085d761`, findings
`notes/cue_binarised_readout_transfer_v1_findings_2026-08-17.md`. **This is the most important of the
four.** Same population, same scorer, same gold; nine regression sub-gates against cell (C) all PASS.

| arm | addressing | hit@1 (tie-corrected) |
|---|---|---|
| `R0_INCUMBENT` | 0.0711 | 0.0223 |
| **`R1_BINARISED`** | **0.1094**, +0.0383 [+0.0295, +0.0473] ABOVE R0 | **0.0249**, **+0.0026 [-0.0026, +0.0078] NOT_SEPARATED** |
| `R2_BINARISED_PROJECTED` | 0.0834, **-0.0260 [-0.0333, -0.0188] BELOW R1** | 0.0205, -0.0018 NOT_SEPARATED |

- **A 54% relative gain in finding the right drawer buys nothing measurable in reading what is
  inside it.** Addressing +0.0383 CI-separated; hit@1 +0.0026 with a CI that straddles zero.
- **The two defects are NOT independent:** binarising and then projecting (R2) gives back two thirds
  of the addressing gain (-0.0260 BELOW R1). You cannot fix one and keep the other.
- Four floors, all recomputed on THIS population, PARTIAL-cue regime for the scramble floor
  (crossing to the exact-key scramble would be a population-crossing error, and the cell says so):
  orthographic **0.0873**, frequency **0.0185**, scramble **0.0095**, constant/prototype **0.1390**
  -- **the constant/prototype floor binds.** R1 is **-0.1140 [-0.1257, -0.1024] BELOW** it, and
  -0.0624 [-0.0722, -0.0527] below orthographic. *(Precision, because a looser phrasing is in
  circulation: the arms are CI-separated below the TWO STRONGEST floors. They are not below the
  frequency floor 0.0185 or the scramble floor 0.0095 -- R1 at 0.0249 is numerically above both. The
  gate is max(four floors) = 0.1390, and that is what they fail.)*
- Standing-rule-12 check clean: Pearson r between per-item R1-minus-R0 gain and that item's own best
  orthographic score is **-0.0037 [-0.0328, +0.0246] NOT_SEPARATED** (n=3,994), and -0.037
  NOT_SEPARATED on the 119 items whose gain is non-zero. **The gain is not a spelling effect in
  costume.**
- `ORACLE_CONSTANT_not_a_floor` 0.1715 is reported and is not a floor.
- **STOP-IF (ii) FIRED: `ii_ADDRESSING_AND_READOUT_ARE_SEPARATELY_CAPPED`**, with
  `does_fixing_addressing_fix_readout: "NO"` recorded in the cell.

### THE STRATEGIC CONSEQUENCE OF (A)-(D), STATED PLAINLY
**Cue-side engineering is measured, understood and exhausted.** Four cells varied what we hand the
store -- compress it, do not compress it, keep only presence, sparsify the address, sparsify the cue,
switch the regime between writing and reading, settle the result against a cleanup organ. The best of
them moved ADDRESSING from 0.0711 to 0.1094 and moved READING by an amount indistinguishable from
zero. **Every remaining road runs through the WRITE RULE -- what gets stored in the first place --
and the section below is the first evidence that that road exists.**

---

## THE WRITE RULE MOVED READ-OUT, AND IT IS THE FIRST THING THAT EVER HAS (2026-08-17) -- stubbed in `STATUS.md` as "WRITE RULE"

`data/exp_readout_writerule_paradigmatic_v1/metrics.json`, commits `a8fdc968f` (cell) and
`24ca42661` (findings appended at `notes/readout_ceiling_findings_2026-08-17.md` section 10). All
figures RECOMPUTED off the metrics file by this pass.

**PLAIN LANGUAGE.** Until now every attempt to fix reading changed the JUDGE -- how we compare a
question against what is stored. This one changed the FILING: a word's stored code is built out of
what its neighbours' own context profiles look like, instead of out of its neighbours' arbitrary
identity tags. It is the first change of that kind, and it is the first one that moved the score.

- **`W1_PARADIGMATIC` 0.0298 vs `W0_SYNTAGMATIC` 0.0223: +0.0075 [+0.0023, +0.0128], CI half-width
  0.00525, analytic null half-width at this n 0.00458, ABOVE.** About a 34% relative lift.
- **The two controls that would have explained it away both fail to.** A frequency-matched profile
  control reads 0.0225 and does **NOT** beat W0 (+0.0002 [-0.0048, +0.0053], NOT_SEPARATED), so the
  lift is not frequency in costume. A random-profile permutation null reads 0.0188 and does not beat
  W0 either (-0.0035 [-0.0078, +0.0008], **NOT_SEPARATED** -- numerically lower, not CI-separated
  lower; state it that way). Three hybrid arms at alpha 0.25 / 0.5 / 0.75 all land ABOVE W0 by
  +0.0065 to +0.0070, so the effect is not one lucky configuration.
- `K1` addressing is **1.0000 on all seven arms** and the permuted null is near chance on all seven,
  so the instrument is alive and the arms fail independently.
- Orthographic-leakage check: mean trigram-cosine of each arm's top-1 winner to the query, W0
  0.02684, **W1 0.02939**, hybrids 0.02711-0.02825, null 0.02640, freq-matched 0.02691, against the
  orthographic floor's own reference of 1.0. All clustered at W0's own value. *(The cell reports no
  confidence interval on this check, so read it as descriptive rather than as a CI-separated result
  -- it is strong enough for its purpose: nothing here looks like a disguised spelling channel.)*
- **IT DOES NOT CLEAR A FLOOR AND THE CELL SAYS SO.** W1's own binding floor becomes
  `F_ORTHOGRAPHIC` **0.08731** (its store-dependent constant/prototype floor collapses to 0.03155),
  and W1 sits **-0.0575 [-0.0673, -0.0478] BELOW** it -- **2.9x short**. W0 misses its own floor by
  more (-0.1167 against a constant floor of 0.13896).
- **NO STOP-IF FIRED CLEANLY, and the cell recorded an honest fourth reading rather than forcing
  one:** verdict `w1_beats_w0_but_does_not_clear_a_floor_W0_also_misses`. In its own words: *"the
  write rule was PART of the defect ... but it is nowhere near enough to close a gap that is still
  2-3x the floor. The write rule is not innocent, and it is not sufficient either."*
- **THE CONTRAST THAT MAKES THIS THE SESSION'S STRATEGIC FINDING.** The read-out scoreboard in
  `notes/readout_ceiling_findings_2026-08-17.md` section 7 records **39 read-out arms across two
  cells, on the identical scorer / n / pool / gold, NONE of which clears the binding floor and NONE
  of which beats the incumbent CI-separated** -- and every one of them changed the COMPARATOR
  (exhaustive cosine argmax; CSLS x6; constant-channel subtraction x6; per-anchor z-normalisation;
  divisive normalisation x12; second-order read-time profile x6; successor representation x4). **This
  arm changed the WRITE RULE, and it is the first to beat the incumbent CI-separated.** *(Honesty
  about the tally: that section's headline says 39 while its own family rows sum to 36. This pass did
  NOT re-enumerate the arms; the count is the findings note's, and the CONTRAST -- all prior arms
  comparator-side, this one write-side -- is what is load-bearing and does reproduce from the family
  table.)*
- `wire_status` in the metrics file reads **`VET_PENDING`**. Whether this is wired or shelved is the
  WIRE-or-SHELVE gate's call and has not been made.

---

## DO NOT REDO -- entries added 2026-08-17 (second docs-reconciliation pass, off-data recompute)

### 44. SPARSIFYING THE STORED ADDRESS (KEY) UNDER A PARTIAL CUE -- MEASURED, COSTS ACCURACY
**CLOSED.** `exp_sparse_address_regime_switch_uncompressed_v1`, full, n=3,994. Truncating the stored
key to its top 32 entries loses **-0.0145 [-0.0203, -0.0088]** of addressing accuracy against the
untruncated store, with the oracle-address arm at 1.0000 and the random-address arm at 0.0000, so the
instrument is not the cause. Sparsifying the CUE instead is reliably better than sparsifying the KEY
(+0.0182 [+0.0118, +0.0248]) but still does not beat the flat store (+0.0037 NOT_SEPARATED). Do not
re-run key sparsification as a capability OR an efficiency play on this population.
***REVIVAL CRITERION:** only where the object being sparsified is an ADDRESS INTO AN EXPANDED SPACE
that does not yet exist -- i.e. after an expansion stage is built and measured, so that "sparse"
means "few active units out of many more than we have" and not "throw away 90% of a 21,688-word count
vector". And any revival must set K_WRITE **below** the cue's own median nnz (12.0 here), or the
control arm is a no-op -- which is exactly the construction caveat this cell flagged against itself.*

### 45. THE BASIN EXPLANATION FOR THE CLEANUP NULLS -- REFUTED ON ITS OWN STRATIFICATION
**CLOSED.** `exp_cleanup_basin_conditional_v1`, landed 08-16 22:41, six tau strata summing to 3,994,
known-answer arm 1.0000 in every stratum. Cleanup lift is CI-separated ABOVE **only in the LOWEST-tau
stratum** (+0.0036 [+0.0009, +0.0072]) and NOT_SEPARATED in every higher one **including the highest**
(+0.0154 [-0.0039, +0.0347]), which is the opposite of what the basin account predicts and of what the
cell pre-registered as the confirming pattern. Do not re-open "the cleanup organ never helps because
our cues are outside its basin", and **do not build a settle / attractor-dynamics mechanism to fix
it** -- the one cheap settle arm that was run anyway is null (-0.0010 [-0.0025, +0.0003]).
***REVIVAL CRITERION:** a cue distribution whose tau mass actually sits inside the measured basin
(cliff between tau 0.20 and 0.30; only 6.5% of our items reach tau >= 0.45) -- which means a better
CUE, not a better completer -- or a completer whose basin is re-measured and found to sit where our
cues already are. Either way the revival begins with a measurement of the cue distribution, not with
a build.*

### 46. CUE-SIDE ENGINEERING AS A READ-OUT FIX -- MEASURED, DOES NOT TRANSFER
**CLOSED.** `exp_cue_binarised_readout_transfer_v1` plus `exp_cue_compression_property_diagnosis_v1`.
Binarising the cue is the strongest cue-side change we have found -- **+0.0383 [+0.0295, +0.0473]**
addressing, the largest single addressing gain in the programme -- and its read-out transfer is
**+0.0026 [-0.0026, +0.0078] NOT_SEPARATED**, still -0.1140 [-0.1257, -0.1024] below the binding
constant/prototype floor. Binarising and then projecting gives two thirds of the addressing gain back
(-0.0260 BELOW). **Do not spend another cell on cue representation hoping it will move hit@1.** The
addressing finding itself stands and is a design constraint for the next encoder (presence, not
counts; no dense 256-dim projection).
***REVIVAL CRITERION:** a cue-side change measured DIRECTLY on hit@1 with the four floors recomputed
on its own population -- never one justified by an addressing gain, because the transfer from
addressing to read-out is now measured at approximately zero. Or, differently: after the read-out
stage itself clears its floor, at which point better addressing finally has something to feed.*

---

## CORRECTIONS TO PRIOR CLAIMS -- added 2026-08-17 (second docs-reconciliation pass)

### C36 -- "d 256 -> 8192 moves partial-cue addressing 0.0711 -> 0.0716" MIXES TWO READ REGIMES; MATCHED, IT IS 0.0711 -> 0.0709
- **THE CLAIM, verbatim,** `notes/substrate_phase_diagram_recovered_from_experimental_history_2026-08-17.md`
  line 81: *"going from 256 to 8,192 numbers -- thirty-two times the memory -- moves the score from
  0.0711 to 0.0716, a gap sixteen times smaller than the measurement's own error bar."* The same
  number appears in that note's partial-cue dense-sweep table row (0.0711 / 0.0714 / 0.0716) and has
  since been copied into `exp_sparse_address_regime_switch_uncompressed_v1`'s own
  `EXPECTATION_BEFORE_RUNNING` string and its `OLD_C0_BASED_CEILING = 0.0716` constant.
- **WHAT IS ACTUALLY ON DISK,** `data/exp_sparse_address_dense_value_v1/metrics.json`,
  `PART_1_ADDRESSING`, partial-cue regime, RECOMPUTED by enumerating every grid key: at
  `a_write=1.0`, **D=8192 reads 0.0716 with `a_read=0.2`, and 0.0709 with `a_read=1.0` and 0.0709
  read symmetrically.** D=256 at `a_read=1.0` reads 0.0711; D=2048 at `a_read=1.0` reads 0.0714.
  **So the quoted sweep compares a dense/symmetric read at 256 and 2048 against an ASYMMETRIC read at
  8192.** Matched at `a_read=1.0` the sweep is **0.0711 / 0.0714 / 0.0709** -- 32x the memory buys
  slightly less than nothing.
- **THE CONCLUSION IS UNCHANGED AND SLIGHTLY STRENGTHENED** (dimensionality does nothing for
  addressing; the CI half-width at that point is 0.0078), which is why this is a citation correction
  and not a retraction. But the row as written is a cross-regime comparison, which this project's own
  standing rule 11 forbids; it should read 0.0709, or name the `a_read` of every cell it compares.
- **AND THE CORRECTION ALREADY FILED AGAINST IT IS ITSELF WRONG.**
  `notes/cue_compression_property_diagnosis_v1_findings_2026-08-17.md` flagged the 0.0716 and
  attributed it to *"`BEST_ADDRESSING_CONFIG_partial_cue` at D=2048 with a different projection seed,
  which reads 0.0719"*. **That provenance does not reproduce.** 0.0719 is indeed
  `BEST_ADDRESSING_CONFIG_partial_cue` (D=2048, a_write=1.0, a_read=sym), but **0.0716 is a genuine
  D=8192 reading** -- it is `BEST_ASYMMETRIC_REGIME_SWITCH_CONFIG` (D=8192, a_write=1.0, a_read=0.2,
  ci95 [0.0636, 0.0796]) and appears at that exact grid key as well. The defect is a mixed READ
  REGIME, not a mixed DIMENSION. Both notes are corrected in place with a dated pointer to this
  entry. **This is standing discipline 7 again -- no demotion without a fresh on-disk re-check --
  applied to a correction rather than to a result, and it is the second time in one day (C35 was the
  first).**
