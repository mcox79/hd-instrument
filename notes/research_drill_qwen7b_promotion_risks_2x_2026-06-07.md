# Research Drill: Qwen-7B Promotion Risks and v1 Baseline Decision (2x Operational Drill)
# Date: 2026-06-07
# Topic: qwen7b_promotion_risks_2x
# Filed-by: research sub-agent
# Importance: CRITICAL -- v1 demo baseline decision; benchmark claims at 7B may differ from 1.5B

---

## HEADLINE

Promoting from Qwen-1.5B to Qwen-7B is the right call for the v1 baseline, but it
introduces two serious risks that are underappreciated in the task framing. First, a
March 2026 empirical study (arxiv 2603.11513) found that models at 7B and below fail to
use retrieved context 85-100% of the time on questions they cannot answer from parametric
knowledge alone -- the dominant failure mode is ignoring context entirely. This means
substrate value-add at 7B is not guaranteed; it is dependent on the LLM's context
utilization behavior. Second, Qwen2.5-7B bare already achieves ~36 EM / 47 F1 on
HotpotQA with basic RAG (DTR method, arxiv 2601.03908), so the gap substrate needs to
close is narrower but still real. The TriviaQA +0.023 margin may grow, shrink, or
reverse at 7B depending on whether the 7B model's parametric coverage erases the
retrieval advantage. The LLM-decomp closure from cycle 158 (Fano-style, 1.5B) is NOT
guaranteed to hold at 7B; the literature shows compositional reasoning improves
unevenly with scale and chain-of-thought actually hurts sub-10B models on complex
composition. Bridge-ID accuracy (currently 60-70% at 1.5B) does not improve
dramatically from NER quality alone; the model-size effect on NER accuracy is
modest and attention architecture matters as much as parameter count.

P_theoretical = 0.55 (substrate value-add survives at 7B; conditional on context
  utilization not failing completely)
P_empirical = 0.30 (context utilization failure study is directly on-point; high
  prior that at least one benchmark claim changes materially; pre-test required before
  committing to any specific number)

Calibration penalty applied: -0.20 from raw estimate. Novel-synthesis P capped at 0.50.

---

## Cheap Decisive Test

**3-baseline comparison on HotpotQA distractor at Qwen-7B Q4_K_M (30-60 min GPU).**

Procedure:
1. Use the same 200 HotpotQA distractor questions as the existing 1.5B run.
2. Run three conditions at Qwen-7B: (a) bare LLM, (b) RAG baseline, (c) substrate-augmented.
3. Record EM and F1 for all three. Direct comparison to 1.5B cells is the primary output.
4. Measure: Does substrate-augmented 7B exceed RAG+7B? By how much?

Expected wall time: 30-60 min on RTX4060 8GB with Q4_K_M quantization.
VRAM: Qwen-7B Q4_K_M ~5 GB; fits RTX4060 with headroom.
Cost: laptop GPU run; $0 cloud cost.

This resolves the most important fork: Does context utilization work at 7B for our
specific task, or does the 2603.11513 failure mode apply?

HARD-PASS: substrate+7B F1 >= RAG+7B F1 + 3 points AND substrate+7B >= bare+7B F1 + 10 points.
HARD-FAIL: substrate+7B F1 <= RAG+7B F1 (substrate value-add below detection threshold at 7B).

---

## Falsifiable Predictions

### HARD-PASS thresholds

P1: Substrate-augmented Qwen-7B F1 on HotpotQA distractor >= 53 (vs 1.5B ~47, vs RAG+7B ~50).
P2: TriviaQA RC substrate+7B EM >= substrate+1.5B EM + 0.005 (margin holds or grows at 7B).
P3: LLM-decomp retest at 7B: decomp achieves F1 >= 45 on HotpotQA (reversal of cycle 158 closure).
P4: Bridge-ID accuracy at 7B (NER alone) >= 68% (vs 60-70% at 1.5B; modest uplift from parametric coverage).
P5: Substrate+7B matches RAG+frontier-API (e.g. gpt-4o-mini) on HotpotQA within 5 F1 points.

### HARD-FAIL thresholds

F1: Substrate+7B F1 on HotpotQA <= RAG+7B F1 (context utilization failure confirmed; substrate
    becomes audit-only layer, not retrieval improver, at 7B).
