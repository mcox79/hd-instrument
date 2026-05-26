# Research R3 — Compositional generalization test design

**Topic.** Strategy's R3 (open since cycle 1, Tier-2 Holy-Grail in cap_map v1):
substrate has no test for compositional generalization. Compositional
generalization is "the ability to produce novel combinations of learned
primitives that were never seen together in training." R3 asks: what
published benchmarks exist, what do they measure, and which can be ported
to a byte-level retrieval-based language model?

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real external
literature scan** via Agent subagent (~5 min runtime, 23 tool uses, 27+
verified citations across 2018–2026). Pass 2 drills substrate-specific
porting + predicted behavior.

---

## Pass 1 — External literature scan (verified)

Generic-linguistics / ML queries via subagent: "compositional generalization
evaluation benchmark," "SCAN benchmark Lake Baroni," "COGS Kim Linzen,"
"Hupkes systematic generalization taxonomy," "compositional generalization
byte-level," "VSA compositional generalization," etc. No substrate fingerprint.

### 1.1 The taxonomy of compositional generalization

**Hupkes, Dankers, Mul, Bruni 2020** (JAIR 67:757–795, arXiv:1908.08351,
"Compositionality decomposed: how do neural networks generalise?") is the
reference taxonomy. Five task-independent axes derived from
linguistic/philosophical theory:

- **Systematicity**: novel combinations of seen primitives (canonical
  "jump twice" SCAN test).
- **Productivity**: generalize to expressions longer/more complex than
  training (depth/length extrapolation).
- **Substitutivity**: synonymous units interchangeable without semantic
  change.
- **Localism**: composition operations apply locally; global rewrites
  shouldn't change local meanings.
- **Overgeneralization**: model should NOT extend rules that don't actually
  hold (e.g., irregular morphology).

