---
problem: extract_spatial_and_causal_relations_from_prose_whole_subgraph_survival
status: PARTIAL
bar: "PASSES only with ALL of: (1) the JOINT parse-once front-end EXTENDED to SPATIAL edges (containment/relative-position/path-transfer, Figure-Ground/RCC8) AND CAUSAL edges (connective + mental-bridge + force-dynamic), as ONE structured extraction over the reader's OWN parse, NO external LLM; (2) WHOLE-SUBGRAPH SURVIVAL (fraction of gold multi-hop >=2-edge chains with EVERY edge recovered) is the headline, CI-separated over the INCUMBENT extractor on the SAME population, gate on the floor's UPPER bound, ALSO report end-to-end; (3) the info-free SHUFFLED-RELATION twin LOSES CI-separated; (4) extraction ISOLATED (each reasoner held at gold); (5) NO-regress full-stack (prototype THIS + the upstream parse to excel/exceed, no live consumer regresses); (6) one-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "SPATIAL is a WIN; CAUSAL is the bar's blessed LOCATED NEGATIVE. Extraction ISOLATED (reasoner held at gold), paired bootstrap (CI half-width + null p95). SPATIAL (SpaceEval/ISO-Space train+trial): building the brain's ACTUAL spatial-semantic mechanisms into the joint pass -- EVENT-FIGURE binding (Talmy: the Figure can be an event; SpaceEval gold uses event trajectors) + DEICTIC grounds (here/there/home) + COORDINATION distribution + PARTITIVE region-parts (heart/middle/part of Y) + HERSKOVITS preposition-semantics (at/on + place/region ground coerces to containment) over the exact-MAP parse -- lifts containment edge recall 0.2282 -> 0.2980 and whole-subgraph containment survival 6/123 = 0.0488 -> 16/123 = 0.1301, margin +0.0813 CI[+0.0244,+0.1463] null_p95 0.065 CI-SEPARATED over the incumbent; the shuffled-relation twin collapses 0/123. CRUCIAL CONTROL + finding: a no-semantics PROXIMITY floor (connect adjacent co-sentential nouns) MATCHES the joint on survival (14/123, joint-proximity +0.0163 CI[-0.0569,+0.0894] NOT CI-sep) -- so recall-survival is DENSITY-CONFOUNDED. The discriminating, brain-faithful test is PRECISION: balanced containment QA with HARD adjacent negatives (adjacent non-containment pairs proximity false-positives). There the proximity prior COLLAPSES (acc 0.1848) while the semantic joint scores 0.5712, beating proximity +0.3864 CI[+0.3527,+0.4196] AND the incumbent +0.0533 CI[+0.0408,+0.0658], both CI-separated -- the semantic Figure-Ground TYPING is decisively load-bearing (the brain distinguishes IN from NEAR; density cannot). CAUSAL (MAVEN-ERE valid, 9698 gold CAUSE+PRECONDITION edges, 710 docs, detection held constant): connective-bound extraction recovers 0.5% of gold edges (incumbent within-sentence 0.0044; joint cross-sentence 0.0052, +0.0007 CI-sep -- negligible) while pure CONTIGUITY recovers 15.2% and the connective arm LOSES to it CI-sep (-0.147); connective recall on the 65.6% UNMARKED edges is 0.0005; the SYMMETRIC precision test confirms the mechanism split -- causal TYPING beats contiguity on hard negatives (+0.33) but is recall-blind, so neither arm is good (contiguity = recall-no-precision, connective = precision-no-recall). Multi-hop causal chain survival is 0/30 (real causal networks are SHALLOW -- 30 chains in 710 docs). The residual is the UNMARKED-link discourse-coherence bridge (SDRT) + directed world-knowledge (the generative simulator) -- distinct organs. THE UNIFYING FINDING: spatial relations are lexically/syntactically MARKED (preposition + ground geometry -> RCC8), so a parse-bound semantic typer wins on precision; causal relations are largely UNMARKED, so no parse-bound typer works -- the brain infers them by recency-prior + world-knowledge + coherence."
floor: "Per channel, recomputed on the item's OWN population. SPATIAL: (a) the incumbent linear extractor (containment survival 6/123 = 0.0488; balanced-QA precision 0.5179) -- joint beats it CI-sep on BOTH; (b) the no-semantics PROXIMITY floor (survival 14/123 = 0.1138 -- MATCHES joint, exposing the density confound; balanced-QA precision 0.1848 -- COLLAPSES on hard negatives, joint beats it +0.3864 CI-sep). CAUSAL: (a) incumbent within-sentence connective 0.0044; (b) the CONTIGUITY floor 0.1522 (the connective signal LOSES to it CI-sep -- density, not causal typing, carries recall); (c) multi-hop chain survival floor 0/30. Ceiling: the reasoners near-perfect on GOLD (spatial 1.000; causal sound) = the ISOLATION control."
controls: "(1) SHUFFLED-RELATION twin loses CI-sep on BOTH channels (spatial survival 0/123; causal joint-twin +0.0035). (2) PROXIMITY / CONTIGUITY density floor (the decisive control this problem adds): matches the semantic joint on recall-survival (spatial) and BEATS the connective signal (causal) -> recall metrics are density-confounded; but COLLAPSES on the PRECISION test (spatial proximity 0.1848 on hard negatives; causal contiguity 0.139), where the semantic typing wins CI-sep -> the typing is load-bearing where PRECISION matters (the brain's competence). (3) HARD-NEGATIVE precision QA (adjacent non-relation pairs) isolates precise typing from density. (4) INCUMBENT floor per channel. (5) ISOLATION: reasoner held at gold. (6) MARKED-vs-UNMARKED split (causal) locates the residual (65.6% unmarked). (7) NO-REGRESS: nothing written to hdlab (Q111); temporal-survival witness 6/6 at HEAD; exact-MAP leaves the tense-agnostic event set byte-identical (0 symmetric-diff). Each EXCLUDES: twin=count artifact; density-floor=proximity masquerading as semantic extraction; hard-negatives=recall inflation; isolation=strong-reasoner-as-extraction; marked-split=the residual organ; no-regress=downstream regression."
files_changed: "experiments/_joint_spatial_frontend.py, experiments/exp_joint_spatial_survival_v1.py, experiments/exp_joint_spatial_precision_qa_v1.py, experiments/exp_joint_causal_survival_v1.py, verification/test_joint_spatial_causal_survival.py, notes/problems/extract_spatial_and_causal_relations_from_prose_whole_subgraph_survival/SOLVED.md (NO hdlab/ written -- Q111: proposed diff in Sec 7)"
reverify: ".venv/Scripts/python.exe verification/test_joint_spatial_causal_survival.py   # 11/11 (survival + the density-confound control + the precision-discriminator + the causal located negative, from source; ~70s)"
---

