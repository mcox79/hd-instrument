# Research drill 5x/#2 — Math + information theory on brain-analog competitive-Hebbian sparse encoder HARD_FAIL vs char-trigram bag on WordNet held-out-synonym retrieval

**Trigger:** USER 2026-07-02 late evening "important negatives 5x drill." This is component 2/5 (math + info theory) on the critical negative: k=2%/N=2048 competitive-Hebbian sparse encoder loses to char-trigram bag by 0.12 recall@5 (0.16 vs 0.28) on WordNet held-out-synonym retrieval, N=100 candidates.

**Discipline:** lit-scan calibration penalty applied (deflate P estimates 0.15-0.25; cap novel-synthesis P at 0.50). Generic terms only in queries. Substrate-KB concept-query MANDATORY-first done (see §1).

---

## §1. Prior-work check — substrate-KB concept-query

Three cosine queries via `tools/substrate_query.sh`:

| Query | Top-3 hits | Overlap |
|---|---|---|
| "sparse bipolar capacity bound Frady Sommer WordNet retrieval" | (1) `notes/research_drill_capacity_envelope_3x_2026-06-27.md::Frady-Sommer capacity bound`, cos=0.40; (2) `notes/research_drill_capacity_envelope_3x_2026-06-27.md::chunk006` (Kanerva 1988 + Frady-Sommer sparse-bipolar SNR), cos=0.31; (3) `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md::chunk015` (Frady-Kleyko-Sommer 2023 TNNLS linear-in-N dense vs quadratic-in-N sparse), cos=0.30 | HIGH |
| "information theoretic sparsification transfer real corpus" | (5) `notes/research_drill_bipartite_engineered_underperforms_learned_2x_2026-06-11.md::chunk026` (Williams-Beer PID; Brown et al. MI feature-selection), cos=0.37 | MEDIUM |
| "bag of features baseline logistic regression retrieval" | (2) `notes/wave14d_edit_then_query_research.md::Tier C retrieval baselines`, cos=0.34; (4) `preregs/2026-06-26_substrate_director_kb_language_trio_v1.md::ARM_REGRESSION_BASE_KB`, cos=0.30 | MEDIUM |

**Prior-work overlap:**
- `research_drill_capacity_envelope_3x_2026-06-27.md` — Frady-Sommer sparse-bipolar bundle SNR O(N/M); Kanerva 1988 sparse-bipolar capacity ≈ 0.1·N to 0.5·N; sparse-bipolar with cleanup expected to survive α_N=2-5 at sparsity **10-20%** active bits (NOT 2%); channel-capacity headroom ~140× (decoder-bound, not channel-bound); hippocampal CA3 capacity ≈ 0.2·C/(a·ln(1/a)).
- `research_drill_hrr_capacity_vs_depth_2026-06-23.md` — Frady-Kleyko-Sommer 2023 TNNLS: **linear-in-N capacity dense bipolar; quadratic-in-N sparse binary** BUT sparse requires factorizer/resonator for unbinding from compositional structures; Kanerva original: BSC stores K=400-800 pairs at N=10000 → M/N ~ 0.05-0.08.
- `research_drill_bipartite_engineered_underperforms_learned_2x_2026-06-11.md` — Williams-Beer 2010 PID; Brown et al. 2012 MI feature-selection framework.

**Delta from prior work:** the prior capacity drills characterized the substrate STORAGE envelope (how many discrete patterns fit); this drill characterizes the RETRIEVAL / GENERALIZATION envelope on a real held-out-synonym task, where the failure mode is TRAINING-OBJECTIVE / SAMPLE-COMPLEXITY misalignment, NOT raw capacity. This is a novel angle not covered by prior work.

---

## §2. Capacity-bound analysis — does k=2% at N=2048 have enough capacity?

**Frady-Sommer sparse-bipolar capacity formula** (openreview 6tazBqPem3, Frady-Kleyko-Sommer TNNLS 2023):

For sparse-bipolar codes with sparsity a (fraction active), bundle capacity M_max at SNR threshold:
- Dense (a=0.5): M_max ≈ 0.138·N (Hopfield critical capacity)
- Sparse-bipolar: M_max ≈ N/(2·ln(1/a)) at cleanup-with-decoder (loose bound; tighter bounds depend on decoder margin)

**Substituting k=2% at N=2048:**
- a = 0.02 → ln(1/a) = ln(50) ≈ 3.912
- M_max ≈ 2048/(2·3.912) ≈ **262 distinguishable patterns**

