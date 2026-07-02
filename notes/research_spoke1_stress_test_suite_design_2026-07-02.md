# Spoke 1 v3-D stress-test suite design

**Filed:** 2026-07-02 late (Director research note)
**Trigger:** USER framing challenge — "stress test spoke 1. how does substrate
know what a cat or airplane are? are we sure we tested apples to apples?"
**Load-bearing under:** brain-best-in-class + honest-scope discipline (USER-LOCKED 2026-07-02).
**Cell referenced (target of stress-test):**
`preregs/2026-07-02_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only.md`.

## 0. TL;DR — top-line

- **Honest answer to USER's question:** the substrate does NOT know what a cat is. In v3-D
  the Hebbian rule is `W[c, :] += lr * x` where `c` is a **designer-supplied one-hot label**
  attached to each synthetic sentence. The mechanism is fully SUPERVISED. The
  claim "concept encoder" needs a scope declaration: *supervised concept-label-conditioned
  sparse coding on synthetic templated corpus*.
- **We have NOT tested apples-to-apples.** The v3-D pre-reg includes an
  `ARM_CHAR_TRIGRAM_BASELINE` (concept-name trigrams only — a trivial surface-form baseline),
  but does NOT include a supervised bag-of-trigrams-plus-softmax classifier trained on the
  same labeled corpus. That is the natural apples-to-apples comparator for a
  label-conditioned encoder, and it is missing.
- **Recommended first stress-test cell:** apples-to-apples supervised baseline + label-
  semantics ablation (Tests 2 + 4 combined). P_CG = 0.40 (deflated novel-synthesis).
- **Framing rule proposal:** every concept-encoder atomization must include a
  `stress_test_scope` field declaring supervision regime, corpus type, and baselines beaten.

## 1. Prior-work check (substrate-KB concept-query, MANDATORY)

Three queries via `tools/substrate_query.sh --chunk-content --schema-version v2 --tau 0.15 --k 5`:

**Query 1:** `unsupervised concept discovery clustering AMI mutual information`
- `Mutual information` (atoms) — cosine 0.397
- `T1/mutual_information` (atoms) — 0.351
- `Mutual information preservation` (notes/research_drill_delinguistification_2x_2026-06-04) — 0.314

**Query 2:** `supervised classifier baseline apples to apples`
- `Apples-to-apples` (preregs/2026-06-24 hub_spoke_E1_v2, cross_layer_compose_LM, stage1_semantic_learner_battery) — 0.351
- `Apples-to-apples (Lane 1)` (preregs/2026-06-24 hub_spoke_E1_v2) — 0.343
- `FLAGSHIP_design_CONVERGED_..._apples_to_apples_guard` (notes 2026-06-21) — 0.338

**Query 3:** `concept invariance transfer template ablation`
- `the invariance of the configuration under translation` (wordnet) — 0.353
- `LEX-A8: Substrate-Translation tier 0 invariance` (research_to_exp_dev_AGGRESSIVE_BOUNDARY_PUSH_BATCH_2026-06-10) — 0.316
- `Concept` (multiple preregs) — 0.311

**Prior-work overlap read:**
- The `Apples-to-apples` discipline HAS been applied at hub-spoke E1 Lane 1 (2026-06-24) —
  but the guard there was `rho`-preservation across encoder variants, NOT a supervised
  classifier baseline comparison. That is a different apples-to-apples axis.
- No prior substrate cell has run a bag-of-trigrams-plus-softmax supervised baseline
  against a concept encoder. `ARM_CHAR_TRIGRAM_BASELINE` in v3-D is concept-name
  trigrams only (a *surface-form-only* baseline), not a supervised classifier trained on
  the same labeled corpus.
- `LEX-A8 Substrate-Translation tier 0 invariance` addressed cross-language token-level
  invariance, NOT within-language cross-template intra-concept invariance. Different axis.
- `Mutual information preservation` (2x delinguistification drill) is on preserving MI
  through position binding — again a different axis.
- Unsupervised concept discovery via emergent clustering on unlabeled sentence stream:
  **no substrate prior work**. NEW LITERATURE THREAD.

**Prior-work verdict:** the six stress-tests below are NOVEL in the substrate for
concept-encoder scope. The `Apples-to-apples` discipline is established but has never
been operationalized against a supervised classifier baseline. Filed as SCHEMA-VET-ready
new atoms if the stress-test cell lands.

## 2. USER framing challenge — what "know" means

