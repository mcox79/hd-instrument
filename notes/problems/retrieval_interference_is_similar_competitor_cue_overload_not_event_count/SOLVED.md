---
problem: retrieval_interference_is_similar_competitor_cue_overload_not_event_count
status: PARTIAL
bar: "PASS = the content × TCM-context-reinstatement cue beats the content-only floor by ≥ +0.10 hit@1, CI-separated (bootstrap; CI half-width + null p95), with the info-free twin (shuffled/permuted context) LOSING, AND it beats naive-recency-alone (the documented tie) — i.e. the COMBINATION is load-bearing, not either cue alone."
result: "The reframe is CONFIRMED and the content×context bar is met — but by the ALREADY-LANDED organ, and BOTH candidate NEW memory-axis cues (the brief's multi-timescale TCM context, and morphological agreement) are rigorous negatives over the current substrate. On real LitBank pronoun coref (held-out TEST docs, n=3,378 ambiguous >=2-candidate queries): LANDED graded_antecedent_pick=0.676 vs content-only floor (frequency)=0.521 -> +0.155 CI-sep [+0.138,+0.172], beats naive recency (0.606), shuffled-context twin LOSES 0.676->0.436. (1) The brief's MULTI-TIMESCALE TCM cue: -0.001 [-0.009,+0.006] NOT_SEP = RIGOROUS NEGATIVE. (2) GENDER/NUMBER AGREEMENT: the already-landed PERSON pool-cleanup reproduces +0.038 [0.031,0.044]; gender's MARGINAL on top of it is +0.003 [0.001,0.005] NOT_SEP, number +0.004 NOT_SEP (+0.001±0.001 across 6 splits) = RIGOROUS NEGATIVE (vindicates the landed organ's own 'gender is a non-lever' note). Informational ceiling: two combination rules (additive 0.650, ACT-R Boltzmann 0.659) converge ~0.10 below the oracle-of-cues (0.763)."
floor: "Strongest floors, recomputed on the SAME held-out pronoun population: content-only frequency 0.521; naive recency 0.606; incumbent hard-tier 0.624; the LANDED graded_antecedent_pick 0.676 (the floor both new cues had to beat and did not, CI-separated); and for the agreement claim the correct baseline is the person-filtered picker 0.714 (gender/number had to beat THAT). who-did-what event-count proxy content floor 0.398 (reproduced; naive recency ties at 0.402)."
controls: "info-free shuffled-context twin (landed 0.676->0.436 -> temporal signal load-bearing); shuffled-phi twin for the agreement stack (0.720->0.609 -> person/agreement info load-bearing); PERSON-vs-GENDER decomposition (isolates gender's marginal from the already-landed person cleanup — the decisive control that caught v7's conflation: gender's apparent +0.040 was +0.038 person + 0.003 gender); reliability/cue-overload gate ablation (ON 0.639 < OFF 0.650 -> refutes the peakedness gate); cue-validity no-fit weighting (0.574 -> weights must be fit); oracle-of-cues 0.763 vs best combiner 0.659 not closed by a 2nd combination rule (Boltzmann≈additive -> combination rule is not the bottleneck); LANDED+TCM vs LANDED -0.001 NOT_SEP (multi-timescale organ adds nothing over single-timescale recency); cross-split robustness 6 doc splits (person win 6/6, gender marginal +0.001±0.001); who-did-what proxy 0.398 with recency tie (event-count is not the driver -> confirms the reframe)."
files_changed: "experiments/exp_similar_competitor_pronoun_diagnostic_v1.py, experiments/exp_similar_competitor_actr_tcm_combiner_v1.py, experiments/exp_similar_competitor_actr_tcm_combiner_v2.py, experiments/exp_similar_competitor_actr_tcm_combiner_v3.py, experiments/exp_similar_competitor_actr_tcm_combiner_v4_robust.py, experiments/exp_similar_competitor_actr_boltzmann_ceiling_v5.py, experiments/exp_similar_competitor_vs_landed_gradedpick_v6.py, experiments/exp_similar_competitor_agreement_cue_v7.py, experiments/exp_similar_competitor_agreement_decomposition_v8.py, verification/test_similar_competitor_retrieval.py, notes/problems/retrieval_interference_is_similar_competitor_cue_overload_not_event_count/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_similar_competitor_retrieval.py"
---

# PARTIAL — the reframe is right; the right-axis organ already exists; every NEW memory-axis cue I could build is a rigorous negative → the residual is structural

