# Pre-reg: arc_retrieval_seed_upgrade_ppr_v2

date: 2026-07-24
cell: experiments/exp_arc_retrieval_seed_upgrade_ppr_v2.py
predecessor: arc_retrieval_multicue_ppr_discriminative_v1 (VET'd/banked 29539, MIDDLE_BAND)
contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; GloVe+WorldTree git-ignored/large => NOT remote-portable; repo .venv; ASCII-only; deterministic (fixed seeds, numpy default_rng, sorted iteration, no hash()); agent-reported VET-PENDING.

## Question
The v1 retrieval cell VALIDATED spreading activation on the REAL WorldTree graph (PPR recall@10 0.3796 vs cosine 0.2798, +0.0998; shuffled control 0.0007) but MISSED the +0.15 HARD-PASS bar and precisely attributed the shortfall to SEEDING: seed_recall 0.365 < 0.50 make-or-break floor. THIS cell upgrades SEED IDENTIFICATION (entity-linking) as the ONE variable and asks: (i) does better seeding clear the 0.50 seed_recall floor + lift fact recall@10 past +0.15? and (ii) THE KEY WATCH -- does higher recall NOW translate to end-to-end ARC, or is retrieval-recall necessary-but-not-sufficient?

## One variable = SEEDING (everything else BIT-UNCHANGED from v1 arm B)
Upgraded seed-linking (brain-grounded lexical access): (1) WordNet morphy morphological normalization via a seeding-only lemma index (graph UNCHANGED); (2) WordNet synonym+hypernym expansion (reuse SemanticHDEncoder._wn_neighbors); (3) lower SEED_COS 0.60->0.45; (4) multi-token bigram phrase seeds. Graph, PPR (2 hops, damp 0.5, idf-weighted transition), and the bind+settle combiner (imported agg.aggregate) are BIT-UNCHANGED. Dropped v1's discriminative re-rank (HURT: v1 C 0.1953<B 0.3796) and hub-idf ablation arm (near-inert: v1 C-E +0.0046).

## Arms
- A  baseline_single_shot   : cosine top-K (QQ @ SV_store.T), unchanged. Head-to-head baseline.
- B0 ppr_baseline_seeds     : PPR with v1/OLD seeds (SEED_COS 0.60, single-word exact+semantic). Gate-D positive control; expect ~0.38 (reproduce v1 arm B).
- B  ppr_upgraded_seeds     : PPR with UPGRADED seeds. [MECHANISM / new variable]. B-B0 isolates the seeding delta.
- D  shuffled_graph_control : B's upgraded seeds on degree-preserving edge-permuted graph. MUST collapse toward A.

## Metrics + bands (author-designed a priori; embedded as cell constants)
PRIMARY (i) seed_recall vs WorldTree gold entity mentions: floor SEED_QUALITY_FLOOR=0.50 (make-or-break).
PRIMARY (ii) recall@10 of gold central facts: HP_RECALL_LIFT B-A >= 0.15 (bar v1 missed at +0.0998); MB_RECALL_LIFT [0.05,0.15).
STRUCTURAL: HP_D_COLLAPSE D-A <= 0.03 (lift is graph-structure-driven).
KEY WATCH (secondary, load-bearing): end-to-end ARC Easy+Challenge through the UNCHANGED combiner; PAIRED McNemar exact test B-vs-A on Challenge; binomial CI vs chance.

Verdict tiers:
- SEED_UPGRADE_HARD_PASS : lift>=0.15 AND D collapses AND seed_recall>=0.50.
- SEED_UPGRADE_MIDDLE_BAND : seed_recall>=0.50 OR lift in [0.05,0.15) (seeding helps, recall not decisively past +0.15).
- SEED_UPGRADE_HARD_FAIL : seed_recall<0.50 AND lift<0.05.
- RETRIEVAL_DISCRIMINATOR_SATURATED : baseline A recall>=0.95 (no headroom).
- necessary_but_not_sufficient FLAG : recall/seed win but end-to-end B NOT significantly > A (McNemar p>=0.05) => combiner/pool-K dilution is the NEXT wall. DO NOT tune to force an end-to-end win.

## Discipline gates
- storage = SHARDED (each fact = own vector + own graph node; no superposition).
- discriminator survives scale: smoke runs the FULL 9720-fact graph (only question set subset).
- Gate D positive control: B0 reproduces prior arm B within B0_REPRO_TOL=0.06.
- baseline_in_band (0.05<A<0.95); arms-differ (A,B0,B,D digests distinct + B!=B0).
- deterministic_seeding (fixed int seeds, numpy default_rng, sorted iteration, no hash()).
- final_metrics_atomicity=tmp_replace; start-marker; crash-diagnostic; heartbeat.
- progress_logging=line_buffered_stdout (+ flush=True); compute_architecture=mixed CPU, wall<10min.

## RESULT (MEASURED@ data/exp_arc_retrieval_seed_upgrade_ppr_v2/metrics.json ; FULL, 1664 q = 1177 Easy + 487 Challenge)
verdict = SEED_UPGRADE_MIDDLE_BAND (elapsed 165.2s).
- seed_recall 0.5446 CLEARS the 0.50 floor (v1 0.365; baseline-seed arm here reproduces 0.365 exactly). BUT seed_precision cratered 0.342->0.0677 (mean_seeds 13.58->112.23).
- recall@10: A=0.2798 (=v1), B0=0.3796 (=v1 arm B EXACTLY; positive control reproduced), B=0.3828, D=0.0024. lift B-A=+0.1030 (MIDDLE). SEEDING-ONLY delta B-B0=+0.0032 (FLAT).
- KEY WATCH end-to-end Challenge: A=0.3101 (=v1), B=0.3552 (+0.045); McNemar b=49 c=71 p=0.0548 (NOT significant); B CI [0.3127,0.3977] above chance 0.25, but B-vs-A NOT significant. necessary_but_not_sufficient=True.

## Finding (honest, VET-PENDING)
Raising seed_recall (0.365->0.545) did NOT raise fact recall@10 (B-B0=+0.0032, flat): the extra correct gold-term seeds were canceled by an ~8x precision collapse (noise seeds dilute the PPR personalization; D still collapses so structure drives it). => seed-TERM coverage is NOT the operative bottleneck for fact retrieval; recall@10 is capped by 2-hop graph reach + K=10, not seed count. End-to-end Challenge lift (+0.045) is real-direction but NOT significant at full scale (smoke p=0.0115 regressed to full p=0.0548 -- classic smoke-inflation). Necessary-but-not-sufficient confirmed: the NEXT wall is the combiner / pool-K dilution and seed PRECISION (better seeds, not more), per the v1 redirect. NOT tuned to force an end-to-end win.