The v3-D mechanism, decomposed:
1. Char+positional encoder — produces sentence HDs entirely from surface tokens.
2. Per-concept Hebbian accumulator — for each sentence-label pair `(s, c)`, does
   `W[c, :] += lr * encode(s)`. **`c` is a designer-provided one-hot label.**
3. Top-K WTA — per-concept top-K mask on `W[c, :]` produces a sparse-bipolar concept HD.

Under this mechanism, "the substrate knows cat is cat" reduces to: *the substrate averages
all sentences we labeled `cat` and produces an HD that reflects that average*. It is a
label-conditioned per-cluster mean encoder. It does NOT discover cats. It does NOT know
what a cat is. It memorializes the labeling we imposed.

That is not intrinsically bad — supervised concept learning is a legitimate primitive —
but it must be declared honestly in scope. The two failure modes to guard against:
1. **Framing creep** — atomizing v3-D as "concept encoder" without the "supervised on
   synthetic corpus" qualifier lets downstream work assume more capability than we built.
2. **Apples-to-apples gap** — if a bag-of-trigrams-plus-softmax classifier trained on the
   same labeled corpus produces equivalent-or-better cluster structure, we have built no
   substrate advantage over a trivial supervised classifier.

The stress-test suite below closes both gaps.

## 3. Six stress-tests + rationale + HP/HF bands

### Test 1 — Unsupervised concept discovery
- **What:** strip concept labels from the training loop. Encode every sentence to an HD
  (char+positional only). Cluster the sentence HDs (k-means k=50 or spectral) or measure
  AMI vs designer labels.
- **Metric:** adjusted mutual information (AMI) between k-means partition and designer
  concept labels.
- **HP:** AMI >= 0.5 (mechanism discovered >=50% of the designer clustering).
- **HF:** AMI < 0.2 (mechanism is entirely label-parasitic).
- **Rationale:** most direct answer to USER's question. If unsupervised AMI is high,
  the substrate DOES discover the clusters. If low, the whole v3-D result is contingent
  on the labels.
- **Cost:** moderate. Requires a new mechanism variant (unsupervised competitive-Hebbian
  on sentence stream) — cannot reuse the v3-D arm code directly.
- **Expected outcome (pre-run guess):** AMI in [0.15, 0.35]. The corpus's char-trigram
  structure DOES separate clusters somewhat (kitten/cat share morphology, differ from
  airplane/jet). But without label conditioning, no mechanism forces per-cluster mean
  formation — clusters bleed together in HD space.

### Test 2 — Char-trigram-softmax supervised baseline
- **What:** bag-of-char-trigrams featurizer over each sentence -> LogisticRegression
  softmax classifier on concept_label. Train on same corpus v3-D uses. Extract per-concept
  weight vectors (or classifier logits per sentence) as "concept HDs". Compare cat_kitten_cos
  and gap on same held-out sentences.
- **Metric:** cat_kitten_cos, cat_airplane_cos, gap, intra_cluster_cos_mean on held-out
  test sentences (5 held-out per cluster).
- **HP for Spoke 1 to earn its complexity:** v3-D gap - softmax gap >= 0.10 on held-out
  sentences, OR v3-D intra_cluster_cos_mean - softmax intra_cluster_cos_mean >= 0.10.
- **HF for Spoke 1:** softmax matches or beats v3-D on both metrics -> Spoke 1 mechanism
  has no advantage over trivial supervised classifier. Substrate framing regresses.
- **Rationale:** THE apples-to-apples test. USER's second question, directly. Cheap
  (~30 lines, sklearn). Any concept encoder should be able to beat bag-of-trigrams-plus-
  softmax on discrimination, otherwise we have no substrate story.
- **Cost:** trivial. sklearn LogisticRegression on ~50-dim label output.
- **Expected outcome:** softmax likely competitive on discrimination gap (linear on
  bag-of-trigrams is a strong baseline for this templated corpus). v3-D's structural
  advantage — if any — is in sparsity + compositional bundling, not in raw discrimination.

### Test 3 — Concept-invariance transfer (cross-template)
- **What:** partition templates into TRAIN (template A: "the {concept} {verb}s the {object}")
  and TEST (template B: "{object} was {verb}d by {concept}"). Train v3-D on template A only.
  Compute concept HDs for held-out template B sentences. Cross-template intra-concept cos.
- **Metric:** for each concept c, mean cos(hd_A(c), hd_B(c)) where hd_B is computed from
  template B sentences of concept c using the trained W.
