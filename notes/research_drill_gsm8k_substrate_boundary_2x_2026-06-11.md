# Research drill: GSM8K substrate honest boundary (2x DEEP)

Date: 2026-06-11
Trigger: Strategy 2x DEEP drill on substrate honest boundary for GSM8K multi-step linguistic math
Discipline: lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis P capped at 0.50); generic terms only off-platform
Prior context (do-not-search inputs): substrate Tier A on MAWPS (2-op family) + MultiArith (2-op composition); GSM8K ceiling probe shows 1-op recall ~0.16, 2-op recall ~0.39; 2-op cannot reach >0.30 on 3-8 op problems

## (a) HEADLINE

GSM8K's substrate-only ceiling at current 2-op composition is honest but NOT a structural limit. The dominant error class on GSM8K across the literature is arithmetic execution (~45%), not problem comprehension (~35%); substrate already has clean execution at single-step level, and a tree-structured recursive composition layer with intermediate-result cleanup is the load-bearing missing primitive. Three untested substrate-only paths (recursive-binding scratch-pad, goal-driven tree decomposition GTS-on-substrate, step-wise verifier composition) plus one hybrid (substrate-extraction + LLM-CoT) are pre-registered for cheap CPU smoke. Headline empirical bet: substrate-only 3-op composition + recursive cleanup reaches GSM8K easy-tier (<3 op subset ~33% of test set) at >=0.45; 3-8 op subset stays substrate-cap-bound until tree decomposition is added.

P_deflated estimates:
- 3-op composition extension reaches >=0.40 on easy-tier subset: 0.55 (theory 0.70, empirical penalty -0.15)
- Tree-structured GTS-style decomposition on substrate reaches >=0.50 overall: 0.40 (novel synthesis, capped)
- Step-wise substrate verifier lifts any base path by >=0.10: 0.50 (verifier-lift effect well-documented in lit)
- Substrate-only beats LLM-CoT at 1B-equivalent size on GSM8K full: 0.20 (HARD-FAIL band; honest)
- Hybrid (substrate-extraction + LLM-CoT) viable as v1 demo path: 0.65 (bypasses NL-parse gap)

## (b) Cheap decisive test (pre-registered)

Test bundle CPU-only, target ~4-8 hours wall time:

### Test 1: 3-op composition extension on substrate (CPU, ~1 hr)
- Take MultiArith 2-op winning recipe; extend the bind-chain to 3 atoms (arg1 binding, arg2 binding, op binding) at depth 3.
- Eval on synthetic 3-op problems (template: "Alice has X. She buys Y more. Then she gives Z away. How many?") n=200.
- Cleanup: per-depth Kronecker-rotation product (per arxiv 2506.15793 linearithmic cleanup, substrate-implementable).
- HARD-PASS: substrate-only 3-op recall >= 0.65 on synthetic template (close to MultiArith 0.753).
- HARD-FAIL: substrate-only 3-op recall < 0.40 (composition cliff at depth-3 = real structural limit).

### Test 2: GSM8K easy-tier (<3 op) substrate-only smoke (CPU, ~2 hr)
- Filter GSM8K test split to <3-op subset (~33% per literature; ~440 problems).
- Substrate-only pipeline: (a) extract quantities via substrate-classical method (count-window emission per substrate-classical NLP finding 2026-06-11), (b) extract op via substrate verb-cue lookup, (c) compose via 2-op substrate primitive, (d) decode via cleanup.
- HARD-PASS: >= 0.45 on easy-tier subset.
- HARD-FAIL: < 0.20 (extraction layer itself is broken; not just composition).

### Test 3: Step-wise substrate verifier on 2-op chain (CPU, ~1 hr)
- After each binding step, verify intermediate-result hypervector against cleanup-memory; if cosine < threshold, re-bind with attentional sharpening.
- Eval on MultiArith subset where 2-op currently fails.
- HARD-PASS: lift >= 0.10 absolute over no-verifier baseline (verifier is real, not noise).
- HARD-FAIL: lift <= 2 * SE (verifier adds noise-level only; method-overclaim per [[feedback-method-overclaim-lift-validation]]).

