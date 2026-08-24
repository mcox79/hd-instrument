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

## WHAT THIS DOES AND DOES NOT LICENSE

- ✅ **Consolidation contributes nothing measurable to the end-to-end read-out**, on a task where the
  ceiling is a floor. That is a real, paired, three-seed null with reachability demonstrated.
- 🚫 **It does NOT say consolidation is useless.** The task tops out at `0.0300`; an organ could
  matter on a task with headroom and be invisible here. **The cell says so itself and I am not
  going past it.**
- ➡️ **The cheapest next question is not "improve consolidation" but "is the reachability of
  `foraging` and `gap_detector` instrumented at all?"** Two of six switches cannot currently be
  shown to fire.

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
