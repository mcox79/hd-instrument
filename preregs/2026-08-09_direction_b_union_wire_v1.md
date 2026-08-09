# Pre-registration: exp_direction_b_union_wire_v1

**Filed by:** exp_dev, 2026-08-09. **Task source:** Director spawn prompt (Direction-B arc close-out:
"measure the exact UNION of the three OOV-recovery mechanisms and WIRE the combined channel into the
pipeline IFF net-positive"), citing all three prior validated-but-SHELVED sub-mechanisms:
`data/exp_direction_b_M1_idiom_grounding_recovery_v1/metrics.json` (MIDDLE_BAND, primary 2/8=0.25,
breadth 0/37), `data/exp_direction_b_M2_speechact_result_generalization_v1/metrics.json` (MIDDLE_BAND,
primary 3/8=0.375, breadth 9/37=0.2432), `data/exp_direction_b_A_goal_outcome_relation_v1/metrics.json`
(MIDDLE_BAND, primary 2/8=0.25, breadth 3/37=0.0811).

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "union OOV recovery channel combining idiom result-type relation
grounding goal achievement"` -> top hit cosine=0.3301 (`goal_achievement_three_channel_valence_
relation_contrast`, the base 3-channel module's own registry entry -- expected, since the union
extends that module), second hit cosine=0.3291 (the POST_COMPACTION_BACKUP note describing that same
base-module promotion). No hit above cosine=0.30 describing a prior attempt at combining M1+M2+fork-A
into one channel. **Verdict: genuinely novel cell -- this is the arc's own explicitly-flagged
close-out step, not a rediscovery.** (The most recent commit before this session, `1258f56dd`, is
fork-A's own synthesis explicitly recommending "wire M2+relation+dictionary additive channel for the
modest real gain" -- this cell is the direct, expected continuation of that recommendation.)

## What / why
Each of the three prior sub-mechanisms recovers a STRUCTURALLY DIFFERENT residual pattern on the
same abstain-to-majority DesireDB cohort:
- **M2 (`utility_channel_resulttype_grounded`)**: refusal/grant/block/achieve/fail speech-act
  constructions, learned + generalizing (held_out_acc=0.88). Best single mechanism (3/8 primary,
  9/37 breadth).
- **fork-A (`utility_channel_relation_grounded`)**: means-end instantiation (held_out_acc=1.0) +
  conventionalized-contradiction dictionary lookup (coverage=0.83). 2/8 primary, 3/37 breadth.
- **M1 (`utility_channel_idiom_grounded`)**: 29-entry hand-vetted idiom/colloquialism lexicon,
  non-compositional long-tail. 2/8 primary, 0/37 breadth.

Hypothesis: their UNION is net-additive over M2-alone. This cell (1) adds a NEW 4th-channel variant
`utility_channel_union_grounded` to `hdlab/goal_achievement.py` combining all three with an explicit,
auditable PRECEDENCE (never a blind additive merge -- same discipline M3-inc1's `combined_grounded`
established for M1+M2, extended 2-way -> 3-way), (2) measures it non-circularly on the identical
DesireDB cohort all four prior cells used, and (3) wires it into `goal_achievement_verdict` as a
strict-ADD, abstain-only fallback IFF the measured numbers clear the task's explicit CAN-FAIL gate.

## Mechanism: `utility_channel_union_grounded` (hdlab/goal_achievement.py)
**Precedence** (fixed, pre-declared BEFORE any DesireDB run -- calibration-honesty, not tuned per
item): within the per-attribute per-token-vote layer (`active` non-empty, the Stage-2/M1/M2/M3-inc1/
fork-A shared path), try **RESULTTYPE (M2) first** (best measured generalization + breadth) ->
**RELATION (fork-A) second** (means-end + dictionary contradiction, a different recovered-item class
than M2) -> **IDIOM (M1) last** (non-compositional long-tail fallback). Only the first source with
ANYTHING to say votes ("never both", the SAME discipline M3-inc1 established for the 2-way
resulttype/idiom case). When NO attribute activates at all (`active` empty), the union reuses
fork-A's own `RELATION_LINK` pseudo-attribute fallback VERBATIM (its own separately-seeded FHRR
codebook, `_relation_fallback_vecs`) -- M1/M2 have no equivalent no-active-attribute path, so this is
the one place the union's coverage is a strict superset of the parts, not just a precedence
extension of the shared layer. `_UNION_PRECEDENCE = ("resulttype", "relation", "idiom_fallback")`.

**Design-probe finding (MEASURED@this session, informs the precedence choice + self-test fixtures):**
the three sources genuinely overlap on SOME items -- e.g. `hdlab.goal_outcome_relation`'s own
`mwe_disengage_scan` ALSO catches "put the kabash on" (via `_KIBOSH_RE`), the same DesireDB idiom
`hdlab/idiom_grounding.py`'s `IDIOM_LEXICON` independently authored an entry for -- so a clean
idiom-ONLY self-test fixture required verifying (empirically, before hard-coding) that resulttype
AND relation both genuinely abstain on the chosen case ("piece of cake" / "came together") before
idiom gets the fallback vote. This overlap is reported honestly, not hidden: it means the union's
gain over the best single mechanism, while real (see Results), is not simple arithmetic addition of
each mechanism's OWN standalone count -- it is closer to (and, per the per-item attribution below,
turns out to be EXACTLY) the SET UNION of what each recovers.

## Self-test (hdlab.goal_achievement.self_test_union_grounded_channel, real_code_path)
Five hand-authored, MEASURED@this-session-verified flagship cases exercising every code path:
(1) resulttype precedence ("Uh. No." -- ALSO matches idiom's own pattern, proving precedence not
just standalone firing), (2) relation precedence (2nd in line -- resulttype genuinely abstains;
`goal_activity_engagement`('busy') x `outcome_errand_activity`('shopping') fires INSTANTIATES), (3)
idiom fallback (3rd/last -- both resulttype AND relation genuinely abstain), (4) RELATION_LINK
fallback, means-end sub-case (fork-A's own flagship, activation empty), (5) RELATION_LINK fallback,
contradiction sub-case (fork-A's own flagship). Plus FHRR round-trip fidelity (all 5 cases),
pairscramble (cases 2 and 4, spanning both branches), determinism. **MEASURED: all 5 cases pass;
plain WordNet-only channel abstains on cases 1-3.**

## Cohort + measurement design (GATE-2, reusing the identical loader/cohort verbatim)
`import exp_utility_satisfaction_channel_v1 as _s2` (no duplication) -- PRIMARY cohort (n=160 draw,
`FULL_N_PER_CLASS=80`, `SEED=20260808` -> cohort n=22, 8 gold-Unfulfilled, the EXACT draw M1/M2/
M3-inc1/fork-A all used) + BREADTH context cohort (`ENLARGED_N_ROWS=900`, `ENLARGED_SEED=20260809` ->
cohort n=152, 37 gold-Unfulfilled, the EXACT denominator M1/M2/fork-A measured 0/37, 9/37, 3/37 on).

### Arms (PRIMARY cohort)
- **(i) majority-only baseline**, **(ii) utility_channel** (Stage-2 WordNet-only) -- unchanged
  references.
- **(iii) M2 alone**, **(iv) M1 alone** (`use_conceptnet_bridge=False`, matching what the union's own
  idiom_fallback path uses internally), **(v) fork-A relation alone** -- RE-MEASURED FRESH this run
  (not just cited) for a true apples-to-apples "union vs each part" comparison in the SAME run.
- **(vi) UNION** (`utility_channel_union_grounded`) -- THE GATE-DEFINING ARM.
- **(vii) UNION, SCRAMBLED goal cue** -- mandatory pairscramble control (`_s2._scrambled_desires`,
  deterministic derangement, PROT-023 compliant).

### Full-bench composition (base-alone vs union-wired, the task's explicit gate)
`composed_verdict_base` = `goal_achievement_verdict` alone (the CURRENT shipped pipeline, no 4th
channel). `full_bench_comparison(n_per_class, hyps)` computes `goal_achievement_verdict` ONCE per
item (not the naive twice a separate base/union pair of calls would cost) and applies the union ONLY
when that call's own `channel == 'majority'` -- exactly the wiring this cell then applies for real.
Computed at **n=160** (the task's explicit WIRE-gate comparison scale) AND **n=80** (matches
`harness_validity_check`'s own documented-baseline scale, for a same-scale cross-check).

### `harness_validity_check` (reproduces the documented 0.686/0.699 pair)
Identical function to Stage-2/M1/M2/M3-inc1/fork-A's own copy: n=80 (`VALIDITY_N_PER_CLASS=40`),
`SEED=20260808`, compares the PRE-wire `goal_achievement_verdict`'s measured macro-F1 against the
documented constant 0.686 (tolerance 0.03). Stage-2's own prior landed run measured 0.6992 at this
exact draw -- the "0.686/0.699" pair the task's contract cites.

## CAN-FAIL WIRE GATE (verbatim from the task contract -- not exp_dev's to loosen)
- **WIRE iff:** (a) union full-bench macro-F1 >= base (net-positive, no regression, checked at BOTH
  n=160 and n=80) AND (b) union PRIMARY abstain-recovery > M2-alone PRIMARY abstain-recovery
  (genuinely additive) AND (c) pairscramble collapses (PRIMARY: `|scr-i|<=0.05`; BREADTH-at-scale:
  `collapses_at_scale`) AND does not leak (`|scr-mech|>0.03`).
- **HARD_FAIL** (overrides WIRE regardless of (a)/(b)): pairscramble leaks OR does not collapse
  (either scale), OR union full-bench macro-F1 falls below the Stage-2-precedent floor 0.620 at n=160.
- **MIDDLE_BAND:** clears HARD_FAIL but fails to meet the full WIRE conjunction (e.g. flat/tied
  full-bench, or recovery not STRICTLY greater than M2-alone).
- **INVALID:** `harness_validity_check` fails, cohort underpowered (`n<15`), or recovery undefined
  (0 gold-Unfulfilled).
- If WIRE earned: wire the union channel into `goal_achievement_verdict` as the strict-ADD,
  abstain-only fallback (fires ONLY when `channel=='majority'`); add a scaffold-free verification
  witness (`tracing=False`); update the capability registry (flip the 3 SHELVE entries + register the
  new WIRED union entry + retroactively register fork-A's own previously-unregistered module).
- If NOT net-positive: do NOT wire; report the honest negative; keep SHELVE.

## Wiring design (goal_achievement_verdict, OPT-IN FLAG, default flipped ON because WIRE_DECISION=True)
**Design corrected mid-task on explicit coordinator instruction (flagged per the task's "flag any
change" mandate).** The FIRST wiring attempt (commit 0946a741b) modified `goal_achievement_verdict`'s
default path directly (union fires whenever `channel=='majority'`). The coordinator correctly flagged
this as NOT strict-ADD: it changed the certified module's DEFAULT output, which is exactly why a fresh
`harness_validity_check` reading the default `verdict` could no longer reproduce the documented 0.686
(it was measuring the already-wired pipeline). A trace-reconstruction patch (commit 44310928d) papered
over this for the cell's own comparisons but left the default certified path modified on an
insufficiently-clean basis.

**Corrected design (the shipped one):** the union is an OPT-IN behind a flag.
`goal_achievement_verdict(desire, outcome, use_union_oov=None)`:
- `use_union_oov=False` -> BYTE-IDENTICAL to the pre-union 3-channel certified pipeline (no `union_*`
  trace fields, verdict/channel unchanged). `harness_validity_check` calls with `False`, so it
  reproduces 0.686 (measured 0.6992, delta +0.0132, VALID) REGARDLESS of the module default.
- `use_union_oov=True` -> tries the union fallback ONLY when the base pipeline's `channel=='majority'`
  (relation AND valence both abstained; contrast-override guaranteed inapplicable there). `channel`
  is DELIBERATELY LEFT AS `'majority'` even when the union fires, so cohort-definition code filtering
  on `channel=='majority'` (`exp_utility_satisfaction_channel_v1.build_cohort`, reused by every
  Direction-B cell) keeps selecting the IDENTICAL cohort -- only `verdict` improves. The union's
  contribution is in NEW additive trace fields (`union_oov_recovery_fired`, `union_verdict`), present
  ONLY when the union path ran.
- `use_union_oov=None` -> uses the module `_UNION_OOV_DEFAULT`. This was held **False** through the
  entire confirmation `--full` run (so the base arm demonstrably reproduced 0.686 on a VALID harness
  with the union measured as a clean opt-in arm), and flipped to **True** (WIRED) ONLY AFTER that run
  reported `wire_decision=True`.

This makes the wire a genuine strict-ADD: the certified base output is always recoverable byte-for-byte
via `use_union_oov=False`, the union's effect is always a clean two-arm (OFF vs ON) comparison on the
same split, and `harness_validity` stays VALID no matter the default. Consumers that want the
pre-union behavior pass `use_union_oov=False`; the production default (`None`) now uses the union.

## Compute architecture
(b) sequential-CPU with justification: two `registry.learn` fits (M2's + fork-A's, both already
fit + cached by `get_induced_hypothesis()`, reused unchanged -- NOT re-litigated by this cell's own
GATE-1) + WordNet lookups (pool_related + MWE scan) + a 29-entry idiom-phrase regex scan + FHRR
bind/bundle/unbind over N=2048 complex64 (unchanged from Stage-2/M1/M2/M3-inc1/fork-A). MEASURED
this session: `--self-test` = 1.99s; `--smoke` (PRIMARY only, 7 arms) = 56.0s; `--full` (PRIMARY 7
arms + harness_validity_check + full_bench_comparison x2 [n=80, n=160] + BREADTH 900-row cohort-build
+ per-item attribution on the 37 gold-Unfulfilled breadth items + pairscramble-at-scale over the
152-item breadth cohort) = 526.6s (~8.8 min), run FOREGROUND-TO-COMPLETION per the INLINE-LOCAL
mandate (LOCAL, no remote authorized, no queue dispatch -- matches this arc's own established
precedent of every prior Direction-B cell running the same way). No matmul-heavy batchable primitive
at this scale. Storage: no_storage/no_composition.

## Cell-template mandatory fields
- `cell_chunked`: false (single-process). `start_marker_written` / `crash_diagnostic_present` /
  `heartbeat_present`: true. `final_metrics_atomicity`: `tmp_replace`.
- `arms_differ_verified`: true (hash-check on all 7 PRIMARY-cohort prediction-vector arms, smoke +
  full -- MEASURED true both runs).
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`) --
  grep-verified clean.
