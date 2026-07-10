# Pre-registration: spanning_grounded_core_reach_social_v1

Date: 2026-07-10
Cell: `experiments/exp_spanning_grounded_core_reach_social_v1.py`
Anchor: `spanning_grounded_core_reach_social_v1`
Author: exp_dev (hdi_exp_dev)
Hand-off: `notes/exp_dev_handoff_research_math_social_abstract_grounding_core_expansion_2026-07-10.md` (ANCHOR 2, rank 2).
Spec: `notes/research_math_social_abstract_grounding_core_expansion_2026-07-10.md` (Section 2 SOCIAL + Section 4 SOCIAL
HARD-PASS items 2/4 / HARD-FAIL items 2/3/4).
Fusion architecture: `notes/research_multi_attribute_grounding_fusion_ATL_hub_2026-07-10.md` (late-fusion hub-and-spoke;
pre-flight pairwise-correlation gate; per-channel scrambled control; Pitfall #1 orthogonalize-if-redundant).
Apparatus reused bit-faithful: `experiments/exp_spanning_grounded_core_reach_v1.py` (base reach engine + probes + VAD/
Lancaster/concreteness/AoA channels) and `experiments/exp_spanning_grounded_core_reach_magnitude_v1.py` (Anchor 1; the
channel-SPECIFIC scramble pattern, the WITH/WITHOUT ablation, the computed-lexicon fusion). SOCIAL before/after is
apples-to-apples vs the +0.015 baseline: the WITHOUT-social arm IS the base-channel regime that produced +0.015.
Prior-work check: `bash tools/substrate_query.sh "social relational power affiliation grounding channel late fusion"`
returns only lexical/taxonomy matches (top: entity 'social relation' cosine 0.4795 = a char-trigram lexical hit; substrate
knows nothing per the foundational anchor). NO genuine prior arc cell for a social-relational grounding-reach channel ->
genuinely novel, not a rediscovery.

## Question

The spanning grounded core cosine-reaches EMOTIONAL (+0.48) / PHYSICAL (+0.27) but BARELY reaches SOCIAL (mean sim_mech
+0.015): the sensorimotor + affect (VAD) channels have no dimension that social-STRUCTURAL / RELATIONAL concepts
(hierarchy, loyalty, authority, marriage) coherently load onto. Per the grounding drill, SOCIAL is grounded via a 2D
POWER/DOMINANCE x AFFILIATION/WARMTH coordinate (hippocampal-entorhinal social space; Tavares/Behrens; the Interpersonal
Circumplex) -- a RELATIONAL channel, NOT more affect. Does adding that 2D channel move SOCIAL grounding-reach from +0.015
toward >= +0.15, AND does the gain SURVIVE the affect-ablation (i.e. is it genuine social-relational content, not relabeled
EMOTIONAL reach)?

Honest prior: Anchor 1 (magnitude) landed MIDDLE_BAND -- a scalar-attribute channel barely moved even numerals. So there is
a real prior that scalar/coordinate channels underperform for abstract domains. SOCIAL is a better bet (power x affiliation
is affect-adjacent, affect reached +0.48) but an honest MIDDLE_BAND / negative is itself informative.

## Channel (the substitution flag)

A curated 2D Interpersonal-Circumplex coordinate lexicon: POWER (dominance/control) + AFFILIATION (warmth/solidarity), from
the 8 octant markers at 45-deg spacing on the dominance x warmth plane. CITED@Interpersonal-Circumplex (Leary 1957; Wiggins
IAS; IPIP-IPC octant structure; public-domain instrument). SUBSTITUTION: rather than downloading raw IPIP-IPC item-level
ratings (slow acquisition), the coordinates are CURATED IN-CELL from the published octant geometry -- the SOCIAL analog of
Anchor 1's definitional magnitude lexicon (self-contained, ASCII, no acquisition). 154 terms (trait adjectives + social
roles + institutional/relational nouns). Applied UNIFORMLY; absent words -> NaN (honest no-coverage). Optional augmentation:
`data/grounding_testbed/social_circumplex_ratings.csv` (word,power,affiliation) fills uncovered words if staged; NOT
self-acquired. Binder Social/Human fallback was NOT needed (curated circumplex coverage sufficient for the probe sets).

## Core assembly + probes

