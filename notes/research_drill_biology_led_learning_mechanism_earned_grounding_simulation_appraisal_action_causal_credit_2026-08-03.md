# Research drill: the brain-faithful LEARNING MECHANISM for the earned grounding-simulation
## (a) appraisal -> action-tendency  +  (b) causal-COHERENCE credit-assignment
### 2026-08-03, Director

Filed by: Director. Task: the USER-committed earned grounding-simulation build (design =
`notes/foundational_grounded_knowledge_layer_program_2026-08-03.md` section 2b; first can-fail
cell `a0b19793` running, NOT touched) uses **"error-driven update" as a PLACEHOLDER** for the
learning that EARNS (a) the appraisal->action-tendency mapping and (b) the causal-COHERENCE
attribution (which prior AGENT-action EXPLAINS the outcome — NOT recency; tonight's decisive
falsification, commit e34d54701). This drill pins the placeholder to a SPECIFIC brain-faithful
mechanism for each, applying the USER standing gate to EACH: (1) which brain STRUCTURE earns it?
(2) does it SHARE a process we already built -> REUSE the organ? Research only; no cells authored
or dispatched.

Lead with the biology. Leverage (cite, do not re-derive) tonight's three brain-drills + the
foundational design, all disk-verified below.

---

## 0. KB-check (dedup) + disk-verified prior art — the load-bearing finding

`bash tools/substrate_query.sh --chunk-content --schema-version v2 --tau 0.15 --k 5` run four times:
- `"reinforcement learning basal ganglia dopamine reward prediction error action value"` ->
  top hits: `B2. Dopamine reward prediction error` (cos 0.457,
  `notes/research_drill_multi_drive_arbitration_5x_2026-06-10.md`); `Dopaminergic reward
  prediction error` (0.394, science atoms); **`preregs/2026-07-05_pfc_gate_cfrpe_trained_v1.md`
  (0.377)** — a REAL prior CELL, not just a concept atom.
- `"hippocampal replay causal credit assignment temporal sequence"` -> top hits:
  `preregs/2026-06-01_hippocampal_nonrecip_replay_v1.md` (0.352, non-reciprocal replay
  directionality), `wave14d_generation_from_k_gram_research.md` (hippocampal replay as sequence
  generator), `research_brain_multihop_working_memory_5x_drill_2026-06-22.md` (Stream E:
  hippocampal sequence replay + planning). Concept-level prior art present; NO cell doing
  outcome-triggered BACKWARD credit-assignment.
- `"appraisal action tendency emotion learning OFC amygdala value"` -> only generic
  concept/FrameNet/WordNet atoms (`emotion` 0.323, `value function` 0.288, `appraisal` 0.278). No
  prior appraisal->action learning work.

**Verdict: the appraisal->action-tendency and outcome-triggered causal-credit LEARNING targets are
new territory — BUT the underlying LEARNING MACHINERY is already built and CERTIFIED, and the
placeholder "error-driven update" is not hypothetical.** Disk-verified this session (the
load-bearing correction to treating this as a from-scratch design):

**`data/exp_pfc_gate_cfrpe_trained_v2/metrics.json` = HARD_PASS** (verified on disk):
`gonogo_lift=0.600`, `dynamics_lift=0.603`, `reach_tcos_corr=-0.079` (the reach signal is
INDEPENDENT of raw target-cosine — passes the anti-tautology gate), `reach_rank_test=0.690`,
`sign_p=0.0000`, `oracle_rail=True`, `cv=0.037`. This cell (prereg
`preregs/2026-07-05_pfc_gate_cfrpe_trained_v1.md`, v1 was `HARD_FAIL_ADDITIVE_RAIL` — a rail
invocation issue, NOT the mechanism; v2 fixed the regime and landed clean) IS, structurally, a
brain-faithful **basal-ganglia actor-critic**:
- the **cfrpe RPE signal** = the substrate's error-driven delta-rule outer-product update
  (Rescorla-Wagner / TD family), "borrowed EXACTLY" from
  `exp_substrate_adaptive_cfrpe_x_k2_compose_v1`;
- a **successor-feature transport map M** (Dayan-1993 SR / Stachenfeld-2017 hippocampal-striatal
  SR) trained by **TD(0)**, whose TD-error IS the canonical reward-prediction-error, doing
  multi-step temporal credit assignment;
