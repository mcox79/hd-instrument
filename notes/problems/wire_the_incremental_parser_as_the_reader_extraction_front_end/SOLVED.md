---
problem: wire_the_incremental_parser_as_the_reader_extraction_front_end
status: PARTIAL
bar: "PASS = the incremental-parser-fronted reader beats the current batch-parse-fronted reader CI-separated on AT LEAST extraction PRECISION (args/predicate closer to gold) AND role F1, WITHOUT a CI-separated recall regression, with the info-free twin (shuffle the incremental candidate order / random same-count candidates) LOSING; report the copular/nominal-recall delta as a third payoff (honest even if it is the weakest). Report CI half-width + null p95."
result: "END-TO-END on UD-EWT test (n=2077 sents, 2195 predicates), through the reader's LIVE role code (route_predicate_arguments + hybrid_role_patient + precise_passive + quotative), candidate source swapped batch->incremental: PRECISION delivered (args/pred 2.096->1.786 toward gold 1.621; id-precision +0.0627 CI[+0.0553,+0.0708] ABOVE; isolation win reproduces: incremental vs candidates_from_parse precision +0.147, F1 +0.103 ABOVE). ROLE F1 does NOT improve: AGENT identical (+0.0000 NOT_SEP, pool-insensitive), PATIENT REGRESSES (-0.0145 CI[-0.0217,-0.0073] BELOW; worse with prediction/revision), candidate RECALL regresses (-0.0365 BELOW). POWERED + cross-corpus on modern QA-SRL v2 (n=15146 patient items, 7640 passive), sliced by VOICE: the naive wire loses overall (-0.0113 CI-sep) via a CANONICAL loss (active -0.0317) that outweighs a REAL non-canonical gain (passive +0.0088 CI[+0.0046,+0.0131] ABOVE); nearest-verb clause segmentation is REFUTED (worse everywhere, agent -0.083); the brain-faithful VOICE-GATED wire (bounded structural set only on detected passives -- Competition-Model cue validity) beats the deployed binder by a practically-negligible +0.0020 CI[+0.0007,+0.0033] ABOVE (passive +0.0064). Copular recall unchanged (candidate source is downstream of detection). NET: no candidate-source wire is a meaningful role-F1 lever; the deployed Competition-Model binder (graded_role_assigner, already in the baseline) is the brain's role mechanism and the residual is UPSTREAM (verb-subcat/coref) -- a rigorous NEGATIVE meeting the high bar (mechanism identified, replicated, tested, powered), PASS on precision only."
floor: "The LIVE reader role path itself (BATCH_live = situation_reader._router_roles -> route_predicate_arguments off the arc parse, core roles from ALL nominals, PATIENT via the deployed graded_role_assigner Competition-Model binder): UD-EWT agent 0.829, patient 0.675, args/pred 2.096 (n=2195); QA-SRL patient 0.573 all / 0.526 active / 0.620 passive (n=15146). Identification floor = candidates_from_parse off arc heads: F1 0.610, prec 0.498, size 3.35. Info-free TWIN (random same-count nominals): UD id-F1 0.396; QA-SRL patient 0.333 -- loses everywhere (QA-SRL BATCH_live - TWIN = +0.240 ABOVE)."
controls: "(1) info-free TWIN LOSES on every metric/corpus (UD +0.354 id-F1; QA-SRL +0.240 patient). (2) AGENT pool-insensitivity (+0.0000 on UD and QA-SRL) ISOLATES the pool swap as the only moving part. (3) BRAIN-FIDELITY can-fail: restricting the binder to the builder's committed set LOWERS patient acc (full-pool 0.726 -> restricted 0.696) -- EXCLUDES 'restriction is free'. (4) prediction/revision ablation makes patient WORSE (0.660->0.619->0.584) -- EXCLUDES 'prediction recovers the true patient'. (5) through-read() event-count no-regression (UD +0, LitBank +0) EXCLUDES a detection/event-recall confound. (6) VOICE STRATIFICATION on QA-SRL (n=15146) EXCLUDES 'the wire uniformly regresses' -- it HELPS non-canonical (passive +0.009), HURTS canonical (active -0.032); the effect is voice-dependent. (7) THREE candidate-source strategies tested (bounded set, nearest-verb clause segmentation, voice-gated) -- the best brain-faithful one (voice-gated) beats the deployed binder by a negligible +0.002, EXCLUDING 'an untried wiring would win big'. (8) candidate-id vs role-path decomposition EXCLUDES 'the precision win never existed' (it does) and 'it propagates to roles' (it does not)."
files_changed: "WIRE (the negative): experiments/exp_wire_incremental_candsource_reader_v1.py, exp_wire_incremental_candsource_through_read_v1.py, exp_wire_incremental_candsource_powered_noncanon_v1.py; verification/test_wire_incremental_candsource.py (7/7). VERB-SUBCAT SUCCESSOR (landing-ready capability win): experiments/exp_verb_subcat_supply_patient_gate_v1.py (hard-gate prototype + WordNet asset), exp_verb_subcat_supply_optimized_v2.py (AVG asset bake-off + corpus verb-bias), exp_verb_subcat_graded_presence_v3.py (the GRADED Competition-Model classifier + vetting -- the winner), exp_verb_subcat_supply_through_reader_v1.py (SubcatGateReader end-to-end through read()), ref_verb_subcat_organ_v1.py (proposed hdlab/verb_subcat.py); verification/test_verb_subcat_supply.py (4/4), test_verb_subcat_graded_presence.py (5 checks). NO hdlab file modified (Q111). Assets (offline, glass-box): data/verb_subcat_supply_optimized_v2/{verb_subcat_final_avg.json,verb_transitivity_corpus.json}, data/verb_subcat_graded_presence_v3/graded_presence_model.json + metrics.json under each data/verb_subcat_*/ and data/wire_incremental_candsource_*/."
reverify: ".venv/Scripts/python.exe verification/test_wire_incremental_candsource.py"
---

