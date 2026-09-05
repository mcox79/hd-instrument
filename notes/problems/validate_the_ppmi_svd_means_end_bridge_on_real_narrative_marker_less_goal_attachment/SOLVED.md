---
problem: validate_the_ppmi_svd_means_end_bridge_on_real_narrative_marker_less_goal_attachment
status: REFUTED
bar: "PASS = the PPMI+SVD means-end bridge validated on REAL LitBank marker-less actions with a COVERAGE CURVE, wired as a RELIABILITY-GATED edge type in build_goal_graph (fires only when a goal is on the open-stack AND the fit clears the margin), lifting isolated-goal attachment CI-separated over the recency-0.0 floor, with an info-free shuffled-index twin LOSING and NO-regress on the explicit-chain goal arm; the honest ATOMIC verb-coverage bound reported (softened by the SVD generalization). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — the bridge cannot generalize to real marker-less actions beyond ATOMIC coverage (with the named coverage number) — is a FULL PASS."
result: "The info-free twin does NOT lose on real narrative, so the bar is not met -- and it is a RIGOROUS located negative (which the brief names a FULL PASS), with a cause DIFFERENT from the one the brief predicted. On 336 real LitBank purpose_bare (action->purpose) pairs, matched-population means-end discrimination (pick the true purpose among {gold + K real-purpose distractors}, distractors drawn per-item deterministically and AVERAGED over 25 draws): CONTAMINATED (all extractions) K1 bridge 0.559 vs info-free shuffled-map twin null p95 0.533 (NOT separated; full-stack ci_lo 0.489<0.533), K3 bridge 0.309 vs twin p95 0.283 (full ci_lo 0.239<0.283). Cleaning the upstream to only spaCy-advcl-genuine purposes LIFTS absolute accuracy (CLEAN K1 raw 0.595 > CONTAMINATED 0.559) but STILL does not separate from the twin (CLEAN K1 full 0.586 ci_lo 0.510 vs twin p95 0.574; K3 full 0.338 ci_lo 0.259 vs twin p95 0.315). The bridge's apparent discrimination is a goal-FREQUENCY/centrality artifact the info-free twin reproduces. Mechanism-diff: the gold narrative purpose appears in ATOMIC's top-10 typical-intents FOR THE ACTION in only 1/201 covered pairs -- context-free typical-intent does not match context-specific authorial purpose. The n=16 authored PoC 0.9375 was an overfit to hand-authored easy contrasts (cook->sleep obviously wrong)."
floor: "Strongest floor actually run = the INFO-FREE shuffled-map TWIN, recomputed per population (200 draws): null p95 = CONTAMINATED K1 0.533 / K3 0.283, CLEAN K1 0.574 / K3 0.315 -- the bridge does NOT clear any of them CI-separated. Weaker floors also run: RANDOM/chance (1/(K+1) = 0.50 at K1, 0.25 at K3); and the recency floor from the earlier in-context design (natural-discrimination recency 0.303, distance-controlled recency 0.0) -- the bridge's lift over recency was itself a prior/frequency artifact (the twin, which keeps that prior, matches the bridge)."
controls: "(1) INFO-FREE TWIN = shuffled action->embedding map (each action rewired to a uniformly-random action's means-end embedding, keeping goal embeddings + candidate structure + goal prior; 200 draws) -- EXCLUDES 'the win is a real action-specific means-end signal': it is not (twin matches the bridge on every population/K). (2) MATCHED-POPULATION distractors (K real purposes as distractors, per-item deterministic seed, averaged over 25 draws) -- EXCLUDES the population-mismatch confound that inflated an earlier uniform-distractor probe. (3) spaCy-advcl PRECISION ORACLE (offline, measurement-only, never runtime) -- LOCATES the upstream wall: bare-purpose extraction precision 0.270 (216/296 are complement/causative/modal errors: xcomp 174). (4) UPSTREAM-CLEAN slice (advcl-only) -- EXCLUDES 'the negative is only bad extraction': the twin still does not lose on clean purposes. (5) DIAGNOSTICITY normalisation (sum_a) + ATL backoff -- neither rescues the bridge (both neutral/negative on discrimination). (6) NO-REGRESS: connected-node ancestor chains byte-identical (645/645) after the gated attachment. (7) bootstrap item CI (2000 reps) on the bridge accuracy; null p95 on the twin."
files_changed: "experiments/exp_meansend_realtext_validate_v1.py (the validation: 4 arms -- upstream purpose precision + glass-box fix; the matched-population thesis test CONTAMINATED/GLASSBOX/CLEAN vs the info-free twin with bootstrap CI + null p95; ATL backoff coverage; no-regress; the InversePlanningAttacher posterior+gate + the AtlVerbBackoff hub-and-spoke generalizer + the keep_purpose glass-box discriminator + the diagnostic means-end fit); verification/test_meansend_realtext_validate.py (scaffold-free witness, 9/9, reads landed metrics + spaCy-free from-source units); data/exp_meansend_realtext_validate_v1/{metrics_full.json, labeled_pairs.json}; notes/problems/validate_the_ppmi_svd_means_end_bridge_on_real_narrative_marker_less_goal_attachment/SOLVED.md. REUSED unchanged: experiments/exp_goal_hierarchy_markerless_bridge_v1.py (the PoC ATOMIC index + PPMISVDBridge), hdlab/goal_register.py, hdlab/goal_hierarchy_graph.py. hdlab/ UNTOUCHED (proposed diffs in §5, strategy lands)."
reverify: ".venv/Scripts/python.exe verification/test_meansend_realtext_validate.py   # 9/9, reads metrics + spaCy-free from-source units (no landed cell re-run). Full recompute (optional): .venv/Scripts/python.exe experiments/exp_meansend_realtext_validate_v1.py --label  (spaCy oracle, writes labeled_pairs.json) then --run  (spaCy-free)."
---

