# Phase 3 Cost / Policy Brief for USER

**Status:** Decision brief; USER ratifies if Phase 1+2 prove insufficient over a few-days observation window.
**Authored:** Testbed (per Director GO; per the original 3-phase hardening proposal).
**Date:** 2026-06-20.

## Context

Phase 1 (Stop hook + StopFailure hook) + Phase 2 (watchdog) target two failure modes:
1. **Idle-one-by-one deaths** — sessions go idle and don't move forward
2. **All-stop-at-once** — API failures (529 / rate-limit contention) hit multiple sessions simultaneously

Phase 1+2 mitigate but don't eliminate the second failure mode at its root: **5 sessions hitting per-minute account caps simultaneously**. Phase 3 options address that systemic constraint.

## Options

### Option A: Stagger heavy turns (Director scheduling discipline)
- **What:** Director coordinates which session has the heaviest work each minute; avoid 5-session concurrent peak.
- **Cost:** $0; only Director scheduling-discipline change.
- **Throughput:** unchanged at floor; reduced peak congestion.
- **Effort:** Director-internal; no code changes; no infra changes.
- **Drawback:** doesn't apply when all sessions independently get a substantive event in the same minute (the worst case for contention).
- **Recommended:** worth doing regardless of other options; near-zero cost.

### Option B: Batch API adoption for Skunkworks
- **What:** Skunkworks's cert-VET work is latency-tolerant (results take minutes/hours from substrate POV anyway). Move to Anthropic Batch API for 50% discount + no per-minute account cap pressure.
- **Cost:** -50% on Skunkworks API spend (Batch is half-price). Net negative cost = SAVINGS.
- **Throughput:** Skunkworks turnaround increases from minutes to 24h (Batch SLA). For cert-VET, this is mostly fine — most VET work isn't time-critical.
- **Effort:** Moderate. Skunkworks's prompt + cert-VET routing layer needs Batch-API integration (Anthropic SDK supports it natively).
- **Drawback:** can't do real-time cert-VET on dispatched experiments; needs queue-based pattern. Skunkworks must opt-in per their VET-discipline.
- **Recommended:** STRONG candidate if Skunkworks adopts; halves per-minute account-cap pressure (removing 1 of 5 sessions from real-time contention).

### Option C: Separate workspaces / multiple Anthropic accounts
- **What:** Run 5 sessions across 2+ Anthropic accounts (e.g., 3 substrate + 2 admin) instead of all 5 on one account.
- **Cost:** +$X per additional account/tier. Approximate: doubles base subscription if going 1 -> 2 accounts.
- **Throughput:** removes per-minute account-cap contention completely.
- **Effort:** Account setup + per-session credential routing.
- **Drawback:** Anthropic ToS may restrict multi-account usage. Need to verify ToS allows this for the same user/org.
- **Recommended:** ONLY if Option B is insufficient + ToS allows. Higher cost.

### Option D: Higher account tier
- **What:** Upgrade to a higher Anthropic tier (Pro -> Team -> Enterprise) with higher per-minute caps.
- **Cost:** +$Y per tier upgrade per month.
- **Throughput:** removes account-cap as a constraint at the new tier.
- **Effort:** Tier upgrade in account settings.
- **Drawback:** monthly recurring cost; possibly more capacity than 5-session workflow needs.
- **Recommended:** Trial if Option B + concurrency-staggering aren't enough; check Anthropic Team/Enterprise pricing for the actual rate-limit deltas.

## Recommendation order (lowest cost first)

1. **Option A NOW** (free) — Director scheduling-discipline; should be adopted immediately.
2. **Option B SOON** (negative cost; savings) — Skunkworks Batch API integration; biggest ROI; closes 1 of 5 contention sources.
3. **Wait + observe** for 1-2 weeks; if all-stop-at-once still hits, evaluate Option D first (single tier upgrade).
4. **Option C** (multiple accounts) only as last resort + only after ToS verification.

## What USER needs to decide

- (a) **Option A endorsement** — empower Director to stagger heavy turns. Cost: $0. Effect: marginal but free.
- (b) **Option B authorization** — Skunkworks adopts Batch API. Cost: -50% on their spend. Effect: high ROI; biggest dent in account-cap contention.
- (c) **Wait-and-see** for now — only revisit if Phase 1+2 + Options A/B insufficient.

## Status without USER decision

Phase 1+2 ship regardless; Phase 3 options only activate on USER ratification. Default = wait-and-see; current Phase 1+2 hardening continues to operate.

---

For Director: this brief is routable to USER when bandwidth permits. No urgency; suggests revisiting after a few-days observation window of Phase 1+2 effectiveness.
