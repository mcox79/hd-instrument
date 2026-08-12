# Binding/addressing credit-assignment: is "gradient-stuck, probe-solvable" a named phenomenon, and is the fix structural?

**Date:** 2026-07-30
**Trigger:** measured this session — a content-gated WM's addressing key, trained end-to-end from random
init on the downstream recall loss alone, gets STUCK_FLAT (all role-queries collapse to cosine ~0.992,
loss never descends), even though the correct linear addressing solution EXISTS and is trivially found by
a logistic probe trained with DIRECT supervision on the slot label (acc 1.0), and transplanting that
probe's weights into the WM key solves addressing at acc 1.0 with zero further training.
**Method:** KB-check (`substrate_query.sh`, 3 queries) + 2 parallel Sonnet external lit-scans (generic
math/ML terms only, no substrate-specific framing sent off-platform) + synthesis against strong existing
internal KB on hippocampal indexing theory (`notes/research_learned_noise_robust_addressing_page_routing_2026-07-16.md`).
**Calibration:** lit-scan penalty applied (deflate 0.15-0.25); novel-synthesis P capped at 0.50 for any
substrate-mapping claim below.

---

## HEADLINE

**Yes, this is a known phenomenon-class, though not under one single name, and the convergent literature
answer across ML and neuroscience is the same: symmetry-breaking for a competitive addressing/attention
mechanism cannot be reliably bootstrapped from downstream task loss alone from a random/symmetric start —
every reported fix intervenes BEFORE or ALONGSIDE the competitive step (warm-start, auxiliary direct
supervision, diverse/structured init, or an architecturally-privileged fast-binding stage), never by
"training the downstream loss harder/longer" on an unmodified random start.** The brain's own answer to
the identical structural problem (bind an arbitrary query to the right stored index) is not "learn
addressing end-to-end from task reward" — it is a dedicated, largely pre-structured, fast-imprinting
circuit (hippocampal indexing + entorhinal grid/place code) that is functionally and temporally SEPARATE
from the slow, reward/error-driven cortical learning used for content. Supplying/warm-starting the address
is therefore the biologically faithful move, not a forbidden shortcut — provided (per the invariant check
in section (c)) that what is supplied is a STRUCTURAL PRIOR/AUXILIARY SIGNAL, not the answer itself.

---

## (a) Is this phenomenon named/known? Top citations

Two independent literatures converge, neither exactly matching your setup but both structurally on-point:

1. **Sukhbaatar et al. 2015, "End-To-End Memory Networks"** (NeurIPS, arXiv:1503.08895) — the single
   closest citation. They report training softmax content-addressing attention from scratch is hard, and
   introduce **"linear start" (LS)**: strip the softmax (train with linear/uniform attention) until
   validation loss plateaus, THEN re-insert softmax. Their own ablation shows softmax-from-init
   underperforms the two-stage warm-started version. This is exactly your failure mode (competitive
   addressing collapses when trained end-to-end from init) and exactly the fix-class (warm-start /
   delay-the-competition), independently converging with your probe-transplant fix.
2. **Collier & Beel 2018, "Implementing Neural Turing Machines"** (arXiv) — reports NTM/DNC
   reimplementations are notoriously unstable, with **memory-content initialization and content-based
   addressing as the crux**, and a named **"mode collapse" in memory usage** where read/write heads
   concentrate on a small subset of locations regardless of query — structurally identical to your
   all-queries-collapse-to-one-slot signature.
3. **Locatello et al. 2020, "Object-Centric Learning with Slot Attention"** (NeurIPS) + follow-ups
   (arXiv:2301.13197 "Unlocking Slot Attention by Changing Optimal Transport Costs"; arXiv:2507.23755
   "Slot Attention with Re-Initialization and Self-Distillation") — report that learned (vs. fixed random)
   slot initialization HURTS, and that slots collapse to near-identical assignments when init is too
   similar because the softmax-over-slots competition has no gradient signal to break symmetry absent a
   diversity-inducing init or an explicit anti-collapse mechanism.
