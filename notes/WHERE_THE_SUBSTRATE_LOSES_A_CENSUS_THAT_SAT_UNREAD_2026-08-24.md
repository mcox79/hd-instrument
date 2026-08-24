# Where the substrate loses: a full pipeline census that sat unread for eleven days

**Filed 2026-08-24 by the strategy session.** Source: `data/exp_e2e_trace_v1/metrics.json`, run
**2026-08-13**. Found by enumerating full runs that landed with no `verdict` field — this cell is
one of twelve (`verification/test_no_full_run_lands_without_a_verdict.py`).

> ## ✅ **ITS MISSING VERDICT IS LEGITIMATE, AND THAT IS THE FIRST FINDING.**
> The cell's own `QUALITY_CLAIM` reads: *"NONE. This cell counts attrition; it scores nothing."*
> **So a verdict-less full run is not automatically a lost result — some cells are deliberately
> scoreless censuses.** The defect is not that it lacked a verdict; it is that **nothing surfaced
> it**, so eleven days of decisions were taken without it. *Do not "fix" this cell by giving it a
> verdict it should not have.*

## 1. THE HEADLINE: 34,169 SENTENCES IN, 386 FACTS OUT

| stage | enter | leave | dominant loss |
|---|---|---|---|
| 1 input sentences | 34,169 | 33,839 | 330 had no content lemma |
| 1b tokens -> content lemmas | 623,522 | 338,506 | 270,779 stopword / len<=2 / non-alpha |
| 2 gap gate | 338,506 | 83,923 | 123,346 seed-known (anchor only, never a target) |
| 2b encoding | 83,923 | 83,732 | **191 all-zero context vector, SILENT** |
| 3 candidate pool | 89,676 | 89,675 | 1 empty anchor field, SILENT |
| **4 selection threshold** | 89,676 | 32,456 | **57,220 below `PBV_INFORMATIVE_MIN = 0.30`** |
| 5 consolidation eligibility | 1,373,320 | 52,186 | 1,313,576 under `MIN_CONFIRM = 4` |
| 5b schema coherence | 52,186 | 25,325 | 26,861 |
| **6 admission gate (PBV)** | **25,325** | **386** | **21,207 `HYPOTHESIS_BELOW_COMMIT_STRENGTH`** |
| 7 store write | 386 | 386 | 0 |

⚠️ **STAGE 5 IS ITEM-PASSES, NOT DISTINCT ITEMS** — the cell says so itself; one library item is
counted once per consolidation pass it is pending for. **Do not quote 1,373,320 as a count of
things.** Distinct-item outcomes live in `stage_detail.5_consolidation.item_terminal_fate`.

➡️ **THE LATE GATE IS WHERE IT DIES: admission rejects `24,939` of `25,325` — `98.5%` — and `21,207`
of those are one reason, `HYPOTHESIS_BELOW_COMMIT_STRENGTH`.** Everything upstream of stage 6 is
ordinary filtering (stopwords, known words, low-information encounters). **Stage 6 is not filtering;
it is the system declining to commit to almost everything it managed to form a hypothesis about.**

## 2. WHY THE READ-OUT MISSES: THE ANSWER IS USUALLY NOT ON THE MENU

`WHERE_THE_CORRECT_ANSWER_IS_LOST`, over **1,353** key subjects:

| bucket | n | share |
|---|---|---|
| **ABSENT** (correct answer not in the pool at all) | **1,069** | **79.0%** |
| PRESENT_NOT_ARGMAX (there, but not picked) | 233 | 17.2% |
| BANKED_OTHER | 39 | 2.9% |
| ARGMAX_NOT_BANKED | 12 | 0.9% |

**And when it IS available (n=253): median rank `20`, mean `57.5`, p90 `180.2`, max `461`.**
**Only `9` of `1,353` subjects ever had the correct answer proposed as a hypothesis at all.**

➡️ **This is a SUPPLY failure far more than a RANKING failure.** Four fifths of the time no
re-ranking, no better comparator and no smarter selection rule could have helped, because the right
answer was never a candidate. *That reframes a large amount of read-out work as optimising the
wrong stage.*

