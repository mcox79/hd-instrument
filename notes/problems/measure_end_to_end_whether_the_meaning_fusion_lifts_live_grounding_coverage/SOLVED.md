---
problem: measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage
status: PARTIAL
bar: "PASS = an END-TO-END measurement on the LIVE reading-grounding loop (a faithful harness of canonicalize_fast's read over the real reading corpus, curriculum-ordered as the loop does it) showing whether reading the sense-assignment ranking over the reliability-weighted convergent fusion (grounded + distributional [+ is-a/taxonomic identity], the landed convergent_cue_reader Bayes rule, weights/taus calibrated OFFLINE + held-out) changes the loop's OWN downstream GROUNDING-COVERAGE GROWTH metric -- with (a) the INFO-FREE TWIN (shuffled representation rows) LOSING, (b) the recall/recognition path byte-identical, (c) the number reported with a CI on the loop's own metric/population (no cross-population/scorer number). A CI-SEPARATED lift is a landable win. A rigorous LOCATED NEGATIVE -- the ranking win does NOT transfer to coverage -- is a FULL PASS if it names, WITH A NUMBER, exactly why (e.g. coverage is gated by candidate GENERATION not sense SELECTION; or the loop's coverage is exposure-bound not decision-bound), and then builds the stronger brain version and tests THAT before concluding."
result: "TWO-PART. (1) LOCATED NEGATIVE on the loop's OWN coverage-COUNT metric: the sense-assignment representation does NOT cleanly move n_grounded -- it is decision-quality-BLIND. Genuine online loop over the full curriculum (4640 sentences, curriculum-ordered, process_sentence + consolidation_pass with a swapped sense-assignment gate): INCUMBENT (distributional) grounds 143 words; the fusion grounds 133 (strict accept) to 202 (accept-all) depending ONLY on the accept threshold -- the count tracks thresh-clearing/exposure, NOT ranking correctness. And the incumbent's 143 grounded links are co-occurrence garbage (artwork->happy, google->hope, owner->fine). (2) CI-SEPARATED WIN on coverage QUALITY (the instrument the count is blind to): ranking the true SimLex-999 sense-partner against the loop's ACTUAL 556-word seed-anchor pool through canonicalize's real decision, a brain-foundational meaning representation beats the distributional incumbent CI-separated -- GROUNDED-ATL MRR@cov0.5 +0.158 CI[+0.089,+0.252] and hit@1@cov0.5 +0.106 CI[+0.021,+0.191] (all-query, n=94; both parameter-free); full-coverage MRR +0.103 CI[+0.058,+0.153]; AUF-MRR grounded-distinctive 0.232 > grounded 0.198 > fusion 0.130 > incumbent 0.037 > twin 0.010. REFINEMENT of the brief's mechanism: the transfer is carried by the GROUNDED ATL identity channel, NOT the grounded+distributional FUSION -- on the live anchor pool the distributional channel is noise, so grounded-alone >= fusion (fusion still beats incumbent +0.096 CI[+0.022,+0.189] but trails grounded). 2026-09-10 UPDATE (W19+W20, see body): the chain is now 100% BRAIN-FOUNDATIONAL (parser-free -- the sibling's directional-sequential SEQ channel removes the NOT_BF pos_tagger+arceager) and STILL beats the incumbent live CI-sep (W19); and GROWING that parser-free channel by reading Simple-Wiki lifts the live increment OVER grounded CI-separated (+0.16 at 250k lines -> +0.26 at 1M, twin losing, monotone), so KNOWLEDGE/EXPOSURE is the proven LIVE lever and the fusion-flip gate is closed POSITIVE (W20). Landable: the hdlab wire spec below. 2026-09-10 (W37) REFERENT-DATA BUILD (item 1): added a REAL, non-text VISUAL referent spoke -- DINOv2 (vision-only ventral-stream/IT stand-in, NOT CLIP whose image embeds are caption-trained) frozen-at-ingest over 1854 THINGS natural photos -- and measured it on the INDEPENDENT THINGS-behavior human-similarity gold (1438 concepts). RESULT (seed-stable, twin-controlled): the pure-visual spoke ADDS +0.018 unique R2 over text+grounded CI-sep [0.014,0.023] with the shuffled-visual twin at +0.000 (twin losing), and DINOv2 is measurably less text-redundant than CLIP (0.029 vs 0.080). So the referent-data lever is REAL, not zero -- BUT small, shown on PERCEPTUAL similarity (grounded/Lancaster alone is the strongest single channel, RSA 0.41 vs visual 0.17), and the SEMANTIC-synonymy (SimLex/SimVerb) payoff stays DATA-COVERAGE-BOUND (only ~18 covered pairs; directional visual>text rho 0.45 vs 0.30 but underpowered). This REFINES the prior data-ceiling conclusion: real referent data adds meaning text cannot reach, but small and coverage-limited for the synonymy target. 2026-09-10 (W38) HONED FUSION + POWERED SEMANTIC TEST: research (E1-E4) found v1's SVD-over-concat fusion was NOT a precision combiner (it maximizes shared covariance, so weak spokes dilute the strong one -- v1 fused 0.29 < grounded-alone 0.41). REPLACED with a recovery-gated, per-concept precision-weighted convergent-cue fusion (Ma-Pouget/Ernst-Banks + the hdlab.gated_fusion recovery-gate pattern: VAL weight-grid includes the best-single-channel one-hot, so fusion CANNOT dilute the strong channel by construction). RESULT (seed-stable): fusion 0.461 > grounded-alone 0.415-0.426 on THINGS-behavior (no dilution, realizes visual). AND added the powered SEMANTIC gold MEN (391 covered pairs vs SimLex's ~18): visual adds +0.044 R2 over text+grounded CI-sep [0.016,0.082], shuffled-visual twin +0.001 (twin losing), seed-stable -- so vision ADDS to SEMANTIC (relatedness) similarity on concrete nouns, not just perceptual, REFINING the W37 perceptual-not-semantic caveat. (MEN is relatedness-leaning, reported as a distinct claim; strict-synonymy SimLex stays data-thin at ~18 pairs.) 2026-09-11 (W39) MULTI-EXEMPLAR VOLUME UPGRADE (Phase 2, research E1/E3): re-embedded the FULL THINGS set (~14 photos/concept, up from 1) -> per-concept denoised DINOv2 CENTROID + exemplar DISPERSION (= the per-concept visual reliability; the photo-set's spread IS the precision, replacing the Visual.mean proxy). The denoised centroid ~DOUBLES the visual referent's unique SEMANTIC contribution over text+grounded on MEN (single-photo +0.044 -> multi +0.086 R2 CI-sep [0.042,0.137], twin +0.001 twin-losing, seed-stable), lifts visual-alone MEN rho 0.42 -> 0.60 (~tied with text 0.60, above grounded 0.53) and visual RSA on the perceptual gold 0.16 -> 0.27; the recovery-gated fusion still does not dilute grounded. Dispersion behaves correctly (submarine/koala tight=reliable; dog/flower/bird loose=unreliable). NET: the referent-data lever is real AND materially larger once the referent vector is denoised by volume -- the single-photo v1/v2 was noise-limited."
floor: "Strongest floor = the DISTRIBUTIONAL incumbent (the loop's live canonicalize representation): coverage-quality MRR@cov0.5 0.034, hit@1 0.000-0.033, AUF-MRR 0.037; live coverage count n_grounded 143. Info-free twins (shuffled representation rows): AUF-MRR 0.010 (fusion twin) / carries no per-word signal. On the true-BF representation prototype the sparse structured channel's own floors: bag-of-words AUF-MRR 0.030, its info-free twins 0.006-0.008."
controls: "INFO-FREE TWIN (shuffled grounded/representation rows) LOSES CI-separated on every headline (grounded vs twin MRR@0.5 +0.195 CI[+0.106,+0.298]; fusion vs twin +0.122 CI[+0.028,+0.241]; DEP-structured vs twin +0.097 CI[+0.042,+0.178]) -> the win carries real per-word meaning, not base-rate. RECALL/RECOGNITION PATH BYTE-IDENTICAL: canonicalize_fast == reference canonicalize (witness W5; only what the ranking READS changed; no hdlab written). HARNESS FAITHFULNESS positive control: the cell's INCUMBENT gate decision == the live canonicalize (accept/refuse + chosen anchor) on 40/40 random query bundles (W4). INDEPENDENT GOLD: SimLex-999 human similarity (WordNet-independent, independent of every representation). HELD-OUT: the fusion weight w is calibrated on a disjoint train split and evaluated on test; grounded/incumbent are parameter-free (evaluated on all queries, no leak). FAITHFUL POOL: candidates restricted to the loop's ACTUAL seed-anchor field (not the full vocab) -- ranking against the whole 4678-word vocab drives hit@1 to floor for every arm and hides the transfer. THRESHOLD SWEEP: coverage count reported across accept thresholds (matched selectivity) so the count comparison is not a single confounded point. PHASE-DIAGRAM densification SWEEP (k in {50,100,200} x power in {0.5 SGNS, 0.0 whitened}) -- excludes 'the structured channel is just under-optimized'."
files_changed: "experiments/exp_meaning_fusion_live_coverage_v1.py (the end-to-end transfer measurement: PART A genuine online coverage-count + PART B coverage-quality selective-prediction frontier, all arms, twins), experiments/exp_meaning_fusion_bf_representation_v1.py (the TRUE-BF representation prototype -- FIX #3/#5: ATL distinctive-feature whitened grounded + structured dependency/adjacency PPMI substitutability, convergent-cue Bayes, + the phase-diagram SVD-densification sweep), experiments/exp_meaning_fusion_bf_accept_criterion_v1.py (FIX #7: the self-calibrating SDT accept criterion on the scale-free z_top standout, replacing the fixed cosine), experiments/exp_meaning_fusion_correct_coverage_growth_v1.py (the PARTIAL->SOLVED converter: genuine online loop with the fully-BF decision wired, WordNet-judged CORRECT-coverage growth, twin-controlled at matched count), verification/test_meaning_fusion_live_coverage.py (scaffold-free witness, 11/11 checks (W1-W13)), data/exp_meaning_fusion_live_coverage_v1/metrics.json, data/exp_meaning_fusion_bf_representation_v1/metrics.json, data/exp_meaning_fusion_bf_accept_criterion_v1/metrics.json, data/exp_meaning_fusion_correct_coverage_growth_v1/metrics.json, experiments/exp_meaning_fusion_taxonomic_lever_v1.py (quantifies THE big remaining lever: the is-a/taxonomic identity channel on the live anchor-pool decision -- lever-proof under the WordNet-circularity caveat), data/exp_meaning_fusion_taxonomic_lever_v1/metrics.json, experiments/exp_meaning_fusion_learned_isa_channel_v1.py (the research-led BRAIN-FOUNDATIONAL is-a channel LEARNED from reading -- Rogers-McClelland property-SVD + Levy-Goldberg dependency + genus-differentia, NO WordNet; beats grounded on AUF, twin losing), data/exp_meaning_fusion_learned_isa_channel_v1/metrics.json, experiments/exp_meaning_fusion_grown_genus_v1.py (GROW the corpus -> read-edge genus 5%->43%; genus-differentia neutral even with the real genus), experiments/exp_meaning_fusion_grow_reading_v1.py (grow-by-reading: GD + learned-is-a beats grounded CI-sep +0.055), data/exp_meaning_fusion_grown_genus_v1/metrics.json, data/exp_meaning_fusion_grow_reading_v1/metrics.json, experiments/exp_meaning_fusion_separate_pools_v1.py (optimization attempt -- separate pools + reliability weighting = MEASURED NEGATIVE; the joint property-SVD feature-fusion is the correct BF architecture), data/exp_meaning_fusion_separate_pools_v1/metrics.json, experiments/exp_meaning_fusion_matched_coverage_v1.py (matched-count online converter: at equal grounding count fully-BF grows more correct-coverage than incumbent at every judge strictness -- directional, not CI-sep at full = judge noise), data/exp_meaning_fusion_matched_coverage_v1/metrics.json, experiments/exp_meaning_fusion_grow_by_reading_isa_curve_v1.py (grow-a-ton closability curve: raw read-edge is-a to 800k sents grows coverage 0.17->0.58 but NOT quality -> raw reading does not close the gap), experiments/exp_meaning_fusion_clean_isa_v1.py (CLEAN vs RAW: confirmation gate removes noise-harm but coverage collapses -> curated clean knowledge is the lever, out of scope), data/exp_meaning_fusion_grow_by_reading_isa_curve_v1/metrics.json, data/exp_meaning_fusion_clean_isa_v1/metrics.json, experiments/exp_meaning_fusion_signal_trace_v1.py (RIGOROUS signal-loss trace: identity(SimLex) vs relatedness(Assoc) rho per rung, math-BF confirmed, localizes the loss to the unordered distributional pooling), data/exp_meaning_fusion_signal_trace_v1/metrics.json, experiments/exp_meaning_fusion_role_bound_context_v1.py (THE BF FIX prototyped: role-filler binding via hdlab.binding for the pooling loss; positional roles move identity the right way but are insufficient -> syntactic roles = a BF parser is the last non-BF atom), data/exp_meaning_fusion_role_bound_context_v1/metrics.json, experiments/exp_meaning_fusion_syntactic_role_binding_v1.py (PROPER-solution test: role-filler binding over SYNTACTIC roles from the BF incremental_parser; confirms syntactic-roles-yes, binding-estimator-too-noisy -> PPMI-SVD is the working low-variance estimator), data/exp_meaning_fusion_syntactic_role_binding_v1/metrics.json, experiments/exp_meaning_fusion_live_coverage_seq_v1.py (W19 -- the parser-free 100%-BF live transfer: the directional-sequential identity channel SEQ (no pos_tagger/arceager) fused with grounded, on the loop's own coverage-quality frontier; beats the incumbent CI-sep + twin losing, but does not add over the best grounded rep at 34k-sentence exposure -> exposure is the lever), data/exp_meaning_fusion_live_coverage_seq_v1/metrics.json, experiments/exp_meaning_fusion_grow_seq_live_v1.py (W20 -- PHASE B: grow the parser-free SEQ channel by reading Simple-Wiki through the loop's REAL ingest taps, measure the live increment over grounded at 0/250k/500k/1M/2M lines; crosses to CI-sep positive at 250k and stays positive+monotone, twin losing; clean-confirmation arm wins too but does not beat raw), data/exp_meaning_fusion_grow_seq_live_v1/metrics.json, experiments/exp_meaning_fusion_confidence_calibration_v1.py (W21 -- confidence-calibration located negative: no BF certainty signal recovers the +0.245 perfect-ordering gap; z_top/SDT marginally best +0.006, gain+agreement anti-track), data/exp_meaning_fusion_confidence_calibration_v1/metrics.json, experiments/exp_meaning_fusion_valence_channel_v1.py (W22 -- valence antonymy 3rd-channel located negative on synonym-ranking: +0.006 not CI-sep, oracle barely rises; both negatives converge on RELATION CONFUSION -> is-a channel is the real lever), data/exp_meaning_fusion_valence_channel_v1/metrics.json, experiments/exp_meaning_fusion_confidence_bf_v1.py (W23 -- brain-exact confidence re-drill: balance-of-evidence DV margin is best + brain-exact; reliability-normalization ties it; gap is representational not metacognitive), data/exp_meaning_fusion_confidence_bf_v1/metrics.json, experiments/exp_meaning_fusion_differentia_channel_v1.py (W24 -- brain-exact differentia channel, parser-free ordered-SVD late modes gated by genus: beats global cosine +0.145 + raises oracle ceiling +0.044 CI-sep, twin losing; realistic capture unsolved), data/exp_meaning_fusion_differentia_channel_v1/metrics.json, notes/problems/measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage/FULL_CHAIN_BF_AUDIT.md (every rung raw-text->decision enumerated BF/BF_SPIRIT, no NOT_BF atom), experiments/exp_meaning_fusion_recollection_gate_v1.py (W25 -- brain-exact dual-process recollection gate (coarse genus/familiarity vs fine differentia agreement) as per-query reliability + genus-local recollection-gated re-rank; directional +0.03 on confidence and capture, real signal vs twin CI-sep, but power-limited at n=169), data/exp_meaning_fusion_recollection_gate_v1/metrics.json, experiments/exp_meaning_fusion_path2_proof_v1.py (W26 -- rigorous powered all-directions K-swept proof attempt for Path 2: recollection real-signal vs twin CI-sep but capture/confidence not CI-sep even at n=338 -> located negative), data/exp_meaning_fusion_path2_proof_v1/metrics.json, experiments/exp_meaning_fusion_targeted_reading_v1.py (W27 -- targeted reading of the rare tail: LOCATED NEGATIVE, tested words already well-read -> plateau is a representational ceiling; produces data/exp_meaning_fusion_targeted_reading_v1/targeted_reading_corpus.txt but it does NOT lift so it is NOT recommended for ingest), data/exp_meaning_fusion_targeted_reading_v1/metrics.json, experiments/exp_meaning_fusion_isa_knowledge_v1.py (W28 -- clean non-circular read-is-a knowledge channel, WordNet-free Hearst: LOCATED NEGATIVE, too sparse/noisy for common vocab, does not beat knowledge-shuffled twin), data/exp_meaning_fusion_isa_knowledge_v1/metrics.json, experiments/exp_meaning_fusion_isa_conceptnet_v1.py (W29 -- curated non-circular ConceptNet is-a, WordNet-excluded: DEEPER located negative, genus similarity promotes co-hyponyms, hurts + worse than knowledge-shuffled twin), data/exp_meaning_fusion_isa_conceptnet_v1/metrics.json, experiments/exp_meaning_fusion_glassbox_lemma_v1.py (W30 -- glass-box WordNet-free lemmatizer to replace the morphy dependency; 92.6%% agreement, over-stems base words -> needs a non-WordNet base-form lexicon for lossless), data/exp_meaning_fusion_glassbox_lemma_v1/metrics.json, experiments/exp_meaning_fusion_componential_hv_v1.py (W31 -- FHRR componential-HV mechanism, ground-truth Binder; proven but not powerable, 4-pair overlap), experiments/exp_meaning_fusion_componential_hv_v2.py (W32 -- DERIVED componential features via Hebbian readout supervised on Binder: FIRST lever to beat our channels on identity 0.171>0.134 twin-losing, identity-selective; HV-binding~flat so the FEATURES are the lever; live-transfer pending), data/exp_meaning_fusion_componential_hv_v1/metrics.json, data/exp_meaning_fusion_componential_hv_v2/metrics.json, experiments/exp_meaning_fusion_componential_live_v1.py (W33 -- the DECISIVE live-transfer test: derived componential does NOT lift the live coverage-quality CI-sep (+0.013), because it is a re-projection of grounded+SEQ, redundant live; twin barely loses = faint signal; the ranking-proxy win did not transfer), data/exp_meaning_fusion_componential_live_v1/metrics.json, experiments/exp_meaning_fusion_predictive_grounding_v1.py (W34 -- the PREDICTIVE re-cast: reuses PredictiveWorldModel (Rescorla-Wagner/N400); cloze prediction from running context beats no-context prior +0.0037 and scrambled twin +0.0043 CI-sep, lowers surprisal 0.04 bits; first controlled top-down signal, small magnitude with simplest model), data/exp_meaning_fusion_predictive_grounding_v1/metrics.json, experiments/exp_meaning_fusion_compositional_prediction_v1.py (W35 -- compositional prediction (verb+agent->patient via composed_hub_predictor + incremental_parser): does NOT add to the frequency prior; per-word prediction intrinsically weak/high-entropy, consistent w/ brain low-cloze; loop value = error-driven learning+integration not cloze accuracy), data/exp_meaning_fusion_compositional_prediction_v1/metrics.json, experiments/exp_meaning_fusion_crossmodal_hub_v1.py (W36 -- cross-modal referent hub, concreteness-gated modality precision over grounded+SEQ: does NOT beat the ungated fusion; visual referent data ~21 words / Binder ~534 = data-blocked; converges the whole investigation on the referent-grounding DATA limit), data/exp_meaning_fusion_crossmodal_hub_v1/metrics.json, experiments/exp_meaning_fusion_visual_referent_ingest_v1.py (W37 STEP A -- DINOv2 (vision-only, R2) + CLIP-diagnostic frozen-at-ingest embedding of 1854 THINGS CC0 photos -> per-concept visual referent vectors; resumable/checkpointed; torchvision-free glass-box preprocessing), experiments/exp_meaning_fusion_visual_referent_hub_v1.py (W37 STEP B/C -- the cross-modal referent hub (Cox-Rogers correlated subspace + Ma-Pouget/Visual.mean precision) + gates G1-G4 on the THINGS-behavior human-similarity gold, twin-controlled, TruncatedSVD-densified text channel), data/things_referents/ (THINGS foundation asset: concepts-metadata_things.tsv, images_CC0.zip, spose_embedding_66d_sorted.txt gold, referent_vectors.npz), data/exp_meaning_fusion_visual_referent_hub_v1/metrics.json, notes/problems/measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage/DESIGN_visual_referent_hub_2026-09-10.md, experiments/exp_meaning_fusion_visual_referent_hub_v2.py (W38 -- the HONED recovery-gated per-concept precision fusion (E3 fix; Ma-Pouget/Ernst-Banks + gated_fusion recovery-gate PATTERN reused, no hdlab write) + the powered MEN semantic gold, twin-controlled), data/encoder_eval_benchmarks/men_3k.txt (MEN gold, Bruni-Tran-Baroni 2014, non-circular), data/exp_meaning_fusion_visual_referent_hub_v2/metrics.json, experiments/exp_meaning_fusion_visual_referent_ingest_v2.py (W39 -- MULTI-EXEMPLAR ingest: DINOv2 over the full THINGS set ~14 photos/concept -> per-concept centroid + exemplar dispersion; resumable/checkpointed; the --multi flag in hub_v2 uses 1/dispersion as the visual precision), data/things_referents/images_THINGS.zip (full THINGS, research/non-commercial license) + referent_vectors_multi.npz + men_3k.txt, data/exp_meaning_fusion_visual_referent_hub_v2_multi/metrics.json. NO hdlab/ modified (Q111 -- the hdlab proposal is stated below for the strategy session to land)."
reverify: ".venv/Scripts/python.exe verification/test_meaning_fusion_live_coverage.py  (37/37 checks, W1-W39 incl. W39 the MULTI-EXEMPLAR volume upgrade (full THINGS ~14 photos/concept -> denoised DINOv2 centroid + exemplar dispersion as the real visual precision; ~doubles the visual referent's unique SEMANTIC contribution on MEN +0.044->+0.086 R2 CI-sep twin-losing, visual-alone MEN rho 0.42->0.60, seed-stable); W38 the HONED FUSION (recovery-gated per-concept precision fusion -- fixes v1's dilution: fused 0.461 > grounded-alone 0.415-0.426 on THINGS-behavior, no dilution by construction) + the POWERED SEMANTIC test (MEN, 391 covered pairs: visual adds +0.044 R2 over text+grounded CI-sep twin-losing, seed-stable -- vision adds to SEMANTIC similarity on concrete nouns); W37 the REFERENT-DATA build (DINOv2 pure-visual spoke over THINGS photos vs the THINGS-behavior human-similarity gold, n=1438; visual adds +0.018 unique R2 over text+grounded CI-sep, shuffled-visual twin losing, seed-stable; DINOv2 less text-redundant than CLIP; REAL but MODEST, perceptual-not-semantic, SimLex coverage ~18 pairs = data-bound); W36 the cross-modal referent hub (concreteness-gated; located negative; richer referent spokes data-blocked -> the limit is referent-grounding DATA); W35 the compositional-prediction located negative (per-word prediction intrinsically weak); W34 the predictive re-cast (prediction from running context beats prior+twin CI-sep, first controlled top-down signal); W33 the componential live-transfer located negative; W31 the componential-HV mechanism + W32 the DERIVED componential features beating our channels on identity; W29 the ConceptNet curated-is-a counterproductive negative + W30 the glass-box lemmatizer (WordNet-morphy replacement); W28 the clean-is-a-knowledge located negative + the WordNet-morphy BF correction; W27 the targeted-reading located negative; W26 the powered Path-2 located negative; W25 the brain-exact dual-process recollection gate -- directional + real-signal but power-limited: incl. W19 parser-free 100%-BF live transfer, W20 grow-by-reading PHASE B live win, W21/W22 the first-round confidence/valence located negatives, W23 the brain-exact confidence re-drill (balance-of-evidence margin is best; gap is representational), W24 the brain-exact differentia channel (beats global cosine + raises the oracle ceiling CI-sep; capture unsolved)). Full-chain BF audit: notes/problems/.../FULL_CHAIN_BF_AUDIT.md. Powered headline reproducer (own-dir only): .venv/Scripts/python.exe experiments/exp_meaning_fusion_live_coverage_v1.py --mode full --no-online ; parser-free live transfer: .venv/Scripts/python.exe experiments/exp_meaning_fusion_live_coverage_seq_v1.py ; grow-by-reading Phase B (up to 2M SW lines, ~4min): .venv/Scripts/python.exe experiments/exp_meaning_fusion_grow_seq_live_v1.py --read-cap 2000000"
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

