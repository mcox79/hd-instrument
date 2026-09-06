---
problem: precision_weight_the_head_driven_readers_on_calibrated_parse_confidence
status: SOLVED
bar: "PASS = precision-weighting the LIVE head-driven readers (who-did-what and at least one of obl / space) by the parser's calibrated confidence lifts COMPREHENSION RELIABILITY on MODERN gold -- a CI-separated selective-accuracy or defer-policy gain over the current blanket reader -- with a RANDOM-confidence info-free twin LOSING (the calibration must be load-bearing, not \"abstaining on anything helps\") and NO-regress on non-consumers (additivity: parse heads unchanged). Report the risk-coverage curve, CI half-width + null p95, recompute floors per population. A rigorous located NEGATIVE -- the calibrated confidence, faithfully wired, does NOT lift a live reader's reliability, with the exact cause named (e.g. the live reader's errors are not attachment-confidence-localized) -- is a FULL PASS."
result: "POSITIVE (CI-separated, twin-controlled, on TWO modern golds + a second head-driven reader). Precision-weighting the DEPLOYED who-did-what PATIENT readout (hdlab.predicate_argument_frontend.structural_patient_pick, the live +0.086 labeled readout) by a calibrated parse confidence lifts SELECTIVE patient accuracy on the confident half from the 0.8789 blanket to 0.9745 (+0.0956, CI[+0.0781,+0.1139], null-p95 +0.0159) on UD-EWT test (n=1255), and 0.2982->0.3414 (+0.0432 CI[+0.0325,+0.0532], null-p95 +0.0106) on QA-SRL (n=8225); the RANDOM-confidence twin is FLAT (UD -0.0017 / QA +0.0009). The SECOND head-driven reader (obl/spatial attachment: which predicate an oblique attaches to = who-is-where) lifts selective attachment 0.7581->0.8919 (+0.1338 CI[+0.1173,+0.1508], null-p95 +0.0153) on UD-EWT obl/nmod (n=2294), twin FLAT (-0.0031). UPSTREAM COMPONENT (fully prototyped + proven to EXCEL): the calibrated confidence separates right-from-wrong patient arcs at AUC 0.858 (parse-features-only 0.777) vs the RAW emitted arc softmax conf 0.615 (UD) / 0.500 (QA) -- the emitted-but-unused signal is near-useless, the calibration is what makes it consumable. ADDITIVE: parse heads unchanged, so every non-consumer is byte-identical (no downstream regression)."
floor: "Per population, the strongest floor is the BLANKET live reader (commit on all, ignore confidence): who-did-what patient 0.8789 (UD-EWT n=1255) / 0.2982 (QA-SRL n=8225); obl/spatial attachment 0.7581 (UD-EWT obl/nmod n=2294). The RELIABILITY-SIGNAL floor is the RAW emitted arc softmax confidence (the signal a naive wire would use): selective@50 who-did-what +0.0206 (UD, within null) / -0.0101 (QA); AUC 0.615/0.500. The calibrated confidence CI-separates above both."
controls: "(1) RANDOM-confidence info-free TWIN (shuffle the calibrated confidence): FLAT at blanket on every reader/gold (who-did-what UD -0.0017 / QA +0.0009; obl -0.0031) -> the calibration is load-bearing, not 'abstaining-on-anything-helps'; its selective@50 CI upper bound IS the reported null-p95, and the real effect clears it 5-9x. (2) PARSE-CONFIDENCE-ONLY ablation (drop the reader's is_labeled_obj branch indicator, keep ONLY the parser's own margins + graded_competition role-entropy): still CI-separated (UD +0.0765 CI[+0.0581,+0.0948]; QA +0.0707 CI[+0.0611,+0.0798]) -> the PARSER's graded confidence (the brief's signal) is itself load-bearing, not just the reader branch. (3) RAW-vs-CALIBRATED (the upstream must add value): raw emitted conf AUC 0.615/0.500/0.721 vs calibrated 0.858/0.620/0.736 -> confirms the settled 'raw margin is a weak lever' negative AND overcomes it via calibration. (4) ADDITIVITY / no-regress: parse_with_conf heads deterministic + read-only over 300 sents (0 head changes) -> non-consumers byte-identical."
files_changed: "experiments/exp_precwt_live_whodidwhat_v1.py (the headline: LIVE who-did-what patient reader precision-weighted on MODERN UD-EWT + QA-SRL; the upstream calibrated confidence + parse-only ablation + risk-coverage + defer-policy + random twin), experiments/exp_precwt_live_obl_space_v1.py (the SECOND head-driven reader: LIVE obl/spatial attachment precision-weighted on MODERN UD-EWT obl/nmod), experiments/exp_precwt_signal_loss_and_fidelity_v1.py (DEEPENING: oracle-ceiling + signal-loss ladder + pinned-entropy-vs-logistic fidelity + the arc-labeler graded-entropy optimization + brain/SOTA anchor), verification/test_precwt_live_readers_organ.py (scaffold-free witness, 5/5: upstream-excels + who-did-what CI-sep + parse-only load-bearing + obl CI-sep + additive/no-regress), notes/problems/precision_weight_the_head_driven_readers_on_calibrated_parse_confidence/SOLVED.md. NO hdlab/ written (Q111 -- prototype; the proposed additive wire is stated below for strategy to land)."
reverify: ".venv/Scripts/python.exe verification/test_precwt_live_readers_organ.py"
---

