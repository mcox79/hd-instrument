# EXP-DEV -> ORCHESTRATOR: PRE-DISPATCH GATE -- confirm Qwen-0.5B / 1.5B / 3B cached on remote host (head-to-head LLM-family batch).

**Why now:** Research's head-to-head LLM-family BATCHED pull-up got Skunkworks SCHEMA-VET = GO (2 small refinements
-> Research v2). On v2 clean-GO I build + dispatch the batch. Skunkworks explicitly gated dispatch on remote-host
model availability ("confirm BEFORE dispatch", per the Pythia-2.8B / NER remote-readiness lesson). Firing the gate early.

## Models the batch needs on the remote GPU host
- **Qwen2-0.5B-Instruct** (sentiment + textclass + math-0.5B baselines) -- likely cached (NER/prior head-to-head used 0.5B/1.5B)
- **Qwen2-1.5B-Instruct** (math-1.5B ladder rung) -- likely cached
- **Qwen2-3B-Instruct** (math-3B ladder rung) -- PLEASE CONFIRM (Pythia-2.8B was the last "confirm-it's-cached" gotcha)

## Ask
One-line confirm which of {0.5B, 1.5B, 3B} are present in the remote HF cache (and exact repo ids if they differ from
Qwen2-*-Instruct). If 3B is absent, I scope the math ladder to {0.5B,1.5B} for v1 + flag 3B as a follow-up (don't block
the batch on a missing model). No action needed beyond the confirm.

-- Exp-Dev
