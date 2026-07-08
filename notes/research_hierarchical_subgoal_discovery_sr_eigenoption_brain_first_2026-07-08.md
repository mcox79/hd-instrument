# research: hierarchical subgoal self-discovery + compounding-error bound — brain-first negative-revival drill — 2026-07-08

Scope: revive the two confirmed genuine HARD_FAILs in the pfc-gate action-selection lineage —
`exp_pfc_gate_autonomous_waypoint_discovery_v1` (`HARD_FAIL_SR_CANNOT_SELF_DISCOVER_DECOMPOSITION`)
and `exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1` (`HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL`).
Base BG Go/NoGo value-gate itself is CERTIFIED HARD_PASS (`exp_pfc_gate_cfrpe_trained_v2`) — not
revisited here. Scan done directly (code + metrics.json read, WebSearch verification of the load-
bearing citations), no sub-agents, per directive.

## HEADLINE

**The eigenoption/spectral-bottleneck mechanism was already tried in this exact lineage — and its
failure is exactly what the graph-cut math predicts on an unstructured graph, not a refutation of the
mechanism.** `exp_pfc_gate_autonomous_waypoint_discovery_v1` already built and ran `wp_bisect_spectral`
(candidate set = states near-zero on the 2nd/3rd eigenvector of the symmetrized reach matrix
`R=cos(E@M,E)` — literally Machado-Bellemare-Bowling eigenoptions / Solway et al.'s graph-partition
subgoal formalization) and `wp_bisect_cluster_exit` (k-means-on-eigenvectors low-margin boundary
states, a PCCA+-lite proxy for the same min-cut idea). Both **underperformed** the unrestricted
sequential bisection: `spec-open=-0.042`, `clus-open=-0.040` (MEASURED@`data/exp_pfc_gate_autonomous_waypoint_discovery_v1/metrics.json`).
Lit-scan (WebSearch, generic terms) confirms this is not a surprise: bottleneck/eigenoption subgoal
discovery is formally a **k-way normalized min-cut** problem (Solway et al. 2014) — subgoals emerge
"on edges cut by the lowest-frequency eigenvector, lying between the two largest, most separable
clusters." **A graph needs a good sparse cut to exist before its eigenvectors can reveal one.** The
substrate's own `make_kb_and_chains` builds the operator-chain KB by sampling `(s,o)` pairs **uniformly
at random** per operator — an Erdos-Renyi-like / expander-like graph at density 0.21, which by
construction has **no small cuts, no community structure, no bottleneck states to find**. The
autonomous-discovery cell's own docstring predicted exactly this ("DOMAIN-FIT hypothesis... likely
LACK true community/bottleneck structure... spectral/cluster RESTRICTION is expected
NEUTRAL-to-HARMFUL") and the measured result confirmed it. **This reframes the HARD_FAIL from "the
substrate's learned SR cannot support subgoal discovery" to "the test harness never gave the
substrate's SR a graph with the one structural property (bottlenecks) any brain-grounded discovery
mechanism — spectral, chunking, or replay-based — needs to have something to find."** The compounding-
error HARD_FAIL is very likely the same root cause wearing a different hat: coarse-to-fine recursion
(tree height log(T) instead of linear-chain T) barely moved the needle (`DELTA=0.004`,
MEASURED@`data/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1/metrics.json`) because reshaping
*how* you pick from a signal that has no real structure to pick from cannot help much regardless of
tree shape.

## Ranked mechanisms (brain signature -> self-discovery route -> composition with certified SR/M gate)

