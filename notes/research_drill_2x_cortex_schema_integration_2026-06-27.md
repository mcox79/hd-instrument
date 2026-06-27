# Research drill 2x — cortex schema integration from ultrametric clusters

**Filed by:** research (Opus 4.7 1M)
**Filed:** 2026-06-27
**Trigger:** Cortex content extraction (ultrametric clustering) hit CHAIN_GRADE today (CERT 623). Gap #1 = converting cluster-assignments into reusable schema atoms the substrate can compose with. USER directive: very careful that it's a fair experiment.
**Constraint:** `cortex_schema_integration_from_ultrametric_v1` prereg authored in parallel by cortex-closure agent a0bc3f2cc9f70b4be — this drill INFORMS top-2 picks and pressure-tests fairness; does NOT author the prereg.
**Lit-scan penalty applied:** P_deflated 0.15-0.25; novel-synthesis cap 0.50.

---

## ANGLE A — pure math / info-theory: minimum-description-length compression

The question: given a cluster of N atoms with centroid mu and covariance Sigma, what's the smallest object that preserves enough to (a) recognize new cluster members at retrieval, (b) not collide with other schemas in the substrate's bind algebra?

### Mechanism A1 — centroid-only schema (MDL floor)

S_c = mu_c = mean(atoms in cluster c). Bind into substrate as `S_c = bundle(atoms)/||bundle(atoms)||`. Recall a query q against {S_1..S_K} by cosine.