### Test 4 (medium effort, ~3-4 hr): substrate goal-driven tree decomposition (GTS-on-substrate prototype)
- Implement substrate analog of Xie-Sun GTS (IJCAI 2019, 70% on Math23K): goal vector decomposed into (left-sub-goal x op x right-sub-goal) recursively via binding tree.
- Eval on 30 GSM8K medium-tier (=3 op) problems with hand-extracted quantity sets (isolates composition from NL parse).
- HARD-PASS: >= 0.30 on this controlled subset (composition layer works without NL bottleneck).
- HARD-FAIL: < 0.10 (tree decomposition does not transfer to substrate).

### Test 5 (hybrid path, ~2 hr): substrate-extraction + GPT-class-CoT recombination
- Substrate extracts (quantity, attribute, role) tuples from NL; LLM consumes structured tuples + does CoT for arithmetic.
- Eval on GSM8K full test (subset n=200).
- HARD-PASS: hybrid >= LLM-only baseline + 5pp (substrate-extraction adds genuine value as front-end).
- HARD-FAIL: hybrid <= LLM-only baseline (substrate-extraction is redundant given LLM already parses).

## (c) Falsifiable predictions

P1 (P_deflated 0.55, HARD-PASS 0.45 / HARD-FAIL 0.20): Substrate 3-op extension hits MultiArith-like recall on synthetic 3-op templates, demonstrating that the 2-op cliff is NOT depth-1 structural but depth-3 reachable with per-level cleanup.

P2 (P_deflated 0.40, HARD-PASS 0.30 / HARD-FAIL 0.10): Goal-driven tree decomposition (GTS-on-substrate) on GSM8K medium-tier with hand-extracted quantities reaches >= 0.30 — composition layer is not the dominant blocker once extraction is given.

P3 (P_deflated 0.50, HARD-PASS lift>=0.10 / HARD-FAIL lift<=2*SE): Step-wise substrate verifier (cleanup-cosine threshold + re-binding) lifts 2-op composition recall on MultiArith failed cases.

P4 (P_deflated 0.65, HARD-PASS hybrid_acc - LLM_acc >= 0.05 / HARD-FAIL hybrid_acc <= LLM_acc): Hybrid (substrate-extraction front-end + LLM-CoT back-end) is the honest v1 demo path; substrate adds value as extraction layer even when LLM does arithmetic CoT.

P5 (HARD-FAIL prediction, P_deflated 0.20 against): substrate-only WILL NOT beat LLM-CoT at 1B size on GSM8K-full in 4-week horizon. Honest boundary: substrate complements, does not replace, LLM-CoT on 3-8 op GSM8K. (This is the drill-defeatism-rule-compliant version: not "structural impossibility" but "not reachable in this product cycle").

## (d) Cross-thread synthesis with prior entries

Cross-thread 1: substrate-classical NLP methods outperform phasor (2026-06-11 memory entry). The 0.906 substrate-only POS tagger + 0.871 slot-filler are exactly the extraction primitives that Test 2 and Test 5 depend on. Quantity-extraction = slot-filling specialized to numerical/quantity slots; the path is structurally proven to substrate's strength.

Cross-thread 2: substrate-LLM boundary decomposition (2026-06-10). The decomposition says LLM-only owns "parsing arbitrary English + statistical fluency"; substrate owns "symbolic + structural + systematic." GSM8K word problems hit BOTH (English parse PLUS structural arithmetic). The hybrid path (Test 5) is the honest decomposition reading: substrate does structural, LLM does English-parse. Substrate-only Test 4 (tree decomposition with hand-extracted quantities) isolates the structural side.

Cross-thread 3: drill pattern TEMPORAL+CONTEXTUAL works FIXED-ARCHITECTURE fails (2026-06-11). GTS-on-substrate is a temporally-recursive context-binding architecture (each sub-goal is a contextual binding within parent goal), NOT a fixed topological structure. The drill-pattern memory entry PREDICTS Test 4 is in the working-class of architectures. P_deflated 0.40 reflects calibration but the architectural form is favorable.

Cross-thread 4: substrate v3.0 compositional cliff (2026-06-10). L5 recall 0.000 -> 1.000 via per-level cascading cleanup. This is the SAME mechanism Test 1 invokes. 30-year VSA cliff was crossed for depth-5 in compositional recall; transferring this technique to arithmetic composition is high-confidence the cleanup will transfer (the underlying problem is identical: recover atoms from compositional hypervector at depth >= 3).

