# End-to-end substrate trace: where 34,169 sentences become 386 facts

Run: `exp_e2e_trace_v1.py --mode full`, PID 35380 (the launch brief said 33620; the PID the run
itself wrote to `data/exp_e2e_trace_v1/_run_pid.txt` is 35380 -- trust the file). Completed
228/228 chunks, 1,653.96 s. All four artifacts written:
`metrics.json`, `key_subject_rows.json`, `pass_rows.json`, `pass_curve.jsonl`.

Config as run: shipped default. `readout=null`, `freeze_episode=false`, `anchor_pool=null`,
`definition_map=null`, `encoder=context_vector_masked (bag)`, `revive_terminal=true`,
N_DIM 2048, ARM_SEED 4201, CHUNK_SIZE 150, SCHEMA_THRESH 0.25, MIN_CONFIRM 4,
PBV_INFORMATIVE_MIN 0.30, PBV_COMMIT_STRENGTH 0.60, 887 known seed lemmas from 1,000 base-vocab
rows.

Every number below is off disk. **This cell scores nothing** -- it is a census of attrition. No
quality claim is made or licensed by it.

---

## 1. The instrumentation-neutrality gate: FAILS AS WRITTEN, AND THE TRACER IS NOT THE CAUSE

The gate required 384 facts / digest `836571fa99d5765d` / 24,949 refusals. Observed:

| | facts | digest16 | refusals | CLOSED_CLASS | BELOW_COMMIT | NO_HYPOTHESIS |
|---|---|---|---|---|---|---|
| reference (expected) | 384 | `836571fa99d5765d` | 24,949 | 247 | 21,240 | 3,462 |
| this run (observed) | 386 | `c5ebeacc3a7063b0` | 24,939 | 241 | 21,207 | 3,491 |

`W2_reference_reproduction.matches = false`.

**But the tracer is exonerated by an independent, tracer-free witness.** `exp_anchor_pool_
expansion_v1` arm `SMALL` (`anchor_pool=None`, i.e. the identical shipped default, a different
cell, no instrumentation of any kind, run 16:53Z the same day) produced **386 facts, digest
`c5ebeacc3a7063b0...`, 24,939 refusals, and the refusal split 241 / 21,207 / 3,491 -- every figure
bit-identical to this run.** Its own S4 regression gate recorded
`small_reproduces_reference: false` against the same 384 reference. Two processes, one
instrumented and one not, agree exactly; both disagree with the landed reference.

**The reference moved, not the measurement.** Timeline, all 2026-08-13, all off disk:

| time (Z) | artifact | facts | digest16 |
|---|---|---|---|
| 02:44 | `exp_grounding_quality_readout_v1` PBV_BASE | 384 | `836571fa99d5765d` |
| 05:42 | `exp_structured_comparator_v1` CONTROL | 384 | `836571fa99d5765d` |
| 14:14 | this trace (tracer ON) | 386 | `c5ebeacc3a7063b0` |
| 16:53 | `exp_anchor_pool_expansion_v1` SMALL (tracer-free) | 386 | `c5ebeacc3a7063b0` |

So the pipeline is bit-reproducible **across processes and across cells within a code version**,
and the version boundary sits between 05:42 and 14:14. The only live-path file changed in that
window is `hdlab/reading_grounding_loop.py` -- commit `525e24d68` (12:52, anchor_pool hook) and an
uncommitted working-tree edit (13:08, the definitional wire). `find hdlab -name '*.py' -newermt
'05:42' ! -newermt '16:53'` returns that one file and nothing else; the seed vocabulary
(`data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv`) has mtime 2026-07-18 and did
not move.

**Both edits are inert by inspection and the run record says they are not.** `git diff
0db7cfdaa 525e24d68` on the live path changes only the signature line (`anchor_pool` guarded by
`if anchor_pool is not None`); the definitional wire is guarded by `if definition_map:` in
`checkpoint`. Both ship a default-OFF self-test
(`_selftest_anchor_pool_is_off_by_default`, `_selftest_definitional_wire_is_off_by_default`), and
both self-tests pass on a small fixture -- the same shape of witness as W1 below, and the same
blind spot. **Two "byte-for-byte default-OFF" claims are contradicted by a 2-fact / 10-refusal
drift at full corpus scale, and neither self-test caught it.**

Unresolved, and the one open action: which of the two hooks moved the number. Closing it needs a
bisect run (one full pass, ~10-28 min) against 05:42-era code, which requires touching the working
tree and was therefore not done here.

