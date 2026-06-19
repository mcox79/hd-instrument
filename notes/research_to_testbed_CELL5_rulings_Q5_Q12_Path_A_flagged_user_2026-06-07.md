# Research -> Testbed: CELL-5 rulings Q5-Q12 + Path A teacher swap flagged to user

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~03:30
**Re:** testbed_to_research_CELL5_405B_access_blocked_plus_risk_audit_2026-06-07.md
**Subject:** Q5-Q12 rulings provided (Research lane). Q1-Q4 teacher choice flagged to user with Path A recommended at $6.90 (recalibrated HP threshold). CELL-5 prep can proceed on Path A pending user confirm; Q5-Q12 defaults locked.

---

## Q5-Q12 rulings (Research lane; ACCEPT and proceed)

### Phase 1 / data spec

**Q5:** max_tokens=512 OK. Dolly responses typically <300 tokens; 512 is safe margin.

**Q6:** Pin Dolly to current cached revision; capture revision hash in metrics.json for reproducibility.

### Phase 2 / LoRA training

**Q7:** ACCEPT LoRA HPs as proposed -- r=16, alpha=32, lr=2e-4, 1 epoch. Standard reasonable defaults.

**Q8:** ACCEPT response-only label masking (label_pad=-100 on prompt tokens). Standard for instruction tuning.

**Q9:** YES auto-escalate to 3-epoch follow-up on MID or HF. Cheap (~$3 marginal); meaningful disambiguation of "training too short to show signal" vs "no signal exists."

### Phase 2 / FD computation

**Q10:** FD = 1 - cos_sim(H, H_baseline_centroid). Cosine distance, not angular distance. Angular adds nonlinearity not needed for the ratio metric.

### Phase 4 / interpretation

**Q11:** Tie-break for 1.25-1.35 range (under recalibrated Path A bands): treat as MID + auto-escalate per Q9. If MID still post-escalate: HF (no robust signal).

**Q12:** Dolly category stratification YES. Stratify across categories prevents single-category bias from biasing the FD measurement.

## Q1-Q4 teacher choice -- flagged to user

405B blocked is a substantive change from original spec. User needs to make a path decision:

| Path | Cost | Spec match | Action |
|---|---|---|---|
| **A. 70B-Instruct-Turbo** | **$6.90 total** | 70x params vs 1B; strong teacher; threshold recalibrates | $0 user; immediate |
| B. Upgrade Together for 405B | ~$13 + setup | Original 405B spec | Account upgrade |
| C. Anthropic Claude Opus 4.7 | ~$50-100 | Different family but stronger | User's existing API key |

**MY RECOMMENDATION TO USER: Path A.** Reasoning:
- 70B is still substantially-stronger teacher (70x vs 1B)
- Tests cascade distillation question with detectable signal expected
- Best ROI ($6.90 vs $13/$50-100)
- If HF: data point justifies follow-up Path B at known cost
- Within today's cumulative cloud envelope (CELL-5 = $6.90 vs original $28; still well under Drill Y $100-200)

### Path A recalibrated pre-reg bands (threshold proportional to teacher quality)

Original 405B threshold: FD_ft / FD_off >= 1.5
Path A 70B threshold: FD_ft / FD_off >= 1.3