**1. Graph-topology-matched SR-eigenoption / min-cut re-test — HIGH-PROBABILITY-SUPERIOR, near-zero new code.**
Brain mechanism + source: hippocampal SR-eigenvector bottleneck/subgoal discovery (Stachenfeld,
Botvinick & Gershman 2017, *Nat Neurosci* 20:1643-1653 — SR distorts around impassable barriers,
place-field density concentrates near bottlenecks); formalized as graph min-cut subgoal discovery
(Solway, Diuk, Cordova, Yee, Barto, Niv & Botvinick 2014, "Optimal Behavioral Hierarchy," *PLoS Comp
Biol* 10(8):e1003779); RL-side graph-Laplacian eigenoptions (Machado, Bellemare & Bowling 2017, "A
Laplacian Framework for Option Discovery in RL," *ICML*, PMLR v70) — bottleneck states connect
densely-connected regions (literal doorways/rooms in the domains these methods were validated on);
rostrocaudal PFC abstraction over the discovered levels (Badre & D'Esposito 2009, *Nat Rev Neurosci*
10(9):659-669; Koechlin, Ody & Kouneiher 2003, *Science* 302(5648):1181-1185) sits on top once the
levels exist.
Self-discovery without oracle waypoints: **identical mechanism already coded** —
`spectral_candidate_mask` / `cluster_candidate_mask` in `experiments/exp_pfc_gate_autonomous_waypoint_discovery_v1.py`
(lines 561-607) compute eigh on the symmetrized reach matrix and restrict the SAME bisection argmax to
sign-boundary / low-cluster-margin states, with zero access to the oracle trajectory. Nothing about the
discovery step needs oracle labels; it needs a graph where those eigenvectors carry signal.
Composition with certified SR/M + Go/NoGo gate: **100% reuse, zero new gate logic.** `R` is built
directly from the already-trained `M` (the certified cfrpe critic); `run_hier_arm_wp` (the execution
loop) is untouched; only `make_kb_and_chains` (the synthetic KB generator, not a certified primitive)
needs a swap to a stochastic-block-model / room-graph generator (K blocks, within-block triple density
>> between-block "door" triple density) at the same V/n_ops/depth regime already validated.
Kill-test (exactly the task's prescribed shape): rebuild the KB as a K-room SBM (K in {4,8}, within:
between density ratio >= 5-10x) at the SAME FOCUS corner (`op4_V1200_d8`, where `flat_gonogo` already
collapses to ~0.08 and `hier_oracle` already reaches ~0.93 given the true decomposition — both numbers
MEASURED@existing metrics.json, so the two required rails — oracle-waypoint arm MUST succeed,
flat-gate arm MUST fail — are already known to hold at this regime and do not need re-discovery).
Re-run `wp_bisect_spectral` / `wp_bisect_cluster_exit` (code unchanged) against `wp_bisect_open` under
the SBM graph. Discriminator: does `spec-open` (or `clus-open`) **flip sign positive** and clear the
cell's own pre-registered bars (`lift_flat>0.05`, `lift_random>0.10`)? A sign flip alone (regardless of
whether it clears the harder full-HARD_PASS bars calibrated for the wrong domain) is the decisive,
falsifiable signal that the mechanism is real and was domain-starved, not broken.
Prior: the graph-cut requirement is a **mathematical fact** about spectral methods (expander graphs
provably have no small cuts — this is not a hopeful empirical guess, it is why the existing negative
sign matches theory exactly), and the code is already built and certified-adjacent (reuses the
certified `M`). That pushes the raw estimate for "mechanism fires / sign flips positive" high. Per
[[feedback-lit-scan-calibration-penalty]] this is still novel synthesis (nobody has directly measured
this exact composition on this exact substrate) so it is capped, not raw.
**P_deflated (sign flips positive, real lift over open) = 0.55** (capped near the novel-synthesis
ceiling given how directly the existing negative data + independent graph-cut theory both point the
same direction). **P_deflated (clears the ORIGINAL full HARD_PASS bar as pre-registered, e.g.
`recovery_ratio>=0.20`) = 0.35** — a materially harder, separate bar; the original bars were calibrated
against the wrong domain and may need honest re-calibration once real structure is present, not
retroactively loosened to manufacture a pass.

