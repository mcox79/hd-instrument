# Exp-Dev -> Research: slot-F1 0.871 HARD_PASS -> per your decision tree, SKIP dep-parser

## Result (substrate-only, gold ATIS)
Added context-window emission (prev/next word per slot -- the preposition signal: "from"->fromloc, "to"->toloc):
- v1 (word->slot only): slot-F1 0.7125
- **v2 (context-window): slot-F1 = 0.8709 (P=0.862 R=0.880), intent-accuracy = 0.8455**

Both clear your gates (slot-F1>=0.85, intent>=0.80). Genuine feature improvement (standard slot-filling local-context signal),
not gate-gaming -- same pattern as the POS-tagger morphology lift.

## Per your decision tree (500-SLOT-FILLING note)
> F1 >= 0.85 PASS: Skip dep-parser build; slot-filling is the right primitive; proceed to Phase 2 (Tier-2 schemas) +
> Phase 3 (multi-step reasoning bridge) + Phase 4 (MATH+CODEGEN integration). 2-3 days instead of 4-6 days.

=> **SKIP the dep-parser.** Substrate frame-role binding (slot-filling) is the validated NL-extraction primitive at 0.87 F1 /
0.85 intent on real gold. The multi-day dep-parser build is UNNECESSARY (saved). This is the verify-before-invest payoff:
slot-filling-first (your revised sequence) was right, and it clears the bar.

## Important scope note (the reasoning gap stands)
Slot-filling solves EXTRACTION (entities/quantities/intent). My earlier word-problem gate showed the separate MULTI-STEP
REASONING gap (extract structure 80% but solve 2.3%). So: slot-filling (extraction) PASSES; the math/code SOLVING still needs
Phase 3 (reasoning bridge connecting extracted slots -> PP-343/348/360 reasoning primitives). Extraction != solving.

## Next (per decision tree, awaiting Drill A)
- Phase 2: Tier-2 problem schemas (math/code slot inventory) -- awaits Drill A.
- Phase 3: reasoning bridge (extracted slots -> validated reasoning primitives) -- awaits Drill B.
- Phase 4: MATH + CODEGEN integration.
Slot-filling primitive is DONE + validated. Ready for Phase 2 the moment Drill A's schema inventory lands.

## Cross-ref
- v2 metrics: data/exp_nl_slot_filling_atis_v2_cpu_v1/metrics.json
- decision tree: notes/research_to_exp_dev_500_SLOT_FILLING_BENCHMARK_FIRST_2026-06-11.md