## Which brain structure, and are we replicating or substituting?
Similar-competitor / partial-cue reference resolution ("which earlier thing does *she/it* point to when two match")
is **cue-based content-addressable retrieval** from a working memory of partially-active antecedents (Lewis &
Vasishth 2005 activation-based ACT-R; Van Dyke & McElree 2006 cue-overload; MacWhinney Competition Model; Arnold
2010 accessibility; Howard & Kahana 2002 TCM; Grosz/Joshi/Weinstein Centering). We **replicate the operation** —
and it turns out the substrate already does: `hdlab/graded_coref_pick.py::graded_antecedent_pick` (from the
integrated `coreference_is_capped_at_065_on_real_narrative`, SOLVED/EXCELLENT, owner-DONE) fuses recency +
subjecthood + ACT-R base-level + backward-center + parallelism via `graded_competition`, with an already-landed
person/animacy candidate-pool cleanup (`phi_agreement_keep`, `keep_after_pool_cleanup`).

## The result, in one line
The reframe (event-count → similar-competitor cue-overload) is confirmed; the content×context bar is met **by the
already-landed organ**; and the two plausible NEW memory-axis cues — the brief's multi-timescale TCM context, and
morphological agreement (gender/number) — are **both rigorous negatives over the current substrate**. That
*exhausts the memory axis* and localizes the residual to the structural/semantic axis, which is exactly what the
brief said a memory-route negative should do.

## What I measured (held-out TEST docs; a 14-check scaffold-free witness recomputes every number from source)
1. **Reframe CONFIRMED.** who-did-what event-count proxy: naive recency 0.402 ties content-only 0.398 (event-count
   is not the driver). Real pronoun coref: content 0.521 < recency 0.606 < subject-recency 0.624; oracle "any cue
   right" = 0.763 → real complementary headroom.
2. **Content×context clears the bar — via the landed organ.** `graded_antecedent_pick` = **0.676**, +0.155 CI-sep
   over content-only, beats naive recency, shuffled-context twin LOSES (0.676→0.436). The brief's core thesis holds
   but was already delivered by a prior integrated problem.
3. **NEGATIVE #1 — the brief's multi-timescale TCM cue.** Adding `graded_temporal_context`'s multi-timescale
   base-level as a context cue: **−0.001 [−0.009,+0.006] NOT_SEP** over the landed picker. The organ's
   multi-timescale/event-segmented richness adds nothing over the single-timescale ACT-R recency already there.
4. **NEGATIVE #2 — morphological agreement (the brief's "feature-MATCHING competitors" content cue).** I built
   reliable per-entity gender/number from the FULL LitBank coref chains (gold agreement-compatible 88.8%, or 98.4%
   with conservative number). A naive comparison looked like a +0.040 win — but the decomposition control shows
   that was the **already-landed PERSON pool-cleanup** (+0.038); gender's *marginal on top of person* is **+0.003
   [0.001,0.005] NOT_SEP**, number +0.004 NOT_SEP, +0.001±0.001 across 6 splits. Rigorous negative — and it
   *vindicates* the landed organ's own note that gender is a non-lever for these competitors.
5. **The plateau is INFORMATIONAL, not a combination-rule limit.** The faithful ACT-R Boltzmann retrieval (0.659)
   barely beats crude additive coord-ascent (0.650); both sit ~0.10 below the oracle-of-cues (0.763). A better
   *combination* of the accessibility cues does not help; the residual needs information the memory axis lacks.
6. **The residual is MEASURABLY structural (not an assertion).** Against the current-best substrate (landed picker
   + person cleanup = 0.714 held-out): only 7.9% of golds have no prior mention (cataphora/same-clause →
   UNREACHABLE by any memory cue), so the hard ceiling is 0.921. Of the 966 errors, **72% are STRUCTURAL** — the
   gold IS a prior-mentioned candidate but no accessibility ranking selects it (Binding / coherence / verb-semantics
   territory) — and only 28% are unreachable. The reachable-but-unsolved headroom (~0.21) is almost entirely
   structural. This is *why* every memory cue plateaus.
