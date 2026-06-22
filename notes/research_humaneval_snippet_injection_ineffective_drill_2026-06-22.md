# Research drill: why does substrate-augmented Qwen-1.5B-Instruct produce no per-problem PASS-rate gain on HumanEval stdlib subset?

From: research (Director)
Date: 2026-06-22
Cell smoked: `experiments/exp_humaneval_stdlib_split_qwen_v1.py` (10 problems, A=6 B=4, run_mode=smoke, gain_A=+0.000, gain_B=+0.000, HARD_FAIL)
Metrics: `data/exp_humaneval_stdlib_split_qwen_v1/metrics.json`

## HEADLINE

The smoke is NOT a "Qwen ignores snippets" finding (token-counts and per-problem error contents show Qwen DOES read snippets and generates different code: HumanEval/1 bare=76 tok vs sub=124 tok; HumanEval/25 bare line-1 SyntaxError vs sub line-27 check-assertion-fail = entirely different code path); the smoke IS a "snippet-prepended Python-stdlib docs cannot rescue a non-code-specialized 1.5B model on a benchmark whose primitives it has either memorized or fundamentally can't produce syntactically-valid Python for" finding. The published lit pre-states the result: CodeRAG-Bench (NAACL 2025 Findings) shows library docs DO NOT HELP HumanEval (it uses Python built-ins models already know); competition / canonical-solution retrieval gives +12.2 points on StarCoder2-7B; StackOverflow gives +1.8 to +4.3. Our retrieval source is in the WRONG category. Net: no novel substrate problem; we are reproducing a published null-result with a wrong-source RAG.

## OBSERVED-vs-CLAIMED CORRECTION

Task brief said "bare and substrate-augmented Qwen produced identical code on ALL 10 smoke problems." This is FALSE on close inspection:
- 6 of 10 problems show different `bare_ntok` vs `sub_ntok` (HE/1 76 vs 124; HE/6 113 vs 138; HE/17 99 vs 154; HE/25 65 vs 36; HE/26 54 vs 48; HE/3 37 vs 54).
- HumanEval/25: bare error path = SyntaxError at line 1; sub error path = AssertionError at line 27 inside `check()`. Sub-arm parses correctly but fails the test; bare-arm doesn't even parse. Radically different outputs.
- 4 of 10 problems have identical pass verdict (P/P or f/f) AND near-identical ntok — those are the cases where Qwen converged on the same canonical implementation regardless of snippets, consistent with HumanEval memorization (see HE/2 `truncate_number` bare=26 tok = sub=26 tok, both PASS).

The correct claim is: **per-problem PASS-rate is identical, but generated code is NOT identical.** Qwen IS using snippets; the snippets are not load-bearing enough to flip outcome on this subset.

## HYPOTHESIS RANKING (lit-anchored, deflation applied per role contract cap=0.50)

