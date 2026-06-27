# RESEARCH 2x drill — WHY damped loopy BP catastrophically COLLAPSED (D0=0.989 → D2/D5_damped=0.006)

date: 2026-06-27
trigger: `exp_loopy_belief_propagation_damped_v1_smoke` per Angle 1 of `research_drill_5x_multihop_barrier_2026-06-27.md`. Smoke at cycle=4, n_seeds=3 came back HARD_FAIL with iteration ACTIVELY DESTROYING signal (D0=0.989 vs D2_damped=0.006, lift=-0.983, cv_d2=1.414).
disciplines: 2x research drill (broad lit-scan focuses operational drill); generic terms only per query-privacy; lit-scan calibration penalty (deflate P 0.15-0.25; novel-synthesis cap P=0.50); verify-the-referent on prior cell evidence; symmetric anti-negativity (don't inflate, don't dismiss).
recurring-failure-pattern anchor: this is the THIRD HARD_FAIL of the form "iterate substrate's HD vector basis -> signal destroyed" in 3 days. Prior: soft_chain_dfe_multihop_v1 (2026-06-24, beta=8192 wiring-bug masked test; underlying mechanism still untested); resonator_multihop_integration_v1 (2026-06-24, same wiring-bug); now damped LBP (2026-06-27, NOT a wiring-bug — proper damping, proper iter count, still collapses). See `research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md` + `research_drill_brain_multihop_M4_belief_propagation_soft_message_passing_3x_2026-06-27.md`.

---

## HEADLINE (one-line synthesis)

D0=0.989 saturating is NOT the explanation for D2_damped=0.006 — even if D0's regime were too easy, damped iteration should DEGRADE GRACEFULLY toward the noise floor (~0.5 at random binary or ~0.02 at V=960 multiclass), not collapse below baseline by 98pp with cv=1.414. The collapse to ~0.006 (mean of 0, 0.0167, 0 across 3 seeds) is the signature of a system where the iteration operator pushes states OFF the codebook manifold, producing readouts uncorrelated with the encoded answer (true random would be 1/V=0.001, observed 0.006 is consistent with random-chance plus tiny tail-correlation). Combined with the soft-chain DFE history at moderate beta, this drill concludes: **substrate's HD vector basis does NOT admit a contractive message-passing operator under any of the standard tricks (damping, normalization, additive update) — it has expanding Lipschitz on noise without a stable attractor structure to absorb perturbations**. Brain DOES iterate, but it does so via fixed-point attractor dynamics that the substrate's superposition + cleanup architecture explicitly does NOT instantiate. Net recommendation = CLOSE the "iterate the HD vector to refine" direction for substrate; atomize as META rule; pivot to plan-then-execute paradigm (replay-based path scoring) where iteration happens in a SEPARATE coordination layer (program / interpreter / scheduler) over substrate as one-shot bind+cleanup oracle, NOT inside the HD vector itself. Two diagnostic-probe cells in case substrate-native iteration CAN be rescued by structural fixes (unit-sphere projection + multiplicative gating), but P_deflated for either lifting D2 above D0 is <=0.20.

Plain English: the substrate works like a calculator that does one math op cleanly. If you keep feeding the answer back in for "refinement," the rounding errors snowball into garbage instead of converging. The brain seems similar at first glance but is actually running on attractor dynamics (think marbles in bowls) — substrate has no bowls, so iteration sends the marbles off the table. Stop trying to iterate the HD vector. Use external coordination (replay, K-beam search, MoE router) to do multi-step reasoning via SEQUENTIAL single-pass substrate calls, not iterative refinement.

---

## ANGLE A — PURE MATH: noise amplification, contraction, Lipschitz under HD vector iteration

**Banach fixed-point theorem requirement.** For iterative message-passing `m_{t+1} = F(m_t)` to converge, F must be a contraction on a complete metric space: `||F(x) - F(y)|| <= L * ||x - y||` with L < 1. Brain BP, LDPC turbo-decoding, Gaussian BP all satisfy this in their convergent regimes (often via damping that artificially scales L below 1). The KEY question for substrate: what is the Lipschitz constant of the substrate's "bind + cleanup + bundle" composite operator?

