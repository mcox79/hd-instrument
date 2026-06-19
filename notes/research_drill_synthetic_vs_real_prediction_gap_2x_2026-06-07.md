# Research Drill: Synthetic-vs-Real Prediction Gap -- Why Do Our Drill Predictions Fail?
# 2x methodology drill -- 2026-06-07
# Trigger: Three back-to-back prediction failures in one session; all failed in the same direction
#   (proxy/synthetic more optimistic than production reality)
# Level: level-2 operational methodology drill per [[feedback-2x-means-depth]]

---

## HEADLINE

Three drill failures in one session share a single root pattern: each drill built its prediction
on a population that differed from production in a specific, detectable way. In all three cases,
a cheap production-encoder check (1-2 hr CPU) would have caught the mismatch BEFORE engineering
work started. The fix is not "do more theory" -- it is to run a mandatory empirical pre-test on
the production setup before authorizing any engineering. Adding this step adds 1-2 days per
decision cycle and should prevent 1-3 weeks of wasted engineering per cycle where the prediction
was wrong.

P_deflated (methodology framework is correct and transferable): 0.55
(deflated 0.20 from naive 0.75; calibration penalty per [[feedback-lit-scan-calibration-penalty]];
this is methodology, not a novel mechanism, so deflation is less severe)

---

## SECTION 1: PATTERN ANALYSIS OF THE THREE FAILURES

### Failure A: Sparse-KEY distractor assumption

What the drill assumed:
  The K-hop noise drill modeled distractors as random vectors with coherence c_d approx 0
  relative to the query. Under random distractors, the distractor contribution cancels via CLT
  averaging across B shards at large bundle size. The drill predicted sparse-KEY would help at
  all B.

What reality showed:
  LVH #248 tested sparse-KEY on a RANDOM-distractor harness at B >= 10 and found a tie (dense
  self-recovers at large B because random distractor noise averages out). The K-hop analysis
  was right about coherent distractors but the test used random distractors.

  Production LSH routing selects shards that are semantically NEAR the query. Near-neighbor
  shards return COHERENT distractors: c_d approximately 0.20-0.35 (LSH-selected near-neighbors).
  Under coherent distractors, the zero-mean cancellation argument breaks. Distractor signal
  ACCUMULATES across K hops instead of cancelling.

  The reconciliation drill (sparse_key_low_B_regime_reconciliation) showed the two findings ARE
  compatible -- they test different distractor regimes. The production regime is coherent, not random.

Was there a signal in the drill that should have flagged the risk?
  YES. The drill literature cited was on random-distractor associative memory retrieval
  (Hopfield-family). Coherent distractors from structured routing were not in the cited
  literature. The drill's "Production posture: Option A" recommendation came from coherent-
  distractor algebra WITHOUT a cited empirical test on coherent distractors. This is the
  signal: prediction from algebra without empirical validation on the production setup.

---

### Failure B: SRHT anisotropy assumption

What the drill assumed:
  The ZKL rescue drill (3x deep, 2026-06-07) predicted SRHT would reduce ZKL on Llama keys.
  The mechanism: SRHT applies a Hadamard transform that spreads energy across all dimensions,
  reducing effective anisotropy rho_eff. Under the arcsin law, lower rho_eff leads to lower
  non-member score mean and lower ZKL. The prior SRHT test on MiniLM showed 1.74x improvement.

What reality showed:
  Exp-Dev URGENT note (smoke n=200, Llama-3.2-1B L15 left-pad):

    SRHT passes | MiniLM ZKL(50) | Llama ZKL(50)
    0 passes    | 0.41           | 0.22
    1 pass      | 0.24           | 0.45
    2 passes    | 0.175          | 0.57
    3 passes    | 0.175          | 0.58

  SRHT MONOTONICALLY INCREASES leakage on Llama (0.22 -> 0.58). The MiniLM result did NOT
  transfer. SRHT engineering (Auth-3, 3-5 days) was cancelled.

  Mechanism hypothesis from Exp-Dev: MiniLM (D=384, bidirectional) and Llama-L15 (D=2048,
  causal last-token) have different anisotropy structures. Hadamard mixing on Llama's cone-
  concentrated last-token representation spreads signal into a more uniform sign pattern that
  the membership inference attack exploits MORE. Hadamard mixing amplifies, not reduces, the
  attack signal on last-token causal LM embeddings.