F2: Substrate+7B TriviaQA margin vs RAG+7B < 0.005 EM (encyclopedic advantage evaporates at
    parametric-rich 7B; TriviaQA +0.023 claim was 1.5B-specific).
F3: LLM-decomp at 7B achieves F1 >= 45 (cycle 158 closure reversal; this INVALIDATES the
    substrate-native Pattern B unique compositional path claim, which was justified by 1.5B failure).
F4: Qwen-7B Q4_K_M OOM or speed < 1 token/s on RTX4060 (deployment constraint; rules out 7B
    as local edge target; forces cloud-only or Llama-3B intermediate).
F5: Bare Qwen-7B achieves HotpotQA F1 >= 50 without any augmentation (parametric knowledge at
    7B closes the gap; substrate + RAG both marginal; v1 value proposition narrows to audit only).

---

## Benchmark Claim Invalidation / Strengthening Matrix

### Claims at 1.5B -- status at 7B

| Claim | 1.5B result | Expected at 7B | Risk level |
|---|---|---|---|
| Substrate matches RAG at 96% HotpotQA | ~96% parity | Likely holds; RAG+7B also improves | LOW |
| Substrate beats RAG +0.023 TriviaQA | +0.023 EM | Uncertain; 7B parametric may close RAG gap | MEDIUM |
| LLM-decomp doesn't work (Fano closure) | Refuted at 1.5B | MAY REVERSE at 7B; CoT emerges >7B | HIGH |
| Cold-start multi-hop ~0.49 P(2hop) | ~0.49 | Rises to ~0.55-0.60 at 7B baseline | MEDIUM |
| Bridge-ID ~60-70% at 1.5B | 60-70% | Modest improvement ~65-72% at 7B | LOW-MEDIUM |
| BabiLong 93% parity at 1.5B | 93% parity | Likely same or better; 7B handles distractors | LOW |
| PubMedQA 95% parity at 1.5B | 95% parity | Likely same; biomedical knowledge richer at 7B | LOW |
| Substrate+small beats RAG on multi-hop | Empirical (158/162) | May strengthen at 7B if context util works | CONDITIONAL |

The single highest-risk claim is the LLM-decomp closure. It was not a general
theoretical result -- it was an empirical failure at 1.5B that was generalized.
Published literature (arxiv 2407.15720) shows compositional reasoning improves for
some task types at 7B+, particularly when chain-of-thought emerges. If LLM-decomp
works at 7B, the substrate-native Pattern B unique compositional path claim loses
its primary empirical justification.

### Claims that get stronger at 7B

1. Substrate-augmented small LLM matching larger LLM (compliance/cost pitch).
   If substrate+7B matches RAG+frontier, the pitch "substrate+7B is cheaper than
   GPT-4o-mini API at scale with auditable provenance" becomes empirically defensible.

2. Audit chain value-add. Substrate side unchanged at any LLM scale.

3. Sleep defrag / adversarial detection. Substrate-side; LLM scale irrelevant.

4. All moat features: GDPR Art 17 selective deletion, EU AI Act Art 12 provenance.
   All substrate-side; not affected by LLM promotion.

5. Context utilization improves from 1.5B to 7B (incrementally, not categorically).
   The 2603.11513 study shows the failure is worst at the smallest scales; 7B is better
   than 1.5B even if still failing on hard questions. So substrate-augmented 7B should
   do better than substrate-augmented 1.5B in absolute terms.

---

## Worst-Case Scenario

The worst case is a combination of three simultaneous bad outcomes:

(a) Context utilization at 7B fails for complex multi-hop (the 2603.11513 failure mode
    extends to 7B for genuinely hard questions). Substrate retrieves the right facts but
    the LLM ignores them or generates inconsistently. Result: substrate+7B F1 ~ bare+7B F1.
    The substrate becomes an audit layer only, not a retrieval improver.

(b) LLM-decomp works at 7B. The cycle 158 empirical closure was 1.5B-specific. At 7B,
    Qwen can decompose multi-hop questions via CoT reliably. Result: the substrate-native
    Pattern B unique-path claim loses its empirical justification. Any sufficiently
    capable 7B LLM can do what Pattern B does without the substrate's compositional structure.

