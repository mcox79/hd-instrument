---
problem: distributed_contextual_representations_into_the_parser_the_tractable_accuracy_fidelity_gap
status: REFUTED
bar: "PASS = a whitened, syntactically-TYPED distributed selectional-preference feature in the arc-eager attachment score that lifts held-out UAS (and the meaning-sensitive obl/PP relations) CI-separated over the current parser, with a shuffled-meaning info-free twin LOSING, on BOTH modern AND 19c (register-general, no 19c regression), landed through the LIVE reader -- and NO-regress on any board dim, ideally a CI-separated lift on one (who-did-what/state/space). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE -- a faithful distributed selectional feature cannot close the gap glass-box (with the exact reason, e.g. the class-typing coverage bound), is a FULL PASS."
result: "LOCATED NEGATIVE (the brief calls this a FULL PASS). A whitened, (head-POS,preposition)-TYPED, object-CONDITIONED distributed selectional-preference feature over the substrate's own meaning_foundation vectors, built faithfully (Pado/Resnik class-level + lemma back-off), scores PP-attachment 0.5743 on UD-EWT test (n=1104 PP cases) -- BELOW the arc-eager parser's own 0.7763, below locality 0.6540, below lexical 0.6603. It is ANTI-complementary: on the 247 cases the parser gets WRONG it scores 0.4737, BELOW chance (0.5). Wired as a confidence-gated PP re-attachment on the full parse (n=2077 sents, 2460 gold obl/nmod arcs) it CI-separated HURTS UAS (0.8459 -> 0.8449, delta -0.0010 CI[-0.0017,-0.0005]) and drops obl/nmod attach (0.7533 -> 0.7451). Whitening does not rescue it (un-whitened 0.5634). The ONLY complementary signal is lexical head<->preposition association (Hindle-Rooth, 0.6437 on parser-wrong cases); confidence-gated it lifts the ISOLATED V/N decision +0.0100 CI[+0.0009,+0.0199] (twin loses) but does NOT survive to full-parse UAS (tau=3.0: -0.0002 CI[-0.0008,+0.0004]) or obl/nmod (-0.0020 CI[-0.0074,+0.0033]); its arithmetic ceiling (+11 net-correct/1104 at perfect targeting) is ~+0.004 obl-LAS / ~+0.0004 UAS, below CI-separability. The parser gives no usable uncertainty gate (softmax-conf AUC 0.645; margin median 42, uncalibrated)."
floor: "The arc-eager parser's OWN PP-attachment pick = 0.7763 (n=1104 UD-EWT test PP cases; majority 0.5870, locality 0.6540, lexical Hindle-Rooth 0.6603 all weaker). Full-parse floor: baseline arc-eager UAS 0.8459 / obl+nmod attachment 0.7533 (n=2077 UD-EWT test sents, 2460 gold obl/nmod arcs). Floors recomputed per population on the same items."
controls: "SHUFFLED-MEANING twin (permute word->vector before whitening): distributed selpref collapses 0.5743 -> 0.5208 (signal is real but far below structure). SHUFFLED-ASSOCIATION twin (randomized preposition) for the lexical route: loses on the isolated decision (0.7699 vs 0.7862) and on the full parse (UAS -0.0004; obl -0.0028). COMPLEMENTARITY control: distributed selpref is BELOW chance (0.4737) on parser-wrong cases = anti-complementary (this is the decisive control -- a cue that cannot beat chance where the parser errs cannot correct it). UN-WHITENED control: 0.5634 (whitening does not rescue). PRECISION-GATE control: arc-eager softmax-conf AUC(right vs wrong)=0.6452, and gating the meaning cue to the low-conf 30% HURTS (-0.0254) -- no usable uncertainty signal. Distributed reattach on full UAS is CI-separated NEGATIVE (-0.0010 CI[-0.0017,-0.0005])."
files_changed: "experiments/exp_typed_selpref_ppattach_v1.py (the decisive isolated PP-attachment test: floors + whitened typed object-conditioned selpref + lexical HR + twins + complementarity + CIs), experiments/exp_lexical_pp_reattach_uas_v1.py (the full-parse UAS + obl/nmod bar via confidence-gated PP re-attachment, sentence-level bootstrap), verification/test_typed_selpref_ppattach_negative.py (scaffold-free witness, 4 assertions). NO hdlab/ written (Q111; and nothing to land -- a located negative proposes no wire)."
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