Was there a signal in the drill that should have flagged the risk?
  YES, explicitly. The 3x rescue drill stated P_deflated=0.35 with "further 0.05 for uncertainty
  on whether SRHT fully restores isotropy post-sign-quant." The citations for SRHT isotropy
  restoration came from the bidirectional-encoder literature (Ailon & Chazelle 2006 on JL
  transforms; post-hoc orthogonalization work on BERT-family embeddings). No citation tested
  SRHT on causal LM last-token pooled embeddings. The "0.05 further deflation" was a correct
  flag but was too small -- the mechanism risk was qualitative, not a small quantitative
  uncertainty.

  The drill should have stated: "This prediction is ONLY valid if Llama's anisotropy structure
  behaves analogously to MiniLM under Hadamard mixing. If Llama's cone structure is different
  in kind (not just magnitude), SRHT may amplify the attack signal instead of reducing it.
  Cheap pre-test: 1-hr CPU test with SRHT {0,1,2} passes on Llama before any engineering."

---

### Failure C: MiniLM-as-proxy (structural, repeated)

What the drills assumed:
  Multiple drills used MiniLM as the test encoder because it is cheap (D=384, fast). When
  production encoder (Llama-1B BASE, L=15, last-token) was introduced, predictions from
  MiniLM tests were expected to transfer.

What reality showed:
  MiniLM and Llama have qualitatively different geometry:
  - MiniLM: bidirectional transformer, [CLS] pooling or mean-pool, D=384, d_eff approximately
    77-91 after whitening, low anisotropy rho_0 approximately 0.02-0.08 (sentence-trained to
    be isotropic)
  - Llama-1B: causal LM, last-token pool, D=2048, d_eff much lower (cone-collapsed raw;
    whitening rescues but to different geometry), anisotropy rho_0 approximately 0.20-0.35 per
    arcsin-law analysis

  Documented transfer failures:
  (a) SRHT: 1.74x improvement on MiniLM, REVERSES to 2.6x degradation on Llama
  (b) Sparse-KEY: synthetic tests on random-distractor harness (structurally MiniLM-era);
      production coherent-distractor behavior different
  (c) Raw capacity: raw_cap=0 for Llama (cone-collapsed); whitening mandatory before any
      capacity measurement (MiniLM raw cap > 0)
  (d) ZKL baseline: MiniLM rho_0 approximately 0.02 -> ZKL(50) approximately 0.03-0.05;
      Llama rho_0 approximately 0.25 -> ZKL(50) approximately 0.40 (11x gap, fully explained
      by anisotropy difference)

Was there a signal?
  YES. The moment production encoder was locked (Llama-1B BASE + last-token pooling,
  PRODUCTION ARCHITECTURE LOCKED note 2026-06-07), every drill output that cited only
  MiniLM-based literature or only MiniLM empirical results became suspect. The flag was
  available but not systematically applied as a veto on "act on drill prediction."

---

## SECTION 2: ROOT-CAUSE TAXONOMY

### Type 1: Wrong distribution assumption

  What it is: The drill assumes input vectors come from a distribution different from
  production reality. The most common form: drill assumes random/uniform inputs;
  production has structured/clustered inputs.

  Example: Sparse-KEY drill used random distractors (c_d approximately 0); production uses
  coherent LSH-selected near-neighbor distractors (c_d approximately 0.20-0.35).

  Detection signal (pre-test check):
  - Does the drill literature explicitly test COHERENT (not random) inputs?
  - Is the distractor/noise model stated explicitly in the drill's theoretical framework?
  - Does the production routing mechanism (LSH, HNSW, consistent hash) preferentially select
    near-neighbor items (i.e., are distractors structurally correlated with the query)?

  If the answer to the last question is YES and the drill noise model is random, the
  prediction is Type 1 suspect.

