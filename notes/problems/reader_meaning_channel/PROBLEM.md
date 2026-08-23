---
priority: 1
review: 
review_text: 
---

<!-- ORIENTATION -- WRITTEN 2026-08-23 AFTER FIVE FINDINGS LANDED ON THIS BRIEF IN ONE DAY -->
> # 🗺️ **READ THIS FIRST: WHAT CHANGED, AND WHAT IT MEANS FOR THE BUILD**
> **SEVEN measurement blocks were added to this brief on 2026-08-23 and they sit above the original
> problem statement in the order they were written, not in the order you need them.** This is the
> map. *Each block carries its own reverify command; none of it is prose you have to take on trust.*
>
> | # | finding | what it does to the build |
> |---|---|---|
> | 1 | **The channel CANNOT GATE LINKS ALONE.** Capped it links `0` of `877`; uncapped `66%` similar / `37%` DISSIMILAR; no threshold better than the one already set. AUC `0.7002`. | 🚨 **THE BIGGEST ONE. The ask "use it INSTEAD" must become "use it AS WELL". Combine, do not substitute.** |
> | 2 | **STORAGE is fine, COMBINATION is the bottleneck.** Our format keeps `94%` of a real signal; bundling with 2 other vectors halves it, 8 leaves `26%`. | **Wiring the channel is necessary and NOT sufficient.** Keep few items per superposition. |
> | 3 | **SPARSITY does not rescue that** -- every density collapses to ~`+0.08`. | **Do not spend a week on a sparser code.** |
> | 4 | **NOR DOES AN ADDRESSED SLOT** -- addressing works, but binding PERMUTES interference rather than removing it. | *A key does not protect you from the other occupants.* **I wrote this advice before testing it; it is corrected in block 5.** |
> | 5 | **THE SAME ASSET GIVES THREE NUMBERS** by entry point (`+0.3107` / `+0.2676` / `+0.2463`); the lowest is the one the substrate calls. | **Measure the ASSET unclamped; ask what the SUBSTRATE sees with the clamped one. Never compare across.** |
> | 7 | 🧠✅ **SEGREGATION IS THE FIX FOR BUNDLING.** At EQUAL 256-dim budget, giving each item its own `D/k` slot beats superposing: at k=16, **16 dims isolated beats 256 dims shared, `+0.1949` vs `+0.0479`.** | 🔻 **A MEASURED COST, NOT A VALIDATED FIX.** *Two landed cells (`STRUCTURE_HURTS`, `CONJUNCTIVE_HURTS`) show replacing the flat bag makes a real readout task WORSE. Read the STOP block first.* |
> | 6 | **DO NOT COMBINE IT WITH WORDNET ON THIS EVIDENCE.** Pooled, WordNet looks twice as good (`+0.543` vs `+0.287`) -- but SimVerb's pairs were SELECTED by WordNet relation. Within class the edge collapses, and on the 60% with NO relation sensorimotor wins `+0.286` vs `+0.154`. | **A benchmark selected by a resource cannot fairly score that resource.** *A both-spokes hub was then tested on the unselected class: mean-of-both is the best rule tried, but the gain over sensorimotor alone is `+0.0245` `[-0.0021,+0.0520]` -- NOT established.* |
>
> ✅ **WHAT DID NOT CHANGE: the channel is still the right direction, and finding 6 STRENGTHENS
> that** -- on the pairs a taxonomy does not already link, which is the case a reader faces on new
> text, this channel is the best one we have. It carries real meaning and is
> the only channel we have that says anything about verbs at all -- our own reads `+0.0000` there.
> **The findings narrow HOW to use it; none of them argue for abandoning it.**
> ⚠️ **AND ONE STANDING PROHIBITION, because it is the obvious wrong move:** do **NOT** raise
> `GROUNDED_CAP`. It sits below the link threshold on purpose, and that gap is what makes "contribute,
> do not decide" enforceable in code rather than hoped for in prose.

> # 🥉 **PRIORITY 1 of 8 -- THE FLAGSHIP, AND THE BROADEST.** *(ranked 2026-08-22)*
> **This is the actual goal; it ranks third only because 1 and 2 are upstream of it and far more
> bounded.** *A better reader writing into a store that destroys what it writes, on a foundation that
> is discarded at the end of the run, cannot show what it is worth.*
> 🔑 **AND THIS BRIEF NOW OWNS A BLOCKER THE OTHERS DEPEND ON: `read()` NEVER CONSULTS THE
> MEANING ASSET AT ALL.** Runtime, positive-controlled: `0` calls to `grounded_similarity` /
> `grounded_vector` / `_table` across a 150-200 sentence read -- **the norms table is never even
> loaded.** The substrate's own B5 slot says so (`NEEDS_ADAPTER`, *"read() does not consult it"*).
> ⚠️ **SO THE ADAPTER IS PART OF THIS PROBLEM.** Until it exists, any meaning-side improvement --
> including PRIORITY 4 -- is real but UNMEASURABLE on a reading task. *Its hub-spoke combination rule
> is UNPINNED, so whatever you build there is our-invention-under-test, not brain-derived.*

