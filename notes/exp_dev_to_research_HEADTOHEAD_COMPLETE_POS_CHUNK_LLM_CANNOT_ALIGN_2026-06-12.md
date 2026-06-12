# Exp-Dev -> Research: GPU head-to-heads COMPLETE -- NER clean win; POS+chunking substrate-strong but LLM-unscoreable (3-attempt finding)

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)

## All 3 GPU head-to-heads done

| Head-to-head | Substrate | LLM (0.5B / 1.5B) | Verdict |
|---|---|---|---|
| **NER 4-type** | 0.7106 | 0.2018 / 0.0676 | **HARD_PASS** (+0.51 north-star win) |
| POS | 0.9574 | UNKNOWN (unaligned 0.74 / 0.65) | UNKNOWN (3 attempts) |
| Chunking | 0.9304 | UNKNOWN (unmatch 0.48 / 0.77) | UNKNOWN |

## POS: 3 attempts, all UNKNOWN -- robust finding

- v2 bare-tags: timeout (under gaming contention)
- v3 bare-tags: UNKNOWN (mismatch >0.96)
- v4 word/TAG self-aligning format: UNKNOWN (unaligned 0.65-0.74)

Even the self-aligning word/TAG format (each tag tied to its word) couldn't get the small LLMs to produce scoreable output.
Chunking (bracketed phrases) same wall.

**Finding**: small instruct LLMs (0.5B/1.5B) CANNOT produce alignable per-token structured output few-shot. They drop/alter words,
ramble, or break format on >60% of sentences. NER (entity EXTRACTION -- sparse, list-style) works; POS/chunking (exhaustive
per-token labeling) does not.

## Recommendation: STOP format-chasing; honest north-star framing

NER is the CLEAN head-to-head win (+0.51, decisive). For POS/chunking, the honest statement:
- Substrate POS 0.957 (Tier-A) + chunking 0.93 (validated) are STRONG
- The small-LLM comparison is UNSCOREABLE because the LLMs can't produce alignable output -- which itself evidences substrate's
  structural-labeling dominance (the LLM is so far from the task it can't even be measured), but can't be reported as a clean margin.

I will NOT build a POS v5 / chunking v2 (3 attempts confirm the wall). Per methodology-rule-7 (substrate-quality-first; comparison
empirical not driving): substrate POS/chunking stand on their Tier-A/validated numbers; NER carries the head-to-head north-star point.

Optional if you want a NUMBER: lenient positional alignment (truncate/pad LLM output, score regardless of mismatch) gives substrate
0.957 vs LLM ~0.12-0.25 -- but that scores unaligned garbage and the sanity gate exists to avoid it. I recommend AGAINST; UNKNOWN is honest.

## GPU lane status

All authorized GPU head-to-heads complete. GPU now idle (no pending authorized GPU work). Desktop free for you.

## Awaiting

Your Gap-7 QA scoring spec (prev note) to build the substrate-self-knowledge QA cell -- the next non-blocked CPU build.
Until then both lanes are at honest dependency gates (GPU work done; QA gated on scoring spec; E4 multi-day fresh-focus; E6 data-blocked).
