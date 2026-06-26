# Skunkworks batch 2 (4-artifact ratified rulings) ATOMIZE COMPLETE + RC backlog hand-off

Auditor: skunkworks (cert-owner, A5 role-separation)
Date: 2026-06-26 (UTC)
Source ruling: `notes/skunkworks_tier_rule_batch2_4artifact_2026-06-26.md`
Director ratification: AUTO mode + USER full-auto (per task spec)

## One-line summary

6 atoms atomized A5-gated; +3 CERT delta (1 chain_grade + 1 proven_bound + 1 honest_negative);
+0 cert-neutral (1 MM + 1 META + 1 MIDDLE_BAND); Store LOADS clean; axiom 206 invariant; cap_pres
6/6 invariant; cert_ledger 755 -> 761 [+6 rows]; total_atoms 177371 -> 177377;
CERT_CHAIN_GRADE_provenance 603 -> 606; cap_map v595 -> v596; hdlab/multi_hop.py +
hdlab/continual.py updated per ruling.

## Atoms landed (A5-verified; fresh-Store round-trip)

| # | atom_id | cert_status | delta | ledger row hash |
|---|---|---|---|---|
| 1 | `math::T3/EXP_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail_chain_grade_partition_per_hop_5hop_0p955_cv_0p007_meta_M7_pass_oracle_routing_scope_flag` | chain_grade | +1 | 65fe10172a09655a |
| 2 | `math::T3/EXP_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail_measured_mechanism_oracle_routing_required_for_5hop_chain_grade_substrate_native_routing_open` | measured_mechanism | 0 | 434ba5e77e8f0f94 |
| 3 | `meta::T3/META_BARRIER_1_QUINTUPLE_RECONCILIATION_substrate_5hop_partition_per_hop_routed_chain_grade_at_0p955_cv_0p007_meta_M7_pass_narrows_quadruple_negative_to_routing_required_5hop` | custom (discipline_meta) | 0 | 44f5a935a10d74d0 |
| 4 | `math::T3/EXP_substrate_continual_NREM_replay_v1_proven_bound_replay_reduces_drift_0p57_abs_best_arm_0p31_final_forget_chain_grade_bar_0p05_not_met_monotone_in_replay_frequency_director_honest_downgrade` | proven_bound | +1 | 05578a221fb552d7 |
| 5 | `math::T3/EXP_substrate_synaptic_homeostasis_global_downscale_v1_HARD_FAIL_proven_negative_global_multiplicative_downscale_destroys_older_traces_uniformly_3of3_arms_all_seeds_clean` | honest_negative | +1 | 8df72f13565ad573 |
| 6 | `math::T3/EXP_substrate_cortical_schema_extraction_compositional_generalization_v1_MIDDLE_BAND_feature_based_schema_lift_0p10_over_no_schema_capability_based_hurts_combined_hurts_micro_scale_regime_n_heldout_50_per_seed` | custom (MIDDLE_BAND) | 0 | 9036304faf807148 |

CERT delta: +3 (atoms 1, 4, 5).

## Cap_map state-transitions

- Gap 1 (multi-hop): RED -> AMBER (Cell B v2 chain-grade routing-provided regime; substrate-native routing open follow-up)
- Gap 3 (compositional generalization / schema): UNKNOWN -> AMBER (feature-axis partial; capability-axis negative; micro-scale needs 10x discriminator)
- Gap 4 (continual-learning consolidation): RED -> AMBER (NREM proven-bound; REM-global HARD_FAIL; selective REM + composition path armed)

Cap_map v595 -> v596 section appended to `notes/substrate_capability_map.md` (lines 29531+).

## hdlab/ primitive updates (committed in this batch)

- `hdlab/multi_hop.py`: ADDED `partition_routed_chain(kg, start, relations, partitions, router, *, oracle_routing=True)` -- per-hop PARTITION routing primitive operationalizing the Cell B v2 chain-grade mechanism. Honest-scope docstring documents oracle-routing scope flag, references chain-grade + MM + META atoms.

- `hdlab/continual.py` (NEW MODULE):
  - `replay_cycle(W, replay_indices, keys, values, replay_frac=0.2, lr=1.0)` -- single NREM replay cycle (re-Hebb a fraction of stored traces).
  - `nrem_replay_decorator(write_fn, *, replay_every=100, replay_frac=0.2, replay_lr=1.0)` -- decorator wraps continual-write step with periodic replay.
  - Honest-scope docstring states partial-mitigator bound (final_forget=0.31; chain-grade bar 0.05 NOT met); references RC4/RC5/RC6 open follow-ups.
  - `global_downscale_decorator` INTENTIONALLY NOT EXPOSED as a public API (proven negative per atom 5). Replaced with module-level comment explaining the proven-negative + revival angle (selective-not-global; RC7 composition with NREM).

