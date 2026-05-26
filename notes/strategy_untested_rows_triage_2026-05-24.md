# Strategy — untested-rows triage (v184 baseline)

**From**: Orchestrator continuous-operation sub-agent dispatch (2026-05-24)
**Cap_map**: v184 (commit pending main-thread push; v183 -> v184 batched 2-verdict)
**Pause state**: ACTIVE (no `orchestrator_paused.flag`)
**Source for inventory**: v1 cap_map tally lines 159-167 (`UNSURE: 9 🔬, 12 ⚪; KILLER: 14 ⚪`) cross-checked against v3+ moves (lines 387-472) and v158-v184 portfolio annotations.

## Why this note exists (and is not an inline experiment design)

Per [[feedback-no-experiment-design-in-prompts]] + the dispatch-prompt style rule in `notes/orchestrator_post_compaction_brief.md` Section 2: a continuous-operation sub-agent must NOT specify experimental parameters (N, M, seeds, thresholds, queue choice, anchor names) inline. The user's directive to "ship 4-6 probes" is satisfied via **pickup-ready hand-offs to the next exp_dev cycle** (parallel to `notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md`), NOT inline `bash queue_add.sh` from this context.

This note: (a) confirms / corrects the user-cited counts; (b) names the canonical untested rows with brief context; (c) ranks them by leverage; (d) ships a 6-anchor hand-off batch to exp_dev; (e) lists the next 5-10 backlog items.

## Confirm / correct the 14 / 12 / 9 counts

The 14/12/9 number set is the **v1 (2026-05-19) snapshot** of the structured KILLER and UNSURE tables. Since v1, 6 of the 14 KILLER rows + 2 of the 21 UNSURE rows have moved into ✅ / 🟢 / 🟡 / annotation-grade portfolio rows. The **honest current counts**:

| Section | v1 count | Moved out (cycle) | Remaining untested as of v184 |
|---|---|---|---|
| KILLER ⚪ | 14 | 6 (ICL v3 ✅; Autoregressive gen v3 ✅; Provenance v3 ✅; Bet A edit-then-query ✅; Cap 1 Crooks principled-forgetting ✅; Bet G TEMPSCALE calibration ✅) | **8** |
| UNSURE ⚪ (capability questions) | 12 | 4 (ICL ✅; few-shot ✅ via ICL pool; principled forgetting ✅ via Cap 1; calibration ✅ via Bet G) | **8** |
| UNSURE 🔬 (architectural extensions) | 9 | 0 (no architectural extension from the v1 set has been shipped as a portfolio row at substrate-product level) | **9** |

Net **8 + 8 + 9 = 25 untested rows** still open from the v1 capability framing, vs. the user-cited 14 + 12 + 9 = 35. The gap is real portfolio progress, not a counting error. **The 25 figure is the correct triage target at v184.**

## Full inventory of remaining untested rows

### KILLER Tier 1 / 2 / 3 — 8 remaining (untested at substrate-product level)

| # | Capability | Tier | v184 substrate context | Shippable now? |
|---|---|---|---|---|
| K1 | **GPT-quality generation with auditable memory** (quality bar vs GPT, not just byte-K=16 generation) | T1 | Generation primitive ✅ at K=16 (v3 wave14d_generation_v2_K16 p1=43.3% vs B3 Markov 27.8%); the QUALITY VS GPT bar untouched | NO — requires GPT eval harness + corpus mapping; new build (~1-3 GPU days) |
| K2 | **True continual learning at production scale (A->B->C->D)** | T1 | Bet A ✅ at A->B edit-then-query; cycle-94 NUMFACTS_2000 multi-task signal RETRACTED; full A->B->C->D pipeline UNBUILT | YES — Lane D end-to-end pipeline already ✅ at 3-stage (cycle 104); 4-stage extension is incremental |
| K3 | **On-device personalization with continual addition** (CPU-only Hebbian pipeline) | T2 | Substrate is Hebbian-only (compatible); local_cpu_runner_local IDLE + revived per project_cpu_resource_underutilized; full pipeline UNBUILT | YES — local CPU runner is exactly the deployment target; primitives all exist |
| K4 | **Cross-modal binding** (text concepts bound with image embeddings) | T2 | R21 partial-path 🔬 (Phase 3 META 22-34 GPU hrs); no empirical anchor | PARTIAL — needs image-embedding source decision before any test |
| K5 | **Real-time learning during inference** (every prediction updates W) | T2 | Train/inference separation enforced in `hdlab/`; substrate-compatible structurally | YES — pipeline change, not new mechanism (cheap-tractable) |
| K6 | **Compositional generalization** (novel combinations of learned concepts) | T2 | R20 named in META Phase 2-4 build path 🔬; hold-out compositional eval UNBUILT | YES — cheap-tractable on existing R10 / Lane D infrastructure |
| K7 | **Multi-step reasoning** (chain inferences) | T2 | Multi-hop ✅ to 50 hops at K=100 N=65536 (cycle 96 / VAMP-on-chain Cap 8 cycle 127); but multi-hop chained INFERENCE (not chain of stored triples) UNTESTED | PARTIAL — Cap 8 VAMP-on-chain covers structural chain; INFERENCE chain (deduction over chained retrievals) needs design |
| K8 | **Hierarchical concepts** (concepts-of-concepts) | T3 | R3 closed at K>=16; no recursive concept layer tested | PARTIAL — needs new concept-discovery primitive |

