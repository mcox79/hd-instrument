---
owner_verdict: DONE
---

SUBMISSION — build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift
STATUS: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO external LLM. Solver scope: experiments/,
verification/, data/frontend_assets/ + data/corpora/ (fetched corpora); strategy lands the hdlab wire (Q111).
Ledger clean. Reverify: .venv/Scripts/python.exe verification/test_knowledge_factory_meaning_store.py (6/6)
 (+ test_knowledge_factory_learner_ready.py 4/4, test_knowledge_factory_consumer_usage_tweak.py 3/3)

WHAT'S DELIVERED — the clean curated knowledge foundation, BUILT + FROZEN + VALIDATED, + the grow/prune/consult
machinery + measured consumer optimizations. Two frozen static assets + a growth engine:
- C1 MEANING  data/frontend_assets/meaning_sense_signatures_v1.npz — 117,614 WordNet synsets, per-sense signatures.
  Rare-sense WSD a_s 0.2512 -> 0.3267 (+0.0755 CI-sep [0.056,0.096]) through the live diagnostic_context_wsd
  readout; shuffled-knowledge twin loses; MFS no-regression; byte-deterministic. Witness 6/6.
- C1b ASSOCIATIVE  data/frontend_assets/associative_similarity_store_v1.npz — 80,002 words / 90 MB, reading-grown
  over 40M BROAD multi-domain tokens (encyclopedic, general/life science, chemistry, PHYSICS, MATH [calculus+
  algebra], astronomy, NEUROSCIENCE, psychology, PHILOSOPHY, fiction, drama, graded readers, news — 6 OpenStax
  textbooks fetched+cleaned this session). SimLex 0.166 (the live 15k hub) -> 0.264 (+0.098, +59%); WordSim 0.604.
  Prune is decisive (raw un-pruned 0.024). Witness 4/4. GAP: materials science (no OpenStax source).
- INGEST->PRUNE->LEARN machinery (consolidation_gate admit + cls_growth keep-both/rollback): ADMITS beneficial
  growth, REJECTS harmful growth (raw reading regresses meaning -> gate blocks), reversible, deterministic. 4/4.
- USAGE OPTIMIZATION: composed_hub_predictor scores selectional preference by AvgSim mean-centroid; swapping to
  MaxSim/top-k nearest-EXEMPLAR lifts which-argument +0.065 CI-sep (verb-shuffled twin loses), transfers to the
  distributional hub. Witness 3/3. Actionable hdlab diff in SOLVED.md.

IS IT READY TO BE THE LIVE PRIMARY KB? The KNOWLEDGE is READY and beats the current live hub on every axis. The
WIRING is the remaining step: the frozen stores have NO live read()-time consumers yet — C1 is blocked on the
reader_meaning_channel read()-stage; C1b's one consumer (composed_hub_predictor) is built but not called by the
reader. So the gains are proven-on-the-instrument but LATENT on read() until wired. Strategy owns the wire (Q111).

TO TURN IT ON (ranked, strategy lands):
1. Rebuild composed_hub_predictor's store on the NEW 80k C1b vectors + adopt the MaxSim usage tweak; measure
   which-argument vs the current (15k hub + AvgSim); wire into the live who-did-what path if net-positive. THE
   readiest live gain — and the one still-unmeasured step (store-growth +0.098 and usage +0.065 were measured
   separately; combine them on the live task).
2. Ship C1b as the reader's default distributional store (replace hub_ppmi_svd_200d: 15k -> 80k words).
3. Add a read()-time WSD stage consuming C1 (the reader_meaning_channel dependency) -> the +0.0755 goes live.

STEPS TO IMPROVE (ranked):
1. Meaning-KB resolution residual: the additive prior-override resolver (semantic_control.additive_reordered_read)
   closes HALF glass-box (acquisition resolution 0.33->0.60, regression -0.048->-0.012); the rest (0.60->1.0) needs
   a CONTEXTUAL reader = the invariant-boundary OWNER DECISION (no glass-box shortcut — proven, mechanism-complete).
2. Per-consumer prune PROJECTIONS: top-k for strict-similarity consumers, recurrence-floor for relatedness
   (measured: consumers disagree on the ideal prune; over-pruning hurts both) — one store, consumer-specific views.
3. Materials-science coverage (Wikipedia/other open text) + re-freeze — the one domain gap.
4. Step-2 ONLINE propose-and-verify learner (grow-experience on the frozen foundation, gated) — keep only if it
   beats the frozen store; raw reading-growth is a mechanism-complete located negative, so growth must be gated.

NEXT EXPERIMENTS: (a) [#1] composed_hub_predictor rebuild-on-80k + wire measurement; (b) contextual-reader owner
decision for the meaning residual; (c) step-2 online learner.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT §2b): the meaning channel is a hub-and-spoke store (one consolidated concept
graph, typed spokes, consumers read projections). Curated foundation frozen (+0.0755). Meaning-KB growth is
RESOLUTION-bound not representation-bound (oracle recovers +0.076; the static rep is adequate); the missing
mechanism is prior-override (additive resolver supplies half glass-box), residual = contextual token representation
(invariant boundary). The prune IS the growth (raw regresses, gated climbs). Ideal prune AND ideal usage are the
same "sharpen-for-discrimination" move on store vs query, and both are consumer-specific.

KEY REALIZATIONS: (1) Freezing forced a hidden bug — the parent's +0.0665 used hyponyms()[:8] over hash-randomised
order (non-reproducible); sort-then-cap fixed it (deterministic, +0.0755). (2) A raw cosine is meaningless without
its random-pair baseline (sibling-cos 0.93 but sibling-minus-random 0.027); and isotropising to "fix" it destroys
the classifier readout — so the ceiling is a DATA gap, not geometry. (3) The loss is acquisition-time RESOLUTION,
not representation (oracle recovers it). (4) A consumer that regresses on CORRECT knowledge is a consumer bug, not a
reason to withhold — fix the consumer (precision-weighting / MaxSim), don't blunt the knowledge. (5) Breadth is the
bridge to the live consumers: narrative/STEM text feeds the selectional-preference/affect/goal knowledge the reader
uses, which encyclopedias lack.

TLDR (plain English): I built the reader's clean dictionary-of-meanings (every WordNet sense) and froze it — it
lifts rare-word meaning accuracy from ~25 to ~33 out of 100, proven and repeatable. Separately I grew a big
word-association store by reading ~40 million words across every subject — encyclopedias, all the sciences
(including chemistry, physics, math, astronomy, neuroscience), psychology, philosophy, plus stories, plays,
children's readers and news — and pruned it (throwing out the noisy 65%); it's now ~80,000 words, five times bigger
than what the reader uses today, and clearly better at judging how similar two words are (up ~60%). I also found
that the one tool that reads this store was using it in a blurry way (comparing to an average) and showed a small
change (compare to the best single example) makes it ~6 points more accurate at who-did-what. The knowledge is
ready and better than what's live; the remaining work is plugging it in — the reader doesn't consult these stores
yet, and that wiring is the strategy session's job. The only subject still missing is materials science (no open
textbook available). Everything is glass-box, no outside AI.

QUESTIONS: one owner decision gates the meaning ceiling — the contextual-reader / invariant boundary (relax the
no-transformer rule for one offline contextual-sense asset, or hold and pursue the online reader). Recommend HOLD;
wire what's ready first.