Effect on the rest of this note: the drift is 2 facts in 386 (0.5%) and 10 refusals in 24,939
(0.04%). The attrition shape below is not materially affected. **The gate result must still be
carried loudly wherever the 384 figure is cited: `384 / 836571fa99d5765d` is stale-by-version as
of 2026-08-13 ~13:00Z, and two independent cells now say the shipped path yields 386 /
`c5ebeacc3a7063b0`.**

### W1 (secured earlier, carried verbatim)

> **W1 neutrality witness PASSED**: same 300-sentence slice tracer-ON vs OFF gives identical
> facts, digest `e859584d081c0cd1`, refusals, and PBV trajectory; tracer proved non-vacuous at
> 1,917 read-out calls.

W1 is upheld and is now corroborated at full scale by the tracer-free `SMALL` arm above, which is
the stronger witness: identical output from a different cell with no tracer at all.

---

## 2. The attrition curve

Units change between stages and the changes are load-bearing; each row states its unit.

| # | stage | unit | enter | leave | lost | % lost | reason(s) for the loss |
|---|---|---|---|---|---|---|---|
| 1 | input sentences | sentences | 34,169 | 33,839 | 330 | 1.0% | sentence had no content lemma |
| 1b | tokens -> content lemmas | tokens | 623,522 | 338,506 | 285,016 | 45.7% | 270,779 stopword / len<=2 / non-alpha; 14,237 duplicate lemma inside one sentence (`content_lemmas` is a set) |
| 2 | gap gate | lemma occurrences | 338,506 | 83,923 | 254,583 | **75.2%** | 123,346 seed-known (anchor accumulation only, never a target); 131,237 already-terminal library item; **0 from the gap detector saying "known"** |
| 2b | encoding | occurrences | 83,923 | 83,732 | 191 | 0.2% | all-zero context vector, SILENT `continue` |
| 2c | trace appended (`Library.flag`) | occurrences | 83,732 | 83,732 | 0 | 0% | -- |
| 3 | candidate pool | read-out calls | 89,676 | 89,675 | 1 | 0.001% | anchor field empty (silent self-return) |
| 4 | selection threshold | read-out calls | 89,676 | 32,456 | 57,220 | **63.8%** | argmax cosine below `PBV_INFORMATIVE_MIN=0.30` |
| 5 | consolidation eligibility | ITEM-PASSES | 1,373,320 | 52,186 | 1,321,134 | **96.2%** | 1,313,576 under `MIN_CONFIRM=4` exposures; 7,558 intervening-pass wait (no patience cost) |
| 5b | schema coherence | ITEM-PASSES | 52,186 | 25,325 | 26,861 | 51.5% | schema score below 0.25 (0 returned `None`) |
| 6 | admission gate (PBV) | ITEM-PASSES in, FACTS out | 25,325 | 386 | 24,939 | **98.5%** | 21,207 hypothesis below commit strength; 3,491 no standing hypothesis; 241 closed-class subject |
| 7 | store write | facts | 386 | 386 | 0 | 0% | no displacement, no lower-trust drop, no conflicting pair |

End-to-end, in the unit that matters: **16,812 distinct content lemmas seen, 16,507 eligible,
15,990 became library items, 386 grounded = 2.4% of items.** Item terminal fates: GROUNDED 386,
ESCALATED 7,082, PENDING 8,522. Exposures per item: median 3, p90 11, max 241, mean 5.24.

Cross-checks the cell asserts on itself and that hold: schema calls == eligible item-passes;
schema-OK == refusals + facts (25,325 = 24,939 + 386); 386 distinct subjects, 0 tautologies, 0
closed-class objects, 0 subject-relation pairs written twice.

## 3. The largest single drop

Three candidates, and the honest answer depends on the unit -- so all three are stated.

- **Largest absolute count:** stage 5, 1,321,134 item-passes. This number is unit-inflated: one
  library item is re-counted on every consolidation pass it is pending for (228 passes), which is
  how `consolidation_pass` itself works. It measures waiting, not rejection.
- **Largest drop in the stream unit (occurrences):** stage 2, 254,583 of 338,506 (75.2%). Also
  not a fault: 48% of it is seed vocabulary doing its job as anchor fuel and 52% is items already
  terminal.
- **Largest genuine, decision-driven drop: stage 6, the PBV admission gate -- 24,939 of 25,325
  item-passes rejected, 98.5%.** Everything reaching it has already cleared 4+ exposures and
  schema coherence 0.25. Within it, **`HYPOTHESIS_BELOW_COMMIT_STRENGTH` alone is 21,207 (85.0%
  of all refusals)**.