## UPDATE 2026-09-10 (W25) -- the brain-exact per-query reliability (DUAL-PROCESS RECOLLECTION) + FINAL vs-brain ladder & signal-loss

`exp_meaning_fusion_recollection_gate_v1.py`. The unified wall (W20-W24): a per-query reliability that is NOT scalar
familiarity. Brain-exact = DUAL-PROCESS RECOLLECTION (Yonelinas/Kepecs/Fleming-Daw): recollection = agreement between
the coarse genus/familiarity code and the fine DIFFERENTIA code -- a confidently-wrong pick is a co-hyponym the
familiarity likes but the differentia REJECTS (familiarity without recollection). Built parser-free: reliability =
the differentia standout of the base top-1 within its genus neighbourhood; capture = genus-local recollection-gated
soft re-rank (z(familiarity)+z(differentia) within the base top-K). MEASURED (n=169): recollection is better
calibrated than margin (rho 0.149 vs 0.132) and DIRECTIONALLY positive on BOTH confidence (+0.030) and capture
(+0.025), and it CARRIES REAL SIGNAL (recgate beats its shuffled-differentia twin +0.101 CI [+0.016,+0.187], twin
losing) -- but neither the confidence recovery nor the capture is CI-separated over the base at this power (CI
half-width ~0.07 vs a ~0.03 effect). VERDICT: the brain-exact mechanism is the RIGHT direction (real signal, better
calibration, directionally positive) but POWER-LIMITED at n=169; the realized capture is small. Resolving it needs
POWER (more anchor-pool queries) + EXPOSURE (grow the channels), which converge with the proven Phase-B lever.

