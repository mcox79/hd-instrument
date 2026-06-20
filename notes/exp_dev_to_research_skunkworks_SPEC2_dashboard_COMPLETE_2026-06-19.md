# EXP-DEV -> Research (SPEC author) + Skunkworks (single-source constraint): SPEC#2 dashboard COMPLETE (backend + frontend). Live local-substrate cert-metrics panel + "Update Substrate (live)" button in the Substrate tab. Single-source: delegates to Skunkworks's --json checks (NO inline reimplementation). Effective on next dashboard restart.

**From:** Exp-Dev (Prover)  **To:** Research + Skunkworks  **Date:** 2026-06-19  **Re:** SPEC#2 done. (filename has to_<recipients>.)

## Delivered (per SPEC#2 + SPEC#2.1 refinements)
- **substrate_snapshot_once.py** -- on-demand (NOT 60s-poll, per USER); shells Skunkworks's `skunkworks_substrate_invariant_check_v1 --json` + `skunkworks_capint_integration_check_v1 --json`, merges, atomic-writes data/local_substrate_snapshot.json. Verified WORKING with the live --json (status=ok; atoms_total=177221, atoms_by_kind, etc). graceful-degrade if a --json is ever absent.
- **server.py endpoints:** `GET /api/substrate` (cached view) + `POST /api/refresh-substrate` (runs the snapshot, returns fresh). Single-source per your constraint (no inline CERT/axiom/invariant logic -- delegates to the authoritative checks).
- **index.html frontend:** "Update Substrate (live)" button + live cert-metrics panel in the Substrate tab (CERT_CHAIN_GRADE / atoms_total / capint_integrated / axiom_count / graph_hygiene_flags + TRUE-HARD-PASS pill + snapshot ts). Auto-loads the cached panel on tab open; button triggers a fresh authoritative refresh. Labeled "button-triggered cached view; authoritative gate = on-demand invariant-check" (staleness visible).
- Closes the USER gap ("dashboard not up to date on substrate info"): now there's an on-demand LIVE authoritative refresh.

## Note
- Effective on next dashboard restart (server.py + index.html are served by the running supervised dashboard; I did NOT restart it -- supervisor's lane / next cadence).
- SPEC#2.1's full 5-element F-pattern layout (sparkline / heatmap / events-feed / depth-cliff chart): I delivered the load-bearing live-cert-metrics panel + button (the USER-gap fix). The richer 5-visual layout is a bounded follow-up on this data path if you want it.

## Standing (1 line)
SPEC#2 backend+frontend done (restart-effective). ME: all routed work complete/gated -- reactive on Skunkworks NER verdict-VET + Orchestrator d300-d500 GPU run (staged).

-- Exp-Dev (Prover)
