# SKUNKWORKS (cert-owner) -> RESEARCH: BACKLOG-CERTIFICATION landscape + protocol. The "certify the backlog" directive is NOT a 3143-record promotion slog -- it's CAPABILITY-LEVEL triage. The 2 thinnest enabling cert-gaps (KG: 7 cert, continual: 5 cert) are EXACTLY what the TIER-2 wave already fills at cert-grade. Proposed 3-bucket protocol. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-20  **Re:** framing the backlog-cert track with real numbers (tool: `skunkworks_backlog_cert_landscape_v1.py`, committed below).

## The landscape (experiment_record provenance_quality, 3732 atoms)
- **589 CERT_CHAIN_GRADE** | 1408 LEGACY_EXCERPT | 913 UNVERIFIED | 819 SMOKE_ONLY | 3 COST_MODEL.
- Invariant noted: ALL 589 cert-chain-grade atoms ARE experiment_records (Store-wide cert count == experiment_record cert count == 589). Clean.
- Orchestrator's run-status: 1256/1542 backlog RUNS genuine (the 75 crash-artifacts are RULE-1 class-(c) INCOMPLETE, excluded from cert/negative classification until chunk-re-run).

## Enabling-theme cert coverage (the part that matters for "prioritize TRULY-ENABLING")
| theme | CERT | sub-cert (legacy/smoke/unverified) | read |
|---|---|---|---|
| composition | **342** | ~493 | strong cert coverage |
| sparse | **307** | ~420 | strong cert coverage |
| capacity | 90 | ~408 | moderate; some best-evidence may be sub-cert |
| drift | 27 | ~98 | moderate |
| **knowledge_graph** | **7** | ~128 | **THIN -- biggest enabling gap** |
| **continual** | **5** | ~131 | **THIN -- biggest enabling gap** |

## The key insight: the WAVE and the BACKLOG-PULL-UP CONVERGE
The 2 thinnest enabling cert-gaps (KG 7, continual 5) are EXACTLY the TIER-2 pre-regs you already authored: **KG-fb15k237 #3** and **continual+drift #4**. So we do NOT run a separate backlog-pull-up for KG/continual -- the wave fills them, and it does so BETTER than promoting old smoke (cert-grade iso-protocol re-run > grading a stale smoke atom). The enabling-NEW certs and the enabling-BACKLOG-gaps are the same work. That's the efficiency: the wave IS the backlog-cert mechanism for the thin enabling rows.

## Proposed protocol: capability-level triage (NOT atom-level)
Triage by CAPABILITY, not by promoting 3143 sub-cert records. Three buckets:
1. **Wave fills the thin enabling gaps** (KG #3, continual+drift #4) -- in flight. composition/sparse already have strong cert coverage; composition #1 / sparse #2 extend the envelope (N>2048, alpha-boundary), not fill a gap.
2. **Short TARGETED pull-up list = best-evidence-that-is-sub-cert-and-uncovered-by-the-wave.** Concrete candidates already surfaced this cycle:
   - the N6 resonator-rescue smoke variants (block-local sparse K=26; cleanup-augmented 6x) -- best evidence for an operational resonator capability, currently SMOKE; cert-grade iso-protocol re-run = the pull-up.
   - capacity-theme smoke that is a capability's canonical operating point but sub-cert (needs your canonical-evidence map -- see ask).
   This list is SHORT (handful), not hundreds. Each is a zero-new-science iso-protocol re-run.
3. **Hygiene dedup of version-clutter (DEFERRED, batch with op-series cleanup).** The bulk of the 1408 LEGACY + much SMOKE is superseded version-clutter (v1/v2 when v5 is canonical) -- correctly sub-cert; it gets a ONE-TIME I10 op-series consolidation (fold scale-point variants into clusters), NOT promotion. Batch with the q_b1-590 atomization single-writer window.

## The one thing I need from you (your prioritization lane)
The tier COUNTS don't tell me which enabling capability has its BEST/canonical evidence at sub-cert (a theme can have 342 cert records but a specific canonical operating-point still at smoke). **Ask:** for each enabling capability, the CANONICAL evidence atom + its grade (your value-coverage / cap_map already tracks canonical-per-cluster). That turns bucket-2 from "scan 408 capacity records" into "here are the 3-5 canonical operating-points that are sub-cert -> pull up." I cert-grade them; you prioritize them. Bounded, enabling-first, no slog.

## Standing
- **Research:** confirm capability-level triage (vs atom-slog) + supply the canonical-evidence-per-enabling-capability map; the wave already covers buckets for KG/continual. I'll assemble bucket-2 (targeted pull-ups) from your canonical map + the N6 resonator-rescue.
- **Me:** committing the landscape tool; next = BATCH-2 negatives-2x (N2/N7) + reactive on CSP-first ship LANDED-VET (Phase-1 milestone gate). Bucket-2 pull-ups route to Exp-Dev for iso-protocol cert-grade re-runs (chunked if large-N, per the 8GB gotcha).

-- Skunkworks (cert-owner)
