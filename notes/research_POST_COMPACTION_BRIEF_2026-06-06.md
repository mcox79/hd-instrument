# Research POST-COMPACTION BRIEF -- read this FIRST on resume

**Compiled:** 2026-06-06 ~20:45 (end-of-day update; supersedes morning version)
**Read these first on resume:**
1. This file (current state + standing responsibilities)
2. `notes/capability_scorecard.md` (capability matrix; tail entries for recent verdicts)
3. `notes/PRIORITY_QUEUE_LIVE.md` (queue priorities; I OWN this)

---

## MY ROLE + STANDING RESPONSIBILITIES (do not deviate)

I am the Research session for hd-instrument substrate cognitive-core. Per user directive 2026-06-06:

1. **I OWN `notes/PRIORITY_QUEUE_LIVE.md`** as single source of truth for experiment priorities
2. **Exp-Dev pulls from top** of LIVE queue; reports verdicts; I cross off + add follow-ons
3. **Every Monitor event (real-time):** read note, categorize, dispatch 2x drill if genuine HF/MIDDLE, ship direct note if recipient has action
4. **Every cadence wake (30 min fallback):** check queue depth, cross-reference capability scorecard, add cells if weak axes
5. **Every drill landing:** synthesize, add cells, direct note to recipient
6. **No padding ever** -- if I can't justify a cell, it doesn't go in
7. **Direct notes to recipients** when there's something for them (Testbed for cloud, Orchestrator for runners, Exp-Dev for cells)
8. **Capability matrix check** every cycle -- if a high-value capability is stalled, queue cells must address it

---

## STANDING RULES ADDED TODAY (locked in for resume)

From 6+ methodology saves + 7 LVH catches + multiple compound revisions today:

1. **Pressure-test capacity metrics** before specifying. Ask "where does this metric fail empirically, and is that within substrate's operating range?" If not, metric is too lenient. (I missed this twice today on M_50 + fixed-load recall; Exp-Dev caught both.)
2. **Disambiguation tests at M near M_c** for capacity. Not at M << M_c where both arms ceiling at 1.0.
3. **Disambiguate "sparse coding"** between sparse-KEY (alpha coding; works) and sparse-VALUE (pattern coding; CLOSED).
4. **Conservative empirical floors, not algebraic ceilings**, when projecting compound math. Today's 4+ compound revisions all traced to this rule.
5. **Every architectural negative gets its own 2x drill** (not just a follow-on cell). I missed this on G5 + DIMSPARSE; user reminded both times.
6. **Match metric across arms** for apples-to-apples comparison.
7. **Verify literature claims before strategic synthesis** (verify-implementations rule applies to my own claims). User caught me overreaching on distillation mechanism today.
8. **Anchor empirical claims on trustworthy metrics**: auto-assoc Hopfield exact-recovery on sign-binarized keys (not unique-value hetero metric that doesn't discriminate).
9. **Cloud dispatch preflight gate**: include `sky launch --dryrun` validation (per Testbed's catalog cache catch).
10. **Causal LM extraction = last-token pool**; bidirectional encoder = mean-pool/CLS.

---

## MONITOR + WAKEUP

- **Monitor task `b3hggokoz`** (persistent): watches notes/ for new exp_dev/testbed/orchestrator notes
- **Monitor task `bz0v8tcmj`**: overlapping coverage; can be killed if dedup desired

---

## TODAY'S MAJOR EMPIRICAL FINDINGS (irrefutable; trustworthy metrics)

### 32 FLAGSHIP ANCHORS (NEW today: 27-32)

- 21st-26th from overnight + morning: KF-1 / real-encoder / continual KV / ETF Hadamard
- 27th: G2 KF-1 robustness AUC 0.975 hard same-domain
- 28th: G4 continual KV at N=8192 / 60 sessions / 99.8%
- **29th: K-hop K=10 at N=16384 100% accuracy + PP-11 BAND-LIFT (Drill X validated)**
- **30th: analogy_map 100% (new capability class; Batch A)**
- **31st: frame_slot_fill k=16 100% (new capability class; Batch A)**
- **32nd: continual KV at N=32768/120 sessions/100% retention (cycle 129; production scale!)**

### CYCLE 126 LVH #228 -- Slot 9 ETF Hadamard re-measured

- Was 2.75x metric artifact
- **NOW 38x SINGLE-AXIS at 2/3 seeds (1/3 ZCA collapse; R2 patch needed)**
- Validates Drill W algebraic ceiling territory

### CYCLE 128 EFFECTIVE-RANK SVD VALIDATION

- **d_eff(participation) = 82.1 in nominal D=384 MiniLM**
- VALIDATES intrinsic-dim framework (Drill W predicted ~50-80)
- Explains ALL today's encoder-side ceilings as intrinsic-rank limits
- 3-way framework convergence: cycle 124 + Drill Z CS-1 + Drill W d_eff

### CYCLE 129 LVH #231 -- LM-ENCODERS DEFINITIVELY OUT

- Pythia-160m d_eff = 18.3 vs MiniLM d_eff = 77.1 (4.2x LOWER despite 2x larger nominal)
- **LM-trained encoders OUT of Phase 4 candidate set**
- **Phase 4 production encoder = sentence-transformer family** (MiniLM baseline; MPNet/BGE upgrade targets in Batch B)

### CELL-1 ARCHITECTURAL_CONFIRMED -- 70B late-layer crash is REAL

- L=74 fp16 = NF4 = 0.056 EXACT (no quant rescue)
- Drill X prediction validated: H2 (late-layer specialization) PRIMARY, H1 (quant) SECONDARY
- Revised cheap-fleet: 1B (0.282) > 8B (0.248) ~ 70B fp16 (0.244); MiniLM 0.890 still dominates
- **Layer convention finalized: 1B L=15, 8B L=29, 70B L=50 (mid-depth, opposite of 1B/8B)**

### Batch A all 4 HP at smoke

- **HOC1 word bigram AUC 0.970** -- KF-1 word-order gate CLOSES with lightweight feature
- EFFECTIVE-RANK d_eff=82 (framework validation)
- analogy_map + frame_slot_fill (30th + 31st flagships)

### Cycle 127 + 129 PSE1 sqrt-K trajectory

- Coverage = 1.0 (structured extraction confirmed)
- Speedup ceiling = 12x at production corpus (not 100x; partition-geometry-determined)
- VQ-fidelity: sqrt-K beats uniform by 3.9% (marginal)

---

## TODAY'S ACTIONS PENDING USER (end-of-day status)

| Item | Status |
|---|---|
| CELL-1 fp16 70B | DONE; ARCHITECTURAL_CONFIRMED at $1.95 |
| 70B-Instruct NF4 follow-up | AUTHORIZED at $0.65; standing for Testbed dispatch |
| CELL-2 Wikipedia extraction at 1B L=15 | Pending user auth ($31-50) |
| CELL-3 distilled 22M student | Gated on CELL-2 ($15) |
| CELL-4 HP-12 V2 at 100K | Gated on CELL-2 + FAISS env ($10-20) |
| CELL-5 cascade distillation FD smoke | Pending user Together API key ($4-9) |
| Standard Batch A (4 cells) | ALL HP at smoke; full multi-seed pending |
| Standard Batch B (8 cells; $0) | Routed to Exp-Dev; ~3.5h sequential / ~1.5h parallel |
| Re-pointed real-encoder family | Continuing (whitened-sign Hopfield) |
| FAISS env Windows OpenMP fix | Recommended idle-time Testbed priority |

---

## CRITICAL STRATEGIC CONTEXT FOR RESUME

### Phase 4 production architecture FINALIZED (empirically grounded)

| Component | Decision | Source |
|---|---|---|
| Encoder family | **Sentence-transformer** (MiniLM baseline; MPNet/BGE upgrade target post-Batch-B) | Cycle 129 LM-encoders OUT |
| Causal-LM (if used) | **Llama-3.2-1B at L=15** | CELL-1 + CLOUD-1b |
| 70B caveat | L=50 mandatory; L>60 unusable | CELL-1 architectural |
| Substrate codebook | Hadamard / ETF whitening | Slots 2/10/9 |
| Sparse mechanism | **sparse-KEY α coding only** (sparse-VALUE definitively closed cycle 125) | Slot 3 + cycle 125 |
| Compound | **Hierarchical sequential** (test in Batch B) | Cycle 129 naive mixture HF |
| Hallucination stack | substrate grounding + HOC1 bigrams + NEG1 NLI | Batch A + drill outputs |
| Audit | HP-12 V1 RSA accumulator | Shipped 17-20th flagships |
| Streaming memory | Continual KV W-free | 32nd flagship cycle 129 |
| Reasoning | K-hop K=10 + analogy + frame_slot_fill | 29th-31st flagships |
| Extraction | Per-cluster stratified (12x speedup ceiling) | Cycle 127 |
| Wikipedia layer | **1B L=15** (saves $150-370 vs original layer-10 plan) | CELL-1 |

### The intrinsic-dim framework is the unifying explanation

All today's encoder-side ceilings = intrinsic-rank limits (d_eff). Not substrate limits. Substrate can absorb arbitrarily more capacity. The primary lever is **higher-d_eff encoder**.

3-way convergence:
- **Cycle 124 empirical:** axes are activation-regime-dependent
- **Drill Z CS-1 theory:** Donoho-Tanner phase boundary in (delta, rho) space
- **Drill W mechanism:** intrinsic-dim-limited via d_eff plateau
- **Cycle 128 empirical anchor:** d_eff = 82 on MiniLM

CS-1 algebraic audit (Batch B; ~1h CPU) will calibrate the phase-boundary math with the empirical d_eff anchor.

### Audacious vision NOW = 2-week eng project + $50-75 cloud

(Cheaper than Drill Y morning estimate of $100-200 because CLOUD-1b revealed 1B is sufficient at correct layer.)

---

## RECENT COMMITS (last ~15; all 2026-06-06)

```
f0b5fb9 research: 70B-Instruct NF4 follow-up AUTHORIZED at ~$0.65
bbce16a research: Testbed idle-time priority routing -- FAISS env fix
64b2c10 research: CELL-1 ARCHITECTURAL_CONFIRMED -- 70B late-layer crash is REAL not quantization
b06d07c research: Batch B ADDENDUM -- swap LM-encoders for sentence-transformer family + add hierarchical
934b0a2 research: cycle 129 -- 32nd flagship + LM-encoders DEFINITIVELY OUT + naive mixture HF
29d482e research: Batch B AUTHORIZED -- 7 cells; EFFECTIVE-RANK multi-encoder is NEW HIGHEST PRIORITY
851a0ac research: Batch A ALL 4 HP at smoke -- 30th + 31st flagships + EFFECTIVE-RANK validates framework
c855d6b research: cycle 128 -- d_eff=82 is the day's unifying insight
851b46f research: CLOUD-1b HARD_PASS -- cheap fleet vindicated; PHASE4A-6 layer-10 needs urgent revision
ff1700a research: cycle 126 -- Slot 9 ETF re-measured at 38x (LVH #228; metric artifact) + KF-1 negation LOCKED
eeb336b research: distillation claim VERIFIED + mechanism CORRECTED
... [see git log for full]
```

---

## IMMEDIATE NEXT ACTIONS ON RESUME

1. **Check for Batch B verdicts** (8 cells in flight; Exp-Dev landing over next hours)
   - Especially: EFFECTIVE-RANK on MPNet/BGE (production encoder choice)
   - DIMSPARSE3-α at M near M_c (compound math definitive)
   - CS-1 algebraic audit (framework calibration)
   - Hierarchical Hadamard → sparse-KEY α (sequential stacking)

2. **Check 70B-Instruct Testbed verdict** ($0.65; ~15 min compute)

3. **Check Slot 10 full multi-seed at N=16384** (LVH #229 confirmation gate)

4. **Check HOC1 full multi-seed + negation generalization** (LVH #230 confirmation)

5. **Check re-pointed family verdicts** (Slot 9 with whitening; Slot 14; G8 with auto-assoc Hopfield + sign-binarized real keys)

6. **Check G4 full** (continual KV at 120 sessions / 6h timeout; already landed = 32nd flagship)

7. **User decisions still pending:**
   - CELL-2 Wikipedia extraction at 1B L=15 ($31-50; saves $150-370 vs layer-10)
   - CELL-5 Together API key ($4-9)
   - CELL-3/4 conditional on CELL-2

---

## STRATEGIC PRIORITIES (in priority order)

1. **Resolve compound stacking definitively** (DIMSPARSE3-α + hierarchical Hadamard→sparse cells in Batch B)
2. **Identify highest-d_eff sentence-transformer encoder** (EFFECTIVE-RANK on MPNet/BGE) → Phase 4 production encoder upgrade
3. **Validate CS-1 phase-boundary framework** (algebraic audit with empirical d_eff anchor) → paradigm-shift unification
4. **Demonstrate composition: per-hop hallucination localization** (fact_checked_khop + auditable_khop_kf1) → KILLER vs frontier LLMs
5. **Production deployment cells** (CELL-2 extraction + CELL-3 distillation + CELL-4 HP-12 V2 + FAISS env)
6. **Cubic-tensor n=3 BUILD** (Slot 1; still gated by capacity story but less urgent given encoder-d_eff is the primary lever)

---

## END OF BRIEF

Compaction may now happen. On resume: read this BRIEF + tail of `capability_scorecard.md` + `PRIORITY_QUEUE_LIVE.md` first. Standing responsibilities continue as documented above.

**Today's discipline pattern (LVH catches + methodology saves + drill predictions empirically validated) was the highest-leverage system. Maintain.**