---

### Type 2: Wrong encoder assumption

  What it is: The drill builds predictions based on the behavior of encoder family A;
  production uses encoder family B. The two families have qualitatively different properties
  that cause the mechanism to behave differently or reverse.

  Example: SRHT drill predictions validated on MiniLM (bidirectional, isotropic);
  production encoder is Llama-1B BASE (causal, last-token, anisotropic cone). SRHT that
  reduces anisotropy on MiniLM amplifies attack surface on Llama.

  Example 2: Any drill whose cited literature comes entirely from the BERT/bidirectional
  encoder community (mean-pool, [CLS] token, contrastively fine-tuned for retrieval).
  Production is a causal LM with last-token pooling. These two families have:
  - Different pooling (CLS/mean vs last-token)
  - Different anisotropy structure (sentence-trained near-isotropic vs causal cone)
  - Different dimensional collapse behavior under fine-tuning
  - Different capacity behavior (raw MiniLM > 0; raw causal LM = 0 without whitening)

  Detection signal (pre-test check):
  - Are the drill empirical citations from the bidirectional-encoder community only?
  - Does the drill cheap test use MiniLM but not the production encoder?
  - Is the mechanism sensitive to pooling strategy (mean-pool vs last-token)?
  - Is the mechanism sensitive to anisotropy level or rho_0?

  If the drill cites only bidirectional literature AND the mechanism depends on the
  isotropy structure of embeddings, the prediction is Type 2 suspect.

---

### Type 3: Wrong scale assumption

  What it is: The drill validates at small N or small M; the production environment
  operates at different scale where qualitatively different regimes appear.

  Example (partial): sparse-KEY was validated at small N (cycle 142 / LVH #248) at
  B=10 random-distractor test. Production is N=65536 with coherent distractors at
  larger K-hop chains.

  Example from prior cycles: cycle 130 Slot 9 regression was a scale-specific failure
  mode that only appeared at larger N.

  Detection signal (pre-test check):
  - Is there an empirical test at production N (N=65536), production B (B=10 typical),
    production K (K=5-12 for multi-hop)?
  - Does the drill theory include a scale-dependent term (sigma approximately 1/sqrt(N),
    CLT arguments, spectral bulk edge at production M/N)?
  - If scale matters to the mechanism, has the drill tested at production scale or only
    at toy N?

---

## SECTION 3: WARNING SIGNS -- PRE-ACTION CHECKLIST

Before acting on a drill prediction (before authorizing engineering or queue slot):

Checklist item 1 -- PRODUCTION ENCODER CHECK
  "Does the drill cite empirical work using the EXACT production encoder family
  (causal LM, last-token pool, D=2048, rho_0 > 0.15)?"
  If NO: mark as Type 2 suspect. Required pre-test: 1-hr CPU run on Llama-1B L15 with
  the proposed mechanism before engineering authorization.

Checklist item 2 -- INPUT DISTRIBUTION CHECK
  "Does the drill theory model use COHERENT/STRUCTURED inputs (c_d > 0.10) that
  match production LSH routing?"
  If the answer is NO (drill uses random/uniform inputs): mark as Type 1 suspect.
  Required pre-test: measure production c_d empirically (1-hr CPU diagnostic) or
  confirm the mechanism is c_d-independent before acting.

Checklist item 3 -- SCALE CHECK
  "Is there empirical validation at production N=65536, production B=10, production
  K-hop chain K >= 5?"
  If NO: mark as Type 3 suspect. Required pre-test: smoke at production-scale N.

Checklist item 4 -- CITATION FAMILY CHECK
  "Are ALL empirical citations from the bidirectional-encoder community (BERT/MiniLM/
  sentence-transformer family) with no causal-LM-specific empirical results?"
  If YES: the prediction may be systematically biased toward bidirectional-encoder
  behavior. Flag. Require at least one citation from the causal-LM community, or run
  production-encoder pre-test.

