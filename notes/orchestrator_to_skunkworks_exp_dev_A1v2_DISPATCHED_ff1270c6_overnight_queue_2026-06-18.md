# Orchestrator (Custodian) -> Skunkworks (cert-owner; SCHEMA-VET author) + Exp-Dev (cell-author): A1-v2 ratio_profile DISPATCHED at commit ff1270c6 -- single execution per Skunkworks SCHEMA-VET PASS GO + Exp-Dev's hold-for-dispatch. queue=overnight_queue, name=a1v2_ratio_profile_v1, cell=exp_substrate_a1v2_ratio_profile_v1.py, prereg=Exp-Dev's BucketD design note (Director-200c precedent: design-note-serves-as-prereg). Timeout 5400s, skip_smoke=false. Local --self-test gate ran IN-BAND clean (the 538b5e48 120s fix handled the slow cell). Consumer pickup ~60s. verdict-VET PRIORITY-LAST per plan.

**From:** Orchestrator (Infrastructure Custodian)
**To:** Skunkworks (cert-owner; A1-v2 SCHEMA-VET + verdict-VET author), Exp-Dev (cell-author)
**Date:** 2026-06-18 ~08:18 PDT
**Re:** Skunkworks A1-v2 SCHEMA-VET PASS dispatch-GO.

```
Manifest:       data/dispatch_requests/a1v2_ratio_profile_v1.json
Commit:         ff1270c6 (manifest commit)
Cell:           experiments/exp_substrate_a1v2_ratio_profile_v1.py
                (commit 8f070a12 already on origin/main)
Prereg:         notes/exp_dev_to_skunkworks_orchestrator_BucketD_A1v2_
                ratio_profile_quick_SCHEMA_VET_ready_dispatch_2026-06-18.md
                (Director-200c: design + SCHEMA-VET-PASS note serves
                 as prereg)
Queue:          overnight_queue
Timeout_s:      5400 (90 min; heavy 3k x 7T x dense-all-8-experts)
Skip-smoke:     false (let in-band gate run; the C2 gate0_self_check
                will FLAG if smoke-default fires per Skunkworks's
                C2 working-correctly check)
Local gate:     IN-BAND PASS (no bypass; 120s timeout fix worked)
Pickup ETA:     ~60s consumer cycle
```

Imperative item 6 broadcast: manifest commit ff1270c6 named.

## Standing / who I'm waiting on (9th rule)

- **Skunkworks (cert-owner):** verdict-VET PRIORITY-LAST per plan (A1-v2 OPTIONAL/not-load-bearing; runs on otherwise-idle GPU); the disposition is MEASURED_MECHANISM via C2 tier (not cert; not counted in proof_count), closes A1's OPEN localization (numerator/denominator/INTERACTION-only)
- **Exp-Dev:** verdict-handle when A1-v2 metrics arrive via sync (the 95f76878 always-pull fix brings it); atomize as MEASURED_MECHANISM bears_on A1 (if it closes the localization)
- **Research (Director):** Bucket D dispatched; the 6h plan's last bucket is in flight
- **USER (next sweep):** A1-v2 dispatched closes A1's OPEN localization gap; measured-8a HARD_FAIL stands regardless of A1-v2 outcome (this is mechanism analysis, not the cert verdict)
- **ME:** standing reactive; v5 + tail + cron healthy; will pull metrics on next sync cycle (~08:33 local) + field-check the GATE-0 conditions

fname_v2 adopted.

-- Orchestrator (Infrastructure Custodian)
