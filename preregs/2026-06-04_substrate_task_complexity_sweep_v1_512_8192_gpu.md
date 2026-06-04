# Prereg: substrate_task_complexity_sweep_v1_512_8192_gpu

## Anchor
substrate_task_complexity_sweep_v1_512_8192_gpu

## Routing
routing_bundled_substrate_explorations_for_gpu_occupancy (Bundle B) + Research refinement (GO; cf-RPE +
Drosophila-sparse variants; tasks = trigram V70 + Zipf V512 + extended-context K8 V70). Owned GPU, $0.

## Scientific question
At what task complexity does substrate-as-training break? 2 archs (cfrpe bipolar, drosophila_sparse f=0.05;
both cf-RPE delta) x 3 tasks (zipf_v512 bigram, wiki_v70 trigram, wiki_v70 extctx8) x N {512,2048,8192} x
3 seeds = 54 cells. Multi-char context = fixed roll-binding encoder (NOT the variable; that's Bundle E).
BPC gap = uniform_nats - val_nats.

## Pre-registered bands (per task, best arch, at N=8192)
per-task HP gap>1.0; MID [0.3,1.0]; HF <0.3. AGGREGATE: HARD-PASS if >=2/3 tasks gap>1.0 (handles complexity
beyond bigram); HARD-FAIL if ONLY bigram learns (trigram+extctx8 both <0.3 -> K=2 bound); MIDDLE otherwise.

## Formula self-tests (PROT-022)
1. roll-binding order-sensitive (cos<0.9). 2. cf-RPE shrinks error. 3. sparse support=f*N. 4. uniform=ln(V).
5. zipf cond-entropy<log(V). [ALL PASS]

## Smoke gate
Smoke PASSED on remote GPU (N=256, 2 seeds): HARD_PASS; complexity ordering visible (bigram +2.84 > trigram
+1.28 > extctx8 +1.12). Full N=8192 + real wikitext corpus is the registered test.

## PROT-018 / 021
NO _nN suffix (N swept {512,2048,8192}; declared _512_8192). timeout 14400s. 3 seeds.

## Queue
overnight_queue (GPU).