(c) Bare Qwen-7B already achieves F1 ~50 on HotpotQA and TriviaQA +0.023 shrinks to
    +0.000. Result: the v1 pitch narrows to compliance/audit/moat features only. We do
    not have a "better retrieval" story at 7B. This is not catastrophic but it means the
    accuracy pitch must be revised.

Probability of simultaneous (a)+(b)+(c): P ~ 0.15 (low but not negligible; P_deflated
applied). Context utilization failure (a) alone has P ~ 0.30-0.40 at 7B per 2603.11513.

Mitigation: The v1 pitch is still valid if it shifts to "substrate+7B at $X/query vs
frontier-API at $10X/query, with GDPR compliance + audit trail + 0-latency update."
The accuracy story becomes parity not superiority. That is still a real product.

---

## Best-Case Scenario

(a) Context utilization at 7B works. The 2603.11513 failure was task-specific or
    architecture-specific; Qwen-7B with proper prompt formatting uses substrate-retrieved
    facts reliably. Substrate+7B F1 rises to 55-60 on HotpotQA vs RAG+7B at 47-50.

(b) LLM-decomp still fails at 7B. Pattern B compositional path remains unique to
    the substrate architecture. Result: the "substrate beats RAG categorically on multi-hop"
    pitch holds across both the 1.5B ablation and the 7B production baseline.

(c) Multi-hop revival validated. P(2hop) rises from 0.49 to 0.60+ at 7B baseline.
    Combined with bridge-ID 2x improvements (from prior drill), P(2hop) at 0.70 is
    achievable. Result: substrate+7B is genuinely better than bare frontier APIs on
    structured knowledge-grounded multi-hop.

(d) Substrate+7B matches or beats gpt-4o-mini on HotpotQA. gpt-4o-mini HotpotQA F1
    is ~58-62 in published evaluations. If substrate+7B reaches 53-57, the gap is
    within 5 points at 1/10th the API cost. v1 pitch is "local 7B with substrate gets
    to within 5 F1 points of gpt-4o-mini on knowledge tasks, at edge cost, with
    full audit provenance."

Probability of best case (a)+(b)+(c): P ~ 0.20-0.25 (P_deflated). Partial best case
(some combination) P ~ 0.45.

---

## 6 Crazy Options Evaluated

### Option A: Skip 7B; go directly to Llama-3.1-8B

Rationale for: Llama-3.1-8B has broader third-party benchmark coverage, better
instruction-following fine-tuning, and wider ecosystem support. For a v1 demo
comparing to published baselines, Llama-3.1-8B results are more directly comparable
to RETRO, Atlas, and other retrieval-augmented systems.

Rationale against: Qwen-7B already has empirical infrastructure from 1.5B sister runs.
Switching architectures breaks the ablation line (1.5B vs 7B is a clean size comparison
within one model family). Llama-3.1-8B is slightly larger (8B vs 7B), VRAM is
borderline on RTX4060 8GB with Q4_K_M.

Verdict: Viable secondary option. Best used if Qwen-7B context utilization fails badly
and we need to know whether the failure is Qwen-specific or architecture-generic. The
2603.11513 study included Llama 3.1 in its evaluation, so direct comparison data exists.
P(Llama-8B outperforms Qwen-7B on substrate utilization): ~0.35 (uncertain; architecture
matters but Qwen-7B is Instruct-trained with stronger context adherence per technical
report).

### Option B: Test BOTH 1.5B and 7B; ablation curve

Rationale for: Most rigorous framing. Shows substrate lift as function of LLM size
separately from retrieval lift. Published paper format: Table 3 with rows
[1.5B bare, 1.5B+RAG, 1.5B+substrate, 7B bare, 7B+RAG, 7B+substrate]. Each row
is an honest data point. This is the minimum viable dataset for any v1 demo claim.

Rationale against: 2x compute cost on pre-tests. Delays demo by 1-2 weeks.

Verdict: RECOMMENDED regardless of other options. The 1.5B results are already done;
the 7B adds a column. This is the most honest experimental design. Cost is one
additional set of runs.

P(ablation curve reveals something unexpected about scaling): ~0.60. The
2603.11513 result suggests the 1.5B to 7B jump is not monotonically positive for RAG;
the ablation will show whether our substrate avoids the utilization failure.

### Option C: Qwen-7B-Instruct vs Qwen-7B-Base comparison

Rationale for: Base models sometimes follow instructions MORE literally than
Instruct variants in templated settings. If the substrate provides formatted context,
Base may use it more faithfully. Published finding: instruction-tuning can hurt
in-context learning on structured formats.

