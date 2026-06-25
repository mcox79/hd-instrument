# Cell spec proposal — Barrier 2 closer: substrate-as-LM with role-tagged Plate context

Director-level proposal; NOT dispatched. Pre-authored Stage 2 spec for USER dispatch decision post Wave D landing.

## Why this cell

Encoder-leakage fair-regime retest (last night) confirmed: substrate + rank-1 Hebbian W + clean encoder = bigram backoff floor *exactly*. NOT below. NOT above. **Diagnosis: rank-1 Hebbian outer-product on sparse-bipolar codes IS a bigram lookup table.** It learns "after X, Y is likely" — same operation as a bigram count.

The SEMANTIC concept-learner battery (yesterday morning landing, v2 FULL HARD_PASS 6/6 arms, A3 generalization top1=1.000) showed substrate GENERALIZES perfectly when given **role-tagged triples**: `bind(R_subj, A) + bind(R_pred, P) + bind(R_obj, B)`. When trained on `(king, plays_role_of, X)` and `(queen, plays_role_of, X)` style data, substrate predicts heldout `(queen, ___, ___)` at top1=1.000 because it learns the ROLE-FILLER structure, not the surface pair.

**The LM cell has never used this primitive.** Every LM cell so far has used substrate as a context-bigram lookup table (encode current word → W lookup → predict next word). To beat bigram we need to wire context as **role-tagged HRR**, exactly as SEMANTIC battery proved works.

## Cell anchor

`substrate_LM_role_tagged_plate_context_v1`

## Lane / corpus / encoding

- Lane 1 (substrate-native)
- Corpus: text8 (WORLD A; same as fair_harness rail 7.3065)
- Encoder: hub-spoke E1 v3 if Wave D HARD_PASSes; else fall back to word2vec sparse-bipolar f=0.05 to match rail
- Storage: rank-1 Hebbian outer-product W (chain-grade primitive)
- Binding: Plate HRR canonical role-binding

## Architecture (the only knob varied across arms)

For each token position t in stream, build the CONTEXT representation as:

**Baseline (ARM_BIGRAM_CONTEXT)**: `c_t = E[w_{t-1}]` — single previous word, no role-tag (this IS the rank-1 Hebbian bigram lookup we have today)

**ARM_ROLE_TAGGED_K2**: `c_t = bind(R_pos1, E[w_{t-1}]) + bind(R_pos2, E[w_{t-2}])` — role-tagged previous 2 words

**ARM_ROLE_TAGGED_K4**: 4-position role-tagged context — `c_t = sum_{i=1..4} bind(R_pos_i, E[w_{t-i}])`

**ARM_ROLE_TAGGED_K4_PLUS_GRAMMAR**: 4-position + grammar-role tags (POS-tag-conditional binding); arm 3 with one additional role per position

**ARM_BIGRAM_NO_ROLE_K4_CONTROL**: 4-word context SUM without role tags (`c_t = sum_{i=1..4} E[w_{t-i}]`) — this isolates whether the ROLE-TAGGING is load-bearing vs just having more context

For all arms, prediction is: `logits = softmax(W @ c_t / T)` over vocab, with T tuned by grid.

## Sanity rail

ARM_BIGRAM_CONTEXT must reproduce fair_harness rail 7.3065 within ±0.05 BPC (same encoder, same N, same N_TRAIN). If it doesn't, encoder/W wiring is different than rail — fix BEFORE running other arms.

## Pre-reg HARD bands

- **HARD_PASS_BIGRAM_BEAT (PRIMARY)**: any role-tagged arm BPC ≤ 7.10 (beats bigram floor 10.12 — wait, this is BIGRAM-conditional metric; for unigram-conditional the bigram floor 7.30; let me be careful)

Actually let me restate the bands in terms of unigram-conditional BPC which is what fair_harness measures:
- fair_harness rail 7.3065 IS the bigram backoff baseline (unigram-conditional)
- To beat bigram → role-tagged arm < 7.31 by margin

