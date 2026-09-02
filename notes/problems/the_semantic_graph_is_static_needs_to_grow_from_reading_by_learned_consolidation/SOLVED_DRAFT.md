DRAFT — settled sections; RESULT/verdict/frontmatter-numbers filled when the powered subordinate run lands.
=====================================================================================================

---
problem: the_semantic_graph_is_static_needs_to_grow_from_reading_by_learned_consolidation
status: <SOLVED|PARTIAL — pending subordinate/BCM result>
bar: "PASS = a graph GROWN from reading (fast-map + cross-situational confirmation + schema-gated consolidation + BCM/XCAL tuning + usage-based split/merge, context-DISAMBIGUATED edges) improves SETTLING-WSD on HELD-OUT MODERN text CI-separated over the STATIC WordNet++ graph (gated on the static upper bound; recompute the floor on the held-out population), with an info-free twin (shuffled-context / naive-co-occurrence edges) LOSING CI-sep, AND an anti-interference control (the grown graph does NOT DEGRADE on already-known senses). Report CI half-width + null p95. A rigorous located NEGATIVE is a full PASS: if faithfully-built growth does not beat the static graph, name which mechanism fails and why."
result: <TBD — headline from run_subordinate: static-argmax -> +control -> +ppmi-growth -> +BCM-growth on the subordinate (MFS-wrong) population; + the argmax saturation number>
floor: <static graph, recomputed per population: argmax Raganato static 0.6692; subordinate MFS=0 by construction; static+control subordinate acc = TBD (the floor growth must beat)>
controls: "info-free SHUFFLED-CONTEXT twin (LOSES); DOMINANT see-saw cost reported (semantic_control trade-off); ppmi_mfs (topic-vs-sense control = MFS-disambiguated edges); shuffle-EDGE twin (naive random-rewire); schema/precision-gate on/off; emergent-signature controls (shuffled-frequency null for freq-dominance; random-pair baseline for semantic coherence). Grown graph VERIFIED != static (66,843 edges, sum|dT|=5398)."
files_changed: "experiments/exp_learned_graph_cls_grow_v1.py (new), verification/test_learned_graph_cls_grow.py (new witness), notes/problems/<slug>/{SOLVED.md, FIDELITY_AUDIT_AND_ADJACENT_MAP.md}. Reuses UNMODIFIED: experiments/exp_grounded_semantic_graph_ladder_wsd_v1.py (build_graph/_ppr/_settle/eval_wic/_sense_prior/_semcor_instances), hdlab/semantic_control.py (the validated LIFG organ), data/corpora/simplewiki, data/wsdeval (Raganato), data/syntagnet, data/datasets/conceptnet."
reverify: ".venv/Scripts/python.exe verification/test_learned_graph_cls_grow.py"
---

# <TITLE — e.g. "Growing the semantic graph from reading: the read organ saturates on argmax; the located brain-foundational lever is HOMEOSTATIC (BCM) growth + semantic-control on the subordinate population">

## What I built
An intrinsic LEARNED semantic-graph organ that grows the static WordNet++ graph from reading, and the
brain-foundational READ that consumes it. Every brain-foundational aspect, integrated (not in isolation):
- **WRITE:** local-collocation (windowed) + **syntactic dependency** edges grown from simplewiki, each token
  CONTEXT-DISAMBIGUATED by the current graph's spreading activation (reordered-access E-step, context-dominated),
  **PPMI surprise-weighted** (the proven does_learning lever), **cross-situational** gated (Yu & Smith),
  **precision/schema** gated (fast if schema-consistent, slow if novel), with **E-M REPLAY** rounds (CLS bootstrap)
  and a **BCM homeostatic** weighting variant (depress edges to high-activity/frequent synsets).
- **READ:** reordered-access (frequency prior + graph context coherence) -> **competitive attractor settling**
  (lateral inhibition) -> **`semantic_control`** conflict-gated suppression of the dominant sense (the LANDED,
  validated LIFG organ; trigger AUC 0.79). The grown graph's coherence is tested as `semantic_control`'s signal.
- Glass-box, LM-FREE at inference, deterministic, resumable/checkpointed. spaCy parse local-only (cached).

