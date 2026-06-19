# Testbed -> Research: CELL-5 405B serverless BLOCKED + full risk audit + need direction

**From:** Testbed
**To:** Research
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~03:15 UTC
**Re:** research_to_testbed_CELL5_Path_X_Option_4_confirmed_2026-06-06.md
**Subject:** Cannot dispatch CELL-5 as speced. (1) User's Together account lacks 405B-Instruct serverless access (HTTP 400 "non-serverless model"). (2) Full risk audit of the cell identified 28 issues, 12 of which need scientific direction from you (LoRA HPs, training mask, FD formula, threshold band recalibration if teacher is weaker). Standing for your call on teacher swap + risk-priority list before any cloud spend.

---

## 1. Blocker: Together 405B serverless inaccessible

Confirmed via API (5-prompt dry-run failed cleanly, $0 burned):

```
HTTP 400: Unable to access non-serverless model meta-llama/Llama-3.1-405B-Instruct
```

The model IS listed in Together's catalog with `type=chat`, `pricing.input=$3.5/M, pricing.output=$3.5/M`, but Together has gated 405B-Instruct to dedicated-instance customers (paid tier / reserved capacity). Free / build-tier accounts get HTTP 400 even with a valid API key.

(`meta-llama/Llama-3.1-405B-Instruct-Turbo` does NOT exist on Together; only 70B and smaller have `-Turbo` variants.)

### User options

| Path | Cost (5K prompts) | What's required |
|---|---|---|
| A. **Swap to Llama-3.3-70B-Instruct-Turbo** | ~$3.90 (input + output) | $0 user action; works immediately |
| B. Upgrade Together account to unlock 405B | ~$13 + account setup (credit card, possibly tier-up wait) | User has to authorize and execute |
| C. Use Anthropic API (Claude Opus 4.7) | ~$50-100 (different family but stronger) | User's Anthropic API key (per `project_anthropic_api_key_available`) |
| D. Try Llama-3.1-405B-Base (NOT Instruct) on Together | unknown; pricing 0/0 in catalog — likely also blocked or dedicated-only | $0 user action; will fail similarly |

**My recommendation if you accept teacher swap: Path A (70B-Instruct-Turbo).** 70B is still ~70x parameters vs 1B (vs 405x for the original spec). The FD-ratio test measures whether SFT moves 1B internals; any substantially-better teacher should produce a detectable signal. If 70B comes back MID/HF, that's a useful data point AND we can re-fire with Path B as a follow-up.

**My concern about Path A:** the HP threshold (FD_ft / FD_off >= 1.5) was calibrated for the 405B teacher's response distribution. A 70B teacher generates responses that are more "1B-adjacent" in style, so the SFT delta might be smaller. Threshold may need recalibration.

### Questions for Research (Q1-Q4)

- **Q1:** Accept Path A (70B-Instruct-Turbo) as teacher? If so, do HP/MID/HF bands need adjustment?
- **Q2:** If you prefer 405B quality, do you want me to flag this to user for Path B (upgrade Together) or Path C (Anthropic Claude)?
- **Q3:** Is there a third teacher option I'm missing (Together's DeepSeek-R1-Distill-Llama-70B at $2/M? Llama-3.1-70B-Instruct-Turbo at $0.88/M?)?
- **Q4:** Should CELL-5 wait for a paid Together account, or proceed with 70B now to get a data point?

---

## 2. Full risk audit (28 items; 12 need your direction)

Before any dispatch, I audited the full pipeline. Categorized as DEFENDED (script already handles), NEEDS WORK (must fix), or ACCEPTED (flag in result).

### Phase 1: Teacher inference (runner-side; either 405B or 70B)

| # | Risk | Status | Needs Research input? |
|---|---|---|---|
| 1 | Wrong model ID | DEFENDED (dry-run gate) | No |
| 2 | Account tier blocks model | DEFENDED (dry-run gate) | No |
| 3 | Rate limit / 429 | DEFENDED (8 concurrent, expo backoff) | No |
| 4 | Cost overrun on long responses | NEEDS WORK (add cumulative-cost cap) | No |
| 5 | Response truncation at max_tokens | ACCEPTED (512 generous) | **Q5: confirm 512 is enough OR specify** |
| 6 | Content-moderation refusals | NEEDS WORK (detect + count) | No |
| 7 | Empty / null responses | NEEDS WORK (skip in cloud) | No |
| 8 | Partial success (3K/5K) | NEEDS WORK (prompt-id join) | No |
| 9 | Resumability (skip already-done) | NEEDS WORK (critical) | No |
| 10 | Unicode in Dolly | DEFENDED | No |
| 11 | Dolly version drift | NEEDS WORK (pin revision) | **Q6: pin which Dolly snapshot?** |
| 12 | temp=0 non-determinism | ACCEPTED (capture full) | No |

### Phase 2: Cloud cell (LoRA training + FD computation)

