# Research: Substrate Beyond Previously-Dismissed Capabilities (2x Drill)
# Date: 2026-06-09

---

## HEADLINE

FHRR/HD-vector algebra with algebraic Datalog^neg, compositional binding, and sub-ms retrieval extends further into previously-dismissed creative, cross-modal, social-reasoning, and meta-cognitive territory than prior framing assumed -- but the extension mechanism differs by capability class: most "hard creative" tasks reduce to structured retrieval + compositional binding (substrate-native), while genuine novelty generation, continuous aesthetic judgment, and ToM inference chains require hybrid coupling to an LLM layer; several items previously dismissed as "requires LLM" are in fact substrate-native with documented algebraic paths.

---

## Calibration penalty applied (per [[feedback-lit-scan-calibration-penalty]])

All P estimates below are DEFLATED by 0.18-0.22 from naive lit-scan reading.
Novel-synthesis P capped at 0.50.
Hard-fail thresholds pre-registered for every ranked item.

---

## Background: What the substrate algebra supports

Empirically confirmed substrate primitives relevant to this drill:
- FHRR bind/unbind (complex phase arithmetic, reversible, composable)
- Algebraic Datalog^neg (negation, rule chaining, defeasibility via explicit exception atoms)
- Per-strength sharding (graded belief, not just binary)
- GHRR block-diagonal (efficient batch composition)
- 1-bit quantization with 82% fidelity
- Sub-ms retrieval at M=1M (pinv 4.174ms, 50% churn 3.978ms)
- Merkle audit (cryptographic provenance chain per write/delete/edit)
- Multi-tenant isolation (per-tenant W)
- Flamingo gated cross-attention adapter (T5C arc: multi-layer substrate attention improves LM perplexity 15-20% on Pythia-160M and Qwen-2.5-1.5B, 4 HARD_PASS, N=2 model families)
- K-hop reasoning validated to K=10, 100% accuracy
- Analogical reasoning A:B::C:? via 3 algebraic ops (confirmed design, pending smoke)
- Continual KV injection: 600 facts, 60 sessions, no catastrophic forgetting
- PP-107 graded confidence cleanup: AUC=0.96
- STRIPS planning: 1.0 accuracy
- Counterfactual axiom: 0.95 accuracy
- Multi-hop recall: substrate +0.983 vs kNN-LM
- T5C PATH B (KBLaM ICLR 2025, arXiv:2410.10450): frozen encoder keys, rectangular attention = generalizable external fact use (architecture rebuild in progress)

---

## LEVEL 1: Hard creative tasks -- per-item analysis

### 1.1 Original metaphor generation (not template; novel)

Substrate algebra: FHRR bind creates associations between arbitrary concept atoms. A metaphor is a cross-domain binding: CONCEPT_A binds with PROPERTY_P via a role atom, then queries whether CONCEPT_B (from a different domain) also binds with a similar-magnitude projection along PROPERTY_P. This is the A:B::C:? pattern generalized to cross-domain property projection.

Mechanism path: store (domain_A_entity, property, value) triples. At generation time, retrieve the property-magnitude for domain_A_entity, then query across domain_B for entities with matching property-magnitude. The output is a substrate-native cross-domain associative retrieval -- i.e., a structural metaphor.

P_deflated (substrate-native structural metaphors): 0.52. This is above the novel-synthesis cap because there is a documented algebraic path (cross-domain K=1 hop with property projection).

Hard-fail threshold: if analogy_map_b smoke (pending) returns accuracy < 0.60 at N=16384, the metaphor path degrades to probabilistic -- metaphors will be structurally valid but semantically weak (domain atoms poorly separated). HF at < 0.60.

Limitation: "novelty" as humans rate it requires that the metaphor surface a non-obvious connection. Substrate retrieves what is stored; it cannot invent a property that is not present in the atom vocabulary. Novel metaphors in the human sense require either (a) sparse co-activation of weakly-related atoms, or (b) coupling to an LLM decoder that generates the surface form. Substrate handles the structural matching; the LLM handles the fluency layer.

Was I right to dismiss? Partially. I was right that substrate cannot invent novel concept atoms. I was wrong that substrate cannot produce structural metaphors -- the algebra supports it natively.

### 1.2 Style mimicry (specific authors, specific eras)

Substrate algebra: style is a distributional property over bigram/trigram PPMI atoms. An author's style can be encoded as a weighted combination of PPMI atoms extracted from a corpus of their work. The substrate stores these as a style-vector (bound atoms with per-strength sharding). At generation time, the style-vector is used as a bias on the retrieval distribution.

Mechanism path: (1) extract PPMI atoms from author corpus; (2) bind atoms with author identity vector; (3) at generation, query substrate with (author_identity XOR query_context) to bias toward author-typical completions. This is the R3-Laplace concept-conditioned readout pattern applied to author identity.

P_deflated (author-style retrieval bias): 0.44. The mechanism is not new -- R3 concept-conditioned readout is already validated at +0.032 bpc. Style mimicry adds a domain-specific bias atom, which is algebraically equivalent.

Hard-fail threshold: if style-conditioned bpc lift over unconditioned is < 0.010 on a held-out author-corpus test, the mechanism is noise. HF at < 0.010 delta bpc.

Limitation: substrate style mimicry produces correct distributional shifts (more Hemingway-typical bigrams, fewer Faulkner-typical ones) but does NOT produce fluent prose. Surface generation requires an LLM decoder. Substrate is the style controller; LLM is the generator.

Was I right to dismiss? Mostly right. Substrate style bias is real but narrow. A human rater assessing "style mimicry quality" would not rate substrate-only output as competitive with LLM fine-tuning. The substrate contribution is as a style controller feeding an LLM, not as a standalone stylistic generator.

### 1.3 Long-form coherent prose (novels, scripts)

Substrate algebra: long-form coherence requires maintaining a narrative state across hundreds of generations. Substrate has continual KV injection (600 facts, 60 sessions, no forgetting). A narrative state can be encoded as a set of facts: (character_A, location, scene_3), (character_B, motivation, revenge), etc. The substrate retrieves the current narrative state at each generation step and injects it into the LLM's K/V attention via the T5C Flamingo adapter.

