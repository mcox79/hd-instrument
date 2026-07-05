# Capability-optimization priority ranking: CONTROL vs REASONING vs COMPREHENSION vs PERCEPTION vs INTEGRATION

**Date:** 2026-07-05. **Type:** 5x-drill angle 1/5 (capability-optimization priorities), operational ranking + brain-mechanism
grounding, not a fresh lit-scan on a single topic. **Discipline:** lit-scan calibration -0.15..-0.25; novel-synthesis P cap
0.50; no-smoke default-deflated; brain = existence proof (basics proven because the brain does them); scour-before-propose
(per [[feedback-prior-work-informs-not-constrains]] and [[feedback-dont-dismiss-adjacent-methods]]).

**Field advisor run:** `research_field_advisor.py` invoked per role contract (110 drills, 22 fields). Its top candidates
(free-cumulants, Glauber/Metropolis dynamics, Tracy-Widom) are substrate-physics math threads UNRELATED to this drill's
question (which is neuroscience-of-executive-function / psycholinguistics, not stat-mech) — noted as run, correctly not
followed here; this drill's search space is the brain-mechanism literature named in the task, not the field-coverage matrix.

**SCOUR DONE FIRST (per USER discipline) — two of the five "not-optimized" items in the task premise are STALE.** Before
proposing anything new I grepped `experiments/`, `data/`, and `notes/` for the three named pointer cells plus the in-flight
control probe. Two corrections follow directly from what's already on disk:

---

## CORRECTION 1 — INTEGRATION hard-regime is NOT untested. It's DONE, verified off-disk, and CLOSED.

`data/exp_integration_end_to_end_loop_bridge_HARD_v2/metrics.json`: verdict **HARD_FAIL**, `margin=-0.706`, `sym=0.806`
vs `cot=0.100`. This is the FULL, not a smoke — VET-confirmed per the 2026-07-05 BACKUP doc ("co-trained linear bridge
margin=-0.706 vs parameter-free symbolic cleanup — composition EFFECTIVELY SYMBOLIC confirmed at scale"). Read correctly,
this HARD_FAIL is a **decisive glass-box-positive**: the learned bridge is not load-bearing; a parameter-free NN-argmax
cleanup->lookup already composes reason->generate at the hard regime (hub-crowded V=4096, D=10, hops=3, both slots
recovered-and-noisy). The only remaining lever (a nonlinear/MLP bridge) is explicitly flagged in the backup doc as
"strategically unnecessary since symbolic already composes transparently." **This is not a ranking candidate — it is
closed. No further experiment is warranted near-term.**

## CORRECTION 2 — PERCEPTION's ship-gate is NOT still failing. It PASSED (graded codes), same day, after the task's framing.

The task's premise ("native-0.85 unrealistic at 970K, distill-from-BGE pragmatic") describes the state as of the *middle*
of 2026-07-05. The backup doc's own LATER entry (same date) reports: `data/exp_encoder_v11_gsbc_graded_sparse_v1_seed7/`
and `_seed13/` (GSBC graded-code) landed **ret_agree10=0.3986 vs hard-code 0.2117 (+0.187, clears the 0.30 gate)**, cosine
0.834 (>=0.80), algebra keyed@J5=1.000 — re-verdicted **PASS** (atom `a12d295`). The retrieval gap that made native-0.85
"unrealistic" was the hard-STE sign-quantization bottleneck; graded (soft) quantization removes it. Native (teacher-free)
0.85 remains explicitly out of scope as "a NON-GATING long-bet research track" per the integrated spec sheet — that
framing is correct and unchanged. **This is not a ranking candidate either — ship-it status confirmed, further native-
encoding work is genuinely diminishing-returns/long-bet, not a near-term optimization target.**

So the real ranking question is over the three items that are genuinely still open: **CONTROL, COMPREHENSION, REASONING.**

---

## HEADLINE

Ranked by capability-gain x feasibility x glass-box-LLM-value: **(1) CONTROL, (2) COMPREHENSION, (3) REASONING.** The
surprise is the reorder of (2) and (3) versus the task's framing-order: an independent literature scan on sentence-
comprehension memory theory found that the substrate's comprehension envelope (17/20, "vocab-dependent") was measured
under a **disjoint-per-role-vocabulary design that structurally avoids the dominant, well-replicated driver of real human
parsing difficulty** (similarity-based cue-overload / fan-effect interference among competing fillers) — meaning the
banked HARD_PASS may not transfer to real language, where the same word can fill either role. That's a validity question,
not polish, so it outranks reasoning's residual cv-instability fix. For CONTROL, an **already-running, already-smoked**
cell (`exp_pfc_gate_cfrpe_deeper_regime_v1`, local pid, not duplicated here) has, at smoke, already produced a clean,
decisive, brain-literature-corroborated finding: the depth-4->depth-6 gating collapse is driven by **branching factor**
(number of competing next-ops per hop), not by insufficient memory horizon — the "fix" it's testing (longer-horizon
successor-representation gamma) shows **zero differential effect** (gonogo identical at gamma=0.85 vs 0.95, both regimes),
while the "fairness lever" it added as a side control (n_ops 4->2 at fixed depth=6) recovers ~3x the closure. An
independent, context-blind lit-scan on basal-ganglia action-selection literature (Hick's law, multi-alternative
drift-diffusion, GPR selection-problem model) converges on exactly this distinction, and a SEPARATE hierarchy literature
(options framework, Botvinick-Niv-Barto HRL, Frank-Badre corticostriatal HRL) independently predicts the actual fix:
temporal-abstraction (hierarchical subgoal decomposition), not a longer memory window.