**CA3 autoassociative capacity** (Treves-Rolls 1991; verified in `research_drill_capacity_envelope_3x_2026-06-27.md`):
- capacity ≈ 0.2·C/(a·ln(1/a)) where C = synaptic fan-in
- If C ≈ N = 2048 (full connectivity in W): capacity ≈ 0.2·2048/(0.02·3.912) ≈ **5238 patterns**

**Task load:**
- Task uses N=100 candidates → **capacity is NOT the bottleneck** on either formula (100 << 262 or 5238).
- WordNet: 6339 atoms → capacity edge on the CA3 formula; at Frady-Sommer bound would fail at 2048.
- ConceptNet 133K nodes → would need N ≈ 65536 at same sparsity, or drop sparsity to a≈0.05.

**Verdict Q1: capacity is NOT the bottleneck at N=100 candidates.** The mechanism could in principle store 100 concept patterns cleanly at k=2%/N=2048 with margin. The failure is elsewhere.

---

## §3. Signal-to-noise / rate — does the mechanism preserve enough surface-feature signal to beat bag?

**Rate comparison (bits/pattern):**

| Encoding | Active dims | Discrete pattern count | Raw bits/pattern |
|---|---|---|---|
| Sparse-bipolar k=2% N=2048 | 40 bipolar | C(2048,40)·2^40 | log2(C(2048,40)) + 40 ≈ 293 + 40 = **~333 bits** |
| Char-trigram bag (500 active of ~17K) | 500 binary | C(17576,500) | log2(C(17576,500)) ≈ **~5300 bits** |

**Bag has ~16× more raw bits/pattern than sparse-bipolar at k=2%.**

**BUT** — raw rate is not what the retrieval task rewards. The task rewards **preservation of surface trigrams shared between held-out synonym and training synonyms/definition**. This is a specific information channel, not raw entropy.

**Information channel analysis:**
- Definition + training synonyms + hypernym: ~500-1000 chars → ~500-1000 unique trigrams, some repeated.
- Char-trigram bag: preserves EACH trigram occurrence with position-agnostic count. Total info about surface features: ~5000 bits.
- Competitive-Hebbian at k=2%: trains 40-dim latent code to SEPARATE atoms → objective is task-agnostic (or class-based); it does NOT explicitly preserve the "which surface trigrams occurred" signal. Even worse: it may *actively discard* redundant surface features to maximize inter-concept margin.

**Mutual information view — what the task actually requires:**
- Held-out synonym S_test shares K trigrams with definition D + training synonyms S_train.
- Bag: I(bag(concept), bag(S_test)) ≈ K · log2(1/trigram_prior) ≈ K · 14 bits (for uniform prior on ~17K trigrams) — direct surface match.
- Competitive-Hebbian: I(code(concept), code(S_test)) requires the LEARNED CODE to preserve the trigram-of-S_test information. But: (a) k=2% throws away 98% of the input signal, (b) the training objective did not explicitly reward preserving surface trigrams of held-out synonyms it never saw.
- **The bag directly implements the sufficient statistic for the task; the learned code implements a task-orthogonal compression.**

**Signal-to-noise numeric estimate for competitive-Hebbian on held-out task:**
- Training signal per concept: ~3 sentences × ~200 chars/sentence × ~200 trigrams/sentence ≈ 600 trigram-instances.
- Encoded to 40 active dims via competitive winner-take-all: each dim represents a compressed conjunction of ~15 trigram-instances.
- On held-out synonym S_test: shares ~10-30 trigrams with training. Under WTA compression, ~10-30/600 ≈ **2-5% overlap in latent activations**.
- SNR = signal_overlap / random_overlap ≈ 0.03 / (40/2048) ≈ 0.03/0.02 ≈ **1.5** — barely above noise floor.
- Bag SNR on same task: signal_overlap / random_overlap ≈ 20/500 / (500/17576) ≈ 0.04/0.028 ≈ **1.4** — comparable numerically.

**BUT bag has ~13× more input bits (500 vs 40 features on comparable Bernoulli approximation), so its DECISION MARGIN scales better.**

**Verdict Q2/Q3: signal-to-noise mismatch is real.** The mechanism aggressively compresses surface features that the retrieval task specifically rewards. The bag benefits from **feature redundancy** exactly where competitive-Hebbian discards it.

---

## §4. Sample-complexity / PAC analysis — is 3-4 training sentences per concept enough?

