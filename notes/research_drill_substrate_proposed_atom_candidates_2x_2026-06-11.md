# research drill: substrate-proposed atom-candidate generation mechanism (2x DEEP)

date: 2026-06-11
topic: Tier 3 substrate-on-substrate self-extension -- atom-candidate generation + validation pipeline
sub-agents dispatched: 6 parallel WebSearch lit-scans (Sonnet) -- clustering validation, AM/Eurisko, conceptual blending, VAE generative, spectral-gap criteria, decoy-injection QC
calibration: lit-scan penalty applied (P deflated 0.15-0.25; novel-synthesis cap 0.50); hard-fail thresholds pre-registered

## HEADLINE

Substrate-native atom-candidate generation is a **3-stage filter pipeline** -- (1) GAP-DETECT via density-valley + spectral-gap on existing-atom occupancy, (2) CANDIDATE-PROPOSE via cluster-center + algebraic-blend of nearest existing atoms, (3) VALIDATE via held-out cross-domain consistency + decoy-injection QC + structural-relation count. The pipeline avoids the AM/Eurisko collapse mode (string-similarity laundering + unbounded self-reference) by requiring **every accepted atom to have >=3 structural relations to pre-existing accepted atoms AND survive a known-decoy contamination test at fixed false-accept rate**. P_deflated (single-month gate achievable substrate-only with this pipeline) = **0.55**. Cheap decisive test runs in <2 hr CPU.

## Cheap decisive test (one-shot, <2 hr CPU)

Build a small reference KB of N=200 accepted atoms with known pairwise structural relations. Do all 4 of the following back-to-back on the same KB:

1. **Hold out 20 atoms** (10% of accepted set) chosen to span tail of occupancy density. Run the 3-stage pipeline on the remaining 180. The pipeline must RE-PROPOSE >=14/20 held-out atoms (>=70% recall) within top-K=30 candidates -- otherwise the gap-detect stage is missing real gaps.
2. **Inject 20 synthetic decoy atoms** with random embeddings but no structural-relation support. The pipeline must REJECT >=18/20 decoys (<=10% false-accept). This is the AM/Eurisko anti-laundering check.
3. **Cluster-quality gate**: compute density-based silhouette (Menardi 2010 style for the proposed-atom occupancy region) AND spectral eigengap on the affinity matrix of (existing-atoms + candidate). HARD PASS requires silhouette_density >= 0.30 AND eigengap_ratio (lambda_{k+1}/lambda_k) >= 1.5 for the candidate cluster.
4. **Cross-domain consistency probe**: project candidate into 3 disjoint sub-substrates (different shards / different cap_map rows) and require >=2 to assign the candidate non-trivial relation weight (>= 1.5x random baseline). Bounds the polysemy / image-schema-0.342 failure mode from 2026-06-10 audit.

Total cost: ~30 min on N=200 if vectorized.

## Falsifiable predictions

### HARD-PASS thresholds (substrate-only Tier 3 gate achievable in 1 month with this pipeline)

- candidate_recall_on_holdout >= 0.70 (re-proposal of removed atoms in top-K=30)
- decoy_reject_rate >= 0.90 at fixed false-accept budget 0.10
- accepted_atom_structural_relations_median >= 3 (per Tier 3 gate spec)
- accepted_atoms_per_month >= 5 (gate spec)
- new_relations_per_month >= 3 (gate spec)
- silhouette_density (Menardi-style) >= 0.30 for accepted clusters
- spectral eigengap_ratio >= 1.5 at chosen K
- cross-domain consistency: >=2/3 disjoint shards assign nontrivial weight

### HARD-FAIL thresholds (pipeline insufficient; need LLM-assisted or human-in-loop)

- candidate_recall_on_holdout < 0.50 -- gap detection is missing real structure; bigger gap-detect overhaul required
- decoy_reject_rate < 0.70 -- AM/Eurisko laundering risk dominant; validation stage too weak
- accepted_atoms with 0-1 structural relations exceed 20% of accepted set -- unbounded self-reference / hallucination
- silhouette_density < 0.15 OR eigengap_ratio < 1.1 -- candidates do not occupy structurally distinct regions; storing noise as atoms
- cross-domain consistency: 0/3 shards agree on >=50% of accepted candidates -- polysemy collapse

