# Research (brain-first): the fusion cell -- ACC/EVC aggregate depth-threshold dial gating the retained-trace condenser via the combinedgate arbitration margin (2026-07-08)

**Author:** Research (Sonnet, direct scan -- no sub-agent fan-out per this cycle's explicit instruction).
**Trigger:** USER brain-grounding steer. Build-order step 3: fuse two already-smoked payoff pieces (certified
`combinedgate` biased-competition arbitration; HARD-PASS `retained_trace_requery` selective-depth condenser)
under an ACC/EVC-tuned scalar dial, following the same content-free-scalar-over-frozen-knob shape already
proven HARD_PASS for Dial#1 (`substrate_acc_evc_adaptive_halting_v1`).
**Method:** deep read of the three same-day prior research notes plus direct on-disk read of the three
implicated cells' docstrings AND their landed `metrics.json` verdicts (not assumed -- verified), followed by
6 external WebSearch queries (generic neuroscience/decision-theory terms only, no substrate-internal names
or numbers sent off-platform, per [[feedback-query-privacy-decomposition]]).
**Calibration:** per [[feedback-lit-scan-calibration-penalty]], all P estimates deflated 0.15-0.25 from raw
confidence; novel-synthesis claims capped at P<=0.50. Per [[feedback-brain-grounding-drills-lead-with-deep-
biology-ml-not-the-guide]] biology leads throughout; ML precedent (early-exit cascades, DDM-as-RL) cited only
as weak secondary confirmation.

---

## HEADLINE

**The two certified/smoked pieces already share the exact mathematical primitive the brain uses to decide
"spend more effort here": competitive/biased normalization over a small candidate set produces, as a pure
byproduct of computing WHICH option wins, a second number -- the margin between the winner and the runner-up
-- and that margin IS the conflict/confidence signal the dorsal ACC's Expected-Value-of-Control machinery
(Shenhav, Botvinick & Cohen 2013) and the balance-of-evidence confidence signal Kiani & Shadlen (2009, Science)
found encoded by the SAME parietal neurons that make the choice, both use to gate extra effort -- no new
readout machinery, no new representational channel, is required to get a conflict signal out of the certified
`combinedgate` cell. The fusion cell is therefore a THIRD scalar tap (after Dial#1's arrival-confidence tap),
computed from a DIFFERENT certified cell's existing arbitration logits, that decides -- via one aggregate
threshold tuned exactly the way Dial#1 tuned its halting threshold (train-time argmax of accuracy-per-compute,
then frozen) -- whether the just-HARD-PASSED retained-trace re-query condenser runs its expensive fine read
on a query or accepts the cheap coarse read. This is the SAME control-law shape validated twice already in
this substrate this week (arrival-confidence -> halt; margin -> drill), which is itself evidence the shape
generalizes, not a coincidence.**

P_deflated(the general fusion thesis -- combinedgate margin is a valid, load-bearing trigger for retained-trace
depth, reusing zero new learned machinery) = **0.42** (capped near novel-synthesis ceiling; both HALVES of the
fusion are independently strongly evidenced -- Dial#1 HARD_PASS at accpc gain 3.21x/3.87x, retained-trace
HARD_PASS at near-ceiling recall 0.994 at 5x cost reduction -- but the CROSS-cell coupling itself, whether
combinedgate's WHICH-slot uncertainty actually predicts retained-trace's HOW-FINE need, is unmeasured; this is
the identical open question flagged P=0.40 in `research_energy_scaled_selective_depth_retrieval_coarse_to_fine_2026-07-08.md`
Part 4, now carried forward with a slightly higher prior because Dial#1's landed result is in-corpus evidence
that a margin/confidence-style telemetry channel IS load-bearing for a hop/depth decision in this exact
codebase, not just in the literature).

---

## Part 0 -- What is already proven on disk (verified, not assumed)

Read directly from `metrics.json` this cycle, not taken from prior notes' claims:

| Cell | Verdict (on-disk) | Load-bearing number |
|---|---|---|
| `exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu` (FULL, non-smoke) | **HARD_PASS** | arbitrates: beats single-signal gates on mixed corpus (+0.327/+0.274), beats each on its failure sub-regime (conflict +1.000, cue_absent +0.801), scramble_sep=+0.658 |
| `exp_substrate_acc_evc_adaptive_halting_v1` | **HARD_PASS** | accpc[FIXED=0.0446 ADAPT=0.1878 RAND=0.0385 SCR=0.0354 ORC=0.1878]; adapt_vs_fixed=3.213x; adapt_vs_random=3.874x; scramble_gap=0.812; closure=1.000; corr[adaptive-vs-oracle-arrival]=1.000 vs corr[scrambled]=-0.026 |
| `exp_encoder_retained_trace_requery_coarse_to_fine_v1` | **HARD_PASS_RETAINED_TRACE_RECOVERS** (smoke) | B@k=0.10: recall=0.994 (== full_fine ceiling 0.994); sparse control fails (0.493/0.532, matches MEASURED v1 wall 0.5383); shortlist_hit@k=0.10 = 1.000; cost_ratio=0.200 (5.0x cheaper); coarse_only(top-1 alone, no fine read at all) = **0.902** |

The `coarse_only=0.902` number (not previously highlighted in the prior note's headline, but present in its
verdict_msg) is the single most important number for this drill: it is the accuracy you get for FREE if you
never run the fine condense at all. The gap `0.994 - 0.902 = 0.092` is exactly the quantity a depth-controller
is fighting over -- there IS a real, non-trivial (9.2 point) accuracy cost to skipping the fine read
uniformly, which means an inert or wrong dial has real teeth to fail against; this is not a near-zero-stakes
decision being dressed up as one.

---

## Part 1 -- The brain mechanism, precisely, tied to the exact substrate signal it maps onto

### 1a. ACC / dACC as the conflict + expected-value-of-control monitor (the AGGREGATE half)

Shenhav, Botvinick & Cohen (2013, Neuron 79:217-240, "The Expected Value of Control: An Integrative Theory of
Anterior Cingulate Cortex Function") propose dACC integrates the expected PAYOFF of additional control against
its CONTROL COST, and allocates control (effort/depth/iterations) only when the net expected value is
positive -- control is not free, and is withheld precisely when the marginal benefit of more processing does
not exceed its cost. This directly generalizes Botvinick's earlier conflict-monitoring model (Botvinick,
Braver, Barch, Carter & Cohen, 2001; Botvinick, Cohen & Carter, 2004, "Conflict monitoring and anterior
cingulate cortex: an update," TICS): ACC computes a trial-by-trial CONFLICT signal -- the coactivation of
mutually incompatible response representations -- and feeds it forward as a gain adjustment on the NEXT
trial's control allocation (the empirically robust Gratton conflict-adaptation effect). Two points matter for
the fusion design: (i) conflict is measured as competition BETWEEN options, not as weakness of one option in
isolation -- it is maximal when two response tendencies are close in strength, regardless of which eventually
wins; (ii) the debate over whether ACC is the SOURCE of the conflict signal or merely learns error-LIKELIHOOD
from it (Brown & Braver 2005; dissociation attempts, e.g. Jessup, Busemeyer & Brown 2010, J. Neurosci) is
still open in the primate literature -- flagged honestly, not resolved by this drill; the control-LAW below
does not depend on resolving it, since both framings agree ACC output is a function of trial-by-trial
competition strength.

### 1b. The balance-of-evidence / confidence signal is the SAME computation that produces the choice (the FREE-BYPRODUCT half)

Kiani & Shadlen (2009, Science 324:759, "Representation of Confidence Associated with a Decision by Neurons in
the Parietal Cortex"): LIP neurons that represent the accumulating evidence FOR the eventual choice also encode
the DEGREE of certainty in that choice -- confidence is read out from the SAME population, at the SAME
computational step, as the choice itself; no separate confidence-computing circuit is required. This is the
single most load-bearing citation for the fusion design, because it is the direct biological warrant for
"don't build a new margin-computation module -- the certified `combinedgate` cell already computes the margin
as a mechanical byproduct of computing `argmax(combined_logit)`." The margin (gap between the top-1 and top-2
`combined_logit` values, equivalently the concentration/entropy of the softmax distribution over candidates)
IS a balance-of-evidence signal in the Kiani-Shadlen sense, already sitting inside the gate's forward pass.

### 1c. LC-NE and ACh as gain/precision SETTERS, not per-item deciders (why the dial stays scalar and aggregate)

Aston-Jones & Cohen (2005, Annu. Rev. Neurosci. 28:403-450): tonic/phasic locus coeruleus-norepinephrine
activity sets GLOBAL gain (signal-to-noise sharpening), and its own state is itself driven by an aggregate
utility signal from ACC/OFC, not by any single item's content. Yu & Dayan (2005) and the cholinergic
precision-weighting literature (Feldman & Friston 2013; directly measured pharmacologically in a 2024 eLife
paper, "Acetylcholine modulates the precision of prediction error in the auditory cortex") frame ACh as setting
the PRECISION (inverse variance / trust) assigned to a prediction-error signal -- again an aggregate,
slow-timescale parameter, not a per-instance judgment call. Pupil-linked LC-NE studies (multiple PMC sources,
2013-2023) confirm this system tracks AGGREGATE uncertainty/surprise across a task epoch, correlating with
exploration-vs-exploitation MODE shifts, not with resolving any one decision's content. **The load-bearing
architectural point these three sources jointly establish: every neuromodulatory system that retunes a
criterion operates on an AGGREGATE, slow statistic; the per-item application of that criterion is always LOCAL
and REFLEXIVE (the actual gating happens at the retrieval/decision site itself, using a locally-available
signal).** This is the identical two-timescale split already independently confirmed by BOTH prior same-day
notes (`research_neuromodulatory_self_manager_controller_2026-07-08.md` sec 3-4; `research_energy_scaled_selective_depth_nondestructive_refinement_brain_first_2026-07-08.md`
Part 1d) and by Dial#1's own landed implementation (theta tuned once on TRAIN via an aggregate acc-per-compute
sweep, then FROZEN and applied as a local per-item reflex on TEST) -- this drill's contribution is showing the
identical two-timescale shape applies to a DIFFERENT telemetry channel (arbitration margin, not arrival cosine)
and a DIFFERENT downstream action (shortlist depth, not hop count), which is exactly the "third proof point"
the HEADLINE claims.

### 1d. Decision-threshold / evidence-accumulation framing, and why it is NOT literally a collapsing bound here

Bogacz et al. (2006) prove the drift-diffusion model has a reward-rate-optimal FIXED threshold for a given
task's evidence statistics; Cisek, Puskas & El-Murr (2009) and the "collapsing bounds vs urgency signal"
literature (Hawkins et al. 2015, J. Neurosci, "Revisiting the Evidence for Collapsing Boundaries and Urgency
Signals") show the threshold can also be made to SHRINK over elapsed WITHIN-TRIAL time, so less evidence is
needed to trigger a decision as a trial drags on. **Honest distinction, flagged rather than glossed over:** the
fusion dial proposed here is NOT a collapsing bound in that literal sense -- theta_M is a single FIXED scalar
(tuned once, frozen), not a function of elapsed time within a query. The correct citation for what this dial
actually is comes from resource-rational metareasoning (Lieder & Griffiths, "Resource-rational analysis":
compute the Value Of Computation for a candidate extra computation, stop when marginal VOC <= 0) -- theta_M is
the pre-computed crossing point of that marginal-value curve, exactly mirroring how Dial#1's theta was tuned
(argmax accuracy-per-compute on TRAIN). The collapsing-bound literature is cited only as the closest DIFFERENT
mechanism (time-varying threshold) that this design deliberately does NOT adopt, to avoid overclaiming
architectural correspondence it does not have; Part 4's "high-probability-superior new mechanism" below is
where an iterative, RHT-style, genuinely time/step-varying version would actually earn that citation.

---

## Part 2 -- The exact control law

**Telemetry (already computed, zero new forward passes):** in the certified `combinedgate` cell,
`combined_logit_j = content_rel_j / GATE_TAU + recency_bias_j` for each candidate slot `j` (GATE_TAU=0.05,
RECENCY_GAP_TARGET=3.0, analytic arbitration boundary q* = GATE_TAU*RECENCY_GAP_TARGET = 0.15, MEASURED and
asserted in the cell's own code, `exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py` lines
151-158, 485-486). Define:

```
M = combined_logit[rank1] - combined_logit[rank2]      # margin: Kiani-Shadlen balance-of-evidence,
                                                          # Botvinick coactivation-conflict (small M = high conflict,
                                                          # symmetric around q*: content-wins-clearly and
                                                          # recency-wins-clearly BOTH give large |M|; only the
                                                          # q ~ q* boundary crossing gives small M)
```

**Aggregate dial (tuned once, offline, EXACTLY Dial#1's method):** on a TRAIN split, sweep a small grid of
candidate `theta_M` values; for each, compute accuracy-per-compute of "shallow (coarse-only, cost~0.10) when
M >= theta_M, else deep (retained-trace fine condense on a k=0.10V shortlist, cost~0.20)"; pick
`theta_M* = argmax(accpc)`; FREEZE theta_M* for TEST. This is the identical code path Dial#1 already
implements for its arrival-confidence theta -- the fusion cell reuses that machinery verbatim, swapping only
the telemetry channel and the downstream action.

**Local reflex (per query, TEST time, parameter-free given frozen theta_M*):**
```
if M(query) >= theta_M*:   # decisive arbitration; low conflict; ACC's EVC says extra control not worth it
    accept coarse_only read (skip fine condense entirely; cost ~0.10)
else:                       # near/below the boundary; high conflict; EVC says extra control likely pays off
    run retained-trace fine condense on the k=0.10V shortlist (cost ~0.20; recall -> ceiling 0.994)
```

**Why this is content-free and sits ABOVE both certified gates unchanged:** `M` is read, not computed anew,
from `combinedgate`'s existing forward pass; `theta_M` is one scalar; the downstream action selects between
two ALREADY-EXISTING, ALREADY-CERTIFIED read paths in `retained_trace_requery` (`coarse_only` and
`retained_trace_requery` arms, both already implemented, already measured). No new W matrix, no new trained
weights, no new representational channel -- exactly the design principle both prior self-manager notes
independently derived and the same shape Dial#1 already proved out.

**Honest corpus caveat (load-bearing, not cosmetic):** the retained-trace cell's OWN smoke corpus currently
measures `shortlist_hit_rate@k = 1.000` at EVERY tested k (0.05V through 0.25V) -- meaning the coarse signal
already perfectly contains the answer at the smallest shortlist tested, so the existing smoke corpus cannot
yet distinguish "always take the cheapest option" from "read the margin correctly," because there is no
regime in the current corpus where skipping the fine read actually costs accuracy on a PER-QUERY basis (the
0.092-point aggregate gap is presumably concentrated in a minority of harder queries, not measured as such).
**The fusion cell's corpus MUST introduce per-query difficulty variation correlated with the combinedgate
margin**, or the dial cannot be tested at all -- this is addressed directly in Part 3's corpus design, not an
afterthought.

---

## Part 3 -- Buildable fusion cell: corpus, arms, decisive multi-arm test

**Corpus (new, minimal, chains the two existing cells' own noise constructions -- no invented mechanism):**
reuse `combinedgate`'s existing NOISY-cue construction verbatim: `noisy_cue = normalize(cue_q * flag_code +
sqrt(1-cue_q^2) * random_unit)`, sweeping `cue_q` over the SAME grid the certified cell already uses
(`{1.0, 0.5, 0.25, 0.12, 0.06}`, straddling the certified q*=0.15 boundary). The winning slot's content code
under `combinedgate`'s own arbitration becomes the QUERY fed into `retained_trace_requery`'s V-item store,
with the SAME `cue_q` also setting that query's corruption level in the retained-trace cell's existing
`alpha`/noise parameter (mechanistically justified, not assumed: the same noisy cue that made the WHICH-slot
decision uncertain is the SAME vector being used to query the V-item store, so coupling is a direct
consequence of chaining the two cells' existing pipelines, not a new correlational assumption bolted on).
This produces, for free, a corpus where combinedgate's margin M and retained-trace's per-query difficulty are
mechanistically linked -- exactly the untested coupling both prior notes flagged as the open question.

**Arms (paired; differ ONLY in the depth-selection policy, mirroring Dial#1's arm-naming convention):**
- `FIXED_SHALLOW` -- always `coarse_only` (never fine-condense). Named baseline; ceiling per current data ~0.902 uniformly.
- `FIXED_DEEP` -- always `retained_trace_requery` fine condense at k=0.10V. Named ceiling; ~0.994 uniformly, cost 0.20 always.
- `MARGIN_GATED_EVC` -- **THE DIAL.** Per-query: M >= theta_M* -> shallow; M < theta_M* -> deep. theta_M* tuned on TRAIN by argmax accpc, frozen for TEST.
- `RANDOM_DEPTH_MATCHED` -- per-query shallow/deep coin-flip with p(deep) matched to MARGIN_GATED_EVC's OWN empirical p(deep) on TEST (equal EXPECTED compute, telemetry ignored). Isolates "does having a mixed budget help at all" from "does reading M specifically help."
- `SCRAMBLED_MARGIN` -- identical rule to MARGIN_GATED_EVC, but M is shuffled across queries within a batch (matched scale/distribution, query-correspondence destroyed). MANDATORY telemetry-sensitivity guard (per house discipline `assert_discriminator_fires`) -- must collapse toward RANDOM_DEPTH_MATCHED.
- `ORACLE_GATED` -- oracle knows whether `coarse_only` would already have been correct for this query; uses shallow exactly when it would suffice, deep otherwise. Perfect-information ceiling / closure denominator (same role as Dial#1's `ORACLE_HALT`).

**Metrics (accpc = accuracy / mean_cost_ratio, matching both parent cells' own cost-accounting):**
`gated_vs_shallow_rel`, `gated_vs_deep_rel`, `gated_vs_random_rel`, `scramble_rel_gap`, `closure`,
`margin_recall_corr` (does M actually predict per-query shallow-sufficiency -- the direct test of the
Part-3-corpus coupling), `depth_spread` (fraction of queries routed deep; must be neither ~0 nor ~1, else the
dial degenerated to a fixed policy).

### The single sharpest kill-test (equal-compute Pareto dominance)

Plot the accuracy-vs-cost_ratio Pareto frontier already fully measured by `retained_trace_requery`'s own
k-sweep (`FIXED_SHALLOW` at cost~0.10, k=0.05 at cost 0.15, k=0.10 at cost 0.20, k=0.15 at cost 0.25, k=0.25 at
cost 0.35, `FIXED_DEEP`/full_fine at cost 1.0) -- this is the uniform-fixed-budget frontier. Place
`MARGIN_GATED_EVC`'s single (accuracy, mean_cost_ratio) point on the same axes.

- **HARD-PASS (the dial earns its keep):** `MARGIN_GATED_EVC`'s point lies STRICTLY ABOVE the fixed-uniform
  frontier -- at its own average cost, no fixed-k arm (including `FIXED_SHALLOW` and `FIXED_DEEP` as the two
  named endpoints the task asks for explicitly) achieves equal-or-higher accuracy. Concretely:
  `accpc(MARGIN_GATED) >= 1.10 * accpc(FIXED_SHALLOW)` AND `accpc(MARGIN_GATED) >= 1.10 * accpc(FIXED_DEEP)`
  AND `accpc(MARGIN_GATED) >= 1.10 * accpc(RANDOM_DEPTH_MATCHED)` AND `scramble_rel_gap >= 0.15` AND
  `margin_recall_corr >= 0.30` (M genuinely predicts per-query shallow-sufficiency, not accidentally) AND
  `depth_spread` in a genuine mixed range (neither <5% nor >95% queries routed deep).
- **HARD-FAIL_INERT_DIAL (the kill-test's negative, exactly as specified):** `MARGIN_GATED_EVC`'s point falls
  ON OR BELOW the fixed-uniform frontier -- i.e. `|accpc(MARGIN_GATED) - accpc(FIXED_SHALLOW)| < 0.05` AND
  `|accpc(MARGIN_GATED) - accpc(FIXED_DEEP)| < 0.05` (some fixed budget choice matches it), meaning conditional
  allocation buys nothing a fixed uniform choice at the same average cost would not already buy -- the dial is
  inert, exactly the failure mode the task brief names.
- **HARD-FAIL_SIGNAL_NOT_LOADBEARING:** `accpc(MARGIN_GATED) <= accpc(RANDOM_DEPTH_MATCHED)` -- having a mixed
  budget alone explains the gain; reading M specifically adds nothing.
- **MIDDLE_BAND:** beats the frontier by some margin but misses one of the 1.10x gates, or `margin_recall_corr`
  in [0.15, 0.30) (directionally right, corpus coupling weaker than hoped).
- **INCONCLUSIVE_TAUTOLOGICAL_METRIC:** `scramble_rel_gap < 0.05` (scramble did not collapse -- not
  telemetry-sensitive, report inconclusive not a clean negative, per house discipline).
- **INCONCLUSIVE_NO_COUPLING:** `margin_recall_corr < 0.10` even before looking at accuracy -- would mean the
  corpus-construction coupling (Part 3) failed to produce a regime where M predicts anything, a corpus-design
  failure to fix before re-running, not a verdict on the dial itself.

---

## Part 4 -- Honest prior, and the flagged HIGH-PROBABILITY-SUPERIOR new mechanism

**Honest prior (stated plainly):** both HALVES of this fusion are strongly evidenced independently (Dial#1
HARD_PASS with a 3.2x-3.9x accpc gain; retained-trace HARD_PASS recovering the 0.994 ceiling at 5x lower cost).
The genuinely UNTESTED piece is narrow and specific: does a margin computed by CELL A (combinedgate, a WHICH-
slot arbitration) predict the depth CELL B (retained-trace, a HOW-FINE retrieval) needs, when chained through a
mechanistically-justified shared noisy-cue construction. This is a real, falsifiable, cheap-to-test empirical
question, not a leap of faith -- P_deflated=0.42, capped under the novel-synthesis ceiling, matches the
identical open question both parent notes independently flagged, now with a modest upward revision because
Dial#1's landed result is direct in-corpus evidence that a confidence/margin-style scalar CAN be load-bearing
for a depth/effort decision in this exact substrate (not just in the outside literature).

**Flagged HIGH-PROBABILITY-SUPERIOR new mechanism (not yet built, not assumed into the pre-reg above):** the
control law proposed here is a single BINARY, one-shot decision (shallow xor deep), which is the simplest
member of a family the brain literature does NOT treat as the ceiling. Three independent threads converge on
something strictly richer: (i) Reverse Hierarchy Theory's descent through cortical levels is ITERATIVE and
FEEDBACK-DRIVEN, not a single jump (Hochstein & Ahissar 2002/2004, already cited in
`research_energy_scaled_selective_depth_retrieval_coarse_to_fine_2026-07-08.md`); (ii) Botvinick's own
conflict-adaptation effect is explicitly a MULTI-TRIAL, recursively-updated control-gain loop, not a one-shot
threshold; (iii) Lieder & Griffiths' resource-rational metareasoning computes Value-Of-Computation and RE-
EVALUATES after each computation, stopping only when marginal VOC crosses zero -- an explicitly iterative
stopping rule, not a single pre-committed cutoff. The high-probability-superior generalization: after the
shallow read, RECOMPUTE a margin (now from the coarse-projection ranking itself, or from the retained-trace
cell's OWN top1-vs-top2 shortlist-ranking gap) and decide AGAIN whether to escalate further (e.g., k=0.05V ->
if still ambiguous, k=0.25V -> if still ambiguous, full_fine) -- a genuinely multi-tier cascade rather than a
binary switch, closing the gap between "one frozen threshold" and the brain's actual iterative-refinement
shape. **This is flagged, not pre-registered**, for two honest reasons: (a) it requires a corpus where
`shortlist_hit_rate` genuinely varies with k (the CURRENT smoke corpus saturates at 1.000 even at the smallest
k tested, so there is no signal yet to iterate against -- the binary fusion cell's own corpus fix in Part 3 is
a prerequisite diagnostic for whether a 3-tier cascade would even have anything to bite on); (b) it adds real
implementation complexity (a loop with a re-evaluated stopping rule) the task brief's "content-free SCALAR
dial" framing is trying to avoid pre-building ahead of need. Recommend: ship the binary fusion cell first
(this note's pre-reg); if HARD-PASS but `closure` leaves meaningful headroom to `ORACLE_GATED`, the multi-tier
cascade is the natural next lever, carrying an estimated P_deflated=0.35-0.40 (capped, capped further than the
binary version because it compounds two untested claims: cross-cell coupling AND graded/iterative
recoverability, the latter itself flagged as an open empirical question in the nondestructive-refinement
note's mechanism C).

---

## Cross-thread synthesis

- **`research_neuromodulatory_self_manager_controller_2026-07-08.md`**: this drill is the DIRECT continuation
  of that note's Section 4/5 -- it names the ACC/EVC channel as cheapest-to-test-first and gives Dial#1 its
  exact pre-reg; that cell has since landed HARD_PASS (verified on disk this cycle, not assumed). This drill
  extends the SAME channel's control-law shape to a second telemetry source (combinedgate margin) and a second
  downstream knob (retained-trace shortlist depth), which is the fusion the task brief asked for.
- **`research_energy_scaled_selective_depth_retrieval_coarse_to_fine_2026-07-08.md`** and
  **`research_energy_scaled_selective_depth_nondestructive_refinement_brain_first_2026-07-08.md`**: both
  independently derive "local reflexive gate decides per-item; aggregate neuromodulatory system only retunes
  the criterion" and both flag "does combinedgate's margin predict retained-trace's depth need" as the open,
  untested composition point (P=0.40 in the first note, restated in the second's Mechanism-A composition
  section). This drill is the direct answer: a concrete, buildable, falsifiable pre-reg for exactly that
  composition, now grounded in the ACC/EVC + Kiani-Shadlen literature the task brief specifically asked for.
- **`research_content_gate_brain_grounding_2026-07-08.md`**: confirms the same biased-competition/normalization
  primitive (Desimone & Duncan; Reynolds & Heeger) underlies the certified combinedgate cell this drill reads
  its margin from -- three independent research cycles this week now converge on the same competitive-
  normalization primitive from three different angles (WHICH context slot, WHAT resolution to read it at, HOW
  to gate admission by content), which raises confidence this is a genuine cross-cutting substrate design
  principle, not a one-off coincidence of framing.

---

## Substrate-product implications

- **No new module.** The fusion cell adds exactly one new scalar (`theta_M`), reusing `combinedgate`'s
  existing forward-pass logits and `retained_trace_requery`'s existing two read-paths verbatim. This is the
  cleanest possible instance of "self-manager as a modulating layer over an already-solid core," now
  demonstrated (pending the pre-reg above) for a THIRD independent telemetry-to-knob pairing this week.
- **The 0.092-point coarse-only accuracy gap is the real stake.** This is not a low-stakes toy decision --
  skipping fine-condense uniformly costs a measured 9.2 accuracy points; a working dial recovers most of that
  gap at a fraction of always-deep's cost, and an inert dial genuinely fails a real test, not a strawman.
- **The multi-tier cascade (Part 4) is the correct next build ONLY after the binary fusion cell's corpus fix
  demonstrates real k-dependent difficulty variation exists to iterate against** -- do not build the richer
  mechanism speculatively; let the cheap binary version's own telemetry (does `shortlist_hit_rate` vary with k
  once the corpus has genuine difficulty spread) decide whether there is anything for a 3-tier version to earn.
- **Recommend build order:** (1) implement the Part 3 corpus coupling (reuses both parent cells' existing
  noise constructions, no new mechanism), (2) run the 6-arm smoke at matched N/V ratio to the parent cells
  (per META_RULE_L / discriminator-survives-scale discipline), (3) if HARD-PASS, this closes the "does the
  self-manager sit ABOVE the certified gates as a pure composition, or does it need bespoke machinery" question
  for a THIRD independent case this week -- strong compounding evidence for the general self-manager thesis if
  it lands; if HARD-FAIL_INERT_DIAL, that is equally valuable -- it would mean WHICH-uncertainty and HOW-FINE-
  need are more decoupled in this substrate's geometry than the brain analogy predicts, redirecting the
  self-manager program toward channel-LOCAL depth signals (e.g., the coarse-projection's own top1-vs-top2 gap)
  rather than cross-cell-borrowed ones.

---

## Citations (verified count: 12 external, 3 internal notes, 3 internal cells' on-disk metrics.json)

External (verified via WebSearch this cycle, generic decision-theory/neuroscience terms only, no
substrate-internal names or numbers sent off-platform):
1. Shenhav, A., Botvinick, M.M. & Cohen, J.D. (2013). "The Expected Value of Control: An Integrative Theory of
   Anterior Cingulate Cortex Function." Neuron 79:217-240. https://www.cell.com/neuron/fulltext/S0896-6273(13)00607-7
2. Botvinick, M.M., Braver, T.S., Barch, D.M., Carter, C.S. & Cohen, J.D. (2001). Conflict-monitoring
   computational model. https://pubmed.ncbi.nlm.nih.gov/12641175/
3. Botvinick, M.M., Cohen, J.D. & Carter, C.S. (2004). "Conflict monitoring and anterior cingulate cortex: an
   update." Trends Cogn. Sci. https://www.sciencedirect.com/science/article/abs/pii/S1364661304002657
4. Aston-Jones, G. & Cohen, J.D. (2005). "An Integrative Theory of Locus Coeruleus-Norepinephrine Function:
   Adaptive Gain and Optimal Performance." Annu. Rev. Neurosci. 28:403-450. https://www.annualreviews.org/content/journals/10.1146/annurev.neuro.28.061604.135709
5. Yu, A.J. & Dayan, P. (2005). "Uncertainty, Neuromodulation, and Attention." https://www.gatsby.ucl.ac.uk/~dayan/papers/yud2005.pdf ;
   Acetylcholine precision-weighting, directly measured: "Acetylcholine modulates the precision of prediction
   error in the auditory cortex," eLife 2024/PMC10942646. https://elifesciences.org/articles/91475
6. Bogacz, R. et al. (2006). Reward-rate-optimal DDM thresholds; Simen, Contreras, Buck, Hu, Holmes & Cohen
   (2009), "Reward Rate Optimization in Two-Alternative Decision Making." https://www.simenlab.org/FinalPublications/SimenContrerasBuckHuHolmesCohen2009_JEP_HPP.pdf
7. Hawkins, G.E. et al. (2015). "Revisiting the Evidence for Collapsing Boundaries and Urgency Signals in
   Perceptual Decision-Making." J. Neurosci. https://www.jneurosci.org/content/35/6/2476 (cited to establish
   the honest DISTINCTION this dial does NOT claim, per Part 1d).
8. Desimone, R. & Duncan, J. (1995). Biased competition, cited via the certified cell's own grounding note;
   Reynolds, J.H. & Heeger, D.J. (2009). "The Normalization Model of Attention." Neuron.
   https://www.cns.nyu.edu/heegerlab/content/publications/Reynolds-Neuron2009.pdf
9. Kiani, R. & Shadlen, M.N. (2009). "Representation of Confidence Associated with a Decision by Neurons in the
   Parietal Cortex." Science 324:759. https://www.science.org/doi/10.1126/science.1169405
10. Lieder, F. & Griffiths, T.L. "Resource-rational analysis: understanding human cognition as the optimal use
    of limited computational resources." Behav. Brain Sci. https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/abs/resourcerational-analysis-understanding-human-cognition-as-the-optimal-use-of-limited-computational-resources/586866D9AD1D1EA7A1EECE217D392F4A
11. Pupil-linked LC-NE uncertainty tracking during exploration/decision-making (multiple PMC sources,
    2013-2023): "Pupil Size Encodes Uncertainty during Exploration," PMID 37382476; "Decision-related pupil
    dilation reflects upcoming choice and individual bias," PNAS. https://pnas.org/content/111/5/E618.full
12. Jessup, R.K., Busemeyer, J.R. & Brown, J.W. (2010) and related work on the conflict-vs-error-likelihood
    dissociation debate (cited for the honest open-question flag in Part 1a), surfaced via the conflict-
    monitoring search thread.

Internal (direct on-disk reads/verification this cycle, not assumed from prior notes' prose):
- `d:/AI/hd-instrument/notes/research_neuromodulatory_self_manager_controller_2026-07-08.md` (full read)
- `d:/AI/hd-instrument/notes/research_energy_scaled_selective_depth_retrieval_coarse_to_fine_2026-07-08.md` (full read)
- `d:/AI/hd-instrument/notes/research_energy_scaled_selective_depth_nondestructive_refinement_brain_first_2026-07-08.md` (full read)
- `d:/AI/hd-instrument/notes/research_content_gate_brain_grounding_2026-07-08.md` (partial read, biased-competition section)
- `d:/AI/hd-instrument/experiments/exp_substrate_acc_evc_adaptive_halting_v1.py` (docstring, arms, contract, lines 1-130)
- `d:/AI/hd-instrument/experiments/exp_encoder_retained_trace_requery_coarse_to_fine_v1.py` (docstring, arms, contract, lines 1-130)
- `d:/AI/hd-instrument/experiments/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu.py` (grep for GATE_TAU/RECENCY_GAP_TARGET/combined_logit/arbitration boundary)
- `d:/AI/hd-instrument/data/exp_substrate_acc_evc_adaptive_halting_v1/metrics.json` (verdict verified: HARD_PASS)
- `d:/AI/hd-instrument/data/exp_encoder_retained_trace_requery_coarse_to_fine_v1/metrics.json` (verdict verified: HARD_PASS_RETAINED_TRACE_RECOVERS)
- `d:/AI/hd-instrument/data/exp_substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu/metrics.json` and `_smoke/metrics.json` (verdict verified: HARD_PASS at both smoke and FULL)
- `d:/AI/hd-instrument/tools/orchestrator/research_field_advisor.py` (run at cycle start; no directly-adjacent
  field-advisor candidate maps onto this specific cross-cell composition question -- noted, not force-fit)

**12 external sources verified this cycle, 3 internal research notes read in full, 3 internal cells read
directly, 3 internal metrics.json verdicts verified on disk (not assumed).**

---

## Intuitive summary (plain language)

Two separate upgrades to the substrate's memory system already work: one learned WHEN to stop taking extra
navigation steps (stop once you're confident you've arrived -- a 3x efficiency win), and one learned HOW to
read memory cheaply most of the time and only pay for an expensive, detailed read on a short list of
candidates (recovers full accuracy at one-fifth the cost). This drill asks: can the SAME "how confident am I"
signal that ANOTHER already-working piece already computes (the gate that decides which piece of context is
relevant) be reused to decide when the expensive detailed memory read is worth it -- instead of building a
third, separate confidence-detector from scratch? The brain's own answer is yes: in real brains, the same
neurons that decide WHICH option wins ALSO encode HOW CONFIDENT that decision was, for free, and a
brain region called the anterior cingulate cortex uses exactly that confidence number to decide whether
spending more mental effort is worth it. So the proposed fusion cell reads that already-computed confidence
number from the context-relevance gate and uses one simple, one-time-tuned threshold to decide, per query,
whether to do the cheap read or the expensive one.

**Why it matters:** skipping the expensive read always costs about 9 accuracy points on average -- this is a
real, meaningful decision with real stakes, not a token gesture. The test proposed here is deliberately hard to
pass by accident: the dial has to beat BOTH "always do it the cheap way" and "always do it the expensive way"
at their own respective costs, and also beat "just randomly mix cheap and expensive in the same proportion" --
if it can't clear all of those, the honest conclusion is that the confidence signal isn't actually predicting
what needs a deeper read, and that's a valuable, real finding either way.
**Near-term decision:** build this as a small add-on (no new training, no new architecture) that chains the
noise-construction the two existing cells already have; run the 6-arm smoke; if it passes, this is the third
independent proof this week that the self-manager idea (thin scalar dials sitting over solid, already-working
machinery) is the right shape for this whole line of work, not just a nice theory.

ASCII-only. No emojis. No em dashes.
