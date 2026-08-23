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

## STATUS.md IS 35x OVER ITS CAP -- BUT ITS SAFETY CONTRACT IS INTACT, SO A TRIM IS NOW *VERIFIED SAFE* (2026-08-20)

**`STATUS_SPEC.md` sec 8 records that an ad-hoc byte-shave once deleted a standing discipline that
had cost two full experiments to learn.** That warning is why I declined to trim `STATUS.md` twice
tonight while adding to it. **This audit replaces the warning with evidence.**

**MEASURED 2026-08-20:**

| | |
|---|---|
| `STATUS.md` | **305,039 bytes / 3,786 lines** -- **35x** the 8,704 B cap |
| `STATUS_LESSONS.md` | 197,717 bytes, **47** entries |
| the six SPEC-REQUIRED sections | **all present, exactly once each** (`# STATUS`, `## POSITION`, `## TOP ITEM`, `## DO NOT REDO`, `## STANDING DISCIPLINES`, `## WHAT IS RUNNING`) |
| **the sec-2 contract** -- *"nothing may appear in `STATUS_LESSONS.md` that is not stubbed by name in `STATUS.md`"* | **46 of 47 stubbed.** The single miss is the literal heading `DO NOT REDO`, a section title rather than a lesson -- a false positive of the check |

**➡️ SO THE OVERSIZE IS ACCUMULATED SESSION NARRATIVE, NOT ORPHANED KNOWLEDGE. Every closed route
is still stubbed, which is precisely the property the spec's cold-session requirement depends on:**
*"A cold session must be able to see that a route is CLOSED from `STATUS.md` alone."*

**WHY I STILL DID NOT TRIM IT, AND THIS IS A JUDGEMENT NOT AN OVERSIGHT.** The risk is asymmetric:
**a bad trim loses knowledge that cannot be recomputed; a delayed trim costs only bytes.** A large
destructive edit is a poor thing to attempt on the 81st continuation of an unattended overnight run,
and the machine-parsed literals currently work (verified: `session_start_hook.py` exit 0,
`board.py self-test` PASS). **What was missing before tonight was not the courage to trim -- it was
the evidence that trimming is safe. That evidence now exists and is written down here.**

**WHOEVER DOES IT:** sections 5 and 6 are **NEVER-TRIM and are floors as well as ceilings** -- they
may be reworded, never emptied. Section 4 (PATH STATE) is the spec's designated first-to-trim
because its content is the most re-derivable. **And the four machine-parsed literals (`AS OF:`,
`## POSITION`, `## TOP ITEM`, `## WHAT IS RUNNING`) are an API shared by
`tools/session_start_hook.py` AND `tools/board.py` -- rewording any of them requires changing both
in the same commit.**


## MOVED OUT OF `notes/STATUS.md` ON 2026-08-21 -- 135 SECTIONS, 280747 BYTES

`STATUS.md` had reached **308,692 bytes against an 8,704 byte cap (35x)** by accumulating
session findings instead of being rewritten in place. Per `STATUS_SPEC.md` sec 7 escalation
step 1 -- *"move more never-trim reasoning to STATUS_LESSONS.md and leave a stub; this is
free"* -- the accumulated blocks are moved here VERBATIM. **Nothing was deleted.** A
byte-identical snapshot of the pre-trim file is also at
`notes/STATUS_ARCHIVE_2026-08-21_pre_trim.md`.

### Contents moved (in original order)

1. [the direction] 🧭 **DECIDED ON THE OWNER'S BRAIN-FOUNDATIONAL CRITERION: BUILD F5**
2. [EARLIER TOP ITEM] ⛔ **THE STRUCTURED COMPARATOR IS *WORSE* THAN THE BAG IT WAS BUILT TO REPLACE**
3. [EARLIER TOP ITEM] ⛔ **THE "LOOKED-UP DEFINITION" WIN IS WITHDRAWN ON ITS SECOND SEED**
4. [WITHDRAWN -- KEPT FOR THE RECORD] A DEFINITION HELPS WHEN **LOOKED UP**, NOT WHEN **READ**
5. [SUPERSEDED, THE NARROW VERSION] THE OBVIOUS FIX -- INDEXING *BY* THE RAW DEFINITION -- FAILS
6. [ANSWERED] WAS THE READ-BACK EVER TESTED ON THE *GOOD* CONTENT
7. [PREVIOUS TOP ITEM, ACHIEVED] PUT THE PHRASE RESULT ON A PROPER FOOTING
8. 🎯 **THE CLEANEST RESULT OF THE DAY, AND IT CLOSES THE QUESTION THE SESSION KEPT CIRCLING:**
9. **WE TIE SECOND-ORDER CO-OCCURRENCE COUNTING. NOT WORSE. NOT BETTER.**
10. ⛔ **THREE TIE ARTIFACTS IN ONE DAY -> THE GUARD IS NOW A FUNCTION, NOT A RULE**
11. 🟢 **THE FIRST ENCOURAGING RESULT IN A LONG STRETCH -- WITH ITS OWN CAVEAT ATTACHED**
12. 🚨 **THE READ-OUT FIX SUBSYSTEM IS DEAD CODE, AND THE ARM WE SHIP WAS NEVER MEASURED**
13. 🔧 GUI: TWO OWNER-REPORTED DEFECTS, BOTH MEASURED AND FIXED
14. ⛔🔴 **READ THIS FIRST: A RESULT THAT LOOKED LIKE THE BREAKTHROUGH OF THE EFFORT WAS WITHDRAWN**
15. **THE SAME HOUR. NOISE SCORED BETTER THAN IT DID.**
16. 🧠 THE DEEP FIDELITY PASS (owner-directed) -- **13 INTERVENTIONS, 5 POSITIONS, 1 SURVIVING GAP**
17. ✅ BOARD Q77 SELF-RESOLVED, AND MY PREMISE WAS THE THING THAT WAS WRONG
18. 🛑 **THE OVERNIGHT LOOP WAS DISARMED (owner instruction 2026-08-20T12:48Z, found UNREAD), THEN**
19. **RE-ARMED ON OWNER REQUEST. Dashboard was CLOSED AND REOPENED for the owner -- it is current.**
20. 🔴 **AND THE OWNER HAS BEEN READING A THREE-DAY-OLD DASHBOARD -- SEE THE PLAN'S TOP BLOCK.**
21. 🔀 **TWO THRUSTS -- THRUST 1 HAS LANDED. THIS IS THE STATE TO RESUME FROM.**
22. ✅ **[SOLVED 2026-08-20, POST-COMPACTION] THE `data/capability_registry.jsonl` "WHOLE-FILE DIFF"**
23. **WAS THE SCHEDULED AUDIT STAMPING `last_audit_utc`. BENIGN. NOT CORRUPTION.**
24. 🧭 RESUME HERE -- **REWRITTEN 2026-08-20 (LATEST). BOTH BOARD Qs ANSWERED; NEXT STEP UNSTARTED.**
25. [PREVIOUS REWRITE] **ONE RESULT, FOUR RETRACTIONS, ONE DECISION.**
26. [PREVIOUS] RESUME BLOCK -- **THE OWNER GAVE TWO DIRECTIONS AND BOTH CHANGED THE PLAN.**
27. 📖 WHERE WE ARE, IN PLAIN WORDS -- added 2026-08-19 because everything below this is jargon
28. 🔴 2026-08-19 -- **THE POSITIVE CONTROL FAILED AND IT CONDEMNS MY EARLIER PROBE: THE BASELINE**
29. **AND OUR ARM WERE BUILT ON DIFFERENT TEXT. THE "2x GAP" AS STATED IS CONFOUNDED.**
30. 🟠 [ITS "31% NEVER RECORDED" STANDS; ITS SIZE-ORDERING IS SUPERSEDED ABOVE] 2026-08-19 -- **PARTIAL CORRECTION TO THE BLOCK BELOW, AND MY VERDICT STATISTIC WAS WRONG.**
31. **WE RECORD ONLY 69% OF OCCURRENCES, AND THE SHORTFALL IS CONCENTRATED ON FREQUENT WORDS.**
32. 🔴🔴🔴 [SEE THE PARTIAL CORRECTION ABOVE -- COVERAGE IS ALSO IN PLAY] 2026-08-19 -- **A RANDOM PROJECTION OF THE CO-OCCURRENCE COUNTS BEATS OUR REPRESENTATION**
33. **BY 2x AT IDENTICAL DIMENSIONALITY. WE LOSE MORE THAN COMPRESSION EXPLAINS.**
34. ⛔ 2026-08-19 -- **WRITE-GATE CELL LANDED, 3 SEEDS. FORMAL VERDICT: (C) AND (D) BOTH FIRE.**
35. **READING (A) IN 0 OF 54 CELLS. FLOOR CLEARED IN 0 OF 54.**
36. ⚠️ 2026-08-19 -- **CORRECTION TO MY OWN INTERPRETATION ONE BLOCK BELOW: THE PROFILES DO**
37. **PREDICT. WEAKLY, BUT REALLY -- 10.4%, CI-SEPARATED, ON 73% OF OBSERVATIONS.**
38. 🔴 2026-08-19 -- [SEE THE CORRECTION ABOVE: "predicts nothing in particular" IS REFUTED] **THE RESIDUAL GATE HURTS, AND IS INDISTINGUISHABLE FROM RANDOM SKIPPING.**
39. **READINGS (C) AND (D) BOTH FIRE. 2 of 3 seeds banked; the picture is not close.**
40. 🧠 2026-08-19 -- **BRAIN-FIDELITY AUDIT ON THE SUBSUMPTION NEGATIVE, AND FIRST THE HONEST**
41. **ACCOUNTING: OF SIX NEGATIVES TODAY, ONE GOT A FIDELITY CHECK, TWO PARTIAL, THREE NONE.**
42. 🧠✅ 2026-08-19 LATER -- **THE FIDELITY AUDIT IS NOW COMPLETE: ALL THREE GAPS FILLED, AND**
43. **THREE OF MY FOUR EXPLANATIONS WERE REFUTED BY THEIR OWN PRE-COMMITTED CONTROLS.**
44. 🧱 2026-08-20 -- **THE UPDATE RULE CHANGES NOTHING EITHER. THE SUM IS OPTIMAL IN ITS OWN**
45. **FAMILY, AND THE PRE-REGISTERED RISK IS EXACTLY WHAT HAPPENED.**
46. 🎚️ 2026-08-20 -- **PRECISION WEIGHTING, THE PINNED TERM, BUILT TO THE ARCHIVE'S OWN CONSTRAINT.**
47. **MEASURABLE, WELL-BEHAVED -- AND STILL NOT A USABLE GATE. FOURTH NEGATIVE ON SELECTION.**
48. 📝 2026-08-19 -- **THE OWNER'S Q71 RULE, TESTED: WHAT MATTERS IS HOW MANY NOTES, NOT WHICH.**
49. **AND I NEARLY HEADLINED A STRONG CLAIM THAT RESTED ENTIRELY ON ONE POINT.**
50. 🧮 2026-08-19 -- **THE 2x2: THE TWO WORKING FIXES ARE SYNERGISTIC, NOT INDEPENDENT -- AND THERE**
51. **IS NO CHEAP VERSION. CENTRING ALONE BUYS 19% OF A 63% TOTAL.**
52. 🔁 2026-08-19 -- **INCREMENTAL DECORRELATION: HYPOTHESIS REFUTED IN THE OPPOSITE DIRECTION.**
53. **DOING IT AFTERWARDS BEATS DOING IT AS YOU GO -- AND MY SCRIPT COULD NOT SEE ITS OWN WINNER.**
54. ⛔ 2026-08-19 -- **COMPETITION AT WRITE TIME FAILS, AND IT FAILS FOR A REASON THAT OVERTURNS MY**
55. **OWN DESIGN ASSUMPTION: SPARSIFYING THE ADDENDS MAKES THE SUM *MORE* DIFFUSE, NOT LESS.**
56. 🔬 2026-08-19 -- **WHICH CAUSE? NOTE-TAKING IS WORTH 39% OF THE DEGRADATION AND NOT ONE POINT**
57. **OF THE DIFFUSION. THE TWO DEFECTS ARE INDEPENDENT AND ONLY ONE IS VISIBLE TO THE RANKING.**
58. 🌡️🌡️ 2026-08-19 -- **THE PHASE DIAGRAM. THERE IS A REAL PHASE BOUNDARY NEAR ~1,000 SENTENCES:**
59. **WE BEAT THE COUNTER BELOW IT AND FALL AWAY FROM IT MONOTONICALLY ABOVE IT.**
60. 🧪 2026-08-19 -- **GAP-TARGETED READING, TESTED TWICE. THE FIRST RUN WAS VOID AND MY OWN GATE**
61. **PASSED IT AT 98% ARM OVERLAP. THE SECOND IS UNDERPOWERED, NOT NEGATIVE.**
62. 🔌 2026-08-19 -- **THE GAP-TARGETED ORGANS ARE BUILT, IMPORT CLEAN, AND ARE DIRECTLY**
63. **STATE-COMPATIBLE WITH THE SUBSTRATE. THEY ARE SIMPLY NOT WIRED IN. NO ADAPTER NEEDED.**
64. 📐 2026-08-19 -- **THE DIMENSIONALITY CLAIM, SETTLED ON MATCHED FORMULA AND MATCHED**
65. **POPULATION. MY ORIGINAL CLAIM WAS INVALID AND MY CORRECTION TO IT WAS ALSO WRONG.**
66. 📉 2026-08-19 -- **REMOVING THE COMMON DIRECTION: A SMALL REAL GAIN, AND A FLOOR THAT MAKES IT**
67. **IRRELEVANT. MY OWN SCRIPT'S VERDICT WAS TOO GENEROUS AND IS CORRECTED HERE.**
68. 📚 2026-08-19 -- **THE OWNER'S Q72 ("GIVE IT ANOTHER TEXTBOOK") HAS TWO HALVES. THE HALF I**
69. **TESTED IS UNTESTED-AT-THIS-N; THE HALF I DID NOT TEST ALREADY HARD_PASSED A MONTH AGO.**
70. 🟢🟢 2026-08-19 -- **THE OWNER REMEMBERED PRIOR WORK THAT PREDICTED TODAY'S FAILURE THREE WEEKS**
71. **AGO, AND IT GIVES THE ORDER OF OPERATIONS: PREDICTION FIRST, NOVELTY SECOND, NOTES THIRD.**
72. ✅ 2026-08-19 -- **9-SEED SWEEP FINAL. THE PRE-REGISTERED CONJUNCTION FAILS, AND THE TWO**
73. **QUANTITIES SEPARATE CLEANLY -- ONE IS SOLID, THE OTHER IS NOISE AROUND A LOW CENTRE.**
74. 📈 [SUPERSEDED BY THE FINAL 9-SEED READ ABOVE] 2026-08-19 -- **RUNNING READ, 7 OF 9 SEEDS: THE ESTIMATE HAS MOVED TWICE AND IS STILL MOVING.**
75. 📉 [SUPERSEDED BY THE 7-SEED READ ABOVE] 2026-08-19 -- **RUNNING READ, 4 OF 9 SEEDS: THE FIRST SEED I HAPPENED TO RUN WAS THE BEST**
76. **ONE, AND I CHARACTERISED THE FINDING FROM IT.**
77. 🔎 2026-08-19 -- **THE INSTRUMENT IS NOT FREQUENCY-DOMINATED, AND THAT MAKES OUR RESULT WORSE.**
78. 🟡 2026-08-19 -- **THE SPOKE REPLICATION: PARTIAL. BY MY OWN PRE-REGISTRATION IT DOES NOT**
79. **REPLICATE, AND I AM HONOURING THAT RATHER THAN RE-READING THE THRESHOLD.**
80. 🔴🔴 2026-08-19 -- **v3 SETTLES IT: THE CORTICAL READ RETRIEVES AND IS NOT COMPETITIVE.**
81. **18 OF 18 FLOOR CELLS FAIL. AND A CUE-BLIND FREQUENCY RANKING BEATS IT AT k>=10.**
82. ✅ [SUPERSEDED BY v3 ABOVE, WHICH ADDS THE FLOORS v2 LACKED] 2026-08-19 -- **v2 LANDED, 3 SEEDS: READING (A) FIRES. THE CORTICAL READ RETRIEVES --**
83. **AND THE CELL CANNOT SAY WHETHER IT BEATS COUNTING, WHICH IS A GAP I BUILT.**
84. 🟢 2026-08-19 -- **THE SPOKE IS NOT SUBSUMED. IT IS ~INDEPENDENT OF COUNTING, AND THE UNION**
85. **MORE THAN DOUBLES IT. THE CONTRAST WITH THE CORTICAL ROUTE IS THE FINDING.**
86. 🔴🔴 2026-08-19 -- **THE CORTICAL ROUTE IS SUBSUMED BY WORD COUNTING. NOT MERELY BEATEN --**
87. **ITS UNIQUE CONTRIBUTION IS BELOW WHAT INDEPENDENCE PREDICTS, AT EVERY k.**
88. 🟢🟢 2026-08-19 -- **v2 SEED 1: THE CUE FIX WORKED AT FULL SCALE, AND THE SCRAMBLE COLLAPSED.**
89. ⚠️ 2026-08-19 -- **CORRECTION TO MY OWN "4.9x" -- A THIRD OF THE SEEN CONTROL WAS A VECTOR**
90. **MATCHING ITSELF. THE READING SURVIVES; THE MAGNITUDE WAS OVERSTATED BY ME.**
91. 🟢 2026-08-19 -- **THE CORTICAL READ DOES RETRIEVE. READING (A) FIRES AT EVERY k -- AND THE**
92. **CELL'S VOID VERDICT IS PART CUE-CONSTRUCTION DEFECT, WHICH IS MINE.**
93. 🔬 2026-08-19 -- **THE REPRESENTATION DIAGNOSTIC. THE SPACE IS NOT BROKEN AND NOT A BLOB: THE**
94. **SIGNAL IS THERE ON HELD-OUT TEXT AND IS 4-7x WEAKER THAN ON READ TEXT.**
95. 🔴 [SEE THE DIAGNOSTIC ABOVE: THE MECHANISM IS "SIGNAL TOO WEAK FOR TOP-1", NOT "IGNORES THE CUE"] 2026-08-19 -- **THE CORTICAL READ CELL IS VOID BY ITS OWN READING (C). NOT A NEGATIVE -- VOID.**
96. ⛔⛔ CORRECTION TO MY OWN CORRECTION, 2026-08-19. **I WAS RIGHT, THEN I "CORRECTED" MYSELF INTO**
97. **BEING WRONG. THE BLOCK BELOW IS THE WRONG ONE. VERIFIED AT RUNTIME, TWICE.**
98. ⛔ [THIS BLOCK IS THE WRONG CORRECTION -- SEE ABOVE] CORRECTION 2026-08-19, TO THE BLOCK DIRECTLY BELOW, WHICH I COMMITTED AND WHICH IS WRONG
99. **I REPLAYED A RULE THE SYSTEM DOES NOT RUN. The 31.8% is explained by that, NOT primarily by**
100. **anchor-field growth, and the auditability claim below is OVERSTATED.**
101. 🔴 [SEE THE CORRECTION ABOVE -- THIS BLOCK'S CAUSAL CLAIM IS WRONG] 2026-08-19 -- **THE GATE'S DECISION CANNOT BE REPLAYED FROM THE FINAL STATE. TWO CONTROLS**
102. **FAILED BEFORE THAT WAS CLEAR, AND IT IS AN AUDITABILITY PROBLEM, NOT A PROBE PROBLEM.**
103. ⚠️ 2026-08-19 -- [v1, SUPERSEDED BY THE BLOCK ABOVE] **A PRE-BUILD PROBE WHOSE OWN POSITIVE CONTROL FAILED. READ THE CAVEAT FIRST.**
104. 🟡 2026-08-19 -- **THE SENSORIMOTOR SPOKE LANDED. READING (B) FIRES: IT TIES THE TEXT CHANNEL.**
105. 🛑 2026-08-19 -- **THE CORTICAL READ ROUTE IS UNWINNABLE ON THE CLOZE TASK, MEASURED BEFORE**
106. **BUILDING IT. AND THE REASON IS BRAIN-FAITHFUL, NOT A DEFECT.**
107. 🧠🔴 2026-08-19 -- **READING (e) FIRED. THE READ-OUT NEVER CONSULTS GROUNDED FACTS.**
108. **AND THE BRAIN-FIDELITY NAME FOR IT: WE BUILT HIPPOCAMPUS-TO-CORTEX TRANSFER AND THEN READ**
109. **THE ANSWER OUT OF THE HIPPOCAMPUS.**
110. 🔧 2026-08-19 LATER -- PHASE 2 RE-RUN AS A **WIRING DIAGNOSTIC**, NOT A REPORT CARD [LANDED]
111. ⏹️ AUTOLOOP **DISARMED** BY OWNER 2026-08-19. BOTH EARLIER CELLS LANDED.
112. 🔬 GROUNDING PRECISION LANDED (3 seeds, n=398-441, NOT underpowered by the cell's own gate)
113. 🟢🟢 2026-08-19 -- THE BEST-CONTROLLED POSITIVE THIS PROGRAMME HAS: **THE SIGNAL TEXT LACKS IS IN
114. THE SENSORIMOTOR NORMS. 0.6413 vs CO-OCCURRENCE'S 0.3067, FOUR CONTROLS BINDING.**
115. 🎯 THE STRONGEST RESULT OF 2026-08-19, AND IT REFRAMES THE TOP ITEM: **IT IS A RANKING PROBLEM**
116. 🧭 WHAT THE 2026-08-19 SESSION CONVERGES ON -- STRATEGIC READ, **HYPOTHESIS-PENDING-VET**
117. 🚨 THE MOST TRANSFERABLE THING FROM 2026-08-19: **SEVEN DEFECTS, ALL MINE, ALL IN THE TOOLING, AND
118. EVERY ONE LOOKED LIKE A FINDING ABOUT THE SUBSTRATE.**
119. WHAT LANDED 2026-08-19 (Phases 0-3; `2e8134fd2` .. `85b146f69`)
120. FOUR CONTROL DEFECTS I BUILT AND FIXED IN ONE DAY -- THE PATTERN IS THE LESSON
121. WHERE WE ARE, IN TWO SENTENCES
122. THE FOUR ARTIFACTS -- USE THESE, DO NOT RE-DERIVE THEM
123. NEXT STEPS, RANKED -- START AT 1
124. THE STRONGEST PREDICTOR, AND IT IS FREE
125. MY FOUR ERRORS THIS SESSION -- ALL ONE FAULT, DO NOT REPEAT IT
126. STANDING CONTEXT
127. [ARCHIVED TOP ITEM] FIND AN ADMISSIBLE SUPERVISION SIGNAL THAT IS NOT THE EVALUATION GOLD
128. SUPERSEDED TOP ITEM -- THE WRITE RULE WAS THE FIRST THING TO MOVE READ-OUT (LESSONS: WRITE RULE)
129. CUE SIDE -- CLOSED IN FOUR CELLS (LESSONS: CUE SIDE CLOSED; DO-NOT-REDO 44, 45, 46)
130. PHASE DIAGRAM -- THERE ISN'T ONE (LESSONS: PHASE DIAGRAM)
131. BRIDGING -- TWO MEASURED NULLS (LESSONS: DO-NOT-REDO 38, 43)
132. STORAGE -- THE WRITE/READ ASYMMETRY IS REAL AND DID NOT SURVIVE AS A WIN (LESSONS: WRITE/READ ASYMMETRY)
133. CLEANUP / SURPRISE / TARGET SPACE (LESSONS: CLEANUP MEMORY, SURPRISE, TARGET SPACE)
134. TOOLING STATE (LESSONS: VERDICT BAR, SKIPPED FULLS, C31, C32)
135. [ARCHIVED 2026-08-19] RUNNING / BLOCKED -- STALE, SUPERSEDED BY `## WHAT IS RUNNING` AT THE TOP

---

## [the direction] 🧭 **DECIDED ON THE OWNER'S BRAIN-FOUNDATIONAL CRITERION: BUILD F5**

**Q90 ANSWERED 2026-08-20T21:13Z:** *"if you've drilled this online and it points in other
directions to be brain foundational, follow those directions. if brain foundational points in this
direction, do it again and verify we're actually brain foundational."*
**`notes/BRAIN_FOUNDATIONAL_ANSWER_the_missing_consumer_is_F5_and_we_quantise_where_the_brain_is_graded_2026-08-20.md`**

**➡️ BRAIN-FOUNDATIONAL POINTS AWAY FROM MORE PERCEPTUAL NORMS AND TOWARD `ORGAN_MAP` F5 -- THE
COHERENCE MONITOR / N400 GENERATOR, ALREADY LISTED THERE AS *MISSING* AND A LEGITIMATE PHASE-B
TARGET.** N400 = **the magnitude of update forced on a running probabilistic SITUATION MODEL** by
the incoming word, a **precision-weighted prediction error against the CURRENT DISCOURSE STATE**
(Rabovsky/Hansen/McClelland 2018; Kutas & Federmeier 2011). **Reference point PINNED; norm, update
rule and precision estimator UNPINNED.**

**✅ CORRECTED -- SMALLER THAN I FIRST SAID.** I claimed F5 depends on F6 *"also MISSING"*. **Wrong.**
`ORGAN_MAP` **E2**: `hdlab/situation_model_accumulate.py` is **`WIRED: YES`, LIVE**, and its fidelity
note reads **RIGHT-OP-WRONG-PLACE / PARTIAL -- *"has the register, has none of the PE-driven
segmentation that decides WHEN to write."*** **➡️ F5's missing piece and E2's are THE SAME PIECE: the
register runs; nothing computes prediction error against it. NOT "build two organs" -- "add the error
signal to an organ that already runs."** *Also PINNED: a boundary posts when PE crosses threshold
(Zacks & Franklin SEM).* Brief: `notes/F5_DESIGN_BRIEF_the_register_already_exists_only_the_error_signal_is_missing_2026-08-20.md`
**🔴 THE TRAP: G2's gate NEVER FIRED (`skip=0.00`) because its residual was `sign()`-quantised. THE
ERROR MUST STAY GRADED, and the build must PRINT the error distribution, the firing rate and a
POSITIVE CONTROL before any verdict is read.**
**⚖️ THE CASE AGAINST: the bottleneck is that nothing reads the banked MEANINGS. A coherence monitor
gives the SITUATION REGISTER a use; `GROUNDED_MEANING` facts stay outside that loop unless the link
is DESIGNED IN. Built without it, the gap survives the build.**

### 🎯 FOUR INDEPENDENT ROUTES, ONE TARGET (none chosen to agree with the others)
| route | conclusion |
|---|---|
| **measurement** | nothing READS the banked meanings; 3 attempts to make retrieval use them FAILED |
| **learning research** | definitions teach only alongside VARIED CONTEXT (Miller & Gildea; Bolger et al.) |
| **philosophy** | referential grounding needs a **HISTORY OF SELECTION** -- use, with consequences |
| **neuroscience + ORGAN_MAP** | the consumer is **F5**, MISSING; our nearest organ NEVER FIRES |

### 🔴 THE VERIFICATION ASKED FOR: WE ARE **NOT** BRAIN-FOUNDATIONAL HERE, AND IT IS MEASURED
`ORGAN_MAP` **G2** (`predictive_coding.py`) = **RIGHT-OP-WRONG-METRIC** -- residual computed on a
**`sign()`-quantised** prediction, no precision term, **WIRED: NO.** Consequence:
`exp_pc1_predictive_coding_residual_gate_v1` at thresh 0.3 -> **skip = 0.00, byte-identical to
ungated. THE GATE NEVER FIRED.** *That is what a quantised error predicts -- the null is a
consequence of the infidelity, NOT evidence about prediction error. **Interpretation note written
beside that cell so it is not cited as "surprise gating does not work here".***

**AND THE SAME SUBSTITUTION IS IN THE READ-OUT** (`canonicalize:776` hard-signs the query while
anchors are graded). **MEASURED, n=400: nearest anchor differs 42.5%; graded clears the 0.45 bar
15.5% vs 8.2%; bank/refuse FLIPS on 7.2%.**
**⚠️ A DOUBLING IS NOT A WIN: the distributional read-out is 0-4% MEANINGFUL, so doubling its yield
doubles the noise.** **ESTABLISHED: the gap is real and consequential. NOT ESTABLISHED: that fixing
it helps.** *And it does not touch the bottleneck -- nothing still reads what is banked.*

## [EARLIER TOP ITEM] ⛔ **THE STRUCTURED COMPARATOR IS *WORSE* THAN THE BAG IT WAS BUILT TO REPLACE**

**A SECOND 7-DAY-PENDING BLIND HAND-SCORE FOUND AND SCORED TODAY.**
`notes/structured_comparator_handscore_the_fix_is_WORSE_than_the_bag_2026-08-20.md`
`exp_structured_comparator_v1` landed 2026-08-13 `STRUCTURAL_PASS_PENDING_HANDSCORE`, never scored.
**It is the built fix for the defect this whole day kept hitting** -- the read-out compares BAGS of
nearby content words, so it cannot separate *"X means Y"* from *"X occurs near Y"*.

| 100 rows, blind, `arm_key.json` unopened until scores were on disk | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|
| **CONTROL** -- bag of nearby content words (SHIPPED) | 0% | **24%** | 76% |
| **STRUCTURED** -- word in THIS DEPENDENCY RELATION to the target | 0% | **6%** | **94%** |

**RELATED 24% vs 6%, Fisher one-sided p = 0.0113 -- THE CONTROL IS SIGNIFICANTLY BETTER.**
MEANINGFUL 0 vs 0 (p=1.0) -- **a tie at ZERO, not a tie between working systems.**

**AND IT IS A FAIR TEST, NOT A REACHABILITY FAILURE:** the cell had already shown **97.8% argmax
disagreement** (6,145 of 6,283 lemmas) and a worked witness -- `wedding` is in the CONTROL bag in
ALL THREE `whisky` sentences and in the STRUCTURED features in NONE. **STRUCTURED genuinely cannot
produce `whisky -> wedding`. It produces DIFFERENT errors instead, and MORE of them. Being unable
to make a known mistake is not the same as being right.**
**➡️ THE BAG-OF-WORDS DEFECT REMAINS OPEN AND IS NOW HARDER: its principled fix is measured worse.**
*Landed `metrics.json` deliberately NOT modified; verdict recorded beside the evidence. Keep it
DEFAULT-OFF. 🚫 Do NOT line these up against the historical 35/64/94 figures -- standing
prohibition.* **Limits: n=50/arm, one scorer, and the only separated cell is RELATED, the softest
category.**

## [EARLIER TOP ITEM] ⛔ **THE "LOOKED-UP DEFINITION" WIN IS WITHDRAWN ON ITS SECOND SEED**

**Seed 7 gave `BOTH` a 16-rank gain. Seed 101 gives it -1.0 AND AN INFORMATION-FREE BLEND BEATS IT.**

| seed 101, n=119, 195 candidates | rank |
|---|---|
| PROFILE | 53.0 |
| BOTH (profile + **right** lookup) | 52.0 -- a **1-rank** "gain" |
| BOTH_SHUFFLE (profile + **wrong** lookup) | 62.0 |
| **BOTH_NOISE (profile + RANDOM VECTOR)** | **45.0 -- BEST ARM ON THIS SEED** |
| COOC | 3.0 |

**BLENDING WITH RANDOM NOISE BEAT BLENDING WITH THE RIGHT DEFINITION.** The guard printed its own
verdict unprompted: *"AN INFORMATION-FREE BLEND ALSO BEATS THE PROFILE -- the gain is SMOOTHING, not
the definition. BOTH is an ARTIFACT unless it clears these two."* Also unstable WITHIN seed 101
(+11.5 low exposure, -16.0 high, where seed 7 won both).
**✅ SEED 13 CONFIRMS IT FROM THE OTHER DIRECTION: `PROFILE 57.0 | BOTH 52.0 | BOTH_SHUFFLE 53.0`
-- using ANOTHER TERM'S definition performs the SAME as the right one, one rank apart.**
**ALL THREE SEEDS: `BOTH - PROFILE` = -16.0 / -1.0 / -5.0, and on TWO OF THREE an information-free
blend matched or beat the treatment.** A gain that appears on one seed and that a RANDOM VECTOR
reproduces on another is not a gain.

**⚠️ FOURTH SINGLE-SEED WIN READ AS A RESULT IN A WEEK. The rule was written in my own limits
section BEFORE the second seed ran, and I still led with the headline.**
**✅ WHAT WORKED: the controls were added BEFORE replication, precisely because a blend beating its
own component is where artifacts hide. They caught it automatically.**

**WHAT SURVIVES ON BOTH SEEDS:** `DEF_LOOKUP` alone is WORSE than `PROFILE` (67.0/54.5; 69.0/53.0).
`SHUFFLE_LOOKUP` is far worse than `DEF_LOOKUP` (106/67; 104/69) -- **the definitions DO carry
term-specific signal, just not enough.** **`COOC` 5.0 / 3.0 crushes every arm on both seeds.**

**⛔ AND MY HOUR-OLD CORRECTION IS ITSELF WITHDRAWN.** I used this artifact to refute my own
"combining dilutes when one channel is weaker" and replace it with "the condition is INDEPENDENCE".
**That refutation rested on the artifact. NEITHER boundary is established** -- both claims came from
single runs, in opposite directions. *The owner's original three-seed "combining channels helps"
result is untouched; what is withdrawn is MY attempt to say WHEN.*

## [WITHDRAWN -- KEPT FOR THE RECORD] A DEFINITION HELPS WHEN **LOOKED UP**, NOT WHEN **READ**

**`notes/a_definition_helps_when_it_is_LOOKED_UP_not_when_it_is_read_2026-08-20.md`**
Two hours ago I measured that indexing a term by its definition's RAW TEXT is 28 ranks worse and
called the route closed. **Too broad. Changing HOW the definition is consumed reverses the sign.**

| ALL, n=132, 211 candidates, seed 7 | midpoint rank (lower better) |
|---|---|
| PROFILE (shipped) | 54.5 |
| DEF_LOOKUP = mean of the **already-learned profiles of the words the definition NAMES** | 67.0 |
| **BOTH = profile + right definition-lookup** | **38.5  (-16 RANKS)** |
| **BOTH_SHUFFLE** = profile + **another term's** lookup | **58.0 -- WORSE than profile** |
| **BOTH_NOISE** = profile + random vector | **78.0 -- far worse** |
| **COOC** | **5.0** |

**➡️ "a drupe is a fleshy FRUIT" is worth little as seven tokens and a lot as a POINTER TO `fruit`
-- borrowed volume.** *Both information-free blends FAIL to beat the profile, so the gain requires
the RIGHT content and is NOT smoothing.* Holds in both strata (**-19.0 low exposure, -12.0 high**).
**⚠️ STILL 8x WORSE THAN COUNTING WORDS (5.0). An internal improvement, NEVER a capability claim.**
It is, though, **the first thing measured all day that makes the definitions DO anything.**

### ⛔ TWO OF MY OWN CLAIMS CORRECTED
1. **"Combining helps only when channels are comparably strong; a weaker one DILUTES" -- REFUTED**
   by this, two hours after I published it in STATUS, the plan, a note and a commit. DEF_LOOKUP
   (67.0) is WEAKER than PROFILE (54.5) and BOTH still gains 16 ranks. **THE CONDITION IS
   INDEPENDENCE, NOT COMPARABLE STRENGTH:** the second channel must be an INDEPENDENT ESTIMATE OF
   THE SAME THING IN A COMPARABLE REPRESENTATION (a mean of learned profiles), not merely more text
   (a raw 7-token vector). **The owner's original "combine channels" hypothesis was right and my
   amendment made it worse.** Corrected in place in the earlier note.
2. **MY PRE-COMMITTED PREDICTION FAILED.** I predicted DEF_LOOKUP would beat PROFILE at LOW exposure
   and not HIGH. It beat it at NEITHER (+8.5 / +11.0). Only the COMBINATION stratifies. **A
   prediction reinterpreted after the fact did not succeed.**

*🚫 `GENUS_HEAD` alone (71.2) is the WORST definition arm -- mild evidence against the narrowest
"head noun is the schema pointer" reading.*

### ⛔ **3rd CORRECTION: I LABELLED THE BRAIN MECHANISM "PINNED". `ORGAN_MAP.md` §G1 SAYS IT IS NOT.**
Verbatim: *"Lexical-semantic acquisition: **UNPINNED, deliberately** ... No equation is offered for
either half. (And the strong 'fast mapping writes directly to cortex' alternative has **collapsed
under replication** -- Warren & Duff 2014; Cooper, Greve & Henson 2019.)"*
**PRESENTING AN INVENTION AS BRAIN-DERIVED IS THE SPECIFICALLY BARRED MOVE, and it is the SAME
FAULT ALREADY ON RECORD FOR VSA BINDING.** I cited Tse et al. 2007 as pinning schema-dependent
rapid consolidation; **I was not entitled to.** What stands: the BEHAVIOURAL phenomenon (few-shot
word learning when told the kind of thing) -- a fact about behaviour, not a mechanism. **The
profile-averaging stand-in is OUR INVENTION UNDER TEST.** The empirical ranks are unaffected; **the
JUSTIFICATION is withdrawn**, which matters because a brain-derived label is what would license
building on this without more evidence. *Found only by running the THIRD archive check (ORGAN_MAP
corrections) AFTER building -- the rule is three reads BEFORE proposing a brain mechanism, and I did
two of them late.*

## [SUPERSEDED, THE NARROW VERSION] THE OBVIOUS FIX -- INDEXING *BY* THE RAW DEFINITION -- FAILS

**`notes/wiring_the_definitions_into_retrieval_would_not_help_measured_2026-08-20.md`**
Same space, same cue, same 212 candidates, same scorer; **one variable: what the index row is made
of.** Ranks via `tools/rank_with_ties.py`. n=133, seed 7.

| arm | midpoint rank (lower better) |
|---|---|
| **PROFILE** -- accumulated context vector. **THE SHIPPED ROUTE.** | **64.0** |
| **DEFINIENS** -- the term's own definition. **THE PROPOSED FIX.** | **92.0** |
| BOTH | 71.0 |
| SHUFFLE_DEF -- *another* term's definition | 99.0 |
| **COOC** | **5.0** |

**➡️ INDEXING BY THE DEFINITION IS 28 RANKS WORSE THAN THE PROFILE IT WOULD REPLACE. DO NOT BUILD
IT.** *DEFINIENS (92) still beats SHUFFLE_DEF (99), so the definitions are NOT noise -- they carry
term-specific signal, just LESS of it. Mechanism is almost certainly VOLUME: ~7 words against a
profile summed over dozens of encounters. A short high-quality signal loses to a long low-quality
one on a task rewarding breadth.*
**🚫 NARROW NEGATIVE, DO NOT WIDEN IT:** one way of consuming meaning (as an index vector), one task
(retrieve term from sentence cue). **Untested and open: use the definition to ANSWER rather than
RETRIEVE; use its GENUS for inference; SEED a new term at first encounter, where volume is zero and
seven good words may beat nothing.**
**📌 A BOUNDARY ON OUR MOST REPRODUCIBLE POSITIVE: `BOTH` (71) is WORSE than `PROFILE` (64).**
Combining channels helps when both are comparably strong; **when one is strictly weaker it
DILUTES** -- 71 sits between 64 and 92, exactly as an average would.
**⚠️ AND COOC IS 5.0 AGAINST THE BEST ARM'S 64.0 ON A TASK BUILT TODAY.** None of today's good news
touches the headline: the phrases are good OUTPUT; the RETRIEVAL machinery is >10x below counting.
*Leak control did real work: **3,269 cue sentences excluded** as a definition's own source; 79 of
212 terms dropped for having no non-source cue, reported rather than absorbed.*

## [ANSWERED] WAS THE READ-BACK EVER TESTED ON THE *GOOD* CONTENT

**THE PHRASE RESULT IS HARDENED (4 seeds, 5 floors, ORACLE at 100%) -- AND THEN THE NEXT LINK IN
THE CHAIN TURNS OUT TO BE BROKEN.**
`notes/good_definitions_in_nothing_competitive_out_the_readback_gap_2026-08-20.md`

| step | status |
|---|---|
| reading produces definitional PHRASES | **GOOD** -- 32% vs 4% paired, p=0.020; 4 seeds vs strong floors |
| those phrases are BANKED | works -- 212 of 402 provenance rows |
| **anything READS them back out and does better with them** | ❌ **NOT COMPETITIVE** |

`exp_cortical_read_consolidated_v1` spec `v3_floors_at_k`, re-read from metrics today: **3 seeds,
`UNDERPOWERED: false`, `items_predate_mechanism: true`, and `CONTEXT_clears: false` /
`BOTH_clears: false` at EVERY k (1/5/10/25/50) on EVERY seed.** `READING_A` fires, so the route
RETRIEVES -- it just never beats `RANK_COOC_floor`. **And this is the route built precisely because
its absence meant consolidation could be ablated to zero without moving the read-out.**

**➡️ WE ARE WRITING BETTER NOTES INTO A NOTEBOOK NOTHING READS COMPETITIVELY.**

### ✅ **SETTLED THE SAME HOUR. MY HYPOTHESIS WAS WRONG AND THE TRUTH IS STRUCTURAL.**
I guessed the read-back had only been tested on single-word content. **No.**
`cortical_recall.py:90 build_cortical_index` iterates the consolidated **TERMS** and builds one
vector per term from **`context_profiles`** (+ spoke). **THE MEANING VALUE IS NEVER VECTORISED,
NEVER COMPARED, NEVER READ** -- the dict is used for its KEYS, and `cortical_recall` attaches the
meaning to the hit for DISPLAY after ranking is already decided. `cue_vector` builds the query from
`context_profiles` too, so **both sides are the distributional representation.**

**➡️ THE CONTENT OF THE CONSOLIDATED STORE IS ARCHITECTURALLY IRRELEVANT TO THE ONLY ROUTE THAT
READS IT. 4% -> 32% MEANINGFUL CANNOT MOVE IT, BECAUSE IT NEVER LOOKS AT THE MEANING.** The
definitional gate changes WHICH TERMS reach consolidation (the candidate set / coverage), never the
vectors anything is ranked by.
**AND THIS MECHANICALLY EXPLAINS THE INERTNESS FINDING** -- consolidation ablates to zero effect
because the read-out ranks by accumulated context profiles, the representation measured at or below
co-occurrence counting all week. **NOT A TUNING GAP: NOTHING IN THE READ PATH CONSUMES MEANING.**

**🔑 SO THE REAL GAP IS NAMED AND IT IS A BUILD TARGET, NOT A DEFECT:** there is no route by which
the CONTENT of a learned definition affects any later answer. **"Improve the definitions" and
"improve the read-out" are currently DISCONNECTED PROBLEMS, and that was not visible before today.**
Whether to build the connection is a strategy call -- **Q89 amended a third time with the plain-
language version.** *🚫 Still do not spend on extractor recall: more material that nothing reads
is not more value.*

## [PREVIOUS TOP ITEM, ACHIEVED] PUT THE PHRASE RESULT ON A PROPER FOOTING

**TODAY'S FINDING, IN ONE LINE: the half of the output nobody had ever scored is the good half, and
what makes it good is the FORM (a whole phrase) rather than the SOURCE (read off the page).**

| same rubric, same scorer, same day | MEANINGFUL |
|---|---|
| definitional **PHRASE** (`d.definiens`) | **32%** |
| definitional **HEAD** (`d.head`, SAME source, one noun) | **4%** |
| distributional (`canonicalize`) | **0-4%** |

Paired on identical terms and traces: McNemar **8 for / 1 against, p = 0.020**. Head-vs-distributional
is **NOT distinguishable** (p = 0.2475), which is what isolates FORM as the cause.
Full: `notes/the_phrase_pathway_measured_definitional_vs_distributional_2026-08-20.md` and
`notes/b3_audit_scored_the_win_is_the_phrase_form_not_the_definitional_source_2026-08-20.md`.

**➡️ THE TOP ITEM IS TO HARDEN IT, AND THAT IS DELIBERATELY *NOT* BUILDING ON IT.** Every phrase
number is **n=25, ONE seed, ONE corpus, 12,000 sentences, and scored by an interested party** -- me,
who argued the phrases looked better before scoring them. The B3 half was genuinely blind; the phrase
half could not be, because a phrase is visibly a phrase. **A result this load-bearing cannot rest
there**, and Q89 is open on exactly this fork, so firming up the evidence the owner is deciding on is
in-bounds while acting on it is not.

**WHAT WOULD MAKE IT SOLID:** seeds and CIs rather than one run; the strongest floor actually RUN on
the phrase population; and a scorer who is not me, or a rubric mechanical enough that being me stops
mattering.

### ✅ **THE FLOOR PROBLEM IS SOLVED, AND IT REMOVES ME FROM THE SCORING LOOP (seed 7, n=160)**
Every floor we own is WORD-TO-WORD, so phrase output had no admissible floor and no machine scorer.
**ConceptNet cannot match a phrase exactly, but it holds 154,974 `/r/IsA` + 2,173 `/r/DefinedAs`
edges -- so score a HIT when the phrase CONTAINS an attested hypernym of the term.** Independent
gold, machine-computed, works on phrases. Gold covers **75%** of our terms; scored on those.

| arm (all floors LENGTH-MATCHED to ours) | hit rate | 95% CI | mean words |
|---|---|---|---|
| **OURS** | **19.4%** | [14.0, 26.2] | 6.9 |
| **CO_SENTENCE** -- random content words FROM THE SAME SENTENCE | **7.5%** | [4.3, 12.7] | 6.9 |
| CONSTANT (most common phrase, every term) | 2.5% | [1.0, 6.3] | 4.0 |
| RANDOM_NOUNS -- **the information-free version of our arm** | 0.6% | [0.1, 3.5] | 6.9 |
| SHUFFLE -- another term's definiens | **0.0%** | [0.0, 2.3] | 6.8 |

**OURS's LOWER bound clears EVERY floor's UPPER bound** (gate on the upper bound, standing rule).
**THE METRIC'S OBVIOUS FAILURE MODE IS LENGTH -- a longer phrase gets more chances to contain a
hypernym -- so every floor emits the SAME number of words.** `RANDOM_NOUNS` at 0.6% with the
identical 6.9-word mean shows it is not counting words, and **`SHUFFLE` at 0.0% is the decisive
one: a real definiens, correct form, correct length, but about the WRONG TERM, scores ZERO.** So
the metric is not rewarding definition-shaped text; it requires the phrase to be about the right
word. *This is the first machine-measured result this week where our output clears a strong floor
on an independent gold -- and it is still a claim about the EXTRACTOR's output, NOT about the HDC
substrate, whose own read-out is the 4% arm.*
**ALL 4 SEEDS IN AND CLEARING: OURS 19.4 / 18.9 / 20.3 / 21.3%; strongest floor 7.5 / 7.4 / 8.2 /
7.7%.** **⚠️ CORRECTION TO MY OWN EARLIER LINE: SHUFFLE IS NOT 0.0% ON EVERY SEED** -- seed 29 reads
**2.6%** (4 hits). Pooled 4/621 = **0.6%**. Still a real floor, still cleared, but "zero everywhere"
was wrong and I had already said it twice.
**THE HARDER FLOOR ALSO CLEARS (seed 7): `CO_SPAN`** -- a CONTIGUOUS same-length window from the
SAME sentence, so syntax is preserved and only span-SELECTION differs -- reads **4.4% [2.1, 8.8]**
against OURS's lower bound of 14.0%. **Its overlap with our own words is only 12.8%**, so the
false-negative risk (a floor that CONTAINS the treatment) did not materialise.
**ORACLE POSITIVE CONTROL = 100.0% [97.7, 100] in-run**, plus a standalone check
(`verification/test_hypernym_matcher_positive_control.py`) firing **400/400** with **0.2%**
false-fire. **A 0.0% floor is only evidence once the scorer is shown to return non-zero.**
*Note `CO_SPAN` (4.4%) scores BELOW `CO_SENTENCE` (6.2%) -- I expected the opposite. `CO_SENTENCE`
draws CONTENT words only, while `CO_SPAN` and OURS both spend slots on function words. So
`CO_SENTENCE` is the harder floor and is ADVANTAGED relative to ours.*

**🚨 NEVER QUOTE THE 19% AS AN ACCURACY -- IT IS A LOWER BOUND ON A DELIBERATELY-CRIPPLED YARDSTICK.**
This gold drops **218,061 WordNet-provenance edges**, and that omission IS its admissibility
property -- **the taxonomic backbone goes with them. `dog IsA animal` IS NOT IN THIS GOLD.** Also
**52.8% of gold objects are MULTI-WORD** and unmatchable by a whitespace-split phrase. So a CORRECT
definition routinely MISSES: our `piraeus -> "a port"` is right, the gold offers only
`administrative_region`; `drupe` has no IsA edge at all. **The under-count hits every arm equally so
the COMPARISON is untouched, but the absolute rate is quotable only as "beats the strongest floor".
The hand-score's 32% is the better quality estimate.**

**🚫 DO NOT SPEND MORE ON HEAD-SELECTION.** Today's `_MEASURE_HEAD` fix (`way`/`means`/`part`, empty
heads 7 -> 5) was a correct fix to the component the B3 audit shows barely carries the result. The
`thing`/`word`/`idea` empty-head backlog should be **re-priced or dropped**, not worked.

## 🎯 **THE CLEANEST RESULT OF THE DAY, AND IT CLOSES THE QUESTION THE SESSION KEPT CIRCLING:**
## **WE TIE SECOND-ORDER CO-OCCURRENCE COUNTING. NOT WORSE. NOT BETTER.**
Synonym-rank task, 3 seeds, paired on identical items, against the floor that is actually trying.
**`SUBSTRATE - COOC2 = -1.0, CI [-5.0, +1.0], NOT SEPARATED.`** Per-seed: SUBSTRATE 46/35/42 vs
COOC2 38/30/31. `SUBSTRATE - FREQUENCY = -7.0 CI[-13,-1]` separated.
**Every piece of HD machinery -- random projection, accumulation, bundling, cosine read-out -- lands
where a plain co-occurrence count lands.** *Not a LOSSY copy (which four routes suggested today) --
a FAITHFUL one.* **➡️ IMPROVING THE CODE CANNOT HELP, AND THAT IS NOW MEASURED, NOT INFERRED. The
lever is what goes INTO the counts.** ⚠️ **SCOPE: this tested only the DISTRIBUTIONAL half. BINDING
and COMPOSITION -- the genuinely distinctive part -- were NOT under test. A tie here is not a verdict
on the approach.** Also: a tie is a NULL; the CI excludes only effects above ~5 ranks. **📋 ON THE
BOARD AS Q82 -- an owner call.**

## ⛔ **THREE TIE ARTIFACTS IN ONE DAY -> THE GUARD IS NOW A FUNCTION, NOT A RULE**
`DG@0.01` (18.0; noise scored 14.0) - the 775-of-775 miss rate (random also scores 0) - `COOC1`
(21.0 optimistic, **100.0 pessimistic**, 92.2% of items tied). All three are
`1 + sum(scores > scores[target])` meeting a spiky score distribution: **ties count as BEATEN, so the
LESS a representation knows the better it scores.** **I added the "report both tie conventions" rule
to CLAUDE.md that MORNING and then failed to apply it to my next two scripts.** ➡️ **USE
`tools/rank_with_ties.py`** -- returns tie count + `suspicious`; there is no signature that yields a
bare rank. Self-tested on all three real failures plus a no-cry-wolf control.
**⛔ ALSO DEAD: my "we ship the worst of three quantisation configs" -- all three TIE (+0.0,
CI[+0.0,+1.0]). The 0-live-calls fact stands; the claimed benefit does not reproduce.**


## 🟢 **THE FIRST ENCOURAGING RESULT IN A LONG STRETCH -- WITH ITS OWN CAVEAT ATTACHED**
**Where does a KNOWN-CORRECT synonym rank among all anchors?** SUBSTRATE **46.0 / 35.0** vs
FREQUENCY 89.0 / 60.0 vs UNIFORM 197.0 / 155.0 (382 / 327 anchors, 2 seeds).
**BUT THE PAIRED NUMBERS DEFLATE THAT HARD (3 seeds, complete): SUBSTRATE-UNIFORM -111.0
CI[-141,-83]; FREQUENCY-UNIFORM -97.0 CI[-119,-79]; SUBSTRATE-FREQUENCY only -7.0 CI[-13,-1].**
**THE CUE-BLIND FREQUENCY FLOOR DOES 97 OF THE 111 RANKS. OUR OWN CONTRIBUTION IS 7 RANKS OUT OF
~350, CI UPPER BOUND -1.0.** Per-seed medians (46 vs 89) LOOK like 2x; paired on identical items it
is seven ranks. *Same trap as the structure-vs-bag tie: median-of-differences != difference-of-
medians.* **Not blind, but mostly a FREQUENCY code with a thin lexical layer on top -- which is what
three other measurements today independently predict.** ⚠️ **BUT I FLAGGED THAT FLOOR AS TOO WEAK BEFORE THE RESULT
WAS QUOTED:** ranking by raw frequency is a strange way to hunt a SYNONYM. The honest opponent is
**SECOND-ORDER CO-OCCURRENCE** (synonyms don't co-occur but share contexts -- the count version of
what we do). Queued. **If the counter ties or wins, this becomes "counting carries the meaning and
we are a lossy copy".**
*Replaces a WITHDRAWN binary measure: "we never pick an available correct synonym, 775 of 775" is
WORTHLESS -- a random picker also scores 0 (expected 0.44 / 0.16 hits, P(zero|random) 0.64 / 0.85).*

## 🚨 **THE READ-OUT FIX SUBSYSTEM IS DEAD CODE, AND THE ARM WE SHIP WAS NEVER MEASURED**
Runtime call-counting over a real 1,500-sentence read: `canonicalize` (**SIGNED query**, `np.sign`
hardcoded line 776) = **451 calls**; `canonicalize_fast` (graded query, the ONLY door to
`ReadoutConfig` F1/F2/F3) = **0**; `freeze` / `freeze_graded` / `operating_readout` = **0**.
**⛔ CORRECTS MY OWN CLOSURE FROM THIS MORNING:** I called the sign hypothesis "refuted by
construction" after verifying `bundle()` is graded. **I checked the ANCHOR side only -- the QUERY is
signed on 100% of live calls.**
**🎯 `exp_graded_divisive_comparator_v1`: R_LIVE 0.6395 (both signed) vs R_BASE 0.69975 (both
graded), +0.0602, scramble floors 0.4953/0.5065, freq 0.4800, positive control self-retrieval
0.9133. BOTH ARE PURE CONFIGS AND WE RUN NEITHER** -- `GRADED_COMPARATOR` flipped True on 08-14,
AFTER that cell, so we ship **signed-query x graded-anchors, which no cell has ever scored** and
which the code's own docstring calls *"worse than either"*. Measuring now. *(That it is worse than
both is an INFERENCE from docstring + dates + call counts, NOT a measurement.)*

## 🔧 GUI: TWO OWNER-REPORTED DEFECTS, BOTH MEASURED AND FIXED
*"it's hanging a lot"* = `_newest_metrics_mtime()` walking **8,155 dirs in 6.91s ON THE UI THREAD**,
once a minute, from the 1-second tick. Now off-thread: **6,910ms -> 0.0ms**.
*"tabs keep changing slightly with every update"* = `nb.tab(text=...)` on all 8 tabs every second.
Now only when the text changes; sub-minute ages read "just now".
**Diagnostics added** (`data/hook_state/status_gui_diag.jsonl` + `tools/gui_health.py`) because two
earlier freeze reports were closed with "I cannot tell you why". Plus an answered-questions ARCHIVE
and a bigger-reading-pane toggle on the questions tab.

## ⛔🔴 **READ THIS FIRST: A RESULT THAT LOOKED LIKE THE BREAKTHROUGH OF THE EFFORT WAS WITHDRAWN**
## **THE SAME HOUR. NOISE SCORED BETTER THAN IT DID.**
DG pattern separation (`hdlab/dg_pattern_separation.py`, ORGAN_MAP fidelity **SAME**, never before
pointed at word meaning) at sparsity 0.01 took the task from **3.09x the co-occurrence floor to
1.06x** -- apparent parity with word-counting for the first time -- **on 3 seeds, leak 0, arms
asserted non-empty, and the script printed its own pre-committed VERDICT calling it real.**
**IT IS A TIE-BREAKING ARTIFACT.** `k=10` of 1024 makes ~91% of pairs share NO support, so their
similarity is exactly 0.0, and the rank `1 + #{sims > target}` counts every tie as BEATEN.
**Random noise at the same sparsity scores 14.0 where the real arm scored 18.0/15.0. An
all-identical arm scores a PERFECT 1.0.** Harness is fine (query==profile -> 1.0 both conventions).
**AT EVERY NON-ARTIFACT SPARSITY DG IS WORSE THAN OR EQUAL TO RAW -> the post-hoc-transform family
CLOSES.** Refutation: `tools/diag_what_would_a_meaningless_sparse_arm_score.py` (no corpus, seconds).
**🔑 TWO RULES EARNED: (1) NON-ZERO IS NOT NON-DEGENERATE -- assert TIE DENSITY and report BOTH tie
conventions (now in CLAUDE.md). (2) PRE-REGISTRATION DOES NOT DEFEND AGAINST A METRIC THAT CANNOT
FAIL SAFELY -- the branch logic, floors, CIs and leak checks were all sound and it still declared a
breakthrough noise reproduces. Two seeds agreeing did NOT catch it; the artifact is deterministic.**

## 🧠 THE DEEP FIDELITY PASS (owner-directed) -- **13 INTERVENTIONS, 5 POSITIONS, 1 SURVIVING GAP**
Closed for free by READING, before any compute: **the sign hypothesis** (already the shipped state
since 08-14, verified at runtime -- STATUS had carried it as the "leading hypothesis" for the 2x
gap); **decorrelation** (rank-1 removal HARD_FAIL_NO_EFFECT, CI includes 0; full whitening
explicitly PARKED, "do not queue"); **a depression/LTD term** (the delta-rule sweep's nested
positive control shows `eta=1/n` IS the running mean and reproduces SUM exactly -- the sum is the
family's optimum). Also declined a +0.500 islanded HARD_PASS: it protects items above a **K=1200
capacity cliff** and we score 150-450 candidates.
**ENUMERATED rather than searched: 311 replay/consolidation cells, 266 LANDED, 30 non-linear --
and 29 OF 30 NEVER TOUCHED WORD MEANING** (all store/capacity work). *Not "nobody tried it" but
"tried 30 times, always on a different object."* Honest limit: the filter matched nothing on 191.
**🔑 THE ONE SURVIVING GAP, IN ORGAN_MAP'S OWN NUMBERS: our hub carries FREQUENCY at R^2 0.4819 and
a typical sensorimotor dimension at 0.01-0.05 -- ~20x. Every transformation of a bag of word-forms
is still a function of word-form statistics.** That explains why 13 interventions at 5 positions all
returned the same answer. **STATUS: strongest surviving HYPOTHESIS, not a result -- one R^2, one
profile set. Do not harden it into "our code is a frequency detector".**
**➡️ IT POINTS AT SUPPLY, WHICH IS THE OWNER'S OWN Q72 ("patchy" was the load-bearing word).**

## ✅ BOARD Q77 SELF-RESOLVED, AND MY PREMISE WAS THE THING THAT WAS WRONG
I argued `social_iqa` might be unable to show a difference because our arm AND the crude floor both
sat at chance. **Backwards.** On all 1,954 items: LONGEST 0.3557, OVERLAP 0.3449, RAREST 0.3234
against floor 0.3362 and bar 0.3682. **No shallow trick clears it -- the set is built so they
cannot, so a crude method at chance is the instrument WORKING.** Therefore our 0.3501-0.3975 is a
**GENUINE NEGATIVE**. The best-looking old score (0.3975) was on **n=400** not 1,954 (bar 0.4069)
and its run logged **28 of 100 sampled items LEAKING**. **Building a new story test would not have
fixed anything -- we would own two story tests we fail.**

## 🛑 **THE OVERNIGHT LOOP WAS DISARMED (owner instruction 2026-08-20T12:48Z, found UNREAD), THEN**
## **RE-ARMED ON OWNER REQUEST. Dashboard was CLOSED AND REOPENED for the owner -- it is current.**
## 🔴 **AND THE OWNER HAS BEEN READING A THREE-DAY-OLD DASHBOARD -- SEE THE PLAN'S TOP BLOCK.**
Their `status_gui.py` started `2026-08-17 17:50`; Tk loads the file once, so **four landed commits
were invisible, including the two they asked for AGAIN** (loop on/off buttons `072c18b05`; per-tab
data age `d79473ab8`). Explains board Q67 too. **FIXED `faa255cc5`** -- the GUI now shows a
"RUNNING OLD CODE" banner when its own file has changed since import; witness
`verification/test_gui_stale_banner.py`, 4 cases including the one that occurred. **RESTART THE GUI.**

## 🔀 **TWO THRUSTS -- THRUST 1 HAS LANDED. THIS IS THE STATE TO RESUME FROM.**

> ### THRUST 1 -- ✅ **LANDED. TIE. `STRUCT - BAG +3.0`, 95% CI `[+0.0, +7.0]`, NOT SEPARATED.**
> Role-binding buys nothing on this task. Both arms still lose to word-counting by **3.65x-8.33x**.
> **A tie means THIS structural encoding is not the right structure -- NOT that structure is
> irrelevant.** *Confound recorded, not buried: STRUCT skipped 121-132 sentences per seed as
> unparseable, so it ran on LESS EVIDENCE than BAG -- a coverage-matched re-run is the honest
> version and was not done.* **Do not read the per-seed medians as the effect: the median of
> per-probe differences is not the difference of medians.** Full table in the plan.
>
> ### THRUST 2 -- **DESIGN SPECIFIED BY THE OWNER (Q76), AND ITS PREMISE IS PARTLY WRONG.**
> **"We cannot measure narrative-kind learning at all" is TOO STRONG.** `social_iqa` is on the shelf
> (33,410 items, 3-way choice, *what did the character WANT*), selection-not-generation, not
> fact-recall, pre-dating every mechanism here -- **and we already ran it: 10 cells, 2026-08-11, all
> HARD_FAIL, every arm 0.3501-0.3975 against a 0.3362 majority floor, with the word-counting baseline
> at 0.3501 too.** **When the clever method AND the crude floor both sit at chance, the likeliest
> reading is the test is not reaching either -- UNTESTABLE, not negative.**
> **➡️ CHEAP NEXT MOVE (hours): hand that test the answer in a form it cannot miss and check the
> score rises.** Broken -> do not build on it. Works -> we already own a narrative ruler.
> *McGuffey carries exactly ONE labelled moral; `moral` and `fable` return 0 cells. That path is
> closed and the transfer test is genuinely unexplored.*
> *"a high score would be able to summarize what happened in the story and generalize any takeways
> from it"* + *"PPL can take different morals from the same story."*
> **THE SHAPE THE CONSTRAINTS FORCE -- A TRANSFER TEST:** read story A; present story B with the SAME
> principle and **ZERO surface overlap**; pick which of N principles they share.
> - no single gold answer (owner's own words) -> **exact match is invalid**
> - no LLM at inference (standing invariant) -> **selection, never generation**
> - **the can-fail floor is BUILT IN**: word overlap ~0 by construction, so a memoriser MUST fail
> **⚠️ UNSOLVED: where the pairs come from.** Authoring them risks encoding the answer in the
> structure we chose -- the *did-the-test-items-exist-before-the-mechanism* trap. **Search the shelf
> first; fables carry explicit morals.**

## ✅ **[SOLVED 2026-08-20, POST-COMPACTION] THE `data/capability_registry.jsonl` "WHOLE-FILE DIFF"**
## **WAS THE SCHEDULED AUDIT STAMPING `last_audit_utc`. BENIGN. NOT CORRUPTION.**
**832 differing bytes across 208 rows, and every one of them is inside a `last_audit_utc` value:
`"2026-08-20T08:35:45Z"` -> `"2026-08-20T09:15:02Z"`.** The distinct byte substitutions are only
`(51,49) (52,48) (53,50) (56,57)` -- i.e. digits. `hd_capability_registry_audit` re-stamps every row
each run, and an ISO timestamp is FIXED-WIDTH, which is exactly why size (508729), row count (208)
and `id` order were all identical while the content differed.
**➡️ THE LESSON, AND IT IS THE ONE THIS PROJECT ALREADY HAS A RULE FOR: I CHECKED SIZE, ROW COUNT AND
ID ORDER -- THREE PROXIES -- AND CALLED IT "IDENTICAL ON EVERY CHECK I COULD RUN". `cmp` ANSWERED IT
IN ONE COMMAND** (`differ: char 3740`). *An absence claim built from proxies inherits every blind
spot of the proxies; a direct byte comparison has none.* **Do not re-open this. The file is fine, and
the diff is safe to commit or discard.** *The standing rule -- never `git add -A` the registry --
still applies for unrelated reasons.*

**⚠️ SEPARATE AND STILL UNEXPLAINED, FOUND WHILE SOLVING THE ABOVE: the working tree carries ~380
modified files, MOSTLY `data/exp_*/metrics.json` WHOSE ONLY CHANGE IS `ts_iso`** (e.g.
`2026-08-13T16:09:40` -> `2026-08-18T23:35:04`, verdict still `RUNNING`), **plus 7 DELETIONS** (3
`data/cornerstone_results/*/metrics.json`, 3 `notes/_forensics_*`, 1 `prereqs/*.md`). **None of it is
this session's work and none of it has been touched.** *Same class as the registry -- a marker
rewrite, not content loss -- but the DELETIONS are not, and should be characterised before anyone
commits or reverts this tree.*

## 🧭 RESUME HERE -- **REWRITTEN 2026-08-20 (LATEST). BOTH BOARD Qs ANSWERED; NEXT STEP UNSTARTED.**

> ### ➡️ THE ONE UNSTARTED ACTION
> **Turn on `StructuralEncoder` (additive, default-off) and measure context-as-STRUCTURE against
> context-as-BAG-OF-NEARBY-WORDS.** Cleared to run: three-read check returned 1 archive hit / 0
> landed, no ORGAN_MAP prohibition, no registry claim; and the organ WORKS (norms 22-33 vs the bag's
> 32.68, front-end assets present).
> **⚠️ PASS TARGETS AS LEMMAS (`content_lemmas` output), NOT SURFACE FORMS -- a mismatch fails
> SILENTLY as a zero vector, and an all-zero arm scores median rank 1.0, i.e. a fake breakthrough.
> That cost me a wrong claim tonight and one command to catch.**
>
> ### ⚖️ THE DISCRIMINATOR WAS AMENDED BY THE OWNER, DATED, BEFORE ANY ARM WAS SCORED
> *Owner 12:31Z: "You don't approach a textbook like a story... it's not the same kind of learning."*
> **SUPERSEDED:** *structure must help narrative MORE than exposition or it is only a better encoder.*
> **CURRENT:** judge structure on **EXPOSITORY prose**, where our fact-recall task fairly measures
> what the text was there to teach. **Narrative is a separate OBSERVATION, not pass/fail.**
>
> ### 🚨 AND THAT AMENDMENT DEMOTES TONIGHT'S HEADLINE "GAP"
> I reported *textbook grounds 12.6%, Sherlock 0.7%, therefore a fidelity failure.* **Our task is
> FACT RECALL -- expository-kind knowledge.** Scoring what a novel taught with a textbook's metric is
> a METRIC infidelity. **We have NO measure of narrative-kind learning, so that claim is currently
> UNFALSIFIABLE -- do not quote it as a finding.**
>
> ### 📉 CLOSED SINCE THE LAST REWRITE
> - **D7 / successor representation: DO NOT WIRE.** Faithful to its pinned closed form, but on
>   reading order plain 1-step co-occurrence beats it **18.5 vs 45.0** (SR-ONE_STEP **+25.5**, CI
>   [+21.0,+29.0]). SR is pinned for NAVIGATION; mapping it onto text was OUR invention and did not
>   transfer. *(Caveat: ONE text sample with CIs over 408 pairs -- the script says "seeds" and is
>   wrong; only the uniform arm was seeded.)*
> - **Owner Q74 answered: SURPRISE DOES NOT SELECT.** High-, low- and random-surprise halves are
>   indistinguishable at matched count (all +0.0, CI [+0.0,+1.0]); only VOLUME moves it (ALL-NONE
>   **-8.0**, CI [-11.0,-5.0]). **Mean surprise 0.4206-0.4252 against a 0.5 no-information floor --
>   the signal is ~4% from chance, so there was nothing to select on.**
> - **ORGAN_MAP gap list was 2/5 STALE** (D7, H2 labelled MISSING while both exist). Corrected in
>   place; all 39 organ sections re-audited; contradictions now NONE.
>
> ### 🧠 THE FIDELITY AUDIT THE OWNER ASKED FOR: 6 of 8 negatives had one; the 2 gaps are filled
> **And filling one INVERTED it:** "the sum beats any single encounter" is CONSISTENT with pinned
> ORGAN_MAP B1' (*LATL conceptual combination is approximately ADDITIVE*). **The first POSITIVE
> fidelity result of the session, filed for hours as a dead lead.**

## [PREVIOUS REWRITE] **ONE RESULT, FOUR RETRACTIONS, ONE DECISION.**

> ### ✅ THE ONE VERIFIED RESULT -- `keep_noting_grounded` (shipped, ADDITIVE, DEFAULT-OFF)
> **The substrate used to seal a word's representation the instant it grounded: 0 of 60 grounded
> terms gained a single trace over 14,000 further sentences, `cos(profile_16k, profile_2k)` =
> 1.000000.** Two gates enforced it (`Library.flag`'s `return False`, and a terminal short-circuit in
> `process_sentence` that fires BEFORE `is_gap`), and the read-out discarded the fix a third time
> until `profile()` was taught to merge POST-grounding traces only.
> **VETTED: 3 seeds x 2 corpora, paired on identical probes, all separated.**
>
> | corpus | DEFAULT | shipped fix |
> |---|---|---|
> | `simplewiki` (3 seeds) | 4.71x / 5.00x / 5.00x | **2.57x / 3.00x / 3.22x** |
> | `textbook_biology_2e` (3 seeds) | 5.45x / 5.63x / 4.76x | **2.60x / 2.66x / 2.74x** |
>
> Phase slope **+1.410 -> +0.667** per e-fold. Post-only BEAT whole-pile in 3 of 3 (the double-count
> was mildly hurting). **⛔ STILL LOSES TO WORD-COUNTING -- the curve bends, it does not cross.**
> **📋 BOARD Q74 IS THE ONLY OWNER DECISION: make it the default? Not blocking.**
>
> ### ⛔ FOUR THINGS I CLAIMED AND THEN RETRACTED. DO NOT RE-QUOTE THE FIRST VERSIONS.
> 1. *"The `gap_detector` ablation is inert; prior results need re-checking."* **FALSE ALARM,
>    WITHDRAWN.** The organ is CORRECT (positive control: seed-known False 8/8, grounded False 8/8,
>    pending True 8/8). It says "gap" 8,053/8,053 only because two earlier filters remove everything
>    it would reject. **Correct and redundant -- a POSITION result. No audit needed.**
> 2. *"Accumulation is the problem, 4th independent time."* **WITHDRAWN.** That rested on the anchor
>    MARGIN. On the task the sum BEATS any single trace (+13.0, CI [+6.0, +17.5]).
> 3. *"Our code is 4-12x too diffuse, so the projection is the defect."* **OVER-ATTRIBUTED** -- an
>    ordinary text encoder (MiniLM, d_eff 91.6) sits there too, under a different formula.
> 4. *"PBV discarded recoverable signal, so build cross-situational tracking."* **CIRCULAR** (margin
>    IS the grounding criterion). Re-tested properly: pooling scores 0.75-0.80x of a SINGLE encounter,
>    so the mechanism would destroy signal. **DO NOT BUILD IT.**
>
> ### 🧠 THE STANDING LESSON, NOW A RULE IN CLAUDE.md
> **A statistic the mechanism OPTIMISES is not an outcome -- it may DIAGNOSE, never DECIDE.** Anchor
> margin, trace coherence and effective dimensionality each produced a confident mechanistic story
> the held-out task then refused. *Three of tonight's more confident claims died to one question:
> "what does the TASK do under this intervention?"*
>
> ### 📌 THE BIGGEST NEWLY-VISIBLE GAP (not acted on, deliberately)
> **This substrate is an EXPOSITORY-TEXT learner.** Grounding rate at 8,000 sentences:
> textbook **12.6%**, simplewiki 3.6%, Little Women 0.8%, Sherlock **0.7%** -- and it is NOT exposure
> (encounters/item 4.16 vs 3.66). **Children acquire most vocabulary from exactly the narrative
> regime this substrate cannot use.** *The obvious fixes were tested and rejected; this needs fresh
> judgement, not another mechanism hunt at 3am.*

## [PREVIOUS] RESUME BLOCK -- **THE OWNER GAVE TWO DIRECTIONS AND BOTH CHANGED THE PLAN.**
> **1. "adjusting a belief ... integrate where it needs to go" (01:31Z).** Answered: belief revision
> in `hd_fact_store` is REAL and CORRECT and **has never once fired** -- 668 facts, 668 distinct
> (subject, relation) keys, **0 ever contested**. Chasing why found worse: **the fact store holds no
> facts.** Its whole relation vocabulary is `KNOWN_WORD` (380, object always the constant `CORE`) and
> `GROUNDED_MEANING` (288). A constant cannot be contradicted.
> **2. "be brain foundational -- don't wire organs because you think it could help" (02:14Z).** This
> **invalidated my own recommendation.** I had proposed wiring contradiction detection *"because it
> feeds the revision path"* -- a utility argument naming no brain structure. And the machinery under
> it, **AGM contraction, is 1985 formal logic, not neuroscience.** The brain's actual mechanism is
> **RECONSOLIDATION** (retrieval makes a trace labile, then re-stores it -- Nader/Schafe/LeDoux 2000),
> and it returns **0 hits in 8,836 archived cells, 0 in 151 `hdlab` modules, 0 in ORGAN_MAP.**
> *We built the philosopher's version of changing your mind and never the brain's.*
> **⛔ CONSEQUENCE: "go fill the fact store" is DOWNGRADED from next-step to diagnosis** -- the store
> is an addressable symbolic database where cortex has a distributed representation, so enriching it
> is not a brain-foundational goal.
>
> **➡️ CURRENT TOP ITEM, CHOSEN BECAUSE ORGAN_MAP PINS IT:** divisive normalisation over a POPULATION
> POOL (*"graded competition implemented BY the normalisation pool, not a hard argmax"*). We tested
> competition twice and both times WITHIN an item (k-WTA on one trace; per-trace L2). **Smoke says no
> win** -- DIVNORM +1.346 vs SUM +1.161, ties its shuffled-pool control, and does NOT concentrate the
> code (28.5 vs 28.9). **The full sweep decides; the smoke must not be quoted** (I published smoke
> numbers as a finding once today already and had to correct it).
>
> ## 🧭 RESUME HERE AFTER COMPACTION -- written 2026-08-19 at the end of the fidelity-audit session
*Written deliberately short. The five commits named here are the record; this block only says where
to stand. **The LEDGER and `git log` OUTRANK anything I remember.***

**STATE: CLEAN. Nothing is running. Nothing is half-done. No orphaned processes, no uncommitted work
of mine.** HEAD is `c6710d753`. The last five commits are the whole of this session's output:

    c6710d753  correct a smoke-numbers finding, answer Q72 with CIs
    3cf399a6e  two archive-found caveats on claims committed earlier today
    e027ccd11  complete the brain-fidelity audit on all three open negatives
    0b987588d  record held-out leak fault and archive-mining finding
    ea62d96a2  fidelity audit on the biggest negative + the honest accounting

**WHAT WAS FINISHED.** The owner asked that every negative get a brain-fidelity check. All three
that had none now have one. **Three of my four explanations were REFUTED by their own pre-committed
controls** -- see the audit block further down. The one surviving account: *a write gate chooses
WHICH counts get added and cannot change that the code IS a count.*

**⛔ THREE CORRECTIONS LIVE IN THIS FILE. DO NOT RE-QUOTE THE SUPERSEDED VERSIONS:**
1. **"Four of four refuted" is WRONG -- it is THREE of four.** The familiarity hypothesis was NOT
   refuted; I had read SMOKE numbers (161 terms). At full n (1,590) the slope separates negative:
   mean -0.0035, CI [-0.0052, -0.0018], 63% of words.
2. **Never quote "spreading reading across corpora made it worse."** Point estimates 91.0 -> 106.5
   look like a negative; the difference is **+15.8, 95% CI [-10.0, +42.5], NOT separated.** Passive
   breadth is **UNTESTED at this n**, not a negative.
3. **"Our code is 4-12x too diffuse" is OVER-ATTRIBUTED.** A prior cell measured MiniLM -- an
   ordinary working text encoder -- at d_eff 91.6, using a **different formula** for participation
   ratio than today's diagnostic. The geometry stands; blaming OUR design does not, yet.
   **⤷ RESOLVED, AND THE CORRECTION ITSELF NEEDED CORRECTING -- SEE THE BLOCK BELOW. The invalid
   comparison was real (formula AND population both differed), but "probably normal for text" was
   NOT supported: measured on the same formula we are 2.60x MiniLM, and on a fully matched
   comparison we are MORE diffuse than the raw counts we are built from.**

**➡️ NEXT STEPS, IN THIS ORDER, AND THE FIRST ONE RESOLVES CORRECTION 3:**
1. **Recompute our participation ratio under BOTH formulas** -- `(sum s)^2/sum s^2` over singular
   values (the prior cell's) and `1/sum(v^2)` over variance shares (today's) -- on our profiles AND
   on a text-encoder reference, so the MiniLM comparison becomes legitimate. Until then we cannot
   say whether we are unusual or merely normal-for-text.
2. **Test the gap-targeted growth loop on the current substrate.** It is the only thing in this area
   with a clean prior win (`exp_breadth_foundation_active_growth_loop_ud_ewt_v1`, HARD_PASS,
   coverage 0.50 -> 0.79, real-vs-shuffle AUC 0.8924 vs 0.5122) **and it is the owner's own idea**
   -- the load-bearing half of Q72 is "patchy", not "another textbook".
3. **Leave the write gate alone.** Four explanations tested; tuning thresholds cannot reach it.

**🔁 THE HABIT THAT PAID OFF MOST AND SHOULD CARRY FORWARD: query the RESULTS archive before
building, not just the code registry.** `python tools/experiment_index.py query "<kw>"` -- it found
that today's write-gate negative had been measured a month earlier, that a prior residual gate
already recorded skip=0.00, and both of the corrections above. **`substrate_query.sh` returns zero
bytes and exits 0 -- never use it.**

## 📖 WHERE WE ARE, IN PLAIN WORDS -- added 2026-08-19 because everything below this is jargon
*The owner answered two board questions with "too jargony so I don't really know how to help".
That was about the board, but this file has the same problem and the owner reads it. Everything
below is unchanged; this block is the translation. **If the two disagree, the blocks below are the
record and this one is the summary.***

**THE GOAL.** Get a system to learn what words mean by reading, with no language model doing the
understanding -- every step has to be inspectable.

**WHERE IT ACTUALLY IS.** It reads text, decides which words it does not know, and writes down what
it learns so each fact can be traced back to the sentence it came from. That part works. **What it
cannot yet do is use what it learned to answer a question better than a crude word counter can.**

**THE ONE THING TO UNDERSTAND ABOUT TODAY.** Give the system a sentence it has never seen and ask
which word belongs in it. A crude method -- just counting which words tend to appear near each
other -- narrows it to about the top 15 out of 450 candidates. **Our system gets to about 70-80.**
Today I tried three different clever ways to close that gap. All three lost. *Three different
clever ideas losing to the crude one usually means the problem is not the thinking -- it is what
went in.*

**THE MOST USEFUL THING FOUND TODAY, and it is a plumbing problem, not a clever one.** The system
stops taking notes on a word once it decides it knows that word -- like a student who stops writing
things down the moment a topic feels familiar. So the words it meets constantly have the fewest
notes: for the word "century" it wrote 7 notes across 92 sightings. **Roughly 3 of every 10
encounters are never recorded, and that alone costs more than all three clever ideas were trying
to win.**

**WHAT IS ON THE OWNER'S DESK.** Two questions, in plain language, on the board: should it keep
taking notes after it thinks it knows a word, and should we change what we feed it rather than how
it thinks.

**HOW MUCH OF TODAY WAS ME CORRECTING MYSELF: a lot, and deliberately so.** Several numbers I
published were wrong and were caught by controls -- a comparison built on text the system had never
read, a measurement inflated by comparing something to a copy of itself, and a claim that our
storage "destroys information" which turned out to be mostly "never wrote it down". *Each is
corrected at the original text below, not just above it.*


# â±ï¸âž¡ï¸ 2026-08-19 -- THE PLAN IS `notes/BUILD_PLAN_post_audit_2026-08-19.md`. OPEN IT. IT IS CURRENT.
**The autoloop is ARMED at 200 and is executing that plan. It is rewritten every continuation and
carries every number below with its controls. THIS BLOCK IS A POINTER, NOT THE RECORD.**
*Stop the loop with `python tools/autoloop.py disarm`.*

## 🔴 2026-08-19 -- **THE POSITIVE CONTROL FAILED AND IT CONDEMNS MY EARLIER PROBE: THE BASELINE**
## **AND OUR ARM WERE BUILT ON DIFFERENT TEXT. THE "2x GAP" AS STATED IS CONFOUNDED.**
`scratch/diag_does_coverage_explain_the_gap.py` was built to separate coverage from quality. Its
first output was the control, and the control did not hold: **`PROJ_COOC_ALL` reads median 17.0
where the earlier probe measured 42.0 for the same arm.**
**⛔ CAUSE, AND IT IS A REAL DEFECT IN THE EARLIER PROBE: it built the counter from
`read_split = pool[:N_READ]` -- MY slice of the corpus handle -- while our profiles are built from
`sub.state.sentence_pool`, THE SENTENCES THE FORAGER ACTUALLY CHOSE. Those are different sentence
sets. The baseline was scored on text the substrate had partly never read.** *So the earlier
"compression costs 20 -> 42, ours costs 20 -> 81" decomposition is void. Same class as the
corpus-arithmetic bug from earlier today: I assumed a slice was what the substrate consumed.*

**✅ ON MATCHED TEXT -- both arms from the substrate's OWN pool -- the decomposition is cleaner and
says something different:**

| arm (256 dims, same items, same candidates) | hit@10 | hit@50 | **median** |
|---|---|---|---|
| **PROJ_COOC_ALL** (every occurrence) | 0.4247 | 0.7057 | **17.0** |
| **PROJ_COOC_TRACED** (only what we recorded, 68.8%) | 0.3211 | 0.5251 | **46.0** |
| **OURS** | 0.1304 | 0.3779 | **81.0** |

**➡️ COVERAGE IS THE DOMINANT COST, NOT A SIDE ISSUE: 17 -> 46 from recording only 68.8% of
occurrences. The remaining 46 -> 81 is real but SMALLER than the coverage penalty.**
*Both factors survive; their sizes have swapped. What I first called "we destroy information" is
the minority term, and "we never wrote it down" is the majority one.*
**🎯 THIS SHARPENS BOARD Q69 CONSIDERABLY: "keep recording traces after a word grounds" is now the
single largest measured lever on this representation, worth more than everything the three closed
mechanism lines were chasing.** *Still an owner call -- it changes core reading behaviour and its
cost profile -- but it is no longer a tidy-up, it is the main event.*

## 🟠 [ITS "31% NEVER RECORDED" STANDS; ITS SIZE-ORDERING IS SUPERSEDED ABOVE] 2026-08-19 -- **PARTIAL CORRECTION TO THE BLOCK BELOW, AND MY VERDICT STATISTIC WAS WRONG.**
## **WE RECORD ONLY 69% OF OCCURRENCES, AND THE SHORTFALL IS CONCENTRATED ON FREQUENT WORDS.**
I published "our representation is DESTROYING information a random matrix preserves". Reading the
code then showed `context_vector(graded=True)` returns the RAW SUM of per-word bipolar draws --
**a LINEAR random projection.** By linearity, summing a term's per-sentence vectors should EQUAL
projecting its summed counts, so OURS and PROJ_COOC should be the same object and there is nothing
for a "quality" difference to live in. Unless they are built from different OCCURRENCES. Measured:

| traces recorded vs sentences containing the term | |
|---|---|
| median ratio | **0.958** |
| mean ratio | 0.802 |
| **OVERALL (total traces / total occurrences)** | **0.688** |
| least covered | `century` 7/92 = 0.076, `european` 5/44, `ways` 5/41, `unite` 7/50 |

**⛔ THE SHORTFALL IS SYSTEMATIC AND FREQUENCY-DEPENDENT: rare terms are covered almost completely,
FREQUENT terms are covered barely at all.** *That is the loop working as designed -- a word stops
being a gap once it grounds, so it stops accruing traces -- but the consequence is that **the terms
with the MOST evidence available have the LEAST recorded**, which is exactly backwards for
estimating a profile.*
**⚠️ AND MY PRE-REGISTERED VERDICT STATISTIC WAS THE WRONG ONE. I gated on the MEDIAN ratio (0.958,
"coverage is not the story"), when the quantity that matters is the FREQUENCY-WEIGHTED TOTAL
(0.688) and its CORRELATION WITH FREQUENCY. The median hides a systematic truncation by
construction.** *Third time this session a threshold I wrote was badly specified. The pattern is
always the same: I pick a statistic that is easy to compute rather than the one that answers the
question.*
**➡️ SO BOTH MECHANISMS ARE LIVE AND NEITHER IS CLEAN: ~31% of occurrences were never recorded
(concentrated where it hurts most), AND that alone may not account for a 2x median-rank gap. The
"destroys information" claim below is NOT refuted but is NO LONGER THE SOLE EXPLANATION and must
not be quoted as one.** *The clean next test: rebuild PROJ_COOC from ONLY the recorded traces. If
it then matches OURS, coverage explains everything.*

## 🔴🔴🔴 [SEE THE PARTIAL CORRECTION ABOVE -- COVERAGE IS ALSO IN PLAY] 2026-08-19 -- **A RANDOM PROJECTION OF THE CO-OCCURRENCE COUNTS BEATS OUR REPRESENTATION**
## **BY 2x AT IDENTICAL DIMENSIONALITY. WE LOSE MORE THAN COMPRESSION EXPLAINS.**
`scratch/diag_is_our_vector_a_compressed_counter.py`. The question the whole session pointed at and
nobody had asked: both sides use co-occurrence, so **is our representation simply a LOSSY VERSION
of the baseline that keeps beating it?** Matched dimensionality, one variable.

| arm | hit@1 | hit@10 | hit@50 | **median rank** |
|---|---|---|---|---|
| **FULL_COOC** (6,145 dims) | 0.1137 | 0.3478 | 0.7124 | **20.0** |
| **PROJ_COOC@256** (same counts, RANDOM projection) | 0.0803 | 0.2475 | 0.5619 | **42.0** |
| **OURS** (accumulated context vectors, 256 dims) | 0.0569 | 0.1304 | 0.3779 | **81.0** |

*POSITIVE CONTROL: FULL_COOC median 20.0, against the 15-20 two other cells measured. Same thing
being scored.*
**⛔ THE PRE-REGISTERED THIRD BRANCH FIRES, AND IT WAS THE ONE I THOUGHT LEAST LIKELY. Compression
to 256 dims costs 20 -> 42. OUR representation at the SAME 256 dims costs 20 -> 81. So HALF THE
GAP IS DIMENSIONAL AND HALF IS OURS: a RANDOM PROJECTION of the same counts beats a carefully
accumulated context representation by 2x on median rank.**
**➡️ THIS IS THE FIRST SPECIFIC, FIXABLE DEFECT THE SESSION HAS FOUND IN THE REPRESENTATION,
rather than another ceiling.** Everything until now said "the representation is the limit"; this
says **the representation is DESTROYING information that a random matrix preserves**, which is a
much stronger and much more actionable claim.
**🧠 AND IT GIVES QUANTITATIVE WEIGHT TO AN EXISTING QUALITATIVE FINDING: `notes/ORGAN_MAP.md` §1
already records 34 `np.sign` call sites across 12 modules and calls the result "mathematically a
PROTOTYPE EXTRACTOR -- the signature of a degrading ATL hub". A sign-quantised accumulation would
lose exactly what a linear random projection keeps.** *That is now the leading hypothesis for the
2x and it is directly testable: rebuild the profile WITHOUT the sign step and re-measure.*
**⚠️ SCOPE: one seed, one corpus, 4,300 sentences, 223 candidates, held-out only. The direction is
large but this is a single measurement and the sign hypothesis is UNTESTED.**

## ⛔ 2026-08-19 -- **WRITE-GATE CELL LANDED, 3 SEEDS. FORMAL VERDICT: (C) AND (D) BOTH FIRE.**
## **READING (A) IN 0 OF 54 CELLS. FLOOR CLEARED IN 0 OF 54.**
`exp_predictive_write_gate_v1`, 1,064 s, 3 seeds x 6 thresholds x 3 k = 54 cells, read by a script
written BEFORE the result existed (`scratch/read_write_gate_result.py`).

| seed 7 | hit@10 | hit@50 | median | skip |
|---|---|---|---|---|
| ACCUMULATE | 0.1533 | 0.3433 | 115.5 | 0% |
| GATED@0.25 | 0.1533 | 0.3533 | 116.0 | 4.7% |
| GATED@0.40 | 0.1600 | 0.3300 | 113.5 | 26.9% |
| GATED@0.50 | 0.0833 | 0.2867 | 138.5 | 72.6% |
| GATED@0.60 | 0.0800 | 0.1733 | 222.5 | 92.1% |
| **COOC_floor** | **0.3667** | **0.7233** | **20.5** | -- |

**THE SHAPE IS THE ARGUMENT: at low thresholds the gate barely skips and MATCHES accumulation; as
it skips more it MONOTONICALLY DEGRADES. There is no window where selectivity helps.** *At 0.60,
GATED and RANDOM_SKIP are IDENTICAL to four decimals on every metric -- at that skip rate the two
selectors have nothing left to disagree about.*
**➡️ AND THE TWO NEGATIVES SAY DIFFERENT THINGS, WHICH IS WHY BOTH ARE REPORTED:**
**(C)** the pinned residual rule does not help AS WIRED HERE -- a real negative about this wiring.
**(D)** no arm clears the floor at any threshold or k, so the representation is not competitive
*regardless* of what happens between the arms.
**✅ THE PINNED EQUATION IS NOT REFUTED, AND THE DISTINCTION IS LOAD-BEARING.** Measured the same
day: profiles DO predict their own contexts 10.4% better than an unrelated term's, CI-separated.
**So the residual is real but too UNIFORM to threshold (sd 0.076 about a mean 0.44). Predictive
coding needs a predictor sharp enough that being wrong is INFORMATIVE. Ours is evenly mediocre, so
its errors carry no ranking.** *That is a statement about our predictor, not about the brain's rule.*

## ⚠️ 2026-08-19 -- **CORRECTION TO MY OWN INTERPRETATION ONE BLOCK BELOW: THE PROFILES DO**
## **PREDICT. WEAKLY, BUT REALLY -- 10.4%, CI-SEPARATED, ON 73% OF OBSERVATIONS.**
I wrote that the write-gate negative was explained by "the profile predicts nothing in particular".
**That was an interpretation, not a measurement, and turning it into one refutes it.**
`scratch/diag_does_a_profile_predict_its_own_contexts.py`, 16,930 PAIRED observations, 1,753 terms.

| residual magnitude (LOWER = better prediction) | mean | median | sd |
|---|---|---|---|
| **OWN** (leave-one-out profile) | **0.4375** | 0.4522 | 0.0759 |
| OTHER (a random other term's profile) | 0.4884 | 0.4904 | 0.0378 |
| **paired difference** | **+0.0510** | +0.0384 | CI **[+0.0498, +0.0522]** |

**A term's profile predicts its own next context 10.4% better than an unrelated term's does, on
73.2% of observations, with the CI nowhere near zero.** *Leave-one-out throughout, so OWN is never
a self-match -- that discipline exists because this session already found a 34% self-match
inflation in a number I published.*
**➡️ SO THE CHAIN IS NARROWER AND MORE HONEST THAN I SAID: the profiles DO carry term-specific
predictive content (10.4%); that content is TOO WEAK AND TOO UNIFORM to threshold (sd 0.076 about
a mean of 0.44); so a residual gate lands where a coin does. The failure is in the SELECTOR'S
RESOLUTION, not in the representation being empty.**
**⛔ AND THAT MATTERS FOR WHAT COMES NEXT: "the representation predicts nothing" would have closed
the representation line entirely. "It predicts 10.4% and that is too little to act on" points
somewhere specific -- the question becomes what would make the prediction SHARPER, not whether
prediction exists at all.** *Second time this session I overstated a negative and the measurement
walked it back. Both times the overstatement was mine and in the pessimistic direction.*

## 🔴 2026-08-19 -- [SEE THE CORRECTION ABOVE: "predicts nothing in particular" IS REFUTED] **THE RESIDUAL GATE HURTS, AND IS INDISTINGUISHABLE FROM RANDOM SKIPPING.**
## **READINGS (C) AND (D) BOTH FIRE. 2 of 3 seeds banked; the picture is not close.**
`exp_predictive_write_gate_v1`. **ACCUMULATE -- keeping everything, what the substrate does today
-- is the BEST of our arms at every k on both seeds.**

| seed 20260819 | hit@1 | hit@10 | hit@50 | median |
|---|---|---|---|---|
| **ACCUMULATE** | 0.0567 | **0.1800** | **0.3433** | **126** |
| GATED@0.45 | 0.0300 | 0.1767 | 0.2933 | 120.5 |
| RANDOM_SKIP@0.45 | 0.0300 | 0.1267 | 0.2967 | 132.5 |
| GATED@0.50 | 0.0200 | 0.0800 | 0.2733 | 133.5 |
| RANDOM_SKIP@0.50 | 0.0400 | 0.0900 | 0.2800 | 135.0 |
| **COOC_floor** | **0.0867** | **0.4067** | **0.7533** | **15** |

**⛔ READING (C): GATED never beats ACCUMULATE -- it LOSES at every threshold on both seeds.**
**⛔ READING (D): nothing comes near the floor (0.3433 vs 0.7533).**
**🎯 AND THE RATE-MATCHED ARM EARNS ITS PLACE: GATED ~= RANDOM_SKIP throughout, and RANDOM is
SLIGHTLY AHEAD at 2 of 3 thresholds on seed 20260819 (0.2967 vs 0.2933; 0.2800 vs 0.2733).** *So
the residual gate is not selecting informatively -- it is just discarding data, and discarding it
no better than a coin would. Without that arm this would have read as "predictive coding hurts";
with it, the honest statement is "the residual carries no usable selection signal here".*
**✅ THE PRE-BUILD PROBE PREDICTED EXACTLY THIS AND IS WHY THE ARM WAS THERE.** Residuals measured
near-constant (p10 0.3575, median 0.4648, p90 0.5237) -> a near-constant selector is a random
selector. **The probe cost minutes and made the negative interpretable instead of merely
disappointing.**
*Also: the "cliff" I described was an artifact of a coarse grid. The fine sweep is smooth --
skip rates 0.057 / 0.279 / 0.482 / 0.721 / 0.884 / 0.912 across thresholds 0.25-0.60. Sweeping
finely is what showed that; adopting 0.50 would have hidden it.*
**➡️ MORE DATA BEATS SELECTIVELY LESS DATA HERE, WHICH IS ITSELF THE FINDING: with a selector that
carries no information, accumulation is the right rule. The pinned equation does not fail -- OUR
RESIDUAL DOES, because the profile it is measured against predicts nothing in particular.**

## 🧠 2026-08-19 -- **BRAIN-FIDELITY AUDIT ON THE SUBSUMPTION NEGATIVE, AND FIRST THE HONEST**
## **ACCOUNTING: OF SIX NEGATIVES TODAY, ONE GOT A FIDELITY CHECK, TWO PARTIAL, THREE NONE.**
*Owner: "I want to make sure that you're properly drilling all negative findings and doing a brain
fidelity check." Audited rather than claimed. **Full: the cortical read (CLS position inversion).
Partial: the residual gate, the random-projection gap. NONE: the SUBSUMPTION result, the 9-seed
spoke failure, the reading-(C) void.** The biggest negative of the day had no fidelity audit at
all -- it was reported as a number and a consequence. This is that audit.*

**IT IS CHECKABLE AGAINST A PINNED QUANTITY, which is rare here.** ORGAN_MAP B4 is one of the twelve
organs whose equation is actually pinned: *"dense, graded, ~4-12 effective dims; IT sparseness
index ~0.2-0.3"* (Huth 2012, first ~4 group PCs define the shared semantic space).

| | effective dims (participation ratio) | components for 90% var | top-4 share |
|---|---|---|---|
| **brain, PINNED** | **~4-12** | -- | first ~4 define the space |
| **OUR PROFILES** | **50.4** | 92 | 0.201 |
| pure noise, same shape | 119.1 | 122 | 0.063 |

**✅ OUR CODE IS REAL STRUCTURE, NOT NOISE: 50.4 against noise's 119.1, and the first four
components hold 20.1% against noise's 6.3%. That much is a genuine positive and I had not measured
it before.**
**⛔ BUT IT IS 4-12x TOO HIGH-DIMENSIONAL AGAINST THE PINNED FIGURE, AND THAT EXPLAINS THE
SUBSUMPTION RESULT MECHANISTICALLY RATHER THAN JUST REPORTING IT: a LINEAR projection PRESERVES
THE RANK of what it projects. It cannot concentrate variance the way a LEARNED code does. So our
"hub" is a compressed COUNT VECTOR, and a compressed count vector cannot beat the counter it
compresses.** *That is why three mechanisms all lost to counting: they were all reading a lossy
copy of the counter.*
**⚠️ THE COMMENSURABILITY CAVEAT, STATED BEFORE ANYONE QUOTES THE COMPARISON: participation ratio
over 223 word profiles and Huth's "~4 group PCs" over voxel-wise encoding across subjects are NOT
the same measurement. The ORDER OF MAGNITUDE gap is the finding; the exact ratio is not.**
**⚠️⚠️ AND A SECOND CAVEAT FOUND AFTERWARDS BY QUERYING THE ARCHIVE I SHOULD HAVE QUERIED FIRST --
IT WEAKENS THE CLAIM ABOVE AND IS RECORDED WHERE THE CLAIM IS, NOT IN A FOOTNOTE:**
- **THE TWO CELLS USE DIFFERENT FORMULAS FOR THE SAME WORD.** `exp_effective_rank_svd_v1`
  (HARD_PASS) defines participation ratio as **(sum s)^2 / sum s^2 over SINGULAR VALUES**; today's
  diagnostic used **1 / sum(v^2) over normalised VARIANCE shares**. Those are different statistics
  and generally give different numbers. **50.4 and any number in that cell must not be put side by
  side until one of them is recomputed.**
- **AND ITS NUMBER MAKES THE "WE ARE UNUSUALLY DIFFUSE" READING LOOK PREMATURE:** that cell measured
  **MiniLM -- a normal, working sentence encoder -- at d_eff 91.6, rank90 175, rank99 296**, and
  landed HARD_PASS for being *intrinsic-dim-limited at d_eff <= 120*. If a competent text encoder
  also sits far above the brain's ~4-12, then **being 4-12x too diffuse may be a property of
  LEARNING-FROM-TEXT rather than a defect specific to OUR code**, and the subsumption explanation
  above is over-attributed. *The geometry finding stands; the blame does not, until both numbers are
  computed the same way on both objects.*
**➡️ AND IT AGREES WITH THE OWNER'S OWN DIAGNOSIS FROM A DIFFERENT DIRECTION: a code that only
ACCUMULATES cannot concentrate. Concentration is what LEARNING buys. Same conclusion as the
novelty work -- prediction first -- reached through geometry instead of through surprise.**

## 🧠✅ 2026-08-19 LATER -- **THE FIDELITY AUDIT IS NOW COMPLETE: ALL THREE GAPS FILLED, AND**
## **THREE OF MY FOUR EXPLANATIONS WERE REFUTED BY THEIR OWN PRE-COMMITTED CONTROLS.**
*The accounting above said: NONE for the subsumption result, the 9-seed spoke failure, the
reading-(C) void. All three now have one. **Every diagnostic was written with a pre-committed
alternative reading, and in three cases out of four the ALTERNATIVE is what fired.** That is the
system working, and it is worth more than three confirmations would have been.*
*(Header corrected from "four of four". The familiarity hypothesis was NOT refuted -- I had read
smoke numbers. See item 3 below, which is left standing as the correction rather than edited away.)*

**GAP 2 -- THE 9-SEED SPOKE FAILURE.** Hypothesis: hub-and-spoke POSITION. In the brain the
sensorimotor spokes are INPUTS that shape the hub over experience; ours is a supplied Lancaster
table consulted AFTER the hub has ranked. Prediction: the hub carries no sensorimotor structure.
**REFUTED.** Ridge read-out of the grounded dimensions from the 256-dim profile, 5,950 covered
words, 5-fold out-of-fold R^2, gated at max(0, shuffled-null p95):

| | R^2 |
|---|---|
| log corpus frequency (positive control) | **0.4819** |
| best sensorimotor dim (Gustatory) | 0.1145 |
| typical sensorimotor dim | **0.01 - 0.05** |
| Head | -0.0086 (no better than the mean) |

11 of 12 dimensions ARE carried, so the hub is **not** sensorimotor-blind and position is not the
explanation. **But the magnitude is the real story: the hub carries frequency ~20x more strongly
than a typical sensorimotor dimension.** Not blind -- overwhelmingly a frequency code.
*⚠️ A THRESHOLD BUG CAUGHT MID-RUN, LOGGED BECAUSE IT NEARLY PUBLISHED A FALSE POSITIVE: the first
gate was "above the shuffled null", and the shuffled null sits at **-0.12** because a 256-dim ridge
on shuffled targets OVERFITS. Under that gate 12 of 12 dims "passed" while every R^2 was NEGATIVE --
worse than predicting the mean. **The bar is max(0, null p95); the ZERO is the binding half.***

**GAP 3 -- THE READING-(C) VOID (the residual write gate did nothing).** Four explanations tested,
four dead:
1. *"It was thresholding noise."* The residual's median 0.4648 sits at the 0.5 that two UNRELATED
   vectors produce, so this looked certain. **REFUTED, n=55,399:** matched 0.4546 vs mismatched
   0.4888 vs chance 0.5001, difference CI [-0.0348, -0.0336]. The prediction carries real
   term-specific information.
2. *"Between-word variation swamped the encounter signal, so a global absolute threshold could only
   sort vocabulary."* **REFUTED:** ICC = **0.201**. Within-word variation is **80%** of the total.
   The absolute rule had exactly the encounter-level variation it needed.
3. *"It is a familiarity detector, not a novelty detector"* (the owner's Q71 distinction).
   **NOT REFUTED -- AND THIS ENTRY IS A CORRECTION OF WHAT I FIRST WROTE HERE.** I published the
   SMOKE numbers (161 terms: slope +0.0103, median -0.0046, 55% negative) as the finding and called
   it refuted. **At full n (1,590 terms) the sign flips and separates: mean slope -0.0035, median
   -0.0061, 63% of words negative, 95% CI [-0.0052, -0.0018].** The residual DOES fall as a word
   becomes familiar. *My own rule -- a smoke with smaller numbers does not test the full run -- and
   I broke it inside the very audit that was checking my rigour.*
   **A detrended encounter-level signal also survives (r = +0.733), BUT I AM NOT LEANING ON THAT
   NUMBER:** the residual is a distance to the word's own profile and "how unusual this use is" is a
   leave-one-out distance to the word's other contexts. **Those are nearly the same computation, and
   the positive control (+0.802) shows the construction correlates by itself.** So (2) mostly
   confirms the arithmetic, not a discovery. *A per-word DETRENDED gate is a real lead; it is not
   yet evidence.*
4. *"The missing PRECISION term is the divergence."* `precision` appears **nowhere** in
   `hdlab/predictive_coding.py` -- enumerated, 15 public names, not one mentions precision, variance,
   confidence or weighting, and `threshold_gate` takes exactly one knob. **But the archive already
   tested the precision-weighted form and it ALSO sat at chance** (Friston arm 0.530 vs flat 0.542).

**🔑 SO THE ACCOUNT THAT SURVIVES IS NOT ABOUT THE SIGNAL AT ALL -- IT IS ABOUT THE ACTION.** The
gate's signal is fine by every test we can put to it. What a write gate can do is choose WHICH
counts get added. **It cannot change that the representation IS a count.** Selectivity inside an
accumulate-only store is a no-op on the KIND of code produced -- which is the same conclusion the
effective-dimensionality measurement reached from geometry, and the same one the subsumption result
reached from ranking. *The fix is a NON-ADDITIVE write, not a better gate. Tuning thresholds cannot
reach it.*
## 🧱 2026-08-20 -- **THE UPDATE RULE CHANGES NOTHING EITHER. THE SUM IS OPTIMAL IN ITS OWN**
## **FAMILY, AND THE PRE-REGISTERED RISK IS EXACTLY WHAT HAPPENED.**
*The three POSITION errors all pointed here: precision belongs on HOW MUCH TO UPDATE, and `acc +=
trace` has no step size to modulate. So the profile was given a delta rule `p <- p + eta*(trace - p)`
-- which has both a residual and a step size, the form G2 actually pins. All arms at full coverage.*

| sentences | SUM | **1/n (control)** | eta .05 | eta .20 | eta .50 | **PREC** |
|---|---|---|---|---|---|---|
| 1000 | 0.98x | 0.98x | 0.84x | 1.07x | 1.16x | 0.93x |
| 2000 | 1.71x | 1.71x | 1.57x | 1.86x | 2.14x | 1.50x |
| 4000 | 2.23x | 2.23x | 2.42x | 2.90x | 3.42x | 2.44x |
| 8000 | 2.06x | 2.06x | 1.89x | 2.92x | 4.24x | 1.90x |
| 16000 | **4.39x** | 4.39x | 6.92x | 8.69x | 10.08x | 6.06x |

    phase slope  SUM +1.035 | 1/n +1.035 | .05 +1.798 | .20 +2.354 | .50 +2.879 | PREC +1.536
    beats SUM at:  1/n 0/5   .05 3/5   .20 0/5   .50 0/5   PREC 3/5

**✅ THE NESTED POSITIVE CONTROL PASSED AT EVERY POINT: `eta = 1/n` IS the running mean, and it
reproduced SUM's ranking EXACTLY (delta +0.00 at all five reads).** *That is what makes the rest of
the table interpretable rather than decorative -- the sum is not a separate arm, it is a POINT
INSIDE the delta-rule family, so "no arm beats the sum" means the family's optimum sits at the
no-forgetting end.*
**⛔ EVERY FIXED LEARNING RATE IS WORSE THAN THE SUM, AND WORSE FASTER: slopes +1.798 / +2.354 /
+2.879 against +1.035, and at 16,000 the recency arms blow out to 6.92-10.08x against the sum's
4.39x.** Precision on the step size does not rescue it (+1.536, 3/5).
**➡️ AND THE RISK WAS WRITTEN DOWN BEFORE THE RUN, VERBATIM: *"if the eta sweep says
smaller-is-always-better, the winner IS the sum and this is a NULL. Say so plainly."* It does, it is,
and I am.**
**🔑🔑 SO THE REPRESENTATION IS INSENSITIVE TO **HOW** IT IS WRITTEN AS WELL AS TO **WHICH** TRACES
GO IN.** Six write-side interventions have now failed on the phase curve (residual gate, k-WTA,
normalisation, incremental decorrelation, novelty/precision selection, and now the whole delta-rule
family). **The only two things that have EVER moved it are HOW MANY traces exist (coverage) and a
POST-HOC transform (centring) -- neither of which is a rule about writing.** *The limit is the
REPRESENTATION -- a random projection of counts -- not the procedure that fills it.*
**🧠 FIDELITY, AND IT NAMES THE ONE HONEST ESCAPE FOR THE DELTA RULE: the brain DOES forget, and
recency weighting is real synaptic behaviour. But forgetting BUYS adaptation to a CHANGING world,
and `simplewiki` read front-to-back is STATIONARY -- there is nothing to adapt to, so tracking can
only discard evidence.** *We tested a rule for non-stationarity on a stationary corpus, which is a
fourth POSITION error of the same shape: right mechanism, wrong regime.* **That is testable: on a
deliberately NON-STATIONARY reading order (topic-blocked, so word senses drift), recency should beat
accumulation. If it does not even there, the delta rule is dead on this instrument outright.**
*⚠️ Single seed per point, one corpus. Per-point deltas reported before slopes.*

## 🎚️ 2026-08-20 -- **PRECISION WEIGHTING, THE PINNED TERM, BUILT TO THE ARCHIVE'S OWN CONSTRAINT.**
## **MEASURABLE, WELL-BEHAVED -- AND STILL NOT A USABLE GATE. FOURTH NEGATIVE ON SELECTION.**
*ORGAN_MAP G2 pins the rule as the residual PRECISION-WEIGHTED, and enumeration found the term
absent from the module. Three lines pointed here. Precision = bias-corrected resultant length of the
term's contexts, computed from the PREFIX ONLY so an occurrence never contributes to its own weight.*

| sentences | AS_IS | **PREC_50** | NOVEL_50 | RANDOM_50 | FULL |
|---|---|---|---|---|---|
| 1000 | 1.20x | **0.84x** | 1.09x | 1.11x | 0.98x |
| 2000 | 2.29x | 1.86x | 1.57x | 1.79x | 1.71x |
| 4000 | 3.12x | 2.58x | 2.92x | 2.56x | 2.23x |
| 8000 | 3.69x | 3.02x | 2.53x | 2.39x | 2.06x |
| 16000 | 6.42x | **4.75x** | 6.64x | 5.44x | 4.39x |

    phase slope   AS_IS +1.708   PREC +1.294   NOVEL +1.740   RANDOM +1.337   FULL +1.035
    PREC beats RANDOM at 2/5 points, beats NOVEL at 3/5 -- a coin flip, deltas swing -0.69 to +0.63

**✅ THE DESIGN CAME FROM THE ARCHIVE, NOT FROM ME, AND THAT MATTERS.** A four-cell arc exists:
`..._reliability_gate_v1` HARD_PASS **but DOWNGRADED on adversarial VET -- its confidence was
INJECTED**; `..._derived_v1` HARD_FAIL_INERT_OR_HARMFUL with a strong same-item signal
(auc **0.8303**) that **still gave a gate delta of -0.0280**; `..._independent_channel_v1` HARD_PASS
**because it was LEAVE-ONE-ITEM-OUT**; `..._correlated_error_v1` HARD_FAIL, fooled **below chance
(auc 0.3198)** by systematic errors. *Reading that arc first is why precision here is prefix-only --
building it without leave-one-out would have reproduced a known failure exactly.*
**⛔ AND IT LANDED IN THE SAME PLACE THE DERIVED CELL DID: MEASURABLE BUT NOT USABLE.** The statistic
is real and its self-test is clean (consistent contexts 0.989, scattered 0.167, single observation
0.000). Weighting the residual by it does not make selection work.
**🔑🔑 AND THIS CORRECTS MY OWN MECHANISTIC STORY, WHICH IS THE MOST USEFUL PART. I had explained the
residual gate's failure as "the selector has no spread to rank on" (sd 0.066 about mean 0.44).
PRECISION HAS 2-3x MORE SPREAD (sd 0.134-0.208) AND FAILS ANYWAY. So spread was NOT the binding
constraint, and the story I have been telling since the write gate closed is wrong.**
**➡️ FOUR INDEPENDENT TESTS NOW AGREE: WHICH TRACES ARE KEPT DOES NOT MATTER ON THIS INSTRUMENT --
ONLY HOW MANY.** (residual write gate 0 of 54; NOVEL vs RANDOM a tie; PREC vs RANDOM a coin flip;
and every selective arm sits between AS_IS and FULL regardless of rule.) *That is a real, useful
negative: STOP BUILDING SELECTORS.*
**🧠 FIDELITY -- POSITION AGAIN, AND IT IS THE ONE HONEST ESCAPE LEFT FOR THE PINNED RULE. G2's
precision-weighted residual is a claim about LEARNING -- how much to UPDATE -- not about WHICH
EPISODES TO STORE. We have now tested it four times in the storage role and never in the update
role, because our profiles have no update rule to modulate: they only ever add.** *So the pinned
term may still be right and tested in the wrong place -- which is the same POSITION error found for
the sensorimotor spoke and for k-WTA. Third time.*
*⚠️ Single seed per point, one corpus. Per-point deltas reported BEFORE slopes, per last night's
endpoint lesson.*

## 📝 2026-08-19 -- **THE OWNER'S Q71 RULE, TESTED: WHAT MATTERS IS HOW MANY NOTES, NOT WHICH.**
## **AND I NEARLY HEADLINED A STRONG CLAIM THAT RESTED ENTIRELY ON ONE POINT.**
*Owner Q71: "it's NEWNESS that gets notes, not just words used the same way." Tested at MATCHED
BUDGET -- keep half of each term's occurrences, chosen by novelty vs chosen at random. The
rate-matched control was demanded by the plan in advance, and it is what makes this readable.*

| sentences | AS_IS | NOVEL_50 | RANDOM_50 | FULL | NOVEL - RANDOM |
|---|---|---|---|---|---|
| 1000 | 1.20x | 1.00x | 1.11x | 0.98x | **-0.11** |
| 2000 | 2.29x | 1.64x | 1.79x | 1.71x | **-0.14** |
| 4000 | 3.12x | 2.69x | 2.56x | 2.23x | +0.13 |
| 8000 | 3.69x | 2.34x | 2.39x | 2.06x | **-0.05** |
| 16000 | 6.42x | 6.39x | 5.44x | 4.39x | **+0.94** |

**✅ THE DEFENSIBLE FINDING: VOLUME, NOT SELECTION. Both half-budget arms land between AS_IS and
FULL, and NOVEL vs RANDOM is a coin flip -- NOVEL wins 3 of 5 points, and every delta except one is
within +-0.14.** *Practically useful either way: half the traces buys ~55% of full coverage's
benefit no matter how they are chosen.*
**🚨 AND THE VERDICT MY SCRIPT PRINTED WAS "NOVELTY SELECTION IS WORSE THAN RANDOM (8% vs 55%) --
our residual is ANTI-correlated with usefulness". THAT CLAIM IS NOT SUPPORTED AND I ALMOST FILED
IT.** It came from a SLOPE over five points, and **the final point's delta (0.944) is 8.7x the mean
of the other four (0.109)** -- one endpoint dragging the whole fit. *Fifth gate defect of the
session, and a new species: not too lenient, but ENDPOINT-SENSITIVE. A slope is a summary, and a
summary can be carried by one observation. The per-point column is now printed and the verdict
refuses to headline a slope that one point dominates.*
**🧠 BRAIN-FIDELITY DRILL, AND IT IS THE THIRD INDEPENDENT ROUTE TO THE SAME MISSING TERM.** Our
residual measures "unlike this word's average so far", which CONFLATES two things the owner's rule
separates: **a genuinely NEW SENSE, and a merely NOISY occurrence.** In `simplewiki` most words are
monosemous, so the noisy ones dominate and the selector behaves as an OUTLIER detector rather than a
new-sense detector. **Distinguishing those two is exactly what PRECISION WEIGHTING does in the
brain -- and precision was measured absent from `hdlab/predictive_coding.py` by enumeration (15
public names, not one mentions precision, variance, confidence or weighting).**
*So the owner's principle is NOT refuted here. What is measured is that WE HAVE NO SIGNAL CAPABLE OF
IMPLEMENTING IT.* **That is now the third independent line pointing at the same absent term** (the
write gate's flat residual; the archive's flat-surprise-at-chance; this).
*⚠️ Single seed per point, one corpus, same caveats as the rest of the sweep family.*

## 🧮 2026-08-19 -- **THE 2x2: THE TWO WORKING FIXES ARE SYNERGISTIC, NOT INDEPENDENT -- AND THERE**
## **IS NO CHEAP VERSION. CENTRING ALONE BUYS 19% OF A 63% TOTAL.**
*Both fixes had shown 39%, but from DIFFERENT runs, and the centring run already had full coverage
on -- so chaining them to "-63%" was an inference. Four cells, ONE run, ONE population per point.*

| sentences | cov | COOC | A as-is+sum | B as-is+**centred** | C **full**+sum | D **full+centred** |
|---|---|---|---|---|---|---|
| 1000 | 0.816 | 22.5 | 1.20x | 1.16x | 0.98x | 1.02x |
| 2000 | 0.730 | 14.0 | 2.29x | 2.14x | 1.71x | 1.64x |
| 4000 | 0.708 | 26.0 | 3.12x | 3.10x | 2.23x | 2.00x |
| 8000 | 0.564 | 31.0 | 3.69x | 3.32x | 2.06x | 1.84x |
| 16000 | 0.435 | 18.0 | **6.42x** | 5.36x | 4.39x | **3.11x** |

    phase slope   A +1.708   B +1.384   C +1.035   D +0.631
    centring:  at as-is coverage 19%  |  at FULL coverage 39%
    coverage:  without centring  39%  |  WITH centring    54%
    A -> D total 63%   |   multiplicative prediction +0.838, MEASURED +0.631, deviation -0.207

**⛔ NO CHEAP VERSION EXISTS, AND THAT WAS THE PRACTICAL QUESTION. Centring alone -- a change to how
profiles are READ, costing nothing and touching no reading behaviour -- buys only a 19% slope
reduction against 63% for both. That is under a third of the achievable benefit.** *Centring needs
complete counts underneath it to pay off; the two are entangled and I should stop offering the cheap
option, which I had been ready to recommend shipping.*
**✅ THEY ARE SUPER-ADDITIVE, NOT MERELY ADDITIVE: the independence prediction was +0.838 and the
measured value is +0.631 (deviation -0.207).** Each fix makes the other work better -- centring is
worth 19% alone and 39% once coverage is complete; coverage is worth 39% alone and 54% once centring
is on. *Mechanistically coherent: centring can only remove the shared direction accurately if the
counts it is estimated from are complete.*
**✅ AND IT VALIDATES THE CROSS-RUN ARITHMETIC I FLAGGED AS UNSAFE: I predicted -63% by chaining two
separate runs, warned in the pre-reg that chaining was an inference and not a measurement, and the
one-run measurement came back at exactly -63%.** *The earlier sweeps are mutually consistent -- a
real check on four experiments, not a formality.*
**⚠️ AND THE POSITION IS STILL NOT WON: the best cell is 3.11x behind the counter at 16,000. Both
fixes together FLATTEN the curve by two thirds and do not CLEAR the floor.** *At 1,000 sentences
every cell is at parity (0.98-1.20x); the whole effect is about how fast we fall away, not whether.*

## 🔁 2026-08-19 -- **INCREMENTAL DECORRELATION: HYPOTHESIS REFUTED IN THE OPPOSITE DIRECTION.**
## **DOING IT AFTERWARDS BEATS DOING IT AS YOU GO -- AND MY SCRIPT COULD NOT SEE ITS OWN WINNER.**
*The plan predicted that removing the shared component INCREMENTALLY AT WRITE would beat removing it
post-hoc, "so the store never accumulates the correlated component". All arms at full coverage.*

| sentences | COOC | SUM | **POSTHOC_CENTER** | INCR_CENTER | INCR_OJA |
|---|---|---|---|---|---|
| 1000 | 22.5 | 0.98x | 1.02x | 0.96x | 1.11x |
| 2000 | 14.0 | 1.71x | 1.64x | 1.50x | 2.14x |
| 4000 | 26.0 | 2.23x | 2.00x | 2.60x | 3.10x |
| 8000 | 31.0 | 2.06x | **1.84x** | 2.21x | 3.56x |
| 16000 | 18.0 | 4.39x | **3.11x** | 5.47x | 7.42x |

    phase slope   SUM +1.035   POSTHOC +0.631   INCR_CENTER +1.406   INCR_OJA +2.025
    effective dims at 16,000   SUM 92.3   POSTHOC 29.1   INCR_CEN 100.3   INCR_OJA 143.7

**⛔ THE HYPOTHESIS IS REFUTED, AND BACKWARDS: incremental removal HURTS (+1.406, +2.025 vs SUM's
+1.035) while POST-HOC removal is the best arm measured all session (+0.631, 39% flatter, and the
ONLY intervention that has ever concentrated the code -- 92.3 -> 29.1 effective dims, 3.2x).**
**🔑 MECHANISM, AND IT IS THE SAME LESSON k-WTA TAUGHT LAST NIGHT: an EARLY running estimate of the
shared direction is a BAD estimate, and subtracting a bad estimate corrupts every trace it touches.
OPERATIONS ON THE ADDENDS HURT; THE SAME OPERATION ON THE ACCUMULATED RESULT HELPS. Two independent
experiments now agree, having been designed to show the opposite.** *This retires the "the store
must never accumulate it" intuition, which was mine and was stated confidently in the plan.*
**🚨 AND MY OWN VERDICT LINE SAID "THE ACCUMULATION ROUTE IS EXHAUSTED" -- FLATLY WRONG. The gate
compared only the two INCREMENTAL arms against SUM; POSTHOC was never on the left-hand side of any
comparison, so the best result of the session was invisible to the code that judged it. FOURTH
mis-specified gate in two sessions** (the floor gate that ignored FREQ; "DISCRIMINATES" on 1 nonzero
in 900; arms-differ passing at 0.981 overlap; now a verdict blind to one of its own arms).
*Every one was caught by reading the NUMBERS rather than the VERDICT LINE. That habit is now the
single most load-bearing thing I do.*
**⚠️ WHAT IT DOES NOT DO, STATED BEFORE ANYONE GETS EXCITED: POSTHOC IS STILL 3.11x BEHIND THE
COUNTER AT 16,000. It flattens the curve; it does not clear the floor.** *And at the single 8,000
point I earlier recorded centring as "NOT A LEAD" because it lost to a cue-blind FREQ ranking --
BOTH are true, and they are answers to different questions: it is the best SLOPE intervention and
still not a capability win.*
**➡️ THE OBVIOUS NEXT TEST, AND IT IS CHEAP: FULL COVERAGE gave a 39% slope cut and POST-HOC
CENTRING gives 39%. They target DIFFERENT defects (recording vs concentration) and were measured
independently. DO THEY ADD?** If they compose, the slope lands near +0.4 and the position at 16,000
improves materially; if they do not, they were the same 39% twice and that is worth knowing too.

## ⛔ 2026-08-19 -- **COMPETITION AT WRITE TIME FAILS, AND IT FAILS FOR A REASON THAT OVERTURNS MY**
## **OWN DESIGN ASSUMPTION: SPARSIFYING THE ADDENDS MAKES THE SUM *MORE* DIFFUSE, NOT LESS.**
*All arms at FULL COVERAGE so the note-taking term is held constant. Same corpus, terms, items,
floors. They differ only in the write operation.*

| sentences | COOC | SUM | KWTA8 | KWTA32 | NORM (control) |
|---|---|---|---|---|---|
| 1000 | 22.5 | 0.98x | 1.07x | 0.98x | **0.89x** |
| 2000 | 14.0 | 1.71x | 2.21x | 1.86x | 1.57x |
| 4000 | 26.0 | 2.23x | 3.35x | 2.77x | 2.23x |
| 8000 | 31.0 | 2.06x | 3.40x | 2.34x | 2.15x |
| 16000 | 18.0 | 4.39x | 6.31x | 4.81x | 3.97x |

    phase slope   SUM +1.035   KWTA8 +1.683   KWTA32 +1.174   NORM +0.972

**⛔ NO ARM CUTS THE SLOPE. k-WTA is WORSE than plain summing at every single point and STEEPENS the
degradation (+1.035 -> +1.683). NORM ties SUM (+0.972 vs +1.035) -- within noise, not a win.**
**🔑🔑 AND HERE IS THE MECHANISM, WHICH IS THE OPPOSITE OF WHAT I DESIGNED THE TEST TO GUARD
AGAINST. I wrote in the pre-reg that "k-WTA REDUCES EFFECTIVE DIMENSIONALITY BY CONSTRUCTION", so PR
would be a tautology and must not be the outcome. IT DID THE REVERSE: at 16,000 the effective
dimensionality is SUM 92.3 -> KWTA8 130.2.** *Sparsifying each trace before adding does not sparsify
the total -- it DECORRELATES the addends, so their sum spreads across MORE independent directions
than the dense traces did.* **Sparsity applied to the INPUT of an accumulator is an
anti-concentration operation.** That is a genuine mechanistic result and it explains the ranking
loss rather than merely reporting it.
**📕 THIS IS NOW THE THIRD PLACE SPARSITY HAS FAILED IN THIS CODEBASE, and the prior two were read
BEFORE building, not after:** `exp_c1_sparse_value_k10_cpu_v1` HARD_FAIL (dense capacity 332 vs
sparse 132, ratio 0.40) and `exp_arc_aggregation_sparse_code_regime_v1` SPARSITY_NEUTRAL (0.308 vs
0.301). *The third, `exp_cortex_schema_tonegawa_sparse_ensemble_v2`, is uninformative -- its
baseline sat at 1.000, a saturated regime.* **A low prior was recorded in advance and it was right.**
**🧠 BRAIN-FIDELITY DRILL ON THIS NEGATIVE -- POSITION, and it names the next build precisely.**
Cortical/DG sparse coding is COMPETITION ACROSS THE POPULATION at encoding, with recurrent settling;
the units that win SUPPRESS the others, and what is stored is the settled pattern. **Ours applies
k-WTA WITHIN a single incoming trace and then sums the results INDEPENDENTLY -- there is no
competition BETWEEN encounters and none BETWEEN terms at all.** *We copied the shape of sparsity and
not its position.* **➡️ SO THE UNTESTED FAITHFUL VERSION IS COMPETITION ON THE ACCUMULATED STATE --
between the stored profiles themselves, which is the ATL hub story -- NOT a filter on the incoming
trace. Every variant tested so far, including this one, competes in the wrong place.**
*⚠️ Single seed per point, one corpus, pool grows 58 -> 480. Internal consistency check that
passed: SUM here reads +1.035, exactly the FULL_COV slope from the previous experiment, as it must.*

## 🔬 2026-08-19 -- **WHICH CAUSE? NOTE-TAKING IS WORTH 39% OF THE DEGRADATION AND NOT ONE POINT**
## **OF THE DIFFUSION. THE TWO DEFECTS ARE INDEPENDENT AND ONLY ONE IS VISIBLE TO THE RANKING.**
*The phase diagram said we fall away from the counter as we read. Two causes tracked that curve --
falling coverage and a spreading code. This is the experiment that separates them: same terms, same
corpus, same projection, arms differing ONLY in whether every encounter gets written down. **Because
the arms share the projection, the projection cannot explain a difference between them.***

| sentences | coverage | AS_IS gap | **FULL_COV gap** | COOC | PR as-is | **PR forced** |
|---|---|---|---|---|---|---|
| 1000 | 0.816 -> 1.0 | 1.20x | **0.98x** | 22.5 | 12.6 | 13.2 |
| 2000 | 0.730 -> 1.0 | 2.29x | 1.71x | 14.0 | 18.2 | 20.1 |
| 4000 | 0.708 -> 1.0 | 3.12x | 2.23x | 26.0 | 50.3 | 52.3 |
| 8000 | 0.564 -> 1.0 | 3.69x | **2.06x** | 31.0 | 71.5 | 73.7 |
| 16000 | 0.435 -> 1.0 | 6.42x | **4.39x** | 18.0 | 91.8 | 92.3 |

    slope of the gap vs log(sentences)   AS_IS +1.708   FULL_COV +1.035   -> 39% reduction

**✅ NOT-RECORDING IS REAL AND WORTH FIXING: forcing a note on every encounter improves the LEVEL at
every single point (3.69x -> 2.06x at 8,000; 6.42x -> 4.39x at 16,000) and holds parity with the
counter out to 1,000 sentences (0.98x).** *The owner's instinct that this is about what gets written
down is CORRECT, and it is the largest single lever measured all session.*
**⛔ AND IT IS NOT SUFFICIENT -- THE VERDICT IS PARTIAL, NOT SOLVED. The slope only falls 39% and is
still climbing at +1.035. Even with PERFECT note-taking we are 4.39x behind at 16,000 and still
degrading.** *Anyone quoting "fix the note-taking" must quote this sentence with it.*
**🔑🔑 THE DISSOCIATION IS THE REAL RESULT, AND IT WAS THE PRE-COMMITTED "MOST INFORMATIVE" OUTCOME:
FORCING COMPLETE NOTES DOES NOT MOVE THE DIFFUSION AT ALL. PR goes 12.6 -> 91.8 as-is and
13.2 -> 92.3 forced -- identical to within noise at every point.** So coverage and diffusion are
INDEPENDENT defects: coverage drives the ranking, diffusion is invisible to the ranking metric, and
**writing MORE cannot concentrate a code. Concentration has to come from the write RULE.**
**🧠 BRAIN FIDELITY, and this is the sharpest statement of it yet: the brain's hub CONCENTRATES with
experience (pinned ~4-12 effective dims). We now know that is NOT achievable by recording more --
we just recorded everything and the code diffused exactly as before. A learned code concentrates
because of COMPETITION between representations; ours sums. THE DIVERGENCE IS THE WRITE OPERATION
ITSELF, not the amount written.** *That is a build target, not a shortfall.*
*⚠️ Same caveats as the phase diagram: single seed per point, one corpus, pool grows 58 -> 480.
The MONOTONICITY and the 5-point slope carry the weight, not any single cell.*

## 🌡️🌡️ 2026-08-19 -- **THE PHASE DIAGRAM. THERE IS A REAL PHASE BOUNDARY NEAR ~1,000 SENTENCES:**
## **WE BEAT THE COUNTER BELOW IT AND FALL AWAY FROM IT MONOTONICALLY ABOVE IT.**
*Owner, COMMENTARY 22:27:04Z: "don't forget the phase diagram for these different components".
Built over READ VOLUME -- the one axis every component shares and the one we had never varied.
**Every conclusion reached earlier today came from a single column of this table (8,000).***

| sentences read | candidates | OURS | COOC | **GAP** | coverage | PR_var | resid_sd |
|---|---|---|---|---|---|---|---|
| 600 | 40 | 15.0 | 10.0 | 1.50x | 0.961 | 10.0 | 0.1099 |
| **900** | 58 | **20.0** | **21.0** | **0.95x -- WE WIN** | 0.882 | 12.6 | 0.0929 |
| 1000 | 58 | 27.0 | 22.5 | 1.20x | 0.816 | 12.6 | 0.0896 |
| 2000 | 74 | 32.0 | 14.0 | 2.29x | 0.730 | 18.2 | 0.0793 |
| 4000 | 222 | 81.0 | 26.0 | 3.12x | 0.708 | 50.3 | 0.0662 |
| 8000 | 330 | 114.5 | 31.0 | 3.69x | 0.564 | 71.5 | 0.0661 |
| 16000 | 480 | 115.5 | **18.0** | **6.42x** | 0.435 | 91.8 | 0.0661 |

**⛔⛔ THE PHASE VARIABLE MOVES MONOTONICALLY THE WRONG WAY: 0.95x -> 6.42x, slope +1.708 per
e-fold of reading. MORE DATA IS NOT THE LEVER -- IT IS THE PROBLEM.**
**🔑 AND THE CLEANEST FORM OF IT IS IN THE LAST TWO ROWS: FROM 8,000 TO 16,000 SENTENCES *OUR* ARM
DOES NOT MOVE (114.5 -> 115.5) WHILE THE COUNTER IMPROVES (31.0 -> 18.0). Our representation stops
extracting anything from additional text while plain counting keeps getting better on the same
text.** *That is saturation, stated as directly as this instrument can state it.*
**➡️ ALL FOUR COMPONENT VARIABLES DEGRADE TOGETHER, WHICH IS WHY THIS IS ONE STORY AND NOT FOUR:**
coverage **halves** (0.961 -> 0.435, we record ever fewer of what we meet); effective dimensionality
**rises 9x** (10.0 -> 91.8, the code spreads out instead of concentrating); the residual spread
**shrinks and then FLATLINES** (0.1099 -> 0.0661, then 0.0661, 0.0661).
**✅ THAT FLATLINE IS A PROPER DRILL OF THE WRITE-GATE NEGATIVE, AND IT HARDENS IT.** The gate closed
because the residual was too uniform to threshold. **The spread does not widen with scale -- it
saturates. So the closure is NOT a single-point artifact and no amount of reading reopens it.**
*I flagged that closure as possibly scale-dependent when I set this up; it is not. Recorded because
the prediction was wrong in the safe direction.*
**⚠️ CAVEATS, BEFORE ANYONE QUOTES THE 6.42x: single seed per point, one corpus, and the candidate
pool GROWS with reading (40 -> 480) so the task itself changes down the column. The ratio is used
precisely because the pool cancels between arms at each point -- but a ratio of medians is not a
CI-separated statistic, and no CI was computed ON THE RATIO.** *What carries the weight is the
MONOTONICITY across seven points, not any single value.*
**🧠 BRAIN FIDELITY, since the owner asked for it on every negative: the brain's hub CONCENTRATES
with experience -- that is what the pinned ~4-12 effective dims means. Ours does the opposite,
moving 10.0 -> 91.8 as it reads. SHAPE diverges, and it diverges PROGRESSIVELY. A learned code buys
concentration; an accumulating random projection buys diffusion. This is the same divergence the
geometry and subsumption results found, now shown as a TRAJECTORY rather than a snapshot.**

## 🧪 2026-08-19 -- **GAP-TARGETED READING, TESTED TWICE. THE FIRST RUN WAS VOID AND MY OWN GATE**
## **PASSED IT AT 98% ARM OVERLAP. THE SECOND IS UNDERPOWERED, NOT NEGATIVE.**
*The owner's "patchy" half of Q72, wired from the existing organs. One variable: WHICH sentences get
read, never how many. Three arms, 6,000 sentences each from one 12,000-sentence pool.*

**⛔ RUN 1 WAS VOID AND IT NEARLY GOT REPORTED. GAP and PASSIVE overlapped 0.981 -- 5,943 of 6,057
sentences identical.** Cause: I drew targets from the top-400 frequent non-consolidated words, which
gave 298 targets; frequent words appear in nearly every sentence, so almost everything scored >= 1,
the ranking was flat, and **ties broke by INDEX -- i.e. corpus order -- so the "gap-targeted" arm
silently reproduced passive reading.** *My arms-differ gate asserted `jac < 0.99` and PASSED at
0.981.* **THAT IS THE THIRD TOO-LENIENT GATE I HAVE WRITTEN TODAY** (the floor gate that ignored
FREQ; the "DISCRIMINATES" check that fired on 1 nonzero in 900). Gate now refuses above 0.60 and
fails loud; targets now drawn from MID-frequency words (5 <= count <= 200) with RANDOM tie-breaks.

**RUN 2, arms genuinely distinct (overlap 0.327 / 0.335 / 0.326), 4,924 shared candidates, 300 items:**

| arm | median rank | 95% CI |
|---|---|---|
| PASSIVE | 1296.0 | [860.5, 1692.1] |
| RANDOM_N (rate-matched) | 1205.5 | [1031.0, 1466.0] |
| GAP | 1292.5 | [1028.8, 1501.0] |
| FREQ floor (cue-blind) | 354.0 | [276.5, 432.0] |
| COOC floor | 195.5 | [135.0, 262.0] |

    GAP minus PASSIVE    -88.98  95% CI [-220.31,  +40.72]   NOT separated
    GAP minus RANDOM_N    -6.68  95% CI [-133.01, +121.76]   NOT separated

**⚠️ THE VERDICT IS "UNDERPOWERED", NOT "DOES NOT HELP", AND THE CI IS WHY: a half-width of 130-220
ranks means this test could only ever have detected an enormous effect.** *Same category as the
corpus-diversity result. My script printed "GAP-TARGETED SELECTION DOES NOT HELP HERE" -- too strong
for what a CI that wide can support.*
**🔑 AND A DISTINCTION THAT MATTERS MORE THAN THE NUMBERS: the prior HARD_PASS I was chasing
(`exp_breadth_foundation_active_growth_loop_ud_ewt_v1`) measured COVERAGE, 0.50 -> 0.79. THIS TEST
MEASURES RANK. Those are different claims, and coverage improving does not imply rank improving.**
*So this is NOT a failure to reproduce that cell -- it is a different question, asked for the first
time, and answered "not at this power".* **⛔ Nothing here licenses "the owner's idea does not work".**
**➡️ Every arm remains 6.6x from the COOC floor and well behind a cue-blind FREQ ranking, exactly as
in every other line this session.**

## 🔌 2026-08-19 -- **THE GAP-TARGETED ORGANS ARE BUILT, IMPORT CLEAN, AND ARE DIRECTLY**
## **STATE-COMPATIBLE WITH THE SUBSTRATE. THEY ARE SIMPLY NOT WIRED IN. NO ADAPTER NEEDED.**
*The top item was "test gap-targeted growth". Per the query-before-building rule I checked the code
registry first, and it is another BUILT-PASSING-UNWIRED case: `hdlab/gap_detector.py`,
`hdlab/gap_driven_reader.py` and `hdlab/three_tier_loop.py` all exist, all import, and
`substrate.py` references **none** of them.*
**✅ COMPATIBILITY CONFIRMED WITHOUT AN ADAPTER: `sub.state` IS a `reading_grounding_loop.
ReadingLoopState`, which is exactly what these functions take.**
**✅ AND THE GAP SIGNAL WORKS, shown with a POSITIVE AND A NEGATIVE CONTROL rather than one:**

    is_gap_now on CONSOLIDATED words (already grounded)   0 of 40   correctly NOT gaps
    is_gap_now on NON-consolidated frequent words        20 of 40   correctly ARE gaps
    rank_material over 10 docs x 30 sentences   scores 8,4,4,2,1,1,1,0,0,0 -- discriminates

**⚠️ AND I NEARLY FILED THE OPPOSITE. My first probe reported "0 of 68 gaps" and "1 nonzero score in
900 pairs" and I was one step from recording THE ORGAN IS INERT. Both signals were MY OWN BUGS:**
1. `rank_material` takes `doc_id -> a sequence of SENTENCES`; **I passed `s.split()`, a sequence of
   single WORDS**, so almost nothing could ever match.
2. I ran `is_gap_now` on the **CONSOLIDATED** terms -- words the substrate has already grounded,
   which by definition are not gaps. **I tested the one population guaranteed to return zero.**
*Both are the same underlying error: an absence result was produced by MY setup and would have been
attributed to the ORGAN. The positive control is what separated them -- "20 of 40 on the other
population" cannot be faked by a broken detector.* **AND MY OWN CHECK PRINTED "DISCRIMINATES" ON A
SINGLE NONZERO OUT OF 900 -- too lenient, the same failure mode as the floor gate two results
earlier. Twice in one session I wrote a gate that could not fail.**

## 📐 2026-08-19 -- **THE DIMENSIONALITY CLAIM, SETTLED ON MATCHED FORMULA AND MATCHED**
## **POPULATION. MY ORIGINAL CLAIM WAS INVALID AND MY CORRECTION TO IT WAS ALSO WRONG.**
*Three versions of this claim now exist. Only the third is measured on a comparison where everything
matches, and it is the only one to quote.*

| object (8,450 sentences, same corpus, same 256 dims) | PR_variance | PR_singular | rank90 | top-4 share |
|---|---|---|---|---|
| **OUR PROFILES (all 9,624 terms)** | **191.5** | **238.6** | 201 | 0.054 |
| OUR PROFILES (consolidated, 330) | 71.5 | 163.9 | 115 | 0.151 |
| **RAW COUNT VECTORS (9,305 terms)** | **131.7** | **219.7** | 182 | 0.092 |
| our profiles, shuffled | 249.1 | 254.2 | 223 | 0.021 |
| pure noise, same shape | 249.4 | 254.3 | 223 | 0.021 |
| MiniLM (CITED, archive, ITS population) | not stored | 91.6 | 175 | -- |
| brain, PINNED (Huth) | ~4-12 | ~4-12 | -- | -- |

**⛔ V1 -- "we are 4-12x too diffuse vs the brain" -- WAS NOT A COMPARISON.** Two mismatches, either
of which alone invalidates it: the archive's formula is `(sum s)^2/sum s^2` over SINGULAR VALUES,
mine was `1/sum(v^2)` over VARIANCE SHARES (they differ by 1.2x on our own matrix); and my 50.4 was
measured on the CONSOLIDATED population while the natural comparison is all profiled terms
(**71.5 vs 191.5 -- the population effect is 2.7x, larger than the formula effect**).
**⛔ V2 -- "so it is probably just what learning from text looks like" -- NOT SUPPORTED.** On the
SAME formula we read **238.6 against MiniLM's 91.6, i.e. 2.60x**. *That comparison still has its own
population caveat -- their number is over sentence embeddings on their corpus, ours over word
profiles on ours -- so it is suggestive, not decisive. But it does not support the shrug.*
**✅ V3, THE ONE TO QUOTE, BECAUSE EVERYTHING MATCHES -- same corpus, same sentences, same terms,
same width, same formula: OUR PROFILES ARE LESS CONCENTRATED THAN THE RAW COUNTS THEY ARE BUILT
FROM. 191.5 vs 131.7, and the top four components hold 0.054 of the variance against the counts'
0.092.** Both are real structure (noise and shuffled sit at ~249).
**🔑 SO THE RANDOM PROJECTION IS NOT NEUTRAL -- IT DE-CONCENTRATES.** We take a count matrix and
produce something MORE spread out than what we started with. *That is a sharper statement of the
subsumption result than the brain comparison ever was, it needs no pinned figure to make its point,
and it names a specific suspect: **the projection, not the counting**.*
**➡️ AND IT MAKES THE NEXT TEST OBVIOUS AND CHEAP:** the ridge read-out says the profile's most
recoverable content is FREQUENCY (R^2 0.4819). If a dominant common direction is eating the
variance, removing it should concentrate the code. *Swept over k, scored against the COOC and FREQ
floors on the same items -- because "better than our own previous arm" is the trap that has caught
three lines already.*

## 📉 2026-08-19 -- **REMOVING THE COMMON DIRECTION: A SMALL REAL GAIN, AND A FLOOR THAT MAKES IT**
## **IRRELEVANT. MY OWN SCRIPT'S VERDICT WAS TOO GENEROUS AND IS CORRECTED HERE.**
330 candidates, 300 held-out items (0.0% leaked -- drawn from the substrate's own advanced handle),
paired bootstrap on identical items:

| arm | median rank | 95% CI | vs RAW, paired |
|---|---|---|---|
| RAW | 91.0 | [74.5, 104.0] | -- |
| **MEAN_REMOVED** | **83.0** | [70.0, 100.0] | **-4.41, CI [-6.83, -2.06] SEPARATED** |
| PC1_REMOVED | 83.5 | [69.0, 107.0] | -3.67, CI [-7.58, +0.15] not separated |
| PC2_REMOVED | 97.5 | [83.0, 118.0] | +3.73 SEPARATED **WORSE** |
| PC4_REMOVED | 106.0 | [86.5, 127.0] | +6.06 SEPARATED **WORSE** |
| PC8_REMOVED | 115.0 | [92.0, 135.5] | +11.71 SEPARATED **WORSE** |
| **FREQ floor** (cue-blind) | **71.0** | [60.5, 71.0] | -- |
| **COOC floor** | **20.5** | [15.0, 26.0] | -- |

**⛔ THE HEADLINE IS THE FLOOR, NOT THE GAIN: A RANKING THAT NEVER LOOKS AT THE SENTENCE -- ORDER
EVERY CANDIDATE BY HOW OFTEN IT APPEARS IN THE CORPUS -- REACHES 71.0. OUR BEST ARM REACHES 83.0.
EVERY ARM WE RAN LOSES TO A FLOOR THAT IGNORES THE QUESTION.** And the real bar, COOC at 20.5, is
four times better again.
**⚠️ AND THE SCRIPT I WROTE DECLARED "REAL LEAD" ANYWAY, because its verdict gate compared only to
COOC and I never wired FREQ into the decision -- I printed it and did not gate on it.** The standing
rule is *CI-separated margin over the STRONGEST floor actually run*; I ran the floor and then failed
to use it. **Corrected verdict: NOT A LEAD.**
**✅ WHAT IS NEVERTHELESS TRUE, AND SMALL: centring the profiles helps by a separated margin**
(91.0 -> 83.0). *Note MEAN_REMOVED is simply CENTRING -- and `PC1_REMOVED` is centring PLUS removing
one more component, which is already no better. Removing further components degrades MONOTONICALLY.*
So there is exactly one direction worth deleting and it buys 8 ranks out of 330.
**🔑 READ TOGETHER WITH THE GEOMETRY ABOVE, THIS IS COHERENT AND IT IS NOT ENCOURAGING: our code is
MORE diffuse than the counts it comes from, and the diffuseness is NOT concentrated in a few
removable directions -- if it were, removing them would help and it makes things worse. The variance
is spread thin across the whole spectrum, which is what a random projection does to a signal.**
*No post-hoc transform reaches that. It is a property of how the code is WRITTEN.*

## 📚 2026-08-19 -- **THE OWNER'S Q72 ("GIVE IT ANOTHER TEXTBOOK") HAS TWO HALVES. THE HALF I**
## **TESTED IS UNTESTED-AT-THIS-N; THE HALF I DID NOT TEST ALREADY HARD_PASSED A MONTH AGO.**
*Owner, Q72: "Why aren't we identifying where the notes are PATCHY and/or giving them another
textbook? There's only so much you can get from one textbook."* They are two proposals and they have
different answers.

**HALF ONE -- PASSIVE BREADTH (read the same amount, spread over more sources). TESTED TODAY, AND
THE ANSWER IS "NO MEASURABLE DIFFERENCE", NOT "IT HURTS".** One variable, same total reading, each
arm scored against its own counter so a harder candidate pool cannot be mistaken for progress:

| | corpora | OUR median rank | counter median rank | ratio |
|---|---|---|---|---|
| ONE_CORPUS | 1 | 91.0 (CI 68.5-111.0) | 19.5 (CI 15.5-25.0) | 4.67x |
| MANY_CORPORA | 27 | 106.5 (CI 89.0-122.0) | 20.0 (CI 16.5-29.0) | 5.33x |

**MANY minus ONE, ours: +15.8, 95% CI [-10.0, +42.5] -- NOT separated from zero.** Counter: +1.2,
CI [-5.0, +10.0], also not separated. **⛔ SO THE HONEST VERDICT IS UNTESTED AT THIS n, AND I NEARLY
FILED IT AS A NEGATIVE:** the point estimates alone (91 -> 106.5) read as "diversity hurts us", and
the pre-committed third reading was written for exactly that. The CI says the width swallows it.
*Do not quote "spreading reading across corpora made it worse."*

**HALF TWO -- ACTIVE, GAP-TARGETED GROWTH (find the patchy bits, then go read for them). ALREADY
LANDED, HARD_PASS, AND I DID NOT KNOW IT WHEN I DESIGNED TODAY'S TEST.**
`exp_breadth_foundation_active_growth_loop_ud_ewt_v1`, disk-verified:

    on_miss_ratio   0.348      per-token miss 0.43 -> 0.15
    coverage        0.50 -> 0.79   (d = +0.291)
    use_real_auc    0.8924     vs shuffle 0.5122 +- 0.1003, delta 0.3802
    retention_gap   0.852      n_sent 6000, n_grown 8422, n_escalations 2099

**➡️ THE OWNER'S INSTINCT IS RIGHT, BUT THE LOAD-BEARING WORD IS "PATCHY", NOT "ANOTHER TEXTBOOK".**
Reading more widely at random does nothing measurable. Reading TO FILL A NAMED GAP moves coverage
from half to four-fifths with a real-vs-shuffled separation of 0.38. *That is the same shape as
GAP == GROUNDING: naming the gap and traversing it are one act.*

**⚠️ AND "NON-ADDITIVE" MUST NOT BE READ AS "IN-PLACE EDITING" -- I CHECKED THE ARCHIVE BEFORE
PROPOSING IT THIS TIME.** `exp_additive_only_cert_cpu_v1` (MIDDLE_BAND) set out to certify that
additive writes stay stable while in-place edits accumulate error ~ edits^2/N and collapse recall.
**Disk-verified, the discriminator did NOT fire: additive@200 = 1.000 and in-place@200 edits =
1.000.** Both arms sat at ceiling, which is why it landed MIDDLE_BAND. *So that cell neither
supports nor blocks a non-additive write -- it is uninformative at that scale, and the honest
statement is that the question is OPEN.* What the geometry argues for is a write that can
CONCENTRATE variance -- competition, normalisation, sparsification, something learned -- **not
subtract-old-and-add-new, which is a different proposal that this cell tried and could not
discriminate.**

## 🟢🟢 2026-08-19 -- **THE OWNER REMEMBERED PRIOR WORK THAT PREDICTED TODAY'S FAILURE THREE WEEKS**
## **AGO, AND IT GIVES THE ORDER OF OPERATIONS: PREDICTION FIRST, NOVELTY SECOND, NOTES THIRD.**
*Owner, COMMENTARY 20:22Z: "on the note taking and a 'newness detector' - I think we did do some
work on this - so is worth looking back at the experimental corpus." They were right; I had not
looked.*
`exp_ingest_gate_strong_foundation_novelty_v2` (2026-07-16), verdict
**`SEMANTIC_NOVELTY_derivability_dose_dependent_on_foundation_strength`**:

| foundation strength (inferable MRR) | novelty-detection AUC |
|---|---|
| **DEAD 0.013** | **0.605 -- near chance** |
| WEAK 0.331 | 0.969 |
| STRONG 0.741 | 0.988 |

**dose-response +0.384; encoding-status AUC tracked separately (0.627 / 0.976 / 1.000) so the two
were never conflated; per-candidate arrays dumped and the key AUC RECOMPUTED OFF-DISK.**
**➡️ ITS CENTRAL SENTENCE EXPLAINS TODAY IN ONE LINE: *"surprise = can the CURRENT foundation
predict this, which BECOMES semantic-novelty as the foundation strengthens"* -- and *"a DEAD
non-generalizing foundation must COLLAPSE the KEY AUC to ~chance."***
**⛔ THAT IS EXACTLY WHAT TODAY'S RESIDUAL WRITE GATE DID.** Our profiles predict their own next
context only 10.4% better than an unrelated term's, and our median rank is 81 of 223 -- **we are in
the DEAD regime by this cell's own dial, where it MEASURED that novelty detection collapses to
chance.** *The gate did not fail because predictive coding is wrong. It failed because novelty
detection is DOWNSTREAM of prediction quality, and ours has none to speak of.*
**🎯 SO THE OWNER'S "NEWNESS GETS NOTES" PRINCIPLE IS RIGHT AND IS NOT YET BUILDABLE. The order is
forced: (1) make the foundation PREDICT, (2) novelty detection then works for free -- it is the
same signal -- (3) only then do notes-on-newness mean anything.** *Steps 2 and 3 are not separate
builds; they fall out of step 1. Everything today was an attempt at step 3 while step 1 was unmet.*
**⚠️ THE HONEST LIMIT, STATED BEFORE ANYONE CITES THIS: that dose-response was measured in a
SYNTHETIC compositional TransE arena, chosen deliberately because a strong generalizing foundation
does not exist on our real data (the same note records real CSKG capping at MRR ~0.13). TRANSFER TO
OUR SUBSTRATE IS A HYPOTHESIS, NOT A RESULT.** *But the DEAD-regime prediction is the part we
already match, and we match it exactly.*

## ✅ 2026-08-19 -- **9-SEED SWEEP FINAL. THE PRE-REGISTERED CONJUNCTION FAILS, AND THE TWO**
## **QUANTITIES SEPARATE CLEANLY -- ONE IS SOLID, THE OTHER IS NOISE AROUND A LOW CENTRE.**

| quantity | mean | median | min | max | sd | seeds passing |
|---|---|---|---|---|---|---|
| **union / counter** | **2.03** | 2.15 | **1.50** | 2.23 | 0.24 | **9 of 9** |
| independence ratio | 0.87 | 0.91 | 0.70 | 0.98 | 0.09 | **6 of 9** |

**⛔ VERDICT AS PRE-REGISTERED: FAILS.** The conjunction required ratio >= 0.85 AND union >= 1.5 on
EVERY seed. Union holds 9 of 9; the ratio holds 6 of 9. **The strong claim -- "the spoke is a
genuinely independent second channel" -- IS NOT ESTABLISHED, and no combination build proceeds on
it.**
**✅ WHAT NINE SEEDS BOUGHT THAT THREE COULD NOT: the two quantities have DIFFERENT RELIABILITY and
should never have been quoted as one finding.** The union gain is **tight and never below 1.50**.
The ratio is **noisy (sd 0.09) around a centre of 0.87-0.91, i.e. slightly BELOW independence**.
*So 0.70 was neither an outlier nor the centre -- it is the low tail of a distribution whose centre
sits just under the bar.*
**🎯 THE SURVIVING, DEFENSIBLE STATEMENT: the spoke and the counter succeed on almost entirely
DIFFERENT items -- only 1-6 of ~250 are ever got right by both, on every seed -- so combining them
would roughly double what counting achieves alone. What is NOT established is that the spoke's
unique contribution exceeds what chance overlap predicts.** *Both halves are needed; either alone
misleads.*
**⚠️ AND THE PROCESS NOTE THAT MATTERS MORE THAN THE RESULT: I characterised this quantity from 1
seed (0.94, "at independence"), then 4 (0.83), then 7 (0.88), then 9 (0.87). Three of those four
characterisations were wrong, and each was stated with more confidence than the data carried.
Nine seeds cost about 80 minutes of compute and prevented a build on a number that was never
there.*

## 📈 [SUPERSEDED BY THE FINAL 9-SEED READ ABOVE] 2026-08-19 -- **RUNNING READ, 7 OF 9 SEEDS: THE ESTIMATE HAS MOVED TWICE AND IS STILL MOVING.**
Ratios in landing order: **0.70 / 0.94 / 0.89 / 0.81 / 0.92 / 0.93 / 0.98**. Union/COOC:
**1.50 / 2.23 / 1.94 / 2.23 / 2.00 / 2.17 / 2.18 -- all seven >= 1.5.**
**My running mean has gone 0.94 (1 seed) -> 0.83 (4 seeds) -> 0.88 (7 seeds). Two of seven sit
below the 0.85 threshold; five clear it.**
*I have now characterised this quantity three times and been wrong twice. The honest statement at
7 seeds: **the union gain is STABLE and unambiguous (1.50-2.23, every seed); the independence
ratio is NOISY around ~0.88 with a low tail.** Those are different quantities with different
reliability, and only the first is safe to build on.*
**⚠️ AND THE PRE-REGISTERED CONJUNCTION STILL FAILS on the ratio arm, exactly as it did at 3
seeds. More data has NOT rescued it -- it has just made the failure better characterised.**
*2 seeds outstanding. The verdict is the 9-seed distribution, not this line.*

## 📉 [SUPERSEDED BY THE 7-SEED READ ABOVE] 2026-08-19 -- **RUNNING READ, 4 OF 9 SEEDS: THE FIRST SEED I HAPPENED TO RUN WAS THE BEST**
## **ONE, AND I CHARACTERISED THE FINDING FROM IT.**
Spoke-independence ratios as they land: **0.70 / 0.94 / 0.89 / 0.81** (seeds 20260819 / 7 / 101 /
13). Union/COOC: 1.50 / 2.23 / 1.94 / 2.23 -- **all four >= 1.5.**
**⚠️ I DESCRIBED THIS FINDING AS "~INDEPENDENT OF COUNTING (0.94)" OFF A SINGLE SEED. The running
mean is ~0.83, and 0.94 is the HIGHEST of four.** *Seed 7 was not cherry-picked -- it was simply
the first one I ran -- but a single seed is as likely to be the best of its distribution as the
worst, and I characterised a distribution from one draw of it. **The correction is not that the
finding is gone; it is that "at independence" was the top of the range, not the centre.***
**🔎 AND BOTH THINGS ARE TRUE AT ONCE, WHICH IS THE ACTUAL SHAPE: the ratio sits consistently a
little BELOW independence (~0.83), AND the union still nearly doubles counting -- because the
ABSOLUTE overlap is tiny (2-6 items of ~250).** A slight positive correlation in which items each
arm gets right coexists with almost no shared successes. *Neither "complementary" nor "subsumed"
is the right word; the honest statement needs both numbers.*
*5 seeds still to land. No verdict until they do.*

## 🔎 2026-08-19 -- **THE INSTRUMENT IS NOT FREQUENCY-DOMINATED, AND THAT MAKES OUR RESULT WORSE.**
A `FREQ_floor` that never looks at the cue beat every cortical arm at k>=10, which raised the
question of whether this task is winnable by cue at all. **It is.** From the v3 metrics already on
disk, no new run:

| seed | COOC@10 | FREQ@10 | ratio | COOC@50 | FREQ@50 | ratio |
|---|---|---|---|---|---|---|
| 101 | 0.3933 | 0.1667 | **2.36x** | 0.7633 | 0.4867 | 1.57x |
| 20260819 | 0.4067 | 0.1767 | **2.30x** | 0.7533 | 0.4700 | 1.60x |
| 7 | 0.3667 | 0.2167 | 1.69x | 0.7233 | 0.4567 | 1.58x |

**Counting beats the cue-blind floor by 2.12x at k=10 and 1.59x at k=50, on every seed, and by
median rank 15-20.5 against 52-61 -- roughly 3x.**
**⛔ SO THE TASK HAS REAL CUE-EXPLOITABLE SIGNAL AND COUNTING HARVESTS IT. THE EXCUSE THAT "THIS
INSTRUMENT MOSTLY MEASURES WORD FREQUENCY" IS NOT AVAILABLE.** *Our arms losing to `FREQ_floor` is
therefore not a property of the task being frequency-shaped -- it is our representation failing to
use a cue that a word counter uses successfully. That reading is strictly worse for us than the
one I flagged two blocks ago, and it is the correct one.*

## 🟡 2026-08-19 -- **THE SPOKE REPLICATION: PARTIAL. BY MY OWN PRE-REGISTRATION IT DOES NOT**
## **REPLICATE, AND I AM HONOURING THAT RATHER THAN RE-READING THE THRESHOLD.**
`scratch/diag_spoke_independence_seeds.py`, 3 seeds, 8,000 sentences each, n=246-277.

| seed | n | SPOKE | COOC | both | spoke-only | predicted | ratio | **union/COOC** |
|---|---|---|---|---|---|---|---|---|
| 20260819 | 277 | 0.0614 | **0.0794** | 6 | 11 | 15.6 | **0.70** | 1.50 |
| 7 | 246 | 0.0732 | 0.0528 | 2 | 16 | 17.0 | 0.94 | 2.23 |
| 101 | 250 | 0.0720 | 0.0640 | 3 | 15 | 16.8 | 0.89 | 1.94 |

**PRE-REGISTERED: ratio >= 0.85 AND union >= 1.5 on ALL THREE. Union holds 3 of 3 (1.50 / 2.23 /
1.94). Ratio holds 2 of 3 -- seed 20260819 reads 0.70. THE CONJUNCTION FAILS, so the strong claim
is NOT established and the combination build DOES NOT PROCEED.**
**⚠️ AND I AM FLAGGING THE TEMPTATION RATHER THAN ACTING ON IT.** Last turn I argued that the
UNION GAIN is the correct discriminator, and union passes 3 of 3 here. Adopting it now, when it is
the criterion that rescues the result, would be motivated reasoning **even though I named it
before seeing this data**. *The pre-registration for THIS run required both. Both is what it gets.*
**✅ WHAT SURVIVES, NARROWED AND USEFUL: the union gain is CONSISTENT (1.50-2.23 on every seed),
and only 2-6 of ~250 items are ever got right by BOTH arms.** So the channels do overlap very
little; what is NOT stable is whether the spoke's unique contribution sits at or below what
independence predicts. **AND THE SPOKE DOES NOT BEAT COUNTING: it wins 2 seeds and LOSES the third
(0.0614 vs 0.0794), which is the same tie reading (B) already gave on the precision instrument.**
**➡️ NEXT IS MORE SEEDS, NOT A BUILD.** The quantity that moved is a ratio of small counts
(11-16 spoke-only against a ~16 prediction); 3 seeds cannot separate real instability from
sampling noise at that count. *Anything built now would rest on the one seed that happened to fire.*

## 🔴🔴 2026-08-19 -- **v3 SETTLES IT: THE CORTICAL READ RETRIEVES AND IS NOT COMPETITIVE.**
## **18 OF 18 FLOOR CELLS FAIL. AND A CUE-BLIND FREQUENCY RANKING BEATS IT AT k>=10.**
`v3_floors_at_k`, 3 seeds, 966 s, 300 items/seed, 428-480 candidates. **I recorded the prediction
BEFORE the run (`3ca164923`): "I expect v3 to show the route does NOT clear the floor." It does not.**

| seed 20260819 | hit@1 | hit@10 | hit@50 | median rank |
|---|---|---|---|---|
| **RANK_COOC_floor** | **0.0867** | **0.4067** | **0.7533** | **15** |
| RANK_FREQ_floor *(never sees the cue)* | 0.0400 | 0.1767 | 0.4700 | 61 |
| RANK_BOTH | 0.0300 | 0.1533 | 0.3967 | 69 |
| RANK_CONTEXT | 0.0567 | 0.1800 | 0.3433 | 126 |
| RANK_SCRAMBLE | 0.0067 | 0.0367 | 0.1900 | 173 |

**⛔ `CONTEXT_clears` AND `BOTH_clears` ARE FALSE AT EVERY k ON EVERY SEED -- 18 of 18 cells.**
Counting puts the target at median rank **15-20 of ~450**; our best arm puts it at **69-79**.
**🚨 AND THE PART I DID NOT PREDICT, WHICH IS WORSE THAN THE PREDICTION: `FREQ_floor` -- a ranking
that NEVER LOOKS AT THE CUE -- BEATS every cortical arm at k>=10** (hit@50 0.4700 vs BOTH's 0.3967
and CONTEXT's 0.3433). *The route does use its cue: it beats SCRAMBLE, CI-separated, on every seed.
But most of the achievable score on this task comes from knowing WHICH TERMS ARE COMMON, and a
constant ranking harvests more of that than our cue-dependent route does.* **That is what the
frequency floor exists to expose, and it is the first time this session it has caught something.**
**➡️ THIS CLOSES THE CORTICAL READ AS A LINE OF WORK. Both claims are now established and they must
travel together: IT RETRIEVES (reading A fires, 3 seeds) and IT IS NOT COMPETITIVE (0 of 18 floor
cells). Combined with the subsumption result -- unique contribution BELOW independence at every k --
there is nothing left to build here.** *The accumulated-context representation is the ceiling, not
the read-out, and that has now been shown three independent ways.*

## ✅ [SUPERSEDED BY v3 ABOVE, WHICH ADDS THE FLOORS v2 LACKED] 2026-08-19 -- **v2 LANDED, 3 SEEDS: READING (A) FIRES. THE CORTICAL READ RETRIEVES --**
## **AND THE CELL CANNOT SAY WHETHER IT BEATS COUNTING, WHICH IS A GAP I BUILT.**
`exp_cortical_read_consolidated_v1` spec `v2_hitk_sentencecue`, 811 s, 300 items/seed, 428-480
consolidated terms. **`READING (C): [True, True, True]` -- the cue fix held on every seed.**
**k where REAL clears SCRAMBLE's upper CI AND chance: [1,5,10,25,50] / [1,5,10,25,50] / [5,10,25,50].**

| seed 20260819 | hit@1 | hit@10 | hit@50 | median rank |
|---|---|---|---|---|
| RANK_CONTEXT | 0.0567 | 0.1800 | 0.3433 | 126 |
| RANK_SPOKE | 0.0100 | 0.1067 | 0.3433 | **82** |
| **RANK_BOTH** | 0.0300 | 0.1533 | **0.3967** | **69** |
| RANK_SCRAMBLE | 0.0067 | 0.0367 | 0.1900 | 173 |
| chance | 0.0023 | 0.0234 | 0.1168 | -- |

**🟢 `BOTH` HAS THE BEST MEDIAN RANK ON ALL THREE SEEDS (69 / 75.5 / 79) and the best hit@50 on two
-- while SPOKE ALONE has a better median (82-88) than CONTEXT (115-126) despite a WORSE hit@1.**
*The two channels are good at different things, which is the independence result showing up
independently in a different table.*
**⛔ THE GAP, AND IT IS MINE: I computed hit@k for the cortical arms and the scramble BUT NOT FOR
THE FLOORS.** So reading (A)'s bar is *"clears SCRAMBLE and chance"*, which is WEAKER than this
project's standard *"clears the strongest floor's upper bound"*. **THIS TABLE THEREFORE CANNOT SAY
WHETHER THE CORTICAL READ BEATS COUNTING AT ANY k, AND MUST NOT BE READ AS SAYING SO.**
*The separate subsumption diagnostic already indicates it does not -- COOC hit@50 0.6800 vs
cortical 0.3767 at 223 candidates -- but that is a different pool size and does not transfer.*
**➡️ FIX: add `COOC_floor` and `FREQ_floor` to the hit@k block. Until then the honest claim is
"the route retrieves", NOT "the route is competitive".**

## 🟢 2026-08-19 -- **THE SPOKE IS NOT SUBSUMED. IT IS ~INDEPENDENT OF COUNTING, AND THE UNION**
## **MORE THAN DOUBLES IT. THE CONTRAST WITH THE CORTICAL ROUTE IS THE FINDING.**
`scratch/diag_spoke_complementary_or_subsumed.py`, on the spoke's OWN instrument (grounded terms,
co-occurring candidates, provenance-filtered ConceptNet gold), 8,150 sentences, n=246.

| | SPOKE | COOC | both | spoke-only | predicted | ratio | **UNION / COOC** |
|---|---|---|---|---|---|---|---|
| spoke | 0.0732 | 0.0528 | **2** | 16 | 17.0 | **0.94** | **0.1179 / 0.0528 = 2.2x** |
| cortical (for contrast) | 0.3767 | 0.6800 | 93 | 20 | 36.2 | 0.55 | 0.7467 / 0.6800 = **1.1x** |

**⚠️ MY PRE-REGISTRATION WAS MIS-SPECIFIED AND I AM NOT GOING TO READ IT LITERALLY.** I wrote
"materially ABOVE independence -> complementary; AT OR BELOW -> subsumed", which lumps *at
independence* together with *below independence*. **Those mean OPPOSITE things for buildability.**
A ratio of 0.94 means the two arms succeed on DIFFERENT items at chance-overlap rates -- only
**2 of 246** items were got right by both -- which is precisely the case where combining them pays.
Subsumption is ratio << 1 **AND** union ~= the stronger arm alone. **The correct discriminator is
the UNION GAIN, and by it the two channels separate cleanly: the spoke's union is 2.2x counting,
the cortical route's was 1.1x.**
**➡️ SO THE SPOKE IS A REAL SECOND CHANNEL AND THE CORTICAL ROUTE WAS NOT.** *That is exactly what
the hub-and-spoke frame predicts: a spoke carries modality information text does not, while another
way of reading the same text-derived profiles carries nothing new.*
**⛔ POWER, STATED HONESTLY: the counts are SMALL -- 18 spoke hits, 13 counting hits, 2 overlapping,
n=246. The direction is clear and the union gain is large, but this is ONE measurement at low
count and it needs seeds before it is quoted as a result.** *It also does NOT rescue the spoke's
tie on precision (reading B, 0 of 3 seeds significant) -- a tie plus independence means two
comparable channels, not a better one.*

## 🔴🔴 2026-08-19 -- **THE CORTICAL ROUTE IS SUBSUMED BY WORD COUNTING. NOT MERELY BEATEN --**
## **ITS UNIQUE CONTRIBUTION IS BELOW WHAT INDEPENDENCE PREDICTS, AT EVERY k.**
`scratch/diag_complementary_or_subsumed.py`. **This is the FIXED route (sentence cue), not the
broken one** -- so it is the best version of our representation, on held-out text, over the same
candidate set as the counter. 4,300 sentences, 223 candidates, n=300.

| k | CORTICAL | COOC | both | **cortical-only** | independence predicts | **ratio** |
|---|---|---|---|---|---|---|
| 1 | 0.0567 | 0.0433 | 4 | 13 | 16.3 | **0.80** |
| 10 | 0.1300 | 0.3367 | 27 | 12 | 25.9 | **0.46** |
| 50 | 0.3767 | 0.6800 | 93 | 20 | 36.2 | **0.55** |

**⛔ AT EVERY k THE CORTICAL-ONLY CELL IS BELOW ITS INDEPENDENCE PREDICTION.** The two routes are
POSITIVELY correlated in what they get right, and our route's unique contribution is *smaller than
chance would give* -- it is not a different view of the problem, it is a WEAKER VIEW OF THE SAME
ONE. *"Scores lower" and "knows nothing new" are different claims, and this is the second.*
**⛔ AND THE GAP WIDENS WITH k: at hit@50 counting reaches 0.6800 against our 0.3767.** The union
oracle -- an impossible arm that always picks the better route -- reaches only 0.7467, barely above
counting alone, which is exactly the signature of subsumption rather than complementarity.
**➡️ THE CONSEQUENCE, AND IT IS A STOP RATHER THAN A PIVOT: STOP BUILDING READ-OUT VARIANTS ON THE
ACCUMULATED-CONTEXT REPRESENTATION.** Three read-out variants have now been built on it (episodic,
cortical-context, cortical-both) and the ceiling is not in the read-out. **The lever is the
REPRESENTATION or the SUPPLY, never another way of querying the same profiles.**
**⚠️ SCOPE, STATED: one seed, one corpus, 4,300 sentences, 223 candidates, held-out only. The
direction is unambiguous at every k but the exact ratios are a single measurement.**

## 🟢🟢 2026-08-19 -- **v2 SEED 1: THE CUE FIX WORKED AT FULL SCALE, AND THE SCRAMBLE COLLAPSED.**
Same seed, same 16,600 sentences, same 428 consolidated terms -- **only the cue construction and
the scorer changed.**

| arm | v1 (profile-sum cue) | **v2 (sentence cue)** |
|---|---|---|
| CORTICAL_CONTEXT | 0.0433 | **0.0567** |
| **SCRAMBLE** | **0.0500** | **0.0067** |

**⛔ THAT IS THE WHOLE VOID VERDICT EXPLAINED: the scramble arm fell 7.5x while the real arm rose.**
v1's arms were indistinguishable because the profile-sum cue let an UNRELATED donor sentence score
almost as well as the real one; querying the space the index is actually built in removes that.
**SO THE ANSWER TO THE OPEN CONFOUND IS CUE CONSTRUCTION, NOT SCALE** -- this is the cell's own
scale, unchanged.
**⚠️ ONE SEED. `COOC_floor` still leads at 0.0867 and the cortical arms have NOT beaten it. Reading
(A) needs REAL to clear SCRAMBLE **and** chance at the same k, per-seed, across three seeds -- the
hit@k table decides that, not this line.** *Do not quote 0.0567 as a capability.*

## ⚠️ 2026-08-19 -- **CORRECTION TO MY OWN "4.9x" -- A THIRD OF THE SEEN CONTROL WAS A VECTOR**
## **MATCHING ITSELF. THE READING SURVIVES; THE MAGNITUDE WAS OVERSTATED BY ME.**
`scratch/diag_seen_control_is_inflated.py`. A term's profile IS THE SUM OF THE CONTEXT VECTORS IT
WAS SEEN IN, so on SEEN text the cue sentence's own context vector is one of the summands and the
cosine is partly **a vector against itself**. I applied this project's no-leak rule to the TARGET
TOKEN and never to the CUE SENTENCE.

| SEEN cue-to-target cosine | value |
|---|---|
| FULL profile (**what I published**) | 0.2588 |
| **LEAVE-ONE-OUT** (cue's own trace removed) | **0.1702** |
| self-match contribution | **+0.0886 = 34% of the full value** |

**POSITIVE CONTROL BINDS: exactly 1 trace removed on 200 of 200 items** -- the leave-one-out was
not vacuous, which is the empty-set trap that already caught me once today.
**➡️ THE CORRECTED NUMBER: the memorise-vs-transfer drop is 3.3x, NOT the 4.9x I published two
turns ago (0.1702 / 0.0519, not 0.2551 / 0.0519).** *The DIRECTION and the reading are unchanged --
profiles still memorise far better than they transfer -- but anyone quoting "4.9x" is quoting a
number inflated by a third by self-match.* **USE 3.3x.**
*Nothing else in that diagnostic moves: the held-out side never had this confound (the cue sentence
was never read, so it contributed no trace), and the hit@k separation is measured on held-out only.*

## 🟢 2026-08-19 -- **THE CORTICAL READ DOES RETRIEVE. READING (A) FIRES AT EVERY k -- AND THE**
## **CELL'S VOID VERDICT IS PART CUE-CONSTRUCTION DEFECT, WHICH IS MINE.**
`scratch/diag_cortical_hit_at_k.py` + `scratch/diag_cue_construction_one_variable.py`, 4,300
sentences, 223 consolidated terms, n=300 held-out items, ties broken AGAINST us.

| k | chance k/N | REAL | SCRAMBLE | CI-separated |
|---|---|---|---|---|
| 1 | 0.0045 | **0.0567** [0.033,0.083] | 0.0067 [0.000,0.017] | ✅ |
| 10 | 0.0448 | 0.1300 [0.093,0.170] | 0.0533 [0.030,0.077] | ✅ |
| 50 | 0.2242 | **0.3767** [0.323,0.427] | 0.2367 [0.190,0.283] | ✅ |

**Median target rank 82 vs the scramble's 108, of 223. REAL beats chance k/N at EVERY k.** *This is
retrieval, NOT discrimination -- being in a top-50 of 223 is not knowing the answer, and it must
not be upgraded into a capability claim.*

**🔧 THE ONE-VARIABLE TEST, SCALE HELD FIXED, ONLY THE CUE VARIED:**

| cue construction | median rank | hit@1 | hit@10 | hit@50 |
|---|---|---|---|---|
| **SENTENCE (`context_vector_masked`)** | 82 | ✅ sep | ✅ sep | ✅ sep |
| **PROFILE-SUM (`cortical_recall.cue_vector`, what the CELL used)** | 74 | ✅ sep | ❌ | ❌ |

**⚠️ A DEFECT IN MY OWN ORGAN, NAMED PRECISELY: the index is built from accumulated CONTEXT
VECTORS, and `cue_vector` queries it with a SUM OF PER-LEMMA PROFILES -- a different kind of
object.** The profile-sum cue is not signal-free (median rank 74 is actually the better of the
two), but **its SCRAMBLE retains far more signal** (hit@50 0.3177 vs the sentence cue's 0.2367),
which is exactly what collapses the separation the cell was testing for.
**⛔ AND THE HONEST LIMIT: SCALE IS STILL UNCONTROLLED between these diagnostics (4,300 sentences,
223 terms) and the cell (16,600 sentences, 428-480 terms). So cue construction is DEMONSTRATED to
matter and is NOT demonstrated to be the whole explanation of the void.** *The cell's own
CORTICAL_CONTEXT hit@1 of 0.0100-0.0433 brackets the profile-sum cue's 0.0234 here, which is
consistent; its SCRAMBLE of 0.0233-0.0500 against 0.0000 here is not, and scale is the open
suspect.*
**➡️ NEXT: fix `cue_vector` to query the space the index is actually built in, then RE-RUN THE CELL
AT THE CELL'S OWN SCALE with hit@k arms. Both changes are needed and only the re-run settles it.**

## 🔬 2026-08-19 -- **THE REPRESENTATION DIAGNOSTIC. THE SPACE IS NOT BROKEN AND NOT A BLOB: THE**
## **SIGNAL IS THERE ON HELD-OUT TEXT AND IS 4-7x WEAKER THAN ON READ TEXT.**
`scratch/diag_cue_vs_profile_space.py`, 4,300 sentences, 223 consolidated terms, n=200 per
condition. Measured on the VECTORS directly rather than through hit@1, with the SEEN condition as
the positive control.

| question | HELD-OUT | SEEN (control) |
|---|---|---|
| cue vs its own target | **0.0519** | 0.2551 🔴 inflated, see below: leave-one-out 0.1702 |
| SCRAMBLED cue vs that target | 0.0231 | 0.1345 |
| **gap (the void condition)** | **+0.0288** | **+0.1206** |
| cue-to-target vs cue-to-RANDOM term | +0.0318 | +0.2218 |
| argmax concentration | 112 distinct winners / 200 cues, top 7.5% | 96 / 200, top 11.5% |

**✅ THREE THINGS ARE RULED OUT.** The measurement is not broken (the control separates strongly).
The index is not degenerate -- 112 distinct winners over 200 cues, no hub. And the held-out gap is
**NOT zero**: +0.0288 real-vs-scramble, +0.0318 target-vs-random.
**⚠️ SO I MUST NARROW MY OWN VOID VERDICT. Reading (C) fired as pre-registered and the cell's
numbers remain void AS A CAPABILITY CLAIM -- that stands. But the MECHANISM is not "the route
ignores the cue". It is "the cue carries a real but very weak signal, and a top-1 argmax over 223
candidates cannot resolve +0.03".** *The scramble arm is not signal-free either (0.0231 vs a
random-term 0.0201), which is exactly why hit@1 could not separate them at n=300.*
**➡️ THIS IS THE PROGRAMME'S STANDING DIAGNOSIS ARRIVING ON A FOURTH INSTRUMENT, AND FOR THE FIRST
TIME AT THE VECTOR LEVEL: the profiles MEMORISE AND BARELY TRANSFER.** Not a retrieval bug, not a
code bug -- the representation itself.
**🔴 THE NUMBERS ON THIS LINE WERE 0.2551 READ / 0.0519 UNREAD, "a 4.9x drop". THAT SEEN FIGURE IS
INFLATED BY SELF-MATCH AND IS RETRACTED AT SOURCE. Leave-one-out gives 0.1702, so the drop is
3.3x. USE 3.3x -- see the correction block at the top of this file.**
**➡️ NEXT, AND IT IS THE DISTINCTION THIS PROJECT ALREADY ESTABLISHED: score hit@k, not hit@1.**
Retrieval dwarfs discrimination here on four corpora already; a +0.03 signal may well place the
target in the top-50 of 223 while never winning top-1. **If hit@50 is above chance, the cell was
measuring the wrong thing rather than measuring nothing.**

## 🔴 [SEE THE DIAGNOSTIC ABOVE: THE MECHANISM IS "SIGNAL TOO WEAK FOR TOP-1", NOT "IGNORES THE CUE"] 2026-08-19 -- **THE CORTICAL READ CELL IS VOID BY ITS OWN READING (C). NOT A NEGATIVE -- VOID.**
`exp_cortical_read_consolidated_v1`, 3 seeds, 1,594 s, 300 items each, 428-480 consolidated terms.
**`READING (C) route reads the cue: [False, False, False]` -- the SCRAMBLE arm (an UNRELATED donor
sentence) TIES OR BEATS the real cue on ALL THREE SEEDS.** My pre-registration says exactly what
that means: *"the route is not reading the cue and EVERY other number in this cell is void."*

| seed | CTX | SPOKE | BOTH | EPI | COOC (floor) | SCRAM |
|---|---|---|---|---|---|---|
| 101 | 0.0200 | 0.0033 | 0.0100 | 0.0000 | **0.0900** | 0.0233 |
| 20260819 | 0.0433 | 0.0100 | 0.0233 | 0.0000 | **0.0867** | 0.0500 |
| 7 | 0.0100 | 0.0100 | 0.0200 | 0.0000 | **0.0700** | 0.0233 |

*p(SCRAMBLE vs CORTICAL_CONTEXT) = 1.0000 / 0.8081 / 0.2704 -- nowhere near separated.*
**⛔ DO NOT REPORT "the cortical read scores 0.02" AS A CAPABILITY, AND DO NOT REPORT COOC BEATING
IT AS A COMPARISON.** Both are void: an arm that scores the same on an unrelated sentence is not
reading anything. The credible bar was 0.1000-0.1233 and nothing came close. *`EPISODIC_FILTERED`
reads 0.0000 on every seed -- the episodic route, restricted to consolidated candidates, never once
retrieves the right one.*
**➡️ WHAT THIS DOES AND DOES NOT SAY. It does NOT say a cortical read is impossible; it says THIS
one, on THIS task, is not reading its cue. The organ's self-tests pass on synthetic fixtures where
the families are separable, so the failure is in the REPRESENTATION the cue and the index are built
from -- accumulated context profiles -- not in the retrieval code.** *Next diagnostic, not next
build: check whether held-out cue vectors and consolidated-term profiles occupy the same space at
all before building anything else on them.*

## ⛔⛔ CORRECTION TO MY OWN CORRECTION, 2026-08-19. **I WAS RIGHT, THEN I "CORRECTED" MYSELF INTO**
## **BEING WRONG. THE BLOCK BELOW IS THE WRONG ONE. VERIFIED AT RUNTIME, TWICE.**
**`checkpoint` defaults `pbv=False`, and the substrate never passes `pbv=True`. Instrumented at
runtime: `_make_grounding_gate` fires 5 times, `_make_pbv_grounding_gate` ZERO. Refusals are
`TAUTOLOGY_NO_ANCHOR` (297) and `CLOSED_CLASS_SUBJECT` (48) -- both the OLD gate's reasons.
THE OLD GATE IS LIVE.**
**So my ORIGINAL v2 replay used the RIGHT rule, the 31.8% IS explained by anchor-field growth as
first stated, and my provenance fix went into the LIVE path all along.** *Verified: 36 of 36
successful gate decisions carried `n_anchors` + `anchor_field_sha1`.*
**🧪 AND THE THING THAT FOOLED ME: `state.gate_decisions` IS DRAINED EVERY PASS.** Peak during the
run 23, after the run **0** -- so reading it afterwards shows zero even though 36 decisions were
recorded. I read an emptied dict, concluded the branch was dead, and published a correction that
reversed a claim that had been right. **The lesson is the one I keep re-learning: I diagnosed by
READING the code and was wrong both times; both were settled in one runtime instrumentation.**
*The PBV fingerprint I added last turn sits in a path that does not execute. Harmless, left in
place with this note, and NOT to be cited as live provenance.*

## ⛔ [THIS BLOCK IS THE WRONG CORRECTION -- SEE ABOVE] CORRECTION 2026-08-19, TO THE BLOCK DIRECTLY BELOW, WHICH I COMMITTED AND WHICH IS WRONG
## **I REPLAYED A RULE THE SYSTEM DOES NOT RUN. The 31.8% is explained by that, NOT primarily by**
## **anchor-field growth, and the auditability claim below is OVERSTATED.**
**`checkpoint` runs with `pbv=True`, which selects `_make_pbv_grounding_gate` -- NOT
`_make_grounding_gate`.** The PBV gate's meaning is **`h.obj`, a STANDING HYPOTHESIS carried
across encounters**; it does **not** canonicalize at consolidation time, and its own docstring says
the summed-trace argmax is the OLD rule it replaced. **My v2 "exact" replay called `canonicalize`
on summed traces -- the retired rule. Of course it did not reproduce the live decision.**
**🧪 AND THE VERIFICATION I WROTE FOR MY OWN FIX PASSED VACUOUSLY:** it asserted "gate decisions
MISSING the new fields: 0" over **ZERO gate decisions**, because I had instrumented the dead
branch. *An absence check over an empty set. Fifth recorded instance of a checker sharing a flaw
with what it checks.*
**✅ WHAT SURVIVES, NARROWED:** the anchor field DOES grow during a pass and `canonicalize` DOES
scan it as-of-call, so a canonicalize-based decision is genuinely path-dependent. **But the live
gate's decision is MORE traceable than I said** -- `gate_decisions` already stores the full
hypothesis record: `proposed_pass`, `proposed_at_n_traces`, `n_confirm` / `n_disconfirm`, the
rejected list and the entire `hypothesis_log`. **The un-recorded quantity is narrower than "the
path": it is the ANCHOR FIELD THE PROPOSER SCANNED at propose time.**
**🔧 FIX APPLIED TO THE LIVE GATE:** `n_anchors_at_bank` + `anchor_field_sha1_at_bank` now recorded
in the PBV gate, which bounds the propose-time field from above. *Pinning the propose-time field
itself belongs in the proposer and is NOT done yet.*
**➡️ THE BUILD CONCLUSION IS UNCHANGED AND IS THE USEFUL PART: the spoke-vs-gate comparison still
cannot be made post-hoc, and must be an ONLINE arm.** It just has to be an arm on the PBV
HYPOTHESIS PROPOSER, not on `canonicalize`.

## 🔴 [SEE THE CORRECTION ABOVE -- THIS BLOCK'S CAUSAL CLAIM IS WRONG] 2026-08-19 -- **THE GATE'S DECISION CANNOT BE REPLAYED FROM THE FINAL STATE. TWO CONTROLS**
## **FAILED BEFORE THAT WAS CLEAR, AND IT IS AN AUDITABILITY PROBLEM, NOT A PROBE PROBLEM.**
`scratch/probe_gate_exact_v2.py`. v2 calls **the gate's own `canonicalize`**, on the gate's own
vector (the Library item's summed traces), with the gate's own `is_eligible_meaning` predicate and
its own `SENSE_MATCH_THRESH=0.45` -- it recomputes NOTHING. It still reproduces only
**71 of 223 decisions (31.8%)**.
**⛔ SO THE ANSWER TO v1's OPEN QUESTION IS NEITHER OF THE TWO I NAMED.** Not "the gate
underperforms its own rule" and not merely "my cosine was wrong": **THE GATE'S DECISION IS
PATH-DEPENDENT AND THE PATH IS NOT RECORDED.** `canonicalize` scans `space.anchors()` AS IT WAS AT
DECISION TIME; by the end of the read the field has grown to 273 anchors, so a replay argmaxes over
a strictly larger set than the gate ever saw. *The codebase already knew this -- `FrozenAnchorSpace`
(READ-OUT FIX 3) exists precisely so a verification episode "compares against a STABLE field instead
of a field that grew under it". I did not connect it until two controls had failed.*
**🚨 THE CONSEQUENCE IS BIGGER THAN THE PROBE. The substrate's stated output is an AUDITABLE store
of facts, and one of its central decisions cannot be re-derived from the artifact it leaves.**
Provenance records the subject, the object and the sentence -- **not the anchor field the choice
was made against.** A fact you cannot re-derive is a fact you can only take on trust.
**➡️ AND IT SETTLES THE BUILD DESIGN, WHICH IS THE USEFUL PART: THE SPOKE-vs-GATE COMPARISON
CANNOT BE MADE POST-HOC AT ALL.** It has to be made ONLINE, inside the gate, with both rules
scoring the same decision against the same field at the same moment. **That is the wiring
experiment itself, so the pre-build probe collapses into the build.** *Two failed controls were
the cheap way to find that out; building a post-hoc comparison cell would have been the expensive
way.*
**📌 SEPARATE, SMALL, AND WORTH DOING ANYWAY: record the anchor-field size (and ideally a hash of
`space.anchors()`) in the provenance row at decision time.** Cheap, and it makes every future
grounding decision re-derivable.

## ⚠️ 2026-08-19 -- [v1, SUPERSEDED BY THE BLOCK ABOVE] **A PRE-BUILD PROBE WHOSE OWN POSITIVE CONTROL FAILED. READ THE CAVEAT FIRST.**
`scratch/probe_spoke_vs_gate_on_anchors.py`, 4,300 sentences, 273 anchors, 209 scorable grounded
terms, gold = provenance-filtered ConceptNet. **Built to answer one question BEFORE wiring the
spoke into the consolidation gate: the spoke's win over the gate was measured on CO-OCCURRING
candidates, and the gate chooses among ANCHORS -- a different population, so discipline 2 says it
does not transfer.**

| arm | hits | n | precision |
|---|---|---|---|
| GATE_ACTUAL (what the gate chose) | 12 | 209 | 0.0574 |
| **CONTEXT_COS (the gate's OWN rule, recomputed)** | 20 | 209 | **0.0957** |
| SPOKE_NEAREST (the candidate wiring) | 21 | 181 | 0.1160 |
| RANDOM_ANCHOR | 0 | 209 | 0.0000 |

**⛔ THE POSITIVE CONTROL FAILED, AND I PRE-COMMITTED TO WHAT THAT MEANS.** `CONTEXT_COS` exists to
check that this probe reproduces the gate's decision; it reads **0.0957 against the gate's 0.0574**,
which is NOT the same decision. My own pre-registered text says: *"If it does not, this probe is
not looking at the gate's decision and NEITHER arm means anything."* **So SPOKE_NEAREST 0.1160 vs
GATE_ACTUAL 0.0574 IS NOT A CLEAN COMPARISON AND MUST NOT BE QUOTED AS ONE**, and the pre-committed
"wire it" trigger does NOT fire. *Also unpaired: 181 vs 209 items, because only anchors with
sensorimotor norms can be ranked by the spoke.*

**🔎 BUT THE FAILURE IS ITSELF THE INTERESTING SIGNAL, AND IT IS A HYPOTHESIS, NOT A RESULT: THE
GATE MAY BE UNDERPERFORMING ITS OWN SIMILARITY RULE.** A plain cosine argmax over the same anchors
scored 20 hits where the gate scored 12. Two live explanations and the probe cannot separate them:
(i) the gate's extra machinery -- encounter-time decision, `SENSE_MATCH_THRESH=0.45`, margin-z, a
growing anchor field -- COSTS accuracy against a plain consolidation-time argmax; or (ii) my
recomputation is simply not the gate's rule. **(ii) is the null and is the more likely of the two.**
**➡️ WHAT SETTLES IT, AND IT IS CHEAP: reproduce the gate's decision EXACTLY by calling the organ's
own `canonicalize` path rather than re-deriving cosine, and re-run PAIRED on the common subset.
Do that BEFORE any wiring.** *Do not build on a probe whose control did not bind.*

## 🟡 2026-08-19 -- **THE SENSORIMOTOR SPOKE LANDED. READING (B) FIRES: IT TIES THE TEXT CHANNEL.**
`exp_sensorimotor_spoke_grounding_v1`, 3 seeds, 4,150 s, n=327-361 scorable per seed, NOT
underpowered. Scored on the CORTICAL instrument (ConceptNet gold), bar pre-registered as
`TOP_COOCCURRENT`.

| arm | seed 101 | seed 20260819 | seed 7 | paired p vs SPOKE |
|---|---|---|---|---|
| **SPOKE_EUCLID** | 0.0699 (23) | 0.0526 (19) | 0.0703 (23) | -- |
| SPOKE_COSINE | 0.0729 (24) | 0.0582 (21) | 0.0887 (29) | 1.0000 / 0.7206 / 0.0600 |
| **TOP_COOCCURRENT** (THE BAR) | 0.0517 (17) | 0.0499 (18) | 0.0673 (22) | **0.3353 / 1.0000 / 1.0000** |
| **SHUFFLED_NORMS** (can-fail) | 0.0182 (6) | 0.0166 (6) | 0.0275 (9) | **0.0025 / 0.0080 / 0.0145** |
| RANDOM_CANDIDATE | 0.0182 (6) | 0.0194 (7) | 0.0153 (5) | 0.0010 / 0.0190 / 0.0020 |
| SUBSTRATE (the gate's own anchor) | 0.0274 (9) | 0.0194 (7) | 0.0275 (9) | **0.0155 / 0.0290 / 0.0170** |

**✅ READING (C) PASSES ON ALL THREE SEEDS: THE NORMS GENUINELY CARRY THE ARM.** Permuting every
profile onto another word, marginals preserved, costs ~2.5-3x the hits and separates at p<0.05
every time. *The channel is reading something real -- that is not in doubt.*
**⛔ READING (B) FIRES: IT IS A TIE WITH COUNTING. SPOKE is higher in 3 of 3 seeds and significant
in 0 of 3** (+1, +1, +6 hits; p 1.0000 / 1.0000 / 0.3353). **DO NOT REPORT THIS AS A WIN.** *It is
a negative FOR THIS WIRING, and it is NOT a refutation of the 0.6413 sensorimotor finding, which
was a different task, scorer and population.*
**🟢 NOT PRE-REGISTERED AND THEREFORE HYPOTHESIS-ONLY, BUT IT REPLICATES 3/3: THE SPOKE PICKS
BETTER MEANINGS THAN OUR OWN CONSOLIDATION GATE** -- 0.0639 pooled vs SUBSTRATE's 0.0248, p<0.05
every seed. *So the gate is the weaker link, not the spoke.*
**⚠️ AND MY OWN METRIC CHOICE IS REFUTED ON THE REAL INSTRUMENT. I pre-registered EUCLID as
primary off a fixture probe (synonym-vs-sibling, 1.348 vs 0.511 pooled SDs). On the actual task
COSINE scores >= EUCLID in ALL THREE SEEDS (24v23, 21v19, 29v23).** *A hand-built fixture probe
did not transfer to the instrument. The sweep is what caught it; adopting euclid would have hidden
it.* **Coverage, measured pre-filter and able to fail: terms 0.651-0.731, candidates 0.764-0.779,
~1,400-1,500 candidates removed.**

## 🛑 2026-08-19 -- **THE CORTICAL READ ROUTE IS UNWINNABLE ON THE CLOZE TASK, MEASURED BEFORE**
## **BUILDING IT. AND THE REASON IS BRAIN-FAITHFUL, NOT A DEFECT.**
`scratch/probe_cortical_route_feasibility.py`, on the read-out cell's OWN call (simplewiki,
`max_patches=1`, `consolidate_every=200`): **1,150 sentences -> 68 consolidated facts, 487
refusals. Only 18 of 300 held-out targets (6.0%) have ANY entry in the consolidated store, which
covers 2.4% of the candidate pool.**
**⛔ SO THE NEXT STEP I HAD WRITTEN DOWN -- "build the cortical read path and score it on the
read-out cell" -- WOULD HAVE PRODUCED A GUARANTEED NEAR-NULL, from having NO ENTRY rather than
from being wrong.** *Caught before the build. Third time this session that asking "could this
experiment have succeeded?" changed the plan; the first two were caught after the compute.*
**🧠 AND THE SPARSITY IS CORRECT BEHAVIOUR, WHICH REFRAMES IT:** the episodic pool holds 2,883
words while the consolidated store holds 68 -- a **42x** gap, with the gate refusing ~88%. That
IS Complementary Learning Systems: the hippocampus holds everything, cortex holds the slowly
distilled residue, and consolidation takes many repetitions. **The cortical store is not
too thin -- the CLOZE TASK IS ASKING IT ABOUT WORDS IT HAS NOT CONSOLIDATED YET.**
**➡️ CONSEQUENCE: WE HAVE TWO INSTRUMENTS AND THEY MEASURE DIFFERENT ORGANS.**
`exp_substrate_end_to_end_readout_v1` = the HIPPOCAMPAL instrument (scores episodic recall) and is
the only one wired. `exp_grounding_precision_gold_v1` = the CORTICAL instrument (scores what was
actually consolidated). **A cortical read route must be scored on the cortical instrument, or on
far more reading -- never on the cloze task.** *Do not re-derive this; the probe is on disk.*

## 🧠🔴 2026-08-19 -- **READING (e) FIRED. THE READ-OUT NEVER CONSULTS GROUNDED FACTS.**
## **AND THE BRAIN-FIDELITY NAME FOR IT: WE BUILT HIPPOCAMPUS-TO-CORTEX TRANSFER AND THEN READ**
## **THE ANSWER OUT OF THE HIPPOCAMPUS.**
`exp_substrate_end_to_end_readout_v1` spec `v3_consolidation`, 18 units, 3 seeds, 1,053 s.
**THE MANIPULATION WAS TOTAL AND VERIFIED BOTH WAYS: control grounded 38 / 68 / 112 provenance
rows, the B3-ablated twin grounded 0 / 0 / 0.** *Reading (g) checked FIRST and in code.*

| contrast | result |
|---|---|
| **consolidation OFF vs control, read-out** | **IDENTICAL in 9 of 12 cells**; the 3 that move are SEMANTIC-at-exact-key by **+0.0033 to +0.0067 = 1-2 items of 300** |
| **EPISODIC route** | **identical to 4 decimals in ALL 6 cells**, both regimes, every seed |
| `definitions` OFF | grounding falls **68->46, 112->64, 38->31** -- it genuinely feeds grounding -- and the read-out moves **EXACTLY 0.0000 in all 12 cells** |
| `gap_detector` OFF | moves nothing, anywhere |
| `foraging` OFF | **now properly rate-matched (1150/1150, 1800/1800, 750/750)** and moves **exactly 0.0000** -- the void arm is fixed and reads a clean null |
| `episodic` OFF | the ONLY organ that moves anything: exact-key **0.9467 -> 0.0000** |

**⛔ AND IT IS NOT AN INFERENCE FROM A NULL -- THE MECHANISM IS A CODE FACT, VERIFIED AT HEAD:**
`recall_sentence` -> `recall()` reads `self._epi_codes`, the episodic DG codes, and **NEVER touches
`state.store`**. `profile()` reads Library `Trace.context_vec`s plus `state.space._sums`, and
ConceptSpace is observed **only at grounding time** -- which is exactly why SEMANTIC moves by 1-2
items and nothing else moves at all. `query()` DOES address the fact store; **the scored arms do
not use `query()`.** *So the consolidated store is WRITTEN AND NEVER READ.*

**🧠 BRAIN-FIDELITY AUDIT (SHAPE / POSITION / METRIC), because the wall is a fidelity divergence:**
- **POSITION -- THE DEFECT.** CLS: hippocampus writes fast and sparse, replay transfers to
  neocortex, and retrieval of CONSOLIDATED knowledge is a **CORTICAL** read. We built the write
  (D3, one of only 5 of 38 organs that compute the brain's actual equation) and the transfer (B3,
  which fires and refuses ~87%), **and then answered every question from the hippocampus.**
  Consolidation sits DOWNSTREAM of retrieval here; in the brain it is upstream. *Position inverted.*
- **METRIC.** The cell scores cloze naming, a LEXICAL-SEMANTIC task, i.e. a cortical one. Scoring
  a cortical task through a hippocampal route is a route/metric mismatch.
- **SHAPE (secondary, named so it is not lost).** Our consolidated store is HD-bound
  `(subject, relation)` triples -- an addressable symbolic database. Cortical semantic memory is a
  distributed overlapping representation. Real divergence, but not what is costing us here.
**🔑 THIS REFRAMES THE STANDING NEGATIVE. "The store memorises and does not transfer" (exact-key
0.9333, held-out 0.0044) IS THE SIGNATURE OF HIPPOCAMPUS-ONLY RETRIEVAL** -- a pure-hippocampal
system recognises what it has seen and generalises nothing. **That is a MISSING ORGAN, not a
representational ceiling.** *And the slot table already named it: `semantic_parser` (Q1,
question -> retrieval cue) and `cortex` (Q3, accept/clarify/refuse) are BOTH NEEDS_ADAPTER. Those
two ARE the cortical read path. The ablation just proved the gap costs everything.*
**✅ CROSS-CHECK, TWO INSTRUMENTS AGREE ONCE THE WIRING IS KNOWN:** the grounding-precision cell
scores the GROUNDED FACTS directly and the substrate DOES beat random there (0.0244 vs 0.0031).
Grounding works; the read-out cannot see it.
**⛔⛔ CONSEQUENCE FOR THE PRIMARY FOCUS, AND THIS IS WHY THE ORDER WAS FLIPPED: A SENSORIMOTOR
CHANNEL FEEDS THE CORTICAL/CONSOLIDATED SIDE, WHICH THIS INSTRUMENT DOES NOT READ. Building B5
first and scoring it end-to-end here would have produced a GUARANTEED NULL, and it would very
likely have been filed as "sensorimotor does not help inside the substrate".** *That is "ask
whether the experiment could have succeeded" paying out a second time -- this time IN ADVANCE.*
**➡️ REVISED NEXT STEP: build the cortical read path (Q1 + Q3 adapters) so the consolidated store
has a reader, OR score B5 on an instrument that reads that store. Do not score B5 here.**
*Floors, recomputed per regime and NOT asserted in advance: `COOC_floor` is strongest in all six
blocks (0.0167-0.0333 held-out); `COOC_COS_floor` is far WEAKER (0.0033-0.0067). My "strongest
floor" wording was an import from another setup and was corrected before it landed.*

## 🔧 2026-08-19 LATER -- PHASE 2 RE-RUN AS A **WIRING DIAGNOSTIC**, NOT A REPORT CARD [LANDED]
**Owner authorised the recommendation in full. `SPEC_VERSION = v3_consolidation`, detached run in
flight.** *The score stays retired: best achievable on this task is 0.0300 vs our 0.0150, so
fixing every defect wins a TIE WITH A FLOOR. What is being recovered is the ABLATION CONTRASTS.*
**⛔ WHY THE OLD TABLE WAS NOT MERELY STALE BUT MEANINGLESS** (`scratch/phase2_cost_probe.py`):
`n_provenance` was **0 on ALL 30 units**, and the `definitions` / `gap_detector` ablations returned
**BIT-IDENTICAL episode counts to the control, 8,394 in every unit**. Those organs feed the
grounding path and the grounding path never ran. **"Changes exactly nothing" was the bug restated.**
**🎯 THE ONE PRE-REGISTERED QUESTION: with consolidation firing, does the read-out change AT ALL?**
(i) NO -> the read-out never consults grounded facts: a WIRING DEFECT that must be known BEFORE
building the sensorimotor channel, because that channel would be invisible to this instrument.
(ii) YES -> the ablation table is interpretable for the first time.
**✅ READING (g) ALREADY PASSES ON THE FIRST LANDED UNIT: control n_provenance 38, refusals 199.**
*The consolidation ablation binds BOTH WAYS by substrate self-test -- on: 30 rows / 91 refusals;
off: 0 / 0. An ablation asserted only by "the ablated arm grounds nothing" would have PASSED on
the broken run, which is exactly why both directions are asserted.*
**⚠️ AND A CORRECTION I MADE TO MY OWN TEXT BEFORE IT LANDED: `COOC_COS_floor` is carried as a
CANDIDATE floor, NOT declared the strongest.** The 0.0300-vs-0.0125 figure came from a DIFFERENT
setup; on this cell's own smoke cosine is WEAKER than counting (0.0 vs 0.0167 held-out). It is a
genuinely different computation, not a no-op -- checked, because the scramble control already
failed that way here.

## ⏹️ AUTOLOOP **DISARMED** BY OWNER 2026-08-19. BOTH EARLIER CELLS LANDED.
**➡️ THE COMPACTION HANDOFF AND THE PRIMARY FOCUS ARE THE FIRST BLOCK OF
`notes/BUILD_PLAN_post_audit_2026-08-19.md`. OPEN IT AND READ ONLY THAT BLOCK.**
**PRIMARY FOCUS: wire the sensorimotor norms in as a foundation asset and test whether the
substrate can USE them.**

## 🔬 GROUNDING PRECISION LANDED (3 seeds, n=398-441, NOT underpowered by the cell's own gate)
**Reading (iii) fires: the gate assigns meanings BETTER THAN RANDOM and WORSE THAN CO-OCCURRENCE.**

| arm | precision | hits per seed | paired p vs SUBSTRATE |
|---|---|---|---|
| **TOP_COOCCURRENT** | **0.0573** | 21, 26, 26 | **0.004 / 0.018 / 0.015 -- BEATS us 3 of 3** |
| SUBSTRATE | 0.0244 | 7, 12, 12 | -- |
| RANDOM_ANCHOR | 0.0031 | 1, 1, 2 | 0.069 / 0.005 / 0.011 |
| MOST_FREQUENT_ANCHOR | 0.0023 | 1, 1, 1 | 0.065 / 0.002 / 0.004 |

**So the grounding gate DOES assign meanings above chance (2 of 3 seeds at p<0.05) -- and "the word
it co-occurs with most" beats it in ALL THREE.** *What the substrate learned is co-occurrence.
Third instrument, same standing diagnosis.*
**✅ AND THE DEGENERACY IS LARGELY GONE AT SCALE: anchor diversity 0.544, top-anchor share 3.1%,
against 39 anchors for 96 terms and 17.7% earlier -- the shelf-rotation fix did that.**
**⛔ CONSEQUENCE FOR THE NEXT BUILD: any sensorimotor channel must be pre-registered to beat
`TOP_COOCCURRENT`, not merely random. Beating random is not the bar here and never was.**

## 🟢🟢 2026-08-19 -- THE BEST-CONTROLLED POSITIVE THIS PROGRAMME HAS: **THE SIGNAL TEXT LACKS IS IN
## THE SENSORIMOTOR NORMS. 0.6413 vs CO-OCCURRENCE'S 0.3067, FOUR CONTROLS BINDING.**
**Task: given 50 candidates that ALL co-occur with the target, pick the taxonomically related one.
Gold = provenance-filtered ConceptNet, no WordNet source. Word-disjoint 5-fold CV. 538 target
words.** *(All fitted -- CEILING DIAGNOSTICS, never capabilities.)*

| feature set | hit@1 |
|---|---|
| **PAIRWISE sensorimotor (11 Lancaster dims + cosine + euclid + |conc diff|)** | **0.6413** |
| co-occurrence + POS + sensorimotor | 0.6394 *(adds nothing)* |
| **CO-OCCURRENCE, every form tried** | **0.3067** |
| co-occurrence + POS | 0.2993 |
| **POS only** | **0.1022** |
| **CANDIDATE-ONLY, never sees the query** | **0.0985** |
| **SHUFFLED PAIRING, marginals preserved** | **0.0595** |

**CO-OCCURRENCE TOPS OUT AT ~0.31 HOWEVER PROCESSED** -- raw, Dice, NPMI, full 1,024-dim profile,
linear, nonlinear, supervised on the answers. **Eight scalars with a tree ensemble and the full
profile with a linear model BOTH land on 0.3104.** *The remaining 69% is not in text.*
**AND SENSORIMOTOR ALONE MATCHES SENSORIMOTOR-PLUS-EVERYTHING -- co-occurrence adds nothing on top
of it.**

**🚨 I EXPECTED AN ARTIFACT AND THE ARCHIVE TOLD ME WHICH ONE.** The 2026-08-18 sensorimotor cell
found a **QUERY-INDEPENDENT genericity score reading 0.6195** that beat every pairwise distance. My
first number was **0.6152**. *So their control ran before anything was written: candidate-only
0.0985, shuffled-pairing 0.0595, and dropping the candidate-only features IMPROVED the score.
**The pairing carries it.***

**🔓 IT RE-OPENS A CLOSED ROUTE. The SAME 11 dimensions were filed at 0.6039 against a 0.6791 bar
as "refuting THIS RESOLUTION".** *That was pairwise similarity on the dissociation instrument; on a
better-posed problem the same eleven numbers double the text-only ceiling.* **"DO NOT GENERALISE A
NARROW FAILURE TO IMPOSSIBLE" (owner, 08-11) paid out, on an asset marked closed.**

**⚠️ WHAT IT IS NOT: a mechanism. It says the INFORMATION is there and text does not have it. The
norms are SUPPLIED human ratings -- admissible (static, offline, no LLM at inference) but not
learned. One gold, one corpus, 538 words, no CI. NEXT BUILD, not next claim.**

## 🎯 THE STRONGEST RESULT OF 2026-08-19, AND IT REFRAMES THE TOP ITEM: **IT IS A RANKING PROBLEM**
**hit@k on the paradigmatic gold, 635 scorable words, 852 candidates** (`scratch/hit_at_k_ceiling.py`):

| arm | hit@1 | hit@10 | **hit@50** | hit@100 |
|---|---|---|---|---|
| BAG cosine | 0.148 | 0.417 | 0.639 | 0.735 |
| TYPED cosine | 0.134 | 0.361 | 0.567 | 0.660 |
| **RAW co-occurrence COUNT** | **0.150** | **0.510** | **0.787** | **0.846** |
| RANDOM | 0.003 | 0.030 | 0.167 | 0.277 |

**A RELATED WORD IS IN THE TOP 50 OF A PLAIN COUNT LIST FOR 78.7% OF WORDS (random 16.7%). THE
INFORMATION IS PRESENT. WE CANNOT PUT IT FIRST.** *That agrees with the one result this programme
trusts from the other direction: the fitted oracle moves AUC 0.03-0.07 -> 0.8629 ON THE SAME
COUNTS. Two independent demonstrations that the counts carry it and the READ-OUT does not.*
**⛔ SO "THE MISSING INGREDIENT IS A LEARNING SIGNAL" MUST NOT BE READ AS "THE INFORMATION IS NOT
IN THE COUNTS". The problem is DISCRIMINATION among ~50 co-occurrence-plausible candidates, with a
79% ceiling -- which is a far better-posed problem than the one we have been working on.**

**⛔⛔ TWO CLAIMS THAT WERE HERE ARE RETRACTED BY MY OWN CONTROLLED CELL
(`exp_discrimination_ceiling_v1`, 4 corpora x 150,000 sentences, paired tests):**
- **"DICE buys +31%" -- RETRACTED. 0 of 4 corpora at p<0.05, and NEGATIVE on two.** *The +31% came
  from one 1,024-word table. The smoke had warned the effect was scale-dependent; I pre-registered
  that warning and promoted the number anyway.*
- **"SECOND-ORDER cosine is WORSE than the raw count" -- RETRACTED, IT IS THE OPPOSITE: it beats
  RAW in 4 of 4 corpora.** *I called it "fifth instrument, same conclusion". It was one instrument
  at one scale.*
- **A BUG IN THAT CELL, DISCLOSED: `BAG_COSINE` and `SECOND_ORDER` are the same computation, so
  that table has THREE arms, not four.**
**✅ WHAT SURVIVES IS THE CLAIM THAT MATTERED: retrieval dwarfs discrimination on ALL FOUR corpora
-- hit@50 0.280-0.542 vs hit@1 0.078-0.136, random 0.066-0.074.** **⚠️ AND THE NUMBER MOVES: the
0.787 above is ONE corpus with an 852-word pool; at 2,400 words it is 0.280-0.542. POOL SIZE
BELONGS BESIDE IT.**

## 🧭 WHAT THE 2026-08-19 SESSION CONVERGES ON -- STRATEGIC READ, **HYPOTHESIS-PENDING-VET**
**EVERY REPRESENTATION WE OWN TIES OR LOSES TO CO-OCCURRENCE COUNTING, ON THREE INSTRUMENTS -- and
the reason may not be that we lack a teacher.**
**MEASURED THIS SESSION: 74% of taxonomically-related word pairs CO-OCCUR in the corpus. Only 26%
of words have a taxonomic relative they are never seen beside.** *So co-occurrence is not a weak
baseline a better mechanism ought to beat -- it is most of the signal text makes available.*
**That reframes the standing "the missing ingredient is a LEARNING SIGNAL" diagnosis: the residue a
teacher would have to capture is a small and genuinely hard 26%, and nothing we own -- bag, typed
slots, episodic, semantic, successor representation -- lifts it above ~0.02 on 4-7 hits.**
**⚠️ NOT A RESULT: one gold (ConceptNet), one corpus, 852 words capped by the asset's own
co-occurrence table. VET BEFORE QUOTING.** *Corollary that would change the programme if it
survives: `SET_P` -- synonym pairs with ZERO co-occurrence -- tests the rare 26% BY CONSTRUCTION.*

## 🚨 THE MOST TRANSFERABLE THING FROM 2026-08-19: **SEVEN DEFECTS, ALL MINE, ALL IN THE TOOLING, AND
## EVERY ONE LOOKED LIKE A FINDING ABOUT THE SUBSTRATE.**
1. a refusal arm that passed because the store returned NOTHING for every cue -- **pair every
   refusal arm with a binding arm**; 2. a working organ reported DEAD because my counter could not
   see the spine invoking it -- **count the artifact, not the call**; 3. a scramble control that
   was a NO-OP against a bag representation (shuffled cue tied the real cue, p=1.0000);
   4. a rate-matched twin broken **TWICE, in opposite directions**; 5. **the substrate consolidated
   only when the forager changed books, so every Phase 2 run grounded NOTHING**; 6. **25 of 28
   corpora unreachable because every read restarted alphabetically -- which produced a textbook
   LEARNING-CEILING curve**; 7. **an encoding repair that VERIFIED ITSELF WITH ITS OWN BROKEN
   DETECTOR -- fixed 9 lines, reported "0 remaining", and 56 were damaged.**
**FOUR OF THE SEVEN WOULD HAVE BEEN PUBLISHED AS SUBSTRATE FINDINGS.** *None was caught by reading
the code. Every one was caught by a control on a control, or by asking whether the experiment
COULD have succeeded before asking why it did not.*
**🔑 AND #7 GENERALISES THE WHOLE LIST: VERIFY WITH A POSITIVE CONTROL, NEVER ONLY AN ABSENCE
CHECK.** *"No mojibake found" inherits the detector's bug; "the character 🚨 is present" does not.
An absence test inherits every blindness of the thing that measures it -- which is also why
"nothing was refused", "no organ was invoked" and "no prior work found" were all wrong this week.*
**THAT QUESTION IS THE HIGHEST-YIELD HABIT
THIS SESSION FOUND -- ask it before every negative, without exception.**

## WHAT LANDED 2026-08-19 (Phases 0-3; `2e8134fd2` .. `85b146f69`)
- **PHASE 0 DONE.** `situation_reader` import **205 s -> 30.4 s** (it trained a model AT IMPORT
  TIME); its self-test now PASSES at 102.7 s where it TIMED OUT. Scratch file out of `hdlab/` and
  the registry. **The dashboard now shows `UNVETTED` instead of a blank** -- 0 blank of 14, checked
  at the rendered cell.
- **PHASE 1 DONE. `hdlab/substrate.py` EXISTS** -- the assembled reader, organs built lazily,
  every organ's use PROVEN by a call count or by the artifact it leaves. Self-test PASSES:
  400 sentences, 3,400 episodic writes, **19 facts grounded with provenance, 124 refused**.
  Slots: **9 FILLED / 6 NEEDS_ADAPTER / 8 EMPTY / 3 EXCLUDED**, reported by the object itself.
- **🚨 PHASE 2 IS THE RESULT, AND IT IS A RESOLVED NEGATIVE**
  (`data/exp_substrate_end_to_end_readout_v1/metrics.json`, 3 seeds, n=300, pool 2,114):
  **exact-key hit@1 0.9333, HELD-OUT 0.0044 against a 0.0233 co-occurrence floor whose credible
  bar is 0.0367.** **AND FEEDING IT AN UNRELATED SENTENCE SCORES THE SAME AS THE REAL ONE
  (0.0033, p up to 1.00) -- ON NEW TEXT IT IS NOT READING THE CUE.** *The same twin separates at
  p=0.0005 at exact key, which is what makes this a result and not a broken cell.*
  **THE STORE MEMORISES ALMOST PERFECTLY AND TRANSFERS NOTHING. That is ORGAN A's conclusion
  reached end-to-end through an assembled substrate on a different task and instrument.**
  **âš ï¸ SCOPE CORRECTION THAT MUST TRAVEL WITH IT: that cell ran `max_patches=1`, and the substrate
  only consolidated when the forager CHANGED CORPUS -- so EVERY Phase 2 run grounded NOTHING and
  the consolidation organ never fired. The retrieval result stands (both routes read from episodic
  writes and Library traces, which happen regardless), but re-run before quoting its ablation
  table. The smoke printed `n_provenance: 0` and I read past it.**
- **🔭 AND THE CLOZE TASK IS RETIRED AS A REPORT CARD (Director's call).** Its BEST achievable score
  is 0.0300 -- exact co-occurrence, cosine-ranked -- against our 0.0150, so **the whole prize for
  fixing every defect found is to tie a floor.** *Also measured: the `COUNT_FLOOR` our cells used
  is NOT the strongest available (0.0125 vs 0.0300), which makes the Phase 2 negative WORSE, not
  better. And the single biggest loss in the pipeline is CUE CONSTRUCTION (a full halving) -- do
  NOT cross that with the older "cue side is closed" null, which was a different scorer and
  population.*
- **🎯 REPLACEMENT TASK RUNNING: GROUNDING PRECISION vs an independent gold.** Gold built and
  admissibility CHECKED FIRST: `data/conceptnet_gold_v1`, **422,082 provenance-filtered edges, no
  WordNet-sourced edge present**, meaning relations only. *The convenient pre-extracted ConceptNet
  file carries NO provenance field and is INADMISSIBLE -- the available-tool trap in one file.*
  **FIRST RESULT: the grounding gate is DEGENERATE -- one word was the meaning of 17.7% of terms.
  A varied shelf halves that to 9.5% and anchors become meaning-like (`physics -> biology`), but a
  NEW generic attractor forms (`campus -> available`), so it is part cold-start and part
  structural.** Precision 0.0355 vs floors 0.0142/0.0071 -- **5 hits of 141, UNDERPOWERED, not a
  win.** ✅ **Self-anchoring, the 2026-08-18 defect, is 0.0% -- a genuine repair.**
- **ABLATIONS: `definitions` and `gap_detector` change EXACTLY NOTHING**, both regimes, all seeds.
  `episodic` is the organ doing the memorising (0.9333 -> 0.0000). **The `foraging` arm is VOID --
  rate-matched on the BUDGET instead of on what the live arm consumes; fix by running the live arm
  first and giving the twin its sentence count.** *Second failure of the same control in two days.*
- **PHASE 3: `hdlab/successor_representation.py`, `M = (I - gamma*P)^-1`** -- built, 7 can-fail
  self-tests PASS, **AND MEASURED AS A REAL NEGATIVE.** *I first filed it STARVED (median ONE
  observed successor per word) and named one way to settle it. **The re-test settled it against
  me.*** `exp_sr_scale_ladder_v1`, pool FROZEN, nested corpora: **across a 32x range in
  transitions per state the COOC floor TRIPLES (0.019 -> 0.058) while SR FALLS to a seventh.** At
  the top rung SR is **27 CI half-widths** below the floor -- resolved, not underpowered.
  **MECHANISM MEASURED: at gamma=0.9 the chain mixes past the cue, so at 40,000 sentences SR gives
  just 31 distinct answers to 300 DIFFERENT cues and ONE WORD TAKES 83.7%. A pinned equation
  converged into the constant floor.** *The gamma SWEEP is what made that legible; adopting one
  value would have shown neither half.*
- **AUDIT, GOOD NEWS: the no-op scramble control I built today did NOT propagate.**
  `tools/scramble_control_audit.py`, all **13,553** `.py` enumerated: **HIGH = 0**, 26 cells
  already use the correct content-destroying recipe. *A word-ORDER shuffle against a BAG scorer is
  the same vector -- it tied the real cue at p=1.0000. My own pre-committed reading caught it.*

## FOUR CONTROL DEFECTS I BUILT AND FIXED IN ONE DAY -- THE PATTERN IS THE LESSON
1. a refusal arm that passed because the store returned NOTHING for every cue -- **always pair a
   refusal arm with a binding arm**; 2. a working organ reported DEAD because my counter could not
   see the spine invoking it -- **count the artifact, not the call**; 3. a scramble that could not
   move the number; 4. **a rate-matched twin broken TWICE, in both directions.**
*Every one was caught by a control on a control. None was caught by reading the code.*

---

# â±ï¸ COMPACTION HANDOFF -- 2026-08-18 END OF SESSION. READ THIS BLOCK, THEN STOP AND ACT.
**Everything below this block is the session's working record and is 112 KB. DO NOT read it top to
bottom on recovery. This block is the entry point; the four artifacts it names are authoritative.**

## WHERE WE ARE, IN TWO SENTENCES
**The CLAIMS layer is mostly unverified: 30 vetted, 1 upheld, and 99.5% of the archive's 2,678
HARD_PASS carry neither a CI nor a null, so they cannot be checked from their own files.**
**The ORGAN layer is in genuinely good shape: 163/163 import, 83/87 self-tests pass, 0 constants
among the 13 largest -- and 67 organs are BUILT, SELF-TEST-PASSING, AND UNWIRED.**

## THE FOUR ARTIFACTS -- USE THESE, DO NOT RE-DERIVE THEM
| artifact | answers |
|---|---|
| `tools/experiment_index.py` | what exists in 8,834 cells. **Prints rows scanned BEFORE results**, so silence can never again read as absence. **REPLACES `substrate_query.sh`, WHICH RETURNS ZERO BYTES AND EXITS 0.** |
| `tools/verdict_evidence_gate.py --census` | which claims carry a CI + null (13 of 2,678) |
| `notes/VETTING_LEDGER.md` + `tools/vetting_ledger.py --cite NAME` | may I cite this, and with what narrowing attached? 1 WIRE / 12 WIRE_NARROWED / 4 RERUN_NAMED / 13 SHELVED_REFUTED |
| `notes/ORGAN_ACCOUNTING_2026-08-18.md` | what machinery works, what is unwired, what would be false coverage |

**PLAN = `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md`, SECTION 7 (prepended; read it BEFORE sec 6).**

# âž¡ï¸ THE PLAN TO EXECUTE IS `notes/BUILD_PLAN_post_audit_2026-08-19.md`. OPEN IT AND START AT PHASE 0.
**It is self-contained, owner-approved, and written for exactly this handoff.** Phase 0 is one hour
(fix `situation_reader`'s import-time training; remove a scratch file from `hdlab/`; make the
dashboard show `UNVETTED` instead of a blank). Phase 1 wires Tier 0+1 (~75 s import). **PHASE 2 IS
THE ONE THAT MATTERS: an end-to-end can-fail test with a real floor and a scramble twin, because
every organ was validated ALONE and wiring ten together is exactly how the 0-for-30 claims layer
happened.** Phase 3 builds the empty slots. The ranked list below is the same plan in summary.

## NEXT STEPS, RANKED -- START AT 1
1. **WIRE THE SIX ORGANS BOTH AUDITS AGREE ON:** `hippocampal_encoder`, `cortex`,
   `information_foraging`, `coref`, `goal_owner_select`, `definitional_extraction`. **Recovering
   built machinery beats building new machinery.** Re-run `situation_reader`'s self-test with a
   >240 s budget first (it needs 204 s just to import) and add it if clean.
   **⛔ A PASSING SELF-TEST IS NOT SUFFICIENT: `atom_consultation` passes AND has `applied`
   hard-coded `False`; `definitional_predicate_v61` passes AND fires on 0.27% of its intended
   population. BOTH SIT INSIDE THE 67. WIRE ONLY THE INTERSECTION of self-test-passing AND
   probe-FUNCTIONAL.**
2. **MINE MIDDLE_BAND, NOT HARD_PASS.** 117 meaning-relevant, never read. **Building the queue from
   HARD_PASS SELECTED FOR OVER-CLAIMING** -- two cells found this session had MIDDLE_BAND as their
   honest tier while an over-claimed sibling took HARD_PASS. **Highest expected yield in the archive.**
3. **Fix `goal_achievement`** -- the one genuine self-test failure (`AssertionError: channel
   'relation:recur' != 'majority'`), and the SAME organ the constant-probe independently flagged.
   Two methods converged; that is the strongest signal in the organ layer.
4. **Remove `_scratch_orig_goal_owner_select`** from `hdlab/` and from the registry. It is a scratch
   file counted as recoverable capability.
5. **Re-rank the remaining claim queue by ITEM-PRIORITY** (below), not by evidence-carrying.
6. **No new verdict without** a CI, a null, a declared STRONGEST floor, and a statement of whether
   the items predate the mechanism.

## THE STRONGEST PREDICTOR, AND IT IS FREE
**DID THE TEST ITEMS EXIST BEFORE THE MECHANISM DID?** Every vetting survivor was scored on items
built independently of the rule; every pass-5 refutation had detectors authored against the items
they were scored on. **It beat every statistical signal tried. Ask it first.**

## MY FOUR ERRORS THIS SESSION -- ALL ONE FAULT, DO NOT REPEAT IT
1. "No prior work found" x3 -- from a tool that returns zero bytes and exits 0.
2. "25 results landed 08-17" -- my index dated cells by **file mtime**; 60 share one bulk-touch
   minute. True count 3. Now reads `ts_iso`.
3. "1,042 never run" -- a LOCAL-DISK claim. **At least 142 had run; 15 recovered from the remote.**
4. "31 organs self-test" -> ~82 -> **87 measured.** A too-narrow regex, corrected upward twice.
**EVERY ONE WAS AN ABSENCE CLAIM MADE FROM A SEARCH INSTEAD OF AN ENUMERATION.**
*Also: I twice framed the owner's WORKING process as a defect (the remote's intentional idleness,
the deliberate SSH-back of results). **Ask what the operator intended before naming something broken.***

## STANDING CONTEXT
Remote `marsh@home` idle **BY INTENT**; results deliberately SSH'd back to this laptop. Growth
paused. Origin push needs USER AUTH. `data/foundation/` READ-ONLY, one disk, NO BACKUP. Never bundle
a deletion with real work. Never `git add -A`.

---

**ðŸ“ WHY WE KEEP PRODUCING NEGATIVES -- NOW A NUMBER, NOT A COMPLAINT (Director, inline, 08-18).
THE ANSWER TO THE OWNER'S "why aren't we narrowing in on GOOD results?" IS PARTLY THAT OUR
INSTRUMENTS CANNOT SEE A WIN AT THE SAMPLE SIZES WE RUN.**
**A floor is itself an ESTIMATE with its own error bar, so an arm must clear the floor's UPPER
bound to be credible -- not the floor's point value.** That gives a **CREDIBLE BAR**:

| instrument | n/cell | floor quoted | floor's own half-width | **CREDIBLE BAR** |
|---|---|---|---|---|
| WordNet (DSI) | 242 | 0.5431 | 0.0513 | **0.5944** |
| human (v3/v4) | 65 | 0.5943 | 0.0975 | **0.6918** |
| **arc representation (the BINDING one)** | 242 | **0.6317** | 0.0493 | **0.6810** |

**AND THAT SETTLES TONIGHT'S ARM INDEPENDENTLY OF EVERY OTHER OBJECTION: `U1_TYPED_CONTEXT` 0.6669
vs a credible bar of 0.6810 -- IT DOES NOT CLEAR.** *The retraction did not depend on this, but this
would have caught it on its own.*
**METHOD AND ITS LIMIT, STATED: Hanley-McNeil analytic SE, an APPROXIMATION. It is trustworthy HERE
because it reproduces the cells' own bootstrap half-widths -- 0.0513 vs observed 0.0516, 0.0975 vs
0.0987, 0.0493 vs 0.0481. IT DOES NOT REPLACE THE BOOTSTRAP; it is for required-n and order of
magnitude.**
**WHAT IT WOULD TAKE.** Per-cell n to tighten a floor's half-width: **±0.05 -> ~250-290; ±0.03 ->
~770; ±0.02 -> ~1,550-1,780; ±0.01 -> ~6,300-7,200.** *The human instrument runs at **65**. Getting
its bar to ±0.03 needs roughly **12x** the pairs, and its matching funnel is what caps it -- which is
why "buy n by loosening the matcher" keeps being proposed and must keep being refused: **a bigger
sample of an unlicensed instrument is worse than no sample.***
**âŒ MY STRATEGIC READ WAS "we have been running experiments that could not have returned a credible
positive, then treating the absence as evidence about the substrate." I TESTED IT IMMEDIATELY AND ON
THE HUMAN SIDE IT IS FALSE. RETRACTED, SAME SESSION, BEFORE IT COULD BE QUOTED.**
Classified all 24 human-side arms by whether their CI **upper** bound could even reach the credible
bar 0.6918: **24 of 24 CANNOT. ZERO are undetectable. EVERY ONE IS A REAL NEGATIVE.** The best arm
`F1_NO_FILTER` tops out at **0.6508** and the runner-up `T1_TYPED_ROLE` at **0.6057** -- both short
of 0.6918 *even in the most favourable corner of their own error bars.*
**SO BOTH THINGS ARE TRUE AND THE SECOND DOMINATES: the human instrument IS underpowered (it demands
>=0.69), AND our arms are so far below that the power problem does not rescue a single one.** *I
reached for an instrument-level excuse for a substrate-level result; the excuse does not survive
contact with the arm table.*
**WHERE THE POWER ISSUE GENUINELY BITES IS NARROW: arms sitting NEAR a floor -- which tonight means
exactly ONE, `U1_TYPED_CONTEXT` at 0.6669 against a 0.6810 credible bar.** *Discipline 18 is still
right and still binding; its SCOPE is "arms near the bar", NOT "our negative record generally".*
**AND THE OWNER'S QUESTION KEEPS ITS HONEST ANSWER: the negatives are mostly REAL. The instrument is
not what is holding us back -- what we are BUILDING is.**

**🚨 OVERNIGHT 08-18, AND THIS BLOCK IS MIRRORED TO YOUR BOARD SO READ IT FIRST: I HEADLINED A WIN AND
THEN TOOK IT APART. NO ARM CURRENTLY CLEARS A TRUSTWORTHY BAR.**
- **A TYPED-ROLE ARM READ 0.6669 AND I CALLED IT THE FIRST EVER TO CLEAR THE BAR. RETRACTED.** Its bar
  was computed on a DIFFERENT REPRESENTATION; rebuilt correctly, **a control containing NO WORDS AT
  ALL reads 0.6317** against that 0.6669.
- **BOTH BARS THIS PROGRAMME GATES ON INCLUDE CHANCE AT THEIR OWN n: 0.5431 CI [0.4922, 0.5953] and
  0.5943 CI [0.4937, 0.6911].** *I spent two days correcting people that "the bar is 0.5431, NOT 0.5";
  at these sample sizes THE TWO CANNOT BE TOLD APART.*
- **AN AUDIT (`37181d944`) FOUND 21 ARMS ACROSS 3 CELLS GATED THE SAME WRONG WAY -- ALL SUSPENDED, NOT
  REFUTED.** *A wrong floor makes a verdict unsupported; it does not prove the opposite.* **NOT
  programme-wide: the main write-rule ladder does it correctly.** No false positive was manufactured.
- **A VERIFIED CODE DEFECT: the prediction-error rule was applied to the BAG channel, not the typed
  one, so "prediction error doesn't help" IS RETRACTED AND THAT QUESTION IS FULLY OPEN AGAIN.**
- **THE ONE FINDING I TRUST, REACHED INDEPENDENTLY BY TWO LANES ON TWO POPULATIONS: THE TYPED CHANNEL
  WAS NEVER GIVEN ENOUGH DATA TO BE TESTED.** ~8.6 slotted observations per word spread over 10,121
  dimensions; the dense 58-dimension arm on the SAME data does not collapse. **A density sweep is
  running against branches pre-committed at `0504bfd00`.**
- **🧠 THE REFRAME WORTH KEEPING (biology, PINNED): the brain's "what is this LIKE" system (ATL) and
  its "what goes WITH this in an event" system (pMTG/TPJ) doubly dissociate. OUR INSTRUMENT IS THAT
  DISSOCIATION. WE BUILT THE SECOND ORGAN AND GRADED IT ON THE FIRST ORGAN'S EXAM.** *Grammatical
  frames CONSTRAIN a meaning hypothesis; they do not SUPPLY it -- stage one of two.*
- **UNCHANGED BELOW AND STILL TRUE:** Organ A closed, the corpus exonerated, the missing ingredient is
  a learning signal. **Tonight did not touch that; it was about what came after.**

**ORGAN A (THE WRITE RULE) IS CLOSED. ALL FIVE STEPS GATED. THE ANSWER IS A LEARNING SIGNAL, AND THE
CORPUS IS EXONERATED (`0f8a3254a`).** The substitutability signal **IS PRESENT** in first-order counts
from our own corpus: a supervised diagonal reweighting of a PPMI+SVD space reaches AUC **0.9670**
fitted / **0.9606** held-out and -- after the leakage objection was TESTED rather than waved away
(37.6% of pair-member words appear in >1 pair) -- **0.8629 under GROUP-DISJOINT, word-clean CV**
(`56175e456`, `tools/verify_ppmi_svd_oracle_group_disjoint_cv.py`). **AND NOTHING UNSUPERVISED
REACHES IT:** our five steps 0.03-0.42; vanilla PPMI **0.0519**; TUNED counts **0.1144** (shift
selected on a WORD-DISJOINT held-out set, the Levy/Goldberg/Dagan steelman, `120cfefae`); second-order
cosine 0.0510; **from-scratch SGNS 0.4417 -- BELOW its own UNTRAINED random-init control at exactly
0.5000.** *Training a neural predictor on this corpus moves it TOWARD co-occurrence.* **So: the corpus
is NOT the blocker, first-order counts CONTAIN the signal, no unsupervised transform extracts it, and
the missing ingredient is WHAT TO SUPERVISE WITH.**

**THE TRAP THAT GOVERNS EVERYTHING NEXT, and it must be stated before any build: the instrument
defines its positive set by WORDNET SYNONYMY and its known-answer arm IS WordNet (0.9599). ANY
supervision derived from WordNet TRAINS ON THE TEST. The 0.8629 fitted oracle is a CEILING
DIAGNOSTIC, NEVER a candidate build.** Drill in flight: `admissible_supervision_sources_drill`.

**METHOD RESULT WORTH AS MUCH AS THE SCIENCE: FOUR arms produced apparent CI-separated wins that their
own controls destroyed** -- max-pool, prediction-error gating (**+0.2369, a 4.3x "improvement"**, killed
by a RATE-MATCHED random gate reading 0.3007 vs 0.3079), the `C2` denominator, and the learned basis.
**Without rate-matched and identity-matched twins this session would have reported four breakthroughs
and built on all of them.** *Any arm that changes HOW MUCH gets written now REQUIRES a rate-matched
random twin.*

**ELIMINATED, each with its own control:** the basis (learned = random), the denominator (row-norm is
a cosine no-op, PROVEN by an identical wrongpool control), not-collapsing (max-pool **-0.0210 BELOW**
the sum at 55x storage; its random-occurrence control sat AT CHANCE, proving the loss is
content-specific), the filter (**a same-size RANDOM draw reads 0.5041 vs the incumbent's 0.4173 --
our stopword selection is WORSE than random**), superposition (**DOES NOT EXIST** -- each word
reconstructs from its own counts to **1.76e-08** across all 617 words), prediction-error gating, and
corpus capacity.

**SUPERSEDED BELOW BUT KEPT FOR ITS REASONING:** **DRILL 1'S CENTRAL PREDICTION IS REFUTED. `CODE` IS
EXONERATED -- TWICE (`ac629b1e7`,
`exp_writerule_learned_basis_denominator_gate_v1`).** The drill argued our store is `H^T p_a`, a random
rotation of `Sigma_yx`, and that the missing operation is factorisation `Sigma_yx Sigma_xx^-1` living
in the `CODE` slot -- so a LEARNED basis should create substitutability where a random projection
cannot. **IT DOES NOT.** `C1_LEARNED_BASIS` +0.0073 [-0.0005,+0.0150] **NOT_SEPARATED**, and
`C1_CTRL_MATCHED_RANK_RANDOM` **MATCHES IT** (-0.0060). Composition moves for NO arm, while
`C1_CTRL_FREQUENCY_SHUFFLED` moves it **+0.0858 [+0.0486,+0.1229] ABOVE (worse)** -- which PROVES the
composition instrument can see change, so the flat readings are real nulls. **"Cortex expands where we
compress" also fails:** accuracy fell MONOTONICALLY across the k sweep, 0.0553 (k=64) -> 0.0393
(k=2048). And `C2`'s one CI-separated accuracy gain is **NOT a denominator effect** -- its winning
`pool='row'` divides each row by a scalar and **cosine is provably invariant to that** (the identical
`WRONGPOOL` control is the PROOF, not a control failure); the genuine denominators (`col`,
`both`=PPMI) scored BELOW A0. **AN ELEGANT DERIVATION IS A HYPOTHESIS. This one made a specific
prediction and its own controls killed it.**

**WHAT IS ESTABLISHED INSTEAD, on TWO independent instruments.** (1) `ACCUMULATE` is the measured
INTERFERENCE source (`b6cad69ca`): the CORRECT score is STATIONARY with depth (POP_128 +0.0013
[-0.0006,+0.0034]) while the competing FIELD's mean AND p95 rise CI-separated; mean pairwise anchor
cosine 0.0127 -> 0.272; **common-mode removal does NOT help (DO-NOT-REDO 27 stays closed)** and the
interference is DIFFUSE, not top-200 words. (2) **THE DISSOCIATION INSTRUMENT IS LICENSED**
(`0eb44eb1d`) -- **the first instrument this programme owns whose FOUR FLOORS SIT AT CHANCE and are
VERIFIED there** (0.5000 / 0.4901 / 0.4664 / 0.5431, every CI including 0.5; known-answer 0.9599 vs a
0.95 gate; random store 0.4862). On it, above 0.5 = substitutability, below = co-occurrence:
`RAW_COUNT_SINGLE_OCC` **0.4173** > `PARADIGMATIC_PROFILE_WRITE` **0.2165** > `INCUMBENT` **0.0710** >
`RAW_COUNT_FULL_ACCUM` **0.0510** > `PRESENCE_ABSENCE_BINARIZED` **0.0294**; the ranking is RESOLVABLE
(max_lo 0.3835 > min_hi 0.0470). **STOP-IF (iii) fired: the incumbent is CI-separated BELOW 0.5.**

**THE ANSWER IS THE LEARNING SIGNAL, AND IT IS MEASURED (`exp_corpus_capacity_ppmi_svd_ceiling_v1`,
plan sec 6.18).** Instrument licensed by EXACT reproduction -- all 8 regression checks at **delta
0.0000**; population loaded BYTE-IDENTICAL from the instrument's own checkpoint; matrix 5,491 x 21,576,
density 0.91%, 1.82M tokens, **coverage PERFECT 242/242 in both cells**.
- **PPMI+SVD FAILS ON OUR CORPUS AT EVERY RANK -- but QUALIFIED 2026-08-18 (`96caca8de`): we ran the
  VANILLA construction (no context-distribution smoothing, no shift, no subsampling). Levy & Goldberg
  proved SGNS implicitly factorises SHIFTED PMI, and a TUNED count method MATCHES SGNS. So the honest
  claim is "UNTUNED PPMI+SVD fails", and A TUNED-COUNT ARM IS NOW MANDATORY AND MUST BE REPORTED
  BEFORE ANY SUPERVISED ARM -- if it clears 0.5 unsupervised, the supervision conclusion below is
  WRONG and the missing thing was hyperparameters.** Numbers as run: k=50/100/300/500 -> **0.0519 / 0.0285 / 0.0230 / 0.0278**, all BELOW 0.5,
  and its BEST is WORSE than our incumbent 0.0710. No k dropped for cost. **We are NOT being beaten by
  truncated SVD.**
- **A SUPERVISED LOW-RANK REWEIGHTING OF THE SAME COUNTS READS 0.8629 UNDER THE STRICTEST TEST.**
  CORRECTED, and the agent caught it before reporting clean: the landed pair-level held-out figure is
  0.9606, but **37.6% of the 617 pair-member words appear in >1 pair**, so pair-level CV leaks word
  identity across folds. Group-disjoint GroupKFold (union-find -> 148 word-disjoint components,
  `tools/verify_ppmi_svd_oracle_group_disjoint_cv.py`) gives **0.8629**. **QUOTE 0.8629, NOT 0.9606**
  -- the finding SURVIVES, clearing 0.5 by a wide margin on pairs never jointly seen in fitting.
- **SAME counts, SAME 242 pairs, SAME scorer. SUPERVISION IS THE ONLY VARIABLE, AND IT MOVES AUC FROM
  0.03-0.07 TO 0.96.** So the missing thing is **NOT information, NOT representation capacity, NOT the
  write steps** -- **IT IS THE LEARNING SIGNAL.** Every arm we have ever built is unsupervised and
  chooses what to write with no error signal about which directions matter. **Routes to the project's
  own named flavour MISSING-LEARNING -> REUSE/EXPAND the learner, never a parallel build.**
- **NEVER QUOTE 0.9606 AS A CAPABILITY.** The oracle is FITTED ON THE EVALUATION CONSTRUCT. It proves
  the counts CONTAIN the signal; it does NOT show an unsupervised or brain-plausible learner finds it.
  The live question is what supervision a BRAIN has that we do not -- not a labelled synonym list, but
  prediction error, cross-modal correspondence, consequences of use. **DRILL, NOT BUILD.**

**ORGAN A IS NOW FULLY GATED -- ALL FIVE STEPS (`f311d0ac2`, `34d3fdbab`, plan sec 6.15).** FILTER:
**REAL BUT NEGATIVE-VALUE** -- a same-size RANDOM token draw reads **0.5041, CI-separated ABOVE** the
incumbent's 0.4173. CODE: exonerated x2. ACCUMULATE: interference source. NORMALISE: not in the live
path. SUPERPOSE: **DOES NOT EXIST** -- rebuilding each word from its OWN counts alone reproduces the
incumbent to **1.76e-08 across all 617 words**; proven by reconstruction, not argued.

**RETRACTED 2026-08-18: "the operative defect is COLLAPSING OCCURRENCES INTO ONE VECTOR."** Tested
directly and **FALSE**: `M1_MAXPOOL` (every occurrence kept, scored by best match) reads **0.0299,
-0.0210 [-0.0393,-0.0020] CI-separated BELOW** the sum, at **55x the storage**. Its control decides the
reading: `N1_MAXPOOL_RANDOM_OCC` sits **AT CHANCE (0.4545)**, NOT depressed -- so the depression needs
the word's OWN occurrence content and is not an artifact of the max operator. Not-collapsing is not
the fix.

**THE ORGAN-LEVEL FINDING, AND IT IS THE REAL RESULT: NOT ONE ARM THIS PROGRAMME HAS EVER MEASURED IS
CI-SEPARATED ABOVE 0.5 ON THE LICENSED INSTRUMENT.** Everything tops out AT chance and never above it
(`N2_SHUFFLED` 0.5296 NOT_SEP, `N1_RANDOM_FILTER` 0.5041 NOT_SEP, `S1_SINGLE_OCC` 0.4173), and
everything carrying MORE accumulated corpus content sits FURTHER BELOW (incumbent 0.0710, full accum
0.0510, max-pool 0.0299, binarised 0.0294). **Interventions that DESTROY information move us TOWARD
chance; interventions that ADD accumulated content move us AWAY from substitutability.** So the
ceiling is not a step we have yet to fix -- **first-order co-occurrence counts from this corpus appear
to carry a co-occurrence signal and NO substitutability signal for these five steps to expose.** The
best any configuration achieves is encoding NOTHING.
**CAVEAT, do not collapse these into one claim:** across `ACCUMULATE` the winner no-relation rate
FALLS 0.8400 -> 0.7971 (-0.043 CI-separated) -- **adjacency was present from sentence one; a bag of
neighbours IS an adjacency record.** Summing does not CREATE adjacency; it raises INTERFERENCE and
degrades retrieval. **REPORT WINNER SHARE, GOLD SHARE AND RATIO TOGETHER, ALWAYS** (the Director once
quoted 66.0->94.4 while dropping the gold's 23.9->60.3 and the ratio, which FELL 3.967->3.822).
**LIMIT: the dissociation instrument is n=242 matched pairs, ALL NOUNS** -- verb/adj/adv strata did not
survive its frequency caliper.
**RETRACTED (VET COMPLETE, off `exp_writerule_step_ladder_v1` `COMPOSITION_DELTA_TABLE`): "summing is
what converts our store from could-replace to appears-near."** FALSE, and backwards: across
`ACCUMULATE` the no-close-relation rate FALLS 0.8400 -> 0.7971, **-0.043 [-0.0800,-0.0086]
CI-SEPARATED**. Adjacency was there from sentence one -- a bag of neighbours IS an adjacency record.
The Director quoted the winner's co-occur share (66.0->94.4) and dropped the gold's (23.9->60.3) and
the RATIO, which FELL 3.967->3.822. **REPORT WINNER SHARE, GOLD SHARE AND RATIO TOGETHER, ALWAYS.**

ONE ORGAN AT A TIME, AND THE ORGAN IS THE WRITE RULE (owner ruling 2026-08-18, `PLAN_ORGAN_STEP_LADDERS`
sec 6.7). The cue side is finished and did not fix the reading; four cells changed the QUESTION we hand
the store and every one improved FINDING THE DRAWER while none improved READING WHAT IS IN IT
(binarising takes addressing 0.0711 -> 0.1094 while hit@1 moves 0.0223 -> 0.0249, +0.0026
[-0.0026,+0.0078] NOT_SEPARATED -- ADDRESSING AND READ-OUT ARE SEPARATELY CAPPED).
**THE DECISIVE WRITE-RULE MEASUREMENT, and it is why this organ is the one:** varying ONLY the target's
own stored row, `SUM_ALL` reads **0.0100**, ONE occurrence picked at RANDOM reads **0.0367**, and
`BEST_SINGLE_ORACLE` reads **0.3033** against the **0.1390** floor we have never cleared. *Summing is
worse than not summing, and individual sentences already carry enough to clear the floor.* The oracle
is a CEILING DIAGNOSTIC, never a capability. **DEPTH IS RETRACTED (sec 6.6): "+0.0503 still climbing"
was an ORACLE-CUE number; on the REAL partial cue POP_72 32->72 is BELOW and POP_128 is NOT_SEPARATED,
with winner composition FLAT at every depth.** Eleven cells across six organs on 08-17 returned ~+0.01
each; the two LADDERS redirected the programme. Method is not in question -- organ selection was.

## [ARCHIVED TOP ITEM] FIND AN ADMISSIBLE SUPERVISION SIGNAL THAT IS NOT THE EVALUATION GOLD
*(renamed 2026-08-20: it is no longer the top item, and while it carried the literal `## TOP ITEM`
buried at line ~2292 it was competing with the current one for the machine parse. Content intact.)*
**🆕 2026-08-19: THE FIRST CANDIDATE IS BUILT AND UNDER TEST -- D7 SUCCESSOR REPRESENTATION**
(`hdlab/successor_representation.py`). **It clears the circularity constraint outright: it is
self-supervised from the corpus's own transitions and derives from NO gold, NO WordNet, NO LLM.**
Full run in flight; **the pre-registered risk is that it is a better COUNTER rather than a
different kind of thing**, since `M` is a discounted multi-step co-occurrence statistic and the
floor is the 1-step one. *Phase 2 independently re-confirmed that the missing ingredient is a
learning signal, end-to-end through the assembly -- see the 2026-08-19 block at the top of POSITION.*

Organ A is closed and its answer is that we need a LEARNING SIGNAL. **The whole question is now WHICH
ONE, and the binding constraint is CIRCULARITY, not performance.**
**VERIFIED OFF DISK 2026-08-18, not asserted** (`exp_dissociation_score_instrument_v1.py`):
`SET_P` is built by `build_wordnet_synonym_candidates()` (line 304) from `wn.synsets()` (line 312);
the known-answer arm is WordNet path similarity (0.9599); and `SET_S` **explicitly EXCLUDES any
WordNet pair even at high co-occurrence** (evidence key
`set_S_excludes_wordnet_pair_even_at_high_cooccurrence`, line 674). **So WordNet does not merely
influence the labels -- it DEFINES both sides of them.** Therefore **any signal derived from WordNet --
synonyms, hypernyms, glosses, or anything computed from them -- trains on the test and is UNUSABLE AS
SUPERVISION however well it scores.** Second constraint, the
owner's invariant: **NO LLM in the operational path**, and a pretrained table is disqualified as a
MEANING SOURCE (ceiling reference only) -- **but a STATIC OFFLINE-BUILT ASSET IS ADMISSIBLE** (owner
Q3: *"we can build that foundation however we want, as long as it is a strong foundation, and the
operation is not llm"*). Do not hold us to a stricter standard than the brain meets.
**IN FLIGHT:** `admissible_supervision_sources_drill` -- biology first (what supervises cortical
semantics, and what the prediction-error NULL does and does NOT rule out: it tested error against the
word's OWN accumulator, which is not error against ANOTHER MODALITY or a DOWNSTREAM CONSEQUENCE);
then an **on-disk enumeration by `os.walk`, never registry-first** (a 1.21M-edge CSKG read by nobody
live -- **check whether it CONTAINS WordNet before trusting it**; OpenStax 117,642 sentences;
Brysbaert concreteness; Warriner VAD; Binder; UD parses); then a ranking on brain fidelity /
independence-from-gold / coverage on the 617 matched-pair words / no-LLM survival; then ONE build
with a mandatory rate-matched control.

## SUPERSEDED TOP ITEM -- THE WRITE RULE WAS THE FIRST THING TO MOVE READ-OUT (LESSONS: WRITE RULE)
`exp_readout_writerule_paradigmatic_v1` (full, `a8fdc968f` / `24ca42661`) rebuilt the STORE so a
word's code sums its neighbours' own context PROFILES instead of their arbitrary identity tags, and
left the comparator untouched. `W1_PARADIGMATIC` **0.0298** vs `W0_SYNTAGMATIC` **0.0223**: **+0.0075
[+0.0023,+0.0128]**, half-width 0.00525, analytic null half-width 0.00458, **ABOVE** (~34% relative).
A frequency-matched profile control reads 0.0225 and does NOT beat W0 (+0.0002 NOT_SEPARATED); a
random-profile null reads 0.0188 and does not either (-0.0035 NOT_SEPARATED -- lower, not separated);
three hybrid alphas all land +0.0065..+0.0070 ABOVE; K1 addressing 1.0000 on all seven arms;
orthographic leakage flat at W0's own value. **NO STOP-IF FIRED CLEANLY** and the cell wrote the
honest fourth reading itself: *the write rule was PART of the defect but is not sufficient* -- W1 is
still **-0.0575 [-0.0673,-0.0478] BELOW** its own binding floor (orthographic 0.08731), 2.9x short.
**THE CONTRAST IS THE FINDING: the read-out scoreboard's ~39 prior arms ALL changed the COMPARATOR
and none beat the incumbent CI-separated; this one changed the WRITE RULE and did.** `wire_status` is
`VET_PENDING` -- WIRE-or-SHELVE not decided.

## CUE SIDE -- CLOSED IN FOUR CELLS (LESSONS: CUE SIDE CLOSED; DO-NOT-REDO 44, 45, 46)
(1) PLAN ITEM 3 landed a CLEAN NULL (`2e5a467ae`): `A0_FLAT` reproduces item 1's 0.0849 target
exactly (regression gate PASS), `T1` key-sparsified 0.0704 = **-0.0145 [-0.0203,-0.0088] BELOW**,
`T2` cue-sparsified 0.0886 is the grid's raw MAXIMUM yet **+0.0037 [-0.0013,+0.0088] NOT_SEPARATED**,
T2 vs T1 +0.0182 ABOVE, oracle 1.0000 and random 0.0000 both passing. **Stop-if (i) fired. The cell's
own verdict: "Neither, cleanly" -- no arm beat the flat store and the sparsified arms LOST accuracy
rather than matching it more cheaply.** `C1` vs `T1` is bit-identical 0.0 [0,0] BUT CARRIES A
CONSTRUCTION CAVEAT: K=32 exceeds the cue's own median nnz of 12.0, so that truncation is a no-op for
most items and the tie is partly an artifact. (2) COMPRESSION DIAGNOSED (`201776cc9`): what matters
is PRESENCE, not counts -- the losing property is MAGNITUDE, not sparsity and not non-negativity.
`B1_BINARIZED_RAW` (presence only, uncompressed) +0.0383 [+0.0293,+0.0476]
above the incumbent and +0.0248 [+0.0160,+0.0338] above raw counts; S1 -0.0100 BELOW, N1 -0.0003
NOT_SEPARATED. Loss is CONCENTRATED: the 93 lost items have shorter cues (10.80 vs 12.48) and much
sparser store profiles (106.4 vs 210.8), both CI-separated. (3) IT DOES NOT TRANSFER (`1e085d761`) --
see POSITION; R2 (binarised THEN projected) gives back two thirds of the addressing gain, so **the
two defects are not independent**. (4) THE BASIN THEORY IS REFUTED -- see CLEANUP.

## PHASE DIAGRAM -- THERE ISN'T ONE (LESSONS: PHASE DIAGRAM)
`substrate_phase_diagram_recovered_from_experimental_history_2026-08-17.md` (`32cc8ce71`), enumerated
from the filesystem: 7,804 `metrics.json` (re-walked 7,807, delta = this session's own files, nothing
missing); ~59 vary dimensionality, ~21 sparsity, 2 expansion; **23 of 42 parameter-by-operation
squares NEVER MEASURED**, 13 usable, six diagrams on six scorers that may NOT be merged. The "55-65%
coverage" recollection traces to `director_TRUE_PHASE_DIAGRAM_COVERAGE_2026-06-30.md`, whose own line
items say ~10% and <5%. Q13's sparsity sweep has NO cell under `data/` -- it is in gitignored
`scratch/sparsify_right_object/`; promote before the next clear. **Its d-sweep row is corrected by
C36.**

## BRIDGING -- TWO MEASURED NULLS (LESSONS: DO-NOT-REDO 38, 43)
Phase 2 FULL: B1 rho 0.0270 n=394 vs floors 0.0412/0.0317/0.0905, NOT_SEPARATED, perm p 0.30, both
known-answer arms ABOVE (K1 0.3301, K2_ORACLE 0.2893); bridged codes KEEP IDENTITY (96.12% distinct)
and LOSE MEANING (retention 0.0819); the curated CSKG arm fails too. SELECTIONAL-CONSTRAINT
BRIDGING, the owner's own mechanism, is the SECOND and worse null: -0.1049 [-0.2041,-0.0057] BELOW
the incumbent, -0.0015 NOT_SEPARATED from a random target, instrument alive (K1 0.3311). KILL
STATUS: withdrawn for thematic, re-worded for selectional, per HANDOFF 8b(B) -- whose numbers remain
NOT re-verified by any pass.

## STORAGE -- THE WRITE/READ ASYMMETRY IS REAL AND DID NOT SURVIVE AS A WIN (LESSONS: WRITE/READ ASYMMETRY)
`exp_sparse_address_dense_value_v1` (n=3994, own floors): best partial-cue addressing anywhere is
0.0719 at a DENSE address; a 1%-occupancy address (82 of 8192 units) read with a DENSE cue matches
it at 0.0699, CIs overlapping; read SYMMETRICALLY it is 0.0483, 1.45x worse; the dense read wins 18
of 24 matched pairs, max 6.27x. **RE-TESTED 08-17 on the UNCOMPRESSED base, where it is a DIRECTION
AND NOT A WIN: T2 (cue sparsified) beats T1 (key sparsified) +0.0182 CI-separated, but T2 does not
beat the flat store (+0.0037 NOT_SEPARATED).** C36: the d-sweep line "0.0711 -> 0.0716 at 8192" mixes
read regimes; matched at `a_read=1.0` it is 0.0711 / 0.0714 / **0.0709** -- 32x the memory buys less
than nothing, so the conclusion strengthens.

## CLEANUP / SURPRISE / TARGET SPACE (LESSONS: CLEANUP MEMORY, SURPRISE, TARGET SPACE)
**AND THE BASIN EXPLANATION FOR THE CLEANUP NULLS IS REFUTED (`exp_cleanup_basin_conditional_v1`,
landed 08-16 22:41, UNREAD BY ANYONE FOR ~14 HOURS).** Six tau strata summing to 3994, known-answer
arm 1.0000 in every one: lift is CI-separated ABOVE **only in the LOWEST-tau stratum** (+0.0036
[+0.0009,+0.0072]) and NOT_SEPARATED in every higher one **including the highest** (+0.0154
[-0.0039,+0.0347]) -- the OPPOSITE of what basin theory predicts and of what the cell pre-registered
as confirming. It licensed skipping an elaborate settle mechanism, and the one cheap settle arm run
anyway is null (-0.0010 [-0.0025,+0.0003]). **AN UNREAD RUN IS A RUN THAT DID NOT HAPPEN -- second
instance in two days.**
CLEANUP MEMORY IS REAL, NOT INERT (fixed points 1.0000, idempotent, capacity on VSA's own d/log d
scale): first measured lift, +0.0033 and +0.0078 CI-separated in 2 of 3 pools, every arm still
-0.1135 BELOW the binding constant floor -- which makes the FIVE BANKED CLEANUP NULLS STRONGER, the
load-bearing half was NOT missing. SURPRISE-WEIGHTING: clean null, named cause -- signal DEGENERATE
(median 0.875 where 1.0 is orthogonal), selection beats a token-matched random subset in 4 of 18
comparisons, residual rule a near-no-op (cos 0.9771 to uniform) = the PRE-REGISTERED bootstrapping
problem. TARGET SPACE: affect +0.1013 is a CEILING DIAGNOSTIC, no floors, no null, clears nothing;
its verb half is now MEASURED, not suspended (C33).

## TOOLING STATE (LESSONS: VERDICT BAR, SKIPPED FULLS, C31, C32)
Corrected base rate: 7,789 enumerated, MEETS_BAR **1** (`exp_cue_to_store_translation_v1`), FAILS
7,770, NO_EVIDENCE 18; 238 flagged cells ARE cited by an index -- OPEN OPERATOR DECISION, NOT TAKEN.
The one pass is rejected on four grounds (pool admits a fitted constant 0.7354 vs chance 0.0625;
exact-key is not the operating point; the cell declines a verdict; margin overstated 4.20x).
`verdict_bar_check.py` HAS FALSE-PASSED FOUR TIMES -- run it, NEVER rely on its verdict, state
arm-by-arm margins; it also returns NO_EVIDENCE on any cell whose arms are nested per-stratum
(ITEM 2's). Only 12 of 7,789 cells ever recorded a constant floor, so every historical bar decision
used a THREE-floor max. `matched_candidate_sets` WAS VOID and is rebuilt; `eligB` still suspect.
FOUNDATION v4 ~49% (`d62acfe58`); TRIAGE -> `RECOVERY_PROGRAM.md`.

## [ARCHIVED 2026-08-19] RUNNING / BLOCKED -- STALE, SUPERSEDED BY `## WHAT IS RUNNING` AT THE TOP
*(renamed 2026-08-20. This copy carried the machine-parsed literal `## WHAT IS RUNNING` while
sitting under 2,300 lines of archive, so it -- not the current state -- was injected into every
compaction recovery for a full day. Both runs named below FINISHED on 2026-08-19. Content intact.)*

- **🟢 AUTOLOOP IS ARMED (owner, 2026-08-19: "enable your stop hook and make sure it's working
  properly"), 26 continuations in.** Stop it with `python tools/autoloop.py disarm`. Anything
  other than exactly boolean `true` in `data/hook_state/autoloop.json` reads DISARMED -- the
  fail-safe direction is OFF. *Both `stop_hook.py --self-test` and `autoloop.py self-test` PASS.*
  **⚠️ THIS BULLET SAID "DISARMED" FOR ~20 CONTINUATIONS AFTER THE LOOP WAS RE-ARMED.** This
  section is MACHINE-PARSED by `tools/session_start_hook.py`, so a resuming session was being told
  the loop was off and the wrong cell was running. **A stale `WHAT IS RUNNING` is worse than an
  empty one -- it is confidently wrong. Update it in the same turn as the launch, not later.**
- **🔵 IN FLIGHT (2 detached, they CONTEND so both are slow -- that is expected, not a stall):**
  - **9-seed spoke independence sweep** -- `scratch/spoke9.log` / `.err`, PID `scratch/spoke9.pid`.
    Decides whether the spoke's independence from counting is real or a small-count artefact.
    **3 of 9 seeds in and reproducing the earlier run EXACTLY (0.70 / 0.94 / 0.89).**
  - **`exp_predictive_write_gate_v1`** spec `v1_residual_gate`, 3 seeds -- `scratch/pwg_full.log`
    / `.err`, PID `scratch/pwg_full.pid`. The pinned residual rule against pure accumulation,
    **with a rate-matched RANDOM_SKIP arm and the threshold SWEPT, both in from the first draft.**
  **DO NOT RESPAWN EITHER.** *Neither writes an artifact until a whole unit lands, so mid-unit the
  only progress signal is the CHILD process's CPU -- never the shim PID's, which reads 0 s on a
  healthy run.*
- **✅ LANDED AND SUPERSEDED: `exp_cortical_read_consolidated_v1`.** v1 was VOID (cue-construction
  defect), v2 fixed the cue, **v3 (`v3_floors_at_k`) is the final word: retrieves, NOT competitive,
  0 of 18 floor cells.** *Its first full run also died on corpus arithmetic -- `simplewiki` yields
  exactly 20,000 sentences and it read all of them, leaving an EMPTY held-out split. That is now a
  CLAUDE.md rule, because the smoke used 2,000+360 and could not have caught it.*
- **✅ LANDED 2026-08-19 12:25Z: `exp_substrate_end_to_end_readout_v1` spec `v3_consolidation`,
  18 units in 1,053 s, 30 older-spec units excluded from the report. NOTHING IS RUNNING.**
  Result and its brain-fidelity audit are the first block of ## POSITION. Read it with
  `scratch/read_v3_result.py`, which reads the pre-committed readings in their own order.
- **[SUPERSEDED -- IT LANDED] IN FLIGHT: `exp_substrate_end_to_end_readout_v1` FULL, spec `v3_consolidation`.** 18 units
  (3 seeds x 6 ablations: control / episodic / definitions / gap_detector / **consolidation** /
  foraging). Detached; shim PID in `scratch/readout_v3_full.pid`, logs
  `scratch/readout_v3_full.log` / `.err`. Read progress with `scratch/peek_v3_units.py`.
  **DO NOT RESPAWN IT** -- a duplicate is the more expensive error.
  **⚠️ THE SHIM PID IS NOT THE WORKER: `.venv/Scripts/python.exe` spawns the real interpreter as a
  CHILD and then idles, so the recorded PID reads 0 s CPU on a perfectly healthy run.** Judge
  progress by `units.jsonl`, or by the child via
  `Get-CimInstance Win32_Process -Filter "ParentProcessId=<pid>"`.
  *Unit keys carry `SPEC_VERSION`, and v3 additionally FILTERS `load_units` at assembly time --
  the bump protects the compute, the filter protects the report. Without it the 30 dead-grounding
  v2 units would have been folded into the new metrics and fired the gate on a run that worked.*
- **â“ Q66 OPEN AND WORKED AROUND, NOT BLOCKING: `hdlab/ca3_completer.py` IS UNTRACKED IN GIT.**
  23 KB, on the Tier 1 wire list, **zero git history to recover from**; any checkout/reset/clean
  destroys it. My recommendation is on the board: commit it alone, in a commit that states the
  authorship is not mine. *I have not done it -- committing another session's in-progress work
  under my name is the thing I declined to do for Q52.*
  **✅ CLOSED 2026-08-19, `f102e7081`. COMMITTED ALONE, 444 lines, nothing bundled.** Verified
  before committing: imports cleanly, carries 5 named self-tests. **Flagged as an owner decision
  twice and passed back twice; the third time it was made, because the commit is protective and
  reversible and the alternative was leaving a 23 KB organ one `git checkout` from deletion.**
  *Slot D2 remains NEEDS_ADAPTER -- it consumes FHRR bundles plus per-spoke codebooks and the
  ingest path produces neither. The commit protects the FILE; it does not WIRE the organ.*
- **📋 BOARD TRIAGE -- 12 OPEN, BUT ONLY 5 NEED YOU. SEVEN ARE ONE FAULT AUTO-FILED SEVEN TIMES.**
  **Q47, Q48, Q53, Q54, Q55, Q57, Q58 are all the SAME `rm`-bundling denial** -- the loop files a
  board question per denial, so a recurring fault floods the board. **I verified two of them touched
  no result** (the deleted paths were a smoke directory and a log truncated by `>` anyway) and the
  rest are the same shape. **Q49 asks the one policy question they all reduce to; answering Q49
  disposes of all seven.** *Read them as one item, not seven.*
  **THE FIVE THAT ARE REAL, in the order I would take them:**
  1. **Q52 -- 844 uncommitted insertions across 10 experiment files that are NOT mine**, last
     modified 2026-08-17, existing only in the working tree. **Any reset/checkout/worktree op
     destroys them.** I did not touch them: committing a concurrent session's in-progress state
     under my name would be wrong either way. *Highest consequence on the list.*
  2. **Q51 + Q56 (one issue, evidence added) -- 3,894 watchdog files, 31% of `notes/`, still
     arriving every 10 min from the DEAD four-session fleet.** **Now MEASURED, not hypothesised: a
     plain `find` over `notes/` TIMED OUT at 300 s tonight**, and the same cost hit the supervision
     drill and two agents. Cheapest performance fix in the repo. *Disable the task first, then
     clear; otherwise it refills at 6/hour.*
  3. **Q50 -- `CLAUDE.md` tells every session to open by running a tool that returns ZERO BYTES and
     exits 0.** I flagged it in this file but did NOT edit the conventions file unprompted.
  4. **Q49 -- keep halting the loop on the `rm` fault, or log-and-continue?** *My recommendation is
     KEEP HALTING and fix the cause; it is the only thing that reliably catches dropped
     preconditions, and it caught them tonight.*
  5. **Q16 / Q17 (older) -- build a word-onset channel? is that blocked file path deliberate?**
  **Nothing on this list blocks the science.** All four research lanes ran to completion or are
  still running.
- **âš ï¸ THE BAR IS `max(four floors)` = 0.5431 ON THE LICENSED INSTRUMENT, **NOT 0.5**. CHANCE is 0.5;
  the BAR is 0.5431 (the constant/prototype floor). Sections of this file below still say "above 0.5
  = substitutability" -- **that describes CHANCE, not the GATE.** No conclusion flips (every arm sat
  0.03-0.44, far below both), but **any future arm must clear 0.5431**, and the Director spent a night
  describing 0.5 as the target. Corrected in `PLAN_ORGAN_STEP_LADDERS` 6.29.
- **✅ THE HUMAN INSTRUMENT IS LICENSED (`f792c3ab8`, v3, THIRD attempt). n=7 -> 65 per cell.**
  Frequency-STRATIFIED matching -- bin each POS stratum's frequency into 3 quantile bins, then run
  the UNCHANGED matcher inside each (POS, bin) cell. **All four floors CI-include 0.5;
  `max(four floors)=0.5943`** (higher than the WordNet instrument's 0.5431). Known-answer is the
  **published human rating**, NOT WordNet -- its AUC 1.0 is **tautological plumbing, not a result**.
  **All seven arms scored AT OR BELOW CHANCE on human judgements** (INCUMBENT 0.2265, SINGLE_OCC
  0.4644, PARADIGMATIC 0.2788) -- the same qualitative picture WordNet gave.
  **THE DECIDING NUMBER IS INCONCLUSIVE, on the PRE-COMMITTED branch: rho = 0.7857 between the two
  instruments' arm orderings, permutation p = 0.048, BUT bootstrap-of-arms 95% CI = [-0.0439, 1.0],
  WHICH INCLUDES ZERO. The 6.24 WordNet caveat REMAINS OPEN.** *rho 0.79 is NOT agreement; the wide
  CI is NOT disagreement.*
  **THE POWER LIMIT MOVED TO THE ARM COUNT.** The bootstrap resamples **ARMS, not pairs** -- 7 items
  cannot give a tight CI however good each AUC is. **Fix = MORE ARMS, not more pairs.** *In flight:
  `arm-expansion`, harvesting the 20+ store variants already built tonight and scoring them on both
  instruments.*
  **CAVEAT THAT TRAVELS WITH EVERY v3 NUMBER:** post-match balance is materially WORSE than its
  sibling's (`mean_log_freq` -0.4382 vs -0.0416; `mean_length` 0.3988 vs -0.0121). **Floors pass,
  which is the gate -- but this instrument is LOOSER.** And absolute AUCs are **NOT comparable across
  the two instruments; only the ORDERING is.**
- **SUPERSEDED: HUMAN INSTRUMENT v1/v2, BOTH `POWER_INSUFFICIENT` AT n=7 (`6976f08ca`).**
  v2 used the FULL 5,491-anchor set and got the SAME n=7 as v1 -- **which disproves the Director's
  own diagnosis.** *I claimed v1 collapsed because I restricted it to the WordNet instrument's 617
  words; v1's checkpoint diagnostics show that restriction NEVER EXISTED. Plan 6.30 is RETRACTED by
  6.33(B).* **The real cause: a structural frequency gap between the human-labelled sets (pre-match
  SMD on `mean_log_freq` = -1.8396) colliding with the WordNet-tuned caliper (0.02), which drops
  429 of 436 candidates. Adjective and noun strata yield ZERO matches; the 7 survivors are VERBS.**
  **So the blocker is the MATCHER, not the population** -- and loosening the caliper stays forbidden
  because it would unlicense the instrument. **The 6.24 WordNet caveat REMAINS OPEN.**
- **0.8629 IS VERIFIED AND NOW HAS AN ARTIFACT (`dfc84429a`).** Spot-checking found the night's most
  load-bearing number lived ONLY in prose -- zero hits in the capacity cell's `metrics.json`. Its
  script was committed, so reproducible not fabricated. **Re-ran: group-disjoint 5-fold CV AUC
  0.8629, pair-level 0.9587, both exact.** Log at `notes/groupdisjoint_verification_log_2026-08-18.txt`.
- **🚨🚨🚨 THIS DOCUMENT HAS BEEN DESCRIBING A TINY, ACCIDENTAL SLICE OF THE PROJECT. THE OWNER SAID
  SO AND THE INDEX PROVES IT. TREAT EVERY "WE HAVE NEVER" AND "NOTHING REACHES" CLAIM BELOW AS
  UNVERIFIED UNTIL RE-CHECKED AGAINST `tools/experiment_index.py`.**
  Measured 2026-08-18 off the newly built index (8,834 cells, 7,570 with verdicts):
  **2,678 HARD_PASS** (June 323 / July 2,193 / August 162), 1,369 HARD_FAIL, 1,068 MIDDLE_BAND.
  Excluding substrate-physics cells (capacity, scaling laws, binding, Hopfield), **236 HARD_PASS are
  MEANING-RELEVANT** -- June 14 / July 182 / August 40.
  **🔴 RETRACTED WITHIN THE HOUR BY THE VET (`a2e65896`): "25 HARD_PASS LANDED 2026-08-17" IS FALSE.
  THE TRUE COUNT IS 3, AND THE ERROR WAS MY OWN TOOL.** `experiment_index.py` dated cells by the
  metrics.json **FILE MTIME**. **Exactly 60 metrics.json share the minute 2026-08-17 17:44 and 3,850
  share 2026-07-03 14:28 -- BULK TOUCHES, NOT RUNS.** Their internal `ts_iso` says the six I vetted
  actually ran **2026-07-17 to 07-23**, and ZERO ran on 08-17. *A file's mtime is when it was last
  WRITTEN, not when the science happened; any copy, checkout or sync rewrites it.* **FIXED: the index
  now reads `ts_iso` first and records `date_source` per row.** *I told the owner we had ignored 25
  results the day after they landed. We had not. The July work was resurfaced by a touch.*
  **âš ï¸ AND THE FIX IS ONLY PARTIAL, SO DO NOT TRUST RANKING BY DATE YET: of 7,794 landed rows only
  **2,538 carry a `ts_iso`**; **5,256 STILL FALL BACK TO MTIME**. Two-thirds of the archive has no
  trustworthy run-date at all.**
  **[SUPERSEDED CLAIM, KEPT VISIBLE] "25 HARD_PASS landed 2026-08-17 and this document mentions none
  of them."** Among the cells named:
  `exp_read_grow_openvocab_fastmap_v1` (**learn NEW words WHILE reading instead of abstaining**),
  `exp_read_grow_oov_verb_extension_v1`, `exp_read_grow_foundation_realprose_glassbox_ie_v1`
  (*"THE SUBSTANTIVE READING STEP"*), `exp_online_knowledge_condenser_selectional_v1`
  (**condenses generalizable knowledge as it reads**), `exp_role_filler_factorization_compgen_v1`
  (brain-faithful structure-content factorization), `exp_three_factor_eligibility_distal_credit_v1`
  (**a three-factor eligibility trace solving DISTAL CREDIT ASSIGNMENT**),
  `exp_reward_contingency_credit_assignment_v1`, and
  `exp_relational_vs_similarity_conflict_viability_probe_v1` (**GREEN_LIGHT_PENDING_VET -- the
  taxonomic-vs-thematic conflict**).
  **THE MOST EMBARRASSING SPECIFIC: I SPENT 2026-08-18 CONCLUDING "THE MISSING INGREDIENT IS A
  LEARNING SIGNAL" AND "WE HAVE NEVER BUILT THE TAXONOMIC ORGAN". A THREE-FACTOR LEARNING RULE AND
  A RELATIONAL-VS-SIMILARITY PROBE BOTH HARD_PASSED THE PREVIOUS DAY, AND
  `hdlab/random_indexing.py` -- AN EARNED DISTRIBUTIONAL ORGAN -- HAS EXISTED SINCE 2026-08-06.**
  **âš ï¸ THE DEFLATION, AND IT IS NOT OPTIONAL: A HARD_PASS IN THIS PROJECT IS A CLAIM, NOT A
  CAPABILITY.** Five apparently clean wins died to their own controls in ONE session on 08-18, one
  of these 25 is explicitly `PENDING_VET`, and this file already records 21 arms suspended for a
  mis-imported bar. **THE CORRECT STATEMENT IS: A LARGE BODY OF CLAIMED POSITIVE RESULTS EXISTS THAT
  OUR POSITION DOCUMENT IGNORES, AND IT NEEDS VETTING -- NOT THAT WE HAVE 2,678 WINS.**
- **🟢🟢 VETTING PASS 5 (`ae41755a`) -- *** THE FIRST UPHELD RESULT IN 30 VETTED CELLS. ***
  1 UPHELD, 2 QUALIFIED, 1 SUSPENDED, 2 REFUTED.**
  **✅ UPHELD -- `exp_agreement_depth_productivity_generalization_v1`. IT GENERALISES, AND THE SPLIT
  IS ASSERTED IN CODE.** A learned function-word accumulator **supervised ONLY on depth<=1**, tested
  on **2,597 HELD-OUT depth>1 Linzen items: 0.7324 [0.7154, 0.7494]** against the strongest floor
  ACTUALLY RUN (majority 0.5741, upper bound 0.5931) -- **margin +0.1223 READ FROM THE CI LOWER
  BOUND.** Still holds out-of-distribution at **depth 4+: 0.6810 [0.6462, 0.7111]** vs majority
  upper 0.5751. Real seed spread (not one measurement printed n times); scramble drops 0.2947 and
  changes 86.5% of decisions; five filters removed 350 / 289 / 518 / 9,887 / 7,122 items, so the
  controls BIND. No LLM on the path.
  **âš ï¸ ITS HONEST CEILING, STATED BY THE AUDITOR AND NOT TO BE DROPPED: IT *TIES* THE HAND-WRITTEN
  RECURSIVE RULE (0.7312). IT DOES NOT BEAT IT.** *So: a learned mechanism reaches parity with the
  symbolic rule it was meant to replace, generalising to depths it never saw. That is a real result
  and a bounded one.*
  - **QUALIFIED -- `exp_graded_divisive_comparator_v1`:** real +0.0602 [0.0440, 0.0762] with a
    scramble twin at 0.5065, **but the CI lower bound does NOT clear its own pre-registered
    `d >= 0.05`, and the "divisive normalisation" half of the title contributes +0.00175.**
  - **QUALIFIED -- `exp_read_xsent_coref_scene_protagonist_v1`:** the gain is real (0.2462 -> 0.4003,
    McNemar CI lower +0.1039) **but the mechanism is a 5-sentence window, not "scenes" -- the cell
    says so itself.**
  - **SUSPENDED -- `exp_multi_turn_loop_realtext_nphead_gate_v1`:** "true zero confident-wrong" is
    **0 wrong of 18 kept** (rule-of-three upper bound 0.167) against a declared band of 0.01, and its
    one new variable fired on **two items that are the same passage, same answer, same gold** -- n=1.
  - **REFUTED -- `exp_social_relational_grounding_axis_v1`: THE SUBSTRATE CANNOT CHANGE ANY
    PREDICTION.** `valence` takes exactly **three distinct values across all 12 items**, and
    `acc_real` equals the WordNet `dictionary_lookup` accuracy **EXACTLY** (10/12). It is a 3-entry
    lookup table wearing a substrate.
  - **REFUTED -- `exp_desiderative_negation_channel_v1`: 8 OF 8 RECOVERIES LIE INSIDE THE 10-ITEM SET
    THE TAXONOMY WAS DESIGNED FROM, AND 0 OF 27 NON-DESIGN ITEMS RECOVERED.** The channel is
    **bit-identical ON vs OFF on both full benches** (n=80: 0.6992/0.6992; n=160: 0.6623/0.6623).
- **🚨 A BUG IN MY OWN GATE, CAUGHT BY THE AUDITOR, AND I HAD ALREADY QUOTED ITS NUMBER TO THE OWNER.**
  `CI_PAT` contained a bare `confidence`, which matched `lookup_confidence` and
  `high_confidence_idxs` -- model confidences, not intervals -- so two cells computing NO interval
  entered the "best evidenced" shortlist. **CORRECTED FIGURES: 28 carry a CI (not 52), 13 carry BOTH
  a CI and a null (NOT 26), and EVIDENCE_INSUFFICIENT is 2,665 = 99.5% (not 99.0%).** *The direction
  was right and the shortlist was half the size I said.*
- **🎯 THE BEST PREDICTOR IS NOT EVIDENCE-CARRYING, AND THIS IS THE MOST USEFUL THING FIVE PASSES
  PRODUCED: WHAT SEPARATES THE SURVIVORS FROM THE FAILURES IS *** WHETHER THE TEST ITEMS EXISTED
  BEFORE THE MECHANISM DID. ***** The three that survived this batch were scored on items built
  independently of the rule; the three that failed had detectors authored against the very items
  they were scored on -- one docstring even names the specific token pair its rule was written for.
  **CARRYING A CI IS NECESSARY AND WEAK; ITEM-PRIORITY IS THE STRONG TEST, AND IT SHOULD BE THE
  FIRST QUESTION ASKED OF EVERY REMAINING CLAIM.**
- **🔬🔬🔬 VETTING PASS 4 (`a6e60cfa`): 3 REFUTED, 1 SUSPENDED, 2 QUALIFIED, 0 UPHELD.
  RUNNING TOTAL OVER 24 CELLS: 11 REFUTED, 4 SUSPENDED, 9 QUALIFIED, *** ZERO UPHELD ***.**
  - **🚨 THE CAUSAL-LINK RESULT IS PROVEN CONTENT-FREE, NOT MERELY SUSPECT. The auditor RE-RAN the
    organ WITH THE GOLD LINKS REPLACED BY ARBITRARY RANDOM PAIRS AND GOT `organ_integration =
    0.9722` -- BIT-IDENTICAL TO THE HEADLINE.** The cell writes `add_causal_link(cause, effect)` for
    every gold item and queries the same indices back; no text is read (its own label is
    "GOLD-ISOLATION"). **It measures FHRR write/read fidelity at bundle-load 2 and nothing else.**
    **⛔ AND THE BASELINE WAS TUNED UNTIL IT FAILED.** The cell's own comment records sweeping
    distractor density from 200/20 to 15/10 to find *"the smallest min_dist that keeps mr_control >=
    the 0.50 can-fail floor WHILE DRIVING mr_integration TO 0.0000"*. **That is a gate adjusted
    until it passed. All three siblings die together: `pilot_v1`, `fuller_v2`, `fuller_v3_cleaned`.**
  - **REFUTED -- `exp_unified_self_learning_loop_v3`: ITS OWN SCRAMBLE CONTROL BEAT IT.** MAIN LOW
    gain **0.0243** vs SCRAMBLED **0.0288** -- scrambled text learns MORE. Every separation gate is
    `HP_CONTROL_SEP = 0.0` and `CONTRAST_EPS = 0.0`: **a margin of literally zero.** Its own
    label-shuffle null on the same slice wobbles **0.0258** cycle-to-cycle, larger than the entire
    claimed gain. Two arms are one measurement (`NO_READ` and `READ_NO_SLEEP` share the store digest
    `c23b44bc…`). **AND `..._loop_v4`, LANDED FIVE HOURS LATER THE SAME DAY, RECORDS
    `teaches_new=False` AND CARRIES v3's OWN NUMBER AS A CONTROL THAT FAILS. v3 WAS ALREADY DEAD AND
    WAS STILL SITTING ON THE QUEUE AS HARD_PASS.**
  - **QUALIFIED -- `exp_pivot_selectional_knowledge_richness_2afc_v1`: THE TABLE IS THE ANSWER KEY.**
    Its 117 rated pairs and its 59 items x 2 fillers = 117 evaluation pairs are a **PERFECT
    BIJECTION** (eval-not-rated 0, rated-not-in-eval 0): an LLM rated EXACTLY THE TEST. *Offline
    LLM-built foundations are admissible under the owner's ruling, but a table whose vocabulary IS
    the eval is an ORACLE, not a foundation.*
    **✅ THE PART THAT SURVIVES AND MATTERS: the dumb twins DO NOT reproduce it** -- verb-noun
    `Counter` 0.5508, noun frequency 0.5339, length 0.4915. **So the knowledge is REAL and ABSENT
    FROM OUR CORPUS. Honest claim: a cheating oracle reaches 0.78-0.85 on these 59 items and THE
    SUBSTRATE DID NONE OF IT.** *Convention was never declared: tie->0.5 gives 0.8136, tie->loss
    0.7797, tie->win 0.8475.*
  - **SUSPENDED -- `exp_outcome_valence_goal_congruence_v1`: THE DUMBEST RULE SITS EXACTLY ON THE
    BAR.** "Predict MET iff the goal's infinitival verb lemma equals the outcome verb's lemma" --
    no referent, no NP head, no registry -- scores **7/8 = 0.875, precisely the pre-registered
    HARD-PASS floor.** Mechanism 8/8 beats it by ONE item; CIs overlap; P(8/8 | p=0.875) = 0.34.
    *Its v2 reaches 1.0 at N=22 and self-tiered MIDDLE_BAND -- the honest tier v1 should have had.*
  - **QUALIFIED -- `exp_learned_argstruct_parser_lccp_independent_gold_v1`: THE WRONG COMPONENT IS
    CREDITED.** Arm B (cue-competition, **no LCCP**) already clears EVERY gate; adding the LCCP
    prior moves F1 0.3934 -> 0.4048, two items. **Its "generalization" gate is ONE-SIDED and fired
    because held-out precision (0.632) EXCEEDS seen (0.449) -- an EASIER held-out subset, not
    generalization.** *"Independent gold" means independent of reader output; the annotator was the
    authoring agent, same day, single pass. Absolute performance: P=0.50, R=0.34.*
  - **🚨🚨 THE CROSS-CUTTING FINDING, AND IT IS THE ONE THAT EXPLAINS THE 0-FOR-24: NOT ONE OF THESE
    SIX CELLS COMPUTED A SINGLE CONFIDENCE INTERVAL, NULL DISTRIBUTION OR p-VALUE.** Grepped for
    `confidence|ci_low|bootstrap|p_value|binomtest|permutation|half_width`: two hits, both unrelated
    words. **EVERY HARD_PASS IN THIS BATCH IS A POINT ESTIMATE COMPARED TO A POINT ESTIMATE, SEVERAL
    AT GATE MARGINS OF EXACTLY 0.0.** *That is not a scoring accident; it is the archive's method.*
- **🔬🔬 VETTING PASS 3 (`a04ef6b9`): 4 REFUTED, 2 QUALIFIED, 0 UPHELD. RUNNING TOTAL OVER 18 CELLS:
  8 REFUTED, 3 SUSPENDED, 7 QUALIFIED, *** STILL ZERO UPHELD AS CLAIMED ***.**
  **AT 0-FOR-18 THE PRIOR HAS MOVED: A HARD_PASS IN THIS ARCHIVE SHOULD BE READ AS "UNVERIFIED
  CLAIM", NOT AS EVIDENCE. THAT IS NOW A MEASURED BASE RATE, NOT A CAUTION.**
  - **REFUTED -- `exp_gap_driven_reader_controlled_v1`: A 12-LINE `Counter` WITH NO SUBSTRATE
    REPRODUCES THE HEADLINE 8/8 EXACTLY.** Ranking co-occurring unknown words by raw count scores
    1.0000, identical to the treatment. *The templates write the target into 2 of 2 intro sentences
    and the distractor into 1 of 2 -- **the margin is AUTHORED**. Its "ablated=0.0000" arm replaces
    the novelty filter with noise, removing the candidate SET rather than changing the RANKING: an
    extreme lesion, not a matched control.*
  - **🚨 REFUTED -- `exp_reading_grounding_loop_cycle2_v1`: THIS PROJECT ALREADY REFUTED IT ON DISK
    AND THIS DOCUMENT NEVER CAUGHT UP.** `exp_reading_grounding_loop_cycle3_groundingfix_v1` records
    `B1_taut 0.656885 -> 0.0` and `B4_grounded 3544 -> 634`. Independently recomputed from
    `data/foundation/reading_grounding_v1/store/store_facts.json`: **2,328 of 3,544
    GROUNDED_MEANING facts are SELF-ANCHORED -- 67% of "grounded concepts" have THEMSELVES as their
    meaning.** Of the 1,216 real links the top anchors are `also` (31), `say` (15), `people` (10),
    with samples like `web -> polar` and `stargaz -> million`; 121 stem/full-form pairs
    (`cigarett`/`cigarette`) are counted as separate concepts.
    **⛔ RETIRE THE FIGURE "3,544 CONCEPTS / 9.87x THE HAND LEXICON" WHEREVER IT APPEARS.**
  - **REFUTED -- `exp_verb_class_openvocab_similarity_v1`: THE "HELD-OUT" SET IS FOUR VECTORS.**
    In `hdlab/verb_lexical_similarity.py` every desiderative word -- 10 seeds AND all 16 held-out --
    carries the SAME four hand-written tags. **Held-out similarity to its own class is EXACTLY
    1.0000, cross-class 0.0104. The 64 "held-out" decisions are 4 distinct vectors; accuracy 1.0 is
    AN IDENTITY, NOT GENERALIZATION.**
    **AND ITS CITED BASELINE DOES NOT EXIST AS QUOTED:** it claims owner-acc 0.30 from
    `exp_real_text_goal_owner_generalization_diagnostic_v1`, whose single copy on disk reads
    **0.6000** and was written AFTER this cell ran. **The claimed +0.20 is unreproducible.** *In its
    own landed numbers the organ scores 0.5 owner vs recency 0.7 and ties its own lexicon baseline
    on polarity -- it LOSES to one dumb baseline and TIES the other, inside a HARD_PASS.*
  - **REFUTED -- `exp_c5_multigoal_content_coherence_tiebreak_v1`: GOLD IS DEFINED BY THE RULE THE
    MECHANISM APPLIES.** Plain bag-of-words overlap scores **12/12 = 1.0000 under all three tie
    conventions with zero ties**; margin over the strongest floor is **0.0000**. The cell's own
    docstring says gold IS the unique theme-overlapper.
  - **QUALIFIED -- `exp_c5_primacy_trap_endtoend_goal_coherence_candidate_gen_v1`: LEAK-CLEAN AND
    REAL, BUT NOT CI-SEPARATED.** It explicitly fixed a predecessor's gold leak and proves it with
    seven self-tests. **But its four floors are ALL POSITIONAL and read 0.0000 BY CONSTRUCTION**,
    while a lexical-overlap floor scores 0.80 / 0.675 depending on tie convention. System 20/20,
    Wilson lower 0.8389 vs the floor's upper 0.9193 -- **overlapping**; paired exact test on the one
    discordant item, p=1.0. *The auditor MEASURED THIS FLOOR AT 0.9839 FIRST AND CORRECTED ITSELF --
    that convention used roster-key order, which favours the owner. Both are reported.*
  - **QUALIFIED -- `exp_reading_grounding_loop_cycle1_v1`:** its context-scramble control BINDS
    (removed 132 of 185), but the same 67% self-anchoring applies, and its curriculum-order arm
    moved link-rate 0.3297 -> 0.3047 -- **a null shipped inside a pass**.
  - **✅ CLEAN ON TWO DIMENSIONS, AND WORTH SAYING: NO LLM in any operational path across six cells
    and four organs (grepped), and every cited path in this batch exists.** *But **NO CELL IN THIS
    BATCH REPORTS A p-VALUE OR A CI AT ALL**, and all three "3-seed" cells return bit-identical
    per-seed numbers BY DESIGN -- one measurement, printed three times.*
- **🔬 VETTING PASS 2 (`afb293f4`): 3 REFUTED, 3 QUALIFIED, 0 UPHELD. RUNNING TOTAL OVER 12 CELLS:
  4 REFUTED, 3 SUSPENDED, 5 QUALIFIED, *** ZERO UPHELD AS CLAIMED ***.**
  - **REFUTED -- `exp_causal_link_comprehension_fuller_v2`: THE ANSWER IS WRITTEN IN.** The cell
    calls `reg.add_causal_link(cause_idx, effect_idx)` for every item and then queries
    `query_effect_of(c_idx)` against `e_idx`. **That is write-then-read from a register at bundle
    load 2, and the two "baselines" NEVER RECEIVED THE WRITE**, so `most_recent=0.0000` and
    `random=0.0000` are STRUCTURAL, not measured. **NO COMPREHENSION WAS TESTED.** *What is
    actually there is 91.7% exact-key retrieval at 697 slots [0.782, 0.971] -- an 8% error rate at
    load 2, which reads as a MILD NEGATIVE ABOUT THE STORE.*
  - **REFUTED -- `exp_pivot_scaled_seed_knowledge_table_v1`: A ZERO-KNOWLEDGE FLOOR COMPUTABLE FROM
    THE CELL'S OWN CACHE SCORES 1.0000 (108/108) AGAINST THE LLM TABLE'S 0.6898.** Its gold is the
    verb's most-frequent attested patient and its distractor a never-attested noun, so plain corpus
    attestation is perfect by construction. **AND SCALING CHANGED NOTHING: the scaled and tiny
    digests are IDENTICAL (`5df85d80df03d57b`), `arms_differ_verified=False`.** *Surviving: LLM
    ratings do carry attestation signal (+0.1852, p=0.0054, n=108). That is not the claim made.*
  - **REFUTED -- `exp_read_grow_adaptor_pyp_kn_breadth_v1`: THE GATE CANNOT FAIL.** `kn_covered =
    (count>0) OR (...)` is a STRICT SUPERSET of flat coverage by construction. **Its "3/3 seeds" is
    ONE measurement printed three times** (identical gain 0.037475 across seeds; the tables do not
    depend on the salt). A **Zipf-count null with no linguistic mechanism reproduces the preemption
    correlation** (-0.60 vs the observed -0.5639 against a -0.15 gate). **On the only genuine
    generalization test -- 132 unseen items -- KN scores 0.1439 vs its OWN scramble 0.1591, WORSE
    in 2 of 3 seeds.**
  - **QUALIFIED -- `exp_information_foraging_reading_v1`: A FLOOR-BEATER, NOT A SHELF-BEATER.**
    FORAGE genuinely beats RANDOM (185 vs 38 of 3000, z=10.1) -- **but FROZEN, the fixed schedule
    foraging exists to REPLACE, scores HIGHER (0.0743 vs 0.0617).** The headline compares only
    against RANDOM. *Any claim that the decision organ improved reading must say this.*
  - **QUALIFIED -- `exp_lexicon_coverage_audit_barrier2_v1`: the COVERAGE half is UPHELD EXACTLY**
    (independently re-implemented: 2077 sentences, 2605 verb tokens, 568 types; union 0.9893/0.9648;
    every figure reproduces to 4 dp). **The second half is a SINGLE-RATER, UNBLINDED LLM
    HAND-AUDIT BY THE AUTHORING AGENT OF THE PREDICTION IT WAS TESTING**, no inter-rater
    reliability. **Under the stricter rubric THE CELL ITSELF NAMES in `honest_limitations`, it is
    89/120 = 0.7417 [0.657, 0.812] -- BELOW its own 0.80 floor.**
  - **✅ QUALIFIED -- `exp_context_vector_signal_v1`, AND A LONG-OPEN QUESTION IS NOW CLOSED CLEAN.**
    CLAUDE.md records that its figure came from a run whose clean-slate teardown was DENIED and
    silently dropped, that the figure is LOAD-BEARING in MEMORY.md, and that closing it needs a
    clean-slate re-run. **IT DOES NOT: the heartbeat trace settles it.** `_start_marker` 22:49:29.5,
    reading pass logged from unit 0 (22:49:43) to unit 49 (22:53:01), `pass_elapsed_s=208.99`; the
    cache is checked BEFORE the pass and skips it on hit, so **unit-0 heartbeats PROVE a cache
    miss**, and the FULL run wrote to a different directory than the denied smoke.
    **CONTAMINATION DID NOT OCCUR -- DEMONSTRATED, NOT ASSUMED. NO RE-RUN NEEDED.**
    **âš ï¸ BUT TWO CORRECTIONS TO HOW IT IS CITED: (a) the HARD_PASS IS POST-HOC -- the pre-registered
    ceiling guard fired on SCRAMBLE_SENT 0.9984 and was AMENDED AWAY AFTER THE RUN; the
    prereg-literal verdict is MIDDLE_BAND. (b) STOP QUOTING 0.7830 vs 0.9984 -- it is
    ceiling-saturated, all three nulls sit at 0.995-0.999. QUOTE `argmax_in_own_window_rate` REAL
    0.2871 vs an EXACTLY BAG-MATCHED SCRAMBLE 0.0050 (informative_rate 0.416808 vs 0.416687).
    A RATE-MATCHED TWIN DOES NOT REPRODUCE IT -- the strongest control-passing result in the batch.**
- **🚨 A THIRD FLOOR-DEFECT CLASS, DISTINCT FROM THE IMPORTED-BAR ONE, AND IT IS THE MOST COMMON:
  THE CELL HAD A STRONGER FLOOR ALREADY COMPUTABLE FROM ITS OWN DATA AND DISCRIMINATED AGAINST A
  WEAKER ONE.** Three of six this pass: attestation at **1.0000**, a superset-by-construction
  coverage gate, and FROZEN at **0.0743**. **THE RULE IS NOT JUST "RECOMPUTE THE FLOOR ON THIS
  REPRESENTATION" -- IT IS "RUN THE STRONGEST FLOOR THE CELL'S OWN DATA SUPPORTS".**
  **AND AUDIT "N SEEDS" FOR SEED-DEPENDENCE: three identical numbers are one measurement.**
- **🔬 FIRST SIX VETTED (`a2e65896`, AUDIT-ONLY, all recomputed off disk from per-item arrays, never
  from `verdict_msg`). ONE REFUTED, TWO SUSPENDED, THREE QUALIFIED. NOT ONE IS UPHELD AS CLAIMED.**
  - **REFUTED -- `exp_base_reader_grounded_relations_coref_v1`.** Headline `coref_lift=0.714,
    p=0.000` is on **SEVEN questions**, and that p is **resample degeneracy**: bootstrapping 7 paired
    diffs gives (2/7)^7 = 0.00016. **Exact paired McNemar on the same 7: p=0.0625, which FAILS its own
    alpha.** Worse, **the cell RAN a real floor arm that scores 5/7 on that slice** -- full vs floor
    p=1.0000 -- and then did not use it as the discriminator. Its NOCOREF control removed **0** items.
    *Surviving secondary: relation_lift over all 25 items, full vs floor exact p=0.0215. That holds.*
  - **SUSPENDED -- `exp_read_grow_foundation_realprose_glassbox_ie_v1`.** Its only floor is a
    **HARDCODED LITERAL `1.0`** (line 749) imported from a DIFFERENT cell on a DIFFERENT corpus (23
    pre-cleaned tuples, where that cell's own docstring says accuracy is 1.0 BY CONSTRUCTION). No
    floor was ever run on this cell's 34 sentences. **This is the SAME defect that suspended 21 arms
    on 08-18 -- and it was already present in JULY.**
    **✅ AND THERE IS A v2 THAT IS THE REAL RESULT: `..._realprose_glassbox_ie_v2` -- 46 sentences,
    correct_rate 0.891 against a REAL STANDALONE baseline of 0.565, delta +0.326, hardcoded stub
    REMOVED. CITE v2. v1 SHOULD NOT APPEAR IN THIS DOCUMENT AT ALL.**
  - **SUSPENDED (UNDERPOWERED) -- `exp_online_knowledge_condenser_selectional_v1`**, the
    best-designed of the six: real held-out split, explicit leakage guard, 4,151 mining sentences.
    **But n=48. FULL 0.750 [0.6275, 0.8725] against a SHUFFLE floor of 0.650 -- the CI lower bound
    sits BELOW the shuffle mean. z=1.07, p=0.285. The "+0.10" is 4.8 items.** Its gate was a bare
    point estimate. **Separating 0.75 from 0.65 at 80% power needs n~350.**
  - **QUALIFIED -- `exp_read_grow_construction_induction_dop_fragments_v1`, and it is the STRONGEST
    thing in the queue.** Only cell on a real external corpus (UD English-EWT, 846 sentences).
    **Scramble binds HARD and is deprel-multiset-preserving: 2/124 vs 44/124, 0/156 vs 44/156, 0/171
    vs 50/171 across three seeds; CI-separated 0.355 [0.271, 0.439] vs scramble upper ~0.038;
    `split_overlap=0`.** *Narrower than "construction induction": the input is GOLD UD `upos`+`deprel`,
    so parsing is ORACLE-SUPPLIED, and the metric is COVERAGE, not correctness (tunable 0.508 /
    0.355 / 0.25 by min_count). Its own verdict says FEASIBILITY PROBE -- that is the honest label.*
  - **QUALIFIED (toy) -- `exp_read_grow_openvocab_fastmap_v1`:** real mechanism, **26 hand-authored
    sentences, 3 nonce words, 5 query cues**; `ABSTAIN_BASELINE=0.0` BY CONSTRUCTION; 5 seeds vary
    only the codebook, so **n=1 dataset**; no CI, no floor, no scramble. Its NO_CONFIRM control DOES
    bind (removed 2 false facts).
  - **QUALIFIED (sharply) -- `exp_read_grow_oov_verb_extension_v1`:** `OOV_VERB_BASE_LEX` (line 165)
    **hardcodes munch->eats, pursue->chases, dwell->live -- THE SAME TABLE GENERATES THE SENTENCE AND
    SCORES IT**, and `coverage_current_pooled = 0.0` by construction, so "+88.2pp" is a gain over a
    definitional zero. Real residue: the morphology inverter. Its OOS control removed **0** items.
  - **🎯 THE CHEAPEST FIX IN THE WHOLE BACKLOG, and it needs no new experiment: SEVERAL CELLS ALREADY
    COMPUTED THE RIGHT FLOOR AND THEN DISCRIMINATED AGAINST SOMETHING ELSE. RE-SCORE EVERY LANDED
    CELL AGAINST THE FLOOR IT ALREADY HAS ON DISK.**
  - **NO LLM IN ANY OPERATIONAL PATH (verified by import scan).** But state these wherever "grounded"
    is claimed: WordNet is LIVE in the coref cell's path supplying the animacy that drives
    resolution, beside a 28-entry hand override and a 13-entry name-gender table curated for those 7
    passages; the condenser's 29-entry seed table is LLM-built OFFLINE and read-only (admissible).
  **ROOT CAUSE, FIXED: `tools/substrate_query.sh` -- the MANDATORY prior-work check -- RETURNS ZERO
  BYTES AND EXITS 0, so every "no prior work found" report from every agent and from me was
  vacuous, and the position document got assembled from whatever I happened to stumble into.**
  Replacement `tools/experiment_index.py` (`dc408b95e`) indexes all 8,834 cells, answers in about a
  second, and **PRINTS HOW MANY ROWS IT SCANNED BEFORE ITS RESULTS**, so an empty answer can never
  again pass for an established absence. **QUERY IT BEFORE WRITING ANY "WE HAVE NEVER" SENTENCE.**
- **â¸ï¸ HALTED ON A WEEKLY USAGE LIMIT (resets 1pm America/New_York). NOT a code, permission or design
  failure -- the scaling-curve cell was dispatched and its agent died on the API limit before writing
  anything. NOTHING IS RUNNING. NOTHING IS HALF-WRITTEN. NO PARTIAL ARTIFACT EXISTS TO CLEAN UP.**
  **RESUME HERE, AND THE WHOLE BRIEF IS ALREADY DECIDED -- DO NOT RE-DERIVE IT:**
  **BUILD: a CORPUS SCALING CURVE, not a single endpoint.** Rebuild the usage representation from
  `data/corpora/simplewiki/simplewiki_clean_v1.txt` at NESTED subsets -- ~0.6M (reproduces today's
  regime as the anchor), 2M, 6M, 20M, 42M tokens -- each smaller set a SUBSET of the larger so the
  curve is about SIZE, not about which text. Score every rung on the dissociation instrument.
  **REPORT MEDIAN CONTEXTS PER EVALUATION WORD at each rung -- that, not raw token count, is the
  quantity that governs a second-order statistic and it is what makes the curve interpretable.**
  **THE PRE-COMMITTED READINGS, decided BEFORE any number exists:** RISING and reaching ~0.5 by 42M
  -> scale was a genuine precondition we never met, and every "this mechanism does not work" verdict
  in this programme was reached where it COULD NOT have worked and must be RE-OPENED, not re-quoted.
  RISING but extrapolating to need MUCH MORE THAN ~50M -> **THE MACHINERY IS NOT BRAIN-FAITHFUL, and
  this is the MOST USEFUL outcome the cell can produce** (report the extrapolated requirement
  explicitly). FLAT -> supply was never binding; the mechanism answers the wrong question; scale
  hypothesis closed. NON-MONOTONIC -> the informative case; report it, do not smooth it.
  **WHY THE CRITERION IS BRAIN-FRAMED AND NOT AN EXCUSE (OWNER, and it is the point of the cell):**
  *"the brain doesn't need 600000 words - if we've set up the machinery right, shouldn't it work?"*
  A child hears on the order of millions of words a year and has real vocabulary by 4-6, so TENS of
  millions of tokens is roughly child scale. **623K is BELOW that -- we have been starving it, which
  is itself not brain-faithful. But needing 1e8-1e9 would be an ADMISSION THE MACHINERY IS WRONG,
  because no child gets that. That is what makes this falsifiable rather than a fudge.**
  **CONTROLS THAT ARE NOT OPTIONAL:** rank-matched null at EVERY rung
  (`tools/rank_matched_null_dissociation.py`) -- without it, a rise toward 0.5 is indistinguishable
  from information destruction, which is exactly the claim that was retracted today; all four floors
  AND the bar RECOMPUTED per rung (a bigger corpus is a DIFFERENT representation, so never import
  0.5431 / 0.5510 / 0.5943 / 0.6317); `F_SCRAMBLE` as a POLICY over >=500 permutations at the 95th
  percentile, reusing the fixed implementation already in
  `experiments/exp_crossview_convergence_hub_v1.py`; CI half-width AND null p95 beside every margin,
  with any rung whose half-width exceeds the chance-to-bar interval marked UNDERPOWERED rather than
  given a verdict; evaluation population HELD FIXED across rungs; checkpoint per rung (42M is a long
  run and must resume).
- **🚨🚨🚨 THE FINDING OF THE NIGHT, AND IT REFRAMES EVERY NEGATIVE ABOVE: WE HAVE BEEN MEASURING
  EVERYTHING ON 623,522 TOKENS. THE METHODS WE KEEP TESTING COME FROM A LITERATURE THAT OPERATES AT
  1e8-1e9. WE ARE 160x TO 1,600x BELOW THE REGIME THEY WERE BUILT FOR.**
  Measured just now, off disk: the store corpus every arm tonight was built on is **34,169 sentences
  / ~623,522 tokens**. **`data/corpora/simplewiki/simplewiki_clean_v1.txt` -- 2,779,032 lines,
  ~41,918,879 tokens, 252 MB -- HAS BEEN SITTING ON DISK THE WHOLE TIME AND WAS NEVER USED TO BUILD
  THE STORE. It is ~67x larger than what we measure on.** *We used it tonight only as a source of
  definition sentences, never as the usage corpus.*
  **WHAT THIS REFRAMES:** SGNS reading BELOW its own untrained control; dependency-typed contexts
  adding nothing; the drill's own note that symmetric-coordination and typed contexts are *"the
  right idea, measured on 1e8-1e9 tokens; our corpus is ~1e6"*; and the definitional teacher channel
  sitting AT CHANCE. **SUBSTITUTABILITY IS A SECOND-ORDER STATISTIC -- it needs enough contexts per
  word to compare two words' context DISTRIBUTIONS. At 0.62M tokens most words have far too few.**
  **âš ï¸ DO NOT OVERSELL THIS EITHER, AND I HAVE ALREADY OVERSOLD ONCE TONIGHT: MORE DATA CANNOT FIX A
  MECHANISM THAT ANSWERS THE WRONG QUESTION.** Co-occurrence accumulated over 42M tokens is still
  co-occurrence. **The honest claim is that SCALE IS A PRECONDITION WE HAVE NEVER ONCE MET, not that
  scale is the answer.** Every "this mechanism does not work" verdict in this programme was reached
  in a regime where the mechanism could not have worked, and that is a DIFFERENT statement from the
  mechanism being wrong. **CHEAP AND DECISIVE: rebuild the usage view on simplewiki and re-measure
  the incumbent. Nothing else should be built until that number exists.**
- **🔴 CROSS-VIEW CONVERGENCE HUB: CLEAN NEGATIVE, `B_NEGATIVE` FIRED AS PRE-COMMITTED. THE
  BEST-CONTROLLED CELL OF THE SESSION, AND THE FIRST BUILT FROM THE BIOLOGY RATHER THAN FROM WHAT
  WAS LYING AROUND.** `experiments/exp_crossview_convergence_hub_v1.py`, all 16 mechanism arms fail.
  Primary `HUB_CCA_BOTH` **0.3129 [0.2630, 0.3644]** against a **RECOMPUTED** bar of **0.5510**;
  margin **-0.2880**. **NOT UNDERPOWERED -- the CI upper bound sits 5.7 half-widths below the bar**,
  so this is a resolved negative, not a width.
  **✅ WHY THE NEGATIVE IS TRUSTWORTHY, and it clears every trap that caught us earlier:** BOTH trap
  pairings stayed dead (0.0446 / 0.1375, `ANY_TRAP_CLEARS_ITS_OWN_BAR` false) so it is not a trap
  artifact; held-out split 3,064 fit / 617 eval with eval words excluded from the SVD basis,
  vocabulary, CCA, ridge, lambda AND k*; all four floors NOT_SEPARATED, known-answer 0.9612, random
  0.4919; **the coverage control removed 40 of 242 rows (16.5%) -- IT BINDS**, unlike the one that
  removed 0 of 242 earlier tonight. A **planted-positive self-test** refused the cell until the
  pipeline could recover a planted invariant (now hub 0.9934, raw views 0.0000).
  **🔴 RETRACTED WITHIN THE HOUR BY THE BRAIN DRILL (`9f27cc5e9`) -- I RELAYED THE 0.06 -> 0.31 MOVE
  TO THE OWNER AS "GENUINELY STRIPS CO-OCCURRENCE". IT IS NOT. THERE IS ZERO MEASURED EXTRACTION.**
  **A RANDOM 8-DIMENSIONAL PROJECTION OF THE INCUMBENT STORE -- WHICH NEVER SEES THE DEFINITIONAL
  CHANNEL AT ALL -- READS 0.3079 [0.2697, 0.3495]. THE ARM READS 0.3129, INSIDE THAT BAND.**
  Dose-response on RANK ALONE reproduces the whole effect: k=2 -> 0.4127, k=8 -> 0.3079, k=32 ->
  0.1770, k=128 -> 0.0798, k=256 -> 0.0536 (centring alone 0.0536, so it is RANK, not centring).
  **AND WORSE: pipeline-matched -- same whitening, same rho, same k*=8, ONLY THE DIRECTIONS
  RANDOMISED -- the null reads 0.3312 and BEATS the real `HUB_CCA_X` (0.2458) IN 200 OF 200 DRAWS.
  THE CROSS-VIEW-CHOSEN DIRECTIONS ARE WORSE THAN RANDOM ONES.**
  **🚨 THE GENERAL LESSON, AND IT IS A NEW FLOOR WE HAVE NEVER HAD: WHEN THE BASELINE SITS FAR BELOW
  CHANCE, DESTROYING INFORMATION MOVES THE SCORE TOWARD 0.5 AND READS AS PROGRESS. THE ENTIRE
  INTERVAL (0.06, 0.50) IS REACHABLE BY PURE DEGRADATION, AND NOT ONE FLOOR IN OUR BATTERY CATCHES
  IT.** *Any future "we moved from 0.06 toward 0.5" claim is void until it beats a RANK-MATCHED
  null.* Control now exists: `tools/rank_matched_null_dissociation.py`.
  **ALSO: the teacher channel was AT CHANCE BEFORE THE HUB WAS BUILT ON IT -- `A_DEF` 0.4780
  [0.4223, 0.5350], NOT separated from 0.5.** *I quoted 0.4780 as a point value; it is a width.*
  **TWO SETUP WEAKNESSES NAMED: the channel-independence preflight has a CEILING (r >= 0.95) but NO
  FLOOR, and the pairing sat at r=0.0363 with held-out cosine 0.0512 -- the channels were nearly
  UNRELATED, which is as fatal as being redundant; and `lam_rel=1.0` was selected AT THE GRID
  BOUNDARY in 3 of 4 pairings with the objective still climbing, so k*=8 is a truncated-search lower
  bound, not an optimum.**
  **SCOPE, as pre-registered: one definitional channel, one usage channel, one LINEAR extractor,
  one instrument, n=202. It says the missing ingredient is not a second view OF THIS KIND.**
- **🚨 A LICENSING DEFECT THIS CELL FOUND THAT REACHES BACKWARDS INTO EVERY RUN WE HAVE GATED:
  `F_SCRAMBLE` WAS A SINGLE COIN FLIP.** Its first smoke voided on `F_SCRAMBLE` 0.4266
  [0.3701, 0.4867] -- **one permutation's own CI excludes 0.5 about 5% of the time BY CONSTRUCTION,
  and across four floors that voids or passes roughly 18% of runs ON NOISE ALONE.** Measured
  single-draw false-fire rate **0.010-0.080 across 17 floors** -- that is the receipt, not an
  estimate. **FIXED HERE: `F_SCRAMBLE` is now a POLICY over 500 permutations with the bar term taken
  from the 95th percentile of that distribution -- which RAISED the bar and made it the BINDING
  term (0.5510).** *So this cell was judged against a HARDER bar than any predecessor.*
  **OPEN AND NOT YET ASSESSED: every earlier licensing decision in this programme used the
  single-draw form. That does not invalidate them, but it means an unknown fraction turned on a coin
  flip, and the fix belongs in the shared instrument, not in one cell.**
- **🚨🚨🚨 AUDIT LANDED 06:52 (`37181d944`) -- BRANCH (i): 3 CELLS, 21 ARMS MIS-GATED, TWO OF THEM NEW.
  AND IT SURFACED SOMETHING LARGER THAN THE IMPORT: THE BAR ITSELF WAS NEVER SEPARATED FROM CHANCE.**
  **`F_CONSTANT_PROTOTYPE` = 0.5431 CARRIES CI [0.4922, 0.5953] -- IT INCLUDES 0.5.** I checked the
  human instrument's bar too: **`F_SCRAMBLE` = 0.5943, CI [0.4937, 0.6911] -- ALSO INCLUDES 0.5.**
  **BOTH BARS THIS PROGRAMME GATES ON ARE STATISTICALLY INDISTINGUISHABLE FROM CHANCE AT THEIR OWN n.**
  *I spent two days correcting people that "the bar is 0.5431, NOT 0.5" -- and the honest statement is
  that at these sample sizes THE TWO CANNOT BE TOLD APART. That correction was itself a width read as
  an effect: discipline 14, committed by the person who wrote it.*
  **MECHANISM (DSI L99-108): `F_SCRAMBLE` and `F_CONSTANT_PROTOTYPE` are computed FROM THE STORE
  MATRIX; the other two are not. The bar is always owned by one of those two -- SO THE BAR IS
  INHERENTLY THE REPRESENTATION-BOUND QUANTITY.** *That is why importing it across representations
  was guaranteed to be wrong, not merely unlucky.*
  **THE THREE, ALL `SUSPENDED, NOT REFUTED` -- a wrong floor makes a verdict UNSUPPORTED, it does NOT
  establish the opposite:** (A) the typed-role arc cell, already retracted; (B) **NEW --
  `exp_typed_role_selectional_asset_writerule_v1` (`c1d2bc80e`, 7 arms)**, corroborated off its own
  data: **its must-fail controls `N1` 0.5516 and `N3` 0.5630 sit ABOVE the 0.5431 bar**, so its native
  floor is ~0.55-0.56 and the imported bar was too low, *same direction as the arc rebuild*; (C)
  **NEW -- tonight's human-instrument cell (`16475c9c5`, 4 arms)**, which re-derived its bar sincerely
  but along the wrong axis -- right population, from v3 arrays built on the **bag** store.
  **✅ WHAT SURVIVES UNTOUCHED, and this matters: (B)'s `WORD_SELECTION_NOT_TYPE` verdict is
  WITHIN-CELL and same-representation, so it STANDS; no false positive was manufactured anywhere
  (B's `T1` never cleared the bar even at its CI lower bound 0.5296); and BRANCH (B) FROM 6.39 STANDS
  *A FORTIORI* -- `U1` 0.4125 failed a bar we now know was TOO LOW.**
  **NOT A PROGRAMME-WIDE CRISIS, and I was primed to call it one.** The write-rule ladder already does
  this correctly **per arm** (`F_CONSTANT_PROTOTYPE__<arm>`); `corpus_capacity`, `tuned_count` and
  `predictive_coding` gate on 0.5 and hold 0.5431 only inside regression gates. **Branch (iii) ALSO
  fired: NO `metrics.json` ANYWHERE records the REPRESENTATION a floor came from** -- every
  determination above needed the source, so this is unauditable from artifacts today.
- **🔴🔴 07:05 -- THE DEGENERACY HYPOTHESIS BELOW IS NOW CONFIRMED FROM THE CELL'S OWN PERSISTED
  DIAGNOSTICS, AND IT MEANS THE HUMAN INSTRUMENT COULD NOT FAIRLY TEST `U1` AT ALL.**
  `report/OCCURRENCE_DATA_STATS`: **`n_occurrences_total` = 10,215, `n_occurrences_with_slot` =
  1,112. ONLY 10.9% OF OCCURRENCES ON THIS POPULATION CARRY THE SLOT INFORMATION THE TYPED ARM IS
  BUILT FROM.** And `report/ARM_DIAGS` gives `U1` **`vocab_size` = 10,121** dimensions. **That is
  ~8.6 SLOTTED OCCURRENCES PER WORD SPREAD OVER A 10,121-DIMENSIONAL SPACE.** *Nearly every pair of
  words shares no dimension at all, so nearly every cosine is zero and the arm collapses onto the
  constant-prototype value -- which is EXACTLY the 0.4125/0.4125 tie the audit spotted.*
  **THE CONTRAST INSIDE THE SAME RUN SETTLES IT: `U3_ROLE_ONLY` uses `vocab_size` = 58 -- DENSE --
  and reads 0.5037, at chance but NOT degenerate. Same corpus, same population, same 28,832 arc
  events; the only thing that changed is how thinly they were spread.**
  **WHAT THIS DOES TO BRANCH (B). THE BRANCH FIRED AS PRE-COMMITTED AND I AM NOT UNFIRING IT -- BUT
  ITS INTERPRETATION IS NOT SUPPORTED. "The 0.6669 was WORDNET-SPECIFIC" REQUIRES THAT THE HUMAN
  INSTRUMENT GAVE THE ARM A FAIR TEST, AND AT 10.9% SLOT COVERAGE IT DID NOT.** *The correct reading
  is much closer to 6.39's branch (C): **this population cannot test this arm.** The agent noted (C)
  "did not fire only because `U1` is not above chance" -- and a starved arm sitting ON its own
  constant floor is precisely how an untestable arm presents.*
  **WHAT IS STILL TRUE AND MUST NOT BE QUIETLY DROPPED: THIS DOES NOT RESCUE THE 0.6669.** That
  number died for an unrelated and still-standing reason -- **its bar was a bag-representation floor,
  and on a rebuilt arc floor a no-words attestation control reads 0.6317.** *Two independent defects,
  one per instrument; fixing this one does not touch that one.*
  **AND IT CONVERGES WITH THE BIOLOGY DRILL, WHICH REACHED THE SAME DIAGNOSIS FROM THE OTHER
  INSTRUMENT: "a median 130 arcs per word cannot populate 21,093 dimensions -- the lexical channel
  was STARVED, NOT FALSIFIED." TWO LANES, TWO POPULATIONS, SAME CAUSE.** *The typed channel has never
  once been given enough data to be tested, on EITHER instrument.*
  **HONEST SCOPE: I measured SLOT COVERAGE, which is the upstream CAUSE. I did NOT measure the
  pairwise-cosine spread, which is the direct SYMPTOM and is still the cleaner confirmation.** *I said
  I would not rewrite branch (B) before measuring, and I am recording a re-interpretation on
  different evidence than the check I named -- stronger evidence, but not the same evidence. The
  cosine-spread check stays open.*
- **🔬 [SUPERSEDED BY THE CONFIRMATION ABOVE] MY OWN FOLLOW-UP, HYPOTHESIS NOT FINDING -- THE ONE ITEM THE AUDIT FLAGGED AND LEFT UNVERIFIED,
  NOW CONFIRMED NUMERICALLY AND IT MAY RE-INTERPRET BRANCH (B).** In the human cell, `U1_TYPED_CONTEXT`
  reads **0.4125 [0.3148, 0.5138]** and `F_CONSTANT_PROTOTYPE` reads **0.4125 [0.3164, 0.5153]** --
  **IDENTICAL TO FOUR DECIMALS, different CIs** (so two genuinely different computations, not one value
  copied). **`F_CONSTANT_PROTOTYPE` IS BY DEFINITION WHAT YOU SCORE WHEN EVERY WORD HAS THE SAME
  VECTOR.** *So the live alternative to "typed context is bad at human similarity" is **"typed context
  produced near-DEGENERATE vectors on this 65-pair population"** -- which would make branch (B) a
  statement about COVERAGE COLLAPSE, not about the channel.* **CHEAP DECISIVE CHECK, NAMED AND NOT RUN:
  the pairwise-cosine spread of `U1`'s vectors on that population -- near-zero spread confirms
  degeneracy.** **DO NOT REWRITE BRANCH (B) UNTIL THAT IS MEASURED; an exact tie at n=65 is suggestive,
  not proof, and I have twice tonight promoted a suggestive number too early.**
- **🚨🚨 RETRACTION, 06:15 -- I HEADLINED "THE FIRST ARM EVER TO CLEAR THE BAR" AND TWO INDEPENDENT
  LANES TOOK IT APART WITHIN THE HOUR. THREE OF THE FOUR SUPPORTS ARE GONE. READ THIS BEFORE THE
  GREEN BLOCK BELOW, WHICH IS SUPERSEDED.**
  1. **THE BAR WAS THE WRONG BAR -- MY OWN RULE, BROKEN BY THE CELL AND MISSED BY ME.**
     `bfc0e941c` rebuilt the arms from the cell's persisted `arc_events`, **reproduced U1 0.6669 /
     U3 0.6466 exactly**, then recomputed the floors **on the arc representation the arms actually
     use.** An **ATTESTATION floor -- `log(min(arc_mass))`, NO WORDS, NO MEANING -- reads 0.6317
     [0.5820, 0.6781]**, effectively at the 0.6669 headline. The 0.5431 bar was a **BAG**-
     representation number imported across representations. *"EVERY FLOOR RECOMPUTED ON THE ITEM'S
     OWN POPULATION, NEVER IMPORT" is discipline (2) in this file, and the run imported one.*
     `U1_COVERAGE_MATCHED` could not catch it -- `COVERAGE_MIN=3` dropped **0 of 242 pairs**, so the
     control never bound.
     **WHAT SURVIVES, AND IT IS NOT NOTHING:** on a **mass-matched subsample (n=189, residual floor
     0.507)** the effect holds -- **U3 0.6369, U1 0.6284** -- and against **frequency-matched random
     noun pairs** U3 reads **0.5958 [0.5458, 0.6458]** vs floors 0.5141 / 0.5053. **A 64-bin role
     histogram with the words thrown away does carry real substitutability. It is a SMALLER, HONEST
     result standing on a REBUILT floor, not the headline I wrote.**
  2. **🔴 "SECOND INDEPENDENT NEGATIVE ON PREDICTION ERROR" IS RETRACTED OUTRIGHT -- I VERIFIED THE
     DEFECT IN SOURCE MYSELF.** `store_from_s1` and `store_from_s1_permuted_magnitude` both iterate
     **`rec["bag_counts"]`** (`experiments/exp_typed_role_context_write_rule_dissociation_v1.py`
     ~590-640, called at 954-957). **The prediction-error rule was applied to the BAG channel -- the
     one already known to be a pure co-occurrence detector at A0 0.0510 -- NOT to the typed channel.**
     That is why S1 0.0695 and N3 0.0591 sit right beside A0. **A null there says essentially nothing
     about whether an error signal helps the typed representation. PREDICTION ERROR ON THE TYPED
     CHANNEL HAS NEVER BEEN TESTED.** *I propagated this claim twice tonight.*
  3. **THE CORRUPTION-TOLERANCE EVIDENCE IS RETIRED.** `N6` replaces corrupted arcs by drawing from
     the marginal, which **adds a shared vector to every word -- near rank-preserving for a rank-sum
     AUC. THE CONTROL AS BUILT IS NEARLY INCAPABLE OF FAILING**, so "survives 50% corruption" was a
     property of the corruption model, not of the representation.
  4. **BRANCH (B) FIRED ON THE HUMAN INSTRUMENT (`16475c9c5`), EXACTLY AS PRE-COMMITTED AT
     `fa5da1d2c`: `U1_TYPED_CONTEXT` = 0.4125 [0.3148, 0.5138] -- BELOW CHANCE.** (`U3` 0.5037,
     `T2` 0.3567; bar 0.5943 **derived here, nothing imported**; both gates PASS.) **6.24 PARTIALLY
     RE-OPENS: the two instruments agree about the poor arms (rho 0.9034) and DISAGREE at the top of
     the range, which is the only region anyone cares about.** **THIS IS THE INFORMATIVE CASE AND IS
     NOT TO BE WRITTEN UP AS "MIXED".**
     **CONFOUND, FLAGGED BY THE AGENT AND NOT RESOLVED: that human population is 83% VERB pairs
     (108v / 18n / 4a) while the WordNet instrument is NOUNS-ONLY. "WORDNET-SPECIFIC" AND
     "NOUN-SPECIFIC" ARE NOT SEPARATED BY THIS RUN.** *A POS-stratified re-read is named, not run.*
  - **WHERE THAT LEAVES THE "WHICH KIND OF SLOT, NOT WHICH WORD" READING -- THE TWO LANES DISAGREE,
    AND THE DISAGREEMENT IS THE POINT.** The OBSERVATION replicates on both sticks (`U1-U3` NOT
    separated: +0.0203 [-0.0185, 0.0591] WordNet, **-0.0911 [-0.2014, 0.0192] human**). But
    `bfc0e941c` argues the tie is **DATA POVERTY, NOT A FINDING: a median 130 arcs per word cannot
    populate 21,093 dimensions, so the lexical channel was STARVED, NOT FALSIFIED** (effective code
    is **~3 relation bins**; top-3 gives 0.6240 of U3's 0.6466). **A starved lexical channel would
    tie on BOTH instruments too, so replication does not discriminate.** *The observation stands;
    my interpretation of it does not follow. I stated it as the finding twice.*
  - **🧠 THE BIOLOGY PUTS THE WHOLE NIGHT IN A DIFFERENT FRAME (PINNED, and the most useful thing
    anyone produced tonight): taxonomic (ATL) and thematic (pMTG/TPJ) systems DOUBLY DISSOCIATE.
    OUR INSTRUMENT *IS* THAT DISSOCIATION MEASURED IN A CORPUS, AND THE WINNING ARM IS THE THEMATIC
    ORGAN DOING THE TAXONOMIC ORGAN'S JOB.** Coarse frames drive **CATEGORY** induction unsupervised
    (Mintz 2003); syntactic bootstrapping shows frames **CONSTRAIN** a meaning hypothesis, they do
    not **SUPPLY** it. **So role profile = STAGE ONE, grounded cross-modal convergence = STAGE TWO --
    WE BUILT STAGE ONE AND SCORED IT ON A STAGE-TWO INSTRUMENT.** *That, not the AUC, is the finding
    worth keeping.* **OPEN (do NOT write as pinned): whether role is coded SEPARATELY from filler --
    F&G's own ROIs reanalyse as non-orthogonal, and Fedorenko 2020 finds NO syntax-selective region.*
- **[SUPERSEDED BY THE RETRACTION ABOVE -- KEPT SO THE OVERCLAIM STAYS VISIBLE] LANDED 05:36
  (2026-08-18) -- `exp_typed_role_context_write_rule_dissociation_v1` (`5170c7751`).**
  Instrument re-licensed IN THIS RUN (all 8 cached DSI checks reproduced at delta 0.0000, floors at
  chance, **n=242 per cell** -- not the n=7 of the human v1 attempt). **Matching is per-POS-stratum,
  so SET_P/SET_S cannot differ in POS by construction.**
  **`U1_TYPED_CONTEXT` 0.6669 [0.6184, 0.7136] vs incumbent bag-of-words `A0` 0.0510** -- and the
  three mandatory controls all held: beats `N1_LABEL_PERMUTED` **+0.1105 [0.0800, 0.1420]**, beats
  `N2_RANDOM_TYPING` **+0.1068 [0.0696, 0.1449]**, and `U1_COVERAGE_MATCHED` is 0.6669, unmoved.
  **READ THE MARGINS FROM THE PAIRED-DIFFERENCE CI, NOT FROM WHETHER THE TWO ARMS' OWN CIs OVERLAP**
  -- I misread overlap as "not separated" while checking this, and the two tests disagree.
  **BUT `STOPIF3` FIRED AND IT DOWNGRADES THE HEADLINE: `U3_ROLE_ONLY` 0.6466 TIES `U1`**
  (+0.0203 [-0.0185, 0.0591], NOT separated), and an independent parse-noise sweep **barely moved the
  score -- 0.667 -> 0.651 with 50% of the parse neighbours CORRUPTED.** *If half the neighbours can be
  wrong and the answer survives, the specific typed neighbours are not what is carrying it.*
  **THE HONEST CLAIM IS THE COARSER ONE: most of the signal is WHICH KIND OF SLOT a word fills, not
  WHICH WORD fills it.** `T2_UNTYPED_SAME_COVERAGE` 0.6128 clears the bar on its own -- selection
  carries the bulk -- with the type label adding a real but small CI-separated increment
  (**+0.0541 [0.0339, 0.0753]**). **DO NOT WRITE "GRAMMAR CARRIES SUBSTITUTABILITY."**
  **SECOND INDEPENDENT NEGATIVE ON PREDICTION ERROR:** `S1_SLOT_COMPETITION` 0.0695 does NOT beat
  `N3_MAGNITUDE_PERMUTED` 0.0591 (+0.0104 [-0.0069, 0.0289]). *That is now twice, on different
  mechanisms.*
  **AND 6.38's PREMISE REPLICATES ACROSS CORPORA:** `T3_COMBINED` (the published Komninos &
  Manandhar window+dependency pattern) **HURT in both corpora** -- 0.3533 here, **-0.3136
  [-0.3476, -0.2812] vs `U1` alone**, and 0.2264 on SimpleWiki. **Concatenating an anti-correlated
  channel is now a two-corpus finding, not a one-off.**
  **CORRECTION TO MY OWN 93d54ba72, MADE 10 MINUTES EARLIER: I claimed this run's stdout log lagged
  its `units.jsonl` because stdout was block-buffered. THAT WAS WRONG.** Re-checked at 05:34: both
  mtimes 2 min ago, in sync. The 11-minute gap I saw was **PRINT CADENCE** -- the occdata stage prints
  every 100 words, and 381 units sat between the 300 and 400 marks. *There is no buffering defect;
  `units.jsonl` mtime is still the better liveness signal, but the log is not lying.*
- **🟢 LANDED 05:44 -- `exp_dissociation_score_instrument_human_v4` (`75e093747`). THE 6.24 WORDNET
  CAVEAT IS DISCHARGED. VERIFIED OFF DISK BY THE DIRECTOR, NOT TAKEN FROM THE AGENT'S PROSE.**
  **rho = 0.9034 at 24 arms, bootstrap-of-arms 95% CI [0.7548, 0.9676] -- EXCLUDES ZERO**, against
  rho 0.7857 / CI **[-0.0435, 1.0]** at 7. **Pre-committed branch (i) fired.** *The arm count really
  was the limit: with 7 arms the CI could not separate from zero at any estimate quality.* Both
  regression gates PASS (DSI 8 checks at tol 0.0005; v3 floors + n=65 bit-for-bit).
  **WHAT THIS BUYS: every Organ A conclusion rested on an instrument built from WordNet, and the fear
  was that we had only ever measured AGREEMENT WITH WORDNET. Two independently-built instruments --
  one from WordNet, one from published HUMAN similarity ratings -- now rank our 24 arms the same way.
  ORGAN A'S CLOSURE IS A FACT ABOUT OUR STORE.**
  **🚨 BUT READ THE HUMAN ARM TABLE BEFORE CELEBRATING: ALL 24 ARMS SIT AT OR BELOW CHANCE ON HUMAN
  JUDGEMENTS.** The two best straddle 0.5 and clear nothing -- `F1_NO_FILTER` [0.4542, 0.6508],
  `T1_TYPED_ROLE` [0.4054, 0.6057] -- and the human bar is **0.5943**. *Agreeing about the ordering of
  24 arms is not the same as any arm being good; the instruments agree that they are all poor.*
- **🎯 THE OBVIOUS NEXT TEST, AND NOBODY HAS RUN IT: `U1_TYPED_CONTEXT` (0.6669, the only arm ever to
  clear the WordNet bar) IS NOT IN THE 24.** It landed at 05:36; the harvest was already built. The
  `T1_TYPED_ROLE` in the table is the **SimpleWiki** arm, a DIFFERENT cell. **So the one arm that
  cleared a bar has never been scored against human judgement.** v4 now has the harvesting machinery,
  so this is cheap. **rho = 0.9034 predicts it should replicate -- WHICH IS EXACTLY WHY IT IS WORTH
  RUNNING: a pre-committed prediction that can FAIL.** *Recorded, deliberately NOT dispatched --
  CLAUDE.md's rule is that an agent report ends my involvement and the owner decides what happens
  next.*
- **🔴 LANDED (`1b79ae57b`) -- SENSORIMOTOR CHANNEL: BRANCH (B) FIRED, EXACTLY AS PRE-REGISTERED AT
  `73edbca69`. THE PERCEPTUAL ROUTE IS CLOSED AT THIS RESOLUTION, AND THE MECHANISM IS THE VALUABLE
  PART.**
  Best arm `SM11_Z_NEG_EUCLID` **0.6039 [0.5439, 0.6644]** against a **credible bar of 0.6791**
  (margin **-0.0752**). **AND IT IS WORSE THAN THAT: IT SITS BELOW THE CONSTANT/PROTOTYPE FLOOR'S OWN
  POINT VALUE (0.6195). 0 OF 6 GRID POINTS CLEAR; ALL SIX CIs OVERLAP THAT FLOOR.** Coverage **166 of
  242** matched units, **557/617 = 90.3% of words -- independently reproducing the drill's §3.2
  figure**, so this is not a coverage failure.
  **🔬 THE MECHANISM, AND IT IS THE FINDING: THE ONLY THING THAT DISCRIMINATES IS A *QUERY-INDEPENDENT
  PER-WORD GENERICITY SCORE* -- ONE THAT NEVER COMPARES THE TWO WORDS AT ALL -- READING 0.6195,
  CI-SEPARATED ABOVE CHANCE AND BEATING EVERY PAIRWISE DISTANCE.** Centring collapses cosine
  0.5990 -> 0.5381 while euclidean is unmoved: **the cosine "signal" was carried by the SHARED
  PROTOTYPE DIRECTION.** Both cells sit in a narrow cone (within-pair cosine 0.8768 vs 0.8434) and
  **effective dimensionality is 6.26 OF 11.** *So the norms do carry a real signal -- "how generic is
  this word" -- and it is NOT "are these two words alike". That is the constant/prototype floor's
  signature, which is precisely what the drill predicted.*
  **✅ THE NEGATIVE IS REAL AND WAS CHECKED BEFORE ANY BRAIN TALK (discipline 17's first clause):**
  instrument still licensed at n=166 (four floors CI-include 0.5; incumbent 0.0884); the
  **planted-separable self-test fires at the deciding n or the cell aborts**; scramble changes 100%
  of scores. **NOT A POWER PROBLEM -- the best arm is below the floor's POINT value, so no amount of
  n converts it.** *Concreteness alone (1 dim): 0.5388 vs its own bar 0.6256 -- also beaten by its
  own floor.*
  **âš ï¸ TWO DISCLOSURES, BOTH THE AGENT'S OWN:** (1) known-answer reads **0.9448 [0.9204, 0.9654]** vs
  a 0.95 **point** gate -- **fails strict-point by 0.005, passes CI-inclusive**; the branch was driven
  by the CI form, both printed, decided and written into the docstring BEFORE the FULL run. (2)
  **`F_PROTOTYPE_MAGNITUDE__CONC1` = 0.3195: `SET_S` PAIRS ARE RELIABLY MORE CONCRETE THAN `SET_P`.**
  *The matcher balances on frequency/length/POS -- NOT on rating-norm properties -- so **discipline 16
  is live here in a new form: the POPULATION is unbalanced on the very axis this channel measures.***
  **WHAT IT DOES AND DOES NOT CLOSE: it refutes THIS RESOLUTION (11 dims), NOT GROUNDING.** And the
  trade is now measured rather than assumed: **Binder's 65 dimensions discriminate far better but
  cover 9.2% of eval words / 5.0% of anchors, and a unit needs ALL FOUR words covered -- which
  collapses the instrument below the "a win on 20 pairs is not a win" line. NO ASSET WE CURRENTLY
  HOLD SITS ON THE GOOD SIDE OF THE COVERAGE-RESOLUTION TRADE.** *The image-derived relational subset
  (57.9%) is a different KIND of signal and a separate cell.*
- **[SUPERSEDED -- LANDED ABOVE] SECOND LANE (08:05) -- `sensorimotor-discrimination`. THE MOST CONSEQUENTIAL TEST OF THE NIGHT,
  AND IT IS PRE-REGISTERED TO FAIL IN A SPECIFIC WAY. DO NOT RESPAWN.**
  **Question, deliberately narrow: does a PERCEPTUAL profile separate `SET_P` from `SET_S` AT ALL?
  A SIGNAL THAT CANNOT DISCRIMINATE CANNOT TEACH**, so this gates every downstream supervision idea.
  Data verified on disk by me: `data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv`,
  16.4 MB, 39,707 rows, all 11 mean dimensions present. **NOT text-derived, NOT WordNet-derived, NOT
  an LLM -- which is exactly why it is admissible where every other candidate was circular.**
  **Branches pre-committed at `73edbca69` (6.43) BEFORE dispatch. THE FAILURE MODE IS NAMED IN
  ADVANCE: `SET_S` pairs are same-POS same-domain nouns ("calcium/carbonate") that may share a
  sensorimotor profile just as the synonyms do, so this channel may behave like the
  constant/prototype floor -- OUR STRONGEST. IF THAT FIRES IT REFUTES THIS RESOLUTION (11 dims), NOT
  GROUNDING**, and the report must name what resolution would be needed rather than concluding
  grounding fails. *Binder's 65 dimensions discriminate better but cover 9.2% of eval words.*
  **IT IS A DISCRIMINATION TEST, NOT A SUPERVISION BUILD -- if it passes, the supervision cell is a
  SEPARATE decision with its own pre-commitment.**
- **🔵 FIRST LANE (07:20) -- `typed-density-sweep`. DO NOT RESPAWN.**
  Sweeps the typed channel's density by coarsening `(neighbour, relation, direction)` binning from
  ~10,121 dimensions toward `U3`'s 58, **recomputing every floor PER CONFIGURATION on that
  configuration's own representation.** **Branches PRE-COMMITTED at `0504bfd00` (plan 6.41) BEFORE
  dispatch -- READ THEM BEFORE READING ITS RESULT:** *(α) some density clears its own rebuilt floor
  -> the channel was starved, and **the occurrences-per-dimension at which it turns on IS the
  finding, not the AUC**; (β) nothing clears anywhere -> it does not carry substitutability at any
  density reachable **on THIS corpus** -- **state the corpus and range, do NOT call it impossible**;
  (γ) it clears only once coarsened onto `U3` -> **role identity is the carrier, typed context adds
  nothing, headline is `U3`** -- pre-committed as **the branch I expect to dislike**, and it must not
  be softened.*
  **IT WAS TOLD TO COPY THE WRITE-RULE LADDER'S PER-ARM FLOOR PATTERN AND EXPLICITLY *NOT* THE CELL
  THAT IMPORTED 0.5431.**
- **📋 BOARD FELL 13 -> 3 WITH NO OWNER INPUT THIS SESSION. NOTED, NOT CHASED.** *Consistent with the
  seven duplicate `rm`-denial questions being auto-closed -- which is what the triage predicted would
  happen once the underlying fault stopped recurring -- but **I have not verified that** and it
  should not be reported as if I had.*
- **[LANDED -- kept for the compaction reader] IN FLIGHT (2 lanes, both dispatched 05:50-05:55). DO NOT RESPAWN EITHER -- a duplicate is the
  more expensive error, and I made exactly that mistake twice tonight.**
  1. **`U1` ON THE HUMAN INSTRUMENT** -- scoring `U1_TYPED_CONTEXT`, `U3_ROLE_ONLY` and
     `T2_UNTYPED_SAME_COVERAGE` against human similarity ratings (n=65, bar **0.5943**). **Its
     branches were PRE-COMMITTED at `fa5da1d2c` BEFORE dispatch -- plan 6.39. READ THEM BEFORE
     READING ITS RESULT.** *(A) clears CI-separated -> holds on two independent instruments;
     (B) at or below chance -> the 0.6669 was WordNet-specific, rho 0.9034 was carried by the poor
     arms, instruments DISAGREE where it matters, 6.24 partially RE-OPENS -- **the informative case,
     NOT "mixed"**; (C) above chance but not separated -> **`POWER_INSUFFICIENT`, NOT a ceiling.***
  2. **BIOLOGY DRILL: role vs filler** -- how cortex represents a word's grammatical role, whether
     role is coded separately from the word filling it, and **whether our coarse corruption-tolerant
     role profile REPLICATES something real or is a symptom of an impoverished encoding.** *That
     second reading is the one that would deflate tonight's result, which is why the drill was told
     to argue both.* Writes a note only; touches no cell.
- **âš ï¸ WHY (C) IS A LIVE OUTCOME, NOT A HEDGE: the human population is n=65 against the WordNet
  instrument's n=242 -- 3.7x smaller -- and v4's human CI half-widths run ~0.10, WIDE ENOUGH TO
  SWALLOW THE ENTIRE 0.6669-vs-0.5943 MARGIN BEFORE ANY CAPABILITY QUESTION IS ASKED.** *Do not let
  a width be read as an effect in either direction.*
  **This is NOT evidence it is dead.** I misread agent silence as death twice tonight and was wrong
  both times -- once standing down a healthy agent that was authoring a 58 KB cell. **Do not respawn
  it; a duplicate is the more expensive error.**
  **NEITHER MAY BE HEADLINED ALONE.** Pre-commitment 6.35 governs (a): it is one half of a
  cross-corpus PAIR with the landed SimpleWiki arm, and *"one of two independent tests is not a
  result"*. **If the two DISAGREE that is the informative case and must NOT be reported as "mixed".**
- **SUPERSEDED IN-FLIGHT NOTE (2026-08-18 ~04:45):** (a) **typed-role write rule** (re-dispatched tight after the
  first attempt stalled an hour on my own over-broad enumeration instruction); (b) **frequency-
  stratified matcher** -- matches WITHIN frequency bands instead of one global caliper, to fix the
  n=7 cause above. **Its gate is unchanged: if it buys n but ANY floor leaves chance, it is REJECTED
  as a worse matcher.** A bigger sample of an unlicensed instrument is worse than no sample.
- **SUPERSEDED IN-FLIGHT NOTE (2026-08-18 ~04:20):**
  (1) **`typed-role write rule`** -- the FIRST arm in ~15 experiments to use the GRAMMATICAL RELATION
  rather than an unordered bag of words. *Every prior arm varied WHICH words counted or HOW they were
  weighted; none used the role label.* Uses `data/selectional_preferences_v1/` (41,529 verb+ROLE
  slots, 90.0% coverage of the 617 scored words, no WordNet, no LLM). Carries an UNTYPED
  same-coverage twin so a win cannot be credited to TYPE when it is really SELECTION, plus
  label-permuted / magnitude-permuted / coverage-matched controls (SET_P 218 vs SET_S 185 coverage
  asymmetry is the flagged artifact risk).
  (2) **`human instrument v2`** -- rebuilt on ITS OWN population after v1 collapsed to **n=7**. That
  collapse was a DESIGN error, not sampling: the deciding statistic is a RANK CORRELATION OVER ARMS,
  which does not require shared ITEMS, and restricting to the WordNet instrument's 617 words threw
  away ~550 of 573 usable SimLex pairs. **Absolute AUCs will NOT be comparable across the two
  instruments -- ONLY the ordering.** See `PLAN_ORGAN_STEP_LADDERS` 6.30.
- **DISK IS FINE (checked 04:20):** one KB staging dir at ~0 MB (not the documented 10.65 GB
  runaway), 456 GB free. The main director KB is **16.4 GB** and answers every query with nothing.
- **🚨 THE MANDATORY PRIOR-WORK CHECK IS NON-FUNCTIONAL. `CLAUDE.md`'s SESSION STARTUP RITUAL TELLS
  YOU TO RUN IT AS "THE LOAD-BEARING FIRST ACTION". DO NOT TRUST ITS ANSWER.** Measured 2026-08-18,
  both interpreters, twice: `tools/substrate_query.sh` and `tools/director_kb_query.py` **return ZERO
  BYTES and exit 0** after ~38-51 s. Bare `python` resolves fine (3.12.10), so this is NOT the
  venv trap and NOT a hang -- the tool runs, prints nothing, and reports success. **AN EMPTY RESULT
  IS NOT EVIDENCE OF ABSENCE**, and this project has a standing rule that an absence claim requires
  an ENUMERATION. **Every "not a rediscovery" claim made through this tool is unsupported.**
  **DO INSTEAD, and SAY WHICH YOU DID:** `ls notes/ | grep -i <topic>` then READ the hits; `os.walk`
  over `data/` for `metrics.json`, then reconcile to the registry, never the reverse.
  **PROVEN COST:** enumerating by hand on 2026-08-18 found `exp_pc1_predictive_coding_residual_gate_v1`
  (2026-06-22) -- the SAME write-gate mechanism as `e822eeaaf`, uncited in its brief. *It turned out
  to REPLICATE tonight's null on a different substrate and instrument, which is a gain, but it was
  found by hand and not by the tool that exists to find it.* Header of `substrate_query.sh` carries
  the full measurement; a 25 s guard was added there and is marked **UNPROVEN** because its firing
  could not be demonstrated.
- **WRITE-RULE ORGAN, GATE STATE (2026-08-18).** `CODE` **EXONERATED TWICE** (`ac629b1e7` -- a learned
  basis is MATCHED by a same-rank RANDOM basis; nothing moves composition; drill 1's prediction is
  REFUTED). `ACCUMULATE` **GATED = the INTERFERENCE source** (`b6cad69ca`). **The DISSOCIATION
  INSTRUMENT IS LICENSED** (`0eb44eb1d`) -- four floors AT CHANCE and verified there, the first such
  instrument this programme owns; incumbent AUC **0.0710**, single-occurrence **0.4173**, above 0.5
  would mean substitutability. `FILTER` and `SUPERPOSE` are the two steps still UNGATED.
- **ONE AGENT LIVE:** `noncollapse-maxpool` -- the organ's decisive build. Scores MAX-over-occurrences
  vs the incumbent SUM on the licensed dissociation instrument, with `N1_MAXPOOL_RANDOM_OCC` as the
  control that decides whether any gain is the mechanism or merely the max operator. Do NOT edit
  `experiments/` or `hdlab/` while it runs. **It replaces `exp_organ_f_noncollapsing_accumulation_v1`,
  which was KILLED at ~9 h projected runtime (spherical k-means per anchor); that cell is on disk,
  self-tested, and is NOT the current attempt.**
- **THE OVERNIGHT LOOP IS FIXED AND VERIFIED (2026-08-18), after running exactly ONE turn for days.**
  Three defects, all real: the `Stop` hook was registered ONLY in `hd-instrument/.claude/settings.json`
  which is NOT the session's project root, so it never executed (canary silent since 08-13) -- now
  registered in `D:/AI/.claude/settings.json` beside the SessionStart hook that demonstrably fires;
  `_plan_path()` resolved only `PLAN_NEXT_12H.md`/`PLAN.md`, NEITHER OF WHICH EXISTS, so every
  continuation pointed at a missing file; and **GUARD 1 returned on `stop_hook_active`
  unconditionally, so the chain could continue ONCE and the cap of 200 was unreachable by
  construction.** GUARD 1 now continues while ARMED, bounded by the cap AND a 20 s wall-clock floor;
  DISARMED behaviour is unchanged. GUARD 1D narrowed to `permission-rule` + `user-rejected` only
  (owner ruling) -- `cancelled` teardowns are logged, never halt. Self-test OVERALL PASS.
- `.claude/scan-out/` REFUSES FILE CREATION (4x); `notes/ tools/ experiments/ verification/` accept.
  `experiments/exp_propose_reject_retrieval_v1.py` IS A BLOCKED PATH -- OWNER'S CALL, never retry a
  variant.
- NO BACKUP, gitignored: `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB).
  Also gitignored and citation-bearing: `scratch/sparsify_right_object/` (the Q13 sparsity numbers).
- Three `data/cornerstone_results/*/metrics.json` are deleted in the working tree but PRESENT in
  git (`39cc197ff`) -- recoverable, not lost; nobody has decided whether the deletion was intended.
- USER AUTH: `d=256->1024` (rewrites every anchor store; the phase-diagram pass says it is justified
  for the comparison job and NOT for addressing), merge to `origin/main`, any push. Autoloop ARMED
  at 200.
- `hd_director_kb_continuous_ingest` LIVELOCKED (10.65 GB, self-killed at 45 min) while the
  scheduler reports it healthy -- `director_kb_query.py` and `substrate_query.sh` are STALE and
  `substrate_query.sh` currently ERRORS on a locked cache file rather than returning no hits.
- **DATA HAZARD FOUND AND FIXED 2026-08-17 -- THIS ENTRY'S EARLIER WORDING IS SUPERSEDED.** It read
  "`notes/LONG_TERM_PLAN.md` HAS NEVER BEEN COMMITTED", which was true when written. **It is now
  TRACKED, committed unchanged at `0c8d202d7`** (`git log -- notes/LONG_TERM_PLAN.md` returns that
  one commit; the working tree is clean against it at 32,823 B). The hazard is closed; the staleness
  below is not.
- `LONG_TERM_PLAN.md` also stale: sec 2 rows 3/4/6 superseded by STORAGE + C30; sec 4's dual-hub
  `[PINNED]` (line 185) should drop to CONTESTED; its Phase 2 kill banner (line 343) is recorded as
  FIRED without the 8b(B) withdrawal-for-thematic. Director's call, NOT done here (PLAN sec 9).
- OVER CAP AND DELIBERATELY SO, AND THE GAP GREW AGAIN: **19,450 B against the 8,704 cap** (11,571 B
  on 08-16, 15,149 B after the first 08-17 docs pass, this figure after the third). The new growth is
  never-trim class -- five landed results, DO-NOT-REDO 44/45/46 each with a revival criterion, C36 --
  offset only partly by tier trims to PHASE DIAGRAM, BRIDGING and STORAGE. **`STATUS_SPEC.md` sec 7's
  own measurement is now stale by ~7.9 KB and BOTH of its options (raise to 12,288 B; move the stub
  index into an uncapped `STATUS_CLOSED.md`, which was sized to land this file at ~8,580 B) are now
  undersized -- re-measure before enacting either.** Still PROPOSED, NOT ENACTED: DIRECTOR'S CALL.
  Never close the gap by evicting a never-trim entry.

## C37 -- "B1 IS A CLIFF" -- FULL TEXT MOVED FROM `STATUS.md` 2026-08-22 (testbed split pass); stubbed in `STATUS.md` DO NOT REDO/CORRECTIONS list as "C37"

**C37 "B1 IS A CLIFF: ours 0.931/0.304/0.002 vs counting 0.859/0.852/0.830" -- WITHDRAWN/INVERTED.**
Those are cos_syn/cos_rel/cos_unrel (SYNONYM/RELATED/UNRELATED), NOT vocabulary strata. A LOW tier-3
is the GOAL -- vessel vs anger should read ~0 -- so OUR 0.002 IS CORRECT AND COUNTING'S 0.830 IS THE
DEFECT: its syn-to-unrel range is 0.0285 vs our 0.9287, hence ordered_frac 0.379 vs 0.966. "The bar
is 0.830" is VOID, it targeted the baseline's PATHOLOGY. Coverage 29/29 on ALL arms: NO tier
measures out-of-lexicon behaviour. Survives: the cell's own coverage_scope, 86 hand-authored
concepts, open-vocabulary "NOT claimed here". CAUSE: took "cliff" from ORGAN_MAP and propagated to
3 docs without opening metrics.json -- the defining phrase sat in the SAME verdict sentence I lifted
the numbers from. A DOCUMENT'S INTERPRETATION IS NOT EVIDENCE; DISK-VERIFY OUR OWN NOTES, ORGAN_MAP
INCLUDED. Caught ONLY by asking whether the FIX could reach the problem -- which also TESTS WHETHER
THE PROBLEM IS REAL.

## STANDING DISCIPLINES 14-18 -- FULL TEXT MOVED FROM `STATUS.md` 2026-08-22 (testbed split pass, STATUS_SPEC sec 7)

`STATUS.md` was 55,070 B against the 28,672 B cap (1.92x). These five disciplines were carried there
in full prose rather than as one-line stubs (unlike disciplines 1-13, which were already condensed).
Moved here verbatim; `STATUS.md` now carries a one-line stub for each, per STATUS_SPEC sec 2's
contract ("nothing may appear here that is not stubbed by name in `STATUS.md`"). 14 and 15 already
had partial prior homes in this file (14 at "THE ERROR PATTERN THAT PRODUCED C32-C34" above; 15 at
"STANDING DISCIPLINES -- entry added 2026-08-17" above) -- kept here anyway, in `STATUS.md`'s more
refined final wording, so the stub contract does not depend on reconciling two phrasings.

### 14. Report the CI half-width and the null p95 beside every margin -- a width is not an effect
REPORT THE CI HALF-WIDTH AND THE NULL p95 AT THAT n BESIDE EVERY MARGIN -- A WIDTH IS NOT AN EFFECT.
Cost 3x in one night (C32/C33/C34), each an UNDERPOWERED NULL read as a CAPABILITY STATEMENT; at
n=86 the "floor" WAS the null distribution's own spread.

### 15. A grid's resolution is part of its verdict
A GRID'S RESOLUTION IS PART OF ITS VERDICT: an equality reported on a 3-value grid is a BIN, not a
measurement (C35). State the swept values and the number of queries per point beside every "no
difference".

### 16. A floor is specific to the representation it was computed on, not only to the population
A FLOOR IS SPECIFIC TO THE REPRESENTATION IT WAS COMPUTED ON, NOT ONLY TO THE POPULATION -- AND
THIS RULE EXISTS BECAUSE RULE 8 AS WRITTEN COULD NOT CATCH THE VIOLATION. 0.5431 was computed on
the BAG-of-words representation and quoted as "THE bar" across `STATUS.md` and the plan for two
days -- including in the banner that corrected everyone for saying 0.5 -- then applied to arms
built on grammatical ARCS. Rebuilt on the arc representation, a no-words attestation floor read
0.6317 [0.5820, 0.6781] against a 0.6669 headline: the gate was meaningless and the coverage
control could not catch it (`COVERAGE_MIN=3` dropped 0 of 242 pairs). Same population, same
scorer, same gold -- so rules 8 and 11 both PASSED while the comparison was already void. STATE
THE REPRESENTATION BESIDE EVERY FLOOR, AND REBUILD THE FLOOR WHENEVER THE REPRESENTATION CHANGES,
EVEN IF NOTHING ELSE DID. Corollary, earned the same night: a control with a threshold that
excludes nothing is not a control -- report how many items each control actually removed.

### 17. Every negative gets a brain-fidelity drill, every time
OWNER INSTRUCTION 2026-08-18 (COMMENTARY): "All negative results you should drill (safely -- we
shouldn't be giving away any of our substrate specifics here) for brain fidelity and what we should
do to get closer to that -- every time." A negative is not filed until it has been asked: WHICH
BRAIN STRUCTURE performs this operation, are we REPLICATING it or SUBSTITUTING something
convenient, and WHAT WOULD CLOSE THE GAP? This is not new doctrine -- it is the standing rule made
non-optional and applied at the moment of the negative rather than in a later drill that may never
happen. SAFETY CLAUSE, OWNER EXPLICIT: NEVER PUT OUR SUBSTRATE SPECIFICS INTO AN EXTERNAL QUERY.
Research drills ask about the BIOLOGY in general terms -- "how does cortex represent grammatical
role" -- never about our architecture, our organs, our operators, our dimensionalities or our
results. Web search is a one-way door; a query naming our design is disclosure that cannot be
recalled. AND THE FIRST QUESTION OF ANY SUCH DRILL IS WHETHER THE NEGATIVE IS EVEN REAL: on
2026-08-18, FOUR of the night's "negatives" were MEASUREMENT DEFECTS, not results -- a bar computed
on the wrong representation, an error rule applied to the wrong channel, an instrument with 10.9%
coverage of the arm it was testing, and a corruption control that was near rank-preserving and so
incapable of failing. Drilling a defect for brain fidelity would have produced a confident, wrong
story about the brain. ESTABLISH THAT THE EXPERIMENT COULD HAVE SUCCEEDED BEFORE ASKING WHY THE
BRAIN SUCCEEDS WHERE WE DID NOT.

### 18. Gate on the floor's upper bound, not its point value
GATE ON THE FLOOR'S UPPER BOUND, NOT ITS POINT VALUE -- AND IF NO ACHIEVABLE SCORE COULD CLEAR IT,
THE POINT IS UNTESTABLE, NOT NEGATIVE. A floor is an ESTIMATE and carries its own error bar, so
CREDIBLE BAR = floor + its own 95% half-width. Measured 08-18: WordNet 0.5431 -> 0.5944; human
0.5943 -> 0.6918; the binding arc floor 0.6317 -> 0.6810. `U1_TYPED_CONTEXT` 0.6669 clears the
floor and FAILS the credible bar -- this alone would have caught the night's retraction. AND THE
SECOND HALF IS THE ONE THAT CHANGES BEHAVIOUR: WHEN A FLOOR'S HALF-WIDTH IS SO WIDE THAT NO
ACHIEVABLE AUC COULD CLEAR ITS CREDIBLE BAR, THAT CONFIGURATION IS UNTESTABLE AND MUST NOT BE
FILED AS A FAILURE OF THE THING BEING TESTED. This is discipline 14 one level up: a width in the
FLOOR is not a GATE. Required per-cell n to tighten a floor: +-0.05 ~250-290, +-0.03 ~770, +-0.02
~1,550-1,780, +-0.01 ~6,300-7,200 -- the human instrument runs at 65. BEFORE BUILDING AN ARM,
DECIDE WHAT n ITS INSTRUMENT NEEDS; IF THAT n IS UNREACHABLE, THE ARM IS NOT YET WORTH BUILDING.
Never buy n by loosening the matcher -- a bigger sample of an unlicensed instrument is worse than
no sample.

## Q109 CREDIT-ASSIGNMENT INVESTIGATION (2026-08-22) -- moved out of `STATUS.md`'s header, stubbed as "Q109 CREDIT ASSIGNMENT"

Board Q109 asked what the autoloop should do (it can MEASURE/DOCUMENT/GUARD but not run an experiment
or edit a cell -- routed to `hdi_exp_dev`, agents off here -- so defects it finds get GUARDED, never
FIXED; 13 commits that day, zero capability code). Q108 was the same question with a too-broad premise
("the build lane is closed") and was WITHDRAWN within the hour -- `verification/` was open all along
and got used minutes later. Third wrong-premise question that week (Q103/Q104/Q108): the pattern is
filing before testing the constraint being complained about. Q104 was also WITHDRAWN, premise wrong --
approval was sought to build who-did-what-to-whom credit assignment; it already exists.
`_credit_targets` bounds each verb's own clause, takes the pre-verb SUBJECT + post-verb OBJECT
NP-head, and credits only if one links to the goal referent -- run, not read: "the girl stumbled
badly and the man laughed loudly" -> girl `['stumble']`, man `['laugh']`; proximity cannot do that.

**THE REAL HOLE WAS UPSTREAM: the morphological verb gate has RECALL 0.6026, never seeing 3,528 of
8,877 real verbs** (vs the UD tagger already loaded on the live path). Swapped in as a default-off
switch (`HD_VERB_GATE=tagger`): primary `0.4722 -> 0.6389`, exactly the majority floor -> still
`HARD_FAIL`. **The paired test refuses the gain: 9 fixed / 3 broken, McNemar exact p=0.1460** -- the
correct test is weaker than the unpaired one declined earlier (0.033). WITHDRAWN: that it is an
improvement. SURVIVES: it changes DECISIONS (12 of 36 flipped) where the `lemma_verb` repair changed
only labels. UNDERPOWERED != NEGATIVE: n=36 is the binding constraint on this whole line -- enlarging
the eval bank is worth more than any further mechanism change. `per_item_predictions` now ships by
default, so every future re-analysis of this cell is free. Separate older defect, both arms: light-verb
canary `neutral_rate 0.0`, `24/24`+`25/25` POLAR-LOCKED where the docstring calls the wash-out "the
pre-registered light-verb payoff".

## EVICTED FROM STATUS.md ON 2026-08-22 (WHAT IS RUNNING was 84 lines and almost none of it was running)

*Evicted per `STATUS_SPEC.md` sec 3/6/7 and STATUS's own standing instruction: when it fills,
EVICT to LESSONS, do not shave. Every entry below was already CLOSED and already cited its note;
what STATUS keeps is a one-line stub pointing here.*

- ✅ **Q112/OP1 FULLY CLOSED 08-22, DO NOT REOPEN: "238 overstated results" was a count of AUDIT
  FLAGS (re-scan: 286), not overstatements** -- `INADMISSIBLE_COMPARISON` 207 (incommensurable
  numbers), `UPHELD` 43, `NOT_SUPPORTED` 35 (marked in place, additive sidecar, no
  `metrics.json`/registry touched), 1 self-declared. 13 of the 35 are already in the capability
  registry. Tools self-tested. Full methodology: `notes/THE_238_OVERSTATED_RESULTS_WERE_NEVER_238_...md`.

- 🔻🔑 **SUBTRACTING CO-OCCURRENCE FROM THE VERB SCORE FAILS MONOTONICALLY** (best lambda = 0.0,
  held-out `-0.0005`, worse than a random penalty at every lambda -- co-occurrence is POSITIVELY
  correlated with human similarity, the antonym effect is real but swamped). **AND THE PROPAGATOR
  BUILT TO FIX IT ALREADY EXISTS, `HARD_PASS`**: `hdlab/wordnet_polarity_propagation.py`, a 12-word
  seed -> 0.833 on 12 held-out verbs (seed-ablation 0.000), predicting the OPPOSITE pole from
  WordNet antonyms. Every number here assigns one value per word where the plan specifies a
  context-conditioned superposition, so these are a FLOOR, not a test of it.
  `notes/THE_SUBTRACT_ARM_FAILED_AND_THE_PROPAGATOR_WE_NEEDED_WAS_ALREADY_BUILT_...md`.
- 🔑 **THE FORK IS ANSWERED: TEXT DOES SEPARATE OPPOSITES FROM SYNONYMS, AND WE INVERT IT.**
  Freq-matched, random-pair control passes: "X and/or Y" antonyms 0.0782 vs synonyms 0.0269 (2.91x)
  vs random 0.0022 (34.8x). Chain, every link measured: antonyms co-occur -> our encoder converts
  co-occurrence INTO similarity -> antonyms become our CLOSEST pairs (0.2062 > syn 0.1727) -> verbs
  read 0.0000. Not a missing feature, an inverted one. Limits: cohyponyms 2nd-closest (coordination,
  not antonymy); only 7.8% of antonym co-occurrences fire; no arm built.
  `notes/THE_SIGNAL_FOR_OPPOSITION_IS_IN_THE_TEXT_...md`.
- 🎯 **SEED PRICE MEASURED: ~50-100 grounded words already propagate; past ~400 more buys
  ~nothing** (concreteness: 50 at 0.2114 vs null 0.1239, 400 at 0.3783, 2000 at 0.4323). IDF at 200
  seeds (0.2971) still beats ours at 2,000 (0.2638) -- 16th measure where counting leads; our
  nearest-seed cosine is HIGHER while carrying LESS (anisotropy).
  `notes/HOW_SMALL_CAN_THE_GROUNDED_SEED_BE_...md`.

- ✅ **FINISHED AND CLOSED (one line each; detail is in the named note and in the plan's top block):**
  - **`exp_graded_vs_signed_query_v1` -- `np.sign` at `:776` COSTS ALMOST NOTHING. CLOSED.**
    `Q_GRADED 0.0480/median 37.0` vs `Q_SIGNED 0.0455/41.0`; paired `+0.0025` CI95
    `[-0.0030,+0.0080]` NOT SEPARATED; `:663`'s "worse than either" is unsupported at this scale.
    ⚠️ *Partly re-derived 08-21 without reading this entry first -- ninth prior-work catch.*
  - **`diagnose_read_with_loaded_foundation`: refusal delta `279 vs 380 = 1.36x`, NOT the 22x
    headline, which was 93% PRE-EXISTING.**
  - **`ReadResult.n_grounded` WAS STRUCTURALLY ALWAYS ZERO** -- `substrate.py:608` read
    `n_grounded_cumulative`, `checkpoint()` emits `cumulative_grounded`, **the same two words
    TRANSPOSED**. Now raises; self-tests PASS; no landed cell affected. **A STATIC scan for this bug
    class DOES NOT WORK (1,925 -> 132 suspects, all legitimate reads). WHAT FOUND IT WAS A
    CONTRADICTION BETWEEN TWO FIELDS OF ONE OUTPUT** (`n_grounded=0` beside `anchors +68`).
    ***Make outputs print quantities that CONSTRAIN EACH OTHER.***
  - **WHY WRITING LESS HELPS (owner Q98):** `exp_crosstalk_capacity_law_v1_gpu_v1`
    `MEASURED_MECHANISM` -- crosstalk over raw keys DOMINATES Hebbian capacity, **r 0.976, n=11**;
    rivals' partials go NEGATIVE. **Our keys sit AT the Welch bound, so "better keys" is closed by
    GEOMETRY; the two remaining levers are FEWER ITEMS and MORE DIMENSIONS.**



## EVICTED FROM STATUS.md ON 2026-08-22 (second pass -- room for the reproducibility findings)

*Both entries were CLOSED and both cite their notes. STATUS keeps a one-line stub.*

- 🔑 **THE OOV-36 ORGAN IS NOT ANSWERING WRONG, IT IS NOT ANSWERING: 20 of 22 errors are
  NON-ANSWERS; accuracy when it commits is 14/16 = 0.8750** -- coverage-limited, not
  discrimination-limited. Known-answer arm (8 in-lexicon controls) reads 4/8 = CHANCE (n=8
  INCONCLUSIVE, not negative). Chasing an `AMBIGUOUS` retraction found a real defect: it is an
  ABSTENTION in 5 consumers but a WRONG ANSWER by omission in the landed cell (OOV-36 unaffected
  today). Guard: `tools/score_with_abstention.py`, no signature returns a bare accuracy, 6/6.
  `notes/THE_LANDED_CELL_SCORES_ABSTENTIONS_AS_ERRORS_BY_OMISSION_...md`.
- 🚨 **THAT ORGAN'S LANDED `HARD_FAIL` IS STALE: measured where the cascade fired 0 of 36; re-read
  from the same checkpoint today it fires 10 of 36 (9 correct).** Verdict unchanged (still far
  below the 0.6389 floor), diagnosis changes. Re-landing needs a fresh cell run (`hdi_exp_dev`, not
  done here). `notes/THE_ORGAN_DOES_NOT_ANSWER_WRONG_...md`,
  `notes/THE_LANDED_HARD_FAIL_WAS_MEASURED_WHERE_...md`.



## EVICTED FROM STATUS.md ON 2026-08-23 (third pass -- headroom for the polarity results)

- 🚨 **STALE-ARTIFACT DEFECT IN THE BLIND SHEET: drawn from `v2_qualityfix` while `v3/v4/v5` also
  exist unmarked -- `draw_representative_blind_sample.py` has no notion of a CURRENT foundation.**
  True stem rate (round-trip detector): sheet `10.4%`, v2q `7.9%`, `v5_termboundary` `0.4%` -- but
  v5 is a DIFFERENT PIPELINE's fact dump (definienda, not subjects), not a later version, and only
  v1/v2q are LOADABLE. **STANDS: the grounding loop stores ~8% stemmer output, NOT known to be
  fixed.** *Three of my own corrections in one day, alternating direction -- full trail:*
  `notes/THE_GROUNDING_LOOP_STORES_8pc_STEMMER_OUTPUT_AND_I_WAS_WRONG_THREE_TIMES_...md`.



## EVICTED FROM STATUS.md ON 2026-08-23 (fourth pass -- it is now owned by a filed brief)

- 🚨🧠 **THE GENERIC-ATTRACTOR DEGENERACY'S CAUSE: NOTHING LOADS A FOUNDATION.**
  `self.foundation_dir` is assigned at `substrate.py:378` and NEVER READ AGAIN -- a dead parameter;
  runtime-measured `load_foundation` calls `= 0`. Makes the plan's own "way-attractor should fall
  as grounded vocabulary grows" prediction UNREACHABLE (cannot grow across runs; arithmetic, not
  tuning). NOT MEASURED: whether loading helps -- that is the next experiment.
  `notes/THE_ASSEMBLED_SUBSTRATE_NEVER_LOADS_A_FOUNDATION_...md`.



## EVICTED FROM STATUS.md ON 2026-08-23 (fifth pass -- room for the two-session reconciliation)

### 2026-08-21 -- THE THREE-WAY COMPARISON THAT DECIDES WHAT F5 BUILDS ON

| arm, paired hit@1 discrimination, 4 sets | median | verdict |
|---|---|---|
| untrained codebook (nothing read) | **~0** | CIs span zero -- donates nothing |
| **THE TRAINED SUBSTRATE** | **+16.3 pp** | **`REPLICATED`, all 4 CIs exclude zero** |
| second-order counting (**the bar**, upper bound **+44.2**) | +29.4 pp | `REPLICATED` |

**LEARNING BOUGHT SOMETHING REAL** -- 0 -> +16.3 pp, same representation and comparison, the only
difference being 7,535 sentences read. First replicated positive from our side on this task.
**AND IT DOES NOT CLEAR THE BAR** (best CI +30.8 vs gate +44.2), reproducing the standing position
*at or below counting* on a task that did not exist when that position was formed.
**AND THE PAIRED TEST NOW SAYS WE ARE MEASURABLY BEHIND, not merely not-ahead:
`SUBSTRATE - COUNTING = -0.142 per item over 478 items, 95% CI [-0.203, -0.082]`, SEPARATED.**
Marginal CIs overlapped, which is NOT a test of a difference; the paired test is.
⚠️ **SCOPED 08-22: this and every "behind counting" number is the WORD-SIMILARITY / RECALL channel,
which BOTH plans of record had already ruled out as the meaning signal (bow `0.5167` = chance HANDED
THE GOLD SENSE). It is NOT a statement about the grounding organ, where counting sits at chance and we
do not. Quote it WITH its channel.** `notes/THE_TRAINED_SUBSTRATE_SCORES_16pp_...md`