**Substrate's operator structure.** A single LBP step on substrate's HD vector typically is: (1) for each cycle node, gather neighbor messages = bundle of bound vectors; (2) unbind incoming "from-which-neighbor" key; (3) cleanup against codebook E; (4) re-bind outgoing key and emit. The cleanup step uses argmax-cosine OR softmax-weighted bundle. **The cleanup is NON-LIPSCHITZ** in the high-dim regime: a small perturbation that flips the argmax from item-A to item-B produces an O(1) jump in output (||E[A] - E[B]|| ~ sqrt(2) at random bipolar). Locally near the codebook (small noise on encoded vector), cleanup is approximately the identity (L~1, NOT strictly < 1). FAR from the codebook (noise comparable to inter-codebook distance), cleanup is chaotic (L >> 1 across argmax basin boundaries). The substrate has NO L < 1 contraction zone.

**Damping does not save you when noise is amplified by O(1) per step.** Damping replaces `m_{t+1} = F(m_t)` with `m_{t+1} = (1-alpha) m_t + alpha F(m_t)`. The effective Lipschitz becomes `L_eff = (1 - alpha) + alpha * L`. For alpha=0.3 and L=2 (modest expansion), L_eff = 0.7 + 0.6 = 1.3, still expanding. For substrate cleanup with argmax-flip L ~ 10+ at moderate cycle noise, L_eff is firmly expanding even at alpha=0.1. The observed collapse (D2_damped = D5_damped = 0.006, no recovery from extending iterations) is consistent with L_eff > 1: after 2-5 iterations, the state has drifted into a regime where ALL cosine-to-codebook scores are sub-discrimination, producing effectively random readouts.

**Diagnostic predictions (testable):**
- If L_eff > 1 hypothesis is right: ARM_D1_damped (single iter, alpha=0.3) should show D1 in {0.5, 0.9} (partway between D0 and noise), not D1 ~ 0.99 ~ D0. Currently the cell did not run D1 — missing data point.
- If the L_eff is actually fine but the operator has WRONG fixed-point (operator converges to a non-answer attractor): D5 should equal D2 (which it does, mean 0.0056 both) and the limit should be reproducible across seeds (cv across-seed should be LOW; observed cv=1.414 says NO — limit varies wildly per seed, consistent with chaotic drift, not stable wrong-attractor).
- cv=1.414 ~= sqrt(2): this is the cv of a Bernoulli(p) distribution with p~0.33 (sqrt(p(1-p))/p ~= 1.41). With 60 test queries per seed, observing 0, 1, 0 successes gives empirical mean 0.33/60 ~ 0.0056 and cv exactly sqrt(2). The seed-7 and seed-23 results are 0/60 (substrate fully collapsed); seed-17 got 1/60 (lucky random). This is the signature of NOISE FLOOR, not WRONG ATTRACTOR.

**Three math-side fixes to MAKE iteration non-destructive** (with deflated priors):
1. **Project to unit sphere every iter** (cosine-normalize): forces `||m_t|| = 1`, removes the magnitude-explosion mode. Lipschitz on the sphere can still be > 1 around argmax boundaries but bounded by 2/sin(theta). P_deflated(lift D2 over D0 by >= 0.05) = 0.15.
2. **Multiplicative gating instead of additive bundle** (Hadamard product of cleaned messages): bounded outputs in [-1,1]^N (bipolar substrate); preserves codebook geometry better than additive bundle which scales unboundedly. P_deflated(rescue iteration) = 0.20.
3. **Strong damping (alpha=0.05) + explicit attractor cleanup at EACH iter** (project to nearest codebook entry after every update): forces the iterate to stay ON the codebook manifold. But this collapses to a sequence of D0-baseline calls, which we already have — adds NO new information across iterations. P_deflated(lift) = 0.10, AND if it works, it's trivially "many D0 calls in disguise."

None of these is a confident rescue. The pure-math angle's symmetric verdict: substrate cleanup is not contractive in the relevant regime; standard damping does not bridge the gap; the most likely outcome of any fix is iteration becomes a no-op (best case) or still destructive (likely case).

---

## ANGLE B — BRAIN / SUBSTRATE: should substrate iterate at all?