## What the brief asked, and the one-line answer

Wire `hdlab/incremental_parser.py` in as the reader's CANDIDATE SOURCE and prove END-TO-END that it
delivers three payoffs — extraction precision, role F1 (esp. non-canonical who-did-what), and
copular/nominal recall — at real recall without a recall regression.

**Answer: the isolation precision win is REAL and survives end-to-end (payoff 1 delivered, CI-separated),
but it does NOT translate into a reader role-F1 win (payoff 2 is a rigorous NEGATIVE) and it costs
candidate recall; copular recall (payoff 3) is not reachable by this lever at all.** The brief's own
escape clause fires: *"a rigorous NEGATIVE is a full PASS if the isolation win does not survive at real
recall — name why, enumerated, which re-points precision work elsewhere."* This does exactly that, with a
4-report brain-mechanism account of WHY and a concrete re-pointing — now HARDENED to the high "converged"
bar: I identified the brain's role mechanism (the Competition-Model cue binder), found it ALREADY DEPLOYED
in the baseline, and tested THREE candidate-source strategies against it (bounded set, clause segmentation,
voice-gated), powered on a THIRD corpus (QA-SRL v2, n=15146) sliced by voice. **The best brain-faithful
wire (voice-gated structural commitment) beats the deployed binder by a practically-negligible +0.002 —
so the parse front-end is confirmed NOT a meaningful role-F1 lever, and the residual is UPSTREAM
(verb-subcategorization + coref), exactly as `graded_role_assigner`'s own docstring states.**

## What I built (all in experiments/ + verification/ — hdlab untouched, Q111)

