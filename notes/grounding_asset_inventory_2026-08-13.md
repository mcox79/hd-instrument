# Grounding asset inventory — non-linguistic anchors (2026-08-13)

READ-ONLY reconnaissance. No code modified, no experiment run, nothing committed. Only three
module **self-tests** were executed (permitted); every other number is read off disk as recorded
by the original run.

Trigger: `notes/downstream_bottleneck_trace_2026-08-13.md` — the meaning read-out can only ever
name ~6% of corpus vocabulary because candidates enter only via seed vocabulary or the failing
loop itself. Every meaning is a word defined by another word. Question: do we own anything that
anchors outside language?

**Tooling note for whoever follows:** the `Glob` tool returned "No files found" for
`data/exp_visual_grounding_coherence_v1*/**` when those directories **do exist and are populated**.
It also ignores its `path` parameter and floods with `.venv` hits. Do not trust a negative Glob
result in this repo. Every finding below was re-derived with `Get-ChildItem` / `Read` / `Grep`.

---

## 0. TOP-LINE

**Yes, the image→hypervector work exists. It ran. It HARD_PASSED. Its VET was UPHELD and it was
graduated to a scope-bounded chain-grade. Then it was parked, and it has never been registered,
never been promoted to `hdlab/`, and its own named follow-up ("bind into concept-atoms") was
never done.** All three modules I self-tested still run today.

There are in fact **two independent image→hypervector families**, not one, and they have opposite
compatibility properties:

- **CLIP-scaffolded FHRR** — the strong result, the *incompatible* representation (complex128, N=4096, CLIP-derived basis).
- **Substrate-native HDC** — a weaker/narrower result, the *compatible-in-kind* representation (bipolar ±1, built from `hdlab.binding` primitives).

**Neither produces a vector that lives in `ConceptSpace`'s space.** `ConceptSpace` is
**d = 256, real, bipolar-signed, and its basis is a per-word-STRING sha256 hash**. There is no
content in that basis at all. A perceptual vector cannot be dropped in; the cosine would be
meaningless. This is the load-bearing negative finding of this inventory.

But there is a route that needs **no vector bridge at all** — see §4c. The image encoders'
primary output is not really a vector, it is a **word label proposed from pixels**. That is a
*generative* anchor, and it lands directly on the live revival criterion (b) of the shelved
sensorimotor work.

---

## 1. THE IMAGE→HYPERVECTOR WORK

### 1a. Provenance / scoping

`notes/scope_visual_grounding_early_reader_words_substrate_native_2026-07-18.md` (195 lines).
A genuine scoping drill. Names two arms explicitly: **(a) CLIP-class encoder as ingest
scaffolding** [recommended first], **(b) HDC-native patch/level encoding** [held as cell 2,
"optimize-then-nativize"]. Both arms were subsequently built. Arm (b) was built for a different
dataset than the scope note anticipated, so the two never met.

### 1b. Arm (a) — CLIP-scaffolded FHRR — **RAN, HARD_PASS, VET-UPHELD**

| field | value |
|---|---|
| cell | `experiments/exp_visual_grounding_coherence_v1.py` (762 lines) |
| metrics | `data/exp_visual_grounding_coherence_v1/metrics.json` |
| commit | `ed5e1cc9e` "exp: visual_grounding_coherence_v1 FULL HARD_PASS (foreground-local, glass-box runtime)" |
| ran | 2026-07-18T13:50:41Z, mode=full, elapsed 164.96 s, CPU, $0 |
| **self-test today** | **PASS (7.91 s)** — `SELF-TEST PASS: fhrr bind/unbind/cleanup/scene, spearman, projection-preserve, npy-parse, arms-differ, wordnet map` |

Verdict `HARD_PASS`. All four gates true, `shuffled_collapsed` true, `arms_differ_verified` true.

| test | result | control | chance |
|---|---|---|---|
| T1 picture→word top-1 (cross-modal) | **0.635** | shuffled 0.074 | 0.050 (K=20) |
| T1a image→image anchor top-1 | 0.756 | — | 0.050 |
| T2a coherence ρ vs WordNet Wu-Palmer | **0.353** | null p95 = 0.117, null mean −0.0017, z = 5.03, empirical p = 0.000 (500 perms) | — |
| T2b confusable 2-way (vision) | **0.882** | dictionary-only pinned 0.500 → **add-delta +0.382** | 0.500 |
| T3 scene-rep 2-object recovery | 1.000 | wrong-key 0.045 | 0.050 |
| FHRR-projection preservation ρ | 0.984 | — | — |