Base spanning core (NSM primes + molecules + earliest-AoA grounding-kernel proxy) UNION 30 SOCIAL_CORE_ANCHORS (trait/role
terms spanning all 8 circumplex octants: dominant/submissive/warm/cold/friendly/hostile/leader/follower/... -- give
power/affiliation RANGE to diffuse; DISJOINT from probes). Primary held-out probes = base.PROBES["SOCIAL"] (16 institutional
nouns: contract, debt, citizenship, marriage, hierarchy, etiquette, reputation, alliance, bureaucracy, ownership, authority,
loyalty, justice, committee, tradition, rank). Secondary sub-domain SOCIAL_RELATIONAL = 20 crisp trait/role probes
(assertive, gregarious, affectionate, modest, timid, ruthless, ... DISJOINT from anchors; the clean circumplex-coverage
demonstration, parallel to Anchor 1's MATH_NUMERAL probes).

## Mandatory decorrelation (ATL-hub Pitfall #1) + the affect-ablation

The RAW curated circumplex channel is measured (smoke, below) to be substantially AFFECT: affiliation ~ Warriner valence
r=0.869, power ~ arousal r=0.748 over the real core -- the interpersonal-circumplex warmth axis is inherently valenced.
Per the ATL-hub note (|r|>0.5 -> orthogonalize), the cell RESIDUALIZES power/affiliation against VAD (valence/arousal/
dominance): least-squares fit on CORE rows with full coverage (leakage-safe), applied to all rows; rows without removable
affect -> NaN. The channel then tests affect-RESIDUAL social-relational content. This IS the channel-level implementation
of the hand-off's mandatory AFFECT-ABLATION: the WITHOUT-social arm KEEPS VAD and drops only the residual power/affiliation.

## Arms / controls

- MECHANISM_WITH_SOCIAL: base channels + affect-residual power/affiliation -> probe coordinate (the reach mechanism).
- MECHANISM_WITHOUT_SOCIAL_KEEP_AFFECT (the AFFECT-ABLATION arm): base channels INCLUDING VAD, power/affiliation DROPPED.
  If SOCIAL's gain collapses (>= ABLATION_MIN_REL relative) when the social channel is removed WHILE VAD is kept, the gain
  is genuine social-relational content; if not (< ABLATION_MIN_FLOOR), the reach was affect bleed-through.
- SCRAMBLED_SOCIAL (channel-specific fairness control): permute ONLY the power/affiliation column(s) across the core nodes
  (every other channel intact) -> the reach GAIN must vanish (scr <= without + null tol).
- PRE-FLIGHT correlation gate: RAW (reported as the finding) + POST-orthogonalization (non-redundant by construction; the
  load-bearing fairness controls post-orth are the SOCIAL-scramble + the affect-ablation).

## Pre-registered bands (numeric; picked BEFORE the run; research note Section 4 SOCIAL; sharpened not loosened)

SIM_FLOOR=0.30 (per-probe cosine; random S-dim alignment E[cos]~0 std~1/sqrt(S)), MIN_REACH_CHANNELS=3, SOCIAL_SIM_PASS=0.15
(SOCIAL mean sim_mech HARD_PASS floor; research item 2), SCR_MAX_SIM=0.05, ABLATION_MIN_REL=0.50, ABLATION_MIN_FLOOR=0.10,
MIN_ABS_GAIN=0.10, REDUNDANT_R=0.70, HOPS=2, DIM=32, CONS_PASSES=6, CONS_ALPHA=0.25.

- SOCIAL_CHANNEL_GROUNDS_SOCIAL (HARD_PASS; ALL): SOCIAL (or SOCIAL_RELATIONAL) median mean_sim >= SOCIAL_SIM_PASS (0.15)
  AND absolute gain over WITHOUT-social >= MIN_ABS_GAIN (0.10) AND affect-ablation relative collapse >= ABLATION_MIN_REL
  (0.50, VAD kept) AND social-scramble null AND power/affiliation non-redundant, on the MEDIAN across seeds.
- HARD_FAIL_AFFECT_RELABEL: WITH-social sim >= 0.15 but the gain does NOT survive the affect-ablation (collapse <
  ABLATION_MIN_FLOOR / no real gain over the VAD-kept baseline) -> relabeled EMOTIONAL reach (the hand-off-flagged most
  likely fake-pass).
- HARD_FAIL_CHANNEL_INSUFFICIENT: social-scramble fires cleanly but SOCIAL stays <= 0 -> residual needs mentalizing/
  theory-of-mind content or the metaphor-bridge (Anchor 3), not this channel (research Section 4 HARD-FAIL item 2).
- HARD_FAIL_FAIRNESS: social-scramble ALSO reaches positive (inflation) OR (raw path, if orthogonalization skipped)
  channel redundant with an existing channel.
- MIDDLE_BAND: sim below the +0.15 bar or ablation weak with clean controls -> matches the Anchor-1 magnitude MIDDLE_BAND
  prior; investigate before scaling.

## Self-test (SELFTEST_PASS; LIGHT local gate; MEASURED)

Planted social world (PHYSICAL grounds via 4 sensorimotor dims; SOCIAL carries a coherent 2D power x affiliation signal but
INCOHERENT + weak sensorimotor AND VAD -> grounds ONLY via the social channel; VAD present-but-uninformative so the
affect-ablation is meaningful). MEASURED@data/exp_spanning_grounded_core_reach_social_v1_selftest/metrics.json
(run_mode=self_test):
- (a) WITHOUT-social (sensorimotor + VAD, affect KEPT): SOCIAL mean_sim 0.2947, reach 0.667.
- (b) WITH-social (+power/affiliation): SOCIAL mean_sim 0.7621, reach 1.0 -> mechanism fires (gap +0.467).
- (c) SOCIAL-scramble: mean_sim -0.0897 (<= without + 0.05) -> fairness discriminator fires.
- (d) AFFECT-ABLATION: VAD kept in WITHOUT (valence/arousal/dominance), SOCIAL still collapses 61% relative -> genuine
  social content discriminator fires. correlation gate non-redundant (max|r| 0.17/0.19 vs sensorimotor+VAD). arms differ.
  physical reach 0.667. st_ok=True. Plants the full reach logic at small n = discriminator-survives-scale (Path C).

## Smoke (SMOKE-ONLY-LOCAL; MEASURED; source=cn; the KEY FINDING)

MEASURED@data/exp_spanning_grounded_core_reach_social_v1_smoke/metrics.json (seeds=[7,13], source=cn, n_kernel=300,
max_nodes=3000, n=3000 nodes / 10448 edges):
- RAW correlation gate FIRED REDUNDANT (the finding): affiliation ~ valence r=0.869, power ~ arousal r=0.748 -- the raw
  circumplex coordinate is substantially affect over the real core (interpersonal warmth is inherently valenced). This is
  exactly the affect-confound the hand-off flagged as the most likely fake-pass.
- Orthogonalization applied: post-orthogonalization VAD correlations 0.0 (residual by construction), max |r| vs any channel
  0.23/0.25 -> non-redundant. Mechanism + ALL 3 discriminators fire.
- SOCIAL (base institutional probes): WITH -0.218 / WITHOUT -0.263 / scramble -0.241 (still negative; cn smoke is a
  harsher/sparser regime than the +0.015 FULL baseline). SOCIAL_RELATIONAL (trait probes): WITH 0.262 / WITHOUT 0.259 /
  scramble 0.45 -> the affect-residual channel adds only +0.003 (their ~0.26 grounding is carried by AFFECT, not the
  residual social coordinate).
- Smoke real-data verdict: HARD_FAIL_AFFECT_RELABEL -> STRONG NEGATIVE PRIOR at smoke scale. The FULL (cskg, all probes,
  5 seeds, median) is the definitive test: the smoke cn regime is not a faithful preview of the FULL cskg regime for the
  base SOCIAL metric (SOCIAL base -0.26 on cn vs +0.015 on cskg full), so the FULL confirms/overturns the bounded finding
  with proper multi-seed statistics on the richer cross-cutting-commonsense graph.

## SCHEMA-VET

cell_chunked: false (single graph; seeds cheap; per-seed loop with cardinality-breach guard); start_marker_written: true;
crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics + traceback; SystemExit/KeyboardInterrupt re-raised);
final_metrics_atomicity: tmp_replace (write_metrics + os.replace; write_partial per seed); arms_differ_verified: true (>=3
distinct arm sigs: with-social / without-social-keep-affect / scrambled, asserted per seed via mech!=scr + WITH vs WITHOUT
channel-subset); except SystemExit before except Exception (no bare/BaseException; grep-gate clean, non-ascii bytes 0);
crlb: per-probe cosine chance ~0 (THEORETICAL), SIM_FLOOR 0.30 strictly above null, SOCIAL_SIM_PASS 0.15 strictly above 0;
baseline_in_band: WITHOUT-social reproduces the base +0.015 SOCIAL regime (barely-reaching, not saturated); by construction
in-band; discriminator-survives-scale: planted self-test fires reach + scramble + affect-ablation at full logic (Path C +
Path B scale-invariance of the reach fraction); HP_SCOPE: SOCIAL-sim-pass + affect-ablation gate apply to
MECHANISM_WITH_SOCIAL vs MECHANISM_WITHOUT_SOCIAL_KEEP_AFFECT + SCRAMBLED only; cardinality_ok: EXPECTED_N_UNITS=n_seeds
(per-seed arms-differ + cardinality-breach guard -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if a seed drops);
calibration_check: default_ok_for_this_regime (bands PRINCIPLED per research note, fixed before the run; engine CONS_*
inherited from the validated a519 engine); progress_logging: print_flush_true (all _log flush=True; MANDATORY as FULL
timeout >= 1800s); sweep_alignment_verdict: N/A (no parameter sweep); discriminating_fraction: N/A (per-domain reach, not a
sweep); composition_edges: base-channels + affect-residual power/affiliation -> diffusion-with-restart -> probe coordinate
(SHAPE_MATCH: engine consumes [n,d] anchors + edge lists directly); positive_control: WITH-social planted core flips SOCIAL
reach positive + reproduces the base reach mechanism at the planted regime; functional_requirements: (i) build a 2D
social-relational coordinate channel (curated circumplex), (ii) DECORRELATE it from affect (orthogonalize vs VAD, leakage-
safe core-fit), (iii) fuse via the validated diffusion engine, (iv) measure SOCIAL per-domain reach with/without the
channel, (v) affect-ablation (VAD kept) + channel-scramble + correlation gate to detect affect-relabel / inflation -- each
decomposed + mapped to a validated primitive. Data-dependency: cell self-acquires 4 norm files + CSKG via curl (validated)
else HARD_FAIL_DATA_MISSING; circumplex coordinates are in-cell (no acquisition).

