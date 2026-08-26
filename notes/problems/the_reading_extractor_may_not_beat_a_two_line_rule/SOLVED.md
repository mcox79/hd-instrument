---
problem: the_reading_extractor_may_not_beat_a_two_line_rule
status: SOLVED
bar: "On a held-out, hand-adjudicated (or controlled-proxy) role-assignment set LARGER than n=100, floor recomputed on that population: the elaborate reader must beat the two-line rule (word-order + voice, elaborate filters OFF) CI-separated over its UPPER bound, information-free twin LOSING. HOW WE WOULD KNOW IT FAILED, and this is a full PASS for the brief: it ties or loses the two-line rule at power -> the elaborate machinery does not earn its keep, and the recommendation is to REPLACE it and redirect the effort to stage 2."
result: "(1) BRIEF ANSWERED -- QA-SRL v2 gold PATIENT selection, n=17,330 held-out (span-accuracy): the elaborate perceptron cue-integration reader (hdlab.thematic_role_labeler) = 0.7511 LOSES to the two-line word-order+voice rule = 0.7661; elaborate-minus-two-line = -0.0149, 95% CI [-0.0188,-0.0112] BELOW -> REPLACE (full PASS). (2) BEST SIMPLE READER -- word order + PRECISE voice (aux+participle) = 0.7950, beats crude two-line (+0.0289) and elaborate (+0.0439). (3) TWO-LINE IS NOT THE CEILING -- on reversible OBJECT-RELATIVES/CLEFTS (the brain's dorsal-parser regime) the two-line rule COLLAPSES (synthetic n=1500: 0.001; real QA-SRL n=1711: 0.080 -- both BELOW the info-free twin), while the brain's FILLER-GAP mechanism recovers it: oracle-parse 1.000 (synthetic), real-parser +0.223 CI[+0.203,+0.244] (synthetic) and +0.214 CI[+0.194,+0.234] (real QA-SRL), both ABOVE. The real-parser filler-gap arm is NET-NEGATIVE overall (-0.107) from weak-parser false-positives on canonical clauses -> the frontier is a STRONGER PARSER + a construction gate, not more cue-integration. (4) BRAIN-FIDELITY -- my structural mechanisms are OVER-ACCURATE (the tell of a convenient substitute): on the Gordon (2001) similar/dissimilar object-relative design, structural point-to-antecedent shows NO similarity effect (flat 1.000/1.000), while a brain-faithful CUE-BASED RETRIEVAL mechanism reproduces the human similarity-interference drop (+0.052/+0.139/+0.201 across a temperature sweep, all CI-separated ABOVE)."
floor: "Per-regime strongest floor recomputed on each population. Natural QA-SRL (n=17,330): floor = the two-line rule = 0.7661; the elaborate reader fails to clear it. Fronted regime (object-relatives/clefts): floor = the two-line rule, which there scores 0.001 (synthetic) / 0.080 (real) -- BELOW the info-free TWIN (0.29-0.46), so the two-line rule is not even a floor there; the filler-gap mechanism clears the TWIN. Info-free TWIN (random covered nominal, 5 seeds) = 0.287 (QA-SRL) and loses to the two-line rule CI-separated in every NATURAL stratum; on the fronted regime the TWIN BEATS the two-line rule (which anti-picks). POSITIONAL (no voice) = 0.663."
controls: "(a) INFO-FREE TWIN (random nominal, 5 seeds): loses to the two-line rule CI-separated on natural text (0.287 vs 0.766); on the fronted regime it BEATS the two-line rule -> EXCLUDES 'the two-line rule always works' and localizes its failure. (b) ELAB_SCRAMBLE (perceptron weights permuted)=0.5295 vs full 0.7511 -> the learned weights carry real signal (drop 0.22): the elaborate reader had a FAIR trained shot and still lost -> EXCLUDES 'it loses only because untrained'. (c) ELAB_ANIMACY_ONLY=0.312 (~=twin) vs ELAB_ORDER_ONLY=0.686 -> the reader's usable cue is WORD ORDER; animacy is near-useless -> EXCLUDES 'animacy is a valid English role cue' (MacWhinney/Bates/Kliegl 1984). (d) REVERSIBILITY stratification: the elaborate reader collapses WORST on reversible items (0.684 vs two-line 0.800) -> EXCLUDES 'the loss is a scoring artifact'. (e) FILLERGAP_ORACLE vs FILLERGAP_REAL (oracle 1.000 vs real 0.19-0.29 on the fronted regime) -> the mechanism is right; the shortfall is PARSER QUALITY, not a ceiling -> EXCLUDES 'the fronted regime is unsolvable'. (f) CUE_RETRIEVAL vs FILLERGAP_ORACLE on the Gordon similarity manipulation (cue-retrieval shows the human drop CI-separated at 3 temperatures; structural is FLAT) -> EXCLUDES 'structural point-to-antecedent computes the way the brain does' (it is over-accurate). (g) TWIN shows NO similarity effect on the fidelity probe -> EXCLUDES 'the similarity effect is an artifact of the item set'."
files_changed: "experiments/exp_reader_vs_twoline_qasrl_power_v1.py, experiments/exp_reader_fillergap_reversible_objrel_v1.py, experiments/exp_reader_cue_retrieval_interference_v1.py, verification/test_reader_vs_twoline_qasrl_power.py, verification/test_reader_fillergap_reversible_objrel.py, verification/test_reader_cue_retrieval_interference.py, data/exp_reader_vs_twoline_qasrl_power_v1/, data/exp_reader_fillergap_reversible_objrel_v1/, data/exp_reader_cue_retrieval_interference_v1/, notes/problems/the_reading_extractor_may_not_beat_a_two_line_rule/SOLVED.md. NO hdlab/ file changed (proposed diff below, Q111). (Leftover throwaway probe experiments/_probe_qasrl_patient_gold.py could not be deleted -- deletions are permission-gated this session; it writes nothing.)"
reverify: ".venv/Scripts/python.exe verification/test_reader_vs_twoline_qasrl_power.py  (headline REPLACE); also verification/test_reader_fillergap_reversible_objrel.py (two-line is not the ceiling) and verification/test_reader_cue_retrieval_interference.py (fidelity: cue-retrieval reproduces human interference)"
---

