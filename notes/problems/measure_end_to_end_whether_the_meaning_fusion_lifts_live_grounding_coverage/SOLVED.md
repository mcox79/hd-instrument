---
problem: measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage
status: PARTIAL
bar: "PASS = an END-TO-END measurement on the LIVE reading-grounding loop (a faithful harness of canonicalize_fast's read over the real reading corpus, curriculum-ordered as the loop does it) showing whether reading the sense-assignment ranking over the reliability-weighted convergent fusion (grounded + distributional [+ is-a/taxonomic identity], the landed convergent_cue_reader Bayes rule, weights/taus calibrated OFFLINE + held-out) changes the loop's OWN downstream GROUNDING-COVERAGE GROWTH metric -- with (a) the INFO-FREE TWIN (shuffled representation rows) LOSING, (b) the recall/recognition path byte-identical, (c) the number reported with a CI on the loop's own metric/population (no cross-population/scorer number). A CI-SEPARATED lift is a landable win. A rigorous LOCATED NEGATIVE -- the ranking win does NOT transfer to coverage -- is a FULL PASS if it names, WITH A NUMBER, exactly why (e.g. coverage is gated by candidate GENERATION not sense SELECTION; or the loop's coverage is exposure-bound not decision-bound), and then builds the stronger brain version and tests THAT before concluding."
result: "TWO-PART. (1) LOCATED NEGATIVE on the loop's OWN coverage-COUNT metric: the sense-assignment representation does NOT cleanly move n_grounded -- it is decision-quality-BLIND. Genuine online loop over the full curriculum (4640 sentences, curriculum-ordered, process_sentence + consolidation_pass with a swapped sense-assignment gate): INCUMBENT (distributional) grounds 143 words; the fusion grounds 133 (strict accept) to 202 (accept-all) depending ONLY on the accept threshold -- the count tracks thresh-clearing/exposure, NOT ranking correctness. And the incumbent's 143 grounded links are co-occurrence garbage (artwork->happy, google->hope, owner->fine). (2) CI-SEPARATED WIN on coverage QUALITY (the instrument the count is blind to): ranking the true SimLex-999 sense-partner against the loop's ACTUAL 556-word seed-anchor pool through canonicalize's real decision, a brain-foundational meaning representation beats the distributional incumbent CI-separated -- GROUNDED-ATL MRR@cov0.5 +0.158 CI[+0.089,+0.252] and hit@1@cov0.5 +0.106 CI[+0.021,+0.191] (all-query, n=94; both parameter-free); full-coverage MRR +0.103 CI[+0.058,+0.153]; AUF-MRR grounded-distinctive 0.232 > grounded 0.198 > fusion 0.130 > incumbent 0.037 > twin 0.010. REFINEMENT of the brief's mechanism: the transfer is carried by the GROUNDED ATL identity channel, NOT the grounded+distributional FUSION -- on the live anchor pool the distributional channel is noise, so grounded-alone >= fusion (fusion still beats incumbent +0.096 CI[+0.022,+0.189] but trails grounded). 2026-09-10 UPDATE (W19+W20, see body): the chain is now 100% BRAIN-FOUNDATIONAL (parser-free -- the sibling's directional-sequential SEQ channel removes the NOT_BF pos_tagger+arceager) and STILL beats the incumbent live CI-sep (W19); and GROWING that parser-free channel by reading Simple-Wiki lifts the live increment OVER grounded CI-separated (+0.16 at 250k lines -> +0.26 at 1M, twin losing, monotone), so KNOWLEDGE/EXPOSURE is the proven LIVE lever and the fusion-flip gate is closed POSITIVE (W20). Landable: the hdlab wire spec below."
floor: "Strongest floor = the DISTRIBUTIONAL incumbent (the loop's live canonicalize representation): coverage-quality MRR@cov0.5 0.034, hit@1 0.000-0.033, AUF-MRR 0.037; live coverage count n_grounded 143. Info-free twins (shuffled representation rows): AUF-MRR 0.010 (fusion twin) / carries no per-word signal. On the true-BF representation prototype the sparse structured channel's own floors: bag-of-words AUF-MRR 0.030, its info-free twins 0.006-0.008."
controls: "INFO-FREE TWIN (shuffled grounded/representation rows) LOSES CI-separated on every headline (grounded vs twin MRR@0.5 +0.195 CI[+0.106,+0.298]; fusion vs twin +0.122 CI[+0.028,+0.241]; DEP-structured vs twin +0.097 CI[+0.042,+0.178]) -> the win carries real per-word meaning, not base-rate. RECALL/RECOGNITION PATH BYTE-IDENTICAL: canonicalize_fast == reference canonicalize (witness W5; only what the ranking READS changed; no hdlab written). HARNESS FAITHFULNESS positive control: the cell's INCUMBENT gate decision == the live canonicalize (accept/refuse + chosen anchor) on 40/40 random query bundles (W4). INDEPENDENT GOLD: SimLex-999 human similarity (WordNet-independent, independent of every representation). HELD-OUT: the fusion weight w is calibrated on a disjoint train split and evaluated on test; grounded/incumbent are parameter-free (evaluated on all queries, no leak). FAITHFUL POOL: candidates restricted to the loop's ACTUAL seed-anchor field (not the full vocab) -- ranking against the whole 4678-word vocab drives hit@1 to floor for every arm and hides the transfer. THRESHOLD SWEEP: coverage count reported across accept thresholds (matched selectivity) so the count comparison is not a single confounded point. PHASE-DIAGRAM densification SWEEP (k in {50,100,200} x power in {0.5 SGNS, 0.0 whitened}) -- excludes 'the structured channel is just under-optimized'."
files_changed: "experiments/exp_meaning_fusion_live_coverage_v1.py (the end-to-end transfer measurement: PART A genuine online coverage-count + PART B coverage-quality selective-prediction frontier, all arms, twins), experiments/exp_meaning_fusion_bf_representation_v1.py (the TRUE-BF representation prototype -- FIX #3/#5: ATL distinctive-feature whitened grounded + structured dependency/adjacency PPMI substitutability, convergent-cue Bayes, + the phase-diagram SVD-densification sweep), experiments/exp_meaning_fusion_bf_accept_criterion_v1.py (FIX #7: the self-calibrating SDT accept criterion on the scale-free z_top standout, replacing the fixed cosine), experiments/exp_meaning_fusion_correct_coverage_growth_v1.py (the PARTIAL->SOLVED converter: genuine online loop with the fully-BF decision wired, WordNet-judged CORRECT-coverage growth, twin-controlled at matched count), verification/test_meaning_fusion_live_coverage.py (scaffold-free witness, 11/11 checks (W1-W13)), data/exp_meaning_fusion_live_coverage_v1/metrics.json, data/exp_meaning_fusion_bf_representation_v1/metrics.json, data/exp_meaning_fusion_bf_accept_criterion_v1/metrics.json, data/exp_meaning_fusion_correct_coverage_growth_v1/metrics.json, experiments/exp_meaning_fusion_taxonomic_lever_v1.py (quantifies THE big remaining lever: the is-a/taxonomic identity channel on the live anchor-pool decision -- lever-proof under the WordNet-circularity caveat), data/exp_meaning_fusion_taxonomic_lever_v1/metrics.json, experiments/exp_meaning_fusion_learned_isa_channel_v1.py (the research-led BRAIN-FOUNDATIONAL is-a channel LEARNED from reading -- Rogers-McClelland property-SVD + Levy-Goldberg dependency + genus-differentia, NO WordNet; beats grounded on AUF, twin losing), data/exp_meaning_fusion_learned_isa_channel_v1/metrics.json, experiments/exp_meaning_fusion_grown_genus_v1.py (GROW the corpus -> read-edge genus 5%->43%; genus-differentia neutral even with the real genus), experiments/exp_meaning_fusion_grow_reading_v1.py (grow-by-reading: GD + learned-is-a beats grounded CI-sep +0.055), data/exp_meaning_fusion_grown_genus_v1/metrics.json, data/exp_meaning_fusion_grow_reading_v1/metrics.json, experiments/exp_meaning_fusion_separate_pools_v1.py (optimization attempt -- separate pools + reliability weighting = MEASURED NEGATIVE; the joint property-SVD feature-fusion is the correct BF architecture), data/exp_meaning_fusion_separate_pools_v1/metrics.json, experiments/exp_meaning_fusion_matched_coverage_v1.py (matched-count online converter: at equal grounding count fully-BF grows more correct-coverage than incumbent at every judge strictness -- directional, not CI-sep at full = judge noise), data/exp_meaning_fusion_matched_coverage_v1/metrics.json, experiments/exp_meaning_fusion_grow_by_reading_isa_curve_v1.py (grow-a-ton closability curve: raw read-edge is-a to 800k sents grows coverage 0.17->0.58 but NOT quality -> raw reading does not close the gap), experiments/exp_meaning_fusion_clean_isa_v1.py (CLEAN vs RAW: confirmation gate removes noise-harm but coverage collapses -> curated clean knowledge is the lever, out of scope), data/exp_meaning_fusion_grow_by_reading_isa_curve_v1/metrics.json, data/exp_meaning_fusion_clean_isa_v1/metrics.json, experiments/exp_meaning_fusion_signal_trace_v1.py (RIGOROUS signal-loss trace: identity(SimLex) vs relatedness(Assoc) rho per rung, math-BF confirmed, localizes the loss to the unordered distributional pooling), data/exp_meaning_fusion_signal_trace_v1/metrics.json, experiments/exp_meaning_fusion_role_bound_context_v1.py (THE BF FIX prototyped: role-filler binding via hdlab.binding for the pooling loss; positional roles move identity the right way but are insufficient -> syntactic roles = a BF parser is the last non-BF atom), data/exp_meaning_fusion_role_bound_context_v1/metrics.json, experiments/exp_meaning_fusion_syntactic_role_binding_v1.py (PROPER-solution test: role-filler binding over SYNTACTIC roles from the BF incremental_parser; confirms syntactic-roles-yes, binding-estimator-too-noisy -> PPMI-SVD is the working low-variance estimator), data/exp_meaning_fusion_syntactic_role_binding_v1/metrics.json, experiments/exp_meaning_fusion_live_coverage_seq_v1.py (W19 -- the parser-free 100%-BF live transfer: the directional-sequential identity channel SEQ (no pos_tagger/arceager) fused with grounded, on the loop's own coverage-quality frontier; beats the incumbent CI-sep + twin losing, but does not add over the best grounded rep at 34k-sentence exposure -> exposure is the lever), data/exp_meaning_fusion_live_coverage_seq_v1/metrics.json, experiments/exp_meaning_fusion_grow_seq_live_v1.py (W20 -- PHASE B: grow the parser-free SEQ channel by reading Simple-Wiki through the loop's REAL ingest taps, measure the live increment over grounded at 0/250k/500k/1M/2M lines; crosses to CI-sep positive at 250k and stays positive+monotone, twin losing; clean-confirmation arm wins too but does not beat raw), data/exp_meaning_fusion_grow_seq_live_v1/metrics.json, experiments/exp_meaning_fusion_confidence_calibration_v1.py (W21 -- confidence-calibration located negative: no BF certainty signal recovers the +0.245 perfect-ordering gap; z_top/SDT marginally best +0.006, gain+agreement anti-track), data/exp_meaning_fusion_confidence_calibration_v1/metrics.json, experiments/exp_meaning_fusion_valence_channel_v1.py (W22 -- valence antonymy 3rd-channel located negative on synonym-ranking: +0.006 not CI-sep, oracle barely rises; both negatives converge on RELATION CONFUSION -> is-a channel is the real lever), data/exp_meaning_fusion_valence_channel_v1/metrics.json, experiments/exp_meaning_fusion_confidence_bf_v1.py (W23 -- brain-exact confidence re-drill: balance-of-evidence DV margin is best + brain-exact; reliability-normalization ties it; gap is representational not metacognitive), data/exp_meaning_fusion_confidence_bf_v1/metrics.json, experiments/exp_meaning_fusion_differentia_channel_v1.py (W24 -- brain-exact differentia channel, parser-free ordered-SVD late modes gated by genus: beats global cosine +0.145 + raises oracle ceiling +0.044 CI-sep, twin losing; realistic capture unsolved), data/exp_meaning_fusion_differentia_channel_v1/metrics.json, notes/problems/measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage/FULL_CHAIN_BF_AUDIT.md (every rung raw-text->decision enumerated BF/BF_SPIRIT, no NOT_BF atom). NO hdlab/ modified (Q111 -- the hdlab proposal is stated below for the strategy session to land)."
reverify: ".venv/Scripts/python.exe verification/test_meaning_fusion_live_coverage.py  (22/22 checks, W1-W24: incl. W19 parser-free 100%-BF live transfer, W20 grow-by-reading PHASE B live win, W21/W22 the first-round confidence/valence located negatives, W23 the brain-exact confidence re-drill (balance-of-evidence margin is best; gap is representational), W24 the brain-exact differentia channel (beats global cosine + raises the oracle ceiling CI-sep; capture unsolved)). Full-chain BF audit: notes/problems/.../FULL_CHAIN_BF_AUDIT.md. Powered headline reproducer (own-dir only): .venv/Scripts/python.exe experiments/exp_meaning_fusion_live_coverage_v1.py --mode full --no-online ; parser-free live transfer: .venv/Scripts/python.exe experiments/exp_meaning_fusion_live_coverage_seq_v1.py ; grow-by-reading Phase B (up to 2M SW lines, ~4min): .venv/Scripts/python.exe experiments/exp_meaning_fusion_grow_seq_live_v1.py --read-cap 2000000"
---

