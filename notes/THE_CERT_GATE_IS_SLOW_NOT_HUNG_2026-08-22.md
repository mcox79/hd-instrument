# 🔻 **THE CERT GATE WAS NOT HANGING. IT WAS WORKING, SLOWLY, AND A HEALTHY RUN WAS KILLED.**

**The claim under test**, from the goal-bearing re-land: *"`verification/run_certification.py`
stalled — CPU flat at `371.4s -> 371.5s` for 11+ minutes while resident — killed after ~20 minutes
having collected only 33 items with one `F`."*

**Measured directly. The premise does not survive.**

---

## 1. COLLECTION IS FINE

```
482 tests collected in 34.70s      exit 0
```

**So nothing hangs during discovery.** Whatever happened was in EXECUTION.

## 2. THE "STALL" IS A SUBPROCESS WAIT, AND THIS REPO HAS DOCUMENTED THAT FALSE ALARM BEFORE

Item ~33 sits **inside `test_all_witnesses_exit_clean`**, which runs each `verify_*.py` as a
**SUBPROCESS**. `PER_WITNESS_TIMEOUT_S = 600`, and the file's own comment records that two witnesses
legitimately need **~94s and ~151s** — *"a 120s cap produced FALSE timeouts in the audit."*

> ### 🔑 **A PARENT PYTEST PROCESS SHOWS FLAT CPU WHILE ITS CHILD DOES THE WORK. THAT IS EXACTLY THE TRAP `CLAUDE.md` ALREADY DOCUMENTS** — *"the recorded PID showed CPU 0 s and a 4 MB working set, while its child held 1,052 MB and was doing all the work... this fooled the Director twice in one session."*
> **`371.4s -> 371.5s` is not a stalled run. It is a run waiting on a subprocess, which is what this
> test does by construction.**

## 3. AND THE SLOW WITNESSES PASS

Ran the two most likely suspects directly:

```
verify_lemma_verb_no_nonword_stems.py + verify_integration_health_import_graph.py
    2 passed in 504.80s (8m 24s)
```

**Both PASS.** *Two tests, eight and a half minutes — that alone makes a ~20-minute kill premature.*

## 4. ⚠️ BUT THERE IS A REAL FAILURE, AND IT IS NOT THE HANG

A bounded run of the witness file reached `.................F` before my own 590s cap — **17 passes
then one genuine `F`, at roughly witness 18 of ~32.** The re-land agent saw the same `F`.

**So the correct statement is: THE GATE IS SLOW, AND SOMETHING IN IT FAILS.** Those are two findings,
and conflating them is how "the gate hangs" got recorded.

**I did NOT identify which witness fails** — the two I tested as candidates both passed, so it is one
of the others. That enumeration is the remaining work.

## 5. 🔻 AND A PROCESS FAILURE OF MY OWN, WORTH MORE THAN THE FINDING

**`certification_gate_hangs` IS ALREADY A FILED PROBLEM**, created by the concurrent session while I
was measuring — and its own entry says *"VERIFY THE PREMISE FIRST... It may be SLOW, not hung."*
**I reached the same conclusion independently, twenty minutes later, having duplicated the work.**

🚫 **I DID NOT RUN `tools/before_you_start.py` BEFORE STARTING.** I built that check, wired it into the
standard flow, and then skipped it on exactly the kind of task it exists for. *Its concurrent-work
section — which I added after two duplications on 2026-08-22 — is the thing that would have caught
this.*

➡️ **THIS EVIDENCE IS HANDED OVER, NOT ACTED ON.** The problem is filed, filed problems belong to the
solver, and the owner's ruling is explicit: *"any 'problem' you have in the problems tab is going to
be worked on, so try not to compete with that."*

---

## TLDR

An experiment helper reported that our mandatory pre-flight check had frozen, and killed it after
twenty minutes. It had not frozen. It runs each of about thirty checks as a separate program and
waits for each one, so the main process sits idle-looking while the real work happens elsewhere —
a false alarm this project has documented before and been caught by before.

The two slowest checks I tested both pass, and take eight and a half minutes between them. So a
twenty-minute kill was always going to look like a hang.

There is a real failure in there — one check genuinely fails — but that is a different problem from
"it hangs", and I have not yet found which one.

The part worth keeping: I duplicated work that another session had already started and already
reached the same conclusion on, because I did not run the check-what-else-is-happening tool that I
built yesterday for precisely this.

## QUESTIONS

None.

## NEXT STEPS

1. 🚫 **NOT MINE.** `certification_gate_hangs` is filed; this note is evidence for whoever works it.
2. **Finding the failing witness is the open half** — the two obvious candidates pass.
3. **Run `before_you_start.py` before starting.** The tool works; I did not use it.