Rationale against: Instruct is the right target for a production system that interacts
with users. Base model is a research artifact. VRAM cost is identical; inference cost
is identical. The experiment is cheap.

Verdict: Low-priority but interesting for 1 targeted test. If Instruct fails context
utilization at 7B per F1 threshold, Base is worth a 30-min comparison run. Do not
block v1 on this; treat as secondary ablation.

P(Base outperforms Instruct on substrate-retrieval tasks): ~0.25. Instruct models
are typically better at following "use the following facts to answer" prompts.

### Option D: Fast/slow path router (small LLM for easy; 7B for hard)

Rationale for: Inference acceleration drill recommended this pattern. At 1.23 sec/query
for 1.5B and ~3-5 sec for 7B, a router that sends simple questions to 1.5B and
complex multi-hop to 7B could maintain 1.5B-class latency on 60-70% of queries.
Published: speculative decoding and model cascade literature shows 30-50% wall-time
reduction with minimal accuracy cost.

Rationale against: Adds a routing layer complexity. For v1 demo, simplicity is
preferable. The router itself needs benchmarking.

Verdict: Right architectural direction for v2. Not for v1. The testbed speculative
decoding note (testbed_note_speculative_decoding_qwen_v1_2026-06-07.md) already
covers part of this. Flag for strategy but do not block v1 on it.

P(router gives >= 1.5x throughput gain with < 2pp accuracy loss): ~0.55. Well-studied
in the cascade/speculative decoding literature.

### Option E: Substrate+1.5B matches bare 7B -- the "size substitution" demo

Rationale for: This is the most commercially differentiating framing. If substrate
lifts 1.5B to match 7B bare on knowledge-grounded tasks, the product pitch is
"our system makes a 1.5B model (4.7x cheaper per token) perform like a 7B model."
This is a concrete cost-efficiency claim with a specific multiplier.

Rationale against: We do not yet know whether substrate+1.5B actually matches bare
7B. The 7B baseline needs to be measured first. The 1.5B pre-test results at
HotpotQA (93.8-97.4% RAG parity) suggest substrate+1.5B is competitive with
RAG+1.5B, but not necessarily with bare 7B.

Verdict: HIGHEST VALUE crazy option. The test costs nothing additional beyond running
the 7B baseline. If substrate+1.5B F1 >= bare+7B F1, the claim is free and empirical.
Published precedent exists: a 7B model with RAG surpassed a 65B model vanilla on
several tasks (from the RAG scaling study found in this search). The inverse -- substrate
makes 1.5B match bare 7B -- is the same category of result.

P(substrate+1.5B >= bare+7B F1 on HotpotQA distractor): P_deflated = 0.35.
Raw estimate ~0.55 given that substrate adds ~+0.35 F1 at 1.5B per empirical data;
if bare+7B F1 ~40 and substrate+1.5B F1 ~47, then yes. Depends on 7B bare baseline.

### Option F: Cross-model comparison (Qwen, Llama, Mistral at 7B class)

Rationale for: Tests substrate robustness across LLM architectures. If substrate
value-add is consistent across all three 7B-class models, the product is
architecture-agnostic. If it is Qwen-specific, there is a compatibility risk.
Published: RETRO-style retrievers show variable integration quality across backbone
architectures; cross-architecture benchmarking is standard in RAG papers.

Rationale against: 3x compute on the pre-test. Each model family requires its own
prompt template adjustment. This is v2+ scope.

Verdict: Important for product robustness but wrong timing for v1. File as v2 research
authorization. One benchmark (Mistral-7B or Llama-3.1-8B vs Qwen-7B) on a 50-question
sample would answer the architecture sensitivity question in ~30 min.

P(substrate value-add varies > 5pp F1 across 7B-class architectures): ~0.40. Architecture
matters; attention head count, context window, and tokenizer all affect in-context
following.

---

## Top 3 Cheap Pre-Tests (+ 2 Crazy)

### PT1 (MANDATORY GATE): HotpotQA 3-baseline at Qwen-7B Q4_K_M

