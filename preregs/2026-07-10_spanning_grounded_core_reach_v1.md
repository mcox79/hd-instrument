# Pre-registration: spanning_grounded_core_reach_v1

Date: 2026-07-10
Cell: `experiments/exp_spanning_grounded_core_reach_v1.py`
Anchor: `spanning_grounded_core_reach_v1`
Author: exp_dev (hdi_exp_dev)
Spec: `notes/research_deliberate_ingest_spec_spanning_grounded_core_2026-07-10.md` (THE spec: spanning-basis reframe,
grounding-reach acceptance test, the density!=spanning anti-pattern).
CSKG core: `notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md` (cross-cutting 12-core 23,632 @ deg 38.4; PASS;
the cross-cutting relation-set + the 79.1% lexical dilution to strip).
Fairness discipline: `notes/grounding_anchor_design_first_testbed_2026-07-10.md` (exterior channel must be LOAD-BEARING;
ablate it -> grounding must collapse).
Engine reused (validated): `grounding_consolidation_loop_degree_invariant_v1` (normalized-Laplacian diffusion-with-restart,
PPR/SR; SELFTEST_PASS) as the correlation-path mechanism.
Discriminator reused (validated this session): `grounding_multiattribute_fusion_v1` (relational-only ablation + scrambled
must-fail control + independence gate) as the reach measurement, re-applied to a domain-diverse adversarial probe set.
Prior-work check: substrate_query "spanning grounded core semantic primes sensorimotor grounding reach commonsense KG"
returns only char-trigram lexical matches on the word "ground" (top cosine 0.3447 = the token "grounding"; substrate
knows nothing per the foundational anchor). NO genuine prior arc cell for a spanning-grounded-core reach test -> this is
genuinely novel, not a rediscovery.

## Question

Does a deliberately-composed grounded CORE (dictionary grounding-kernel proxy UNION Wierzbicka/Goddard NSM 65 semantic
primes + ~50 molecules UNION Lancaster-sensorimotor-covered entities), grounded at ingest with a multi-channel measured-
attribute vector and wired with CSKG cross-cutting commonsense relations, actually SPAN meaning-space -- i.e. can a
deliberately-DIVERSE held-out probe set across 6 domains (PHYSICAL / ABSTRACT / EMOTIONAL / MATHEMATICAL / SOCIAL /
TEMPORAL) each find a CORRELATION PATH to the grounded core (via relations + attribute-similarity)? Selection criterion
= dimensional SPAN + grounding-reach, NOT density/size.

## Core assembly (the spanning basis)

- NSM 65 semantic primes (CITED: Goddard & Wierzbicka 2014) + ~50 semantic molecules -- the ONLY basis covering
  logical/relational/abstract meaning sensorimotor norms structurally cannot reach (the sadness/multiplication/because gap).
- Grounding-kernel proxy: words present in Lancaster AND concreteness AND AoA, ordered by EARLIEST AoA (developmental
  concrete-first curriculum), top-N (cheap MGS proxy pending exact feedback-vertex-set recomputation, per the spec's
  honest-gap note). FULL N=1500; SMOKE N=250.
- UNION, resolved to relational-graph node labels. FULL relational source = CSKG (Zenodo 4331372 cskg.tsv.gz; its 251k
  mw:SameAs identity links already merge ConceptNet/WordNet/Wikidata-CS/FrameNet), restricted to the CROSS-CUTTING
  commonsense subgraph (ATOMIC at:* + LocatedNear/MayHaveProperty/UsedFor/CapableOf/PartOf/AtLocation/HasSubevent/
  HasPrerequisite/Causes/HasA/MannerOf/MotivatedByGoal/HasProperty/ReceivesAction/CausesDesire/Desires/MadeOf/...),
  STRIPPING the 79.1% lexical dilution (RelatedTo/Synonym/Antonym/FormOf/IsA/HasContext/DerivedFrom/dbpedia/SameAs...).
  SMOKE relational source = local ConceptNet relations.jsonl (CN_ scope) for a light dispatch-visible smoke.
- Each core concept grounded at ingest with its multi-channel attribute vector; concepts with NO norm coverage FLAGGED
  (grounded_fraction reported), never fabricated.

## Relational structure

CSKG cross-cutting commonsense edges among the core concepts + their H=2-hop neighborhood, induced subgraph capped to
max_nodes (FULL 6000, SMOKE 3000; neighbors ranked by edge-count to the core/probe seed set; all seeds retained).

## Datasets (public human-rating norms + CSKG; LOCAL testbed inputs; provenance in data/grounding_testbed/)

- Brysbaert (2014) concreteness Conc.M; Warriner (2013) valence/arousal/dominance; Lynott-Connell/Lancaster (2020) 6
  sensory-modality perceptual-strength means; Kuperman (2012) age-of-acquisition AoA_Kup.
  (staged; provenance data/grounding_testbed/PROVENANCE_multiattribute.md; sha256 recorded there).
- CSKG v1.0 cskg.tsv.gz -- Zenodo record 4331372, https://zenodo.org/api/records/4331372/files/cskg.tsv.gz/content;
  MEASURED@disk 112,312,195 bytes (exact match to the k-core gate note); gitignored.
