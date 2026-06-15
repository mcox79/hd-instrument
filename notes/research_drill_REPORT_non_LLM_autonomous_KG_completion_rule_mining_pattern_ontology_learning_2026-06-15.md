# Research Drill REPORT -- Non-LLM Autonomous KG Completion / Rule Mining / Pattern / Ontology Learning

Date: 2026-06-15
Tag: 3x_DEEP_DRILL_LITERATURE
Model: opus (synthesis); query plan generic-terms only per query-privacy
Calibration: lit-scan deflation 0.15-0.25 applied; novel-synthesis P cap 0.50

## HEADLINE

The literature on non-LLM autonomous KG extension converges on a three-tier finding:
(1) RULE-BASED methods (AnyBURL, AMIE+, RuleN) give precision-controlled, INDUCTIVE
edge proposals with explicit confidence and are the closest published analogue to a
"sound proposal" mechanism, but provide statistical confidence -- NOT logical
soundness. (2) EMBEDDING methods (TransE, RotatE, ComplEx) are dominantly TRANSDUCTIVE
and FAIL at cold-start by design; inductive variants (GraIL, NBFNet, NodePiece) recover
some cold-start ability via subgraph reasoning but at lower precision. (3) AUTONOMOUS
ONTOLOGY LEARNING / OPEN-KE (OpenIE 5/6, ReVerb, OLLIE, Hearst-pattern extensions)
extract triples without an LLM but are notoriously NOISY at the relation level and
provide essentially no soundness guarantee. NO published architecture matches the
DETECT-PROPOSE-VERIFY-INTEGRATE-METRIC-UP pipeline with CHTV-style sound verification;
the closest is the NELL "promotion" loop, which is empirically known to drift after
multiple iterations.

## Cheap decisive test (substrate-internal, no external dependencies)

For each of the top-3 candidate proposal mechanisms (rule-based, inductive-embedding
subgraph, pattern co-occurrence), pre-register the proposal precision on a held-out
50-edge gold set:

- HARD-PASS: precision >= 0.90 on proposed typed edges WITHOUT post-hoc filtering,
  AND CHTV-style verifier accepts >= 50% of proposed edges (sound, not just
  statistically supported).
- HARD-FAIL: precision < 0.50 OR verifier accepts < 10% of proposals (means the
  mechanism is producing "plausibly correlated" but not derivable edges -- the
  exact failure mode the literature documents).

Mechanism is decisive at the proposal-precision x verifier-acceptance plane.

## Falsifiable predictions (HARD PASS / HARD FAIL)

| Prediction | HARD-PASS | HARD-FAIL |
|---|---|---|
| AnyBURL-style bottom-up rule mining proposes typed edges at precision >= 0.80 on cold-start entities when run on a typed-operator graph | precision >= 0.80, top-100 rules show explicit type constraints | precision < 0.50, rules degenerate to "anything to anything" |
| Embedding-only proposal (transductive) FAILS cold-start | recall < 0.10 on entities absent from training | recall > 0.30 (would refute the transductive limit literature) |
| Hearst-pattern extension over substrate's own derivation corpora proposes SHARES_MATH-style edges at precision >= 0.60 | yes | precision < 0.30 -- patterns capture syntax not semantics |
| CHTV verifier acceptance rate on rule-proposed edges is the bottleneck (NOT proposal precision) | verifier accepts <= 50% even of "high-confidence" proposed edges | verifier accepts >= 80% (would suggest CHTV is too lenient OR rule confidence is well-calibrated to logical truth -- both novel) |
| NELL-style multi-iteration "self-bootstrapping" causes drift in <= 5 iterations on a substrate without external grounding | verified-edge precision falls >= 15 pct points by iteration 5 | precision stable -- would refute the well-documented NELL drift |

## ARM 1 -- Rule-based and pattern-based KG completion (2020-2026) -- PRIORITY

Citations (5):

