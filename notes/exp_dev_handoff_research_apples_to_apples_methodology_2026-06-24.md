# exp_dev hand-off -- research: apples-to-apples substrate evaluation methodology

Filed-by: research (Opus 4.7) 2026-06-24
Trigger: USER directive 2026-06-24 -- "apples to apples, no bias"; corrective
framework derived in `notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md`
on top of the Skunkworks bias audit at
`notes/skunkworks_experiment_bias_audit_2026-06-24.md`.

Pause state: defer to `data/orchestrator_paused.flag` at dispatch time. If
paused, atomize anchor candidates without dispatching cells.

Per [[feedback-no-experiment-design-in-prompts]] this hand-off names anchor
candidates with substrate-product reading + tier hint + why-now; it does NOT
prescribe cell internals. exp_dev owns cell design and arm structure.

## Anchor candidates (rank-ordered)

### 1. substrate_n1v3_corpus_transfer_discriminator_v1  (TIER: CHAIN-GRADE-ELIGIBLE)
Anchor pointer: re-land n1_v3 atom on text8 + word2vec ingest at WORLD A
encoder (sparse-bipolar f=0.05 or matched f=0.006 concept-sparse-Willshaw);
measure top1 on the SAME corpus the cf-RPE family uses.
Substrate-product reading: this discriminator gates whether the +61.6% n1v3
top1 is substrate-general (transfers to WORLD A) or Pythia-residual-specific
(does not). Two failed compose cells (v1 + v2_BUGFIX) cost the program two
sessions already; this cell prevents a third.
Why-now: highest priority. All "n1v3 x cf-RPE" claims are blocked on this
until it lands; downstream compose cells cannot proceed without the
provenance bridge.

### 2. substrate_audit_chain_coherence_v1  (TIER: CHAIN-GRADE-ELIGIBLE; new axis)
Anchor pointer: for each substrate prediction, surface top-5 contributing
atoms with weights; LLM-judge (or pre-vetted human-rating script) scores
coherence on a 5-point scale across 100 queries.
Substrate-product reading: AUDIT-CHAIN is the substrate-product capability
NO statistical LM can provide. This is the apples-to-apples axis where
substrate has no peer baseline by construction; the only baseline is
substrate-with-audit-disabled. Chain-grade if mean coherence >=0.80.
Why-now: cap_map row coverage gap. Substrate product story currently rests
on capacity + composition; auditability is named but never measured. This
cell adds the missing chain-grade evidence on the product's headline axis.

### 3. substrate_refuse_gate_v1  (TIER: CHAIN-GRADE-ELIGIBLE; new axis)
Anchor pointer: partition queries into in-store (atom exists) vs out-of-store
(atom never ingested); measure precision on in-store (>=0.95 pre-reg) and
rejection rate on out-of-store (>=0.80 pre-reg) across substrate confidence
thresholds.
Substrate-product reading: the cap_map closure-rescue axis. Substrate's
REFUSE is a feature; LLM hallucination is a bug; the asymmetry means this is
the substrate-as-memory product story's load-bearing capability.
Why-now: precondition for any "substrate as auditable AI-memory" claim
beyond capacity. The story has been told without the evidence.

### 4. substrate_pc_hierarchy_fair_harness_v2_4arm  (TIER: RE-TIER existing finding)
Anchor pointer: 4-arm split (PC-only / cf-RPE-only / PC+cf-RPE / neither) on
fair_harness encoder; isolate PC contribution from cf-RPE contribution. The
v1 reported HARD_PASS on +0.005 top1 + OR-gated metric -- weak discriminator.
Substrate-product reading: re-tier the v1 to MEASURED_MECHANISM until the
4-arm split lands. Per the bias audit; reaffirmed by this drill.
Why-now: prevents PC-hierarchy from being cited as chain-grade in compose
cells until the contribution is isolated. Cheap (intra-family, fair_harness).

### 5. substrate_capacity_intra_lane_codebook_sweep_v1  (TIER: chain-grade-eligible)
Anchor pointer: M-sweep at fixed encoder, varying codebook (Kerdock /
uniform-random / antipodal) at fixed N_DIM=8192. Measure M_critical and
top1 at named M. The intra-lane capacity discriminator missing from the
current evidence.
Substrate-product reading: directly answers "does the codebook choice
shift the capacity slope or the intercept?" -- a substrate-product knob.
Apples-to-apples by construction (encoder/N_DIM/f held; codebook varied).
Why-now: under-drilled axis; cheap on synthetic; resolves a long-standing
"which codebook for production" question intra-lane.

### 6. substrate_continual_learning_real_corpus_v1  (TIER: PARTIAL until two-paradigm cell lands)
Anchor pointer: replace synthetic per-domain permutations with text8
partitioned by topic or WikiText partitioned by section; measure intra-
lane CL primitives (replay-rate sweep) at REAL-CORPUS distribution.
Substrate-product reading: gates any "CL moat" claim. The
continual_learning_spectrum cell is honest about synthetic-only; this is
the real-corpus follow-on that lets the moat claim atomize at the next
tier.
Why-now: blocks the moat citation downstream; only chain-grade evidence
the prompt asks for that is also intra-lane by definition (substrate-with-
CL vs substrate-without-CL; transformer baseline optional/later).

## Standing discipline (pre-cell gate for ALL future cells)

CONFOUND_AUDIT step: BEFORE designing arms, write the (corpus, encoder,
N_DIM, vocab, metric_primary, baseline_paradigm) tuple. If
`mechanism_paradigm != baseline_paradigm`, the cell must include an
explicit "two-paradigm tag" and the verdict cannot atomize as
substrate-general.

INTRA_LANE_DELTA arm: at least one arm holds everything constant except the
named mechanism. If absent, no causal claim on the mechanism is supported.

CORPUS PROVENANCE on cert atoms: every chain-grade atom carries (corpus,
encoder_paradigm, N_DIM, vocab, metric_primary, baseline_paradigm) in its
cert_ledger.jsonl provenance. Cross-world citations must surface the tuple.

WORD-BIGRAM baseline arm: standing-required for all BPC-primary cells in
WORLD A (fair_harness encoder). Word-bigram has NOT been beaten in this
world; lifts versus weaker baselines must be qualified, not propagated as
substrate-general.

## Context pointers

- Parent drill (this hand-off's source):
  `notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md`
- Skunkworks 22-cell bias audit (the per-cell breakdown):
  `notes/skunkworks_experiment_bias_audit_2026-06-24.md`
- n1v3 provenance audit (cross-world port failure mode):
  `notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md`
- META_HARNESS_RIGGED context (substrate-as-LM harness fix):
  `project_substrate_as_LM_test_harness_rigged_2026-06-23_methodology_audit.md`
- Fix #28 metrics discipline (top1 primary; verify per-arm not verdict_msg):
  `feedback_fix28_verify_per_arm_metrics_not_summary_verdict_text_2026-06-22.md`

## Contract

This hand-off names anchor candidates + tier hints; it does not design cells.
exp_dev owns: arm structure, pre-reg bands, smoke gate, queue routing,
self-test, post-ship REMOTE VERIFY, smoke envelope-fail-bands. Skunkworks
owns: post-landing VET + cert tiering.

## Autonomy declaration

exp_dev decides: which anchor to prioritize (top-2 are roughly equal in
strategic value; bias audit and product story both name the n1v3 corpus-
transfer-discriminator as the unblocking dependency); how many to ship per
cycle (~3-spawn budget per Fix #14); whether to bundle adjacent anchors
(audit-chain-coherence and refuse-gate share infra and may bundle).

End of hand-off.