### Middle band (PARTIAL -- Tier 3 gate achievable hybrid; substrate proposes, lightweight LLM-judge accepts)

recall in [0.50, 0.70] OR decoy_reject in [0.70, 0.90] OR cross-domain in [1/3, 2/3 shards] -- substrate-only proposes well but final accept needs external arbiter.

## The 3-stage pipeline (concrete, substrate-native)

### Stage 1 -- GAP-DETECT (where to propose)

Three complementary signals, ANY of which fires a "candidate gap":

- **Density valley**: kernel-density-estimate over current-atom occupancy in the substrate codebook space. A valley between two density modes whose mode-separation exceeds bandwidth h by >=2x is a gap. Inherits from Menardi 2010 density-based silhouette and DBSCAN / HDBSCAN reachability cores.
- **Spectral eigengap**: build affinity matrix W on currently-accepted atoms. Compute Laplacian eigenvalues. A "missing cluster" shows up as a near-zero region in lambda spectrum that does not correspond to an existing accepted atom. Per Luxburg tutorial: the eigengap heuristic is least reliable on noisy data, so we require both density-valley AND spectral-gap to agree before proposing.
- **Algebraic-gap (substrate-native)**: for every pair (a_i, a_j) of accepted atoms, compute the algebraic blend a_i (op) a_j (where op is the substrate-native binding operator) and check whether the blend lives in an under-occupied region (density < 0.5x median). This is the Fauconnier-Turner generic-space + blend-operation idea cast onto substrate algebra. Goguen 2006 modeled this as a categorical colimit of input spaces; we use the substrate's binding algebra directly (no category-theoretic machinery -- the substrate algebra IS the input-space colimit).

ANY-of-3 firing -> region is a candidate-gap; advance to Stage 2.

### Stage 2 -- CANDIDATE-PROPOSE (what to put there)

Three proposal mechanisms tried in parallel; each emits 1 candidate per gap:

- **Cluster-center**: meanshift-style centroid of the points falling in the gap's neighborhood (per scikit-learn MeanShift -- candidates are centroids filtered to remove near-duplicates).
- **Algebraic-blend**: the binding result a_i (op) a_j that triggered the algebraic-gap signal becomes the candidate vector directly. This is the conceptual-blending channel.
- **Adjacent-interpolation**: spherical linear interpolation between the two nearest accepted atoms in the gap region.

All 3 candidates are kept and ALL advance to Stage 3. The accept-or-reject decision is per-candidate, not per-gap.

### Stage 3 -- VALIDATE (whether to keep)

Each candidate must pass ALL of:

- **Structural-relation count >= 3**: candidate must have >=3 detectable structural relations (binding-partner, role-filler, cluster-membership, antonym-edge, etc.) to pre-existing accepted atoms. AM laundered string-similarity for "interesting"; the structural-relation floor is the empirical countermeasure.
- **Decoy-injection QC**: at acceptance time, the pipeline simultaneously evaluates K decoys (random-vector candidates with no structural support). The candidate's structural-relation count must exceed the 90th percentile of the decoy distribution. This calibrates the accept threshold per-cycle and prevents drift.
- **Cluster-quality**: silhouette_density >= 0.30 AND eigengap_ratio >= 1.5 measured on (accepted-atoms + this candidate).
- **Cross-domain consistency**: candidate is projected into 3 disjoint sub-substrates; >=2 must assign non-trivial relation weight (>= 1.5x random baseline).
- **No unbounded self-reference**: the candidate's structural relations must not be dominated (>50%) by other proposed-this-cycle candidates. Eurisko's meta-rule collapse is the canonical failure here; the floor on "relations to pre-existing accepted atoms" (not "relations to other new candidates") enforces grounding.

Candidates passing all 5 -> accept as new atom; log structural relations to existing graph.

## False-positive avoidance (5 mechanisms layered)

