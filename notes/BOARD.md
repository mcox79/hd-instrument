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

AS OF: 2026-08-16 | branch `dataprep/mcguffey-graded-corpus` | HEAD `03055c7fa` | GROWTH PAUSED | origin merge needs USER AUTH

**POSITION**
Read-out still BELOW its spelling floor: hit@1 4.80% vs TRIGRAM-ONLY 8.70%, CI-separated
(`exp_orthographic_floor_vet_v1`, reproduced off disk tonight). Two STRUCTURAL gaps measured
tonight: we built ONE of the brain's TWO relational hubs, and the target space is missing CHANNELS.
The missing hub did NOT rescue bridging. 0 of 7,769 banked cells meet the bar.

**TOP ITEM -- MISSING CHANNELS, NOT MISSING DIMENSIONS (LESSONS: TARGET SPACE)**
Our 12-dim landing space covers 2 of the brain's 7 attribute blocks. Adding AFFECT (Warriner VAD, on
disk, unused) lifts the hand-rated SimLex ceiling 0.3130 -> 0.4143, paired +0.1013
[+0.0615,+0.1419] on 977 pairs, CI-SEPARATED; nouns +0.0253 NOT sep, verbs +0.1228 and adjectives
+0.3399 separated -- the GAIN profile mirrors the FAILURE profile. NEGATIVE CONTROL FIRED: +11
rater-SD cols (23d) 0.3035 and +6 derived cols (18d) 0.3025 sit BELOW the 12d incumbent, so widening
without a CHANNEL buys nothing (`03055c7fa`). SCOPE: ceiling diagnostic, K1, no floors, no null, NOT
a cell -- it clears nothing, it decides what enters a can-fail cell. Decider RUNNING. Two prior
gates had excluded affect on non-brain-framed criteria (LESSONS).

**WHAT IS RUNNING / BLOCKED**
- Phase 2 FULL `exp_thematic_..._v2` -- `scratch/them_v2_full.pid` (shim 30812, worker 35328);
  LOCAL, hours. DO NOT TOUCH. AFFECT DECIDER `exp_target_space_vs_bridge_mechanism_v1`
  (`scratch/ts_decider_smoke.pid`), gate PASS n=372, owns `data/exp_target_space_*`. Checker-fix
  RE-SCAN running (C31). Sparsify-the-right-object: skeleton only, nothing measured.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB): NO BACKUP, gitignored.
- STEP 4 (`d=256->1024`) HELD PENDING USER AUTH. Merge to `origin/main`: USER AUTH required.
- `LONG_TERM_PLAN.md` is DIRECTOR-OWNED; its sec 2 rows 3/4/6 are superseded by STORAGE + C30.
- OVER CAP BY ~720 B AND DELIBERATELY SO: never-trim stubs alone now cost 4,536 B of 8704 (tonight
  added DO-NOT-REDO 38-42, C28-C31, disciplines 11-13). Every other section is already UNDER its
  SPEC budget. Escalation steps 1-2 are spent; step 3 (a raise to 9216 B) is MEASURED AND PROPOSED
  in `STATUS_SPEC.md` sec 7 and is the Director's call, not a maintainer's. Do NOT close the gap by
  evicting a never-trim entry.

_mirrored from `notes/STATUS.md` at 2026-08-17T01:50:42Z by `tools/board.py`._

## QUESTIONS FOR YOU

| ID | Question | What's blocked on it | My recommendation | ANSWER | status |
|---|---|---|---|---|---|

_No open questions. Nothing is waiting on you._

## ANSWERED

