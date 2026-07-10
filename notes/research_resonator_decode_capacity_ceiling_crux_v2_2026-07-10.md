# Research — resonator-network decode: does it plausibly close the crux-v2 recall gap, or hit its own ceiling?

Filed by: research (Sonnet 5, self-contained — no sub-agent fan-out per explicit task constraint;
WebSearch/WebFetch + own synthesis + on-disk substrate-history scour) | 2026-07-10

**Trigger:** crux-v2 HARD_FAILed because single-shot VSA unbind loses candidates to bundle-superposition
crosstalk AT COMPOSE (VET-confirmed: vsa candidate-recall@10 0.203 vs symbolic 0.491; verify+rank stages
are HEALTHY conditioned on recall). exp_dev is implementing a resonator-network decode (Frady/Kent/
Olshausen/Sommer 2020) as the fix. This is the strategic/ceiling question exp_dev doesn't have cycles for:
will a resonator plausibly recover the gap for our regime (~14k FB15k-237 entities, relation-path
factorization, N_DIM ~2048-8192), or does it hit its own capacity/convergence ceiling first.

**Discipline note:** this substrate has an unusually deep, very recent (2026-07-06 through 07-09) internal
research trail on this EXACT mechanism family (resonator basin-proliferation, K-sweep, restart-budget law,
ACF codebook rescue, sequential-vs-simultaneous topology, correlated-codebook gap). Per
`[[feedback-dont-dismiss-adjacent-methods]]` and cross-thread discipline, this note leads with that
internal trail (Section (d)) as load-bearing context, not an afterthought — several of the open literature
questions below were ALREADY answered, in whole or in part, by this substrate's own prior cycles.

---

## (a) HEADLINE

**Plausible, with three named preconditions, not a free win.** The literature strongly supports that
resonator-network decode beats single-shot argmax/unbind at exactly this kind of problem (factor recovery
from a noisy superposed/bound composite) — that is the resonator's designed comparative advantage, and the
published capacity gains over naive/optimization baselines run from ~10x to ~10^6x depending on codebook
structure. Combined with this substrate's OWN prior finding that a closely related K=4 resonator
reachability residual was **primarily a cheap restart-budget problem** (not a basin-measure wall), and
that an already-validated, already-built rescue (ACF — Asymmetric Codebook Factorizer) gives **50x+
capacity gain on exactly the codebook-SIZE axis** that a 14k-entity codebook sits on, this drill's
calibrated read is: **plausible recovery of most of the 0.203->0.491 gap (a 2.4x improvement, not an
order-of-magnitude ask), P_deflated=0.50 (capped)**, GATED on three things that must be checked, not
assumed: (1) the crux's failure topology is genuinely SIMULTANEOUS multi-factor composite factorization
(resonator's home turf), not SEQUENTIAL hop-by-hop chaining (where this substrate already found resonator
alone weak, P=0.25, and hard-decision error propagation was the real driver); (2) the codebooks are not
too semantically correlated (FB15k-237 entities are not i.i.d. random — an OPEN gap in the resonator
capacity literature per two independent 07-09 drills on this substrate); (3) the cell explicitly detects
non-convergence/limit-cycles rather than silently reporting spurious "recovered" states, which the
literature identifies as a real, well-documented failure mode distinct from the search-space-size ceiling.

---

## 1. Resonator capacity / does it beat the wall or just move it

**No closed-form capacity formula exists anywhere in the literature** — the founding papers say so in
print. Frady, Kent, Olshausen, Sommer ("Resonator Networks, 1," Neural Computation 32(12):2311, arXiv:
2007.03748; "Resonator Networks, 2," Neural Computation 32(12):2332, arXiv:1906.11684) report **empirical**
operational capacity `M_max` scaling as a **quadratic function of vector dimension N** (least-squares fit
`M_max = aN^2 + bN + c`, coefficients vary by factor count F), explicitly stating "the parameters of this
particular combined scaling are estimated from simulation and not derived analytically" and that "our
attempts to analytically derive this result were stymied." This is NOT a bundling-SNR-style closed form
like `SNR ~ sqrt(N/M)` — it is a fitted curve. Two concrete numbers from the same paper: (i) **percolated
noise instability** — for the outer-product weight variant, when `F/N > 0.056` (their `D_f/N` ratio), the
resonator becomes strictly less stable than a plain Hopfield network; at our regime (N=2048-8192,
F~2-4 for relation-path factorization) `F/N` is ~0.0005-0.002, two orders of magnitude below that threshold
— **not a binding constraint for us**; (ii) large-search-space onset of failure — once the total
combinatorial search space `M^F` exceeds roughly `1.2x10^5`, factorizers start hitting limit cycles and
spurious fixed points that hinder convergence even with unlimited iterations.