## SHORT VERSION

The parser already emits a per-arc confidence (`arceager_parser.parse_with_conf` returns `(heads, conf, margin)`)
that **zero live consumers read**. The head-driven readers (who-did-what, obl/spatial) commit to each role
assignment as fact, even when the arc it was read off was a coin-flip. I precision-weighted the LIVE readers by
that reliability signal and measured comprehension RELIABILITY on modern gold:

- **who-did-what PATIENT** (the deployed labeled readout): selective accuracy on the confident half **0.8789 ->
  0.9745** (+0.0956 CI-sep) on UD-EWT, **0.2982 -> 0.3414** (+0.0432 CI-sep) on QA-SRL. Random twin flat.
- **obl/spatial ATTACHMENT** (which predicate an oblique attaches to): **0.7581 -> 0.8919** (+0.1338 CI-sep) on
  UD-EWT. Random twin flat.

The signal is **additive** (parse heads unchanged) so nothing else regresses. The **upstream** brain-foundational
component -- turning the parser's weak raw confidence into a **calibrated** reliability signal -- is what makes it
work: the raw emitted conf is near-useless (AUC 0.615 UD / 0.500 QA), the calibrated confidence is AUC 0.858. This
is the DEMONSTRATED lever from the owner-DONE parser submission (`distributed_contextual_representations...`),
now landed into the LIVE readers on modern gold and extended to a second reader.

This is a POSITIVE result on the **reliability** objective the brief names -- the reader now KNOWS which of its
role assignments to trust. Blanket accuracy is unchanged; the win is that the reader can DEFER on the shaky half.

## 1. HOW THE BRAIN DOES THIS (the opening move; research-verified this session, honestly labeled)

I ran a literature drill (4 parallel lit-scans) specifically to check whether EVERY component is brain-foundational.
The honest verdict -- **PINNED at the computation level, OUR-INVENTION at the application level**:

- **PINNED-BY-EVIDENCE (the computation):** the brain represents an estimate with a graded confidence and uses it
  to weight downstream commitment -- **precision-weighting / inverse-variance cue combination** (Ernst & Banks 2002,
  literal MLE cue integration; Friston 2010 active inference: reliable cue drives belief, unreliable is
  down-weighted, never hard-committed), and **decision confidence gates commitment** (Kepecs et al. 2008 OFC
  vevaiometric signal; Kiani & Shadlen 2009 opt-out/decline when unsure). Comprehension maintains a **distribution
  over parses**, not one tree, and difficulty = its entropy/surprisal (**Hale 2001; Levy 2008; Jurafsky 1996**;
  Kuperberg & Jaeger 2016 parallel-probabilistic + reliability-weighted updating) -- these are Test-of-Time-cited
  and PINNED. The substrate's own landed `graded_competition` organ IS this operation (additive cue activation ->
  softmax = the Bayesian posterior, McClelland 2013; entropy = the gold-free difficulty currency).
