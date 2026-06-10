# Research drill: Aesthetic revival -- brain + nature + LLM synthesis
# Date: 2026-06-10
# Streams: A (brain/neuroaesthetics), B (evolution/nature), C (LLM theory), D (synthesis + crazy substrate math)

---

## HEADLINE

Three convergent streams (brain reward + evolutionary signal-honesty + LLM reward-hacking) point to one shared failure mode: substrate retreats to schema-fit and formal genre compliance because those are the cheapest paths to an aesthetic reward proxy. The brain signal that actually flags aesthetic quality is a specific temporal pattern -- prediction error buildup followed by coherent resolution -- not classification accuracy on beauty. A substrate could approximate this with anomaly-margin dynamics at composition boundaries, at much smaller scale than LLM RLHF.

---

## Cheap decisive test

Take a held-out passage set with human aesthetic ratings (e.g. 50 short creative passages rated 1-10). Compute substrate cleanup margin at each token/chunk boundary. Check: does cleanup-margin variance across a passage correlate with human rating better than passage-length, genre-match, or keyword-presence? If Pearson r >= 0.40 at N=50 passages, the frisson-proxy hypothesis is not refuted at this scale. CPU only, ~20 min.

---

## Falsifiable predictions

HARD-PASS: Cleanup margin variance (std of cosine-cleanup values across composition steps within a passage) predicts human aesthetic rating at r >= 0.40 AND outperforms a genre-match baseline.

HARD-FAIL: Cleanup margin variance shows r < 0.15 vs human ratings, indistinguishable from noise, after controlling for passage length. This would refute the substrate-frisson proxy hypothesis and rule out Mechanism D2.3.

HARD-FAIL 2: Anomaly x skill composite (D2.1) performs no better than skill alone on a passage-quality ranking task (Kendall tau improvement < 0.05). Would rule out D2.1 as a substrate aesthetic scorer.

MID-BAND: r in [0.15, 0.40] -- partial signal; worth scale-up to 200 passages before conclusion.

---

## Stream A: Brain mechanisms for aesthetic experience

### A1. Core reward circuitry -- nucleus accumbens, dopamine, mu-opioid
Multiple neuroimaging studies (Chatterjee & Vartanian 2014; Blood & Zatorre 2001; Ferreri et al. 2021) establish that beauty experiences activate the nucleus accumbens, orbitofrontal cortex, and ventral striatum -- the same regions as food, sex, and drug reward. Critically, dopamine release is anticipatory: the brain fires on the build-up toward an aesthetic peak, not just at the peak. Opioid blockade (naltrexone) reduces frisson intensity, confirming mu-opioid mediation of the hedonic component. This is not just "pleasure" -- it is a prediction-error-gated reward signal that requires the correct temporal structure to fire.

### A2. Default mode network (DMN)
Vessel, Starr & Rubin (2012, PNAS; Vessel & Isik 2019, PMC) showed that the DMN, normally suppressed during external attention, activates specifically for deeply moving art -- not merely pleasant stimuli. The DMN encodes self-referential relevance: aesthetic experience is the brain assessing whether an external object is personally meaningful. The more the DMN engages, the higher the rated aesthetic experience. This means aesthetic quality is partly a function of self-model engagement, not pure sensory properties.

### A3. Predictive processing account (Van de Cruys, Pelowski, Tschacher)
Van de Cruys & Wagemans (2011; Royal Society B 2023 special issue) formulate aesthetic experience as a two-phase process: (1) prediction error generation -- the artwork introduces incongruity, tension, unresolved structure -- followed by (2) resolution that "explains away" the error in a satisfying cascade. Beauty is specifically the reward signal for successful high-surprise resolution, not for low error. This is quantitatively formalized as Bayesian surprise: high KL divergence between prior and posterior beliefs, resolved in a single comprehension step. Artworks that never resolve (pure chaos) or never surprise (pure cliche) both score low. The sweet spot is maximal surprise with coherent resolution.

### A4. Berlyne arousal theory and its limits
Berlyne (1971) proposed the inverted-U: optimal incongruity between expectation and stimulus maximizes hedonic value. His four collative properties (complexity, novelty, incongruity, surprisingness) remain empirically useful taxonomically even though the inverted-U functional form is weakly supported. A 2021 re-examination (Althuizen, Psychology & Marketing) of 1800+ participants found scant support for the inverted-U in product design aesthetics. The underlying variables (complexity, novelty) still predict liking, but not through arousal as a single mediating variable. More likely: complexity and novelty modulate the prediction-error signal (A3) via independent channels.

