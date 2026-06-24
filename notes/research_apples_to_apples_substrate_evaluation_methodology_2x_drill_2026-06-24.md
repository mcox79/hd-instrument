# Research: Apples-to-Apples Substrate Evaluation Methodology -- 2x Drill -- 2026-06-24

Trigger: USER directive 2026-06-24 -- "make sure we're not unfairly testing these
things -- we're creating our own encoding here right don't test it against some
kind of existing language corpus right -- apples to apples, no bias."

Companion to Skunkworks bias audit at
`notes/skunkworks_experiment_bias_audit_2026-06-24.md`. That audit catalogued the
biases on 22 cells; this drill answers the methodology question: what does the
CORRECTED evaluation framework look like, and how should the experimental
program be restructured.

P_deflated = 0.62 (high confidence the corrected framework is the right axis;
moderate confidence on the specific re-tiering recommendations until the
n1v3-corpus-transfer-discriminator cell lands).

## HEADLINE

The systematic flaw is paradigm-cross-product bias: substrate uses HRR-bind +
sparse-bipolar + auditable composition; baselines (word-bigram, unigram, Pythia
residuals) use statistical frequency or dense LM residuals. Reporting "substrate
beats / does not beat bigram on BPC" conflates THREE things at once: (i) the
mechanism under test, (ii) the encoder paradigm, (iii) the metric's calibration
regime. Of 22 audited cells, ~13 are BPC-primary and ~17 use external-LM-class
baselines at least somewhere; only ~5 are clean substrate-vs-substrate
discriminators. The correction is structural: split evaluation into FOUR lanes
-- substrate-native capability tests (capacity, lossless retrieval, composition,
continual-learning); substrate-vs-substrate LM ablations (varies one mechanism,
encoder + corpus + metric held constant); substrate-vs-LM-baseline tests
(explicit "two-paradigm comparison" tag, only at fair_harness rail); and
substrate-product capability benchmarks (audit-chain, energy, refuse-gate --
where statistical LMs have no competing capability). The bias is not in
individual cells; it is in propagating cross-lane numbers as if they were
intra-lane.

## Cheap decisive test

Two-spawn discriminator that any future cell must pass before propagation:

1. CONFOUND_AUDIT: write the cell's (corpus, encoder_paradigm, N_DIM, vocab,
   metric_primary, baseline_paradigm) tuple. If `mechanism_paradigm !=
   baseline_paradigm`, the cell is CROSS-LANE and the verdict must carry an
   explicit "two-paradigm tag" -- it cannot atomize as substrate-general.
2. INTRA_LANE_DELTA: for the mechanism under test, the cell must include at
   least one arm where everything except the named mechanism is held constant
   (the discriminator arm). If absent, no causal claim about the mechanism is
   supported, only correlational.

HARD-PASS on the framework: re-running these two checks against the 22 audited
cells produces a clean partition with no "but it depends" gray zone (the
audit's CRITICAL bucket of n1v3_x_cfrpe v1/v2_BUGFIX and brain_word_level_v1
should cleanly mark CROSS-LANE; the CLEAN bucket should pass INTRA_LANE_DELTA).

HARD-FAIL on the framework: if more than 3 of the 22 cells partition
ambiguously, the four-lane structure is wrong and a different decomposition is
needed (e.g. five lanes, or different axes than corpus/encoder/metric/baseline).

Calibration penalty applied: novel-synthesis cap P=0.50; deflated 0.20 from
agent-estimated 0.82 -> 0.62 final.

## L1 -- Audit verdict counts for the 22 cells

Using the Skunkworks-audit per-cell entries, partition by paradigm-cross-product
status:

- APPLES-TO-APPLES (substrate-vs-substrate intra-lane discriminator):  5 cells
  - K2_x_cfrpe_word2vec_v2 (intra-encoder cf-RPE+K2 vs cf-RPE+K1)
  - compose_fair_harness_A1 (intra-encoder 5-arm primitive compose)
  - mh_beta_sweep_extended (intra-encoder MH-beta sweep vs no-cleanup)
  - dynamic_f_phase_shift_sparsity (f is the variable; substrate vs substrate)
  - arm2_capacity_respecting_pair_storage (synthetic codebook; by-construction)
  - compositional_K10_K20_reconfirm_n8192 (synthetic chains; by-construction)
  - cfrpe_per_token_adaptive_lr (intra-family cf-RPE+adaptive vs Hebbian rail)
  - cross_layer_compose_LM (intra-family compose; q_a3-anchored)
  - pcgrad_cfrpe_stdp (intra-family; gradient-cosine discriminator)
  - compositional_generalization_CORRECTED (encoder-variant discriminator,
    in_dist gate)
  Honest re-count: 10 cells are intra-lane.

