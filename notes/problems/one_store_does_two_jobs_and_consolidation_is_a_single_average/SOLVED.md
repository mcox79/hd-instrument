---
problem: one_store_does_two_jobs_and_consolidation_is_a_single_average
status: PARTIAL
bar: "On an OLD-vs-NEW interleaved-retention task from real reading (learn NEW facts across a session while retaining a held-out OLD set; corpus era fixed), floor recomputed on that population: brain-faithful consolidation (fast/slow separation + SELECTIVE, SCHEMA-GATED, INTERLEAVED replay) must beat the single-average consolidation CI-separated over the strongest floor's UPPER bound on JOINT old+new retention, with the info-free twin (RANDOM replay selection, same replay budget) LOSING CI-separated, CI half-width + null p95 reported. Sweep the selection / interleave parameters; do not adopt a number."
result: "Real simplewiki reading (era fixed; 3 seeds; ~128 OLD + 128 NEW concepts; hit@1, self-masked codebook, bootstrap 95% CI). THE ANSWER DEPENDS ON THE CORTICAL CODE, and getting the code brain-faithful FLIPS the selection verdict. (A) In a DENSE/overlapping cortex: uniform INTERLEAVED replay prevents catastrophic forgetting CI-separated (SEQUENTIAL OLD 0.076 [0.049,0.104] -> INTERLEAVED 0.349 [0.302,0.396]); but SELECTIVE replay does NOT beat the uniform twin at any replay budget (scarcity sweep 0.1->1.0) -- zero-sum in an overlapping store. (B) In a SPARSE PATTERN-SEPARATED cortex (k-WTA hidden, the brain-faithful architecture): sparse coding SHARPLY REDUCES catastrophic interference (SEQUENTIAL retention rises with sparsity 0.229->0.557; a DENSE-hidden control at EQUAL CAPACITY collapses to 0.000 -> sparsity, not capacity, is causal; French 1991), AND SELECTIVE interleaved replay NOW BEATS the uniform info-free twin CI-separated where retention is not already saturated (keep=0.01: 0.779 [0.734,0.820] vs uniform 0.680 [0.630,0.727]; keep=0.02: 0.977 vs 0.896). So the brief's mechanism (selective interleaved replay beats the average, twin losing) IS met -- but ONLY in the brain's sparse-code regime; the v1 negative was an artifact of an unfaithful dense/linear cortex. NOTE (CLS-correct framing, lit-verified): sparse coding and replay are COMPLEMENTARY, not competing -- sparse coding is the hippocampal-style low-interference encode, replay is the cortical structure-extraction op; the point is no single scheme does both (O'Reilly & McClelland 1994). (C) TRADEOFF: the sparse cortex RETAINS (0.68-1.00) but does NOT generalise (held-out 0.047-0.052, near floor); the overlapping cortex generalises slightly better but forgets -- so ONE store cannot do both jobs (the problem's premise). (D) FORK B: the LIVE single-average store is separable-row (SEP_LOOKUP 1.000 invariant) -> it never forgets -> catastrophic forgetting is not the live binding constraint. (E) CONTENT WALL: generalisation is low for EVERY arm/architecture (best 0.104 = first-order similarity floor) -> representation-bound."
floor: "STRONGEST single-average = SEP_LOOKUP (the LIVE separable-row store) JOINT hit@1 1.000 [1.000,1.000] -- never forgets, unbeatable on retention. Distributed single-average controls: HEBBIAN_SUM (naive shared-W sum) 0.000 (crosstalk collapse); SEP_AVG_SIM (first-order similarity read) 0.181. Info-free twin = UNIFORM/RANDOM-selection interleaved at MATCHED budget (dense OLD 0.349; sparse keep=0.01 OLD 0.680, keep=0.02 0.896). No-replay forgetting floor SEQUENTIAL (dense 0.076; sparse 0.229-0.557). DENSE-hidden collapse control 0.000. shuffle null 0.000; chance 0.0027; null p95 ~0.001."
controls: "SEQUENTIAL no-replay (forgetting floor); INTERLV_RANDOM/uniform interleaved at MATCHED budget (the bar's info-free twin); HEBBIAN_SUM distributed naive-average (excludes shared-W crosstalk as the single-average); SEP_AVG_SIM first-order similarity; SEP_LOOKUP separable live store (excludes 'forgetting bites on the live path' -> fork B); SHUFFLE null 0.000; self-mask; REPLAY-BUDGET SCARCITY SWEEP 0.1->1.0 (excludes 'selection null because budget=whole OLD set'); SPARSITY k-WTA sweep keep 0.01/0.02/0.05/0.15 with DENSE-HIDDEN CONTROL (excludes 'sparsity win is capacity or the extra layer' -- the equal-capacity dense control collapses to 0.000); INTERLV_3FACTOR neuromod error-weighted plasticity; held-out GENERALISATION set trained in NEITHER phase (excludes 'retention == usefulness' -> exposes the retention/generalisation tradeoff)."
files_changed: "experiments/exp_consolidation_real_reading_old_vs_new_v1.py (linear/overlapping cortex + scarcity+sparsity sweeps); experiments/exp_consolidation_sparse_hidden_cortex_v2.py (SPARSE k-WTA hidden cortex -- the flip; +dense control, +generalisation, +DG-neurogenesis mode); verification/test_consolidation_real_reading.py (scaffold-free witness, 8 tests, WITNESS PASS); data/exp_consolidation_real_reading_old_vs_new_v1/{metrics.json,metrics_sweep.json}; data/exp_consolidation_sparse_hidden_cortex_v2/metrics.json (self-contained: flip + tradeoff + dense-collapse control); data/exp_consolidation_sparse_hidden_cortex_v2_neurogen/metrics.json; notes/problems/one_store_does_two_jobs_and_consolidation_is_a_single_average/{SOLVER_NOTES.md,SOLVED.md}. Brain-fidelity verified by independent read-only literature scan (see BRAIN-FIDELITY VERIFICATION section). hdlab/ NOT touched (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_consolidation_real_reading.py"
---

