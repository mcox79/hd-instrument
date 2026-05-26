# Pre-reg: Bet A continual edit 5-seed v3 -- N=32768 OOM-safe respec

**Date**: 2026-05-23
**Experiment**: wave14_betA_continual_edit_5seed_v3
**Script**: experiments/exp_wave14_betA_continual_edit_5seed_v3.py
**Cap-map axis**: Bet A editable memory at scale (capability class 2)

## Background and motivation

v1: OOM at M_init=N=65536 (8.6 GB bf16 W alone exceeds 8 GB GPU).
v2: Targeted N=65536 M_init=8192; smoke PASSED at N=4096; FULL on remote
    OOM per cycle 175 Sweep A -- even M_init=1024 at N=65536 exceeds 8 GB.
v3: Re-specs to N=32768 (W=2.15 GB bf16; fp32 edit peak ~4.3 GB; total <5 GB;
    safe margin on 8 GB GPU). M_init=4096 maintains M/N=0.125, the same
    substrate-product operating ratio validated in cycle 172 v2 smoke and the
    N=4096 substrate baseline.

N=32768 is a genuine production scale: 8x the N=4096 smoke scale, 4x larger
than default N=8192 workloads, and within the substrate's characterized
N-scaling envelope (N=65536 scaling tested in wave14_substrate_N_* series).

## Protocol

- N=32768, M_init=4096, M/N=0.125
- n_edits=100 (same as v2 FULL; sufficient to test edit-then-kept integrity)
- seeds: [17, 23, 31, 41, 53] (same 5-seed set as v2)
- Anti-Hebbian erase + insert (ba.run_one_seed from N65536_v1 base)
- Smoke: N=4096, M_init=512, n_edits=50, 2 seeds

## Verdict criteria

- **BETA_5SEED_PASS**: mean edit_acc >= 0.95 AND mean kept_acc >= 0.95 AND sd < 0.05
- **BETA_5SEED_PARTIAL**: mean >= 0.5 for both
- **BETA_5SEED_KILLED**: mean < 0.5 (substrate fails editable memory at N=32768 M/N=0.125)
- **BETA_5SEED_INCONCLUSIVE**: missing metrics

## Expected outcome

BETA_5SEED_PASS at P=0.85. Reasoning:
- v2 smoke at N=4096 M/N=0.125 returned edit_acc=1.000 kept_acc=1.000 across 2 seeds
- The N=32768 regime with M/N=0.125 is within the AGS-class capacity envelope
- N-scaling from wave14_substrate_N_* confirms substrate operates at N=32768
- Only failure mode is if N-scaling introduces unexpected cross-talk at N=32768 M/N=0.125

Hard-fail threshold: BETA_5SEED_KILLED is a genuine substrate refutation
(not OOM-inconclusive) and would trigger PROT-004/006 rehab discipline
(5 rescue sketches + Research routing).

## Substrate-product implication

If BETA_5SEED_PASS: substrate editable memory confirmed at N=32768 with
5-seed statistical rigor. Capability class 2 (editable memory) validated at
scale 8x the standard substrate operating point. Extends the Bet A ✅ row
from "cycle 172 v2 smoke" to "cycle 175+ v3 FULL at large N."