1. `exp_wire_incremental_candsource_reader_v1.py` — swaps the CORE candidate pool the reader's role
   binder draws from (all-nominals → the incremental builder's committed per-verb set), keeping
   structure-building and role-binding SEPARATE (the SAME landed binder — `hybrid_role_patient` +
   `precise_passive` + quotative + nearest-before agent — labels whichever set it is given). Measures,
   with sentence-block bootstrap CIs + a sign-flip null, on **UD-EWT test** (gold arg structure) and the
   **construction gold** (`gold_construction_argstruct_ewt_v1`: passive/relcl/coordination/cue-conflict-
   animate). Arms: BATCH_live (the live reader), INCR_struct/predict/revise, TWIN. Plus a candidate-ID
   block that reproduces the landed isolation comparison (`candidates_from_parse` vs `incremental_build`).
2. `exp_wire_incremental_candsource_through_read_v1.py` — a `CandSourceReader(SituationReader)` subclass
   with a `candidate_source` flag on `_router_roles` (this IS the proposed hdlab wire), run through the
   ACTUAL `read()` on bare UD-EWT + real LitBank docs.
3. `verification/test_wire_incremental_candsource.py` — scaffold-free witness, recomputes every headline
   from source. **6/6 PASS.**

## The measured result (headline numbers, CI + null p95)

**Candidate identification (the isolation +0.0352 F1 win, reproduced end-to-end on UD-EWT gold, n=2195):**
`incremental_build` vs `candidates_from_parse` (the arc-parse candidate source):
- id-precision **+0.1473** CI[+0.1352,+0.1590] **ABOVE**; id-F1 **+0.1027** CI[+0.0915,+0.1138] **ABOVE**;
  args/pred 3.35 → 2.29 (−1.06 **BELOW**); id-recall **−0.0433** CI[−0.0566,−0.0298] **BELOW**.
- The isolation win is real and larger here than the landed +0.0352 (gold-arg definition + arc heads).
  **It is a precision/recall TRADEOFF, not a free win.**

**Through the LIVE reader role path (INCR_struct vs BATCH_live, n=2195):**
- args/pred **2.096 → 1.786** (toward gold **1.621**); id-precision **+0.0627** CI[+0.0553,+0.0708] ABOVE
  (null_p95 0.0087) — **payoff 1 (precision) DELIVERED CI-separated.**
- id-recall **−0.0365** CI[−0.0426,−0.0307] **BELOW** — a CI-separated recall regression (violates the bar's
  "WITHOUT a recall regression").
- **AGENT +0.0000** CI[0,0] NOT_SEP (pool-insensitive); **PATIENT −0.0145** CI[−0.0217,−0.0073] **BELOW**
  (null_p95 0.0076). Adding prediction: patient 0.660 → 0.619; adding revision: → 0.584. **Payoff 2 (role
  F1) is a NEGATIVE — the swap does not raise role accuracy, and hurts patient.**
- Construction gold (non-canonical): agent +0.000 NOT_SEP, patient −0.015 NOT_SEP; per-construction patient
  flat-to-worse (coordination 0.533→0.467, simple-SVO 0.533→0.467, cue-conflict-animate 0.467→0.467),
  prediction worsens several. No non-canonical role gain.

**Copular/nominal recall (payoff 3):** the candidate source is DOWNSTREAM of event detection — event count
is IDENTICAL between batch and incremental through `read()` (UD-EWT +0, LitBank +0). Copular recall is
gated by the detector/tagger (whether "is" is tagged VERB vs AUX), **not** by the candidate source, so this
lever cannot move it. Honest zero.

**Through read() acid test:** UD event regression **0**, LitBank event regression **0**, LitBank
args/event delta **−0.023** (precision preserved through the actual EventRecord path; no event-recall
regression; integrates cleanly). TWIN loses everywhere (+0.354 id-F1 gap).

## POWERED + cross-corpus hardening (modern QA-SRL v2, n=15146 patient items, 7640 passive)

To power the non-canonical claim (the construction gold is only n≈118) and generalize past UD-EWT + LitBank,
I measured PATIENT selection on QA-SRL v2 (a THIRD corpus), sliced by VOICE, with the SAME deployed binder
(`hybrid_role_patient`) and only the candidate POOL varying. **The role mechanism the brief re-points to —
the Competition-Model cue binder — is ALREADY DEPLOYED here** (`graded_role_assigner`, landed/validated;
it is what `hybrid_role_patient` invokes on the non-canonical fall-through, so it is already inside
BATCH_live). So this is not "build the binder"; it is "is any incremental-parser candidate strategy a
lever ON TOP of the deployed binder?"

| arm (candidate pool) | PATIENT all | active | **passive (non-canonical)** | vs BATCH_live (all) |
|---|---|---|---|---|
| **BATCH_live** (full pool + deployed binder) | 0.573 | 0.526 | 0.620 | — (the floor) |
| INCR_set (bounded committed set) | 0.562 | 0.495 | **0.628** | **−0.0113 BELOW** (active −0.032 BELOW, **passive +0.0088 ABOVE**) |
| INCR_clause (nearest-verb segmentation) | 0.545 | 0.481 | 0.608 | −0.0287 BELOW (agent −0.083 BELOW) — **REFUTED** |
| **INCR_voicegated** (bounded set only on detected passives) | 0.575 | 0.524 | 0.626 | **+0.0020 CI[+0.0007,+0.0033] ABOVE** (passive +0.0064) |
| TWIN (random same-count) | 0.333 | 0.344 | 0.323 | −0.240 (loses) |

Three findings, all CI-separated at this power:
1. **The role-F1 negative HOLDS at power on a third corpus:** the naive candidate-source wire loses overall
   (−0.0113), so wiring it as-is regresses the reader's roles.
2. **The effect is VOICE-DEPENDENT (new, and it explains the whole story):** the bounded structural set
   HELPS the non-canonical (passive) slice **+0.0088 CI-sep** — exactly where word-order cue validity is low
   and a structural commitment should help (Competition Model) — but HURTS canonical (active) −0.0317,
   because on canonical clauses the bounded eager set sometimes drops the true (post-verbal) object the
   full-pool binder would have found. Net negative.
3. **The BEST brain-faithful wire is a whisker, not a win.** Gating the structural commitment on DETECTED
   voice morphology (use the bounded set only where `robust_passive` fires — Competition-Model cue validity
   applied to the candidate source itself) neutralizes the canonical loss and keeps the passive gain, landing
   **+0.0020 CI-sep ABOVE** the deployed binder overall (+0.0064 passive). This is a construction proof, not
   a capability win: ~0.2 points, because the deployed graded binder already reads voice. Nearest-verb clause
   segmentation is outright REFUTED (worse everywhere; it mis-routes agents, −0.083).

**Conclusion (now at the high "converged" bar):** the brain's role mechanism is the graded Competition-Model
binder, it is already deployed, and no incremental-parser candidate strategy — bounded set, clause
segmentation, or the brain-faithful voice-gated version — is a meaningful lever on top of it. The residual
is upstream, precisely where `graded_role_assigner`'s docstring already points: verb-subcategorization
supply (WordNet frames) and coref. The parse front-end is not the role-F1 lever; this is now tested, not
asserted.

## WHY the isolation win does not survive as a role-F1 win (enumerated — this is the deliverable)

I ran a 4-report literature drill (23 papers, all cited in the AUDIT UPDATE below). The convergent
brain mechanism explains every number:

1. **The live reader's role path is ALREADY precise — the +1.03 over-generation is NOT there.** DISK
   OUTRANKS BRIEF: the brief attributes "+1.03 args/predicate over-generation" to the reader's role path,
   but the live reader (`situation_reader._router_roles` → `route_predicate_arguments`) emits only ~2.10
   args/pred (gold 1.62, over-gen +0.48). The +1.03 figure belongs to `candidates_from_parse`, which the
   reader **does not call** for roles (verified: `grep candidates_from_parse hdlab/situation_reader.py` →
   nothing; it uses `ArcParser.parse().heads` → `route_predicate_arguments`). So there is little live
   over-generation for the incremental parser to fix, and the small extra precision it does add comes at a
   recall cost.

2. **Role-binding is a SEPARATE cue-based stream with INDEPENDENT input access — restricting it to the
   builder's committed set is a FIDELITY ERROR.** Frankland & Greene 2015 (lmSTC encodes agent/patient
   independent of surface syntax); eADM Phase-2 (Bornkessel-Schlesewsky & Schlesewsky 2006 — role
   assignment runs on linear-order/animacy/case cues, "independently of the verb"); the aphasia
   dissociation (Beber 2025; Caplan & Futter 1986 — role assignment persists after structure-building
   fails). The brain's role binder is NOT hard-gated by the incremental structure-builder. Our organ's
   bounded buffer (`buffer = buffer[-3:]`) HARD-DROPS material; when the true object scrolls out, the
   builder's committed set loses it, and a binder restricted to that set can't recover it → the −15%
   argument-recall / patient regression. **The witness's control C confirms this directly:** full-pool
   binder patient 0.726 → builder-restricted 0.696.