- `crlb_n/a`: "deterministic construction-cue-vote learners (M2 resulttype + fork-A relation,
  estimation/ruleind over fixed boolean feature spaces) + WordNet-MWE dictionary lookup (fork-A
  disengagement) + hand-authored idiom-phrase regex (M1) + FHRR bind/bundle/cleanup over a fixed
  6-role x 3-filler codebook PLUS the separately-seeded 1-role RELATION_LINK fallback codebook --
  identical justification to Stage-2/M1/M2/M3-inc1/fork-A's crlb_n/a, unchanged FHRR mechanism layer."
- `HP_SCOPE`: `{arm_vi_union: [primary_recovery_strictly_gt_m2, fullbench_no_regression_n80_and_n160,
  pairscramble_collapse_primary, pairscramble_collapse_breadth]}` -- arms i/ii/iii/iv/v/vii are
  comparators/controls, not independently gated.
- `cardinality_ok`: `EXPECTED_N_UNITS = 7` (one unit per PRIMARY-cohort arm: i, ii, iii_m2, iv_m1,
  v_relation, vi_union, vii_union_scr).
- `deterministic_seeding`: true (all seeds `random.Random`-based fixed integers, `sorted(set())`
  base ordering for the breadth subsample, derangement offset `n//2` not `hash()`-derived --
  grep-verified no `hash()`-derived seeding anywhere in this cell).