**Bands:**
- HARD_PASS_BIGRAM_BEAT (PRIMARY): best role-tagged arm BPC ≤ 7.10 AND beats BASELINE (bigram_context) by ≥ 0.10 BPC AND CV ≤ 0.03
- HARD_PASS_CHAIN_GRADE: best role-tagged arm BPC ≤ 6.95 AND beats baseline by ≥ 0.20 BPC
- MIDDLE_BAND: 7.10 < best ≤ 7.25
- HARD_FAIL: best ≥ 7.30 (no lift over bigram)

**Discriminator:** ARM_BIGRAM_NO_ROLE_K4_CONTROL isolates whether ROLE-TAGGING is load-bearing. If K4-no-role ≈ K4-with-role, then role-tagging adds nothing (substrate just benefits from more context); if K4-with-role significantly beats K4-no-role, role-tagging IS the lever.

## Config

- N_DIM=8192 (match rail)
- N_TRAIN=100000, N_HELD=20000 (match rail)
- V=4000 (match rail)
- 3 seeds [7, 17, 23] (match rail)
- TEMP_GRID = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
- LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
- sparse_f = 0.05 (match rail encoder)
- Role codebooks R_pos1..R_pos4 = Gram-Schmidt orthogonalized sparse-bipolar (4 roles only; orthogonality preserved at N=8192)

## Routing

GPU overnight_queue (via hdi_orchestrator handoff). Matmul-heavy at N=8192 with 4-fold context bind sums.

## Timeout

7200s (similar to fair_harness FULL)

## Honest scope flags

- **WHAT THIS DOES**: tests whether role-tagged HRR context lets substrate beat bigram, leveraging the SEMANTIC battery's chain-grade A3 generalization
- **WHAT THIS DOES NOT DO**: prove substrate beats LSTM/transformer; that's Stage 3+. This is Stage 2 first-architectural-win.
- **WHAT COULD KILL IT**: (a) text8's stripped corpus may lack role-structure that the binding mechanism can exploit; (b) at K=4 the bundle norm may hit cleanup-margin issues (need amplitude tuning); (c) rail mismatch if encoder differs.
- **CONFOUND AUDIT**: bigram_no_role_K4 control isolates role-tagging from context-size; orthogonal R_pos codebooks isolate role-mechanism from random projection; sanity rail isolates pipeline correctness.

## Expected outcome

P_deflated(some role-tagged arm beats bigram by ≥0.10 BPC): **0.50**
- Brain prior +0.10 (role-filler is decisive cortical mechanism)
- SEMANTIC battery precedent +0.10 (A3 chain-grade)
- Calibration penalty -0.20 (no prior substrate-LM cell used role-tagged context; novel synthesis)

P_deflated(all role-tagged arms tie at bigram floor): 0.20 — would suggest role-tagging needs deeper architecture (multi-position grammar parse, not just position roles)

P_deflated(role-tagged arm LIFTS by ≥0.20 BPC, chain-grade-eligible): 0.30 — would close Barrier 2 and unlock substrate-as-LM Stage 2.

## Cross-thread context

- SEMANTIC battery v2 FULL HARD_PASS 6/6 (A3 top1=1.000) — the existence proof that substrate generalizes via role-tags
- fair_harness 7.3065 — the bigram rail to beat
- encoder-leakage retest MIDDLE_BAND — substrate=bigram at fair regime confirmed; need new lever
- cross-layer compose +0.376 BPC indep beats shared — Barrier 3 fix works; this cell is Barrier 2 fix (independent)
- hub-spoke v3 — Stage 1.5 anisotropic encoder; this cell can use it if Wave D HARD_PASSes

## Dispatch sequence (proposed)

1. Wait for Wave D hub-spoke v3 landing
2. If hub-spoke v3 HARD_PASS → ship this cell with hub-spoke encoder
3. If hub-spoke v3 MIDDLE_BAND/FAIL → ship this cell with word2vec sparse-bipolar (matches rail; still tests the role-tagging mechanism independently of encoder upgrade)

Either way, this cell ships. Encoder upgrade is multiplier, NOT prerequisite.

## Status

Not authored as code yet. Awaiting USER green-light to author + dispatch.
