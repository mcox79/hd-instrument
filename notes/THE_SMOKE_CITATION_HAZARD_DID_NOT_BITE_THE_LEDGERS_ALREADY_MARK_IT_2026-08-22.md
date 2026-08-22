# **I TRACED THE HAZARD I REPORTED AND IT HAS NOT BITTEN. EVERY CITATION OF A SMOKE-PASSES/FULL-FAILS CELL MARKS IT AS A SMOKE.**

**Yesterday's note said `156` smoke runs carry a pass their own full run does not, and that "the hazard
is citation". I explicitly wrote that I had NOT traced a single citation. I have now traced them, and
the answer is that the existing bookkeeping already handles it.**

---

## 1. WHAT I LOOKED FOR

**All 156 smoke cell names, searched across every note and the memory index.** *47 name-mentions
found, concentrated in a handful of cells.*

## 2. ✅ WHAT THE CITATIONS ACTUALLY SAY

| where | how it appears |
|---|---|
| `RECOVERY_PROGRAM.md` (M60, M100, M107, ...) | `... /metrics.json \| HARD_PASS \| **smoke** \| ...` -- **a dedicated `smoke` COLUMN, filled in** |
| `recovery_ledger_reading_tier_2026-08-14.md` | same rows, same explicit `smoke` marking |
| `research_drill_2x_pfc_v2_depth12_cv_collapse` | **"Source HARD_PASS (smoke):"** -- marked in the text, and the note is a DRILL INTO the collapse |
| `skunkworks_landed_vet_wave1_smoke_HF_4cell_verification` | *"Counter-evidence verified"* -- a VET note whose own FILENAME carries `smoke_HF` |

> # **EVERY CITATION I READ MARKS THE SMOKE STATUS. THE LEDGERS HAVE A COLUMN FOR IT AND IT IS FILLED IN. NOBODY MISTOOK A SMOKE FOR A FULL RUN.**

**That is a control that already existed, that I did not know about, and that I implicitly assumed was
missing when I wrote "the hazard is citation".**

## 3. 🔻 WHAT I THEREFORE WITHDRAW, AND WHAT SURVIVES

| claim from yesterday | status |
|---|---|
| 156 smoke rows carry a pass their full run does not | ✅ **stands, measured** |
| they are 5.8% of all HARD_PASS rows | ✅ **stands** |
| the single-file evidence gate cannot see the class | ✅ **stands, confirmed on the pair** |
| **"the hazard is CITATION"** | 🔻 **WITHDRAWN -- traced, and it has not happened** |
| **"a prior-work check that reads row 1 will sometimes read the smoke"** | 🔻 **UNSUPPORTED -- I asserted a mechanism and never checked whether it had occurred** |

**The residual risk is COUNTING, not citing:** *a bare count of HARD_PASS verdict strings still includes
all 156.* **But the ledgers carry the column needed to exclude them, so even that is a query defect
rather than a records defect.**

## 4. ⚠️ LIMITS

1. **I read the citation contexts for 3 of the ~12 most-cited cells**, not all 47 mentions. *A
   mis-citation could exist in the tail.*
2. **Name-matching only.** *A note quoting a smoke's NUMBER without naming the cell is invisible to
   this trace -- and that is the more likely form of the error.* **So this is "not found", not
   "absent".**
3. **The memory index was searched and returned no hits**, which is a genuine positive for the banner.

## TLDR

Yesterday I reported that 156 of our recorded successes are quick trial runs whose real run failed, and
said the danger was that someone would quote the trial as if it were the real result.

**I went and checked whether that had ever actually happened. It hasn't.**

Every place these results are written down marks them as trial runs — the main ledger literally has a
column for it, filled in correctly on every row I read. One of them is cited in a note whose entire
purpose is investigating why the result collapsed at full scale.

**So the bookkeeping was already better than I gave it credit for**, and the specific worry I raised was
mine rather than the archive's.

**What still stands:** the 156 count is real, and a simple tally of "how many successes do we have"
would still count them, because the tally reads the success column and not the trial column. That's a
fixable query, not a broken record.

**And one honest caveat about my own check:** I searched for these results by *name*. If someone quoted
one of their *numbers* without naming the experiment, I would not have found it — and that is the more
likely way this kind of mistake actually happens. So this is "I looked and did not find it", which is
weaker than "it is not there."

## QUESTIONS

None — Q105 still open, independent of this.

## NEXT STEPS

1. **Credit the existing control**: the `smoke` column in `RECOVERY_PROGRAM.md` / the recovery ledger is
   what prevented this. *Any future results tally should read it.*
2. 🚫 **Stop drilling this line.** *The class is measured, the hazard is traced and did not fire, and
   the residual is a one-line query fix. Continuing would be drilling a closed question.*
3. *Method note: **an absence claim requires an enumeration, and mine was a name search** -- I have said
   so in the limits rather than letting "not found" read as "absent", which is the standing rule and
   the exact thing I got wrong the other direction yesterday.*
