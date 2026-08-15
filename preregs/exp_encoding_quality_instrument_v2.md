# Pre-reg: `exp_encoding_quality_instrument_v2` (PLAN STEP 2 — score the PRODUCTION encoding)

STATUS: **PRE-REGISTERED BEFORE ANY v2 RUN.** Written to disk and committed before the v2 cell was
executed once. Supersedes nothing in `preregs/exp_encoding_quality_instrument_v1.md` — that file is
frozen and untouched. Every v1 threshold is carried forward VERBATIM so that the v1 gate set is a
clean REGRESSION CHECK on the two fixes below.

Serves `notes/PLAN_NEXT_12H.md` STEP 2 and component-table row 1
(`word/concept encoding | NONE - BUILD FIRST | unmeasured`).

---

## 0. WHY v2 EXISTS — the two defects v1 disclosed about itself

v1 (`4f6b54852`) reported `INSTRUMENT_VALIDATED`, 17/17 gates, and then disclosed two defects in its
own `DISCLOSURE` block. Both are fixed here, RECORDED, not silently. Neither fix touches any v1
threshold.

### FIX (a) — M4 STAGE-CHAIN used TWO criteria and therefore TWO chance levels

v1's five-stage chain measured `S0_ORACLE / S1_ENCODE / S2_ENCODE_SIGN` with a **top-1** criterion
(chance `1/N` = `1/1024`) and `S3_BUNDLE / S4_BUNDLE_SIGN` with a **top-8** criterion (chance
`8/1024`), then subtracted the resulting Fano bits across the `S2 -> S3` boundary as if they were
commensurable. They are not. The signature is visible in v1's own metrics: `A_COLLAPSE` shows
`destroyed_bits_vs_prev = -0.35` at that step — a null arm apparently GAINING information by being
bundled.

**The fix: one criterion for the whole chain.** All five stages now use the **top-`B` list
criterion** with `B = BUNDLE_B = 8` over a store of `N = N_GATE`:

| stage | representation | readout (IDENTICAL at every stage) |
|---|---|---|
| `S0_ORACLE` | one-hot over the vocabulary (`d = V`) | is the true word in the **top-8** by cosine? |
| `S1_ENCODE` | the encoder's own output, L2-normalised | same |
| `S2_ENCODE_SIGN` | `sign(S1)` | same |
| `S3_BUNDLE` | `S1` summed in groups of `B = 8` | same (against the bundle containing it) |
| `S4_BUNDLE_SIGN` | `sign(S3)` | same |

`S0/S1/S2` use a noisy probe at `sigma = SIGMA_GATE = 1.0` exactly as v1 did; only the top-1 -> top-8
criterion changes. `S3/S4` are unchanged.

**The bits conversion changes with it.** A top-1 Fano bound is wrong for a list-of-`B` decoder. v2
uses the **list-decoding Fano bound**:

```
I_list(p, n, B) = max(0, log2(n) - H_b(p) - (1-p)*log2(n-B) - p*log2(B))
```

Properties, all asserted in the cell's self-tests before any run:
- `B = 1` reduces EXACTLY to v1's `fano_bits` (the same formula).
- `p = 1` gives `log2(n/B)`; at `n=1024, B=8` the chain **ceiling is 7 bits, not 10**.
- `p = B/n` (chance) gives `~0` bits.
- monotone non-decreasing in `p`.

**Consequence for citation:** every v1 stage-chain number is on a 10-bit scale that mixed two
criteria. v2 numbers are on a 7-bit single-criterion scale. **v1 and v2 stage bits are NOT
comparable and must never be quoted side by side.** The v1 claim "bundling destroyed 7.80 of 10
bits" is superseded by whatever v2 measures on the corrected scale.

### FIX (b) — the pre-registered headline `sigma = 1.0` is SATURATED

v1 disclosed: at `sigma = 1.0` every non-degenerate arm scores recoverability `1.000` and
discriminability `1.000` at every `N` up to 4096. The metric separates a degenerate encoder from a
good one but **cannot separate two good encoders there**. The arms only spread at `sigma` in `[4,16]`.

**The fix: the headline is the SIGMA CURVE, not a point.**
- `HEADLINE_SIGMAS = [4.0, 8.0, 16.0]` is pre-registered as the reporting band, with
  `HEADLINE_SIGMA = 8.0` as the single reference point when one is needed.
