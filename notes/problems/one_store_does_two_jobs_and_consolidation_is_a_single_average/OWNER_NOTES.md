---
owner_verdict: DONE
---

=====================================================================================
SUBMISSION -- SOLVER PROBLEM: one_store_does_two_jobs_and_consolidation_is_a_single_average
Status: PARTIAL   (awaiting owner_verdict: DONE -> strategy re-verify + integration)
Reverify (scaffold-free, writes nothing landed):
  .venv/Scripts/python.exe verification/test_consolidation_real_reading.py   -> WITNESS PASS (8 tests)
Ledger --check: 0 malformed. All writes in experiments/, verification/, data/, and the
problem folder. hdlab/ UNTOUCHED (board Q111) -- proposed diff below is NOT landed.
This is the WRITE/REPLAY half of the memory architecture; p2 was the READ half. Coordinate.
=====================================================================================

THE PROBLEM (plain)
  The brain keeps two memory systems separate on purpose: a FAST one that binds a single
  experience in one shot (hippocampus) and a SLOW one that folds it into general knowledge
  over time by REPLAYING it selectively during sleep (cortex). We use ONE store and a single
  averaging step -- ungated, un-interleaved, un-prioritised. The faithful replay engine
  (continual.py) was built and left unwired. Question: does brain-faithful consolidation
  (fast/slow + selective, schema-gated, interleaved replay) actually beat the single average
  at learning NEW from reading WITHOUT catastrophically forgetting OLD?

THE BAR (verbatim, PROBLEM.md sec 7)
  "On an OLD-vs-NEW interleaved-retention task from real reading ... brain-faithful
  consolidation (fast/slow separation + SELECTIVE, SCHEMA-GATED, INTERLEAVED replay) must beat
  the single-average consolidation CI-separated over the strongest floor's UPPER bound on JOINT
  old+new retention, with the info-free twin (RANDOM replay selection, same replay budget)
  LOSING CI-separated, CI half-width + null p95 reported. Sweep the parameters; do not adopt a number."

