---
problem: audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins
status: SOLVED
bar: "PASS = a prioritized, DISK-VERIFIED CATALOG (CATALOG.md) of every LIVE non-brain-faithful stand-in in the grounding-acquisition subsystem, each with FIVE disk-verified fields (the brain structure+computation it should implement / why the current thing is not it / the brain-foundational replacement / blast + live-vs-dormant with the consuming file:line / fix class), top-K ranked by blast, denominator = the subsystem's actual live import+call closure (reconciled against flag defaults, not comments), explicitly distinguishing live-defective vs live-but-inert vs dormant -- PLUS a powered can-fail LOCALIZATION of the #1 item on the subsystem's OWN metric (the grounding loop's ranking / growth-quality measure), with a machine-checkable pure-disk witness (verification/test_audit_grounding_subsystem.py) that reproduces every LIVE/DORMANT classification from disk. NO hdlab/ writes (Q111)."
result: "CATALOG.md = 4 LIVE stand-ins (G1 bag-of-content-words co-occurrence comparator; G2 grounded input channel imported-but-INERT; C7 attractor-as-ranker; C8 hd_fact_store trust-only vetting) + 3 located-negatives/corrections (N1 dormant+refuted structured encoder; N2 dormant VWFA; N3 six dormant-islanded orchestrators), each with all five disk-verified fields, top-K ranked. Denominator = the live import+call closure of Substrate.read() + the grounding-core run, classified by a runtime import+settrace trace (exp_audit_grounding_subsystem_v1.py): 16 LIVE-CALLED / 23 LIVE-IMPORTED-INERT / 6 DORMANT-ISLANDED, positive control fired. #1 LOCALIZATION (exp_ground_readout_localization_v1.py, n=999 SimLex pairs + n=1685 ConceptNet targets): a DISSOCIATION -- the brain-faithful ATL conceptual channel beats the co-occurrence family on grounded MEANING (SimLex rho 0.521 vs 0.371, +CI-sep, info-free twin loses) but does NOT beat it on the loop's OWN relatedness gold (ConceptNet prec@1 0.261 vs 0.248, CIs overlap; WordSim rho 0.432 vs 0.596, co-occurrence WINS) -> the #1 stand-in is locally optimal for a mis-specified (relatedness) objective over an ungrounded (co-occurrence) input. The #1 FIX was ALSO prototyped (owner 'do all'): a powered LOCATED NEGATIVE (exp_grounded_meaning_readout_v1, n=888 targets/810 pairs) that grounding the DISTRIBUTIONAL context does NOT transfer for reading-learned words (GROUNDED_CTX SimLex rho 0.041 loses CI-sep to BAG 0.061 AND PPMI counting 0.064; info-free twin valid at -0.01) -> sharpens the fix to DIRECT grounding (the target's own definition/sensorimotor features) + a meaning objective + online coverage, with the exact hdlab diff given. Witness 15/15."
floor: "Localization floors, all run: the co-occurrence STEELMAN = GloVe (ASSOC, a strong co-occurrence model; SimLex rho 0.371); the landed COUNTING floor on the live own metric = TOP_COOCCURRENT 0.0476/0.0653/0.0590 which the live bag read-out (SUBSTRATE 0.0159/0.0302/0.0272) LOSES to (disk-verified, data/exp_meaning_readout_own_metric_v1); the info-free TWIN = word->conceptual-vector permutation (near-chance, loses CI-separated). Catalog floor/positive-control: the reader-audit's C7/C8 handoff, both recovered as LIVE-CALLED and extended."
controls: "(1) runtime import+call trace with a POSITIVE CONTROL (tracer fired, caught process_sentence) separating LIVE-CALLED from LIVE-IMPORTED-INERT from DORMANT-ISLANDED -- excludes the 'imported != executed' false positive (caught grounded_similarity imported-but-inert; caught StructuralEncoder/parser/vwfa/three_tier dormant despite being importable). (2) info-free TWIN (word->vec permutation) LOSES on meaning -> the conceptual channel reads distinctive features, not a population artifact. (3) co-occurrence STEELMAN (GloVe, stronger than the live bag) still loses on meaning -> the wall is the co-occurrence FAMILY, not a weak implementation. (4) the ConceptNet own-gold EXCLUDES WordNet provenance -> no circularity with the WordNet-sourced conceptual channel. (5) do-not-over-fire: every LIVE-CALLED organ scanned; the brain-faithful HD/CLS organs (foraging=MVT, hippocampal=CA3, event_bundle/role_slot=FHRR-recall, definitional=WordNet supply) verified admissible, not flagged."
files_changed: "experiments/exp_audit_grounding_subsystem_v1.py (the import+call trace/denominator); experiments/exp_ground_readout_localization_v1.py (the #1 dissociation localization); experiments/exp_grounded_meaning_readout_v1.py (the #1 FIX prototyped -- a powered located negative that refines the fix to DIRECT grounding); verification/test_audit_grounding_subsystem.py (15/15 pure-disk witness); notes/problems/audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins/CATALOG.md (the deliverable) + SOLVED.md. NO hdlab/ writes (Q111 -- this is a MAP + proposed fixes + the #1 localization + the #1 fix prototyped)."
reverify: ".venv/Scripts/python.exe verification/test_audit_grounding_subsystem.py"
---

