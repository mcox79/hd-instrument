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
| **Sensorimotor contingency theory / enactivism** (O'Regan & Noe 2001; Noe 2004; Gibson 1979 ecological affordances; Varela/Thompson/Rosch 1991) | Grounding = mastery of the lawful, action-contingent structure of how real sensory input changes as a function of movement — a regularity DISCOVERED in the world via a closed action-perception loop, not invented internally. | **Secondary — a STRONGER, more complete variant of predictive coding.** Requires action/perturbation capability closing through the real world; the literature (per this drill's own prior on-disk finding, the Bender-Koller/Bisk-et-al critique) treats passive prediction of a static stream as a weaker, non-equivalent case — genuine but partial. |
| **Harnad categorical-perception symbol grounding** (Harnad 1990 "The Symbol Grounding Problem"; Harnad 1987 categorical perception; Cangelosi, Greco & Harnad 2000 "From robotic toil to symbolic theft"; Steels 2008) | A small set of elementary symbols are grounded via NON-SYMBOLIC categorical discrimination of real sensory input at a learned decision boundary; everything else inherits grounding TRANSITIVELY through pure symbolic composition of already-grounded primitives — no further perceptual contact required for the bulk of the vocabulary. | **Tertiary — the MINIMAL-KERNEL special case of predictive coding applied to category-boundary discrimination, plus a transitive-spread claim.** This substrate has ALREADY empirically validated the transitive-spread half of this claim today (grounding-cascade note, HARD-PASS on near/far-hop decay), independently of this drill — the open part is what grounds the SEED kernel itself, which is exactly predictive coding's job. |
| **Causal representation learning intervention screen** (Scholkopf et al. 2021 "Towards Causal Representation Learning"; Ahuja et al. 2022 interventional identifiability; Peters, Buhlmann & Meinshausen 2016 invariant causal prediction; Locatello et al. 2019 disentanglement-impossibility) | Formalizes WHEN a representation can be proven to track true causal factors: perturbing the real factor must move the representation differentially more than perturbing a spurious/confounded one; provable identifiability generally requires MULTIPLE environments or interventions, not just more passive observation. | **Not a grounding-manufacturing mechanism — the VERIFICATION mechanism.** This is the test, not the anchor. Already specified on this substrate as Prediction C (perturbation-sensitivity, `>=2x` differential requirement). |

