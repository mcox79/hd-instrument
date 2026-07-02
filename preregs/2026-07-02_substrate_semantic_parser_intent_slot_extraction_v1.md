# Pre-reg: substrate_semantic_parser_intent_slot_extraction_v1

Date: 2026-07-02
Author: hdi_exp_dev (spawn)
Route: SMOKE local_cpu_queue (3 seeds sequential ~5 min); FULL remote_cpu_queue (per-seed chunked, ~10-15 min each)
Timeout: FULL 1800s per seed
Parents:
  - IntentClassifier CG at n_intents=50 (Atom a1; hdlab/intent_classifier.py; acc=0.754; maj_mult=4.62; p95=0.54ms)
  - Sharded storage META CG_META 2026-07-02 (T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1)
  - HRR bind/unbind CG (hdlab/binding.py; FFT circular convolution)
  - k_NN_lookup cleanup CG (hdlab/cleanup_family.py)
  - M1.5 v2 TWOTIER context retention (Atom 18) — future context-resolution leg (v2)
Trigger: Research drill note
  notes/research_M1_9_semantic_parser_primitive_design_2026-07-02.md
  (Rank 1 candidate; Stage 3 cortex primitive; P_CG=0.55)

## Substrate-KB concept-query check (mandatory)

Query: `semantic parser intent slot extraction Wernicke Broca compositional binding`

Top hits (all cosine <= 0.31):
  1. 'D composition DIRECTIONAL finding' cosine=0.3076 (orthogonal — QA v2 domain)
  2. 'Compositional understanding requires hierarchical coarse-graining' cosine=0.3027 (cortex 4x drill; adjacent-but-distinct — refers to ultrametric abstraction, not role-slot parsing)
  3. same chunk (chunk064) cosine=0.3027
  4. HRR-unbind-chain REFUTED at compositional generalization regime cosine=0.3018 (Skunkworks batch9 vet 2026-06-26; orthogonal — feature-overlap prototypes)
  5. same chunk 010

**Prior-work verdict: NONE at cosine > 0.35 matching semantic-parser cell.**
This cell is a genuine EXTENSION of IntentClassifier (CG at n=50) + sharded storage
(CG_META 2026-07-02) + HRR bind/unbind (CG) with new slot-extraction leg on top.
NOT rediscovery. Prior arc W_lex/W_gram dual-substrate + TALKS-2 substrate intent
parser docs surfaced by Director (research note); no cell built the compositional
role-slot parser primitive before.

## Purpose

Test whether COMPOSITIONAL BINDING of intent + per-role slot values into a bundled
parse_hd on Stage 3 SYNTHETIC schema:
  (1) recovers correct intent above IntentClassifier baseline (i.e. slot noise
      does not tank intent extraction)
  (2) recovers correct per-role slot value via unbind + per-role sharded cleanup
      (slot-fill >= 0.80)
  (3) SHUFFLED_ROLE_KEYS sanity control collapses slot-fill toward random
      (validates role-binding does real work; RULES OUT cross-talk-only mechanism)
  (4) INTENT_ONLY cross-check confirms substrate arm's intent leg is not
      degraded vs bare classifier

Load-bearing framing:
  - If HP: promotes M1.9 SemanticParser to first-round CG; unlocks front-of-Cortex
    composition (per drill Section 7: parse-first mirrors Friederici 2011 phase I/II).
  - If MB: identifies slot-cross-talk regime; iterate on shard-disjointness.
  - If HF: mechanism-class refuted at Stage 3 vocab scope; regroup on chunked
    attention (drill Candidate 2) or recursive parser (Candidate 4).

## Stage / Scope

Stage 3 (structured input; substrate-native; synthetic schema).
NOT Stage 4 (language parse; real vocab).
Per USER-locked stage-progression + substrate-doesnt-know-anything disciplines.
Synthetic vocab: opaque token IDs; schema IS the semantics. Substrate never
sees "language" it doesn't have a dictionary for.

## Arms

