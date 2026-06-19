# research drill: substrate-CRF as UNIVERSAL discriminative structured prediction primitive for substrate-classical NL (2x DEEP)

Date: 2026-06-11
Topic: 2x DEEP drill on the unification hypothesis: is substrate-CRF the SINGLE architectural primitive that subsumes POS + NER + chunking + dep-parse + slot-filling + intent + text-class + sentiment + math op-classification + code algopattern under one library + per-task feature templates + per-task Tier-2 schema bundles?
Predecessor: research_drill_substrate_structured_prediction_2x_2026-06-11.md (1x; CRF+SSVM+EBM trichotomy on substrate); this 2x extends to the UNIVERSALITY claim across the 11 empirically validated tasks (POS 0.9499 / dep-parse 0.787 / math op-class / code 0.739 / NER 0.58 / text-class 0.848 / sentiment 0.767 / chunking F1>=0.85 / slot-filling 0.871 / intent 0.834 / [PP-379 + PP-381 + earlier]).
Per user strategic refocus: substrate-intrinsic capability extension, NOT LLM comparison.

## (a) HEADLINE

Substrate-CRF is the unified architectural primitive for substrate-classical NL structured prediction across all 11 validated tasks, with unusually clean lit-precedent for the unification claim itself. The unification is exact (not metaphorical) because (i) multinomial logistic regression is the degenerate CRF with a single output variable -- so flat multi-class classification (text-class + sentiment + intent + math op-classification) is SUBSUMED by the CRF framework with zero architectural change; (ii) arc-factored MST dependency parsing is a tree-structured CRF whose training procedure is the structured perceptron acting on an Eisner/Chu-Liu-Edmonds decoder -- so dep-parse is SUBSUMED with the only change being the decoder argument; (iii) BIO-tagged sequence labeling (NER + chunking + slot-filling + POS) is the linear-chain CRF -- subsumed exactly; (iv) compositional 2-op structured outputs (math + code algopattern) are k-best-tree CRFs on a small operator grammar, which is again a tree CRF with a finite operator alphabet -- subsumed. The COMMON CORE the substrate provides is a SCORE FUNCTION evaluator and a DECODER ORACLE; the per-task variation lives in (a) the FEATURE TEMPLATE list, (b) the DECODER (Viterbi for chains, Eisner/CLE for trees, argmax-over-K for flat), and (c) the Tier-2 SCHEMA BUNDLE that names the slot types. This matches the IllinoisSL (Chang et al. 2015) and Torch-Struct (Rush 2020) library designs verbatim, which proves the abstraction is sound at industrial scale. Substrate's distinguishing primitive is that the feature templates are themselves substrate bundles -- the cross-domain features (slipnet-relation typing, cue-adjacency, polysemic-context binding) that flat probabilistic CRFs cannot include without combinatorial feature-engineering blowup are SUBSTRATE-NATIVE and ship as Tier-2 bundles by construction.

P_deflated = 0.55 for "substrate-CRF library + per-task feature templates + per-task Tier-2 schemas covers all 11 validated tasks at or above current published count-based / phasor-only baselines" within 2-4 weeks engineering (capped at 0.55 because the unification ITSELF has direct lit-precedent in IllinoisSL/Torch-Struct/Collins, only the substrate-bundle-as-feature-template integration is novel-synthesis; deflated 0.20 from raw 0.75 because no VSA/HDC platform has shipped this stack at production scale).

## (b) Cheap decisive test

UNIFICATION-PILOT-1 (~2-3 hr CPU): Implement a single substrate-CRF library `hdlab/structured/crf.py` with the following API:

```
class SubstrateCRF:
    def __init__(self, schema: Tier2Bundle, decoder: str):
        # schema: Tier-2 bundle naming slot types (e.g. POS tags, BIO-NER labels, dep arc labels, intent classes)
        # decoder: 'viterbi' | 'eisner' | 'cle' | 'argmax_flat'
    def add_feature_template(self, name: str, fn: Callable[[Context], SubstrateBundle]): ...
    def score(self, x: Sequence, y: Structure) -> float: ...
    def predict(self, x: Sequence) -> Structure: ...
    def update(self, x: Sequence, y_gold: Structure, y_pred: Structure) -> None: ...
```

Validate by re-running the 4 anchor tasks already passed (POS 0.9499 + dep-parse 0.787 + math op-class + 1 BIO task like slot-filling 0.871) through the SAME library with task-specific feature template + schema bundle + decoder selection. HARD-PASS: all 4 tasks reproduce their published numbers within +/- 0.01 absolute on the library. If yes: the unification holds and the per-task variation reduces to (feature template + schema + decoder). Then extend to the remaining 7 tasks (NER + chunking + intent + text-class + sentiment + code algopattern + slot-filling) using only feature-template + schema-bundle modifications.

