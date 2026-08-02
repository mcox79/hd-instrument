# Contextual-stream situation-model WM: SOR task + cheapest can-fail first probe (2026-08-01)

Director build-ready spec. The NEXT comprehension layer after the now-validated interactive
extraction (which resolves WHO-DID-WHAT per clause: McGuffey quotative 0.895 / by-agent passive 1.0,
atoms 29605/29606, commit 9a901e51d). This layer maintains the ENTITY/SITUATION STATE ACROSS
clauses as a stream is read: introduce entities, bind per-clause roles, and UPDATE state
content-gated (overwrite on new info, recall on re-mention, allocate on novel). CPU, Probe-1 cost
class, measurement-first, one-variable. NOT the big build.

Calibration: CITED@ = underlying brain/ML finding; REASONED@ = transfer. ESTABLISHED/CONTESTED
per claim. P deflated; novel-synthesis capped 0.50.

KB-check: heavy director_kb_query NOT re-run (box CPU-thrashed, per coordinator). Bounded
`ls experiments/ | grep sor/overwrite/selective/contextual_stream` = NO existing SOR cell (genuinely
new). Grounding = direct read of `wm_value_regime_and_contextual_stream_design_2026-07-30.md` (the
pre-planned design, which itself synthesized 3 cited lit-scans) + `hdlab/slot_attention_wm.py` (the
proven organ, read end-to-end this session). This spec turns that design into a build-ready cheap
probe; the SOR construction + architecture are from the pre-planned doc, the probe bands + brain-
metric + can-fail hardening protocol are the new content.

---

## THE PROVEN ORGAN TO REUSE (confirmed on disk)
`hdlab/slot_attention_wm.py::SlotAttentionWM` (atom 29592 situation-model loop) ALREADY implements
every mechanism SOR needs:
- **Content-addressed slot routing:** `addr_net` scores each slot from [entity_filler, slot_k],
  temperature-sharpened softmax ACROSS slots -> routes an event to the slot for the entity it is
  about (NOT position). = the ALLOCATE/OVERWRITE/RECALL router.
- **PBWM PE-gated bistable write:** `boundary_k = sigmoid((surprise_k - write_theta)/tau)` x
  `gate_mod`; `new_slots = (1-w)*slots + w*candidate` -> at w~1 this is REPLACE (overwrite-with-
  suppression of prior content), at w~0 it HOLDS (recall unaffected). Annealed soft->sharp.
- **HRR role-binding + recall:** `candidate = bind(key, clause_rep)`; `readback = unbind(slots, key)`
  -> content-keyed store + recall.
So SOR is a NEW TASK + NEW READOUT on an EXISTING organ, not a new mechanism. What is genuinely new:
(1) the SOR stream task; (2) a "query slot_id -> return most-recently-written filler" readout head;
(3) the reservoir/random-init OFF arm; (4) the can-fail hardening protocol (below).

---

