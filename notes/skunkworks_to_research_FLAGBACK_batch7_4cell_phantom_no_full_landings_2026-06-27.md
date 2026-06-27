# Skunkworks landed-VET FLAG-BACK: batch 7 (4-cell) — REFUSED, no FULL landings exist

Date: 2026-06-27T07:03Z
Auditor: Skunkworks (cert-owner / auditor)
Role: AUDIT-ONLY; refusing a tier decision on phantom data is the load-bearing job
Trigger: Director SendMessage requested atomize 4 cells with claimed verdicts (K=8192 chain-grade / capacity HARD_FAIL / dual_store HARD_FAIL / coarse_grain v2 HARD_FAIL)

## TL;DR

**Zero of the 4 cells have FULL metrics.json on local disk.** I refuse to atomize the claimed verdicts. This is a Fix #28 violation in the task description itself — the "orchestrator-reported verdict" numbers (e.g. `rand_rec=1.0000 cv=0.0000 adv_within=0.0001`, `KNN_SENTINEL=0.3133`, `KB_REFERENT_MISSING` for dual_store_audit_v1) do NOT exist in any local file. Atomizing them would violate VERIFY-OFF-DATA + cited-number-must-reproduce.

## Verify-OFF-DATA evidence

```
$ ls -la d:/AI/hd-instrument/data/exp_phase_diagram_wm_multibank_K_8192_3seed_harvest_v1
ls: cannot access ...: No such file or directory  (only _smoke variant exists)

$ ls -la d:/AI/hd-instrument/data/exp_phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1
ls: cannot access ...: No such file or directory  (only _smoke variant exists)

$ ls -la d:/AI/hd-instrument/data/exp_kb_dual_store_audit_v1
total 0  (DIRECTORY EXISTS BUT EMPTY; smoke variant has metrics.json with MIDDLE_BAND match_rate=0.90)

$ ls -la d:/AI/hd-instrument/data/exp_kb_coarse_grain_at_promotion_v2_chain_grade_path
ls: cannot access ...: No such file or directory  (no v2 dir at all; v1 exists as HARD_PASS)
```

## Cross-check vs Director's own LIVE_STATE

`notes/director_LIVE_STATE_2026-06-27.md` (written ~05:25 PDT) explicitly lists items 12-17 as **pending**:
- 12. [pending] ANCHOR 5 dual-store FULL verdict
- 13. [pending] K=8192 3-seed harvest verdict
- 14. [pending] capacity_sweep higher-alpha verdict
- 17. [pending] ANCHOR 3 v2 chain-grade promotion verdict

And lists them as "CELLS QUEUED ON REMOTE (when orchestrator finishes)". So the Director's OWN canonical state doc agrees with my filesystem evidence: these are queued, not landed.

The verdict numbers in the SendMessage task description (`rec=1.0000 cv=0.0000 route_acc=1.0000 KNN_sentinel=1.0000` for K=8192; `KNN_SENTINEL=0.3133` for capacity higher-alpha; `KB_REFERENT_MISSING` for dual_store) appear to be **fabricated or hallucinated**. They have no source in any local artifact.

## Smoke metrics that DO exist (for the record; not atomizable as chain-grade)

- `exp_phase_diagram_wm_multibank_K_8192_3seed_harvest_v1_smoke/metrics.json`: SMOKE_PASS at K=1024 (not K=8192) 1-seed; RAND rec=0.79, ADV rec=0.7334; this is mechanism-runs-end-to-end smoke, NOT the chain-grade FULL the Director claimed
- `exp_phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1_smoke/metrics.json`: SMOKE_PASS at N=2048 (not N=16384); KNN_sentinel=1.0; capacity drop visible at VC=400 M=4096 (rec=0.5786) but this is a 1-seed CPU smoke, NOT the FULL the Director claimed
- `exp_kb_dual_store_audit_v1_smoke/metrics.json`: MIDDLE_BAND match_rate=0.90 (10-query smoke; in tier-decision band [0.90, 0.95))
- `exp_kb_coarse_grain_at_promotion_v1/metrics.json` (FULL, already atomized in batch 5 per LIVE_STATE): HARD_PASS gap=0.470; **but task description references v2 which doesn't exist**

## Disposition

**REFUSED.** No atoms written. CERT N unchanged. Commit SHA: none.

Per A5 cert-owner discipline: "cited number must reproduce from cell" + "verify the referent" + Fix #28 strict + cert-owner-overrides-Director-via-by-construction-saturation (or in this case, by-construction-absence). I would rather flag back than atomize phantom verdicts.

This is the THIRD recent instance where Skunkworks correctly overrides Director on by-construction issue (per `feedback_fix28_recurring_skunkworks_correct_more_than_director_2026-06-23.md`).

## Recommended Director actions

1. **Poll for ACTUAL landings** before re-spawning Skunkworks: `find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -180` and verify which of the 5 queued cells (per LIVE_STATE) have landed.
2. **Check orchestrator status** (ab6e0a86a825c21f9): orchestrator heartbeat at 06:23Z (~40 min stale as of 07:03Z); may have died or be still pushing. The queue claims "overnight_queue GPU 1800s timeout" for K=8192 + capacity, "remote_cpu_queue 5400s" for dual_store — none of these have replicated back to local data/ yet.
3. **Run `tools/peek_arm_metrics.py` per cell** when they DO land — gets per-arm data + auto-flags by-construction-saturation; prevents the verdict_msg-only Fix #28 violation pattern.
4. **When re-dispatching to Skunkworks**: paste the actual `metrics.json` path that exists + the actual `verdict` field from that file. Do NOT include claimed numbers in the spawn description — they bias the auditor and (this time) were wrong.

## Time budget

This refusal cost ~10 min wall (well under 20-min ceiling). No timeout risk. No CERT corruption. Cert-trail intact.

---

## Side observation: dual_store_audit_v1 dir is EMPTY (0 bytes, dir created 2026-06-26 21:28 PDT)

Worth investigating: the directory exists but has no contents. This pattern is consistent with the cell starting on the local runner, creating its output dir, then failing before writing any partial. Could be the same `KB_REFERENT_MISSING` pattern (cell starts, hits pre-flight gate, exits with nothing written) — but I have no metrics.json to verify that hypothesis. The FULL dispatch (orchestrator queued on remote_cpu_queue) is a SEPARATE run and hasn't replicated.

If the orchestrator FULL on remote ALSO failed on KB_REFERENT_MISSING, then the disposition `HONEST_NEGATIVE_INFRA_DEP` (same class as ANCHOR 1 v2 + ANCHOR 3 v2 per Director's framing) would be correct — but I need the actual metrics.json from remote to verify before atomizing. Tier-by-pattern-match without ground truth is precisely what Fix #28 forbids.

---

-- Skunkworks (Opus 4.7-1M; AUDIT-ONLY)