NOT written to canonical substrate_index; NEVER git add -A; cell self-acquires each via curl (header/size validated) if
absent on the runner, else HARD_FAIL_DATA_MISSING.

## The reach metric (operationalized; reuses the validated engine + discriminator)

A probe's GROUNDED COORDINATE = diffusion-with-restart of the CORE's global-z-scored multi-channel measured-attribute
vectors over the relational graph (core anchored, non-core start at 0). reach(probe)=1 iff that coordinate ALIGNS with
the probe's OWN true (held-out) global-z-scored attribute vector above SIM_FLOOR (cosine over co-present channels;
MIN_REACH_CHANNELS=3 required else the probe is a NO-COVERAGE flag, not counted). A nan/zero coordinate (no diffusion
mass reached the probe = no relational path to the core) = reach 0, the strongest form of non-spanning. per-domain reach
= fraction of that domain's covered probes that reach.

Independence gate (over the grounded CORE channels): marginal-correlation greedy pruning (anchor=concreteness; add a
channel iff it has variance AND max |r| with every selected channel < REDUNDANT_R 0.70). >=2 non-redundant channels
required else HARD_FAIL_CHANNELS_NOT_INDEPENDENT.

## Arms / controls

- MECHANISM_CORE_GROUNDED: core-grounded-attr diffusion -> probe coordinate (the reach mechanism).
- SCRAMBLED_CORE (values-dependence ablation): core attribute rows PERMUTED across core nodes, SAME relations, re-diffused.
  Aggregate scrambled reach must NOT ground (values-dependent = grounding is real, not a structural artifact).
- RELATIONAL_ONLY_F_A: structural spectral geometry (no exterior grounding) -- reported diagnostic + distinct arm sig.
- NARROW-CORE must-fail control (density != spanning): a core of ONLY high-concreteness (Conc.M >= 4.0) PHYSICAL concepts
  (NSM logical/abstract primes + low-concreteness molecules DROPPED). It MUST FAIL grounding-reach on the abstract /
  emotional / mathematical domains (it lacks both the relations INTO those regions and the attribute dimensions they load
  on) while still reaching PHYSICAL probes.

## Pre-registered bands (numeric; picked BEFORE the run; deflated per the fusion-FULL 5/7-gate analogy)

SIM_FLOOR=0.30 (per-probe grounded-vs-true cosine; random S-dim alignment has E[cos]~0, std~1/sqrt(S), so 0.30 separates
real from null), MIN_REACH_CHANNELS=3, REACH_FLOOR=0.60 (per-domain), AGG_FLOOR=0.70 (aggregate), NARROW_COLLAPSE=0.40,
SCRAMBLE_MAX=0.40, REDUNDANT_R=0.70, HOPS=2, DIM=32, CONS_PASSES=6, CONS_ALPHA=0.25.

### SPAN_HARD_PASS (core SPANS meaning-space; ALL must hold)
every one of the 6 domains reaches REACH_FLOOR (0.60) AND aggregate >= AGG_FLOOR (0.70) AND the controls fire:
narrow-core reach on {ABSTRACT,EMOTIONAL,MATHEMATICAL} all <= NARROW_COLLAPSE (0.40) AND narrow PHYSICAL reach >=
REACH_FLOOR AND scrambled aggregate reach <= SCRAMBLE_MAX (0.40).

### SPAN_FAIL_MISSING_DIMENSION (fixable; expand the core)
1-2 domains below REACH_FLOOR while >=3 pass comfortably -> names the missing dimension; ACTION = add a channel/relation
donor for that dimension and re-run (structural, falsifiable expand-the-core signal, NOT a mechanism failure).

### SPAN_FAIL_MECHANISM (decoder wall; pause core-expansion)
>=4 of 6 domains below REACH_FLOOR (roughly uniform) -> reproduces the loop-closer grounding-doesnt-chain negative; the
bottleneck is the decoder/inference mechanism, not core span.

### HARD_FAIL_CONTROL_VACUOUS
the narrow-core must-fail control did NOT collapse OR narrow physical did not reach OR the scrambled control grounded ->
the reach test cannot certify it detects non-spanning; the spanning verdict is untrustworthy.

### MIDDLE_BAND
3 domains below floor, or controls ambiguous -> investigate before scaling.

## Self-test (SELFTEST_PASS; LIGHT local gate; MEASURED)

Planted 6-domain latent space (6 orthogonal domain-dims). MEASURED@data/exp_spanning_grounded_core_reach_v1_selftest/
metrics.json (run_mode=self_test, elapsed 0.067s):
- (a) SPANNING planted core reaches all 6 domains: per-domain reach {PHYSICAL 1.0, ABSTRACT 1.0, EMOTIONAL 0.938,
  MATHEMATICAL 1.0, SOCIAL 1.0, TEMPORAL 0.812}, aggregate 0.958 -> the reach discriminator FIRES.
- (b) NARROW (physical-only) planted core: PHYSICAL 0.938 (reaches) but ABSTRACT/EMOTIONAL/MATHEMATICAL/SOCIAL/TEMPORAL
  all 0.0 -> the density!=spanning must-fail control FIRES (narrow_missing_fail=True, narrow_phys_ok=True).