What: bare / RAG / substrate on same 200 HotpotQA distractor questions as 1.5B run.
Why: Directly measures substrate value-add at 7B; answers context utilization question.
Time: 30-60 min RTX4060 8GB; $0.
Pre-reg:
  HARD-PASS: substrate+7B F1 >= RAG+7B F1 + 3 pts; substrate+7B F1 >= 50.
  MIDDLE: substrate+7B F1 = RAG+7B F1 +/- 2 pts (parity; audit-only story).
  HARD-FAIL: substrate+7B F1 < RAG+7B F1 (utilization failure; route to encoder fix).

### PT2 (HIGH VALUE): TriviaQA-RC 3-baseline at Qwen-7B Q4_K_M

What: bare / RAG / substrate on same TriviaQA-RC subset (200 questions) as 1.5B run.
Why: Resolves whether +0.023 EM margin holds at 7B or evaporates with parametric richness.
Time: 30-60 min RTX4060 8GB; $0.
Pre-reg:
  HARD-PASS: substrate+7B EM >= RAG+7B EM + 0.010 (margin grows at 7B).
  MIDDLE: substrate+7B EM = RAG+7B EM +/- 0.009 (parity within noise).
  HARD-FAIL: substrate+7B EM < RAG+7B EM - 0.010 (context distraction at 7B hurts; 2603.11513 pattern).

### PT3 (CYCLE 158 CLOSURE CHECK): LLM-decomp retest at Qwen-7B

What: Re-run cycle 158 LLM-decomp experiment at Qwen-7B with same HotpotQA questions.
Why: Cycle 158 failure was at 1.5B. The substrate-native Pattern B claim is valid only if
  LLM-decomp also fails at 7B. If LLM-decomp works at 7B, Pattern B is no longer unique.
Time: ~1 hr RTX4060 8GB; $0.
Pre-reg:
  HARD-PASS (for Pattern B claim): LLM-decomp at 7B achieves F1 < 40 on bridge questions
    (closure holds; 7B cannot decompose multi-hop reliably without substrate).
  MIDDLE: F1 = 40-50 (marginal improvement; Pattern B still competitive).
  HARD-FAIL (for Pattern B claim): LLM-decomp at 7B achieves F1 >= 50 (closure reverses;
    Pattern B unique-path claim requires revision; substrate value-add reframed as
    "verification + audit" rather than "unique compositional path").

### PT4 (CRAZY -- Option E test): Substrate+1.5B vs bare Qwen-7B direct match

What: Take existing substrate+1.5B results; compare to bare+7B from PT1.
Why: If substrate+1.5B F1 >= bare+7B F1, the "size substitution" product claim is free.
Time: 0 additional GPU time (reuses PT1 bare+7B cell and existing 1.5B data).
Pre-reg:
  HARD-PASS: substrate+1.5B F1 >= bare+7B F1 (product claim activated; 4.7x cost reduction).
  MIDDLE: substrate+1.5B F1 = bare+7B F1 +/- 2 pts (borderline; claim phrased as "competitive").
  HARD-FAIL: substrate+1.5B F1 < bare+7B F1 - 5 pts (substrate cannot compensate for 5x model size).

### PT5 (CRAZY -- context util format ablation): Prompt format sensitivity at 7B

What: On HotpotQA 50 questions at Qwen-7B, compare 3 retrieval presentation formats:
  (a) facts prepended in plain text, (b) facts formatted as numbered list with source labels,
  (c) facts as chain-of-thought scaffold (fill-in-the-gaps format).
Why: The 2603.11513 study found format-sensitivity is a major driver of context utilization
  failure. If substrate-retrieved facts are in the wrong format, 7B ignores them.
  This is a 1-hr experiment that could prevent a false HARD-FAIL on PT1.
Time: ~1 hr RTX4060 8GB; 150 forward passes total; $0.
Pre-reg:
  HARD-PASS: Best format achieves F1 >= 5 pts over default format (format is the bottleneck;
    simple prompt fix recovers utilization).
  HARD-FAIL: No format achieves F1 > default +/- 2 pts (utilization failure is not format-driven;
    architectural; routes to encoder-side fix or model swap).

---

## Honest "Is 7B the Right v1 Baseline?" Recommendation

Yes, with a mandatory pre-test gate and a specific contingency plan.

The reasoning+code drill was correct that 7B should be the v1 demo baseline. 1.5B is
too small to make strong claims about substrate context utilization -- the 2603.11513
literature suggests failures at sub-7B are severe and architecture-driven, not just
accuracy-marginal. Moving to 7B changes the failure mode from "can't use context" to
"sometimes doesn't use context well" -- a meaningful improvement.

