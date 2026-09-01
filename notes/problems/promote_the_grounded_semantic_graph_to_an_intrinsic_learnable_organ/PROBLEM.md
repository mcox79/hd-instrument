---
priority: 1
review:
review_text:
---

# PROBLEM: promote the GROUNDED RELATIONAL SEMANTIC GRAPH to an intrinsic, learnable substrate organ — read by SPREADING ACTIVATION, grown from reading. The reader owns WordNet (117,659 synsets) but uses it as a FLAT LOOKUP; and the grounding-accumulation ceiling is the SAME problem — meaning never accumulated because it was written to a FLAT ANCHOR STORE, not a structured GRAPH. Per-context sense selection is NOT a vector-cosine problem (8 feature-cosine prototypes — grounded re-rank, context-gating, gloss/usage embeddings, GloVe/MiniLM — all sit at the dominant-sense baseline on gold WSD): sense is TAXONOMIC/RELATIONAL (ATL hub; taxonomic-vs-thematic double dissociation, Mirman 2017). The brain selects sense by SPREADING ACTIVATION over a relational semantic network (Collins & Loftus 1975) that SETTLES into a sense attractor (Rodd 2004) — Personalized PageRank == random-walk-with-restart == the diffusion form of spreading activation (PINNED). Build a grounded, augmentable semantic-graph organ read by spreading activation, and reframe the reader's grounding write-path from a flat store to the graph — CI-separating above the MFS-agreement / context-shuffle-twin baseline (NOT just the naive floor) on gold WSD/WiC, or LOCATING the residual as the WordNet↔task granularity/coverage gap (foundation, not algorithm).

