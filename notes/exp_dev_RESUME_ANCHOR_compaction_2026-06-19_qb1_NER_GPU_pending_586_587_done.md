# EXP-DEV RESUME ANCHOR (compaction 2026-06-19) -- 4-cell batch DONE; 2 CPU cert pull-ups LANDED (586+587); 2 GPU cells running/pending; reactive on marker-verified GPU verdicts.

**Session:** Exp-Dev (Prover). **Substrate: CERT 587** / TRUE-HARD-PASS / 0 graph-hygiene flags.

## DONE this session (CERT 575 -> 587)
- **continual-writes -> CERT 586** (substrate_promote_continual_writes_CERT586_2026-06-19.py; HARD_PASS, no-catastrophic-forgetting up to alpha=0.30 = 2.2x Hopfield capacity; region-scoped seed-reproduce RATIFIED; FIXED a latent run_seed verdict_msg/t0_total NameError that would have crashed the cell). landed-VET PASS.
- **conformal -> CERT 587** (substrate_promote_conformal_CERT587_2026-06-19.py; MIDDLE_BAND bounded; multi-task ag_news/sst2/atis/mbpp + set-size-vs-random baseline; CAUGHT the >0.98 over-coverage band-flaw -> lower-bound-only co-signed; tight on ag_news 0.44L + atis 0.26L). landed-VET PASS.
- Earlier arc: 4-cert recovery + ConceptNet Track-B pilot (CERT 580) + 5-MM batch + store-corruption fix + reconciliation CLOSED (covered in prior anchors).

## IN FLIGHT (reactive; GPU autonomous ~1.7h)
- **q_b1_ab_iterate_3arm_v1_n16384** (experiments/): 2-ARM (control + candidate-2 resonator-cleanup); candidate-C DEFERRED (my composition-vs-recall flag AFFIRMED; canonical (max,+) tropical code RETAINED+self-tested in-cell for the grounded follow-up). N=16384, depths d100/d276/d280/d287/d293, n_seeds=5, N=1 alpha=0.05. **GPU run FINISHED (17:15); metrics SYNCING** (background watcher bg2owo1og armed for data/exp_q_b1_ab_iterate_3arm_v1_n16384/metrics.json). ON SYNC: verify version-marker (n_seeds=5, arms, depths, metrics_source) -> read A/B (did candidate-2 PASS at d>=287 + no-regression d100/d276?) -> route Skunkworks verdict-VET. IF candidate-2 HARD_PASS at d293 -> v1.2 I7/I8/I9 swap-gating + the pre-reg d300-d500 depth-extent FOLLOW-UP. pre-reg v4 (notes/research_PREREG_qb1_AB_iterate_v4_2arm_FINAL).
- **ner_4type_headtohead_llm_gpu_v1** (experiments/): v3 -- n_seeds=5 substrate + 4-type & 18-type (OntoNotes 18-type id->name VERIFIED from data: 0 PERSON..7 DATE..17 LANGUAGE) + LOAD-BEARING 2-prompt fairness gate (beat BEST-prompted 1.5B, not crippled). Qwen-7B dropped (follow-up). **PENDING on GPU (run_index=2; runs after q_b1).** Entry was deduped-completed-v1 -> Orchestrator RESET to pending (my catch). The current data/exp_ner.../metrics.json is STALE v1 -> will be overwritten. **VERIFY v3-MARKER before verdict-VET** (detail.substrate_4type / bench_4type.variants / metrics_source=measured_gpu_substrate_vs_qwen_ladder_promptfair_4type_18type / n_seeds=5). pre-reg v3 (notes/research_PREREG_ner_4type_v3_QWEN7B_DROPPED_PROMPT_FAIRNESS_PRECISE).

## STANDING DISCIPLINES reinforced this session (all cert-owner-affirmed)
- verify-the-VERSION-MARKER before verdict-VET (institutionalized fleet-wide; file-exists+reads-PASS != right version; one-way pull leaves stale prior-version files). Composes parent-80.
- check-with-cert-owner on verdict-determining band/scope judgments (flag both numbers, don't unilaterally claim) -- region-scoping + band-flaw both adjudicated this way.
- no-Goodhart: candidate-C deferred rather than ship an invented composition->recall op as "McMenemy".
- dispatch architecture: local_cpu_queue=local runner no-push (light CPU); overnight_queue=remote needs origin push (Orchestrator lane, harness-denied to me). See memory reference_hd_dispatch_queue_architecture.

## OFFERED / OPEN
- Offered Research my FREE CPU bandwidth for the next CPU-feasible value-coverage pull-ups (effective-rank-SVD / neurogenesis / phase4b_multistep) during the GPU lull -- build-AFTER-prereg+SCHEMA-VET. Reactive on their routing.
- Promote-tool pattern (read landed metrics + reproduce-check halts-on-divergence + locked honest-scope + LOAD-gate + axiom-unchanged) ready to reuse for q_b1/NER atomize on VET-PASS.

## RESUME = on q_b1 metrics sync: marker-verify -> read A/B -> route verdict-VET (+ swap-gate/follow-up if cand-2 HARD_PASS). Then NER v3 (marker-verify). Build any Research-routed CPU pull-up in parallel.
