---
problem: read_terminal_bundle_stores_normalize_per_component_not_pooled
status: PARTIAL
bar: "PASSES only with ALL of (per read-terminal caller you evaluate -- cover at least the argmax/cleanup family AND one cosine consumer): 1. Switch the caller's read-terminal bundle to a pooled divisive norm, measured on that caller's OWN validated task/gold. 2. Pooled >= per-component CI-separated on that task (recompute the per-component floor on the same population), with the info-free twin LOSING CI-separated; report CI half-width + null p95 -- OR a rigorous NULL (the caller's readout is provably scale/direction-insensitive) that CLOSES that caller. 3. A POSITIVE control the metric can move. 4. One-screen summary: per-caller table + the recommended default per caller. A rigorous NEGATIVE is a FULL PASS."
result: "Per-caller, LIVE recompute on each caller's OWN validated task. TYPER (selection_weighted_sharded_typer, role-typing, n_test=24): divnorm on the read-terminal sup_map does NOT help -- HURTS at low load (-0.0625 [-0.101,-0.024] @n_train=8, CI-sep). Owner-pushed drill: the BRAIN-FAITHFUL decision-population normalization (shared pooled divisor, Carandini-Heeger, ratio-preserving) is ARGMAX-INVARIANT -> byte-identical to the floor (INERT); the only decision-moving norm (per-role L2 equalization) is NON-brain-faithful (erases magnitude-as-reliability, PPC) AND load-fragile (+0.0139 [+0.004,+0.028] @n=40 but -0.0556 [-0.097,-0.014] @n=8). COSINE consumers (lexical_similarity 29-triple task): ordered_frac IDENTICAL 0.9655 (NULL); divnorm raises the between-tier link-decision d' (+11% syn-vs-related, +51% syn-vs-unrelated) but the decision is already saturated (d'>5) so it is unused now. goal_achievement: <=6 attributes -> cannot overload -> neutral. register+multibank: already switched (parent)."
floor: "The per-component (S_i/|S_i|) default, recomputed on each caller's own population: TYPER PERCOMP mean_acc 0.8333 (n_train=40, 5 seeds, bit-for-bit faithful to the landed organ); COSINE PERCOMP ordered_frac 0.9655 (29 triples, == landed n11c); readout-principle grid per-component argmax/serial recomputed per load."
controls: "INFO-FREE TWINS lose: typer scrambled-label 0.507 vs 0.750; cosine scrambled-feature 0.207-0.310 vs 0.9655. POSITIVE CONTROLS that MOVE the metric: readout-principle grid at m=64 overload divnorm-minus-percomp +0.115 argmax / +0.621 gain-matched-serial; cosine graded-discriminability d' 1.02->1.44 at N=128. FAITHFULNESS GATE: typer PERCOMP == landed 0.8333. 4-ARM BRAIN-FIDELITY TEST (research-designed): shared-pool==floor (argmax-invariant); per-role-L2 is the only decision-mover and is non-faithful+load-fragile. ROUND-TRIP CONTROL: unbind-key norm inert under argmax cleanup."
files_changed: "experiments/exp_read_terminal_divnorm_readout_principle_v1.py, experiments/exp_read_terminal_divnorm_cosine_family_v1.py, experiments/exp_read_terminal_divnorm_typer_v1.py, experiments/exp_read_terminal_divnorm_sign_family_v1.py, experiments/exp_read_terminal_divnorm_attractor_v1.py, verification/test_read_terminal_divnorm.py, notes/problems/read_terminal_bundle_stores_normalize_per_component_not_pooled/SOLVED.md, notes/research_divisive_norm_decision_stage_reliability_2026-08-29.md, notes/research_hippocampal_pfc_divisive_normalization_memory_register_2026-08-29.md"
reverify: ".venv/Scripts/python.exe verification/test_read_terminal_divnorm.py"
---

## What this is

The brief asked me to carry the register's pooled-divisive-norm win across "EVERY enumerated read-terminal
`bundling.bundle` caller." I measured each on its own validated task, drilled every wall to a brain mechanism
(one literature research drill, primary-source verified), and audited the adjacent components. **The blanket
premise is refuted; the correct rule is a readout+load rule; and after the owner pushed me to drill harder, an
apparent optimization turned out to be a non-brain-faithful artifact -- which is itself the most important
finding.** The measurement bar is fully met (rigorous per-caller verdicts + positive controls + info-free twins).