Stage 4 is the mechanism behind stage 6: 63.8% of read-outs never clear cosine 0.30, so the
hypothesis they would have confirmed never gets the evidence to reach 0.60. Final hypothesis
strength across the 9,918 items still holding one: median 0.50, p90 0.50, p95 0.75 -- only 654
items (6.6%) ever reach the 0.60 commit bar. **The system is not rejecting bad answers at stage 6;
it is failing to accumulate enough agreement to make any answer commit-worthy.**

## 4. Correct answer ABSENT vs PRESENT-BUT-NOT-SELECTED

Known-answer key: 1,353 subjects (the v5 definitional extraction, itself ~64% MEANINGFUL --
see limitations). Probe is read-only and live, at every read-out call for a key subject.

| bucket | n | share | meaning |
|---|---|---|---|
| **ABSENT** | **1,069** | **79.0%** | the correct object was never a scannable anchor at any read-out for this subject |
| PRESENT_NOT_ARGMAX | 233 | 17.2% | it was on the menu and lost |
| BANKED_OTHER | 39 | 2.9% | something else was banked |
| ARGMAX_NOT_BANKED | 12 | 0.9% | it won the argmax but was not banked |

- Answer available at least once: **253 of 1,353 (18.7%)**.
- Correct answer ever proposed as a hypothesis: **9 of 1,353 (0.7%)**.
- Rank of the correct answer when it *was* available (best rank per subject, n=253): median
  **20**, mean 57.5, p75 63, p90 180, p95 269, max 461.

This confirms `notes/downstream_bottleneck_trace_2026-08-13.md` at full scale and sharpens it:
**four out of five failures are unrepresentable, not mis-ranked.** The anchor pool finishes the
run at 1,171 anchors (1,000 eligible after the closed-class filter) against 16,812 distinct
lemmas seen -- **7% of the vocabulary the substrate read is expressible as a meaning.** Mean
scannable candidates per call 766 (p50 776, max 1,000).

Even among the 17.2% that were present, median rank 20 means the read-out is not close: fixing
ranking alone converts a minority of a minority.

## 5. Refusal reasons, with counts

24,939 refusals total (23,290 at chunk 201, which is what the earlier progress line showed):

| reason | n | share |
|---|---|---|
| `HYPOTHESIS_BELOW_COMMIT_STRENGTH` | 21,207 | 85.0% |
| `NO_STANDING_HYPOTHESIS` | 3,491 | 14.0% |
| `CLOSED_CLASS_SUBJECT` | 241 | 1.0% |

`TAUTOLOGY_NO_ANCHOR` and `CLOSED_CLASS_OBJECT` exist as reason codes and fired **zero** times --
the tautology and closed-class-object defects fixed on 08-12 are confirmed dead on this path
(0 tautologies, 0 closed-class objects among the 386 banked facts).

Note what the split says: 85% of refusals are items that HAD a hypothesis and could not raise it
to 0.60. Only 14% had nothing to say at all.

## 6. Timing by stage

Wall clock 1,653.96 s (27.6 min); 1,663.24 s including setup.

| phase | s | share of wall |
|---|---|---|
| **read phase** | **1,627.67** | **98.4%** |
| consolidation phase | 23.04 | 1.4% |
| instrumentation overhead (key probe + census) | 19.14 | 1.2% |

Inside the read phase (INCLUSIVE and NESTED -- these do not sum):

| stage | s | note |
|---|---|---|
| `stage2_gap` (`is_gap`) | 748.06 | 83,923 calls, ~8.9 ms/call -- the single largest live-path cost |
| `stage2c_flag_incl` (`Library.flag`) | 695.06 | contains propose + verify below |
| `stage6_verify_incl` | 397.59 | 49,320 calls |
| `stage6_propose_incl` | 294.49 | 40,356 calls |
| `stage34_select` (`canonicalize_fast`) | 410.28 | 89,676 calls, inside propose+verify |
| `stage2b_encode` | 171.87 | 207,269 calls |
| `stage5_schema` | 2.21 | 52,186 calls |
| `stage1_input` / `stage5_census` / `stage7_store` | 1.90 / 1.28 / 0.29 | negligible |