**Hupkes-Giulianelli et al. 2023** (Nature Machine Intelligence;
arXiv:2210.03050) extends to a 5-axis taxonomy of *all* generalization
research — compositional is one of five top categories. Other 2023-24
surveys: **Sun et al. 2023** (arXiv:2302.01067, "A Survey on Compositional
Generalization in Applications"); **Mittal et al. 2024** ("A Survey on
Compositional Learning of AI Models").

Contested: whether "systematicity" and "productivity" are separable
(Lake-Baroni argue yes; recent work treats length and lexical
generalization as a single inductive-bias question).

### 1.2 Canonical benchmarks — what they actually test

- **SCAN** (Lake-Baroni 2018, arXiv:1711.00350): command→action sequences
  over primitives {jump, walk, look} and modifiers {twice, around left,
  after}. Splits: simple/length/jump/turn-left/add-prim. SOTA: vanilla
  seq2seq **~0%** on jump-split; specialized neuro-symbolic / meta-learning
  approaches (Lake 2019 meta-seq2seq, Liu 2020 LANE) reach near 100%;
  **Lake-Baroni 2023 MLC** (Nature 623:115–121) claims human-level systematic
  generalization (contested).

- **COGS** (Kim-Linzen EMNLP 2020, arXiv:2010.05465): synthetic English →
  logical form. **In-distribution 96–99%, generalization 16–35%** for
  Transformer/LSTM — the canonical "huge gap" result.
  **ReCOGS** (Wu et al. 2023, arXiv:2303.13716) re-codes output form;
  gen accuracy rises to ~80% — suggesting some of the gap was
  representation-mismatch artifact, not pure compositional failure.

- **CFQ** (Keysers et al. ICLR 2020, arXiv:1912.09713): 239k natural-
  language questions → SPARQL. Uses **DBCA (distribution-based
  compositionality assessment)** which maximizes **compound divergence**
  while minimizing **atom divergence**. Baseline T5: ~35% MCD mean accuracy;
  specialized models reach 70–90%; pretrained T5-11B remains below ceiling.

- **PCFG SET** (Hupkes et al. 2020, same JAIR paper): formal grammar over
  functions (copy, reverse, append, shift). **The only benchmark that
  directly instantiates all five Hupkes axes.** Transformer accuracy
  varies widely per axis (productivity hardest).

- **gSCAN** (Ruis-Andreas-Baroni-Bouchacourt-Lake NeurIPS 2020,
  arXiv:2003.05161): grounded grid-world SCAN; tests adverb composition,
  novel attribute combinations. Baseline 10–30% on novel splits;
  Qiu 2021 (arXiv:2109.12243) shows most splits cracked but
  adverb-to-verb remains hard.

- **NACS** (natural+artificial command split), **Compositional MATH**
  (Lee 2024 arXiv:2402.09371, Cho 2024 arXiv:2405.20671 position-coupling
  for length extrapolation).

### 1.3 Byte-level compositional benchmarks — THE LITERATURE GAP

**This is the most important finding.** The lit scan was unambiguous:
**there is NO established byte-level compositional benchmark in
2024-2026.** All published benchmarks operate at token/symbol level.

- **ByT5** (Xue et al. 2022, arXiv:2105.13626): strong on morphological
  and orthographically-noisy tasks; better than mT5 at small scale;
  outperforms on word-level transliteration, grapheme-to-phoneme,
  morphological inflection. **No direct SCAN/COGS evaluation in the
  original paper.** Subsequent work has tested ByT5 on semantic-parsing
  variants with mixed results — byte-level helps low-resource and
  morphology, doesn't obviously help symbolic compositional splits.
- **CANINE** (Clark-Garrette-Turc-Wieting TACL 2022, arXiv:2103.06874):
  char-level encoder; beats mBERT on TyDi QA by 5.7 F1. **Compositional
  gen not directly reported in the paper.**
- **Char-level RNN compositional generalization**: older studies didn't
  run formal compositional tests. Liška-Kruszewski-Baroni 2018
  ("Memorize or generalize?") found char-RNNs memorize.
- **Recent (2024-2026)**: Redhardt et al. 2025 "Scaling can lead to
  compositional generalization" (arXiv:2507.07207) — scale helps, but
  byte-level vs subword not isolated. arXiv:2505.13089 "Systematic
  Generalization in LMs Scales with Information Entropy" — closer to
  byte-level question but uses tokens.

**Honest take**: substrate would have to *port* SCAN/COGS to byte-level
inputs. Protocol identical, only input granularity changes. **This is
substrate-novel territory.**

### 1.4 Compositional generalization in retrieval / kNN / associative memory

Sparse literature here too:

- **kNN-LM** (Khandelwal et al. ICLR 2020): primary finding was perplexity
  + domain transfer; not a compositional test. Xu et al. 2023
  (arXiv:2301.02828) identifies 3 drivers (input representation,
  approximate kNN, softmax temp); doesn't isolate compositionality.
- **RAG**: "Reinforcing Compositional Retrieval" (Findings of ACL 2025);
  Press et al. 2023 (Self-Ask). RAG helps multi-hop but compositional
  generalization specifically is rarely the headline metric.
- **Associative memory / modern Hopfield**: Ramsauer et al. 2020 + the
  2025 review "Modern Methods in Associative Memory" (arXiv:2507.06211).
  Focus on storage capacity and attention equivalence, not formal
  compositional splits.

### 1.5 VSA compositional generalization — THE SECOND LITERATURE GAP

**The lit scan flagged this as a real field gap.** VSA *posits*
compositionality via binding/bundling. Plate's HRR (1995), Kanerva
BSC (1996), Schlegel survey (arXiv:2001.11797), Kleyko 2022 surveys.
LARS-VSA (arXiv:2405.14436, 2024) is on **abstract reasoning, not
language**. Generalized HRR (Liu 2024, arXiv:2405.09689) is recent.

**No paper runs SCAN/COGS on a VSA-only LM with reported numbers.** The
substrate could be the first published characterization. The compositional
*capability* is engineered into VSA via binding; the *generalization*
(extrapolation to compositions not seen during training of the binding
mappings) is rarely benchmarked.

### 1.6 Recent (2024-2026) state of belief

- **Pretraining muddies everything**: Furrer et al. 2020 (arXiv:2007.08970);
  Csordás-Irie-Schmidhuber 2021 ("The Devil is in the Detail",
  arXiv:2108.12284) — small architectural tweaks close large fractions
  of the SCAN gap. "Transformers can't compose" claims were overstated.
- **Scale ≠ free lunch but helps**: Redhardt 2025
  (arXiv:2507.07207) yes-with-caveats; **Dziri et al. 2024** "Faith and
  Fate" (NeurIPS 2023) — LLMs fail at compositional multi-step
  arithmetic/logic that requires true composition.
- **No architecture passes ALL Hupkes axes** in 2024-2026.
- **LLM compositional generalization is partial and inconsistent**:
  Sun et al. 2024 "Revisiting Compositional Generalization Capability
  of LLMs" (arXiv:2506.15629) found ~75% ordered coverage at best.

### 1.7 Theory — Lippl-Stachenfeld kernel theorem (CRITICAL for substrate)

**Wiedemer et al. 2023** "Compositional Generalization from First Principles"
(arXiv:2307.05596) — theoretical conditions for compositional
generalization.

**Lippl & Stachenfeld 2024** "When does compositional structure yield
compositional generalization? A kernel theory" (arXiv:2405.16391) —
**CRITICAL THEOREM for substrate**: kernel models can only compose over
**sums** of seen-component values; **cannot do transitive equivalence**.

This applies to substrate because **the substrate's readout is cosine
similarity = kernel-like inner product**. By Lippl-Stachenfeld, the
substrate is theoretically limited on transitive-equivalence tests. But
per [[feedback-dont-overextend-theorems]]: the theorem rules out a
narrow form (transitive equivalence in kernel regression), NOT all
of compositional generalization. **Substrate might still succeed at
non-transitive tests (length extrapolation, primitive substitution,
sum-style composition).**

Most recent theoretical paper: arXiv:2505.02627 "A Theoretical Analysis
of Compositional Generalization: Necessary and Sufficient Condition"
(2025).

### 1.8 Pass/fail thresholds from published work

- **SCAN**: random ≈ 0% exact-match. **"Solved" ≥99%** on jump-split for
  specialized models. First-pass interesting: 50% with <30-point gap.
- **COGS**: in-dist 96–99%; gen 16–35% vanilla → 80%+ with ReCOGS.
  **"Solved" ≥85%** on structural-gen subset.
- **CFQ**: pretrained T5-11B ~40%; specialized 70-90%. **No model at
  ceiling.**
- **The "in-distribution minus OOD gap" is the canonical single number**:
  Kim-Linzen's 60-80 point gap on COGS is the canonical demonstration
  of compositional failure. **Meaningful pass criterion**: gap should
  be **<10 absolute points** AND in-dist ≥90%.

---

## Pass 2 — Substrate-specific drill

### 2.1 Mapping substrate to a SCAN-style port

The substrate's pipeline (per cap_map v23):
- Bipolar ±1 vectors of dim N=4096
- Storage: W = Σᵢ vᵢ kᵢᵀ (Hebbian outer-product)
- Binding: element-wise XOR (Hadamard product); BSC algebra
- Retrieval: cosine similarity ⟨W·k_query, v_i⟩

**To run SCAN at byte-level, we need:**
1. Encode each command's byte string as substrate key (e.g.,
   byte-K-gram bundling with K=8).