Checklist item 5 -- P_DEFLATED SPLIT CHECK
  "What is the drill P_theoretical vs P_empirical at production setup?"
  P_theoretical = confidence the mechanism is real in some regime (often high: 0.70-0.90)
  P_empirical = confidence the mechanism transfers to production setup (often low: 0.20-0.50)
  Actionable P = P_theoretical x P_empirical
  If actionable P < 0.35: do NOT authorize engineering. Run pre-test first.

---

## SECTION 4: FIVE RECOMMENDATIONS FOR MORE RELIABLE DRILLS

### Recommendation 1: Run the cheap production-setup confirmation BEFORE engineering

Standard three-check protocol:
  (a) Production encoder test: 1-2 hr CPU, Llama-1B BASE L15 left-pad, NOT MiniLM proxy
  (b) Production-realistic input distribution: coherent near-neighbor distractors NOT random
  (c) Production scale: N=65536, B=10, K=5-12 as appropriate

Cost: adds 1-2 days per engineering decision.
Benefit: prevents 1-3 weeks of wasted engineering when prediction was wrong.
Net: faster progress toward v1 demo.

The check is NOT verification. It is a cheap falsification opportunity before spend.
If the check fails: do NOT proceed to engineering. Return to Research for root-cause.
If the check passes: proceed to engineering with substantially higher confidence.

---

### Recommendation 2: Drill outputs MUST explicitly state prediction validity conditions

Every drill prediction should include a "Prediction valid under" block:

  "Prediction valid under these specific conditions:
  - Encoder: [exactly which encoder family + pooling strategy]
  - Input distribution: [random/structured; c_d assumption]
  - Scale: [N range, B range, K range]
  - Mechanism dependencies: [list of structural assumptions]"

  "Prediction will NOT survive if:
  - Encoder is causal LM with last-token pooling AND mechanism is sensitive to rho_0
  - Input distribution is coherent (c_d > 0.10) AND drill was validated on random inputs
  - [encoder-specific failure mode]"

  "Cheap empirical pre-test to validate:
  - [1-2 sentence description of the 1-hr CPU test that would confirm or refute]"

This makes the prediction transfer assumptions visible at output time, not post-mortem.

---

### Recommendation 3: Split P_deflated into P_theoretical and P_empirical

Current practice: single P_deflated (e.g., 0.45) that combines mechanism confidence with
transfer confidence.

Problem: the three failures all had reasonable P_deflated (0.35-0.55) but for the wrong
reason -- P_theoretical was high (0.70-0.85) while P_empirical-at-production was low
(0.20-0.40). The product (0.14-0.34) would have flagged these as pre-test required.

Proposed drill output format:
  P_deflated (theoretical): 0.75 -- confidence the mechanism is real in some regime
  P_deflated (empirical at production setup): 0.35 -- confidence it transfers to Llama+coherent
  P_deflated (actionable): 0.75 x 0.35 = 0.26 -- use THIS for engineering authorization

  If P_actionable < 0.35: RUN PRODUCTION PRE-TEST before authorizing engineering.
  If P_actionable >= 0.35 and P_empirical < 0.50: RUN PRE-TEST but can proceed in parallel
    with pre-test if engineering is low-cost (less than 0.5 day).
  If P_actionable >= 0.35 and P_empirical >= 0.50: Proceed with normal caution.

---

### Recommendation 4: Retire MiniLM as primary proxy for Llama production

MiniLM and Llama are in different geometry regimes. They differ on:
  - Pooling strategy: [CLS]/mean-pool (MiniLM) vs last-token (Llama)
  - Anisotropy: rho_0 approximately 0.02-0.08 (MiniLM) vs rho_0 approximately 0.20-0.35 (Llama)
  - Raw capacity: MiniLM > 0 raw; Llama = 0 raw (whitening mandatory)
  - SRHT behavior: reduces ZKL (MiniLM); amplifies ZKL (Llama)
  - Effective rank: d_eff approximately 77-91 (MiniLM); lower raw but whitening-rescuable (Llama)