# The means-end bridge does NOT validate on real narrative -- and the wall is not where the brief put it

## The one-line answer
The brief predicted the marker-less-goal wall was a KNOWLEDGE-COVERAGE bound in the means-end bridge, softened by SVD
generalization, to be validated on real text and wired as a gated edge. **It is not.** On real LitBank narrative the
PPMI+SVD means-end bridge does NOT beat an info-free twin (a shuffled action->goal map) -- its apparent picks are a
goal-FREQUENCY artifact the twin reproduces -- and this holds even after I make the whole chain brain-foundational and
even on a perfectly-parsed subset. The n=16 authored PoC's 0.9375 was an overfit to easy hand-authored contrasts. Two
REAL walls are located and measured on the way: (1) the UPSTREAM goal-extraction over-fires (purpose precision 0.27 vs
a spaCy-advcl oracle -- 2/3 of "purposes" are complements/causatives/modals), and (2) the means-end KNOWLEDGE itself is
context-free (ATOMIC typical-intent contains the true narrative purpose in only 1/201 covered pairs). The real problem
underneath -- attaching a marker-less action to the goal it serves -- needs CONTEXTUAL inverse planning (the situation
model conditioning the goal posterior), not a context-free knowledge lookup. This is the same "contextual
representation, not a knowledge lookup" boundary the reader's meaning channel already hit (the WSD wall).

## §0 The brain opening move (research drill 2026-09-05, cited in full in the cell docstring)
"How does the brain attach an action to the goal it serves?" -> **Bayesian INVERSE PLANNING** (Baker/Saxe/Tenenbaum
2009; Jara-Ettinger naive-utility-calculus 2016/2020): `posterior(goal|action) ~ P(action|goal)*P(goal)`, run over a
rational-agent model, with a confidence/uncertainty gate (dmPFC tracks the inference's uncertainty, not its content --
Berkay & Jenkins 2025). ATOMIC xIntent IS the crowd-sourced marginal of that posterior, so the means-end bridge is a
defensible COMPUTATIONAL-LEVEL model of the LIKELIHOOD term -- BUT the research flagged the load-bearing omissions up
front: the goal PRIOR, the diagnosticity normalisation over alternative actions, and (the one that proved decisive) the
fact that "the inverse-planning validation base is spatial/perceptual; transfer to TEXT, where there is no perceptual
cost analog, is the standing generalization gap." That flagged gap is exactly what killed the bridge on real text.

