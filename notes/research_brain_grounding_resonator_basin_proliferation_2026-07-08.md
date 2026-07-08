# Research -- brain-grounding drill (#1 of up to 5): escaping resonator basin-proliferation

Filed by: research (Sonnet 5, 3 parallel Sonnet lit-scan sub-agents + own synthesis) | 2026-07-08
Trigger: resonator/factorization mechanism smoke-craters as K grows
(`data/exp_resonator_ksweep_reachability_v1_smoke/metrics.json`, seed=3, single-seed SMOKE:
`K3(oracle_any=1.000) K4(0.867) K5(0.000) K6(0.000)`, verdict `HARD_FAIL "WALL_FUNDAMENTAL"`,
diagnosed as basin-proliferation).

**STATUS GATE (per live coordinator correction mid-cycle): the K5/K6=0 wall is SMOKE-ONLY. The K-sweep
FULL run is in flight and skunkworks has NOT yet confirmed this is a genuine result (not a harness /
oracle / budget misconfig, wrong regime, or saturation-vacuous null). Nothing below should be read as
"the wall is real, go build the fix." This note is capability groundwork: (1) it grounds the negative in
real neuroscience/theory regardless of whether the wall survives confirmation, and (2) it produces ONE
concrete, ready-to-build candidate cell that is BUILD-GATED on skunkworks clearing the K-sweep FULL
result. If skunkworks instead finds a harness bug, this note's ranking and candidate stay valid as
future-work groundwork but the trigger urgency drops to zero -- do not dispatch the candidate cell until
that gate clears.**

---

## (a) HEADLINE

**Ranked brain mechanisms, by likelihood of being the load-bearing escape from basin-proliferation IF
the wall is confirmed genuine (highest first), each independently verified by a dedicated Sonnet
lit-scan sub-agent against public neuroscience/theory literature (generic-term queries only, no
substrate-specific framing off-platform):**