**VET outcome** (from `notes/director_BACKUP_ARCHIVE_full_session_chronology_2026-07-22.md`):
> "**VISION (Track B) GRADUATED = scope-bounded CHAIN-GRADE (VET a6ae09b4 UPHELD, atom 29310) = FIRST new CG of the reading arc** (prior CGs all memory). Genuine earner = the COHERENCE (perceptual CLIP-grounding COHERES with INDEPENDENT WordNet structure rho=0.35, z=5.0, LOO-robust [0.31,0.46], while retaining useful independent variance) — **NOT** the T2b 'beats dict-only'."

VET caveats recorded at the time, which still stand:
- coherence is against a **WordNet-taxonomy PROXY, not live concept-atoms**. The named follow-up was *"bind into atoms"* — **never done**. That follow-up is precisely the ConceptSpace bridge.
- K=20 is small.
- T3=1.000 was **author-flagged as a CONSTRUCTION-PROOF at K=2, not a win**. Do not cite T3 as a capability.
- sketch modality was *not* the limiter; photos would be stronger.

Then: *"Track B vision = graduated scope-bounded CG (parked)."* That is where it stopped.

**Data is ON DISK — nothing needs re-downloading.** `data/exp_visual_grounding_coherence_v1_cache/`,
24,405,120 bytes total:
- 20 × `qd_<word>.npy` @ 196,128 B = 250 × 28 × 28 uint8 QuickDraw sketches per word = **5,000 sketches**
- 20 × `clip_<word>.npy` @ 1,024,128 B = 250 × 512 float64 CLIP embeddings per word

Words (all 20 validated present, `dropped_words_404: []`): cat, dog, hat, fan, sun, duck, bird,
fish, tree, star, moon, apple, hand, book, key, cup, house, car, horse, pig.
(`ball` was removed by the cell author — not a live QuickDraw category; the staging MANIFEST
listed it optimistically.)

**Encoding chain:** QuickDraw 28×28 uint8 → PIL 3-channel resize 224 → CLIP ViT-B/32
`get_image_features` → 512-d L2-normalized → **per-modality mean-centering** (Liang et al. 2022
modality-gap fix; the cell notes this was a caught false-negative: cross-modal similarity
0.13→0.77) → fixed random projection `R = γ·N(0,1)`, shape (4096, 512), γ = 0.694 from median
pairwise distance → `exp(iθ)` → **FHRR phasor, complex128, N = 4096**.

Glass-box invariant is honoured: CLIP/WordNet/QuickDraw are touched **only at ingest**; all of
T1/T2/T3 runs on numpy bind/unbind/cosine-argmax with no torch.

### 1c. Arm (b) — substrate-NATIVE HDC image encoder — **RAN, PASS**

| field | value |
|---|---|
| cell | `experiments/exp_image_hd_encoder_digits_v1.py` (25,161 B) |
| metrics | `data/exp_image_hd_encoder_digits_v1/metrics.json` |
| data | sklearn `load_digits` (8×8, 10 classes, 1257 train / 540 test) — **not** early-reader vocabulary |
| **self-test today** | **PASS** — `thermometer-monotonic, bit-identical-to-bsc_primitives, toy-record-acc=1.000, scramble-fires(0.700), fixed-global-isomorphism(1.000), arms-differ` |

| arm | test acc |
|---|---|
| **HD_record** (position⊗level, bundled) | **0.907** |
| HD_scramble (per-image position permutation) | 0.107 — **collapsed**, delta 0.800 |
| HD_value_only (no position binding) | 0.196 |
| HD_fixed_global (isomorphism check) | 0.911 — confirms global perm is a no-op, as it must be |
| pixel_kNN / pixel_linear (reference ceilings) | 0.985 / 0.961 |
| 2D position recovery by unbinding | 0.993 (chance 0.059) |

Config: **N = 10000 bipolar**, Q = 17 thermometer levels, 64 grid positions.
**Uses `hdlab.binding.bsc_bind` / `bsc_bundle` and `hdlab.iterative_attractor.iterative_cleanup`,
with the vectorized path verified bit-identical to the primitives in self-test.** No CLIP, no
torch model, no external encoder. This is the fully glass-box front-end.

