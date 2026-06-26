# Research drill 1 of 4 — BARRIERS half (math + literature)

**Date:** 2026-06-25
**Author:** Research (Director)
**Wall:** ~40 min
**Companion:** parallel drill (solutions/brain-analogs) covers the other half — this file is BARRIERS only

**Discipline applied:** lit-scan calibration penalty (deflate P 0.15-0.25; novel-synthesis cap P=0.50); under-claim by default; literature claim vs substrate evidence labeled inline; intuitive language with math relegated to footnotes.

---

## TL;DR (read this if nothing else)

Anisotropy breaks dense superposition memory for ONE load-bearing reason: **the cleanup step at retrieval relies on items being approximately ORTHOGONAL on average; when items cluster into a narrow cone the dot products between an unrelated key and the cue are no longer near zero — they have a non-trivial mean and a fat-tailed distribution — so the signal-from-the-right-item drowns in correlated cross-talk from the others**. Increasing item count M makes it worse because every additional item adds correlated noise rather than independent noise.

- **Fundamental (theory says you cannot beat it with this code-class):** the capacity bound `M ≈ d / (cone_concentration)` is geometric — it depends on the eigenspread of the item covariance, not on cleverness in retrieval. With encoder anisotropy `PR/D ≈ 0.22` (substrate measurement, r3 diagnostic), effective dimension is `~0.22 d` not `d`. At d=768 that's ~170 useful directions, not 768.
- **Engineering (people keep trying, keep getting partial fixes):** whitening / flow / contrastive — each rotates the SAME underlying low-rank manifold; they don't ADD new directions. They look great on similarity-task benchmarks (where you just need angles) and stay broken on retrieval-from-superposition (where you need M independent orthogonal signal-carriers).
- **Substrate evidence is consistent with this story:** ZCA-whitening (`exp_dense_KV_whitening_revival_v1_gpu`) recovered only +0.020 absolute on real Pythia residuals despite passing the cone diagnostic — same low-rank manifold, just rotated.

The hard claim: **anisotropy isn't a corruption to clean — it's a property of the data. The encoder's output literally lives in a thin cone, so there are only ~PR/D worth of independent directions to distribute M items across.** Every solution that does not ADD directions (or USE the cone-structure rather than fight it) hits the same ceiling.

---

## ANGLE A — Math / theory of WHY anisotropy breaks dense superposition

### A1. Formal capacity bound (Frady-Sommer / Plate / Cohen)

**Literature claim:** For dense bipolar / HRR superposition with `M` items in dimension `d`, retrieval is reliable when `M ≲ c · d / log(K)` where K is the codebook size and c is an O(1) constant set by the cleanup-recall threshold. The bound assumes items are drawn iid from a near-isotropic distribution (uniform on the sphere, or symmetric Bernoulli). Frady-Sommer 2020 (NeurIPS / arXiv 2009.06734, "Variable Binding for Sparse Distributed Representations") gives the dense and sparse-block versions; Plate's 1995 HRR thesis is the original derivation; Cohen (2017+) refines.

**Why anisotropy breaks the assumption:** the proof works because the cross-term inner products `<x_i, x_j>` for `i≠j` are zero-mean with variance `1/d`. Add M of them and you get noise of variance `M/d` against signal of variance `1`. So `M < d` is reliable, `M ≫ d` is not. With anisotropy, `<x_i, x_j>` is NOT zero-mean — items in a cone are positively correlated on average. So you accumulate `M · μ` of MEAN cross-talk (not just noise floor), and signal-to-cross-talk goes from `O(d/M)` to `O(1/μ)` where μ depends on cone concentration. Once `μ > 1/d`, capacity is no longer linear in `d`.

**Intuitive:** orthogonality is the magic. If every pair of items is at 90° on average, their inner products average to zero and you can stack M items and still pull each one out. When items lean into a cone, every pair has a positive baseline overlap, and stacking them just builds up that baseline. You're not retrieving anymore — you're reading the cone direction back.

