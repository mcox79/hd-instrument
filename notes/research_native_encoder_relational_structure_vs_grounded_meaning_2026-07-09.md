# Research: Is a relational-graph encoder "understanding language," or something else?

Field: `semantic-grounding-cogsci` (NEW field — not yet in research_field_advisor tracked-fields list; cross-domain: cognitive neuroscience, philosophy of mind, computational linguistics, developmental psychology, causal ML). Brain-first per USER 07-08 directive; ML treated as evidence source, not guide.

Date: 2026-07-09. Dispatched: 4 parallel Sonnet lit-scan sub-agents (hub-and-spoke neuroscience / symbol grounding problem / distributional-hypothesis ceiling / embodied-cognition minimal-grounding-channels), synthesized by research (self).

---

## (a) HEADLINE

**Relational/structural knowledge and grounded meaning are two different, empirically dissociable things, and the difference is not a matter of scale.** Four independent literatures (semantic neuroscience, philosophy of language, computational linguistics, developmental psychology) converge on the same structural claim: a system that only has symbol-to-symbol (or atom-to-atom) relational data — however large, however densely interconnected — can build a real, useful, but **categorically incomplete** representation. It supports similarity, analogy, taxonomic inference, one-shot property inheritance along graph edges. It **cannot**, by any amount of added relational data, acquire content that refers to anything outside the symbol set (Harnad 1990's dictionary-go-round; Bender & Koller 2020's octopus test; Coelho Mollo & Millière 2023's "Vector Grounding Problem"). This is a **logical/structural** ceiling, not an empirical one that more graph edges fix.

Our native encoder, trained on ConceptNet-style relational topology with near-random atom codes, is doing exactly what the hub-and-spoke neuroscience literature calls the **hub's job**: integrating/converging co-occurrence structure among inputs. The neuroscience is unusually direct on what a hub-without-spokes produces: the congenitally-blind color-knowledge study (Connolly et al., *PNAS* 2007) shows blind subjects have essentially identical relational/co-occurrence-derived similarity structure to sighted subjects for non-perceptual categories (r=0.97), but for color — the property they've never perceived — their knowledge is **propositionally present but functionally inert**: color explains 0% of similarity-judgment variance in blind subjects vs 23% in sighted subjects, even though most blind subjects can *state* correct color facts. That is a literal biological instance of "hollow retrieval skeleton vs. real meaning," and it is the closest empirical analogue to what a relational-only encoder is structurally doomed to produce for anything the graph itself doesn't encode.

The honest framing for our product: **the current encoder is learning relational topology, which is a real and useful capability, but it is not language understanding and will not become language understanding by adding more relational data.** Per house discipline (no smoke, deflate our claims not the ambition) — this is a claim about the CURRENT encoder's design, not a ceiling on what a self-contained substrate could ever do; the literature also identifies concrete, buildable, non-LM grounding channels (below) that a self-contained system could add.

---

## (b) Cheap decisive test

**No new build required.** Construct two probe sets over the EXISTING encoder's atom vocabulary, using data already present or trivially derivable from the existing graph:

1. **Relational probes** (should be near-ceiling): edge-type prediction, hypernym/hyponym distance, analogy-style completion (A:B :: C:?) restricted to relation types present in training.
2. **Grounded-attribute probes** (should be near-chance if the hollow-skeleton hypothesis is correct): magnitude/perceptual-property judgments NOT explicitly present as graph edges — e.g. "is X bigger than Y" (physical-size ordering), "is X louder/heavier/faster than Y," or any attribute-comparison for atom pairs where the comparison itself was never an edge in the training graph (only co-hyponymy/is-a edges were).

Run both probe families on the current encoder with no changes. This is a <1 day CPU test.

**Pre-registered thresholds:**
- **HARD-PASS** (confirms hollow-skeleton diagnosis, matches literature): relational-probe accuracy is well above chance (task-appropriate baseline, e.g. >2x chance) AND grounded-attribute-probe accuracy is statistically indistinguishable from chance (gap between the two probe families >= 40 percentage points).
- **HARD-FAIL** (refutes the diagnosis for our specific substrate, or reveals leakage): grounded-attribute-probe accuracy is ALSO well above chance with no grounding channel added. If this happens, check for leakage first (did comparative/magnitude info sneak in via an existing relation type, e.g. an implicit ordering encoded in the graph structure itself) before concluding the theory doesn't apply here.

---

## (c) Falsifiable predictions

**Prediction A — hollow-skeleton ceiling split (see cheap decisive test above).** HARD-PASS/HARD-FAIL thresholds as stated.

**Prediction B — transitive grounding inheritance via a small externally-fed seed set.** Per Günther et al. (2018, *Cognitive Science*, "Symbol Grounding Without Direct Experience") and the hub-and-spoke graded-gradient evidence (Cerebral Cortex 2016), grounding does NOT need to be attached to every atom — a small directly-grounded seed set can propagate transitively through relational structure to neighboring ungrounded atoms, with strength decaying by graph distance. Buildable cell: attach real external numeric/attribute features (size, weight, or any measured, non-symbolic magnitude) to a small seed set (order 50-200 atoms), run existing relational propagation/training, then re-run the grounded-attribute probe restricted to atoms 1-2 hops from a seed vs. atoms far from any seed.
  - **HARD-PASS**: grounded-attribute-probe accuracy for near-seed atoms improves over the ungrounded baseline by a pre-registered margin (e.g. +15 points), with the improvement monotonically decaying as graph distance from the nearest seed increases (mirrors both Günther's transitive-inheritance result and the ATL's graded-hub gradient).
  - **HARD-FAIL**: no improvement near seeds, OR improvement is flat/uncorrelated with graph distance (the latter would suggest an artifact/leakage rather than genuine transitive grounding, since the theory specifically predicts distance-decay).
  - Novel-synthesis P estimate (untested in any HD/graph-embedding artificial system per lit scan — genuinely uncharted): **P=0.35 (deflated; capped at 0.50 per calibration rule)**.

**Prediction C — causal/index diagnostic for "real meaning" vs. "hollow skeleton."** Per Peirce's icon-index-symbol distinction and causal representation learning (Ahuja et al. 2023; Bengio et al. 2021): the operational test for whether an internal representation is grounded vs. merely self-consistent is whether perturbing the purported external referent CAUSALLY moves the internal representation. Buildable cell: perturb an exogenous grounded feature attached to an atom (from Prediction B's seed set) and measure representational shift (cosine/similarity delta) vs. perturbing an arbitrary relational edge of matched "size" (same number of downstream affected atoms).
  - **HARD-PASS**: representational shift from grounded-feature perturbation exceeds shift from matched relation-only perturbation by >=2x.
  - **HARD-FAIL**: no differential sensitivity — this would mean the exogenous channel isn't actually wired into the learned representation (an implementation failure to diagnose, not evidence against the theory).
  - P estimate: **P=0.40 (deflated; capped at 0.50)** — mechanism is well-motivated but the specific wiring into an HD/VSA relational encoder is untested.

