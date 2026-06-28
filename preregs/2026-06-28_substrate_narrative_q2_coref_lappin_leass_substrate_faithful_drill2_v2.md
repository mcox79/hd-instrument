# Pre-reg: substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2

Author: exp_dev (Opus 4.7 1M ctx) 2026-06-28
Trigger: Skunkworks invalidation `f60880f7` of drill 2 v1 (oracle leak); VALID drill 2 required for USER 2x-drill-before-capability-closure rule

## Why-now

Drill 2 v1 (`substrate_narrative_q2_coref_lappin_leass_drill2_v1`) was INVALIDATED by Skunkworks landed-VET commit `f60880f7`:

- Reported "HARD_PASS" (2 seeds 7+13) + MIDDLE_BAND (seed 19), Lappin-Leass Q2 = 0.875 / 0.875 / 0.750.
- Skunkworks's independent feature-ablation recompute via .venv python showed:
  - `only_focus` ablation (W_FOCUS * f_focus only, other features zeroed) = **1.000 across all 3 seeds** = PERFECT
  - `no_focus` ablation (other 4 features; f_focus zeroed) = 0.500 / 0.500 / 0.250 = WORSE than random
  - full Lappin-Leass = 0.875 / 0.875 / 0.750 = BELOW only_focus ablation (the other 4 features inject noise into a perfect oracle lookup)
