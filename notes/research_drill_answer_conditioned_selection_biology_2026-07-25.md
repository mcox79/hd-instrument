# Research drill: answer-conditioned selection as the next lever on the ARC selection wall

**Date:** 2026-07-25
**Serves:** the 5-experiment SELECTION_HARD_FAIL finding (retrieval recall@100=0.69 given gold, oracle-combine Challenge=0.71, but answer-agnostic selection precision 0.11-0.19 vs oracle 0.97; content-enrichment fair re-test shows richer CONTENT raises topic-cosine symmetrically across all 4 choices and cannot break gold-vs-lure symmetry through a linear read-out).
**KB-check:** `substrate_query.sh` run on two queries ("answer-conditioned retrieval hypothesis testing fact selection multiple choice"; "differential support evaluation which candidate answer brain") — both top hits were noise-level cosine (0.34-0.38: WordNet "conditioned reaction", "differential evolution", unrelated pre-regs). **No prior-arc drill exists on answer-conditioned/hypothesis-testing selection.** This is new ground, not a dedup.

---

## 1. Is human MC-reasoning answer-conditioned / hypothesis-testing? — YES, well-grounded

Three independent literatures converge on the same shape:

- **PFC goal-biased memory retrieval (biology-grounded).** Retrieval is not passive best-match search. Goal/hypothesis representations held in PFC bias competition among memory traces by boosting activation for goal-relevant content and, via lateral inhibition, suppressing competitors (Kuhl et al.; "Competition and representation during memory retrieval," PNAS). The PFC differentially engages with the *degree of competition* during retrieval — i.e. it actively tracks which candidate is currently being tested, not just "what's most associated with the cue."
- **Differential diagnosis / illness-script reasoning (biology + cognitive-architecture, closest task-analog to 4-way MC).** Clinicians generate a small candidate SET early (hypothetico-deductive method), then for each candidate they seek a specific test that would confirm-or-rule-out THAT candidate. This is explicitly per-hypothesis, per-candidate evidence-seeking — structurally identical to what an answer-conditioned selector would do for ARC-Challenge's 4 choices.
- **Sequential-sampling / evidence-accumulation decision models (DDM extended to n-alternative choice; Leaky Competing Accumulator, Usher & McClelland 2001).** The brain's decision variable is not a single scalar "how relevant is this evidence" — it is N parallel accumulators (one per candidate), each integrating evidence over time, coupled through mutual inhibition/leakage. Multiple-alternative DDM extensions formalize exactly the n-way competitive-accumulation structure MC discrimination needs.

**Conclusion:** answer-conditioning is not a hack, it is the literal brain-mechanism shape — retrieval/evidence-seeking in the brain is *always* referenced against a currently-held candidate/hypothesis representation, never candidate-agnostic.

## 2. Differential support / avoiding the confirmation trap

- **Likelihood ratio vs. likelihood.** The normative measure of how strongly a piece of evidence discriminates between two hypotheses is the *likelihood ratio* P(e|H_gold)/P(e|H_lure), not the raw likelihood P(e|H_gold). A fact that is equally probable under gold and under lure has LR≈1 and should NOT move the decision, however strong its raw topical relevance. This is precisely the failure mode diagnosed in the fair re-test: enrichment raises P(fact-topic-match | any choice) roughly uniformly, which raises likelihood for all 4 candidates together and leaves the ratio near 1.
- **Caveat, biology-grounded (Nelson 2005):** pure Bayesian "diagnosticity" (odds-based measure) has been shown empirically and normatively flawed as a predictor of what people actually treat as a useful question/test; humans track something closer to *information gain / probability gain / impact* — measures that also weight prior probability and expected posterior shift, not just the raw odds ratio. For a roughly-uniform 4-way MC prior this collapses close to a per-choice log-likelihood-ratio matrix, but the general lesson is: the RIGHT discriminability metric is not "topic similarity," it is some form of *expected shift in the belief distribution over the 4 choices*, which requires scoring each fact against each choice, not once against the question alone.
- **Mutual inhibition / competitive normalization (LCA, attractor networks; biased competition, Desimone & Duncan).** The brain does not score each hypothesis independently and then compare scores post-hoc — competing representations actively suppress each other AS evidence accumulates, so evidence for one candidate is intrinsically evidence *against* the others (a relative/contrastive quantity), not an independent additive scalar per choice.
- **Thagard's ECHO (explanatory coherence).** Formalizes hypothesis evaluation as constraint satisfaction with explicit INHIBITORY links between rival hypotheses and between a hypothesis and evidence that better explains a competitor. Coherence-maximization is a network relaxation over excitatory (supports) and inhibitory (contradicts/competes) links — again fundamentally a *contrastive*, not additive, computation.

**Conclusion:** the correct metric shape is a per-fact × per-choice matrix reduced by a *contrast* operation (max-margin / softmax-with-inhibition / explicit likelihood ratio) across the choice dimension — never a single question-only relevance scalar.