## §1 What I built -- every component made brain-foundational (the user's explicit ask)
1. **UPSTREAM PARSE -- purpose-vs-complement discrimination** (Malle 1999 reason-vs-cause / the "in order to"
   substitution; Friederici syntax network). A bare "to VP" is a purpose adjunct only if its governor does NOT SELECT
   the infinitive as a complement (control/raising/aspectual/causative/reporting -> xcomp). Prototyped glass-box
   (`keep_purpose`) -- no spaCy at runtime.
2. **UPSTREAM MEANING -- ATL-style semantic verb generalization** (`AtlVerbBackoff`, Lambon-Ralph hub-and-spoke): a verb
   absent from ATOMIC is abstracted to its nearest covered WordNet verb neighbour(s) and borrows their means-end
   embedding. "More edge types, not deeper search."
3. **LIKELIHOOD -- ATOMIC PPMI+SVD means-end fit** (reused from the PoC) + a **DIAGNOSTICITY** normalisation
   (`fit - mean_a fit`, the inverse-planning sum_a term the raw cosine drops).
4. **THIS component -- the Bayesian inverse-planning posterior + reliability gate** (`InversePlanningAttacher`):
   `posterior ~ softmax(fit) * activation(g)`, `activation = recency-decay * status-weight * connectivity` (the goal
   prior, from Suh&Trabasso reinstatement + Lutz&Radvansky graded status + Trabasso connectivity); commit iff the
   posterior margin >= theta AND fit >= tau, else REFUSE (the neurally-grounded uncertainty gate).

## §2 What I measured (4 arms; the info-free twin is the strongest floor)
| arm | result | verdict |
|---|---|---|
| **A1 upstream purpose precision** (spaCy-advcl oracle, n=296 scorable) | 0.270 raw -> **0.397 glass-box** (recall 0.70); 216 complement-errors (xcomp 174) | the upstream WALL, measured |
| **A2 thesis: bridge vs info-free twin** (matched-pop, per-item draws x25, twin 200 draws, bootstrap CI) | CONTAMINATED K1 0.559/twin p95 0.533 (ci_lo 0.489); CLEAN K1 0.586/twin p95 0.574 (ci_lo 0.510); K3 same shape | **twin NEVER loses -> located NEGATIVE** |
| A2 sub: cleaning lifts absolute acc | CLEAN raw 0.595 > CONTAMINATED 0.559 (K1); CLEAN 0.368 > 0.309 (K3) | the parse matters, but does not rescue |
| **A3 ATL backoff coverage** | 0.71 -> 0.82 (7 missing verbs recovered) | coverage up; discrimination unchanged |
| **A4 no-regress** | connected-node chains 645/645 byte-identical | the gated edge is a pure ADD |

**Mechanism-diff (why the twin does not lose):** the gold narrative purpose is in ATOMIC's top-10 typical-intents for
the action in only **1/201** covered pairs. ATOMIC answers "why do people usually X"; a novel narrates "why THIS
character did X HERE" -- context-specific, often atypical. So the bridge ranks by how central/frequent a goal is (which
the twin reproduces by shuffling the action), not by an action-specific means-end signal.

## §3 The located NEGATIVE, stated precisely (the brief's "FULL PASS" condition, met differently than predicted)
The brief allowed a rigorous located negative -- "the bridge cannot generalize beyond ATOMIC coverage" -- as a full
pass. The negative I found is **stronger and different**: the bridge does not clear the info-free twin *even inside
coverage* and *even on perfectly-parsed purposes*. It is therefore not a coverage bound (the SVD generalization the
brief hoped for cannot help -- the signal is absent, not merely sparse). Two honest caveats that keep this from being
overstated: (a) cleaning the upstream DOES lift absolute accuracy monotonically, so the parse is a real, separate
contributor; (b) at K3 the raw-bridge point estimate on clean purposes (0.368) sits just above the twin p95 (0.315),
but the full-stack CI does not separate and the effect vanishes under the diagnosticity control -- i.e. within noise. I
would withdraw any positive read of that K3 point first.

