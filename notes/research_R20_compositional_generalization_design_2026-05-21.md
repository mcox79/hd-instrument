# Research R20 — Compositional generalization experiment design (Pass 2 of R3)

**Topic.** Strategy's R20 (HIGH PRIORITY, cycle 27 followup): R3 lit
scan landed cycle 15. R20 = Pass 2 substrate-compatible drill →
detailed experiment spec for Experiment Dev. Closes Tier-2 KILLER ⚪
(compositional generalization untested since cap_map v1).

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min, 24 tool uses,
22+ verified citations 2018-2026). Fifteenth consecutive cycle following
post-audit protocol.

**HEADLINE** (per [[feedback-no-smoke]]): R3 already covered Pass 1
(broad lit survey). R20's Pass 2 produces a **ready-to-build
experiment specification** with:
- Exact file URLs (github.com/brendenlake/SCAN, github.com/najoungkim/COGS)
- Byte-level encoding scheme (ASCII direct + 4 reserved control bytes)
- Multi-metric evaluation (SEQ-EM + byte-accuracy + byte-CER +
  per-category breakdown)
- Csordas 2021 baseline (relative PE + EOS-loss reweighting) as the
  comparison standard
- **ReCOGS recommended over original COGS** (Wu et al. 2023 fixes
  format-artifact penalty)
- **Lippl-Stachenfeld 2024 kernel-theorem-operationalizing diagnostic**:
  per-action-complexity accuracy breakdown to test whether substrate
  hits the predicted kernel bound

---

## Pass 1 — External literature scan (verified)

Generic ML/NLP queries via subagent: "SCAN dataset structure," "Hupkes
systematic generalization implementation," "compositional generalization
sample efficiency," "byte-level NLP evaluation pipeline," "PCFG
synthetic compositional benchmark," etc. No substrate fingerprint.

### 1.1 SCAN dataset — structure and format

**Lake-Baroni 2018** (arXiv:1711.00350) — small synthetic seq2seq
benchmark generated from a phrase-structure grammar.

**Vocabulary** (verified):
- Input primitives: `jump`, `walk`, `run`, `look`, `turn left`,
  `turn right`
- Modifiers: `twice`, `thrice`, `and`, `after`, `around`, `opposite`,
  `left`, `right`
- Output actions (6): `I_JUMP`, `I_WALK`, `I_RUN`, `I_LOOK`,
  `I_TURN_LEFT`, `I_TURN_RIGHT`
- Total: ~20,910 command/action pairs

**File format** (verified from github.com/brendenlake/SCAN): plain
text, newline-delimited. Each line: `IN: <command> OUT: <action>`.
No JSON.

**Five canonical splits**:

| Split | Train | Test | Description |
|---|---|---|---|
| Simple | ~16,728 | ~4,182 | random 80/20 |
| Length | varies | varies | train action ≤22, test ≥24 |
| **Add-prim jump** | ~14,670 | ~7,706 | training excludes `jump` compositionally; standalone `jump`→I_JUMP oversampled |
| Add-prim turn-left | varies | varies | analog with `turn left` |
| Template | varies | varies | 4 variants withholding subcommands |

**Standard baselines**:
- LSTM seq2seq (Lake-Baroni 2018): simple 99%; length 14%; add-prim-jump **1%**
- Transformer absolute PE: length **0%**
- Transformer relative PE (Csordas 2021): length 100% at cutoff 26;
  jump split **~78% mean** (with Csordas tricks)
- CPG (Klinger 2023): perfect SCAN with 14 examples (grammar priors)
- MLC (Lake-Baroni 2023 Nature): human-level systematic generalization
  via meta-learning

### 1.2 Hupkes 2020 5-axis PCFG SET implementation

**Repository**: github.com/i-machine-think/am-i-compositional

**Grammar**: synthetic PCFG producing string-manipulation programs
(functions: `reverse`, `copy`, `append`, `shift`, `swap`, `repeat`,
`echo`) over small terminal alphabet. Outputs = token sequences from
interpreting program.

