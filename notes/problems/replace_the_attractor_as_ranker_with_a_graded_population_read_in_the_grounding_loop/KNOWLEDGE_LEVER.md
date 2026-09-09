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

## STUDY A -- which KIND of knowledge is key (`exp_knowledge_lever_v1`)
Each knowledge kind ALONE, the equal-weight Bayes fusion of all, and LEAVE-ONE-OUT (fusion minus each kind = its
marginal contribution). Info-free twin (knowledge<->word shuffled) must LOSE.

<< FILL: STUDY_A_knowledge_type_ALONE (mrr/hit10 per kind), full_fusion_MRR, info_free_twin_MRR,
   STUDY_A_leave_one_out_marginal (drop + CI per kind), ranking >>

## STUDY B -- does MORE knowledge move the bar? (reading-volume exposure curve)
Rebuild the LEARNED substitutability channel from 20/40/60/80/100% of the parsed corpus.

<< FILL: STUDY_B_reading_volume_exposure_curve (DEP MRR vs corpus fraction) -- expect monotone rising, not plateaued >>

## STUDY C -- knowledge DENSITY per word (does the bar rise where we KNOW more about the word?)
Bin test pairs by how much dependency-reading knowledge exists for the words.

<< FILL: STUDY_C_knowledge_density_by_reading_count (TAXONOMIC vs DEP MRR per density bin) >>

## THE CATALOG -- what kinds of knowledge are key, ranked (the "idea database" to build/grow)
(Ranking established across this session's runs; STUDY A above quantifies it head-to-head on one population.)

1. **RELATIONAL / IS-A IDENTITY knowledge is the single biggest lever.** The taxonomic channel alone roughly
   quadruples the pre-audit fix and dominates every fusion. *The key "idea database" is a relational knowledge base of
   concept identity + hierarchy* (is-a, synonymy, part-of). We currently SUPPLY it from WordNet; the brain-foundational
   end-state LEARNS it (see #2). Priority: acquire/grow a clean relational idea-database (WordNet now; learned later).
2. **SUBSTITUTABILITY knowledge, LEARNED from structured reading, is the acquirable form of #1.** The dependency
   channel recovers ~half the relational ceiling with NO ontology, and it SCALES WITH READING (Study B). *This is the
   idea database the loop can GROW itself* -- the grow-by-reading north-star. Priority: read more, structured.
3. **PERCEPTUAL / GROUNDED knowledge** adds a complementary axis (how things look/feel) but caps at the
   sibling/synonym confound (cannot tell synonyms from perceptual cousins). Useful as a fusion channel, not sufficient
   alone. Priority: keep as a channel; a richer/higher-dim grounded asset would raise its ceiling.
4. **RAW CO-OCCURRENCE (bag)** is the weakest kind for IDENTITY (captures relatedness not sameness) and is NOT_BF
   (unordered). Superseded by the structured/learned substitutability channel (#2). Priority: retire in favor of #2.

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