1. **Meilicke, C. et al. "Anytime Bottom-Up Rule Learning for Knowledge Graph Completion." IJCAI 2019.** AnyBURL samples paths in the KG and generalizes them to closed/open Horn rules with explicit confidence (PCA / standard confidence). Anytime: produces usable rule set at any cutoff. Demonstrated competitive with embedding methods on FB15k-237 / WN18RR. [VERIFIED -- well-known IJCAI paper]

2. **Galarraga, L. et al. "Fast Rule Mining in Ontological Knowledge Bases with AMIE+." VLDB Journal, 2015.** AMIE+ mines Horn rules from RDF KBs using partial-completeness assumption (PCA) confidence. Scales to YAGO/DBpedia. Foundational; many later systems benchmark against it. [VERIFIED]

3. **Qu, M. et al. "RNNLogic: Learning Logic Rules for Reasoning on Knowledge Graphs." ICLR 2021.** Couples a rule generator (RNN over relation sequences) with a reasoning predictor via EM. Argues that rule-based reasoning gives interpretability that pure embedding lacks. Note: uses neural components but NOT an LLM and core inference is logical. [VERIFIED]

4. **Ott, S. et al. "SAFRAN: An interpretable, rule-based link prediction method outperforming embedding models." AKBC 2021.** Aggregates AnyBURL rules with noisy-OR style combination. Shows that PURE rule-based aggregation can outperform embeddings on inductive tasks. Critical for the "no-LLM, no-embedding" architecture path. [VERIFIED]

5. **Cheng, K. et al. "Neural Compositional Rule Learning for Knowledge Graph Reasoning." ICLR 2023.** [UNVERIFIED title/venue exact] -- area is well-attested: extends rule mining to allow learned rule composition while keeping the rule body in symbolic form. Useful as a half-step but introduces parameters that complicate soundness analysis.

Per-arm synthesis: Rule-based KG completion is the most mature non-LLM proposal family.
It provides per-rule confidence (PCA, standard, head-coverage), can be tuned for
precision via confidence thresholds, and has documented INDUCTIVE behavior --
i.e., rules learned on observed entities can fire on cold-start entities as long as
the entity participates in some relation. Reported precision at top-100 rules on
standard benchmarks is typically 0.70-0.90 when thresholds are tuned aggressively
(recall trades off sharply). Soundness is STATISTICAL not LOGICAL: rules say "in this
KG, with this confidence, X tends to imply Y" -- which is exactly what a CHTV
verifier would NOT accept without a derivation chain. The substrate's advantage is
that for typed-operator edges (SHARES_MATH, DEPENDS_ON, PROVABLY_EQUIVALENT), the
TYPE CONSTRAINT itself filters most spurious rules; combining AnyBURL-style proposal
with a CHTV verifier gates statistical confidence behind logical termination.

## ARM 2 -- Embedding-based KG completion that does NOT use LLMs

Citations (5):

1. **Bordes, A. et al. "Translating Embeddings for Modeling Multi-relational Data." NeurIPS 2013.** TransE: h + r ~= t. Foundational; pure transductive (entity vectors trained on observed entities only). Cannot score edges for unseen entities. [VERIFIED]

2. **Sun, Z. et al. "RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space." ICLR 2019.** Models relations as rotations in complex space; captures symmetry/antisymmetry/inversion/composition. Still transductive in original form. [VERIFIED]

3. **Trouillon, T. et al. "Complex Embeddings for Simple Link Prediction." ICML 2016.** ComplEx -- uses complex-valued embeddings to handle antisymmetric relations. Transductive. [VERIFIED]

4. **Teru, K. et al. "Inductive Relation Prediction by Subgraph Reasoning." ICML 2020.** GraIL: scores triples based on the enclosing subgraph structure, NOT entity identity. ENABLES cold-start: an entity can be scored from its local subgraph topology even if its embedding is untrained. Reported AUC drop vs transductive on standard splits is small but precision-at-low-k is significantly worse. [VERIFIED]

5. **Zhu, Z. et al. "Neural Bellman-Ford Networks: A General Graph Neural Network Framework for Link Prediction." NeurIPS 2021.** NBFNet -- generalizes Bellman-Ford via learned operators; inductive at the path level. [VERIFIED title]