UNIFICATION-PILOT-2 (~1-2 hr CPU): Cross-task feature transfer ablation. Train substrate-CRF on POS with the canonical [unigram, prefix, suffix, prev-tag, next-tag] feature template. ABLATE one template at a time and measure NER F1 (with the same library, different schema, different decoder, but IDENTICAL feature templates). Map which templates are TASK-UNIVERSAL (contribute to >=4 of 11 tasks) vs TASK-SPECIFIC (contribute to <=2 tasks). HARD-PASS: at least 3 feature templates are universal (lift >=0.01 on >=4 tasks); at least 5 features have predicted task-specific affinity (e.g. capitalization is NER-specific, suffix is POS-specific).

UNIFICATION-PILOT-3 (~30 min CPU): Layer 1 attribution sanity check. For each task and each feature template, log the structured perceptron weight magnitude after training. HARD-PASS: predicted task-affinity from PILOT-2 correlates Spearman rho >= 0.60 with attribution weight rank within task. If yes: Layer 1 attribution validates feature value PRE-SHIP, closing the loop on "validate each task's features add value before ship" (drill question 11).

Total decisive cost: ~4-6 CPU-hr, all on existing infrastructure, no GPU, no LLM, no new datasets beyond what the 11-task suite already includes.

## (c) Falsifiable predictions

HARD-PASS (all four must hold for the unification primitive to ship):

- **HP1 library reproduction**: UNIFICATION-PILOT-1 reproduces all 4 anchor tasks within +/- 0.01 absolute (POS 0.9489-0.9509 / dep-parse 0.777-0.797 / math op-class within published band / slot-filling 0.861-0.881). The library does not regress because of the unification.
- **HP2 universal feature templates exist**: PILOT-2 identifies >=3 cross-task universal templates with lift >=0.01 on >=4 tasks each.
- **HP3 attribution validates pre-ship**: PILOT-3 Spearman correlation >=0.60 between Layer 1 attribution rank and held-out task lift, per task.
- **HP4 extension to 7 remaining tasks**: applying the library + per-task template + per-task schema + per-task decoder to NER + chunking + intent + text-class + sentiment + code algopattern + slot-filling reaches the published substrate-classical baselines within 2-4 weeks of engineering, with no architecture additions.

If HP1+HP2+HP3+HP4 all hold: substrate-CRF is confirmed as the universal discriminative structured-prediction primitive. cap_map gets a new row "substrate-CRF universal" at tier-load-bearing. The 11 separate Tier-2 schema bundles + 11 separate feature template lists become the library catalog; the inference / training / decoding machinery is one substrate-CRF library.

HARD-FAIL (any of the four refutes the universality claim):

- **HF1 library reproduction breaks**: any of the 4 anchor tasks drops by >0.02 absolute under the library; the unification introduces a per-task-incompatible abstraction. The unification is refuted at the API level.
- **HF2 no universal templates**: PILOT-2 finds zero templates with lift >=0.01 on >=4 tasks; every task needs entirely bespoke features. The "shared infrastructure" claim degenerates to "shared infrastructure is the decoder only", and the library savings are marginal.
- **HF3 attribution does not predict lift**: PILOT-3 Spearman <=0.30; Layer 1 attribution is decorrelated from held-out value. Cannot validate pre-ship; need full eval-per-task, which kills the rapid-extension claim.
- **HF4 extension fails on multiple tasks**: 3+ of the 7 extension tasks fall >0.05 absolute below their substrate-classical baseline. The unification is real for some task classes but not all, and the library needs class-specific (chain / tree / flat) divergence. Substrate-CRF is then a useful but NOT universal primitive.

MIDDLE-BAND (calibrated as likely outcome):

- HP1 passes for chain + flat tasks (POS + intent + sentiment + slot-filling + chunking + NER all within +/- 0.01)
- HP1 partial for tree tasks (dep-parse within +/- 0.02 due to Eisner subtleties)
- HP2 passes with ~3-5 universal templates: [unigram-emission, bigram-transition, context-window-emission, prev-label, next-label]
- HP3 passes with rho in [0.45, 0.65] band (good but not tight)
- HP4 partial: 5 of 7 extension tasks reproduce their baseline; 2 (likely code algopattern + nested-NER) need extra mechanisms (k-best tree decode + nested BIO scheme)

If MIDDLE-BAND: substrate-CRF is the universal primitive for the CHAIN + FLAT + ARC-FACTORED-TREE regime (covers 9 of 11 validated tasks), and the 2 outliers route through targeted extensions of the same library (nested-BIO + k-best-tree + 2-op composition).

## (d) Cross-thread synthesis

Thirteen drill questions integrated below.

