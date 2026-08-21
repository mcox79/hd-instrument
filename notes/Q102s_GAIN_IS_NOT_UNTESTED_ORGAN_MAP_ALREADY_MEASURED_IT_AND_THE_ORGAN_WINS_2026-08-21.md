# **I TOLD THE OWNER "THE GAIN IS GENUINELY UNTESTED" WHEN FILING Q102. IT IS TESTED, IT IS IN `ORGAN_MAP` UNDER THE ORGAN'S OWN ENTRY, AND THE ORGAN WINS.**

**Sixth prior-work catch tonight, and the third where the answer was in the file the rules tell me to
read. `organ_map_cite.py vwfa` returned it in its FIRST constraint line.**

---

## 1. WHAT Q102 SAYS, AND WHAT IS ACTUALLY ON DISK

**My filed recommendation:** *"I have measured what the current arrangement costs, not what
connecting these would gain. **The gain is genuinely untested.**"*

**`ORGAN_MAP.md` §10.1, entry A1 (VWFA), heading verbatim: `NO LONGER UNTESTED`.**

*Disk-verified against `data/exp_orthographic_floor_vet_v1/metrics.json` -- every figure below
matches the map exactly, n = 4000, 5000-sample bootstrap, `a1_base_reproduces_c3_headline_exactly:
true`:*

| arm | hit@1 | 95% CI |
|---|---|---|
| **A1_BASE** -- the live substrate | **0.0480** | [0.0413, 0.0548] |
| **A6_TRIGRAM_ONLY** -- the form organ, alone | **0.0870** | [0.0783, 0.0960] |
| A8_MAXORTHO | 0.0610 | [0.0537, 0.0685] |
| A7_PREFIX_ONLY | 0.0588 | [0.0515, 0.0660] |

**`A6 - BASE = +0.0390 [0.0282, 0.0500]`, CI EXCLUDES ZERO. All three orthography-only arms beat the
live substrate, each CI-separated.**

> ### **THAT IS A FLOORED, CAN-FAIL, IDENTICAL-POOL MEASUREMENT OF EXACTLY THE THING Q102 PROPOSES TO WIRE. THE GAIN WAS MEASURED ON 2026-08-14 AND I TOLD THE OWNER IT WAS UNTESTED.**

## 2. ⚠️ **AND THE CAVEAT THAT MUST TRAVEL WITH IT -- FROM TONIGHT'S OWN WORK**

***That task has an ORTHOGRAPHIC SHORTCUT, and this cell's own `example_picks` are the evidence.***

| arm | what it picks |
|---|---|
| A6_TRIGRAM_ONLY | `don, able, capability, capable, abnormal, busy, burn, broad, absent, absence` |
| A7_PREFIX_ONLY | `abbey, able, abiotic, abbey, abnormal, above, about, abbey` |

**These are orthographic neighbours of the cue.** *An arm that picks spelling-neighbours can only
score ABOVE chance if the GOLD ANSWERS are themselves spelling-neighbours of the cue* -- **so this is
direct evidence for the shortcut I hypothesised earlier tonight, and it closes that open item.**

**AND THE SUBSTRATE WINS THE FULL RANKING** (median rank **37.0 vs 54.0**, already in the plan).
***So the honest statement is narrow: the form organ wins AT RANK 1, on a task where rank 1 is
partly reachable by spelling.***

## 3. ✅ WHAT THIS CHANGES FOR THE DECISION -- **NOT THE RECOMMENDATION**

| | |
|---|---|
| **wire form as a SEPARATE channel** | ✅ **UNCHANGED.** *Three independent measurements now support it.* |
| *"the gain is genuinely untested"* | 🚫 **WITHDRAWN. It was measured a week before I said it.** |
| the size of the gain | **`+0.0390` hit@1, CI-separated -- but on a task with a spelling shortcut.** |

**I am NOT filing a second board question.** *The recommendation is unchanged, and the owner
complained tonight about settled items reappearing in front of them. This belongs in the record, not
in a new prompt.*

## TLDR

When I asked you to decide whether to switch on our word-recognition components, I said we had never
measured what switching them on would buy. **That was wrong. It was measured on 14 August, and the
result is filed under the component's own entry in the document I am supposed to consult first.**

**The measured answer: the spelling-based component alone gets the right answer at the top of the
list nearly twice as often as our full system does** — 8.7% against 4.8%, on four thousand test
items, with the difference comfortably outside the margin of error.

**But it comes with a catch I found tonight, and this experiment's own records confirm it.** Looking
at what the spelling component actually picks — *abbey, able, abiotic, absent, absence* — **it is
choosing words that look like the question.** That only scores well if the right answers *also* tend
to look like the question. **So the test rewards spelling more than it should**, and on the fuller
measure of ranking our own system still does better.

**None of this changes the recommendation** — three separate measurements now point the same way.
**What changes is that I owe you a correction:** the thing I told you was untested had already been
tested, and I would have found it by reading the entry for the component itself.

**I am deliberately not filing this as a new question**, since you told me tonight that settled items
reappearing in front of you is worse than useless.

## QUESTIONS

None.

## NEXT STEPS

1. **Q102's "gain is untested" is WITHDRAWN.** *Recorded here, in the plan, and in STATUS.*
2. **The orthographic-shortcut hypothesis from earlier tonight is now SUPPORTED** by this cell's own
   `example_picks`. *That closes its open follow-up.*
3. *Method note: **`organ_map_cite.py vwfa` returned this in its first constraint line.** I ran it
   only because a different ID returned "NO MENTION" and the tool warned me that is not evidence of
   absence. **The tool's own caution is what produced the catch.***