## 3. Is the read-out nonlinear/conjunctive?

- **Dendritic coincidence detection / supralinear integration (biology-grounded).** Neurons that must respond to the CONJUNCTION of two converging input streams (e.g. a top-down hypothesis signal and a bottom-up evidence signal) show supralinear (threshold, multiplicative-like) dendritic integration — the neuron fires disproportionately more when both inputs coincide than the sum of either alone. This is the brain's hardware solution to "this fact matters only in conjunction with this specific candidate."
- **Biased-competition gain modulation.** Top-down attention/goal signals act as a *multiplicative gain* on bottom-up evidence, not an additive offset — consistent with conjunctive/nonlinear combination rather than a linear sum of independent relevance terms.
- **Substrate-native implication — this is actually EASIER for us than for a biological/connectionist net.** A biological neuron *needs* a special nonlinear dendritic mechanism to get a conjunctive code, because linear summation is the default in point-neuron models. A VSA/HDC substrate gets conjunction for free: the `bind` operator (typically XOR/circular-convolution/multiplication) is *inherently* a nonlinear, non-additive, conjunctive combination of its operands — it is structurally the substrate-native analog of dendritic coincidence detection. This means "answer-conditioned selection" and "nonlinear conjunctive read-out" are not two separate builds for us — binding the question representation with each candidate-choice representation (Q⊗C_i) to form 4 distinct conditioned queries *is* the nonlinear conjunctive step, already available as a primitive. This collapses candidate-builds #1 and #3 from the prompt into one build in our architecture.

## 4. Grounding — separate lever, deeper, same or different problem?

- **Barsalou perceptual symbol systems / simulation.** For fine-grained content distinctions where the symbolic/relational content is genuinely thin (the diagnosed case: nuclear/coal/gas power-plant facts share the SAME relation and direction as hydroelectric — differing only in a fine physical-mechanism feature, e.g. "turns a turbine via falling water" vs "via combustion"), the brain's edge comes from perceptual/motor simulation instantiating the fine feature, not from denser co-occurrence statistics over the same symbol type.
- **This is a SEPARATE lever from answer-conditioning, addressing a different part of the failure.** Answer-conditioning fixes the *selection mechanism* (compare fact-to-EACH-choice, not fact-to-question-only). Grounding fixes *content resolution* (whether the fact representation can express the fine feature that actually distinguishes gold from lure in the first place). Diagnostically: if the fact content contains NO signal that discriminates "hydroelectric" from "coal/gas/nuclear" beyond generic power-plant co-occurrence, then even a perfect answer-conditioned contrastive selector has nothing to condition on — grounding is then necessary, not just sufficient.
- Sequencing implication: answer-conditioning should be tried FIRST because (a) it is brain-accurate at the mechanism level we're currently missing entirely (we have zero conditioning today — a bigger, cheaper-to-fix gap than content resolution), and (b) it is a precondition for correctly diagnosing whether remaining failures are selection-mechanism failures or content-resolution failures. Cases where enriched content already contains the discriminating feature (even faintly) but answer-agnostic selection washes it out in the symmetric average will be fixed by conditioning alone; cases where the feature is absent from content entirely will surface as a residual failure *specifically diagnostic of the grounding gap*, i.e. the correct next-build order self-reveals from the results of build #1.

---

## Comparison to current pipeline — name the gap (shape / place / metric)

| | Current | Brain-accurate |
|---|---|---|
| **Shape** | Single question-only retrieval → K facts selected answer-agnostically → combiner scores 4 choices post-hoc (additive/linear read-out over a shared fact pool) | 4 parallel conditioned retrievals, one per candidate (Q⊗C_i), each forming its own evidence accumulator; facts scored per-choice, not once |
| **Place** | Selection happens BEFORE any choice-conditioning exists in the pipeline | Conditioning must happen AT retrieval/selection time, not after (post-hoc scoring of an unconditioned pool cannot recover information destroyed by the earlier answer-agnostic max/top-K cut) |
| **Metric** | Topic-cosine / relevance-to-question (symmetric across choices by construction) | Contrastive / differential-support metric: per-fact per-choice score reduced by a competitive-normalization or explicit-contrast operation across the 4 choices (likelihood-ratio-flavored, not raw similarity) |

The prior fair re-test (content-enrichment) already proved the metric-and-shape gap analytically: raising symmetric topic-relevance cannot fix an asymmetric (gold-vs-lure) decision, no matter how rich the content, because the read-out never compares across choices. That is exactly the shape gap named above, independently confirming the diagnosis from the biology side.

## Ranked candidate builds