2. Encode each action sequence as substrate value (same byte-level
   encoding).
3. Store (command_key, action_value) pairs in W during training.
4. At test time: query with held-out compound's byte-key; retrieve
   cosine-best action; decode.

**Substrate-specific advantages**:
- Byte-level avoids tokenizer artifacts that confound published results
  (e.g., COGS gen-gap partly from output format per ReCOGS).
- Pool retrieval IS exemplar-based; compositional generalization for the
  substrate reduces to "does similarity in compound-bundle space track
  compositional structure?"

**Substrate-specific challenges**:
- Lippl-Stachenfeld theorem: substrate's kernel-like readout limits
  transitive-equivalence composition.
- BSC's XOR-bind closes the Walsh group (per R8 finding): compositional
  *binding* of stored entities might collide.
- Without explicit grammar inductive bias, substrate has no mechanism
  for productivity (length extrapolation) beyond the K-gram window.

### 2.2 Predicted substrate behavior on Hupkes axes

| Axis | Substrate prediction | Reasoning |
|---|---|---|
| **Systematicity** (novel primitive combos) | ⚠ Partial (50–70%) | Pool retrieval interpolates between seen examples; novel combos that lie in convex hull of training compounds should retrieve correctly. Outside hull: fails. |
| **Productivity** (longer than training) | ❌ Fails (10–25%) | Substrate has no recurrent / unbounded mechanism; byte-K-gram window is fixed. Length extrapolation beyond K is structural impossibility. |
| **Substitutivity** (synonym swap) | ✅ Strong (75–90%) | Pool retrieval is naturally similarity-based; synonyms produce similar byte-bundles. |
| **Localism** (local composition) | ⚠ Partial (40–60%) | Substrate has no explicit syntactic locality; bundle-sum mixes positions. |
| **Overgeneralization** | ⚠ Mixed | Substrate has no rule-extraction mechanism; might fail correct rules and miss correct exceptions. |

