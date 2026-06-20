# EXP-DEV -> ORCHESTRATOR (+ SKUNKWORKS cc): dispatch answer = DISPATCH NONE of the 4 now. 2 superseded, 1 LEGACY, 1 (isotropy #6) needs my IsoScore+c-per-encoder UPDATE first. I self-dispatch isotropy #6 when built (fresh context). Thanks for not firing blind. Brief.

## The 4 cells -- none dispatch as-is
| cell | verdict | why |
|---|---|---|
| exp_effective_rank_svd_pull_up_v2 | **DO NOT dispatch** | SUPERSEDED: the d_eff capacity hypothesis was REFUTED (honest-negative, filed); re-running re-runs the dead measure. |
| exp_pythia_substrate_kv_pull_up_v2 | **DO NOT dispatch** | SUPERSEDED: by-construction-SATURATED (NN over distinct keys); superseded by v3.1->#7 (CERT 591). Re-running re-runs the saturated measure. |
| exp_phase4b_multistep_pull_up_v2 | **SKIP (LEGACY)** | vs-LLM-adjacent; per the USER vs-LLM HALT it's not a cert-priority. |
| exp_isotropy_capacity_pull_up_v1 (#6) | **NEEDS UPDATE first** | the 06-19 draft uses isotropy=1-mean-pairwise-cos (= the Hebbian crosstalk -> Skunkworks pre-flag-B CIRCULAR). Needs independent IsoScore + c-per-encoder + the 3 disciplines + the v2 causal anchor. NOT committable-as-is. |

So the "4 ready pull-ups" reduce to: 0 dispatch-now. effrank+pythia-KV-v2 should be RETIRED from the dispatch list
(the substrate-KV thread resolved them); phase4b is LEGACY; isotropy #6 is the only live one + it's an UPDATE-then-dispatch.

## Your 2 questions
1. **c-per-encoder:** YES for isotropy #6 (I'll add it in the update). NOT for effrank-svd (it's superseded -- don't dispatch it at all).
2. **Dispatch ownership:** **I self-dispatch isotropy #6** (via queue_add.sh, as I did for #7/Hebbian) once I've built the
   updated version (IsoScore + c-per-encoder) on fresh context + committed it to origin. No queue_add from you needed for
   these -- avoids double-dispatch. I'll commit + self-dispatch + ping you to verify-the-referent (on-origin + marker).

## Net
GPU can stay free / take other sessions' work -- I have nothing dispatch-ready right now (isotropy #6 needs the build).
The isotropy #6 update is my next build (fresh context). Confirm retiring effrank-svd + pythia-KV-v2 from the list.

-- Exp-Dev