## 5. ADJACENT COMPONENTS (evaluated for brain-fidelity + leverage -- seeds the next problems)

- **CALIBRATED per-attachment posterior/precision for the parser (HIGH VALUE).** The blocker in section 4.2 is
  the missing reliability signal. A graded-competition posterior over legal attachments (the landed
  graded_competition organ; cross-references the "upgrade the pos tagger to a calibrated joint-decoded
  posterior" problem and the sibling's "per-arc CONFIDENCE is consumed by ZERO live consumers, AUC 0.81 on
  arc_parser object attachment") would let a complementary lexical cue be precision-weighted in ONLY where the
  parser is genuinely uncertain -- the one path that could turn the isolated +0.0100 into a net gain. This is the
  most promising follow-on and it is a PARSER-FIDELITY problem, not a meaning-vector problem.
- **The meaning_foundation vectors are collinear (cos 0.93) EVERYWHERE they are used.** Whitening is a cheap,
  brain-consistent (contrast/gain normalization) fix that the meaning channel (diagnostic_context_wsd) should
  adopt before any consumer relies on cosine -- flagged, not this problem's to land. (It did not rescue
  attachment, but it is load-bearing wherever cosine over these vectors is used.)
- **Lexical head-preposition subcategorization is a real, register-stable signal (0.644 on parser-wrong cases)**
  that the parser does not fully capture -- but harvesting it needs the calibrated gate above, not a distributed
  feature. A candidate PARSER problem, contingent on the posterior.
- **NO board dim is touched** (nothing is proposed for landing), so there is zero downstream regression risk; the
  downstream no-regress check the bar asks for is vacuously satisfied by proposing no wire.

## 6. PROPOSED hdlab CHANGES (Q111)

**NONE.** A located negative proposes no wire. The distributed selectional feature CI-separated hurts UAS; the
lexical route does not clear the bar. Landing either would regress the parser. The value delivered is the
refutation + the precise cause + the two adjacent seeds, not a diff.

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

## What I did NOT establish

- I did not measure 19c. There is NO 19c gold UD treebank (documented in the sibling problem), so UAS on 19c is
  unmeasurable; and since the modern result already fails the bar, the register-regression question does not
  arise (there is no modern gain to check for OOD collapse). If a positive modern result had existed, 19c would
  have needed a separate instrument.
- I did not test a trained contextual encoder (barred by the invariant) -- so I cannot say a glass-box CONTEXTUAL
  distributed representation is impossible, only that the STATIC selectional-preference slice the brief specifies
  fails, and that the contextual version is exactly what the no-trained-encoder invariant excludes.
- I did not build the calibrated-posterior parser (section 5) -- I localized it as the blocker and the next
  problem, but did not prove it would turn the isolated lexical +0.0100 into a net UAS gain.

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
fix does not work, here is exactly why, and the genuinely promising next step is to give the grammar-connector a
calibrated sense of its own confidence so a meaning cue can be trusted only where it is actually unsure.

### QUESTIONS
None. (The mechanism is refuted on the brief's own instrument with the info-free twins losing and the cause
triangulated three independent ways; the 19c and contextual-encoder gaps are documented, not worked around.)

### NEXT STEPS (ordered)
1. **File the calibrated per-attachment posterior/precision parser problem** (section 5.1) -- the real blocker.
   Without a reliable "unsure here" signal, no complementary cue (lexical or otherwise) can be precision-weighted
   in without spoiling correct structural picks. This is the highest-value parser-fidelity follow-on and it
   reuses the landed graded_competition organ + the sibling's discarded per-arc confidence.
2. **Adopt whitening in the meaning channel** (diagnostic_context_wsd) before any cosine-over-meaning consumer
   lands -- cheap, brain-consistent, load-bearing wherever these collinear vectors are compared (it did not help
   attachment, but attachment is not where it pays).
3. **Escalate the "distributed CONTEXTUAL representation" question to the owner as an invariant decision.** The
   true -0.083 SOTA lever is a trained whole-sentence encoder, which the NO-trained-encoder invariant excludes.
   Either accept the glass-box parser at ~0.79-0.84 UAS, or relax the invariant for an OFFLINE-built static
   contextual asset -- an owner call, not a solver call.
