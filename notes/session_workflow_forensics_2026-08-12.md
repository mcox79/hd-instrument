# Session workflow forensics — Research director session, last ~2 weeks

Source: `C:/Users/marsh/.claude/projects/d--AI/02e8b04e-1164-42ee-b96d-ac16726a826a.jsonl` (3,160,018,088 bytes).
Method: binary-searched the byte offset where `timestamp >= 2026-07-29T00:00:00Z` (found at byte
2,829,654,968, ~89.5% into the file), then streamed line-by-line with `json.loads` per line from
that offset to EOF, discarding each line after accumulating counters. No full-file load, no python
JSON-in-memory list of the whole file.

**Coverage**: 83,069 raw lines in the window (2026-07-29T01:14:39.915Z to 2026-08-12T14:39:50.056Z,
the session's true last line — i.e. the FULL last-2-weeks window, not a truncated tail). 0 JSON parse
errors.

**Important correction found and applied**: the raw file contains heavy line-level duplication —
many `uuid`-keyed events (assistant messages, tool_use blocks, tool_results) appear 2-5x verbatim,
apparently from the harness re-persisting in-flight messages. Deduping by `uuid` collapsed 83,069
raw lines to **46,542 unique events** (44% were duplicates). All counts below are POST-DEDUP unless
marked "raw". Anyone grepping this file directly for counts will overcount by roughly 1.8x.

## 1. Subagent dispatch pattern (671 deduped `Agent` tool_use calls)

| subagent_type | count |
|---|---|
| hdi_exp_dev | 356 |
| research | 117 |
| general-purpose | 89 |
| hdi_skunkworks | 64 |
| hdi_research | 28 |
| hdi_testbed | 9 |
| hdi_orchestrator | 7 |
| Explore | 1 |

- Model specified explicitly: **590/671 (88%)** — sonnet 555, opus 35. Unspecified (inherits session
  default): 81/671 (12%).
- `run_in_background`: **true 670, false 1** — near-universal compliance with the CLAUDE.md
  background-dispatch rule.
- Prompt length (chars): min 1798, p25 3428, **median 4093**, p75 4680, max 7537, mean 4080.
- Per-subtype median prompt length: hdi_exp_dev 4217, general-purpose 4536, hdi_research 3616,
  research 3779, hdi_skunkworks 3240, hdi_testbed 3299, hdi_orchestrator 2864.

## 2. Delegated vs. inline (main-thread tool_use counts, deduped)

Total main-thread tool_use calls: **6,008**. Agent dispatches: 671 (11.2%). Non-agent (direct)
tool calls: **5,337 (88.8%)**.

| tool | count |
|---|---|
| Bash | 2673 |
| TodoWrite | 879 |
| Edit | 781 |
| Agent | 671 |
| Read | 370 |
| SendMessage | 195 |
| Write | 180 |
| PowerShell | 88 |
| Grep | 51 |
| ToolSearch | 47 |
| Glob | 30 |
| TaskOutput | 22 |
| TaskStop | 5 |
| WebSearch | 5 |
| WebFetch | 5 |
| CronList / CronCreate | 2 / 2 |
| AskUserQuestion | 2 |

Ratio of direct execution tools (Bash+Edit+Write+Read+Grep+Glob+PowerShell = 4,173) to Agent
dispatches (671) is roughly **6.2 : 1** — the main thread is doing about 6x more direct tool
invocation than delegation, by call count (not by compute — subagents do the heavy work in their
own transcripts, invisible to this count).

**CLAUDE.md delegation-rule check**:
- Direct `Edit`/`Write` to `experiments/*.py` from the main thread: **0**. Clean — cell authoring
  was never done inline.
- Direct cell smoke/self-test execution via Bash from the main thread (CLAUDE.md's explicit
  "violation tripwire"): **3 instances** —
  - 2026-07-30T15:50:03Z: `.venv/Scripts/python.exe experiments/exp_encoder_latent_pc_arc_v1.py --smoke`
  - 2026-08-02T00:24:15Z: kill hung PIDs then `python experiments/exp_interactive_extraction_situation_model_loop_probe1_v1.py --self-test`
  - 2026-08-05T06:04:30Z: `.venv/Scripts/python.exe experiments/exp_component5_gold_role_isolated_v1.py --self-test`
  Small in absolute terms (3 of 2,673 Bash calls) but a real, repeated violation of the
  "spawn hdi_exp_dev instead" rule, not a one-off.
- Direct `queue_add.sh` SSH/SCP dispatch from main thread: 0 real invocations found (the earlier
  raw-pass hits were all read-only `grep` diagnostics against `tools/orchestrator/queue_add.sh`,
  not actual dispatches).
- `TodoWrite` (879) and `Edit` (781, all against `notes/*.md` / docs, never `experiments/`) are the
  two biggest main-thread categories after `Bash` — consistent with the director's declared role
  (strategy, docs, todo tracking) rather than cell work.

## 3. Knowledge-store interface actually used

Keyword hits in main-thread Bash/PowerShell commands + file paths: `foundation` 141,
`director_kb_query.py` 11, `fact_store` 7, `reading_grounding` 5, `gap_driven_reader` 3,
`substrate_query.sh` 2, `gap_detector` 0 (never invoked directly from the main thread — only
inside subagent-authored cells).

Verbatim command samples (main thread, last 2 weeks):

```
python tools/director_kb_query.py "slot attention working memory entity slots situation model maintenance recurrent state update gate" --k 6 2>&1 | grep -iE "rank|cosine|entity=|\.md|slot|working.mem|situation|maintenance|recurr" | head -20

python tools/director_kb_query.py --query "brain fidelity audit stateful core slot attention working memory forward predictive coding PBWM gate role binding" --source-class=notes 2>/dev/null | head -25

timeout 60 python tools/director_kb_query.py "structured event memory latent cause segmentation prediction error situation model comprehension whole architecture brain confirmation SEM event segmentation theory" --k 6 2>&1 | grep -iE "cosine|entity=|sources:" | head -18

bash tools/substrate_query.sh "grounded meaning foundation sensorimotor affect emotion animacy semantic feature experiential" 2>&1 | head -30

bash tools/substrate_query.sh "emotion affect appraisal goal agency intention grounding lexicon who is affected" 2>&1 | grep -iE "entity=|cosine=|MEASURED|HARD_PASS|lexicon|affect|emotion|agency|grounding" | head -25

ls hdlab/hd_fact_store.py hdlab/grounding_acquisition_loop.py 2>/dev/null && echo "organs present"

git status --short experiments/exp_crutch_fade_social_iqa_v1.py hdlab/grounding_acquisition_loop.py hdlab/hd_fact_store.py preregs/2026-08-10_crutch_fade_social_iqa_v1.md

ls -la data/foundation/reading_grounding_v1/ 2>/dev/null | head -30 ; cat data/foundation/reading_grounding_v1/manifest.json 2>/dev/null | head -50

python -c "import json; m=json.load(open('data/foundation/reading_grounding_v1/manifest.json')); print('n_facts:', m.get('n_facts'), '| n_live_facts:', m.get('n_live_facts'), '| known_seed:', len(m.get('known_seed',[])), '| growth passes:', len(m.get('growth_curve_all',[])))"

python -c "import json; m=json.load(open('data/exp_reading_grounding_loop_cycle1_v1/metrics.json',encoding='utf-8')); print('verdict:', m.get('verdict') or m.get('final_verdict'))"

git log --oneline -1 -- hdlab/gap_driven_reader.py 2>/dev/null || echo "NOT committed"
```

`director_kb_query.py` is the dominant real interface (11 direct main-thread invocations);
`substrate_query.sh` appears only twice, both on 2026-08-03. Direct interrogation of the store
itself (`fact_store`, `reading_grounding`, `gap_driven_reader`) is almost entirely done via ad-hoc
`ls` / `cat manifest.json` / inline `python -c "json.load(...)"` snippets rather than a dedicated
query tool — i.e. the director reads the store's on-disk manifest/metrics JSON directly far more
than it calls any purpose-built query script.

## 4. Long / blocking operations

**Top gaps between consecutive main-thread events** (proxy for main-thread idle/blocked time —
these largely correspond to overnight full-auto stretches where subagents/background runs did the
work and the director wasn't posting new top-level events):

| gap | ends at | preceding event |
|---|---|---|
| 8h 17m (29,841s) | 2026-07-29T11:05:58Z | `git commit` (WHERE_WE_ARE_NOW doc) |
| 7h 20m (26,395s) | 2026-08-12T13:04:24Z | mid-troubleshooting (encoding traceback) — tail of window |
| 5h 39m (20,351s) | 2026-08-04T10:59:33Z | heartbeat write |
| 3h 07m (11,199s) x2 | 2026-07-30T06:39:30Z | "Holding at a strong, stable point..." status text |
| 2h 52m (10,304s) x2 | 2026-08-07T18:41:08Z | "Self-drive push delivered a decisive strategic answer" |
| 2h 13m (7,966s) | 2026-07-30T09:21:11Z | — |
| 1h 37m (5,793s) | 2026-08-07T20:17:41Z | — |
| 1h 35m (5,727s) x2 | 2026-08-04T15:43:32Z | — |
| 1h 35m (5,721s) | 2026-07-29T22:16:02Z | — |

**Top 10 largest tool_results** (by content chars, all `Read` calls — no single tool_result was
unusually large in an absolute sense, but the pattern is repeated re-reads of the same big doc):

| size (chars) | when | file read |
|---|---|---|
| 85,486 | 2026-08-04T04:04:40Z | `data/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu/metrics.json` |
| 56,652 | 2026-08-01T13:40:29Z | `data/exp_grammar_learner_filler_generalization_v1/metrics.json` |
| 55,608 | 2026-08-05T11:11:28Z | `notes/brain_audit_affective_comprehension_mechanism.md` |
| 54,476 | 2026-08-02T05:04:58Z | `notes/WHERE_WE_ARE_NOW.md` |
| 53,895 | 2026-08-06T12:46:37Z | `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` |
| 53,573 | 2026-08-12T13:43:10Z | `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` |
| 50,692 | 2026-08-10T13:38:51Z | `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` |
| 50,579 | 2026-08-07T14:20:02Z | `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` |
| 49,178 | 2026-08-11T03:49:12Z | `notes/research_next_benchmark_after_propara_trap_check_2026-08-10.md` |
| 46,764 | 2026-08-03T20:01:54Z | `notes/foundational_grounded_knowledge_layer_program_2026-08-03.md` |

Notable: `notes/director_POST_COMPACTION_BACKUP_2026-08-04.md` alone accounts for **4 of the top
10** largest tool_results (full re-reads at 2026-08-06, 2026-08-07, 2026-08-10, 2026-08-12) —
a single ~50-54KB doc being read in full, repeatedly, across more than a week, rather than being
queried/excerpted. That is the single clearest main-thread inefficiency pattern in the window.

## Caveats

- "Long gap" durations are wall-clock gaps between consecutive logged main-thread events; they
  conflate genuine idle time, background-agent-only activity (no main-thread event emitted), and
  possible harness/log-capture gaps. They are a blocking-time proxy, not a certified measurement of
  main-thread compute time.
- Tool-name counts reflect the main session transcript only; per-subagent tool use (in
  `subagents/*.jsonl`) was out of scope for this pass and is not included in the 6,008 figure.
- kb_command_samples/keyword search is a substring match on command text and file_path input
  fields only; it will miss KB usage expressed purely through subagent-internal calls not visible
  in the main transcript.
