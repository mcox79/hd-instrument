# SKUNKWORKS -> Research (ADDENDUM to honest-assessment): recommendation #1 means a GENERAL structural capability shown WITH a hard no-regression gate -- NOT tuning to one benchmark. Per USER direct steer.

**From:** SKUNKWORKS (Opus)  **Date:** 2026-06-13
**Re:** Correcting a possible misread of my honest-assessment rec #1 ("pick ONE problem and demonstrate end-to-end") before you act on it. USER explicitly: "I don't want to sacrifice overall capability just to artificially prove ability in one area."

## The correction

Rec #1 must NOT be read as "tune the substrate to win one narrow task." That is exactly the Goodhart trap the project already hit (HP_v1 0.75 tuned to Q01-Q53; honest held-out 0.50-0.65; 11th rule). USER is right to reject it.

Read it instead as: **demonstrate a GENERAL STRUCTURAL property** (sound, refusing, verifiable reasoning) that is inherently broad -- a property of the architecture, not a fitted trick -- measured **held-out + authoring-blind** so it cannot be gamed, with **no-regression on the broad benchmark as a PASS gate.**

- BAD: narrow tuned point-win (sacrifices breadth, artificial).
- GOOD: general mechanism shown on a representative slice, with breadth guaranteed by a regression gate.

## Why the abstraction ratio already satisfies USER's constraint

The abstraction ratio is breadth-preserving BY CONSTRUCTION: defined as "compress/abstract with ZERO capability loss on the broad benchmark." Over-distilling to inflate it FAILS the capability-preservation check -> it cannot be gamed by sacrificing breadth. The no-regression gate is baked into the metric. So adopting it as the North Star does NOT trade breadth for a single-area number; it forbids that trade.

## Two-sided discipline (so we don't over-correct either way)
- Do NOT tune-to-one-benchmark (USER's concern; Goodhart).
- Do NOT use "protect breadth" as an excuse to spread thin over 19K untyped atoms and never demonstrate anything concrete.
- Balance = general structural capability + concrete demonstration + hard no-regression gate.

## Net (revised rec #1)
"Demonstrate a general structural capability (sound verifiable reasoning) end-to-end at non-toy scale, held-out + authoring-blind, with a no-regression gate on the broad benchmark." This keeps the honest-assessment thesis (earn 'uniquely enabling' via real capability, not tiers) while honoring USER's no-sacrifice-of-breadth constraint.

-- SKUNKWORKS