This is **the representationally compatible one** and it has never been pointed at word-grounding.

### 1d. McGuffey woodcuts — real reader illustrations, on disk

The 07-18 scope note said McGuffey illustrations were **"EXTRACTION-BLOCKED"** (PG editions carry
only `[Illustration: caption]` text placeholders). **That was subsequently solved.**
`data/exp_textbook_extract_mcguffey_v1/figures/` holds **102 real PNG woodcuts** segmented from
page scans (plus 3 in `sample/`, 105 total in that tree), alongside
`mcguffey_first_structured.json` (159,277 B) and `mcguffey_first_document_order.txt` (39,387 B).

| cell | verdict | numbers |
|---|---|---|
| `exp_reader_image_word_grounding_v1.py` (36,484 B) — **keyed** word↔image | `PASS_GROUNDING` | n_clean = **112** pairs, chance 0.0169; rung1_raw 0.996, rung2_edge 1.000, rung2b_ink 0.977, scramble delta 0.970. **N-STRESS at f=0.40, acc@N=125: raw 0.254 / edge 0.175 / ink 0.299** |
| `exp_reader_image_content_recognition_v1.py` (31,676 B) — **keyless** content recog | `GLASSBOX_RECOG_CONTENT_SENSITIVE` | weaker; the cell's own docstring: multi-object scenes + noisy labels + tiny per-class N; "glass-box woodcut recognition needs MORE (resonator scene-factoring...)" |
| `exp_reader_image_shape_recognition_hog_v1.py` (30,959 B) | `GLASSBOX_SHAPE_RECOG_STRONG` | on **clean/synthetic** images, not woodcuts |

`exp_reader_image_word_grounding_v1 --self-test` today: **PASS**
(`involution, bit-identical-bsc, edge-suppresses-bg+contour-concentrated, round-trip(acc=1.000), scramble-fires(0.000), arms-differ`).

**Be blunt about the N-STRESS row.** The headline 0.996 is at small load. At 125 items with 40%
distractors it falls to 0.175–0.299. The woodcut channel does **not** currently scale, and the
best feature front-end flips (ink beats edge under load, edge beats ink at small N). This is a
real result but it is a small-N result.

### 1e. Other perceptual cells (complete list, verdicts as recorded)

| cell | verdict | read |
|---|---|---|
| `exp_perception_bridge_scene_vector_digits_v1` | `PASS` | pixels→scene-vector→query→symbol grounding. xmodal_symbol 1.000, loc↔concept 1.000 at small K; **capacity K1→K36 degrades 1.000→0.648**, resonator setacc 0.800→0.312. scramble 0.124, wrongkey 0.091 |
| `exp_reader_perception_meaning_grounding_v1` | **`AWARE_USES_CONTENT_BUT_NO_GROUNDING_LIFT`** | **negative.** olivetti 40-class: aware(hog) 0.232 *below* blind(raw) 0.317, aware−blind = **−0.085** |
| `exp_reader_perception_meaning_grounding_soft_shard_v1` | `SOFT_SHARD_RECOVERS_GROUNDING_LIFT_STRONG` | sparse keyless store recovers the lift: best aob +0.093, i2w hog 0.825, D=32768, sparsity 0.20, controls_ok |
| `exp_reader_perception_meaning_grounding_sharded_v1` | (sharded variant) | hard-shard aob 0.123 |
| `exp_image_schema_codebook_cpu_v1` | `HARD_PASS` | grounding 1.000, cross-domain purity 1.000 — but a **SYNTHETIC codebook** of Lakoff/Johnson primitives |
| `exp_image_schema_real_cpu_v1` | **`HARD_FAIL`** | **the same idea on real abstract concepts: cluster purity 0.342.** "polysemy is the killer; synthetic primitive does NOT survive real abstract concepts" |
| `exp_substrate_sq3_structured_image_retrieval_v1_n2048` | `MIDDLE_BAND` | structured capacity M_crit 100, ratio 1.00 |
| `exp_substrate_cross_modal_binding_visual_auditory_v1` (seeds 7/13/19) | ran 2026-06-28 | synthetic modality vectors, not real sensor data |