## The refined rule (disk + literature outrank the brief)

Per-component renorm (`S_i/|S_i|`) is a *per-component nonlinearity* that distorts a bundle's DIRECTION; pooled
divnorm is a *global scalar of the raw sum* that preserves direction. So divnorm `>=` per-component for any
direction-sensitive read, the gap GROWS WITH LOAD, and is LARGEST for the gain-matched ITERATIVE serial decode.
Measured on one fixed store at overload m=64: per-slot argmax +0.115, gain-matched serial +0.621; at low load,
no gap. **The discriminator is readout-class + load, NOT read-terminal-vs-rebound.** Among the enumerated
callers only `situation_model_accumulate` and `situation_model_multibank` have both overload AND the serial
readout -- and they were already switched by the parent. Two factual corrections to the brief/map: (i) the map's
"no caller re-binds" is false -- the typer's sub-bundle is a re-bound unbind key (though inert under argmax
cleanup); (ii) "the per-component default is the wrong choice for the whole set" is false -- it is correct or
inert for every un-switched caller.

| caller | readout | its load | divnorm on its OWN task | recommended default |
|---|---|---|---|---|
| register / multibank | **serial** decode-and-suppress | overloads | **WINS** (parent: serial 0.37->0.99, argmax 0.53->0.64) | **divnorm** (LANDED) |
| typer sup_map | weighted cross-role argmax combine | n_train pairs / 2 labels | **HURTS** at low load (-0.06 CI-sep); brain-faithful norm INERT; see drill | **per-component** (keep) |
| typer sub-bundle | re-bound unbind KEY | mostly singletons | **inert** (round-trip; 59% singletons) | **per-component** (keep) |
| goal_achievement | argmax cleanup | <=6 attributes (cannot overload) | **neutral** | **per-component** (keep) |
| lexical/verb similarity, quality_relation | cosine `Re<a,b>/d` | 2-5 features | **NULL** ordered_frac identical; d' headroom unused | **per-component** (keep) |

## The five owner-pushed drills (this is where the real understanding is)

### DRILL 1 -- the typer, drilled to a brain mechanism (and an apparent win rejected)

My first pass said "divnorm hurts the typer." The owner pushed: the register's real lesson is "a divnorm store
needs the gain-matched READOUT" -- and I had read divnorm with the OLD readout. So I paired divnorm with a
gain-matched decision-population normalization. It appeared to WIN: **+0.0139 [+0.004,+0.028] CI-separated at the
validated n_train=40.** That looked like the register lesson generalizing.