1. **Answer-conditioned contrastive selection (bind Q with each choice, score per-choice, reduce by contrast/inhibition across choices).** Highest brain-fidelity (PFC goal-biased competitive retrieval + illness-script differential diagnosis + multi-alternative DDM/LCA + likelihood-ratio norm + ECHO inhibitory contrast — five independent literatures converge) and highest expected leverage (it is a direct, structural fix for the exact mechanism gap the fair re-test diagnosed: answer-agnostic averaging destroys the discriminating signal before the combiner ever sees it). In a VSA substrate this build inherently IS the nonlinear/conjunctive read-out too (bind is conjunctive by construction), so this ranks build-candidates #1 and #3 from the prompt as one build, not two.
2. **Nonlinear conjunctive read-out as a separate/general mechanism.** Subsumed by #1 for us (see above) — not worth building as an independent lever; only relevant if a linear-algebra (non-VSA) combiner stage remains downstream and needs its own conjunctive term (e.g. an explicit Q·C_i·fact three-way term) after conditioned retrieval is in place. Lower priority, revisit only if #1's combiner stage still under-performs after conditioning is added.
3. **Perceptual/embodied grounding for fine-feature content resolution.** Real and biology-grounded (Barsalou), but addresses a DIFFERENT part of the pipeline (content, not selection mechanism) and is a deeper/costlier build. Correct sequencing: ship #1 first; its residual failure pattern will diagnostically separate "selection-mechanism cases" (fixed by conditioning) from "content-resolution cases" (need grounding), avoiding a premature, harder investment before knowing how much of the gap #1 closes.

## Claim classification

- Biology-grounded (direct citation support above): PFC goal-biased/competitive memory retrieval; DDM/LCA multi-alternative evidence accumulation; biased competition (Desimone & Duncan) top-down gain modulation; dendritic supralinear/coincidence-detection nonlinearity; likelihood-ratio as normative discriminability measure; Barsalou perceptual symbol systems/simulation; illness-script/hypothetico-deductive differential diagnosis.
- Cognitive-architecture / partially speculative synthesis (reasoned extension, not directly cited): the specific claim that "VSA bind is the substrate-native analog of dendritic coincidence detection, collapsing builds #1 and #3 into one" is our own architectural inference, not a claim from the literature — flagged as speculative-but-well-motivated, to be confirmed empirically once the build lands (does conditioned-bind selection actually recover discriminability on the dam-Q case, per the glass-box test that surfaced it).
- Speculative: the exact sequencing prediction ("residual failures after #1 will self-diagnose the grounding need") is a testable hypothesis, not yet observed.

## Sources
- [Effective remembering requires the retrieval of goal-relevant information](https://web.stanford.edu/group/memorylab/papers/KUHCABN08.pdf)
- [Competition and representation during memory retrieval: Roles of the prefrontal cortex and the posterior parietal cortex (PNAS)](https://www.pnas.org/doi/10.1073/pnas.0832374100)
- [A Prefrontal-Hippocampal Comparator for Goal-Directed Behavior](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4658443/)
- [Drift–diffusion models for multiple-alternative forced-choice decision making (J. Math. Neurosci.)](https://link.springer.com/article/10.1186/s13408-019-0073-4)
- [A practical introduction to using the drift diffusion model (Frontiers in Psychology)](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.1039172/full)
- [The Leaky, Competing Accumulator Model (Usher & McClelland 2001, Psych Review, Stanford PDF)](https://stanford.edu/~jlmcc/papers/UsherMcC01.pdf)
- [Choice selective inhibition drives stability and competition in decision circuits (Nature Communications)](https://www.nature.com/articles/s41467-023-35822-8)
- [Biased competition theory (overview)](https://en.wikipedia.org/wiki/Biased_competition_theory)
- [Visual attention mediated by biased competition in extrastriate visual cortex (Desimone 1998)](https://www.cns.nyu.edu/csh/csh04/Articles/Desimone-98.pdf)
- [Explanatory coherence (Thagard, gwern archive of BBS target article)](https://gwern.net/doc/philosophy/epistemology/1989-thagard.pdf)
- [Likelihood ratios in diagnostic testing (overview)](https://en.wikipedia.org/wiki/Likelihood_ratios_in_diagnostic_testing)
- [Finding Useful Questions: On Bayesian Diagnosticity, Probability, Impact, and Information Gain (Nelson 2005, PubMed)](https://pubmed.ncbi.nlm.nih.gov/16262476/)
- [Confirmation, Disconfirmation, and Information in Hypothesis Testing (Klayman & Ha 1987, UCSD PDF)](https://pages.ucsd.edu/~mckenzie/KlaymanHaPsychReview1987.pdf)
- [How Doctors Generate Diagnostic Hypotheses: fMRI study of radiological diagnosis (PLOS ONE)](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0028752)
- [Contribution of sublinear and supralinear dendritic integration to neuronal computations (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4371705/)
- [Perceptual symbol systems (Barsalou 1999, PubMed)](https://pubmed.ncbi.nlm.nih.gov/11301525/)
- [Grounded Cognition (Barsalou, MIT Open Encyclopedia of Cognitive Science)](https://barsaloulab.org/Online_Articles/2026-Barsalou-OECS-grounded_cognition.pdf)