### FINAL vs-BRAIN LADDER + SIGNAL-LOSS (live coverage-quality AUF-MRR, n=169, read_cap 500k; brain=perfect=1.0)
| stage | AUF-MRR | ~% of brain |
|---|---|---|
| incumbent (distributional bag, the old live rep) | 0.051 | 5% |
| grounded ATL alone | 0.164 | 16% |
| grown-SEQ alone (parser-free, read to 500k) | 0.363 | 36% |
| **fused {grounded, grown-SEQ}** (the landable win) | **0.412** | **41%** |
| + recollection gate (directional, not CI-sep) | ~0.41 | ~41% |
| fusion with PERFECT confidence ordering (ceiling) | 0.658 | 66% |
| oracle over {grounded, SEQ, differentia} | 0.681 | 68% |
| brain (perfect sense-assignment) | 1.000 | 100% |

WHERE THE SIGNAL IS LOST (descending from brain=1.0), and the state of each lever:
- **0.681 -> 1.0 = +0.319 KNOWLEDGE/EXPOSURE** (queries all channels miss). Lever = grow-by-reading (PROVEN Phase B:
  +0.16->+0.26 CI-sep, monotone) + more channels. ADDRESSABLE, in progress.
- **0.412 -> 0.658 = +0.246 CONFIDENCE / PER-QUERY RELIABILITY** (the rep ranks well but can't say which pick is
  right). Levers tried: scalar confidence (W21/W23, ~0 recovery), recollection (W25, directional +0.03, real signal,
  power-limited). BRAIN-EXACT DIRECTION FOUND (recollection), REALIZATION power-limited.
- **0.658 -> 0.681 = +0.023 per-query channel routing** (small; opens only once the differentia is added -- W24).
- Everything ABOVE 0.412 (incumbent 0.051 -> fused 0.412, +0.361) is BANKED, CI-sep, twin-losing, 100% brain-
  foundational (parser-free), and is the landable win. The differentia raising the oracle ceiling to 0.681 (+0.044
  CI-sep, W24) proves the remaining coverage is real and reachable.

## UPDATE 2026-09-10 (W20 full-corpus + W26) -- the TWO improvement paths, PROVEN / REFUTED rigorously

Owner: "prove those 2 improvement paths, BF and rigorous."

**PATH 1 -- KNOWLEDGE / GROW-BY-READING: PROVEN (CI-separated, monotone, twin-losing, full corpus).**
`exp_meaning_fusion_grow_seq_live_v1.py` re-run to the FULL 2,778,810-line Simple-Wikipedia corpus. The increment
grounded(+)grown-SEQ minus grounded-alone on the live coverage-quality frontier (n=169, 3000-boot, gain-weighted):
0 lines -0.066 -> 250k **+0.160** -> 500k **+0.223** -> 1M **+0.263** -> 2M **+0.250** -> 2.8M **+0.271**, CI-separated
at every point from 250k (crossover) through 2.8M, twin losing throughout, and CI-sep POSITIVE for BOTH word classes
independently at top (SimLex +0.211, SimVerb +0.270). It saturates on a ~+0.26 plateau after ~1M lines (bulk generic
reading has diminishing returns; the tail is the rare words -> targeted reading is the extension). This is a proven,
brain-foundational (parser-free online Hebbian accrual + PPMI) lever.