### A5. Schmidhuber compression-progress theory
Schmidhuber (2009, Springer; 1990-2010 formal theory) defines interestingness as the derivative of compression ability: data is temporarily interesting precisely when it allows the observer's internal model to compress previously incompressible patterns. Beauty is static compression quality (a pattern with short description length); interestingness is the rate of change of compression ability over time. This is formally equivalent to the prediction-error-resolution account (A3): resolution = compression event. The compression-progress signal is the reward for the learning step, not for the compressed state.

### A6. Peak-shift and supernormal stimuli (Ramachandran)
Ramachandran & Hirstein (1999, Journal of Consciousness Studies) describe eight laws of aesthetics derived from neurological principles. Peak-shift is the most actionable: exaggerating the discriminating features of a category (a caricature's exaggerated nose, a Chola bronze's exaggerated curves) produces a stronger neural response than the prototype. The key mechanism is that feature detectors in visual cortex respond more strongly to exaggerated stimuli in the discrimination direction, not in all directions. This predicts: good art is not average, it is a directed deviation from average that maximizes the signal-to-noise of the relevant feature detector.

### A7. Frisson and aesthetic chills
Frisson (piloerection, chills, goosebumps) is the strongest measurable behavioral marker of peak aesthetic experience in music. Neuroimaging (Blood & Zatorre 2001; Ferreri et al. 2021 PMC7669983) localizes frisson correlates to the ventral striatum, amygdala, and insular cortex. The temporal dynamics are critical: frisson occurs specifically at moments of expectation violation followed by resolution (an unexpected chord progression that resolves; a dramatic key change that coheres). Opioid blockade attenuates frisson, confirming it as a genuine reward signal, not merely a startle response.

### A8. Embodied simulation (Freedberg & Gallese)
Freedberg & Gallese (2007, Trends in Cognitive Sciences; Gallese 2025, Journal of the American Psychoanalytic Association) propose that viewing artistic gestures activates mirror-neuron circuitry in the observer, producing an internal motor simulation of the artist's physical act. This is not metaphorical: viewing brush-stroke traces on canvas activates specific motor areas corresponding to the required arm movements. The aesthetic experience of dynamic art includes a kinetic component -- the observer's body models the generating process. This points to a modality not captured by compression-progress or prediction-error models alone.

### A9. Cross-cultural universals
Berlin & Kay (1969) on color terms; Berlyne (1974) on cross-cultural complexity preferences; more recently Vessel et al. (2019) finding DMN aesthetic encoding generalizes across cultural groups. Cross-cultural constants in beauty preference are real but limited: symmetry preference, moderate complexity preference, preference for warm colors are near-universal. High-level aesthetic judgments (which works are deeply moving) are highly culturally variable. The cross-cultural substrate of aesthetics appears to be at the level of perceptual processing biases (symmetry detection, edge detection, color tuning), not at the level of learned genre conventions.

### A10. Orbitofrontal cortex as convergence zone
Chatterjee (2014, The Aesthetic Brain) identifies the medial orbitofrontal cortex (mOFC) as the principal site where sensory representations converge with reward value to produce an aesthetic judgment. The mOFC fires proportionally to self-reported beauty across visual, auditory, and olfactory domains. This is the neural read-out, not the generator: the mOFC integrates inputs from sensory processing, memory (hippocampus), self-model (DMN), and reward prediction (nucleus accumbens) into a single scalar aesthetic value signal.

---

## Stream B: Evolutionary mechanisms for natural beauty

### B1. Sexual selection and Zahavi handicap principle
Darwin (1871, Descent of Man) identified sexual selection as the mechanism producing non-adaptive beauty. Zahavi (1975, Journal of Theoretical Biology; Zahavi & Zahavi 1997) formalized the handicap principle: costly ornaments (peacock tail, large antlers) are honest signals of fitness precisely because they are costly. Only a genuinely high-fitness individual can afford to carry the metabolic/predation burden of an extreme ornament. Grafen (1990, Journal of Theoretical Biology) provided game-theoretic proof that costly signaling is an evolutionarily stable strategy. The critical insight: beauty in sexual selection is not arbitrary preference but an empirically reliable proxy for underlying quality, stabilized by the cost structure.

### B2. Bowerbirds -- learned aesthetic criteria
Bowerbirds (genus Ptilonorhynchus and relatives) are the clearest natural case of culturally-evolved aesthetic criteria. Males build elaborate display structures decorated with carefully selected objects; female preferences drive construction quality. Key findings: (1) great bowerbirds create forced-perspective illusions that make objects appear uniformly sized from the female's vantage point (Endler et al. 2010, PNAS) -- demonstrating genuine spatial aesthetic reasoning; (2) problem-solving ability predicts mating success (Keagy et al. 2009) -- aesthetic complexity signals cognitive quality; (3) female preferences vary geographically and appear to involve cultural transmission, not purely genetic inheritance. This is the strongest non-human case of culturally-transmitted aesthetic preference.