- **HP:** cross-template intra >= 0.4 (real learned invariance).
- **HF:** cross-template intra < 0.2 (template memorization — the concept HD is
  template-specific artifact).
- **Rationale:** the honest test of "did we learn a concept or did we memorize a template?"
  Templated synthetic corpora make it easy to accidentally learn template structure instead
  of concept structure.
- **Cost:** moderate. Requires corpus rewrite with template-partitioned generation.
- **Expected outcome:** cross-template intra in [0.15, 0.35]. Char+positional encoding puts
  each concept in a template-specific bucket; cross-template will have low overlap unless
  the Hebbian averaging smooths over templates.

### Test 4 — Label-semantics ablation (shuffle test)
- **What:** shuffle concept labels randomly across the training sentences (each sentence
  gets a random concept label from the 50). Train v3-D on shuffled labels. Compute
  cat_kitten_cos and gap on true cat/kitten held-out sentences using the shuffled-trained W.
- **Metric:** delta = (v3-D unshuffled gap) - (v3-D shuffled gap).
- **HP:** delta >= 0.30 (mechanism uses label semantics meaningfully — unshuffled gap
  much higher than shuffled).
- **HF:** delta < 0.10 (mechanism produces similar gap whether labels are meaningful or
  random -> mechanism is structural not semantic).
- **Rationale:** direct probe of whether the mechanism depends on the label semantics or
  just the label structure (i.e., 50 buckets to route sentences into). If shuffling labels
  still produces a high gap, the mechanism is exploiting arbitrary clustering, not concept
  semantics.
- **Cost:** trivial. Same code, shuffle one column.
- **Expected outcome:** delta in [0.20, 0.50]. Shuffling breaks the semantic per-cluster
  mean; shuffled W[c] converges toward "mean of random sentences" for all c, so all shuffled
  concept HDs become similar to each other. Gap should collapse toward zero.

### Test 5 — Corpus-transfer diagnostic
- **What:** train v3-D on synthetic templated corpus. Encode held-out sentences drawn from
  a real corpus (curated Wikipedia subset with cat/kitten/airplane/jet mentions, 50 concepts
  x 5 sentences). Compare concept HDs against synthetic-corpus concept HDs.
- **Metric:** cross-corpus intra-concept cos on real sentences.
- **HP:** N/A (diagnostic; expected FAIL).
- **HF:** N/A (result is scope-declaration, not pass/fail).
- **Rationale:** honest delineation. The mechanism is trained on synthetic templated corpus;
  real Wikipedia sentences have entirely different char-trigram distributions. Result should
  be near-chance. Purpose is to atomize "v3-D concept encoder scope = synthetic-only-with-
  labels" in the substrate.
- **Cost:** moderate (Wikipedia subset curation).
- **Expected outcome:** cross-corpus intra in [-0.05, +0.15]. Near chance.

### Test 6 — Compositional generalization (optional)
- **What:** train v3-D on concepts {cat, kitten, dog, puppy, airplane, jet, ...} MINUS
  {puppy}. Test whether puppy's HD (computed from puppy sentences using the trained W)
  clusters near dog.
- **Metric:** cos(hd_puppy, hd_dog) - cos(hd_puppy, hd_airplane).
- **HP for compositional:** delta >= 0.30 (mechanism generalizes to unseen concept via
  shared surface features).
- **HF:** delta < 0.10 (mechanism cannot generalize; only knows trained labels).
- **Rationale:** stretch test. If the mechanism is truly building semantic-cluster
  structure, puppy should land near dog via shared morphological / char-trigram features.
  If it can't generalize, the mechanism is a per-label lookup, not a concept space.
- **Cost:** moderate. Requires leave-one-out training + held-out concept sentences.
- **Expected outcome:** delta in [0.10, 0.40]. Depends heavily on whether puppy/dog share
  enough char-trigram signal to co-project via char+positional encoder.

## 4. Cell structure recommendation

Three options considered:

**Option A — single stress-test cell with 6 arms** — REJECTED. Test 1 requires a new
mechanism variant (unsupervised competitive-Hebbian); Test 5 requires a Wikipedia subset;
Test 3 requires template-partitioned corpus. Bundling forces the least-ready sub-tests to
gate the whole cell. Diagnostic clarity suffers when a test-3 corpus bug fails the cell.

**Option B — 3 cells** — RECOMMENDED.
1. **Cell 1:** `spoke1_v3_D_apples_to_apples_stress_test` — Tests 2 + 4 combined.
   Baseline supervised classifier + label-shuffle ablation. Uses existing v3-D corpus
   and existing v3-D arm code (adds softmax arm, adds label-shuffle arm). Trivial to
   implement. Answers the two most-load-bearing USER questions.
