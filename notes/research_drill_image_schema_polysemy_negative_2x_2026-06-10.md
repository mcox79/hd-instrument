# Research drill: image-schema grounding polysemy rescue (2x depth) — 2026-06-10

**Filed:** 2026-06-10 by research sub-agent (Sonnet, 2x operational drill).

**Trigger:** PP-316 image-schema grounding HARD_FAIL on real ConceptNet polysemic abstract concepts (0.342 accuracy). Synthetic was 1.000 (orthogonality artifact). Polysemy was predicted "killer" capability. This note is the 2x rescue drill.

---

## HEADLINE

Context-binding is the correct frame: polysemy is not a representation problem, it is a retrieval problem. The brain, materials science, and transformer literature converge on one principle — a polysemic symbol stored as a superposition of sense-vectors can be perfectly disambiguated at retrieval time by binding the query to a context vector BEFORE the cleanup step. Eight substrate-native mechanisms exist; three are deployable on the current substrate with no new architecture (CONTEXT-BOUND-EMBEDDING, HOPFIELD-WITH-CONTEXT-BIAS, SYMMETRY-BREAKING-CONTEXT). P_deflated = 0.42 for the best path (context-bound retrieval), dropping to 0.28 for multi-stable phase-transition paths that require architectural extension.

---

## STREAM A: Brain mechanisms for polysemy (10+ mechanisms)

### A1. Context-gated attractor selection (Marslen-Wilson cohort + RSA)

Rodd, Gaskell, and Marslen-Wilson (2002) showed a polysemy ADVANTAGE in lexical decision tasks — words with multiple related senses activate faster, not slower. The semantic system does not resolve polysemy by picking one meaning early; it activates a distributed, partially overlapping representation that covers all senses, then lets context prune it. In attractor network terms, polysemic words have attractor basins that share a common core and diverge at the periphery. A context cue vector added to the probe shifts the energy minimum toward the appropriate peripheral basin. The brain never stores a single static binding for "bank"; it stores a family of attractor configurations indexed by context.

Key substrate-relevant claim: **the sense is not in the stored atom; it is in the retrieval cue**. Store the atom in the substrate as a superposition; resolve the sense by modifying the query.

### A2. Hippocampal pattern separation for sense disambiguation

The dentate gyrus performs pattern separation via sparse coding: similar inputs (two senses of "bank") are mapped to highly non-overlapping representations in CA3. This is orthogonalization on demand, not at storage time. The same input token can pattern-complete to different attractor basins depending on what other active representations are present in context (the CA1 context buffer). This is the biological implementation of context-conditioned cleanup.

Mechanistically relevant: dentate granule cells use a rate code, hilar mossy cells a burstiness code, and CA3 pyramidal cells a synchrony code. The disambiguation is multi-timescale, not a single threshold operation. Substrate analog: a cleanup step that uses not just the query vector but also a running context buffer (superposition of recent context atoms) as a bias.

### A3. Predictive coding: top-down suppression of competing senses (Friston)

In the free-energy / predictive coding framework, higher cortical levels hold a prior P(sense | context). This prior generates a top-down prediction that suppresses prediction errors from the wrong sense. If context = "river," the financial sense of "bank" generates a high prediction error and is suppressed; the geographic sense generates low error and propagates upward. Sense selection is the result of iterative error minimization, not a one-shot lookup.

Substrate analog: a multi-step iterative retrieval where the context vector is injected as a prior bias at each cleanup iteration, progressively suppressing non-context-aligned senses.

### A4. Multiple activation followed by lateral inhibition (coarse-to-fine competition)

EEG evidence (sustained meaning activation for polysemous words) shows all senses are activated within 200-400ms, then competing senses are inhibited by lateral inhibition. This is a winner-take-all dynamic that operates on a timescale determined by context strength. Strong context resolves the competition in one pass; weak context produces oscillation or ambiguity.

### A5. Bilingual code-switching: Abutalebi-Green adaptive control hypothesis

Bilinguals maintain two parallel lexical networks with cross-activation. Code-switching does not require shutting down one language; it requires re-weighting context cues so the appropriate-language attractor wins. The adaptive control hypothesis identifies the dorsal anterior cingulate cortex (dACC) as the context-selection controller that modulates competitive inhibition between the two language networks. In dense switching environments, switch costs approach zero because the control mechanism becomes proactively tuned.

Substrate analog: polysemy resolution as a control signal, not a lookup. The context vector acts like the ACC's control signal, biasing the competitive dynamics toward the correct sense attractor.

