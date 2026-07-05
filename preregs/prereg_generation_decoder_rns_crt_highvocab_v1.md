# Pre-reg: RNS/CRT high-vocab generation envelope-push v1

- Cell: `experiments/exp_generation_decoder_rns_crt_highvocab_v1.py`
- Anchor: `generation_decoder_rns_crt_highvocab_v1`
- Metrics: `data/exp_generation_decoder_rns_crt_highvocab_v1/metrics.json`
- Extends: `exp_generation_decoder_gsbc_native_blocklocal_v1` (CHAIN_GRADE; single-block cliff
  0.856 @ V8192 D26 MEASURED@data/exp_generation_decoder_gsbc_native_blocklocal_v1/metrics.json:arms.blocklocal_gsbc@V8192D26.exact_ordered_mean)
- Date: 2026-07-05. Author: hdi_exp_dev. Prior-work check: NONE at cosine>0.30 (top substrate-KB
  hit `decoder` cosine=0.2959, WordNet lexical only). Genuinely novel mechanism (no prior RNS/CRT arc cell).

## Question
Does RNS/CRT sub-block decomposition (brain-grounded: entorhinal grid cells are modular/RNS,
CITED@Kymn/Fiete) extend the block-local generation decoder to HIGHER VOCABULARY past the 0.856 cliff?
Code token id t as residues (t mod m1, t mod m2, t mod m3) with pairwise-coprime moduli in r=3 disjoint
sub-blocks; effective vocab = prod(m_i) >= V; each sub-block resolves only an m_i-way residue alphabet.

## Calibration finding (drives the design)
The single-block cliff is a CORRELATION artifact, not an iid capacity limit. Disjoint blocks are
interference-free (one code per block), so IID single-block stays exact to V=millions (MEASURED
single_synth=1.000 through V65536). The v1 native-GSBC cliff is because CORRELATED concept codes project
to near-identical sparse block codes -> cleanup ties. This cell reproduces the cliff with a self-contained
correlated pipeline (no 10000-concept pool dependency, so V pushes past the pool): MEASURED single_corr
0.90/0.73/0.50/0.167 as V 8192->16384->32768->65536 @ D26 (scratchpad calibration). RNS residue labels
(t mod m_i) are non-semantic -> residue codebooks are naturally iid/decorrelated (the grid-cell property),
which is exactly what sidesteps the correlation cliff.

## Arms (PAIRED on the same token-id props per (V,D,seed))
- `single_corr`  : correlated V-way codebook, single-block v1 decode -> CLIFFS. [DISCRIMINATOR BASELINE]
- `single_synth` : iid V-way codebook, single-block v1 decode -> iid CEILING (cliff=corr artifact). [CEILING]
- `rns_crt`      : iid residue codebooks (r=3 coprime moduli), RNS/CRT decode -> HOLDS. [MECHANISM/DELIVERABLE]
- `rns_scram`    : rns residues decoded then DERANGED before CRT -> COLLAPSES. [DISCRIMINATOR CONTROL]

Load-bearing PAIRED comparison: `rns_crt` vs `single_corr` at V beyond the cliff (V=65536 D26).

## Grid / cardinality
FULL grid (V,D): (8192,26)anchor (16384,26) (32768,26) (49152,26) (65536,26)envelope (65536,16)boundary
(65536,32)boundary. Arms=4, seeds=(7,13,19). `EXPECTED_N_UNITS = 7 x 4 x 3 = 84`. `cardinality_ok` gate:
verdict HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if len(per_unit) < 84.
SMOKE grid: (8192,26),(65536,26), trials=12, 3 seeds = 24 units (keeps N/D/V at gate points).

## Moduli (pairwise-coprime, product >= V; asserted at runtime + CRT self-test)
8192:(20,21,23)=9660; 12288:(22,23,25)=12650; 16384:(25,27,28)=18900; 32768:(31,33,35)=35805;
49152:(36,37,41)=54612; 65536:(40,41,43)=70520.

## Bands (envelope-fail-bands; gates on rns_crt vs single_corr at anchor V8192D26 + envelope V65536D26)
- HARD_PASS: rns_crt exact-ordered >= 0.85 at anchor AND envelope, cross-seed cv < 0.10, AND
  (rns_crt - single_corr) at envelope >= 0.30. MEASURED (smoke, full envelope regime): rns=1.000 cv=0.000
  gap=0.889. Strictly-above-floor (META_RULE_L): floor 0.85, band from HF=0.50 width 0.35, +5%=0.5175;
  0.85 well above; measured 1.000 >> 0.85.
- HARD_FAIL: rns_crt < 0.50 at envelope OR (rns_crt - single_corr) <= 0 (ties/loses single-block --
  per-residue errors cancel the capacity gain).
- MIDDLE_BAND: rns_crt in [0.50,0.85) OR gap in (0,0.30) OR cv >= 0.10.

## Discriminator-fires gates (ALL modes incl smoke; META_RULE_K)
1. iid single-block ceiling recovers: single_synth >= 0.90 at anchor+envelope (MEASURED 1.000).
2. single_corr CLIFFS at envelope: single_corr < 0.70 (MEASURED 0.111). If not, regime too easy -> STOP.
3. scrambled control collapses: rns_scram <= 0.10 at anchor+envelope (MEASURED 0.000) -> CRT is load-bearing.
Smoke ran ALL THREE at the full envelope regime (N=8192 D26 V65536); all fired.

