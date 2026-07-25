# PRE-REG: arc_retrieval_selection_gate_learned_credit_v1

**Date:** 2026-07-25
**Author:** exp_dev (Opus 4.8 1M, agent-spawn)
**Cell:** `experiments/exp_arc_retrieval_selection_gate_learned_credit_v1.py`
**Anchor:** `arc_retrieval_selection_gate_learned_credit_v1`
**Thrust:** attack the VET-confirmed #1 ARC lever (retrieval PRECISION) AND the one structural gap (credit-assignment / Stage 8), the brain's way, WITHOUT re-treading the retired similarity-scoring path.
**Status:** LOCKED. Bands author-set a priori as cell constants BEFORE any run. INLINE-LOCAL smoke + FULL both landed foreground-to-completion (NOT remote-portable: GloVe + WorldTree git-ignored/large). VET-PENDING (skunkworks owns landed-VET + atomization).

## Prior-work check (concept-query mandate)
`bash tools/substrate_query.sh "learned credit assignment retrieval selection gate basal ganglia Go NoGo value ARC"` -> top hits at cosine>0.30: `B1. Basal ganglia action selection` (0.3486, June multi-drive-arbitration research note), `Basal ganglia` neurolex (0.3154), `notes/research_value_based_action_selection_basal_ganglia_2026-07-08.md` (0.3154), and `preregs/2026-07-05_pfc_gate_cfrpe_trained_v1.md` (0.3096). Read the top-2: the prior CFRPE gate cell (`exp_pfc_gate_cfrpe_trained_v2`, cert MEASURED_MECHANISM) trains a Go/NoGo value gate by RPE but ONLY on SYNTHETIC navigation chains (state@W_ops + SR-transport reach), NEVER on ARC correctness. **Novelty:** this cell is the FIRST wiring of the dopamine-RPE credit-assignment loop to REAL ARC answer-correctness at the proven retrieval-selection insertion point. It is genuinely NOVEL, not a rediscovery. Prior-work check: [prior CFRPE gate is synthetic-nav only; ARC-correctness wiring is new].

## Hypothesis
Given GOLD central facts the UNCHANGED bind+settle combiner reasons at Challenge 0.6899 (oracle); over the noisy PPR spreading pool it drowns to Challenge 0.2936. ~40 pts of headroom is locked behind SELECTING the right facts. A hand-set SIMILARITY gate (goal-bias + RIF suppression) lifts Challenge to 0.3409 (MEASURED@data/exp_arc_retrieval_selection_gate_suppression_v1/metrics.json:acc_by_arm.B.challenge) but is fundamentally a cosine/margin operation -- the same operation that HARD_FAILed 7x (atoms 29544-29550, root-caused as "still similarity/margin, NOT entailment" = the thin-encoder wall).

**Claim under test:** a LEARNED value gate whose weights are trained on REAL ARC correctness by a dopamine-RPE credit-assignment rule -- consuming NON-similarity STRUCTURAL features (PPR spreading-activation, pool-rank, IDF overlap, degree) alongside cosine features -- beats the hand-set similarity gate on HELD-OUT Challenge. If it cannot, learning-from-correctness cannot overcome the thin encoder's fact reps => the encoder/meaning wall is foundational even for selection (the pre-registered honest-negative).