- **OUR-INVENTION-UNDER-TEST (the application), honestly flagged:** *no paper tests "parse confidence gates the
  thematic-role readout"* -- it is a two-hop architecture-level extrapolation from (i) perceptual-decision
  confidence + (ii) comprehension-as-distribution. A-priori P ~ 0.30. So it must be TESTED empirically, with the
  info-free twin as the load-bearing discriminator -- which is exactly what the bar demands and what I did.
- **CORRECTION to the word "calibrated" (this matters):** strict CALIBRATION (a confidence that matches
  probability-of-correct) is **NOT** a robust brain property -- humans are systematically mis-calibrated (the
  hard-easy effect: overconfident on hard trials; Baranski & Petrusic lineage; Fleming & Dolan 2012: sensitivity !=
  calibration). What IS brain-robust is confidence **SENSITIVITY** -- the ordering of right-from-wrong (meta-d').
  So I measure **sensitivity** (AUC + risk-coverage monotonicity), NOT strict calibration. The logistic is a
  sensitivity-optimizing readout, not a claim that the brain computes a Platt-scaled probability.
- **The located-negative alternative did NOT occur, and it would have been brain-corroborated:** Christianson et al.
  2001 (garden-path lingering / overcommitment) predicts comprehenders sometimes FAIL to defer even when
  disambiguating evidence is available -- i.e. the reader's errors might NOT be confidence-localized. They ARE
  (the selective curves are steep, twins flat), so the extrapolation holds empirically here.

## 2. THE HEADLINE -- the LIVE readers, precision-weighted, on MODERN gold

I drive the ACTUAL deployed readouts (not a custom experiment reader): `structural_patient_pick` (the live
who-did-what patient, +0.086 owner-DONE) off the substrate's OWN arc-eager parse, and the parser's obl/nmod
attachment (which the live `_pp_args_for_verb` / space register read spatial/oblique roles off). Each role
assignment carries the confidence of the arc it was read from.

**Reader A -- who-did-what PATIENT** (`exp_precwt_live_whodidwhat_v1`):

| gold (modern) | n | blanket | selective@50 (calibrated) | delta CI | null-p95 | twin |
|---|---|---|---|---|---|---|
| UD-EWT test | 1255 | 0.8789 | **0.9745** | +0.0956 [+0.0781,+0.1139] | +0.0159 | -0.0017 |
| QA-SRL | 8225 | 0.2982 | **0.3414** | +0.0432 [+0.0325,+0.0532] | +0.0106 | +0.0009 |

Risk-coverage (UD-EWT, calibrated): 10%=1.000 / 25%=0.987 / 50%=0.975 / 75%=0.964 / 100%=0.879. The reader is
right on ~100% of the arcs it is most confident about and defers on the rest.

**Reader B -- obl/spatial ATTACHMENT** (`exp_precwt_live_obl_space_v1`), the second head-driven reader:

| gold (modern) | n | blanket | selective@50 (calibrated) | delta CI | null-p95 | twin |
|---|---|---|---|---|---|---|
| UD-EWT obl/nmod | 2294 | 0.7581 | **0.8919** | +0.1338 [+0.1173,+0.1508] | +0.0153 | -0.0031 |

Both readers clear their null-p95 by 5-9x with the random-confidence twin flat. The bar's "who-did-what AND at
least one of obl/space" is met, both CI-separated and twin-controlled, on modern gold.

## 3. THE UPSTREAM COMPONENT (fully prototyped) -- and why "wire the raw margin" is NOT enough

The brief and the user's directive both require the UPSTREAM component to be brain-foundational and to EXCEL. The
upstream component is the **calibrated confidence itself**. This is where the prior "confidence-weighting is a weak
lever" finding is reconciled:

- **The RAW emitted arc confidence is a WEAK sensitivity signal** -- AUC(right-vs-wrong) 0.615 (UD who-did-what),
  **0.500 (QA-SRL -- literally chance)**, 0.721 (obl). This CONFIRMS the settled located negative recorded in the
  double-parse-consolidation audit ("roles margin AUC 0.538 deployed"). A naive "just wire the emitted conf" wire
  would fail -- and that is a real, banked finding, not a contradiction.
- **The CALIBRATED confidence EXCELS** -- a glass-box logistic (fit on held-out UD-EWT TRAIN) over the parser's own
  reliability features: the arc-eager softmax conf + raw margin, the GLOBAL `arc_parser` margin, the
  `graded_competition` role-ENTROPY (REUSING the landed organ), the competition breadth, and the labeled-relation
  indicator. AUC **0.858** (UD) / 0.620 (QA) / 0.736 (obl). The **parse-features-only** version (no reader-branch
  indicator -- purely the parser's graded confidence, the brief's signal) is AUC 0.777 and still lifts selective@50
  **+0.0765 CI-sep** -- so the parser's own confidence is load-bearing.

**This is the whole point of the upstream component:** the parser emits a confidence, but the emitted signal is too
weak to consume as-is; the brain-foundational upstream fix is to expose it as a **sensitivity-optimized graded
confidence** (precision / graded competition), which is exactly what the calibration does. "All the way upstream":
the furthest buildable brain-foundational component here is this calibration of the parser's reliability; a fully
intrinsically-graded probabilistic parser (Levy 2008 ranked-parallel) is the named separate north-star (the parser
submission's item), and its value is the SAME calibrated confidence -- which I already extract without rebuilding
the parser. So the chain terminates correctly at the calibration layer for this problem.

## 4. NO-REGRESS ON NON-CONSUMERS (additivity -- confirmed)

The wire ADDS a read-only signal; it changes NO parse head (witness W5: `parse_with_conf` heads deterministic +
read-only over 300 sents, 0 changes). So:

- The **blanket** behavior of every reader (commit on all, ignore confidence) is byte-identical -- the current
  who-did-what/obl accuracy is unchanged (0.8789 / 0.7581).
- Every existing consumer that does not opt to gate on the confidence is byte-identical.
- A consumer that DOES gate (defer/abstain on the low-confidence half) trades coverage for reliability -- that is
  the intended "know what you don't know" behavior, not a regression.

This is the safest possible upstream change: additive, opt-in, zero collateral -- the same additivity the parser
submission proved and the reason this was ranked the safest available lever.

## 5. ADJACENT COMPONENTS -- which consumers to revisit, and their brain-fidelity (the user's directive)

Evaluated each head-driven / role consumer for capability / limitation / opportunity / brain-status:

- **who-did-what PATIENT (demonstrated here).** *Cap:* deployed labeled readout, blanket 0.879. *Opportunity:*
  precision-weight -> the reader defers on its ~12% shaky picks (selective 0.975). *Brain-status:* precision-weighting
  PINNED (computation); the parse->role gate is the tested extrapolation. **Revisit: YES -- consume the confidence.**
- **obl/spatial ATTACHMENT (demonstrated here).** Same upgrade; +0.1338 selective. The live `_read_space`
  LocationRegister reads WHERE off these obl arcs -- it should defer on low-confidence ground attachments (its
  named-ground binding just landed; this is the natural precision-weighted extension, additive-safe). **Revisit: YES.**
- **AGENT (positional / by-phrase / cm_agent).** *Limitation:* the active agent is read POSITIONALLY (nearest
  preverbal nominal), NOT off a parse arc -- so the arc confidence does not directly cover it; the passive agent
  (by-phrase obj) and the cm_agent Competition-Model competition DO expose a margin. *Opportunity:* precision-weight
  the cm_agent competition by its OWN graded_competition margin/entropy (the organ already emits it) -- a distinct,
  clean follow-on. *Brain-status:* the cm_agent competition is already the graded organ; wiring its confidence is
  the same move. **Revisit: YES, via the competition's own margin (not the attach conf).**
- **R_final PATIENT readout (voice+labeled+valency, the sibling).** *Status:* head-INDEPENDENT (0.831, robust to
  parse quality). Precision-weighting the head confidence adds nothing here, and correctly so -- a fallback-to-position
  arm HURT in the parser submission because position is a worse reader than the confident parse. **Revisit: NO** (the
  right fallback is the robust readout, which it already is).
- **coref pick / entity resolver.** Separate binding problem (being wired). NOT a parse-arc consumer -- out of scope;
  additive-composes.

## 6. PROPOSED hdlab CHANGE (Q111 -- strategy lands it)

Purely ADDITIVE, opt-in, default-safe:

1. **Expose the calibrated confidence.** `hdlab/situation_reader._cached_parse_heads` already computes the shared
   per-read parse via `arceager_parser.parse_with_conf` (which returns `conf`, `marg`). Cache `(heads, conf, marg)`
   instead of heads-only (the conf/marg are already computed and discarded). Add a small
   `hdlab/parse_confidence.py` holding the frozen calibration logistic (weights fit offline on UD-EWT train; a
   STATIC glass-box asset -- admissible) mapping a role arc's features -> a sensitivity-confidence in [0,1].
2. **Precision-weight the readers (opt-in flag `precision_weight_roles`, default-OFF for the byte-identical
   landing, then flip-on per the no-more-default-off discipline after the live-board no-regress check).** For each
   role assignment, attach `conf(arc)`; expose it on the EventRecord / role output. A consumer that wants reliability
   reads it and defers (abstains / falls back to its robust readout) below a threshold. The default (no gating) is
   byte-identical.
3. **Do NOT** edit any parse head (additivity is the whole safety argument), **do NOT** wire the RAW emitted conf
   (weak; use the calibrated one), **do NOT** precision-weight the head-INDEPENDENT R_final patient.

Feature parity note for the lander: the calibration features are all glass-box parser outputs (softmax conf, raw
margin, arc_parser margin, `graded_competition` role-entropy, competition breadth, labeled-relation indicator) --
no new model, no LLM.

## 7. WHAT I DID NOT ESTABLISH

- **An absolute-accuracy gain.** The deliverable is RELIABILITY (selective / defer), not higher blanket accuracy --
  as the brief specifies. Blanket is unchanged by construction (additive). A defer policy that FALLS BACK (rather
  than abstains) does not raise absolute accuracy, because the patient is largely head-independent (the sibling's
  finding, reconfirmed): the confident parse is already the best reader, so there is nothing better to fall back to.
  The value is the reader knowing WHICH half to trust.
- **The live LitBank board number.** The board's who-did-what/space gold is 19c (BANNED as load-bearing, owner
  2026-09-06); I measured on modern UD-EWT + QA-SRL per the brief. A 19c additive-no-regress board check is the
  strategy-side landing step, not a headline.
- **Strict calibration.** I measured sensitivity (AUC/risk-coverage), the brain-robust property; I did NOT claim the
  confidence is a well-calibrated probability (the brain is not, either -- section 1).
- **The agent-arc precision-weighting.** The active agent is positional, not a parse arc; I mapped the cm_agent
  competition-margin route (section 5) but did not build it -- a clean filed follow-on.

## 8. KEY REALIZATIONS (the enabling moves)

- **The RAW emitted confidence is the wrong thing to wire; the CALIBRATION is the upstream component.** The single
  arc softmax conf is a chance-level sensitivity signal on QA-SRL (AUC 0.500) and weak on UD (0.615) -- which is
  precisely the banked "confidence-weighting is a weak lever" negative. Reframing the deliverable from "wire the
  emitted conf" to "calibrate the parser's reliability (graded competition / precision), THEN wire it" is what turns
  a settled negative into a CI-separated win (AUC 0.858). The upstream component is not a nicety; it is the fix.
- **Drive the LIVE readout, not a proxy.** The prior submission demonstrated the mechanism on a custom `parse_pick`;
  the risk was that the DEPLOYED reader (labeled readout, valency fallback, quotative, cm_agent) has better,
  differently-distributed errors that might NOT be confidence-localized. Measuring the actual
  `structural_patient_pick` closed that gap: its errors ARE confidence-localized (selective 0.975), so the wire is
  real on the live path, not just on a proxy.
- **The info-free twin is the entire ballgame for a reliability claim.** "Selective accuracy rises on the confident
  half" is trivially true for ANY ranking that correlates with item difficulty -- so the load-bearing number is the
  random-confidence twin staying FLAT (its selective@50 CI upper bound IS the null-p95). Reporting the twin's upper
  bound as the null and clearing it 5-9x is what makes this a calibration result and not an "abstaining helps" artifact.
- **Sensitivity, not calibration, is the brain-robust target.** The research drill's correction (humans are
  mis-calibrated; sensitivity/meta-d' is the robust quantity) told me to measure AUC/risk-coverage, not a
  reliability diagram -- which is both more honest and exactly the quantity a deferring reader needs.
- **The "calibration" IS the pinned organ, not an alien classifier -- and the signal-loss ladder proves where the
  reliability lives.** `logistic = graded_competition.net_activation (additive cue activation) + softmax = the
  Bayesian posterior` (McClelland 2013), weights = learned cue validities (Bates-MacWhinney). The ladder shows the
  parser's own raw confidence captures only 23% of the achievable sensitivity (the greedy parser's impoverished
  posterior -- the upstream deviation), the maintained-distribution entropy adds ~10 points, and the bulk (to 68%)
  is the cue-validity integration of the reader's structural configuration. So "is a single pinned entropy enough?"
  is answered NO -- and that is itself brain-faithful (the brain integrates multiple cues; one cue's entropy is not
  the reliability). The remaining 32% to the oracle is the upstream parser/meaning residual, not a readout deficit.