# One store, two jobs: sparse coding is the primary anti-forgetting lever; selective replay works ONLY in the sparse regime; and one store cannot both retain and generalise

## The one-paragraph answer
The brief asks whether brain-faithful consolidation (fast/slow + selective/schema-gated/interleaved replay)
beats a single averaging step. The decisive finding is that **the answer hinges on the cortical CODE, and
making the code brain-faithful (sparse + pattern-separated) changes the verdict.** Sparse pattern-separated
coding (deviation #4) is the PRIMARY defence against catastrophic forgetting -- far stronger than replay. In a
DENSE store, uniform interleaved replay is needed and selective replay is a zero-sum wash; but in a SPARSE
store, selective interleaved replay DOES beat its info-free twin CI-separated (the brief's mechanism,
vindicated -- my own earlier dense-cortex "selection isn't a lever" was a modelling artifact). The catch:
sparse codes RETAIN but do not GENERALISE, and overlapping codes generalise but forget -- so a single store
cannot do both jobs, which is exactly why the brain keeps two. On the LIVE path, the store is already
separable (never forgets), so forgetting is not the current constraint; the real limit is that the meaning we
consolidate is too thin to generalise (a content problem, not a write-schedule problem).

## What I verified before building (disk outranks the brief)
- Live consolidation (`reading_grounding_loop.py::checkpoint`) is a single average that never calls
  `continual.py` / `additive_map` replay / `hippocampal_encoder.cls_replay_cycle`. **Premise CONFIRMED.**
- **BRIEF WRONG:** `cls_discrete_budget` (a "stale VET_PENDING row to read first") is ABSENT from the registry
  and the experiment index. The real prior evidence is three SYNTHETIC D4 cells; the organ map states the
  frontier: **"UNTESTED: D4 on REAL TEXT, and at the LIVE call site"** -- which is what I built.
- **BRIEF OVER-CLAIM:** `continual.py::replay_cycle` selects its replay fraction UNIFORMLY AT RANDOM -- it IS
  the info-free twin, not a selective engine. The selection function was genuinely unbuilt.

## What I built and measured
Two instruments, both on real simplewiki reading (era fixed), CLS paired-associate catastrophic-interference:
KEY = a concept's PPMI+SVD semantics; TARGET = its top-PMI associate; OLD learned first, NEW second, HELD-OUT
never trained; arms differ only in the Phase-2 consolidation schedule.

**v1 -- DENSE / overlapping-linear cortex** (`exp_consolidation_real_reading_old_vs_new_v1.py`):
| arm | OLD | NEW | held-out gen |
|---|---|---|---|
| SEQUENTIAL (no replay) | 0.076 | 0.688 | 0.052 |
| **INTERLEAVED (uniform replay)** | **0.349 [.302,.396]** | 0.370 | 0.073 |
| INTERLV_SELECTIVE | 0.336 | 0.365 | 0.073 |
| INTERLV_SCHEMA (Tse) | 0.695 | 0.083 (HOARDS) | 0.062 |
| SEP_AVG_SIM (first-order) | 0.190 | 0.172 | **0.104** |
| SEP_LOOKUP (live separable store) | **1.000** | 1.000 | 0.000 |
| HEBBIAN_SUM (distributed avg) | 0.000 | 0.000 | 0.000 |
Interleaving prevents forgetting CI-separated; selective/schema/3-factor never beat the uniform twin at ANY
replay budget (scarcity sweep 0.1->1.0) -- zero-sum in a shared overlapping store; SCHEMA's high OLD is
hoarding (NEW 0.083). SEP_LOOKUP never forgets (fork B). No arm generalises above the first-order floor.

**v2 -- SPARSE k-WTA hidden cortex** (`exp_consolidation_sparse_hidden_cortex_v2.py`; the brain-faithful
architecture: fixed random expansion Dh=512 -> relu -> k-WTA keep -> sparse hidden -> learned readout):
| keep | SEQ (no replay) | UNIFORM | SELECTIVE | generalise |
|---|---|---|---|---|
| 0.01 | 0.229 | 0.680 [.630,.727] | **0.784 [.740,.826]** | 0.052 |
| 0.02 | 0.333 | 0.896 [.862,.924] | **0.979 [.964,.992]** | 0.052 |
| 0.05 | 0.557 | 1.000 | 0.995 (ceiling) | 0.047 |
| dense-hidden control | 0.000 | 0.000 | 0.000 | 0.000 |
Sparse coding is the PRIMARY anti-forgetting lever (dose-response; dense collapses -> sparsity causal, not
capacity). **SELECTIVE interleaved replay CI-BEATS the uniform twin** where retention is not saturated
(keep 0.01, 0.02) -- the v1 negative FLIPS in the faithful regime. And the sparse cortex RETAINS (0.68-1.00)
but does NOT GENERALISE (0.05) -- the retention/generalisation tradeoff.

## The brain-foundational drill (three rounds, each caught a divergence -- owner-driven)
1. **Fork B / separable floor:** modelling the "single average" as the LIVE op actually is (separable-row,
   never forgets) rather than a distributed shared-W sum. Catastrophic forgetting is not the live constraint.
2. **Scarcity confound:** my selection test was null by construction (`replay_ratio=1.0` -> budget = whole OLD
   set -> selective and uniform replay identical items). Fixed with a budget-scarcity sweep. Selective still
   lost in the DENSE cortex -> the negative was not just scarcity.
3. **The store was the divergence, not the schedule (the decisive one):** the v1 "selection is zero-sum" result
   was measured in a single-layer LINEAR cortex. The real cortex has a SPARSE nonlinear hidden layer (Leabra
   k-WTA / lateral inhibition) that allocates concepts to separable subpopulations. Building THAT (v2) flipped
   the selection verdict -- selective replay is a lever once codes are sparse enough that replay is not zero-sum.
   Witnessed both directions: selective WINS under separable subspaces, is ~zero (+0.003) under overlap; sparse
   hidden retains OLD 1.000 vs dense-hidden 0.000. This is the SOLVER-protocol "leave the family, ask the
   biology" move: the faithful method was DIFFERENT IN KIND (sparse multi-layer), not another selection heuristic.
4. **DG neurogenesis (finest-resolution fast-store mechanism):** modelled the dentate gyrus recruiting FRESH
   hidden units for NEW memories (disjoint granule-cell pools for temporally-distinct memories). Result:
   SEQUENTIAL retention jumps to 0.971-1.000 with NO replay (vs 0.33 without neurogenesis), and generalisation
   drops further (0.021-0.026). Neurogenesis is a MORE EXTREME pattern separation -> it SHARPENS the
   retention/generalisation tradeoff, it does not escape it -- confirming (not flipping) the two-store
   conclusion. **FIDELITY CAVEAT (Akers/Frankland 2014):** real neurogenesis is DOUBLE-EDGED -- the same
   circuit remodeling that separates the new memory also ERASES some established ones; my idealised
   disjoint-units model omits that cost, so it OVERSTATES old-memory retention.

## What I did NOT establish / would withdraw first
- I did NOT beat the SEP_LOOKUP separable floor on pure retention (a perfect lookup cannot be beaten on recall);
  the sparse cortex reaches 0.98, not >1.0. The win is 'selective interleaved replay beats the info-free twin in
  the sparse regime', which IS the bar's twin criterion, not 'beats a lookup table'.
- I did NOT achieve generalisation on real reading -- every architecture sits at/near the first-order floor.
  **First thing I'd withdraw:** any hope that a better WRITE schedule fixes generalisation; the wall is CONTENT.
- v2's expansion is FIXED RANDOM; a LEARNED/competitive sparse code (DG-style) is untested and might separate
  better. A MULTI-SESSION spaced schedule (Landauer-Bjork) is untested. Both are plausible further fidelity.

## Proposed hdlab change -- NOT landed (board Q111; strategy re-verifies + lands)
The evidence gives a concrete, ordered recommendation:
1. **PRIMARY: make the consolidated cortical code SPARSE + PATTERN-SEPARATED (k-WTA), not dense.** This is the
   main anti-forgetting lever (deviation #4) and it is what makes selective replay work at all. It is the same
   lever load-bearing on the READ half (p2). Concretely: when a distributed cortical code is written, apply
   k-WTA sparsification (sweep the keep fraction; do not adopt a number) -- this is the highest-value change.
2. **SECONDARY: wire `continual.replay_cycle` as UNIFORM interleaved replay behind a default-off flag**, and
   -- only in the sparse regime -- allow a SELECTIVE (surprise-prioritized) variant, which then beats the
   uniform twin CI-separated. Do NOT add a selective scheduler to a DENSE store (zero-sum there).
3. **KEEP the separable HDFactStore as the fast/episodic store** -- it is already hippocampus-like (retains,
   does not generalise). Do NOT try to make ONE store both retain and generalise; the tradeoff is real. The
   architecture the brief's title points to (fast sparse + slow overlapping + replay bridge) is the fix.
4. **Do NOT expect any of this to improve GENERALISATION on the current corpus** -- that is content-bound
   (route to `reader_meaning_channel` / supply-or-teach a distributional code). Coordinate with the read-half (p2).

## KEY REALIZATIONS
- **The store, not the schedule, was the divergence.** "Selective replay isn't a lever" was true in my dense
  linear cortex and FALSE in a sparse pattern-separated one. When several schedule variants hit the same wall,
  the faithful fix was different IN KIND (sparse multi-layer cortex), exactly as the SOLVER protocol warns.
- **Sparse pattern-separated coding sharply reduces catastrophic interference** (equal-capacity DENSE-hidden
  control collapses to 0.000 -> sparsity, not capacity, is causal; French 1991). LIT-CORRECTED framing: this
  does NOT mean "sparse beats replay" -- CLS treats them as COMPLEMENTARY (sparse = low-interference encode;
  replay = cross-episode structure extraction). For OUR single homogeneous store, sparsifying the code is the
  highest-value engineering lever; in the brain it is one half of a two-system design.
- **Selection becomes a lever precisely when replay stops being zero-sum** -- i.e. when codes are separable
  enough that protecting one memory does not disturb another. Witnessed both directions.
- **Score BALANCED(min old,new) and HELD-OUT generalisation, not JOINT-as-mean-retention.** The mean is gamed by
  OLD-hoarding (SCHEMA), and retention alone hides that sparse codes cannot generalise.
- **Model the single-average floor as the LIVE op actually is (separable-row).** It never forgets (fork B), so
  the honest verdict is 'forgetting is not the live constraint', not a strawman distributed-average collapse.
- **The retention/generalisation tradeoff is the quantitative reason the brain keeps TWO stores** -- the literal
  premise of this problem's title, now measured (retain 0.98 vs generalise 0.05 in the sparse store).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, deviation #5 / ORGAN_MAP D4)
- **D4 tested on REAL TEXT** (was "untested"). Uniform interleaved replay prevents catastrophic forgetting
  CI-separated (SEQ 0.076 -> 0.349 dense; sparse SEQ 0.23-0.56 -> 0.68-1.0 with replay).
- **SPARSE PATTERN-SEPARATED CODING (deviation #4) sharply reduces catastrophic interference** (measured:
  sparse-hidden retains, equal-capacity dense-hidden collapses to 0.000). Deviation #4 is load-bearing on the
  WRITE as well as the READ (p2). LIT-CORRECTED: it is COMPLEMENTARY to replay (CLS: sparse-encode + replay-
  extract-structure are different jobs), not a replacement -- do not frame as "sparse beats replay". For our
  single store, sparsifying is the top engineering lever; the faithful brain answer is the two-system design.
- **The SELECTION FUNCTION is regime-dependent, NOT a flat negative:** zero-sum (no lever) in a dense/overlapping
  store; a REAL lever (CI-separated over the uniform twin) in a sparse pattern-separated store. Corrects both the
  surprise cell's and my own v1 "priority can't be exploited" reading -- the missing ingredient was sparse
  coding, not a better plasticity rule.
- **Deviation #5 reframed:** "one store, single average" is not causing catastrophic forgetting (live store is
  separable-row = already hippocampal; fork B). The real gap is the retention/generalisation TRADEOFF -- one
  store cannot both retain (needs sparse) and generalise (needs overlapping). The fix is the two-store CLS
  architecture + sparse coding, and generalisation itself is content-bound (read-half / reader_meaning_channel).

## BRAIN-FIDELITY VERIFICATION (independent read-only literature scan; corrected 2 over-claims)
Ran a focused adversarial literature check on the 5 mechanistic claims this submission rests on. Verdicts:
1. **Sparse coding reduces catastrophic interference** -- mechanism PINNED (French 1991 activation-sharpening;
   McClelland/McNaughton/O'Reilly 1995; O'Reilly 2014). **CORRECTED:** do NOT frame it as "beats/primary vs
   replay" -- CLS treats sparse-coding and interleaved replay as COMPLEMENTARY (different jobs, different
   systems); the whole point is no single scheme does both. Regime caveat (van de Ven 2024, arXiv:2403.05175):
   interleaving dominates at aligned/orthogonal extremes, is weakest at INTERMEDIATE overlap (where real
   memories live); sparsity's benefit degrades under capacity/superposition pressure.
