# C12 (gap index) and C13 (validation harness re-run) -- fresh on-disk re-check, hdi_testbed, 2026-08-15 ~17:45Z

Both dispatch-queue items pointed at `notes/STATUS.md` "OTHER PATH STATE" line 47-48 ("PHASE DIAGRAM
closed... OPEN (C13 re-run, C12 gap index NOT BUILT...)") which in turn points to `STATUS_LESSONS.md`
"OPEN THREADS (older)". That numbered list (4 items: encoder-swap uncommitted, parser UAS unmeasured,
42% glass-box trail unrecoverable, no post-landing import check) does NOT actually contain C12/C13 --
the labeled C12/C13 entries live one section earlier, under `STATUS_LESSONS.md` "CORRECTIONS TO PRIOR
CLAIMS -- added 2026-08-14" (lines 816-834). Flagging this pointer mismatch for whoever next edits
`STATUS.md` line 48's "LESSONS 'OPEN THREADS (older)'" citation -- it should cite "CORRECTIONS TO
PRIOR CLAIMS" instead. Not fixing it myself: `notes/STATUS.md` is DO-NOT-TOUCH this session.

## C12 -- sub-linear gap index: RE-VERIFIED STILL NOT BUILT

`STATUS_LESSONS.md` C12 correction says the design doc is `notes/research_sublinear_gap_detector_
cleanup_shard_dg_ca3_design_2026-08-12.md` (not the `_08-14` filename some other doc cited) and that
its build target `hdlab/sharded_gap_index.py` does not exist.

Fresh disk check (this session, not trusting the 08-14 note blindly):
- `hdlab/sharded_gap_index.py` -- **does not exist** (`ls` confirms `No such file or directory`).
- `find hdlab -iname "*gap_index*" -o -iname "*sharded*"` -- only hit is an unrelated module,
  `hdlab/selection_weighted_sharded_typer.py` (a K-way classifier, explicitly ruled out as the wrong
  problem shape by the design doc itself, section "Considered and NOT reusable").
- **Confirmed: still genuinely NOT BUILT**, current as of this check.

**No new design needed.** The 2026-08-12 design doc already IS a complete, ready-to-dispatch build
spec (375 lines): banked-work audit (what's reusable vs not, with reasons), brain-fidelity design,
a numbered CONCRETE BUILD SPEC section (`## (c)`, lines 192-255: sharding key = `(relation,
_sr_key_bytes)` two-tier exact hash, incremental per-bucket maintenance replacing full-rebuild
`refresh()`, a CAN-FAIL correctness invariant against `GapDetector`'s existing 6 self-tests, a
throughput target, explicit do-not-touch list), and a VERIFICATION PLAN section (`## (d)`, starts
line 256). This is genuinely handoff-ready for `hdi_exp_dev` as-is -- no further scoping pass
required. Item 0 in the build spec ("flip `use_index=True` on every live `HDFactStore` construction")
is called out as a free, zero-risk, do-first sub-step, separable from the main build.

## C13 -- grounding-quality validation harness re-run: RE-VERIFIED STILL OPEN, SCOPED BELOW

`STATUS_LESSONS.md` C13 correction: the claim "the validation harness FULL run never reported" is
WRONG -- a full run exists (`data/exp_foundation_validation_harness_v1/metrics.json`, `ts_iso`
2026-08-12T14:27:19Z, verdict `HARD_PASS_foundation_validated`). What is actually owed is **"a
re-run against the current foundation with floor arms, not a first run."**

Fresh disk re-check (this session):
- Only one `exp_foundation_validation_harness_v1*` result set exists on disk (`_selftest`, `_smoke`,
  and the full run) -- no newer/`_v2` variant. `metrics.json` still shows the same `ts_iso`
  2026-08-12T14:27:19.938042+00:00, `run_mode: full`, no `arms` field at all. **Confirmed: the
  re-run has NOT happened; still genuinely open.**
- The foundation it validated is STALE relative to what exists now: `data/foundation/` mtimes show
  `reading_grounding_v4_parsefix` (Aug 12 15:56) and `reading_grounding_v5_termboundary` (Aug 12
  16:29) were both written AFTER the 14:27 validation run. The harness validated an earlier
  snapshot, not the current one -- independently corroborates why a re-run (not just a re-read) is
  needed.
- Context that motivates it further (not re-derived here, cited from MEMORY.md banner /
  `STATUS.md` C10): the original run's self-tautology framing was later found to be an ELIGIBILITY
  BUG (live tautology rate 0%, not 65.7%), so the original HARD_PASS's own internal accounting has
  since moved -- another reason the existing 08-12 result cannot stand in for a current-state
  validation.

### Scope for the re-run (design only -- NOT launched this pass)

No existing design doc for "validation harness + floor arms" was found (checked via
`director_kb_query.py --filename-contains validation_harness`, top hits are the same C13 correction
note, an unrelated wiring note, and the original 08-12 landed-VET note -- no re-run design exists).
Scoping it now so the next `hdi_exp_dev` dispatch has a concrete brief:

1. **Point `--foundation-dir` at the current foundation**, not the frozen 08-12 snapshot. Confirm
   with whoever owns `data/foundation/` which of `reading_grounding_v5_termboundary` or a later
   snapshot is the one considered "current" before dispatch (this session did not enumerate beyond
   v5; a newer snapshot may exist by the time this is picked up -- re-check, don't trust this note).
2. **Add floor arms to each of the three claims**, per the standing gate rule ("a gate is a
   CI-separated margin above max(orthographic, frequency, scramble) on the identical scorer/n/pool/
   gold -- never a bare absolute number", `MEMORY.md`):
   - Claim1 (correctness, `run_claim1`, co-occurrence check): add a scrambled-store control (the
     harness already has `build_scrambled_store` used by claim3 -- reuse it for claim1 too) so
     HARD_PASS on claim1 can't be earned by a store with no real correctness signal.
   - Claim2 (coherence, `run_claim2`, `cohesion_gap` clustering): the function signature already
     takes an `rng` for a null/random comparison (`cohesion_gap(clusters, rng, ...)`) -- confirm at
     build time whether that null is already a proper floor or needs strengthening to match the
     "strongest floor must actually be run" standard from the orthographic-floor-vet lesson.
   - Claim3 (can-reason, two-hop chains): already has mechanism/ablation/scrambled prediction arrays
     per the file's own header comment ("claim3 mechanism/ablation/scrambled prediction arrays
     hashed") -- verify these are genuine floors and not just presence-checks.
3. **HARD_PASS bands must sit strictly above the floor**, matching the harness's own stated design
   principle at the top of the file ("HARD_PASS strictly above floor (explicit gap margins, not
   at-floor)") -- confirm this principle, already declared in the file's own docstring, is actually
   enforced per-claim once floor arms are wired in, not just declared.
4. This is scoping only. Per this dispatch's brief, the actual build/dispatch is `hdi_exp_dev`'s job,
   not this pass's.

## Files referenced (read-only, not modified)
- `notes/STATUS.md` (read only, lines 44-49)
- `notes/STATUS_LESSONS.md` (read only, lines 723-935)
- `notes/research_sublinear_gap_detector_cleanup_shard_dg_ca3_design_2026-08-12.md` (read only)
- `experiments/exp_foundation_validation_harness_v1.py` (read only, header + function list)
- `data/exp_foundation_validation_harness_v1/metrics.json` (read only)
- `data/foundation/*` (read only, mtimes only, per this session's READ-ONLY constraint)