**`exp_image_schema_real_cpu_v1` is a genuine recorded dead end** and should not be rediscovered:
image-schema grounding of *abstract* concepts collapses on real data. It says nothing about
concrete-noun grounding, which is what §1b/§1d actually do.

---

## 2. NON-LINGUISTIC ASSET INVENTORY (row counts verified off disk today)

| asset | path | size | rows | live consumer? |
|---|---|---|---|---|
| Lancaster sensorimotor norms | `data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv` | 17,196,336 B | **39,708 lines** (39,707 words × 11 modality dims) | `hdlab/grounded_similarity.py` — **registry line 115, `integration_status: WIRED`, but `pipeline_status: WIRED_BUT_NOT_PIPELINE_REACHABLE`** |
| Brysbaert concreteness | `data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt` | 1,646,191 B | **39,955 lines** | same module |
| Warriner valence/arousal/dominance | `data/grounding_testbed/Ratings_Warriner_et_al.csv` | 3,722,885 B | **13,916 lines** | **none found** |
| Kuperman age-of-acquisition | `data/grounding_testbed/AoA_51715_words.csv` | 3,524,642 B | **51,716 lines** | **none found** |
| **Binder 2016 experiential attributes** | `data/corpora/binder/binder2016_ratings.csv` | 357,370 B | **536 lines** (535 words) × **65 brain-system dims** (Vision, Bright, Motion, Biomotion, Touch, Temperature, Audition, Taste, Smell, UpperLimb, Path, Near, Harm, Arousal, ...) | 2 cells; see below |
| Binder aux | `data/corpora/binder/{word_ratings,queries,word_similarity}.zip`, `WordSet1_Ratings.xlsx` | ~2.4 MB | — | — |
| CSKG commonsense graph | `data/grounding_testbed/cskg.tsv.gz` | 112,312,195 B | **6,001,531 rows**, ~5.95M edges, ~2.16M nodes | testbed input only; gitignored, NOT canonical |
| QuickDraw sketches | `data/exp_visual_grounding_coherence_v1_cache/` | 24,405,120 B | **5,000 images**, 20 categories | §1b only |
| McGuffey woodcuts | `data/exp_textbook_extract_mcguffey_v1/figures/` | — | **102 PNGs** | §1d only |
| `word_image_early_vocab` staging | `data/corpora/word_image_early_vocab/` | ~4 KB | **MANIFEST.json + PROVENANCE.md ONLY — no bitmaps** | superseded; the actual bitmaps live in the exp cache above |

**On `data/corpora/word_image_early_vocab/` specifically** (the task named it as a likely lead):
it is a **2-file license-cleared fetch manifest, not a dataset**. `MANIFEST.json` lists 21
recommended categories, 6 confusable pairs, 200 exemplars/category, and the GCS URL pattern.
`PROVENANCE.md` documents CC-BY 4.0 for QuickDraw, a staged photo-upgrade path (Open Images V7
CC-BY 2.0 / Wikimedia PD), and an explicit **license hazard note deliberately excluding CIFAR-10 /
COCO / Tiny-ImageNet** (permissive top license, murky per-image provenance). The images it points
at were pulled and are cached — so the manifest has already served its purpose.

**Binder is the most interesting unexploited asset and its headline cell never completed a full
run.** `experiments/exp_native_meaning_encoder_binder_grounded_v1.py` has **no
`data/exp_native_meaning_encoder_binder_grounded_v1/` directory** — only `_smoke`. The smoke
verdict is a recorded negative:
> `CONTEXT-CARRIES-distributional-to-grounded` — "CONTEXT-ONLY carries the signal (context_only p@10=0.2426 > relations_only 0.139 by 0.1036). The generalization is DISTRIBUTIONAL-to-grounded projection (native Feature2Vec) — honest, but this is NOT the brain-grounded-from-relations result and is the weaker/less-brain-consistent lever."

That cell's own docstring also records a hard coverage finding worth not re-deriving: **0 of 2264
WorldTree v2 items are fully Binder-grounded, and only ~6% of candidate values have Binder
vectors.** Binder's 535 words is a real ceiling. Other Binder consumers:
`exp_grounding_tem_factorized_heldout_concept_v1` (`MIDDLE_BAND_..._STRUCTURE_TRAINING_NOT_THE_LEVER`,
random-bind 0.836 vs factorized 0.837 — i.e. structure was **not** the lever),
`exp_propara_schema_learned_grounded_binder_v1` (`HARD_PASS`, but msg is only `SELFTEST_PASS`),
`exp_wave14_binder_ratio_v1` (`BINDER_RS_CONFIRMED` — this is HD "binder" as in binding ratio, an
unrelated name collision, **not** the Binder norms).