2. **Cell 2:** `spoke1_v3_D_invariance_transfer_stress_test` — Test 3. Template-
   partitioned corpus + cross-template intra measurement. Moderate corpus rewrite.
   Answers "concept vs template memorization" honestly.
3. **Cell 3:** `spoke1_unsupervised_concept_discovery_stress_test` — Test 1 + Test 6.
   New mechanism variant (unsupervised competitive-Hebbian on unlabeled stream). Highest
   engineering cost; answers deepest USER question ("does the substrate DISCOVER cats").

Test 5 (corpus-transfer diagnostic) can be added as a report-only arm to Cell 1 or Cell 3
depending on whether Wikipedia subset is ready. Not a blocker for either.

**Option C — 5 separate cells** — REJECTED. META-atomization overhead is 5x for
diagnostic bundles that share substrate infrastructure. Cell 1's two tests share the same
corpus, encoder, and metric functions — splitting them is over-serialization.

**Parallel-dispatch efficiency:** Cell 1 and Cell 2 can run in parallel on `remote_cpu`
(no shared state). Cell 3 depends on new mechanism arm and should serialize behind Cell 1
so we know if the supervised story holds before investing in unsupervised.

**Diagnostic clarity:** each cell answers one clean question. Verdict maps clean-onto
scope declarations.

## 5. First cell — apples-to-apples stress-test (prereg sketch)

**Anchor:** `substrate_concept_encoder_spoke1_v3_D_apples_to_apples_stress_test_v1`
**Cell:** `experiments/exp_substrate_concept_encoder_spoke1_v3_D_apples_to_apples_stress_test_v1.py`
**Depends on:** `experiments/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026-07-02.py`
(reuses corpus generator + char+positional encoder + Hebbian-WTA arm code).

**Arms (cardinality_ok: 5 arms x 3 seeds = 15 units):**

| Arm | Mechanism | Role |
|---|---|---|
| ARM_V3_D_TRUE_LABELS | v3-D char+positional + per-concept Hebbian + top-K WTA, true labels | Reference (reproduces v3-D positive control) |
| ARM_V3_D_SHUFFLED_LABELS | Same mechanism, labels permuted uniformly at random | **Test 4** (label-semantics ablation) |
| ARM_SOFTMAX_BOT_BASELINE | Bag-of-char-trigrams + sklearn LogisticRegression on concept_label; concept HD = per-class weight vector, normalized bipolar | **Test 2** (apples-to-apples supervised) |
| ARM_SOFTMAX_BOT_SHUFFLED | Same softmax, shuffled labels | Baseline for Test 4 (shuffled softmax) |
| ARM_RANDOM_BASELINE | Random bipolar HD per concept | Chance control |

**Metrics (held-out test sentences: 5/concept x 50 concepts = 250 held-out):**
- cat_kitten_cos_mean (held-out)
- cat_airplane_cos_mean (held-out)
- gap_mean = cat_kitten - cat_airplane (held-out)
- intra_cluster_cos_mean (all 25 clusters, held-out)
- softmax_test_accuracy (Test 2 sanity)
- shuffle_delta_gap = ARM_V3_D_TRUE_LABELS.gap - ARM_V3_D_SHUFFLED_LABELS.gap
- softmax_shuffle_delta_gap = ARM_SOFTMAX_BOT_BASELINE.gap - ARM_SOFTMAX_BOT_SHUFFLED.gap

**HP bands:**

| ID | Applies to | Metric | Threshold | Rationale |
|---|---|---|---|---|
| HP1 | ARM_V3_D_TRUE_LABELS | gap_mean (held-out) | >= 0.30 | Reproduces v3-D positive control on held-out (may drop from in-sample 0.50 due to held-out gap) |
| HP2 | ARM_V3_D_TRUE_LABELS - ARM_SOFTMAX_BOT_BASELINE | gap_mean or intra_cluster_cos_mean | >= 0.10 | **Test 2 apples-to-apples HP** — v3-D beats trivial supervised baseline |
| HP3 | ARM_V3_D_TRUE_LABELS - ARM_V3_D_SHUFFLED_LABELS | shuffle_delta_gap | >= 0.30 | **Test 4 label-semantics HP** — mechanism uses label semantics |
| HP4 | ARM_RANDOM_BASELINE | \|gap_mean\| | <= 0.05 | Chance control |
| HP5 | ARM_SOFTMAX_BOT_BASELINE | softmax_test_accuracy | >= 0.30 | Softmax at least beats chance (chance = 1/50 = 0.02); sanity |