READ dominates by a factor of 70 over consolidation. Per-chunk cost falls 26 s -> 5.6 s across the
run as `is_gap` novelty calls memoise (secured earlier; `pass_curve.jsonl` per-chunk
`read_s` / `consolidation_s`, consolidation 0.00-0.14 s/chunk vs 5-26 s read).

**The most expensive thing the substrate does is ask "have I seen this word before" (748 s, 45% of
the read phase). The actual meaning decision -- the matvec over the anchor matrix -- costs 410 s,
and the store write costs 0.29 s.**

## 7. Every stage that silently returns empty rather than failing loudly

Eight sites in the read path, with live counts from this run:

| site | behaviour | count |
|---|---|---|
| `reading_grounding_loop.py:1076 process_sentence` | all-zero context vector -> `continue`; occurrence dropped with no counter, no log line, no refusal row | 191 |
| `reading_grounding_loop.py:657 canonicalize_fast` | empty anchor field -> returns `(target, 0.0)`, which the caller reads as "uninformative encounter". **An EMPTY POOL and a BELOW-THRESHOLD ARGMAX are the same return value.** | 1 |
| `reading_grounding_loop.py:663 canonicalize_fast` | no scannable anchor (mask all False) -> same indistinguishable self-return | 0 |
| `reading_grounding_loop.py:668 canonicalize_fast` | zero-norm query profile -> same indistinguishable self-return | 0 |
| **`grounding_acquisition_loop.py:331 Library._propose`** | **`propose_fn` returned None -> `return` with NO `hypothesis_log` entry. An encounter that failed to propose leaves no trace in the audit trail; only failed VERIFY is counted (as `Hypothesis.n_uninformative`).** | **24,494** |
| `grounding_acquisition_loop.py:524 consolidation_pass` | `schema_score is None` -> `continue`, no patience cost, nothing recorded | 0 |
| `grounding_acquisition_loop.py:126 context_vector` | window with no content word -> all-zero vector returned as if it were a representation; the caller's `np.any` guard is the only thing that notices | 395 |
| `reading_grounding_loop.py ReadingLoopState.refusals` | the refusal ledger is never written to disk by the loop itself; only a calling cell that chooses to persist it keeps the per-lemma reasons | 24,939 |

The dominant one is the fifth: **24,494 of 40,356 propose calls (60.7%) returned None and left no
audit row.** The glass-box trail records what was verified, never what could not be proposed.

Two further silent-empty findings, secured earlier and carried verbatim:

> - **41.8% of the glass-box evidence trail is unrecoverable.** On `arm_PBV_BASE_provenance.json`:
>   184 of 384 banked facts carry fewer evidence rows than exposures (1,750 recorded vs 3,009
>   exposures), and the short set is exactly the 184 revived items. Cause: `checkpoint` pops
>   `state.evidence[lemma]` on ESCALATION (`reading_grounding_loop.py:1382`) while
>   `revive_terminal=True` re-opens the item; pre-escalation sentences are lost while
>   `n_exposures` still counts them.
> - **`SENSE_MATCH_THRESH = 0.45` is dead on the live PBV path** -- every read-out call uses
>   `PBV_INFORMATIVE_MIN = 0.30`.

The `SENSE_MATCH_THRESH` finding is confirmed by the cosine histogram: 0.45 would have admitted
only 4,885 of 89,676 calls (5.4%); the live 0.30 admits 32,456 (36.2%). A constant that reads like
the operating threshold, is named as such in the docstring, and is not the operating threshold, is
the same defect class as the eight rows above -- a value that misleads silently rather than
failing.

And one more, found in this run's own gate: **`_selftest_anchor_pool_is_off_by_default` and
`_selftest_definitional_wire_is_off_by_default` both PASS on their fixtures while the full-corpus
output moved by 2 facts** (sec 1). A default-OFF self-test on a hand-built fixture is not a
neutrality witness at scale.

---

## 8. Cross-check against `notes/brain_fidelity_subsystems_2026-08-13.md`

That note concluded the deepest fault is below the read-out: the atom basis is random, fixed and
dense, so all concepts start equidistant and only first-order co-occurrence can form.

**Verdict: the attrition data SUPPORTS the geometric half of the claim and CONTRADICTS its
ranking as the deepest fault. The contradiction is the more valuable half.**

**Where it is supported (the 21% that reach the comparison):**