---

## RANKED PRIORITIES

### #1 CONTROL — branching-factor-vs-depth disentangle, then hierarchical-options gate (MUST-HAVE)

**What we have (verified off-disk):**
- `exp_pfc_gate_cfrpe_trained_v2` FULL, HARD_PASS but scoped: only 2/7 regimes are FAIR (baseline-in-band); both are
  depth-4 (`V1200_d4` closure=0.661, `V2400_d4` closure=0.514). At depth-6 (`V2400_d6`) closure collapses to 0.073 —
  but the additive baseline there is FLOORED (0.007, unfair), so this collapse was never cleanly attributable to depth.
- `exp_pfc_gate_cfrpe_deeper_regime_v1` (in-flight now, local pid — **do not duplicate**, this ranking builds on it): its
  own docstring names the hypothesis under test as an SR-temporal-horizon fix (`gamma` 0.85->0.95->0.99, citing
  Stachenfeld 2017 dorsoventral-hippocampal-SR-scale gradient) and adds `n_ops={2,4}` as a secondary "fairness lever."
  **SMOKE RESULT (on disk now, HARD_PASS at its own gate, but read past the verdict string):**
  - `op4_V300_d6` (branching=4, depth=6): `gonogo_g0.85 = 0.10417` vs `gonogo_g0.95 = 0.10417` — **bit-identical**. The
    SR-horizon fix produced **zero** measurable lift.
  - `op2_V300_d6` (branching=2, depth=6, same V, same depth): `gonogo_g0.85=0.3889` vs `gonogo_g0.95=0.3819` — again
    no gamma effect, but **~3x higher than op4 at the identical depth** (closure 0.306-0.315 vs 0.073-0.106).
  - Read honestly: **the smoke already falsifies its own headline hypothesis** (temporal horizon) and confirms a
    different one (branching factor) that was only wired in as a side control. This is exactly the kind of
    "verdict-string vs per-cell metrics" gap the no-smoke discipline exists to catch.

**How the brain does it (independent lit-scan, generic terms, no substrate context leaked):**
- **Branching factor is the textbook-established axis.** Redgrave, Prescott & Gurney 1999 (*Neuroscience*, "The basal
  ganglia: a vertebrate solution to the selection problem?") frame BG function as arbitrating among a *number of
  competing* action requests — reliability is a function of how many channels compete, not sequence position. Hick's
  law (1952, extensively replicated) gives RT/accuracy scaling ~log2(N-alternatives); multi-alternative drift-diffusion
  / leaky-competing-accumulator models (Usher & McClelland 2001) show accuracy degrading as competing accumulators
  increase, explicitly mapped onto striatum/STN/pre-SMA circuitry in several reviews. Converging, well-established.
- **Depth (temporal credit assignment) is a genuinely separate literature, and hierarchy is its specific fix.** Sutton,
  Precup & Singh's options framework (1999, *AIJ*) and Botvinick, Niv & Barto's hierarchical-RL account (2009,
  *Cognition*; neural signature: Ribas-Fernandes et al. 2011, *Science*) decompose long sequences into
  options/subgoals so each level's policy spans FEW steps — an explicit depth-reduction mechanism (SMDP formalism).
  Frank & Badre's corticostriatal HRL work and Badre & Frank's rostro-caudal PFC gradient model a SEPARATE hierarchy
  over conjunctive feature/rule dimensions (abstraction/branching-reduction, not temporal depth). **The brain appears
  to run two orthogonal hierarchies** — one for branching/dimensional complexity (rostro-caudal PFC), one for temporal
  depth (options/subgoals) — matching, independently, the substrate's own empirical split (gamma=depth-axis-lever,
  inert; n_ops=branching-axis-lever, decisive).
