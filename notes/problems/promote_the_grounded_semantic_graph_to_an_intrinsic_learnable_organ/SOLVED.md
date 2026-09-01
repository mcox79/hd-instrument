---
problem: promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ
status: SOLVED
bar: "A grounded, augmentable semantic-graph organ, read by spreading activation, that (a) CI-SEPARATES above the MFS-AGREEMENT / context-shuffle-twin baseline on gold WSD/WiC (NOT just the naive floor -- the floor over-credits dominant-sense), OR (b) if it cannot, LOCATES the residual as the WordNet<->task GRANULARITY/COVERAGE gap (foundation, not algorithm) with the evidence -- and in EITHER case reframes the reader's grounding write-path from a flat store to the graph."
result: "cn arm (WordNet relations + MFS-disambiguated gloss edges + ConceptNet MFS-disambiguated thematic edges), personalized-PageRank spreading activation, gold WiC HELD-OUT TEST (n=1400, human-judged same/different-sense): acc 0.6164 CI[0.5907,0.6414]; real-minus-context-shuffle-twin +0.0521, paired margin CI [0.0229,0.0807] (excludes 0 -> CI-SEPARATED above the twin). Dev (n=638): 0.6661, +0.1066 [0.0642,0.1505]. base arm (no ConceptNet) also clears held-out: +0.0464 [0.0171,0.0764]."
floor: "context-shuffle twin (dominant-sense null; side-2 disambiguated from a RANDOM other sentence) = 0.5643 (WiC test) / 0.5596-0.5737 (dev) -- the strongest floor for bar (a), gated on the paired-margin lower CI. Also: naive floor 0.50; MFS 0.50 on balanced WiC; NO_GLOSS (relations-only) ~MFS (0.569 dev, baseline cell). CROSS-TASK BOUNDARY: on SemCor all-words WSD the frequency prior MFS=0.7292 (n=2500 polysemous n/v) BEATS the walk (pure 0.39; +prior 0.58) -- reported as the honest scope limit."
controls: "context-shuffle twin (winner CI-separates above it on HELD-OUT test, paired margin CI excludes 0); NO_GLOSS ablation ~MFS (gloss edges load-bearing); disambiguated(g1) vs undisambiguated(g3) glosses -- g3 does NOT clear the twin (+0.047 beats=False), g1 does; IC-weighting ablation NEUTRAL-TO-NEGATIVE (cn_ic +0.078 < cn +0.107 -- excludes IC as the lever); grounded-node ablation SHRINKS the margin (context-free lift -- excludes feature-vectors as the per-context lever); prior-combination (Rodd resting-level) on WiC dilutes but preserves the twin win (+0.044 [0.006,0.083]) and on SemCor lifts 0.39->0.58 but stays < MFS (locates the missing reliability-weighted-control component); damping sweep d0.6-0.95 all clear (robust); SemCor cross-task (MFS floor)."
files_changed: "experiments/exp_grounded_semantic_graph_ladder_wsd_v1.py (new); verification/test_grounded_semantic_graph_ladder.py (new witness, 5/5); notes/problems/promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ/SOLVED.md. Reuses UNMODIFIED: experiments/exp_ppr_spreading_activation_wsd_wic_v1.py (baseline PPR operator), experiments/exp_sense_wall_breakthrough_wic_v1.py, tools/load_wsd_benchmarks.py, data/datasets/conceptnet5_en_100k.jsonl, nltk wordnet_ic + semcor."
reverify: ".venv/Scripts/python.exe verification/test_grounded_semantic_graph_ladder.py"
---

# SOLVED: a grounded relational semantic-graph organ, read by spreading activation, clears the context-shuffle twin on held-out WiC -- and the residual is located to two named components, not to WordNet granularity

## Verdict
**SOLVED via bar (a): CI-SEPARATED above the context-shuffle twin on HELD-OUT gold WiC.** The mechanism is a
personalized-PageRank spreading-activation walk over a GROUNDED, AUGMENTABLE WordNet++ graph. Glass-box,
LM-FREE at inference, deterministic. This confirms AND strengthens the drill's finding (WiC dev 0.618,
twin-marginal): climbing the augmentation ladder (DISAMBIGUATED gloss edges + ConceptNet THEMATIC edges)
takes the HELD-OUT test margin from twin-marginal to CI-separated. Bar (b) is ALSO delivered -- but it
REFUTES the brief's guess: the residual is NOT the WordNet<->task granularity/coverage gap (that is ~3% of
WiC errors); it is located to two named components (per-context signal strength; the missing
reliability-weighted frequency prior = `semantic_control`).

