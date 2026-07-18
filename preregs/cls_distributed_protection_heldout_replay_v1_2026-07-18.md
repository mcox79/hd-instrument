# Pre-reg: exp_cls_distributed_protection_heldout_replay_v1

Filed 2026-07-18 (exp_dev). Cell: `experiments/exp_cls_distributed_protection_heldout_replay_v1.py`.
Metrics: `data/exp_cls_distributed_protection_heldout_replay_v1/metrics.json`. CPU, self-contained numpy, glass-box.

## Question (the CLS chain-grade revival criterion)
Does interleaved replay of a SMALL SUBSAMPLE of old memories protect a HELD-OUT, NEVER-REPLAYED subset
of old memories from catastrophic interference (genuine DISTRIBUTED protection -- the scalable thing
"ingest textbook after textbook without forgetting" requires), or only the specific items it explicitly
rehearses (PER-ITEM rehearsal, which does not scale)?

## Why the pilot could not answer it (VET a93a9b1e, the localization that triggered this cell)
The pilot `exp_cls_interleaved_replay_consolidation_pilot_v1` (7a682685f) was HARD_PASS but VET-deflated
to MEASURED_MECHANISM: its old pool was 40 items and the replay budget drew ~40/step, so EVERY old item
was rehearsed ~3x (n_never_replayed=0). The decisive VET control (exclude eval items from replay)
collapsed old-recall to ~0.19 -> the retention was PER-ITEM rehearsal, and the distributed-protection
claim was untested. This cell scales the pool + designates a disjoint NEVER-REPLAYED held-out set so the
distinction is measurable.

## Design (ONE variable = replay COVERAGE of the old pool; held-out eval FIXED across arms)
Old block = 400 structured items: OLD_CLASSES=20 x OLD_EXEMPLARS=20; each class a bipolar prototype,
exemplars flip each bit w.p. P_FLIP (within-class structure). Deterministic split per class: first 4
exemplars = REPLAY-ELIGIBLE (80 items = 20% of old = the subsample); remaining 16 = HELD-OUT
NEVER-REPLAYED (320 items = 80%). Held-out items ARE trained in the old block (legitimately learned) but
NEVER appear in any replay -> n_never_replayed = 320 (was 0 in the pilot). Interference = K_INTERFERE=10
sequential NEW-class blocks (NEW_CPB=4, 20 exemplars) trained after the old block, V=60. Slow store =
shared-hidden-layer net N=128 -> H=24 -> V=60 (tanh+softmax, batch backprop, E_OLD=150, E_NEW=120, LR=0.3).
H=24 gives the capacity PRESSURE that makes sequential training catastrophically overwrite the shared
representation. Difficulty knobs (H, K_INTERFERE, E_NEW) locked from a difficulty-ONLY sweep (they set
baseline behavior, NOT the mechanism).

ARMS (identical net init across arms -> clean one-variable):
- no_replay: sequential, NO old replay = McCloskey-Cohen single-shared-store failure mode AND the
  no-replay LOWER reference (floor for held-out old).
- subsample_replay (MECHANISM): interleave replay of ONLY the 80 eligible old items each consolidation
  step; the 320 held-out are NEVER replayed. LOAD-BEARING = held-out old-recall.
- replay_all: interleave replay of ALL 400 old items (incl. held-out) = UPPER reference / ceiling
  (proves the held-out items ARE protectable if rehearsed; metric not saturated-low).

SWEEP AXIS: P_FLIP in {0.20, 0.26, 0.30, 0.34, 0.38} = within-class structure. Low P_FLIP =
related/structured memories (textbook topics); high = arbitrary/unrelated facts. Distributed protection
is only POSSIBLE when old memories share structure (CITED@ McClelland-McNaughton-O'Reilly 1995: interleaved
learning discovers/preserves shared STRUCTURE; fast ARBITRARY learning needs the hippocampus). The
high-P_FLIP end is therefore a MEASURED per-item CONTROL, not an assertion.

## Design-gate (verified at smoke BEFORE full)
- REAL baselines: no_replay genuinely forgets held-out old at every point (not strawman/abstain);
  replay_all is a real rehearse-everything ceiling.
