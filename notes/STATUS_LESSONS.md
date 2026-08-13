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
