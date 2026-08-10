# Pre-reg: crutch-fade BANK->native promotion connector + Test A (2026-08-10)

Anchor: `crutch_fade_bank_native_promotion_test_a_v1`
Cell: `experiments/exp_crutch_fade_bank_native_promotion_test_a_v1.py`
Engine changes: `hdlab/grounding_acquisition_loop.py::consolidation_pass` (new optional
`native_store` / `promote_min_exposure` / `promote_min_consistency` kwargs; default-None preserves
prior behavior byte-for-byte). Target native store: `hdlab/hd_fact_store.py::HDFactStore` (unmodified).

Director task: build the FIRST, cheapest, most-decisive precondition of the crutch-that-fades
architecture -- wire BANK to PROMOTE confirmed knowledge into the native fact store, gated by the
already-computed exposure + consistency signals, then run a synthetic-mechanism TEST A that is
HARD on the guard (inconsistent items must never promote).

Drills this build composes (read in full, not re-derived): `notes/research_crutch_fade_loop_owned_
organ_wiring_2026-08-10.md` (DRILL 3, names the connector + the flat-overlay problem),
`notes/research_brain_scaffolding_that_fades_2026-08-10.md` (DRILL 2, names the fade literature --
Fitts & Posner 1967 staged transfer, Logan 1988 instance theory, Schneider & Shiffrin 1977
consistent-mapping -- and the exact Test A design this cell operationalizes), `notes/research_crutch_
design_and_generalization_2026-08-10.md` (DRILL 1, names hd_fact_store's SOURCE/TRUST binding as the
literal fade-representation target).

Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring): `tools/substrate_query.sh
"crutch fade acquisition loop bank promote native fact store hd_fact_store trust weighted exposure
consistency"` -> top hit cosine=0.417 is `hd_fact_store` itself (the target organ -- expected, not a
duplicate). No prior cell found that wires grounding_acquisition_loop's BANK step to hd_fact_store or
that tests exposure/consistency-gated overlay->native promotion. Genuinely novel wiring, not a
rediscovery.

## What this is (and is not)

A MECHANISM test on controlled, synthetic confirmations -- not a capability claim, not run against
real narrative text. The question is narrow and load-bearing: can a confirmed item mechanically
migrate overlay -> native when (and only when) it is both repeatedly AND consistently confirmed? If
this fails, the whole crutch-that-fades architecture is dead before any benchmark build. If it
passes, the next step (out of scope here) is feeding it the real crutch (CSKG) + a real-corpus
fade-curve test (Social IQa).

## The connector (built, self-tested, real code path)