## What I built
`experiments/exp_grounded_semantic_graph_ladder_wsd_v1.py` -- the augmentation ladder on the baseline's
EXACT PPR operator (`exp_ppr_spreading_activation_wsd_wic_v1._ppr` + disambiguation logic, reused; only the
GRAPH changes, so every rung is a clean ablation and the base rung cross-validates against the baseline's
WiC-dev 0.652). Brain-foundational framing -- each rung a distinct EVIDENCED component, not "more edges":
- **base** = WordNet relations (ATL taxonomic hub) + MFS-DISAMBIGUATED gloss edges (definitional).
- **+cn** = + ConceptNet commonsense edges, MFS-disambiguated = the THEMATIC pole (Mirman 2017's TPJ/pMTG
  system, the OTHER half of the taxonomic-vs-thematic double dissociation).
- **+ic** = edges weighted by information content (`wordnet_ic`; the reliability-reweighting analog).
- **grounded** (mode) = fuse the walk with predicted-Binder-65 node coherence (sensorimotor spoke).
- **prior** (mode) = a resting-activation / frequency term (WordNet sense order; Rodd 2004 resting levels).

## What I measured -- 1) gold WiC (human-judged; context-shuffle twin = dominant-sense null)
DEV (n=638) / TEST (n=1400, HELD-OUT). margin = real-minus-twin, [paired 95% CI]; CI half-width ~0.038 (dev):
| arm | dev acc | dev margin | test acc | test margin | clears twin |
|---|---|---|---|---|---|
| base (disambig glosses) | 0.652 | +0.078 [0.035,0.125] | 0.611 | +0.046 [0.017,0.076] | YES (dev+test) |
| **cn (base+ConceptNet)** | **0.666** | **+0.107 [0.064,0.151]** | **0.616** | **+0.052 [0.023,0.081]** | **YES (dev+test)** |
| ic | 0.647 | +0.082 [0.033,0.127] | -- | -- | yes (dev) |
| cn_ic | 0.644 | +0.078 [0.031,0.124] | -- | -- | yes (dev) |
| base+grounded | 0.644 | +0.030 [-0.014,0.074] | -- | -- | NO |
| cn+grounded | 0.652 | +0.046 [0.002,0.089] | -- | -- | weak |
| cn+prior | 0.632 | +0.044 [0.006,0.083] | -- | -- | yes (diluted) |

**ConceptNet thematic edges are the real lever**: they grow the held-out test margin (+0.046 -> +0.052) AND
raise accuracy, and grow the dev margin most (+0.078 -> +0.107). Adding the brain's THEMATIC pole to the
taxonomic graph improves per-context selection -- a brain-foundationally predicted, MEASURED gain.
**Damping sweep** (base, dev): d0.6 +0.074 / d0.75 +0.066 / d0.85 +0.078 / d0.9 +0.080 / d0.95 +0.082 --
ALL clear the twin; d=0.85 (the literature value) is near-optimal. The result is robust to the one swept param.

## What I measured -- 2) SemCor all-words WSD (second gold, field-standard, per-token) -- THE HONEST BOUNDARY
Per-token WSD accuracy on polysemous n/v tokens (n=2500), MFS = the frequency floor (WordNet sense-1 order is
SemCor-derived, so MFS is near-oracle here -- reported with that caveat):
| arm | acc | vs MFS 0.7292 | beats MFS |
|---|---|---|---|
| pure spreading activation (base) | 0.388 | -0.342 | NO |
| pure spreading activation (cn) | 0.393 | -0.336 | NO |
| **+ resting-level prior (base)** | **0.579** | -0.150 | NO |
| + resting-level prior (cn) | 0.577 | -0.152 | NO |

**The pure walk LOSES to the frequency prior on all-words WSD** -- decisively. Adding the resting-level prior
lifts it 0.39 -> 0.58 (+0.19) but, at equal z-weight, context still DRAGS the pick off MFS (0.73). This does
NOT contradict the WiC win: WiC's context-shuffle twin controls for frequency, so WiC measures PURE
per-context signal (which is real, +0.05 held-out); SemCor's MFS floor is the frequency prior itself. The two
golds together locate the gap precisely (below).

## Locating the residual (bar (b)) -- the brief's guess is REFUTED; two better-located components
WiC-dev error decomposition (base, 222/638 errors): monosemous/no-context = 3; WordNet OVER-SPLIT
near-synonyms (gold=same, we said different, wup>=0.8) = 3; **everything else = 216 (97%)**. So the
WordNet<->task GRANULARITY/COVERAGE gap the brief guessed is only ~2.7% of the residual -- **REFUTED as the
dominant residual**. The residual is instead:
1. **Per-context SIGNAL STRENGTH (WiC):** 97% of errors are the walk picking a wrong (not near-synonymous)
   sense -- the diffusion is real but not sharp enough. Levers: stronger edges (SyntagNet, ConceptNet already
   helped), the LEARNED graph.