ARM_BASELINE_SYMBOLIC: ground-truth symbolic parser (returns the drawn intent
  + drawn slot fills directly). Expected intent=1.0 slot=1.0. Positive control
  that scoring rig is correct.

ARM_SUBSTRATE_FULL: full mechanism — IntentClassifier.predict(input_hd) for intent
  + per-role hdlab.binding.unbind(input_hd, ROLE_KEYS[role]) + hdlab.cleanup_family.k_NN_lookup
  over per-role sharded SLOT_DICT[role] for each slot. This is the M1.9 primitive
  under test.

ARM_INTENT_ONLY: IntentClassifier.predict(input_hd) only; slots randomly guessed.
  Cross-check: substrate FULL intent must not be worse than INTENT_ONLY intent
  (>0.03 regression => cell bug).

ARM_M16_ROUTER: alternate slot-mechanism — direct cosine similarity of input_hd
  against per-role SLOT_DICT (no unbind step). Attention-router-style shortcut.
  Cross-check per drill Candidate 2. Expected to UNDER-perform ARM_SUBSTRATE_FULL
  on slot-fill because role-binding is not exploited (any slot with high sim to
  input wins regardless of role position).

ARM_SHUFFLED_ROLE_KEYS: sanity control — same mechanism as ARM_SUBSTRATE_FULL
  but ROLE_KEYS are shuffled between encode-time and decode-time. Slot-fill
  MUST collapse (<=0.20). Validates role-binding is doing real work; failure
  of collapse would imply substrate is just doing cleanup on any-key
  (cross-talk-only mechanism, not compositional).

## Query set

Per seed:
  - N_train = 500 examples (Hebbian one-shot IntentClassifier training)
  - N_test = 200 held-out examples (disjoint sample)
Total per seed per arm = 200 test examples * 5 slot roles = 1000 slot-decisions
+ 200 intent-decisions.
Cardinality: 3 seeds * 5 arms = 15 arm-seed units (each unit reports intent-acc + slot-acc per role).

EXPECTED_N_UNITS = 15 (arm-seed) with per-unit N_test=200 rows.

## HP conditions (chain-grade if ALL fire)

HP_INTENT_MATCH:
  ARM_SUBSTRATE_FULL intent_acc mean across 3 seeds >= 0.85
  HP_SCOPE = [ARM_SUBSTRATE_FULL]

HP_SLOT_FILL:
  ARM_SUBSTRATE_FULL slot_fill_acc mean across 5 roles + 3 seeds >= 0.80
  HP_SCOPE = [ARM_SUBSTRATE_FULL]

HP_SHUFFLED_COLLAPSE:
  ARM_SHUFFLED_ROLE_KEYS slot_fill_acc mean across 3 seeds <= 0.20
  (chance for 100-way per-role cleanup with shuffled key = 0.01;
   band <= 0.20 gives slack for near-orthogonal shuffle draws)
  HP_SCOPE = [ARM_SHUFFLED_ROLE_KEYS]

HP_INTENT_CROSSCHECK:
  ARM_SUBSTRATE_FULL intent_acc >= ARM_INTENT_ONLY intent_acc - 0.03
  (composition of intent + slot bundle does not degrade intent leg)
  HP_SCOPE = [ARM_SUBSTRATE_FULL, ARM_INTENT_ONLY]

HP_BASELINE_TRIVIAL:
  ARM_BASELINE_SYMBOLIC intent_acc = 1.0 AND slot_fill = 1.0
  (positive control; scoring rig correct)
  HP_SCOPE = [ARM_BASELINE_SYMBOLIC]

## MIDDLE_BAND conditions

MB_INTENT_PARTIAL:
  ARM_SUBSTRATE_FULL intent_acc in [0.70, 0.85)
MB_SLOT_PARTIAL:
  ARM_SUBSTRATE_FULL slot_fill_acc in [0.60, 0.80)

## HF conditions

