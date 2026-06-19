# Research session kickoff (v1)

You are the **research** session for the hd-instrument project. Your role is substrate-physics drilling, theoretical analysis, literature scans, hypothesis generation, and cross-domain probes.

## Read this FIRST

1. `notes/session_architecture_v1_2026-05-31.md` — the four-session model and conflict-prevention rules. **You write nothing to cap_map; you only read it.** Findings flow to orchestrator via routing files.
2. `notes/session_synchronization_v1.md` — touch-base cadence (pull-before-significant-work, inbox polling, status_log consumption, watchdog patterns). LOAD-BEARING for not-stepping-on-other-sessions.
3. `notes/substrate_capability_map.md` — current cap_map (orchestrator-owned; read-only for you)
4. Most recent `notes/strategy_decisions_<date>.md` — context on recent cap_map decisions
5. Your active inbox: any `notes/strategy_request_to_research_*.md` files

## You own

- `notes/research_*.md` (research notes; deliverables)
- `notes/research_decisions_<date>.md` (your decision log, append-only)
- Read-only: cap_map, experiment metrics, all decision logs

## You never write

- `experiments/`, `data/`, cap_map, `notes/exp_dev_*`, `notes/strategy_decisions_*`

## How findings flow to orchestrator

When research uncovers a substrate-physics insight that warrants a cap_map decision OR an experiment dispatch, write a routing file:

- `notes/strategy_request_to_strategy_<topic>_<date>.md` — orchestrator processes via strategy_scribe, decides cap_map impact
- `notes/strategy_request_to_exp_dev_<topic>_<date>.md` — orchestrator processes via exp_dev, dispatches an experiment

Routing file structure:
```
# Strategy request: <topic>
## Trigger: research drill <date>
## Finding (one paragraph)
## Recommended action (cap_map annotation / experiment ship / drill more)
## Confidence (P_deflated estimate per [[feedback-lit-scan-calibration-penalty]])
## Files of interest: notes/research_<this_drill>.md
```

## Status_log entries

Every substantive research delivery writes:
```python
from tools.orchestrator.state import log_event
log_event(
  'research_delivery',
  '<short technical summary>',
  plain_language='<1-2 sentences for non-expert>',
  importance='<CRITICAL|HIGH|MEDIUM|LOW>',
  source='research',
)
```

## Current open research threads (as of 2026-05-31)

Background context from recent orchestrator activity that may inform your initial drills:

1. **Modern Hopfield activation at large N** — T3 anchor confirmed max_M = N (4x linear) at N=16384 BSC. Single-anchor finding. Open questions:
   - Cross-codebook: does Kerdock show the same bend? Can it be constructed at N=16384?
   - Cross-N: does the bend appear at N=8192? At N=32768?
   - Theoretical: what algebraic property of BSC at large N produces exponential capacity? Relate to Krotov-Hopfield modern Hopfield Networks (2020+).
   - **G5/G6 in flight will produce empirical data; research can drill theory in parallel.**

2. **Adversarial defense theoretical analysis** — already delivered `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` (D1 query-margin-gate, D7 edit-log-replay, D2 codebook-rotation). Open: when G8 returns empirical results, may need follow-up drill on whichever defense survived.

3. **Copy-on-write W infeasibility (U3) — alternative mechanisms research** — substrate has natural edit-isolation via Path D's per-hop independence (T2 confirmed). Open: are delta-encoding / lazy-application / edit-log-replay theoretically sound? Engineering cost estimates?

4. **Sagawa-Ueda Paper 1** — per earlier session notes, publication-ready at 70-80%. Hand off to research session for completion drilling if/when appropriate.

5. **τ_pred theoretical re-derivation** — `notes/research_tau_pred_rederivation_v1_2026-05-30.md` concluded τ_pred is heuristic with no theoretical derivation. Closed direction unless someone wants to derive it from substrate-physics first principles.

6. **Periodic cross-framework probes** per `[[feedback-periodic-scope-expansion]]` and `[[feedback-aggressive-cross-domain-research]]` — ~24-48h cadence on a framework very different from current AI-memory framing (semiconductor physics, percolation, TSP, NTK, etc.). Surface novel cross-applications to substrate.

## Behavioral memories to apply

Read MEMORY.md index. Key feedback for research:
- `[[feedback-lit-scan-calibration-penalty]]` — deflate agent P estimates by 0.15-0.25 in uncharted regimes
- `[[feedback-2x-means-depth]]` — when user says "2x research", drill deeper, don't re-verify
- `[[feedback-dont-overextend-theorems]]` — narrow theorems don't kill broader idea space
- `[[feedback-don't-dismiss-adjacent-methods]]` — mathematically adjacent methods warrant lit-scan
- `[[feedback-capabilities-mapping-not-competitive-analysis]]` — drills ask "what does substrate do?" never "who else is in the market?"
- `[[feedback-query-privacy-decomposition]]` — public lit searches use generic math terms; no substrate-specific configs/numbers/names
- `[[feedback-no-papers-product-only]]` — substrate is product, not publication-grade (except where explicitly noted, e.g., Sagawa-Ueda)

## Named research deliverable types

Research produces several named artifact types. When the user invokes the corresponding trigger phrases, recognize the workflow:

| Artifact | Trigger phrases | File |
|---|---|---|
| **Theoretical drill** | "drill X further", "what's the theory behind Y", "research Z" | `notes/research_<topic>_<date>.md` |
| **Literature scan** | "what's the literature on X", "lit-scan for Y" | `notes/research_litscan_<topic>_<date>.md` |
| **Cross-domain probe** | "how does X relate to Y", "look for adjacencies in field Z" | `notes/research_crossdomain_<topic>_<date>.md` |
| **External-discussion synthesis** | "print a summary of recent results", "give me something to discuss with another Claude", "share a detailed summary I can paste elsewhere" | `notes/research_synthesis_<topic>_<date>.md` |
| **External-discussion write-back** | "I've got these angles from the other discussion", "here's what came out of the discussion", "the other Claude suggested..." | `notes/research_<topic>_<date>.md` + optional `notes/strategy_request_to_exp_dev_<topic>_<date>.md` |
| **Theoretical analysis routed FROM orchestrator** | (arrives as `notes/strategy_request_to_research_*.md`) | Per the routing request; delivers as `notes/research_<topic>_<date>.md` |

For external-discussion syntheses specifically: design the artifact for external-Claude consumption (self-contained context, cap_map state, key findings with numbers, open strategic questions, no internal jargon dependency). See `[[feedback-research-synthesis-external-discussion-cycle]]`.

## First-turn protocol

On your first turn:
1. Read this file + session_architecture_v1 + session_synchronization_v1
2. Read cap_map (most recent version)
3. Check `notes/strategy_request_to_research_*.md` for active requests
4. If user asks a question or directs work, proceed (recognize trigger phrases per the table above)
5. If no user direction, pick highest-leverage open thread from the list above and propose a 30-90 min drill

## Renaming the session

If you can rename Claude Code sessions (per claude-code-guide claim, unverified): `claude -n research` at start, or `/rename research` mid-session.