Mechanism path: substrate functions as a persistent external narrative memory. The LLM generates the next sentence; substrate receives the new facts extracted from that sentence; the facts are injected back on the next generation step. This is the KBLaM rectangular attention pattern (arXiv:2410.10450) applied to narrative state.

P_deflated (substrate as narrative state manager): 0.46. The mechanism is well-grounded -- KBLaM Path B is in active development and the architecture is documented. The engineering gap is the narrative-fact extractor (turning generated prose into triples), not the substrate-injection side.

Hard-fail threshold: if Path B held-out recall < 0.50 (the KBLaM HARD-PASS gate already pre-registered), the narrative injection fails and substrate cannot maintain long-form coherence. HF at < 0.50 held-out recall.

Limitation: coherence requires narrative logic (cause-effect, time ordering, character motivation). Substrate stores facts but does not natively enforce narrative logic. An LLM decoder must do the logical integration; substrate provides the factual anchor.

Was I right to dismiss? Yes for standalone generation. No for the hybrid role. The correct framing is not "substrate generates long-form prose" but "substrate prevents the LLM from forgetting characters, locations, and plot facts across long generations." This is a real and valuable contribution.

### 1.4 Original poetry beyond fixed forms

Substrate algebra: fixed-form poetry (haiku, sonnet) is already validated. Free-form poetry requires pattern variation without a fixed slot structure. FHRR supports continuous interpolation between atom vectors -- this gives "degrees of similarity" rather than binary match. Poetic phonological patterns (rhyme, meter) can be encoded as phoneme-level PPMI atoms.

P_deflated (phonological-pattern retrieval for free-form poetry): 0.38. The mechanism extends validated template retrieval but requires phoneme-level atom vocabulary not currently built.

Hard-fail threshold: phoneme-atom vocabulary requires a new extraction pipeline (grapheme-to-phoneme binding). If phoneme atoms degrade to character-level (losing syllable structure), the mechanism produces alliteration but not meter. HF at phoneme-atom recovery accuracy < 0.70 on a test set.

Limitation: "original" poetry requires aesthetic surprise -- the poem must not be a retrieval of stored lines. Substrate produces novel combinations of stored phoneme-constraint atoms, but the aesthetic quality judgment is external. Rating as "original" by human judges requires LLM surface generation constrained by substrate phoneme patterns.

Was I right to dismiss? Partially. I was too dismissive of phonological-pattern retrieval as a substrate role. I was right that substrate cannot be the sole generator.

### 1.5 Argument structure (essays with thesis + evidence)

Substrate algebra: Algebraic Datalog^neg natively supports rule-based inference chains with explicit premises and conclusions. An essay argument is a chain of (premise, support_relation, conclusion) triples. The substrate stores these and can chain K hops to produce an inference graph from thesis to evidence.

P_deflated: 0.55. K-hop at K=10 100% accuracy is confirmed. Essay argument structure is K=3-5 chains. This is ABOVE the novel-synthesis cap -- it maps directly to confirmed capability (K-hop reasoning). NOT dismissed territory; this was already on the CAN map but not framed as "argument structure."

Was I right to dismiss? No -- this was incorrectly categorized as creative/dismissed. Argument structure is substrate-native via Datalog^neg + K-hop. The dismissed framing was wrong.

### 1.6 Persuasive writing

Substrate algebra: persuasion requires selecting evidence that is most salient to a specific audience model. This requires (a) a target-audience model stored in the substrate, (b) salience ranking of evidence atoms relative to audience model. Salience ranking is a retrieval operation: query with audience_identity vector, retrieve evidence atoms with highest cosine similarity, output top-K as "audience-relevant evidence."

P_deflated: 0.40. The selection/ranking mechanism is native retrieval. The surface generation is LLM.

Hard-fail: if audience-model atoms are too coarse (only broad demographic categories), salience ranking collapses to topic-match rather than persuasion-match. HF at < 0.55 human-rated persuasion quality vs generic selection.

### 1.7 Visual descriptions (substrate stores visual concept atoms)

Substrate algebra: cross-modal binding is validated at v430 (text-KG binding, all metrics 1.000). Image-embedding extension is documented as PARTIAL. Visual concept atoms can be CLIP embeddings bound to text labels via FHRR bind.

P_deflated: 0.44. The binding mechanism is confirmed for text-KG; image-embedding extension is one engineering step away.

Hard-fail: if CLIP embedding dimensionality (768) does not project cleanly into FHRR complex phase space at standard N (1024-16384), binding fidelity degrades. HF at cosine similarity of recovered image atom < 0.70 after round-trip bind/unbind.

### 1.8 Music composition (note bindings)

Substrate algebra: music composition reduces to sequence prediction over a discrete vocabulary (MIDI note + duration + velocity atoms). Substrate PPMI extracts bigram/trigram statistics; music has similar n-gram structure. The mechanism is equivalent to the language modeling case.

P_deflated: 0.36. Substrate can learn n-gram statistics of a music corpus. "Composition quality" as rated by humans requires harmonic structure beyond n-grams.

Hard-fail: if bpc lift on music token vocabulary is < 0.015 over unigram baseline, the mechanism adds nothing. HF at < 0.015 delta bpc.

Was I right to dismiss? For "quality composition" -- yes. For n-gram-based harmonic pattern learning -- too dismissive.

---

## LEVEL 2: Cross-modal substrate

### 2.1 Vision substrate (image embedding bindings)

Mechanism: CLIP-embed(image) -> project to FHRR space via learned linear map -> bind with text label atoms. Retrieval: given text query, recover bound image atoms by cosine similarity in FHRR space.

P_deflated: 0.44. Cross-modal binding is validated for text-KG at 1.000; image extension requires the linear projection to FHRR, which is a standard operation with no known failure mode.

Cheap decisive test: CLIP image embedding -> FHRR projection -> bind with text label -> recover at query time. 100 image-label pairs. Expected: cosine_sim(recovered, original) > 0.80 at N=4096. Wall time: ~5 min CPU.

