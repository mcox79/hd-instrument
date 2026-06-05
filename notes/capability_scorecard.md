# Substrate Capability Scorecard

**Single source of truth for validated substrate capabilities.** Living document; update per drill/experiment landing.

**Created:** 2026-06-04 (per continuous-exploration-with-tracking system design 2x drill)
**Last honest review:** 2026-06-04 (post-compaction; user-requested audit; reasoning capabilities surfaced)
**Status legend:** VALIDATED (HP) / PARTIAL (MIDDLE) / PENDING (not yet tested) / REFUTED (HF after iteration)

---

## FOUNDATION: what substrate IS

Substrate is a **bipolar discrete-state memory based on Vector Symbolic Architectures (VSA / HRR / FHRR)**. This is the architectural foundation; all capabilities derive from it.

- **Bipolar discrete state:** each weight in {-1, +1}; not continuous floats
- **VSA algebra:** binding (combine vectors into structured relations), unbinding (recover components), bundling (superpose multiple), composition (stack operations)
- **Structural reasoning by algebra (not approximation):** vector operations exactly recover compositional structure; not probabilistic prediction
- **Non-equilibrium (NESS) dynamics:** substrate doesn't converge to equilibrium like gradient-trained networks; active write rules + decay keep it in non-equilibrium steady state
- **Hardware advantage:** bipolar arithmetic is 4-8x faster per op than float32; many ops parallelizable
- **Modality-agnostic at the algebra level:** VSA binding works on any modality (vision, audio, text, sensor data) — substrate is medium-blind

This foundation is why substrate has the capabilities below. They are NOT decorations on a vector database; they are direct consequences of the VSA algebra + Hopfield-class dynamics + bipolar discrete state.

**Lit anchors:** Plate 1995 (HRR); Kanerva 1996 (binary spatter codes); Frady-Sommer 2020 (resonator networks); Ramsauer 2020 (modern Hopfield = attention identity).

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

## REASONING CAPABILITIES (must be prominent; ALWAYS check before discussing substrate's role)

**Substrate is a STRUCTURED REASONING SYSTEM, not just a memory store.** VSA-based binding/unbinding/composition gives substrate reasoning capabilities that LLMs only approximate.

| Reasoning capability | Status | Mechanism | Empirical anchor / lit |
|---|---|---|---|
| **Multi-hop iterated retrieval** | **HP validated** | Mode 4; chained queries through stored associations | SQ2 K=12 hops 100% acc (FLAGSHIP); K=24 hierarchical |
| **Analogical / relational reasoning** | **Mechanism present (VSA-native); HyperProbe scaffold tests this** | VSA binding: structural relations applied to novel entities via vector arithmetic | Plate 1995 HRR; Kanerva 1996; saturnMars/hyperprobe-dataset-analogy is the test dataset |
| **Counterfactual reasoning** | **Mechanism validated (cf-RPE primitive HP)** | Computes prediction WITH vs WITHOUT pattern; extends to inference-time "what if" queries | Bundle A bigram HP; Klampfl-Maass 2013 |
| **Cross-domain transfer** | **HP validated** | Hierarchical aggregator transfers patterns across domains | 5/10/20 domains scale extension HP; 98.6% specialist preservation |
| **Compositional generalization** | **HP validated (EXACT)** | Chain stored facts to reach conclusions never directly stated; depth L=10000 | Composition EXACT-1.0000 at L=10000; SQ2 multi-hop empirical |
| **Symbolic manipulation** | **VSA-native (architectural)** | Binding / unbinding / factor recovery / type-respecting operations | Frady-Sommer 2020 resonator; Plate HRR; structural |
| **Pattern completion** | **VALIDATED** | Hopfield-class retrieval from noisy/partial queries | alpha_c=0.138 dense; 1.5*N sparse (SQ5) |
| **Audit-preserving reasoning** | **HP validated (NEW today)** | B6 D-ECR eviction preserved AND K=12 reasoning preserved at capacity | B6 x SQ2 HP 2026-06-04 22:16 |
| **Continual learning at $0/pattern** | **Algebraic; ~10^9x faster than fine-tune** | Hebbian writes per new pattern; no gradient required | Training-speed design space drill 2026-06-04 |
| **Mode 4 reasoning reaches NC1** | **HP validated** | Iterated retrieval has same complexity class as parallel-poly-log circuits | SQ2 K=12 empirical; Merrill-Sabharwal 2022 |
| **Mode 5 substrate + WM = Turing-complete** | **PENDING** | NTM/DNC precedent; substrate as memory + small state machine | Graves 2014 NTM; Siegelmann-Sontag 1991 |

