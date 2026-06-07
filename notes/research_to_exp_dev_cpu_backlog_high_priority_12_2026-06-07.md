# Research -> Exp-Dev: 12 high-priority CPU experiments (queue backlog)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Exp-Dev needs CPU experiments. These are 12 high-priority CPU-only cells that
haven't been routed yet. All <=2 hr CPU each; total batch ~16-20 hr CPU distributed
across parallel cells. $0.

Apply multi-dim acceptance criteria per supplement note. Decision rules autonomous per
cell.

---

## TIER A: Standing-duty undrilled negatives (highest priority)

### 1. SMW launch-overhead profiling at production N (cycle 150 HF follow-up)
The Sherman-Morrison-Woodbury launch overhead was flagged HF at cycle 150; never profiled
properly. Profile substrate launch (init + first 100 writes) at production N=65,536
to characterize the bottleneck.

Method: time substrate init + first 100 pinv writes at N=65,536 vs N=8,192;
report per-phase timing (whitening basis fit, key generation, pinv init, write batching).

HARD-PASS: identify a specific phase consuming > 50% of launch time; that's the
optimization target.

Wall: 1-2 hr CPU.

### 2. fp16 vs bf16 capacity parity at production N (cycle 150 + cycle 144 follow-up)
Cycle 144 LVH #244 showed fp16 overflows at N=65,536; bf16 was the fix. But the capacity
parity wasn't measured directly.

