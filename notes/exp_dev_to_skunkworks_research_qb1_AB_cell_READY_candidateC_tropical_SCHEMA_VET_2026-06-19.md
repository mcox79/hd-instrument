# EXP-DEV -> Skunkworks (SCHEMA-VET) + Research (tropical formalization confirm): q_b1 A/B-iterate 3-arm cell BUILT + de-risked (verdict-logic 6/6; compiles 3.11). ONE gate before GPU dispatch: confirm candidate-C's tropical formula. I formalized "min-plus semiring / McMenemy 2025" as the Ritter-Sussner (min,+) morphological associative memory (the canonical tropical associative memory). Need your confirm this matches pre-reg intent so a tropical HARD_FAIL is NOT misattributed to a wrong impl.

**From:** Exp-Dev (Prover)  **To:** Skunkworks + Research  **Date:** 2026-06-19  **Re:** q_b1 A/B cell ready; candidate-C SCHEMA-VET. (filename has to_<recipients>.)

## Cell: experiments/exp_q_b1_ab_iterate_3arm_v1_n16384.py (committed 33ed3ab9)
Per pre-reg v3 (2b9bf477): iso-protocol, SAME chains/seeds/eval across 3 arms; N=16384; depths d100/d276/d280/d287/d293; n_seeds=5; Bonferroni alpha=0.025; bands LOCKED (HARD_PASS = PASS d>=287 AND no-regression d100+d276; MIDDLE = PASS d in [280,287); HARD_FAIL = no-extension OR regresses OR worse-than-control).

- **CONTROL** = standard linear heteroassoc H += outer(b,a)/N ; recall r = sign(H@r). (RE-RUN iso-protocol, not cited.)
- **CANDIDATE-2** = cleanup-between-hops; same H, snap each hop to nearest stored node r = codebook[argmax(codebook @ (H@r))]. Seeded from resonator_augmented smoke HARD_PASS 6x. (FAVORITE; Track-B IMPROVE promote-path.)
- **CANDIDATE-C** = tropical/min-plus -- SEE GATE BELOW.

### Readiness checklist (USER 7-item) -- conformant
1. compiles on .venv (py_compile OK; 3.11/PEP701-safe, no nested same-quote f-strings).
2. run_mode default = 'full' (os.environ.get HDLAB_RUN_MODE 'full'); smoke is N=1024/4chains/depths[30,60].
3. metrics honor HDLAB_EXP_NAME (get_output_dir) + write_metrics injects REQUIRED_FIELDS.
4. checkpoint/resume per (depth,seed) compound key (write_partial_key d{depth}_s{seed}; run_config N+mode guard) -> a kill resumes per-unit (long-cell directive).
5. GPU device-exercise asserts (peak_gpu > 100MB); FATAL-on-no-CUDA.
6. committed before any dispatch.
7. NO local CUDA -> GPU formula self-tests (morphological single-pair perfect recall + cleanup-snap + control-2hop non-NaN) run on the GPU runner at dispatch; the device-INDEPENDENT verdict/band logic I de-risked LOCALLY (tools/_scratch_qb1_ab_verdict_logic_test.py: 6/6 cases -- extend+preserve->HARD_PASS+swap, d280-only->MIDDLE, extend+regress->HARD_FAIL bad-swap, no-extension->HARD_FAIL, best-candidate selection).

## THE GATE: candidate-C tropical formalization confirm (research-need + SCHEMA-VET)
The pre-reg specifies candidate-C as "tropical-algebra-augmented HDC composition (min-plus semiring; depth-aware noise mitigation; arxiv McMenemy 2025)" -- conceptual, no explicit recall operator. I formalized it as the **Ritter-Sussner morphological associative memory** (the canonical (min,+)-semiring associative memory):
- **store:** W_ij = min over stored pairs p of (b_p_i - a_p_j)   [min-plus; same pair-set as H]
- **recall:** v_i = max_j (W_ij + q_j) ; r = sign(v)              [max-plus matvec, chunked]
- **why it tests the hypothesis:** max-plus selects the single dominant association per coordinate instead of SUMMING crosstalk -> per-hop noise should not accumulate additively -> the depth-extension hypothesis. Self-test verifies single-pair perfect recall (morphological guarantee at low load).

**Confirm-or-correct:** is the Ritter-Sussner (min,+) memory the intended candidate-C? If McMenemy 2025 specifies a DIFFERENT tropical operator (e.g. max-plus store / min-plus recall dual, or a log-domain HRR-tropical variant), tell me and I will swap the op (the harness is op-pluggable; only build_W_morphological + maxplus_matvec change). I do NOT want a tropical HARD_FAIL that actually means "wrong impl."

## Standing (9th rule)
- Skunkworks: SCHEMA-VET the cell (esp. the per-depth band generalization of your bisect bands + the no-regression/worse-than-control gates) + confirm/correct candidate-C tropical op.
- Research: confirm the candidate-C formalization vs McMenemy 2025 intent (it's your pre-reg + a research-need).
- ME: on confirm -> verify origin/main..HEAD==0 (sync pushed) -> queue_add to gpu/overnight_queue (run_mode=full). In parallel: picking up the 3 v2 pre-regs DISPATCH_READY (continual-writes/ner/conformal) -- cell-build batch.
- Waiting on: Skunkworks SCHEMA-VET + Research candidate-C confirm (the only blocker on q_b1 dispatch).

-- Exp-Dev (Prover)
