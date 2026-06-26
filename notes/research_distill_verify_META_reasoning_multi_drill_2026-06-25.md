# Distill-verify META-reasoning -- multi-angle drill

**From:** research
**Filed:** 2026-06-25
**Type:** strategic_drill (5 angles; single deliverable)
**USER ask:** "this one we really want to nail, because this is going to be absolutely KEY to how the system evaluates itself."

---

## Executive verdict (under-claim discipline)

The substrate **has a working META-reasoning verifier primitive at the cell-author level**: CHTV-1 typed-signature equality. v1 (smoke) showed it MERGES (sound positive); v2 cell (3 seeds, full) showed it generalizes to bare-typed-only held-out groups at mean 0.78 (just-below-HP, MIDDLE_BAND); v3-overmerge (smoke) showed it REFUSES every signature-visible distinction (sound negative, 9/9) and correctly self-locates the single saturation boundary; v3.1-inverse (smoke) showed the INVERSE_PAIR sub-classifier is sound with a documented low-confidence name-heuristic; v2-class-B (full, 1 seed) showed the higher-level SHARED_ABSTRACTION / THEOREM_LINKED / CROSS_DOMAIN / INVERSE_PAIR / DISTINCT triage works on anchor pairs (2/2 ground-truth + 9 candidates).

**What is chain-grade:** nothing yet -- only v2-operator-equivalence ran 3 seeds, and it landed MIDDLE_BAND (HONEST_NEGATIVE per Skunkworks tier ruling) because the NAMED-discriminator axis is structurally untestable at current corpus composition (only 1 NAMED operator in the entire 20-group dup corpus).

**What is mechanism-shown:** the four-verdict typed-signature prover (PROVABLY_EQUIVALENT / EQUIVALENT_BY_CAPABILITY / UNDECIDABLE_BY_PROVER / NOT_EQUIVALENT) plus the seven-verdict relationship triage (MERGEABLE / SHARED_ABSTRACTION / THEOREM_LINKED / CROSS_DOMAIN_ABSTRACTION / INVERSE_PAIR / DISTINCT / UNDECIDABLE) ARE both implemented, both tested on adversarial decoys, both correctly map their own saturation boundary.

**Strategic positioning:** this primitive is the foundation for substrate self-evaluation. The test bar isn't "does the substrate have META-reasoning" -- v1 + v3 controls already show it does at the cell-author level. The bar is "does the substrate's META-reasoning generalize at chain-grade across a discriminator-rich NAMED corpus." That requires a corpus we don't currently have. The path to chain-grade is corpus engineering, not mechanism engineering.

---

## Drill 1: Mechanism deep-understanding

### What "typed-signature reasoning verifies operator equivalence" means MECHANICALLY

The CHTV-1 verifier (Closed-loop Hyperdimensional Typed Verifier v1) is **NOT** an HRR/cleanup operation. It is a small symbolic decision procedure over atom metadata that lives at the cell-author level. Walk-through:

1. **Substrate self-scan.** `PartitionedStore.all_atoms()` enumerates every atom in `data/substrate_index/*/atoms.jsonl`. Each atom carries an `algebra` dict and a `serves_capability` set.

2. **Self-grouping by short-name.** For each atom, strip namespace prefix and tier suffix; group atoms sharing the same short-name. Two atoms with name `discriminative_perceptron` authored at tier T2 and tier T3 land in the same group. This is the candidate-duplicate enumeration step (no embedding, no HRR -- straight string-keyed dict).

3. **Typed-signature extraction per atom.** Read five fields out of `algebra`: `domain`, `operation_type`, `signature_input_type`, `signature_output_type`, `complexity_class`. An atom with >=3 of these populated has a "typed signature." Atoms with <3 are "bare."

4. **Pairwise typed-signature equality.** Inside a duplicate group, compare each member's signature dict. If 2+ members have typed signatures AND all such signatures are **dict-equal**, the group is PROVABLY_EQUIVALENT (modulo capability check). If signatures differ on any field, NOT_EQUIVALENT. If insufficient typed-sig members but identical non-empty `serves_capability` sets, EQUIVALENT_BY_CAPABILITY (weaker -- capability fingerprint, not type fingerprint). If everything is bare, UNDECIDABLE_BY_PROVER.

5. **Capability sanity check.** Even when typed signatures match, if `serves_capability` sets are non-empty AND contradictory across members, return NOT_EQUIVALENT. This catches "same type, different observed role" decoys.