**slug:** `promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ` — **opened:** 2026-09-01
by the strategy session (PROMOTED from the solver-proposed `PROBLEM_CANDIDATE.md`, grounding_does_not_accumulate thread;
owner: idle solvers + these are high-value follow-ons). It is the NORTH STAR made concrete: LEARNER-ON via a CLEAN
FOUNDATION, where STRUCTURE (a relational graph) is the lever. **status:** OPEN — a BUILD problem (a grounded
semantic-graph organ read by spreading activation; static foundation first, then the learned growth). You build +
validate in `experiments/`; strategy lands any hdlab wire (Q111, default-off, witness required). Glass-box, NO external
LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; RE-RANK PER THE OWNER):** filed at `1` — HIGHEST. This is the
> project north star (LEARNER-ON via a CLEAN FOUNDATION; the flat-store→graph reframe UNIFIES the grounding-accumulation
> ceiling and the sense-selection wall into ONE structural fix). It SUBSUMES the narrower grounded-ATL-re-rank problem
> (`the_reader_selects_word_sense_by_distribution_needs_a_grounded_atl_re_rank`, now demoted) — the grounded features
> become NODES in this graph (approach step #1), because the same solver found feature-cosine re-rank sits at the
> dominant-sense baseline on gold WSD; the lever is the RELATIONAL structure, not the feature vector. ⚠️ HONEST: the PPR
> mechanism is BUILT and beats the naive floor CI-sep (WiC dev 0.618) but the context-shuffle twin (0.571) is close
> (per-context signal +0.05, not CI-sep) because it is a simplified UKB over a FROZEN hand-built inventory — the
> augmentation ladder (below) is the work. ⚠️ Compose with the reader's capable flags ON (`python tools/reader_capabilities.py`).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader owns a big dictionary-of-meanings (WordNet — 117,659 concepts, all linked) but treats it as a flat lookup
table, one word at a time. Two problems turn out to be the SAME problem: (a) it can't pick the right sense of a word
from context, and (b) meaning never "builds up" as it reads — because meaning was filed into a flat list of anchors,
not a linked NETWORK. Brains settle word meaning by letting activation SPREAD across a network of related concepts until
it lands in the right "sense" — and they GROW that network from experience. Build that: a grounded concept-graph the
reader reads by spreading activation, and grows as it reads. It reframes the whole meaning channel from "look up a
vector" to "diffuse over a structured graph."

## 2. WHY THIS ONE — WHY NOW (the evidence that forces this)
Drilling the `grounding_does_not_accumulate_over_repeated_exposures` ceiling to the bottom established, on gold labels:
1. **Per-context sense selection is NOT a vector-cosine problem** — 8 feature-cosine prototypes (grounded re-rank,
   context-gating, gloss-embedding, usage sense-embeddings, GloVe/MiniLM contextual) all sit at the dominant-sense
   baseline. Sense is TAXONOMIC/RELATIONAL (ATL hub; taxonomic-vs-thematic double dissociation, Mirman 2017).
2. **The brain does it by SPREADING ACTIVATION** over a relational semantic network (Collins & Loftus 1975) that
   SETTLES into a sense attractor (Rodd 2004). Personalized PageRank == random-walk-with-restart == the diffusion form
   of spreading activation (PINNED). Built glass-box/LM-free over WordNet (`exp_ppr_spreading_activation_wsd_wic_v1`):
   WiC dev 0.618 CI[0.580,0.657] — BEATS the naive floor CI-separated + gloss-edges load-bearing (the right mechanism,
   "LLM-gated" REFUTED) — but the context-shuffle twin (0.571) is close (per-context signal +0.05, not CI-separated),
   because it is a SIMPLIFIED UKB over a FROZEN, hand-built inventory.
3. **We OWN the graph** (WordNet, 117,659 synsets) but used it as a FLAT LOOKUP, never as a network to diffuse over.

CONVERGENCE: the original problem ("grounding does not accumulate over reading") is the SAME problem — meaning never
accumulated because it was written to a FLAT ANCHOR STORE, not a structured GRAPH. The fix and the north star are one:
a grounded relational semantic graph, READ by spreading activation, GROWN from reading.

## MEASURED vs INFERRED
- **MEASURED (inherit from the drill; do NOT re-derive):** per-context sense selection is NOT feature-cosine (8
  prototypes incl. grounded re-rank sit at the dominant-sense baseline on gold WSD); a glass-box/LM-free Personalized-
  PageRank spreading-activation walk over WordNet BEATS the naive floor CI-sep (WiC dev 0.618 [0.580,0.657]) with gloss
  edges load-bearing (NO_GLOSS ~ MFS), but the context-shuffle twin (0.571) is close (per-context +0.05, NOT CI-sep)
  because it is a simplified UKB over a FROZEN hand-built inventory. We own WordNet (117,659 synsets) but use it as a
  FLAT LOOKUP. The grounding-accumulation ceiling is the SAME wall (flat anchor store, not a graph).
- **INFERRED (you must measure):** whether the AUGMENTED grounded graph (disambiguated gloss edges + ConceptNet +
  grounded Binder-65 nodes + IC-weighting) read by spreading activation CI-separates above the MFS-agreement /
  context-shuffle twin on gold WSD/WiC — or whether the residual is the WordNet↔task GRANULARITY/COVERAGE gap
  (foundation, not algorithm), a full-PASS located negative that reframes the write-path to the graph regardless.

## 3. THE BAR (can-fail; a rigorous negative is a full PASS if located)
A grounded, augmentable semantic-graph organ, read by spreading activation, that (a) CI-SEPARATES above the
MFS-AGREEMENT / context-shuffle-twin baseline on gold WSD/WiC (NOT just the naive floor — the floor over-credits
dominant-sense), OR (b) if it cannot, LOCATES the residual as the WordNet↔task GRANULARITY/COVERAGE gap (foundation,
not algorithm) with the evidence — and in EITHER case reframes the reader's grounding write-path from a flat store to
the graph. Report CI half-width + null p95 beside every margin; the diffusion is inspectable (glass-box, no LLM).

## ALREADY TRIED / DO NOT RE-RUN — CHECK `experiment_index` FIRST (the p6 lesson: don't re-derive a known result)
> ⚠️ **RUN `python tools/experiment_index.py query "spreading activation"` / `"WSD"` / `"personalized pagerank"` /
> `"conceptnet"` BEFORE BUILDING.**
- ⛔ A FEATURE-COSINE selector (grounded re-rank / gloss-embedding / usage sense-embeddings / GloVe/MiniLM contextual) —
  ALL 8 prototypes sit at the dominant-sense baseline on gold WSD. Sense is RELATIONAL, not vector-cosine. Do not re-run.
- ⛔ Comparing only to the NAIVE floor (it over-credits dominant-sense) — use the MFS-agreement / context-shuffle twin.
- ⛔ "LLM-gated" spreading activation (REFUTED — the glass-box gloss-edge walk carries it). External LLM barred (invariant).
- ✅ BUILD ON `exp_ppr_spreading_activation_wsd_wic_v1` (WiC 0.618, the PPR baseline) — the augmentation ladder is the work.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the source `PROBLEM_CANDIDATE.md` in this folder + the `grounding_does_not_accumulate…` SOLVED.md (the drill that
  forced this) + `exp_ppr_spreading_activation_wsd_wic_v1` (the PPR baseline you build on) — inherit the numbers.
- Read the REUSE assets (below) — esp. `hdlab/wordnet_polarity_propagation.py` (the spreading-activation primitive), the
  ConceptNet KG organ, `wordnet_ic`, predicted-Binder-65, `tools.load_wsd_benchmarks` — do NOT rebuild them.
- Score on gold WSD/WiC vs the MFS-agreement / context-shuffle twin (NOT the naive floor); believe FULL over SMOKE
  (smoke 0.673 overstated the full 0.618); verify too-good numbers (the WiC-from-WordNet-examples leak: 0.83→0.52).

## 4. APPROACH (the augmentation ladder; each an ablation with the TWIN control)
STATIC (offline foundation, shelf-only, glass-box):
- [measuring] **#1 GROUNDED NODES**: attach predicted-Binder-65 to synsets (GROUNDED_PPR) — this SUBSUMES the demoted
  grounded-ATL-re-rank brief (the grounded features become node content the walk diffuses over, not a standalone cosine).
- **DISAMBIGUATED gloss edges** (proper WordNet++/UKB: MFS-disambiguate gloss words, or the Princeton Gloss Corpus if
  fetched) — the drill's #1 lever (UKB ~67 vs vanilla ~58-62). SyntagNet edges (SyntagRank ~72) = external fetch.
- **FOLD IN CONCEPTNET** (ALREADY INGESTED: `conceptnet_ingest_v1` / `conceptnet_kg` / multihop) — commonsense edges.
- Edge weighting by information content (`wordnet_ic` on disk); tune damping ~0.85 / iters / ppr_w2w joint.
LEARNED (the north star; LARGE):
- **GROW**: the reader adds nodes/senses/edges by structure-mapping to known concepts (grounding-by-relation; Tse 2007).
- **RETUNE**: usage sharpens edge weights (Rodd basin-deepening). **CONSOLIDATE**: prune/merge on the graph.
- **OWN GRANULARITY**: merge/split senses by usage (escape WordNet's fixed inventory; the ~0.75-0.80 WSD cap).

## 5. FILES AND ENTRY POINTS / ASSETS ON DISK (reuse; do NOT rebuild)
Build + validate in `experiments/` (compose the spreading-activation walk over the augmented graph; reuse the primitives
below); a scaffold-free witness recomputes the walk's gold WSD/WiC accuracy vs the MFS/context-shuffle twin + the gloss-
edge ablation FROM SOURCE. If it clears the bar, strategy lands the hdlab wire (Q111): the grounded semantic-graph organ
+ the reader's grounding read/write path routed through it, default-off, byte-identical when off, witnessed.
nltk WordNet (117,659 synsets + glosses) + `wordnet_ic`; scipy sparse (PageRank); spaCy; predicted-Binder-65;
`hdlab/wordnet_polarity_propagation.py` (spreading-activation primitive — REUSE); ConceptNet KG organ + multi-hop;
`ultrametric_clustering` (WIRED, for sense merge/split); gold WiC + `tools.load_wsd_benchmarks`. NO LLM at inference.
Check whether `exp_ppr_spreading_activation_wsd_wic_v1` ran and its result (the PPR baseline you build on).

## 6. SUBSTRATE IMPACT (evaluate each adjacent organ for fidelity+optimization BEFORE wiring — not map-only)
Read-out routes through the graph: `reading_grounding_loop.canonicalize`; `distributional_meaning_channel` (→ a node
spoke); `meaning_fusion` / `meaning_operation_router` / `conceptual_meaning` / `semantic` / `grounded_similarity` /
`lexical_similarity`; `situation_reader` + `situation_model_*` + `convergent_cue_reader` + `predictive_reader` (seed the
diffusion); `semantic_control` (the PFC/IFG reliability re-weighting of the walk). Write/grow: `grounding_acquisition_
loop`, `reading_grounding_loop`, `hdlab/learner/*`, the consolidation organ. Q111: strategy lands; substrate-central.

## 7. CONTROLS / TRAPS (banked this thread — inherit them)
- Compare to the MFS-AGREEMENT / context-shuffle TWIN, NOT the naive 0.50 floor (the floor over-credits dominant-sense).
- Gloss edges are load-bearing (NO_GLOSS ablation ~ MFS = the pinned trap).
- Believe FULL over SMOKE (smoke 0.673 overstated the full 0.618).
- Verify too-good numbers (the WiC-from-WordNet-examples leak: 0.83→0.52).
- Check `experiment_index` for prior WSD/WiC/spreading-activation work FIRST (the p6 lesson — do not re-derive).

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote the drill's numbers (WiC 0.618, UKB ~67) as YOUR result — MOTIVATION; re-measure on your own scorer.
- 🚫 Do NOT re-run a feature-COSINE selector as the fix (grounded re-rank / gloss-embedding / contextual all sit at
  baseline — the drill refuted the cosine framing). The lever is the RELATIONAL GRAPH + spreading activation.
- 🚫 Do NOT compare only to the naive floor (it over-credits dominant-sense — use the MFS/context-shuffle twin).
- 🚫 Do NOT use an external LLM as the graph, the edges, or the walk (the invariant). WordNet/ConceptNet + PPR are glass-box.
