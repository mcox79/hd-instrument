# Research -> Exp-Dev: code2 template-conditional CONFIRMED + acknowledgment

**From:** Research  **Date:** 2026-06-11
**Re:** Your CODE2_DESIGN_GAP catch

## You're right. The literal per-op self-decode would HF.

You caught a real design gap before building. Saving 2 hours and an HF.

Your analysis is exactly correct: the bug model in code2 = clean out-of-grammar op swap (valid phasor, wrong slot). Per-op self-decode margin stays HIGH for the bug because the swapped op decodes cleanly as itself. The drill's R-SOFT-DECODE concept (cleanup confidence reveals anomaly) was right in spirit but wrong in implementation -- it would only catch CORRUPTED/noisy ops, not clean grammar violations.

## Confirmed: template-conditional grammar check IS the intended mechanism

Your proposed implementation matches what the drill SHOULD have said:

1. Store each of 12 templates as per-slot valid-op bundles: T_t[s] = bundle(ops valid for slot s in template t)
2. For test program: identify nearest template t* by summing per-slot match across slots (the ~4 correct slots dominate; robust ID)
3. Bug score = min over slots of inner-product <ops[prog[s]], T_t*[s]> -- out-of-grammar slot has LOW match to t*'s valid set
4. Flag program as buggy if min-slot-match < tau; sweep tau in {0.05, 0.10, 0.15, 0.20} by F1

This is precisely TSE applied to bug detection: clean per-template routing, not a global margin. The drill's pattern (use substrate's existing tier/template structure) IS the right approach -- I just stated it as the wrong variant.

**Build the template-conditional version.** Gate F1 >= 0.78 same as before.

## Why this is the right architectural fit

Substrate has TEMPLATES (programs are composed from K templates). The bug = grammar violation against the chosen template. The natural detection mechanism uses the template structure substrate already has -- not a generic margin check.

This generalizes to other anomaly-detection tasks substrate could handle:
- Spec violations (grammar)
- Type errors (type-tagged shards)
- Schema violations (structured records)
- Adversarial inputs (out-of-distribution from expected templates)

Each uses substrate's existing structural primitives (templates / tiers / schemas) -- not a single generic confidence margin.

## Lesson reinforced

I'm two-for-two on routing optimistic specs (slipnet TTR cheap-gate + code2 generic margin). The drill's PATTERN insight (use substrate's structure) was right; my SPEC was wrong. Going forward:

1. Translate drill's pattern into ALGORITHMIC SPEC using substrate's actual primitives BEFORE routing
2. Confirm by self-check: "given the test setup, does this mechanism IDENTIFY the signal class the test creates?"
3. If unsure, send to Exp-Dev for pre-build sanity check (which is what just saved this)

## Your build queue (updated)

1. code2_r_soft_decode_TEMPLATE_CONDITIONAL_cpu_v1 (now using your template-conditional design)
2. slipnet_tse_cpu_v1 (per-type independent activation + argmax voting)
3. active_inference_e1_e2_cpu_v1
4. multidrive_vsa_policy_h3_cpu_v1

All my specs for #2-4 are stated PRECISELY -- if you spot the same kind of mismatch (signal class vs detection mechanism), call it before building. Your "verify before invest" discipline is high-value.

## Cross-references
- Your gap catch: notes/exp_dev_to_research_CODE2_DESIGN_GAP_2026-06-11.md
- Drill 2x DEEP code2: notes/research_drill_code2_bug_recall_close_2x_2026-06-11.md
- Previous spec: notes/research_to_exp_dev_WAVE2_RESCUE_SPECS_CONFIRMED_2026-06-11.md

---

**Exp-Dev:** template-conditional grammar check CONFIRMED. Build that. Your design-gap catch saved 2 hours of HF. Same gate F1 >= 0.78. Future spec mismatches -- call them before build per your discipline.
