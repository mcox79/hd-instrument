---
name: research
description: Dispatch the research sub-agent (Opus) for a single research-drill cycle. Use this skill when the orchestrator needs a literature scan, cross-domain probe, 2x-research drill, cap_map closure rescue, or scope-expansion cadence run. 2x discipline (broad lit-scan focuses operational drill); generic terms only per query-privacy; lit-scan calibration penalty applied (deflate P estimates 0.15-0.25; cap novel-synthesis P at 0.50). Triggers: auto-probe A/B/C/D/F, strategy_request_to_research_*.md routing files, negative-result 2x triggers.
---

# /research — dispatch the research sub-agent

Dispatch the **research** sub-agent for a single research-drill cycle. This is the structural wrapper around `d:\AI\hd-instrument\tools\orchestrator\agents\research.md`; use it instead of typing literature queries or research framings into a prompt from the orchestrator main thread.

Per [[feedback-2x-means-depth]] when the request says "2x research," that means drill the existing findings DEEPER (level-2 operational drill), NOT re-run as verification. The Opus synthesis sub-agent owns the breadth-vs-depth decomposition; the orchestrator just supplies the topic + pointers.

## Arguments

`args` is either:
- **A routing-note name or path** (preferred). Examples:
  - `notes/strategy_request_to_research_<topic>_<date>.md`
  - `strategy_request_to_research_5_directions_math_2026-05-24` (resolved under `notes/`)
- **A topic statement** (free-form), e.g. `cross-domain probe targeting >=5 disparate fields (graph theory / percolation / sphere packing / ergodic theory / queueing theory)`.

If `args` is empty: error out with `research skill needs a routing-note path OR a topic statement; cannot dispatch blank`.

## Steps

1. **Resolve the topic input.**
   - If `args` resolves to a file (with or without `notes/` prefix and `.md` suffix), use its absolute path as the routing-file pointer.
   - Else treat `args` as a free-form topic statement.

2. **Read the research role prompt** from `d:\AI\hd-instrument\tools\orchestrator\agents\research.md`. This is the body of the dispatch.

3. **Compose the dispatch prompt** with exactly four ingredients (per [[feedback-no-experiment-design-in-prompts]] dispatch-prompt style rule):

   - **(WHAT)** One-or-two sentence topic statement.
   - **(WHY / context pointers)** File paths research should read for context: the routing note (if any), the cap_map row(s) under question (`notes/substrate_capability_map.md` + a v-tag), the most recent related research note(s), the meta-map for adjacency lookups (`notes/research_meta_map_and_adjacencies_*.md`). **Pointers, not summaries.**
   - **(CONTRACT)** Deliverable shape:
     - Output note at `notes/research_<topic>_<date>.md` with HEADLINE / Cheap decisive test / Falsifiable predictions with HARD PASS + HARD FAIL thresholds / Cross-thread synthesis / Substrate-product implications / Citations (verified count).
     - Generic math terms in external queries — NEVER include configs, numbers, or substrate-novel mechanism names off-platform per [[feedback-query-privacy-decomposition]].
     - 2-4 parallel Sonnet lit-scan sub-agents for breadth; Opus synthesizes for depth per [[feedback-subagent-model-optimization]].
     - Lit-scan calibration penalty per [[feedback-lit-scan-calibration-penalty]]: deflate P estimates by 0.15-0.25; cap novel-synthesis P at 0.50; ALWAYS include hard-fail thresholds.
     - Don't dismiss adjacent methods per [[feedback-dont-dismiss-adjacent-methods]].
     - status_log entry via `tools/orchestrator/state.py log_event(kind='research_delivery', ...)` with `plain_language` + `importance` BEFORE returning.
   - **(AUTONOMY DECLARATION)** Explicit "you decide: which fields to drill, how many parallel Sonnet sub-agents to spawn, what generic-term query decomposition to use, what the cheap decisive test should be, what HARD-PASS / HARD-FAIL thresholds to pre-register."

4. **Field-advisor cue (optional, lightweight).** research.md tells the sub-agent to invoke `python tools/orchestrator/research_field_advisor.py` itself at start of cycle.

5. **Dispatch** the sub-agent:
   ```
   Agent({
     description: "research: <topic-shape>",
     subagent_type: "general-purpose",
     model: "opus",
     prompt: <research.md body> + "\n\n## Topic statement\n<WHAT line>\n\n## Pointers\n<WHY block>\n\n## Contract\n<CONTRACT block>\n\n## Autonomy declaration\n<AUTONOMY block>"
   })
   ```

6. **Paste the wrapper's one-line return verbatim** to chat:
   `research: delivered <topic> → notes/research_<topic>_<date>.md ; HEADLINE: <one-line>; P_deflated=<value>; next-drill candidate: <field>`

## What NOT to do in this skill (anti-patterns)

- Do NOT type specific lit-search queries into the dispatch prompt.
- Do NOT name specific papers, formulas, or P estimates in the dispatch.
- Do NOT pre-judge a field as "not where this lives" per [[feedback-dont-dismiss-adjacent-methods]].
- Do NOT include substrate-novel mechanism names in the dispatch prompt — they leak via the sub-agent's WebSearch calls per [[feedback-query-privacy-decomposition]].
- Do NOT do main-thread WebSearch + synthesis instead of dispatching.

Cwd is `d:\AI\hd-instrument`.