### UNSURE ⚪ capability questions — 8 remaining

| # | Question | v184 substrate context | Shippable now? |
|---|---|---|---|
| U1 | **Multi-task transfer (corpus A -> corpus C, different domain)** | Only A->B distribution shift tested historically; cycle-94 NUMFACTS retraction; genuinely different corpus untested | YES — cheap-tractable on Lane D pipeline (~CPU hours) |
| U2 | **Multi-step reasoning chains** (duplicates K7) | (see K7) | (see K7) |
| U3 | **Self-supervised concept discovery (no PPMI prior)** | PPMI is the hand-crafted prior across all R3/R10 experiments; no learned-codebook anchor | PARTIAL — needs new mechanism (Wave 4.5 gradient W candidate) |
| U4 | **Hierarchical concepts** (duplicates K8) | (see K8) | (see K8) |
| U5 | **Sleep-style memory consolidation** (replay during quiescence) | Random replay ✅ (cycle 1 BWT); offline-strengthening primitive UNBUILT | YES — cheap-tractable (replay schedule variant) |
| U6 | **Online adaptation during inference** (every query updates W) | Duplicates K5 | (see K5) |
| U7 | **Multi-task transfer beyond A->B** (duplicates U1) | (see U1) | (see U1) |
| U8 | **Compositional generalization** (duplicates K6) | (see K6) | (see K6) |

Note: U1 / U2 / U4 / U6 / U7 / U8 are LITERAL DUPLICATES of KILLER rows above. Deduplicated unique-capability count from KILLER + UNSURE-⚪ = **K1, K2, K3, K4, K5, K6, K7, K8, U1, U3, U5 = 11 unique untested capability rows.**

### UNSURE 🔬 architectural extensions — 9 remaining

| # | Extension | v184 substrate context | Shippable now? |
|---|---|---|---|
| A1 | **Wave 9 MPS / DMRG** (Matrix Product States) | Literature-rec; no port; compositional advantage hypothesis | NO — new build (medium); F-4 Clifford-TN closely-related KILLED at v181 |
| A2 | **Wave 8 Clifford algebras** (grade-aware readout) | F-4 Clifford-TN closed-form KILLED at v181 (HARD_FAIL_TN_DIVERGENCE rel_err_max=0.308); approximate-Clifford-bounded-magic reframing at v181 partly absorbs this | PARTIAL — closed-form theory killed; empirical port still possible |
| A3 | **Wave 10A RG-flow** (Krotov-WTA + linear Layer 1) | Literature-rec; no anchor; would compete with Bet Y V2.D Kerdock | NO — new build (medium); Bet Y V2.D Phase 2 ✅ at intermediate-beta regime ALREADY occupies this slot |
| A4 | **Wave 4.5 gradient W** (preconditioned delta rule) | ~50 LOC est at v1; substrate is Hebbian-only by design (CLAUDE.md "No autograd anywhere") | PARTIAL — conflicts with substrate identity (CL no-autograd convention) |
| A5 | **Schlag-Irie slow projection** | ~150 LOC 1h GPU est at v1; "probably skip per CANNOT" already at v1 (pre-shift wrong goal) | NO — pre-flagged skip |
| A6 | **Learned codebook atoms** (SVD/PCA of bigram PPMI) | ~15 min CPU est; "Estimated +0.02-0.08 at K=4" | YES — cheapest item on the list; local_cpu runner target |
| A7 | **Bricken SDM substrate** (Top-K + L2-norm) | ~1 GPU hour est; claimed pre-shift parity + native CL | PARTIAL — port required; pre-shift target is wrong goal per v2 framing |
| A8 | **Sparse block codes (Hersche 2024)** | log(N/B)*B capacity claim; on list, not built | YES — Hersche 2024 paper has reference impl; cheap-tractable port |
| A9 | **Hierarchical context pool** (recent K bigrams + episodic anchors) | Speculative +0.05-0.15; medium build at v1 | PARTIAL — design space large; needs scoping pass first |