> ## 🧠 **ADDED 2026-08-23 BY THE STRATEGY SESSION: THE CHANNEL COVERS OUR VERB HOLE, AND THIS BRIEF DID NOT SAY SO**
> **This brief mentioned "verb" ZERO times before this block**, while the sharpest fact about the
> channel it replaces is that it reads **exactly `+0.0000` on verbs**. So I measured whether the
> proposed replacement covers that hole before anyone builds it.
>
> 🔻 **CORRECTION, SAME DAY: "nobody had checked" IS FALSE.** `STATUS.md` has carried this
> since 08-22 (*"THE VERB HOLE IS OURS, NOT THE ASSET'S"*, asset verb `+0.2607` vs null `0.1241`,
> brief at priority 7). **My prior-work check looked in this brief and not in STATUS.** What is NEW
> below is the SOMATOTOPY split and the SimVerb-3500 measurement, not the headline.
>
> 🚨 **AND BEFORE YOU MEASURE ANYTHING HERE: THE SAME ASSET GIVES THREE DIFFERENT NUMBERS DEPENDING
> ON WHICH ENTRY POINT YOU CALL.** Same benchmark, same `3,487` pairs -- raw CSV 11 dims `+0.3107` |
> `grounded_vector` cosine `+0.2676` | **`grounded_similarity()` `+0.2463` <- WHAT THE SUBSTRATE
> ACTUALLY CALLS.** The shipped one is lowest because it is double-clamped (`min(0.45, max(0.0,
> raw))`): **56% of pairs sit exactly on the cap, 17% at zero.** ⚠️ **THE CAP IS DELIBERATE SAFETY**
> (below the link threshold) -- **do not remove it to improve a number.** ➡️ **Measure the ASSET
> unclamped; ask what the SUBSTRATE sees with the clamped one; never compare across.** *Three passes
> in two days got this wrong, two of them mine.* Pinned:
> `verification/test_which_number_is_the_meaning_asset.py`.
>
> ✅ **IT DOES COVER THE VERB HOLE** *(answering the question three paragraphs up -- stated in full
> because this line once sat directly under a block whose answer was NO, and read as answering that
> instead)*. On **SimVerb-3500** -- the same benchmark our verb zero was measured on -- a plain
> cosine over the raw norms reads **`+0.3107` `[+0.2822,+0.3390]`, null p95 `0.0304`**, covering
> **3,487 of 3,500 pairs (99.6%)**. It also reads **`+0.3109`** on SimLex's 222 verbs: *two
> independent verb benchmarks agreeing to three decimals.* On SimLex, verbs (`+0.3109`) sit only
> slightly below nouns (`+0.3469`) -- **our channel falls from weak to nothing across that same
> boundary, so the verb hole is OURS, not the world's.**
> ⚠️ **NOT A SUBTRACTION:** our channel covers 2,651 SimVerb pairs and the norms cover 3,487.
> **Quote it as "ours is absent where this one is present", never as a gain of `0.31`.**
>
> 🧠 **AND THE MOTOR DIMENSIONS ARE WHAT CARRY VERBS -- WHICH IS A BRAIN PREDICTION THAT COULD HAVE FAILED.**
> Lancaster splits into 6 PERCEPTUAL and 5 ACTION dimensions, the seam somatotopy predicts (Hauk,
> Johnsrude & Pulvermuller 2004: *kick* recruits leg motor cortex, *pick* hand). **ACTION minus
> PERCEPTUAL on verbs = `+0.0651` `[+0.0306,+0.1005]` -- CI-SEPARATED FROM ZERO**, paired, 3,487
> pairs. *At `n=222` it was `[-0.0989,+0.2031]` and said nothing; the fix was power, not caution.*
> 🔻 **A SINGLE dissociation, not a double one** -- on nouns the same test reads
> `-0.0150` `[-0.0951,+0.0635]`. **Do NOT retell as "motor for verbs, perceptual for nouns."**
>
> ➡️ **WHAT THIS CHANGES FOR WHOEVER BUILDS THIS:** the channel is worth wiring for verbs
> specifically, and if you weight or select dimensions, **the action dimensions are the load-bearing
> ones for verbs and that is measured, not assumed.** *It says nothing about our substrate reaching
> this ceiling -- `read()` still makes zero calls to the asset, which is this brief's other half.*
> ## 🚨 **AND THIS CHANGES WHAT THE BRIEF ASKS FOR: THE CHANNEL CANNOT GATE LINKS ALONE (08-23)**
> This brief says *"make the system get meaning from that channel **INSTEAD**"*. **As a replacement
> DECIDER it cannot work, and that is structural rather than a tuning problem.**
>
> 🔻 **AS SHIPPED IT CONTRIBUTES EXACTLY ZERO.** `GROUNDED_CAP = 0.45` sits below
> `lexical_similarity.SIMILARITY_LINK_THRESHOLD = 0.5`, so `grounded_similarity()` **can never reach
> the link threshold** -- by construction. On SimVerb-3500's `877` genuinely-similar verb pairs
> (top quartile of human rating): **`0` linked. Zero.**
>
> **AND UNCAPPING IS NOT THE FIX.** Unclamped, at that same `0.5`:
>
> | | genuinely SIMILAR (877) | genuinely DISSIMILAR (898) |
> |---|---|---|
> | linked | **`579` (66.0%)** | 🔻 **`335` (37.3%)** |
>
> **A third of genuinely-dissimilar verb pairs would link. The cap is not paranoia.**
>
> 📉 **AND NO THRESHOLD RESCUES IT** -- swept `0.30`→`0.95`, best hit-minus-false-alarm margin is
> **`+0.287`, occurring AT `0.50`, where the threshold already sits.** *The design put it in the right
> place.* Threshold-free: **AUC `0.7002`** -- real signal, well above chance, nowhere near separable.
>
> ➡️ **SO THE ASK MUST CHANGE: THIS CHANNEL IS A CONTRIBUTOR, NOT A DECIDER.** It carries real meaning
> and is the only channel we have that says anything about verbs at all -- but it cannot be what
> decides whether two words link. **Wire it in as a drop-in replacement and you get nothing (capped)
> or one link in three wrong (uncapped).** *The cap already encodes the right reading.*
> ⚠️ **NOT a licence to raise the cap** -- the `0.05` gap is what makes "contribute, do not decide"
> enforceable in code rather than hoped for in prose.
> **REVERIFY:** `.venv/Scripts/python.exe verification/test_the_channel_cannot_gate_links_alone.py`
>
> ### 🧭 **AND HERE IS WHAT NOT TO COMBINE IT WITH -- MEASURED 2026-08-23**
> The obvious second spoke is a taxonomy, and we have WordNet (supplied knowledge is admissible).
> **Pooled, WordNet looks decisive: margin `+0.543` vs sensorimotor's `+0.287`, false alarms `7.0%`
> vs `37.3%`. On that reading the answer is "just use WordNet".**
>
> 🔻 **IT IS READING ITS OWN SELECTION. SimVerb's PAIRS WERE CHOSEN BY WORDNET RELATION** -- the
> benchmark carries a relation column (`SYNONYMS` / `HYPER/HYPONYMS` / `COHYPONYMS` / `ANTONYMS` /
> `NONE`). Hold the relation FIXED and the edge collapses:
>
> | relation | n | SENSORIMOTOR | WORDNET |
> |---|---|---|---|
> | **`NONE`** (60% of the benchmark) | **2,084** | **`+0.286`** | `+0.154` |
> | `HYPER/HYPONYMS` | 797 | `+0.231` | **`+0.298`** |
> | `SYNONYMS` | 305 | **`+0.349`** | `+0.262` |
> | `COHYPONYMS` | 190 | `+0.178` | **`+0.239`** |
>
> ➡️ **ON THE PAIRS A TAXONOMY DOES NOT ALREADY LINK -- THE CASE A READER ACTUALLY FACES ON NEW TEXT
> -- THE SENSORIMOTOR CHANNEL IS NEARLY TWICE AS GOOD.** ⚠️ **NOT "WordNet is useless"**: it wins on
> hyper/hyponyms and cohyponyms, and a hub taking BOTH spokes is still worth testing. **What is
> refuted is the pooled number and the conclusion a builder would have drawn from it.**
> *A benchmark selected by a resource cannot fairly score that resource.*
> **REVERIFY:** `.venv/Scripts/python.exe verification/test_wordnet_advantage_is_selection_not_meaning.py`
>
> #### 🧪 **AND I TESTED THE BOTH-SPOKES HUB PROPERLY -- IT IS NOT ESTABLISHED (08-23)**
> The block above says *"a both-spokes hub is still worth testing"*. **Tested, on the `NONE` class
> only, because a pooled hub test inherits the same selection bias the pooled comparison had.**
>
> | arm (on `NONE`, n=2,084) | margin | AUC |
> |---|---|---|
> | sensorimotor alone | `+0.286` | `0.6996` |
> | WordNet alone | `+0.154` | `0.5981` |
> | **HUB (mean of the two)** | **`+0.321`** | **`0.7155`** |
> | HUB (max) | `+0.310` | `0.6999` |
> | HUB (both-must-agree) | `+0.272` | `0.6854` |
>
> 🔻 **THE POINT ESTIMATE SAYS THE HUB WINS AND THE INTERVAL SAYS IT IS NOT ESTABLISHED:**
> paired bootstrap, same resample both arms -- **hub minus sensorimotor `+0.0245`, 95% CI
> `[-0.0021, +0.0520]`. Includes zero.** *I wrote "HUB WINS" off the point estimate before running
> this; that is the third time in one day an estimate pointed one way and the interval did not.*
>
> ✅ **BUT THE NEGATIVE CONTROL SAYS WORDNET IS CONTRIBUTING SOMETHING REAL:** a hub built from
> sensorimotor **+ NOISE** instead of WordNet is **`-0.0507` `[-0.0891,-0.0105]`, CI-separated
> BELOW zero** -- adding noise actively hurts, adding WordNet does not. **So the second spoke carries
> real information and not enough of it to prove a gain at this n.**
> ➡️ **FOR THE BUILD: averaging the two spokes is the best combination rule of the three tried
> (mean > max > both-must-agree), and it is a reasonable default -- but do NOT bill it as a measured
> improvement over the sensorimotor channel alone. It is not.**
>
> ## 🔍 **ADDED 2026-08-23: STORAGE IS FINE; COMBINATION IS WHERE IT GOES -- YOUR DIAGNOSIS, NOW A NUMBER**
> This brief says the system *"stores word codes that carry no meaning by construction, then combines
> them in a way that destroys most of what little arrives."* **The first half is being fixed by the
> channel swap. I measured the second half** -- using the sensorimotor channel precisely *because* it
> demonstrably has signal to lose, so the answer is interpretable rather than confounded with "there
> was nothing there".
>
> **Our substrate stores 256 DENSE BIPOLAR values, every element exactly `-1` or `+1`** (inspected:
> 2 distinct values, 100% non-zero). Pushing the raw norms through that pipeline:
>
> | stage | rho | share of raw |
> |---|---|---|
> | raw 11 dims | `+0.3107` | 100% |
> | projected to 256 | `+0.3089` (sd `0.0029`, 8 seeds) | **99.4%** |
> | **+ bipolar `{-1,+1}` = OUR FORMAT** | `+0.2920` (sd `0.0087`) | **94.0%** |
>
> ✅ **SO THE REPRESENTATION IS NOT THE BOTTLENECK.** *Info-free control: the same pipeline on noise
> reads `-0.0112`, so 94% is signal surviving, not projection preserving something generic.*
>
> 🔻 **BUT BUNDLING IS. Superposing the meaning code with k other vectors, same format:**
>
> | k distractors | 0 | 1 | **2** | 4 | **8** | 16 |
> |---|---|---|---|---|---|---|
> | rho | `+0.2778` | `+0.2299` | **`+0.1468`** | `+0.1376` | **`+0.0808`** | `+0.0483` |
> | share of raw | 89% | 74% | **47%** | 44% | **26%** | 16% |
>
> 🚨 **TWO distractors HALVE it. Eight leave a quarter.** At `k=8` it is `+0.0808` against a null of
> `0.0338` -- still present, barely, and nothing you could build a capability on.
>
> ➡️ **WHAT THIS MEANS FOR THE BUILD: wiring the adapter is necessary and NOT sufficient. Do not
> superpose the meaning vector with many distractors** -- keep it in a slot addressed on its own, or
> use a binding scheme that survives superposition. **The bottleneck is the combination step, and it
> is now priced.** *Compare `k` against `k=0`, not against the stage-2 row: `k=0` uses one projection
> seed, stage 2 is a mean over 8.*
> **REVERIFY:** `.venv/Scripts/python.exe verification/test_does_our_format_survive_the_meaning_signal.py`