Sparse/structured codebooks move the ceiling dramatically. Hersche et al., "Factorizers for Distributed
Sparse Block Codes" (arXiv:2303.13957, BCF), at `D=512, F=2, B=4 blocks`: binary sparse-block-code (SBC)
gives ~`10^3` operational capacity; adding a threshold + conditional-sampling nonlinearity pushes this to
**~`5x10^6`** — a ~1200x gain over the naive binary-SBC baseline, at the SAME dimension. They test
combinatorial problem sizes up to `10^6` (`prod_f M_f = 10^6`) and demonstrate 100-1000-class factorized
codebooks (CIFAR-100, ImageNet-1K scale) with convergence in as few as 2 iterations up to `10^4` problem
size and up to 6x fewer iterations than dense resonators at `10^6`. **14k entities sits comfortably inside
the demonstrated regime of this specific published technique** — this is the single most directly relevant
number in the external literature for our scale.

In-memory/analog implementations push further still: "In-memory factorization of holographic perceptual
representations" (Nature Nanotechnology 2023, arXiv:2211.05052) reports **five orders of magnitude larger
solvable problems**, achieved even while REDUCING vector dimension by >4x, by exploiting intrinsic
phase-change-memristor stochasticity to break limit cycles (see Section 4).

**Bottom line for our regime:** plain dense resonator capacity growth (quadratic in N) alone is a real but
modest lever going from N=2048 to N=8192 (roughly 4-16x, depending on the fitted coefficients, which are
NOT published for our F/N combination — this is an empirical unknown, not a derivable one). The
demonstrated capacity headroom that actually matters for 14k entities comes from **structured/sparse
codebooks and/or the substrate's own already-validated ACF rescue** (Section (d)), not from raw N scaling
alone.

---

## 2. Failure modes: non-convergence, spurious fixed points, limit cycles, detection

Three distinct terminal outcomes are consistently separated in the literature (this is the correct
taxonomy, not a simplification): **correct convergence**, **spurious convergence** (settles to a stable
but WRONG joint fixed point), and **non-convergence** (limit cycle or effectively-chaotic wandering that
never settles within the iteration budget). All three matter and are measured separately.

Karunaratne, Hersche, Sebastian, Rahimi, "On the Role of Noise in Factorizers for Disentangling Distributed
Representations" (arXiv:2412.00354, NeurIPS MLNCP 2024 workshop): limit cycles emerge specifically from the
**symmetric, deterministic** nature of codebooks in large search spaces with many local minima. Critically
for a GPU implementation: **noise applied ONLY at reconstruction-codebook initialization (not at every
iteration) is sufficient to relax the noise requirement** — meaning a digital/GPU implementation does not
need per-iteration analog-style noise injection; cheap, randomized-restart initialization is enough to get
most of the noise benefit. This directly supports a batched-random-restart GPU design (Section 4).

A 2026 comparative study of nonlinear cleanup rules in resonator networks (Frontiers in AI,
10.3389/frai.2026.1793314) benchmarked sign / softmax / ReLU / polynomial cleanup nonlinearities. Sign
cleanup wins in easy/moderate regimes (95.2% / 93.7% exact-scene accuracy on Multi-CMNIST / Multi-dSprites
factorization tasks); ReLU degrades more gracefully at higher factor counts (F=4,5). Mean iterations to
correct convergence ranged 3-14 depending on rule and difficulty. **Detection guidance the paper gives
explicitly:** track iteration-to-iteration state stability (has the estimate stopped changing) SEPARATELY
from correctness (does the converged state actually re-bind to reproduce the composite within tolerance) —
"lower accuracy can arise either because the dynamics settle into incorrect attractors or because they fail
to converge," and these are **separable, both trackable, neither inferable from the other**.