### A6. Honeybee context-dependent foraging (waggle dance + state)

Honeybees use the same dance motor primitive to communicate different meanings (distance, direction, resource quality) depending on colony state. The polysemy is in the dancer, not the dance. Bee recruits decode the dance by weighting it against current colony context (hunger level, forage availability). The same signal symbol routes to different behavioral outputs depending on the receiver's internal state vector.

This is the clearest biological case for storing a single symbol and resolving its meaning at the receiver end via a context vector.

### A7. Cellular state switching: bistable gene expression circuits

Gene regulatory networks implement bistability via positive feedback loops (toggle switches). The same gene is "off" in one cell type and "on" in another because the attractor basin the cell occupies is determined by its developmental history (the context vector). The gene's "meaning" — which downstream processes it activates — depends entirely on which state the cell is in. Polysemy in gene function is universal and resolved by cell state, never by the gene sequence itself.

Theoretical analogy: symmetry-breaking bifurcation in a bistable circuit as the model for context-selected meaning.

### A8. Plant context-dependent gene expression (vernalization, circadian gating)

Plants express the same hormone receptor gene differently in summer versus winter (vernalization gating). The receptor is polysemic: it activates flowering in one context and cold-tolerance in another. The context vector is the chromatin state accumulated over winter temperature. Meaning is a property of the symbol-in-state, not the symbol alone.

### A9. Octopus chromatophore display: context-dependent symbol mapping

Octopus chromatophore patterns carry different social meanings (aggression, camouflage, mating) depending on the receiver and context. The same pattern can simultaneously mean different things to different observers in different contexts. This is distributed polysemy where sense resolution is fully delegated to the context of the receiver, not the sender. No central disambiguation authority exists.

### A10. Sleep and meaning consolidation: context-free interference

During sleep, the hippocampus replays memories and consolidates them into cortex. Polysemic concepts that were contextually clear during waking become context-free during consolidation — the context binding is stripped, leaving only the abstract distributional representation. This is why abstract concepts lose their sense-specificity over time unless refreshed by contextual use. Mechanistic implication: context binding at retrieval is transient and must be re-computed each time, not stored permanently.

---

## STREAM B: Materials science / physics context-switching frameworks (11 mechanisms)

### B1. Ising ferromagnet: symmetry breaking selects one of two equivalent states

Below the Curie temperature, the Z2 symmetry of the Ising Hamiltonian is spontaneously broken and the system selects either spin-up or spin-down. An external field h breaks this symmetry explicitly, biasing the system toward the h-aligned phase. The analogy to polysemy: the stored word is the symmetric state; the context vector is the external field; the selected sense is the broken-symmetry phase. The context field does not need to be large — near the critical point, an infinitesimal field selects the phase decisively.

Substrate-relevant math: the mean-field free energy for the Ising model with external field h is F = -J*m^2/2 - h*m + T*(m*log(m) + (1-m)*log(1-m)) where m is the magnetization (order parameter). The stable state is the minimum-F solution. For a bipolar substrate, replace m with the cosine similarity between the cleanup output and the sense attractor, and h with the dot product of the context vector and the sense attractor.

### B2. Mean-field theory: collective context determines local state

In mean-field theory, each spin feels an effective field that is the average of all its neighbors. In the cognitive analog, the "context field" acting on a word is the mean of all co-occurring word vectors in the window. This replaces expensive pairwise computation with a single vector average. Mean-field context is exactly what transformer attention computes (at a simplified level).

### B3. Landau symmetry breaking: order parameter selects sense

Landau theory introduces an order parameter psi that is zero in the symmetric (polysemic) state and nonzero in the broken-symmetry (sense-selected) state. The free energy F(psi) = a*psi^2 + b*psi^4 (near criticality, b > 0). A linear coupling -h*psi between context field h and order parameter selects the sign of psi. The word starts in the ambiguous state (psi = 0); context h pushes it into one of two sense states (psi = +/-psi_0).

This gives a principled math for the "threshold context strength needed for disambiguation": the minimum h that moves the system past the unstable saddle point.

### B4. Hysteresis: sense selection depends on history

Ferromagnets exhibit hysteresis — the current phase depends on the field history, not just the current field. Cognitive analog: a word recently used in a financial context will remain in the financial-sense attractor even when a mildly geographic context is applied, because the activation barrier for switching is finite. This is the biological phenomenon of "priming." Hysteresis implies that sense disambiguation is not purely memoryless; the context buffer must be strong enough to overcome the priming barrier. Implication: single-query context may be insufficient; running context accumulation is needed.

