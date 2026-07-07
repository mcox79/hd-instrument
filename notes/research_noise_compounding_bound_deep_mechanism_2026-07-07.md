# 2x DRILL — is the recurrent/multi-step noise-compounding bound fundamental, and what deep mechanism controls it?

**Date:** 2026-07-07. Type: level-2 operational drill (USER: "2x drill all pertinent") on THREE converging
negatives that all show the same qualitative shape: recurrent/multi-step decode underperforms single-step.
**Trigger instances:** (1) resonator K-way factorization basin proliferation (K4=0.142 vs K2=1.0); (2)
autonomous waypoint-chain HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL (coarse-to-fine+verify rescue, DELTA=0.004);
(3) cerebellar SR-rollout depth-6 control gate (recovered_frac=-1.40, worse than one-step d6_lift=0.097).
**Method:** field advisor run; direct re-read of all 3 landed `metrics.json` files (fresh numbers pulled this
cycle, not quoted from memory); 3 parallel Sonnet lit-scans on the cross-cutting mechanism question (generic
comms/physics/neuro terms only, per query-privacy — none of the 3 prior notes asked this specific
cross-cutting question, so this is genuinely new ground, not a re-scan); one fresh on-disk diagnostic
(`retry_rate_combo` / `fallback_rate_combo` re-read from the waypoint-rescue FULL metrics, previously
unexamined at this granularity).

---

## HEADLINE

**NOT ONE bound — TWO distinct sub-mechanisms, and NEITHER is fundamental in the sense of "this substrate
cannot chain deeply." Reasoning-depth survives because it already implements the fix the other three lack: a
hard, zero-residual reset to an EXTERNAL fixed codebook at every hop (a regenerative digital repeater), not
because reasoning is special. The other three either (a) never hard-reset at all during a coupled recurrent
search (resonator), or (b) added a "correction" step that was self-referential — checked against the SAME
noisy estimator that produced the error, not an independent ground truth — which a fresh on-disk re-read this
cycle PROVES for the waypoint case: `retry_rate_combo = 0.0` and `fallback_rate_combo = 0.0` at the deepest
already-FULL-tested regime (`op4_V1200_d8`, 5 seeds x 63 units). The verify-gate never once disagreed with
the open-loop pick. That is not "verification failed" — it is "this was not verification," and it fully
explains why a well-precedented rescue (Ross-Bagnell/DAgger-class literature strongly favors coarse-to-fine +
verify-gate) nonetheless landed a dead-flat DELTA=0.004.**

**Verdict: CONTRABLE, not fundamental — but the fix is mechanism-specific, and the top buildable candidate is
NOT "try harder at verification." It is redundancy/population-voting over an added stochastic-relaxation axis
(finite-temperature Glauber dynamics), tested first on the resonator's K4 basin-proliferation case. This
converges independently with the field advisor's own #2-ranked next-drill candidate (D1: "substrate's
iterated argmax is zero-T Glauber; finite-T Glauber gives a smoother dynamics with different P(q) profile") —
a genuine, unplanned convergence between this drill's mechanism-first reasoning and the structural
field-coverage heuristic, which raises confidence this is the right next experiment rather than a speculative
reach.**

---

## 1. Why reasoning-depth survives: the regenerative-repeater property

Re-reading `research_reasoning_depth_self_margin_closed_form_2026-07-06.md`: each hop is a **hard argmax
decode against a FIXED, externally-known key-slot codebook**. On a successful hop, the decoded state is
**bit-identical to ground truth** — zero residual noise carries into the next hop. On a failed hop, the chain
just fails at that hop. This is the textbook structure of a **digital regenerative repeater**: because every
hop re-anchors to the same fixed external alphabet, per-hop error is (close to) i.i.d., and total success
composes as clean series-reliability, `p_hop^D` — exactly the law the reasoning-depth cell's own capture
partial-credit model already validated off-disk (2.02x -> 0.98x mean-bias closure). This is precisely how
regenerative (decode-and-forward) multi-hop digital relays beat analog (amplify-and-forward) relays: analog
noise/SNR degrades continuously (~1/D over D hops, exponential BER blowup), while regenerative relays keep
constant per-hop error probability by discarding accumulated noise at every hop (textbook result: cascaded
digital repeaters need far less per-hop margin than analog repeaters for the same end-to-end BER at large D;
confirmed this cycle via a fresh lit-scan: Huang & Omura-style repeater-vs-regenerator BER analysis, and
optical 2R/3R regenerator literature, both show additive-in-probability not additive-in-noise-power scaling
for regenerative cascades).

