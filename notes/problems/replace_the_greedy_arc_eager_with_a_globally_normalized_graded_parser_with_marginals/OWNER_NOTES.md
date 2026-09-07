---
owner_verdict: DONE
---

SUBMISSION -- replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals
status: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO external LLM at inference. NO hdlab/ written
(Q111 -- a PROMOTION-READY module + exact wire points are provided). Wrote only experiments/, verification/,
notes/problems/<slug>/. Ledger --check clean (malformed 0). Reuses the LANDED hdlab.arc_parser + UD-EWT (modern gold).

REVERIFY (15 witnesses; the first is the promotion gate = brute-force exactness):
  .venv/Scripts/python.exe verification/test_graded_parser_promote.py        # 4/4 (promotion gate: exact + valid API)
  .venv/Scripts/python.exe verification/test_matrix_tree_parser.py           # 5/5 (brute-force exactness + attachment + marginal)
  .venv/Scripts/python.exe verification/test_matrix_tree_noregress.py        # 4/4 (no-regress + invalid-tree positive control)
  .venv/Scripts/python.exe verification/test_matrix_tree_patient_lift.py     # 5/5 (marginal reliability + twin + calibrator gain)
  .venv/Scripts/python.exe verification/test_matrix_tree_deepen.py           # 4/4 (wrong-pick decomposition + obl reader beats calibrator)
  .venv/Scripts/python.exe verification/test_matrix_tree_upgrades.py         # 4/4 (Hale entropy + universal per-label reliability)
  .venv/Scripts/python.exe verification/test_matrix_tree_singleroot.py       # 3/3 (grammar-faithful single-root, exact)
  .venv/Scripts/python.exe verification/test_matrix_tree_ood.py              # 3/3 (OOD generalization, QA-SRL)
  .venv/Scripts/python.exe verification/test_argstructure_unification_organ.py # 4/4 (ABSOLUTE who-did-what gain, ensemble)
  .venv/Scripts/python.exe verification/test_parsemiss_recovery.py           # 4/4 (marginal exposes 77.5% of parse-miss gold)
  (+ test_full_brain_chain 4/4, test_valency_unification_organ 4/4, test_document_discourse_organ 4/4,
     test_matrix_tree_thematic_fusion 3/3)

HEADLINE. Built the globally-normalized graded parser over the landed arc-factored scorer: exact Chu-Liu/Edmonds MAP
+ exact SINGLE-ROOT Matrix-Tree edge MARGINALS (Koo 2007) + an exact 2nd-best tree, all BIT-EXACT vs brute-force
enumeration of every spanning arborescence (n<=4). Key reframe: the arc-factored score is ALREADY global (sum of arc
potentials, no label bias) -- the deviation was the greedy DECODE; and the exact marginal sums over ALL trees, so
gold is never pruned (search failure structurally eliminated).

ALL SIX BAR CONDITIONS MET (modern UD-EWT). Plus a full deepening + upgrade program:
 - RELIABILITY: the RAW marginal is a strong right-vs-wrong signal (AUC 0.855 all-arc / 0.765 patient vs greedy 0.613)
   and on OBL attachment it BEATS the entire landed obl calibrator (0.782 vs 0.736) -> drop the obl logistic; it is a
   UNIVERSAL per-label reliability (median AUC 0.825 / 29 labels); live patient defer 0.879->0.947 CI-sep, twin flat.
 - ABSOLUTE who-did-what GAIN (the breakthrough, after the owner pushed on a weak first cut): the marginal wired into
   ROLE SELECTION via a Competition-Model ensemble (labeled-reader anchor + marginal + argument-vs-adjunct typing)
   BEATS the strong labeled reader CI-sep: 0.8785 -> 0.8850 (+0.0065 CI[+0.0008,+0.0121]). SUPERSEDES the earlier
   "absolute recovery is a located negative" (that was a WEAK impl -- fall-back cascade + wrong cues).
 - HALE parse ENTROPY: a graded sentence-difficulty signal the greedy 1-best cannot give (Spearman 0.70; defer +0.058).
 - PARSE-MISS RECOVERY: on the 34% slice where greedy never attached gold to v (floor 0), the marginal EXPOSES gold
   as a top-2 head 77.5% of the time (twin 2.5%); selection among exposed candidates is the remaining gap.
 - NO-REGRESS + positive control (greedy leaves invalid non-tree parses on 7.2% of sents; MST recovers gold there).

