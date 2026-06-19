# Strategy x Research shore-up matrix — 2026-05-23

**Author**: combined Strategy + Research sub-agent (opus, single-shot)
**Trigger**: user directive "look at characteristics we need to shore up for our substrate and use indications from our research map to identify opportunities for research that could potentially resolve"
**Inputs**: cap_map v168 ([[active_priorities.md]] open-row inventory + stale-row inventory + portfolio gap audit Task 4 of cycle 188 proactive drill); `research_meta_map_and_adjacencies_2026-05-23.md` (110-drill yield matrix + adjacency graph + Patterns 1-7); field-advisor v168 (top-5 candidates by score; saturated-field caution); `research_cross_domain_probe_*_2026-05-23.md` (QECC-Kerdock-MUB STRONG, ICA-JADE medium-high, tensor-PCA high); `research_promising_direction_2026-05-23.md` (BBMD regime).
**Calibration**: per [[feedback-lit-scan-calibration-penalty]] deflated P 0.15-0.25 in uncharted regime; novel-synthesis cap P=0.50. Per [[feedback-no-smoke]] honest classification of each weakness as "math missing" vs "probe missing".
**Scope**: I enumerate 7 weaknesses with concrete probes. Per request to not pad, these are the 7 honest non-duplicate pairs after de-duplicating against in-flight (BBMD VAMP correspondence + KAPPA_PROFILE cross-codebook + Haar-vs-Kerdock cumulant + PFK partial-ETH + Gold sequences quickprobe).

---

## Weakness #1 — Cap 2 self-monitoring confidence: structurally CLOSED with no extant rescue verdict

**The weakness**: Cap 2 left the v153 portfolio at v160 with PROVISIONAL ❌ closure. Two independent metric framings (tau iteration count v153 + cosine margin v160) crossed pre-reg hard-fail. The substrate carries no margin/tau-based intrinsic confidence signal. Strategy filed `strategy_request_to_research_cap2_self_monitoring_rehab_2026-05-23.md` HIGH-priority with 5 rescue sketches but NONE of the five (endpoint-ID, VAMP posterior variance, chi_4-per-query, Kovacs-per-query, conformal subsumption) has been operationalized as an experiment. This is the largest open refutation in the portfolio.

**Field-coverage indication**: Three fields offer angles.
- **Free probability (tier-1, yield 100%)**: VAMP-on-chain (Cap 8) produces a Bayesian posterior variance per cue (Pattern 2 engineering-borrowed readout); never extracted as a Cap-2-substitute. This is Rescue 2 of the v160 rehab.
- **Conformal prediction (load-bearing, Pattern 1 metric re-axiomatization)**: re-axiomatize Cap 2 as a downstream conformal layer wrapping the existing Bet G calibration. This is Rescue 5 — Pattern 1 says re-axiomatize the audit metric before re-engineering the substrate. Zero substrate change; cheapest path; cleanest portfolio move.
- **Observability suite (chi_4 + Kovacs, load-bearing v166)**: chi_4 spike-per-query as a predictive confidence signal — Pattern 7 cross-family consistency. This is Rescue 3.

**Concrete probe proposal** — `cap2_conformal_subsumption_v1` (FIRST) + `cap2_vamp_posterior_variance_v1` (SECOND).
- **Type**: Both Anchor experiments. (1) is theory-only re-axiomatization + ~30 min CPU re-analysis of cycles 153 + 160 logits through a Venn-Abers wrapper. (2) is ~15 min CPU extraction of VAMP posterior variance from existing cycle-162 VAMP-on-chain runs.
- **Hypothesis**: (1) Cap 2 reframed as "calibrated abstention via conformal threshold on the Bet G confidence stream" satisfies the customer-facing self-monitoring claim WITHOUT any substrate-level margin signal — closure becomes a re-axiomatization not a capability loss. (2) VAMP posterior variance per cue correlates with retrieval correctness at Spearman rho >= 0.5, giving a Bayesian intrinsic-confidence signal at zero extra substrate cost.
- **Hard-fail**: (1) Venn-Abers conformal threshold fails to achieve >= 0.90 coverage at <= 0.20 abstention rate on Bet G stream → re-axiomatization does not deliver a customer-facing claim. (2) Spearman rho < 0.2 → VAMP posterior variance carries no usable confidence signal on this substrate.
- **Cost**: (1) ~30 min CPU + 1 hr theory write-up. (2) ~15 min CPU.