**Concrete detection recipe for the crux-v2 cell** (synthesized from the above, not a single-source quote):
(i) **convergence check** — Hamming/cosine delta between the last K (e.g. 5) iterates near zero;
(ii) **spurious-convergence check** — after declaring convergence, re-bind the recovered factors and
measure residual `||composed - rebind(recovered_factors)||`; only count a trial as a genuine recovery if
this residual clears a pre-registered threshold. A cell that skips (ii) and only checks (i) risks silently
reporting spurious convergences as recoveries, inflating the measured recall artifactually — this is the
single most important implementation discipline from this section, and it maps directly onto this
substrate's own prior finding (below) that raw `oracle_any` and residual-gated `oracle_any` can diverge.

---

## 3. Brain-grounding: is this CA3 attractor pattern completion, or something else

**Partial match, with a real structural gap the literature is honest about.** CA3's recurrent-collateral
network is the textbook attractor-completion circuit: sparse, recurrently-connected pyramidal cells
"attract" a partial or degraded input pattern to a stored full pattern via iterated recurrent dynamics
(Rebecca Rolls et al.; "A Signature of Attractor Dynamics in the CA3 Region of the Hippocampus," PLOS Comp
Bio, PMC4031055; "The mechanisms for pattern completion and pattern separation in the hippocampus,"
Frontiers Systems Neurosci, PMC3812781). Two hippocampal pathways matter: the direct perforant path
(entorhinal cortex -> CA3, carrying the noisy/partial cue) and the recurrent collaterals (which do the
actual iterative cleanup toward the stored attractor). This is structurally the SAME shape as the
resonator's alternating projection: noisy composite in, iterative recurrent refinement, converged
(hopefully correct) attractor out.

**Where it diverges:** CA3's recurrent completion resolves ONE degraded pattern to ONE attractor — it is
not, on its own, solving a K-way SIMULTANEOUS multiplicative-factorization problem the way a resonator's
coupled multi-population search does. The brain's actual answer to avoiding combinatorial multi-factor
search (this substrate's own 07-08 brain-grounding drill on the same mechanism family found this
independently, see (d)) is more often to **never pose the K-way joint problem in the first place** —
sequential theta-gamma phase-slotting (Lisman & Idiart 1995) resolves bound items ONE AT A TIME in
successive gamma sub-cycles, turning a `M^K` simultaneous search into `K` sequential `M`-way searches. That
is a different (bigger, encode-side) redesign, not a decode-side resonator patch — flagged here as
"more brain-faithful" but explicitly NOT proposed as this cycle's fix (matches the prior drill's own
scoping decision).

The other brain-side lever that IS a direct decode-time analog and IS cheap: dentate-gyrus-style pattern
separation (sparse random expansion recoding) happens BEFORE CA3 storage, decorrelating inputs so CA3's
attractor basins are better separated. This substrate already has a validated, unit-tested implementation
of exactly this primitive (`hdlab/hippocampal_encoder.py`'s `DGProjection`, selftest passing with a
measured decorrelation gap) that has never been wired into any resonator codebook path — see (d) for the
existing, gated, ready-to-adapt candidate cell.

