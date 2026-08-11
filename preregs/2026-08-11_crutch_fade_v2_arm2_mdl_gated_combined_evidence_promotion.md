# Pre-reg: crutch_fade_social_iqa_v2_semantic_cluster_key -- ARM-2 (mdl-gated combined-evidence promotion)

**Filed-by:** exp_dev, 2026-08-11.
**Extends:** `preregs/2026-08-11_crutch_fade_semantic_cluster_key_v2.md` (the v2 ONE-VARIABLE
semantic-clustering-key fork), which in turn extends
`preregs/2026-08-10_crutch_fade_prelim_tier_staged_consolidation_v1.md` (3-tier) and
`preregs/2026-08-10_crutch_fade_social_iqa_v1.md` (binary baseline).
**Cell:** `experiments/exp_crutch_fade_social_iqa_v2_semantic_cluster_key.py` (edited in place,
commit base 72eb854e3 -- the v2 FULL run that HARD_FAILED at scale, see "Context" below).

## Prior-work check (SUBSTRATE-KB, MANDATORY per exp_dev core discipline)

`bash tools/substrate_query.sh "MDL two-part code gate combined evidence cluster promotion
conjunctive filter"` -> confidence=0.3164, top-5 hits ALL generic WordNet
`copulative_conjunction` string-collision false-positives or one unrelated routing note
(`research_routing_tier4_training_speedup...`, cosine=0.3076). **NONE at cosine>0.30 is a real
prior cell/prereg match for this specific wiring.** Verdict: genuinely novel, matching the
design audit's own explicit framing ("never exercised in any real run"). This is expected --
the design audit (`notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md`,
Gap G5 / Gap-fix (ii)) is itself the record of this gap; this cell is that gap-fix's first real
exercise.

## Context (read the numbers on disk, not the framing)

`data/exp_crutch_fade_social_iqa_v2_semantic_cluster_key/metrics.json` (FULL, commit 72eb854e3):
`verdict=HARD_FAIL`. At full scale, combined-evidence cluster promotions scored
`combined_acc=0.3515` (n=165) vs raw `cru_acc=0.3690` -- i.e. combining evidence via the
semantic-clustering-key fix was about EQUAL to (slightly below) a single raw crutch lookup, not
better. `HP2 (tier_fidelity_ok)=False`, `HP3 (comp_lift_covered)=False`. HP1 (fade) + scramble +
ablations were clean. The v2 fork's own semantic-embedding clustering key (replacing v1's
too-coarse relation-family key) did NOT flip the fidelity flags. The design audit's Gap-fix (ii)
is the NEXT untried lever, cited verbatim: "turn on the already-wired-but-unused mdl_gate_fn
hook ... as a SECOND, conjunctive filter on which clusters are even eligible to combined-evidence
promote."

## What this tests

