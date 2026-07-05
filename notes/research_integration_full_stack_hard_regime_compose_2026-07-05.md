# Research: are the brain components INTEGRATED at hard regime? (5x-drill angle 3/5)

Date: 2026-07-05. Owner: research (Opus synthesis over substrate scour + 3 parallel Sonnet lit-scans).
Question posed by USER directly: the 8 capabilities are each individually proven; the only end-to-end
loop test that passed was EASY-REGIME (single-hop, object-slot-only, symbolic). Does the substrate
actually COMPOSE 4+ real subsystems at HARD regime, or does it collapse the way independent per-stage
accuracies would predict if errors compounded multiplicatively/worse across the chain?

## HEADLINE

**The one seam that HAS been hard-regime-tested already answered half the question by accident, and the
answer is good news with a sharp caveat.** `exp_integration_end_to_end_loop_bridge_HARD_v2` (FULL, landed,
verified off-disk) is a 2-slot (subject+object), hub-crowded, multi-hop (hops=3, V=4096) composition test
of exactly ONE seam (reason -> generate), run under TWO bridge conditions that are, without anyone having
framed it this way, a direct test of "regenerative cleanup vs analog pass-through":

- **`naive_symbolic`** (argmax the noisy reasoning-output to its nearest KNOWN concept, then emit that
  concept's clean codeword) = a **regenerative relay**: subj_acc=0.939, obj_acc=0.861, end2end=**0.806**.
  0.939 x 0.861 = 0.808 -- **matches the observed end2end almost exactly.** No extra compounding penalty
  beyond naive per-slot independence.
- **`cotrained_linear`** (a learned linear map + per-bit sign, no concept-level snap) = an **analog
  repeater**: subj_acc=0.467, obj_acc=0.228, end2end=**0.10**. 0.467 x 0.228 = 0.106 -- again matches.
  Same near-independence, but each stage's OWN fidelity is much lower without the snap-to-known-code step,
  so the product collapses.

So: **regenerative cleanup at a seam does not eliminate degradation, but it does keep degradation
per-stage-independent rather than adding an extra "seam tax."** This is exactly the digital-repeater-vs-
analog-repeater distinction the user asked about, and it is already proven, not hypothesized -- but it is
proven for **one seam, two slots**. The never-tested question is whether this holds for a REAL 4+-subsystem
chain (comprehension's role-typing -> memory/reasoning's multi-hop retrieval -> a goal-conditioned control
gate -> generation), where (a) each additional hop is another chance for a *confidently wrong* attractor
convergence to poison everything downstream with no way to detect or backtrack, and (b) the control-gate
subsystem is ITSELF only proven at one depth (fair at depth-4, degrading by depth-6) -- so composing it
with reasoning's own depth-dependent degradation could interact in a way no isolated cell has measured.
Literature (3 lit-scans below) supports the general mechanism strongly but flags precisely this "hard
decision commits, no backtrack" hazard as the real risk, and **confirms nobody has published a benchmark
of chaining 3+ cleanup stages in series** -- this is a genuinely open question, not a foregone one.

## Cheap decisive test: `exp_integration_full_stack_hard_regime_v1` (spec; not dispatched)

**4 real, independently-proven subsystems, chained for the first time, at HARD regime, with the
anti-compounding mechanism (regenerative relay) as the primary experimental axis.**

### Stages (reusing proven primitives, no new mechanism invented)

1. **COMPREHEND** (role-typing / selectional restriction). Reuse
   `exp_comprehension_envelope_superposition_vocab_v1`'s content-conditioned block-assignment mechanism.
   Operating point: D=6, V=500 (MEASURED@same cell: order_content_exact_mean=1.000, parse_holds=true at this
   cell -- hard but not past the cliff). Assigns D_STORE real BGE fillers to their typed slots (subject-role
   vs relation-arg roles) BEFORE storage -- i.e. slot identity is no longer handed in clean, as it was in
   both integration v1 and HARD_v2 (their #1 scope limitation per the VET).
2. **STORE + REASON** (multi-hop, hub-crowded). Reuse `exp_integration_end_to_end_loop_bridge_HARD_v2`'s
   hard regime: V=4096, hops=3, D_store=10, near-neighbor hub cluster, real correlated BGE fillers, HRR
   circular-conv bind/unbind (`hdlab.binding`, the proven store/reason primitive). Consumes the COMPREHEND
   stage's typed output (not ground-truth slot labels).
3. **CONTROL-GATE** (goal-conditioned go/nogo). Reuse `exp_pfc_gate_cfrpe_trained_v2`'s RPE-trained Go/NoGo
   gate (PBWM/Frank-style; MEASURED@same cell: GONOGO=0.653, ADD=0.053, ORACLE=0.962 at the FAIR V1200/
   depth-4 operating point). The reasoning-recovered candidate must clear the gate against a per-trial goal
   vector before being allowed to reach generation; NOGO trials abstain (scored as a miss, not excluded).
4. **GENERATE** (bipolar-BSC / block-local decode). Reuse the HARD_v2 / `exp_generation_decoder_roundtrip_v1`
   decoder: gated candidate -> spoken 3-slot ordered proposition, decode-per-slot, exact-ordered scoring.

Phase-2 (not blocking): swap stage-0 ground-truth BGE rows for the live graded-GSBC encoder (v11/v12,
already ship-gate-passing) as a true PERCEIVE stage -- 5 subsystems. Flagged as follow-up; the 4-stage
version already answers the composition question the user asked and is cheaper to ship first.

### Arms (the anti-compounding axis -- orthogonal to the stage chain)

- **REGEN** ("thalamic-relay" arm): at every hand-off (comprehend->store, gate->generate; reason->generate
  already uses `naive_symbolic`-style snap per HARD_v2), snap the inter-stage signal to its nearest KNOWN
  discrete codeword (argmax-to-codebook / attractor cleanup) before the next stage consumes it.
- **ANALOG** (no-relay arm): pass the raw continuous/noisy inter-stage representation directly, mirroring
  `cotrained_linear`'s failure mode, at every hand-off.
- **STAGE-ORACLE isolation** (diagnostic, not a pass/fail arm): re-run each stage in isolation fed
  GROUND-TRUTH clean input (bypassing the previous stage's real output). Gives `PRODUCT_OF_STAGES` = the
  naive-independence prediction for the full chain, against which the REAL chained result is compared.
- **BROKEN** discriminator: sever identity at the reasoning hop (unbind by an unstored role, as in v1/
  HARD_v2) -> must collapse to chance.

### Metrics (the decisive numbers)

- `full_chain_end2end[arm]`: exact-ordered spoken triple == stored fact, per arm, per seed.
- `product_of_stages` = comprehend_acc(isolated) x reason_acc(isolated) x gate_GO_acc(isolated) x
  generate_acc(isolated) -- the naive-independence prediction.
- `compounding_ratio[arm]` = `full_chain_end2end[arm] / product_of_stages`. This is THE compounding
  diagnostic: ~1.0 means the chain behaves as independent multiplicative stages (matches the HARD_v2
  precedent); << 1 (e.g. <0.5) means a NEW emergent compounding penalty appears only when subsystems are
  genuinely chained -- the negative result the user is worried about, and one no pairwise seam test could
  have revealed.
- `wrong_attractor_rate[REGEN]`: fraction of trials where an intermediate cleanup step converges to a WRONG
  codeword with HIGH internal margin (glass-box-logged: cosine-to-committed-code minus cosine-to-second-best
  both above a confidence threshold, yet committed != ground truth). This operationalizes the "confident
  wrong attractor, no backtrack" failure mode literature flags as the sharp edge of hard-decision relays.

### Pre-registered bands (deflated per calibration-penalty discipline; P estimates below)

- **WIRING gate**: full-oracle chain (every stage fed ground truth) >= 0.85. Below this, the machinery
  itself is broken, not the composition question.
- **BROKEN_CEIL**: identity-severed discriminator <= chance-adjacent (~0.05).
- **HARD_PASS** (regenerative relay composes -- the optimistic, precedent-consistent outcome):
  `full_chain_end2end[REGEN] >= 0.35` AND `compounding_ratio[REGEN] >= 0.70` AND REGEN beats ANALOG by
  `>= 0.20` absolute AND cross-seed cv < 0.15. (0.35 floor is deflated from the naive product estimate of
  ~0.48-0.56 computed below -- see Cross-thread synthesis.)
- **HARD_FAIL** (genuinely negative -- integration itself, not any pairwise seam, is the wall):
  `full_chain_end2end[REGEN] < 0.25` **despite** `compounding_ratio[REGEN] < 0.50` -- i.e. even with
  cleanup at every seam, the real chain underperforms what independent per-stage multiplication would
  predict. This is the "0.7^4-style collapse survives the relay fix" finding -- the one that would mean a
  pairwise-relay mechanism is necessary but NOT sufficient, and something like a sustained cross-stage
  working-memory/thalamic context buffer (not just point-to-point relay) is the next lever.
- **MIDDLE_BAND**: `full_chain_end2end[REGEN]` in [0.25, 0.35) OR `compounding_ratio` in [0.50, 0.70) OR
  REGEN-ANALOG margin present but < 0.20 -- partial composition, quantify per-stage contribution.
- Cost: CPU-only, no new mechanism, comparable build/run cost to `exp_integration_end_to_end_loop_bridge_
  HARD_v2` (a few hours dev, minutes-to-low-hours CPU wall time). Not GPU-gated.

## Falsifiable predictions (P estimates, lit-scan calibration penalty applied: deflated 0.15-0.25, novel-
synthesis capped at 0.50)

1. **REGEN beats ANALOG at the full 4-stage chain, decisively.** P=0.80 (this is re-derivation from ALREADY
   LANDED FULL data at one seam, not novel synthesis -- not subject to the 0.50 cap; ANALOG's per-stage
   ceilings are so low without cleanup that near-zero end-to-end is close to certain regardless of chain
   depth).
2. **REGEN chain clears HARD_PASS (>=0.35, compounding_ratio>=0.70).** P=0.45 (novel-synthesis extrapolation
   from a naive per-stage product ~0.48-0.56 -- computed: comprehend 0.86-1.0 x reason-per-slot 0.86-0.94 x
   gate-GO 0.65 x generate-given-clean ~1.0 ~= 0.48-0.59 -- deflated into the 0.45 band per calibration
   penalty because the product assumes independence, which is exactly the assumption under test).
3. **A measurable `wrong_attractor_rate` > 0 exists and is the dominant error mode in the REGEN arm (more
   trials fail via confident-wrong-commit than via low-margin uncertain miss).** P=0.40 (this is the
   sharpest, least-tested claim; both the VSA lit-scan and the compounding lit-scan flag this as a real but
   *unbenchmarked-in-series* phenomenon -- capped at the novel-synthesis ceiling).
4. **HARD-FAIL scenario (compounding survives the relay fix) is NOT the outcome, but is a live enough risk
   to pre-register explicitly** -- P=0.20 that the full chain HARD_FAILs despite REGEN. This would be the
   most valuable possible negative: it would mean pairwise-relay is necessary-but-insufficient and motivate
   the thalamic-relay-as-SUSTAINED-buffer (not just point cleanup) build next.

## Cross-thread synthesis

**Within-substrate precedent (this session, already landed, re-read for this drill):**
- `exp_integration_end_to_end_loop_bridge_HARD_v2` (HARD_FAIL verdict as originally read, but VET-scoped as
  a POSITIVE glass-box finding: composition is "effectively symbolic," i.e. regenerative-cleanup-based, not
  a hidden learned bridge). Re-analysis here (new, not in the original cell or its VET): the two arms'
  per-slot accuracies multiply to match their observed end2end almost exactly (0.939x0.861=0.808 vs
  observed 0.806; 0.467x0.228=0.106 vs observed 0.10) -- meaning THIS seam shows NO super-multiplicative
  compounding penalty in either direction. That is new information this drill is banking: the "does it
  compound" question already has a partial, precise, quantitative answer at n=1 seam.
- `exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2` (HARD_PASS): regen holds ~0.69-0.74 through
  depth-5 where naive analog accumulation collapses -- SAME mechanism, different substrate location
  (within-reasoning hop-to-hop, not cross-subsystem). Confirms the regenerative-relay principle is not a
  one-off; it recurs wherever it's been tested inside this substrate.
- `exp_cortex_iterative_attractor_cleanup_depth_ceiling_v1` (HARD_FAIL, decisive negative): *iterating* the
  cleanup step does NOT extend usable depth beyond single-shot argmax -- the ceiling is COLLISION/capacity-
  bound (confirmed separately by `exp_reasoning_depth_keyslots_sharding_v1`, MIDDLE_BAND FULL, depth extends
  16-18+ only via MORE key-capacity/sharding, not more cleanup iterations). **This matters for the new
  cell**: regenerative cleanup fixes compounding-from-noise but does NOT fix compounding-from-capacity --
  if COMPREHEND's role-vocab or REASON's hub-crowded V exceeds the codebook's collision-free capacity at
  the chosen operating point, no amount of cleanup rescues it. The chosen hard-but-pre-cliff operating
  points above (D6/V500 comprehend; V4096/hops3 reason) were picked to sit inside each subsystem's own
  proven envelope for exactly this reason.
- `exp_pfc_gate_cfrpe_trained_v2` (HARD_PASS, VET-scoped PROVEN-AT-DEPTH-4): the control-gate subsystem
  itself degrades with depth (closure 0.661@d4 -> 0.075@d6 per the backup doc). This is a live risk the new
  cell must watch: if reasoning's own hop count interacts with the gate's depth-sensitivity, the two
  subsystems' individual weaknesses could compound in a way neither cell alone could show -- exactly the
  kind of interaction effect a real 4-subsystem chain (and only such a chain) can surface.
- Prior research note `research_integration_end_to_end_substrate_loop_2026-07-05.md` (this session, earlier)
  already found + cited thalamic-relay literature (Sherman & Guillery; Halassa & Kastner 2017) and the
  Hersche et al. (*Nat. Nanotech.* 2023) 16.22-point naive-vs-cotrained bridge gap. This drill extends that
  thread from "one seam, is a bridge needed" to "four subsystems, does the relay principle survive being
  chained."

**External literature (3 parallel Sonnet lit-scans, generic terms per query-privacy discipline):**

*Thalamocortical relay (confidence self-rated 0.55 by the scanning agent):* Sherman & Guillery's driver/
modulator framework and layer-6 corticothalamic gain control (*Cerebral Cortex* 2018) describe thalamic
relay as ACTIVE re-representation, not passive pass-through. Khona & Fiete (*Nat Rev Neurosci* 2022) give
the geometric reason attractor manifolds denoise: a noise ball in N dimensions projects onto a K-dim
attractor manifold with magnitude ~sqrt(K/N). Thalamic-lesion/diaschisis literature (multiple PMC/PubMed
sources on stroke, TBI, antisaccade error-monitoring) shows damage to relay/error-correction produces
CASCADING, not merely local, downstream dysfunction -- directly consistent with "removing the regenerative
step causes compounding degradation across a pathway." Caveat the agent flagged: most biological relay
cleanup is graded/continuous (line-attractor), not literally symbolic re-quantization -- the "digital
repeater" framing is an extrapolation, not a verbatim neuroscience finding.

*Attractor cleanup as inter-module interface (confidence 0.6):* this is a NAMED, established VSA pattern --
"clean-up memory" / "item memory" (Plate's HRR; Kanerva's spatter codes) and, more elaborately, Resonator
Networks (Frady, Kent, Olshausen & Sommer, *Neural Computation* 2020) which interleave VSA algebra with
attractor cleanup specifically to interface with a downstream module. Frady/Kleyko/Sommer (*Nat. Commun.*
2021) use a content-addressable memory as the interface between a controller and noisy analog hardware,
tolerant to >30% bit corruption at high dimensionality. Classical capacity result: ~0.14N patterns
(Amit-Gutfreund-Sompolinsky), with basin radius shrinking as load rises -- capacity/noise-tolerance is a
hard tradeoff, and directly relevant to why the operating points above were chosen inside each subsystem's
proven envelope. **Critically: the agent found NO paper that benchmarks CHAINING several cleanup stages in
series against chaining raw continuous interfaces** -- confirmed by the agent as an open/understudied
question. That is exactly this cell's contribution. Negative/caveat: spurious attractors and "silent"
confident-wrong convergence are explicitly documented (recent arXiv work on spurious overlaps) -- this is
the literature backing for the `wrong_attractor_rate` metric above.

*Compounding in chained pipelines (confidence 0.6):* the Data Processing Inequality is the information-
theoretic ceiling on cascaded processing. Exposure bias / the "snowball effect" in autoregressive
generation is the canonical ML instance of compounding. Ross & Bagnell's imitation-learning result is the
sharpest caveat found: naive behavioral cloning error grows QUADRATICALLY in horizon under covariate shift
(not merely multiplicatively) -- DAgger (retraining on the actual visited-state distribution) reduces this
to linear. This means compounding CAN be worse than the naive product-of-stages model assumes, specifically
when an early stage's errors shift what the next stage sees away from its own training distribution --
relevant here because COMPREHEND's typed output, when wrong, feeds REASON a distribution of inputs unlike
anything `exp_deep_reasoning_hub_robustness_v1` was tuned against. The digital-repeater-vs-analog-repeater
distinction is confirmed as TEXTBOOK-established telecom theory (not an analogy -- a real, quantified
result): analog repeaters compound noise multiplicatively/exponentially with hop count; digital repeaters
keep end-to-end error near the SINGLE WORST hop. Sharp counter-example the agent surfaced: decode-and-
forward relaying can produce CATASTROPHIC error propagation (worse than amplify-and-forward's graceful
degradation) when hop SNR is poor, because one bad hard decision corrupts the entire downstream message
with no graceful fallback -- this is the same "confident wrong commit, no backtrack" hazard from the second
lit-scan, converging from an independent literature.

**Convergent verdict across all 3 scans + the within-substrate precedent:** the regenerative-relay /
thalamic-relay framing is real and well-supported in its GENERAL form, but two caveats recur independently
across neuroscience, VSA, and information theory: (1) it is capacity/basin-bound (matches this substrate's
own collision-bound reasoning-depth finding exactly), and (2) it converts graceful average-case degradation
into a rarer but harder-to-detect worst-case failure mode (confident wrong commitment, no backtrack) --
and nobody has published a direct study of what happens when 3+ such relays are chained in series. This
substrate is positioned to be the first place that gets measured.

## Substrate-product implications

- **The compounding fear ("each ~0.7 -> 0.7^4 collapse") is NOT the substrate's actual failure mode when
  cleanup is present at seams** -- the one seam tested shows near-independent multiplicative degradation,
  bounded by each stage's own (already-known, already-improvable) fidelity, not by an extra "seam tax."
  That is a genuinely good, product-relevant finding: it means each subsystem's OWN accuracy is the lever to
  pull (perception's retrieval gap, reasoning's collision-bound depth, control's depth-degradation), not
  some emergent, un-attackable "integration tax."
- **But the glass-box value proposition (inspectable, auditable, "we can tell you why") is threatened
  specifically by the confident-wrong-attractor failure mode, not by graceful degradation.** A system that
  fails gracefully (lower confidence, detectable near-misses) is a very different product risk than one
  that fails by confidently committing to a plausible-but-wrong answer and propagating it silently. The
  `wrong_attractor_rate` metric this cell introduces is directly a trust/auditability metric, not just a
  research curiosity -- it should become a standing instrumented quantity any time a relay/cleanup step is
  used in a shipped pipeline.
- **The control-gate's own depth-degradation (proven-at-depth-4, degrading by depth-6) is a compounding risk
  multiplier that exists BEFORE any cross-subsystem chaining is even considered** -- fixing/extending
  control's depth-robustness (already flagged as an open envelope-push in the backup doc) directly de-risks
  the full-stack integration test's HARD_PASS odds, independent of whether the relay mechanism itself works.

## Verdict: is integration the #1 next thrust?

**HIGH priority, not automatically #1, but the best next FULL-regime cell to ship in the current wave.**
Reasoning: (1) the mechanism question ("does a relay prevent compounding") already has a decisive, cheap,
already-landed partial answer -- re-testing it in isolation would be low-value; (2) the SPECIFIC gap (does
it hold at 4+ chained subsystems, and does a new confident-wrong-cascade failure mode appear that no
pairwise test can see) is genuinely untested and cheap to test (CPU-only, reuses 4 already-proven
primitives, no new mechanism); (3) it directly serves the glass-box positioning (auditability is the
product thesis, and the specific risk it tests -- silent confident-wrong propagation -- is the one failure
mode that most undermines that thesis if unmeasured); (4) it is NOT more urgent than closing perception's
still-open co-measurement gap or the generalization one-to-many ceiling (those are individual-capability
gaps with their own live levers), but it IS more urgent than further pairwise-seam drilling, because the
marginal information from one more pairwise test is now low (the mechanism recurs consistently every time
it's been checked) while the marginal information from the first genuine multi-subsystem chain is high
(literature explicitly flags this as unstudied). Recommend: hdi_exp_dev authors + smokes
`exp_integration_full_stack_hard_regime_v1` per the spec above in the next wave; cost is comparable to
HARD_v2 (a cell that already shipped this session).

## Citations (verified count: 11 named sources across 3 independent lit-scans + within-substrate cells)

External (verified real by the scanning agents; 2 flagged by the agents themselves as recalled-with-
uncertainty, marked below):
1. Sherman & Guillery, driver/modulator thalamic relay framework; layer-6 corticothalamic gain control,
   *Cerebral Cortex* 2018 ("Focal Gain Control of Thalamic Visual Receptive Fields by Layer 6 Corticothalamic
   Feedback").
2. Halassa/Mukherjee, "associative thalamus" mediodorsal error/uncertainty decomposition -- agent flagged
   citation as recalled-but-not-fully-certain.
3. Khona & Fiete, "Attractor and integrator networks in the brain," *Nat Rev Neurosci* 2022.
4. Thalamic-lesion/diaschisis literature (stroke connectional diaschisis PMC12459977 2024; antisaccade
   error-monitoring degradation, Seifert et al., PubMed 21731771; amnesic diaschisis, PubMed 17419833; TBI
   thalamocortical disruption, ScienceDirect 2022).
5. Plate, *Holographic Reduced Representations* (clean-up/item memory).
6. Kanerva, spatter codes (clean-up memory).
7. Frady, Kent, Olshausen & Sommer, Resonator Networks, *Neural Computation* 2020.
8. Frady, Kleyko & Sommer, "Robust high-dimensional memory-augmented neural networks," *Nat. Commun.* 2021.
9. Amit-Gutfreund-Sompolinsky, classical Hopfield capacity result (~0.14N).
10. Ross & Bagnell, DAgger / quadratic-horizon imitation-learning compounding result.
11. Digital-repeater-vs-analog-repeater telecom theory (textbook-established, no single paper).
Plus within-substrate: `exp_integration_end_to_end_loop_bridge_v1`/`HARD_v2` metrics.json (re-analyzed
here), `exp_cortex_regenerative_cleanup_vs_analog_accumulate_v2`, `exp_cortex_iterative_attractor_cleanup_
depth_ceiling_v1`, `exp_reasoning_depth_keyslots_sharding_v1`, `exp_pfc_gate_cfrpe_trained_v2`,
`exp_comprehension_envelope_superposition_vocab_v1` (all verified off-disk, metrics.json read directly).
Prior research note `research_integration_end_to_end_substrate_loop_2026-07-05.md` (Hersche et al. *Nat.
Nanotech.* 2023 16.22-pt bridge-gap citation carried forward, not re-verified here).