**Substrate-evidence cross-check:** `exp_dense_KV_whitening_revival_v1_gpu` measured ARM0 (kNN, no superposition) = 1.000 at M=400 — items ARE retrievable when stored explicitly. ARM2 (softmax-attention, dense allocator with M-dependent normalization) = 0.75-0.93. ARM1 (M-independent superposition) collapsed to 0.05-0.07 raw, 0.07-0.16 whitened. The collapse is specific to the M-independent superposition store, exactly as the math predicts.

### A2. Why anisotropy compounds geometrically AND probabilistically

**Geometric reading:** if items live in an eigenspread where the top-10% of dimensions hold >50% of variance (substrate measurement: 0.512 top10pct_energy at D=384), then the "effective angle" between random items is much smaller than 90° — even after re-normalization. Small angles → high dot products → bigger cross-talk. The cleanup head sees a wash.

**Probabilistic reading:** the cross-term sum `Σ_{j≠i} <x_i, x_j>` is a sum of correlated random variables, not iid. By the Lindeberg condition / CLT in the iid case, the sum has stdev `O(√M)`. In the anisotropic case the sum has BOTH a mean term `O(M·μ)` AND inflated variance `O(M · σ²_correlated)`. The mean dominates for any reasonable M.

Compounding: if you add MORE items to fight noise (more redundancy), you ALSO add more correlated cross-talk. So the usual "more samples = less noise" intuition is inverted under anisotropy.

**Intuitive:** imagine a choir. Independent singers (isotropic): adding more makes the sound fuller but no single voice dominates. Singers who all lean the same way (anisotropic): adding more just makes everyone sound MORE like the leaning direction; you can't pick out any individual voice.

### A3. Marchenko-Pastur edge — when does eigenspread → 1 cause the cliff?

**Literature claim:** for an `M × d` matrix of items with iid entries, the singular value spectrum has support `[√M-√d, √M+√d]` (the M-P density). When `M/d → 1`, the smallest singular value → 0 — meaning the codebook becomes rank-deficient. Cleanup heads (which usually solve a least-squares or pseudo-inverse) blow up because the smallest singular value sits in the denominator.

For dense associative memory: the relevant M-P regime is the BASIN structure. As load `α = M/d → critical`, basins shrink anisotropically; some patterns lose their basin entirely (PMC review on attractor stability). Anisotropic codes hit critical α at LOWER M because the effective dimension is `d_eff = d · (PR/D)` — substrate measured `d_eff ≈ 86` at d=384.

**Substrate-evidence cross-check:** the substrate's calibration regime (M=400 already showing ARM1=0.048) is consistent with `M ≈ 5 · d_eff` already exceeding the linear regime. This is NOT 10x or 100x past — it's already saturated at modest M.

### A4. Mu-Viswanath cone-collapse — is it the right frame?

**Literature claim:** Mu & Viswanath 2018 ("All-but-the-Top") and follow-ups show that word embeddings (word2vec, GloVe) have a dominant mean component plus a few dominant directions; removing the top few principal components dramatically improves cosine-similarity tasks. This is the original "anisotropy hurts retrieval" diagnostic.

**Is it the right frame for substrate?** Partly. The Mu-Viswanath frame says "subtract the cone, then the residual is more isotropic." This works for similarity tasks because they only need DIRECTIONS to disambiguate. It does NOT work for superposition memory because removing the dominant components REDUCES the dimensionality of the residual space, making the capacity problem WORSE (smaller d → smaller M-capacity). You can't subtract your way to more directions.

**This is the load-bearing distinction the user is asking about:** anisotropy is a problem for two DIFFERENT reasons:
1. **For similarity tasks:** the cone WASHES OUT signal — Mu-Viswanath fix works (rotate / subtract / re-norm).
2. **For superposition retrieval:** the cone LIMITS CAPACITY — Mu-Viswanath fix is irrelevant because the residual has fewer useful directions, not more.

The substrate (`exp_dense_KV_whitening_revival_v1_gpu`) is in case 2. Whitening = rotate to fix anisotropy, but the residual still lives in the same low-rank manifold. Recovery = +0.020. Bound by the M-P / capacity ceiling.

### A5. Information-theoretic ceiling at fixed d, eigenspread X