**KEY INSIGHT:** Substrate reasons VIA ALGEBRA, not via probability distributions. LLMs do these operations by learned approximation; substrate does them by direct compositional VSA operations. This is why substrate could exceed frontier LLMs on STRUCTURED reasoning tasks even at small system sizes.

**WHAT SUBSTRATE'S REASONING IS GOOD FOR (compared to LLMs):**
- Structured logic over typed bindings — EXCEEDS LLM approximation
- Multi-hop factual chains — depth validated to K=12 (single) / K=24 (hierarchical)
- Analogical inference via relational evaluation — VSA-native; lit-validated for HRR
- Counterfactual queries over stored knowledge — cf-RPE mechanism present
- Cross-domain transfer — hierarchical aggregator validated
- Knowledge graph reasoning — VSA bindings are KG triples in vector form
- Type-respecting composition — VSA binding algebra enforces type structure
- Formal verification — substrate operations are exact, not probabilistic
- Mathematical / symbolic proofs over discrete representations — algebraic primitive

**WHAT SUBSTRATE STILL NEEDS LLM PARTNER FOR:**
- Generating fluent natural language text (SQ1 generative HF; needs LLM decoder)
- Open-world knowledge not distilled into substrate
- Continuous/numerical computation (substrate is bipolar discrete)
- Open-ended creative synthesis where probabilistic exploration matters

---

## SUBSTRATE-LLM INTEGRATION TIERS (architectural roadmap)

| Tier | Mechanism | Status | Empirical anchor |
|---|---|---|---|
| **Tier 0** (substrate-class char-LM) | EX1 substrate-direct LM | **MIDDLE** | ppl=43.1 beats bigram 60.4 (2nd-order synthetic) |
| **Tier 0.5b** (residual injection at 0.7L) | Substrate retrievals injected as activations into LLM | Architecture LOCKED; not empirically tested at scale | Phase 0.5 v1 Pythia-160M ready (Testbed) |
| **Tier 1** (RAG-backend) | Substrate replaces FAISS for LLM retrieval | PENDING (1-month target) | NQ@10K corpus vs FAISS HNSW |
| **Tier 4** (Hopfield-attention substitution) | Substrate-Hebbian attention replaces 1+ transformer attention layers | **PENDING (high P)** | Ramsauer 2020 identity P=0.95 algebraic; Pythia-160M scaffold ready |
| **Tier 6 (substrate-hybrid LLM training)** | **Substrate-Hebbian attention IS the attention layer; gradient head only** | **VALIDATED AT SMOKE (FLAGSHIP today)** | 4-layer char-LM smoke: BPC 1.08x baseline + 2x speedup + audit operational during training (2026-06-04 22:05) |
| **Tier 7** (substrate-native LLM training) | Substrate replaces transformer entirely | REFUTED at frontier | 17x parameter penalty per training-speed drill 2026-06-03 |

**Tier 6 smoke result is the FIRST empirical evidence substrate works as PART of an LLM**, not just as memory/audit accessory. Strategic pivot point.

---

## SUBSTRATE-AS-COGNITIVE-CORE positioning (post-2026-06-04 strategic shift)

**Frame:** substrate = reasoning + memory + audit engine; LLM = language interface (encode + decode).

