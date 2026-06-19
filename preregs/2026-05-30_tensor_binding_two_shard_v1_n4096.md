# Pre-registration: tensor_binding_two_shard_v1_n4096

Date: 2026-05-30
Anchor: tensor_binding_two_shard_v1_n4096
Track: B (cross-shard relational) Phase 1 of 3 (two-shard tensor binding gate)
Script: experiments/exp_tensor_binding_two_shard_v1_n4096.py
Queue: overnight_queue (GPU)
Timeout: 14400s (PROT-019 _n4096 floor)
N-suffix: _n4096 -> production N = 4096 (PROT-018 binding contract)

## Scientific question

Two substrate shards W_A (customer -> email) and W_B (customer -> phone)
share a key space. Does the tensor-bound query route correctly to the right
shard and yield the same decoded answer as the sequential per-shard baseline?

Canonical form (per user msg 1 spec):
  Sequential:    r_email = W_A k_X;  r_phone = W_B k_X.
  Tensor-bound:  q_email = k_X (*) k_email_role;  r_relational = W_A q_email.
                 q_phone = k_X (*) k_phone_role;  r_relational = W_B q_phone.

The bind operator (*) is BSC element-wise multiply (the involutive analog of
HRR tensor product). The substrate's response to the bound query should
isolate the role-specific value of the requested type if the bind structure
is preserved through the matmul.

## Decision context (msg 1 staging)

If two-shard tensor binding works (HARD_PASS), ship T2 P2 (3-shard
tensor binding). If it does not (HARD_FAIL), cross-shard relational
operations close; sequential per-shard composition is the only path.

## Design

- N=4096, BSC-equivalent Kerdock_4coset codebook.
- 2 shards (K=2): W_A stores 50 (customer_key, email_value) pairs;
  W_B stores 50 (customer_key, phone_value) pairs.
- The same 50 customer keys are stored in both shards (shared key space).
- Independent value assignment per shard for each customer.
- 2 codewords reserved as ROLE keys (k_email_role, k_phone_role).
- 5 seeds: [7, 17, 23, 31, 41] for fact selection.
- 100 test queries per seed (50 email + 50 phone).
- 5 cell-seeds total at FULL.

## Metrics (per cell)

1. sequential_acc: fraction of 100 queries where BOTH
     decode(W_A k_X) == v_email_X AND decode(W_B k_X) == v_phone_X.
2. tensor_acc: average per-query accuracy across BOTH 50 email + 50 phone
     tensor-bound queries.
3. tensor_vs_sequential_match: fraction of 100 queries where the
     tensor-decoded result EQUALS the sequential-decoded result exactly.
4. latency_ratio: tensor_total_time / sequential_total_time.

## Pre-registered bands

HARD_PASS:
  tensor_acc >= 0.85 AND tensor_vs_sequential_match >= 0.90
  in >= 3/5 seeds.

HARD_FAIL:
  tensor_acc <= 0.50 OR tensor_vs_sequential_match <= 0.50
  in >= 50% of seeds.

MIDDLE_BAND:
  0.50 < tensor_acc < 0.85; useful for some queries but not all.

## Formula self-tests (verified in `_instrumentation_selftest`)

1. N == 4096 (PROT-018 binding).
2. K_SHARDS == 2; 50 customers; 100 queries/seed at FULL.
3. BSC bind involution: bind(bind(a, b), b) == a for sign vectors.
4. Verdict gates: HARD_PASS, HARD_FAIL, MIDDLE_BAND fixtures classify correctly.

## Smoke result (CPU, N=1024, 8 customers, 1 seed)

  seed17: seq_acc=1.000  tensor_acc=0.375  tensor_vs_sequential_match=0.375
          latency_ratio=0.870

  smoke wall: 0.17s (CPU). Verdict: TBIND_HARD_FAIL at smoke because
  tensor binding does not preserve the customer key cleanly through W_A/W_B
  in the BSC bind form.

  IMPORTANT: tensor_acc=0.375 is significantly above pure chance
  (1/C ~ 1/C_smoke ~ 1/(C at N=1024 Kerdock-4-coset) << 0.375), indicating
  SOME bind information survives but most is lost. This is the gate signal
  the user requested -- whether the partial signal scales to actionable
  accuracy at N=4096 is the FULL-run question.

  Per role contract: smoke shows real signal (not all-zero, not constant,
  not instrumentation-suspect). PROCEEDING TO SHIP. FULL outcome is the
  gate answer.

## OOM check

W_A + W_B: 2 * 4096^2 * 4 = 128MB. Codebook: ~256MB. Query buffers: <1MB.
Total < 500MB. Well under 6GB ceiling.

## Timeout estimate

smoke_wall_s = 0.17 (CPU, 1 cell-seed smoke).
FULL has 5 cell-seeds (5x), N=4096 vs N=1024 (4x), 100 queries per cell
vs 16 at smoke (~6x). Per-query: matmul N*N (W @ q). scaling_exp = 1.5.
  ceil(1.5 * 0.17 * 4^1.5 * 5 * 6) = ceil(1.5 * 0.17 * 8 * 30) = 62s CPU
GPU much faster; expected GPU wall < 30s.

User-specified timeout: 14400s. Generous; PROT-019 _n4096 floor.

## Outcome handlers (post-verdict)

- HARD_PASS -> file strategy_request_to_exp_dev for T2 P2 (3-shard tensor
  binding); cap_map row "cross-shard tensor binding" advanced.
- HARD_FAIL -> close Track-B; cap_map row marked X with sequential
  composition as the fallback path.
- MIDDLE_BAND -> diagnostic: which query types work; ship rescue (e.g.,
  alternative bind operator: HRR circular convolution rather than BSC
  element-wise multiply) before deciding.
