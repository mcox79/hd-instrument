# AGGRESSIVE BRAIN-FOUNDATIONAL AUDIT OF *THE COMPONENT ITSELF* (2026-09-09)

Owner directive: "get a very, very good sense of the component we're trying to build; then evaluate it AGGRESSIVELY
for how brain-foundational it is, DOWN TO THE MATHEMATICS OF THE OPERATIONS; research to support."

This audit does what the prior sessions did NOT: it interrogates the END COMPONENT's own math, instead of assuming it is
"BF in form" and tracing upstream. **Headline: the designated final component's central operation is NOT the
counterfactual it is named for — it is a rung-1 (associational) leave-one-out relevance read, and the Causal Hierarchy
Theorem proves no rung-1 functional can be the rung-2/3 quantity it claims to be, REGARDLESS of what feeds it.** An
independent adversarial literature check (hdi_research, 3 refutation attempts, all failed; citations below) confirms it.

---

## 0. WHAT THE COMPONENT IS (a precise, math-level statement)

There are TWO organs in the substrate that both claim "counterfactual causal necessity." The docs designate the FIRST as
the final component and treat the SECOND as an auxiliary sign-consumer. **Mathematically that is backwards.**

**READER A — `hdlab/predictive_world_model.py :: causal_antecedent`** (the designated "final component"; owner-DONE,
"BF in form"). Exact math:
```
P(next_event | context) = softmax(Wᵀ·c + b0)          # single linear read-out, then softmax
c = Σ_k  decay^age(k) · onehot(concept_k)             # recency-weighted BAG of context verb-concept one-hots
surprisal(B | ctx)      = −log2 P(B | ctx)
necessity(A, B)         = surprisal(B | ctx∖A) − surprisal(B | ctx)     # ablate A from the CONDITIONING SET, re-read
inferred cause of B     = argmax_A necessity(A, B)
```
W is learned by a Rescorla–Wagner / delta-rule online pass (`err = onehot − p ; W += lr·outer(c, err)`) on raw textual
ADJACENCY of verb-concepts (simplewiki). Events = bare VERB lemmas (UPOS==VERB via glass-box `pos_tagger` + WordNet
morphy); no arguments, no roles.

**READER B — `hdlab/causal_reasoner.py :: CausalGraph`** (tagged `BF_UNVERIFIED`, "AUDIT NEXT"; treated as the sign
consumer). It operates over a GIVEN discrete cause→effect graph and implements genuine graph SURGERY:
`is_necessary` (remove node, re-propagate reachability from remaining exogenous roots), `intervene_and_compare`
(block/clamp a node → re-realize the outcome sign → compare factual vs counterfactual), `is_actual_cause`
(Halpern–Pearl AC2 with a witness contingency), `signed_effect` (±1 sign-product propagation, conflicting→0).

## 1. THE OPERATION-BY-OPERATION VERDICT (Reader A, the designated final component)

| # | operation | exact math | verdict | the defect (if any) |
|---|---|---|---|---|
| 1 | surprisal | −log2 P(B\|ctx) | **BF (PINNED)** | Shannon/Hale surprisal; N400 amplitude ∝ surprisal (Frank 2015; Rabovsky 2018). Genuinely the brain's signal. |
| 2 | forward predictor | softmax(Wᵀc + b0), ONE linear layer | **BF-SPIRIT** | a log-linear generative predictor is defensible, but SHALLOW — Rao–Ballard predictive coding is HIERARCHICAL; one layer has no compositional/hidden structure. |
| 3 | learning rule | R–W delta-rule, online single pass, no freeze | **BF (PINNED rule)** | Schultz dopaminergic RPE; the delta-rule = the exact gradient of softmax cross-entropy (elegant). BUT R–W learns cue→outcome ASSOCIATION — it builds a rung-1 model *by construction*. Right rule; associative object. |
| 4 | context representation | recency-decay BAG: c = Σ decay^age·onehot | **NOT-BF (load-bearing)** | (a) recency decay = ACT-R base-level, OK; (b) a BAG discards role-binding — the brain's discourse unit is a BOUND situation state (Zwaan–Radvansky event-indexing; Frankland–Greene lmSTC agent/patient binding). The substrate HAS FHRR binding (`event_bundle`) and it is unused here. |
| 5 | event grain | bare VERB lemma, no arguments | **NOT-BF** | "water", "fall" as free atoms; no patient, no state, no value. The brain-faithful relatum is a bound proposition WATER[agent,patient:PLANT]→LIVE[patient:PLANT] (Schank–Abelson CD; Kintsch CI; Dowty CAUSE(BECOME(state))). |
| 6 | **THE CAUSAL READ** | necessity(A,B) = surprisal(B\|ctx∖A) − surprisal(B\|ctx), argmax_A | **NOT-BF — RUNG-1 MISLABEL (the headline)** | see §2. |
| 7 | selection | hard argmax_A | **BF-SPIRIT** | the brain does graded constraint-satisfaction (Kintsch CI; McClelland IA) + admits multiple causes; winner-take-all is a simplification. |

