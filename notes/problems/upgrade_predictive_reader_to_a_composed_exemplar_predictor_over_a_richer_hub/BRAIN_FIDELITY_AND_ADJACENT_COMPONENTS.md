# Brain-fidelity of the walls + adjacent-component evaluation (seeds the next problems)

Solver deliverable for `upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub`,
answering the owner's two standing asks: **"is each wall a fidelity gap to build across, or a
brain-consistent ceiling?"** and **"map the capabilities/limitations/opportunities/brain-status of adjacent
components to plan the next problems."** Every claim is measured on this problem's landed cells or cited
from the two research drills folded into `SOLVED.md`.

---

## PART 1 -- THE WALLS, EVALUATED FOR BRAIN-FIDELITY (gap to build across, or brain-consistent ceiling?)

### WALL A -- the live who-did-what deployment does not lift with the hub (AUC +0.008 ns; Channel-A +0.012 ns)
- **How the brain does it:** English who-did-what SELECTION is word-order-dominant (Competition Model,
  MacWhinney-Bates; the parent's audit). Thematic fit is a LOW-validity cue that surfaces only at syntactic
  ambiguity. The live candidate pool competes co-event participants (agent/obliques), so ranking the patient
  there is a selection task where position rules.
- **Verdict: BRAIN-CONSISTENT CEILING, not a fidelity gap.** The brain ALSO would not use the meaning
  representation to win who-did-what selection here -- it uses syntax. The hub's advantage is real for
  *prediction* (random-distractor pools: +0.076 held-out, +0.049..+0.114 across the pool-size sweep) and it
  is muted in the selection-flavored live pool exactly as the Competition Model predicts. No gap to build.

### WALL B -- 46.9% of the reader's residual errors are un-flaggable by marginal surprisal
- **How the brain does it (two mechanisms):** (1) good-enough processing (Ferreira 2003) -- the brain
  ITSELF misses plausible-but-wrong role bindings; these are not flaggable by any prediction signal. (2) BUT
  the brain has a SECOND, dissociable error signal our organ lacks: the semantic P600 / conflict-monitor
  (Van Herten & Kolk 2005/06; Kuperberg thematic-role-reversal) -- it fires on a role assignment that
  CONFLICTS with a more plausible alternative, not merely on a low-probability filler.
- **Verdict: BRAIN-CONSISTENT CEILING (tested at power).** `exp_composedhub_conflict_flag_v1` (n=2992,
  200-d): the CONFLICT margin (s_pick - min_{c!=pick} s_c) as the error-flag is CI-separated WORSE than the
  marginal surprisal (HUB conflict vs marginal -0.028 CI[-0.048,-0.010] NEG; ORGAN -0.038 NEG). Two
  drill-grounded reasons: (1) the P600 conflict signal fires on thematic-role REVERSALS, but the reader's
  wrong pick is the agent only 3.3% of the time -- the residual errors are good-enough (a plausible
  NON-agent noun), not reversals. (2) The margin form is not the brain's mechanism: the only FORMALIZED P600
  account (Brouwer, Crocker, Venhuizen & Hoeks 2017) is a same-stream INTEGRATION-COST metric [1 -
  cos(integration_t, integration_{t-1})] over the compositional SITUATION-MODEL update, NOT a
  margin-against-a-competing-alternative -- so the faithful conflict signal is an integration-cost over the
  situation model (the north-star P1's generative state), which the verb-patient predictor cannot compute.
  And good-enough processing (Christianson 44-74%, Ferreira 12-45%, Patson 69-74% undetected) confirms the
  ~47% residual is what a HUMAN reader also misses. **Kill for this organ; the correct form belongs to P1.**

### WALL C -- ~11.5% live coverage loss (pick/verb OOV of the hub); the hub's dim cap is on VOCAB coverage
- **How the brain does it:** ATL taxonomic generalization -- a rare/novel concept inherits the semantic
  neighbourhood of its category (Lambon Ralph). The faithful computational form is Resnik selectional
  association (1996): back off an OOV filler to the WordNet class with MAXIMAL selectional association to the
  verb slot, weighted by that association -- an evidence-SELECTED backoff, not a uniform hypernym average.
- **Verdict: a REAL fidelity gap, DE-RISKED to a well-specified next problem (drill-grounded recipe below).**
  The parent measured NAIVE hypernym-averaging HURTS; the drill confirms WHY and gives the faithful fix.
  **Exact recipe (Resnik 1996 + Clark & Weir 2002):** selectional preference strength
  S_R(v) = sum_c P(c|v) log[P(c|v)/P(c)]; per-class association A_R(v,c) = (1/S_R(v)) P(c|v) log[P(c|v)/P(c)],
  with P(c|v)/P(c) estimated by spreading each patient's corpus count across its WordNet sense-ancestor
  classes. Back off an OOV filler n to c* = argmax_c A_R(v,c) over n's OWN ancestor chain, and represent n
  by that class's hub centroid. **Do NOT use naive argmax alone** -- Clark & Weir show it still
  over-generalizes (climbs 4.2 levels, 63.9% pseudo-disambiguation) vs their chi-square evidence-gated
  stopping rule (1.9 levels, 73.9%); a high ancestor class scores spuriously from unrelated verbs (the ATL
  "damaged-hub over-generalization" parallel). **Pre-registered kill-criterion:** HARD-PASS = frequency-
  stratified held-out MRR improves on the OOV/rare bin over drop-OOV with non-overlapping CIs WHILE the
  covered bin does not regress beyond its CI; HARD-FAIL = evidence-gated backoff's rare-bin gain vanishes OR
  covered-bin regresses (then the coverage tail is taxonomically unrecoverable -- do NOT retry uniform
  averaging, already refuted). Not built here (a proper Clark-Weir build is its own problem; a rushed naive
  version would reproduce the known failure) -- handed off with this recipe. It does not help WALL A.

### WALL D -- composition (agent x verb) adds nothing live, is small held-out (+0.018 agent-covered)
- **How the brain does it:** conjunctive role-filler binding (Frankland & Greene 2015). The research drill
  flagged FHRR role(x)filler binding could beat exemplar reweighting on NOVEL (agent,verb) pairs (the
  low-coverage tail), where reweighting needs an attested pair.
- **Verdict: brain-consistent that it is SMALL** (agent coverage 43%; the live pool is selection-flavored),
  but a FHRR-binding composition for novel pairs is an untested micro-opportunity. LOW priority -- the
  representation, not the composition op, is the lever (confirmed; the "MORE IDEAL" integrator was an honest
  negative). Log, do not fund near-term.

---

## PART 2 -- ADJACENT COMPONENTS (capability / limitation / brain-fidelity / opportunity -> next problem)

| component | brain frame + fidelity | limitation (measured on disk) | opportunity -> candidate next problem |
|---|---|---|---|
| **`predictive_reader`** (this problem) | PINNED-in-form (Altmann-Kamide pre-activation; Levy/Hale surprisal). Representation-bounded, now FIXED for prediction (hub +0.076/2.4x). | The live who-did-what flag does not lift (WALL A, brain-consistent). Coverage tail (WALL C). Marginal-only flag (WALL B). | (a) land the hub as the shared foundation asset (P1). (b) Resnik coverage backoff (WALL C). (c) conflict-flag (WALL B) if it lands. |
| **The PARSER front-end** (pos_tagger + arc_parser + role-assigner) | Role-assigner is Competition-Model-faithful (order-dominant + marked override; the owner's NP-head fix added the Right-hand Head Rule). HIGH fidelity. | **The dominant live loss: 27.4% front-end (extraction-miss 8.3% + abstain 10.4% + gold-pron 8.7%) + 32.2% role-pick error.** The organ is a downstream consumer -- garbage in, garbage out. | **Front-end RECALL is the highest-leverage live lever** (extraction-miss + abstain = ~19% of items never reach the predictor). Already an active problem (`the_extraction_front_end_parser_is_the_cross_task_bottleneck`); this quantifies its downstream cost on forward prediction. |
| **`n400_coherence_monitor`** (event coherence, ORGAN F5) | PINNED (Event Segmentation; N400 = coherence error vs running gist). Backward-looking EVENT level. | Consumes a forward surprisal that is coarse; and it is the N400 half -- the semantic-P600 CONFLICT half is absent. | **Build the semantic-P600 conflict/reversal monitor** (WALL B) as the dissociable second error signal -- a distinct organ (Van Herten-Kolk), not a tweak to the N400 monitor. |
| **The situation model / P1** (top-down sense selector) | PINNED (predictive coding; the situation predicts the specific sense/referent). The GENERATIVE half is the north-star. | The un-flaggable ambiguous errors (WALL B share) and the atypical-patient predictions need DISCOURSE/event knowledge (Metusalem) -- which the verb-patient hub does not carry. | **This is where the hub deploys** (fine-grained "which specific one"). The hub built here IS P1's shared representation; the orthogonal strong stream is narrative-chain event knowledge (Chambers-Jurafsky), NOT a same-hub gist (my honest negative). |
| **The HUB representation** (built here) | PINNED (ATL convergent hub; PPMI-SVD as CLS consolidation). Register-general (transfers ~2x cross-register). Surpasses the count ceiling. | Distributional-ONLY (no grounded-spoke fusion; naive concat HURTS -- measured). Vocab-coverage capped (WALL C). | (a) Resnik coverage backoff. (b) a FAITHFUL grounded+distributional FUSION (a DEEP transmodal integration, not concat) -- the north-star's `meaning_fusion` territory; my ideal-system found concat hurts, so this needs a learned fusion, not a bolt-on. |

### Candidate next problems, ranked by leverage x cheapness x brain-fidelity
1. **Front-end RECALL for the extraction organ** -- ~19% of forward-prediction items never reach the
   predictor (extraction-miss + abstain). Highest live leverage; already an active problem, now quantified
   as the forward-prediction bottleneck. Route the funnel numbers to it.
2. **Resnik selectional-association taxonomic backoff** for the hub's rare-filler tail (WALL C) -- cheap,
   brain-faithful, extends the proven prediction lever; naive-hypernym-averaging is the losing control.
3. **The semantic-P600 conflict/role-reversal monitor** (WALL B) -- the dissociable second error signal the
   organ lacks; a distinct organ. Fundable if the conflict-flag test here shows headroom.
4. **(log, do not fund near-term)** FHRR role-filler binding composition for novel pairs (WALL D); a faithful
   grounded+distributional hub fusion (needs a learned integrator, the P1 `meaning_fusion` route).

### One-line reconciliation
The representation is the PREDICTION lever (proven, register-general, delivered as the shared P1 asset); the
live who-did-what ceiling is brain-consistent (selection is order-dominant; ~half the residual errors are
good-enough); the highest-leverage LIVE lever is the PARSER front-end (recall), which the owner is already
improving; the two genuine representation gaps left are the coverage tail (Resnik) and the missing
conflict-monitor error signal (semantic P600).
