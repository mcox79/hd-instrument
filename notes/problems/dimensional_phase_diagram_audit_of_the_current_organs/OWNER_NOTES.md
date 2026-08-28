---
owner_verdict: DONE
---

SUBMISSION — SOLVER RESULT: dimensional_phase_diagram_audit_of_the_current_organs
STATUS: SOLVED | witness 18/18 PASS | ledger malformed:0 | hdlab UNTOUCHED (you land, Q111)
INTEGRATE ONLY on owner_verdict: DONE in notes/problems/<slug>/OWNER_NOTES.md.
REVERIFY: .venv/Scripts/python.exe verification/test_dim_phase_diagram.py  (18 checks, live recompute, ~4 min)

ONE-LINE: Dimensionality (N) is NOT a bottleneck anywhere in the substrate — the register is STRUCTURAL at
D=1024, meaning is sparse-exact, and the memory stores were ALREADY pinned to 8192. The substrate spans FOUR
distinct capacity laws across its store families (not one universal sweep), and the real fidelity/performance
levers are all non-dimensional: the memory READOUT rule, code ORTHOGONALITY, and — the biggest LIVE one — the
cortical/consolidated READ regime.

THE BAR (PROBLEM.md §7): phase curve per organ + composed reader (floor + info-free twin recomputed AT EACH D);
per-ceiling STRUCTURAL vs UNDER-DIMENSIONED verdict; a positive control that the harness SEES a cliff; distinguish
the more-D vs more-SPARSITY lever; one-screen summary table. "A rigorous NEGATIVE (all already saturated at D=1024)
is a FULL PASS." => delivered as a full-pass NEGATIVE on N, plus positive non-dimensional findings.

RESULT (two parts):
(1) NEGATIVE on N. Register real-task ORACLE decode FLAT across D=256..8192 (0.60→0.61, all CIs overlap) =>
    STRUCTURAL; wall is front-end LINKING (ACTR 0.17 vs ORACLE 0.60), not capacity. Meaning = sparse-EXACT (no
    fixed D; signal by K*≈256, SimLex rho 0.568). Memory stores already at N_DIM=8192 with documented envelopes ->
    brief premise "all at D=1024, never swept" is FALSE on disk.
(2) The real levers (none dimensional): READOUT (register argmax cliff is ~4x a readout artifact — CA3/resonator
    joint completion 0.64→0.99 at load 64); CODE ORTHOGONALITY (dominates N; ρ≥0.6 → near chance even with
    dimensional headroom; real WordNet codes ARE correlated 0.039 vs 0.025, DG decorrelation recovers 0.71→0.96);
    precision bites only at q=2; depth is a non-lever.

STORE-FAMILY CENSUS (4 distinct dimensional laws; the register does NOT generalise across families):
  vector-bundle/dense-cleanup  ~N/log2(N)  (register + vsa_cleanup_memory.capacity_curve AGREE — cross-validated)
  sparse-coded autoassociative  Willshaw C/(a·ln 1/a) > bundle  (DG raises it)
  matrix-Hebbian relational     ~16·N  (~190x the bundle!) — kg_traversal/multi_hop, the actual multihop memory
  multi-timescale temporal      floor set by PERIOD spectrum, NOT 1/√D — graded_temporal_context (D = timescale bank)