## 2. THE HEADLINE FINDING — the "counterfactual necessity" read is rung-1 association, and provably cannot be otherwise

Algebra: `necessity(A,B) = surprisal(B|ctx∖A) − surprisal(B|ctx) = −log P(B|ctx∖A) + log P(B|ctx) = log[ P(B|ctx) / P(B|ctx∖A) ]`.
That is the **pointwise conditional log-likelihood ratio** — the *leave-one-out predictive relevance / information gain*
of A for B given the rest of the context. It is a **functional of ONE observed joint distribution** (the softmax
predictor). Removing A from the CONDITIONING SET is an OBSERVATION (`P(B | ctx∖A)`); it does **not** sever A's causal
parents (no graph surgery) and does **not** abduct-then-act. **It is definitionally Pearl Layer 1.**

The three rungs, made precise on the canonical barometer/storm (Reichenbach common cause):
- **Observational** `P(storm | barometer=low)` is HIGH (they co-vary through atmospheric pressure). Leave-one-out
  relevance of the barometer for "storm" is LARGE — dropping it moves the prediction a lot. **← what Reader A computes.**
- **Interventional** `P(storm | do(barometer=low))` = `P(storm)`. Forcing the needle does nothing to the weather. **Effect = 0.**
- **Counterfactual** `P(storm_{barometer=high} | observed low reading + storm)`: abduct (pressure was low) → act (needle high)
  → predict (pressure still low ⇒ storm still occurs). **Effect = 0.**

So `necessity(barometer, storm) > 0` under Reader A ⇒ **it would name the barometer a cause of the storm** — the textbook
confound. That one example demonstrates the operation is rung-1: leave-one-out relevance ≠ 0 while BOTH the causal effect
and the counterfactual effect = 0.

**Causal Hierarchy Theorem backstop (PINNED):** Bareinboim, Correa, Ibeling & Icard 2022 (*On Pearl's Hierarchy and the
Foundations of Causal Inference*) — the three layers separate on all but a **measure-zero** set of SCMs; Ibeling & Icard
(NeurIPS 2021) add that assumption-free lifting is possible only on a **meager** set and any licensing assumption is
**statistically unverifiable in principle**. So **no functional of the observational distribution — Reader A's included —
generically recovers necessity, REGARDLESS of what W feeds it.** This is deeper than the prior "the input is associative"
framing: even a PERFECT directed-causal forward model, read by leave-one-out, stays rung-1. Feeding mined directed
testimony into W makes W a better rung-1 *direction* statistic (which we measured: +0.097), NOT a counterfactual engine.

**Refutations attempted by the research lead, all FAILED:**
1. *"R–W recovers causal structure → lifts the rung."* No. R–W's fixed point relates to ΔP (Danks 2003), but ΔP is
   itself a rung-1 contrast; it equals a causal effect only under Cheng's untestable no-confounding premise — imported
   from outside the data, neither stated nor checked here. And the code isn't even ΔP; it's a leave-one-out log-ratio
   (conditioning-adjustment), which identifies an effect only under the back-door criterion (known graph + verified
   admissible set — absent).
2. *"Maybe it lands in the measure-zero collapse set."* That set is the non-generic pathology; the module asserts no
   structural condition placing it there. Even if the softmax coincidentally equalled the interventional distribution,
   "condition on a subset" equals the effect only under unconfoundedness — unasserted, unverified.
