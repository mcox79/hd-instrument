# **MEASURED WHERE IT ACTUALLY MATTERS -- INSIDE CREDIT WINDOWS -- THE VERB-SENSE GATE WOULD REMOVE `5.4%` OF CREDITED TOKENS. NOT `73%`, NOT `12.2%`. AND THAT MAKES IT A SMALL FIX, NOT THE HIGH-VALUE ITEM I CALLED IT TWO TURNS AGO.**

**Third and final denominator. Each time I measured closer to the decision, the number got smaller.**

---

## 1. THE PROGRESSION -- AND WHY EACH NUMBER WAS RIGHT IN ITS OWN FRAME

| what I measured | denominator | non-verb share |
|---|---|---|
| the old cell's **error list** | its 173 `light_lemmas` | **73%** |
| **all admitted tokens**, raw corpora | 70,141 tokens | **12.2%** |
| ⭐ **actually-credited targets, IN-WINDOW** | **12,670 credited tokens** | ⭐ **`5.4%`** |

*Method: `_credit_targets` -- **the real function** -- over 4-sentence windows around 8 frequent
referents (`jo`, `tom`, `dorothy`, `anne`, `meg`, `beth`, `amy`, `huck`) across 18,071 sentences from
the cell's own four corpora. `12,670` targets returned, `1,085` distinct.*

> ### **`5.4%` OF CREDIT IS THE OPERATIVE NUMBER. THE EARLIER FIGURES WERE NOT WRONG -- THEY ANSWERED DIFFERENT QUESTIONS, AND I QUOTED THEM AS IF THEY ANSWERED THIS ONE.**

⚠️ *In-window TYPES are `171/1,085 = 15.8%` -- **not comparable to the 73%**, which was a share of the
error bucket only, not of all credited types.*

## 2. 🔄 **AND THE DOMINANT LEAK REVERSES FROM LAST TURN**

*Most frequent non-verb credits, in-window:*

| | |
|---|---|
| **plural nouns** *(kinship + body parts)* | `sister` **66**, `lip` **56**, `friend` **37**, `girl` **18**, `knee` **17**, `ear` **16** |
| `-ing` pronouns/quantifiers | `something` 23, `anything` 20, `nothing` 19, `thing` 12 -- **62 of 683, ~9%** |
| `-ed` adjectives | `red` 11 |

**Last turn I called the `-ing` clause "the largest single source". That was true on RAW CORPORA and is
FALSE IN CREDIT WINDOWS**, where the plural-noun path dominates.

***Why: credit requires the token to be a clause subject or object linked to the referent. Kinship and
body-part nouns occupy those slots constantly ("her sister", "his lip"); `something`/`nothing` rarely
do.*** **The selection step changes which error dominates.**

## 3. 🔻 **SO I RETRACT "THE CHEAPEST HIGH-VALUE FIX"**

*Two turns ago I called the morphology gate "the cheapest high-value fix in this thread".*
**At `5.4%` of credited tokens it is a small, cheap, real improvement -- not a high-value one.**

⚠️ **AND IT IS A CEILING, NOT A GAIN.** *Removing 5.4% of credit only helps if those credits are
disproportionately harmful. I have not measured their effect on attribution precision, and given the
wall reproduced exactly through a much larger lemma change, I would not expect it to move the verdict.*

## 4. ⚠️ LIMITS

1. **8 hand-picked referents**, *chosen for frequency, not sampled.*
2. **My windows are 4 consecutive sentences containing the referent** -- *the cell builds windows from
   detected GOALS, which is a different and narrower selection.*
3. **`sister`/`lip` etc. are credited as SINGULAR lemmas** *because the surface form was plural -- the
   plural-noun path, consistent with the mechanism established earlier.*
4. **Nothing measured about attribution PRECISION** *-- only about what the filter would remove.*

## TLDR

I have now measured the same thing three times, each time closer to where the decision actually happens,
and it shrank each time: **73%, then 12%, then 5%.**

The first number counted distinct mistake-names in an old error list. The second counted real words in
real books. **The third counted what the system actually credits when it runs — and that is the only one
that matters. It is one in twenty.**

**The earlier figures were not wrong; they answered different questions, and I quoted them as if they
answered this one.**

**The picture also flipped.** Last turn I said the biggest leak was treating anything ending in "-ing" as
a verb. In the real setting the biggest leak is plural nouns — *sister, lip, friend, girl, knee, ear* —
because credit only goes to things sitting in subject or object position, and those words live there
while *something* and *nothing* do not.

**And I take back "the cheapest high-value fix".** At one in twenty it is cheap and real, but it is not
high-value — especially since the earlier wall survived a far larger change to the same machinery
without moving at all.

## QUESTIONS

None.

## NEXT STEPS

1. **Quote `5.4%` and stop quoting `73%`.** *The plan and notes now carry all three with their
   denominators.*
2. **This closes the morphology thread honestly:** *a small real defect, precisely located, with a
   bounded and modest payoff.*
3. *Method note: **three denominators, three answers, one question.** The discipline that saved this was
   refusing to project across them -- but I still led with the biggest number twice before measuring the
   right one.*