FaithFULLY DRILLED (owner: research all walls; do it right). 4 biology-first drills + a diagnostic corrected two of
my own errors: (i) the two-valid residual is 66% ROLE / 34% PARSE-miss (addressable), NOT 67% irreducible; (ii) the
faithful mechanism is JOINT frame unification (Hagoort MUC: argument-vs-adjunct typing, core-object uniqueness), not
a per-arc prior (redundant with the parser by construction). The arg/adjunct typing is load-bearing standalone (twin
0.85->0.55). Located negatives that remain honest: the coarse document-discourse organ (Centering + IC) recovers ~0
on naturalistic gold (needs full coref + comprehensive IC norms); the reversible/Winograd minority needs grounded
event-knowledge. WALLS_RESEARCHED_2026-09-07.md has the full synthesis.

IMPLEMENTATION (promotion-ready): experiments/graded_parser_promote_v1.py = GradedParse(parse -> map_heads +
single-root marginals + 2nd-best) + patient_confidence_cue + attachment_reliability + self_test(), the exact module
to copy into hdlab/graded_parser.py.

PROPOSED hdlab WIRES (Q111 -- all off ONE marginal = one matrix inverse/sentence; additive, heads byte-identical):
 1. HIGH: marginal -> parse_confidence a2_marg slot, OBL FIRST (drop the obl logistic; +0.048), then patient (+0.008).
 2. HIGH: marginal + arg/adjunct typing -> structural_patient_pick as a Competition-Model re-ranking cue (ABSOLUTE
    +0.0065 CI-sep), candidates including the marginal's parse-miss reach, anchored on the labeled pick.
 3. HIGH: ship single-root marginals + exact CLE decode (eliminates the 7.2% invalid-tree parses; UAS +0.002 CI-sep).
 4. MEDIUM: expose Hale entropy (sentence defer) + a modern selective-reliability board arm.
 EFFICIENCY: compute the marginal once, reuse everywhere; DROP the exact 2nd-best TREE from the read path (weak live
 lever, 5% vs the marginal's 77.5%); single-root is free (same inverse).

DO NOT: chase UAS; use the exact 2nd-best TREE as a live lever; train a deep OOD-losing parser; use an external LLM;
 re-attach the parse post-hoc; lean on 19c gold; REPLACE the labeled reader (ensemble with it -- a standalone
 structural selector loses the easy cases).

KEY REALIZATIONS: (1) the arc-factored scorer was ALREADY globally-normalized -- only the DECODE was greedy; a
different object from the settled arc-eager small-beam negative. (2) verify marginals vs brute force BEFORE trusting
any number (caught the Laplacian indexing + the singular-matrix fix). (3) a fair test of a WEAK impl is not a fair
test of the brain's mechanism -- the owner's push converted two located negatives into an absolute gain by (a)
diagnosing role-vs-parse errors and (b) building the FAITHFUL joint frame unification + ensembling instead of
replacing. (4) the incremental lever in the absolute gain is THIS problem's own deliverable -- the marginal.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md sec 2b, parser): the Matrix-Tree north-star is BUILT + validated; the
parser is brain-foundational in STRUCTURE + DECODE + posterior; the marginal lifts reliability AND absolute
who-did-what; the residual is two DISTINCT organs (k-best-forest parse-miss selection; grounded-event-knowledge /
full-coref for the reversible minority), each PINNED, each a separate build.

TLDR (plain English): the reader's grammar engine made one snap decision per word with no runner-up; I rebuilt it to
keep an exact spread of possible structures (proven correct against brute force), and one cheap calculation off it
now pays off many ways -- it beats our hand-tuned certainty model, works for every grammatical link, gives an honest
"how hard is this sentence," finds the right word-to-verb link 77% of the time even when the old parser missed it
entirely, and -- once I fixed a wrong first attempt and combined it with our existing reader instead of replacing it
-- nudges who-did-what accuracy up a real, statistically-clean notch. The remaining hard cases (choosing between two
equally-good characters) genuinely need story/world knowledge, scoped as separate builds.

QUESTIONS: none. NEXT STEPS: land wires 1-3 (all off the one marginal); drop the live 2nd-best-tree computation; file
the two follow-ons (k-best-forest parse-miss selection; grounded event-knowledge / full-coref discourse).
