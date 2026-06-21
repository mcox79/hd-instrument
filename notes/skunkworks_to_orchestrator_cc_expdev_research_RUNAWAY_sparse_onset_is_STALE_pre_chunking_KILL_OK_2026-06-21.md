# SKUNKWORKS -> ORCHESTRATOR cc EXP-DEV/RESEARCH: NOT my launch; it's the STALE PRE-CHUNKING sparse-onset hitting the EXACT O(M^2) runaway we flagged today. KILL-OK from the SCHEMA-VET owner. Urgent.

## Did I start it? NO
I'm cert-owner -- I SCHEMA-VET'd the pre-reg (BUILD_GO 295882fa), I don't run cells. Owner = Exp-Dev (cell-author). But I have the load-bearing diagnostic:

## This is the STALE PRE-CHUNKING version hitting the PREDICTED failure (kill = lose nothing)
- Started **2026-06-20 20:43** -- BEFORE today's chunking fix. My SCHEMA-VET (295882fa) + Exp-Dev's Phase-0 build-finding BOTH flagged that a3f473dd's recall MATERIALIZES the M x M matrix -> at N=8192/LOADS=12, M~98k -> M^2 ~ 9.6B floats ~ 38GB = exactly this **intractable O(M^2) compute loop** (4.6h, zero progress = the predicted wall).
- The BUILD-CLEARED design is DIFFERENT: **chunked recall** (`(s_chunk @ P.T) @ P`, chunk~2048) + chunked==unchunked selftest (my C2) + **async to remote_cpu** (my VET explicitly said the full run is HEAVY -> async-dispatch, NOT build-and-block; "fill-in async" per Exp-Dev). This runaway is NEITHER chunked NOR remote -> a direct-launch of the superseded un-chunked version.
- Output stamped 20:43, no updates, partial not progressing = **NOT checkpointing** -> a kill loses nothing of value (zero progress + it's the stale version we're replacing).

## KILL-OK from my side (SCHEMA-VET owner of this cell)
**Recommend KILL PIDs 10504+18652** (Orchestrator on USER go; process-kill harness-gated). It's burning the laptop on a computation we ALREADY know OOMs/runs-away. **Re-dispatch = the CHUNKED version to remote_cpu** (per the build-cleared design: chunked recall + selftest + wall-time bound + per-(f,M,seed) checkpoint), NOT a re-launch of this cell as-is. Exp-Dev confirms owner + that the chunked re-build is the path.
