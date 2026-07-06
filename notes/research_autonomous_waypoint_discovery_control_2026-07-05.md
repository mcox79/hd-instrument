# RESEARCH DRILL — Autonomous Waypoint/Sub-Goal Discovery (follow-on to control-depth-solved)

**Date:** 2026-07-05
**Author:** research (Sonnet 5)
**Trigger:** Director steer. Control depth is HARD_PASS at FULL *given a correct decomposition*:

```
MEASURED@data/exp_pfc_gate_branching_depth_entropy_grid_v1/metrics.json
FOCUS=op4_V1200_d8(entropy=16.0) FLAT=0.082 HIER=0.861 SHUF=0.000 ORACLE=0.938
hier_closure=0.910 hier_lift=0.779 shuf_gap=0.861 reach_tcos_corr=-0.035
sign_p=9.2e-261 reach_rank=0.450(min 0.300) cv=0.050 oracle_rail=True af_collision=False
Full grid (flat/hier/shuf/oracle/closure/entropy):
  op2_V800_d4  0.904/0.938/0.070/0.957 closure=0.635 ent=4.0
  op2_V800_d6  0.547/0.922/0.013/0.950 closure=0.930 ent=6.0
  op2_V800_d8  0.202/0.902/0.006/0.936 closure=0.953 ent=8.0
  op3_V1000_d4 0.742/0.943/0.026/0.963 closure=0.906 ent=6.3
  op3_V1000_d6 0.191/0.917/0.003/0.947 closure=0.960 ent=9.5
  op3_V1000_d8 0.087/0.877/0.003/0.928 closure=0.939 ent=12.7
  op4_V1200_d4 0.514/0.937/0.009/0.960 closure=0.948 ent=8.0
  op4_V1200_d6 0.117/0.908/0.000/0.947 closure=0.954 ent=12.0
  op4_V1200_d8 0.082/0.861/0.000/0.938 closure=0.910 ent=16.0
```

