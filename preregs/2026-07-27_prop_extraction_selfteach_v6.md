# Pre-reg: prop_extraction_selfteach_v6

Anchor: `prop_extraction_selfteach_v6`. Cell: `experiments/exp_prop_extraction_selfteach_v6.py`.

## Question
Can a small LEARNED proposition-extraction head, self-taught from the foundation's typed edges
(distant supervision), read a sentence about a concept and emit a role-bound (relation, object)
proposition -- and is any resulting "win" genuine COMPREHENSION or KG-frequency/concept-identity
MEMORIZATION? This is STEP 2 from notes/v4_negative_brain_fidelity_audit_readout_is_order_blind_next_
lever_2026-07-27.md -- the general, learned successor to v5's hand-built position-bind readout.

## Brain grounding (see notes/research_brain_faithful_learned_proposition_extraction_selfteach_from_
foundation_2026-07-27.md for the full lit-scan)
Frankland & Greene (2015, PNAS): reusable, role-general lmSTC subregions decode agent/patient identity
across arbitrary fillers -- a slot architecture. Rabovsky/Hansen/McClelland (2018) + St. John & McClelland
(1990): role assignment is learned from a PREDICTION-ERROR signal during comprehension, no hand labels
needed. v6's design (reusable per-relation role slots, trained via prediction-error against the
foundation's typed edges) is a direct engineering analog.

