# Research: what structural capability is missing for learning to COMPOUND (5x biology-led drill)

Date: 2026-07-18. Filed by: research (3 parallel Sonnet lit-scan sub-agents — human/developmental; neuroscience
schema-timing + prioritized replay; classical-cognitive-architecture + modern ML — synthesized by director against
an extensive, already-landed internal research thread on schema-gated consolidation, 07-14 through 07-17). This
drill does NOT re-derive what is already built out on-disk; it (a) fills three genuinely new angles the existing
thread had not yet covered (Matthew effect/chunking/Bransford; exact Tse timing numbers + Mattar-Daw prioritized
replay; ACT-R/SOAR/MAML/EWC/NTM), and (b) makes the connective diagnosis the existing notes had not yet stated
explicitly: that the SPECIFIC negatives handed to this drill (flat re-reading, null curriculum order, budget-flat
CLS replay, no schema-selection headroom) are jointly overdetermined by ONE missing structural property, not four
unrelated weaknesses. Generic biology/cog-sci/ML terms only used in all external queries; no substrate-novel
mechanism names, configs, or numbers went off-platform.

---

## HEADLINE

**All three lit-scans, and the pre-existing internal thread, converge on the same answer: the substrate has the
right THREE PRIMITIVES (surprise, schema-fit, recurrence) but is running them as a ONE-SHOT, FLAT-COST gate,
whereas every literature examined here — human development, neuroscience, classical cognitive architecture, and
modern ML — treats compounding as requiring a persistent abstraction/schema layer whose CONSOLIDATION COST is a
graded, continuously-recomputed function of fit-to-that-layer, applied BOTH at first write AND at re-exposure of
already-written material. The substrate currently has neither half: cost is flat (a rehearsal-percentage budget,
not schema-weighted allocation) and eligibility is one-shot (a gate fires once at arrival; there is no mechanism to
revise an already-consolidated-but-wrong entry on re-encounter). This single joint gap explains all four negatives
without needing four separate explanations, and it is independently confirmed as the same gap by the human
literature (Matthew effect / chunking / Bransford schema-priming / Harlow learning sets), the neuroscience
literature (Tse 2007/2011's exact 1-trial/48h vs. weeks number, van Kesteren's variable hippocampal "dose," Mattar
& Daw's gain x need concentrated replay, McClelland's own 2013 revision of CLS), and the ML literature (ACT-R
production compilation, SOAR chunking, EWC's Fisher-weighted variable protection, the Bayesian hierarchical
concept-learning split, and the standard forward-transfer measurement protocol). Deflated per lit-scan-calibration
discipline; this is a stitched, novel-for-this-substrate synthesis, capped below the mandatory P<=0.50 ceiling —
**P_deflated = 0.45** for the overall structural verdict, higher (0.60-0.75, established literature) for each
individual cited mechanism.

---

## (1) HUMAN / DEVELOPMENTAL angle