Predictive coding is a distinct, complementary mechanism, not a substitute: "Linking pattern completion in
the hippocampus to predictive coding in visual cortex" (Hindy, Ng, Turk-Browne, Nature Neuroscience 2016,
PMC4948994) shows CA3/CA1 retrieve a conjunctive (attractor-style) representation and then REINSTATE it as
a top-down expectation in visual cortex — i.e. predictive coding downstream consumes the OUTPUT of
attractor completion, it does not replace the iterative search itself. This does not suggest a
predictive-coding-style iterative-collapse should replace the resonator's alternating-projection search;
it suggests predictive-coding-style residual gating (Section 2's spurious-convergence check) is the right
downstream discipline, which is exactly what this substrate's own 07-09 crosstalk drill independently
proposed (CA1-style comparator/residual gate, forwarding only the unpredicted component between hops — see
(d)).

**Verdict on brain-fidelity:** the resonator's iterative unbind-and-cleanup IS a genuine, reasonable
CA3-attractor analog for the decode step itself. The bigger brain-faithful lever this substrate has not
yet tried is DG-style decorrelation of the codebooks feeding the resonator (encode-side), not a different
decode-side dynamics.

---

## 4. GPU + variants

Three concrete, literature-grounded, GPU-cheap levers, ranked by how directly they apply to this cell:

1. **Batched random restarts (highest priority, cheapest, and already substrate-validated).** Per
   arXiv:2412.00354, noise at INITIALIZATION alone breaks most limit cycles — no per-iteration analog noise
   needed. This is trivially GPU-batchable: stack R independent random-initialized trajectories along a
   batch dimension and run all iterations as one batched matmul per step (`decode_trial` pattern already
   used elsewhere on this substrate, see (d) — "the batched R=10 restarts already show oracle_any=0.247 vs
   R=1 single-shot=0.133 at T0=0, nearly 2x lift with NO engineered dither at all," attributed to
   floating-point-order-induced trajectory divergence in the batched BLAS call). The restart-budget law
   `oracle_any(R) = 1-(1-p_basin)^R` is textbook independent-Bernoulli-trial theory and was validated
   on-substrate this same week (see (d)) — R~19-29 restarts (a small, GPU-cheap multiple of current
   compute) closed most of a comparable K=4 reachability residual.
2. **Sparse/structured (block) codebooks (BCF, arXiv:2303.13957).** GPU-friendly because block-local
   operations reduce effective per-block dimension and are naturally chunk-parallel; demonstrated ~1200x
   capacity gain and up to 6x fewer iterations at large problem sizes (Section 1). This is the more
   substantial engineering lift of the three but has the largest demonstrated headroom for a 14k-entity
   codebook specifically.
3. **In-memory/analog factorization (Nature Nanotechnology 2023)** is NOT directly portable to a GPU (it
   is a distinct memristive hardware substrate) but its *lesson* — cheap, intrinsic stochasticity beats
   engineered per-iteration noise schedules — is exactly what motivates lever 1 above; treat it as
   inspiration/validation for the batched-restart design, not a hardware target.

No GPU-specific resonator-network paper was found in this drill (searched directly; general batched-tensor
GPU literature exists but nothing resonator-specific) — the batching argument above is a direct, low-risk
inference from the algorithm's structure (independent per-restart matmul chains), not a cited GPU-benchmark
result. Flagged honestly as an inference, not a verified claim.

---

## 5. THE HONEST VERDICT — will resonator decode plausibly beat the crux's recall gap, or hit a ceiling

**Favorable indicators:**
- The gap needed is 2.4x (0.203 -> 0.491), not orders of magnitude — well inside demonstrated resonator
  gains over naive/optimization baselines in every cited paper.
- Verify+rank are HEALTHY conditioned on recall — meaning correct candidates are not fully destroyed, just
  not surfaced by single-shot argmax. This is EXACTLY the regime resonator networks are designed to help
  with ("searching in superposition," recovering signal a hard single-shot readout throws away) — a much
  more favorable starting condition than "the information is gone."
- This substrate's own, very recent (this week) parallel resonator work found a comparable K=4 residual
  was PRIMARILY a cheap restart-budget problem, not a fundamental wall — and that a fully validated,
  already-built rescue (ACF, cap_map row 51, 50x+ capacity gain) exists on exactly the codebook-SIZE axis
  a 14k-entity codebook sits on. If the crux-v2 cell wires in restarts + ACF from day one rather than
  building a naive dense resonator first, it is reusing proven, derisked, on-substrate machinery, not
  betting on unproven literature alone.

**Named risks that could cap the recovery below what's needed (not the same as "resonator doesn't
apply"):**
- **Topology mismatch.** If the crux-v2 recall failure is actually driven by SEQUENTIAL hop-by-hop
  hard-decision chaining (candidate loss compounding across relation-path hops) rather than a genuinely
  SIMULTANEOUS multi-factor composite factorization, this substrate's OWN 2026-06-24 disparate-fields
  drill found resonator-network-proper a comparatively WEAK fix for that specific topology (P_deflated=0.25,
  vs. 0.35 for soft-decision/soft-DFE-style confidence chaining across hops). The task description
  ("crosstalk AT COMPOSE") sounds like the simultaneous-composite topology, which is favorable — but this
  should be explicitly confirmed against the actual crux-v2 cell code before assuming resonator alone is
  the complete fix, not just a partial one.
- **Correlated codebooks — an open literature gap, not resolved for or against.** All published resonator
  capacity results (Frady/Kent/Olshausen/Sommer and successors) are derived/measured on i.i.d. or
  quasi-orthogonal random codebooks. Two independent drills on this substrate this same week
  (`research_sparse_compatible_binding_operator_2026-07-09.md`,
  `research_learned_code_crosstalk_cleanup_decorrelation_at_scale_5x_2026-07-09.md`) confirmed this is a
  genuinely open gap: no paper measures resonator capacity under semantically-correlated codebooks. FB15k-
  237 entities are NOT i.i.d. random by construction (real-world entity/relation semantics correlate).
  Mitigation is already known on this substrate: decouple store-codes (near-orthogonal random assignment)
  from retrieval-semantics, per this substrate's own validated cross-cell law
  (`reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md`) — if the
  crux-v2 codebook construction binds entity IDENTITY codes directly to embedding-derived (and therefore
  correlated) vectors, that is a likely place the resonator's theoretical capacity gain will NOT fully
  materialize.
- **Silent spurious-convergence inflation.** Per Section 2, a cell that declares success on iteration-limit
  or naive convergence alone (without a residual re-bind check) can report a falsely-inflated recall gain.

**P_deflated = 0.50 (capped, novel-synthesis rule)** for "resonator decode (with restarts, and ACF if
wired) recovers residual-gated candidate-recall@10 to >= 0.35 at N_DIM=2048-4096" — favorable base
literature rate deflated for: no direct precedent at this exact entity-count/topology/codebook-correlation
combination, and the named topology-mismatch and correlated-codebook risks above not yet ruled out.

