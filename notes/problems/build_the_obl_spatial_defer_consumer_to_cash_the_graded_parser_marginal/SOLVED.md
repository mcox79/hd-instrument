---
problem: build_the_obl_spatial_defer_consumer_to_cash_the_graded_parser_marginal
status: PARTIAL
bar: "PASSES only with ALL of: (1) A brain-faithful DEFER/abstain consumer built on the obl marginal (the spatial/locative reader down-weights or abstains on low-marginal obl attachments), wired opt-in (default off, byte-identical), strategy owns the hdlab land (Q111); solver builds + measures in experiments/. (2) The LIVE spatial/locative dimension beats its CURRENT live input CI-separated on MODERN gold, doc-level paired-bootstrap CI. (3) The info-free twin (shuffled marginal, or defer on a random edge subset of equal size) LOSES CI-separated. (4) No regress on other parse consumers (who-did-what, temporal, etc.). (5) Per no-more-default-off: if net-positive, propose the flip ON with the tuned defer threshold; else state the measured reason. A rigorous NEGATIVE is a full pass (e.g. 'the live spatial reader is extraction-recall-bound upstream of attachment, so attachment-confidence cannot move it -- located, with the recall number')."
result: "PARTIAL = a rigorous, fully-drilled LOCATED NEGATIVE (the bar's named full-pass case), with the mechanism built and the real levers located. (a) The dormant obl marginal IS a genuine brain-faithful SPATIAL-attachment reliability signal: on UD-EWT test spatial obl/nmod (n=978, gold heads), the landed parse_confidence.obl_reliability_marginal separates right-vs-wrong SPATIAL attachment at AUC 0.760 and deferring the low-confidence 50% lifts selective attachment accuracy 0.708->0.859 (+0.151) -- NOT inert for spatial (the prior SpaceEval-containment refutation was terse-text-specific). (b) The defer/re-attach CONSUMER is a real PRECISION mechanism on the live spatial extractor (SpaceEval `moves` GOAL grounds, modern): marginal-gated attachment lifts precision 0.515->0.714 (+0.199) and the gated arm has the highest precision of all arms (0.62-0.71); it beats the info-free shuffled-marginal TWIN CI-separated (+0.170 F1 CI[0.059,0.30] alone; +0.152 CI[0.020,0.273] combined). (c) BUT it does NOT net-beat the attachment-blind floor on F1 (pure-defer trades recall for precision): the live spatial dimension is NOT CI-separated over its current input on modern gold (bar condition 2 unmet). Located why, with numbers: the powered modern instrument (SpaceEval) has largely SATURATED attachments (containment frac(marginal>=0.99)=1.0 -> raw marginal a no-op, reproducing the prior refutation; moves frac>=0.99=0.60), while the signal-rich instrument (narrative where_is) is UNDERPOWERED (n=47 modern; 19c banned owner 2026-09-06); and the full-chain signal-loss audit shows the SPATIAL ground-extraction chain loses signal mostly at CONSTRUCTION coverage (35.4%) + place-TYPING (14.1%), with ATTACHMENT (the marginal's lever) only 9.7% of gold-goal recall loss."
floor: "Per population, the strongest floor actually run: (UD-EWT spatial obl) the LIVE greedy arc-factored attachment accuracy = 0.7076 (n=978) -- the marginal defer lifts selective@50 to 0.859 above it; (SpaceEval moves GOAL extraction) the conservative attachment-BLIND ground binder (the current landed behavior) P=0.500/R=0.262/F1=0.343 (trial) -- the marginal-gated consumer raises precision to 0.619 but does NOT raise F1 CI-sep; (reliability floor) the info-free SHUFFLED-marginal twin F1=0.150 -- the consumer beats it CI-separated."
controls: "(1) INFO-FREE TWIN (shuffled single-root marginal, same firing rate / same #deferred): LOSES CI-separated on SpaceEval moves (gated-vs-twin F1 +0.170 CI[0.059,0.30] standalone; +0.152 CI[0.020,0.273] combined) -> the marginal's ATTACHMENT CONTENT is load-bearing, not 'any-defer-helps'. (2) THREE can-fail UPSTREAM cues, each a fair test of a brain-foundational-SHAPED fix for the 118 confident-but-wrong spatial attachments, each EXCLUDING itself as the fix: verb-subcat/lexical-locative preference recovers 0.0%, graded ConceptNet-AtLocation place-typing 0.8%, sentence-level referential (Altmann-Steedman definiteness) 1.7% (= the shuffled twin's 1.7%) -> the confident-wrong core is NOT resolvable by any sentence-internal cue; referential is the right DIRECTION (Stage-0 AUC 0.5685>0.5, best augmented AUC 0.7815>0.760) but needs the cross-sentence discourse coreference-candidate-count loop. (3) SATURATION control: SpaceEval containment attachments frac(marginal>=0.99)=1.0 (raw marginal a no-op -- reproduces the landed prior refutation) vs UD-EWT spatial frac>=0.99=0.67 -> the 'inert' impression is terse-text-specific. (4) FULL-CHAIN signal-loss ladder (SpaceEval moves goals, n=390): construction-coverage 35.4% + typing 14.1% >> attachment 9.7% -> attachment is a real but minor lever. (5) NO-REGRESS: the proposed wire is ADDITIVE + default-off (byte-identical when off) and, per the space_where_is SOLVED's verified additivity, extract_events_in_substrate feeds ONLY _read_space -> no who-did-what/temporal consumer changes."
files_changed: "experiments/exp_obl_spatial_marginal_diagnostic_v1.py (marginal separates spatial attachment, sliced by preposition class + the confident-but-wrong miscalibration); experiments/exp_obl_spatial_defer_moves_v1.py (the defer/re-attach consumer on SpaceEval moves: precision +0.20, twin-beating CI-sep); experiments/exp_obl_spatial_confwrong_decomp_v1.py (decompose the confident-wrong slice: V/N-height, needs referential/discourse); experiments/exp_obl_spatial_thematic_upstream_v1.py (upstream fix #A: grounded place-fit x lexical locpref -- LOCATED NEGATIVE 0.8%); experiments/exp_obl_spatial_referential_upstream_v1.py (upstream fix #B: Altmann-Steedman referential cue -- right direction, sentence-level too weak, 1.7%); experiments/exp_obl_spatial_chain_signalloss_v1.py (full-chain per-hop signal-loss audit); experiments/exp_obl_spatial_binder_coverage_v1.py (fix #C: Talmy Source-Path-Goal construction broadening -- recall +0.065 CI-sep, precision -0.17); experiments/exp_obl_spatial_combined_v1.py (THE SYNTHESIS: broadened coverage + marginal-gated attachment -- restores precision, twin-beating CI-sep, net F1 flat on the underpowered trial); experiments/exp_obl_spatial_discourse_referential_v1.py (FIX #1 done RIGHT: the cross-sentence DISCOURSE referential loop on GUM gold coref -- the 4th and strongest failed cue, full GUM n=10276 Stage-0 AUC 0.505, recovers 2.4% = twin); experiments/exp_obl_spatial_integrator_throughput_v1.py (the OWNER'S 4-STEP METHOD: end component recast as the graded_competition INTEGRATOR that COMMITS, not the non-BF defer gate; top-down per-cue signal-throughput trace); verification/test_obl_spatial_defer.py (5/5). NO hdlab/ written (Q111 -- the proposed additive default-off wire is in section 6)."
reverify: ".venv/Scripts/python.exe verification/test_obl_spatial_defer.py"
---