| Finding | Citation (best-verified) | Mechanism | Structure implied |
|---|---|---|---|
| Matthew effect in reading | Stanovich 1986, *Reading Research Quarterly* | early decoding fluency -> more reading -> more vocabulary/knowledge -> easier future reading; explicitly framed as RECIPROCAL causation, not a one-time head start | a persistent long-term vocabulary/semantic store that accumulates across episodes, PLUS an automaticity mechanism that frees capacity to feed it |
| Chunking / expertise | Chase & Simon 1973 (chess); Miller 1956; Cowan 2001 revision (~4 slots) | experts don't have bigger raw WM, they have a large (10,000-100,000-item) reusable chunk library in long-term memory, retrieved as single WM units DURING perception | a chunk/pattern store consulted at encoding time, not just recall |
| Schema-primed comprehension | Bransford & Johnson 1972; Anderson & Pichert 1978 | a relevant schema given BEFORE reading roughly doubled recall (8 vs 3.6/14 idea units); Anderson & Pichert then showed the SAME schema is redeployed at retrieval as a search template (a later schema-shift changes what's recoverable) | schema used prospectively (encoding organizer) AND again at retrieval (search template) — two uses of one persistent structure |
| Vocabulary coverage threshold | Hu & Nation 2000 (partial-replication caveat: Kremmel et al.) | ~95-98% lexical coverage needed for comprehension to become efficient; below that, unknown-word density overwhelms working memory / breaks contextual guessing | a large-enough base vocabulary store such that MOST incoming words are handled by recognition, not effortful decoding |
| Learning sets ("learning to learn") | Harlow 1949, *Psychological Review* | monkeys go from slow trial-and-error to near-one-trial solutions after ~200+ discrimination problems, via an abstracted "win-stay/lose-shift" STRATEGY, not memory of specific stimulus-response pairs | an abstracted rule/strategy store, separate from and above episodic trial memory, applied to brand-new instances on their FIRST encounter |

**Synthesis (angle 1):** every one of these needs a persistent, reusable, abstracted store (vocabulary / chunks /
schema / strategy) that is architecturally UPSTREAM of new encoding — consulted while the new item is being
processed, not only retrieved afterward. None of these is "more instances remembered"; all are "a compact
generalized structure that changes how cheaply the NEXT instance is processed."

---

## (2) NEUROSCIENCE angle — exact numbers, not just qualitative shape

**Tse et al. 2007 (*Science* 316:76-82), verified via full text.** Rats built a flavor-place "schema" over ~1
month (13-20 sessions). Once established, a BRAND-NEW paired associate, trained in a **single trial**, became
hippocampus-independent within **48 hours** (hippocampal lesion at 48h left recall intact; lesion at **3 hours**
post-training abolished it — a steep 3h/48h gradient). Normal systems consolidation in the same literature is
**weeks**. This is a >10x speedup, contingent specifically on an already-formed schema, not on trial count or
elapsed time alone (Experiment 4: the SAME animals failed to show 24h retention when the new pairing was
schema-INCONSISTENT, ruling out a mere familiarity confound).

**Tse et al. 2011 (*Science* 333:891-895).** Schema-consistent rapid learning drives immediate-early-gene
activation specifically in prelimbic mPFC; mPFC blockade impairs both the new fast learning and recall of
previously-consolidated schema material. mPFC is the site holding/gating the schema.

**van Kesteren et al. 2010 (*PNAS* 107:7550), SLIMM model (van Kesteren et al. 2012, *Trends Neurosci*).**
Human fMRI: STRONGER prior schema correlates with REDUCED hippocampal-vmPFC connectivity during encoding;
schema-INconsistent material recruits MORE hippocampal-cortical crosstalk. vmPFC gates a variable, not fixed,
hippocampal "dose" per item — inversely scaled to schema-fit.

**McClelland 2013 (*J Exp Psychol Gen* 142:1190), the CLS theory's own author revising the 1995 account.**
Simulations show a cortex-like network CAN learn new information rapidly with little interleaving IF it is
schema-consistent; interference (and the need for slow interleaved learning) arises specifically for
schema-INconsistent material. **The original 1995 CLS account (budget/rehearsal-flat: interleave everything,
regardless of content) is explicitly superseded by its own author for exactly the regime this drill's negative #3
sits in.**

**Mattar & Daw 2018 (*Nat Neurosci* 21:1645).** Replay priority = **gain x need** (expected behavioral improvement
times likelihood the state matters soon) — this produces sharply CONCENTRATED, non-uniform replay on a small
high-value subset, not flat sampling across all stored experience (exact concentration statistic paywalled,
unverified; the gain x need construction itself is directly confirmed from the model/code).

**Reconsolidation (Nader, Schafe & LeDoux 2000, *Nature*; Lee 2009 review).** Retrieval of an ALREADY-CONSOLIDATED
memory re-labilizes it; it requires a fresh protein-synthesis-dependent re-stabilization ("recapture") to remain
stable, and can be updated or degraded if that recapture doesn't happen cleanly on reactivation. This is the
direct biological precedent for "a settled item can become revisable again on re-encounter," independently
confirmed by a prior internal drill (`research_consolidation_confidence_permanence_relational_inference_2026-07-14.md`)
as thin-but-real in the schema-editing direction and strong in the confidence/permanence-gradient direction.

**Honest complication.** Rudy & Sutherland (2008 commentary, title/existence confirmed, content not independently
verified — paywalled) disputes whether Tse's 48h effect is genuine SYSTEMS-level consolidation vs. faster
cellular consolidation within an already-tagged local circuit — an open, unresolved alternative reading, not
suppressed here. Sleep-dependence of the schema effect is separately contested (a 2023 Sleep Advances paper: the
sleep-specific advantage "may last only a day"). Flag: the fast-track number is well-replicated; whether it is
mechanistically "systems consolidation, just faster" or "a different, more local process" is not settled.

**Synthesis (angle 2):** consolidation SPEED and hippocampal "dose" are graded functions of schema-fit, not a
flat rehearsal timetable (Tse, van Kesteren, McClelland's own revision all converge); replay ALLOCATION is itself
sharply prioritized by expected value, not uniform (Mattar & Daw); and already-written memories remain revisable
on reactivation via a separate, biologically-real mechanism (reconsolidation) that is distinct from the write-time
schema gate.

---

## (3) CLASSICAL COG-SCI + (4) MODERN ML angle

| System | Mechanism | Structure required | How compounding is measured |
|---|---|---|---|
| **ACT-R knowledge compilation** (Anderson; Taatgen & Anderson 2002) | repeated declarative-retrieval-then-apply sequences get compiled into a single fast production, skipping the retrieval step | 2 stores (declarative vs procedural) + a compilation mechanism watching traces | fewer retrieval/firing cycles per instance; power-law-of-practice fit |
| **SOAR chunking** (Laird, Newell, Rosenbloom) | an impasse (missing knowledge) forces sub-problem-solving; the resolved trace compiles into a new persistent production, so future equivalent situations skip search | impasse-detection + generalization step + persistent production store separate from working memory | reduced search/impasse recurrence on repeated task classes |
| **CLS** (McClelland/McNaughton/O'Reilly 1995; McClelland 2013 revision) | fast pattern-separated hippocampus vs. slow interleaved cortex, to avoid catastrophic interference in overlapping distributed codes; 2013 revision makes interleaving REQUIREMENT itself schema-dependent | two systems at two timescales, PLUS (2013) a schema-fit-conditioned bypass of the slow route | — |
| **Bayesian hierarchical concept learning** (Tenenbaum, Kemp, Griffiths, Goodman 2011, *Science*) | a slow-updating abstract structural layer (what kinds of categories/relations exist) constrains/accelerates fast few-example concept inference at the layer below | nested representation, explicit separation of slow-abstract vs fast-specific levels | few-shot accuracy vs. no-prior baseline |
| **MAML** (Finn, Abbeel, Levine 2017) | optimizes a SINGLE initialization from which a few gradient steps generalize well to a new task | no explicit second store — the "abstraction" is implicit in the initialization geometry | k-shot-after-m-steps accuracy vs. from-scratch/pretrain+finetune baseline, MATCHED budget |
| **EWC** (Kirkpatrick et al. 2017, *PNAS*) | Fisher-information-weighted quadratic penalty protects IMPORTANT prior weights, leaves unimportant ones free — explicitly graded, not flat | per-parameter importance estimate + persistence of the prior optimum to compare against | forgetting-vs-plasticity curve at varying penalty weight |
| **NTM / DNC** (Graves et al. 2014, 2016) | controller + external addressable memory matrix, read/write via differentiable attention | memory as a distinct store OUTSIDE network weights — "learning" a fact can mean a memory write, not a weight update | — |
| **Forward-transfer measurement** (Diaz-Rodriguez et al. 2018, NeurIPS CL workshop; Continuum/Avalanche libraries) | compare post-prior-training performance on a NEW task against a random-init/from-scratch control at MATCHED budget; a positive gap = genuine transfer | — | THE standard rigorous protocol: without a matched from-scratch control, an apparent speedup cannot be attributed to compounding vs. task-easiness |

**Synthesis (angles 3+4):** every architecture examined splits into a slow/abstract/persistent layer and a
fast/episodic layer, with an explicit, NAMED mechanism for the slow layer to modulate the fast layer's cost
(compilation, chunking, interleaved replay gated by schema-fit, hierarchical priors, Fisher-weighted protection,
addressable memory). **EWC's Fisher-weighted protection and McClelland 2013's schema-fit-gated bypass are, at the
formal level, the SAME principle independently discovered in two different literatures — a genuine, not merely
analogical, convergence**: both make consolidation cost/protection a graded function of "how much this matters to
what's already known," not a flat rule. The one credible partial counter-example, MAML, still requires the
abstraction to live SOMEWHERE (in initialization geometry) even without an explicit second store — it does not
contradict the structural claim, it just implements it implicitly.

---

## (5) THE STRUCTURAL VERDICT — ranked

**Rank 1 (most likely missing piece, concrete name): a SCHEMA-FIT-GATED, VARIABLE-COST, REACTIVATION-CAPABLE
consolidation path.** Concretely, two fused sub-requirements, both absent:

- **1a. Variable consolidation COST, not a flat rehearsal budget.** Per Tse (>10x speedup, schema-consistent
  1-trial-to-48h vs. weeks baseline), van Kesteren (hippocampal dose scales inversely with schema-fit), McClelland
  2013 (interleaving need itself schema-gated), Mattar & Daw (replay is gain x need concentrated, never flat), and
  EWC (Fisher-weighted, graded protection) — consolidation cost should be a continuously-recomputed DECREASING
  function of schema-fit, not a flat X%-of-corpus rehearsal rule.
- **1b. Reactivation-triggered reconsolidation, not a one-shot write-time gate.** Per Nader/Schafe/LeDoux 2000 and
  the confirmed literature gap already flagged in the internal thread's function-inventory note
  (`research_consolidation_function_inventory_schema_reorg_2026-07-16.md`): the write-time schema gate (Tse/SLIMM)
  is about how NEW items get filed; it structurally cannot revise an OLD, already-written, possibly-WRONG entry.
  Biology solves this with a SEPARATE mechanism (retrieval re-labilizes, then a fresh signal re-stabilizes or
  updates). Without this second mechanism, re-encountering material can add missed items but has NO channel
  through which a previously mis-encoded meaning gets corrected.

**Rank 2 (precondition for Rank 1 to work): pairwise/multi-path schema-fit, not a per-node aggregate.** Already
diagnosed in the internal thread (`research_schema_fit_derivability_signal_upgrade_2026-07-16.md`): the current
schema-fit computation discards the specific pairwise relationship and reduces to a generic connectivity
percentile. If schema-fit itself is this noisy, gating cost or eligibility by it will not help — this is the
direct, already-identified explanation for negative #4 (schema-selection gave no headroom because the signal
being selected FROM cannot discriminate).

**Rank 3 (also a precondition): surprise computed LOCALLY/schema-conditioned, not against a flat global rank.**
Already diagnosed (`research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`): every credible
biological account computes prediction error against a structured, locally-conditioned prediction (Bayesian
surprise = KL(posterior||prior), prior = schema), not a corpus-wide base rate. Needed for "spend attention on the
surprising residual" (the task's candidate (b)) to do anything at all.

**Rank 4 (the umbrella / precondition for all of the above): a persistent abstraction store, distinct from
episodic memory, consulted DURING encoding.** Universally supported by angle 1 and angles 3-4 above. The
substrate already has PARTIAL pieces of this (additive_map scoring, reachability_audit derivability) — what is
missing is that this layer is not yet (i) queried to set variable cost, or (ii) itself revisable over time. Ranks
1-3 are the concrete, buildable refinements of this umbrella finding, not a separate fifth thing.

**Why this jointly explains all four negatives, not four unrelated weaknesses:**
- **Negative #1 (re-reading flat, wrong meanings resurface):** no reconsolidation channel (1b) — a wrong old
  encoding cannot be corrected on re-exposure; a flat-cost gate (1a) also means the system doesn't concentrate
  effort on the specific residual that's actually learnable on pass 2.
- **Negative #2 (curriculum order null):** ALREADY EXPLAINED, and likely a CORRECT result, not a failure — see
  honesty section below. Not further addressed by this drill's new findings.
- **Negative #3 (CLS replay budget-inefficient at low %):** directly explained by 1a — a flat-%-of-corpus sweep
  is the wrong experiment; the brain's own literature says replay should be schema-fit/gain-weighted allocation,
  concentrated on the low-fit tail, not spread evenly. A flat sweep needing 25-50% to show benefit is consistent
  with "most of that budget is being wasted rehearsing already-easy, already-fit material."
- **Negative #4 (schema-selection no headroom):** directly explained by Rank 2 — the schema-fit proxy being
  selected FROM is a weak per-node aggregate, not a pairwise derivability score.
- **Negative #5 (no compounding loop):** the mathematical consequence of 1a+1b: if cost is flat and eligibility is
  one-shot, per-pass efficiency is structurally CONSTANT by construction — there is no mechanism by which growing
  knowledge could make future consolidation cheaper, regardless of how good schema-fit or surprise individually
  are. Compounding requires cost to fall as fit rises; a flat-cost architecture cannot produce it even with a
  perfect schema-fit signal.

---

## Cheap decisive test

Two small, additive-only re-analyses of ALREADY-COLLECTED data, zero new compute, before any new cell:

1. **Re-bucket the existing flat-% CLS replay sweep results by schema-fit of the rehearsed items** (using the
   CURRENT, even-if-noisy schema-fit signal) rather than by raw %. Prediction: within any fixed total-%, arms that
   happened (by chance of random sampling) to rehearse more LOW-schema-fit items should show more benefit than
   arms that rehearsed more HIGH-fit items. If this pattern already exists latent in the existing data, it is a
   free, decisive confirmation before building an explicit allocator.
2. **Re-check the "got meaning wrong" cases from the re-reading negative** against whether those specific terms
   were previously WRITTEN (present in the store, i.e. an old, wrong entry existed) vs. genuinely NEVER captured
   before (a true miss). If most wrong-meaning cases are old, already-written, never-revised entries, that is a
   direct, on-disk confirmation of the reconsolidation gap (1b) rather than a residual-detection failure.

## Falsifiable predictions — HARD-PASS / HARD-FAIL

**Prediction A (schema-fit-weighted replay allocator beats flat-% sweep at equal budget).**
P=0.45 (deflated, novel-synthesis capped). HARD-PASS: at a FIXED total rehearsal budget (e.g. 10%), a
schema-fit-weighted allocator (spend on low-fit/high-gain items first, per Mattar-Daw gain x need form) beats
random-%-of-corpus allocation on held-out derivability/retention by a real margin (>=0.05 absolute, matching the
project's standard MEDIUM-effect bar). HARD-FAIL: no reliable margin over random allocation at ANY tested budget —
this would mean the schema-fit signal (even after the Rank-2 pairwise fix) carries no real predictive value for
WHERE consolidation benefit concentrates, a serious negative for the whole schema-gating hypothesis, not just an
allocation-strategy failure.

**Prediction B (reactivation-triggered reconsolidation corrects previously-wrong entries on re-read, where a
write-once gate cannot).**
P=0.35 (deflated further; reconsolidation's applicability to abstract/declarative-fact revision, vs. its
best-evidenced domain of fear-conditioning, is a genuine extrapolation). HARD-PASS: on a held-out set of
deliberately-seeded wrong first-pass encodings, a reactivation pass that re-evaluates schema-fit/prediction-error
at re-exposure and allows overwrite (gated by a confidence/permanence scalar, not unconditional) corrects >=50% of
the seeded errors on the SAME material a write-once gate leaves uncorrected (0% by construction). HARD-FAIL:
overwrite rate <15% even with the mechanism explicitly present, OR the mechanism introduces net-new errors
(overwrites previously-correct entries) at a rate exceeding the corrections it makes — the second failure mode
(hallucination cost) is explicitly expected as a possible honest cost, not a surprise, per the confirmed brain
literature that schema-driven reconstruction produces both true generalization and false schema-congruent
confabulation from the SAME mechanism (Payne 2009; Alba & Hasher 1983 — see honesty section).

**Prediction C (per-pass capture-rate rises with foundation size, at matched difficulty — the actual compounding
signature).** See the fair efficiency test below; this is Prediction C stated formally.
P=0.40 (deflated; this is the composite claim the whole verdict rests on, capped at the novel-synthesis ceiling).
HARD-PASS/HARD-FAIL: given in the efficiency-test section immediately below.

---

## Concrete glass-box-buildable proposal

1. **Schema-fit-weighted consolidation-cost allocator** (replaces flat-% rehearsal sweep): compute pairwise
   schema-fit per candidate fact (reusing the already-landed SRColumnSolver resolvent per the Rank-2 fix, not a
   new mechanism); allocate rehearsal budget inversely proportional to fit (spend cycles on low-fit/high-surprise
   items, per Mattar-Daw gain x need weighting; near-skip high-fit items). Fully auditable — every allocation
   weight is a named, inspectable schema-fit + surprise score, no learned black-box selector.
2. **Reactivation-triggered reconsolidation pass**: when an already-written fact/slot is touched again (2nd/3rd
   read, or any re-encounter), re-run the SAME schema-fit + local-surprise computation against the CURRENT
   (grown) foundation rather than skipping on "already known." If the current context disagrees with the stored
   entry (a local misprediction), mark it LABILE and allow controlled overwrite gated by a confidence/permanence
   scalar (already scoped, not new invention, per
   `research_consolidation_confidence_permanence_relational_inference_2026-07-14.md`) rather than treating all
   written entries as immutable.
3. **(supporting, lower priority, already-diagnosed) local/schema-conditioned surprise fix**: needed as the input
   signal for both 1 and 2 to fire on the right items rather than a global corpus-rank proxy.

## The fair, externally-reviewed efficiency test

**Design.** Use a corpus with a genuinely verifiable "learnable residual" — either a text with a known
ground-truth fact list (so an external, non-substrate reviewer can enumerate exactly which extractable facts
remain uncaptured before each pass) or a held-out gold annotation set scored by a reviewer blind to the
substrate's own gate decisions. Before EVERY pass, the external reviewer computes: `residual_N` = facts that are
genuinely present/extractable in the text AND not yet correctly captured by the substrate. After the pass,
compute `capture_rate_N` = (newly correctly captured facts) / `residual_N`.

**Distinguishing success-flat from failure-flat (the honesty-critical step):**
- If `residual_N` (independently, externally verified) is near-zero entering pass N, then a flat/zero
  `capture_rate_N` is CORRECT — there was nothing learnable left, and this must be reported as a SUCCESS, not
  relabeled as a negative.
- If `residual_N` is externally confirmed to be substantial, and `capture_rate_N` still does not rise (or is flat
  relative to an equally-hard earlier slice), that is the genuine FAILURE case — knowledge grew but did not make
  the system better at scooping up what was still available to learn.

**The actual compounding signature (matched-difficulty control, per the ML forward-transfer discipline —
Diaz-Rodriguez et al.'s protocol, generalized here):** hold difficulty fixed by comparing `capture_rate` on the
SAME difficulty-matched held-out slice at foundation-size N vs. foundation-size 2N (not a moving target across
different material). Compounding is confirmed only if `capture_rate` at 2N exceeds `capture_rate` at N on that
IDENTICAL slice — a rising fraction of available, externally-verified residual captured per unit compute, as
accumulated foundation size grows.

**HARD-PASS:** `capture_rate` at foundation-size 2N exceeds foundation-size N by >=15% relative on a
difficulty-matched held-out slice, replicated across >=3 seeds/slices, AND the schema-fit-weighted allocator
(build-proposal #1) beats flat-random allocation at equal total budget (Prediction A's bar).
**HARD-FAIL:** `capture_rate` is flat or declining at 2N vs N despite externally-confirmed nonzero residual, AND
the schema-fit-weighted allocator does not beat flat-random at equal budget — this is the genuinely serious
negative: the schema-fit signal would carry no real predictive value for consolidation payoff, not merely a
wrong-architecture problem.

---

## Cross-thread synthesis

This drill sits directly on top of, and does not contradict, the extensive existing 07-14 through 07-17 thread:
`research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md` (the 3-signal gate, already identifying
the missing-formal-combination-rule gap this drill's Ranks 1-3 answer), `research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`
(local-vs-global surprise diagnosis = this drill's Rank 3), `research_schema_fit_derivability_signal_upgrade_2026-07-16.md`
(pairwise-vs-node-aggregate diagnosis = this drill's Rank 2), `research_consolidation_function_inventory_schema_reorg_2026-07-16.md`
(the write-time-vs-reorganization split = this drill's Rank 1b, now with the Nader/reconsolidation citation this
prior note flagged as the needed mechanism but did not fully cite), `research_consolidation_confidence_permanence_relational_inference_2026-07-14.md`
(confidence/permanence gradient + reconsolidation precedent, directly reused in build-proposal #2), and
`research_curriculum_order_corpus_mismatch_brain_check_2026-07-16.md` (negative #2's corpus-mismatch explanation,
reused verbatim, not re-derived — see honesty section). This drill's contribution is the explicit CONNECTION:
these separately-diagnosed gaps are one joint architectural property (flat-cost, one-shot-eligibility) and jointly,
not separately, explain all four fresh negatives handed to this cycle, plus three genuinely new external citations
(Matthew effect/chunking/Harlow; Tse's exact 3h/48h/weeks numbers; ACT-R/SOAR/EWC/MAML/NTM + the standard
forward-transfer measurement protocol) that had not yet been pulled into the thread.

## Substrate-product implications

Not a publication angle — a build-priority angle. If Prediction A and the efficiency test's HARD-PASS conditions
hold, the product-relevant claim is: ingestion cost (compute spent per document/pass) can be REDUCED, not just
retention improved, by concentrating rehearsal on the genuinely novel/low-fit tail — this is a cost story as much
as a capability story, relevant to any pricing or latency argument for a continual-ingestion product. If
Prediction B holds, the product gets a genuine self-correction capability (fixing its own earlier mistakes on
re-exposure) which is a differentiator most static-embedding or single-pass-extraction competitors structurally
lack. If either HARD-FAILs, the honest fallback is: schema-fit and surprise, even after the Rank 2/3 fixes, may
not carry enough signal to justify variable-cost consolidation — in which case the flat, simple, already-working
one-shot gate remains the right engineering choice and further investment here should stop.

## Honesty / calibration

- **Established literature (P~0.60-0.75, deflated for secondary-sourcing/paywall gaps flagged by the sub-agents):**
  Stanovich 1986, Chase & Simon 1973, Bransford & Johnson 1972 + Anderson & Pichert 1978, Hu & Nation 2000, Harlow
  1949, Tse 2007/2011 (full-text verified), van Kesteren 2010/2012, McClelland 1995/2013, Mattar & Daw 2018
  (construction verified, exact concentration statistic NOT independently verified — paywalled), Nader/Schafe/LeDoux
  2000, ACT-R (Anderson/Taatgen), SOAR (Laird/Newell/Rosenbloom), Tenenbaum et al. 2011, MAML (Finn et al. 2017),
  EWC (Kirkpatrick et al. 2017), NTM/DNC (Graves et al. 2014/2016), Diaz-Rodriguez et al. 2018 forward-transfer
  protocol.
- **Novel-for-this-substrate synthesis, capped P<=0.50 throughout per lit-scan-calibration discipline:** the
  overall "one joint missing property explains all four negatives" framing; the EWC-equals-McClelland-2013
  convergence claim (both individually well-cited, the EQUIVALENCE framing is this drill's synthesis); all three
  falsifiable predictions and the efficiency test.
- **Flagged speculation / open tension, not suppressed:** Rudy & Sutherland's unverified content disputing whether
  Tse's effect is genuine systems-consolidation; sleep-dependence of schema effects contested (2023 Sleep Advances,
  advantage "may last only a day"); Mattar-Daw's exact concentration number unverified (construction only);
  reconsolidation's extension from fear-conditioning to general declarative-fact revision is a real extrapolation,
  not a directly-cited result for that domain.
- **A negative that is likely a CORRECT result, not a failure:** negative #2 (curriculum order null) — already
  established by `research_curriculum_order_corpus_mismatch_brain_check_2026-07-16.md` that the tested corpus
  (CoDEx) is an ~11-16x-denser-than-tree flat associative web with <0.3% hierarchical edges, which THREE
  independent frameworks (Knowledge Space Theory's degenerate surmise relation, Piaget's figurative-vs-operative
  distinction, interleaving/blocking literature) predict should show a near-vacuous order effect. This negative
  should NOT be folded into the "no compounding" cluster as evidence against schema-gating — it is a correctly-
  measured null on the wrong-shaped corpus, and the recommended AL-CPL re-test (already scoped in that note) is
  the right next step for that specific question, independent of this drill's Ranks 1-3.
- **Brain and ML agree, strongly, on:** the two-timescale/two-store split (universal across every framework
  surveyed); that consolidation cost/protection should be GRADED by importance/fit, not flat (McClelland 2013 and
  EWC are the clearest converging pair); that rigorous compounding measurement requires a MATCHED baseline/control
  (forward-transfer protocol and Tse's own within-subject schema-consistent-vs-inconsistent control are the same
  logical move in two different fields).
- **Brain and ML diverge / remain open on:** no literature (biological or ML) gives an exact JOINT formula
  combining schema-fit x surprise x recurrence into one consolidation-cost number — confirmed independently by
  TWO separate internal drills now (07-15 and 07-16) plus this drill's own sub-agents; this remains a genuine,
  not incidental, gap that any implementation will have to resolve by internal experiment, not literature lookup.

## Citations (verified count)

**~35 distinct primary/named sources** across the three lit-scans (full list embedded in each angle's table
above; full-text-verified where noted: Tse 2007, van Kesteren 2010). Combined with the ~25 sources already cited
in the five directly-reused internal notes listed under Cross-thread synthesis, this drill's total evidentiary
base is ~60 distinct sources, none newly hallucinated — every citation not independently verified this session is
explicitly flagged as such inline (Tse 2011's exact repeated number, Mattar-Daw's concentration statistic, Preston
& Eichenbaum's specific numeric claims, Rudy & Sutherland's argument content).
