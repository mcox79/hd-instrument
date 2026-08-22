---
problem: harness_cannot_recompute
status: SOLVED
bar: "A re-run through the new path must be able to FAIL. That is the whole deliverable." -- the DECIDING control (corrupt one input, re-run through the fresh path, verdict CHANGES) and the NEGATIVE control (an unmodified fresh re-run reproduces the landed number), with units_before/after/elapsed passed through tools.reproduction_check.classify_run, nothing deleted, and the original output directory byte-identical afterwards.
result: A re-run through the proposed fresh path CAN FAIL. Deciding control flips HARD_PASS -> HARD_FAIL (corrupt one input, fresh recompute); negative control reproduces HARD_PASS (unmodified fresh recompute, RECOMPUTED, 10/10 units); the naive incident re-run REPLAYED (0/10 units, 0.000s, verdict unchanged). Proven live in a separate process on the real filesystem AND hermetically. Real-archive breadth: 60/60 stratified sampled landed cells (1..12,137 units) classify REPLAYED, every dir byte-identical (read-only).
floor: The naive-replay baseline the fresh path must beat -- classify_run = REPLAYED_NOT_A_REPRODUCTION (0 units computed, elapsed 0.000s, verdict returned unchanged with NO work); the fresh path beats it with RECOMPUTED (all units recomputed). Real-cell floor: 60/60 sampled landed cells classify REPLAYED; strongest counting of skipped work exercised = 12,137 units in one cell.
controls: DECIDING/positive -- corrupt one input (signal_strength 3.0->0.0, i.e. remove the signal dimension's information), fresh re-run -> verdict FLIPS HARD_PASS->HARD_FAIL. NEGATIVE -- unmodified fresh re-run excludes nothing -> RECOMPUTED, reproduces HARD_PASS. INFO-FREE arm -- F_CHANCE reads a pure-noise coordinate, lands ~chance, LOSES to A_SIGNAL (excludes the signal). BYTE-IDENTICAL -- landed units.jsonl AND metrics.json sha256 unchanged after every fresh re-run (the fresh path is excluded from touching base); read-only sample exercise mutated 0 of 60 dirs. NAIVE re-run rewrites base/metrics.json volatile fields (disclosed hazard, excluded from the fresh path).
files_changed: experiments/fresh_recompute.py (proposed fix, prototyped standalone -- NOT landed into the shared harness); experiments/exp_recompute_falsification_demo_v1.py (falsification demo cell); experiments/exercise_replay_sample.py (real-sample exerciser); verification/test_recompute_can_fail.py (scaffold-free witness); notes/problems/harness_cannot_recompute/SOLVED.md. Artifacts left on disk (safe to remove): data/exp_recompute_falsification_demo_v1/, data/exp_recompute_falsification_demo_v1__fresh_nc/, data/_harness_cannot_recompute_replay_sample.json. NO change made to hdlab/, experiments/_seed_checkpoint.py, or tools/exp_checkpoint.py -- the exact diff to those is proposed below for the strategy session to land.
reverify: cd d:/AI/hd-instrument && .venv/Scripts/python.exe verification/test_recompute_can_fail.py
---

# A LANDED CELL CANNOT BE FALSIFIED BY RE-RUNNING IT -- SOLVED (mechanism proven; diff proposed, not landed)

## What the bar asked, and what it got

The deliverable was one thing: **a way for the harness to recompute into a fresh output directory
without deleting anything, and proof that a re-run through it can actually FAIL.** That is met.

`verification/test_recompute_can_fail.py` (the reverify command) asserts, and
`experiments/exp_recompute_falsification_demo_v1.py --self-test` prints:

```
step                 classify_run.status          u_before  u_after  elapsed   verdict
LAND                 RECOMPUTED                          0       10   0.063s   HARD_PASS
NAIVE_RERUN          REPLAYED_NOT_A_REPRODUCTION        10       10   0.004s   HARD_PASS   <- the incident
FRESH_SAME_INPUT     RECOMPUTED                          0       10   0.026s   HARD_PASS   <- NEGATIVE control: reproduces
FRESH_CORRUPT_INPUT  RECOMPUTED                          0       10   0.065s   HARD_FAIL   <- DECIDING control: FLIPS
```

Live, in three separate processes, on the real filesystem (not a tempdir):

```
RUN 1 land   : RECOMPUTED (u 0->10)  HARD_PASS
RUN 2 re-run : REPLAYED_NOT_A_REPRODUCTION (u 10->10, 0.000s)  HARD_PASS      <- replays, does no work
RUN 3 fresh  : RECOMPUTED (u 0->10) into ...__fresh_nc         HARD_PASS
landed dir units.jsonl + metrics.json sha256 IDENTICAL before and after RUN 3 (fresh path never touched it)
```

So: the naive re-run is the incident (skips every unit, returns the verdict with no work); the fresh
re-run **recomputes**; an unmodified fresh re-run **reproduces** the verdict (negative control); a
fresh re-run with one input corrupted **changes** the verdict (deciding control) -- which is the
whole point, a re-run that can disconfirm. Every run is classified through the real
`tools.reproduction_check.classify_run`, and the landed directory is byte-identical throughout.

## The mechanism (prototyped in `experiments/fresh_recompute.py`)

`completed_units(out_dir)` returns the set of units already in `<out_dir>/units.jsonl`; a cell skips
any unit already in that set. So the only lever that turns a replay into a recompute, **without
deleting** the checkpoints (separately forbidden and auto-denied here), is to point the cell at a
**different, empty output directory**. `fresh_run_output_dir(base, tag)` does exactly that:

- env `HDI_FRESH_RUN` unset -> `base` returned unchanged (backward-compatible; on-disk behaviour is
  byte-identical to today for every existing cell);
- `HDI_FRESH_RUN=<tag>` set -> `<base>__fresh_<tag>`, a NEW sibling. `completed_units()` reads the
  empty sibling, the cell recomputes every unit, and `record_unit()` / `write_metrics()` write into
  the sibling. **The landed dir is never opened for writing, so nothing is deleted or clobbered --
  byte-identity is by construction, not by cleanup.**

This is the same shape as the run-mode redirects already in `experiments/_seed_checkpoint.get_output_dir`
(SH-4 double-prefix, SH-5 `--self-test`/`--smoke` argv, SH-6 resolved self_test mode). It is SH-7.

## THE DISK OUTRANKED THE BRIEF in five places -- read these before quoting the brief

1. **Census drift.** The brief says `399 / 7,868`. On disk today it is `400 / 7,871` (a pre-existing
   drift; these notes go stale within hours). After my work it reads `402` -- because my two demo
   output dirs now carry `units.jsonl` and count as replay cells themselves. Disclosed; both are in
   `files_changed` and are safe to remove.
2. **`reproduction_check.unit_count` counts LINES, not unique keys.** 3 of my 60 sampled cells had
   `unit_key`s appended more than once (e.g. `exp_grounding_readout_known_answer_v1_SMOKE`: 24 lines,
   6 unique keys). `completed_units` (a set) and `load_units` (a dict) dedup, so the cell still skips
   correctly and replays -- but the census's "units that would be skipped" is a slight UPPER BOUND
   for dup-cells, not an exact count. Conclusion unaffected.
3. **Unit count is a poor cost proxy; the brief's "12,137 units is not free" worry is backwards.**
   Priced from each cell's own landed `elapsed_s` (a fresh recompute redoes exactly the original
   work): the 12,137-unit cell recomputes in **123 s (2.0 min)**, while a 9,820-unit cell takes
   **25.7 min** and a 619-unit cell takes **13.4 min**. Recomputing ALL 400 fresh sums to **~39.3 h**
   of compute (26 cells carry no numeric elapsed). The expensive cells are not the big-unit ones.