**Five axes operationalized**:
- **Systematicity**: train has primitive A, primitive B separately;
  test combines (A∘B)
- **Productivity**: train depth N; test depth N+1, N+2
- **Substitutivity**: synonyms introduced at training; test swaps
- **Localism**: structurally equivalent sub-expressions
- **Overgeneralisation**: rules vs memorized exceptions

**Baseline accuracies** (Hupkes 2020):
- Overall task: 80-90% IID
- Productivity: ~50% (Csordas tricks → ~85%)
- Localism: ~45%
- Substitutivity: ~95% (easy)
- Overgeneralisation: ~70%

**Dataset size**: ~100k training, ~10k per axis test split.

### 1.3 COGS dataset — structure

**Kim-Linzen 2020** (arXiv:2010.05465, EMNLP 2020). English sentence
→ lambda-calculus logical form.

**Repository**: github.com/najoungkim/COGS

**Format**: TSV `source\ttarget\tcategory`

**Sizes** (verified):
- train: 24,155 pairs
- dev / test (IID): 3,000 each
- **gen**: **21,000** examples across **21 generalization categories**
  - **16 lexical** (subject-to-object swap, verb-class generalization,
    prim→nominal, etc.)
  - **3 structural** (CP recursion, PP recursion, obj_PP→subj_PP)

**Scoring**: **exact-match on logical form string**.

**Critical**: ReCOGS (Wu-Manning-Potts 2023, arXiv:2303.13716,
github.com/frankaging/ReCOGS) normalizes output format so exact-match
tracks semantic correctness. COGS LFs contain incidental details
(variable indices) that penalize semantically-equivalent strings.
**Use ReCOGS / ReCOGS_pos instead of original COGS for new work**.

**Standard baselines**: vanilla Transformer ~80% lexical / **~0%
structural** on gen; with tricks (relative PE, careful EOS handling),
structural rises to 30-80% but PP-recursion remains hard.

### 1.4 Byte-level port mechanics

**ByT5** (Xue 2022, TACL, arXiv:2105.13626): UTF-8 bytes (256-symbol
vocab + sentinels). Encoder-decoder; trained on mC4. Outperforms mT5
in-language; stronger on morphology/noisy text.

**CANINE** (Clark 2022, arXiv:2103.06874): Unicode codepoint-level
encoder; hash-based char embeddings + downsampling. +5.7 F1 on TyDi
QA vs mBERT.

**Porting SCAN/COGS to byte-level**:
- Mechanically simple — tokens are ASCII
- Encode each input/output character (including spaces) as bytes 0-255
- Reserved control bytes: 256=BOS, 257=EOS, 258=SEP (`IN:`/`OUT:`),
  259=PAD
- SCAN command lengths: ~20-80 bytes
- SCAN action lengths: ~30-250 bytes (e.g., `look around right thrice
  and walk twice` → ~70 bytes)
- COGS sentences: ~50-150 bytes; LFs: ~100-400 bytes
- PCFG SET programs: ~30-200 bytes

**Exact-match in byte space**: compare output byte sequence with
reference byte-for-byte (strip trailing PAD/EOS). Metric unchanged.
**But**: any single-byte error fails the example, so byte-level models
look worse than token-level peers unless normalized edit distance also
reported.

### 1.5 Sample-efficiency

- SCAN simple: ~16.7k train; add-prim-jump: ~14.7k train
- COGS: 24k train; gen: 21k
- PCFG SET: ~100k overall
- CFQ: 95,743 with three MCD splits

**Recent low-shot results**:
- CPG (Klinger 2023, arXiv:2309.16467): perfect SCAN with 14 examples
  (grammar priors)
- MLC (Lake-Baroni 2023 Nature): episodic meta-learning, hundreds-
  thousands of episodes
- Csordas 2021 (arXiv:2108.12284): on SCAN/COGS the data is enough;
  problem is architectural inductive bias

