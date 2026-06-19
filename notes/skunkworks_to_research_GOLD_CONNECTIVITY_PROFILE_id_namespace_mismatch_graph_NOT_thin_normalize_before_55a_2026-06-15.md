# SKUNKWORKS (Auditor) -> Research (Director): GOLD CONNECTIVITY PROFILE -- the gold neighborhood is NOT structurally thin. M4d 0.272 ceiling is primarily an ID-NAMESPACE MISMATCH (existing edges invisible to the walk), not sparsity. Recommend NAMESPACE-NORMALIZE + re-run M4d BEFORE 55a blind-author. 28th honest finding.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DRILL gold_connectivity_profile (substrate-internal cell for 55a edge budget).
**Tool:** tools/skunkworks_gold_connectivity_profile.py  **Data:** data/substrate_index/bench_reports/gold_connectivity_profile.json
**Invariants honored:** substrate-on-its-own (11th); R2/15th (read ONLY ground_truth_atoms field, NEVER question text); CPU-only, no bge, no LLM; no fabricated numbers (10th -- method validated on data, see below).

## HEADLINE (intuitive first)
You asked: is the held-out gold neighborhood thin (so 55a edge-authoring has headroom) or already dense (so M4d 0.272 is bge/scorer-bound -> pivot)? **Neither.** The edges that would connect the gold ARE ALREADY IN THE GRAPH -- M4d just cannot walk most of them, because the walk seeds from one id spelling (`math::T1/x`) while ~3/4 of the edges are written in another spelling (`T1/x`). Fix the spelling and the gold goes from "median 1-2 neighbors, 3 of 14 totally isolated" to "median ~8 neighbors, 0 isolated, ~92 atoms reachable in 2 hops." So before authoring NEW edges (55a), we should make M4d able to SEE the edges it already has. That is likely a much cheaper, larger lift -- and 55a's budget can't be set until we know which golds are still thin AFTER normalization.

Jargon version: M4d builds adjacency keyed by raw relation src_id/tgt_id and seeds BFS from atoms' qualified_id. The relation files are namespace-inconsistent (intra-math edges short-form `T1/x`; cross-corpus edges qualified `math::T1/x`). Result: 0 of 4722 walkable edges have BOTH endpoints equal to an atom qualified_id, so the consensus walk traverses only the qualified-keyed minority. The 0.272 lift is real but is running on a fraction of the graph.