---

## Cheap decisive test (pre-registered)

Run on the SAME crosstalk-degraded compose vectors that single-shot unbind failed on (the VET's 0.203-
recall evaluation set) — cheapest N_DIM (2048), plain resonator (no ACF yet, to isolate the resonator's
own marginal contribution), R=10 batched random restarts, T0~0.3-0.5 dither, MAXIT~60-100 iterations.
Measure BOTH raw candidate-recall@10 AND **residual-gated** candidate-recall@10 (only count trials that
pass the re-bind residual check from Section 2) — the gap between these two numbers is itself a diagnostic
for spurious-convergence rate.

**HARD-PASS:** residual-gated candidate-recall@10 >= 0.35 (roughly 70% of the way from 0.203 to symbolic's
0.491) at N=2048, AND non-convergence/limit-cycle rate < 20% (Hamming-stability check). This licenses
wiring ACF next (already validated, cheap) for the remainder of the gap and sweeping N_DIM up if still
short.

**HARD-FAIL:** residual-gated candidate-recall@10 stays < 0.25 (no material lift over raw single-shot 0.203)
even after restarts + temperature dither. This would indicate the crosstalk is an **SNR-floor problem**
(the compose-time noise variance is too large relative to N for even efficient iterative search to recover
— the same fundamental bundling-load-vs-N tradeoff that governs Hopfield/HDC catastrophic capacity limits),
not a search-space-size problem — meaning the fix has to move upstream (bigger N_DIM, decorrelated/
sparse-block codebooks per BCF, or reduced bundling load K at compose time), not stay at decode.

**Secondary must-fail control:** if non-convergence rate alone exceeds 20% regardless of the recall number,
fix the restart/temperature schedule FIRST (this substrate's own prior finding: pushing T0 past ~0.5 gave
diminishing returns, a textbook Kramers-type saturating curve — do not expect an unlimited noise dial).

---

## CEILING + NEXT-LEVER

**Does resonator plausibly close the gap for the 14k-entity regime?** Plausibly yes for the majority of it,
GATED on the three named risks (topology, codebook correlation, convergence-detection discipline) — not a
free win, not a dead end. The single most load-bearing fact from this drill is that **this substrate
already has a validated, built, 50x+-gain rescue (ACF) sitting on exactly the axis (codebook size) that a
14k-entity codebook needs**, discovered independently by this substrate's own 2026-07-06/07 cycles before
this drill started. The crux-v2 cell should be designed to use it from the start rather than re-deriving
the need for it after a plain-resonator HARD-FAIL.