2. **The missing RELIABILITY-WEIGHTED PRIOR (SemCor):** the walk needs the frequency/resting-level prior AND
   a control layer that weights context-vs-prior by reliability. The optimal weight is task-dependent
   (context-heavy on frequency-balanced WiC; prior-heavy on frequency-skewed SemCor) -- a FIXED z+z cannot be
   optimal for both. This is exactly the job of **`semantic_control` (PFC/IFG; Controlled Semantic
   Cognition)** -- a distinct, already-named organ. THE located next component.

## The honest negatives (what did NOT work, and why it teaches)
1. **IC-weighting (my OUR-INVENTION heuristic) does not help** -- cn_ic (+0.078 dev) < cn (+0.107 dev); IC
   erodes the ConceptNet gain. A reliability reweighting is brain-plausible, but this STATIC IC edge-weight is
   not its right form. Withdraw first.
2. **Grounded features as NODE CONTENT give only a CONTEXT-FREE lift** -- GROUNDED_PPR raises raw accuracy but
   SHRINKS the real-minus-twin margin at every rung (base+grounded +0.030, does NOT clear). Binder
   node-coherence helps the shuffled twin too. Same signature the audit reports for `conceptual_meaning` (the
   ATL identity hub is context-free). It sharpens the thesis: per-context discrimination is a property of the
   RELATIONAL DIFFUSION, not the node vectors -- exactly why the 8 feature-cosine prototypes plateaued.

## KEY REALIZATIONS (the enabling moves)
1. **The ladder is the SAME operator; only the GRAPH changes** -- every rung is a clean ablation and the base
   rung cross-validates against the baseline (fidelity, not re-derivation).
2. **wordnet_ic stores FREQUENCY, not information content** -- using it raw INVERTS the weighting (generic
   hubs look informative). IC = -log(freq/root); a self-test (`poodle >= entity`) caught the inversion before
   it built the +IC rung backwards.
3. **Two golds disambiguate the claim.** WiC (frequency-balanced) isolates per-context signal; SemCor
   (frequency-skewed) exposes the missing prior. Reporting ONLY WiC would have hidden that the mechanism is
   not yet task-general-WSD-competitive; reporting ONLY SemCor would have hidden that the per-context signal
   is real. The pair locates the gap to `semantic_control`.
4. **Grounded-as-node-content is a context-free lift** -- the per-context lever is the diffusion over
   relational structure; grounding belongs in the graph for meaning-IDENTITY, not as the selection signal.
5. **Disambiguating the ADDED edges is load-bearing at every rung** -- g1 glosses clear the twin where g3 did
   not; ConceptNet edges are MFS-mapped for the same reason (a lemma-level edge wires ALL senses = the g3
   failure in a new place).

## The hdlab wire (Q111 -- STRATEGY LANDS; a proposed diff, default-off, witness required)
The mechanism proven here is a NEW intrinsic organ + a reframe of one existing read-out.

**NEW ORGAN `hdlab/grounded_semantic_graph.py` (the ATL relational hub, read by spreading activation).**
- STATE: a WordNet++ graph (relations + MFS-disambiguated gloss edges + ConceptNet MFS-disambiguated thematic
  edges), synset nodes optionally carrying a grounded Binder-65 vector. Built offline (admissible static
  foundation), cached as a row-stochastic sparse transition matrix.