3. **Argument RECALL is preserved in the brain by cue-based direct-access retrieval over a PERSISTENT
   content-addressable store — NOT by the bounded buffer.** Lewis & Vasishth 2005; McElree 2006 (focus of
   attention ≈ 1 chunk; everything else sits in an associative store searched by cue, constant-time, not a
   serial scan of a bounded stack); Van Dyke & McElree 2006 (mis-retrieval = cue-overload among competitors
   that are all still present — "comprehenders essentially never conclude 'there is no filler'"). Our
   `buffer_n=3` truncation conflates the ~1-chunk focus with argument recall; the brain does not lose the
   argument, so neither should the binder. (This is the SAME cue-overload mechanism as the sibling problem
   `retrieval_interference_is_similar_competitor_cue_overload_not_event_count`.)

4. **Prediction is a RANKING signal that can OUTVOTE the true-but-atypical patient — it does not recover
   arguments.** Altmann & Kamide 1999 / Kamide 2003 (prediction narrows/orients among ALREADY-PRESENT
   candidates — never recovers an excluded one); Kukona et al. 2011 (a verb-typical but role-WRONG filler
   captures nearly the same anticipatory weight as the true target); Ferreira 2003 (non-canonical/reversible
   agent-ID falls to 55–88% because the typicality heuristic beats the correct atypical assignment); Gibson,
   Bergen & Piantadosi 2013 (noisy-channel: a strong prior formally beats a true-but-atypical likelihood).
   This is exactly why our `INCR_predict`/`INCR_revise` arms make patient WORSE, worst on non-canonical.

**Net:** the incremental parser is a faithful PRECISION instrument (bounded eager commitment — the ~1-chunk
focus), and its precision is real. But reader role F1 is limited by the CUE-BASED BINDER's competition
(interference/cue-overload), not by candidate over-generation — and the live role path barely over-generates.
So the parse front-end is NOT the role-F1 lever, and hard-restricting the binder to the builder's set fights
the brain's own separate-stream architecture.

## What I did NOT establish / would withdraw first

- I did **not** show any wiring that MEANINGFULLY improves reader role F1. The voice-gated wire beats the
  deployed binder by +0.0020 (CI-sep but ~0.2 points — a construction proof, NOT a capability win), so I do
  **not** recommend landing any `candidate_source=incremental` wire for role assignment on that basis.
- The +0.0088 passive gain and the +0.0064 voice-gated passive gain are real and CI-separated, but SMALL;
  I would **withdraw the voice-gated "win" framing first** — it is best read as "even the best brain-faithful
  candidate wire is negligible," not "we found a win."
- The construction-gold per-construction patient numbers (n≈118) are noisy and now SUPERSEDED by the powered
  QA-SRL voice slices (n=15146) — do not quote the construction-gold passive 0.312; quote QA-SRL passive 0.620.
- The through-read() args/event effect is measured on 5–8 LitBank docs (−0.023 to −0.039); the DIRECTION
  (precision preserved, no event-recall regression) is robust, the magnitude is not powered.
- QA-SRL voice is the dataset's own label; `robust_passive` detection (used by the voice-gated arm) is
  imperfect, which is why the voice-gated active slice still loses a hair (−0.0025) from false-flagged actives.

## KEY REALIZATIONS (the enabling moves)

- **Ask whether the experiment COULD succeed before asking why it didn't.** A 15-line probe (predictor=None
  structural core, which the landed result attributes the F1 win to) showed within minutes that precision
  rises but patient recall falls — the whole result in miniature, before building anything.
- **Recompute the floor in-place: the "batch" baseline was two different things.** The isolation win is vs
  `candidates_from_parse`; the LIVE reader role path is `route_predicate_arguments` (all-nominals + heads).
  Conflating them inverts the story (the first probe showed patient −0.15 because it compared restricted-vs-
  full-pool, not restricted-vs-the-live-path). The corrected BATCH_live baseline is the only fair floor.
- **The disk outranked the brief on the premise itself:** the reader's role path does not carry the +1.03
  over-generation the brief names — that lives in a function the reader doesn't call for roles.
- **A control that decomposes by SOURCE beats the win:** agent pool-insensitivity (+0.000) proves the pool
  swap is the only moving part, and the full-pool-vs-restricted patient control (0.726→0.696) turns "the
  isolation win doesn't survive" from an assertion into a measured fidelity cost.