- A new non-saturating scalar per arm, `sigma_half` = the `sigma` at which recoverability at
  `N_GATE` crosses `0.50`, by linear interpolation in `log2(sigma)` on the pre-registered grid
  (`None` if it never crosses; `>` the grid max if it never falls below). Monotone, one number,
  summarises the whole curve, cannot saturate.
- **`sigma = 1.0` remains the GATE point for every v1 gate, unchanged**, precisely so the v1 gate
  set stays a clean regression check. It is retired as the HEADLINE only.

---

## 1. WHICH ENCODER IS THE PRODUCTION ONE — established by RUNTIME evidence, not grep

`CLAUDE.md` Evidence discipline §2 (enumerate from the filesystem, then reconcile to the registry,
never the reverse) and §3 (prefer runtime evidence over static search). A previous session
mis-identified the encoder twice. This is how it was established this time.

**Step 1 — enumerate from disk.** `ls hdlab/` = **147 entries** (v1 recorded 141; the tree grew).
Full listing read. Modules whose NAME implies an encoder:
`char_positional_encoder`, `char_trigram_encoder`, `composed_encoder_v3`, `concept_encoder`,
`encoder_retrain_persist`, `gsbc_graded_encoder`, `hippocampal_encoder`, `kb_encoder_registry`,
`ppmi_sparse_encoder`, `random_indexing`, `token_vocab`, `vwfa` — **12 candidates.**

**Step 2 — runtime observation of the live path.** Import the two live entry points
(`hdlab.reading_grounding_loop`, `hdlab.grounding_acquisition_loop`) and diff `sys.modules`:
**40 `hdlab.*` modules load. NONE of the 12 encoder-named candidates is among them.** Not
`char_trigram_encoder`, not `concept_encoder`, not `random_indexing`, not `vwfa`.

**Step 3 — reconcile to the registry (never the reverse).** `data/capability_registry.jsonl` = 198
rows, 42 matching `encod`. Every encoder-named module carries
`pipeline_status = WIRED_BUT_NOT_PIPELINE_REACHABLE` — including `random_indexing_open_vocab_encoder`,
`char_trigram_encoder`, `concept_encoder`, `gsbc_graded_encoder`, `char_positional_encoder`.
The registry AGREES with the runtime observation. **And no registry row names the encoder that IS
live** — the production word encoder has no registry row at all, which is exactly the leak
`CLAUDE.md` §2 documents.

**Step 4 — what the live path actually does.** The production word code is INLINED, not imported:

```python
# hdlab/grounding_acquisition_loop.py, inside context_vector()
seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2**32)
rng  = np.random.default_rng(seed)
acc += rng.choice([-1.0, 1.0], size=d)
```

and is exposed verbatim as `hdlab.reading_grounding_loop.symbol_vector`. Verified at runtime:
`context_vector("aardvark") == symbol_vector("aardvark")` is `True` elementwise.

Live constants, read at runtime: `CTX_D = 256`, `grounding_acquisition_loop.D = 256`,
`GRADED_COMPARATOR = True` (raw un-quantised sums are the default since 2026-08-14).

**Therefore there are TWO production encodings, at two levels, and BOTH are scored here:**

| arm | what it is | why it counts as production |
|---|---|---|
| `P_LIVE_WORD` | `sha256(word) -> seed -> default_rng(seed).choice([-1,+1], d)` | the primitive per-word code. Literally `encode(word) -> vector` on the live path. |
| `P_LIVE_CONCEPT` | per-lemma accumulated sum of `context_vector_masked(sentence, lemma)` over every corpus sentence containing it — i.e. `ConceptSpace.bundle(lemma)` with `GRADED_COMPARATOR=True` | the learned concept profile the live comparator (`canonicalize_fast`) actually reads. This is where distributional structure could live. |

`P_LIVE_CONCEPT` is built by calling the live functions' exact math; the cell asserts the vectorised
construction is **byte-identical** to `reading_grounding_loop.context_vector_masked` on a sample of
real (sentence, lemma) pairs before using it, and records the sample size.

---

## 2. ARMS (v1 arms carried forward VERBATIM; new arms added)

Carried forward unchanged: `A_ORACLE_ONEHOT`, `A_RANDOM_IID`, `A_COLLAPSE`, `A_ORTHOGRAPHIC`,
`A_PLANTED_STRUCTURE`, `A_SHUFFLED_PLANTED`, `A_PLANTED_SEMANTIC`.

New:

| arm | construction | predicted IDENTITY | predicted STRUCTURE |
|---|---|---|---|
| `P_LIVE_WORD` | the live inlined sha256 -> bipolar draw | near-ceiling | **chance, by construction** |
| `P_LIVE_CONCEPT` | the live per-lemma graded context accumulation | unknown | **unknown — this is the question** |
| `C_CONCEPT_SHUFFLED` | `P_LIVE_CONCEPT`'s rows PERMUTED across words | identical to `P_LIVE_CONCEPT` | **must fall to chance** |

`C_CONCEPT_SHUFFLED` is mandatory and is the N5-class control applied to the production arm: without
it, ANY structure lift measured on `P_LIVE_CONCEPT` is unfalsifiable, because a code matrix with
frequency-correlated norms can produce apparent lift on a frequency-correlated gold with no meaning
in it at all.

**DIMENSION.** The instrument's pre-registered `D = 1024`; production runs at `d = 256`. A dimension
mismatch is a real confound on the IDENTITY axis (it is not on the STRUCTURE axis, where a null is
1.0 at any `d`). So **every arm is run at BOTH `d = 1024` and `d = 256`**, and every comparison in
the report is `d`-matched. `A_ORACLE_ONEHOT` runs at `d = V` at both settings, as in v1, and remains
NOT dimension-matched by construction.

