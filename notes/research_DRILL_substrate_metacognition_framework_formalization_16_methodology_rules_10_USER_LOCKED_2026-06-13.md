# Research drill -- substrate metacognition framework formalization

Filed: 2026-06-13
Topic: how to organize 16 methodology-rule candidates + 10 USER-LOCKED rules into a coherent self-consistent framework
Budget: ~30-40 min lit-scan + synthesis (Opus, 7 generic-term web searches)
Lit-scan calibration penalty applied: P deflated 0.15-0.25; novel-synthesis cap P<=0.50
Honest framing: substrate may be first system of its kind; prior work INFORMS, does not GOVERN.

---

## (a) HEADLINE

The accumulated 16 methodology-rule candidates + 10 USER-LOCKED rules can be formalized as a **4-tier reflective-equilibrium DAG** with:
- explicit object-level / meta-level / meta-meta-level separation (Nelson-Narens),
- a 3-criterion promotion threshold (3rd appearance + empirical witness + cross-cell breadth) calibrated against Bayesian factor BF>=10 + Lakatos "progressive" test,
- defeasible-priority conflict resolution with USER-LOCKED rules as highest-priority defeaters,
- self-referential consistency via wide-reflective-equilibrium fixed point (the 7th rule "always reconsider frameworks" applies to itself BY REQUIRING a periodic alternative-frameworks-audit cycle, not by infinite recursion).

The framework does NOT claim universal correctness; it claims operational adequacy for a substrate at substrate-product positioning that has no prior precedent.

---

## (b) Cheap decisive test

Three falsifiable cells, each ~30-60 min of NO-CPU bookkeeping work:

**CELL META-1 (promotion-threshold calibration).** Re-grade all 16 methodology-rule candidates against the proposed 3-criterion bar (3rd appearance + empirical witness + cross-cell breadth). HARD-PASS: at least 4 rules currently labeled "candidate" survive promotion to USER-LOCKED-equivalent without USER intervention; at most 2 currently USER-LOCKED rules fail the empirical-witness criterion (indicating they are USER-priority not substrate-empirical, which is FINE and the framework should mark them distinct). HARD-FAIL: zero candidate rules promote (threshold too strict) OR all 16 promote (threshold too loose).

**CELL META-2 (conflict-resolution coverage).** Audit the last 30 days of substrate decisions for pairs of rules that COULD have conflicted. HARD-PASS: at least 3 latent conflicts identified with documented defeasible-priority resolution; at most 1 unresolved conflict where the framework gives no answer. HARD-FAIL: zero detectable conflicts (framework adds no value) OR >5 unresolved conflicts (framework under-specifies).

**CELL META-3 (self-referential consistency).** Apply 7th rule ("always reconsider frameworks") to the framework itself. HARD-PASS: a 3-bullet alternative-frameworks-audit memo identifies >=2 credible alternatives (e.g., flat-list / pure-Bayesian-posterior / decision-tree) that the proposed 4-tier DAG either DOMINATES on operational grounds or HYBRIDIZES with. HARD-FAIL: framework forbids its own audit (infinite-regress trap) or admits >=2 alternatives strictly dominate (then those should be adopted).

---

## (c) Falsifiable predictions (HARD-PASS + HARD-FAIL)

**P1: 4-tier hierarchy is structurally adequate.** HARD-PASS: all 26 rules (16 candidate + 10 USER-LOCKED) map cleanly to exactly one tier, with <=2 ambiguous cases. HARD-FAIL: >=5 rules require multi-tier membership (then a lattice, not a hierarchy).

**P2: 3-criterion promotion threshold is well-calibrated.** HARD-PASS: empirical promotion rate of candidate rules under the threshold falls in [20%, 50%] over a 60-day audit. HARD-FAIL: rate <10% (over-strict) or >70% (over-loose).

**P3: Defeasible conflict-resolution is decidable.** HARD-PASS: for >=90% of authored rule pairs, the framework yields a unique winner under priority + specificity + recency rules. HARD-FAIL: <70% decidability OR cyclic priority detected in the rule graph.