4. **Dong, Cordonnier & Loukas 2021, "Attention is Not All You Need: Pure Attention Loses Rank Doubly
   Exponentially with Depth"** (ICML, arXiv:2103.03404) — proves pure self-attention has an inherent bias
   toward token/output uniformity ("rank collapse") absent residual connections/MLPs; the fix is
   architectural, not more gradient steps. Gives a theoretical mechanism for WHY an attention-like
   addressing computation can degenerate all outputs toward one point independent of input.
5. **Csordás & Schmidhuber 2018, "Improved Addressing in the DNC"** (NeurIPS workshop / arXiv:1904.10278)
   — diagnoses specific addressing pathologies in the original DNC (content-lookahead ignored, improper
   de-allocation, link-sharpness degradation) and fixes them with explicit structural/masking mechanisms,
   not longer training. Directly supports "pure downstream-loss training of addressing gets stuck in bad
   regimes that need an explicit structural correction," which is your finding.
6. **Olsson et al. 2022, "In-context Learning and Induction Heads"** (Anthropic, arXiv:2209.11895) — the
   counter-data-point: induction heads DO form as a sudden phase transition from plain next-token loss
   alone, no auxiliary supervision. This is evidence pure downstream loss CAN bootstrap a addressing-like
   circuit given the right architecture/scale/data statistics — it does not show a case going flat
   forever, so it tempers (does not refute) the "always needs external help" reading: scale, architecture,
   and training-data statistics may be the missing ingredient in some regimes, not always an auxiliary
   signal. Flag this as the live alternative hypothesis, not dismiss it.

No single paper names your EXACT phenomenon (a linear addressing solution existing, probe-recoverable,
gradient-inaccessible from downstream loss alone). The mapping across (1)-(5) to your setup is INFERENCE,
though a well-corroborated one (independent literatures, same qualitative signature, same fix-class).

---

## (b) VERDICT: structural fix vs. "optimize harder" — brain-grounded

**Structural.** Three independent lines converge:

- **ML literature (a, above):** every reported repair of this exact failure signature (softmax
  addressing/attention collapsing to uniform or single-target regardless of query) is a warm-start,
  auxiliary-signal, structured-init, or architectural change — never "more epochs on the unmodified
  setup." Sukhbaatar's own controlled ablation is the cleanest evidence: same architecture, same loss,
  same data — the ONLY difference is whether softmax competition is introduced immediately (fails to
  differentiate keys well) or after a linear warm-start (works).
- **Theory (Dong/Cordonnier/Loukas):** there is a proven MATHEMATICAL bias in attention-like operators
  toward output collapse; this is a property of the operator class, not merely an optimization-schedule
  artifact fixable by patience. That is a structural, not a "try harder," diagnosis.
- **Brain (already in KB, `research_learned_noise_robust_addressing_page_routing_2026-07-16.md`, sections
  A1-A3, reused not re-derived): the hippocampal/entorhinal addressing solution is not "the same slow
  reward-driven learning that also learns content, just needing more trials" — it is an architecturally
  SEPARATE, fast-Hebbian, largely pre-structured mechanism** (dentate-gyrus fixed random
  expansion+sparsify, entorhinal grid-cell path-integration attractor dynamics) operating on a completely
  different timescale and plasticity rule than the slow cortical statistical learning used for content.
  This session's fresh external lit-scan corroborates and sharpens this: grid-cell firing appears
  IMMEDIATELY on entering a novel environment via intrinsic attractor dynamics (biorxiv
  10.1101/2023.09.07.556744, "one-shot entorhinal maps" — sourced), and a 2024 study
  (eLife 10.7554/eLife.89356) found a feedforward network learns grid-like codes on par with a
  path-integrating recurrent model and that the grid code "does not appear to be defined by the task of
  path integration" — i.e. the addressing code self-organizes from structural/statistical constraints
  independent of the downstream task loss that will later consume it. Caveat (sourced, genuine nuance,
  not full consensus): fine-grained anchoring of the grid/place code to a SPECIFIC task's reference frame
  does require experience and slower plasticity — so "pre-structured" applies to the raw
  addressing-capacity/coordinate-system, not to every last task-specific alignment detail.

**Verdict:** the fix belongs in the SAME category as Sukhbaatar's linear-start, Locatello's fixed-diverse
init, and the brain's dedicated fast-binding stage — NOT in the category of "run more optimizer steps on
the coupled downstream-loss-only setup." Continuing to train the WM's current setup longer is
predicted, by convergent theory and empirical precedent, to stay stuck; this is the informative NEGATIVE
prediction this note stakes (see falsifiable predictions below).