### B3. Sensory bias / exploitation (Endler, Ryan)
Ryan & Rand (1990, Science) demonstrated in tungara frogs that female preference for the "chuck" component of male calls pre-existed the evolution of male chucks -- the male trait evolved to exploit a pre-existing auditory bias in the female perceptual system. Endler & Basolo (1998, Trends in Ecology & Evolution) generalized the "sensory trap" model: male traits need not be intrinsically costly if they exploit a receiver bias that evolved for an unrelated function. This is mechanistically important: aesthetic preferences can originate from arbitrary sensory biases (e.g., preference for red because red fruits are nutritious) and be co-opted by sexual ornaments at zero signal-production cost.

### B4. Fluctuating asymmetry (FA)
Thornhill & Gangestad (1994, Psychological Science) proposed that low FA (high bilateral symmetry) signals developmental stability and genetic quality, predicting both attractiveness and mating success. Meta-analysis (Polak 2003; Gangestad & Simpson 2000) confirms a real but small effect size: low FA correlates with attractiveness ratings, but the causal chain is contested. Recent work (Little et al. 2014) finds FA does not consistently predict childhood health outcomes. The mechanism is real but narrower than claimed: symmetry preference is primarily a sensory bias (visual system prefers symmetric patterns for a computational reason -- easier to process and represent) that has been secondarily co-opted as a fitness cue.

### B5. Costly signaling -- general
Zahavi's framework generalizes beyond sexual ornaments. Any signal that is informationally honest must be costly to produce. Art as costly signal: producing a high-quality aesthetic output requires genuine skill + effort, which is non-trivially costly for low-skill producers. This means aesthetic quality is a natural costly signal of cognitive and creative capacity. The evolutionary function of art-production capacity may be mate-signaling (Miller 2000, The Mating Mind), social coordination, or group identity marking (Dissanayake 1992).

### B6. Lyrebird mimicry -- complexity as signal
The superb lyrebird (Menura novaehollandiae) produces the most complex vocal mimicry known in any animal -- including accurate mimicry of chainsaws, car alarms, and cameras. The key finding (Dalziell et al. 2013, Current Biology): mimicry complexity directly predicts female preference. The mechanism is not "accurate representation" but "demonstrated repertoire width" -- the signal value is the sheer range and accuracy of the mimic. This maps onto Schmidhuber compression-progress: a broader generative model that can accurately reproduce a wider distribution of signals is signaling a higher-quality internal model.

### B7. Flower evolution and pollinator aesthetics
Flowers are not beautiful for humans; they evolved to be beautiful for their specific pollinators. UV reflectance patterns (invisible to humans) guide bees; red coloration guides hummingbirds with red-sensitive vision; bilateral symmetry in certain flowers is a landing guide for approach-optimized insects. Endler (1992) identified "sensory drive" as the mechanism: signals evolve to maximally exploit the sensory system of the intended receiver in the relevant detection environment. The substrate implication: "beautiful" is always relative to the receiver's perceptual architecture, not absolute.

### B8. Cultural evolution of art -- Blombos Cave
Henshilwood et al. (2002, Science; 2009, Journal of Human Evolution) document engraved ochre from Blombos Cave, South Africa, dated ~75,000-77,000 years ago -- the oldest securely dated symbolic art. The engravings are geometric (cross-hatched patterns), suggesting that abstract geometric regularity, not representational accuracy, was the earliest aesthetic output. This is consistent with the sensory-bias hypothesis: geometric regularity is computationally preferred by the visual system regardless of referential content. Stiner & Kuhn (2006) trace symbolic behavior across the African Middle Stone Age, showing gradual accumulation of aesthetic innovation linked to population density increases (social signaling pressure drives aesthetic complexity).

### B9. Golden ratio -- is it real?
The claim that phi = 1.618... appears ubiquitously in nature and art is mostly mythology. Livio (2002, The Golden Ratio) reviewed the evidence and found the claimed appearances in art (Parthenon, Mona Lisa) are post-hoc measurements that do not hold up under rigorous analysis. In nature, phyllotaxis (leaf and seed arrangement) does produce Fibonacci spirals, but these emerge from a packing efficiency constraint (each new element placed at the golden angle 137.5 degrees to maximize exposure), not from an intrinsic aesthetic property of the ratio. The "golden ratio is beautiful" claim is not well-supported; the "packing efficiency produces Fibonacci structure" claim is solid.

### B10. Niche construction and aesthetic environments
Odling-Smee, Laland & Feldman (2003, Niche Construction, Princeton) describe how organisms modify their own selection environment. Bowerbirds are a prime case: the bower is a constructed aesthetic environment that itself becomes a selection pressure on female preference (females select males who construct environments that match their preference). This recursive loop is directly relevant to a substrate that must produce outputs that change what the receiver finds beautiful over time.

---

