# Envelope-push: deg8+ hub bundle-capacity residual — is it a wall or a cost?

**Filed by:** research (Sonnet main synthesis + 2 parallel Sonnet lit-scans), 2026-07-05.
**Scope:** constructive build spec for the one open memory limiter. Not a vs-LLM comparison. Brain-first per USER steer.

---

## DISK-VERIFY (Fix#28) — the residual is real, and a same-day sibling cell already tested the fix on synthetic data

Re-read `data/exp_deep_reasoning_hub_robustness_v1/metrics.json` (seed 7) directly, per-degree, not the aggregate:
`idx_bind_top1`: deg2=1.00, deg3=0.996, deg4=1.00, deg5=0.988, deg6=0.971, deg7=0.932, **"8plus"=0.466** (bucket mean degree ~16, real chain-reasoning hubs, n_edges=1287/80 sources). This exactly reproduces the task's numbers — confirmed, not stale.

**Cross-thread finding (the load-bearing discovery of this drill):** a sibling cell landed the SAME day — `exp_mem_joint_capacity_hub_degree_redundancy_v1` (HARD_PASS, verdict `HARD_PASS_COMPUTE_COST_ENVELOPE_ESTABLISHED`) — already tested a redundancy lever (R independent banks storing the same bundle, mean-unbind-before-cleanup) on CLEAN SYNTHETIC uniform-degree hubs at op_R=4, op_load=0.2, across deg{2,3,5,10,20}: min recall **0.8196**, spread 0.057 (gate_diagnostics `HP1_protected_hub_recall_by_deg_at_OP`: deg10=0.822, deg20=0.820). This is essentially the exact rescue the task is asking for — **already validated, on synthetic data, up to deg20**. It has NOT yet been re-run against the REAL heterogeneous hub_robustness dataset that produced the 0.42-0.47 residual. That gap — synthetic-validated vs real-untested — is the single decisive next test, not a fresh mechanism search.

---

## HEADLINE