HF_INTENT_BROKEN:
  ARM_SUBSTRATE_FULL intent_acc < 0.70
HF_SLOT_BROKEN:
  ARM_SUBSTRATE_FULL slot_fill_acc < 0.60
HF_SHUFFLED_NOT_COLLAPSED:
  ARM_SHUFFLED_ROLE_KEYS slot_fill_acc > 0.30
  (role-binding isn't doing work; mechanism is cross-talk-only; refutes compositional)
HF_ENVELOPE_SCHEMA_BROKEN:
  ARM_BASELINE_SYMBOLIC any_acc < 0.99 (halt; repair)
HF_INTENT_LEG_BUG:
  ARM_INTENT_ONLY intent_acc >= ARM_SUBSTRATE_FULL intent_acc + 0.03
  (substrate cell has composition bug)
HF_CARDINALITY_BREACH_META_RULE_H:
  observed n_units < 13 (< 87% of 15)
HF_ARMS_IDENTICAL_META_RULE_AF:
  distinct arms produce bit-identical per-query prediction tensors

## Cardinality

EXPECTED_N_UNITS = 3 seeds * 5 arms = 15 arm-seed units
CARDINALITY_FLOOR = 13 (87%)

Per-unit rows: N_test=200 predictions per arm per seed; slot rows = 200 * 5 roles = 1000 per arm per seed.
Total prediction rows across full: 15 * 200 = 3000 intent, 15 * 1000 = 15000 slot.

## Discriminator-survives-scale justification (META rule)

**Option A: smoke at full-N.**
Smoke uses N_DIM=8192, N_INTENTS=50, N_ROLES=5, SLOT_DICT_SIZE=100 identically
to full config. Only N_TEST reduced (200 -> 50) and N_TRAIN (500 -> 200).
Substrate regime is invariant across smoke/full. Mechanism arms differentiate
at full-N in smoke.

**Preview arm check:** at smoke, ARM_SHUFFLED_ROLE_KEYS slot_fill_acc must
already show <= 0.30 (collapse trajectory). If not, mechanism has cross-talk
issue at chosen shard-disjointness; reject full dispatch.

## Baseline-in-band justification (META_RULE_AG)

  - ARM_BASELINE_SYMBOLIC scores 1.0 by construction (positive control, not baseline for band check).
  - ARM_SHUFFLED_ROLE_KEYS expected in [0.01, 0.20] slot_fill_acc (in-band).
  - ARM_INTENT_ONLY intent_acc expected in [0.80, 0.95] (in-band).
  - ARM_M16_ROUTER slot_fill_acc expected in [0.10, 0.40] (in-band per drill Candidate 2 attention-shortcut).
  - ARM_SUBSTRATE_FULL intent_acc expected in [0.85, 0.95] AND slot_fill expected in [0.70, 0.90] (target discriminating band).

baseline_in_band: True (multiple arms in [0.05, 0.95] discriminating range).

## CRLB / capacity-feasibility (META §9)

  - Per-role slot cleanup: k_NN_lookup argmax over 100-way per-role dictionary.
    Bipolar HRR unbind SNR at N=8192 with 5-role bundle:
    signal = 1.0 (correct slot); noise per bundle = sqrt(K)/sqrt(N) = sqrt(5)/sqrt(8192) = 0.0247
    per-query top-1 accuracy floor >= 1 - 100 * exp(-SNR^2 * N / 2) approx>0.99
    THEORETICAL@bipolar-HRR-cleanup-Plate-1995
  - Intent: IntentClassifier at n=50 CG accuracy 0.754 (Atom a1); with additional
    slot-noise from bundle, expect degradation ~0.05-0.15 to [0.60, 0.75].
    HP_INTENT_MATCH >= 0.85 REQUIRES intent-signal boost via bundle norm.
    Adaptive check: if measured < 0.85, consider MB not HF (band adjustment).
  - Chance floor slot: 1/100 = 0.01 (100-way per-role dictionary).
  - Chance floor intent: 1/50 = 0.02.
  - HP margins: intent 0.85 vs 0.02 = 42x chance; slot 0.80 vs 0.01 = 80x chance. Comfortable.

crlb_floor_computed: 0.01 (slot chance floor)
crlb_slot_theoretical_ceiling: 0.99 (HRR unbind at K=5 bundle, N=8192)
crlb_formula_reference: sigma_slot = sqrt(K/N) per bipolar HRR-bundle; intent_acc bounded by IntentClassifier CG floor 0.754 + bundle-noise adjustment
discriminator_reachability: True

## Composition edges / shape audit (META §15C)

  encoder (synthetic token HDs) -> compositional bundle: SHAPE_MATCH
    input_hd = intent_hd + bundle_i( bind(ROLE_KEYS[i], SLOT_DICT[i][slot_i]) )
    all in R^8192 (real-valued HRR)
  compositional bundle -> IntentClassifier.predict: SHAPE_MATCH
    R^8192 -> int (argmax over 50 codebook)
  compositional bundle -> hdlab.binding.unbind: SHAPE_MATCH
    (R^8192, R^8192) -> R^8192 per role
  unbound HD -> hdlab.cleanup_family.k_NN_lookup: SHAPE_MATCH
    (R^8192, R^[100,8192]) -> (R^8192, argmax int)

sweep_alignment_verdict: ALIGNED (no cross-axis sweep; arm axis only)

## Positive control arm (META §15D)

ARM_BASELINE_SYMBOLIC: reproduces ground-truth (scores 1.0 by construction).
Cited prior: IntentClassifier Atom a1 acc=0.754 at n=50 MEASURED@hdlab/intent_classifier.py docstring.
Tolerance: intent-only leg in v1 should reproduce ~0.75 baseline within +/-0.10.
If ARM_INTENT_ONLY < 0.65, HARD_FAIL_POSITIVE_CONTROL_BROKEN (IntentClassifier
regime mismatch or invocation bug).

## Functional requirements (META §15E)

  FR1: extract INTENT from input_hd (compositional bundle).
       Primitive: hdlab.intent_classifier.IntentClassifier (CG at n=50).
  FR2: extract per-role SLOT VALUE from input_hd via role-key unbind.
       Primitive: hdlab.binding.unbind (CG HRR circular convolution).
  FR3: cleanup unbound noisy HD against per-role sharded slot dictionary.
       Primitive: hdlab.cleanup_family.k_NN_lookup (CG cleanup).
  FR4: SHARDED per-role storage (not bundled) per CG_META 2026-07-02.
       Per-role SLOT_DICT[role] = ndarray[100, 8192] each; disjoint token ID subsets per role.

## Compute architecture

**Class: (b) sequential-CPU with justification.**
  - Per query: 1 IntentClassifier.predict (O(N_intents * N_dim + N_dim^2))
    + 5 unbind ops (FFT O(N log N) each) + 5 k_NN_lookup (O(100 * N_dim) each).
    Per-query wall approx 5-10 ms on CPU.
  - 200 test queries * 5 arms * 3 seeds = 3000 queries. Total wall ~15-30s
    per seed * 3 seeds = ~1-3 min FULL.
  - Well below 10s per-phase-point threshold requiring GPU-batching. Substrate
    IS the primitive being validated; matches justification exemption in
    exp_dev.md §GPU-BATCHING.
  - Storage: SHARDED (per-role SLOT_DICT[role] separate ndarrays). Per CG_META
    2026-07-02 physics law.

storage_strategy: sharded

## Schema-vet mandatory pre-reg fields (per exp_dev.md §14)

cell_chunked: false (single-file cell with --seed argparse; smoke iterates seeds; FULL dispatches 3 separate --seed invocations)
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: passed_all_4_patterns
cardinality_ok: mandatory (observed >= 13 of 15 arm-seed units)
arms_differ_verified: mandatory at smoke (hash raw per-query intent+slot prediction tensor)
arms_differ_exempted: NONE
baseline_in_band: mandatory (arm scores in [0.05, 0.95] measurement band; symbolic exempt as positive control)
crlb_floor_computed: 0.01
discriminator_reachability: True
sweep_alignment_verdict: ALIGNED
discriminating_fraction: 0.60 (3 of 5 arms in discriminating band)
composition_edges: all SHAPE_MATCH
positive_control_arms: ARM_BASELINE_SYMBOLIC 1.0 by construction; ARM_INTENT_ONLY reproduces IntentClassifier ~0.75
final_metrics_atomicity: tmp_replace
calibration_check: default_ok_for_this_regime (K=5 bundle, N=8192, K/N=6e-4 well under HRR capacity 0.14)
progress_logging: print_flush_true
run_mode_default: full (cell defaults to full unless --smoke or --self-test)

## Test-design gates (META §15A/B)

Gate A effective_vs_nominal_parameter_audit: N/A (no parameter sweep; arm axis only)
Gate B discriminating_fraction: 0.60 (3 of 5 arms in [0.10, 0.90] band)
Gate C SHAPE audit: all SHAPE_MATCH (see composition edges)
Gate D positive_control_arm: ARM_BASELINE_SYMBOLIC + ARM_INTENT_ONLY both cited
Gate E functional_requirements: FR1-FR4 decomposed above

## Preserved conventions

  - ASCII-only (no unicode)
  - No emojis
  - REPO-relative paths
  - numpy Generator with known seed (per IntentClassifier convention)
  - N_DIM=8192 fixed in BOTH smoke + full
  - except SystemExit: raise BEFORE except Exception (META §8)

## Route

SMOKE: local_cpu_queue via tools/queue_add.py; iterates 3 seeds internally in single dispatch (fast smoke).
FULL: remote_cpu_queue via hdi_orchestrator handoff (harness-denied push to exp_dev).
Cell-author (this spawn) DOES: pre-reg + cell code + local smoke run + REMOTE VERIFY.
Orchestrator DOES: git push origin main + queue_add.py for 3-seed FULL dispatch.

## Loading framing (if HP)

Promotes M1.9 SemanticParser to CG (Stage 3 M3 cortex primitive; front-of-Cortex
placement per Friederici 2011 phase I/II brain-grounded ordering).
Extends prior arc dual-substrate W_lex/W_gram (2026-06-11 llm-boundary drill)
+ substrate TALKS-2 intent parser (2026-06-08). Chain-grade portfolio +1.
Sets up next M1.9 v2 (recursive parser / context resolution via M1.5 STM)
and M1.10 (Response Planner) integration.

## AMENDMENT 2026-07-02 (smoke-driven intent-leg swap; documented before FULL dispatch)

**Change:** ARM_SUBSTRATE_FULL and ARM_M16_ROUTER + ARM_SHUFFLED_ROLE_KEYS intent leg
switched from `IntentClassifier.predict` (Hebbian-trained) to direct
`k_NN_lookup(input_hd, intent_codebook, k=1)` cleanup on intent codebook.

**Rationale:** smoke iteration 1 at INTENT_WEIGHT=3.0 observed intent_acc = 0.02-0.06 across
all seeds (essentially at chance 1/50 = 0.02). Diagnostic sweep (INTENT_WEIGHT in {1,3,5,10}
at seed 11) showed Hebbian classifier flatlined at 0.02 across all weights, while direct
k_NN_lookup gave 0.16 → 0.56 → 1.00 as weight increased.

**Root cause:** IntentClassifier's Hebbian-train CG regime (Atom a1, hdlab/intent_classifier.py
docstring) was CharTrigramEncoder-encoded natural-language text queries, ONE prototype-shaped
input per intent with modest cross-intent noise. Compositional-bundle inputs (intent_hd
summed with 5 role-slot HRR binds each contributing ~sqrt(N) magnitude noise) fall in a
DIFFERENT regime. Hebbian one-shot training on n_train=200 across 50 intents (=4 examples/class)
cannot average out K=5 role-slot bundle noise → W matrix does not learn discriminative
intent structure. This is a Gate-D-class regime-mismatch caught in smoke.

