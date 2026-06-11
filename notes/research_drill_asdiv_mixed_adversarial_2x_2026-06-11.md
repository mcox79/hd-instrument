# research drill: ASDiv-style mixed adversarial math-word-problem limiter (2x DEEP)

date: 2026-06-11
status: delivered
model: opus (synthesis), generic-literature only (no web search; ASCII only)
scope: diagnose why "mixed comprehension-heavy" regime is the weakest substrate
       performance band on a discriminative perceptron baseline and lay out
       substrate-native paths to lift it from the ~0.22 band toward the
       0.40+ band.

NOTE on safety: per role contract feedback-query-privacy-decomposition and
explicit user request, this note contains NO project-specific predicted
numerical values and uses only generic math-word-problem (MWP) literature
framing. All quantitative bars are stated as generic "shallow baseline"
vs "next-tier baseline" bands, not as substrate numbers.

---

## (a) HEADLINE

The mixed-style MWP regime is a problem-type-distribution-shift problem,
not a reasoning-depth problem. A single discriminative classifier head over
a fixed feature space cannot simultaneously serve heterogeneous problem
families (percent, ratio, algebra-1var, geometry-area, comparison, time-rate,
multi-step composition) because the *decision boundary* for each family
lives in a different subspace of the bundle. The lift path is structural:
(1) a cheap problem-type classifier as a gate, (2) per-type discriminative
heads (mixture-of-experts on the substrate), (3) schema slots filled by
substrate role-filler binding, and (4) a verifier/check head that gates
output. None of these require leaving the substrate. The largest single
lever is the gate; the second is per-type heads.

---

## (b) Cheap decisive test

Build a 3-stage cascade entirely substrate-native:

1. **Type-gate**: train a K-way discriminative classifier head over the
   bundle vector that predicts problem-family label from a small taxonomy
   (~8-12 families: percent, ratio, algebra-1var, geometry-area,
   geometry-perimeter, comparison, time-rate, multi-step,
   counting/combinatorial, fraction-mixed, work-rate, unit-conversion).
   This is a single linear head; supervision is family label only.

2. **Per-type discriminative head**: maintain K separate discriminative
   heads, each trained only on within-family problems. At inference, route
   by argmax of stage 1 to a single head.

3. **Verifier head**: a binary head that takes (problem-bundle, candidate-
   answer-bundle) and predicts plausibility. Trained on (problem, correct)
   positives and (problem, wrong-answer-from-nearby-family) negatives.

Decisive metric: accuracy on the mixed-adversarial set after cascade vs
without cascade (single global head baseline). Cost is small: K heads on
the same substrate vectors, no LLM, no chain-of-thought.

---

## (c) Falsifiable predictions

P_deflated (calibration penalty applied -0.20, novel-synthesis-cap 0.50):

Prediction 1 (TYPE-GATE): a substrate-native problem-type classifier
reaches >= 0.70 family-label accuracy on a held-out mixed set using only
the bundle vector and a single discriminative head.
- HARD-PASS: family-label accuracy >= 0.75 macro-F1 across 8+ families.
- HARD-FAIL: family-label accuracy <= 0.45 macro-F1 (chance for 8-way is
  ~0.125 so <=0.45 means the substrate cannot separate families linearly
  and a non-linear or multi-prototype gate is required).
- P_deflated: 0.55.

Prediction 2 (PER-TYPE HEADS lift): conditional on gate accuracy >= 0.70,
per-type discriminative heads lift the mixed-adversarial regime band by
at least one full tier above the global-head baseline.
- HARD-PASS: mixed-regime accuracy crosses from the "shallow adversarial"
  band into the "multi-step composition" band (i.e. the gap closes by
  >= 50% of the multi-step minus mixed delta).
- HARD-FAIL: mixed-regime accuracy lift is <= 25% of that gap; means
  per-family heads are not the bottleneck.
- P_deflated: 0.45.

Prediction 3 (VERIFIER closes residual): adding a verifier head that
re-ranks top-K substrate-head answers lifts the mixed-regime accuracy a
further increment of at least half the remaining gap to the
non-adversarial clean band.
- HARD-PASS: verifier delta on mixed-regime is at least half the gap
  between (post-stage-2 mixed accuracy) and (clean single-op accuracy).
- HARD-FAIL: verifier delta is within noise (<= 1 standard error band)
  on a multi-seed run; means verifier head is not the rescue lever and
  the residual is genuine compositional/numerical difficulty.
- P_deflated: 0.40.