# SPATIAL: the joint semantic Figure-Ground typer WINS (beats the incumbent AND the density prior on precision); CAUSAL: a rigorous located negative -- and the unifying reason is MARKED vs UNMARKED relations

**Bottom line (revised after drilling the wall the owner pushed on -- my first "located negative on both" was PREMATURE).**
The temporal channel won whole-subgraph survival via a single detection gate (tense). I extended the same one-parse
front-end to SPATIAL and CAUSAL. For SPATIAL, building the brain's ACTUAL mechanisms (event-figure binding, deictic
grounds, coordination, partitive region-parts, Herskovits preposition-semantics) over the exact-MAP parse beats the
incumbent CI-separated on survival (6 -> 16/123) -- and, decisively, beats a no-semantics DENSITY floor on a
PRECISION test where that floor collapses (0.185 vs 0.571, +0.386 CI-sep). That precision result is the real
brain-foundational win: the semantic Figure-Ground TYPING is load-bearing (the brain tells IN from NEAR; proximity
cannot). For CAUSAL it is a rigorous located negative: causal relations are dominantly UNMARKED, so no parse-bound
extractor recovers them (connective 0.5%, contiguity 15.2% but no causal signal), and the brain's mechanism
(recency-prior + world-knowledge + discourse coherence) lives in DISTINCT organs (the filed SDRT reader + the causal
reasoner's generative simulator). Filed PARTIAL (spatial passes; causal is the blessed negative).

## 1. OPEN -- how the brain does this, and the UNIFYING mechanism finding (PINNED vs OUR-INVENTION)
- **PINNED (the shared computation).** Comprehension extracts a clause's relations JOINTLY in ONE structural pass
  (IFG structure-building -> pMTG/ATL role binding; Friederici 2017; Frankland & Greene 2015). SPACE: Talmy/Jackendoff
  Figure-Ground + Place/Path schemas; the RCC8 relation TYPE is carried by the preposition + the ground's geometry
  (Herskovits 1986 -- "in the heart of X" = containment). CAUSE: continuous causal-antecedent search during reading
  (Graesser-Singer-Trabasso constructionist theory) = a recency/contiguity PRIOR refined by directed causal
  WORLD-KNOWLEDGE + discourse coherence (Hobbs abduction; SDRT). The brain also INFERS unstated relations.
- **THE UNIFYING FINDING (why spatial wins and causal does not).** Spatial relations are LEXICALLY/SYNTACTICALLY
  MARKED -- the preposition + ground encode the RCC8 type -- so a parse-bound semantic typer recovers them with recall
  AND precision, beating a proximity prior decisively (+0.386). Causal relations are largely UNMARKED (no lexical
  signal; 65.6% of MAVEN causal edges have no connective) -- so no parse-bound typer works: connective typing is
  precise-but-recall-blind (0.5%), contiguity is recall-but-imprecise (collapses on hard negatives). The brain closes
  the causal gap with a recency prior + world-knowledge typing + coherence -- DISTINCT organs, not the front-end.
- **OUR-INVENTION-UNDER-TEST (swept).** The spatial construction inventory + preposition-semantics thresholds; the
  causal connective/contiguity binding; the deictic/partitive lexicons; the marginal gate. NOT brain-faithful
  (avoided): external LLM at inference; scoring recall-survival as the capability WITHOUT the density control (the
  trap this problem surfaces); a 19c corpus as gold.

## 2. REUSE
- REUSED + EXTENDED `hdlab.joint_relation_frontend` (parse cache + `joint_spatial_frames` + `joint_event_ranks`) in
  `experiments/_joint_spatial_frontend.py`. REUSED the incumbent `spatial_relation_extractor.extract_edges` (floor),
  `spatial_relational_model` (SpatialModel + `contains_path` reasoner, held at gold), the survival TEMPLATE. REUSED
  `hdlab.arc_parser.parse(decode='exact', want_marginals=True)` (the 2026-09-07 graded_parser) as the upstream.
  REUSED MAVEN-ERE `causal_relations` (the temporal SOLVED's power gold). The reasoners UNCHANGED (owner-DONE).

## 3. What was built (glass-box, NO LLM)
- `experiments/_joint_spatial_frontend.py` -- the extended joint SPATIAL extractor over ONE exact-MAP parse: base
  Figure-Ground frames + EVENT-FIGURE + DEICTIC-ground + COORDINATION distribution + PARTITIVE region-part + HERSKOVITS
  at/on->containment coercion + PATH/move source-goal.
- `experiments/exp_joint_spatial_survival_v1.py` -- whole-subgraph survival + the PROXIMITY density floor + twin + CI.
- `experiments/exp_joint_spatial_precision_qa_v1.py` -- the PRECISION discriminator: balanced containment QA with HARD
  adjacent negatives (the metric recall-survival cannot do).
- `experiments/exp_joint_causal_survival_v1.py` -- causal edge recovery + chain survival on MAVEN, detection held
  constant, binding varied (incumbent within-sentence / joint cross-sentence connective / contiguity floor / twin),
  marked-vs-unmarked split.
- `verification/test_joint_spatial_causal_survival.py` -- scaffold-free witness, 11/11, recomputes everything from
  source.

## 4. What was measured (deterministic, PYTHONHASHSEED=0)
**SPATIAL -- SpaceEval train+trial (123 multi-hop containment chains):**
| arm | survival | precision-QA (hard negs) | containment recall |
|---|---|---|---|
| incumbent (linear) | 6/123 = 0.0488 | 0.5179 | 0.2282 |
| **joint (semantic, exact-MAP)** | **16/123 = 0.1301** | **0.5712** | **0.2980** |
| PROXIMITY floor (no semantics) | 14/123 = 0.1138 | **0.1848 (collapses)** | -- |
| shuffled-relation twin | 0/123 | -- | -- |

- Survival: joint - incumbent **+0.0813 CI[+0.0244,+0.1463]** CI-sep; joint - twin +0.1301 CI[+0.0732,+0.1870].
  BUT joint - proximity **+0.0163 CI[-0.0569,+0.0894] NOT CI-sep** (the density confound: recall-survival rewards
  emitting many co-sentential edges).
- PRECISION QA (the discriminator): joint - proximity **+0.3864 CI[+0.3527,+0.4196]**; joint - incumbent **+0.0533
  CI[+0.0408,+0.0658]** -- both CI-sep. The proximity prior collapses (0.185) on adjacent non-containment pairs;
  the semantic TYPING correctly rejects them. This is the brain-foundational win.
- Each construction was measured additively (survival): base 6 -> +event-figure 8 -> +deictic/coordination 13 ->
  +partitive 13->16(with prep-sem). The misses were ENUMERATED on real text (96.9% co-sentential STATED -- NOT
  unstated world-knowledge), which is what refuted my premature "irreducible construction coverage" call.

**CAUSAL -- MAVEN-ERE valid (9698 gold edges, 710 docs, 34.4% marked):**
| arm | edge recall (all/marked/unmarked) | precision (hard negs) | chain survival (n=30) |
|---|---|---|---|
| incumbent within-sentence | 0.0044 / 0.0129 / 0.0000 | -- | 0/30 |
| joint cross-sentence connective | 0.0052 / 0.0141 / 0.0005 | 0.47 (recall-blind) | 0/30 |
| CONTIGUITY floor (no signal) | 0.1522 / 0.0518 / 0.2049 | 0.14 (collapses) | 0/30 |
| shuffled twin | 0.0016 | -- | 0/30 |

- joint - incumbent +0.0007 CI-sep (negligible); joint - contiguity **-0.147 CI[-0.154,-0.140]** (the causal signal
  LOSES to density on recall); connective recall on UNMARKED edges 0.0005. Symmetric precision test: causal typing
  beats contiguity +0.33 on hard negatives but is recall-blind -> neither arm is good; the brain needs BOTH (prior +
  world-knowledge typing). Multi-hop chains are vanishingly rare (30/710 docs).

## 5. FULL-STACK BRAIN-FOUNDATIONAL AUDIT (owner's ask: "make sure everything all the way up is 100% brain-foundational" -- it is NOT; here is the honest per-component scan)
| component | brain mechanism (PINNED) | what we run | fidelity | the gap |
|---|---|---|---|---|
| **POS tagger** | lexical-category access (Hagoort MUC) | learned averaged structured perceptron (Collins 2002), UD | MEDIUM | a learned proxy, not the brain's lexical access; but not the binding constraint |
| **Parser** | INCREMENTAL, PREDICTIVE structure-building (Friederici IFG; left-corner; surprisal) | exact-MAP Chu-Liu/Edmonds + Matrix-Tree marginals (graded_parser) OR greedy arc-eager | MEDIUM | the exact-MAP is MORE brain-foundational than greedy (globally-normalized, Koo 2007) and is what I route through -- but it is BATCH, not incremental/predictive. The brain-foundational parser is FILED (`...online_predictive_reader`, `close_the_recurrent_predictive_coding_loop_n400`). Not the binding constraint here (parse is 22.8% of the spatial miss). |
| **Spatial Figure-Ground typer** | Talmy/Jackendoff Figure-Ground + Herskovits preposition-semantics at the syntax-semantics interface | parse-bound semantic typer (event-figure + deixis + partitive + Herskovits at/on->in) | HIGH mechanism / MEDIUM acquisition | the MECHANISM is brain-faithful (proven load-bearing on precision, +0.386 over density); the construction inventory is HAND-CODED, whereas the brain LEARNS constructions (usage-based grammar, Goldberg/Tomasello). A learned/online construction inventory is the fidelity upgrade. |
| **Causal binder** | recency PRIOR + world-knowledge causal typing + discourse coherence (Graesser-Singer-Trabasso; SDRT; Talmy force-dynamics) | connective-matching + contiguity | LOW | connective-matching is NOT the brain's mechanism (the brain needs no connectives). The brain-foundational causal organs are FILED/prototyped: the SDRT coherence reader (unmarked links) + the causal reasoner's generative simulator (directed world-knowledge, U8). The front-end connective channel should NOT be landed as a capability. |
| **Reasoner (SpatialModel / CausalGraph)** | mental-model inspection + transitive inference (Johnson-Laird); Trabasso reachability + Pearl | as PINNED | HIGH | owner-DONE, brain-faithful. |

Honest verdict: the extraction FRONT-END is brain-foundational for SPACE (marked relations, semantic typing proven
load-bearing) but NOT for CAUSE (unmarked -> needs the SDRT + simulator organs); the PARSE is the best-available
(exact-MAP) but not yet incremental/predictive (filed); the construction inventory is hand-coded, not learned. The
one place we are fully brain-foundational and winning is the spatial semantic Figure-Ground typing over the exact-MAP
parse.

## 6. PERFORMANCE vs the brain / where we lose signal
Spatial: we now recover ~0.30 of containment edges and, crucially, TYPE them precisely (IN vs NEAR), beating a density
prior +0.386 on precision -- the brain-faithful competence. We still lose the ~55% of edges needing constructions/
world-knowledge beyond the inventory (a learned construction grammar + a place-hierarchy KB would close more). Causal:
we recover ~0.5% of edges by connectives vs the brain's near-complete unmarked inference -- the whole gap is the
world-knowledge + coherence typing the front-end structurally lacks.

## 7. PROPOSED hdlab DIFF (Q111 -- strategy lands it; NOTHING landed by me)
1. **Add the spatial semantic-typing channels to `hdlab.joint_relation_frontend`** (default-off additive): event-figure
   + deictic-ground + coordination distribution + partitive region-part + Herskovits at/on->containment. PROVEN
   load-bearing on precision (+0.386 over the density prior, +0.053 over the incumbent, both CI-sep) and CI-sep over
   the incumbent on survival. This is a real brain-foundational spatial extraction capability.
2. **Route the joint front-end's shared parse through `arc_parser` exact-MAP + marginals** (decode='exact'): the
   more-brain-foundational parser; byte-identical temporal event set (no-regress).
3. **Do NOT land a parse-bound CAUSAL extraction channel.** It recovers 0.5% and loses to contiguity. The causal
   extraction levers are the FILED SDRT coherence reader (unmarked links) + the generative simulator (directed
   world-knowledge). Wire THOSE.
4. **The spatial extraction should be scored on PRECISION (typed QA), not recall-survival alone** -- recall-survival is
   density-confounded (a methodological correction for the board's spatial instrument).

## KEY REALIZATIONS (the enabling moves; several overturned my own first conclusions)
- **A located negative only counts if the BRAIN'S mechanism, faithfully built, is what failed -- and mine was not
  built.** My first pass tested connective/construction EXTRACTION and called it a ceiling. Drilling (the owner's push)
  showed the SpaceEval misses are 96.9% STATED co-sententially via brain-foundational constructions I had not built
  (deixis, coordination, partitive, preposition-semantics). Building them turned the located negative into a CI-sep win.
- **Recall-survival is DENSITY-CONFOUNDED; the brain's competence is PRECISION.** A no-semantics proximity floor MATCHES
  the semantic joint on survival (14 vs 16/123) -- so the survival win over the incumbent is largely density. Only a
  PRECISION test with HARD adjacent negatives separates them: proximity COLLAPSES (0.185), the semantic typing wins
  +0.386 CI-sep. This is the single most important control in the problem, and it is the SAME trap the causal channel
  fell into (contiguity "beat" the connective signal on recall). Recall metrics reward flooding; type-precision does not.
- **MARKED vs UNMARKED is why spatial wins and causal does not.** Spatial RCC8 type is carried by the preposition +
  ground (Herskovits) -> a parse-bound typer recovers it precisely. Causal type is UNMARKED (65.6% of MAVEN edges) ->
  no parse-bound typer works; the brain infers it from world-knowledge + coherence (distinct organs). One sentence
  explains both channels' results and both prior SOLVEDs' walls.
- **The partitive is transparent and pervasive.** "in the heart/middle/part of Romania" -- a region-part is a distinct
  gold node; binding it lexically (not via fragile 'of'-attachment) recovered a large class of chain-critical edges.
- **The parent's reverted event-grounding bound the WRONG node.** Binding the located EVENT (not its subject) as the
  Figure is credited (Talmy) and lifts recall -- a genuine correction.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **FRONT-END (sec.1).** Refine "the front-end is the binding constraint" PER RELATION TYPE: the joint semantic typer
  WINS for MARKED relations (spatial RCC8 -- proven load-bearing on precision, +0.386 over a density prior) and is
  INSUFFICIENT for UNMARKED relations (causal -- needs the SDRT + simulator organs). Recall-survival is
  density-confounded; score marked-relation extraction on TYPE-PRECISION.
- **SPACE (sec.2b).** The extraction wall is NOT irreducible construction coverage: 96.9% of chain-critical misses are
  STATED via brain-foundational constructions (deixis/coordination/partitive/Herskovits preposition-semantics). Building
  them: containment survival 6/123 -> 16/123 CI-sep over the incumbent; balanced containment QA 0.518 -> 0.571; and the
  semantic typing beats a proximity density floor +0.386 CI-sep on hard negatives (the density floor collapses to
  0.185). The spatial Figure-Ground typer is brain-foundational and load-bearing.
- **CAUSE (sec.2b).** On the largest modern gold, connective extraction recovers 0.5% of edges (65.6% unmarked);
  contiguity recovers 15.2% but carries no causal signal (connective loses to it CI-sep on recall, beats it +0.33 on
  precision but is recall-blind). Multi-hop causal networks are SHALLOW (30 chains/710 docs). Residual = SDRT +
  generative simulator.
- **PARSER (sec.1).** exact-MAP (graded_parser) is the more-brain-foundational shared parse and should default for all
  joint-front-end channels; it is not yet incremental/predictive (filed).

## 8. ADJACENT COMPONENTS (seeds the next problems)
- **A LEARNED (usage-based) spatial construction inventory + a place-hierarchy world-knowledge gap-filler** -- the
  brain-foundational upgrade past hand-coded constructions; would close more of the ~55% residual and the unstated
  place-nesting. Brain-foundational (construction grammar; Barsalou simulation).
- **The SDRT discourse-coherence reader (FILED) + the causal generative simulator (U8, prototyped)** -- the named causal
  extraction levers (unmarked links + directed world-knowledge). This problem quantifies why they are needed.
- **The incremental/predictive parser (FILED)** -- the brain-foundational parse upstream (Friederici); exact-MAP is the
  interim. Its marginals are an unused per-arc reliability signal the typer could gate on.

## TLDR (plain English)
The reader has one "reading step" that pulls facts out of each sentence; it already works for TIME. I extended it to
SPACE and CAUSE. First I concluded both failed -- but you pushed me to check whether I had actually built the way the
BRAIN reads space and cause, and I had not. When I built the brain's real spatial mechanisms (treating "here/home" as
places, reading a place off an action, distributing "in the area" over a list, understanding "the heart of Romania"
means "in Romania", and knowing "at the bottom of X" means inside X), the reader went from recovering whole space-chains
1 time in 20 to about 1 in 8 -- beating the old reader. But I found a trap: just guessing that "nearby things are inside
each other" does almost as well on that score, because the score only rewards finding links, not getting them RIGHT. So
I ran the fair test -- can it tell "the statue IN the temple" from "the statue NEAR the plaza"? -- and there the
guess-by-nearness method collapses (18% right) while the real understanding scores 57% and clearly wins. That is the
brain-faithful result: understanding the MEANING of "in/on/at" is what matters, and we now do it. For CAUSE it genuinely
does not work by this reading step, and I can say exactly why: stories almost never SAY "X caused Y" (only ~1 in 3 even
hint it with a word like "because"), so the brain INFERS cause from world knowledge and how the story hangs together --
which needs two other pieces we have already identified and started (the "what-makes-sense" discourse reader and the
"imagine what would happen" simulator). Finally, the honest full-stack check you asked for: not everything upstream is
the brain's mechanism yet -- the grammar parser is a good approximation but not the brain's predictive one; our spatial
rules are hand-written where the brain LEARNS them; and the cause reader is not brain-faithful at all (the right organs
are the two named ones). The one place we are fully brain-faithful and winning is spatial meaning-typing.

## QUESTIONS
None blocking. One judgement call: I filed PARTIAL. SPATIAL passes the bar (whole-subgraph survival CI-sep over the
incumbent + twin collapses) AND is proven brain-foundational on the precision discriminator (beats a density prior
+0.386). CAUSAL is the bar's blessed located negative (unmarked-dominated -> SDRT + simulator, named with counts). A
SOLVED reading is defensible (one channel passes, one blessed negative -- the temporal-parent shape); I deflated to
PARTIAL because the survival HEADLINE is density-confounded for spatial (the win is real on precision, not on
recall-survival alone) and causal has no positive. Science identical either way.

## NEXT STEPS (priority-ordered)
- **P1 -- LAND (Q111) the spatial semantic-typing channels + exact-MAP shared parse** (Sec 7.1-7.2). A proven
  brain-foundational spatial extraction capability (precision +0.386 over density, +0.053 over incumbent; survival
  6->16/123 CI-sep). Score it on TYPE-PRECISION, not recall-survival (which is density-confounded).
- **P2 -- WIRE the SDRT coherence reader + the generative simulator as the CAUSAL extraction levers** (not a connective
  extractor). This problem quantifies the need (0.5% connective recall; 65.6% unmarked; loses to contiguity).
- **P3 -- a LEARNED spatial construction inventory + place-hierarchy world-knowledge gap-filler** -- the brain-
  foundational upgrade past hand-coded constructions (usage-based grammar + Barsalou simulation).
- **P4 -- the incremental/predictive parser (FILED)** -- the brain-foundational parse upstream; exact-MAP is interim.
- **DO NOT re-file:** a parse-bound connective causal extractor (0.5%, loses to contiguity); recall-SURVIVAL as the
  spatial capability metric (density-confounded -- use type-precision); whole-subgraph SURVIVAL as the causal metric
  (networks shallow, 30 chains/710 docs -- score at the EDGE level); a denser causal dataset (the sparsity is language);
  coref-driven spatial chain repair (0% of SpaceEval broken edges are pronoun/deictic).