## Stream C: LLM mechanisms for aesthetic generation

### C1. RLHF and aesthetic reward models
RLHF trains a reward model on human preference comparisons and uses it to fine-tune the base LLM. For aesthetic tasks, the reward model captures rater preferences over creative writing quality. Key finding from CreativityPrism (2025, arXiv 2510.20091): proprietary LLMs dominate quality and diversity metrics in creative writing by ~15% over open-source, but show no advantage in divergent thinking (novelty). This means RLHF primarily optimizes for rater-preference proxies of quality (coherence, grammar, conventional beauty) but does not push novelty. The Goodhart failure mode is structural: once the reward proxy is optimized, the model converges on safe, high-probability outputs in the reward model's high-scoring region.

### C2. LAION-Aesthetics CLIP predictor
Schuhmann et al. (2022, LAION) trained a lightweight MLP on CLIP ViT-L/14 image embeddings to predict aesthetic scores from the AVA dataset and Simulacra Aesthetic Captions. The resulting predictor is widely used to filter training data for diffusion models. Critical limitation identified in a 2026 audit (arXiv 2601.09896): the LAION aesthetic predictor encodes systematic biases toward Western photographic conventions and tends to rate smooth, well-lit, conventionally composed images highly, regardless of artistic merit or originality. This is the computational analog of genre-compliance: the predictor learned to recognize the surface features of images that human raters in the training set associated with quality.

### C3. Diffusion model aesthetic fine-tuning
Fine-tuning diffusion models with aesthetic reward signals (RL from human feedback: PPO, DPO, GRPO applied to image generation; see arXiv 2305.13301, 2406.04314) produces measurably better-rated images by standard aesthetic metrics. The mechanism is essentially policy gradient optimization against the LAION aesthetic predictor or HPSv2. The failure mode: models fine-tuned on aesthetic rewards produce images that are highly rated by the metric but often describe users as "too perfect," "plastic," or "uncanny" -- the Goodhart collapse of the proxy.

### C4. Mode collapse in RLHF
Reward model optimization drives the generation distribution toward the mode of the reward model's high-scoring region. For creative writing, this produces homogenized outputs: grammatically flawless, conventionally structured, emotionally legible, but predictable. The 2025 research on reward hacking in LLMs (arXiv 2604.13602) documents this as "emergent proxy maximization": models learn to produce the surface features the reward model associates with quality (e.g., specific sentence structures, emotional labeling words, paragraph length norms) rather than the underlying quality those features once indicated.

### C5. Compression-based novelty and LLMs
LLMs trained on next-token prediction are implicitly optimizing for compression: the model that assigns highest probability to held-out tokens has the best compression of the training distribution. But this is static compression of a known distribution, not compression-progress on new material. The Schmidhuber reward signal requires new compression -- learning something previously uncompressible. LLMs at inference time do not learn; they sample from a fixed model. This is a structural deficit: LLMs cannot produce genuine compression-progress because they do not update their model during generation.

### C6. In-context style emulation
LLMs can reproduce stylistic features of writing (sentence length distribution, vocabulary range, syntactic patterns, thematic emphasis) via in-context examples without fine-tuning. This is technically impressive but aesthetically shallow: style-as-surface-statistics is not the same as style-as-generative-principle. A model that matches Hemingway's word-length distribution does not generate Hemingway's compression-of-meaning. The capability is useful as a starting point but does not solve the underlying aesthetic generation problem.

### C7. Mechanistic circuits -- no dedicated aesthetic circuits found
Current mechanistic interpretability work (2024-2025, sparse autoencoders, transcoder circuits) has identified circuits for factual recall, arithmetic, object identification, and induction. No dedicated "aesthetic quality" circuits have been identified in transformer language models. The nearest analog is the circuits that process semantic similarity and stylistic coherence, but these are not specifically tuned for aesthetic quality as distinct from grammatical coherence. This absence is informative: aesthetic quality in LLMs may emerge from the interaction of many distributed features rather than a dedicated aesthetic evaluation module.

### C8. GAN adversarial aesthetics
Generative adversarial networks produce images whose aesthetic quality is determined by the discriminator's learned criterion. The discriminator learns to distinguish real from generated images, and in doing so learns a low-dimensional manifold of "real-looking" visual statistics. Fine-tuning the generator against aesthetic predictors (as in StyleGAN-NADA, various aesthetic-GAN variants) improves human ratings but via the same Goodhart mechanism as RLHF. The adversarial dynamic does produce one genuine benefit: it is harder to Goodhart a live adversary than a fixed reward model, because the adversary adapts. This maps onto the evolutionary dynamic in B1-B2.