- a **Go/NoGo winner-take-all competition** (PBWM / Frank-O'Reilly 2004/2006) selecting the action.

So the two things this drill must specify — (a) an RPE-trained action-selection policy and (b) a
TD-bootstrapped multi-step credit-assignment map — are BOTH the components of a HARD_PASS organ
we already own. The drill's real job is therefore to (i) NAME the brain structure per the gate,
and (ii) make the **REUSE / re-point** call precisely, with an honest note on what does and does
NOT transfer for free.

**One honest disk-verified caveat that scopes the reuse:**
`data/exp_substrate_adaptive_cfrpe_x_k2_compose_v1/metrics.json` = **HARD_FAIL**
(`compose_lift=-0.0935`; "even ADAPTIVE primitives DO NOT compose K=2; sub-additivity is
mechanistic"). This is NOT a strike against the delta-rule — it is a strike against STACKING two
delta-rules in series (K=2). The pfc_gate HARD_PASS uses a SINGLE error-driven update stage. So
the reuse call is: reuse the delta-rule / SR-transport / Go/NoGo as ONE learning stage each; do
NOT design the earned mapping as a composed chain of delta-rules (evidence says it won't compose).

---

## PART A — EARNING THE APPRAISAL -> ACTION-TENDENCY MAPPING

### A.1 Lead with biology: what learns "(goal-blocked, agent-caused, coping-high) -> retaliate"?

This is **instrumental / reinforcement learning of action VALUE conditioned on an affective-goal
STATE** — precisely the problem the dopaminergic basal-ganglia system solves.

- **The critic (state value) — ventral striatum + OFC/amygdala.** The appraisal outcome IS the
  reward/value signal. Schultz, Dayan & Montague 1997 (*Science* 275:1593) established that
  midbrain dopamine neurons encode a **reward-prediction-error** (RPE): fire to better-than-
  expected outcomes, dip to worse-than-expected — the biological TD-error. OFC and basolateral
  amygdala supply the *value/affect* content that the RPE is computed against (O'Doherty 2004,
  *Science* 304:452, dissociates a ventral-striatal "critic" prediction-error from a dorsal-
  striatal "actor"; Rangel, Camerer & Montague 2008 *Nat Rev Neurosci* on OFC value-coding;
  Balleine & Killcross 2006 on amygdala's two value pathways). In appraisal terms: the appraisal
  computation (goal-congruence, coping-potential) IS the critic's value estimate of the current
  situation; anger/fear/joy are the labelled valence of that appraised value.
- **The actor (action policy) — dorsal striatum, trained by the SAME RPE.** The
  Go/NoGo direct/indirect-pathway architecture (Frank 2005; PBWM, Frank & O'Reilly 2004/2006)
  learns, via dopamine-gated cortico-striatal plasticity, WHICH action to release given the
  cortical (goal/appraisal) state — the "actor" whose policy the critic's RPE shapes.
- **dACC — action-outcome / effort-cost credit.** Anterior cingulate contributes the
  action-specific outcome history and effort/cost weighting that biases action selection
  (Holroyd & Coles 2002 RL theory of ACC; Shenhav, Botvinick & Cohen 2013 expected-value-of-
  control). This is the structure that makes "is retaliation WORTH it given coping-potential" a
  learned action-value, not a fixed reflex.

The mapping the design wants to earn — appraisal-vector (goal-blocked, agent-caused, coping-high)
-> preferred action among {pursue, retaliate, withdraw, help} — is therefore, biologically, an
**actor-critic policy**: STATE = the appraisal-vector (the critic's value + its dimensions),
ACTION = the action-tendency, REWARD = episode-level goal-restoration (did targeting the causal
blocker actually restore goal-progress). "Error-driven update" resolves to: **the RPE-driven
delta-rule updates the action-values / policy; a Go/NoGo competition selects the tendency.** This
is exactly the developmental picture the design's section 2a already argued (appraisal STRUCTURE
is early/fast = supplied; the action-tendency->behaviour COUPLING and its generalization across
novel blockers is experience-shaped = earned) — now with the specific circuit named.

### A.2 The gate — (1) structure, (2) shared-process REUSE

- **(1) Brain structure that earns it:** basal-ganglia **actor-critic trained by dopaminergic
  RPE** (dorsal striatum actor + ventral-striatal/OFC critic + dACC action-outcome), the
  Schultz/Montague-Dayan-Sejnowski TD account, action-gated by the Frank-O'Reilly Go/NoGo circuit.
- **(2) Shared process — REUSE, do not rebuild:** the substrate's **`pfc_gate_cfrpe_trained_v2`
  organ (HARD_PASS)** IS this actor-critic. Re-point it:
  - STATE features fed to the Go-value = the **appraisal-vector** (from the design's supplied
    appraisal schema reading Binder valence / animacy agent-capability / verb-affectedness —
    section 2b), replacing the operator-manifold/goal-cosine features the gate currently uses.
  - ACTION set = the action-tendencies {pursue, retaliate, withdraw, help} instead of chain
    operators.
  - REWARD / TD target = episode-level goal-restoration instead of chain-to-goal reachability.
  - LEARNING RULE unchanged = the certified cfrpe delta-rule providing the RPE; SELECTION
    unchanged = Go/NoGo winner-take-all.
  This is a **re-point of a certified organ, not a new organ** — the exact "does it SHARE a
  process we have" answer the gate asks for. It also matches the brain: the SAME dopaminergic
  RPE + striatal actor-critic learns action-values across every domain; the appraisal/goal
  domain is one more STATE space fed to the same circuit, not a new learner.

### A.3 Fair / can-fail (per mechanism)

Reuse the design's 2c three-floor test, now mechanism-specific:
- **NO-APPRAISAL floor** (action-value conditioned on RAW event features, not the appraisal
  dimensions): isolates whether the SUPPLIED appraisal structure adds value over what the
  actor-critic could learn from raw features alone. If the reused Go/NoGo matches this floor, the
  appraisal architecture is vacuous (design's own PARTIAL band).
- **MEMORIZED-lookup floor** (train on training agents, eval on HELD-OUT identities): forces the
  RPE-learned policy to GENERALIZE across novel blockers/goals, not memorize (agent,goal) pairs —
  the Hamlin-style "valence tracks causal ROLE not surface identity" requirement.
- **RANDOM-action floor.**
- **Anti-tautology (inherited from the pfc_gate prereg):** the certified organ already carries a
  `reach_tcos_corr` guard proving its learned signal is independent of raw cosine (v2 = -0.079).
  The re-pointed cell must carry the analogous guard: the appraisal-conditioned action-value must
  not be a relabelling of a single raw feature (e.g. a bare "harm-word present" cue).
- **Brain-fidelity gate:** a FAIL should look like a dopamine-lesioned actor (cannot acquire the
  action-value — flat learning that is a BROKEN experiment per the flat-result discipline, not a
  ceiling) or a Hamlin-infant misattribution (retaliates at a bystander), NOT a representational
  failure to hold the appraisal-vector at all.

### A.4 Lock-compatibility

EARNED (own FHRR representations, own RPE, own error), glass-box (Go-values + RPE trace
inspectable, exactly as the pfc_gate cell logs `reach_rank`/`dynamics_lift`), no borrowed
embedding, no reader (world-state is discrete, not text). Scope note (from the K=2 HARD_FAIL):
keep the earned mapping to ONE delta-rule stage; do not compose delta-rules in series.

---

## PART B — EARNING THE CAUSAL-COHERENCE ATTRIBUTION (the falsified piece)

### B.0 What exactly was falsified, and why it matters for the mechanism

Tonight (commit e34d54701, WHERE banner): the reuse-shortcut "coref backward-search
(`_pick_strict_cb`) = causal bridging" was **FALSIFIED** — on the richer eval it IS recency
(argmax position), wrong 0/4 on recency-trap items. The banner's own diagnosis is the load-bearing
biology cue: *"pronoun-antecedent selection (recency/salience) != causal-antecedent selection
(coherence/explanation); shared hippocampal substrate but DIFFERENT selection SIGNAL."* So the
mechanism question is precise: **what brain process does credit assignment over a temporal
sequence by an EXPLANATORY-COHERENCE signal, not by temporal proximity?**

### B.1 Lead with biology (ranked candidates)

**Rank-1 mechanism: outcome-triggered PRIORITIZED/REVERSE hippocampal replay for credit
assignment, SELECTED by causal-coherence integration.**
- **Reverse replay = the brain's temporal-credit-assignment operation.** Foster & Wilson 2006
  (*Nature* 440:680) discovered that at the END of a run, hippocampal place-cell sequences replay
  in REVERSE order, starting from the current (outcome/reward) location and running backward along
  the just-traversed path — precisely a mechanism to propagate an outcome signal BACKWARD to the
  antecedent states that led to it. Ambrose, Pfeiffer & Foster 2016 (*Neuron* 91:1124) showed
  reverse-replay strength SCALES WITH REWARD — i.e. it is an outcome-magnitude-weighted backward
  credit assignment, not a uniform rewind. This is the biological answer to "which prior event
  explains the outcome": the outcome REACTIVATES its own causal antecedents.
- **Prioritization is by utility/prediction-error, NOT recency.** Mattar & Daw 2018 (*Nature
  Neuroscience* 21:1609, "Prioritized memory access") — replay preferentially reactivates the
  experiences with the highest **need x gain** (expected future relevance x value-of-updating),
  which optimally trades off, and explicitly reproduces both forward (planning) and reverse
  (credit-assignment) replay as the two regimes of ONE prioritized-access rule. Recency is not the
  priority signal; expected-value-of-update is. This is exactly the property that dissociates
  causal credit from the recency-selection that the coref shortcut collapsed to.
- **The SELECTION among surfaced antecedents is coherence/explanation (Trabasso/Kintsch),
  not proximity.** Trabasso & van den Broek 1985 (*J. Memory & Language* 24:612) — narrative
  causal-network construction links an event to the ANTECEDENT that is causally necessary in the
  circumstances (a counterfactual/explanatory criterion), and causally-central events (many
  connections, on the main causal chain) are the ones retained. Kintsch's Integration stage is
  the constraint-satisfaction settle that picks the coherent antecedent. Neurally, this coherence
  integration recruits the mPFC/anterior-temporal schema system that gates hippocampal
  consolidation (van Kesteren 2012; systems-consolidation schema-consistency — the same analogy
  the design's 3.5 false-consolidation gate already invokes).

**Rank-2 mechanism (already researched, cite): the Successor Representation's PREDECESSOR
structure.** The SR drill (`notes/research_drill_biology_led_predictive_learning_mechanism_
successor_representation_2026-08-03.md`) established SR = TD-bootstrapped discounted future-
occupancy map (Dayan 1993; Stachenfeld 2017), which spreads value along MULTI-STEP paths (not one
step) and structurally cannot mean-collapse. Its TRANSPOSE / predecessor direction answers "what
LEADS here" = the credit-assignment direction. Mattar-Daw unify SR-based replay and prioritized
credit assignment; the SR-transport M is literally the object reverse-replay propagates over.
This is a CHEAPER amortized fast-path once the transition map is stable (BASIS-style, per the
inverse-planning drill's §1b, P=0.50) — but it presupposes a learned M.

**Rank-3 (complement, not selector): joint goal/causal constraint.** Baker, Saxe & Tenenbaum 2009
/ 2017 inverse planning (inverse-planning drill) — goal and causal attribution are JOINTLY
inferred (a goal hypothesis that makes the causal chain coherent is evidence for that goal, and
vice-versa). This is the integration-stage coupling, not a separate credit-assignment learner.

### B.2 The gate — (1) structure, (2) shared-process REUSE

- **(1) Brain structure that earns it:** **outcome-triggered reverse/prioritized hippocampal
  replay** (Foster-Wilson / Ambrose-Pfeiffer-Foster / Mattar-Daw) propagating the outcome signal
  backward over the event sequence, with **causal-coherence integration** (Trabasso/Kintsch,
  mPFC/ATL schema) SELECTING the explanatory antecedent — a DIFFERENT selection signal
  (explanatory coherence, outcome-weighted) than the recency/salience of pronoun-antecedent
  retrieval.
- **(2) Shared process — REUSE (three organs, one re-point + explicit non-reuse):**
  1. **REUSE the SR-transport M from `pfc_gate_cfrpe_trained_v2` (HARD_PASS), re-pointed to the
     PREDECESSOR direction.** The certified organ already learns, by the cfrpe delta-rule + TD(0),
     a multi-step transport map whose forward reach was validated (`reach_rank_test=0.690`,
     `reach_tcos_corr=-0.079` = genuinely dynamics-carried, not cosine-in-disguise). Re-point:
     score `is candidate-antecedent-event on a path that PRODUCES this outcome-event`
     (predecessor/transpose reachability) instead of `candidate on a path to goal`. This is the
     credit-assignment map, EARNED, and it is the SAME learning rule already certified.
  2. **REUSE `situation_model_multibank` / `situation_model_accumulate` (WIRED_AND_PIPELINE_USED,
     decode >=0.999) as the replay buffer to reverse-replay over.** Reverse replay = iterate the
     accumulated event sequence BACKWARD from the outcome, propagating the RPE/credit signal along
     the SR-transport — reusing the exact accumulate register the SR drill already proposed as the
     replay source (there for negatives; here for backward credit propagation). No new buffer.
  3. **REUSE `CausalLinkRegister` (0.9722 GIVEN links) + the coherence-gated `self_improving_loop`
     as the INTEGRATION/coherence SELECTOR** that picks the explanatory antecedent among the
     replay-surfaced candidates — the Trabasso/Kintsch integration step, which these organs ALREADY
     implement as coherence/constraint-satisfaction over candidate relations (per all three
     tonight drills' convergent construction-integration frame).
  4. **EXPLICIT NON-REUSE (the falsified move):** do NOT use the coref backward-search
     `_pick_strict_cb` as the selector. Its selection signal is recency/salience (proven this
     session to be recency); it is the WRONG circuit for causal credit even though it shares the
     hippocampal substrate. This is the single most important negative the gate produces here.

### B.3 Fair / can-fail (per mechanism)

- **The eval must contain RECENCY-TRAP items** where the coherent/explanatory cause is NOT the
  most-recent antecedent (the exact discriminating structure tonight's 15-item richer eval,
  commit e34d54701, was built to have — reuse it / extend it). The mechanism must beat a
  **RECENCY floor** (argmax-position antecedent) on the multi-candidate subset where
  coherent-cause != recent — this is the floor the falsified shortcut TIED (0/4). PASS requires
  strictly beating recency exactly where recency is wrong.
- **Anti-tautology:** the SR-transport predecessor score must carry the analogous
  `reach_tcos_corr`-style guard proving it is not a relabelled surface-overlap/recency cue (the
  certified forward organ already carries this; the re-pointed backward version must re-earn it —
  do NOT assume the forward HARD_PASS transfers to the backward direction for free; that is a
  design change requiring its own can-fail).
- **Brain-fidelity gate:** a FAIL should look like a replay-lesioned credit assignment (defaults
  to recent/adjacent, the hippocampal-replay-KO signature) or a coherence-filter miss, NOT a
  representational inability to hold the sequence.
- **HARD-FAIL that does NOT reopen "impossible":** if the coherence-selected, replay-propagated
  credit still ties recency on the trap items even with the full accumulate context, that
  sharpens (per the fidelity-gap synthesis) the content-encoding fork — it would mean the
  explanatory-coherence SIGNAL itself needs richer content, not that credit-assignment is
  impossible.

### B.4 Lock-compatibility

EARNED (SR-transport learned by own TD/delta-rule over own FHRR events; reverse-replay over own
accumulate buffer; coherence selection by own already-validated organs), glass-box (the credit
trace = the backward-replay sequence + per-candidate coherence scores, all inspectable), no
borrow. Negatives/counterfactuals for any contrastive component are self-generated via replay
(the SR drill's already-argued lock-clean choice), never an external bank.

---

## PART C — COMPOSITION + brain-faithful path to SIM-TO-TEXT transfer

### C.1 How (a) and (b) compose IN THE SIMULATION's earning

They compose through the **appraisal-vector's causal-attribution slot** — (b) FEEDS (a):
1. An episode runs; agent A's goal flips satisfied->false.
2. **(b) runs first:** outcome-triggered reverse-replay + SR-transport predecessor credit +
   coherence selection identifies WHICH prior agent-action explains the block (not the most
   recent event) = the `causal-attribution: identifiable-AGENT-cause = agent B` dimension of the
   design's 2b appraisal-vector.
3. The supplied appraisal schema computes the full appraisal-vector (goal-relevance, congruence
   from Binder Harm/Benefit, causal-attribution = B from step 2, coping-potential).
4. **(a) runs:** the RPE-trained actor-critic Go/NoGo maps that appraisal-vector -> action-
   tendency, and the earned lesson is `blocked + agent-caused-by-B + coping-high ->
   retaliate-toward-B` — retaliation targeted at B (the credit-assigned blocker), NOT a bystander,
   is what episode-level goal-restoration differentially reinforces.

So (b) is the causal-attribution INPUT to (a)'s state; (a) is the action-value learner over that
state. This is exactly the design's own 2b appraisal computation ("causal-attribution: was there
an identifiable AGENT cause") made mechanistically specific — and it is Baker et al.'s JOINT
attribution (goal/causal mutually constrain in ONE integration pass), which is why all three
tonight drills converged on the single Kintsch construction->integration frame as the composition
point rather than two bolted modules. Construction = SR/replay overgenerates candidate
antecedents/successors + goal-schemas; Integration = CausalLinkRegister/coherence-loop selects;
the actor-critic consumes the selected causal-attribution.

### C.2 Brain-faithful path to sim-to-text transfer (the PENDING claim — flagged honest)

**The transfer bridge = the appraisal-vector INTERFACE (Harnad grounding-transfer, reused).** The
simulation earns two functions over the appraisal-vector: (b) the credit-assignment selector and
(a) the appraisal->action-tendency policy. Reading does NOT re-earn them — the existing extraction
stack (coref / situation_model / situated-structure parse agent->target->action) produces the
SAME appraisal-vector FROM TEXT (its causal-attribution slot filled by (b) run over the
text-extracted event sequence; its valence slot from Binder; its agent slot from animacy_lexicon).
Text maps onto an already-grounded function; it never originates the concept. This is the design's
section 3 two-stage architecture (FOUNDATION built once in sim; READING queries it), and the
transfer is lock-clean because the shared object is a grounded FEATURE VECTOR, not a borrowed
embedding.

**Honest cap (calibration discipline):** sim-to-text transfer is UNVERIFIED — it is the pending
claim, not a result. The fair test is whether the sim-earned (a)+(b) functions generalize to
TEXT-extracted appraisal-vectors WITHOUT retraining (or with only the reward vector re-learned —
the SR revaluation property, Stachenfeld 2017, which lets the reachability map hold while only the
goal-weight changes; BASIS-style w-inference, inverse-planning drill §1b). P for clean zero-shot
sim->text transfer is deflated and capped at **0.35** (novel synthesis, cross-domain generalization
gap is exactly the unproven step). P that the sim itself earns (a)+(b) on held-out agents (the
first can-fail, a0b19793) — higher, because the machinery is certified in-domain.

### C.3 Scale note

The actor-critic + SR-transport are amortized: once M is stable for a narrative domain, goal/credit
inference is a cheap projection (BASIS w-inference), not a per-candidate replan. Curriculum: simple
2-agent single-block episodes -> multi-agent, multi-goal, false-belief-modulated blocks (appraisal
runs over the agent's REPRESENTED state — reuse the Sally-Anne organ, design 1.5-F). Keep each
learning stage a SINGLE delta-rule (K=2 composition HARD_FAILED on disk).

---

## RANKED LEARNING-MECHANISM SPEC (the deliverable, one table)

| # | What to earn | Brain STRUCTURE (lead-with-biology) | Shared-process REUSE call | Fair / can-fail | P (deflated) |
|---|---|---|---|---|---|
| **1** | **(a) appraisal -> action-tendency** | Basal-ganglia **actor-critic trained by dopaminergic RPE** (Schultz 1997; Montague-Dayan-Sejnowski; O'Doherty 2004 actor/critic; dACC action-outcome Holroyd-Coles 2002); **Go/NoGo** action gate (Frank-O'Reilly PBWM 2004/2006) | **REUSE `pfc_gate_cfrpe_trained_v2` (HARD_PASS, disk-verified) re-pointed**: STATE=appraisal-vector, ACTION=action-tendencies, REWARD=goal-restoration; cfrpe delta-rule = the RPE (unchanged); Go/NoGo = selection (unchanged). A re-point of a CERTIFIED organ, not a new organ | 3 floors (no-appraisal / memorized-held-out / random) + reach_tcos-style anti-tautology; FAIL = dopamine-lesioned flat learn (broken exp, not ceiling) or Hamlin misattribution | **0.60** (est. right mechanism-class + organ certified; caps for the new STATE space) |
| **2** | **(b) causal-COHERENCE credit-assignment** (the falsified piece) | **Outcome-triggered reverse/prioritized hippocampal replay** (Foster-Wilson 2006; Ambrose-Pfeiffer-Foster 2016 reward-scaled; Mattar-Daw 2018 need×gain, NOT recency) propagating outcome backward; **causal-coherence integration** SELECTS the explanatory antecedent (Trabasso 1985; Kintsch integration; mPFC/ATL schema) | **REUSE SR-transport M from `pfc_gate_cfrpe_trained_v2` re-pointed to PREDECESSOR direction** + **`situation_model_multibank/accumulate` as the reverse-replay BUFFER** + **`CausalLinkRegister`+`self_improving_loop` as the coherence SELECTOR**. **EXPLICIT NON-REUSE:** NOT the coref `_pick_strict_cb` (its signal is recency — the falsified move) | eval MUST have recency-trap items (coherent-cause != recent); beat RECENCY floor exactly where recency is wrong (the floor the shortcut TIED 0/4); re-earn anti-tautology guard for the BACKWARD direction (don't assume forward HARD_PASS transfers) | **0.45** (established reverse-replay biology; the predecessor re-point + coherence-selection is novel synthesis, capped) |
| 3 | Composition (a)+(b) | Baker 2009/2017 JOINT belief-desire attribution; Kintsch construction->integration | (b) feeds (a) via the appraisal-vector's causal-attribution slot; ONE integration pass over CausalLinkRegister; architecture reuse | (b) and (a) can-fails run together; PARTIAL if joint no better than sequential | 0.55 (reuses validated organs) |
| 4 | Sim->text transfer (PENDING) | Harnad grounding-transfer; SR revaluation (Stachenfeld 2017) / BASIS w-inference | shared appraisal-vector INTERFACE; reading fills the same slots from text via existing extraction organs; only reward-vector re-learned | zero-shot sim->text on held-out text appraisal-vectors, no retrain | 0.35 (unverified cross-domain, the real gap) |

---

## What is NEW vs KB (dedup summary)

- **NEW learning TARGETS** (no prior cell): appraisal->action-tendency policy; outcome-triggered
  BACKWARD causal-credit; sim->text transfer of an earned appraisal function.
- **NOT new (REUSE, disk-verified):** the LEARNING MACHINERY — cfrpe delta-rule (RPE), SR-transport
  M via TD(0), Go/NoGo action selection — all in the HARD_PASS `pfc_gate_cfrpe_trained_v2`;
  the replay buffer (`situation_model_multibank/accumulate`); the coherence selector
  (`CausalLinkRegister`, `self_improving_loop`); the goal/false-belief hosts (Sally-Anne organ).
  The three tonight drills (SR/TD, inverse-planning, fidelity-gap) + the foundational design supply
  the frame (construction->integration) and are cited, not re-derived.
- **The single sharpest NEW finding of this drill:** the placeholder "error-driven update" is not
  hypothetical — it is the RPE/TD delta-rule of an organ we ALREADY certified HARD_PASS; and the
  falsified causal-coherence piece has a SPECIFIC brain fix (reverse/prioritized replay + coherence
  selection, an OUTCOME-triggered BACKWARD signal), which REUSES the SAME SR-transport organ
  re-pointed to the predecessor direction, while EXPLICITLY NOT reusing the coref recency-selector
  that just falsified.

## Lock-compatibility (whole spec)

All EARNED (own FHRR, own RPE/TD error, own replay buffer, own coherence organs); glass-box
(RPE trace, backward-replay sequence, per-candidate coherence scores all inspectable); no borrowed
embedding, no bolt-on reader (sim is discrete world-state, not text; text enters only at the
transfer stage as feature-vector queries); single-delta-rule stages only (K=2 composition
HARD_FAILED on disk). Consistent with brain-foundational, no-borrow, meaning=assignment, and the
route-errors rule (missing-PRIMITIVE handled by re-pointing an existing built primitive, not a
new supply).

## Citations (biology-first; tonight's docs cited, not re-derived)

Schultz, Dayan & Montague 1997 *Science* 275:1593; Montague, Dayan & Sejnowski 1996 *J Neurosci*;
O'Doherty et al. 2004 *Science* 304:452 (actor/critic dissociation); Holroyd & Coles 2002 *Psych
Review* (ACC RL theory); Shenhav, Botvinick & Cohen 2013 *Neuron* (EVC); Frank & O'Reilly
2004/2006 (PBWM Go/NoGo); Rangel, Camerer & Montague 2008 *Nat Rev Neurosci* (OFC value); Balleine
& Killcross 2006 (amygdala value); Foster & Wilson 2006 *Nature* 440:680 (reverse replay);
Ambrose, Pfeiffer & Foster 2016 *Neuron* 91:1124 (reward-scaled reverse replay); Mattar & Daw 2018
*Nat Neurosci* 21:1609 (prioritized memory access, need×gain); Dayan 1993 *Neural Comp* 5:613 (SR);
Stachenfeld, Botvinick & Gershman 2017 *Nat Neurosci* 20:1643 (hippocampus as predictive map,
revaluation); Trabasso & van den Broek 1985 *JML* 24:612; Kintsch 1988/1998 (construction-
integration); Baker, Saxe & Tenenbaum 2009 *Cognition* / 2017 *Nat Hum Behav* (inverse planning,
joint attribution); van Kesteren et al. 2012 *Trends Neurosci* (schema-gated consolidation).
Disk-verified prior art: `data/exp_pfc_gate_cfrpe_trained_v2/metrics.json` (HARD_PASS, gonogo_lift
0.600), `preregs/2026-07-05_pfc_gate_cfrpe_trained_v1.md`, `data/exp_substrate_adaptive_cfrpe_x_k2_
compose_v1/metrics.json` (K=2 HARD_FAIL — scopes reuse to single-stage). Tonight's drills (cited,
not re-derived): `research_drill_biology_led_predictive_learning_mechanism_successor_representation_
2026-08-03.md`, `research_drill_biology_led_unstated_goal_inference_inverse_planning_2026-08-03.md`,
`research_synthesis_brain_fidelity_gap_event_prediction_relation_inference_2026-08-03.md`,
`foundational_grounded_knowledge_layer_program_2026-08-03.md`.

## HEADLINE

The design's "error-driven update" placeholder pins to a SPECIFIC, already-certified mechanism.
**(a) appraisal->action-tendency = a basal-ganglia actor-critic trained by dopaminergic RPE
(Schultz) with Go/NoGo selection (Frank-O'Reilly) — REUSE the HARD_PASS `pfc_gate_cfrpe_trained_v2`
organ (gonogo_lift 0.600, dynamics-attributable), re-pointed so STATE=appraisal-vector,
ACTION=action-tendency, REWARD=goal-restoration; the delta-rule IS the RPE, unchanged.**
**(b) causal-COHERENCE credit-assignment (the falsified piece) = outcome-triggered
reverse/prioritized hippocampal replay (Foster-Wilson; Mattar-Daw need×gain, NOT recency)
propagating credit BACKWARD, with causal-coherence integration (Trabasso/Kintsch) SELECTING the
explanatory antecedent — REUSE the SAME SR-transport map re-pointed to the PREDECESSOR direction +
the accumulate/multibank register as the reverse-replay buffer + CausalLinkRegister/self-improving-
loop as the coherence selector; EXPLICITLY do NOT reuse the coref recency-selector that just
falsified.** They compose because (b) fills the causal-attribution slot of the appraisal-vector
that (a) conditions on (Baker joint attribution). Sim->text transfer rides the shared
appraisal-vector interface (Harnad transfer, SR revaluation) but is UNVERIFIED, P capped 0.35.
Everything is earned, glass-box, no-borrow, single-delta-rule-stage (K=2 composition HARD_FAILED).
The brain-structure + shared-process REUSE gate keeps predicting right: both hard pieces re-point
ONE already-certified RL organ, exactly as the brain reuses ONE dopaminergic RPE + striatal
actor-critic + hippocampal replay across every domain.
