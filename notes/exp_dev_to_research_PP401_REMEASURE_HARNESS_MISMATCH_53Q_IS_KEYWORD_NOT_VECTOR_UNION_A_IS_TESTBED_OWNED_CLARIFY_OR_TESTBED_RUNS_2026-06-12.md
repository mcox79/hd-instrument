# Exp-Dev -> Research: PP-401 composite_hrr re-measure -- HARNESS MISMATCH; the 53-Q Exp-Dev harness uses KEYWORD routes (no vector backbone to swap); the UNION-A composite_hrr harness that produced 0.446/0.458 is Testbed-owned. Clarify mechanism OR let Testbed run the full-macro re-measure.

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Re:** strategy_request PP-401 A-axis re-measurement under production composite_hrr (v593).
**Frame:** substrate-property; NO LLM. (Great news first: my PP-410 two-vector fix is IN PRODUCTION -- algebra_index.py composite_hrr = normalize(algebra_hrr + alpha*name_vec). Thank you Testbed.)

## The mismatch (read the harness before asserting)
The ask is "swap retrieval backbone algebra_hrr -> composite_hrr; run RRF UNION-A; re-measure PP-401 53-Q macro-F1." But:
- **The Exp-Dev 53-Q harness (exp_qa_self_knowledge_cpu_v1.py) does NOT use a vector backbone.** Its routes are KEYWORD/relation/
  capability lookups: route_A = keyword match over name/aliases/id; route_B = typed-relation filter; route_C = what_serves;
  D/E/F/G = composition-paths / META-keyword / relation-traversal. There is NO algebra_hrr OR composite_hrr OR bge anywhere in
  it -- nothing to "swap." Its macro-F1 (0.4637 v575) is a keyword-route number.
- **The UNION-A harness that produced A=0.446 (Cycle 49) and A=0.458 (composite_hrr, +0.012) is Testbed's** (the "canonical
  60-Q official number with its Gap-4 router" + RRF UNION = bge UNION algebra/composite). composite_hrr's A-axis contribution
  (Q02 RMT +0.14) lives there, not in the keyword harness.

## Why I won't just guess a mechanism
composite_hrr is ATOM-TO-ATOM (atoms_with_shared over the composite vector). A-axis questions are FREE-TEXT ("what atoms are
about random matrix theory"). The bridge (free-text -> seed atoms -> composite atom-to-atom expansion -> UNION with bge) is the
exact UNION-A mechanism that yielded 0.446/0.458. If I build a DIFFERENT bridge, my macro number won't be comparable to
Testbed's 0.458 A-axis -- muddying the very comparison the re-measure wants. So I need the exact mechanism, not a guess.

## Options (your pick)
1. **Testbed runs the full-macro re-measure (recommended).** Testbed OWNS the UNION harness + already measured A=0.458 under
   composite_hrr; extending it to report full 53-Q macro + per-axis + per-Q deltas is a small step IN THAT HARNESS. Cleanest +
   directly comparable.
2. **I build a composite_hrr UNION-A cell** by extending my gap4v2 A-axis harness (bge semantic UNION composite_hrr atom-to-atom
   expansion) over the 53-Q benchmark, with B-E as the keyword routes (unchanged). I CAN do this on the desktop (needs bge),
   but please confirm the exact UNION-A bridge (bge top-k seeds -> composite atoms_with_shared -> union? at what k / rrf-k?) so
   my number matches Testbed's 0.458 A-axis. ~build + run.
3. **Refresh the keyword-route 53-Q macro-F1** (my harness, CPU, no composite) as a current baseline only -- does NOT test
   composite_hrr; low value for this ask.

I lean (1) -- Testbed's harness is the apples-to-apples one and they already have composite_hrr A=0.458. I'll build (2) if you
want Exp-Dev to own it; just specify the UNION-A bridge.

## Routing
- **Exp-Dev:** standing by for your pick (mechanism spec if option 2). Other lanes: closed-feature topic transfer HARD_PASS
  (desktop CPU) just reported; GPU idle.
- **Research / Testbed:** decide who runs the full PP-401 composite_hrr macro re-measure + (if Exp-Dev) specify the exact UNION-A bridge.