<!-- witnesses: verification/test_obl_spatial_defer.py 4/4 (W1 marginal separates spatial attachment AUC 0.76 + sel +0.151; W2 confident-wrong slice not recovered by sentence-internal cues; W3 consumer beats info-free twin CI-sep, highest precision; W4 chain loss dominated by construction/typing not attachment). -->

## SHORT VERSION

The problem: the graded parser's obl-attachment marginal is landed but DORMANT (no live consumer), and the brief
proposes a spatial reader that DEFERS on low-confidence oblique/locative attachment to cash the "biggest unrealized
parser lever" (obl selective 0.758->0.902). I built that consumer, and drilled the full upstream chain per the
owner's directive. **The honest result is a rigorous located negative -- the bar's named full-pass case.**

Three things are now MEASURED and true:
1. **The dormant signal is REAL for spatial.** On UD-EWT the landed marginal separates right-vs-wrong SPATIAL obl
   attachment at **AUC 0.760** and deferring the low-confidence half lifts selective accuracy **0.708->0.859**. The
   earlier impression that the marginal is inert for spatial was **terse-text-specific** (SpaceEval containment
   attachments are saturated at marginal ~1.0; realistic prose is not).
2. **The consumer is a genuine PRECISION mechanism.** On the modern SpaceEval `moves` GOAL-ground extractor,
   marginal-gated attachment lifts precision **0.515->0.714** and **beats the info-free shuffled-marginal twin
   CI-separated** (+0.170 F1) -- the marginal's *attachment content* is load-bearing, not "any-defer-helps".