2. **Selective replay is representation-dependent (zero-sum in overlap)** -- direction SUPPORTED (Schaul 2016
   PER; Rolnick 2019; Isele 2018; van de Ven 2024; TD-error priority can EXACERBATE interference). Refinement:
   it is TWO coupled knobs (which sample x available capacity), and a high-priority sample can overwrite
   neighbors via gradient bleed independent of capacity -- stated accordingly.
3. **DG neurogenesis for temporal pattern separation** -- PINNED (Aimone 2011; Sahay 2011; Clelland 2009).
   **CORRECTED:** it is DOUBLE-EDGED -- Akers/Frankland 2014 (Science) shows elevated neurogenesis CAUSES
   forgetting of established memories via circuit remodeling. My neurogenesis arm (disjoint fresh units ->
   retention ~1.0) models the idealised separation WITHOUT that remodeling cost, so it OVERSTATES old-memory
   retention; the real mechanism trades some old-forgetting. (Human adult neurogenesis is itself contested:
   Sorrells 2018 vs Boldrini 2018.)
4. **Retention/generalisation tradeoff motivates two systems** -- PINNED (O'Reilly & McClelland 1994, title:
   "avoiding a trade-off"; Rolls 2013/2016). Caveat: retention side is causally pinned (DG lesion studies);
   the generalisation-needs-density side rests more on model convergence + correlational consolidation data.