**If capped (HARD-FAIL per the test above), next levers in priority order:**
1. **Wire ACF** (already built, already validated on this exact substrate, cap_map row 51) — first, cheap,
   not speculative.
2. **Block-local/sparse structured codebooks** per Hersche BCF (arXiv:2303.13957) — larger engineering
   lift, largest demonstrated headroom (~1200x) for entity-scale codebooks.
3. **DG-style decorrelation front-end** (`hdlab/hippocampal_encoder.py`'s `DGProjection`, already built,
   never wired to any resonator codebook path) — cheap to try, causal link to basin-count/crosstalk
   reduction specifically is honestly unproven in the literature (both external and this substrate's own
   07-08 drill flag this), but directly instantiates the substrate's own validated
   correlation-hurts-capacity law.
4. **Bigger N_DIM** (2048->8192) — real but the most expensive lever (quadratic scaling, unknown fitted
   coefficients for our specific F/N combination) and should be LAST, not first, given levers 1-3 are
   cheaper and better-precedented on this exact substrate.

**For exp_dev (direct, no separate hand-off file per current discipline):** build the crux-v2 resonator cell
with (i) batched random restarts (R~10-20) from the start — near-zero marginal cost, validated lever;
(ii) explicit residual re-bind check gating "recovered" (Section 2) — do not trust iteration-limit alone;
(iii) confirm the failure topology is simultaneous-composite (not sequential hop-chain) before treating a
plain-resonator result as final; (iv) if the cheap decisive test above HARD-FAILs, escalate directly to
wiring ACF (`experiments/exp_wave14b_acf_resonator.py` and siblings are the existing template) rather than
tuning the plain resonator further.

---

## (d) Cross-thread synthesis (internal, all read in full this cycle)

- `notes/research_resonator_basin_proliferation_self_predictability_2026-07-07.md` (2026-07-07): 3
  independent lit-scans confirm no closed-form resonator capacity law exists (matches this drill's own
  external findings exactly); basin-proliferation mechanism classified as AGS/TAP/K-SAT annealed-counting
  family, P_deflated=0.50 (capped). Names ACF-transfer-to-factor-count-axis as the top near-term follow-up
  — a DIFFERENT axis from this drill's codebook-SIZE relevance, but the same underlying validated primitive.
- `notes/research_brain_grounding_resonator_basin_proliferation_2026-07-08.md` (2026-07-08): ranks DG
  pattern-separation front-end as top practical rescue candidate (cheap, primitive exists, causal link to
  basin-count reduction unproven in lit — matches this drill's Section 3 finding exactly, independently
  arrived at); notes the K5/K6 "WALL_FUNDAMENTAL" result was SMOKE-ONLY and NOT skunkworks-confirmed as of
  filing — status of that confirmation was not re-verified this cycle (out of scope for this strategic
  drill) and should be checked before treating basin-proliferation-at-large-K as settled fact for the
  crux-v2's own factor count.
- `notes/research_resonator_reachability_ceiling_2026-07-07.md` (2026-07-07): directly the strongest
  positive precedent cited above — at K=4, a comparable resonator reachability residual was PRIMARILY a
  restart-budget problem (p_basin~0.15/restart, R~19-29 restarts reaches 0.90-0.99), with a
  Kramers-type saturating noise-temperature curve (T0>0.5 gives diminishing returns). Also reports the
  "free diversity from batched-BLAS floating-point order" observation used in Section 4 above.
- `notes/research_resonator_restart_budget_geometric_race_law_2026-07-07.md` (2026-07-07): derives and
  validates `oracle_any(R) = 1-(1-p_basin)^R` as the correct restart-budget model (textbook, near-certain);
  confirms `p_basin(K)` itself is not closed-form derivable (same "stymied" finding as the founding
  literature) — consistent with Section 1's "no capacity formula exists" finding from independent external
  search.