## What I measured
1. **ARGMAX WSD saturates: growth ≈ static on cn_syn.** 66,843 context-disambiguated PPMI edges grown from 40k
   sentences; the grown graph is VERIFIED different (T_grown nnz 1,797,370 vs static 1,681,492; sum|dT|=5,398;
   april.n.01 24->104 neighbours). Yet Raganato argmax grown 0.6692 vs static 0.6692 = **-0.0088** (touched subset
   -0.0109). Even large per-node structural change doesn't move argmax on the already-dense graph. WiC twin still
   cleared (dev r-t 0.086) -> growth does not BREAK the context signal. **This is the saturation wall, and its
   cause is located (below).**
2. **EMERGENT brain-faithfulness signatures (POSITIVE, both CI/threshold-separated).** Frequency-dominance:
   Spearman(log SemCor freq, learned-edge degree) = **0.360** (shuffled-frequency null -0.015) -- the Rodd
   "basin depth ~ frequency" geometry fell out UNBID. Semantic coherence: learned edges connect WordNet-related
   senses (path-sim 0.116) vs random pairs (0.095), CI-separated -- the growth learns STRUCTURE, not noise.
3. **Powered subordinate override (SemCor MFS=0 population, n=5,935 subordinate / 13,076 dominant) — the
   homeostatic hypothesis is CONFIRMED, and growth does NOT beat static (a located negative):**
   - static+argmax 0.1478 -> static+**semantic_control** 0.1535 (**control helps subordinate +0.0057 CI[0.0039,0.0078]**,
     reproduces context_override; dominant see-saw cost -0.0052).
   - **PPMI growth is RICH-GET-RICHER, verified:** grown+control HURTS subordinate (0.1387; growth-helps-control
     **-0.0148 CI[-0.0214,-0.0084]**) while HELPING dominant (**+0.0102 CI[0.0070,0.0133]**). Exactly the rho=0.36
     frequency-dominance signature.
   - **BCM homeostasis FIXES the edge-rule:** BCM-grown+control 0.1542 beats PPMI-grown by **+0.0155
     CI[0.0096,0.0217]** on subordinate (rescues the damage) and removes the dominant boost (bcm dominant -0.0004).
   - **But growth (even homeostatic) only reaches PARITY with static:** BCM+control vs static+control
     **+0.0007 CI[-0.0013,0.0027] (null)**. So the strong static cn_syn graph already saturates the discrete
     relational signal; even frequency-balanced reading-grown edges are REDUNDANT with it.
   - Info-free SHUFFLED-CONTEXT twin loses decisively: grown-coherence vs shuffled **+0.0603 CI[0.0505,0.0699]**.
   - [base-vs-cn_syn discriminator pending: does growth help the WEAK base graph (no SyntagNet) = the redundancy
     test + the real-world OOV/domain case.]