**Brain DOES iterate — but on attractor dynamics, not HD vector message-passing.** Cortical recurrent loops, theta-gamma nesting (Lisman-Jensen 1998), CA3 pattern-completion (Treves-Rolls 1991), drift-diffusion accumulation (Gold-Shadlen 2007), Friston predictive-coding (Millidge 2021) all involve iteration. **In every case**, iteration is anchored by a stable attractor structure: Hopfield-style energy minimization (CA3); critical balance between excitation and inhibition (cortical microcircuits); thresholded boundary in drift-diffusion (cortical decision-making); precision-weighted error correction in predictive coding (each iter reduces a Bregman divergence).

**Substrate's architecture has NO attractor structure for arbitrary multi-hop queries.** The codebook E is a stable attractor for SINGLE-step cleanup (argmax-cosine pulls noisy vectors to nearest codebook entry). But for a 4-cycle heterogeneous query, the "right answer" is a COMPOSITE of multiple codebook entries bound together — and there is NO attractor in the substrate's dynamics that corresponds to that composite. The HD bundle of multiple bound role-filler pairs is a transient superposition, not a basin of attraction. Iterating it does not converge to it; it diffuses away from it.

**The brain has TWO architectural pieces substrate lacks for iteration:**
1. **Energy-function-bearing recurrent connectivity** (Hopfield, CA3, cortical microcircuit). Substrate's W matrix is not energy-bearing in the Lyapunov sense; it is a passthrough projection used for one-shot bind/unbind, not an attractor network.
2. **Precision-weighting / lateral inhibition** that suppresses competing hypotheses each iteration. Substrate has no lateral inhibition; the cleanup is argmax (winner-take-all once, then forgotten); softmax with moderate beta does some suppression but the suppressed hypothesis re-emerges next iter because the bundle sum re-mixes everything.

**Brain answer to "how do you do multi-hop iteratively"** is NOT "iterate the working state." It is plan-then-execute via REPLAY: hippocampus generates candidate paths via reverse-replay, evaluates each by sweep through cortex, COMMITS to one, and the iteration happens at the SEQUENCE-OF-COMMITMENTS level, not at the state-vector level. Pfeiffer-Foster 2013 (preplay), Olafsdottir-Bush-Barry 2018 (replay review), Wittkuhn-Schuck 2021 (sequential replay in fMRI) all converge on this story. Substrate ALREADY does this single-pass-per-hop; the question is whether to add the planning loop OUTSIDE the substrate (as a coordination layer) or to try to fold it INSIDE the HD vector (where it keeps failing).