> ## 🚫 **ADDED 2026-08-23: SPARSITY DOES NOT RESCUE IT -- DO NOT SPEND A WEEK ON A SPARSER CODE**
> The obvious next move after the bundling result is the brain's own answer: **cortex is SPARSE**, a
> few percent active, and sparse patterns interfere far less under superposition because they mostly
> do not touch the same units. Our code is the opposite extreme -- **100% non-zero**. So: sweep
> density 1%->100% and re-measure bundling at `k=8`. *(Swept, not adopted -- this repo's pinned
> biological `0.2%` band was once the WORST point in its own sweep.)*
>
> | density | 1% | 2% | 5% | 10% | 25% | 50% | **100% (ours)** |
> |---|---|---|---|---|---|---|---|
> | k=0 | `+0.1856` | `+0.2218` | `+0.2567` | `+0.2882` | `+0.3049` | `+0.3022` | **`+0.2893`** |
> | **k=8** | `+0.0817` | **`+0.0912`** | `+0.0840` | `+0.0788` | `+0.0682` | `+0.0752` | **`+0.0764`** |
> | retained | **44%** | 41% | 33% | 27% | 22% | 25% | **26%** |
>
> 🔻 **JUDGED ON RETENTION, SPARSITY WINS (44% vs 26%). JUDGED ON THE SIGNAL YOU ACTUALLY END UP
> WITH, IT IS A WASH:** best sparse `+0.0912` vs dense `+0.0764`, a difference of `+0.0147`.
> **Every density in the sweep collapses to roughly `+0.08`.** The sparse code retains a larger share
> of a SMALLER signal -- its `k=0` is `+0.1856` against dense's `+0.2893`. **A ratio whose denominator
> you also changed is not a result.**
>
> 🧠 **AND THE BRAIN READING IS THE USEFUL PART OF THIS NEGATIVE.** Sparsity is not what buys
> cortex its interference resistance ON ITS OWN -- **cortex does not superpose a word's meaning into
> one shared vector at all.** It keeps separate populations and addresses them. So the half of the
> brain's answer we tried to import in isolation was never the load-bearing half.
> ➡️ **THEREFORE: not a sparser vector. Do not spend the week.**
> **REVERIFY:** `.venv/Scripts/python.exe verification/test_does_sparsity_fix_the_bundling_loss.py`
>
> ## ✏️ **CORRECTION 2026-08-23, SAME DAY: I SAID "USE AN ADDRESSED SLOT" BEFORE MEASURING IT**
> The line above originally ended *"the fix is an ADDRESSED SLOT, not a sparser vector"*. **The
> second half stands; the first half was an assertion I had not tested, written into a brief a
> solver would act on.** So I tested it: bind the meaning code to a key, superpose with k
> key-value distractors, unbind to recover.
>
> | k | plain bundle | ADDRESSED | recover w/ right key | w/ WRONG key |
> |---|---|---|---|---|
> | 2 | `+0.1860` | `+0.1745` | `+0.5775` | `-0.0012` |
> | **8** | **`+0.0670`** | **`+0.0536`** | `+0.3336` | `-0.0037` |
> | 32 | `+0.0155` | `+0.0004` | `+0.1767` | `-0.0000` |
>
> ✅ **ADDRESSING WORKS AS ADDRESSING:** the right key recovers the stored item at cos `+0.3336`,
> the wrong key at `-0.0037`. **You can get back WHICH item you stored** -- the slot is real.
> 🔻 **BUT IT BUYS NO SIGNAL: `+0.0536` addressed vs `+0.0670` plain at k=8, and it is WORSE at
> k=32.** Binding **PERMUTES** the interference, it does not remove it -- unbinding returns the item
> plus a noise term of the same magnitude the plain bundle already had. **Capacity is set by the
> dimension and the NUMBER OF ITEMS, not by whether you bound them to keys.**
>
> ➡️ **THE RULE THAT ACTUALLY SURVIVES, AND IT IS BLUNTER THAN WHAT I FIRST WROTE: KEEP THE
> NUMBER OF ITEMS IN ONE SUPERPOSITION SMALL, or give meaning ITS OWN STORE rather than a key into a
> shared one.** *A key does not protect you from the other occupants.*
> ⚠️ **OUR-INVENTION-UNDER-TEST, not brain-derived:** no recording shows neurons computing an
> algebraic binding over two full-rank vector codes; the binding problem is open. What the brain
> licenses is only that meaning stays *addressable* rather than stirred into one pot.
> **REVERIFY:** `.venv/Scripts/python.exe verification/test_does_an_addressed_slot_survive_bundling.py`