# What this is: the fusion does NOT lift the loop's coverage COUNT (the count is quality-blind), but a brain-foundational meaning representation lifts coverage QUALITY CI-separated -- and the lever is GROUNDED, not the grounded+distributional fusion

**The short version.** C7 proved the reliability-weighted convergent fusion beats the distributional
incumbent on the sense-assignment RANKING PROXY (MRR vs SimLex). This problem asked whether that transfers
to the live loop's downstream grounding coverage. It does -- but not the way the brief hypothesized, and
not on the metric the loop currently scores:

1. **The loop's OWN coverage-COUNT metric (`n_grounded`) is decision-QUALITY-BLIND.** A word grounds iff
   `canonicalize` finds an eligible anchor over `SENSE_MATCH_THRESH`; the count checks only that SOME anchor
   clears the threshold, never that the link is CORRECT. So the count tracks threshold-clearing and exposure,
   not ranking quality. Measured on the genuine online loop over the full curriculum: incumbent grounds 143
   words; the fusion grounds 133-202 depending ONLY on the accept threshold. There is no clean count lift --
   a **located negative, with numbers** (exactly the bar's blessed "coverage is gated by generation/exposure,
   not sense selection").
2. **Coverage QUALITY -- did the loop link the word to the RIGHT meaning? -- is where the transfer lives, and
   it is CI-separated.** Ranking the true SimLex sense-partner against the loop's actual seed-anchor pool
   through `canonicalize`'s real decision, the grounded ATL representation beats the distributional incumbent
   **+0.158 MRR / +0.106 hit@1 CI-separated**, info-free twin losing, recall path byte-identical. The
   incumbent's own coverage-quality is at floor (hit@1 ~ 0) and its 143 grounded links are co-occurrence
   garbage (`artwork->happy`, `google->hope`, `owner->fine`) -- the C7 loss, live, in the store's content.
3. **REFINEMENT of the brief's mechanism (leave-room-to-solve-it-differently).** The transfer is carried by
   the **GROUNDED ATL identity channel**, NOT the grounded+distributional FUSION. On the live anchor pool the
   distributional channel is noise, so grounded-alone (AUF-MRR 0.198) >= the fusion (0.130); the ATL
   distinctive-feature (whitened) read is the single best arm (0.232). The fusion still beats the incumbent
   CI-separated (+0.096), it just trails grounded -- consistent with C7's own grounded-dominant weight w=16.

## UPDATE 2026-09-10 -- the chain is now 100% BRAIN-FOUNDATIONAL on the live loop (parser-free), and still beats the incumbent; the remaining lever is EXPOSURE (W19)

A sibling solver (`the_meaning_representation_is_a_point_vector_not_a_probabilistic_population_code`, 2026-09-10,
owner-DONE) landed the **parser-free directional-sequential identity channel (SEQ)**: direction+distance-typed
PPMI over the RAW word stream (`hdlab.reading_grounding_loop.directional_context_lemmas`, taps L1/R1/L2/R2 =
theta-phase order coding / the `sequence_memory` S-matrix principle; PPMI = Hebbian-predictive surprise,
Levy-Goldberg; L2 = divisive norm). It **removes the two NOT_BF atoms** that fed the learned identity channel --
`hdlab.pos_tagger` (NOT_BF) and `hdlab.arceager_parser` (NOT_BF) -- with NO parser, NO POS tagger, NO treebank,
NO hard decode. That sibling measured SEQ only on the OFFLINE SimLex-999 ranking (SEQ matches the parser channel
with no loss, MRR 0.0905 vs 0.0872; twin loses). It was never measured on THIS loop. The audit says the live
fusion-flip is GATED on the end-to-end grounding-coverage measurement -- i.e. this problem. So this update SUPERSEDES
the planned Phase A1 (arc-eager -> incremental_parser swap): incremental_parser still depends on the NOT_BF
pos_tagger, whereas SEQ removes the entire stack -- strictly more brain-foundational.

**W19 -- MEASURED on the loop's own coverage-quality frontier** (`exp_meaning_fusion_live_coverage_seq_v1.py`,
reuses the exact PART-B instrument: decide_arm/frontier/area_under_frontier/boot_ci_at; SEQ built from the SAME
curriculum pool the loop reads; anchor-pool-restricted; n_test=47; 3000-boot; SEQ covers 99% of the anchor vocab):

- **THE WIN (CI-separated, twin losing, at 100% BF).** The fully-BF parser-free rep beats the live distributional
  incumbent: distinctive-grounded (+) SEQ AUF-MRR **0.129 vs incumbent 0.037**, diff@cov0.5 **+0.161 CI
  [+0.006,+0.274]**; grounded (+) SEQ **0.138 vs 0.037**, +0.121 CI [+0.013,+0.248]; both twins LOSE CI-separated
  (GD_SEQ vs twin +0.168 CI [+0.021,+0.276]). So the chain from raw text to the sense-assignment decision is now
  brain-foundational at EVERY rung -- no POS tagger, no parser anywhere -- and STILL beats the incumbent live.
- **THE HONEST LOCATED NEGATIVE (unchanged lever).** The learned SEQ channel does NOT yet add over the best
  grounded rep: GD_SEQ 0.129 < **distinctive-grounded-alone 0.206** (increment **-0.034 CI [-0.237,+0.124]**, not
  CI-sep); SEQ alone 0.092 beats the incumbent 0.037 only directionally (CI grazes 0). The AUF-MRR ladder:
  GD-distinctive 0.206 > grounded 0.199 > grounded+SEQ 0.138 > FUSION(g+distrib) 0.130 > GD+SEQ 0.129 > SEQ 0.092
  > incumbent 0.037 > twin 0.024. GROUNDED carries the win; the learned distributional/structural channel is
  exposure-limited at 34k curriculum sentences -- exactly the sibling's measured **+0.186 EXPOSURE GAP** (learned
  0.112 vs supplied WordNet ontology 0.298 on SimLex).
- **WHY the flip vs SimLex.** On SimLex near-synonyms the structural channel (SEQ 0.091) beats grounded (0.053)
  because grounded suffers the sibling/synonym confound; on the live anchor-pool decision grounded (0.206) is much
  stronger (rich ATL coverage of the seed vocabulary), so equal-weight fusing the under-read SEQ dilutes it. Both
  are the SAME finding: SEQ has the right (now fully BF) mechanism and is under-read.