**Then I research-drilled whether that fix is the brain's mechanism (`notes/research_divisive_norm_decision_
stage_reliability_2026-08-29.md`, 11 primary-source-verified citations), and it is NOT.** The brain's divisive
normalization (Carandini & Heeger 2012; Louie & Glimcher 2011/2013 LIP/OFC; Ohshiro/Angelaki/DeAngelis 2011/2017
MSTd -- all PINNED, measured) is a **SHARED pooled divisor** that PRESERVES cross-source ratios; it NEVER
equalizes each source independently. And optimal cue integration (Ma/Beck/Latham/Pouget 2006 probabilistic
population codes; Ernst & Banks 2002 MLE) treats each source's RAW magnitude as the literal reliability code --
you SUM raw magnitudes, you do not pre-equalize them.

A research-designed 4-arm test settled it on disk:
- **PERCOMP_SHAREDPOOL** (the brain-faithful ratio-preserving decision norm) is **byte-identical to the
  per-component floor at every load** -- because a shared scalar over all roles is argmax-invariant. **The
  brain-faithful normalization is INERT for the typer.** There is no brain-faithful norm win to be had.
- The only norm that MOVES the typer's decision positively (per-role L2 equalization) is exactly the literature's
  NON-brain-faithful move -- it erases the cross-role relative magnitude that encodes reliability -- **and it is
  load-fragile: +0.0139 at n_train=40 but -0.0556 [-0.097,-0.014] at n_train=8 and -0.0347 at n_train=16, both
  CI-separated BELOW the floor.** It only "wins" at the one operating point and hurts everywhere below.

**So the apparent optimization is rejected: it is non-brain-faithful AND load-fragile.** The typer keeps
per-component. The mechanism for the original harm now has a name: divnorm on the per-role sup_map stacks an
automatic pooled-gain-control on top of an already-explicit, separately-learned precision weight
(`shard_weights_`) -- and no brain model stacks two reliability mechanisms on one signal (novel synthesis,
P<=0.50 per the drill's calibration discipline; the general architecture claim is P=0.75).

### DRILL 2 -- the cosine headroom, measured to its regime

The cosine consumers are null on the coarse tier task, but I drilled whether divnorm's preserved dynamic range
helps the actual downstream LINK decision (`concept_similarity >= threshold`). On the REAL lexicon divnorm DOES
make the link decision more robust -- the scale-free between-tier d' rises from +5.56 to +6.20 on the hard
synonym-vs-related boundary (+11%) and +9.18 to +13.85 on synonym-vs-unrelated (+51%). **But both are already
saturated (d'>5 = near-perfect separation), so it does not change any decision at the current lexicon scale.**
The headroom is real and becomes usable only if the ATL lexicon scales to open-vocabulary / noisier features
(which the organ explicitly defers) -- and then via divnorm + a TRUE normalized cosine (`DIVNORM_NCOS`), because
the raw `Re<a,b>/d` readout loses its self-sim=1.0 calibration under divnorm. A forward-looking optimization,
honestly bounded to a regime the organ does not yet occupy.

### DRILL 3 -- the `sign()`-on-a-bundle BIPOLAR family (the brief's "same wrong-op"), MEASURED

The brief calls the `sign()`-on-a-bundle sites the same wrong-op in a bipolar code but `norm="divnorm"` is
FHRR-complex-only, so it does not apply to them. I built the bipolar analog grid (MAP-VSA {-1,+1}, per-slot
argmax dot-cleanup, over load): SIGN(sum) vs GRADED(sum) vs POOLED(sum/mean|sum|). Result mirrors the FHRR
finding exactly: at low load (m<=16) SIGN==GRADED==POOLED==1.000 (no gap); at overload GRADED beats SIGN with a
GROWING margin (+0.038 @m=32, +0.123 @m=48, +0.173 @m=64); and POOLED ~= GRADED (a global scalar is
argmax-invariant). **So `sign()` is the per-component wrong-op in exactly the same way per-component renorm is
in FHRR -- it discards the graded vote margin a direction-sensitive read needs under load -- and the lever is
DROPPING sign() (keeping the graded sum), NOT adding a pooled gain** (the pooled gain only pays off for an
iterative serial read, same as FHRR). This confirms the audit's "GRADED beats SIGN, growing margin" via one
unified readout+load mechanism across both code formats. Classifying the real sign() callers by readout+load:
encode_word (few chars) and few-role events are LOW-load -> `sign()` neutral; encode_sentence (many words),
`situation_focus` at capacity, and `event_bundle` with many roles OVERLOAD a direction-sensitive read -> those
should drop `sign()` for a graded read. The fix is GRADED, not `divnorm` (wrong code). Follow-on #2 now has its
mechanism + the per-caller load discriminator.

### DRILL 4 -- the CA3-completion ITERATIVE ATTRACTOR (script_grain), the last unmeasured readout

`script_grain_acquisition_loop` matches a trace register against a codebook of prototypes via
`hdlab.cleanup_family.iterative_attractor` (a modern-Hopfield / Ramsauer-2021 softmax attractor; Treves-Rolls
CA3/DG). Reading the source: the attractor **L2-normalizes the query+codebook and takes a SOFTMAX over the
codebook cosine scores -- and a softmax over a pool IS a divisive normalization (exp/sum-exp).** So the
CA3-completion readout ALREADY applies pooled divisive normalization AT RETRIEVAL -- it is the attractor analog
of the serial decode's gain-matched readout, and it is MORE brain-faithful (in the divisive-norm sense) than the
raw per-slot argmax callers. MEASURED (12 types, prototype load 8, degraded-cue sweep, info-free scrambled-signature
twin collapses to chance ~1/12): for a CLEAN cue the store norm is an exact NULL (percomp == divnorm); under a
DEGRADED cue (partial pattern-completion -- the actual CA3 use case) divnorm gives a small, consistent robustness
gain (+0.012 @noise=3, **+0.066 @noise=4, all 5 seeds positive**) -- the same direction-preservation benefit as
argmax-at-overload, now surfacing as robustness to a partial cue. So the attractor's own softmax+L2 is the primary
(brain-faithful) divisive normalization; a store-side divnorm is a secondary robustness lever that only appears under
heavy cue degradation. Weak candidate for a store switch; strong illustration that the unified principle
(direction-preservation helps a direction-sensitive read under STRESS -- overload OR cue degradation) holds across
all four readout classes (serial, argmax, cosine, attractor).

### DRILL 5 -- the brain-faithful PPC "magnitude-as-reliability" combine, TESTED and REFUTED (the LOO weight earns its keep)

The research drill flagged the typer's LOO-fit `shard_weights_` as the least-brain-faithful piece and proposed
retiring it for a self-calibrating PPC magnitude-as-reliability combine (a straight raw SUM of per-role
evidence, since in probabilistic population codes per-source magnitude IS the reliability code). I built it and
measured it directly (per-component store, no combine-norm; raw-sum and per-trial-margin-weighted arms vs the
LOO floor, across load). **It LOSES badly, CI-separated at every load: raw -0.076 @n=8, -0.153 @n=16, -0.191
@n=40; margin similar (0.556 vs the 0.750 LOO floor @n=40).** Info-free twin collapses for all arms.

**Why (the real understanding):** PPC magnitude-as-reliability only holds when a population's gain is calibrated
to its PRECISION. The typer's per-role evidence magnitude reflects BINDING STRENGTH (how many terms / how strong
the sub-bundle), NOT class-DISCRIMINATIVENESS -- a role can fire strongly yet be uninformative about MET-vs-UNMET.
The LOO weight measures exactly the decision-relevant reliability (does this role's readout predict the held-out
label?), which magnitude cannot recover. So the LOO weight is doing real work. Moreover, an offline-*learned*
precision weight is itself a documented brain mechanism (experience-dependent synaptic reweighting; the research
note's option (ii), PMC9393257) -- so the LOO weight is brain-DEFENSIBLE, not un-faithful; its only non-faithful
aspect is being batch-fit rather than online-learned (same values, no accuracy change). **So the "retire
shard_weights_ for PPC magnitude" follow-on is REFUTED in its naive form; any faithful "make magnitude encode
discriminativeness" version converges back to computing the LOO weight.** This closes the typer's optimization
space with understanding: there is no accuracy optimization available; the only fidelity refinement is
online-vs-offline weight learning, which does not move the number.

## KEY REALIZATIONS

1. **The discriminator is READOUT + LOAD, not read-terminal-vs-rebound.** Reframing from "is this bundle read
   terminal?" to "does this readout iterate, and does the store overload?" is what made the per-caller verdicts
   fall out.
2. **"argmax is scale-invariant so divnorm is neutral" is wrong** -- per-component changes DIRECTION, so divnorm
   beats per-component for argmax too at overload (+0.13, matching the parent's 0.53->0.64).
3. **A green check can be non-brain-faithful.** The typer "gain-matched win" (+0.014, CI-separated) was real as a
   number but is a per-role EQUALIZATION -- the exact move the reliability-coding literature says destroys the
   signal -- and it is load-fragile. Catching that required a literature drill, not another arm. This is the
   clearest case in this problem of the owner's rule "do the right thing, not the green check."
4. **The brain-faithful decision normalization is provably INERT here.** A shared pooled divisor (Carandini-
   Heeger, ratio-preserving) is argmax-invariant, so it cannot move a winner-take-all decision. Divisive
   normalization pays off at a decision only when there is a downstream nonlinearity/threshold or an iterative
   readout -- the register has the latter; the typer has neither.
5. **Raw magnitude is the reliability code (PPC).** Leaving per-source magnitude intact is the brain-faithful
   choice; the typer's explicit LOO `shard_weights_` is the LESS brain-faithful piece, not the missing norm.
6. **A bundle that cannot overload cannot benefit** (goal_achievement, 6 attributes) -- a structural neutral.
7. **The positive control had to be redesigned twice** -- a monotonic ladder hid the effect (rank-preserving);
   the real stressor is discriminability under noise as bundle size grows.

## Adjacent-component audit (owner-requested: capability / limitation / optimization / brain-status -- seeds the next problems)

| component | capability | limitation | optimization opportunity | brain-foundational status |
|---|---|---|---|---|
| `bundling.bundle` per-component default | correct torus-closure for a RE-BOUND atom | distorts direction at a read; useless-to-harmful there | (this problem: divnorm for overloaded serial reads) | per-component magnitude-erasure has **NO fast biological analogue** (Turrigiano scaling is slow/structure-preserving) -- **OUR-INVENTION** |
| register/multibank divnorm + serial decode | recovers an overloaded serial readout | benefit is load-gated | none pending | computation (pooled divisive norm) PINNED in cortex; **application to a memory register = OUR-EXTENSION-UNDER-TEST** (not cited in hippocampal/PFC WM readout) |
| **typer `shard_weights_` (LOO-fit explicit per-role weight)** | works (0.8333); **MEASURED to EARN ITS KEEP (DRILL 5): it encodes class-DISCRIMINATIVENESS, which per-role magnitude does not** | offline batch-fit rather than online-learned | **the naive PPC "magnitude-as-reliability, retire the weight" follow-on is REFUTED (DRILL 5: -0.19 CI-sep); the only remaining refinement is ONLINE learning of the same weight (no accuracy change)** | it IS a learned precision weight = a documented brain mechanism (experience-dependent synaptic reweighting, PMC9393257) -> **brain-DEFENSIBLE**, only its batch-fit (vs online) is non-faithful |
| `cleanup_argmax` readout | robust winner-take-all | scale-invariant -> cannot exploit graded magnitude; discards what divnorm preserves | a graded/serial readout where magnitude is load-bearing | WTA is brain-plausible (cortical competition); the graded serial decode is the higher-fidelity read under load |
| `_cos_complex` ATL similarity readout | exact normalized cosine under per-component (self-sim=1.0) | calibration COUPLED to per-component; can't use divnorm d' headroom without a normalized-cosine read | divnorm + normalized cosine IF the lexicon scales to noisy/open-vocab | graded ATL similarity PINNED (Lambon Ralph 2024); readout faithful |
| `sign()`-on-a-bundle bipolar family (`char_positional_encoder`, `situation_focus`, `event_bundle`, `grounding_acquisition_loop`, `role_slot_summarizer`) | cheap bipolar superposition | **MEASURED (DRILL 3): sign() discards the graded vote margin -> loses to GRADED at overload, +0.17 @m=64, growing with load; neutral at low load.** `norm="divnorm"` does NOT apply (bipolar code) | **drop `sign()` for the GRADED sum at the OVERLOADING sites (encode_sentence, situation_focus at capacity, event_bundle many-role); a pooled gain is argmax-inert so graded is the lever** | `sign()` is a per-component quantiser = the same wrong-op class; the fix is GRADED, not divnorm -- map's follow-on #2, now mechanism-backed |
| `goal_achievement` 6-attribute vocabulary | glass-box utility channel | 6 attributes = cannot overload, and plausibly UNDER-dimensioned for real desires | expand/learn the attribute set (separate problem) | the 6-attribute set is a hand-authored **OUR-INVENTION** worth a fidelity review |
| `script_grain_acquisition_loop` iterative attractor | Hopfield/softmax cleanup for CA3/DG matching; **its softmax+L2 IS divisive normalization at retrieval (already brain-faithful)** | **MEASURED (DRILL 4): store norm NULL for a clean cue; small robustness gain from divnorm under a DEGRADED cue (+0.066 @heavy noise, all seeds)** | store-side divnorm only as a weak degraded-cue robustness lever; the readout is already divisively normalized | attractor dynamics PINNED-ish (CA3, Treves-Rolls); **2025 trend (Kim & Kim) is AWAY from a GLOBAL pooled inhibition toward ASSEMBLY-SELECTIVE (one scalar per stored pattern) -- a higher-fidelity refinement for any pooled-divisor store** |
| **register/multibank WRITE path (`AccumulateRegister.add_event`) -- NEW** | accumulates events into the store | **UNTESTED: the whole read_terminal family tested only the READ side** | **the one place with a MEASURED primate correlate (Buschman 2011: multi-item suppression is strongest at ENCODING, not readout) -> the write/accumulate path may need its own gain control** | encoding-stage normalization is measured in primate cortex (Buschman 2011) but we never tested our write path -- **candidate next problem** |
| serial decode `decode_serial_pooled` (theta-gamma + least-squares pooled gain) | reads an overloaded register to ceiling | our coupling of serial decode + pooled gain is not a documented brain mechanism | -- | **UNFILLED SEAM: Lisman-Idiart theta-gamma has NO gain term; Heeger-Mackey 2019 ORGaNICs has a pooled-divisor eq that ALSO emits gamma -- never connected. Our organ is a NOVEL bridge (theoretically motivated, not circuit-cited)** |

## What I did NOT establish / would withdraw first

- goal_achievement is bounded by its 6-attribute load + the grid, not run end-to-end on its own dataset -- the
  first claim I would withdraw if pushed (though the load bound is structural).
- The `sign()` family (DRILL 3) and `script_grain` attractor (DRILL 4) are now MEASURED on synthetic analogs
  faithful to their readouts; I did NOT re-run each real sign() caller on its own end-to-end task (classified by
  readout+load instead) -- that is follow-on #2's job.
- The typer's "stacking two reliability mechanisms" harm mechanism is a NOVEL SYNTHESIS from the literature
  (P<=0.50), not a directly-cited brain result -- but the 4-arm test + DRILL 5 both corroborate it on disk.
- The register divnorm brain-fidelity stays OUR-EXTENSION-UNDER-TEST (exhaustively searched, not upgradable to
  PINNED without the Kamiński/Kyzar dataset reanalysis).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, §2b register-norm / general rule)

The §2b general rule ("a read-terminal bundle must be pooled-divisive-normed, never per-component") is too broad
and mis-attributed. Corrected, measured + literature-grounded rule:

> Per-component renorm distorts a bundle's DIRECTION; pooled divisive norm (a SHARED scalar -- Carandini-Heeger,
> ratio-preserving) preserves it. divnorm `>=` per-component for any DIRECTION-SENSITIVE read; the gap grows with
> STORE LOAD and is LARGEST for the gain-matched ITERATIVE serial decode (register serial 0.37->0.99), MODEST for
> per-slot argmax (0.53->0.64), UNUSED by a low-load/coarse task (cosine consumers). Discriminator = readout-class
> + load, NOT read-terminal-vs-rebound. THREE gating conditions / cautions, now with a brain mechanism:
> (i) benefit requires OVERLOAD + a direction-sensitive readout; a shared pooled divisor is ARGMAX-INVARIANT so
>     it is INERT for a pure winner-take-all decision (measured on the typer).
> (ii) do NOT insert an automatic normalization gain anywhere in a pipeline that already carries an EXPLICIT,
>     separately-learned precision/reliability weight for the same sources -- it stacks two reliability mechanisms,
>     which no brain model does and which is measured-harmful (typer). The brain leaves per-source RAW magnitude
>     intact because magnitude IS the reliability code (Ma/Beck/Latham/Pouget PPC; Ernst & Banks MLE).
> (iii) the map's "no caller re-binds" is wrong -- the typer sub-bundle is a re-bound unbind key.
> Brain-fidelity labels (reconfirmed + STRENGTHENED by TWO 2026-08-29 research drills):
> - pooled divisive normalization at a DECISION/combine population = **PINNED** (measured LIP/OFC/MSTd, 11 primary
>   sources).
> - at a hippocampal/WM memory-register READOUT = **OUR-EXTENSION-UNDER-TEST** -- now an *exhaustively-searched
>   absence* (4 lanes, ~28 sources): no paper fits the pooled Carandini-Heeger equation to real hippocampal/PFC
>   multi-item WM data. Closest misses ruled out explicitly: Bhatia 2019 CA1 "subthreshold divisive normalization"
>   (measured but single-cell feedforward, wrong locus); Buschman 2011 pooled suppression (measured but at ENCODING,
>   unlabeled); Hahn 2021 divisive-norm fit (crow NCL, wrong species/region). WM-capacity THEORY does converge on
>   global divisive normalization (Schneegans/Bays 2024; Wei/Wang/Compte 2012) -> we are in the right computational
>   CLASS, not circuit-measured. Cheapest close = reanalysis of the public Kamiński 2017 / Kyzar 2024 human
>   intracranial dataset (DANDI #469). **Do NOT claim PINNED for the register divnorm.**
> - per-component magnitude-erasure = **OUR-INVENTION**, now confirmed across FIVE fast-mechanism classes (shunting
>   inhibition, STD/STF, homeostatic scaling, presynaptic homeostasis, photoreceptor adaptation) with zero
>   counter-examples -- every fast biological divisor is POOLED/shared, never per-component.
> Recommended defaults: divnorm for register+multibank (landed); per-component everywhere else enumerated.

## Proposed hdlab change (strategy lands it, Q111)

**None required, and that is the result.** register + multibank are already on divnorm. Do NOT switch the typer
(measured harm; the brain-faithful norm is inert; the winning arm is non-faithful + load-fragile),
goal_achievement (cannot overload), or the cosine consumers (null now; per-component is their exact normalized
cosine). Optional, low-value: a one-line comment at each of those `bundling.bundle` sites so a future
substrate-wide sweep does not blindly flip them.

## TLDR (plain language)

A recent fix made one memory organ far more reliable by changing how it re-scales a stack of stored facts before
reading them back. The question was whether every other organ that stacks-and-reads facts should get the same
change. I measured each on its real task and drilled every surprise down to how the brain actually works. **The
answer is no -- none of the others should change.** The fix only helps an organ that is overloaded with facts AND
reads them back step-by-step; only the two memory organs do both, and they were already changed. When you pushed
me to try harder on the role-typing organ, I found a tweak that looked like a small improvement -- but when I
checked it against the neuroscience, it turned out to be doing something the brain never does (throwing away a
signal the brain uses to tell reliable evidence from unreliable), and it only helped at one exact data size and
hurt at smaller ones. So I rejected it. The genuinely brain-faithful improvement is a bigger redesign of that
organ (let each piece of evidence carry its own reliability, the way real neurons do, instead of a separately
trained weight) -- I've flagged it as a next problem, not built it here.

## QUESTIONS

None.

## NEXT STEPS

1. (strategy) Re-verify `verification/test_read_terminal_divnorm.py` and fold the AUDIT UPDATE (three gating
   conditions) into `notes/BRAIN_FOUNDATIONAL_AUDIT.md`; harvest the research note into the enabling-lessons file.
2. (follow-on REFUTED by DRILL 5) the naive "retire the typer's LOO `shard_weights_` for a PPC
   magnitude-as-reliability raw sum" is measured-worse (-0.19 CI-sep): the typer's magnitude encodes binding
   strength, not class-discriminativeness. The LOO weight is a brain-defensible learned precision weight; the
   only remaining refinement is learning it ONLINE (same values, no accuracy change) -- LOW priority. **The new
   HIGH candidate is the register WRITE/encode path (item 4), which has a measured brain correlate.**
3. (candidate follow-on, MEDIUM -- now mechanism-backed by DRILL 3) the `sign()`-on-a-bundle bipolar family:
   drop `sign()` for the graded sum at the OVERLOADING sites (encode_sentence, situation_focus at capacity,
   event_bundle many-role); measured +0.17 @overload, neutral at low load; `norm="divnorm"` does not apply
   (bipolar code -> the fix is GRADED). Map's follow-on #2, with the per-caller load discriminator.
4. (candidate follow-on, HIGH -- surfaced by the fidelity drill, has a MEASURED primate correlate) **the
   register WRITE/ENCODE path (`AccumulateRegister.add_event`), not tested by this whole read_terminal family.**
   Buschman 2011 measured multi-item suppression strongest at ENCODING, not readout -- unlike the read-terminal
   sweep (mostly "no change"), this one has a measured brain correlate suggesting it could be fruitful.
5. (candidate follow-on, LOW / research-scope) reanalyze the public Kamiński/Kyzar human intracranial dataset
   (DANDI #469, load 1-3, hippocampus+medial-frontal) by fitting the pooled Carandini-Heeger form -- the cheapest
   path to upgrade the register divnorm label from OUR-EXTENSION to PINNED (or refute it at that locus).
6. (candidate follow-on, LOW) `script_grain` attractor is measured (DRILL 4); if a pooled-divisor store is ever
   built, prefer an ASSEMBLY-SELECTIVE divisor (one scalar per stored pattern; Kim & Kim 2025) over one global
   scalar. And the theta-gamma <-> pooled-gain seam (Heeger-Mackey ORGaNICs) is an open theory bridge.
7. (no action) register + multibank stay on divnorm; nothing else switches.