**HF bands:**

| ID | Applies to | Metric | Threshold | Consequence |
|---|---|---|---|---|
| HF1 | ARM_V3_D_TRUE_LABELS | gap_mean (held-out) | < 0.15 | v3-D collapses on held-out -> mechanism cannot generalize even within-template |
| HF2 | ARM_SOFTMAX_BOT_BASELINE - ARM_V3_D_TRUE_LABELS | gap_mean or intra_cluster_cos_mean | >= 0.05 | **HARD_FAIL: substrate has no advantage over trivial supervised classifier** — Spoke 1 arc pauses |
| HF3 | ARM_V3_D_SHUFFLED_LABELS | gap_mean | > 0.20 | Shuffled gap high -> mechanism is structural not semantic; v3-D scope regresses to "arbitrary label routing" |

**HP scope:** LOAD_BEARING on HP2 and HP3 (the two stress-test cores). HP1 is
positive-control sanity. HP4/HP5 are chance/sanity guards.

**cardinality_ok:** EXPECTED_N_UNITS = 5 arms x 3 seeds = 15.

**Substrate-KB concept-query prior-work check (mandatory):** completed in section 1 above.
Three queries; verdict: novel stress-test for concept-encoder scope; SCHEMA-VET-ready.

**Compute architecture:** class (b) sequential-CPU. Softmax arm ~10s per seed
(sklearn LogisticRegression on ~2000 sentences x ~5000 trigram features). v3-D arms
~30-60s per seed at N=2048 (v2 MEASURED). Total smoke ~15 units x ~30s = ~7.5min.
smoke --timeout 900s; full at N=4096 --timeout 1800s.

**Timeline:**
- Cell 1 (this): author -> smoke -> `remote_cpu` FULL, wall ~30 min author + 10 min smoke
  + 30 min FULL. Landing E+2h from spawn.
- Cell 2 (invariance transfer): author -> smoke -> `remote_cpu` FULL, wall E+4h.
- Cell 3 (unsupervised): design + author -> smoke -> `remote_cpu` FULL, wall E+8-16h
  (needs mechanism design).

## 6. P_CG estimate for Cell 1

Novel-synthesis cap 0.50; lit-scan deflation 0.15-0.25.

- Substantive novelty: apples-to-apples supervised comparison is standard ML methodology,
  but this SPECIFIC comparison (bag-of-trigrams-softmax vs sparse-Hebbian concept HD on
  templated concept corpus) is novel to substrate.
- Diagnostic yield: symmetric — result is decision-relevant whether HP2 passes or HF2 fires.
  Both directions land clean scope declarations.
- Mechanism robustness: v3-D reproduces v2 COMPETITIVE_ONLY within 0.05 (positive control);
  softmax is deterministic given labels. Both are seed-stable.
- Prior-work overlap: apples-to-apples discipline is established (2026-06-24 hub-spoke E1
  Lane 1); this is its first application against a supervised classifier baseline for a
  concept encoder.

Raw P = 0.55. Deflated P_CG = **0.40** (novel-synthesis-cap-adjusted).

## 7. Framing rule proposal — durable memory

**Proposed feedback file:** `feedback_concept_encoder_atoms_must_declare_stress_test_scope_USER_2026-07-02.md`