- Calibration: the branching-factor axis is well-established/textbook; the "hierarchy specifically fixes depth, not
  branching" framing is the lit-scanning sub-agent's OWN cross-lineage synthesis (stated honestly as such by that
  sub-agent), not one paper's stated conclusion — treat as plausible-and-independently-corroborated-by-our-own-data,
  not settled neuroscience.

**Feasibility:** HIGH. No new architecture — reuses the existing anchor's trainer/harness. A proper `n_ops x depth`
grid (not 3 ad hoc cells) at FIXED gamma (since gamma is empirically inert) is a straightforward CPU/GPU cell.

**Glass-box-LLM value:** HIGH and structural, not incidental. The Go/NoGo gate IS the "should I act / stop / continue"
circuit any agentic glass-box LLM needs for multi-step tool-use; knowing that the limiting factor is decision-branching-
entropy rather than raw hop-count changes the actual engineering fix (macro-action/subgoal decomposition, not "hold state
longer").

### #2 COMPREHENSION — shared/overlapping-vocabulary retest (MUST-HAVE, validity question not polish)

**What we have (verified off-disk):** `exp_comprehension_envelope_superposition_vocab_v1` FULL, HARD_PASS, order-recovery
20/20, full-parse 17/20, cliff only at `D8 x V>=250`. Its own docstring names the vocab axis as
`"vocab_axis": "V_per_role_disjoint_partition_selectional_restriction"` — each role's V candidate fillers are drawn from
a **disjoint partition** (role-A fillers never appear as role-B candidates).

**How the brain does it (independent lit-scan):** the psycholinguistics literature treats real comprehension difficulty
as dominated NOT by a pure structural/depth ceiling but by **similarity-based cue-overload among competing fillers**:
Van Dyke & McElree 2006 (*J. Memory & Language*) show retrieval interference rises with the number/similarity of
competitors when retrieval cues can't uniquely distinguish them; Jäger, Engelmann & Vasishth 2017 (*J. Memory &
Language*, Bayesian meta-analysis) confirms this as a well-replicated research program; Anderson's fan effect
(1974, textbook) is the domain-general analog — more associations per concept-node reliably degrades retrieval purely
as a function of competitor count, structure held fixed. Even the classic center-embedding "depth cliff" (Miller &
Chomsky 1963) is now reinterpreted by Lewis 1996 as similarity-based interference among concurrently-held NPs, not a
depth-only stack-capacity wall (Gibson & Thomas 1999 give direct behavioral evidence for memory-driven forgetting over
a hard grammatical ceiling). Gibson's Dependency Locality Theory (1998, *Cognition*) prices integration cost by the
number of intervening discourse referents — already partway toward a competitor-count metric, not pure linear distance.
**Bottom line: a disjoint-vocabulary test isolates the WEAKER-evidenced structural/count axis and specifically avoids
the mechanism decades of retrieval-interference literature identifies as dominant.** Real language — where the same
word/concept can fill either role — should be measurably harder than the current envelope predicts.
Calibration: well-established/textbook (cue-based retrieval, fan effect, Cowan capacity); the claim that
center-embedding is *entirely* interference-driven (vs partly structural) is an active, not fully settled, debate.

**Feasibility:** MEDIUM. Reuses the existing cell's GSBC pool/harness; changes only the vocab-partition scheme (shared
pool sampled per-role WITH overlap instead of disjoint partition) and adds a cue-overlap/competitor-count axis. Not a
new architecture, but a new independent variable, so more build-work than #1's grid extension.

**Glass-box-LLM value:** HIGH — this is precisely the realistic case (a shared open vocabulary across grammatical
roles) a language-capable substrate must handle; the currently-banked HARD_PASS should not be quoted as representative
of real-sentence performance until this is tested.

### #3 REASONING — cv-instability / D_MAX-censoring resolution (real, but incremental — closer to polish than #1/#2)