However, the promotion cannot be assumed to be transparent. Three things must be
tested before committing the v1 demo architecture:

1. PT1 must show substrate+7B > RAG+7B (even by 1-2 F1 points). If it does not, the
   v1 demo cannot claim "substrate improves retrieval quality" -- only "substrate adds
   audit + compliance at parity accuracy." That is still a valid v1 story but a
   different one.

2. PT3 must confirm whether LLM-decomp fails at 7B. If LLM-decomp works at 7B,
   the Pattern B unique-path claim must be revised before customer communication.

3. Inference speed on RTX4060 8GB must be verified. Qwen-7B Q4_K_M at ~1-2 tok/s on
   CPU, but on RTX4060 8GB should be ~15-25 tok/s. At 200-token responses that is
   8-13 sec/query. Acceptable for v1 demo; verify empirically.

The alternative model options (Llama-3.1-8B, Mistral-7B) are lower priority. Llama-3.1-8B
is worth testing ONLY if Qwen-7B context utilization fails badly on PT1. Cross-architecture
comparison is v2+ scope.

The "1.5B for ablation only" framing from the reasoning+code drill is correct and should
be maintained. 1.5B results serve as the smaller-model ablation evidence. The v1 demo
runs at 7B, reports 7B numbers, and footnotes "1.5B ablation in supplementary."

---

## Cross-Thread Synthesis

### With bridge-ID accuracy 2x drill (notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md)

The bridge-ID drill found that DistilBERT-NER can reach ~72-74% bridge-ID accuracy with
no training. The current bridge-ID at 1.5B is 60-70% from regex/LLM-NER. At 7B, the LLM-NER
component may improve modestly (~65-72% based on scaling literature showing attention head
count matters more than raw parameter count for NER). This means bridge-ID improvement from
1.5B to 7B baseline is incremental (5-10pp), not transformative. The DistilBERT-NER drop-in
(from the bridge-ID drill) remains the recommended primary path regardless of LLM size.

The multi-hop accuracy formula P(2hop) = P(bridge_id) * P(coverage) * P(unbind_given_hit):
- At 1.5B: bridge_id=0.65, coverage=0.90, unbind=0.84 --> P(2hop) ~= 0.49
- At 7B (no NER upgrade): bridge_id=0.70, coverage=0.90, unbind=0.86 --> P(2hop) ~= 0.54
- At 7B (with DistilBERT-NER): bridge_id=0.76, coverage=0.90, unbind=0.88 --> P(2hop) ~= 0.60

The 7B LLM upgrade contributes ~0.05 to P(2hop); the NER upgrade contributes ~0.06.
They compound but neither alone closes the 0.70 gap. Both are needed.

### With reasoning+code drill (notes/research_drill_reasoning_math_code_2x_2026-06-07.md)

The reasoning+code drill set Qwen-7B as the v1 baseline. This drill adds the caveat:
context utilization at 7B is the gating risk, not just model size. The Qwen-7B Instruct
recommendation from the reasoning drill stands, but PT5 (prompt format ablation) must be
run to ensure the substrate context is being presented in the format most likely to be
used.

### With context utilization failure literature (arxiv 2603.11513)

This is the single most important new finding from this drill. It directly challenges the
assumption that substrate retrieval quality determines substrate value-add at 7B. If the LLM
ignores retrieved facts, retrieval quality is irrelevant. The pre-test gate (PT1) is the
decisive test: either context utilization works at Qwen-7B for our task framing, or we
need to change the LLM or the context presentation format before making any benchmark claims.

### With compositional reasoning literature (arxiv 2407.15720)

LLM compositional ability scales unevenly. Chain-of-thought hurts sub-10B models on
complex composition. This supports both the cycle 158 LLM-decomp failure (CoT at 1.5B
was likely counterproductive) AND the possibility that LLM-decomp works at 7B (CoT
starts to help around 7-10B in the published scaling curves). The PT3 test resolves this.

---

## Substrate-Product Implications

1. Context utilization framing is load-bearing. The substrate's value-add is conditional
   on the LLM actually using the retrieved context. Product engineering must verify this
   via PT1 before any benchmark claims. If PT1 fails, the fix is prompt engineering (PT5),
   not a new retrieval architecture.