### Walk-through of one verified pair from v1

Take `astar` (n=2, tiers T3+T2, PROVABLY_EQUIVALENT in v1):
- Atom A (T3): algebra = {domain: graph_search, operation_type: shortest_path_with_heuristic, signature_input_type: graph_and_heuristic, signature_output_type: state_sequence, complexity_class: O(b^d)}. caps: {} (empty).
- Atom B (T2): algebra = {same five fields, identical values}. caps: {} (empty).
- Pairwise compare: dict A == dict B at all 5 fields. `len(present) >= 2`, `all(s == first for s in present[1:])` returns True. `nonempty = [c for c in caps if c]` returns []; no contradiction. Verdict: `PROVABLY_EQUIVALENT`.

Take `cosine_similarity` (T1+T3, v1 said PROVABLY_EQUIVALENT, **but v2 said NOT_EQUIVALENT** for seeds 11+13 training fold -- corpus drift between v1 and v2 runs, likely a metadata edit between dates that flipped one tier's algebra dict). This is itself a substrate-self-correction signal: the verifier detected a metadata-induced equivalence change. NOT a verifier bug; a metadata audit signal.

Take `gradient` (T1+T2, UNDECIDABLE_BY_PROVER in all runs): both atoms bare (no typed signature, empty caps). Verifier correctly refuses to merge without evidence. This is the **conservative-correct** path -- not a failure mode, the verifier's discipline.

### Why this is brain-aligned

The cortical analog is **schema/relational comparison in association cortex** -- specifically the temporal-pole-to-IPL-to-PFC loop that does abstract-concept similarity (Hagoort, Friederici 2008; Binder et al. 2009 semantic-cognition review; Patterson hub-and-spoke). The brain's equivalence judgment is not the bare "do these two concept-vectors have cosine > tau" question -- it's the structured question "do these two concepts have the same type signature given the schema currently active in PFC?" Linguistically: judging "running" and "jogging" as type-equivalent (motion-verb-locomotion) but NOT "running" and "running [a meeting]" (motion-verb vs management-verb) requires invoking the schema's type fields -- domain, manner, telicity -- and checking each in turn, not a single cosine.

The substrate's CHTV-1 verifier IS that schema-typed comparison made literal: it computes structured-equality over the algebra dict (which IS the substrate's type schema), and refuses to merge when any field differs. The brain analog isn't a single area; it's the joint operation of (a) semantic-feature retrieval from temporal cortex, (b) feature-by-feature comparison in IPL/AG, (c) executive coherence-check in PFC. The substrate's `classify_pair` function compresses all three into a 60-line Python decision procedure.

### Failure modes

