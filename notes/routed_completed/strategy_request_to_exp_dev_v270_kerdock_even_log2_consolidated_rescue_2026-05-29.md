# strategy_request_to_exp_dev — v270 CONSOLIDATED Kerdock-even-log2 vulnerability rescue (2026-05-29)

## TASK

Audit and reship the family of pending N=8192 anchors that hit `make_kerdock_4coset_codebook` requiring even log2(N). Currently confirmed crashed at import-time:
- kf3_multisub_v3_n8192 (verdict V4 this batch)
- t1_beta_sweep_v2_n8192 (verdict V5 this batch)
- t2_codebook_boundary_v2_n8192 (verdict V6 this batch)

Caller-flagged upstream pending vulnerable set (per `notes/strategy_decisions_2026-05-29.md`):
- axis1_mb_chunk9_v1_n8192 (confirmed Kerdock import)
- axis1_mb_chunk10_v1_n8192_fine (confirmed Kerdock import)
- pb3_extended_v4 (per caller; verify Kerdock usage)
- t3_susceptibility_v2 (per caller — currently running per queue state; verify Kerdock usage)
- kf2_be1 family at N=8192 (fp32 / fp16 / int8 / int4 / int2 / int1 — 6 anchors; verify each whether Kerdock is reached)

## WHY

The script `experiments/exp_wave14y_erase_kerdock_v3.py` defines `make_kerdock_4coset_codebook(N, device)` with a hard precondition at lines 167-172:

```python
n_log2 = int(round(math.log2(N)))
if 2 ** n_log2 != N:
    raise ValueError(...)
if n_log2 % 2 != 0:
    raise ValueError(f"N={N} requires even log2(N) for MM construction (got n_log2={n_log2})")
t = n_log2 // 2
```

At N=8192, log2=13 (odd) → ValueError raised before any work. This is a SCRIPT_PRECONDITION_VIOLATION new sub-flavor of LABEL-VS-HONEST. Three already crashed (V4/V5/V6) wasting 50 wall_s aggregate; 5-6 more upstream anchors will crash identically if shipped as-is at N=8192.

Even-log2 N values nearest to 8192: N=4096 (log2=12) or N=16384 (log2=14).

## CONTRACT

For each vulnerable anchor:
- **Audit step (cheapest-first):** grep the script for `make_kerdock_4coset_codebook` import or call. If absent, NOT vulnerable; no reship needed.
- **If vulnerable + experiment is N-scoping or M-density variation:** reship at N=4096 (log2=12). Cheaper compute footprint, same substrate-physics signal at smaller scale.
- **If vulnerable + experiment specifically demands production-scale corroboration of a prior N=4096 finding:** reship at N=16384 (log2=14). Adds N-scale evidence; warrants the bigger budget.
- **Per [[feedback-per-experiment-timeout-required]]:** every reship MUST carry an explicit `--timeout` derived from the per-cell wall formula `1.5 * smoke_wall_s * (FULL_N/smoke_N)^exp * (FULL_seeds/smoke_seeds)`; if the formula yields >14400s, surface to strategy for review before queue_add.
- **Per [[feedback-no-experiment-design-in-prompts]]:** NO specific cell grids, no HF1/HF2 numerical bounds, no anchor-name suffix beyond `_n<N>` enforcement — exp_dev re-derives from the original spec.
- **Per [[feedback-rescue-sketch-first-sequencing]]:** cheapest rescue (N=4096 reship + grep-audit-only-no-ship for upstream) sequenced FIRST; N=16384 reship sequenced second; (d) script structural fix (graceful downgrade) deferred to STRATEGY-level for next cycle.

## AUTONOMY

You decide:
- Whether each anchor in the upstream set actually reaches the Kerdock codebook call (some scripts import many codebooks; Kerdock may be optional).
- Whether N=4096 or N=16384 is the right reship N for each anchor based on the original experiment's design intent.
- Pre-reg HP/HF bands at the new N (NOT the same bands as the N=8192 attempt — re-derive per the new scale).
- Anchor name with `_n<N>` binding contract per PROT-018.
- Queue routing (GPU overnight vs CPU sweep) per per-cell wall estimate.
- Smoke gate before FULL ship.
- Whether to file a STRATEGY-level proposal for option (d) — modify `make_kerdock_4coset_codebook` to gracefully downgrade (e.g., embed N=4096 codebook in N=8192 with structured padding) so future N=8192 anchors don't need pre-work reship. Recommended: file as STRATEGY proposal, not implement in this rescue cycle.

## CONTEXT POINTERS

- Source script: `d:/AI/hd-instrument/experiments/exp_wave14y_erase_kerdock_v3.py` lines 159-176.
- Original strategy decision: `d:/AI/hd-instrument/notes/strategy_decisions_2026-05-29.md` v269->v270 entry verdicts V4/V5/V6 section.
- Cap_map impact: 0 row-level moves for V4/V5/V6 (no substrate-physics signal); rescue is operational unblock not capability-level rehab.
- v270 cap_map history row in `notes/substrate_capability_map_history.md`.
- Caller's upstream context: 5-6 more pending anchors at N=8192 in the pending overnight_queue carry the same vulnerability.

## NOT YOUR JOB

- Diagnosing whether the Kerdock construction is the right codebook for these experiments — that is a STRATEGY question, NOT an exp_dev rescue scope.
- Reshipping at N != {4096, 16384} — those are the only adjacent even-log2 values; if the original anchor needs a different N, file a STRATEGY request instead.
- Implementing graceful-downgrade in the script — that is a STRATEGY-level proposal, not a per-rescue change.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