**What we have (verified off-disk):** `exp_reasoning_depth_keyslots_sharding_v1` FULL, **MIDDLE_BAND**: usable depth
extends from baseline 3.2-9.2 hops to 16.4-18.0+ via 4x key-slot capacity (collision-bound mechanism, confirmed:
`eff_capacity_by_arm` baseline=2048 -> keyslots_4x=8192), shuffled-structure control=0 (extension is real, from
structure not raw store size). MIDDLE not HARD_PASS because cross-seed `cv_base` ranges 0.1636-0.3633 (>0.10 stability
bar) and 3/6 op-points are D_MAX=18-censored (16-18 is a lower bound, not a measured ceiling).

**How the brain does it:** already drilled in depth this session (`research_5x_drill_reasoning_spec_and_brain_mechanism_
2026-07-05.md`, reused not re-run here per scour discipline) — PFC persistent-activity scratchpad (Miller & Cohen 2001)
+ hippocampal regenerative cleanup (Marr 1971; Renart & Brunel 2007) + TEM factorized relational code (Whittington &
Behrens 2020, *Cell*) + resonator-network recurrent settling (Frady, Kent, Olshausen & Sommer 2020). That drill's own
"augment beyond biology" section already named the exact lever later confirmed empirically: "grow D and bank count
until the resonator/cleanup operating margin is comfortably below threshold" — the keyslot-sharding cell IS that
augment, now measured.