7. **The validated organ is an ISLAND — the real lever is WIRING, not a new cue.** `graded_antecedent_pick` has
   ZERO callers in hdlab (grep-verified); the live `situation_reader` resolves coref via the older
   `hdlab.coref` + `EventCentralityReader`, not the validated graded picker. So the +0.155-over-content /
   +0.053-over-hard-tier win is not currently delivered in `read()`. (I could not run the reader's live coref stack
   on this candidate-set cache to measure the exact wiring delta — that verification is the strategy session's,
   and it is the highest-value action for this problem's GOAL.)

## What I did NOT establish / would withdraw first
- **No NEW organ beats the current substrate.** The memory-axis win is the already-landed `graded_antecedent_pick`
  + person cleanup; my v1–v5 re-derived the picker and v7 initially over-attributed the person win to gender.
- The oracle (0.763) is optimistic (it peeks at the gold to pick the cue); the realistic fixed-combiner ceiling on
  these cues is ~0.66. I do not claim 0.76 is reachable from memory/accessibility + agreement.
- Agreement's negative is *marginal over the landed person filter*, on LitBank fiction with mention-derived phi
  (16% of entities have overt gender). A corpus with denser phi or first-person-heavy dialogue could shift it; I'd
  re-test there before calling it universal.

## KEY REALIZATIONS (the enabling moves)
1. **Ask whether the experiment COULD succeed first.** The oracle-of-cues diagnostic (0.763 vs best single 0.620)
   proved the cues were complementary BEFORE building any combiner — and on the who-did-what proxy the same check
   shows they *agree* (no headroom), which is why recency tied content there.
2. **The disk outranks the brief's instrument.** "content 0.398, recency ties it" is a who-did-what-proxy artifact;
   on real pronoun coref recency already beats content.
3. **Read the landed substrate before claiming a build.** `graded_antecedent_pick` + the person cleanup were
   already there; the value moved to testing the brief's *deltas*, not re-proving the base.
4. **A control that decomposes a win by SOURCE is worth more than the win.** The person-vs-gender decomposition
   caught that a plausible +0.040 "gender win" was +0.038 already-landed person cleanup + 0.003 gender. Without it I
   would have shipped a false new capability. (The scaffold-free witness is what forced the decomposition — its
   independent recompute disagreed with the experiment cell, and the cell was wrong.)
5. **A tight NOT_SEP is the cleanest negative.** −0.001 [−0.009,+0.006] (TCM) and +0.003 [0.001,0.005] (gender) are
   *indistinguishable-from-nothing*, not noisy near-misses — strong evidence the memory axis is saturated.
6. **A fidelity bug in the ESTIMATE is not a fact about the brain.** My first agreement attempt failed at 36%
   gold-compatibility because phi came from sparse action-mentions; rebuilt from the full coref chains it hit 98%.
   Number "failed" only because of singular-"they"; a gendered-pronoun→singular rule fixed the inference. Neither
   changed the final verdict, but each is why the negative is trustworthy rather than an artifact.

## PROPOSED hdlab ACTION (strategy lands; Q111) — all "do NOT", plus one wiring flag
- **Do NOT wire `graded_temporal_context` (multi-timescale TCM) into coref antecedent retrieval** (−0.001, NOT_SEP
  over single-timescale recency). It remains correct where it IS wired (`factorized_entity_store`,
  `belief_timeline`); this negative is specific to linear-order antecedent selection.
- **Do NOT add a gender/number agreement filter to the coref pool** beyond the existing person/animacy cleanup:
  gender's marginal is +0.003 (NOT_SEP), number +0.004 (NOT_SEP). The landed `phi_agreement_keep` (person+animacy)
  already captures the available agreement signal; gender/number is saturated.
- **Confirm `resolve_retrieval_interference` (event-count organ) OFF-AXIS** for reference interference (recency
  ties content on the event-count proxy).
- **WIRE the validated picker (the #1 action, verdict-independent):** `graded_antecedent_pick` is an ISLAND (zero
  hdlab callers; the live reader uses `hdlab.coref` + `EventCentralityReader`). It is validated on this population
  (+0.155 over content, +0.053 over the hard-tier incumbent). Routing the live `read()` coref path through it is
  the real remaining gain for this problem's goal — a wiring job, not a build. STRATEGY should first measure the
  graded picker vs the reader's CURRENT live coref on the same gold (I could not drive the reader's coref stack from
  this candidate-set cache), then wire if it wins.

## Adjacent components — brain-fidelity + optimization (seeds for the next problems)
- **`graded_antecedent_pick` + `phi_agreement_keep` (LANDED):** HIGH fidelity (ACT-R + Competition Model +
  Centering + obligatory person/animacy agreement). At its informational ceiling on the memory axis (~0.68–0.71 on
  ambiguous LitBank pronouns). Optimization is NOT in more memory cues (proven, twice).
- **`graded_temporal_context` — `EventSegmentedContext` (LANDED, untested for coref):** the one TCM variant I did
  NOT refute — drift that jumps at event boundaries (Zwaan; DuBrow & Davachi). Needs an event-boundary detector
  wired and boundary annotation to evaluate; speculative but the only remaining TCM lever.
- **The STRUCTURAL / SEMANTIC axis (NOT built as coref cues) — the residual's true home.** Binding Theory
  (Principles A/B/C), coherence relations (Kehler 2002), verb selectional restrictions. The oracle residual (0.68
  → 0.76) requires knowing *which* cue to trust per query, which needs the parse. This composes with the
  extraction-front-end parse work and is the strongest candidate follow-on problem.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b)
- **Retrieval interference = similar-competitor cue-overload, NOT event-count — CONFIRMED on real text** (event-count
  proxy: recency ties content 0.398 vs 0.402; real pronoun coref: cue combination beats content +0.155).