Cross-thread 5: recursive binding for sequences (arxiv 2201.11691) + HyPE error propagation (arxiv 2024) + linearithmic Kronecker cleanup (arxiv 2506.15793). External lit has shipped exactly the primitives needed for substrate scratch-pad. Implementing on substrate is engineering, not novel synthesis.

Adversarial cross-thread: PP-225 fact-scaling correction (2026-06-10). The illusory-scaling pattern means we MUST instrument Test 1's 3-op pool with genuine-vs-padded distinguishing; if 3-op composition only "works" because the same 3 atoms are reused, that is the DISC_POOL trap. Pre-reg: each 3-op test problem MUST draw 3 distinct atoms from a pool of >= 200 quantity atoms.

## (e) Substrate-product implications

Product reading 1: GSM8K is NOT the substrate's product showcase. The benchmark is dominated by arithmetic execution (45% error class) which is exactly where LLM-CoT excels and substrate is neutral. Pushing substrate-only on full GSM8K is product-strategically misallocated. Honest v1 demo positioning: GSM8K is a DIAGNOSTIC for the substrate-as-extraction-layer claim, not a head-to-head benchmark.

Product reading 2: substrate-extraction + LLM-CoT hybrid (Test 5) IS the v1 demo path. North-star "functional system beats LLMs" applies at the SYSTEM level: substrate-extraction front-end gives auditability, verifiability, edit-ability (memory writes are addressable; LLM weights are not) — the substrate's structural advantages — while LLM-CoT does the arithmetic execution it is good at. This is the honest product story for math reasoning.

Product reading 3: tree-structured composition (Test 4) is the substrate-internal capability that matters for cross-domain reasoning broadly, not just GSM8K. If P2 hits (>= 0.30 on medium-tier controlled), the same primitive transfers to multi-hop QA, plan composition, code-function-tree composition. GSM8K is a probe, the capability is the asset.

Product reading 4: step-wise verifier (Test 3) is a substrate-native auditability story. Each intermediate hypervector is addressable + verifiable against cleanup memory — this is structurally what LLMs cannot do (intermediate activations are not addressable). If P3 hits with lift >= 0.10, it is a substrate-axis product differentiator (verifier-as-feature, not just accuracy lift).

Product reading 5 (HONEST PASS): if all 5 tests partially-pass, the substrate v1 demo for math reasoning is positioned as: "substrate provides verifiable, editable arithmetic extraction + composition layer; pairs with LLM-CoT for full coverage on multi-step problems." This is the architecturally hybrid story refined to a product narrative, NOT the substrate-replaces-LLM overclaim.

## (f) Untested substrate-only paths inventory (per drill-defeatism rule)

Per the drill-defeatism memory entry (2026-06-11), no boundary claim accepted without exhausting path inventory. Five paths still untested empirically before any structural-closure framing:

Path 1: 3-op composition extension with per-depth cleanup (Test 1). UNTESTED at scale; substrate v3.0 cliff-crossing technique transfers in principle.

Path 2: Goal-driven tree decomposition on substrate (Test 4, GTS-analog). UNTESTED; literature precedent at IJCAI 2019 achieved 70% on Math23K with this exact architectural pattern in neural setting; substrate analog never empirically attempted.

Path 3: Step-wise verifier composition (Test 3). UNTESTED; lit precedent (Tree-PLV, T1) shows verifier-lift effect is large (15pp on Mistral-7B); substrate's natural addressability makes the analog cheap.

Path 4: Substrate-native scratch-pad as intermediate-atom storage. UNTESTED as a full path; relies on recursive binding for sequences (arxiv 2201.11691) which substrate has not yet operationalized for arithmetic. Each intermediate result stored as a substrate atom with position-binding + cleanup-on-recall.

Path 5: Substrate-classical extraction + symbolic equation solver (no LLM). Substrate extracts (quantity, attribute, role) tuples; symbolic Z3 / sympy solves the system. UNTESTED on GSM8K but the extraction precondition was validated 2026-06-11 (slot-filling 0.871). This is the fully-symbolic substrate-only path: no neural arithmetic at all, just extraction + classical equation solver.

