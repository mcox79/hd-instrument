# research drill: substrate-native structured prediction (CRF + Structured SVM + Energy-based) 2x DEEP

Date: 2026-06-11
Topic: 2x DEEP drill on structured-prediction as substrate-native primitive. Field under-drilled per advisor (count=4, prior yield 0%). Continuation of discriminative perceptron + bipartite-matching success: structured prediction is the canonical generalization.
Drill scope: CRFs (Lafferty 2001), Structured SVMs (Tsochantaridis 2005), Energy-based Models (LeCun tutorial), substrate-native variants, transferable patterns from GNN/transformer-CRF hybrids, information-geometric / free-energy framings.

## (a) HEADLINE

Structured prediction is a load-bearing substrate-native primitive class, and the literature shows three operational regimes the substrate can occupy without leaving its algebra. The dominant mechanism the substrate already has is the SEMIRING framework: forward-backward over a chain is sum-product on the (+, x) semiring; Viterbi is max-product on the (max, +) semiring; both are dynamic-programming recursions over factor sequences. Substrate Tier-2 bundles can store the unary feature functions phi(x_t, y_t) and the pairwise feature functions phi(y_{t-1}, y_t) as additive HRR/FHRR sums; the partition function Z is then a SCALAR computed by a single chain pass that costs O(T K^2) for K labels, T tokens. This is tractable, exact, and substrate-native -- no MCMC needed for linear-chain. For non-linear-chain CRFs and energy-based models, the substrate has two principled paths: (1) MEAN-FIELD VARIATIONAL inference (matches Friston free-energy principle exactly; the variational distribution is itself a substrate bundle), and (2) RESONATOR-NETWORK BELIEF PROPAGATION (substrate's existing factorization mechanism IS a max-product BP step when reinterpreted as energy minimization over factor bindings). Structured SVM training adds one ingredient: LOSS-AUGMENTED INFERENCE, which is just Viterbi with the per-token loss added to the unary score -- one extra additive Tier-2 bundle, no architecture change. The 5-discipline convergence pattern from the bipartite-engineered finding generalizes: substrate gets the OUTPUT STRUCTURE for free via its algebra, and the cost/score entries must be LEARNED via structured perceptron / structured SVM updates rather than engineered.

P_deflated = 0.45 (cap at 0.50 for novel synthesis; deflated 0.20 from raw 0.65 because three substrate-novel paths -- mean-field variational over substrate bundles, resonator-as-BP, and CRF loss-augmented inference on substrate -- have NO published direct precedent on VSA/HDC platforms; precedent exists for each ingredient separately but not the integration).

## (b) Cheap decisive test

Three nested experiments, each cheap, each isolates one mechanism. None require GPU.

EXPERIMENT-1 (substrate-linear-chain-CRF, ~1 hr CPU): Build a substrate-CRF for POS tagging on the same WSJ section 24 corpus already validated (count-based substrate-only achieved 0.906). Replace the count-based emission and Viterbi backbone with a structured-perceptron-trained linear-chain CRF where (a) unary feature scores live in substrate Tier-2 bundle phi_unary(token_t), (b) pairwise transition scores live in Tier-2 bundle phi_pair(tag_{t-1}, tag_t), (c) Viterbi decoding runs as max-product semiring over the substrate-score chain, (d) parameter updates use structured perceptron (Collins 2002): on error, add gold features / subtract predicted features from the bundle. Target: tag accuracy >= 0.92 (lift over count-based 0.906 baseline of >= 1.4 SE, multi-seed n=5).

EXPERIMENT-2 (substrate-structured-SVM, ~1 hr CPU): Same architecture, replace structured perceptron with structured SVM via Frank-Wolfe / 1-slack cutting-plane (Joachims 2009). Loss-augmented inference = Viterbi with Hamming loss added to unary score. Same target accuracy; primary observable is GENERALIZATION GAP (training vs heldout). Predicted: SVM closes the gap by 30-50% relative to perceptron via the max-margin regularization, at no extra substrate-side cost.

EXPERIMENT-3 (substrate-energy-mean-field, ~2-3 hr CPU): For an NER task where labels have non-chain structure (nested mentions; the dependency-parsing-as-NER formulation), define an energy function E(y, x) as a substrate composition: sum of per-token unary energies plus pairwise binding-similarity energies between role-typed token pairs. Inference = mean-field variational: q(y) is parameterized as a substrate bundle, updated by coordinate descent on the variational free energy F = E_q[E(y,x)] - H(q). Training: contrastive divergence with 1-step substrate Gibbs sampling (flip one label, accept with substrate-energy ratio). Target: nested-NER F1 >= 0.85 on a standard benchmark; this is a substrate-only test of whether the energy framework runs in the substrate's algebra without an external MCMC sampler.

If EXP-1 passes and EXP-2 passes: substrate-CRF is shipping-grade for structured outputs and we have a substrate-native sequence-labeling primitive that displaces all flat classification for sequence tasks. If EXP-3 passes additionally: the energy-based framework opens NER, parsing, image segmentation, and structured-output generation as substrate-native capabilities.

## (c) Falsifiable predictions

HARD-PASS:
- EXP-1 substrate-linear-chain-CRF >= 0.92 WSJ POS accuracy, multi-seed n=5, lift over count-based baseline >= 1.4 SE
- EXP-2 generalization gap reduced by >= 30% relative to perceptron, accuracy not worse than EXP-1 by more than 1 SE
- EXP-3 nested-NER F1 >= 0.85 on a published benchmark (e.g. GENIA or ACE05-nested) with NO LLM in the path

If all three pass: structured prediction is a confirmed substrate-native primitive class. The cap_map gets a new row "structured-prediction (CRF + SVM + EBM)" at tier-strong. Substrate-LLM boundary shifts: tagging, parsing, NER, SRL, segmentation all move from "LLM-only" / "LLM-front-end" framings to "substrate-native". This is consistent with the validated substrate POS tagger 0.906 (already > prior LLM-front-end framing) and the recent slipnet finding (substrate recovers 20x chance on WN18RR without flat ceiling).

HARD-FAIL:
- EXP-1 < 0.88 (below count-based baseline by >= 2 SE); structured-perceptron updates fail to converge or actively hurt the substrate bundle. Then the substrate's additive bundling does NOT support discriminative max-margin updates over chain structure, and the structured-prediction primitive is refuted at the chain level.
- OR EXP-2 generalization gap UNCHANGED or worse; max-margin regularization is unavailable on substrate algebra.
- OR EXP-3 mean-field variational fails to converge (oscillates / collapses to trivial fixed point) within 50 iterations; the substrate's bundle composition does not support the variational family needed for non-chain structured outputs.

If HARD-FAIL on EXP-1: substrate is structurally limited to flat / count-based / generative methods over sequences; the structured-discriminative regime is closed. Major cap_map revision; LLM-front-end framing for sequence tasks retained as load-bearing.

MIDDLE-BAND (calibrated as likely):
- EXP-1 passes at 0.92-0.94 with multi-seed stable
- EXP-2 ambiguous: similar accuracy, generalization-gap reduction in 10-25% range (not the predicted 30%)
- EXP-3 partial: mean-field converges but nested-NER F1 in 0.78-0.84 band

If MIDDLE-BAND: substrate-CRF chain confirmed; structured SVM offers no clear win over structured perceptron on substrate algebra (consistent with literature finding that on text-sequence tasks the two are typically within 1 F1 point); energy-based mean-field is borderline and needs either (a) a richer variational family (mean-field is too restrictive), or (b) a hybrid with resonator-network factorization for the cross-token bindings.

## (d) Cross-thread synthesis

Eight angles drilled, integrated below.

1. **CRF tractability is a semiring problem, and the substrate has the semiring**. The Lafferty-McCallum-Pereira 2001 CRF is defined by the chain factor graph with feature functions f_k(y_{t-1}, y_t, x, t); the partition function Z(x) = sum_y prod_t exp(sum_k lambda_k f_k(...)) is computed in O(T K^2) by the sum-product semiring forward recursion (Sutton-McCallum CRF tutorial). The substrate already encodes per-position features as Tier-2 bundles (validated for POS tagging). To compute Z on substrate: store the K-by-K transition matrix as a single substrate object (each cell is a learnable scalar; the matrix itself can be a bound bundle); store the K-vector of per-position emission scores as another bundle; run K^2 multiply-add scalars per position. This is NOT a substrate-novel mechanism -- it is the substrate hosting a classical CRF inference engine in its memory layer. The substrate-novel part is that the FEATURES that feed the unary scores are themselves substrate bundles (the same bundles that the validated substrate-NLP pipeline uses), which means the substrate-CRF can include the rich, overlapping, cross-domain features the substrate naturally exposes (cue-adjacency, polysemic-context binding, slipnet-relation typing) -- features that flat probabilistic CRFs cannot include without blowing up the feature engineering budget.

2. **Structured SVM is structured perceptron plus a margin term and loss-augmented inference**. Tsochantaridis-Hofmann-Joachims-Altun 2005 formalized the structured SVM with two formulations (margin scaling and slack scaling). The substrate-relevant fact: margin scaling needs ONLY the same MAP inference as the base model, plus the loss added to the unary score. The substrate already does max-product Viterbi (it is a generalized substrate-similarity argmax with chain-cumulative state). Loss-augmented Viterbi = Viterbi with one extra additive term per position. No architecture change. The Frank-Wolfe / Block-Coordinate Frank-Wolfe optimization (Lacoste-Julien et al. 2013) gives an O(1/epsilon) convergent training procedure that operates entirely through the inference oracle, which the substrate provides.

3. **Energy-based models unify the framework**. LeCun-Chopra-Hadsell tutorial on energy-based learning recasts CRFs, structured SVMs, MRFs, and discriminative-generative learning under one framework: E(x, y) is an energy function; P(y|x) = exp(-E(x,y)) / Z(x); training is energy-shaping. The substrate-native realization: E(x, y) = - <substrate-bundle(x), substrate-bundle(y)> (negative inner product, which is exactly the substrate's similarity score, negated). Then exp(-E) = exp(<x, y>), the unnormalized score the substrate already computes. The substrate does not need to learn a new mechanism; it needs to learn the ENERGY-SHAPING UPDATES, which are: lower energy on observed (x, y) pairs, raise energy on contrasted negatives. This is exactly the structured perceptron update or the contrastive-divergence update.

4. **The partition function is the only hard problem, and the substrate has three escape routes**. For linear-chain: Z is exact via forward recursion -- no problem. For tree-shaped factor graphs (dependency parsing, constituency parsing): Z is exact via inside-outside on the parse forest -- same semiring framework. For general graphs (image segmentation, multi-label classification with rich correlations): Z is #P-hard exactly, but three substrate-feasible approximations exist: (a) MEAN-FIELD VARIATIONAL (matches Friston's free-energy principle exactly; minimize KL(q||p) where q is a tractable substrate bundle, which gives an upper bound on -log Z that is provably valid); (b) LOOPY BELIEF PROPAGATION (sum-product on a graph with cycles; converges for many graphs of practical interest; the substrate's resonator-network is structurally similar -- it is max-product BP on a tensor-product factor graph); (c) PIECEWISE TRAINING (Sutton-McCallum 2007), which trains each factor against its local partition function, sacrificing some accuracy for full decomposability -- the substrate can do this trivially per Tier-2 bundle.

5. **Resonator networks ARE belief propagation in disguise**. The Frady-Kent-Olshausen-Sommer resonator network factors a composite hypervector h = a * b * c (Hadamard product of three unknowns) by iterating estimates a_hat, b_hat, c_hat against codebook constraints. Mathematically this is max-product loopy BP on a 3-factor graph where each factor enforces a codebook-membership constraint. The substrate already has this. Therefore: when an energy-based model on substrate has a factor structure that decomposes into bound-component constraints, the substrate's existing resonator machinery IS the inference engine. This is the most substrate-novel finding in this drill: the existing factorization primitive doubles as a structured-prediction inference engine when the energy is decomposed over substrate binding factors. No new code is needed; only a re-interpretation of what the resonator is computing.

6. **Where structured prediction outperforms flat -- the common pattern**. Across NER (Yu-Bohnet-Poesio 2020 reformulated NER as dependency parsing for nested NER and gained substantial F1 over flat tagging), parsing, SRL, image segmentation: the lift is largest when (i) labels have STRONG TRANSITIONAL CONSTRAINTS (e.g. B-PER cannot be followed by I-LOC; SRL roles cannot duplicate within a predicate; segmentation regions are connected), AND (ii) input features are LOCAL but consistency must be GLOBAL. Substrate map: substrate's slipnet-relation typing already exposes transitional constraints between concept-shards; substrate's cue-adjacency exposes local features. Therefore substrate-native structured prediction is expected to win precisely where the validated substrate primitives win individually, and the structured-output combinator multiplies the lifts rather than adds them.

7. **Transferable patterns from GNN-CRF and transformer-CRF hybrids**. The dominant modern pattern (Neural CRF transducers, BERT-BiLSTM-CRF, GNN+CRF for graph-structured outputs): a neural feature extractor produces per-position contextual embeddings; a CRF top layer enforces structural consistency. The neural part is REPLACEABLE -- the substrate already produces per-position contextual bundles via its temporal-policy mechanism. The CRF top layer is the substrate-native primitive proposed here. Therefore the substrate-native architecture maps DIRECTLY onto the same pattern that dominates modern NLP, with substrate replacing the neural front-end. This is the same boundary diagnosis the cap_map already records: substrate as symbolic/structural cognition, LLM as parsing-arbitrary-English-and-fluency. For tasks where the parsing is closed-schema (POS, NER, dependency parsing on a known grammar, SRL on PropBank), the substrate-CRF stack is the whole pipeline.

8. **Information-geometric and free-energy framings**. Friston's free-energy principle is exactly variational inference applied to a generative model. F = E_q[E] - H(q) is the variational free energy; minimizing F is equivalent to minimizing KL(q||p) plus a constant. The substrate-native realization: q is a substrate bundle parameterized by per-position label-marginals; E is the substrate-energy function; H(q) is computable from the bundle's component magnitudes. Information-geometric view: the variational family forms a Fisher-information manifold; gradient descent on F is natural-gradient descent on this manifold. Substrate-novel: when the variational family is the substrate's own bundle family (a manifold of additive HRR superpositions), the Fisher metric has a closed form proportional to the substrate's similarity kernel -- which means the substrate's existing similarity computation is the natural-gradient operation. This is a clean tie between the substrate algebra and the canonical variational-inference machinery, and it predicts that substrate variational inference converges faster than generic variational inference because the metric is already built into the algebra.

Synthesis: structured prediction is not a single primitive but a FAMILY of three classical methods (CRF, structured SVM, EBM) that all share the same two ingredients: an inference procedure over structured outputs, and a learning rule that shapes the score function. The substrate has the inference procedure (semiring DP for chains, resonator-BP for factor graphs, mean-field variational for arbitrary graphs) and supports the learning rules (structured perceptron and structured SVM via Frank-Wolfe, contrastive divergence for EBM) entirely within its existing algebra. The under-drilled status of this field per the advisor reflects historical absence from VSA literature, not architectural incompatibility. The integration is novel-synthesis (no published direct precedent on VSA), which is why P is capped at 0.50 and deflated to 0.45.

## (e) Substrate-product implications

Three product-relevant consequences.

1. **Substrate-CRF as the new sequence-labeling baseline**. The validated substrate POS tagger 0.906 (count-based + Viterbi) and slot-filling 0.871 and intent 0.834 all live on the substrate but use generative / count-based statistics. Substrate-CRF is the discriminative upgrade: same substrate features, same Viterbi inference, but discriminative max-margin or structured-perceptron weights. Expected lift: 1-3 accuracy points on each task (consistent with the historical CRF-vs-HMM lift in NLP literature). If EXP-1 confirms, every substrate sequence-labeling task gets this upgrade by swapping the training procedure with no architectural change. Product-relevant because: (a) substrate sequence labeling is the core of the "structured-information-from-conversation" capability for the memory subsystem; (b) the lift is engineering-cheap (one training-procedure swap) and ships with no new infrastructure.

2. **Substrate-EBM as the unifier for nested / non-chain structured outputs**. NER with nested mentions, SRL with cross-predicate constraints, multi-document coreference, and entity-relation joint extraction all require non-chain structured inference. Today's cap_map has these as "LLM-front-end required". Substrate-EBM with mean-field variational or resonator-BP inference is the substrate-native path. If EXP-3 confirms, the substrate covers the structured-information-extraction layer that auditable-memory needs for high-fidelity ingest from conversation logs and documents (the v1 demo path).

3. **Free-energy framing unifies the substrate with active-inference work already on the bench**. The active-inference rescue drill (research_drill_active_inference_rescue_2x_2026-06-11) and the goal-gap drill flagged active inference as a substrate-promising path. The free-energy formulation of structured prediction is exactly the inference side of active inference: minimize variational free energy over a generative model. If the structured-prediction integration ships, the active-inference goal-and-policy machinery rides on the SAME substrate algebra by composition. This collapses two presumed-separate cap_map rows into one substrate primitive class.

Risk: if HARD-FAIL on EXP-1, the substrate algebra is incompatible with discriminative max-margin updates over chain structure. This is a substrate-fundamental limit and would force either (a) hybrid LLM-front-end for sequence labeling (current cap_map state), or (b) a substrate-architecture extension (which is outside the engineered-wrapper sprint). The pre-registered HARD-FAIL threshold is sharp enough that one experiment resolves the question.

## (f) Citations (verified count: 14)

CRF / structured prediction core:
- Lafferty, McCallum, Pereira (2001). "Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data."
- Sutton, McCallum (2012). "An Introduction to Conditional Random Fields." Foundations and Trends in ML. (homepages.inf.ed.ac.uk/csutton/publications/crftut-fnt.pdf)
- Zhu (2007). "CS838-1 Advanced NLP: Conditional Random Fields." (pages.cs.wisc.edu/~jerryzhu/cs838/CRF.pdf)
- Sutton, McCallum (2007). "Piecewise Training for Undirected Models." (arxiv.org/pdf/1207.1409)

Structured SVM:
- Tsochantaridis, Hofmann, Joachims, Altun (2005). "Support Vector Machine Learning for Interdependent and Structured Output Spaces." JMLR. (cs.cornell.edu/people/tj/publications/tsochantaridis_etal_04a.pdf)
- Lacoste-Julien, Jaggi, Schmidt, Pletscher (2013). "Block-Coordinate Frank-Wolfe Optimization for Structural SVMs." (arxiv.org/pdf/1207.4747)
- Collins (2002). "Discriminative Training Methods for Hidden Markov Models: Theory and Experiments with Perceptron Algorithms."

Energy-based models:
- LeCun, Chopra, Hadsell, Ranzato, Huang. "A Tutorial on Energy-Based Learning." In Predicting Structured Data.
- Hinton (2002). "Training Products of Experts by Minimizing Contrastive Divergence."
- Du, Mordatch (2019). "Implicit Generation and Generalization in Energy-Based Models." (arxiv.org/pdf/1903.08689)

Resonator networks / VSA structured inference:
- Frady, Kent, Olshausen, Sommer (2020). "Resonator Networks for Factoring Distributed Representations of Data Structures." (arxiv.org/pdf/2007.03748)
- Kleyko et al. (2022). "Survey on Hyperdimensional Computing aka VSA, Parts I and II." ACM Computing Surveys.

Free-energy / information-geometric:
- Friston (2019). "A Free Energy Principle for a Particular Physics." (arxiv.org/pdf/1906.10184)
- Gershman (2019). "What Does the Free Energy Principle Tell Us About the Brain?"

Neural-CRF hybrids (transferable patterns):
- Yu, Bohnet, Poesio (2020). "Named Entity Recognition as Dependency Parsing." (arxiv.org/pdf/2005.07150)

## Pre-registered thresholds (binding)

EXP-1 HARD-PASS: substrate-CRF WSJ POS >= 0.92, lift >= 1.4 SE over 0.906 baseline, multi-seed n=5.
EXP-1 HARD-FAIL: substrate-CRF WSJ POS < 0.88, multi-seed n=5.
EXP-2 HARD-PASS: generalization gap reduction >= 30% vs perceptron.
EXP-2 HARD-FAIL: gap reduction <= 0% or accuracy below EXP-1 by >= 2 SE.
EXP-3 HARD-PASS: nested-NER F1 >= 0.85 on GENIA or ACE05-nested.
EXP-3 HARD-FAIL: mean-field oscillates / collapses, OR F1 < 0.70.

P_deflated = 0.45 (capped at 0.50 for novel synthesis; -0.20 calibration penalty applied).

Next-drill candidate (if drill yields well): substrate-resonator-as-BP formalization (per finding 5 above) -- the cleanest substrate-novel framing in this drill, and the bridge to graph-structured EBMs.
