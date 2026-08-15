# BOARD -- questions waiting on you

**How to answer:** type your decision into the **ANSWER** cell of any row below, in any markdown
editor, on any device. Save. That is the whole protocol. You do NOT need to touch the `status`
cell, and you do NOT need to run anything: a non-empty ANSWER is treated as answered, and the row
moves down to ANSWERED on the next update.

This file is **REWRITTEN IN PLACE**, never appended, so it does not scroll and never gets long.

**Stop the overnight loop instantly:** `python tools/autoloop.py disarm`
(or open `data/hook_state/autoloop.json` and set `"armed": false`). See
`notes/BOARD_AND_LOOP_README.md`.

<!-- PARSER CONTRACT -- READ BEFORE REWORDING ANYTHING ABOVE OR BELOW.
     This document is machine-parsed by tools/board.py (which also rewrites it) and its open-
     question count is injected at every session start by tools/session_start_hook.py.
     The following are an API, not formatting choices:
       - the headings `## STATUS`, `## QUESTIONS FOR YOU`, `## ANSWERED`
       - the QUESTIONS column order: ID | Question | What's blocked on it | My recommendation | ANSWER | status
       - the ANSWERED column order: ID | Question | My recommendation | ANSWER | resolved
     Editing CELL TEXT is always safe and is the intended use, including typing a raw `|`.
     Adding your own `## <anything else>` section is safe; it is preserved verbatim.
     Renaming a managed heading or reordering columns is NOT safe -- change tools/board.py in the
     same edit. (CLAUDE.md: "A doc parsed by code is coupled to it".) -->


## STATUS

AS OF: 2026-08-14 | branch `dataprep/mcguffey-graded-corpus` | GROWTH PAUSED | origin merge needs USER AUTH

**POSITION**
C3 read-out 4.80% hit@1 clears scramble (0.80% / 1.375%, DONOR-RULE dependent) but is BELOW the
ORTHOGRAPHIC floor 8.70% -- see FLOOR VET
(`exp_grounding_readout_known_answer_v1`, `204eba1a0`). THE GATE WAS GAMEABLE, NOW HARDENED
(`9316f98ee`): a PURE-SPELLING channel on the base arm reaches 0.10275, clearing the old ">=10% vs
a floor" criterion, now RETIRED. C3 needs FOUR conditions via `tools/c3_gate.py`; no string-form
control = NOT_EVALUABLE, never PASS. NOTHING passes: 0 of 13 arms, incl. the gate's own cell.

**TOP ITEM -- A FLAT BAG OF CO-OCCURRING WORDS CANNOT HOLD MEANING**
FACTORED role/filler held-out 1.000 vs FLAT 0.003 (`exp_role_filler_factorization_compgen_v1`).
CONJUNCTIVE 1.000 vs ADDITIVE 0.273 at M=256
(`exp_interference_avoidance_conjunctive_vs_additive_v1`) -- the additive arm IS our bag geometry.
PERMUTATION binding 1.0000 vs FHRR 0.0629 on same-role collision
(`exp_substrate_permutation_binding_multiocc_v2_full`). NEXT = CONNECT EXISTING WORK, not invent:
give the live comparator a structured code. QUALIFIED: perirhinal CONJUNCTION OP is UNPINNED +
feature-ambiguity CONTESTED (real failed replications) -- OURS to choose, NOT pinned brain
fidelity (4 rescued `lit_scan_*_2026-08-14.md`).

**WHAT IS RUNNING / BLOCKED**
- COREF-MARGIN agent LIVE (STEP 5) owns
  `data/exp_coref_margin_gated_cleanup_local_window_break050_v1*` -- do not touch.
- `data/exp_structured_comparator_v1/probes/` + `CLAUDE.md`: concurrent writers; never stage.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB), NO BACKUP; 37MB snapshot
  GITIGNORED, not in remote (reproducible from code+corpora).
- STEP 4 (`d=256->1024`) HELD PENDING USER AUTH -- rewrites every persisted anchor store while a
  concurrent session is live.
- Merge to `origin/main`: USER AUTH required.

_mirrored from `notes/STATUS.md` at 2026-08-15T23:10:41Z by `tools/board.py`._

## QUESTIONS FOR YOU

| ID | Question | What's blocked on it | My recommendation | ANSWER | status |
|---|---|---|---|---|---|
| Q1 | Remove the DUPLICATE Stop-hook registration from your USER-level settings (C:/Users/marsh/.claude/settings.json)? It registers D:/AI/hd-instrument/data/hooks/staging/stop_hook.py a second time, on top of the project-level one. | The hook fires TWICE per Stop event (13,223 invocations logged; pairs of PIDs one second apart are visible in data/hook_state/_invocation_log.txt). It also applies this repo's hook to every OTHER project on this machine. I mitigated the counter double-increment but did not fix the cause: I am not allowed to edit your user-level config. | Delete the whole 'hooks' block from C:/Users/marsh/.claude/settings.json. The project-level registration in D:/AI/hd-instrument/.claude/settings.json already covers this repo and is the correct scope. Then set HD_STOP_DEDUPE_WINDOW_S=0 to retire the mitigation. |  | open |
| Q2 | Is UNLIMITED the cap you actually want for the overnight loop, or a large finite number like 200? | Nothing: the loop is built and left DISARMED, and arming defaults to unlimited per your 'no limit' instruction. This only decides what the arm command should say. | Arm with a large finite cap the first night (python tools/autoloop.py arm --max 200), not unlimited. Evidence: three sessions have already hit the old cap of 10, one of them today at 14:43, so the loop does run long. 200 gives you a full night and still terminates if something degenerates while you are asleep. Switch to --max 0 (unlimited) once you have seen one clean night. |  | open |

## ANSWERED

| ID | Question | My recommendation | ANSWER | resolved |
|---|---|---|---|---|