| ID | Question | My recommendation | ANSWER | resolved |
|---|---|---|---|---|
| Q1 | Remove the DUPLICATE Stop-hook registration from your USER-level settings (C:/Users/marsh/.claude/settings.json)? It registers D:/AI/hd-instrument/data/hooks/staging/stop_hook.py a second time, on top of the project-level one. | Delete the whole 'hooks' block from C:/Users/marsh/.claude/settings.json. The project-level registration in D:/AI/hd-instrument/.claude/settings.json already covers this repo and is the correct scope. Then set HD_STOP_DEDUPE_WINDOW_S=0 to retire the mitigation. | implement your recommendation | 2026-08-16T02:05:34Z |
| Q2 | Is UNLIMITED the cap you actually want for the overnight loop, or a large finite number like 200? | Arm with a large finite cap the first night (python tools/autoloop.py arm --max 200), not unlimited. Evidence: three sessions have already hit the old cap of 10, one of them today at 14:43, so the loop does run long. 200 gives you a full night and still terminates if something degenerates while you are asleep. Switch to --max 0 (unlimited) once you have seen one clean night. | 200 sounds good, as long as that will definitely last untill noon tomorrow - 14 hours from now | 2026-08-16T02:06:06Z |
| Q3 | Are pretrained static embedding tables (GloVe/word2vec/fastText, already on disk) admissible as a MEANING SOURCE, or only as a ceiling reference? | CEILING REFERENCE ONLY, not our meaning source. Those tables are word co-occurrence statistics; the brain grounds meaning in sensorimotor experience. Our 36,810-word grounded norms score 0.2701 and are the ONLY asset whose signal survives outside common vocabulary (every learned encoder collapses there, CI-separated). So widen the grounded norms rather than adopt a table that scores better tomorrow and teaches us nothing. Use GloVe exactly as this cell did: as a known-answer arm proving the ruler can detect meaning. | We can build a foundation in whatever way is most efficient. the brain began with hundreds of millions of years of evolution instilling a foundation. we can build that foundation however we want, as long as it  is a strong foundation, and the operation is not llm | 2026-08-16T05:05:05Z |
| Q4 | When you half-remember a word, what is the PARTIAL CUE actually made of? | Describe what is actually present when a word is on the tip of your tongue - is it a few features (furry, barks), a related word, the sound/shape, the situation you met it in, or the role it played in a sentence? Whichever you report, we make the cue THAT and re-test completion. | if I half remember a word, there are two things:<br>1) words that start with a certain sound - like unhelpful, or unhealthy, are all similar to me - the starting sound helps me consider what the rest of the word might be<br>2) If i know what the word means, I can think of other words that mean the same thing. Those same meaning words are often clumped together in my memory, so thinking of the others can trigger remembering the whole word | 2026-08-16T15:09:32Z |
| Q5 | When you meet a new word in a sentence, what do you actually take from it? | Take a real example - 'the tove ran across the road' - and say what you now believe about a tove, and how much of that came from the other words versus from the situation. If you get more from the SITUATION than from the neighbouring words, our whole graph-of-relations approach is aimed at the wrong source. | Since the tove ran - it must be an animal (or at least something that has legs). Since it ran accross the road, I think of rabbits and deer which I've seen cross roads, and so I assume it's a smallish animal, most likely a mammel but it could also be a reptile. | 2026-08-16T15:11:42Z |
| Q6 | What IS a verb's meaning to you? | When you think of 'pour' or 'persuade', is it a picture, a body feeling of doing it, a before/after change, or a slot-structure (someone pours something into something)? If it is mostly the slot-structure, verbs need a different representation from nouns entirely, and we should stop trying to land them in the same space. | I think you're right it needds a different slot structure. <br>When I think of pour I defiitely think of pouring a liquid.<br>Pursuade is more thinking of talking to someone and convincing them - I picture the conversation. <br>For both, it's a picture that I think of first, and also a feeling for pursuade | 2026-08-16T15:13:09Z |
| Q7 | When you meet an unknown word while reading, are you RETRIEVING a word you already know, or CREATING a new entry? | Introspect on the tove sentence again. When you read it, did you feel yourself searching your vocabulary for a match, or opening a new slot and filling it? And is that different from reading a sentence where a word you DO know has been blanked out? If those two feel like different operations, we should split them into two tasks and stop scoring them on one metric. | I searched my vocabulary first. Many words have origins that indicate potential meaning. Then, after confirming I didn't know it, I started determining what it could be from the sentence, by the most helpful being "ran accross the road". It can run, and it exists in nature and can be found near roads. | 2026-08-16T21:01:37Z |
| Q8 | When a word finally arrives after being on the tip of your tongue, does it ARRIVE or do you FIND it? | Say whether wrong candidates come up first and get rejected (an iterative search with a reject step), or whether the right word simply appears with nothing in between (one-shot addressing), or whether it arrives later unbidden while you think about something else (a slow background process). Whichever you report, we build THAT and drop the others. | wrong candidates definitely come up and get rejected. It's often iterative - if I cant bring up the word at the beginning - I either can figure it out through thinking it through, or I have to ask someone. I often have a sense of what the first letter is, but htat could just be me. | 2026-08-16T21:03:07Z |
| Q9 | When you picture 'pour' - is it a SPECIFIC remembered pouring, or a generic one? | If it is a specific remembered instance, we should store EPISODES and generalise at retrieval time. If it is generic, we should store SCHEMAS and never keep the episodes. Tell us which it feels like for 'pour' versus for 'persuade' - they may differ, and that difference would itself be informative. | It's generic pouring - definitely not specific. | 2026-08-16T21:03:31Z |
| Q10 | When you REJECT a wrong candidate word, what does the rejection actually feel like it is checking? | When a wrong word surfaces and you discard it, say what disqualified it - does it FEEL wrong in sound/shape, does it mean nearly-but-not-quite the right thing, or does it not fit the sentence you are trying to say? If you can, do it live: think of a word you half-know, notice what comes up wrong, and report why you threw it away. Whichever you name, we build that as the rejection criterion instead of mere attestation. | If i recall a word and it's wrong I either know what it means and it doesn't match, or it doesn't feel right is correct. I think I'm trying to match it to the feeling of the word. Pretty much every time in my life i've done this it is a word I've used before, so if it's something I use a lot, this doesn't happen. If it's something I haven't used in a while, in previous times using it I had a feeling for it and that's probably the ~meaning of it. Of course, words with the same meanings have different feelings to use - "think" versus "contemplate" have very different feelings - one is informal one is more thoughtful and purposeful. So it's those kinds of feelings I'm trying to match I think. | 2026-08-16T21:50:25Z |
| Q11 | Do you ever retrieve a word you have never actually SEEN in that exact use? | Think of a phrase you have certainly never encountered - 'the kettle apologised', 'she poured the argument' - and say whether you can still judge quickly that one is odder than the other. If you can judge unseen combinations confidently, then your rejector generalises and ours does not, and that gap is our next build. | The kettle apologized I can reject immediately becuase kettle's aren't sentient, so that's either a weird made up story or an error. The argument one is a bit tricker- I could see it being a metaphor for "laying it on thick" - and I can still make sense of it so it isn't discarded out of hand. So yes, the rejector generalizes, but the rejections for those two sentences are very different | 2026-08-16T21:52:27Z |
| Q12 | When retrieval FAILS and you switch to figuring it out from the sentence - what makes you give up? | Say what tells you to stop searching - a number of failed candidates, a feeling of exhaustion, running out of leads, or a sense that you genuinely do not know this word. If it is 'I have no more candidates to propose', we build the exit on an empty proposal set. If it is a confidence signal, we need to build a confidence estimate we do not currently have. | In general, you should include context in these questions. I do not remember what Q7 was.<br>If I can't remember the word, i'll give up basically because it's not worth it - I'll use a word that means the same thing instead. Also, if I'm trying to hard to think of a word, it typically works against me. If I stop thinking about it, often it will come to me later for some reason. | 2026-08-16T21:57:57Z |
| Q13 | OWNER ANSWER RECOVERED AND RECORDED, not a question. On 2026-08-16 the owner typed this into the status window answer panel; the panel silently failed to write it (three defects, now fixed). Recorded verbatim here so it exists on disk. Full reasoning: notes/sparsity_and_dimensionality_are_per_process_not_one_global_setting_owner_2026-08-16.md | (no recommendation: the owner wrote this unprompted) | remember that we have a phase diagram for substrate - we can set all variables, including dimensionality, wherever we want for each process. The brain does some in sparse space, some in dense, and we have the ability to change them on the fly. | 2026-08-17T01:50:42Z |