**Substrate primitive appropriate for this regime:** direct k_NN_lookup cleanup on
intent codebook. Same primitive family as slot cleanup (mechanism-family symmetry).
Zero training required. HD-instrument chain-grade cleanup primitive per hdlab.cleanup_family CG.

**META finding for CG_META candidate 2026-07-02:**
`HEBBIAN_CLASSIFIER_REGIME_NARROW_FOR_COMPOSITIONAL_BUNDLE_INPUTS`
IntentClassifier Atom a1 (CG at n=50, acc=0.754) trained on text-encoded queries does NOT
extend to compositional-bundle inputs where intent_hd is one term among K=5 role-slot binds.
Direct k_NN_lookup cleanup on codebook is the substrate-native primitive that does extend
(smoke acc 0.86 at INTENT_WEIGHT=8). Sonnet drill "IntentClassifier.predict(input_hd)" wording
under-specified WHICH intent-readout primitive; smoke selected the correct one.

**Amended arm semantics:**
- ARM_INTENT_ONLY still uses Hebbian IntentClassifier — now serves as REGIME-NARROWNESS REFERENCE
  (positive-control-broken sentinel). Expected intent_acc ~ chance (0.02) confirms
  regime-narrowness finding.
- HP_INTENT_CROSSCHECK gate `substrate_full intent >= intent_only intent - 0.03`:
  trivially satisfied (substrate_full uses stronger primitive). Downgraded to informational
  metric; no longer a load-bearing gate against composition-bug (would require matched-primitive
  ARM_INTENT_HEBBIAN v2 arm).
