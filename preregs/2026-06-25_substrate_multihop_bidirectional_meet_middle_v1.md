# PREREG: substrate_multihop_bidirectional_meet_middle_v1

**Date:** 2026-06-25
**Author:** exp_dev (via Research 5x revival drill)
**Revival angle:** ANGLE 3 (bidirectional meet-in-middle)
**Source drill:** `notes/research_multihop_revival_5x_drill_2026-06-25.md`
**Brain prior:** STRONG (cortical-cortical bidirection universal; hippocampal forward-backward replay during sharp-wave ripples — Foster-Wilson 2006 Nature)

## Hypothesis

Forward-only multi-hop compounds error at every step. The substrate's unbind primitive (hdlab/binding.py:30) supports walking the chain in REVERSE: given the answer Z and the predicate sequence, unbind via W.T then re-bind R[p] (bipolar HRR R is involutive) to recover predecessors. By walking forward MID hops from S and backward (depth-MID) hops from each candidate Z, then ranking by midpoint state-cosine, we halve the compounding for each direction:
- 5-hop forward only: per-step floor 0.69 -> 0.69^5 = 0.156
- Bidirectional: 0.69^2 forward + 0.69^3 backward; midpoint match is HIGH-SIGNAL when chain is correct (uncorrelated errors)

## Mechanism (substrate-only; zero LLM forward calls)

- ARM_SINGLE_CHAIN_5HOP_FORWARD: pointer-chain v2 monolithic 5hop (rail)
- ARM_BIDIRECTIONAL_5HOP_MEET_HOP2: walk forward 2 hops, backward 3 hops; report midpoint state-cosine on CORRECT-chain queries (no ranking; probe arm to verify mechanism)
- ARM_BIDIRECTIONAL_5HOP_MEET_MID: walk forward MID hops; for each candidate Z in V_C, walk backward (depth-MID) hops; top1 = argmax over candidates by midpoint cosine
- ARM_BASELINE_HRR_2HOP: beta-sweep sanity rail

Critical self-test built into cell: single-triple W must give positive forward-cosine AND positive backward-cosine to verify unbind math is correct.

Also reports: error-correlation between forward-only and bidirectional across queries. Low correlation = bidirectional gives INDEPENDENT signal; high correlation = bidirectional just re-encodes forward error.

## Regime

- N=8192, V_C=200, V_P=10, K_SET=20, n_chains=200, seeds=[7, 17, 23]
- Midpoint = depth//2 = 2 hops forward, 3 hops backward
- Candidates = all V_C entities (V_C=200; computationally tractable)

## Pre-registered bands (LOCKED via assert at module init)

- **HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL**: BIDIRECTIONAL_MEET_MID top1 >= 0.50 AND cv <= 0.07
- **HARD_PASS_PARTIAL**: BIDIRECTIONAL_MEET_MID top1 >= 0.25
- **MIDDLE_BAND**: BIDIRECTIONAL_MEET_MID top1 in [0.15, 0.25]
- **HARD_FAIL_BIDIRECTIONAL_DOESNT_HELP**: BIDIRECTIONAL_MEET_MID top1 < 0.15
- **SANITY_BREACH**: ARM_BASELINE not in [0.62, 0.68] for majority of seeds

## META-discipline

- META_PROSPECTIVE_BANDS_FRESH_SEEDS: bands locked at module-init via assert
- META_M7: smoke must NOT show >> 0.50 lift over rail
- Fix #28: per-arm metrics reported; error-correlation explicit

## Strategic significance

- HARD_PASS: substrate-native bidirectional unbind chain works; multi-hop revival via reverse-walk; mechanism is genuinely different from prior 4 HARD_FAIL attempts (those were all forward-only downstream of cleanup)
- HARD_PASS_PARTIAL: bidirectional gives some lift; combine with Angle 5 (PFC chunking) — chunk + bidirectional-per-chunk as second wave
- MIDDLE_BAND: partial; if error-correlation is HIGH, bidirectional doesn't add info; if LOW, the lift is real but the bands are calibrated wrong
- HARD_FAIL: rules out bidirectional revival; the W matrix's per-cue crosstalk dominates regardless of direction

## Cost

~25-35 min on local_cpu_queue (substrate-only; numpy; 3 seeds; ranking arm does V_C=200 backward walks per query x 200 queries x 3 hops = ~120k mat-vec; bounded but not trivial)