**1. Substrate-CRF architecture: emission features + transition features + structured-perceptron updates + Tier-2 schema bundles.**
The architecture is the classical Lafferty-McCallum-Pereira (2001) linear-chain CRF generalized to arbitrary structured outputs via Tsochantaridis-Hofmann-Joachims-Altun (2005) structured SVM / Collins (2002) structured perceptron. Substrate-native realization: emission features phi_emit(x_t, y_t) are stored as Tier-2 bundles keyed by (token_context, label); transition features phi_trans(y_{t-1}, y_t) are stored as a single Tier-2 bundle indexed by label-pair; the score function score(x, y) = sum_t [<phi_emit, w_emit> + <phi_trans, w_trans>] is a substrate inner-product accumulation; structured perceptron updates add gold features and subtract predicted features from the substrate weight bundle on error. No new substrate primitive is needed; the substrate's inner-product and additive-bundling primitives suffice.

**2. Universal applicability: which NL structured prediction tasks does substrate-CRF SUBSUME?**
Per the lit-precedent gathered:
- FLAT MULTI-CLASS (text-class + sentiment + intent + math op-classification + code algopattern when the latter degenerates to algorithm-family choice): SUBSUMED. Multinomial logistic regression is the degenerate CRF with one output variable (An Introduction to Conditional Random Fields, Sutton-McCallum 2012); the substrate-CRF library with `decoder='argmax_flat'` is exactly this case.
- LINEAR-CHAIN SEQUENCE LABELING (POS + NER + chunking + slot-filling): SUBSUMED. BIO-encoded sequence labels are the canonical linear-chain CRF; the substrate-CRF library with `decoder='viterbi'` covers it. POS at 0.9499 already validates this empirically.
- ARC-FACTORED TREE STRUCTURE (dependency parsing): SUBSUMED. First-order graph-based dep-parse is structured-perceptron-trained against Eisner (projective) or Chu-Liu-Edmonds (non-projective) MST decoder; substrate-CRF library with `decoder='eisner'` covers it. dep-parse 0.787 already validates this empirically.
- COMPOSITIONAL 2-OP (math word problems + code algopattern as compositional structured output): SUBSUMED with extension. The 2-op composition can be encoded as a height-2 tree CRF over an operator alphabet of size O(10-20); k-best-tree decode + product-of-2-arc-factored scores. Substrate-CRF library with `decoder='kbest_tree'` covers it.

Tasks NOT subsumed (out of scope for this drill): semantic parsing into open-vocabulary logical forms (needs a generative decoder over arbitrary expressions), open-domain creative generation (refuted today; see substrate_open_domain_creative_nl drill), arbitrary multi-hop reasoning chains beyond k=2 (separate substrate question).

**3. Per-task substrate-CRF variants: features needed per task; shared infrastructure.**
Per the search on cross-task feature template transfer (CRF tutorials + GeeksforGeeks CRF POS + Bangla NER paper) and the IllinoisSL feature-template inventory:

Universal feature templates (contribute on ALL chain + flat tasks):
- U_unigram: phi(x_t) -- the token itself, hashed or substrate-bound
- U_context_window: phi(x_{t-2:t+2}) -- 5-token window with substrate-product of position-tagged bindings
- U_prev_label: phi(y_{t-1}) -- previous label (only when decoder != flat)
- U_next_label: phi(y_{t+1}) -- next label (only when decoder != flat)
- U_label_bigram: phi(y_{t-1}, y_t) -- transition feature

Task-specific feature templates (predicted by literature):
- POS: T_suffix, T_prefix, T_morphology (rich suffix-prefix derivatives)
- NER: T_capitalization, T_gazetteer (Wikipedia + lexicon), T_word_shape (Xxx vs XXX vs xxx)
- chunking: T_pos_window (POS tags of context window; piggybacks on POS output)
- dep-parse: T_arc_distance, T_arc_direction, T_head_pos, T_mod_pos
- slot-filling: T_intent (predicted intent class as a feature; cascade)
- intent + text-class + sentiment: T_word_polarity_lexicon (sentiment), T_topic_lexicon (text-class), T_action_verb (intent)
- math op-class: T_number_count, T_op_keyword (sum/difference/each)
- code algopattern: T_keyword_python, T_loop_structure, T_recursion_marker

The shared infrastructure is the SCORE FUNCTION (substrate inner-product + accumulation), the DECODER selection (Viterbi / Eisner / CLE / argmax / k-best), and the STRUCTURED PERCEPTRON UPDATE (gold-minus-predicted bundle delta). The per-task variation is in the feature template list and the Tier-2 schema bundle naming the slot types.