**PAC-learning bound** for a hypothesis class H at accuracy ε, confidence δ:
- m ≥ (1/ε) · (ln|H| + ln(1/δ))

**Competitive-Hebbian hypothesis class:**
- Each concept mapped to sparse-bipolar code with 40 active dims of 2048.
- Distinct codes: C(2048,40) · 2^40 ≈ 10^96 raw hypotheses per concept.
- For 100 concepts jointly: |H| ≈ (10^96)^100 = 10^9600. ln|H| ≈ 22100.
- At ε=0.1, δ=0.05: m ≥ 10 · (22100 + 3) ≈ **221000 samples per concept required for PAC-guarantee generalization.**

**Available: 3-4 sentences per concept. Shortfall: ~5 orders of magnitude.**

But PAC bounds are loose; effective sample complexity for competitive-Hebbian at N=2048/k=2% with 3-sample training may still be tractable IF the effective VC dimension of the LOSS surface (not the full hypothesis class) is small.

**Effective VC dimension estimate:**
- Competitive winner-take-all with lateral inhibition selects ~40 dims to represent each concept.
- Each dim's activation is a linear function of ~2048 input features (before WTA).
- Effective VC ≈ 40 · 2048 ≈ 80K parameters (if trained end-to-end); ~40 · 100 = 4000 effective (if only concept-specific slots learn per concept).
- With 3 sentences × 100 concepts = 300 samples total → hopelessly below either bound.

**Bag-of-features has NO learning:**
- Sample complexity = 0 for the FEATURE map; only the concept "prototype" (bag average over training sentences) requires samples.
- 3 samples per concept is enough for a stable bag prototype (bag is high-dim and averaging is well-conditioned).
- **Bag exploits the fixed-feature structure to bypass learning; the mechanism cannot.**

**Verdict Q4: 3-4 samples per concept is dramatically insufficient for competitive-Hebbian to learn discriminative latents at k=2%.** This is a fundamental sample-complexity gap, not a config tuning question. Bag-of-features wins because it doesn't need to learn.

---

## §5. Rate-distortion characterization — where on R-D curve is the current mechanism?

**Rate-distortion frame:**
- Rate R = bits/pattern in the encoding.
- Distortion D = task-specific error (e.g., 1 - recall@5).

Empirical operating points on this task:
- Bag-of-features: R ≈ 5300 bits, D ≈ 0.72 (recall@5 = 0.28).
- Competitive-Hebbian k=2%: R ≈ 333 bits, D ≈ 0.84 (recall@5 = 0.16).

**R-D curve interpretation:**
- At same rate, the mechanism should sit ON OR ABOVE the R-D curve (Shannon bound).
- Bag is far ABOVE the R-D curve (D=0.72 at R=5300 is suboptimal — a learned encoder at 5300 bits should hit D << 0.72).
- Sparse-Hebbian at R=333 bits is also above the curve but the curve at low rate is inherently worse for this task (retrieving among 100 concepts with held-out synonyms requires ~log2(100)=6.6 bits minimum + surface-feature overlap).

**Prediction:** if we relaxed sparsity from k=2% to k=20% (Frady-Sommer recommended band per `research_drill_capacity_envelope_3x_2026-06-27.md`):
- 400 active dims → R ≈ log2(C(2048,400))+400 ≈ 1470+400 ≈ **1870 bits/pattern (5.6× current)**.
- Should partially close the R-D gap. Whether it beats bag on this specific task depends on whether the LEARNED code exploits its ~6× rate budget better than bag exploits its ~3× rate budget.

**Information bottleneck (Tishby) frame:**
- IB objective: minimize I(X;T) subject to I(T;Y) ≥ threshold, where Y is task-relevant target.
- For held-out-synonym retrieval, Y = "which concept does this held-out synonym belong to."
- Competitive-Hebbian's WTA training objective is NOT the IB objective. WTA minimizes I(X;T) subject to concept-separation, which is a proxy for I(T;Y_seen) but not I(T;Y_held-out).
- **IB prediction:** at k=2%, competitive-Hebbian sits BELOW the IB optimal frontier for the held-out-synonym task. The k=20% relaxation moves it closer; a task-aligned training objective (e.g., contrastive with held-out synonyms as positives) would move it further.

**Verdict Q5/Q6: current k=2% + WTA-only training is misconfigured for the R-D curve of this task.** Both sparsity relaxation AND objective realignment are theoretically required.

---