⚠️ **THE CELL'S OWN LIMIT, AND IT IS LOAD-BEARING — DO NOT DROP IT:** *"The known-answer key is the
v5 definitional extraction, itself ~64% correct, so the ABSENT / PRESENT_NOT_ARGMAX split is
structural: 'the key's object was not on the menu' does not mean 'no correct answer was on the
menu'."* **So `79%` is the share where THE KEY'S answer was absent, not the share where ANY correct
answer was absent. The direction is solid; the exact figure is not a clean measurement of the
substrate.**

## 3. SILENT DROPS, NAMED WITH LINE NUMBERS

The cell enumerates code sites that discard work with **no counter, no log line, no refusal row**:

- **`reading_grounding_loop.py:1076` `process_sentence`** — all-zero context vector -> `continue`.
  **191 occurrences dropped silently.**
- **`reading_grounding_loop.py:657` `canonicalize_fast`** — empty anchor field returns
  `(target, 0.0)`, which the caller reads as "uninformative encounter". **AN EMPTY POOL AND A
  BELOW-THRESHOLD ARGMAX ARE THE SAME RETURN VALUE.** *That is a genuine design defect: two
  conditions needing opposite responses are indistinguishable to every caller.* Count 1 here, but
  the count is not the point — the ambiguity is.
- `canonicalize_fast:663` (no scannable anchor) and `:668` (zero-norm query profile) — same
  indistinguishable self-return, 0 occurrences in this run.

---

# SECOND OF THE ELEVEN: CONSOLIDATION FIRES, AND REMOVING IT CHANGES NOTHING

Source: `data/exp_substrate_end_to_end_readout_v1/metrics.json`, run **2026-08-19**, 18 units,
3 seeds x 6 arms. Also verdict-less, also unread.

**This cell retires its own headline, for the right reason:** *"The best achievable score on this
task is 0.0300 (COOC_COS_floor, carried as an arm here) against the substrate's 0.0150, so fixing
every defect wins a tie with a floor. The hit@1 is NOT a capability claim. What is being measured is
the ABLATION CONTRASTS, which are within-cell paired differences and do not need the task to have
headroom."* ✅ **Its interpretability gate passed here** (`grounding_fired_in_control: true`) —
the note warns that *"every unit of the v2 run recorded 0"*, so v2 was uninterpretable and this run
is not.

## ITS PRE-REGISTERED QUESTION, ANSWERED: NO

> *"With consolidation actually firing, does the read-out change at all? The deciding contrast is
> `ablate=['consolidation']` against the control at the same seed."*

**Held-out hit@1, all three seeds, EPISODIC / SEMANTIC / COOC floor — the consolidation-ablated arm
is BIT-IDENTICAL to the control, including the floor** (so it is the same items and the same pool,
i.e. a clean paired comparison). Same for `definitions`, `foraging`, `gap_detector`.

## ⚠️ AN EXACTLY-ZERO NULL IS A REACHABILITY FAILURE UNTIL PROVED OTHERWISE — SO I CHECKED, AND IT SPLITS 2/2

CLAUDE.md: *"a zero-WIDTH CI is a reachability failure, not a null."* Bit-identical output across
four organs and three seeds is exactly that fingerprint. The internal counters decide it (seed
20260819):

| arm | n_episodes | n_provenance | n_refused | pool | reached? |
|---|---|---|---|---|---|
| (control) | 5346 | 38 | 199 | 2114 | — |
| **consolidation** | 5346 | **0** | **0** | 2114 | **YES** |
| **definitions** | 5346 | **31** | **209** | 2114 | **YES** |
| episodic | **0** | 38 | 199 | **2161** | YES, but pool CHANGED |
| foraging | 5346 | 38 | 199 | 2114 | **NOT ESTABLISHED** |
| gap_detector | 5346 | 38 | 199 | 2114 | **NOT ESTABLISHED** |