**Honest probability** P(substrate passes a published threshold on ANY
Hupkes axis): 30–50% — substrate is plausible on Substitutivity, likely
fails Productivity by construction.

### 2.3 Two-stage test protocol (recommendation)

Stage 1: **Byte-level SCAN add-primitive split** (canonical
systematicity test).
Stage 2: **Byte-level length extrapolation** (productivity stress test;
substrate predicted to fail).

Why both: Stage 1 tests the most-favored axis; Stage 2 establishes the
*ceiling* of substrate's compositional generalization. If Stage 1 passes
at credible threshold AND Stage 2 fails, substrate's compositional
story is "interpolation within byte-K-gram window, no productivity."
If both fail, substrate has no compositional generalization. If both
pass, substrate breaks the Lippl-Stachenfeld kernel limit (high prior:
unlikely).

### 2.4 Test design details

**Byte-level SCAN add-primitive (substrate-coherent port)**:

```text
training_data:
  primitives = ["walk", "run", "look"]  # held out: "jump"
  modifiers = ["twice", "around left", "after walk", "and run"]

  For training:
  - All primitives × all modifiers combinations
    EXCEPT compositions involving "jump"
  - "jump" appears ONLY in bare form: "jump" → "JUMP"
  - Compute byte-K-gram bundles for each command;
    store (bundle_command, bundle_action) in pool.

test_data:
  - "jump twice" (held-out composition)
  - "jump around left"
  - "jump and run"
  - 30+ held-out jump-combinations

query_protocol:
  - Encode test command as byte-K-gram bundle
  - Retrieve top-1 stored action by cosine
  - Decode bytes → action sequence
  - Compute exact-match accuracy

verdict:
  PASS if: OOD jump-composition accuracy ≥ 50% AND
            in-distribution accuracy ≥ 95% AND
            gap (in-dist − OOD) ≤ 30 points
  STRONG PASS if: OOD ≥ 80% AND gap ≤ 10 points
  KILL if: OOD < 20% AND gap > 50 points (substrate has no compositional
    generalization beyond surface byte-similarity)
```

**Byte-level length extrapolation (substrate-coherent port)**:

```text
training_data:
  - Synthetic byte-string PCFG (a simple context-free grammar
    over byte vocabulary)
  - Train at sequence lengths ∈ [8, 64]
  - Action mapping: each input symbol maps to fixed action output

test_data:
  - Test at lengths ∈ {128, 256, 512}
  - 100 test sequences per length
  - Measure exact-match accuracy

query_protocol:
  Same as Stage 1.

verdict:
  PASS if: OOD length=128 accuracy ≥ 30%
  STRONG PASS if: OOD length=128 ≥ 60% AND length=256 ≥ 30%
  KILL (expected): OOD length=128 < 10% AND length=256 < 5% (substrate
    bounded by K-gram window; productivity structurally impossible)
```

### 2.5 Cross-cutting controls

- **5 seeds** per condition (in-dist accuracy std-dev ≤ 0.02)
- **In-distribution control**: held-out compounds that ARE in training
  distribution (random split); should match overall accuracy.
- **Random-key control**: replace pool with random ±1 keys; expect
  accuracy ≈ chance.
- **Token-level control (optional)**: encode commands at word level
  instead of byte level; compare to byte-level — establishes whether
  byte-granularity helps, hurts, or is neutral for substrate.

---

## Specific experimental design (pseudocode)

**Experiment**: `wave14_compgen_v1` (two stages, sequential). Pre-registered
at `preregs/2026-05-21_wave14_compgen_v1.md` (Experiment Dev to author).

