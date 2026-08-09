# exp_dev hand-off — research: VSA script/schema representation, chaining, capacity

**Filed-by:** research sub-agent, 2026-08-09.
**Trigger:** `notes/research_vsa_script_representation_chaining_2026-08-09.md` — director-assigned
"how-to-represent" drill for the grounded self-growing narrative-comprehension program: design how
grounded SCRIPTS/SCHEMAS (trigger->consequent event structures with roles) should be represented as FHRR
hypervectors to support partial matching, multi-step chaining, composition, and capacity at scale. Finding:
this is >80% REUSE of already-owned, mostly already-VET-confirmed organs
(`hdlab.situation_model_accumulate.RelationRegister`/`CausalLinkRegister`/`AccumulateRegister`,
`hdlab.lexical_similarity.concept_vector`, `hdlab.sequence_memory.SequenceMatrix.chain_predict`,
`hdlab.cleanup_family`), plus a small number of genuine builds (an FHRR port of `hdlab.event_bundle.
EventBundleCodec`'s bipolar role-slot event pattern; a real/complex adapter for `hdlab.schema_exemplar_bayes.
SchemaExemplarBayesIndex`; resonator-network multi-factor decode, deferred until measured-necessary; the
chunking/nesting calling pattern). Literature (3 fresh lit-scan lanes, mostly full-text-verified) gives
concrete capacity formulas, a confirmed brain analog (Tolman-Eichenbaum Machine + Baldassano et al. 2018
narrative-schema fMRI), and one load-bearing NEW constraint (unbinding error compounds multiplicatively per
chaining hop) not previously in the KB.

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed regardless
of pause state per research-role convention — it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable bands,
context pointers) — exp_dev owns exact implementation (which script-role vocabulary size to start with,
exact toy-corpus construction, exact cell structure, seeds).

## Anchor candidates (rank-ordered)

### 1. `exp_script_representation_partial_match_capacity_v1` (primary, do this first — cheapest, CPU-only, no new corpus)

**Anchor pointer:** research note's "Cheap decisive test" section (items 1-3) + section 1a/1b (the
TYPE-vs-INSTANCE representation design) + section 5b (the capacity question this test measures for the
first time on script-specific content, rather than the field's generic random-vector curve).

**Substrate-product reading:** if this HARD-PASSes, it validates that the existing
`RelationRegister.bind_filler` pattern (already built for the 2-role GOAL/OUTCOME case) generalizes cleanly
to a richer script-role vocabulary and an open script-TYPE codebook — the direct prerequisite for every
downstream script-representation build (chaining, chunking, resonator decode) the parent note lays out. It
also produces the FIRST script-specific capacity number this whole research arc has been extrapolating
without (the 08-06 sibling note's own Prediction 7 flagged this gap and it has not yet been run).

**Tier hint:** load-bearing gate — a HARD-FAIL here means direct bind/bundle/cleanup at N=1024 cannot
support even toy-scale script codebooks, forcing either bigger N or the resonator-decode build (anchor #3
below) BEFORE any further script work, not after.

**Why now:** cheapest possible test — reuses `hdlab.goal_outcome_relation`'s EXISTING 6 hand-authored pools
(`COGNITION_GOAL_POOL`/`SKILL_GOAL_VERB_POOL`/`INFO_EXCHANGE_POOL`/`ERRAND_POOL`/`SKILL_TRAIN_POOL`, plus one
CONFLICT/preclusion type from `quality_relation`'s engagement axis) as the seed TRIGGER-role vocabularies —
no fresh hand-authorship, no new corpus, no gradient training, CPU-only.

**Design (from the research note, exp_dev owns implementation details):**
1. Define a small `SCRIPT_ROLE_VOCAB` (research note section 1a: `TRIGGER_ROLE`, `CONSEQUENT_ROLE`, at
   minimum; `AGENT_ROLE`/`PATIENT_ROLE` optional for this first pass) as a shared, seeded
   `unit_phase_vec`-per-role dict, following `CausalLinkRegister`'s exact class-extension pattern on
   `AccumulateRegister`.
2. Construct 5-10 script-TYPE codebook entries (section 1b) from the existing 6 pools; for each, build a
   canonical script-INSTANCE vector via `RelationRegister.bind_filler`-style construction (TRIGGER_ROLE +
   CONSEQUENT_ROLE bound to `lexical_similarity.concept_vector` fillers drawn from the pool).
3. Partial-match test (research note section 2): given ONLY a TRIGGER-role cue, score
   `cleanup_family.iterative_attractor` / `k_NN_lookup` against the script-TYPE codebook; report top-1
   accuracy at N=1024.
4. Capacity sweep: repeat step 3 at 5 / 10 / 20 / 50 script types to find the first measured degradation
   point (research note section 5b's open question).
5. Scramble control (mandatory, per standing pairscramble-must-collapse discipline): shuffle role<->filler
   pairing within each type; accuracy MUST collapse toward chance (1/n_types).

**Pre-registered bands (from the research note, verbatim, Prediction 1):**
- **HARD-PASS**: partial-TRIGGER-cue cleanup-argmax correctly identifies the source script TYPE at >=90%
  for at least 15 script types at N=1024 (consistent with, within ~20% of, Schlegel/Neubert/Protzel's
  ~330-dim/15-item curve scaled to N=1024's headroom) **AND** the scramble control collapses to within 10%
  of chance-level (1/n_types).
- **HARD-FAIL**: accuracy is not appreciably above chance for ANY tested script-type count (5/10/20/50), OR
  the scramble control does NOT collapse (generic concept-similarity leakage, not genuine role-structure
  reading) — forces either bigger N or the resonator-decode build (anchor #3) before further script work.

### 2. `exp_sequence_matrix_script_scene_transfer_v1` (cheap, near-mechanical transfer check)

**Anchor pointer:** research note section 3a + Prediction 2.

**Substrate-product reading:** confirms (or refutes) that the ALREADY chain-grade-certified
`sequence_memory.SequenceMatrix.chain_predict` primitive (HARD_PASS at depths [1,3,5,7,10] on the c3 cell,
commit a27939c5) transfers to script-scene content without special-casing — a near-zero-risk reuse check,
not a novel-mechanism test.

**Tier hint:** confirmatory — expected PASS given P=0.55 (least-deflated prediction in the note); a
HARD-FAIL would be a genuinely surprising finding requiring its own follow-up (script-scene vectors having
different statistical properties than the c3 cell's original content).

**Design:** bind a 3-5-scene toy script sequence (e.g. REPAIR script: diagnose -> fix -> test) into
`SequenceMatrix` via `bind_sequence`; call `chain_predict(scene_1, depth=<=5, codebook=...)`; compare
recall against the c3 cell's own certified depth-5 figure.

**Pre-registered bands (Prediction 2, verbatim):**
- **HARD-PASS**: reproduces the SAME chain-grade recall profile (near-1.0 at depth<=5) the c3 cell already
  certified, no special-casing needed.
- **HARD-FAIL**: recall degrades measurably (>10%) below the c3 cell's certified depth-5 figure on
  script-scene content specifically.

### 3. `exp_recursive_goal_respawn_chain_depth_v1` (do after #1, tests the NEW multiplicative-error finding)

**Anchor pointer:** research note section 3b (recursive Goal->Attempt->Outcome->new-Goal chaining) +
section 3c/5e (the fresh lit-scan finding that unbinding error compounds MULTIPLICATIVELY per chaining hop,
not previously in the KB) + Prediction 4.

**Substrate-product reading:** this is the mechanism the task's "consequent feeds next inference" language
most directly points at — decode `CONSEQUENT_ROLE`, run the ACHIEVE/CONTRADICT queries (per the sibling
`notes/research_psych_bridging_inference_situation_models_2026-08-09.md` hand-off, NOT re-derived here),
and if unsatisfied, re-seed a fresh script lookup from the decoded consequent, recursively. If HARD-PASS,
this sets a safe default recursion-depth budget; if HARD-FAIL, it means chaining purely through decoded
vectors (without re-grounding against the original text) is unreliable past 1-2 hops, a materially
different design than section 3b currently proposes.

**Tier hint:** MEDIUM priority — depends on anchor #1 landing first (needs a working script-TYPE codebook
to chain through) and on the sibling psych-bridging hand-off's ACHIEVE/CONTRADICT queries existing (or a
stand-in placeholder for this specific smoke).

**Design:** construct a toy 3-hop goal-failure chain (goal unmet -> new goal spawned from decoded
consequent -> goal unmet again -> new goal spawned again); log per-hop verdict correctness AND
cleanup-confidence; check whether confidence decays monotonically and stays correlated with correctness.

**Pre-registered bands (Prediction 4, verbatim):**
- **HARD-PASS**: maintains >=85% correct verdicts through at least 3 recursive hops, with per-hop
  confidence monotonically informative (correlates with correctness, enabling a principled abstain
  threshold).
- **HARD-FAIL**: accuracy drops below 60% by hop 2, OR confidence is uninformative — would mean recursive
  chaining needs a per-hop re-grounding step (re-read the original text), not pure vector-chaining.

## Context pointers (files, not summaries)

- `notes/research_vsa_script_representation_chaining_2026-08-09.md` — full synthesis: sections 1
  (representation design, TYPE vs INSTANCE split, EventBundleCodec/SchemaExemplarBayes integration), 2
  (partial matching), 3 (chaining, two mechanisms), 4 (composition/chunking), 5 (four-tier capacity
  analysis), 6 (brain analog, TEM + Baldassano et al. 2018), all 4 falsifiable predictions with
  pre-registered bands.
- `hdlab/situation_model_accumulate.py` — `AccumulateRegister`, `CausalLinkRegister`, `RelationRegister`
  (the exact class-extension pattern to follow for a richer `SCRIPT_ROLE_VOCAB`; `bind_filler`/
  `decode_filler` already accept open-vocabulary content vectors, no change needed there).
- `hdlab/lexical_similarity.py` — `concept_vector`, `CONCEPT_FEATURES` (includes the literal vocabulary of
  `goal_outcome_relation`'s 6 pools already re-encoded as concept features — the seed content for anchor
  #1's script-TYPE fillers).
- `hdlab/cleanup_family.py` — `iterative_attractor`, `k_NN_lookup` (anchor #1's cleanup primitives).
- `hdlab/sequence_memory.py` — `SequenceMatrix`, `chain_predict`, `bind_sequence` (anchor #2, already
  chain-grade certified, commit a27939c5).
- `hdlab/event_bundle.py` — `EventBundleCodec` (the bipolar role-slot event pattern to PORT to FHRR per
  the research note's section 1d resolution (i); its own self-test shape — round-trip accuracy, THIN-LABEL/
  BAG-OF-ARGS baselines, `encode_scrambled_event` control — is the template for anchor #1/#2's self-tests).
- `hdlab/schema_exemplar_bayes.py` — `SchemaExemplarBayesIndex` (deferred build: real/complex adapter for
  instance-to-type induction; not required for anchors #1-3, flagged for a later cycle).
- `hdlab/goal_outcome_relation.py` — the 6 hand-authored pools (`COGNITION_GOAL_POOL` etc.) anchor #1 seeds
  its script-TYPE codebook from.
- `notes/research_psych_bridging_inference_situation_models_2026-08-09.md` +
  `notes/exp_dev_handoff_research_psych_bridging_inference_situation_models_2026-08-09.md` — the sibling
  drill anchor #3's ACHIEVE/CONTRADICT queries depend on; read before implementing anchor #3.
- `data/capability_registry.jsonl` — query before building; `situation_model_accumulate_register_organ` and
  `working_memory_multibank_K_capacity` are already registered and should be consulted, not reinvented.

## Contract section

- exp_dev owns: exact `SCRIPT_ROLE_VOCAB` size/naming for the first pass (minimum `TRIGGER_ROLE`/
  `CONSEQUENT_ROLE`; whether to include `AGENT_ROLE`/`PATIENT_ROLE` in v1), exact script-TYPE codebook
  construction details (how many canonical fillers per type), exact cell/file naming, exact seed handling,
  whether anchors #1-3 ship as one cell or three.
- Research (this hand-off + parent note) fixes: the falsifiable HARD-PASS/HARD-FAIL bands for all 3 anchors,
  the mandatory scramble control on anchor #1 (not optional — it is what makes this a genuine test of
  role-structure reading rather than generic concept-similarity), the mandatory capacity sweep (5/10/20/50
  script types) rather than a single fixed count, and the glass-box/no-LLM-at-inference invariant — every
  organ named above is already owned; nothing in these tests may introduce a trained/opaque external
  component.
- Honest scope note (carry into the pre-reg): anchor #1's script-TYPE codebook is hand-seeded from existing
  pools, not yet grown via the acquisition loop (`SchemaExemplarBayesIndex`-based induction is a DEFERRED,
  separate build, section 1d of the parent note) — do not overclaim this test validates open-ended script
  discovery; it validates the representation/capacity mechanism on a fixed, small, hand-seeded codebook.

## Autonomy declaration

exp_dev decides the exact `SCRIPT_ROLE_VOCAB` composition for v1, exact script-TYPE codebook construction,
exact cell/file naming and structure, and whether anchors #1-3 ship together or separately. The falsifiable
bands, the mandatory scramble control, the mandatory capacity sweep, and the glass-box/no-LLM invariant are
NOT exp_dev's to loosen or drop without flagging the change explicitly in the pre-reg.