## 1. THE SOR (Selective-Overwrite-Recall) CAN-FAIL TASK
**Construction (oracle-vector, CHEAPEST first-probe form -- prove the mechanism before real text):**
A stream of events. Each event = an oracle `(slot_id_vec, filler_vec)` pair drawn from small
discrete vocabularies (`|SLOT_IDS| = 6` target entities, `|FILLERS| = 20`), each vocab item a fixed
random FHRR unit vector (identity only, NO semantics -- own-mechanism, like probe1).
- Per stream: interleave the 6 target-slot assignment events with `D` DISTRACTOR slot-touches
  (D >> #slots, e.g. 30+), so no fixed attention window covers all relevant touches.
- RANDOMIZE per-example ordering/spacing so NO fixed position predicts any binding (position-blind).
- Each target slot is touched MULTIPLE times with DIFFERENT fillers (re-assignment / overwrite).
- At stream end: query one `slot_id` and require its **MOST-RECENTLY-WRITTEN filler** (the last
  overwrite, NOT the first, NOT an average). This is what forces OVERWRITE-WITH-SUPPRESSION.

**Metric:** query-recall accuracy = fraction of streams where the readout's returned filler ==
the most-recently-written filler for the queried slot_id (nearest-neighbour in FILLERS, or exact-id
match). Chance = 1/|FILLERS| = 0.05.

**Why random-init/reservoir PROVABLY fails (the can-fail argument, CITED@):** SOR requires
CONTENT-DEPENDENT routing (write to the slot matching slot_id) AND last-write-wins suppression. A
fixed random-dynamics reservoir superimposes/averages successive writes to the same slot and cannot
SELECT the most-recent -- Gu&Dao 2023 Mamba selective-copying: non-selective S4 ~57% vs selective S6
~99.8% (ESTABLISHED). **HONEST NUANCE (this is the weakest link, below):** reservoirs/echo-state
nets are SPECIFICALLY good at preserving RECENT inputs decodably, so a trained linear readout on a
random-init reservoir could shortcut "return the most-recent thing" UNLESS the task forces
untangling of MULTIPLE same-slot overwrites amid heavy distractors -- which is exactly what the
multi-overwrite + high-D construction is engineered to defeat. The floor-must-fail is therefore a
NON-TRIVIAL, EMPIRICALLY-VERIFIED calibration, not an assumption.

---

## 2. THE CONTEXTUAL-STREAM WM WIRING (glass-box; new vs reused)
Per the pre-planned design (fixes the clause-blind 0.50 bug), for the REAL-TEXT version later:
1. ONE shared encoder pass over the whole passage -> contextualized `[B,L,d]` (each token attended
   to the others). [REUSED encoder; later step.]
2. SLICE at clause/event boundaries -> per-clause reps that each carry cross-clause context.
   [The interactive extraction cell `exp_interactive_loop_real_gold_mcguffey_v1` supplies the
   per-clause role-resolved fillers here.]
3. Feed slices SEQUENTIALLY into `SlotAttentionWM.run_clause_stream()` -> content-gated entity WM
   with overwrite-with-suppression + HRR recall. [REUSED organ.]

**For the FIRST PROBE we test step 3 in ISOLATION on oracle vectors** (no encoder, no real text):
feed the SOR `(slot_id_vec, filler_vec)` stream directly as `clause_reps`/`tok_reps` into
`SlotAttentionWM`, add the query-recall readout. This proves the WM MECHANISM before wiring the
shared-pass encoder (steps 1-2), exactly as probe1 proved the interactive loop on oracle vectors
first. **Genuinely new in the probe:** SOR stream generator, query-recall readout head, OFF/reservoir
arm, hardening protocol. **Reused:** the entire SlotAttentionWM gate/router/binding.

---

## 3. CHEAP CAN-FAIL FIRST PROBE
**ONE VARIABLE: content-gated WM ON vs OFF.**
- **ARM_OFF (reservoir / no content-gating):** random-init frozen `SlotAttentionWM` (addr_net,
  gate_net, write_theta NOT trained) + a TRAINED linear readout probe on the final slot states.
  Content-blind routing + un-tuned gate => superimposes, cannot select last-write.
- **ARM_ON (content-gated WM):** the SAME `SlotAttentionWM` TRAINED end-to-end (addr_net routes by
  slot_id content; gate learns overwrite-with-suppression; theta learns the write boundary) + the
  same readout.

**PRE-REGISTERED BANDS** (both seeds; chance = 0.05):
- **CAN-FAIL FLOOR (must hold or the task is reservoir-decodable -> HARDEN):** ARM_OFF recall
  accuracy <= **0.20** (near chance, <= chance + ~3x-chance margin). If OFF clears this, the
  echo-state readout is shortcutting -> increase D (distractors), increase same-slot overwrites, and
  re-verify OFF fails BEFORE trusting any ON result. This hardening loop is done in SMOKE against the
  FLOOR only (honest, pre-registered use of a smoke loop -- harden until the reservoir fails, never
  tune against the ON number).
- **HARD-PASS (ARM_ON):** recall accuracy >= **0.75** (>= ~15x chance) AND >= ARM_OFF + **0.50** AND
  the BRAIN-METRIC (below) holds. Both seeds.
- **MIDDLE/PARTIAL:** ARM_ON accuracy up but the brain-metric gating-dynamics do NOT show content-
  selective spiking -> got the answer by a shortcut, not the mechanism; distinct informative outcome.
- **HARD-FAIL:** ARM_ON <= ARM_OFF + 0.10 -> content-gating provides no lift; the honest refutation
  of the WM bet for this reachable regime (per the pre-planned doc's own falsification clause).

**CONTROLS:**
- **Reservoir floor** = the primary can-fail (ARM_OFF, above).
- **Shuffled-slot_id control:** feed the WM slot_ids DECORRELATED from fillers (shuffled) -> content-
  routing has nothing to key on -> MUST fail (~floor). Proves it is the slot_id CONTENT driving
  routing, not a spurious signal. (The SOR analogue of probe1's random-feedback placebo.)
- **Position-only probe:** predict the answer from position/order features alone -> MUST fail
  (task is position-randomized). Confirms content is REQUIRED.
- **Known-reader headroom (cite, do not build):** Mamba/S6 selective ~99.8% establishes the ceiling
  exists, so a HARD-FAIL indicts OUR mechanism, not task-impossibility.

**BRAIN-METRIC (judge the mechanism, not just accuracy):** reproduce content-gated overwrite/recall +
event-segmented update:
- **Overwrite spiking (SEM/EST update-at-discontinuity, Zacks):** mean write-gate `w` on NEW-INFO
  events (new filler for a known slot) >= **2x** mean `w` on RECALL/DISTRACTOR events. Update fires
  at the discontinuity, HOLDS otherwise -- not continuous averaging.
- **Routing consistency:** the same slot_id routes to the SAME slot across its touches (addr_w argmax
  stability) >= **0.80**; novel slot_id routes to a previously-unused slot (allocate).
These certify the answer came VIA content-gated overwrite-recall, not a readout shortcut. A model that
clears accuracy but fails the gating-dynamics is MIDDLE, not PASS.

**EST. COST:** CPU-minutes. n_slots=6-8, d_model=256, stream length ~40 events, |FILLERS|=20, a few
hundred training streams, few epochs, 2 seeds, all arms. Reuse SlotAttentionWM + the probe1 harness
scaffold (arm loop, per-(arm,seed)-unit checkpoint via `tools/exp_checkpoint.py`, atomic
`os.replace`, `_arms_must_differ` self-test, `decide_verdict`). Well under ~10 CPU-min.

---

## SINGLE WEAKEST LINK: making the task GENUINELY reservoir-failing (echo-state hardening)
The load-bearing risk is NOT whether the trained WM works -- it is whether the CAN-FAIL FLOOR
genuinely fails. Reservoir/echo-state networks are specifically good at preserving recent inputs in a
LINEARLY-DECODABLE subspace (that is what reservoir computing exploits), so a random-init WM + trained
linear readout could shortcut "return the most-recent filler" and the floor would NOT fail -> the
probe would be VACUOUS (ARM_ON beats nothing). The construction defeats this ONLY if it forces
untangling of MULTIPLE overwrites to the SAME slot amid heavy distractors (a linear readout of a
superimposing reservoir cannot separate the last same-slot write from the earlier ones it averaged
in). Therefore the floor-fails property MUST be EMPIRICALLY VERIFIED in smoke (increase D and
same-slot-overwrite count until ARM_OFF <= 0.20) BEFORE any ARM_ON number is trusted. If the task
CANNOT be made to fail the reservoir while staying trainable, then there is no reservoir-failing
regime here and that is the honest null on the WM bet -- report as such, do not force a pass.
Secondary risk: the ALLOCATE sub-mechanism -- pure content-addressing may mis-route a NOVEL slot_id to
an occupied slot without an explicit novelty signal; if allocate fails, SOR degrades ambiguously
(WM-bet-failed vs allocate-sub-mechanism-failed). Instrument allocate separately (routing-consistency
metric) so a failure is diagnosable, not conflated.

## NOT-CLEANLY-BRAIN-GROUNDED (honest)
- Content-gated PBWM write (O'Reilly&Frank 2006), event-segmented update-at-discontinuity (Zacks EST;
  Franklin/Gershman/Norman SEM 2020), content-addressed recall (Henaff EntNet 2017; hippocampal
  pattern-completion) -- these are BRAIN-TOPOLOGY, ESTABLISHED computational-neuroscience mechanisms.
- HRR bind/unbind for role-filler storage -- SUBSTRATE-NATIVE OP (VSA); brain-PLAUSIBLE (Eliasmith
  NEF) but the brain's actual bind is conjunctive/mixed-selectivity, not clean algebraic bind/unbind.
  "Brain-grounded PRINCIPLE (structured binding), substrate-native OPERATION."
- Overwrite-with-suppression via convex `(1-w)*slot + w*cand` -- the PRINCIPLE (overwrite suppresses
  prior, retroactive-interference/updating) is brain-grounded; the convex form is engineering.
- Oracle-vector slot_ids/fillers + the query-most-recent readout head -- PROBE SCAFFOLD, not brain
  claims (the mechanism proof; real-text streams via steps 1-2 come later).
- "Brain-foundational" applies to the WM TOPOLOGY (content-gated event-segmented entity state), not
  to every operation inside it.

## P_DEFLATED
**P_deflated (ARM_OFF genuinely fails + ARM_ON HARD-PASS + brain-metric gating-dynamics hold): 0.35.**
The organ is proven (atom 29592) and the task is designed to need exactly what it does, so ARM_ON
clearing accuracy is fairly likely IF the task calibrates. The drag is the weakest link: making the
reservoir genuinely fail while staying trainable is a real, non-trivial calibration (echo-state
recency decoding is a strong shortcut), and the allocate sub-mechanism adds risk. MIDDLE_PARTIAL
(ARM_ON accuracy up but gating-dynamics not clean, or floor only partially fails) is comparably likely
(~0.40), consistent with the program's first-attempt middle-band pattern. Novel-synthesis cap 0.50
respected.

## RECOMMENDED NEXT ACTION
Hand to `hdi_exp_dev` as `exp_contextual_stream_wm_sor_probe1_v1` (Tier-1 CPU, reuse probe1 harness +
SlotAttentionWM). SMOKE against the CAN-FAIL FLOOR first (harden D / same-slot overwrites until
ARM_OFF <= 0.20) -- VET that the reservoir genuinely fails BEFORE trusting any ARM_ON pass. Report
recall accuracy + the two brain-metric gating-dynamics + the shuffled-slot control, per arm/seed.
Verdict to USER before wiring the shared-pass encoder (steps 1-2) or any real-stream/scale build.