> ## 🔻🔻 **STOP -- BEFORE THE SEGREGATION BLOCK BELOW: TWO LANDED EXPERIMENTS ALREADY REFUTED "REPLACE THE FLAT BAG"**
> **I found these AFTER writing the segregation result, by checking how the reader actually consumes
> the context vector. They are prior work and they point the other way.**
>
> | cell | verdict | what it measured |
> |---|---|---|
> | `exp_structured_code_vs_flat_bag_c3_v1` | 🔻 **`STRUCTURE_HURTS`** | *"STRUCTURED is BELOW BASE by `-0.0113` (CI `[-0.0195,-0.0030]`)"* -- **CI-separated BELOW** |
> | `exp_perirhinal_conjunctive_readout_c3_v1` | 🔻 **`CONJUNCTIVE_HURTS`** | *"no conjunctive arm beat the flat bag; `A2_CONJ_PAIR`, `A3_CONJ_HYBRID` are CI-separated BELOW it"* |
>
> **AND `hdlab/perirhinal_conjunctive.py` ALREADY EXISTS** -- a default-off drop-in replacement for
> `context_vector_masked`, properly labelled for brain fidelity. **Its docstring already states my
> finding, and states it better:** *"the live read-out profile is a BARE FLAT SUM ... verified by
> runtime reconstruction, bit-exact, order-invariant. Its similarity metric is therefore LINEAR in
> how many context words two profiles share."*
>
> ## ⚖️ **SO WHAT SURVIVES OF MY SEGREGATION RESULT, AND WHAT DOES NOT**
> ✅ **SURVIVES -- it is a property of REPRESENTATIONS and it is measured:** at equal budget,
> superposing k items destroys per-item similarity, and at the reader's real `k=6` about `62%` of it
> goes. That is true and reproducible.
> 🔻 **DOES NOT SURVIVE -- "so replace the flat bag":** that is the exact move both cells tested and
> **both found it CI-separated WORSE on a real readout task.** *My measurement asks whether INDIVIDUAL
> WORD MEANING survives the representation. Task c3 may not need individual word meaning -- if
> similarity-by-shared-context-words is what the task wants, then blending is the feature, not the
> bug.* **A property of a representation is not a licence to change it.**
>
> ➡️ **THE HONEST STATE: I have a measured cost with no demonstrated benefit, against two landed
> results showing the obvious remedy backfires.** Anyone building here must reconcile those, not pick
> the one they like.
> 🔑 **AND A SEPARATE ALARM FROM THE SAME RECORD, WORTH MORE THAN EITHER: `strongest floor is
> A5_STRINGCTRL at 0.0870, live base 0.0480`. A STRING-MATCHING CONTROL BEATS THE LIVE SYSTEM NEARLY
> 2:1 ON THAT TASK.** *That is not about bundling at all, and it outranks this whole thread.*