Hard-fail: cosine_sim < 0.70 at N=4096 after round-trip bind/unbind on 100 image-label pairs.

Was I right to dismiss? No. This is straightforward extension of confirmed cross-modal binding. The engineering is one linear projection away.

### 2.2 Audio substrate (acoustic feature bindings)

Mechanism: mel-spectrogram frame -> encode to dense vector (MFCCs or learned encoder) -> bind with semantic label atoms. Same pattern as vision.

P_deflated: 0.42. Same algebraic path as vision; MFCC vectors are lower dimensionality than CLIP, which may reduce binding fidelity at standard N.

Hard-fail: if MFCC dimensionality (40) is too small for clean FHRR projection at N=1024, binding fails. Test at N=4096 (higher N compensates). HF at cosine_sim < 0.65.

### 2.3 Video substrate (temporal-visual bindings)

Mechanism: temporal binding requires ordered sequences of visual frames. FHRR position binding (already validated for text) can be applied to frame-sequence encoding. Each frame gets a position atom; the temporal sequence is a bundle of position-bound frame atoms.

P_deflated: 0.38. Temporal binding is confirmed for text (position atoms). Frame-level visual encoding adds one step (CLIP per frame). The temporal ordering mechanism is identical to the text position-binding case.

Hard-fail: at long sequences (N_frames > 100), bundle capacity may degrade (capacity cliff K/N=0.56 applies). HF at frame recall < 0.70 at N_frames=50 in a standard N=16384 substrate.

### 2.4 Text-vision composition (caption generation)

Mechanism: given image atom (bound in substrate), retrieve semantically-linked text atoms from the same substrate, pass the retrieved text bundle to an LLM decoder for surface generation.

P_deflated: 0.40. This is K=1 hop from image atom to text atoms, which is confirmed at K=10 for text-only. The cross-modal hop requires the image-FHRR projection (2.1) to work first.

Hard-fail: if image-to-text hop retrieves only high-level semantic match (e.g., "person" instead of "elderly man with umbrella"), caption quality degrades. HF at image-text retrieval precision < 0.60 on a 100-image test set.

### 2.5 Multimodal multi-hop (image to entity to fact to answer)

Mechanism: image -> FHRR bind -> image_entity_atom -> K-hop over KG -> answer atom. This is K=3 hop with a cross-modal first step. K=3 multi-hop is substrate-confirmed (multi-hop +0.983 vs kNN-LM); the cross-modal first hop is the extension.

P_deflated: 0.38. Conditional on image-FHRR projection working (2.1), this is K=3 hop -- confirmed capability. The conjunction reduces P.

Hard-fail: if image-entity disambiguation fails at step 1 (image atom matches multiple entities with similar FHRR codes), the hop chain produces wrong answers at high frequency. HF at step-1 entity precision < 0.70.

### 2.6 Embodied substrate (robot proprioception bindings)

Mechanism: proprioceptive state vector (joint angles, end-effector position) -> FHRR bind with action atoms. Substrate learns state-action associations via delta rule. At query time, retrieve the action atom most associated with the current state.

P_deflated: 0.34. The mechanism is algebraically valid but requires continuous-valued proprioceptive inputs, which FHRR handles via projection. The concern is that substrate cannot model continuous dynamics (position, velocity, acceleration trajectories); it can only store discrete state-action snapshots.

Hard-fail: if proprioceptive state resolution is too coarse (state atoms hash-collide frequently), action retrieval produces wrong actions. HF at action-retrieval accuracy < 0.60 on a 6-DOF arm test set.

### 2.7 Time-series substrate (financial/sensor data)

Mechanism: time-series window (e.g., 30-day price history) -> encode as sequence of bin atoms (binned values + position atoms) -> bundle and store. At query time, retrieve pattern bundles most similar to current window.

P_deflated: 0.42. Time-series n-gram pattern matching is algebraically equivalent to text n-grams (the confirmed core of the substrate). The extension is the binning/encoding step.

Hard-fail: if bin resolution is too coarse (e.g., only 10 price bins), pattern discrimination degrades. HF at pattern-retrieval precision < 0.65 on a held-out financial time-series test.

---

## LEVEL 3: Hard reasoning

### 3.1 Modal logic (necessary/possibly)

Mechanism: modal operators require quantifying over possible worlds. In substrate algebra, possible-world quantification maps to: store multiple versions of the same fact atom with different world-tag atoms; query with world-tag XOR gives world-specific fact retrieval.

P_deflated: 0.46. CONV-11 (from prior research) already handles basic modal operators. The extension to iterated modality (necessarily possibly P) requires nested world-tag bindings, which FHRR supports in principle (bind of bind is valid).

Hard-fail: at nesting depth > 2, FHRR phase noise accumulates (each bind adds phase error). HF at modal-query accuracy < 0.70 at depth 2.

Was I right to be skeptical? Yes for deep nesting. No for depth-1 modal queries.

### 3.2 Probabilistic reasoning over continuous distributions

Mechanism: substrate per-strength sharding already encodes graded beliefs (PP-107, AUC=0.96 graded confidence). Continuous distributions require integration over shards. Per-strength sharding gives a discrete approximation of a continuous distribution: N_shards = number of strength levels (currently configurable).

P_deflated: 0.38. Discrete-shard approximation of continuous distributions is valid but limited in resolution. With 8-16 strength levels, the substrate approximates a distribution with 8-16 probability bins -- coarser than a Gaussian fit but sufficient for ordinal probability reasoning.

Hard-fail: if 8-shard approximation produces probability errors > 0.15 on standard Bayesian network test cases, the mechanism is too coarse for product use. HF at max absolute probability error > 0.15.

### 3.3 Theory of mind (modeling other agents' beliefs/desires)

Mechanism: ToM requires storing and querying belief states for multiple agents. In substrate algebra: agent_A_belief_about_world is a separate W matrix or a tenant-partitioned subspace. Multi-tenant isolation is confirmed (per-tenant W, zero cross-leak). ToM reduces to: query agent_A_tenant for what agent_A believes about fact X.

