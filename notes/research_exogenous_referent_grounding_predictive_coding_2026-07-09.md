# Research: The minimal exogenous-referent grounding mechanism for a self-contained substrate — predictive coding, sensorimotor contingency, categorical-perception grounded kernels, and the causal intervention screen

Filed by: research (Sonnet). Date: 2026-07-09.

**Process note on this delivery:** 4 parallel Sonnet lit-scan sub-agents were dispatched on (1) predictive
coding/active inference as exogenous grounding, (2) sensorimotor contingency/enactivism, (3) Harnad
categorical-perception grounded-kernel + transitive spread, (4) causal representation learning
intervention/held-out screens — generic academic terms only, no substrate-novel names exposed, per
`[[feedback-query-privacy-decomposition]]`. A first pass of this note was drafted from on-disk context plus
direct knowledge before the sub-agents' live results landed (per instruction not to block/poll); all 4 have
since returned with live-verified web findings and this revision integrates them. Two corrections of note
versus the first-pass draft, in the interest of not overclaiming: (1) the data-processing-inequality argument
for why a closed loop cannot manufacture exogenous grounding is NOT established doctrine in the classical
Friston/Rao-Ballard/Harnad literature — it is a reasonable synthesis, best DIRECTLY supported by a thin,
very recent (2026), not-yet-replicated ML/self-play literature (Pu et al. arXiv:2605.22217), with the
DPI-for-closed-systems math itself solid but its application to symbol grounding specifically an inference,
not a cited theorem; (2) the strongest, best-cited, most direct literature finding this cycle is actually a
DIFFERENT one than the DPI argument — Pezzulo, Parr, Cisek, Clark & Friston (2023, *Trends in Cognitive
Sciences*) explicitly argue passive prediction-error minimization is INSUFFICIENT for "genuine understanding"
and that active, embodied intervention is the load-bearing ingredient — this is now the headline finding of
S1/S3 below, promoted above the DPI framing.

