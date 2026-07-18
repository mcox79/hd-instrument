# Pre-reg: exp_cls_distributed_protection_independent_content_v1

Filed 2026-07-18 (exp_dev). Cell: `experiments/exp_cls_distributed_protection_independent_content_v1.py`.
Metrics: `data/exp_cls_distributed_protection_independent_content_v1/metrics.json`. CPU, self-contained numpy, glass-box, local-runnable.

## Question (the CLS chain-grade revival criterion, done right)
Does interleaved replay of a SMALL SUBSAMPLE of old memories protect held-out NEVER-REPLAYED memories that
carry INDEPENDENT WITHIN-CLASS CONTENT -- BEATING the two confound baselines (1-NN proximity +
fresh-net-trained-on-subsample) -- so the protection is genuine DISTRIBUTED CONSOLIDATION and not
GENERALIZATION?

## Why the prior attempt could not answer it (VET a15e4d91, the confound diagnosis)
`exp_cls_distributed_protection_heldout_replay_v1` (c09f92f38) was HARD_PASS (subsample held-out=0.969 vs
no_replay=0.318 at the structured end) but VET-diagnosed a GENERALIZATION CONFOUND: its "320 never-replayed
memories" were 16 noisy re-draws of 20 prototypes and the held-out metric was CLASS classification. The
held-out items carried NO independent information -- their class was recoverable by GENERALIZATION. A
zero-training 1-NN lookup against the replayed subsample AND a fresh-net-trained-only-on-the-subsample both
MATCH the replay arm (you only need the CLASS, not the item's own trace). So the "protection" was
generalization, not distributed consolidation. The VET's exact revival criterion: construct held-out items
carrying INDEPENDENT within-class content where BOTH confounds FAIL, and ADD them as ARMS.

## Design (ONE variable = how the old pool is used; cue/target/init FIXED across arms)
Old block = OLD_CLASSES=12 x OLD_EXEMPLARS=12 = 144 items. Each item's CUE = [shared class code | item probe]:
a shared bipolar class code on the first SHARED_FRAC*N dims (shared class STRUCTURE -> distributed
consolidation mechanistically POSSIBLE) + an item-specific bipolar probe on the rest. Each item's TARGET =
a UNIQUE per-item bipolar vector (D_T=64) from a codebook, assigned independently of class (INDEPENDENT
within-class content: the class tells you NOTHING about which target). Slow store = shared-hidden-layer
REGRESSION net N=256 -> H=160 -> D_T=64 (tanh hidden, linear output, MSE, batch backprop, E_OLD=400,
E_NEW=200, LR=0.04). LOAD-BEARING metric = held-out RETRIEVAL of the item's own target: nearest target
(cosine) among the full 144-item old codebook; chance = 1/144 = 0.0069. Deterministic split per class:
first ELIG_PER_CLASS=3 exemplars = replay-eligible (36 items = 25% = subsample); remaining 9 = HELD-OUT
NEVER-REPLAYED (108 items = 75%). Interference = K_INTERFERE=8 sequential NEW-class blocks (NEW_CPB=3,
NEW_EXEMPLARS=12, fresh random targets). CITED@ McClelland-McNaughton-O'Reilly 1995; Kumaran-Hassabis-McClelland 2016.

ARMS (5; identical net init across the 3 learned arms -> clean one-variable):
- no_replay (FLOOR): sequential, NO old replay = McCloskey-Cohen failure mode AND the no-replay floor.
- subsample_replay (MECHANISM): interleave replay of ONLY the 36 eligible items; the 108 held-out NEVER
  replayed. Does distributed consolidation protect their INDEPENDENT targets?
- replay_all (CEILING): interleave replay of ALL 144 old items (incl held-out) = protectable ceiling.
- one_nn_proximity (MUST-BEAT CONFOUND, zero training): held-out target := target of the nearest REPLAYED
  cue (cosine). FAILS iff held-out content is genuinely independent of class-proximity.
- fresh_net_subsample (MUST-BEAT CONFOUND): a FRESH net trained ONLY on the 36-item subsample (never sees
  held-out, zero interference). FAILS iff held-out content is not generalizable from the subsample.

SWEEP AXIS: SHARED_FRAC in {0.75, 0.55, 0.35} = fraction of cue that is the shared class code. HIGH =
strong shared structure (distributed consolidation MOST plausible) = the "structured" end where the HP gate
applies. LOW = items more arbitrary/independent = per-item CONTROL end.

## Design-gate (verified at smoke/self-test BEFORE full -- MEASURED@ self-test)
- REAL baselines/arms: 5 arms above (floor / mechanism / ceiling / 2 confounds); no strawman/abstain-all.
- LOAD-BEARING metric = held-out INDEPENDENT-target retrieval + margin of subsample OVER max(1-NN, fresh-net).
- CAN-FAIL (first-class): HARD_FAIL_GENERALIZATION_NOT_CONSOLIDATION if subsample <= max(confound)+0.05 at
  the structured end -> generalization again / per-item only, distributed protection REFUTED at scale.
- DIFFICULTY-ON (per point): BOTH confounds FAIL to recover held-out (<=0.25, proves independence) AND net
  LEARNED held-out initially (>=0.70) AND no_replay FORGETS (<=0.30) AND replay_all PROTECTS (>=0.55).
  Self-test @ SF=0.75: no=0.083 sub=0.231 all=1.000 1nn=0.000 fresh=0.000 init=1.000 diff=Y (all gates met).
- ONE variable: the 3 learned arms differ only by replay coverage (same init, same cues/targets).
- No leak: held-out never REPLAYED but WERE trained in the old block; target is RETENTION of a trained
  independent trace (legitimate CLS). arms_differ hash-test over per-arm held-out predictions.
- cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = 3 SF x 3 seeds = 9. crlb_n/a (retrieval, chance=1/144).
  No hash()/list(set()) nondeterminism (deterministic index split + fixed int seeds).
- DISCRIMINATOR-MUST-SURVIVE-SCALE: forgetting deepens with pool/interference (not seeds); self-test runs
  the FULL grid at 1 seed.

## Bands (envelope-fail-bands, pre-registered BEFORE full)
- HARD-PASS (=chain-grade attempt, >=2/3 seeds, at STRUCTURED end SF=0.75): subsample held-out retrieval
  >= max(1-NN, fresh-net) + 0.15 (CONFOUND_MARGIN) AND >= no_replay + 0.15 (FLOOR_MARGIN) AND >= 0.40 abs.
- HARD-FAIL / CAN-FAIL (first-class): subsample <= max(confound) + 0.05 at the structured end -> distributed
  protection REFUTED (generalization / per-item only; does not scale to textbook-after-textbook).
- MIDDLE_BAND: subsample beats confounds+floor but below the >=0.15-margin / >=0.40-abs bar (partial
  distributed consolidation), OR structured-end difficulty gate off.
- Feasibility: replay_all ceiling = 1.000 (self-test) >> 0.40 abs bar -> HARD_PASS is reachable; REFUTE is
  reachable (arbitrary end). Genuinely two-sided.

## Result (MEASURED@ data/exp_cls_distributed_protection_independent_content_v1/metrics.json)
VERDICT = MIDDLE_BAND_PARTIAL. 9/9 units, arms_differ=True, difficulty ON at the two structured points.
Held-out INDEPENDENT-content retrieval (chance=0.0069), curve [no_replay/subsample/replay_all/1-NN/fresh-net]:
- SF=0.75 (structured): no=0.096 sub=0.247 all=1.000 1nn=0.000 fresh=0.000  init=1.000  diff=Y  hp=0/3
- SF=0.55           : no=0.259 sub=0.343 all=1.000 1nn=0.000 fresh=0.000  init=1.000  diff=Y  hp=0/3
- SF=0.35 (arbitrary): no=0.407 sub=0.392 all=1.000 1nn=0.000 fresh=0.000  init=1.000  diff=N (no_replay does not forget)
Per-seed @ SF=0.75: subsample vs max(confound) margin = 0.231 / 0.241 / 0.269 (all 3 seeds >> 0.15);
subsample vs no_replay floor margin = 0.148 / 0.167 / 0.139 (2/3 >= 0.15); absolute = 0.231 / 0.241 / 0.269
(all < the 0.40 abs bar). BOTH confounds recover 0.000 of held-out at EVERY structure level.

## Interpretation (STRATEGIC READ = hypothesis-pending-VET, deflated)
The prior GENERALIZATION CONFOUND is DISSOLVED: with genuinely independent per-item targets, the 1-NN and
fresh-net baselines recover 0.000 (they had 0.969-matching power in the prior classification design) -->
the held-out content is truly independent (difficulty-on PROVEN). Against that, subsample-replay recovers
~0.23-0.34 of the never-replayed independent traces, DECISIVELY and ROBUSTLY above BOTH confounds (margin
0.23-0.39, all 3 seeds) AND above the no_replay floor (margin ~0.05-0.17). So distributed consolidation of
INDEPENDENT content is REAL, not generalization -- the VET's literal confound-beating criterion is met on
3/3 seeds. HOWEVER it is PARTIAL: subsample protects only ~25% of held-out traces absolutely (ceiling
replay_all=1.000), below the pre-registered >=0.40-abs / >=0.15-floor-margin HARD_PASS bar --> MIDDLE_BAND,
not HARD_PASS. Structure-dependence is directionally present (subsample > no_replay at SF=0.75/0.55; subsample
< no_replay at the arbitrary SF=0.35 end), but the arbitrary end has difficulty OFF (no_replay does not
forget when cues are item-distinctive), so it is a NOTED trend, not a clean control. HONEST CAVEATS: (1)
tier is MIDDLE_BAND per my stricter abs bar; whether the decisive confound-margin ALONE (VET's literal
criterion) warrants chain-grade is a VET adjudication, not a self-declaration. (2) partial ~25% protection
is a real but modest effect -- "distributed consolidation contributes to protecting independent content"
is supported; "distributed consolidation FULLY protects independent content (textbook-after-textbook)" is
NOT. (3) toy shared-code+probe structure; real textbook structure not shown. CLAIM-VET-pending.

## Status
CLAIM-VET-pending (landed-VET by skunkworks required before any chain-grade claim). NOT self-declared
chain-grade. Pause was ACTIVE: authored + smoked + ran INLINE (local foreground), NO queue dispatch.
```
bash tools/orchestrator/queue_add.sh remote_cpu_queue cls_distributed_protection_independent_content_v1 \
  experiments/exp_cls_distributed_protection_independent_content_v1.py \
  preregs/cls_distributed_protection_independent_content_v1_2026-07-18.md 1200
```
(above = the OPTIONAL remote re-run command for the orchestrator to ship WHEN UNPAUSED; not required since
the full ran locally to completion.)
```