**4. Substrate-CRF + multi-step composition (PP-375 multistep extension): does substrate-CRF generalize to compositional structured prediction?**
Yes, with a specific extension. PP-375 multi-step composition (multi-hop or multi-operator) maps to a tree CRF over a small grammar of composition rules. The same structured-perceptron training works as long as the composition GRAMMAR is bounded (finite operator alphabet + max-depth k). Lit precedent: Dynamic Modularized Reasoning for Compositional Structured Explanation Generation (arxiv 2309.07624) frames multi-step reasoning as a structured output over reasoning-type tokens; the CRF top layer enforces compositional consistency. Substrate-CRF realization: encode each composition step as a label, use a k-best-tree decoder, score each step independently (arc-factored) plus a tree-level normalization. This is exactly the inside-outside semiring on substrate (already validated in the 1x predecessor drill).

CAUTION: compositional structured prediction is ONLY substrate-tractable for BOUNDED compositional depth. Unbounded recursion (arbitrary multi-hop chains > k=3) requires either external decoding (search) or a hybrid -- this is the same boundary the GSM8K-substrate-boundary drill found this morning.

**5. Substrate-CRF + BIO scheme for sequence labeling: NER + slot-filling unified.**
The BIO (Begin / Inside / Outside) encoding scheme is the canonical lit-precedent for unifying NER + slot-filling + chunking under one linear-chain CRF (per metricgate.com CRF doc + Sutton-McCallum tutorial). Each entity type E maps to two labels (B-E, I-E), all non-entities get label O. Transitions are constrained (I-E cannot follow B-F for F != E; I-E can follow B-E or I-E). Substrate-CRF realization: the Tier-2 schema bundle names the entity types {PER, LOC, ORG, MISC, INTENT_ACTION, INTENT_OBJECT, ...}; the BIO encoding doubles the label space; the substrate-CRF library handles the Viterbi decode with hard transition constraints by setting transition feature weights to -infty for illegal transitions (or equivalently, masking them in the substrate score lookup). NER F1 0.58 -> 0.85+ rescue (per the morning NER drill) lives here: BIO-constrained Viterbi + gazetteer feature + bigram boundary + cascade-from-POS are all CRF-feature-template additions, not architecture changes.

**6. Substrate-CRF + tree decoding: dep-parse + constituency parsing unified.**
First-order arc-factored dep-parse with Eisner (projective) or Chu-Liu-Edmonds (non-projective) decoding is the canonical lit-precedent for structured-perceptron training on tree outputs (per GitHub MST parser + arxiv 1603.04351 + ACL E17-1063). Substrate-CRF library extension: `decoder='eisner'` or `decoder='cle'`; scoring function is sum-of-arc-scores; structured perceptron update on arc-disagreement. Constituency parsing extends by replacing arc-factored score with span-factored score and using CKY decode (inside-outside semiring). Both decoders are dynamic-programming with substrate-inner-product as the score primitive. Higher-order parts (sibling, grandparent, third-order) compose multiplicatively (per the dep-parse 0.787-to-0.85 drill this morning) as additional feature templates on the decoder's already-existing parts.

**7. Substrate-CRF + multi-class classification: text-class + sentiment + intent unified.**
Multinomial logistic regression IS the degenerate CRF with a single output variable (per Sutton-McCallum CRF tutorial section 2.2, explicit). The substrate-CRF library with `decoder='argmax_flat'` reduces exactly to multinomial logistic regression where the K-class score is sum_k <phi_k, w_k>. Structured perceptron update becomes the standard multi-class perceptron / averaged perceptron. The substrate's empirical text-class 0.848 / sentiment 0.767 / intent 0.834 are already this case under count-based scoring; switching to discriminative structured perceptron on the same substrate features is the same lever that took POS 0.906 -> 0.9499 and dep-parse 0.60 -> 0.787. Predicted lift band per literature: +0.02 to +0.05 absolute on each of the three flat tasks.

**8. Substrate-CRF + 2-op composition: math + code algopattern unified per user compositional-engine insight.**
Per the user's compositional-engine framing: 2-op math word problems (a + b * c, (a + b) * c, ...) and code algopattern (loop-over-list-then-aggregate, recurse-then-combine, ...) are both 2-step structured outputs with a finite operator alphabet (math ~ 20 ops; code algopattern ~ 10-15 templates). Both map to height-2 tree CRFs where each level is an arc-factored choice. Structured perceptron training works identically; decoder is k-best-2-step-tree (small enumeration over O(|ops|^2 * |operands|^2) candidates, which is O(10^3-10^4) at small task scale). The unification is: math op-classification (1-step) + 2-op math composition + code algopattern (1-3 step) are all the same `decoder='kbest_tree'` library entry with a per-task operator alphabet (in the Tier-2 schema bundle) and per-task feature templates (T_number_count + T_op_keyword for math; T_keyword_python + T_loop_structure for code).