1. **Pre-registered acceptance criteria** (per [[feedback-lit-scan-calibration-penalty]] convention) -- thresholds in HARD-PASS/HARD-FAIL above are committed before pipeline runs.
2. **Cross-validation hold-out** -- 10% of accepted atoms removed; pipeline must re-propose them at >=70% recall. Catches gap-detect overfitting to current atom set.
3. **Adversarial decoy probes** -- random-embedding decoys at 10% rate; calibrated rejection threshold per cycle.
4. **Counterfactual injection** -- 5% of cycles run with a known-fake atom seeded into the gap region; pipeline must NOT accept it. This is a stronger QC than random decoys because the fake atom is constructed to mimic legitimate algebraic-blend output but has hand-crafted incorrect structural relations. Failure to reject -> validation stage compromised.
5. **Quarantine bucket** -- accepted atoms that have <5 structural relations after 2 months get auto-quarantined (not deleted; flagged for re-validation). Mirrors Tier-1 frozen / per-tier importance defaults from substrate v3.2 wrapper.

## Cluster-quality criteria (operational defaults)

- silhouette (standard): >= 0.30 for accepted; in [0.15, 0.30] requires manual review
- density-based silhouette (Menardi 2010): >= 0.30 for density-based clusters where standard silhouette mis-scores elongated shapes
- Davies-Bouldin: <= 1.5 (lower is better; bounds within/between scatter ratio)
- Calinski-Harabasz: track but do not gate (relative measure across K values)
- spectral eigengap: lambda_{k+1}/lambda_k >= 1.5
- gap-statistic vs uniform-null: candidate cluster's within-cluster dispersion must beat uniform-reference by >= 1 SD

Use density-based silhouette as primary when clusters are non-spherical (typical in substrate codebook space after binding ops). Standard silhouette is misleading on elongated/crescent shapes per Menardi and the scikit-learn cluster validation literature.

## Substrate-native validation primitives the substrate already provides

Per substrate v3.2 wrapper findings (2026-06-11 memory): substrate has
- per-shard write-lock -> trivially supports decoy injection (decoys go in a sandbox shard until accepted)
- Tier-1 frozen + per-tier importance defaults -> quarantine bucket = Tier-4-equivalent with importance 0.0
- substrate-classical NLP outperforming phasor-only (POS 0.906, slot-filling 0.871) -> count-based statistical signals are substrate-native; structural-relation count IS a count-based signal
- FHRR Reed-Solomon parity (~30 lines torch) -> error-correction on accepted-atom representation; spurious candidates fail the parity check

So the validation stage is NOT a bolt-on -- it's substrate algebra used compositionally.

## Cross-thread synthesis

This pipeline reconciles three prior findings:

- **drill_pattern_temporal_contextual_vs_fixed_architecture_2026-06-11**: gap-detect via density-valley + spectral-gap is TEMPORAL (rolling, recomputed each cycle); algebraic-gap is CONTEXTUAL (binding-operator-driven). Both classes that drill-validated; fixed-architecture gap-detect (e.g. fixed K-means K) would be the failure class.
- **substrate_representation_artifacts_rescued_2026-06-10** (concept-context binding + ZCA prewhiten): cross-domain consistency probe IS the polysemy guard from that rescue, generalized. Without it, image-schema-style 0.342 collapse re-occurs at atom-discovery layer.
- **historical AI self-indexing 2x DEEP** (2026-06-11 earlier): 6 success patterns + 4 failure modes from CYC/Eurisko/AM/Soar/ACT-R/Hofstadter map directly:
  - SUCCESS "partition before scale" -> per-shard decoy injection
  - SUCCESS "graded fluid retrieval" -> density-valley + algebraic-blend (not rigid logic)
  - SUCCESS "role-tagged retrieval" -> structural-relation count
  - SUCCESS "auto-extract not hand-curate" -> pipeline IS auto
  - FAILURE "string-similarity laundering" (AM) -> structural-relation floor blocks it
  - FAILURE "self-mod meta-rules collapse" (Eurisko) -> the floor requires relations to PRE-existing accepted atoms, not to other new candidates
  - FAILURE "unbounded self-reference" -> quarantine bucket + 2-month re-validation
  - FAILURE "hand-coded scaling failure" (CYC) -> 0 hand-coding in this pipeline