Does gating COMBINED-EVIDENCE cluster promotions (inside `update_prelim_and_generalize`, this
cell's own cluster-grain analogue of `script_consolidation_pass`) to only clusters whose pooled
evidence is genuinely MDL-compressible (Perfors & Tenenbaum 2009 two-part code, via
`hdlab.learner.registry.learn`/`per_cluster_gate`) flip the two HARD_FAIL flags (HP2
`tier_fidelity_ok`, HP3 `comp_lift_covered`) on the SAME real Social IQa + 1.15M-edge CSKG
benchmark, holding every other v2 design element fixed?

## ONE variable

Adds exactly ONE new arm, `with_mdl_gated_promotion`, and its own parallel `TierState`
(`mdl_state`), fed the IDENTICAL real exposure stream as `real_state` (same
`process_exposure_slice` calls, same single-item promotion mirrors from `consolidation_pass`'s
`promotion_log`). The ONLY thing that differs between `with_mdl_gated_promotion` and
`gap_driven_3tier` is whether `update_prelim_and_generalize`'s combined-evidence promotion step
ALSO requires a conjunctive `mdl_gate_fn(agreeing_traces) -> bool` verdict, consulted ONLY after
the existing exposure/consistency cluster-grain gate already passes (AND semantics -- the
existing gate is NEVER loosened, only possibly made stricter). Every other v2 constant
(`HUB_DEGREE_THRESH=500`, `CLUSTER_EXPOSURE_MULTIPLIER=4`, `PROMOTE_MIN_EXPOSURE`,
`PROMOTE_MIN_CONSISTENCY`, the semantic clustering key itself, the 9 pre-existing arms, the
frozen 1,954-item dev set, the real 1.15M-edge CSKG) is held byte-identical to the landed v2
file. Single-item promotion (via `real_lib`/`consolidation_pass`) is UNCHANGED for the new arm
(only combined-evidence/cluster-grain promotion is gated).

## Design

### The adapter (`mdl_gate_decision`, copied+attributed from `experiments/exp_learner_mdl_gate_on_acquisition_traces_v1.py`)

Same feature-space design as the source cell's own proven adapter: `N_MDL_PROJECTIONS=8` fixed,
deterministic (hashlib-seeded, PROT-023/F.5-compliant) random-hyperplane sign-buckets of the
256-dim bipolar context vector (that cell's own "Amendment" section MEASURED that a dense
per-raw-dimension encoding starves `induce_rules`' own rule-cost budget; the coarse encoding is
reused verbatim, not re-derived). Operates directly over a `List[Trace]` (the exact shape
`update_prelim_and_generalize`'s own `agreeing_traces` pool already produces at the
combined-evidence decision point) -- no LibraryItem-wrapping needed, unlike the source cell's own
single-item use.

### MANDATORY pre-check finding (flat-result-means-diagnose discipline, same as the source cell's own "Amendment")

The FIRST implementation reused `ruleind_plugin`'s DEFAULT `purity_thresh=0.75`
(`experiments/exp_parser_ruleinduction_cls_ppattach_v1.py PURITY_THRESH`). Self-test (13b) --
a hand-constructed cluster whose pooled evidence carries ZERO label-correlated signal
(consistency=0.833, purity=0.917, but the encoded context vector is IDENTICAL for both POS and
NEG traces within each contributing pair -- mathematically guaranteed no rule can separate them)
-- **still promoted** (`n_mdl_blocked_this_pass=0`). Root cause: `induce_rules`' terminal "else
predict majority" default clause is ZERO-COST (`bits_rule=0.0`, `bits_exceptions=0.0`) whenever
the residual's raw majority purity clears `purity_thresh`. Since `mdl_gate_fn` is only ever
consulted AFTER the existing gate's `consistency >= promote_min_consistency (0.75)` already
holds -- i.e. purity = (1+consistency)/2 >= 0.875 by construction -- the free default clause
fires on EVERY cluster that reaches this gate at the plugin's own default threshold, making the
gate VACUOUS (always True) regardless of whether any real feature-conditional structure exists.

**Fix (implemented, re-verified, not just proposed):** `MDL_PURITY_THRESH=0.95`, passed through
`hypothesis_space_spec["purity_thresh"]` to `induce_rules`. This is comfortably above the
schema/consistency floor's own implied purity (0.875) so the free default clause is no longer
trivially available to every eligible cluster. Re-measured at self-test (13b) after the fix: the
incompressible construction (purity=0.917) is correctly BLOCKED
(`n_mdl_blocked_this_pass>=1`, `n_combined_promoted_total=0`); the SAME construction WITHOUT
`mdl_gate_fn` (default `None`) still promotes (`n_combined_promoted_total=3`) -- proving AND
semantics (the gate is doing real, non-vacuous blocking, not merely reproducing a pre-existing
block). The compressible construction (perfectly label-separable, precision~1.0) still promotes
regardless of the raised bar (an explicit compressing rule, not the free default, covers it).
Unit-level precheck against the raw adapter (16-trace balanced perfectly-separable set, matching
the source cell's own precheck construction exactly) reproduces that cell's own MEASURED
`compression_ratio=2.6016` -- confirms the copied adapter plumbing itself is correct,
independent of this cell's own cluster-grain call site. `MDL_PURITY_THRESH=0.95` is a considered,
disclosed choice made from the self-test's own diagnostic construction, BEFORE any real-corpus
dispatch -- not tuned against a FULL result.

### Wire point

`update_prelim_and_generalize` gains an optional `mdl_gate_fn: Optional[Callable[[list], bool]] =
None` parameter (default preserves prior behavior byte-for-byte for every other arm's
`TierState`). Consulted exactly once per cluster, immediately after the existing
`exposure >= cluster_exposure_floor and consistency >= promote_min_consistency` check passes:
`if mdl_gate_fn is not None and not mdl_gate_fn(agreeing_traces): n_mdl_blocked_this_pass += 1;
continue`.

## DECISIVE DEEPER MEASUREMENT (task-mandated, reported regardless of verdict)

For the mdl-gated PROMOTED subset (`with_mdl_gated_promotion`'s own
`promo_source_acc["combined_evidence_cluster"]`), does combined-evidence accuracy EXCEED that
same arm's own raw `CRUTCH_RESOLVED` accuracy (`cru_acc_mdl`)? Reported explicitly as
`decisive_measurement` in `metrics.json` (fields: `combined_acc_mdl`, `cru_acc_mdl`, `gap`,
`exceeds_raw`) regardless of the overall verdict. If gating to compressible clusters STILL
yields `combined_acc_mdl <= cru_acc_mdl`, that is evidence the COMBINATION LOGIC itself (pooling
multiple sub-threshold pairs' votes) does not add fidelity -- a deeper issue than which clusters
get selected for promotion.

## Pre-registered bands (verbatim from the task, exp_dev may not loosen)

- **HARD-PASS**: HP2 (`tier_fidelity_ok`, scoped to `with_mdl_gated_promotion`) AND HP3
  (`comp_lift_covered`, scoped to the same arm) both flip to True, AND the decisive measurement
  shows `combined_acc_mdl > cru_acc_mdl` (mdl-gated combined-evidence accuracy strictly exceeds
  raw), AND controls are clean (scramble still collapses; no-leak; the mdl gate discriminator
  actually fired -- `mdl_gate_ever_blocked=True` -- since an inert gate cannot legitimately claim
  credit for a flip).
- **HARD-FAIL**: HP2/HP3 do not both flip, OR `combined_acc_mdl <= cru_acc_mdl` on the gated
  subset, OR a control is broken, OR the gate never fired (untested mechanism).
- **MIDDLE_BAND**: none of the HARD-FAIL reasons fire, but the HARD-PASS conjunction is not
  fully satisfied (e.g. partial flip with controls otherwise clean).

Scored SEPARATELY from (and reported alongside) the pre-existing v2 3-TIER (arm-1, ungated)
verdict, which is left computed UNCHANGED (`tier_ungated_verdict` / `tier_ungated_verdict_msg` in
metrics.json) as a byte-for-byte reproduction check of the already-landed HARD_FAIL. The
TOP-LEVEL `verdict`/`verdict_msg` fields in this run's `metrics.json` report the NEW ARM-2
question (same convention v2 itself used relative to v1's own `binary_baseline_verdict`).

## SCHEMA-VET / cell-template fields

```yaml
cell_chunked: false                      # single-shot cell (5 checkpoints x 10 arms), not multi-seed
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true                  # _hb() every checkpoint; FULL wall time ~750-1000s (>15min N/A here, <30min)
progress_logging: print_flush_true       # SCHEMA-VET #17 (timeout_s >= 1800 not applicable at ~15min, still uses flush=True throughout)
defensive_error_checking: passed_all_4_patterns
final_metrics_atomicity: tmp_replace
deterministic_seeding: true              # hashlib-seeded RNG only; no hash()/list(set()) ordering
arms_differ_verified: "10-arm hash-differ check; bow/never_crutch exempted (declared);
  non-exempt collisions reported diagnostically, non-blocking (v2's own landed run already
  disclosed one: gap_driven_3tier vs gap_driven_3tier_no_pull -- pre-existing, out of scope here)"
crlb_n/a: "symbolic KB-lookup + vote-count pipeline; no argmax/capacity-noise-floor discriminator applies"
baseline_in_band: n/a                    # not a baseline-vs-mechanism accuracy sweep; paired-arm comparison
discriminating_fraction: n/a             # not a swept-parameter cell (gate B does not apply)
cardinality_ok: "EXPECTED_N_CHECKPOINTS=5, EXPECTED_N_ARMS=10"
hp_scope:
  dev_checkpoint_eval: [tier_fire_drop, tier_comprehension_lift, tier_scramble_control,
    tier_consolidation_fidelity, combined_evidence_promotion, ablation_underperformance]
  with_mdl_gated_promotion: [mdl_gated_combined_evidence_promotion, mdl_tier_fidelity,
    mdl_comprehension_lift, mdl_gate_discriminator_fires]
calibration_check: "adaptive_with_discriminator_gate -- MDL_PURITY_THRESH=0.95 calibrated via
  the self-test's own diagnostic (in)compressible construction (see 'MANDATORY pre-check
  finding' above), logged, not hand-tuned against a real-corpus result"
real_code_path_exercised: [Library, consolidation_pass, HDFactStore, ScriptLibrary,
  build_instance_register, match_or_spawn, CharTrigramEncoder, "hdlab.learner.registry.learn(ruleind)"]
substrate_signature_checked: ["update_prelim_and_generalize(mdl_gate_fn=...)", "registry.learn"]
guard_baseline_validated: n/a            # not a control-beats-baseline break-guard cell
functional_requirements:
  - requirement: "does gating combined-evidence promotion to genuinely-compressible clusters
      restore fidelity (HP2) and coverage-controlled comprehension (HP3) that the ungated v2
      semantic-key fix did not achieve"
    primitive: "hdlab.learner.core.per_cluster_gate / mdl_select (MDL two-part code, Perfors &
      Tenenbaum 2009), wired conjunctively into update_prelim_and_generalize"
  - requirement: "is the combination LOGIC itself (pooling sub-threshold votes across a cluster)
      sound, independent of WHICH clusters are selected"
    primitive: "decisive_measurement: combined_acc_mdl vs cru_acc_mdl on the gated subset"
arms_must_differ: "with_mdl_gated_promotion vs gap_driven_3tier: expected to differ (mdl gate
  blocks >=1 cluster per self-test); if bit-identical at FULL, that IS informative (gate never
  fired at real scale) and is reported via arms_differ_non_exempt_collisions, not hidden"
```

## Compute architecture

Class (b) sequential-CPU (same as v2 -- symbolic KB-lookup + vote-count pipeline, not a
matmul-batchable primitive; the added `mdl_gate_fn` calls are small per-cluster `registry.learn`
fits, <=136 candidate rules over <=~50-trace pools, each a fast closed-form search). Storage
strategy: sharded (each pair its own `HDFactStore` entry; `mdl_state` is a THIRD parallel
sharded store, same shape as `real_state`/`scr_state`). Adds ONE more parallel TierState +
ONE more arm's dev-eval pass to v2's own 340-750s FULL wall time (v2's own landed FULL measured
`elapsed_s=742.58`); expect roughly proportional growth (~15-25% more work: 1 extra arm out of 9
existing = +11% eval, plus one extra `update_prelim_and_generalize` call per checkpoint = small
constant overhead) -- budget FULL timeout generously above the prior run's own 742s.

## Smoke plan

`--smoke` (existing contract: `SMOKE_TRAIN_CAP=15000`, `SMOKE_DEV_CAP=400`, FULL real 1.15M-edge
CSKG index -- discriminator-preview per DISCRIMINATOR-MUST-SURVIVE-SCALE option A, matching v2's
own smoke design) with `--out-tag arm2mdl` (writes to
`data/exp_crutch_fade_social_iqa_v2_semantic_cluster_key_smoke_arm2mdl/metrics.json`, preserving
the existing `..._smoke/metrics.json` history). Smoke-gate check (BEFORE any FULL dispatch):
`mdl_gate_ever_blocked` must be True at smoke scale (discriminator-fires, META_RULE_K) --if the
gate never blocks anything at smoke's own real-CSKG scale, STOP and re-diagnose (do not dispatch
FULL hoping it differs) per the DISCRIMINATOR-MUST-SURVIVE-SCALE + "smoke must fire the
discriminator" disciplines.

## Dispatch plan

FULL via `--out-tag arm2mdl` (writes to
`data/exp_crutch_fade_social_iqa_v2_semantic_cluster_key_arm2mdl/metrics.json`, preserving the
existing landed HARD_FAIL at the canonical v2 path). Route: `remote_cpu_queue` (CPU-only,
symbolic pipeline, no torch/CUDA -- routing-sanity gate in `queue_add.sh` would REJECT
`overnight_queue` for a no-torch script). Timeout: `ceil(1.5 * prior_FULL_wall_s * 1.25)` where
`prior_FULL_wall_s=742.58` (v2's own landed FULL elapsed_s, same checkpoint/dev/train scale,
+25% margin for the extra arm/state) = `ceil(1.5 * 742.58 * 1.25)` = 1392s -> rounded up with
additional safety margin to **2400s** (40 min) to absorb remote-CPU variance (v2's own smoke-vs-
FULL and prior remote-dispatch timeout conventions in this cell family use similarly generous
multipliers over measured wall time).