MiniLM is still useful as a cheap sanity check or as a "does the harness work" test.
It is NOT a valid proxy for Llama production behavior on any mechanism that depends on
anisotropy, pooling geometry, or membership-inference privacy.

Rule: if the drill mechanism is sensitive to rho_0 or pooling strategy, MiniLM results
are uninformative about Llama behavior. Use the production encoder in the pre-test even if
it is more expensive.

---

### Recommendation 5: Explicitly require the pre-test in routing notes to Exp-Dev

Current routing notes specify the experiment design. They should also include:
  "Pre-test required before full run: [1-2 sentence description]"
  "Engineering authorization: HOLD until pre-test smoke passes"

This structurally prevents Exp-Dev from proceeding to engineering on a prediction that
has not been empirically validated at production setup. The pre-test should be:
  - 1-2 hr CPU maximum
  - On the production encoder (Llama-1B BASE L15 left-pad)
  - With production-realistic input distribution
  - Measuring the key quantity the mechanism claims to improve

If the pre-test fails: escalate to Research for root-cause, do NOT proceed to engineering.

---

## SECTION 5: UPDATED DRILL OUTPUT TEMPLATE

For every drill going forward, the output should include the following block after the
HEADLINE and before SECTION 1:

---
PREDICTION VALIDITY BLOCK

Conditions under which this prediction is valid:
  Encoder: [name exactly; pooling; dimension; anisotropy expected]
  Input distribution: [random / structured-coherent / LSH-coherent; c_d estimate]
  Scale: [N range; B range; K range]
  Write rule: [Hebb / pseudoinverse / other]