**Prediction D — grounding gains concentrate on perceptual/attribute tasks, not relational tasks (literature-level prediction, should transfer).** Per Silberer & Lapata (2012/2014), Bruni/Baroni (2014), and the general pattern across the distributional-ceiling literature: if/when a grounding channel is added, improvement should appear specifically on attribute/perceptual probes, with little-to-no change on already-near-ceiling relational/taxonomic probes.
  - **HARD-PASS**: post-grounding improvement concentrated (>80% of total probe-accuracy gain) in the grounded-attribute probe family.
  - **HARD-FAIL**: gains spread evenly across both families, or concentrate in the relational family (would suggest the "grounding channel" is actually just adding more relational signal in disguise, not real grounding).
  - P estimate: **P=0.45 (deflated; capped at 0.50)**.

---

## (d) Cross-thread synthesis with prior entries

**This connects directly to `notes/research_compounding_error_bound_5x_drill_new_mechanism_class_cross_domain_2026-07-09.md`, filed the same day.** That drill's core diagnosis — four generation-mechanism HARD_FAILs all traced to correction signals being a re-derived function of the SAME noisy estimator, with the fix being an **exogenous, independent-of-the-estimator ground-truth gate** (verified via a Kalman-observability-style independence criterion) — is the SAME structural pattern as the symbol grounding problem's core claim: **a closed system cannot bootstrap the property it lacks (accuracy, or reference/meaning) from more of the same internally-generated material; it needs a channel that is exogenous to the loop that's trying to acquire the property.**

This is now a recurring cross-domain meta-pattern across two unrelated research threads this week (compounding-error correction AND semantic grounding): "self-referential closure cannot manufacture the property it's missing; only an external/independent channel can." Worth flagging as a standing structural heuristic for future cell design — before proposing any correction/enrichment mechanism, ask whether its signal is actually independent of (not just a transformation of) the thing it's meant to correct or ground.

