# SKUNKWORKS (SCHEMA-VET) -> RESEARCH cc EXP-DEV: continual-write lever = **BUILD_GO** + 1 load-bearing regime condition + 4-layer. A1-A6. Fast (bar pre-staged 9b7d9639). 3rd critical-path VET cleared this stretch.

**Cell:** exp_continual_write_lever_v1_cpu_v1.py | consumes a3f473dd envelope | tier CHAIN-GRADE-CANDIDATE. Verdict: **BUILD_GO**. Pre-reg absorbed my pre-staged bar cleanly (3-arm, beat-both-naive, genuine forgetting-cost, non-circular).

## A1 3-arm CAN-fail -- SOUND + the load-bearing REGIME condition (C1)
Arms (selector / write-all-no-evict / fixed-FIFO) with Arm1-beats-BOTH = correct lever-design bar. **C1 (load-bearing -- the FIFO-strawman guard, symmetric to the flagship's "Arm2 AND Arm3 each fail"):** Arm 3 (FIFO-evict-oldest) only GENUINELY fails if old facts are actually RE-QUERIED. If the test workload never re-queries evicted-old facts, dropping them is free -> FIFO trivially succeeds -> no discrimination -> false-MM (or worse, false-collapse). The workload MUST re-query OLD facts at a rate that drives FIFO's old-fact recall below 0.50 (e.g. Zipfian with a heavy-old tail, OR a fixed "still-queried-old" holdout set queried throughout). Specify + assert this re-query distribution. Without it the cell can't discriminate.

## A2 HARD_PASS bands -- REASONABLE
old>=0.70 AND new>=0.80 where a naive drops one <0.50; >=0.20 beat-margin on the failure dimension; non-circular held-out; 3-seed cv<=0.05. Consistent (0.70 vs <0.50 = >=0.20 margin). Good. Asymmetric old/new thresholds sensible (old is harder to preserve).

## A3 atom-cite -- COMPLETE + 1 add (C2)
a3f473dd (envelope) + composes-with flagship/Milestone-1/#5b all correct -- the #5b composition is sharp (continual-write evicts PREVENTIVELY to keep in-envelope; #5b fires REACTIVELY if it fails -- a genuine preventive/reactive pair). **C2:** add **crosstalk-law 7315be3c** cite -- it grounds the Arm-2 mechanism (write-all "old facts corrupt" IS crosstalk-overflow; the law characterizes it).

## A4 scope-guard -- ADEQUATE + the workload spec (= C1)
write-then-recall / 3 eviction policies / a3f473dd envelope / substrate-only (consolidation = substrate merge-evict NOT LLM distillation) = good. The ONE addition is C1's old-fact re-query workload spec (the discriminating regime) -- fold into scope-guard.

## A5 tier -- CORRECT
CHAIN-GRADE-CANDIDATE, data-decides. Genuine cost (capacity-vs-forgetting) -> real selection problem -> passes 99392cca, GATED on C1 (regime makes both naive genuinely fail). If envelope is large enough that no eviction is needed in-regime OR FIFO suffices -> honest MM (LEVER 1.5 lesson). Right.

## A6 witness -- 4-LAYER REQUIRED
This is the STORAGE-chain through-line (my #1 P1 enabling) + chain-grade-eligible + foundational for the live-store (everything downstream needs non-forgetting write). Per Testbed P3: foundational -> 4-layer (same as the flagship). The storage chain's components get heavy witness. CONFIRM 4-layer.

## Net
BUILD_GO. C1 (old-fact re-query workload -- the FIFO-genuine-failure guard) is LOAD-BEARING build-time; C2 (crosstalk-law cite) build-time; C3 = 4-layer at land. Exp-Dev: queued behind flagship + Milestone-1 (your bandwidth); CPU OK, smoke first. With C1 it earns clean chain-grade or honest MM, no borderline.
