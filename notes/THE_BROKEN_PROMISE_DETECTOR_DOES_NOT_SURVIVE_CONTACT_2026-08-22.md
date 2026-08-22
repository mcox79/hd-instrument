# 🔻 NEGATIVE: **"AN UNWIRED MODULE THAT DECLARES THE GAP IT CLOSES" IS NOT A USABLE FLAG**

**The idea.** `hdlab/foundation_persistence.py` is unwired and its docstring says, verbatim, *"THE
GAP THIS CLOSES: ... every run starts from an EMPTY store."* **A module that names the problem it
solves and is not connected is a broken promise** -- so scan for that shape and rank the ~100
unwired organs by what they claim to fix. The prior audit (`504d9abb4`) answered *which* modules are
unwired; this would answer *which to wire first*.

**I tested the signal before building the tool. It does not hold.**

## THE MEASUREMENT

Live closure at RUNTIME (a real `Substrate.read()` + `query()`, per the documented method -- grep is
wrong in both directions here): **151 modules on disk, `36` loaded, `115` not loaded.** *The `36`
reconciles exactly with the 2026-08-20 audit, which is the only reason I trust the probe at all.*

**Gap-declaring language in the docstring of an unwired module: `3` of `115` (2.6%).** *That base
rate is in the range this project calls a signal -- the ceiling-detector proposal was abandoned at
48.5% because a flag firing on half the archive is not a flag.* **The rate was fine. The PRECISION
was not.**

| candidate | matched line | verdict |
|---|---|---|
| `foundation_persistence` | *"THE GAP THIS CLOSES: ... every run starts from an EMPTY store"* | ✅ **TRUE POSITIVE** |
| `context_grounded_valence` | *"it is NOT wired to anything"* | 🔻 **FALSE POSITIVE** |
| `parse_goal_extraction` | *"that induction step itself is NOT wired here"* | 🔻 **FALSE POSITIVE** |

**`1` of `3`. And the one true positive is the one I had already found by following a defect, so the
detector surfaced NOTHING new.**

## WHY IT FAILS, AND THE FAILURE IS THE INTERESTING PART

**Both false positives are scoping their OWN limits precisely, which is exactly the behaviour this
repo asks for.**

- `context_grounded_valence`: the phrase describes **one reserved parameter** (`prior_context`) of a
  convenience entrypoint. **The same docstring says `WIRED (2026-08-06)` further down**, and the
  module is imported by `situation_reader.py:130` and lazily by `word_acquisition_loop.py:221`.
- `parse_goal_extraction`: *"NOT wired **here**"* scopes to a single induction step the module
  deliberately does not cover.

> # 🔑 **A DOCSTRING THAT CAREFULLY STATES WHAT IT DOES *NOT* DO IS INDISTINGUISHABLE, TO A KEYWORD DETECTOR, FROM ONE ADMITTING AN UNFULFILLED PROMISE.**
> **So the flag fires hardest on the best-documented modules.** *A detector that punishes precise
> boundary-marking would train the archive out of the one habit that makes it auditable.*

## ⚠️ AND A SCOPING ERROR OF MY OWN, CAUGHT BEFORE IT TRAVELLED

**`115 not loaded` IS NOT `115 unwired`.** It is *"not loaded by a 60-sentence read plus one query"* --
**a LOWER BOUND on wiring, not a census.** `CLAUDE.md` documents the trap directly: `pos_tagger`,
`arc_parser` and `arc_labeler` are on the live path via imports **inside function bodies**, invisible
to any probe that does not exercise that path. `context_grounded_valence` is reached through exactly
such a chain.

🚫 **DO NOT QUOTE `115` AS AN UNWIRED COUNT.** The comparable prior figure is the audit's **`81`
registered `gate=WIRE` but not loaded**, which cross-references the registry rather than resting on
one probe.

## WHAT SURVIVES

- ✅ **`foundation_persistence` is genuinely unwired**, established independently: nothing on the live
  path calls `load_foundation`, and repo-wide **no caller passes `foundation_dir` at all**.
- ✅ **The live-closure probe reconciles with the prior audit (`36`)**, so the method is sound even
  though the conclusion I wanted from it is not.
- 🚫 **The tool was NOT built.** *Testing the signal cost one command; building first and discovering
  a 33% precision afterwards would have cost a tool, a self-test, and a wrong prioritisation of ~100
  organs.*

---

## TLDR

I had an idea for finding our most valuable unfinished work: look for parts of the system that
describe the problem they were built to fix, and check whether they were ever plugged in. One real
example suggested it.

I checked before building it. **Three modules matched, and two of them were false alarms** -- they
weren't confessing to being unplugged, they were carefully documenting which small piece of
themselves is out of scope. That's good practice, not a broken promise, and my detector would have
punished exactly the people doing it right.

So I'm not building it. The check cost one command; building first would have cost a tool and a
wrong ranking of about a hundred components.

I also caught myself about to report "115 unplugged parts". The honest number is "115 not used by
the specific small test I ran", which is a very different claim.

## QUESTIONS

None.

## NEXT STEPS

1. 🚫 **Do not re-propose the docstring-promise detector** without a way to tell module-scope from
   component-scope claims. Keyword matching cannot.
2. The real prioritisation question -- *which of the ~81 unwired organs to connect first* -- stays
   open and is not keyword-answerable; it needs reading each organ's cited evidence.
3. `foundation_persistence` remains the one confirmed case, and its brief
   (`notes/problems/substrate_never_resumes/`) already carries it.