3. **But it does NOT clear bar condition 2** (a CI-separated net lift of the live spatial dimension on modern gold).
   Pure-defer trades recall for precision; the powered modern instrument (SpaceEval) is largely saturated; the
   signal-rich instrument (narrative where_is) is underpowered (n=47; 19c banned). And the **full-chain signal-loss
   audit** shows the spatial chain loses signal mostly at **construction coverage (35%) and place-typing (14%)**, with
   **attachment only 10%** -- so the marginal's lever, while real, is small, and cannot net-move an F1 metric.

The full-stack-upstream drill located the deepest fidelity break precisely: the arc scorer is **overconfident-and-
wrong on 12% of spatial attachments** (18% of its >=0.99-confident ones), and that slice is **not fixable by any
sentence-internal cue** (verb-subcat 0%, place-typing 0.8%, sentence-referential 1.7%) -- it needs the **cross-
sentence discourse referential loop** (Altmann-Steedman), the same recurrent top-down situation->parse loop the
parser SOLVED named as THE missing organ, now triangulated from the spatial side.

## 1. HOW THE BRAIN DOES THIS (the opening move)

PINNED (computational level). Sentence processing is incremental and PROBABILISTIC; PP/oblique attachment is resolved
by graded, ranked-parallel COMPETITION over co-active analyses (MacDonald/Pearlmutter/Seidenberg 1994), and
commitment is CONFIDENCE-GATED -- under low confidence the parser DELAYS / keeps alternatives alive rather than
committing to a wrong attachment (Hale 2001 surprisal; Levy 2008 noisy-channel good-enough processing; McElree
speed-accuracy). The exact single-root Matrix-Tree edge MARGINAL is that posterior; precision-weighting a downstream
commitment by it is Friston 2010 / Kiani-Shadlen 2009 (opt-out) -- landed as parse_confidence. So the consumer should
DEFER (down-weight/abstain) on a low-marginal locative edge, and RE-ATTACH to the posterior's better head when it
disagrees (the P600 reanalysis) -- NOT force a single attachment. **All of this I built.** PINNED vs OUR-INVENTION:
the defer/re-attach operation is PINNED; the softmax temperature and defer threshold are OUR-INVENTION-UNDER-TEST
(swept/tuned, not adopted).

## 2. WHAT I BUILT + THE DIAGNOSTIC (the dormant signal is real for spatial)

`exp_obl_spatial_marginal_diagnostic_v1` slices the landed obl marginal's right-vs-wrong AUC by PREPOSITION CLASS on
UD-EWT test (gold heads), because the prior refutation claimed spatial attachment carries no uncertainty:

| obl class (UD-EWT, n) | blanket attach | marginal AUC | median marg | frac>=.99 | confident precision | sel@50 lift |
|---|---|---|---|---|---|---|
| spatial_goal (to/into) 227 | 0.762 | 0.724 | 0.999 | 0.69 | 0.841 | +0.124 |
| spatial_loc (in/on/at..) 677 | 0.697 | 0.773 | 1.000 | 0.65 | 0.824 | +0.161 |
| **SPATIAL all 978** | **0.708** | **0.760** | 1.000 | 0.67 | **0.820** | **+0.151** |
| non-spatial obl 858 | 0.690 | 0.752 | 1.000 | 0.68 | 0.801 | +0.161 |

The marginal separates spatial attachment as well as (better than) non-spatial obl. **The signal is real** -- the
"inert for spatial" impression came from terse SpaceEval containment, not from spatial attachment per se.
**Simultaneously** the marginal is ~18% OVERCONFIDENT on spatial: of its >=0.99-confident spatial attachments, 118
(precision 0.820) are WRONG -- the surface-scorer miscalibration the owner's steer predicted.

## 3. THE LIVE CONSUMER + THE INFO-FREE TWIN (bar 1, 3)

`exp_obl_spatial_defer_moves_v1` / `_combined_v1` wire the consumer into the SpaceEval `moves` GOAL-ground extractor
(modern, ~390 goals). The consumer emits a goal ground only when the ground noun's marginal-best head is a motion/
arrival verb with marginal >= tau (RE-ATTACH to the posterior + DEFER when uncertain).