- (c) SCRAMBLED core does NOT ground: in-run scrambled aggregate 0.281 (<= SCRAMBLE_MAX 0.40, and < spanning - 0.15).
- arms differ (>=3 distinct arm signatures). st_ok=True.

This plants the FULL reach logic at small n = discriminator-survives-scale evidence (per-domain reach fraction is
scale-invariant in expectation; Path C planted-preview + Path B analytical).

## Two design bugs the self-test CAUGHT before dispatch (honesty log)

1. Structural relational-only baseline was too strong in the clean planted graph (structure alone determined attributes)
   -> the reach gate never fired; switched the reach readout to grounded-coordinate-vs-true-attribute COSINE with the
   SCRAMBLED-core and NARROW-core contrasts as the load-bearing controls.
2. Per-core z-scoring blew up noise on the near-constant channels of the homogeneous narrow core -> narrow PHYSICAL failed
   spuriously; switched to GLOBAL z-scoring (stable across cores), and treat a zero/unreached coordinate as reach=0 (not
   a silent drop). Both are calibration corrections, not threshold tuning; the bands were fixed before and unchanged.

## SCHEMA-VET

cell_chunked: false (single graph; seeds cheap, per-seed loop with cardinality-breach guard); start_marker_written: true;
crash_diagnostic_present: true (Exception -> CELL_CRASHED metrics + traceback; SystemExit/KeyboardInterrupt re-raised);
final_metrics_atomicity: tmp_replace (write_metrics + os.replace; write_partial per seed); arms_differ_verified: true
(>=3 distinct arm sigs asserted per seed); except SystemExit before except Exception (no bare/BaseException; grep-gate
clean); crlb: per-probe cosine chance ~0 (THEORETICAL), SIM_FLOOR 0.30 strictly above the null band, HARD_PASS floors
strictly above; baseline_in_band: NARROW core drops reach BELOW floor in the missing domains by construction + scrambled
collapses (not saturated); discriminator-survives-scale: planted self-test fires reach + narrow must-fail + scramble at
full logic; cardinality_ok: EXPECTED_N_UNITS=n_seeds (per-seed arms-differ + cardinality-breach guard);
calibration_check: default_ok_for_this_regime -- SIM_FLOOR/REACH_FLOOR/NARROW_COLLAPSE/SCRAMBLE_MAX are PRINCIPLED
(random-alignment null / deflated fusion-FULL analogy), fixed before the run; engine CONS_* inherited from the validated
a519 engine; progress_logging: print_flush_true (all _log flush=True; MANDATORY as FULL timeout >= 1800s);
sweep_alignment_verdict: N/A (no parameter sweep); discriminating_fraction: N/A (per-domain reach, not a sweep);
composition_edges: core-grounded-attr -> diffusion-with-restart -> probe coordinate (SHAPE_MATCH: engine consumes
[n,d] anchors + edge lists directly); positive_control: SPANNING planted core reaches all 6 domains (reproduces the
reach mechanism at the planted regime); functional_requirements: (i) assemble a span-complete core (NSM+kernel+Lancaster
union), (ii) ground each core concept multi-channel (norm join; no-coverage flagged), (iii) wire cross-cutting relations
(CSKG spine), (iv) measure per-domain reach (diffusion+cosine), (v) detect non-spanning (narrow must-fail) + fake-grounding
(scramble) -- each decomposed + mapped to a validated primitive. Data-dependency: cell self-acquires 4 norm files + CSKG
via curl (validated) else HARD_FAIL_DATA_MISSING.

## Compute architecture

class (a), CPU-fast eval; DOMINANT cost = the one-time streaming parse of the ~6M-edge CSKG TSV (CPU/IO-bound; gzip
112MB) then dense diffusion-with-restart (dense [n,n]@[n,DIM], n capped 6000) x 6 passes x arms x 5 seeds x {spanning,
narrow} cores -> seconds/seed on CPU (per the fusion cell's same-regime measurement; k-core note did the full 2.1M-node
decomposition on CPU). Storage SHARDED (each concept its own grounded vector). SELF-TEST is planted-only (0.067s) and
runs LOCAL. The FULL CSKG assembly + 6-domain reach eval is INTENSIVE and routes to REMOTE (remote_cpu_queue; graph parse
dominates; GPU optional). SMOKE-ONLY-LOCAL lock honored: nothing intensive runs local.

## Config

FULL: seeds=[7,13,17,23,29], source=cskg, n_kernel=1500, max_nodes=6000. SMOKE: seeds=[7,13], source=cn (local
ConceptNet), n_kernel=250, max_nodes=3000. SELFTEST: planted worlds (local, 0.067s, SELFTEST_PASS).
FULL timeout: 3600s -- covers worst-case CSKG self-acquire (curl --max-time 1200 if not cached) + ~3min streaming parse
of 6M edges + ~5min eval (5 seeds x 2 cores) + margin. progress_logging=print_flush_true (per-seed + per-stage flush) as
the FULL timeout >= 1800s heartbeat-mandate threshold.