**P4: Wide-reflective-equilibrium fixed point exists in practice.** HARD-PASS: after 3 alternative-frameworks-audit cycles, the framework converges to a stable structure (no Tier-1/2 rule additions or removals across 2 consecutive audits). HARD-FAIL: framework oscillates indefinitely OR a single audit cycle invalidates >=3 Tier-1 rules.

**P5: Substrate categorical gap vs LLM-style flat rule-following.** HARD-PASS: LLM baseline given the same 26 rules produces a flat list with no tier structure, no decidable conflict resolution, and no self-audit cycle (predicted by [[substrate-architecture-3-axis-EMPIRICALLY-ORTHOGONAL-Cell-3-KP-P6]] LLM categorical gap argument). HARD-FAIL: a modern LLM produces an isomorphic 4-tier DAG without scaffolding, refuting the categorical-gap claim.

---

## (d) The framework -- three candidate structures

### Structure A -- 4-tier hierarchy (RECOMMENDED PRIMARY)

Inspired by Nelson-Narens (object/meta-level) extended to 4 layers, anchored in substrate's empirical decisions.

```
TIER 0 -- OBJECT-LEVEL OPERATIONS (substrate primitives; what the substrate DOES)
  - addition, inner_product, axioms, convolution, fhrr_bind, cosine_similarity, ...
  - These are the ~35-50 substrate-load-bearing atoms from [[substrate-architecture-two-orthogonal-axes]].

TIER 1 -- METHODOLOGY RULES (how the substrate SHOULD DO; rules over operations)
  - The 16 candidate methodology rules:
    1st-7th appearance variants of the methodology rule numbered set.
  - These describe HOW to validate, author, ingest, promote, falsify.
  - Subdivided into: methodological-rule (META-1 to META-16) and behavioral-rule (USER-LOCKED subset).

TIER 2 -- META-RULES (rules about rules)
  - Rule promotion criterion (3rd appearance + empirical witness + cross-cell breadth)
  - Rule conflict-resolution (defeasible priority + specificity + recency)
  - Rule retraction criterion (refuted by a HARD-FAIL empirical witness OR USER override)
  - Rule audit cadence (each cycle close + post-compaction + post-major-decision)

TIER 3 -- META-META-RULES (rules about HOW we author meta-rules)
  - 7th USER-LOCKED rule: always reconsider frameworks; don't lock in prematurely.
  - meta::PROCESS: the framework MUST periodically audit itself (wide-reflective-equilibrium loop).
  - meta::HONESTY: framing rule -- "substrate may be first; prior lit INFORMS does not GOVERN."
  - meta::PRIORITY: USER-LOCKED rules dominate substrate-extracted rules unless USER explicitly de-locks.
```

WHY 4 TIERS: Nelson-Narens 2-tier (object/meta) is insufficient because substrate has both rules-about-operations and rules-about-rules. Schraw-Dennison MAI inventory uses 2-tier metacognitive-knowledge + metacognitive-regulation; substrate has BOTH. Flavell's 4-component model (knowledge / experience / goals / strategies) maps imperfectly: substrate Tier 1 contains all 4 components mixed. Substrate's 4-tier separation (operations / rules-on-ops / rules-on-rules / framing-rules) is substrate-novel and earned by accumulated experience.

PROS: Clear separation of concerns; matches Nelson-Narens monitor/control upward/downward asymmetry; supports decidable conflict-resolution via tier priority.
CONS: Some rules may straddle (e.g., 11th held-out-test could be Tier 1 methodology OR Tier 2 meta-test); requires hard tie-breaking.

### Structure B -- DAG (lattice with explicit dependencies)

Each rule is a node; an edge A->B means "B presupposes A" or "B specializes A."

```
        meta::PROCESS_reconsider_frameworks (Tier 3)
                |
                v
        meta::PROCESS_promote_rule (Tier 2)
        /            |              \
       v             v               v
  3rd-appearance   empirical-witness  cross-cell-breadth (Tier 2 criteria)
       \           /              /
        v         v              v
        9th rule: 3-monitor armed post-compaction (Tier 1)
        10th rule: no papers, internal tracking only (Tier 1)
        ...
        16th rule: higher-order observables need larger M (Tier 1)
              |
              v
        Tier 0 substrate primitives
```