## v6.1 revision (BEFORE any run landed, director-flagged 2026-07-28)
Original draft reused v5's readout verbatim (fixed PER-POSITION role vectors bound to token hiddens).
data/probe_v5_bind_readout_derisk_v1.json (n=49, well-powered) measured that scheme's cross-mention
self-consistency at 0.517 (vs 0.955 mean-pool) -- a concept's own different mentions bind inconsistently
because the SAME concept lands at different absolute sentence positions across sentences. Fixed:
`ContentRoleReadout` (role_i = f(h_i), a function of token CONTENT only, never position i) --
content-addressed, therefore position-invariant by construction. Re-measured on the REAL ckpt_seed_7
encoder (data/probe_v6_content_role_readout_derisk_v1.json, n=40 concepts / 120 mentions, untrained-init
role_proj): cross-mention consistency recovers to 0.895 (content_learned_init) / 0.905 (content_fixed) --
close to mean-pool's 0.949, the self-consistency pathology is resolved. Order-sensitivity at INIT is
modest (coh-vs-scrambled cos 0.976/0.978 vs mean-pool's 0.990) -- this is expected and NOT a red flag:
`role_mode="fixed"` (untrained) is exactly the ablation arm, and `role_mode="learned"`'s role_proj is
TRAINED jointly with the rest of the head by the actual prediction-error objective (CE+NCE+prop loss),
which is where any order-sensitivity gain over the untrained baseline should emerge -- that IS the
"self-taught" claim under test, not something that should already be large before training. `--role-mode
fixed` is wired as a one-line follow-up ablation if `learned` lands positive but the source of the gain
needs isolating (content-addressing alone vs the joint learning).

## Design (see cell docstring for full detail)
- FROZEN encoder (SMOKE/SELFTEST: tiny fresh MLM-trained toy encoder, matches v1-v5 convention;
  FULL: `exp_scale_meaning_learn_arc_heldout_v2` ckpt_seed_7, own from-scratch). Never fine-tuned by v6.
- `ContentRoleReadout`: role_i = f(h_i) (learned Linear or fixed random projection), bind(h_i, role_i)
  summed over non-pad, L2-normalized -- position-invariant, content-addressed sentence gestalt.
- `PropositionHead`: reusable per-relation role_slots (Frankland-Greene style) + obj_proj (filler
  projection) + rel_head (relation classifier) + `.proposition()` = `hdlab.binding.bind(role_slots[rel],
  obj_repr)` -- the actual role-bound proposition vector.
- DATASET: `data/cskg_foundation_v1` typed /r/* edges restricted to pairs where BOTH endpoints are
  single-token ARC-universe concepts. For each edge, search the ARC corpus for REAL sentences that
  co-mention both surfaces (Mintz 2009 distant-supervision assumption) -- NO synthetic templates in v1;
  an edge with zero real co-occurring sentences is simply dropped (avoids CONSTRUCTION-DETERMINED risk).
- SPLIT: reuses the standing concept-level held-out split (`V2.build_split`, freq-stratified,
  sha256-ranked, deterministic, leak-proof -- same split every loop cell v1-v5 uses). TRAIN instance iff
  subject not held; HELD instance iff subject held (subject never available at train time in any form).
- OBJECTIVE: CE(relation) + InfoNCE(object, in-batch negatives, target = frozen mean-pool concept
  identity embedding) + cosine(proposition, target-proposition) auxiliary term. Adam, head-only
  (encoder frozen). CHECKPOINTED EVERY EPOCH (non-negotiable; `head_ckpt_latest.pt` + per-epoch
  `head_ckpt_epoch_NN.pt`, both atomic tmp+os.replace).

## Metrics reported (both requested by the director's 2026-07-28 note)
1. **Extraction accuracy vs controls** -- `extraction_acc_coherent` / `extraction_acc_scrambled` /
   `extraction_acc_wrong_rel_slice`: joint (relation-correct AND object-correct) hit@1 over a bounded
   candidate pool (`pool_size`, true object + hard-negatives = other true objects of the same subject
   under a different relation + random fill). This is a real 0-1-range cloze/fact-acquisition metric,
   NOT relational-AUC placement -- deliberately avoids the compression problem the director flagged in
   v4/v5 (v5 FULL: usable AUC range ~0.05 around chance 0.51; here chance floor is ~1/pool_size and the
   ceiling is 1.0, pool_size=8 at FULL).
2. **Comprehension-vs-memorization band** -- see below.

## Controls (all can-fail; this is the whole ballgame)
(a) HELD-OUT-TO-NEW-CONCEPT: eval only on instances whose subject was held (never trained on, text or
    edges). Standing leak-proof split.
(b) CONCEPT-PAIR-PRESERVING SCRAMBLE: same held sentence, word-order scrambled (`LOOP2._scramble_words`
    -- multiset-preserving, self-tested). Comprehension = coherent beats scrambled by margin.
(c) WRONG-RELATION SLICE: held instances where the asserted relation is NOT that subject's own dominant
    relation (computed from the FULL foundation graph, descriptive only, never used in training).
(d) B0 IDENTITY-ONLY baseline (Peng et al. 2020): majority relation for the OBJECT, from TRAIN edges
    only (subject supplies zero signal by construction, since it's held-out).

## Bands (FULL; ported from the research note's falsifiable predictions)
- `MAJORITY_BASELINE_MAX = 0.35` -- task non-degenerate (majority-relation-only baseline must clear this)
- `B0_HARD_PASS_MAX = 0.40` -- identity-only baseline must be below this for HARD-PASS eligibility
- `B0_HARD_FAIL_MIN = 0.65` -- identity-only baseline at/above this => any win is memorization, HARD-FAIL
- `COMPREHENSION_MARGIN = 0.05` -- coherent extraction_acc must beat scrambled by >= this
- `WRONG_REL_MARGIN = 0.05` -- coherent extraction_acc on the wrong-relation slice must beat B0 (same
  slice) by >= this (catches "head just parrots X's dominant relation")
- `MIN_HELD_N = 60` -- power floor (else MIDDLE_BAND_UNDERPOWERED)
- HARD-FAIL: `B0 >= 0.65` OR `coherent - scrambled <= 0`
- HARD-PASS: power_ok AND non_degenerate AND `B0 < 0.40` AND comprehension_specific_gain AND
  wrong_rel_ok AND NOT hard_fail
- else MIDDLE_BAND (or MIDDLE_BAND_UNDERPOWERED if `n_held_eval < MIN_HELD_N`)

## Compute architecture
Class (a) batched-GPU for the encoder forward passes (frozen, no_grad, batched per training step) and
head training (all matmuls). Storage strategy: no_storage / no_composition -- this is a single-hop
classification+retrieval cell, not a chained/composed retrieval task; sharded-vs-bundled storage strategy
does not apply.

## Gates (SCHEMA-VET checklist, abbreviated -- full declarations in cell docstring)
- `cell_chunked: false` (single-seed, no sweep axis)
- `crlb_n_a`: classification/retrieval-accuracy cell, no closed-form noise floor
- `final_metrics_atomicity: tmp_replace`
- `deterministic_seeding: true` (all RNG via `np.random.default_rng`/fixed `torch.Generator` seeds;
  `sorted(set(...))` for sentence dedup, never `list(set(...))` or `hash()`)
- `arms_differ_verified`: coherent vs scrambled predictions checked not bit-identical at smoke (True,
  landed SMOKE_MECHANISM_PASS)
- `real_code_path_exercised`: self-test constructs the REAL typed-edge loader, dataset builder, readout
  (both modes), head, training loop, checkpoint round-trip, eval+scramble control, B0 table, and both
  `build_verdict` paths at N~16-32 synthetic scale (not a mocked branch)
- `progress_logging: print_flush_true` (FULL timeout_s >= 1800)

## SMOKE landed (2026-07-27, local CPU, tiny fresh encoder -- data/exp_prop_extraction_selfteach_v6_smoke/
metrics.json)
`SMOKE_MECHANISM_PASS`: loss decreases (5.008 -> 4.887), n_held_eval=76 (>= floor 8), arms differ
(coherent != scrambled predictions), checkpoint round-trips, B0=0.566/majority=0.395 both sane, 1456/14401
edges had a real co-occurring sentence. rel_acc_coherent == rel_acc_scrambled == majority_baseline exactly
at this scale -- the tiny undertrained smoke-scale head has NOT learned anything beyond majority-class,
which is expected and fine: SMOKE's bar is mechanism-fires, not the comprehension bar (that's FULL's job).

## FULL dispatch
Ships to `overnight_queue` as `prop_extraction_selfteach_v6_full`, queued PENDING behind
`unified_self_learning_loop_v5` (already completed per inflight_monitor -- GPU free at dispatch time).
Uses `exp_scale_meaning_learn_arc_heldout_v2` ckpt_seed_7 (default `--ckpt` path). `role_mode=learned`
(primary arm). `--role-mode fixed` is a one-line follow-up ablation, not run tonight (keeps the GPU
commitment modest; the director's ablation request is wired, not spent, unless the primary result is
positive and needs the source-of-gain isolated).

## Honest deflate null (pre-registered, not spun if it happens)
If `B0 >= 0.65`: the foundation's per-object relation distribution is skewed enough that any head "win"
is indistinguishable from frequency memorization -- report HARD_FAIL plainly (mirrors the v3
"distributional sample-accumulation, not comprehension" downgrade). If `coherent - scrambled <= 0`: the
head is using concept-pair identity, not reading -- report HARD_FAIL plainly, and treat it as a real
negative pointing at the objective/architecture (see cell docstring "Divergences from the brain" #3 --
batch contrastive objective vs the brain's incremental online prediction-error account -- before
concluding the self-teach direction itself is wrong).