**Rule:** every concept-encoder atomization (or any atom claiming "learned representation
of X") must include a `stress_test_scope` field declaring:
1. **Supervision regime:** {supervised-label-conditioned | semi-supervised | unsupervised-
   discovery}.
2. **Corpus type:** {synthetic-templated | synthetic-diverse | real-corpus-subset |
   real-corpus-full}.
3. **Baselines beaten:** which trivial baselines the mechanism has been shown to beat
   (bag-of-trigrams-softmax, char-trigram-cos, random-bipolar, etc.). At least ONE
   supervised-baseline comparison required for label-conditioned mechanisms.
4. **Invariance tested:** cross-template? cross-corpus? compositional? or none-tested?
5. **Label-shuffle ablation result:** did shuffled-label control land at chance? (Any
   mechanism whose shuffled-label control produces gap > 0.20 has failed the label-
   semantics test and is a structural artifact, not a concept encoder.)

Enforcement: SCHEMA-VET on any concept-encoder atomization rejects atoms missing this
field. Skunkworks landed-VET spot-checks the declared scope against the cell's actual
arms.

**Load-bearing rationale:** without this rule, downstream cells and atomizations assume
capabilities the encoder does not have. "Concept encoder" without scope = framing creep.
USER's challenge today would not have surfaced if the atomization discipline forced the
scope declaration.

**Directive to file after Cell 1 lands (regardless of verdict):** file the durable memory
rule + update MEMORY.md index.

## 8. Sequencing + gates

1. **NOW:** spawn `hdi_exp_dev` with Cell 1 (apples-to-apples stress-test) — author +
   smoke + local ship. Pause-gated if orchestrator paused; otherwise `remote_cpu` FULL
   dispatch on smoke HARD_PASS.
2. **On Cell 1 land:** Skunkworks landed-VET on Cell 1. Then:
   - If HP2 passes (v3-D beats softmax by >= 0.10) AND HP3 passes (shuffle delta >= 0.30):
     Spoke 1 apples-to-apples cleared. Atomize v3-D as
     `Spoke1_v3_D_supervised_concept_encoder_scope_synthetic_templated_v1` with the
     scope declaration (per rule 7). Then queue Cell 2 (invariance transfer).
   - If HF2 fires (softmax beats or matches v3-D): SPOKE 1 ARC PAUSES. Route to Skunkworks
     + Research for mechanism rethink. Do NOT ship v3-D as substrate advantage.
   - If HF3 fires (shuffled gap > 0.20): flag mechanism as structural-not-semantic; reframe
     atomization; consider Test 1 (unsupervised) as blocker for further work.
3. **After Cell 1 verdict:** Cell 2 (invariance transfer) and Cell 3 (unsupervised) queued
   per what Cell 1 tells us about the mechanism.
4. **File framing rule** (section 7) as durable memory immediately after Cell 1 lands
   regardless of verdict — the discipline is right whether or not v3-D passes.

## 9. Sub-agent dispatch plan

- `hdi_exp_dev` — author Cell 1 (apples_to_apples_stress_test). Handoff includes:
  the v3-D pre-reg path, this note's section 5 (arms + HP + HF bands), sklearn
  LogisticRegression + bag-of-trigrams softmax arm implementation guidance, the reuse-
  v3-D-corpus-and-encoder pointer.
- On smoke land: `hdi_orchestrator` ships FULL to `remote_cpu_queue`.
- On FULL land: `hdi_skunkworks` landed-VET + honest re-read.
- Cell 2 + Cell 3 authored after Cell 1 verdict.

## 10. Honesty caveats + open Qs for USER

- **Cell 1 HF2 is a real risk.** Templated synthetic corpora with char-trigram surface
  features are exactly the regime where linear classifiers dominate. If softmax matches
  v3-D on gap and intra, we should reframe substrate advantage as sparsity + compositional-
  bundling (downstream use) rather than raw discrimination. USER may want to hear about
  this framing pre-emptively.
- **Test 1 unsupervised needs new mechanism design.** Cannot reuse v3-D arm code.
  Competitive-Hebbian on unlabeled stream needs a winner-selection rule that DOES NOT USE
  labels — most candidates (SOM, k-winners-take-all with cluster centroids, growing
  neural gas) need mechanism-level design. This is Cell 3 scope; if USER wants prioritized
  earlier, flag.
- **Test 5 corpus-transfer requires curated Wikipedia subset** for cat/kitten/airplane/jet/
  etc. concept vocabulary. Substrate does NOT currently have this. Can defer to report-only
  arm or build small subset (~250 sentences) manually.
- **Framing rule (section 7) is orthogonal to Cell 1 verdict.** It should file regardless.
  Filing early prevents the same framing creep on Cell 2 / Cell 3 atomizations.

## References

- Foldiak 1990. Forming sparse representations by local anti-Hebbian learning. Biol Cybern.
- Kohonen 1982. Self-organized formation of topologically correct feature maps. Biol Cybern.
- Prior substrate: `preregs/2026-07-02_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only.md`
- Prior investigation: `notes/research_spoke1_pc_earning_complexity_investigation_2026-07-02.md`
- Apples-to-apples prior application: `preregs/2026-06-24_substrate_hub_spoke_E1_v2_diverse_algorithm.md` (Lane 1 rho guard)
- FLAGSHIP apples-to-apples guard: `notes/skunkworks_to_expdev_research_cc_orch_FLAGSHIP_design_CONVERGED_build_cleared_rho_apples_to_apples_guard_2026-06-21.md`
- Substrate-KB v2 query wrapper: `tools/substrate_query.sh`