---

## (c) Is supplying/supervising the address brain-faithful, or a forbidden bolt-on shortcut?

This is the load-bearing question for your invariants (no bolt-on reader/parser; no borrowed embeddings
as the encoder; runtime reasoning must stay glass-box, no external oracle at inference).

**Brain-faithful, with a specific, narrow condition — and this session's mechanism ALREADY satisfies it.**
The distinction that matters is not "was the address supplied" but **WHAT is supplied and by WHAT
mechanism**:

- **Forbidden pattern** (the thing the no-bolt-on-reader / no-borrowed-embedding disciplines correctly
  guard against): importing an externally-pretrained, opaque black-box model to DO the comprehension work
  at inference time, or hard-coding the answer to a specific instance (e.g. hand-writing `role->slot`
  lookup dicts per item, which is exactly what the existing `exp_wm_paging_*` cells' hand-built page-table
  does, and exactly what the KB note above already flags as the untested, non-generalizing assumption).
  That is supplying the ANSWER, not the mechanism, and it does not generalize to unseen roles by
  construction.
- **What you actually did (probe transplant):** the probe was trained with direct supervision on the
  SLOT LABEL from THIS SUBSTRATE'S OWN frozen encoder representations — a linear readout over your own
  glass-box vectors, inspectable, not an external model, not per-instance memorization. Structurally this
  is a **warm-start / auxiliary-supervision intervention on an addressing key**, in the same family as
  Sukhbaatar's linear-start (warm-starting the addressing computation before/alongside the competitive
  step) and the DG-analog fixed-projection router already validated for a DIFFERENT purpose in this
  project's own KB (`research_learned_noise_robust_addressing_page_routing_2026-07-16.md`: a FIXED,
  non-per-item-trained expand+sparsify projection is exactly this kind of structural prior, and it is
  already accepted in this project as brain-faithful because DG's separation function is genuinely fixed
  and non-per-item, generalizing to any input including novel ones by construction, not a lookup table).
- **The biological analogy is precise, not loose:** hippocampal index formation is FAST, Hebbian,
  largely pre-structured (grid/place code, DG projection) and functionally privileged relative to slow
  cortical content learning — this is not "the brain also has to slowly discover addressing from reward,"
  it is "the brain's addressing stage runs on different, faster, more structurally-given machinery than
  its content-learning stage." Auxiliary-supervising or warm-starting the WM's key from an
  already-existing, generalizing linear signal in your OWN encoder is the substrate-native analog of that
  same division of labor — not an external shortcut.

**The test that separates faithful-warm-start from forbidden-answer-supply is exactly section (d)'s
protocol**: if the warm-started/aux-supervised key GENERALIZES to roles/slots it was never
supervised on, that is a structural prior (brain-faithful, DG/grid-analog). If it only works for the
supervised roles and needs a fresh probe-transplant per new role, that is per-instance lookup (the
forbidden pattern), and the "fix" would be equivalent to hand-building the page-table the KB note already
flags as non-generalizing.

---

## (d) The concrete held-out-role generalization protocol + can-fail control

**Protocol ("held-out-role warm-start transfer test"):**

1. Split the full set of roles/slots into TRAIN-ROLES (majority, e.g. 80%) and HELD-OUT-ROLES (remainder,
   e.g. 20%), disjoint, fixed seed.
2. Train the auxiliary/warm-start signal (the linear probe, or whatever aux loss is chosen) using direct
   slot-label supervision on TRAIN-ROLES ONLY. Held-out roles must NEVER appear in this supervision signal.
3. Warm-start / initialize the WM's addressing key from this TRAIN-ROLES-only probe, then continue
   end-to-end training on the downstream recall loss (as already planned) using episodes drawn from BOTH
   train and held-out roles mixed in the downstream task (the downstream loss itself may see held-out
   roles — that's fine, task exposure without ADDRESS-label supervision is exactly the generalization
   being tested).