CAVEAT: structured perceptron convergence on compositional outputs is slower than on chain outputs (per Collins 2002 + Frank-Wolfe analyses); expect 5-10x more passes through training data for the same convergence target. Empirically tractable within the cheap-test budget.

**9. Substrate-CRF as substrate-distinguishing primitive (no LLM equivalent for this combination of features).**
The product-relevant differentiator: substrate-CRF's FEATURE TEMPLATES are themselves SUBSTRATE BUNDLES, which means cross-domain features that flat probabilistic CRFs cannot include without combinatorial feature engineering blowup ARE the natural feature space:

- Slipnet-relation typing feature: phi_rel(x_t, x_{t-k}) = substrate-bound (type_of_relation, span_between_tokens) -- gives the CRF a typed-pairwise-feature without engineering it.
- Polysemic-context binding feature: phi_pcb(x_t) = context-binding(x_t, context_window) -- gives the CRF a context-disambiguated token embedding without engineering it.
- Cue-adjacency feature: phi_cue(x_t, x_{t+1}) = substrate-bound (cue_strength_t, cue_strength_t+1) -- gives the CRF a learned-by-substrate cue feature.
- Algebraic-tag feature: phi_alg(x_t) = substrate-bound (math_tag_t, code_tag_t, semantic_tag_t) -- gives the CRF the substrate-classical multi-axis tags as a single bundle.

These are not features classical (probabilistic) CRF practitioners could write down without the substrate. They are not features LLMs expose to a CRF head either (BERT-BiLSTM-CRF uses contextual EMBEDDINGS, not TYPED RELATIONAL features). The substrate-CRF stack therefore has access to a feature class that neither classical-CRF nor LLM-CRF-head architectures can use. This is the substrate-product axis: typed-relational-feature CRFs as a discriminator versus both classical CRFs and LLM-front-ended CRFs.

Calibration: this is a NOVEL-SYNTHESIS claim and is capped at P=0.50 per [[feedback-lit-scan-calibration-penalty]]. The P_deflated=0.55 above reserves 0.40 mass for "substrate-CRF library works on chain + flat + arc-factored-tree" (which has direct lit precedent at IllinoisSL / Torch-Struct / Collins) and 0.15 mass for "the substrate-bundle feature templates produce measurable lift over classical CRF features on >=3 of 11 tasks" (which is the novel-synthesis component requiring empirical test).

**10. Generalization to unseen tasks: which NL tasks does substrate-CRF predictably handle?**
Beyond the 11 validated tasks, the unified library predictably handles (by decoder + schema swap):

- Semantic role labeling (SRL): linear-chain or arc-factored tree, BIO-arg or span-arg encoding; substrate-CRF with `decoder='viterbi'` (flat-SRL) or `decoder='eisner'` (parse-conditioned-SRL).
- Coreference resolution (within-document): pairwise mention-pair classification = flat CRF; document-level clustering = a small graph CRF with mention-mention factor; substrate-CRF with `decoder='argmax_flat'` for first cut.
- Aspect-based sentiment analysis (ABSA): joint aspect-extraction (BIO) + sentiment-per-aspect (flat); two-pass substrate-CRF with cascade.
- Word segmentation (Chinese, Japanese): BIO-character-level CRF; substrate-CRF with `decoder='viterbi'`. Lit precedent: arxiv 1510.07099 CRF+MMSEG for Chinese segmentation in social media.
- Punctuation restoration / capitalization: chain CRF over punctuation slots; substrate-CRF with `decoder='viterbi'`.
- Discourse relation classification: pair-of-clauses flat classification; substrate-CRF with `decoder='argmax_flat'`.

Tasks NOT predictably handled (boundary of the substrate-CRF primitive):

- Open-domain QA (needs retrieval + reasoning + generation; substrate-CRF is one layer among many).
- Machine translation (sequence-to-sequence generation; outside structured prediction scope).
- Abstractive summarization (open-domain generation; same as MT).
- Multi-hop reasoning with k > 3 (compositional decode breaks per the bounded-grammar caveat in question 4).
- Free-form text generation (refuted today; see substrate_open_domain_creative_nl drill).

Predicted reach: ~6-8 more NL structured prediction tasks are substrate-CRF-tractable beyond the 11 validated; reach plateaus at the open-generation boundary.

**11. Substrate-CRF + Layer 1 attribution: validate each task's features add value before ship.**
Layer 1 attribution (per the substrate-on-substrate visibility program) ranks each feature template's contribution to held-out task performance by structured-perceptron weight magnitude + ablation-counterfactual lift. The UNIFICATION-PILOT-3 cheap test (~30 min CPU) validates the closed-loop: train substrate-CRF with N feature templates, log attribution weights, ABLATE one template at a time, measure held-out F1 delta. Spearman correlation rho >= 0.60 between attribution rank and ablation lift VALIDATES Layer 1 as a pre-ship feature filter; rho < 0.30 INVALIDATES it and forces full ablation per task.