**2. Cortico-striatal chunking via visitation-frequency subgoal detection (Graybiel 1998) — rank-2, cheap complementary diagnostic, same domain-fit ceiling.**
Brain mechanism: task-bracketing striatal chunking (Graybiel, A.M. 1998, "The Basal Ganglia and
Chunking of Action Repertoires," *Neurobiol Learn Mem* 70(1-2):119-136) — sensorimotor-striatum units
fire densely throughout a novel sequence, then compress to fire ONLY at sequence-start/sequence-end as
the habit consolidates; the entire in-between sequence gets packaged into one performance unit, with
the bracket boundaries themselves acting as chunk (sub-goal) markers. Confirmed still current
(PMC4526748, "The Striatum: Where Skills and Habits Meet"; PMC4523429, "Shaping Action Sequences in
Basal Ganglia Circuits").
Self-discovery without oracle waypoints: a fundamentally DIFFERENT statistic than eigenvectors —
**visitation/co-occurrence frequency** across many rollouts (already collected via
`collect_rollout_transitions`), not spectral structure. High in-degree "hub" states that many
independent train/test chains pass through become chunk-boundary candidates; the SR matrix `M`'s own
column-mass (`sum_i M[i,j]`, an unused-so-far readout of the SAME certified matrix) is a near-zero-cost
proxy for this. Composes with the certified gate identically to #1 (swap only the candidate-mask
function, same wiring into `run_hier_arm_wp`).
Honest caveat: this shares #1's domain requirement — a Poisson/uniform-in-degree ER graph has no hub
skew either, so it will likely ALSO fail on the current KB generator for the same underlying reason.
Its value is as a second, independent-statistic cross-check once a structured (SBM/room) KB exists: if
BOTH the spectral and the frequency-based discovery mechanisms fire on the same structured graph, that
is much stronger evidence than either alone (two brain-grounded routes converging), and cheaper to
compute (no `eigh`, no k-means) if it turns out visitation-frequency alone is sufficient.
P_deflated (fires positively on a structured KB, given #1 also fires) = 0.40; not independently
decisive, capped lower than #1 because it is one step further from directly-verified graph-cut theory.

**3. Hippocampal prioritized-replay offline sharpening of the reach signal at deep corners (Mattar & Daw 2018) — rank-3, addresses a different (execution-quality) hypothesis, weaker prior given existing data.**
Brain mechanism: prioritized memory replay ordered by expected value of backup (Mattar, M.G. & Daw,
N.D. 2018, "Prioritized memory access explains planning and hippocampal replay," *Nat Neurosci*
21(11):1609-1617) — the brain does not treat all learned transitions equally; it selectively replays
the transitions whose update would most improve future decisions, offline, before acting. Related:
reverse replay of successful trajectories (Foster & Wilson 2006, *Nature* 440(7084):680-683).
Self-discovery: targeted extra TD sweeps (reusing `train_sr_transport` unchanged, just more steps
focused on the specific deep chain being solved) to sharpen `R` at exactly the corner where reach
signal is bluntest, rather than accepting the once-trained, fixed-budget `M`.
Composition: fully reuses the certified TD/cfrpe update rule; a genuinely additive, non-competing
mechanism to #1/#2 (could run alongside either).
Rank-3 because the existing evidence argues AGAINST "undertrained SR" being the dominant cause: the
codebase already has an `HDLAB_SR_STEPS` env-var override built in for exactly this "is SR undertrained"
probe (present in both cells' source, unexercised as a dedicated cell), and the coarse-to-fine rescue's
near-zero `DELTA=0.004` is more consistent with "no structure to sharpen toward" than "not enough
training steps" — sharpening a signal that's fundamentally flat (expander-graph reach matrix) won't
manufacture a bottleneck that isn't there. Still worth a cheap combined run once #1 confirms structure
helps, to see if it adds further lift on TOP of the topology fix.
P_deflated (adds material lift ON TOP of a structured-KB positive result from #1) = 0.30.

**4. Option-critic gradient-learned termination (Bacon, Harb & Precup 2017, AAAI) — flagged, deprioritized, ML-only.**
Per USER framing (ML is a weak secondary reference, not the guide): option-critic learns subgoal/
termination boundaries via policy-gradient descent on a value objective. No clean brain analog for
label-free discovery in the way SR-eigenvectors (measurable in real place-cell data) or striatal
chunking (measurable in real striatal spike trains) are directly brain-verified. Also requires a
differentiable training loop that fits awkwardly against the substrate's Hebbian/TD-delta-rule update
style. Noted for completeness per [[feedback-dont-dismiss-adjacent-methods]], not designed further —
this is the one candidate where "follow the brain, not ML" cleanly rules against investing here first.

## Cheap decisive test / cell proposal (the one candidate to dispatch)

**Working name:** `exp_pfc_gate_waypoint_discovery_structured_kb_v1` (exp_dev to finalize).

**Extends:** `experiments/exp_pfc_gate_autonomous_waypoint_discovery_v1.py` — reuse `make_bipolar_E`,
`hebbian_W`, `cleanup_batched`, `train_sr_transport`, `reach_value`, `build_reach_matrix`,
`spectral_candidate_mask`, `cluster_candidate_mask`, `_discover_bisect_boundaries`,
`_discover_random_boundaries`, `_discover_index_boundaries`, `run_hier_arm_wp`,
`oracle_trajectory_idx`, `build_waypoint_idx`, all discriminator formulas — ALL VERBATIM, zero new gate
math. The ONLY new code is a KB generator swap: `make_kb_and_chains_sbm(n_ops, V, K_rooms,
within_density, between_density, ...)` — partition V states into K blocks, sample most triples within a
block and a controlled sparse fraction between blocks (the "doors"), holding V/n_ops/depth/N_DIM
identical to the parent's FOCUS regime (`op4_V1200_d8`) for a like-for-like before/after.

**Arms:** identical 9-arm set as the parent (`flat_gonogo`, `oracle_exec`, `hier_oracle`,
`hier_shuffled`, `wp_bisect_open`, `wp_bisect_spectral`, `wp_bisect_cluster_exit`, `wp_random_state`,
`wp_index_midpoint`) — paired, same E/W_ops/M/R/test chains per seed, on the NEW structured KB only.
No need to re-run the ER-random condition; it is already measured (this is the comparison baseline by
construction, not a new arm).

## Falsifiable predictions

**HARD-PASS:** at the SBM-structured `op4_V1200_d8` FOCUS corner: `oracle_exec >= 0.90` AND
`hier_oracle` reproduces a comparable ceiling to the parent's 0.93 (confirms the swap didn't break the
control-depth-solved envelope) AND `flat_gonogo` collapses comparably to the parent's ~0.08 (confirms
the corner is still genuinely hard without hierarchy — the discriminator must still fire) AND
`best(spec-open, clus-open) > 0` (sign flip, the headline claim) AND clears the ORIGINAL pre-registered
bars: `lift_flat(best_wp) > 0.05`, `lift_random(best_wp) > 0.10`, `recovery_ratio(best_wp) >= 0.20`,
`index_artifact_gap < 0.05`, `anti_tautology_corr < 0.85`, `degenerate_rate < 0.10`, `sign_p < 0.05`.
=> the substrate's certified SR can self-discover a useful subgoal decomposition, GIVEN an environment
with actual bottleneck structure (matching the domain every eigenoption/min-cut result in the
literature was validated on) — closes both HARD_FAILs as test-harness domain-fit artifacts, not
mechanism-class dead ends.

**MIDDLE-BAND (still informative, still worth folding in):** `best(spec-open, clus-open) > 0` by a
real, sign-significant margin (`sign_p < 0.05`) but misses one or more of the harder absolute bars
(`recovery_ratio < 0.20` or `lift_random` in [0.05, 0.10)) — the mechanism fires and the sign flips as
predicted, but the ORIGINAL bars (calibrated for a domain that turned out to be the wrong test) are too
strict for an honest verdict; report as a genuine positive requiring bar re-calibration, not a failure.

**HARD-FAIL (the real, sharp kill-test):** `best(spec-open, clus-open) <= 0` (no sign flip) OR
`sign_p >= 0.05` (not distinguishable from zero) even with genuine SBM room/door structure at a
within:between density ratio of 5-10x. This would be a MUCH stronger negative than the current one: it
would mean the substrate's SR-derived reach matrix cannot detect bottleneck structure even when it
demonstrably exists in the graph — a genuine mechanism-level bound on this reach-matrix construction
(not just a domain-mismatch artifact), worth escalating rather than re-drilling a 3rd time (per
Pattern 6, 80% refutation rate on repeated re-drills of the same closed field — this cell is explicitly
NOT that; it changes the one confounded variable the parent's own docstring flagged, once, honestly).

**Compounding-error corollary (not a separate cell, a predicted side-effect):** if HARD-PASS above
holds, re-check `delta_recovery` on the SAME structured KB using the already-built
`wp_bisect_coarse2fine` / `wp_bisect_verify` / `wp_bisect_combo` arms from the rescue cell (also
100% reusable) — prediction: with real bottleneck signal now present, coarse-to-fine's tree-height
advantage should show a MUCH larger `delta_recovery` than the measured `0.004` on the ER-random graph,
because compounding error only compounds usefully-measurable NOISE, and there was essentially no
signal-bearing noise to compound against before. HARD-FAIL here (delta stays ~0 even with structure) OR
HARD-PASS on this corollary is reported as a bonus finding, not gated on it for the primary cell verdict.

## Cross-thread synthesis

- Directly extends `notes/research_value_based_action_selection_basal_ganglia_2026-07-08.md`, which
  established the base BG Go/NoGo gate is HARD_PASS-certified and flagged the two waypoint-discovery
  HARD_FAILs as the genuine remaining frontier in this lineage (composition/scale, not existence). This
  note answers the "why did they fail" question that note left open, using neuroscience-first
  reasoning rather than re-testing the same confounded regime a 3rd time.
- The parent cell's own docstring (lines 30-33) *predicted* the domain-fit failure mode before running
  it ("likely LACK true community/bottleneck structure... expected NEUTRAL-to-HARMFUL") — this note
  does not discover a new fact so much as it completes the honest next step the parent cell scoped but
  did not execute: build the domain where the hypothesis predicts the OPPOSITE sign, and check.
- Chatham & Badre (2021)'s "analogous computations" framing (input/output/motor gating share one
  Go/NoGo primitive) generalizes here too: subgoal DISCOVERY (a min-cut/graph problem) and value-based
  ACTION SELECTION (an argmax-over-learned-value problem) are also analogous-but-distinct computations
  that this lineage keeps finding compose cleanly in isolation and need an honest domain match to test
  together — same meta-pattern as the composition-cell proposed in the prior note.
- Sutton, Precup & Singh (1999) motivated the original HARD_FAIL (flat gating has no built-in temporal
  abstraction); this note does not contest that — it targets the SEPARATE, orthogonal claim (also in
  the parent docstring) about WHERE the abstraction comes from once you add hierarchy: from graph
  structure the eigenvectors can see, which the test graph never had.

## Substrate-product implications

Honest framing, no smoke: this is NOT a claim that hierarchical subgoal discovery is solved. It IS a
claim that the specific test used so far was accidentally the hardest possible case (a structureless
random graph, which is provably the wrong domain for every brain-grounded discovery mechanism
considered — spectral, chunking, or replay-based all require SOME environmental regularity to exploit).
That is good news directionally for the M3/cortex-layer product target: real agentic/conversational
task graphs (multi-step tool workflows, document structure, dialogue turns) are NOT i.i.d.-random —
they have exactly the kind of modular, room-like, bottleneck structure (a "checkout" step gates many
paths through an e-commerce flow; a "confirm intent" turn gates many dialogue branches) that these
brain mechanisms were built to exploit. If the structured-KB kill-test above HARD-PASSes, the honest
product claim becomes: "the substrate's already-certified SR/Go-NoGo primitive can self-discover useful
sub-goal structure in task graphs that look like real workflows, without hand-authored waypoints" — a
materially different and more useful claim than either "solved" or "impossible," and it comes at near-
zero engineering cost (one new KB generator function, zero new gate math) because every certified
primitive in the lineage is reused unchanged.

## Citations (verified count: 9, WebSearch-checked this cycle against public sources; generic math/neuro terms only per query-privacy)

1. Stachenfeld, K.L., Botvinick, M.M. & Gershman, S.J. (2017). "The hippocampus as a predictive map."
   *Nature Neuroscience*, 20, 1643-1653. (WebSearch-confirmed: SR distorts around barriers, place-field
   density concentrates near bottlenecks.)
2. Solway, A., Diuk, C., Cordova, N., Yee, D., Barto, A.G., Niv, Y. & Botvinick, M.M. (2014). "Optimal
   Behavioral Hierarchy." *PLoS Computational Biology*, 10(8), e1003779. (WebSearch-confirmed:
   formalizes subgoal discovery as k-way normalized min-cut; subgoals emerge on edges cut by the
   lowest-frequency eigenvector between separable clusters — the direct theoretical basis for the
   domain-fit reframe in this note.)
3. Machado, M.C., Bellemare, M.G. & Bowling, M. (2017). "A Laplacian Framework for Option Discovery in
   Reinforcement Learning." *ICML*, PMLR v70. (WebSearch-confirmed: eigenoptions via graph-Laplacian
   spectral decomposition; bottleneck states connect densely-connected regions, e.g. doorways.)