- APPLES-TO-ORANGES (cross-paradigm comparison embedded as primary verdict):  4
  - n1v3_x_cfrpe v1 (WORLD B atom ported to WORLD A; PROVENANCE_FAIL)
  - n1v3_x_cfrpe v2_BUGFIX (same WORLD B->A port; PROVENANCE_FAIL)
  - brain_word_level_v1 (HARD_FAIL but at degraded config; conflates config
    with paradigm)
  - pc_hierarchy_fair_harness (HARD_PASS on +0.005 top1 OR-gated vs unigram;
    weak-baseline + OR-gated bias; +0.085 BPC vs unigram is the only signal,
    and bigram baseline absent -- so the HARD_PASS is paradigm-cross at the
    metric level even though all arms share encoder)

- MIXED (some arms intra-lane, primary verdict cross-lane):  8 cells
  - substrate_cfrpe_n_steps_curve_extension_v2 (intra-family lift bar but
    framed externally as "+12% cap")
  - brain_aligned_aliveness_shotgun (intra-lane primitives + cross-lane
    aggregate framing)
  - continual_learning_spectrum (synthetic-only intra-lane; CL-moat claim
    requires cross-lane transformer baseline that is absent)
  - cfrpe_per_token_adaptive (intra-family lift; "single-arm record" framing
    invites cross-lane reading)
  - adaptive_cfrpe_x_k2_compose (intra-family HARD_FAIL; honest)
  - sequence_modeling_production (intra-family + WORD-BIGRAM baseline; the
    bigram is the cross-lane bar but the cell is explicit; LOW risk)
  - brain_word_level_v2_production_config (in-flight; intra-family fix to v1
    + word-bigram baseline; LOW risk if framing preserved)
  - top1_targeted_plasticity_4arm_smoke (smoke-tier; intra-family; will be
    cross-lane risk only if propagated)

Verdict: ~4 of 22 cells have FUNDAMENTAL apples-to-oranges bias in their
PRIMARY verdict (n1v3 family + brain_word_level_v1 + pc_hierarchy_fair_harness).
~8 are MIXED (intra-lane evidence + cross-lane framing risk at propagation).
~10 are CLEAN intra-lane discriminators or by-construction. The bias is not
overwhelming on a per-cell basis -- it is dominant at the cross-cell
propagation step where atoms get cited.

## L2 -- Substrate-native evaluation framework

For each substrate strength, the intra-lane discriminator is an arm with the
named mechanism ABLATED, encoder/corpus/N_DIM/vocab/metric held constant.

1. COMPOSITIONAL REASONING: substrate-compose vs substrate-no-compose (bind
   replaced with no-op/addition) at fixed primitive vocab; holdout (A_i, B_j)
   pairs. HARD_PASS = +0.20 holdout accuracy with cv<=0.05. AVOID: text8
   perplexity vs word-bigram.

2. LOSSLESS RETRIEVAL: substrate at f=0.02/0.05/0.50; substrate at N_DIM
   4096/8192; same M=(100..5000). HARD_PASS = top1>=0.95 at named M. AVOID:
   LSH/HNSW comparison (paradigm-cross; valid only as tagged two-paradigm
   cell).

3. CAPACITY: M_critical vs N_DIM at varied codebook (Kerdock / uniform /
   antipodal). Pre-reg alpha_c coefficient. AVOID: floating-point storage.

4. WORKING MEMORY: capacity-vs-bank-count for K modular macrocolumn;
   substrate-M=1 vs M=4 vs M=16. HARD_PASS = K=15 with top1>=0.90. AVOID:
   transformer KV cache span tests.