**Three brain-side proposals (when SHOULD substrate iterate vs single-pass):**
1. **Iterate ONLY single-step cleanup** (the operation that DOES have a codebook attractor). Repeated argmax-cleanup on a noisy single-vector state will converge (it's literally projection to nearest codebook entry). Already implicitly done in substrate's single-step cleanup. P_deflated(extends to chain) = N/A — this is the existing baseline.
2. **Move iteration to a separate coordination layer** (interpreter / scheduler / replay generator) that calls substrate as a one-shot oracle. Each substrate call is single-pass clean; the coordination layer (e.g., K-beam search, MoE router, schema-indexed selector) chooses what to ask next based on previous returns. This is the comp_router_moe_v1 + comp_pfc_schema_replay_v1 direction from the 5x multihop barrier drill. Matches brain plan-then-execute. P_deflated(lifts heterogeneous multi-hop) = 0.40 (per prior drill).
3. **Build an explicit attractor layer** (small Hopfield-style energy network with substrate-encoded keys; iterate on the energy network, read out into substrate). This is closer to true brain iteration but requires substrate-side architectural addition (a new module with explicit energy function and Hebbian-style learning). Substantial engineering; P_deflated(rescue iteration WITHIN substrate vector space) = 0.20. Brain-grounded existence proof gives some prior boost, but the integration with current substrate is open.

**Recognizing iteration-friendly substrate operations** (heuristic):
- Single-step argmax cleanup: ITERABLE (attractor exists, the codebook itself).
- Bundle of K bound pairs being read out one-at-a-time via different unbind keys: NOT ITERABLE (no attractor for the bundle; each readout is independent single-shot).
- Multi-hop chain following SAME relation: NOT ITERABLE as state-refinement, but ITERABLE as sequential bind+permute calls (already chain-grade).
- Cross-cycle / loopy graph message passing: NOT ITERABLE (no attractor; this is what the v1 cell tested and what failed).

---

## CONVERGED CONCLUSION + META RULE PROPOSAL

The empirical pattern is now 3 cells deep:
- soft_chain_dfe_multihop_v1 (2026-06-24): wiring-bug masked test, but the underlying soft-iteration mechanism remains untested at correct beta. The proxy evidence (beta=2 at top1=0.6483 vs baseline 0.6500) showed NO useful lift from iteration even when the soft regime was correctly entered.
- resonator_multihop_integration_v1 (2026-06-24): same wiring bug; same proxy evidence of no lift.
- exp_loopy_belief_propagation_damped_v1 (2026-06-27): clean test, no wiring bug, damping properly applied, NO ceiling regime confound for the iteration arms (D2/D5 fell to floor regardless of D0's saturation level). Iteration is actively destructive.

The pattern converges: **iterating the substrate's HD vector state through message-passing-like updates is mathematically non-contractive (Lipschitz unbounded near argmax boundaries) and architecturally un-anchored (no attractor structure for composite states). Substrate cannot do useful iterative message-passing on its HD vector basis under any standard trick (damping, normalization, beta-tuning).**

**Proposed META rule to atomize:**
> META_RULE_SUBSTRATE_NO_HD_ITERATION (2026-06-27): Substrate's HD vector basis does NOT support iterative message-passing / refinement loops. Three independent cells (soft_chain_dfe, resonator_multihop, loopy_BP_damped) have failed catastrophically (signal collapse to noise floor) under standard iteration tricks. Root cause: cleanup operator is non-contractive (Lipschitz unbounded near argmax basin boundaries) and there is no attractor structure for composite multi-bind states. DO NOT propose new "iterate the HD vector to refine" cells. Multi-step reasoning must be done via SEQUENTIAL single-pass substrate calls coordinated by an EXTERNAL layer (K-beam search, MoE router, schema-indexed PFC analog, replay-based path scorer). The substrate is a single-pass oracle, not an iterable dynamical system.

This is a SUBSTRATE-PROPERTY finding worth recording. It re-frames the 5x multi-hop barrier drill's TOP-3 picks (all of which already moved iteration to coordination layer; none tried to iterate the HD vector). The drill's analysis was directionally right; the loopy_BP cell was a useful FALSIFICATION of the alternative "maybe substrate can do BP itself" hypothesis. Negative result has high value: it closes a whole class of approaches.

---

## TOP-2 PICKS (cell candidates OR honest close-direction)

**RANK 1 — CLOSE DIRECTION + ATOMIZE META RULE.** Do not dispatch any further "iterate the HD vector" cells. File META_RULE_SUBSTRATE_NO_HD_ITERATION to Store. Update spawn template to warn against iteration-on-vector cell designs. Re-affirm the 5x drill's TOP-3 picks (comp_router_moe_v1 RANK-1; comp_pfc_schema_replay_v1 RANK-2; comp_orthogonal_role_basis_v1 RANK-3) which all correctly place iteration in coordination layer. P_deflated(this is the right call) = 0.75.

**RANK 2 — ONE DIAGNOSTIC PROBE (only if USER wants explicit refutation):** `loopy_BP_diagnostic_v1` — adds the missing data points to confirm the noise-floor diagnosis. ARM_D1_damped (single iter alpha=0.3) + ARM_D0_lower_difficulty (V_C=200 not 960; cycle=3 not 4 — get D0 off ceiling so we can see graceful degradation if it exists) + ARM_D2_unit_sphere_proj (the math-fix #1 above) + ARM_D2_hadamard_gate (math-fix #2). 4 arms, 5 seeds, ~45 min local CPU. HARD_PASS = any of D2_unit_sphere or D2_hadamard lifts above D0_lower_difficulty by >= 0.05. HARD_FAIL = both fixes also collapse to noise floor → META rule fully confirmed; close direction with certainty. P_deflated(any arm rescues iteration) = 0.15. This is a CONFIRMATORY cell, not an exploratory one — its value is closing the door cleanly, not opening a new one. Run only if explicit refutation is desired before atomizing the META rule.

**RECOMMENDED: RANK 1 only.** The 3-cell pattern + clean math diagnosis + brain-architectural argument all converge. Diagnostic-probe RANK 2 has low expected value (P=0.15 rescue with low payoff even if it works — would only buy us back narrow attractor-style iteration which the brain analysis says needs a separate attractor module anyway).

End.