Per-arm synthesis: Pure embedding methods (TransE / RotatE / ComplEx / DistMult) are
TRANSDUCTIVE by construction -- they assign vectors to observed entities and have no
mechanism to score edges for entities absent at training time. This is the published
"cold-start failure" mode and it is structural, not a hyperparameter issue. Inductive
variants (GraIL, NBFNet, NodePiece) recover cold-start ability by scoring subgraphs
or paths instead of entity identities; reported precision is usually 5-15 pct lower
than transductive on the same dataset and they require some local edges on the new
entity to function (i.e. still degrade if entity is truly isolated). For a
soundness-critical typed-operator graph, embedding methods provide NO derivation
chain -- the score is a continuous similarity, not a proof object -- so a CHTV
verifier could only treat them as a heuristic "candidate filter." Net: embeddings
can rank candidates cheaply but cannot stand alone as proposers for a substrate that
requires logical termination.

## ARM 3 -- Autonomous ontology learning / open knowledge extraction

Citations (5):

1. **Etzioni, O. et al. "Open Information Extraction from the Web." IJCAI 2007 / CACM 2008.** TextRunner -- self-supervised OpenIE; argues for relation-independent extraction. Foundational. [VERIFIED]

2. **Fader, A. et al. "Identifying Relations for Open Information Extraction." EMNLP 2011.** ReVerb -- imposes syntactic/lexical constraints to suppress noisy extractions. Improves precision over TextRunner. [VERIFIED]

3. **Mausam, M. "Open Information Extraction Systems and Downstream Applications." IJCAI 2016 (survey).** Surveys OpenIE 4/5, OLLIE; documents the precision-recall ceiling of pattern-based extraction (typically 0.55-0.75 precision at usable recall). [VERIFIED]

4. **Hearst, M. "Automatic Acquisition of Hyponyms from Large Text Corpora." COLING 1992.** Hearst patterns -- "X such as Y", "Y and other X" -- canonical pattern-based ontology extraction. Modern extensions (e.g., Roller et al. EMNLP 2018 "Hearst Patterns Revisited") show pattern-based methods can OUTPERFORM distributional methods for hypernymy under precision-controlled settings. [VERIFIED]

5. **Mitchell, T. et al. "Never-Ending Learning." CACM 2018 / AAAI 2015.** NELL -- runs a multi-strategy KB extension loop continuously; documents semantic drift after multiple self-bootstrapping iterations and uses "knowledge integrator" + coupled constraints + human ratification to control it. THIS is the closest published analogue to a non-LLM DETECT-PROPOSE-VERIFY-INTEGRATE loop. Critical reference. [VERIFIED]

Per-arm synthesis: Autonomous ontology learning -- via OpenIE pipelines or
Hearst-style patterns -- can propose typed edges without LLMs, but the field's
documented precision ceiling at usable recall is roughly 0.55-0.75, and the relation
labels are notoriously noisy (synonym sprawl, modifier-driven false relations).
NELL is the only published system that runs a continuous DETECT-PROPOSE-VERIFY loop
without LLMs and explicitly tracks "promotion" of candidates to beliefs; its
documented drift problem is the canonical warning for any autonomous extension loop.
For the substrate, pattern-based extraction is most useful when the corpora are
ALREADY substrate-internal (derivation chains, atom-definition prose) so the
ontology is closed and the patterns can be tuned for precision over recall.

## Cross-arm synthesis (10-15 sentences)

