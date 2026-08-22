# **THE VERB CHANNEL I HAD QUEUED AS "UNRUN" WAS RUN ON 2026-08-17. ARGUMENT STRUCTURE FAILED. THREE AFFECT DIMENSIONS BEAT ALL TWELVE SENSORIMOTOR ONES.**

**Tenth prior-work catch of the session, and the first that reverses a BUILD decision rather than a
sentence.** *`tools/before_you_start.py` returned `sensorimotor` 9 cells / `verb` 133 cells. Reading
all nine -- per the standing rule that a query returning N rows has N answers -- found
`exp_verb_event_salient_channel_v1` (LANDED 2026-08-17, `EVENT_SALIENT_CHANNEL_REAL`) and its
population-matched rescore.*

> 🚫 **SUPPLY, NOT LEARNING. The cell's own header sets
> `measures_the_instrument_not_a_capability = True` and `cue_regime = exact_key_own_code`.** *Every
> number below is a property of a HANDED-OVER RATING TABLE used as a similarity scorer. None of it is
> the substrate having learned anything. It names a TARGET; it is not a result about us.*

---

## 1. 🔻 **CANDIDATE 🅐 -- "VERB MEANING FROM ITS OWN ARGUMENTS" -- IS NOT UNRUN. IT RAN, AND IT FAILED.**

*The plan said: **"UNRUN: the two landed thematic/selectional cells derive a NOUN's meaning from
verbs, the opposite direction."** That is wrong. This cell built the RIGHT direction, from parsed
argument structure (`data/selectional_preferences_v1/selectional_slots_v1.pkl`):*

| arm | what it is | raw rho | band | after concreteness+frequency partial |
|---|---|---|---|---|
| **S1_SLOT_FRAME** (24 dims) | the sensorimotor code of the verb's **SUBJ and OBJ slot-fillers**, concatenated | **0.0442** | 🚫 `NOT_SEPARATED` | margin `+0.0140` CI `[-0.0384,+0.0593]` -- **`survives_partial: false`** |
| **S2_SLOT_DELTA** (12 dims) | **OBJ-mean minus SUBJ-mean** -- the asymmetry between the two roles | **0.0798** | 🚫 `NOT_SEPARATED` | margin `+0.0569` CI `[+0.0010,+0.1110]` -- *lower bound is one thousandth* |

> ### **BOTH ARMS ARE `NOT_SEPARATED` RAW. S1 DOES NOT SURVIVE THE PARTIAL AT ALL, AND S2'S PARTIAL MARGIN HAS A LOWER BOUND OF `+0.0010`.** *Neither is a channel worth building on.*

**AND I HAD ASSERTED THE MECHANISM ALL NIGHT WITHOUT MEASURING IT.** *Every verb write-up says "a
verb's neighbours are its ARGUMENTS -- `give/receive`, `feed/starve` share arguments and mean
opposites". **That is the S1/S2 hypothesis, it was tested four days ago, and the arguments do not
carry the meaning.*** *So the sentence is a plausible story, not a finding, and it should stop being
repeated as the explanation for our verb zero.*

## 2. ⭐ **AND WHAT DOES WORK ON VERBS IS AFFECT -- WHICH NO CANDIDATE OF MINE MENTIONED**

*All five arms below on the **IDENTICAL 3,152 pairs** (the population-matched rescore, `N_BOOT=2000`).
The 3 event dims are **Valence, Arousal, Dominance** (Warriner et al.), NOT effector/somatotopic dims.*

| arm | width | partial rho | 95% CI |
|---|---|---|---|
| **A1 = 12 sensorimotor + 3 AFFECT** | 15 | **`0.3655`** | `[0.3347, 0.3954]` |
| **A2 = the 3 AFFECT dims ALONE** | **3** | **`0.3030`** | `[0.2719, 0.3345]` |
| **A0 = the 12 sensorimotor dims (incumbent)** | 12 | **`0.2639`** | `[0.2309, 0.2999]` |
| A3 = 12 + 3 **NOISE** dims *(width control)* | 15 | 0.2469 | `[0.2134, 0.2800]` |
| A4 = 12 + 3 **WRONG** dims *(content control)* | 15 | 0.2322 | `[0.1979, 0.2645]` |
| *K = WordNet oracle (ceiling reference, no verdict weight)* | -- | *0.4808* | `[0.4529, 0.5077]` |

✅ **A1 CLEARS A0 AND BOTH WIDTH-MATCHED CONTROLS WITH NON-OVERLAPPING MARGINAL CIs** (`0.3347` vs
`0.2999` / `0.2800` / `0.2645`). **So the gain is CONTENT, not width -- adding three noise dims makes
it slightly WORSE, and three wrong dims worse still.**

⚠️ **A2-vs-A0 IS SUGGESTIVE ONLY, AND I AM NOT GOING TO OVERSTATE IT.** *Three affect dims beat twelve
sensorimotor ones on the point estimate (`0.3030` vs `0.2639`) but their **marginal CIs OVERLAP**
(`0.2719` vs `0.2999`) and* **no paired test was run** *-- and marginal overlap is not a test of a
difference, which is the exact rule this project already carries.*

