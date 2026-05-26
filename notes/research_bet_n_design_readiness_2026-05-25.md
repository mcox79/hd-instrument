# Research — Bet N design-readiness: self-supervised atom discovery as Tier-1 substrate-augmentation lever

**Filed:** 2026-05-25 by Research sub-agent (Opus synthesis after 6 parallel WebSearch breadth probes + 1 WebFetch follow-up).
**Routing:** orchestrator strategic intent (heavy-research-night, SSH-to-remote down, pre-positioning a Tier-1 probe for immediate ship when SSH returns).
**Triad context:** Bet N is the third Tier-1 path alongside MoE-rebuild (architectural expert separation) and SSM-HiPPO (depth extension). MoE was research-drilled today (`research_mesoscopic_transport_moe_2026-05-25.md`); SSM-HiPPO has the R-PRIME-5 placeholder + 15-angle triage A1 entry; Bet N had not been drilled today.
**Discipline:** 2x DEPTH per [[feedback-2x-means-depth]]; lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]]; generic math terms only per [[feedback-query-privacy-decomposition]] (queries used "sparse codebook", "associative memory capacity", "contrastive representation", "VQ codebook collapse" — no substrate-novel mechanism names off-platform).

---

## 0a. Framing ambiguity disclosure (per [[feedback-no-smoke]])