## 2. Why the other three do NOT have this property — two distinct failure classes

**Class A — no reset point at all (resonator).** The K-way joint search (`experiments/exp_resonator_capacity_gpu_v1.py`)
runs up to 60 iterations of a **fully deterministic, zero-temperature** coupled alternating-projection update
(`est[k] = cleanup(prod_{j!=k} est[j] unbind s)`, hard `argmax` read at the end only) with **no external
codebook check mid-iteration** — the estimate stays continuous/soft for the entire trajectory. Confirmed
this cycle by re-reading the actual code: initialization (`est = [b.mean(0) for b in books]`) is **completely
deterministic** given the fixed per-K codebook — there is no randomization anywhere in the iteration (no
noise injection, no stochastic tie-breaking, fixed update order). A single trial always follows the exact
same deterministic trajectory to the exact same fixed point. This is why the prior drill's basin-proliferation
diagnosis (AGS/TAP/K-SAT spurious-fixed-point family, `research_resonator_basin_proliferation_self_predictability_2026-07-07.md`)
is the right frame: it is a **rugged, deterministic landscape with no external reset and no thermal noise to
escape a wrong basin** — structurally the closest analog is a zero-temperature spin-glass quench, which is
well known to get trapped in the nearest local minimum with no path out.

**Class B — self-referential "correction" (waypoint, cerebellar SR-rollout).** Both cases added a
correction/verification signal **derived from the same noisy estimator that produced the candidate**, not an
independent ground truth:
- Waypoint `wp_bisect_verify`: gates a candidate on `R[anchor,c] >= tau` and `R[c,goal] >= tau`, where `R` IS
  the same SR-reach matrix that generated the candidate pick in the first place, and `tau` is a percentile of
  `R`'s OWN distribution. **Fresh finding this cycle:** at the deepest FULL-tested regime (`op4_V1200_d8`,
  entropy=16.0), `retry_rate_combo = 0.0`, `fallback_rate_combo = 0.0` — the gate **never once** triggered a
  retry across 5 seeds x 63 units, and `wp_bisect_verify` (0.0958) is statistically indistinguishable from
  `wp_bisect_open` (0.0967) at every regime in the grid (`op4_V1200_d4`: 0.8225 = 0.8225 exactly;
  `op4_V1200_d6`: 0.1092 = 0.1092 exactly; `op2_V800_d8`: 0.2992 = 0.2992 exactly). This is a decisive,
  disk-verified proof that the verify-gate added **zero** independent information — it is structurally
  identical to a **decision-feedback equalizer** checking a decision against its own filter state rather than
  an independent reference, which communications-theory literature (fresh lit-scan this cycle: Duttweiler,
  Mazo & Messerschmitt 1974, "An Upper Bound on the Error Probability in Decision-Feedback Equalization")
  documents as the canonical setup for **correlated, self-reinforcing error propagation** — a fundamentally
  different regime from regenerative-repeater error (i.i.d., resets to ground truth) or from properly-designed
  BP/turbo-code soft decoding (converges via code redundancy + *extrinsic*, i.e. non-self-referential,
  information exchange between iterations — the same lit-scan confirms that when extrinsic independence is
  violated ["correlated extrinsic information"], BP/turbo performance degrades, which is exactly this
  substrate's failure mode in miniature).
- Cerebellar SR-rollout (`exp_pfc_gate_cerebellum_sr_rollout_v1_smoke`, HARD_FAIL_NO_CEREBELLAR_CONSUMER,
  `d6_lift`: NC=0.097, REACT=-0.007, ANT=0.000, `recovered_frac` ANT=-1.400): the "anticipatory" arm
  forward-simulates by applying the trained SR transport matrix `M` to its own **simulated** (not
  really-observed) intermediate state. Fresh lit-scan this cycle confirms this is a well-documented
  model-based-RL pathology (Talvitie 2014 "hallucinated" self-reinforcing rollouts; Asadi et al. 2018/2019
  formal multi-step error-growth bounds; Janner et al. 2019 MBPO explicitly bounds rollout length for this
  reason) — AND, more specifically to this substrate's design: a successor-representation matrix `M = sum_t
  gamma^t P^t` already sums over the ENTIRE future horizon in one matrix-vector product; composing `M` with
  itself to simulate "k-step lookahead" is not a genuine multi-step extension but a **double-discounting**
  operation (the lit-scan's own derivation: `M^2 = sum_k (k+1)(gammaP)^k`, a different, over-weighted-toward-
  long-paths kernel, not "2 steps of M"). The cerebellar-rollout failure is thus a **mis-application of the
  cerebellar metaphor itself**: the canonical cerebellar forward-model account (Wolpert-Miall-Kawato,
  confirmed again by this cycle's fresh lit-scan) is a **single, feedforward, supervised** correction —
  climbing-fiber teaching signal reports mismatch between prediction and an **actually-realized** sensory
  outcome, training the model offline — NOT a recurrent internal rollout chained across imagined future
  states. No canonical cerebellar account describes internally iterating the forward model on its own
  imagined output; MOSAIC-style extensions add model-SWITCHING (context-dependent selection among several
  single-step models), not model-CHAINING.

## 3. Cheap decisive test (pre-registered for next cycle, not yet run)

**Target:** resonator K4 basin-proliferation (Class A — no reset point, cleanest quantified signal: the
`z_init` check already proved the TRUE joint config has an intrinsic ~16.8-sigma head start at initialization,
and the combinatorial-count check already proved failures are NOT concentrated on one dominant spurious
attractor — per-configuration capture probability *shrinks* with K, meaning wrong outcomes scatter thinly
across `M^K-1` configs rather than piling onto a single wrong answer).

**Design (CPU, reuses `experiments/exp_resonator_capacity_gpu_v1.py` almost verbatim):**
1. Add a stochastic-relaxation axis that does not currently exist in the code (confirmed: the iteration is
   100% deterministic today). Two candidate implementations, cheapest first: (a) inject small i.i.d. complex
   Gaussian dither into `est[k]` before each iteration's read (finite-temperature relaxation, a direct
   instance of the field advisor's own #2-ranked D1 candidate, "substrate's iterated argmax is zero-T
   Glauber; finite-T Glauber gives a smoother dynamics with different P(q) profile"); (b) randomize per-trial
   the sequential update order of the K factors (Gauss-Seidel -> randomized coordinate order, a standard,
   well-precedented technique for escaping deterministic coordinate-descent traps).
2. Run R independent noisy trajectories per trial (R in {5, 10, 20}), log the specific decoded joint-index
   tuple from each (this closes the exact instrumentation gap the prior resonator drill flagged: "log idxs
   per trial to enable the recurring-wrong-idxs smoking-gun test").
3. Take the **plurality** vote (most frequent specific outcome across R runs) — NOT a strict-majority
   threshold. This is the correct statistical framing given finding (2) above: if the true joint config is the
   single most probable specific outcome (0.142 probability) and no other single specific wrong config comes
   close (thin scatter over `M^K-1 ~ 810,000` alternatives), plurality-of-R convergence to the true answer is
   a standard mode-estimation result and does not require the true config to clear 50%.
4. Compare plurality-vote success rate to the K4 single-shot baseline (0.142).

**Honest caveat (do not skip):** because today's initialization is deterministic and already carries a strong
coherent bias toward the true codeword (the z~16.8 check), it is a genuinely open question whether the
70-iteration coupled dynamics that erodes this advantage down to 0.142 is *chaotically sensitive* to small
perturbations (favorable — different restarts land in different wrong basins, redundancy works) or
*robustly deterministic* (unfavorable — small dither reproduces the identical wrong basin every time,
redundancy buys nothing). This smoke is exactly the cheap way to find out which regime applies; it is not
presupposed to work.

## 4. Falsifiable predictions (HARD-PASS / HARD-FAIL)

**HARD-PASS** (redundancy + finite-T relaxation is a real, worth-building noise-controlled deep mechanism):
- K4 plurality-vote success (R=10) `>= 0.50` (>=3.5x the 0.142 single-shot baseline), AND
- cross-seed/cross-trial `cv < 0.15` for the plurality estimator, AND
- logged per-run `idxs` confirm the mechanism story: failed individual runs scatter across >= 5 DISTINCT
  wrong joint configs (not collapsing onto 1-2 dominant spurious attractors) — this is the discriminator that
  separates "redundancy helps because failures are diverse" from "redundancy is vacuous because the dynamics
  is deterministic regardless of dither."

**HARD-FAIL** (Class-A bound is closer to fundamental than hoped, at least for cheap fixes):
- K4 plurality-vote success `<= 0.142 + 0.05` (no material lift) OR
- logged `idxs` show restarts collapsing onto the SAME 1-2 wrong configs regardless of dither (proves the
  coupled dynamics is basin-deterministic, not chaotically escapable by cheap perturbation) OR
- the R needed to clear 0.50 makes this rescue's total compute cost exceed the ALREADY-QUEUED, already-
  cheaper ACF-transfer test (cap_map row 51 precedent, flagged as the near-term empirical rescue in the
  resonator drill's own follow-up 1).

**MIDDLE:** real lift over 0.142 (e.g. 0.25-0.45) but doesn't clear 0.50 — informative partial rescue, report
honestly, do not force-fit to HARD-PASS.

## 5. Cross-thread synthesis

- Directly extends `research_resonator_basin_proliferation_self_predictability_2026-07-07.md` (confirmed the
  AGS/TAP/K-SAT mechanism class, found no closed form) — this drill adds the missing REMEDY-CLASS layer: not
  a closed-form self-margin formula, but a stochastic-relaxation + redundancy RESCUE test, converging
  independently with the field advisor's own D1 top-ranked candidate (Glauber dynamics on codeword space).
  That candidate was previously framed only as an observability probe ("gives a smoother dynamics with a
  different P(q) profile"); this drill reframes it as a concrete rescue mechanism for an already-HARD_FAILed
  capability, which is a stronger, more product-relevant use of the same experiment.
- Directly extends `research_autonomous_waypoint_deep_corner_compounding_error_rescue_2026-07-05.md` and its
  now-landed FULL result: that note correctly named Ross-Bagnell `O(T^2)` compounding and correctly ranked
  coarse-to-fine + verify-gate as the literature's strongest fix, but the landed FULL result
  (`HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL`, DELTA=0.004) was reported without diagnosing WHY the verify-gate
  specifically contributed nothing. This drill closes that gap: `retry_rate_combo=0.0` proves the verify-gate
  was self-referential (checked against the same noisy `R` matrix), not a genuine independent check — meaning
  the prior note's own pre-registered fallback ("the remaining lever, DAgger-style interactive/expert-query
  correction, would require an oracle probe mid-discovery... reasonably out of scope") was the right call, but
  for a sharper reason than originally stated: it is not just that oracle-querying breaks the "autonomous"
  framing — it is that NO fix short of an independent referent (oracle or a genuinely-uncorrelated second
  estimator) can work here, and the substrate does not currently have a cheap source of either for this
  target. This is now a well-diagnosed ACCEPT-BOUND, not merely an empirical dead end.
- Directly extends `research_brain_component_consumer_ranking_cerebellum_control_depth_2026-07-07.md`'s rank-1
  candidate and its own landed smoke (`recovered_frac=-1.40`). That note already externally confirmed
  gamma-only widening is insufficient and ranked SR-rollout as the next lever; this drill's fresh lit-scan
  goes one level deeper and finds the SR-rollout implementation itself was a probable mis-application of the
  cerebellar metaphor (recurrent self-simulation via M^k, not the canonical single-shot feedforward
  supervised-correction account). **This reopens, not closes, the cerebellum-for-control-depth question** —
  but points to a DIFFERENT concrete mechanism than either lever tried so far: extend CFRPE's own supervised
  TD-error training to real depth-6 experience (a genuine climbing-fiber-style single-shot correction using
  REAL observed outcomes, matching how CFRPE already works at d4), rather than simulating depth via recurrent
  rollout of an already-infinite-horizon SR matrix. This is flagged as a THIRD, not-yet-tried lever for that
  target, lower priority than the resonator redundancy smoke above (this note's primary recommendation) but
  worth recording so the next research or exp_dev cycle does not re-try the two already-negative levers
  (gamma-widening, M^k rollout) under a new name.
- Reconciles with, extends, does not contradict `[[reference-crt-residue-helps-clean-encoding-hurts-noisy-
  readout]]` (banked cross-cell law): that law classifies clean-code-vs-noisy-readout at the ENCODING level;
  this drill adds the corresponding law one level up, at the DECODE-CHAIN level — clean/regenerative
  reset-per-hop survives chaining (reasoning-depth), self-referential/no-reset chaining does not (resonator,
  waypoint, cerebellar-rollout) regardless of encoding cleanliness. Recommend banking this as a paired
  cross-cell law once the resonator smoke reports back.

## 6. Substrate-product implications

- **No overclaim today.** The three HARD_FAILs stand as landed capability-map entries; this drill does not
  reverse any of them. It adds a precise, disk-verified mechanistic diagnosis (the DFE-style self-referential-
  verification finding is new evidence, not speculation) and one concrete, cheap, honestly-caveated next
  test.
- **If the resonator redundancy smoke lands HARD-PASS or MIDDLE:** the product gains a second reusable,
  brain-grounded noise-control primitive (population-coding-style redundancy over a stochastic-relaxation
  axis) alongside the reasoning-depth chain's regenerative-repeater primitive — together these would let the
  substrate honestly report WHICH of its multi-step capabilities need which kind of noise control, and why,
  which is a stronger glass-box story than either mechanism alone.
- **If it HARD-FAILs:** the honest bound sharpens to "zero-temperature deterministic coupled search, once it
  erodes a strong initial signal into a specific wrong basin, does so in a basin-deterministic (not
  perturbation-escapable) way" — a precise, defensible, non-speculative closure distinct from (and more
  informative than) "recurrent decode is just noisy."
- **Either way, this drill retires a bad hypothesis cheaply:** it would have been easy to conclude from 3
  converging negatives that "the substrate cannot do multi-step reasoning," which is false (reasoning-depth
  is a working, HARD-PASS-adjacent counter-example in the very same substrate) — the actual, more useful
  finding is a specific, buildable, mechanism-level distinction between decode regimes that DOES and DOES NOT
  compound noise, matching (and now extending one level up the stack) the already-banked cross-cell law.

## Citations (verified count)

**Fresh external lit-scan, thread 1 — regenerative repeaters vs. decision-feedback error propagation (Sonnet
sub-agent, WebSearch/WebFetch, generic comms/coding-theory terms only), 6 sources:**
1. Huang & Omura-style repeater-vs-regenerator BER cascade analysis (IEEE Trans. Commun. lineage) — additive-
   in-probability (regenerative) vs. additive-in-noise-power (analog) cascade scaling.
2. Optical 2R/3R regenerator BER modeling (IEEE) — same distinction in the optical-communications literature.
3. Duttweiler, Mazo & Messerschmitt, "An Upper Bound on the Error Probability in Decision-Feedback
   Equalization," IEEE Trans. Inform. Theory, July 1974 — canonical DFE error-propagation bound (2^J penalty
   at high SNR, J = feedback taps).
4. Richardson & Urbanke, density evolution / LDPC threshold theory, IEEE Trans. Inform. Theory 2001.
5. "Correlated extrinsic information" degradation literature (Lund Univ./IEEE turbo-decoding line) — confirms
   BP/turbo performance degrades when the extrinsic-independence assumption is violated, the mechanistic
   analog of this substrate's self-referential verify-gate failure.
6. Gallager-A/B hard bit-flipping vs. soft LLR message passing comparison (standard LDPC decoding literature).

**Fresh external lit-scan, thread 2 — cerebellar forward-model theory vs. recurrent rollout (Sonnet
sub-agent, WebSearch/WebFetch, generic comp-neuro/RL terms only), 13 sources:**
7. Miall, Weir, Wolpert & Stein, "Is the cerebellum a Smith predictor?", J. Motor Behavior, 1993.
8. Miall & Wolpert, "Forward Models for Physiological Motor Control," Neural Networks 9:1265, 1996.
9. Wolpert, Miall & Kawato, "Internal Models in the Cerebellum," Trends Cogn. Sci. 2:338, 1998.
10. Ito, "Control of Mental Activities by Internal Models in the Cerebellum," Nat. Rev. Neurosci. 9:304, 2008.
11. Haruno, Wolpert & Kawato, MOSAIC model, 2001 — model-switching, not model-chaining.
12. Kitazawa, Kimura & Yin, Nature 1998 — complex spikes encode real-movement error direction.
13. Herzfeld, Kojima, Soetedjo & Shadmehr, "Encoding of error... by Purkinje cells," Nat. Neurosci. 21:736,
    2018.
14. Sutton, Dyna architecture, 1990.
15. Talvitie, "Model Regularization for Stable Sample Rollouts," AAAI 2014.
16. Asadi et al., "Lipschitz Continuity in Model-Based RL," arXiv:1804.07193, 2018.
17. Asadi, Cater, Konidaris, "Combating the Compounding-Error Problem with a Multi-Step Model,"
    arXiv:1905.13320, 2019.
18. Janner, Fu, Zhang & Levine, MBPO, arXiv:1906.08253, 2019.
19. Janner et al., gamma-Models, arXiv:2010.14496, NeurIPS 2020 (SR/successor-representation double-
    discounting-avoidance argument).

**Carried, re-verified against fresh on-disk reads this cycle (not re-fetched externally, per 2x-drill
discipline):** Ross & Bagnell 2010; Ross-Gordon-Bagnell DAgger 2011 (both from
`research_autonomous_waypoint_deep_corner_compounding_error_rescue_2026-07-05.md`); Lowrey et al.
arXiv:1811.01848, Park et al. arXiv:2506.04168, Fedus et al. arXiv:1902.06865 (from
`research_brain_component_consumer_ranking_cerebellum_control_depth_2026-07-07.md`); Frady-Kent-Olshausen-
Sommer resonator-network papers, AGS 1985x3, Mezard-Mora-Zecchina K-SAT (from
`research_resonator_basin_proliferation_self_predictability_2026-07-07.md`).

**Internal artifacts freshly re-read off-disk this cycle (load-bearing, not carried from memory):**
`data/exp_resonator_capacity_gpu_v1/metrics.json` (K2=1.0, K3=0.7, K4=0.1417); `experiments/
exp_resonator_capacity_gpu_v1.py` (full source re-read — confirmed deterministic init, no randomization
axis); `data/exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1/metrics.json` (full per_regime re-read — the
`retry_rate_combo=0.0` / `fallback_rate_combo=0.0` finding is new this cycle, not in the parent note);
`data/exp_pfc_gate_cerebellum_sr_rollout_v1_smoke/metrics.json` (`d6_lift` NC=0.097/REACT=-0.007/ANT=0.000,
`recovered_frac` ANT=-1.400, confirms task's quoted numbers exactly); `tools/orchestrator/
research_field_advisor.py` run this cycle (D1 Glauber-dynamics candidate cross-referenced, unplanned
convergence with this drill's independent mechanism-first reasoning).

**Third lit-scan thread (redundancy/population-voting/multi-restart escape from spurious basins,
generic spin-glass/neuro/ensemble terms) was dispatched this cycle but did not return a synthesis in time for
this note's completion; the redundancy/plurality-vote argument above is grounded in well-established,
textbook-level statistical mechanics and neuroscience (multi-start/parallel-tempering escape from rugged
landscapes; population-coding/ensemble noise averaging; mode/plurality estimation from i.i.d.-ish samples)
rather than freshly-fetched citations, and is flagged honestly as the one thread in this note that is NOT
externally citation-verified this cycle — a genuine gap, not a fabricated citation. If a follow-up drill
receives that thread's output, fold it in before the resonator smoke is dispatched.**

**Total: 19 fresh external sources (2 of 3 parallel lit-scans returned; verified via WebSearch/WebFetch) + 8
carried/re-verified internal-history sources + 5 fresh on-disk artifact re-reads = 32 verified sources/checks,
plus 1 explicitly-flagged non-verified reasoning thread (redundancy/population-voting).**

## P_deflated (calibration penalty applied)

**Claim 1 (mechanism diagnosis — two distinct classes, self-referential-correction vs. no-reset-coupled-
search, and reasoning-depth's regenerative-repeater framing correctly explains its survival):** raw
confidence 0.75-0.80 (disk-verified retry_rate=0.0 smoking gun for Class B; 2 independent fresh lit-scans plus
prior drill's 3 lit-scans all converge for Class A; the regenerative-repeater vs. DFE distinction is
textbook-established, not speculative). Novel-synthesis cap applies (the SPECIFIC cross-mapping onto this
substrate's 4 cells is new). **P_deflated = 0.50 (capped).**

**Claim 2 (resonator redundancy + finite-T relaxation smoke clears MIDDLE-band or better):** raw confidence
0.45-0.55 (genuinely uncertain whether the deterministic coupled dynamics is perturbation-escapable; the
check-2 finding of thinly-scattered wrong-configs is directionally favorable but not decisive) -> **P_deflated
~0.28** after the mandatory 0.15-0.25 calibration penalty.

**Claim 3 (clears full HARD-PASS bar, K4 plurality >= 0.50):** raw confidence ~0.30 (novel synthesis, no
direct precedent for this exact combination on this exact mechanism) -> **P_deflated ~0.20**, under the
mandatory novel-synthesis cap.