# SOLVED: the elaborate reader loses to a two-line rule -- but the two-line rule is not the ceiling, and the brain's real mechanism is cue-based retrieval, not either of them

The brief asked one question (does the elaborate reader earn its keep?). Pushed as far brain-foundational
as it goes, it opened four, and all four are now answered on disk.

## 1. THE BRIEF, ANSWERED AT POWER -> REPLACE

Powering the n=100 comparison to **n=17,330 real gold items** (QA-SRL v2, dev+test), scoring which
nominal is the verb's PATIENT (span-accuracy):

| arm (QA-SRL patient selection, n=17,330) | acc | vs two-line rule |
|---|---|---|
| **TWO_LINE_PRECISE** (word order + aux+participle voice) | **0.7950** | **+0.0289 [+0.0260,+0.0319] ABOVE** |
| **TWO_LINE** (word order + voice) -- the baseline | **0.7661** | -- |
| **ELABORATE** (thematic_role_labeler perceptron) | **0.7511** | **-0.0149 [-0.0188,-0.0112] BELOW** |
| ELAB_ORDER_ONLY / ELAB_ANIMACY_ONLY | 0.686 / 0.312 | (diagnostics) |
| ELAB_SCRAMBLE (weights permuted) | 0.5295 | (control) |
| TWIN (random nominal, info-free) | 0.2872 | two-line beats it +0.479 |