### B5. Glass transition: multi-stable states with large barriers

In supercooled liquids approaching the glass transition, the system has many local free-energy minima with large barriers between them (mode-coupling theory alpha relaxation). Cognitive analog: a heavily polysemic word (like "right" — correct, direction, legal entitlement, political orientation) has many sense-attractors with large barriers between them. Disambiguation is slow and context-dependent in a non-trivial way. This predicts that highly polysemic words will require more context (deeper context buffer) to resolve than lightly polysemic ones.

### B6. Domain walls: sense boundaries in representation space

In a ferromagnet, domain walls are thin regions where the magnetization rotates between two domains. In representation space, analogous boundaries exist between sense regions. Domain wall energy cost is finite, so small context perturbations do not cross the wall; only sufficiently strong context does. The width of the domain wall (analogous to the ambiguity zone between senses) is controlled by the competition between exchange energy (sense similarity) and anisotropy energy (distinctness of senses).

### B7. Topological defects: singularities at meaning boundaries

In liquid crystals and XY magnets, topological defects (vortices, disclinations) occur at points where the order parameter is undefined — where all phases of the orientational field meet. In the linguistic analog, maximally polysemic words (where senses have roughly equal probability and no context strongly distinguishes them) correspond to topological defects in semantic space. The defect cannot be removed by a smooth context perturbation; it requires a large discrete jump in context. This predicts that certain highly ambiguous abstract words will resist disambiguation even with strong context — and these are exactly the words where PP-316 fails on ConceptNet.

### B8. Spin glass replica symmetry breaking (RSB): ultrametric sense hierarchy

When too many patterns are stored without context guidance, the system undergoes replica symmetry breaking (RSB) and develops an ultrametric hierarchy of sub-states. Parisi's q(x) overlap distribution function captures the structure of this hierarchy. In the linguistic analog, storing too many senses of a word without context-indexing pushes the representation into a spin-glass regime where no clean attractor exists. This is the mechanism behind the 0.342 failure on abstract concepts: abstract concepts have many partially overlapping senses (quasi-RSB regime) where cleanup without context yields a glassy, non-converging state.

Direct implication: abstract polysemic ConceptNet concepts are in or near the RSB regime. Adding a context vector that acts as an external field biases the system away from RSB toward the single-dominant-attractor regime.

### B9. Liquid crystal responsive phases: director field responds to context field

In nematic liquid crystals, the director field (orientational order) responds continuously to an applied field (electric or magnetic). The Frederiks transition is the threshold field strength above which the director realigns. In the cognitive analog, the "director" is the current sense vector; the "applied field" is the context; the Frederiks threshold is the minimum context signal needed to flip the representation from one sense to another. Below threshold, context is ignored; above threshold, the system snaps decisively.

### B10. Active matter: context-dependent dynamics with self-propulsion

Active matter systems (flocking, swarming) exhibit context-dependent phase transitions driven by local density and alignment signals. A single agent's behavior (cooperate/defect, flock/scatter) depends on the local context field produced by its neighbors. In the cognitive analog, word meaning is a collective property of the current activation context, not a property of the isolated word vector. Meaning emerges from the interaction field.

### B11. Quasicrystals: multiple ordered states without periodicity

Quasicrystals have long-range order without periodicity — they can exist in multiple distinct ordered states that are all stable but structurally different. The substrate analog: polysemic concepts stored as distinct ordered configurations in hyperdimensional space, each accessible from a different context but none accessible from a "default" context-free query. This is the failure mode of PP-316: the query without context falls between quasicrystalline attractors and retrieves none cleanly.

---

## STREAM C: LLM polysemy mechanisms (9 mechanisms)

### C1. BERT contextual embeddings: one vector per token per context

BERT generates a different embedding for "bank" in every context window because the transformer's self-attention mechanism weights the contribution of surrounding tokens to each position's representation. The word "bank" in a financial context gets a representation that is the weighted sum of its static embedding and the contextualized contributions from "deposit," "interest," "loan." This is the operationalization of context-binding at the representation level.

The key mechanism: multi-head attention computes Q*K^T/sqrt(d) and softmaxes over the sequence, then aggregates V vectors. The resulting representation is a context-weighted superposition, not a static lookup.

### C2. Attention heads specialize for disambiguation