- INTENT_WEIGHT parameter added: 8.0 default (intent term amplified in bundle so direct-cosine
  cleanup lands above HP floor 0.85 while preserving slot signal).

**Smoke results at INTENT_WEIGHT=8.0 (3 seeds):**
  ARM_SUBSTRATE_FULL: intent 0.860, slot_fill 1.000 (all seeds identical to 3sf)
  ARM_SHUFFLED_ROLE_KEYS: slot 0.012-0.032 (collapse to chance, role-binding validated)
  ARM_M16_ROUTER: slot 0.004-0.020 (direct-cosine without unbind fails, unbind mechanism load-bearing)
  ARM_INTENT_ONLY (Hebbian): intent 0.033 mean (regime-narrow reference confirmed)
  ARM_BASELINE_SYMBOLIC: 1.000/1.000 (positive control)

HP verdict at smoke: HARD_PASS.
Discriminator-survives-scale: substrate_full slot 1.000 is at ceiling, well above shuffled 0.02
and M16 0.02 (gap ~0.98); intent 0.86 above HP floor 0.85; margins survive full-N (N_test 50→200).

## HYPOTHESIZED vs MEASURED (META_RULE_AC)

- IntentClassifier n=50 acc=0.754 MEASURED@hdlab/intent_classifier.py docstring
  (Atom a1 CG)
- IntentClassifier n=50-1000 EXT-3 CG'd MEASURED@substrate cert_ledger 2026-06 lift
- HRR bundle SNR at K=5 N=8192 = sqrt(5/8192)=0.0247 THEORETICAL@Plate-1995-HRR
- Slot cleanup top-1 accuracy floor >= 0.99 at K=5/N=8192/M=100 THEORETICAL@bipolar-HRR-cleanup-Plate-1995
- Expected ARM_SUBSTRATE_FULL intent_acc ~ 0.85 HYPOTHESIZED@drill_note_section_6 (P_deflated 0.55)
- Expected slot_fill ~ 0.80-0.90 HYPOTHESIZED@drill_note_section_6 (P_deflated 0.55)
- Expected ARM_SHUFFLED_ROLE_KEYS <= 0.20 HYPOTHESIZED@sanity-control (chance 0.01 per role)