- **Pros:** 1 atom per cluster; MDL-optimal under Gaussian-isotropic assumption; trivial to query.
- **Cons:** loses variance — outlier exemplars become indistinguishable from cluster-mean; can't discriminate two clusters with overlapping centroids but different shapes.
- **Fairness risk:** BY-CONSTRUCTION-SATURATION HIGH. If smoke uses well-separated Gaussian-isotropic clusters (the ultrametric cell's regime: family_noise=0.008, between-cluster cosine 0.076), centroid-only HITS 1.000 and so does any reasonable baseline → no discriminator headroom. Need a regime where clusters overlap (between-cluster cosine 0.3-0.5) so variance-blind centroid LOSES vs variance-aware schemes.

### Mechanism A2 — sufficient-statistics schema (centroid + variance + k exemplars)

S_c = bind(SCHEMA_ID_c, mu_c) + bind(VAR_ROLE, sigma_c) + sum_k bind(EXEMPLAR_k_ROLE, x_ck). k = log2(N_c) exemplars chosen by farthest-point sampling.

- **Pros:** preserves cluster shape; exemplars cover variance directions centroid misses; native substrate-bind composition; query can unbind via exemplar roles for fine-grained recall.
- **Cons:** k+2 atoms per cluster (vs 1); risk of exemplar-binding noise saturating bundle capacity if K_total > substrate capacity ceiling.
- **Fairness risk:** verify-the-referent — must measure schema-construction quality (centroid-shift + exemplar-coverage), NOT just final retrieval. Otherwise we test cluster-quality rediscovery, not schema construction. Discriminator: held-out cluster members should retrieve schema via centroid OR via exemplar-role unbind; pure-bundle schemes can't separate these paths.

### Mechanism A3 — information-bottleneck schema (compress to fixed-bit budget, max I(S;C))

Train a projection W_schema: R^D → R^d (d < D) that maximizes mutual information between schema vector S = W_schema·x and cluster label C. Substrate-native: W_schema is a learned bind-key bank; schema atom = bind(W_schema, sample_from_cluster).

- **Pros:** principled compression rate; ties to brain compression literature (Tishby IB).
- **Cons:** requires learned W_schema → adds training overhead + risk of overfitting to current cluster set (no generalization to new clusters without retraining).
- **Fairness risk:** SHARED-W BUG TRAP. If W_schema is fit on the same atoms used for retrieval test, baseline is unfairly handicapped. Need cross-split: fit W_schema on cluster-set-train, retrieval test on cluster-set-heldout drawn from same distribution.

---

## ANGLE B — biology / brain: how cortex actually builds schemas

### Mechanism B1 — Tse-Morris schema-engram (1-shot integration into existing scaffold)

After scaffold trained, a NEW exemplar binds to nearest existing schema via single-shot Hebbian update on schema-cell ensemble. Substrate-native: schema-cell = bundle of atoms previously assigned to cluster c; new x updates S_c via `S_c <- normalize(S_c + eta * x)` with eta small (1e-2).

- **Pros:** brain-aligned (Tse-Morris 2007 1-trial consolidation); cheap; preserves running mean.
- **Cons:** still centroid-flavored — no variance machinery; vulnerable to outlier drift if a misassigned x corrupts S_c.
- **Fairness risk:** BY-CONSTRUCTION-SATURATION — if cluster-assignment is given (oracle), update rule is trivially optimal. Discriminator must include arms where assignment is NOISY (P_correct_assignment in [0.7, 0.9]) so schema robustness to misassignment becomes the discriminating axis.

### Mechanism B2 — Posner-Keele prototype + variance band

Schema = explicit (prototype, variance_radius) pair. New x admitted to schema iff cosine(x, prototype) > threshold(variance_radius). On admission, prototype updates AND variance_radius updates (running EMA of within-cluster distance).

- **Pros:** brain-grounded (Posner-Keele 1968 + Bartlett 1932 prototype theory); substrate-native; variance band serves as a per-schema refuse-gate threshold.
- **Cons:** 2-atom schema per cluster; threshold tuning sensitivity.
- **Fairness risk:** verify-the-referent — discriminator must test BOTH false-accept rate (atoms from other clusters wrongly admitted) and false-reject rate (true cluster members rejected). Single-number recall metric hides the trade-off.

### Mechanism B3 — Tonegawa engram-cell schema (sparse-distributed ensemble)

Schema = k-WTA sparse code over a fixed schema-cell population. Each cluster activates k=20 of N=2000 schema cells (sparsity 1%). Construction: train sparse coding (e.g., k-means w/ sparsity penalty) so each cluster lights up a distinct k-subset.

- **Pros:** brain-grounded (Tonegawa engram cells); high capacity (C(N,k) distinct schemas); naturally orthogonal sparse codes give low interference.
- **Cons:** requires k-WTA training; cost scales with N_schema_cells.
- **Fairness risk:** SHARED-W BUG TRAP if schema-cell population is shared with episodic store. Must allocate separate W_schema_cells from W_episodic. Also: if k is tuned per regime, that's an undeclared free parameter — cell-author must pre-register k.

---

## TOP-2 picks (cross-angle, P-deflated, falsifiable)

### TOP-1 — Mechanism B2 (Posner-Keele prototype + variance band) — P_deflated = 0.48

**Why top:** brain-aligned + substrate-native + minimal new primitives (prototype = bundle; variance_radius = scalar; admission rule = existing refuse-gate). 2-atom schema cheap. Variance band directly addresses A1's variance-loss weakness.

**Falsifiable discriminator (concrete numbers):**
- Regime: overlap cluster pairs at between-cluster cosine 0.35 +/- 0.05 (NOT the 0.076 ultrametric-smoke regime — that saturates).
- Arms: ARM_CENTROID_ONLY (A1 floor), ARM_PROTOTYPE_VARIANCE (B2), ARM_RANDOM_BAND (control with fixed band irrespective of cluster), ARM_NO_SCHEMA (raw atom retrieval baseline).
- Metric: F1 = harmonic mean of (held-out recall) + (1 - cross-cluster false-accept).
- HARD_PASS: B2 F1 >= 0.75 AND CENTROID_ONLY F1 in [0.45, 0.65] AND RANDOM_BAND F1 in [0.30, 0.50] AND NO_SCHEMA F1 < B2 by >= 0.15.
- HARD_FAIL: B2 F1 < 0.60 OR B2 F1 - CENTROID_ONLY F1 < 0.08.

**Fairness pressure-tests:**
- Regime check: smoke at between-cluster cosine 0.35 (NOT 0.076) so CENTROID_ONLY can't saturate.
- Separate-W: each arm gets own W (no shared bind-keys).
- Verify-referent: report BOTH false-accept AND false-reject — single F1 hides trade-off.
- META_RULE_K: smoke must FIRE the discriminator — at smoke N, at least ONE arm pair must show >= 5% spread.

### TOP-2 — Mechanism B3 (Tonegawa sparse-ensemble schema) — P_deflated = 0.42

**Why second:** highest theoretical capacity (sparse codes scale); brain-grounded; provides natural orthogonality so interference between schemas is bounded a priori. Complementary mechanism class to B2 (distributed vs prototype) — if B2 wins, B3 falsifies; if both win, we have two mechanism legs.

**Falsifiable discriminator (concrete numbers):**
- Setup: N_schema_cells = 2000, k = 20 (1% sparsity), 8 clusters from ultrametric output.
- Arms: ARM_SPARSE_K20 (B3 nominal), ARM_DENSE_K2000 (k=N, equivalent to centroid), ARM_RANDOM_K20 (sparse but random assignment to schema-cells — no structure), ARM_PROTOTYPE_B2 (top-1 head-to-head).
- Metric: capacity@95%-recall = max number of distinct clusters whose schema atoms can coexist with mean recall >= 0.95.
- HARD_PASS: SPARSE_K20 capacity >= 2x DENSE_K2000 AND >= 3x RANDOM_K20.
- HARD_FAIL: SPARSE_K20 capacity <= DENSE_K2000 OR < 1.5x RANDOM_K20.

**Fairness pressure-tests:**
- Separate W_schema_cells from W_episodic (do NOT reuse cluster atom matrix).
- Pre-register k = 20 (not tuned post-hoc).
- Verify-referent: capacity must be measured at fixed recall threshold, NOT max recall (else trivially capacity = 1).
- META_RULE_K: smoke at N_clusters = 4 must show SPARSE > DENSE by >= 5% in capacity OR halt.

---

## Recommendation to prereg-author (cortex-closure agent a0bc3f2cc9f70b4be)

- If their v1 prereg picks **prototype + variance** → drill confirms TOP-1; suggest adding ARM_SPARSE_K20 as 5th arm for cheap second-mechanism evidence (~+10% cost).
- If their v1 prereg picks **sparse-ensemble** → drill confirms TOP-2; suggest adding ARM_PROTOTYPE_B2 for head-to-head.
- If their v1 prereg picks **centroid-only** (A1) → drill flags BY-CONSTRUCTION-SATURATION risk; insist on overlap-cluster regime (cosine 0.35) with at least ONE variance-aware arm.
- If their v1 prereg picks **information-bottleneck** (A3) → drill flags SHARED-W risk; insist on cross-split fit/test atoms.

**Universal fairness floor for any prereg-author choice:**
1. between-cluster cosine in [0.30, 0.45] regime (NOT the 0.076 ultrametric-smoke regime — saturates all arms).
2. Separate W per arm (no shared bind-keys / cluster matrix).
3. Discriminator measures schema-construction (false-accept + false-reject), NOT cluster-rediscovery.
4. Smoke FIRES discriminator: at least one arm pair shows >= 5% spread or HALT.
5. CARDINALITY_OK: pre-register N_clusters_expected; HARD_FAIL if observed < expected (catches silent-drop on sweep arms).

---

## Word count: ~990