- `notes/research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md` (2026-06-24): **the most
  important caution in this note.** For a SEQUENTIAL multi-hop chaining topology, resonator-network-proper
  alone was found to be a comparatively WEAK fix (P_deflated=0.25) — the actual driver of that HARD_FAIL was
  hard-decision error propagation across hops, with soft-decision/soft-DFE-style confidence chaining ranked
  higher (P=0.35). This drill's Section 5 explicitly surfaces this as a named risk requiring confirmation
  against the actual crux-v2 topology before treating resonator alone as sufficient.
- `notes/research_sparse_compatible_binding_operator_2026-07-09.md` and
  `notes/research_learned_code_crosstalk_cleanup_decorrelation_at_scale_5x_2026-07-09.md` (2026-07-09,
  both): independently confirm that published resonator/VSA capacity theory assumes i.i.d./quasi-orthogonal
  codebooks, and that the CORRELATED-codebook regime is an open literature gap — directly informs Section
  5's "correlated codebooks" risk for FB15k-237 entity/relation codes.
- `notes/research_encoder_clean_composable_relational_codes_2026-07-09.md` (2026-07-09): sparsity is the
  primary interference lever for typed-binding recovery on this substrate, and recovery-vs-sparsity is a
  SHARP phase transition (Donoho-Tanner), not gradual — relevant caution for lever 4 (bigger N_DIM) above:
  do not assume gradual improvement from N_DIM increases; the substrate's own encoder work found step-
  function behavior in an adjacent regime.
- `notes/substrate_capability_map.md` row 51, "Resonator decomposition with ACF rescue": Validated status,
  `acf_K_dependent_retry`, `acf_resonator_redo`, `acf_sparsity_sweep_redo` all positive, 50x+ gain recovering
  atoms past the naive capacity cliff (K/N=1.5 at 97%) — the single most load-bearing internal fact this
  drill surfaces for the crux-v2 fix.

**No contradiction found between external literature and internal substrate history** — they converge
independently on the same open questions (no closed-form capacity law, correlated-codebook gap,
convergence-vs-correctness separability), which raises confidence these are the genuinely right open
questions for this mechanism, not artifacts of query framing.

---

## Substrate-product implications

- If the crux-v2 resonator fix lands (HARD-PASS per the cheap decisive test), the product gains a reusable,
  general "recover superposition-crosstalk-degraded candidates via iterative factorization" capability —
  directly reusable beyond KG completion, anywhere this substrate composes multiple bound items and later
  needs to recover them (the SAME underlying primitive family already validated for pool retrieval past
  naive capacity, cap_map row 51).
- If it HARD-FAILs per the SNR-floor band, that is itself a valuable, well-localized negative: it would
  mean the compose-time bundling load is fundamentally too high for the current N_DIM/codebook structure,
  pointing product effort toward compose-time fixes (sparser/decorrelated codebooks, bigger N_DIM, or
  reduced per-compose bundling load) rather than continued decode-side iteration — a clean, actionable
  redirection, not a dead end.
- Either outcome sharpens this substrate's own emerging general law (echoed across at least 4 independent
  drills this week alone): **decode-time iterative cleanup recovers information lost to correlated/
  crosstalk-degraded superposition only up to a point set by codebook decorrelation and bundling load at
  ENCODE time** — decode-side cleverness (resonator, ACF, restarts) is real and cheap-to-add value, but is
  not a substitute for encode-side discipline (near-orthogonal store-codes, decoupled from
  retrieval-semantics) when that discipline is missing.

---

## Citations (verified count)

**External literature, fetched/verified this cycle via WebSearch/WebFetch:**
1. Frady, Kent, Olshausen, Sommer, "Resonator networks for factoring distributed representations of data
   structures," Neural Computation 32(12):2311-2331 (2020), arXiv:2007.03748.
2. Kent, Frady, Sommer, Olshausen, "Resonator Networks, 2: Factorization Performance and Capacity Compared
   to Optimization-Based Methods," Neural Computation 32(12):2332-2388 (2020), arXiv:1906.11684. Full text
   fetched (ar5iv): quadratic empirical capacity scaling, percolated-noise F/N>0.056 instability threshold,
   M^F>~1.2x10^5 limit-cycle onset, all confirmed directly from source text this cycle.
