---
priority:
review: EXCELLENT
review_text: "Refuted my proposed fix and found what the signal actually is: store membership, not confidence. INTEGRATION CAVEAT ADDED 08-23: its 0.999 is read-words vs invented strings; on real English we simply have not read, the same gate refuses 90.6 percent. Wire DEFAULT-OFF."
---

> # 🔻 **INTEGRATION NOTE, ADDED 2026-08-23 WHILE WIRING THIS -- THE ARM NOBODY RAN.**
> *The EXCELLENT rating stands and nothing below challenges the finding. Re-verify PASSED here:
> familiarity gate `1.000`/`1.000`/`1.000`. This is about what the number MEANS for switching it on.*
>
> ✅ **WHY THE FINDING IS SOLID:** the refusable signal is **cue familiarity**, not answer
> confidence, and the brief's own named mechanism is refuted in the same run (similarity threshold
> `0.568`/`0.524` against an info-free floor of `0.500`). **The LEVEL control is what makes it
> convincing** -- the recollection-level gate FAILS the same bar (`accept_real 0.008`), so this is
> not "any membership check passes."
>
> 🔻 **BUT EVERY "REAL" ITEM WAS A WORD THE SUBSTRATE HAD JUST READ**, so the positive class is
> defined by the very property the gate reads. *The submission says so in its own control 7 -- "a
> clean trace-presence boundary".* **A lookup asked to separate present from absent returns `1.000`
> by construction.** So I measured the deployment case instead: **genuine English words we have
> simply not read**, taken from an EXTERNAL list that was not built from our store.
>
> | after a 2 x 1,500-sentence read | |
> |---|---|
> | familiarity set | **`4,429`** lemmas |
> | real English words sampled | `4,000` (Lancaster norms) |
> | would be ANSWERED | `376` -- **`9.4%`** |
> | 🔻 **would be REFUSED** | `3,624` -- **`90.6%`** *(`abdomen`, `abduct`, `aardvark`)* |
>
> ⚖️ **THIS IS NOT A DEFECT IN THE SUBMISSION AND MAY NOT BE A DEFECT AT ALL.** Refusing a word you
> have never encountered is arguably the CORRECT conservative behaviour, and it is exactly what
> "contribute, do not decide" asks for. **The two numbers answer different questions:** `0.999` =
> *does it tell read words from invented ones* (YES, decisively); `90.6%` = *what share of ordinary
> English it refuses* (the cost of switching it on).
> 🚫 **DO NOT read "balanced `0.999`" as "the system knows what it knows about English."** It knows
> what it has READ, which after a few thousand sentences is a small slice of the language.
> ➡️ **WIRING DECISION: DEFAULT-OFF**, or ON only where refusing unread vocabulary is the wanted
> behaviour.
> 🔑 **AND A POINTER TO ANOTHER OPEN BRIEF:** `abandon` is answered while `abandoned` is refused --
> that is `lookup_does_not_lemmatise` surfacing here as refusals of INFLECTED FORMS of words we HAVE
> read. *Fixing that would move this number without touching the gate.*
> *Witness: `verification/test_the_familiarity_gate_refuses_most_of_english.py` (external word list,
> positive control that the read happened, negative control that it does not refuse everything).*

> # MY REVIEW OF THE SUBMISSION: **EXCELLENT**
> *(reviewed 2026-08-23 by the strategy session. Re-ran their witness: PASS, with both native
> refuse rates at `0/20` and the positive control refusing `8/8` invented strings.)*
>
> **I FILED THIS AS A WIRING JOB AND SAID THE GATE WAS "ALREADY BUILT AND TESTED, SIMPLY NOT
> CONNECTED". THEY CONNECTED IT AND IT DOES NOT WORK.** Thresholding a route's top-1 retrieval
> confidence separates real from invented words at **AUC `0.624`** on one route and **`0.547`** on
> the other, and the calibrated gate's balanced accuracy (`0.568` / `0.524`) sits **at or inside**
> the information-free floor of `[0.447, 0.553]`. At a threshold refusing `90%` of invented words it
> keeps **`24%` and `20%`** of real ones. **A gate that throws away four fifths of what it knows is
> not a gate, it is an off switch.**
>
> **THE CONTROL SET IS WHAT MAKES THIS TRUSTWORTHY, AND ONE ARM IN IT IS THE FINDING.** The invented
> strings are matched to real words on length AND unigram letter frequency and verified absent from
> the read vocabulary, which forecloses the orthographic shortcut that would have made this look
> easy. The native-refuse baseline is `0/20` on both routes, so every refusal is attributable to the
> added gate. And the **consolidated-subset arm separates at AUC `0.65-0.95`** -- but on only `6-11`
> of `300` words.
>
> 🔑 **THAT IS THE ANSWER, AND IT IS NOT THE ONE I ASKED FOR: THE SEPARABLE SIGNAL IS STORE
> MEMBERSHIP, NOT SIMILARITY CONFIDENCE.** Whether a word is IN the consolidated store is knowable
> and discriminative; how confident a similarity lookup feels about it is not. **Refusal should be a
> membership question.** That is a different build from the one I filed, and I would not have got
> there from my own brief.
>
> 🔻 **THE ONE CAVEAT I WOULD ATTACH:** the `6-11 of 300` subset is small, so "membership
> separates" is a direction with a wide interval, not a bankable margin. It should be tested at
> power before anything is built on it -- which is what I have written into the tab rather than
> quietly promoting it to a plan.
>
> ## WHAT I DID WITH IT
> **Stages 5 and 6 of the SUBSTRATE tab rewritten.** Both said the fix was to connect the existing
> gate. That is refuted, and the tab now says so and names the membership route instead. **Nothing
> was landed in `hdlab/`** -- correctly, since the proposed change does not clear its bar.
>

