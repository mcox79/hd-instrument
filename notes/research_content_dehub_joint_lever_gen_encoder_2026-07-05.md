# Research: content-embedding de-hubbing as a JOINT lever across the generalization rank-1
# ceiling and the encoder retrieval-agreement gap — mechanism quantified, cell spec'd (SPEC ONLY)

**Filed:** 2026-07-05 by research (Opus off-disk recompute of both content-embedding spaces
directly — no reimplementation of scorer/training code, only raw-embedding-level diagnostics —
plus 2 parallel Sonnet lit-scan sub-agents, generic-math-terms only per query-privacy discipline).
**Spec only — no dispatch.**

**Trigger:** two independently-landed findings that both localize to a content-embedding
neighborhood/hubness problem:
1. `notes/research_hardneg_mined_scorer_v1_spec_2026-07-05.md` — VET-confirmed the generalization
   rank-1 gap's FROZEN-slot hubness lives in the FIXED content-embedding geometry (REAL-vs-SHUFFLED
   Gini nearly identical: V300 CausesDesire 0.980/0.971, AtLocation 0.918/0.927 — a linear/bilinear
   relation transform cannot touch it, Feldbauer & Flexer 2019 PCA/ICA null result). Fair (paired
   REAL-minus-SHUFFLED) rank-1 lift is stuck at **0.0867** (`data/exp_schema_relation_hitsatk_mrr_reframe_v1/metrics.json`,
   `wins[0].slot_rms.FROZEN.hits1`, CausesDesire/bge_semantic @ V300) — confirmed on disk this cycle,
   matches the task's "0.087" figure exactly.