**Substrate-scale guidance**: at N=4096 pool size 10⁴-10⁵, SCAN
simple/jump (≤16k pairs) sits squarely in range. COGS gen (24k+21k)
workable. PCFG SET (100k) at upper edge.

### 1.6 Recent (2024-2026) developments

- **Lippl-Stachenfeld 2024** (arXiv:2405.16391, ICLR 2025): kernel
  theorem — fixed-feature kernel models do "conjunction-wise
  additivity" only. **Substrate-applicable bound.**
- **Wiedemer et al. 2023 NeurIPS** (arXiv:2307.05596): Jacobian
  reconstructability conditions for compositional gen
- **Redhardt 2025** (arXiv:2511.02667): scaling alone may suffice on
  some compositional benchmarks (contested)
- **Sun 2025** (arXiv:2505.13089): "Systematic Generalization Scales
  with Information Entropy"

### 1.7 Substrate-compatible implementation details

For substrate (byte K-gram bundle input, byte sequence output via pool
retrieval, outer-product W at N=4096):

**Input encoding**:
- Sliding K-gram (K=8 or 16) over byte stream of command
- Each K-gram → key vector via byte-position bundling
- Pool stores (key, action_value) pairs

**Train/test split strategy**:
- Use canonical SCAN files unmodified
- Train: process every (command, action) pair through K-gram extractor
- Test: query pool with test command K-grams, decode action
  autoregressively

**Window length**:
- K=8 covers `jump` (4 bytes) + modifier root
- K=16 covers `walk twice` etc.
- Run BOTH as ablation; Hupkes-style productivity stresses larger K

**Action encoding**:
- One byte per step
- ASCII `I_JUMP ` directly
- Reserve byte 0 = PAD, 1 = EOS, 257 = BOS, 258 = SEP

**Pool size vs training set**:
- SCAN simple: ~17k pairs × ~40 bytes/action = 680k step-targets
- Pool capacity must exceed this with margin for collisions
- At N=4096 capacity bound is ~N² = 16M (Hopfield upper bound) but
  effective ceiling is lower due to binding noise

### 1.8 Evaluation metrics

- **Sequence Exact Match (SEQ-EM)**: canonical SCAN, COGS, PCFG SET
- **Byte-level next-token accuracy**: diagnostic for byte-level
  models (separates "structure right but one byte flipped" from
  "completely wrong")
- **Byte-CER (character error rate)**: normalized edit distance
- **Compound divergence**: CFQ MCD splits
- **Per-category accuracy**: COGS gen REQUIRES this; 21 categories

For byte-level: track whether errors cluster at EOS vs interior
(EOS errors dominate length-split failures per Csordas 2021).

### 1.9 Materials science / mathematical analog (LOAD-BEARING)

**Lippl-Stachenfeld 2024 kernel theorem** is the substrate-applicable
load-bearing piece:

> For any fixed-feature kernel model (which includes a frozen-encoder
> retrieval LM), the predicted value on a test compound equals the
> sum of training values restricted to seen sub-conjunctions.

**Substrate implication**: substrate IS a kernel model (frozen-encoder
retrieval). Per the theorem, substrate can predict SCAN add-prim-jump
correctly ONLY IF target action equals **linear sum of training
component actions in feature space**.

**Operationalizable test**: measure performance on add-prim-jump by
**action complexity**:
- Simple compositions (`jump twice` → `I_JUMP I_JUMP`): kernel bound
  passes (linear sum of `jump` and `twice`)