## Compute architecture

class (a), CPU-fast eval; DOMINANT cost = one-time streaming parse of the ~6M-edge CSKG TSV (CPU/IO-bound; gzip 112MB) then
dense diffusion-with-restart (dense [n,n]@[n,d], n capped 6000) x 6 passes x 2 arms x 5 seeds -> seconds/seed on CPU (same
regime as the base reach + magnitude cells). Storage SHARDED (each concept its own grounded vector). SELF-TEST planted-only
(local, sub-second). SMOKE source=cn (local relations.jsonl; no CSKG download) LOCAL, 6.4s. FULL CSKG assembly + all-domain
reach is INTENSIVE -> REMOTE (remote_cpu_queue; graph parse dominates; Tier B; CPU/numpy). SMOKE-ONLY-LOCAL lock honored.

## Config

FULL: seeds=[7,13,17,23,29], source=cskg, n_kernel=1500, max_nodes=6000. SMOKE: seeds=[7,13], source=cn, n_kernel=300,
max_nodes=3000. SELFTEST: planted world (local, SELFTEST_PASS). Median-seed reported (not mean-only) per seed-fragility.
FULL timeout: 3600s -- covers worst-case CSKG self-acquire (curl --max-time 1200 if not cached) + ~3min streaming parse of
6M edges + ~5min eval (5 seeds x 2 arms) + margin. progress_logging=print_flush_true (per-seed + per-stage flush) as the
FULL timeout >= 1800s heartbeat-mandate threshold.

## Dispatch

Remote (remote_cpu_queue) -- exp_dev returns the queue_add.sh command; the orchestrator ships + owns REMOTE VERIFY:
`bash tools/orchestrator/queue_add.sh remote_cpu_queue spanning_grounded_core_reach_social_v1 experiments/exp_spanning_grounded_core_reach_social_v1.py preregs/2026-07-10_spanning_grounded_core_reach_social_v1.md 3600`