## §6. Theoretical verdict — can the mechanism beat bag on this task?

**Given theory alone, is the mechanism fundamentally incapable of beating bag-of-features on this task?**

**NO — mechanism is not fundamentally incapable, but the current config (k=2%, WTA-only training, 3 samples/concept) IS fundamentally under-configured for the specific task shape.**

**Structural verdict decomposition:**

1. **Capacity bound (Q1):** 100 concepts easily fit — capacity is NOT the bottleneck. NO WALL HERE.
2. **Rate (Q2, Q5):** k=2% throws away ~16× the raw bits vs bag. WALL AT CURRENT CONFIG, RELAXABLE by k→20%.
3. **Sample complexity (Q4):** 3-4 sentences/concept is dramatically below PAC bound for learning discriminative latents. WALL AT CURRENT PROTOCOL, RELAXABLE only by external data augmentation OR non-learning-based feature initialization (see hybrid path in §7).
4. **Training-objective alignment (Q3, Q5):** WTA separation objective is NOT aligned with held-out-synonym task. WALL AT CURRENT OBJECTIVE, RELAXABLE by contrastive / masked-synonym / reconstruction objective.
5. **Signal preservation (Q2, Q3):** WTA compression discards surface features that bag directly rewards. WALL AT CURRENT COMPRESSION, RELAXABLE by hybrid architecture (bag prior + learned residual) or by fixed-feature-preserving encoder pre-layer.

**Overall theoretical verdict: mechanism CAN work with all four config levers moved (sparsity ↑, objective realigned, hybrid architecture, sample augmentation). Any ONE lever alone is insufficient.**

---

## §7. If theory says CAN work: which config regime?

**Configuration recommended by theory (composes with drill 1 empirical sweep):**

| Lever | Current | Theory-recommended | Rationale |
|---|---|---|---|
| Sparsity k | 2% (40 dims) | **10-20%** (200-400 dims) | Frady-Sommer optimal band; ~5× rate lift |
| N_dim | 2048 | 2048 (unchanged for this task) or 4096 (for scale) | Capacity headroom already large at N=100 |
| Training objective | WTA separation only | **Contrastive with masked-synonym positives** + WTA regularizer | IB-aligned to held-out task |
| Architecture | Pure learned | **Bag-features fixed prior + learned residual overlay** | Composes surface-feature strength of bag with latent-space strength of Hebbian |
| Samples/concept | 3-4 (WordNet-limited) | **Augmented** via synonym-swap paraphrase generation OR use synonym set membership as label expansion | Push effective m up 5-10× |
| Cleanup decoder | argmax nearest-neighbor | **Factorizer/resonator** (Frady-Kleyko-Sommer 2023) | Sparse-bipolar retrieval requires factorizer for compositional structures |

**Composing with drill 1 (empirical sweep):**
- Drill 1's sweep should include k ∈ {2%, 5%, 10%, 20%, 40%} × training-objective ∈ {WTA, contrastive, contrastive+WTA} × architecture ∈ {pure learned, bag-prior + learned residual}.
- Predicted best: k=15-20%, contrastive+WTA, bag-prior + learned residual. Expected recall@5 = 0.30-0.40 (matches or slightly beats pure bag).

---

## §8. If theory says CANNOT work: what mechanism class WOULD work theoretically?

Even though the CAN-work verdict is positive, honest naming of what mechanism-classes are unambiguously better on this task:

1. **Dense embeddings from character-CNN or BPE-tokenizer + shallow MLP** — sits at high-rate low-distortion corner of R-D curve; sample-complexity manageable with pre-training.
2. **Pure bag-of-trigrams + IDF weighting** — the current opponent; theoretically optimal for surface-feature retrieval up to concept count where co-occurrence noise dominates (empirically ~10K-100K concepts).
3. **Hybrid HRR bundle of trigram-hyperbind rolls** (Plate 1995 + Frady-Sommer 2023) — preserves surface-feature signal via distributed binding; k=10-15% sparsity; theoretically superior to competitive-Hebbian WTA for compositional surface features.
4. **Random-feature-fixed sparse code + learned prototype vectors** — bypasses learning entirely; ~zero sample complexity; would likely match bag-of-features at N=100 with less rate.

**Class most closely aligned with substrate-native philosophy:** Option 3 (HRR bundle of trigram hyperbinds) — this is compositional, brain-analog, and theoretically superior at the current sample-complexity budget.

---

## §9. Cross-thread synthesis with substrate arcs

