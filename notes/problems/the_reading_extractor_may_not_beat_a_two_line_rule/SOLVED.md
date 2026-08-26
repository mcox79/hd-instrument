---
problem: the_reading_extractor_may_not_beat_a_two_line_rule
status: SOLVED
bar: "On a held-out, hand-adjudicated (or controlled-proxy) role-assignment set LARGER than n=100, floor recomputed on that population: the elaborate reader must beat the two-line rule (word-order + voice, elaborate filters OFF) CI-separated over its UPPER bound, information-free twin LOSING. HOW WE WOULD KNOW IT FAILED, and this is a full PASS for the brief: it ties or loses the two-line rule at power -> the elaborate machinery does not earn its keep, and the recommendation is to REPLACE it and redirect the effort to stage 2."
result: "On QA-SRL v2 gold PATIENT (ARG1) selection, n=17,330 held-out items (dev+test, span-accuracy scorer), the elaborate perceptron cue-integration reader (hdlab.thematic_role_labeler) scores 0.7511 and LOSES to the two-line word-order+voice rule (0.7661): elaborate-minus-two-line = -0.0149, 95% CI [-0.0188, -0.0112], CI-separated BELOW. => the elaborate machinery does not earn its keep -> REPLACE (a full PASS per the bar). PUSH (real problem underneath): a MORE brain-faithful reader -- word order + PRECISE voice (auxiliary + participle morphology) -- scores 0.7950 and beats BOTH the crude two-line rule (+0.0289, CI [+0.0260,+0.0319]) and the elaborate reader (+0.0439), and is the single best arm overall and on every reversibility stratum."
floor: "Strongest floor actually run = the two-line rule itself (word order + voice) = 0.7661 span-accuracy on n=17,330; the elaborate reader fails to clear it (loses, CI-separated). Below it: information-free TWIN (a random covered nominal, mean of 5 seeds) = 0.2872, and POSITIONAL (first nominal after verb, NO voice) = 0.6634. TWIN loses to the two-line rule CI-separated ABOVE in EVERY stratum."
controls: "(a) INFO-FREE TWIN (random nominal, 5 seeds)=0.2872, loses to the two-line rule CI-separated in all 8 strata -> EXCLUDES 'any nominal pick works / task is trivial'. (b) ELAB_SCRAMBLE (perceptron weight-values permuted)=0.5295 vs full 0.7511 -> the learned weights carry real signal (drop 0.22), so the elaborate reader was given a FAIR, trained, non-crippled shot and still lost -> EXCLUDES 'it loses only because it is untrained/broken'. (c) ELAB_ANIMACY_ONLY (single-cue ablation)=0.3117 (~=TWIN) vs ELAB_ORDER_ONLY=0.6862 -> the reader's usable signal is WORD ORDER, and the animacy cue it also weights is near-useless for English -> EXCLUDES 'animacy is a valid English role cue' (it is the wrong cue; MacWhinney/Bates/Kliegl 1984). (d) POSITIONAL (no voice)=0.6634 vs two-line 0.7661 -> EXCLUDES 'voice does not matter' (the +voice line adds ~0.10). (e) REVERSIBILITY STRATIFICATION (patient-animate n=1897; both-args-animate n=462) -> the elaborate reader collapses WORST exactly where syntax is the only cue (reversible: 0.684 vs two-line 0.800, -0.117; both-animate: 0.747 vs 0.848, -0.102) -> EXCLUDES 'the aggregate loss is a canonical-only scoring artifact'; it is the brain-predicted failure of an animacy-cue on reversible items. (f) PRECISE-VOICE arm beats the crude two-line rule CI-separated -> EXCLUDES 'the two-line rule is already optimal' and shows the headroom lies in the WORD-ORDER/voice direction, not the elaborate-machinery direction."
files_changed: "experiments/exp_reader_vs_twoline_qasrl_power_v1.py, verification/test_reader_vs_twoline_qasrl_power.py, data/exp_reader_vs_twoline_qasrl_power_v1/ (metrics.json, _detail_sample.json), notes/problems/the_reading_extractor_may_not_beat_a_two_line_rule/SOLVED.md. NO hdlab/ file changed (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_reader_vs_twoline_qasrl_power.py"
INTEGRATED_BY_STRATEGY: "2026-08-25 -- EXCELLENT; re-verified WITNESS PASS (ELABORATE_DOES_NOT_BEAT_TWO_LINE_REPLACE reproduces); elaborate reader loses to a two-line rule -> REPLACE; precise-voice reader (better, brain-faithful) recorded PROVEN-READY as a deliberate hdlab landing in situation_reader"
---

