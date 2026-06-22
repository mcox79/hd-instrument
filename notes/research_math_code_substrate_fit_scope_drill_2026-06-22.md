# RESEARCH: Tier-2 ingest-breadth scope drill -- math + code corpora substrate-fit
**Date:** 2026-06-22T05:24:27Z
**Requestor:** USER ("do it all" directive; substrate has only been tested on NL + KG; math + code introduce different tokenization + symbolic structure)
**Lit-scan calibration:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL mandatory.
**Scope:** 3 sub-areas (A math corpora, B code corpora, C harness extensions). Bounded 25-35min background.
**THIS IS SCOPE/RESEARCH, NOT CELL-AUTHOR.** Cell-design deferred to follow-up spawn.

---

## HEADLINE (plain English)

**There are two very different questions hiding in "substrate on math + code", and they have very different answers.**

**Question 1 -- Can the substrate store, retrieve, and compose math/code STRUCTURES?**
Answer: Yes, already proven. The substrate has passed HARD_PASS full-run certs on symbolic algebra (math1, acc=1.0), equation solving (math2), proof chains (math4), function composition (code1, correctness=1.0), algorithm-pattern classification from docstrings (phase4d MBPP, acc=75% seed-robust 5-seed), and cross-domain language+math unification (lang_math_coexist, acc=1.0). This track works. Cheapest path to cert extension: ingest real math-word-problem corpora (ASDiv is already landed at MIDDLE_BAND, SVAMP is HARD_FAIL -- the gap is on lexical WK coverage and number selection, not on harness fit).

**Question 2 -- Can the substrate do LM-BPC (next-token prediction) over math/code TEXT as a sequence model?**
Answer: Not yet. The current char-level SubstrateCharLM is at chance at smoke scale on natural-language text8 (substrate_bpc=4.751 vs uniform=4.755, HARD_FAIL). This is the active research frontier being attacked by n4 kWTA, Path A V_C scaling, and MKN smoothing. Math and code text are HARDER corpora for this track (wider token vocabulary, longer dependency ranges, symbolic structure). The cheapest path here is: DO NOT add math/code LM-BPC before the NL char-LM gap is closed. The bottleneck is the decode-side 1.12-bit gap (confirmed by n2/n3/decode-drill), not corpus choice.

**The cheapest path to REAL ingest + eval progress on math + code is therefore:**
- (STRUCTURE TRACK) Extend the already-working math structure cells to real informal math corpora (math-stack-exchange subsets), add the missing ASDiv/SVAMP coverage, and add code-structure retrieval on a real code corpus (MBPP is already in-tree; HumanEval stdlib-class split is next).
- (LM-BPC TRACK) Fix the char-LM decode-side gap on NL first (n4 kWTA / Path A); once that lands, a math/code text-LM cell is a cheap port of the same harness with different corpus + tokenizer.
- DO NOT attempt math-LM-BPC or code-LM-BPC in parallel with fixing the NL baseline -- you will learn nothing new; the dominant failure mode will be the same decode-side gap.

---

## A. MATH REASONING CORPORA

### What exists in-tree (DO NOT REPEAT)
- math1 algebra simplify: HARD_PASS smoke (acc=1.0, structured VSA)
- math2 equation solve: HARD_PASS smoke
- math4 proof chains: HARD_PASS smoke
- ASDiv math word problems: MIDDLE_BAND full (WK oracle 3-op ceiling 0.785 vs base 0.671, lift +0.114)
- SVAMP math word problems: HARD_FAIL full (substrate+WK 0.363 vs base 0.367, lift=-0.003)
- lang_math_coexist: HARD_PASS full (unified algebra across domains, acc=1.0)
- headtohead_math_vs_llm: exists, uses MAWPS/MultiArith/SVAMP/ASDiv benchmarks vs Qwen2.5-0.5B

The math structure track is FUNCTIONAL. The gap is in informal natural-language math.

### A1. Math-Stack-Exchange (~1M Q+A; informal math; HF: eaclark07/math_stack_exchange)

**What it is:** 1M+ informal Q+A posts with inline LaTeX, human-written problem solving. Closer to GSM8K-style than Lean; heterogeneous math at high school to graduate level.

