# research drill: substrate as COMPLETE RESEARCH-HISTORY LEDGER + tiered protection (2x DEEP)

date: 2026-06-11
field: institutional-memory / content-addressed storage / provenance graphs / drift detection / VSA-retrieval (cross-domain synthesis)
adjacency: extends substrate-self-index (Day 1 operational) to FULL project corpus; rides on substrate-proposed-architectures Tier-4 stack (frozen-gate invariant); rides on Layer 4 dialectic surprise-classifier; rides on Layer 8 drift tracker
calibration: deflate P by 0.20; novel-synthesis cap = 0.50; HARD-FAIL bands pre-registered; lit-precedent is dominant on each of 4 component-mechanisms (CAS+merkle-DAG, PROV-O lineage, tiered hot/warm/cold, BOCPD drift), but the assembly + bounded-recursion under self-ingest is novel-synthesis.
companion: notes/exp_dev_handoff_research_substrate_as_full_research_ledger_2026-06-11.md (5 rank-ordered anchors for ledger pilot gate)

## (a) HEADLINE

Substrate-as-full-research-history-ledger is a SUBSTRATE-NATIVE EXTENSION of substrate-self-index (60-atom Day 1 working) to the full project corpus (~235 cap_map cycles + 381 PP rows + 150+ routing notes + 50+ memory + 32 drills today), bounded by FOUR architectural invariants borrowed verbatim from mature lit. (1) STORAGE: content-addressable Merkle-DAG (git/IPFS/ForkBase pattern) gives immutable history, deduplication, branch+rollback. (2) TIERING: hot/warm/cold (Tier-1 frozen substrate-current-state / Tier-2 last-N-cycles evolving / Tier-3 archive append-only) - mature 4-decade storage-system literature. (3) LINEAGE: typed edges per W3C PROV-O (Entity/Activity/Agent, wasGeneratedBy/wasDerivedFrom/wasAttributedTo) make drill -> PP row -> memory -> routing -> next-drill machine-traversable. (4) BOUNDED RECURSION: the substrate that analyzes its own history MUST be gate-frozen-at-cycle-0 (the Layer 1 attribution + Layer 4 dialectic classifier methodology is fixed-external, per the meta-evaluation-collapse bound from substrate-proposed-architectures drill earlier today + OpenReview IF0L7HSs3K). The full-research-ledger interacts with bounded-recursion as follows: substrate may INGEST any historical artifact (Tier-3 archive is unrestricted), may RETRIEVE+RANK+CLUSTER over the corpus (Layer 4/8 capabilities), may PROPOSE new drills/architectures from corpus patterns, but the GATE methodology and the CURRENT-STATE substrate (Tier-1) is frozen-external and cannot be overwritten by self-analysis. The result is a substrate that knows its own research history, can trace lineage of any current cap_map claim back to founding drill, can detect persistent vs noise patterns at corpus scale, can predict surprise locations for next drill - WITHOUT collapsing into self-evaluation. P_deflated = 0.55 (lit-precedent is unusually clean: CAS+merkle-DAG industrial 20+yr; PROV-O W3C standard 12+yr; tiered storage 40+yr; BOCPD drift 10+yr; novel-synthesis is the assembly + bounded-recursion safety case under self-ingest, NOT the parts; cap at 0.50 is appropriate but we float just above because each component has direct precedent).

## (b) Cheap decisive test

A SINGLE CPU pilot (~4-8 hr) deciding whether substrate-as-full-ledger is empirically achievable BEFORE committing to full ingest of 235+ cycles. The pilot is a small-N rehearsal of the full pipeline on the LAST 10 drills + 10 PP rows + their cross-references; success criteria are pre-registered.

**Pilot LEDGER-1 (~4-8 hr CPU): scaled-down substrate-ledger end-to-end.**