## §4 The two REAL walls + the brain-foundational fixes (verdict-independent, landable regardless of the bridge)
- **WALL 1 -- upstream purpose extraction (precision 0.27).** The goal register's bare-purpose branch fires on
  causatives/modals/aspectuals ("made her understand", "had to give", "began to play", "taught to read"). ROOT CAUSE
  found on disk: the subcat-frame path BYPASSES the register's own `NON_GOAL_TO` list, so a non-complement-taker
  governor falls through and fires. The glass-box fix (`keep_purpose`: reject control/raising/causative/reporting
  governors) lifts precision 0.27->0.40 at recall 0.70; the FULL fix is the register-native dependency parser
  (advcl vs xcomp) -- the already-filed `parser_arceager` adjacent problem. **This fix is net-positive on the live
  goal-why consumer regardless of the bridge (see §5a) -> recommend landing.**
- **WALL 2 -- context-free means-end knowledge.** ATOMIC typical-intent (or any context-free store) cannot supply the
  context-specific purpose a novel asserts. The brain uses the SITUATION to constrain the goal posterior. This is the
  same boundary as the reader's meaning channel (`[[wsd-wall-is-contextual-representation-not-grounding]]`): a
  knowledge lookup is not a contextual representation. **This is the real next problem** (§7).

## §5 FOR STRATEGY (proposed hdlab landing -- Q111; you own it)
- **LAND (verdict-INDEPENDENT, net-positive): the upstream purpose-precision fix in `hdlab/goal_register.py`.** In
  `extract_goals_sentence` branch (3), apply the expanded non-purpose-governor filter (control/raising/aspectual/
  causative/reporting) in the `subcat is not None` path too (today it only checks `is_complement_taker`, bypassing
  `NON_GOAL_TO`). Prototype = `keep_purpose` in the cell. It removes 5.5x more wrong purposes than genuine ones (§5a).
  Better still: route the advcl-vs-xcomp decision through the reader's dependency parse (the register-native parser
  problem). Default-on with the recall caveat measured, or hold for the parser fix.
- **HOLD (verdict-DEPENDENT): do NOT wire the means-end bridge as a gated edge type** in `build_goal_graph`. It does
  not beat the info-free twin, so an ATOMIC means-end edge would add frequency-artifact links that do not encode a real
  action->goal relation. The `link_open_stack` Tier-2 hook should stay OFF. The `AtlVerbBackoff` + `InversePlanningAttacher`
  are ready if a CONTEXTUAL means-end signal is later validated, but they have no admissible live consumer today.

## §5a Consumer impact + revisit opportunities (the user's "no-regress + should consumers be revisited?" ask)
- **Downstream consumers enumerated on disk:** the goal register feeds `situation_reader._read_goals` (the board QA
  goal arm: WANT + depth-1 goal-why), `goal_hierarchy_graph`, `affect_register`, `commonnoun_binder`. The upstream
  purpose-precision fix changes ONLY the purpose_bare set; measured effect on the `why()` readout: it removes **131
  wrong purposes vs 24 genuine (5.5:1 favourable)** -> net-positive on goal-why precision, small recall cost (the
  register-native parser removes the recall cost). The ATL backoff + inverse-planning attachment are strictly ADDITIVE
  (backoff fires only on otherwise-zero-fit uncovered verbs; attachment touches only isolated action nodes) -> zero
  regression, witnessed 645/645 byte-identical.
- **Revisit opportunity (make a consumer more brain-foundational using the optimized upstream):** the flat register's
  `wants()` uses pure recency; it could adopt the **activation-weighted reinstatement prior** built here
  (`recency-decay * status-weight * connectivity`) -- Suh&Trabasso + Lutz&Radvansky + Trabasso, strictly more
  brain-faithful than recency. Verdict-independent; a clean follow-on. (I did NOT land it -- solver scope + it needs
  its own no-regress pass on the reinstatement arm.)

## §6 AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
GOAL HIERARCHY / marker-less attachment: the means-end BRIDGE route is a located NEGATIVE on real narrative -- ATOMIC
context-free typical-intent does not encode context-specific authorial purpose (gold purpose in ATOMIC top-10 only
1/201; bridge within the info-free twin band on real pairs). **PINNED:** attachment is Bayesian inverse planning
(Baker/Jara-Ettinger); the reliability gate = dmPFC uncertainty (Berkay & Jenkins 2025). **NEW deviation logged:** the
`link_open_stack` Tier-2 hook + any ATOMIC means-end edge is an OUR-INVENTION that does NOT clear the info-free floor on
real text -- keep OFF. **NEW upstream fact:** goal-register bare-purpose precision is 0.27 on 19c prose (subcat path
bypasses NON_GOAL_TO); the fix is the register-native parser (advcl/xcomp) -- ties the goal dimension to the
`parser_arceager` wall. The residual is the meaning channel's CONTEXTUAL-representation boundary, same as the WSD wall.