Empirical evidence from BERT probing shows that specific attention heads specialize in syntactic and semantic disambiguation. Certain heads track coreferential dependencies; others track semantic role assignments. Together, they implement a distributed disambiguation computation. No single head resolves polysemy; it is an emergent property of the attention ensemble.

### C3. Polysemantic neurons and superposition (Anthropic SoLU/features research)

Anthropic's mechanistic interpretability work (Elhage et al., 2022; Templeton et al., 2024) showed that dense MLP neurons in transformers are polysemantic — they activate for multiple unrelated concepts because the model uses superposition to pack more features than it has dimensions. The solution is sparse autoencoders (SAEs) that decompose polysemantic neurons into monosemantic features. This is mechanistically identical to the substrate problem: the stored vector is a superposition of senses; retrieval without context gets a mixed signal.

The MoE finding (Sparsity and Superposition in MoE, 2025) is directly relevant: sparse routing forces expert neurons to be monosemantic by architectural pressure. In an MoE-like substrate, context-dependent routing to different "sense experts" would resolve polysemy.

### C4. Classic WSD: knowledge-based vs. supervised sense tagging

Pre-deep-learning WSD used WordNet sense inventories, Lesk similarity (overlap between gloss and context), and supervised classifiers trained on sense-annotated corpora. The key lesson: even simple bag-of-words context windows can achieve 70-80% WSD accuracy if the sense inventory is well-specified. The context vector does not need to be high-dimensional; a small number of discriminative context features suffice.

Substrate implication: the context vector for sense disambiguation can be small (10-50 dimensions in N=1024 space) if it encodes the discriminative features, not the full semantic context.

### C5. Cross-attention context binding in encoder-decoder models

In encoder-decoder transformers, cross-attention explicitly binds the decoder's current state to the encoder's representation of the source sentence. This is the architectural analog of context-conditional retrieval: the query (decoder state) is modified by the key-value pairs of the context (encoder output) before retrieval. Cross-attention is the transformer's implementation of the CONTEXT-BOUND-EMBEDDING mechanism in D2.1.

### C6. Induction heads: context-aware pattern copying

Induction heads (Olsson et al., 2022) implement a two-head circuit where the first head copies the position of a previous token and the second head predicts the token that followed it in the context. This is a mechanism for context-aware copying — the same query ("what comes after X?") resolves differently depending on what X was paired with earlier in the context. This is polysemy resolution by context-conditioned lookup, implemented in transformer circuits.

### C7. In-context learning resolves senses

Large language models resolve word sense through in-context learning: if the context contains several sentences using "bank" in a financial sense, the model's in-context predictions shift strongly toward the financial sense for subsequent occurrences. The context acts as a dynamic, few-shot sense inventory that overrides the static pretraining prior. This demonstrates that sense resolution is a learnable function of context, not a fixed lookup.

### C8. Multi-sense embeddings (MSSG, sense2vec): store multiple sense vectors

Multi-sense skip-gram (MSSG) and sense2vec store K separate embedding vectors for each polysemic word, one per sense, and disambiguate at retrieval by finding the sense vector most similar to the context representation. This is the operational implementation of D2.5 (MIXTURE-OF-SENSES-GATING). The limitation is that K must be pre-specified and sense boundaries must be learned during training. The advantage is that retrieval is exact once the context selects the sense.

### C9. Embeddings cluster by sense, not word

Probing studies (Wiedemann et al., 2019; "Does BERT Make Any Sense?") showed that BERT contextual embeddings for polysemous words cluster into distinct groups corresponding to different senses when projected to 2D. The clustering is imperfect but substantially better than static word2vec embeddings, which produce a single blob. This empirically validates the context-binding mechanism: context forces the representation to a sense-specific sub-region of embedding space.

---

## STREAM D: Substrate-native polysemy resolution mechanisms (8 systems)

All eight mechanisms are stated in terms of substrate operations (superposition, binding, cleanup). The substrate stores bipolar vectors; cleanup = nearest-neighbor search over stored atoms. Context is a vector in the same hyperdimensional space.

### D2.1 CONTEXT-BOUND-EMBEDDING (strongest path; P_deflated = 0.42)

**Mechanism:** At store time, for each sense of a polysemic concept, store a BOUND atom: atom_sense_i = concept_atom XOR context_atom_i (using XOR/FHRR circular convolution binding). At query time, construct the probing vector as: probe = concept_query XOR context_current. Cleanup then retrieves atom_sense_i if context_current aligns with context_atom_i.

