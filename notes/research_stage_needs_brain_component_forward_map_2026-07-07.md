# Research: Stage-needs x brain-component FORWARD map (anticipate, don't build early)

**Date:** 2026-07-07. **Type:** Planning/synthesis drill (USER-directed). No cell dispatch, no cell
design, no experiment authored. Pure internal-corpus synthesis re-scoping the existing
CONSUMER-first brain-component work (07-05 inventory, 07-07 x2 consumer-ranking passes, 07-07
ingest-CLS drill) into a forward-looking STAGE-NEEDS map. Field-advisor run per contract
(`research_field_advisor.py`); output correctly overridden for this cycle because the task is a
USER-directed planning question (Trigger-E equivalent), matching the explicit precedent set by
`research_ingest_arc_scoping_staged_plan_2026-07-07.md`.
**Discipline:** mechanism-analog-is-not-task-analog applied throughout — a brain-component's NAME
sounding relevant to a stage is not evidence it is load-bearing for that stage's actual mechanism.
Lit-scan calibration penalty applied where citations are carried (deflate 0.15-0.25; novel-synthesis
P capped 0.50). Two spot-check figures re-verified off-disk this cycle (Fix#28): `exp_pfc_gate_cfrpe_
trained_v2/metrics.json` (`HARD_PASS`, `focus_gonogo_lift=0.6`, `focus_closure=0.6605...`, matches the
`0.600`/`0.661` figures cited in prior notes) and `exp_ingest_knowledge_integration_verify_v1/metrics.
json` (`HARD_PASS`, confirming the Stage-0 ingest landing PROGRESS.md/prior notes describe).

---

## HEADLINE

**The consumer-first work done 07-05/07-07 was correctly scoped to "don't build orphans NOW" — this
forward pass shows it under-states how close Stage 3->4 already is to needing the shelved pile, and
reveals that the "on-hold" toolkit is not a clean monolith: two of its three flavors of
"neuromodulation" and one of its two "cerebellum" targets have ALREADY been quietly built under
different cortex-primitive names (M1.3 NoiseChannel = stochastic-coupling/generation-control;
cfrpe = dopamine-RPE training signal; the basal-ganglia gate itself graduated from MISSING to
PROVEN-BUILT in the 2 days between the 07-05 inventory and the 07-07 re-audit). Of the four
components genuinely still idle (thalamic dynamic routing, cortical microcircuit / predictive
coding, CLS-interference-avoidance, ACh-uncertainty-gain), Stage 4 (conversational multi-turn
dialogue) is precisely the load that would finally activate THREE of them — thalamic routing
(multi-subsystem arbitration across a live dialogue), full N-way basal-ganglia action-selection
(not just binary Go/NoGo), and a second cerebellar consumer (multi-turn dialogue-strategy horizon
degradation, mechanistically the same shape as the already-identified Stage-3 gate-depth
degradation). The FOURTH — cortical microcircuit / predictive coding — is the one piece of the
on-hold pile that Stage 4 does NOT appear to need: the hierarchical-generation function it would
have served is already being met by a structurally different, already-proven mechanism (the
frame-slot/Levelt block-local resonator decoder, CHAIN_GRADE, exact-ordered 1.000), so this
component may be permanently retirable from the toolkit rather than merely deferred. On Stage 1: the
~12% gap is NOT a hidden capability hole — one clean housekeeping demotion (Probes 1/6/7/8, now
corrected with a properly-paired replacement that HARD_PASSED), one cheap unclaimed loose end
(`exp_n8_conceptnet_ingest_eval_v1`, pre-registered + smoke-passed, never dispatched), one
non-load-bearing long-tail item (CRT grid-cell code, smoke-only n=1), and exactly ONE genuinely
load-bearing item worth shoring up before Stage 4 matures: the refuse-gate's measured need to
upgrade from a 1D (sigma-only) to a 2D (alpha, sigma) joint-surface controller — because refuse-gate
IS M3 capability block 5 (self-knowledge primitive), which directly gates the M3 conversational
milestone Stage 4 is embedded in.**

---

## 1. STAGE x COMPONENT forward map

Columns: the FUNCTION each stage needs (not the anatomical label), the brain component that
supplies it, its BUILT/PARTIAL/MISSING status, and the referent.

### Stage 1 — Foundational primitives (~88% mature per PROGRESS.md, 2026-06-30 ladder)

| Function needed | Brain component | Status | Referent |
|---|---|---|---|
| Bind/unbind, superposition | HRR/FHRR/BSC bind+unbind | **BUILT** | PROGRESS.md Stage-1 primitive list |
| Pattern completion / attractor cleanup | CA3 regenerative cleanup | **BUILT — strong** | `regen_d5 ~0.70 vs analog ~0.10`, gap widens with load (07-05 inventory row 2) |
| Pattern separation / hub-collision protection | Hippocampal DG-CA3 index protection | **BUILT — strong** | hub-deg5+ recall `0.261->0.727`, matches Clarkson-Ubaru-Yang O(K^2) theory (07-05 inventory row 1) |
| Sequential/positional binding | Sequence binding K-cliff | **BUILT** | PROGRESS.md Stage-1 list |
| Short buffering across a few items | WM multi-bank | **BUILT** | PROGRESS.md Stage-1 list |
| Fabrication-refusal / confidence boundary | Refuse-gate V_REL=256 | **BUILT — but 1D, upgrade identified** | CG at 1D-on-sigma; Dim-T joint-surface finding: sigma_crit shifts 0.069 between alpha=0.10 and alpha=0.45 (2.3x margin) -> **needs 2D (alpha,sigma) controller** (`session_synthesis_M3_architecture_readiness_2026-07-02.md` item 6) |
| Real-world fact storage/retrieval | KG ingest FB15k/CN/HotpotQA | **BUILT, live** | Stage-0 ingest FULL HARD_PASS today (`exp_ingest_knowledge_integration_verify_v1`, completeness 142219/142219 exact) |
| Addressing at scale | Partition routing M=10M | **BUILT** | PROGRESS.md Stage-1 list |
| Query classification | Intent classifier | **BUILT** | PROGRESS.md Stage-1 list; reused directly by M3 router M1.1 |
| Capacity/multi-bank scaling | Capacity multi-bank alpha-K | **BUILT** | PROGRESS.md Stage-1 list |
| Action execution independent of position | Action-at-any-position | **BUILT** | PROGRESS.md Stage-1 list |
| Modular/grid-like composition | Entorhinal grid / CRT block-local | **PARTIAL — smoke only, n=1 seed** | `crt_multi_scale_grid_cell_composition_v1`, PROT-021 multi-seed not yet met (07-05 inventory row 5) |

**Inference vs documented:** the BUILT rows above are documented (PROGRESS.md + cited cell metrics).
The mapping of "refuse-gate" to a proto-basal-ganglia/proto-thalamic "stop" function is Director's own
functional inference, not a literature-asserted mapping — flagged, not load-bearing to the conclusion.

### Stage 2 — Meta-primitives + optimization (~85% mature)

| Function needed | Brain component | Status | Referent |
|---|---|---|---|
| Category/family generalization | Schema family CG | **BUILT** | PROGRESS.md Stage-2 list |
| Memory-strength decay over time | ANCHOR 4 time-decay | **BUILT** | PROGRESS.md Stage-2 list |
| Stabilization of learned associations | Lock-in amp | **BUILT** | PROGRESS.md Stage-2 list |
| Abstraction / coarse-graining | ANCHOR 3 coarse-grain | **BUILT** | PROGRESS.md Stage-2 list |
| Hierarchical clustering of memory | ULTRAMETRIC | **BUILT** | PROGRESS.md Stage-2 list |
| Frequency-weighted routing | Compose-freq routing v5 | **BUILT** | PROGRESS.md Stage-2 list |
| Offline consolidation / replay | NREM replay (compartmentalized cortex K-banks) | **BUILT** | Cell C v2 HARD_PASS at K=200, covers 92% of bottleneck gap (PROGRESS.md 06-30) |
| Structural/schema generalization (TEM-style: does content transform consistently with structure) | Schema-formation / TEM | **PARTIAL — real frontier, not sufficient** | MIDDLE_BAND real-minus-shuffled `0.05-0.13`, under-parameterized not walled (07-05 inventory row 6) |
| Interference-avoidance in a shared store (classic CLS) | CLS dual-W fast/slow | **TESTED, NO consumer for THIS half** | 2 HARD_FAIL/MIDDLE_BAND cells against a superposed decaying substrate; the actually-shipped Stage-0-2 ingest pipeline is a discrete graph-store write with structurally nothing to interfere (today's ingest-CLS drill, Section 2a) |
| Hierarchical predictive generation | Cortical microcircuit / FEP | **TRIED — narrow HARD_FAIL x2** | bigram `-0.789 nats`, trigram `-1.019 nats`, 3/3 seeds (07-05 inventory row 12) |

**Stage-2 gap, forward-looking:** schema-formation/TEM is real but not yet sufficient — this is the
one Stage-2 item genuinely still open and it feeds forward into BOTH Stage-3 compositional
generalization AND Stage-4's relation-vocabulary-growth question (Item 3 below).

### Stage 3 — Capability primitives (~60% banked)

| Function needed | Brain component | Status | Referent |
|---|---|---|---|
| Deep multi-hop reasoning | Hippocampal recall + CA3 cleanup (reused from Stage 1) | **BUILT, strengthened by ingest** | multi-hop depth-15 CG; ingest's 2-hop composition (`A_ingest_2hop=1.0`) rides on the same primitive at real corpus scale |
| Compositional generation | Compositional generation lift | **BUILT** | PROGRESS.md Stage-3 list |
| Cross-modal binding | Cross-modal binding | **BUILT** | PROGRESS.md Stage-3 list |
| Counterfactual value / regret signal | CF regret vmPFC | **BUILT** | PROGRESS.md Stage-3 list |
| In-context task induction | TASK_VECTOR HRR ICL K-cliff | **BUILT** | PROGRESS.md Stage-3 list |
| Goal-conditioned control / instruction-following (binary Go/NoGo) | Basal ganglia proper (trained Go/NoGo + RPE) | **BUILT — PROVEN this arc** | `exp_pfc_gate_cfrpe_trained_v2`, HARD_PASS, `gonogo_lift=0.600` at d4, `closure=0.661` (verified off-disk this cycle). Graduated from MISSING (07-05) to HAVE within 2 days — the fastest-moving row in this whole map. |
| Reward-prediction-error training signal | Neuromodulation — dopamine RPE (cfrpe) | **BUILT, feeds BG gate above** | same cell; context-dependent elsewhere (HARD_PASS arch-ablation +0.683 nats / HARD_FAIL weighted-replay) |
| Extending gate reliability beyond depth-4 | Cerebellar forward-model (anticipatory) | **MISSING but spec'd, top recommended next build** | `gonogo_lift` collapses 0.653 (d4) -> 0.075 (d6); SR-rollout lever fully spec'd, P_deflated 0.20-0.28, not yet dispatched (07-07 consumer-ranking note) |
| Theory-of-mind / narrative comprehension | Multi-structure-bio (ToM, narrative) | **IN FLIGHT** | ToM 3rd+ v5 d=5-isolated smoke confirms dilution hypothesis; FULL pending (PROGRESS.md 06-30) |
| Dynamic arbitration across many live subsystems | Thalamic dynamic routing hub | **MISSING — correctly shelved, no consumer yet** | current inter-module bridge is static plumbing; "nothing in the ingest pipeline creates dynamic multi-subsystem traffic for a thalamic gate to arbitrate" (today's ingest-CLS drill, row 6) |

**Stage-3 gap, forward-looking:** the cerebellar forward-model target is the single item most likely
to be built NEXT (already spec'd, cheap CPU smoke, reuses `train_sr_transport`) — not because it's a
missing brain part in the abstract, but because it's the measured scope-gap of an ALREADY-SHIPPED
mechanism (basal-ganglia gate). Thalamic routing remains correctly un-built because Stage 3 itself
still has no dynamic multi-subsystem traffic — see Stage 4 below for where that changes.

### Stage 4 — LM equivalence (DEFERRED, 0% progress per `project_glass_box_LLM_..._2026-07-01`;
the M3 cortex layer is the enabling scaffold running in parallel, NOT Stage 4 itself)

This is where the forward-vs-consumer-first framings diverge most. See Section 2 for the detailed
function-by-function reasoning; table below is the summary.

| Function Stage 4 needs | Nearest on-hold brain component | Forward verdict |
|---|---|---|
| Sequential/hierarchical language generation | Cortical microcircuit / predictive coding | **LIKELY NOT NEEDED** — function already met by frame-slot resonator decoder (HAVE-strong, Stage-1/M3), a structurally different mechanism than predictive coding, which has 2x narrow HARD_FAIL on its own terms |
| Multi-turn context/attention routing across many live subsystems | Thalamic dynamic routing hub | **CONFIRMED — this is the load that's been missing.** M3's M1.6 attention-router (static 4-class classifier, HAVE-strong) is a necessary but not sufficient proto-version |
| Action-selection among MANY candidate response strategies (not binary) | Basal ganglia (extend Go/NoGo to N-way) | **CONFIRMED, as an EXTENSION of an already-built primitive**, not a new component |
| Generation-time confidence/exploration control | Neuromodulation — stochastic-coupling / "arousal" tone | **ALREADY BUILT, under a different name** — M1.3 NoiseChannel (cortex-injected calibrated noise), CG, already the substrate-appropriate analog of this function |
| Uncertainty-gated learning-rate / attention gain | Neuromodulation — ACh-style uncertainty gain | **GENUINELY OPEN, not yet load-bearing** — flagged in the 07-07 consumer-ranking note as "my own speculative extension... untested, not recommended now" |
| Multi-turn strategic horizon (which conversational move to commit to several turns ahead) | Cerebellar forward-model (SECOND consumer) | **PLAUSIBLE, mechanistically identical shape to the Stage-3 gate-depth problem** — not yet named as a Stage-4 consumer anywhere on disk; this note is the first place that connects them (see Section 2) |
| Open-corpus relation-type discovery (once ingest moves past curated schemas) | CLS schema-extraction half | **CONFIRMED, already staged** (Stage-4 of the INGEST sub-arc specifically, not the whole-system Stage-4) — see caution below on stage-numbering collision |

**IMPORTANT naming caution:** "Stage 4" in PROGRESS.md's system-wide ladder (LM equivalence) and
"Stage 4" in the ingest sub-arc's own internal staging (`research_ingest_arc_scoping_staged_plan_
2026-07-07.md`, its own Stages 0-4) are TWO DIFFERENT NUMBERING SCHEMES that happen to share a
number. The ingest sub-arc's "Stage 4" (neocortical-analog consolidation loop / relation-vocabulary
growth) is a sub-stage of overall system Stage 1-2 work (ingest is a Stage-1/2-ish capability), not
the system-wide Stage-4 LM-equivalence milestone. Do not conflate them in future notes — flagging
explicitly since the pointer materials for this drill used "Stage 4" in both senses.

---

## 2. STAGE 4 SPECIFICALLY — does the on-hold pile equal Stage 4's toolkit?

**Answer: PARTIAL CONFIRM.** Reasoning from function, not name:

**(a) Sequential generation.** Stage 4 needs the substrate to produce multi-word, structured output.
The brain-mechanism most naturally NAMED for this (cortical hierarchical predictive coding /
Rao-Ballard / Bastos canonical microcircuits) has already been tried twice in this project and
narrowly HARD-FAILed both times (bigram -0.789 nats, trigram -1.019 nats, 3/3 seeds). But the
FUNCTION — producing correctly-ordered multi-slot structure — already has a working substrate-native
mechanism that is NOT predictive coding: the Levelt frame-slot block-local resonator decoder, HAVE
strong, CHAIN_GRADE, exact-ordered 1.000 on native GSBC fillers. This is the clearest case in the
whole map of the mechanism-analog trap running in REVERSE: the component whose NAME matches best
(cortical microcircuit) is not what's doing the job; a component whose name sounds less obviously
relevant (hippocampal/entorhinal-style block-local decoding) already does it. **Recommendation:
Stage 4's generation work should scale up frame-slot decoding to open-vocabulary dialogue, not
resurrect cortical-microcircuit predictive coding.**

**(b) Context/attention routing.** Stage 4 conversational dialogue is, by construction, the first
point in the whole stage ladder where MANY subsystems must be arbitrated simultaneously and
dynamically per turn: working-memory context (M1.5 two-tier STM/LTM), self-knowledge/refuse-gate
(M1.4), the attention-router's op-classification (M1.6), CLARIFY (M1.8), plus live KG retrieval — all
competing for "what does this turn actually need." This is EXACTLY the "dynamic multi-subsystem
traffic" that every prior audit (07-05, both 07-07 passes) found absent and used to justify shelving
thalamic dynamic routing. **This confirms the on-hold pile's central prediction: thalamic routing's
consumer arrives specifically at Stage 4, not before.** The current M1.6 attention-router is real
groundwork (proves content-based classification works) but is a STATIC per-query 4-class classifier,
not a stateful arbiter across a live multi-turn dialogue with several concurrently-active subsystems
— extending it into that shape IS the concrete Stage-4 thalamic-routing work item, not a fresh build
from zero.

**(c) Action-selection among many candidates.** The basal-ganglia gate currently does binary Go/NoGo
(HARD_PASS at d4). Stage 4 needs the same underlying mechanism (RPE-trained competitive gating) to
arbitrate among N candidate response strategies (answer / clarify / refuse / ask-follow-up /
ingest-new-fact / self-explain — mapping directly onto the 10 M3 demo properties). This is a
genuine, confirmed Stage-4 need, but it is explicitly an EXTENSION of an already-working component,
not a build-from-scratch of a missing one — the on-hold-pile framing ("basal ganglia proper" as a
missing component) is now STALE; the component exists, what's missing is only its N-way scope.

**(d) Generation control / neuromodulation.** This is the most interesting partial-confirm/refute
case. Two of the three neuromodulation flavors this project has separately tracked are ALREADY BUILT:
(i) the dopamine-RPE training-signal flavor (cfrpe) already trains the basal-ganglia gate; (ii) the
arousal/NE-style "stochastic coupling at the decision boundary" flavor is EXACTLY what M1.3
NoiseChannel already provides (regime-dependent sigma/temperature injected at the cortex/substrate
boundary, CG-status per the 2026-07-02 architecture-readiness synthesis) — this is a direct,
already-shipped answer to "how does Stage 4 control generation-time confidence/exploration," even
though nobody has previously connected M1.3 to the "neuromodulation" brain-component line item in the
consumer-ranking notes. Only the THIRD flavor (ACh-style uncertainty-gated learning-rate / attention
gain) remains genuinely unbuilt and unconsumed — correctly flagged in the 07-07 note as speculative,
not yet load-bearing.

**(e) Cerebellar forward-model, a SECOND consumer.** The 07-07 consumer-ranking note names exactly
one cerebellum consumer: the Stage-3 basal-ganglia gate's d4->d6 depth-degradation. This forward
pass adds a second, not previously connected: Stage-4 multi-turn dialogue strategy has the same
SHAPE of problem — deciding which conversational move to commit to now, several turns before its
payoff is known, is structurally identical to the gate's "commit now, degrade by depth" problem, just
at the turn-level instead of the hop-level. If the SR-rollout-based anticipatory-bias mechanism
(already spec'd for the Stage-3 target) works, it is very likely portable to Stage-4's turn-level
horizon problem with no new representational machinery — a second, free consumer for the same build.
This is Director's own forward inference (not evidenced on disk anywhere yet) — flagged as such, not
claimed as verified.

**(f) CLS.** The interference-avoidance half of CLS is REFUTED as a toolkit member for the
system-wide Stage 4 (the shipped architecture structurally does not have shared-weight interference
to prevent, confirmed by two independent external lit-scans plus 3 internal cells). The
schema-extraction half survives, but under a DIFFERENT name and a DIFFERENT numbering (the ingest
sub-arc's own internal "Stage 4," which sits inside the system's Stage 1-2, not the system-wide
LM-equivalence Stage 4) — do not carry this forward as "Stage 4 needs CLS."

**Bottom line on Q2:** the on-hold pile is NOT a clean 1:1 match to Stage 4's toolkit. Confirmed:
thalamic routing (strongest match), N-way basal-ganglia extension, a second cerebellum consumer
(inferred, not yet evidenced). Refuted or already-resolved-elsewhere: cortical microcircuit (wrong
mechanism for the job; frame-slot decoding already does it), CLS-interference (structurally
unneeded), two of three neuromodulation flavors (already built under cortex-primitive names, not
waiting on the shelf). Genuinely still open and untouched: ACh-style uncertainty gain.

---

## 3. STAGE 1 GAP — what is the missing ~12%?

Four items surface when the 12-primitive Stage-1 list is cross-checked against everything found this
cycle. Classified per the task's own (a)/(b)/(c) scheme:

**(a) Demoted-artifact housekeeping — correctly removed, NOT a hole.** The mechanism-moderation
cross-term family (Probes 1/6/7/8, including the Probe-1 CG_META claim) was demoted 4/4 as
unpaired-sampling artifacts — the underlying mechanisms were argmax-readout-degenerate
(bit-identical outputs across the compared arms), so the original "finding" was a measurement
artifact, not a real capability claim being walked back. PROGRESS.md is explicit that MAIN-EFFECT
laws (storage 0.93, scale-free, M-scaling, N x L additive) stand unaffected. The correction produced
a positive byproduct: a genuine PAIRED replacement (`probe_18`, storage-advantage boundary scales
with N, cv=1%) landed HARD_PASS, and the paired-trials-mandatory-for-arm-comparison discipline was
filed as a standing methodology rule. **This item should not be read as "12% missing capability" —
it is closed, correctly, with a stronger replacement already in hand.**

**(b) Non-load-bearing long-tail coverage — real but low-priority.**
- CRT block-local modular composition (entorhinal-grid-style): algebraically exact but only
  smoke-tested at n=1 seed; PROT-021 multi-seed discipline not yet satisfied. No known consumer is
  currently blocked on this (grid-cell-style composition is a "nice to formalize," not something any
  downstream stage currently calls). Recommend: pick up opportunistically (cheap, 2-3 more seeds), no
  urgency.
- `exp_n8_conceptnet_ingest_eval_v1`: pre-registered 2026-06-22, smoke already HARD_PASS at M=5k,
  confirmed via status_log grep still never dispatched as of 2026-07-07 (`research_ingest_arc_
  scoping_staged_plan_2026-07-07.md`, Item 2). Zero design cost, zero blocking dependency — this is
  the single cheapest loose end in the whole Stage-1/2 boundary and should be picked up in the next
  ingest-track cycle regardless of this drill's other conclusions.
- The NEG1 (N x depth cross-term near-capacity) follow-up flagged in `research_stage1_regime_map_
  4negatives_2026-07-03.md`: an open, real, but explicitly diagnostic/parameter-fitting question
  ("the substrate's job is to locate its own operating constants within known theoretical shapes, not
  discover new shapes" — that note's own framing). Not load-bearing for any stage transition.

**(c) Genuine load-bearing gap — recommend shoring up before Stage 4.** The refuse-gate's measured
need to upgrade from a 1D (sigma-only) controller to a 2D (alpha, sigma) joint-surface controller.
This is qualitatively different from (a) and (b) because refuse-gate is not an isolated diagnostic —
it IS M3 capability block 5 ("self-knowledge primitive: refuse-gate + META v4 extended"), which the
M3 milestone plan lists as a hard dependency for the glass-box conversational demo, and the M3 demo
IS the vehicle that eventually leads into system-wide Stage 4. The `Dim T` joint-surface finding
(`session_synthesis_M3_architecture_readiness_2026-07-02.md`, item 6) shows sigma_crit shifts by
0.069 between alpha=0.10 and alpha=0.45 (a 2.3x margin) — meaning the CURRENT 1D refuse-gate is
tuned correctly for only ONE point on a 2D surface, and Stage 3/4 workloads (multi-hop composition,
longer dialogue context) will naturally sweep alpha across a wider range than Stage-1/2 workloads
did. The fix is already scoped (smoke HARD_PASS exists; FULL pending) — this is cheap, not
speculative, and unlike the cerebellum/thalamus builds above, it extends a primitive Stage 1 itself
already depends on, rather than adding new machinery for a not-yet-arrived stage.

**Recommendation, concretely:** (a) no action; (b) opportunistic, not urgent — dispatch
`exp_n8_conceptnet_ingest_eval_v1` next ingest cycle (near-zero cost), defer CRT grid-cell multi-seed
indefinitely until a consumer appears; (c) **shore up now** — author the refuse-gate 2D
(alpha, sigma) joint-controller FULL cell before M3's capability-block-5 (self-knowledge) work
matures further, since every additional cell built on top of the current 1D refuse-gate inherits its
narrow operating point.

---

## Cheap decisive test

Not applicable in the cell-dispatch sense (this is a planning artifact). The nearest equivalent
"cheap decisive test" per component:

1. **Refuse-gate 2D upgrade** (Stage-1 gap, category c): dispatch the already-scoped FULL cell for
   the (alpha, sigma) joint-surface controller (smoke already HARD_PASS per the 07-02 synthesis;
   seeds 13/19 were queued remote_cpu as of that note — verify current queue state before
   re-dispatching). HARD-PASS: joint controller matches or beats the two single-alpha operating
   points' individual sigma_crit values simultaneously, cross-seed cv<0.10. HARD-FAIL: joint
   controller cannot beat picking the better of the two 1D controllers per-regime (would mean the
   1D gate is already adequate and this is not, in fact, load-bearing).
2. **Cerebellar SR-rollout** (Stage-3 top-pick, already spec'd in the 07-07 consumer-ranking note):
   unchanged from that note's own design — 3-arm CPU smoke, `GONOGO_SR_ROLLOUT_ANTICIPATORY` vs
   `NO_CORRECTION` vs `FEEDBACK_ONLY_REACTIVE`.
3. **N8 ConceptNet dispatch** (Stage-1 gap, category b): trivial dispatch of an already-smoke-passed
   pre-registered cell, no new test design needed.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Claim under test 1: "the on-hold brain-component pile substantially overlaps Stage 4's real
needs, once Stage 4 actually arrives."**
- **HARD-PASS:** when Stage 4 work begins, thalamic-routing-style dynamic arbitration and N-way
  basal-ganglia action-selection are both required within the first 2-3 M3-capability-block cells
  authored (matching this note's prediction).
- **HARD-FAIL:** Stage 4 work proceeds through several cycles using only extensions of ALREADY-BUILT
  primitives (frame-slot decoding, M1.6 router, cfrpe-trained gate) with no genuine need for a new
  dynamic-arbitration or N-way-selection mechanism — would mean this note over-predicted the
  toolkit-match.
- P(claim holds) undeflated ~0.55 (functional reasoning from a real architectural bottleneck —
  many concurrent live subsystems per turn — but no direct Stage-4 cell has been built yet to
  confirm it) -> **P_deflated ~0.35** (novel-synthesis: connecting Stage-4's dialogue-arbitration
  need to the specific "thalamic routing" brain-component label is this project's own synthesis, not
  literature-precedented for THIS substrate).

**Claim under test 2: "cortical microcircuit / predictive coding is permanently unneeded, not merely
deferred, because frame-slot decoding already fills its Stage-4 function."**
- **HARD-PASS:** Stage-4 generation work scales frame-slot decoding to open-vocabulary/multi-sentence
  output without requiring any predictive-coding-style hierarchical mechanism.
- **HARD-FAIL:** frame-slot decoding hits a genuine ceiling at open-vocabulary scale (e.g. cannot
  handle variable-length nested structure) and a hierarchical predictive mechanism becomes necessary
  after all.
- P(claim holds) undeflated ~0.45 (frame-slot decoding is proven only on a bounded, closed-vocabulary
  block-local task; open-vocabulary dialogue is a real scale-up, not yet tested) -> **P_deflated
  ~0.25**, reflecting real uncertainty about whether the two mechanisms are truly substitutable at
  Stage-4 scale rather than only within the narrow regime both have been tested in so far.

**Claim under test 3: "Stage 1's ~12% gap contains exactly one load-bearing item (refuse-gate 2D
upgrade) and nothing else."**
- **HARD-PASS:** the refuse-gate 2D joint-controller FULL cell closes cleanly (per test 1 above) and
  no other Stage-1 primitive surfaces a load-bearing gap when Stage 3/4 work stresses it further.
- **HARD-FAIL:** a DIFFERENT Stage-1 primitive (not refuse-gate) turns out to break under Stage-3/4
  load conditions not yet tested (e.g. the CRT grid-cell code, dismissed here as long-tail, turns out
  to matter once compositional depth increases further).
- P_deflated ~0.40 (moderate confidence; the inventory scoured here is thorough but Stage 3/4 has not
  yet stress-tested Stage-1 primitives under conditions that would reveal a currently-invisible gap).

---

## Cross-thread synthesis

- Directly extends (does not repeat) `research_thrust_brain_component_inventory_and_build_priorities_
  2026-07-05.md` (original 17-component inventory), `research_brain_component_consumer_ranking_
  cerebellum_control_depth_2026-07-07.md` (5-candidate consumer audit, cerebellum target-B top pick),
  and `research_brain_structure_consumer_remap_post_ingest_live_2026-07-07.md` (6-candidate
  re-ranking post-ingest-Stage-0, CLS split-verdict). This note's contribution is the FORWARD
  reframing those three explicitly avoided (by design, per the "don't build orphans now" discipline)
  — it does not overturn any of their CURRENT-consumer verdicts, only extrapolates which currently-
  absent consumers arrive WHEN Stage 4 does.
- Uses `research_stage1_regime_map_4negatives_2026-07-03.md` for the Stage-1 NEG1-4 lit-grounding and
  the paired-trials discipline's origin story.
- Uses `research_ingest_arc_scoping_staged_plan_2026-07-07.md` for the ingest sub-arc's OWN internal
  "Stage 4" (relation-vocabulary growth) — explicitly flagged in Section 1 as a DIFFERENT numbering
  scheme from the system-wide Stage 1-4 ladder, to prevent a conflation error in future notes.
  M3 architecture grounding from `director_M3_M1_3_stochastic_noise_injection_design_spec_2026-07-01.
  md` (NoiseChannel design) and `session_synthesis_M3_architecture_readiness_2026-07-02.md`
  (cortex-primitive CG status table, Dim-T refuse-gate finding).
- Milestone framing from `project_M3_M4_milestones_glass_box_conversational_agentic_USER_2026-06-26.
  md` and `project_glass_box_LLM_substrate_native_language_no_external_LLM_USER_LOCKED_2026-07-01.md`
  (Stage 4 = the actual deferred endpoint, not skipped; M3 cortex layer is the enabling scaffold, not
  Stage 4 itself).
- New this cycle, not previously connected anywhere on disk: (i) M1.3 NoiseChannel as the already-
  built answer to the "neuromodulation for generation control" line item; (ii) a second, inferred
  (not yet evidenced) cerebellum consumer at the Stage-4 multi-turn-horizon level; (iii) the explicit
  naming collision between system-wide Stage 4 and the ingest sub-arc's internal Stage 4.

## Substrate-product implications

For the glass-box narrative: this map lets Director say, honestly, "we know which brain-inspired
mechanisms Stage 4 will need before we build them, and two of the three neuromodulation-flavored
needs are already met by cortex primitives we built for other reasons" — a stronger, more
disciplined claim than either (a) building the on-hold pile speculatively now (repeating the
thalamic-router mistake the 07-05/07-07 notes were explicitly designed to avoid) or (b) treating the
consumer-first "no build now" verdict as permanent rather than staged. It also gives a concrete,
cheap, non-speculative next action (refuse-gate 2D upgrade) that shores up Stage 1 exactly where a
real dependency chain (Stage 1 primitive -> M3 capability block 5 -> Stage 4 milestone) exists,
rather than treating "Stage 1 is 88%" as a number to close for its own sake.

## Citations (verified count: 0 new external sources this cycle — internal-corpus planning synthesis
per task scope; all brain-science citations underlying the component classifications are carried,
not re-verified, from the source notes named in Cross-thread synthesis above, per 2x-drill
discipline. Two internal figures re-verified off-disk directly this cycle, per Fix#28, listed in the
preamble.)