> ## 🧠✅ **AND HERE IS WHAT DOES WORK -- SEGREGATION, MEASURED AT EQUAL BUDGET (08-23)**
> Three blocks above establish that combining destroys meaning and that **sparsity does not rescue
> it, nor does an addressed slot.** Each of those tried to make SUPERPOSITION survive. **Cortex's
> answer is not to superpose at all** -- distinct attributes live in distinct populations, addressed
> anatomically.
>
> ⚠️ **THE TAUTOLOGY TRAP, AND WHY THIS TEST FIXES THE BUDGET.** *Of course* separate storage has no
> interference -- there is nothing to interfere with. So both schemes get the **SAME total `D=256`**:
> superposition spends it on resolution and pays in crosstalk; segregation gives each item `D/k` and
> pays in dimensionality. **Either could win.**
>
> | k | SUPERPOSED (all in 256) | SEGREGATED (each in 256/k) | segregated slot |
> |---|---|---|---|
> | 1 | `+0.2914` | `+0.2983` | 256 dims *(identical by construction -- the harness check)* |
> | 2 | `+0.2296` | **`+0.2882`** | 128 dims |
> | 4 | `+0.1397` | **`+0.2565`** | 64 dims |
> | 8 | `+0.0929` | **`+0.2263`** | 32 dims |
> | **16** | `+0.0479` | 🧠 **`+0.1949`** | **16 dims** |
>
> 🔑 **SEGREGATION WINS AT EVERY k, AND THE MARGIN GROWS WITH k. At k=16 a SIXTEEN-dimensional
> isolated slot beats a 256-dimensional superposed code by 4x** -- a representation 16x smaller,
> winning decisively. **ISOLATION IS WORTH FAR MORE THAN RESOLUTION**, which is the arrangement
> cortex actually uses.
>
> ➡️ **FOR THE BUILD, THIS IS THE ANSWER TO THE BUNDLING PROBLEM: give meaning its own narrow slot
> rather than a share of a wide one.** The earlier blocks say what does NOT work; this says what
> does, and it is cheap -- narrow slots, not bigger vectors.
> ⚠️ **ENGINEERING, NOT BIOLOGY:** anatomical segregation of attributes IS pinned in cortex; the
> ALGEBRA either scheme uses here is **our-invention-under-test** (VSA binding is unpinned). This
> compares two of OUR options against a brain-motivated question.
> #### 📐 **AND THE DESIGN NUMBER: HOW NARROW CAN A SLOT GET?** Swept to `k=256` looking for the
> crossover where superposition wins back. **THERE ISN'T ONE -- segregation leads at every `k`.**
> What changes is whether EITHER is useful:
>
> | k | slot | SUPERPOSED | SEGREGATED | |
> |---|---|---|---|---|
> | 32 | **8 dims** | `-0.0011` | **`+0.1537`** | ✅ **last USEFUL width -- over half the full-resolution `+0.2983`** |
> | 64 | 4 dims | `-0.0019` | `+0.0752` | *both weak* |
> | 256 | **1 dim** | `+0.0139` | `+0.0387` | *info-free is `+0.0233`* -- **a ONE-dim slot still beats a 256-dim superposed code, but both are near-dead** |
>
> 🚨 **SUPERPOSITION IS COMPLETELY DESTROYED BY `k=32` -- it reads ZERO.** ⚠️ **BELOW ~8 DIMS PER
> SLOT SEGREGATION WINS A RACE BOTH SCHEMES ARE LOSING.** *Do not read "segregation wins at k=256" as
> a licence for 1-dim slots.* ➡️ **~8 dims per slot is the practical floor; that is the number to
> build to.**
>
> *Controls: k=1 agreement (harness favours neither), info-free arm `+0.0233` at the narrowest slot.*
> #### ⚠️ **SCOPE, AND IT CHANGES THE BUILD INSTRUCTION: THIS IS ATTRIBUTE SEGREGATION, NOT PER-ITEM**
> **The segregated arm assumes you KNOW WHICH SLOT TO READ.** Superposition hands you everything at
> once with no addressing; segregation needs an address. **In cortex that is free because slots are
> ANATOMICAL AND TYPED -- the visual area IS the visual area, no search.** That freeness holds only
> when slots are typed by ATTRIBUTE. At `D=256`:
>
> | slots typed by... | k | dims/slot | verdict |
> |---|---|---|---|
> | **ATTRIBUTE** (cortex-style, addressing structural) | 5 / 11 / 20 / **32** | 51 / 23 / 12 / **8** | ✅ **all at or above the floor** |
> | PER-ITEM (needs an index) | 100 | `2.56` | 🔻 far below, **and addressing is not free** |
> | PER-ITEM | 1,000 | `0.26` | 🔻 hopeless |
>
> ➡️ **SO THE BUILD INSTRUCTION IS NOT "GIVE EVERY WORD ITS OWN SLOT" -- that is impossible at 256
> dims and I nearly wrote it. IT IS: KEEP MEANING IN ITS OWN ATTRIBUTE-TYPED SLOT, SEPARATE FROM
> WHATEVER ELSE THE READING LOOP IS ACCUMULATING.** *Up to ~32 attribute streams fit above the
> practical floor, which is far more than we have. The constraint is not tight -- we are simply not
> using it.*
>
> #### 🎯 **AND HERE IS WHAT IT COSTS US RIGHT NOW -- THE `k` MEASURED ON THE LIVE READER**
> Everything above is a sweep over abstract `k`. **`context_vector` is the reader's actual bundler
> and its own docstring says what it does: a "bag-of-content-words bipolar bundle",
> `sign(sum of its content words' vectors)`. So `k` = CONTENT WORDS PER SENTENCE.**
>
> **Measured on 3,998 real corpus sentences: mean `5.6`, median `6`, p75 `7`.** Re-running the
> comparison at exactly those `k`:
>
> | k | slot | SUPERPOSED | SEGREGATED | superposed retains |
> |---|---|---|---|---|
> | 1 | 256d | `+0.2914` | `+0.2983` | 100% *(baseline)* |
> | 5 | 51d | `+0.1127` | `+0.2625` | `38.7%` |
> | **6 (median sentence)** | **42d** | **`+0.1095`** | **`+0.2343`** | 🔻 **`37.6%`** |
> | 7 | 36d | `+0.0916` | `+0.2512` | `31.4%` |
>
> 🚨 **AT THE `k` THE READER ACTUALLY OPERATES AT, THE BAG-OF-CONTENT-WORDS BUNDLE THROWS AWAY ABOUT
> `62%` OF THE MEANING SIGNAL** -- and **a 42-dimensional isolated slot would carry MORE than the
> full 256 shared** (`+0.2343` vs `+0.1095`, better than double).
>
> ➡️ **THIS IS NO LONGER A SWEEP, IT IS A COST THE RUNNING SYSTEM IS PAYING PER SENTENCE.** *And it
> compounds with the channel problem: the reader is losing ~62% of a signal it was not getting in the
> first place.*
> ⚠️ *Separate from the known `sign()` issue -- that docstring already records `+0.0245`-`+0.0267`
> for dropping the terminal `sign`. **This is the BUNDLING, not the normalisation.*** Both are live.
>
> **REVERIFY:** `.venv/Scripts/python.exe verification/test_segregated_beats_superposed_at_equal_budget.py`