- Nested compositions (`jump around right twice`): kernel bound
  predicts failure (action structure isn't linear sum)
- Performance should drop monotonically with structural complexity

If accuracy is **uniformly poor** regardless of complexity: bottleneck
is upstream (encoder doesn't disentangle).

**Wiedemer 2023 condition** complements: full-Jacobian
reconstructability — if you can't perturb each primitive in isolation
during training, you can't learn it.

---

## Pass 2 — Substrate-compatible experiment specification

### 2.1 Experiment overview (ready-to-build)

**Experiment ID**: `wave14r_R20_compgen_v1`

**Substrate-compatible dataset**: byte-level SCAN add-primitive-jump
split, with secondary COGS validation.

**Why this design**:
- SCAN add-prim-jump is the canonical compositional test (Lake-Baroni
  2018 SOTA = 1% LSTM, 78% Csordas Transformer — wide range)
- Byte-level is required for substrate
- ReCOGS is the secondary validation if Pass 1 (SCAN) succeeds

**Test scope (Stage 1)**: SCAN simple-split sanity + add-prim-jump
generalization with full Hupkes axes breakdown.

### 2.2 Dataset preparation pipeline

```python
# Stage 1: download canonical SCAN
git clone https://github.com/brendenlake/SCAN
cd SCAN/add_prim_split

# Files: tasks_train_addprim_jump.txt, tasks_test_addprim_jump.txt

# Stage 2: byte-level encoder
def encode_scan_pair(line):
    """
    Parse 'IN: command OUT: action' → (input_bytes, target_bytes)
    """
    parts = line.split('OUT:')
    cmd = parts[0].replace('IN:', '').strip()  # lowercase command
    action = parts[1].strip()  # uppercase action

    input_bytes = [ord(c) for c in cmd]  # ASCII bytes 0-127
    target_bytes = [ord(c) for c in action]
    target_bytes.append(1)  # EOS=1
    return input_bytes, target_bytes

# Stage 3: K-gram bundling
def kgram_bundle(byte_seq, K=16):
    """
    Sliding K-gram bundling: for each position i, bundle bytes [i-K, i]
    Returns list of bundle vectors for K-gram retrieval keys.
    """
    bundles = []
    for i in range(K, len(byte_seq) + 1):
        kgram = byte_seq[i-K:i]
        bundle = sum(byte_atom[b] * position_atom[j] for j, b in enumerate(kgram))
        bundles.append(bundle)
    return bundles

# Stage 4: build substrate pool
pool = []
for cmd_bytes, action_bytes in training_set:
    cmd_bundles = kgram_bundle(cmd_bytes, K=16)
    for i, next_byte in enumerate(action_bytes):
        # store (context_bundle, next_byte) pairs
        if i < K:
            context = cmd_bundles[-1]  # use last command bundle
        else:
            context = kgram_bundle(action_bytes[:i], K)[-1]
        pool.append((context, next_byte))
```

### 2.3 Training protocol

```python
config:
  N = 4096
  K = 16  # byte-K-gram window
  num_byte_atoms = 256
  num_position_atoms = K  # one per K-gram position
  num_action_classes = 256 + 4  # bytes + control codes
  seeds = [7, 17, 23, 31, 41]

  # Codebooks
  byte_atoms = random_bipolar(N, 256, seed=seed)
  position_atoms = random_bipolar(N, K, seed=seed+1)

train_substrate(training_pairs):
  W = zeros(N, N)
  for context_bundle, next_byte in pool:
    target_vector = byte_atoms[next_byte]
    # Delta rule update (substrate-standard)
    pred = W @ context_bundle
    error = target_vector - pred
    W = W + (learning_rate * outer(error, context_bundle))
  return W
```

### 2.4 Inference protocol

```python
def predict_action(command_bytes, W, max_action_length=512):
    """
    Autoregressive byte generation for action sequence.
    """
    cmd_bundles = kgram_bundle(command_bytes, K=16)
    context = cmd_bundles[-1]  # initial context from command

    generated = []
    for step in range(max_action_length):
        # Substrate readout
        pred_vector = W @ context

        # Decode byte via cosine similarity to byte_atoms
        scores = cosine(pred_vector, byte_atoms)
        # Temperature scaling (per Bet G ✅ TEMPSCALE β=32)
        probs = softmax(scores * 32.0)
        next_byte = argmax(probs)

        if next_byte == 1:  # EOS
            break
        generated.append(next_byte)

        # Update context with new byte
        context = kgram_bundle(command_bytes + generated, K=16)[-1]

    return bytes(generated)
```

### 2.5 Evaluation protocol

```python
def evaluate(test_set, W):
    """
    Multi-metric evaluation per published best-practice.
    """
    results = {
        'seq_em': [],
        'byte_acc': [],
        'byte_cer': [],
        'per_complexity': defaultdict(list),  # action length buckets
    }

    for cmd_bytes, target_bytes in test_set:
        pred_bytes = predict_action(cmd_bytes, W)

        # Sequence exact match
        seq_em = (pred_bytes == target_bytes)
        results['seq_em'].append(seq_em)

        # Byte-level accuracy
        common_len = min(len(pred_bytes), len(target_bytes))
        byte_acc = mean([pred_bytes[i] == target_bytes[i]
                         for i in range(common_len)])
        results['byte_acc'].append(byte_acc)

        # Byte CER (normalized edit distance)
        results['byte_cer'].append(
            edit_distance(pred_bytes, target_bytes) / len(target_bytes)
        )

        # Per-complexity breakdown (Lippl-Stachenfeld test)
        action_complexity = compute_action_structure_depth(target_bytes)
        results['per_complexity'][action_complexity].append(seq_em)

    return {
        'seq_em_mean': mean(results['seq_em']),
        'byte_acc_mean': mean(results['byte_acc']),
        'byte_cer_mean': mean(results['byte_cer']),
        'per_complexity_em': {k: mean(v) for k, v in results['per_complexity'].items()},
    }
```

### 2.6 Verdict logic (per published best-practice)

```text
PASS_R20_Stage1 iff (5-seed means):
  # Sanity checks (must pass before drawing compositional conclusions):
  simple_split_seq_em >= 0.95  # IID baseline works
  AND simple_split_byte_acc >= 0.99

  # Compositional gen:
  add_prim_jump_seq_em >= 0.30  # exceeds Csordas Transformer floor
                                # (1% LSTM, 78% Csordas mean)
  OR add_prim_jump_byte_acc >= 0.80  # byte-level threshold

  # Lippl-Stachenfeld kernel-bound diagnostic:
  per_complexity[simple] - per_complexity[nested] < 0.2
  # i.e., performance drop with complexity should be GRADUAL not CLIFF

STRONG_PASS iff:
  add_prim_jump_seq_em >= 0.70  # beats Csordas Transformer mean
  AND per_complexity curve monotone-decreasing AND consistent across seeds

KILL iff:
  simple_split_seq_em < 0.80  # substrate can't even do IID
  OR add_prim_jump_seq_em < 0.05  # canonical compositional failure
                                  # mirrors LSTM baseline

PARTIAL iff:
  simple_split_seq_em >= 0.95 AND add_prim_jump_seq_em in [0.05, 0.30]
  # IID works but compositional fails — substrate hits kernel bound
  # as predicted by Lippl-Stachenfeld 2024
```

### 2.7 Lippl-Stachenfeld kernel-bound operationalization

**The substrate-specific diagnostic** that R3's note proposed but
didn't operationalize:

```python
def kernel_bound_diagnostic(eval_results):
    """
    Test whether substrate hits the Lippl-Stachenfeld kernel bound.
    Predicted: kernel models pass simple compositions, fail nested.
    """
    complexity_levels = sorted(eval_results['per_complexity_em'].keys())

    # Simple compositions: jump TWICE, jump THRICE, ...
    simple_em = mean([eval_results['per_complexity_em'][c]
                      for c in complexity_levels if c <= 2])

    # Nested compositions: jump AROUND RIGHT, ...
    nested_em = mean([eval_results['per_complexity_em'][c]
                      for c in complexity_levels if c >= 4])

    kernel_bound_signature = simple_em - nested_em
    # If kernel_bound_signature > 0.3, substrate IS exhibiting
    # the predicted kernel-bound failure pattern

    return {
        'kernel_bound_signature': kernel_bound_signature,
        'simple_em': simple_em,
        'nested_em': nested_em,
    }
```

**Per [[feedback-no-smoke]]**: substrate hitting the Lippl-Stachenfeld
bound is a PREDICTION, not a failure. The bound is real;
substrate-novel claim would be DEFEATING it (which Csordas-style
tricks partially do via architectural changes).

### 2.8 Smoke test (queue_add gate)

```text
config:
  N = 512
  K = 8
  num_train_pairs = 100
  num_test_pairs = 30
  seed = 7

oracle_assertions:
  simple_split_seq_em > 0.5  # smoke must show retrieval works at all
  inference_completes_without_error
```

### 2.9 Self-test (4 synthetic cases)

```text
- Identity train=test: predict seq_em = 1.0 (trivial check)
- Random shuffled action labels: predict seq_em ≈ 1/256 (chance)
- All training has primitive A only, test has primitive A: predict
  high seq_em (no compositional challenge)
- All training has A+twice, A+thrice but test on B+twice: predict
  kernel-bound failure (compositional test)
```

### 2.10 Wall budget

Full multi-seed at substrate scale:
- N=4096, 5 seeds, SCAN add-prim-jump: ~1 GPU hour per seed
- Total: ~5 GPU hours
- ReCOGS validation if Stage 1 passes: +5 GPU hours
- Smoke: ~30s

### 2.11 Stage 2: ReCOGS extension (conditional)

If R20 Stage 1 passes (substrate exceeds Csordas Transformer floor on
SCAN add-prim-jump), Stage 2 ports ReCOGS:

```python
# Stage 2 dataset
git clone https://github.com/frankaging/ReCOGS

# Use ReCOGS_pos (positional variant) - cleaner format
files = ['recogs_pos_train.tsv', 'recogs_pos_test.tsv', 'recogs_pos_gen.tsv']

# Train/test same protocol; gen has 21 categories
# Report per-category breakdown (16 lexical + 3 structural + edge cases)
```

---

## Materials analog (load-bearing — Lippl-Stachenfeld kernel theorem)

**Lippl-Stachenfeld 2024 kernel theorem** is the SUBSTRATE-APPLICABLE
load-bearing piece. From the lit-scan summary:

> "For any fixed-feature kernel model (which includes a frozen-encoder
> retrieval LM), the predicted value on a test compound equals the
> sum of training values restricted to seen sub-conjunctions."

**Substrate is a kernel model**: outer-product W = Σ vᵢkᵢᵀ with cosine
similarity readout is mathematically a Gaussian kernel regressor in
the random feature space.

**Substrate prediction (kernel-bound)**:
- Simple add-prim-jump (`jump twice` → `I_JUMP I_JUMP`): substrate
  CAN predict if `jump` + `... twice` examples in training span the
  feature space directions needed. Per kernel theorem.
- Nested compositions (`jump around right twice`): substrate likely
  CANNOT predict by linear sum — actions interleave (`around` is
  not concatenation), kernel theorem predicts failure.

**Mathematical map**:
- Substrate's encoder = identity (raw byte K-gram bundle)
- Substrate's feature space = R^N (linear bundle space)
- Substrate's training value at compound = stored W·k for that
  compound's bundle representation
- Lippl-Stachenfeld's "sum of seen sub-conjunctions" =
  W·(test_bundle) = Σᵢ vᵢ · (test_bundle · kᵢ) which IS linear sum
  weighted by similarity

**Per [[feedback-dont-overextend-theorems]]**: the kernel theorem
rules out a NARROW form (kernel regression on test compounds outside
the training span). It does NOT rule out:
- Architectural tricks (Csordas relative PE, EOS-loss reweighting)
- Meta-learning (Lake-Baroni 2023 MLC)
- Scaling (Redhardt 2025 — contested)
- Substrate hybridization with explicit grammar (CPG)

Substrate's experiment will likely show kernel-bound signature; the
substrate-novel contribution would be characterizing WHICH
architectural modifications defeat the bound for substrate.

**Wiedemer 2023 Jacobian condition**: complementary diagnostic.
If substrate can't perturb each primitive in isolation during
training (e.g., if `jump` always co-occurs with `twice`), it can't
learn the primitive. Test: vary primitive frequency in training set;
if accuracy improves linearly with primitive isolation, substrate
respects the Wiedemer condition.

---

## Falsifiable prediction

**Primary prediction (Stage 1, byte-level SCAN add-prim-jump)**:

At N=4096, K=16, 5 seeds:

- **Simple split SEQ-EM**: ≥ 0.95 (IID baseline must work — substrate
  is high-capacity memory)
- **Add-prim-jump SEQ-EM**: **0.10 – 0.40** (5-seed mean)
  - Better than LSTM (1%) due to substrate's K-gram input encoding
    capturing more compositional structure
  - Worse than Csordas Transformer (~78%) due to lack of architectural
    inductive bias (no relative PE in pure substrate)
- **Per-complexity decay**: monotone decreasing with action complexity;
  kernel_bound_signature > 0.3 (predicted Lippl-Stachenfeld signature)
- **Byte-level accuracy**: 0.85 - 0.95 even when SEQ-EM is much lower
  (substrate gets mostly-right answers with single-byte errors)

**Stress prediction (length split)**:
- **Length split SEQ-EM**: 0.05 - 0.15 (substrate's K-gram window is
  fixed; length extrapolation beyond K=16 is structurally impossible)

**ReCOGS Stage 2 prediction (if Stage 1 passes)**:
- **Lexical gen categories**: 0.30 - 0.60 (substrate's pool retrieval
  helps with familiar-word swaps)
- **Structural gen categories**: 0.00 - 0.15 (CP/PP recursion is
  beyond substrate's fixed K-gram window)

**Kill criterion**:
- If simple_split_seq_em < 0.80: substrate's basic IID retrieval is
  broken; fix that before drawing compositional conclusions
- If add_prim_jump_seq_em < 0.05 AND byte_acc < 0.70: substrate
  exhibits LSTM-level compositional failure; no architectural
  improvement possible without redesign

**Substrate-novel claim (if STRONG PASS)**:
- If add_prim_jump_seq_em ≥ 0.70: substrate's K-gram input encoding
  PARTIALLY defeats the kernel-bound; this would be a substrate-
  novel publishable contribution (no prior VSA/HDC SCAN result
  cited in lit scan)

**Honest probability estimates**:
- P(simple_split passes ≥ 0.95) ≈ **80-95%** (substrate is high-
  capacity memory; IID retrieval should work)
- P(add_prim_jump ≥ 0.30 — STRONG PASS) ≈ **15-25%** (would defeat
  kernel-bound partially; not impossible per Csordas tricks lineage)
- P(add_prim_jump ∈ [0.05, 0.30] — PARTIAL PASS) ≈ **45-60%**
  (predicted regime; substrate hits kernel-bound as theory predicts)
- P(add_prim_jump < 0.05 — KILL) ≈ **15-25%**
- P(length_split < 0.15) ≈ **80-90%** (structural cap)
- P(R20 publishable substrate-novel finding) ≈ **30-50%** (depends on
  whether STRONG PASS or characterization of kernel-bound failure)

---

## Citations

1. **Lake, Baroni (2018). "Generalization without Systematicity."**
   ICML 2018. arXiv:1711.00350.
   — SCAN benchmark; foundational paper.

2. **Hupkes, Dankers, Mul, Bruni (2020). "Compositionality
   Decomposed."** JAIR 67 / arXiv:1908.08351.
   — 5-axis taxonomy + PCFG SET.

3. **Kim, Linzen (2020). "COGS: A Compositional Generalization
   Challenge."** EMNLP 2020. arXiv:2010.05465.
   — Synthetic semantic parsing benchmark.

4. **Csordás, Irie, Schmidhuber (2021). "The Devil is in the Detail:
   Simple Tricks Improve Systematic Generalization of Transformers."**
   arXiv:2108.12284.
   — Strongest reproducible baselines (relative PE, EOS-loss).

5. **Wu, Manning, Potts (2023). "ReCOGS: How Incidental Details of a
   Logical Form Overshadow an Evaluation of Semantic Interpretation."**
   TACL. arXiv:2303.13716.
   — Format-corrected COGS; should be default.

6. **Lake, Baroni (2023). "Human-like Systematic Generalization
   through a Meta-Learning Neural Network."** Nature 623.
   — MLC; episodic meta-learning.

7. **Lippl, Stachenfeld (2024). "When does compositional structure
   yield compositional generalization? A kernel theory."**
   arXiv:2405.16391. ICLR 2025.
   — **LOAD-BEARING substrate analog**: kernel models do conjunction-
   wise additivity; substrate predicted to hit this bound.

8. **Wiedemer et al. (2023). "Compositional Generalization from First
   Principles."** NeurIPS 2023. arXiv:2307.05596.
   — Jacobian reconstructability condition; complementary substrate
   diagnostic.

9. **Xue et al. (2022). "ByT5: Towards a Token-Free Future."** TACL.
   arXiv:2105.13626.
   — Byte-level T5; reference for byte-level NLP evaluation.

10. **Klinger et al. (2023). "Compositional Program Generation."**
    arXiv:2309.16467.
    — CPG: perfect SCAN with 14 examples (grammar priors).

---

## Routing

- **Experiment Dev (E_R20)**: this note recommends building
  `wave14r_R20_compgen_v1` per the detailed specification:
  - Stage 1: byte-level SCAN add-prim-jump (substrate-applicable
    Lippl-Stachenfeld kernel-bound test)
  - Stage 2 (conditional on Stage 1 PASS): ReCOGS lexical + structural
    gen
  - Multi-metric evaluation (SEQ-EM + byte-acc + byte-CER +
    per-complexity)
  - Use Csordas 2021 Transformer baseline numbers as comparison
    floor/ceiling (1% LSTM, 78% Csordas mean)
  - Pre-reg + smoke gate + queue-add per standard pipeline. ~5 GPU
    hours for full Stage 1; +5h for Stage 2.

- **Strategy**: this note proposes:
  - cap_map row addition: "Compositional generalization" moves from
    ⚪ (untested since v1) to 🔬 (experimental design ready, ~5 GPU
    hours to verdict)
  - On STRONG PASS (≥ 0.70 add_prim_jump SEQ-EM): substrate-novel
    publishable contribution (first VSA/HDC SCAN result per lit
    scan). Promote to ✅ Tier-2 KILLER.
  - On PARTIAL PASS (predicted regime): substrate hits kernel-bound;
    NOT a failure; substrate-applicable physics prediction validated.
  - On KILL (< 0.05): substrate compositional gen closed ❌; reframe
    to "interpolation within K-gram window" as honest product story.

- **Research (this session, future cycles)**: R20 closes ✅ with
  ready-to-build experiment spec. Remaining HIGH PRIORITY R# from
  cycle 27 followup: **R23** (continuous RSB / AT line, HIGH),
  **R24** (FDT violation, HIGH), **R29** (ferromagnetism, user-
  explicit HIGH). Per Strategy ordering: R20/R23/R24 first; R29
  next.

**HONEST FINAL NOTE (per [[feedback-no-smoke]])**: substrate's
predicted compositional generalization outcome is **PARTIAL PASS in
the kernel-bound regime** (P ≈ 45-60%). This is the predicted
Lippl-Stachenfeld behavior; not a failure but a characterization.
If experiment lands STRONG PASS, substrate has partially defeated
the kernel bound — substrate-novel. If experiment lands KILL,
substrate exhibits canonical compositional failure consistent with
fixed-feature kernel models. Per [[feedback-no-papers-product-only]]:
product story remains valid regardless ("interpolation within
byte-K-gram window with auditable provenance"); publishability is
side-effect of STRONG PASS only.