✅ **CONSOLIDATION AND DEFINITIONS ARE REAL NULLS.** Ablating consolidation drives provenance
`38 -> 0` and refusals `199 -> 0`, so it demonstrably did something — **and the read-out did not
move by a single item.** Definitions likewise (`38 -> 31`, `199 -> 209`). *These organs run, do
measurable internal work, and contribute nothing to this read-out.*

🚫 **FORAGING AND GAP_DETECTOR ARE NOT NULLS AND MUST NOT BE REPORTED AS SUCH.** Every counter is
identical to the control; only `read_seconds` differs (`13.8` vs `16.2` / `11.0`). **On this
evidence I cannot tell "the organ does nothing" from "the switch did not disable it".** *The
episodic arm proves the ablation MACHINERY works — that is the positive control — but it does not
prove these two switches work.*

⚠️ **AND THE EPISODIC ARM IS NOT A CLEAN CONTRAST EITHER:** `pool_size` moves `2114 -> 2161` and the
COOC floor moves with it, so the item population changed. Part of its EPISODIC drop to `0.0000` is
also near-tautological — the route being scored was removed.

## 🔴 THE CELL PRE-REGISTERED THIS EXACT OUTCOME, AND ITS READING IS STRONGER THAN MINE

I wrote the section above before reading the cell's source. **It had already pre-committed how to
interpret this result, on 2026-08-19, BEFORE it was run** — and my "consolidation contributes
nothing" is the weak form of what it actually says:

> **(e)** *the `consolidation` ablation moves NO substrate route, at any seed, in either regime,
> while the control's `n_provenance` is > 0 -> outcome (i). **THE READ-OUT DOES NOT CONSULT GROUNDED
> FACTS.** Report it as a wiring defect in the assembly and **do NOT build a new channel on the
> grounding path until it is fixed, because that channel could not be measured here.***
>
> **(f)** *the `consolidation` ablation moves a substrate route -> the table is interpretable; the
> definitions / gap_detector nulls **may now be read as facts about those organs, and only now**.*
>
> **(g)** *the control's `n_provenance` is 0 -> THE FIX DID NOT TAKE AND NOTHING ELSE IN THIS RUN IS
> INTERPRETABLE. Checked FIRST, before any arm is looked at.*

**ALL THREE CONDITIONS FOR (e) HOLD.** No substrate route moved on any seed; and
`control_n_provenance = [38, 68, 112]` — every control is above zero, so **(g) does not fire and the
run is interpretable.**

➡️ **THE PRE-REGISTERED CONCLUSION IS THEREFORE: THE READ-OUT DOES NOT CONSULT GROUNDED FACTS. THAT
IS A WIRING DEFECT IN THE ASSEMBLY, NOT A FACT ABOUT CONSOLIDATION'S QUALITY.** *Consolidation is
not weak here; it is DISCONNECTED from the thing being scored.* The substrate banks facts
(`38`/`68`/`112` provenance records) and the read-out never looks at them.

🚫 **AND (f) DID NOT FIRE, SO THE `definitions` AND `gap_detector` NULLS ARE STILL NOT READABLE AS
FACTS ABOUT THOSE ORGANS.** My caution above was right; the cell's reason is better than mine.

## ⚠️ THIS LANDS ON OUR OWN CURRENT PLAN, AND IT ARRIVED FIVE DAYS LATE

The pre-registered instruction is explicit: **do NOT build a new channel on the grounding path until
the wiring defect is fixed, because that channel could not be measured here.**

**Priority-2 brief `the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by` proposes
building exactly such a channel.** On this evidence it is **PREMATURE, NOT WRONG**: if the read-out
does not consult grounded facts, a new grounded channel would be unmeasurable for the same reason
consolidation is — it would show a clean, meaningless null and we would learn nothing.
➡️ **Fix the read-out's connection to grounded facts FIRST; that is now the cheaper and prior item.**
*This is the second time this week that reading a finished-but-unread result reversed the next
build.* (The first was `exp_sr_scale_ladder_v1`.)