- READ: `select_sense(lemma, pos, context_words) -> synset` = personalized PageRank seeded on the context
  synsets (excluding the target's own senses; ppr_w2w), read out the target synset with max settled
  activation. Combine with a resting-level frequency prior under a reliability gate (the `semantic_control`
  hook -- see below). Glass-box, LM-free, deterministic. REUSE `hdlab/wordnet_polarity_propagation.py` (its
  `_signed_reach` is a bounded-hop spreading activation over WordNet neighbours -- generalize to unsigned
  personalized-PageRank readout).
- CONTROL HOOK: `semantic_control` supplies the context-vs-prior weight (the located residual #2). Default =
  the WiC-tuned context-heavy weight; a reliability gate (top-2 activation separation) is the brain-faithful
  form and the first follow-on.

**REFRAME (write-path) `hdlab/reading_grounding_loop.py::canonicalize`.** Today it assigns a newly-read word's
sense by COSINE nearest-anchor over a FLAT ConceptSpace (above threshold -> near-sense of an anchor; below ->
new standalone concept). This is the flat store the grounding-accumulation ceiling blamed. Reframe: seed the
diffusion with the word's context; the settled activation over its candidate synsets picks the sense (a
genuinely new concept = no strong attractor => a new node). Meaning then ACCUMULATES as graph structure
(nodes/edges), not as appended flat anchors. Default-off, byte-identical when off, witnessed.

**READ-OUTS to route through the organ (evaluate fidelity before wiring, not map-only):** `meaning_fusion`
(add a per-context sense-selection spoke alongside the context-free relatedness/similarity routes),
`conceptual_meaning` (its taxonomic bag becomes node content the walk diffuses over),
`distributional_meaning_channel` (idle -> a node feature), `situation_reader`/`convergent_cue_reader`/
`predictive_reader` (seed the diffusion with the situation). `semantic_control` = the PFC/IFG reliability
reweighting (the located residual #2 -- the context-vs-prior gate).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
The substrate has WordNet-based meaning organs -- `conceptual_meaning` (ATL identity hub, PINNED, demand-routed
into `meaning_fusion` 2026-08-30) and the relatedness pool -- but ALL operate at the WORD level (context-free):
a per-word feature bag / similarity, never a per-CONTEXT sense. NONE reads WordNet as a relational GRAPH via
spreading activation to SELECT a sense from context. This cell establishes per-context sense selection as a
DISTINCT capability (a personalized-PageRank diffusion clearing the context-shuffle twin CI-sep on held-out
WiC), shows grounded features as NODE CONTENT give only a context-FREE lift (corroborating conceptual_meaning's
context-free signature), and NEWLY LOCATES that converting per-context signal into task-general WSD accuracy is
gated by `semantic_control` (the context-vs-prior reliability weighting) -- the pure walk LOSES to the MFS
frequency prior on all-words SemCor (0.39/0.58 vs 0.73). NEW deviation to record: `reading_grounding_loop.
canonicalize` is a FLAT cosine read-out where the brain-faithful operation is graph diffusion (spreading
activation settling into a sense attractor; Collins & Loftus 1975 / Rodd 2004). PINNED bridge confirmed:
personalized PageRank == random-walk-with-restart == the diffusion form of spreading activation.

## What I did NOT establish / would withdraw first
- **Task-general WSD accuracy above MFS is NOT established** -- on SemCor the walk (even +prior at equal weight)
  loses to the frequency prior. The claim is bounded to: the walk carries real per-context signal (clears the
  frequency-controlled twin on human-gold held-out WiC). The prominent boundary, not buried.
- **IC-weighting is withdrawn first** (an OUR-INVENTION that did not help).
- **The reliability-weighted control** (the fix for the SemCor loss) is DESCRIBED and LOCATED, not built --
  deliberately not fitting a global prior-weight to beat MFS on the same SemCor I evaluate on (that would be
  soft overfitting). The brain-faithful form is the `semantic_control` gate.
- **SyntagNet edges** (the literature's biggest all-words lever, ~72) NOT tested -- an external fetch
  (owner-auth foundation build), flagged as the next static rung.
- **The LEARNED growth** (grow/retune/own-granularity) is NOT built here -- the large follow-on program; this
  cell delivers the STATIC foundation + the proof the diffusion-over-relational-graph is the right per-context
  mechanism, plus the two located next components.

## TLDR (plain English)
The reader owns a big dictionary whose word-meanings are all linked to each other, but it was using it like a
flat list -- looking words up one at a time. I made it work the way a brain does: let the meaning of the
surrounding words SPREAD through the network of links until it settles on the right sense. On a standard
human-labelled "same meaning or not?" test this beats the honest "just guess the common meaning" baseline by a
margin that HOLDS UP on held-out data -- with NO large language model, every step inspectable. Adding a second
set of links (everyday "related-to" facts) helped most. Two things I tried did NOT help, and I report them as
such. On a harder, frequency-heavy word-sense test the method LOSES to simply "always pick the commonest sense"
-- because it is missing the brain's habit of weighting how much to trust the context versus the default
meaning. That is a specific, named next piece to build, and the remaining gap is that piece plus letting the
network grow its own senses -- NOT a flaw in the spreading-activation idea itself.

## QUESTIONS
None blocking. One decision for the owner when convenient: whether to authorize an external download of
SyntagNet (the one static ingredient not already on disk, and the literature's largest remaining lever).

## NEXT STEPS
1. Strategy: land the wire (grounded-semantic-graph organ + reframe `canonicalize` flat->graph), default-off, witnessed.
2. The `semantic_control` reliability gate (context-vs-prior weighting) -- the located fix for the SemCor/MFS gap.
3. SyntagNet edges (owner-auth external fetch) = the next static rung toward ~0.72.
4. The #2/#3 LEARNED graph (grow/retune/own-granularity) = the north-star follow-on program.