The waypoints in `hier_options` are `oracle_trajectory_idx(...)` — **the true intermediate states of
the chain**, an assumed-optimal top-level option policy handed to the arm (see
`experiments/exp_pfc_gate_branching_depth_entropy_grid_v1.py:598-632`, docstring lines 34-39: "SUB-GOAL
SOURCE (declared oracle-assist, scoped honestly)... Autonomous waypoint DISCOVERY is an explicit
FOLLOW-ON, not claimed here."). This drill answers that follow-on: **can the substrate supply its own
decomposition from what it has already learned (E, W_ops, trained M), with no oracle trajectory?**

This is a narrow glass-box control-mechanics question. It is explicitly connected to, but does not
constitute, the self-improvement/self-reasoning north star: a system that structures its OWN
sub-problems is doing one small piece of "reasoning about how to solve," not autonomous
self-improvement. **USER-LOCKED scope: this is a sub-goal-discovery primitive step, nothing more.**

---

## SUBSTRATE-MINE FIRST (what already exists, verified on disk)

From `exp_pfc_gate_branching_depth_entropy_grid_v1.py` and its ancestor `exp_pfc_gate_cfrpe_trained_v2.py`:

- `E` — `[V, n_dim]` bipolar codebook, row-normalized (`make_bipolar_E`).
- `W_ops` — one Hebbian outer-product matrix per operator, `hebbian_W`.
- `cleanup_batched` — nearest-neighbor argmax cosine against `E` (the substrate's only readout primitive).
- `M` — **already a learned successor-representation (SR) transport matrix**, trained by TD(0) on
  random-walk exploration rollouts: `E[cur]@M ~= E[nxt] + gamma*(E[nxt]@M)`, `gamma=0.85`
  (`train_sr_transport`). This is literally Dayan-1993 SR / Stachenfeld-2017 hippocampal-predictive-map
  machinery, already trained and already load-bearing in the passed cell.
- `reach_value(cand, target, M) = cos(E[cand]@M, E[target])` — the "does this move toward target"
  signal already used by the flat and hier gates.
- Nothing on disk builds a **state-by-state reach matrix** (`R[i,j] = reach_value(E[i], E[j], M)` for
  all `i,j` in the codebook) or does anything graph-spectral with it. This is the one genuinely new
  primitive this drill proposes, and it is a near-zero-cost addition: `Efwd = normalize_rows(E @ M);
  R = Efwd @ normalize_rows(E).T` — one `[V,n_dim]x[n_dim,V]` matmul, computed once per `(seed,V,n_ops)`
  group exactly like `M` itself (V is 800-2400 in the FULL grid — trivial GPU cost).

No prior substrate cell or note addresses SR-eigenoptions, betweenness/min-cut subgoal discovery, or
PCCA-style metastable clustering (grep of `notes/` for `waypoint|subgoal|eigenoption|landmark|bottleneck`
returns only the BlocksWorld-domain hierarchical-planning line from 2026-06-27/28, which used a
different mechanism class — closed-form D-prediction / hand-defined options with I/pi/beta channels —
and closed on a different domain entirely. That line is not directly reusable here; the operator-chain
domain and its trained-SR machinery are new since 2026-07-05.)

---

## LIT-SCAN SYNTHESIS (4 parallel Sonnet sub-agents, generic math queries, 40 citations total)

### Thread 1 — SR eigenoptions / betweenness bottleneck discovery
**Machado, Bellemare, Bowling 2017** (ICML, "A Laplacian Framework for Option Discovery"): eigenoptions
from eigenvectors of the graph Laplacian; smoother (lower-eigenvalue) eigenvectors span longer
timescales. **Machado et al. 2018** (ICLR, "Eigenoption Discovery through the Deep Successor
Representation") is the single most directly relevant paper found: eigenoptions extracted from a
**learned** SR matrix (not ground truth), with a direct quantitative approximate-vs-exact comparison
showing graceful degradation as the SR converges — the only method in the whole scan with that property
measured. **Şimşek-Barto 2004/2005/2009** (relative novelty -> local graph partitioning -> betweenness
centrality): cheap, local, sample-based, but explicitly documented to misfire "in dense/well-connected
graphs lacking true bottlenecks." **McGovern-Barto 2001** (diverse density) and **Menache-Mannor-Shimkin
2002** (Q-Cut, min-cut on a sampled transition graph) are both min-cut/statistical, known-sensitive to
noisy/spurious edges. 2019-2025 follow-ups (Successor Options / Ramesh 2019, TATC 2022, Proto-Value
Networks 2023) confirm SR/PVF-based representations tolerate function-approximation noise better than
single-eigenvector or exact-graph min-cut variants.

### Thread 2 — Landmark path planning / recursive bisection
**Goldberg-Harrelson 2005** (ALT: A*, Landmarks, Triangle inequality) and **Botea-Muller-Schaeffer 2004**
(HPA*): both are precomputation-heavy and assume **exact** edge costs offline — landmarks/transition
points are geometric/coverage-maximizing, chosen once, not adaptively re-derived from a noisy model.
Neither transfers cleanly to a learned short-horizon-accurate forward model. **Bidirectional /
meet-in-the-middle search** (MM algorithm, Holte et al. 2016): the clean theoretical link is
depth-reduction — bidirectional search is `O(b^(d/2))` vs `O(b^d)`, i.e. halving effective search depth
squares down the branching cost. **MPNet** (Qureshi et al. 2019) is the closest literature analog to
"pick a midpoint from an approximate similarity heuristic, recurse if it fails": a learned (imperfect)
proposal network suggests candidate waypoints, and **recursion is the documented mitigation** whenever a
single hop isn't verifiable. This is the one branch of the literature that explicitly assumes an
approximate/learned distance oracle rather than ground truth.

### Thread 3 — Spectral clustering / metastable Markov states
**Ng-Jordan-Weiss 2001** and **Shi-Malik 2000** (spectral clustering / normalized cuts): standard
Laplacian-eigenvector + k-means/threshold recipe, needs the full affinity matrix, degrades when the
eigengap is small. **Deuflhard-Weber 2005 (PCCA/PCCA+)** operates directly on a row-stochastic
**transition matrix** (exactly the shape of our `R`), gives **fuzzy** (continuous) cluster membership via
a simplex-vertex construction on the leading eigenvectors — states near a simplex edge are natural
boundary/waypoint candidates, which is a strictly better formalism for "waypoint-ness" than a hard
partition. **Mahadevan 2005** (Proto-Value Functions) builds the Laplacian from *sampled* transitions,
closer to our setting than PCCA+'s exact-matrix assumption. **Girvan-Newman 2002** (edge-betweenness
communities) is non-spectral, expensive (`O(m^2 n)`), and has no confidence measure for noisy edges.
Critically, the **Markov State Model (MSM) literature** (Prinz et al. 2011 and the Noe/Pande tradition)
has directly studied this exact failure mode: transition matrices estimated from finite trajectories have
sampling noise that propagates through matrix perturbation theory into **corrupted small eigenvalues** —
the eigengap PCCA+ needs may be noise, not signal, on a learned matrix. **Şimşek-Wolfe-Barto 2005
"L-Cut"** applies Ncut on locally-sampled RL transition graphs specifically to handle this — reports it
works at grid-world scale but is sensitive to how the local subgraph is built.

### Thread 4 — Brain grounding (hippocampal replay / neural subgoal discovery)
**Stachenfeld-Botvinick-Gershman 2017** ("hippocampus as predictive map"): explicitly proposes, as a
**normative computational extension** (not an observed neural computation), that SR eigenvectors
approximate a graph-Laplacian min-cut and that states straddling the cut are natural bottleneck/subgoal
candidates. **Solway et al. 2014** ("Optimal Behavioral Hierarchy"): strong behavioral evidence (4 human
experiments) that people spontaneously discover bottleneck-aligned hierarchies, but the discovery
mechanism itself is not identified — this is an optimality argument, not an algorithm. **Tomov et al.
2020**: uses a Bayesian generative model with explicit bridge-node inference (MCMC), not SR-eigenvector
extraction — a useful correction to the premise; SR is present in their toolkit but is not their
bottleneck-detection engine. **Schapiro et al. 2013** and **Baldassano et al. 2017**: genuine fMRI
evidence that hippocampal/cortical activity reflects temporal-community and event-boundary structure —
correlational, not mechanistic-recording evidence of subgoal computation. **Honest verdict from the
lit-scan (unprompted, independently reached):** "best characterized as a plausible, well-motivated
computational-modeling metaphor with behavioral corroboration, not a mechanistically confirmed brain
algorithm." Treat the brain-grounding lift as real but modest, not a strong prior.

**Citations (verified, new to this drill): 24** across the 4 threads (listed above; full paper list
available in sub-agent transcripts). Combined with the 20 citations already verified in the 2026-06-27/28
hierarchical-planning drills (different mechanism class, same general options/HRL literature), this
drill's total literature base for the "waypoint discovery" question stands at **24 new + partial overlap
with 20 prior** (17-20 of the prior HRL citations are option-framework generalities, not
eigenoption/spectral-specific — treat as loosely inherited context, not directly re-verified here).

---

## MECHANISM EVALUATION — which candidate fits THIS substrate and THIS domain

All three candidates in the prompt reduce, on this substrate, to the **same new primitive**: the
`[V,V]` reach matrix `R[i,j] = reach_value(E[i], E[j], M)`, built once from the already-trained SR
matrix `M`. They differ only in what they DO with `R`:

| Candidate | What it does with R | Feasibility (reuse) | Literature support for noisy/learned input | Domain fit |
|---|---|---|---|---|
| (a) SR eigenoptions / bottleneck | eigendecompose `R` (or its Laplacian), find sign-change / low-magnitude states on top eigenvectors | Moderate — new eigh call, new sign-boundary extraction logic | **Strongest** (Machado 2018 is the only method with a direct approx-vs-exact degradation study) | **Weak** — assumes the graph has genuine community/bottleneck structure |
| (b) Recursive bisection (midpoint) | argmax balance-score `min(R[anchor,c], R[c,goal])` over ALL V candidates, applied sequentially per segment | **High** — reuses `reach_value` wholesale, one new argmax function, zero new training | Moderate (MM depth-reduction theory + MPNet's "recurse on learned midpoint proposal") — a reasonable extrapolation, not a slam-dunk citation | **Strong** — makes no assumption about bottleneck structure; only needs "a state on a plausible path," which exists whether or not community structure does |
| (c) Reachability-clustering | spectral-embed + cluster `R`, restrict candidates to cluster-boundary states, then argmax balance-score within that set | Moderate — reuses the same eigh as (a) plus a clustering step | PCCA+ is mathematically clean for any row-stochastic matrix, but its guarantees lean on near-decomposability | **Weak**, same concern as (a) |

**The domain-fit column is the decisive finding of this drill, and it did not come pre-baked into the
prompt's three candidates — it fell out of cross-referencing the lit-scan's own honest failure-mode
notes against how this substrate's chains are actually generated.** The operator-chain KB
(`make_kb_and_chains`) builds each op's edges by uniform random draw over `V` states at fixed density
(`DENSITY=0.21`, i.e. ~`0.21*V` triples per operator) — this is close to an Erdos-Renyi-style random
directed multigraph, not a spatial/room-like domain. Random graphs at this density typically have **no
strong community/bottleneck structure** (no "doorways") — every state is roughly equally
well-connected. Both threads 1 and 3 of the lit-scan *independently* flagged "degrades in
dense/well-connected graphs lacking true bottlenecks" as a known failure mode for exactly the
eigenvector/min-cut family. This means candidates (a) and (c) may be trying to solve a problem
(finding a *structurally privileged* bottleneck state) **that likely does not exist in this domain**,
while candidate (b) only needs *a* valid interior state on *a* plausible path — a much weaker,
domain-agnostic requirement that should exist regardless of whether community structure does.

**Brain grounding, honestly scoped:** Stachenfeld 2017's SR-eigenvector-min-cut proposal is the most
directly brain-grounded of the three (SR = hippocampal predictive map is the substrate's own `M`), but
per the independent lit-scan verdict this is "a plausible computational metaphor with behavioral
corroboration," not confirmed neural computation — it does not carry decisive extra weight. Hippocampal
bidirectional replay (forward from start, reverse from goal, meeting in the middle — Ambrose-Pfeiffer-
Foster-style reverse-replay findings, not separately re-verified in this drill) is at least as plausible
a grounding for candidate (b) as the eigenvector story is for (a)/(c). **Mechanism-analog is not
task-analog either way** — no candidate gets a free pass from brain citation alone.

**Recommendation: candidate (b) (recursive/sequential bisection via the SR-reach balance score) as the
PRIMARY mechanism for the first cell**, because it is (i) the cheapest to implement (reuses
`reach_value` verbatim, no eigendecomposition required for the primary arm), (ii) has the most direct
literature analog for a *noisy, learned* metric specifically (MPNet), and (iii) makes the weakest,
most domain-appropriate structural assumption. Candidates (a) and (c) are included as **secondary arms
in the same cell** (restricting the SAME balance-score argmax to a spectrally-privileged candidate
subset) because the reach matrix `R` needed for them is already built for (b) at near-zero marginal
cost — running them turns "does bottleneck-restriction help" into a second, cheap, honestly-negative-or-
positive test of the domain-fit hypothesis above, rather than a guess left unstested.

---

## CELL SPEC — `exp_pfc_gate_autonomous_waypoint_discovery_v1` (ready for exp_dev; NOT built yet)

**Inherits verbatim** from `exp_pfc_gate_branching_depth_entropy_grid_v1.py`: `make_bipolar_E`,
`hebbian_W`, `cleanup_batched`, `make_kb_and_chains`, `train_sr_transport`, `reach_value`,
`reach_control_targetcos`, `run_selection_arm` (flat_gonogo), `run_hier_arm` (hier_options /
hier_shuffled with oracle waypoints), `oracle_trajectory_idx`, `build_waypoint_idx`, the full entropy
grid (`n_ops in {2,3,4} x depth in {4,6,8}`, `SEG_LEN=2`), and the discriminator formulas
(`hier_closure`, `hier_lift`, `shuf_gap`, `entropy`). **New code is additive, not a rewrite.**

### New primitive: reach matrix
```
Efwd = normalize_rows(E @ M)                    # [V, n_dim]
R = Efwd @ normalize_rows(E).T                   # [V, V], R[i,j] = reach_value(E[i], E[j], M)
```
Computed once per `(seed, V, n_ops)` group, immediately after `M` is trained — identical cadence to `M`
itself.

### New arms (waypoint SOURCE only differs; execution loop is `run_hier_arm` unchanged)

| Arm | Waypoint source | Purpose |
|---|---|---|
| `wp_bisect_open` | **PRIMARY.** Sequential greedy bisection: for segment boundary `i` (in hop order), `anchor = wp_{i-1}` (or `start` for `i=1`); `wp_i = argmax_{c not in {start,goal,already-chosen}} min(R[anchor,c], R[c,goal])` over ALL V candidates | Candidate (b), open search |
| `wp_bisect_spectral` | Same argmax, candidate set restricted to the bottom-`k` (default 10%) magnitude states on the 2nd/3rd eigenvector of `R` (sign-boundary states) | Candidate (a) |
| `wp_bisect_cluster_exit` | Same argmax, candidate set restricted to states with low cluster-margin in a `k`-means-on-top-eigenvector embedding of `R` ("PCCA+-lite") | Candidate (c) |
| `wp_random_state` | Uniform random codebook state (not even balance-scored) | TRUE floor — is discovery beating pure noise |
| `wp_index_midpoint` | `floor((start_idx+goal_idx)/2)` by raw codebook index | **Structural-artifact guard** — codebook indices carry no order by construction; if this beats `wp_random_state`, something in chain-generation leaks index order and ALL other arms' results must be treated as suspect |
| `hier_shuffled` | *(inherited, unchanged)* wrong-chain's TRUE oracle waypoints | isolates "correct decomposition" from "any real intermediate state" |
| `hier_options` | *(inherited, unchanged, relabeled `hier_oracle` for clarity)* true trajectory waypoints | **ceiling** — ORACLE-ASSISTED hierarchy, re-run in-cell (not cited from the prior run) for a proper paired comparison on identical seeds/regimes |
| `flat_gonogo` | *(inherited, unchanged)* no hierarchy | **floor** — the collapse this whole apparatus tries to fix |

All `wp_*` arms share IDENTICAL `run_hier_arm` execution once waypoints are assigned — only
`build_waypoint_idx`'s job (find the waypoint index per hop) is replaced by a discovery function; no
other code path differs. `oracle_trajectory_idx` is still computed (needed for `hier_oracle` /
`hier_shuffled` and for one diagnostic below) but is NOT visible to any `wp_*` arm's decomposition logic.

### Discriminators (per regime, FOCUS = same rule as ancestor: highest-entropy regime with
`oracle >= 0.90 AND headroom_flat >= 0.10`)

```
autonomous_closure(arm) = (arm_acc - flat_gonogo) / (hier_oracle - flat_gonogo)   # re-derived in-cell
recovery_ratio(arm)     = autonomous_closure(arm) / hier_closure_oracle_this_run  # paired, same seeds
degenerate_rate(arm)    = P(wp == start OR wp == goal) across all waypoint picks
index_artifact_gap      = wp_index_midpoint_acc - wp_random_state_acc
anti_tautology_corr(arm)= corr(balance_score ranking, raw target-cosine-to-goal-only ranking)
exact_match_rate(arm)   = P(discovered wp index == true oracle-trajectory wp index at that boundary)
                          # DIAGNOSTIC ONLY, not gating — a soft/imperfect match can still route correctly
```

### HARD-PASS (locked; `best_wp = max(wp_bisect_open, wp_bisect_spectral, wp_bisect_cluster_exit)` at FOCUS)

- `autonomous_closure(best_wp) >= 0.15` (deliberately below the oracle cell's 0.25 floor — this is a
  strictly harder, unassisted problem)
- `best_wp - flat_gonogo > 0.05` (real lift over no-hierarchy)
- `best_wp - wp_random_state > 0.10` (real lift over a noise waypoint — mechanism-fires gate)
- `recovery_ratio(best_wp) >= 0.20` (recovers at least a fifth of what oracle-assisted hierarchy itself
  achieves, same seeds/regime)
- `index_artifact_gap < 0.05` (no structural leak in chain generation)
- `anti_tautology_corr(best_wp) < 0.85`
- `degenerate_rate(best_wp) < 0.10`
- `sign_p < 0.05`; `cv(best_wp) < 0.10` at FULL only
=> **the substrate can discover a partially-useful decomposition from its own trained SR, without an
oracle trajectory** — a genuine, narrow, positive result on autonomous sub-goal discovery.

### HARD-FAIL (locked)

- `best_wp - flat_gonogo <= 0.05` (no lift over flat at all) OR
- `best_wp - wp_random_state <= 0.05` (indistinguishable from a noise waypoint)
=> **control is solvable GIVEN a correct decomposition (already proven HARD_PASS), but the substrate's
own learned SR does not carry enough information to supply that decomposition itself.** This is a real,
informative, structural bound, not a machinery artifact (guarded by the index-artifact and
anti-tautology checks below) — document as: *autonomous waypoint discovery from a TD-trained SR at this
training budget/domain density is closed; oracle-assist boundary is real.*

### MIDDLE_BAND
Beats flat and random by the required margins but `recovery_ratio < 0.20`, OR any of the honesty guards
(`index_artifact_gap`, `anti_tautology_corr`, `degenerate_rate`) fails while the accuracy margins pass =>
partial/uninterpretable signal — report and do not treat as either a clean win or a clean bound.

### INCONCLUSIVE
No regime satisfies the FOCUS-selection rule (same as ancestor), OR `index_artifact_gap` itself is
large and significant (>0.10, `sign_p<0.05`) => a genuine chain-generation structural leak; the cell's
comparisons are invalid until fixed, reported as a machinery issue, not a science result.

### Reported regardless (same "always report" ethos as ancestor)
Full entropy-grid table for every `wp_*` arm (not just FOCUS); `spearman(recovery_ratio, entropy)` — does
discovery get relatively harder or easier as branching/depth grows (two competing hypotheses: harder,
because M's reach signal is noisier at longer effective horizons; OR easier, because the
oracle-hierarchy's OWN advantage over flat is largest exactly where entropy is highest, so even a
partial recovery ratio yields a large absolute win); and the domain-fit sub-result:
`spectral/cluster arms - open arm` at FOCUS (a negative delta here is itself a clean, informative,
independent confirmation that this substrate's randomly-generated operator graphs lack exploitable
community/bottleneck structure — consistent with random-graph theory, not a bug).

### Compute
`R` build: one `[V,n_dim]x[n_dim,V]` matmul per `(seed,V,n_ops)` group — same cost class as `M` training,
negligible. Bisection argmax: batched row/column gather + elementwise min + argmax over `V` candidates,
per chain per waypoint — fully vectorizable across chains (no python loop over candidates). Spectral
arms: one `torch.linalg.eigh` per `(seed,V,n_ops)` group, `V<=2400` — a few seconds on GPU, once per
group (15 calls total at FULL scale: 5 seeds x 3 V-groups). No new training loop anywhere. Should fit
comfortably inside the ancestor cell's existing smoke/FULL wall-clock budget.

---

## (b) Cheap decisive test

Smoke: reuse the ancestor's 2x2 smoke grid (`n_ops in {2,4} x depth in {4,6}`, `N=2048`, 3 seeds),
add the 5 new `wp_*` arms + re-run `hier_oracle`/`hier_shuffled`/`flat_gonogo` in-cell for pairing. Focus
regime = `op4_V300_d6` (matches ancestor's smoke focus). Wall: expect well under the ancestor's smoke
budget since no new training loop is added, only matmuls + one small eigh per group.

---

## (c) Falsifiable predictions (HARD-PASS / HARD-FAIL — see full bands above; summary table)

| Quantity | Predicted (raw) | P(raw) | After calibration | Reasoning |
|---|---|---|---|---|
| `best_wp` beats `flat_gonogo` and `wp_random_state` by required margins (MIDDLE-clearing bar) | yes | 0.60 | **P_deflated ~0.45** | `reach_rank_test` was already measured at 0.450 (vs 0.300 chance at n_ops=4) in the ancestor cell — M's reach signal is real; picking among `V~1200` candidates should clear a `1/V` chance floor easily even with a noisy signal |
| `best_wp` clears full HARD-PASS (`recovery_ratio >= 0.20`) | yes | 0.40 | **P_deflated ~0.22** (capped at novel-synthesis 0.50 per calibration rule) | Harder bar — requires M's reach signal to be roughly metric-like (monotonic in true graph-distance), not just directionally correct; genuinely uncertain, no substrate precedent |
| `wp_bisect_spectral` or `wp_bisect_cluster_exit` beats `wp_bisect_open` (bottleneck-restriction helps) | no (restriction hurts or is neutral) | 0.25 for "helps" | **P_deflated ~0.15-0.20 for "helps"** | Domain-fit argument above: randomly-generated operator graphs at this density likely lack true community/bottleneck structure, so restricting candidates to spectral-boundary states is expected to be neutral-to-harmful, not helpful — itself a testable, informative sub-hypothesis either way |
| `index_artifact_gap` is null (no leak) | yes | 0.90 | **P_deflated ~0.75** | Chain generation draws indices uniformly at random; no obvious mechanism for index-order leakage, but not yet empirically checked |

All estimates carry the mandatory lit-scan calibration penalty (deflate 0.15-0.25 for uncharted-regime
combination of "SR-derived candidate set x sequential bisection" on THIS substrate; novel-synthesis P
capped at 0.50 per `[[feedback-lit-scan-calibration-penalty]]`).

---

## (d) Cross-thread synthesis

- Directly extends the just-passed `exp_pfc_gate_branching_depth_entropy_grid_v1` HARD_PASS: same
  domain, same trained M/E/W_ops, same entropy grid, same discriminator family (`closure`, `lift`,
  `shuf_gap`) — this cell asks "how much of that closure survives when the waypoint source is the
  substrate's own SR instead of an oracle."
- The BlocksWorld-domain hierarchical-planning line (`research_drill_A_bacon_roy_option_critic...
  2026-06-28`, `research_sutton_precup_options...2026-06-28`) closed on a DIFFERENT mechanism class
  (hand-defined I/pi/beta option channels, closed-form state-delta prediction) in a DIFFERENT domain
  (composite BlocksWorld goals). That closure does not transfer here — this cell's mechanism
  (SR-reach-matrix bisection) was never tested in that line, and per
  `[[feedback-prior-work-informs-not-constrains]]` the prior closure informs caution but does not
  foreclose this genuinely different mechanism/domain combination.
- If HARD_PASS: this is the first piece of evidence that the substrate's TD-trained SR carries enough
  structure to support autonomous decomposition, not just execution-given-decomposition — directly
  relevant to the self-reasoning/self-improvement north star (a system that can propose its own
  sub-problems is doing a small piece of "reasoning about how to solve"), though still scoped narrowly
  (single-domain, single-mechanism, oracle-comparison-gated).
- If HARD_FAIL: an honest, useful bound — "hierarchical control is solved given structure, but
  structure-provision is a separate, harder, currently-closed capability" — this sharpens the M3/M4
  glass-box story (planner needs an external or hand-specified decomposition; auto-decomposition is not
  yet available) rather than being a null result.
- Adjacency-cascade candidate if MIDDLE or HARD_FAIL: try discovery with a BETTER-trained SR (more
  rollout coverage, matching the `cfrpe_trained_v2` FIX-2 boost that rescued the flat-gate cell earlier)
  before concluding the mechanism class (bisection) itself is dead — isolates "SR undertrained" from
  "bisection doesn't work," the same discipline that rescued v1->v2 of the flat gate.

---

## (e) Substrate-product implications

- **Narrow, honest framing only** (USER-LOCKED): this is a sub-goal-discovery PRIMITIVE test, not
  autonomous planning and not self-improvement. A HARD_PASS would mean "given a trained SR over a small
  known state space, the substrate can propose its own waypoints for control tasks in that space" —
  useful for M3/M4 planning-under-uncertainty scenarios where an oracle decomposition won't be
  available (e.g. a Director option-sequence, a KB-traversal plan) but NOT evidence of general
  autonomous problem-structuring.
- If it HARD_PASSes even partially (MIDDLE_BAND), the `recovery_ratio` metric becomes a reusable
  product-facing capability number: "the substrate recovers X% of the benefit of a hand-given plan
  decomposition on its own," a defensible, deflated, honest claim rather than an inflated "substrate
  plans autonomously" claim.
- If it HARD_FAILs, the actionable follow-on is explicit and cheap: re-test with a better-trained SR
  (FIX-2-style rollout/step boost) before closing the capability box, per the 2x-drill-before-closure
  discipline.

---

## Honest prior — does this likely work or hit a bound?

**My overall call: more likely than not to land MIDDLE_BAND, not a clean HARD_PASS or HARD_FAIL.**
The substrate's own `reach_rank_test` diagnostic (already measured at 0.450 vs 0.300 chance in the
passed ancestor cell) shows the trained SR carries real but modest directional information — enough to
almost certainly beat a random/index-midpoint waypoint by a wide margin (mechanism *fires*), but not
obviously enough to reliably land waypoints near the TRUE segment-boundary depth (the harder
`recovery_ratio >= 0.20` bar). The domain-fit finding (operator graphs likely lack true bottleneck
structure) is the most novel/useful output of this drill: it predicts the spectral/cluster-restricted
arms will NOT beat the open bisection arm, which — if it happens — is itself a clean, informative,
independent confirmation, not a failure of the drill. P_deflated for full HARD-PASS: **~0.22** (capped
per calibration rule). P_deflated for "beats flat and random, i.e. mechanism fires at all": **~0.45**.

---

## (f) Citations (verified count: 24 new, this drill)

**Thread 1 (SR eigenoptions/bottleneck):** Machado, Bellemare, Bowling 2017 ICML; Machado et al. 2018
ICLR (Deep Successor Representation eigenoptions); Şimşek & Barto 2004/2005/2009; McGovern & Barto 2001
ICML; Menache, Mannor, Shimkin 2002 ECML (Q-Cut); Ramesh et al. 2019 (Successor Options); Machado et al.
2021 (arXiv:2110.05740, online/TD-learned SR eigenoptions); TATC 2022 (arXiv:2203.11369); Proto-Value
Networks 2023; Kotamreddy & Machado 2025.

**Thread 2 (landmark planning/bisection):** Goldberg & Harrelson 2005 SODA (ALT); Botea, Muller,
Schaeffer 2004 (HPA*); Holte et al. 2016 AAAI (MM bidirectional search); Sacerdoti 1974 (ABSTRIPS);
Qureshi et al. 2019 (MPNet, arXiv:1907.06013); RMPD (arXiv:1709.00488).

**Thread 3 (spectral/metastable clustering):** Ng, Jordan, Weiss 2001 NIPS; Shi & Malik 2000 PAMI;
Deuflhard & Weber 2005 (PCCA/PCCA+); Roblitz & Weber 2013 (fuzzy spectral clustering by PCCA+); Mahadevan
2005/2007 JMLR (Proto-Value Functions); Girvan & Newman 2002 PNAS; Prinz et al. 2011 (Markov State Model
error analysis); Şimşek, Wolfe & Barto 2005 (L-Cut).

**Thread 4 (brain grounding):** Stachenfeld, Botvinick, Gershman 2017 Nat Neurosci; Solway et al. 2014
PLoS Comp Biol; Tomov et al. 2020 PLoS Comp Biol; Schapiro et al. 2013 Nat Neurosci; Baldassano et al.
2017 Neuron; Botvinick & Weinstein 2014 Phil Trans R Soc B.

Total new citations this drill: **24**. All verified via WebSearch by 4 independent Sonnet sub-agents;
mechanism details flagged where sub-agents noted extrapolation vs direct citation (see per-thread notes
above — this has been preserved rather than smoothed over).

---

## Dispatch readiness

Cell `exp_pfc_gate_autonomous_waypoint_discovery_v1` spec is complete and additive to the passed
ancestor. No hand-off routing file written (ferry mechanism deprecated per USER-locked discipline) —
this note is the complete, actionable deliverable. Director should read this note directly and dispatch
`hdi_exp_dev` with a pointer to this file + the ancestor cell path for verbatim-reused primitives.