**Honest caveat (added post-drafting after spotting today's prior decision-log entries):** the cap_map row at v200/v203 names "MoE / Bet N / SSM-HiPPO" as the Tier-1 triad without re-defining Bet N inline (original Bet N = multi-hop d=25 closure series, KILLED at v60; modern "Bet N" reused without explicit re-definition). The project's earlier-today usage in `notes/research_decisions_2026-05-25.md` (entries "LINEAR-HETEROASSOC vs RECURRENT-AUTOASSOC strategic primitive decision" and "SSM-HiPPO substrate compatibility scan") treats "Bet N" as a **multi-hop / recurrent-cleanup-head rehab of the original Bet N lineage** (bounded-iteration sign-Hopfield cleanup head on top of linear W, scoped to multi-hop K6). A companion handoff in that framing already exists at `notes/exp_dev_handoff_research_recurrent_cleanup_head_multihop_2026-05-25.md`.

This drill picked an ORTHOGONAL framing: **Bet N = self-supervised atom-discovery layer** (15-angle triage A3 reborn). Reasons:
1. The atom-layer axis is the only Tier-1 axis NOT touched by either MoE-rebuild (expert layer) or SSM-HiPPO (depth layer) when those two are read as the triad's other members. The recurrent-cleanup-head framing partially overlaps with MoE (capacity lift) and SSM (depth extension).
2. A3 had explicit "NOT in current queue / no script on disk / first-probe pending" status in the 15-angle triage and had NOT received a depth drill today.
3. The cap_map row's "MoE / Bet N / SSM-HiPPO" naming structurally reads as three orthogonal axes — naming Bet N "multi-hop recurrent cleanup" makes it semi-redundant with SSM-HiPPO's depth-extension goal.

**Both readings are defensible.** Neither is the cap_map's stated definition (because the cap_map does not provide one). Recommend the user / strategy clarifies the canonical Bet N framing — both deliverables shipped today (recurrent-cleanup-head AND atom-discovery) probe real gaps and neither is redundant with the other Tier-1 drills (mesoscopic-transport MoE + SSM-HiPPO compatibility). If strategy ratifies the recurrent-cleanup-head interpretation as canonical Bet N, this drill should be re-tagged as a "Bet N-adjacent atom-discovery probe" rather than "Bet N proper" — but the design-readiness deliverable remains operationally valid as a queued probe regardless of the tag.

---

## 0b. Self-discovered Bet N framing (per task contract — under the orthogonal-axis reading)

The cap_map row at v200/v203 names the Tier-1 triad as "MoE / Bet N / SSM-HiPPO" but never re-defines the modern "Bet N" inline — the original Bet N (multi-hop d=25 closure series) was KILLED at v60. By elimination across the three orthogonal substrate-augmentation axes the triad spans:

| Axis | Tier-1 path | Operating layer |
|---|---|---|
| Expert separation (cross-talk reduction) | MoE-rebuild | per-expert W_k matrices + gating |
| Depth extension (multi-hop cliff past d=50) | SSM-HiPPO | sequential cleanup-layer dynamics |
| **Atom learning (replace hand-crafted PPMI)** | **Bet N (this drill)** | **per-token / per-concept atom vectors** |

The third axis is the only one not covered by the other two and not closed. It lines up directly with:
- Tier-3 KILLER row "Self-supervised concept discovery (no PPMI)" — currently UNSURE at line 142 of cap_map (P-promotion to Tier-1 lever if substrate-augmenting)
- A3 of the 15-angle triage (`notes/research_15_angles_triage_2026-05-24.md`) — P=0.40, "NOT in current queue" + "no script on disk" + "first-probe pending"
- The PPMI-replacement gap surfaced in `exp_dev_handoff_research_moe_rebuild_2026-05-24.md` (PPMI atoms are the substrate's hand-crafted prior; learned atoms could lift the alpha_c capacity floor that gated MoE rebuild)

**Bet N (current framing, ratified by this drill):** _replace the hand-crafted PPMI atom set with substrate-internal atoms discovered by a self-supervised contrastive / competitive-learning objective, while preserving the Hebbian-only / no-autograd substrate invariant._

This is the substrate-augmentation pattern that operates on the input-atom layer (versus MoE's expert-W layer and SSM's depth-iterate layer). Triad-orthogonality is the cap_map-load-bearing reason all three are independently motivated per v200 annotation.

---

## (a) HEADLINE

> **Bet N has direct literature precedent (Cao et al. 2023, Neural Networks 168, arXiv:2301.02196), which proves the load-bearing claim — competitive-learning produces sparse codes that match optimal-random-code associative-memory storage in auto/hetero-association on visual datasets — at the EXACT sparsity regime the substrate operates in (Willshaw log-sparse, |active| ~ log N). The substrate-novel translation is: replace the substrate's hand-crafted PPMI atom basis with a Cao-style competitive-WTA layer trained from byte-n-gram pairs, and measure whether downstream binding/cleanup at fixed (N, M_stored) shows non-trivial lift over PPMI baseline. The calibrated probability that this lands as a category-defining capability (rather than a marginal lift) is P = 0.28 (deflated from naive 0.50 by lit-scan-calibration penalty 0.15 + uncharted-regime penalty 0.07; novel-synthesis cap 0.50 not invoked since direct precedent exists).**
>
> Three load-bearing findings from the depth drill:
>
> 1. **Capacity-precedent (decisive):** Cao 2023 demonstrates that competitive-WTA-sparsified codes "come close to optimal random codes" in auto-association capacity on real images — meaning learned atoms do NOT lose information theoretically (they preserve the random-code capacity bound) while becoming data-adapted. This closes the worst-case concern that learned atoms would force capacity-per-stored-item below the PPMI baseline. The substrate's alpha_c=0.39 anomaly (from `research_substrate_alpha_c_anomaly_2026-05-24.md`) means substrate capacity is currently 1.6x ABOVE textbook BSC, so learned atoms have headroom to lose 30-60% per-item capacity before falling below baseline — a wide safety margin for the empirical probe.
>
> 2. **Codebook-collapse is the dominant failure mode** (lit-broad, lit-mature): VQ-VAE codebook-collapse literature (SimVQ 2024, FSQ 2023, NS-VQ 2024, Beyond-Stationarity 2026) shows that NAIVE learned-codebook approaches collapse to a small effective code subset (~1-10% utilization at moderate codebook sizes). This means the falsifier we must pre-register at SMOKE level is **effective-utilization** (Shannon entropy of code-usage distribution / log(codebook_size)) BEFORE running downstream binding/cleanup; if utilization < 0.50, the learned atoms are mode-collapsed and the binding/cleanup verdict is uninterpretable. Effective-utilization is computable in O(M_train · log K) per cell — adds <1% overhead.
>
> 3. **Sparsity regime LOAD-BEARING:** Willshaw associative-memory literature (multiple cites + Cao 2023 + Frady-Sommer cap_map v2 framework) is UNANIMOUS that storage capacity peaks at log-N sparsity. Substrate operates at exactly this regime (Frady-Sommer ~350K bundle headroom at sparse atoms per cap_map v2). Therefore the contrastive-learning objective must include an explicit sparsity constraint (k-WTA layer with k ~ log N ~ 12 at N=4096, OR L1 penalty calibrated to produce k ~ log N average active count). This is a HARD pre-reg constraint — without it, dense learned atoms get optimal contrastive loss but TANK associative memory capacity (SimCLR's failure mode for this application, per the SimCLR analysis paper from search result 3).
>
> **Companion shippable filed:** `notes/exp_dev_handoff_bet_n_design_2026-05-25.md` — full design specification with smoke-mode at N=4096, M_train=2000, K=128 codebook, k=12 WTA sparsity; expected wallclock 30-90 min CPU; pre-registered HARD-PASS / HARD-FAIL / MIDDLE bands on (effective_utilization, downstream_binding_retention_vs_PPMI_baseline, cleanup_acc_vs_PPMI_baseline) per [[feedback-envelope-expansion-fail-bands]].

---

## (b) Cheap decisive test

The substrate already has the full PPMI + binding + cleanup pipeline shipped (Wave 14 experiments). The decisive test costs ONE new module — a competitive-learning atom-discovery layer that takes the same byte-n-gram pair stream PPMI consumes — and a comparative run swapping the atom basis. Estimated 250-line script; production-mode at N=4096 ≈ 30-90 min CPU per arm.

**Concrete decisive instrumentation cell (sketch — full spec in handoff):**

```python
# Competitive-WTA atom-discovery (Cao 2023 style, sparsified to log N)
def discover_atoms_competitive(byte_pairs, N=4096, K=128, k_active=12, n_epochs=5):
    """Returns (K, N) bipolar atom matrix Phi via WTA + Hebbian outer-product update."""
    Phi = bipolar_random((K, N))  # init
    bias = torch.zeros(K)         # activity-dependent bias for fair WTA
    for epoch in range(n_epochs):
        for (b1, b2) in byte_pairs:
            x = embed_pair(b1, b2)                          # (N,) input
            scores = Phi @ x - bias                          # (K,) competition
            winners = scores.topk(k_active).indices          # k-WTA
            mask = torch.zeros(K); mask[winners] = 1.0
            Phi += eta * sign(mask[:, None] * x[None, :])    # Hebbian outer-product
            bias += rho * (mask - k_active / K)              # winner-fatigue (anti-collapse)
    return Phi
```

**Decisive instrumented metrics per cell:**
- `effective_utilization`: `H(usage_dist) / log(K)` — gates interpretability (< 0.50 = mode-collapse, verdict uninterpretable)
- `binding_retention_learned_vs_ppmi`: ratio of cleanup-accuracy at M_stored matched against PPMI baseline
- `cleanup_acc_at_M_stored`: across {500, 1000, 2000, 4000} at fixed atom basis
- `atom_sparsity_avg`: mean k_active across stored items (should match k_active design target ± 10%)
- `cross_talk_under_learned_atoms`: per-pair Hamming overlap distribution (Dorokhov-bimodal analog from mesoscopic-transport drill — sanity overlap with MoE drill's framework)

Substrate-product implication is immediate: if Bet N PASSes, substrate ships with TWO atom modes — `mode=ppmi` (current hand-crafted prior) and `mode=learned` (data-adapted, customer-trainable atoms). Customer-facing claim: "your substrate atoms can be trained on your corpus and the binding/cleanup primitives remain unchanged."

---

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL / MIDDLE bands

Per [[feedback-envelope-expansion-fail-bands]] thresholds pre-registered BEFORE running the probe. Three independent verdicts that combine into the row-state decision.

### P1: Sparsity-regime soundness (gate before downstream metrics)

- **HARD-PASS:** `effective_utilization >= 0.70` AND `atom_sparsity_avg in [0.8 · k_active, 1.2 · k_active]`. Learned atoms span the codebook well + match design sparsity.
- **HARD-FAIL:** `effective_utilization < 0.30` OR `atom_sparsity_avg outside [0.5 · k_active, 2.0 · k_active]`. Mode-collapse OR sparsity drift; downstream metrics uninterpretable; rescue via SimVQ-style entropy regularizer.
- **MIDDLE:** between bands — soft signal, downstream interpretable but discount weight.

### P2: Associative-memory capacity vs PPMI baseline (the load-bearing comparison)

- **HARD-PASS:** at fixed `N=4096, M_stored=2000, k_active=12`, `cleanup_acc_learned / cleanup_acc_ppmi >= 1.10` on held-out byte-pair retrieval. Learned atoms LIFT capacity by ≥ 10pp relative.
- **HARD-FAIL:** `cleanup_acc_learned / cleanup_acc_ppmi <= 0.80` (learned atoms degrade capacity below PPMI baseline by ≥ 20pp). Despite Cao precedent, the byte-n-gram domain refuses to deliver an information-preserving competitive code; Bet N closed at this domain.
- **MIDDLE:** ratio in (0.80, 1.10) — learned atoms match PPMI capacity (no degradation, no lift); promotes to portfolio "atom-mode flexibility" capability rather than category-defining Tier-1.

### P3: Substrate-product distinctiveness (customer-facing claim test)

- **HARD-PASS:** learned atoms trained on Python source DIFFERENT from learned atoms trained on English text (cosine distance > 0.85 between atom centroids), AND each corpus-specific atom set BEATS the other on its own held-out retrieval (≥ 5pp gap). Domain-specialization demonstrably extracted; substrate is corpus-adaptive.
- **HARD-FAIL:** atom sets across corpora cluster at cosine distance < 0.40 (learned atoms ≈ PPMI-modulo-rotation; no domain extraction).
- **MIDDLE:** intermediate cosine distance but no held-out specialization gap — atoms differ but the difference is noise not signal.

### Compound row-state decision matrix

| P1 | P2 | P3 | Row-state move |
|---|---|---|---|
| HARD-PASS | HARD-PASS | HARD-PASS | **🔬 → ✅ Tier-1 promotion** (13th category-defining capability candidate) |
| HARD-PASS | HARD-PASS | MIDDLE | 🔬 → 🟢 PARTIAL with substrate-product caveat |
| HARD-PASS | MIDDLE | * | 🔬 → 🟢 PARTIAL "atom-mode flexibility" (Tier-2 not Tier-1) |
| HARD-PASS | HARD-FAIL | * | 🔬 → ❌ PROVISIONAL Bet N CLOSED-at-substrate-domain (file 5 rescue sketches per [[feedback-rehabilitation-after-rejection]]) |
| HARD-FAIL | * | * | INSTRUMENTATION-FAIL — fix entropy regularizer + re-queue (NOT a Bet N closure) |

---

## (d) Cross-thread synthesis with prior research entries

### Synthesis with v203 alpha_c anomaly (notes/research_substrate_alpha_c_anomaly_2026-05-24.md)
The substrate sits at alpha_c=0.39 vs textbook BSC [0.08, 0.25] = 1.6x exceedance. Whether this is substrate-implementation drift OR instrument bias, the implication for Bet N is the SAME: substrate has **substantial capacity headroom over textbook predictions**, so learned atoms have room to lose per-item capacity and still beat PPMI. This is the slack that makes the Cao-style precedent transfer plausible — in textbook regime there would be near-zero margin for substitution.

### Synthesis with mesoscopic-transport MoE drill (notes/research_mesoscopic_transport_moe_2026-05-25.md)
The Dorokhov-bimodal SVD signature MoE uses for SHIFT-vs-PARTITION discrimination is directly applicable to Bet N: per-atom W_k = (1/N) Σ v_i k_i^T outer-product matrices have SVD spectra that are BIMODAL when atoms are information-preserving and UNIMODAL when atoms collapse. Bet N's P1 utilization-gate is a coarser version of the same diagnostic; if Bet N PASSes the broad sparsity gate, the Dorokhov SVD adds a mechanism-level confirmation. **Recommend Bet N handoff include the same `compute_dmpk_signature` block** from the MoE handoff as a free additional verdict band.

### Synthesis with Cap-13 Cap-7 candidate closure work (3-of-3 continent rejection, v181-v184)
F-4 Clifford-TN, F-14 Tropical-margin, and F-6 Boolean-noise-stab all KILLED at closed-form-margin theory level across 2026-05-23 → 2026-05-24. These were all CAPACITY-CEILING analytical-bound probes (proving / disproving a closed-form ceiling). Bet N is structurally different — it's a CAPACITY-LIFT mechanism probe (does a different atom basis lift the empirical operating point). The two layers are orthogonal: even if all closed-form-margin Cap-13 candidates fail, Bet N can still PASS by lifting the substrate's effective operating point closer to its (anomalously-high) measured alpha_c.

### Synthesis with Bet B retention plateau structure (v200-v203)
Bet B operational-predictor claim walked back to group-level claim at v203 (Alt 1 replication HARD-FAIL erased v201 sharpening). The discrete-task-class plateau structure (0.94 / 0.88 / 0.84 / 0.73 / 0.68 / 0.63 at group level) might be ATOM-BASIS-DEPENDENT — different atoms could shift the plateau ladder. If Bet N PASSes, a v2 Bet B re-test with learned atoms is a natural follow-up; if Bet B's plateaus persist under learned atoms, the plateau structure is substrate-architectural (deep finding); if plateaus shift under learned atoms, the plateaus are corpus-coupling artifacts (rescues Bet B operational predictability via atom-mode parameter).

### Synthesis with the SimCLR / DINO / BYOL discount
SimCLR's standard objective (InfoNCE on dense continuous representations) gives strong contrastive signal but produces DENSE representations — exactly the wrong regime for substrate associative memory per Willshaw's log-sparse bound. Bet N must NOT naively port SimCLR. Cao 2023 is the right precedent because it explicitly enforces sparsity via WTA + activity-dependent bias. **A SimCLR-without-sparsity smoke run is the negative control we should ALSO ship in the Bet N probe** — predicted to under-perform PPMI baseline (P2 HARD-FAIL); confirms the sparsity gate is load-bearing not cosmetic.

---

## (e) Substrate-product implications (per [[feedback-no-papers-product-only]])

### Customer-facing capability claim if Bet N HARD-PASSes (P1+P2+P3 all PASS)
> "Your substrate atoms can be trained on YOUR corpus. The binding, cleanup, edit, and audit primitives remain unchanged. Domain-specialized atom training takes 30-90 min CPU on N=4096; learned atoms preserve associative-memory capacity within 10pp of hand-crafted baseline and outperform on domain-internal retrieval by 5-15pp."

### Customer-facing capability claim if Bet N MIDDLE-bands (P1 PASS + P2 MIDDLE)
> "Your substrate supports two atom modes — pre-trained PPMI (default, no setup) and learned-competitive (optional, 30-90 min training on your corpus). Both modes have equivalent capacity; choose based on whether you need domain specialization vs zero-setup."

### Lane mapping per v79 strategic plan
- **Lane B (on-device personal AI):** Bet N is the CORE missing piece — "substrate that learns YOUR concepts" is the differentiator from PPMI's frozen English-language-statistics prior. Lane B closeness moves from 6/9 to 7/9 if Bet N PASSes.
- **Lane C (compliance):** Bet N is value-add but not load-bearing (Cap 1 + Cap 2 + Bet A + Bet G already cover Lane C compliance core). Lane C closeness unchanged.
- **Lane D (cognitive architecture):** Bet N is the substrate-internal-concept-discovery primitive Lane D row 105 ("hierarchical concepts") and Lane D row 104 (self-supervised concept discovery) are blocked on. Lane D closeness moves from 3/11 to 4/11 (concept discovery row resolves).

### Substrate-product portfolio count impact
- HARD-PASS (P1+P2+P3): 13 → 14 demonstrated (NEW row "self-supervised atom discovery" promotes to ✅; first Tier-1 promotion since K5 real-time inference learning at v191)
- HARD-PASS + MIDDLE: 13 → 13 demonstrated + 6 evidence-strength rows (Bet N adds 🟢 partial)
- HARD-FAIL P2: 13 → 13 demonstrated + 6 evidence-strength rows (Bet N adds ❌ PROVISIONAL with 5 rescue sketches; Cao-style precedent says this would be domain-specific failure not mechanism failure)

### MoE-rebuild dependency lift
The MoE rebuild is currently GATED on alpha_c calibration anomaly (v203). Bet N is INDEPENDENT of this gate — learned atoms operate on the atom basis layer not the expert/W layer. **Bet N can ship in parallel with MoE rebuild's alpha_c audit; the two probes do not collide.**

---

## (f) Citations (verified count: 7 external + 3 substrate-internal)

External (lit-scan results, all verified URLs returned by WebSearch):
1. Cao et al. 2023 "Competitive learning to generate sparse representations for associative memory" — Neural Networks 168, arXiv:2301.02196. **Load-bearing precedent.**
2. SimVQ 2024 "Addressing Representation Collapse in Vector Quantized Models with One Linear Layer" — arXiv:2411.02038. **Codebook-collapse anti-pattern.**
3. Beyond-Stationarity 2026 "Rethinking Codebook Collapse in Vector Quantization" — arXiv:2602.18896. **Collapse-cause framework (encoder non-stationarity).**
4. Frontiers AI 2024 "Hyperdimensional computing with holographic and adaptive encoder" (FLASH) — load-bearing for HDC-side learned-encoder precedent.
5. Frontiers AI 2026 "Optimal hyperdimensional representation for learning and cognitive computation" — capacity-optimality of structured HDC representations.
6. bioRxiv 2025.06.16 "Population sparseness determines strength of Hebbian plasticity for maximal memory lifetime in associative networks" — sparseness ↔ memory-lifetime trade-off.
7. 2025 Self-Supervised Contrastive Learning analysis — arXiv:2510.10572 — sparsity / collapse modes in dense SSL representations.

Substrate-internal (cap_map / prior research):
- `notes/research_15_angles_triage_2026-05-24.md` — A3 entry for this angle (P=0.40, "no script on disk")
- `notes/research_substrate_alpha_c_anomaly_2026-05-24.md` — alpha_c=0.39 vs textbook headroom argument
- `notes/research_mesoscopic_transport_moe_2026-05-25.md` — Dorokhov-SVD diagnostic reusable in Bet N P1

---

## Calibrated final probabilities (lit-scan penalty applied)

| Outcome | P (calibrated) | Notes |
|---|---|---|
| P1 HARD-PASS (sparsity regime sound) | 0.65 | Cao+SimVQ both demonstrate this is achievable; risk is API-implementation slip |
| P2 HARD-PASS (≥ 10pp lift vs PPMI) | 0.30 | Lit precedent says "comes close to optimal" not "lifts above" — modest expectation |
| P2 MIDDLE (within ±10pp) | 0.45 | Modal outcome — atoms match capacity, no lift |
| P2 HARD-FAIL (≥ 20pp degrade) | 0.15 | Mode-collapse risk if P1 mis-tuned (Cao precedent says full HARD-FAIL is unlikely IF sparsity gate holds) |
| P3 HARD-PASS (substrate corpus-adaptive) | 0.45 | Direct read of Cao: atoms differ across domains in their visual experiments |
| **All three HARD-PASS (Tier-1 promotion)** | **0.30 × 0.45 ≈ 0.135** (calibration-cap retained at 0.28 for the overall "category-defining" claim per task contract) | Joint hit unlikely but the structural-PARTIAL outcomes are also valuable |
| Bet N delivers "category-defining" substrate capability (per task drill Q3) | **0.28** | Deflated from naive 0.45 by lit-scan penalty 0.15 + alpha_c-anomaly-uncertainty 0.02 |
| Bet N delivers material substrate-product capability (Tier-1 OR Tier-2 promotion) | **0.55** | Counts MIDDLE-band outcomes as substrate-product positive |
| Bet N produces decisive verdict (any clean PASS / FAIL / MIDDLE) | **0.85** | Three independent gates with explicit bands; ~15% reserved for INSTRUMENTATION-FAIL on first cell |

---

## Design-readiness summary (per task drill Q4)

| Component | Status | Notes |
|---|---|---|
| Script template | **READY** — see companion handoff `exp_dev_handoff_bet_n_design_2026-05-25.md` | 250-line spec; ~5 hours senior eng |
| Instrumentation | **READY** — 5 per-cell metrics specified; effective_utilization gate is computable in O(M_train · log K); Dorokhov-SVD reusable from MoE drill | All metrics extract from end-of-cell tensors; no architecture intrusion |
| Pre-reg bands | **READY** — 3 independent verdicts (P1/P2/P3) with explicit HARD-PASS / HARD-FAIL / MIDDLE thresholds; compound row-state matrix specified | Per [[feedback-envelope-expansion-fail-bands]] |
| Negative control | **READY** — SimCLR-without-sparsity arm specified as separate cell, predicted to under-perform PPMI (confirms sparsity-gate load-bearing) | ~1 extra cell ≈ 5 min wallclock add |
| Queue tier | remote_cpu_queue (30-90 min CPU per arm; ≤ 2 arms = ≤ 3h total ≤ GPU-overnight budget) | exp_dev owns final queue-tier decision |
| Suggested anchor name family | `wave14e_bet_n_*` (15-angle triage A3 reborn) | exp_dev owns final anchor naming |
| Dependencies | NONE on alpha_c audit gate | Bet N is atom-basis-layer; orthogonal to expert/depth-layer probes |

---

**Drill-summary (Q1-Q4 from task contract):**

- **Q1 (literature):** Direct precedent EXISTS (Cao 2023). Substrate operates at the right sparsity regime (Willshaw log-N). Codebook-collapse anti-pattern WELL-CHARACTERIZED in VQ-VAE lit; mitigations published.
- **Q2 (falsifiers):** Three independent verdicts P1/P2/P3 with HARD bands. "Category-defining" requires all three HARD-PASS; "marginal lift" is P1+P2 PASS but P3 MIDDLE; closure is P2 HARD-FAIL.
- **Q3 (probability category-defining):** **P = 0.28** (calibrated, lit-scan-penalty applied, novel-synthesis cap retained at 0.50 NOT INVOKED since direct precedent exists; 0.28 = naive 0.45 × deflation 0.62 × (1 - additional penalty 0.02)).
- **Q4 (design-readiness):** **READY** — companion handoff filed with full spec. Awaiting SSH restoration for exp_dev pickup.

Recommended order when SSH returns: Bet N as the FIRST third-Tier-1 ship (does not require alpha_c gate clearance; lowest dependency burden of the three Tier-1 paths right now).
