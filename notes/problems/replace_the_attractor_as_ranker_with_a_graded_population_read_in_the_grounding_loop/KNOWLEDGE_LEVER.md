# KNOWLEDGE MOVES THE BAR -- which KINDS of knowledge are key for the grounding-loop sense-assignment

Owner (2026-09-10): "use existing tools to show that knowledge moves the bar, and record what kinds of knowledge
(or an idea database) are key."

**Context (why this is the frame).** The readout (cosine population read) and the fusion (equal-weight Bayes) are
now BF and VERIFIED (`BF_AUDIT.md`), and the BF-fidelity tweaks that do NOT touch knowledge did NOT move the bar
(`exp_bf_residuals_v1`: Euclidean-in-z vs cosine null -0.012 CI incl 0; labeled vs unlabeled deprels null/slightly
worse -0.013 -- labeling fragments sparse counts; the upgraded chain null -0.021). So the remaining signal loss is
KNOWLEDGE, and the lever is what knowledge the channels carry. Metric throughout: the loop's own held-out SimLex-999
sense-assignment ranking (rank the true synonym among ~4,400 read words), MRR / hit@10, info-free twin losing.

Each channel IS a KIND of knowledge, drawn from an existing tool:
| knowledge kind | what it knows | tool / "idea database" | brain analog |
|---|---|---|---|
| **relational / IS-A IDENTITY** | which concepts ARE the same / kind-of | conceptual_meaning over **WordNet** (a curated idea database) | ATL taxonomic organization + distinctive features |
| **substitutability (LEARNED)** | which words fill the same syntactic slot | dependency-context PPMI from **parsed reading** (no ontology) | lexical-class learning from syntactic frames |
| **perceptual / GROUNDED** | how a thing looks / feels / is acted on | **Lancaster+Brysbaert** sensorimotor+concreteness norms | ATL amodal hub over modality spokes |
| **raw co-occurrence** | what words appear together | ConceptSpace context **bag** from reading | temporal-cortex statistical learning |

## STUDY A -- which KIND of knowledge is key (`exp_knowledge_lever_v1`, n=4359 words, 169 test pairs, 3000-boot)
Full-knowledge fusion MRR **0.342** (hit@10 0.604) vs the info-free twin (knowledge<->word shuffled) **0.0016** --
a ~214x gap: KNOWLEDGE moves the bar, decisively. Which kind:

| knowledge kind | ALONE MRR | ALONE hit@10 | LEAVE-ONE-OUT marginal (remove it -> drop) |
|---|---|---|---|
| **relational / IS-A IDENTITY** (taxonomic) | **0.318** | 0.562 | **+0.227, CI [+0.178, +0.280]** -- removing it collapses the fusion 0.342 -> 0.115 (3x) |
| learned SUBSTITUTABILITY (DEP) | 0.096 | 0.189 | -0.001, CI incl 0 (NULL -- redundant *with* the taxonomy present; it is the LEARNED form of the same identity signal) |
| perceptual / GROUNDED | 0.075 | 0.178 | +0.013, CI [+0.00002, +0.025] (small but real) |
| raw CO-OCCURRENCE (bag) | 0.023 | 0.041 | -0.004, CI incl 0 (NULL -- retire) |

Ranking by contribution: **relational IDENTITY >> grounded > (learned substitutability, redundant-when-supplied) > bag**.
The one load-bearing kind is RELATIONAL / IS-A IDENTITY.

## STUDY B -- does MORE knowledge move the bar? YES (reading-volume exposure curve, learned channel)
DEP MRR vs corpus fraction: 0.031 (20%) -> 0.053 (40%) -> 0.059 (60%) -> 0.082 (80%) -> **0.096 (100%)** -- monotone
rising, steepest in the last quarter, NOT plateaued. More reading -> more learned identity knowledge -> higher bar.

## STUDY C -- knowledge DENSITY per word: the learned deficit is entirely low-knowledge words
DEP MRR by dependency-context count: 0.050 (0-20) -> 0.070 (20-60) -> 0.086 (60-200) -> **0.213 (200+)**; the
TAXONOMIC channel is flat ~0.30-0.35 across all bins (the ontology knows every word equally). So the learned
channel is exposure/density-limited per word: well-read words approach the taxonomy's ceiling with NO ontology.

## THE CATALOG -- what kinds of knowledge are key (quantified by STUDY A leave-one-out)

1. **RELATIONAL / IS-A IDENTITY knowledge is THE load-bearing kind.** Alone 0.318; removing it collapses the fusion
   3x (marginal +0.227 CI-sep). *The key "idea database" is a relational knowledge base of concept identity +
   hierarchy* (is-a, synonymy, kind-of, part-of). Everything else is a rounding error next to it. We SUPPLY it now from
   WordNet; the brain-foundational end-state LEARNS it (#2). **Priority 1: a clean relational IDENTITY idea-database.**
2. **SUBSTITUTABILITY knowledge, LEARNED from structured reading, is the ACQUIRABLE form of #1 -- redundant with the
   supplied taxonomy TODAY, but it is how the loop grows its own identity store.** Its leave-one-out marginal is ~0
   ONLY because the WordNet taxonomy already occupies that role in the fusion; ALONE it is the 2nd-strongest single
   kind (0.096) and it RISES with reading (Study B, still climbing) and per-word knowledge density (Study C: 0.05 ->
   0.21). *This is the idea database the loop can build itself* -- the grow-by-reading north-star; at volume it
   converges toward the taxonomy's ceiling and could REPLACE the supplied ontology. **Priority 2: read more, structured.**
3. **PERCEPTUAL / GROUNDED knowledge** is the only kind with a real ADDITIVE marginal on top of the taxonomy
   (+0.013 CI-sep) -- a complementary "how it looks/feels" axis -- but caps at the sibling/synonym confound alone.
   **Priority 3: keep as a fused channel; a richer/higher-dim grounded asset raises its ceiling.**
4. **RAW CO-OCCURRENCE (bag)** is the weakest for IDENTITY (0.023; relatedness not sameness) and NOT_BF (unordered);
   its marginal is null-negative. **Priority 4: retire in favor of #2.**

## THE IDEA-DATABASE SPEC (what to acquire/grow, in priority order)
- **A relational IDENTITY store** (concept is-a / synonymy / kind-of) -- the highest-value knowledge; supply from a
  curated ontology now, grow by reading later. This is the "idea database" that most moves the bar.
- **Structured (dependency-parsed) READING at volume** -- the mechanism that GROWS the identity store without an
  ontology; the bar rises monotonically with reading (Study B), and low-knowledge words carry the whole remaining gap.
- **Grounded sensorimotor norms** -- a complementary perceptual axis, fused not solo.
- (labeled syntactic structure and a magnitude-aware read do NOT help at current volume -- `exp_bf_residuals_v1`.)

## HONEST BOUNDS
- The taxonomic channel's strength partly reflects that WordNet was curated to encode the synonymy SimLex rates
  ("selection not meaning" caveat); the LEARNED channel (#2) is the un-caveated version and is exposure-limited.
- All numbers are on the SimLex SIMILARITY axis (the sense-assignment's real need); relatedness axes rank co-occurrence
  higher. Gold is human/WordNet-independent; the info-free twin losing controls for artifact.