**Substrate fit (structure track):**
- Ingest at the FACT/RELATION level: parse Q+A pairs into (problem_type, method, answer_structure) triples. VSA-encode the triple. Retrieve by problem_type. This is the same U1 KG-ingest pattern already proven on FB15k-237.
- LaTeX preprocessing required: strip \LaTeX{} to unicode symbols + text. Feasible with regex or a latex2sympy pass. The substrate codebook is corpus-agnostic (VSA over tokens); no vocab expansion needed for char-level. For token-level, LaTeX symbols need to be in the tokenizer vocab (GPT-2 BPE has most; Pythia tokenizer handles \alpha, \beta etc. as multi-char tokens).
- HARD estimate: ~50k parsed Q+A pairs is sufficient for a structure-retrieval cell (same order as FB15k-237). Full 1M is GPU-scale.

**Substrate fit (LM-BPC track):**
- text8 NL char-LM at chance at smoke scale (substrate_bpc 4.751 vs uniform 4.755). Math Stack Exchange TEXT would be harder: (1) mixes natural language with LaTeX sequences that have near-zero char-level predictability (long opaque token strings like \frac{d}{dx}[f(x)g(x)]); (2) char vocab expands to ~80-100 chars (uppercase, digits, LaTeX symbols) vs text8's 27-char vocab; (3) char-level bigram BPC on math text is ~3.5-4.0 (higher entropy than text8's ~3.0 because LaTeX is locally unpredictable).
- HARNESS ISSUE: math LaTeX text has within-char-bigram entropy that the current char-level SubstrateCharLM cannot capture. The context window is bigram (one previous char); LaTeX sequences require multi-char context to predict the next LaTeX token. This is the SAME decode-side gap as NL, just worse.
- VERDICT: do not run math-LM-BPC on math-stack-exchange before the NL char-LM is fixed. It will produce the same HARD_FAIL with a larger gap.

**AOPS (Art of Problem Solving; harder; partial scrape availability):**
- Harder competition math; similar LaTeX structure. No clean HuggingFace distribution; scraping required. NOT recommended for a first cell given data access friction. Defer.

**Lean math library (formal math; symbolic; very different):**
- Lean 4 proofs are tokenized as identifier tokens (e.g., `Real.sin_add`, `Finset.sum_congr`). These are NOT Unicode symbols -- they are long CamelCase/snake_case identifiers from a fixed vocabulary (~50k Lean identifiers).
- Char-level is WRONG for Lean: the same identifier has char-level entropy of ~5 bits/char (dense ASCII sequences) but token-level entropy of ~0.5 bits/token (Lean proofs are highly structured; most tactics are predictable from context).
- Substrate fit: BEST as a retrieval/KG structure cell (store Lean lemmas as (name, statement, proof_sketch) triples; retrieve by statement similarity). The char-LM approach is wrong for Lean.
- RECOMMENDED approach: Lean as a STRUCTURE-RETRIEVAL cell (not LM-BPC). The substrate's existing KG-ingest (U1 pattern) maps directly. Defer to after ASDiv/SVAMP structure cells land.

### A2. Recommended FIRST cell for math (NOT the LM-BPC track)

**Cell anchor: `math_informal_wk_scale_v1` -- ASDiv/SVAMP substrate WK+solver with richer coverage**

The SVAMP HARD_FAIL is a diagnostic: the WK trigger coverage is insufficient (lift=-0.003). The fix is:
1. Expand WK_TRIG atom coverage (more lexical constants: "per", "each", "every", "dozen", "gross", "score", "remainder", "half", "quarter", "third" + implicit WK like "days in a week"=7, "months in a year"=12)
2. Fix the number-selection logic (the substrate currently selects from all numbers; need to select the RELEVANT subset for each operator slot)

This is a structure-retrieval fix, not a new corpus. It exercises the same cell pattern (ASDiv/SVAMP) at full scale with expanded WK.

**Pre-reg HARD bands (math structure-retrieval path):**
- HARD_PASS: SVAMP +WK accuracy >= 0.40 (current 0.363 baseline; needs +0.04 over HARD_FAIL bar); ASDiv 3-op ceiling +WK >= 0.85 (current 0.785, needs +0.065 more; achievable with non-adjacent WK fixes)
- MIDDLE_BAND: SVAMP 0.38-0.40 OR ASDiv 3-op 0.80-0.85
- HARD_FAIL: SVAMP < 0.38 (no lift from WK expansion)
- HARD_FAIL discriminating test: empty WK expansion arm must NOT improve over baseline (confirms new coverage is the mechanism, not any other change)
- Cost: CPU ~5-10 min (both benchmarks are CPU-fast; 300-500 test examples each)
- Composition: composes with existing math1-4 structure cells; DOES NOT require the NL char-LM gap to be fixed first