2. `notes/research_encoder_perception_state_buried_win_shipmetric_carrythrough_2026-07-05.md` +
   `data/exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_smoke/metrics.json` — the
   in-batch-RKD encoder's ship-metric forecast: spearman-to-teacher is strong (0.886 held-pair /
   0.848 smoke) but **ret_agree10** (top-10 SET overlap with the BGE teacher's own top-10) sits at
   **0.221 FULL-forecast** (verified this cycle from `exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_core.py`
   line 18/64: "INBATCH_BLOCK ret_agree10 vs teacher mean 0.221 range [0.184,0.266]... MISSES the
   0.30 gate on all 5 seeds") / 0.333 in the smoke that already landed HARD_PASS-on-machinery.

Both are a "strong aggregate rank agreement, weak exact top-k/top-1 identity" signature — the
textbook hubness fingerprint. This note tests whether they are the SAME content-geometry problem
(a genuine joint lever) or two coincidentally-similar problems, by direct off-disk measurement of
BOTH content-embedding spaces (not by inference from the two prior notes' prose).

---

## HEADLINE

**The hubs are NOT literally the same index/matrix — but the underlying mechanism is genuinely
shared, with a measurable, non-trivial shared-INSTANCE component, not merely a shared mechanism
class.** Verified directly this cycle:

- **Different spaces, confirmed on disk:** the generalization content is `BAAI/bge-small-en-v1.5`
  (384-dim) over 9,340 ConceptNet-style commonsense entity strings
  (`data/datasets/bge_small_schema_TEM_entities_v1.npz`); the encoder's teacher content is BGE-large
  (1024-dim) over 177,899 concept names (`data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz`,
  keys `semantic`/`composite`, id-namespaced e.g. `T1/vector_space`, `CN_print_shop`). Different
  checkpoint, different dimensionality, different corpus size — literally one shared vector index
  is FALSE.
- **But 49.4% direct vocabulary overlap:** of the 9,340 schema entities, 4,613 appear byte-for-byte
  (case-insensitive, `CN_`-prefix-stripped) inside the encoder's teacher pool (133,305 of the
  177,899 concepts carry the `CN_` ConceptNet-origin prefix; the other namespaces — T1/T2/T3, PHYS,
  BIO, CHEM, NEURO, RF, MWP, SCHOOL, CROSSDISC — are the substrate's own technical/domain KB and do
  not overlap). This is the SAME underlying real-world entity set, independently embedded twice.
- **Among that overlap, hub status correlates across the two independently-trained, differently-
  scaled checkpoints: Spearman rho = 0.545 (p ~ 0, n=4,613)** on the object-side k-occurrence (Nk,
  k=10, cosine) distribution. The SAME literal category words top BOTH hub lists independently —
  `food`, `animal`/`animals`, `clothing`, `people`/`person`, `drink`/`drinks`, `human`/`humans` —
  and the top-50 hub sets overlap 16/50 (32%) vs ~0.5/50 (1%) expected under independence. This is a
  genuinely novel measurement (no literature found testing cross-model hub-identity correlation
  directly; see Section 2) and it says hub status here is **substantially an intrinsic property of
  an entity's own semantic generality** (broad superordinate category nouns sit near the centroid of
  almost any general-domain sentence-embedding space, by construction of what "generality" means),
  **not an idiosyncratic artifact of one specific BGE checkpoint** — while rho=0.545 (not ~1.0) also
  says this is real but PARTIAL: roughly 30% of rank-variance is shared, ~70% is checkpoint/corpus-
  specific. This partial-not-total picture is independently corroborated by the KG-embedding
  literature (Obraczka & Rahm 2021; Fanourakis et al. 2023, ESWC — both directly read by lit-scan):
  hub severity is real-but-method-modulated, "degree-driven bias direction consistent across most
  methods, magnitude/robustness method-specific" — exactly the shape of the rho=0.545 result.
- **Raw content-geometry hubness is real but more moderate than the scorer-compounded numbers
  already on record:** direct Nk10-Gini on the raw embeddings (no trained scorer in the loop) is
  **0.372** (schema, bge-small, full n=9,340) and **0.468** (encoder teacher, bge-large, n=6,000
  random subsample) — genuinely hub-laden (textbook skew, well above a uniform null) but well below
  the 0.87-0.98 Gini the parent hubness note measured on the TRAINED SCORER's argmax-winner
  distribution at V=300. Reading: **the trained scorer + label-frequency layer compounds heavily on
  top of a real but more moderate raw-content hub floor** — content-embedding de-hubbing is a
  necessary-but-likely-partial lever, not the whole story (consistent with the residual-decomposition
  caveat below).
- **Both downstream signatures are the SAME qualitative hubness fingerprint, independently
  re-confirmed this cycle**: generalization's filtered Hits@10 clears while Hits@1/MRR does not
  (FROZEN CausesDesire Hits@1 rms=0.087 vs Hits@10 rms=0.653); encoder's rank-correlation is strong
  (spearman 0.886/0.848) while exact top-10 SET agreement with the teacher is weak (ret_agree10
  0.221-0.333) — this is precisely the pattern the hubness literature predicts when a handful of
  generic/central points contaminate exact top-k neighbor SETS without much disturbing the broad
  rank ORDER (Radovanović et al. 2010; corroborated directly this cycle by Nielsen, Macocco & Baroni,
  AISTATS/NLDL 2024, arXiv:2311.18364, on the closest available direct analog — hubness reduction on
  Sentence-BERT-family embeddings, the SAME embedding family BGE belongs to).

**Verdict on the task's core question: genuine JOINT lever, not two coincidentally-similar
problems — but a MECHANISM-shared, INSTANCE-partially-shared lever, not a literal one-index fix.**
A single de-hubbing methodology, applied independently to each content space, has a real,
quantified prior (rho=0.545, corroborated qualitatively by KG-embedding degree-persistence
literature) for helping both — but it is genuinely untested at the specific, mechanistically
distinct application point this spec proposes (pre-training content transform + retrain-from-
scratch, NOT the post-hoc score-rescoring already tried and found partially phantom on this exact
FROZEN locus).

---

## 1. MECHANISM — off-disk recompute (both content spaces, methodology reported in full)

### 1a. Confirming the two spaces are genuinely different checkpoints/corpora

| | Generalization content | Encoder teacher content |
|---|---|---|
| Model | `BAAI/bge-small-en-v1.5` | BGE-large (`bge_large_v2_name_*` cache family) |
| Dim | 384 | 1024 |
| Corpus | 9,340 ConceptNet-style commonsense entities (schema relation objects) | 177,899 concept names (substrate's own KB: ~75% `CN_`-prefixed ConceptNet-derived + 19 technical namespaces T1-T4/PHYS/BIO/CHEM/NEURO/RF/MWP/SCHOOL/CROSSDISC/SELF/META) |
| File | `data/datasets/bge_small_schema_TEM_entities_v1.npz` | `data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz` |
| Downstream use | frozen features `Fo` -> bilinear relation scorer `W` | frozen teacher target for in-batch RKD distillation of a sparse-code MLP student |

Confirmed by direct `.npz` inspection this cycle (model field, shape, dtype) — not asserted from
either prior note's prose.

### 1b. Vocabulary overlap and cross-model hub correlation (the decisive new measurement)

Method: intersect the 9,340 schema entity strings against the encoder's `CN_`-prefixed concept
names (leaf name after stripping `CN_`, case-insensitive) -> **4,613 exact matches** (49.4% of the
schema vocabulary). For this aligned subset, extract the SAME entities' embeddings from BOTH spaces
(bge-small 384d subset, bge-large 1024d subset) and compute, independently in each space: L2-
normalize, cosine similarity matrix, top-k=10 nearest-neighbor lists (excluding self), object-side
k-occurrence count Nk (how many times each object appears in another query's top-10).

| | n | Gini(Nk10) | max Nk10 | mean Nk10 |
|---|---|---|---|---|
| bge-small (schema), overlap subset | 4,613 | 0.372 | 91 | 10.0 |
| bge-large (encoder teacher), overlap subset | 4,613 | 0.384 | 109 | 10.0 |

**Spearman rho(Nk_bge-small, Nk_bge-large) across the 4,613 shared entities = 0.545 (p ~ 0).**
Top-15 hubs in each space (independently computed, no cross-referencing during computation):

- bge-small: food(91), animal(76), animals(69), room(63), clothing(59), humans(54), human(53),
  drink(53), dogs(51), clothes(50), air(48), snack(47), people(47), person(46), water(45)
- bge-large: food(109), people(70), outside(66), clothing(66), snack(65), home_appliance(62),
  animal(61), person(58), learn(54), ketchup(53), animals(52), fun(51), drinks(51), humans(51),
  appliance(50)

Top-50 hub-rank overlap: **16/50** — vs an expected ~0.5/50 under independence (50 x 50 / 4,613).
**Reading:** hub status for a SPECIFIC entity is substantially, but not fully, invariant across two
independently-trained checkpoints of very different scale (small vs large) trained on different
data. Superordinate/generic category nouns (food, animal, clothing, person) are geometric hubs
almost regardless of which general-purpose sentence-embedding model produces the space — a genuine,
directly-measured (not merely inferred) shared mechanism. This appears to be a novel measurement:
neither lit-scan sub-agent found a paper directly testing cross-model hub-identity correlation on
overlapping vocabulary (flagged, own synthesis, novel-synthesis cap applies).

### 1c. Full-scale raw content-geometry hubness (no scorer in the loop)

Method: full n=9,340 for schema (tractable, O(n^2)=87M pairs); random n=6,000 subsample of the full
177,899 for the encoder teacher (tractable; representative of the actual Step2/RKD training pool,
not restricted to the ConceptNet-overlap subset).

| | raw Gini(Nk10) | raw max |
|---|---|---|
| schema (bge-small, full n=9,340) | 0.372 | 92 |
| encoder teacher (bge-large, n=6,000 subsample) | 0.468 | 312 |

**Reading:** both content spaces are genuinely hub-laden (well above a uniform null, textbook
skew), and the encoder-teacher space is if anything MORE concentrated at this larger scale
(0.468 vs 0.372) — consistent with hubness worsening as intrinsic-dimensionality-to-ambient-
dimensionality ratio and corpus scale increase (Radovanović et al. 2010). Both Gini values are well
below the 0.87-0.98 measured on the TRAINED scorer's argmax-winner distribution in the parent note
— **the raw content floor is real but moderate; the scorer + label-frequency layer compounds
heavily on top of it.** This bounds expectations: de-hubbing the CONTENT alone should not be
expected to recover the full 0.87-0.98-Gini-scale compounding, only the content-geometry component
of it (see the stratified prediction in 1e).

### 1d. Candidate de-hub method comparison — own off-disk Nk-Gini reduction, both spaces

All four candidates the task named were run directly (training-free, applied to the raw embedding
matrices, no scorer/label information used):

| Method | schema raw->post Gini | encoder raw->post Gini |
|---|---|---|
| **raw (no transform)** | 0.372 | 0.468 |
| All-but-the-Top, D=1 (Mu & Viswanath 2018: subtract mean + top-1 PC) | 0.372 -> 0.328 | 0.468 -> 0.355 |
| All-but-the-Top, D=2 | 0.372 -> 0.325 | 0.468 -> 0.344 |
| All-but-the-Top, D=3 | 0.372 -> 0.327 | 0.468 -> 0.333 |
| ZCA whitening (full covariance) | 0.372 -> **0.297** | 0.468 -> **0.259** |
| **Local Scaling** (Zelnik-Manor & Perona 2004; nonlinear, distance-distorting similarity rescore) | 0.372 -> **0.202** | 0.468 -> **0.260** |

**Reading, mapped directly onto the pick-by-merit instruction:**
- ABTT (D=1-3) is the **weakest** de-hub method in both spaces, consistently — matches the lit-scan
  finding that the ABTT source paper (Mu & Viswanath 2018, arXiv:1702.01417, directly read by
  lit-scan) makes **no hubness claim at all**; it targets anisotropy, a related-but-distinct
  property, and low-rank component removal is exactly the class of "linear, non-distance-distorting"
  transform Feldbauer & Flexer (2019) predict to underperform.
- ZCA whitening (full-rank, but still linear/orthogonal + rescale) is **stronger than ABTT and close
  to Local Scaling** — directly precedented by Su et al. (2021, arXiv:2103.15316, fetched/verified:
  full-covariance whitening beats BERT-flow +9.6 STS points), though that paper frames its gain via
  anisotropy/dimensionality, not hubness explicitly.
- **Local Scaling is the strongest reducer on schema content and ties ZCA on encoder content** —
  and is the training-free method with the closest DIRECT external precedent on a Sentence-BERT-
  family embedding space (the same family BGE belongs to): Nielsen, Macocco & Baroni (AISTATS/NLDL
  2024, arXiv:2311.18364, fetched/verified) combine per-dimension normalization with Mutual
  Proximity (Local Scaling's close cousin) and report skewness 6.06-8.79 -> 0.42 and ~7-9% error
  reduction across 4 SBERT variants on 20 Newsgroups — the single most directly analogous, most
  strongly verified external result found this cycle.

**Pick: Local Scaling is the lead/primary training-free candidate** (empirically strongest-or-tied
on our own data, best-precedented on the closest available analog task/embedding family). ZCA
whitening is retained as a cheap, well-precedented secondary arm (nearly ties Local Scaling on the
encoder side, worth a fair head-to-head). ABTT is retained only as a reference/weakest-expected arm
— included to test, not to lead with, the falsifiable prediction that low-rank linear removal
underperforms both.

### 1e. Why this is NOT a repeat of the already-tried (partially phantom) post-hoc rescore

The already-landed `exp_schema_relation_hubness_debias_rescore_v1` applied CSLS + logit-adjustment
to an **already-converged FROZEN scorer's OUTPUT SCORES**, post-hoc — and measured that this is
**structurally incapable of helping without collateral damage** on the content-baked locus
specifically (monotonic REAL degradation as correction strength increases, apparent rms "win" 100%
attributable to a SHUFFLED-arm collapse). The mechanistic reason (per that note, Section 1a/1b,
grounded in Feldbauer & Flexer's PCA/ICA null result plus a Bayes-consistency argument, Gordon-
Rodriguez et al. 2020): a linear/bilinear map already fit to a biased marginal has no "W-induced
excess" to subtract — the excess mass sits in the object geometry itself, and any global rescoring
of its OUTPUT strips real per-query discrimination the map already learned, along with the bias.

**This spec is deliberately a different application point, not a re-run:** it transforms the
CONTENT EMBEDDING INPUT itself, BEFORE any downstream fit, and retrains the relation-scorer /
distillation student FROM SCRATCH on the de-hubbed features. There is no "already-fitted-to-bias"
collateral to strip, because nothing has been fit yet. Both lit-scan sub-agents searched
specifically for a direct "de-hub before training" vs "de-hub after convergence" comparison in any
domain and **found none** — this is a genuine, first-of-its-kind, falsifiable test for this
substrate, not a rerun of a result already on record.

**Important honest caveat, pre-registered as a stratified secondary prediction (per the fanout-
tercile-diagnostic discipline already established in the hardneg_mined_scorer spec):** the parent
hubness note's residual-decomposition showed the two HP-eligible relations sit at DIFFERENT points
on the geometric-hubness <-> label-prior spectrum — AtLocation is a genuine MIX (residual Gini
0.175 after regressing out training frequency: real geometric hubness survives) while CausesDesire
is almost ENTIRELY label-prior-driven (residual Gini 0.077: almost nothing survives once frequency
is removed). A pure content-embedding de-hub transform touches ONLY the geometric component. It is
therefore predicted, before running, to help **AtLocation more than CausesDesire** — and the current
>=2-relation HARD-PASS convention (which, on this cell family, currently has exactly these two
semantic relations available) may be structurally hard to clear on BOTH simultaneously via this
lever alone. This is reported as a diagnostic, NOT folded into the primary joint-lever gate, exactly
as fanout-stratification was reported (not gating) in the prior spec — conflating the two would
corrupt the falsification test of the JOINT-LEVER claim itself.

---

## 2. Lit-scan citations (2 parallel Sonnet sub-agents, generic math/stats terms only)

1. Radovanović M, Nanopoulos A, Ivanović M (2010) Hubs in Space. *JMLR* 11:2487-2531. — carried
   forward; canonical hubness mechanism (spatial centrality -> disproportionate nearest-neighbor
   frequency).
2. Feldbauer R, Flexer A (2019) A comprehensive empirical comparison of hubness reduction in
   high-dimensional spaces. *Knowledge and Information Systems*. — carried forward (snippet-level
   re-confirmation this round, direct fetch failed/paywalled): linear rotations (PCA/ICA/SNE) do not
   reduce hubness unless truncated below intrinsic dimension; nonlinear distance-distorting methods
   (Isomap, diffusion maps) do, even above intrinsic dimension. Centering/mean-subtraction flagged as
   a narrower, related-but-distinct family (Suzuki et al. 2013) vs ABTT's mean+top-D removal.
3. **Nielsen A, Macocco K, Baroni M (2024) Hubness Reduction Improves Sentence-BERT Semantic
   Spaces.** AISTATS/NLDL, arXiv:2311.18364. — VERIFIED (fetched via ar5iv). Diagonal per-dimension
   normalization (f-norm) + Mutual Proximity: k-skewness 6.06-8.79 -> 0.42 on 20 Newsgroups; error
   rate down ~7-9% (p<2.1e-9) across 4 SBERT variants. **Closest direct analog available**: same
   embedding family (Sentence-BERT / BGE lineage), directly confirms Local-Scaling-family methods
   are the strongest training-free hub-reducer on THIS kind of space. Does not test full ZCA or
   ABTT head-to-head against MP.
4. Su J et al. (2021) Whitening Sentence Representations for Better Semantics and Faster Retrieval.
   arXiv:2103.15316. — VERIFIED (fetched). Full-covariance (ZCA-like) whitening of BERT sentence
   embeddings beats BERT-flow +9.6 STS-B points. Frames gain via anisotropy/dimensionality, NOT
   hubness explicitly — the whitening-hubness connection used in this note's Section 1d is this
   note's own bridging inference, not the source paper's claim (flagged).
5. Mu J, Viswanath P (2018, w/ Bhat S) All-but-the-Top: Simple and Effective Postprocessing for Word
   Representations. ICLR workshop, arXiv:1702.01417. — VERIFIED (fetched, direct text read).
   **Confirmed: the paper never mentions hubness, k-occurrence, Nk, Gini, or Radovanović** — frames
   the problem entirely as isotropy/downstream accuracy. The ABTT<->hubness link in this note's own
   Section 1d is an inference, not a claim the source paper makes.
6. Zelnik-Manor L, Perona P (2004) Self-Tuning Spectral Clustering. — origin of Local Scaling;
   carried forward, cited via Feldbauer & Flexer, not independently re-fetched this round.
7. Obraczka D, Rahm E (2021) An Evaluation of Hubness Reduction Methods for Entity Alignment with
   Knowledge Graph Embeddings. KEOD. — VERIFIED (direct read this round). 240 KGE-method pairs: hub
   magnitude (Robin Hood index) varies drastically BY METHOD on the SAME knowledge graph (e.g.
   BootEA low-hub even uncorrected; SimplE ~75% Robin Hood on the same dataset) — hubness severity is
   method-dependent, not a pure entity/degree property. Directly informs this note's rho=0.545
   ("real but partial, method-modulated") reading rather than expecting near-total transfer.
8. Fanourakis N et al. (2023) ESWC workshop — entity-alignment robustness across RREA/MultiKE/PARIS/
   RDGCN. — VERIFIED (direct read). Node-degree/structural measures correlate with alignment
   accuracy (Spearman up to 0.93) for structure-only methods; RDGCN (uses entity NAMES as extra
   signal, closer in spirit to BGE-style semantic embedding) is substantially more robust to this
   bias — suggestive that semantically-grounded embeddings (like BGE) partially, not fully, escape
   pure degree/frequency-driven hubness, consistent with this note's moderate (not near-1.0)
   rho=0.545.
9. Wu Z et al. (2024) The Semantic Hub Hypothesis. arXiv:2411.04986. — VERIFIED as a **false friend**:
   a different, unrelated use of "hub" (shared cross-lingual/cross-modal representation convergence),
   not nearest-neighbor hubness; explicitly excluded from this note's claims.
10. Menon AK et al. (2021) Long-Tail Learning via Logit Adjustment. ICLR. — carried forward from
    prior notes; NOT the mechanism this spec targets (label-prior, not content-geometry) but retained
    as the correct complementary fix for the CausesDesire-class relations per the stratified
    prediction in 1e.
11. Park W et al. (2019) Relational Knowledge Distillation. arXiv:1904.05068. — carried forward;
    the base RKD objective this spec proposes substituting a de-hubbed target INTO.

**Verified count: 3 newly, directly fetched this round (Nielsen/Macocco/Baroni 2024, Su et al. 2021,
Mu & Viswanath 2018 full-text confirmation of the negative claim), 2 directly-read secondary sources
(Obraczka & Rahm 2021, Fanourakis et al. 2023), 1 explicitly-excluded false-friend (Wu et al. 2024),
5 carried forward from prior notes (re-used, not re-verified this round) — cross-checked by 2
independent Sonnet lit-scan sub-agents, generic-math-terms queries only per query-privacy
discipline, plus this note's own direct off-disk recompute of both content-embedding spaces (Section
1), not asserted from either prior note's metrics.json prose alone.**

**Explicitly-flagged literature gaps (both lit-scans searched and found nothing):** (a) no paper
directly compares "de-hub before training" vs "de-hub after convergence" in any domain; (b) no paper
combines a hub-reduction transform (local scaling / mutual proximity) with a knowledge-distillation
loss, or uses a hub-aware distance transform as the distillation TARGET; (c) no paper directly tests
cross-model hub-identity correlation on overlapping vocabulary the way Section 1b does here. All
three gaps are exactly what the proposed cell (Section 3) tests — genuinely novel-synthesis
territory, P capped accordingly below.

---

## 3. ENVELOPE — falsifiable cell spec (SPEC ONLY, no dispatch)

**Proposed cell name:** `exp_content_dehub_joint_lever_v1`

**Design (reuse, don't rebuild; one shared transform module, two harnesses):**

A single `dehub_transforms.py`-style module implementing the three candidates as pure functions on a
raw embedding matrix (no label/scorer information used): `local_scaling(X, k=10)` (PRIMARY),
`zca_whiten(X, eps=1e-3)` (SECONDARY), `abtt(X, D=1)` (REFERENCE/weakest-expected). Each is applied
BEFORE any downstream training, on the CONTENT EMBEDDING INPUT — never as a post-hoc score rescore
(that lever is `exp_schema_relation_hubness_debias_rescore_v1`, already run, already shown partially
phantom on this exact locus; not repeated here).

**Generalization side** — reuse `exp_schema_relation_hitsatk_mrr_reframe_v1.py` harness verbatim
(same V-scan, same relations AtLocation/CausesDesire semantic + DerivedFrom watchdog, same 2
encodings, same 3 seeds, same paired REAL/SHUFFLED arms, same inductive/transductive modes, same
`filtered_ranks`/`rank_metrics` functions). **The only change:** transform the raw entity feature
matrix `Fo` (the V x 384 bge_semantic slice) via each de-hub method BEFORE
`encode_feature_matrix`/`fit_scorer_paired` is called, then retrain BOTH FROZEN and JOINT scorers
FROM SCRATCH on the transformed features (paired REAL/SHUFFLED per arm per slot, same discipline as
the family). Control arm: `CONTENT_RAW` = byte-identical reproduction of the already-landed reframe
cell (fresh baseline, not the already-tried rescore cell).

**Encoder side** — reuse `exp_encoder_step2step3_inbatch_rkd_shipmetric_carrythrough_v1_core.py`
harness verbatim (same in-batch-RKD-only objective, nce_weight=0, same Step2/Step3 chain). **The
only change:** transform the BGE-large teacher embedding matrix via the SAME method (dimension-
agnostic hyperparameters carried over unchanged, e.g. k=10 for local scaling) BEFORE computing the
in-batch RKD relational target (the distance-wise/angle-wise pairwise structure the student is
trained to match), then retrain the student MLP+block-STE encoder FROM SCRATCH against the
de-hubbed teacher target. **Ground truth for evaluation is NOT changed**: `ret_agree10` is measured
against the UNCHANGED original raw-teacher top-10 throughout (de-hubbing is a training-time lever,
not a redefinition of the ship metric — changing the evaluation target would manufacture an
uninterpretable win).

**New required diagnostic (informative, not gating):** compute the STUDENT's own retrieval-Nk-Gini
(k-occurrence Gini of the student's own top-10 retrieval sets across held queries), before and after
de-hub training, alongside the raw teacher's own Nk-Gini. This directly tests the "open, not
reconciled" question flagged in the hardneg_mined_scorer note (Section 1b: is JOINT-slot/distillation
hubness partly a DISTILLATION-INDUCED AMPLIFICATION — student more hub-collapsed than its own
teacher, a dimensional-collapse-under-distillation signature per Jing et al. 2022 — or purely
INHERITED teacher-content hubness, student roughly matching the teacher's Gini). Reported per-arm,
not folded into the HP/HF gate.

**Controls (mirrors established family discipline + one new joint-lever-specific control):**
- Paired REAL/SHUFFLED per arm per slot (existing discipline; SHUFFLED arm's de-hub transform and
  retraining run independently from its own permuted labels, never borrowed from REAL).
- `synth_content_baked_hub` (POSITIVE, reused from hardneg_mined_scorer spec): by-construction
  geometric-hub synthetic content generator; de-hub must measurably narrow the constructed bias.
- `synth_ambiguous_null` (NEGATIVE, reused): genuinely ambiguous synthetic regime; de-hub must not
  manufacture a fake win (Bayes-consistency guard, Gordon-Rodriguez et al. 2020).
- **`synth_cross_domain_shared_hub` (NEW, joint-lever-specific POSITIVE control):** construct TWO
  independent synthetic content spaces (different dimensionality, different generator seed) that
  share a DESIGNED common subset of items with elevated centrality (mirroring the measured
  rho=0.545 cross-model property from Section 1b, but by construction). Verify the SAME de-hub
  transform, fit and applied INDEPENDENTLY to each synthetic space, measurably reduces Nk-Gini in
  BOTH — a by-construction positive control for the JOINT-LEVER claim itself (not just a per-domain
  hubness claim), directly testable before spending compute on the two real downstream harnesses.
- `SHUF_OVERFIT_GUARD` (reused from hardneg_mined_scorer spec, applies here too since this is a
  retrain-from-scratch, not a post-hoc rescore): SHUFFLED arm's absolute inductive Hits@1 (gen side)
  / SHUFFLED-arm retrieval metrics (encoder side, using a permuted teacher-target control) must not
  rise more than +0.03 absolute over the matched CONTENT_RAW/CE_BASELINE SHUFFLED value.

**HP_SCOPE:** `{LOCAL_SCALING: [gen: best-of-{FROZEN,JOINT} filtered Hits@1/MRR rms; enc:
ret_agree10, cosine_to_gold non-regression, composed_roundtrip non-regression]}`. ZCA_WHITEN and
ABTT are reference/secondary arms, reported not primary-gated (per "pick the lead by merit, run
others as reference" instruction) — but ZCA_WHITEN clearing where LOCAL_SCALING does not would
itself be an actionable, reportable finding, not discarded.

### Falsifiable predictions

**HARD-PASS** (task's bands, restated formally): LOCAL_SCALING (the primary arm) delivers, with all
controls firing as specified above:
- Generalization: best-of-{FROZEN,JOINT} filtered Hits@1 REAL-minus-SHUFFLED rms lift **>= +0.05
  absolute** over the matched CONTENT_RAW control, on **AtLocation AND CausesDesire** (>=2 relations)
  x >=2 encoders at V>=300 — **AND**
- Encoder: `ret_agree10` lift **>= +0.05 absolute** over the matched (retrained, de-hub-free)
  CONTENT_RAW control, with `cosine_to_gold` and `composed_roundtrip` not regressing below their
  own pre-registered floors (0.80 / 0.95) — **AND**
- `synth_cross_domain_shared_hub` fires (Nk-Gini reduces in BOTH synthetic spaces) — **AND**
- `SHUF_OVERFIT_GUARD` holds on both sides.

**HARD-FAIL**: LOCAL_SCALING's lift is **<= +0.02** on EITHER side (generalization OR encoder) —
i.e., the "joint lever" claim is falsified even if one side shows a real, non-phantom improvement,
because the task explicitly requires BOTH to move for this to be a genuine joint lever rather than a
single-domain hubness fix. If this happens, fall back to reporting whichever single side (if any)
cleared its OWN domain-specific bar (>=+0.05, non-phantom) as a standalone finding — informative,
but not a joint-lever HARD-PASS.

**MIDDLE-BAND** (the most likely outcome given (i) the stratified AtLocation-vs-CausesDesire
prediction in Section 1e, which argues content-geometry de-hub should help AtLocation more than
CausesDesire, and (ii) the raw-content-Gini-vs-scorer-Gini gap in Section 1c, which argues content
de-hub alone should not be expected to close the FULL compounding): lift clears +0.05 on ONE side
(most likely: generalization/AtLocation specifically, OR encoder ret_agree10, which has never had
ANY de-hub attempt before and is the "cleaner" first test of this specific application point) but
not both, OR clears on AtLocation but not CausesDesire specifically (the predicted stratified
split) — this would confirm the mechanism is REAL and the pre-training application point IS more
tractable than the already-tried post-hoc rescore, while showing the joint claim needs the
complementary label-prior fix (Menon et al. 2021 logit-adjustment, already spec'd) layered on top
for full-recovery on label-prior-dominant relations, rather than either declaring the joint-lever
question closed or re-running content de-hub alone expecting a bigger effect.

**Cardinality / compute:** heavier than either previously-run cell alone (this one retrains BOTH
harnesses from scratch, x3 de-hub methods x2 arms REAL/SHUFFLED), but each individual training run
reuses proven, already-cheap code paths (schema side: same ~7-10 min FULL as the reframe family;
encoder side: same cheap in-batch-RKD-only retrain, no landmark/InfoNCE term, per the carry-through
cell's own cost estimate). Expect roughly 3x the generalization family's own wall-clock (3 de-hub
methods) plus 1x the encoder carry-through cell's wall-clock (de-hub is a cheap vectorized
pre-processing step on top of an already-cheap retrain, not an added order of magnitude).

---

## Cheap decisive test

This note's own off-disk measurement (Section 1: vocabulary overlap, cross-model Nk correlation,
raw-content Gini in both spaces, and Nk-Gini reduction under 3 candidate transforms) IS the cheap
decisive test for whether a joint lever is even worth building — answer: yes, a genuine, moderate-
strength, directly-measured shared mechanism (rho=0.545, 49.4% vocab overlap, matching top-hub
identities, matching qualitative downstream signature on both tasks). The proposed cell is the next
cheap test: whether CORRECTING it, at a genuinely untested (pre-training, not post-hoc) application
point, moves both downstream metrics as the shared-mechanism evidence would predict.

## Cross-thread synthesis

- Directly extends `notes/research_hubness_popularity_debias_rank1_sharpening_2026-07-05.md` and
  `notes/research_hardneg_mined_scorer_v1_spec_2026-07-05.md`: takes their content-baked-locus
  finding (FROZEN-slot hub concentration lives in the fixed object geometry, immune to post-hoc
  rescore and to a linear/bilinear relation transform) and asks whether the SAME finding, tested at a
  genuinely different application point (pre-training, not post-hoc), transfers to a SECOND,
  independently-diagnosed capability track (`notes/research_encoder_perception_state_buried_win_shipmetric_carrythrough_2026-07-05.md`'s
  ret_agree10 gap) sharing a partially-overlapping content vocabulary.
- Does NOT re-run the already-landed `exp_schema_relation_hubness_debias_rescore_v1` (post-hoc
  score rescore, MIDDLE_BAND/phantom-on-FROZEN) or pre-empt `exp_schema_relation_hardneg_mined_scorer_v1`
  (trained margin+mining, not yet dispatched) — this is a THIRD, mechanistically distinct lever
  (content-input transform + retrain-from-scratch) applied to BOTH the already-studied generalization
  locus and the newly-implicated encoder locus, not a repeat of either prior spec.
- The stratified AtLocation-vs-CausesDesire prediction (Section 1e) is a direct, falsifiable
  extension of the parent hubness note's own residual-decomposition (geometric-mix vs label-prior-
  dominant relations) — if this cell's per-relation results do NOT follow that predicted split, that
  itself would be informative (it would suggest the residual-decomposition framing under-explains
  what a genuinely fresh retrain on de-hubbed features actually recovers).
- Ties into the KG-embedding literature's "hubness is real-but-method-modulated" finding (Obraczka &
  Rahm 2021; Fanourakis et al. 2023) as the closest available external grounding for WHY rho=0.545
  (not near-1.0) is the right order of magnitude to expect, rather than either "fully shared" or "not
  shared at all."

## Substrate-product implications

If the proposed cell clears joint HARD-PASS, the product story becomes unusually strong: **one
mathematical fix (a training-free content-embedding transform, applied once per content space before
any downstream training) measurably improves two capability tracks that looked, until this cycle,
like unrelated stuck-points** — a genuine unification, not a coincidence of two separately-tuned
fixes, backed by a directly-measured (not assumed) shared root cause (rho=0.545 cross-model hub
correlation on real overlapping vocabulary). If it lands MIDDLE (the more likely outcome per Section
1e/1c), the honest sharpening is still valuable and non-trivial: it would show the content-geometry
component of both problems IS reachable by a genuinely different application point than what has
already been tried (pre-training vs post-hoc), localizing exactly how much of each capability's
ceiling is content-geometry-driven vs label-prior/distillation-dynamics-driven, and giving a
concrete, falsified-or-confirmed answer to whether "de-hub once, benefit twice" is a real product-
level lever or an appealing-but-false economy. If it HARD-FAILs on both sides, that is itself
informative: it would mean the content-geometry locus, even attacked at the least-yet-tried
application point (pre-training transform, not post-hoc score correction), is genuinely resistant to
training-free correction for THIS substrate's specific corpora — motivating either a heavier
nonlinear re-embedding (nonlinear nonlinear kernel/Isomap-class methods, not yet tried) or accepting
the content-geometry ceiling as a structural property of BGE-family embeddings at these corpus
scales, distinct from (and cheaper to have ruled out than) either of the label-prior/margin-loss
fixes already spec'd for the generalization side alone.

## Citations (verified count)

See Section 2: 3 newly directly-fetched this round (Nielsen/Macocco/Baroni 2024, Su et al. 2021, Mu
& Viswanath 2018 full-text negative-claim confirmation), 2 directly-read secondary sources
(Obraczka & Rahm 2021, Fanourakis et al. 2023), 1 explicitly-excluded false-friend identified and
ruled out (Wu et al. 2024 "Semantic Hub Hypothesis"), 5 citations carried forward from the two prior
notes in this thread (not re-verified this round, already verified previously) — cross-checked by 2
independent Sonnet lit-scan sub-agents (generic-math-terms queries only, no substrate-novel mechanism
names sent off-platform, per query-privacy discipline), plus this note's own direct off-disk
recompute of BOTH content-embedding spaces from their raw `.npz` files (not asserted from either
prior note's metrics.json prose or from inference alone).

## P_deflated

**P_deflated(joint HARD-PASS as spec'd, i.e. LOCAL_SCALING clears BOTH generalization >=+0.05 AND
encoder ret_agree10 >=+0.05, with all controls firing) = 0.20.** Raw estimate ~0.35-0.40: the shared-
mechanism evidence is unusually strong for a novel-synthesis claim (directly-measured rho=0.545, not
merely argued; a well-precedented training-free method on the closest available direct analog,
Nielsen/Macocco/Baroni 2024's own SBERT-family result; a genuinely different, untested application
point relative to the already-partially-phantom post-hoc rescore). Deflated by ~0.15-0.20 for: (a)
the stratified prediction in Section 1e argues content-geometry de-hub is mechanistically UNLIKELY to
move the label-prior-dominant relation (CausesDesire) much, and the current HP_SCOPE convention needs
BOTH semantic relations to clear — a real, identified, non-hand-wavy reason the strict joint bar may
be structurally hard to clear via this lever alone; (b) no direct precedent exists for the "de-hub
before training, not after" comparison in ANY domain (both lit-scans confirmed this gap), nor for
hub-aware RKD distillation targets — both are genuinely first-of-their-kind for this substrate; (c)
the strict two-task AND-conjunction compounds two already-uncertain individual outcomes. Capped
within the 0.50 novel-synthesis ceiling regardless per [[feedback-lit-scan-calibration-penalty]],
since the "one lever, two capability tracks" claim is this note's own synthesis, not a cited direct
result.

**P_deflated(at least one side shows a genuine, non-phantom, >=+0.05 lift — i.e., the mechanism is
reachable at this application point even if the strict joint claim doesn't fully clear) = 0.48**
(capped just under the 0.50 novel-synthesis ceiling; higher confidence here since this is a
materially easier bar, the encoder side is a genuinely first attempt at ANY de-hub lever with no
prior negative result on record, and the AtLocation-class geometric-hub relation on the
generalization side has real headroom per Section 1e's stratified reasoning).

**Confirmed (not a prediction — directly measured this cycle): the hub mechanism IS meaningfully
shared across the two content spaces** (rho=0.545, p~0, n=4,613; 49.4% vocabulary overlap; 16/50
top-hub identity overlap vs ~0.5/50 chance) — this is reported as an empirical finding, not a
calibrated forecast, since it was measured directly rather than inferred.
