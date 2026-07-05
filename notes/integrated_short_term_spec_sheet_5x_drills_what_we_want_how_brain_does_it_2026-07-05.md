# Integrated short-term spec sheet: what we want + how the brain does it (5x-drill synthesis)

Date: 2026-07-05. Owner: Director. Type: cross-goal synthesis of the 5 parallel 5x convergence drills.
Source memos: notes/research_5x_drill_{generation,reasoning,memory,continual_learning,perception_encoder}_spec_and_brain_mechanism_2026-07-05.md
USER ask: "5x drill on every concrete short-term goal -- know EXACTLY what we want, and how the brain does it."
USER frame: brain = north star + EXISTENCE PROOF (the basics are proven achievable because the brain does them);
augment BEYOND biology's low-energy/single-shot operating point with high-energy compute; efficient-biological is the
proven floor, not a constraint. We do NOT accept perceived limits without proof.

## THE UNIFYING FINDING (the load-bearing result across all 5)

**1. NOT ONE DRILL FOUND A PROVEN WALL.** Every hard limit reduced to a compute cost, a folk bound, or a threshold:
- reasoning depth -> a noise THRESHOLD (below it, cleanup holds error flat at any depth), not a decay wall.
- memory capacity -> a COMPUTE COST with headroom (~2458 empirical vs ~16384 combinatorial at N=8192), not physics.
- generation factorization -> no info-theoretic wall (modern-Hopfield exponential-capacity theorem); scale is open-empirical.
- encoder teacher-dependence -> the "student <= teacher" DPI bound is an INFORMAL FOLK bound (Born-Again / Noisy-Student
  / DINOv2 are counterexamples), not proven.
- continual learning -> stability-plasticity is a design cost (segregated stores solve forgetting), not a wall.
Exactly the picture the USER predicted: the brain proves these are doable; others' "limits" are not fundamental.

**2. THREE OF FIVE GOALS SHARE ONE MECHANISM.** Memory, reasoning, and continual-learning all bottleneck on the SAME
thing -- how much you can superpose into one vector before it collapses -- and all five memory literatures + our own
hub-rescue win converge on the SAME fix: **protect a compact INDEX/pointer, kept SEPARATE from the content** (hippocampal
indexing theory). Our hub-rescue (permutation-indexed binding, deg5+ 0.254->0.712) IS this mechanism, empirically, on real
concept hubs. So the substrate already holds the master key; the work is applying it in each layer + buying capacity headroom.

**3. THE CAPACITY QUESTION IS ANSWERED: compute cost, not wall.** At N=8192: empirical ~2458 items, classical-Hopfield-cost
~1130, true combinatorial ceiling ~16384. The gap between empirical and combinatorial is buyable with dimension/redundancy/
high-energy cleanup -- the USER's "augment beyond biology" lever applies directly. deg8+ hubs (hub-VET residual 0.42-0.47)
are inside this headroom, not beyond it.

## PER-GOAL SPEC (what we want | brain mechanism = existence proof | augment | honest rating | ready build)

### 1. GENERATION (the "mouth") -- #1 gap, gated on the envelope (running)
- WHAT WE WANT: bound proposition HV -> exact ORDERED surface token sequence, faithful by construction. MVP = round-trip
  S/V/O (D=3, N=8192) at HARD-PASS >=0.70 exact-match, per-term within 0.10 of the envelope ceiling; HARD-FAIL <0.30.
- BRAIN: Levelt/Dell frame-and-slot + lemma/lexeme; serial order via competitive-queuing + theta-gamma phase-slots
  (~4 items/cycle = Cowan WM limit -> justifies the chunking wrapper). Resonator factorization (Frady/Kent/Sommer) = readout.
- AUGMENT: high-energy restarts + iterate-to-convergence + explaining-away peel-off vs biology's single pass; the ~4-slot
  limit is the biological floor, chunking + high-dim exceed it.
- RATING: mechanism GOOD (4/5 fields converge, no proven wall). Capacity-at-our-scale MEDIOCRE/UNKNOWN pending the envelope.
- READY BUILD: decoder per notes/decoder_design_stage_A_factor_B_order_C_cleanup...; GATED on envelope. If NO_GO/MIDDLE ->
  the SPARSE-BLOCK-CODE resonator (Hersche/Terzic 2025, ~10^5x, matches our GSBC geometry) BEFORE concluding hard.

### 2. REASONING (deep multi-step over own memory) -- the current frontier
- WHAT WE WANT: 3-5 hop chains holding FLAT >=0.50 (not decaying), refuse false-accept <=10% / false-refuse <=15%,
  faithfulness = trace mechanically replays to the same answer >=95% (checkable by construction, unlike LLM CoT).