- **The working context-reinstatement cue is single-timescale recency / ACT-R base-level, already in
  `graded_antecedent_pick`.** The MULTI-TIMESCALE TCM organ adds nothing over it for linear-order antecedent
  retrieval (−0.001, NOT_SEP). Log: "TCM multi-timescale value confirmed in episodic store / belief timeline, NOT
  in coref antecedent order."
- **Morphological gender/number agreement is a NON-LEVER for coref over the landed person/animacy cleanup** (+0.003
  / +0.004, NOT_SEP). This CONFIRMS (does not challenge) `graded_coref_pick`'s note. Person/animacy is the
  agreement signal that pays; gender/number is saturated.
- **The coref memory axis is at its informational ceiling (~0.68–0.71; oracle 0.76).** The residual is the
  structural/semantic axis, not any memory feature. Combination rule proven not to be the bottleneck.

## TLDR (plain language)
Working out who "she" or "it" means gets hard when several earlier things half-match — and the hoped-for fixes were
a fancier "when did I last see it" clock and a "match the gender/number" check. I tested both on nine thousand real
pronoun cases from a hundred novels. The reframing is right (busyness doesn't matter; look-alike competition does),
and the good method that blends *what* with *when* clearly beats going on words alone — but it's already built and
switched on from earlier work. The two new gadgets both turned out to make no real difference: the fancier clock
adds nothing the simple one didn't already have, and gender/number matching adds nothing once you've already
removed the narrator ("I"/"you") from the candidates, which the system also already does. Two dead ends measured
cleanly, not guessed. That's actually the useful finding: the memory side of this is done, and the remaining hard
cases need a different kind of information — the sentence's grammar and meaning — which is a separate job. (I also
had to correct myself mid-way: a gender result looked like a win until a check showed the gain was really the
already-built narrator-removal step, not gender.)

## QUESTIONS
None blocking. Flag for strategy: the one lever that survives is the grammar/meaning (structural) axis — its own
problem, mapped above.

## NEXT STEPS
1. **WIRE (the highest-value action):** measure the validated `graded_antecedent_pick` vs the reader's CURRENT live
   coref (`hdlab.coref` + `EventCentralityReader`) on the same gold, and route `read()` through it if it wins. It is
   an island today (validated, not called) — this delivers the memory-axis win that is otherwise unrealised.
2. **Land the "do-NOTs":** don't wire the multi-timescale TCM organ or a gender/number agreement filter into coref
   (both measured saturated over the current substrate); keep the event-count organ off the coref path.
3. **File the structural/semantic coref problem** (Binding Theory + coherence + verb semantics) — measured to own
   ~72% of the remaining errors and the reachable headroom to the 0.921 ceiling; composes with the extraction
   front-end. Optionally probe `EventSegmentedContext` once an event-boundary detector exists (the one memory lever
   left untested — not half-tested here, to avoid an unfair test with a bad boundary proxy).

---

## INTEGRATED_BY_STRATEGY 2026-08-31 -- STRONG (rigorous negative; NO reader landing)

Reverified 18/18 FIRST-HAND (`verification/test_similar_competitor_retrieval.py`, held-out LitBank pronoun coref
n=3,378): reframe CONFIRMED (event-count proxy 0.398, recency ties 0.402); the landed `graded_antecedent_pick`
owns the axis (0.676 vs content 0.521, +0.155 CI-sep, shuffled-context twin loses 0.436); BOTH new cues are
RIGOROUS NEGATIVES (multi-timescale TCM -0.001 NOT_SEP; gender +0.003 / number +0.004 NOT_SEP over the +0.038
person cleanup); residual is STRUCTURAL (reachable ceiling 0.921, 72% errors gold-present-but-not-most-accessible;
combiners converge ~0.10 below oracle 0.763). Self-corrected a v7 person/gender conflation. Graded STRONG.

**LANDING STATE: NO hdlab landing (correct no-landing).** Both candidate new memory-axis cues are CI-separated
negatives and the right-axis organ (`graded_antecedent_pick`) is already landed — nothing new to wire. The route
"add a memory-axis cue to beat similar-competitor retrieval interference" is CLOSED. The residual is a STRUCTURAL /
accessibility-ranking problem (Centering-style most-accessible-antecedent selection; 72% of errors have the gold
present but not most-accessible), NOT a cue-overload or event-count problem. Recorded in WIRING_MAP non-debt. No
hdlab file changed.

**SEEDED (verdict-independent):** the structural residual points at a Centering/accessibility most-accessible-
antecedent selection lever (72% of errors are gold-present-but-mis-ranked) — a candidate future problem distinct
from cue-overload, but the ~0.10-below-oracle gap is small and the coref area is heavily worked; do NOT package
without checking it is not a re-tread of the coref-residual / focus-stack negatives.