Per the rule: none of these can be excluded without empirical refutation. Test 1-4 sample 4 of the 5; Path 5 (Z3 / sympy back-end) is added as P_deflated 0.35 cheap follow-up if Tests 1-4 illuminate the extraction quality.

## (g) Honest comparison to LLM-CoT

LLM-CoT wins on GSM8K because:
- It absorbs the 45% arithmetic-execution error class via large-scale token-level optimization (LLMs internalize arithmetic patterns at scale).
- It absorbs the natural-language variability (idiomatic phrasing, distractor sentences, cultural names per the July 2025 study showing template-shift degrades CoT 10-20pp).
- It scales generation + verifier compute at inference time (self-consistency + best-of-N).

Substrate-only is structurally weaker on GSM8K because:
- Arithmetic execution at 3-8 step depth requires cleanup memory that scales with composition depth; literature linearithmic cleanup helps but is not zero-cost.
- Natural-language variability has to be absorbed via the extraction layer; substrate-classical extraction is at 0.87 (one error per 8 problems), and errors compound across 3-8 step problems.

Substrate-only is structurally STRONGER on:
- Auditability: every binding addressable, every intermediate-result verifiable. LLMs cannot do this.
- Editability: facts and operators are memory atoms; edit a quantity, recompose. LLMs require fine-tuning.
- Composition correctness guarantees: cleanup at each step gives provable atom-recovery (vs. LLM hallucination).

Honest read: GSM8K is the WRONG benchmark for substrate-axis advantage. The substrate-axis advantages don't show up on a single-shot accuracy benchmark; they show up on iterative/auditable/editable reasoning tasks. GSM8K is included in the test suite as a NL-math composition diagnostic, not a product hero benchmark.

## (h) Citations (verified count: 12)

External lit verified via WebSearch 2026-06-11:
1. arxiv 2201.11903 — Wei et al. Chain-of-Thought Prompting. (GSM8K CoT baseline)
2. arxiv 2404.14963 — Achieving >97% on GSM8K with deep problem understanding. (97.4% upper bound; arithmetic-execution dominance)
3. arxiv 2402.02658 — Multi-step problem solving through verifier (Liang et al. 2024). (verifier-lift 15pp)
4. arxiv 2206.02336 — Step-aware verifier. (intermediate verification framework)
5. arxiv 2312.09241 — TinyGSM 1.3B 81.5%. (small-model GSM8K via synthetic decomposition data)
6. arxiv 2409.12393 — Small language models are equation reasoners. (equation-extraction front-end)
7. arxiv 2106.05268 — VSA as computing framework. (binding + superposition + cleanup primitives)
8. arxiv 2301.10352 — Capacity analysis of VSA. (composition-depth ceiling theory)
9. arxiv 2506.15793 — Linearithmic cleanup with Kronecker rotation products. (substrate-implementable cleanup)
10. arxiv 2201.11691 — Recursive binding for similarity-preserving sequences. (substrate scratch-pad primitive)
11. IJCAI 2019 — Xie & Sun GTS goal-driven tree-structured neural model. (70% on Math23K)
12. ScienceDirect 2023 — Recursive tree-structured neural network for math word problems. (goal forgetting + information aggregation)

Cognitive science cross-refs (3):
- PMC 8558208 — Working memory demands in simple vs complex arithmetic word problems.
- ScienceDirect S0022096511001585 — Working memory components as predictors of children's word problem solving.
- Frontiers psyg 2019.00148 — Working memory, strategy use, and multi-step mental addition.

## (i) Next-drill candidate

If Tests 1-3 pass: drill 3x DEEP on substrate-native scratch-pad implementation (Path 4) — operational details of position-binding for intermediate results, depth-dependent cleanup scheduling, when to write-then-clear.

If Tests 1-3 fail: drill 3x DEEP on substrate-extraction + Z3 path (Path 5) — fully symbolic back-end, fully substrate front-end, no neural arithmetic at all. This is the most cleanly substrate-axis path and the one most likely to give a defensible v1 demo if the compositional-substrate path saturates.

If Test 5 (hybrid) is the strongest: pivot research priorities to substrate-extraction-layer hardening (slot-filling at scale, multi-quantity ambiguity resolution, distractor robustness) — these are the load-bearing pieces for the v1 demo hybrid story.

End of note.