> **REVERIFY (tracked, runs in ~40s):**
> `.venv/Scripts/python.exe verification/test_sensorimotor_covers_the_verb_hole.py`
> Write-up: `notes/THE_SENSORIMOTOR_CHANNEL_COVERS_OUR_VERB_HOLE_2026-08-23.md`.

# PROBLEM: THE READER'S MEANING CHANNEL IS THE WRONG MODALITY

**slug:** `reader_meaning_channel` · **opened:** 2026-08-22 by the strategy session
**status:** OPEN · **this is the highest-value problem in the project**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

Our system works out what a word means by noticing which other words show up near it. That is the
only channel it has. **We can now prove that channel cannot carry the answer** -- not that it is
weak, that it tops out, and we have hit the top.

Meanwhile a set of human sensory ratings already sitting on our disk -- how much a word involves
seeing, hearing, touching, moving -- predicts what words mean **two to seven times better**, and
covers 100% of the vocabulary we test on. It is not connected to anything that runs.

**The job: make the system get meaning from that channel instead, at reading time, and prove the
gain survives on text it has never seen.**

---

## 2. WHY THIS ONE

**It is upstream of nearly every negative in the archive.** The system stores word codes that carry
no meaning by construction, then combines them in a way that destroys most of what little arrives.
Every downstream repair has measured null -- and this explains why: *there was nothing there to
repair.*

**And it is the clearest case of the project's own pattern:** the fix is already on disk, unwired,
and was filed CLOSED.

---

## 3. MEASURED vs INFERRED

### MEASURED -- these have controls and you may build on them