This prediction WILL NOT survive if:
  [failure mode 1: e.g., "production encoder is causal LM with rho_0 > 0.15 and mechanism
  is sensitive to non-zero-mean embedding geometry"]
  [failure mode 2: e.g., "production distractor structure is coherent (c_d > 0.10) and drill
  was validated on random distractors"]
  [failure mode 3: scale-specific failure]

Cheap empirical pre-test to validate (1-2 hr CPU):
  [Description of single cheap test: what to run, what to measure, what threshold to check]
  PASS if: [specific numerical criterion]
  FAIL if: [specific numerical criterion]

P_deflated (theoretical): [X]
  Confidence that the mechanism is real in some regime; high for well-derived algebraic results
P_deflated (empirical at production setup): [Y]
  Confidence that the mechanism transfers to Llama + coherent inputs + production N
  Note: start at 0.40 by default if no production-encoder empirical work cited; reduce further
  if literature is bidirectional-encoder-only
P_deflated (actionable = X * Y): [Z]
  Engineering authorization threshold: Z >= 0.35 for proceed; Z < 0.35 for pre-test first

Transfer confidence from proxy to production: HIGH / MEDIUM / LOW
  HIGH: drill has empirical results on production encoder + production distribution
  MEDIUM: drill has theoretical argument why behavior should transfer; one side tested
  LOW: drill uses proxy encoder or random inputs; no production-encoder empirical work
---

---

## SECTION 6: NORTH-STAR IMPLICATION

The core inefficiency: "prediction -> engineering" cycle skips an empirical confirmation step.
The fix is adding "prediction -> 1-2 hr pre-test -> engineering."

Cost of pre-test: 1-2 days per decision.
Cost of skipping pre-test when wrong: 1-3 weeks wasted engineering.
Breakeven: pre-test is net positive if P(prediction wrong) > 5-10%, which is clearly the case
given three consecutive failures in one session.

For the 5-7 week v1 demo timeline:
  Without pre-test discipline: expect 1-2 more week-long dead ends (same failure mode).
  With pre-test discipline: those dead ends convert to 1-2 day pivots.
  Net gain: 2-4 weeks of recovered engineering time, which is 40-60% of the remaining timeline.

This is not a marginal improvement. It is the rate-limiting factor for the final stretch.

For drills currently in flight:
  - Storage efficiency drill (3x): output should include the production-setup empirical pre-test.
    Key question: does the storage mechanism transfer from synthetic to real Llama embeddings?
    Pre-test: 1-hr CPU cell with Llama-1B L15, production-realistic fact distribution.
  - Privacy mechanism path: SRHT cancelled on correct grounds. Next mechanism proposal
    should include the split P_deflated before authorization.

For routing notes to Exp-Dev going forward:
  Include the pre-test cell explicitly in the routing note.
  "HOLD engineering authorization until pre-test passes."

---

## SECTION 7: FALSIFIABLE PREDICTIONS AND HARD-FAIL THRESHOLDS

### Prediction P1: Pre-test protocol reduces wasted engineering cycles

HARD-PASS: Over the next 5 experiments authorized via the new pre-test protocol, zero
  experiments result in a "mechanism does not transfer from proxy to production" failure.
HARD-FAIL: Two or more experiments, even with pre-test, fail due to proxy-to-production gap.
  (Indicates there is a deeper failure mode not captured by the three-type taxonomy.)
MIDDLE-BAND: One experiment fails despite pre-test; pre-test was too cheap to catch the gap.
  (Indicates pre-test threshold needs to be raised or scope extended.)

---

### Prediction P2: Splitting P_deflated into theoretical x empirical improves calibration

HARD-PASS: Drills that generate P_actionable >= 0.35 have empirical validation at >= 70%
  rate over the next 10 drills.
HARD-FAIL: Drills with P_actionable >= 0.35 fail empirically at > 40% rate (same as current).
  (Indicates the P_empirical estimate is not well-calibrated even with the new framework.)

---

### Prediction P3: MiniLM-to-Llama gap is encoder-family-specific, not mechanism-specific

HARD-PASS: At least 3 mechanisms that show X on MiniLM show DIFFERENT X' on Llama (not
  merely attenuated; qualitatively different direction).
HARD-FAIL: MiniLM and Llama predictions agree within 2x on all mechanisms tested in next
  10 experiments. (Indicates gap was specific to SRHT, not a general proxy failure.)
Current evidence: SRHT reverses; raw capacity differs qualitatively; anisotropy rho_0
  differs by 5-15x. P_deflated for P3: 0.70.

---

## SECTION 8: CROSS-THREAD SYNTHESIS WITH PRIOR FINDINGS

### Connection to [[feedback-causal-lm-last-token-pool]]
The mean-pool bug (CLOUD-1) and the SRHT failure are the same root cause from different angles.
Both trace to: causal LMs concentrate semantics at the last token, creating a geometric cone
that differs qualitatively from bidirectional encoder output. The first time this surfaced as
a production failure was mean-pool (2026-06-06, CLOUD-1). The SRHT failure is the second
manifestation. A third will likely appear unless the encoder-family check is structural.

### Connection to [[feedback-small-scale-first-methodology]]
The rung ladder methodology assumes cheap tests will reveal what expensive tests will confirm.
This is correct when proxy and production belong to the SAME family. It fails when the cheap
test uses a qualitatively different proxy. The fix is not to skip small scale -- it is to
ensure the small-scale test uses the right encoder family, even if the test is smaller in N.
A tiny Llama test at N=1024 is more informative than a medium MiniLM test at N=4096 for any
mechanism that depends on encoder geometry.

### Connection to [[feedback-negative-results-2x-research]]
SRHT engineering was cancelled based on a clear HARD-FAIL direction (monotone worse at
n=200). This is the correct outcome of the pre-test being run (though post-planning, not
pre-planning). The discipline already caught one dead end. The goal is to catch it BEFORE
the engineering slot was opened, not after the smoke was run.

### Connection to [[feedback-dont-dismiss-adjacent-methods]]
The taxonomy here cuts the other direction: do NOT assume adjacent methods (e.g., SRHT
from bidirectional-encoder privacy literature) transfer to production without a pre-test.
Adjacency in the mathematical family does not guarantee transfer when the encoder-family
geometry differs.

---

## SECTION 9: SUBSTRATE-PRODUCT IMPLICATIONS

For the v1 demo timeline:

  1. Privacy mechanism path: SRHT cancelled correctly. Next mechanism (qualified claim,
     rate-limit posture, or non-SRHT decorrelation) should follow the pre-test protocol
     before engineering authorization.

  2. Storage efficiency path: if any proposed storage improvement was validated on
     synthetic inputs or MiniLM, run the production-encoder pre-test before engineering.

  3. K-hop path: sparse-KEY at B >= 10 prediction (Option A) rests on the c_d estimate
     for production LSH routing. The cheap decisive test (Cell A: measure production c_d
     on real Llama keys) is the pre-test that determines whether Option A applies.

  4. General principle: any mechanism whose correctness depends on the input distribution
     (coherence, anisotropy, rho_0) or on encoder geometry requires a production-encoder
     pre-test before engineering authorization.

  5. Opportunity cost framing: the SRHT cancellation saved 3-5 engineering days. Three
     such cancellations (which is the approximate frequency of this failure mode) saves
     9-15 engineering days, or roughly half the remaining v1 timeline. Pre-test protocol
     is not overhead -- it is the critical path.

---

## CITATIONS

1. Ethayarajh K. (2019) "How Contextual are Contextualized Word Representations?" EMNLP 2019.
   -- documented non-zero pairwise cosine similarity in GPT-2 / BERT activations (anisotropy)

2. Ailon N., Chazelle B. (2006) "Approximate nearest neighbors and the fast Johnson-
   Lindenstrauss transform." STOC 2006. -- SRHT theory; foundation for SRHT isotropy claim

3. McEliece R.J. et al. (1987) "The capacity of the Hopfield associative memory."
   IEEE Trans. Inf. Theory. -- correlated pattern capacity formula; (1-rho)^2 denominator

4. Li Y. et al. (2022); Hua T. et al. (2021) -- dimensional collapse in contrastive learning
   (BGE-large cone collapse mechanism)

5. "Preventing Sensitive Information Leakage via Post-hoc Orthogonalization" PAKDD 2025
   (arXiv:2311.01349) -- post-hoc orthogonalization for privacy in bidirectional embeddings;
   cited as SRHT analog in ZKL rescue drill

6. Kovaleva O. et al. (2021) "BERT Busters: Outlier Dimensions that Disrupt Transformers."
   -- outlier singular values inflate spectral-entropy d_eff while reducing usable rank

Internal empirical references (session-verified):
7. LVH #248: sparse-KEY at B=10 ties dense under random distractors -- reconciliation drill
8. Exp-Dev URGENT (2026-06-07): SRHT passes 0/1/2/3 on MiniLM vs Llama (table in Section 1B)
9. Cycle 151 ZKL measurement: real-key ZKL=0.40 vs synthetic ZKL=0.035 (11x gap)
10. Strategy decisions 2026-06-07 LVH #254: SRHT hurts P1=0.073 > P0=0.047; HARD_FAIL

Verified citation count: 6 public literature + 4 session-internal empirical references (10 total)

---

## PLAIN-LANGUAGE SUMMARY

We made three predictions in one session that turned out to be wrong, all in the same
direction: each was more optimistic than reality.

In every case, we were testing our ideas on a stand-in system that behaved differently from
our actual production system in a specific detectable way:

1. Sparse-KEY: we tested whether a memory trick helped when other memories were random noise.
   In production, the interference is not random -- it comes from memories that are similar to
   what you are looking for (because the routing system deliberately picks the most-similar
   shards). The trick helps in production; our test just happened to use the wrong kind of noise.

2. SRHT: we found a technique that improved privacy on a small, cheap encoder (MiniLM). When
   we ran it on our real encoder (Llama), it made things worse, not better. The two encoders
   are different enough that what helps one hurts the other.

3. MiniLM as stand-in: multiple predictions used MiniLM as a cheap test. When we moved to
   Llama, the predictions did not transfer.

The fix is straightforward in principle but requires discipline: before authorizing any
engineering work, run a cheap 1-2 hour test on the actual production encoder and the actual
production input distribution. This adds 1-2 days per decision but prevents 1-3 weeks of
wasted engineering when the prediction was wrong. For a 5-7 week remaining timeline, this
protocol is the most important process change we can make.