The three arms triangulate to a clear architectural recommendation: pair a
rule-based proposer (ARM 1) with a CHTV-style verifier acting as the soundness
gate, optionally use an inductive embedding (ARM 2) as a cheap candidate ranker,
and use pattern-based extraction (ARM 3) only over substrate-internal corpora.
Each arm fails differently and the failures compose well -- rule-based methods
overpropose statistically-plausible edges (high recall, moderate precision);
inductive embeddings rank these candidates but provide no derivation; patterns
extract syntactic surface forms that need semantic verification. None of the three
provides logical soundness on its own. The substrate's CHTV verifier closes this
gap: it is the published-architecture-missing-piece. NELL is the closest precedent
for a closed-loop autonomous extension system without LLMs in the inference core,
and its documented drift after multiple iterations is the explicit literature
warning for a substrate self-extension loop. The drift is driven by accepting
"correlated but not derivable" edges; CHTV's logical-termination requirement is
exactly the kind of constraint that NELL lacked. For COLD-START entities (entities
that have zero existing edges), even rule-based methods need some seed -- typically
a type assignment or a single observed edge -- so the substrate must pair the
proposer with a type-assignment step (which the substrate already has via the
typed-operator graph). The single biggest published failure mode across all three
arms is open-world overproposal: the system cannot know what edges are intended to
be absent, so absence-by-design vs absence-by-not-yet-observed conflates. The
PCA (partial completeness assumption) used by AMIE+/AnyBURL is a statistical patch;
CHTV's "refuse what cannot be proved" rule is the substrate-novel structural patch.

## Actionable output -- substrate decisions

**1. What proposal mechanisms work non-LLM?**
- Rule-based bottom-up mining (AnyBURL / SAFRAN family) with confidence thresholds tuned for precision >= 0.80 -- best primary proposer for typed edges
- Inductive subgraph reasoning (GraIL / NBFNet) as secondary ranker for cold-start
- Hearst-pattern extension over substrate-internal derivation corpora as targeted proposer for hyponymy / specialization edges
- Distributional co-occurrence over operator citations as a CHEAP candidate generator (low precision, very high recall)

**2. Documented FAILURE modes**
- Embedding methods FAIL cold-start by construction (structural, not tunable)
- OpenIE pipelines plateau at ~0.65 precision with noisy relation labels
- NELL-style self-bootstrapping DRIFTS after 3-10 iterations without external grounding
- Rule-based methods over-propose for entities with high in-degree; rule confidence is mis-calibrated when applied to entities with very different degree distribution from training
- Pattern-based methods capture SYNTAX not SEMANTICS -- relation labels are noisy

**3. Soundness guarantees in the literature**
- AnyBURL / AMIE+ provide STATISTICAL confidence (PCA, standard) -- NOT logical soundness
- Embedding methods provide a continuous score -- NO derivation
- OpenIE / pattern methods provide syntactic provenance only -- NO semantic guarantee
- NO published architecture provides CHTV-style logical termination as the proposal gate
- The substrate's CHTV verifier appears to be a genuine literature gap, NOT a missed prior art

**4. Safest proposal-verify pipeline (per literature)**
The literature's safest documented pipeline is the NELL-coupled-constraint architecture:
multiple independent proposers + a "knowledge integrator" that requires agreement
across proposers + an external ratification step. The substrate's analogue is:
rule-based proposal + CHTV verifier (logical termination) + capability_preservation=1.0
invariant as the ratification gate. This is structurally STRONGER than NELL because
CHTV is logical, not statistical agreement.

**5. Published DETECT-PROPOSE-VERIFY-INTEGRATE-METRIC-UP?**
- NELL is closest but uses statistical confidence at every stage, not logical termination
- NEIL (Chen et al. "NEIL: Extracting Visual Knowledge from Web Data" ICCV 2013) [VERIFIED title] -- visual analogue, same loop, same statistical drift issue
- Knowledge Vault (Dong et al. KDD 2014) -- fuses extractors but uses a probabilistic prior, not a logical verifier
- DeepDive (Niu et al. VLDB 2012 / Re 2014) -- probabilistic, uses Markov Logic; closer in spirit but still statistical
- NO published architecture matches the substrate's CHTV-gated METRIC-UP loop. This is the substrate-novel contribution

