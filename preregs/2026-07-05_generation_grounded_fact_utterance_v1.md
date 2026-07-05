# Pre-registration: generation_grounded_fact_utterance_v1

Anchor: `generation_grounded_fact_utterance_v1`
Cell: `experiments/exp_generation_grounded_fact_utterance_v1.py`
Queue: remote_cpu_queue (CPU probe; torch pinned to cpu; no GPU, no LLM)
Date: 2026-07-05

Note (provenance): the substantive pre-registration lives in the cell header + band
constants (lines 121-142). This file materializes those bands verbatim so queue_add.sh
can ship + record provenance. All values transcribed off-disk from the cell; nothing added.

## HONEST FRAMING (USER-LOCKED 2026-07-05 -- carry to verdict_msg + verdict-handler)

This RE-EMITS held CONCEPT-NAME strings in composed order via the integrated
retrieve->compose->decode loop. It is the first end-to-end grounded re-emission: the proven
loop retrieves + composes + decodes REAL held ConceptNet facts. It is NOT English-language
generation, NOT fluent language, NOT language knowledge, NOT the capstone. Frame ONLY as
"grounded-fact re-emission via the integrated loop." Regime is SHAPE_DRIFT-documented: real
ConceptNet D_STORE=2 is EASIER than the integration bridge's random D=3, so no over-claim.
Full fluent language is a separate capstone needing a language ingest (scoped separately).

## Loop under test (glass-box, per queried fact)

HELD KNOWLEDGE -> STORE (HRR circular-conv over REAL BGE concept vectors) -> RETRIEVE
(unbind role) -> COMPOSE/BRIDGE (HRR-BGE N_R=1024 -> bipolar generation code N_G=8192) ->
DECODE+SPEAK (unbind ordered slots + argmax cleanup -> subj/rel/obj codebook indices ->
LOOK UP + PRINT real name strings). Metric gates on the RETRIEVED object slot (subj/rel clean).

## Arms

- grounded_symbolic (deliverable): cleanup r_hv to nearest concept, speak its clean code.
- grounded_cotrained (deliverable): learned held-out ridge bridge W (train pool DISJOINT from cleanup vocab).
- posctrl_stored_direct (WIRING control): bridge the CLEAN object -> bridge ceiling.
- broken_retrieval (DISCRIMINATOR): unbind a role NOT stored -> identity severed -> garble toward chance.

## Pre-registered bands (transcribed from cell lines 133-138)

- HP_REEMIT = 0.70          HARD_PASS: deliverable (best of symbolic/cotrained) re-emission exact-ordered.
- HP_DISCRIM_GAP = 0.40     HARD_PASS: (deliverable - broken_retrieval) must exceed this.
- HP_LEGIBILITY = 0.80      HARD_PASS: fraction of emitted object strings that are plain-legible words.
- HF_REEMIT = 0.30          HARD_FAIL: below -> chained composition breaks a per-primitive-proven step.
- POSCTRL_FLOOR = 0.70      WIRING gate: stored_direct (bridge ceiling) must recover >= this.
- BROKEN_COLLAPSE_CEIL = 0.10  DISCRIMINATOR: broken_retrieval must collapse at/below this.
- THEORETICAL@chance = 1/V_CLEANUP (V=1024 -> 0.00098): broken-retrieval discriminator lands here.

## Config

N_R=1024 (store/reason), N_G=8192 (bipolar-BSC generation) -- NEVER reduced in smoke.
D_STORE=2 real facts/subject; V_CLEANUP=1024; N_SUBJ_FULL=100; N_TRAIN=4096; seeds=(7,13,19).
Data: prebuilt compact cache data/gen_grounded_fact_cache/grounded_triples_v1.npz (SCP'd to
remote; queue_add does NOT auto-ship untracked npz). When the cache exists the cell loads it
directly and never touches the master BGE table or ConceptNet edges.

## Verdict gate

HARD_PASS iff deliverable exact-ordered >= 0.70 AND discriminator gap >= 0.40 AND posctrl
>= 0.70 AND legibility >= 0.80. HARD_FAIL if deliverable < 0.30. Zero KB_REFERENTs -> PROT-022 no-op.