---

## 3. CAPABILITY REGISTRY + PRIOR VERDICTS

`data/capability_registry.jsonl` — **123 entries** (read only, unmodified).

**There is NO registry entry for any image / visual / perceptual / CLIP / QuickDraw capability.**
A direct search for `visual_grounding | quickdraw | clip | image_word` returns nothing. The only
grounding-adjacent entry is:

- **line 115** `grounded_similarity_perceptual_fallback_organ` — `hdlab/grounded_similarity.py`,
  Lancaster + Brysbaert as an **additive fallback** to `lexical_similarity`, never replacing it.
  `gate_decision: WIRE`, `integration_status: WIRED`, 5 measured consumers,
  **`pipeline_status: WIRED_BUT_NOT_PIPELINE_REACHABLE`**.
  (line 58 matched only on the substring "perceptron"; it is a thematic-role assigner, irrelevant.)

**Correction to the task brief:** the norms are described there as "established as UNWIRED from
the meaning path". More precisely — they are **WIRED as a module dependency but NOT
PIPELINE-REACHABLE**. The registry's own field says so. The practical consequence is the same
(nothing on the live meaning path calls them), but the module exists and works, so a future use
does not start from zero.

**So: a VET-upheld chain-grade capability (§1b) never passed through the WIRE-or-SHELVE gate at
all.** It is neither wired nor shelved — it is in exactly the limbo the gate exists to prevent.
`hdlab/` contains **no** image/visual/perceptual module; the only grounding-named modules are
`grounded_similarity.py`, `grounding_acquisition_loop.py`, `reading_grounding_loop.py`,
`idiom_grounding.py`, `context_grounded_valence.py`, `goal_outcome_relation_grounded.py` — all
text/lexical.

### Prior grounding attempt already SHELVED, and why

`notes/sensorimotor_anchoring_scope_2026-08-13.md` — **SHELVED** by Director decision.

Reason (accepted "in its strong form"): coverage is **not** the blocker. The norms cover the
NOISE rows *at least as well as* the good rows (text_vs_mechanism NOISE 0.740 vs non-NOISE 0.640;
readout_v1 NOISE 0.641 vs RELATED 0.684). **"A filter cannot create meaning that a 2–3%
MEANINGFUL generator never produced."**

Retained evidence (do not re-derive): on 124 both-covered blind pairs, NOISE sits on the
random-word-pair Lancaster floor (**0.8071 vs 0.8060**) while non-NOISE sits at **0.8834**,
one-sided permutation p = 0.0012 (20k shuffles); AUC 0.685, **in-sample** (threshold picked on the
same rows). Also recorded so nobody re-measures it: **Lancaster and Brysbaert are near-perfectly
nested** — owning both buys ~nothing over one; and the uncovered residue is ~75% proper nouns plus
technical terms, i.e. exactly what no lexical norm table will ever cover.

**REVIVAL CRITERIA, verbatim:**
> (a) A read-out is achieved that produces a materially higher MEANINGFUL rate.
> (b) **Sensorimotor grounding is needed as a *generative* anchor rather than a filter — with a mechanism that *proposes* candidate bindings rather than *scoring* pre-existing ones. A proposing mechanism is a different object from M1/M2/M3 above and would need its own brain-fidelity siting (shape + position + metric), not a threshold.**

**Criterion (b) is live, and §1b/§1d bear on it directly.** T1 of `exp_visual_grounding_coherence_v1`
is *picture → word*: it **proposes** a word from pixels at 0.635 top-1 over 20 words (12.7× chance,
shuffled control 0.074). `exp_reader_image_word_grounding_v1` proposes across 112 McGuffey
word↔image pairs at 0.996 (chance 0.0169). These are **generators, not scorers** — structurally
the object criterion (b) asks for. Neither has ever been sited brain-fidelity-wise (shape +
position + metric), which is the work criterion (b) also demands and which this recon does not do.

---

## 4. COMPATIBILITY WITH `ConceptSpace` / `hd_fact_store` — THE KEY QUESTION