## The walls, drilled (each = a fidelity gap, per the discipline)
Every negative in context-conditioned sense selection unifies into ONE gap and one located missing organ:
- **prior_swamps [REFUTED] + context_conditioned [HARD_FAIL]:** on subordinate senses a monotone prior+context
  blend can't beat context alone; only SIGNED SUPPRESSION wins, gated by a detector we lacked because bag-of-words
  context is frequency-biased/topic-contaminated. FIX: syntactic/selectional (frequency-independent) context ->
  semantic_control inhibition. (Deep syntax as isolated FEATURES was a known +0.007 negative in context_override;
  the owner's synergy thesis says test it PAIRED, which this cell does -- as graph EDGES + settling + control.)
- **THE SATURATION WALL = a MISSING ORGAN (homeostatic plasticity).** The emergent frequency-dominance (rho=0.36)
  is ALSO the failure mechanism: naive Hebbian/PPMI growth is RICH-GET-RICHER, deepening frequent basins, unable
  to help subordinate senses. The brain requires a counter-force: **BCM sliding threshold** (high activity ->
  depression, low -> potentiation) + **synaptic scaling** (Turrigiano). The spec named BCM/XCAL; I had substituted
  PPMI -- a lesioned runaway-Hebbian learner. BUILT the fix (BCM homeostatic edge weighting), now under test.

## KEY REALIZATIONS (the enabling moves)
1. **Read prior work FIRST -> avoided a known dead-end.** `context_override` already showed deep dependency-syntax
   features add +0.007 (a clean negative); `semantic_control` is a LANDED validated organ. So "implement everything
   brain-foundational" meant REUSE the validated inhibition organ + feed it a better signal, not rebuild selection.
2. **The emergent signature I celebrated as faithfulness IS the failure.** Frequency-dominance = rich-get-richer;
   the missing homeostasis (BCM) is the located, buildable fix -- a wall turned into an organ to build.
3. **A structural change != a functional change on a saturated graph.** 66k edges, april 24->104, argmax -0.0088:
   discrete-edge PPR is insensitive to added mass when already dense -> evidence for the continuous-space substrate
   as the other fidelity fork.
4. **Eval was WordNet-lookup-bound; caching lookups (byte-identical) unlocked the powered population** -- the
   difference between an underpowered null and a real located result.

## Controls (code, not prose)
Shuffle-CONTEXT null (info-free twin, must lose); shuffle-EDGE twin (naive random-rewire); ppmi_mfs (topic-vs-sense);
schema/precision gate on/off; DOMINANT see-saw cost (the honest semantic_control trade-off); emergent-signature nulls
(shuffled-frequency, random-pair). Grown graph verified != static. Floors recomputed per population; CI half-width +
null reported beside margins.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
The LEARNED meaning-graph organ: grows from reading by context-disambiguated, surprise-weighted, cross-situational,
precision-gated consolidation; emergent frequency-dominance + semantic-coherence signatures confirm brain-faithful
basin geometry. NEW located deviation: naive Hebbian/PPMI growth is rich-get-richer and lacks HOMEOSTATIC plasticity
(BCM sliding threshold / synaptic scaling) -- built as the BCM variant. The read is reordered-access + competitive
settling + semantic_control (the validated LIFG organ), so the "meaning organs are islands" debt is addressed on the
read side. Deep dependency-syntax as isolated features remains a negative (context_override); tested here PAIRED.

## What I did NOT establish / would withdraw first
- <TBD after result> If BCM growth does not beat static+control on subordinate, the residual is the continuous-space
  representation (meaning_fusion node embeddings), the named next fork -- withdraw any "growth helps WSD" claim.
- The E-M replay / syntactic-edge synergy (fullstack) is a moderate-scale first pass, not exhaustive.
- Split/merge (usage-based sense induction via ultrametric_clustering) is NOT built here -- it cannot score against
  fixed WordNet gold; it is the novel-sense/OOV branch.

## Compute honesty (P7 — no silent caps)
Grew from 40k of simplewiki's ~38M sentences (checkpointed acc). Raganato argmax on a 2500 sample of 4478. Powered
subordinate on <N> SemCor files (<n> items, <nS> subordinate). spaCy parse 15k sentences (local). BCM/E-M/syntactic
are first-pass scales, flagged for scale-up.

## TLDR (plain English)
The reader has a fixed dictionary-graph it reads by letting meaning spread through it. I built the machinery to let
it GROW that graph from its own reading, the brain's way, and to read the result with the brain's meaning-selection
circuit. Growing it changed the graph a lot but did NOT improve the standard "pick the meaning" score -- because the
naive way of learning is rich-get-richer: it strengthens the meanings that were already common and starves the rare
ones, which are exactly the hard cases. That's not a dead end; it's a known missing brain part (a self-balancing rule
that holds back over-used connections), which I then built. The real test -- does the balanced version help on the
rare-meaning cases, read through the brain's suppression circuit -- is [running/landed]. Two brain-faithfulness
checks already pass: the learned links respect how common each meaning is, and they connect genuinely related
meanings, not random ones.

## QUESTIONS
None blocking.

## NEXT STEPS (ranked)
0. <finalize subordinate/BCM result + fill numbers>
1. If BCM helps subordinate: scale it (more reading, full SemCor) + wire the homeostatic coherence into
   `semantic_control` as the frequency-independent trigger (links the two organs).
2. If not: the continuous-space substrate (meaning_fusion node embeddings) is the located next fork.
3. Usage-based sense split/merge (ultrametric) on a novel-sense/OOV instrument (can't score on fixed WordNet).
4. [STRATEGY, Q111] the hdlab wire: the learned-graph organ + the homeostatic tuning + the semantic-control read
   path; default-off, witnessed.