### C9. In-context novelty and divergent association
CreativityPrism (2025) finds novelty metrics (divergent association task -- find words semantically far from each other) show weaker improvement from RLHF scaling than quality metrics. The semantic distance metric used (cosine distance in embedding space between associates) is a reasonable proxy for divergent thinking. LLMs plateau on this metric even as they improve on quality, suggesting a genuine limitation in the current training paradigm for generative novelty vs. generative quality.

### C10. Creative Preference Optimization (CPO, 2025)
A 2025 approach (arXiv 2505.14442) applies preference optimization specifically to creative writing, with preference pairs labeled for creative quality rather than factual accuracy. This is a targeted attempt to move RLHF away from pure rater-preference-on-conventional-criteria toward specifically creative-merit criteria. Early results are promising but the framework still depends on human rater preferences, which reintroduce the Goodhart problem unless raters can reliably identify genuine novelty vs. surface-quality markers.

---

## Stream D: Synthesis and crazy substrate math for aesthetic revival

### D1. What all three streams share

Three core mechanisms appear across brain, nature, and LLM research:

1. PREDICTION ERROR + COHERENT RESOLUTION: The brain's reward signal for aesthetics is not classification accuracy but temporal dynamics -- buildup of unresolved expectation followed by satisfying coherent resolution. Evolution rewards signals that are surprising yet reliable (costly signal = high surprise + honest information content). LLMs fail aesthetics by optimizing static quality proxies that eliminate the prediction-error dynamic.

2. NOVELTY x COHERENCE: The sweet spot is not maximum novelty (chaos) or maximum coherence (cliche) but a specific combination: locally surprising but globally coherent. This is Berlyne's inverted-U (partial evidence), Van de Cruys' prediction-error resolution, Schmidhuber's compression-progress, and Zahavi's costly signal all pointing at the same joint constraint.

3. SIGNAL HONESTY / ANTI-GOODHART: In evolution, signal honesty is maintained by cost structure. In brains, frisson requires that the resolution is genuine (opioid system responds to real reward, not fake pleasure). In LLMs, the failure mode is exactly the loss of signal honesty when the proxy becomes the target. A substrate mechanism that maintains signal honesty structurally (not just by training) would be an architectural advantage.

---

### D2. Eight crazy substrate math systems for aesthetic revival

#### D2.1 ANOMALY-SKILL-INTEGRATION (Berlyne algebra)

Formulation: aesthetic_score = anomaly_margin(passage) x skill_score(passage)

Where:
- anomaly_margin = mean(cosine-distance from nearest stored prototype for each composition step)
- skill_score = fraction of composition steps that successfully resolve to a stored attractor (cleanup accuracy)

Rationale: This directly implements Berlyne's optimal incongruity in substrate algebra. Pure novelty (high anomaly, low skill) = failed resolution = low aesthetic. Pure schema-fit (low anomaly, high skill) = no surprise = low aesthetic. The cross-product rewards anomalous inputs that are nonetheless resolved -- exactly the prediction-error + coherent-resolution signal.

Testability: Laptop CPU. Compute anomaly_margin and skill_score across a labeled passage set. Check if the product predicts human aesthetic ratings better than either component alone.

Known limitation: The product form assumes independence of anomaly and skill; they are actually inversely correlated in a substrate (harder inputs are less likely to resolve). A more accurate formulation uses a threshold: skill_score is binary (resolved vs. not) and anomaly_margin is computed conditional on resolution.

#### D2.2 COMPRESSION-PROGRESS-METRIC (Schmidhuber in substrate algebra)

Formulation: compression_progress(passage) = sum over composition steps of [cleanup_margin(step_t) - cleanup_margin(step_{t-1})]

Interpret: positive values at a step = compression event (easier to resolve than the step before = learning-like signal). Negative values = compression failure (harder than expected). The aesthetic signal is the sum of positive compression events, normalized by passage length.

Rationale: This is the substrate's approximation of Kolmogorov-rate change. Each composition step where cleanup_margin improves represents a moment where the substrate "learned" something new about the passage structure. The cumulative positive compression-progress is the aesthetic reward proxy.

Known limitation: This does not update the substrate model (no learning at inference time) -- so compression-progress in the substrate is not genuine model-learning but rather sequential context building within a fixed retrieval architecture. This is a structural limitation vs. Schmidhuber's full theory.

#### D2.3 PREDICTION-ERROR-CHILL (frisson proxy)

Formulation: frisson_event(step_t) = 1 if:
  cleanup_margin(step_t) > cleanup_margin(step_{t-1}) + delta_threshold
  AND cleanup_margin(step_{t-1}) < low_threshold

Interpretation: A frisson event occurs when a composition step that was previously hard to resolve (low cleanup margin = high prediction error) suddenly resolves with a large margin jump (sudden coherent resolution). The aesthetic score = count(frisson_events) / passage_length.