## Substrate-product implications

- **Tier 3 gate (5+ atoms/month, 3+ relations/month) achievable substrate-only with P_deflated = 0.55** if the pipeline as specified runs and passes the cheap test. If cheap test gives PARTIAL band, hybrid (substrate-proposes, lightweight LLM-judge accepts) is the fallback at P_deflated = 0.70.
- Pipeline is **<300 lines of code** estimated: 3 stages, each ~50-100 LOC, plus shared infrastructure (KDE + spectral + decoy generation).
- **Demo-grade visualization**: "watch the substrate discover an atom" is a marketable demo -- the gap-detect + propose + validate sequence has a natural visual narrative (heatmap valley -> centroid marker -> structural-relation graph -> accept/reject light).
- **No new substrate primitives required**: pipeline rides on existing algebra (binding op, KDE on codebook, structural-relation count). Adds ONE new persistent state: the decoy distribution from previous cycles (used for calibration).
- **Risk: scope creep from Tier-3 to Tier-4 (self-extending the validation rules themselves) -- DEFER. AM/Eurisko both collapsed when they tried to self-modify the meta-rules.** Hard rule: this pipeline does NOT propose changes to its own validation thresholds. That is a separate (Tier 5+) gate.

## Citations (verified count: 17)

1. Menardi, G. (2010). "Density-based Silhouette diagnostics for clustering methods." Statistics and Computing. (density-silhouette primary)
2. von Luxburg, U. (2007). "A Tutorial on Spectral Clustering." arXiv:0711.0189. (eigengap heuristic, limits)
3. scikit-learn documentation, "2.3. Clustering." (MeanShift cluster-center filtering)
4. CAS -- Condensed and Accelerated Silhouette, arXiv:2507.08311 (optimal K selection)
5. Lenat, D. B. (1983). "EURISKO: A Program That Learns New Heuristics and Domain Concepts." (Eurisko mechanism + early failures)
6. Lenat & Brown, "Why AM and EURISKO Appear to Work," AI 1984. (string-similarity laundering diagnosis)
7. Fauconnier & Turner (1998). "Conceptual Integration Networks." (blending source theory)
8. Goguen, J. (2006). "Mathematical Models of Cognitive Space and Time." (categorical colimit blending)
9. Pereira & Cardoso (2003). "Optimality Principles for Conceptual Blending: A First Computational Approach." (implementation precedent)
10. Eppe et al. ScienceDirect, "A uniform model of computational conceptual blending."
11. Goal-Driven Conceptual Blending (Li & Zook) -- creativity-oriented computational blending.
12. Adversarial Symmetric VAE (arXiv:1711.04915). (latent-space generation + adversarial training)
13. Concept-based adversarial generation method with steerable semantics (US patent 11763135).
14. Adversarial Attacks on VAEs (arXiv:1806.04646) -- latent-space perturbation robustness.
15. Davies-Bouldin Evaluation, MATLAB / multiple practitioner refs.
16. Gap statistic + Davies-Bouldin + Calinski-Harabasz comparative practical (Das, Medium).
17. From Data Fusion to Knowledge Fusion (arXiv:1503.00302) -- gold-standard / decoy approaches for KB quality.

## Open follow-ups

- Implement Stage 1-2 only as a first 1-day cell; observe gap candidates qualitatively before wiring Stage 3.
- Calibrate decoy distribution per substrate (probably varies by codebook fan-out).
- Investigate whether the algebraic-blend mechanism (Fauconnier-Turner via substrate binding op) generates DIFFERENT candidates than cluster-center -- if they overlap >80%, drop the cluster-center channel as redundant.
- TIER-5+ self-extension of validation thresholds is explicitly DEFERRED -- AM/Eurisko historical lesson is dispositive.

next-drill candidate: free-probability F4 (Voiculescu free cumulants kappa_n) -- adjacency to atom-isolation margins; substrate-novel observability beyond mean+variance for accepted-atom QC.