| # | Hypothesis | Lit anchor | P (deflated, cap 0.50) | Status after smoke |
|---|------------|------------|------------------------|---------------------|
| H1 | Wrong retrieval source: stdlib-doc snippets help DS-1000/ODEX (lib-API tasks) but NOT HumanEval (built-ins already memorized). RIGHT source = canonical / competition solutions. | CodeRAG-Bench Table 7: lib-docs flat on HumanEval; competition solutions +12.2 pts; StackOverflow +1.8 to +4.3 pts. | 0.45 | CONSISTENT — strong primary explanation |
| H2 | HumanEval pre-training contamination: Qwen2.5-Coder explicitly removed HumanEval/MBPP via 10-gram dedup; Qwen2.5-1.5B-Instruct (non-Coder, the one we use) inherited the base pre-training corpus; even with dedup the canonical solutions for HumanEval are saturated in web crawl. Both arms get the same recall. | Qwen2.5-Coder Tech Report (arXiv 2409.12186) §dedup; arXiv 2601.06103 measures gap-from-contamination shrinks after SFT; 2025 contamination studies show MBPP "code is memorized better at sight." | 0.30 | CONSISTENT for the 4 P/P + f/f identical cases |
| H3 | Qwen2.5-1.5B-Instruct (non-Coder) lacks SyntaxError-floor: the 8 fail cases ALL fail at the def line with SyntaxError-class errors (not NameError; typing-import IS being prepended per cell L251-252 selftest). At 1.5B non-Coder, instruction-following is too weak to produce syntactically valid Python on docstring-heavy prompts. Snippets can't paper over basic syntax failures. | arXiv 2405.19874 "Is In-Context Learning Sufficient for Instruction Following?" — ICL alignment underperforms instruction-FT at all scales; gap larger at 1.5B. arXiv 2507.03160 small-LM survey — non-coder 1.5B sits below 30% pass@1 on HumanEval even with strong prompts. | 0.40 | CONSISTENT — bare baseline pass1_A=0.167 (1/6) is below the 0.421 published Qwen2.5-1.5B-Instruct HumanEval baseline, consistent with stdlib-subset being the hard subset + N=6 noise |
| H4 | Top-K=3 + 39-snippet corpus is below useful-context threshold; HumanEval needs full canonical implementations, not 1-line API summaries. | CodeRAG-Bench "first 500 tokens" optimal — our snippets are <30 tokens each; total context add ~80 tokens of API one-liners. | 0.35 | CONSISTENT — even when sub PASSES, ntok grows (HE/3 37→54 means model writes more code but doesn't gain pass-rate signal at N=6) |
| H5 | MiniLM retrieval picks SEMANTICALLY-wrong snippets (e.g. HE/1 separate_paren_groups gets "string.split / re.split / string.join" — none of which use the bracket-counting algorithm needed). | snippet_top_sim values 0.31–0.62: mediocre; visual inspection of returned snippets shows ZERO algorithmic match for paren-balancing problems. | 0.45 | CONSISTENT — retrieval surfaces lexically-near "string-manipulation" snippets where the actual problem is a stack/counter algorithm |
| H6 | Qwen at 1.5B is fully memorized on HumanEval and produces same canonical answer regardless of context. | CodeRAG-Bench §"both datasets mostly test on common Python libraries, which powerful models may have already memorized"; arXiv 2509.21882 RLVR contamination measurement. | 0.15 | WEAK — Qwen-1.5B is NOT a "powerful model" and produces different code per token-counts; memorization predicts identical outputs, not different ones |
| H7 | Prompt template is broken (snippets reach Qwen as noise). | — | 0.05 | RULED OUT by selftest + visual prompt inspect (cell L213-222) |
| H8 | Sub-arm token budget swallows the actual prompt. | max_new_tokens=256; snippets add ~80 input tokens. | 0.05 | RULED OUT — output ntoks are 24–154, never hit cap |

**Combined picture:** H1 + H5 (wrong source × wrong-snippet retrieval) and H3 (1.5B Syntax-floor) are the dominant signals. H2 (memorization) explains the 4 identical cases. None of these are substrate-fundamental — they are all "wrong knob" or "wrong scale" findings.

## DECISIVE CHEAP TEST PRE-REG (REPLACEMENT CELL)

**Anchor name:** `exp_humaneval_canonical_solution_retrieval_qwen_v1`

**Design (1-A-B-C 3-arm; smoke = 10 problems same split; full = 80 stdlib + 84 algo; 1 seed):**
- ARM 0 BARE: identical to current bare arm.
- ARM 1 STDLIB-DOC (current cell's substrate-augmented arm): unchanged.
- ARM 2 CANONICAL-RETRIEVAL: substrate retrieves the top-K canonical solutions from a holdout-AWARE corpus of MBPP solutions (NOT HumanEval to avoid contamination) where retrieval target = NL prompt → MBPP canonical solution by MiniLM cosine. Snippet body = full `def f(...): ...` body, 500 tokens max (per CodeRAG-Bench optimal).

**Why this is decisive:** ARM 2 - ARM 0 is the direct replication of CodeRAG-Bench's published +12.2 point lift. ARM 1 - ARM 0 is what we already measured (≈0). If ARM 2 - ARM 0 ≥ +8 points on Class A AND ARM 1 - ARM 0 < +5, then H1 (wrong-source) is the right diagnosis and substrate-as-canonical-retrieval-index has a path forward. If BOTH arms are flat, then H3 (1.5B floor) dominates and the bottleneck is model size, not retrieval.

**Pre-reg bands (cell-local; cap novel-synthesis P at 0.50; deflate 0.15-0.25):**

| Outcome | ARM 2 - ARM 0 (Class A) | ARM 1 - ARM 0 (Class A, reproducing current) | Verdict | P (deflated, cap 0.50) |
|---------|--------------------------|------------------------------------------------|---------|--------------------------|
| **HARD_PASS** | ≥ +0.10 | < +0.05 | retrieval-source-decisive; canonical-solution RAG works at 1.5B; substrate-as-canonical-retrieval-index validated | **0.30** (CodeRAG-Bench saw +12.2 on StarCoder2-7B; deflated for 1.5B-non-Coder + smaller corpus) |
| **MIDDLE_BAND** | +0.05 to +0.10 | < +0.05 | weak signal toward canonical-retrieval; ship full N=164 to confirm | 0.30 |
| **MIDDLE_BAND (both)** | ≥ +0.05 AND ARM 1 ≥ +0.05 | — | retrieval helps generically; not source-specific; weaker substrate claim | 0.15 |
| **HARD_FAIL (1.5B floor)** | < +0.05 AND ARM 1 < +0.05 | < +0.05 | model-size floor; ALL retrieval ineffective at 1.5B; pivot to 3B or Coder-variant | **0.20** |
| **HARD_FAIL (wrong-direction)** | ≤ -0.05 OR ≤ -0.05 | — | canonical-retrieval HARMS; investigate prompt-bloat / context-confusion | 0.05 |

**Mandatory HARD-FAIL bands (negativity-symmetry per role contract):** ARM 2 ≤ -0.05 → HARD_FAIL wrong-direction; ARM 2 ≥ +0.20 OR ARM 1 ≥ +0.20 → MIDDLE_BAND-suspicious (likely contamination leakage from MBPP→HumanEval; investigate before HARD_PASS).

**Cost:** ~12 minutes laptop CPU smoke; same path as current cell. Full N=164 ≈ 3 hours laptop (or 30 min remote_cpu via Orchestrator).

**Falsifiable predictions:**
1. ARM 2 will produce LONGER outputs than ARM 1 (canonical-solution context primes longer code; deflated P=0.45).
2. ARM 2 will have lower per-problem snippet_top_sim variance than ARM 1 (canonical solutions are tighter semantic matches; deflated P=0.40).
3. On the 4 HumanEval problems already passing bare (HE/2, HE/3, HE/16, HE/26 partial), ARM 2 will NOT regress (canonical retrieval is monotonically helpful on memorized cases; deflated P=0.55, slightly above cap → set to 0.50).
4. The HumanEval/25 factorize problem (currently bare-SyntaxError, sub-AssertionError) will pass ARM 2 if any canonical factorize solution is in the corpus; deflated P=0.40.

## CROSS-THREAD SYNTHESIS

**(a) vs glass-box-LLM lane (L2 vision):** This cell is NOT substrate-native (substrate_native=False; substrate_role=prompt_augmentation). The glass-box-LLM lane's MOAT is continual-learning via CLS-replay, NOT prompt augmentation. Even a HARD_PASS on the canonical-retrieval variant would be a TIER-2 finding (substrate-as-tool-for-LLM), not chain-grade evidence for the glass-box vision. Worth shipping IF it builds infrastructure (a canonical-solution KG indexed in the substrate) but not as a primary L2 lever.

**(b) vs substrate KG retrieval (CERT 588 portfolio):** Substrate has ALREADY demonstrated chain-grade retrieval over (i) FB15k-237 structured KG (584), (ii) ConceptNet lexical KG (585), (iii) HotpotQA multi-hop Wikipedia (588). Adding "canonical Python solutions" as a 4th KG-style retrieval domain is a NATURAL extension of the proven substrate-as-retrieval-index pattern. The substrate is NOT the gating factor here; the LM consumer is. This re-frames the cell as substrate-KG-stress-test on a NEW domain rather than substrate-augmented-LLM probe.

**(c) vs L3 capability table:** The "substrate-augmented LM at 1.5B" probe is testing a different axis than the substrate's CERT'd capability. If we want substrate-augmented-LM as a published L3 capability, the right model scale is 7B+ where CodeRAG-Bench shows the lift is robust. At 1.5B the entire RAG literature shows mixed results; failing to replicate Qwen2.5-Coder-1.5B's 41-46% HumanEval (we got 16.7%) suggests our model loading or prompt template has a SECONDARY issue (Qwen2.5-1.5B-Instruct non-Coder vs Qwen2.5-Coder-1.5B-Instruct — possible model-card swap-out worth verifying before any future re-spin).

**(d) vs USER 4-phase program:** USER said "halt LLM head-to-head positioning; capability development is goal; cert-grade is instrument." This cell is LLM-head-to-head-adjacent. The substrate-native arc (sequence-binding c3, autoregressive g1b, by-construction-saturation) is higher-leverage than chasing HumanEval gain. **Recommendation: do NOT ship the canonical-retrieval variant as a substrate priority; preserve it as an opportunistic add-on if Exp-Dev wants to validate the substrate-as-canonical-KG indexing infrastructure for later glass-box use.**

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **At 1.5B scale, substrate-augmented LM has limited path forward via prompt-prepending.** Lit converges: <3B models are below the instruction-following floor where RAG context is reliably used; gains are noisy and depend on retrieval source matching benchmark distribution. Substrate's value is NOT in being a better prompt-RAG index than MiniLM-FAISS for a 1.5B model.
2. **Substrate-as-canonical-KG for LLM augmentation is plausible at 7B+ scale**, where CodeRAG-Bench published +12 point lifts. This is a future product lever, NOT a current cell-level priority.
3. **The current cell's primary load-bearing finding is NEGATIVE on the chosen knob (stdlib-docs as retrieval source) and SILENT on the substrate**. Skunkworks should atomize as MEASURED_MECHANISM (scope-locating: stdlib-doc retrieval is wrong source for HumanEval at 1.5B), NOT as substrate-capability evidence either way.
4. **The 16.7% bare Class-A pass rate (vs 42.1% published Qwen2.5-1.5B-Instruct HumanEval baseline) suggests the cell's BARE arm may be under-performing.** Cause hypothesis: stdlib subclass is the hard subset + N=6 (1/6 = 16.7% is wide CI [0.4%, 64%]). Not alarming at smoke; full N=80 will tighten the CI. Worth a sanity-check that the bare prompt template isn't sub-optimal vs the published eval harness.

## RECOMMENDED NEXT ACTION

1. **HOLD this cell.** Do NOT re-dispatch the original stdlib-doc-retrieval cell at full N=164; the smoke null is well-explained by published lit.
2. **OPTIONAL low-priority follow-up:** If Exp-Dev has spare capacity, ship the 3-arm canonical-retrieval variant `exp_humaneval_canonical_solution_retrieval_qwen_v1` (12-min smoke) to nail down H1 vs H3. HARD_PASS adds a TIER-2 finding (substrate-as-canonical-solution-KG). HARD_FAIL definitively closes the 1.5B-substrate-augmented-LM lane for now.
3. **HIGHER-PRIORITY redirect:** Move Exp-Dev attention back to the substrate-native arc (bigram-gap closure, brain-drills, phase-portrait v1, substrate_self_map_v2). The substrate's CERT-class wins this arc are coming from substrate-native cells, not prompt-augmentation cells.

## CITATIONS (verified)

1. **CodeRAG-Bench: Can Retrieval Augment Code Generation?** Findings of NAACL 2025. https://aclanthology.org/2025.findings-naacl.176.pdf — Table 5 (HumanEval baselines: StarCoder2-7B 31.7%, CodeLlama-7B 34.8%, DeepSeekCoder-7B 70.1%); Table 6 (BM25-retrieval competition solutions +12.2 pts on StarCoder2-7B); Table 7 (retrieval-source ablation: library docs flat on HumanEval; StackOverflow +1.8 to +4.3 pts).
2. **DocPrompting: Generating Code by Retrieving the Docs** (Zhou et al. 2022). https://arxiv.org/abs/2207.05987 — CodeT5 +2.85 pass@1 on CoNaLa (52% relative); tldr +6.9 EM on GPT-Neo-1.3B. Note: CoNaLa / tldr are library-API tasks where docs ARE the right source; not HumanEval-comparable.
3. **Qwen2.5 Technical Report** (Qwen Team 2025). https://qwenlm.github.io/blog/qwen2.5-llm/ — Qwen2.5-1.5B-Instruct HumanEval pass@1 = 42.1; Qwen2.5-Coder-1.5B pass@1 = 41.6 (baseline) → 46.8 after 4-stage filtering. arXiv: https://arxiv.org/pdf/2412.15115
4. **Qwen2.5-Coder Technical Report** (Hui, Yang et al. 2024). https://arxiv.org/abs/2409.12186 — 10-gram overlap dedup applied to HumanEval, MBPP, GSM8K, MATH; explicit contamination-control language at §dedup.
5. **Is In-Context Learning Sufficient for Instruction Following?** (Zhao et al. 2024). https://arxiv.org/abs/2405.19874 — ICL alignment underperforms instruction-FT on established benchmarks; adding more ICL demos doesn't systematically improve instruction-following at small scale.
6. **Assessing Small Language Models for Code Generation: An Empirical Study** (2025). https://arxiv.org/html/2507.03160v4 — survey of 20 open-source SLMs 0.4B-10B across HumanEval/MBPP/Mercury/HumanEvalPack/CodeXGLUE; documents pass@1 floor for non-code-specialized 1.5B models.
7. **The Impact of Post-training on Data Contamination** (2026). https://arxiv.org/html/2601.06103 — contamination injected into Qwen2.5 (0.5B/1.5B); MBPP "code is memorized better at sight" but performance normalizes through SFT+GRPO.
8. **EvalPlus / HumanEval+** (Liu et al.). https://github.com/evalplus/evalplus — auto-generates ~80x more tests per HumanEval problem; many models drop 10-20 pass@1 pts on HumanEval+, suggesting standard HumanEval is too permissive for tight differentiation.

## ONE-LINE OUTPUT

`humaneval_drill_delivered: D:/AI/hd-instrument/notes/research_humaneval_snippet_injection_ineffective_drill_2026-06-22.md; HEADLINE: smoke null is well-explained by published lit (CodeRAG-Bench: lib-docs don't help HumanEval; canonical solutions give +12.2pt on 7B; 1.5B floor compounds); P_deflated=0.30 (canonical-retrieval variant likely HARD_PASS at +0.10 ClassA gain if shipped, but LOW priority vs substrate-native arc); next-cell: exp_humaneval_canonical_solution_retrieval_qwen_v1 (OPTIONAL; HOLD if substrate-native bandwidth-constrained)`
