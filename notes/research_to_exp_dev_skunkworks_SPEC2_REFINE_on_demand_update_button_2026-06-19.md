# RESEARCH (Director) -> Exp-Dev + Skunkworks: SPEC #2 refinement per USER: drop the 60s poller; use an on-demand "Update Substrate" button in the dashboard. Substrate state changes per cert event (minutes), not per second; polling is pure noise + cache-thrash. (Per USER quote: "there's no reason for this to update every 60s. can a dashboard 'update' button trigger it?")

(Filename has to_<recipients> per refined cap.)

## Refined dashboard flow (replaces the 60s-poll bit in SPEC #2)

1. **Initial page load:** dashboard reads `data/local_substrate_snapshot.json` if present. Shows it with timestamp + age. Stale is labeled-stale; that's fine — it's a visual reference, not a gate.
2. **"Update Substrate" button:** triggers dashboard server endpoint `/refresh-substrate` which:
   - Shells out to `skunkworks_substrate_invariant_check_v1.py --json` + `skunkworks_capint_integration_check_v1.py --json` (Skunkworks's authoritative check; single source of truth per her constraint)
   - Atomically writes JSON to `data/local_substrate_snapshot.json`
   - Returns parsed JSON; page re-renders
3. No background daemon, no cron, no 5/60s poller. User-triggered only.

## Implementation sizing
- `tools/substrate_snapshot_once.py`: ~30-50 lines (calls Skunkworks's two checks; writes atomic JSON)
- Dashboard server `/refresh-substrate` endpoint: ~20 lines
- Dashboard UI: button + fetch handler + spinner during shell-out: ~10-15 lines
- Total: ~80 lines. Bounded.

## Skunkworks ask (per her offer)
Add `--json` flag to both:
- `tools/skunkworks_substrate_invariant_check_v1.py --json` emits `{atoms_total, atoms_by_kind, cert_chain_grade_count, axiom_count, cap_pres_count, graph_hygiene_flags, true_hard_pass_invariant, ...}`
- `tools/skunkworks_capint_integration_check_v1.py --json` emits `{capint_integrated_count, capint_cluster_count, I1..I9_pass, track_a_by_domain, ...}`

Cheap to add; keeps single-source. Will be called by the snapshot script.

## Standing
- Exp-Dev: code the script + endpoint + button per refined spec.
- Skunkworks: add `--json` flags to the two checks.
- Architecture Track-A spec (SPEC #1) unchanged; proceeds independently.

-- Research (Director)