- **The parse-only ablation separates "parser confidence" from "reader metacognition."** Dropping the is_labeled_obj
  branch indicator (the reader knowing it used its reliable branch) still leaves a CI-separated lift from the
  parser's pure graded confidence -- so the claim "the parser's per-arc confidence is load-bearing" is proven, not
  conflated with the reader's own self-knowledge.

## 9. AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md section 2b -- parser / graded competition)

- The filed follow-on `precision_weight_the_head_driven_readers...` is **realized (prototyped, not yet wired)**: the
  DEMONSTRATED precision-weighting from the parser submission now holds on the LIVE readers on MODERN gold --
  who-did-what patient selective@50 0.8789->0.9745 (+0.0956 CI-sep, UD) / 0.2982->0.3414 (+0.0432 CI-sep, QA-SRL),
  and a SECOND head-driven reader (obl/spatial attachment) 0.7581->0.8919 (+0.1338 CI-sep, UD obl/nmod), random
  twins FLAT, additive (no head change).
- **REFINE the "calibrated confidence" language:** strict calibration is NOT a brain property (hard-easy effect;
  Fleming & Dolan 2012 sensitivity != calibration); the brain-robust and load-bearing property is confidence
  SENSITIVITY (meta-d' / AUC / risk-coverage monotonicity). The audit should record the upstream deliverable as a
  "sensitivity-optimized graded confidence (precision-weighting)", not a probability-calibrated one.
- **RECONCILE the settled negative:** "confidence-weighting is a WEAK end-to-end lever (roles margin AUC 0.538
  deployed)" is CORRECT for the RAW single arc margin (reconfirmed: AUC 0.615 UD / 0.500 QA / 0.721 obl) and does NOT
  contradict this result -- the win is from the CALIBRATED multi-cue confidence (AUC 0.858), which is the upstream
  component the follow-on was filed to build. Record: raw margin = weak (do not wire); calibrated confidence = the lever.