5. **Surprise as replay priority** -- SUPPORTED but my framing was TOO NARROW: replay priority is a MULTI-
   FACTOR salience composite (reward, RPE/surprise, novelty, valence, recency; weights unresolved), not
   surprise-vs-reward (Ambrose-Pfeiffer-Foster 2016; TiNS 2025 replay review; Nat Neuro 2023 valence). Honest
   statement: surprise is A valid member of a genuinely OPEN selection space, not THE alternative to reward.
**Mechanisms my system-level model does NOT capture (flagged, different in kind):** (a) SYNAPTIC TAGGING &
CAPTURE (Frey & Morris 1997; Redondo & Morris 2011) -- the local synapse-level coincidence gate for what
consolidates (this is a separate organ, ORGAN_MAP D9, not this problem); (b) SCHEMA-gated consolidation RATE
(Tse 2007/2011; van Kesteren 2012) -- schema-congruent facts consolidate in ~24-48h, SKIPPING slow
interleaving by landing directly on safe overlapping cortical structure; my SCHEMA arm modeled budget
reallocation, not this "skip-the-slow-path" mode -- a partial-fidelity caveat.

## TLDR (plain language)
The brain keeps a fast memory and a slow memory separate and folds new learning into the slow one by REPLAYING
it during sleep. We use one store and a single averaging step. I tested this on real reading. Findings: (1) a huge part
of what stops new learning from erasing old is the CODE itself -- using SPARSE memory codes, where each fact
lights up its own small set of "neurons" so learning a new fact barely touches the old ones. With dense codes
everything erases; with sparse codes almost nothing does. (The brain uses BOTH sparse codes AND replay -- they
do different jobs; I'm not claiming one beats the other.) (2) Once the codes are sparse, being
CLEVER about which memories to replay (replay the ones about to be lost) genuinely helps -- I was wrong earlier
when I said it didn't; that earlier test used the wrong (dense) kind of memory. So the brain's recipe -- sparse
codes plus targeted replay -- does work. (3) But there's a catch that explains WHY the brain bothers to keep two
memories: sparse codes are great at REMEMBERING but useless at GENERALISING to new questions, while dense codes
generalise a bit but forget. No single store can do both -- so the brain uses two. (4) Our current store already
never forgets (it files each fact separately), so forgetting was never our real problem. Our real problem is the
same as last time: the MEANING we store is too thin to answer new questions -- and that's a different job to fix.

## QUESTIONS
None.

## NEXT STEPS
1. Land the ordered write-op guidance: make the consolidated cortical code SPARSE/pattern-separated (primary
   lever); wire UNIFORM interleaved replay behind a default-off flag, with a SELECTIVE variant allowed only in
   the sparse regime; keep the separable fast store as-is.
2. Route the real limit (a meaning code that GENERALISES) to the content lanes (`reader_meaning_channel` /
   supply-or-teach a distributional code), coordinated with the read-half (p2). Both halves point there.
3. Fold the four AUDIT UPDATE notes into `BRAIN_FOUNDATIONAL_AUDIT.md` (D4 on real text; sparse coding is the
   primary anti-forgetting lever; selection is regime-dependent not a flat negative; deviation #5 reframed to
   the retention/generalisation tradeoff + two-store necessity).
4. (Optional further fidelity, NOT closed here -- from the literature scan) a DOUBLE-EDGED neurogenesis model
   with the Akers-2014 remodeling cost (my disjoint model omits it); SCHEMA-gated consolidation RATE (Tse: skip
   slow interleaving when congruent -- distinct from my budget-reallocation SCHEMA arm); the SYNAPTIC TAGGING &
   CAPTURE synaptic-implementation layer (separate organ D9); a LEARNED/competitive sparse code and a
   MULTI-SESSION spaced schedule. None are expected to change the retention/generalisation-tradeoff conclusion.

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT (owner-DONE); verdict PARTIAL. Full SOLVED re-read FRESH; re-verified scaffold-free FIRST-HAND (test_consolidation_real_reading.py 8/8 WITNESS PASS: SEQ 0.076->INTERLV 0.349 CI-sep; separable store never forgets 1.000; sparse OLD 1.000 >> dense 0.000; selective sparse 0.784 CI-beats uniform 0.680; SELECTIVE<=uniform in dense). THE STORE, NOT THE SCHEDULE, was the divergence: making the cortical code SPARSE + pattern-separated (k-WTA) FLIPS the selection verdict; sparse coding is the PRIMARY anti-forgetting lever (equal-capacity dense control collapses to 0.000 -> sparsity causal). Two-store necessity measured (retain 0.68-1.0 vs generalise 0.05). FORK B: the live store never forgets -> forgetting is not the live constraint; the wall is CONTENT (generalisation at the first-order floor). Model of the protocol: leave-the-family-ask-the-biology (dense->sparse multi-layer, different in kind); honest self-corrections (fork B, scarcity confound, v1 artifact, neurogenesis double-edged); an INDEPENDENT literature-fidelity scan that corrected 2 of its own over-claims. 4 AUDIT UPDATEs folded (deviation #5 reframed to the retention/generalisation tradeoff; sparse coding primary + load-bearing on WRITE+READ, complementary to replay; selection regime-dependent; D4 on real text). Review + SOLVER REVIEW in PROBLEM.md; priority cleared. hdlab landing EARNED (ordered: PRIMARY sparse k-WTA cortical code default-off = the p2 cortical-read's sparse lever; SECONDARY uniform interleaved replay default-off, selective only in sparse regime; KEEP the separable fast store) -> queued, coordinate with p2. Generalisation routes to the meaning-supply line. NO hdlab landing yet. Committed (no push).
