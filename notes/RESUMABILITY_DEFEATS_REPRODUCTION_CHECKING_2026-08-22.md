# **I TRIED TO RE-RUN A LANDED CELL TO VERIFY ITS NUMBERS AND GOT `elapsed 0.0s`. THE MANDATORY CHECKPOINT/RESUME DISCIPLINE MAKES "RE-RUN TO VERIFY" A NO-OP.**

**A real tension between two of this project's own rules, found by trying to obey both.**

---

## 1. WHAT HAPPENED

*I had quoted `exp_bridge1_twostage_event_situation_v2`'s numbers into a re-plan without recomputing
them, and my own next step said to fix that before building on them.*

| attempt | result |
|---|---|
| `--full` | **`[resume] seed=N already done, skipping` x5, `elapsed 0.0s`** -- metrics re-assembled from stored units, **NOTHING RECOMPUTED** |
| `--smoke` | *same* -- its own output dir already held completed units |
| **`--self-test`** | ✅ **GENUINELY RECOMPUTED** |

## 2. ⚠️ **SO WHAT I CAN AND CANNOT CLAIM**

✅ **THE SELF-TEST RECOMPUTED AND REPRODUCED THE PATTERN INDEPENDENTLY:**
`A_two_stage 1.000 | B_two_stage 1.000, B_governor 0.500, B_scrambled_event 0.667, B_bow 0.500 |
C_two_stage 1.000, C_governor 0.500, C_scrambled_discourse 0.583, C_bow 0.500 | Bgen 1.000, Cgen 1.000`

*Its scramble values differ from the landed run (`0.667`/`0.583` vs `0.583`/`0.650`) because it uses
its own fixed configuration -- **which is what makes it an independent check rather than a replay.***

🔻 **WHAT I CANNOT CLAIM: I have NOT independently recomputed the landed FULL numbers.** *`0.962`,
`lift_B 0.417`, `lift_C 0.350` and the open-vocab figures remain READ, not REPRODUCED.*

✅ **NO DAMAGE: the landed `metrics.json` is byte-identical on `means` and `verdict` to the backup I
took first.** *`data/` is git-tracked, so this was recoverable regardless.*

## 3. 🔑 **THE GENERAL PROBLEM, WHICH IS WORTH MORE THAN THIS ONE CELL**

**`CLAUDE.md` MANDATES per-unit checkpoint/resume for any multi-unit cell**, and it is right to -- it
exists because killed runs used to lose everything. **But the same mechanism means a landed cell can
never be re-run as a CHECK: it will always replay its stored units and report a verdict in `0.0s`.**

> ### **A CELL THAT CANNOT BE RE-COMPUTED CANNOT BE FALSIFIED BY RE-RUNNING IT. AND THE RE-RUN *LOOKS LIKE A PASS* -- SAME VERDICT LINE, SAME NUMBERS, ZERO SECONDS.**

***THAT IS THE DANGEROUS PART: the output of a no-op re-run is INDISTINGUISHABLE from a successful
reproduction unless you read the elapsed time and the resume lines.*** *I would have reported
"verified, reproduces exactly" if I had only read the verdict line -- which is precisely what a
verification step is supposed to prevent.*

**AND THE WORKAROUND IS BLOCKED BY ANOTHER CORRECT RULE:** *forcing recompute means DELETING the
stored per-unit results, and this project forbids bundling a deletion with real work (auto-denied,
24 of 31 denied commands destroyed the work bundled with them) -- quite apart from those units being
canonical artifacts.*

## 4. ➡️ THE FIX I AM **NOT** BUILDING WITHOUT A DECISION

*The clean answer is a `--verify` / `--fresh-units` flag that writes to a NEW output directory and
ignores existing checkpoints -- recompute without deleting anything.* **That is a change to the cell
harness, it touches every experiment, and it is not mine to make unilaterally at 3am.** *Filed here;
`--self-test` remains the available independent check in the meantime.*

## 5. ⚠️ LIMITS

1. **Tested on ONE cell.** *I have not confirmed every cell resumes this way, though the discipline is
   mandatory so most multi-unit cells should.*
2. **`--self-test` is not a full reproduction** -- *different configuration, smaller, its own fixtures.*
3. **This does not cast doubt on the landed numbers.** *It says they are UNVERIFIED BY ME, not wrong.*

## TLDR

I quoted some results into a plan without re-running them, then tried to fix that. **Re-running
finished in zero seconds and printed the same answer — because it had simply loaded its saved
workings rather than redoing them.**

That safety feature is correct and exists for good reasons: long runs used to lose everything when
interrupted. **But it means a finished experiment cannot be checked by running it again — and worse,
the fake re-run looks exactly like a real one.** Same verdict, same numbers, no warning. I would have
told you "verified" if I had not noticed the zero.

**What I could do: the built-in self-check does recompute, and it independently produced the same
pattern** — the system at 100%, the word-counting comparison at coin-flip, and sabotaging the relevant
structure breaking it. **So the finding holds up; the exact headline numbers remain quoted rather than
reproduced.**

**The clean fix is a "recompute from scratch into a fresh folder" option**, which avoids deleting
anything. That touches every experiment in the project, so I am flagging it rather than doing it
unannounced.

## QUESTIONS

None.

## NEXT STEPS

1. **Treat `--self-test` as the available reproduction check** until a fresh-run flag exists.
2. **Any claim resting on a landed cell should say READ or REPRODUCED.** *I have been saying neither.*
3. *Method note: **the tell was `elapsed 0.0s`, not the verdict.** A verification step that reads only
   the conclusion verifies nothing.*