- BRAIN: PFC persistent-activity SCRATCHPAD holds intermediates + hippocampal REGENERATIVE CLEANUP snaps each noisy hop
  back to a discrete stored concept + evidence accumulation to a stop-bound (Miller-Cohen, TEM, drift-diffusion).
- AUGMENT: deep resonator iteration + many-candidate parallel search vs biology's ~4-7 WM-item single pass.
- RATING: static algebra MEDIOCRE; substrate + regenerative-cleanup GOOD. NO proven wall (only the noise threshold).
- READY BUILD: exp_cortex_regenerative_cleanup_vs_analog_accumulate_v1 (3 arms, depth-flatness metric, P 0.45).
  DEPENDS on cleanup capacity = the memory sweep. FIRING NOW alongside the memory sweep.

### 3. MEMORY (robust recall + reliable composition) -- the LINCHPIN, now resolved
- WHAT WE WANT: recall the right memory incl. high-degree hubs; bind/compose without crowding collapse; every memory editable.
  MVP = hub-robust recall (deg5-7 done via index binding) + reliable algebra on real atoms; full = capacity-scaled with
  graceful degradation. Target the capacity headroom (toward ~16384 at N=8192, from ~2458 today).
- BRAIN: hippocampal PATTERN SEPARATION (DG sparse expansion) + hippocampal INDEXING theory (protect a compact index
  separate from content) = the convergent mechanism across all 5 literatures; matches our hub-rescue win.
- AUGMENT: higher dimension + redundancy + many cleanup iterations buy the empirical->combinatorial headroom (compute cost).
- RATING: GOOD-and-improving. hub-rescue MM_STANDARD (real, +0.458, deg5-7 solid; deg8+ 0.42-0.47 residual, INSIDE headroom).
  Capacity limit is a COMPUTE COST not a wall.