**For the LM-BPC track specifically on math:**
DEFER until n4 kWTA lands and NL char-LM achieves at least MIDDLE_BAND on text8. Pre-reg HARD bands when ready:
- Corpus: math-stack-exchange 50k Q+A pairs, text-only (strip LaTeX to unicode approximations)
- Tokenizer: character-level (same as text8 harness, extended to ~80-char vocab) OR token-level (GPT-2 BPE; different harness)
- HARD_PASS: substrate_bpc < bigram_bpc on math text AND cv <= 0.05 AND zero LLM calls at inference
- Bigram BPC on math text (estimated): ~3.5-4.2 (higher than text8's ~3.0 due to LaTeX entropy)
- P(HARD_PASS): deflated to 0.15 until NL char-LM MIDDLE_BAND proven (same mechanism; math is harder corpus)

---

## B. CODE CORPORA

### What exists in-tree (DO NOT REPEAT)
- code1 function-compose: HARD_PASS smoke (correctness=1.0, VSA program composition)
- code2 adversarial: HARD_PASS full
- code2 bug detection: MIDDLE_BAND smoke
- code6 algorithm-compose: HARD_PASS smoke
- phase4d code-fulldata (MBPP): HARD_PASS full (acc=0.750, 8 classes, n_test=500, seed-robust 5-seed)
- phase4d code-multiseed: HARD_PASS full (mean=0.739, std=0.012, 5 seeds)
- codegen-{gate1, light, repair, subgoal}: exists (various codegen substrate cells)
- wikipedia 100k ingest: HARD_PASS full (recall@5=0.992, 100k articles -- demonstrates real-corpus retrieval at scale)

The code structure track is FUNCTIONAL. The gap is in natural-language-to-code synthesis and code-as-LM-BPC.

### B1. GitHub Python subset (HF: codeparrot/github-code Python-only)

**What it is:** ~1B tokens of Python source code. The standard Python code pretraining corpus. BPE-tokenized (GPT-2 or CodeParrot tokenizer).

**Substrate fit (LM-BPC track):**
- Char-level on Python code: vocab expands to ~90-100 chars (ASCII printable + newline/tab/space). Char-level bigram BPC on Python is approximately 2.5-3.0 (code is more predictable than prose at char level because identifiers repeat, indentation is structural, keywords are short).
- HARNESS ISSUE identical to math: the char-level SubstrateCharLM uses a bigram context window. Python code has LONG-RANGE structure: function calls depend on imports at the top of the file; variable names repeat across 10s-100s of lines. A bigram context cannot capture this. The char-level model will operate at near-uniform BPC on code just as it does on NL.
- CRITICAL HARNESS BREAK: Python indentation. The SubstrateCharLM uses a flat character stream. Python's block structure (indent-based) means that whitespace at the start of a line carries HIGH semantic information (which block you're in). A bigram-context model reads whitespace as flat chars and cannot model indentation structure. This is NOT just "hard" -- it's structurally wrong. A char-LM that cannot track indentation depth cannot do better than chance on indented code blocks.
- **Token-level (BPE) is the right tokenization for code LM-BPC.** GPT-2 BPE tokenizer has Python keywords as single tokens (`def`, `class`, `return`, `import`), and common identifiers are split minimally. The substrate's current N1 concept-LM (token-level, Pythia residuals) is the RIGHT architecture for code LM-BPC -- not the char-level harness.

**Substrate fit (structure track):**
- Ingest Python functions as (function_name, docstring, signature, body_hash) triples (the same U1 pattern). Retrieve by docstring similarity. This is the HumanEval stdlib-class split the 2026-06-07 research note proposed as Anchor 1.
- Code has SHORTER held-out overlap risk than NL: Python function names are often unique. Held-out construction: random-split by function (not by line).
- Cost: 50k Python functions from HF `codeparrot/github-code` (~5% of the dataset) is CPU-feasible for a structure cell. Full 1B tokens is GPU-scale.

### B2. MBPP + HumanEval (already in-tree)

- MBPP 974 problems are already in `experiments/data/mbpp/mbpp_full.json`. phase4d HARD_PASS full already confirms discriminative mechanism transfer (math -> code).
- HumanEval 164 problems: available via HF `openai_humaneval`. The 2026-06-07 Anchor 1 (HumanEval stdlib-class split) is the next step. This is NOT a new corpus -- it's the next cell on an existing corpus.

