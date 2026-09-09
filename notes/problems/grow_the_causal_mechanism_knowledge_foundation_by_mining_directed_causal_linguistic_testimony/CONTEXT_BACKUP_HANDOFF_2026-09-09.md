# CONTEXT BACKUP / HANDOFF -- causal-mechanism knowledge foundation (2026-09-09)

**READ THIS FIRST after compaction.** Single recovery entry point. Slug:
`grow_the_causal_mechanism_knowledge_foundation_by_mining_directed_causal_linguistic_testimony`.
Solver session (opus 4.8). This traces the whole arc + the CURRENT signal chain + every artifact + exactly where to pick up.

---
## 0. SCOPE / INVARIANTS (do not violate)
- WRITE ONLY: `experiments/`, `verification/`, and THIS folder. NOT `hdlab/` (strategy is sole writer, board Q111),
  NOT `preregs/**`, NOT `arm_key*`. `data/foundation/` READ-ONLY. `data/` else is writable (cell outputs).
- NO external LLM at inference (THE invariant). spaCy/GLUCOSE/MAVEN not brain-foundational. Offline static
  foundation assets (WordNet/FrameNet/Lancaster norms/open MODERN gold) ARE admissible.
- If a tool call is DENIED: STOP and report verbatim (do not retry a variant). `rm` is denied -- use cap-specific
  filenames, not deletion.
- Integrate only on `owner_verdict: DONE`. Strategic forks -> PROSE, never AskUserQuestion. Only stop/kill THIS
  session's spawns. Bash cwd RESETS on background runs -> prefix `cd /c/AI/hd-instrument &&`. Cap threads to 4
  (`OMP_NUM_THREADS=4 ...`); cells already `setdefault` 3.
- A concurrent session is managing `data/bf_status_registry.jsonl` + the registry-driven `verification/test_bf_status_tags.py`.
  Do NOT write that registry (two-writers lost-update hazard). My cells are honestly tagged for them to register.