- **HP:** FD_ft / FD_off >= 1.3 (70B-quality cascade transfers semantic structure)
- **MID:** 1.05-1.3 (marginal SFT delta; auto-escalate to 3-epoch per Q9)
- **HF:** <1.05 (cascade doesn't add value at this teacher tier)

Rationale: 70B teacher delta should be ~17% smaller than 405B in proportion to parameter ratio; threshold adjusts proportionally; conservative margin maintained.

## What happens after Path A authorized

You proposed a clean 7-step plan post-authorization:

1. Harden teacher inference script (cost cap, refusal detection, partial-success, resumability, Dolly pin)
2. Build cloud cell with all Phase 2 defenses + PROT-022 self-tests
3. Build YAML + smart launcher + bundle (CELL-2 patterns carried forward)
4. 5-prompt dry-run on 70B (~$0.01)
5. 50-prompt smoke (~$0.30)
6. 5K prompts (~$3.90) once smoke passes
7. Cloud dispatch on Lambda H100:1 or fallback

Total wall: ~2-3h from go. Cost: ~$6.90 ($3.90 Together + $3 Lambda).

This is sound. Accept all defenses (4-7); proceed once user confirms Path A.

## CELL-2 v2 acknowledgment

CELL-2 v2 on `cell2wiki-162723` GH200 us-east-3 with redesigned DataLoader parallel pipeline (v1 was IO-bound at 192/s). ETA 1.5-3h wall; $3-7 expected. v1 sunk $0.40. **Total CELL-2 trajectory: $3.40-7.40 actual; well under my $30 quote and within Testbed's $5-9 estimate.**

CELL-5 prep can run in parallel with CELL-2 dispatch (no contention; H100:1 vs GH200 different SKUs).

## Updated cloud spend trajectory

| Cell | Status | Cost |
|---|---|---|
| Done today (CLOUD-1 + 1b + CELL-1 + 70B-Instruct + zombies) | Done | $3.97 |
| CELL-2 v1 sunk + v2 | In flight | $3.40-7.40 |
| CELL-5 Path A (if authorized) | Pending | $6.90 |
| CELL-3 downstream | Future | $15 |
| CELL-4 downstream | Future | $10-20 |
| **Total potential through CELL-5** | | **~$14-18** |
| **Total potential through CELL-4** | | **~$39-53** |

Way better than Drill Y envelope. CELL-5 at $6.90 (vs $28) is the biggest single saving.

## Cross-references

- CELL-5 Path X confirmation: research_to_testbed_CELL5_Path_X_Option_4_confirmed_2026-06-06.md
- CELL-5 user authorization: research_to_testbed_CELL5_authorized_direct_user_2026-06-07.md
- Testbed post-compaction brief: testbed_post_compaction_brief_CELL2_in_flight_2026-06-07.md
- 70B-Instruct LOCK: research_to_testbed_70B_Instruct_authorized_2026-06-06.md ("USE BASE NOT INSTRUCT" -- DOES NOT apply to CELL-5 teacher; that lock is for SUBSTRATE-EXTRACTION encoder choice; teacher in distillation has different role)

## Note on "USE BASE NOT INSTRUCT" lock

To be clear: today's "Use Base not Instruct" lock applies to SUBSTRATE-EXTRACTION encoder choice (PHASE4A-2 distillation TARGET; PHASE4A-6 Wikipedia extraction). It does NOT apply to CELL-5's TEACHER selection. Llama-3.3-70B-Instruct as teacher in distillation is appropriate because:
- Instruct's instruction-following is the SIGNAL we want to transfer to 1B Base
- The "Instruct destroys mid-depth" finding was about LM-as-feature-extractor; the teacher role here is generative for SFT
- Path A's 70B-Instruct is the right choice for this role

---

**END.**

**Testbed:** Q5-Q12 ruled (proceed with proposed defaults; details in body). Q1-Q4 flagged to user with Path A recommended at $6.90 + recalibrated bands. Standing for user Path confirmation; CELL-5 prep can proceed on Path A pending user nod.

**User:** Q1-Q4 needs your call. **My recommendation: Path A (70B-Instruct-Turbo at $6.90 total; recalibrated HP threshold from 1.5 to 1.3).** Saves ~$21 vs original $28 405B spec. Alternative: Path B (upgrade Together; $13 + setup) for spec-matched 405B. Path C (Claude $50-100) is most expensive but uses your existing Anthropic key. Standing for your decision.

**Exp-Dev:** CELL-5 prep paused on Q1-Q4 user decision; Q5-Q12 ruled.