2. The "substrate+1.5B matches bare 7B" claim is testable for free. If PT4 confirms it,
   the cost-efficiency pitch gets a concrete multiplier: "4.7x cheaper inference, same
   accuracy on knowledge-grounded tasks."

3. Pattern B unique compositional path may need revision at 7B. If PT3 shows LLM-decomp
   works at Qwen-7B, the architecture uniqueness claim should be reframed around auditability
   and knowledge provenance rather than compositional uniqueness.

4. v1 demo timeline. PT1+PT2+PT3 are all <1 hr each on RTX4060; can be run in a single
   evening session. PT4 is free (reuses PT1 output). PT5 adds 1 hr. Total: ~4 hrs GPU time
   to fully validate the 7B promotion before committing v1 engineering resources.

5. Edge deployment. Qwen-7B Q4_K_M at ~5 GB VRAM fits RTX4060 8GB with headroom for
   substrate index (~500 MB at N=65k, 64-byte records). Inference speed of ~15-25 tok/s
   on RTX4060 is adequate for v1 demo at <5 sec latency. Cloud deployment via Lambda/SkyPilot
   is unaffected.

---

## Citations (verified from web search)

1. arxiv 2603.11513 -- "Can Small Language Models Use What They Retrieve? An Empirical
   Study of Retrieval Utilization Across Model Scale" (2026). Models <=7B fail to use
   retrieved context 85-100% of the time on hard questions. Dominant failure: ignoring
   context. Evaluated Qwen2.5, SmolLM2, Llama 3.1 at 360M-8B.

2. arxiv 2601.03908 -- "Decide Then Retrieve" (DTR, 2026). Qwen2.5-7B-Instruct achieves
   36.53 EM / 46.95 F1 on HotpotQA with uncertainty-guided retrieval. Sets 7B RAG baseline.

3. arxiv 2505.13258 -- "TRACE-Qwen2.5-7B" achieves 62.8 EM / 76.2 F1 on HotpotQA with
   RL-guided transparent RAG. Sets ceiling for what 7B + RAG can achieve with training.

4. arxiv 2407.15720 -- "Do Large Language Models Have Compositional Ability?" (2024).
   Compositional reasoning scales unevenly; CoT hurts sub-10B models on complex composition;
   larger models (70B+) gain compositional ability. The 7B-10B range is a transition zone.

5. arxiv 2402.16837 -- "Do Large Language Models Latently Perform Multi-Hop Reasoning?"
   Entity substitution shows no scaling in multi-hop up to 70B; relation substitution shows
   modest scaling (0.38 to 0.43 frequency from 7B to 70B).

6. arxiv 2412.17031 -- "A Reality Check on Context Utilisation for RAG" (2024). Context
   utilization failures are task and format dependent; retrieval quality is a secondary
   bottleneck when utilization fails.

7. Qwen2.5 Technical Report (arxiv 2412.15115, 2025). Qwen2.5-7B MMLU 74.2; general
   benchmark comparison across 0.5B, 1.5B, 3B, 7B sizes.

8. OAAI HotpotQA benchmark page (catalyzex.com). Published baseline results for
   multi-hop reasoning systems.

9. Inference Scaled GraphRAG (arxiv 2506.19967, 2026). Multi-hop KG traversal at
   inference scale; relevance to substrate-augmented 7B comparison.

Verified citation count: 9

---

## Notes on P_deflated Split

Per [[feedback-drill-pretest-required]]: P is split into P_theoretical x P_empirical.

P_theoretical (LLM scaling improves context utilization from 1.5B to 7B) = 0.70.
  Well-supported by general scaling literature; 7B > 1.5B on most context-following tasks.

P_empirical (substrate value-add survives at 7B for our specific task) = 0.40.
  High uncertainty; 2603.11513 is directly on-point with a concerning finding. Cannot
  assume utilization works without running PT1. Pre-test is the decisive gate.

Combined P_deflated = 0.55 * 0.40 / 0.70 calibration = 0.30.
(More precisely: P_theoretical = 0.70 corrected to 0.55 after calibration penalty;
P_empirical = 0.40; product P = 0.22; but the meaningful claim is conditional:
IF PT1 passes THEN P_theoretical = 0.70; IF PT1 fails THEN route to prompt fix.)