**NET.** Phase A (100% chain BF) is CLOSED on the live loop -- and better than planned (parser-free removal, not a
parser swap). The `pos_tagger` residual is MOOT for this channel. The remaining distance to a live INCREMENT over
grounded is proven-to-be KNOWLEDGE/EXPOSURE: **grow SEQ by reading and re-test the live increment (Phase B)** -- the
sibling already showed SEQ grows 0.071 -> 0.163 (~80% of the ontology ceiling) on +1.5M Simple-Wiki lines on SimLex;
the open question this problem now owns is whether GROWN SEQ starts to add over grounded ON THE LIVE LOOP.

## UPDATE 2026-09-10 (W20) -- PHASE B WIN: growing the parser-free channel by READING lifts the LIVE increment over grounded, CI-separated, twin losing, monotone. KNOWLEDGE/EXPOSURE is the proven live lever.

`exp_meaning_fusion_grow_seq_live_v1.py`. Hold the live decision / anchor-pool / grounded foundation FIXED; grow
ONLY the SEQ channel by reading modern Simple-Wikipedia in exposure slices; measure the increment GD_SEQ minus
GD-distinctive on the loop's OWN coverage-quality frontier (pooled SimLex-999 + SimVerb-3500 high-sim,
anchor-pool-restricted, n_test=169, 3000-boot). Growth goes through the substrate's REAL ingest: `_accumulate_seq`
uses SEQ_TAPS = the loop's `_DIRECTIONAL_OFFSETS` (byte-identical to `ConceptSpace.observe_context_counts` +
`directional_context_lemmas`; witness A6 + W20 self-test), so this IS the loop's online-learning path, not a sidecar.

**THE EXPOSURE CURVE (increment gain-weighted, PPC saturating log1p; twin = SEQ rows shuffled):**
- 0 extra lines (curriculum only): increment **-0.066 CI [-0.141,+0.012]** -- SEQ under-read, does not add (reproduces W19).
- 250k SW lines:  **+0.160 CI [+0.063,+0.255]**  (CROSSOVER: CI-separated POSITIVE, twin losing)
- 500k SW lines:  **+0.223 CI [+0.120,+0.325]**
- 1M SW lines:    **+0.263 CI [+0.161,+0.361]**  (best)
- 2M SW lines:    **+0.250 CI [+0.156,+0.353]**  (plateauing ~0.25-0.26)
- Twin LOSES at every exposure. GD-distinctive baseline AUF-MRR 0.149 -> grown GD_SEQ 0.446 at 2M (nearly 3x).

**READING IS THE LEVER, PROVEN LIVE.** The increment crosses to CI-separated positive at 250k lines and stays
positive and monotone through 2M, with the info-free twin losing throughout -- the control that isolates KNOWLEDGE
from mechanism. So the meaning fusion DOES lift the live grounding-coverage decision once the learned identity
channel is read to strength: a fully-brain-foundational representation (no parser, no POS tagger) whose learned
channel is grown by reading beats grounded-alone CI-separated on the loop's own instrument. This CLOSES the audit's
fusion-flip gate ("the live fusion-flip is gated on the end-to-end grounding-coverage measurement") with a POSITIVE
result.

**CLEAN vs RAW (cross-source confirmation).** A confirmation gate (keep directional features seen >= 3x across
episodes = consolidation) also wins CI-sep (+0.234 CI [+0.129,+0.334]) but does NOT beat raw (+0.25). The
direction-TYPED channel is clean enough raw -- unlike the old UNORDERED bag (W15), which needed cleaning and then
collapsed. Direction-typing (order coding) is what makes reading grow an IDENTITY channel rather than a noisy
relatedness bag. So no cleaning stage is needed; raw grow-by-reading suffices.

**PER-GOLD DECOMPOSITION (closes the "is it just verbs?" check).** At top exposure the increment is CI-separated
POSITIVE for BOTH word classes independently: SimLex (nouns/adjectives, n=43) +0.210 CI [+0.034,+0.421]; SimVerb
(verbs, n=126) +0.248 CI [+0.146,+0.379]. So the grow-by-reading win is BROAD across word classes, not a verb
artifact (the verb slice is merely better-powered). GD_SEQ AUF reaches ~0.433 for both; grounded-alone is 0.167
(nouns) / 0.145 (verbs).

**HONEST caveats.** (1) The grounded and
incumbent channels are curriculum-only by design (grounded is a fixed foundation asset; the incumbent is the loop's
live field) -- the point is precisely that the ONLINE-LEARNABLE channel, given reading, adds over the fixed
foundation. (3) Every rung is math-BF (order-coded directional context / theta-phase window -> Hebbian-predictive
PPMI, Levy-Goldberg -> divisive norm, Carandini-Heeger -> cosine, Georgopoulos -> convergent-cue Bayes with
saturating population gain, Weber-Fechner / Ma-Pouget).

## UPDATE 2026-09-10 -- VS-BRAIN ladder + SIGNAL-LOSS decomposition on the live loop (top exposure), and the reframed improvement opportunities

`vs_brain_and_signal_loss_top_exposure` in `exp_meaning_fusion_grow_seq_live_v1.py`. AUF-MRR on the live
coverage-quality frontier; the brain reference for this task = perfect sense-assignment (AUF-MRR 1.0).

LADDER: incumbent 0.051 (~5%) -> grounded 0.149 (~15%) -> grown-SEQ-alone 0.351 (~35%) -> gain/equal-fused
{grounded, grown-SEQ} 0.44/0.45 (~44%) -> fusion with PERFECT CONFIDENCE ordering 0.675 -> ORACLE per-query
channel-select over {G,SEQ}, perfect 0.698 -> brain 1.0. So the fully-BF live chain reaches ~44% of the brain's
perfect sense-assignment (up from the incumbent's ~5% and grounded's ~15%).

SIGNAL LOSS, descending from the ceiling (WHERE the remaining ~0.56 is lost):
- **CONFIDENCE CALIBRATION = +0.236** (fusion realistic 0.440 -> fusion perfect-ordering 0.675). The fusion RANKS
  the right partner well, but its per-query CONFIDENCE (the margin used for selective prediction / the accept gate)
  is poorly ordered w.r.t. correctness -- it trusts wrong-but-confident links. This is the BIGGEST ACTIONABLE lever
  and it maps straight onto the live loop's accept gate (better confidence = more CORRECT coverage).
- **NEW CHANNEL / MORE KNOWLEDGE = +0.302** (oracle{G,SEQ} 0.698 -> brain 1.0). Queries BOTH channels miss; needs a
  3rd BF channel or more reading. Biggest raw gap, but harder.