> **AMENDMENT A3, made BEFORE any v2 run, on a measured memory constraint.** `P_LIVE_CONCEPT` and
> `C_CONCEPT_SHUFFLED` run at the **production-native `d = 256` ONLY**, not at `d = 1024`. Reason,
> measured not estimated: the live concept profile is accumulated over the symbol codebook for the
> FULL context vocabulary of the corpus, which is **251,087 unique content words** at
> `CORPUS_BYTES = 64,000,000`; that codebook is 257 MB at `d = 256` and **1,028 MB at `d = 1024``.
> Truncating the context vocabulary to fit would be a silent deviation from the production
> algorithm, which is worse than not running the variant. All SYNTHETIC arms and `P_LIVE_WORD` still
> run at both `d`, so the concept arm is compared against a fully `d`-matched `d = 256` family and
> no comparison in the report crosses dimensions. What is lost is only the counterfactual "how would
> the concept profile do with 4x the dimensions", which is not the question STEP 2 asks.

**LEMMA COLLISION.** The live path keys concepts by LEMMA, not surface form. Two vocabulary words
with the same lemma (`arteries`/`artery` -> `artery`) therefore receive the SAME production concept
code. This is a real property of the production system, not an artifact, and it will depress
`P_LIVE_CONCEPT` identity scores. It is reported as `n_lemma_collisions`, and identity is ALSO
reported restricted to collision-free words (`recoverability_collisionfree`) so the two causes are
never conflated.

---

## 3. GATES

### 3a. THE v1 GATE SET — carried forward VERBATIM, evaluated at `d = 1024`, `sigma = 1.0`, `N_GATE = 1024`

All 17: `N1 N2 N3 N4 N5a N5b N6a N6b` (NULL), `K1 K2 K3 K5` (KNOWN), `S1 S2 S3 S4` (SAT),
`K4` (KNOWN_SEMANTIC_READOUT_ONLY). Same thresholds, same arms, same evaluation points as
`preregs/exp_encoding_quality_instrument_v1.md` section 5. **No threshold is edited.**

**STOP CONDITION, binding:** if ANY null gate that passed in v1 stops passing, the verdict is
`INSTRUMENT_STILL_LOOSE` and **no production number is published.**

### 3b. NEW v2 gates — the two fixes must be demonstrated, not asserted

| id | family | condition | rationale |
|---|---|---|---|
| **M1** | CHAIN | min over ALL arms and ALL stage steps of `destroyed_bits_vs_prev` **>= -0.25** | the defect signature was `-0.35` on a null arm. One criterion must remove it. |
| **M2** | CHAIN | `A_ORACLE_ONEHOT` `S0` bits within `0.01` of `log2(N_GATE / B) = 7.0` | known-answer check on the new list-Fano bound |
| **M3** | CHAIN | `A_COLLAPSE` `S1` bits **<= 0.20** | the null arm must still carry ~no information under the new criterion |
| **SEP1** | SEP | at `sigma = 8.0`, `N_GATE`: `A_ORACLE_ONEHOT` recoverability minus `A_PLANTED_STRUCTURE` recoverability **>= 0.20** | the instrument must separate TWO GOOD encoders somewhere. This is the whole point of fix (b). |

Reported as a DIAGNOSTIC, not a verdict gate (it asserts a defect exists, and its failure would be
good news rather than instrument breakage): `SEP2_DIAG` = the same difference at `sigma = 1.0`,
expected `<= 0.05`, evidencing that the v1 headline point was saturated.

### 3c. VERDICT ORDER (no exceptions)

1. any NULL fails -> `INSTRUMENT_STILL_LOOSE`. **No production number published. STOP.**
2. else any of K1/K2/K3/K5 fails -> `INSTRUMENT_CANNOT_DETECT_QUALITY`. STOP.
3. else any SAT fails -> `INSTRUMENT_SATURATED`. STOP.
4. else any CHAIN fails -> `INSTRUMENT_CHAIN_DEFECT`. Production identity/structure numbers stand;
   stage-chain numbers are withheld.
5. else any SEP fails -> `INSTRUMENT_CANNOT_SEPARATE_TWO_GOOD_ENCODERS`.
6. else -> `INSTRUMENT_VALIDATED`, `semantic_readout_validated = (K4 passed)` reported separately.

---

## 4. THE QUESTION v2 ANSWERS, and the answer format (fixed before the run)

**TWO AXES, REPORTED SEPARATELY. NO SINGLE SCALAR.** v1's load-bearing finding is that any scalar
mixing identity and structure is unfalsifiable. v2 therefore reports a position on each axis
independently and **explicitly refuses to average them.**

- **IDENTITY** — recoverability + discriminability. `A_COLLAPSE` is the floor, `A_ORACLE_ONEHOT` the
  ceiling, and **a random encoding is near-OPTIMAL here by design.** Scoring high on this axis is
  therefore NOT a win and may not be reported as one.
- **STRUCTURE** — gold AP lift + SimLex rho. `A_RANDOM_IID` / `A_SHUFFLED_PLANTED` /
  `C_CONCEPT_SHUFFLED` must all sit at `~1.0` / `~0.0`. **Any real lift here is the actual signal.**

**THE TRADE-OFF, priced.** v1's synthetic arms predicted that structured codes buy structure by
paying in identity: `A_PLANTED_STRUCTURE` recoverability `0.592` vs `A_RANDOM_IID` `1.000` at
`sigma = 4`, and `7.8` bits of `10` lost to bundling where random lost `0`. v2 places both production
arms on that same trade curve, using the corrected 7-bit chain scale, and reports where they sit.
The bundling stage (`S2 -> S3`, THE SUM) is called out separately because it bears directly on the
flat-store question.

---

## 5. WHAT v2 STILL DOES NOT MEASURE (stated before the run)

Carried forward from v1 section 6, all still true:
- Meaning beyond SimLex-999 pair similarity. `GOLD_ORTHO` / `GOLD_FREQBAND` are surface and
  statistical golds — validity scaffolding, not meaning. No WordNet, ConceptNet or human category
  gold is wired.
- Compositionality, binding, roles, polysemy, context-sensitivity. One word -> one static code.
- Anything downstream: no store, no reader, no selection, no retrieval index. By design.
- `A_ORACLE_ONEHOT` runs at `d = V`, not dimension-matched.
- Fano numbers are LOWER BOUNDS on retained information, not estimates.
- `K4`'s arm is fitted BY GRADIENT DESCENT TO THE SIMLEX GOLD. Circular by design; its rho may
  never be quoted as a quality result.

New to v2:
- `P_LIVE_CONCEPT` is built over `simplewiki` at `CORPUS_BYTES`, which is NOT the corpus the live
  foundation was actually grown on. It is the production ALGORITHM on the instrument's corpus, so
  that the vocabulary, golds, sigmas and seeds are identical across arms. It is not a snapshot of
  any persisted production store, and `data/foundation/**` is never opened.
- The `StructuralEncoder` role-bound path (`process_sentence(encoder=...)`) is DEFAULT-OFF on the
  live path and is NOT scored here.

## 6. RESOURCES

CPU only, numpy, single-threaded (`OMP_NUM_THREADS` pinned in-file before the numpy import).
No GPU, no queue dispatch, no network, no `data/foundation/**` read. Per-unit checkpointing via
`tools/exp_checkpoint.py`, unit key = `(arm, d, seed)`. The concept-profile build is cached to
`concept_profiles_d<d>.npz` in the output directory so a resumed run does not rebuild it.
Output `data/exp_encoding_quality_instrument_v2/metrics.json` (smoke: `..._smoke/`).