- CAN-FAIL (shown as DATA): if subsample held-out sits at the no_replay floor even at the structured end
  -> HARD_FAIL_PER_ITEM_REHEARSAL. The sweep's arbitrary end (P_FLIP=0.38) is the measured per-item
  control: sub -> floor when structure is absent.
- DIFFICULTY-ON (per sweep point): no_replay held-out <= 0.45 AND held-out_initial >= 0.70 (net learned
  old first, forgetting not inability) AND replay_all held-out >= 0.70 (ceiling works) AND recent >= 0.55.
  Forgetting deepens with pool/interference (not seeds), so smoke/self-test run the FULL grid, 1 seed
  (DISCRIMINATOR-MUST-SURVIVE-SCALE).
- ONE variable: no_replay / subsample / replay_all differ only by replay coverage (same init, same task).
- No held-out LABEL leak: held-out items are never REPLAYED, but WERE trained in the old block; target
  is RETENTION of trained memories, the legitimate CLS mechanism (replaying already-seen items is not a leak).
- cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = 5 x 3 = 15; verdict emits HARD_FAIL_CARDINALITY_BREACH if short.
- crlb_n/a: retention accuracy, no argmax-noise floor. arms_differ hash-test over predictions. No
  hash()/list(set()) nondeterminism (deterministic index split + fixed int seeds).

## Bands (envelope-fail-bands)
- HARD-PASS (=chain-grade attempt, >=2/3 seeds): at the structured end (P_FLIP=0.20), subsample held-out
  old-recall >= no_replay floor + 0.20 AND >= 0.55 abs AND recent >= 0.55.
- HARD-FAIL / CAN-FAIL (first-class): subsample held-out <= no_replay + 0.05 at the structured end ->
  per-item rehearsal only, distributed protection REFUTED at this scale.
- MIDDLE_BAND: partial (beats floor but below margin/abs bar), or structured-end difficulty gate off.
- Feasibility: replay_all held-out = 1.000 (ceiling) >> 0.70 floor at every point.

## Result (MEASURED@ data/exp_cls_distributed_protection_heldout_replay_v1/metrics.json)
VERDICT = HARD_PASS, 3/3 seeds at the structured end, 15/15 units, arms_differ=True, difficulty ON at
every point. HELD-OUT never-replayed old-recall curve (no_replay floor / subsample / replay_all ceiling):
- P_FLIP=0.20: no=0.318  sub=0.969  all=1.000  hp=3/3  <- distributed protection (structured/related)
- P_FLIP=0.26: no=0.096  sub=0.799  all=1.000  hp=3/3
- P_FLIP=0.30: no=0.038  sub=0.581  all=1.000  hp=3/3
- P_FLIP=0.34: no=0.024  sub=0.324  all=1.000  hp=0/3  <- partial
- P_FLIP=0.38: no=0.004  sub=0.160  all=1.000  hp=0/3  <- per-item collapse (arbitrary/unrelated)
replayed-subset recall (structured) = 1.000 (rehearsed items always retained). n_never_replayed=320,
n_replayed=80.

## Interpretation (STRATEGIC READ = hypothesis-pending-VET, deflated)
Distributed protection is REAL in the shared-net regime, but CONDITIONAL on shared structure: replaying a
20% subsample protects the 80% never-replayed old memories to 0.969 when memories are structured/related
(the textbook-topic regime) and COLLAPSES to the per-item floor (0.160) when memories are
arbitrary/unrelated. The clean monotone structure-dependence (0.969 -> 0.160 as P_FLIP 0.20 -> 0.38, with
no_replay ~0 and replay_all ~1 throughout) is the mechanism signature and doubles as the internal per-item
control. This complements (does not contradict) the prior-credited additive-substrate REPLAY finding
(strategy_decisions_2026-05-26: zero-sum per-item at N=8192) -- that substrate lacked the shared
distributed representation this test provides. HONEST CAVEAT: "structured" here = prototype+bit-flip toy
structure; whether real textbook-topic structure sits at the protected end of this axis is the next
question, not shown here.

## Status
CLAIM-VET-pending (landed-VET by skunkworks required before chain-grade). NOT self-declared chain-grade.
Pause was ACTIVE: ran INLINE (local foreground, ~32s full), NO queue dispatch.