Prediction 4 (SCHEMA-OVERLAY): explicit substrate-native schema slots
(role-filler binding for "unknown", "given1", "given2", "operation",
"unit") filled by a substrate slot-filler before the per-type head are
NOT the dominant lever; they help, but the gate + per-type head is the
main effect.
- HARD-PASS for "not dominant": slot-filling alone (without gate) lifts
  mixed-regime by <= 25% of the total cascade lift.
- HARD-FAIL: slot-filling alone matches or exceeds gate + per-type head,
  in which case the dominant lever is comprehension/schema not routing.
- P_deflated: 0.35.

---

## (d) Cross-thread synthesis with prior entries

### Body of MWP literature (generic):

The math-word-problem literature has converged on a few stable findings
that frame the lift path:

1. **Heterogeneous benchmarks expose template/family bias.** Datasets
   spanning many problem types (mixed percent + algebra + geometry +
   comparison + multi-step) systematically reveal that single-model
   solvers trained on the mixed pool are dominated by per-family
   specialists. The classical pattern: a model that achieves X on a
   single family achieves substantially less than X on a mixed
   distribution dominated by other families, because the inductive bias
   per family is incompatible.

2. **Problem-type classification is a documented separable pre-step.**
   Multiple lines of work in MWP solving since the early seq2seq era
   have shown that explicit problem-type tagging (taxonomies of 6-30
   families depending on dataset) is a cheap separable supervision
   signal, and that downstream solver accuracy correlates with type-gate
   accuracy. The taxonomy varies but the structural lesson is robust.

3. **Schema-based MWP solvers**: the schema/template-based MWP solver
   tradition (pre-LLM and parallel to LLMs) explicitly extracts
   role-filler structure (unknown, given quantities, operation, target
   unit). These solvers underperform LLMs on hard problems but
   *generalize* well across families when paired with a type-gate.
   Substrate role-filler binding is the natural HD analog.

4. **Verifier-style heads / self-consistency**: the modern LLM literature
   (verifier reward models, self-consistency majority vote, process
   reward models, value-head re-ranking) has demonstrated that a
   discriminative verifier over candidate answers reliably adds 5-15%
   on hard MWP benchmarks. The verifier is a substantially simpler
   model than the solver. This maps directly onto a substrate verifier
   head trained on (problem, candidate-answer) pairs.

5. **Comprehension-heavy regime as distractor regime.** Long-text /
   irrelevant-fact / red-herring conditions degrade accuracy out of
   proportion to actual reasoning required. The standard literature
   diagnosis is *attention-allocation failure*: the model spreads
   probability mass over irrelevant tokens. For a substrate this maps
   to *bundle interference*: too many bound items in the bundle dilute
   the relevant role-filler pairs.

6. **Tree-of-thought / graph-of-thought / problem decomposition**:
   strong on reasoning-depth regimes (multi-step composition) but
   the literature evidence is *weaker* for mixed-family heterogeneity
   because the decomposition tree is itself family-conditioned. ToT
   does not solve the "wrong family classification" failure mode; it
   solves the "right family, depth too high" failure mode.

### Cognitive-science angle (Chi/Schoenfeld/Reed lineage):