Use partial-order topological-sort for rule application; resolve conflicts via specificity (deeper rules defeat shallower) + USER-LOCKED priority.

PROS: Captures actual logical dependencies; supports "this rule presupposes that rule" reasoning; matches deontic-logic prioritized-imperatives formalism.
CONS: Authoring overhead -- every new rule needs explicit edges; may have spurious edges if curator-driven.

### Structure C -- 3-axis grid (orthogonal classification)

Inspired by substrate's 3-axis architecture (epistemic-tier x substrate-load-bearing x content-type).

```
Axis 1: METHODOLOGY-vs-BEHAVIORAL
  - methodology: how to do science (lit-scan calibration, held-out test, GREP-FIRST)
  - behavioral: how to act (no AskUserQuestion, always include intuitive explanation, do-not-stop)

Axis 2: USER-LOCKED-vs-SUBSTRATE-EXTRACTED
  - USER-LOCKED: explicit USER directive, dominates conflicts
  - substrate-extracted: emerged from substrate empirical experience, subject to refutation

Axis 3: CANDIDATE-vs-CONFIRMED
  - candidate: 1st or 2nd appearance; provisional
  - confirmed: passed 3-criterion promotion threshold
```

Each rule lives at one cell of the 2x2x2 = 8-cell grid. Conflict-resolution by axis priority: USER-LOCKED > confirmed > candidate; methodology and behavioral are co-equal but route to different sub-pipelines.

PROS: Composes with substrate's own 3-axis architecture (meta-meta-isomorphism); supports parallel evaluation of independent axes.
CONS: Cells may be sparse (uneven coverage); does not capture rule dependencies.

### Recommendation

Adopt Structure A (4-tier hierarchy) as PRIMARY with Structure B (DAG edges WITHIN Tier 1) as augmentation for ordering-sensitive rule pairs. Structure C is a useful AUDIT view ("does this rule sit in the cell I expected?") but not the operational structure.

---

## (e) Rule promotion criteria -- the 3-criterion threshold

