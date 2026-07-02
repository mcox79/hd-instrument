# Prereg: stretch4_4_meta_learning_cpu_v1 (3-seed R1 rescue)

## Anchor
`stretch4_4_meta_learning_cpu_v1`

## Version marker
2026-07-02 UPGRADE from 1-seed (PP-292 MIDDLE_BAND, 2026-06-19) to 3-seed variance probe.
Prior: fewshot_acc=0.707, n=1500, single seed. R1 rescue plan (multi-seed) named in
`notes/strategy_decisions_2026-06-09.md`. Same substrate mechanism (FHRR prototype bundling
+ overlap classification); adds cross-seed variance quantification. No mechanism change.

## Queue
- SMOKE: `local_cpu_queue` (per USER 2026-07-01 rule: SMOKE ONLY on local)
- FULL:  `remote_cpu_queue` (via Orchestrator; ~1 second wall)

## Scientific question
Does substrate prototype-bundling few-shot induction (K=5 in-cat examples → bundled
prototype; classify new instances via FHRR overlap) reproduce the 0.707 fewshot_acc
result under multi-seed variance, and does the variance qualify as MIDDLE_BAND_ROBUST
(tight cv → reproducible partial capability at a substrate mechanism ceiling)?

## Substrate mechanism (invocation verified)
1. `props = cphasor(NPROP=50, N=8192, g)` -- FHRR basis vector generation (unit complex phasors)
2. `instance(in_cat)` -- FHRR bundling: `sum(props[p] for p in schema_or_random)`
   - in-cat: schema properties with 15% dropout + 30% distractor add
   - out-cat: SCHEMA_SZ=6 random property IDs
3. `prototype = sum(instance(True) for _ in range(KSHOT=5))` -- FHRR bundling of K instances
4. Classification: `sim = vdot(query_instance, prototype).real / (N*KSHOT)`; `pred = sim > 0.35`

Cell body grep-verified: 3 primitive references (`cphasor` decl + decl + invocation) plus
FHRR bundling via `sum(complex64 vectors)` and overlap via `np.vdot(...).real`. NOT the
numpy-in-substrate-costume phantom pattern that killed stretch4_1 / stretch4_3.

## Discriminator-must-survive-scale check (USER 2026-06-26)
Method A (smoke fires discriminator at full-N): SATISFIED.
- N=8192 FIXED between smoke (TR=40) and full (TR=250). Only trial count changes for
  statistical power. Substrate scale is IDENTICAL in smoke and full.
- Local smoke ran mean=0.717 (in MIDDLE_BAND band, not at HP saturation, not at FAIL floor)
  → discriminator firing at full-N, not saturating.

## Formula self-test (mandatory)
```
in_mean=4.212, out_mean=0.816, margin=3.397 at N=8192, K=5
```
Assertions:
- `in_mean > out_mean` (substrate discriminates)
- `margin > 0.5` (clear separation)
Self-test PASSES. Note: fixed classification threshold `0.35` is downstream of substrate;
it is intentionally left un-tuned per bounded scope (R1=multi-seed only, not R2=classifier
recalibration). The fixed-threshold vs empirical-margin gap is the primary MIDDLE_BAND cause.

## Cardinality gate
- `cardinality_ok = (len(per_seed) == 3)` — mandatory pre-reg field for sweep-axis cells
- `arms_differ_verified = (len(set(seed_ids)) == 3)` — no phantom-duplicate seed rows
- HARD_FAIL if either False

## Envelope-fail-bands (verdict logic)
- `HARD_PASS` — `min(fewshot_acc) >= 0.80` (all 3 seeds at/above 0.80)
- `MIDDLE_BAND_ROBUST` — `mean in [0.68, 0.80]` AND `cv <= 0.05`
- `MIDDLE_BAND` — `mean in [0.68, 0.80]` (variance too wide for robust closure)
- `HARD_FAIL` — `mean < 0.68`

Prognosis (from smoke): mean 0.71-0.72, cv 0.02-0.04 at TR=250 → likely
MIDDLE_BAND_ROBUST. Substrate-ceiling closure (not HP; threshold-limited).

## Configs
- N=8192, NPROP=50, SCHEMA_SZ=6, KSHOT=5, SIM_THRESH=0.35
- SEEDS=[4, 5, 6]
- SMOKE: TR=40 (episodes) x 6 queries x 3 seeds = 720 test judgments
- FULL: TR=250 x 6 queries x 3 seeds = 4500 test judgments
- Metrics path: `data/exp_stretch4_4_meta_learning_cpu_v1/metrics.json`

## Timeout
- SMOKE: 60s (observed ~0.06s wall)
- FULL: 60s (observed ~0.16s per seed x 3 seeds x TR ratio 6.25 = <5s expected)

## Stage classification
Stage 3 (higher functions -- meta-learning / compositional understanding).
NOT Stage 4 language equivalence. Synthetic categorical schemas; no ingested language;
no LLM head-to-head. Passes substrate-doesn't-know-anything discipline.

## Progress logging
Trivial wall (<5s) -- progress_logging N/A per META_RULE §17 (only required at
`timeout_s >= 1800`).

## REQUIRED_FIELDS in metrics.json
`anchor_name, verdict, verdict_msg, run_mode, n_seeds, seeds, per_seed,
mean_fewshot_acc, std_fewshot_acc, cv_fewshot_acc, N, TR, KSHOT, NPROP, SCHEMA_SZ,
SIM_THRESH, elapsed_s, cardinality_ok, arms_differ_verified, summary`

## Notes for verdict handler
- If MIDDLE_BAND_ROBUST: this closes PP-292 as substrate-ceiling; a future R2 (adaptive
  threshold from held-out calibration split) could push to HARD_PASS but is out of scope
  for R1 rescue.
- If HARD_FAIL: mechanism has regressed vs 2026-06-19 baseline; treat as
  reproducibility-audit failure.
- If HARD_PASS: single-seed 0.707 was pessimistic; variance-across-seeds resolved upward.

## Prior-arc context (substrate-KB query result)
Concept query `"meta-learning few-shot prototype category learning K-shot substrate FHRR
bundling"` returned this cell's own PP-292 result at cosine=0.356 (rank 3); prior related
work: research_drill_self_modification_5x_2026-06-10 (B5 meta-learning topic);
cls_replay_continual_learning_smoke_v1 prereg (rank 5, cosine=0.350).