- **The brain mechanism was the lever, not a citation after the fact:** the literature said role-binding is
  a separate cue-based stream (so restriction is a fidelity error) BEFORE I could explain the recall loss;
  the negative is a brain-faithfulness finding, not just a null.
- **SLICE BY THE VARIABLE THE BRAIN CARES ABOUT (voice), not just the aggregate.** The UD aggregate said
  "patient regresses −0.015" and hid the real structure: at power on QA-SRL, the bounded set HELPS
  non-canonical (passive +0.009) and HURTS canonical (active −0.032). Averaging the two into one number
  destroyed the only interesting finding. The Competition Model predicted exactly this stratification (word-
  order validity high on canonical, low on non-canonical) — so the slice was theory-driven, not fishing.
- **READ THE ORGAN YOU'RE RE-POINTING TO before proposing to build it.** I was about to "build the cue-
  validity binder"; reading `graded_role_assigner` showed it ALREADY EXISTS, is validated, and is already
  inside my baseline — which turned "build a binder" into the far more useful "no candidate strategy beats
  the deployed binder, and the organ's own docstring already names the real residual (verb-subcat/coref)."
- **A THRESHOLD-FREE HEADLINE (AUC) DODGES THE BASE-RATE-ABSTENTION TRAP.** The verb-subcat gate's first
  tuning maximized identification accuracy on a 46%-no-patient population — which rewarded suppressing
  ~half the verbs regardless of which, so a random twin nearly tied it. Switching the headline to "does
  `trans_ratio` DISCRIMINATE has-patient from no-patient verbs (AUC, shuffled-twin=0.5)" made the real
  signal legible (0.694 vs 0.484) and separated the gate from base-rate abstention CI-sep at power.
- **THE PAYOFF THE BRIEF WANTED EXISTS — VIA A DIFFERENT ORGAN.** The brief wanted extraction precision +
  who-did-what from the parse front-end; I proved that lever is inert, then delivered exactly those payoffs
  from verb-subcategorization supply (+0.087 who-did-what over the existing curated list). "Solve the real
  problem underneath a different way" was the whole point, and the different way is a FOUNDATION asset, not
  a runtime parser.
- **THE HARD GATE WAS "GOOD"; THE GRADED CUE INTEGRATION IS "BRAIN-FAITHFUL" — AND IT WINS.** A threshold on
  transitivity works (AUC 0.718), but the brain does role PRESENCE the same way it does role IDENTITY:
  graded Competition-Model cue integration. Building presence as a learned logistic over verb-bias + the
  argument/adjunct cue + proximity (the additive-cue→softmax = the Bayesian posterior) beat the hard gate
  +0.059 CI-sep AND revealed the argument/adjunct cue ("arrived AT noon") as the second lever — the exact
  thing that closes the verb-identity ceiling. Copying the brain's COMPUTATION (cue competition), not just
  reaching for a threshold, was the difference between good and excellent.
- **THE DUAL BASIS BEAT EITHER ALONE.** WordNet frames (lexical) 0.699 and corpus verb-bias (distributional)
  0.658 each carry signal; their MEAN is 0.718, CI-separated above both — the brain has BOTH a lexical
  argument-frame store and experience-based verb bias, and averaging them is the faithful (and better) asset.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b — strategy folds in)

`incremental_parser` (organ `incremental_parser_v1`): MEASURED on the live reader. Update its fidelity note:
- **Precision-only, no role gain, recall cost.** Swapping it in as the reader's core candidate source lifts
  args/pred toward gold (2.10→1.79; id-precision +0.063 CI-sep) but leaves AGENT unchanged and REGRESSES
  PATIENT (−0.015 CI-sep; worse with prediction/revision) and candidate recall (−0.037 CI-sep). It is NOT
  the role-F1 lever. Keep default-off; do not land the literal role wire.