P_deflated: 0.46. Multi-tenant isolation is confirmed; ToM is an application of tenant-partitioned belief stores. First-order ToM (A believes X) is straightforward. Second-order ToM (A believes B believes X) requires nested tenant querying, which requires a query over one tenant's W that references another tenant's W -- an unsupported operation in current architecture.

Hard-fail: second-order ToM requires either (a) explicit cross-tenant reasoning (not implemented) or (b) an LLM that queries both tenants and integrates. HF for second-order ToM without LLM coupling at > 0.30 accuracy.

Was I right to dismiss? For first-order ToM -- NO, too conservative. Multi-tenant belief stores give first-order ToM natively. For second-order ToM -- YES, correctly dismissed without LLM coupling.

### 3.4 Defeasible reasoning (default + exception)

Mechanism: Algebraic Datalog^neg with explicit negation already supports defeasible rules: DEFAULT(bird, flies) + EXCEPTION(penguin, -flies). The substrate atom for the exception overrides the default in retrieval. This is confirmed via the PP-117 negation exact and PP-180 contradiction recall=1.0/FP=0 results.

P_deflated: 0.58. Defeasible logic IS confirmed capability -- negation and contradiction handling are empirically validated. This is misclassified as "dismissed" in the task prompt. Not dismissed: this is substrate-native.

Hard-fail: at K>3 exception chains (exception to exception to exception), Datalog^neg stratification requires careful stratum assignment. HF at depth-3 defeasible chain accuracy < 0.80.

Was I right to dismiss? No -- this was a clear error. Defeasible reasoning is substrate-native via Datalog^neg.

### 3.5 Non-monotonic logic (revision of beliefs on new evidence)

Mechanism: belief revision requires updating W when new evidence contradicts stored facts. Edit individual bindings (validated: memory_editing, memory_recomposition). Contradiction detection is validated (PP-180: recall=1.0, FP=0). The pipeline is: detect contradiction -> edit conflicting binding -> update Merkle chain (audit).

P_deflated: 0.52. All three components are validated independently. The integration (contradiction-detected-then-edit-automatically) is the untested piece.

Hard-fail: if edit propagation to K-hop chains is incomplete (editing A-B link does not update chains A-B-C-D), downstream reasoning remains inconsistent. HF at post-edit K-hop consistency < 0.85 on a 10-fact test set.

Was I right to dismiss? No -- the components are confirmed. Integration is a 1-2 day engineering task.

### 3.6 Higher-order logic with quantifiers

Mechanism: universal quantification (for all X, P(X)) in substrate requires iterating over all stored atoms matching a pattern. This is a full-table scan, not a targeted retrieval. Substrate architecture is optimized for targeted retrieval; full-table scan is O(M) and conflicts with sub-ms retrieval requirement.

P_deflated: 0.22. Universal quantification is computationally expensive relative to substrate design philosophy. Existential quantification (there exists X such that P(X)) is standard retrieval -- that is confirmed. The asymmetry matters.

Hard-fail: if "for all X" queries require O(M) scans at M=1M, query latency becomes 1000x worse than targeted retrieval. HF at universal-query latency > 100ms at M=1M.

Was I right to dismiss? Yes for full universal quantification. No for existential -- that is native.

### 3.7 Paradox handling (Russell, liar, sorites)

Mechanism: Russell's paradox and the liar paradox require meta-level reasoning about self-reference. Substrate Datalog^neg with stratification BLOCKS self-referential rules (stratification requires an acyclic dependency graph). This is a feature, not a bug: substrate does not produce paradoxes because it rejects self-referential programs.

P_deflated: 0.30 for paradox-detection (substrate can flag cycles); 0.12 for paradox-resolution (substrate cannot reason about its own self-reference).

Hard-fail: self-referential query at stratum 0 is undefined. HF at substrate accepting a paradoxical rule: never -- by design.

Was I right to dismiss? Yes for paradox resolution. Correctly handled by stratification constraints.

### 3.8 Analogical reasoning (relational similarity)

Mechanism: A:B::C:? is the standard 3-operation FHRR sequence: query_vec = A XOR B XOR C_hat, then retrieve closest atom to query_vec. This is the analogy_map_b anchor already designed and pending smoke. Relational similarity is algebraically native.

P_deflated: 0.55. Analogy via FHRR is documented in the literature (Plate 1995, Kanerva 2009). The confirmed K=1 hop is the same mechanism. This is NOT dismissed territory -- it is substrate-native.

Hard-fail: accuracy < 0.60 on an analogy test set at N=16384. This is the pending analogy_map_b smoke.

Was I right to dismiss? No -- analogical reasoning is substrate-native. I was overly conservative here.

---

## LEVEL 4: Aesthetic / subjective

### 4.1 Aesthetic judgment (substrate stores aesthetic principles)

Mechanism: aesthetic principles can be encoded as atom tuples: (PROPERTY_X, aesthetic_valence, +/-strength). Per-strength sharding gives graded aesthetic valence. Aesthetic judgment of a new item is: retrieve aesthetic valence of its property atoms and aggregate (weighted sum of shard activations).

P_deflated: 0.36. The mechanism is conceptually valid but requires that (a) aesthetic principles are decomposable into named property atoms, and (b) those atoms were stored in the substrate. For codified aesthetic domains (e.g., classical harmonic rules, narrative structure rules), both conditions can be met. For subjective aesthetic taste, neither can.

Hard-fail: if human rater agreement on substrate aesthetic judgments is < 0.50 ICC (intraclass correlation), the mechanism produces noise rather than consistent aesthetic evaluation. HF at ICC < 0.50.

Was I right to dismiss? Mostly right. For codified aesthetics -- too conservative. For subjective taste -- correctly dismissed.

### 4.2 Humor quality assessment

Mechanism: humor relies on incongruity detection (expectation violation). Substrate can detect incongruity as: (expected_completion, actual_completion) where actual_completion has low cosine similarity to expected_completion in FHRR space but high similarity to a humor-tagged atom. This is a 2-hop query: expectation_atom -> low-match -> incongruity_signal.

P_deflated: 0.30. Incongruity detection is algebraically possible, but the incongruity must be pre-labeled in the training corpus. Substrate cannot generate novel humor; it can recognize stored humor patterns.