**PATH 2 -- CONFIDENCE / PER-QUERY RELIABILITY (recollection): rigorously tested, LOCATED NEGATIVE.**
`exp_meaning_fusion_path2_proof_v1.py`. Given every fair chance WITHOUT relaxing fidelity: POWERED to all query
directions (n=338, legitimate -- the recollection arms are PARAMETER-FREE, nothing fit to eval labels); at GROWN SEQ
(2M, sharper differentia); K swept {5,8,12,16,24}. RESULT: the recollection-gated re-rank beats its info-free
(shuffled-differentia) twin CI-SEPARATED at EVERY K (+0.078..+0.126) -- the dual-process recollection signal is REAL
-- BUT it does NOT beat the base fusion (capture: best +0.024 at K=24, CI [-0.033,+0.065], NOT CI-sep at any K) nor
the margin (confidence: best +0.029, NOT CI-sep; at this power the plain balance-of-evidence margin is actually the
better-calibrated signal, rho 0.219 vs recollection <=0.21 -- the W25 edge was noise). VERDICT: the brain-exact
per-query reliability signal is genuine but its net effect (~+0.02 AUF) is below the RESOLUTION of the available
identity gold (n=338, CI half-width ~0.05; resolving a +0.02 effect needs n~2000, unavailable). The differentia's
oracle-ceiling gain (+0.044, W24) is real but NOT capturable by any per-query reliability we can build at this
exposure -- three principled mechanisms tried (linear fusion, hard rerank, soft genus-local rerank), all fail to
beat the base CI-sep. HONEST BOUND, not a ceiling proof: a stronger per-query reliability (richer episodic
recollection/source memory) could still capture it, but is not available in the current representation.

