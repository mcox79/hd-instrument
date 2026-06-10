# exp_dev hand-off -- research: embodied cognition NOW shard overclaim retraction (2x)

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_embodied_cognition_now_shard_2x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

A prior claim that "NOW shard with sensorimotor state solves embodiment" has been
identified as an overclaim and retracted. The retraction is not contested -- it is
a direct reading of Lakoff/Johnson/Harnad/Gibson against the mechanism.

The research note establishes:
- Embodied cognition requires sensorimotor LOOPS that constitute abstract concepts,
  not passive data binding.
- Substrate lacks sensorimotor loop, body schemas, affordance computation, and
  developmental sensorimotor history.
- Substrate CAN do: multi-modal binding, schema-tagged retrieval, affordance-triple
  storage, and (via integration) serve as memory layer in genuinely embodied systems.
- Five honest engineering anchors are identified and pre-reg'd.

The highest-priority anchor is IMAGE-SCHEMA-CODEBOOK -- it is the cheapest test of
whether schema-structured retrieval is achievable, and it gates the METAPHOR-BINDING
anchor that follows.

All five anchors are CPU-laptop tier. No cloud dispatch needed.

---

## Anchor Candidates (rank-ordered by P_actionable x prerequisite order)

### 1. IMAGE-SCHEMA-CODEBOOK (HIGHEST PRIORITY -- runs first)

Anchor pointer: EMBOD-SCHEMA-1 (new; not yet queued)
Substrate-product reading: Tests whether substrate can support schema-conditioned
  retrieval over a codebook of 10 canonical image schemas (CONTAINER, PATH, BALANCE,
  FORCE, LINK, NEAR-FAR, VERTICALITY, FULL-EMPTY, PART-WHOLE, CENTER-PERIPHERY).
  If precision >= 0.70, schema-structured retrieval is viable as a substrate capability
  and METAPHOR-BINDING is worth running. If precision < 0.45, the schema encoding
  methodology needs redesign before further anchors.
Tier hint: CPU laptop; estimated 2-4 hr wall; pure substrate retrieval, no LLM fine-tuning
Why-now: Cheapest gate for all embodiment-adjacent anchors. Runs first.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: Schema-conditioned precision@5 >= 0.70 on 10-schema, 200-item held-out set
  HARD-FAIL: Precision@5 < 0.45 (chance-level for 10-class schema classification)
  MID-BAND: Precision@5 in [0.45, 0.70] -- schema boundary refinement needed

Data required: Build 200 short sentences (20 per schema) labeled by schema type.
  Tag and store in substrate. Evaluate held-out 100 items with schema-conditioned queries.
  Schema definitions: CONTAINER (bounded inclusion), PATH (source-trajectory-goal),
  BALANCE (bilateral symmetry / equilibrium), FORCE (exertion-resistance-result),
  LINK (connection-separation), NEAR-FAR (proximity relative to agent), VERTICALITY
  (up-down orientation), FULL-EMPTY (degree of containment), PART-WHOLE (mereology),
  CENTER-PERIPHERY (focal vs. peripheral).

### 2. METAPHOR-BINDING (prerequisite: IMAGE-SCHEMA-CODEBOOK HARD-PASS or MID-BAND)

Anchor pointer: EMBOD-METAPHOR-2 (new; not yet queued)
Substrate-product reading: Tests whether binding conceptual metaphor structure (UP =
  POSITIVE-OUTCOME, WARMTH = AFFILIATION, CONTAINER = CATEGORY) enables cross-domain
  retrieval transfer. Queries in the abstract target domain retrieve items from the
  concrete source domain via the shared schema vector.
Tier hint: CPU laptop; estimated 2-4 hr wall; depends on schema codebook from anchor 1
Why-now: Second in the schema-retrieval sequence. Only valuable if anchor 1 passes.

Pre-reg bands:
  HARD-PASS: Metaphor-mediated recall@5 >= 0.60 on 50 test pairs spanning
             3+ source domains (spatial UP, thermal WARMTH, spatial CONTAINER)
  HARD-FAIL: recall@5 < 0.30 (no metaphor transfer above chance)
  MID-BAND: recall@5 in [0.30, 0.60] -- metaphor transfer is schema-specific; identify
            which source domains transfer and which do not

### 3. SENSOR-SYMBOL-CO-OCCURRENCE (independent of 1 and 2)

Anchor pointer: EMBOD-COOCCUR-3 (new; not yet queued)
Substrate-product reading: Formalizes the existing PP-257 cross-modal binding result
  as a retrieval benchmark. Populates substrate with (sensor reading, symbolic label,
  context) triples across 3 modalities. Measures cross-modal recall@10 vs. single-
  modality recall@10 on matched queries.
Tier hint: CPU laptop; estimated 1-3 hr wall; uses existing multi-modal pipeline
Why-now: Independent of anchors 1-2. Provides honest benchmark for the multi-modal
  binding claim that replaces the retracted embodiment claim.

Pre-reg bands:
  HARD-PASS: Cross-modal recall@10 >= 0.75 AND single-modal recall@10 < 0.60
             (multi-modal binding provides measurable retrieval advantage)
  HARD-FAIL: Cross-modal recall@10 <= single-modal recall@10 + 0.05
             (binding provides no advantage; PP-257 result may be task-specific)
  MID-BAND: Cross-modal improves by [0.05, 0.15] over single-modal