POSITIVE CONTROL + LEVER: synthetic FHRR cliff (V=100) collapses 0.995→0.529 (load 16→64 @ D=256), recovers 0.988
  @ D=1024; M*(D) doubles with D. Sparsity is a distinct lever (+0.497 from multibank at fixed D; multibank's own
  cliff at per-bank ~64 = working_memory's documented threshold). Info-free twins recomputed everywhere, all LOSE.

TWO INTEGRITY CORRECTIONS (from consulting the substrate — please carry these):
  1. My synthetic cliff REPRODUCES an existing closed form, hdlab.k_cliff_scaling.k_cliff(N)=0.87·N/log2(N) — it
     is a positive control on the harness, NOT a new law. Cited.
  2. My "multihop directedness DEFECT" was on a NAIVE commutative-bind edge store. The substrate's REAL multihop
     organ (kg_traversal.KGStore + multi_hop) is directed by construction (relation-typed key + asymmetric Hebbian
     W; verified) and already does Modern-Hopfield inter-hop cleanup. On CLEAN chains it reasons PERFECTLY to 8
     hops at every D — so the documented "K=2 limit" is DATA ambiguity (multi-valued edges/fan-out), not mechanism
     or dimension. Downgraded to a caution about naive storage, NOT a substrate gap.

BIGGEST LIVE LEVER — and it is NOT this slug's, it's ALREADY FILED (route it, don't re-open here):
  The cortical/consolidated READ regime. Measured (exp_addressed_store_partial_cue_v1): a RELATED cue retrieves the
  right family at 1.00 with a DISTRIBUTED semantic code but 0.12 (~chance) with the exact-key hash the substrate
  currently reads = +0.88 generalisation headroom; real WordNet arm confirms (nn-sim 0.41 vs 0.05). This reproduces
  the audit's "exact-key 0.93, held-out 0.004." It is a REINFORCING datapoint for the filed PARTIAL problems
  `the_consolidated_cortical_store_is_written_but_never_read` and `cortical_read_never_tested_where_it_matters` —
  please attach it there; I did NOT build the wiring (that would compete with filed work, Q113).

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md): (a) add CODE ORTHOGONALITY / FEATURE_OVERLAP as a first-class fidelity
  axis — it dominates N and our iid-random/maximal-orthogonality code assumption is an unflagged OUR-INVENTION;
  fix = DG sparse pattern separation. (b) The substrate is NOT uniformly D=1024 (stores at 8192). (c) Register D
  verdict = STRUCTURAL @1024 (reinforces "binding constraint is the front-end, not memory").

PROPOSED hdlab (you land; I did NOT write hdlab/):
  1. Swap the register's argmax cleanup for CA3/resonator JOINT completion (recovers ~4x load in the high-fan/
     book-scale regime; complements p2). 2. Add code-orthogonality + numeric-precision as first-class audit axes;
     add a DG-decorrelation check before autoassociative storage. 3. Optionally prototype the ADAPTIVE CONTROLLER
     (confidence-gated lever recruitment) as a substrate service — the phase diagram is a runtime control surface.
  DO NOT: raise D anywhere as a capacity fix (ruled out); build a directedness fix for multihop (already handled).

DO NOT QUOTE: N/dimensionality as a performance lever (it isn't, anywhere); the multihop "directedness defect" as
  a substrate gap (it's a naive-storage caution — the real organ is fine); the +0.88 cortical-read number as MY
  result (it belongs to the filed cortical-read problems); any single capacity number across store families (they
  obey DIFFERENT laws — ~N/12 vs ~16N differ ~190x).

FILES: experiments/exp_dim_phase_diagram_{register,axes,cleanup_rule,multihop,partialcue,adaptive,realcode,stacked,
  realtask,meaning,census,multihop_real,temporal}_v1.py + exp_addressed_store_partial_cue_v1.py;
  verification/test_dim_phase_diagram.py; notes/problems/<slug>/SOLVED.md; data/exp_dim_phase_diagram_*_v1/*.json.
  15 experiments; NO hdlab/.

TLDR (plain language): We worried each memory was stored at too-low a resolution (1024 numbers) and never checked.
  We checked exhaustively: resolution is NOT the problem anywhere — the memory that packs things into one vector
  works the same at 256 as at 8192 on the real task, the meaning part is an exact lookup, and the big long-term
  stores were already set high on purpose. The substrate actually runs on FOUR different capacity rules for its
  different memory types (one is ~190x roomier than another), so "is the number big enough" has different answers
  in different places — and it's "yes, fine" nearly everywhere. The things that DO limit it are not resolution:
  how the memory is READ (a smarter read recovers ~4x more), how DISTINCT the internal codes are (overlap hurts;
  the brain's sparse trick fixes it), and — the big live one — that the system reads memory through a lookup that
  only recognises EXACT matches and generalises to related things at chance, where a brain-style overlapping code
  would generalise perfectly (a ~+0.88 gap). That last one is the real performance headroom, and it's already a
  filed problem — this result hands it a strong datapoint.

QUESTIONS: none blocking. One scope note: the cortical-read finding is a diagnostic that belongs to the filed
  consolidation problems, not this slug — please route it there rather than integrating it under this audit.
NEXT STEPS: (1) land the CA3/resonator readout + the two new audit axes; (2) route the cortical-read datapoint to
  `the_consolidated_cortical_store_is_written_but_never_read`; (3) the 20-min deepening cron continues finer
  per-organ operating-point checks in the background — CronDelete it once you've integrated.