The elaborate machinery LOSES to the two-line rule, CI-separated. Per the bar ("it ties or loses ->
REPLACE"), that is a full PASS. It collapses worst on **reversible** items (0.684 vs 0.800) -- the
brain-predicted failure of its animacy-leaning cue for word-order-dominant English (MacWhinney, Bates &
Kliegl 1984). The best simple reader is word order + a PRECISE voice cue (aux + participle morphology),
which recovers the crude rule's false-passive errors.

## 2. BUT THE TWO-LINE RULE IS NOT THE CEILING -- IT FAILS WHERE THE BRAIN'S DORSAL PARSER EXISTS

The QA-SRL win is on canonical-heavy text. The brain recruits its DORSAL stream (posterior Broca's
BA44 + arcuate fasciculus) for **reversible non-canonical** clauses -- object-relatives and object-
clefts, where the patient is a FRONTED antecedent reached by a filler-gap/movement dependency, NOT by
linear position (Friederici 2011; Grodzinsky & Santi 2008; Caramazza & Zurif 1976). On a CONTROLLED
reversible set (gold by construction; `exp_reader_fillergap_reversible_objrel_v1`, n=1500/cell) and on
REAL QA-SRL object-relatives (`exp_reader_vs_twoline_qasrl_power_v1`, n=1711):

| construction | two-line | brain filler-gap (ORACLE parse) | filler-gap (REAL arc parser) |
|---|---|---|---|
| synthetic object_relative (n=1500) | **0.001** | **1.000** | 0.224 (+0.223 ABOVE) |
| synthetic object_cleft (n=1500) | **0.003** | **1.000** | 0.186 (+0.183 ABOVE) |
| REAL QA-SRL object-relative-like (n=1711) | **0.080** | -- | 0.294 (**+0.214 ABOVE**) |
| synthetic canonical / passive | 1.000 | 1.000 | 0.95 / 1.00 |

On the fronted regime the two-line rule is **below the info-free twin** -- it systematically anti-picks.
The brain's filler-gap operation with a correct parse resolves it PERFECTLY (1.000), so **the two-line
rule is not the ceiling**; and even our weak arc parser (UAS ~0.79) beats the two-line rule there
CI-separated on synthetic AND real text. **Honest cost:** applied ungated with the weak parser, the
filler-gap arm is NET-NEGATIVE overall on real data (-0.107) because the parser false-fires the
relative-clause rules on canonical sentences (-0.18 there). So the real frontier is a **stronger
relative-clause parser + a construction gate** -- a missing PRIMITIVE to BUILD, not a ceiling. That is
the honest hole in "two lines beat the machinery": it is true on the easy regime and the OPPOSITE on the
hard one.

## 3. BRAIN-FIDELITY: MY MECHANISMS ARE OVER-ACCURATE -- THE BRAIN'S IS CUE-BASED RETRIEVAL

A deeper fidelity drill (grounded, adversarial) found that "point to the antecedent" is not how the
brain resolves the dependency. The brain does **cue-based memory retrieval** of the filler at the gap
(Lewis & Vasishth 2005; McElree/Foraker/Dyer 2003; Van Dyke & McElree 2006), and therefore suffers
**similarity-based interference**: the object-relative penalty grows when a similar intervening noun
matches the retrieval cues (Gordon, Hendrick & Johnson 2001). A structural pointer is IMMUNE -> it is
MORE accurate than humans, the tell of a convenient substitute. I tested this
(`exp_reader_cue_retrieval_interference_v1`, Gordon design, n=2000/condition):

| mechanism | similar | dissimilar | similarity effect (dis-sim) |
|---|---|---|---|
| structural point-to-antecedent (ORACLE) | 1.000 | 1.000 | **+0.000 FLAT (over-accurate)** |
| **cue-based retrieval** (ACT-R-style, cue-overload) | 0.71-0.90 | 0.91-0.96 | **+0.05..+0.20 CI-separated ABOVE (temp sweep)** |
| two-line | 0.000 | 0.000 | +0.000 (fails outright) |
| twin (control) | 0.46 | 0.46 | +0.000 (no artifact) |

The cue-based retrieval mechanism REPRODUCES the human interference signature (worse when a similar noun
competes at retrieval), robustly across a temperature sweep; the structural mechanism does not. **So the
brain-faithful copy of the computation is content-addressable retrieval with cue-overload, not
structural pointing** -- but note the direction of the tension in Section 5.

## 4. BRAIN-FIDELITY VERDICT TABLE (each component, PINNED or OURS-UNDER-TEST)

| component | verdict | evidence |
|---|---|---|
| positional patient (NVN heuristic) | **PINNED-BY-EVIDENCE** (ventral/heuristic route) | Bever 1970; Ferreira 2003 |
| voice-flip (reassign role on passive) | **OVER-SIMPLIFICATION** -- the brain often FAILS to flip (role-reversal on implausible passives) | Ferreira 2003 |
| aux+participle voice detection | **DEFENSIBLE-REDUCTION** -- real cue; ignores by-phrase, be/get, animacy | be/get-passive lit. |
| filler-gap = point-to-antecedent | **OVER-SIMPLIFICATION** -- infallible; brain shows similarity interference | Gordon et al. 2001 |
| dual-route HARD if/else | **OVER-SIMPLIFICATION** -- the routes run PARALLEL and COMPETE, not dispatched exclusively | Bornkessel-Schlesewsky & Schlesewsky 2013 |
| cue-based retrieval | **PINNED as the faithful mechanism** (tested: reproduces the human signature) | Lewis & Vasishth 2005; Gordon 2001 |

## 5. THE ENGINEERING vs FIDELITY TENSION (stated honestly, owner's call)

There is a real fork here that the owner should see: the meaning pipeline wants MAXIMALLY ACCURATE role
assignment (get the right patient), and for that the structural mechanisms are BETTER precisely BECAUSE
they are over-accurate -- they do not make the human errors. The brain-faithful mechanism (cue-based
retrieval) is LESS accurate by design (it reproduces human interference errors). So "most brain-faithful"
and "most accurate for extraction" point in DIFFERENT directions on the hard regime. My recommendation:
for the EXTRACTION goal, adopt the structural filler-gap resolver and invest in a stronger parser (the
accuracy ceiling); keep the cue-based-retrieval result as the faithful model of comprehension, relevant
if/when the goal becomes modeling human reading rather than maximizing extraction accuracy.

## WHAT I DID NOT ESTABLISH

- **I did not build the stronger parser** that the fronted regime needs; I diagnosed it (oracle 1.000 vs
  real ~0.25) and localized it (relative-clause gap resolution at UAS 0.79). That is a BUILD, a separate
  organ-level effort.
- **The fronted-regime real-text set (n=1711) is object-relative-LIKE** (patient before verb, active),
  detected structurally, not hand-verified to be all true object-relatives; it also contains reduced
  relatives and fronting. The synthetic set is clean; the real set corroborates the direction.
- **The cue-retrieval model's exact drop magnitude is parameter-dependent** (I swept temperature to show
  the effect's PRESENCE is robust, not to claim a specific number). It is a minimal ACT-R-style model,
  not a fit to human RT data.
- **I did not run `extract_facts_strict`** (the fate-verb reader that scored the original 0.90) itself at
  power; I tested the GENERAL machinery the brief names. See the prior n=100 SOLVED for that decomposition.

## WHAT I WOULD WITHDRAW FIRST IF WRONG

The **+0.214 real-QA-SRL filler-gap gain** on the object-relative-like stratum, if that structurally-
detected stratum is contaminated by non-fronted items -- the synthetic result (clean gold) is the one I
would defend last. I would NOT withdraw the headline (elaborate loses to two-line at n=17,330: CI-
separated, witness-reproduced, twin loses everywhere) nor the fidelity finding (structural is flat,
cue-retrieval shows the drop, across a temperature sweep, both witness-reproduced).

## KEY REALIZATIONS

1. **The voice signal was a trap that flipped the headline.** QA-SRL `isPassive` is the QUESTION's voice,
   not the clause's; feeding it as gold made the two-line rule look worse than the elaborate reader.
   Detecting voice from the sentence -- the rule's actual job -- flipped it to two-line WINS.
2. **"Replace it" was the halfway point; the ceiling question was the real one.** Stopping at "two lines
   beat the machinery" would have implied the brain's parsing is unnecessary. Testing the regime the
   brain's dorsal parser exists for showed the OPPOSITE: there the two-line rule is below random, and the
   brain's filler-gap mechanism is required. The aggregate win hid a regime where the story inverts.
3. **Oracle-vs-real parse turned a null into a diagnosis.** "Nothing beats the two-line rule on the hard
   cell" was a WEAK-PARSER artifact, not a ceiling: with a correct parse the mechanism is perfect. Route
   the error by flavor -- missing-PRIMITIVE (a stronger parser), not intrinsic-limit.
4. **Over-accuracy is a fidelity FAILURE, not a success.** The drill's sharpest point: a mechanism that
   never makes the human error is not a copy of the human computation. Building the Gordon (2001)
   similar/dissimilar test and showing my structural arms are FLAT while cue-based retrieval reproduces
   the human drop is what converted "we cite neuroscience" into "we test the brain's actual computation."
5. **Most-brain-faithful and most-accurate can diverge.** Naming that fork (Section 5) is itself the
   finding: the faithful mechanism (error-prone retrieval) is not the one the extraction pipeline wants.

## PROPOSED hdlab CHANGE (a result, not a landed diff -- Q111; strategy lands it)

1. **REPLACE the perceptron cue-integration path for PATIENT selection with word order + PRECISE voice**
   (aux + participle). In `hdlab/situation_reader.py::_pick_role_mentions`, keep the positional backbone
   and add the participle-gated voice flip (~4 lines). Do NOT weight animacy as an English role cue.
2. **ADD a filler-gap resolver for relative-clause constructions**, GATED on confident relative-clause
   detection (only fire when the verb's clause is reliably a relative clause) so the weak parser's
   canonical false-positives (-0.18) do not leak. Until the gate is reliable, keep it OFF on the live
   path -- its ungated form is net-negative.
3. **Invest in a stronger relative-clause / filler-gap parser** -- this is the measured ceiling on the
   reversible non-canonical regime (oracle 1.000 vs real ~0.25), and it is the brain-foundational build,
   not more cue-integration. Redirect the effort freed by (1) here and to stage 2 (meaning).
4. **(Fidelity track, optional)** if the goal shifts to modeling human comprehension, the faithful
   patient-retrieval is content-addressable retrieval with cue-overload (reproduces Gordon interference),
   not structural pointing.

## TLDR

The pipeline's first step reads a sentence and works out who did what to whom. We suspected its fancy
version was no better than a dumb two-line rule (word order, flipped for "was X-ed"). On 17,330 real
sentences the dumb rule doesn't just tie -- it BEATS the fancy version, so retire the fancy machinery
for ordinary sentences. BUT that's only true for easy sentences. On the genuinely hard ones -- "the
banker that the lawyer chased", where you must hold the first noun in mind and connect it across the
sentence, exactly the sentences the brain switches on a special circuit for -- the two-line rule is
WORSE than guessing, and the brain's real trick (reach back and grab the noun the clause is about) gets
them right. Our software can't do that reliably yet because our grammar-parser is too weak, so the real
job is a better parser, not a fancier guesser. And going deeper: the brain's version of "reach back and
grab" isn't perfect -- it's a memory lookup that a similar nearby word can hijack, which is why people
misread those sentences too. We built that faithful version and it makes the same mistakes humans do,
where our clean version doesn't -- a reminder that copying the brain sometimes means copying its errors,
and that "most accurate" and "most brain-like" aren't always the same choice.

## QUESTIONS

None. (One decision is flagged for the owner in Section 5: for the hard regime, optimize for extraction
accuracy via a stronger parser, or for fidelity via cue-based retrieval. My recommendation is the former.)

## NEXT STEPS

1. **Land the precise-voice patient selector** and retire the perceptron cue-integration for PATIENT
   (proposed hdlab #1). Re-verify on the witness first.
2. **Build a stronger relative-clause / filler-gap parser** (the measured ceiling on the reversible
   non-canonical regime) and a construction gate; then re-run the filler-gap arm gated. This is the
   brain-foundational build the honest hole points to.
3. **Redirect freed effort to stage 2 (meaning)** -- the named Phase-1 bottleneck and the point of the
   bar's REPLACE branch.
4. **(Optional fidelity)** if modeling human comprehension becomes a goal, adopt cue-based retrieval and
   validate against human RT/accuracy on the Gordon and Ferreira designs.