## §7 ADJACENT COMPONENTS evaluated (candidate next problems)
- **CONTEXTUAL inverse planning (the real fix, highest value).** Condition the goal posterior on the situation model
  (open goals + current state) rather than a context-free ATOMIC lookup. Brain: the mentalizing network integrates the
  scene (precuneus) with the rational-agent model. This is the same engine the belief timeline needs -> the unification
  the prior SOLVED named (one inverse-planning organ for goal + belief). OUR-INVENTION-under-test.
- **Register-native dependency parser (advcl vs xcomp)** -- the production fix for WALL 1; already filed
  (`parser_arceager`). Lifts goal-why precision AND every downstream purpose consumer.
- **Activation-weighted reinstatement for `wants()`** (§5a) -- a small, verdict-independent brain-fidelity upgrade.

## KEY REALIZATIONS (the enabling moves)
1. **A single-draw discrimination probe LIED.** My first clean-set probe showed 0.72 vs twin 0.60 (a "pass"); averaging
   the distractor draw per item (the honest floor recomputation) collapsed it to 0.586 vs 0.574 (no separation). The
   apparent win was one lucky distractor set. "A width is not an effect" -- and neither is a single draw.
2. **The info-free twin has to keep the PRIOR to be a fair floor.** A twin that shuffles the means-end map but keeps the
   goal-frequency/centrality prior isolates the ONLY thing the bridge is supposed to add -- action-specific means-end
   knowledge. It adds nothing: the twin matches it. Without that twin the frequency artifact reads as a real signal.
3. **Routing the negative by flavor found the wall was upstream, not in my component.** Printing the actual extracted
   pairs (`made->understand`, `had->give`) showed 2/3 were not purposes at all -- a 0.27-precision parse gap the bridge
   was being blamed for. Fixing it lifted absolute accuracy but did not separate from the twin, which localised the
   SECOND wall (context-free knowledge) cleanly.
4. **The PoC number was an artifact of authored contrasts.** 0.9375 needed distractors like cook->sleep (obviously
   wrong). Real distractors are the agent's other real goals; ATOMIC cannot rank the true one first (top-10 hit 1/201).

## TLDR (plain English)
The idea under test: to guess which big goal a character's unexplained action serves, look it up in a commonsense
table of "why people usually do things." On sixteen hand-made examples it looked great. On real 19th-century stories it
does not work: a scrambled version of the same table does just as well, which means the table isn't actually supplying
the answer -- it's just favouring goals that are common in general. Two real reasons emerged. First, the step that
finds "purposes" in the text is wrong two times out of three on old prose -- it mistakes "had to give", "made her
understand", "began to play" for purposes -- so the guesser was being fed mostly garbage; I built a fix that roughly
halves that error and helps the reader's existing goal answers (it removes about five wrong purposes for every good one
it drops). Second, and more fundamental: a general "why people do things" table can't know the *specific* reason a
character does something in *this* story -- that comes from the situation, not from a dictionary. So the honest verdict
is that this particular method can't clear the bar, and the real path forward is to let the *situation* shape the
guess, which is the same lesson the reader's word-meaning work already reached. Everything is glass-box, no outside AI.

## QUESTIONS
None blocking. One decision for the owner (named, not asked as a widget): the real fix (contextual inverse planning) is
a new problem, not a tweak to this one -- worth opening as the goal/belief unification, or fold into the meaning
channel's contextual-representation work? Recommend opening it as its own brief.

## NEXT STEPS
1. **LAND the upstream purpose-precision fix** (goal_register; net-positive on goal-why, verdict-independent) -- ideally
   as the register-native advcl/xcomp parse decision (`parser_arceager`).
2. **Open CONTEXTUAL inverse planning** as the real marker-less-attachment mechanism (condition the goal posterior on
   the situation model; the goal+belief unification engine).
3. **Optional brain-fidelity upgrade:** activation-weighted reinstatement for `wants()` (§5a).
4. **Do NOT wire** the context-free means-end bridge as a gated edge (it does not clear the info-free floor).