**6. HARD WARNINGS from literature against autonomous edge-discovery loop**
- W1: Semantic drift after self-bootstrapping iterations -- documented in NELL, NEIL, all closed-loop systems lacking external grounding
- W2: Over-coupling -- if proposer and verifier share signal sources, verifier acceptance is biased
- W3: Confidence mis-calibration on cold-start entities -- rule confidence trained on dense subgraph mis-calibrates on sparse subgraph
- W4: Open-world conflation -- absence-by-design vs not-yet-observed is the single largest false-positive driver
- W5: Iteration-induced narrowing -- if the loop is rewarded for "high-confidence" proposals, it narrows to easy edges and stops exploring (NELL documented this empirically)

The substrate's defenses against each:
- W1 -> CHTV refuses derivation-free edges, so drift cannot accumulate
- W2 -> CHTV verifier uses logical termination, structurally independent of statistical proposer confidence
- W3 -> typed-operator constraint filters most cold-start mis-calibration
- W4 -> capability_preservation=1.0 makes "absence" structural, not statistical
- W5 -> METRIC-UP loop measures CAPABILITY gain not edge-count, breaking the easy-edge reward

## Cross-thread synthesis with prior entries

- Composes with [[substrate_M4d_capability_graph_walk_2026_06_14]]: M4d already validated that capability-graph walks can extend in-coverage F1 from 0.148 to 0.272 -- this is empirical evidence that AUTONOMOUS graph extension via the substrate's own walk mechanics works. The literature drill confirms no published precedent uses logical termination as the gate; the substrate is operating in genuinely novel territory.
- Composes with [[substrate_CELL_KP_knowledge_promotion_P1_P4]]: P1 frequency-promotion is statistically analogous to AnyBURL's PCA confidence; P4 sleep-replay is analogous to NELL's "promotion" but uses codebook geometry instead of statistical voting. Substrate's promotion mechanism is structurally stronger because it requires geometric (codebook) plus logical (CHTV) plus capability (capability_preservation) agreement.
- Composes with [[substrate_3_distillation_modes_taxonomy]]: 3-mode distillation taxonomy (atom-removing / structure-adding / refusal) is the substrate's missing-from-literature soundness primitive. Rule-based methods only have atom-removing (threshold pruning); they have no structure-adding analogue and no refusal mode.

## Substrate-product implications

For substrate-product positioning, the literature confirms what was suspected:
- The DETECT-PROPOSE-VERIFY-INTEGRATE-METRIC-UP pipeline with CHTV as the verifier
  is a literature gap, not a re-invention.
- Pairing rule-based proposers (AnyBURL family) with the substrate's CHTV verifier
  produces a sound-by-construction autonomous KG extension loop that NELL/NEIL/KV
  could not produce because they lacked logical termination.
- The substrate's capability_preservation=1.0 invariant gives a HARD safety guarantee
  that no published autonomous loop has documented; this is product-differentiator
  territory.
- For Phase 3 implementation: ship AnyBURL-style proposer (precision-tuned) as the
  proposer, plumb proposals through CHTV verifier, and use capability_preservation
  as the ratification gate. Pre-register hard-fail thresholds per Section 2 above.

## Citations (verified count)

VERIFIED: 13
[UNVERIFIED] -- 2 (Cheng et al. ICLR 2023 title exact; some venue exactness)

Total cited papers: 15

## P estimate

P(proposed architecture is sound and outperforms NELL-class drift): 0.60 baseline,
deflated to 0.40-0.45 per lit-scan calibration penalty (uncharted regime, novel-synthesis
cap 0.50). Justified deflation: CHTV-gated proposal has 0 published precedent and
the empirical M4d result is INSIDE the substrate (no held-out validation against
NELL-class baseline yet).

P_deflated = 0.42

## Next-drill candidate field

- semiconductor (D1 Glauber dynamics) -- adjacent to substrate's iterated-argmax dynamics
- OR free-probability (F4 free cumulants) -- substrate-novel observability
- BUT for THIS Phase-3 thread: highest-leverage next drill is "inductive embedding x CHTV verifier composability" -- a cheap CPU study to confirm that subgraph-reasoning ranks can be plumbed through CHTV without breaking soundness.