| what | number | scope you must carry with it |
|---|---|---|
| **sensorimotor cosine predicts HUMAN similarity** | **rho `0.3171`, CI `[0.2605, 0.3707]`** | 988 SimLex-999 pairs; **UNFITTED** -- a plain cosine, no model |
| raw co-occurrence predicts the same | **rho `0.0446`, CI `[-0.0177, 0.1077]`** | **CI INCLUDES ZERO** -- same pairs |
| the paired difference | **`+0.2348`, CI `[+0.1605, +0.3155]`** | **CI-SEPARATED**, paired bootstrap |
| sensorimotor on pick-the-right-one-of-50 | **`0.6413`** (345/538) | fitted, **word-disjoint CV**, one corpus |
| co-occurrence on the same task | **`0.3067`** (165/538) | same folds, same model |
| **co-occurrence CEILING** | **`0.3104`** | **two completely different feature sets converge**: 8 scalars + tree ensemble, and the full 1,024-dim profile + linear model |
| controls on the sensorimotor arm | candidate-only **`0.0985`**, shuffled-query **`0.0595`** | **the PAIRING carries it**; removing candidate-only features IMPROVED the score |
| coverage | **100%** of the 1,024 test words | so this is NOT coverage-limited |

**The brain side, and it is why this is not just a benchmark trick:** form (spelling) and meaning
are **separate systems** -- a spelling area behind the left ear, and meaning distributed across the
senses with a hub at the front of the temporal lobe binding them. **We have been using a spelling
code as a meaning code.** That is structural, not a tuning problem.

### INFERRED -- overturning any of this is a RESULT, not a failure

- *That a read-time mechanism can capture what the fitted ceiling diagnostic sees.* **The 0.6413 is
  a CEILING, fitted on the gold. It says THE INFORMATION IS THERE. It does not give a mechanism, and
  building one is exactly this problem.**
- 🔻 **CORRECTED 2026-08-22: I first wrote "coverage at scale is UNMEASURED". IT IS MEASURED, and
  the number is in `notes/LONG_TERM_PLAN.md` Phase 1, which names this exact problem as the current
  bottleneck.** *The asset **covers `60.4%` of RUNNING TEXT but only `10.3%` of DISTINCT WORDS, and
  coverage falls to `4%` beyond rank 64,000.*** ➡️ **So coverage is not an unknown risk -- it is a
  KNOWN, QUANTIFIED constraint with a named work item beside it: widen the grounded core by
  **`+14,704` words** in frequency order to reach ~90% token coverage (`+40,160` -> 95%; `+103,558`
  -> 98%). **The ~15k option is the knee of the curve.***
  ⚠️ **AND THE PLAN'S OWN NON-NEGOTIABLE ON THAT WIDENING, WHICH IS THE TRAP: re-score the widened
  set ON ITS OWN NEW WORDS.** *The existing evidence that norms generalise is about rare words that
  ALREADY HAVE norms. Until new words are scored, the coverage number is arithmetic, not
  capability.*
- 🔑 **ADDED 2026-08-22 -- BEFORE NORMING A SINGLE NEW WORD, READ THIS: `+13.2` POINTS OF THAT
  COVERAGE ARE ALREADY ON DISK AND THE LOOKUP CANNOT REACH THEM.** `hdlab/grounded_similarity.py:165`
  is `_table().get(word.lower())` -- **a raw string match with no morphology**, so the asset holds
  `country` and reads past `countries`, holds `release` and misses `released`. *Corpus-scale, with
  the landed cell's `0.6035`/`0.1027` reproduced exactly first as the control:* **token coverage
  `0.6035` -> `0.7350` under the repo's own `normalize_lemma`; type coverage `0.1027` -> `0.1633`.**
  ➡️ **The gap from `60.35%` to the `90%` target is `29.65` points and this is `13.15` of them -- 44%
  of the way, at ZERO data cost. So `+14,704` counts inflected forms of ALREADY-NORMED words as words
  needing new norms.** ⚠️ *Two limits, both measured not assumed: ~4% of the recoveries are wrong
  (`using -> us`, `angeles -> angel`, `notes -> not`), and irregulars (`women`, `feet`) are missed by
  both methods so the ceiling is HIGHER than `0.7350`.* 🚫 **AND THE TRAP DIRECTLY ABOVE APPLIES TO
  IT UNCHANGED -- this is COVERAGE, not CAPABILITY. No task was run. `grounded_similarity.py` was
  deliberately NOT changed.** *The bar: a TASK score, with an information-free twin that lemmatises
  to a RANDOM covered word required to LOSE.*
  📎 `notes/THE_NORMS_LOOKUP_DOES_NOT_LEMMATISE_AND_THAT_IS_13_POINTS_OF_FREE_COVERAGE_2026-08-22.md`
- *That replacing rather than blending is right.* Argued from the brain and supported by one
  HARD_FAIL (below) -- not proven.

### ⚖️ THE HONEST DEFLATION, WHICH MUST TRAVEL WITH ANY WRITE-UP
**Perceptual norms predicting semantic similarity is a KNOWN result in the literature. We have not
discovered embodiment.** What is new *for this project* is narrow and worth stating plainly: our
substrate has been working in a modality that measurably cannot carry the target, while an
admissible, already-on-disk, 100%-covering asset carries it far better -- and that asset was filed
as CLOSED.

---

## 4. ALREADY TRIED -- DO NOT RE-RUN THESE

- **Blending form into one combined query: `HARD_FAIL`.**
  `exp_substrate_concept_encoder_v2_vwfa_late_combine_2spoke` -- combined `recall@5 0.2000` vs
  `max(form 0.2533, semantic 0.1667)`: *"composition HURTS relative to best single spoke."*
  **Note the form spoke also BEAT the semantic spoke.** ⚠️ smoke, N=100, 3 seeds, `n_dim=2048`.
- **The same 11 sensorimotor dimensions were filed CLOSED** at `0.6039` against a `0.6791` bar --
  on a DIFFERENT instrument (pairwise similarity). On the better-posed pick-one-of-50 problem the
  same eleven numbers reach `0.6413`. **This is "do not generalise a narrow failure to impossible"
  paying out; do not re-close it on the old instrument.**