**Trigger / on-disk grounding (verified via Read, not hallucinated, per Fix#28):** the dentate-gyrus
upstream-decorrelation cell (`B1+PS`, pre-registered in
`notes/research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md`) landed FULL and produced exactly its
own pre-registered **HARD-FAIL case (a)**: `DG_XFIT corr(failmask) = 0.377` against a HARD-FAIL threshold of
`>= 0.35` (no material improvement over the disjoint-data-alone `B1` baseline of `~0.39`; measured lift only
`+0.015`, under any usable margin), while grounding held at `0.589` (comfortably above that note's `>= 0.50`
floor, so this is not a case-(b) over-aggressive-sparsification failure — the representation stayed
semantically intact, it simply did not decorrelate further). Per that note's own pre-registered S3 fork, this
HARD-FAIL is diagnostic, not a dead end: it distinguishes "blind spot lives in the shared representation/coding
transform" (case a, now REFUTED — a representation-level fix was tried and did not move the needle) from
"blind spot lives in the shared training signal/distribution both branches ultimately chase" (not yet tried).
Verdict, as pre-registered: **REPRESENTATION_INSUFFICIENT_REDIRECT_EXOGENOUS.** This is the third confirmed
internal-only grounding negative this program has produced (settling HF, differentiation HF, now DG HF) —
together they constitute a strong, convergent, non-cherry-picked empirical case that a purely-internal,
purely-symbolic substrate cannot manufacture referential grounding from itself, and needs a genuinely
exogenous referent (real, non-symbolic data as "the world," not an external model).

Also load-bearing from same-day on-disk work (read before dispatch):
`notes/research_prediction_error_native_learning_signal_grounding_link_2026-07-09.md` already scoped a
buildable `W_pred` second-matrix predictive-coding learning axis (reusing existing
`hdlab/predictive_coding.py` `residual_magnitude`/`proportional_gate` precision-weighting primitives) and
already named, as its own lowest-confidence but most cross-thread-relevant Falsifiable Prediction (P=0.25),
exactly the mechanism this drill is now asked to specify in full: prediction-error against real ingest data,
wired as a **shared reconstruction target both self-play branches must independently hit**, tested against the
`corr(failmask)` screen. `notes/research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md` established
that transitive grounding-spread (Harnad's mechanism, operationally) already HARD-PASSED on this substrate
(near d1=0.63, far d3=0.48, monotone decay 0.146, scrambled-grounding control flat) but caps at 1 hop absent
iterative settling or compositional binding.
`notes/research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md` Prediction C already
specified the causal/held-out perturbation screen this drill's S2 calls for: perturbing a real grounded
feature must shift the representation `>=2x` more than perturbing a matched relation-only feature (P=0.40).

---

## HEADLINE

**Four literatures converge on real-data prediction as the load-bearing exogenous anchor, but the live-verified
findings sharpen (and partly correct) the mechanism-level story: the cleanest, best-cited, most DIRECT result
this cycle is not a formal closed-loop-cannot-bootstrap-reference proof — no such theorem exists in the
classical canon — it is Pezzulo, Parr, Cisek, Clark & Friston's (2023, *Trends in Cognitive Sciences*) explicit
argument that PASSIVE prediction-error minimization is insufficient for "genuine understanding," and that
ACTIVE, embodied intervention on the world (not just prediction of it) is what does the grounding work,
because only an acting agent can "constantly put its best models to the test." This is reinforced from a
second, independent direction by Coelho Mollo & Millière's (2023) "Vector Grounding Problem," which argues
referential grounding needs BOTH a causal-informational relation to the world AND a teleosemantic
selectional-history condition — prediction-error minimization against real data satisfies at best the first,
not the second. The "closed loop cannot manufacture exogenous information" intuition IS independently
supported, but by a thinner, much more recent thread: a single 2026 ML/self-play paper (Pu et al.,
arXiv:2605.22217) explicitly distinguishes externally-sourced data-gating (exogenous) from internally-generated,
even cross-branch-decorrelated reward grounding (endogenous), and states directly that "decorrelated components
within the same training loop can share fundamental error modes" — a close, direct hit on this program's own
DG HARD-FAIL, but flagged low-medium confidence (single paper, unreplicated, 2026). Sensorimotor
contingency/enactivism turns out to be a LIVE, UNSETTLED dispute rather than settled doctrine: O'Regan & Noe's
own tradition claims the closed action-loop is necessary, but the field's own empirical record (passive-movement
adaptation studies, passively-transported-kitten depth-avoidance) undercuts strict necessity — good news for a
passive-prediction design, but not a clean pass. Harnad's categorical-perception mechanism gets a genuinely
strong, QUANTITATIVE anchor this cycle: Vincent-Lamarre et al. (2016) show a grounding kernel of only ~1% of a
full dictionary's vocabulary (a "MinSet," ~15% of a ~10%-of-dictionary "Kernel") suffices to reach the entire
remaining vocabulary by pure symbolic composition/definition-chaining — and Greco & Caneva's (2010) robotic
study shows 9 elementary grounded motor-symbols compositionally covering 18 patterns generalize to 51%
novel-composition naming accuracy (vs 29-46% for non-compositional controls) — concrete calibration numbers
for "how small can the grounded seed be and how well does transitive spread work" that the first-pass draft
lacked. A newer, contested paper (Shahid & Rothe 2026, arXiv:2604.26521) directly challenges Harnad's
transitive-sufficiency claim, arguing grounding measurably decays with compositional distance — independently
converging with this substrate's OWN already-measured decay curve (0.146/hop). Causal representation learning
supplies the fourth piece — the measurable TEST — but the live scan found the bridge from CRL identifiability
theory to Harnad-sense symbol grounding is "thin/indirect... promising synthesis, not settled research," so
this note treats CRL as a verification tool this program is applying novelly, not an established equivalence.**

**P_deflated (predict-real-ingest-data supplies a genuine, structurally distinct exogenous anchor that breaks
the closed-loop blind-spot ceiling, at the mechanism level): 0.45** (revised down slightly from the 0.50 cap
used in the first-pass draft, now that live verification shows the strongest DIRECT support for the specific
"exogeneity beats internal decorrelation" claim comes from one thin, unreplicated 2026 paper rather than
established doctrine — the substrate's own DG HARD-FAIL remains real, direct, on-disk confirmatory evidence
independent of that paper, which is why this stays close to, not far below, the cap).

---

## S1 — The brain's exogenous-referent grounding mechanism(s), and which is load-bearing

| Mechanism | What it does | Load-bearing status |
|---|---|---|
| **Predictive coding / active inference** (Rao & Ballard 1999; Friston 2010 free-energy principle; Clark 2013/2015 "surfing uncertainty"; Hohwy 2013) | Minimizes prediction error between top-down generative model and bottom-up sensory signal caused by the real world. The residual is informative specifically because the sensory cause is exogenous — a physical process outside the model's own generative loop. | **PRIMARY / load-bearing.** This is the minimal common mechanism underlying the other three; the other three are variants or consumers of it, not alternatives. |
| **Sensorimotor contingency theory / enactivism** (O'Regan & Noe 2001; Laflaquiere/O'Regan/Gas/Terekhov 2018 arXiv:1806.02739; Held & Hein classic; SEP "Action-based Theories of Perception" 2025 ed.) | Grounding = "practical mastery" of the lawful structure governing how sensory input changes as a function of self-generated action — a regularity DISCOVERED via a closed action-perception loop. | **Secondary, and — per live verification — an UNSETTLED, contested claim, not established doctrine.** The theory's own text treats action-loop mastery as necessary-not-sufficient (a conjunctive condition with raw sensory stimulation), and the field's own empirical record undercuts strict necessity: passive-movement optical-rearrangement adaptation and passively-transported-kitten depth-avoidance both occurred without active reafference in some paradigms (SEP, citing counter-evidence to Held & Hein). This is genuinely double-edged for a passive-prediction substrate design: it means passive-only prediction is not automatically disqualified by orthodox SMCT, but it also means no consensus "minimal sufficient condition" exists anywhere in this literature to appeal to (explicitly flagged an "open research area" by Pak, arXiv:1810.01870). |
| **Harnad categorical-perception symbol grounding** (Harnad 1990 *Physica D*; Harnad 1987 *Categorical Perception*; Vincent-Lamarre et al. 2016 *Topics in Cog. Sci.* / arXiv:1411.0129; Greco & Caneva 2010 *Front. Neurorobotics*; Shahid & Rothe 2026 arXiv:2604.26521) | A small set of elementary symbols are grounded via NON-SYMBOLIC categorical-perception discrimination of real sensory input at a learned category boundary; everything else inherits grounding TRANSITIVELY through pure symbolic composition — no further perceptual contact required for the bulk of the vocabulary. | **Tertiary — the MINIMAL-KERNEL special case, now with a genuinely quantitative anchor.** Vincent-Lamarre et al.'s dictionary-graph analysis found a "MinSet" of only ~1% of a full dictionary's vocabulary (~15% of a larger ~10%-of-dictionary "Kernel") suffices to transitively define/reach the ENTIRE remaining vocabulary — the strongest available "how small can the grounded seed be" number in the literature (symbolic/graph-theoretic demonstration, not itself a sensorimotor test). Greco & Caneva's robotic instantiation (9 elementary grounded motor-symbols, 18 compositional patterns) reached 51% novel-composition naming accuracy transitively, vs 29-46% for non-compositional controls — real but FAR FROM PERFECT generalization, a useful calibration ceiling. A newer, contested 2026 paper (Shahid & Rothe) directly challenges pure transitive-sufficiency, arguing grounding decays with compositional distance — converging independently with this substrate's OWN already-measured decay curve (0.146/hop, grounding-cascade note). |
| **Causal representation learning intervention screen** (Scholkopf et al. 2021 arXiv:2102.11107; Ahuja et al. 2023 arXiv:2209.11924; Squires/Seigal/Bhate/Uhler 2023; Geiger et al. 2022/2024 arXiv:2303.02536 — Distributed Alignment Search / Interchange Intervention Accuracy; Veitch et al. 2021 arXiv:2106.00545) | Formalizes WHEN a representation can be proven to track true causal factors: under PERFECT interventions, latents are identifiable up to permutation/scaling (Ahuja et al.); for the linear-Gaussian case a single intervention per latent is necessary+sufficient (Squires et al.), with newer work reducing this to O(log n) unknown multi-node interventions with finite-sample bounds. The actual empirical protocol used in practice is "interchange intervention" / Interchange Intervention Accuracy (Geiger et al.'s DAS) — patch in another input's representation at a hypothesized causal-variable location and measure whether the output changes to match — reported as a continuous fidelity score, NOT gated at a universal numeric threshold. | **Not a grounding-manufacturing mechanism — the VERIFICATION mechanism, and its bridge to Harnad-sense grounding is explicitly "thin/indirect" per live verification** ("promising synthesis... not settled research" — no paper found that formally equates CRL identifiability with solving the symbol grounding problem). This program's use of it (Prediction C, `>=2x` differential-sensitivity requirement) is itself a novel application of the CRL protocol to this exact question, not an established transfer. |

**Why predictive coding specifically plausibly breaks the ceiling internal decorrelation cannot (honest framing
after live verification):** the DG fix (`B1+PS`) applied a fixed, independently-seeded,
sparse-expansion-plus-competitive-sparsification transform to the SHARED representation before splitting it
per branch — a purely internal, deterministic function of data that was itself entirely self-generated within
the loop. The intuitive argument is a data-processing-inequality one: no transform applied downstream of a
signal can increase that signal's mutual information with anything it never carried information about upstream.
**This intuition is well-supported by solid, general information theory (directed-DPI-for-feedback-systems,
arXiv:2103.13591; closed-systems boundary-information formalization, arXiv:2311.10786) but its SPECIFIC
application to symbol grounding is this program's own synthesis, not a cited theorem in the classical
Friston/Rao-Ballard/Harnad canon** (confirmed absent across all 4 live lit-scans). The closest DIRECT literature
hit is a single, very recent (2026), unreplicated ML/self-play paper (Pu, Weng, Liu et al., "Survive or
Collapse," arXiv:2605.22217) which explicitly distinguishes externally-sourced data-gating (exogenous) from
internally-generated reward-grounding (endogenous, even if cross-branch-decorrelated) and states directly that
"decorrelated components within the same training loop can share fundamental error modes" — this is a strong,
on-topic match to the DG HARD-FAIL's own diagnostic fork, but should be treated as suggestive corroboration
from a thin source, not a proof. The substrate's OWN on-disk evidence remains the strongest single data point:
`B1+PS` DID partially decorrelate the two branches from EACH OTHER (`corr` moved from a naive-mirror baseline
down through B1's cross-fit to `0.377`) but — exactly as its own pre-registered fork predicted for case (a) —
failed to move the needle further, consistent with (though not proof of) the ceiling being distribution/
objective-level rather than representation-level. Real ingest data, being caused by a process outside the loop,
remains the best-motivated candidate for breaking that ceiling — but this note now holds that claim at
P=0.45 (revised down from the initial 0.50 cap) specifically because the direct literature support turned out
thinner than the first-pass draft assumed.

---

## S2 — Minimal buildable design for this substrate

**The grounded seed (Harnad's elementary-symbol layer, predictive-coding-instantiated):** a small kernel of
atoms is grounded not by symbolic composition but by direct, non-symbolic prediction/reconstruction of real
ingest data at those atoms — concretely, the already-scoped `W_pred` dedicated weight matrix
(`research_prediction_error_native_learning_signal_grounding_link_2026-07-09.md` S2), reusing
`predictive_coding.py`'s `residual_magnitude`/`proportional_gate` precision-weighting machinery unchanged,
writing a precision-weighted update driven by the mismatch between predicted-next-real-token and
actually-observed-next-real-token. This is the substrate-native analog of categorical-perception discrimination:
the write strength is concentrated on genuinely novel/surprising real transitions (Harnad's category-boundary
warping, restated as a continuous precision-weighted gate rather than a hard boundary).

**Transitive spread (already validated, reuse don't rebuild) — now with external quantitative calibration:**
the grounding-cascade note's already-HARD-PASSED transitive-inheritance mechanism (near d1=0.63, far d3=0.48,
decay 0.146) IS the spread mechanism — grounded seed atoms propagate their grounding to the rest of the
vocabulary via the existing relational-graph readout, with the same note's two named depth-extension levers
(iterative/recurrent settling; compositional bind-then-unbind chaining) available to extend reach beyond 1 hop
when needed. No new architecture required for a first cut — this piece of S2 is a reuse instruction, not a new
build. **Live-verified external calibration for "how small a seed / how far can it reach":** Vincent-Lamarre
et al. (2016) found that in a real dictionary-definition graph, a "MinSet" of only ~1% of the full vocabulary
(a feedback-vertex-set subset of a larger ~10%-of-dictionary "Kernel") suffices to transitively define the
ENTIRE remaining vocabulary by pure symbolic composition — i.e., this substrate's `W_pred` seed kernel does not
need to be large to plausibly reach broad coverage, IF the compositional/definitional graph has similar
connectivity structure to a natural-language dictionary (untested assumption, flagged). Greco & Caneva's (2010)
robotic instantiation (9 grounded elementary motor-symbols compositionally covering 18 patterns) is a more
sobering ceiling: novel-composition accuracy topped out at 51% (vs 29-46% non-compositional controls) — real,
significant, but far from perfect. Combined with Shahid & Rothe's (2026, contested) direct claim that grounding
decays with compositional distance, the honest expectation for a `W_pred`-sourced kernel is: broad transitive
REACH is plausible (dictionary-graph precedent), but transitive ACCURACY should be expected to degrade with
hop-distance (robotic precedent + this substrate's own already-measured 0.146/hop decay + the contested 2026
critique) — not a clean, lossless spread.

**Causal/held-out screen (already specified, reuse don't rebuild):** Prediction C
(`research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md`) is precisely the causal
representation learning intervention screen this literature calls for: perturb a REAL grounded feature (a
seed atom's actual predicted/reconstructed ingest-data target) and require the representational shift to
exceed the shift from perturbing a matched relation-only (non-exogenous) feature by `>=2x`. This is the
concrete, already-pre-registered operationalization of "grounding verified, not just claimed."

**Composition with the differentiated self-play — does prediction-error-against-data BE the shared exogenous
ground?** Yes, and this is not a new proposal invented by this drill — it is the exact fallback the DG note's
own S3 fork named in advance, now the live path since case (a) fired as predicted. The concrete wiring
(already specified as the lowest-confidence, most-consequential Falsifiable Prediction row of the
prediction-error note): apply prediction-error against real ingest data as a **shared reconstruction target**
that BOTH the Speaker and Listener self-play branches must independently reconstruct/predict correctly,
trusting agreement only where both branches' independent predictions of the SAME real external target concur.
Because the target is real and exogenous, this instantiates differentiation axis 1 (disjoint/exogenous data,
the only axis proven `rho=0` by construction, per the self-play differentiation-axis taxonomy) directly at the
objective/distribution level rather than at the representation level — exactly the level the DG HARD-FAIL
identified as the actual site of the blind spot. This composes cleanly with, rather than replaces, the existing
disjoint-data cross-fit (B1): B1 splits WHICH data each branch sees; the exogenous-prediction-target addition
constrains WHAT BOTH branches are ultimately being checked against, closing the loophole (Thread 2 of the DG
note, and the efference-copy/schizophrenia calibration case in
`research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md`) where two branches can be
internally decorrelated yet both converge on the same self-consistent-but-wrong answer (folie a deux) because
neither is ever checked against anything outside the loop.

**Concrete cell (extends B1, no new cell architecture):** `B1+EXOG` — disjoint-data cross-fit (B1, unchanged)
+ a shared, real-ingest-data prediction target both branches must independently reconstruct via the `W_pred`
mechanism above, with agreement/disagreement on that real target substituted for (or added to) the
`corr(failmask)` screen already instrumented for B1/B1+PS.

---

## S3 — Honest bound and the sharpest residual question

**Does this give FULL referential grounding, or a stronger-but-still-partial anchor?** The live-verified
literature answer is even more clear-cut than the first-pass draft suggested: **a stronger-but-still-partial
anchor, not full referential grounding**, now for THREE independently-sourced reasons (one upgraded by live
verification from a plausible extrapolation to a directly-cited, well-published claim):

1. **Passive prediction is explicitly, directly argued insufficient by the field's own leading authors —
   this is now the single best-cited finding of the whole drill.** Pezzulo, Parr, Cisek, Clark & Friston (2023,
   *Trends in Cognitive Sciences*) — Friston himself among the authors — argue living systems are
   "inextricably anchored to the body and world" specifically because they must capture and control the
   SENSORY CONSEQUENCES OF ACTION, which lets them "constantly put their best models to the test" in a way
   passive generative AI cannot; they state this active testing is "essential to the development of genuine
   understanding." This is a direct, high-confidence, peer-reviewed statement from within the active-inference
   field itself that passive prediction (this note's S2 design) does not cross the full grounding threshold.
2. **A second, independent condition is also unmet: teleosemantic function, not just causal-informational
   contact.** Coelho Mollo & Millière (2023, "The Vector Grounding Problem," arXiv:2304.01481) argue referential
   grounding requires BOTH (i) an appropriate causal-informational relation to the world AND (ii) a
   selectional/functional history that gives the representation the FUNCTION of carrying that information.
   Prediction-error minimization against real data plausibly satisfies (i) — this is exactly what `W_pred`
   would supply — but says nothing about (ii), which this substrate has no mechanism for at all. This sharpens
   "partial anchor" into a precise, two-part bound rather than a vague hedge.
3. **The sensorimotor/enactivist bar is itself unsettled (see S1), which cuts both ways.** Passive-only design
   is not automatically disqualified by orthodox SMCT (the field's own action-necessity claim has documented
   counter-evidence), but neither is there a consensus minimal-sufficient condition to appeal to for a passive
   design to claim victory against.
4. **The already-on-disk "epistemic parasitism" critique (Bender & Koller 2020; Bisk et al. 2020) stands
   unchanged** — a corpus is a record of experience, not experience itself.

**What genuinely changes as a result of this drill's synthesis:** the DG HARD-FAIL is not merely "another
negative" — it is the third confirmatory data point (with settling HF and differentiation HF) for a specific,
now well-triangulated structural claim: **closed internal loops cannot manufacture the SPECIFIC kind of
grounding that requires genuine external mutual information, no matter how well-decorrelated their internal
parts are — but they CAN, and per this substrate's own already-landed evidence (grounding-cascade HARD-PASS,
Spoke1 v2 predictive-only arm outscoring hybrid) DO successfully consume and propagate exogenous information
once it is present.** The bound is therefore precise: prediction-against-real-data supplies genuine,
verifiable (via Prediction C), STRUCTURAL grounding sufficient to break the specific closed-loop blind spot
this program has now confirmed three times — but it does not, on the weight of the literature, constitute the
full referential/embodied grounding the strongest philosophical bar (Harnad's complete symbol grounding
problem, sensorimotor mastery) demands. This is a genuine, product-relevant advance (a real anchor, not a
placebo), correctly bounded (not oversold as "solved").

**Sharpest residual question (now with live-verified specificity):** the causal-representation-learning
identifiability literature is explicit and quantitative that provable recovery of true causal factors
generally requires INTERVENTIONS, not passive observation alone — Ahuja et al. (2023) show perfect
interventions give identifiability up to permutation/scaling; Squires, Seigal, Bhate & Uhler (2023) show that
for the linear-Gaussian case a SINGLE intervention per latent variable is both necessary and sufficient (missing
even one leaves that factor's identity unresolvable); very recent work (arXiv:2406.05937, arXiv:2603.25796)
reduces the budget further to O(log n) unknown multi-node interventions with finite-sample guarantees. Does
this substrate's ingest data supply enough NATURAL environment-diversity/quasi-interventional structure
(different real sources, different real conditions) to approximate this, or is the current ingest stream
effectively a single static environment with zero interventions — in which case prediction-error-against-it,
however genuinely exogenous, may still leave the learned representation under-identified in the CRL sense, even
if it is information-genuine in the weaker "real data, not self-generated" sense above? The live-verified
protocol for testing this directly is interchange-intervention accuracy (Geiger et al.'s DAS): patch another
real input's representation state into a hypothesized grounded-atom location and measure whether output
tracks the swap — a more rigorous version of Prediction C's perturbation screen, reported as a continuous
fidelity score rather than a fixed pass/fail cutoff (no universal threshold exists in this literature; this
program should set its own via held-out validation, not import an external number). This is a DIFFERENT
failure mode than the one just confirmed (identifiability/uniqueness, not exogeneity/information-content) and
is the natural next drill if `B1+EXOG` HARD-PASSes but a follow-up probe finds the grounded representation
unstable across resampling of the same static corpus.

**Deflated P estimates (capped at 0.50, calibration penalty applied, revised post-live-verification):**
- P(predict-real-ingest-data supplies a genuine, structurally distinct exogenous anchor at the mechanism
  level): **0.45** (revised down from the initial 0.50 cap — live verification found the strongest direct
  literature support is one thin, unreplicated 2026 paper rather than classical doctrine; the substrate's own
  DG HARD-FAIL remains real, direct, on-disk confirmatory evidence independent of that paper).
- P(`B1+EXOG`, wiring prediction-error-against-real-ingest-data as a shared reconstruction target for both
  self-play branches, HARD-PASSES `corr(failmask) <= 0.30` with grounding `>= 0.50` intact — the pre-registered
  number already carried from the prediction-error note): **0.25** (unchanged from that note's own figure;
  this is the single most consequential number in this note, and it was set BEFORE knowing the DG HARD-FAIL
  would land, so it is not post-hoc-inflated).
- P(this constitutes FULL Harnad-sense referential/embodied grounding, not a partial structural anchor):
  **0.12** (revised down slightly from 0.15 — live verification found a direct, well-cited, peer-reviewed
  statement (Pezzulo et al. 2023, Friston co-author) that passive prediction is explicitly insufficient for
  "genuine understanding," plus a second independent necessary-condition gap (Coelho Mollo & Millière's
  teleosemantic/functional-history requirement) that this design has no mechanism for at all — sharper,
  better-sourced grounds for a low number than the first-pass draft had).
- P(passive ingest-data prediction alone satisfies causal-representation-learning identifiability conditions
  without additional environment-diversity/interventional structure): **0.20** (revised down from 0.25 —
  live verification found the identifiability literature's positive results are constructively interventional
  (single-intervention-per-latent, or O(log n) multi-node interventions), not passive-observation results;
  a purely passive, single-environment ingest stream is a WEAKER case than anything the positive identifiability
  results actually cover).

---

## Cheap decisive test

**Test name:** `B1+EXOG` (extends the already-designed `B1` disjoint-data cross-fit cell and reuses the
already-scoped `W_pred` predictive-coding matrix; no new architecture).

**Step 0 (near-zero cost, mandatory before building):** confirm off disk whether the landed `B1+PS` (DG) cell's
harness already logs per-branch prediction accuracy against real ingest data anywhere in its instrumentation —
if so, a first pass at the `B1+EXOG` signal may already exist without a new run.

**Step 1:** add a shared, real-ingest-data prediction target that BOTH Speaker and Listener branches must
independently reconstruct via `W_pred` (S2 above), on top of the existing disjoint-data cross-fit (B1,
unchanged — do not remove).

**Step 2:** measure `corr(failmask)` (same instrumentation as B1/B1+PS) and grounding (same floor as B1+PS,
`>=0.50`), plus run Prediction C's perturbation-sensitivity screen on the `W_pred` seed atoms specifically (real
grounded-feature perturbation vs. matched relation-only perturbation, `>=2x` differential requirement) as the
causal-verification companion metric — this catches the case where `corr(failmask)` improves for a spurious
reason (e.g., the shared target adds noise that happens to decorrelate branches without adding genuine
referential signal).

**Cost estimate:** reuses `predictive_coding.py`, the existing B1 harness, and the already-specified `W_pred`
matrix; incremental build is the shared-target wiring + the Prediction C perturbation harness. Comparable order
of cost to the already-completed B1+PS cell (CPU-feasible smoke, FULL dispatch for the decisive run).

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE_BAND, calibration-deflated)

| Claim | HARD-PASS | HARD-FAIL | MIDDLE_BAND | P_deflated |
|---|---|---|---|---|
| `B1+EXOG` closes the self-play blind-spot beyond `B1`/`B1+PS` | `corr(failmask) <= 0.30` AND grounding `>= 0.50` AND Prediction-C perturbation-sensitivity ratio `>= 2x` on `W_pred` seed atoms (rules out spurious decorrelation) | `corr(failmask) >= 0.35` (no material improvement over `B1+PS`'s already-measured `0.377`) — would mean even objective/distribution-level exogenous correction fails, redirecting to the costlier axis-4 (differentiated learning-algorithm-class) fallback named in the self-play differentiation-axis note | `corr(failmask)` in `(0.30, 0.35)` OR grounding/perturbation-ratio conditions only partially met | **0.25** |
| Prediction-C perturbation screen validates `W_pred` seed atoms as genuinely causally tracking real data (not a hollow correlate) | real-feature perturbation shift `>= 2x` matched relation-only-feature perturbation shift | no differential sensitivity (`< 1.3x`) — implementation/wiring failure, not evidence against the theory | ratio in `[1.3x, 2x)` | **0.40** (carried from the native-encoder note, unchanged — mechanism well-motivated, wiring untested) |
| Grounded seed + transitive spread jointly reach a usable fraction of vocabulary without new seed atoms beyond the `W_pred` kernel | far-hop (`d3+`) grounding accuracy stays `>= 0.40` when propagated from the `W_pred` kernel specifically (vs. the already-measured `0.48` from the prior, differently-sourced seed set) | far-hop accuracy collapses below `0.25` from a `W_pred`-sourced kernel — would mean the kernel itself, though causally verified, is too narrow/noisy a seed for transitive spread | `[0.25, 0.40)` | **0.30** |
| Ingest data supplies enough natural environment-diversity for causal-representation-learning-style identifiability (not just single-environment passive observation) | representation is measurably STABLE (low variance) across independent resamples/subsets of the ingest corpus, at a level comparable to a genuine multi-environment invariant-prediction baseline | representation varies substantially across resamples (non-identifiable / underdetermined by the corpus as currently constituted) — would motivate deliberately partitioning ingest data into distinct "environments" (e.g. by source/genre/time) to manufacture quasi-interventional structure | measurable but modest instability | **0.20** (most novel, least-precedented row; deliberately conservative) |

All rows capped `<=0.50` per lit-scan calibration penalty; all four are genuinely untested on this substrate
(novel-synthesis regime), and this cycle carries an ADDITIONAL deflation for unconfirmed live lit-scan
verification (see process note at top).

---

## Cross-thread synthesis

- **`research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md`:** this drill's central finding is the
  direct, confirmed continuation of that note's own S3 fork. Case (a) (representation-level fix insufficient)
  fired exactly as pre-registered; this note specifies the exogenous-referent mechanism that fork named but
  left unspecified, closing the loop between "what the DG negative means" and "what to build next."
- **`research_prediction_error_native_learning_signal_grounding_link_2026-07-09.md`:** supplies the entire
  buildable substrate (`W_pred`, precision-weighting reuse) this note's S2 depends on, and already flagged (at
  P=0.25, set BEFORE the DG result landed) the exact cross-link this note now elevates to the primary
  recommended next cell.
- **`research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md`:** supplies the already-HARD-PASSED
  transitive-spread mechanism this note's S2 reuses as the "rest of the vocabulary" half of the Harnad
  minimal-kernel design, plus the two depth-extension levers (iteration, binding) available if `W_pred`-sourced
  seeds need deeper reach than the prior seed set achieved.
- **`research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md`:** supplies Prediction C,
  reused here unchanged as the causal-representation-learning verification screen this note's literature
  independently identifies as the correct operational test for "grounded, not just correlated."
- **`research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md`:** supplies the
  differentiation-axis taxonomy and the efference-copy/folie-a-deux calibration case that motivates WHY a
  shared exogenous check (not just more internal differentiation) is needed even after branches are
  representation-decorrelated — two branches can still independently converge on the same self-consistent
  wrong answer absent an outside-the-loop check.

---

## Substrate-product implications

- This is not a publication-framing question. Every recommendation is a concrete extension of already-built,
  already-scoped primitives (`predictive_coding.py`, the `B1`/`B1+PS` harness, the transitive-spread readout,
  Prediction C's perturbation harness) — no new representational format or store-schema change.
- **Recommended next cell:** `B1+EXOG` as specified in "Cheap decisive test" above — directly actionable,
  reuses existing instrumentation, comparable cost to the already-completed `B1+PS` cell.
- **Standing discipline this drill reinforces:** three confirmed internal-only negatives (settling,
  differentiation, DG) plus this drill's convergent four-literature synthesis together justify treating
  "closed internal loops cannot manufacture referential grounding, but can propagate it once seeded
  exogenously" as a load-bearing design principle for this program going forward, not a one-off finding — any
  future internal-only grounding proposal should be checked against the data-processing-inequality argument
  above BEFORE being built, not after a fourth negative.
- **Honest scope discipline:** frame any `B1+EXOG` HARD-PASS as "closes the specific closed-loop blind spot
  this program identified," not as "grounding solved" — the sensorimotor/enactivist and full-Harnad bars
  remain open per S3, and the causal-identifiability residual question (environment-diversity of the ingest
  corpus) is a distinct, not-yet-addressed risk even if `B1+EXOG` passes.

---

## Citations (verified count: 34 sources across 4 live Sonnet lit-scan sub-agents, WebSearch/WebFetch-confirmed
this cycle; generic academic terms only, no substrate-novel names exposed, per
`[[feedback-query-privacy-decomposition]]`)

**Predictive coding / active inference (8):** Rao, R.P.N. & Ballard, D.H. (1999) *Nat. Neurosci.*; Friston, K.
(2010) "The free-energy principle: a rough guide to the brain?"; Pezzulo, G., Parr, T., Cisek, P., Clark, A. &
Friston, K. (2023) "Generating meaning: active inference and the scope and limits of passive AI," *Trends in
Cognitive Sciences* — **load-bearing for S1/S3, highest-confidence direct finding of this drill**; Coelho
Mollo, D. & Milliere, R. (2023/2024) "The Vector Grounding Problem," arXiv:2304.01481, *Philosophy and the
Mind Sciences* — load-bearing second necessary-condition; Harnad, S. (1990) "The Symbol Grounding Problem,"
*Physica D* 42:335-346 (cross-cited); Pu, S.X. et al. (2026) "Survive or Collapse: The Asymmetric Roles of
Data Gating and Reward Grounding in Self-Play RL," arXiv:2605.22217 — low-medium confidence, single very
recent unreplicated paper, but the most direct on-topic hit for the exogenous-vs-endogenous-decorrelation
question; arXiv:2603.02218 and arXiv:2601.05280 (2026, self-play information-closure arguments) — low
confidence, unreplicated; data-processing-inequality math: arXiv:2103.13591 (directed DPI, feedback systems),
arXiv:2311.10786 (closed-systems boundary-information formalization) — medium-high confidence for the math,
medium confidence for its application to grounding (this program's own inference, not a cited theorem).

**Sensorimotor contingency / enactivism (7):** O'Regan, J.K. & Noe, A. (2001) "A sensorimotor account of
vision and visual consciousness," *Behav. Brain Sci.* 24:939-1031; Laflaquiere, A., O'Regan, J.K., Gas, B. &
Terekhov, A. (2018) "Discovering space," *Neural Networks*, arXiv:1806.02739; companion papers
arXiv:1810.01871, arXiv:1609.08009 (same group, robotic sensorimotor-contingency simulations); Pak, "Grounding
Perception: A Developmental Approach to Sensorimotor Contingencies," arXiv:1810.01870; Stanford Encyclopedia of
Philosophy, "Action-based Theories of Perception" (2025 ed.) — source of the necessity-vs-sufficiency
disambiguation and the passive-adaptation counter-evidence; Held & Hein (classic, cited secondarily);
"A critical approach to sensorimotor contingency theory" (2020-21, academia.edu/ResearchGate) — medium
confidence, non-peer-reviewed venue.

**Harnad symbol grounding / categorical perception (7):** Harnad, S. (1990) *Physica D* 42:335-346; Harnad, S.
(ed., 1987) *Categorical Perception*; Vincent-Lamarre, P., Blondin Masse, A., Lopes, M., Lord, M., Marcotte, O.
& Harnad, S. (2016) "The Latent Structure of Dictionaries," *Topics in Cognitive Science* 8:625-659,
arXiv:1411.0129 — **load-bearing, highest-confidence quantitative kernel-size result of this drill**; Greco, A.
& Caneva, C. (2010) "Compositional Symbol Grounding for Motor Patterns," *Frontiers in Neurorobotics* —
load-bearing robotic transitive-grounding calibration; Greco, A. & Carrea, E. (2012) "Grounding Compositional
Symbols," *Cognitive Processing* 13(2):139-150; Shahid & Rothe (2026) "Grounding vs. Compositionality: On the
Non-Complementarity of Reasoning in Neuro-Symbolic Systems," arXiv:2604.26521 — moderate confidence, very
recent/single-source, contested; Kleyko et al. (2022/2023) "A Survey on Hyperdimensional Computing," *ACM
Computing Surveys* Parts I & II — VSA/binding background, no direct Harnad-transitive-inheritance citation
found (inferred connection only).

**Causal representation learning (8):** Scholkopf, B., Locatello, F., Bauer, S., Ke, N.R., Kalchbrenner, N.,
Goyal, A. & Bengio, Y. (2021) "Toward Causal Representation Learning," *Proc. IEEE* 109(5), arXiv:2102.11107;
Locatello, F. et al. (2019) "Challenging Common Assumptions in the Unsupervised Learning of Disentangled
Representations," ICML (arXiv:1811.12359, best paper) — the disentanglement-impossibility-without-inductive-bias
result; Ahuja, K. et al. (2023) "Interventional Causal Representation Learning," ICML, arXiv:2209.11924;
Squires, C., Seigal, A., Bhate, S. & Uhler, C. (2023) "Linear Causal Disentanglement via Interventions," ICML;
arXiv:2406.05937 (2024) and arXiv:2603.25796 (2026) — reduced intervention-budget results, moderate confidence,
recent; Geiger, A. et al. (2022) "Inducing Causal Structure for Interpretable Neural Networks," ICML, and
(2024) "Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations,"
CLeaR, arXiv:2303.02536 — the Distributed Alignment Search / Interchange Intervention Accuracy protocol, the
concrete held-out perturbation-screen mechanism; Veitch, V. et al. (2021) "Counterfactual Invariance to
Spurious Correlations," NeurIPS, arXiv:2106.00545 — the stress-test/spurious-vs-real differential-sensitivity
design.

**Already on-disk, reused (see prior notes for full citations):** Bender & Koller (2020) "the octopus test";
Bisk et al. (2020) "Experience Grounds Language"; Chernozhukov et al. (2017/2018) Neyman-orthogonal
cross-fitting.

Confidence: HIGH for Pezzulo et al. 2023 (peer-reviewed, prominent venue, Friston co-author — this drill's
single best-sourced finding), Vincent-Lamarre et al. 2016 (peer-reviewed, quantitative, directly on-topic), and
the core predictive-coding/Harnad foundational texts. MEDIUM for the sensorimotor-contingency
necessity-vs-sufficiency dispute and the CRL identifiability specifics (real, correctly characterized, but some
numeric thresholds are recent/single-source). LOW-MEDIUM, explicitly flagged, for the 2026 self-play-RL papers
(Pu et al. and companions) and the Shahid & Rothe grounding-decay paper — genuinely on-topic and worth citing,
but thin/unreplicated and should be treated as suggestive, not decisive.

---

Per [[feedback-no-papers-product-only]]: no publication framing. Every recommendation above is scoped to a
concrete substrate cell extension (`B1+EXOG`) using primitives already on disk, not a scientific contribution
claim.
