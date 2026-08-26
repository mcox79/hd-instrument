---
priority: 3
review:
review_text:
---

# PROBLEM: THE ACCURATE HALF OF THE ORGAN COVERS 1% AND THE INACCURATE HALF DOES THE WORK

**slug:** `propagate_along_the_relation_that_carries_valence` - **opened:** 2026-08-23 by the strategy session
**status:** OPEN - **the population was priced before filing; it exists (see §5)**

> **PRIORITY NOTE, and the call is not mine alone:** filed at `8` because that slot was free, not
> because it ranks there. **On evidence I would put it around `4`.** It is the direct successor to a
> two-session synthesis finished hours ago, it is on the goal-bearing line, the experiment is
> feasible today, and it has the rare property of being a REPLACEMENT rather than an addition.
> *Re-rank it if you agree.*

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**
> *Reason, so you do not self-negotiate it: a dropped precondition invalidates the declared gate even
> when the result may be fine.*

---

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The system has a component that works out whether a word means something good or something bad. It
starts from about fifty words we labelled by hand, and reasons outward.

It does that in two ways.

**The first way is accurate and almost never used.** It follows *opposite-of* links: if a word is
the opposite of one we labelled "good", call it "bad". When it fires it is right about **84 times in
100** - but it fires on **19 questions out of 1,971. Under one percent.**

**The second way is inaccurate and does nearly all the work.** It asks which labelled words sit
*nearby* in a dictionary-style map of word meanings, and takes a vote. That is **307 of its 326
answers - 94% of everything it says**.

🔑 **AND NEARNESS IN THAT MAP CARRIES NO INFORMATION ABOUT GOOD VERSUS BAD.** Measured, with a proper
null and both positive controls: two words sitting close together agree about good-and-bad no better
than two words picked at random.

**So the component is loud where it is uninformed and silent where it is right.** That is the
problem.

## 2. WHY THIS ONE

- **It is a REPLACEMENT, not an addition.** Almost everything here proposes building something new.
  This proposes moving existing work onto an axis measured to carry the signal, and there is a
  measured axis to move it to.
- **The feasibility is already priced** (§5), so the run cannot fail for lack of items - which is the
  most common way a brief here wastes a session.
- 🔑 **AND IT HAS A CLEAN, ALREADY-MEASURED CONTROL BUILT IN.** The current Stage B is the thing to
  beat, and its accuracy on the same population is known: `0.6482` on 307 items. *You are not
  inventing a baseline; you are inheriting one.*

## 3. MEASURED vs INFERRED

**MEASURED** (this session and a concurrent one, both on disk):

| | |
|---|---|
| Stage A (opposite-of into the anchor set) | **`0.8421`** accuracy, fires on **`19`** items |
| Stage B (vote by taxonomic distance) | `0.6482` accuracy, fires on **`307`** items = **94% of output** |
| does taxonomic distance predict valence agreement? | 🔻 **NO** - Spearman `-0.0023` over 6,000 random verb pairs, inside a shuffled null (p95 `0.0231`) |
| positive controls on that null | ✅ antonym pairs `2.031` (larger, as required); same-synset `1.063` (smaller, as required) |
| whole organ, held-out | `0.6595` CI `[0.6074, 0.7117]` vs a majority floor `0.5583` CI `[0.5031, 0.6135]` |
| seed ablation (labels shuffled) | `0.4645` - collapses to chance, so the hand labels ARE load-bearing |

**INFERRED, NOT MEASURED:**

- 🔻 **That extending the lexical axis will beat Stage B.** The population exists; the accuracy at 2
  hops is **unknown**. Accuracy may decay with distance and the whole point may evaporate at hop 2.
- 🔻 **That Stage A's `0.8421` survives at scale.** `n=19`, and its CI is `[0.6842, 1.0000]` - too few
  to carry a claim. **Do not quote `0.8421` as established.**

## 4. ALREADY TRIED - DO NOT REDO

- **Scoring the whole organ against human valence ratings on 326 items: DONE.** `0.6595` vs a
  `0.5583` floor. *Do not re-run it to establish the organ works; that is settled and modest.*
- **Testing whether taxonomic distance carries valence: DONE, with a null and both positive
  controls.** It does not. *Do not re-measure this; build on it.*
- **Lowering the confidence gate to buy coverage: MEASURED AND EXPLICITLY NOT A FINDING.** Accuracy
  slides smoothly `0.6597 -> 0.5773` from 12% to 94% coverage. **Weakening a gate is not a result.**
- **The 52-word anchor set: DO NOT EXPAND IT AS THE FIX.** Only **6 of the 83** abstention points are
  "no anchor in range"; **78 are anchors that disagree**. More anchors addresses the small corner.

## 5. THE POPULATION EXISTS - PRICED BEFORE FILING

Reach along **lexical** relations (antonym, derivationally-related, similar-to, also-see,
verb-group) from each of the 1,971 polar held-out verbs to any anchor:

| | items | share |
|---|---|---|
| 1 hop | **`121`** | `6.1%` |
| 2 hops (additional) | `392` | `19.9%` |
| **1 or 2 hops** | **`513`** | **`26.0%`** |
| *for scale: Stage A today* | *19* | *1.0%* |
| *for scale: Stage B today* | *307* | *15.6%* |

🔑 **THE VALENCE-BEARING AXIS CAN REACH MORE ITEMS THAN THE UNINFORMATIVE ONE CURRENTLY DOES.** That
is what makes this worth a session rather than a note.

## 5b. VERIFY BEFORE YOU START

1. **Re-run the two numbers this whole brief rests on** and confirm they still hold: Stage A fires on
   `19` with accuracy `0.8421`, Stage B on `307` with `0.6482`. *Notes here go stale within hours;
   these were measured 2026-08-23.*
2. `python tools/before_you_start.py "propagate valence along antonymy instead of taxonomic distance"`
   and **read every row it returns**, not the first. *`"antonymy"` returns 0 cells but `"valence"`
   returns 29, all landed.*
3. `python tools/organ_map_cite.py` for anything you plan to cite about the mechanism, and
   `python tools/symbol_corrections.py dictionary_lookup` -- **that function's own docstring carries
   the Stage A / Stage B precedence rules**, and this project has repeatedly quoted a claim whose
   correction sat in the docstring of the thing being quoted.
4. **Re-price the population yourself** (§5). It is one script and it decides whether the run can
   fail informatively; do not inherit my `121` / `513` on trust.
5. `python tools/slot_status.py polarity` -- confirm what is and is not on the live path before
   assuming a gain here moves a downstream number.

## 6. THE BAR

**A CI-SEPARATED MARGIN OVER STAGE B, ON THE ITEMS BOTH CAN ANSWER, WITH THE FLOOR RECOMPUTED ON
THAT SUBSET.**

- 🚨 **THE COMPARISON IS PAIRED - SAME ITEMS, BOTH ARMS.** Comparing lexical-reach accuracy on its
  513 against Stage B's accuracy on its 307 is two different populations and means nothing. Score
  both on the intersection, and report the paired difference. *A related result this week was
  SEPARATED under a paired test and NOT_SEPARATED under an independent one; say which you ran.*
- **RECOMPUTE THE MAJORITY FLOOR ON WHATEVER SUBSET YOU SCORE.** It is `0.5583` on the current
  committed set and `0.5165` on the full population - **they are different numbers and neither
  transfers.**
- **REPORT ACCURACY PER HOP.** 1-hop and 2-hop are different mechanisms wearing one name; if 2-hop
  is at chance, the honest headline is "1 hop works, and it buys 6%".
- **BUILD THE INFORMATION-FREE TWIN:** traverse the SAME number of hops along the same relations but
  with the anchor labels SHUFFLED. If that scores well, the reach is doing the work and the labels
  are not. *The existing seed ablation does exactly this for the current organ and reads `0.4645`.*
- **A NULL IS A REAL ANSWER.** If lexical reach is no better than distance, that closes the direction
  and is worth knowing - say so plainly rather than reaching for a threshold.

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the organ | `hdlab/wordnet_polarity_propagation.py` - `dictionary_lookup`, Stage A / Stage B |
| the anchors | `ANCHOR_WORDS` (52), `ANCHOR_WORDS_EXTENDED` (84) |
| human valence gold | `data/grounding_testbed/Ratings_Warriner_et_al.csv` (13,905 rated words) |
| the two-session synthesis | `notes/RECONCILING_TWO_SESSIONS_THE_SEEDS_ARE_CLUSTERED_...md` |
| the powered scoring | `notes/ANCHOR_AND_PROPAGATE_SURVIVES_A_26x_LARGER_TEST_...md` |
| feasibility count above | `scratch/can_antonymy_reach_further.py` *(promote it if you cite it)* |

## 8. DO NOT QUOTE

- 🚫 **`0.8421` as Stage A's accuracy.** `n=19`, CI `[0.6842, 1.0000]`.
- 🚫 **The `0.5` coin-flip baseline for anchor purity.** The correct baseline on a balanced 26/26
  anchor set is `0.600`, and I got that wrong once already.
- 🚫 **"anchored valence propagates outward"** as an established mechanism. Measured: the seeds are
  CLUSTERED by polarity (`+0.0232` against a permutation null `[-0.0076, +0.0087]`), so Stage B reads
  **which hand-labelled cluster a target landed beside** - competence inherited from seed placement,
  not from the graph carrying valence.

## 9. WHAT THE BRAIN SAYS, AND WHERE WE ARE INVENTING

**The direction is PINNED by the plan, not by me:** ANCHOR + PROPAGATE, set 2026-08-06/07 - ground a
small affective anchor and reason outward, because **antonyms are distributional twins**, so
good-versus-bad is in neither grammar nor text statistics. *That premise is exactly why the
taxonomic-distance axis fails, and it was written down before anyone measured the failure.*

**OURS-UNDER-TEST:** which relation carries valence, and how far it propagates. **Nothing pins
WordNet's lexical relations as the brain's valence pathway** - this is our invention being tested,
and a null here indicts our choice of axis, not the anchor-and-propagate idea.