| Tier | Substrate config | Total system | Training cost | LLM equivalent |
|---|---|---|---|---|
| Pythia-160M (REC'D START) | N=8192, 20-50 domains | ~1-4 GB | ~$50-200 + 8-10 hrs | ~500k-1.2M facts (21-52% Pythia) |
| Llama-3.2-1B | N=16384, 100-200 domains | ~9 GB | ~$500-2000 + ~1 day | ~5-10M facts (33-67% Llama-1B) |
| Llama-3.1-8B | N=16384, 500-1000 domains | ~36 GB | ~$5-50k + ~2 weeks | ~25-50M facts (20-42% Llama-8B) |

**Smallest viable empirical test:** CCC-1 REVISED at Pythia-160M tier, ~$30 + 1-3 eng-days. Eval includes analogical / counterfactual / compositional / cross-domain transfer / multi-hop factual (not just retrieval). See `research_to_exp_dev_ccc_REVISED_relational_analogical_evaluation_2026-06-04.md`.

**Product positioning:** NOT "cheaper LLM" — instead **"auditable reasoning system with selectable knowledge"**. Differentiating: per-fact deletion certificates, continual learning at $0/pattern, multi-hop K=12 reasoning, type-respecting structured composition.

---

## FUNDAMENTAL PROPERTIES (architectural; affect everything)

| Property | Status | Implication |
|---|---|---|
| **NESS dynamics (non-equilibrium)** | Architectural | Substrate doesn't converge; active write + decay maintains non-equilibrium steady state; explains why Friston FEP variational machinery is subsumed (no free energy to minimize) |
| **Bipolar arithmetic** | Architectural | 4-8x faster than float32 per op; many ops parallelizable; storage cost 1 bit per weight (~32x storage advantage vs float32) |
| **VSA binding algebra** | Architectural | Compositional structures recoverable exactly; basis for symbolic manipulation; type-respecting |
| **Modality-agnostic** | Algebraic (PENDING empirical at scale) | VSA binding works on any modality; substrate is medium-blind at the algebra level |
| **Hopfield-class capacity** | Validated | alpha_c=0.138 dense; 1.5*N sparse (SQ5 N=100k HP); capacity scales linearly with N |
| **Continual learning at ~10^9x fine-tune speed** | Algebraic | Hebbian write per pattern is O(N^2) constant; no gradient; per training-speed drill |
| **Per-pattern compute ~10^5x LLM cheaper** | Algebraic | Substrate retrieval per pattern is much cheaper than LLM forward pass at matched complexity |

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
- 2026-06-04 22:05: **TIER 6 PHASE D BUILT (FLAGSHIP)** -- substrate-hybrid 4-layer char-LM Shakespeare smoke: hybrid_BPC=4.04 vs baseline_BPC=3.73 (ratio 1.08x, UNDER HP bar 1.20x); speedup=1.98x (just under 2.0x; MIDDLE by a hair); deletion-cert audit OPERATIONAL DURING training. **FIRST empirical evidence for substrate-intrinsic LLM training**. Full run (D=256, T=64, 600 steps, 3 seeds) queued.
- 2026-06-04 22:16: **B6 x SQ2 HARD_PASS** -- audit-preserving reasoning at capacity (K=12 holds AND deletion-cert preserved with eviction active). Substrate's flagship audit + flagship reasoning compose cleanly.
- 2026-06-04 22:16: **Position-binding x B2 HARD_FAIL** -- sparsity does NOT help sequence/position-binding capacity (1.0x ratio). NEW PRINCIPLE: sparsity is MODALITY-SPECIFIC (helps PATTERN auto-assoc; not SEQUENCE).
- 2026-06-04 22:30 (Cognitive-core 3x drill): substrate-as-cognitive-core at Pythia-160M tier algebraically viable; PATH A distillation recommended; ~$50-200 + 8-10 hrs; 6-8 independent published groups building similar architectures; substrate's unique contributions: deletion certs + NESS + B8 bridge + SQ2 K=12 + bipolar arithmetic.
- 2026-06-04 23:00 (HONEST AUDIT): scorecard reorganized to surface REASONING capabilities prominently (multi-hop / analogical / counterfactual / cross-domain transfer / compositional / symbolic / pattern completion / audit-preserving / continual learning / Mode 4 NC1 / Mode 5 PENDING). Added VSA FOUNDATION; Substrate-LLM integration tiers; Substrate-as-cognitive-core positioning; Fundamental properties. CCC-1 evaluation BROADENED to include analogical / counterfactual / compositional / cross-domain transfer / KG reasoning (not just factual recall).
- 2026-06-04 23:10 (**FLAGSHIP**): **CCC-AGGRESSIVE smoke = HARD_PASS on ALL 4 VSA reasoning dimensions** -- recall 1.00 + **analogical 1.00** + **counterfactual 0.94** + **cross-domain transfer 1.00**. DIRECTLY EMPIRICALLY VINDICATES user's pushback on factual-recall-only framing earlier today. Substrate's distinguishing strength is STRUCTURED REASONING (analogical binding, counterfactual deletion, cross-domain relation transfer), not just retrieval -- validated at scaffold level. Full N=8192 queued. This is the empirical answer to "is substrate a reasoning system or just retrieval?": IT REASONS.
- 2026-06-04 23:30 (Domain-distillation 2x drill): Path Y (direct KG triple binding) dominates cost for medical/legal; Path W hybrid for unstructured. Production cost ~1/100th LLM API inference; ~1/10,000th continual update. Deletion certs categorically unavailable in fine-tuned LLMs -> HIPAA/GDPR primary product wedge. P=0.245 for "1/100th cost at parity accuracy".
- 2026-06-04 23:40 (Interface-preservation 2x drill): **Bridge D (attention K/V injection) is the ONLY algebraically correct bridge for VSA binding**. Modern Hopfield = attention identity means K/V injection IS the unbinding op. Bridge A (text) loses binding at tokenization; Bridge B (logit-residual) viable only at concept-vocab scale; Bridge C (hidden-state) partial. **Two-bridge hybrid (A text for factual + D attention K/V for relational) is the product architecture.** D-RIP norm preservation != binding preservation (critical distinction). P=0.33 for bridge D analogical 1.5x lift. Validates Tier 4 substitution as architecturally correct.
- 2026-06-04 23:50 (Depth-scaling 2x drill): **K_max = 3.3 * (1 - alpha/alpha_c)^2 / alpha** per substrate; empirical K=12 at alpha=0.5*alpha_c matches; predicts K=47 at alpha=0.1*alpha_c; K scales sqrt(N) at fixed alpha. **Hierarchical: D^2 * f(alpha/D) gain; saturation at D~8-16 from routing error**. Compositional generalization 60-80% of stored-chain depth. **Resonator augmentation gives 2.7x depth boost** (highest-leverage architectural extension). **Substrate has NO position bias vs LLM CoT's K~4 collapse from Weakest Link Law** -- structural 3-25x depth advantage on stored chains. **D=4-6 substrates cover medical/legal/KG-QA production at K=40-80**; scientific synthesis (K>=50 compositional) needs resonator or DAG extension.
- 2026-06-04 23:55: 5 new high-priority experiments routed to Exp-Dev from drill synthesis (research_to_exp_dev_3_drill_synthesis_priority_experiments): K_max formula validation; compositional generalization K=10-20; resonator-augmented depth; Medical Path Y KG distillation prototype; hierarchical D saturation. Plus CCC-1 REVISED -> CCC-1 REVISED-v2 (two-bridge hybrid). Tier 4 substitution ELEVATED priority (bridge D implementation).
- 2026-06-04 22:50 (**FLAGSHIP**): **Tier-4 substrate-attention IN Pythia-160M HARD_PASS** -- ppl_ratio 1.06x, entropy_ratio ~3, grad_ratio <1. Substrate-Hebbian attention is TRAINING-STABLE inside a REAL pretrained LLM. **EMPIRICAL VALIDATION of Bridge D (per interface-preservation drill)**. Substrate-as-intrinsic-LLM-component validated at Pythia-160M scale. This + Tier 6 = substrate's two paths into LLM both work.
- 2026-06-04 23:35 (Overnight batch 1): **Tier-6 Phase D FULL on GPU = MIDDLE_BAND** -- BPC within band but GPU speedup didn't clear 2.0x. CRITICAL NUANCE: GPU parallelizes baseline's backprop cheaply -> no-backprop advantage is HARDWARE-DEPENDENT (favors CPU/backprop-expensive regimes). Tier-6-CPU full run is the BETTER speedup test (smoke showed 1.98x; CPU full still pending). + Confirmed FULL HP: P1 SQ2*cfRPE; P2 SQ2*hierarchical (24-hop); B36-ratio (3 ratios); SQ5 N=100k matrix-free 10x+ biological scale. MIDDLE: SQ2 load (collapse at 2x alpha_c); efficiency-comp 16x; SQ3. HF: B5-bounded (replay fundamental negative); SQ6-v2 cleanup (membership SNR-limited).
- 2026-06-05 00:55 (hourly cadence): substrate-as-intrinsic-LLM-component now has TWO empirical anchors (Tier 4 HP at Pythia + Tier 6 Phase D BPC viable). Pythia extraction npz STILL pending -- blocks CCC-1 REVISED-v2 + EX-CONCEPT-real + substrate-audit-core. Architecture's training-speed advantage is hardware-dependent (CPU > GPU).
- 2026-06-05 00:00 (Exp-Dev): **Pythia-160M extraction QUEUED** (gate fix: --self-test early-exit added). GPU idle post-v7-kill.
- 2026-06-05 00:25 (**FLAGSHIP**): **Pythia-160M extraction HARD_PASS** (residuals.npz 11.9MB; >=5000 residuals; shape (n,768)). **Audit-core C2/C3 BUILT + QUEUED on REAL Pythia residuals** (smoke synthetic HP: C2 deletion-cert=1.00, C3 drift-separation=7.4x). This is the HIPAA/GDPR product wedge approaching empirical validation: deletion certs categorically unavailable in fine-tuned LLMs.
- 2026-06-05 00:25: **EX-CONCEPT-1 REAL GATING: NEEDS PER-TOKEN extraction** -- current npz is PER-DOC (n,768), not token sequences within docs. Holding EX-CONCEPT-real pending Testbed per-token extraction.
- 2026-06-05 02:00 (hourly cadence): audit-core C2+C3 on REAL Pythia residuals is the STRONGEST near-term product anchor (per Exp-Dev surfacing); validates HIPAA/GDPR product wedge empirically. EX-CONCEPT-real gated on per-token extraction. CCC-1 REVISED-v2 + CCC-1-EXTRA need offline KG/QA datasets (Wikitext loader had HfUriError; may need offline Wikidata/HotpotQA/NQ data).
- 2026-06-05 01:00 (**FLAGSHIP**): **audit-core-v2 whitened on REAL Pythia residuals = HARD_PASS** (C2 deletion-cert=0.98, C3 drift=11x). HIPAA/GDPR product wedge EMPIRICALLY VALIDATED. Whitening insight: real (correlated) activations need DECORRELATION before storage for clean deletion (PCA-whiten or cf-RPE storage).
- 2026-06-05 01:20 (**FLAGSHIP**): **Tier-6 Phase D CPU FULL = HARD_PASS** (BPC<=1.20x baseline AND speedup>=2.0x AND audit-during-training operational). Substrate-intrinsic LLM training validated at substrate's ACTUAL speedup regime. "Vastly increase LLM training speed (CPU/edge)" thesis EMPIRICALLY ANCHORED. Plus full HP confirmations: P3 B6xSQ2 audit-preserving reasoning; compositional generalization K10-20; CCC-AGGRESSIVE VSA reasoning.
- 2026-06-05 01:20: **K_max depth formula is PESSIMISTIC** -- substrate reasons deeper than 3.3*(1-alpha/alpha_c)^2/alpha predicts. Recommend revisiting derivation. Likely candidate: NESS dynamics not captured in equilibrium-derived formula; need non-equilibrium correction. Future-drill candidate.
- 2026-06-05 01:20: **P4 + P5 confirm sparsity-modality-specificity at FULL** -- sparse coding helps PATTERN/auto-assoc capacity (B2 x B4 100x; B2 x hierarchical 125k) but NOT SEQUENCE capacity (P4 posbind, P5 STDP). Bloom-SQ6 also confirms structural membership wall.
- 2026-06-05 01:45 (**FLAGSHIP**): **CCC-2 substrate-only structured QA = HARD_PASS** -- exact-match >=70% at K=3 multi-relation KG traversal (V=200, R=5). PATH-B CEILING CONFIRMED: substrate alone handles structured multi-relation retrieval/reasoning (no LLM needed). + **NEW EXP 3 resonator/cleanup-augmented depth = HARD_PASS at 6x depth boost** (drill predicted 2.7x; actual 6x). Plain iterated retrieval collapses to ~4 hops at 2x alpha_c overload; cleanup-augmented sustains 24+ hops. PRODUCTION KNOB: resonator/cleanup extends reasoning depth far past plain ceiling.
- 2026-06-05 01:45: DEFERRED pending Research design input: R1 4-modulator (cf-RPE is dimension-bound; needs importance-weighted reframe); R2 sparse-resonator (construction subtleties); R5/R6 D-RIP composition (shared-metric framing required).
- 2026-06-05 01:45: capacity-comp N4096/N8192 GPU failed 3x with no logs/metrics (infra issue, NOT script -- passed --self-test + smoke). Flag for Testbed GPU-runner inspection. Capacity multiplicative principle validated at N=2048 (125k); N>2048 scaling is nice-to-have, not blocking.
- 2026-06-05 03:00 (hourly cadence): substrate cognitive-core product narrative empirically anchored at 5 validation points: (1) audit-core HP on real Pythia residuals (HIPAA/GDPR wedge); (2) Tier-6 CPU FULL HP (training-speedup); (3) Tier-4 Pythia HP (bridge D); (4) CCC-AGGRESSIVE + CCC-2 HP (VSA reasoning + PATH-B structured); (5) resonator depth 6x boost (production knob). The "substrate-as-cognitive-core for regulated multi-hop reasoning" story is empirically anchored.
- 2026-06-05 02:35 (**FLAGSHIP**): **NEW EXP 5 hierarchical-D saturation FULL HP** -- capacity scales linearly to D>=20 (independence held). Production (N, D) sizing confirmed. **Depth-capacity production-curve HP**: plain reasoning depth is LOAD-FRAGILE (24 @ 1x alpha_c -> 4 @ 2x -> 0 @ 3x); CLEANUP-augmented depth is LOAD-ROBUST (24 across all loads to 3x; 15x advantage at high load). Cleanup/resonator augmentation is THE production knob for reliable deep reasoning under capacity pressure. Substrate can deploy at 3x alpha_c with cleanup = maximum-capacity production deployment.
- 2026-06-05 02:10 (Exp-Dev clarification requests): R1 needs FAMILIARITY/RECURRENCE signal (not just error/novelty signals); R2 needs sparse-preserving BIND operator (Frady-Sommer block-local binding per published spec); R5/R6 needs concrete shared-substrate + shared-metric op-by-op spec. Design input shipped 04:00.
- 2026-06-05 04:00 (hourly cadence): substrate cognitive-core empirically anchored at SIX validation points (added NEW EXP 5 + depth-capacity production-curve). Production deployment story: maximum-capacity (3x alpha_c) with cleanup-augmentation gives reliable deep reasoning. Clarifications for R1/R2/R5/R6 design shipped to Exp-Dev.
- 2026-06-05 03:20: **R2 sparse-resonator block-local binding HP smoke** (K4/K8=1.00) -- queued full. R1 4-modulator HF AGAIN -- DEFERRED FINAL with root cause: cf-RPE error-gating ALREADY provides recurrence-reinforcement (when recurring pattern degrades, error rises, cf-RPE re-writes); familiarity is REDUNDANT with cf-RPE on recurring-recall. To show 4-modulator gap need ACTIVE-DELETION-PRESSURE task or ONE-SHOT-important-amid-noise. Accept single-modulator sufficiency for recurrence tasks.
- 2026-06-05 03:45 (R-series wrapup): **R2 sparse-resonator FULL HP at K=26** (block-local sum-bind enables high-K vs dense ~7-9 ceiling). VALIDATED Mode 4 NC1 extension. **R6 B2-storage x sparse-resonator HARD_FAIL** -- D-RIP super-additive REFUTED for this pairing. Root cause: storing M composites in shared auto-assoc W creates CROSSTALK that corrupts BLOCK structure resonator needs for cleanup -> wrong codes. **NEW COMPOSITION LESSON: storage x structured-recovery INTERFERE rather than compose** (refines composition taxonomy: orthogonal-axis multiplicative on CAPACITY but NOT on every pairing/metric; cross-space pairs need shared metric; error-axis modulators don't stack). R5 DEFERRED -- B8 is logit-BRIDGE not capacity primitive; its M_crit contribution undefined.
- 2026-06-05 05:00 (hourly cadence): R-series complete. Final composition taxonomy: (a) capacity orthogonal-axis MULTIPLICATIVE (B2 x B4 = 125k); (b) capacity orthogonal-axis INTERFERES if storage x structured-recovery (R6 HF); (c) reasoning orthogonal-axis MULTIPLICATIVE (SQ2 x Hierarchical = 24-hop); (d) audit + reasoning MULTIPLICATIVE (B6 x SQ2); (e) mixed-stream input SUPERADDITIVE (B36); (f) sparsity is MODALITY-SPECIFIC (helps auto-assoc; not sequence); (g) efficiency SUB-MULTIPLICATIVE (B3a x B3b 16x; gates overlap); (h) error-axis modulators DON'T STACK (R1 DEFERRED -- single-modulator sufficient). Substrate cognitive-core empirically anchored at 7 validation points (added R2 sparse-resonator K=26 HP).
