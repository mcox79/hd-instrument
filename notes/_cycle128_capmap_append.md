
## v449 -> v450 -- 2026-06-06 CYCLE 128 (3 verdicts; 0 HP; 0 HF; 3 SMOKE-PASS; 2 LVH #229+#230)

**Trigger.** 3 orphan-recovered verdicts: substrate_etf_hadamard_n_sweep_capacity_v1 (Hadamard N-sweep smoke), hoc1_word_bigram_v1 (KF-1 word-bigram rescue smoke), effective_rank_svd_v1 (intrinsic-dim diagnostic).

### Step 0 honest re-read (MANDATORY)

**(1) substrate_etf_hadamard_n_sweep_capacity_v1 -- [label-vs-honest] LVH #229**
Labeled HARD_PASS. source=remote, run_mode=smoke, n_seeds=1.
Per-cell: N=1024 ratio=8.02x, N=2048 ratio=8.03x -- both exceed >=5x HP threshold. Ratios nearly identical (delta=0.01x) suggesting flat N-dependence.
LVH CATCH: run_mode=smoke, n_seeds=1. HARD_PASS from single smoke seed is an over-claim per PROT-021/022 and feedback-pre-reg-peak-not-final-HP-fragile. "Phase-3 linear capacity scales (~10x more facts)" extrapolation from 2 N-values is beyond what smoke supports.
Honest verdict: HP-SMOKE pending full multi-seed N-sweep. Signal is genuine and very promising.
LVH #229: label HARD_PASS but smoke n_seeds=1; honest = HP-SMOKE. HONEST: 977 -> 978 (+1).

**(2) hoc1_word_bigram_v1 -- [label-vs-honest] LVH #230**
Labeled HARD_PASS + "gate closes, no NLI needed". source=remote, run_mode=smoke, n_seeds=1.
Per-cell: auc_shuffle=0.970 (>> 0.90 HP threshold). Char-ngram baseline 0.19, MiniLM-only 0.22.
LVH CATCH: run_mode=smoke, n_seeds=1. "gate closes" is a closure-level declaration from 1 smoke seed.
Honest verdict: HP-SMOKE. Result is extremely strong (4.5x above char-ngram baseline) but gate-closed declaration requires multi-seed full run.
LVH #230: label HARD_PASS + gate-closes but smoke n_seeds=1; honest = HP-SMOKE, gate-open. HONEST: 978 -> 979 (+1).

**(3) effective_rank_svd_v1 -- LABEL HONEST**
Labeled HARD_PASS. source=remote, run_mode=smoke, n_seeds=1, n_enc=2000.
Per-cell: d_eff=82.1, rank90=164, rank99=287, D=384.
SVD is a deterministic measurement -- n_seeds=1 is appropriate. d_eff=82.1 < 120 threshold by 32%. Intrinsic-dim-limited finding definitively supported: 21% utilization of nominal D. No over-claim. NO LVH.
HONEST: 979 -> 980 (+1).

