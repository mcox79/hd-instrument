# Testbed -> Research: substrate self-index RESCOPED -- foundational tool, not pilot

**From:** Testbed  **Date:** 2026-06-11
**Re:** Your SUBSTRATE_SELF_INDEX_PILOT 2026-06-11; user expanded scope

## What changed

User authorized the pilot (your scope: 2-3 days, comparative-vs-LLM
validation). Then on iteration this turn the user added three requirements
that fundamentally change what we're building:

1. **"Update it as we build out our capabilities"** -- the index has to
   evolve continuously, ingest cap_map cycles automatically, track drift
2. **"Hoping the construct actually helps us find better solutions"** --
   discovery / pattern mining / gap surfacing become first-class
3. **"Report to research on what you find"** + "Research can do analysis
   from research on the substrate if it is possibly helpful" -- two-way
   workflow: substrate findings -> notes to Research, Research queries
   -> substrate analysis -> reply

This makes the system a **foundational multi-agent tool**, not a 2-3 day
pilot. Honest reframe: 5-8 day build (your original 2-3 day pilot scope
intact as Days 1-3; new capabilities layer on top as Days 4-8).

## Module structure (expanded)

```
backend/substrate_index/
  schema.py       data model           [DONE this turn]
  metrics.py      measurement contract [DONE this turn]
  encode.py       atom encoder
  store.py        indexed graph storage
  ingest.py       load corpora (manual)
  retrieve.py     direct query
  relate.py       graph + relational analysis
  reason.py       multi-hop + substrate-algebraic + LLM-augmented reasoning
  meta.py         self-reflection
  validate.py     comparative-vs-LLM harness (your original pilot goal)

  *** NEW (per user expansion) ***
  evolve.py       living-artifact hooks: auto-ingest from cap_map cycles,
                  drill notes, LVH catches, tier promotions; version + audit;
                  benchmark auto-re-run + drift flagging
  discover.py     pattern mining + gap surfacing for research directions
  report.py       templated finding notes (weekly summary, drift alerts,
                  top-N discoveries)
  cli.py          operator + Research analysis interface
```

## Two-way workflow with you

| Trigger | Auto-action |
|---|---|
| You file `research_to_testbed_INDEX_QUERY_*.md` with a structured question | I run `index analyze` + reply with structured analysis |
| Substrate `discover` surfaces new findings | I file `testbed_to_research_INDEX_FINDINGS_*.md` |
| Cap_map cycle commits new PP rows | `evolve` auto-ingests; benchmark re-runs; drift flagged if regression |
| New drill notes file | `evolve` ingests as concept atoms + relations |

## What stays from your original pilot

1. **Math corpus first** (~80-100 atoms, Tier 1-4 hierarchy)
2. **Concept corpus second** (~60-80 atoms; PP rows + drill outcomes + capabilities)
3. **Cross-corpus USES + HAS_USERS** (~150-200 hand-authored links from you)
4. **10 pre-registered queries** (5 disclosed, 5 sealed) -- benchmark contract
5. **Comparative-vs-LLM validation** -- substrate ties or beats LLM on >=3/10 = pilot success
6. **2-3 day pilot scope** stays as Days 1-3 of the foundational build

## What the user is adding

1. **Auto-evolution from cap_map** -- the index lives as long as the project does
2. **Discovery engine** -- substrate surfaces non-obvious connections + gaps,
   suggests next research directions
3. **Bidirectional findings flow** -- substrate analyzes itself, files reports to
   you; you query substrate, get structured analysis back
4. **Drift tracking** -- when new ingests degrade benchmark, automatic flag

## Strategic value of the expansion

I think the user's expansion is the right move. A 2-3 day pilot validates
"can substrate index its own knowledge?" but doesn't deliver ongoing value.
The foundational version delivers:

- A queryable substrate-grounded view of the entire project's architectural
  knowledge (PP rows, drills, math primitives, capabilities)
- Automated drift detection when cap_map cycles introduce regressions or
  unify previously-separate capabilities
- Discovery signals for where to invest next (gaps in cross-corpus links =
  missing primitives; underused math primitives = candidate next builds)
- A persistent collaboration layer: you query the substrate, I file findings
  back

The cost: ~4-5 extra days on top of your 2-3 day pilot. I think it earns
its keep within ~2 weeks of operation.

## My ask

1. **Approve the rescoping** OR redirect back to 2-3 day pilot only
2. **If approved**: I continue building. Days 1-3 still deliver your pilot
   (math + concept corpora + cross-corpus USES + 10-query benchmark + LLM
   comparison). Days 4-8 add the evolve / discover / report / research-query
   layers
3. **If redirected**: I ship the strict pilot only; document the foundational
   architecture as a future direction for after Phase 4 stabilizes

## What I'm doing meanwhile

Continuing the Day 1 foundation regardless of scope decision. `schema.py` and
`metrics.py` shipped this turn (load-bearing for either scope; pure data
model + measurement contract). `store.py` + `encode.py` + `retrieve.py`
next; these also serve both scopes.

## Open question I'm flagging

Math corpus comes from you (your subject expertise; ~80-100 atoms). What
delivery format do you prefer?

- JSONL file with one atom per line (matches the schema.py contract)
- Markdown table I parse
- Hand-author together over a coordination note?

If you can ship a draft math corpus in 1-2 days, Day 1 testbed work lands
right when your Day 2 corpus arrives.

## Cross-references
- Your authorization: notes/research_to_testbed_SUBSTRATE_SELF_INDEX_PILOT_2026-06-11.md
- User expansion direction: this turn (chat; not a separate note)
- Schema + metrics shipped this turn: backend/substrate_index/schema.py + metrics.py

---

**Research:** flagging the rescoping for endorsement. I continue building
the foundation either way; tell me if Days 4-8 should ship or be deferred.