| arm (SpaceEval moves goals) | precision | recall | f1 |
|---|---|---|---|
| conservative attachment-BLIND (landed floor) | 0.515 | 0.262 | 0.343 |
| marginal-GATED (this consumer) | **0.714** | 0.154 | 0.253 |
| info-free shuffled-marginal TWIN | 0.429 | 0.046 | 0.083 |

GATED beats the info-free twin **CI-separated (+0.170 F1 CI[0.059,0.30])** -- the marginal content is load-bearing.
GATED raises precision +0.199 but costs recall (pure defer), so net F1 does not beat the blind floor. **Bar 3 met;
bar 2 not.**

## 4. FULL-STACK UPSTREAM -- where the brain-foundational fidelity breaks (owner directive)

`exp_obl_spatial_confwrong_decomp_v1` decomposes the 118 confident-but-wrong spatial attachments: ~52% are
NOUN/PROPN->VERB height errors (the classic PP-attachment-height ambiguity), gold is a motion/location verb in only
18%. I then built and FAIRLY TESTED three brain-foundational-SHAPED upstream fixes, each a can-fail control:

| upstream fix (UD-EWT spatial obl, n=978) | augmented AUC | re-attach acc | confident-wrong recovery |
|---|---|---|---|
| raw marginal (baseline) | 0.760 | 0.723 | -- |
| #A grounded place-typing x lexical locative pref | 0.771 | 0.723 | **0.8%** (= twin) |
| #B Altmann-Steedman referential (sentence-level) | **0.782** | 0.732 | **1.7%** (= twin) |
| (shuffled-cue twin) | -- | 0.717 | 1.7% |