4. Evaluate addressing accuracy (does query -> correct slot) SEPARATELY on: (i) TRAIN-ROLES (sanity floor,
   should be high — already established), (ii) HELD-OUT-ROLES never seen by the aux signal
   (the decisive number).
5. **Can-fail control arm — no-warm-start baseline**: identical architecture, identical downstream-loss
   training, but addressing key initialized randomly (the ORIGINAL STUCK_FLAT setup), same train/held-out
   role split. This arm is EXPECTED to fail on both train and held-out roles (reproducing STUCK_FLAT) —
   if it does NOT fail, the split/task construction is broken (vacuous test, report as INVALID, do not
   proceed to interpreting the warm-started arm).
6. **Second can-fail control — per-role-lookup control**: an explicit non-generalizing baseline built to
   look good on TRAIN-ROLES and fail cleanly on HELD-OUT — e.g. a k-NN/nearest-train-role lookup table
   with no shared structure. This arm should score near-chance on held-out roles; if the warm-started arm
   scores similarly to THIS control on held-out roles (rather than near its train-role score), that is
   evidence the warm-start bought per-role memorization, not generalizing binding.

**Falsifiable predictions:**

- **HARD-PASS (genuine generalizing binding, structural prior confirmed):** held-out-role addressing
  accuracy >= 0.80 (vs. train-role accuracy, gap <= 0.15) AND no-warm-start control stays at/near
  STUCK_FLAT on both splits (confirms the test is non-vacuous) AND warm-started arm clears the
  per-role-lookup control by >= 0.30 on held-out roles (rules out disguised memorization).
- **HARD-FAIL (per-role lookup only, not comprehension):** held-out-role accuracy < 0.40, OR held-out gap
  vs. train-role accuracy > 0.35, OR warm-started arm's held-out score is statistically indistinguishable
  (within 0.10) from the per-role-lookup control's held-out score. Any of these means the fix, however
  useful practically, is NOT the brain-faithful generalizing mechanism claimed in section (c) — it is the
  forbidden "supply the answer per instance" pattern in disguise, and must be reported as such, not
  reframed as success.
- **INVALID:** no-warm-start control does not reproduce STUCK_FLAT on this split (test construction bug,
  fix before interpreting); or TRAIN-ROLE addressing accuracy itself is below ~0.85 (aux-signal training
  didn't even converge on its own supervised set — a prerequisite failure, not a generalization failure).

---

## Cross-thread synthesis

- Directly extends `research_learned_noise_robust_addressing_page_routing_2026-07-16.md` (KB, reused not
  re-derived): that note already established the DG-analog fixed-projection router as the brain-faithful
  generalizing-addressing mechanism for a DIFFERENT gap (paging/routing to a stored page under a hand-built
  dict). This note's question is upstream of that one: whether a LEARNED (not fixed) addressing key can
  be made to reach the same generalizing property via warm-start/aux-supervision, when a fully fixed
  random projection is not what the WM architecture uses. The held-out-role protocol above is the fair
  test that would tell you whether your WM's learned-key approach earns the same generalization property
  the fixed-projection DG-analog gets "for free," or whether it needs the fixed-projection instead.
- Consistent with `research_native_binding_compositional_generalization_2026-07-25.md`'s general finding
  that a FIXED bind + single learned linear readout systematically outperforms unconstrained
  entanglement for compositional generalization — the addressing key is the "fixed role vector" analog in
  that framing; warm-starting it from a generalizing probe (rather than leaving it free to entangle
  per-query idiosyncrasies from a stuck random init) is the same structural move applied to your specific
  WM component.
- Olsson et al.'s induction-head phase transition (citation 6) is the honest live counter-hypothesis:
  before concluding "must warm-start," it would be cheap to also check whether MORE training data /
  longer schedule / a scale change alone produces a late, sudden un-stuck transition (their induction
  heads form this way from plain loss). If a longer-schedule control (same architecture, same loss, 5-10x
  more steps/data, no warm-start) also stays flat, that strengthens the structural verdict; if it suddenly
  un-sticks, this note's structural conclusion would need revision. Recommend running this cheap control
  ALONGSIDE the held-out-role protocol, not instead of it — they're orthogonal checks (schedule-only vs.
  structural-prior) and both are cheap.

## Substrate-product implications