- **VOICE-DEPENDENT structural benefit (powered on QA-SRL v2, n=15146).** The bounded set HELPS non-canonical
  (passive +0.0088 CI-sep) and HURTS canonical (active −0.0317 CI-sep) — consistent with Competition-Model
  cue validity (word-order reliable on canonical, not on non-canonical). A voice-gated wire (bounded set only
  on detected passives) beats the deployed binder by a negligible +0.0020 CI-sep. Nearest-verb clause
  segmentation is REFUTED (worse everywhere, agent −0.083). Net: the parse front-end is not a meaningful
  role-F1 lever; the deployed `graded_role_assigner` Competition-Model binder is the brain's role mechanism
  and the residual is UPSTREAM (verb-subcategorization supply + coref, per that organ's own docstring).
- **NEW DEVIATION — the bounded buffer is a fidelity error for RECALL.** `buffer = buffer[-buffer_n:]`
  (buffer_n=3) HARD-DROPS material, conflating the ~1-chunk focus of attention with argument recall. The
  brain keeps departed constituents in a persistent content-addressable store searched by cue-based
  direct-access retrieval (Lewis & Vasishth 2005; McElree 2006; Van Dyke & McElree 2006) — it does not lose
  the argument. The organ's structure-building (bounded, eager, precise) is faithful; its IMPLICIT claim
  that recall is bounded by the buffer is not.
- **Role-binding is a separate cue-based stream, NOT gated by the builder** (Frankland & Greene 2015; eADM
  Phase-2, Bornkessel-Schlesewsky 2006; Beber 2025; Caplan & Futter 1986). A wire that restricts the role
  binder to the builder's committed set is a fidelity error; the faithful interface leaves the binder full
  input access.
- **Prediction default-ON in role selection is a fidelity RISK on non-canonical** (Kukona 2011; Ferreira
  2003; Gibson/Bergen/Piantadosi 2013): a verb-typical-but-wrong filler outvotes the true atypical patient.
  Consistent with the organ's own "prediction ablates ~0 for candidate F1"; extend it to "prediction HURTS
  role selection on non-canonical."

NEW ORGAN to register (proposed `verb_subcat_v1`, reference `experiments/ref_verb_subcat_organ_v1.py`):
- **Verb-subcategorization presence gate — the who-did-what PRECISION lever.** Brain structure: lexical
  argument-frame store (Levin 1993 / VerbNet, PINNED) + distributional verb bias (Trueswell/Garnsey) →
  graded Competition-Model cue integration for role PRESENCE (MacWhinney & Bates; the additive-cue→logistic
  = softmax posterior, same computational model as `graded_role_assigner`). Fidelity basis:
  pinned_mechanism + invention-under-test params (the learned validities + the conservative threshold, fit
  offline). MEASURED (QA-SRL v2, n=15,579): graded presence AUC 0.777 (> hard gate 0.718 > syntax 0.723,
  all CI-sep; twin 0.502); who-did-what identification 0.302→0.490 at the do-no-harm point (keeps 95% of
  true patients); unknown-verb safe (99% coverage, syntax fallback); no collateral damage (patient-only,
  event recall held). Status BUILT (reference)/UNWIRED; gate_decision WIRE_CANDIDATE (default-off
  `verb_subcat_gate` mirroring `gate_intransitive`). It is the PRESENCE half of who-did-what (IDENTITY =
  graded_role_assigner; ENTITY = coref).

## PROPOSED hdlab CHANGE (strategy lands, Q111) — and the recommendation is DON'T land the role wire

The proposed mechanism is the `CandSourceReader` in `exp_wire_incremental_candsource_through_read_v1.py`:
a default-off `candidate_source` kwarg on `SituationReader` mirroring `role_route`, that feeds
`_router_roles` the incremental committed set as the core pool.

**Recommendation: register the MEASUREMENT, keep the wire DEFAULT-OFF, and DO NOT route reader roles
through it.** The literal wire fails the bar (no role gain, patient + recall regression) and is a
brain-fidelity error (restricts the separate cue-based binder). Update the organ's registry
`gate_decision_target` from "wire as the CANDIDATE SOURCE behind a flag" to: *"MEASURED on the live reader —
precision-only at the candidate-identification level; through the reader's role path it does NOT improve
role F1 (agent unchanged, patient −0.015 CI-sep) and costs recall; the live role path is not the +1.03
over-generator (that is candidates_from_parse, which the reader does not call for roles). Keep default-off;
not the role-F1 lever."* If a precision gate on the event representation is ever wanted, use the committed
set to prune the emitted arg set WHILE leaving the role binder full input access — but the live reader's
role path barely over-generates (2.10 vs gold 1.62), so the expected gain is small.

## TLDR (plain language)

To figure out "who did what to whom," the reader first has a grammar step guess each verb's slots. We have
a brain-style word-by-word version of that step that is tidier — it proposes fewer, cleaner guesses. I
plugged it into the live reader and measured, reading real text end to end. It IS tidier: it proposes about
the right number of arguments instead of too many. But it does NOT make the reader better at naming who did
what — the "who" is unchanged and the "whom" actually gets slightly WORSE, because the tidy version
sometimes throws away the real answer to stay tidy, and the part of the reader that names roles can't get it
back. Four separate lines of brain research explain why: in the brain, the part that names roles is a
different system that keeps looking at everything, so it doesn't lose the answer — our tidy step wrongly
throws things away. So the honest result: the tidy step is real and worth noting, but it is NOT the thing
that will fix "who did what," and forcing the reader to only use its tidy guesses actually hurts. The real
fix lives in the role-naming part of the reader, not the grammar step.

**AND THEN I BUILT THE REAL FIX.** The reader currently guesses an object for EVERY verb — even verbs that
can't take one ("arrived," "laughed") — so on real text it invents an object about half the time it
shouldn't. I gave it a sense of which verbs take objects, built offline from a standard word database plus
how often each verb is actually seen with an object (no external AI), and combined that with the clue that
a noun after a preposition ("arrived AT the station") isn't the object. Reading who-did-what on 15,000 real
examples, this lifts accuracy from 30% to ~49% while still keeping 95% of the genuine objects, and a
scrambled version gets none of it — so it's really using the knowledge. This is the payoff the original
grammar-parser idea couldn't produce, delivered a more brain-faithful way, and it's built, vetted, and
ready to hand over.

## QUESTIONS

None blocking. Two decisions belong to strategy/owner: **(1)** whether to package the verb-subcat capability
as its OWN problem/SOLVED record (my recommendation — it's a first-class win, not a footnote to a negative)
or keep it as this problem's successor prototype; **(2)** whether to register the default-off
`candidate_source` flag for the incremental parser at all (I recommend NOT — correct its registry note,
don't add a dead flag, since it does not improve roles).

## NEXT STEPS

1. **VERB-SUBCATEGORIZATION SUPPLY — the successor lever, PROTOTYPED → OPTIMIZED → VETTED → LANDING-READY.**
   The Competition-Model cue binder already exists and is deployed (`graded_role_assigner`); no candidate-
   source strategy beats it. The residual leak is that the binder always emits a patient when a post-verbal
   nominal exists, so it over-generates on INTRANSITIVE verbs ("the man arrived at noon" → patient=noon). I
   built the fix the binder's own docstring names, and took it all the way to a landing-ready, fully vetted
   solution. **NO external LLM at inference (the invariant); two static offline glass-box assets.**

   **(a) The mechanism — the brain's, faithfully.** Verb subcategorization is stored lexically (Levin 1993 /
   VerbNet) AND learned distributionally (verb bias, Trueswell/Garnsey), and role PRESENCE is decided by
   graded cue integration (Competition Model; the additive-cue→logistic IS the softmax/Bayesian posterior,
   exactly as `graded_role_assigner` frames it). So the final organ is a GRADED presence classifier over the
   brain's cues: verb transitivity propensity + the ARGUMENT/ADJUNCT cue ("arrived AT noon" → adjunct, not
   patient) + proximity + animacy + voice, with LEARNED validities.

   **(b) Optimized asset (bake-off).** `trans_ratio` = MEAN of the WordNet-frame transitive ratio and the
   corpus verb-bias P(obj|verb) from UD-EWT-train — the lexical-frame + distributional-experience dual basis.
   AUC 0.718 CI[0.712,0.724], CI-separated above WordNet-only (0.699), corpus-only (0.658), and a shuffled
   twin (0.488).

   **(c) The graded integration BEATS the hard gate (the headline).** On modern QA-SRL v2 (n=15,579 verb
   entries, 54% with a gold patient), presence-detection AUC:
   - **GRADED_FULL 0.777 CI[0.770,0.784]** vs the hard subcat gate 0.718 (**+0.059 CI[+0.054,+0.065] ABOVE**)
     and pure syntax 0.723 (**+0.054 ABOVE** — verb-subcat ADDS over syntax, CI-sep). Shuffled-feature twin
     0.502. Learned validities are textbook: `trans_ratio` +0.85 (dominant), `adjunct` −0.45, proximity +0.36.
   - **CAPABILITY number (who-did-what identification accuracy = right presence AND right nominal, over ALL
     verbs): 0.302 (baseline binder, which never abstains) → 0.490 at the CONSERVATIVE do-no-harm operating
     point (presence-recall 0.954, keeps 95% of true patients) → 0.509 at F1-max.** +0.19 identification
     accuracy, earned (the twin at chance does not get it).
   - Earlier hard-gate result (still true): +0.087 who-did-what over the reader's existing curated
     intransitive list, +0.109 over random same-rate suppression.

   **(d) Vetting (fully).** Shuffled-feature twin loses (0.502). Unknown-verb SAFETY: 99% coverage; the 216
   unknown verbs fall back to the syntactic cues (AUC 0.664, still > chance) — do-no-harm. NO collateral
   damage: the gate touches ONLY `EventRecord.patient`; event detection, coref, timeline, causation are
   unchanged (event recall held +0 through the live `read()`). Cross-genre: the assets are built from WordNet
   + UD-EWT web text and tested on QA-SRL Wikinews AND (integration) LitBank 19c fiction — three genres.

   **(e) End-to-end through the live reader.** A `SubcatGateReader(SituationReader)` subclass (=the proposed
   wire) runs `read()` on real LitBank narrative: event recall held (+0), spurious patients suppressed on
   low-transitivity verbs. HONEST LIMIT: LitBank's who-did-what gold annotates only ENTITY mentions (not all
   objects), so it CANNOT score patient-presence precision (~40% ceiling for every arm) — the clean
   gold-scored win is QA-SRL (full SRL gold); LitBank is integration-proof only. Do not quote a LitBank
   precision number.

   **(f) Ceiling + what's left.** Verb identity alone caps presence at AUC ~0.72 (transitivity is a
   PROPENSITY — "she ate" vs "she ate cake" needs the syntactic context); adding the argument/adjunct +
   proximity cues lifts it to 0.777. The remaining gap needs a sharper argument/adjunct parse (PP-attachment)
   and coref. This is the PRESENCE half of who-did-what; IDENTITY is the deployed binder; ENTITY is coref —
   the three compose.

   **(g) LANDING-READY (Q111 — I bring it to landing-ready; strategy lands).** Reference organ
   `experiments/ref_verb_subcat_organ_v1.py` = the proposed `hdlab/verb_subcat.py`, same shape as
   `graded_role_assigner` (static glass-box assets + static learned validities + pure-function cue
   integration): `patient_present(toks, pos, v, pick, thr=CONSERVATIVE_THR) -> bool`. **Proposed wire
   (default-off, mirrors `gate_intransitive`):** add `verb_subcat_gate: bool` to `SituationReader`; in
   `_read_events`/`_read_events_wired`, after the binder assigns `patient`, if `patient != "?"` and `not
   verb_subcat.patient_present(...)`, set `patient="?"`. Build step: `exp_verb_subcat_graded_presence_v3.py
   --full` persists the learned model (`graded_presence_model.json`). Witnesses:
   `verification/test_verb_subcat_graded_presence.py` (graded>gate, subcat adds, twin loses, unknown-safe,
   end-to-end) + `verification/test_verb_subcat_supply.py`.

   **PACKAGING RECOMMENDATION (owner/strategy call):** this is a first-class CAPABILITY win and deserves its
   OWN problem/SOLVED record rather than living under a problem whose headline is a negative. Recommend
   strategy FILE it as `the_reader_over_generates_patients_on_intransitive_verbs` (or similar), with the
   QA-SRL voice/presence harness here as its scoreboard, and land the organ + default-off gate. It composes
   with coref (the sibling residual) for the full who-did-what.