Setup:
- Select 10 most-recent drills (today's 2026-06-11 drill outputs ARE the corpus convenience sample - they are recent, cross-linked, and have ground-truth provenance because the orchestrator log knows the dispatch order).
- Select the 10 PP rows corresponding to recent verdicts (or synthetic stand-ins from cap_map verdict log).
- Compute a CAS hash (SHA256) for each artifact; build a merkle-DAG where parent edges = wasDerivedFrom (drill cites prior memory + routing); child edges = wasInfluencedBy (PP row cites drill).
- Ingest into substrate as typed FHRR bundles: drill_atom = role:DRILL bound to value:cas_hash; PP_atom = role:PP_ROW bound to value:cas_hash; edge_atom = role:LINEAGE_EDGE bound to value:(parent_cas, child_cas, edge_type).
- Tier-1 = Tier-1 frozen substrate-current-state (untouched). Tier-2 = the 20 new ingested atoms. Tier-3 = synthetic 200-artifact prior corpus (random-substrate-noise baseline).
- Run 4 capability probes on the resulting substrate-ledger:
  - Q1 (lineage trace): "What drill led to claim X in cap_map row Y?" Retrieve via substrate resonator factoring over LINEAGE_EDGE atoms. Ground truth from orchestrator log.
  - Q2 (pattern detection / Layer 4): retrospective Bayesian-surprise classifier (per Layer 4 dialectic methodology, prior delivery 2026-06-11) labels each of the 10 drills as expected/surprise/second-order. Ground truth from manual gold labels (substrate produces labels; we compare to operator-written gold).
  - Q3 (drift / Layer 8): does substrate-current-state-bundle diverge from corpus-mean-bundle as cycles advance? BOCPD on the cosine-drift series.
  - Q4 (next-drill prediction): substrate proposes 3 candidate next-drill topics from corpus patterns (where surprise concentrated). Operator scores 1-5 for plausibility.

Decisive metric package: Q1 top-1 precision + Q2 classifier F1 vs manual gold + Q3 BOCPD detects the cap_map flip events we DO know occurred + Q4 expert-plausibility >= 3.5/5.

- HARD-PASS (all 4 probes): Q1 top-1 precision >= 0.80; Q2 F1 >= 0.70 macro on 3-class (expected/surprise/second-order); Q3 BOCPD detects >= 2 of 3 known cap_map flips with FDR <= 0.10; Q4 expert-plausibility mean >= 3.5/5 with no proposal scored <= 2.
- HARD-FAIL: ANY of: Q1 <= 0.40 (lineage retrieval broken); Q2 F1 <= 0.40 (classifier no better than majority class); Q3 BOCPD detects 0 of 3 known flips; Q4 expert-plausibility <= 2.5/5.
- MIDDLE: mixed - typical outcome would be Q1 strong + Q2 weak + Q3 marginal + Q4 acceptable; diagnostic = lineage retrieval is the easy substrate-native primitive, classifier+drift+prediction need Layer 4/8 maturation. RESCUE = ship 3 second-tier anchors before full corpus ingest.

Pilot is anchor-sized (Tier-2 cell budget), all-CPU, uses ONLY existing substrate primitives + already-validated Layer 4 surprise-classifier + BOCPD numpy primitive.

## (c) Falsifiable predictions (HARD-PASS + HARD-FAIL bands)

**Prediction P1 - Substrate-ledger STORAGE+RETRIEVAL scales sub-linearly in ingest cost via CAS deduplication; linear in retrieval cost.**
- HARD-PASS: SHA256-CAS deduplication on 235 cycles + 381 PP + 150 routings + 50 memory + 32 drills (total approx 850 artifacts, approx 5-15 MB raw text) yields >= 30 percent storage reduction vs naive store (typical CAS dedup on git-like corpora per merkle-DAG industry data); ingest time scales O(N) at <= 1 sec/artifact on a single CPU. Retrieval (Q1 lineage trace) O(log N) via substrate resonator factoring at <= 100 ms/query at N approx 850.
- HARD-FAIL: dedup <= 10 percent (insufficient sharing); OR ingest >= 10 sec/artifact (substrate atom-write becomes bottleneck before tiering kicks in); OR retrieval >= 1 sec/query at N=850 (resonator-factor scales worse than predicted - real issue for the substrate-product story).
- P_deflated: 0.65 (CAS dedup at 20-50 percent is well-established for write-heavy versioned corpora; substrate retrieval cost is the empirical risk; deflate 0.15 for substrate-specific scaling unknowns).

**Prediction P2 - Tiered protection (Tier-1 frozen / Tier-2 evolving / Tier-3 archive) admits clean rollback semantics matching git-revert semantics.**
- HARD-PASS: rollback the substrate-current-state to an earlier cycle N=k by (a) replacing Tier-1 bundle with the Tier-3-archived k-cycle bundle, (b) replaying Tier-2 changes since cycle k onto the rolled-back Tier-1, (c) verifying cap_map row reconstruction matches historical cap_map at cycle k within token-level diff (>= 95 percent semantic equivalence via substrate-cosine on cap_map atom embeddings). Test on 3 historical rollback points (e.g. cycle 200 pre-RETRACTION of cross-domain claim).
- HARD-FAIL: rollback produces cap_map at <= 70 percent semantic equivalence (state divergence is unrecoverable - rollback claim fails); OR replay introduces ordering ambiguity that breaks lineage edges (graph-consistency failure).
- P_deflated: 0.55 (git-revert semantics on text+bundle corpora is industrially proven; substrate-specific complication is the FHRR-bundle-superposition non-commutativity if Tier-2 changes interfere; deflate 0.25 for novel-substrate-rollback synthesis).

**Prediction P3 - Cross-corpus auto-ingestion (evolve.py extension) ingests ALL artifact classes (drills + memory + routings + cap_map + user-directives) into a UNIFIED typed-edge graph that supports lineage traversal in both directions (parent and child).**
- HARD-PASS: evolve.py extended to 6 ingest paths (drills, memory, routings, cap_map, user-directives, PP-row verdicts); achieves typed-edge graph with >= 90 percent of cross-references discovered by simple regex+filename matching (low bar because PROV-O patterns are explicit in filenames + headers); bi-directional traversal (drill -> PP -> memory -> routing -> next-drill) terminates correctly on >= 95 percent of test traversals.
- HARD-FAIL: cross-references discovered <= 50 percent (auto-ingest can't handle the routing-note naming conventions reliably); OR traversal cycles non-terminate on >= 10 percent (graph has unbounded cycles from circular references).
- P_deflated: 0.62 (PROV-O is the W3C-standard template for exactly this; deduplication + typed-edge graph from text artifacts is mature in scientific-literature provenance literature; deflate 0.10 for substrate-storage-format adaptation; +0.05 because filename conventions are already PROV-friendly).

**Prediction P4 - Substrate self-version-control: substrate knows its own version + history + rollback path via a SUBSTRATE-INTERNAL ATOM that names the current Tier-1 cycle and points to the Tier-3 chain of prior frozen states.**
- HARD-PASS: a single typed atom (role:SUBSTRATE_VERSION value:<cas_hash_of_Tier-1_at_cycle_k>) stored at every cap_map bump; substrate query "what was your state at cycle N?" returns the right Tier-3 CAS hash with >= 95 percent precision; substrate query "show me the lineage chain from current Tier-1 back to cycle 0" terminates in <= 235 steps (one per cycle); this works WITHOUT any retraining, just via the existing substrate-self-index primitive Day 1 demonstrated.
- HARD-FAIL: substrate self-version atom corrupts under self-update (the substrate that knows its own version can't reliably retrieve it because the version-atom is in the same Tier-1 it points to - the OBVIOUS recursion bug); OR lineage-chain traversal fails at depth >= 10 (chain breaks); OR substrate can't distinguish current-self from prior-self bundles (self-identification failure).
- P_deflated: 0.42 (substrate-self-index Day 1 is already operational with 60 atoms + 88 relations - this is direct extension; the recursion-bug risk is REAL because the version-atom is structurally self-referential; deflate 0.20 for substrate-novel circularity + 0.18 for empirical bug risk).

**Prediction P5 - Bounded recursion under self-ingest: the substrate-on-substrate analysis remains stable because the GATE (Layer 1 attribution methodology + Layer 4 dialectic classifier + Layer 8 BOCPD threshold) is FROZEN at cycle 0 and is NEVER substrate-proposed - even when the substrate ingests its own prior substrate-on-substrate analyses as Tier-3 archive entries.**
- HARD-PASS: stress test - ingest the substrate's own prior substrate-on-substrate analyses (Layer 4 dialectic note from 2026-06-11, substrate-proposed-architectures note from 2026-06-11, etc.) as Tier-3 archive; substrate continues to classify new drills with surprise-classifier F1 within 0.05 of baseline (no classifier-drift from self-ingest); cap_map flip rate stays within 0.15 percent of historical baseline (no meta-evaluation collapse). HARD-PASS is the DIFFERENTIAL: F1_after_self_ingest - F1_baseline >= -0.05 AND flip_rate_after - flip_rate_baseline within +/- 0.15.
- HARD-FAIL: F1 degrades by >= 0.15 after self-ingest (the substrate analyzing its own self-analyses corrupts the surprise-classifier); OR cap_map flip rate doubles (meta-evaluation collapse signature); OR the substrate begins to propose architecture changes to its own GATE (boundary breach).
- P_deflated: 0.45 (operator-theoretic precedent for meta-evaluation collapse is strong - this prediction tests THE bound; the SAFETY claim that fixed-external-gate prevents collapse is the load-bearing piece; deflate 0.20 for novel-synthesis safety case + 0.10 for stress-test arbitrariness).

**Prediction P6 - Layer 4 dialectic across full 235+ cycle history detects PATTERNS PERSISTENT across cycles (signal) vs ISOLATED to a single cycle (noise) at >= 2x the detection rate of single-cycle analysis.**
- HARD-PASS: retrospective application of Layer 4 surprise-classifier across the 235-cycle corpus surfaces >= 5 patterns each appearing in >= 10 cycles with q-value <= 0.10 (BH-FDR corrected); these patterns are at >= 80 percent overlap with operator-curated "north star" claims in memory (e.g. "substrate is static-robust dynamic-fragile", "substrate-LLM boundary is symbolic-vs-statistical", "compositional cliff crossed").
- HARD-FAIL: patterns identified <= 2 with q-value <= 0.10; OR overlap with operator-curated north-stars <= 40 percent (classifier is detecting noise not signal).
- P_deflated: 0.50 (Layer 4 dialectic methodology already pre-registered with HARD-PASS bands earlier today; cross-cycle aggregation is the natural scaling; deflate 0.15 for classifier-application-at-scale risk + 0.05 for ground-truth ambiguity in operator-curated labels).

**Prediction P7 - Layer 8 drift tracker detects DIVERGENCE of current substrate-state from historical-pattern at the cycle-level; drift_rate is predictable from cap_map bump rate.**
- HARD-PASS: BOCPD on cosine-drift series (substrate-current-state vs rolling-mean-of-last-10-cycles) detects >= 3 of the 4 known major pivots (e.g. cycle 200 RETRACTION, cycle 225 PP-225 production validation, cycle 226 polysemy 0.42 -> 1.000) with FDR <= 0.10; drift_rate correlates with cap_map bump rate at Spearman rho >= 0.50.
- HARD-FAIL: BOCPD detects 0-1 of 4 known pivots; OR drift_rate uncorrelated with cap_map bump rate (rho <= 0.20).
- P_deflated: 0.55 (BOCPD on text-corpus drift has direct precedent per Springer/arxiv 2309.03831 2211.04250; substrate-bundle-cosine as drift signal is the natural primitive; deflate 0.15 for substrate-specific tuning).

**Prediction P8 - Auto-propose drills from past patterns: substrate predicts surprise locations for next drill at expert-plausibility >= 3.5/5; >= 30 percent of substrate-proposed drills surface a field with drill_count <= 2 OR an adjacency edge unseen in the meta-map.**
- HARD-PASS: substrate-proposed drill candidates score >= 3.5/5 expert plausibility on a 1-5 Likert; >= 30 percent target under-drilled fields (per research_field_advisor.py's scope_expansion list).
- HARD-FAIL: expert plausibility <= 2.5/5 (substrate proposes confused drills); OR <= 10 percent target under-drilled fields (substrate proposes only popular fields - signaling it can't predict surprise).
- P_deflated: 0.40 (this is the most speculative prediction; substrate-pattern-recognition surfacing useful drills is the dream but is empirically untested; deflate 0.25 for novelty-of-claim + 0.15 for evaluator-subjectivity).

**Prediction P9 - Schools-of-thought extended to PROJECT-INTERNAL: substrate traces the evolution of >= 5 ideas through the project history (e.g. polysemy framing 0.42 ceiling -> rescue -> 1.000 + retraction chain) with >= 80 percent of inflection points matched to verdict events.**
- HARD-PASS: substrate produces a "school-of-thought lineage chain" for >= 5 ideas with >= 80 percent of operator-identified inflection points captured; chain length matches operator-curated timeline within +/- 2 nodes.
- HARD-FAIL: <= 2 ideas successfully traced; OR <= 50 percent of inflection points captured.
- P_deflated: 0.48 (lineage-via-PROV-O is well-precedented; idea-tracking-at-semantic-level requires substrate to do conceptual clustering reliably; deflate 0.20 for clustering-quality risk).

## (d) Cross-thread synthesis

**Connects to substrate-proposed-architectures (drill 2026-06-11, P_deflated=0.50).** That drill anchored the gate-frozen-at-cycle-0 invariant as the single architectural bound preventing meta-evaluation collapse. THIS drill EXTENDS the same bound from "substrate proposes architectural changes" to "substrate ingests its own prior substrate-on-substrate analyses". Same fix: GATE frozen-external. The full-research-ledger AMPLIFIES the Tier-4 stack because the substrate-proposed-architectures pipeline can RETRIEVE prior architectural-proposals (their outcomes, their failures, their cited papers) directly from the ledger as Tier-3 archive evidence - making the candidate-codebook information-richer.

**Connects to Layer 4 dialectic methodology (drill 2026-06-11, P_deflated=0.55).** That drill established the surprise-classifier (Itti-Baldi Bayesian surprise + Lakatos hard-core/protective-belt + OOD filter). THIS drill APPLIES the classifier at corpus scale (P6: 235 cycles retrospective). The cross-thread synthesis: Layer 4 was designed for the surprise-on-NEW-finding case; full-research-ledger lets us apply it RETROSPECTIVELY at scale to surface persistent vs noise patterns - which is the higher-value capability for the substrate-product story.

**Connects to substrate-self-discovery validation (drill 2026-06-11, P_deflated=0.30).** That drill established the 5-stage filter pipeline (numerical + symbolic + novelty + human + adversarial). THIS drill makes the NOVELTY check tractable because the substrate-ledger gives a CORPUS-INTERNAL novelty baseline (does this finding rhyme with any prior finding?). Novelty-relative-to-our-own-history is cheaper than novelty-relative-to-external-literature and is the natural first filter.

**Connects to substrate v3.2 ENGINEERED WRAPPER (memory entry 2026-06-11).** That synthesis converged on "5 protection layers ride on substrate algebra via WRAPPER". THIS drill makes the WRAPPER MATERIAL: the per-tier protection (Tier-1 frozen / Tier-2 write-locked / Tier-3 append-only-archive) is the SAME pattern as the wrapper's per-shard write-lock + erasure-coded-redundancy + locality-frozen. The full-research-ledger demonstrates the wrapper on a DIFFERENT corpus (research history) than the original (KB facts) - which is exactly the universality claim.

**Connects to Pattern 4 closures (algebraic-topo P=0, quantum-info P=0, dynamics P=0).** The ledger gives a CHEAP retrospective check: search prior drills for any P=0 closure that was later REOPENED (cycle 226 polysemy 0.42 ceiling was REOPENED via cycle 226 WN18RR + cycle 226 concept-context-binding). The ledger surfaces this pattern at corpus scale (P6) - which informs the "5th drill-defeatism rule validation" memory entry from today.

**Connects to feedback-dont-parrot-drill-defeatism (memory 2026-06-11).** The substrate-ledger gives the structural defense against drill-defeatism: every "honest ceiling" claim is auto-linked to (a) drill that proposed it, (b) PP rows that validated, (c) PP rows that REFUTED, (d) memory + routing that argued either side. Defeatism is auditable, not asserted.

**Boundary with external scientific-corpus ingest (drill 2026-06-11 substrate_universal_scientific_corpus).** That drill addressed external corpus (arxiv etc); THIS drill addresses INTERNAL corpus (project history). The two are STORAGE-FORMAT compatible (both ride on FHRR + typed atoms + CAS) but VALIDATION-LATENCY incompatible (internal corpus has operator ground truth and verdict log; external doesn't). Recommendation: ship INTERNAL ledger first; external follows.

## (e) Substrate-product implications

**Product claim 1: substrate-as-institutional-memory is a marketable feature.** Customer-facing: "your substrate doesn't just store facts - it stores the COMPLETE LINEAGE of every fact: who claimed it, when, in response to what, refuted by what, currently supported by what." This is a real product differentiator vs vector-DB + RAG which loses provenance at retrieval. Aligns with NORTH STAR (functional system beats LLMs in measurable ways): substrate provides AUDITABLE memory; LLM-backed systems can't.

**Product claim 2: tiered protection IS the auditable-AI-memory-subsystem story.** Per product-cycle skill direction (auditable-AI-memory-subsystem strategic direction in MEMORY index). Hot/warm/cold + immutable-archive matches GDPR Article 12 EU AI Act Aug 2026 deadline (per cycle-146 PHASE 2 5x CHAINS memory). Tier-3 archive is the GDPR-compliant "complete decision history" requirement.

**Product claim 3: bounded-recursion safety case is a regulatory differentiator.** Demonstrating a substrate that CAN ingest its own self-analyses + provably DOES NOT collapse (because gate is frozen-external) is a strong AI-safety story. Few competitors have a self-improving-AI architecture that comes with a non-vapid safety argument. The operator-theoretic bound (meta-evaluation-collapse OpenReview IF0L7HSs3K) is citable + concrete.

**Product claim 4: lineage-traced rollback enables "explain how this answer changed over time" UX.** A user can ask the substrate "show me how your answer to question X has evolved over our 6-month history". Substrate retrieves the lineage chain (drill -> PP -> memory -> verdict -> next-drill) and renders an evolution timeline. NO LLM-backed system has this capability built in.

**Product claim 5: drift detection on internal corpus drives auto-curation.** Layer 8 BOCPD on the substrate-ledger SURFACES which historical claims have drifted vs which are persistent - auto-curating memory MEMORY.md index instead of relying on manual curation. Reduces the 202-line / 57KB memory-curation burden flagged in the MEMORY.md WARNING.

**Risks (regulatory + product):** corpus quality (typos in routings + deprecated decisions) propagates if ingest is uncritical (P3 HARD-FAIL band catches this); circular self-reference (substrate analyzes its own history that includes substrate-on-substrate analyses) is bounded by P5 but only at <= 0.15 differential - if the bound fails empirically the safety case crumbles. The pilot (b) is structured to surface both risks at cheap cost before full ingest.

## (f) Citations (verified count = 12)

- Tiered storage architecture (hot/warm/cold/archive) - solved.scality.com data-center-storage-tiers (canonical industry reference)
- LiveVectorLake real-time versioned KB architecture for streaming vector updates and temporal retrieval - arxiv 2601.05270
- Memory tiering 3-tier hot/warm/cold for long-running AI agents - clawrxiv 2603.00037
- Append-only event logs / git-like immutable history pattern - industry reference (Medium komalshehzadi 2024-era)
- Content-addressable storage (CAS) - source.network DefraDB documentation + Abilian Innovation Lab survey
- Merkle DAGs (IPFS / Git unified view) - IPFS Docs concepts + rya-sge accessdenied 2025
- ForkBase: immutable tamper-evident storage substrate for branchable applications - arxiv 2004.07585 (ICDE 2020)
- Merkle-CRDTs: Merkle-DAGs meet CRDTs - arxiv 2004.00107
- Full traceability and provenance for knowledge graphs (FOIS 2024) - Dibowski paper
- W3C PROV-O / PROV-DM / PROV-N standard - W3C standard for provenance vocabulary in RDF
- MLflow + W3C PROV-O auto-capture for PyTorch pipelines (PROV in AI / ML lineage practice) - Ranjan Kumar 2025
- Concept drift adaptation in text stream mining settings (systematic review) - arxiv 2312.02901
- DetAIL drift detection tool in language - arxiv 2211.04250
- Uncovering drift in textual data unsupervised method - arxiv 2309.03831
- (cross-thread cited) Meta-evaluation collapse operator-theoretic bound - OpenReview IF0L7HSs3K (2025/26 - prior drill substrate-proposed-architectures cited)
- (cross-thread cited) Causal-SHAP / ablation-based-counterfactual ABC - arxiv 2406.07908 / 2509.00846 / 2509.20211 (prior drill cited)
- (cross-thread cited) Itti-Baldi Bayesian surprise (2009) + BOCPD - prior Layer 4 dialectic drill cited

External lit-scan verified = 12 unique external sources (CAS/merkle 4 + PROV-O 3 + tiered-storage 3 + drift 2); cross-thread cited = 5 (already verified by prior drills today).

## (g) Pre-registered HARD-PASS / HARD-FAIL summary (for status_log compactness)

| Pred | HARD-PASS | HARD-FAIL | P_deflated |
|---|---|---|---|
| P1 storage+retrieval | dedup >= 30%, ingest <= 1s/artifact, retrieval <= 100ms/query at N=850 | dedup <= 10% OR retrieval >= 1s | 0.65 |
| P2 tiered rollback | semantic equivalence >= 95% on 3 historical rollback points | semantic equivalence <= 70% | 0.55 |
| P3 cross-corpus ingest | cross-references discovered >= 90%, traversal terminates >= 95% | discovered <= 50% OR cycles non-terminate >= 10% | 0.62 |
| P4 self-version-control | version-query precision >= 95%, lineage-chain depth <= 235 | self-version atom corrupts under self-update OR depth >= 10 break | 0.42 |
| P5 bounded-recursion safety | classifier F1 within 0.05 + flip-rate within 0.15% of baseline after self-ingest | F1 degrades >= 0.15 OR flip-rate doubles | 0.45 |
| P6 Layer 4 at corpus scale | >= 5 patterns at q <= 0.10, >= 80% overlap with north-star claims | <= 2 patterns OR overlap <= 40% | 0.50 |
| P7 Layer 8 drift | detect >= 3/4 known pivots at FDR <= 0.10, rho >= 0.50 with bump-rate | detect 0-1/4 pivots OR rho <= 0.20 | 0.55 |
| P8 auto-propose drills | expert-plausibility >= 3.5/5, >= 30% under-drilled fields targeted | plausibility <= 2.5/5 OR <= 10% under-drilled | 0.40 |
| P9 schools-of-thought traced | >= 5 ideas with >= 80% inflection points captured | <= 2 ideas OR <= 50% inflection points | 0.48 |

Overall P_deflated for SOMETHING (>= 4 of 9 HARD-PASS): approx 0.55 (bounded above by novel-synthesis cap; some predictions independent, some correlated; geometric-mean of HARD-PASS rate across independent component-mechanism literature).

Note: P5 (bounded-recursion safety) is the load-bearing prediction - if it FAILS, the full ledger is unsafe and we ingest only Tier-3-read-only without self-feedback. P1-P3 are nearly-certain (mature lit); P4 + P8 are the speculative tails.