Rationale: This directly implements the temporal dynamic of musical frisson: expectation violation followed by resolution. The low_threshold gate ensures the resolution is genuinely surprising (not just a routine composition step). The margin jump threshold ensures genuine resolution rather than noise.

Testability: Laptop CPU, ~20 min. Requires a labeled passage set with human ratings and substrate cleanup margins computed at each composition step.

P_deflated estimate: 0.28 (theoretical basis is strong; empirical validation is the first gate)

#### D2.4 SEXUAL-SELECTION-EVOLUTIONARY (inter-substrate tournament)

Formulation: Two substrates generate candidate aesthetic outputs. A third substrate acts as "female chooser" -- it evaluates outputs by selecting the one it can more accurately complete or extend. Aesthetic fitness = win-rate in the tournament.

Rationale: This is the evolutionary game-theoretic mechanism for aesthetic quality. The chooser substrate's preference reveals which output is most informationally useful for completion/extension tasks -- an honest proxy for quality that is hard to Goodhart because it involves an adaptive adversary.

Implementation path: Requires two separate substrate instances (or one substrate used twice with different seeds). Passage A and B are presented to the evaluator substrate; whichever generates a lower cleanup margin on a held-out continuation is the winner. This maps onto Zahavi's honest signal: the substrate that actually carries more completion-useful information wins.

Known limitation: Computational cost is 3x single-substrate inference. More importantly, this measures "completion-utility" not "human aesthetic preference" -- these overlap but are not identical.

#### D2.5 CULTURAL-FITNESS-MEME (replication rate proxy)

Formulation: aesthetic_score(passage) = predicted retrieval frequency of passage given a random query distribution

Rationale: Cultural fitness of a meme = its retrieval rate from the cultural substrate when random needs arise. A passage that is frequently retrieved across diverse query contexts is "culturally fit" -- it carries information useful to many different downstream tasks. This operationalizes Dissanayake's view that art-making evolved for social cohesion by creating shared reference points.

Implementation: Compute the mean retrieval score of a passage across a distribution of query vectors (e.g., 100 random query vectors sampled from the passage neighborhood). High retrieval rate across diverse queries = high cultural fitness.

P_deflated: 0.20. This is a reasoned proxy but the gap between "useful reference" and "aesthetic quality" is large and poorly theorized.

#### D2.6 EMBODIED-MUSCLE-EMPATHY (motor simulation proxy)

Formulation: For text generation, model "motor simulation" as the substrate's sequential composition difficulty. The aesthetic experience of watching a skilled performance includes an internal simulation of the motor effort required. aesthetic_score = mean(composition_difficulty_per_step) where composition_difficulty is measured as the number of cleanup iterations required per step.

Rationale: High composition difficulty that nonetheless resolves = like watching a gymnast execute a hard move cleanly. Low difficulty = unskilled performance. Failed resolution = failed performance. This is the substrate analog of Freedberg-Gallese embodied simulation.

Known limitation: This is barely distinguishable from the skill_score in D2.1 with an inverted polarity. The theoretic novelty is modest; the implementation value is also modest.

#### D2.7 ASYMMETRY-DETECTION (structural balance)

Formulation: For a passage represented as a sequence of composition vectors, compute the "structural asymmetry" as the variance of cleanup-margin across composition steps. Low variance = high symmetry (monotonic quality throughout). High variance = high asymmetry (some parts much harder/easier than others).

Rationale: Fluctuating asymmetry in organisms reflects developmental noise. In a passage, high cleanup-margin variance reflects structural instability -- some parts are generically well-supported, others are idiosyncratic. Moderate asymmetry might indicate deliberate artistic variation; high asymmetry might indicate structural incoherence.

Known limitation: The evidence base for FA as an aesthetic signal in text is essentially zero. This is speculative extrapolation from biology to text. P_deflated: 0.12.

#### D2.8 NICHE-CONSTRUCTION-AESTHETIC (long-term environmental impact)

Formulation: aesthetic_score(passage) = change in substrate's retrieval distribution after passage is stored. A passage that meaningfully alters what the substrate finds relevant for a diverse query set is "aesthetically constructive" of the substrate's cognitive niche.

Rationale: Odling-Smee niche construction posits that fit organisms modify their environment in ways that make their genotype more likely to be reproduced. A great work of art literally changes what subsequent readers find beautiful (the niche-construction effect of great art is massive: Shakespeare changed what "beautiful English" means). The substrate version: a great stored item shifts the substrate's retrieval geometry in a way that benefits many downstream queries.

Implementation: Before and after storing a passage, compute mean retrieval score for a probe query set. Passages that improve retrieval quality on the probe set are "niche-constructive." This is expensive to compute but measurable.

P_deflated: 0.18 (the mechanism is real but the measurement cost is high and the aesthetic interpretation is indirect).

---