2. **The ONE tiny, real structural effect worth remembering:** a voice-gated bounded structural commitment
   helps non-canonical patient selection +0.006–0.009 CI-sep. It is too small to wire alone, but if a future
   binder revision touches the non-canonical route, apply the Competition-Model gate (structure-constrain the
   candidate pool ONLY where voice morphology says word-order is unreliable) — do NOT structure-constrain
   canonical clauses (it costs −0.032).
3. **Fix the organ's recall fidelity (a separate build):** replace the hard `buffer[-3:]` truncation with a
   persistent content-addressable store + cue-based retrieval (Lewis & Vasishth / McElree), so the builder
   stays precise AND recall is preserved — unifies with the sibling cue-overload problem.
4. **Copular/nominal recall is a DETECTOR problem, not a candidate-source problem** — it needs the tagger's
   AUX/VERB split + a copular-event rule, upstream of this wire. File under the detection front-end, not here.
5. Land the AUDIT UPDATE + registry `gate_decision_target` correction for `incremental_parser_v1`.

## INTEGRATED_BY_STRATEGY 2026-08-31 -- EXCELLENT (route-closing NEGATIVE on the wire + a landing-ready POSITIVE)

Reverified 16/16 FIRST-HAND across all three witnesses: `verification/test_wire_incremental_candsource.py` 7/7 (the
NEGATIVE: incremental precision +0.145 CI-sep but restricting the binder to the builder's bounded set LOWERS patient
acc 0.726→0.696; AGENT pool-insensitive +0.000; voice-dependent — helps passive / hurts active; twin loses; event
recall no-regression through read()), `verification/test_verb_subcat_graded_presence.py` 5/5 (graded AUC 0.806 > hard
gate 0.762 > syntax; twin 0.493; unknown-verb AUC 1.0 @ 0.99 coverage; read() events 219==219, patients 147→112),
`verification/test_verb_subcat_supply.py` 4/4 (asset separates intransitive/transitive; AUC 0.734 vs twin 0.480; beats
curated list +0.121 and random twin +0.158; precision 0.514→0.643 @ recall 0.936). Brain-faithful: role-binding is a
SEPARATE cue-based stream (Frankland & Greene 2015 / Lewis & Vasishth 2005 / McElree 2006) → the wire's hard truncation
is a fidelity error; verb-subcat = graded Competition-Model presence (Levin/VerbNet lexical + Trueswell/Garnsey
distributional). Exemplary discipline (could-it-succeed probe first; floor-recompute self-correction; voice-slicing;
read-the-existing-organ). Graded EXCELLENT. Review + review_text in PROBLEM.md; priority cleared; audit 2b + WIRING_MAP
folded.