- `calibration_check`: `default_ok_for_this_regime` -- all 3 sub-mechanisms + their precedence were
  independently calibrated/validated in their OWN prior cells; this cell reuses their fitted
  hypotheses (`get_induced_hypothesis()`, cached) UNCHANGED, and only newly calibrates the 3-way
  PRECEDENCE ORDER itself, which was fixed BEFORE any DesireDB run (see "Mechanism" section above)
  from the parts' OWN prior standalone measurements (best-generalizing/best-breadth first), not
  tuned against this cell's own GATE-2 numbers.
- `functional_requirements`: "combine 3 structurally-different OOV-recovery mechanisms with an
  auditable, non-arbitrary precedence, without double-counting or losing coverage either has alone"
  -> `_attribute_outcome_state_union_grounded` (3-way precedence) + `utility_channel_trace_union_
  grounded` (RELATION_LINK fallback superset); "measure genuine additivity vs the best single
  mechanism, non-circularly, on the identical cohort" -> per-sub-mechanism re-measurement (arms
  iii/iv/v) + per-item attribution; "wire IFF net-positive, with zero risk to existing cohort
  definitions" -> the opt-in-flag, `channel`-preserving wiring design above (base recoverable
  byte-identically via `use_union_oov=False`).
- `real_code_path_exercised`: `[activate_attributes, result_type_votes, relation_votes, idiom_votes,
  dedupe_repeated_sentences, goal_atoms, bind, unbind, bundle, utility_channel_trace_union_grounded,
  goal_achievement_verdict]` -- `--self-test` constructs the REAL construction-cue extraction + REAL
  `registry.learn` fits (both modules) + REAL WordNet-MWE scan + REAL idiom-phrase regex + the REAL
  FHRR primitives (both the shared `_utility_vecs()` codebook AND the separately-seeded RELATION_LINK
  fallback codebook) + the REAL wired `goal_achievement_verdict` on real-DesireDB-flavored flagship
  cases, not a synthetic-only branch.