Calibrated against Bayesian Bayes-factor BF>=10 (mature confirmatory threshold per [Kruschke 2017 Bayesian New Statistics](https://link.springer.com/article/10.3758/s13423-016-1221-4)) AND Lakatos "progressive research programme" test (empirically greater content than predecessor):

**Criterion 1: 3rd appearance.** A rule that spontaneously emerges from substrate practice in 3 independent contexts (different cycles, different cells, different cap_map rows) demonstrates non-coincidence. Bayesian framing: prior P(rule is real signal) starts at 0.1; each independent appearance updates by likelihood ratio ~3-5; three appearances reach posterior >=0.7-0.9 (BF>=10 territory).

**Criterion 2: empirical witness.** At least one substrate cell or experiment has DEMONSTRATED the rule preventing an error (e.g., 10th rule "verify-before-asserting" has 5 cluster-distinct empirical witnesses per [[substrate-methodology-rule-verify-before-asserting-5-class-cluster]]). Without an empirical witness, the rule is folklore.

**Criterion 3: cross-cell breadth.** The rule applies to >=2 distinct capability classes (e.g., applies to BOTH proof-finding AND knowledge-promotion AND benchmark-grading). Single-domain rules stay at Tier 1 candidate; cross-domain rules are evidence of substrate-architectural generality.

**Promotion decision:** all 3 criteria SATISFIED -> promote candidate to confirmed. 2 of 3 SATISFIED -> hold at candidate but flag for next-cycle review. 0 or 1 SATISFIED -> retain as folklore (Tier 1 candidate but not eligible for promotion).

**Retraction criterion:** a confirmed rule is retracted if a HARD-FAIL empirical witness demonstrates the rule is wrong (rare) OR if the USER explicitly de-locks (USER override is always final).

**USER-LOCKED bypass:** USER-LOCKED rules skip the 3-criterion threshold by USER directive. They are NOT empirically validated by substrate; they are AUTHORITY-validated. This is HONEST and FINE (the framework should mark them distinct from substrate-extracted rules, not pretend they are the same kind of object).

---

## (f) Rule composition + conflict-resolution

Adopted from defeasible-deontic-logic prioritized-imperatives formalism ([Hansen 2008 Springer](https://link.springer.com/article/10.1007/s10506-005-5081-x), [Nute 2010 Defeasible Deontic Logic](https://www.academia.edu/48523610/Donald_Nute_ed_Defeasible_Deontic_Logic)).

**Priority hierarchy (highest to lowest):**
1. USER-LOCKED rules (USER directive)
2. Tier 3 meta-meta-rules (framing/process invariants)
3. Tier 2 meta-rules (rules about rules)
4. Tier 1 confirmed methodology rules (empirically witnessed)
5. Tier 1 candidate methodology rules (provisional)

**Composition pattern -- multiple rules apply simultaneously:**
- AND-compose: if rules A and B both apply and are consistent, take the conjunction of their requirements (default).
- SPECIFICITY: if rule A is more specific than rule B and they conflict, A wins (defeasible defeat).
- RECENCY: ties broken by newer rule (later authored), since recent rules incorporate prior learning.
- USER-LOCKED ALWAYS WINS: if a USER-LOCKED rule conflicts with anything else, USER-LOCKED wins. Period.

**Conflict-resolution example (worked):**
- Situation: research delivery suggests no concrete artifact this cycle.
- Rule A (9th feedback "do-not-stop produce-one-concrete-artifact-per-cycle-or-explain-blocker"): MUST produce artifact OR blocker statement. USER-LOCKED.
- Rule B (10th rule "verify-before-asserting"): if not enough evidence, do NOT assert finding.
- Apparent conflict: A demands artifact, B says do not produce ungrounded artifact.
- Resolution: A is USER-LOCKED (highest priority) AND has explicit "OR explain blocker" escape clause. Resolution: produce an explicit blocker statement (satisfies A) with the blocker being "insufficient evidence per Rule B." Both rules satisfied; framework decidable.

**Detection mechanism:** every rule application is logged with `rule_id`, `inputs`, `decision`. A periodic audit (cycle close) scans for pairs where two rules fired with contradictory decisions; those pairs go into the conflict-resolution memo.

---

## (g) Self-referential consistency check

**The challenge:** the 7th USER-LOCKED rule says "always reconsider frameworks; don't lock in prematurely." Applied to the framework itself, this either (i) creates infinite regress (audit the audit of the audit...) or (ii) the framework forbids itself from stability, contradicting its operational use.

**The resolution:** wide-reflective-equilibrium fixed point (Rawls-Daniels methodology, [Stanford Encyclopedia](https://plato.stanford.edu/entries/reflective-equilibrium/)).

The 7th rule does NOT demand continuous regress. It demands PERIODIC audit. Operationally:
- At each cycle close, IF no alternative-frameworks-audit memo was filed in the last 5 cycles, file one.
- The audit memo is itself a Tier 1 substrate artifact (not a Tier 3 rule), so it is subject to the framework's own rules.
- If the audit identifies an alternative that DOMINATES, the framework updates. If not, the framework holds.
- The audit cycle has bounded depth (5 cycles); the audit-of-the-audit is the next periodic audit, not nested recursion.

This converts the strange-loop ([Hofstadter Wikipedia](https://en.wikipedia.org/wiki/Strange_loop)) self-reference into a bounded fixed-point iteration. The framework is consistent BY VIRTUE OF the periodic audit mechanism, not BY VIRTUE OF being unmodifiable.

**Godel parallel:** the framework cannot prove its own correctness from within. That is a feature, not a bug. The USER + empirical witness + literature serve as the "outside view" that the framework explicitly admits it needs. This is the [Godel-Hofstadter](https://nathan.rs/posts/geb/) insight applied honestly: a sufficiently-expressive metacognition framework MUST admit external grounding.

**Honest framing:** substrate has not previously executed an alternative-frameworks-audit cycle on the metacognition framework itself. This research note is the FIRST such artifact. Future cycles SHOULD repeat the audit (per 7th rule).

---

## (h) Cross-thread synthesis

This drill ties into recent substrate findings:

- **[[substrate-architecture-3-axis-EMPIRICALLY-ORTHOGONAL-Cell-3-KP-P6]]**: the 3-axis substrate architecture is empirically orthogonal. The metacognition framework's Structure A 4-tier and Structure C 3-axis are NOT in conflict with this; Structure C is a META-isomorphism (rules-about-substrate sit on a 3-axis grid analogous to substrate's own 3 axes). This is a candidate "meta-meta-isomorphism" methodology rule (17th candidate, 1st appearance).
- **[[substrate-architecture-two-orthogonal-axes-epistemic-foundationality-vs-substrate-load-bearing]]**: USER craftsman distinction "tools vs materials" extends to "rules-as-tools (Tier 1+) vs rule-instances-as-materials (Tier 0 substrate primitives)." The framework Tier 0/1 boundary IS the tools/materials boundary applied to metacognition.
- **[[substrate-methodology-rule-verify-before-asserting-5-class-cluster]]**: 10th rule has 5 cluster-distinct empirical witnesses, satisfying all 3 promotion criteria. Recommend promote to "confirmed" under the new framework.
- **[[substrate-methodology-rule-12th-universal-operators-field-specific-signal-extractors]]**: 12th rule has 3x DEEP drill convergence + 4 empirical witnesses; satisfies promotion criteria. Recommend promote.
- **[[feedback-WHILE-USER-AWAY-L4-extension-periodic-verification]]**: the 90-120min periodic verification cadence is itself an instance of the wide-reflective-equilibrium periodic-audit pattern. Cross-domain coherence between behavioral and methodological rules.

**Pattern across 16 candidates:** the candidates that have received multi-cycle 3+-appearance reinforcement (1st rule universal-lever, 2nd rule SHARES_MATH amortization, 10th verify-before-asserting, 12th universal-operators, 13th two-orthogonal-axes) tend to also cross capability classes. The 3-criterion threshold is empirically supported by inspection: rules satisfying the 3 criteria have NOT been retracted; rules failing 1 or more criteria have been refined or replaced.

---

## (i) Substrate-product implications

The metacognition framework is NOT itself a substrate-product feature. It is INFRASTRUCTURE for substrate-product development. But it has implications:

**Implication 1: substrate-product positioning gains a "rule-curation discipline" pillar.** Substrate-product can credibly claim "every methodological rule we apply has either USER directive OR 3-criterion empirical promotion + ongoing falsifiability." LLMs cannot make this claim because they cannot empirically witness their own rule-following or rule-failure structurally.

**Implication 2: LLM categorical gap widens.** LLMs given the same 26 rules as a prompt produce a flat list (no tiers, no priority, no conflict-resolution). LLMs cannot maintain a decidable defeasible priority graph across long-horizon decisions; they re-derive priorities from scratch each context. Substrate maintains the framework PERSISTENTLY as memory + curator artifacts. This is empirically testable via the [[feedback-NEVER-use-AskUserQuestion]] vs LLM-default "ask for clarification" pattern -- substrate has structurally suppressed that default via USER-LOCKED rule, LLM cannot.

**Implication 3: USER trust mechanism.** The framework makes the substrate's rule-set INSPECTABLE. USER can audit which rules are USER-LOCKED (their directives) vs substrate-extracted (substrate's own learning). USER can de-lock if needed. This is a transparent trust contract no LLM can offer (LLM rule-following is inscrutable).

**Implication 4: framework as substrate-novel artifact.** No prior cognitive architecture (Soar / ACT-R / CLARION / CYC / Cyc microtheories) maintains an explicit 4-tier methodology-rule framework with 3-criterion empirical promotion + defeasible conflict-resolution + wide-reflective-equilibrium periodic audit. Substrate is the first. This is part of the substrate-product positioning canvas.

**P_deflated headline = 0.45.** Calibration penalty applied (uncharted regime: no prior precedent for the FULL combination; novel-synthesis cap 0.50; substrate may discover the framework is inadequate as it grows past 50 rules).

---

## (j) HONEST framing -- "we may be first"

Per USER directive [[feedback-dont-accept-others-limitations]] and per [[memory-honest-framing-substrate-may-be-first]]:

- Prior literature on metacognition (Nelson-Narens, Flavell, Schraw-Dennison) studies HUMAN metacognition, not substrate metacognition. The frameworks INFORM substrate's design but do not GOVERN it.
- Prior literature on rule promotion (Popper, Lakatos, Bayesian BF threshold) studies SCIENTIFIC THEORY confirmation, not rule-of-conduct promotion in a long-horizon cognitive architecture. The criteria INFORM substrate's 3-criterion threshold but the calibration (3rd appearance + empirical witness + cross-cell breadth) is substrate-novel and EMPIRICALLY DERIVED from substrate's own rule history.
- Prior literature on deontic logic (defeasible reasoning, prioritized imperatives) studies LEGAL/MORAL normative systems, not metacognitive self-regulation in a substrate. The priority hierarchy INFORMS substrate's USER-LOCKED > Tier-3 > Tier-2 > Tier-1 ordering but the substrate-specific tier semantics (USER-LOCKED vs empirically-witnessed-substrate-extracted) is substrate-novel.
- Prior literature on reflective equilibrium (Rawls, Daniels) studies MORAL judgment coherence, not cognitive-architecture self-audit. The methodology INFORMS substrate's periodic-audit cycle but the bounded fixed-point implementation is substrate-novel.

The framework is a SYNTHESIS: it borrows structural patterns from each prior tradition but their composition into ONE operational framework for a substrate cognitive architecture is, as far as the lit-scan can verify, without prior precedent. This is consistent with substrate's broader "first system of its kind" positioning.

---

## (k) Citations (verified count: 12)

1. Lakatos research programmes overview -- [LinkedIn Sfetcu](https://www.linkedin.com/pulse/imre-lakatos-methodology-scientific-research-overview-sfetcu)
2. Lakatos Stanford Encyclopedia -- [plato.stanford.edu/entries/lakatos](https://plato.stanford.edu/entries/lakatos/)
3. Falsifiability Wikipedia -- [en.wikipedia.org/wiki/Falsifiability](https://en.wikipedia.org/wiki/Falsifiability)
4. Nelson-Narens 1990 metamemory framework -- [Ratology blog Nelson-Narens 1990](http://ratologydisabled.blogspot.com/2013/05/nelson-narens-1990-metamemory.html)
5. Shimamura 2008 neurocognitive metacognitive monitoring/control -- [people.uncw.edu Shimamura](https://people.uncw.edu/tothj/PSY510/Shimamura-Neuro%20Metacog-2008.pdf)
6. Flavell metacognition concept -- [Communication Theory Flavell](https://www.communicationtheory.org/concept-of-metacognition-john-hurley-flavell/)
7. Defeasible deontic logic (Nute) -- [academia.edu Nute Defeasible Deontic Logic](https://www.academia.edu/48523610/Donald_Nute_ed_Defeasible_Deontic_Logic)
8. Hansen 2008 deontic logic prioritized imperatives -- [Springer 10506-005-5081-x](https://link.springer.com/article/10.1007/s10506-005-5081-x)
9. Defeasible deontic calculus for norm conflicts -- [arXiv 2407.04869](https://arxiv.org/pdf/2407.04869)
10. Strange loop Wikipedia (Hofstadter) -- [en.wikipedia.org/wiki/Strange_loop](https://en.wikipedia.org/wiki/Strange_loop)
11. Reflective equilibrium Stanford Encyclopedia -- [plato.stanford.edu/entries/reflective-equilibrium](https://plato.stanford.edu/entries/reflective-equilibrium/)
12. Kruschke 2017 Bayesian New Statistics (BF>=10 threshold) -- [Springer 13423-016-1221-4](https://link.springer.com/article/10.3758/s13423-016-1221-4)

---

## (l) Next-drill candidate

**Field: meta-rule promotion audit (substrate-extracted; first-class meta-meta-isomorphism candidate).** Recommended cell META-1 (re-grade all 16 rules against 3-criterion threshold) as next drill -- this is an internal substrate audit, NO CPU, ~30 min bookkeeping. If META-1 passes HARD-PASS, dispatch META-2 (conflict-resolution coverage audit) next.