# PROBLEM: THE SYSTEM CANNOT SAY "I DO NOT KNOW", AND THE PART THAT COULD IS BUILT AND UNPLUGGED

**slug:** `wire_the_refuse_gate_onto_the_readout` - **opened:** 2026-08-23 by the strategy session
**status:** OPEN - **this is a WIRING job with a measured cost and a written recipe, not a build**

> **RANKED 2, AND I AM STANDING BEHIND THE NUMBER RATHER THAN FILING IT LOW WITH AN APOLOGY.** The
> organ exists and is `HARD_PASS`; the wiring recipe is already written down; the cost of leaving it
> unplugged is now measured. **Cheap, certain, and it changes what every other read-out result
> means** - a score computed over items the system should have refused is measuring the wrong thing.
> *Everything below it moved down one.*

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

I made up eight words the system has never seen - `blorptaxis`, `qwixandor`, `vunmerlish` - and asked
it about them.

**Two of its three ways of answering gave every single one a confident, ranked, five-item answer.**
Not a shrug, not an empty list: the same shape of reply a real word gets.

The third way, `query()`, correctly says *"I do not know that word."*

**The component that decides when to refuse an answer already exists, already passed its tests, and
is not plugged into the two routes that need it.** The system's own wiring table has said so for
weeks; nobody had measured what it costs.

## 2. WHY THIS ONE, AT THIS RANK

- **It is a WIRING job, not a build.** `hdlab/refuse_gate.py` exists, is in the capability registry,
  and has landed `HARD_PASS` cells behind it. **Slot `Q3` even ships the recipe: *"Wire with
  `atom_consultation` OFF"*, with a probe showing monotone confidence `1.0 -> 0.0256`, 11/11
  distinct.** *You are connecting a proven part, not inventing one.*
- 🔑 **IT CHANGES WHAT EVERY OTHER READ-OUT NUMBER MEANS.** Any accuracy scored over a population
  that includes items the system should have refused is measuring the wrong quantity. **This is
  upstream of the scoring work, not parallel to it.**
- **The cost is measured, not asserted** (§3), and it was found by driving the substrate end to end -
  which is why an organ-by-organ pass had not surfaced it.

## 3. MEASURED vs INFERRED

**MEASURED 2026-08-23** - one 400-sentence `simplewiki` read, all three public read-out routes:

| route | invented strings answered | can it refuse? |
|---|---|---|
| `recall_sentence` | 🔻 **8 of 8** | **NO** |
| `recall_cortical` | 🔻 **8 of 8** | **NO** |
| `query` | 0 of 8 (`known=False`, `n_facts=0`) | ✅ **YES** |

*`query`'s correctness is not luck - `substrate.py` carries
`_selftest_query_refuses_what_it_never_read` protecting exactly this.*

**DIRECTIONAL, UNDERPOWERED, NOT A VERDICT** (n=8 real vs 8 invented, ONE read):

- returned neighbourhoods are statistically indistinguishable: `recall_cortical` real-vs-real overlap
  `0.200` against real-vs-invented `0.191`; `recall_sentence` `0.064` against `0.038`
- answers are generic: for `recall_cortical` the **top 5 items are `35%` of every slot returned**
  across 16 cues (`war` alone `9%`) - the same family as the `way`-attractor the plan records

**INFERRED, NOT MEASURED:** 🔻 **that wiring `Q3` will fix it.** The gate was validated on torch HD
tensors against its own codebooks, **not on these routes' output**. It may not transfer.