# Audit — the grounding-acquisition subsystem's non-brain-foundational stand-ins

**The deliverable is `CATALOG.md` in this folder** (4 LIVE stand-ins + 3 corrections, five disk-verified fields each,
top-K, admissible list, positive control). This SOLVED.md is the summary + the #1 full-stack-upstream localization +
the required sections.

## What I built
1. **The denominator, by enumeration not comment-grep** (`experiments/exp_audit_grounding_subsystem_v1.py`). A runtime
   **import trace** (5 fresh-subprocess closures) + a **settrace call trace** over the subsystem's live entry point
   `Substrate.read()` and a direct grounding-core run (`seed → process_sentence → checkpoint`, default flags). It
   classifies every hdlab module in the closure into **LIVE-CALLED (16)** / **LIVE-IMPORTED-INERT (23)** /
   **DORMANT-ISLANDED-ONLY (6)**, with a positive control (the tracer caught `process_sentence`) and twelve targeted
   probes. This is what let me separate a *live decision* from an *imported-but-inert* organ from a *dormant island* —
   the reader-audit's own lesson that "LIVE has three failure modes."
2. **The prioritized CATALOG.md** — G1 bag comparator (#1, CRITICAL), G2 grounded-channel-inert (HIGH), C7
   attractor-as-ranker (MEDIUM, bounded), C8 store trust-vetting (LOW, remediated), + N1–N3 located negatives.
3. **The #1 localization** (`experiments/exp_ground_readout_localization_v1.py`) — a powered can-fail DISSOCIATION on the
   loop's own metric, addressing the owner's full-stack-upstream directive step by step.
4. **The pure-disk witness** (`verification/test_audit_grounding_subsystem.py`, 14/14) that re-derives the classification
   from the current bytes and checks the two landed numbers.

## The #1 item, localized full-stack-upstream (the owner's four steps)

**Step 1 — is the end component 100% brain-foundational? What are its inputs? Is it research-supported?**
The end component is the grounding decision — `canonicalize` (nearest-anchor sense assignment) + the consolidation
gate. It is **NOT** brain-foundational: it decides meaning by a **cosine over a bag of nearby content-word codes**
(`canonicalize` `reading_grounding_loop.py:872–911`; `context_vector` `grounding_acquisition_loop.py:117`;
`schema_consistency_split_half` `:414–462`). Its inputs are (i) the context representation — a sum of sha256-seeded
**random bipolar codes** (`symbol_vector:297–310`), i.e. ungrounded word identities in a d=256 superposition; (ii) the
anchor space — the same bags; (iii) the gap signal (C7). The brain grows word meaning in the **anterior-temporal
semantic hub**, integrating **sensorimotor spokes + verbal/definitional experience** into a grounded distinctive-feature
code (hub-and-spoke: Lambon Ralph et al. 2017; Rogers & McClelland 2004; Binder & Desai 2011). A co-occurrence bag is a
different, lower-fidelity computation — the classic distributional convenience (Firth 1957), not the hub.

**Step 2 — trace, all the way up, where the signal on those inputs is lost.**
On the loop's OWN metric the bag read-out **loses to word-counting**: `SUBSTRATE 0.0159/0.0302/0.0272 <
TOP_COOCCURRENT 0.0476/0.0653/0.0590` (`data/exp_meaning_readout_own_metric_v1`, disk-verified). Two prior drills
already refuted the two obvious *comparator/input* fixes over the same bag — dependency **STRUCTURE hurts** (−0.0113
CI[−0.0195,−0.0030], `exp_structured_code_vs_flat_bag_c3_v1`) and sensorimotor **GROUNDING ties** the counting floor
(paired-perm p=1.0, `exp_sensorimotor_spoke_grounding_v1`). So the signal is not lost *in the cosine*; it is lost at
the **input representation** (ungrounded co-occurrence) and — the deeper find — at the **objective** (the loop's own
growth-quality metric is itself co-occurrence-shaped).

**Step 3 — dig deep: it is not brain-foundational *somewhere*. Where?** A powered can-fail dissociation (n=999 SimLex
pairs; n=1685 ConceptNet targets) pins it to **two coupled non-brain-foundational links**:
- **The input.** A brain-faithful ATL **conceptual** channel (WordNet gloss+genus distinctive-feature cosine) **EXCEEDS**
  on grounded-MEANING similarity where the co-occurrence family cannot: SimLex rho **0.521** vs GloVe (a strong
  co-occurrence steelman) **0.371** vs the wired grounded spoke **0.291**; the info-free **word→vector-permutation twin
  loses CI-separated**. So grounded meaning IS learnable/measurable — the co-occurrence input just cannot carry it.
- **The objective.** On the loop's OWN gold (ConceptNet-neighbour precision@1) the conceptual channel does **NOT** beat
  the co-occurrence family (0.261 vs 0.248, CIs overlap), and on a relatedness gold (WordSim) co-occurrence **WINS**
  (0.596 vs 0.432, CI-sep). The loop's own metric REWARDS association, and is blind to the meaning signal that separates
  the two channels on SimLex.
→ **The #1 stand-in is locally optimal for a mis-specified (relatedness) objective, over an ungrounded (co-occurrence)
input.** No comparator swap fixes that; the brain-faithful fix couples a **grounded input channel** with a **meaning
objective**. Both grounded inputs already exist in the process and are not fed to the decision: `grounded_similarity`
is **LIVE-IMPORTED-INERT** (funcs=0), and the conceptual/definitional channel fires only on explicit genus statements.

**Step 4 — are the tools cheap off-the-shelf things?** Yes, and named: the **co-occurrence bag** (Firth distributional
convenience) and the **ConceptNet/relatedness objective** are the easy distributional stand-ins; the brain uses grounded
ATL representations and a meaning objective. (The audit also confirmed no *external tool at inference* in the subsystem:
the WordNet lookups are admissible static foundation supply, and the in-substrate parser assets are dormant.)

**"Excel and exceed" + no downstream regression + upstream is brain-foundational (owner directive).** The brain-faithful
upstream representation (ATL conceptual channel) EXCEEDS the co-occurrence family on the *right* metric (grounded meaning,
+CI-sep, twin loses) — research-backed (hub-and-spoke; Rogers–McClelland covariance distillation). Because this audit is a
MAP (no hdlab writes), no live consumer is changed, so nothing regresses yet; the localization explicitly warns that
wiring the grounded channel WITHOUT also fixing the co-occurrence objective would move no board number (it ties on the
own metric) — the two must land together. That is the full-stack-upstream conclusion: **every link (input AND objective)
must be brain-foundational for the wall to fall.**

## THE #1 FIX, PROTOTYPED (owner directive: "do all, brain-foundational, right not easy")
The localization named the coupled fix (grounded input + meaning objective). I then built the INPUT half the
hard way -- and it produced a decisive, powered LOCATED NEGATIVE that sharpens the fix.

**What I built** (`experiments/exp_grounded_meaning_readout_v1.py`): the brain-faithful "learn a word's meaning
by composing the GROUNDED representations of its reading contexts" mechanism (ATL hub; Rogers-McClelland
covariance distillation). For each SimLex-999 target, gather its masked contexts from a MODERN corpus
(simplewiki; 19c banned), build four read-outs -- **BAG** (the live random-code stand-in), **GROUNDED_CTX**
(compose the context words' grounded conceptual vectors = the fix), **COUNTING** (a PPMI distributional floor),
**TWIN** (info-free permutation) -- all informativeness-weighted (PPMI, Church-Hanks) and common-mode-removed
(Carandini-Heeger divisive normalisation), scored on grounded MEANING (SimLex rho) + the loop's own ConceptNet
metric. Powered: n=888 targets, 810 pairs.

**The located negative (CI-separated, twin valid):** composing GROUNDED contexts does NOT transfer to
reading-learned words -- `GROUNDED_CTX` (SimLex rho **0.041**) LOSES to BOTH the plain `BAG` (**0.061**, delta
CI[-0.040,-0.0002]) AND the PPMI `COUNTING` floor (**0.064**, delta CI[-0.042,-0.008]); the info-free `TWIN`
sits at **-0.01** (control valid -- common-mode removal was the enabling move: before it, the twin scored a
spurious 0.055 and masked the result). **Mechanism, stated:** a word's CONTEXTS encode what it is RELATED to
(co-occurrence); grounding that relatedness does not recover the word's OWN distinctive meaning. Grounding the
DISTRIBUTIONAL context is the wrong lever -- which, with the two prior negatives (dependency-structure hurts;
sensorimotor-context ties), means NO transform of the co-occurrence context is the fix.

**Where the fix that EXCELS actually is (research-backed, already partly proven):** DIRECT grounding of the
target's OWN features. The localization proved a direct grounded/conceptual representation beats co-occurrence
on meaning (SimLex 0.521 vs 0.371, twin loses). For a word learned from reading that is: the on-page
DEFINITION/genus (`definitional_extraction`, already LIVE, 32% vs 8% distributional) and the sensorimotor spoke
(`grounded_similarity`, currently INERT), accumulated over encounters by ONLINE propose-verify (the north-star;
the brain does not batch-train). The lever is COVERAGE + a MEANING objective, not a better distributional comparator.

**The exact hdlab diff (for strategy to land, Q111 -- three coupled changes, landed TOGETHER):**
1. **DIRECT grounded read-out (not context-composed).** In `reading_grounding_loop.canonicalize` /
   `_make_grounding_gate` (`:1469`), compare the target's DIRECT grounded representation against grounded
   anchors, not the co-occurrence bag: wire the currently-INERT `grounded_similarity` spoke (36,810-word
   coverage) as the target's grounded code where covered, and keep/broaden `definitional_extraction` as the
   on-page direct-grounding path.
2. **MEANING objective.** Replace the growth-quality metric (ConceptNet-neighbour relatedness precision, on which
   the stand-in is locally optimal -- the dissociation) with a grounded-MEANING objective (SimLex-type
   substitutability); compute `schema_consistency_split_half` / `canonicalize` decisions in grounded space.
3. **COVERAGE via online growth**, not a single-pass distributional guess -- grow direct grounding by online
   propose-verify over encounters (MINERVA-2 episodic; the north-star), NOT the batch distributional composition
   this prototype refuted.
**DO NOT** (this prototype's located negative, plus the two prior ones): ground/structure the co-occurrence
CONTEXT representation -- it ties or loses PPMI counting.

## What I did NOT establish (honest bounds)
- I did **not** build the live grounding read-out's bag over a fresh corpus inside the drill; I used GloVe as a strong
  co-occurrence STEELMAN (so the argument is *a fortiori* — the live bag is weaker than GloVe) and quoted the landed live
  own-metric loss (SUBSTRATE < counting) directly. The dissociation is about the co-occurrence *family*.
- I did **not** re-solve grounding or wire anything — the learner turn-on and the fix are out of scope (Q111; named
  follow-ons below). The catalog is a MAP + the #1 localization.
- The C7 "bounded" verdict rests on the gap gate reading the RAW CA1 margin (`gap_detector.py:114–117`); I did not measure
  how often the attractor's settled argmax diverges from the true nearest neighbour (that quantification is pri-5's job).
- ConceptNet own-metric precision is low in absolute terms for every arm (~0.05–0.26) — it is a hard sparse metric; the
  load-bearing claim is the *relative* dissociation, not the absolute level.

## What I would withdraw first if wrong
The G2 framing that the grounded channel is "one wire from live." The dissociation shows wiring `grounded_similarity`
alone would tie the own metric (the objective is also the wall). If a reader reads G2 as "just wire it," that is the
over-claim to strike first — the localization is explicit that input AND objective must change together.

## KEY REALIZATIONS (the enabling moves)
- **The import trace had to trace CALLS, not imports.** The first pass ran the fixture's `import` statements *under*
  `settrace`, so every module body registered as a "call" and 40 modules looked LIVE-CALLED — including the dormant
  `StructuralEncoder` (its class body fired at import). Pre-importing before tracing and filtering `<module>` frames
  collapsed it to the true 16 LIVE-CALLED, and flipped `structural_encoder_dormant` from a false-negative to True. The
  live/dormant distinction is only meaningful once "executed a function" is separated from "was imported."
- **The obvious brain-faithful fix was a known double-negative — so I stopped and asked the deeper question.** Surveying
  prior work first showed dependency-structure HURTS and sensorimotor-grounding TIES on the live path. That killed
  "swap the comparator" and forced the real question: *why does every comparator over this input tie/lose?* — which is
  what surfaced the objective (the loop's own metric is relatedness).
- **The loop's own metric validates its own stand-in.** The single most useful measurement was scoring the
  meaning-winning conceptual channel on the loop's OWN ConceptNet gold and finding it *ties* the co-occurrence family. A
  metric that cannot tell grounded meaning from association cannot supervise a grounded learner — the objective is a
  stand-in, not just the representation.
- **A dormant-looking win can be a live *inert* input.** `grounded_similarity` is imported by the live path and never
  called — the grounded input the comparator needs is in the room and unused. "Imported ≠ consumed" is the input-side
  twin of the reader-audit's "computed-and-discarded."
- **The control was the finding.** In the fix prototype, common-mode removal (Carandini-Heeger) was the move that made
  the result readable: before it, the info-free twin scored a spurious 0.055 and would have let me mis-read a frequency
  artifact as a win. Centring collapsed the twin to ~0 and revealed the honest negative (grounded-context composition
  loses to counting). A brain-faithful *control* (divisive normalisation) rescued a brain-faithful *measurement*.
- **"Ground the input" split into two very different claims.** Grounding the TARGET's own features excels on meaning
  (localization, 0.52); grounding the target's CONTEXTS does not transfer (this prototype, a located negative). The
  distinction — direct vs distributional grounding — is the whole fix: a word's contexts are what it's *related to*,
  and relatedness stays relatedness however you encode it.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b — strategy re-verifies + folds in)
- **EXTENDS the existing "grounding ceiling is REPRESENTATION-bound" entry (2026-09-01):** the ceiling is representation
  **AND objective**. The live grounding read-out (bag-of-content-words cosine) loses to counting on its own metric; a
  brain-faithful ATL conceptual representation separates grounded meaning (SimLex 0.521 vs 0.371 co-occurrence, twin
  loses) but the loop's own growth-quality metric (ConceptNet-neighbour precision) is a *relatedness* gold on which it
  does not separate — so the stand-in is locally optimal for a mis-specified objective. Fix = grounded input + meaning
  objective, landed together.
- **NEW live-map for the grounding-acquisition subsystem (the reader-audit's excluded second entry point):** LIVE-CALLED
  decision organs = the bag comparator (`canonicalize`/`context_vector`/`schema_consistency`), the C7 attractor gap-gate,
  `hd_fact_store`, `definitional_extraction`; the grounded channel `grounded_similarity` is LIVE-IMPORTED-INERT; the
  StructuralEncoder + parser assets + VWFA + the six orchestrators (`three_tier_loop`, `gap_driven_reader`,
  `gather_reason`, `kg_traversal`, `prelim_tier`, `script_grain_acquisition_loop`) are DORMANT.
- **C7 refined:** LIVE but BOUNDED — the gap gate reads the honest RAW CA1 pre-settle cosine as its margin; only the
  attractor's *row-selection* (settled argmax, `iterative_attractor.py:125–126`) can drift to hubs. (Owned by pri-5.)
- **C8 confirmed remediated:** `hd_fact_store` vets by source-trust only, but the tautology/quality gate is live upstream
  (`_make_grounding_gate` `REFUSAL_TAUTOLOGY`); the correctness-cleanup problem is integrated.

## TLDR (plain English)
The system has a second way it runs that the last audit skipped: the part that LEARNS word meanings by reading. I traced
exactly what code actually runs when it learns (not what the comments claim), and made one ranked list of every place it
takes a convenient shortcut instead of working like a brain. The worst shortcut, switched on right now: to decide what a
new word means, it just checks which other words tend to sit near it — a word-company tally. On the system's own report
card that tally scores *worse than plain word-counting*. I then dug into WHY, all the way up the chain, and found the
loss is in two linked places, and I proved it: (1) the INPUT it reads is a bag of meaningless word-tags with no grounding,
and a proper brain-style "meaning from a dictionary-definition" representation beats the word-company tally on a real
human meaning test — while a scrambled version fails, so it's real; (2) but the system's own report card only measures
"do these words hang out together", not "do they mean the same thing", so it actually *rewards* the shortcut and can't
see the better method at all. So you can't fix this by tweaking the tally — you have to feed it grounded meaning AND
change what the report card rewards, together. I also found the grounded-meaning part it needs is already loaded into the
program but never actually used, and I confirmed a couple of earlier-flagged shortcuts are either switched off or already
fixed. I changed no live code (that's the other lane); this is the map plus the one deepest fix proven.

## QUESTIONS
None blocking. One judgement call for integration: I marked **SOLVED** because the bar asks for a disk-verified catalog +
a powered can-fail localization + a witness, and all three are delivered and green (14/14). If you would rather the #1
item's *fix* be prototyped end-to-end on the live loop before calling it solved, that is the named follow-on below, and
PARTIAL would be defensible — but per the brief ("this is a MAP + the one deepest fix localized", "NOT a full rebuild")
the audit deliverable is complete.

## NEXT STEPS (priority-ordered — the fixes this audit sets up; all are strategy-lands-it, Q111)
1. **[the #1 fix — now prototyped + sharpened] DIRECT grounding + a meaning objective + online coverage.** The fix
   is NOT to ground the distributional context (prototyped located negative above). It is the three coupled hdlab
   changes in "THE #1 FIX, PROTOTYPED": (a) a DIRECT grounded read-out (wire the inert `grounded_similarity` spoke +
   broaden `definitional_extraction`), (b) a grounded-MEANING objective (not ConceptNet relatedness), (c) COVERAGE by
   online propose-verify, land TOGETHER. This is the deepest fix and it gates the whole learn-by-reading line. *Worth
   filing: `ground_the_meaning_readout_directly_and_fix_the_cooccurrence_objective`.*
2. **[filed pri-5] C7 attractor-as-ranker → graded population read** in the gap gate
   (`replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop`). Bounded blast; do not
   duplicate — this audit confirms it LIVE and refines it to row-selection-only.
3. **[hygiene] Confirm C8 residual is telemetry-only** and close it — the correctness gate is already live upstream; the
   store-side is source-trust by design.
4. **[do-not-redo] Do NOT re-propose the on-disk dependency-structured encoder** (N1) — it is a landed CI-separated
   negative; only a non-starved, in-domain structured encoder is an open fair-test.