`consolidation_pass(..., native_store=None, promote_min_exposure=8, promote_min_consistency=0.75,
promote_relation="OUTCOME_POLARITY", promote_source=...)`. When an item BANKS (schema_ok AND
mdl_ok, the pre-existing false-memory-safe gate, unchanged), it is ADDITIONALLY evaluated for
promotion: `exposure = len(traces)` and `consistency = abs(vote_margin)` must BOTH clear their own,
strictly stronger thresholds (promote_min_exposure=8 > MIN_CONFIRM=4; promote_min_consistency=0.75 >
NEUTRAL_BAND=0.34, the banking bar) before `native_store.store(lemma, "OUTCOME_POLARITY", label,
source, trust)` is called. GROUNDED_NEUTRAL items never promote (no directional fact to assert).
This is a THIRD, independent, strictly-additive gate -- it can never cause an item that previously
banked-and-registered-to-the-overlay to newly LEAK past the existing schema-consistency guard; it can
only ever block additional (native-store) writes the old code path never made at all. `native_store is
None` (the default) reproduces the exact prior return value and side effects byte-for-byte (verified:
the module's own pre-existing self_test items 1-6 still pass unmodified).

Organ self-test (real code path, not synthetic-only): `hdlab/grounding_acquisition_loop.py::self_test`
item (7) constructs a REAL `HDFactStore(n_dim=1024, seed=7)`, runs a coherent+consistent item through
the real `consolidation_pass` and asserts it promotes AND is `store.query()`-readable (lookup-free);
runs a coherent-but-inconsistent item (margin=0.5, banks as GROUNDED_POS) through the SAME store and
asserts it does NOT promote and `store.query()` returns `[]`. Both PASS (verified this session,
`PYTHONPATH=. python hdlab/grounding_acquisition_loop.py` -> `ALL SELF-TESTS PASSED`).

## Test A design (synthetic confirmation regime; I own every parameter)

17 synthetic lemmas across 5 categories, each with a hand-specified (n_pos, n_neg, context_mode)
so exposure and consistency are EXACT, not statistical:

1. **PROMOTE_EXPECTED** (5 lemmas, coherent context, both gates cleared):
   `c1`(8,0)->margin=1.0 exp=8; `c2`(10,0)->1.0 exp=10; `c3`(11,1)->0.833 exp=12;
   `c4`(0,9)->-1.0 exp=9 (tests NEG direction); `c5`(1,7)->-0.75 exp=8 (boundary: consistency
   EXACTLY at the 0.75 floor, `>=` inclusive).
2. **BANKED_BUT_BLOCKED** (5 lemmas, coherent context, banks but must NOT promote -- the sharp guard
   test): `b1`(6,2)->0.5 exp=8 (exposure clears, consistency 0.5<0.75 does not); `b2`(3,9)->-0.5
   exp=12 (same, NEG direction); `b3`(6,0)->1.0 exp=6 (consistency clears, exposure 6<8 does not);
   `b4`(7,0)->1.0 exp=7 (same, boundary exp=7); `b5`(3,1)->0.5 exp=4 (both gates fail, at
   MIN_CONFIRM floor).
3. **NEUTRAL_INCONSISTENT** (2 lemmas, coherent context, banks GROUNDED_NEUTRAL, never promotes):
   `n1`(4,4)->0.0 exp=8; `n2`(5,5)->0.0 exp=10 -- demonstrates high exposure alone never rescues a
   genuinely inconsistent mapping (Schneider & Shiffrin's core point).
4. **RARE_UNDER_MIN_CONFIRM** (3 lemmas, never reach consolidation eligibility, stay PENDING
   forever): `r1`(2,0) exp=2; `r2`(1,1) exp=2; `r3`(3,0) exp=3 -- cardinality/floor control.
5. **SCRAMBLED_CONTEXT_ADVERSARIAL** (2 lemmas, consistent votes, INDEPENDENT-RANDOM per-trace
   context -- must ESCALATE via the PRE-EXISTING schema guard, never reach BANK, hence trivially
   never promote): `s1`(8,0) exp=8; `s2`(10,0) exp=10 -- confirms the new connector does not weaken
   the old guard.

`promote_min_exposure=8`, `promote_min_consistency=0.75` (module defaults, not tuned for this test).
6 consolidation passes run (>= the pass count needed for the Dumay-Gaskell intervening-pass rule PLUS
patience_max=3 to fully resolve the scrambled-context items to ESCALATED).

## Bands (declared BEFORE running)

**Gate 1 -- promotion works** (deterministic, not statistical: every PROMOTE_EXPECTED item's
(exposure, consistency) is hand-computed to clear both thresholds): 5/5 must promote for HARD_PASS;
<=4/5 is a mechanism-partial signal (MIDDLE_BAND candidate, not expected).

**Gate 2 -- guard holds** (the decisive gate, vetted hardest per Director instruction): ZERO leaks
required across all 12 "must not promote" items (5 BANKED_BUT_BLOCKED + 2 NEUTRAL_INCONSISTENT + 3
RARE + 2 SCRAMBLED). ANY leak (>=1/12) is an automatic HARD_FAIL regardless of Gates 1/3 -- a leaking
guard falsifies the whole architecture's safety property and the verdict short-circuits to HARD_FAIL.

**Gate 2b -- old guard still fires** (regression check): both SCRAMBLED_CONTEXT_ADVERSARIAL items
must reach ESCALATED (2/2); this proves the new connector did not weaken the pre-existing
schema-consistency false-memory guard.

**Gate 3 -- native coverage correlates with exposure x consistency**: computed over the 12 items that
actually REACH the BANK branch (5 PROMOTE_EXPECTED + 5 BANKED_BUT_BLOCKED + 2 NEUTRAL_INCONSISTENT --
RARE never reaches evaluation, SCRAMBLED never reaches BANK, both structurally excluded from a gate
whose inputs are only defined once an item banks). Pearson r between `exposure * consistency` and
`promoted` (0/1) over these 12 points. SCRAMBLE CONTROL: 200 fixed-seed random permutations of the
`promoted` labels across the same 12 items; compute r for each permutation (a permutation-test null
distribution, not a single shuffle -- n=12 is too small for one shuffle to be a reliable null).
HARD_PASS requires r_true >= 0.5 AND r_true above the 95th percentile of the null |r| distribution
(permutation p < 0.05) AND mean(null |r|) < 0.15. A secondary, non-gating number is also reported:
the same correlation computed over ALL 17 items (RARE contributes consistency=0/exposure<4 as
"never evaluated", SCRAMBLED contributes high exposure*consistency but promoted=0 since it never
banks) -- expected to be WEAKER than the 12-item number, honestly disclosed as showing
exposure*consistency predicts promotion only CONDITIONAL on clearing the orthogonal schema-context
guard, not unconditionally.

## Verdict logic

```
HARD_FAIL  if any_leak (Gate 2 fails)                      # short-circuits everything else
HARD_FAIL  elif gate1_rate < 0.6 (< 3/5 promote)            # mechanism doesn't fire
HARD_FAIL  elif (r_true - mean(null_r)) < 0.2               # correlation indistinguishable from noise
HARD_FAIL  elif not gate2b (scrambled items don't escalate)  # old guard regressed
HARD_PASS  if gate1==5/5 AND no_leak AND gate2b==2/2 AND r_true>=0.5 AND perm_p<0.05 AND mean(null_r)<0.15
MIDDLE_BAND otherwise (no leak, but gate1 in [3,4]/5 or r_true in [0.2,0.5) or perm_p in [0.05,0.15))
```

## Compute architecture

(b) sequential-CPU, justified: n=17 synthetic lemmas, <=6 consolidation passes, all numpy (context_vec
dim=256) + one small HDFactStore(n_dim=4096). Total wall time expected < 5s. No GPU batching
candidate -- this is a control-flow/logic mechanism test, not a matmul-heavy sweep. Storage strategy:
no_storage (single in-process Library + single HDFactStore instance; no sharding/bundling axis).

## Gates (SCHEMA-VET applicable subset for a mechanism/unit-test-shaped cell)

- `cardinality_ok`: n/a in the sweep sense (no swept axis); cell instead asserts `len(promotion_log)
  == 12` (every BANK-branch item logged exactly once) as its cardinality check.
- `arms_differ_verified`: true -- the 5 category groups produce provably different final-status
  distributions (verified by comparing the set of (lemma, status) tuples across groups; also a
  SHA256 digest of each group's raw (n_pos, n_neg) config differs, ruling out a copy-paste bug).
- `final_metrics_atomicity`: tmp_replace (os.replace), matching the existing exp_grounding_
  acquisition_loop_v1.py pattern.
- `except SystemExit: raise` before `except Exception` (no bare/BaseException).
- `crlb_n/a`: "deterministic threshold-gate + permutation-test mechanism cell; no argmax/capacity
  noise floor applies."
- `deterministic_seeding`: true (fixed integer seeds throughout; `np.random.default_rng(fixed)`
  for the scrambled-context noise and the permutation-test shuffles; no built-in `hash()`, no
  `list(set(...))`).
- `real_code_path_exercised`: [Library, consolidation_pass, HDFactStore, HDFactStore.store,
  HDFactStore.query] -- all constructed/called for real inside the cell's own `self_test()`, not a
  synthetic-only branch, at reduced (n=3-lemma) scale.
- `progress_logging`: n/a (`timeout_s` << 1800; cell completes in seconds, no heartbeat required
  per the >=30min threshold in exp_dev canonical file SS17).
- `discriminator_reachability`: true -- Gate 1 structurally cannot pass if the promotion mechanism
  is dead (0 promotions), so a "0 leaks because nothing ever promotes" phantom-pass is impossible:
  Gate 1 and Gate 2 jointly falsify a dead mechanism.

## Dispatch

Synthetic, <5s wall time, no corpus I/O, no GPU benefit -- run directly (`python
experiments/exp_crutch_fade_bank_native_promotion_test_a_v1.py`), foreground to completion, per
Director's explicit "Local foreground to completion, no background-and-wait" instruction and the
"do lightweight measurements inline, don't over-route to heavyweight cells" standing discipline. Not
queued to local_cpu_queue/remote_cpu_queue/overnight_queue (there is no full-vs-smoke distinction
worth a queue round-trip for a sub-5-second deterministic mechanism test); metrics.json is still
written to `data/exp_crutch_fade_bank_native_promotion_test_a_v1/` for the audit trail.
