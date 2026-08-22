# **RUNTIME CHECK: `94` REGISTERED CAPABILITIES CLAIM THEY ARE NOT REACHED BY THE LIVE PATH, AND ONLY ONE APPARENT COUNTER-EXAMPLE EXISTS -- WHICH TURNS OUT TO BE AN ARTIFACT OF MY OWN COMPARISON.**

**CLAUDE.md says `pipeline_status` is wrong in BOTH directions, so I checked it against runtime rather
than quoting it. The field is in better shape than its warning suggests, and the "built but unreached"
count is real.**

---

## 1. METHOD -- RUNTIME, NOT GREP

*Reused `tools/audit_docstrings_vs_live_closure.py`, which READS with the substrate (1,200 sentences)
so lazily-imported organs actually load, then snapshots `sys.modules`. **That IS the live closure.***

**Live `hdlab` modules: `45`.**

## 2. THE COMPARISON

| registry claim | rows | disagrees with runtime |
|---|---|---|
| `WIRED_AND_PIPELINE_USED` | 55 | **16 not in the live closure** |
| `WIRED_BUT_NOT_PIPELINE_REACHABLE` | 94 | **1 appears live** |
| | **149 checkable** | **17 = `11.4%`** |

## 3. 🔻 **AND `11.4%` IS AN UPPER BOUND I AM NOT ENTITLED TO REPORT AS AN ERROR RATE**

**The single "not reachable but IS live" row is `form_identity_channel_vwfa_additive` -- MY OWN row,
set an hour earlier.** *Its path is FUNCTION-level (`...reading_grounding_loop.py::form_identity_vector`);
my comparison stripped the `::` and matched the MODULE, which is live while the function is never
called.* **A granularity artifact of my probe, not a registry error. The status I wrote is correct.**

**And several of the 16 -- `arc_parser`, `pos_tagger`, `arc_labeler` -- are documented in CLAUDE.md as
lazy imports inside function bodies that "load only on a path it did not exercise".** *The tool's own
scope note says it: **"the closure is from ONE read path. An organ reached only by a different entry
point would not appear as live here."***

> # **SO THIS PROBE CANNOT SEPARATE REGISTRY ERROR FROM PROBE INCOMPLETENESS. `11.4%` IS THE CEILING ON DISAGREEMENT, AND THE TRUE ERROR RATE IS LOWER BY AN UNKNOWN AMOUNT.**

## 4. ✅ WHAT *IS* ESTABLISHED, AND IT IS THE USEFUL PART

**Of `94` rows claiming they are NOT reached by the live path, exactly ONE looked otherwise, and that
one was my own artifact.** *Runtime evidence corroborates the field in the direction that matters.*

> ## **~`94` REGISTERED CAPABILITIES ARE BUILT, WIRED INTO `hdlab/`, AND NOT REACHED BY THE READING PATH. PLUS `25` MARKED `ISLAND`. THAT IS ROUGHLY HALF OF THE `212` REGISTERED CAPABILITIES NOT PARTICIPATING IN WHAT THE SYSTEM ACTUALLY DOES.**

*That is not automatically waste -- an opt-in lever, a diagnostic, or an organ on a different entry
point is legitimately unreached. But it is the honest denominator for "what have we built".*

## 5. AN INCIDENTAL FINDING WORTH RECORDING

**`hdlab/learner/plugins/estimation_plugin.py` imports from `experiments/`** -- surfaced when an import
chain failed under my stdout redirect. **A library module depending on an experiment file is a layering
inversion**: experiments are supposed to be disposable, and one of them is now load-bearing for
`hdlab.learner`. *Not fixed here; recorded.*

## 6. LIMITS

1. **ONE read path** (`read + recall + query`). *An organ reached by a different entry point is
   invisible to this and reads as unreached.*
2. **MODULE granularity.** *A live module does not mean a live function -- that is exactly the artifact
   above, and it applies to every row whose path names a function.*
3. **149 of 212 rows were checkable**; the rest do not name an `hdlab/*.py` path.
4. **My probe crashed once** on `sys.stdout.reconfigure` under a `StringIO` redirect. *Fixed by not
   redirecting; the crash is what surfaced the layering inversion.*

## TLDR

Our records mark each built component with whether the running system actually uses it. The project's
own notes warn that this marking is unreliable in both directions, so I checked it by **running the
system and seeing which components actually load**, rather than trusting the label.

**The records are in better shape than their warning suggests.** Of 94 components marked "not used by
the live system", exactly one looked like it might be used — **and that one turned out to be a mistake
in my own checking**, not in the records. I was comparing whole files when the record referred to a
single function inside one.

**So the useful number stands: about 94 built components are not reached by the system's main reading
path, plus 25 more marked as isolated — roughly half of everything we have built.** That isn't
automatically waste; some are deliberate optional levers or tools for a different entry point. But it
is the honest answer to "what have we built and what is actually running".

**One thing I can't claim:** the 16 components marked "used" that didn't show up. Several are known to
load only when a specific code path runs, and my test didn't exercise those paths. **My check can't tell
a wrong record from an incomplete test**, so I'm reporting that as a ceiling, not a finding.

**And an unrelated thing fell out:** a core library file imports from an experiment file. Experiments
are meant to be disposable; one of them is now holding up part of the library.

## QUESTIONS

None — Q106 (the 150-line scoring sheet) is the only open one.

## NEXT STEPS

1. **The `94` unreached capabilities are the honest denominator for "what have we built".** *Worth a
   pass to separate deliberate opt-in levers from genuinely stranded work -- but only when there is a
   consumer to wire them to, not as a tidying exercise.*
2. ⚠️ **A function-level registry path cannot be checked by a module-level closure.** *Any future
   reachability audit must compare at the same granularity as the path field, or it will manufacture
   exactly the false positive I did.*
3. *Method note: **the probe's one disagreement was mine.** Checking who owns a discrepancy before
   reporting it is becoming the highest-yield habit of the week.*