- **Arc: encoder-side cleanup ceiling** (`notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md`, ENC1 sparse-fan-in encoder in flight) — ENC1's k=5 sparse-fan-in is closer to the Frady-Sommer optimal band; expect ENC1 to partially close the gap without further config changes.
- **Arc: char-trigram encoder as substrate default** (`preregs/2026-06-26_substrate_director_kb_language_trio_v1.md::ARM_REGRESSION_BASE_KB`) — bag-of-trigrams is ALREADY the encoder used for substrate-KB queries and it works well; this drill supplies theoretical backing for its use as a fixed prior in hybrid architectures.
- **Arc: capacity envelope** (`research_drill_capacity_envelope_3x_2026-06-27.md`) — predicted k=10-20% sparsity is optimal; current k=2% is deep in the underrate regime for this task.
- **Discipline check "substrate doesn't know anything yet":** this drill is about the ENCODER, not about substrate language-knowledge. No Stage-3+ overclaim. Held-out-synonym retrieval is a Stage-1/2 instrument property.

---

## §10. Deliverable summary

- **Path:** `d:/AI/hd-instrument/notes/research_5x_drill_2_math_info_theory_substrate_content_HF_2026-07-02.md`
- **Top-line theoretical verdict:** competitive-Hebbian sparse encoder at k=2% is NOT fundamentally incapable of beating bag on WordNet held-out-synonym retrieval; it is CONFIG-UNDERTUNED across four independent levers (sparsity, training objective, architecture, sample augmentation). Any ONE lever alone is insufficient; theory predicts all four are needed to match-or-beat bag at the current 100-concept scale.
- **Best single lever:** relax sparsity from k=2% to k=10-20% (Frady-Sommer optimal band). Predicted alone gain: 0.05-0.10 recall@5 (0.16 → 0.21-0.26; still below bag's 0.28).
- **Second-best single lever:** hybrid architecture with bag-features as fixed prior + learned residual. Predicted alone gain: 0.08-0.15 recall@5.
- **Combined all four levers:** predicted recall@5 = 0.30-0.40 (matches or slightly beats pure bag).
- **P estimate for "config-retuned mechanism beats pure bag on this specific task":** raw 0.55 (theory strongly supports), lit-scan calibration penalty −0.20 (novel synthesis: no published bench of this exact hybrid), novel-synthesis cap 0.50 → **P = 0.35**.
- **P estimate for "pure competitive-Hebbian at ANY k with WTA-only training beats bag":** **P = 0.10** (theoretically the WTA objective mismatch is fundamental; sparsity relaxation alone cannot close it).
- **P estimate for "bag remains best on this task at N=100 concepts even with tuned mechanism":** **P = 0.55** (bag has structural advantage on surface-feature-shaped task at low concept count; mechanism advantage only emerges at scale).

**Recommended compose with drill 1 (empirical):** drill 1's sweep should be run at the four-lever combined config, not just sparsity sweep. Without objective realignment + hybrid architecture, the sparsity sweep alone will land in MIDDLE_BAND (recall improves but does not match bag).

**Recommended compose with drill 3-5:** if drill 3 (brain-analog / mechanism) shows the sparsification-is-brain-grounded prior is at k=5-10% (dentate gyrus expansion), that aligns with this drill's k=10-20% recommendation and strengthens the hybrid-architecture path.

---

## References

- Frady, F., Sommer, F. "Capacity Analysis of Vector Symbolic Architectures." OpenReview 2018/2022. `openreview.net/pdf?id=6tazBqPem3`
- Frady, F., Kleyko, D., Sommer, F. "Variable Binding for Sparse Distributed Representations: Theory and Applications." IEEE TNNLS 2023. `arxiv.org/pdf/2009.06734`
- Kanerva, P. "Sparse Distributed Memory." MIT Press 1988.
- Treves, A., Rolls, E. "What determines the capacity of autoassociative memories in the brain?" Network 1991.
- Tishby, N., Zaslavsky, N. "Deep learning and the information bottleneck principle." 2015.
- Williams, P., Beer, R. "Nonnegative Decomposition of Multivariate Information." arXiv 1004.2515 2010.
- Plate, T. "Holographic reduced representations." IEEE TNN 1995.
- Substrate: `notes/research_drill_capacity_envelope_3x_2026-06-27.md`, `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md`, `notes/research_drill_bipartite_engineered_underperforms_learned_2x_2026-06-11.md`.