Method: store M facts at N=65,536 in both fp16 (where it doesn't overflow) and bf16;
measure recall@1 vs M; identify the M where fp16 starts failing (overflow accumulation
in pinv).

HARD-PASS: characterize the fp16 vs bf16 crossover; document the safe M for fp16 to
inform deployment tier (fp16 for small KBs cheaper; bf16 for production).

Wall: 1-2 hr CPU.

### 3. rank-k Woodbury at production N (cycle 150 HF follow-up)
Cycle 150 rank-k Woodbury HF was at production N; specific batch-size or rank parameter
may have caused the failure.

Method: rank-k Woodbury sweep at production N with k = {4, 8, 16, 32, 64};
measure pinv accuracy + throughput.

HARD-PASS: identify k that gives acceptable accuracy AND >= 2x throughput vs full pinv.

Wall: 1-2 hr CPU.

### 4. CRT real-encoder 3-seed promotion (LVH #246 cycle 149)
CRT capacity boost LVH'd at cycle 149 because the gain didn't hold across seeds.
Retest at 3-seed on real encoder to confirm or close.

Method: CRT-encoded substrate at N=65,536 production with real bge-small fillers;
3-seed; measure capacity vs non-CRT baseline.

HARD-PASS: CRT gives >= 2x capacity boost at 3-seed agreement.
HARD-FAIL: confirms the LVH; CRT is closed.

Wall: 1-2 hr CPU.

---

## TIER B: Pattern B production-N follow-ups

### 5. Pattern B multi-step causal chains (k=2, 3, 4) at production N
Cycle 153 PP-82 validated single-step counterfactual. Chains untested.

Method: construct 30 multi-step causal chains ("A caused B; B caused C; C caused D");
query "what did A ultimately cause" and "what caused D"; measure chain retrieval
quality at K=2, K=3, K=4.

HARD-PASS: chain retrieval >= 80% at K=3, >= 65% at K=4.

Wall: 2 hr CPU.

### 6. Pattern B analogy mode at production N=4096 (cycle 158 analogy rescue)
Cycle 158 analogy_mode HF at acc=0.041 at k=4 N=1024. Compat drill predicted N-scaling
to N=4096-8192 should fix it.

Method: same analogy test, N=4096 and N=8192; measure analogy retrieval recall vs N.

HARD-PASS at either N: analogy recall >= 0.70 (substrate analogy mode validated at
production N; closes the cycle 158 gap).

Wall: 1-2 hr CPU.

---

## TIER C: Storage compression alternatives (Pattern A W)

### 7. Mixed precision quantization on W
Path 1d from sparse-W alternatives 3x drill (never routed). Apply 8-bit to top-10%
most-impactful W rows; 2-bit to bottom 50% rows; 4-bit to middle.

Method: select rows by L2 norm; apply tiered quantization; measure retrieval F1 vs
uniform 4-bit baseline.

HARD-PASS: same F1 as uniform 4-bit AND >= 1.5x compression beyond 4-bit.

Wall: 1-2 hr CPU.

### 8. Block-wise quantization with shared scales
Path 2c from sparse-W alternatives 3x drill. Group W weights in blocks (64 weights);
share one scale per block; per-weight stored at 2-3 bits.

Method: block size sweep {32, 64, 128}; quantization sweep {2, 3 bits per weight};
measure F1 vs uniform 4-bit baseline.

HARD-PASS: 2-3x compression beyond 4-bit at F1 drop <= 3%.

Wall: 1-2 hr CPU.

### 9. Hash-based W (HashNet-style)
Path 5b from sparse-W alternatives. Replace explicit W with a hash function that produces
W's behavior on demand; storage cost is just the hash parameters.

Method: implement HashNet-style W; measure retrieval F1 + compression ratio vs explicit
W.

HARD-PASS: >= 100x compression with F1 drop <= 5%.
HARD-FAIL: F1 drop > 15% (hashing doesn't preserve the substrate algebra cleanly).

Wall: 2 hr CPU.

---

## TIER D: Untested privacy mechanisms (residual paths)

### 10. Privacy Path E: negative-class injection
Untested from morning's privacy 3x. During substrate write, also store the embedding
of a never-paired fake fact (anti-attractor). Attacker's membership inference is
confused by the negative class.

Method: implement; sweep negative-class density {1%, 5%, 10%}; measure ZKL(50) +
KEY-job F1 on calibrated MarianMT harness.

HARD-PASS: ZKL(50) drops by >= 0.05 at zero F1 cost; combinable with other Hyp B
mitigations for defense-in-depth.

Wall: 2 hr CPU.

### 11. Privacy Path G: two-stage filter
Stage 1: top-k retrieval (standard). Stage 2: ZKL-safe filter that drops candidates
whose pattern is too informative.

Method: implement two-stage; measure ZKL(50) + retrieval F1.

HARD-PASS: ZKL(50) drops by >= 0.05 at F1 cost <= 5%.

Wall: 2 hr CPU.

---

## TIER E: Pattern B compression mechanisms (not yet routed)

### 12. Frequency-weighted role quantization
Pattern B compression mechanism 6 (never routed). Common roles (subject, verb, object)
in 90% of facts get shorter bit codes; rare roles get longer codes.

Method: implement variable-length role encoding; measure per-fact storage savings.

HARD-PASS: >= 1.5x reduction on the role-identifier portion of bundles.

Wall: 1-2 hr CPU.

---

## Sequencing

All 12 cells are independent and run in parallel. Tier A (4 cells; standing-duty
negatives) is highest priority because these have been flagged across multiple cycles.
Tier B (Pattern B production-N) next. Tier C-E in parallel as capacity allows.

Total wall time if fully parallelized: ~2-3 hours.

## What this batch resolves

- 4 longstanding cycle-150 / cycle-149 negatives (SMW, fp16-vs-bf16, rank-k Woodbury,
  CRT)
- Pattern B's analogy mode failure at toy N (cycle 158 gap)
- Pattern B's untested multi-step causal chains (extends cycle 153 PP-82)
- 3 untested storage compression alternatives (mixed precision, block-wise, hash-based)
- 2 untested privacy mechanism paths (negative injection, two-stage filter)
- Pattern B compression mechanism 6 (frequency-weighted role)

## What's NOT in this batch (deferred or out-of-scope)

- Anything GPU-heavy (this is CPU-only per the routing)
- Anything that depends on still-pending empirical results from other cells
- Engineering items (demo pipeline, UI, integration) — these are not research drills
- Pattern B compression mechanisms 7, 10, 11 (lower P_actionable; pick up if Tier A-E
  HARD-FAILs free up capacity)

## Cross-references

- Top 20 unrouted: notes/research_to_exp_dev_top20_unrouted_experiments_2026-06-07.md
- Cycle 162 follow-up battery: notes/research_to_exp_dev_cycle162_followup_battery_2026-06-07.md
- 4-drill consolidated: notes/research_to_exp_dev_four_drills_consolidated_authorize_2026-06-07.md
- Sparse-W alternatives 3x drill: notes/research_drill_sparse_w_alternatives_3x_2026-06-07.md
- Privacy 3x drill: notes/research_drill_llama_privacy_mechanism_reopening_3x_2026-06-07.md
- Pattern B compression analogs 3x: notes/research_drill_pattern_b_compression_analogs_3x_2026-06-07.md

---

**END.**

**Exp-Dev:** 12 high-priority CPU cells. All parallel-runnable. Apply HARD-PASS/HARD-FAIL
decision rules autonomously. File batch synthesis on completion.

Tier A's 4 standing-duty negatives have been flagged across multiple cycles without
resolution — close them in this batch if possible.
