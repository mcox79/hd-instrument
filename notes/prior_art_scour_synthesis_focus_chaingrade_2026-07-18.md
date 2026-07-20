# Prior-art scour SYNTHESIS + updated focus + chain-grade map (4 scours, director fold)

**Filed:** Director, 2026-07-18 (overnight full-auto; USER authorized the BUILD). Governed by: brain-faithful + flexible/improving-not-static; learn-from/build-on/credit never steal; brain = existence proof. Scours: VSA-language (a5e5d50c -> research_vsa_learned_reader_prior_art_scour), semantic-parsing (a0cf63c2 -> research_prior_art_text_to_relational_meaning), neurosymbolic (a6a2dd9f -> research_neurosymbolic_glassbox_read_reason_prior_art), comprehension+grounded (af876943 -> research_prior_art_comprehension_loop_grounded_language). HYPOTHESIS-pending (per-scour P below).

## THE VERDICT (4 independent scours CONVERGE)
**ALREADY DONE -- ADOPT + CREDIT, do NOT reinvent:**
- Comprehension LOOP = Kintsch-van Dijk CONSTRUCTION-INTEGRATION (1978/88) + descendants (Landscape/LSA, Rabovsky Sentence-Gestalt 2018, Franklin/Gershman SEM 2020). Our compress-and-carry loop IS this. NOT novel (P_novelty 0.10). BUILD ON IT.
- Parse REPRESENTATION = AMR / PropBank-roles / DRS (box-nesting for cross-sentence coref). Solved + settled -> adopt wholesale.
- Neurosymbolic PATTERN = NVSA (IBM: fixed-VSA-algebra bind + LEARNED front-end + glass-box reasoning -- PROVEN, but VISION-only) + NS-CL 3-stage template (learned parse -> glass-box executor, vision-only). The single most direct "port this to TEXT" candidate.
- VSA-reasoning-over-triples = PSI (Cohen/Widdows -- proven multi-hop at scale, but hand-built extraction).
- Grounded relation-learning = Artzi & Zettlemoyer 2013 weak-supervised CCG (strongest precedent for learning RELATIONS from weak grounded supervision).

**GENUINELY UNBUILT / OUR EDGE (all 4 converge from different angles):**
- The COMBINATION (learned-read + fixed-VSA-bind + glass-box + grounded natural text + compositional reasoning) = UNBUILT (P_existence 0.72). Two lineages (learned-binding-on-synthetic; VSA-reasoning-over-hand-extracted) never cross-pollinated.
- The one OPEN mainstream problem + our plausible edge = COMPOSITIONAL / SYSTEMATIC GENERALIZATION via native binding at the text->role ENCODER (P<=0.50). Flat architectures FAIL (COGS 96-99% in-dist -> 16-35% held-out combinations); built-in compositionality fixes it (AM-parser ~98%); native VSA bind is a plausible-UNPROVEN fix, UNTESTED by anyone incl. us. Independently cross-validates the 07-18 thematic-roles drill (the encoder is the one real gap).

## UPDATED FOCUS / WHERE WE'RE GOING
BUILD the learned in-substrate reader = PORT the proven NVSA/NS-CL neurosymbolic pattern to TEXT:
- BACKBONE: Kintsch CI comprehension loop (brain-faithful, credited).
- REPRESENTATION: AMR/DRS role-graph = FHRR bindings (Stage-1-validated target).
- LEARNING SIGNAL: weak/grounded supervision (Artzi-Zettlemoyer) + coherence-gate + predict-error. NOT treebank, NOT next-token. FLEXIBLE/IMPROVING (scaffold/construction inventory grows with exposure).
- KEY DIFFERENTIATOR + CHAIN-GRADE TARGET: native VSA binding delivers COMPOSITIONAL GENERALIZATION (held-out role-combinations) where flat fails.
Build COMPONENT-BY-COMPONENT; brain-drill-first each (USER directive).

## CHAIN-GRADE MAP (recent wins -> CG)
- All recent wins (29326-31) = proven MECHANISMS in scope (MM). Reading/learning axis = ZERO CG (the session's CGs are all memory/capacity + SHRINK-prune + vision -- the substrate's strength zone).
- CG path (shared): assemble the mechanisms into the LEARNED real-text IMPROVING reader, evaluate CORPUS-WIDE vs INDEPENDENT gold, BEATS the hand-rule/frequency baseline + IMPROVES-as-it-reads (the learning curve = the flexible/improving evidence).
- SHARPEST CG target (scour-revealed): COMPOSITIONAL GENERALIZATION via native binding = the one place we produce a genuinely NEW best-in-class result (not just match prior art). CHEAP DECISIVE TEST (all scours + the design converge): COGS/SCAN-style held-out-combination split, native-bind vs flat baseline, relation-F1 + comprehension-Q + learning-curve. HARD-PASS = CG candidate (novel + brain-faithful + beats-baseline + flexible).

## BUILD SEQUENCE (component-by-component, brain-first; USER: "the brain clearly does this so it CAN be done")
1. [FIRED aca50f75] brain-drill: how the brain does COMPOSITIONAL GENERALIZATION + variable/role BINDING (binding problem, systematicity, structure-content factorization / cognitive-maps / TEM -- ties to our PRIMARY factorization focus).
2. Design the glass-box VSA compositional ENCODER around the brain mechanism.
3. Build the design-gated can-fail cell (held-out-combination generalization; native-bind vs flat; measure the LEARNING CURVE).
4. skunkworks-VET. Then next component (CI-loop integration, grounding, coref, ...), each brain-drill-first.

## CREDITS (learn-from + build-on, never steal)
Kintsch & van Dijk (Construction-Integration); Banarescu et al (AMR); Kamp / Bos + Parallel Meaning Bank (DRT/DRS); Kleyko et al (VSA surveys); Plate (HRR); Smolensky + Schlag/Palangi (TPR / TPR-nets); Eliasmith (Semantic Pointer Architecture / Spaun); IBM NVSA team (fixed-algebra neuro-vector-symbolic); Mao & Tenenbaum (NS-CL); Dhingra et al (DrKIT); Cohen & Widdows (PSI); Mitchell et al (NELL); Artzi & Zettlemoyer (grounded CCG); Whittington & Behrens (TEM / cognitive maps); Rabovsky (Sentence Gestalt); Franklin & Gershman (SEM).

## Caveats
Per-scour P_deflated 0.10-0.72; the novelty ("unbuilt combination") is strongest (0.72), the "our edge = compositional generalization" is capped <=0.50 UNPROVEN. Residual risk: a very-recent (2024-26) preprint doing exactly this (flagged 3-query re-search in the neurosymbolic scour). Load-bearing claims -> VET before treating as fact / before a build depends on them.