**Why predictive coding specifically breaks the ceiling internal decorrelation cannot:** the DG fix
(`B1+PS`) applied a fixed, independently-seeded, sparse-expansion-plus-competitive-sparsification transform
to the SHARED representation before splitting it per branch — a purely internal, deterministic function of
data that was itself entirely self-generated within the loop. By the data-processing inequality, no
deterministic (or even stochastic, data-independent-of-the-referent) transform applied downstream of a signal
can increase that signal's mutual information with anything the signal never carried information about in the
first place. If the shared upstream representation carries zero bits about a genuine external referent (because
it was self-authored inside the loop), pattern separation can decorrelate the TWO BRANCHES from each other
(and it partially did — `corr` moved from a naive-mirror baseline down through B1's cross-fit to `0.377`) but
it cannot manufacture bits about an external world that were never there. This is precisely the formal content
of the DG cell's own pre-registered HARD-FAIL case (a): a representation-level fix was tried, and — exactly as
that fork predicted — failed to move the needle further, because the ceiling was never representation-level to
begin with. Real sensory/ingest data does not have this ceiling: it is caused by a process outside the loop, so
predicting it against a real target necessarily injects information the internal loop could not have generated
on its own, no matter how the internal branches are shaped.

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

**Transitive spread (already validated, reuse don't rebuild):** the grounding-cascade note's already-HARD-PASSED
transitive-inheritance mechanism (near d1=0.63, far d3=0.48, decay 0.146) IS the spread mechanism — grounded
seed atoms propagate their grounding to the rest of the vocabulary via the existing relational-graph readout,
with the same note's two named depth-extension levers (iterative/recurrent settling; compositional
bind-then-unbind chaining) available to extend reach beyond 1 hop when needed. No new architecture required
for a first cut — this piece of S2 is a reuse instruction, not a new build.

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

**Does this give FULL referential grounding, or a stronger-but-still-partial anchor?** The literature answer,
held consistently across all four angles even without live re-verification, is: **a stronger-but-still-partial
anchor, not full referential grounding**, for two independent reasons already flagged on-disk and reconfirmed
by direct knowledge of the source literatures:

1. **Passive prediction is not the same as sensorimotor/enactivist grounding.** O'Regan & Noe's mechanism
   requires mastery of a LAWFUL ACTION-CONTINGENT regularity via a closed perception-action loop through the
   real world; predicting a static real ingest stream with no ability to act on or query it is, at best, a
   degenerate/minimal case the enactivist literature does not treat as equivalent to full sensorimotor
   grounding. This substrate's design (predicting ingest data) is passive by construction.
2. **Passive prediction is not the same as full Harnad-sense referential grounding, and the ML literature is
   explicit and unresolved on this exact point** — already surfaced on-disk (Bender & Koller 2020 "the octopus
   test"; Bisk et al. 2020 "Experience Grounds Language"; the 2025/2026 "epistemic parasitism" critique): a
   corpus is a RECORD of experience, not experience itself, and text-only next-token prediction risks
   inheriting form (and grounding humans already encoded into the text) rather than manufacturing new,
   first-person referential contact. This drill's literature does not overturn that critique.

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

**Sharpest residual question:** the causal-representation-learning identifiability literature (Ahuja et al.;
Peters/Buhlmann/Meinshausen invariant prediction) is fairly explicit that provable recovery of true causal
factors from passive observational data alone is generally UNDER-IDENTIFIED — reliable identifiability
typically requires multiple environments or genuine interventions, not merely more of the same static
real-data stream. Does this substrate's ingest data supply enough NATURAL environment-diversity (different
real sources, different real conditions, quasi-interventional structure across the corpus) to satisfy this
condition, or is the current ingest stream effectively a single static environment — in which case
prediction-error-against-it, however genuinely exogenous, may still leave the learned representation
under-identified/non-uniquely-grounded in the causal-representation-learning sense, even though it is
mutual-information-genuine in the data-processing-inequality sense above? This is a DIFFERENT failure mode
than the one just confirmed (it is about identifiability/uniqueness, not about exogeneity/information-content)
and is the natural next drill if `B1+EXOG` HARD-PASSes the `corr(failmask)` screen but a follow-up probe finds
the grounded representation is not stable/unique across resampling of the same static corpus.

**Deflated P estimates (capped at 0.50, further deflated for this cycle's live-verification gap):**
- P(predict-real-ingest-data supplies a genuine, structurally distinct exogenous anchor at the mechanism
  level — the data-processing-inequality argument): **0.50** (capped; DG HARD-FAIL is direct on-disk
  confirmatory evidence, not pure extrapolation).
- P(`B1+EXOG`, wiring prediction-error-against-real-ingest-data as a shared reconstruction target for both
  self-play branches, HARD-PASSES `corr(failmask) <= 0.30` with grounding `>= 0.50` intact — the pre-registered
  number already carried from the prediction-error note): **0.25** (unchanged from that note's own figure;
  this is the single most consequential number in this note, and it was set BEFORE knowing the DG HARD-FAIL
  would land, so it is not post-hoc-inflated).
- P(this constitutes FULL Harnad-sense referential/embodied grounding, not a partial structural anchor):
  **0.15** (unchanged from the prediction-error note's own figure — literature explicitly contests full
  equivalence and this drill does not overturn that).
- P(passive ingest-data prediction alone satisfies causal-representation-learning identifiability conditions
  without additional environment-diversity/interventional structure): **0.25** (deflated — identifiability
  literature generally requires more than single-environment passive observation; untested whether this
  substrate's ingest corpus has enough natural diversity to qualify).

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

## Citations (verified count: 15 foundational/highly-cited sources from direct knowledge; NOT independently
re-fetched via live search this cycle — see process note at top; treat as HIGH confidence for the well-known,
textbook-adjacent items and flag for follow-up live-verification)

**Predictive coding / active inference (5):** Rao, R.P.N. & Ballard, D.H. (1999) *Nat. Neurosci.* 2(1):79-87;
Friston, K. (2010) "The free-energy principle: a unified brain theory?" *Nat. Rev. Neurosci.* 11:127-138;
Friston, K., Kilner, J. & Harrison, L. (2006) "A free energy principle for the brain," *J. Physiol.-Paris*;
Clark, A. (2013) "Whatever next? Predictive brains, situated agents, and the future of cognitive science,"
*Behav. Brain Sci.* 36:181-204; Hohwy, J. (2013) *The Predictive Mind*, Oxford University Press.

**Sensorimotor contingency / enactivism (4):** O'Regan, J.K. & Noe, A. (2001) "A sensorimotor account of
vision and visual consciousness," *Behav. Brain Sci.* 24:939-1031; Noe, A. (2004) *Action in Perception*, MIT
Press; Gibson, J.J. (1979) *The Ecological Approach to Visual Perception*; Varela, F., Thompson, E. & Rosch, E.
(1991) *The Embodied Mind*, MIT Press.

**Harnad symbol grounding / categorical perception (3):** Harnad, S. (1990) "The Symbol Grounding Problem,"
*Physica D* 42:335-346; Harnad, S. (ed., 1987) *Categorical Perception: The Groundwork of Cognition*;
Cangelosi, A., Greco, A. & Harnad, S. (2000) "From robotic toil to symbolic theft: grounding transfer from
entry-level to higher-level categories," *Connection Science* 12:143-162.

**Causal representation learning (3):** Scholkopf, B., Locatello, F., Bauer, S., Ke, N.R., Kalchbrenner, N.,
Goyal, A. & Bengio, Y. (2021) "Towards Causal Representation Learning," *Proc. IEEE* 109:612-634,
arXiv:2102.11107; Ahuja, K. et al. (2022) "Interventional Causal Representation Learning," arXiv:2209.11924;
Peters, J., Buhlmann, P. & Meinshausen, N. (2016) "Causal inference using invariant prediction," *J. R. Stat.
Soc. B*.

**Already on-disk, reused (not re-cited independently this cycle):** Bender & Koller (2020); Bisk et al.
(2020); Chernozhukov et al. (2017/2018) Neyman-orthogonal cross-fitting — see prior notes for full citations.

Confidence: HIGH for the core predictive-coding/free-energy and Harnad symbol-grounding mechanisms
(foundational, textbook-adjacent, extremely well-replicated literatures). MEDIUM for the precise
sensorimotor-contingency minimal-sufficient-condition and the causal-representation-learning
identifiability-condition specifics (real literatures, correctly characterized at a high level, but exact
thresholds/sample-complexity numbers were not independently re-verified via live search this cycle — flagged
as the specific follow-up if the 4 dispatched lit-scan sub-agents' results arrive later).

---

Per [[feedback-no-papers-product-only]]: no publication framing. Every recommendation above is scoped to a
concrete substrate cell extension (`B1+EXOG`) using primitives already on disk, not a scientific contribution
claim.