### 4. AFFORDANCE-REPRESENTATION (independent; runs after 1 or in parallel)

Anchor pointer: EMBOD-AFFORD-4 (new; not yet queued)
Substrate-product reading: Stores explicit (object, action-type, agent-type) triples
  as structured vectors. Tests whether task-planning queries (given object-context,
  retrieve applicable actions) return appropriate action-type items at recall >= 0.65
  on a 100-item held-out set with 10-class action taxonomy.
Tier hint: CPU laptop; estimated 2-4 hr wall; explicit triple construction + retrieval
Why-now: Independent of schema anchors. Useful for robotics integration path. Provides
  an honest, achievable affordance-adjacent capability without the Gibson overclaim.

Pre-reg bands:
  HARD-PASS: Action-retrieval recall@5 >= 0.65 given object-context queries
  HARD-FAIL: recall@5 < 0.35 (chance for 10-class action taxonomy)
  MID-BAND: recall@5 in [0.35, 0.65] -- action retrieval requires finer context encoding

### 5. HYBRID-ROBOTICS-SUBSTRATE (long-horizon; requires robotics platform)

Anchor pointer: EMBOD-ROBOT-5 (new; not yet queued)
Substrate-product reading: Integration study connecting a robotic simulation (or physical
  platform) providing sensorimotor data to the substrate as the memory layer. The NOW
  shard holds current sensorimotor state (joint angles, contact forces, proprioception).
  Tests whether substrate-mediated episodic memory improves task success rate on repeated-
  context navigation vs. no-memory baseline.
Tier hint: Simulation preferred; physical robot if available; 4-8 hr wall for simulation
  setup + 20-trial evaluation. Requires robotics simulation environment (e.g., PyBullet,
  MuJoCo, or similar).
Why-now: The ONLY anchor that reaches genuine sensorimotor loop territory. Anchors 1-4
  are multi-modal binding tests; this is the actual embodied system test. Low priority
  until anchors 1-4 are evaluated -- do not block on this.

Pre-reg bands:
  HARD-PASS: Task success rate >= 0.80 vs. no-memory baseline <= 0.40 on 20-trial
             repeated environment (substrate memory provides substantial navigation aid)
  HARD-FAIL: Task success rate improvement <= 0.10 over no-memory baseline
             (substrate-as-memory provides no benefit in sensorimotor task context)
  MID-BAND: Improvement in [0.10, 0.40] (memory helps but is not constitutive of
            navigation strategy -- partial result, worth continuing)

---

## Strategic context for exp_dev

The retraction is not a capability loss -- it is a scope correction. The substrate
does not lose any existing capability. The change is:

  OLD CLAIM: "NOW shard with sensorimotor state implements embodied cognition"
  NEW CLAIM: "Substrate is multi-modal associative memory suitable for integration
              into embodied systems"

The five anchors above build the honest version of this claim empirically. Anchors 1-3
are the near-term priority (IMAGE-SCHEMA-CODEBOOK -> METAPHOR-BINDING -> SENSOR-SYMBOL).
Anchor 4 (AFFORDANCE-REPRESENTATION) adds planning-adjacent utility. Anchor 5 is the
long-horizon integration test.

Do NOT reintroduce embodiment framing in experiment descriptions or results summaries.
The honest framing is "multi-modal associative memory with schema-structured retrieval."

P_deflated values (from research note):
- IMAGE-SCHEMA-CODEBOOK: 0.55
- METAPHOR-BINDING: 0.40
- SENSOR-SYMBOL-CO-OCCURRENCE: 0.60
- AFFORDANCE-REPRESENTATION: 0.50
- HYBRID-ROBOTICS-SUBSTRATE: 0.35

---

## Context pointers

- Research note (full analysis, 14 citations):
  d:/AI/hd-instrument/notes/research_drill_embodied_cognition_now_shard_2x_2026-06-10.md
- Prior multi-modal binding result (PP-257 cross-modal):
  Look in data/exp_*/metrics.json for PP-257 cross-modal runs
- Substrate capability map (multi-modal rows):
  d:/AI/hd-instrument/data/substrate_capability_map.md
- Compositional shard system (v3.0 -- independent of embodiment claim):
  d:/AI/hd-instrument/notes/research_drill_substrate_compositional_shard_system_3x_*.md

---

## Contract section

This hand-off is research-to-experiment. The 5 anchor specs above are pre-reg
recommendations. Exp_dev is responsible for:
- Validating pre-reg bands before dispatch (adjust if empirical baseline differs)
- Building the image-schema sentence dataset for anchor 1 (200 labeled sentences,
  20 per schema, 10 schemas; held-out split 100/100)
- Implementing schema-conditioned retrieval query in the substrate harness
- Assigning each anchor to the correct queue (all are CPU laptop tier)
- Writing verdict notes for each anchor per standard protocol
- Escalating any HARD-PASS on anchor 5 to orchestrator for product documentation update

## Autonomy declaration

Exp_dev may dispatch anchors 1, 3, 4 independently without orchestrator approval (all
are CPU pre-tests, low cost, low risk, no product framing changes triggered by results).
Anchor 2 requires anchor 1 HARD-PASS or MID-BAND first. Anchor 5 requires robotics
platform availability confirmation; check with orchestrator before investing in
simulation setup if not already available.

A HARD-PASS on anchor 5 that would support updating product documentation to include
embodied-system integration claims MUST be escalated to orchestrator first.