## 🔎 TRACED THE CAUSE, AND IT IS NOT UNKNOWN — THE FIX IS BUILT AND UNWIRED

The cell scores two substrate routes, and neither reads the fact store:

| route | what it actually reads |
|---|---|
| `episodic()` | `sub.recall_sentence(...)` — the **episodic** store |
| `semantic()` | `sub.profile()` — the accumulated **context bundles** (`_sums[lemma]`) |

**The substrate exposes more routes than the cell scored:** `recall_cortical`, `consolidated`,
`query`. And `Substrate.recall_cortical`'s own docstring names this exact symptom, in advance:

> *"THE CORTICAL READ. Retrieve CONSOLIDATED concepts by content similarity to a cue. **THE ROUTE
> THAT DID NOT EXIST, and whose absence was this substrate's largest measured fidelity defect: every
> other retrieval route addresses the episodic store, so consolidation could be ablated to zero
> without moving the read-out at all.** Under CLS, retrieval of consolidated knowledge is a CORTICAL
> read; this is it."*

➡️ **SO THE DEFECT WAS KNOWN, THE FIX WAS BUILT, AND IT IS SLOT `B3'` — `NEEDS_ADAPTER`, i.e. built
and NOT on the live path.** The 08-19 cell re-measured the very defect `B3'` exists to fix, because
it scored only the two old routes. *That is not a criticism of the cell — it pre-registered its
readings and reported honestly. It is a statement about what was and was not on the scored path.*

🔗 **AND IT JOINS UP WITH TONIGHT'S INTEGRATION.** `cortical_read_never_tested_where_it_matters`
(re-verified 6/6, reviewed STRONG) found the cortical read clears its floor **only with a SUPPLIED
distributional space**; nothing self-built generalises. **So B3' is built, unwired, and known to
need a channel we have not settled.** The wiring question and the channel question are one project,
and each was unmeasurable without the other — which is a sufficient explanation for why both
stalled.

## WHAT THIS DOES AND DOES NOT LICENSE

- ✅ **Consolidation contributes nothing measurable to the end-to-end read-out**, on a task where the
  ceiling is a floor. That is a real, paired, three-seed null with reachability demonstrated.
- 🚫 **It does NOT say consolidation is useless.** The task tops out at `0.0300`; an organ could
  matter on a task with headroom and be invisible here. **The cell says so itself and I am not
  going past it.**
- ➡️ **The cheapest next question is not "improve consolidation" but "is the reachability of
  `foraging` and `gap_detector` instrumented at all?"** Two of six switches cannot currently be
  shown to fire.

---

# THIRD OF THE ELEVEN: THE DISCRIMINATION CEILING, AND ONE ARM THAT WAS NEVER IMPLEMENTED

Source: `data/exp_discrimination_ceiling_v1/metrics.json`, run **2026-08-19**, 4 corpora. Also
verdict-less, also unread. **Its gold is `conceptnet_gold_v1`, provenance-filtered, NO WordNet
source, paradigmatic only** — so it is untouched by the `~78%` morphology leakage that voided the
WordNet-scored floors.

**Its design is the good kind:** retrieval and discrimination are reported SEPARATELY, and the
discrimination arms re-rank **the same top-50 candidate set**, so any difference is attributable to
the ranker and not to retrieval. `items_predate_mechanism: true`.

## THE CEILING RESULT: THE ANSWER IS IN THE POOL AND WE STILL MISS IT ~88% OF THE TIME

`ORACLE_ceiling_diagnostic = 1.0` on all four corpora — by construction the pool always contains a
gold answer. Yet:

| corpus | n in pool | RAW | DICE | NPMI | BAG_COSINE | RANDOM |
|---|---|---|---|---|---|---|
| simplewiki | 1047 | 0.1356 | 0.1184 | 0.1127 | **0.1557** | 0.0392 |
| onestop | 515 | 0.0913 | 0.0641 | **0.0485** | 0.1010 | 0.0291 |
| mcguffey_graded | 589 | 0.0781 | 0.0866 | 0.0594 | 0.0985 | 0.0170 |
| arc | 913 | 0.1117 | 0.1260 | 0.1216 | **0.1566** | 0.0329 |

