# Interactive extraction<->situation-model loop: brain-foundational design + cheapest first probe (2026-08-01)

Director design spec answering the USER re-lock ("always go after brain-foundational, we KNOW it
works") + the broad brain-fidelity audit's #1 architectural risk: our roadmap runs
extraction -> situation-model FEED-FORWARD; the brain runs them as ONE interactive loop with
top-down feedback within ~200ms.

Calibration: CITED@ = the underlying brain finding (carried from the audit +
`brain_syntax_to_role_mechanism..._2026-07-30.md`, CITED@ there via 2 lit-scans; NOT
re-verified this cycle). REASONED@ = the transfer to this substrate design (my synthesis, not
an established result). ESTABLISHED/CONTESTED flagged per brain claim. P deflated per the
lit-scan-calibration penalty; novel-synthesis capped at 0.50.

KB-check: `substrate_query.sh` / `director_kb_query.py` both returned empty this cycle
(queryable index stale/misbehaving, as the task warned); direct `grep notes/` timed out
(notes dir too large for a 20s ripgrep). Grounding is therefore off the THREE authoritative
recent design notes read end-to-end this cycle + direct read of the reuse organ
`hdlab/slot_attention_wm.py`. No prior note designs THIS interactive-loop architecture (the
07-30 spec adds a within-ENCODER hold-then-revise gate; it does NOT add situation-model ->
extraction top-down feedback -- that is this note's new content). PRIOR-ART OVERLAP: the graded
PE-gate + content-addressed slots + HRR binding already exist and are reused verbatim (see
"reuse", below); the NEW content is the top-down feedback wiring + precision-weighting + the
first probe.

---

## THE CORE GAP (measured, precise)

`hdlab/slot_attention_wm.py` today: `tok_reps` (extraction output) -> `entity_filler()`
(role-query attention over tokens) -> `step()` updates slots. **The slots never influence the
extraction of `entity_filler`.** `entity_filler` scores tokens with a STATIC learned
`role_query` that is independent of current slot state. That is precisely the feed-forward
order the audit flagged as non-biological (risk #1). It is also connected to run-6: a
standalone feed-forward extractor's entity rep is unconstrained by any downstream objective, so
it collapses / drifts; a top-down loop gives the entity rep an objective (match the
situation-model's expectation) that shapes it.

The measured wall this fixes: `exp_syntactic_role_agent_patient_voice_probe_v1` cross-voice
agent/patient = **0.16-0.18 (BELOW chance, INVERTS on passives)**, within-voice = 0.90/0.85.
That inversion is the Broca's-agrammatism / TDH signature (Caramazza&Zurif 1976;
Grodzinsky TDH) of a system that reverts to "first-noun = agent" when the structure-building /
revision stage is absent -- exactly what a feed-forward, no-top-down extractor does.

---

## PART 1 -- THE BRAIN-FOUNDATIONAL DESIGN (each element cited + ESTABLISHED/CONTESTED)

An interactive loop, evaluated clause-by-clause. At clause t, with slots S_{t-1}:

### (a) TOP-DOWN: situation-model state gates/biases extraction

**Mechanism to implement:** the addressed slot(s) emit a top-down expectation `p_td = g(S_{t-1})`
(a d-dim expected entity/role-filler vector -- e.g. "the incoming clause is about the entity in
slot k, in the patient role" or "this verb expects an animate agent"). The bottom-up role-query
attention over `tok_reps` is BIASED by `p_td`: the effective query = `role_query (+)
modulate(p_td)` rather than the static `role_query` alone. So the situation model gates WHICH
token is extracted as which role -- constraint-based parsing, not linear-position default.

- **Brain grounding (CITED@, ESTABLISHED):** constraint-based / interactive lexicalist parsing
  -- MacDonald, Pearlmutter & Seidenberg 1994; Trueswell & Tanenhaus 1994 (referential/discourse
  context modulates syntactic ambiguity resolution in the *earliest* measures); Altmann & Kamide
  1999 (anticipatory eye movements: verb selectional expectation -- "eat" -> edible object --
  directs attention to the argument BEFORE the noun arrives = top-down expectation biasing
  extraction); Crain & Steedman 1985 (referential theory). The strong syntax-first modularity
  account (Frazier garden-path) is the LOSING side of this debate. **CONTESTED:** the exact
  *timing/degree* of interactivity at the millisecond level is still argued; "fully interactive
  from word 1" is not universally accepted, but "situation-model info feeds back to constrain
  parsing" is mainstream.
- **Neural grounding (CITED@, CONTESTED-as-mechanism):** cortex is massively feedback-connected;
  higher levels send predictions DOWN that modulate lower processing (Rao & Ballard 1999;
  Friston free-energy). ESTABLISHED that feedback exists and is functional; CONTESTED that it is
  specifically Bayesian predictive coding.
- **HONEST FLAG (not cleanly brain-grounded):** the *algebraic form* of the bias (adding /
  FHRR-binding the expectation into the query) is a SUBSTRATE-NATIVE operation, not the brain's.
  The PRINCIPLE (top-down feedback modulates extraction) is brain-foundational; the OPERATION is
  ours (glass-box, but engineering). Labelled "brain-grounded principle, substrate-native op."

### (b) ENTITY-REP SHAPING by GRADED prediction-error (predict-then-revise, graded)

**Mechanism to implement:** graded PE `e = f_bu (-) p_td` (bottom-up filler vs top-down
expectation; 1-cos or vector residual). The entity/slot representation is updated by a GRADED
(not hard-discrete) function of `e` -- a precision-weighted blend of expectation and input. This
directly shapes the entity rep (fixes run-6): the rep is no longer a free-floating pooled vector
but is pulled toward "consistent with the situation model's expectation, revised by the
disambiguating input."

- **REUSE (already built + VET'd):** `SlotAttentionWM.step()` already computes per-slot
  `surprise_k = 1 - cos(readback, clause)` and a `boundary_k = sigmoid((surprise_k - theta)/tau)`
  write gate with tau ANNEALED soft->sharp. For THIS loop, **keep tau in the SOFT/graded regime**
  (do not anneal fully to bistable) -- the audit's exact refinement (PE-gate is defensible but
  "may need to be more graded/probabilistic than a hard gate").
- **Brain grounding (CITED@):** predict->mismatch->revise cycle -- N400/P600 dissociation;
  Osterhout & Holcomb 1992/1994 (P600 reanalysis at the disambiguating word). ESTABLISHED that
  revision happens. **Graded, not discrete (CONTESTED which):** surprisal theory (Hale 2001;
  Levy 2008, CONTINUOUS -log P) + constraint-satisfaction (MacDonald) + good-enough processing
  (Ferreira) favor GRADED; discrete commit-then-revise (Van Gompel race; P600-as-reanalysis) has
  real precedent but is not the modal view. => graded is the safer brain-faithful default here.

### (c) PRECISION-WEIGHTING: inverse-variance reliability-gain on the update

**Mechanism to implement:** a scalar gain `pi = 1 / var(e)` (running estimate of the variance of
the prediction error, per channel/slot/level) multiplies the error-driven update. Reliable
channels (low variance) get high gain (big update); noisy channels get downweighted. NOT a new
organ -- a scalar multiplier on the existing `write_k` / update magnitude.

- **Brain grounding (CITED@, CONTESTED-as-mechanism):** Friston free-energy; Feldman & Friston
  2010 ("Attention, uncertainty, and free-energy") -- precision = inverse variance of prediction
  error; attention = optimizing precision; belief updates are precision-weighted. ESTABLISHED as
  a formal computational theory; **CONTESTED as THE brain mechanism** (leading framework, not
  settled neuroscience; proposed neural substrate = synaptic/NMDA gain, ACh/NE neuromodulation).
- **HONEST FLAG:** the running-variance estimator is an engineering instantiation. The principle
  (reliability-weighted error) is brain-grounded-but-contested; the estimator is ours.

### REUSE INVENTORY (this is ASSEMBLY, not new parts)
- Graded PE-gate commit-then-revise: `SlotAttentionWM.step()` boundary_k + annealed tau (kept
  soft). Already VET'd (WM_PROVEN, per module docstring / 07-29 arc).
- Content-addressed slots + role-query extraction: `SlotAttentionWM.entity_filler()` +
  `addr_net`. Reused; the ONE change is conditioning the query on `p_td`.
- FHRR entity binding: `hdlab/binding.bind/unbind`. Unchanged.
- Situation-model loop endpoint: the slot stream itself. Unchanged.
- **The genuinely NEW wiring:** (i) `g(S_{t-1}) -> p_td` top-down predictor head (one small MLP);
  (ii) query modulation by p_td in `entity_filler`; (iii) the precision estimator `pi = 1/var(e)`.
  Three small additions, glass-box, own-mechanism. No bolt-on parser, no borrowed embedding.

---

## PART 2 -- THE CHEAPEST CAN-FAIL FIRST PROBE

Design intent: prove the interactive TOPOLOGY can USE top-down constraint to override linear
order on the exact order!=role cases the wall found (active vs passive), on HELD-OUT verbs.
Synthetic, oracle-structured, CPU-cheap -- exactly the Probe-1 profile. This proves the
MECHANISM/plumbing, NOT real-text comprehension (scope flag below).

### Task (controlled, order!=role)
Synthetic clauses over oracle vectors (no encoder training). Each clause has 2 entity mentions +
1 verb. Two constructions, balanced:
- ACTIVE: "A verb B" -> agent=A (first noun). Canonical; linear-order heuristic CORRECT.
- PASSIVE: "B was verb-ed by A" -> agent=A (second noun). Non-canonical; linear-order heuristic
  WRONG (inverts).
Oracle scaffold (allowed for a mechanism probe, like Probe-1's oracle signal): the verb vector
carries selectional expectation in the substrate's OWN space (e.g. `verb (bind) {agent:animacy,
patient:edibility}`); entities carry animacy/edibility features. Entities are feature-OVERLAPPING
enough that POSITION is the only cheap cue for a feed-forward extractor (keeps the baseline
genuinely fail-able, not trivially solvable by feature alone).

### ONE VARIABLE: interactive-loop ON vs OFF
- **OFF (feed-forward baseline):** static role-query extraction, no p_td feedback, no precision.
  ~ the current `entity_filler`.
- **ON (interactive):** p_td from slot/verb-expectation biases the query; graded PE + precision
  shape the assignment.

### PRE-REGISTERED PASS/FAIL BANDS (per arm, on HELD-OUT verbs)
Metric = agent/patient assignment accuracy, reported SEPARATELY for active and passive, plus the
gap `G = acc_active - acc_passive` (the psycholinguistic signature).

1. **CAN-FAIL FLOOR (must empirically hold or the probe is broken):**
   feed-forward baseline **passive acc <= 0.55** (reproduces the wall; ideally INVERTED < 0.40),
   while **active acc >= 0.80** -> baseline gap `G_off >= 0.30` (the canonical-order bias / TDH
   signature). If the baseline does NOT fail on passives, the task is too easy -- STOP, harden it.
2. **HARD-PASS (interactive):** interactive **passive acc >= 0.75 AND active acc >= 0.75**, both
   on held-out verbs, AND gap **G_on <= 0.15** (closes the active-passive gap = reproduces
   interactive disambiguation, NOT a uniform accuracy bump). Brain-metric: it must be the
   NON-CANONICAL cases that lift, not everything uniformly.
3. **HARD-FAIL:** interactive passive acc <= 0.55 (no better than baseline) -> top-down feedback
   did not resolve order!=role; the loop is not doing what the theory says.
4. **MIDDLE / PARTIAL:** passive acc in (0.55, 0.75) -> no longer inverted but not yet reading
   role -- report as a distinct informative outcome, do NOT force into PASS/FAIL.

### CONTROLS (each pre-registered; each must behave as stated or the result is an artifact)
- **RANDOM-FEEDBACK placebo (CRITICAL):** interactive wiring intact but `p_td` drawn from a
  SHUFFLED/random slot state (not the true situation model). **MUST NOT help** (passive acc must
  stay near the feed-forward floor). This proves it is the CONTENT of the top-down signal (verb
  expectation / discourse referent) that resolves the ambiguity, not merely "having a recurrent
  connection." If random feedback helps as much as true feedback -> artifact, HARD-FAIL the claim.
- **NO-PRECISION control (fair-test-gated):** interactive loop with precision fixed to uniform
  (pi=1). Isolates whether precision-weighting specifically contributes beyond top-down feedback.
  **FAIRNESS REQUIREMENT (USER: a null only counts if the experiment COULD show a lift):** on a
  clean synthetic task all channels are equally reliable, so precision has nothing to weight and
  a null would be UNFAIR/uninformative. Therefore the probe MUST include a **noisy-cue arena**: a
  subset of items where one entity-feature channel is corrupted with noise. In THAT arena,
  precision-ON should beat precision-OFF (downweight the noisy channel). Pre-reg:
  precision-ON passive acc in noisy-cue arena **>= precision-OFF + 0.10**. If both are equal in
  the noisy arena too, THEN the null is fair and informative (precision not load-bearing at this
  scale). Without the noisy arena, do not claim anything about precision.

### BRAIN-METRIC (not just average accuracy)
The result must reproduce the interactive-disambiguation SIGNATURE: baseline shows the
directional inversion (`G_off` large, canonical advantage / passive below chance); interactive
specifically LIFTS the non-canonical cases (`G_on -> 0`). "Raised average accuracy uniformly"
does NOT count as reproducing the brain's mechanism.

### COST
CPU, minutes -- oracle vectors + tiny MLPs (p_td head, precision estimator, reused
SlotAttentionWM gate). d_model small (256-512); a few thousand synthetic clauses; no encoder
training, no GPU. Mandatory per-(arm,seed) checkpointing per CLAUDE.md. Est: a Tier-1 CPU cell,
< ~1 CPU-hour total across arms/seeds. This is the Probe-1 cost class deliberately.

### SCOPE FLAGS (honest)
- Oracle-supplied selectional features = a PROBE SCAFFOLD, not a brain/capability claim. This
  proves the interactive topology can USE available top-down constraint to override linear order;
  it does NOT prove the substrate can LEARN selectional restrictions from real text (that is the
  later real-text / 07-30-causal-encoder scaling step).
- CONSTRUCTION-DETERMINED RISK: because we hand the substrate the verb's selectional info in its
  own space, "interactive resolves passives" is close to construction-guaranteed IF wired
  correctly. What makes the probe non-vacuous is the CAN-FAIL floor (baseline must invert) + the
  RANDOM-FEEDBACK placebo (proves the top-down CONTENT, not the connection, carries the result) +
  HELD-OUT verbs (not memorization). Report as a MECHANISM/plumbing proof, a necessary
  precondition -- NOT a comprehension-capability win.

---

## P_DEFLATED + WEAKEST LINK

**P_deflated (full pre-registered pattern: baseline inverts + interactive HARD-PASS + random-
feedback placebo stays down + held-out generalizes + precision fair-test shows a lift in the
noisy arena): 0.35.** Base ~0.55 (top-down feedback resolving order!=role on an oracle-structured
task is well-motivated and near-construction-guaranteed for the primary variable) minus the
lit-scan-calibration penalty and the compound-conjunction risk (5 conditions must ALL land as
specified; the random-feedback placebo and the precision noisy-arena sub-claim are the shakiest).
The PRIMARY sub-claim alone (interactive resolves passives, gap->0, held-out) is higher, ~0.45.

**SINGLE WEAKEST LINK: precision-weighting (element c).** Two compounding weaknesses: (1) it is
the least cleanly brain-grounded element -- Friston/Feldman precision is a leading but CONTESTED
computational theory, not a settled brain mechanism, and the running-variance estimator is
engineering; (2) on the clean synthetic task it has nothing to bite on, which is why the probe
MUST add the noisy-cue arena to give it a fair test at all -- and even there it may not beat the
top-down feedback that is already doing the disambiguation. Precision risks being decorative on
THIS task. Honest handling: make TOP-DOWN FEEDBACK (element a, the best-grounded, most
load-bearing part) the primary variable; treat precision as a secondary factor with its own
fair-test arena and a pre-registered "fair null is acceptable and informative" outcome. Do NOT
label the whole loop's success as evidence for precision if precision's own control is null.

**Second weakest: the "brain-grounded principle, substrate-native operation" seam** -- the
top-down bias is implemented by a VSA algebraic op the brain does not use. The principle is
brain-foundational; the operation is glass-box engineering. This is honest and acceptable (we
never claimed the brain does convolution-binding), but it means "brain-foundational" applies to
the ARCHITECTURE/TOPOLOGY, not every operation inside it -- stated so no one over-reads it.

---

## RECOMMENDED NEXT ACTION
Hand this to `hdi_exp_dev` as a Tier-1 CPU probe (exp_dev owns anchor naming, sweep grid,
threshold formulas, exact pre-reg bands per envelope-fail-bands -- the bands above are a
starting point). Sequence: build + smoke the interactive-loop cell reusing SlotAttentionWM;
run the 4 arms (feed-forward OFF / interactive ON / random-feedback placebo / no-precision) x
seeds x {clean, noisy-cue} arenas; VET the can-fail floor + placebo before trusting the HARD-PASS.
This is CHEAP, measurement-first, can-fail, and tests the audit's #1 architectural risk before
any real-text/GPU build. Bring the verdict to USER before scaling to real text.