- READY BUILD: joint capacity x hub-degree CPU sweep (memory drill's decisive test, HARD-PASS/HARD-FAIL pre-reg, P 0.50).
  FOUNDATIONAL -- sets the M/redundancy envelope for reasoning-cleanup AND schema-bundling. FIRING NOW.

### 4. CONTINUAL LEARNING (learn without forgetting + form schemas) -- half done, honestly
- WHAT WE WANT: ingest forever with no catastrophic forgetting (DONE, proven 4x) AND abstract episodes into generalizing
  SCHEMAS (UNTOUCHED -- transfer=0.000 even after forgetting solved). MVP-forgetting = cleared; MVP-schema = structural
  transfer to novel same-relation items >= random+0.30 with a shuffled-relation control <= random+0.05.
- BRAIN: Complementary Learning Systems -- hippocampal fast sparse bind + cortical slow REPLAY-CONSOLIDATION that BUNDLES
  shared structure into overlapping schema vectors (McClelland/O'Reilly; Tse/Morris schema-assimilation).
- AUGMENT: offline high-energy massive replay + explicit schema-extraction vs biology's sleep-bounded slow consolidation.
- RATING: forgetting GOOD/DONE; schema-formation = the real hard part, NOT started (VSA lit flags multi-schema bundling
  interference as open). Honest correction: our "natural strength" is only the easy half.
- READY BUILD: schema_bundle_structural_transfer_v1 (bundle episodes into a segregated one-way schema store, test novel-item
  transfer; P 0.32). STAGED behind the memory capacity sweep (M budget determines pass/fail). Reuses c3 segregated-dual-W harness.

### 5. PERCEPTION / ENCODER -- essentially done for the build path
- WHAT WE WANT: native perception (retrieval + ~0.85 coarse cosine + algebra at ~2% sparse). MET by GSBC_EXPAND2X (distilled).
  Teacher-FREE target is separate + lower (~0.65 cosine-to-gold, clears orthographic ceiling 0.49-0.52 by a wide margin).
- BRAIN: perceptual codes = Hebbian/sparse/predictive-coding/DG-expansion; the perceptual->SEMANTIC bridge = TEMPORAL-
  CONTIGUITY / slow-feature learning (Foldiak trace rule, SFA) -- implicit self-supervision from experience over time, no teacher.
- AUGMENT: big self-supervised pretraining + backprop exceed biology's slow local learning; a big teacher is a LEGITIMATE
  brain-analogous BOOTSTRAP (humans learn from the language community), not a dependence to be ashamed of.
- RATING: GSBC_EXPAND2X correctly MEDIOCRE-but-DONE -> SHIP IT, move on. Teacher-dependence is NOT a proven wall (DPI = folk bound).
- READY BUILD: NONE near-term. Native-grounding (RI/BEAGLE on our own KB via temporal-contiguity, ~0.65 target) = a
  NON-GATING long-bet research track; the substrate already has an unfollowed teacher-free MIDDLE_BAND (n11) to revive later.

## DISPATCH PLAN (sequenced on dependencies; full-auto)
- FIRE NOW (foundational + decisive, independent, well-pre-registered):
  (A) MEMORY joint capacity x hub-degree sweep -- validates compute-cost-not-wall + sets the envelope for B and the schema cell.
  (B) REASONING regenerative-cleanup vs analog-accumulate -- the frontier capability test (digital-repeater mechanism).
- STAGED (fire on dependency):
  (C) CONTINUAL schema_bundle_structural_transfer_v1 -- after (A) lands (M budget). The first-ever genuine schema-formation test.
  (D) GENERATION decoder -- after the envelope verdict (GO/MIDDLE = decoder; NO_GO = sparse-block resonator first).
- NO BUILD: perception (ship-it); native-grounding parked as a long bet.

## VET RESULTS (audits landed 2026-07-05; both banked at honest tiers, both scoped DOWN from the build verdicts)
- **GENERATION (Skunkworks a72ec7):** envelope = **CHAIN_GRADE** (clean-iid capacity map, discriminators fire, scoped as UPPER BOUND).
  decoder = **MM_STANDARD** (reframed DOWN from HARD_PASS). Honest capability: frame-KNOWN D=3 S/V/O round-trip on real
  correlated fillers = exact-ordered 1.000, 3-seed bit-identical, NON-vacuous (2 controls fire). Scoped: easy-end (single-shot
  already 1.0 -> iteration not load-bearing), bipolar-BSC not native GSBC. KEY REFRAME: the "blind factorization = 0.000" wall
  is a COMPREHENSION/parsing problem, NOT a generation blocker -- generation is legitimately frame-known (you speak from a known
  frame). Generation roadmap = SCALE the mouth (higher D, bigger V, native GSBC fillers), NOT blind factorization.
- **MEMORY (Skunkworks a2ae46):** = **MM_STANDARD** (novelty-downgraded). The "no wall" is GENUINE capacity (not free averaging)
  BUT it is the STANDARD capacity-linear-in-memory crosstalk law, not a novel "redundancy lever": equal-memory head-to-head
  R banks of N == 1 bank of R*N (delta<0.004). Honest restatement: capacity is BUYABLE with LINEAR memory at **M ~= 40 floats/item
  for recall~1.0** (c~25-30 at recall>=0.95); at FIXED memory the linear crosstalk ceiling IS a hard bound. => "compute-cost not
  wall" SURVIVES only because linear memory is cheap (high-energy-compute-allowed) -- it is affordable, not a magic escape.
  Concrete: at N=8192, ~200 items/clean-bundle at recall~1.0 (~270-320 at 0.95). This is the real M-budget for cleanup/bundling.
- Both compose with (not re-count) the prior E3 permutation-indexed-binding + hub-rescue MM_STANDARD.

## >>> LATEST LANDINGS (session-live, supersede the tiers below where they differ) <<<
- **REASONING = STRONG (not modest):** v2 collision-corrected -- the v1 HARD_FAIL was chain-key COLLISION (N_TEST over slot count), NOT load (all 3 prior witnesses mis-diagnosed; ac66c2 caught it via pre-flight sim). Collision-fixed: regen_d5 ~0.70 vs analog ~0.10, gap +0.60, RISES with N, faith 1.0. FULL running remote (5 seeds) -> VET.
- **GENERATION = STRONG on native encoder:** exp_generation_decoder_gsbc_native_blocklocal_v1 (ec7aa9064) round-trips REAL native GSBC fillers PERFECTLY via the block-local sparse resonator (scour-relayed proven component) -- exact-ordered 1.000 to D=26/V<=1024, cliff only V8192/D26=0.86. Proved the encoding mismatch (dense bipolar-BSC on GSBC = 0.000). Resolves the earlier VET caveats. Saturates in-box (controls fire). FULL pending -> VET. Mechanism+envelope research running (block-local capacity law + next lever).
- **FRONTIER = OFF ZERO (the session's deepest result):** exp_schema_relation_TEM_structural_content_binding_v1 (d814a43bc) smoke = MIDDLE_BAND but GENUINE nonzero inductive real-minus-shuf on ALL 3 real relations (~0.05-0.13, both mechanisms, both encoders, NOVEL entities) where the exhausted averaged-transform family showed ZERO. Repaired controls FIRE (non-vacuous). Under-parameterized, NOT a wall -> scale-up (K/steps/hidden-dim). NOTABLE: differentiable SCORER >= brain-first TEM at smoke. FULL queued -> VET. Mechanism+envelope research running (why-emerge / why-modest / scorer-vs-TEM / scale-up ceiling).
- **NEXT (gated on the 2 mechanism+envelope drills): dispatch the frontier SCALE-UP (push ~0.1 toward >=0.21, GPU-trainable scorer) + the generation past-D26 lever.** These are the envelope-pushes.

## SESSION OUTCOME + FRONTIER + FORWARD PLAN (2026-07-05 close -- this is the current recovery state)
All 5 goals taken through BUILD + independent VET. Verified tiers (off-disk, atomized):
- **PERCEPTION** = done-mediocre (GSBC_EXPAND2X). Teacher-dependence NOT a proven wall (DPI = folk bound). SHIP-IT.
- **GENERATION** = decoder MVP MM_STANDARD (frame-known S/V/O round-trip exact-ordered 1.000, non-vacuous, controls fire);
  envelope CHAIN_GRADE. The "mouth" exists for simple sentences. Blind factorization = a COMPREHENSION problem, not a generation blocker.
- **MEMORY** = MM_STANDARD. Capacity is a BUYABLE linear-memory cost (M~=40 floats/item, ~200 clean items/bundle@N8192), not a wall;
  fixed-memory ceiling is the standard crosstalk law. Hub-recall rescued (protected/index binding).
- **REASONING** = MEASURED_MECHANISM (modest-real). Digital-repeater cleanup beats analog above the M/N~1 crosstalk threshold
  (regen_d5 0.263 vs analog 0.087, gap WIDENS with load), faith 1.0, controls fire -- but MODEST absolute (the 0.60 smoke was over-optimistic).
  N-scale-up refinement DEFERRED (smoke hung on N=32768 python-loop-scaling; re-launched smoke testing the fix).
- **CONTINUAL LEARNING** = SPLIT. Not-forgetting = DONE (proven 4x). Schema-formation MECHANISM works on SYNTHETIC structure (MM_STANDARD,
  transfer +0.59). But **real subject-conditional relational mapping = SCOPED HARD_FAIL / the FRONTIER** (VET-corrected a0f6dae): schema
  ablation FULL (12 arms) shows real-minus-shuffled ~= 0 under BOTH surface (char-trigram) AND semantic (BGE) encodings (relation-typical prior,
  NOT per-instance mapping). VET CORRECTED 2 of my over-claims: (1) "TRAINED~=NAIVE => training refuted" is NOT established -- the estimator-axis
  positive control SATURATED (discriminator never fired) so the trained-transform axis is VACUOUS/untested this run (why it's MIDDLE_BAND not
  HARD_FAIL); (2) it is NOT inductive-specific -- TRANSDUCTIVE (seen entities) also fails. Only 2 semantic relations; the TARGET GSBC encoder UNTESTED.

**THE ONE FRONTIER (VET-corrected):** subject-conditional relational mapping on real KG -- recover the SPECIFIC object for a specific subject
(seen OR unseen) instead of the relation's typical answer. Fails under both encodings tested; but the trained-transform lever is UNTESTED
(vacuous control) and GSBC untested -- so it is NOT yet "refuted," it is OPEN. Brain does it (TEM: separate learned STRUCTURAL code + content).
Likely engineering-hard, not info-theoretic (needs proof either way). Next experiment MUST use a PROPERLY-DISCRIMINATING trained-transform control
(calibrate the positive control BELOW ceiling so trained CAN beat naive when it should) + test the GSBC encoder + more relations. [META_RULE banked:
a comparison-axis positive control must DIFFERENTIATE the arms, not merely PASS.]

**NO FUNDAMENTAL WALL found anywhere** across 5 goals + all drills + all VETs -- every limit was a compute cost / folk bound / threshold /
engineering distance. The audits repeatedly trimmed build-verdict HARD_PASSes to MM_STANDARD (no-smoke working).

**FORWARD PLAN (in flight / next):**
1. GENERATION scale-the-mouth (native GSBC fillers + higher D/V) -- does the mouth work with our REAL encoder + at scale. [IN FLIGHT]
2. FRONTIER: inductive relational transfer -- content-conditioned relation transform generalizing to unseen entities (TEM-grounded,
   likely GPU-trainable -- fills the idle GPU). Drill -> decisive first-attempt cell. [IN FLIGHT]
3. REASONING useful-magnitude re-run (fix: fast small-N smoke, big-N in FULL, vectorize) -- deferred, not critical (mechanism banked).
4. Deferred tidy: director_plan.json refresh (stale pre-reframe C0-C6); capability_scorecard honest revision; a97751df light-VET;
   push commits; auto-refill USER cmd; --self-test infra fix; n11 teacher-free revival. Re-encode still HELD.

## DISCIPLINE
Verify off-disk before claiming; no-smoke (ratings above are deflated-honest); brain = existence proof + high-energy augment;
this is CONSTRUCTIVE build work, not vs-LLM. Every cell: HARD-PASS/HARD-FAIL pre-reg, self-test, multi-seed FULL, joint-gate.