### 4a. What the targets actually are

**`ConceptSpace`** — `hdlab/reading_grounding_loop.py:405`:
- `numpy`, `float64`, dimension `d = CTX_D`, and **`CTX_D` is imported as `D` from
  `hdlab/grounding_acquisition_loop.py:79`, where `D = 256`** ("context bipolar vector
  dimensionality").
- A concept is `self._sums[lemma]` = a running **sum of context vectors**; `bundle()` /
  `anchor_matrix()` return `np.sign(...)`, i.e. **bipolar ±1 in 256 dims**.
- A context vector is (line 1849-1851) `acc = zeros(CTX_D); acc += symbol_vector(w, CTX_D)` over
  content words — a **bag-of-words sum of random codes**.
- `symbol_vector` (line 255-268) is
  `sha256(word)[:8] → seed → default_rng(seed).choice([-1,1], d)`.

**That last line is the crux. The basis of `ConceptSpace` is a hash of the word's SPELLING.**
There is zero content in it. Two words are similar iff they co-occur with the same *other word
strings*. This is exactly the closed loop the bottleneck trace describes.

**`HDFactStore`** — `hdlab/hd_fact_store.py:138-203`: `torch`, **bipolar**, `n_dim` default
**8192**, symbol vectors from `codec._sym_vec(sym)` — again **derived from the symbol's name**,
via a deterministic codebook. Same structural problem.

### 4b. What the encoders produce — verdict: INCOMPATIBLE

| | ConceptSpace | Arm (a) CLIP-FHRR | Arm (b) native HDC |
|---|---|---|---|
| library | numpy | numpy | numpy / `hdlab.binding` torch |
| dtype | float64 → sign ±1 | **complex128 phasor** | **bipolar ±1** |
| dim | **256** | **4096** | **10000** |
| basis | sha256(word string) | random projection of CLIP-512 | random position ⊗ thermometer-level codes |
| comparable by cosine to a ConceptSpace anchor? | — | **No** (complex; different dim; unrelated basis) | **No** (different dim; unrelated basis) |

- **Arm (a) is incompatible on all three axes** — dtype, dimension, and basis. `fhrr_cos` on a
  complex phasor vector and `np.sign` cosine on a real bipolar vector are not the same operation
  and the two spaces share no axes. It cannot supply a ConceptSpace anchor without a bridge.
- **Arm (b) is compatible in KIND but not in COORDINATES.** It is bipolar, sign-bundled, and built
  from the very primitives `hdlab` uses, so the *algebra* matches. Dimension is a config constant
  (N=10000 → 256 is a parameter change, though 256 is very small for a 64-position record code and
  crosstalk would need measuring). **The basis mismatch survives the dimension fix**: a vector
  built from position⊗intensity codes is near-orthogonal to a vector built from word-string
  hashes. Making them share a space is not a config change.

**Blunt statement: no encoder we own emits a vector that lives in `ConceptSpace`'s space, and
matching the dimension would not fix it.** Anyone who reports "we can just inject the perceptual
vector" has not looked at `symbol_vector`.

### 4c. The route that needs NO vector bridge (and why it is the interesting one)

`ConceptSpace` exposes a **public, existing injection API**:

```python
def seed_from_bundle(self, lemma: str, raw_sum: np.ndarray) -> None:
    """Seed (or overwrite) a lemma's accumulator directly from an already-computed raw sum
    (used at grounding time: the sum of a Library item's own trace context vectors)."""
```

The class docstring says a newly-GROUNDED word is "seeded ONCE at grounding time from the bundle
of their own accumulated Library traces… **This is what lets the foundation's CONCEPT SPACE grow**".

So the existing grounding act is: *decide a word is grounded → seed its anchor from its own text
traces.* The gate is **the decision**, not the vector.

**The image encoders' real output is a decision: a word label, from pixels.** T1 returns a word.
`exp_reader_image_word_grounding_v1` returns a word. If the perceptual channel is used as the
**admission criterion** — a word earns an anchor because a picture of it was correctly recovered,
not because another word co-occurred with it — then:
- no vector bridge is needed, only the label;
- `seed_from_bundle` is called on the existing text traces, unchanged;
- the anchor's *content* is still distributional, but its *admission* is now non-linguistic,
  which is precisely what breaks the "candidates enter only via seed vocabulary or the failing
  loop" closure.

That is an honest, small, buildable move. **It is also strictly weaker than real perceptual
grounding** and must not be described as "we grounded meaning in perception" — the vectors would
still be bags of words. The scoping note's own §2 line applies: the forbidden move is letting a
table (or here, an encoder) *be* the reasoning organ; the permitted move is letting it supply a
fact. Admission-by-picture is a fact supply. It should be pre-registered as such, and the
overclaim pre-empted, exactly as the sensorimotor note recommended for itself.

**Coverage is the brutal limit on this route: 20 QuickDraw words, 112 McGuffey pairs, ~59 clean
McGuffey classes.** Against a 6%-of-corpus-vocabulary problem measured in thousands of types, a
20-word generative anchor is a mechanism demonstration, not a fix. QuickDraw has 345 categories
total (only 21 were staged, one of which did not exist), and the photo-upgrade path (Open Images /
Wikimedia PD) is staged but never pulled — so the ceiling is raisable, but nobody has raised it.

---

## 5. RANKING — what could actually supply non-linguistic anchors

Criteria: (i) genuinely non-linguistic? (ii) works today? (iii) cost to connect to `ConceptSpace`?

**1. `exp_visual_grounding_coherence_v1` (CLIP→FHRR, QuickDraw).** *Genuinely non-linguistic:
YES — pixels.* *Works today: YES* (HARD_PASS on disk, VET-upheld, self-test PASS, all 5,000 images
+ CLIP embeddings cached so it re-runs offline). *Cost to connect:* **low via the label route
(§4c), high via the vector route.** Covers **20 concrete nouns**. The strongest asset we own and
the only one whose grounding claim survived an independent VET. Its named follow-up ("bind into
concept-atoms") is still open and is the exact bridge question. Caveats that are load-bearing:
K=20; coherence measured against a WordNet *proxy* not live atoms; T3 is a construction proof, not
a win; CLIP is an external encoder used as ingest scaffolding (permitted under the pivot, but it
means the *shared space* is CLIP's, not ours).

**2. `exp_reader_image_word_grounding_v1` (McGuffey woodcuts).** *Non-linguistic: YES.* *Works
today: YES* (self-test PASS, 102 real PNGs on disk). *Cost: low via the label route.* Covers
**112 word↔image pairs** from the actual reader corpus we ingest — better *aligned* to the reading
loop than QuickDraw. **But the N-STRESS numbers (0.175–0.299 at 125 items / f=0.40) say it does
not hold up at load, and the woodcuts are multi-object scenes with OCR-derived noisy labels.**
Ranked second on strength, arguably first on relevance.

**3. `exp_image_hd_encoder_digits_v1` (substrate-native HDC).** *Non-linguistic: YES.* *Works
today: YES* (PASS, self-test PASS, verified bit-identical to `hdlab` primitives). *Cost to
connect: medium — the only asset whose algebra already matches the substrate.* **But it has never
been pointed at words at all** — it classifies handwritten digits. It is the right *front-end* with
no *grounding* attached. The scope note held it as "cell 2, optimize-then-nativize"; that cell was
never written. This is the highest-leverage unbuilt thing here, and it is the brain-faithful arm,
not the scaffolded one.

**4. Binder 2016 experiential attributes (535 words × 65 brain-system dims).** *Non-linguistic:
PARTIALLY — human ratings of experience, not experience; the same objection §3 raises against
Lancaster applies, though Binder's dimensions are brain-system-derived rather than introspective
modality scales.* *Works today: PARTIALLY* — the headline cell **never completed a full run**
(smoke only) and the smoke result is a recorded negative (context, not relations, carried the
signal; the generalization was distributional→grounded projection). *Cost: unknown.* 535 words is
a hard ceiling and the recorded WorldTree overlap is ~6%.

**5. Lancaster (39,707) + Brysbaert (39,954).** *Non-linguistic: NO — "3,000 undergraduates'
verbal introspection about perception, encoded as 11 numbers, distributed as a text file"
(scoping note's own words).* *Works today: module works, not pipeline-reachable.* **SHELVED
2026-08-13 as a filter.** Only revivable under criterion (b), as a *generative* mechanism — which
they structurally are not: a ratings lookup scores an existing pair, it cannot propose one from
sensory input. **Do not re-open these as an anchor source.** Their retained value is diagnostic
(the random-floor result).

**6. Warriner (13,916) and Kuperman AoA (51,716).** Large, on disk, **no consumer found anywhere**.
Same class as #5 — introspective lexical ratings, not perception. AoA is arguably useful as a
*curriculum ordering* signal rather than an anchor. Neither is a grounding asset. Listed for
completeness so nobody counts them as one.

**7. CSKG (6,001,531 rows).** Contains Visual Genome among its merged sources — but as a
**graph of labels**, not pixels. It is more language. It does not anchor outside language and
should not be ranked as if it does.

**Explicitly NOT recommended / recorded dead ends:**
- `exp_image_schema_real_cpu_v1` — **HARD_FAIL**, purity 0.342, "polysemy is the killer". Its
  synthetic sibling's HARD_PASS (purity 1.000) is construction-determined. Do not revive the
  image-schema route for abstract concepts.
- `exp_reader_perception_meaning_grounding_v1` — content-aware encoding was **worse** than
  content-blind (−0.085). The soft-shard variant recovered it (+0.093) but at D=32768 with a
  sparse keyless store, which is a storage fix, not a grounding result.
- `data/corpora/word_image_early_vocab/` as a "dataset" — it is a 2-file manifest, already
  superseded by the populated cache.
- Any plan that "just injects the perceptual vector into ConceptSpace" — see §4b.

---

## 6. WHAT I COULD NOT VERIFY

- **I did not re-run any full experiment.** Every accuracy/ρ/verdict above is read off the
  `metrics.json` written by the original run. I verified the files exist, are parseable, and
  contain the numbers quoted. I did **not** independently recompute any of them. Only the three
  **self-tests** in §1b/§1c/§1d were actually executed today.
- **The VET (a6ae09b4 / atom 29310) was not independently checked.** The "UPHELD", the LOO-robust
  ρ range [0.31, 0.46], and the "genuine earner is the coherence, not T2b" framing all come from
  the narrative in `notes/director_BACKUP_ARCHIVE_full_session_chronology_2026-07-22.md`. I did
  not open the atom in the store or locate a standalone VET note. **Treat the VET status as
  reported-not-verified.**
- **I did not test whether `exp_visual_grounding_coherence_v1` still runs END-TO-END.** Self-test
  passes and the caches are present, so a re-run should not need network — but I did not run the
  `--smoke` or full path, and I did not confirm `transformers`/`CLIPModel` still loads in the
  current `.venv`. (The BACKUP doc records an environment gotcha: a stray
  `C:\...\Temp\inspect.py` shadows stdlib if a cell is run from `/tmp`; run cells from the project
  dir.)
- **I did not verify the QuickDraw URLs still resolve.** Irrelevant for re-running the cached 20
  words; relevant if anyone tries to expand to more of QuickDraw's 345 categories.
- **The 256-dim claim for `ConceptSpace` rests on a single import chain** (`reading_grounding_loop.py:87`
  imports `D as CTX_D` from `grounding_acquisition_loop.py:79`, `D = 256`). I did not check
  whether any live caller overrides `d=` at construction. If a caller passes a different `d`, the
  dimension mismatch numbers change — **the basis mismatch, which is the real problem, does not.**
- **I did not enumerate all ~150 `data/exp_grounding_*` directories.** I sampled the ones matching
  image/visual/perceptual/binder names. There may be perceptual work under a name I did not
  pattern-match.
- **`Glob` gave at least one confirmed false negative** (§0). Other assets may exist that neither
  my Glob nor my `Get-ChildItem` filters surfaced. The image inventory in §1 should be treated as
  "everything matching `*image*|*visual*|*percept*|*multimodal*` in `experiments/` plus what those
  cells import", not as an exhaustive proof of absence.
- **I did not touch `data/exp_frontier_distance/` or `data/exp_minimum_basis/`** (owned by
  concurrent agents), so nothing there is reflected here.
- **I did not assess whether the label-route in §4c would survive the control stack**
  (scramble / prior-lesion / ablation / no-leak / attribution). It is an untested proposal, and
  per standing discipline it is a hypothesis, not a finding.
- **I did not do the brain-fidelity siting (shape + position + metric)** that revival criterion (b)
  explicitly requires of any proposing mechanism. §3's claim is only that the existing cells are
  structurally *generators rather than scorers* — not that they are correctly sited.