**Also connects to the distillation-ban discussion.** The literature gives a sharper, more precise reason the distillation-from-external-text-model path is not just rule-violating but likely **not a real fix even if permitted**: per Coelho Mollo & Millière (2023, "Vector Grounding Problem") and Lyre (2024, "epistemic parasitism"), an external text model's embeddings encode relational/distributional structure that is itself parasitic on human authors having already grounded that text through embodied/causal experience — the model rides on human-grounded traces baked into the corpus, it does not independently ground anything. Distilling from it would import **second-hand, laundered relational structure that LOOKS grounded (better completions, richer similarity structure) without actually solving the self-containment problem** — the substrate would still have no exogenous channel of its own; it would just have a denser, better-shaped hollow skeleton. This reframes the ban from "compliance cost" to "not even the fix you'd hope it is" — there is no real efficacy loss from staying self-contained on this specific dimension, since the banned move wouldn't deliver primary grounding anyway.

---

## (e) Substrate-product implications

1. **Framing discipline**: do not describe the current relational-graph encoder as "understanding language" or as building toward it via more relational data alone — that is the exact overclaim the "substrate knows nothing / stop testing against language" foundational anchor already warns against, now with a precise mechanistic reason (structural ceiling, not a scale problem). Frame it instead as: "learns relational/topological structure — real, useful, and near-ceiling for taxonomic/analogical tasks; does not carry perceptual/referential content by construction."
2. **Encoder eval axis split**: the "085 sparse algebra / native perception" encoder goals should track TWO distinct eval axes going forward, since the literature says these have different ceilings and respond to different interventions: a relational/taxonomic axis (near-ceiling already, don't over-invest) and a grounded-attribute/perceptual axis (currently near-zero by design, requires an exogenous channel to move at all).
3. **Buildable, self-contained grounding path exists and does not require an external LM**: small externally-fed numeric/attribute seed set (Prediction B) + an exogenous non-self-authored training signal (any real measured data stream, sensor log, or intervention-style before/after pair — NOT another model's embeddings) + the causal/index diagnostic (Prediction C) as a standing verification gate before any future claim of "the encoder now has real meaning." This satisfies the self-contained rule (external = a raw non-symbolic data channel, not another language model) while directly answering the literature's minimal-grounding bar (Harnad's categorical-perception threshold: an elementary symbol set grounded via non-symbolic discrimination, with everything else inheriting transitively).
4. **Multi-perspective triangulation as a cheap secondary channel**: per Steels' language-game and emergent-communication literature, feeding the SAME atom through >=2 structurally-independent data channels (not just one relational-edge type) — e.g. a co-occurrence-graph relation channel AND a separate independently-sourced numeric/statistical feature channel — gives a second, cheaper form of grounding pressure (the encoder must reconcile two independent "views," which per the ML literature is what drives referential precision in multi-agent grounding, without needing a body or an LM).

---

## (f) Citations (verified count: 20 distinct sources cited across 4 sub-agent reports, cross-checked for consistency; confidence-flagged per sub-agent)

**Hub-and-spoke / semantic neuroscience:**
- Lambon Ralph, Jefferies, Patterson, Rogers, "The neural and computational bases of semantic cognition," *Nat Rev Neurosci* 2017.
- "Mapping the Multiple Graded Contributions of the ATL Representational Hub," *Cerebral Cortex* 2016 (PMC5066834).
- "The anterior temporal lobes are critically involved in acquiring new conceptual knowledge" (PMC3884130).
- Rogers, Lambon Ralph, Garrard, Bozeat, McClelland, Hodges, Patterson, "Structure and deterioration of semantic memory," *Psychol Rev* 2004.
- "Effect of congenital blindness on the semantic representation of some everyday concepts," *PNAS* 2007 (PMC1895936) — the load-bearing empirical result (23% vs 0% color-variance finding).
- "BLIND: a set of semantic feature norms from the congenitally blind," *Behav Res Methods* 2013.
- "Phonological Feature Abstraction Before 6 Months" (PMC11733024).
- "A test of indirect grounding of abstract concepts using multimodal distributional semantics," *Frontiers in Psychology* 2022 (PMC9577286).

**Symbol grounding problem:**
- Harnad, "The Symbol Grounding Problem," *Physica D* 42:335-346, 1990 — load-bearing, high confidence, directly sourced.
- Bender & Koller, "Climbing towards NLU," ACL 2020 — the octopus test.
- Coelho Mollo & Millière, "The Vector Grounding Problem," arXiv:2304.01481, 2023.
- Lyre, "Understanding AI: Semantic Grounding in LLMs," arXiv:2402.10992, 2024.
- Cangelosi & Riga, symbol grounding transfer, 2006.
- Moulin-Frier et al., "Grounding the Meanings in Sensorimotor Behavior using RL," *Frontiers in Neurorobotics* 2012 (medium confidence, not full-text verified).
- Marocco et al., simulated iCub language-motor grounding, 2010 (medium confidence).

**Distributional-hypothesis ceiling:**
- Mohammad et al., antonym/synonym confusion in distributional models, *Computational Linguistics* 39(3), 2013.
- Derby et al., "Feature2Vec," arXiv:1908.11439, 2019.
- Porada et al., physically-grounded plausibility judgments, arXiv:1911.05689, 2019.
- Bruni, Tran, Baroni, "Multimodal Distributional Semantics," *JAIR* 2014.
- Silberer & Lapata, "Grounded Models of Semantic Representation," EMNLP 2012; "Learning Grounded Meaning Representations with Autoencoders," ACL 2014.
- Lazaridou, Pham, Baroni, "Is this a wampimuk?", 2015 (+ multimodal skip-gram 2014-16).
- Abdou et al., "Can Language Models Encode Perceptual Structure Without Grounding? A Case Study in Color," arXiv:2109.06129, 2021 (medium confidence on magnitude, high on direction).
- Andrews, Vigliocco, Vinson, "Integrating experiential and distributional data to learn semantic representations," *Psychol Rev* 116(3), 2009.
- Louwerse, Symbol Interdependency Hypothesis, *Topics in Cognitive Science* 2011.
- Bender, Gebru et al., "On the Dangers of Stochastic Parrots," FAccT 2021.

**Embodied cognition / minimal grounding channels:**
- Barsalou, "Perceptual Symbol Systems," 1999 — foundational, high confidence.
- Günther et al., "Symbol Grounding Without Direct Experience," *Cognitive Science* 2018 — load-bearing for the transitive-inheritance mechanism (Prediction B).
- Yu & Smith, cross-situational statistical word learning, 2007/2012 (+ 15-yr review, PMC10400455).
- Baldwin, joint-attention/gaze-following in word learning, 1991/1995.
- Markman, mutual exclusivity bias; Landau/Smith/Jones, shape bias.
- Steels, language games / multi-robot grounding, 1997-2012.
- Lazaridou et al., emergent-communication referential games, 2022 (+ review arXiv:2407.03302).
- Friston, predictive coding / free-energy principle, 2010 (+ world-models review arXiv:2301.05832).
- Ahuja et al., interventional causal representation learning, arXiv:2209.11924, 2023; Bengio et al., "Towards Causal Representation Learning," 2021 — load-bearing formal separation (observational under-identifies, intervention identifies).
- Peirce icon-index-symbol distinction (SEP); recent info-theoretic gloss arXiv:2606.06380 (flagged as very recent/less vetted — treat as a promising framing, not an established protocol).

**Confidence flags applied per calibration rule**: high-confidence items (Harnad 1990, Bender & Koller, the congenitally-blind PNAS 2007 result, Rogers/Lambon Ralph 2004, Bruni/Baroni 2014, Silberer & Lapata, Yu & Smith, Ahuja/Bengio causal-ID) form the load-bearing spine of this note's HEADLINE claim. Medium/lower-confidence items (2025-26 arXiv papers not yet peer-reviewed, robotics grounding papers not full-text-verified, the Peirce info-theoretic gloss) are used only to motivate buildable directions, not the core claim, and their P estimates are capped at 0.50 per the novel-synthesis rule.

---

## Open question (sharpest)

Does transitive grounding-inheritance (Günther et al.'s human-semantic-memory finding, and the ATL's graded-hub-gradient structure) actually occur in an artificial relational/HD encoder the way it does in biological semantic memory — i.e., does attaching real exogenous grounding to a SMALL seed set propagate usefully to neighboring atoms via existing relational training, with the right distance-decay signature? No literature directly tests this in an HD/graph-embedding artificial system. This is genuinely uncharted (novel-synthesis, P capped at 0.50 per calibration rule) and is the highest-leverage next experiment: it's cheap (small seed set, reuses existing relational training pipeline), directly falsifiable (Prediction B thresholds above), and if it HARD-PASSes, gives a concrete, minimal, self-contained recipe for real grounding without an external LM. If it HARD-FAILs, it would suggest our specific relational-encoder architecture (near-random atom codes + graph-task training) lacks the compositional structure that lets biological semantic memory propagate grounding transitively — a genuinely different and more serious architectural finding.