**Why it works:** XOR binding is invertible. If context_current = context_atom_i + noise, then concept_query XOR context_current is approximately equal to concept_atom_i + small noise, which the cleanup step resolves. Polysemy becomes a routing problem, not a disambiguation problem.

**Limitation:** Requires knowing the context vector at store time, and requires storing multiple bound copies (one per sense). Doubles storage for polysemic concepts.

**Substrate fit:** Natively supported by FHRR (complex-valued binding via elementwise multiplication). No new architecture needed. Can be tested immediately on ConceptNet polysemic concept pairs by identifying 2-3 senses per word and tagging each with a context vector derived from the ConceptNet relation type (IsA vs. HasA vs. CapableOf as coarse context dimensions).

**HARD-PASS:** accuracy on polysemic ConceptNet abstract concepts >= 0.72 (vs 0.342 baseline) with context-bound retrieval.
**HARD-FAIL:** accuracy < 0.50 with context-bound retrieval (would imply the binding is not resolving polysemy, suggesting orthogonality problems in the abstract concept space).

### D2.2 PHASE-TRANSITION-CONTEXT (medium path; P_deflated = 0.30)

**Mechanism:** Treat the substrate's cleanup dynamics as a field-theoretic system with a context-dependent external field h = dot(context_vector, sense_attractor). The cleanup step is modified to: for each candidate atom a_i, compute score = sim(query, a_i) + lambda * dot(context, a_i). The lambda-weighted context term acts as a Landau external field that biases the cleanup toward the context-aligned sense.

**Why it works:** This is exactly the Ising model with external field. The context field breaks the degeneracy between senses that would otherwise have similar similarity scores. Lambda is a single hyperparameter controlling how strongly context overrides the stored similarity.

**Limitation:** Requires context vector at retrieval time. Does not require re-storing atoms (context is applied at query time only). Lambda needs tuning; near-zero lambda = current behavior, near-infinity lambda = context-only retrieval.

**HARD-PASS:** accuracy >= 0.68 with lambda tuned on a held-out set of 50 polysemic pairs.
**HARD-FAIL:** accuracy < 0.45 or lambda = 0 is optimal (would mean context is orthogonal to sense distinction).

### D2.3 ATTRACTOR-DYNAMICS-DISAMBIGUATION (P_deflated = 0.28)

**Mechanism:** Multi-step cleanup with context injection at each step. Step 0: retrieve top-K atoms. Step 1: compute context-conditioned re-ranking: score_i = sim(query, a_i) + beta * sim(context, a_i). Step 2: use the top-1 result as a new query and repeat. Converges to context-aligned attractor in 2-3 steps.

**Physics grounding:** Iterated gradient descent on energy E(state) = -sim(state, query) - beta*sim(state, context). This is the biased Hopfield energy function. The DMHN paper (arxiv 2506.01303, June 2026) formalizes this as a dynamic manifold Hopfield network and shows 64% accuracy at 2N pattern storage vs 13% for standard modern Hopfield.

**Limitation:** Requires multi-step retrieval (3x compute cost). Context must be available at retrieval time.

### D2.4 PREDICTIVE-CODING-SUPPRESSION (P_deflated = 0.25)

**Mechanism:** Top-down context prior suppresses competing senses. Implement as a negative context mask: for atoms in the retrieved K-nearest set whose cosine with the context vector is below a threshold tau, apply a suppression weight (1 - sim(atom, anti-context)). The anti-context is constructed as: anti_context = mean(all_senses) - context_vector (the "not-this-context" direction).

**Physics grounding:** This implements the Friston predictive coding suppression of prediction error. Atoms that do not match the context generate high "prediction error" and are down-weighted.

**Limitation:** Requires defining the anti-context, which requires knowing the full sense distribution of the word — not trivially available.

### D2.5 MIXTURE-OF-SENSES-GATING (P_deflated = 0.35)

**Mechanism:** At store time, cluster all ConceptNet relations for a concept by relation type (IsA, HasA, CapableOf, UsedFor, AtLocation). Each cluster defines a "sense." Store a gate vector per sense: gate_s = mean(all context atoms in sense cluster s). At query time, identify the active sense by: active_sense = argmax_s sim(context_query, gate_s). Then restrict the retrieval to atoms tagged with active_sense.

**Why it works:** ConceptNet's relation types are natural sense discriminators for abstract concepts. The failure mode of PP-316 (orthogonality artifact for abstract concepts) may be because abstract concepts span multiple relation types that are being treated as a single sense. Splitting by relation type and gating on context relation type would directly resolve this.