## 1. STATUS IN ONE PARAGRAPH
Problem status = PARTIAL (SOLVED.md; owner has NOT marked DONE -- WIP). This session did NOT chase a number; it
answered the owner's escalating questions: (a) fully unlock the causal signal, (b) determine what signal is missing
and why, (c) implement 100% brain-foundational all the way up, (d) VERIFY every organ (don't assume), (e) make BF
status apparent, (f) build the grounded-simulation sign source. NET RESULT: the ENTIRE upstream causal-reading chain
is now verified-BF or composed-from-verified-BF at operation/math precision, and the problem is reduced to ONE
precisely-isolated, proven frontier -- a **grounded-experience SIGNED-QUANTITY source** (does an event drive quantity
X up/down). FIVE candidate sign sources were built and ALL fail the more/less discrimination for the SAME root reason
(no bound signed-quantity representation grounded in experience; Causal Hierarchy Theorem: text = rung-1). The
counterfactual do-simulation machinery (`causal_reasoner.signed_effect`) is BF and READY to consume a signed edge the
instant a grounded-experience sign source exists.

## 2. THE SIGNAL CHAIN, TRACED (final component -> up), with BF status + where signal dies
The END component = `hdlab.predictive_world_model.causal_antecedent` (counterfactual-necessity reader). BF in FORM
(Gerstenberg CSM / Trabasso / Hesslow). It needs a DIRECTED cause->effect production strength.
| stage | organ | signal | BF verdict | where signal dies |
|---|---|---|---|---|
| tokenize | regex | tokens | not-BF (mechanical) | - |
| POS | `pos_tagger`+`perceptron` | UPOS | **NOT_BF** | frozen supervised avg-perceptron; hard Viterbi discards marginals; SEPARATE from parse |
| parse | `arc_parser` | heads | **NOT_BF** | arc-factored BATCH, frozen, greedy hard-decode discards Matrix-Tree marginals; "route around" |
| parse (BF alt, OFF) | `incremental_parser`+`predictive_reader` | incremental heads + surprisal | BF_SPIRIT | genuine (left-corner Now-or-Never; -logP+Friston precision) but DEFAULT-OFF islands |
| roles | `graded_role_assigner` | agent/patient | BF_SPIRIT | Competition-Model op pinned BUT `DEFAULT_VALIDITIES` gold-FITTED+adopted |
| binding | `event_bundle`/`role_slot_summarizer` | bound (role,filler) | **BF** | genuine FHRR bind+bundle+unbind+cleanup, non-fitted keys (latent sign() deviation only) |
| concept grain | my `span_concepts` | bag of lemmas | **NOT_BF** | BAG, not bound participant-state (info-losing; Frankland-Greene lmSTC) |
| grounded magnitude | `fractional_power_encoding` | Weber log-ratio | **BF** | genuine Nieder/Plate log-Gaussian phasor code |
| grounded magnitude | `scalar_adjective_operation` | signed oriented pos | BF_SPIRIT | real signed more/less via oriented_position BUT graded axis = markedness/rarity; 3/4 dims GloVe not Lancaster |
| grounded read (deployed) | `grounded_similarity`/`sensorimotor_spoke` | similarity | BF_SPIRIT | capped-cosine read discards magnitudes ("no cosine in the brain") |
| causal store (mine) | `exp_causal_testimony_mine` cs_pmi | assoc PMI | BF_SPIRIT | mined directed testimony = structural PRIOR; cs_pmi = rung-1 association |
| force typing | `force_dynamics_lexicon` | CAUSE/ENABLE/PREVENT | BF_SPIRIT | Wolff truth-table pinned; inputs = FrameNet lookup + hand lists; ~16% coverage (physical only) |
| harm/help | `force_dynamics_valence` | harm/help | **NOT_BF** | verb-list membership dressed as force dynamics; retired test-fitted list |
| forward model | `predictive_world_model` | surprisal/necessity | BF_SPIRIT | counterfactual OP faithful BUT over associative single-layer model on BARE UNBOUND verb bag |
| necessity SIM | `causal_reasoner.signed_effect` | do()+signed propagation | BF_SPIRIT (op) | **the more/less do-sim EXISTS + is BF; but NO organ supplies the +-1 SIGN -> all live edges +1 -> "never less"** |
| **sign source** | (none BF) | promote/inhibit | **THE FRONTIER** | **the one missing BF component -- see sec 4** |
**Where the signal dies (headline):** the counterfactual-necessity reader is BF but fed an ASSOCIATIVE forward model
over a BAG of bare concepts; the do-simulation is BF but has NO signed-edge source. Position-confounded gold (TMW 0.91)
hid the whole thing. On-disk: 54-59% of gold causes share ZERO lexical overlap with the effect.

## 3. THE ARC (what was done, in order)
1. Reproduced the wall: adjacency-W causal-antecedent selection AT CHANCE (TMW answerable non-adj n=273: full AUC
   0.495, zero-overlap 0.489). TMW is POSITION-CONFOUNDED (nearest-non-adjacent 0.91) -> banned as load-bearing.
2. Built the causal-testimony MINER (`exp_causal_testimony_mine_v1`): connectives/causatives/counterfactuals ->
   1.29M directed edges (161k causal sents, 13 textbooks + simplewiki); gold-link coverage 5%->50%. **Coverage is NOT
   the wall.**
3. TRAP-PROOF intrinsic win: on held-out testimony (n=10164), mined DIRECTION beats same-corpus co-occurrence
   **0.609 vs 0.513, +0.097 CI-sep** (twin loses +0.234). => testimony recovers causal DIRECTION association can't
   (Pearl asymmetry). This is the banked constructive positive.
4. Deep research (many drills; see RESEARCH_KNOWLEDGE_MAP + PATH_TO_SOLVED_RESEARCH): the missing signal is the rung-2
   counterfactual-NECESSITY SIMULATION; text is rung-1 (Causal Hierarchy Theorem, Bareinboim 2022) + biased by the
   abnormality-selection mechanism (Hilton-Slugoski/Gordon-Van Durme) that DEFINES causal selection. Brief corrections
   recorded: "54/73/34" garbled (real=54-59% zero-overlap); Feng-2021 mis-cited as amodal (it argues the opposite).
5. Acquired POSITION-BALANCED golds (`fetch_causal_selection_gold_v1`): COPA (1000), e-CARE (dev 2122, MIT),
   BCOPA-CE (1000, direction-sensitive). All offline, provenance-pinned.
6. Position-free selection (COPA): causal_directed 0.538 beats lexical 0.485 (+0.053 CI-sep) + twin 0.501 (+0.037);
   e-CARE loses to strong lexical 0.588. Combination (held-out tuned): ties twin-combination at power. Direction not
   load-bearing on 2AFC (task doesn't need it). Absolute ~0.54 << non-LLM mined-KB ceiling 0.70 (scale gap).
7. Directional-score UPGRADE (`exp_causal_directional_score`): asym/cond beat cs_pmi on direction golds (+0.008-0.023
   CI-sep). Real but modest (rung-1 ceiling).
8. VERIFIED every organ at operation/math precision (4 audit agents + 2 more) -> VERIFIED_BF_LEDGER.md.
9. BF-STATUS TAG convention (greppable `__bf_status__`) + checker; concurrent session formalized it into a registry.
10. Composed verified-BF `causal_reasoner.signed_effect` -> isolated the frontier to the SIGNED-EDGE SOURCE.
11. Built + tested FIVE sign sources -- all fail more/less (sec 4).

## 4. THE FIVE SIGN-SOURCE ATTEMPTS (all fail the WIQA more/less, SAME root cause)
Instrument: WIQA (Tandon 2019) -- interventional "suppose X happens -> effect on Y" = P(Y|do(X)); more/less/no-effect;
association at chance on more/less by construction; process domain matches the textbook store.
| # | source | cell | more/less result | why it fails |
|---|---|---|---|---|
| 1 | Wolff force-dynamics | `exp_causal_wiqa_bfsim_v1` | neg-edges **0.0%** | PREVENT fires on 0 process steps (process language != prevent/block) |
| 2 | marker-mined signed store | `exp_causal_signed_wiqa_v1` | **0.34** (below chance) | heuristic-marker signs = noise |
| 3 | grounded increase/decrease directional (LEARNED, delta-rule) | `exp_causal_quantity_dynamics_v1` | full n=5005: **0.457**, TIES random twin **+0.000**; neg-edges 4.1% | learned grounded signs add nothing over random on specific process |
| 4 | grounded QP simulation (Forbus + grounded matching) | `exp_causal_qp_simulation_v1` | **0.255** (below chance) | grounded matching mis-aligns; influence signs still noise |
| 5 | entropy / GEK (`generalized_event_knowledge`, `predictive_world_model`) | (analysis) | DIRECTIONLESS | keys on concept lemmas with "more"/"less" DROPPED as stop-words -> "more clouds"=="less clouds"; entropy = confidence over concept-IDENTITY, no signed-quantity rep |
3-way WIQA gains (+0.13 over majority) are ALL from reachability (the random-sign twin matches). The SIGN is the wall.

## 5. THE FRONTIER (the one remaining non-composable BF component) + WHY IT'S BF
**A grounded-experience SIGNED-QUANTITY source**: a mechanism that determines whether an event drives quantity X UP or
DOWN, from a bound signed-quantity representation grounded in EXPERIENCE of the dynamics -- an intuitive-physics /
action-conditioned forward model (Battaglia intuitive physics; Wolpert forward models = P(sensation|do(command)); the
generative world-model over grounded magnitudes; predictive coding). BF because: quantity/magnitude is amodal parietal
(ATOM/Nieder = our BF `fractional_power_encoding`), directional; the coupling sign is learned from grounded interaction
(Rescorla-Wagner). WHY text can't supply it: Causal Hierarchy Theorem (rung-1 can't determine rung-2) + the corpus is
generated BY the abnormality-selection mechanism. HONEST: this is a major research program (grounded experience of
dynamics), NOT a cell, and NOT derivable from a text + static-perceptual-norm substrate. Do NOT build a 6th
text-derived sign source -- proven to fail for the same reason.

## 6. ARTIFACTS (all mine, this session)
EXPERIMENT CELLS (experiments/):
- `exp_causal_testimony_baseline_v1` -- reproduces the adjacency-W chance wall (BF_SPIRIT-adjacent measurement).
- `exp_causal_testimony_mine_v1` -- THE MINER: 1.29M directed edges -> `data/exp_causal_testimony_mine_v1/store_v1.json`. [BF_SPIRIT]
- `exp_causal_testimony_eval_v1` -- head-to-head causal vs adjacency vs twin on TMW.
- `exp_causal_testimony_heldout_v1` -- trap-proof held-out DIRECTION test (the +0.097 constructive win).
- `fetch_causal_selection_gold_v1` -- pinned fetch: COPA + e-CARE + BCOPA-CE -> data/corpora/{copa,ecare,bcopa_ce}/.
- `exp_causal_selection_ecare_copa_v1` -- position-free 2AFC (COPA win, e-CARE lexical-dominated).
- `exp_causal_selection_framegrain_v1` -- frame-lookup on bag store (doesn't help).
- `exp_causal_selection_combined_v1` -- association+causal combination, held-out tuned (ties twin at power).
- `exp_causal_directional_score_v1` -- UPGRADE: asym/cond/condXasym beat PMI on direction golds.
- `exp_causal_direction_ecare_v1` -- direction test on e-CARE gold pairs (assoc=0.5 by construction).
- `exp_causal_bcopa_ce_v1` -- BCOPA-CE (floors at chance by construction; causal_directed +0.022 vs blind covered +0.035).
- `exp_causal_wiqa_dosim_v1` -- rung-2 do-sim v1 (reachability + process-sim; ties assoc).
- `exp_causal_signed_wiqa_v1` -- signed do-propagation (crude; below chance). [NOT_BF]
- `exp_causal_situation_sim_v1` -- full-stack situation-sim prototype (reachability 0.703 but sign fails). [NOT_BF]
- `exp_causal_wiqa_bfsim_v1` -- composes causal_reasoner.signed_effect + Wolff signs (neg-edges 0%). [BF_SPIRIT]
- `exp_causal_quantity_dynamics_v1` -- grounded increase/decrease LEARNED sign source (ties random twin). [BF_SPIRIT]
- `exp_causal_qp_simulation_v1` -- grounded Forbus QP simulation (below chance). [NOT_BF]
- (note: `exp_causal_selection_instrument_diagnostic_v1` present -- NOT confirmed mine; verify owner before touching.)
WITNESSES (verification/), all GREEN:
- `test_causal_testimony_foundation.py` (6/6) -- the intrinsic direction win + the wall + honest bounds.
- `test_causal_selection_positionfree.py` (5/5) -- COPA position-free win + e-CARE limit + scale ceiling.
- `test_causal_direction_signal.py` (4/4) -- direction signal on direction-sensitive golds (BCOPA-CE/e-CARE).
- `test_bf_status_tags.py` -- registry-driven (concurrent session owns the registry); positive-control self-check.
NOTES (this folder) -- the detailed record:
- `SOLVED.md` -- THE submission (PARTIAL): frontmatter (bar/result/floor/controls/reverify) + deep analysis +
  PERFORMANCE-PUSH ATTEMPTS + PHASE A/B + AUDIT UPDATES + TLDR/QUESTIONS/NEXT STEPS.
- `VERIFIED_BF_LEDGER.md` -- **the most current + comprehensive**: per-organ BF verdicts (op/math), the tagging
  convention + exact per-organ hdlab tag spec, the composition result, the QP + entropy unified conclusion.
- `UPSTREAM_BF_AUDIT.md` -- the operation/math audit table + why the sign fails.
- `RESEARCH_KNOWLEDGE_MAP.md` -- the brain-foundational research synthesis (testimony/connectives/assoc-vs-causation/
  online-use) with citations + PINNED/CONTESTED.
- `PATH_TO_SOLVED_RESEARCH.md` -- the Phase A-D research SPECs (instruments, state-grain).
- `DEAD_ENDS_AND_SIGNAL_MAP.md` -- the 3-parent graveyard + how this lever differs.

## 7. KEY NUMBERS (landed)
- Adjacency-W causal-antecedent selection: AT CHANCE (TMW n=273 full 0.495 / zero-overlap 0.489). TMW position 0.91.
- Mine: 1,292,955 directed edges; gold-link coverage 0.502. store_v1.json (3.9MB).
- Held-out DIRECTION (n=10164): causal 0.609 vs co-occurrence 0.513, +0.097 CI-sep; effect-pred +0.022; twin +0.234.
- COPA position-free: causal 0.538 > lexical 0.485 (+0.053 CI-sep) > twin 0.501 (+0.037). e-CARE: causal 0.540 < lexical 0.588.
- BCOPA-CE: causal_directed 0.522 vs blind 0.500 (+0.022 full, +0.035 covered CI-sep); floors ~0.50 by construction.
- WIQA more/less: qdyn 0.457 (ties random twin +0.000); QP 0.255; signed-crude 0.34; Wolff 0% neg-edges. All fail.
- Directional-score upgrade: BCOPA-CE 0.522->0.530 (asym); e-CARE-dir 0.517->0.540 (cond).

## 8. NEXT STEPS / WHERE TO PICK UP (owner said "trace this again")
1. RE-TRACE (this doc sec 2 is the current trace). The single open question: is the grounded-experience signed-quantity
   source achievable in this substrate, or is it genuinely a new research program (embodiment / learned intuitive
   physics)? Enumerate what grounded-dynamics signal COULD be built from existing organs before concluding impossible.
2. If pursuing: scope it as its OWN problem -- instrument = WIQA more/less (twin-controlled, association=chance);
   floor = random-sign twin + majority; compose `fractional_power_encoding` (magnitude) + `causal_reasoner` (do-sim) +
   a grounded quantity-DYNAMICS learner (the missing piece). Do NOT build a 6th text-derived sign source.
3. BANKABLE regardless: the mined causal store (structural prior), the held-out DIRECTION win (+0.097), the directional
   scoring upgrade, the verified-BF ledger, the BF-tag convention. All green; ledger `malformed/incomplete: 0`.
4. The BF-tag hdlab spec (VERIFIED_BF_LEDGER sec) is for STRATEGY to land (Q111); the registry is the concurrent
   session's -- coordinate, don't double-write.
5. owner_verdict NOT yet DONE -- this remains WIP; do not integrate.