If HARD-PASS: the substrate can learn NEW addressing/binding tasks by warm-starting from a small
auxiliary-supervised signal over its own frozen representations, then generalizing to unseen
roles/queries never explicitly supervised — directly supports the "converse about combinations never
literally trained" product story already scoped in the native-binding note, extended from fixed-algebra
binding to LEARNED-key binding, which is likely the more general case product-facing tasks will need
(schemas aren't always known/fixable in advance).
If HARD-FAIL: the warm-start is a practical unstick-the-optimizer trick but not a generalizing mechanism;
either the WM addressing must move to a FIXED/structural-projection design (per the 07-16 note, proven
generalizing) rather than a learned key, or the encoder's slot signal (while present, per the linear-probe
evidence) is not the right SHAPE for a learned-key attention mechanism to exploit zero-shot, which would
be a genuinely new, reportable gap (encoder CONTAINS the signal but not in an attention-consumable form).

## Citations (verified count: 6 external, cross-checked across 2 independent sub-agent lit-scans, no
contradicting source found; plus 8 internal KB citations reused without re-verification from
`research_learned_noise_robust_addressing_page_routing_2026-07-16.md` and
`research_native_binding_compositional_generalization_2026-07-25.md`)

1. Sukhbaatar, S. et al. (2015). "End-To-End Memory Networks." NeurIPS. arXiv:1503.08895.
2. Collier, M. & Beel, J. (2018). "Implementing Neural Turing Machines." arXiv.
3. Locatello, F. et al. (2020). "Object-Centric Learning with Slot Attention." NeurIPS. (+ follow-ups
   arXiv:2301.13197, arXiv:2507.23755)
4. Dong, Y., Cordonnier, J-B. & Loukas, A. (2021). "Attention is Not All You Need: Pure Attention Loses
   Rank Doubly Exponentially with Depth." ICML. arXiv:2103.03404.
5. Csordás, R. & Schmidhuber, J. (2018/2019). "Improved Addressing in the DNC." arXiv:1904.10278.
6. Olsson, C. et al. (2022). "In-context Learning and Induction Heads." Anthropic. arXiv:2209.11895.

Internal (reused): Teyler & DiScenna 1986; Teyler & Rudy 2007; Hafting et al. 2005; Fiete, Burak &
Brookings 2008; Whittington et al. 2020 (TEM); Marr 1971; O'Reilly & McClelland 1994 — all already
verified in `research_learned_noise_robust_addressing_page_routing_2026-07-16.md`, not re-verified here.
Plus 2 fresh sourced neuroscience results this session: biorxiv 10.1101/2023.09.07.556744 ("one-shot
entorhinal maps," grid firing immediate on novel environment); eLife 10.7554/eLife.89356 (feedforward
network learns grid-like code independent of path-integration task). McClelland/McNaughton/O'Reilly 1995
(Complementary Learning Systems) also freshly cited this session as direct support for point (b)'s
fast/pre-structured-vs-slow-content framing.

## P_deflated

Naive P (held-out-role protocol clears HARD-PASS) ~ 0.55 given strong convergent evidence (ML fix-class
literature + brain fast-binding literature both point the same direction, corroborating your own
probe-transplant result). Deflated per lit-scan calibration penalty (-0.20: no paper tests your EXACT
setup — linear-probe-warm-start into a VSA/HDC-style content-gated WM key — the mapping from Sukhbaatar's
linear-start / Locatello's diverse-init / hippocampal fast-binding to this specific mechanism is inference,
not directly measured precedent) and novel-synthesis cap applied.

**P_deflated = 0.40** (HARD-PASS band, held-out-role generalization). Flag: the STRUCTURAL-vs-schedule
verdict in section (b) is higher confidence (~0.60-0.65, two independent theory lines + strong brain
precedent) than the specific numeric HARD-PASS bands in section (d), which are novel-synthesis engineering
extrapolation and correctly capped lower.

Next-drill candidate if HARD-FAIL: Olsson et al.'s induction-head-phase-transition alternative — run the
cheap longer-schedule-only control (no warm-start, 5-10x steps/data) before concluding warm-start is
strictly necessary; if that alone un-sticks the optimizer, the lever is schedule/scale, not a structural
prior, and this note's verdict would need revision.
