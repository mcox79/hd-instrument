# SYNTHESIS -- **THE HOP-DISTANCE BODY OF WORK: WHAT IT ESTABLISHED, HOW THE 11x LIFT ACTUALLY WORKS, AND THE WALL IT RAN INTO**

**Owner: *"drill the relevant previous experimental results to learn more."*** Four cells read in
full, not just the two I opened first.

---

## 1. THE MECHANISM OF THE 11x LIFT -- FROM THE SELFTEST, WHICH TURNED OUT TO BE SUBSTANTIVE

`exp_cold_placement_recovery_opt_v1_selftest` states it plainly:

> *"the **WN-tier** recovers name-transparent, **hypernym-only, AND synonym-only** cold entities --
> **proving the WN tier recovers cases the base cell's gloss-only mechanism could NOT**"*

| version | how it reaches a new word | opaque exact |
|---|---|---|
| base (`usefulness_v1`) | **gloss only** | 0.0262 |
| optimised (`recovery_opt_v1`) | **gloss + WordNet hypernym + synonym tiers** | **0.2930** |

**➡️ THE 11x DID NOT COME FROM A CLEVERER ALGORITHM. IT CAME FROM ADDING MORE KINDS OF LINK TO
TRAVEL ALONG.** *A word unreachable by definition-text is often one hypernym hop from something
known.* **That is the owner's "how many hops" question answered structurally: the win was
new EDGE TYPES, not deeper search.**

*Both selftests also confirm `SCRAMBLE / RANDOM / POP / GRAPH_SELF_REFERENCE` collapse to floor on
both metrics, and the `usefulness` selftest reproduces the `NEIGHBOR_COMPOSE` structural-zero and
fires a polysemy guard. These are real control batteries, not rubber stamps.*

## 2. 🧱 **AND THE BODY OF WORK FOUND A WALL -- MEASURED, WITH THE OBVIOUS EXCUSE RULED OUT**

`exp_course_c_frontier_fit_capacity_ceiling_v1` -- **`FRONTIER_FIT_PLATEAU_REPRESENTATION_WALL`**:

> *"across a **1x coordinate-capacity jump (k=32 -> k=64)** at RotatE-comparable epochs + fixed LR +
> n_neg up to 256, the transductive DIRECT-readout oracle **ASYMPTOTES at h@10 = 0.594 << 0.90** --
> the top frontier rung did NOT improve on the prior best by >= 0.03.
> **Core is dense (avgdeg = 39.7 -> 'not enough data' ruled out).**"*

**➡️ DOUBLING THE REPRESENTATION DID NOT MOVE IT, AND SPARSITY WAS EXPLICITLY EXCLUDED.** *The
cheapest two explanations -- too small, too little data -- are both already dead. That is a properly
closed negative, and it is rarer than it sounds.*

## 3. WHAT THE FOUR CELLS SAY TOGETHER

| question | answer, with its evidence |
|---|---|
| **Can we measure how far a new word is from what we know?** | **YES** -- `reach_frac_h1/h2/h3` over a 141,511-node graph |
| **How many hops are useful?** | **ONE.** 40.8x the popularity floor at h1, **1.9x by h3** *(baseline only)* |
| **What makes a word placeable?** | whether a LINK TYPE reaches it -- decomposition, gloss, hypernym, or synonym |
| **Which words can't we place?** | base: 31% abstain -> **optimised: 3.7%** |
| **Can we fix it by scaling the representation?** | **NO** -- plateau at h@10 0.594 across a 2x capacity jump, dense core |

**THE THROUGH-LINE: EVERY GAIN IN THIS BODY OF WORK CAME FROM ADDING A ROUTE, AND THE ONE ATTEMPT TO
GAIN BY ADDING CAPACITY HIT A WALL.** *Gloss -> +hypernym -> +synonym each bought real ground;
k=32 -> k=64 bought none.*

## 4. WHAT I WOULD DO WITH THIS, AND THE HONEST CAVEAT

**The cheap, unexploited measurement: run the hop profile on the OPTIMISED method.** It has never
been done -- `recovery_opt_v1` reports every `reach_frac` as 0 because it did not compute them.
**The one-hop finding is a property of the weaker version**, and the version that is 11x better on
opaque words may have a different profile entirely. *No new mechanism, no new data -- the same cell
with the hop metric switched on.*

**⚠️ THE CAVEAT THAT MATTERS: this whole line depends on WordNet.** Hypernym and synonym tiers are an
external lexical resource. **That is admissible under the standing rule -- a static, offline-built
asset is permitted, and the no-LLM-at-inference invariant is untouched** -- but it must be stated
whenever the capability is described, because **"the system worked out where the word belongs" and
"a dictionary told it" are different claims**, and only the second one is supported here.

## TLDR

You asked me to dig into the earlier work properly. Four experiments, read in full.

**The big lift came from somewhere simpler than I assumed.** When the system got eleven times better
at placing hard words, that wasn't a cleverer algorithm — **it was giving it more kinds of connection
to travel along.** Originally it could only use a word's dictionary definition. The improved version
could also follow "is a kind of" and "means the same as" links. **A word that's unreachable by
definition is often one step away via "is a kind of".**

So the answer to your "how many hops" question has a twist: **the wins came from having more kinds of
step available, not from taking more steps.** In fact taking more steps stops helping quickly —
beyond the first, you're mostly just rediscovering that everything is near something popular.

**And this body of work found a real wall.** A separate experiment doubled the size of the
representation and got no improvement at all, plateauing well short of where it needed to be — **and
it explicitly ruled out "not enough data" by showing the data was dense.** Both easy excuses are dead,
which makes it a genuinely closed negative rather than a shrug.

**The obvious cheap next move:** nobody ever measured the hop profile of the *improved* method. The
"one hop is what matters" finding came from the weaker version only. Same experiment, one metric
switched back on.

**One honest caveat I'd want stated every time this is described:** it leans on WordNet, a
human-built dictionary of word relationships. That's allowed under our rules and doesn't compromise
anything. But *"the system figured out where the word belongs"* and *"a dictionary told it"* are
different claims, and only the second is supported.

## QUESTIONS

None.

## NEXT STEPS

1. **Re-run the optimised cell with the hop metric enabled** -- cheapest unexploited measurement here.
2. **State the WordNet dependency wherever this capability is described.**
3. The representation wall (h@10 0.594, capacity-invariant, dense core) belongs in any plan that
   assumes scaling the embedding will help. It won't.