1. **Sparse expansion recoding (dentate-gyrus pattern separation / Tsodyks-Feigelman sparse-coding
   capacity) -- HIGHEST practical rank, MEDIUM-LOW confidence in the specific mechanism claimed.**
   This substrate ALREADY HAS a fully built, unit-tested, validated implementation of exactly this
   primitive: `hdlab/hippocampal_encoder.py`'s `DGProjection` class (random expansion `N -> dg_dim` +
   top-K magnitude sparsify + sign, explicitly modeled on DG expansion coding). Its own selftest
   `_st_dg_pattern_separation` PASSES with a measured decorrelation gap (`code_cos < input_cos - 0.20`
   on `input_cos~0.85-0.95` inputs) -- the pattern-separation property is real and already
   machine-verified on this substrate, in a *different* application (`bet_b_moe_per_task_dg_gating`,
   MoE-gating retention task). **It has never been wired into the resonator's factor-codebook path.**
   BUT: the lit-scan honestly found that the specific causal chain "input decorrelation before storage
   -> fewer SPURIOUS BASINS in the retrieval dynamics" is *plausible-but-unproven* in the literature --
   Amit-Gutfreund-Sompolinsky spurious mixture-state suppression is driven by *temperature*, not
   sparsity, in the founding theory; Tsodyks-Feigelman's sparse-coding capacity gain (`alpha_c ~
   1/(f|ln f|)`) comes from a *different* mechanism (fewer terms in the crosstalk-noise sum for
   PURE-pattern retrieval), not from directly suppressing basin MULTIPLICITY. No paper was found that
   measures spurious-basin count vs. input correlation holding pattern count fixed. This candidate is
   ready-to-build (primitive exists) but its mechanistic justification is an inference, not a proven
   result -- exactly the honest gap the calibration discipline requires flagging.

2. **Theta-gamma phase-multiplexing (Lisman & Idiart 1995; sequential, not simultaneous, resolution)
   -- mechanistically the MOST STRUCTURALLY CORRECT answer, but NOT a resonator front-end patch.**
   The brain's actual answer to "resolve many bound items without a combinatorial joint search" is, per
   this model, to never pose the K-way joint-search problem in the first place: each item occupies its
   own gamma sub-cycle within a theta cycle and is decoded ALONE, one at a time, converting a K-way
   simultaneous problem (`M^K` configuration space) into K sequential 1-way problems (`K*M` total). This
   is the closest brain-mechanism analog to "why doesn't the brain suffer combinatorial basin
   explosion" -- but it requires the K factors to be stored SEPARATELY in time/phase slots to begin
   with, not bound multiplicatively into one superposed vector and then factored post-hoc as the
   resonator does. It is a different ENCODING strategy, not a decode-side fix, so it is a bigger redesign
   than candidate #1 and is NOT proposed as this cycle's cell (see (b)). It also carries real costs:
   the lit-scan found the model's own headline quantitative prediction (theta/gamma ratio predicts digit
   span) FAILED a pre-registered replication (Malenínská et al. 2021), and phase-multiplexing trades item
   count for per-item fidelity/speed (a proven capacity-vs-precision tradeoff, not a free lunch). This
   substrate has ALSO already attempted theta-gamma nested oscillation once, in a composition context
   (`substrate_theta_gamma_nested_oscillation_LM_v1`, HARD_FAIL, needed an added "brain-compensation"
   variant to recover) -- independent evidence that phase-multiplexing is nontrivial to get right on this
   substrate, reinforcing that it is a longer-horizon redesign, not a quick front-end swap.

3. **Winner-take-all / inhibitory sharpening -- RANKS LOW, likely NOT load-bearing, possibly
   counterproductive.** A specific literature result ("Disappearance of Spurious States in Analog
   Associative Memories," cond-mat/0302029) found that SMOOTHING the nonlinearity (analog
   threshold-linear units), not sharpening it, is what killed 2- and 3-mixture spurious states in that
   model -- the opposite of the naive "harder WTA = fewer spurious attractors" intuition. k-WTA
   uniqueness proofs in the literature are existence proofs under fine-tuned gain/connectivity, not
   general anti-combinatorial-blowup theorems. Flagged explicitly as a commonly-conflated-but-not-
   equivalent claim.

4. **Neurogenesis / continuous capacity expansion -- RANKS LOWEST, mixed/negative evidence.** At least
   one computational-model literature result (Aimone et al., PMC4593858) reports neurogenesis can
   *paradoxically decrease* both pattern separation and interference performance in some regimes --
   not a clean, uniformly-positive mechanism. Not recommended as a rescue candidate.

**Overall calibrated verdict: candidate #1 (pattern-separation front-end) is the top practical
recommendation for a next GPU cell IF/WHEN the K5/K6 wall is confirmed -- not because its mechanism is
proven, but because (i) it is the cheapest to test (primitive already built and validated on this
substrate), (ii) it directly instantiates this substrate's own already-validated cross-cell law
(`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md`:
decorrelated/near-orthogonal codes raise capacity in this substrate's stores), and (iii) a clean
HARD-FAIL is itself informative (would show sparsity raises PURE capacity without touching BASIN
multiplicity -- exactly the gap the lit-scan flagged as unresolved in the literature). Candidate #2 is
the deeper, more brain-faithful answer but is scoped as a separate, larger redesign project, not this
cycle's test.**

---

## (b) Proposed GPU-testable cell (candidate #1) -- BUILD-GATED, do not dispatch yet

**Name (proposed): `exp_resonator_dg_frontend_ksweep_v1`**

**Design:** Wire `hdlab.hippocampal_encoder.DGProjection` (or a complex/FHRR-compatible port of it --
the existing class is bipolar/ternary-real; the resonator's codebooks are complex64 FHRR, so this is a
real, bounded adaptation task, not a drop-in reuse) in front of the resonator's per-factor codebook
generation: each of the K factor codebooks (M codewords, N dims) is generated at an EXPANDED dimension
`r*N` (propose `r=4`, matching the DGProjection selftest's `2-8x` target range), then top-K
magnitude-sparsified to a target active-rate `~0.02` (matching the DGProjection default), phase-preserved
for the nonzero entries. The resonator's multiplicative-unbind/alternating-projection decode then runs
natively over these sparser, more-decorrelated codebooks at the SAME K5/K6 that cratered in the smoke.
Compare `oracle_any(K5)`, `oracle_any(K6)` against the naive-codebook baseline
(`data/exp_resonator_ksweep_reachability_v1_smoke/metrics.json`: both 0.000).

**HARD-PASS (mechanism confirmed as load-bearing for basin-proliferation, promotes candidate #1 to a
real rescue):** `oracle_any(K5) >= 0.70` AND `oracle_any(K6) >= 0.40` (order-of-magnitude recovery from
the smoke's 0.000/0.000), on the SAME per-cell `<=1.5x` / aggregate `[0.80,1.25]` bands convention used
elsewhere in this cell family, multi-seed (>=3 seeds, paired against the naive baseline, per
[[feedback-paired-trials-mandatory]]).

**HARD-FAIL (informative negative -- decorrelation raises pure capacity, not basin count):**
`oracle_any(K5)` and `oracle_any(K6)` both remain `< 0.10` (no material rescue) across all seeds. This
would directly CONFIRM the lit-scan's own honest gap (Amit-Gutfreund-Sompolinsky-style mixture-state
suppression is temperature-driven, not sparsity-driven; Tsodyks-Feigelman sparsity gain is a
pure-pattern-capacity mechanism, not a basin-multiplicity mechanism) -- a genuine, reportable,
mechanism-clarifying negative, not a dead end.

**P_deflated for HARD-PASS: 0.30** (below the standard 0.50 novel-synthesis cap -- deflated further
because the lit-scan explicitly could not find a single paper directly linking input decorrelation to
reduced spurious-BASIN count, only to raised pure-pattern capacity; the mechanism this cell tests is a
plausible inference bridging two well-established-but-distinct results, not an established law).

**Gate: do not dispatch until skunkworks confirms the K-sweep FULL result is a genuine wall** (not a
harness/oracle/budget misconfig or saturation-vacuous null). If skunkworks instead finds the smoke wall
was an artifact, this cell's urgency drops to zero and it should be re-scoped as ordinary
scope-expansion work, not urgent rescue.

---

## (c) Falsifiable predictions

See (b) for the primary HARD-PASS/HARD-FAIL bands on the proposed cell. Two secondary, cheaper checks
worth running FIRST if/when the gate clears (both CPU-only, no GPU needed, per this substrate's own
existing tooling patterns):

1. **Decorrelation-transfer sanity check (numpy, CPU, minutes):** verify that `DGProjection`'s
   `_st_dg_pattern_separation` gap (measured on real-valued bipolar inputs) transfers to complex-phase
   FHRR codewords at the SAME sparsity/expansion settings, before spending GPU budget on the full
   resonator integration. HARD-PASS: measured `code_cos < input_cos - 0.15` on FHRR-analog complex
   codewords (slightly relaxed vs. the real-valued 0.20 gap, since phase decorrelation is a different
   geometry). HARD-FAIL: gap `< 0.05` (mechanism does not port to the complex representation at all --
   would kill candidate #1 before any GPU spend).
2. **Crosstalk-variance direct measurement (numpy, CPU):** at fixed K=4 (where the naive resonator
   still partially works, oracle_any=0.867), measure whether sparsified/expanded codebooks reduce the
   measured crosstalk-term variance in the unbinding step relative to the naive dense codebooks. This
   directly tests the Tsodyks-Feigelman-style mechanism (fewer/weaker crosstalk terms) independent of
   whether basin COUNT changes -- disentangles the two candidate explanations before the expensive K5/K6
   GPU test.

---

## (d) Cross-thread synthesis

- **Directly extends `research_resonator_basin_proliferation_self_predictability_2026-07-07.md`**
  (which confirmed the mechanism classification -- convergence-basin proliferation, AGS/TAP/K-SAT
  annealed-counting family -- via 3 independent lit-scans, `P_deflated=0.50` capped) by adding the
  brain-grounding half of the question: not just "what IS the failure," but "what does the best-in-class
  existence proof (the brain) do differently that might escape it." That note explicitly recommended, as
  its Follow-up 1, transferring this substrate's OWN validated ACF (Asymmetric Codebook Factorizer,
  cap_map row 51) rescue from the codebook-SIZE axis to the factor-COUNT axis. This note's candidate #1
  (DG pattern-separation front-end) is a DIFFERENT, complementary rescue mechanism from ACF -- ACF
  operates on the DECODE side (bit-flip mask + hard threshold on the reconstruction codebook), while the
  DG front-end operates on the ENCODE side (decorrelating the codebooks themselves before any decode
  runs). Both are cheap, both are precedented-on-this-substrate, and they are not mutually exclusive --
  a future cycle could test them jointly.
- **Directly instantiates `reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md`**
  (decorrelated/near-orthogonal codes raise capacity in this substrate's stores/composition; semantic
  correlation hurts). Candidate #1 is exactly this law applied to the resonator's factor codebooks --
  the SAME substrate-wide pattern, not a new one, which raises confidence this is at least
  well-precedented-on-THIS-substrate even where the general literature is honestly incomplete.
- **Confirms and sharpens `research_resonator_reachability_ceiling_2026-07-07.md`**, which found the
  K3/K4 residual was PRIMARILY a restart-budget problem (not a basin-measure wall) but explicitly flagged
  the K5/K6 question as the real open CG_META risk and recommended exactly the K-sweep now in flight as
  the decisive test. The smoke result now in hand (`K5=0.000, K6=0.000`, `HARD_FAIL "WALL_FUNDAMENTAL"`)
  is consistent with that note's Prediction B HARD-FAIL band (`p_basin(K6) < 0.01`) -- but per the live
  coordinator gate, this is SMOKE ONLY and not yet skunkworks-confirmed as genuine (vs. e.g. an R-budget
  or T0-grid misconfiguration specific to the smoke harness).
- **Prior substrate scour (this cycle, targeted grep, not broad crawl):** `hdlab/hippocampal_encoder.py`
  (DGProjection/CA3AutoAssociator, built + 13 passing selftests, applied only to
  `exp_bet_b_moe_per_task_dg_gating_v1_n2048` and `exp_sbc_charlm.py`, NEVER to any resonator cell);
  `notes/research_drill_biological_precedents_animal_scales_substrate_2x_2026-06-04.md` (independently
  names DG pattern separation + CA3 pattern completion + theta phase coding as the three relevant mouse
  hippocampus mechanisms, unprompted, two months before this drill); `tools/composition_landings_analysis.py`
  (theta-gamma nested oscillation substrate history: HARD_FAIL then brain-compensated variant, composition
  context, not resonator); `hdlab/director_kb_bio_sources.py` (DG/CA3/entorhinal KB graph entries, context
  only). No prior cell found that applies expansion+sparsify decorrelation to the resonator's
  factor-count axis specifically -- this is a genuinely un-drilled adjacency, not a re-run of a dead
  family.

---

## (e) Substrate-product implications

- **No product claim changes today.** The K5/K6 wall is smoke-only and unconfirmed; nothing here
  asserts a new capability or a new limit as fact.
- **If the wall is confirmed AND candidate #1 HARD-PASSes:** the product gains a second, complementary,
  cheap rescue path for K-way joint factorization (alongside the already-validated ACF codebook-size
  rescue) reusing an EXISTING, already-tested substrate primitive (`DGProjection`) -- low marginal
  engineering cost, since the primitive is not being invented, only re-wired and adapted to complex
  FHRR codewords.
- **If the wall is confirmed AND candidate #1 HARD-FAILs:** still valuable -- it would cleanly separate
  "sparsity raises pure-pattern capacity" (well-established, keep using this substrate-wide) from
  "sparsity suppresses basin-count proliferation" (would now be substrate-specific evidence AGAINST,
  closing that inference cleanly rather than leaving it as an open unproven assumption).
  It would also elevate candidate #2 (theta-gamma phase-slotting -- a genuine re-encoding redesign, not
  a decode-side patch) as the next, more expensive thing to scope, consistent with this substrate's own
  prior partial theta-gamma attempt needing brain-compensation to work at all.
- **If skunkworks instead finds the smoke wall was a harness artifact:** this note's ranking and
  candidate remain valid capability-groundwork for a future genuine K5/K6 test, but nothing here should
  be treated as urgent until that recurs with a confirmed FULL-run wall.

---

## (f) Citations (verified count)

**Lit-scan sub-agent 1 (pattern separation / decorrelation-capacity link), 10 sources:**
Marr, "Simple memory: a theory for archicortex," Phil. Trans. R. Soc. B (1971); Rolls (1989);
Treves & Rolls, "Computational analysis of the role of the hippocampus in memory," Hippocampus 4:374
(1994); O'Reilly & McClelland, "Hippocampal conjunctive encoding, storage, and recall," Hippocampus 4:661
(1994); Leutgeb, Leutgeb, Moser & Moser, "Pattern separation in the dentate gyrus and CA3 of the
hippocampus," Science 315:961-966 (2007); GoodSmith et al., eLife 6:e20252 (2017); Yassa & Stark,
"Pattern separation in the hippocampus," Trends Neurosci 34:515 (2011); Amit, Gutfreund & Sompolinsky,
Phys. Rev. A 32:1007 (1985); Tsodyks & Feigelman, Europhys. Lett. 6:101 (1988); Buhmann, Divko & Schulten,
Phys. Rev. A 39:2689 (1989).

**Lit-scan sub-agent 2 (spurious-fixed-point scaling under K-way joint binding), 9 sources:**
Amit, Gutfreund & Sompolinsky, "Statistical mechanics of neural networks near saturation," Ann. Phys.
(1987); Newman, "On the number of spurious memories in the Hopfield model," IEEE Trans. Info. Theory
(1988); Tsodyks & Feigelman, Europhys. Lett. 6:101 (1988) [cross-cited]; "Disappearance of Spurious
States in Analog Associative Memories," cond-mat/0302029; "Collective stability of networks of
winner-take-all circuits," arXiv:1105.3106; "The Algorithmic Phase Transition of Random k-SAT,"
arXiv:2106.02129; "The Condensation Phase Transition in the Regular k-SAT Model," Dagstuhl
LIPIcs.APPROX-RANDOM.2016.22; Aimone et al., "Contributions of adult neurogenesis to dentate gyrus
network activity and computations," PMC6724741; "Neurogenesis paradoxically decreases both pattern
separation and memory interference," PMC4593858.

**Lit-scan sub-agent 3 (theta-gamma phase-multiplexing vs. simultaneous resolution), 7 sources:**
Lisman & Idiart, "Storage of 7±2 short-term memories in oscillatory subcycles," Science 267:1512 (1995);
Jensen & Lisman (2005); Lisman & Jensen, "The Theta-Gamma Neural Code," Neuron (2013); Axmacher et al.,
"Cross-frequency coupling supports multi-item working memory in the human hippocampus," PNAS 107:3228
(2010); Kaminski et al. (2011); Malenínská et al., Neurobiology of Learning and Memory (2021,
non-replication); Balagué & Dempere-Marco, BMC Neuroscience 16(Suppl 1):P58 (2015); "Theta oscillations
optimize a speed-precision trade-off in phase coding neurons," PLOS Comp. Biol. (2024).

**Internal/substrate sources (on-disk, verified this drill):** `hdlab/hippocampal_encoder.py` (full
read, DGProjection/CA3AutoAssociator + 13 selftests, all passing per source);
`data/exp_bet_b_moe_per_task_dg_gating_v1_n2048/metrics.json` (DG-analog primitive's one prior landed
application, MIDDLE_BAND); `notes/substrate_capability_map.md` (cap_map cross-reference, DG-gating
NO_METRICS crash noted at N=2048 in a different run, informational only);
`data/exp_resonator_ksweep_reachability_v1_smoke/metrics.json` (source of the smoke numbers this drill
grounds); `notes/research_resonator_basin_proliferation_self_predictability_2026-07-07.md`,
`notes/research_resonator_reachability_ceiling_2026-07-07.md` (direct prior-cycle context, read in
full); `notes/research_drill_biological_precedents_animal_scales_substrate_2x_2026-06-04.md`;
`tools/composition_landings_analysis.py` (theta-gamma substrate history); `hdlab/director_kb_bio_sources.py`;
`tools/orchestrator/research_field_advisor.py` (run this cycle: `dynamics` field remains closed at 0%,
distinct from this drill's basin-counting phenomenon per the 2026-07-07 note's own resolution of that
question).

**Total: 26 external literature sources (3 independent Sonnet lit-scan sub-agents, WebSearch/WebFetch
verified) + 10 internal on-disk sources = 36 verified sources/checks. Zero new GPU/CPU trials of the
resonator capability itself this cycle -- pure brain-grounding + prior-work scour + one concrete,
gated cell proposal.**

## P_deflated summary

- **Mechanism ranking (candidate #1 > #2 > #3 > #4 for THIS resonator's specific failure mode):** raw
  confidence 0.55-0.60 (three independent, honest lit-scans; substrate's own DG primitive already
  validated the pattern-separation property in a different context). Novel-synthesis cap applies (no
  single source ranks these four mechanisms against THIS specific resonator problem) -> **P_deflated =
  0.50** (capped).
- **Candidate #1 cell HARD-PASS probability (if dispatched, gated on skunkworks confirmation):
  P_deflated = 0.30** (deflated below the standard cap; the specific causal link tested -- decorrelation
  reduces basin count, not just pure-pattern capacity -- was explicitly NOT found proven in the
  literature by the lit-scan, making this an honest coin-flip-leaning-negative bet, not a
  confident rescue).