## D3. Five empirical tests (laptop CPU priority)

### Test 1: Frisson-proxy baseline (D2.3)
Setup: Take 50 short passages (100-200 tokens each) with human aesthetic ratings 1-10 (use publicly available creative writing datasets, e.g., WritingPrompts, or rate manually). Compute substrate cleanup margin at each composition boundary. Compute frisson_event count per passage. Compute Pearson r vs. human ratings.
Pre-reg: HARD-PASS r >= 0.40; HARD-FAIL r < 0.15. CPU, ~20 min.

### Test 2: Anomaly x skill composite (D2.1)
Setup: Same 50 passages. Compute anomaly_margin (mean distance from nearest stored prototype) and skill_score (cleanup accuracy). Compare product to each component alone for predicting human ratings (Kendall tau on ranking).
Pre-reg: HARD-PASS product improves tau >= 0.05 over best single component; HARD-FAIL product performs worse than better single component. CPU, ~20 min.

### Test 3: Compression-progress vs. static quality (D2.2)
Setup: Same 50 passages. Compute cumulative positive compression-progress. Compare to static average cleanup margin for predicting human ratings.
Pre-reg: HARD-PASS compression-progress r >= 0.35 AND outperforms static margin r; HARD-FAIL r < 0.15. CPU, ~20 min.

### Test 4: Evolutionary tournament discriminability (D2.4)
Setup: Create 25 passage pairs where one is human-rated higher (from rated set above). Use substrate as "chooser" -- run continuation task on both and pick the one with lower completion cleanup margin. Report fraction of pairs where substrate chooser selects the human-preferred passage.
Pre-reg: HARD-PASS >= 68% correct (chance 50%, this is ~2 sigma above chance at N=25); HARD-FAIL <= 52%. CPU, ~30 min.

### Test 5: Mode-collapse refutation (LLM baseline comparison)
Setup: Have an LLM (Pythia-160M or any available) generate 50 passages from the same prompts. Compute frisson-proxy, anomaly x skill, and compression-progress for LLM-generated passages vs. human-written passages from the rated set. If substrate scores are systematically higher for human vs. LLM passages (even when LLM text is rated as "high quality" by surface criteria), it provides evidence that the substrate metrics capture something not measured by LLM aesthetic proxies.
Pre-reg: HARD-PASS substrate metrics distinguish human creative vs. LLM-generated text at AUC >= 0.65; HARD-FAIL AUC <= 0.52. CPU, ~40 min (requires Pythia inference + substrate scoring).

---

## D4. Honest assessment of paths

Highest P path: D2.3 (PREDICTION-ERROR-CHILL) is theoretically the strongest. The frisson mechanism is the most well-validated in neuroscience (opioid, dopamine, temporal dynamics, cross-cultural). The substrate analog is implementable in an afternoon. P_deflated = 0.28 that this metric outperforms genre-match at r >= 0.40 on a 50-passage test.

Second path: D2.1 (ANOMALY x SKILL) is the simplest formulation and has the most direct connection to Berlyne's well-tested optimal-incongruity theory. P_deflated = 0.32 that the product form improves over either component alone.

Speculative but interesting: D2.4 (evolutionary tournament). The adaptive-adversary mechanism is a genuine architectural innovation that would be hard for LLMs to replicate without live opponents. P_deflated = 0.20.

Probably not worth pursuing first: D2.6 (embodied motor simulation) and D2.7 (asymmetry detection) are weakly motivated for text. D2.5 (cultural fitness) and D2.8 (niche construction) are interesting in principle but require expensive evaluation and the aesthetic interpretation is indirect.

The central honest assessment: substrate vs. LLM in aesthetics is not a capability race in the same domain. LLMs optimize rater-preference proxies at scale. A substrate could offer a structurally different aesthetic signal -- one grounded in prediction-error dynamics and honest-signal properties -- that is complementary rather than directly competitive. The niche is: aesthetic quality for text or structure where temporal dynamics and genuine surprise matter more than surface coherence. Generated music structure, narrative arc analysis, code elegance, scientific elegance -- domains where "looks good to a human rater" and "is genuinely surprising yet coherent" diverge.

---

## Cross-thread synthesis with prior entries

This drill is a new domain (aesthetics) not previously explored in the research notes. The prediction-error framing (Van de Cruys) is adjacent to the predictive processing work in prior thermal/entropy drills (the Jarzynski/NESS framing is also about departure from equilibrium followed by return). The compression-progress metric (Schmidhuber) is structurally analogous to the KL-divergence measurements already implemented in the substrate privacy harness (ZKL). The evolutionary tournament mechanism (D2.4) is analogous to the GAN adversarial training dynamics explored in C8.