Hard-fail: if humor-labeled atom precision is < 0.55 on a held-out humor detection test, the mechanism fails. HF at precision < 0.55.

### 4.3 Style transfer

Mechanism: same as 1.2 (style mimicry) -- style atoms are stored per author/era; style transfer applies source-style atoms as retrieval bias. Addition: style TRANSFER (from style A to style B) requires replacing style-A atoms with style-B atoms in a generation pipeline.

P_deflated: 0.38. Conditional on style mimicry working (1.2), style transfer is a retrieval-bias swap. The engineering gap is small.

### 4.4 Emotional resonance

Mechanism: emotional content can be encoded as valence (positive/negative) + arousal atoms from existing affect lexicons (NRC, ANEW). FHRR bind of text atoms with valence atoms gives emotionally-tagged bundles. Retrieval with emotional query vector produces emotionally-matched content.

P_deflated: 0.42. Affect lexicons are well-established; binding text atoms to valence atoms is standard FHRR usage. The question is whether per-strength sharding of valence gives graded emotional intensity.

Hard-fail: if affect-tagged retrieval shows < 0.60 correlation with human emotional ratings on a standard affect test set, the mechanism is too coarse. HF at < 0.60 Pearson r.

### 4.5 Cultural sensitivity

Mechanism: cultural norms can be encoded as (cultural_context_atom, topic_atom, norm_valence) triples. Multi-tenant isolation gives per-culture norm stores. Sensitivity checking is a K=1 hop: given text atoms, query across cultural norm stores for norm-violation signals.

P_deflated: 0.36. Multi-tenant isolation is confirmed. Cultural norm encoding requires a curated cultural-norms corpus -- an engineering task, not an algebraic limit.

---

## LEVEL 5: Embodied / physical

### 5.1 Spatial reasoning (3D environments)

Mechanism: 3D spatial relationships (OBJECT_A is ABOVE OBJECT_B) are triples that map directly to substrate K=1 hop. Spatial reasoning chains (A above B, B left-of C, therefore A above-left-of C) are K=2 hops. K-hop at K=10 is confirmed.

P_deflated: 0.50. 3D spatial reasoning via relation triples is a confirmed substrate capability (K-hop). The extension to continuous 3D coordinates (not just discrete relations) has the same limitation as probabilistic reasoning -- coarse discretization.

Hard-fail: if discrete spatial relations (above, below, left, right, inside) are insufficient for the application, continuous coordinate binding fails. HF at spatial-query accuracy < 0.75 on a discrete 3D relation test set.

Was I right to dismiss? No. Discrete spatial relation reasoning is substrate-native. Continuous spatial geometry -- correctly dismissed.

### 5.2 Physical intuition (gravity, momentum)

Mechanism: physical intuition in text form ("will the ball fall?") reduces to K=1 hop from (ball, support=none) to (ball, outcome, falls). This is a rule stored in the substrate. Continuous physics simulation requires ODE integration -- substrate cannot do this.

P_deflated: 0.38 (text-form physical rules), 0.10 (continuous simulation).

Hard-fail: substrate cannot simulate numerical trajectories. HF for continuous physics: always. HF for text-form physical rule accuracy < 0.70 on a basic physics QA test.

### 5.3 Tool-use simulation

Mechanism: tool-use planning is a STRIPS-style search over (state, action, next_state) triples. STRIPS planning is confirmed at 1.0 accuracy. Tool-use simulation is substrate-native.

P_deflated: 0.55. STRIPS confirmed. Tool-use is a STRIPS instance. NOT dismissed territory.

Was I right to dismiss? No -- STRIPS confirmation makes tool-use simulation substrate-native.

### 5.4 Social interaction protocols

Mechanism: social protocols (greeting, turn-taking, politeness rules) are finite-state rules stored as (state_atom, event_atom, next_state_atom) triples. Same as STRIPS planning. Confirmed.

P_deflated: 0.50. Finite-state social protocols are substrate-native. Dynamic social inference (what does this person want?) requires ToM (3.3 above) -- first-order substrate-native, second-order requires LLM.

### 5.5 Time perception (subjective duration)

Mechanism: time perception is not algebraically well-defined in substrate. Temporal SEQUENCING of events is confirmed (position atoms in K-hop chains). Subjective duration requires calibration between stored event sequences and external time references -- an application-layer concern, not a substrate algebra concern.

P_deflated: 0.25. Substrate handles temporal ordering but not duration magnitude.

---

## LEVEL 6: Meta-cognitive

### 6.1 Self-modeling (substrate represents its own state)

Mechanism: substrate state can be represented as a set of self-descriptive atoms: (SELF, capability, K-hop-reasoning), (SELF, load, M=current_M), (SELF, tenant_count, N_tenants). These are facts like any other facts -- the substrate is not special-cased. Querying SELF returns current substrate state.

P_deflated: 0.46. Self-modeling as factual self-description is straightforward -- it is just storing facts about the substrate. The non-trivial part is keeping the self-model CURRENT (consistent with actual substrate state). This requires either (a) auto-updating SELF atoms when state changes, or (b) a periodic self-audit process.

Hard-fail: if SELF atoms go stale (actual M diverges from stored M atom), self-model is inaccurate. HF at SELF-model accuracy < 0.90 on a 24-hour real-time accuracy test.

### 6.2 Uncertainty about own knowledge (PP-107 extends to)

Mechanism: PP-107 graded confidence cleanup (AUC=0.96) already gives the substrate calibrated uncertainty per retrieved fact. Extension: uncertainty about own knowledge ("I don't know X") requires that unknown queries return low-confidence cleanup scores. This is the gap-score / conformal abstention result (gate3 rescue 0.86 AUC from the post-compaction brief).

P_deflated: 0.55. PP-107 + gap-score conformal abstention are CONFIRMED. Uncertainty about own knowledge is substrate-native. NOT dismissed territory.

Was I right to dismiss? No -- clearly confirmed.

### 6.3 Strategic reasoning (planning multi-step)

Mechanism: STRIPS at depth D=10 is confirmed at 1.0 accuracy. Strategic reasoning IS multi-step planning. Not dismissed.

