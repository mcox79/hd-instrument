# exp_dev hand-off -- research: Clustered codebook spectral characterization, Cell C spike-bulk decomposition

Filed-by: research (Opus, 2026-06-13)
Trigger: F4 Cell B NEGATIVE finding (kappa_2 = 1.93 vs alpha = 0.236; flat dev-SNR ~1.4 at orders 3-8); 2x deep drill complete.
Source research note: d:/AI/hd-instrument/notes/research_drill_clustered_codebook_spectral_characterization_8d_pillar_revision_for_clustered_case_F4_Cell_B_negative_2x_2026-06-13.md
Pause state: orchestrator_paused.flag NOT present (no pause; exp_dev queue refill permitted).

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHOR CANDIDATES and POINTERS; exp_dev owns the experiment design and pre-registration values within the envelope below.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY): Cell C -- spike-bulk decomposition on real substrate codebook

- **Anchor pointer**: research note section (b) Cheap decisive test + section (e) "Specific cell design"
- **Substrate-product reading**: spike count k = number of recovered partitions = new 9th observability dimension; clustered codebook STRENGTHENS substrate-LLM categorical gap (per research note section (e))
- **Tier hint**: Tier-1 (free-probability fruit-bearing under-drilled; advisor score 5.5; current drill brings free-prob count to 2)
- **Why-now**: F4 Cell B left the 8d pillar in a NEGATIVE state. Cell C is the cheap (~90 min CPU) decisive test that resolves whether the pillar holds under multi-cut MP + spike revision OR requires non-Wishart bulk model. Until resolved, several downstream cap_map rows (L4 GNN SHARES_MATH compression, L5 SDM, 8d-pillar-positioning artifact) inherit the uncertainty.
- **Envelope (pre-register within)**:
  - HARD-PASS: 2 <= k <= 10 outliers; deflated kappa_2 in [0.21, 0.31]; deflated kappa_3/4 in [-0.3, 0.3]; spike-strength vs partition-size Spearman > 0.5; |k - true partition count| <= 2
  - HARD-FAIL: k = 0 OR k > 30 OR deflated kappa_2 > 1.0 OR spike-partition Spearman < 0.1
  - MIDDLE-BAND: k in [2, 10] AND deflated kappa_2 in [0.5, 1.0] (Wachter component candidate)
- **Sample size**: M=242 (full codebook; no subsampling)
- **Smoke gate**: synthetic clustered codebook with k=5 known clusters, d=1024, M=200; PASS smoke before real run

### Anchor 2 (SECONDARY): Cell D -- interior-edge universality (Pearcey / cusp)

- **Anchor pointer**: research note section (d) IMRN 2024 multi-cut measure result + section (e) dim 5 revision
- **Substrate-product reading**: if Cell C HP, then interior gaps between spikes follow CUSP universality, not Tracy-Widom; this is a substrate-novel claim adjacent to Tracy-Widom (F2) that distinguishes us from generic MP / Hopfield literature
- **Tier hint**: Tier-1b (RMT-beyond-free-prob; adjacent to fruit-bearing F4)
- **Why-now**: only run AFTER Cell C HARD-PASS; conditional anchor
- **Cost**: ~1 day theory derivation + ~1 hr CPU

### Anchor 3 (PROBE): post-ingest Cell C re-run

- **Anchor pointer**: research note section (e) "Implications for ingest"
- **Substrate-product reading**: Cell C becomes a STANDING observability test of ingest health; predict post-ingest k' > k spikes (more partitions); refutation = HF-2 (k > 30) = ingest destroying partition structure
- **Tier hint**: standing test, run after Phase-6 ingest batches
- **Why-now**: defer until Phase-6 ingest in flight

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_clustered_codebook_spectral_characterization_8d_pillar_revision_for_clustered_case_F4_Cell_B_negative_2x_2026-06-13.md
- Prior F4 Cell B output: search exp_dev logs for "F4 Cell B" / "kappa_2 = 1.93" results 2026-06-12 or 2026-06-13
- Prior substrate-extracted rule (no-cliff clustered-codebook): MEMORY index entry `substrate_composition_decomposition_no_cliff_ceiling_is_clustered_codebook_2026-06-12.md`
- 8d pillar source: MEMORY entry `substrate_mathematical_foundation_8_dimensional_spectral_observability_pillar_2026-06-12.md`
- Codebook source file: hdlab algebra_index codebook (substrate-internal; exp_dev knows path)
- Atom.partition ground truth field: queryable via tools/substrate_query.py (per Gap 3 CLI)

---

## Contract

- exp_dev owns: experiment design within the envelope above; choice of numerical implementation (numpy vs torch); smoke-gate pass; pre-registration values within envelope; ship via queue_add.sh (CPU queue); post-ship REMOTE VERIFY; status_log update.
- research owns: the literature framework + the envelope thresholds + the 8d pillar revision narrative. NOT the experiment code.
- verdict_handler owns: cap_map update + Memory write upon Cell C verdict.

## Autonomy declaration

exp_dev is autonomous within this envelope. No further check-in needed from research between hand-off and Cell C verdict. If exp_dev encounters a structural issue (e.g. codebook file format unexpected, partition ground truth missing), file a check-in routing note; otherwise proceed.

End of hand-off.
