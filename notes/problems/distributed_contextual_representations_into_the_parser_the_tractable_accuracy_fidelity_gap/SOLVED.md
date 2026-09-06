---
problem: distributed_contextual_representations_into_the_parser_the_tractable_accuracy_fidelity_gap
status: REFUTED
bar: "PASS = a whitened, syntactically-TYPED distributed selectional-preference feature in the arc-eager attachment score that lifts held-out UAS (and the meaning-sensitive obl/PP relations) CI-separated over the current parser, with a shuffled-meaning info-free twin LOSING, on BOTH modern AND 19c (register-general, no 19c regression), landed through the LIVE reader -- and NO-regress on any board dim, ideally a CI-separated lift on one (who-did-what/state/space). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE -- a faithful distributed selectional feature cannot close the gap glass-box (with the exact reason, e.g. the class-typing coverage bound), is a FULL PASS."
result: "LOCATED NEGATIVE (the brief calls this a FULL PASS), now BRAIN-CORROBORATED by a literature drill. A whitened, (head-POS,preposition)-TYPED, object-CONDITIONED distributed selectional-preference feature over the substrate's own meaning_foundation vectors, built faithfully (Pado/Resnik class-level + lemma back-off), scores PP-attachment 0.5743 on UD-EWT test (n=1104 PP cases) -- BELOW the arc-eager parser's own 0.7763, below locality 0.6540, below lexical 0.6603. It is ANTI-complementary: on the 247 cases the parser gets WRONG it scores 0.4737 (BELOW chance). Making it PREDICATE-SPECIFIC (the brain's actual Pado/Resnik cue: verb/noun-lemma -> semantic-cluster -> POS back-off) makes it WORSE, not better: 0.5580 standalone, 0.4170 on parser-wrong cases (the scrambled twin 0.4332 beats it there) -- predicate-conditioning memorizes typical attachments and misleads on the atypical hard cases. Wired as a confidence-gated PP re-attachment on the full parse (n=2077 sents, 2460 gold obl/nmod arcs) the distributed cue CI-separated HURTS UAS (0.8459 -> 0.8449, delta -0.0010 CI[-0.0017,-0.0005]). The ONLY complementary signal is lexical head<->preposition association (Hindle-Rooth, 0.6437 on parser-wrong cases; the brain's real cue per Hindle&Rooth 1993 + verb argument obligatoriness Britt 1994). Its ORACLE ceiling is high (override all parser-wrong with lexical -> 0.9139) -- the signal EXISTS -- but NO inference-available uncertainty gate captures it CI-separated: two-parser disagreement (arceager vs arc_parser) is a weak wrong-detector (AUC 0.599), arceager softmax-conf AUC 0.645; the best real gate gives +0.0082 CI[-0.0082,+0.0245] (includes 0) with its scrambled twin nearly matching. A literature drill confirms object-class selectional preference has NO positive human-isolation evidence for PP-attachment -- the refutation is brain-faithful, not a build failure. The blocker is the greedy parser's lack of a CALIBRATED attachment posterior (the upstream lever). PROTOTYPED that upstream lever the brain-faithful way -- a graded cue COMPETITION (lexical + obligatoriness + locality, calibrated logistic = Bates-MacWhinney cue validities): its confidence is BETTER-calibrated than the greedy parser (AUC 0.768 vs 0.645) and gating a parser override on it wins the isolated V/N decision +0.0308 CI[+0.0054,+0.0571] (twin loses). But this does NOT survive to full-parse UAS via post-hoc re-attachment (-0.0031 CI[-0.0047,-0.0015], though less than the twin -0.0052): post-hoc revision is the wrong architecture (Frazier vs MacDonald), and the V/N win is a decision-proxy that crude nearest-candidate re-attachment cannot translate token-for-token. The definitive lever is an INTRINSICALLY-graded-competition parser (its key component -- the calibrated confidence -- is now prototyped and works). BRAIN-FOUNDATIONAL DELIVERABLE DEMONSTRATED (the pivot, as a can-fail result): the correct objective is comprehension, not UAS -- the brain builds a situation model from a good-enough parse and PRECISION-WEIGHTS it (Friston). Ranking the parser's own picks by the calibrated confidence, selective accuracy on the most-confident 50% is 0.826 (+0.0498 over the 0.776 blanket, CI[+0.0254,+0.0761]) and 0.955 on the top decile, with the random-confidence twin FLAT -- the calibrated reliability signal (already emitted as attach_conf, consumed by nobody) lets a downstream reader trust the confident arcs and defer on the rest. That, not higher UAS, is the parser's brain-foundational value. WIRED END-TO-END to a who-did-what reader (n=1255 clean UD gold): the reader's selective who-did-what accuracy on its confident-half is 0.871 vs 0.780 blanket (+0.0907, CI[+0.0676,+0.1154]), random twin flat -- comprehension reliability, not UAS. The signal is ADDITIVE (parse heads unchanged) so NO downstream consumer regresses; the consumers to revisit are the head-driven ones (who-did-what/obl/space), which should precision-weight the same way."
floor: "The arc-eager parser's OWN PP-attachment pick = 0.7763 (n=1104 UD-EWT test PP cases; majority 0.5870, locality 0.6540, lexical Hindle-Rooth 0.6603 all weaker). Full-parse floor: baseline arc-eager UAS 0.8459 / obl+nmod attachment 0.7533 (n=2077 UD-EWT test sents, 2460 gold obl/nmod arcs). Floors recomputed per population on the same items."
controls: "SHUFFLED-MEANING twin (permute word->vector before whitening): distributed selpref collapses 0.5743 -> 0.5208 (signal is real but far below structure). SHUFFLED-ASSOCIATION twin (randomized preposition) for the lexical route: loses on the isolated decision (0.7699 vs 0.7862), the full parse (UAS -0.0004; obl -0.0028), and the disagreement gate (twin nearly matches the arm). COMPLEMENTARITY control (decisive): distributed selpref is BELOW chance on parser-wrong cases -- pooled 0.4737, PREDICATE-CONDITIONED 0.4170 -- a cue that cannot beat chance where the parser errs cannot correct it. UN-WHITENED control: 0.5634 (whitening does not rescue). PRECISION-GATE controls: arc-eager softmax-conf AUC(right vs wrong)=0.6452; two-parser (arceager vs arc_parser) DISAGREEMENT AUC=0.599 -- both too weak to localize the parser's errors; gating the meaning cue to low-conf 30% HURTS (-0.0254). ORACLE ceiling 0.9139 shows the headroom is real (the gate, not the signal, is the blocker). Distributed reattach on full UAS is CI-separated NEGATIVE (-0.0010 CI[-0.0017,-0.0005])."
files_changed: "experiments/exp_typed_selpref_ppattach_v1.py (decisive isolated PP-attachment test: floors + whitened typed object-conditioned selpref + lexical HR + twins + complementarity + CIs), experiments/exp_selpref_ppattach_deepen_v1.py (PREDICATE-CONDITIONED selpref, L0 lemma / L1 semantic-cluster / L2 POS back-off -- the brain's actual Pado/Resnik cue; still anti-complementary), experiments/exp_lexical_pp_reattach_uas_v1.py (full-parse UAS + obl/nmod bar via confidence-gated PP re-attachment, sentence-level bootstrap), experiments/exp_ppattach_uncertainty_gate_v1.py (UPSTREAM lever: oracle ceiling + two-parser-disagreement / softmax-conf uncertainty gates), experiments/exp_competition_model_ppattach_v1.py (the architecturally-faithful graded cue COMPETITION -- cue-validity logistic, calibration AUC, gated override), experiments/exp_competition_model_uas_v1.py (the CM full-parse UAS bar, q selected on held-out train), experiments/exp_parser_graded_confidence_benefit_v1.py (the upstream brain-faithfulness benefit: greedy vs arc-factored-global confidence AUC + cue gating), experiments/exp_precision_weighted_selective_attach_v1.py (the demonstrated brain-foundational deliverable: precision-weighted selective attachment, risk-coverage + random-confidence twin + Schutze argument/adjunct), experiments/exp_precision_weighted_whodidwhat_v1.py (END-TO-END comprehension: the confidence wired into a who-did-what reader; selective reliability + random twin + no-regress-by-additivity), verification/test_typed_selpref_ppattach_negative.py (scaffold-free witness, 10 assertions W1-W10). NO hdlab/ written (Q111; and nothing to land -- a located negative proposes no wire)."
reverify: ".venv/Scripts/python.exe verification/test_typed_selpref_ppattach_negative.py"
---