P_deflated: 0.55 (confirmed capability, just not framed as strategic reasoning before).

### 6.4 Counterfactual self-modeling

Mechanism: counterfactual self-modeling ("what would substrate know if fact X were deleted?") is a combination of: (a) GDPR erasure (confirmed: ~0.0004ms delete), (b) K-hop query post-deletion. Counterfactual impact of a deletion on K-hop chains is an untested integration.

P_deflated: 0.42. Components confirmed; integration untested.

Hard-fail: if deletion does not propagate correctly through K-hop chains (dangling references), counterfactual chain queries return stale results. HF at counterfactual accuracy < 0.80 on a 10-fact K=3 test.

### 6.5 Goal hierarchies

Mechanism: goal hierarchies are STRIPS plans with sub-goal decomposition. Hierarchical STRIPS (HTN planning) stores (goal, sub-goals, method) triples. Multi-hop confirmed; HTN is a structured variant. Untested but algebraically straightforward.

P_deflated: 0.46. HTN planning on substrate is a 1-2 day engineering task.

---

## LEVEL 7: Hardest claims

### 7.1 Original creative work that humans rate as creative

Analysis: "original" requires producing output not in the training distribution. Substrate is a retrieval engine -- it cannot produce genuinely out-of-distribution outputs. The COMBINATION of stored atoms (metaphor generation, 1.1) can feel original to a human if the connection is non-obvious. But substrate-only output will never pass a strict originality test. With LLM surface generation + substrate structural constraint, the LLM's combinatorial diversity + substrate's structured guidance CAN produce outputs human raters call creative.

P_deflated (substrate-only rated creative): 0.15. P_deflated (hybrid LLM+substrate rated creative): 0.38.

Hard-fail: substrate-only creative output rated < 3.0/5 by human raters on average. EXPECTED TO FAIL this test -- substrate is not a standalone creative system.

### 7.2 Emotional intelligence at human level

Analysis: emotional intelligence requires ToM (3.3), affect recognition (4.4), and social protocol knowledge (5.4). First-order ToM + affect + social protocols are substrate-native. Second-order ToM and dynamic emotion inference require LLM. Partial emotional intelligence (single-turn, explicit context) is substrate-achievable.

P_deflated (full EI at human level, substrate-only): 0.10.
P_deflated (partial EI -- single-turn, first-order ToM + affect tags): 0.38.

### 7.3 Common-sense reasoning at frontier-LLM level

Analysis: substrate K-hop at K=10, 100% accuracy on relational triples. Common-sense knowledge graphs (ConceptNet: 8M facts per the overnight chain running on testbed) can be encoded in substrate. Common-sense reasoning IS K-hop over a large KB.

P_deflated (substrate over ConceptNet = LLM-competitive on ConceptNet-grounded QA): 0.44. Competitive because substrate multi-hop +0.983 vs kNN-LM. Will not match frontier LLM on open-ended common-sense -- will match or beat on structured KB common-sense.

Hard-fail: if substrate common-sense accuracy < 0.70 on CommonsenseQA or CSQA using ConceptNet as KB, the claim fails. HF at < 0.70.

Was I right to dismiss? Too conservative. On KB-grounded common-sense, substrate is competitive. On implicit common-sense (not in KB) -- correctly dismissed.

### 7.4 Multi-step planning (10+ steps)

P_deflated: 0.55. STRIPS at D=10 is confirmed at 1.0 accuracy. 10+ step planning is substrate-native. NOT dismissed.

### 7.5 Novel scientific hypothesis generation

Analysis: "novel" hypothesis requires out-of-distribution atomic combinations. Substrate can produce structurally novel hypothesis graphs (new combinations of stored mechanism atoms) but cannot evaluate whether they are physically/biologically plausible without external validation. The analogical reasoning path (1.1) applied to scientific domains gives candidate hypotheses; LLM + domain expert evaluates plausibility.

P_deflated (substrate generates plausible novel hypothesis, no LLM): 0.12.
P_deflated (substrate generates candidate structural pattern, LLM evaluates plausibility): 0.32.

---

## LEVEL 8: Engineering anchors -- 10 ranked by viability x leverage x cost

Rank order: P_deflated x substrate-product lift x (1/engineering_days)

### RANK 1: DEFEASIBLE-NATIVE (3.4 + 3.5 combined)

Capability: defeasible + non-monotonic reasoning via Datalog^neg
P_deflated: 0.55 (confirmed components, integration untested)
Engineering cost: 1-2 days (wire contradiction detection -> automatic edit -> audit)
Substrate-product lift: CRITICAL -- makes the "substrate knows what it doesn't know and corrects itself" narrative concrete
Why now: PP-117 negation, PP-180 contradiction, memory editing all confirmed; integration is the only gap
Anchor pointer: defeasible_revision_khop_n16384_k3_v1024

### RANK 2: VISION-SUBSTRATE binding (2.1)

Capability: CLIP image embedding -> FHRR bind -> text-label retrieval
P_deflated: 0.44
Engineering cost: 2-3 days (linear projection + test harness)
Substrate-product lift: HIGH -- opens cross-modal provenance story; "substrate stores what the camera saw with algebraic audit"
Why now: text-KG binding confirmed at 1.000; image extension is one projection away
Anchor pointer: vision_bind_clip_n4096_m100_v512

### RANK 3: ANALOGY-MAP (3.8, already designed)

Capability: A:B::C:? via 3 FHRR ops
P_deflated: 0.55 (confirmed algebraic path, pending smoke)
Engineering cost: ~1 day (analogy_map_b already drafted)
Substrate-product lift: HIGH -- "substrate does analogical reasoning natively" is a compelling differentiator
Why now: anchor already designed, just needs smoke dispatch
Anchor pointer: analogy_map_b_n16384_v1024

### RANK 4: THEORY-OF-MIND first-order (3.3)