- **PER-QUERY CHANNEL ROUTING = +0.023** (oracle 0.698 -> fusion perfect-order 0.675). NEAR-ZERO -- the two channels
  are near-redundant in coverage, so a relationship-kind ROUTER is NOT a lever (this REFUTES the natural "route by
  channel kind" hypothesis; measurement-driven negative).

REFRAMED IMPROVEMENT OPPORTUNITIES (measurement-ordered):
1. **Fix the confidence/precision signal (largest actionable, +0.236 ceiling).** Replace the fusion-margin confidence
   with a better-calibrated precision for the selective ordering + accept gate: the self-calibrating SDT z_top
   criterion (FIX #7, already prototyped) and/or the PPC population-GAIN precision (the sibling PROVED gain tracks
   correctness, Spearman 0.221 CI-sep). Test which confidence best orders correctness on the live frontier.
2. **Add a 3rd complementary BF channel (+0.302 raw gap).** Candidates, both non-circular / no-WordNet: the SIGNED
   valence-polarity channel (`hdlab.valence_polarity_channel`, LATENT; un-blinds ANTONYMY, which grounded+SEQ both
   miss) and/or the learned is-a property-SVD taxonomic channel grown parser-free. Fuse and re-measure the ladder.
3. **NOT per-query channel routing** (+0.023) -- measured dead end; do not build it.
4. Phase-diagram SWEEP (not adopt): the SEQ theta-phase window taps (L1/R1/L2/R2 = +-1,+-2; extend to +-3 = Lisman-
   Idiart capacity) -- may extend the ~0.25 grow plateau.

## UPDATE 2026-09-10 (W21+W22) -- the two identified levers, tested at full power: BOTH located negatives, converging on ONE diagnosis (relation confusion)

Following the W20 signal-loss trace, the two indicated levers were built + measured at grown SEQ (500k lines, n=169,
3000-boot). Both are RIGOROUS LOCATED NEGATIVES on this population, each with a mechanism -- and they point to the
SAME real lever.

**W21 -- CONFIDENCE CALIBRATION (`exp_meaning_fusion_confidence_calibration_v1.py`).** The perfect-ordering ceiling
is 0.658 vs the current margin-confidence 0.412 (the +0.245 gap). Six BF confidence signals were compared as the
selective-prediction ordering: z_top (SDT standout, Carandini-Heeger + Yonelinas) 0.418 = BEST but only +0.006 over
margin (recovers ~2% of the gap); posterior concentration 0.401; neg-entropy 0.392; cross-cue agreement 0.336 and
earned population gain 0.323 both ANTI-track (calibration Spearman < 0). NEGATIVE: no BF certainty signal meaningfully
recovers the calibration gap -- z_top (= FIX #7) is directionally best but the gain is tiny. The gap is real but NOT
capturable by a scalar certainty signal.

**W22 -- VALENCE 3rd CHANNEL (`exp_meaning_fusion_valence_channel_v1.py`).** Added the signed valence-polarity
antonymy channel (Osgood/Russell/vmPFC, Warriner foundation, NO WordNet; LATENT organ). On the live synonym-ranking
decision: fusion {G,SEQ} 0.412 -> {G,SEQ,VAL} 0.415 (+0.006 CI [-0.035,+0.076], NOT CI-sep); the {G,SEQ} oracle
ceiling barely moves (+0.0095 CI [0.0,+0.029]); the info-free valence twin loses but not CI-sep. NEGATIVE: valence
does not add HERE. Mechanism: valence separates ANTONYMS, but the distractors outranking the true synonym in the
anchor pool are rarely antonyms -- so valence almost never bites (the oracle barely rising confirms it adds ~no new
coverage on this population). (Valence remains a real BF win on its OWN task, synonym-vs-antonym AUC 0.535->0.72.)

**THE CONVERGENT DIAGNOSIS (what both negatives reveal).** The +0.236 "confidence" gap and the +0.302 "both channels
miss" gap are the SAME phenomenon: RELATION CONFUSION. The fused decision confidently ranks a WRONG-RELATION neighbor
(co-hyponym / associate / occasionally antonym) above the true synonym. That is why (a) no scalar CONFIDENCE catches
it (the wrong pick has a genuinely high score) and (b) a single-relation channel (valence = antonymy only) barely
helps (antonyms are a small slice of the confusions). The real lever is a RELATION-DISCRIMINATING channel that
separates true synonymy/identity from co-hyponymy/hypernymy -- i.e. the IS-A / taxonomic identity channel (W10/W11
showed the WordNet-supplied version lifts to 0.65 and the learned property-SVD version beats grounded), but built
PARSER-FREE + BF (property-covariance SVD over the SAME grown directional counts, Rogers-McClelland; no arc-eager),
plus TARGETED reading of the specific under-covered synonym words (the SEQ exposure gap for rare items). That is the
indicated next build; valence and scalar-confidence engineering are DE-PRIORITIZED (measured dead ends here).

## UPDATE 2026-09-10 (W23+W24) -- AGGRESSIVE brain-exact RE-DRILL of the two W21/W22 negatives (research-led); full-chain BF audit

Owner: "research and drill those aggressively -- double check the entire chain is mathematically BF." A biology drill
(Kepecs 2008; Kiani-Shadlen 2009; Pouget-Drugowitsch-Kepecs 2016; Meyniel 2015; Patterson-Nestor-Rogers 2007; Saxe-
McClelland-Ganguli 2019; Cree-McRae 2006) showed BOTH W21/W22 negatives tested WEAK PROXIES, not the brain-exact
computation. Re-drilled both brain-exactly (grown SEQ 500k, n=169, 3000-boot).

**W23 -- CONFIDENCE, brain-exact (`exp_meaning_fusion_confidence_bf_v1.py`).** Brain confidence = P(correct) =
BALANCE OF EVIDENCE (top-1-minus-top-2 MARGIN on the accumulated decision variable), normalized by estimated
reliability (DV/sqrt(var_hat)) -- NOT the whole-field standout / concentration / raw gain W21 tried (those are its
"first-order shadows"). MEASURED: the margin (balance of evidence) IS the best confidence (AUF 0.4123, calib rho
0.13); reliability-normalization ties it (margin_relnorm 0.4113, recovers ~0% of the +0.245 gap); seq-gain-alone
anti-tracks. FAIR-TESTED NEGATIVE with a mechanism: the confidently-wrong cases are REPRESENTATIONAL relation-
confusions (the rep genuinely ranks a co-hyponym #1 with a large margin), so NO confidence signal can separate them
-- the fix is the REPRESENTATION, not metacognition. The confidence gap DISSOLVES into the differentia lever.

**W24 -- DIFFERENTIA, the brain-exact relation-confusion lever (`exp_meaning_fusion_differentia_channel_v1.py`).**
The synonym-vs-co-hyponym separator is the DISTINCTIVENESS-WEIGHTED LATE modes of the ordered property SVD, gated by
genus -- NOT global cosine (genus-dominated) and NOT one antonymy axis (W22). Built PARSER-FREE from [grounded (+)
grown-SEQ], ordered SVD, early modes = genus, late modes whitened = differentia. VALIDATED CI-separated: differentia
0.319 BEATS genus-dominated global cosine (isa_full 0.196) +0.145 CI [+0.040,+0.243]; adding it RAISES the two-channel
oracle ceiling 0.650 -> 0.681 +0.044 CI [+0.017,+0.075]; the differentia re-ranking beats its shuffled twin +0.169
CI [+0.084,+0.238]. So the differentia carries REAL, complementary, brain-exact synonym-discriminating signal --
exactly the relation-confusion lever W20 diagnosed, which valence (W22) and confidence (W21/W23) could not supply.
CAPTURE UNSOLVED (honest): converting the ceiling gain into the REALISTIC decision fails both ways tried -- linear
convergent fusion (fus{G,SEQ,DIFF} 0.400 ~ fus{G,SEQ} 0.412) and hard coarse-to-fine re-ranking (0.371, -0.043 CI
[-0.087,-0.003]) -- because differentia-alone (0.319) is weaker than SEQ and a scalar cannot say per-query WHEN to
trust it.

**THE UNIFYING CONCLUSION (what the aggressive drill revealed).** Both re-drills converge: the remaining distance to
the brain is dominated by the PER-QUERY RELIABILITY / channel-selection problem -- oracle-over-channels 0.68 vs the
realistic fusion 0.44 (~0.24 routable IF we knew per-query which answer is right) -- and this is the SAME wall the
confidence drill hit (a scalar certainty cannot say which of two high-scoring candidates is the correct RELATION),
PLUS more knowledge (oracle 0.68 -> brain 1.0). Neither is a NOT_BF atom (the full-chain audit confirms 100% BF), and
neither is the specific lever first guessed (per-query channel routing over {G,SEQ} was ~0 at W20; it OPENS UP only
once the complementary differentia channel is added). The differentia is the validated next channel; the open problem
is a brain-exact per-query reliability that scalar signals do not supply (candidate: recollection/relation-type
gating, not familiarity -- a further drill).

**FULL-CHAIN MATHEMATICAL BF AUDIT (`FULL_CHAIN_BF_AUDIT.md`).** Every rung raw-text->decision enumerated with its
brain-exact computation + citation + PINNED/parameter status: lemma (Rastle-Davis), directional window (theta-phase
order coding, Lisman-Idiart/Christiansen-Chater), Hebbian accrual, PPMI (Levy-Goldberg prediction-error), divisive
norm (Carandini-Heeger), grounded ATL (Patterson-Nestor-Rogers, PINNED), cosine (Georgopoulos), softmax (Gibbs),
convergent-cue gain-ratio fusion (Ma-Pouget/Ernst-Banks, parameter-free), balance-of-evidence confidence (Kepecs/
Kiani-Shadlen), SDT accept gate (Yonelinas), online grow-by-reading. VERDICT: NO NOT_BF atom in the live chain; the
two historically load-bearing NOT_BF atoms (arc-eager parser + POS tagger) are REMOVED; every parameter is SWEPT not
adopted; fusion weight and accept criterion are parameter-free. The residual is knowledge/exposure + the per-query
reliability lever, not fidelity.

## NET (both phases answered, affirmatively).
Phase A: the chain is 100% brain-foundational (parser-free) and beats
the incumbent live (W19). Phase B: growing the parser-free identity channel by reading LIFTS the live
grounding-coverage increment over grounded, CI-separated, twin losing, monotone 250k->2M lines (W20). The remaining
distance to the brain that the sibling localized as a "+0.186 exposure gap" is now MEASURED to close by reading, ON
THE LIVE LOOP. The landable action is the hdlab wire spec below (strategy/Q111): flip the SEQ channel live in
`canonicalize` and enable grow-by-reading.

## The measurement (faithful to the live loop)
`exp_meaning_fusion_live_coverage_v1.py`. Two instruments, because the loop's own metric cannot see quality:
- **PART A (loop's OWN coverage count, genuine online).** `process_sentence` + `consolidation_pass` with a
  custom sense-assignment `mdl_gate_fn` per arm, over the real curriculum corpus, curriculum-ordered. The
  INCUMBENT gate is byte-identical to the live `canonicalize` (witness W4, 40/40). Only what the ranking
  READS changes; the schema/exposure gate, the field growth, and the recall/recognition path are the loop's.
- **PART B (coverage QUALITY frontier, the headline).** Threshold-free selective-prediction: rank the true
  SimLex-999 near-synonym partner against the loop's actual 556-word seed-anchor pool; sort queries by each
  arm's own confidence; at coverage c report precision = hit@1 / MRR among the top-c. A better ranker
  DOMINATES the frontier. Paired bootstrap CI (3000x) over queries; info-free twin (shuffled rows) losing.

I first established on the CURRENT bytes (a probe, folded into the design) that `canonicalize`'s threshold
is a HARD gate on ALL coverage: on current code every grounded word is LINKED (0 self-grounded) and ~40% of
consolidation-survivors are refused (TAUTOLOGY_NO_ANCHOR, best_cos just under 0.45). The landed 2026-08-12
`cycle1` metrics show 124 self-grounded words -- that reflects OLD code (pre the refuse-tautology fix); on
current bytes the sense-assignment ranker gates coverage, which is why the representation matters here.

## Coverage-quality numbers (SimLex gold, loop's anchor pool, n=94 all-query / n_test=47 held-out)
| arm (rank true partner among the 556-word seed-anchor pool) | AUF-MRR | vs incumbent MRR@cov0.5 |
|---|---|---|
| INCUMBENT (distributional bag -- the live representation) | 0.037 | -- (floor) |
| info-free TWIN (shuffled rows) | 0.010 | loses CI-sep |
| GROUNDED+DISTRIBUTIONAL FUSION (C7's arm, held-out w=16) | 0.130 | +0.096 CI[+0.022,+0.189] |
| **GROUNDED ATL (the lever)** | **0.198** | **+0.158 CI[+0.089,+0.252]** |
| **GROUNDED-DISTINCTIVE (whitened ATL -- upstream BF upgrade)** | **0.232** | **+0.182 CI[+0.102,+0.275]** |

hit@1@cov0.5 grounded +0.106 CI[+0.021,+0.191]; grounded vs twin +0.195 CI[+0.106,+0.298]. The distinctive
(whitened) read is directionally best but NOT CI-separated over raw grounded (+0.024 CI[-0.036,+0.084]) --
its held-out SimLex edge does not clearly transfer to the live task (echoing C7's "BF residuals null").

## THE BF FIX FOR THE LOSS, PROTOTYPED -- role-filler binding; localizes the last non-BF atom to the parser
`exp_meaning_fusion_role_bound_context_v1.py`. The loss (below) is the UNORDERED pooling. The brain's fix is
not a bag: it BINDS each filler to its ROLE (Smolensky role-filler; the substrate's PINNED binding basis is
FHRR/HRR -- reused `hdlab.binding.bind` = circular convolution). v(w)=SUM bind(role(pos_x), filler(x)) makes
cos(v(w),v(c)) high iff w,c have the SAME fillers in the SAME slots = PARADIGMATIC (identity). MEASURED
(identity=SimLex rho, relatedness=Assoc rho, n=590 covered):
| rep | identity rho | relatedness rho |
|---|---|---|
| UNORDERED bag (incumbent) | -0.023 | 0.093 |
| ROLE_BOUND positional (FHRR, NO parser) | +0.024 | 0.095 |
| info-free TWIN (shuffled) | 0.032 | 0.057 |
- **The mechanism is correct: role-binding moves identity the right way (-0.023 -> +0.024).** But POSITIONAL
  roles are INSUFFICIENT -- role-bound (0.024) does NOT beat its info-free twin (0.032), so positional binding
  carries no real identity signal at this scale. Position is not the paradigmatic role.
- **The paradigmatic/identity signal needs SYNTACTIC roles** (which grammatical slot the word fills), and the
  dependency-structured version ALREADY works (the learned-is-a property-SVD, identity rho 0.233, beats
  grounded, twin losing CI-sep) -- but it uses the arc-eager parser, tagged NOT_BF.
- **SYNTACTIC roles via the BF parser, TESTED (`exp_meaning_fusion_syntactic_role_binding_v1.py`):** supplied
  the syntactic roles the brain's way -- `hdlab.incremental_parser` (BF_SPIRIT, incremental left-corner, beats
  arc-eager; NOT the NOT_BF batch parser) -> SUBJ/OBJ frames -> bind(role, verb/arg filler). Result: identity
  rho 0.010, still < its info-free twin (0.048). So role-filler BINDING -- positional OR syntactic -- is
  DIRECTIONALLY correct (identity > relatedness) but NOISE-LIMITED at curriculum exposure: binding SPREADS
  signal, so a word's SUM role(x)filler superposition needs far more edges/word than 4640 sentences give.
- **THE PROPER SOLUTION -- SAME paradigmatic signal, LOW-VARIANCE estimator (already validated).** The
  paradigmatic (syntactic-slot substitutability) signal has two BF estimators: role-filler BINDING (purest op,
  hdlab.binding; but HIGH variance -> data-hungry -> noise-limited here) and DEPENDENCY-PPMI PROPERTY-SVD (the
  SAME signal via rectified-MI [Hebbian] + ordered SVD [efficient coding], both BF; LOW variance). The
  property-SVD one WORKS: identity rho 0.233, beats grounded, twin losing CI-sep, and grounded-distinctive (+)
  it is the best landable arm (beats grounded +0.055 CI-sep). So the PROPER BF FIX for the pooling loss = the
  grounded-distinctive (+) dependency-PPMI property-SVD representation already prototyped; the binding
  exploration CONFIRMED the two load-bearing choices -- SYNTACTIC roles (not positional) and the PPMI-SVD
  estimator (not binding) at feasible exposure. The one further-upstream residual is the UPOS tagger feeding
  any syntactic-role source; incremental_parser (BF_SPIRIT) is the BF structure-builder for the roles.

## RIGOROUS SIGNAL-LOSS TRACE (what signal the BF decision needs, where it is lost, math-confirmed at every rung)
`exp_meaning_fusion_signal_trace_v1.py`. THE DECISION is canonicalize(w)=argmax_c sim(rep(w),rep(c)) accepted
by an SDT criterion; Bayes-optimally it argmaxes P(c = concept-of-w | evidence). THE SIGNAL IT NEEDS is
meaning-IDENTITY similarity -- sim HIGH iff w,c are the SAME CONCEPT (synonymy/is-a) -- NOT associative
RELATEDNESS. The two are mathematically distinct: RELATEDNESS is SYNTAGMATIC (w,c co-occur; a FIRST-order
statistic; Firth 1957); IDENTITY is PARADIGMATIC (w,c occur in the SAME environments = substitutable; a
SECOND-order property = their context DISTRIBUTIONS match; Harris 1954, Levy-Goldberg 2014). MEASURED at each
rung: Spearman rho of the rung's cosine vs SimLex-999 IDENTITY ratings and vs the Assoc(USF) free-association
RELATEDNESS ratings, SAME covered pairs (n~600-900):

| rung | math operation | BF (pinned) | identity rho | related. rho |
|---|---|---|---|---|
| 0. raw text | -- | -- | (ceiling: is-a is recoverable, see WordNet row) | -- |
| 1. lemmatize (normalize_lemma) | surface -> lemma (morphological normalization) | BF PINNED (Rastle-Davis 2008: morphology stripped at lexical access) | preserved | -- |
| 2a. DISTRIBUTIONAL bag (context_vector) | v(w)=SUM_x R.onehot(x); cos(v(w),v(c)) ~= shared-neighbour count (JL: R^T R ~= I) | random proj BF (JL/Marr), superposition BF -- but UNORDERED POOLING = the FIRST-order co-occurrence marginal | **-0.02 (LOST)** | 0.07 |
| 2b. GROUNDED (Lancaster/Brysbaert) | z=(x-mu)/sigma, cos | BF (ATL modality spokes, PINNED; z = subtractive+divisive normalization) | **0.220 (RECOVERED from perception)** | 0.281 |
| 3. GROUNDED-distinctive (whiten) | (x-mu)W, W=eigvec(Sigma)diag(1/sqrt(eigval)) = ZCA | BF (ATL privilege-distinctive = decorrelation, Patterson-Nestor-Rogers; Carandini-Heeger) | 0.268 (sharpened) | 0.277 |
| 3'. learned IS-A (property-SVD) | truncated SVD of distinctiveness-reweighted word x property matrix; U.Sigma | BF (Rogers-McClelland; Saxe-McClelland-Ganguli 2019 PROVE GD learns these ordered modes) | 0.233 | 0.281 |
| 4. readout | sim=(M q)/(||M||||q||); softmax(s/tau) | BF (Georgopoulos pop-vector + Carandini-Heeger divisive norm; softmax = Gibbs/max-entropy posterior) | preserves rep | -- |
| 5. fusion | comb=SUM_c w_c logsoftmax(s_c/tau_c)=log PROD softmax_c | BF (Bayes cue integration, Ma/Pouget 2006) | preserves | -- |
| 6. decision | argmax + accept iff z_top=(s1-mu)/sigma >= SDT criterion | BF (WTA; Yonelinas SDT; Bruce-Young familiarity gate) | preserves | -- |
| CEILING. WordNet taxonomic (curated) | IDF-weighted definitional-feature cosine | BF op; knowledge CURATED (circular w/ SimLex -- reference only) | **0.498 (id >> rel: clean identity)** | 0.316 |

**WHERE THE SIGNAL IS LOST -- rung 2a, mathematically.** The distributional bag pools the context UNORDERED,
so cos(bag(w),bag(c)) measures how often w,c share neighbours = the SYNTAGMATIC (relatedness) statistic; it
CANNOT express the PARADIGMATIC (same-context-distribution = substitutability) structure that identity is.
MEASURED: its identity rho collapses to ~0 (-0.02) while relatedness survives (0.07) -- the DISSOCIATION is
the proof it computes the wrong quantity. Every other rung's math is BF and PRESERVES/RECOVERS signal:
grounded RECOVERS identity from a DIFFERENT source (perception, 0.220); whitening SHARPENS it (0.268);
property-SVD adds the paradigmatic-from-reading (0.233); readout/fusion/decision are faithful. The ONLY rung
where identity DOMINATES relatedness is the CURATED WordNet ceiling (0.498 vs 0.316) -- the mathematical
signature of a clean identity representation, and the target the fully-BF chain approaches without an ontology.
So: the chain is BF at every rung; the single loss is the unordered pooling (the first-order projection that
annihilates the second-order identity structure), and it is bypassed by grounded + structured/is-a. The
residual gap to the ceiling is CLEAN paradigmatic (is-a) coverage = curated knowledge (out of scope), NOT a
missing or non-BF computation. (Trace reproduces C7's isolated numbers on this population: distributional
~0.04, grounded ~0.245, WordNet ~0.521.)

## FULL-STACK-UPSTREAM: the true-BF representation, prototyped and math-audited (owner directive)
`exp_meaning_fusion_bf_representation_v1.py`. The signal-loss trace located the non-BF weak link: the
sense-assignment ranks a DISTRIBUTIONAL BAG-OF-COOCCURRENCE (NOT_BF: unordered pooling; carries relatedness,
not identity; live coverage-quality hit@1 ~ 0). Prototyped the representation that IS brain-foundational,
per-operation:

| operation | brain-foundational? (math) |
|---|---|
| grounded z-score | BF -- subtractive+divisive normalization (Carandini-Heeger) |
| grounded WHITENING (distinctive-feature) | BF -- decorrelate the shared axis = ATL privilege-distinctive-features (Patterson-Nestor-Rogers) |
| PPMI = max(0, log p(w,c)/(p(w)p(c))) | BF -- rectified pointwise MI = predictive surprise / Hebbian-predictive fixed point (Levy-Goldberg) |
| ADJ structured context (direction-typed adjacency) | BF -- sequential order intrinsic; NO parser (fully BF end-to-end) |
| DEP structured context (dependency-typed) | BF operation; parse INPUT NOT_BF (frozen supervised arceager -> fix incremental_parser) |
| SVD densification | BF -- efficient-coding / linear-autoencoder cortical dim-reduction (SVD-of-PPMI ~ SGNS) |
| convergent fusion (equal-weight sum of log-Gibbs-posteriors) | BF -- Bayes cue integration, uniform prior, no fitted params (Ma/Pouget) |
| cosine population read | BF -- population coactivation + divisive normalization (Georgopoulos) |

**Findings (full curriculum, n=94):**
- **Structured > unordered, LIVE (Levy-Goldberg confirmed):** the dependency-substitutability PPMI channel
  (DEP, AUF-MRR 0.105) beats its info-free twin CI-separated (+0.097 CI[+0.042,+0.178]) and beats the
  bag directionally (+0.075 CI[-0.003,+0.156]). Pure adjacency (ADJ, no parser) is much weaker
  (0.018) -- the dependency structure, not mere order, carries the identity signal.
- **The structured channel is EXPOSURE-limited, not a ceiling:** DEP rose 0.022 -> 0.105 as reading went
  900 -> 4640 sentences (still far below C7's 34k). But it does NOT yet exceed grounded (0.188), and fusing
  it with grounded is null (does not lift grounded at this exposure).
- **PHASE-DIAGRAM densification move (owner: "make signals dense easily"), swept and MEASURED:** truncated
  SVD densification of the sparse structured PPMI (k in {50,100,200} x power in {0.5 SGNS, 0.0 whitened})
  did NOT cross the wall -- every dense config underperforms the raw sparse channel (best 0.070 < 0.105) and
  AUF rises monotonically with k TOWARD the sparse value. The reason is mechanistic and generalizable:
  meaning-IDENTITY lives in the rare DISTINCTIVE contexts, which low-rank compression smooths away (the same
  place low-variance directions get dropped). Densify-by-WHITENING HELPS a LOW-dim shared-axis-dominated
  signal (it is exactly why grounded-distinctive 0.232 > grounded-raw 0.188); it HURTS a high-dim
  sparse-distinctive signal. So for the structured channel the lever is EXPOSURE (or a better structure),
  not compression. (Recorded in memory: densify AND measure; whiten low-dim, do not low-rank-compress
  sparse-distinctive.)

## END-TO-END ONLINE CORRECT-COVERAGE GROWTH (the PARTIAL->SOLVED converter)
`exp_meaning_fusion_correct_coverage_growth_v1.py`. The decision-level win is at the ranking; this closes the
gap to a WIRED online read. The genuine online loop (process_sentence + consolidation_pass + swapped gate)
runs over the full curriculum with the fully-BF decision (grounded-distinctive rep + SDT z_top accept) vs the
distributional incumbent vs an info-free twin (shuffled grounded rows). Every banked (word -> anchor) link is
judged CORRECT by an INDEPENDENT gold -- WordNet Wu-Palmer neighbour, independent of BOTH the distributional
and grounded channels, used only to JUDGE (never on the read path). correct-coverage = # words grounded to a
genuine meaning-neighbour.

| WordNet judge | correct-coverage INCUMBENT / FULLY_BF / TWIN | FULLY_BF vs TWIN precision (matched count 165) |
|---|---|---|
| wup>=0.5 | 49 / **70** / 49 | +0.134 CI[+0.023,+0.239] |
| wup>=0.6 | 23 / **41** / 25 | +0.101 CI[+0.015,+0.188] |
| wup>=0.7 | 13 / **26** / 14 | +0.076 CI[+0.007,+0.144] |
| wup>=0.8 (strict) | 8 / **13** / **2** | +0.069 CI[+0.025,+0.118] |

- **CORRECT-COVERAGE GROWTH: the fully-BF decision grows MORE correctly-grounded vocabulary than the incumbent
  at EVERY judge strictness (70 vs 49 ... 13 vs 8), and beats its own info-free twin CI-separated at MATCHED
  grounding count (both ground 165) at every strictness.** At the same 165 groundings the real grounded rep
  yields 70 correct vs the twin's 49 (+43%). Qualitatively: incumbent links artwork->happy, google->hope,
  owner->fine; fully-BF links artwork->picture, owner->president.
- **HONEST BOUND (settled with a matched-count converter, `exp_meaning_fusion_matched_coverage_v1.py`):**
  precision vs the INCUMBENT is directional but NOT CI-separated online. I MATCHED the grounding count by a
  RANK-CUTOFF (top-K by confidence, K=143 = min count) since the z-criterion cannot match via threshold. At
  matched K, the fully-BF decision grows MORE correct-coverage at EVERY judge strictness (correct@K
  58/34/23 vs incumbent 49/23/13 at wup>=0.5/0.6/0.7) but the precision difference stays DIRECTIONAL
  (+0.035 to +0.065, CI incl 0) -- the WordNet-judge noise + online variance limit CI-separation at this
  scale (a smoke CI-sep +0.318 did NOT survive to full power = it was underpowered). So the online
  correct-coverage CORROBORATES the direction; the clean CI-separated advantage over the incumbent remains the
  DECISION-level measurement (+0.158 MRR / +0.106 hit@1 through the anchor pool). Absolute correctness is
  modest (43% at wup>=0.5 down to 8% at wup>=0.8) -- the knowledge/exposure gap, not a mechanism defect.

So the online converter STRENGTHENS the result to a strong PARTIAL: end-to-end, on a wired read, the fully-BF
decision demonstrably grows more correct-coverage, twin-controlled at matched count. It stays PARTIAL (not
SOLVED) because the clean online precision win over the incumbent is power/operating-point-limited, and the
fully-live SOLVED needs strategy to LAND the wire in hdlab (Q111) and the is-a channel + reading volume to
lift absolute correctness (below).

## THE BRAIN-FOUNDATIONAL is-a / TAXONOMIC IDENTITY CHANNEL -- LEARNED from reading, prototyped (owner: "prototype the is-a channel, research, right not easy")
`exp_meaning_fusion_learned_isa_channel_v1.py`, research-led (hdi_research drill 2026-09-09). The WordNet
taxonomic channel is a lever-proof but circular + SUPPLIED. The brain ACQUIRES taxonomic identity from
experience, three ways copied exactly, NONE using WordNet at inference:
  (1) ROGERS-McCLELLAND property-prediction -> the ORDERED SVD of a word x property covariance (Saxe-
      McClelland-Ganguli 2019 PNAS PROVE gradient descent learns exactly these ordered modes; coarse->fine;
      reproduces the semantic-dementia distinctive-features-first gradient). PINNED computation.
  (2) LEVY-GOLDBERG dependency-typed predications as PROPERTIES (functional, not topical similarity). PINNED
      computation; the arc-eager parser TOOL is the NOT_BF dependency (sweep/replace -> incremental_parser).
  (3) GENUS-CENTROID SUBTRACTION for siblings-vs-synonyms (differentia). Genus from READ is-a edges (best).
ANTI-CIRCULARITY GATE enforced: the channel uses ONLY grounded norms + reading-derived dependency features;
NO WordNet. SimLex (human, WordNet-independent) is the gold; the shuffled twin loses.

MEASURED (live anchor pool=556, SimLex gold, n_q=94):
| arm | AUF-MRR |
|---|---|
| grounded-distinctive (current best BF) | 0.188 |
| **learned is-a: property-SVD [grounded (+) dependency predications] (NO WordNet)** | **0.260** |
| grounded + learned-is-a (fusion) | 0.272 |
| info-free twin (shuffled) | 0.006 |
| WordNet CM (LABELLED CIRCULAR ceiling -- not landable) | 0.650 |

- **The learned is-a channel (no ontology) BEATS grounded-distinctive on AUF-MRR (0.260 vs 0.188) and beats
  its info-free twin CI-separated (+0.251 CI[+0.144,+0.356]).** It works: property-covariation SVD +
  dependency predications, learned from reading, is a real is-a signal. HONEST BOUND: the @cov0.5
  point-comparison vs grounded is DIRECTIONAL not CI-separated at this power (+0.058 CI[-0.023,+0.150]) -- an
  area-under-frontier gain that needs more reading/power to be CI-clean.
- **Genus-centroid subtraction via K-MEANS CLUSTERING is a MEASURED NEGATIVE (-0.126 CI[-0.202,-0.048]):**
  clustering is a bad genus proxy; the differentia op needs READ is-a edges. THE READ-EDGE GENUS ORGAN EXISTS
  AND IS WIRED -- `hdlab/definitional_extraction.py` (v6.2 glass-box; `Definition.head` = the genus;
  `_make_definitional_gate`/`substrate.py:538`). BUT MEASURED on the curriculum (news + science, 4640 sents):
  only 320 is-a edges, ~4.5% anchor-pool / ~5.6% query-word coverage, and noisy on news (labour->artwork,
  cup->people). So the read-edge genus is CORPUS/EXPOSURE-STARVED, not missing -- clean genus statements are
  rare in news, dense in encyclopedic/textbook text (~2092 facts over 40k simplewiki+biology sents, prior
  notes). The differentia op needs DEFINITION-RICH reading AT VOLUME (grow-by-reading + corpus selection),
  not more mechanism.
- The circular WordNet ceiling (0.650) marks the headroom: reading volume (grow-by-reading) + a read-edge
  genus (or a curated NON-circular is-a foundation asset) is the path from 0.26 toward it. Blueprint recorded
  in memory (brain-foundational-is-a-acquisition-blueprint).

### OPTIMIZATION ATTEMPT -- separate pools + reliability weighting (MEASURED NEGATIVE; confirms the current architecture)
`exp_meaning_fusion_separate_pools_v1.py`. Our numbers showed the fusion under-exploiting the stronger is-a
channel, suggesting two PINNED upgrades: (1) SEPARATE POOLS combined at read (double dissociation), (2)
RELIABILITY-WEIGHTED convergent Bayes (Ma/Pouget). Built + measured at full power (n_test=47): the upgrade
does NOT beat the current feature-fused representation -- SEP_CALIB (calibrated separate pools) AUF-MRR 0.247
vs FEATFUSE (current) 0.272; SEP_CALIB vs FEATFUSE +0.032 CI[-0.086,+0.165] (null); SEP_EQUAL is worse
(-0.074). PRINCIPLED REASON: Rogers-McClelland taxonomy emerges from the JOINT covariance of ALL properties
in ONE word x property matrix -- so feature-level fusion (grounded (+) dependency in one SVD) IS the brain-
foundational operation here (the joint SVD lets dependency features reorganize the grounded structure); the
"separate pools" double dissociation is for EPISODIC vs SEMANTIC (different memory systems), not feature-types
within one taxonomic computation. So the current feature-fused representation is already architecturally
correct -- no architecture upgrade available; the remaining lever is knowledge/exposure (rare words), not
composition. (Word-class-ROUTED read-out -- noun->taxonomic, verb->relational, adj->grounded-magnitude,
`meaning_operation_router` -- is the mapped next architectural candidate, but needs per-class channels and the
SimLex noun-heavy eval would under-show it.)

### GROW THE CORPUS (owner: "can you grow the corpus?") -- YES; and grounded + learned-is-a now beats grounded CI-sep
The read-edge genus organ (`definitional_extraction`) was STARVED on the curriculum (320 edges, ~5% word
coverage). GROWING the reading corpus with simplewiki (2.3M sentences already on disk -- no acquisition)
clears it: 6660 is-a edges, anchor-pool coverage 4.5% -> 43%, SimLex-query coverage 5.6% -> 37%. Three
measured results (`exp_meaning_fusion_grown_genus_v1.py`, `exp_meaning_fusion_grow_reading_v1.py`):
- **The genus-DIFFERENTIA op is the wrong lever for identity-ranking, even with the grown REAL genus** (read-
  genus differentia vs plain SVD -0.033 CI[-0.121,+0.020], null-to-negative at 49% anchor coverage). It DOES
  cleanly fix the harm the k-means-genus caused (k-means -0.096 CI-sep). Genus-centroid subtraction separates
  SIBLINGS (a discrimination task); it removes the taxonomic signal that helps RANK a same-genus synonym.
- **Growing the corpus did NOT lift the property-SVD is-a channel ALONE on this eval** (ISA_grown vs
  ISA_curriculum -0.015, null) -- because the eval population is COMMON seed words whose dependency coverage
  was ALREADY 0.99 on the curriculum (0.99 -> 1.00 after +40k simplewiki). The grow-by-reading payoff is for
  the RARE long-tail words the loop encounters, which sit outside this common-word eval.
- **BUT the fully-BF fusion now clears the bar: GD + learned-is-a (property-SVD, NO WordNet) beats grounded-
  distinctive CI-separated, +0.055 MRR@0.5 CI[+0.005,+0.127]** (AUF-MRR 0.275 vs 0.188; twin loses +0.238
  CI-sep). A landable, ontology-free improvement over the current best representation.

### GROW A TON BY READING -- CLOSABILITY CURVE (owner: "if closable by reading, show it, and grow a ton") -- CORRECTED FINDING
`exp_meaning_fusion_grow_by_reading_isa_curve_v1.py`. I claimed the 27%->65% gap was "closable by grow-by-
reading" and tested it directly: harvest read-edge is-a from GROWING simplewiki (fast regex, no parser),
build a shared-genus is-a SIMILARITY channel (Roller PPMI+SVD), and measure vs reading volume. RESULT --
**RAW reading does NOT close the gap.** Coverage rose a ton with reading (anchor-genus coverage 0.17 -> 0.28
-> 0.48 -> 0.58 across 40k/120k/400k/800k sentences; 22,735 edges at 800k) but the channel QUALITY did NOT
(ISA_read AUF stuck ~0.02-0.05, non-monotone, `rising=False`), and it DRAGS the grounded fusion BELOW grounded
CI-separated worse (-0.11 to -0.13). **This REVISES my "closable by raw reading" claim** and CONFIRMS the
project's knowledge north-star: RAW reading-derived is-a is noisy/polysemous (work->product/focus/j;
cup->people) so MORE of it adds coverage, not clean identity -- raw regresses. The WordNet ceiling's advantage
(0.65) is CURATION (clean/typed/RESOLVED), not coverage. So the lever to reach the ceiling is CLEAN/CURATED
is-a knowledge (a curated non-circular is-a foundation asset, or online propose-verify-RESOLVE cleanup of the
read edges -- the north-star's curated-foundation-first), NOT raw reading volume. Follow-on TESTED
(`exp_meaning_fusion_clean_isa_v1.py`, 400k reads): cross-encounter CONFIRMATION (keep is-a edges attested
>=K times = the consolidation/propose-verify gate) + polysemy RESOLUTION progressively REMOVES the noise-harm
(fusion vs GD: K=1 raw -0.123 CI-sep worse -> K=2 -0.046 -> K=3 -0.038 -> K=5 +0.004 ~= GD) -- confirming
raw is-a was noise-limited -- BUT it never crosses to HELPING, because confirmation trades COVERAGE for
cleanliness (K=5 coverage collapses to ~1%). **Reading-derived is-a can be CLEAN or HIGH-COVERAGE, not both,
at feasible volume.** DEFINITIVE: the WordNet ceiling (0.65) has clean AND high coverage BECAUSE it is
CURATED; reading cannot supply both. So the lever to reach the ceiling is a CURATED clean is-a FOUNDATION
asset (or the north-star's curated-foundation-first + online propose-verify-resolve) -- OUT OF SOLVER SCOPE (a
knowledge asset + a landing), not a mechanism buildable in experiments/. The mechanism side is complete.

## THE THREE NON-BF WEAK LINKS -- FIXED, fully brain-foundational (owner: "fix them, right not easy")
The performance-vs-brain audit named three components in the upstream chain that were NOT fully BF. They
collapse into two real fixes (the representation fix sidesteps the parser), both prototyped + measured:

**FIX #3 (unordered bag-of-words pooling = the total identity-signal loss) AND #5 (arc-eager parser = NOT_BF
parse input) -- fixed by the SAME move: use the GROUNDED-DISTINCTIVE ATL representation, which needs NO bag
and NO parser.** The bag carries relatedness not identity (live hit@1 ~ 0); the grounded-distinctive read
(z-score = normalization, whitening = ATL privilege-distinctive-features decorrelation) beats it CI-separated
(+0.182 MRR CI[+0.102,+0.275]) and uses only the PINNED Lancaster/Brysbaert norms -- no unordered pooling, no
supervised parser. So the fully-BF representation SIDESTEPS both non-BF dependencies rather than patching
them. (The structured-DISTRIBUTIONAL channel that WOULD need a BF parser is exposure-limited and not the
lever; forcing a parser build there would be metric-chasing, not the right fix. The BF parser
`incremental_parser` remains the mapped follow-on IF that channel is later pursued at reading volume.)

**FIX #7 (the OUR-INVENTION fixed cosine `SENSE_MATCH_THRESH=0.45`) -- fixed by a self-calibrating SDT
criterion on a scale-free familiarity standout** (`exp_meaning_fusion_bf_accept_criterion_v1.py`). MEASURED:
the fixed cosine is representation-BROKEN -- 0.45 admits 22% of decisions in the distributional geometry (what
it was tuned for) but 100% in the grounded geometry (grounded cosines cluster ~0.87-0.92), spread 0.78. The
easy patch (re-sweep 0.45 per rep) is not the right fix. The BF fix: the accept decision is a FAMILIARITY
signal exceeding a CRITERION on a DIVISIVELY-NORMALIZED axis -- z_top = (s1 - mean)/std over the candidate
field (Carandini-Heeger gain control; scale-free), with the criterion set by SIGNAL-DETECTION THEORY (the
z_top at a target false-alarm rate on the info-free null; Yonelinas 2002; Bruce-Young/IAC familiarity gate).
Because z_top is scale-free, the criterion self-calibrates in ANY representation's geometry -- NO hand-set
constant, NO re-tuning when the representation changes. MEASURED: on grounded-distinctive the SDT criterion
gives a controllable precision-coverage knob (5% FA -> accept 5% at 0.600 hit@1; 20% FA -> accept 19% at
0.278), z_top ordering costs NO ranking quality vs raw cosine (+0.000 hit@1@0.5), and accept-by-z_top beats
the info-free twin CI-separated (+0.128 CI[+0.043,+0.234]). BF math verified per operation.

So the fully-BF sense-assignment decision = read canonicalize's ranking over the GROUNDED-DISTINCTIVE ATL
representation (no bag, no parser), accept by a SELF-CALIBRATING SDT familiarity criterion on the scale-free
standout (no fixed cosine). Every operation in that path is a brain computation (see the BF ledgers in the
two cells); nothing in it is an OUR-INVENTION constant or an external tool.

## The hdlab proposal (for the strategy session to land, Q111)
A map + witnessed prototype, not a landed diff. All LOCAL to the ranking's READ; the recall/recognition path
stays byte-identical (witness W5).
1. **Read `canonicalize`'s sense-assignment ranking over the GROUNDED ATL representation** (grounded-dominant;
   `grounded_similarity.grounded_vector`, or the distinctive-feature whitened `distinctive_grounded_vector`),
   NOT the distributional context bundle. On the live anchor-pool decision this is the lever
   (+0.158 MRR / +0.106 hit@1 CI-sep over the incumbent). Keep it a single-shot graded population read.
   **DOWN-WEIGHT the distributional channel to ~0 for this decision** (it is relatedness noise on the small
   anchor pool; grounded-alone >= the grounded+distributional fusion here) -- i.e. the C7 fusion-wire should
   land grounded-DOMINANT, not equal-weight, for canonicalize.
2. **REPLACE the fixed `SENSE_MATCH_THRESH=0.45` with the self-calibrating SDT familiarity criterion** on the
   scale-free z_top standout (`exp_meaning_fusion_bf_accept_criterion_v1.py`). 0.45 is representation-BROKEN
   (admits 22% in the distributional geometry, 100% in the grounded one). The BF fix -- accept iff z_top =
   (s1-mean)/std over the candidate field exceeds the criterion at a target false-alarm rate on the info-free
   null -- is scale-free and self-calibrating, so it needs NO re-tuning when the representation changes (and no
   hand-set constant). The FA rate is the precision-coverage knob (5% FA -> 0.60 hit@1 on grounded). This is
   the BF replacement for the fixed threshold, not a re-sweep.
3. **BUILD A COVERAGE-QUALITY INSTRUMENT** (correct-link rate against an independent gold), because the loop's
   current `n_grounded` COUNT is decision-quality-blind and will not show this win. Without it the lift is
   real but board-invisible.
No other downstream consumer regresses: the change is only what the ranking READS; `canonicalize_fast` ==
reference `canonicalize` (recall/completion untouched), and no hdlab was written.

### ADDENDUM (W19+W20, 2026-09-10) -- the parser-free SEQ channel SUPERSEDES item-1's "down-weight distributional to 0", and grow-by-reading is now a live win
Item 1 above concluded the (unordered, curriculum-only) distributional channel was noise on the anchor pool, so it
should land at ~0 weight. W19/W20 REFINE this: the noise was the UNORDERED pooling, not distributional evidence per
se. The fix (already landed default-OFF by the sibling `the_meaning_representation_is_a_point_vector...`, Q111) is the
DIRECTION-TYPED parser-free channel SEQ (`directional_context_lemmas` + the ROUTE-B store `track_directional_context_counts`
+ existing PPMI). Revised landing:
1b. **Land the fusion as grounded-distinctive (+) SEQ** (the parser-free directional-sequential identity channel),
    NOT grounded-alone and NOT the old unordered bag. At curriculum-only exposure SEQ is under-read and adds nothing
    (keep grounded-dominant); but with reading it BECOMES the lever.
4.  **ENABLE GROW-BY-READING for the SEQ channel** (`track_directional_context_counts=True` in the live ConceptSpace;
    it is parser-free so reading is cheap and online). MEASURED: grounded (+) grown-SEQ beats grounded-alone on the
    live coverage-quality frontier CI-separated once >= ~250k modern lines are read (+0.16 -> +0.26 at 1M, twin
    losing, monotone; W20). Use SATURATING population-gain weighting (log1p, Weber-Fechner / Ma-Pouget) so SEQ's
    weight rises automatically as it earns evidence -- no fitted knob.
5.  **No cleaning stage needed.** A cross-source confirmation gate also wins but does not beat raw (W20) -- direction
    typing already yields an identity (not relatedness) channel, so raw grow-by-reading suffices. (Contrast the old
    UNORDERED bag, W15, which needed cleaning and then collapsed.)
This CLOSES the audit's fusion-flip gate ("live fusion-flip gated on the end-to-end grounding-coverage measurement")
with a POSITIVE result: flip SEQ live + enable grow-by-reading + keep the W20 coverage-quality instrument (item 3).

## What I did NOT establish (and would withdraw first if wrong)
- **I did NOT show the fusion lifts the loop's `n_grounded` COUNT** -- it does not (the count is quality-blind).
  The first thing I would withdraw is any implied coverage-COUNT gain. The win is on coverage QUALITY
  (correct sense-links). It is now measured TWO ways -- the decision-level ranking frontier (CI-separated over
  the incumbent) AND the end-to-end online correct-coverage growth (WordNet-judged, twin-controlled at matched
  count) -- but the online precision advantage over the INCUMBENT specifically is directional, not CI-separated
  (power + unmatched grounding count). I would withdraw any claim of a CI-separated ONLINE precision win over
  the incumbent; the CI-separated incumbent advantage is the decision-level ranking number.
- **The quality win is on the SimLex-covered subset of the anchor-pool decision** (n=94 all-query / 47
  held-out), not on every corpus word the loop grounds (most corpus words have no similarity gold). It is a
  faithful sample of `canonicalize`'s decision, not a whole-corpus correct-coverage census.
- **The distinctive-feature (whitened) upgrade is directional, not CI-separated over raw grounded** on the
  live task; I would not claim it as a separate win, only as the more-brain-foundational default.
- Absolute coverage-quality remains low (MRR ~ 0.1-0.2 among 556 anchors); I claim a decisive RELATIVE win
  over the incumbent, not a solved absolute task.

## KEY REALIZATIONS
- **Measure the metric the mechanism actually affects.** The loop's own coverage COUNT cannot see a
  sense-assignment quality improvement -- it counts threshold-clearing, not correctness. The transfer is real
  but invisible on the count; it needed a coverage-QUALITY instrument to surface. (Board-invisible win needs
  its own instrument-arm.)
- **Rank against the LIVE anchor field, not the full vocab.** Ranking the partner among all 4678 covered
  words drove hit@1 to floor for every arm and hid the transfer; restricting to the loop's actual ~556-word
  seed-anchor pool (what `canonicalize` really scans) is both faithful and where the win is visible.
- **The brief's fusion was over-specified; the identity channel is the lever.** C7's grounded+distributional
  fusion helps in the full-vocab proxy but on the live anchor decision the distributional channel is noise;
  grounded-alone is stronger. The reliability weighting was already telling us this (w grounded-dominant).
- **Densification is not universally a win -- it depends WHERE the signal lives.** Whitening a low-dim
  shared-axis signal (grounded) sharpens identity; low-rank-compressing a high-dim sparse-distinctive signal
  (structured PPMI) discards it. Moved the operating point on the phase diagram AND measured, rather than
  assuming either direction.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- `reading_grounding_loop` (BF_SPIRIT): confirmed the BF_SPIRIT residual is the REPRESENTATION the ranking
  reads (distributional bag = NOT_BF unordered pooling), now measured LIVE on the loop's coverage-quality
  (incumbent hit@1 ~ 0; grounded beats it +0.106 CI-sep). The `canonicalize_fast` graded read itself is BF
  and untouched.
- New deviation to record: the loop's coverage metric `n_grounded` (COUNT) is decision-quality-blind -- it
  cannot register a sense-assignment quality gain, so it is the wrong instrument for the meaning-channel
  landing. A correct-link coverage-quality instrument is the missing measurement organ.

---
## TLDR (plain language)
When the system reads a new word it grows its vocabulary by deciding which known word it means. We asked: if
it makes that decision with a more brain-like sense of meaning (what a thing IS -- its felt/perceptual
identity) instead of mere word-company, does it end up knowing MORE words after a real read? The plain count
of words it "learned" does NOT go up -- but that count is a bad yardstick: it only checks that the system
picked SOME match, never whether the match is RIGHT, and today most of its matches are junk (it links "owner"
to "fine", "google" to "hope"). When we measure whether the matches are CORRECT, the brain-like meaning cue
wins clearly and reliably, and the plain word-company cue is essentially never right. The winning cue is the
grounded "what it is" sense; adding word-company back in only adds noise here. We also tried the owner's
"make the signal dense" trick on a second, learned cue; it helped the perceptual cue but not the learned one
(that cue's meaning lives in rare specific clues that get blurred by compression -- it needs more reading, not
compression). Bottom line: don't expect more words learned; DO expect the words it learns to be matched to the
RIGHT meaning far more often -- and to see that, we need to start scoring match CORRECTNESS, not just counts.

## QUESTIONS
None blocking.

## NEXT STEPS
1. **(hand-off to strategy, Q111)** Land the fully-BF sense-assignment decision: read `canonicalize`'s
   ranking over the GROUNDED-DISTINCTIVE ATL representation (grounded-dominant; distributional down-weighted to
   ~0 on this decision; no bag, no parser -- FIX #3/#5), and REPLACE the fixed `SENSE_MATCH_THRESH` with the
   self-calibrating SDT familiarity criterion on the z_top standout (FIX #7). Recall path byte-identical. This
   is the C7 fusion-wire, REFINED to grounded-dominant with a brain-foundational accept gate.
2. **(the missing instrument -- prerequisite to a visible landing)** Build a coverage-QUALITY / correct-link
   metric (independent gold) into the loop's measurement, so a sense-assignment quality gain is scorable. The
   current `n_grounded` count will not show it.
3. **(THE biggest optimization -- quantified) The is-a / TAXONOMIC IDENTITY channel is the dominant lever.**
   Live anchor-pool decision (same population, SimLex gold): taxonomic AUF-MRR 0.650 vs grounded-distinctive
   0.188 (+0.488 CI[+0.360,+0.620]); grounded+taxonomic 0.657 (best); twin 0.006 -- supplying is-a knowledge
   takes the live decision from ~15% to ~65% of achievable (`exp_meaning_fusion_taxonomic_lever_v1.py`). HONEST
   CAVEAT: measured with WordNet definitional features (partly circular with SimLex) = a LEVER-PROOF, not a
   landable BF number. The BRAIN-FOUNDATIONAL way to BANK it is PROTOTYPED (above): the learned property-SVD
   is-a channel (Rogers-McClelland + Levy-Goldberg, NO WordNet) beats grounded on AUF (0.260 vs 0.188), twin
   losing -- a real learned-from-reading is-a signal. To make it CI-clean over grounded and approach the
   circular ceiling: MORE READING (grow-by-reading) + a READ-edge genus for the differentia op (the
   clustering-genus substitute measured NEGATIVE) or a curated non-circular is-a FOUNDATION asset.
4. **(the learned is-a channel's real lever)** The dependency-substitutability channel is exposure-limited, not
   ceilinged -- it rises with reading and is BF (parse input aside). The lever is MORE READING (the
   grow-by-reading north-star) and a BF general parser (`incremental_parser`) to remove the arceager NOT_BF
   dependency. Densification is NOT the lever for it (measured: low-rank SVD smooths the distinctive contexts).
5. **(the other identified improvement -- WORD-CLASS-ROUTED read-out, a validated-organ WIRING)** Per-POS, the
   fused identity representation is 3x WEAKER on ADJECTIVES (SimLex identity rho: NOUN 0.315, VERB 0.255, ADJ
   0.099) -- and ALL 63 covered adjectives are GRADABLE, where cosine-similarity is the WRONG operation
   (gradable adjectives are a scalar MAGNITUDE, not a "similar-to-what"; old/new share a dimension at opposite
   poles). The landed, validated `hdlab.meaning_operation_router` (SOLVED/EXCELLENT: routed 0.616 vs gloss-only
   0.424) already DETECTS gradable adjectives; the improvement is to WIRE it into the sense-assignment read-out
   -- route gradable adjectives to the scalar-magnitude op (`hdlab.scalar_adjective_operation`), nouns/verbs/
   classificatory-adjectives to the identity representation. Operation-specific semantic cognition, fully BF,
   fixes the weakest word class. Impact is BOUNDED (adjectives ~12% of pairs) but real; it is a composition/
   wiring of existing organs, not a new mechanism.