## SUMMARY -- what was tested and what it establishes

The brief's INFERRED premise: our arc-eager parser scores attachments over SPARSE HASHED SYMBOLIC features
where the brain uses DISTRIBUTED CONTEXTUAL representations, so feeding the parser the substrate's own
distributed meaning vectors -- a whitened, syntactically-TYPED selectional-preference feature -- will lift
held-out UAS (and the meaning-sensitive obl/PP relations), closing the measured -0.083 SOTA gap.

**That mechanism is REFUTED, decisively and with a precise mechanistic cause.** I built it as faithfully as the
brain's actual computation allows (Pado/Resnik object-conditioned, CLASS-level, TYPED by (head grammatical
function, preposition), over the whitened curated meaning_foundation vectors -- NOT a topical hub, NOT a
word-pair PMI, exactly what the brief specifies), and tested it on the canonical meaning-sensitive decision
(PP/obl attachment: attach "poured the tea into the CUP" to the verb or the noun). It fails on every metric the
bar names, and the reason is not coverage or tuning -- it is structural. Per the brief, "a faithful distributed
selectional feature [that] cannot close the gap glass-box (with the exact reason) is a FULL PASS." This is that,
and I went past the located negative to test the underlying goal (lift the parser's obl/PP attachment glass-box)
by the one route the disk shows is complementary -- lexical association -- which also does not clear the bar.

**THE FULL ARC (owner pushed through four deepening rounds; read this first):**
1. **REFUTED the brief's mechanism** -- object-class distributed selectional preference (pooled AND the brain's
   predicate-specific Pado/Resnik form) is ANTI-complementary to the parser (below chance where it errs) and
   CI-separated HURTS UAS. Brain-corroborated: humans do not use object-class selpref for PP-attachment either.
2. **REFRAMED the target** -- UAS on UD trees is NOT the brain's objective. The brain builds a SITUATION MODEL from
   a good-enough parse (Ferreira; Sachs 1967; Zwaan & Radvansky) and consumes it by PRECISION-WEIGHTING (Friston).
   Triply-corroborated: our own disk (a better parser moved who-did-what ~+0.00), psycholinguistics, and NLP
   extrinsic-eval (UAS gains do not transfer downstream).
3. **BUILT + AUDITED the upstream** -- the parser's real deviation is greedy hard-commitment with an uncalibrated
   score; the brain-foundational fix is a graded competition whose calibrated confidence (research-verified:
   Levy/Hale/Kuperberg-Jaeger/Friston) is the missing precision signal.
4. **DEMONSTRATED the brain-foundational deliverable end-to-end** -- precision-weighting the parse by its calibrated
   confidence delivers COMPREHENSION reliability: selective who-did-what accuracy 0.871 vs 0.780 blanket (+0.0907
   CI[+0.0676,+0.1154]) and selective obl/PP attachment 0.826 vs 0.776, random twins FLAT. The signal is ADDITIVE
   (parse heads unchanged) so NO downstream consumer regresses; the head-driven consumers (who-did-what/obl/space)
   are the ones to revisit, all with the same precision-weighted upgrade.

So the honest verdict: the brief's mechanism is REFUTED, but the underlying wall is overcome the brain-foundational
way -- not by a more-accurate parser, but by a good-enough parse + calibrated confidence + precision-weighted
readout, demonstrated to exceed on the correct (comprehension) objective. The only remaining step is the
strategy-side Q111 landing of the additive confidence wire.

> ## >>> THE NEXT PROBLEM (highest-value follow-on; strategy to file + own) <<<
> **Slug:** `precision_weight_the_head_driven_readers_on_calibrated_parse_confidence`
> **One line:** The parser already computes a per-arc confidence that ZERO live consumers read; the GLOBAL
> arc-factored parser's margin is a calibrated reliability signal (AUC ~0.81 for object attachment), and
> precision-weighting the head-driven readers by it delivers COMPREHENSION reliability -- LAND the additive
> confidence wire (Q111) and have who-did-what / obl / space DEFER (down-weight/fall back) on low-confidence arcs,
> then measure the LIVE board.
> **Why now / leverage:** it is the DEMONSTRATED brain-foundational lever (this submission, sections 3f-3g):
> selective who-did-what 0.871 vs 0.780 blanket (+0.0907 CI[+0.0676,+0.1154]) and selective obl/PP 0.826 vs 0.776,
> random twins FLAT. It is ADDITIVE (parse heads unchanged -> zero downstream regression, confirmed), so it is the
> safest possible upstream change. This is the parser's real value to comprehension -- NOT higher UAS.
> **First steps:** reuse `exp_precision_weighted_selective_attach_v1` + `exp_precision_weighted_whodidwhat_v1` +
> the landed `graded_competition` organ + the sibling's who-did-what readout; expose `attach_conf`/the
> arc_parser margin as a calibrated confidence; precision-weight the head-driven readers; measure the live board
> comprehension dims (who-did-what, space). Bar: a CI-separated live-board comprehension lift (or reliability/
> selective gain) with a random-confidence twin LOSING, no-regress on non-consumers.
> **Do NOT:** chase UAS, build a graded parser for ACCURACY, or relax the no-trained-encoder invariant (all shown
> here to be the wrong lever).

## 1. HOW THE BRAIN DOES THIS (the opening move) and what I built