-------------------------------------------------------------------------------------
THE VERDICT: the answer depends on the CORTICAL CODE, and making the code brain-faithful FLIPS it
-------------------------------------------------------------------------------------
Real simplewiki reading (era fixed; 3 seeds; ~128 OLD + 128 NEW concepts; hit@1, self-masked
codebook ranking; bootstrap 95% CI). Two instruments: an overlapping-linear cortex (v1) and a
sparse k-WTA-hidden cortex (v2, the brain-faithful architecture).

  (A) DENSE / overlapping cortex (v1):
      - Uniform INTERLEAVED replay PREVENTS catastrophic forgetting, CI-separated on real text:
        SEQUENTIAL OLD 0.076 [.049,.104] -> INTERLEAVED 0.349 [.302,.396]. (First demo on real reading.)
      - SELECTIVE replay does NOT beat the uniform twin at ANY budget (scarcity sweep 0.1->1.0),
        and SCHEMA "wins" only by HOARDING old (NEW crushed to 0.083). Zero-sum in an overlapping store.

  (B) SPARSE PATTERN-SEPARATED cortex (v2 -- the brain's architecture):
      - Sparse coding SHARPLY reduces interference (dose-response: SEQUENTIAL 0.229->0.557 as sparsity
        rises); an EQUAL-CAPACITY dense-hidden control COLLAPSES to 0.000 -> sparsity, not capacity, is causal.
      - SELECTIVE interleaved replay NOW BEATS the uniform info-free twin CI-separated where retention
        isn't already saturated: keep=0.01 SELECTIVE 0.779 [.734,.820] vs uniform 0.680 [.630,.727];
        keep=0.02 0.977 vs 0.896. -> THE BRIEF'S MECHANISM IS MET, but ONLY in the sparse-code regime.
        My earlier v1 "selection isn't a lever" was an ARTIFACT of an unfaithful dense/linear cortex.

  (C) THE TRADEOFF (why one store can't do both = the problem's premise): the sparse cortex RETAINS
      (0.68-1.00) but does NOT generalise (held-out 0.02-0.05); the overlapping cortex generalises a
      little but forgets. DG neurogenesis (fresh units for new memories) pushes this to the extreme:
      retention 0.97-1.00 with NO replay, generalisation 0.02 -- it SHARPENS the tradeoff, doesn't escape it.

  (D) FORK B: the LIVE single-average store is separable-row (SEP_LOOKUP 1.000, invariant) -> it never
      forgets -> catastrophic forgetting is NOT the live binding constraint.

  (E) CONTENT WALL: generalisation is near-floor for EVERY arm and architecture (best 0.104 = the
      first-order similarity floor) -> representation/content-bound (agrees with the read-half, p2).

FLOORS
  Strongest single-average = SEP_LOOKUP (live separable store) JOINT 1.000 -- unbeatable on pure recall.
  Distributed single-average HEBBIAN_SUM 0.000 (crosstalk collapse); SEP_AVG_SIM first-order 0.181.
  Info-free twin = uniform/random-selection interleaved (dense 0.349; sparse 0.68/0.90). SEQUENTIAL
  no-replay forgetting floor 0.076 (dense). DENSE-hidden collapse control 0.000. shuffle null 0.000;
  chance 0.0027.

CONTROLS (each excludes something)
  SEQUENTIAL no-replay (forgetting floor); INTERLV_RANDOM/uniform at MATCHED budget (the bar's info-free
  twin); HEBBIAN_SUM (excludes shared-W crosstalk as the single-average); SEP_AVG_SIM (first-order sim);
  SEP_LOOKUP (excludes forgetting-on-the-live-path -> fork B); SHUFFLE null; self-mask; REPLAY-BUDGET
  SCARCITY SWEEP 0.1->1.0 (excludes 'selection null because budget=whole OLD set'); SPARSITY k-WTA sweep
  with DENSE-HIDDEN CONTROL at equal capacity -> 0.000 (excludes 'sparsity win is capacity/the extra
  layer'); INTERLV_3FACTOR (excludes 'rank-1 plasticity is why selection fails'); held-out GENERALISATION
  set (excludes 'retention == usefulness' -> exposes the tradeoff).

-------------------------------------------------------------------------------------
THE BRAIN-FOUNDATIONAL DRILL (owner-driven; four rounds, each caught a divergence)
-------------------------------------------------------------------------------------
  1. FORK B: modelled the "single average" as the LIVE op actually is (separable-row, never forgets),
     not a strawman distributed sum -> forgetting is not the live constraint.
  2. SCARCITY CONFOUND: my selection test was null by construction (budget = whole OLD set -> uniform
     and selective replay identical items). Fixed with a budget sweep.
  3. THE STORE WAS THE DIVERGENCE (decisive): "selection is zero-sum" was measured in a single-layer
     LINEAR cortex. The real cortex has a SPARSE k-WTA hidden layer that separates concepts. Building
     THAT flipped the verdict -- selective replay is a lever once codes are sparse enough. Witnessed
     both directions (wins under separable subspaces, ~zero under overlap).
  4. DG NEUROGENESIS (finest grain): fresh units for new memories -> near-perfect retention w/o replay,
     even lower generalisation -> sharpens the tradeoff. (Caveat below: real neurogenesis is double-edged.)

-------------------------------------------------------------------------------------
BRAIN-FIDELITY VERIFICATION (independent read-only literature scan -- corrected 2 over-claims)
-------------------------------------------------------------------------------------
  1. Sparse coding reduces interference: mechanism PINNED (French 1991; MMO 1995; O'Reilly 2014).
     CORRECTED: do NOT frame sparse as "beating" replay -- CLS treats them as COMPLEMENTARY (different
     jobs, different systems; no single scheme does both). van de Ven 2024: interleaving is weakest at
     INTERMEDIATE overlap (where real memories live); sparsity degrades under capacity pressure.
  2. Selective replay is representation-dependent: SUPPORTED (Schaul 2016; Rolnick 2019; van de Ven 2024;
     TD-priority can EXACERBATE interference). It is two coupled knobs (which sample x capacity).
  3. DG neurogenesis for temporal pattern separation: PINNED (Aimone 2011; Sahay 2011; Clelland 2009).
     CORRECTED: DOUBLE-EDGED -- Akers/Frankland 2014 (Science): neurogenesis also ERASES established
     memories via remodeling. My disjoint-units model omits that cost -> OVERSTATES retention.
  4. Retention/generalisation tradeoff -> two systems: PINNED (O'Reilly & McClelland 1994 "avoiding a
     trade-off"; Rolls 2013/2016).
  5. Surprise as replay priority: SUPPORTED but too narrow -- priority is a MULTI-FACTOR salience
     composite (reward, RPE, novelty, valence, recency); surprise is A valid member of an OPEN space.
  UNMODELLED (flagged, different in kind): synaptic tagging-and-capture (Frey&Morris 1997; separate organ
  D9); schema-gated consolidation RATE (Tse 2007/2011 -- schema-congruent facts skip slow interleaving;
  my SCHEMA arm modelled budget reallocation, not this).

-------------------------------------------------------------------------------------
PROPOSED hdlab CHANGE -- NOT landed (board Q111; strategy re-verifies + lands)
-------------------------------------------------------------------------------------
Ordered by evidence:
  1. PRIMARY: make the consolidated cortical code SPARSE + PATTERN-SEPARATED (k-WTA). This is the main
     interference-reducer AND what makes selective replay work at all -- the same deviation-#4 lever that
     was load-bearing on the READ half (p2). Sweep the keep fraction; do not adopt a number.
  2. SECONDARY: wire continual.replay_cycle as UNIFORM interleaved replay behind a default-off flag; allow
     a SELECTIVE (surprise-prioritized) variant ONLY in the sparse regime (it beats the twin CI-separated
     there). Do NOT add a selective scheduler to a DENSE store (zero-sum).
  3. KEEP the separable HDFactStore as the fast/episodic store -- it is already hippocampus-like (retains,
     does not generalise). Do NOT force one store to both retain and generalise; the tradeoff is real.
  4. Do NOT expect this to improve GENERALISATION on the current corpus -- content-bound; route to
     reader_meaning_channel / the read half (p2).

AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, deviation #5 / ORGAN_MAP D4)
  * D4 tested on REAL TEXT (was "untested"). Uniform interleaved replay prevents catastrophic forgetting
    CI-separated.
  * SPARSE pattern-separated coding (deviation #4) sharply reduces interference and is load-bearing on the
    WRITE as well as the read -- COMPLEMENTARY to replay (not a replacement).
  * The SELECTION FUNCTION is REGIME-DEPENDENT, not a flat negative: zero-sum in a dense/overlapping store,
    a real lever (CI-separated over the twin) in a sparse store. Corrects the surprise cell's and my own v1
    "priority can't be exploited" reading -- the missing ingredient was sparse coding, not the plasticity rule.
  * Deviation #5 reframed: "one store, single average" is not causing forgetting (fork B); the real gap is
    the retention/generalisation TRADEOFF -> the two-store CLS design + sparse coding, with generalisation
    itself content-bound.

WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST
  * Did NOT beat SEP_LOOKUP on pure retention (a perfect lookup can't be beaten on recall; sparse reaches 0.98).
  * Did NOT achieve generalisation on real reading (every architecture at/near the first-order floor).
    First thing I'd withdraw: any hope a better WRITE schedule fixes generalisation -- the wall is CONTENT.
  * The neurogenesis retention number is IDEALISED (omits the Akers-2014 remodeling/forgetting cost).

FILES
  experiments/exp_consolidation_real_reading_old_vs_new_v1.py      (overlapping-linear cortex + sweeps)
  experiments/exp_consolidation_sparse_hidden_cortex_v2.py         (sparse k-WTA cortex: flip + dense
                                                                    control + generalisation + neurogenesis)
  verification/test_consolidation_real_reading.py                  (scaffold-free witness, 8 tests, PASS)
  data/exp_consolidation_real_reading_old_vs_new_v1/{metrics.json,metrics_sweep.json}
  data/exp_consolidation_sparse_hidden_cortex_v2/metrics.json      (self-contained: flip+tradeoff+dense)
  data/exp_consolidation_sparse_hidden_cortex_v2_neurogen/metrics.json
  notes/problems/one_store_does_two_jobs_and_consolidation_is_a_single_average/{SOLVED.md,SOLVER_NOTES.md}

-------------------------------------------------------------------------------------
TLDR (plain language)
-------------------------------------------------------------------------------------
The brain keeps a fast memory and a slow memory separate and folds new learning into the slow one by
REPLAYING it. We use one store and a single averaging step. Testing this on real reading: (1) A huge part
of what stops new learning from erasing old is the CODE -- using SPARSE codes where each fact lights up its
own small set of "neurons," so learning something new barely touches the old. Dense codes erase everything;
sparse codes almost nothing. (The brain uses BOTH sparse codes and replay; they do different jobs -- I'm not
claiming one beats the other.) (2) Once codes are sparse, being CLEVER about which memories to replay
genuinely helps -- I was wrong earlier saying it didn't; that test used the wrong (dense) kind of memory. So
the brain's recipe -- sparse codes plus targeted replay -- does work. (3) The catch that explains WHY the
brain keeps two memories: sparse codes are great at REMEMBERING but useless at GENERALISING; dense codes
generalise a bit but forget. No one store does both. (4) Our current store already never forgets (it files
each fact separately), so forgetting was never our real problem. Our real problem is the same as last time:
the MEANING we store is too thin to answer new questions -- a different job to fix. I also had the
neuroscience of all this independently checked against the literature and corrected two places where I'd
overstated it.

QUESTIONS: none.

NEXT STEPS
  1. Land the ordered write-op guidance: sparse/pattern-separated cortical code (primary); uniform
     interleaved replay behind a default-off flag, selective variant only in the sparse regime; keep the
     separable fast store as-is.
  2. Route the real limit (a meaning code that GENERALISES) to reader_meaning_channel / the read half (p2).
  3. Fold the AUDIT UPDATE notes into BRAIN_FOUNDATIONAL_AUDIT.md.
  4. (Optional further fidelity, not closed) double-edged neurogenesis (Akers cost); schema-gated
     consolidation RATE; synaptic tagging-and-capture; learned sparse codes; multi-session spaced schedule.
=====================================================================================