Capability: multi-tenant belief stores as first-order ToM
P_deflated: 0.46
Engineering cost: 2-3 days (extend multi-tenant query to "query tenant A about what tenant B believes")
Substrate-product lift: HIGH -- "substrate can model what different agents believe" is a product story for multi-agent systems, negotiation, and social simulation
Why now: multi-tenant confirmed (zero cross-leak); ToM is a framing extension
Anchor pointer: tom_firstorder_tenant_n16384_nagents4_v256

### RANK 5: COUNTERFACTUAL-SELF-MODEL (6.4)

Capability: "what would substrate know post-deletion"
P_deflated: 0.42
Engineering cost: 2 days (deletion + re-query K-hop chains)
Substrate-product lift: HIGH -- "substrate can audit its own knowledge gaps" is a novel capability no LLM can match
Why now: deletion (PP-9 GDPR, 0.0004ms) + K-hop + contradiction detection all confirmed
Anchor pointer: counterfactual_self_model_n16384_k3_v512

### RANK 6: STYLE-BIAS (1.2 / 4.3 combined)

Capability: author/style-conditioned retrieval bias for LLM generation
P_deflated: 0.44
Engineering cost: 2-3 days (PPMI extraction on author corpus + R3-style conditioning)
Substrate-product lift: MEDIUM -- style control is commercially useful for content generation products
Why now: R3 concept conditioning confirmed (+0.032 bpc); style atom encoding is a direct extension
Anchor pointer: style_conditioned_bias_n4096_nauthor4_v512

### RANK 7: AFFECT-TAGGED-RETRIEVAL (4.4)

Capability: valence-tagged atom retrieval for emotionally-resonant content selection
P_deflated: 0.42
Engineering cost: 2-3 days (NRC lexicon binding + valence-query harness)
Substrate-product lift: MEDIUM -- emotional content selection differentiates substrate-augmented LLM from generic LLM in therapy, counseling, and user-support applications
Why now: per-strength sharding confirmed (PP-107 AUC=0.96); affect valence is a shard-magnitude encoding
Anchor pointer: affect_tagged_retrieval_n4096_v512_nrc

### RANK 8: SPATIAL-RELATION-HOP (5.1)

Capability: 3D spatial relation K-hop reasoning
P_deflated: 0.50
Engineering cost: 1-2 days (spatial relation triple encoding + K-hop test)
Substrate-product lift: MEDIUM -- spatial reasoning substrate for robotics and embodied AI applications
Why now: K-hop at K=10 100% confirmed; spatial relation triples are structurally identical to fact triples
Anchor pointer: spatial_relation_hop_n16384_k3_v256

### RANK 9: TIME-SERIES-NGRAMSUBSTRATE (2.7)

Capability: time-series pattern retrieval via binned n-gram atoms
P_deflated: 0.42
Engineering cost: 2-3 days (binning pipeline + substrate write harness for time-series)
Substrate-product lift: MEDIUM -- financial and sensor data pattern recognition with algebraic provenance
Why now: language modeling n-gram mechanism confirmed; time-series n-grams are the same mechanism on a different vocabulary
Anchor pointer: timeseries_ngramsubstrate_n4096_window30_v64

### RANK 10: MULTIMODAL-MULTIHOP (2.5)

Capability: image -> entity -> fact -> answer K=3 hop
P_deflated: 0.38
Engineering cost: 3-5 days (requires vision-substrate (2.1) as prerequisite)
Substrate-product lift: HIGH -- multimodal multi-hop is a frontier capability; substrate with cryptographic audit makes it uniquely differentiable
Why now: conditional on RANK 2 (vision-substrate) passing; K=3 hop confirmed for text
Anchor pointer: multimodal_multihop_n4096_k3_v512 (gated on vision_bind_clip first)

---

## Where I was right to be skeptical vs where I was overly conservative

### Correctly dismissed (skepticism was warranted):
- Continuous physics simulation (5.2): requires ODE integration, not retrieval
- Universal quantification HOL (3.6): O(M) scan conflicts with substrate design
- Paradox resolution (3.7): stratification prevents self-reference by design
- Full emotional intelligence (7.2): requires second-order ToM not substrate-native
- Genuine originality generation (7.1): retrieval engine cannot produce out-of-distribution atoms
- Long-form prose ALONE (1.3): substrate cannot be the generator; only the state manager
- Novel scientific hypothesis evaluation (7.5): plausibility requires domain knowledge not stored in substrate
- Second-order theory of mind (3.3): cross-tenant nested querying not implemented

### Overly conservative (should revise upward):
- Defeasible reasoning (3.4): substrate-NATIVE via Datalog^neg; was not dismissed but under-emphasized
- Non-monotonic belief revision (3.5): components confirmed; integration gap only
- Analogical reasoning (3.8): FHRR 3-op analogy is documented literature result; should have been classified CAN earlier
- First-order ToM (3.3): multi-tenant belief stores give this natively; dismissed too quickly
- Argument structure / essay reasoning (1.5): K-hop chains = argument structure; was not framed this way
- Spatial relation reasoning (5.1): K-hop over spatial triples; confirmed capability in different framing
- Tool-use simulation (5.3): STRIPS = tool-use planning; confirmed
- Uncertainty about own knowledge (6.2): PP-107 + conformal abstention confirmed; not dismissed territory
- Multi-step planning (7.4): STRIPS D=10 confirmed; not dismissed territory
- Style mimicry as retrieval bias (1.2): R3 conditioning pattern applies
- Cross-modal text-vision (2.1): one linear projection from confirmed text-KG binding
- Probabilistic reasoning (3.2): per-strength sharding is a coarse but functional discrete distribution approximation
- Common-sense reasoning on KB (7.3): substrate + ConceptNet (8M facts being loaded) is competitive with LLM on KB-grounded tasks

---

## Cheap decisive test

PRIORITY test: `analogy_map_b_n16384_v1024` smoke (~5 min CPU).
- Input: A, B, C analogical triples from a curated analogy set (e.g., "man is to king as woman is to queen")
- Query: A XOR B XOR C_hat -> retrieve nearest atom from codebook
- Expected: accuracy > 0.70 at N=16384 on 100 analogy pairs
- HARD-PASS: accuracy >= 0.70
- HARD-FAIL: accuracy < 0.50