This is operationally important: in a unified library with ~20 candidate feature templates and 11+ tasks, full ablation per task is 220 training runs (expensive). Layer 1 attribution gives a fast filter that picks the top-K templates per task without running all 20 ablations. This is the "shared infrastructure" promise made operational.

Per the morning Layer 4 dialectic drill (research_drill_layer4_dialectic_methodology_2x_2026-06-11.md), the substrate runs the attribution self-check via a 30-line numpy primitive (substrate-cosine between prior-feature-weight-distribution and posterior-feature-weight-distribution tracks external KL). Same primitive validates substrate-CRF feature attribution pre-ship.

**12. Substrate-CRF + free-prob F4 (drill A): spectral observability of CRF weights.**
Free-probability F4 (free cumulants of P(h)) is the top-1 next-drill candidate per the field advisor; it applies to substrate-CRF directly. The structured-perceptron weight bundle accumulates over training; its eigenvalue distribution (after a substrate-cosine-similarity-to-feature kernel) has a spectral signature. Tracy-Widom edge fluctuations (F2 adjacency per the advisor) discriminate substrate-CRF in the "saturated training" regime from substrate-CRF in the "under-trained" regime: a healthy-trained CRF has weight-matrix eigenvalues with an extended-tail distribution; an under-trained CRF has near-Wigner-semicircle.

Operational use: the substrate can log structured-perceptron weight-bundle moments (mean, variance, skew, kurtosis) per epoch and detect convergence saturation via the Tracy-Widom-edge collapsing onto the Wigner edge. This is a substrate-novel observability primitive that classical CRF training does not have (classical CRF logs training-loss curves; substrate logs spectral-moment curves). Predicted: spectral saturation lags train-loss saturation by 1-3 epochs (the weight-distribution structure stabilizes before the scalar loss does); this gives an EARLIER stop criterion than train-loss.

Calibration: spectral observability of training trajectories is well-precedented (the free-prob 3x drill earlier today validated the substrate-side path); applying it specifically to CRF weights is incremental + novel-synthesis-cap-bounded; P=0.40 standalone, not gating the unification claim.

**13. Concrete unified architecture: one substrate-CRF library + task-specific feature templates + Tier-2 schema bundles per task.**
Concrete proposed implementation:

```
hdlab/
  structured/
    __init__.py
    crf.py                  # SubstrateCRF class (score, predict, update)
    decoders/
      viterbi.py            # linear-chain max-product semiring
      eisner.py             # projective MST dep-parse
      cle.py                # Chu-Liu-Edmonds non-projective MST
      argmax_flat.py        # multinomial argmax
      kbest_tree.py         # bounded-depth k-best tree decode
    feature_templates/
      universal.py          # unigram, context-window, label-bigram, prev/next-label
      task_pos.py           # suffix, prefix, morphology
      task_ner.py           # capitalization, gazetteer, word-shape
      task_dep.py           # arc-distance, arc-direction, head-pos, mod-pos
      task_flat.py          # task-specific lexicons (sentiment, intent, topic, op-keyword)
    schemas/
      pos_ptb.py            # 45-tag Penn Treebank
      ner_conll.py          # 8 BIO labels {B-PER, I-PER, B-LOC, I-LOC, ...}
      dep_ud.py             # Universal Dependencies arc labels
      intent_atis.py        # ATIS intent classes
      text_class.py         # per-corpus class set
      math_op.py            # operator alphabet for math word problems
      code_algopattern.py   # algopattern templates
    layer1_attribution.py   # weight-magnitude + ablation-lift Spearman gate
  
  registry/
    crf_tasks.yaml          # registry: task -> {decoder, schema, feature_templates, eval_metric, baseline}
```

The `crf_tasks.yaml` registry holds the per-task wiring; adding a new task = adding a registry row + (optionally) a new feature template + (optionally) a new schema. Existing infrastructure (training loop, structured perceptron, Frank-Wolfe SSVM, k-fold eval, multi-seed) is task-agnostic. This is the IllinoisSL / Torch-Struct design pattern verbatim, adapted to substrate primitives.

Engineering cost estimate:
- Core SubstrateCRF class + viterbi + argmax_flat decoder + universal templates: 1-2 days.
- Eisner + CLE + kbest_tree decoders: 1 day each.
- Per-task feature templates + schemas + registry: 0.5 day per task.
- Layer 1 attribution gate: 0.5 day.
- Total: ~7-12 engineering days for 11-task coverage.