**NET on the two paths:** one PROVES OUT (grow-by-reading, the +0.319 knowledge gap, CI-sep to full corpus), one is
a rigorous LOCATED NEGATIVE (recollection confidence/capture, the +0.246 gap -- real signal, effect too small to
beat the incumbent margin/fusion at the gold's resolution). The efficient program is Path 1 (proven) + targeted
reading; Path 2 is de-prioritized as a realistic lever until a stronger reliability signal exists. Both conclusions
are 100% brain-foundational and twin-controlled.

## UPDATE 2026-09-10 (W27) -- TARGETED reading of the rare tail: LOCATED NEGATIVE, and it pins the plateau as a REPRESENTATIONAL CEILING

`exp_meaning_fusion_targeted_reading_v1.py`. To push past the ~+0.26 bulk plateau, targeted the rare tail: 85
query-relevant words in the bottom quartile of accumulated evidence, gathered every line CONTAINING them from 13
OpenStax textbooks + breadth + literary readers (definition-dense natural prose, non-circular -- no dictionary/
WordNet/relations resource), reaching all 85 via 9,982 lines (+12,635 occurrences, median 102/word). RESULT: no
lift. OVERALL targeted-vs-bulk +0.0233 CI [-0.013,+0.054] (not CI-sep); RARE-WORD subset (n=112) -0.0203 CI
[-0.064,+0.061] (flat, slightly negative). LOCATED NEGATIVE -> the targeted corpus is NOT worth ingesting.

MECHANISM (why, and what it reveals). The tested vocabulary is SimLex-999 + SimVerb-3500 -- COMMON words: the
"rare" bottom quartile still has >=3,419 tokens (full-vocab token distribution p10=228, p25=754, median=2,586,
p75=8,095; the query words skew high). So (a) +102 occurrences on a ~3,000-token word is a ~3% bump = negligible,
and (b) textbook/literary context mismatches those words' GENERAL sense (hence the slightly-negative rare subset).
The tested words are ALREADY WELL-READ. Therefore the +0.26 plateau is NOT an under-exposure of the tested words --
it is a REPRESENTATIONAL CEILING of distributional co-occurrence: once a word is adequately read, more co-occurrence
(bulk OR targeted) cannot be converted into more paradigmatic IDENTITY signal. This is the same ceiling as the
SimLex WordNet-vs-distributional gap and it CONVERGES with the Path-2 understanding: the remaining loss is
REPRESENTATIONAL KNOWLEDGE, and the missing ingredient is CLEAN TAXONOMIC / is-a structure (a different knowledge
type), NOT more reading and NOT a confidence signal.

HONEST CAVEAT (scope of the negative): this refutes targeted reading only for the TESTED (common SimLex/SimVerb)
vocabulary. The live loop also grounds GENUINELY rare words (full-vocab p10=228 tokens) that are NOT in this gold;
targeted reading could still help THOSE, but it is UNMEASURABLE with SimLex/SimVerb (they do not contain them). So:
targeted reading is exhausted as a lever for the measured metric; its value for the loop's genuinely-rare tail is
unmeasured, not disproven.

REVISED PROGRAM (all three levers now rigorously resolved): PATH 1 grow-by-reading = PROVEN but BOUNDED (saturates
~+0.26 after ~1M lines; targeted extension null on the tested vocab). PATH 2 confidence/recollection = located
negative (real signal, too small). THE REMAINING LEVER past the plateau = CLEAN is-a / TAXONOMIC KNOWLEDGE (the
WordNet-ceiling 0.65 headroom on SimLex), built brain-foundationally from a CURATED non-circular source per the
knowledge north-star -- a representational addition beyond distributional co-occurrence. That is the next problem;
more co-occurrence reading and scalar confidence are both measured to be exhausted here.

## UPDATE 2026-09-10 (W28 + BF-ledger correction) -- clean is-a knowledge = LOCATED NEGATIVE; and a WordNet-morphy dependency corrected

**W28 -- CLEAN NON-CIRCULAR IS-A KNOWLEDGE CHANNEL (`exp_meaning_fusion_isa_knowledge_v1.py`): LOCATED NEGATIVE.**
Built a SELF-CONTAINED, WordNet-free/nltk-free/parser-free Hearst extractor (patterns: "X is a kind of Y", "Ys such
as X", guarded copula; confirmation gate >=2), read is-a edges from 13 OpenStax textbooks + 1.5M Simple-Wiki lines,
built a PPMI hypernym-bag GENUS channel (runtime BF: Levy-Goldberg + cosine + gain-ratio Bayes), fused with
grounded+SEQ. RESULT: is-a covers only 15% of the (common) query words (52/339; 15 covered pair-queries); adding the
genus channel does NOT lift and slightly HURTS (OVERALL -0.020 not CI-sep; covered subset -0.134), and it does NOT
beat its KNOWLEDGE-SHUFFLED twin (twin_loses=False) -- the read hypernyms are no better than shuffled on this task.
Read-is-a knowledge is too SPARSE + NOISY for the common SimLex/SimVerb vocabulary (converges with the prior
read-is-a-GROWTH hard-fails: exp_read_grow_textbook_isa_growth_v1 NO_ACCUM_BENEFIT, exp_read_grow_structure_guided
CLOSURE_AMPLIFICATION prec ~0.09). The WordNet-on-SimLex ceiling (0.65) is real headroom but is realized ONLY by a
COMPLETE, CLEAN taxonomy, which is available only CIRCULARLY (WordNet); NO non-circular source on disk (read edges,
distribution, entity-type KB) has the coverage+precision. So the clean-is-a lever is a located negative WITH the
available non-circular resources; realizing it needs a curated non-circular common-noun taxonomy (e.g. Wikidata
P279) that is not on disk -- a data-acquisition task, not a modelling one.

**BF-LEDGER CORRECTION (caught while building W28; owner "keep tabs on mathematical BF").** The pipeline-wide
lemmatizer `normalize_lemma` -> `thematic_role_labeler.lemma_word` uses **WordNet MORPHY** at runtime (and
`hdlab.conceptual_meaning` imports `nltk.corpus.wordnet`). So the earlier blanket claim "no nltk / no WordNet in the
chain" was WRONG and affects EVERY channel that lemmatizes (SEQ, grounded, genus, anchors). It is MORPHOLOGICAL ONLY
(returns base forms, NOT is-a/synonym relations) -> NON-CIRCULAR w.r.t. SimLex similarity and IDENTICAL across all
arms and controls (invalidates NO measured comparison), but it IS a WordNet-data / external-tool dependency, so the
lemma rung is BF-in-computation but NOT glass-box-in-implementation. Corrected in FULL_CHAIN_BF_AUDIT.md; the fix
(Q111) is to swap morphy for a glass-box morphology. This is now the deepest residual in the chain.

## FINAL CONCLUSION -- all levers past the fused ~41% (68%-oracle) rigorously resolved
1. Grow-by-reading (distributional): PROVEN but BOUNDED (~+0.26 plateau after ~1M lines; W20).
2. Targeted reading of the rare tail: NULL -- tested words already well-read (W27).
3. Confidence / recollection (per-query reliability): LOCATED NEGATIVE -- real signal, effect < gold resolution (W23/W25/W26).
4. Differentia channel: raises the oracle CEILING CI-sep but UNCAPTURABLE by any per-query reliability built (W24).
5. Clean read-is-a knowledge: LOCATED NEGATIVE -- too sparse/noisy, does not beat its knowledge-shuffled twin (W28).
The fully-brain-foundational live chain reaches ~41% of the brain (68% oracle). The remaining distance is a
REPRESENTATIONAL KNOWLEDGE ceiling whose only headroom (the WordNet 0.65) requires a COMPLETE CLEAN TAXONOMY that is
not available NON-CIRCULARLY on disk. The honest next move is DATA acquisition (a curated non-circular taxonomy),
not more modelling; and to make the chain fully tool-free, replace the WordNet-morphy lemmatizer with glass-box
morphology. Everything is twin-controlled, witnessed (26/26), and 100% brain-foundational in COMPUTATION (with the
morphy implementation caveat now on the ledger).

## UPDATE 2026-09-10 (W29 + W30) -- STEP 2 (curated non-circular taxonomy) + STEP 3 (glass-box lemmatizer)

**STEP 2 -- CURATED NON-CIRCULAR IS-A (ConceptNet, WordNet-EXCLUDED): DEEPER LOCATED NEGATIVE, and it explains the
whole knowledge story (`exp_meaning_fusion_isa_conceptnet_v1.py`, W29).** Used ConceptNet /r/IsA as the curated
foundation taxonomy, EXCLUDING every WordNet-sourced edge to stay non-circular (verified: 74,802 en-en IsA edges
dropped, 155,335 non-WordNet kept; 0 WordNet edges kept). This fixes read-Hearst's coverage problem: 67% of query
words covered (vs 15%), 158 covered pair-queries. RESULT: adding the genus channel HURTS -- OVERALL -0.130, covered
subset -0.184 -- and does WORSE than its KNOWLEDGE-SHUFFLED twin (twin_loses=False; real hypernyms worse than
random). MECHANISM (the deep point): a genus/is-a SIMILARITY channel scores by shared hypernyms, which groups
CO-HYPONYMS (dog/cat both -> animal) EQUALLY with synonyms -- so it actively PROMOTES the wrong-relation neighbours
that are the confusion, and shuffled hypernyms (which do not systematically promote co-hyponyms) hurt LESS. So clean
taxonomic KNOWLEDGE, added as a similarity channel, is COUNTERPRODUCTIVE for synonymy. The WordNet-0.65 ceiling was
NOT reachable by adding is-a knowledge; it reflects WordNet's fine taxonomic DISTANCE (the DIFFERENTIA / within-kind
separation), which W24 already showed raises the oracle ceiling but is UNCAPTURABLE by the fusion. This closes the
knowledge lever definitively: the genus is not the lever (it hurts), the differentia is (but is uncapturable).

**STEP 3 -- GLASS-BOX LEMMATIZER (remove the WordNet-morphy dependency): WELL-CHARACTERIZED PARTIAL
(`exp_meaning_fusion_glassbox_lemma_v1.py`, W30).** Built a glass-box, provably WordNet-free morphology (irregular
table + suffix rules + corpus lexical-familiarity + a frequency-ratio guard) to replace morphy. It is BF
(morphological decomposition, Rastle-Davis), loads ZERO WordNet, and lemmatizes regular inflection correctly
(self-test 12/12). Agreement with WordNet-morphy: 92.6% decision vocab, 89.7% corpus tokens. NOT yet lossless: it
OVER-STEMS base words (anger->ang, bring->br, brother->broth -- the last a semantic COLLISION), because distinguishing
a base word from an inflected one requires a BASE-FORM LEXICON, exactly what morphy/WordNet supplies; a
frequency-ratio guard did NOT fix it (short fragments are too frequent in a large corpus). CONCLUSION: the glass-box
DIRECTION is proven (WordNet-free, BF, correct on regulars); making it lossless needs a curated NON-WordNet
base-form word list (trivially available -- SCOWL / a citation-form frequency list -- unlike Step 2's taxonomy).
That is the spec for strategy (Q111) to land the fully tool-free lemmatizer.

## FINAL CONCLUSION (updated) -- the knowledge lever is closed; the deepest BF residual is a lemmatizer data-swap
Every knowledge/representation lever past the fused ~41% (68%-oracle) is now rigorously resolved: grow-by-reading
PROVEN-but-BOUNDED (W20); targeted reading NULL (W27); confidence/recollection LOCATED NEGATIVE (W23/25/26);
differentia raises the oracle but UNCAPTURABLE (W24); read-Hearst is-a NULL (W28); and now curated ConceptNet is-a
COUNTERPRODUCTIVE (W29) -- because genus similarity promotes co-hyponyms; the only headroom (the differentia / fine
within-kind distance) is uncapturable by any per-query reliability we can build. So the fully-BF live chain sits at
~41% of the brain (68% oracle) and the remaining distance is NOT closable by adding taxonomic knowledge as a
channel. On BF PURITY: the one standing external-tool dependency is the WordNet-MORPHY lemmatizer (pipeline-wide,
morphological-only, non-circular w.r.t. SimLex); a glass-box replacement is prototyped (W30) and needs only a
non-WordNet base-form word list to be lossless. Net: the science is closed (knowledge-as-a-channel does not help;
the differentia is the only headroom and is uncapturable), and the BF ledger is honest and current.

## UPDATE 2026-09-10 (W31/W32) -- POSITIVE: DERIVED COMPONENTIAL FEATURES are the first representation to beat our channels on identity

Owner hypothesis: componential features + hypervectors + relational significance. Built + tested rigorously.

**W31 -- ground-truth componential HV (`exp_meaning_fusion_componential_hv_v1.py`): mechanism proven, test not
powerable.** FHRR role-filler binding (hdlab.binding, PINNED) over Binder brain-based features + relational-
significance weighting; self-test confirms identical-feature concepts bind to sim 1.0 vs 0.29 differing. But Binder's
534 words overlap SimLex/SimVerb in only 4 pairs, and Binder's own similarity matrix is FEATURE-DERIVED (circular) --
so the ground-truth representation cannot be powered against an independent identity gold.

**W32 -- DERIVED componential features, FULL power (`exp_meaning_fusion_componential_hv_v2.py`): THE POSITIVE LEVER.**
Learn brain-based componential features for the whole vocab (ridge linear readout = Hebbian/delta-rule; ATL-hub
generalization, Rogers-McClelland; inputs = grounded (+) SEQ-SVD; supervised on the 243 Binder-covered scene words),
build the componential representation, test on the FULL SimLex-999 + SimVerb-3500 identity gold (n=592 pairs).
RESULT: derived componential rho **0.171** > our best fusion **0.134** > grounded **0.126** > SEQ **0.075**;
knowledge-shuffled twin **-0.111** (loses hard). And it is IDENTITY-SELECTIVE: derived identity 0.171 vs its
relatedness(Assoc) 0.158 (balanced), whereas SEQ is identity 0.075 vs relatedness 0.289 (pure relatedness). So the
componential representation captures IDENTITY not relatedness -- the differentia, working, twin-controlled, well
powered. FIRST lever in the whole investigation to beat the fused channels on identity.

HONEST CAVEATS (kept on the ledger):
- The HYPERVECTOR BINDING does NOT beat the flat componential vector (HV 0.1705 ~ flat 0.1714), and relational-
  significance ~ uniform. The lever is the COMPONENTIAL FEATURES + Binder supervision, NOT the FHRR algebra --
  because Binder features are a FLAT attribute list; binding pays off for COMPOSITIONAL/relational structure, which a
  flat attribute vector does not have. (The owner's hypervector bet is a faithful representation but adds nothing here.)
- This is the SimLex-RANKING PROXY (identity Spearman on pairs) -- C7's original metric, NOT the live-loop AUF. The
  LIVE-LOOP TRANSFER is untested (the whole problem's question), and the absolute gain is modest (+0.037 over fusion).
- EMBODIMENT-GAP MEASUREMENT (per-dim CV R2, mean 0.511): the owner was right that much IS derivable from text+grounding
  -- Taste 0.87, Smell/Vision/Human/Touch ~0.70 recoverable; Dark 0.05, Number 0.26, Disgusted 0.27 not. So the gap is
  narrower than I earlier argued: the sensory + some social/motor dims derive well; fine-perceptual + some
  abstract-emotional do not. WHY IT BEATS OUR CHANNELS: the Binder-supervised projection learns which directions of
  grounded+SEQ are IDENTITY (componential) vs RELATEDNESS, flipping SEQ's relatedness-heavy signal into an
  identity-selective one.

NET SHIFT: the knowledge-as-a-channel levers were closed (genus hurts, etc.), but a DERIVED COMPONENTIAL-FEATURE
representation -- brain-based features generalized by a Hebbian readout, supervised on curated norms -- IS a real,
twin-controlled identity lever on the ranking proxy. The decisive next step is whether it TRANSFERS to the live
grounding-coverage loop (bring derived-componential into `exp_meaning_fusion_live_coverage_v1`'s frontier).

## UPDATE 2026-09-10 (W33) -- the componential identity win does NOT transfer to the live loop (located negative, with the mechanism)

`exp_meaning_fusion_componential_live_v1.py`. Brought the derived componential channel into the LIVE anchor-pool
coverage-quality frontier (same instrument as W6/W19), fused with grounded+SEQ, twin-controlled (n_test=169, grown
SEQ, deriv mean R2=0.51). RESULT: the W32 ranking-proxy win did NOT transfer CI-separated.
- AUF-MRR: FUS_ALL(Gd+SEQ+COMP) 0.380, FUS_GD_SEQ 0.371, SEQ 0.330, TWIN 0.321, FUS_GD_COMP 0.160, GD 0.157,
  COMP 0.145, INCUMBENT 0.026.
- COMP alone (0.145) ~ grounded (0.157) LIVE -- the SimLex advantage (COMP 0.171 > grounded 0.126) VANISHED.
- COMP adds to the fusion: +0.013 CI [-0.033,+0.058] (NOT CI-sep); FUS_ALL beats its knowledge-shuffled twin
  +0.067 CI [+0.001,+0.125] (barely CI-sep, twin_loses=True) -- a WHISPER of real signal, no clean win.

MECHANISM (why it didn't transfer): the derived componential channel is a RIDGE RE-PROJECTION of grounded+SEQ, so
on the live loop -- where grounded and SEQ are ALREADY fused -- it is largely REDUNDANT with them and adds little
independent information. On SimLex pairs it helped because the supervised projection emphasized identity; live, the
fusion already captures that. Also a population reversal: on SimLex pairs SEQ=0.075/COMP=0.171, but on the live
anchor-pool SEQ=0.330/COMP=0.145 (the distributional signal dominates the live decision). The genuinely-NEW signal
would be GROUND-TRUTH brain-based features (independent of grounded+SEQ), but that is untestable here (Binder-SimLex
overlap 4 pairs; Binder similarity matrix is feature-derived=circular; ground-truth feature norms don't scale).

## FINAL SYNTHESIS -- the complete lever map (all measured, twin-controlled, BF-ledgered)
On the SimLex-ranking PROXY: the DERIVED componential-feature representation is the first real, identity-selective,
twin-controlled win over our channels (W32: 0.171 vs 0.134). On the LIVE loop it does NOT transfer CI-separated
(W33), because the derived channel is redundant with the grounded+SEQ it is built from. Combined with the earlier
map -- grow-by-reading PROVEN-but-bounded (W20); targeted reading null (W27); confidence/recollection located
negative (W23/25/26); differentia raises oracle but uncapturable (W24); read-Hearst is-a null (W28); ConceptNet
genus counterproductive (W29); componential ranking-win-but-no-live-transfer (W32/W33) -- the picture is complete
and consistent: the fully-BF live chain sits at ~41% of the brain (68% oracle), and NO signal DERIVABLE FROM OUR
CURRENT INPUTS (text + sensorimotor grounding) adds a CI-separated live lift beyond the grounded+SEQ fusion. The
one representation that carries genuinely-new identity information -- GROUND-TRUTH brain-based componential features
(independent of text/grounding) -- is real (the differentia direction, the componential ranking win) but is
DATA-BOUND: it requires high-coverage feature norms or embodied/multimodal experience that are unavailable in the
text-only sandbox. That is the honest frontier: the modelling levers are exhausted; the remaining gain is an
ACQUISITION problem (embodied/experiential or scaled curated feature data), and the deepest BF-purity residual is
the WordNet-morphy lemmatizer (glass-box replacement prototyped, W30).

## UPDATE 2026-09-10 (FRAMING RE-DERIVATION) -- we were solving the wrong shape of problem; full trace in BRAIN_SIGNAL_BF_TRACE.md

Owner (correct): "we do NOT understand what we're working on -- research how the brain does this, all the signals,
trace bottom-up through the entire chain." A deep biology drill (hdi_research, prior-work-checked) + a full
bottom-up trace (`BRAIN_SIGNAL_BF_TRACE.md`) delivered the root cause of every non-transferring lever:

THE FRAMING ERROR: we compute meaning as a NOUN (a stored vector retrieved + compared, "which is nearest?"); the
brain computes it as a VERB (a PREDICTION from the running context, corrected by PREDICTION ERROR, "what update to
my situation model does this word imply, and how well does it fit what I predicted?"). Static word-similarity is the
degenerate ZERO-CONTEXT special case. This is EXACTLY why is-a/confidence/componential all won the SimLex ranking
proxy but did NOT transfer to the live loop: the live loop's currency is prediction-error over a running model, and
a static-similarity channel produces NO prediction -> no error -> nothing to consume.

THE TRACE (15 brain signals vs our chain): we implement the BOTTOM-UP / STATIC half (lemma, spoke, cosine, gain-ratio
fusion, SDT gate) BF-faithfully, but the ENTIRE TOP-DOWN / PREDICTIVE half is ABSENT from the decision -- prediction
(5), N400 prediction-error (6), contextual sense-selection (7), semantic control (8), compositional feedback (10),
running situation-model (11), error-driven learning (15). The ATL HUB (3) is MISHANDLED (we use a spoke), and
EPISODIC one-shot grounding (12, our loop's exact job) is MISHANDLED (count-accumulation, not one-shot). DECISIVE:
the top-down organs ALREADY EXIST as landed BF modules -- `predictive_world_model`, `n400_coherence_monitor`,
`composed_hub_predictor`, `predictive_reader`, `graded_competition`, `bound_event_backbone`,
`generalized_event_knowledge`, `graded_temporal_context` -- but the SENSE-ASSIGNMENT DECISION routes through NONE of
them. The gap is ARCHITECTURAL (a noun-shaped decision that must be re-cast as a verb), not a missing static channel.

THE PATH (reuses landed organs, per full-stack-upstream): re-cast sense-assignment as a PREDICTIVE / biased-competition
computation -- running world-model (predictive_world_model/bound_event_backbone) = the top-down PRIOR; the incoming
word's coactivated senses SETTLE under that prior (graded_competition); score the PREDICTION ERROR
(n400_coherence_monitor/composed_hub_predictor); use the error as BOTH the grounding-fit and the (error-driven)
learning signal. This is the FAIR test the two HARD_FAILed STATIC context-conditioning cells never ran, and the
already-designed-but-unbuilt ANGLE_B architecture ("the meaning IS the prediction"). This supersedes the static-lever
program: STOP adding static channels; BUILD the predictive loop and consume prediction-error.

## UPDATE 2026-09-10 (W34) -- FIRST BUILD OF THE PREDICTIVE RE-CAST: prediction from the running context is a real, twin-controlled signal

`exp_meaning_fusion_predictive_grounding_v1.py`. Acting on the framing re-derivation (meaning is a VERB/prediction,
not a NOUN/lookup), built the missing top-down half at its foundation: reused the LANDED
`PredictiveWorldModel` (Rescorla-Wagner delta-rule online, err=onehot-p = the N400 error, PINNED error-driven
learning; recency-weighted predictive read-out), generalized from verbs-only to ALL content-word concepts, and ran
the brain's own CLOZE operation (self-supervised: the true next content word IS the gold) on the held-out curriculum.
RESULT (full, vocab=400, n=2933): prediction from the running context beats the no-context PRIOR (the static
no-prediction baseline) +0.0037 MRR CI [0.0027,0.0048] AND the SCRAMBLED-context twin +0.0043 CI [0.0030,0.0057],
both CI-separated; and the context LOWERS N400 surprisal by 0.040 bits CI [0.033,0.046]. prediction_works=True.

SIGNIFICANCE: after every STATIC lever failed to transfer, the PREDICTIVE re-cast produces the FIRST controlled
top-down meaning-signal -- context-prediction genuinely reduces surprise about the upcoming meaning, twin-controlled.
The framing is validated: meaning-as-prediction is a real, measurable signal the static chain entirely lacked, and it
is built from a landed BF organ (error-driven world-model).

HONEST MAGNITUDE CAVEAT: the effect is SMALL (+0.004 MRR, 0.04 of ~8.3 bits) because (a) next-content-word prediction
is intrinsically high-entropy and (b) this is the SIMPLEST predictive model -- a linear content-word event-transition
read-out, with NO situation-model entities, NO compositional role-structure, NO ATL-hub composed prediction. It is the
FLOOR of the predictive approach, not the ceiling. The richer landed organs (`composed_hub_predictor` role-structure
prediction, `bound_event_backbone`/`generalized_event_knowledge` situation-model, `graded_competition` biased
sense-selection) are the strengthening path. And this is a CLOZE/prediction test (self-supervised), NOT yet a live
grounding-coverage lift -- connecting predict->score-candidate-fit->ground on the live frontier is the next rung.

NET DIRECTION: the predictive loop is REAL (direction confirmed, twin-controlled, CI-sep) but WEAK with the simplest
model; strengthen it with the compositional/situation-model organs, then wire predict->error->ground into the live
decision. This is the productive frontier -- unlike the exhausted static-lever program.

## UPDATE 2026-09-10 (W35) -- strengthening prediction with COMPOSITIONAL structure: located negative; the honest read on "is this the real gap"

`exp_meaning_fusion_compositional_prediction_v1.py`. Tried to strengthen W34's weak flat predictor with COMPOSITIONAL
structure: predict the PATIENT from (verb, agent) via the LANDED `composed_hub_predictor` (precision-weighted
selectional preference, N400 read-out), roles from the BF `incremental_parser`, grounded hub. RESULT (n=1213, 301
verbs, pool=1387): compositional prediction does NOT add to the frequency prior -- PRIOR 0.101, COMP 0.025,
PRIOR+COMP 0.100 (add -0.0006 CI [-0.0021,+0.0008], NOT CI-sep); composition-vs-agent-shuffled-twin +0.0007 (not
CI-sep). LOCATED NEGATIVE on exact-patient ranking.

TWO predictive builds now triangulate the answer to "is this the real gap we can go after":
- W34 (flat learned transition): prediction beats the no-context prior +0.0037 MRR, CI-sep -- REAL but TINY.
- W35 (compositional selectional-preference): does NOT add to the prior -- richer structure did not strengthen it.
The honest synthesis: the predictive loop IS the real STRUCTURAL gap (the trace shows the whole top-down half is
absent; the framing error explains every static failure; W34 confirms the signal is real + twin-controlled). BUT
per-word/patient PREDICTION ACCURACY is intrinsically WEAK -- and this is CONSISTENT WITH THE BRAIN: human cloze
probabilities for content words are mostly low; per-word next-meaning prediction is genuinely high-entropy. So
optimizing "rank the next word" is likely the WRONG objective. The brain's prediction is weak per-word BY DESIGN; its
VALUE is (a) the PREDICTION ERROR as the LEARNING signal (error-driven plasticity, signal 15) and (b) SITUATION-MODEL
INTEGRATION over time (signal 11) -- NOT cloze accuracy. Neither is captured by the cloze/ranking metric; both require
wiring predict->error->ground->LEARN on the live loop with a running situation-model, which is the bigger,
un-run build.

RECOMMENDATION (honest, tempered): the predictive/error-driven direction is the correct mechanism and the real gap,
but two shallow predictors (flat transition, compositional selectional-preference) both give small/null per-word
signal -- so the payoff is UNCERTAIN and the decisive test is the harder one: wire the ERROR signal into grounding +
error-driven LEARNING over a running situation-model, and measure the LIVE grounding-coverage lift (not cloze
accuracy). That is a substantial multi-organ build (predictive_world_model + bound_event_backbone situation-state +
graded_competition + error-driven update). Odds are tempered by the weak per-word signal, but the mechanism is right
and it is the only remaining direction that addresses the actual framing error rather than the static special case.

## UPDATE 2026-09-10 (W36) -- the CROSS-MODAL REFERENT HUB (brain-true mechanism): confirms the limit is referent-grounding DATA

Owner corrected the framing (meaning is a GROUNDED REFERENT CONCEPT via cross-modal feature convergence -- the ATL
hub -- NOT a prediction; prediction is a downstream comprehension PROCESS). Built the hub, buildable version.

`exp_meaning_fusion_crossmodal_hub_v1.py` (W36). The brain's meaning = cross-modal convergence of the referent's
features; hub metric = cross-modal FEATURE-CORRELATION, not text co-occurrence (Cox-Rogers 2024). Converged the two
VOCABULARY-SCALE spokes we have -- grounded (perceptual-referent, Lancaster) + SEQ (text/thematic) -- with the one
vocabulary-scale referent-precision signal (Brysbaert CONCRETENESS, ~40k words): trust the perceptual spoke where the
referent IS perceptual (concreteness-gated modality precision; Ma/Pouget across modalities). RESULT (live frontier,
n=169): HUB (concreteness-gated) 0.364 vs FUS_equal 0.371 -- does NOT beat the ungated fusion (+0.0022, not CI-sep;
a whisper over its concreteness-shuffled twin +0.023, not CI-sep). LOCATED NEGATIVE.

THE RICHER REFERENT SPOKES ARE DATA-BLOCKED (confirmed from the data side): the only per-word VISUAL referent features
on disk are CLIP embeddings for ~21 QuickDraw words (cat/dog/apple...), with NO synonym pairs and ~0 SimLex overlap;
Binder componential features cover ~534 words (10% of the query vocab). So the referent-feature modalities that would
make the hub brain-faithful exist only at demo coverage.

## CONVERGED FINAL CONCLUSION -- the limit is referent-grounding DATA (embodiment), not modelling
Every direction now converges on ONE cause. The brain grounds meaning in the MULTIMODAL EXPERIENCE OF REFERENTS
(cross-modal feature convergence, the hub). Our system has: TEXT co-occurrence (one thematic spoke) + a THIN
sensorimotor NORM-proxy (Lancaster = the perceptual spoke, our single best channel) + a vocabulary-scale concreteness
scalar. The RICHER referent modalities (vision ~21w, componential ~534w) are demo-coverage. Therefore:
- grounded (Lancaster) is our best channel because it is the closest thing to referent experience we have;
- every TEXT recombination plateaus (SEQ, is-a, prediction, componential-derived) -- same impoverished source;
- the concreteness-gated cross-modal hub built from the two vocab-scale spokes does NOT beat their ungated fusion;
- so grounded+SEQ (~41-44% of the brain, 68% oracle) IS the best cross-modal referent hub the AVAILABLE DATA supports.
PREDICTION was a wrong turn (a downstream process, not the substance of meaning; W34/W35 measured it real-but-weak).
The frontier is now unambiguous and it is a DATA-ACQUISITION one: vocabulary-scale REFERENT-FEATURE data (perceptual/
visual via CLIP-at-ingest over the full vocab -- the infra exists in exp_visual_grounding_coherence_v1; and/or scaled
componential norms). That is a FOUNDATION data-build (offline, admissible, owner-authorized), NOT a model to invent
in the text-only sandbox. This is the symbol-grounding/embodiment limit, confirmed from the mechanism side (hub needs
cross-modal referent features), the modelling side (every text-derived lever exhausted), and the data side (referent
modalities are demo-coverage).

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

## UPDATE 2026-09-10 (W37) -- THE REFERENT-DATA BUILD: a REAL but MODEST pure-visual (DINOv2) referent lever, and the coverage bound

Owner: "foundational data build -- make it happen ... brain foundationally, and do it right, not easy." Item 1 of
PLAN_referent_grounding_data_build. Four literature drills (R1-R4, 2026-09-10) fixed the design (DESIGN_visual_referent_hub):
the ATL hub is a CORRELATED SHARED SUBSPACE not concatenation (Cox-Rogers 2024) with per-concept precision-weighting
(Ma-Pouget/Ernst-Banks); the most faithful, NON-text-contaminated visual transducer is DINOv2 (vision-only; CLIP's
image embeds are caption-trained and would re-measure text -- the W33 redundancy trap; Raugel 2024/Conwell 2024/
Konkle-Alvarez 2022); the image source is THINGS natural photos (Hebart, R3; photos beat sketches for a photo-trained
encoder); the visual-spoke precision gate is Lancaster Visual.mean (Connell-Lynott strongest-sense; Fernandino 2015).

STEP A (`exp_meaning_fusion_visual_referent_ingest_v1.py`): DINOv2-base + CLIP (diagnostic) frozen-at-ingest over
1854 THINGS CC0 photos -> per-concept referent vectors (768-d / 512-d), 0 missing. Torchvision-free glass-box
preprocessing; resumable/checkpointed. CLIP touched ONLY at ingest; no external model at runtime (the invariant).

STEP B/C (`exp_meaning_fusion_visual_referent_hub_v1.py`): the cross-modal hub + four gates on the INDEPENDENT
THINGS-behavior gold (SPoSE 66-d, 4.7M human odd-one-out judgments = human PERCEPTUAL similarity; non-circular w.r.t.
SimLex and w.r.t. our channels). TEXT spoke = SEQ directional-PPMI built for the concepts on 1M Simple-Wiki lines,
TruncatedSVD-densified to 256-d (LSA-style, phase-diagram move). n=1438 concepts (single-token, all channels present).
Two seeds, identical results:

- G1 (non-redundancy): DINOv2-TEXT RSA 0.029 vs CLIP-TEXT 0.080 -> DINOv2 is measurably LESS text-redundant. The
  choice to use DINOv2 over CLIP was load-bearing: CLIP's "visual" signal is ~3x more entangled with text.
- G2 (THE POWERED CORE, twin-controlled): the pure-visual spoke ADDS +0.0177 unique R2 over {text, grounded} in
  predicting human similarity, CI [0.0142, 0.0229] (CI-separated positive), shuffled-visual twin +0.0000 (twin
  losing), seed-stable. So a genuinely NEW, non-text modality carries real meaning-structure that text+grounded miss.
- G3 (fusion form): the correlated-subspace hub RSA 0.287 beats flat concatenation 0.192 (Cox-Rogers form helps);
  the Visual.mean precision gate is ~neutral here (hub 0.287 vs shuffled-precision twin 0.283-0.285). HONEST: the
  fused hub (0.287) is BELOW grounded-alone (0.407) -- equal-weighting dilutes the strong channel; a net fused win
  needs full per-spoke reliability-weighting, not just gating the visual spoke.
- G4 (semantic gold, honest): SimLex+SimVerb visual-covered pairs = 18 -> UNDERPOWERED (as pre-measured: only 23/1349
  pooled pairs have both words photograph-able as THINGS concepts). Directional only: on those 18 pairs visual
  predicts SimLex similarity better than text (rho 0.45 vs 0.30), but n=18 is far below the ~30-50 for a CI.

vs-BRAIN / channel ladder (RSA vs human perceptual similarity, n=1438): incumbent-text 0.09 -> visual(DINOv2) 0.17
-> grounded(Lancaster) 0.41 -> CLIP 0.43 (text-contaminated). Grounded/Lancaster is the strongest single channel;
visual is an ADDITIVE +0.018-unique contributor, not a dominant lever.

CONCLUSION (refines the prior data-ceiling, does not overturn it). The referent-data lever is REAL, not zero: real
visual referent experience adds CI-separated, twin-controlled meaning-structure that every prior text-derived lever
(all exhausted, W20-W36) could not reach. BUT it is (1) SMALL (~1.8% unique variance), (2) demonstrated on PERCEPTUAL
similarity -- where a visual signal is expected to help -- not on SEMANTIC synonymy, and (3) the semantic-synonymy
payoff (the problem's actual SimLex/SimVerb target) stays DATA-COVERAGE-BOUND: too few meanings are photograph-able
AND in the synonymy gold to power it. So the honest refined answer to "does real referent grounding lift meaning
where text-derived signals could not": on perceptual similarity YES (small, CI-sep, twin-losing); on the semantic
synonymy target, the lever is real but the available referent-data coverage is too thin to realize it -- the ceiling
for THAT gold is data-coverage-bound, now measured, not modelling.

BF status: every rung BF/BF_SPIRIT. DINOv2 = frozen foundation transducer at ingest (vision-only ventral-stream/IT
stand-in, no text), analogous to the Lancaster/Brysbaert curated norms; hub = Cox-Rogers correlated subspace +
Ma-Pouget precision (PINNED computations); precision gate = Lancaster Visual.mean (curated norm); cosine readout
(Georgopoulos). NO external model at runtime. THINGS/SPoSE = curated foundation assets, non-circular w.r.t. SimLex.

SUBSTRATE INCORPORATION MANIFEST (W37): INCORPORATE as a DURABLE finding -- the referent-data lever is real but
small/perceptual/coverage-bound; DO NOT re-tread "add more text-derived channels for the semantic gap" (exhausted)
NOR "the visual modality is useless" (refuted: +0.018 CI-sep). AS-DURABLE-NEGATIVE: DINOv2/CLIP/THINGS at INGEST are
admissible foundation assets, but a visual referent spoke is NOT a headline synonymy lever at the available coverage.
DO-NOT: do not wire a runtime vision model; do not claim a SimLex synonymy win from this (underpowered). Open next
(if pursued): full per-spoke reliability-weighted fusion (so the fused hub beats grounded-alone), and whether scaling
photograph-able coverage (the full password-protected THINGS set / ecoset) materially raises the ~18-pair semantic
overlap -- likely still bounded, since abstract/verb synonymy is structurally non-visual.

## UPDATE 2026-09-10 (W38) -- HONED FUSION (recovery-gated precision) + the POWERED SEMANTIC gold: vision adds to SEMANTIC similarity, and the fusion no longer dilutes

Owner: "hone what we do on 1 (fusion) and in particular 2 (expansion); do it right not easy." Four research drills
(E1-E4, 2026-09-10) sharpened both axes; two are landed here (v2), the rest scoped for Phase 2.

WHY v1's fusion was wrong (E4 / precision-weighted-fusion drill). v1 fused via SVD over the standardized concatenated
spokes -- which maximizes SHARED CROSS-SPOKE COVARIANCE, not precision-weighted agreement on the target, so the two
weak, mutually-noisy spokes (text 0.09, visual 0.16) DILUTED the strong one (grounded 0.41): v1 fused hub 0.29 < 0.41.
This also violates the Ernst-Banks 2002 / Ma-Beck-Latham-Pouget 2006 guarantee that a precision-weighted combination is
never worse than the best single cue.

THE FIX (v2, `exp_meaning_fusion_visual_referent_hub_v2.py`) -- recovery-gated, per-concept precision-weighted
convergent-cue fusion, reusing the PROVEN hdlab.gated_fusion recovery-gate PATTERN (no hdlab write): per-pair
reliability-weighted similarity fused across spokes, with the fusion weights grid-searched on a held-out split over a
grid that INCLUDES the best-single-channel one-hot -- so fusion is NEVER worse than the strongest channel BY
CONSTRUCTION. Per-concept, per-spoke precision (oracle-free, E3 estimators): TEXT = log1p(read token count)
(frequency/evidence); GROUNDED = 1/mean(Lancaster modality SD) (rating agreement, Lynott-Connell); VISUAL = Lancaster
Visual.mean perceptual-strength PROXY (Phase-2 replaces it with within-concept DINOv2 exemplar DISPERSION -- the
E1/E3 convergence: the photo-set's spread IS the visual reliability).

G5 (fusion fix, THINGS-behavior perceptual gold, concept train/test split, two seeds): recovery-gated precision fusion
test RSA 0.461 vs grounded-alone 0.415 (seed1) / 0.426 (seed2); no_dilution=True, improves=True both seeds; selected
weights dropped/down-weighted noisy text and combined grounded+visual. So the fusion now REALIZES the visual signal
(+0.035-0.046 over grounded) instead of diluting it -- the v1 bug is fixed, brain-foundationally and by construction.

G6 (THE POWERED SEMANTIC TEST -- the SimLex 18-pair coverage bound, bypassed). Added MEN (Bruni-Tran-Baroni 2014):
391 pairs have both words in our concept set (vs SimLex/SimVerb ~18) -- a ~17x more powered, non-circular semantic gold
(human relatedness judgments). Per-channel Spearman vs MEN human similarity: text 0.597 > grounded 0.527 > visual 0.422
(text is the strongest single channel for semantic RELATEDNESS, as expected -- co-occurrence captures relatedness).
DECISIVE: the visual spoke ADDS +0.0437 unique R2 over {text, grounded} in predicting MEN similarity, CI [0.016, 0.082]
(CI-separated positive), shuffled-visual twin +0.001 (twin losing), seed-stable. So on a powered SEMANTIC gold, real
visual referent experience adds meaning-similarity signal that text+grounded miss -- LARGER than the perceptual
additive (+0.044 vs +0.018, W37). This REFINES the W37 "perceptual-not-semantic" caveat: vision DOES contribute to
semantic similarity on concrete nouns. (HONEST bounds: MEN is relatedness-leaning, not strict SimLex synonymy -- report
as a distinct claim; strict-synonymy SimLex coverage stays ~18 pairs; text remains the strongest single semantic channel.)

NET. Both levers the owner asked to hone are advanced: (1) the fusion is fixed (recovery-gated precision -> fusion beats
the best single channel, cannot dilute by construction); (2) the expansion is honed -- the specificity lever is a
CONCRETE-NOUN-RICH GOLD (MEN, landed; the depictable ceiling on SimLex is gold-construction-bound at ~107 pairs, not
image-coverage-bound), the volume lever is ~20-30 exemplars/concept keeping exemplar-variance as the visual precision
(Phase 2). Still BF/BF_SPIRIT at every rung (frozen transducer at ingest; precision-weighted convergent-cue fusion;
curated non-circular golds). Phase 2 (next): full-THINGS multi-exemplar re-embed -> exemplar dispersion as the real
visual precision (replacing the Visual.mean proxy), which should sharpen the fusion and the visual precision further.

SUBSTRATE INCORPORATION MANIFEST (W38 update): INCORPORATE -- (a) the recovery-gated precision fusion is the correct
combiner (fusion >= best single by construction); DO-NOT re-use SVD-over-concat as a fusion step (it dilutes). (b) MEN
is the powered concrete-noun semantic gold to use alongside SimLex. (c) vision adds to semantic similarity on concrete
nouns (powered, CI-sep) -- update the durable finding from "perceptual-only" to "perceptual + concrete-noun-semantic".
AS-DURABLE-NEGATIVE: strict-synonymy (SimLex) visual coverage is gold-construction-bound (~18-107 pairs); the verb/
abstract wall is categorical. DO-NOT: no runtime vision model; MEN-relatedness != strict-similarity (keep the claims distinct).

## UPDATE 2026-09-11 (W39) -- PHASE 2 the VOLUME + real-precision upgrade: the denoised multi-exemplar centroid ~DOUBLES the visual referent's semantic contribution

Research E1 (exemplar count) + E3 (precision) converged on one quantity: a concept's photo-set SPREAD is its visual
reliability, and ~20-30 exemplars is the diminishing-returns elbow for a stable centroid. v1/v2 used ONE CC0 photo per
concept -- noise-limited. Phase 2 re-embedded the FULL password-protected THINGS set (26,107 photos, mean 14.0/concept,
capped at 20) with frozen DINOv2 -> per-concept CENTROID (denoised referent) + DISPERSION (mean cosine distance of
exemplars to the centroid = per-concept visual precision). `exp_meaning_fusion_visual_referent_ingest_v2.py`
(resumable/checkpointed, torchvision-free); `hub_v2 --multi` uses 1/dispersion as the visual precision (replacing the
Lancaster Visual.mean proxy).

DISPERSION is a valid reliability signal (face-validity): tightest/most-reliable = sonogram, koala, anteater, revolver,
sewing_machine, submarine (visually canonical); loosest/least-reliable = painting, butterfly, dog, plant, bird, flower
(huge within-category variance -- many breeds/species). range [0.037, 0.622], median 0.218.

RESULT (two seeds, identical; n=1438 concepts):
| metric | v2 single-photo (Visual.mean proxy) | v3 multi (~14 photos, dispersion precision) |
|---|---|---|
| visual RSA vs perceptual gold (THINGS-behavior) | 0.163 | 0.272 (+67%) |
| visual rho vs MEN semantic | 0.422 | 0.595 (~tied with text 0.597, above grounded 0.527) |
| visual ADDS over text+grounded on MEN (R2) | +0.044 CI [0.016,0.082] | +0.086 CI [0.042,0.137], twin +0.001, twin-losing |
| G5 recovery-gated fusion vs grounded-alone | 0.461 > 0.415 | 0.436-0.449 > 0.415-0.426 (no dilution both seeds) |

INTERPRETATION. The denoised multi-exemplar centroid roughly DOUBLES the visual referent's UNIQUE SEMANTIC contribution
over text+grounded (+0.044 -> +0.086, CI-separated, twin-losing) and lifts visual-alone semantic prediction to parity
with the text channel. The single-photo v1/v2 substantially UNDER-STATED the referent lever -- it was noise-limited, not
signal-limited. The G6 additive gain is driven by the denoised CENTROID (the volume lever, E1); the DISPERSION precision
is the secondary refinement in the G5 fusion weighting (which stays non-diluting). On the PERCEPTUAL gold the fused
number is ~flat because grounded already dominates perception; the win is on SEMANTIC similarity.

BF status unchanged: frozen DINOv2 transducer at ingest (vision-only ventral-stream/IT stand-in); multi-exemplar
centroid = prototype abstraction (Posner-Keele/Rosch); dispersion-as-precision = reliability-weighting (Ma-Pouget/
Ernst-Banks; Shi-Jain probabilistic embeddings); recovery-gated convergent-cue fusion. THINGS = curated foundation asset
(research/non-commercial), non-circular w.r.t. the golds.

SUBSTRATE INCORPORATION MANIFEST (W39 update): INCORPORATE -- (a) the referent visual vector MUST be a multi-exemplar
centroid (>=~12-14 photos), not a single image (single-photo halves the semantic lever); (b) exemplar dispersion is the
per-concept visual precision. UPDATE the durable finding: the referent-data lever, once denoised by volume, is real AND
materially larger (visual ~tied with text on concrete-noun semantic relatedness). AS-DURABLE-NEGATIVE unchanged: strict-
synonymy SimLex coverage is gold-construction-bound; verb/abstract wall is categorical. DO-NOT: no runtime vision model.

## UPDATE 2026-09-11 (W39 gap-closure, end-of-arc gate) -- the FUSED hub beats its best single channel (whole > part), and the dispersion-precision is an honest neutral

Owner end-of-arc directive: "how did we do vs the goal? ... research all optimizations and implement, BF and right,
not easy, address loose ends." Self-assessment found two gaps in the completeness of the claim; both now closed
(added as G7 to hub_v2, twin/split-controlled, 3 seeds).

GAP 1 (was: the fusion's payoff on the SEMANTIC gold was unmeasured -- only the additive R2 of visual, and no-dilution
on the PERCEPTUAL gold). CLOSED, POSITIVE: on MEN (held-out pair split), the recovery-gated FUSED hub {text, grounded,
visual} beats the BEST SINGLE channel CI-separated on all 3 seeds -- multi fused 0.72 vs best-single 0.64 (fused-minus-
best CI [0.007,0.144] across seeds, always > 0); single-photo fused 0.69 vs 0.60. So the whole system beats its best
part on the powered semantic gold, and the recovery gate chooses the MOST weight on the (denoised) visual spoke (0.5).
This is the headline the additive-R2 alone did not give.

GAP 2 (was: the dispersion-precision's specific contribution was not isolated -- G6 additive used the raw centroid).
CLOSED, HONEST NEGATIVE: dispersion-precision does NOT beat UNIFORM precision (multi 0.723 vs 0.751; single similar),
consistent on all 3 seeds. So E3's per-concept precision-weighting -- though theoretically motivated (Ma-Pouget/Shi-Jain)
and behaving sensibly (dog/flower loose, submarine/koala tight) -- does NOT empirically improve the fusion beyond the
denoised centroid on this gold. The lever that mattered was VOLUME (E1: the multi-exemplar centroid), not the
dispersion-precision (E3). The recovery gate still guarantees no harm (fusion > best single regardless), so keeping the
precision term is neutral-safe, but the honest attribution is: the referent win comes from denoising by volume.

NET (end-of-arc). The claim is now complete and stress-tested: (1) a real, non-text visual referent modality adds
meaning-similarity signal text+grounded miss, on BOTH perceptual (THINGS-behavior) and semantic (MEN) golds, CI-sep,
twin-losing, seed-stable; (2) denoised by ~14-exemplar volume it roughly DOUBLES and reaches text-parity semantically;
(3) the recovery-gated precision fusion makes the FUSED hub beat its best single channel (whole > part) CI-sep, and
cannot dilute by construction; (4) honest bounds: dispersion-precision is neutral (volume was the lever); strict-
synonymy SimLex coverage stays gold-construction-bound (~18 pairs); the verb/abstract wall is categorical. Remaining
identified-but-not-built levers (diminishing / future): fill the ~116 missing concrete nouns (ecoset/OpenImages) to
widen MEN coverage further; a niche SOUND spoke (~55 auditory-strong words); the learned shared-latent (autoencoder) hub
(R1 Stage-A) vs the current weighted-sum combiner. These are optimizations beyond the now-complete core claim.