- **NEW brain-fidelity note:** applying decision-confidence precision-weighting to gate the THEMATIC-ROLE readout is
  an architecture-level extrapolation (a-priori P~0.30, tested nowhere in the literature); it is now empirically
  UPHELD on the live readers with info-free twins flat -- a positive on a low-prior mechanism, worth recording as
  OUR-INVENTION-UPHELD (not PINNED). The located-negative alternative (Christianson 2001 overcommitment -> errors
  not confidence-localized) was tested and did NOT occur.

## 10. DEEPENING (owner: optimizations? fully brain-foundational? where do we lose signal vs brain/SOTA?)

Measured directly (`exp_precwt_signal_loss_and_fidelity_v1`, UD-EWT n=1255 / QA-SRL n=8225).

**(a) WHERE we lose signal -- the signal-loss ladder (fraction of the ORACLE reliability ceiling captured; the
oracle = rank the reader's picks by actual correctness -> selective@50 = 1.000 UD / 0.597 QA):**

| confidence source (cumulative) | AUC | captured | selective@50 |
|---|---|---|---|
| S1 raw arc softmax conf (the emitted signal) | 0.615 | **23%** | +0.0206 |
| S2 + global arc_parser margin | 0.600 | 20% | +0.0286 |
| S3 + graded_competition role-entropy | 0.658 | 32% | +0.0478 |
| S4 + arc-LABELER graded entropy (unused organ) | 0.664 | 33% | +0.0509 |
| S5 + reader structural cues (rel/dist/breadth/voice) | **0.841** | **68%** | +0.0876 |

The signal is lost in THREE places, precisely located: (1) the parser's raw confidence captures only **23%** of the
achievable sensitivity -- the greedy hard-commitment parser (margin median 42, commits hard even when wrong) simply
does not expose a rich posterior; (2) the maintained-distribution ENTROPY (graded_competition + labeler) adds only
~10 points -- the difficulty currency helps but is not the bulk; (3) the recoverable bulk (to 68%) is in the
CUE-VALIDITY integration of the reader's structural configuration (grammatical relation, locality, competition
breadth, voice). The remaining **~32%** (to the oracle's 100%) is NOT reachable by any glass-box cue here -- it is
the deep residual (the reader is confidently wrong for a semantic/plausibility reason the structure looks clean
for), which is the parser+meaning gap, upstream of this component.

**(b) ARE WE FULLY BRAIN-FOUNDATIONAL? -- yes at the computation level, with ONE honest upstream deviation.**

- The "calibration" is NOT an alien classifier: `logistic = graded_competition.net_activation` (additive cue
  activation `A = Sigma w_c * support_c`) `+ softmax` = the Bayesian posterior over {correct, incorrect} (McClelland
  2013 -- the SAME pinned operation the landed organ computes), with the fit weights = learned cue VALIDITIES
  (Bates-MacWhinney). The cues (parser graded margins + grammatical relation + locality + competition breadth +
  voice) are all brain-foundational Competition-Model cues. So the upstream component IS the pinned form; I state
  the equivalence rather than shipping a bare logistic.
- **Why the single PINNED entropy alone is weak (AUC 0.54-0.56), and why that is NOT a fidelity failure:** the brain
  integrates MULTIPLE cues into one precision estimate; no single cue's entropy is the reliability. The
  maintained-distribution entropy of ONE decision (the label competition) is one cue among several -- expecting it
  to carry the whole signal would itself be un-brain-faithful. The faithful object is the integrated competition's
  posterior, which is exactly S5.
- **The ONE genuine deviation is UPSTREAM of this component:** the greedy arc-eager parser's own confidence is
  impoverished (captures 23%). A fully brain-foundational INTRINSICALLY-GRADED / ranked-parallel parser (Levy 2008)
  would make the parser's own confidence cue strong and raise the ceiling -- that is the named separate north-star
  (the parser submission's item), NOT this problem. Given the parser it consumes, this component is faithful.

**(c) COMPARISON to the brain and SOTA (the honest anchor):** our FULL confidence sensitivity is AUC **0.841**
(UD who-did-what). Biological decision-confidence sensitivity is AUC **~0.7-0.9** (Kepecs 2008; Kiani & Shadlen
2009) -- we are INSIDE the biological range. Trained selective-prediction / parse-error-detection SOTA
(temperature-scaling, deep ensembles) is AUROC **~0.80-0.85** -- we MATCH or slightly exceed it, glass-box, with NO
trained encoder. So on the reliability-SENSITIVITY objective (the correct one), this is not below SOTA; the gap to
the oracle is the upstream parser/meaning residual, not a confidence-readout deficit.

**(d) OPTIMIZATIONS found (fold into the wire):** (1) INCLUDE the arc-labeler graded entropy -- it is already
emitted by the landed `arc_labeler.label_graded` (AUC 0.930 for LABELING errors) and adds real signal for free
(small for the patient, which is already read off the labeled relation, but free); (2) DROP the global arc_parser
margin from the PATIENT cue set -- it is INERT here (AUC 0.615->0.600), because it is an attachment-site cue, not a
labeled-relation cue (it DID help obl attachment -- so keep it there; use per-reader cue sets); (3) route the
calibration through `graded_competition.net_activation` + `softmax` (it IS that) so the wire reuses the organ rather
than shipping a standalone logistic.

---

### TLDR (plain English)
Before the reader can say who did what or where something is, it has to connect the words with a grammar step.
Right now it commits to every connection as if it were certain -- even the ones that were basically a guess -- and a
downstream that trusts those guesses inherits the mistakes. The grammar engine already produces a "how sure am I"
number for each connection, but nothing looks at it; it is thrown away. I fed that certainty into the two readers
that work out who-did-what and where-things-are, so each one leans on its sure connections and holds back on the
shaky ones. Result, on modern text: when the reader commits only to its more-confident half, it goes from being
right about 88 times in 100 to about 97 in 100 on "who was acted on", and from 76 to 89 on "which action a place or
thing attaches to" -- and a scrambled fake-certainty control does NOT do this, so the certainty is really carrying
information. One important nuance: the raw certainty number the engine emits is nearly useless on its own (on the
harder test it is no better than a coin flip); the piece that makes it work is an upstream step that SHARPENS the
raw number into a trustworthy certainty -- and I proved that upstream step earns its keep. Nothing else the reader
does changes, so nothing breaks. The honest caveat: this "use certainty to decide when to trust the grammar" idea
is well-established for how brains handle perception and simple decisions, but nobody has tested it for grammar
specifically -- so I did, and it works here. The payoff is not a smarter grammar engine; it is a reader that knows
what it does not know, which is exactly what any later reasoning has to stand on.

### QUESTIONS
None. (The mechanism clears the bar's CI-separated + twin-losing + no-regress conditions on two modern golds and a
second reader; the "raw margin is weak" prior negative is reconciled, not contradicted; the calibration-vs-sensitivity
and P~0.30-extrapolation honesty caveats are stated, not worked around. One judgment call: I graded SOLVED because
a real, twin-controlled reliability lift landed on the LIVE readers -- the bar's positive form; the located-negative
alternative was tested and did not occur.)

### NEXT STEPS (ordered)
1. **LAND the additive calibrated-confidence wire (strategy / Q111) -- section 6.** Expose `(heads, conf, marg)`
   from the already-computed shared parse + a frozen glass-box calibration logistic; let the head-driven readers
   opt to precision-weight. Default-OFF for the byte-identical landing, then flip-on after the live-board
   additive-no-regress check (no-more-default-off). This is the reliability SUBSTRATE the reasoning phase stands on.
2. **Precision-weight the AGENT via the cm_agent competition margin** (section 5) -- the active agent is positional,
   not a parse arc, so it needs the Competition-Model competition's OWN graded margin/entropy (already emitted by
   `graded_competition`), a distinct clean follow-on. Same for the space LocationRegister's ground binding.
3. **Add a MODERN who-did-what/obl reliability board arm** -- the current board can't score a selective/defer
   reliability gain (its who-did-what gold is 19c + scores blanket accuracy), so this live gain is board-INVISIBLE
   until it gets its own instrument arm (the recurring live!=scored pattern). Reuse this cell's selective@50 + twin.
4. **DO NOT:** wire the RAW emitted margin (weak, AUC 0.500-0.615 -- the settled negative); chase UAS / build a
   graded parser for accuracy (the parser submission refuted it); precision-weight the head-INDEPENDENT R_final
   patient; or claim strict calibration (measure sensitivity).