- `progress_logging`: `print_flush_true` (elapsed 526.6s > the 30-min §17 mandate threshold is not
  reached, but this cell prints `[full]`/`[smoke]` progress lines with `flush=True` throughout
  regardless, for auditability parity with M2/fork-A's own convention).

## Autonomy notes (exp_dev-owned, per the task's contract)
The sub-mechanism precedence/combination logic (RESULTTYPE -> RELATION -> IDIOM_FALLBACK, plus the
RELATION_LINK no-active-attribute superset), cell/file naming, seeds, and the verification-witness
design are all exp_dev's own choices, documented above. The strict-ADD (abstain-only, no-regression)
requirement, the mandatory pairscramble control, the anti-circular measurement (reusing the fitted
hypotheses unchanged, never re-fitting against DesireDB), and the WIRE-only-if-net-positive gate were
NOT exp_dev's to loosen and were not altered. **The exact wire-in mechanism was corrected mid-task on
explicit coordinator instruction** (from a default-path modification to an opt-in flag whose default
was flipped ON only after the gate was confirmed on a VALID harness) -- flagged per the task's "flag
any change" mandate; this STRENGTHENED the strict-ADD guarantee (the earlier default-path edit was not
truly strict-ADD), it did not loosen any gate.

## Results (MEASURED, `--full` landed)
See `data/exp_direction_b_union_wire_v1/metrics.json` for the complete record. Summary:

- **PRIMARY recovery (n=22 cohort, 8 gold-Unfulfilled):** union **5/8=0.625** vs M2-alone 3/8=0.375,
  M1-alone 2/8=0.25, relation-alone 2/8=0.25 (all three RE-MEASURED fresh this run, reproducing the
  prior cells' own landed numbers exactly). **Genuinely additive: TRUE** (0.625 > 0.375). Per-item
  attribution shows the union recovers EXACTLY the set-union of what the 3 parts recover individually
  (5 items total, `n_recovered_by_ANY_single_mechanism == n_recovered_by_union == 5`) -- no
  interference/precedence losses, no super-additive surprises beyond the parts' own union.
- **BREADTH context (900-row draw, cohort n=152, 37 gold-Unfulfilled):** union **10/37=0.2703** vs
  M2-alone 9/37=0.2432 (re-measured, matches the cited reference exactly), M1-alone 0/37, relation-
  alone 3/37. `union_beats_max_single = True`. Again exactly the set-union of the 3 parts (no items
  recovered by union alone that no single mechanism also recovers).
- **Full-bench composed macro-F1 (base-alone vs union-wired), NO REGRESSION at BOTH scales:**
  n=160: 0.6623 -> 0.6875 (**+0.0252**). n=80: 0.6992 -> 0.7248 (**+0.0256**).
- **`harness_validity_check`** (base arm, `use_union_oov=False`, n=80): measured_macro_f1=0.6992,
  documented=0.686, delta=+0.0132, **valid=True** (within 0.03 tolerance) -- the "0.686/0.699" pair
  reproduced exactly ON A VALID HARNESS, confirming the base arm is byte-identical to the pre-union
  pipeline and the +0.025 union gain is a true base-vs-union delta, not a wired-vs-wired artifact.
- **Pairscramble:** PRIMARY `|scr-i|=0.0000` (collapses cleanly), `|scr-mech|=0.1818` (>0.03,
  not-leak). BREADTH-at-scale: delta=0.0461 (<=0.05, collapses).
- **`wire_decision`: TRUE. `verdict`: HARD_PASS.** All CAN-FAIL WIRE GATE conditions cleared, on a
  VALID harness, with the confirmation run's module default held at `_UNION_OOV_DEFAULT=False`.

**Action taken:** wired `utility_channel_union_grounded` into `hdlab.goal_achievement.
goal_achievement_verdict` as an OPT-IN, strict-ADD, abstain-only fallback behind `use_union_oov`
(module default `_UNION_OOV_DEFAULT` flipped False->True ONLY after the confirmation run above passed
the gate; `use_union_oov=False` remains byte-identical to the pre-union certified pipeline forever).
Added `verification/test_direction_b_union_wire.py` (scaffold-free, tracing=False, 9/9 pytest checks
green including the pre-existing `test_goal_achievement.py`; asserts the flag's byte-identity/strict-ADD
invariant both ways). Full verification suite: 220 passed, 3 skipped (no regression; the 4 excluded
modules are pre-existing missing-dependency skips: hypothesis, duckdb). Updated
`data/capability_registry.jsonl`: flipped `result_type_induction_learned_speechact_classifier`,
`idiom_grounding_lexicon`, and `utility_channel_grounded_architecture` from SHELVE to WIRE (via the
union), added `direction_b_union_oov_recovery_channel` (the new WIRED entry, gate_decision=WIRE,
pipeline_status=WIRED_AND_PIPELINE_USED), and retroactively registered `hdlab/goal_outcome_relation.py`
(fork-A's own module, which had never been separately registered -- a gap fixed as part of this wire).