- The argmax cosine distribution is one narrow blob with no separation: p01 0.148, p05 0.169,
  p25 0.211, **p50 0.273**, p75 0.342, p95 0.461, mean 0.290. Of 89,676 calls only 163 (0.18%)
  exceed 0.85 and only 1,742 (1.9%) exceed 0.60. The operating threshold 0.30 cuts through the
  **median** of the distribution -- the informative/uninformative decision is slicing a unimodal
  blob, not separating signal from background. That is exactly what equidistant dense random
  atoms predict.
- Schema coherence behaves identically: median 0.239 against a threshold of 0.25, mean 0.280,
  p05 -0.020. The second gate also sits at the median of its own blob.
- Winners concentrate on high-frequency generic anchors: `people` 1,097 wins, `new` 593, `world`
  378, `know` 344, `big` 337 -- 1,097 of 32,456 cleared calls (3.4%) go to one anchor. Banked
  objects concentrate the same way (`people` 13, `york` 7, `driving`/`talking`/`dioxide`/`stem`
  6). Cosine tracking raw co-occurrence mass with frequent words is the first-order-only
  signature the note predicts.

**Where it is contradicted (the 79% that never reach the comparison):**

- **1,069 of 1,353 key subjects fail because the correct object was never in the anchor matrix at
  all.** No change to the basis -- sparse, learned, structured, whatever -- can make the argmax
  return a vector that is not in the matrix. An absent candidate is a pool-composition fault, and
  it is 4x more common than the ranking fault the basis argument addresses.
- The pool is small by construction, not by geometry: anchors enter at exactly two sites (seed
  vocabulary and lemmas this same loop already grounded), finishing at 1,171 anchors / 1,000
  eligible against 16,812 lemmas read.
- Direct evidence from an independent cell the same day: `exp_anchor_pool_expansion_v1` raises the
  anchor matrix from 1,171 to 12,792 rows -- **basis unchanged, encoder unchanged, threshold
  unchanged** -- and facts go **386 -> 600 (+55%)**. A pure availability intervention beats
  anything the basis argument has produced. (Its own limitation stands: LARGE's banked population
  is not subset-comparable to SMALL's, and no quality claim is made from it here.)

**Synthesis.** Both faults are real and they are stacked, but they bind in a fixed order:
availability first, geometry second. Fixing the basis while the pool holds 7% of the vocabulary
buys the ranking of the 18.7% of subjects whose answer is on the menu at all. Fixing availability
without fixing the basis raises the ceiling but leaves median rank 20 among available answers, so
it will saturate. The brain-fidelity note names the fault that will bind **second**; on this run's
numbers it is not the one binding **now**. A read-out cannot select what was never encoded as a
candidate -- and 79% of the time, it was not.

---

## Limitations (carried from the cell, unedited in substance)

1. This is a CENSUS. No fact is scored for correctness anywhere in this cell.
2. The known-answer key is the v5 definitional extraction, itself ~64% MEANINGFUL, so the
   ABSENT / PRESENT_NOT_ARGMAX split is structural: "the key's object was not on the menu" does
   not mean "no correct answer was on the menu". The 79% figure is a statement about the key's
   objects, not proof that nothing correct was available.
3. Stage-5 counts are ITEM-PASSES, not distinct items.
4. Timing is INCLUSIVE and nested; per-stage seconds do not sum to wall clock.
5. The stage-2 split between "terminal skip" and "gap-detector says known" is derived
   arithmetically (non-seed occurrences minus `is_gap` calls); exact given that
   `process_sentence`'s only other exit before `is_gap` is the terminal-status check.
6. One configuration only: the shipped default. F1/F3, the structural encoder, the anchor pool and
   the definitional wire are all OFF, as in production.
7. **The W2 gate FAILED and the 384 reference is stale-by-version (sec 1). The specific commit
   that moved it is not identified; that requires a bisect run not performed here.**

## Provenance

- `data/exp_e2e_trace_v1/{metrics.json,key_subject_rows.json,pass_rows.json,pass_curve.jsonl,_detached_run.log}`
- `data/exp_grounding_quality_readout_v1/metrics.json` (`objective_metrics.PBV_BASE`, 02:44Z)
- `data/exp_structured_comparator_v1/metrics.json` (`objective_metrics.CONTROL`, 05:42Z)
- `data/exp_anchor_pool_expansion_v1/metrics.json` (`objective_metrics.SMALL` and
  `structural_gates.S4_small_regression`, 16:53Z)
- `notes/downstream_bottleneck_trace_2026-08-13.md`, `notes/brain_fidelity_subsystems_2026-08-13.md`

Nothing was wired by this work; `hdlab/` is unmodified by this cell and no commit was made.