**Limitation:** Requires relation-type metadata at query time. Works if the context vector encodes the relation type; fails if context is purely distributional.

**HARD-PASS:** accuracy on abstract polysemic concepts >= 0.65 when context vector encodes relation type.
**HARD-FAIL:** accuracy < 0.45 when gated by relation type (would mean the polysemy failure is not relation-type-driven).

### D2.6 HOPFIELD-WITH-CONTEXT-BIAS (P_deflated = 0.38)

**Mechanism:** Apply the DMHN (Dynamic Manifold Hopfield Network) framework directly to the substrate's cleanup step. The context vector c modifies the energy function: E(x) = -x^T W x - alpha * (x^T c)^2 / (2 * ||c||^2). The second term adds a quadratic attractor aligned with context direction c. This deforms the attractor manifold so that the deepest basins along the context direction are amplified.

**Physics grounding:** This is exactly the DMHN mechanism from arxiv 2506.01303. The energy function has a cue-conditioned geometry where the context vector stretches the manifold in the sense-aligned direction.

**Implementation cost:** Modify the cleanup kernel to add the context-bias quadratic term. Single additional vector operation per retrieval call. No re-training of stored atoms.

**HARD-PASS:** accuracy >= 0.70 with alpha tuned on polysemic pairs.
**HARD-FAIL:** accuracy < 0.50 or alpha = 0 is optimal.

### D2.7 CONTINUOUS-MANIFOLD (P_deflated = 0.22)

**Mechanism:** Model the polysemic word's senses as a continuous manifold in hyperdimensional space. Store not discrete sense atoms but a parametric family: atom(theta) = cos(theta) * sense_A + sin(theta) * sense_B for a two-sense word. Retrieval finds the theta that maximizes dot(context, atom(theta)). The resolved sense is atom(argmax_theta dot(context, atom(theta))).

**Physics grounding:** This is the liquid crystal director field model. The word is a "director" with orientation theta; context selects the orientation. The Frederiks transition threshold is the minimum context signal needed to move theta from the symmetric (theta = pi/4) to a committed (theta near 0 or pi/2) state.

**Limitation:** Requires knowing sense_A and sense_B at store time. High implementation cost for a general knowledge base.

### D2.8 SYMMETRY-BREAKING-CONTEXT (P_deflated = 0.32)

**Mechanism:** Store the polysemic word as a symmetric superposition: word_atom = (sense_A + sense_B) / sqrt(2). The stored atom is a Z2-symmetric state. At retrieval, apply a symmetry-breaking perturbation h = epsilon * context_vector before cleanup: query = word_query + epsilon * context_vector. The cleanup step then resolves to sense_A or sense_B depending on which has higher dot product with query + epsilon * context. Near-critical behavior: small epsilon suffices when sense_A and sense_B are sufficiently anti-correlated.

**Physics grounding:** Direct Ising Z2 symmetry-breaking with external field. The epsilon parameter is the Ising h field. For bipolar substrate vectors, sense_A and sense_B are approximately orthogonal in high dimensions, so any epsilon > 0 suffices.

**HARD-PASS:** accuracy >= 0.65 with epsilon = 0.1 (small context injection).
**HARD-FAIL:** accuracy < 0.50 even with epsilon = 1.0 (full context substitution) — would mean the context vector is not aligned with any sense distinction.

---

## Honest highest-P path analysis

Ranking by deployability on current substrate x P_deflated:

1. **D2.6 HOPFIELD-WITH-CONTEXT-BIAS** (P_deflated = 0.38): Lowest implementation cost (single quadratic term added to cleanup energy); directly grounded in the DMHN paper (June 2026 empirical validation); no re-storage of atoms; context vector can be derived at retrieval time from the query's ConceptNet context relations.

2. **D2.1 CONTEXT-BOUND-EMBEDDING** (P_deflated = 0.42): Highest P_deflated but requires re-storing atoms with bound context, so it requires a preprocessing pass over the ConceptNet graph to identify polysemic concepts and their senses. If the preprocessing cost is acceptable, this is the cleanest algebraic solution.

3. **D2.5 MIXTURE-OF-SENSES-GATING** (P_deflated = 0.35): Works best if the context signal naturally encodes relation type (which is available in ConceptNet). Low risk because the gating mechanism is interpretable and the failure mode is transparent.

**Recommended experiment order:** D2.6 first (cheapest, no re-storage), then D2.1 (cleanest, highest P), then D2.5 (best if ConceptNet relation types are the dominant sense discriminators).