## Triage — leverage ranking

Per user prior framing "shipped probes should cover REAL gaps not 'smoke extensions of validated primitives' (diminishing returns)":

### Priority A — KILLER-tier + cheap-tractable + real gap (SHIPPABLE THIS CYCLE)

1. **K6 / U8 Compositional generalization** — KILLER Tier 2; existing R10 + Lane D infrastructure; cheap CPU; FIRST-time real gap closure.
2. **K2 True continual learning 4-stage (A->B->C->D)** — KILLER Tier 1; Lane D 3-stage ✅ at v103; 4-stage is incremental extension at GPU.
3. **K3 On-device personalization end-to-end** — KILLER Tier 2; local_cpu_runner revival + existing primitives; deployment-target real gap.
4. **K5 / U6 Real-time learning during inference** — KILLER Tier 2; pipeline-config change not new mechanism; cheap GPU.
5. **U1 / U7 Multi-task transfer A -> genuinely-different-corpus C** — UNSURE ⚪; cycle-94 retraction left this gap; cheap CPU on Lane D pipeline.
6. **A6 Learned codebook atoms (SVD/PCA of bigram PPMI)** — UNSURE 🔬; ~15 min CPU; cheapest architectural extension; A/B against random bipolar.

### Priority B — KILLER but PARTIAL / NEEDS-BUILD (NEXT 5-10 CYCLES)

7. **K1 GPT-quality generation eval harness** — needs corpus + eval design (~1-3 GPU days). Highest-leverage T1, highest cost.
8. **U5 Sleep-style memory consolidation** — replay schedule variant; cheap CPU; substrate-novel mechanism candidate.
9. **K7 Multi-step inference (not just multi-hop retrieval)** — needs deduction harness above Cap 8 VAMP-on-chain.
10. **A8 Sparse block codes (Hersche 2024)** — cheap port; log(N/B)*B capacity claim worth empirical anchor.
11. **U3 Self-supervised concept discovery** — would dethrone PPMI as load-bearing prior; high-novelty.
12. **A9 Hierarchical context pool** — needs scoping pass; speculative gain.

### Priority C — CLOSED-AT-THEORY / WRONG-GOAL / IDENTITY-CONFLICT (DO NOT SHIP)

- **A2 Wave 8 Clifford** — closed-form theory KILLED at v181; only empirical-margin port remains and that overlaps Bet Y V2.D
- **A3 Wave 10A RG-flow** — Bet Y V2.D already occupies this regime ✅
- **A4 Wave 4.5 gradient W** — conflicts with substrate Hebbian-only identity (CLAUDE.md convention)
- **A5 Schlag-Irie** — pre-flagged skip; pre-shift is wrong goal per v2 framing
- **K8 / U4 Hierarchical concepts (recursive)** — R3 closed at K>=16; rehab structurally weak

## Shipped this cycle — 6 pickup-ready anchors for next exp_dev cycle

Per the dispatch-prompt style rule + [[feedback-no-experiment-design-in-prompts]]: this list specifies the WHAT, the WHY, and pointers, NOT the experimental design parameters. Exp_dev picks N / M / seeds / thresholds / queue / anchor names.

| # | Anchor | KILLER/UNSURE row | Default queue (exp_dev may revise) | Base-script pointer |
|---|---|---|---|---|
| 1 | **Compositional generalization hold-out probe** — measure substrate ability to read out NOVEL (atom1, atom2) combinations not seen at train | K6 / U8 KILLER T2 | local_cpu_queue (CPU-bound; existing R10 infra) | `experiments/exp_r10_best_config_*.py` family |
| 2 | **4-stage continual learning (A->B->C->D)** — extend Lane D 3-stage v103 to 4 stages with retention measurement per stage | K2 KILLER T1 | overnight_queue (GPU; Lane D infra) | `experiments/exp_wave14d_lane_d_end_to_end_*.py` family |
| 3 | **On-device end-to-end personalization smoke** — local_cpu_runner runs full Hebbian add-on-user-data + retrieval-from-bundle pipeline at consumer-laptop scale | K3 KILLER T2 | local_cpu_queue (deployment-target match) | `experiments/exp_cpu_platform_timing*.py` + `experiments/exp_wave14d_betB_kovacs_v1.py` |
| 4 | **Real-time-learning inference loop** — single-query-updates-W ablation against frozen-W baseline | K5 / U6 KILLER T2 | local_cpu_queue (CPU-bound; small N) | `experiments/exp_wave14_eligibility_charlm.py` (existing eligibility-trace candidate) |
| 5 | **Multi-task transfer A -> genuinely-different-corpus C** — extend cycle-94 retracted NUMFACTS pattern to a clean different-domain corpus | U1 / U7 UNSURE ⚪ | local_cpu_queue (CPU; small) | `experiments/exp_r7_concept_replay.py` family |
| 6 | **Learned codebook atoms A/B** — SVD/PCA of bigram-PPMI codebook vs random-bipolar baseline at K=4-16 | A6 UNSURE 🔬 | local_cpu_queue (~15 min CPU per v1 estimate) | new (no base script; lightweight) |