3. *"N400 is a real brain signal, so it's foundational."* This actually SUPPORTS rung-1 (see §4) — it does not lift the rung.

**The naming is a mislabel across the board.** All THREE constructs the docstring cites are rung-2/3:
- **Gerstenberg–Tenenbaum CSM** (Gerstenberg et al. 2021, *Psych Review*) is a rung-2/3 SIMULATION over a *generative
  model* (noisy physics engine): (a) build the structural model, (b) abduct/condition on the observed clip, (c)
  do-intervene removing the candidate, (d) simulate forward resampling noise and compare. Its Experiment 1 is decisive
  FOR THIS AUDIT: judgments diverged between scenes where *what actually happened was identical but what would-have
  differed* — so the judgment is provably NOT a function of the observed distribution, which is all a leave-one-out
  predictor can see. The CSM's own paper contains the empirical refutation of the identification.
- **Trabasso "necessity in the circumstances"** (Trabasso & van den Broek 1985; from Mackie's INUS) is explicitly a
  COUNTERFACTUAL test — also rung-3.
- **Kuperberg N400** is *associative predictive coherence* (rung-1) — so citing it actually UNDERCUTS the "counterfactual"
  label while confirming the surprisal machinery is a real rung-1 brain signal.

## 3. READER B (`causal_reasoner`) IS the rung-2/3 engine — but it was unverified, and it is impoverished

I audited its code (the ledger had it `BF_UNVERIFIED`/"AUDIT NEXT"). Findings, at the operation level:
- `is_necessary`, `intervene_and_compare`, `_realize(blocked=/forced=)` — genuine graph SURGERY: they SEVER a node's
  incoming determination and re-propagate. **This IS a rung-2 do()-operation.** Form: BF-SPIRIT→BF.
- `is_actual_cause` — Halpern–Pearl AC2 with a witness contingency (hold over-determining alternatives off, check the
  flip). **This IS rung-3 actual causation.** Form: BF-SPIRIT.
- **BUT the impoverishments are real:** (i) NO ABDUCTION — `intervene_and_compare` fixes all exogenous roots to +1
  instead of inferring the exogenous state from evidence, so it is a "fixed-root twin network," not the full
  abduct→act→predict counterfactual; (ii) signs are DISCRETE ±1 with "conflicting→0" cancellation — a heavy
  simplification of graded structural equations (real SCMs have graded functional forms, noise, non-monotone
  combination); (iii) necessity = pure graph REACHABILITY from remaining roots — no quantitative degree of
  sufficiency/necessity; (iv) it operates over a GIVEN discrete graph (`sm.causal_links`), so it inherits the
  extraction + the signed-edge-source problem wholesale.

**Verdict: `causal_reasoner` is the correct rung-2/3 FORM (relabel it BF-SPIRIT, not BF), but it is edge-starved,
sign-starved, abduction-free, and discrete.** It is the real "final component" candidate for genuine counterfactual
necessity — not `causal_antecedent`.

## 4. THE FAIR STEELMAN (what IS brain-foundational here)

Reader A is a **faithful model of a real rung-1 brain computation** — just not the one it's named for:
- **Surprisal = −log P is PINNED as the brain's signal** (Frank et al. 2015 N400∝surprisal; Rabovsky et al. 2018
  N400 = semantic-update/prediction-error in the Sentence-Gestalt model; Kuperberg & Jaeger 2016 multi-level predictor).
- **Leave-one-out predictive relevance IS what passive RESONANCE does during reading** — the always-on, automatic,
  associative reactivation of causally-*associated* antecedents (Myers & O'Brien 1998 resonance; van den Broek Landscape
  Model; Tzeng et al. 2005). This is a genuine rung-1 process and it genuinely concerns causal-antecedent *reactivation*.
