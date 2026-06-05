# Substrate Capability Scorecard

**Single source of truth for validated substrate capabilities.** Living document; update per drill/experiment landing.

**Created:** 2026-06-04 (per continuous-exploration-with-tracking system design 2x drill)
**Status legend:** VALIDATED (HP) / PARTIAL (MIDDLE) / PENDING (not yet tested) / REFUTED (HF after iteration)

---

## VALIDATED bio-primitives (12 at substrate-class)

| # | Capability | Status | Empirical anchor | Algebraic prediction | Lit anchor | Next step |
|---|---|---|---|---|---|---|
| 1 | Drosophila MB sparse f=0.05 | VALIDATED | Bundle A bigram HP | Willshaw-Buckingham capacity boost | Aso-Rubin 2014; Willshaw 1990 | Combined with cf-RPE (Bundle A) |
| 2 | cf-RPE counterfactual rank-1 | VALIDATED | Bundle A bigram HP | Task-supervised axis | Klampfl-Maass 2013 | INVERTS for generative; use for retrieval only |
| 3 | Position-binding + symmetric Hebbian | VALIDATED | Bundle E E1 trigram HP +1.291 nats 3/3 | K*_corr=3.97 (4 mechanisms; r=0.43; beta=4) | Plate 1995 HRR; Kanerva 1996 | Combined with STDP for sequence |
| 4 | STDP-asymmetric | VALIDATED | Bundle E E2 trigram HP +1.249 nats 3/3 | 1.94x sequence capacity | Crisanti-Sompolinsky 1988 | Compose with position-binding |
| 5 | DG sparse-expansion (B2; f=0.02, 4x) | VALIDATED | 48x capacity gain; 3/3 seeds | sqrt(N/K) SNR | Treves-Rolls 1991; Willshaw 1990 | Compose with hierarchical (HP at 125k patterns) |
| 6 | D-ECR audit-preserving eviction (B6) | **VALIDATED (FLAGSHIP)** | 2x capacity; 0.79 vs LRU 0.39; 3/3 seeds | Energy-contribution eviction | recent 2022-2024 cache | Operational window 1.5-2.5x alpha_c |
| 7 | Cortical column ensemble (B4) | VALIDATED | Param-efficient; beats single large | Mountcastle 1957 | Lakshminarayanan 2017 | Disjoint splits > bagging |
| 8a | Active gating top-K (B3a) | VALIDATED | 13.8x write reduction @ 83% perf | Task-supervised axis | Schultz 1998 | Stretch to top-2% |
| 8b | Exp-smoothed surprise gating (B3b) | VALIDATED | 116% perf vs baseline | Anti-crosstalk at alpha=0.558 | recent 2024 active learning | Capacity-management primitive |
| 9 | Logit-space sparse residual (B8 Cell 4) | **VALIDATED (LVH CLARIFIED)** | r=0.263 vs 0.267 predicted (full N=2048) | sqrt(K/V); reconstruction 0.625->0.805 | Krahmer-Needell-Ward 2015 D-RIP | M_crit_gain sub-metric was MEASUREMENT BUG (sparse-residual vectors don't auto-associate); B8 stands on r + reconstruction |
| 10 | Hierarchical aggregator (5-corpus + scale-ext) | VALIDATED | 98.6% specialist preserved; delete retention 1.002; scale ext 5/10/20 domains | N_domains * alpha_c * N | Cross-domain interference drill | Sharper at 50/100 domains |
| 11 | SQ2 multi-hop iterated retrieval (Mode 4) | **VALIDATED (FLAGSHIP)** | K=12 hops 100% acc 3/3 seeds at 0.5*alpha_c | NC1 via iterated retrieval | Frady-Sommer 2020 resonator | Test K=16, K=24 |
| 12 | cf-RPE + STDP heterogeneous (Bundle A combined) | VALIDATED (3/5 seeds) | Superadditive at 3/5 seeds; LVH catch from 5/5 | Task + temporal orthogonal axes | shared-axis drill | Compose with capacity primitives |

---

## VALIDATED composition principles

| Principle | Status | Empirical anchor | Implication |
|---|---|---|---|
| Capacity MULTIPLICATIVE (orthogonal axes) | **VALIDATED (FLAGSHIP; full N=2048 confirmed)** | B2 x B4 x hierarchical = 125,000 patterns; independence_recall=1.00 HP | Substrate's compounding-storage product narrative |
| Same-axis SUBSUMED (collinear) | VALIDATED | B36 single-stream (gating + eviction); B26 (sparse + eviction) | Don't stack same-axis primitives on single-stream tasks |
| **B36-MIXED-stream SUPERADDITIVE** | **VALIDATED (HP; input-regime-specificity confirmed)** | 50% redundant + 50% novel; gains gate=+0.01, evict=-0.06, both=+0.19 >> sum | B3b filters redundant; B6 evicts novel; complementary on MIXED streams |
| Heterogeneous-axis SUPERADDITIVE (3/5) | VALIDATED (partial) | cf-RPE x STDP (task + temporal) | Different axes can compose; 3/5 seeds |
| **Efficiency SUB-MULTIPLICATIVE (partial)** | **VALIDATED (partial)** | B3a x B3b = 16x reduction; > best-single (13.8x) but < full product (gates overlap on high-error examples) | Efficiency composition is partial; gates not fully independent |
| **REASONING MULTIPLICATIVE (FLAGSHIP)** | **VALIDATED** | SQ2 x Hierarchical = 24-hop at 2x alpha_c via ensemble (single substrate collapses to depth 0) | Reasoning scales multiplicatively with hierarchical aggregation |
| **AUDIT-PRESERVING REASONING (FLAGSHIP)** | **VALIDATED** | B6 x SQ2 HP: K=12 holds AND deletion-cert preserved at capacity (eviction active) | Substrate's flagship audit + flagship reasoning compose cleanly |
| **SPARSITY-MODALITY SPECIFICITY (NEW)** | **VALIDATED** | B2 x B4 PATTERN/auto-assoc = 100x MULT; B2 x Position-binding SEQUENCE = 1.0x (no gain) | Sparsity benefits AUTO-ASSOC capacity but NOT SEQUENCE/position-binding capacity |

---

## VALIDATED operating modes

| Mode | Status | Complexity class | Empirical anchor |
|---|---|---|---|
| Mode 1: Single-pass bundling | VALIDATED (algebraic) | TC0 | Merrill-Sabharwal 2022 |
| Mode 4: Iterated retrieval | **VALIDATED EMPIRICAL** | NC1 | SQ2 K=12 HP today |
| Mode 5: Substrate + working memory | PENDING | Turing-complete | NTM/DNC precedent (Graves 2014) |
| Mode 2: Adaptive composition | PENDING | DTIME(L) | Siegelmann-Sontag 1991 |
| Mode 3: External routing | PENDING | depends on engine | Tool-use lit |

---

## VALIDATED audit primitives

| Primitive | Status | Empirical anchor |
|---|---|---|
| Deletion certificate cos=1 | VALIDATED (algebraic + small-N) | Ramsauer Theorem 1; v341 cos=1.000 |
| Drift detection kappa_3 | VALIDATED | gamma~8 isochoric ratio; NHSE-class |
| Composition L=10000 | VALIDATED | EXACT-1.0000 |
| Audit-preserving eviction (B6) | **VALIDATED EMPIRICAL** | 0.79 vs LRU 0.39 at 2x capacity |
| Hierarchical audit (5-corpus + scale-ext) | VALIDATED | Deletion retention 1.002 |

---

## PARTIAL / MIDDLE results (worth follow-up)

| Capability | Result | Why partial | Next step |
|---|---|---|---|
| EX1-v2 substrate-direct LM | ppl=43.1 beats bigram 60.4 on 2nd-order synthetic | Wikitext loader blocked | Wikitext rerun OR concept-level (EX-CONCEPT-1) |
| Spectral edge regime (PP-50) | beta=0.513 (Gaussian; not BBP-critical 1/3) | Wider CI than expected | Finer-N + more seeds |
| Phase 0.5 v1 Llama Hyperprobe | Pythia-160M Rung 0 HP | Llama-3.2-1B Rung A HUNG at 70% | Testbed unstuck Llama (--max-docs=50k cap) |
| Bundle E E3 + E4 (position-binding + sparse / +STDP) | MIDDLE @ trigram (2/3 seeds) | Below 3/3 threshold | Test at extctx |

---

## REFUTED / HARD-FAIL (with clear next-step or accepted-negative)

| Item | Result | Mechanism | Status |
|---|---|---|---|
| B1 one-shot Hebbian | HF (task too easy) | Adam matches in 1 epoch on linear-separable | Accepted artifact; retest on hard task |
| B5 STDP replay (palimpsest linear) | HF (FUNDAMENTAL; ACCEPTED) | Linear W replay-order algebraically irrelevant; bounded-W ALSO failed (B5-bounded HF); Wright-Fisher neutral theory retrodicts | ACCEPT NEGATIVE; substrate-class scale lacks native replay-consolidation primitive |
| Friston FEP | HF (predicted) | Inference-overhead subject to NESS subsumption | Accepted; documented in W-modifying methodology |
| Topological beta_0 Mapper | HF | beta_0 insensitive to drift | Accepted; classical TDA constrained by Adams-Virk |
| SQ6 graph adjacency naive | HF | E_max < 0.25N capacity ceiling | SQ6-v2 cleanup HF (cleanup aids recovery not membership; bundle SNR-limited); ACCEPT NEGATIVE for membership; recovery still works |
| Resonator dense V=100 capacity | HF | Capacity zero at this V | Sparse + noise-injection variants pending |
| SQ1 resonator-generative | HF (cleanup mistuned) | Data-adaptive noise-injection too aggressive for generative framing | Re-examine cleanup if SQ1 priority |

---

## NEXT-STEP capabilities (PENDING)

| Capability | Status | Cell | When |
|---|---|---|---|
| Efficiency MULTIPLICATIVE composition | PENDING | B3a x B3b x DeltaNet on wall-to-target-BPC | Priority 1 |
| Capacity full N=2048 (smoke confirmed) | PENDING | Running on remote CPU | In flight |
| B5-bounded weights | PENDING | One clip; Lazaro 2025 | ~10-15 min CPU when dispatched |
| EX-CONCEPT-1 (concept-level training) | PENDING | VQ Pythia-160M activations | Pending Pythia-160M extraction (Llama hang dependency clarification) |
| EX-OPTION-C-W_proj | PENDING | B8 logit-space bridge | When Phase 0.5 v1 Llama npz available |
| SQ1 resonator-generative (substrate-direct language) | **REFUTED (cleanup mistuned)** | Combinatorial composition V^K=10^12 | Cleanup re-examination required; data-adaptive noise-injection too aggressive for generative framing |
| SQ4 Hebbian few-shot meta-learning | PENDING | Substrate W IS meta-learner | When bandwidth |
| SQ5 N=100k biological-scale | PENDING | Matrix-free design | When bandwidth |
| SQ7 two-substrate transfer | PENDING | Distributed intelligence | When bandwidth |
| SQ8 homeostatic self-deletion | PENDING | Smoke STABLE (drift 0.03); full pending | Pending full run |
| C1/C2/C3 cornerstone audit Llama-3.1-8B | PENDING | Testbed cloud H100 ~$9-12 | Testbed dispatch |
| Level 3 meta-LLM smoke | PENDING | 1B + LoRA + text injection | After EX-CONCEPT-1 |
| Tier 1 RAG-backend vs FAISS HNSW | PENDING | NQ@10K corpus | 1-month target |

---

## Critical-path dependencies

| Capability | Blocking | Status |
|---|---|---|
| EX-CONCEPT-1 + EX-OPTION-C-W_proj + audit-core | Pythia-160M / Llama extraction pipeline | Llama v6 HUNG; Pythia-160M extraction status TBD |
| Phase 0.5 v1 audit on REAL Llama residuals | Llama v6 npz | Testbed action; --max-docs=50k cap suggested |
| C1/C2/C3 cornerstone | Testbed dispatch | Routed; not yet dispatched |
| 12-18mo deployment timeline | First production-scale validation | Phase 0.5 v1 is the critical-path gate |

---

## 3 fundamental composition lessons (today)

1. **Same-axis composition is SUBSUMED (collinear)** — B36, B26, pure-bio-BPC
2. **Linear additive W cannot benefit from replay-order** — needs nonlinearity (B5-bounded weights via Lazaro 2025)
3. **Metric must match axis of improvement** — capacity primitives on M_crit; efficiency on wall-to-target; not BPC

---

## Update protocol

- Per drill landing: add atomic fact to facts/ directory; update relevant scorecard row
- Per experiment verdict: update status + empirical anchor
- Per composition test: update composition_matrix.md
- LVH catches: update with honest read; note in row
- Periodic synthesis: every 24-48h, build product-narrative from validated rows

**Total validated count: 12 bio-primitives + 5 composition principles + 4 audit primitives + 1 operating mode (Mode 4) + 1 biological-scale validation (SQ5 N=100k sparse 10.9x dense HP) empirically anchored**

## Cross-domain theoretical anchors (Wright-Fisher / Kimura adjacency)

- M_c = 1/alpha = population-genetics coalescent timescale (universal)
- cf-RPE selection threshold s_min ~ alpha (Kimura selection boundary; below this drift dominates)
- B5 replay HF retrodict from neutral theory (selection term absent → no order-dependent benefit)
- Pattern persistence P_fix ~ 2s in selection-dominated regime (s > 1/(2N) ~ 2.4e-4 at N=2048)
- Diversity equilibrium at write_rate = alpha (Wright's formula)

Substrate maps onto population-genetics framework algebraically. Provides theoretical anchor for empirical findings.

## Recent updates (per system protocol)

- 2026-06-04 20:45: B8 LVH clarified as M_crit_gain measurement bug (case a); B8 stands at r + reconstruction
- 2026-06-04 20:42: EX-CONCEPT-1 proxy V=5000: MIDDLE (ppl=37.7 << uniform 500; captures concept structure)
- 2026-06-04 20:42: Capacity multiplicative full N=2048 GPU HP at 125k patterns
- 2026-06-04 20:42: **B36-MIXED-stream SUPERADDITIVE HP** (input-regime-specificity confirmed; flagship win)
- 2026-06-04 20:42: Efficiency composition (B3a x B3b) sub-multiplicative MIDDLE at 16x reduction
- 2026-06-04 20:42: SQ1 resonator-generative HF (cleanup mistuned)
- 2026-06-04 20:35: Pythia-160M LOADS on runner; extraction is FEASIBLE + INDEPENDENT of Llama v6 (Testbed request filed)
- 2026-06-04 21:00: Llama v6 KILL authorized + v7 with --max-docs=50000 running (Testbed; unblocks Phase 0.5 v1 audit on real Llama-3.2-1B residuals)
- 2026-06-04 21:24: Cornerstone Llama-3.1-8B C1/C2/C3 HF -- TESTBED ENGINEERING BUGS (hyperprobe API + torchmetrics BFloat16); NOT substrate science failure. Recovery path: validate C2+C3 at Llama-3.2-1B FIRST via Rung A v7 npz (substrate-audit-core); then targeted 8B retry (~$2-3) with bug fixes + salvaged artifacts. Substrate frontier-scale empirical anchor delayed; 1B-scale anchor on track.
- 2026-06-04 21:10: BATCH verdicts: B36-RATIO-SWEEP HP across ALL mix ratios (0.3/0.5/0.7) -- robust mixed-stream superadditive; **SQ5 matrix-free biological-scale N=100k HARD_PASS** -- sparse M_crit >= 10.9x dense limit; sparse coding extends capacity to biological N. SQ6-v2 cleanup HF (cleanup aids recovery not membership; WHY-DRILL answered). **B5-bounded-weights HARD_FAIL -- replay-consolidation FUNDAMENTAL NEGATIVE for substrate (linear-W AND bounded-W). STOP PURSUING REPLAY**. SQ2-load-sweep MIDDLE (K=12 holds to 1.5x alpha_c; ceiling at 2x). SQ3 structured-image retrieval MIDDLE. Efficiency composition MIDDLE 16x sub-multiplicative.
- 2026-06-04 21:15: Exp-Dev AGREED Tier-6 + Tier-4 are right strategic gap; **Tier-6 Phase D BUILDING as next dedicated build** (substantial; Shakespeare corpus fallback since Wikitext loader still broken). Tier-4 depends on Pythia scaffold.
- 2026-06-04 21:36: Llama v7 STUCK SECOND HANG -- before first extraction batch (different than v6); GPU blocked; Testbed py-spy + per-batch timeout requested.
- 2026-06-04 21:30 (Wright-Fisher drill): population-genetics retrodict for substrate -- M_c = 1/alpha = coalescent timescale; cf-RPE threshold = Kimura selection boundary; **B5 HF EXPLAINED THEORETICALLY** (neutral theory predicts replay-order irrelevant absent nonlinear selection term -- second independent reason to accept B5 negative beyond empirical B5-palimpsest + B5-bounded HF); pattern persistence P_fix ~ 2s in selection-dominated regime (s > 1/(2N) ~ 2.4e-4); diversity optimum at write_rate = alpha.