**Falsifier band specification** is deferred to exp_dev per [[feedback-no-experiment-design-in-prompts]]. Each anchor MUST carry both HARD-PASS and HARD-FAIL falsifiers per [[feedback-no-smoke]] + [[feedback-envelope-expansion-fail-bands]] in the prereg the exp_dev sub-agent writes.

## Backlog — next 5-10 ships for subsequent cycles

In recommended-order:

1. **K1 GPT-quality generation eval harness** (largest build; T1 cap)
2. **U5 Sleep-style memory consolidation** — replay-during-quiescence variant
3. **K7 Multi-step inference (deduction over chained retrievals)** — needs harness design
4. **A8 Sparse block codes (Hersche 2024)** port
5. **U3 Self-supervised concept discovery** — Wave 4.5 boundary case
6. **A9 Hierarchical context pool** — scoping pass first then build
7. **A1 Wave 9 MPS / DMRG** port (lower priority given F-4 Clifford-TN killed)
8. **A7 Bricken SDM** port (low; pre-shift target is wrong goal)
9. **K4 Cross-modal binding** — needs image-embedding source decision before any test
10. **K8 Hierarchical concepts** — R3 closed; structurally weak rehab

## Honest reading — shippable vs needs-code-build

**Shippable now (next 1-2 exp_dev cycles, anchors 1-6 above)**: K6/U8, K2, K3, K5/U6, U1/U7, A6 — six anchors reusing existing infrastructure with cheap-tractable scopes. These are the 6 shipped via this triage.

**Needs new code-build first**: K1 (GPT-quality eval harness), K7 (multi-step inference deduction harness), U3 (self-supervised concept primitive), A1 (Wave 9 MPS port), A7 (Bricken SDM port), A8 (Hersche sparse block codes port), A9 (hierarchical context pool scoping).

**Closed at theory / wrong-goal / identity-conflict (DO NOT SHIP)**: A2 (Clifford closed-form), A3 (Wave 10A absorbed by Bet Y), A4 (Hebbian-only identity), A5 (Schlag-Irie pre-shift), K8/U4 (R3 closed at K>=16).

**Honest gap reading**: ~6/25 untested rows are immediately shippable on existing infrastructure. ~7/25 need new code-build first. ~5-6/25 are CLOSED at theory / wrong-goal / identity-conflict and should NOT be probed. The user's "untested rows" framing is correct as a portfolio-gap audit, but the operational subset is ~6 immediately-actionable + ~7 medium-build + ~6-12 deferred.

## Routing

- This triage filed: `notes/strategy_untested_rows_triage_2026-05-24.md` (this file)
- 6-anchor exp_dev pickup-ready hand-off: this note serves as the hand-off (Strategy -> Exp Dev) — exp_dev reads section "Shipped this cycle" and designs preregs per [[feedback-no-experiment-design-in-prompts]]
- Existing 5-anchor + MS_1ST_ORDER hand-off (`notes/exp_dev_handoff_5anchors_post_v183_2026-05-24.md`) is ORTHOGONAL — those address v183 verdict follow-ups; this 6-anchor batch addresses v1 KILLER/UNSURE portfolio gaps

## PROT discipline

- Per [[feedback-no-experiment-design-in-prompts]]: no N / M / seed / threshold / formula specification in this note; only WHAT + WHY + pointer-to-base-script
- Per [[feedback-structural-agent-usage-mandate]]: this sub-agent dispatch routes to exp_dev next cycle (does NOT design experiments in main thread)
- Per [[feedback-for-you-tab-primary-channel]]: status_log entry written for this triage delivery (HIGH importance — portfolio-gap audit closing 25-row untested-inventory framing)
- Per [[feedback-no-smoke]]: honest correction of user-cited 14/12/9 to actual 8/8/9 = 25 remaining (with 11 unique after dedup)
- Per [[feedback-rehabilitation-after-rejection]]: A2 / A3 / A4 / A5 / K8 explicitly marked DO-NOT-SHIP with rehab paths exhausted or identity-conflict
- Per [[feedback-dont-overextend-theorems]]: A2 closed-form theory KILLED at v181 does NOT close empirical-margin port (kept on backlog at lowered priority)
- Per PROT-009: no cap_map commit this triage (filing-grade only; portfolio rows unchanged)