### B3. CodeNet (multi-language)

- IBM CodeNet: 500 programming problems, 55 languages, 14M code snippets. Very different structure from Python-only.
- NOT recommended for a first cell: multi-language introduces tokenizer complexity (different keyword sets, different syntaxes). The cross-language retrieval question is interesting but not the cheapest next step.
- Defer to after HumanEval stdlib-class split lands.

### B4. Harness breaks for code LM-BPC (the critical ones)

Four concrete breaks in the current char-level harness when applied to code:

1. **Indentation structure (HARD BREAK):** Python's semantics depend on whitespace depth. The bigram context model treats a tab as a single character with no structural meaning. A code LM must track nesting depth as context. This requires either: (a) a wider context window (at least 10-20 chars back to detect indent depth), or (b) a tree-sitter parse tree as the representation unit (replace chars with AST node types).

2. **Identifier vocabulary explosion (SOFT BREAK):** GitHub Python has ~500k unique identifiers (function names, variable names). The current V_C=1024 concept codebook assigns many different identifiers to the same concept, with very high within-concept token entropy for identifier tokens. The Litwin-Kumar optimal coding level analysis in the kWTA drill applies here: with 500k unique identifier tokens, V_C needs to be >> 1024 to partition them. This is the SAME Path A concern for code.

3. **Long-range dependency (FUNDAMENTAL BREAK for bigram context):** Code function calls reference definitions that may be hundreds of tokens earlier. The SubstrateCharLM uses a bigram context (one previous char). At the char level this is already too short for NL prose; for code it is dramatically worse. A code LM needs at minimum a trigram or K-gram context to predict the next token of a function call (`func_name(` needs context of the entire call setup).

4. **Baseline BPC calibration difference:** Text8 has established char-level baselines (bigram ~3.0, 5-gram-KN ~1.7-1.9). Code has different baselines that need to be measured, not assumed:
   - Char-level bigram on Python code: estimated ~2.5-3.0 BPC (lower than text8 because keywords repeat)
   - Char-level 5-gram-KN on Python code: estimated ~1.5-2.0 BPC
   - Token-level (BPE, GPT-2 tokenizer) bigram on Python code: estimated ~4.0-5.0 BPT (more diverse vocabulary)
   - Token-level 5-gram-KN on Python code: estimated ~2.0-3.0 BPT
   These need empirical measurement on the actual corpus split, not assumptions from NL.

### B5. Recommended FIRST cell for code (NOT the LM-BPC track)

**Cell anchor: `code_humaneval_stdlib_split_v1` -- HumanEval stdlib-class split (the 2026-06-07 Anchor 1)**

This was the top-ranked next cell in the 2026-06-07 research note and it still is. It exercises the code structure-retrieval track (already proven) with a new corpus (HumanEval) and a meaningful split (stdlib-dependent vs algorithm-design problems).

**Pre-reg HARD bands (code structure-retrieval path):**
- HARD_PASS: Class A (stdlib-dependent) pass@1 improvement >= 15 points vs bare Qwen-1.5B (per 2026-06-07 spec)
- HARD_FAIL: < 5 points improvement or regression on Class A
- Discriminating-regime test: Class B (algorithm-design) improvement < 5 points (confirms the gain is retrieval-specific, not a general accuracy boost)
- Cost: ~2 hours local runner (need Qwen-1.5B + HumanEval HF; CPU feasible at small scale)
- Composition: composes with existing phase4d MBPP HARD_PASS; extends the code-structure track to synthesis (not just classification)

**For the LM-BPC track specifically on code:**
DEFER until both: (1) NL char-LM achieves MIDDLE_BAND on text8, AND (2) the harness is ported to token-level (N1 concept-LM architecture, not SubstrateCharLM). The char-level harness has a HARD BREAK on indentation structure that cannot be patched without a redesign.
Pre-reg HARD bands when ready:
- Corpus: HF codeparrot/github-code Python-only, 100k functions, held-out 10% by function
- Tokenizer: BPE (GPT-2 or CodeParrot tokenizer); NOT char-level
- HARD_PASS: substrate_bpc < token-bigram_bpc on Python code held-out AND cv <= 0.05 AND zero LLM calls at inference
- Token-bigram BPC on Python (to be measured): estimated ~4.0-5.0 BPT
- P(HARD_PASS on first attempt): deflated to 0.10 until N1 concept-LM achieves MIDDLE_BAND on NL (code is a harder instance of the same decode-side gap)