## SCHEMA-VET mandatory fields
- `cardinality_ok`: true (EXPECTED_N_UNITS=84 gate wired).
- `final_metrics_atomicity`: tmp_replace (metrics.json.tmp -> os.replace).
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException; grep-gate clean).
- `crlb_n_a`: "disjoint-block recovery is interference-free (one code per block; no superposition noise
  within a block). RNS reconstruction is exact iff all residues correct; a residue error requires a
  per-sub-block codebook COLLISION, not a noise-floor event. No argmax-noise floor gates the deliverable."
  (Empirical: k_sb=2 collision fragility MEASURED cv=0.243; K_MIN_ACTIVE=4 floor -> collision-free, cv=0.000.)
- `baseline_in_band` (META_RULE_AG): single_corr in (0.05,0.95) across the sweep (0.90->0.167). single_synth
  CEILING-exempt (intentionally ~1.0); rns_scram CONTROL-exempt (intentionally ~0.0).
- `arms_differ_verified` (META_RULE_AF): corr vs synth codebooks + single vs residue codebooks hash-distinct;
  rns_scram recovered-index array differs from rns_crt (scramble alters output). Perfect-recovery token
  arrays NOT compared (rns_crt/single_synth legitimately emit identical truth tokens).
- `discriminator_survives_scale`: (A) smoke runs the discriminator AT full N/D/V gate points (reduces
  trials/grid-length only). MEASURED envelope gap=0.889 in smoke.
- `HP_SCOPE`: {rns_crt: [HP_rns_floor, HP_cv, rns_gap], single_corr: [single_cliff_thresh, baseline_in_band],
  single_synth: [synth_ceiling_floor], rns_scram: [scram_collapse]}. Chain-grade rns floor applies ONLY to
  rns_crt; baseline/ceiling/control arms carry their own gates, not the mechanism floor.
- `calibration_check`: adaptive_with_discriminator_gate. Correlation (N_CLUSTERS=128, FRAC_SHARED=0.85)
  chosen to reproduce the v1 native-GSBC single-block cliff (~0.90 @ V8192 D26 near v1 0.856); NOT tuned
  for RNS (rns passes by construction). Discriminator still fires (scram collapse + gap + ceiling), logged.

## §15 composition/sweep gates
- `sweep_alignment_verdict`: ALIGNED. Swept param V. single_corr experiences effective_V=V (full V-way
  cleanup); rns experiences per-sub-block alphabet m_i. Both aligned with the mechanism claim.
- `discriminating_fraction`: single_corr spans the FULL cliff transition across the sweep (0.90/0.73/0.50/
  0.167 predicted at 8192/16384/32768/65536; +12288~0.82, 49152~0.30). This is the OPPOSITE of
  by-construction saturation (the sweep resolves the transition); the below-band envelope point (0.167) is
  the intended "single-block fell off the cliff" target, not a saturation artifact.
- `composition_edges`: single edge concept-id -> {residues via mod} -> sub-block codes -> CRT.
  SHAPE_MATCH (integer residues < modulus; CRT bijection [0,M)<->residue tuples; V<=M).
- `positive_control_arms`: single_synth reproduces the iid-block ceiling AT the test regime (MEASURED 1.000);
  single_corr reproduces the v1 correlation cliff AT the test regime (MEASURED ~0.90 anchor).
- `functional_requirements`: (1) large ordered vocabulary readout -> RNS residue decomposition; (2) exact
  reconstruction -> CRT (coprime moduli, self-tested); (3) order -> disjoint block-per-slot binding (v1);
  (4) discriminate mechanism from artifact -> scram control + iid ceiling.

## Formula self-test (--self-test)
CRT reconstruction: CRT(t mod m_i) == t for all t in [0,min(M,4096)) + 256 random spot-checks to M, for
every moduli set. Coprimality (gcd) check. MEASURED crt_ok=True. Plus wiring: rns_crt>=0.90, single_synth
>=0.90, rns_scram<=0.10.

## Distinctive RNS win (honest scope)
rns_crt FIDELITY ~ single_synth iid ceiling (both ~1.0); RNS does NOT beat an iid single codebook on
fidelity. It (1) matches the iid ceiling where the REALISTIC correlated baseline cliffs, and (2) reaches
effective vocab prod(m_i) with only sum(m_i) codes -- MEASURED 528x codebook compression at V65536
(70520 effective vocab via 124 residue codes). This capacity-efficiency + correlation-immunity is the
grid-cell property (Kymn/Fiete).

## Compute architecture
- Class (b) sequential-CPU with justification: reuses v1's proven CPU block-local pipeline (v1 FULL=26s CPU);
  task mandates CPU probe (no LLM/GPU, matches v1); cleanup is BLAS-vectorized (cb @ seg); only Python loop
  is over trials/slots (cheap). Largest cost = single_corr/single_synth V65536 cleanup, ~minutes CPU.
- Storage strategy: block_local_disjoint (sharded-equivalent: each slot/residue occupies a disjoint block;
  no cross-item bundling WITHIN a block). No superposition interference within a block.
- `progress_logging`: print_flush_true (line_buffered stdout + per-unit print + per-unit _heartbeat.jsonl).
- `cell_chunked`: false (sweep cell, single-seed-loop with per-unit heartbeat + start-marker + crash-diag).

## Dispatch
- SMOKE: LOCAL, run directly (--smoke) as the gate. MEASURED HARD_PASS (SMOKE_MACHINERY_OK), elapsed 20.4s.
- FULL: STAGE for remote (remote_cpu_queue or overnight_queue via orchestrator; push needed, harness-denied
  to exp_dev). Recommended `--timeout 1800` (extrapolated full ~3-4 min from smoke 20.4s x 8.3x V*D*trials
  ratio; 1800s = generous margin for slower remote CPU). run_mode must land `full` (verify §16).