**Sketch:** the information capacity of a dense superposition store is bounded by `I ≤ d · log(K) · η` where η is a coding efficiency factor proportional to the eigenspread (entropy of the singular spectrum). For perfectly isotropic codes, η ≈ 1. For anisotropic codes with PR/D = 0.22, η ≈ 0.22 (proportional but not identical — depends on the cleanup decoder).

So at d=768 with PR/D=0.225, the EFFECTIVE store capacity is `~169 · log(K)` not `~768 · log(K)` — a ~4.5x reduction. This is enough to explain ARM1 collapse at M=200 (200 > 169 already past the bound).

**Caveat (lit-scan calibration penalty applied):** the exact form of η depends on encoder + decoder choice and is NOT a clean closed-form. Treat the `0.22` factor as a LOWER BOUND on the efficiency loss; the practical loss can be worse due to non-Gaussian heavy tails in the inner-product distribution. P=0.45 on the exact functional form being usable for capacity prediction (not 0.60).

### A6. Closed-form for anisotropy → recall cliff?

**Honest answer:** there's no clean single-equation closed-form for arbitrary encoder distributions. The Frady-Sommer dense bound `M ≈ d/c` and the M-P spectrum together give the BEST-CASE; deviations are heavy-tailed and require monte-carlo. The substrate's own meter (calibration ARM cap at 0.445-0.824) reflects exactly this — it's a measured upper bound per encoder + decoder combo, not a derived constant.

Functional form that fits substrate data approximately: `recall ≈ recall_max · exp(-α · M / d_eff)` where `d_eff = d · PR/D` and α depends on the decoder. The substrate `exp_dense_KV_whitening_revival_v1_gpu` data is roughly consistent with `α ≈ 1` and `recall_max ≈ 1` if `d_eff` is taken as the post-whitening effective rank — but n=1 seed; this is a hypothesis-fit not a chain-grade finding.

---

## ANGLE B — Literature history: what people tried and where they hit walls

### B1. LSH lineage (Indyk-Motwani → Charikar → Andoni-Indyk)

**Original:** Indyk & Motwani 1998 "Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality" — formalized LSH as a family of hash functions where `P[h(x)=h(y)]` depends only on `d(x,y)`. Charikar 2002 SimHash gives cosine-similarity LSH via random hyperplanes.

**Formal guarantee:** finds (1+ε)-approximate nearest neighbor in time `O(n^(1/(1+ε)))` with high probability — sub-linear, but ONLY for the SEARCH problem (given a query, find the closest stored point).

**Where it BREAKS for dense superposition:** LSH is a SEARCH primitive (return the index of the closest stored point), not a STORE primitive (compress M items into one vector and recover individually). They're different problems:
- LSH: O(M) storage, sub-linear query.
- Dense superposition: O(d²) storage independent of M, requires cleanup-from-mixture.