4. **A single-point fix at `get_output_dir` covers only ~80 of the 400 (20%), not all of them.** By
   source grep of the 400 replay cells: **80 route output through `get_output_dir`** (the SH-7 fix
   covers these for free, units and metrics both), **264 hold a bare module-level `OUTPUT_DIR`**
   (e.g. `exp_cleanup_basin_conditional_v1`: `OUT_DIR_FULL = os.path.join(REPO_ROOT, "data",
   ANCHOR_NAME)`), and **56 sources were not located** (mostly `_smoke`/`_reduced` siblings). The
   diagnosis note's own words -- "the fix touches the cell harness across every experiment" -- are
   right, and this quantifies the cost: 264 one-line cell edits, not one function.
5. **A hazard the brief did not name: the naive re-run REWRITES the landed `metrics.json`.** Even
   though it recomputes zero science, it re-emits `metrics.json` with new `elapsed_s`/timestamp. So a
   naive "reproduction" both proves nothing AND silently mutates the landed metrics file. The fresh
   path avoids this entirely (it writes to the sibling). Measured in the self-test
   (`naive_rewrote_metrics_json: True`).

## THE PROPOSED DIFF (for the strategy session to land; I did not touch the shared harness -- Q111)

**Primary, clean, one point, covers the 80 `get_output_dir` cells for free.** In
`experiments/_seed_checkpoint.py`, add two module constants and one redirect at the end of
`get_output_dir`, immediately before `return _REPO / "data" / f"exp_{name}"`:

```python
_FRESH_ENV = "HDI_FRESH_RUN"      # set to a short tag to force a fresh recompute into a sibling
_FRESH_MARKER = "__fresh_"
...
    base = _REPO / "data" / f"exp_{name}"
    # SH-7 fresh-recompute isolation (harness_cannot_recompute). HDI_FRESH_RUN=<tag> -> a NEW sibling
    # so completed_units() is empty and the cell RECOMPUTES; the landed dir is never written, so it
    # stays byte-identical. Same shape as SH-4/5/6. Unset env -> base unchanged (backward-compatible).
    _tag = os.environ.get(_FRESH_ENV, "").strip()
    if _tag and not base.name.endswith(_FRESH_MARKER + _tag):
        base = base.with_name(base.name + _FRESH_MARKER + _tag)
    return base
```

**For the 264 bare-`OUTPUT_DIR` cells:** a mechanical one-line migration each -- wrap the bare
constant at the point it is assigned:

```python
from experiments.fresh_recompute import fresh_run_output_dir
# where a cell has:   OUTPUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
# make it:            OUTPUT_DIR = fresh_run_output_dir(os.path.join(REPO_ROOT, "data", ANCHOR_NAME))
```

This is scriptable but is 264 edits and touches in-flight-run-shaped code, so it is the strategy
session's call whether to migrate all, migrate on demand, or leave the bare cells un-recomputable for
now (they simply keep replaying until migrated). **Recommended:** land SH-7 now (zero risk, covers 80),
add a tiny driver `tools/reproduce.py <cell>` that sets `HDI_FRESH_RUN=<tag>`, runs the cell, and
reports `classify_run` on the fresh sibling; migrate bare cells lazily the first time one is actually
being re-verified. **Risk of that recommendation:** the 80/264/56 split is a source-grep heuristic
(an aliased import or an unusual path construction could be miscounted), so the migration count could
move; the SH-7 mechanism itself is unaffected by any miscount.

**Rejected alternative, and why:** an env-var in `tools/exp_checkpoint.py` that makes
`completed_units()` return empty and redirects `record_unit()` would force a recompute for all 400
without per-cell edits -- BUT it does not redirect `metrics.json` (each cell writes that to its own
`OUTPUT_DIR`), so a bare cell would overwrite its landed `metrics.json`. That breaks the
byte-identity guarantee. The output-directory redirect is the only lever that moves both the units
and the metrics together, which is why the fix lives at the directory, not at the shard.

## Is this brain-foundational? (asked twice by the owner -- answered honestly)

**Mostly no, and I will not dress it up.** The brief itself ranks this LAST of 8 because it "improves
our ability to CHECK, not the system itself." The fix is plumbing; per the standing directive,
measurement and guard-writing are hygiene, not the mission.

**There is one genuine, non-retrofitted brain principle it embodies, and I built the design around
it rather than bolting it on:** the distinction between **replay** and **reconstruction**. A
checkpoint replay returns a stored answer without re-deriving it from inputs -- pattern-completion
recall from a consolidated engram, as opposed to re-encoding from the stimulus. That is *the same*
distinction the substrate's own capability claims turn on: the slug I closed just before this one
(`flat_store_destroys_the_code`) failed exactly here -- an addressed store scored 0.9954 at the exact
key (replay) and collapsed to 0.1399 under a partial cue (reconstruction). A harness that can say
"this number was replayed, not recomputed" is the meta-level instrument for that confound. **The
analogy stops there:** this is a verification tool, not a pinned brain mechanism, and I say so in the
code.

## What I did NOT establish

- **I did not land the fix.** Per board Q111 the strategy session owns the live/shared harness; this
  is a prototype (`experiments/fresh_recompute.py`) plus the exact diff above.
- **I did not run all 400 cells end-to-end as separate processes.** I ran 1 end-to-end (my demo cell,
  live, 3 processes) and exercised 60 real landed cells read-only through the actual replay-path
  functions (`completed_units`/`load_units`). The 60-cell result rests on the determinism contract
  CLAUDE.md already mandates (a resumed run regenerates exactly the recorded keys); that dependency
  is stated in `exercise_replay_sample.py`.