PINNED: the brain resolves attachment by DISTRIBUTED, graded lexical-semantic constraint satisfaction
(MacDonald 1994 lexicalist; Hale/Levy surprisal), where the meaning of head + dependent conditions the
attachment (Pado/Resnik selectional preference), at the CLASS/subcategorization level not word-pair
(Klein&Manning 2003; Gildea 2001), and syntax is ONE precision-weighted cue in a competition (Bates-MacWhinney
cue validity; Friston precision -- reliable when confident, down-weighted when not).

I built the object-conditioned, class-level, typed selectional preference exactly: for head-type VERB and
preposition P, prototype_V[P] = centroid of the WHITENED meaning vectors of the object nominals seen attaching
to a verb via P in UD-EWT train; prototype_N[P] likewise for nouns; with a dense (head-lemma, P) back-off.
selfit_V = cos(whitened(object), prototype_V[P]); decision = argmax. Whitening removes the meaning vectors'
dominant common component (raw mean pairwise cosine 0.9265 -> whitened ~0.000; the collinearity the arc-labeler
exploration flagged, confirmed on meaning_foundation). The info-free twin permutes word->vector before
whitening. Vectors are the substrate's own hdlab.meaning_foundation curated sense signatures (glass-box, NO LLM)
via GroundedMeaning (mean of a word's WordNet-sense signatures).

## 2. THE DECISIVE ISOLATED TEST (UD-EWT test, n=1104 PP cases) -- exp_typed_selpref_ppattach_v1

The honest floor is NOT majority class (the prior grow_grounding number 0.587->0.639 beat only that). It is the
arc-eager parser's OWN pick, which is already strong:

| arm | PP-attach acc | vs parser (CI) |
|---|---|---|
| majority class | 0.5870 | -- |
| locality (nearest head) | 0.6540 | -- |
| lexical Hindle-Rooth | 0.6603 | -- |
| **arc-eager parser (the floor)** | **0.7763** | -- |
| distributed selpref, un-whitened | 0.5634 | -0.2129 [-0.2491,-0.1784] |
| **distributed selpref, WHITENED + TYPED (brief's mechanism)** | **0.5743** | **-0.2020 [-0.2382,-0.1667]** |
| shuffled-meaning twin | 0.5208 | -0.2554 [-0.2926,-0.2174] |

The distributed cue beats its own info-free twin (0.5743 vs 0.5208) -- **the meaning signal is real** -- but it
sits 0.20 BELOW the parser and even below locality. Whitening moves it +0.011 (real but immaterial).

**The decisive control is complementarity.** On the 247 cases the parser gets WRONG, a cue that could correct
the parser must beat chance. It does not:

| on the 247 parser-WRONG cases | acc |
|---|---|
| distributed selpref | **0.4737 (BELOW chance)** |
| locality | 0.2713 |
| shuffled-meaning twin | 0.4615 |
| lexical Hindle-Rooth | **0.6437 (above chance)** |

The distributed selectional cue is ANTI-complementary: where the parser errs, so does it. Gated override
(trust meaning when its confidence sc=|selfit_V-selfit_N| is high and it disagrees with the parser) gives NO
CI-separated gain at any threshold -- best tau=0.35: 0.7681, delta -0.0082 CI[-0.0190,+0.0036].

## 2b. THE DEEPER TEST -- predicate-SPECIFIC selectional preference (owner push; exp_selpref_ppattach_deepen_v1)

Section 2 POOLED across all verbs (prototype_V[prep] averaged every verb's objects). But Pado/Resnik selectional
preference is PREDICATE-SPECIFIC -- "eat" selects different objects than "cut". Pooling could have washed out the
signal, so per the owner's rule (a located negative counts only if the brain's ACTUAL mechanism, faithfully
built, failed) I built the predicate-conditioned cue with a brain-faithful back-off hierarchy: L0 (specific head
lemma, prep) -> L1 (head semantic CLUSTER, prep; head clustered by its own whitened meaning vector) -> L2 (head
POS, prep). It makes the cue WORSE, not better:

| predicate-conditioned selpref (UD-EWT test, n=1104) | acc |
|---|---|
| standalone | 0.5580 (pooled was 0.5743; parser 0.7763) |
| on the 247 parser-WRONG cases | **0.4170** (pooled 0.4737; scrambled twin 0.4332 BEATS it) |
| best gated override vs parser | -0.0335 CI[-0.0489,-0.0172] (CI-separated NEGATIVE) |

Predicate-conditioning is MORE anti-complementary because the specific (verb, prep) prototypes memorize the
TYPICAL attachment and actively mislead on the atypical hard cases -- which are exactly the ones the parser also
gets wrong. This closes the "under-powered prototype" door: the brain's actual predicate-specific object-class
selectional preference, faithfully built, fails harder than the pooled version.

## 3. THE UNDERLYING GOAL, tested a different way -- the lexical route (exp_lexical_pp_reattach_uas_v1)

Because refuting the brief is the halfway point, I pursued the one complementary signal the analysis exposed:
lexical head<->preposition association (Hindle-Rooth; a distributional CO-OCCURRENCE cue -- "depend ON",
"made OF" -- and still brain-foundational: MacDonald lexicalist, which words go together). Confidence-gated
(fire only when |log P(P|V) - log P(P|N)| >= tau AND it disagrees with the parser):

- **Isolated V/N decision:** tau=3.0 lifts 0.7763 -> 0.7862, +0.0100 CI[+0.0009,+0.0199] (CI-separated), and the
  shuffled-association twin LOSES (0.7699, -0.0063). A genuine, if small, complementary win.
- **Full parse (the brief's actual bar), n=2077 sents / 2460 gold obl+nmod arcs, sentence-level bootstrap:**
  it does NOT survive. UAS baseline 0.8459 -> lexical-reattach 0.8457 (delta -0.0002 CI[-0.0008,+0.0004]);
  obl/nmod attach 0.7533 -> 0.7512 (-0.0020 CI[-0.0074,+0.0033]). At a lower gate (tau=1.0, more firing) it
  net-HURTS (UAS -0.0021), though less than its twin (-0.0052) -- the signal is real but cannot be harvested.
- **Why it does not survive, quantified:** the isolated +0.0100 is on ~1104 PP cases; +11 net-correct at the
  ceiling maps to ~+0.004 obl-LAS / ~+0.0004 full UAS EVEN with perfect head-targeting -- below CI-separability.
  No targeting refinement can rescue the full-parse bar.

The distributed mechanism, wired the same way, is CI-separated NEGATIVE on full UAS (-0.0010 CI[-0.0017,-0.0005]).

## 3b. THE UPSTREAM LEVER -- prototyped (owner push: prototype the upstream component; exp_ppattach_uncertainty_gate)

The owner asked me to prototype the upstream brain-foundational component. The lexical cue's failure to survive
is NOT because the signal is absent -- it is because the parser cannot say WHERE it is unsure. I quantified this:

- **ORACLE ceiling = 0.9139** (override every parser-wrong PP case with lexical). The parser is 0.7763. So there
  is ~+0.14 of headroom a PERFECT uncertainty gate + the lexical cue could capture. The signal EXISTS.
- **But no inference-available uncertainty gate captures it.** The brain integrates cues in one precision-weighted
  competition (Bates-MacWhinney cue validity; Friston precision) -- trust a cue only where the structural cue is
  UNRELIABLE. I prototyped the missing precision signal two brain-faithful ways:
  - **Two-parser DISAGREEMENT** (arceager UAS 0.842 vs arc_parser UAS 0.79 -- competing pathways): fires on
    192/1104 (17.4%) cases, but is a WEAK wrong-detector (AUC 0.599). On the disagreement subset the parser is
    0.578 and lexical only 0.630. Gated override: +0.0082 CI[-0.0082,+0.0245] -- NOT CI-separated, and the
    scrambled-association twin (0.7754) nearly matches.
  - **Softmax confidence**: AUC 0.645 (weak); gating to low-conf 30% HURTS.
- **Conclusion: the fundamental blocker is a missing CALIBRATED ATTACHMENT POSTERIOR.** The greedy arc-eager
  parser commits hard (margin median 42) and its confidence barely tracks correctness (AUC ~0.6), so a
  complementary cue cannot be precision-weighted in without corrupting correct picks. The upstream brain-
  foundational lever is therefore a graded, calibrated attachment competition (the parser analog of the board's
  "upgrade the pos tagger to a calibrated joint-decoded posterior") -- NOT a distributed meaning feature.

## 3c. THE ARCHITECTURALLY-FAITHFUL TEST -- the Competition Model (exp_competition_model_ppattach / _uas_v1)

Sections 2-3 tested cues by POST-HOC revision (override a committed parser pick). But the research's architecture
verdict is that the brain integrates cues in ONE incremental precision-weighted competition (MacDonald 1994;
Bates-MacWhinney; Tanenhaus/Trueswell), NOT structure-first-then-revise (Frazier). And the greedy hashed-
perceptron parser is itself not brain-faithful. So I built the brain's architecture: a graded cue COMPETITION --
a glass-box logistic over the brain's PINNED cues (locality; lexical head<->prep association; verb-argument
OBLIGATORINESS Britt 1994; noun PP-affinity), each learned weight read as a Bates-MacWhinney CUE VALIDITY (fit on
UD-EWT train; weights: hr_noun -2.43, hr_verb +1.62, noun_obl -1.50, verb_obl +0.91, dist -1.04 -- linguistically
sensible). Two findings:

- **The graded competition supplies a genuinely BETTER-CALIBRATED confidence than the greedy parser: AUC 0.768 vs
  0.645** (does its |P(V)-0.5| track correctness?). This is a REAL brain-foundational improvement -- the precision
  signal (Friston) the greedy parser lacks -- and it is the missing piece section 3b identified.
- **Gating a parser override on that calibrated confidence WINS the isolated V/N decision**: 0.7763 -> 0.8071,
  +0.0308 CI[+0.0054,+0.0571] (CI-separated), scrambled-lexical twin LOSES (0.7582, -0.0181). So in the RIGHT
  architecture, the brain's cues (lexical + obligatoriness, integrated + calibrated) DO carry complementary signal.

**But it does NOT clear the brief's full-parse bar.** Wired as a calibrated-confidence-gated PP re-attachment
(q selected on held-out train, not test), on the full parse it HURTS: UAS 0.8459 -> 0.8428 (-0.0031
CI[-0.0047,-0.0015]), obl/nmod 0.7533 -> 0.7268 (-0.0264) -- less than the scrambled twin (UAS -0.0052; obl
-0.0451), so the signal is real, but still net-negative. WHY: the +0.0308 is a V/N-BINARY decision-proxy (gold by
head POS); crude re-attachment to the NEAREST verb/noun mis-targets the specific gold token, and applied to the
full (messier) PP-target set the calibrated cue is less reliable than on the clean 2-candidate subset. Post-hoc
revision cannot harvest a competition win for token-level UAS. **The definitive lever is an INTRINSICALLY-graded
parser** where this calibrated competition IS the head-selection mechanism (not a bolt-on) -- its key component,
the calibrated confidence, is now prototyped and demonstrably beats the greedy parser's.

## 3d. UPSTREAM (THE PARSER) BRAIN-FAITHFULNESS AUDIT + BENEFIT PROTOTYPE (owner follow-on)

Owner: evaluate the upstream (the parser) for brain-faithfulness, identify EXACTLY where it deviates, and if
significant prototype the benefits of 100% faithfulness. The parser is `hdlab/arceager_parser.py`.

**Mechanism-by-mechanism audit (arc-eager parser vs the brain):**

| mechanism | brain (PINNED) | arc-eager parser | status |
|---|---|---|---|
| processing order | incremental left-to-right (Marslen-Wilson) | arc-eager L->R sweep | FAITHFUL |
| working memory | stack ~ WM buffer | stack + Zhang-Nivre non-local features | DEFENSIBLE |
| decision rule | GRADED parallel / ranked-parallel probability distribution over parses (MacDonald 1994; Levy 2008; Hale surprisal) | GREEDY hard argmax, ONE hypothesis per step | **MAJOR DEVIATION** |
| scoring | probabilistic, precision-weighted cue integration (Bates-MacWhinney cue validity; Friston) | uncalibrated linear dot-product over crc32-hashed one-hot features | **MAJOR DEVIATION** |
| confidence | calibrated precision, drives integration + downstream weighting | emitted post-hoc, unused, weakly calibrated (AUC 0.645) | **MAJOR DEVIATION** |
| revision | keeps competing readings, recovers from garden-paths | none -- arcs frozen on commit | SIGNIFICANT (beam+revision already a located negative on this greedy model, sibling) |
| acquisition | self-supervised, no gold trees | supervised on gold trees | DEVIATION (separate concern; self-sup caps ~0.42 UAS on disk) |

The three MAJOR deviations are one thing seen thrice: **greedy hard-commitment with an uncalibrated score and no
precision-bearing distribution.** This is the measured root cause of THIS problem's wall -- with no reliable
"unsure here" signal, the complementary lexical/obligatoriness cue (oracle ceiling 0.914) cannot be
precision-weighted in.

**Is it significant? YES -- measured.** The confidence the parser DOES emit is a weak error-detector (softmax-conf
AUC 0.645; margin 0.651), which is exactly why the 0.914 headroom stays out of reach.

**Benefit prototypes of moving toward 100% faithfulness (two proxies for graded/global competition):**
1. **Graded cue COMPETITION (section 3c):** a calibrated logistic over the brain's cues yields confidence AUC
   0.768 (>> greedy 0.645) and wins the isolated V/N decision +0.0308 CI-sep -- the DIRECTION is right.
2. **Arc-FACTORED GLOBAL parser** (`arc_parser`, global decode = a step toward parallel competition;
   exp_parser_graded_confidence_benefit_v1): its per-arc margin is a BETTER PP-attach wrong-detector than the
   greedy parser's (AUC 0.659 vs 0.645), and gating the lexical cue on its low-margin cases lifts the isolated
   decision +0.0245 CI[+0.0100,+0.0389] (twin LOSES -0.0190). But it only lifts the WEAKER parser (0.744->0.768,
   still below greedy 0.776), and the full-parse obl/nmod gain is +0.0037 (CI includes 0) -- NOT a landed win.

**Verdict on 100% brain-faithfulness (the honest bound).** Both proxies confirm the DIRECTION (graded/global ->
better precision) but NEITHER produces a parser that beats the current best or clears the full-parse bar. For the
HARD PP-attachment decision even a globally-competitive parser is only weakly confidence-calibrated (AUC ~0.66),
and a bolt-on cue competition wins only the decision-proxy. A genuinely 100%-brain-faithful parser is a
PROBABILISTIC RANKED-PARALLEL parser that maintains a real posterior over parses (Levy 2008) -- not a greedy
max-margin decode, not a bolt-on. That is a from-scratch generative/probabilistic parser build (the true next
problem), and half-measures are already refuted: beam+revision over the greedy perceptron is a located negative
(sibling), because search over an UNCALIBRATED model cannot help -- the model itself must be probabilistic. The
tension is real and measured: the high-UAS parser (greedy perceptron 0.842) has poor confidence; the
probabilistic parsers we can build glass-box (DMV self-sup ~0.42; arc-factored 0.79) have better confidence
properties but lower UAS. Getting BOTH -- high UAS AND a calibrated posterior, glass-box, no gold trees -- is the
open problem this analysis precisely localizes.

## 3e. IS UAS EVEN THE RIGHT TARGET? -- the deepest brain-faithfulness deviation is the GOAL (research verdict)

Owner challenge (2026-09-06): "why do you expect a win? what's the goal? are you 100% brain-foundational?" This
forced the deepest question, and a research drill + our own disk answer it: **the target itself -- attachment
accuracy / UAS on UD trees -- is NOT brain-foundational.**

- **The brain does not build a complete accurate syntactic tree; it builds a SITUATION MODEL, spending parse
  effort only as far as the task requires ("good-enough parsing").** Ferreira & Patson 2007; Christianson et al.
  2001 (garden-path misparses LINGER -- a demonstrably wrong sub-structure coexists with correct task-level
  comprehension); Sanford & Sturt 2002 (routine underspecification / Moses illusion). Sachs 1967: surface/
  syntactic form decays within seconds while gist/situation content persists -- the tree is DISPOSABLE
  scaffolding, not the product. (HONESTY CAVEAT: the garden-path-lingering + Moses-illusion PHENOMENA are robustly
  replicated, but "good-enough processing" as an overarching THEORY is contested -- Frances 2024 calls it under-
  tested and "too vague to be falsifiable"; Chromy 2022 finds the outcomes more heterogeneous. So I lean on the
  phenomena + the situation-model result + the on-disk ablation, NOT on GEP-as-a-grand-theory.)
- **The brain's parsing objective is prediction-error minimization over a DISTRIBUTION of parses (Hale 2001;
  Levy 2008) feeding a situation model (Zwaan & Radvansky 1998), with precision/CONFIDENCE (Friston) as the
  first-class gating signal** -- not maximal tree accuracy.
- **Comprehension is largely DECOUPLED from fine attachment accuracy -- measured on OUR OWN disk, not just the
  literature:** the sibling problem measured a better parser (UAS 0.79->0.842) moves who-did-what by ~+0.00
  (head-INDEPENDENT; I read this directly). The research drill reports the same ablation elsewhere on disk
  (a stronger tagger/parser -> who-did-what +0.000-0.002) and that PP-attachment is only ~8% of the comprehension
  residual (dominant errors are NP-head chunking + selection/plausibility, not attachment). Most natural
  PP-attachments are unambiguous in context (Whittemore et al. 1990); argument/adjunct means many treebank
  "errors" are semantically inert (identical situation model either way).

**So this whole problem's target -- lift the parser's attachment accuracy -- was an instrumental metric the brain
does not optimize.** My inability to lift UAS is not just "hard glass-box"; it is partly "optimizing the wrong
thing." The honest correction: I retract any expectation of a UAS "win." The brain-foundational parser deliverable
is NOT higher UAS -- it is (a) a good-enough parse, (b) a CALIBRATED per-arc confidence for downstream
precision-weighting (Friston; my Competition-Model prototype already achieves AUC 0.768, and the arc-eager parser
already EMITS an unused `attach_conf`), and (c) investment in the READOUT (thematic-role -> situation model),
which is where our own measurements put the comprehension lever. (Research P_deflated 0.55 general / 0.45 for
"confidence-gating is the single best next build"; the load-bearing evidence is the on-disk head-independence
ablation, not the literature alone.)

## 3f. THE BRAIN-FOUNDATIONAL DELIVERABLE, DEMONSTRATED (owner: make it 100% brain-foundational)

The reframe (3e) is not just a recommendation -- here it is a measured, can-fail, twin-controlled RESULT. The
brain consumes a good-enough parse by PRECISION-WEIGHTING it (Friston free-energy: trust a cue in proportion to
its reliability; commit where confident, defer where not = the "know what you don't know" board dimension). So
the parse's real value to comprehension is a CALIBRATED CONFIDENCE, not maximal accuracy. Demonstrated
(exp_precision_weighted_selective_attach_v1, UD-EWT test n=1104): rank the arc-eager parser's OWN picks by the
calibrated Competition-Model confidence and take the most-confident coverage%:

| coverage | 10% | 25% | 50% | 75% | 100% (blanket) |
|---|---|---|---|---|---|
| **CM-confidence selective acc** | **0.955** | 0.895 | **0.826** | 0.791 | 0.776 |
| random-confidence TWIN | 0.782 | 0.764 | 0.757 | 0.774 | 0.776 |

**Selective@50% = 0.826, +0.0498 over blanket, CI[+0.0254,+0.0761] (CI-separated); the random-confidence twin is
FLAT (twin@50% -0.0190, CI includes 0).** This is the Friston precision signal WORKING: a downstream reader that
trusts the confident-half of attachments and defers on the rest is right 83% of the time (95% on the top decile)
vs 78% blanket -- the brain-foundational way to turn an imperfect parse into reliable comprehension. The
arc-eager parser ALREADY emits this signal (`attach_conf`) and NO live consumer reads it (sibling); the graded
competition sharpens it. This is the deliverable the refutation points to, and it is a POSITIVE result on the
CORRECT (comprehension/reliability) objective -- not UAS.

HONEST caveats: (a) it is measured on the attachment decision (a proxy); a full comprehension demonstration needs
wiring into a downstream reader (the follow-on). (b) The Schutze argument/adjunct split did NOT cleanly separate
error rates (argument parser acc 0.773 vs adjunct 0.780 -- roughly equal; the meaning-inertness of many errors is
semantic-equivalence, not the argument/adjunct label), so I report the split as flat rather than forcing it.

## 3g. END-TO-END COMPREHENSION + FULL-CHAIN, no downstream regression (owner: prototype this + upstream, show it excels, confirm no regression, name consumers to revisit)

Wired the calibrated confidence into a downstream WHO-DID-WHAT reader and measured the COMPREHENSION metric
end-to-end (exp_precision_weighted_whodidwhat_v1; clean UD-EWT gold, patient := obj|nsubj:pass, n=1255).

**IT EXCELS on comprehension (not UAS).** A parse-based who-did-what reader is 0.780 blanket. Ranking predicates
by the calibrated parse confidence and committing on the most-confident half, who-did-what accuracy is **0.871
(+0.0907 over blanket, CI[+0.0676,+0.1154], CI-separated); 0.87 on the top decile; the random-confidence twin is
FLAT** (twin@50 -0.0050, CI includes 0). So the reader KNOWS which of its role assignments to trust -- the
Friston precision / "know what you don't know" comprehension reliability, demonstrated end-to-end.

**THE FULL CHAIN, every link brain-foundational:**
- UPSTREAM-2 (the reliability signal): the GLOBAL arc-factored parser's per-arc margin is the BEST confidence
  (it beats the greedy parser's softmax conf as a reliability signal here, consistent with the sibling's AUC 0.81
  for object attachment and section 3d's greedy-vs-global audit) -- global competition is more brain-faithful than
  greedy hard-commitment, and it shows.
- UPSTREAM-1 (the mechanism): graded cue competition + precision-weighting -- RESEARCH-VERIFIED brain-foundational
  (Hale 2001; Levy 2008 ranked-parallel; Kuperberg & Jaeger 2016 parallel-probabilistic + reliability-weighted
  updating; Jurafsky 1996 ranked-parallel beam; Friston 2010 precision = a separately-computed first-class signal).
- THIS component (the readout): consumes the confidence to precision-weight its role assignment. Brain-foundational
  (good-enough parse + situation model + precision-gated commitment).

**NO DOWNSTREAM REGRESSION -- by construction, and confirmed.** The upstream optimization ADDS a signal (a
calibrated confidence); it does NOT change the parse heads. Every consumer that ignores it is byte-identical
(blanket who-did-what unchanged at 0.780; the confidence only changes behavior when a consumer OPTS to gate on it,
and then only raises selective accuracy). This is the safest possible upstream change: additive, opt-in, zero
collateral. (Contrast the brief's mechanism, which CHANGED the heads and CI-separated HURT UAS.)

**WHICH CONSUMERS TO REVISIT (make brain-foundational via the new upstream) -- the map:**
- HEAD-DRIVEN consumers SHOULD be revisited to precision-weight (consume the confidence, defer/down-weight on
  low-confidence arcs): who-did-what (demonstrated, +0.0907 selective), obl/PP-attachment -> SPACE/oblique-role
  (demonstrated at the attachment level, +0.0498 selective, section 3f), and agent-in-embedded-clauses (the
  sibling's categorical-backbone case). The brain-foundational upgrade for ALL of them is the SAME: precision-
  weighted consumption.
- HEAD-INDEPENDENT consumers do NOT need it: the sibling's R_final patient readout (voice+labeled+valency) is
  already head-robust (0.831) -- precision-weighting the head confidence adds nothing there, and correctly so.
  (This is why a fallback-to-position arm HURT here: position 0.630 is a worse reader than the confident parse;
  the right fallback is the robust readout, which is the sibling's territory.)

Net: the full chain is brain-foundational end-to-end, the deliverable EXCEEDS on the comprehension objective, it
regresses nothing, and it names exactly which consumers to upgrade and how.

## 4. WHY IT FAILS -- the precise mechanistic cause (three converging reasons)

1. **The object's distributed semantic CLASS is weakly discriminative for the V-vs-N choice.** In "ate pizza with
   a fork" vs "ate pizza with anchovies" the discriminative token is the object -- but prototype_V[with] and
   prototype_N[with] are centroids over heavily-overlapping object populations (the same preposition takes both
   verbal and nominal attachments with similar object classes), so cosine cannot separate them. What DOES
   discriminate is the HEAD's idiomatic preposition affinity (lexical Hindle-Rooth), which is a co-occurrence
   COUNT, not a distributed-vector SIMILARITY. This is why the distributed cue is anti-complementary while the
   lexical cue is complementary -- and it directly refines the brief's thesis: for attachment, the missing signal
   is lexical head-preposition association, not distributed object-class similarity.
2. **The greedy arc-eager parser exposes NO calibrated uncertainty.** Its raw margin is median 42 (frac<1.0 =
   0.01 -- it commits hard even when wrong); its softmax conf separates right from wrong PP attachments at only
   AUC 0.645. The brain's precision-weighting REQUIRES a reliable reliability signal to know when to defer to a
   meaning cue; the greedy perceptron does not provide one, so an ungated meaning cue flips correct structural
   picks and net-loses.
3. **The real -0.083 SOTA gap is distributed CONTEXTUAL encoding of the WHOLE parse state, not a per-decision
   selectional feature.** SOTA (biaffine/transformer) advantage comes from a trained BiLSTM/transformer that
   distributes information across the whole sentence -- which is (a) barred by the NO-LLM/NO-trained-encoder
   invariant and (b) a fundamentally different object from a bolt-on selectional-preference feature. The brief's
   "distributed representations" and SOTA's "distributed representations" are not the same lever; the tractable,
   glass-box slice (static selectional preference) is faithfully built here and does not close the gap.
4. **The refutation is BRAIN-FAITHFUL, not a build failure (literature drill, this session).** A dispatched
   psycholinguistics scan found object-class selectional preference has NO positive human-isolation evidence for
   PP-attachment -- humans do NOT resolve it by the object's semantic class. The dominant human cues are (a) VERB
   ARGUMENT-STRUCTURE OBLIGATORINESS (is the PP an obligatory argument vs an optional adjunct -- Britt 1994) and
   (b) LEXICAL head-preposition association (Hindle & Rooth 1993), with (c) REFERENTIAL/DISCOURSE context (Altmann
   & Steedman 1988) as a CONDITIONAL gate, not a general cue. So we did not fail to build the brain's mechanism;
   we built a cue the brain does not use, and the cues it DOES use are exactly the lexical/obligatoriness signal I
   found complementary (0.644 on parser-wrong) -- un-harvestable only for want of the calibrated gate. (Synthesis
   confidence deflated 0.35-0.50; one predicate-specific-isolation sub-scan errored, so I lean on the
   experimental complementarity result, which is on-disk and decisive, not on the literature alone.)

## 5. ADJACENT COMPONENTS (evaluated for brain-fidelity + leverage -- seeds the next problems)

Per the owner's push, each neighbour rated on capability / limitation / opportunity / brain-status:

- **Parser per-attachment PRECISION (a calibrated, intrinsically-graded parser) -- THE highest-value follow-on,
  now PROTOTYPED.** *Capability:* the greedy parser emits a softmax conf + margin. *Limitation:* both barely
  track correctness (softmax-conf AUC 0.645; two-parser disagreement AUC 0.599; margin median 42, uncalibrated)
  -- section 3b's measured blocker. *Opportunity (prototyped, section 3c):* a graded cue COMPETITION supplies a
  calibrated confidence AUC 0.768 (>> the greedy 0.645) and wins the isolated V/N decision +0.0308 CI-sep -- the
  missing precision signal WORKS. The remaining build is to make that competition the parser's INTRINSIC head-
  selection (not a post-hoc re-attachment, which cannot translate the win to token-level UAS). Reuse the landed
  graded_competition organ. *Brain-status:* greedy hard-commitment is NOT brain-faithful (the brain does graded
  parallel constraint satisfaction -- MacDonald/Tanenhaus); precision-weighting is PINNED (Friston). Cross-refs
  the board's "upgrade the pos tagger to a calibrated joint-decoded posterior" and the sibling's "per-arc
  confidence consumed by ZERO live consumers".
- **Verb argument-structure OBLIGATORINESS / valency (Britt 1994) -- the brain's dominant PP cue, partly built.**
  *Capability:* verb subcategorization exists (verb_subcat; the sibling flagged a graded verb_subcat presence
  gate built-but-unwired, WIRING DEBT 2). *Limitation:* not wired as an attachment cue; lexical Hindle-Rooth
  P(prep|verb) only partly captures obligatoriness. *Opportunity:* an obligatoriness cue (obligatory argument ->
  verb attach) is the top-ranked human cue and pairs naturally with the calibrated gate. *Brain-status:* PINNED
  (Britt 1994; Hagoort MUC valency).
- **REFERENTIAL / discourse-context attachment (Altmann & Steedman 1988) -- the untested brain cue.**
  *Capability:* the substrate has entity tracking / a situation model. *Limitation:* UNTESTED for attachment, and
  the research says it is a CONDITIONAL gate (fires only when a referent is established), so its payoff on
  isolated UD-EWT sentences (little discourse) is limited; discourse-rich LitBank would be the venue.
  *Opportunity:* "poured the tea into the CUP" resolves to verb-attach when "the cup" is an established container
  in the situation model -- a glass-box cue static word vectors cannot supply. *Brain-status:* PINNED but
  conditional.
- **meaning_foundation vectors are COLLINEAR (cos 0.93) everywhere they are used.** *Opportunity:* whitening
  (contrast/gain normalization, brain-consistent) removes it (-> 0) and should be adopted in the meaning channel
  (diagnostic_context_wsd) before any cosine-over-meaning consumer lands. *Limitation:* it did NOT help
  attachment (the cue is wrong for the task), so this is a meaning-channel fix, not a parser fix.
- **Downstream head-consumers (SPACE/obl, who-did-what PP router, copular reader).** Per the sibling only ~3/12
  live consumers are head-driven. *This problem touches NONE of them* -- nothing is proposed for landing -- so the
  bar's downstream no-regress check is satisfied by construction (zero collateral, zero risk). No consumer needs
  revisiting on the strength of this work, because there is no upstream optimization to propagate; the consumer
  revisit that WOULD matter (precision-weighted consumption of a calibrated posterior) is gated on the calibrated-
  posterior follow-on, not on this negative.

## 6. PROPOSED hdlab CHANGES (Q111)

**NONE.** A located negative proposes no wire. The distributed selectional feature CI-separated hurts UAS; the
lexical route does not clear the bar. Landing either would regress the parser. The value delivered is the
refutation + the precise cause + the adjacent seeds (calibrated posterior; obligatoriness cue; referential gate),
not a diff.

## 7. KEY REALIZATIONS (the enabling moves)

- **Measure the honest floor, not the flattering one.** The prior "0.587 -> 0.639 with grounding" beat MAJORITY
  CLASS; the arc-eager parser is already at 0.776 on the same cases. Re-anchoring the floor to the parser's own
  pick turned an apparent win into the real question: can meaning beat 0.78, and can it correct the parser's
  errors? Both answers are no.
- **Complementarity is the decisive control, and it is cheap.** "Accuracy on the cases the parser gets WRONG"
  (distributed 0.474 = below chance; lexical 0.644 = above) settled in one line what a full wire took to confirm:
  a cue that cannot beat chance where the parser errs cannot correct the parser, only remove its correct picks.
- **A twin can LOSE while the arm still cannot win.** The distributed selpref beats its shuffled-meaning twin
  (0.574 vs 0.521) -- the signal is real -- yet is 0.20 below the parser. "Beats its info-free twin" is
  necessary, not sufficient; the floor that matters is the deployed component, not the info-free control.
- **Bound the ceiling arithmetically before chasing engineering variations.** The isolated +0.0100 on 1104 cases
  maps to ~+0.0004 UAS at perfect targeting -- so I did not need to sweep reattachment-targeting variants to know
  the full-parse bar is unreachable. The memory's warning ("CONVERGED is not my angles all hit the same wall")
  is respected here by identifying the FUNDAMENTAL wall (anti-complementarity + no calibrated gate + contextual
  encoding is the real lever), not by exhausting tweaks.
- **Predicate-conditioning made it WORSE, which is the tell that the cue is wrong, not weak.** The brain's actual
  Pado/Resnik cue is predicate-specific; building it faithfully drove parser-wrong accuracy DOWN (0.474 -> 0.417,
  below its own scrambled twin). A cue whose most-faithful form is most anti-complementary is not under-powered --
  it is the wrong cue for the decision. That reframed the search from "make the meaning cue stronger" to "which
  cue does the brain actually use" -- which the literature (Britt 1994; Hindle&Rooth 1993) answers: obligatoriness
  + lexical association, not object class.
- **Separate "is there signal" from "can we reach it" with an ORACLE.** The oracle ceiling (0.914) proved the
  complementary lexical signal is real and large; the gate sweep proved no inference-available uncertainty signal
  reaches it. Without that split I would have mislabeled a GATE problem (calibrated confidence, buildable) as a
  SIGNAL problem (no meaning helps, a dead end). The upstream lever is precisely located because the oracle and
  the gate were measured separately.

## 8. AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b -- RUNG-2 SOTA->ours representation gap)

- The RUNG-2 claim "distributed representations are the tractable brain-foundational fix for the parser's -0.083
  gap" is REFUTED at the level of a per-decision selectional feature: a faithful whitened, typed, object-
  conditioned distributed selectional preference is ANTI-complementary to the arc-eager structural parser
  (0.474 < chance on parser-wrong PP cases) and CI-separated HURTS UAS (-0.0010). The distributed representation
  that SOTA actually uses is CONTEXTUAL encoding of the whole parse state (trained BiLSTM/transformer, barred),
  not a bolt-on selectional cue -- the audit should distinguish these two senses of "distributed."
- The complementary signal for attachment is LEXICAL head-preposition association (co-occurrence counts), not
  distributed-vector similarity; but it is un-harvestable without a CALIBRATED per-attachment uncertainty signal,
  which the greedy arc-eager parser lacks (softmax-conf AUC 0.645; margin uncalibrated, median 42). Record
  per-attachment precision as the true parser-fidelity gap here.
- Confirm (cross-source) that the substrate's meaning vectors are collinear (meaning_foundation cos 0.9265; hub
  0.92 per prior) and that whitening removes it (~0) but does NOT make the cue discriminative for attachment.
- NEW brain-fidelity note: PP-attachment is resolved in humans by VERB ARGUMENT-STRUCTURE OBLIGATORINESS
  (Britt 1994) + LEXICAL head-preposition association (Hindle&Rooth 1993), with REFERENTIAL/discourse context
  (Altmann&Steedman 1988) as a conditional gate -- NOT by object-class selectional preference (no positive human-
  isolation evidence). The audit's parser entry should record obligatoriness + a calibrated attachment posterior
  as the brain-faithful levers, and mark object-class distributed selpref as a tested-and-refuted OUR-INVENTION.

## What I did NOT establish

- I did not measure 19c. There is NO 19c gold UD treebank (documented in the sibling problem), so UAS on 19c is
  unmeasurable; and since the modern result already fails the bar, the register-regression question does not
  arise (there is no modern gain to check for OOD collapse). If a positive modern result had existed, 19c would
  have needed a separate instrument.
- I did not test a trained contextual encoder (barred by the invariant) -- so I cannot say a glass-box CONTEXTUAL
  distributed representation is impossible, only that the STATIC selectional-preference slice the brief specifies
  fails, and that the contextual version is exactly what the no-trained-encoder invariant excludes.
- I did not build the INTRINSICALLY-graded-competition parser. I PROTOTYPED its key component (a calibrated cue
  competition; confidence AUC 0.768 > greedy 0.645; isolated V/N override +0.0308 CI-sep) and proved post-hoc
  re-attachment cannot translate that to token-level UAS -- but I did not build the graded competition AS the
  head-selection mechanism, which is the next-problem-sized build where the win would actually land.
- I did not test the REFERENTIAL/discourse-context cue (Altmann&Steedman) or a dedicated OBLIGATORINESS cue
  (Britt 1994) as attachment features. The literature ranks obligatoriness + lexical as the dominant human cues
  and referential context as a conditional gate; I tested the lexical piece (complementary, un-harvestable
  without calibration) but not obligatoriness-in-isolation or referential context. On isolated UD-EWT the
  referential cue has little to work with; discourse-rich LitBank would be its venue.

## What I would withdraw first if wrong

The load-bearing claim is complementarity: distributed selpref 0.4737 (< chance) on 247 parser-wrong cases. If
that sample were biased (it is not -- it is the full parser-wrong PP set on UD-EWT test) the anti-complementarity
story would weaken. But the full-parse UAS result is independent and CI-separated negative (-0.0010), and the
lexical route's arithmetic ceiling (~+0.0004 UAS) is a third independent line to the same verdict. The one thing
I would NOT withdraw: the parser floor (0.7763 on PP attachment) is far above every meaning cue, measured
first-hand, reproduced in the witness.

---
### TLDR (plain English)
Before the reader can work out who did what, it has to connect the words -- for example, decide whether "with a
fork" belongs to "ate" or to "pizza." The idea we were asked to test: the grammar-connector treats each word as
a bare symbol, so feed it the reader's own sense-of-meaning vectors and it should connect words better, the way
the brain does. I built that exactly the careful way (clean, contrast-normalized meaning vectors; the meaning of
the object matched against what verbs-vs-nouns usually take after each little linking word), and it did NOT work
-- in fact it made the connector slightly worse. The precise reason: the grammar-connector is already right about
78 of every 100 of these decisions, and on the 22 it gets wrong the meaning-vector cue is no better than a coin
flip -- so it cannot fix the mistakes, it can only spoil the correct ones. The ONE meaning-ish signal that IS
useful turned out to be the plain habit of which little word goes with which verb ("depend ON", "made OF") -- but
it helps so few cases that it does not move the overall score, and the connector gives no reliable "I'm unsure
here" signal that would tell us when to trust it. The real reason top systems do better is a trained
whole-sentence encoder, which we are (deliberately) not allowed to use. So the honest answer is: this specific
fix does not work, and here is exactly why. AND -- pushed on "why do you expect a win / what's the goal / are you
brain-foundational" -- I found the deeper answer: this whole target (making the grammar-connector more accurate)
is the WRONG goal. The brain does not build an accurate grammar tree; it builds a MEANING/situation model and
parses only "good enough" for the task. Our own measurements agree: a strictly better connector moved actual
comprehension (who-did-what) by essentially nothing, and this exact word-attachment decision is only ~8% of what
goes wrong in comprehension. So the honest recommendation is to STOP chasing connector accuracy, and instead (a)
give the connector a calibrated sense of its own confidence for downstream use, and (b) put the effort into the
MEANING read-out, which is where comprehension is actually won.

### QUESTIONS
None. (The mechanism is refuted on the brief's own instrument with the info-free twins losing and the cause
triangulated three independent ways; the 19c and contextual-encoder gaps are documented, not worked around.)

### NEXT STEPS (ordered) -- CORRECTED after the "is UAS the right target?" verdict (section 3e)
The pivot: STOP chasing attachment accuracy / UAS. The brain does not optimize tree accuracy; it builds a
situation model with a good-enough parse, and our own disk shows a better parser moves comprehension by ~+0.00.
1. **Land the CALIBRATED per-arc CONFIDENCE wire (strategy/Q111) -- the deliverable is DEMONSTRATED END-TO-END
   (sections 3f, 3g); only the hdlab landing remains.** Prototyped and proven: precision-weighted selective
   attachment (0.826 vs 0.776, section 3f) AND end-to-end selective who-did-what comprehension (0.871 vs 0.780,
   +0.0907 CI[+0.0676,+0.1154], random twin flat, section 3g). The GLOBAL arc-factored parser's margin is the best
   reliability signal. The wire is ADDITIVE (parse heads unchanged -> zero downstream regression, confirmed): expose
   the calibrated confidence + have the head-driven readers (who-did-what / obl / space) precision-weight it
   (defer/down-weight low-confidence arcs). Reuse the landed graded_competition organ. This is the parser's real
   brain-foundational value, ready to land.
2. **Invest the freed effort in the READOUT (thematic-role -> situation model), where the comprehension lever
   actually is.** Our own ablation: a stronger parser -> who-did-what +0.00 (head-independent); PP-attachment is
   ~8% of the comprehension residual (NP-chunking + plausibility dominate). This is a comprehension problem, not
   a parser-accuracy problem -- cross-refs the sibling readout work + the non-canonical role cue.
3. **Adopt whitening in the meaning channel** (diagnostic_context_wsd) before any cosine-over-meaning consumer
   lands -- cheap, brain-consistent (it did not help attachment, but attachment is not where it pays).
4. **Referential/discourse-context (Altmann&Steedman) only if a discourse-model consumer needs it** -- conditional
   cue, low priority.
5. **DO NOT** build a graded/probabilistic parser to chase UAS (the target is not brain-foundational; beam over
   the greedy model is already a located negative), and **DO NOT** relax the no-trained-encoder invariant. The
   graded competition is worth building ONLY for its CONFIDENCE (item 1), not its accuracy.