| # | Risk | Status | Needs Research input? |
|---|---|---|---|
| 13 | LoRA hyperparams | NEEDS WORK | **Q7: r=16, alpha=32, lr=2e-4, epochs=1 OK? Or specify** |
| 14 | Training mask (prompt+response vs response-only) | NEEDS WORK | **Q8: response-only mask (label_pad=-100 on prompt) standard, confirm** |
| 15 | LoRA merge before H_ft | NEEDS WORK (merge_and_unload) | No (mechanical) |
| 16 | Single epoch insufficient | ACCEPTED + ESCALATE | **Q9: if MID/HF, fire 3-epoch follow-up at ~same cost?** |
| 17 | Catastrophic forgetting | ACCEPTED | No (LoRA r=16 minimizes) |
| 18 | OOM during training | DEFENDED (H100 80GB plenty) | No |
| 19 | OOM during extraction (LM head) | DEFENDED (use AutoModel, lesson from CELL-2) | No |
| 20 | MAX_TOK / tokenizer config mismatch H_off vs H_ft | NEEDS WORK (must be identical) | No |
| 21 | Padding side mismatch | DEFENDED (force right) | No |
| 22 | Last-token pool cross-device | DEFENDED (CELL-1 fix carried fwd) | No |
| 23 | FD_off near zero -> divide by zero | NEEDS WORK (epsilon + sanity) | No |
| 24 | Cosine distance vs similarity confusion | NEEDS WORK | **Q10: confirm FD = 1 - cos_sim(H, centroid). Or angular distance?** |
| 25 | fp16 precision loss in FD | NEEDS WORK (cast fp32) | No |
| 26 | Prompt-id ↔ response-id ordering | NEEDS WORK (dict-keyed join) | No |
| 27 | LoRA adapter not saved to disk | NEEDS WORK | No |
| 28 | Training NaN loss | NEEDS WORK (check + abort) | No |

### Phase 3: Infrastructure

All 12 items DEFENDED via CELL-1 + 70B-Instruct + CELL-2 hardening reuse. No new work.

### Phase 4: Strategic / interpretation

| # | Risk | Status | Needs Research input? |
|---|---|---|---|
| 41 | Just-under-HP threshold | NEEDS WORK | **Q11: tie-break rule for 1.45-1.55 range?** |
| 42 | 70B vs 405B teacher quality | ACCEPTED + DOC | Implicit in Q1 |
| 43 | Dolly category bias | NEEDS WORK | **Q12: stratified sample across categories? Or accept natural distribution?** |

---

## 3. Questions for Research (consolidated, Q1-Q12)

**Teacher choice (Q1-Q4):** Path A, B, C, or D? If A, do HP/MID/HF bands shift?

**Phase 1 / data spec:**
- Q5: max_tokens=512 enough for instruction following?
- Q6: pin Dolly to a specific snapshot revision?

**Phase 2 / LoRA training:**
- Q7: LoRA HPs (r=16, alpha=32, lr=2e-4, 1 epoch) OK or specify?
- Q8: response-only label masking (prompt tokens get -100)?
- Q9: auto-escalate to 3-epoch follow-up if MID/HF?

**Phase 2 / FD computation:**
- Q10: FD formula -- cosine distance (1 - cos_sim) or angular distance?

**Phase 4 / interpretation:**
- Q11: tie-break rule for 1.45-1.55 ratio (just under HP)?
- Q12: Dolly category stratification or natural distribution?

---

## 4. Status of CELL-2 + Testbed lane

- CELL-2 v2 IS in flight (cluster `cell2wiki-162723` on GH200 us-east-3). Redesigned with DataLoader parallel pipeline after v1 was IO-bound at 192/s.
- CELL-2 v2 ETA: 1.5-3h wall; expected cost $3-7. v1 sunk $0.40.
- Together API key tested + works generally; just 405B specifically is blocked.
- Llama-3.2-1B Base weights downloaded to runner today (G15/G16 unblocked for Exp-Dev).
- FAISS env fix landed (CELL-4 HNSW gate cleared).

---

## 5. My current proposal (subject to Research direction)

If you say "proceed with Path A (70B) + accept my conservative defaults on all Phase 2 items," I will:

1. Harden teacher inference script (4 fixes: cost cap, refusal detection, partial-success handling, resumability + Dolly pin)
2. Build cloud cell script with all Phase 2 defenses inline + PROT-022 self-tests
3. Build YAML + smart launcher + bundle (carry-forward CELL-2 patterns)
4. 5-prompt dry-run on 70B (~$0.01; verify API + response shape)
5. 50-prompt smoke (~$0.30; verify cost meter + refusal detection + partial-success handling)
6. Then 5K prompts (~$3.90) once smoke passes
7. Cloud dispatch on Lambda H100:1 (or fallback)

Total wall: ~2-3 hours from your go. Cost: ~$7 ($3.90 Together + $3 Lambda).

Standing for your direction. CELL-2 v2 keeps running independently in the meantime.

---

**END.**

**Research:** Q1-Q12 above need your direction before CELL-5 dispatch. Key blocker: 405B serverless blocked on user account. Propose Path A (70B-Instruct-Turbo at ~$3.90 + $3 Lambda = $6.90 total) but you may want HP/MID/HF bands recalibrated.

**Exp-Dev:** No action; CELL-5 prep paused pending Research direction.

**User:** Filed risk audit + 12-question spec clarification to Research. CELL-2 v2 still running. Awaiting Research's call on teacher swap + LoRA defaults. No additional spend until you and Research align.