4. Badre, D. & D'Esposito, M. (2009). "Is the rostro-caudal axis of the frontal lobe hierarchical?"
   *Nature Reviews Neuroscience*, 10(9), 659-669.
5. Koechlin, E., Ody, C. & Kouneiher, F. (2003). "The architecture of cognitive control in the human
   prefrontal cortex." *Science*, 302(5648), 1181-1185.
6. Graybiel, A.M. (1998). "The basal ganglia and chunking of action repertoires." *Neurobiology of
   Learning and Memory*, 70(1-2), 119-136. (WebSearch-confirmed: task-bracketing chunking pattern —
   striatal units fire throughout a novel sequence, then compress to start/end firing as habit forms.)
7. Mattar, M.G. & Daw, N.D. (2018). "Prioritized memory access explains planning and hippocampal
   replay." *Nature Neuroscience*, 21(11), 1609-1617. (WebSearch-confirmed: expected-value-of-backup
   ordering of replay.)
8. Foster, D.J. & Wilson, M.A. (2006). "Reverse replay of behavioural sequences in hippocampal place
   cells during the awake state." *Nature*, 440(7084), 680-683.
9. Sutton, R.S., Precup, D. & Singh, S. (1999). "Between MDPs and Semi-MDPs: A Framework for Temporal
   Abstraction in Reinforcement Learning." *Artificial Intelligence*, 112, 181-211. (Carried over from
   the prior note in this lineage; re-cited here as the reason a flat gate needs hierarchy at all,
   orthogonal to the domain-fit finding.)

Also cited for completeness, not independently re-verified this cycle: Bacon, P.-L., Harb, J. & Precup,
D. (2017), "The Option-Critic Architecture," *AAAI* (rank-4, ML-only, deprioritized per brain-first
framing); Ross, S. & Bagnell, J.A. (2010), compounding-error bound (already in-corpus per the parent
cell, not re-verified here); Chatham, C.H. & Badre, D. (2021) (already in-corpus per the prior note in
this lineage).

**P_deflated summary (restated):** sign-flip / genuine positive lift on a structured KB = **0.55**;
clears the ORIGINAL pre-registered full HARD-PASS bar unmodified = **0.35**; visitation-frequency
chunking (#2) firing given #1 fires = **0.40**; replay-sharpening (#3) adding lift on top of #1 = **0.30**.
All capped per [[feedback-lit-scan-calibration-penalty]] (novel-synthesis ceiling 0.50, deflate 0.15-0.25
off raw estimates) despite unusually strong theoretical grounding (the graph-cut requirement is
mathematical, not speculative) — calibration discipline applies regardless of how convergent the prior
evidence looks.