**Priority**: **HIGH**. Cap 2 is the only PROVISIONAL ❌ closure in the v168 portfolio and the v160 rehab request explicitly names Rescue 5 (conformal) as the cleanest move. Per Pattern 1 (metric re-axiomatization is the highest-leverage cheap intervention) this is the single highest-leverage probe in this matrix.

---

## Weakness #2 — Bet T parallel hypothesis tracking: 67 cap_map versions stale at PARTIAL min_acc=0.689

**The weakness**: PARTIAL min_acc=0.689 mean=0.740 at cycle 101 (cap_map v101). Sixty-seven cap_map versions stale at v168. 2/3 rescues KILLED at FULL (TEMPSCALE per-hypothesis killed v158; Mondrian conformal queued but NEVER RUN). Per the proactive drill cycle 188 Task 2 the recommendation is "close-or-reject" — version-staleness alone is structural evidence the row is not on a credible path.

**Field-coverage indication**: Two angles remain mathematically alive.
- **Conformal prediction (load-bearing, Gap C ✅)**: Mondrian/RC3P conformal stratified by anti-RM(1,16) coset (NOT RM(1,16) which was REFUTED at v152). Per meta-map Drill 3, P(deflated)=0.40 because the natural stratification basis was refuted; must use ANTI-coset modification.
- **ICA / JADE kappa_4 joint diagonalization (cross-domain probe #2 finding, medium-high)**: substrate's kappa_4 dichotomy could discriminate the K-hyp hypothesis subspace as independent components; this is a substrate-novel angle that was NOT in the v158 rescue list and surfaced only via the cross-domain probe.

**Concrete probe proposal** — `betT_mondrian_anti_RM_conformal_v1` (cheap close-or-reject) + IF KILLED `betT_JADE_kappa4_diagonalization_v1` (one final salvage).
- **Type**: Both Anchor experiments. First is ~10 min CPU (apply class-wise RC3P stratified by anti-RM coset to cycle-101 saved logits). Second is ~1 hr CPU (JADE on state-snapshot tensor).
- **Hypothesis**: (1) Per-coset coverage >= 1-alpha for all 4 anti-RM cosets at the cycle-101 logits → Bet T rescues from PARTIAL to ✅ via Mondrian. (2) If (1) fails, JADE kappa_4 diagonalization on the K-hyp logit tensor returns an algebraic basis that recovers min_acc >= 0.85.
- **Hard-fail**: (1) coverage fails for >= 1 coset → close Bet T at PROT-004/006 as the FINAL Mondrian rescue tried; (2) JADE returns degenerate kappa_4 (not full-rank) OR diagonalized acc < 0.75 → close Bet T cleanly.
- **Cost**: (1) ~10 min CPU. (2) ~1 hr CPU + ~1 day theory.

**Priority**: **MEDIUM**. Per [[feedback-strategy-shore-up-capabilities]] item 1, 🟡 rows must be drilled before scope expansion, but this row has been stale for 67 versions and the audit recommendation is close. Two clean shots remain (Mondrian + JADE) — both cheap CPU. After these the row closes per PROT-004/006 with a clear rescue-exhausted audit trail.

Adjacent: [[weakness-3]] (Bet V uses the same v158 routing letter).

---

## Weakness #3 — Bet V self-reflective: 65 versions stale at PARTIAL gap=0.424, framing structurally inconsistent

**The weakness**: PARTIAL gap=0.424 at largeN (cycle 103). 65 cap_map versions stale at v168. Per cycle 188 Task 2 honest assessment: a "self-reflective" claim implies gap of order epsilon; gap=0.424 is structurally inconsistent with the label. Closure framing pre-filed: "framing was over-promised at cycle 103".

**Field-coverage indication**: 
- **Free probability F4 (tier-1 from field advisor, yield 100%)**: free cumulants kappa_n of the stored-vs-unstored separation distribution. The v167 KAPPA_PROFILE_GROWS finding suggests substrate's higher cumulants carry algebraic structure invisible to mean/variance — gap=0.424 is a SECOND moment quantity; kappa_4-separation may show structure where gap doesn't.
- **NONE other clearly applicable**. Honest read: this is mathematically a closure candidate, not a rescue candidate. The cross-domain probes and meta-map adjacencies did not surface a strong self-reflective angle.

**Concrete probe proposal** — `betV_kappa4_separation_v1` (one final probe; if null, close).
- **Type**: Anchor experiment, ~30 min CPU.
- **Hypothesis**: kappa_4 of the stored-item logit distribution differs from kappa_4 of the unstored-item logit distribution by >= 2 SD at largeN, providing a higher-cumulant separation signal where the second-moment gap is too small.
- **Hard-fail**: kappa_4-separation < 1 SD → Bet V closes PROT-004/006 (final rescue tried). Filed sketches: (a) re-axiomatize as downstream conformal calibration; (b) absorb into v166 codeword-overlap KS-test row; (c) deprecate.
- **Cost**: ~30 min CPU.

**Priority**: **MEDIUM-LOW**. The honest reading per [[feedback-no-smoke]] is that Bet V is probably a closure not a rescue. Worth one cheap final probe because kappa_4 is genuinely a substrate-novel direction (per v167) the original cycle-103 metric didn't access, but realistic P(rescue) <= 0.25.

Adjacent: [[weakness-2]] (same v158 routing letter; both should close together if probes fail).

---

## Weakness #4 — Anti-RM(1,16) coset bias: substrate-physics row with MECHANISM UNKNOWN

**The weakness**: 0% within-linear-subcode overlap at v152 (REFUTED the RM(1,16) 25% prediction). Substrate-physics row labeled "mechanism unknown". Stale since cycle 145 per active_priorities. Per cycle 188 Task 2 Strategy explicitly recommended filing a Research routing request for a 2x mechanism drill; not yet done. This blocks the substrate-physics characterization narrative from sharpening — Pattern 6 says structural framings dominate the durable tier and the current label is non-structural.

**Field-coverage indication**:
- **QECC-Kerdock-MUB (cross-domain probe #2 STRONG)**: Kerdock 4-coset is provably isomorphic to a stabilizer-code MUB system; this gives a stabilizer-code-native vocabulary for the 0% anti-coset overlap finding (it is the *off-syndrome* condition of the Kerdock stabilizer code).
- **List-decoding / weight enumerators (cross-domain probe #2 WEAK but suggestive)**: anti-coset = the complement of the Kerdock code support; weight-enumerator methods on RM(1,16) complement give moment-style aggregate counts that should reproduce the 0%.
- **Free cumulants (tier-1)**: v166 codeword-overlap distribution is non-Gaussian (KS=0.259); the anti-coset bias likely lives in higher kappa_n of the overlap distribution. Pattern 7 cross-family consistency: anti-coset bias should also appear in v164a R-transform asymmetry.

**Concrete probe proposal** — `antiRM_mechanism_drill_v1` (Research drill, no compute).
- **Type**: Research drill (no compute) ~30 min. Generic-math framing per [[feedback-query-privacy-decomposition]]: "anti-coset bias in Kerdock 4-coset / RM(1,m) frame constructions" + "moment-based discriminators between coset and anti-coset subspaces" + "stabilizer code off-syndrome statistics on Z_4-linear Kerdock lifts".
- **Hypothesis**: The anti-RM(1,16) coset bias is a structural consequence of the Kerdock = Z_4-linear lift / unitary-2-design property (QECC-Kerdock probe finding) — the off-syndrome subspace of the Kerdock stabilizer code carries exactly the algebraic signature that produces 0% intra-subcode overlap.
- **Hard-fail**: Lit-scan finds either (a) a published explanation of anti-RM/anti-Kerdock bias in stabilizer-code complement subspaces — promotes the row's mechanism to a citable theorem — OR (b) no relevant lit + no clean substrate-internal kappa_n connection → close as "substrate-physics observable without mechanism narrative" and stop trying.
- **Cost**: ~30 min research-only.

**Priority**: **MEDIUM**. Pattern 6 says structural framings are the durable tier; the current "mechanism unknown" label is exactly the kind of non-structural row that drifts. This is a CHEAP research-only drill that either upgrades the row to theorem-anchored or closes it cleanly. Per [[feedback-dont-dismiss-adjacent-methods]] the QECC-Kerdock-MUB adjacency surfaced in probe #2 was flagged STRONG — dismissing it without dispatch is the dominant failure mode.

---

## Weakness #5 — Portfolio gap: NO generative-mode capability (substrate is read-only)

**The weakness**: Per cycle 188 Task 4 Gap #1, every capability in the v168 portfolio is a read/retrieve/infer-mode primitive. Cap 1 (erase), Cap 3 (inference), Cap 5 (online updates), Cap 7 (streaming), Cap 8 (readout), Cap 9 (multi-target), Cap 10 (continual edit), Cap 11 (observability). NO row anchors generative-mode behavior. This was flagged in v1 (year ago) and never moved. A customer asking "what does the substrate PRODUCE" gets "it doesn't produce; it retrieves" — a structural portfolio gap.

**Field-coverage indication**:
- **Drift-diffusion ≡ BP (load-bearing, Cap 3 anchor)**: meta-map adjacent D6 = Score-based diffusion model on substrate codewords. If substrate codewords admit a score function, score-based reverse-diffusion gives a NEW erase primitive AND a NEW generative primitive. ~3 days impl (largest cost in matrix); P=0.30 per advisor.
- **Drift-diffusion adjacents D1 / D2 (tier-1)**: Glauber dynamics on substrate codeword space (~1 hr CPU smoke); Metropolis-Hastings on W-perturbation space (~1 day theory + 1 hr CPU). Either gives a generative primitive (Glauber sampling from substrate Boltzmann; MCMC over W). Glauber is the cheaper probe.
- **Forward-flux sampling D7 (tier-1)**: rare-event sampling between substrate basins. Generative in the sense of "sample novel basin trajectories"; less customer-relevant.

**Concrete probe proposal** — `substrate_glauber_generative_smoke_v1` (CPU smoke, cheap dead-or-alive test).
- **Type**: Anchor experiment, ~1 hr CPU smoke per advisor D1.
- **Hypothesis**: Finite-T Glauber dynamics on substrate codeword space produces a NEW, valid codeword distribution distinct from the empirical training set — measured by (a) novelty rate (fraction of Glauber samples not in training set), (b) reconstruction quality of binding when Glauber-sampled codewords are used as keys, (c) cross-entropy vs training distribution.
- **Hard-fail**: Glauber samples either collapse to training set (novelty <= 5%) OR fail binding (reconstruction acc <= 0.20). Either closes generative-mode-via-Glauber.
- **Cost**: ~1 hr CPU.

**Priority**: **HIGH-strategic / MEDIUM-tactical**. This is the largest portfolio gap surfaced in the cycle 188 audit. Glauber smoke is the cheapest possible answer to "can the substrate generate?" If smoke passes, it opens a 12th capability axis (the first non-retrieve capability). If smoke fails, the portfolio is honestly characterized as RETRIEVAL-ONLY and the substrate-product story sharpens accordingly. Per Pattern 6 / [[feedback-dont-overextend-theorems]], either outcome is informative.

---

## Weakness #6 — Portfolio gap: NO failure-mode-observability anchor (Cap 11 is passive)

**The weakness**: Per cycle 188 Task 4 Gap #5, Cap 11 chi_4/Kovacs/avalanche are PASSIVE characterizations — "we CAN compute these primitives". There is no row anchoring PREDICTIVE observability — "chi_4 spike PRECEDES Cap 10 edit failure by N writes". Cap 2 closure (intrinsic confidence) was the substrate's failed intrinsic-confidence attempt; the failure-mode-observability anchor is the natural rescue framing per [[feedback-rehabilitation-after-rejection]] and explicitly named at cycle 188 Task 4 ("the natural candidate per v150 RS-cert anchor").

**Field-coverage indication**:
- **Observability suite (load-bearing, v166 + cycles 168-170)**: 4-family P(q) + C_ij + chi + dynamic. Pattern 7 cross-family consistency is the right gate.
- **Free probability F4 (tier-1)**: kappa_4 / kappa_n of per-write substrate state distribution. v164a R-transform deviation is N-stable and growing in n — could provide early-warning signature per write.
- **Cross-capability composition (cycle 188 Task 3 composition stories 1+3)**: composing Cap 11 with Cap 1, Cap 5, or Cap 10 in flight to test chi_4 / Kovacs as early-warning during ACTIVE-phase of host primitive.

**Concrete probe proposal** — `cap11_chi4_early_warning_during_cap10_v1` (composition probe).
- **Type**: Anchor experiment, ~45 min GPU per cycle 188 Task 1.
- **Hypothesis**: During Cap 10 continual-edit at M_init=8192 N=65536 (the validated operating point), chi_4 dynamic susceptibility traces show measurable spike (SNR >= 3 against quiescent baseline) BEFORE the substrate crosses the M/N=0.125 -> M/N=2 capacity boundary characterized in v155. If the chi_4 spike precedes the cap_10 failure by >= N_warning writes, this lands the failure-mode-observability anchor — the FIRST predictive (not passive) observability row.
- **Hard-fail**: chi_4 / Kovacs traces show no measurable signal (SNR < 3) during ANY of the three candidate host capabilities (Cap 1 / Cap 5 / Cap 10) — observability primitive is too noise-floor-limited to surface dynamics under host primitive active phase. Per cycle 188 Task 1 rescue ladder filed.
- **Cost**: ~45 min GPU per host primitive trace; 5 seeds; cheap envelope expansion not a new mechanism build.

**Priority**: **MEDIUM-HIGH**. Composition stories #1 and #3 of cycle 188 Task 3 are explicitly cross-capability strengthening; both compose mechanically without new mechanism builds. This converts Cap 11 from passive to predictive without engineering work. If it lands it directly resolves the "no failure-mode-observability anchor" gap and gives a substrate-product framing ("watch chi_4 spike DURING erase as the substrate transitions") that is fundamentally different from "we can compute chi_4".

Adjacent: [[weakness-1]] (Cap 2 rehab Rescue 3 chi_4-per-query is the per-cue version of this same idea).

---

## Weakness #7 — Engineering wall: Bet A continual-edit HARD-GATED at N>=16384 (build_initial_W OOM)

**The weakness**: Cap 10 ✅ at M_init=8192 N=65536 but HARD-GATED at N>=16384 since v156 due to `values.T @ keys` float32 matmul intermediate ~4.3 GB exceeding 8 GB VRAM. This is the ONLY ENGINEERING WALL in the portfolio (per [[feedback-negative-results-2x-research]] OOM-INCONCLUSIVE is explicitly EXCLUDED from Research 2x trigger). Three FULL OOM events on 2026-05-23 (v1/v2/v3). Per cycle 188 Task 2 this stays GATED until exp_dev refactors `build_initial_W`.

**Field-coverage indication**: NONE from Research perspective. **This is honestly NOT a research weakness — it is an engineering blocker.** Per [[feedback-no-smoke]] including this in the matrix is necessary for completeness but the answer is "not a research probe; an exp_dev refactor". The field-coverage map has nothing to add here — Pattern 1 (metric re-axiomatization) does not apply because the substrate WORKS at N<=8192; only scale-up is blocked.

**Concrete probe proposal** — NONE in research scope. Strategy logs the standing recommendation: `build_initial_W_bf16_matmul_refactor` (exp_dev work, ~1-2 days engineering). Alternative: chunked allocation along M axis. Either fix unblocks the entire N>=16384 sweep family.

**Priority**: **HIGH-engineering / N/A-research**. Including this row in the matrix per [[feedback-no-smoke]] brutal honesty — three OOM events in one day at N=32768 is a real bottleneck. But the matrix is "weaknesses paired with research probes" and the honest answer here is "no research probe applies; engineering must own this". Listed for completeness so the matrix isn't silent on the biggest scale-up blocker.

---

## Recommended sequencing — which 2-3 probes to ship FIRST

Per [[feedback-pipeline-pacing]] (CPU for explore, GPU for deep), [[feedback-dispatch-wrappers-default]] (queue depth >= 1), and the cheap-CPU bias in the v168 era:

**1. CPU slot — `cap2_conformal_subsumption_v1` (Weakness #1, HIGH)** as the FIRST dispatch.
- *Justification*: Pattern 1 (metric re-axiomatization is the highest-leverage cheap intervention) + this is the only PROVISIONAL ❌ closure in the portfolio with an unrun rehab + zero substrate change required. ~30 min CPU + theory. If it lands, Cap 2 returns to the portfolio as a rescued ✅ via Gap C subsumption — the cleanest possible portfolio move. The v160 rehab routing explicitly names Rescue 5 (this probe) as "FIRST in sequencing".

**2. CPU slot — `betT_mondrian_anti_RM_conformal_v1` (Weakness #2, MEDIUM) + `betV_kappa4_separation_v1` (Weakness #3, MEDIUM-LOW)** as a paired close-or-rescue dispatch.
- *Justification*: Both filed v158, both stale 56+/65+ versions, both cheap CPU (~10 + ~30 min). Per cycle 188 Task 2 the recommendation is close-or-reject; running both at once either rescues both (low probability) or closes both with a clear audit trail. Burns down two of the five named stale rows. Conformal angle for Bet T is field-advisor-Drill-3 endorsed.

**3. CPU slot — `substrate_glauber_generative_smoke_v1` (Weakness #5, HIGH-strategic)** as the THIRD dispatch.
- *Justification*: Largest portfolio gap (no generative-mode capability) + cheapest possible probe (~1 hr CPU smoke per advisor D1 tier-1). Either outcome is portfolio-shaping: if smoke passes → 12th capability axis opens; if smoke fails → portfolio honestly characterized as retrieval-only. Per [[feedback-dont-dismiss-adjacent-methods]] not running this is exactly the dominant failure mode.

**Honorable mention for GPU slot when one opens — `cap11_chi4_early_warning_during_cap10_v1` (Weakness #6)** at ~45 min GPU. Composition story; converts Cap 11 passive -> predictive without new mechanism builds.

**Honorable mention for parallel Research slot — `antiRM_mechanism_drill_v1` (Weakness #4)** at ~30 min research-only, no compute. QECC-Kerdock-MUB adjacency from cross-domain probe #2 STRONG.

**Skip for now**: `build_initial_W` refactor (Weakness #7) is exp_dev's; no research dispatch. Sequenced below the others because it does not improve substrate-product capability axes — it only widens N envelope on an already-✅ capability.

**Total cost for sequencing 1-3**: ~3 hr CPU. All three CPU-cheap, all three either close-or-rescue or portfolio-gap-shaping. Aligns with [[feedback-pipeline-pacing]] CPU-explore guidance and the cycle 188 active_priorities pipeline depth recommendation.

---

## Honest reading per [[feedback-no-smoke]]

- Weaknesses #1, #2, #3 are "we have the math, just haven't probed yet" — three concrete substrate-test dispatches each ~30 min CPU. Mathematical machinery (conformal, Mondrian, kappa_4) is load-bearing elsewhere in the portfolio.
- Weakness #5 (generative-mode) is "we don't actually have the math yet" — Glauber smoke is a dead-or-alive test; per Pattern 4 substrate may be too discrete-binary to support continuous-relaxation generative dynamics, in which case the gap is structural not probe-deficient.
- Weakness #4 (anti-RM mechanism) is split — QECC-Kerdock-MUB adjacency is mathematically there per cross-domain probe but no one has done the synthesis yet; this is genuinely "math missing" and a research drill is the right cost.
- Weakness #6 (failure-mode-observability) is "we have the math AND we have the primitives, just haven't composed them" — pure composition probe with no new mechanism build.
- Weakness #7 (build_initial_W OOM) is "we don't need research here at all" — engineering blocker, listed only for completeness per brutal-honesty rule.