- **I did not verify the 264 bare cells each migrate cleanly.** The one-line change is mechanical but
  unchecked per-cell.
- **Nothing here says any landed NUMBER is wrong** (per the brief's DO NOT QUOTE): `400/7,871` counts
  cells that cannot be re-verified by re-running, not cells that are incorrect; `elapsed 0.0s` is the
  harness resuming as `CLAUDE.md` mandates, not a broken cell.

## What I would withdraw first if it turned out to be wrong

The **80 / 264 / 56 split**. It is a heuristic source grep; if it is off, the *pricing* of the
per-cell migration moves. It does not touch the mechanism proof -- the deciding control, the negative
control, and the byte-identity all stand independently of how many cells the single-point fix covers.

## TLDR (plain language)

Re-running a finished experiment here doesn't actually redo it -- it reads back its saved answer and
prints the same result in about no time, so "I re-ran it and it matched" currently proves nothing. I
built and proved a switch that makes a re-run genuinely redo the work in a brand-new folder, touching
none of the saved data. Proof it works both ways: with the switch on and the inputs unchanged, the
result comes back the same (good); with the switch on and one input deliberately broken, the result
correctly changes from pass to fail -- so a re-run can now catch a real problem, which was the whole
ask. I confirmed 60 real saved experiments across the archive all currently replay, and none were
altered by my checking. I also found the clean version of the switch only auto-covers about 80 of the
~400 affected experiments; the other ~264 each need a tiny one-line edit, and I wrote down exactly
what it is. Recomputing everything from scratch would take about 39 hours of compute total -- and,
against the brief's guess, the experiment with the most saved pieces is actually one of the cheapest
(2 minutes). I did not switch anything on in the live system; that hand-off is the strategy session's.

## Questions

None.

## Next steps (for the strategy session, which owns integration)

1. Re-verify with the `reverify` command above, then land the SH-7 block in
   `experiments/_seed_checkpoint.get_output_dir` (zero risk; env-unset behaviour is byte-identical).
2. Add a thin `tools/reproduce.py <cell>` driver that sets `HDI_FRESH_RUN=<tag>`, runs the cell, and
   reports `classify_run` on the fresh sibling -- so an operator gets a one-command falsifiable re-run.
3. Decide the policy for the 264 bare-`OUTPUT_DIR` cells: migrate all (scriptable, 264 one-liners),
   migrate lazily on first re-verify, or leave un-recomputable for now. This is a priced decision, not
   an open-ended worry.
4. Clean up my throwaway artifacts if desired (`data/exp_recompute_falsification_demo_v1/`,
   `.../__fresh_nc/`, `data/_harness_cannot_recompute_replay_sample.json`).


---

## INTEGRATED_BY_STRATEGY 2026-08-22

**Re-verified on the artifact, not by re-running the pipeline** (a re-run shares the pipeline's
bugs): `verification/test_recompute_can_fail.py` RESULT PASS in my hands. The submission's
self-declared weakest claim -- the `80 / 264 / 56` split -- I recounted independently from disk
and got `87 / 275 / 59` of 421: same proportions, so the thing they were least sure of held.

**LANDED (`ed9ce6273`):** the SH-7 block in `experiments/_seed_checkpoint.get_output_dir`, exactly
as proposed. The load-bearing control is the NEGATIVE one and it is now a witness rather than a
comment -- env unset must resolve to byte-identical paths, or every landed directory in the repo
is silently orphaned with nothing erroring (`verification/test_fresh_recompute_redirect.py` 6/6,
and I injected the bug to confirm the guard FIRES).

**ALSO LANDED (`62796844a`):** `tools/reproduce.py`, the one-command driver they recommended. It
REFUSES a cell that cannot be redirected, because running one anyway would write into the LANDED
directory while reporting a 'reproduction'.

**AND THEIR FINDING AGAINST MY OWN TOOL WAS CONFIRMED AT FULL SCALE AND FIXED (`6d5f480d1`):**
`unit_count` counted LINES, not distinct units. Archive-wide, `21` of `421` cells repeat a key --
`70,644` lines against `70,191` distinct, a `0.65%` overstatement. *Deflating it: the census
headline counts CELLS and no cell crosses the replay boundary; only the secondary units total
moves, by 453.*

**NOT DONE, and it is a priced decision rather than an open worry:** the `275` bare-`OUTPUT_DIR`
cells each need a one-line wrap. Until then they keep replaying, and `tools/reproduce.py --check`
says so per cell.