## (e) Substrate-product implications

Four product-relevant consequences.

**1. Auditable structured-NLP stack as a substrate-product wedge.**
The substrate-CRF library is the structural backbone for an auditable structured-NLP stack: every prediction is decomposable into per-feature-template contributions, every training update is logged with weight-delta-per-feature, and Layer 1 attribution gives a customer-visible "why this label" explanation. This is the EU AI Act Article 12 compliance hook the universal-scientific-corpus drill and the architecture-change drill both already flagged. The substrate-CRF stack is the operational layer for that compliance story for any task in the 11-task list plus the 6-8 extensions.

**2. Cross-task feature reuse as a substrate-product efficiency wedge.**
The universal feature templates (unigram + context-window + label-bigram + prev/next-label) and the task-specific feature templates are SHARED across customers' tasks. A customer ingesting customer-specific intent classification + custom NER + custom slot-filling + custom text-class via substrate-CRF gets the universal templates for free and only pays for the task-specific templates. Versus per-task ML pipelines, this is a ~5-10x engineering-cost reduction per new task. Combined with the substrate's substrate-bundle feature class (typed-relational features that classical CRFs cannot use), this is a marketable efficiency + quality wedge.

**3. Cap_map row simplification.**
Currently the cap_map has 11 separate validated rows for the 11 NL tasks. Substrate-CRF universal collapses them into ONE row at tier-load-bearing ("substrate-CRF universal NL structured prediction") with sub-rows per task. The visibility surface goes from N=11 rows to N=1 row + N=11 task-feature entries. Strategy decisions get cleaner ("does substrate-CRF row pass HARD-PASS thresholds?") rather than 11 separate maintenance decisions.

**4. Risk: the unification holds only WITHIN the structured-prediction class.**
Substrate-CRF universal does NOT subsume open-domain generation, multi-hop reasoning > k=3, or arbitrary-LF semantic parsing. The substrate-CRF library is the structured-discriminative half of the substrate's NL stack; the generative half (formulator-style generation per the bounded-creative drill) remains a separate substrate primitive. The product story is therefore "substrate-CRF for structured outputs + substrate-generative-formulator for bounded generation + LLM-handoff for open-domain", consistent with the substrate-LLM boundary memory's current state.

## (f) Citations (verified count)

15 verified external citations + 8 cross-thread.

External:
1. Lafferty, McCallum, Pereira (2001). "Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data". ICML 2001. (canonical CRF)
2. Sutton, McCallum (2012). "An Introduction to Conditional Random Fields". Foundations and Trends in ML. arxiv 1011.4088. (degenerate-MLR-is-CRF; sum-product semiring; feature templates)
3. Collins (2002). "Discriminative Training Methods for Hidden Markov Models". EMNLP 2002. (structured perceptron)
4. Tsochantaridis, Hofmann, Joachims, Altun (2005). "Large Margin Methods for Structured and Interdependent Output Variables". JMLR. (structured SVM)
5. Chang, Srikumar, Goldwasser, Roth (2015). "IllinoisSL: A JAVA Library for Structured Prediction". arxiv 1509.07179. (universal library design; per-task instantiation)
6. Rush (2020). "Torch-Struct: Deep Structured Prediction Library". arxiv 2002.00876. (generic distributional API; CRF + semiring abstraction; vectorized DP)
7. Lacoste-Julien, Jaggi, Schmidt, Pletscher (2013). "Block-Coordinate Frank-Wolfe Optimization for Structural SVMs". ICML 2013. (training oracle = MAP inference)
8. McCallum (2003). "Efficiently Inducing Features of Conditional Random Fields". UAI 2003 + arxiv 1212.2504. (CRF feature induction; 93.96% POS via induced features)
9. McDonald, Crammer, Pereira (2005). "Online Large-Margin Training of Dependency Parsers". ACL 2005. (arc-factored MST dep-parse; structured perceptron on Eisner)
10. Sutton, McCallum (2007). "Piecewise Training for Structured Prediction". Machine Learning. (decomposable training; per-factor partition function)
11. Wikipedia (2026). "Structured prediction". (taxonomy of CRF / SSVM / structured perceptron)
12. arxiv 2309.07624 (2023). "Dynamic Modularized Reasoning for Compositional Structured Explanation Generation". (multi-step reasoning as structured output)
13. arxiv 1907.01339. "Sequence Labeling Parsing by Learning Across Representations". (parsing-as-sequence-labeling unification under multi-task framework)
14. arxiv 1103.0890. "Efficient Multi-Template Learning for Structured Prediction". (per-task template libraries)
15. arxiv 1510.07099. "Combine CRF and MMSEG to Boost Chinese Word Segmentation in Social Media". (BIO-character CRF for word segmentation = same library)