The deg8+ residual is a **compute cost, not a fundamental wall** — with one real caveat. A redundancy lever (R independent redundant banks, averaged before cleanup) already HARD_PASSED on synthetic uniform-degree hubs to deg20 (min recall 0.82). This is brain-grounded via **population coding / population-vector averaging** (Georgopoulos 1986; Seung & Sompolinsky 1993: Fisher information grows linearly in independent-channel count, so SNR ~ sqrt(R)) — a directly-tested, well-quantified mechanism, not a loose analogy. It is a *different* mechanism than hippocampal multiple-trace-theory (lit-scan found MTT/competitive-trace-theory is about graded lesion-robustness via non-identical traces that actually *compete*, not constructive SNR-averaging — that brain-grounding claim was too generous and is downgraded here). RNS/CRT modular coding (the generation-thread's shared lever) is confirmed a genuinely open, unpublished extrapolation for the hub/fan-in axis specifically (published RNS/CRT-in-HDC work — Kymn/Kleyko/Frady/Sommer 2024/2025 — targets vocabulary/range capacity, not fan-in/reuse capacity); grid-cell modules ARE documented as simultaneously range-extending AND interference-reducing (Sreenivasan & Fiete 2011, *Nat Neurosci*, explicitly "an analog error-correcting code"), so the analogy is well-grounded but untested for this specific axis. Separately, the lit-scan confirms plain repetition-redundancy is information-theoretically **inefficient** vs. a structured code (Shannon 1948; error-exponent theory) — so R-bank redundancy is a real, working fix but not the cheapest one; RNS/CRT or erasure coding (PP-354, already HARD_PASS in-system) are better second-stage candidates once the redundancy fix is confirmed on real data.

---

## Cheap decisive test

Apply the ALREADY-VALIDATED redundancy lever (R independent banks, mean-before-cleanup — reuse the mechanism from `exp_mem_joint_capacity_hub_degree_redundancy_v1`) to the REAL heterogeneous `exp_deep_reasoning_hub_robustness_v1` corpus (same real BGE-derived chain-reasoning codebook, same degree bins, "8plus" bucket ideally split finer, e.g. 8-12 / 13-19 / 20+, to see if the fix degrades at the true tail).

**Arms:** (a) idx_bind-only, R=1 (current baseline, 0.466 measured); (b) idx_bind + R=4; (c) idx_bind + R=8. CPU-only, reuses existing real dataset + codebook — cheap.

## Falsifiable predictions

**HARD-PASS** (rescues the residual, confirms compute-cost-not-wall on REAL data):
- 8plus-bucket recall at R=4 ≥ 0.65 (matches the synthetic HP1 floor), AND R=8 ≥ 0.75.
- No collapse in the finer degree sub-bins (spread ≤0.20 across 8-12/13-19/20+, mirroring the synthetic HP1 flat-degree result).

**HARD-FAIL** (real heterogeneous structure breaks the mechanism — a genuine, different wall):
- 8plus-bucket recall at R=8 stays ≤0.50 (i.e., doubling R twice buys almost nothing) — this would mean real cross-hub correlated interference (shared factors between DIFFERENT hubs in actual reasoning chains) violates the i.i.d.-independent-noise assumption the sqrt(R) population-averaging gain requires (lit-scan flag: Abbott & Dayan-era correlated-noise results show correlated noise caps or sharply reduces the diversity-combining gain). This is the one thing not yet checked and exactly what distinguishes "clean synthetic wins" from "real substrate wins."

**MIDDLE BAND:** partial rescue (0.50-0.65 at R=8) — routes to RNS/CRT hub-sharding prototype or PP-354 erasure coding as the next lever, since both are structured (non-repetition) codes the lit-scan confirms should out-perform naive redundancy per unit dimension cost.

---

## Cross-thread synthesis

Connects directly to: `notes/research_5x_drill_memory_spec_and_brain_mechanism_2026-07-05.md` (this drill's Section D/F "compute cost not wall" framing, now empirically reinforced by the same-day joint-capacity HARD_PASS); `exp_deep_reasoning_hub_robustness_v1` (the real-data baseline this drill re-verified per-degree); `exp_mem_joint_capacity_hub_degree_redundancy_v1` (the synthetic-validated fix awaiting real-data confirmation); `notes/research_generation_blocklocal_next_lever_RNS_CRT_experiment_proposal_2026-07-05.md` (the shared RNS/CRT lever proposed for generation-vocab capacity — confirmed by this drill's lit-scan as NOT yet tested for the hub/fan-in axis; a genuinely open cross-domain hypothesis rather than a redundant re-test); PP-354 erasure coding (already HARD_PASS in-system, the other structured-code candidate). Downgrades one claim from the memory 5x-drill: hippocampal multiple-trace-theory is NOT solid brain-grounding for "averaging redundant copies boosts SNR" (that mechanism is better grounded in population coding / diversity combining, a different literature); MTT is about graded robustness-to-damage via non-identical, sometimes-competing traces.

## Substrate-product implications

If the real-data decisive test HARD-PASSes: "every stored fact, including your most-referenced entities, stays reliably retrievable — the fix costs redundant storage bandwidth, not a redesign" is a defensible product claim, and it composes with the already-banked audit/deletion narrative (deleting R redundant copies of a protected index is a bounded, enumerable operation, same shape as the existing deletion-certificate story). If it HARD-FAILs on real data specifically, that is itself a valuable, honest finding: it would mean real associative structure (not synthetic i.i.d. hubs) has correlated cross-hub interference that no amount of naive redundancy fixes — pointing product positioning toward "graceful degradation with disclosed limits" rather than "solved," and toward RNS/CRT-style structural sharding as the required next engineering step rather than an optional optimization.

---

## Achievability (honest, no smoke)

**GOOD:** the mechanism (redundant-bank averaging) is real, brain-grounded (population coding, high-confidence literature, not analogy), already HARD_PASSED once (synthetic, deg2-20, min 0.82), and the Gardner/Cover combinatorial wall sits ~6.7x above current empirical operating points per the prior drill — there is real headroom; this is a cost curve, not a wall, AS FAR AS TESTED.
**MEDIOCRE / open:** never tested on the actual heterogeneous real-data regime that produced the residual; repetition-style redundancy is a known-inefficient way to buy the fix (confirmed by classic coding theory) even if it works, so a structured code (RNS/CRT, erasure coding) is likely a strictly better long-run answer.
**Downgraded:** multiple-trace-theory as brain-grounding for constructive-averaging — lit-scan shows this was too generous; population coding is the correct, better-grounded citation.

**P_deflated = 0.50 (capped, novel-synthesis rule)** for "redundancy lever generalizes to the real heterogeneous deg8+ regime at ≥0.65." Underlying mechanism confidence (population-averaging SNR scaling itself) is HIGH (~0.80-0.85, directly tested, not analogy); the deflation is entirely about generalization from synthetic-uniform-hub to real-correlated-hub structure, which is genuinely untested.

---

## Citations (verified count)

18 distinct citations surfaced across 2 independent Sonnet lit-scans (live-link-verified by the sub-agents via WebSearch/WebFetch: arXiv, PubMed, MIT Press/Neural Computation, Nature Neuroscience, PLOS Comp Bio, NeurIPS, Stanford course notes, Wikipedia for uncontested textbook results). Not independently re-verified a second time by this synthesis — single-source-verified. Highest-value: Georgopoulos et al. 1986 (*Science*, population vector coding); Seung & Sompolinsky 1993-era Fisher-information population-coding scaling; Sreenivasan & Fiete 2011 (*Nat Neurosci*, grid cells as analog error-correcting code); Kymn, Kleyko, Frady, Bybee, Kanerva, Sommer, Olshausen 2025 (*Neural Computation* 37(1):1-37, arXiv:2311.04872 — RNS/CRT in HDC, confirmed range/vocabulary-scoped not fan-in-scoped); Nadel/Samsonovich/Ryan/Moscovitch 2000 + Yassa/Sekeres et al. 2013 Competitive Trace Theory (*Front Behav Neurosci*, PMC3740479 — the MTT downgrade); Shannon 1948 noisy-channel coding theorem (repetition-code inefficiency).

## Next-drill candidate

Field: `sparse-coding-compressed-sensing` (Tier-1b) or `coding-theory` (Tier-2, adjacent) — once the real-data decisive test lands, a follow-up drill comparing R-bank redundancy's dimension-cost-per-recall-point against a structured code (RNS/CRT hub-sharding prototype, or PP-354 erasure coding applied to hub degree specifically) would quantify the "how much cheaper is a smarter code" question this drill's lit-scan flagged but could not numerically answer.