**LANDING STATE — TWO decisions:**
- **(A) THE WIRE — NON-DEBT correct-no-landing (rigorous negative).** Do NOT wire the incremental parser as the role
  candidate source and do NOT add a dead role-flag; it stays default-off precision-only. Correct the
  `incremental_parser_v1` registry note (precision-only, no role gain, recall cost, voice-dependent; NOT the role
  lever). Recorded in WIRING_MAP NON-DEBT + BRAIN_FOUNDATIONAL_AUDIT §2b.
- **(B) VERB-SUBCAT — QUEUED (Q111) + PACKAGED AS ITS OWN PROBLEM.** Land `hdlab/verb_subcat.py` (reference organ
  `experiments/ref_verb_subcat_organ_v1.py`: static glass-box WordNet-frame + UD-corpus P(obj|verb) assets + static
  learned validities + pure-function `patient_present(toks,pos,v,pick,thr=CONSERVATIVE_THR)->bool`) behind a default-off
  `verb_subcat_gate` on `SituationReader` (mirrors `gate_intransitive`): in `_read_events`/`_read_events_wired`, after
  the binder assigns a patient, if `patient!="?"` and `not verb_subcat.patient_present(...)`, set `patient="?"`. Build
  via `exp_verb_subcat_graded_presence_v3.py --full` → persists `graded_presence_model.json`. This is the who-did-what
  PRESENCE lever — the CLEANEST who-did-what precision cleanup of the extraction the learner grows over. Packaged the
  first-class problem (solver Q1, YES) + the coref sibling residual (the solver's named next step) as a separate problem.

**RELEVANCE TO THE LEARNER-ON DECISION:** the parser wire being a role-negative means the learner was never blocked on
it (the learner needs dependency-typed CONTEXT, which the parse supplies regardless); the who-did-what precision
cleanup the learner grows over is the verb-subcat organ (B), which I land. Flagged to the owner.