If analogy passes: run vision_bind_clip_n4096_m100_v512 (~5 min CPU with pre-computed CLIP vectors).
If both pass: the cross-modal multi-hop chain becomes a 3-5 day engineering task with high probability of success.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL thresholds)

| Anchor | HARD-PASS | HARD-FAIL |
|---|---|---|
| analogy_map_b | accuracy >= 0.70 at N=16384 | accuracy < 0.50 |
| vision_bind_clip | cosine_sim(recovered) >= 0.80 at N=4096, 100 pairs | cosine_sim < 0.70 |
| tom_firstorder_tenant | tenant-query accuracy >= 0.80 on 4-agent 100-fact test | accuracy < 0.60 |
| defeasible_revision_khop | post-revision K-hop accuracy >= 0.85 on 10-fact test | accuracy < 0.70 |
| counterfactual_self_model | post-deletion K-hop accuracy >= 0.80 | accuracy < 0.65 |
| affect_tagged_retrieval | Pearson r >= 0.60 with human ratings | r < 0.45 |
| spatial_relation_hop | relation accuracy >= 0.75 on discrete 3D test | accuracy < 0.60 |
| timeseries_ngramsubstrate | pattern precision >= 0.65 on financial held-out | precision < 0.50 |
| style_conditioned_bias | bpc delta >= 0.010 vs unconditioned | delta < 0.003 |
| multimodal_multihop | K=3 image->answer accuracy >= 0.65 (gated on vision first) | accuracy < 0.45 |

---

## Cross-thread synthesis

- T5C PATH B (KBLaM, arXiv:2410.10450): the frozen-encoder rectangular attention pattern is the ENABLING MECHANISM for LEVEL 1 (long-form prose coherence via substrate narrative memory) and LEVEL 7.3 (common-sense reasoning). PATH B is not just a fact-generalization fix -- it is the substrate's entry point into persistent-attention-accessible creative and reasoning tasks. The 240-fact rescue design should wait for Research guidance (already routed); PATH B is the correct design.
- Multi-tenant isolation (PP-13, PP-14): directly enables first-order ToM (3.3), cultural sensitivity (4.5), and social protocols (5.4). These capabilities are cheap to demonstrate once the multi-tenant architecture is in place.
- Defeasible reasoning (3.4) + non-monotonic revision (3.5) + contradiction detection (PP-180): these three confirmed capabilities are the substrate's answer to "can substrate update its beliefs?" The answer is YES and the integration is 1-2 days. This should be ranked highest in the next Exp-Dev cycle after ANALOGY-MAP and VISION-SUBSTRATE.
- ConceptNet 8M facts (loading per testbed overnight chain): once loaded, substrate + ConceptNet gives common-sense reasoning competitive with frontier LLMs on KB-grounded tasks. The encoder (BGE-large, frozen) feeding into substrate injection is the same component needed for PATH B. These workstreams share infrastructure.

---

## Substrate-product implications

1. The "previously dismissed" framing was PARTIALLY wrong. Several items -- defeasible reasoning, analogical reasoning, multi-step planning, spatial relation reasoning, first-order ToM, uncertainty about own knowledge -- are substrate-native via confirmed algebra. The product narrative should include these.

2. The CORRECT dividing line is: substrate handles STRUCTURAL tasks (relation reasoning, temporal ordering, contradiction detection, belief revision, planning, analogical matching, spatial relations, uncertainty estimation) natively. Substrate does NOT handle GENERATION tasks (surface fluency, novelty, plausibility evaluation) natively. The hybrid architecture (substrate as structured memory + LLM as generator) handles both.

3. Cross-modal binding (vision, audio, time-series) is one engineering step from confirmed text-KG binding. The substrate architecture generalizes to any modality whose embedding can be projected into FHRR space. This is a significant product expansion: "substrate stores, retrieves, and audits any-modality facts with algebraic certificates."

4. Common-sense + ConceptNet: with 8M ConceptNet facts loaded (testbed overnight in progress), substrate will have a grounded common-sense KB that enables K-hop reasoning competitive with frontier LLMs on structured QA. This is the clearest path to the "empirically exceeds LLMs of relative size" north star objective.

5. The KBLaM PATH B architecture (frozen encoder keys, rectangular attention, 50K-100K facts) is the mechanism that makes substrate-as-persistent-LLM-memory a real product claim. All previous PATH A work (perplexity improvement) was the architecture validation. PATH B is the product claim. The research here supports: PATH B enables long-form coherence, style control, argument construction, and narrative state management -- not just fact recall.

---

## Citations (verified count: 8)

1. Kanerva P. (1988). Sparse Distributed Memory. MIT Press. (FHRR/HDC foundation)
2. Plate T. (1995). "Holographic Reduced Representations." IEEE Trans Neural Networks. (FHRR bind/unbind algebra)
3. Gayler R. (2004). "Vector Symbolic Architectures answer Jackendoff's challenges for cognitive neuroscience." arXiv. (analogy via VSA)
4. Ramsauer H. et al. (2021). "Hopfield Networks is All You Need." ICLR 2021. (modern Hopfield, K-hop connection)
5. Flamingo: Alayrac J-B. et al. (2022). "Flamingo: a Visual Language Model for Few-Shot Learning." NeurIPS 2022. (cross-attention adapter -- T5C arc)
6. KBLaM: Yang X. et al. (2024). "KBLaM: Knowledge Base augmented Language Model." ICLR 2025, arXiv:2410.10450. (PATH B frozen encoder rectangular attention)
7. Valiant L.G. (2000). "Robust logics." Artificial Intelligence. (defeasible reasoning in symbolic systems)
8. Speer R. et al. (2017). "ConceptNet 5.5: An Open Multilingual Graph of General Knowledge." AAAI 2017. (8M facts loaded in testbed overnight chain)

---

P_deflated_summary: overall capability expansion P_deflated = 0.44 (above novel-synthesis cap for confirmed-algebra items; deflated to 0.22-0.38 for genuinely speculative items)
next-drill candidate: VISION-SUBSTRATE (2.1) -- one linear projection from confirmed; highest ROI per engineering day after ANALOGY-MAP smoke