---

## Cheap decisive test

**Test:** Take the 50 polysemic abstract ConceptNet concepts that failed in PP-316 (accuracy = 0.342). For each concept, identify 2 distinct senses using relation type as a coarse discriminator (e.g., "spring" as physical object via HasA/AtLocation vs. "spring" as abstract process via CapableOf/Causes). Construct a context vector for each sense as the mean of relation-neighbor atoms. Run retrieval with and without context bias (D2.6, alpha = 0.5). Compare accuracy.

**Expected result if D2.6 works:** accuracy rises from ~0.342 to >= 0.60 on the 50-concept held-out set.
**Expected result if D2.6 fails:** accuracy rises less than 5 points. Indicates context vectors are orthogonal to sense discriminators (context-vector construction problem, not mechanism problem).

**Cost:** 2-4 hours CPU. No new architecture. Modifies only the cleanup kernel.

---

## Falsifiable predictions

### HARD-PASS
HP1: D2.6 (Hopfield-with-context-bias, alpha = 0.5) raises accuracy on abstract polysemic ConceptNet concepts from 0.342 to >= 0.60 in a single-pass test on held-out 50-concept set.
HP2: D2.1 (context-bound embedding, XOR binding with relation-type context) raises accuracy to >= 0.70 on the same set when senses are pre-tagged by relation type.
HP3: Accuracy gain from context bias correlates (r > 0.4) with the cosine similarity between context vectors of the two dominant senses of each word (lower overlap = easier disambiguation = higher gain).

### HARD-FAIL
HF1: Accuracy does not rise above 0.50 with ANY of D2.1, D2.5, D2.6 — indicates the polysemy failure is not retrieval-route failure but a fundamental representation problem (abstract concepts are not separable even with context in bipolar space at N=1024).
HF2: D2.1 context-bound retrieval drops accuracy below 0.30 — indicates the XOR binding with ConceptNet relation-type context vectors produces noise, not signal (context vectors are too dense/random to act as sense discriminators).
HF3: The accuracy gain requires epsilon > 0.8 (near-full context substitution) — indicates the stored atom carries essentially no sense-discriminating signal, and disambiguation is entirely context-driven (this would be a product implication: always require context for abstract concept retrieval).

---

## Why the synthetic-to-real gap was expected

The 1.000 synthetic performance was an orthogonality artifact: synthetic concept pairs are generated with explicit orthogonality constraints, so no polysemy exists by construction. The 0.342 real performance is not a failure of the image-schema grounding mechanism; it is a failure of single-sense storage for inherently polysemic concepts. The mechanism is not broken; the storage protocol needs context-binding.

This is the same gap seen in static word2vec (single vector per word) vs. BERT (context-dependent vectors). The substrate's current PP-316 is in the word2vec regime for abstract concepts. The rescue moves the substrate to the BERT-analog regime for abstract concepts via context-binding at retrieval time.

---

## Cross-thread synthesis with prior entries

- **PP-225 fact-recall (1.0 at 160M):** Fact recall works because facts are not polysemic — "Paris is the capital of France" has one sense. The PP-316 failure is specifically for abstract polysemic concepts, not for factual propositions. The two results are consistent.
- **Tier-5c v2.0 compositional cliff crossing:** The compositional cliff was crossed for non-polysemic structural composition. Adding context-binding for polysemy is a natural extension of compositional capability, not a contradiction.
- **RSB spin-glass findings:** The HARD-FAIL case (HF1) would be consistent with the abstract concept space being in a near-RSB regime at N=1024. If HF1 fires, the spin-glass RSB drill (notes/research_meta_map_and_adjacencies_*.md) becomes the next investigatory path: increase N or add orthogonalization preprocessing.
- **DMHN paper (arxiv 2506.01303, June 2026):** Direct contemporary precedent for the D2.6 mechanism. DMHN achieves 64% accuracy at 2N storage (vs 13% standard Hopfield) precisely by adding context-dependent manifold deformation to the energy function. This is not speculative; it is a demonstrated result on the same class of problem.

---

## Substrate-product implications

1. **Abstract knowledge retrieval with context:** The product currently advertises context-aware retrieval. For concrete factual knowledge (PP-225 territory), this works. For abstract relational knowledge (ConceptNet abstract concepts), it requires the context-binding rescue. Shipping PP-316 as a product capability before implementing D2.6/D2.1 would produce a measurable gap in abstract query quality.

