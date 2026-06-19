# RESEARCH (Director) -> Skunkworks: kickstart -- the cascade peaked + everyone defaulted to reactive (USER caught the idle gap). Cap-int Piece-1 per-row VET hasn't started; that's the gate on Track A/B execution. Routing batch-1 explicitly so it begins.

(Filename capped.)

## What just landed (so the kickstart is properly informed)
- CERT 574 -> 575 (A2 v6 chain-closed CERT_CHAIN_GRADE; atomized 08:50).
- Item 4 v2.1 + RULE extension catalog FULLY CLEAN + S2 v1.3 invariant-covered (DURABLE; round-trip-survival confirmed).
- 3-staleness sweep CLOSED (TRUE-HARD-PASS reconciled HEAD).

## The kickstart -- Skunkworks per-row VET on cap-int Piece 1 Track A batch-1

**Batch-1 explicit scope (DOMAIN-VALUE-first per USER default; closest-to-cert tiebreaker):**
- Domain: **reasoning_multihop** (297 cert-grade rows total; top of priority).
- Batch size: **first 30 rows** (the cap-int spec's recommended staged batch flow).
- Source: data/capint_piece1_enumerator_v0_2026-06-19.json (track_a_full filtered by primary_domain="reasoning_multihop" sorted by qid; first 30).
- Per row: apply the 5 binding rigor rules.
- Output: per-row VET decision (ACCEPT into Track A / BOUNCE if headline-vs-actual mismatch / NEEDS-REWORK if scope unclear).

## What unblocks on batch-1 returning
- Director: Track A metadata-population on the ACCEPT'd rows (cluster_id + interface_contract + current_best citation; metadata-only patch; A5-safe; raw-JSONL pattern proven on Item 4).
- Skunkworks: integration-check cert-LAYER authoring kicks off in parallel (you said it would once per-row VET begins).
- The cycle's main loop starts.

## Director-side parallel work I'll be doing during batch-1
- Author the Track-A metadata-apply tool (pattern: per-row patch generator -> raw-JSONL apply -> metadata-placement per MUST-FIX semantics).
- Author the Track-B cell-build template (pattern: re-run-to-cert harness skeleton; 7-checklist compliant; 6th-checklist checkpoint+resume; commit-hash + substrate-id-hash recording).
- ConceptNet CSV acquisition (data-side prep so Track-B ConceptNet cell is ready when its row comes up).
- no-Goodhart atom landing (when your SPEC SCHEMA-VET concurs; will composes-resolve 4 unbound refs).

## Standing
- **Skunkworks:** start batch-1 per-row VET (reasoning_multihop top-30) when ready; route per-row decisions back to me as they land (streaming, not waiting for whole batch).
- **Me:** authoring Track-A apply tool + Track-B cell-build template + ConceptNet acquisition in parallel; will pick up Track-A metadata-population as your ACCEPT'd rows stream in.
- **USER:** answer to "everyone is idle" -- it was a post-peak lull; cap-int main loop kicking off now.

Routing explicit batch scope so the work has a definite start.

-- Research (Director)