- Root cause:
  - `_build_mention_history(narr)` reads `narr.events[*]["char_id"]` directly — gives perfect map of which character is in which event (substrate's job, bypassed)
  - `_feature_focus(c, scene_id, narr)` reads `narr.scene_focus[scene_id]` directly
  - Narrative-gen line 396: `ev["char_id"] = scene_focus[scene_id]` for ALL pronoun events — so `scene_focus` lookup IS the Q2 ground-truth answer
  - Cell verdict-logic at line 1015-1022 EXEMPTED this collision from META_RULE_AF check (bias-justification, not bias-prevention)
- Disposition (Skunkworks): drill 2 v1 does NOT satisfy USER 2x-drill rule. Q2 capability remains OPEN with 1 of 2 VALID drills landed.

**This pre-reg authors a VALID drill 2 — substrate-faithful Lappin-Leass.**

## Mechanism class orthogonality argument (vs drill 1)

- **Drill 1 (HRR sequence-recency, HARD_FAIL today, Q2=0.125):** readout = `argmax_c < cosine(per-char position-indexed bank, query_position) >`. The mechanism IS associative-recall — substrate stores patterns; query retrieves nearest pattern; cosine ranks candidates.
- **Drill 2 v2 (substrate-faithful Lappin-Leass):** readout = `argmax_c sum_i W_i * f_i(c)` where each `f_i` derives its scalar value from a substrate cosine query (`||W_part[c] @ probe||` or `cosine(W_cortex @ probe, chars_cortex[c])`). The mechanism is a SYMBOLIC weighted-sum scorer over substrate-extracted features; the substrate provides FEATURE INPUTS, not the argmax via similarity matching.

Brain-grounded reference: Lappin & Leass (1994) Comp Linguistics 20(4):535-561 — canonical symbolic-algorithmic Centering Theory pronoun-resolution; orthogonal to the connectionist associative-recall family in drill 1.

## v2 fixes vs v1 (Skunkworks audit defenses)

1. **ORACLE_LEAK_GUARD at module load** (NEW in v2):
   - Cell startup runs `_oracle_leak_guard()` which greps its own source for forbidden regex patterns (`narr\.scene_focus`, `narr\.events[*]["char_id"]`, etc.) in the bodies of the substrate-faithful function set:
     - `_feature_recency_substrate`, `_feature_scene_substrate`, `_feature_subject_substrate`, `_feature_focus_substrate`, `_feature_parallel_substrate`
     - `q2_lappin_leass_full_substrate_faithful`, `q2_recency_only_substrate_faithful`
   - If ANY violation found in these function bodies, cell raises RuntimeError and refuses to run.
   - (Allowed in non-substrate-faithful arms: ARM_NAIVE_MAGNITUDE reproduces drill-1 baseline using `narr.events[ev_idx]`; ARM_ORACLE uses `q["expected_char_id"]`; corpus generator reads `narr.events` to BUILD the narrative.)

2. **Substrate-faithful feature extractors** (rewritten from v1):
   - `_feature_recency_substrate(c, ev_idx, vocab, W_part)`: probes `W_part[c]` at position-only keys for offsets {1..20} back from pronoun; sums `exp(-lambda*d) * ||W_part[c] @ probe||`. Position-key = `sign(scene_v + pronoun_tag)` projected through input pipeline — NO char_id leaked.
   - `_feature_scene_substrate(c, ev_idx, vocab, W_part)`: probes `W_part[c]` with aggregated scene-key for the pronoun's scene window (positions before pronoun). Response = whether c was in scene.
   - `_feature_subject_substrate(c, ev_idx, vocab, W_part)`: probes `W_part[c]` with aggregated even-verb-id role key (substrate's canonical subject-role aggregator). Response = how often c was bound with subject-role verbs.
   - `_feature_focus_substrate(c, ev_idx, vocab, W_cortex, pronoun_encoded_h)`: queries `W_cortex` with pronoun event's encoded H-key; readout via `cosine(W_cortex @ probe, chars_cortex[c])`. Substrate's OWN readout of what character "belongs" with this scene/event context. NOT a direct `narr.scene_focus[s]` read.
   - `_feature_parallel_substrate(c, ev_idx, vocab, W_part, pronoun_encoded_raw)`: probes `W_part[c]` with the pronoun event's role-residual (encoded raw minus scene + pronoun_tag components). Response = whether c was associated with this verb-role.

3. **Corpus diversification — `NON_FOCUS_PRONOUN_FRAC` parameter** (NEW in v2):
   - Pronoun events choose ground-truth target as:
     - With prob `1 - NON_FOCUS_PRONOUN_FRAC`: scene_focus[scene_id] (v1 default)
     - With prob `NON_FOCUS_PRONOUN_FRAC`: random non-focus character who appeared earlier in same scene
   - Smoke + full default = **0.3** (the discriminating regime: scene-focus argmax can only get ~0.7 floor; mechanism must do better)
   - Sweepable via `--non-focus-frac` flag or `HDLAB_NON_FOCUS_FRAC` env var

4. **Operational baseline change** (NEW in v2):
   - v1 used `NAIVE_MAGNITUDE` as the operational baseline (because `SCENE_FOCUS_ONLY` was oracle-class by construction)
   - v2 uses `max(NAIVE_MAGNITUDE, COSINE_ONLY)` — both are substrate-faithful 1-feature baselines
   - `ARM_COSINE_ONLY` = pure `q2_cosine_only` readout (substrate's W_cortex top-1 cosine over chars_cortex; substrate-faithful)
   - Mechanism must beat the STRONGER of the two 1-feature baselines by >= 0.15

5. **META_RULE_AF strengthened**:
   - HARD_FAIL if `lappin_q2_pred_sha == naive_q2_pred_sha` (mechanism collapses to naive)
   - HARD_FAIL if `lappin_q2_pred_sha == cosine_only_q2_pred_sha` (mechanism collapses to pure cosine = W_FOCUS dominating)
   - This catches the v1 failure mode where mechanism was just "noised f_focus" in disguise

## Chain-grade primitives feeding features (substrate-faithful)

| Substrate primitive | Source | Used as |
|---|---|---|
| W_part[c] (per-char partition store) | hebbian-written during encoding pass | cosine-query target for f_recency, f_scene, f_subject, f_parallel |
| W_cortex (consolidated cortex store) | scene-boundary-replayed cortex writes | cosine-query target for f_focus |
| vocab["scenes"][s] | canonical scene bipolar vector | building scene-key probes |
| vocab["chars_cortex"][c] | canonical character cortex vector | readout target for f_focus cosine |
| vocab["verbs"][even_idx] | canonical role vectors | building subject-role probe |
| pronoun event raw encoded vector | encoded with pronoun_tag (NOT true char_v) | role-residual probe for f_parallel |

## Functional-requirement decomposition (§15 Gate E)

| FR | Spec | Substrate primitive (feature source) | Mechanism (readout) |
|---|---|---|---|
| FR1 | Track each character's mention positions | W_part[c] cosine-query at position-only probes | f_recency via decay-weighted sum |
| FR2 | Identify which chars appeared in current scene | W_part[c] cosine-query at scene-aggregated probe | f_scene via sum of response magnitudes |
| FR3 | Detect subject-role frequency per candidate | W_part[c] cosine-query at canonical subject-role key | f_subject via response magnitude |
| FR4 | Identify scene-focus (substrate's OWN guess) | W_cortex cosine-query at pronoun event probe; readout via chars_cortex | f_focus via cosine(W_cortex @ probe, chars_cortex[c]) |
| FR5 | Detect parallelism with pronoun's verb | W_part[c] cosine-query at pronoun's role-residual key | f_parallel via response magnitude |
| FR-READOUT | Rank candidates and select argmax | (NOT substrate — symbolic weighted sum) | `argmax_c sum_i W_i * normalized(f_i(c))` |

Each FR step maps to a substrate cosine query — NOT a `narr.events[*]` dict read. The cell HARD_FAILs at module-load time if the source-grep detects any violation in these function bodies.

## §15 Gate compliance

- **Gate A (effective vs nominal param):** N/A. Single-regime cell (single non_focus_frac per dispatch); does NOT sweep parameters within a cell. `sweep_alignment_verdict: N/A`. Multi-regime achieved by separate dispatch with different `--non-focus-frac` if needed.
- **Gate B (discriminating bracket):** ARM-level (6 arms span floor → 2 substrate-faithful 1-feature baselines → recency-only → lappin-leass → oracle). The discriminator FIRES when `lappin_q2 > max(naive_q2, cosine_only_q2)` by >= 0.15 at NON_FOCUS_FRAC=0.3.
- **Gate C (signal-shape audit / META_RULE_AP_v3):** Every feature extractor calls substrate (cosine query against W_part or W_cortex); NO dict reads. Module-load `_oracle_leak_guard()` enforces this by source-grep. Smoke gate VERIFIES guard accepts.
- **Gate D (positive control reproduces prior CG):** ARM_NAIVE_MAGNITUDE positive control = drill 1's measured naive baseline 0.625; tolerance +/- 0.20 (smoke band 0.425 - 0.825). NOTE: at NON_FOCUS_FRAC=0.3, naive baseline expected to drop to ~0.65 * 0.7 + 0.20 * 0.3 = ~0.515 (theoretical) because pronouns target non-focus chars 30% of time. Cited prior atom: drill 1 ARM_NAIVE_MAGNITUDE Q2 = 0.625 MEASURED@`data/exp_substrate_narrative_q2_recency_sequence_log_v1_smoke/metrics.json`.
- **Gate E (functional-requirement decomposition):** filled above.

## §13 Defensive error checking (MANDATORY)

- `cell_chunked: True` (single-seed-per-cell via HDLAB_SEED env var; 3 sibling shims for seeds 7/13/19)
- `start_marker_written: True` (atomic tmp+os.replace at main() entry)
- `crash_diagnostic_present: True` (CELL_CRASHED metrics.json sentinel via outer-try `except Exception`; SystemExit/KeyboardInterrupt preserved per §8)
- `heartbeat_present: True` (per-arm heartbeat write inside main loop; atomic)
- `defensive_error_checking: "passed_all_4_patterns"`

## Arms (6) — ALL DISTINCT CODE PATHS (META_RULE_AF)

1. **ARM_RANDOM_FLOOR** — uniform random over N_CHARACTERS (floor ~0.20 = 1/5)
2. **ARM_NAIVE_MAGNITUDE** — drill-1's failing readout reproduced (per-char W_part magnitude argmax); positive control
3. **ARM_COSINE_ONLY** — substrate-faithful 1-feature baseline = pure `q2_cosine_only` (f_focus alone as argmax)
4. **ARM_RECENCY_ONLY_SUBSTRATE** — substrate-faithful 1-feature baseline = pure `f_recency_substrate` as argmax
5. **ARM_LAPPIN_LEASS_FULL_SUBSTRATE** — THE MECHANISM: 5-feature symbolic weighted-salience scorer with substrate-extracted features; argmax
6. **ARM_ORACLE** — ground-truth `expected_char_id`; pins ceiling 1.000

## Regime (smoke-or-full, single-seed-per-cell)

```
N_HIPPO          = 512    (same as drill 1)
N_CORTEX         = 1024
N_PART           = 1024
N_RAW            = 64
N_EVENTS         = 100
N_CHARACTERS     = 5
K_SCENE_BOUNDARY = 10
N_PRONOUN_EVENTS = 8
Q_PER_TYPE       = 8
N_FACTS_PER_CHAR = 3
N_UPDATE_PAIRS   = 3
K_HIPPO_ACTIVE   = 51     (10% of 512)
ETA_CORTEX       = 0.005
N_REPLAY_CYCLES  = 3
NON_FOCUS_PRONOUN_FRAC = 0.3  (smoke + full default; sweepable to 0.0, 0.6)
RECENCY_LOOKBACK = 20
SUBJECT_LOOKBACK = 5
SEEDS_SMOKE      = [7]
SEEDS_FULL       = chunked: seed_7 | seed_13 | seed_19 (3 sibling cells)
```

## Pre-registered bands (LOCKED at module init; PRE-SMOKE)

### HARD_PASS (drill 2 v2 PASS = capability box DOES NOT close)
- `ARM_LAPPIN_LEASS_FULL_SUBSTRATE` Q2 >= 0.80 AND
- `lift_over_baseline` >= 0.15 where `baseline = max(NAIVE_MAGNITUDE, COSINE_ONLY)` AND
- `ARM_ORACLE` Q2 = 1.000 (sanity) AND
- `arms_distinct` >= 4 distinct Q2 pred_sha across 6 arms AND
- `cardinality_ok` = True

### HARD_FAIL (drill 2 v2 FAIL = combined with drill 1 HARD_FAIL → capability box CLOSES)
- `ARM_LAPPIN_LEASS_FULL_SUBSTRATE` Q2 <= 0.50 (below stronger 1-feature baseline at any NF frac) OR
- `lift_over_baseline` <= 0.00 (mechanism adds no information beyond strongest 1-feature substrate baseline) OR
- `ARM_LAPPIN_LEASS_FULL_SUBSTRATE` q2_pred_sha == `ARM_NAIVE_MAGNITUDE` q2_pred_sha (META_RULE_AF — collapses to naive) OR
- `ARM_LAPPIN_LEASS_FULL_SUBSTRATE` q2_pred_sha == `ARM_COSINE_ONLY` q2_pred_sha (META_RULE_AF — collapses to pure cosine = W_FOCUS dominating) OR
- `ARM_ORACLE` Q2 < 1.000 (sanity broken) OR
- `ORACLE_LEAK_GUARD` triggered at module load (forbidden token in substrate-faithful function body)

### MIDDLE_BAND
- `ARM_LAPPIN_LEASS_FULL_SUBSTRATE` Q2 in (0.50, 0.80); symbolic scorer partial. NOT sufficient for capability closure (would need BOTH drills HARD_FAIL); MB result keeps capability box OPEN pending iteration.

## Band-calibration rationale (META_RULE_L strict-above-floor)

At NON_FOCUS_PRONOUN_FRAC=0.3 with 8 Q2 questions:
- Random floor = 0.20 (1/5 chars)
- Scene-focus argmax (oracle-on-corpus-by-construction in v1; substrate-faithful proxy via cosine-only here): expected ~0.7 * (focus-recovery-rate from W_cortex)
- If W_cortex perfectly recovers scene_focus from pronoun event probe: ~0.7 * 1.0 + 0.3 * 0.20 = ~0.560
- If W_cortex partially recovers: lower
- Oracle ceiling = 1.000

HF_LAPPIN_LEASS_Q2_MAX = 0.50 is BELOW the theoretical scene-focus-recovery baseline — mechanism that scores below pure cosine is inert.
HP_LAPPIN_LEASS_Q2_MIN = 0.80 requires mechanism to recover non-focus pronouns substantially (~0.7 * 0.95 + 0.3 * 0.50 = ~0.815 means mechanism gets ~50% of non-focus pronouns correct, vs ~20% random).
HP_LIFT = 0.15 corresponds to >= 1.2 additional Q2 correct at Q=8.
Strict-above-floor: HP_MIN - HF_MAX = 0.30; HP target 0.80 well above HF_MAX + 0.05 * 0.30 = 0.515.

## Capacity-feasibility / discriminator-survives-scale

- Lappin-Leass scorer is closed-form 5-feature linear sum over substrate cosine queries; no CRLB-applicable noise floor.
- Discriminator reachability: at Q_per_type=8, sigma = sqrt(0.5 * 0.5 / 8) = 0.177; HP=0.80 vs baseline 0.55 = +0.25 = 1.4 sigma. Reachable.
- **Discriminator-survives-scale check (USER 2026-06-26 rule):** smoke at full-N (N_HIPPO=512, N_CORTEX=1024, N_PART=1024, N_EVENTS=100) matches full-run regime — no scale extrapolation. Discriminator behavior at smoke = discriminator behavior at full.

## ORACLE_LEAK_GUARD (mandatory; self-asserted at module load)

```python
def _oracle_leak_guard() -> None:
    src = open(__file__).read()
    forbidden_patterns = [
        (r"narr\s*\.\s*scene_focus"),
        (r"narr\s*\.\s*events\s*\[[^\]]+\]\s*\[\s*[\"']char_id[\"']"),
        (r"narr\s*\.\s*events\s*\[[^\]]+\]\s*\[\s*[\"']scene_id[\"']"),
        (r"narr\s*\.\s*events\s*\[[^\]]+\]\s*\[\s*[\"']role_tag_idx[\"']"),
        (r"narr\s*\.\s*events\s*\[[^\]]+\]\s*\[\s*[\"']is_subject_role[\"']"),
    ]
    SUBSTRATE_FAITHFUL_FUNCS = [
        "_feature_recency_substrate", "_feature_scene_substrate",
        "_feature_subject_substrate", "_feature_focus_substrate",
        "_feature_parallel_substrate",
        "q2_lappin_leass_full_substrate_faithful",
        "q2_recency_only_substrate_faithful",
    ]
    # Walk source; track current function scope; for each line in a
    # substrate-faithful function, fail if pattern matches.
    # Allowed in: ARM_NAIVE_MAGNITUDE / ARM_ORACLE / corpus generator
    # because those reproduce the prior naive baseline OR are the
    # ground-truth oracle OR build the narrative.
```

Cell hard-fails RuntimeError at module load if violation found.

## EXPECTED_N_UNITS (CARDINALITY_OK)

- Per chunk: `EXPECTED_N_UNITS = 1 * 6 = 6` units (1 seed x 6 arms)
- Full aggregated across 3 chunks: 18 units total

If `observed_n_units != expected_n_units` → HARD_FAIL_CARDINALITY_BREACH per META_RULE_H.

## Per-arm primitive API binding (META_RULE_AF defense)

| Arm | Q2 readout function | substrate-faithful? |
|---|---|---|
| RANDOM | `_rng.integers(0, N_CHARACTERS)` | N/A (floor) |
| NAIVE | `argmax_c \|\|W_part[c] @ cue_pc\|\|` (cue from full ev encoding incl true char) | partial (uses narr.events[ev_idx] for cue building; positive control) |
| COSINE_ONLY | `argmax_c cosine(W_cortex @ pronoun_probe_c, chars_cortex[c])` | YES (substrate-faithful 1-feature baseline) |
| RECENCY_ONLY | `argmax_c f_recency_substrate(c)` | YES (substrate-faithful 1-feature baseline) |
| LAPPIN_LEASS | `argmax_c sum_i W_i * normalized(f_i_substrate(c))` | YES (5-feature symbolic; THE MECHANISM) |
| ORACLE | `q["expected_char_id"]` | N/A (ceiling) |

All 6 functions are DISTINCT code paths; pred_sha collision = bug or mechanism-collapse.

## Chunked architecture (USER 2026-06-28 + exp_dev.md §13)

3 sibling files, one seed each:
- `exp_substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2_seed_7.py`  → seed 7
- `exp_substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2_seed_13.py` → seed 13
- `exp_substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2_seed_19.py` → seed 19

Each sibling is a thin shim that imports `_q2_lappin_leass_drill2_v2_impl` and sets `HDLAB_SEED` env var. Smoke uses seed_7 only. After smoke clearance, dispatch all 3 to local_cpu_queue at 2700s each.

## ANCHOR/timeout binding (PROT-018/019)

- ANCHOR_NAME = `substrate_narrative_q2_coref_lappin_leass_substrate_faithful_drill2_v2`
- N_DIM tier = 1024 (N_CORTEX/N_PART); no `_n<N>` anchor suffix; PROT-018 N/A
- PROT-019: no _n>=4096 in anchor; --timeout >= 0 unrestricted; chose 2700s for full per chunk
- Smoke local: ~300s estimate (heavier than drill 1 due to substrate cosine queries in feature loops)

## Capability-box logic (consumes both drill verdicts)

- **Drill 1 HARD_FAIL + Drill 2 v2 HARD_FAIL** → capability box closes per USER 2x-drill rule. File capability-closed atom; Q2 coref enters substrate-not-implementable register (with this corpus + this regime).
- **Drill 1 HARD_FAIL + Drill 2 v2 MIDDLE_BAND** → box stays open; iterate weights or regime for drill 2 v3.
- **Drill 1 HARD_FAIL + Drill 2 v2 HARD_PASS** → drill 2 v2 supersedes drill 1 framing; Q2 coref IS substrate-implementable via mechanism class 5a (symbolic salience over substrate-extracted features). M3 concern #3 unblocked.

## HYPOTHESIZED / MEASURED / THEORETICAL / CITED tags (META_RULE_AC)

- random floor: 0.200  THEORETICAL@1/N_CHARACTERS=1/5
- oracle ceiling: 1.000  THEORETICAL@by-construction
- expected baseline (cosine_only) at NF=0.3: ~0.55  HYPOTHESIZED@theoretical 0.7*f_recovery + 0.3*(1/5)
- HP mechanism Q2 floor: 0.80  PRE-REG'D bound; mechanism must recover non-focus pronouns substantially
- HP lift over baseline: 0.15  PRE-REG'D; corresponds to >= 1.2 additional Q2 correct out of 8 questions
- sigma at Q=8 around 0.55: 0.177  THEORETICAL@sqrt(p(1-p)/n)
- drill 1 baseline measured (NF=0.0, all pronouns at scene_focus): 0.625  MEASURED@`data/exp_substrate_narrative_q2_recency_sequence_log_v1_smoke/metrics.json:per_arm.ARM_NAIVE_MAGNITUDE.Q2_coreference`
- drill 2 v1 oracle leak verdict: INVALID  CITED@commit f60880f7 skunkworks landed-VET
- Lappin-Leass weighted-salience reference: CITED@Lappin S, Leass HJ (1994) An algorithm for pronominal anaphora resolution, Comp Linguistics 20(4):535-561 Table 4

## ASCII-only; no LLM at inference; substrate-only (substrate provides FEATURES via cosine query; symbolic algorithm provides READOUT); numpy CPU.