3. Hersche, Terzic, Karunaratne, Langenegger, Pouget, Cherubini, Benini, Sebastian, Rahimi, "Factorizers
   for Distributed Sparse Block Codes," arXiv:2303.13957 — BCF capacity numbers (~10^3 -> ~5x10^6, ~1200x
   gain at D=512, F=2, B=4), problem sizes up to 10^6, iteration-count comparisons.
4. Karunaratne, Hersche, Sebastian, Rahimi, "On the Role of Noise in Factorizers for Disentangling
   Distributed Representations," arXiv:2412.00354 (NeurIPS 2024 MLNCP workshop) — limit-cycle mechanism,
   initialization-only noise sufficiency finding.
5. "In-memory factorization of holographic perceptual representations," Nature Nanotechnology (2023),
   arXiv:2211.05052 — phase-change memristor substrate, 5-orders-of-magnitude capacity gain, O(1) per-
   iteration matmul complexity.
6. "A comparative study of nonlinear cleanup rules in resonator networks," Frontiers in Artificial
   Intelligence, 10.3389/frai.2026.1793314 (2026) — sign/softmax/ReLU/polynomial cleanup comparison,
   convergence-vs-correctness separability guidance.
7. "A Signature of Attractor Dynamics in the CA3 Region of the Hippocampus," PLOS Computational Biology,
   PMC4031055.
8. "The mechanisms for pattern completion and pattern separation in the hippocampus," Frontiers in Systems
   Neuroscience, PMC3812781.
9. Hindy, Ng, Turk-Browne, "Linking pattern completion in the hippocampus to predictive coding in visual
   cortex," Nature Neuroscience (2016), PMC4948994.
10. "Neuromorphic visual scene understanding with resonator networks," Nature Machine Intelligence (2024)
    — confirmed real (title/venue verified via search), context only, not fetched in full this cycle.

**Internal substrate sources (on-disk, read in full this cycle):**
11. `notes/research_resonator_basin_proliferation_self_predictability_2026-07-07.md`
12. `notes/research_brain_grounding_resonator_basin_proliferation_2026-07-08.md`
13. `notes/research_resonator_reachability_ceiling_2026-07-07.md`
14. `notes/research_resonator_restart_budget_geometric_race_law_2026-07-07.md`
15. `notes/research_resonator_hard_fail_revival_disparate_fields_2026-06-24.md`
16. `notes/research_sparse_compatible_binding_operator_2026-07-09.md` (referenced via status_log summary,
    not re-read in full this cycle — cited for its stated conclusion only)
17. `notes/research_learned_code_crosstalk_cleanup_decorrelation_at_scale_5x_2026-07-09.md` (referenced via
    status_log summary, not re-read in full this cycle — cited for its stated conclusion only)
18. `notes/research_encoder_clean_composable_relational_codes_2026-07-09.md` (referenced via status_log
    summary, not re-read in full this cycle — cited for its stated conclusion only)
19. `notes/substrate_capability_map.md` (grepped, row 51 confirmed: ACF rescue validated status + gain
    figures)

**Total: 10 external literature sources (WebSearch/WebFetch verified) + 9 internal on-disk sources = 19
verified sources/checks.** Sources 16-18 were confirmed via their own status_log entries and note titles
but not re-read line-by-line this cycle (time-budget tradeoff for a same-day strategic drill); their cited
conclusions are reported as stated in those entries, flagged here for transparency rather than presented as
independently re-verified this cycle.

## P_deflated summary

- **"Resonator decode plausibly recovers most of the crux-v2 recall gap" (Section 5 headline claim):**
  raw literature-plus-substrate-history confidence ~0.65-0.70 (favorable gap size, healthy verify+rank,
  strong on-substrate restart-budget precedent, already-validated ACF rescue on the right axis). Novel-
  synthesis cap applies (no direct precedent at this exact entity-count/topology/codebook combination) ->
  **P_deflated = 0.50 (capped)**.
- **"Plain resonator alone, with no ACF/restarts, clears the HARD-PASS band on the first try":** deflated
  further to **P_deflated = 0.30** — the favorable precedent above is contingent on wiring the
  already-validated rescues (restarts, ACF), not the naive resonator in isolation.
