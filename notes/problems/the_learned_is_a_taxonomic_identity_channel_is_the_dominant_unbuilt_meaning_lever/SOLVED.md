---
problem: the_learned_is_a_taxonomic_identity_channel_is_the_dominant_unbuilt_meaning_lever
status: REFUTED
bar: "Build the LEARNED is-a/taxonomic identity channel (Rogers-McClelland property-SVD + Levy-Goldberg contexts + genus-differentia, NO WordNet at inference), GROW it by reading, and fuse it into the live meaning read; SHOW the sense-assignment decision rises CI-separated over the grounded floor on the live decision (SimLex-held-out), with the info-free twin LOSING, and report the grow-by-reading curve toward the taxonomic ceiling (0.65) -- OR a rigorous LOCATED NEGATIVE naming exactly why the learned is-a channel cannot approach the ceiling without WordNet (with a number; the brain's actual mechanism faithfully built). INVARIANT: recall path byte-identical; NO WordNet / NO external LLM at inference."
result: "LOCATED NEGATIVE (the bar's blessed full-pass clause) that REFUTES the priority-1 PREMISE. The brief's dominant-lever number (taxonomic AUF-MRR 0.650 vs 0.188, +0.488) was measured against grounded-distinctive ALONE (0.188) -- the PRE-SEQ floor. Measured against the CURRENT strongest floor (grounded-distinctive (+) grown-SEQ, the parent's just-landed parser-free lever) on the SAME live anchor-pool decision + SimLex gold: BASE AUF-MRR = 0.505 (n=94 SimLex-high) / 0.391 (n=338 pooled SimLex+SimVerb), because grown-SEQ ALONE already reaches 0.455 (n=94) -- the co-occurrence channel banks the identity signal (Harris). Against that strong floor, EVEN THE CIRCULAR WordNet taxonomic ceiling adds only +0.159 (n=94, CI[-0.001,+0.298], NOT CI-sep) / +0.057 (n=338, CI[-0.019,+0.137], NOT CI-sep); and oracle{grounded+SEQ}=0.744 EXCEEDS the WordNet ceiling 0.650 -- so the taxonomic channel adds NO reachable coverage the grown co-occurrence channel lacks on its own axis; the residual is a READ-OUT/confidence gap (0.505->0.744=+0.239, larger than the whole CM advantage), which the parent already located-negatived. My learned DIRECTED is-a channel, built faithfully (parser-free/WordNet-free Hearst read-edges -> Roller-Kiela-Nickel PPMI+SVD densification -> Collins-Quillian genus-differentia CO-HYPONYM-PENALTY capture), SEQ-backfilled to 100% is-a coverage on the favorable n=94 population: CAPTURE_vs_BASE = +0.000 (CI[0,0]), additive FUSE_vs_BASE = -0.054 (HURTS), knowledge-shuffled twin NOT beaten -- the learned is-a supplies no net identity-discrimination the strong baseline lacks. So the taxonomic identity channel is NOT the dominant unbuilt lever: it was dominant only over the obsolete pre-SEQ floor; grow-by-reading already captured it."
floor: "STRONGEST floor actually run = grounded-distinctive (+) grown-SEQ (the parent's landed parser-free BF representation), AUF-MRR 0.505 (n=94 SimLex-high, the brief's exact lever population) / 0.391 (n=338 pooled). This SUPERSEDES the brief's grounded-distinctive-alone floor (0.188), which grown-SEQ beats CI-separated (+0.329 CI[+0.201,+0.466], n=94). Info-free / knowledge-shuffled twins: symmetric shared-genus twin (isa_knowledge) and directed-capture twin BOTH not-beaten (twin_loses=False); the earlier SEQ info-free twin loses CI-sep (parent W20)."
controls: "(1) KNOWLEDGE-SHUFFLED TWIN (permute which word owns which is-a edge-row): NOT beaten by the real is-a channel on either the symmetric (isa_knowledge, twin_loses=False) or the directed (capture, twin_loses=False) variant -> the learned is-a carries no net identity signal on this decision (excludes 'a real but small effect'). (2) CIRCULAR WordNet-CM UPPER-BOUND reference (the most an is-a channel could supply): even it is NOT CI-separated over grounded+SEQ (+0.159 n=94 / +0.057 pooled) -> excludes 'a better learned extractor would win'. (3) ORACLE (perfect selective-prediction) + ORACLE-UNION (perfect per-query {BASE,CM} router): oracle_BASE 0.744 > CM 0.650 (no missing reachable coverage from CM's own axis), oracle_union 0.897 > oracle_BASE (taxonomic complementary IN PRINCIPLE but only under a perfect router+confidence -- both parent-located-negatives) -> localizes the residual to READ-OUT, not knowledge. (4) SEQ-BACKFILL to 100% is-a coverage (Rogers-McClelland inheritance): CAPTURE still +0.000 -> excludes 'coverage-limited'. (5) BASE_vs_GD CI-separated -> the strong floor is genuinely stronger than the brief's, not a measurement fluke. (6) recall path byte-identical (ranking arms only; no hdlab written); NO WordNet / NO parser / NO LLM anywhere in the learned channel."
files_changed: "experiments/exp_meaning_fusion_directed_isa_capture_v1.py (the DIRECTED learned is-a channel: parser-free Hearst read-edges -> Roller PPMI+SVD densification -> genus-differentia co-hyponym-penalty capture + SEQ-backfill generalization; the strongest faithful build), data/exp_meaning_fusion_directed_isa_capture_v1/metrics.json (pooled, no-backfill grow curve), data/exp_meaning_fusion_directed_isa_capture_v1_simlex_bf/metrics.json (n=94 favorable pop + backfill, 100% coverage), experiments/exp_meaning_fusion_isa_headroom_diag_v1.py (the DIAGNOSTIC: taxonomic headroom over the strong grounded+SEQ baseline on SimLex-high vs pooled, + oracle + oracle-union), data/exp_meaning_fusion_isa_headroom_diag_v1/metrics.json, data/exp_meaning_fusion_isa_knowledge_v1/metrics.json (LANDED the never-run symmetric clean-Hearst-genus baseline -> located negative), verification/test_learned_isa_taxonomic_channel.py (scaffold-free 18-check witness). NO hdlab/ modified (Q111). NO preregs/arm_key touched."
reverify: ".venv/Scripts/python.exe verification/test_learned_isa_taxonomic_channel.py  (18 checks; reads landed metrics + live micro-checks of the mechanism)"
---