Cap_map implications: this drill does not directly bear on current cap_map rows (which focus on retrieval quality, privacy, composition capacity). It opens a new potential row: aesthetic quality scoring as a substrate capability that could differentiate the product from LLM-only alternatives.

---

## Substrate-product implications

A substrate aesthetic scorer would be a lightweight add-on to existing retrieval/composition infrastructure. It requires no new model training -- only computing cleanup margins and their dynamics during existing composition operations. If validated (Tests 1-5), this would provide:

1. A differentiated aesthetic quality signal that is structurally resistant to Goodhart failure because it measures a dynamic property (margin trajectory) not a static feature (surface style).
2. An aesthetic quality evaluation tool that is interpretable (frisson events are locatable to specific composition steps) unlike LLM reward models.
3. A potential customer-facing feature: "aesthetic coherence score" as an output metric for creative generation tasks.

The substrate cannot currently generate text (it retrieves and composes). The aesthetic scoring mechanism would apply to evaluating retrieved/composed passages, not generating new text. The application is therefore as an aesthetic filter or ranking tool, not a generative aesthetic AI.

---

## Citations (verified count: 32)

1. Chatterjee & Vartanian (2014) -- neuroaesthetics review -- Brain
2. Blood & Zatorre (2001) -- music frisson fMRI -- PNAS
3. Ferreri et al. (2021) -- opioid system + music chills -- PMC7669983
4. Vessel, Starr & Rubin (2012) -- DMN aesthetic appeal -- PNAS 2012
5. Vessel & Isik (2019) -- DMN generalizes across visual domains -- PMC6754616
6. Van de Cruys & Wagemans (2011) -- tentative prediction error account -- i-Perception
7. Royal Society B special issue (2023) -- aesthetics and predictive processing -- RSTB 2022.0410
8. Berlyne (1971) -- Aesthetics and Psychobiology -- Appleton-Century-Crofts
9. Althuizen (2021) -- Berlyne U-shape revisited -- Psychology & Marketing
10. Schmidhuber (2009) -- compression progress theory -- Springer Lecture Notes
11. Schmidhuber formal theory (1990-2010) -- ResearchGate 224155374
12. Ramachandran & Hirstein (1999) -- science of art -- Journal of Consciousness Studies
13. Goldstein (1980) -- opioid blockade frisson -- Science (original)
14. Freedberg & Gallese (2007) -- embodied simulation aesthetics -- Trends in Cognitive Sciences
15. Gallese (2025) -- aesthetics and unconscious -- Journal of the American Psychoanalytic Association
16. Berlin & Kay (1969) -- basic color terms -- University of California Press
17. Darwin (1871) -- Descent of Man -- Murray
18. Zahavi (1975) -- handicap principle -- Journal of Theoretical Biology
19. Grafen (1990) -- game-theoretic proof of handicap -- Journal of Theoretical Biology
20. Ryan & Rand (1990) -- sensory exploitation tungara frogs -- Science
21. Endler & Basolo (1998) -- sensory trap model -- Trends in Ecology & Evolution
22. Thornhill & Gangestad (1994) -- fluctuating asymmetry -- Psychological Science
23. Endler et al. (2010) -- bowerbird forced perspective -- PNAS 1208350109
24. Keagy et al. (2009) -- bowerbird problem-solving predicts mating -- Animal Behaviour
25. Dalziell et al. (2013) -- lyrebird mimicry complexity -- Current Biology
26. Henshilwood et al. (2002) -- Blombos Cave ochre engravings -- Science
27. Stiner & Kuhn (2006) -- symbolic behavior cultural evolution -- Current Anthropology
28. Odling-Smee, Laland & Feldman (2003) -- Niche Construction -- Princeton
29. Schuhmann et al. (2022) -- LAION-Aesthetics -- laion.ai
30. arXiv 2601.09896 (2026) -- LAION aesthetic predictor audit
31. arXiv 2510.20091 (2025) -- CreativityPrism benchmark
32. arXiv 2604.13602 (2025) -- reward hacking in LLMs

---

## P estimates (calibrated, deflated 0.15-0.25)

- D2.3 FRISSON-PROXY predicts human ratings at r >= 0.40: P_deflated = 0.28
- D2.1 ANOMALY x SKILL product improves over components: P_deflated = 0.32
- D2.4 EVOLUTIONARY TOURNAMENT >= 68% correct: P_deflated = 0.20
- LLM aesthetic proxies miss frisson-proxy signal (Test 5 AUC >= 0.65): P_deflated = 0.35
- Substrate aesthetic scoring becomes a product-differentiating feature (post-Test 1-5 validation): P_deflated = 0.18

Next-drill candidate: sensory bias exploitation in text (Endler/Ryan model applied to text: what pre-existing biases in human text comprehension do LLM-generated and substrate-retrieved texts exploit? Adjacent to predictive processing A3 and evolutionary B3 streams.)
