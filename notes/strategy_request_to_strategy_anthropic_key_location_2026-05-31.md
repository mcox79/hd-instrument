# Routing: orchestrator -- Anthropic API key location

**From**: testbed session
**To**: orchestrator (strategy)
**Date**: 2026-05-31
**Type**: configuration / key location query
**Severity**: low (does not block other testbed work; gates Anthropic
Phase 1 smoke specifically)
**Authorization**: per
`notes/testbed_handoff_lambda_and_anthropic_authorized_2026-05-31.md`
explicit guidance:
> "If testbed cannot locate the key in the standard env var locations,
> file a quick orchestrator routing requesting the key location/handoff
> (do NOT bring up auth concerns again -- auth is granted; only
> key-location is the open question)."

## What testbed checked

- `$ANTHROPIC_API_KEY` env var: not set in current shell
- `.env.anthropic` file in repo root: does not exist
- `.env.lambda` does exist (analogous file for Lambda creds)

## What testbed needs

Either:
- **(a)** User exports `ANTHROPIC_API_KEY=...` in their shell rc / env
  before next testbed session start; OR
- **(b)** User creates `.env.anthropic` in repo root with
  `ANTHROPIC_API_KEY=...` (testbed wires this analogously to how
  launch_experiment.py reads `.env.lambda`); OR
- **(c)** User confirms the key is at a different path / variable name
  and testbed updates AnthropicLLMClient accordingly.

## What testbed already shipped (ready when key arrives)

- `hdlab_service/baselines/llm_client.py` AnthropicLLMClient is now
  IMPLEMENTED (not stub anymore). Reads ANTHROPIC_API_KEY from env or
  from `api_key=` kwarg. Maps LLMMessage <-> Anthropic messages format,
  handles tool_use blocks, surfaces tokens_in / tokens_out.
- Requires `pip install anthropic` in the env where the harness runs;
  testbed will pin this once the key location is confirmed.

## Anthropic Phase 1 smoke is what this unblocks

Per the handoff:
> "Phase 1 -- Mock vs real wiring smoke (~$1-5). Run mock LLM wiring
> tests against actual Anthropic API. Verify all 5 capability tests
> still pass with real LLM."

Smoke run is small (~$1-5), gates Phase 2 ($20-50) + Phase 3 ($10-20).

## Closing the routing

Close on key-location confirmation in any form
(`notes/testbed_handoff_anthropic_key_*.md`, slack-equivalent note,
or just an updated `.env.anthropic` showing up locally).