# SOLVED: the elaborate reader does NOT beat a two-line rule at power -- it LOSES to it, and a more brain-faithful two-line rule beats them both

## HEADLINE

Powering the n=100 comparison up to **n=17,330 real gold items** (QA-SRL v2, dev+test), on the axis
the n=100 errors lived on (which nominal is the verb's PATIENT), the answer is now unambiguous and it
is the REPLACE branch of the bar:

| arm (QA-SRL patient selection, n=17,330) | span-accuracy | vs two-line rule (paired 95% CI) |
|---|---|---|
| **TWO_LINE_PRECISE** (word order + aux+participle voice) *-- the push* | **0.7950** | **+0.0289 [+0.0260, +0.0319] ABOVE** |
| **TWO_LINE** (word order + voice) *-- the baseline to beat* | **0.7661** | -- |
| **ELABORATE** (thematic_role_labeler perceptron cue-integration) | **0.7511** | **-0.0149 [-0.0188, -0.0112] BELOW** |
| POSITIONAL (first noun after verb, no voice) | 0.6634 | -0.103 BELOW |
| ELAB_ORDER_ONLY (perceptron, order cue only) | 0.6862 | (diagnostic) |
| ELAB_SCRAMBLE (perceptron, weights permuted) | 0.5295 | (control) |
| ELAB_ANIMACY_ONLY (perceptron, animacy cue only) | 0.3117 | (diagnostic ~= twin) |
| TWIN (random covered nominal, info-free) | 0.2872 | +0.479 (two-line beats it) |

**The elaborate machinery loses to the two-line rule, CI-separated.** Per the bar, "it ties or loses
the two-line rule at power -> the elaborate machinery does not earn its keep, and the recommendation is
to REPLACE it." That is a full PASS, and I then solved the problem underneath it: **the best reader for
this task is a word-order rule with a PRECISE voice cue**, which beats both the crude two-line rule and
the elaborate reader.

## THE BRAIN FRAME (opened first, per method)

**Which brain structure does this, and are we replicating its computation or substituting something
convenient?** Thematic-role assignment is cue integration (MacWhinney's Competition Model). The one
fact that decides this problem: **English is WORD-ORDER dominant** -- MacWhinney, Bates & Kliegl (1984)
show word order *beats* animacy in conflict for English adults; animacy dominance is faithful for
Italian-type languages and for *degraded/agrammatic* English, not healthy English. So:

- **Word order as the dominant cue -- PINNED-BY-EVIDENCE.** The two-line rule copies the brain's
  dominant English cue (Bever's 1970 NVN heuristic for canonical sentences).
- **Voice-flip on passives -- PINNED-BY-EVIDENCE.** Voice is the *only* valid cue on reversible
  passives (Caramazza & Zurif 1976; Ferreira 2003). The two-line rule's second line copies it.
- **Precise voice = auxiliary + participle morphology -- the OPERATION is PINNED** (that IS the surface
  marker of the passive); the 3-token window is OUR-INVENTION-UNDER-TEST (a swept parameter).
- **The elaborate reader's animacy cue -- MISLABELLED as brain-faithful; it is the WRONG cue for
  English.** The reader's docstring calls it "brain-faithful cue-integration"; its *learned* weights
  came out animacy-leaning, which for English is a brain-*infidelity*, and the data prove it hurts.
- **Verb-frame override (ditransitive) -- OUR-INVENTION-UNDER-TEST.** The operation (verb-conditioned
  role assignment; MacDonald et al. 1994; Trueswell et al. 1994) is PINNED, but my specific
  double-object heuristic did not measurably add (0.7902 vs precise 0.7950) -- tested and shelved.

The reversibility manipulation is the field's clean test of "is the comprehender USING syntax or
leaning on plausibility/animacy" (agrammatics fall to chance on reversible passives/object-relatives).
It is the discriminator this experiment is built around, and it is where the diagnosis is sharpest.

## WHAT I BUILT

- **`experiments/exp_reader_vs_twoline_qasrl_power_v1.py`** -- loads QA-SRL v2 gold (patient = the
  validated answer span to the ARG1 question), parses each sentence with the repo's own glass-box
  front-end, and scores every arm by span-accuracy (a picked token index is correct iff it lies in the
  gold patient span). The verb index is anchored from QA-SRL gold, so the tagger's verb errors do not
  confound patient selection -- the ONE variable is the patient-selection rule. Trains the elaborate
  perceptron on the QA-SRL **train** split (97,944 examples) and evaluates on **dev+test** (17,330
  aligned items). Paired bootstrap CIs (10,000 resamples), stratified by canonicity x reversibility.
- **`verification/test_reader_vs_twoline_qasrl_power.py`** -- scaffold-free witness: imports the
  experiment as a library, recomputes the headline on a reduced-but-real run, asserts the elaborate
  reader does NOT beat the two-line rule, the twin loses, and order >> animacy. WITNESS PASS.

## WHAT I MEASURED, AND THE BRAIN-MECHANISTIC DECOMPOSITION

Reading the strata (all n_boot=10,000) turns the aggregate into a mechanism:

| stratum | n | TWO_LINE | PRECISE | ELABORATE | elaborate vs two-line |
|---|---|---|---|---|---|
| ALL | 17,330 | 0.766 | **0.795** | 0.751 | **-0.015 BELOW** |
| canonical (patient after verb) | 11,994 | 0.903 | 0.953 | 0.874 | -0.029 BELOW |
| non-canonical (patient before verb) | 4,578 | 0.534 | 0.513 | 0.553 | +0.019 ABOVE |
| detected passive clause | 3,638 | 0.638 | 0.776 | 0.671 | +0.033 ABOVE |
| irreversible (patient inanimate) | 12,779 | 0.803 | 0.836 | 0.806 | +0.003 NOT_SEP |
| **reversible (patient animate)** | 1,897 | 0.800 | 0.826 | 0.684 | **-0.117 BELOW** |
| **both-args animate (true reversible)** | 462 | 0.848 | 0.885 | 0.747 | **-0.102 BELOW** |

1. **The elaborate reader's only wins are on non-canonical/passive** (+0.019/+0.033), a minority, and
   they are swamped by its losses on the canonical majority. On canonical sentences the extra
   machinery *over-thinks*: e.g. "Wind-blown sand scours **rocks** like sandpaper" -- the two-line
   rule takes the adjacent `rocks`; the elaborate reader scores `sandpaper` (the PP object) higher and
   picks it. On canonical items even PURE POSITIONAL (0.959) beats the elaborate reader (0.874).
2. **The elaborate reader collapses on REVERSIBLE items** (0.684 vs two-line 0.800; both-animate 0.747
   vs 0.848). This is the brain's own prediction: when both arguments are animate, animacy is
   neutralized and only word order/voice can recover the roles. The animacy-leaning reader mis-picks
   (e.g. "...**brought** in **miners** from around the world" -> elaborate picks `world`; two-line
   picks `miners`). Its `animacy_only` ablation on this stratum is 0.113 -- *below* the random twin.
3. **The ablations confirm English word-order dominance ON OUR OWN READER:** `order_only`=0.686 (nearly
   the full 0.751 -- the model's usable signal is word order), `animacy_only`=0.312 (~= the info-free
   twin 0.287). `scramble`=0.529 (drops 0.22 from full) proves the learned weights are not decorative,
   so the reader had a fair, trained shot -- and still lost to two lines of code.
4. **The push -- precise voice -- is the whole story of the crude rule's residual error.** The crude
   two-line detector fires on any nearby `is/was`, so it false-flips active clauses whose verb is not a
   participle and looks backward: "Mineralogists **are** scientists who study **minerals**" -> crude
   rule picks `who`; requiring participle morphology (study is not one) keeps it active -> `minerals`.
   Precise voice recovers +0.050 on canonical and +0.138 on genuinely-passive clauses, and it wins on
   the reversible stratum too -- it beats the elaborate reader by +0.142 there.

## DISK OUTRANKED THE BRIEF (two places)

1. **The "elaborate reader" the brief names is already positional on the live path.** The deployed
   `hdlab/situation_reader.py::_assign_roles` picks "PATIENT = nearest nominal strictly after the
   predicate" (+ a strictly-intransitive gate) -- i.e. the live reader is *already* essentially the
   two-line rule minus the voice flip. The elaborate cue-integration (the perceptron in
   `thematic_role_labeler.py`) is a drop-in it can opt into; this cell tests that machinery directly.
2. **A landed cell already hinted at this and I corrected its comparison.**
   `exp_thematic_role_labeler_qasrl_modern_revalidation_v1` (HARD_FAIL) found the perceptron is
   reproduced within 0.05 by an animacy-only ablation and scored it against a *positional* (non-voice)
   baseline (0.477). It never ran the clean voice-aware two-line rule. This cell does, and the
   voice-aware rule (0.766) closes almost all of that apparent gap and then beats the full model.

**One number in the brief did not reproduce, and it does not change the verdict:** the brief's §3/§4
imply the elaborate reader's extra signal is real but unproven at power (the +0.07 at n=100). At power
it is not merely unproven -- it is *negative* on honest voice (-0.015). The brief's own "full PASS =
it ties or loses -> REPLACE" anticipated exactly this.

## WHAT I DID NOT ESTABLISH

- **I did not run `extract_facts_strict` (the fate-verb reader that scored the original 0.90) itself at
  power.** It is specialised to a ~40-verb fate lexicon and does not fire on general QA-SRL verbs. I
  tested the GENERAL machinery the brief names (`thematic_role_labeler`), which is the "verb-conditioned
  role assignment" §3 says to keep only if it beats the positional rule. The n=100 SOLVED already
  decomposed the 0.90 into filter-selection + the two-line rule + a non-separated +0.07; this result
  resolves that +0.07 on the general machinery at 173x the power and finds it negative. If the strategy
  session wants the fate-verb reader powered on its own turf, that needs hand-adjudication of a larger
  fate-verb corpus draw (no gold exists) -- a separate, more expensive measurement.
- **QA-SRL over-samples passives (~21% of items here vs ~2-25% of natural text).** That is generous to
  the elaborate reader (its only wins are on passives), which makes the REPLACE verdict conservative:
  on the natural canonical-heavy distribution the elaborate reader would lose by *more*.
- **The precise-voice arm is a proposal, not a landed reader.** Its +0.029 is measured on this task and
  this front-end; a different tokenizer/tagger would move the absolute numbers (not the direction).
- **Span-accuracy, not exact-head-match.** A pick is correct if it lands in the gold patient span; this
  is the standard SRL scorer and is applied identically to every arm, so it cannot favour one.

## WHAT I WOULD WITHDRAW FIRST IF WRONG

The **+0.029 precise-minus-crude two-line margin** (the push), if the participle-morphology voice
detector interacts badly with the specific POS tagger on some register -- it is the newest, least-swept
piece. I would NOT withdraw the headline (elaborate loses to two-line): it is CI-separated at n=17,330,
reproduced by a scaffold-free witness, survives on every reversibility stratum, and the info-free twin
loses everywhere. The claim I would defend last, because a witness recomputes it from disk, is
"elaborate does not beat two-line and the twin loses."

## KEY REALIZATIONS

1. **The voice signal was a trap, and catching it flipped the headline.** QA-SRL's `isPassive` flag is
   a property of the QUESTION phrasing, not the sentence clause -- a passive question ("What can be
   seen?") is routinely asked of an ACTIVE sentence. Feeding that as "gold voice" made the two-line rule
   look *worse* than the elaborate reader (0.683 vs 0.719). Detecting voice from the sentence itself --
   the two-line rule's actual job -- flipped it: two-line 0.766 BEATS elaborate 0.751. The lesson: give
   the baseline the signal it would really compute, not a mislabeled gold.
2. **Stratify by reversibility or you measure nothing.** The aggregate -0.015 hides a +0.03 on passives
   and a -0.12 on reversible items. Only the reversibility split (the brain's own instrument for
   "is this syntax or plausibility?") shows the elaborate reader fails *exactly* where the brain says
   syntax is the only cue -- turning a bookkeeping number into a mechanism.
3. **Run the ablation the reader's own docstring claims.** The file says "brain-faithful cue-integration
   ... weighted by cue validity." Ablating to single cues showed the *learned* validity is animacy-
   leaning (animacy_only ~= random; order_only ~= full model) -- the wrong cue for word-order-dominant
   English. The reader's brand and its behaviour disagreed, and the ablation is what exposed it.
4. **"Replace it" is not the end -- find the BEST brain-faithful rule.** The refutation (elaborate
   loses) was the halfway point; the deliverable is that a word-order rule with *precise* voice
   (aux+participle morphology) beats both the crude rule and the machinery. The headroom was in the
   word-order/voice direction the brain points to, not in more cue-integration machinery.

## PROPOSED hdlab CHANGE (a result, not a landed diff -- Q111; strategy session lands it)

The recommendation is **REPLACE the elaborate cue-integration path for PATIENT selection with a
word-order + precise-voice rule**, and **do not weight animacy as a role cue for English**. Concretely:

1. In `hdlab/situation_reader.py::_pick_role_mentions` / `_assign_roles`, keep the positional backbone
   (already there) but add the PRECISE voice flip: if the predicate is passive (a BE-aux within 3
   tokens before it AND the predicate token is a past participle), select PATIENT = nearest nominal
   *before* the predicate (surface subject); else nearest nominal *after*. This is ~4 lines and beats
   the current positional-only behaviour by +0.10 on passive clauses.
2. Do NOT route patient selection through the `thematic_role_labeler` averaged-perceptron
   cue-integration: at power it loses to the two-line rule (-0.015) and collapses on reversible items
   (-0.12). If the perceptron is retained for AGENT/EXPERIENCER/RECIPIENT roles, its animacy cue should
   be down-weighted for English (it is the wrong cue; it is near-useless here and harmful on reversible
   patients).
3. The freed effort goes to Stage 2 (deciding what words MEAN), which `LONG_TERM_PLAN.md` names as the
   Phase-1 bottleneck -- exactly the redirect the bar calls for.

*A proposed diff is the answer; the strategy session re-verifies and lands it.*

## TLDR

The first step of the pipeline reads a sentence and works out "who did what to whom." We had suspected
the fancy version of that step was no better than a dumb two-line rule (use word order, and flip it for
"was X-ed" sentences). On a hundred hand-checked sentences the fancy version looked 7 points better,
but that could have been luck. I re-ran the contest on **17,330 real sentences with published correct
answers**. The dumb two-line rule doesn't just tie the fancy version -- **it BEATS it**, clearly and
repeatably. The fancy version fails worst on exactly the sentences that are hard for a reason: ones
where both things named could plausibly have done the action ("the miners brought..."), where you truly
need the grammar and the fancy version instead guesses from which noun sounds more like a doer -- the
wrong instinct for English. Better still, I found the reader that wins: the *same* two-line rule with a
slightly smarter check for "was X-ed" (look for the -ed/-en ending, not just a nearby "is/was"). It
beats both. So: retire the elaborate machinery for this step, use the two-line rule, and spend the
saved effort on the step that is actually broken -- figuring out what words mean.

## QUESTIONS

None.

## NEXT STEPS

1. **Land the precise-voice two-line patient selector** in `hdlab/situation_reader.py` (proposed above)
   and retire the perceptron cue-integration path for PATIENT; down-weight animacy as an English role
   cue. Re-verify on this cell's witness first.
2. **Redirect the freed effort to Stage 2** (`reader_meaning_channel` / meaning supply), the named
   Phase-1 bottleneck -- which is the explicit point of the bar's REPLACE branch.
3. **(Optional) Power the fate-verb `extract_facts_strict` reader on its own turf** with a larger
   hand-adjudicated fate-verb corpus draw, if the strategy session wants the original 0.90 cell's exact
   machinery powered rather than the general machinery it embodies. Expected to confirm the same
   direction; costs annotation because no gold exists there.