- **But the line is well-drawn in that same literature (RI-Val; O'Brien & Cook 2016):** stage 1 = passive resonance
  (always-on, associative, rung-1 — RETRIEVE candidates); stage 2 = validation/integration (slower, coherence-break
  gated, resource-limited — ADJUDICATE whether the candidate actually coheres/causes); explicit counterfactual necessity
  sits above that, a separate constructive stage. **Even resonance theorists do NOT claim resonance computes necessity —
  resonance retrieves; necessity is adjudicated downstream.**
- **A DISTINCT neural circuit does the rung-2/3 work** (additive, not disjoint): Satpute et al. 2005 (identical word
  pairs, CAUSAL vs ASSOCIATIVE judgment → selective left dlPFC + right precuneus; framed as evidence AGAINST
  associationist accounts); Van Hoeck, Watson & Barbey 2015 (counterfactual reasoning = PFC control + vmPFC/hippocampal
  constructive SIMULATION network); constructive-simulation substrate (Mullally–Maguire 2014; Schacter–Addis).
  (Caveat: DROP any "Gerstenberg 2017 fMRI" citation — the 2017 study is eye-tracking, not fMRI; unverifiable as fMRI.)

## 5. WHAT THIS CHANGES (the reframe — this corrects a mislabel propagating through the ledger and the frontier claim)

1. **The BF-tag on `predictive_world_model` is WRONG.** It currently reads "counterfactual-ablation OPERATION faithful."
   Correct tag: the operation is **rung-1 predictive-relevance / associative-antecedent reactivation**, faithful at
   Layer 1, MISLABELED as rung-2/3. Disposition = **relabel-and-descope, not rip-out**: keep the organ for what it is
   (rename `causal_antecedent` → e.g. `predictive_relevance` / `associative_antecedent_reactivation`; strip the
   CSM/Trabasso/necessity language; re-cite Frank/Rabovsky/Kuperberg/Myers–O'Brien). This is a Q111 hdlab change for
   strategy; the solver cannot write hdlab. Also correct `causal_reasoner` `BF_UNVERIFIED` → `BF_SPIRIT` (rung-2/3 form,
   impoverished as in §3). Coordinate with the concurrent registry session — do NOT double-write the registry.
2. **The prior "frontier = grounded signed-quantity source" conclusion was directionally right but ROOTED one level too
   shallow.** The deeper truth: genuine counterfactual necessity needs the **abduct→do→simulate loop over a bound,
   graded generative situation model** (Reader B's form, made graded + given abduction + fed a bound state). The signed
   edge is ONE input to that loop; even a perfect sign source read by Reader A (rung-1) cannot produce necessity. So the
   "5 sign sources all fail" result is a symptom of the deeper mislabel, not the whole story: they were all being asked
   to rescue a rung-1 read.
3. **The banked positives still stand and are correctly rung-1.5:** the mined store's DIRECTION win (+0.097 CI-sep) is a
   genuine rung-1.5 contribution (causal MARKING carries a directional prior co-occurrence lacks) — it is exactly the
   right *kind* of thing to feed the FORWARD model / the resonance stage, and it is honestly a rung-1 asset. Nothing to
   withdraw; only the "necessity reader is BF-in-form" claim is corrected.

## 6. CITATIONS (from the independent adversarial check; PINNED unless noted)
Bareinboim, Correa, Ibeling & Icard 2022 (Causal Hierarchy Theorem); Ibeling & Icard 2021 (topological, NeurIPS);
Danks 2003 (R–W↔ΔP); Cheng 1997 (causal power, untestable premise); Gerstenberg, Goodman, Lagnado & Tenenbaum 2021
(CSM, *Psych Review*); Gerstenberg et al. 2017 (eye-tracking — NOT fMRI); Trabasso & van den Broek 1985; Satpute et al.
2005 (causal vs associative fMRI dissociation); Van Hoeck, Watson & Barbey 2015 (counterfactual network review);
Mullally & Maguire 2014 (scene construction); Frank, Otten, Galli & Vigliocco 2015 (N400∝surprisal); Rabovsky, Hansen &
McClelland 2018 (N400 = update, *Nat Hum Behav*); Kuperberg & Jaeger 2016; Myers & O'Brien 1998 (resonance);
van den Broek / Tzeng et al. 2005 (Landscape Model); O'Brien & Cook 2016 (RI-Val two-stage). [CONTESTED: granular
modularity of the causal circuit — it is additive, not disjoint; any CSM-specific fMRI localization.]