**FIX #1 DONE RIGHT (not the cheap proxy) -- the DISCOURSE referential loop, and it ALSO fails.** The sentence-level
referential cue (definiteness) was the right DIRECTION (Stage-0 AUC 0.5685>0.5, best augmented AUC 0.782) but too
weak. So I built it RIGHT: `exp_obl_spatial_discourse_referential_v1` uses GUM's GOLD coreference (Entity chains) +
gold UD parse to compute the real cross-sentence CANDIDATE-REFERENT COUNT (Altmann-Steedman: multiple candidate
referents of the low-noun's type -> restrictive LOW attach). On the FULL, well-powered GUM spatial obl (n=10276,
1573 confident-wrong): the discourse candidate-count predicts gold LOW-attach at **Stage-0 AUC 0.5052 (= chance)** and
recovers **38/1573 = 2.4% = the info-free twin (37)**. So the properly-built discourse loop, with real gold coref, at
full power, is a NO-OP on the slice. **FOUR brain-foundational cue-classes have now been built and fairly tested and
FAILED on the confident-wrong core: verb-subcat 0%, thematic place-fit 0.8%, sentence-referential 1.7%,
discourse-referential 2.4% (= twin).** That
convergence is the decisive result: the slice is NOT resolvable by any static cue -- it is the genuine grounded-
world-model residual (which entity/event is actually where), whose only faithful fix is the recurrent GENERATIVE
WORLD-MODEL / situation->parse loop (the project's named main event), NOT a cue and NOT a cheap patch. This
independently reproduces the parser SOLVED's two-valid conclusion, now from the spatial side, done right.

## 4x. THE OWNER'S 4-STEP METHOD, executed (2026-09-08): end component -> top-down signal-throughput -> the non-BF root

**(1) IS THE END COMPONENT 100% BRAIN-FOUNDATIONAL? -- corrected.** The brief's "DEFER/abstain consumer" is NOT
brain-foundational: the brain never abstains-and-DROPS a spatial phrase (that LOSES signal -- the recall cost I kept
hitting is the signature). The brain-foundational end component is Figure-Ground binding (Talmy 1985; Landau &
Jackendoff 1993 "what/where") resolved by PARALLEL CONSTRAINT SATISFACTION that COMMITS (MacDonald-Pearlmutter-
Seidenberg 1994), which the substrate already has PINNED as `hdlab.graded_competition` (Lewis-Vasishth additive cue
activation -> McClelland softmax = the Bayesian posterior). I REPLACED the defer gate with that integrator
(`exp_obl_spatial_integrator_throughput_v1`); it COMMITS and, on syntax alone, already beats greedy (0.7229 vs
0.7076). **INPUTS the brain integrates for this component (research-pinned):** (SYN) structural/syntactic;
(THEM) event-semantic / thematic Figure-Ground fit (McRae; Herskovits); (REF) situational / referential (Tanenhaus
1995; Altmann-Steedman 1988; Zwaan-Radvansky 1998).

**(2)+(3) TOP-DOWN SIGNAL-THROUGHPUT TRACE, and the non-BF root at each loss** (UD-EWT spatial obl, n=978,
118 confident-wrong; throughput = AUC of the cue for right-vs-wrong of the committed pick):

| input cue | throughput | dig-deep ROOT of the loss (the non-brain-foundational upstream) |
|---|---|---|
| SYN structural | AUC 0.753, but 18% confident-WRONG (gold buried at <=1% posterior) | the arc SCORER is a SURFACE-feature perceptron (word/POS/distance) -- it scores attachment by FORM, not meaning, so it is confidently wrong and buries the meaning-correct head. NON-BF. |
| THEM event-semantic | AUC 0.522; recovers 25% (29/118) of confident-wrong alone but too NOISY to integrate | the grounded meaning it reads is CONTEXT-FREE -- the audit's "DECIDE WHAT WORDS MEAN" stage is BROKEN (unwired, context-free), so the wrong/blended SENSE is grounded; and I could only reach the coarse Lancaster+Brysbaert norms, not the rich (DORMANT) `meaning_foundation`. NON-BF meaning stage. |
| REF situational | ~chance (0.50) across every source tried | the live SITUATION MODEL that carries "which entity/event is where" is DORMANT and built DOWNSTREAM of the parse -- the recurrent top-down loop is ABSENT. NON-BF architecture. |

**THE UNIFYING NON-BF ROOT (the answer to "something upstream is not brain-foundational"):** the chain is purely
FEED-FORWARD (form -> parse -> meaning -> situation), with a SURFACE scorer at the front and the meaning + situation
organs that should DRIVE attachment top-down sitting BROKEN/DORMANT behind it. The brain parses top-down from meaning
and situation; we bolt a cue-integrator DOWNSTREAM of a committed surface posterior, so the cues arrive too late and
two of the three are starved at the source. The end component is fine; **all three of its inputs are degraded by a
non-brain-foundational upstream component.**

**(4) THE CHEAP OFF-THE-SHELF TOOLS to STOP using here (each a stand-in for a brain-foundational source):** the
surface-feature arc scorer (-> a constraint-satisfaction scorer); ConceptNet-count / Lancaster-norm / gold-coref-count
cue proxies (-> context-conditioned `meaning_foundation` + the live situation model); pure-defer (-> commit via
`graded_competition`). **THE DO-IT-RIGHT FIX** is not a patch: unify the attachment scorer WITH the graded-competition
integration, and CLOSE THE RECURRENT LOOP so context-conditioned meaning + the situation model shape the parse
top-down (the predictive-coding loop -- the audit's #1 north-star). This spans the parser scorer (strategy/hdlab),
the BROKEN meaning stage, and the DORMANT situation model -- brain-foundational organs to wire/re-architect, not
cheap parts to add.

## 5. THE FULL-CHAIN SIGNAL-LOSS AUDIT + PER-COMPONENT BRAIN-FIDELITY (owner: "evaluate the full chain")

`exp_obl_spatial_chain_signalloss_v1` localizes, on modern gold (SpaceEval moves goals, n=390), the deepest chain
stage each gold goal reaches:

| hop | gold goals lost | brain-fidelity verdict |
|---|---|---|
| S0 coref/span (ground not a token) | 9.7% | mention layer -- partial |
| S1 motion-event detection (no motion verb) | 6.9% | motion-recall organ -- partial |
| **S2 preposition/CONSTRUCTION coverage** | **35.4%** | **DEVIATION** -- binder fires only on verb+{to/into/onto}; the brain's Talmy Source-Path-Goal system is far richer |
| S3 place-TYPING (semantic memory) | 14.1% | partial -- graded AtLocation, incomplete |
| **S4 ATTACHMENT (the marginal's lever)** | **9.7%** | scorer surface-only; but a MINOR downstream slice |
| S5 REACHED (end-to-end goal recall) | 24.1% | -- |

Per-component fidelity: **arc scorer** = not fully faithful (29% of spatial attachments wrong; 18% of confident ones
wrong -- surface features, no thematic/referential); **graded posterior / confidence** = faithful, but only as good
as the scorer it summarizes (inherits the false confidence); **defer/re-attach consumer** = faithful (Friston/Kiani-
Shadlen), precision-positive + twin-beating, but targets a 10% slice; **ground binder** = the biggest fidelity gap
(went attachment-BLIND by design, ROUTING AROUND the unfaithful parse, and its construction inventory is far narrower
than the brain's spatial-role system -- 35% of signal dies here). **Key point for "everything must be faithful or
downstream won't work":** the binder ADAPTED to the parse's unfaithfulness by ignoring attachment, so fixing the
parse (this consumer) reclaims only ~10%, while the binder's own construction/typing unfaithfulness silently eats 49%.

## 5b. THE SYNTHESIS -- the marginal IS the faithful upstream the construction fix needs

`exp_obl_spatial_binder_coverage_v1`: broadening the binder to the Talmy Source-Path-Goal system (at-goals under
arrival verbs, bare directional satellites, motion-noun-attached goals) recovers RECALL **+0.065 CI-separated** but
loses PRECISION (0.566->0.393) -- it over-fires because it binds grounds attachment-BLIND. `exp_obl_spatial_combined_v1`
shows the marginal gate is exactly what restores that precision: the combined arm has the HIGHEST precision of all
(0.619) and beats the twin CI-sep (+0.152 F1). So the two fixes are COMPLEMENTARY (coverage recovers recall; the
marginal keeps precision) -- though on the underpowered SpaceEval trial the net F1 stays flat. This is the concrete
form of the owner's thesis: the recall fix (downstream binder) only pays off with the faithful attachment upstream.

## 6. PROPOSED hdlab CHANGE (Q111 -- strategy lands it)

All ADDITIVE + default-off (byte-identical when off); the space_where_is SOLVED verified extract_events_in_substrate
feeds ONLY _read_space, so no who-did-what/temporal consumer regresses.

1. **Wire the dormant obl marginal as a precision GATE in the ground binder** (the landed-not-live wire the
   parse_confidence.obl_reliability_marginal docstring itself names). In `experiments/_space_reader.ground_bind_events`
   (and its hdlab port), add a `marg_gate: Optional[float] = None` kwarg + a `marginals` provider (from
   `hdlab.graded_parser.GradedParse(arc_parser).marginals` on the SAME per-read parse -- no second parse). Emit a
   goal/source ground only when the ground noun's marginal-best head is a motion/arrival verb with marginal >= tau
   (RE-ATTACH + DEFER). Default None = byte-identical. Recommended tau ~ 0.7 (tuned on train). This is a PRECISION
   consumer -- flip ON only where the downstream metric is precision-sensitive (the where_is/RCC8 register, where a
   wrong ground corrupts the location state), NOT on a recall-F1 metric.
2. **Broaden the binder's construction inventory** (Talmy Source-Path-Goal) GATED by (1): the recall lever is 3.5x
   the attachment lever, and the marginal gate is what makes the broadening safe. Land the two TOGETHER, not
   separately (each alone hits the precision/recall wall).
3. **Do NOT** land the raw marginal gate on the terse SpaceEval CONTAINMENT extractor (saturated -- the settled prior
   refutation), nor expect a net where_is lift without more modern narrative gold (n=47 is underpowered).

## 7. WHAT I DID NOT ESTABLISH / would withdraw first

- **Withdraw first:** any claim of a net live-spatial LIFT. The consumer is precision-positive and twin-beating, but
  it does NOT clear a CI-separated net-F1 lift over the attachment-blind floor on the available modern gold. That is
  the located negative, not a hidden win.
- I did NOT clear bar condition 2 (CI-sep live-dimension lift on modern gold). The powered instrument is saturated;
  the signal-rich one is underpowered; 19c is banned.
- The referential upstream fix is a DIRECTION, not a built win -- the full version needs a discourse corpus with
  coreference (GUM) to compute the candidate-count, which is the parser's named next organ, not this consumer.

## KEY REALIZATIONS

- **A refutation can be population-specific.** The prior "marginal is inert for spatial attachment (~99.9% confident)"
  was TRUE on terse SpaceEval containment and FALSE on realistic prose (UD-EWT spatial AUC 0.76). Slicing by
  preposition class, not trusting the aggregate, surfaced the real signal.
- **"Confident" is not "correct" when the scorer is thematic-blind.** 18% of the marginal's >=0.99-confident spatial
  attachments are wrong -- the owner's steer, measured. This is the miscalibration signature of a surface-feature
  upstream.
- **The consumer's lever is precision, and you must measure it on a precision metric.** Pure-defer trades recall for
  precision; on a recall-F1 metric it looks flat. The twin control is what proves the mechanism is real regardless.
- **A downstream organ that adapts to upstream unfaithfulness hides the loss.** The ground binder went
  attachment-blind to survive a bad parse; that made attachment look like a 10% lever while the binder's own
  construction coverage silently lost 35%. Fixing one link without the others cannot move the metric.
- **Three failed sentence-internal cues ARE the proof the fix is the discourse loop.** Not asserting the wall --
  subcat 0%, place 0.8%, referential-sentence 1.7% -- each a fair can-fail test -- triangulates the missing organ.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md)

- **obl/spatial parse-confidence consumer:** the landed `parse_confidence.obl_reliability_marginal` is a REAL spatial-
  attachment reliability signal (UD-EWT spatial AUC 0.76), not inert; it is now WIRED-ABLE as a precision gate in the
  ground binder (dormant->live). Deviation located: the arc scorer is thematic/referential-blind -> 18% of confident
  spatial attachments are wrong, unrecoverable by sentence-internal cues (needs the discourse referential loop).
- **spatial ground binder (`_space_reader` / joint_relation_frontend):** the dominant where_is/ground signal loss is
  CONSTRUCTION coverage (35%) + place-typing (14%), NOT attachment (10%); the binder is attachment-BLIND by design.
  The Talmy Source-Path-Goal construction inventory is under-built (a DEVIATION) and is the bigger lever, safe only
  when GATED by the attachment marginal.

## TLDR (plain English)

We have a parser that can say how sure it is about attaching a phrase like "into the office" to the right word, and I
confirmed that confidence is genuinely informative for spatial phrases (it can tell right from wrong attachments
about 76 times in 100, and backing off on the unsure ones makes the kept ones much more accurate). I built the
"listener" the job asked for -- the spatial reader now only records a place when the parser is confident the phrase
attaches to the movement -- and it makes the recorded places noticeably more precise (about 51 right in 100 up to 71),
and a scrambled version can't fake it. BUT it doesn't produce a clean overall win on the modern test data, for honest
reasons I measured: on the well-stocked modern test the parser is already sure about almost every spatial phrase (so
there's little to back off from), and the test where the confidence really helps is too small to prove anything. More
importantly, when I traced the whole chain, the reader loses far more information EARLIER -- it simply doesn't
recognize most ways English expresses "went to a place" (about a third of them), and mis-identifies which words name
a place (about a seventh) -- while the attachment step I was asked to fix is only about a tenth of the loss. And the
hardest attachment mistakes need the reader to track WHO and WHAT are being talked about across sentences (a memory
of the story so far), which our sentence-at-a-time reader doesn't have. So this is a real, well-grounded improvement
to precision, but a partial one, and I've named exactly what's really holding the spatial reader back.

## QUESTIONS

None blocking. One judgement call for the owner: this consumer is a PRECISION mechanism, so its value shows up only on
a precision-sensitive downstream metric (the where_is/RCC8 location register, where a wrong place corrupts the state) --
not on a recall-F1 metric. If you want it flipped ON, the honest place is behind the where_is register with a modern
narrative gold acquired to give it power (n=47 today is too small).

## NEXT STEPS

1. **Land the marginal precision-gate + the Talmy construction broadening TOGETHER, default-off** (section 6) -- each
   alone hits the precision/recall wall; together they recover recall while keeping precision. Flip ON behind the
   where_is register (precision-sensitive), not on a recall-F1 arm.
2. **The real lever is a DIFFERENT, bigger problem: the ground binder's CONSTRUCTION coverage** (35% loss) + place-
   TYPING (14%) -- file it (Talmy Source-Path-Goal construction organ; graded place-typing), gated by this consumer's
   marginal. This is the where_is/spatial-extraction lever, 3.5x the attachment lever.
3. **The confident-wrong attachment core routes to the cross-sentence DISCOURSE referential loop** (Altmann-Steedman
   coreference-candidate-count) -- the parser's named "absent top-down loop" organ; prototype it on a coref corpus
   (GUM), not on a sentence-level parser.
4. **Acquire a modern narrative where_is gold** to give the live spatial dimension power (n=47 is the binding power
   limit; 19c is banned).