TOTAL HONEST: 977 -> 980 (+3). LVH: 228 -> 230 (+2; catches #229 and #230).

### Cap_map annotation (v449 -> v450)

**(1) substrate_etf_hadamard_n_sweep_capacity_v1 SMOKE-PASS [LVH #229; HP-SMOKE n_seeds=1 smoke].**
Hadamard lift persists across N: N=1024 ratio=8.02x, N=2048 ratio=8.03x (smoke single-seed). Ratio flat across N (delta=0.01x over 2x N-increase) -- ETF geometry appears scale-invariant. Consistent with v439 N=4096 ratio=10x (3-seed full): 3-N corroboration at smoke level (1024, 2048, 4096). Full multi-seed N-sweep (N in {1024,2048,4096,8192,16384}) is the next step to close the Hadamard N-sweep question and update Phase-3 plan.
Capacity-scaling row annotation: 'etf_hadamard_n_sweep HP-SMOKE v450: N=1024/2048 ratio=8.02/8.03x (smoke n_seeds=1; LVH #229; FULL multi-seed sweep required). Ratio flat across N -- consistent with N-independent ETF lift. 3-N corroboration with v439 N=4096 ratio=10x. Phase-3 floor upgrade deferred pending full multi-seed N-sweep.'
Band: UNCHANGED pending full run.

**(2) hoc1_word_bigram_v1 SMOKE-PASS [LVH #230; HP-SMOKE n_seeds=1 smoke; KF-1 adversarial rescue candidate].**
Word bigrams rescue KF-1 adversarial order-sensitivity: AUC_shuffle=0.970 vs char-ngram 0.19 and MiniLM-only 0.22 (4.5x improvement over best prior adversarial baseline). Mechanistically correct: word-level bigrams inject word-order signal as a separate channel independent of MiniLM encoder order-blindness. Architecturally distinct from the closed negation-detection rescues (v443/v444/v448).
KF-1 hallucination-detection row annotation: 'hoc1_word_bigram HP-SMOKE v450: AUC_shuffle=0.970 (smoke n_seeds=1; LVH #230; gate-closed declaration premature). Char-ngram baseline 0.19, MiniLM-only 0.22 -- 4.5x improvement. Word-order signal via bigrams is mechanistically correct. Full multi-seed run required to confirm gate closure. Active rescue R5 (adversarial training, v443) remains open as backup. hoc1 prefix = methodology tag.'
Band: KF-1 72-87% UNCHANGED (smoke-only; no band move on smoke). Band-lift candidate pending full multi-seed replication of auc_shuffle >= 0.90.

**(3) effective_rank_svd_v1 HARD_PASS [LABEL HONEST; intrinsic-dim diagnostic; DT framework validated].**
MiniLM encoder is intrinsic-dim-limited: d_eff=82.1 (participation-ratio), rank90=164, rank99=287, D=384, n_enc=2000. Encoder uses only 21% of nominal capacity (82/384). This is a structural constraint for all Phase-4A real-encoder operations. DT/intrinsic-dim-limited hypothesis CONFIRMED on MiniLM. Dim-expansion anchors (v441/v442/v444) were correctly operating in d_eff-limited regime; dim-expansion beyond d_eff is redundant until effective rank is improved (e.g. via larger encoder).
DT/intrinsic-dim framework annotation: 'effective_rank_svd v450: MiniLM D=384, d_eff(participation_ratio)=82.1, rank90=164, rank99=287 (n_enc=2000, deterministic). Real encoder capacity bounded by d_eff=82 not D=384. Phase-4A whitening (v441) can push toward d_eff ceiling; larger encoder (higher d_eff) is primary lever for Phase-4 capacity expansion.'
PP-8 sub-prop annotation (intrinsic-dim constraint): 'effective_rank_svd v450: MiniLM d_eff=82 confirmed. PP-8 real-encoder integration operates at d_eff=82 ceiling. Encoder with higher d_eff is primary PP-8 capacity lever. Dim-expansion above d_eff is redundant.'
No new row required. Portfolio 32+77 UNCHANGED.

### PROT compliance (v449 -> v450)

- PROT-004/006: No closures. 3 smoke-pass anchors. No rescue sketches required.
- PROT-007: v450 history row appended to substrate_capability_map_history.md.
- PROT-008: Annotation-only; 0 row state changes; 0 portfolio changes. 2 LVH catches (#229/#230). Validator not triggered.
- PROT-009: cap_map.md + substrate_capability_map_history.md + strategy_decisions_2026-06-06.md staged atomically; 362nd PROT-009 paired commit.
- PROT-018: No _nN suffixes. hoc1 prefix is methodology tag, not N-binding. CLEAN.
- PROT-021: All 3 source=remote. Smoke runs legitimate; over-labeled as HARD_PASS -- that is the LVH catch, not a PROT-021 violation.
- PROT-022: Single-seed smoke -- no multi-seed spread to check. N/A for smoke-only runs.

### Commit & push

Commit message: Cap map: v449 -> v450 CYCLE 128 (0 HP; 0 HF; 3 SMOKE-PASS; 2 LVH #229+#230: etf_hadamard_n_sweep HP-SMOKE-N1024/2048-8x-FLAT-NOT-HARD_PASS + hoc1_word_bigram HP-SMOKE-AUC-0.970-GATE-OPEN; effective_rank_svd HONEST-D_EFF-82-INTRINSIC-DIM-CONFIRMED; HONEST 977->980 +3; LVH 228->230 +2; KF-1 72-87% UNCHANGED; Portfolio 32+77; 362nd PROT-009 paired commit)

Push: BLOCKED from sub-agent context per feedback-subagent-permission-inheritance; orchestrator main thread executes git push origin main as 1-tool follow-up.