5. CONTINUAL LEARNING: replay-rate sweep (r=0 / r=0.5 / r=1.0); forgetting
   curve substrate-CLS vs substrate-no-replay. AVOID: vs EWC/L2 transformer
   without matched-budget tag.

6. GENERALIZATION: SCAN-style novel compositions; substrate-memorized-only
   vs substrate-compose; substrate-random-compose as sanity floor.

## L3 -- Substrate-as-LM corrected framework

Per the n1v3 audit (notes/research_n1v3_provenance_audit_2x_drill_2026-06-24)
and the bias audit, substrate-as-LM has THREE distinct worlds that have been
treated as one:

- WORLD A: text8 + word2vec-google-news-300 -> sparse-bipolar f=0.05 ->
  N_DIM=8192 -> VOCAB_CAP=4000. (fair_harness rail; cf-RPE family; K2/PC/MH
  compose family.) bpc=7.306 / top1=0.213.
- WORLD B: Pythia-160m residuals -> sparse-Willshaw f=0.006 -> N_DIM=4096 ->
  V_TOK=50087. (n1_v3 anchor.) top1=0.4455.
- WORLD C: synthetic codebooks (HRR / bipolar chains).

The corrected substrate-as-LM framework partitions all cells by world AND
treats cross-world claims as their own special class:

INTRA-WORLD A discriminators (the right place for most LM ablations):
- does cf-RPE help? -> substrate-cf-RPE vs substrate-no-cf-RPE (same encoder,
  metric, corpus). Lift bar quoted ONLY against intra-family Hebbian rail; do
  not propagate as "substrate-vs-real-LM" unless paired with bigram baseline.
- does K=2 compose help? -> substrate-K2 vs substrate-K1 (same).
- does PC-hierarchy help? -> substrate-PC vs substrate-no-PC (same; 4-arm to
  isolate from cf-RPE).
- does word-grain help? -> substrate-word vs substrate-char at MATCHED V_eff
  (i.e. not "4000 word vocab vs 27 char tokens" which is paradigm-cross at the
  vocab axis; either match V or match information-content of the unit).

INTRA-WORLD B discriminators (n1v3 family):
- does an n1v3 readout help downstream of cf-RPE? -> only valid if BOTH arms
  ingest Pythia residuals at the same f / N_DIM / V_TOK.
- the v1/v2_BUGFIX failure mode (ported to WORLD A) is the methodological
  warning: same name + different corpus = different mechanism.

CROSS-WORLD comparison (special class, only when explicitly tagged):
- "two-paradigm compare" cells must include word-bigram baseline at the WORLD A
  encoder AND must explicitly tag "substrate vs statistical LM" rather than
  framing as substrate-general.
- Bar for these: substrate must beat word-bigram by >=0.05 top1 AND with
  audit-chain capability that bigram cannot provide. The capability axis is
  load-bearing -- substrate without auditable composition has no advantage
  worth claiming over a 1ms bigram lookup.

AVOID at the framework level:
- Substrate-vs-unigram-only verdicts. Unigram is a floor; clearing unigram is
  necessary not sufficient. The right intra-world bar is the strongest
  intra-world baseline (Hebbian rail for ablations; bigram for two-paradigm
  cells).
- Cross-world atom citation. n1v3 top1=0.4455 lives in WORLD B; cf-RPE +12%
  lives in WORLD A; quoting both in the same lift table is the dominant bias.

## L4 -- Substrate-product evaluation framework

Product = auditable AI-memory subsystem. Evaluation is substrate-as-memory
on its own axes, NOT substrate-as-LM-perplexity.

1. AUDIT-CHAIN COHERENCE: prediction -> top-5 contributing atoms with
   weights; human or LLM-judge rates coherence 5-point. HARD_PASS = mean
   coherence >=0.80 across 100 queries. Baseline: audit-disabled
   (final-readout only). Statistical LMs have NO competing capability.

2. KNOWLEDGE STORE THROUGHPUT: M tuples ingested/held/retrieved at
   top1>=0.95; ingest_rate and query_latency pre-reg'd. Baseline:
   substrate-different-bank-config. Optional two-paradigm: vector DB
   (tagged).