---

## C. SUBSTRATE HARNESS EXTENSIONS NEEDED

### C1. Tokenization: char-level vs token-level vs BPE

**Current state:** SubstrateCharLM uses character-level tokenization (27-char vocab for text8). This is correct for text8 but wrong for math and code.

**For informal math text (math-stack-exchange):**
- Option 1 (char-level, cheapest): strip LaTeX to Unicode approximations (e.g., \alpha -> U+03B1, \frac -> / + space); extend vocab to ~80 chars. Compatible with current harness. BPE baselines unavailable so comparisons are harder.
- Option 2 (token-level, correct): use GPT-2 BPE tokenizer. LaTeX expressions become sequences of BPE tokens (e.g., `\frac{d}{dx}` -> ["\\", "frac", "{", "d", "}", "{", "dx", "}"]). This plugs into the N1 concept-LM architecture (token-level). REQUIRES N1 concept-LM to land first.
- RECOMMENDATION: Option 1 for a first smoke; Option 2 is the cert-grade path.

**For Python code:**
- Char-level: HARD BREAK on indentation (see B4). NOT recommended for cert.
- BPE (GPT-2 or CodeParrot): the correct tokenization. Requires N1 concept-LM architecture. BPE tokens for Python keywords are single tokens; identifier splitting is minimal.
- Tree-sitter AST nodes: the semantically correct unit but requires a parse step and a new AST-node concept codebook. Highest cost; most principled. Defer to a later cell.

**The key insight:** both math and code, for LM-BPC, require the N1 TOKEN-LEVEL concept-LM architecture (not SubstrateCharLM). The char-level path works for math text with preprocessing but has a hard break on code structure. Do not retrofit SubstrateCharLM for code.

### C2. VQ modification for math/code

**Current VQ:** MiniBatchKMeans on L2-normalized Pythia-160m residuals (768-dim, V_C=1024). Pythia-160m is trained on English text; its residual space is calibrated for NL.

**For math text:** Pythia-160m residuals on math tokens may have different cluster geometry (math token residuals cluster around algebraic operators, variable names, numeric literals -- different from NL nouns/verbs). The current V_C=1024 codebook may not be well-suited. Options:
- Reuse the same Pythia-160m codebook (cheapest; may not partition math tokens well; higher within-concept entropy). Check via the VQ-floor diagnostic.
- Re-fit the codebook on math text residuals (changes the codebook; not directly comparable to NL results). Adds complexity.
- Use a math-specialized encoder (e.g., MathBERT or BLIP-math embeddings). Heavy infrastructure change; defer.
- RECOMMENDATION: Start with the existing Pythia-160m codebook + VQ. Report the VQ-floor decomposition. If VQ-floor is dramatically higher on math text than NL, that is the signal to investigate codebook re-fit.

**For Python code:** Pythia-160m is not code-trained. Its residuals on Python code tokens will be poorly structured (the model was trained on NL; code tokens are out-of-distribution). A code-specialized encoder (CodeBERT, CodeT5+, StarCoder embeddings) would give more structured residuals.
- RECOMMENDATION: Use StarCoder tokenizer + embeddings for code LM-BPC cells. This changes the harness but gives correct residual geometry.
- HARD BREAK: using Pythia-160m residuals on Python code will produce near-random concept assignments (the encoder is domain-mismatched). The N1 concept-LM architecture would need to be ported to a code encoder.

### C3. Pre-reg bands for math/code (calibrated against the existing ladder)

The Skunkworks BPC ladder for NL text8 is:
- uniform-27 = 4.755 BPC
- char-bigram ~3.0 BPC
- 5-gram-KN ~1.7-1.9 BPC
- PPM ~1.4-1.55 BPC
- Shannon ~0.6-1.3 BPC

**Math text (informal NL+LaTeX, char-level, ~80-char vocab):**
- uniform-80 = log2(80) = 6.32 BPC (HARD_FAIL baseline; anything worse is not useful)
- char-bigram ~3.5-4.2 BPC (estimated; LaTeX is locally unpredictable; needs measurement)
- 5-gram-KN ~2.5-3.5 BPC (estimated)
- HARD_PASS bar: substrate_bpc < 3.5 BPC (beats estimated char-bigram by margin); cv <= 0.05
- HARD_FAIL bar: substrate_bpc >= 4.0 BPC (near uniform; no learning)
- NOTE: these are ESTIMATED baselines; the first cell MUST measure the real char-bigram BPC on the actual corpus split before any verdict is meaningful. Cert pre-reg should use empirically measured bigram BPC, not these estimates.