✅ **EVERY ARM SURVIVES THE CONFOUND THE CELL ITSELF DECLARED BLOCKING.** *Its design note says the
verdict may not be read unless `C1_PARTIAL` (mean and abs-diff of concreteness AND log-frequency,
residualised inside every bootstrap replicate) holds -- "if A0's rho does not survive, the whole
'verbs need their own channel' framing may be a concreteness artifact". It ran on every arm;
`stop_ifs/iv_C1_PARTIAL_CONCRETENESS_CONFOUND = false`.*

## 3. ⚠️ **TWO NUMBERS THAT MUST NOT BE SWAPPED, INCLUDING ONE OF MINE FROM TONIGHT**

| number | what it is |
|---|---|
| **`0.2983`** *(mine, tonight)* | supplied norms12, **euclid**, **3,487** SimVerb pairs |
| **`0.2711`** *(this cell)* | `A0_INCUMBENT_12`, **3,161** pairs, its own comparator |

***DIFFERENT POPULATIONS AND DIFFERENT SCORERS. They agree qualitatively and neither may be quoted
in the other's sentence.*** *The A0-vs-A1-vs-A2 contrast IS internally valid -- the rescore exists
precisely to put every arm on one population.*

## 4. 🧠 WHY THIS IS THE MORE BRAIN-FAITHFUL ANSWER, AND WHY THAT CUTS BOTH WAYS

**I went looking for SOMATOTOPY** -- the Hauk/Pulvermüller result that action verbs drive motor
cortex by effector, `kick`/foot, `lick`/mouth. *The Lancaster norms carry exactly those five effector
dims, so the prediction was that verbs would load on them.* **They are already in A0, and A0 is the
arm that LOSES.**

***What separates verbs here is how an event FEELS -- its valence, its arousal, its dominance -- not
which limb performs it.*** *The cell's own pinned note anticipates this: pMTG is tuned by argument
valency and telicity, **explicitly NOT motor/premotor.***

⚠️ **AND THE HONEST LIMIT: this is a supplied table, so it says the INFORMATION is sufficient, never
that a reading system could recover it.** *Affect is plausibly harder to learn from text than
sensorimotor content, not easier. **The result names a target and does not hand us a method.***

## 5. ⚠️ LIMITS

1. **SUPPLY, NOT LEARNING** -- the cell flags itself as measuring the instrument, not a capability.
2. **No paired tests between arms**; every separation claim above rests on marginal CIs, which are
   weaker. *A1-vs-A0 does not overlap; A2-vs-A0 does.*
3. **S2's partial margin is technically ABOVE** (`survives_partial: true`) with a lower bound of
   `+0.0010`. *Calling argument structure "failed" rests on its RAW `NOT_SEPARATED` plus S1's
   outright failure -- not on S2 alone.*
4. **Socialness norms (Diveica et al. 2022) are NOT on disk**, so A1 is 15 dims, not the drill's
   hypothesised 17. *The channel is not fully built even as a supplied table.*
5. **This is SimVerb only.** *Nothing here was re-run on SimLex verbs.*

## TLDR

I was about to build a way for the system to work out what a verb means by looking at **who does it
and what it is done to** -- the subject and object. Before starting I searched what we had already
done, and found we ran exactly that four days ago. **It does not work.** Both versions of it score
close to nothing, and the stricter of the two checks kills one outright.

**I had been telling you that story all night as the EXPLANATION for why we score zero on verbs** --
that *give* and *receive* sit next to the same words. It is a good story. It is not what the data
says, and I should have checked before repeating it.

**What the same experiment did find is more interesting.** The information that separates verbs is
not which body part does the action -- it is **how the event feels**: whether it is pleasant, how
worked-up it is, and whether the doer is in control. Three such ratings beat all twelve of the
body-and-senses ratings we currently use, and adding them to the twelve is clearly better than either.

**Two cautions.** This is a table of human ratings, so it tells us what information is ENOUGH, not
that our system could ever learn it -- and feelings are plausibly harder to pick up from reading than
physical descriptions, not easier. And the "three beats twelve" comparison is suggestive rather than
settled; the "fifteen beats twelve" one is solid.

## QUESTIONS

None.

## NEXT STEPS

1. **STRIKE candidate 🅐 from the plan.** *It is not unrun and it is not promising.*
2. **REPLACE candidate 🅑.** *Wiring the RAW SENSORIMOTOR profile is wiring the arm that LOSES
   (`0.2639`). If a supplied verb channel is wired, it should be the 15-dim one at `0.3655`.*
3. **STOP repeating "a verb's neighbours are its arguments" as the explanation for our verb zero.**
   *It is the S1/S2 hypothesis and it was measured `NOT_SEPARATED`.*
4. *Method note: **`before_you_start.py` returned this in one command, and the catch came from reading
   ALL NINE rows rather than the top one.** The cell I needed was ninth alphabetically and its name
   contains neither "sensorimotor" as its subject nor the word I was searching for.*