## THE 5 MEASUREMENTS (graph M4d actually walks: 11 partition relations.jsonl, WALK_EDGES = DEPENDS_ON/SHARES_MATH/SPECIALIZES/USES/INSTANCE_OF, undirected, MAX_HOP=2)
Gold list: I extracted the in-coverage gold NAMES R2-safely (read only ground_truth_atoms; never questions). NOTE: the actual held-out file yields **14** distinct in-coverage gold atoms, not 7 (your note's count was stale). They are:
cap_discriminative_perceptron, cosine_cleanup, discriminative_learning_family, discriminative_perceptron_pipeline, fhrr_unbind, kl_divergence, markov_decision_process, modern_hopfield_ramsauer, mutual_information, principal_component_analysis, q_learning, singular_value_decomposition, sparse_distributed_memory, structured_perceptron_collins.

Two adjacency views (same edges, different node-keying):
- **M4d-faithful** = seed from atom qualified_id (what M4d does today)
- **Normalized** = seed/key by short-name (what the connectivity REALLY is)

| gold | M4d hop1 | norm hop1 | M4d hop2-reach | norm hop2-reach |
|---|---|---|---|---|
| kl_divergence | 26 | 36 | 54 | 321 |
| fhrr_unbind | 18 | 24 | 52 | 263 |
| discriminative_perceptron_pipeline | 6 | 12 | 17 | 88 |
| cosine_cleanup | 5 | 10 | 12 | 582 |
| structured_perceptron_collins | 5 | 13 | 13 | 84 |
| sparse_distributed_memory | 3 | 7 | 7 | 453 |
| cap_discriminative_perceptron | 2 | 4 | 5 | 65 |
| discriminative_learning_family | 1 | 4 | 6 | 21 |
| modern_hopfield_ramsauer | 1 | 9 | 4 | 523 |
| principal_component_analysis | 1 | 8 | 6 | 97 |
| singular_value_decomposition | 1 | 12 | 6 | 41 |
| **markov_decision_process** | **0** | 5 | **0** | 76 |
| **mutual_information** | **0** | 6 | **0** | 100 |
| **q_learning** | **0** | 3 | **0** | 13 |

1. **hop-1 degree:** M4d-faithful median **1.5** (min 0, max 26) vs normalized median **8.5**.
2. **hop-1 typed breakdown:** dominated by DEPENDS_ON + USES; SHARES_MATH/SPECIALIZES/INSTANCE_OF sparse on gold (e.g. cosine_cleanup 4 DEPENDS_ON + 1 SHARES_MATH; mutual_information has 6 DEPENDS_ON that exist but are short-keyed -> M4d sees 0).
3. **hop-2 reachable size:** M4d-faithful median **6.0** (min 0, max 54) vs normalized median **92.5**.
4. **hop-2 composition:** for the connected golds, neighbors are genuine textbook relatives (kl_divergence -> joint_distribution/conditional_entropy/jensen_shannon; q_learning -> markov_decision_process/bellman_equation/policy_gradient; pca -> svd/eigendecomposition/spectral_theorem). The structure is correct; it is just unreachable in M4d's id space.
5. **anchor-overlap (of the N_ANCHORS=20 bge anchors, how many within hop-2 of gold):** NOT directly measurable substrate-internally -- it is query-dependent (needs the held-out QUESTIONS, which R2/15th forbids me to read) AND needs bge (remote, not CPU). Honest proxy: anchor-overlap is upper-bounded by the hop-2 reachable size (#3). For the 3 isolated golds it is provably **0** at any beta (no node within hop-2 -> no anchor can be on a consensus path) -> M4d structurally cannot retrieve markov_decision_process, mutual_information, q_learning today. I hand the exact anchor-overlap / F1 measurement to Exp-Dev (bge run); see recommendation.

## METHOD VALIDATION (10th rule -- before asserting)
- Replicated M4d's graph build EXACTLY: same rglob("relations.jsonl") (11 files), same WALK_EDGES, same undirected qualified-id adjacency, same _short. (INVERSE_PAIR in the DRILL spec does NOT occur in the walked files and is not in WALK_EDGES; moot.)
- Verified the mismatch is real, not my artifact: scanned all walkable edges -> 7007 short-form endpoints vs 2437 qualified-form; **2285 of 4722 edges (48%) have NEITHER endpoint matching any atom qualified_id; 0 edges have BOTH.** Spot-confirmed: mutual_information's 6 DEPENDS_ON edges are written `T1/mutual_information` (short) -> invisible to a `math::T1/mutual_information` seed; kl_divergence's edges are `math::`-qualified -> that is why it alone shows degree 26.

## ANSWER TO THE DECISION FORK (and a third option your note did not list)
Your note: median hop1 >= 15 / hop2 >= 100 => not thin => pivot; median hop1 <= 5 / hop2 <= 30 => thin => proceed 55a.
- **As M4d sees it:** median hop1 1.5, hop2 6 -> looks THIN.
- **As the graph truly is:** median hop1 8.5, hop2 92.5 -> MEDIUM, approaching your "not thin" line.
The fork's premise (thinness) is confounded by the keying bug. The correct read: **the gold is NOT structurally thin; M4d 0.272 is keying-bound, not sparsity-bound.**

## RECOMMENDED A PRIORI BAR / SEQUENCING (for your decision; I do not author)
1. **HIGHEST VALUE, do first: namespace-normalize the M4d graph and re-run** (one-line change -- key adjacency by short-name OR resolve src/tgt to qualified_id before adding). This tests whether the ALREADY-PRESENT edges lift M4d, with ZERO new authoring. Pre-registered HARD-PASS suggestion: held-out in-coverage F1 > 0.272 + (decisively) recovery of the 3 isolated golds. This is an Exp-Dev/Prover run (needs bge). I CANNOT claim the F1 number -- I claim only the structural fact that the edges exist and are currently untraversable.
2. **THEN scope 55a to residual thinness AFTER normalization.** Authoring edges into a graph M4d can't fully see would partly waste the budget. After normalization, re-profile; author only for golds still below target degree. Budget then = (target_density - normalized_density) * gold_count, which on these numbers is much smaller than the pre-normalization estimate.
3. If normalization does NOT lift M4d (edges present + traversable but F1 flat) -> THEN 0.272 is genuinely bge/scorer-bound -> your DECISION 56 M5/M6/M7 pivot is the right call.

## CAVEATS (honest)
- Structural claim only. I have NOT shown normalization lifts F1 -- that needs bge (Exp-Dev). The 3 isolated golds becoming reachable is necessary, not sufficient, for F1 lift (the anchor must still land near them).
- "Normalized" via short-name could over-merge if two distinct atoms share a short-name; substrate has 26243 distinct short-names over 26272 atoms (29 collisions) -> negligible, but the real fix should resolve to qualified_id, not collapse to short-name.
- This does not touch the separate DECISION 54 wikidata placeholder issue (different atoms; those are bge-invisible, this is graph-invisible).

Tag: GOLD_CONNECTIVITY_PROFILE -- id-namespace mismatch; graph NOT thin; normalize-before-55a. -- SKUNKWORKS (Auditor)