- **Divisive normalisation over a population pool: ANALYTICALLY IMPOSSIBLE.** The denominator is a
  scalar for the whole representation and cosine is scalar-invariant. `ORGAN_MAP` §3 says *"do not
  re-propose"* with a measured null. **Do not.**
- **Rank-1 common-mode removal / anisotropy: CLOSED HARD** (`DO NOT REDO 27`). The operation fully
  worked -- mean pairwise cosine `0.1427 -> -0.0004` -- for accuracy `0.6980 -> 0.6985`, and a
  RANDOM rank-1 direction gives the same `+0.0005`.
- **Second-order cosine ("do these two words keep the same company")** -- our semantic route's own
  operation -- **is WORSE than the raw count it is built from** on one instrument (`0.1506` vs
  `0.1859`). ⚠️ *A controlled 4-corpus re-run REVERSED this: second-order BEAT raw in 4 of 4. Treat
  the question as OPEN, and note the earlier claim is retracted.*

**Prior-work counts already run (2026-08-22):** `query "grounding"` 711 cells · `"encoder"` and
`"sensorimotor"` not yet queried by this brief -- **run them.**

---

## 5. VERIFY BEFORE YOU START -- THE DISK OUTRANKS THIS BRIEF

*Written because this project retracted, un-retracted and re-retracted one recommendation inside
three hours on the day this brief was written.*

```bash
python tools/before_you_start.py "wire sensorimotor norms as the meaning channel at read time"
python tools/experiment_index.py query "sensorimotor"
python tools/experiment_index.py query "norms"
python tools/organ_map_cite.py <organ you intend to touch>
python tools/cite_check.py 0.6413        # confirm the caveats above are still the source's caveats
```
**If any of these disagree with section 3, the disk wins -- say so in `SOLVED.md`.**

---

## 6. THE BAR

**Turn the ceiling diagnostic into a MECHANISM.**

- **An UNFITTED read-time mechanism** -- no model trained on the gold -- that uses the sensorimotor
  channel to choose a word's meaning **on the live reading path**.
- 🚨 **AND IT MUST NOT BE A SOLE-CHANNEL DECIDER. MEASURED 2026-08-23, see the block at the top:**
  this channel alone links `66%` of genuinely-similar verb pairs **and `37%` of genuinely-dissimilar
  ones**, at the best threshold in a `0.30`-`0.95` sweep. **A mechanism that decides on this channel
  alone will get roughly one link in three wrong, and that is not a tuning problem** -- AUC is
  `0.7002`, real but not separable. **Combine it; do not substitute it.** *This narrows the bar; it
  does not lower it.*
- **Scored on held-out text**, CI-separated over **the strongest floor actually run**, gated on the
  **floor's upper bound** (floor + its own half-width), with the floor recomputed on this
  population and this representation.
- **The three controls that bound the existing result must be rebuilt and must still bind:**
  candidate-only (never sees the query), shuffled-query (pairing destroyed, marginals kept), and an
  **information-free version of your own winning arm** which must LOSE.
- **Report coverage.** What fraction of the words encountered have norms? That number is the
  finding if it is low.

### HOW WE WOULD KNOW IT FAILED -- pre-register which of these fired
- **(a)** The mechanism does not clear the floor's upper bound -> a real negative; go to the
  brain-fidelity drill and ask FIRST whether it could have succeeded.
- **(b)** It clears, but the information-free twin also clears -> artifact, not mechanism.
- **(c)** It clears on covered words and coverage is too low to matter -> **say so in the headline**;
  a gain on 30% of tokens is a 30% gain.
- **(d)** It only works FITTED -> you have re-measured the ceiling, not built a mechanism.

---

## 7. FILES AND ENTRY POINTS

- **The live reading path:** `hdlab/reading_grounding_loop.py`, `hdlab/substrate.py`
- **The meaning read-out to replace or bypass:** the accumulated-context-profile route
- **The form channel, already wired ADDITIVELY:** `form_identity_vector` -- **do not blend it into
  the meaning query**; it is a recognition index and its meaning path is barred in its docstring
- **The assets:** the sensorimotor/Lancaster norms and the learned encoder, both on disk, both
  unwired -- locate them via the registry rather than trusting this line
- **🚫 YOU DO NOT WRITE TO `hdlab/` -- THE LIVE SUBSTRATE (owner ruling, board Q111, 2026-08-22).** *Prove the mechanism in `experiments/` and `verification/`, then state in `SOLVED.md` exactly what would have to change in `hdlab/` and why. **The strategy session re-verifies and lands it, and is the sole writer there** -- two writers on one live file already destroyed a full day's audit here, silently.*

**🚫 DO NOT TOUCH:** `preregs/**`, any `arm_key*` file, `notes/STATUS.md`, the build plan, or
  another problem's folder. **The `== "UNK"` guard in the animacy path is a deliberate hand-off.**

---

## 8. DO NOT QUOTE / DO NOT REDO

- 🚫 **Never place `0.6413` beside a live-substrate number without saying it is a FITTED CEILING
  DIAGNOSTIC on word-disjoint CV.**
- 🚫 **`0.3104` is one corpus, 538 target words, no CI.** The CONVERGENCE of two feature sets is the
  finding; the exact tie may be coincidence (a one-hit difference is 0.0019).
- 🚫 **Do not re-propose divisive normalisation or rank-1 common-mode removal.** Both closed, one
  analytically.
- 🚫 **Do not re-close the sensorimotor route on the pairwise-similarity instrument.** That is the
  narrow failure this result already escaped.
- ⚠️ **Supplied knowledge is ADMISSIBLE** (owner ruling) but it is SUPPLIED, not learned. Say which.
- ⚠️ **No external LLM at inference. Ever.** That invariant is not negotiable and not in scope here.