3. REFUSE-GATE: in-store query precision >=0.95; out-of-store rejection
   >=0.80. Baseline: substrate-without-refuse-threshold. The asymmetry
   (refuse-feature vs hallucination-bug) means the cap_map closure-rescue
   axis is here.

4. COMPOSITIONAL GENERALIZATION: as in L2 (K=15 holdout >=0.70, cv<=0.05).

5. ENERGY / OPS PER QUERY: substrate ops/query at f=0.05 vs f=0.50;
   per-query cost must follow predicted scaling within 10%. Optional
   two-paradigm: transformer at matched task (fact retrieval, not free
   generation).

6. CONTINUAL LEARNING / NO-FORGETTING: forgetting curve substrate-CLS vs
   substrate-no-replay (intra-lane). Two-paradigm = transformer + EWC
   matched-budget, tagged.

The product framework explicitly DOES NOT include "substrate vs GPT-x on
text8 perplexity" -- paradigm-cross test the substrate is not designed
for.

## L5 -- Restructuring recommendations

A. CELLS TO RE-FRAME (re-interpret existing data; do not re-run):
   - n1v3_x_cfrpe v1 + v2_BUGFIX: PROVENANCE_FAIL is "cross-corpus port
     failure" not "mechanism failure" -- atomize as
     META_CROSS_WORLD_PORT_REQUIRES_RE_LAND.
   - pc_hierarchy_fair_harness_v1: re-tier to MEASURED_MECHANISM pending
     4-arm split to isolate PC contribution from cf-RPE contribution; the
     +0.005 top1 is noise-grade, +0.085 BPC vs unigram is paradigm-cross.
   - cfrpe_per_token_adaptive_lr "single-arm record": qualify all citations
     to "intra-family vs Hebbian rail at fair_harness encoder" -- not
     substrate-vs-real-LM.
   - continual_learning_spectrum: HONEST framing "synthetic per-domain
     permutations + intra-lane CL primitives"; do NOT propagate as "CL moat"
     until real-corpus + matched-budget transformer baseline lands.

B. CELLS TO ADD NEW ARMS (existing cell with arm gap):
   - substrate_pc_hierarchy_fair_harness_v2: 4-arm (PC-only / cf-RPE-only /
     PC+cf-RPE / neither) on same encoder; isolates each mechanism.
   - cf-RPE family extension: add WORD-BIGRAM baseline arm at fair_harness
     encoder; quantify the gap between intra-family lift and beat-bigram.
   - top1_targeted_plasticity production-config follow-on: when smoke clears,
     add SUBSTRATE-NO-PLASTICITY arm explicitly (not just cf-RPE-reference).

C. NEW CELLS TO DESIGN (substrate-native evaluations missing from program):
   - substrate_n1v3_corpus_transfer_discriminator_v1 (already in plan; AUTHOR
     IT). Re-land n1v3 atom on text8 + word2vec ingest with f=0.006
     concept-sparse-Willshaw; measure top1 in WORLD A. Either it transfers
     (then compose cells can quote +61.6% as substrate-general) or it does
     not (then n1v3 is Pythia-residual-specific and atom is corpus-tagged).
   - substrate_audit_chain_coherence_v1: produce top-5 contributing atoms
     per prediction; LLM-judge or human rates coherence; chain-grade if mean
     coherence >=0.80 across 100 queries. This is the substrate-product axis
     missing from the cert ledger.
   - substrate_refuse_gate_v1: in-store / out-of-store query partition;
     measure precision + rejection rates. Tests substrate's refuse capability
     intra-lane (at different confidence thresholds).
   - substrate_capacity_intra_lane_sweep_v1: M-sweep at fixed encoder,
     varying f / N_DIM / codebook (Kerdock vs uniform vs antipodal). The
     intra-lane capacity discriminator missing from current evidence.
   - substrate_continual_learning_real_corpus_v1: replace synthetic
     permutations with text8 partitioned by topic (or WikiText partitioned by
     section); measure intra-lane CL primitives at real-corpus distribution
     BEFORE quoting any moat claim. Two-paradigm transformer arm optional and
     explicitly tagged.

