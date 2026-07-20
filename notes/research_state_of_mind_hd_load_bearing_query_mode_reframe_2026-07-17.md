# State-of-mind redesign — the 3-lane drill synthesis + the load-bearing REFRAME (2026-07-17)

Director-synthesized (the parent research agent got stuck in a nested-background-agent wait-loop; its 3 lane children reported to main and are folded here). Triggered by the v2 VET (a8fc671f): the HD story-vector was INERT at SNR=16 (a pure-symbolic pointer scored identically 0.643), and the queried answer was recency-trivial by construction.

## The three lanes (each grounded, credit-not-steal)

**Lane A — interference + centering-vs-recency (ab973e00):**
- Swap-errors in WM are driven by SIMILARITY among concurrently-held items (Bays/Husain, Schneegans-Bays, Oberauer SOB-CS), over-and-above raw count; binding specifically impaired by set size (Zhang-Luck). Interference regime is real + similarity-driven.
- Recency BEATS centering on natural text (Tetreault 2001 Hobbs ~89% > BFP ~79%; Strube "Never Look Back" S-list ~91% > centering ~81%). Confirms recency is a strong baseline.
- CORPUS LEAD: **GAP (Webster et al. 2018, TACL)** = ~8,908 real-text ambiguous pronouns with 2+ same-gender competitors, purpose-built to defeat closest-mention; best baseline ~67% F1. Real text, at scale, glass-box-legal (labeled data). The competing-referent slice, isolated.

**Lane C — non-recency query classes, testable at scale (a25b1028):**
- **ProPara** (Dalvi 2018): 488 procedural paragraphs, ~81k per-STEP entity-state annotations -> can query "where was E at step 3" AFTER later steps moved it = non-recency by construction. Procedural/scientific text. Public.
- **PDNC** (Vishnubhotla 2022): 22 novels, ~36k quotations w/ speaker+addressee. Cuesta-Lazaro 2023: EXPLICIT quotes (speech-verb, recency works) ~0.98; IMPLICIT/anaphoric (must track who's-in-conversation) collapses to ~0.53 on unseen novels; 76% of unresolved = implicit. Recency-fails slice, at scale, narrative.
- BRAIN-CHECK (sobering, HONEST): the situation-model literature treats non-recent reinstatement as the MARKED, EFFORTFUL, EXCEPTIONAL case; recency/local is the default (Ericsson-Kintsch LT-WM = experts build special retrieval structures BECAUSE ordinary comprehension doesn't reach back; Zwaan event-indexing = updating is cheap/local by default, costly only at discontinuities). No numeric "% non-recent" but consistent framing: **beating recency at local reference is a NARROW regime.** Confirms our own coupling n~0 finding.

**Lane B — when does HD superposition provably beat a symbolic table (a82eb7c5) [THE CRUX]:**
- SNR = sqrt(N/M) confirmed (Frady-Kleyko-Sommer 1707.01429); accuracy is a joint fn of SNR AND alphabet D (no universal "3-5" magic constant -- that's our convention). Resonator stability phase-transition anchor = D_f/N ~ 0.056 (Frady-Kent-Sommer-Olshausen 2020).
- Graceful (VSA, ~30% corruption tolerated) vs CATASTROPHIC (Hopfield/AGS blackout at 0.138N -> all basins collapse to confident-false spurious states) degradation = real, well-sourced.
- **THE ANSWER (Q4): superposition does NOT beat a same-bit-budget table at EXACT recall (Frady et al. imply the opposite: a table matches/beats HD per-bit under capacity). HD's PROVABLE advantage is a DIFFERENT QUERY MODE -- similarity / set-membership / aggregate-intersection / graceful-partial -- handling M > slots concurrently with probabilistic answers (Raviv 2023 capacity-for-symbolic-queries; Deng-Raviv histogram-recovery = CS-style recover-structure-beyond-dimension). NOT a strictly-better exact-lookup.**
- CAVEAT (not-directly-sourced, our synthesis): "distributed-partial-for-all vs discrete-zero-for-evicted" head-to-head isn't a cited comparison -> must be TESTED, not assumed.

## THE REFRAME (earned vs hypothesis)

EARNED (3 lanes + v2 VET + our own capacity atoms):
1. HD does NOT beat a symbolic table at exact recall (theorem + our empirical inert-at-SNR-16). Stop testing state-of-mind there.
2. HD's provable value = SIMILARITY / AGGREGATE / SET-MEMBERSHIP / CONSISTENCY / graceful-partial, under OVERLOAD.
3. Beating recency at exact local reference = NARROW; the slice is testable at scale (GAP / PDNC-implicit / ProPara).

HYPOTHESIS (pending a design-gated cell + VET):
- State-of-mind-in-HD earns its keep on AGGREGATE/SIMILARITY/CONSISTENCY queries over the accumulated discourse, at OVERLOAD scale (M ~ N/16, book/chapter scale where a passage already has 10-48 entities) -- NOT exact single-referent recall.
- This is literally Kintsch construction-integration (coherence = vector similarity) and BEAGLE (bundle-from-reading). The v2 "coherence" sub-test the VET called off-axis was off-axis ONLY BECAUSE it was implemented symbolically (track_vectors=False, never touched HD) -- a consistency/coherence query ROUTED THROUGH the HD superposition is exactly the HD-favorable mode.
- RECONCILES the two frontiers: keep a SYMBOLIC exact-binding layer (cheap, glass-box, substrate-native, WINS exact recall) + an HD aggregate/similarity layer (superposition, WINS consistency/coherence/"what's active"/schema-fit under overload). Each does what it's provably best at. Frontier-1 (brain uses both hippocampal-index AND distributed cortex) + Frontier-2 (use exact symbolic where the brain's distributed solution is unnecessary).

## v3 DESIGN DIRECTION (task-shape for exp_dev; exp_dev owns N/M/K/corpus/metric/bands)
- TASK: does an HD superposed discourse state add value in the AGGREGATE/SIMILARITY/CONSISTENCY mode at OVERLOAD, where a fixed-capacity symbolic store must evict (and thus fails on the evicted-but-relevant) or a discrete store blacks out?
- DIFFICULTY-ON: overload regime (M concurrent bindings pushed toward the D_f/N~0.056 / SNR-near-threshold zone so HD is load-bearing, verified by a pure-symbolic-pointer control being NON-identical this time -- the exact discriminator the VET used to catch v2).
- REAL BASELINES (the VET's tools, mandatory): (a) recency/current-holder oracle; (b) pure-symbolic-pointer control; (c) SYMBOLIC-STORE-WITH-EVICTION (fixed capacity) -- the one HD must beat on the aggregate/similarity query at overload.
- HARD-PASS: HD superposed state beats the symbolic-store-with-eviction on a consistency/aggregate/set-membership query at overload, by a margin, with the pure-symbolic-pointer control NO LONGER identical (proving HD is load-bearing). HARD-FAIL: symbolic-pointer still identical (HD inert again) OR symbolic-store ties/beats HD.
- CAN-FAIL, ONE-VARIABLE. Corpus candidates: ProPara (retrospective state at scale) and/or PDNC-implicit (consistency of speaker-in-conversation) and/or a controlled synthetic-overload passage; exp_dev picks the one that puts HD genuinely at overload.
- RISK: if even at overload the symbolic-store-with-eviction wins (exact + cheap), the HONEST verdict is substrate-native = use a SYMBOLIC state-of-mind, reserve HD for the proven memory/retrieval frontier. That is a legitimate result, not a failure.
