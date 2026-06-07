- d_eff/capacity ceiling theory: notes/research_drill_d_eff_capacity_ceiling_theory_2026-06-07.md -- cap~1.33*d_eff from bipolar noise suppression; BGE-large predicted 140-165; PCA cannot break ceiling post-whitening; 4 ceiling-breaking mechanisms; 5 negative scenarios; sharding mandated
- [2026-06-07] default-choice capacity taxes: notes/research_drill_mean_pool_tax_investigation_2026-06-07.md | P_deflated=0.17-0.62 | top EV: alpha-sweep(1.86), M_max-uncensor(1.82), write-rule(1.57), padding(1.13), ZCA-eps(0.83)
- adversarial_robustness_adaptive_2x 2x drill (2026-06-07): notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md -- 4 refutations: fp16+anchoring GENUINE; KF-1+middle-hop PARTIALLY LUCKY; 12 adaptive attacks catalogued; AT-1 through AT-6 proposed; exp_dev handoff written
- [2026-06-07] G8 anchoring-propagation 2x drill -> notes/research_drill_clustered_KB_anchoring_propagation_2x_2026-06-07.md | HEADLINE: MMR diversification is primary rescue (P=0.45); rho_cluster>0.30 is production-blocking without mitigation; 4 empirical rescue cells filed
- fp16_N65536_overflow_3x_deep -> notes/research_drill_fp16_N65536_overflow_3x_deep_2026-06-07.md ; bf16 is the production fix; overflow is ZCA/matmul chain sqrt(N) scaling; P_deflated=0.65 parity; N_max(fp16)~50k confirmed; N_max(bf16)~10^76

- [2026-06-07] temporal-fact-versioning 2x -> notes/research_drill_temporal_fact_versioning_2x_2026-06-07.md | P_deflated=0.45-0.65 | HEADLINE: bitemporal algebra maps to substrate via Merkle+valid-time composition; 5-6 week engineering path; Blue Ocean = semantic+temporal+cryptographic audit composition none of XTDB/Datomic/RAG provide
- gradient_based_adversarial_attacks_2x (2026-06-07): notes/research_drill_gradient_based_adversarial_attacks_2x_2026-06-07.md -- KF-1 smooth gradient primary threat (P=0.52); HOC1+KF-1 paradox joint evasion P=0.22; cross-hop Merkle gap P=0.35 NEW; 5 cells; handoff filed

# Major architectural decisions LOCKED today 2026-06-07
- PRODUCTION RECIPE LOCKED (cycle 143; v464): whiten + pseudoinverse on real keys = alpha_c=0.400; OLD raw+Hebb = 0 (non-functional). All future substrate code paths use whiten + pinv.
- ENCODER GEOMETRIC SCREEN MANDATORY (cycle 144 G1; v465): PR > 40 AND rho_eff < 0.35 pre-condition before any capacity measurement. Llama-3.2-1B preferred; BGE-large narrow-regime viable; E5-large + MPNet + Pythia excluded.
- SPARSE-KEY MUTUALLY EXCLUSIVE (cycle 143; v464): cannot stack with main capacity stack (pinv + sparse + multi-head -> 0 capacity). Sparse-KEY is its own production line.
- PADDING FIX LOCKED (cycle 142 + Q4 Testbed validation +22.6%): all retrieval/extraction uses left-padding. Right-padding + last-token extracts PAD embeddings (zero signal).
- COMPOUND MATH REVISED: pinv x sparse DO NOT stack (Batch F F7 GENUINE HF). Production picks BEST SINGLE LEVER per axis. Multi-head + CRT + sharding are independent axes that DO compose. Cycle 143 main stack potentially BILLIONS of facts via sharding.
- KF-1 6-ATTACK ADVERSARIAL COVERAGE (cycles 122/130/141/144/145): hard-negative + word-shuffle + paraphrase + entity-sub + semantic-similar + consistent-lie K-hop chains. All HP at full multi-seed.
- CLUSTERED-KB MITIGATION VIA MMR (cycle 145 H1; Carbonell-Goldstein 1998): propagation 0.341 -> 0.050 via MMR diversification (lambda=0.5, top-10). Production-deployable with MMR-gated retrieval for clustered domains.
- FP16 AT N=65,536 BLOCKED -> bf16 (Drill A 3x deep): one-line dtype fix; bf16 capacity parity > 0.95 P_deflated=0.65. Batch I I1 empirically validates.
- LORA HURTS RETRIEVAL (-28.9%; Q4): SFT objective structurally incompatible with retrieval geometry per Drill B (3x deep; P_deflated=0.72 for Hyp-A). CELL-3 trains from BASE with feature-mimic, NOT logit-distill.
- CELL-2 800K UNIFORM ACCEPTED ($2.24 actual vs $30 quoted; cycle 145): substrate foundation for CELL-3/4 + Phase 3 demo. Re-extract with left-padding flagged to user for +22.6% baseline (decision pending).
- CELL-5 CASCADE DISTILLATION FD ratio 3.91 ($2.67 actual): Path A 70B-Instruct-Turbo teacher viable; PHASE4A-2 distillation grounded.
- TESTBED COST DISCIPLINE: $8.88 actual cloud spend today (vs Drill Y $100-200 envelope = 93% under). Projected through CELL-3+CELL-4: ~$35-45.
- BLUE OCEAN AXES OPENED: agentic memory (drill pending; just temporal landed); temporal fact versioning (HEADLINE: bitemporal Snodgrass/SQL:2011 maps to substrate; Merkle = transaction-time; Pattern D hash-chain low engineering cost; 5 markets); federated privacy (drill in flight); gradient adversarial (drill just landed).

Sat Jun  6 20:21:05 EDT 2026: federated_privacy_substrate_2x -> notes/research_drill_federated_privacy_substrate_2x_2026-06-07.md ; P_deflated=0.38 ; HEADLINE: additive secret sharing composes algebraically with pseudoinverse write; DP hard-fail at N=1024 confirmed analytically; N>=4096 required
2026-06-07 | research_drill_agentic_memory_layer_2x -- notes/research_drill_agentic_memory_layer_2x_2026-06-07.md -- EU AI Act compliance pull + 5 patterns + CRDT synthesis + 5 cells. P_deflated=0.52.