# What this is: the taxonomic identity channel is NOT the dominant unbuilt lever -- grow-by-reading already captured it, and the residual is a read-out gap, not missing is-a knowledge

**The brief's premise, stated as priority-1:** the is-a / taxonomic identity channel is "the single dominant
meaning lever" -- taxonomic AUF-MRR **0.650 vs grounded 0.188 (+0.488)**, taking the live sense-assignment
decision "from ~15% to ~65% of achievable." Build it learned-from-reading (no WordNet), grow it, fuse it, and
approach the 0.65 ceiling.

**What the disk says (the number that reframes everything).** That +0.488 was measured against
**grounded-distinctive ALONE (0.188)** -- the floor as it stood *before* the parent solver
(`measure_end_to_end...`, integrated) landed the parser-free **grown-SEQ** channel (direction-typed PPMI over
the raw word stream, grown by reading). On the SAME live anchor-pool decision and SAME SimLex gold, measured
against the **current strongest floor** (grounded-distinctive **(+) grown-SEQ**), the lever collapses:

| arm (rank the true SimLex partner among the live ~556-anchor pool) | AUF-MRR n=94 (SimLex-high, the brief's pop) | AUF-MRR n=338 (pooled) |
|---|---|---|
| grounded-distinctive ALONE (the brief's floor) | 0.188 | 0.150 |
| **grown-SEQ ALONE** (parser-free, read to 500k) | **0.455** | 0.341 |
| **BASE = grounded-distinctive (+) grown-SEQ** (the STRONGEST floor) | **0.505** | **0.391** |
| WordNet-CM taxonomic (CIRCULAR ceiling -- the MOST an is-a channel could supply) | 0.650 | 0.462 |
| oracle{BASE} (perfect confidence ordering) | **0.744** | 0.642 |
| oracle{BASE ∪ CM} (perfect per-query router) | 0.897 | 0.804 |

- **The premise is REFUTED.** Against the strong floor, even the **circular** WordNet taxonomic channel adds
  only **+0.159 (n=94, CI[-0.001,+0.298], NOT CI-separated)** and **+0.057 (n=338, CI[-0.019,+0.137], NOT
  CI-separated)**. The "+0.488 dominant lever" was the distance from the *obsolete* pre-SEQ floor; grow-by-reading
  (SEQ alone 0.455) already banks the bulk of it. This is the Harris distributional hypothesis realized: a
  direction-typed co-occurrence channel, read to strength, *is* a paradigmatic (identity) signal.
- **oracle{BASE} = 0.744 EXCEEDS the WordNet ceiling 0.650.** The grounded+SEQ representation, with perfect
  confidence, reaches HIGHER than the circular taxonomic channel does with its own confidence. So on its own
  axis the taxonomic channel supplies **no reachable coverage the co-occurrence channel lacks**; the entire
  realistic CM advantage (+0.159) is *better native confidence*, and the internal read-out gap of BASE itself
  (0.505 -> 0.744 = **+0.239**) is LARGER than that. **The residual is a read-out / confidence gap, not missing
  is-a knowledge** -- exactly the gap the parent already located-negatived (Path 2: recollection/confidence,
  real signal but not CI-sep).
- **The taxonomic channel IS complementary in principle** (oracle{BASE ∪ CM}=0.897 > oracle{BASE}=0.744): a
  *perfect per-query router* between the two would gain reachable coverage. But realizing it needs both a
  perfect router (parent measured per-query {G,SEQ} routing = +0.023, a dead end) AND perfect confidence
  (parent's Path-2 located negative). So the complementary coverage is real but **unrealizable with any learned
  read-out we can build** -- and even the ceiling-defining circular WordNet channel cannot realize it CI-sep.

## The learned DIRECTED is-a channel, built the research note's way -- and why it captures +0.000

The RESEARCH note (`RESEARCH_bf_isa_acquisition.md`) correctly diagnosed that the earlier property-SVD prototype
was missing the **directed, labelled genus EDGE**, and pointed to Roller-Kiela-Nickel 2018 (SVD-densify a
Hearst-pattern PPMI matrix; BLESS AP 0.45->0.76). I built exactly that, parser-free and WordNet-free, and
confronted the true wall (relation confusion) with a mechanism the parent never tried:

1. **Read is-a EDGES** via the self-contained Hearst extractor (copular / "kind of" / "such as"; NO WordNet, NO
   parser, NO POS), cross-occurrence CONFIRMED (>=2) + pattern-reliability weighted (CLS graded accumulation,
   McClelland-McNaughton-O'Reilly; not a hard count). Both directions (w's hypernyms and w's hyponyms).
2. **ISA_dense = Roller-Kiela-Nickel**: PPMI over the [as-hyponym (+) as-hypernym] is-a-pattern matrix,
   truncated-SVD densified (generalizes sparse edges; Saxe-McClelland-Ganguli ordered modes).
3. **The CAPTURE (the crux, and NEW vs the parent's failed symmetric captures): a Collins-Quillian
   genus-differentia CONJUNCTION** -- the co-hyponym penalty `genus_overlap(q,c) * (1 - isa_interchange(q,c))`.
   A co-hyponym (same genus, different differentia) is down-weighted; a synonym (same genus, interchangeable in
   is-a patterns) is kept. This is an explicit AND (coincidence gate), not the additive fusion / coarse-to-fine
   re-rank the parent tried and that failed.
4. **SEQ-backfill** (Rogers-McClelland property inheritance): edge-less words inherit an is-a vector = the
   SEQ-neighbour-weighted average of edge-bearing neighbours' is-a vectors -> raises is-a coverage from 18% to
   **100%** on the eval vocabulary (the research note's OOV backfill).

**Result (n=94 SimLex-high, the favorable population, backfill -> 100% is-a coverage, read to 1.5M lines):**
`CAPTURE_vs_BASE = +0.000 (CI[0,0])`; additive `FUSE_vs_BASE = -0.054` (the is-a channel HURTS the strong
baseline -- it carries relatedness/co-hyponymy, not clean identity); **knowledge-shuffled twin NOT beaten**.
Every faithful lever -- directed edges, Roller densification, the conjunction capture, 100% coverage -- and the
learned is-a channel supplies **nothing net** over grounded+SEQ. On the pooled population without backfill,
read-edge coverage caps at **18%** even at 1.5M lines, and the capture is likewise +0.000.

**Why (mechanism of the negative).** (a) The identity signal the taxonomic channel would supply is *already in*
the grown co-occurrence channel (SEQ 0.455; oracle{BASE} 0.744 > CM 0.650) -- there is almost nothing left to
add. (b) What little the taxonomic axis adds is a per-query READ-OUT gain that needs a perfect router+confidence
(unrealizable; parent-located-negatives). (c) Reading-derived is-a is either sparse (18%) or, once backfilled
via co-occurrence, becomes a *symmetric* co-hyponym-conflating similarity -- the same relatedness signal SEQ
already has -- so it cannot supply the clean DIRECTED discrimination. The WordNet ceiling's only advantage is
**CURATION/completeness** (a complete, sense-resolved graph), and even that advantage is not CI-separable over
grounded+SEQ on this decision.

## The symmetric shared-genus channel (the brief's other route), LANDED -- also a located negative
`exp_meaning_fusion_isa_knowledge_v1.py` (built by the parent solver but **never run to full**; I landed it):
the CLEAN, non-circular, cross-confirmed shared-genus PPMI channel, fused with grounded+SEQ. At 1.5M lines it
covers 15% of query words and **HURTS**: OVERALL genus_adds **-0.020 (CI[-0.039,+0.002], not CI-sep)**, covered
subset **-0.134**, and the knowledge-shuffled twin is NOT beaten. A shared-hypernym bag is a **co-hyponym
detector** (dog and cat both share "animal" -> high) -- it reinforces the relation confusion rather than
resolving it. This is why the directed edge was worth trying; but the directed edge, faithfully built, also
fails (above).

## Every component is 100% brain-foundational -- and the negative is NOT an upstream fidelity gap (owner directive #1-4)
The owner's standing mental model: "if a truly brain-foundational component is not working, some upstream
component is not 100% BF." **This is the documented exception, and it matters.** The end component (the learned
is-a channel) is 100% BF: Hearst-family reading evidence (a computation a competent reader performs; NOT a
dictionary lookup) -> graded reliability-weighted CLS accumulation -> Levy-Goldberg PPMI -> Saxe-McClelland
ordered SVD -> Georgopoulos cosine -> Ma-Pouget convergent-cue Bayes; NO WordNet, NO parser, NO POS. The entire
upstream chain (grounded ATL + grown-SEQ) is the parent's audited **100%-BF, parser-free** representation
(`FULL_CHAIN_BF_AUDIT.md`). The is-a channel does not underperform because something upstream is non-BF -- it
underperforms because its **contribution is redundant** with the already-BF co-occurrence channel (Harris), and
the small residual is a read-out problem. A faithful BF component can be *correct and redundant*; that is a real,
non-obvious outcome, and it is why chasing "more knowledge here" is the wrong move.

## What I did NOT establish (and would withdraw first if wrong)
- I did NOT prove the taxonomic axis is *worthless* -- oracle{BASE ∪ CM}=0.897 shows real complementary reachable
  coverage IN PRINCIPLE. I claim only that it is NOT the dominant lever and NOT realizable by a learned-from-reading
  channel (or even by circular WordNet's own confidence) CI-separated over grounded+SEQ. I would withdraw any
  "taxonomy is useless" reading; the honest claim is "not dominant, not learnable-to-CI-sep here, read-out-bound."
- The eval is the SimLex/SimVerb-covered subset of the live anchor-pool decision (n=94 / n=338), a faithful
  sample of `canonicalize`'s decision, not a whole-corpus census. The genuinely-rare tail the loop also grounds
  is unmeasured by SimLex (parent W27 caveat inherited).
- The co-hyponym-penalty beta was fixed at 1.0 (CAPTURE AUF 0.5054 <= BASE 0.5063 already, so larger beta only
  down-weights a null-to-negative signal further). I did not exhaustively sweep beta; I would test that first if
  challenged, but the additive-FUSE-hurts + twin-not-beaten + CM-not-CI-sep evidence converges.

## KEY REALIZATIONS (the enabling moves)
- **Recompute the floor in-place against the STRONGEST rep, not the number in the brief.** The whole refutation
  turns on one move: the brief's "grounded floor 0.188" was stale (pre-SEQ). Measuring grounded+SEQ (0.505) on
  the SAME population dissolved the +0.488 "dominant lever" into +0.159-not-CI-sep. This is the `flat_store`
  lesson again: an isolation/pre-baseline number that collapses against the strongest floor.
- **oracle > ceiling is the tell that a channel adds no new reachable coverage.** oracle{grounded+SEQ}=0.744 >
  WordNet-CM 0.650 proves the co-occurrence channel already reaches past the taxonomic ceiling on its own axis;
  the taxonomic "advantage" is confidence, not knowledge. Compute the oracle before concluding a knowledge gap.
- **A symmetric shared-genus bag is a co-hyponym DETECTOR, not an identity discriminator** -- it structurally
  reinforces the very relation confusion it was meant to fix (measured: hurts + twin not beaten). Directionality
  is the missing axis; but even the directed edge, at 100% coverage, is redundant with SEQ.
- **A brain-foundational component can be correct AND redundant.** The "not-working -> upstream-not-BF" heuristic
  has an exception: when an earlier BF channel already captures the signal, a new faithful BF channel adds nothing
  -- the diagnosis is redundancy, not a fidelity gap. Test contribution against the strongest existing rep, not
  against a bare floor.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **Meaning channel / is-a taxonomic identity:** the "is-a is the dominant unbuilt lever" verdict is STALE and
  should be corrected. Against the landed grounded+SEQ representation the taxonomic headroom is +0.159 (n=94, not
  CI-sep) / +0.057 (pooled, not CI-sep); grown-SEQ already supplies the paradigmatic identity signal (SEQ alone
  0.455). Record: the residual over grounded+SEQ is a READ-OUT/confidence gap (oracle 0.744 vs realistic 0.505),
  not a missing knowledge channel; the taxonomic axis is complementary-in-principle (oracle-union 0.897) but
  read-out-bound and not learnable-to-CI-sep from reading.
- `exp_meaning_fusion_isa_knowledge_v1` (built by the parent, previously un-landed): now LANDED as a located
  negative (symmetric shared-genus HURTS, twin not beaten).

## CROSS_SOLUTION_IMPROVEMENT_MAP inputs (owner 2026-09-09)
- **My wall (flagged UPSTREAM component):** the meaning-decision READ-OUT / per-query confidence (metacognition),
  NOT a knowledge channel. The reachable-coverage ceiling of grounded+SEQ is 0.744 (n=94) but realistic is 0.505;
  closing that +0.239 is the real lever, and it is a confidence/selective-prediction problem the parent
  (`measure_end_to_end`) already located-negatived (Path 2). This is a DIFFERENT problem-cluster (read-out), not
  meaning-supply.
- **Inputs my (refuted) channel consumed:** the parser-free grown-SEQ store
  (`reading_grounding_loop.track_directional_context_counts` + `directional_context_lemmas`); grounded ATL
  (`grounded_similarity`); the self-contained Hearst read-edge extractor; SimLex-999 + SimVerb-3500 gold.
- **Reopen trigger:** if a brain-exact per-query reliability / metacognition signal is built that closes the
  BASE read-out gap CI-sep, the taxonomic axis's complementary coverage (oracle-union 0.897) becomes worth
  re-testing as a routed channel -- but only then.

---
## TLDR (plain language)
The system learns what a new word means by matching it to a word it already knows. The brief said the biggest
missing helper is knowing "what kind of thing a word is" (a robin is a bird), and that adding it would take the
system from getting about 15% of these matches right to about 65%. That 65%-vs-15% comparison was made against
an OLD, weak version of the system. In the meantime a different fix already shipped -- letting the system learn
word meanings from the ORDER words appear in as it reads -- and that fix alone already does most of the job. When
I measure the "what kind of thing it is" helper against the CURRENT system instead of the old one, it barely
adds anything: even a perfect dictionary (which we're not allowed to use at read time anyway, and which is
"cheating" on this test) only nudges the score up by an amount too small to be sure it's real, and the
learned-from-reading version I built -- done the careful way the research recommended, and stretched to cover
every test word -- adds exactly nothing and sometimes hurts. The reason is that reading word-order already
teaches the system most of "what kind of thing" a word is; the remaining shortfall is not missing knowledge but
the system being bad at KNOWING WHEN IT'S RIGHT -- a separate problem. So the headline "this is the dominant
missing piece" is wrong against today's system: it was the dominant piece against last month's system, and it's
already largely built.

## QUESTIONS
None blocking. One flag for the strategy session: the priority-1 ranking rested on the +0.488 lever number,
which does not survive the strongest-floor discipline (grounded+SEQ). Suggest re-ranking the meaning cluster
around the READ-OUT/confidence gap instead of a taxonomic-knowledge channel.

## NEXT STEPS
1. **(re-rank, strategy)** The taxonomic-knowledge lever is refuted against grounded+SEQ; the live lever is the
   per-query READ-OUT/confidence gap (0.505 -> oracle 0.744 on n=94). That is a metacognition problem, already a
   parent located-negative -- worth a dedicated brain-exact-reliability problem, not a knowledge channel.
2. **(do NOT redo)** Do not build another learned is-a / shared-genus / Roller-densified channel to lift THIS
   decision: symmetric shared-genus HURTS (twin not beaten); directed edges at 100% coverage add +0.000; even
   circular WordNet is not CI-sep over grounded+SEQ. The ceiling advantage is curation, which is barred at
   inference and unrealizable from reading at feasible volume.
3. **(where is-a MIGHT still pay -- a different task)** is-a's proven wins are on DIRECTIONAL entailment and
   common-noun coref (typed-spoke cells), not on synonym-identity ranking. If the taxonomic axis is pursued, do
   it where directionality is the task, not where grown co-occurrence already suffices.
