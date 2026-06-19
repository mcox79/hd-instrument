# Pre-registration: wave14r_multihop_cooper_pair_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy push (Bet O — queued after Bet N per cycle 42 followup)
Author: experiment_dev session, pipeline tick 70

## Why

R8 rescue list closed (all 5 KILLED: A1 FHRR, C1 hybrid, B1 modern Hopfield,
B3 adaptive-beta, Bet N soft cleanup). d=25 cliff is architectural for the
single-encoding regime.

Bet O is a STORAGE/ENCODING-side rescue (vs all prior CLEANUP/BINDING-side
rescues). Mechanism: encode each fact TWICE with independent random twists.
Cleanup requires BOTH representations to agree — gap-protected redundancy
analogous to Cooper pairs in BCS superconductivity (single-twist corruption
doesn't break the pair).

Storage cost doubles; acceptable at M/N <= 8 (current substrate operating point).

## Mechanism

Two global random twist atoms t_1, t_2 in {-1,+1}^N. For each (subj, rel, obj):
  store both:  triple_1 = (subj*t_1) * (rel*t_1) * (obj*t_1)
               triple_2 = (subj*t_2) * (rel*t_2) * (obj*t_2)
  M = sign(sum of all triples)

Multi-hop cleanup at each hop:
  probe_1 = M * (current*t_1) * (rel*t_1)
  probe_2 = M * (current*t_2) * (rel*t_2)
  sims_1 = (entity_atoms*t_1) @ probe_1      # similarity in twist_1 space
  sims_2 = (entity_atoms*t_2) @ probe_2
  combined = sims_1 + sims_2                  # require both to agree
  current_idx = argmax(combined)

## Verdict labels

- BET_O_50HOP_VALIDATED (acc_50 >= 0.50 — rescues multi-hop via gap protection)
- BET_O_PARTIAL (0.22 <= acc_50 < 0.50; beats single-encoding floor)
- BET_O_KILLED (acc_50 < 0.22; redundancy alone doesn't help; encoding axis closed)
- BET_O_INCONCLUSIVE

## Runtime: ~12 min full