## 4. ALREADY TRIED - DO NOT REDO

- **Building a refuse gate: DONE.** `query "refuse gate"` returns **79 cells, 59 landed**, including
  `exp_cortex_refuse_gate_v9_joint_alpha_sigma_surface_controller_v1` and
  `exp_cortex_hippo_replace_with_refuse_gate_v1`, both `HARD_PASS`. **Do not build another.**
- **Establishing that `query` refuses correctly: DONE**, and it has a self-test. Leave it alone; it
  is the positive control for the other two.
- **Measuring the cost: DONE (this brief).** *Do not re-run the 8-invented-word probe to confirm the
  problem exists - run it POWERED, as the bar requires.*

## 5. VERIFY BEFORE YOU START

1. `python tools/slot_status.py Q3` - read the whole entry, including the measured cost appended
   2026-08-23 and the `atom_consultation` instruction.
2. `python tools/before_you_start.py "wire the refuse gate onto the read-out routes"` and **read
   every row**, not the first. *`"refuse"` alone returns 91 cells.*
3. `python tools/organ_map_cite.py Q3` and `python tools/symbol_corrections.py refuse_gate` -
   **this project has repeatedly quoted a claim whose correction sat in the docstring of the thing
   quoted.**
4. **Reproduce the 8-of-8 result yourself** before trusting it - one script, and it decides whether
   the problem is still live. *Notes here go stale within hours.*

## 6. THE BAR

**AFTER WIRING: INVENTED WORDS ARE REFUSED *AND* REAL WORDS ARE STILL ANSWERED. BOTH ARMS, OR THE
RESULT IS WORTHLESS.**

- 🚨 **THE TRAP IS NAMED IN OUR OWN SOURCE AND YOU WILL WALK INTO IT OTHERWISE.** `substrate.py`:
  ***"A store that refuses everything passes the nonce arm trivially."*** A gate that refuses 100%
  scores perfectly on the invented words and is useless. **REPORT THE REFUSAL RATE ON REAL WORDS AS
  PROMINENTLY AS ON INVENTED ONES.**
- **POWER IT.** n=8 vs 8 is this brief's evidence that a problem exists, not a measurement of a fix.
  Use **at least 100 of each**, with invented strings matched to real words on length and letter
  statistics so the gate cannot win on orthography alone.
- **THE INFORMATION-FREE TWIN:** a gate that refuses at the SAME RATE but at RANDOM. If it scores
  like the real gate, the gate is contributing nothing beyond its refusal rate.
- **RECOMPUTE ANY ACCURACY ON THE SURVIVING POPULATION.** Refusal changes which items are scored, so
  a floor imported from the pre-wiring population does not transfer. *This session made exactly that
  error this week and had to correct it.*
- **A NULL IS A REAL ANSWER.** If the gate does not transfer to these routes, say so - that is worth
  knowing and it sends the work to the retrieval space instead.

## 7. FILES AND ENTRY POINTS

| what | where |
|---|---|
| the gate | `hdlab/refuse_gate.py` (registered; `HARD_PASS` cells behind it) |
| the slot + recipe + measured cost | `hdlab/substrate.py`, slot `Q3` |
| the routes that cannot refuse | `Substrate.recall_sentence`, `Substrate.recall_cortical` |
| the route that CAN, as positive control | `Substrate.query`, `_selftest_query_refuses_what_it_never_read` |
| the probe that measured the cost | `scratch/can_the_readout_say_i_dont_know.py` *(promote it if you cite it)* |

## 8. DO NOT QUOTE

- 🚫 **The overlap numbers (`0.200`/`0.191`, `0.064`/`0.038`) as established.** n=8 vs 8, one read.
  **Directional only.**
- 🚫 **"the read-out is inert."** It is NOT - every cue gets a distinct answer. The failure is
  refusal and genericness, not inertness, and those need different repairs.
- 🚫 **`35%` top-5 concentration as a system property.** One route, one 400-sentence read, 16 cues.

## 9. WHAT THE BRAIN SAYS, AND WHERE WE ARE INVENTING

**Knowing that you do not know is a real and separable function** - metamemory, and the
feeling-of-knowing literature treats it as a judgement made ON a retrieval attempt rather than as an
absence of one. *That is exactly the shape here: the retrieval attempt succeeds and returns
something; what is missing is the judgement about it.*

**OURS-UNDER-TEST:** that `refuse_gate`'s confidence signal is the right judgement to apply to these
particular routes. **Nothing pins that.** A null here indicts our gate, not the idea that a system
should be able to decline.