➡️ **Every arm is far above RANDOM, so the machinery is doing something. But with the answer
GUARANTEED present, the best ranker picks it `~10-16%` of the time.** *This is the discrimination
gap isolated from the supply gap — the complement of the `79% ABSENT` census above. Both are real
and they are different problems.*
✅ **The one CI-separated re-ranking win is `BAG_COSINE` on `arc`: `+0.0449` over RAW, p=`0.004`.**
🔻 *`NPMI` on `onestop` is a CI-separated LOSS (`-0.0427`, p=`0.006`) — reweighting can hurt.*

## 🔴 `SECOND_ORDER` AND `BAG_COSINE` ARE THE SAME COMPUTATION. THE ARM WAS NEVER IMPLEMENTED.

**Identical hit COUNTS on all four corpora — `163/163`, `52/52`, `58/58`, `143/143`, over 3,064
items.** Two rankers cannot agree that exactly by chance. The source says why:

```python
bagc = np.array([float(Cn[i] @ Cn[j]) for j in cand])
sec  = np.array([float((Cn[i] * Cn[j]).sum()) for j in cand])
```

**`Cn[i] @ Cn[j]` and `(Cn[i] * Cn[j]).sum()` are the same dot product written two ways.** The
docstring intends *"cosine between profiles restricted to shared neighbours"* — **there is no
restriction in the code.** This is not a collapse under a parameter setting (like `multi_hop`'s
`beta = n_dim` Dirac delta, which the slot table already records as having confounded two prior
cells); it is the same expression twice.

⚠️ **WHAT THIS VOIDS, AND ONLY THIS:** the cell pre-registered *"(iii) BAG_COSINE **or SECOND_ORDER**
beats RAW -> our accumulate/project machinery earns its keep."* **The SECOND_ORDER half of that
reading was never tested.** Anyone reading `SECOND_ORDER +0.0449, p=0.008` on `arc` would conclude
the paradigmatic cue helped; it is `BAG_COSINE` counted twice.
✅ **WHAT SURVIVES:** `RAW`, `DICE`, `NPMI`, `BAG_COSINE` and `RANDOM` are genuinely different
computations, the positive control holds (`RAW 142` vs `RANDOM 41` hits), and **the `BAG_COSINE`
win on `arc` stands on its own.** *The defect is one duplicated arm, not a broken cell.*
🔗 **AND IT DOES NOT CONTRADICT THE LANDED SECOND-ORDER NEGATIVE** (`exp_readout_second_order_v1`,
`NEW_READOUT_CLEARS_FLOOR_NO`). That cell tested the cue properly; this one simply never tested it.
**Second-order remains closed on that evidence, not on this.**

## TLDR

We read thirty-four thousand sentences and stored three hundred and eighty-six facts.

Almost all of that loss happens at the very last step: of the things the system managed to form an
opinion about, it refuses to commit to **98.5%** — nearly always for one reason, "not confident
enough".

And when we test whether it can retrieve the right meaning, **four times out of five the right
answer was never among the options it was choosing from.** So a lot of effort spent making the
choosing smarter was aimed at the wrong stage.

Both numbers come with a caveat that travels with them: the answer key used here is itself only
about 64% correct, so treat the four-in-five as a direction, not a precise measurement.

## QUESTIONS

None. This is a census; it decides nothing on its own.

## NEXT STEPS

1. **The empty-pool / below-threshold collision at `canonicalize_fast:657` is a real defect and is
   cheap to fix** — the caller cannot currently tell "nothing to compare against" from "compared and
   unconvinced", and those need opposite responses.
2. `HYPOTHESIS_BELOW_COMMIT_STRENGTH` at 21,207 is the single largest late loss. **Whether that
   threshold is right has not been tested here** — this cell counts, it does not score.
3. Ten more verdict-less full runs remain unread.