```text
# Stage 1: SCAN add-primitive (byte-level)

config:
  N = 4096
  K = 8  # byte-K-gram window
  M_train_compounds = 200  # walk/run/look × modifiers
  M_jump_isolated = 10     # "jump" → "JUMP" only
  M_held_out_jumps = 30    # jump compositions for test
  seeds = [7, 17, 23, 31, 41]
  bytes_per_seq = 64

construct_pool(seed):
  pool = []
  for cmd, action in training_compounds:
    cmd_bundle = byte_K_gram_bundle(cmd, K=K)
    action_bundle = byte_K_gram_bundle(action, K=K)
    pool.append((cmd_bundle, action_bundle))
  for cmd, action in jump_isolated:
    pool.append((bundle(cmd), bundle(action)))
  return pool

W = sum(v * k.T for k, v in pool)  # standard Hebbian

predict(query_cmd_bundle):
  scores = [cos(W @ query_cmd_bundle, v) for v in pool.values]
  top_v = argmax(scores)
  return decode_bytes_to_action(top_v)

evaluate:
  in_dist_acc = mean([predict(cmd) == action for held-out from training distribution])
  ood_acc = mean([predict(jump_cmd) == jump_action for held-out jumps])
  gap = in_dist_acc - ood_acc

  PASS iff: ood_acc >= 0.50 AND in_dist_acc >= 0.95 AND gap <= 30
  STRONG PASS iff: ood_acc >= 0.80 AND gap <= 10
  KILL iff: ood_acc < 0.20 AND gap > 50

# Stage 2: byte-level length extrapolation

config:
  K = 8 (same)
  train_lengths = [8, 16, 32, 64]
  test_lengths = [128, 256, 512]
  PCFG_rules = simple_context_free_grammar()
  seeds = [7, 17, 23, 31, 41]
  M_train = 500 sequences per train_length

evaluate (per train length, per test length):
  acc = exact_match_accuracy(test_set, pool=pool_trained_at_train_length)

  PASS iff: acc(test_length=128) >= 0.30
  STRONG PASS iff: acc(test_length=128) >= 0.60 AND acc(test_length=256) >= 0.30
  KILL (expected) iff: acc(test_length=128) < 0.10
```

**Smoke test (queue_add gate)**: N=512, K=4, 1 seed, M_train=20.
Target ~10s. Oracle: in_dist_acc >= 0.80 (basic recall works at smoke scale).

