# Research -> Exp-Dev + Testbed: HP-9 HP ack + FAISS HNSW env hang + 2x drill on MIDDLE/NEGATIVES dispatched

**From:** Research session
**To:** Exp-Dev (HP-9 ack) + Testbed (FAISS env fix)
**Inform:** Orchestrator + User
**Date:** 2026-06-05 ~17:00
**Subject:** HP-9 multimodal HARD_PASS acknowledged (16th flagship anchor). FAISS HNSW environment hang flagged to Testbed runner-env lane. 2x rescue drill dispatched on today's MIDDLE-band + HARD_FAIL findings (theta-burst, cerebellar, HotpotQA, EX-CONCEPT bigram-ceiling).

---

## HP-9 multimodal HARD_PASS acknowledged (16th flagship anchor)

Per Exp-Dev 14:54 note: HP-9 multimodal (pure-numpy) ran HP while HNSW empirical blocked. VSA's modality-agnostic claim empirically validated.

**Updated flagship count: 16 anchors** (was 15 + HP-9).

Implementation note: pure-numpy implementation means substrate can demonstrate cross-modal binding without GPU/cloud dependencies. Adds to demo material for HP-12 (could show cross-modal retrieval in extended demo if useful for product positioning).

---

## FAISS HNSW environment hang (Testbed action)

Per Exp-Dev 14:54 note: substrate_hnsw_sublinear_cleanup_v1 HANGS at IndexHNSWFlat.add() at M=10000 on runner. Root cause: OpenMP conflict between faiss libomp140 and numpy/MKL libiomp5md on Windows.

**This blocks HP-12 V2 critical path** (sub-linear cleanup at 100K+ scale).

Testbed options (per Exp-Dev's note):
- (a) Install faiss-cpu in a way that shares numpy's OpenMP (conda faiss-cpu often bundles compatible OMP)
- (b) Clean venv with faiss + numpy from same OpenMP toolchain
- (c) Run HNSW cell on small Linux CPU cloud box (~$0.50)

**Recommendation:** option (a) conda faiss-cpu is the cheapest first try. If that fails, option (c) cloud is straightforward fallback. Option (b) clean venv is the most thorough but slowest.

This is genuinely runner-env work, not strategic research. Testbed lane.

---

## 2x rescue drill DISPATCHED on MIDDLE/NEGATIVE findings

Per [[feedback-pressure-test-negative-findings]] + [[feedback-negative-results-2x-research]]: every "substrate cannot do X" claim treated as operating-mode-specific hypothesis; enumerate rescue paths before accepting.

Today's NON-clean-HP findings to drill:

### MIDDLE-band

1. **HotpotQA multi-hop Q&A** (10:05): substrate 2-hop mechanism works 1.20x; end-to-end EM 0.083 (Pythia decoder floor)
2. **EX-CONCEPT-1-real at Llama-1B** (12:31): substrate 0.727 vs bigram 0.716 (bigram-level confirmed at 1B; not Pythia-specific)

### HARD_FAIL (architectural puzzles)

3. **THETA-BURST-1** (11:34): novel hippocampal multi-step trajectory write didn't deliver. Algebraic case strong; bipolar implementation gap.
4. **CEREBELLAR-EXP-1** (11:34): novel cerebellar random-expansion (capacity O(N) -> O(N^2) claim) didn't deliver.

Drill addresses:
- Why each failed (post-mortem: algebra wrong vs implementation gap vs operating-mode wrong)
- 2-3 rescue paths per finding within substrate's structural moats
- Honest verdict: RECOVERABLE / BOUNDED / UNCLEAR
- Recommended next-step cell per recoverable finding
- Architectural closure language per bounded finding

Plus cross-domain probe: are novel-architecture empirical failures recurring in bipolar associative memory because of a known specific algebraic reason?

ETA ~25 min sonnet.

---

## Why this drill matters strategically

Today's pipeline is dominated by clean HARD_PASSes (16 anchors). The NON-clean-HP findings represent honest architectural gaps. Drilling them:

1. **Closes vs preserves architecture decisions:** if the novel directions (theta-burst, cerebellar-exp) are recoverable, they could improve Phase 3+ capacity. If bounded, document the limit and move on.

2. **Sharpens demo narrative:** the bigram-ceiling on sequence prediction is the LIMIT of substrate cognitive-core. Drill clarifies whether the limit is at "neural-LM-class" (already known; depth gap is fundamental) or further architectural improvements within bigram-Markov class exist.

3. **Pre-empts user pushback:** "what doesn't substrate do well?" needs honest answers. Drill provides them.

4. **Phase 2/3 prep:** if HotpotQA EM bound is purely Pythia decoder limit, Llama-1B HotpotQA test should resolve it. If there's also a substrate-side limit, drill identifies what.

---

## Pipeline status (post-FAISS-hang)

**In flight:**
- HP-12 V1 build (per simplified 4-day plan; in flight)
- HP-7 V1 verdict (in flight)
- HP-5 medical Q&A (data delivered; building)
- K2-XOR-1B full verdict (mechanism confirmed; full pre-reg pending)
- CCC-1-v2 at 1B residual-only transfers (buildable)
- 2x rescue drill (research session; ~25 min)

**Blocked:**
- HNSW empirical (Testbed env fix needed)

**Standing for:**
- 2x rescue drill landing
- HP-7 V1 verdict
- HP-5 first verdict
- HP-12 V1 cheap decisive test (2-hour pre-build validation)
- Testbed FAISS env fix
- K2-XOR-1B full + CCC-1-v2 transfers

**Pipeline still well-loaded but FAISS hang is the new blocker.**

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary on HP-9 ack; Testbed primary on FAISS env
- Per [[feedback-pressure-test-negative-findings]]: 2x rescue drill on negatives
- Per [[feedback-negative-results-2x-research]]: drill before architectural closure
- Per [[feedback-no-padding-experiments]]: drill addresses 4 distinct architectural questions (not padding)
- ASCII-only

---

**END.**

**Exp-Dev:** HP-9 HP acknowledged (16th flagship anchor; pure-numpy multimodal validates VSA's modality-agnostic claim). FAISS HNSW hang correctly flagged to Testbed. 2x rescue drill running on theta-burst + cerebellar HFs and HotpotQA + EX-CONCEPT MIDDLE-band; output may surface V2 cells worth queueing.

**Testbed:** FAISS HNSW environment hang on runner (Windows OpenMP conflict). Three fix options: (a) conda faiss-cpu (cheapest first try; recommended); (b) clean venv with matched OpenMP toolchain; (c) small Linux CPU cloud box ~$0.50. Blocks HP-12 V2 critical path. Action requested when bandwidth allows.

**User:** HP-9 HP (16 flagship anchors total). FAISS env hang on runner kicked to Testbed (Windows OpenMP issue). 2x rescue drill dispatched on today's MIDDLE/NEGATIVE findings (theta-burst HF + cerebellar HF + HotpotQA MIDDLE + EX-CONCEPT bigram MIDDLE) per pressure-test-negative-findings protocol. Output ~25 min.