D. CORPUS PROVENANCE TAG ON ALL CERT ATOMS (process change, not a cell):
   - Every chain-grade atom carries (corpus, encoder_paradigm, N_DIM, vocab,
     metric_primary, baseline_paradigm) in its cert_ledger.jsonl provenance.
   - Atom citations must surface the tuple when crossed against a different-
     world atom.
   - The Skunkworks audit recommended this; this drill seconds the
     recommendation as load-bearing for cross-cell propagation.

E. STANDING DISCIPLINE (carry into all future cells):
   - Pre-cell CONFOUND_AUDIT step: write the (corpus, encoder, N_DIM, vocab,
     metric, baseline) tuple BEFORE designing arms. If
     mechanism_paradigm != baseline_paradigm, the cell must include an
     explicit "two-paradigm tag" and the verdict cannot atomize as
     substrate-general.
   - Pre-cell INTRA_LANE_DELTA arm: at least one arm where everything except
     the named mechanism is held constant; absence of this arm = no causal
     claim on the mechanism.
   - Bigram baseline at fair_harness encoder is standing-required for all
     BPC-primary cells in WORLD A. Word-bigram has not been beaten in this
     world; lifts versus weaker baselines should be qualified, not
     propagated as substrate-general.

CELL-DESIGN TEMPLATE (for future LM-relevant cells):

```
Arms (minimum 4):
  ARM_1: SUBSTRATE-WITH-MECHANISM (the candidate)
  ARM_2: SUBSTRATE-WITHOUT-MECHANISM (intra-lane discriminator; everything
         else identical)
  ARM_3: SUBSTRATE-RAIL (provenance check; matches a prior chain-grade
         landing within +/-0.05 drift)
  ARM_4: WORD-BIGRAM (the strong cross-paradigm baseline at fair_harness
         encoder; explicitly tagged as two-paradigm comparison)
Metric primary: top1 (per Fix #28); BPC secondary.
Pre-reg HARD_PASS: ARM_1 - ARM_2 >= named_delta (intra-lane causal lift)
                   AND ARM_1 - ARM_4 >= 0.0 (clear two-paradigm bar; even
                   noise-clear over bigram is publishable as
                   not-worse-than).
Pre-reg HARD_FAIL: ARM_3 drifts >0.05 from rail (provenance broken).
```

## Cross-thread synthesis

Per prior drills:
- META_HARNESS_RIGGED (2026-06-23): substrate-as-LM test harness rigged at
  T=1.0 cosine softmax; fair_harness fixed it. The bias-audit shows the
  fix held, but propagation outside fair_harness is uncontrolled.
- n1v3_provenance_audit (this morning): same root cause -- WORLD B atom
  ported to WORLD A without re-landing.
- Skunkworks bias audit (this morning, parent of this drill): catalogued
  bias on 22 cells; the present drill provides the corrective framework
  and the cell-design template.
- USER directive `feedback_brain_is_existence_proof`: brain has substrate
  strengths; we should test those, not transformer strengths. L2 framework
  directly implements this.

## Substrate-product implications

The substrate product story does not hinge on beating word-bigram on BPC.
It hinges on auditable AI-memory subsystem capability -- knowledge store +
compositional reasoning + continual learning + refuse-gate. The corrected
evaluation framework re-routes effort to the SUBSTRATE-PRODUCT axes (L4),
where the comparison is intra-lane and the capability is uniquely
substrate's. The substrate-as-LM lane (L3) remains valuable for internal
ablations of mechanisms (cf-RPE, K2, PC) but should not be the headline
benchmark.

If apples-to-apples on the L4 axes lands chain-grade (audit-chain coherence
>=0.80; refuse-gate precision >=0.95; capacity at named M; continual-
learning forgetting reduced vs no-replay), the substrate product has a
defensible apples-to-apples evidence base independent of LM benchmarks.

## Citations (verified count: 4 internal references)

- notes/skunkworks_experiment_bias_audit_2026-06-24.md (parent audit; 22-cell
  per-cell entries).
- notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md (cross-world
  port failure mode).
- project_session_2026-06-23_FINAL_pickup_state.md (n1v3 chain-grade evidence
  in WORLD B; fair_harness rail in WORLD A).
- feedback_fix28_verify_per_arm_metrics_not_summary_verdict_text_2026-06-22.md
  (top1-primary discipline; underpins L2/L3 metric recommendation).

End of drill.