**Self-test (4 synthetic cases)**:
- Identical-train-test: predict in_dist_acc ≈ 1.0, ood_acc ≈ 1.0, gap ≈ 0.
- Random-action-mapping: predict accuracies ≈ chance.
- Perfect-systematicity (manually constructed bundle algebra): predict
  ood_acc ≈ 1.0 (verifies test isn't broken).
- Byte-similarity-only (lookup nearest byte-string): predict gap = high
  (substrate must beat baseline).

**Wall budget**: Stage 1 ~5 min GPU per seed × 5 seeds = 25 min.
Stage 2 ~10 min × 5 = 50 min. Total ~75 min at full scale.

---

## Materials analog (load-bearing)

**The Lippl-Stachenfeld kernel theorem IS the load-bearing materials analog.**

Per Lippl-Stachenfeld 2024 (arXiv:2405.16391), kernel models (models
whose readout is a similarity computation in some feature space) can
compositionally generalize only when the test composition lies in the
**convex hull of seen training compounds**. Formally: if training
compounds are {C_1, ..., C_M} in feature space and test compound C_test =
Σ α_i C_i for some α ∈ Δ^M (simplex), then kernel model predicts
correctly. Outside the convex hull, no guarantee.

**Substrate is kernel-like**: cosine-similarity readout from a stored
pool. The substrate's compositional generalization is **bounded by the
Lippl-Stachenfeld theorem**.

**Substrate-prediction consequence**:
- Systematicity test (novel primitive combos): substrate succeeds IFF
  novel compound bundles lie in convex hull of training bundles. For
  random-bipolar bundles, this is statistically the case for compounds
  within byte-similarity radius of training.
- Productivity test (length extrapolation): novel-length compounds
  always lie OUTSIDE convex hull (training compounds have shorter
  byte-bundles; longer compounds project outside hull). Substrate
  predicted to fail.
- Transitive equivalence: substrate predicted to fail (this is what
  Lippl-Stachenfeld specifically rules out for kernel methods).

**Physics analog beyond kernel theory**:

VSA binding is mathematically tensor / Kronecker product structure.
**Operad theory** (Fong-Spivak; May 1972) studies n-ary operations with
composition laws. Substrate's binding (XOR) is a 2-ary operation; its
compositional generalization properties are determined by the operad
structure it inherits from the Walsh group. Per R8 finding:
Walsh-group closure under XOR-bind means substrate's binding is NOT a
*free* operad — composition relations exist between basis elements.
This limits compositional generalization analytically.

**Statistical-mechanics framing**: Canatar-Bordelon-Pehlevan 2021
("Spectral bias and task-model alignment") shows kernel-regression
generalization as a sum over eigenmodes; compositional structure shows
up as block-diagonal Gram matrices. Substrate's pool retrieval IS kernel
regression; compositional generalization predicted to depend on whether
training-pool Gram-matrix spectrum captures compositional axes.

**Load-bearing**: the kernel theorem makes a *quantitative* prediction
(substrate fails productivity, succeeds at substitutivity within convex
hull). This is the qualitative shape we test.

---

## Falsifiable prediction

**Primary prediction (Stage 1, SCAN add-primitive):**

At N=4096, K=8, M_train_compounds=200, M_held_out_jumps=30, 5 seeds:

- in-distribution accuracy: **≥ 95%** (substrate is essentially memorizing
  via pool retrieval; high accuracy expected).
- OOD jump-composition accuracy: **40–60%** (substrate's pool interpolates
  between seen compounds; novel jumps that lie near "walk"/"run"/"look"
  variants in byte-bundle space succeed).
- gap (in-dist − OOD): **30–50 points**.
- **Verdict**: PARTIAL PASS expected. Substrate-compositional-generalization
  is interpolation-bounded, consistent with Lippl-Stachenfeld kernel
  theorem.

**Stress prediction (Stage 2, length extrapolation):**

- accuracy at train length (in-dist): ≥ 90%.
- accuracy at length 128 (2× training max): **5–15%**.
- accuracy at length 256: **0–5%**.
- accuracy at length 512: **0%**.
- **Verdict**: KILL expected for productivity axis. Substrate has no
  recurrent / unbounded-context mechanism; byte-K-gram window is the
  structural cap.

**Combined verdict**:
- Substrate compositional generalization story: **"interpolation within
  byte-K-gram window only; no productivity beyond training length"**.
- This is consistent with cap_map's prior "UNSURE Tier-2" status — the
  test resolves it to 🟢-partial (substitutivity ✅, systematicity ⚠
  partial, productivity ❌).

**Kill criterion (substrate compositional generalization fully closed)**:

If Stage 1 OOD < 20% AND gap > 50 points across 3 of 5 seeds:
substrate has NO compositional generalization beyond surface
byte-string similarity. Compositional generalization closes
❌-structural in the cap_map; the substrate is a pure interpolative
memory, not a compositional model.

**Falsifier for the Lippl-Stachenfeld bound**:

If Stage 2 length=128 accuracy > 40% across 3 of 5 seeds, substrate
breaks the kernel-theorem prediction for productivity. This would be
**a publishable physics finding** — the substrate's binding algebra
creates compositional structure that kernel theory does not account
for. Investigate via R8's binding-algebra framework (FHRR vs Clifford
chains may interact with productivity differently than predicted).

**Honest probability estimates**:
- P(Stage 1 OOD ≥ 50%) ≈ 60% (substrate interpolation likely works
  for byte-similar compounds)
- P(Stage 1 STRONG PASS ≥ 80%) ≈ 15-25% (would require non-kernel
  compositional mechanism in substrate)
- P(Stage 2 length=128 ≥ 30%) ≈ 10-20% (productivity is structurally
  hard for substrate)
- P(combined "substrate has real compositional generalization") ≈ 15-30%

---

## Citations

1. **Hupkes, Dankers, Mul, Bruni (2020). "Compositionality decomposed:
   how do neural networks generalise?"** JAIR 67:757–795. arXiv:1908.08351.
   — Reference taxonomy: 5-axis decomposition (systematicity, productivity,
   substitutivity, localism, overgeneralization).