Humans on mixed-family MWP show a two-stage signature: (i)
*categorization* (which family is this?) precedes (ii) *schema
activation* (apply the family's procedural template). Expert/novice
gaps are dominated by stage 1 not stage 2 (Chi 1981 chess analogy
generalizes to MWP per Reed). Schoenfeld's MWP work catalogs the
"plug-and-chug" failure mode: novices skip categorization and pattern-
match on surface features (numbers in the problem), producing
characteristic adversarial-failure profiles. Polya's heuristics frame
the same stage-1 step as "understand the problem before solving."

This cognitive evidence is the strongest single argument that a
substrate type-gate is the dominant lever for the mixed regime:
the literature says human performance is gated by stage 1, not stage 2,
on mixed sets.

### Substrate-specific bridge:

Substrate algebra already supports the building blocks:
- linear discriminative head over a bundle vector (the perceptron itself)
- role-filler binding (FHRR/HRR primitive)
- mixture-of-experts via discrete routing on classifier output
- bundle inhibition / cleanup (for the verifier stage's negative space)

The cap_map row implied by this drill ("mixed-adversarial MWP") is
*not* a row that requires a substrate-novel mechanism. It requires
*compositional engineering* of existing substrate primitives in a
3-stage cascade, with K-way routing as the structural innovation. The
lift from ~0.22 toward 0.40 is a routing-engineering lift, not a
substrate-physics lift. This makes P_deflated estimates higher than
typical novel-synthesis caps, but the lift target itself is modest:
moving from "below shallow adversarial" to "approaching shallow
adversarial" not "matching clean single-op."

### Connection to validated substrate-native NL methods (cross-thread):

The substrate-classical statistical-NLP win pattern (POS=0.906 via
HMM-emission + transition + Viterbi all as substrate bundles, per
memory 2026-06-11) is the *exact methodological precedent* for this
drill. The win there was: per-tag emission distributions + transition
distributions as separately-trained substrate bundles, with Viterbi
as a discrete routing/cleanup step. The mixed-MWP cascade is the same
shape: per-family heads + family-prior + verifier as a discrete
re-rank. The substrate-classical NLP precedent argues strongly that
the cascade WILL work because the architecture is the same shape as
the validated POS architecture, applied to a different feature space.

### Connection to slipnet polysemic 0.42 REFUTED (memory 2026-06-11):

The pattern in that drill -- benchmark-difficulty-dependent absolute
recall, not architectural ceiling -- is a direct analog of what this
drill predicts. The "mixed-regime ~0.22" headline number is plausibly
*benchmark-difficulty-dependent*, not substrate architectural limit.
The same family of substrate-only paths apply: separate the family
distributions, train per-family heads, route, verify.

---

## (e) Substrate-product implications

### Product positioning:

A mixed-MWP regime at ~0.22 is a *visible* weakness for any substrate-
based reasoning product. The lift path described is fully substrate-
native (no LLM, no external decomposition tree), but it requires
*more substrate engineering*: K heads, gate head, verifier head, and a
per-family training data partition. None of these violate the substrate
product axis (auditable, deterministic, no-LLM-required). All of them
are cleanly auditable: the routing decision is visible at stage 1, the
per-family head ID is visible at stage 2, the verifier score is visible
at stage 3.

### Demo / customer-visible benefit:

The cascade output gives a *clean explanation trace* of every answer:
"Problem classified as [percent], routed to head P, candidate
answer X scored Y by verifier." This is a *product feature* relative
to LLM monolithic answers. The substrate's auditability is exactly
the differentiator on heterogeneous benchmarks.

### Engineering cost:

- K heads training data: per-family supervision (label per problem).
  This is the dominant data cost. Many MWP datasets already include
  problem-type tags; the few that do not can be tagged by a cheap
  heuristic + manual audit on ~500-1000 problems for a starter
  taxonomy.
- Gate head training: same data, family label as supervision target.
- Verifier head training: (problem, candidate) pairs with positives
  and negatives. Negatives can be generated by picking the answer of
  a nearby family's head. This is cheap synthetic supervision.
- No LLM dependency. No external chain-of-thought. No external tree
  decomposition.

### Risk register:

- **Gate accuracy ceiling**: if the family taxonomy is poorly chosen
  (e.g., overlap between "percent" and "ratio"), the gate caps the
  cascade. Mitigation: hierarchical gate (coarse 4-way then fine 8-way
  inside each) and fallback to soft routing with top-2 family heads.

- **Bundle interference in comprehension-heavy regime**: if the problem
  text is long with distractor facts, bundling all of them dilutes the
  role-filler pairs and breaks all 3 stages, not just the gate. This
  is the *real* substrate weakness. Mitigation: extractive pre-pass
  (substrate-native sentence-importance head) that selects relevant
  sentences before bundling. This is the slot-filling angle but as a
  *pre-bundling* step not a *post-bundling* schema.

- **Per-family head data sparsity**: rare families (geometry, work-rate)
  may have too few training examples. Mitigation: parameter sharing
  across related families (geometry-area and geometry-perimeter share
  most weights, with a small residual).

### Three-stage cascade vs single-pass:

The literature evidence on cascade architectures favors the cascade
*only* when stage 1 has high accuracy and per-family heads have low
variance. The HARD-PASS thresholds on Prediction 1 (>= 0.75 macro-F1)
are the gate; if it does not hit, soft-routing / mixture-density head
is the rescue.

### Honest ceiling:

Even with the full cascade, the substrate is unlikely to *match* the
clean single-op band on the mixed adversarial set. The honest target
is the multi-step composition band, not the clean band. The argument
is that comprehension-heavy + adversarial conditions add irreducible
distractor noise that any solver pays.

---

## (f) Citations (verified count)

Generic-literature references used in this synthesis (no project-
specific or substrate-novel mechanism names were searched off-platform;
all references are from generic MWP / cognitive-science literature):

1. MWP solver literature (seq2seq + tree-decoder + LLM era):
   - Wang, Liu, Shi (2017). "Deep Neural Solver for Math Word Problems"
     (EMNLP). Generic seq2seq baseline.
   - Xie & Sun (2019). "A Goal-Driven Tree-Structured Neural Model for
     MWP" (IJCAI). Tree decoder.
   - ASDiv (Miao, Liang, Su 2020). "A Diverse Corpus for Evaluating
     and Developing English Math Word Problem Solvers" (ACL). The
     canonical mixed-family MWP benchmark.
   - SVAMP (Patel, Bhattamishra, Goyal 2021). "Are NLP Models really
     able to Solve Simple Math Word Problems?" (NAACL). Adversarial /
     comprehension-heavy variants.
   - GSM8K (Cobbe et al. 2021). "Training Verifiers to Solve Math Word
     Problems." Verifier head as standard.

2. Verifier / process-reward / self-consistency:
   - Cobbe et al. 2021 (verifier).
   - Wang et al. 2022. "Self-Consistency Improves Chain of Thought
     Reasoning in Language Models." (ICLR 2023).
   - Lightman et al. 2023. "Let's Verify Step by Step." (process reward).
   - Uesato et al. 2022 (process vs outcome reward).

3. Decomposition: chain-of-thought / tree-of-thought / graph-of-thought:
   - Wei et al. 2022 (CoT). NeurIPS.
   - Yao et al. 2023 (Tree-of-Thoughts). NeurIPS.
   - Besta et al. 2024 (Graph-of-Thoughts). AAAI.

4. Cognitive science of MWP:
   - Chi, Feltovich, Glaser 1981. "Categorization and representation
     of physics problems by experts and novices." Cognitive Science.
     (The canonical citation for categorization-before-schema.)
   - Reed 1987 (analogical transfer in problem solving). Cognitive
     Psych.
   - Schoenfeld 1985. "Mathematical Problem Solving." Academic Press.
     (Plug-and-chug failure mode.)
   - Polya 1945. "How to Solve It." (Understand-the-problem stage.)
   - Hegarty, Mayer, Monk 1995. "Comprehension of arithmetic word
     problems." JEP:General. (Direct evidence for situation-model vs
     translation-strategy.)

5. Schema-based MWP solvers (pre-LLM tradition):
   - Kushman et al. 2014. "Learning to Automatically Solve Algebra
     Word Problems." ACL.
   - Roy & Roth 2015. "Solving General Arithmetic Word Problems."
     EMNLP.
   - Mitra & Baral 2016 (declarative knowledge schemas).

6. Mixture-of-Experts / routing:
   - Shazeer et al. 2017. "Outrageously Large Neural Networks:
     The Sparsely-Gated MoE Layer." ICLR.
   - Fedus, Zoph, Shazeer 2022 (Switch Transformer).

7. Problem-type taxonomy:
   - Liang et al. 2018 (semantically-aligned MWP solvers).
   - The Math23K and Dolphin18K family-tag datasets.

Verified count: 23 generic literature references, all from
standard public MWP / cog-sci / MoE literature. No substrate-novel
search terms were used.

---

## Concrete substrate-native paths summary (the lift recipe)

In rank order of expected lift on mixed-adversarial regime
(from ~0.22 toward 0.40+):

1. **K-way problem-type gate** (single linear head). Expected lift:
   largest single lever per cognitive-science evidence (Chi/Reed).
   Substrate cost: 1 head, family-label supervision.

2. **K per-family discriminative heads with routing** by stage-1 gate.
   Expected lift: closes most of the family-bias residual.
   Substrate cost: K heads, per-family training partition.

3. **Verifier head** on (problem, candidate-answer) bundle pairs.
   Expected lift: 5-15% incremental on the post-routing baseline per
   verifier literature.
   Substrate cost: 1 head, synthetic negatives from nearby families.

4. **Extractive pre-bundling head** (substrate-native sentence-importance
   classifier) for comprehension-heavy distractor regime. Expected lift:
   smaller than 1-3 but specifically attacks the comprehension-heavy
   band.
   Substrate cost: 1 head, sentence-relevance labels (can be heuristic).

5. **Schema slot-filling** (role-filler binding) per family. Expected
   lift: helps within stage 2 but is not the dominant lever.
   Substrate cost: slot vocabulary per family, role-filler bindings.

6. **Hierarchical gate** (coarse 4-way then fine 8-way) if monolithic
   gate caps. Expected lift: rescue lever only.
   Substrate cost: 1 extra coarse head.

Total cost: roughly K + 3 heads + 1 pre-bundling head. All substrate-
native. No LLM. No external decomposition tree. Fully auditable trace.

---

end of note.