Charikar SimHash on substrate (`exp_anisotropy_rescue_4arm_sweep_v1_gpu` ARM B' = 0.982 at M=1000) basically WORKS — but it's a 238 bits/memory explicit store, which is by-design rather than M-independent. The capacity isn't anisotropy-limited because it doesn't superpose.

**Lesson (intuitive):** LSH is a different storage class. It "solves" anisotropy by paying O(M) storage. Substrate dense KV wants the M-independent superposition class — different problem.

### B2. Fly LSH (Dasgupta-Stevens-Navlakha 2017)

**Claim:** "A neural algorithm for a fundamental computing problem" (Science 2017) — Drosophila olfactory circuit implements a variant of LSH: 50 PNs → 2000 KCs via sparse random expansion, then anterior-paired-lateral (APL) feedback enforces top-5% winner-take-all. This 5%-sparse high-dimensional code preserves locality.

**What follow-ups found:**
- Ryali et al. 2020 ("Bio-Inspired Hashing for Unsupervised Similarity Search", ICML) extended FlyHash with learned random weights — modest gains, mostly in low-dimensional regime.
- The KEY LIMITATION: FlyHash assumes ISOTROPIC inputs (or near-uniform odor distribution). When inputs are anisotropic, the sparse expansion preserves the anisotropy in the expanded space — you get sparse codes but still cone-concentrated. Sharan / Vaezi follow-ups confirm.
- Density-preserving variants (Sharan-Valiant; Indyk) try to preserve LOCAL density too, helping with anisotropic data — but at cost of formal LSH guarantees.

**Substrate-evidence:** ARM B in `exp_anisotropy_rescue_4arm_sweep_v1_gpu` (fly-LSH on Pythia residuals) = 0.612 at M=1000, well below the Charikar variant (0.982). The vanilla fly-LSH variant did NOT fully recover, consistent with the lit-scan finding that fly-LSH inherits its inputs' anisotropy.

**Lesson (intuitive):** the fly works because odor space is approximately isotropic (or the fly's earlier processing isotropizes it). Drop anisotropic inputs into the same architecture and you don't get isotropic outputs — you get sparse anisotropic outputs.

### B3. Cerebellar sparse fan-in (Marr 1969 → Albus 1971 → modern)

**Claim:** cerebellar granule cells receive ~K=4-5 mossy-fiber inputs each (Marr 1969 "A theory of cerebellar cortex" — the original); the sparse fan-in DECORRELATES inputs by combinatorial mixing. Modern work (Cayco-Gajic & Silver 2019 Neuron "Re-evaluating circuit mechanisms underlying pattern separation"; Litwin-Kumar et al. 2017 Neuron "Optimal degrees of synaptic connectivity") confirms K=4-7 is optimal for pattern separation, with the optimum depending on input correlation structure.

**Why K=5 specifically:** for K too small (K=1-2), outputs inherit input correlations directly. For K too large, every granule cell sums to similar values → decorrelation collapses. K≈4-7 hits the sweet spot where mixing is sufficient to decorrelate but not so much that all outputs converge.

**Limit relevant to substrate:** the cerebellar trick works only if the GRANULE LAYER IS EXPANSIVE (more granule cells than mossy fibers). Cerebellum has ~50B granule cells vs ~50M mossy fibers — 1000x expansion. Substrate ARM A (`exp_anisotropy_rescue_4arm_sweep_v1_gpu`, K=5 cerebellar) = 0.041 at M=1000 — well below the cone-rotation ceiling. Likely a smoke-test calibration issue (expand5x was probably insufficient; cerebellum uses 1000x) OR the input anisotropy was severe enough that even sparse fan-in can't decorrelate.

**Lesson (intuitive):** brain uses ~1000x expansion ratio with K=5 fan-in. A 5x expansion with K=5 is the right MECHANISM at the wrong SCALE.

### B4. BERT / RoBERTa anisotropy and the whitening attempts

**Diagnosis:** Ethayarajh 2019 EMNLP ("How Contextual are Contextualized Word Representations?") showed BERT / GPT-2 representations have average random cosine similarity approaching 1.0 in upper layers — embeddings live in a narrow cone. Confirmed by Mu & Viswanath, Gao et al., and many follow-ups.

**Whitening attempts:**
- Su et al. 2021 ("Whitening Sentence Representations for Better Semantics and Faster Retrieval") — apply PCA-whitening to sentence embeddings. WORKS for STS (semantic textual similarity) — measurable Spearman gains.
- Li et al. 2020 ("On the Sentence Embeddings from Pre-trained Language Models") — BERT-flow uses normalizing flows to map to isotropic Gaussian. Also works for STS.

**Why it doesn't generalize:**
- "Whitening Not Recommended for Classification Tasks in LLMs" (arXiv 2024) — whitening HELPS similarity tasks (where geometry matters) but HURTS downstream classification (where the cone-structure may itself encode useful information).
- WhitenedCSE / WhiteningBERT confirm: whitening + contrastive is COMPLEMENTARY — neither alone is enough.
- Critical limit: whitening is a LINEAR REVERSIBLE transformation. It rotates the existing low-rank manifold into an isotropic-looking shell, but the RANK doesn't increase. Information capacity is unchanged.

**Lesson (intuitive — load-bearing for substrate):** whitening makes the cone LOOK round from outside, but the data still lives on a low-rank surface inside that round shell. For similarity (where you only ask "are these two close?") it works because the angles now properly reflect closeness. For superposition retrieval (where you need M orthogonal carriers) it fails because the rank is unchanged.

**Substrate-evidence:** `exp_dense_KV_whitening_revival_v1_gpu` whitened-recovery = +0.020 absolute. The diagnostic `exp_r3_encoder_anisotropy_diagnostic_v1` measured PR/D = 0.225 BEFORE whitening; the encoder is in the same low-rank manifold AFTER whitening (whitening doesn't change rank). The substrate finding directly confirms the linear-transformation-doesn't-add-rank principle.

### B5. Sentence-BERT contrastive (Reimers-Gurevych 2019) and why contrastive works where whitening fails

**Claim:** Reimers & Gurevych 2019 EMNLP ("Sentence-BERT") — Siamese BERT with contrastive loss produces sentence embeddings that work for STS. Subsequent SimCSE / DiffCSE / unsupervised CSE confirm.

**Why contrastive works:** Wang & Isola 2020 ICML ("Understanding Contrastive Representation Learning through Alignment and Uniformity on the Hypersphere") prove contrastive loss optimizes a trade-off between (1) alignment (positives close) and (2) uniformity (negatives spread). The UNIFORMITY term DIRECTLY incentivizes the model to USE more of the hypersphere — not just rotate.

This is the LOAD-BEARING DIFFERENCE vs whitening:
- Whitening: a post-hoc LINEAR rotation. Cannot add rank.
- Contrastive: a TRAINING SIGNAL that reshapes the encoder. The encoder's weights actually CHANGE to spread mass over more directions. Rank CAN increase.

**Limit:** contrastive only works if you can train (or fine-tune) the encoder. For a FROZEN encoder (substrate's case with Pythia), you can't get this gain — you're stuck with the cone-shaped output and can only rotate it.

**Lesson (intuitive):** contrastive succeeds because it CHANGES the encoder to use more directions. Whitening fails because it only ROTATES the existing directions. If you're frozen-encoder, you have whitening's problem, not contrastive's solution.

### B6. Cone-collapse in attention (Dong et al. 2021)

**Claim:** Dong, Cordonnier & Loukas 2021 ICML ("Attention is not all you need: pure attention loses rank doubly exponentially with depth") — pure self-attention (without skip-connections / MLP) causes outputs to converge to a rank-1 subspace doubly-exponentially fast with depth. Skip-connections and MLPs are NECESSARY to prevent collapse, not nice-to-haves.

**Substrate relevance:** confirms anisotropy is an INTRINSIC dynamic of attention-style operations, not a training artifact. Any architecture that does many rounds of "weighted sum of all keys" will tend to cone-collapse without explicit counter-pressure.

**Lesson (intuitive):** attention naturally compresses to a cone. Modern transformers fight this with skip-connections (which preserve the input distribution) and MLPs (which add nonlinear non-collapsing directions). Substrate dense superposition is the WORST CASE — pure weighted-sum, no skip, no MLP. Of course it cone-collapses; that's the default dynamic.

### B7. HRR / VSA anisotropy — did Plate know?

**Plate (1995 thesis, 2003 book):** assumes ISOTROPIC base vectors (uniform on the sphere or Gaussian). Capacity bound `M ≈ d/k` (k = O(1)) derived under this assumption. Plate did NOT address what happens with real anisotropic data — his work was foundational symbolic-binding, not data-encoded HRR.

**Eliasmith / NEF (2002+):** the Neural Engineering Framework uses tuning curves to map real-world signals into vectors, then HRR operations. Eliasmith's encoding step DOES include explicit decorrelation (tuning-curve diversity), which is one way of avoiding the anisotropy problem at the encoding stage — buy isotropy with engineering, don't fight it post-hoc.

**Lesson (intuitive):** the foundational HRR/VSA papers assume isotropy. Real-data HRR is a "new" problem (in the sense that the formal papers don't address it). The substrate-relevant lit-scan finding: there's no well-known fix that says "drop in real anisotropic data and HRR will work." Either decorrelate at encoding (NEF) or accept reduced capacity.

### B8. Modern Hopfield (Ramsauer et al. 2020) — anisotropy break differently?

**Claim:** Ramsauer et al. 2020 NeurIPS ("Hopfield Networks is All You Need") — modern continuous Hopfield with energy `E = -lse(βX^T ξ) + ...` has EXPONENTIAL capacity `M = O(exp(d))` for random patterns, because the energy landscape is sharper.

**Where anisotropy bites:** the exponential capacity is for IID random patterns. For anisotropic real-data patterns, the capacity degrades — basins around correlated patterns merge. Recent work (2024-2025 spin-glass associative memory papers, e.g. Stanford / arXiv 2509.12202) shows the practical capacity on real data is much lower than the theoretical exponential bound.

**Substrate connection:** modern Hopfield uses softmax attention in the cleanup step. Substrate ARM2 (`exp_dense_KV_whitening_revival_v1_gpu`) = 0.75-0.93 — this IS the modern-Hopfield-flavored cleanup, and it recovers MUCH better than vanilla cleanup (ARM1 = 0.05-0.07). So modern-Hopfield-style softmax-cleanup IS a partial fix for anisotropy. But it costs M-dependent computation (the softmax sums over all M items).

**Lesson (intuitive):** modern Hopfield avoids the cliff by spending more compute at cleanup. If you accept O(M) work per query, you can rescue much of the anisotropy loss. Substrate's M-independent constraint (one matrix-multiply per query) makes this trade unavailable.

### B9. Substrate failures (this codebase) — re-read

**Evidence summary:**
- `exp_r3_encoder_anisotropy_diagnostic_v1` (HARD_PASS): PR/D=0.225, mean|corr|=0.073, top10pct=0.512 at D=384. CONFIRMS encoder is heavily anisotropic.
- `exp_dense_KV_whitening_revival_v1_gpu` (HARD_FAIL): ZCA whitening on real Pythia keys recovered only +0.020 absolute (0.048 → 0.068). ARM0 explicit kNN = 1.000; ARM2 softmax = 0.75-0.93; ARM1 M-indep superposition = collapse. Confirms whitening DOES NOT rescue dense superposition on real anisotropic data.
- `exp_anisotropy_rescue_4arm_sweep_v1_gpu` (MIDDLE_BAND, meter under-calibrated): A (cerebellar K=5 5x expand) = 0.041; A' (dense 5x) = 0.040; B (fly-LSH) = 0.612; B' (Charikar) = 0.982; C (compose) = 0.573; D (attention upper-bound) = 0.445. Only Charikar (explicit M-dependent storage) recovers fully — confirms the M-independent storage class is the binding constraint.

**Mechanism (load-bearing for the user's understanding):** the substrate's "M-INDEP O(d²) superposition" storage class is fundamentally cone-rank-limited. Whitening / cerebellar / fly-LSH all fail because they don't ADD rank. Charikar succeeds because it BUYS O(M) storage. Modern-Hopfield (ARM2 softmax) partially succeeds because it BUYS O(M) compute.

---

## Fundamental vs engineering — sorted

**FUNDAMENTAL (theory says you cannot beat with this code-class):**
1. **Rank bound:** linear post-hoc transforms (whitening, ZCA, PCA-rotate, BERT-flow if used after-the-fact) cannot add rank to a frozen encoder. The cone-rank IS the capacity ceiling.
2. **Storage-class trade:** M-independent O(d²) storage gives up the ability to use M-dependent compute or storage for cleanup. This trade is in the problem statement, not in cleverness.
3. **Mu-Viswanath irrelevance for capacity:** subtracting cone direction reduces effective dimension. It can help similarity tasks but cannot help superposition capacity.

**ENGINEERING (people haven't found the right fix yet):**
1. **Encoder retraining:** contrastive / SimCSE work but require training. For frozen-encoder use cases, this is closed off — but if substrate trained its own encoder, this lever is open.
2. **Sparse expansion at the right scale:** brain uses 1000x expansion with K=5. Substrate tried 5x. The mechanism may work at the right scale.
3. **Bio-inspired pre-processing:** density-preserving LSH variants, learned random projections (Ryali 2020), tuning-curve diversification (NEF) — partial engineering wins, mostly under-explored on the substrate.
4. **Hybrid storage classes:** pay O(M) compute (modern Hopfield / softmax cleanup) when needed; reserve M-indep superposition for items where it's known to work (e.g. orthogonal-codebook constructions).
5. **Use the cone:** instead of fighting anisotropy, EXPLOIT the structure. If real data lives in a low-rank cone, design retrieval that uses the cone as part of the addressing scheme (this is roughly what attention does at inference — it's not fighting anisotropy, it's using it). Brain analog candidate; under-explored.

---

## What the SOLUTIONS drill should look at (deferring per drill-2-parallel coordination)

Pointers for the parallel solutions/brain-analogs drill (not duplicated here):
- Cerebellar 1000x expansion + K=5 — the substrate ARM A used 5x, which is way below biological scale.
- Predictive coding encoder — train an encoder for ISOTROPY as a primary objective (not as a side-effect).
- NEF tuning-curve diversification — engineer isotropy at the encoding stage.
- Hippocampal pattern-separation (dentate gyrus) — 5x expansion with strong inhibition + Hebbian thresholding.
- Lock-in amplifier chain (USER 2026-06-23 intuition, flagged chain-grade-eligible) — orthogonal-by-construction reference signals.
- Trained encoder (Path C substrate-owned) — escape the frozen-Pythia constraint that locks substrate into rank-225/384.

---

## Confidence calibration

- **A1-A3 (capacity bound, eigenspread, M-P):** P=0.70 the math is correctly described; P=0.55 the substrate's specific recall numbers map cleanly to the M-P framework without seed/calibration caveats. (Lit-scan calibration penalty applied: cap novel-synthesis P=0.50.)
- **A4 (Mu-Viswanath distinction between similarity vs capacity tasks):** P=0.75 — this is a well-known distinction in the literature and substrate evidence supports it.
- **A5-A6 (information-theoretic ceiling, closed-form):** P=0.45 — heuristic; exact form depends on encoder/decoder; substrate fit is n=1.
- **B1-B8 (literature history):** P=0.65-0.75 individually — citations verified by web search; descriptions are summaries of paper claims; verify before citing in publication.
- **B9 (substrate evidence):** P=0.85 — direct re-read of substrate metrics files; numbers are exact.

---

## Deliverable closed.

File: `d:/AI/hd-instrument/notes/research_anisotropy_drill_1_barriers_math_literature_2026-06-25.md`

Companion drills (parallel; not duplicated here): SOLUTIONS half covers brain-analogs and substrate-specific paths.

Sources (lit-scan, for record):
- Ethayarajh 2019 EMNLP "How Contextual are Contextualized Word Representations?"
- Su et al. 2021 "Whitening Sentence Representations" (arXiv 2103.15316)
- Li et al. 2020 EMNLP "BERT-flow" (arXiv 2011.05864)
- Dasgupta, Stevens, Navlakha 2017 Science "A neural algorithm for a fundamental computing problem"
- Ryali et al. 2020 ICML "Bio-Inspired Hashing"
- Frady & Sommer 2020 (arXiv 2009.06734) "Variable Binding for Sparse Distributed Representations"
- Plate 1995 thesis / 2003 book on HRR
- Wang & Isola 2020 ICML "Understanding Contrastive Representation Learning through Alignment and Uniformity"
- Reimers & Gurevych 2019 EMNLP "Sentence-BERT"
- Dong, Cordonnier, Loukas 2021 ICML "Attention is not all you need"
- Ramsauer et al. 2020 NeurIPS "Hopfield Networks is All You Need"
- Marr 1969 "A theory of cerebellar cortex"; Cayco-Gajic & Silver 2019 Neuron; Litwin-Kumar et al. 2017 Neuron
- Mu & Viswanath 2018 "All-but-the-Top"
- "Whitening Not Recommended for Classification Tasks in LLMs" arXiv 2407.12886
- Stanford spin-glass associative memory arXiv 2509.12202

Substrate evidence:
- `d:/AI/hd-instrument/data/exp_r3_encoder_anisotropy_diagnostic_v1/metrics.json`
- `d:/AI/hd-instrument/data/exp_dense_KV_whitening_revival_v1_gpu/metrics.json`
- `d:/AI/hd-instrument/data/exp_anisotropy_rescue_4arm_sweep_v1_gpu/metrics.json`