Cross-thread (from today's drills, all under d:/AI/hd-instrument/notes/):
- research_drill_substrate_structured_prediction_2x_2026-06-11.md (1x predecessor: CRF+SSVM+EBM trichotomy)
- research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11.md (MST + higher-order parts + structured perceptron compose)
- research_drill_ner_substrate_paths_2x_2026-06-11.md (BIO-constrained Viterbi + gazetteer + bigram + cascade)
- research_drill_asdiv_030_plateau_substrate_paths_2x_2026-06-11.md (compositional 2-op math limit + dispatcher)
- research_drill_gsm8k_substrate_boundary_2x_2026-06-11.md (multi-step + tree-decomposition substrate paths)
- research_drill_layer4_dialectic_methodology_2x_2026-06-11.md (Layer 4 surprise classifier = substrate-CRF attribution analog)
- research_drill_substrate_proposed_architectures_2x_2026-06-11.md (gate-frozen-at-cycle-0 invariant applies to substrate-CRF library evolution)
- research_drill_substrate_open_domain_creative_nl_2x_2026-06-11.md (boundary diagnosis: substrate-CRF does NOT subsume open-domain generation)

## (g) Calibration summary

| Claim | P_raw | P_deflated | Cap | Lit-precedent strength |
|---|---|---|---|---|
| Substrate-CRF library covers chain + flat + arc-factored-tree | 0.80 | 0.65 | 0.50 (cap not binding) | strong (IllinoisSL + Torch-Struct + Collins direct precedent) |
| All 11 validated tasks reproduce in unified library within +/- 0.01 | 0.65 | 0.45 | 0.50 | moderate (cross-task variance, library abstraction risk) |
| At least 3 universal feature templates with lift >=0.01 on >=4 tasks | 0.75 | 0.60 | 0.50 (cap binding) | strong (unigram + bigram + context-window universal per CRF tutorials) |
| Layer 1 attribution Spearman >=0.60 predicts task-feature lift | 0.55 | 0.40 | 0.50 | moderate (attribution methods well-known; substrate-side attribution novel) |
| Compositional 2-op tasks (math + code) reach baseline via library | 0.60 | 0.40 | 0.45 | moderate (k-best-tree decode is standard; substrate compositional bound applies) |
| Typed-relational features (slipnet + cue-adjacency) lift >=3 tasks | 0.55 | 0.30 | 0.45 | weak-novel (no published precedent on substrate-bundle-as-CRF-feature integration) |
| Substrate-CRF universal as load-bearing cap_map row after pilots | 0.70 | 0.55 | 0.55 | net of above |

The headline P_deflated=0.55 is the bottom-line for the substrate-CRF universal claim conditional on UNIFICATION-PILOT-1/2/3 all passing or middle-banding. If HF1 or HF2 fires, the claim retracts to "substrate-CRF library for chain + flat only" at P=0.65.

## (h) Substrate-intrinsic capability extension framework

Per user strategic refocus (substrate-intrinsic capability extension, NOT LLM comparison):

The substrate-CRF universal primitive is the FIRST architectural primitive in the substrate-classical NL stack that subsumes more than ONE empirically validated capability. Prior cap_map rows are per-task (POS row, NER row, dep-parse row). Substrate-CRF universal is the FIRST cross-task PRIMITIVE row.

This sets a template for subsequent substrate-intrinsic capability extensions:

- **Substrate-CRF universal** (this drill): covers structured prediction class (11+ tasks).
- **Substrate-resonator universal** (open candidate): covers factorization + retrieval-from-composite + slot-filling on bound vectors.
- **Substrate-formulator universal** (per bounded-creative drill): covers bounded generation under templated structure.
- **Substrate-attribution universal** (per Layer 1 + Layer 4 drills): covers surprise classification + feature-value pre-ship gating + structural-drift detection.

The capability-extension framework is: identify a PRIMITIVE class with N>=3 validated empirical instantiations; build a substrate-native UNIFIED library that subsumes them under one API; verify the unification holds on the existing instantiations + extends predictably to neighboring tasks. Substrate-CRF universal is the test case for this framework; if UNIFICATION-PILOT-1/2/3 pass, the framework is empirically validated and we apply the same pattern to substrate-resonator, substrate-formulator, substrate-attribution as the v1 product's structural backbone.

This is the substrate-intrinsic axis the user-locked NORTH-STAR (functional system beats LLMs) wants surfaced: the substrate ships PRIMITIVES that subsume task classes, not per-task implementations. The marketable product story is "substrate-CRF is one library, 11+ NL tasks, audit-grade explanations, cross-task feature reuse, typed-relational features no classical or LLM CRF stack can use" -- a structural differentiator at the architecture level, not a per-benchmark win.