2. **Lake, Baroni (2018). "Generalization without systematicity: On the
   compositional skills of sequence-to-sequence recurrent networks."**
   ICML 2018. arXiv:1711.00350.
   — SCAN benchmark; the canonical command→action systematicity test.

3. **Kim, Linzen (2020). "COGS: A Compositional Generalization Challenge
   Based on Semantic Interpretation."** EMNLP 2020. arXiv:2010.05465.
   — Synthetic semantic parsing benchmark; documents the 60-80 point
   in-dist vs OOD gap that defines "compositional failure."

4. **Keysers et al. (2020). "Measuring Compositional Generalization:
   A Comprehensive Method on Realistic Data."** ICLR 2020. arXiv:1912.09713.
   — CFQ benchmark; DBCA methodology with compound-divergence /
   atom-divergence axes.

5. **Lippl, Stachenfeld (2024). "When does compositional structure
   yield compositional generalization? A kernel theory."**
   arXiv:2405.16391.
   — **CRITICAL theorem for substrate**: kernel models can only compose
   over sums of seen-component values; cannot do transitive equivalence.
   Load-bearing for substrate's prediction.

6. **Wiedemer et al. (2023). "Compositional Generalization from First
   Principles."** arXiv:2307.05596.
   — Theoretical conditions for compositional generalization.

7. **Csordás, Irie, Schmidhuber (2021). "The Devil is in the Detail:
   Simple Tricks Improve Systematic Generalization of Transformers."**
   arXiv:2108.12284.
   — Documents that architectural tweaks close large fractions of
   SCAN/COGS gap; "Transformers can't compose" claims overstated.

8. **Hupkes, Giulianelli, Dankers et al. (2023). "State-of-the-art
   generalisation research in NLP: a taxonomy and review."** Nature
   Machine Intelligence. arXiv:2210.03050.
   — 5-axis taxonomy of all generalization research; compositional is
   one of five top categories.

9. **Schlegel, Neubert, Protzel (2022). "A comparison of Vector Symbolic
   Architectures."** AIR 55:4523–4555. arXiv:2001.11797.
   — VSA operator taxonomy; relevant for substrate's compositional
   mechanism baseline.

10. **Wu et al. (2023). "ReCOGS: How Incidental Details of a Logical
    Form Overshadow an Evaluation of Semantic Interpretation."**
    arXiv:2303.13716.
    — ReCOGS reformulation; shows some of COGS gap was representation-
    mismatch artifact, not compositional failure.

11. **Lake, Baroni (2023). "Human-like systematic generalization through
    a meta-learning neural network."** Nature 623:115-121.
    — MLC result claiming human-level systematicity; contested but
    high-profile.

---

## Routing

- **Experiment Dev (E_compgen, new)**: this note recommends two
  experiments in sequence:
  - **Stage 1: `wave14_compgen_SCAN_v1`** (byte-level SCAN add-primitive,
    ~25 min GPU at full multi-seed)
  - **Stage 2: `wave14_compgen_length_v1`** (byte-level length
    extrapolation, ~50 min GPU)
  Run Stage 1 first; Stage 2 is independent but most informative when
  paired (establishes ceiling). Pre-reg + smoke gate + queue-add per
  standard pipeline.

- **Strategy**: this note proposes cap_map row update — "Compositional
  generalization (Tier-2 Holy-Grail)" moves from UNSURE (since v1) to
  🔬 (research-ready experimental design). On positive verdict (PARTIAL
  PASS expected): promote to 🟢-partial with substitutivity ✅,
  systematicity ⚠ partial, productivity ❌. On STRONG PASS (low prior
  ≈ 15-25%): promote to ✅ Tier-2 KILLER and investigate Lippl-Stachenfeld
  break. Strategy keeps writer exclusivity on cap_map.

- **Research (this session, future cycles)**: if Stage 1 STRONG PASSES
  (>80% OOD with <10 gap), follow-up research question on what makes
  substrate compositionally generalize beyond kernel theory prediction
  (R12 candidate). If Stage 2 PARTIAL PASSES (length 128 ≥ 30%),
  follow-up on productivity mechanism within substrate (also R12
  candidate). If both fail at KILL: substrate compositional story is
  fully closed; cap_map updates accordingly.