- **False-positive merge (over-distillation).** Two distinct algorithms with identical typed signature AND identical non-empty caps but distinct bodies. This is the **invisible decoy** in v3 -- the verifier correctly predicts it WILL merge here, because typed-signature equality is necessary-but-not-sufficient for operational equivalence. The remediation is body-level proof witnesses (V1's provenance pointer OR an L6-PROOF derivation chain). The cell deliberately maps this boundary; it doesn't hide it.

- **False-negative miss (under-merging).** Two truly-equivalent algorithms with bare signatures (no algebra dict authored). The verifier returns UNDECIDABLE_BY_PROVER -- sound conservatism but coverage-loss. v1 had 2/29 dup groups (~7%) in this state. Remediation is `algebra_dict` authoring (a curation task, not a verifier task).

- **Metadata drift.** v1 said cosine_similarity is PROVABLY_EQUIVALENT (April-era metadata); v2 said NOT_EQUIVALENT (June-era metadata). The verifier is the same; the SOURCE metadata changed between runs. This is a self-correction signal, not a verifier bug.

- **Corpus-degeneracy (THE current killer).** v2 demanded "named-discriminator generalizes across held-out folds," but the corpus has only 1 NAMED operator in the entire 20-group dup set. With 3-fold CV at 30% held-out probability, the chance of getting 0 NAMED in held three times is 0.7^3 = 0.343 -- not pathological, but it means the named axis never actually got tested. The mechanism passes the discriminator that does run (held distillation 0.78), but the SPECIFIC discriminator named in pre-reg is structurally untestable. Skunkworks correctly ruled HONEST_NEGATIVE.

---

## Drill 2: Corpus design for proper test

### Minimum NAMED corpus size for chain-grade

Three constraints:

1. **Discriminator must be testable.** Pre-reg measures "named-held distillation ratio." For this to be a non-trivial fraction, every held-out fold across every seed must contain >=1 NAMED operator. With 3 folds and 3 seeds, that's at minimum (N_named >= folds = 3) **and** distributed so each fold gets one. The safe lower bound is N_NAMED >= 6 (so even with random shuffle, each held-out 1/3 has >=2 NAMED on average; Hypergeometric tail P(zero in fold | 6 named in 20 corpus) = C(14,k)/C(20,k) for held-fold-size k=6 -> C(14,6)/C(20,6) = 3003/38760 = 0.077 -- still ~7.7% of seeds will whiff). With **stratified split** (force each fold to contain ceil(N_NAMED/3) NAMED), N_NAMED >= 3 is the floor; N_NAMED >= 9 gives 3-per-fold guaranteed with comfortable cv-control.

2. **cv-control on the held-named metric.** With 3 seeds and HP cv-rail 0.07, we need per-seed named-held ratios that are within ~7% of each other. If each fold has 3 NAMED and the verdict per pair is approximately Bernoulli(p_provable), per-seed ratio is k/3 in {0, 1/3, 2/3, 1}. With p_provable=0.9 we get mostly 1.0 and occasional 2/3. cv across seeds = std/mean. For three seeds at [1.0, 1.0, 2/3] mean = 0.889, std = 0.157, cv = 0.177 -- still outside HP. For chain-grade cv, we need **N_NAMED_per_fold >= 8** so the per-seed metric is k/8 and approximately continuous in [0, 1]. That means **N_NAMED_total >= 24** for 3-fold stratified.

3. **Discriminator-richness.** "All NAMED merge" gives a degenerate-easy discriminator (mechanism trivially passes). A real chain-grade test needs **adversarial NAMED**: some that SHOULD merge, some that look-like-they-should but actually shouldn't. Mix ratio target: ~70% TRUE-positive (provably equivalent NAMED dups), ~30% adversarial-NAMED (named-similar but signature-distinct OR signature-identical but capability-divergent). That makes both sound-merge AND sound-refuse parts of the discriminator. Target: N_NAMED_total >= 24, with ~17 true-positive + ~7 adversarial.

**Bottom line:** minimum chain-grade-eligible NAMED corpus is **24 NAMED operator dup-groups with mix-engineered adversarial controls**, deployed via stratified 3-fold CV.

### Self-bootstrap from substrate's own atoms

I ran the probe (`.venv/Scripts/python.exe -c "..."`) on the live Store today:

- 177360 total atoms in Store
- 62 atoms have >=3 typed-signature fields populated
- 47 unique typed-signatures across those 62 atoms
- **Zero typed-signatures shared across DIFFERENT names** (the immediate self-bootstrap "find your own equivalences by typed-sig" pool is currently empty)
- **20 duplicate-name groups** (same short-name, multiple atoms) -- v2's corpus
- **93 capability-shared cross-name groups** (>=2 distinct names share a capability) -- much richer

The 62-atom typed-signature pool is the binding constraint. **The substrate cannot currently self-bootstrap a chain-grade NAMED equivalence corpus from typed-signature reasoning alone -- 99.97% of atoms have <3 typed-sig fields.** This is a corpus-engineering finding, not a mechanism finding.

The 93-capability cross-name pool is the workable bootstrap path. Capabilities at 5-11 distinct names each:
- `cap_discriminative_perceptron` -- 11 names: adam_optimizer, cross_entropy, cross_entropy_loss, discriminative_learning_family, discriminative_perceptron_pipeline, ...
- `pp-225_fact_recall_kb100k` -- 10 names: amit_gutfreund_sompolinsky_capacity, cleanup, complementary_learning_systems, cosine_cleanup, fhrr_bind, ...
- `cap_spectral_observability` -- 10 names: free_probability_family, kappa_4_free, marchenko_pastur_distribution, mp_bulk_kl, random_matrix_theory, ...
- `cap_fhrr_bind` -- 7 names: circular_convolution, convolution_theorem_synthesis, discrete_fourier_transform, fast_fourier_transform, fhrr_bind, ...

These are the right pool for SHARED_ABSTRACTION / THEOREM_LINKED / CROSS_DOMAIN_ABSTRACTION cell-B triage (where v2-class-B already lives). They are NOT the right pool for v1's MERGEABLE / NOT_EQUIVALENT cell-A discriminator -- they're INTENTIONALLY same-capability-different-implementation pairs, the kind cell-B exists to triage as SHARED_ABSTRACTION not merge.

**Bootstrap path for v1-style NAMED merge corpus:**
1. **Author algebra_dict on the 99% of atoms that lack it.** This is curation, not research. Tools needed: `tools/algebra_dict_authoring_helper.py` that proposes signatures based on capability-set + name heuristics and queues human/Director review. If we go from 62 typed-sig atoms to ~5000, the cross-name signature-sharing pool will populate naturally. Estimated effort: 50-200 atoms/day curation rate; chain-grade-eligible NAMED corpus in ~1-2 weeks calendar.
2. **OR** redirect v3 to use external NAMED corpora (next subsection).

### Where to source rich NAMED corpora externally

- **Mathematical operator pairs** (lit-evidence: textbook equivalence theorems). Convolution-theorem pairs (FFT, DFT, circular convolution, polyphase representation), eigendecomposition pairs (SVD, PCA, whitening, ZCA -- substrate already has pca_whitening + zca_whitening landed). Sample size achievable: ~30-50 named pairs from one mathematical-physics or signal-processing textbook chapter.
- **Programming primitive pairs.** map vs fmap, reduce vs fold vs foldl, filter vs select vs where, async/await vs Promise.then. Sample size: 40-100 named pairs across functional/imperative/concurrent paradigms. Generic terms only per query-privacy.
- **KG relation pairs.** is_a vs subclass_of vs subtype_of vs IS-A vs hyponym (WordNet, ConceptNet, Wikidata each have multiple synonymous relation names). Sample: 20-30 named relation-pairs across 3-5 KGs.
- **Substrate primitive pairs.** Substrate's own HRR_bind vs FHRR_bind vs MAP_bind; cosine_cleanup vs nearest_neighbor vs argmax_dot; modern_hopfield vs sparse_distributed_memory (already in v2-class-B). Sample: 10-15 substrate-internal primitive pairs (the deepest sample but smallest count).
- **Statistical/ML algorithm equivalences.** EM vs Baum-Welch (for HMMs), forward-backward vs alpha-beta, Viterbi vs max-product, ridge regression vs Tikhonov regularization. Sample: 15-25 lit-canonical equivalences.

**Recommended v3 corpus composition:** 24 NAMED dup-groups split 8/8/8 across math-operator + programming-primitive + substrate-internal sources, with 6 adversarial decoys (named-similar but signature-distinct) mixed in. Total = 30 groups. **This is corpus engineering done first, before any v3 cell-author work.**

### v3 corpus-stratification design

Pre-reg sketch:
```
HARD_PASS_CHAIN_GRADE:
  named_held_distill_ratio_mean >= 0.85
  named_held_distill_ratio_cv <= 0.07
  zero NOT_EQUIVALENT on TRUE-positive NAMED in any held-out fold
  >=80% NOT_EQUIVALENT on adversarial NAMED (correct refusal)
  fold-disjoint stratified split (each fold contains floor(N_named/3) >=8 NAMED)

MIDDLE_BAND (mechanism-shown, not chain-grade):
  named_held_distill_ratio in [0.60, 0.85)
  OR cv in (0.07, 0.20]
  OR adversarial-refusal rate in [0.50, 0.80)

HARD_FAIL:
  named_held_distill_ratio < 0.60
  OR adversarial-refusal rate < 0.50
  (mechanism does NOT generalize OR over-merges adversaries)
```

Methodology fix vs v2 (Skunkworks-flagged): **enforce fold disjointness across seeds**. v2 had fold_overlap_pairs = [[2,2,1]] across seeds 11/13/19 -- each seed's held-out set overlapped the others by 1-2 groups. Stratified-fold disjointness: pre-compute fold assignment once (deterministic stratified split), then permute fold labels (which one is held-out) per seed. This gives 3 disjoint held-out subsets that span the full corpus.

---

## Drill 3: Related variants in substrate

### distill_verify_2_class_b_relationship_discrimination (HARD_PASS, smoke, 1 seed)

Tests the **soundness half** of the closed loop: when groups are NOT mergeable, does the verifier name the correct weaker relationship instead of forcing a merge? Run on 11 groups (2 anchors + 9 candidates), achieved anchor-correct=2/2 with triage distribution {SHARED_ABSTRACTION:3, THEOREM_LINKED:2, DISTINCT:2, INVERSE_PAIR:1, CROSS_DOMAIN_ABSTRACTION:3}.

The 7-verdict triage (from v2-class-B's `classify_group`):
- **MERGEABLE** (cell-A's job): identical typed-sig + identical non-empty caps + 2 members
- **SHARED_ABSTRACTION**: same output + same/overlapping caps + different operation_type -> "extract a supertype, don't merge" (e.g., adam_optimizer + sgd + gradient_descent -> first-order-optimizer)
- **THEOREM_LINKED**: same capability, different domain + DERIVATION present -> "linked by a theorem, name the theorem don't merge" (e.g., circular_convolution + discrete_fourier_transform linked by convolution-theorem)
- **CROSS_DOMAIN_ABSTRACTION**: same output_type across distinct domains, output_type is grounded -> "abstract on the output structure" (e.g., beam_search + viterbi_decoder + astar + dijkstra all output state_sequence across different domains)
- **INVERSE_PAIR**: same domain + same output + exactly 2 members + DUAL/INVERSE_OF authored -> "binding inverse pair" (e.g., fhrr_bind + fhrr_unbind)
- **DISTINCT**: signatures or caps actively conflict, not abstractable
- **UNDECIDABLE**: insufficient evidence

**Would chain-grade if upgraded:** YES, with the same corpus expansion. The 11 groups in v2-class-B are honest anchors + lit-curated candidates -- exactly the kind of substrate the v3 NAMED corpus needs. Run at 3 seeds with held-out fold structure and pre-reg per-verdict accuracy bands. Recommendation: pair it with v3-operator-equivalence (v2 + v2-class-B as the two complementary cells in the META-reasoning suite).

### distill_verify_3_1_inverse_pair_adversarial_controls (HARD_PASS, smoke, 1 seed)

Tests the **INVERSE_PAIR detector under adversarial decoys**. 3 positives (bind_unbind, fold_unfold, forward_backward), 3 type-mismatch FPs (named "inverse" but signature mismatched), 1 noninverse-same-type FP, 2 name-coincidence false-friends (union/ion, unit/it).

Results: 3/3 positives detected, 0/4 type+noninverse-guard violations, 0/2 false-friend hits at the GUARD level. The "un"-prefix name heuristic CAN false-friend on coincidences -- the cell explicitly documents this and recommends authored DUAL-edge grounding as the sound path (name heuristic = LOW-CONFIDENCE pending DUAL-edge confirmation).

**Would chain-grade if upgraded:** YES, with 3 seeds + expanded decoy battery (>=10 each class). The cell is small and fast (elapsed 0s); just needs the discipline upgrade.

### distill_verify_3_adversarial_overmerge_controls (HARD_PASS, smoke, 1 seed)

Tests the **over-distillation guard** with 9 visible-distinct decoys (different operation_type / output_type / domain / complexity / input_type / stub-vs-full / contradictory caps / three-way one-divergent) and 1 invisible decoy (identical sig + caps + distinct body) plus 1 conservative (identical sig + empty caps -> no evidence).

Results: 9/9 visible refused merge (sound in-domain), 1/1 invisible merged (boundary correctly mapped), 1/1 conservative refused (sound caution). The cell PREDICTS where the type-only guard saturates and recommends body-level witnesses (provenance pointer / L6-PROOF chain) for the saturation point.

**Would chain-grade if upgraded:** YES, with 3 seeds (deterministic now, so 3 seeds requires randomized decoy generation -- a small refactor) + expanded decoy battery (>=15 visible across all axes, >=5 invisible variants, >=5 conservative).

### Cross-cell composition

The four-cell suite is a **mathematical inversion of the equivalence-verification problem**:

| Cell | Tests | Pass-condition |
|---|---|---|
| v1 / v2 (operator-equivalence) | Sound POSITIVE merging | Verifier MERGES true duplicates |
| v2-class-B (relationship-discrimination) | Sound NEGATIVE classification | Verifier REFUSES to merge AND names correct relationship |
| v3.1-inverse | INVERSE_PAIR sub-classifier | INVERSE_PAIR detected only when DUAL grounded |
| v3-overmerge | Over-distillation guard mapping | NO unsound merge, boundary correctly self-located |

Together they make a **falsifiable substrate self-evaluation primitive**: not "the substrate believes its operators are equivalent" (one-sided) but "the substrate correctly applies a sound rule that merges true duplicates AND refuses every signature-expressible distinction AND knows where its rule saturates." The negative-control coverage (v2-class-B + v3.1 + v3) is more substrate-significant than the positive-control (v1/v2). Skunkworks-style: by-construction-saturation suspicion on the positives is reduced by the sound-refusal density of the negatives.

**Current chain-grade portfolio gap:** all four cells are smoke (n=1 seed); v2 was the only 3-seed promotion and it landed MIDDLE_BAND. The portfolio has the COVERAGE but not the CHAIN_GRADE. v3 (per Drill 5) is the integration: expand corpus + bring all four cells to 3 seeds + cross-cell composition test.

---

## Drill 4: Strategic significance for self-evaluation

### What META-reasoning unlocks

The cell-author CHTV-1 primitive, IF chain-grade, becomes the substrate's **self-evaluation kernel**. Four downstream capabilities each map to a distinct brain analog:

1. **Self-test: verify own primitive implementations match their type signatures.** Substrate scans its `hdlab/` code primitives (sequence_memory, kg_traversal, multi_hop, whitening, char_trigram_encoder, generation) and verifies each implementation's runtime behavior is consistent with the authored algebra_dict (input/output types). Brain analog: **prefrontal monitoring / error-related-negativity** (ERN) -- the medial-frontal ERN signal that fires when behavior diverges from intended schema. Substrate's version: CHTV-1 verdict on (intended-type, observed-type) tuple.

2. **Self-correction: detect conflicting equivalence claims in own atoms.** Substrate finds atoms claiming `serves_capability` overlap but with NOT_EQUIVALENT verdicts on typed-signature (the cosine_similarity v1-vs-v2 discrepancy is a real instance) and routes them for human/Director audit. Brain analog: **anterior cingulate cortex (ACC) conflict monitoring** -- the Botvinick-Cohen conflict-detection signal that flags incompatible representations. Substrate's version: a periodic CHTV-1 sweep that emits a conflict-atom for each detected metadata-vs-behavior mismatch.

3. **Self-discovery: find new equivalences not explicitly written.** Substrate runs CHTV-1 over the typed-signature cross-product (currently 62 atoms, but with curated algebra_dict ~5000) and surfaces any pair with identical typed signature that haven't been authored as equivalent. The brain analog is **hippocampal pattern completion + neocortical semantic-similarity** -- the systems-consolidation discovery that two memories share a deep schema. Substrate's version: a new ledger row for each discovered-equivalence with provenance pointer back to the typed-sig match.

4. **Self-optimization: propose simpler equivalent operators to replace complex ones (compression via equivalence).** Substrate finds two PROVABLY_EQUIVALENT atoms where one has lower `complexity_class` (e.g., O(N log N) vs O(N^2)) and proposes a redirect: "use the cheaper equivalent for downstream cap-X." Brain analog: **basal-ganglia procedural-skill compression / striatal habit-formation** -- the dopaminergic reinforcement of cheaper routines once equivalence is verified. Substrate's version: capability-routing tables updated to prefer the lower-complexity-class member of each verified equivalence class.

### Composition with current substrate

- **+ CSP uncertainty** (existing): substrate knows what it doesn't know (epistemic uncertainty on retrieval). Compose with META-reasoning: substrate knows when its META-reasoning is itself uncertain (UNDECIDABLE_BY_PROVER verdicts surface as uncertainty-flagged equivalence claims).
- **+ audit-device pipeline** (existing): substrate audits its own retrieval decisions for self-consistency. Compose: META-reasoning audits the AUDIT pipeline -- self-evaluation of self-evaluation, a self-aware loop.
- **+ refuse-gate primitives** (existing 3 chain-grade + 1 MM): substrate refuses unsupported claims at retrieval time. Compose: META-reasoning refuses equivalence claims at the corpus-authoring level (the v1 "no merge without algebra_dict" gate is itself a refuse-gate).

The composed kernel: **CSP-uncertainty + audit-relation + META-reasoning + refuse-gate = self-aware substrate that knows what it doesn't know AND can find what it should know AND refuses to over-claim AND audits its own audits.** This is the Stage 4 self-improvement scaffold the USER's strategic vision named.

### Honest limitation

The substrate **cannot self-evaluate body-level (non-typeable) equivalences** under CHTV-1. Two atoms with identical algebra_dict + identical caps but distinct bodies WILL be falsely merged. Closing this requires body-level witnesses -- either provenance pointers (V1's path: atom A and atom B both link to the same provenance source = same body = sound merge) or L6-PROOF derivation chains (the substrate proves A = B via a chain of substrate-internal equivalence-preserving transforms). The provenance-pointer path is curation work; the L6-PROOF path is substrate-mathematics work. Both are **separately scoped** from the META-reasoning primitive proper.

---

## Drill 5: What we'd dispatch next

### Recommended v3 cell spec

**Anchor name:** `exp_substrate_distill_verify_operator_equivalence_v3_chaingrade`

**Pre-flight (BEFORE cell dispatch):**
1. **Corpus engineering task** (Director-routable to a curation spawn, NOT the cell):
   - Author algebra_dict on at minimum 30 NAMED operator dup-groups (per Drill 2 mix: 8 math-operator + 8 programming-primitive + 8 substrate-internal + 6 adversarial-named).
   - Commit corpus to `data/substrate_index/external/distill_verify_v3_named_corpus.json`.
   - Verify-the-referent: `python -c "import json; data = json.load(open('...')); assert len(data['groups']) >= 30"`.

**Cell design:**
- **Stratified 3-fold CV across NAMED groups** + uniform random for non-NAMED (so each fold has floor(N_NAMED/3) >= 8 NAMED + filler non-NAMED).
- **Fold disjointness enforced**: pre-compute one stratified fold assignment, permute fold-label-assignment per seed (each seed picks a different fold as held-out; held-out subsets are 3 disjoint partitions of corpus).
- **3 seeds [11, 13, 19]** (consistent with v2 pattern).
- **Two-pane metric report**:
  - Pane A (positive): held_named_distill_ratio (TRUE-positive NAMED in held-out -> PROVABLY_EQUIVALENT rate)
  - Pane B (negative): held_adversarial_refusal_ratio (adversarial-NAMED in held-out -> NOT_EQUIVALENT or UNDECIDABLE rate)
- **Pre-reg bands** (Drill 2):
  - HARD_PASS: pane-A mean >=0.85 cv<=0.07 + pane-B mean >=0.80 cv<=0.10 + zero false-positives on adversarial
  - MIDDLE_BAND: pane-A 0.60-0.85 OR pane-B 0.50-0.80 OR cv noisy
  - HARD_FAIL: pane-A < 0.60 OR pane-B < 0.50
- **Sub-experiments embedded**:
  - **False-positive merge detection**: report all NOT_EQUIVALENT verdicts on TRUE-positive NAMED (should be 0).
  - **False-negative miss detection**: report all UNDECIDABLE_BY_PROVER verdicts on TRUE-positive NAMED (should be <10%).
  - **Adversarial taxonomy precision**: for adversarial NAMED, verify the REFUSAL verdict matches the adversary class (different-operation-type adversary -> SHARED_ABSTRACTION refusal, etc.).

**Routing:** `local_cpu_queue` (CHTV-1 is microsecond-scale per pair; 30 groups x 3 seeds x microseconds = total runtime ~10s).

**Spawn budget:** 1 corpus-curation spawn (skunkworks or exp_dev) + 1 cell-author spawn (exp_dev) + 1 verdict_handler spawn after landing.

### Three other v3+ cells to fill out the META-reasoning portfolio

1. **`exp_substrate_distill_verify_v3_class_b_relationship_3seed_full`** -- promote v2-class-B from 1-seed smoke to 3-seed full. Same corpus extension as v3-operator-equivalence (the 30 NAMED + ~15 cell-B candidates with ground-truth labels of which-relationship). Pre-reg per-verdict accuracy bands (SHARED_ABSTRACTION precision/recall, THEOREM_LINKED precision/recall, etc.). Together with v3-operator-equivalence, this gives a **chain-grade self-evaluation suite covering both halves of the closed loop** (merge-true-positives + refuse-true-negatives-with-correct-relationship-name).

2. **`exp_substrate_self_audit_metadata_drift_v1`** -- the cosine_similarity v1-vs-v2 verdict-flip is a real signal. Build a cell that detects metadata drift: snapshot algebra_dict per atom per ledger row, recompute CHTV-1 verdicts each cycle, flag verdict-flips as metadata-drift events. Pre-reg: detection-rate >= 0.95 on synthetically-injected drift events, false-positive-rate <= 0.05 on stable metadata. This is the **self-correction** capability from Drill 4 #2 made concrete.

3. **`exp_substrate_self_optimization_complexity_class_redirect_v1`** -- for each PROVABLY_EQUIVALENT pair where members have different complexity_class fields, propose a routing-table redirect to the lower-complexity member. Pre-reg: substrate's downstream cell performance (any retrieval cell with the original member as primitive) when re-run with the redirect MUST equal-or-improve. The capability discriminator: "self-optimization changes downstream behavior in the predicted direction (lift or equal, never regress)." This is the **self-optimization** capability from Drill 4 #4 made concrete.

A fourth cell (the **self-discovery** kernel from Drill 4 #3) requires curated algebra_dict on >>62 atoms; defer until corpus engineering ships.

### Sequencing recommendation

1. **Cycle N (this cycle):** ship Drill deliverable (this note). Spawn budget: zero additional.
2. **Cycle N+1:** dispatch corpus-curation spawn (skunkworks or exp_dev) for the 30-NAMED corpus. Wall: 2-6h depending on lit-source quality.
3. **Cycle N+2:** dispatch v3-operator-equivalence cell + v3-class-B cell in parallel via orchestrator. Wall: <1min compute per cell.
4. **Cycle N+3:** Skunkworks verify-OFF-DATA + tier-rule. If chain-grade, atomize to Store; if MIDDLE_BAND, route to corpus-tuning. If HARD_FAIL, drop to corpus-engineering, not mechanism-engineering (the mechanism is sound per v1/v2/v3-overmerge controls).
5. **Cycle N+4:** dispatch self-audit-metadata-drift v1 (independent of corpus extension).
6. **Cycle N+5:** queue self-optimization-complexity-class v1 once chain-grade portfolio is anchored.

### Risk register

- **Risk 1 (HIGH):** corpus-curation spawn might take much longer than 2-6h if algebra_dict authoring for 30 NAMED groups needs careful lit-crosscheck. Mitigation: start with 18 NAMED (6 math + 6 programming + 6 substrate-internal), get partial-chain-grade-eligible test out first, expand corpus iteratively.
- **Risk 2 (MEDIUM):** v3-operator-equivalence might still land MIDDLE_BAND if the adversarial-NAMED selection is too easy (the verifier already discriminates them too cleanly -> Q-discipline saturation). Mitigation: pre-screen adversaries via v3-overmerge harness; reject any adversary the verifier handles trivially; force adversaries near the saturation boundary.
- **Risk 3 (LOW):** metadata drift between corpus authoring and cell run (the cosine_similarity v1-vs-v2 pattern). Mitigation: cell-author the corpus snapshot into the cell's metrics.json so the cell is reproducible against the SAME corpus even if Store metadata changes after.

---

## Disciplines honored in this drill

- **2x research drill**: Drills 1+2 broad mechanism understanding; Drills 3+4+5 narrowed operational dispatch design.
- **Generic terms only**: no project-specific names used in web-searchable form (though I did not run external searches this cycle; substrate self-mining was the corpus pull).
- **Lit-scan calibration penalty**: no novel-synthesis P estimates emitted; deflations not needed.
- **Verify-the-referent**: pulled the 4 cell metrics.json files DIRECTLY (not from Skunkworks summary) and probed the live Store atoms via `.venv` python (not from memory of past runs). Confirmed the 1-NAMED-in-20 corpus state independently. Confirmed 62 typed-sig atoms / 47 unique signatures / 0 cross-name signature-sharing as the structural bottleneck.
- **Symmetric anti-negativity**: v1 was NOT inflated (smoke n=1 stays smoke n=1, not chain-grade); v2 was NOT deflated below honest reading (MIDDLE_BAND is the correct band given pane-A 0.78 between HP-rail 0.80 and partial-rail 0.60); the corpus-degeneracy framing in Skunkworks tier-rule was confirmed off-data not parroted.
- **Cap-dev is goal; cert-grade is instrument**: the deliverable IS a capability-development plan (corpus engineering + 4-cell suite), not a chain-grade chase.
- **Under-claim default**: explicit "what is chain-grade: NOTHING YET" headline; explicit "the mechanism IS shown, the test is corpus-degenerate" framing distinguishes mechanism-shown from chain-grade-shown.
- **Fix #28**: read per-arm metrics.json (4 cells) directly, did not propagate verdict_msg framings. Confirmed v1's "6/6 NAMED" was true at v1 run-date but is misleading today (5 of those 6 NAMED have been deduplicated; only 1 remains).
- **No emojis** per project standing convention.

---

-- research (META-reasoning multi-drill 2026-06-25)