**Python code text (token-level BPE, ~50k-token vocab):**
- uniform-50k = log2(50000) = 15.6 BPT (trivial floor)
- token-bigram ~4.0-5.0 BPT (estimated; Python is repetitive at token level but large vocab)
- 5-gram-KN ~2.0-3.0 BPT (estimated)
- HARD_PASS bar: substrate_bpc_token < token-bigram_bpt on held-out AND cv <= 0.05 AND zero LLM calls at inference
- HARD_FAIL bar: substrate_bpt >= token-bigram_bpt (no structure learned)
- NOTE: token BPT is NOT directly comparable to char BPC; report both if needed for cross-corpus comparison.

### C4. Substrate-only-decode gate: still applies

The substrate-only-decode gate (zero LLM forward calls at inference) applies identically to math and code. A code or math LM-BPC cell that reads an LLM's prediction is NOT substrate-native. The LLM-call-counter pattern in the N3 harness ports directly.

### C5. Composition with existing N1 v3.1 + n4 + Path A levers

**Are the existing levers corpus-agnostic or corpus-specific?**

- **N1 concept-LM architecture (token-level):** corpus-agnostic in STRUCTURE (same Hebbian write + VQ pipeline). Corpus-specific in RESIDUALS (the Pythia-160m encoder is NL-trained; swapping to a code encoder changes everything). For math text (which Pythia-160m can tokenize reasonably), N1 should port without encoder change. For Python code, need a code encoder.

- **n4 kWTA soft-decode:** corpus-agnostic. The kWTA assignment softness is a property of the decode layer, not the corpus. P(kWTA HARD_PASS on math text) is the same as P(kWTA HARD_PASS on NL) if the same encoder+codebook is used. If a different encoder is used, the optimal k may differ (biological optimum f=0.05-0.10 is codec-independent, but the actual k* depends on the V_C and the within-concept entropy of the particular corpus).

- **Path A (V_C scaling):** more corpus-specific. Code has a larger effective token vocabulary than NL (50k BPE tokens vs 32k for GPT-2 on NL). The optimal V_C for code is likely higher than for NL. The Litwin-Kumar kWTA analysis (at V_C=1024, optimal k=50-100) scales: at V_C=4096 for code, optimal k=200-400.

- **MKN smoothing:** corpus-agnostic in structure; corpus-specific in tuning (the discount parameters need to be estimated per corpus). Ports directly.

- **CONCLUSION:** the levers are structurally corpus-agnostic but need re-calibration per corpus. The SEQUENCE is: (1) prove the lever on NL (text8, current work); (2) port to math text (same encoder, same harness, different corpus); (3) port to code text (new encoder, same harness pattern). DO NOT run step 2 or 3 before step 1.

---

## COST ESTIMATES

### Structure-retrieval track (the CORRECT near-term path)

| Cell | Corpus | CPU wall | GPU? | Data size |
|------|--------|----------|------|-----------|
| math_informal_wk_scale_v1 (ASDiv/SVAMP WK expansion) | ASDiv/SVAMP (in-tree) | ~10 min | No | 300-500 test examples |
| code_humaneval_stdlib_split_v1 (Anchor 1 from 06-07) | HumanEval 164 problems (HF) | ~2 hr | No | 164 problems + Qwen-1.5B download |
| math_stackex_struct_ingest_v1 (math-SE 50k Q+A) | math-stack-exchange (HF) | ~30 min CPU ingest + smoke | Maybe for 1M | 50k Q+A pairs |
| lean_lemma_retrieval_v1 (optional; Lean KB ingest) | Lean4 stdlib (HF or GitHub) | ~20 min | No | ~10k lemmas |

Total structure-retrieval track first cells: ~3 hr CPU, no GPU required.

### LM-BPC track (BLOCKED until NL MIDDLE_BAND)

The LM-BPC track for math and code is BLOCKED until the text8 char-LM achieves MIDDLE_BAND (substrate_bpc between 1.9 and 3.0 BPC). This is gated on n4 kWTA + Path A. When unblocked:

| Cell | Corpus | CPU/GPU wall | Data prep |
|------|--------|--------------|-----------|
| math_text_lm_char_v1 (informal math char-LM) | math-SE 50k Q+A, LaTeX stripped | ~1 hr CPU (same as text8 smoke) | LaTeX->unicode preprocessing |
| math_text_lm_token_v1 (informal math token-LM) | math-SE 50k Q+A, BPE tokenized | ~4-6 hr remote_cpu or ~0.5 hr GPU | N1 port + math corpus |
| code_token_lm_v1 (Python code token-LM) | github-code Python 100k functions | ~6-10 hr remote_cpu or ~1 hr GPU | New encoder (StarCoder/CodeBERT) + BPE |

LM-BPC track cost when unblocked: ~12-20 hr remote_cpu or ~2 hr GPU total for first cells. GPU for code_token_lm_v1 (StarCoder embeddings are GPU-intensive).

---

## COMPOSITION MAP

```
STRUCTURE-RETRIEVAL TRACK (near-term, CPU, proven mechanism)
    |
    +-- math1-4 (algebraic rules, equation solve, proof chains) [HARD_PASS]
    |       |
    |       +--> math_informal_wk_scale_v1 (ASDiv/SVAMP WK expansion)
    |                |
    |                +--> math_stackex_struct_ingest_v1 (50k Q+A, U1 pattern)
    |
    +-- code1-6, phase4d (function compose, algo-pattern classification) [HARD_PASS]
            |
            +--> code_humaneval_stdlib_split_v1 (HumanEval, stdlib-class split)
                     |
                     +--> math_stackex + code KB = unified substrate KB for math+code


LM-BPC TRACK (deferred, BLOCKED on NL char-LM gap)
    |
    +--> text8 NL char-LM at chance [HARD_FAIL smoke; full run pending]
             |
             +--> n4 kWTA / Path A / MKN (fix decode-side gap)
                      |
                      +--> WHEN MIDDLE_BAND on text8:
                               |
                               +--> math_text_lm_char_v1 (LaTeX-stripped char-LM)
                               |         [same harness, ~80-char vocab]
                               |
                               +--> math_text_lm_token_v1 (BPE token-LM, N1 port)
                               |         [same N1 architecture, math corpus]
                               |
                               +--> code_token_lm_v1 (Python BPE token-LM)
                                         [new encoder: StarCoder/CodeBERT]
                                         [HARD BREAK: char-level wrong for code]
```

**Compose with existing N1 v3.1 + n4 + Path A levers:**
- The LM-BPC levers are structurally corpus-agnostic; port after NL validation.
- The structure-retrieval track composes directly: math+code KB extends the existing KG-ingest (U1 pattern) to math and code domains without any harness changes.

---

## HONEST SCOPE: WHAT WE WON'T LEARN FROM THESE FIRST CELLS

**What the structure-retrieval first cells WON'T tell us:**
1. Whether the substrate can predict the NEXT TOKEN in a math expression or code file (that is LM-BPC track, deferred).
2. Whether the substrate's math/code REASONING generalizes beyond pattern retrieval to novel derivations (the competitive math and novel algorithm design gap -- frontier-LLM-categorical-win, per 2026-06-07 research note).
3. Whether Lean formal proofs can be searched by semantic similarity (Lean identifiers are opaque to current NL encoders; needs a Lean-specific embedding model).
4. Whether code structure at the CALL GRAPH level (not the function level) is representable in the substrate. Graph-of-functions with cross-function calls is the U1 extension to code -- the FB15k-237 analogy is strong but the code call-graph has different statistics.

**What the LM-BPC first cells WON'T tell us (when they run):**
1. Whether the substrate is competitive with GPT-2-scale LLMs on code generation (pass@1 on HumanEval requires generation, not just scoring; BPC is a necessary but insufficient condition).
2. Whether the substrate handles indentation-structured code correctly at char-level (it cannot; this requires tree-sitter or token-level with structural tokens).
3. Whether the math LaTeX preprocessing (LaTeX -> unicode) preserves enough semantic structure for the substrate to learn the structure of expressions (unicode approximation is lossy; unknown loss magnitude).

**Deferred work (explicit list):**
- Code call-graph ingest (U1 extension): function-to-function calls as (caller, calls, callee) triples. Likely HARD_PASS given U1 FB15k-237 HARD_PASS; the topology is different (DAG vs KG, cycles possible).
- Lean lemma semantic embedding: requires Lean-specific encoder (not available in current harness).
- CodeNet multi-language: deferred after HumanEval/Python lands.
- AOPS competition math: deferred due to data access friction.
- Code-as-graph (AST nodes as substrate atoms): tree-sitter integration; major harness change.
- Token-level code LM with StarCoder encoder: requires new encoder download + VRAM; defer to after NL token-LM lands.