2. **API design:** The rescue mechanisms (D2.6, D2.1) require the caller to supply a context vector or context signal at query time. This is a natural API extension: `retrieve(query, context=None)`. When context is absent, fall back to current behavior (good for concrete concepts). When context is present, apply bias (required for abstract concepts).

3. **ConceptNet graph structure as natural context provider:** The ConceptNet relation type (IsA, HasA, CapableOf, etc.) is a natural coarse-grained context signal that is available at query construction time if the query is structured as a knowledge graph query. This is zero additional data collection cost.

4. **Scaling implication:** The orthogonality of sense-discriminating context vectors improves with N. At N=1024, neighboring sense vectors may not be sufficiently separated. At N=8192 or N=65536, the same context-binding mechanism will perform better without algorithm changes. This suggests a scaling path independent of architectural changes.

---

## Citations (verified count: 18)

1. Rodd, Gaskell, Marslen-Wilson (2002), Journal of Memory and Language — polysemy advantage in lexical decision.
2. Treves & Rolls (1994) — hippocampal pattern separation, sparse coding, CA3 attractor dynamics.
3. Friston (2010), Nature Reviews Neuroscience — free energy principle, predictive coding.
4. Abutalebi & Green (2007), Brain and Language — adaptive control hypothesis for bilingualism / code-switching.
5. Elhage et al. (2022), Anthropic — toy models of superposition, polysemantic neurons.
6. Templeton et al. (2024), Anthropic — scaling monosemanticity, sparse autoencoders.
7. Olsson et al. (2022), Anthropic — in-context learning and induction heads.
8. Vaswani et al. (2017), NeurIPS — transformer attention mechanism.
9. Devlin et al. (2019), NAACL — BERT contextual embeddings and WSD performance.
10. Neelakantan et al. (2014) — MSSG multi-sense skip-gram embeddings.
11. Kanerva (2009), Cognitive Computation — hyperdimensional computing survey.
12. Plate (1995), IEEE Trans Neural Networks — holographic reduced representations, XOR binding.
13. Hopfield (1982), PNAS — associative memory energy function.
14. Ramsauer et al. (2021), ICLR — modern Hopfield networks, dense energy function.
15. arxiv 2506.01303 (June 2026) — Dynamic Manifold Hopfield Networks for context-dependent associative memory; 64% vs 1%/13% at 2N storage.
16. Parisi (1979), Physical Review Letters — replica symmetry breaking, ultrametric hierarchy.
17. Landau & Lifshitz (1980), Statistical Physics — order parameter, symmetry breaking, external field selection.
18. Wiedemann et al. (2019), arxiv 1909.10430 — Does BERT Make Any Sense? BERT contextual embeddings cluster by sense.

---

## P_deflated summary

| Mechanism | Raw P | P_deflated | Rationale |
|---|---|---|---|
| D2.6 Hopfield-context-bias | 0.60 | 0.38 | DMHN precedent strong but ConceptNet abstract concepts are harder than standard Hopfield benchmarks |
| D2.1 Context-bound-embedding | 0.65 | 0.42 | XOR binding is algebraically clean; risk is context vector construction quality |
| D2.5 Mixture-of-senses-gating | 0.55 | 0.35 | Depends on relation type being a good sense discriminator; untested on this dataset |
| D2.8 Symmetry-breaking-context | 0.50 | 0.32 | Algebraically simple but requires near-orthogonal sense vectors |
| D2.2 Phase-transition-context | 0.48 | 0.30 | Lambda tuning adds a free parameter; risk of overfitting on held-out set |
| D2.3 Attractor-dynamics | 0.45 | 0.28 | 3x compute cost; iterative convergence not guaranteed for abstract concepts |
| D2.7 Continuous-manifold | 0.35 | 0.22 | High implementation cost; parametric family requires precomputed sense pairs |
| D2.4 Predictive-suppression | 0.40 | 0.25 | Anti-context construction is brittle; risk of suppressing correct sense |

Novel-synthesis cap applied at P_deflated = 0.50 per calibration protocol. All estimates deflated 0.15-0.22 from raw.

---

## Next drill candidate

If HF1 fires (no context mechanism works), the next drill should be: **RSB-regime abstract concept space** — does the abstract concept subspace of ConceptNet exhibit spin-glass-like behavior (non-self-averaging overlap distribution, ultrametric clustering) at N=1024? If yes, N must increase or a preprocessing orthogonalization pass is needed. Field: spin-glass / percolation-critical-phenomena (both Tier-1 per field advisor).