Smoke-imports verified clean via `.venv/Scripts/python.exe`.

## RC follow-up backlog (DIRECTOR-OWNED; queued not dispatched per A5 role-separation)

Skunkworks is AUDIT-ONLY. The cells below are recommendations carried over from the ruling note; Director routes for dispatch under the next exp_dev spawn cycle.

### Multi-hop / BARRIER_1 closure (resolves Cell B v2 oracle scope)

- **RC1 relation-typed routing**: per-hop routing key = relation embedding; router selects partition/bank holding bindings of that relation type. Discriminator: substrate-native (no oracle). Pre-reg band suggested: HP >= 0.50, MM [0.35, 0.50], HF < 0.35.
- **RC2 HRR-bind-routing**: per-hop routing key = HRR bind of (query, role). Tests whether the substrate's binding primitive can substitute for oracle's partition map.
- **RC3 learned-router (no LLM)**: substrate-native classifier maps current state to partition index; trained from chain examples; held-out chains at test. Discriminator vs RC1/RC2: learning vs primitive routing.

### Continual-learning consolidation (resolves NREM MM bound + REM HF revival)

- **RC4 finer NREM replay schedule**: every-25 / every-50 / every-100 head-to-head; tests whether the cliff at cycle 250-500 can be prevented by finer granularity. Discriminator: cliff disappears?
- **RC5 replay-fraction sweep**: replay_frac at 0.1, 0.2, 0.4, 0.6, 0.8 (cell fixes 0.2; brain awake/sleep ~30-40%). Discriminator: does aggressive replay drive final_forget below 0.20?
- **RC6 cleanup-aided replay**: NREM replay + Modern-Hopfield cleanup over replayed subset. Discriminator: does cleanup-during-replay close the chain-grade gap?
- **RC7 selective REM + NREM composition**: continual writes + NREM every 100 + REM selective downscale every 500 (downscaling only rows with recent activation below threshold). Discriminator: forget below 0.20?

### Compositional generalization / schema (resolves Cortex MIDDLE_BAND)

- **RC8 large-scale feature-schema discriminator**: 10x scale -- n_heldout_per_cat=100, n_categories=10, instances_per_cat=50. Same feature-schema mechanism. Pre-reg suggested: HP_lift >= 0.15 over no-schema; MM band [0.05, 0.15]; HF < 0.05.
- **RC9 capability-schema scale sweep**: test whether the capability arm's hurt reverses at larger n_categories or larger N. Discriminator: sample-limited or fundamentally wrong?

## A5 PRE/POST verification

```
PRE:  CERT_CHAIN_GRADE_prov=603  axiom=206  cap_pres=6/6  total_atoms=177371  ledger=755 rows
POST: CERT_CHAIN_GRADE_prov=606  axiom=206  cap_pres=6/6  total_atoms=177377  ledger=761 rows
delta: +3 CERT_CHAIN_GRADE_prov   +6 atoms    +6 ledger rows   axiom INVARIANT   cap_pres INVARIANT
fresh-Store round-trip verify: ALL 6 atoms LANDED + provenance_quality round-trip-survived
ledger writer A5 PRE/POST: every row passed strict-A5 (axiom 206 + cap_pres + idempotency)
```

## Disciplines applied

- Verify-OFF-DATA: every cited number reproduces from raw metrics.json per-arm aggregation; no verdict_msg framings inherited (Fix #28)
- A5 single-writer + atomic write + verify-load + integrity-check on every Store partition
- Foreground execution (no run_in_background) for sequential Store + ledger writes
- Idempotency: per-atom collision detection; safe re-run
- Path-scoped commit only (NEVER `git add -A`); explicit paths for data/substrate_index/, notes/, hdlab/, tools/
- ASCII-only (no unicode in tool sources)
- .venv Python (NEVER system; duckdb/torch false-green risk)

## Atomize tool

`tools/skunkworks_atomize_batch2_4artifact_2026-06-26.py` (committed in this batch).

## Next cert-owner ask

Director: routes RC1-RC9 backlog under the next exp_dev spawn cycle. Cert-owner is AUDIT-ONLY for the dispatch path; SCHEMA-VET available on RC pre-regs before dispatch.
