# 🚨 **`Substrate.read(n_sentences=N)` DOES NOT READ `N`. ASK FOR 8,000 AND YOU GET ~1,000.**

**Measured 2026-08-22, chasing why a bigger read produced no more consolidated knowledge.**

| asked | ACTUALLY READ | checkpoints | consolidated terms |
|---|---|---|---|
| `1,000` | `1,000` | 9 | 30 |
| `3,000` | 🔻 **`1,060`** | 9 | 30 |
| `6,000` | 🔻 **`1,060`** | 9 | 30 |
| `10,000` | 🔻 **`1,060`** | 9 | 30 |

**Asking for ten thousand sentences and asking for three thousand return the SAME 1,060 sentences,
the SAME 9 checkpoints and the SAME 30 consolidated terms.** *Deterministic: repeated runs agree
exactly.*

## IT IS NOT ONE SEED, ONE DIMENSION, OR ONE MAGIC NUMBER

| config | asked `8,000` -> read |
|---|---|
| seed `20260819`, `n_dim=512` | `1,060` |
| seed `20260819`, `n_dim=1024` | `1,200` |
| seed `7`, `n_dim=512` | `1,220` |
| seed `7`, `n_dim=1024` | `1,500` |
| seed `101`, either | `960` |

**Every configuration stops between `960` and `1,500` when asked for `8,000`.** The cap moves with
configuration; the fact of it does not.

### 🔻 **AND SUCCESSIVE CALLS READ PROGRESSIVELY LESS**

```
call 1: 1,060 sentences   call 2: 240   call 3: 220
```

**So "read again to read more" degrades too** -- three calls asking 8,000 each delivered `1,520`
sentences in total. *This is why chunked reading produced more consolidated terms than one long
call (126 vs 30): each CALL gets a fresh, smaller allowance, and more calls means more allowances.*

## ⚠️ WHY THIS IS DANGEROUS RATHER THAN MERELY SURPRISING

**IT IS SILENT.** No exception, no warning, no log line. **`read(n_sentences=40000)` returns
normally**, and every downstream number is computed on ~1,000 sentences.

✅ **THE EVIDENCE WAS ALWAYS THERE AND NOBODY LOOKED: `ReadResult.n_sentences` reports the TRUE
count.** *One attribute, on the object every caller already holds. **This is the "make outputs print
quantities that constrain each other" rule with the quantity already present and simply unread.***

## 🔻 **BLAST RADIUS, ENUMERATED THE NEXT MORNING -- AND IT DEFLATES THIS FINDING SUBSTANTIALLY**

**The alarming number above is from a call shape NOTHING IN THE CODEBASE USES.** Enumerated across
`experiments/`, `tools/`, `verification/`, `hdlab/`:

- **Literal `n_sentences` call sites: 14. Only `2` exceed 1,500 -- and both are MY OWN witness file.**
- **Variable call sites: 16. Every experiment cell binds `chunk = 400`** and reads in a LOOP
  (`exp_sensorimotor_spoke_grounding_v1`, `exp_cortical_read_consolidated_v1`,
  `exp_predictive_write_gate_v1`, `exp_grounding_precision_gold_v1`,
  `exp_substrate_end_to_end_readout_v1`). The rest are `min(...)`-bounded diagnostics.

> ### **NO EXPERIMENT CELL ASKS FOR A SINGLE LARGE READ. THE PATTERN THAT FAILS AT 13% IS ONE NOBODY WRITES.**

**And the pattern everyone DOES write was measured directly -- 25 successive `read(400)` calls:**

```
400 400 400 340 180 400 400 300 200 400 220 340 400 240 400 280 400 360 220 280 320 400 200 180 400
requested 10,000  ->  delivered 8,060  =  81%     (short_read fired on 13 of 25 calls)
```

| pattern | delivery |
|---|---|
| one call asking `8,000` | 🔻 `13%` |
| **25 chunked calls of `400` -- REAL USAGE** | **`81%`** |

➡️ **SO THE HONEST IMPACT IS A ~19% SHORTFALL ON REAL CELLS, NOT AN ~87% ONE.** *A cell that reports
40,000 sentences across 100 chunks probably read closer to 32,000. That is worth knowing and worth
recording; it is NOT the catastrophe the single-call number implies.*

**🚫 DO NOT QUOTE THE `13%` AS THE PROJECT'S EXPOSURE.** It is the exposure of a call shape that
appears nowhere but in the test written to catch it. **The `81%` is the number that describes us.**

## 🚫 WHAT I AM **NOT** CLAIMING

- 🚫 **NOT that every landed cell is affected.** This measures **`Substrate.read()`**. Cells that
  drive `reading_grounding_loop` directly may take a different path and may be fine. **That
  enumeration has not been done and is the obvious follow-up.**
- 🚫 **NOT that any specific published number is wrong.** A result computed on 1,000 sentences is
  still a result *on 1,000 sentences*; the defect is that it may be described as 40,000.
- 🚫 **NOT that the cause is identified.** The pattern -- a large first allowance, then sharply
  smaller ones -- is consistent with the forager exhausting patches or a corpus handle advancing,
  **but I have not traced it and will not guess in a note.**

## ➡️ WHAT IT EXPLAINS ALREADY

- **The consolidation "cap" at 30 terms per call is not a consolidation cap at all** -- it is the
  read cap in disguise. Consolidation scales with checkpoints, checkpoints scale with sentences, and
  the sentences stopped arriving.
- **My own growth curve was measuring the wrong thing.** Reading in chunks appeared to grow the
  consolidated pool to 180; it was buying extra per-call allowances, not extra reading.
- **The plan's "read more" lever is inert inside a single call**, which is how most cells read.

---

## TLDR

If you ask this system to read ten thousand sentences, it reads about a thousand and tells you it is
done. Ask for three thousand — the same thousand. Ask again and you get two hundred more.

Nothing errors. Nothing warns. Any measurement taken afterwards is quietly based on a fraction of the
text you thought you gave it.

The honest part: the system **does** report how much it actually read, on the same object every
caller already has. Nobody had looked at it.

I found this chasing something else entirely — why reading more produced no more remembered
knowledge. The answer was that it was never reading more.

I am not claiming our published results are wrong. A number measured on a thousand sentences is a
real number about a thousand sentences. The risk is that it gets described as forty thousand.

## QUESTIONS

None.

## NEXT STEPS

1. **Enumerate which cells call `Substrate.read()` with a large `n_sentences`** and check what their
   `ReadResult.n_sentences` actually was. That is a bounded search and it decides how far this
   reaches.
2. **A guard belongs in `read()`**: if it delivers materially fewer sentences than asked, say so
   loudly. A caution in a note will not be read by the next caller.
3. 🚫 **Do not quote a cell's requested `n_sentences` as its corpus size** without checking the
   returned count.