**Feasibility:** MEDIUM (more seeds + raised D_MAX ceiling is a bigger/more expensive GPU sweep than #1's grid).
**Glass-box-LLM value:** real but the capability is already usefully demonstrated (16-18 hops, MIDDLE_BAND is a
genuine, citable result); tightening the confidence interval doesn't unlock new build surface right now the way #1
and #2 do. **Rank this a "worth doing, not urgent" — the closest of the three to diminishing-returns polish, though
still above PERCEPTION-native and INTEGRATION which are genuinely closed/parked.**

---

## MUST-HAVE vs DIMINISHING-RETURNS-POLISH (direct answer to the task's question)

**MUST-HAVE for a glass-box LLM:**
1. CONTROL branching-vs-depth disentangle + hierarchical-options gate — this IS the executive-function circuit an
   agentic system needs; currently proven only to depth-4 and the in-flight fix is (per its own smoke) chasing the
   wrong mechanism.
2. COMPREHENSION shared-vocab retest — a validity check on whether the banked "comprehension holds" number means
   anything for real sentences, where role-fillers overlap in vocabulary.

**DIMINISHING-RETURNS / POLISH (real, but not urgent):**
3. REASONING cv-instability/D_MAX fix — the capability already works and is banked; this narrows error bars.
4. PERCEPTION native-0.85 — explicitly a non-gating long-bet per the substrate's own spec sheet; ship-gate already
   passed via graded codes (Correction 2 above). Do not spend near-term cycles here.
5. INTEGRATION hard-regime nonlinear-bridge follow-up — explicitly flagged "strategically unnecessary" in the backup
   doc; the decisive negative (symbolic beats learned bridge) already closed this thread (Correction 1 above).

---

## Cheap decisive test (top-1 pick, buildable now, does not duplicate the in-flight cell)

**`exp_pfc_gate_branching_depth_entropy_grid_v1`** (staged to fire AFTER the in-flight `..._deeper_regime_v1` FULL
lands — reuses its trainer/harness, does not re-test gamma since smoke already shows it's inert):

- **Grid:** `n_ops in {2,3,4}` x `depth in {4,5,6,7,8}` at FIXED `gamma=0.85` (the v2/baseline value — gamma dropped
  as an axis since the deeper-regime smoke shows zero differential effect), FIXED `N=8192` (canonical scale, matches
  v2 FULL), `V` chosen per-cell to keep the additive baseline in-band at every depth (reuse v2's META_RULE:
  `INCONCLUSIVE_NO_FAIR_REGIME` rather than a false HARD_FAIL when the baseline floors).
- **Primary metric:** fit `closure` (and `gonogo_lift`) against three candidate models across the grid: (A) depth
  alone, (B) `n_ops` alone, (C) `log2(n_ops) * depth` (Hick's-law-generalized decision-entropy / effective
  search-complexity, per the GPR-selection-problem + multi-alternative-DDM literature above).
- **HARD-PASS:** model (C) predicts the cross-over the smoke already hints at (an `op2_d8` cell should out-perform
  an `op4_d5` cell despite MORE total depth, because its per-decision branching is lower) — i.e., entropy-model rank
  correlation with measured closure beats the depth-alone model by >= 0.15 Spearman-rho margin, replicated across
  >= 3 seeds, with the anti-tautology `reach_tcos_corr` gate held (per v2's own discipline).
- **HARD-FAIL:** depth alone predicts closure as well as or better than the entropy-product model (i.e., `op2_d8`
  does NOT beat `op4_d5`, and cross-seed the entropy model's rank-correlation gain is < 0.05) — this would mean the
  smoke's clean 3x branching effect does not generalize across a real grid, and the two-lever confound would need a
  different explanation than branching factor.
- **P_deflated: 0.50** (raw ~0.70 given the smoke already shows an exact gamma-tie plus a clean 3x branching effect at
  2 depths — a strong pre-existing signal, not speculation — but this is a full grid + a formal entropy-model fit on
  this exact substrate for the first time; capped at the novel-synthesis ceiling per [[feedback-lit-scan-calibration-
  penalty]]).

**On HARD-PASS, the natural follow-on build** (a genuinely NEW brain-component, not an analysis cell):
`exp_pfc_gate_hierarchical_options_v1` — a two-level Go/NoGo gate: a top-level gate selects among <=4 subgoals/
macro-ops, each realized by a depth<=4 low-level gate (matching the already-PROVEN-at-depth-4 envelope), tested
against a flat single-level gate at matched TOTAL depth (e.g., 2 subgoals x depth-4 = total depth-8). Brain-grounded
directly in Sutton-Precup-Singh options (1999) + Botvinick-Niv-Barto HRL (2009) + Frank-Badre corticostriatal HRL —
HARD-PASS: hierarchical closure at total-depth-8 recovers >= 80% of the native depth-4 closure (0.661 at V1200_d4 ->
target >= 0.53 at hierarchical depth-8); HARD-FAIL: hierarchical closure at depth-8 <= flat single-level gate's own
depth-8 closure (hierarchy adds nothing, matching this session's caution about not assuming a fix works before testing
it). This is the correctly-sequenced next brain-component per the BRAIN-COMPONENT-DRIVEN thrust: it targets the SAME
CONTROL capability, is the "missing hierarchy" analog to the "missing training signal" thesis that already worked once
this session (cfrpe RPE gate), and directly answers "how does the brain extend reliable control past ~4-7 sequential
decisions" (answer: temporal abstraction, not a bigger single-level buffer — the same shape as REASONING's
"chunk-and-regenerate, don't flat-superpose" finding, C.2 of the reasoning drill, appearing again in a different
capability).

## Falsifiable predictions (HARD-PASS / HARD-FAIL, restated compactly)

- **CONTROL entropy-grid:** HARD-PASS = entropy-product model (C) beats depth-alone by >=0.15 Spearman-rho margin,
  >=3 seeds, anti-tautology clean. HARD-FAIL = depth-alone model matches or beats the entropy model (op2_d8 does not
  beat op4_d5).
- **CONTROL hierarchical-options follow-on:** HARD-PASS = hierarchical depth-8 closure >= 80% of native depth-4
  closure. HARD-FAIL = hierarchical depth-8 closure <= flat single-level depth-8 closure.
- **COMPREHENSION shared-vocab retest (spec, not yet cell-authored — flagging for next drill/dispatch):** expect a
  new cliff to appear EARLIER than `D8_V>=250` once role-vocabularies overlap and a competitor-count/cue-overlap axis
  is added; HARD-FAIL-of-the-current-tier = full-parse holds >= 15/20 cells even under shared vocab with competitor
  count matched to V (i.e., the disjoint-vocab design turns out not to matter); HARD-PASS-of-the-hypothesis = full-
  parse envelope shrinks measurably (fewer than 12/20 cells hold) once fillers are drawn from a shared, overlapping
  pool, confirming cue-overload as the real driver (this is a "found a bigger gap" HARD-PASS on the research
  hypothesis, an honest negative on the previously-banked comprehension tier).

## Cross-thread synthesis

Extends without repeating: `research_5x_drill_reasoning_spec_and_brain_mechanism_2026-07-05.md` (reasoning brain
mechanisms, reused verbatim for #3, not re-derived); the 2026-07-05 BACKUP doc's honest scoreboard (source of the
task's five-item list, two of which — perception, integration — this drill found stale via scour); the
BRAIN-COMPONENT-DRIVEN thrust (`project_brain_component_driven_development_thrust...`) — the hierarchical-options gate
proposed here is the natural next brain-component after the cfrpe-RPE Go/NoGo gate, following the same "missing
mechanism, not missing part" pattern that thrust predicts. New contribution: the branching-factor-vs-depth
disentangle for CONTROL (independently corroborated by a context-blind lit-scan against the substrate's own already-
collected smoke data — a clean convergence, not an assumption), and the comprehension vocab-overlap validity concern
(new, not previously flagged in any prior comprehension memo — the existing envelope cell's own docstring names the
disjoint-partition design choice but no prior note connected it to the cue-overload literature).

## Substrate-product implications

1. Do not build more CONTROL depth-extension on the SR-horizon/gamma lever — the in-flight cell's own smoke already
   shows it's inert; redirect the next brain-component build to hierarchical/options decomposition instead once the
   entropy-grid confirms branching factor is the driver (avoids a wasted build cycle chasing the wrong mechanism).
2. Do not quote the current comprehension HARD_PASS (17/20) as representative of real-sentence performance in any
   product framing until the shared-vocabulary retest runs — the disjoint-vocab design is measuring an easier-than-
   real regime by the literature's own account.
3. PERCEPTION and INTEGRATION should be explicitly marked CLOSED/SHIPPED in the next capability_scorecard revision
   (deferred tidy item already on the backup doc's list) — continuing to list them as "not-optimized" open items
   costs planning attention that should go to CONTROL/COMPREHENSION.
4. The hierarchical-options gate, if it HARD-PASSes, is a legitimate glass-box differentiator: an inspectable
   two-level Go/NoGo decomposition (each subgoal's gate is a named, loggable decision) is exactly the kind of
   mechanical-faithfulness property (per the reasoning drill's Part A) that opaque LLM planners don't offer by
   construction.

## Citations (verified count: 15 distinct sources across 2 lit-scans, all traceable to author/year/venue or arXiv ID)

CONTROL lit-scan (8): Redgrave, Prescott & Gurney 1999 (*Neuroscience*, BG selection-problem); Hick 1952 (Hick's law,
extensively replicated); Usher & McClelland 2001 (multi-alternative leaky-competing-accumulator); Sutton, Precup &
Singh 1999 (*AIJ*, options framework); Botvinick, Niv & Barto 2009 (*Cognition*, hierarchical RL); Ribas-Fernandes et
al. 2011 (*Science*, subgoal neural signature); Frank & Badre 2012 (*Cerebral Cortex*, corticostriatal HRL);
Stachenfeld et al. 2017 (dorsoventral hippocampal SR-scale gradient — cited in the in-flight cell's own docstring,
not re-derived here).
COMPREHENSION lit-scan (7): Miller & Chomsky 1963 (center-embedding, textbook); Lewis 1996 (*J. Psycholinguistic
Research*, similarity-interference reframe); Gibson & Thomas 1999 (*Language & Cognitive Processes*, structural
forgetting); Gibson 1998 (*Cognition*, Dependency Locality Theory); Van Dyke & McElree 2006 (*J. Memory & Language*,
retrieval interference); Jäger, Engelmann & Vasishth 2017 (*J. Memory & Language*, meta-analysis); Anderson 1974 /
Anderson & Reder 1999 (fan effect, textbook).
On-disk/measured (own substrate, not literature, all verified off-disk this cycle): `data/exp_pfc_gate_cfrpe_trained_
v2/metrics.json`; `data/exp_pfc_gate_cfrpe_deeper_regime_v1_smoke/metrics.json`; `data/exp_reasoning_depth_keyslots_
sharding_v1/metrics.json`; `data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json`;
`data/exp_integration_end_to_end_loop_bridge_HARD_v2/metrics.json`; `data/exp_encoder_v11_gsbc_graded_sparse_v1_seed7/`.

---
-- Research, 5x-drill angle 1/5; deflated-honest; two lit-scan sub-agents dispatched in parallel (Sonnet, generic
neuroscience/psycholinguistics terms only, no substrate-novel mechanism names leaked per [[feedback-query-privacy-
decomposition]]); scour-before-propose caught two stale premises in the task statement before any new dispatch.