## Brain-faithful frame
VLPFC controlled retrieval (Badre & Wagner 2007) + basal-ganglia Go/NoGo gating (O'Reilly & Frank 2006 PBWM) + dopamine reward-prediction-error credit-assignment (Schultz 1997): select task-relevant facts by LEARNED value; resist surface-lures. **Honest tension:** the repo master-map RETIRED similarity-scoring-selection and pivoted to derivation-SEARCH (coverage-blocked). This LEARNED gate is the complementary, untested PRECISION lever (credit-assignment), cheaper than un-blocking search. Its features still partly derive from the thin encoder (g_stem/g_disc/best_cos are cosines over thin GloVe reps); credit-assignment can only RE-WEIGHT the available features -- if none separate correct-from-lure at the needed fine grain, learning cannot manufacture signal.

## Mechanism (reuse; ONE new piece)
- **UNCHANGED PPR spreading pool** (arm B, imported from `exp_arc_retrieval_multicue_ppr_discriminative_v1`).
- **UNCHANGED bind+settle combiner** (`agg.aggregate 'bundle'`, imported) -- the pool->gate->combiner insertion point proven one-variable in `exp_arc_retrieval_selection_gate_suppression_v1`.
- **UNCHANGED hand-set similarity gate** (`simgate.gate_scores`, imported) = arm G (reproduce insertion arm B).
- **THE ONE NEW PIECE = the learned credit-assignment gate.** Per-fact linear Go-value `g_i = w.phi_i`; Go-prob `p_i = sigmoid(g_i)`; greedy top-K_SEL selection at eval. `w` trained by a dopamine-RPE REINFORCE rule on ARC correctness: `rpe = r - baseline`; `w += adaptive_lr * rpe * sum_i (a_i - p_i) z_i - L2*w`, reusing `hdlab.action_selection`'s Go/NoGo WTA + cfrpe adaptive-LR clamp (`ADAPT_LR_FLOOR/CEIL`) + `LR_DECAY_END` schedule. Feature set: STRUCTURAL {ppr_act, ppr_rank, surf_pull, lure_align, idf_overlap, n_terms} + SIMILARITY {g_stem, g_disc, best_cos} + bias.
- **HONEST ADAPTATION (not force-fit):** `action_selection.GoNoGoActionGate` is a MULTI-HOP nav actor (state@W_ops + SR-transport reach `M`); ARC fact-selection is a ONE-SHOT contextual bandit, so the SR-M reach is NOT applicable and we use an ARC-native linear value. We reuse the actor PRINCIPLE (linear value + WTA disinhibition) + the RPE credit-assignment update, NOT the nav SR machinery.

## Fairness / no-leak (critical -- a learned gate can memorize)
- `w` trained on a TRAIN split's correctness ONLY; ALL arms eval on a disjoint HELD-OUT split; feature standardization stats (mu, sd) from TRAIN pools only.
- Deterministic stratified-by-source 50/50 split (numpy default_rng permutation over sorted qids; NO hash()).
- Report train vs held-out (overfit gap; `generalizes` gate).
- **L_shuffreward** (train on PERMUTED reward) MUST collapse to baseline -> proves the win needs REAL reward structure.
- **Sh_graph** (train+eval on a SHUFFLED incidence graph) MUST collapse -> proves the win needs REAL retrieval structure.
- **L_cosonly** (cosine features only) anti-tautology -> does STRUCTURE add over learned-cosine?

## Arms (paired; identical pool + UNCHANGED combiner; ONLY selection differs; all eval HELD-OUT)
| Arm | Description | Role / rail |
|---|---|---|
| A_baseline | whole K_POOL pool -> combiner | reproduce insertion A (Chal ~0.29 full-set) |
| G_simgate | hand-set similarity gate top-K_SEL | reproduce insertion B (Chal ~0.34 full-set); the bar to beat |
| L_learned | LEARNED credit-assignment gate top-K_SEL | THE TEST |
| L_cosonly | learned gate, cosine features only | anti-tautology (structure-adds foil) |
| L_shuffreward | learned gate on PERMUTED reward | MUST-FAIL leak control (~baseline) |
| Sh_graph | learned gate on SHUFFLED incidence | MUST-FAIL structure control (~baseline) |
| O_oracle | gold central facts -> combiner | ceiling ~0.69 |

## PRE-REG BANDS (LOCKED; author-set as cell constants BEFORE any run; PRIMARY = HELD-OUT Challenge)
Let `d_LG = L_learned.chal - G_simgate.chal`, `d_LA = L_learned.chal - A_baseline.chal` (all held-out).
- **WIN / CREDIT_ASSIGNMENT_LEVER_WORKS (HARD_PASS):** `d_LG >= 0.03` (HP_LG) AND paired McNemar(L vs G) `p < 0.05` AND `d_LA >= 0.05` (HP_LA) AND `L_shuffreward - A <= 0.015` (collapses) AND `Sh_graph - A <= 0.03` (collapses) AND generalizes (held-out `d_LA >= 0.5 * train d_LA`) AND arms differ.
- **HONEST-NEG / HONEST_NEG_encoder_wall_foundational (HARD_FAIL):** `d_LG <= 0.01` (MB_LG) -- learning-from-correctness cannot beat the hand-set similarity gate => the encoder/meaning wall is foundational even for selection (consistent with the 7x similarity-lineage root cause; a real deep finding). The fix is grounded/learned MEANING, not a better selector over thin reps.
- **MIDDLE:** `0.01 < d_LG < 0.03`, OR `d_LG >= 0.03` but a gate unmet (e.g. beats G directionally but McNemar not significant, or a control fails to collapse -> suspect leak). Selection helps but not decisively.

**discriminator_reachability = TRUE:** A~0.29, G~0.34, O~0.69 on Challenge => 0.35 headroom above G; `+0.03` over G lands ~0.37, well inside feasibility. **Can-fail BOTH ways:** McNemar B-vs-A on the lure subset was p=0.19 in the insertion cell (effect sizes here are small/noisy), so beating G by +0.03 at p<0.05 on held-out n~243 is genuinely uncertain -> honest can-fail discriminator.

## SCHEMA-VET mandatory fields
- `cardinality_ok`: n/a-single-config (no seed/sweep axis; ONE train/held-out split, 7 arms fixed). No `EXPECTED_N_UNITS` cardinality gate applies.
- `arms_differ_verified`: True (per-arm pick SHA256 over {A,G,L,Lc,Lsr,Shg}; MEASURED all 6 distinct at FULL).
- `final_metrics_atomicity`: `tmp_replace` (os.replace on metrics.json).
- `crlb_n/a`: "accuracy-lift discriminator over ARC answers; no single closed-form noise floor. Reachability declared via A->O headroom feasibility (0.35 >> 0.03) + the honest McNemar-power caveat."
- `baseline_in_band`: True (A_baseline Challenge MEASURED 0.3333 in (0.05,0.95); AG-guard at 0.95).
- `calibration_check`: `default_ok_for_this_regime` -- lr/epochs/L2 author-set a priori, NOT tuned to force a win; the must-fail controls (shuffled reward / shuffled graph) collapse toward baseline BY CONSTRUCTION if there is no real signal, so a spurious PASS is guarded.
- `cell_chunked`: False (single-config, ~151s FULL; no multi-seed axis). `start_marker_written`: True. `crash_diagnostic_present`: True (Exception -> CELL_CRASHED + traceback, atomic; except SystemExit: raise BEFORE except Exception; no BaseException/bare except). `heartbeat_present`: True (_heartbeat.jsonl per stage). `defensive_error_checking`: passed (start marker + crash diag + heartbeat + no silent continue).
- `progress_logging`: `line_buffered_stdout` (FULL ~151s < 30min, so §17 not strictly required; provided anyway with per-stage heartbeats + flushed prints).
- `run_mode`: cell writes `run_mode` = mode; FULL verified MEASURED@metrics.json:run_mode = "full", size 14738 B, elapsed 150.9s.

### Gate A -- effective vs nominal parameter audit
No V_C/M/alpha/K capacity sweep. `sweep_alignment_verdict: ALIGNED` (single config; K_POOL/K_SEL fixed at the insertion cell's values for one-variable comparison).

### Gate B -- bracket includes discriminating band
Not a sweep. All non-oracle arms predicted (and MEASURED) in [0.30, 0.46] Challenge -- the discriminating band [0.30,0.70]. `discriminating_fraction ~ 1.0`.

### Gate C -- signal-shape compatibility
Composition edges (all SHAPE_MATCH): PPR pool activation [P] -> feature phi [P,F]; feature -> Go-value `Z@w` [P]; top-K select -> combiner `agg.aggregate` [C]. RPE update `elig=(a-p)Z` [F] -> `w` [F]. No SHAPE_MISMATCH_no_adapter.

### Gate D -- reproduce prior result as positive control
`A_baseline` reproduces insertion arm A and `G_simgate` reproduces insertion arm B (SAME pool + SAME combiner + SAME hand-set gate, imported UNCHANGED). Held-out is a 50% subsample so exact reproduction is not expected; MEASURED held-out A_chal=0.3333 (full-set 0.2936), G_chal=0.3704 (full-set 0.3409) -- both within split-variance and directionally consistent (G>A as in the full set). `O_oracle` reproduces insertion arm O (held-out 0.7284 vs full-set 0.6899). Regime-extension audit: SAME encoder/pool/combiner regime, subsampled split (SHAPE_MATCH; no synthetic->narrative drift).

### Gate E -- functional requirement decomposition
1. "Select task-relevant facts, resist surface lures" -> LEARNED Go-value over structural + similarity features (the build).
2. "Credit-assignment: which selected facts led to the correct answer" -> dopamine-RPE REINFORCE on ARC correctness (the NEW piece; no prior primitive wired RPE to ARC correctness).
3. "Winner-take-all gating" -> top-K_SEL greedy over Go-values (basal-ganglia disinhibition).
4. "Do not leak the answer" -> train on TRAIN correctness only; disjoint held-out eval; standardization from TRAIN only; shuffled-reward + shuffled-graph must-fail controls; answer-agnostic selection (gold used only for reward on TRAIN + held-out EVALUATION).

## Compute architecture
Class **(b) sequential-CPU with justification**: GloVe encode + scipy.sparse PPR are batched; the REINFORCE loop is a cheap per-fact linear-value update over a 20-fact pool (matmul-trivial); the UNCHANGED combiner is a small bundle. Wall MEASURED 150.9s FULL (< 10min foreground) -- no GPU speedup warranted (GPU-batching rule: per-phase wall << 10s equivalent; the cell is I/O + Python-loop bound on tiny matmuls, not GPU-bound). INLINE-LOCAL mandate honored (foreground-to-completion; NOT remote-portable). Storage strategy: **sharded** (each fact = own embedding + own graph node; no superposition).

## Discriminator-survives-scale
Option **(A) smoke at full-graph + (C) preview**: smoke used the FULL 9720-fact graph (real pool at scale), question SUBSET (300E/250C). Smoke MEASURED the discriminator FIRING in the PASS direction (held-out Chal L=0.448 > G=0.40 > A=0.36; both controls collapse) at reduced n; FULL is canonical. The discriminator is INFORMATIONAL (learned value ranking), not capacity-limited.

## SMOKE RESULT (INLINE-LOCAL, full graph, 300E/250C subset, 40 epochs) -- MEASURED
`MEASURED@data/exp_arc_retrieval_selection_gate_learned_credit_v1/metrics.json` (smoke overwritten by FULL; values from smoke run log): held-out Chal L=0.448, G=0.40, A=0.36, Lc=0.44, Lsr=0.20, Shg=0.248, O=0.808; d_LG=+0.048, d_LA=+0.088, shuffreward R-A=-0.16 (collapses), shuffgraph Sh-A=-0.112 (collapses), generalizes=True, McNemar p=0.377 (not sig at n=125), arms_differ=True, learn_fired=True. **SMOKE GATE PASSED:** cell runs at full graph, rails hold, discriminator fires in PASS direction, both must-fail controls collapse, learning fires. MIDDLE label at smoke driven ONLY by McNemar significance at reduced held-out n (expected to tighten -- or not -- at FULL).

## FULL RESULT (INLINE-LOCAL, full graph, all 1664 Q, 60 epochs) -- MEASURED, CANONICAL
`MEASURED@data/exp_arc_retrieval_selection_gate_learned_credit_v1/metrics.json` (run_mode=full, 14738 B, elapsed 150.9s):
- Held-out Challenge (n=243): **L_learned=0.4115**, G_simgate=0.3704, A_baseline=0.3333, L_cosonly=0.3827, L_shuffreward=0.3045, Sh_graph=0.3045, O_oracle=0.7284; chance=0.25.
- `d_LG = +0.0411` (clears HP_LG=0.03); `d_LA = +0.0782` (clears HP_LA=0.05; closes ~20% of the A->O oracle headroom).
- **McNemar L vs G: b=19 c=29 stat=1.69 p=0.194 (NOT significant)** -- L wins 29 vs 19 discordant pairs (directional) but not decisively.
- Structure adds: `d_LA=0.0782` vs cos-only `d_cosonly_minus_A=0.0494` -> structural features add +0.0288 over learned-cosine.
- Controls collapse: shuffled-reward R-A=-0.0288 (<=0.015), shuffled-graph Sh-A=-0.0288 (<=0.03). generalizes=True. arms_differ=True. learn_fired=True. baseline_in_band=True.
- **Learned weights** (the mechanism signature): ppr_act=1.884 (LARGEST -- the gate learned to rely most on the NON-similarity structural spreading-activation feature), lure_align=-0.447 (learned RIF suppression FROM REWARD), best_cos=1.296, g_stem=1.123, surf_pull=0.629, ppr_rank=0.619, g_disc=0.257, idf_overlap=0.036, n_terms=-0.189.
- **VERDICT = LEARNED_GATE_MIDDLE_BAND.** The credit-assignment gate beats the similarity gate DIRECTIONALLY (+4.1pp held-out Chal, 29>19 discordant) and clears the baseline by +7.8pp, up-weighting a genuinely NON-similarity structural feature and learned lure-suppression from reward, with both must-fail controls collapsing and clean generalization -- but the L-vs-G margin is NOT statistically decisive at held-out n=243 (McNemar p=0.19). NOT the clean WIN (no significant separation from G); NOT the honest-negative (the encoder wall is NOT total -- reward-driven learning over structural+cosine features extracts a real, if modest, precision gain that directionally beats the hand-set similarity gate).

## Self-test (formula correctness) -- MEASURED, ALL PASS
Planted credit-assignment discriminator: full-feature learned gate reward=1.0 vs cosine-only learned gate reward=0.225 (structure beats cosine by +0.775) -- the credit-assignment lever is ISOLATED from similarity and reachable; REINFORCE increases train reward; arms differ. Real code path: builds REAL SemanticHDEncoder + REAL PPR pool + REAL features + REAL learned gate + UNCHANGED combiner; deterministic features + deterministic disjoint split; McNemar in range.

## Falsifiable predictions (recorded pre-lock; FULL MEASURED above)
- WIN: d_LG>=0.03, McNemar p<0.05, controls collapse. [MEASURED: d_LG=0.041 cleared magnitude but p=0.19 -> NOT met on significance.]
- HONEST-NEG: d_LG<=0.01. [MEASURED: d_LG=0.041 -> NOT met; the gate DOES directionally beat G.]
- MIDDLE: in between or a gate unmet. [MEASURED: this is the landed outcome -- directional lift, controls clean, significance not reached.]

## Cites
- data/exp_arc_retrieval_selection_gate_suppression_v1/metrics.json (insertion point A/B/S/R/O + the 0.341 similarity-gate anchor)
- data/exp_arc_retrieval_multicue_ppr_discriminative_v1/metrics.json (the PPR spreading pool, arm B)
- data/exp_arc_aggregation_retriever_bindsettle_v1/metrics.json (the UNCHANGED bind+settle combiner + oracle-gold 0.6899 ceiling)
- hdlab/action_selection.py (Go/NoGo actor + cfrpe adaptive-LR credit-assignment PRINCIPLE reused)
- preregs/2026-07-05_pfc_gate_cfrpe_trained_v1.md (prior CFRPE gate; synthetic-nav only -- ARC-correctness wiring is the novelty)
```