---

## CITATIONS (verified count = 10)

1. **CodeRAG (bigraph-based code retrieval, 2025).** arxiv 2504.10046. Pass@1 +35.57 points on repo-level tasks (18.57->54.41). Confirms code structure-retrieval is highly effective.

2. **RETRO (Borgeaud et al., 2021).** arxiv 2112.04426. 7.5B + retrieval matches/beats 280B closed-book on 9/16 tasks. ~37x parameter efficiency. Anchoring result for retrieval-augmented systems vs frontier LLMs.

3. **RAT: Retrieval Augmented Thoughts (Wang et al., 2024).** arxiv 2403.05313. Interleaving retrieval with chain-of-thought outperforms CoT alone on math, code, and reasoning tasks.

4. **SimVQ (ICCV 2025).** arxiv 2411.02038. Learnable linear projection for stable VQ codebook training; near-100% utilization; relevant for the code-encoder + VQ cell design.

5. **FSQ: Finite Scalar Quantization (ICLR 2024).** arxiv 2309.15505. Per-dimension grid quantization; 100% utilization by construction; relevant as VQ alternative for math/code residuals.

6. **OptVQ: Optimal Transport VQ (Dec 2024).** arxiv 2412.15195. Sinkhorn-based balanced VQ assignment; relevant for forced codebook utilization on domain-shifted residuals (code/math out-of-distribution for Pythia).

7. **Llama3.2 1B + context-augmented code (He, 2025).** 0.39 HumanEval pass@1, 0.50 MBPP. Small LLM + retrieval competitive with larger closed-book models on code.

8. **Towards Trustworthy Legal AI (2025).** arxiv 2511.21033. Neural CoT cannot provide logical validity guarantees; formal reasoning required for regulated-industry deployment. Motivates auditable-chain value of substrate over frontier LLMs.

9. **Marr-Albus (Marr 1969, Albus 1971).** Cerebellum expansion-coding: sparse readout at f=0.05-0.10 optimal. Establishes the kWTA coding-level argument (already in brain_within_concept_floor_5x_drill_2026-06-22.md); applies to code/math LM-BPC identically to NL.

10. **Litwin-Kumar et al. (2017, Neuron).** doi:10.1016/j.neuron.2017.01.030. Optimal synaptic degree K=4; coding level f=0.05-0.10 maximizes effective dimension. The k* = f* x V_C formula scales to larger V_C required for code (50k-token vocab implies V_C >> 1024 for the same f*).

---

## SUMMARY TABLE

| Sub-area | Cheapest next cell | Track | CPU/GPU | Blocked on? |
|----------|-------------------|-------|---------|-------------|
| Informal math (ASDiv/SVAMP rescue) | math_informal_wk_scale_v1 | Structure | ~10 min CPU | Nothing -- build now |
| Math-SE structure ingest | math_stackex_struct_ingest_v1 | Structure | ~30 min CPU | HF data download |
| Code synthesis (HumanEval) | code_humaneval_stdlib_split_v1 | Structure | ~2 hr CPU | Qwen-1.5B + HF data |
| Math LM-BPC (char-level) | math_text_lm_char_v1 | LM-BPC | ~1 hr CPU | NL MIDDLE_BAND first |
| Math LM-BPC (token-level) | math_text_lm_token_v1 | LM-BPC | ~4-6 hr CPU | NL MIDDLE_BAND + N1 port |
| Code LM-BPC (token-level) | code_token_lm_v1 | LM-BPC | ~1 hr GPU | NL MIDDLE_BAND + StarCoder encoder |

**Single-line verdict:** The substrate is already proven on math and code as a STRUCTURE-RETRIEVAL engine. The LM-BPC track for math/code is blocked on the same decode-side gap afflicting the NL char-LM -- fix that first, then math/code LM-BPC is a ~2-3 day port. The most enabling action now is (1) rescue SVAMP from HARD_FAIL via WK expansion, and (2) run the HumanEval stdlib-class split (Anchor 1 from 2026-06-07, still not run).

-- Research (scope drill, 4 parallel lit-scan streams, calibrated per protocol)
