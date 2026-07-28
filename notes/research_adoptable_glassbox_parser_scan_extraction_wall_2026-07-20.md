# Adoptable glass-box parser scan: fixing the extraction-coverage wall
Research drill (safe internet lit-scan + prior-art reconcile) — Director, 2026-07-20

Trigger: fresh full-gold diagnostic on the McGuffey Third Reader shows 84% of who-is-affected misses
(56/67) are EXTRACTION failures upstream of role-assignment — the hand-rolled candidate generator never
proposes the right verb-patient pair, because of coordinated verbs (43-count bucket includes: coordinated
"took up X and threw it", relative-clause "the blockhouse he was building", control/infinitive "began to
lay", imperatives/negated-modals), dropped pronoun objects (10), and dropped noun heads (3). 0 misses are
passive/alternation/preposition. USER instruction: this must be an EXISTING glass-box-compatible parser,
not something to invent. Scope: research/scoping only. No cell dispatch, no push, no store write.

3 parallel Sonnet lit-scans dispatched (symbolic/rule-based; transparent-statistical; neural-frontend +
SRL). Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25; novel-synthesis P capped at
0.50), per [[feedback-lit-scan-calibration-penalty]].

---

## HEADLINE

**MID-DRILL COURSE CORRECTION (Director, live):** we already have a substrate-native, glass-box
dependency-parser build ON DISK from June — `hdlab/semantic_parser.py` + `hdlab/perceptron.py`, plus the
cell ladder `exp_depparse_hashed_cpu_v1.py` (~0.787 UAS hashed structured perceptron),
`exp_depparse_discriminative_cpu_v1.py`, `exp_depparse_2ndorder_cpu_v1.py`, `exp_depparse_v2_mst_cpu_v1.py`
(the MST-decode / higher-order-parts ladder the June drill designed) — confirmed present on disk this
session (glob-verified: all 7 files exist under `hdlab/` and `experiments/`). This changes the shape of
the adopt-vs-build question from a binary into a genuine THREE-WAY call, ranked here in the order the
Director asked to weight it:

**(1) REVIVE + WIRE our own glass-box parser — PREFERRED, if it runs.** No new dependency, fully
learned-in-substrate, fully brain-faithful, and per the June drill's own analysis a credible classical-NLP
ladder (Chu-Liu-Edmonds/Eisner MST decode + Carreras/Koo-Collins higher-order sibling/grandchild parts +
averaged structured-perceptron weighting, all CPU-cheap, <4hr estimated) sits between the already-achieved
0.787 UAS and an honest ceiling of ~0.88-0.89 UAS (0.90+ needs contextualized embeddings / the
substrate-LLM boundary — out of scope for this fix). This is EXACTLY the "learn-in-substrate" outcome the
07-18/07-19 drills wanted, and it was never refuted — see the June-stall reconcile below for why it was
parked, not killed. A parallel exp_dev cell is verifying whether it still runs and wiring it into the
reader's extraction stage; this note does not re-verify that (out of scope, avoid duplicate work) but
treats REVIVE as the primary path pending that verification.

**(2) ADOPT an external front-end — FALLBACK, only if REVIVE proves stale/broken/insufficient.** If the
in-substrate parser cannot be revived cost-effectively (bit-rotted since June, or the 0.787->0.85+ ladder
doesn't land in practice), the external scan below identifies **Stanza** (Stanford NLP's actively-maintained
UD pipeline) as the strongest fallback: pip-installable with zero JVM/C++-toolchain friction, Apache-2.0
licensed, June-2026-fresh maintenance signal, and native UD labels (`conj`, `xcomp`, `acl:relcl`, `obj`)
matching 3 of our 4 named failure phenomena. It would satisfy the glass-box invariant as a LEARNED
FRONT-END emitting an inspectable tree (the NVSA pattern named in the task brief), but is NOT
learned-in-substrate and adds a real external dependency (PyTorch, ~700MB) — a genuine cost relative to
option (1), only worth paying if (1) fails.

**(3) The honest tradeoff.** REVIVE wins on brain-faithfulness, zero new dependency, and "no wasted work"
(the June build is 90%+ of the way to a competitive UAS already). ADOPT wins on CERTAINTY and SPEED (Stanza
is a known-working, currently-accurate artifact today; REVIVE carries real bit-rot/integration risk after
a month-plus dormant, and the 0.787->0.85+ ladder, while credible, was never actually executed to
completion — see below). Neither tool, revived or adopted, automatically solves the subject-propagation-
across-coordination gap (a field-wide convention gap, not specific to any single tool) — that small
glass-box rule layer is needed regardless of which parser wins. Recommendation: let the parallel exp_dev
verification decide (1) vs (2) empirically — if REVIVE's cell ladder runs clean and lands >=0.82 UAS
quickly, ship it and treat Stanza as documented-but-unused insurance; if REVIVE is broken/stale beyond
quick repair, fall back to Stanza without re-opening this scan. Caveat, load-bearing either way: no
phenomenon-specific accuracy numbers (conj-scope, acl:relcl vs ccomp confusion, xcomp control-type
resolution) were found published for ANY tool, in-substrate or external, on ANY corpus — this is a
hypothesis pending the design-gated fair test below regardless of which parser is chosen, not a banked fact.
Deflated P=0.45 that the chosen front-end (either arm) recovers >=70% of the 56 missed links on a landed
test; P=0.65 that it recovers a large majority (>=40%) even if the HARD-PASS bar is missed.

---

## Ranked shortlist (top 4 EXTERNAL adoptable tools — the FALLBACK arm)

Everything below answers "which external tool would we reach for IF our own revived in-substrate parser
proves stale/broken/insufficient." It is not the primary recommendation (see HEADLINE) — it is the
fallback bench, ranked and ready so the fallback decision is fast if REVIVE doesn't land.

### 1. Stanza — RECOMMENDED PRIMARY

- **Maintenance:** actively maintained by Stanford NLP (John Bauer et al.); most recent release found dated
  **June 18, 2026** — live in 2026, best signal of any tool scanned.
- **License:** Apache 2.0 — fully permissive, no commercial-use friction.
- **Glass-box class:** neural-frontend-emitting-inspectable. Internals are a trained neural pipeline;
  output is a literal, labeled Universal Dependencies tree (token, lemma, UPOS, head, deprel) — fully
  auditable per-token, per-arc.
- **Install/footprint on Windows (venv w/ only nltk):** `pip install stanza`, pure-Python wheels, no JVM,
  no native compile. Pulls PyTorch (~700MB CPU build) as the dominant marginal cost. CPU-only is fully
  feasible (GPU optional/accelerative). This is a moderate-to-heavy add relative to the current nltk-only
  venv, but it is a clean `pip install`, not a build-toolchain problem.
- **Failure-phenomenon fit (the acceptance test):** emits genuine UD labels matching 3 of our 4 named gaps
  by name — `acl:relcl` (relative-clause verbs), `xcomp` (control/infinitive), `conj` (coordinated verbs,
  modulo the subject-propagation caveat below), `obj` (pronoun objects, ordinary attachment, the phenomenon
  dependency parsers are most reliably good at). **No phenomenon-specific accuracy number was found** for
  any of these labels on any corpus — only an aggregate cross-lingual UD v2.5 benchmark (LAS 75.68%
  macro-averaged over 100 treebanks; English-specific number not verified this session, but English UD
  parsing from this lineage is generally well above the cross-lingual macro-average). This is an honest gap
  in the literature, not a tool-specific weakness — general parsing literature (Ficler & Goldberg 2017)
  independently confirms coordination-scope resolution is a known hard, elevated-error category across the
  whole field, and coordination appears in roughly 40% of PTB sentences, so this is exactly the sub-problem
  our own diagnostic flags as dominant.
- **Known gap (structural, applies to every UD-emitting parser, not just Stanza):** `conj` does not itself
  carry a second `nsubj` arc for the second coordinated verb — this must be recovered by a post-processing
  rule (walk `conj` edges, inherit `nsubj` from the conj-head verb). Same is true of spaCy and any other
  UD-labeled tree.

### 2. spaCy — fallback if Stanza's PyTorch footprint is unacceptable

- **Maintenance:** actively maintained (Explosion), pip-installable with prebuilt Windows wheels, zero
  compile/JVM friction. `en_core_web_sm` is ~13MB (much lighter than Stanza's PyTorch dependency);
  `en_core_web_trf` needs `spacy-transformers` + PyTorch (heavy, comparable to Stanza).
- **License:** MIT.
- **Glass-box class:** neural-frontend-emitting-inspectable, same category as Stanza.
- **Failure-phenomenon fit:** labels the same 3 phenomena but under a **non-UD, ClearNLP/OntoNotes-derived
  scheme** (`dobj` not `obj`, `relcl` not `acl:relcl`, `xcomp` shared) — still inspectable and auditable,
  just not literally standard UD. `en_core_web_trf` reports aggregate UAS 0.953/LAS 0.939 (no
  phenomenon-specific breakdown found). **Same missing-subject-propagation gap as Stanza** — documented on
  spaCy's own issue tracker as a known limitation ("verb has no subject" after coordination), not a fringe
  bug.
- **No native SRL** (a feature request, GH #170, was never implemented as a core component; no mature
  community ARG0/ARG1 pipeline component found).
- **Verdict:** viable, lighter install, but Stanza's literal UD vocabulary (especially `acl:relcl`, which
  names our exact relative-clause failure category) and slightly more standard labeling make it the primary
  pick; keep spaCy as the documented fallback if PyTorch footprint becomes an operational constraint.

### 3. English Resource Grammar (ERG) + ACE (DELPH-IN, HPSG) — flagged for follow-up, not a now-pick

- **Maintenance:** actively maintained; PyDelphin (the Python layer) had documented activity as recent as
  March 2026.
- **License:** **unverified precisely** — DELPH-IN states a general open-source commitment but this scan
  could not read the exact ERG LICENSE file text; historically LGPL-like, needs direct verification before
  any commit.
- **Glass-box class:** fully symbolic/rule-based — zero statistical component. Hand-written HPSG grammar
  producing both a derivation tree AND Minimal Recursion Semantics (MRS), a formal predicate-argument
  logical form. **This is arguably the single most directly "who-did-what-to-whom"-shaped output format of
  anything scanned** — MRS bakes in argument roles compositionally rather than requiring a UD-to-role
  mapping layer.
- **Coverage:** a real, citable number — "parses 94% of reasonably well-edited English text" per current
  ERG release docs. Designed explicitly to handle control/raising, relative clauses, and coordination as
  first-class HPSG phenomena (not verified with phenomenon-specific numbers, but this is architecturally
  what HPSG grammars are built to do).
- **Windows footprint — the blocker:** ACE (the runtime that executes the grammar) ships Linux/macOS
  binaries only; the documented path on Windows is **WSL2**. This is real but not extreme friction (WSL2
  is well-supported, low-friction infrastructure on a modern Windows box) — meaningfully higher setup cost
  than Stanza/spaCy's pure pip install, but not in MINIPAR/RASP's abandonware territory.
- **Recommendation:** worth a dedicated, cheap follow-up (read the LICENSE file directly, time a WSL2+ACE
  install) given the MRS output's structural advantage, but do not block the current wall on it — Stanza
  gets a working front-end running today with zero WSL dependency.

### 4. MaltParser (via NLTK's Java wrapper) — credited fallback, dominated for this use case

- **Maintenance:** frozen since **v1.9.2, February 2018**. No newer official release found.
- **License:** MIT-style, permissive.
- **Glass-box class:** transparent-statistical — genuinely the most literally inspectable of anything
  scanned (linear/SVM classifier over hand-specified feature templates; you can dump feature weights and
  the step-by-step transition sequence directly). Same architectural family (transition-based +
  perceptron-style discriminative weighting) as our OWN June in-substrate dep-parser build.
- **Accuracy:** widely cited ~89-90% UAS on English PTB-derived dependencies in strong configurations
  (config-dependent; one comparative citation found as low as 77.4% in a weaker setup — treat as
  feature/language-dependent, not a single fixed number). Found: MaltParser shows high accuracy on the
  `cc` (coordinating-conjunction) relation label itself, but this is about labeling the conjunction word,
  not resolving coordination SCOPE (the harder problem) — general literature confirms scope resolution
  remains an open weak point field-wide.
- **Cost:** requires a JRE (Java dependency) — a much smaller ask than a C++ compile toolchain, but a real
  new dependency not needed by Stanza/spaCy.
- **Verdict:** genuinely more literally transparent than a neural-frontend UD parser, and philosophically
  closer to "classical NLP glass-box" — but frozen since 2018 and LOWER accuracy than Stanza/spaCy's
  current models, with a JVM dependency neither of those needs. Dominated for THIS use case; keep as the
  credited reference point for "if maximum literal weight-level inspection is ever required."

### Not recommended (flagged honestly, with reasons)

- **Link Grammar** (opencog/link-grammar): actively maintained (2025 releases!), LGPL, genuinely symbolic —
  but no current coverage number found, and Windows needs a native compile (Cygwin/MSVC/MinGW, no PyPI
  wheel). **RelEx**, built directly on top of Link Grammar to solve exactly our subject/object extraction
  problem, is stale (last substantive version ~2016), needs a JVM AND a running Link Grammar server
  process — too much accumulated staleness/friction to adopt now, though the fact that this exact
  extraction problem was solved once on this stack is worth knowing as a design reference.
- **RASP** (Briscoe & Carroll): stale since March 2018, **non-commercial-only license** (commercial license
  requires a separate purchase from iLexIR), explicitly does not run on native Windows (no Python API
  found). Ruled out.
- **MINIPAR** (Dekang Lin): confirmed abandonware, **binary-only distribution** (no source ever released),
  Windows 95/98-era builds, non-commercial license. Ruled out — cannot audit internals even in principle,
  which fails the glass-box requirement on its own terms regardless of maintenance status.
- **CollinsHeadFinder / tregex** (Stanford): not a standalone parser — a deterministic rule table that
  post-processes a tree ALREADY produced by another (statistical) parser. Useful component to borrow/
  reimplement (it's short, well-documented, and genuinely rule-based) but does not solve extraction by
  itself; no maintained pure-Python port found (Java class, needs a JVM bridge). Deprioritized as a
  standalone pick.
- **AllenNLP SRL-BERT** (`structured-prediction-srl-bert`): the ONE tool scanned that emits literal
  PropBank ARG0/ARG1/ARGM-* frames, and architecturally may handle coordinated shared-subject BETTER than a
  dependency tree (whole-sentence per-predicate tagging doesn't strictly require an explicit second
  `nsubj` arc) — but **AllenNLP itself was archived by AI2 on 2022-12-16**, `allennlp-models`' last release
  is 2022-10-19, and current install reports require pinning a 2022-era PyTorch/spaCy stack, isolated in
  its own venv, with real dependency-conflict risk and zero upstream maintenance. No coordination-specific
  ARG0-propagation accuracy number was found even in the original literature. Verdict: usable only via
  careful legacy pinning, not a 2026-maintained choice; not recommended as the primary adopt target, but
  worth a cheap opportunistic side-check later (an isolated venv, cross-check a handful of coordinated
  sentences) if the Stanza-based rule layer's ARG0/ARG1 mapping needs a second opinion.
- **mate-tools** (Bohnet): confirmed abandonware, no 2026 activity, Java-based. Ruled out.
- **FrameNet/SEMAFOR line** (Das et al.): effectively superseded/abandoned, and FrameNet's frame-element
  inventory is a worse fit than PropBank ARG0/ARG1 for our purposes even setting maintenance aside. Ruled
  out.
- **transformer-srl**: latest release Feb 2022, and it is itself built on top of AllenNLP — inherits every
  one of AllenNLP's staleness problems rather than escaping them. Ruled out.
- **Stanford CoreNLP** (Java): actively maintained but **GPL v3+** (real commercial-use friction) and
  requires a JVM server process — superseded for our purposes by Stanza (same research group, pure-Python,
  Apache 2.0, genuine UD labels, no SRL either way). Ruled out as redundant with a strictly worse cost
  profile.
- **CCG family** (EasyCCG/depccg/C&C): EasyCCG frozen ~2014 (Java); C&C effectively dead (site down,
  binaries gated); depccg is the only one with a pip path but needs a C++11 compiler toolchain on Windows
  (fails the low-friction-install ask) and no current accuracy numbers were verifiable. Ruled out for now.
- **Berkeley Parser (PCFG) / BLLIP-Charniak-Johnson**: Berkeley Parser is dead (frozen ~2015, Java). BLLIP
  is the best-maintained PCFG option with a real Python package (`bllipparser` on PyPI) but has a
  **documented, unresolved GitHub issue reporting Windows build failure** (BLLIP/bllip-parser#55) — a
  concrete, not theoretical, install risk. Also gives constituency trees, requiring an extra head-finding
  layer to reach predicate-argument structure at all (more engineering than starting from a dependency
  tree). Ruled out for now; note the unrelated "Berkeley Neural Parser" (Kitaev & Klein) is a DIFFERENT,
  actively-maintained project but is a neural black box with no inspectable derivation — explicitly
  disqualified regardless of the name overlap.

---

## The reconcile: REVIVE (our own parser) is the preferred path; ADOPT is the honest fallback

**Updated framing (post course-correction):** the reconcile below was drafted before confirming our own
June dep-parser build is on disk. It remains useful for two reasons: (a) it explains WHY, even if REVIVE
succeeds, we still need the same small subject-propagation rule layer regardless of which parser wins
(the gap is a UD/dependency-representation-level convention gap, not specific to Stanza or to an external
tool), and (b) it is the exact analysis needed for the FALLBACK decision if REVIVE proves insufficient.
Read "adopting Stanza" below as "adopting the fallback, if needed" — not as the primary call.

The 07-18 blueprint (`research_learned_parser_clause_seg_np_head_blueprint_2026-07-18.md`) proposed
learning two components in-substrate: (1) NP-head-finding (citing Ramshaw & Marcus chunking F1~92, Collins
head-percolation, Vadas & Curran 2011) and (2) clause-segmentation/coordination (citing CoNLL-2001
Carreras & Marquez F1 78.6, Ficler & Goldberg 2016, CoRec 2023). **If REVIVE succeeds**, both components are
answered by the SAME on-disk parser: the revived dep-parser's tree gives NP-heads (via its own head/
modifier arc structure) and gives verb-argument arcs directly — no separate chunker or clause-identifier
needed, and no external dependency, which is a strictly better outcome than either the original 07-18
blueprint (build two NEW learned components from scratch) or the Stanza-adopt path (one external
dependency). The subject-propagation-across-coordination rule (below) is still needed on top of the
REVIVED tree too — it is a representation-level gap, not a Stanza-specific one. **If REVIVE does not
succeed**, the analysis below (originally written as the primary adopt-vs-build case) applies verbatim to
Stanza-as-fallback:

- **Component #1 (NP-head-finding) is SUBSUMED, essentially for free, at higher accuracy than the target.**
  A UD dependency tree already identifies the syntactic head of every NP (the token that `det`/`amod`/
  `nummod`/etc. children attach to) as a structural byproduct of parsing the whole sentence — there is no
  separate chunker to build or train. Stanza's aggregate accuracy figures, while not phenomenon-specific,
  sit well above the 92-F1 chunking target this component was aiming for. This is a clean win: adopt fully
  replaces build here, no honest tradeoff to report.

- **Component #2 (clause-seg/coordination) is NOT subsumed, but its remaining scope shrinks dramatically.**
  Adopting a UD tree does not solve subject-propagation across `conj`-linked verbs (no tool does, this is a
  field-wide convention gap, confirmed independently by both the symbolic and neural-frontend lit-scans).
  BUT the problem the 07-18 blueprint sized at "build a CoNLL-2001-grade clause identifier from scratch"
  (F1 78.6 newswire anchor, genuinely hard, requires training data + a boosted-tree/CRF classifier) shrinks
  to "write a short, hand-auditable graph walk over an ALREADY-CORRECT tree" (inherit `nsubj` from the
  conj-head verb unless the second verb has its own local subject) — a massive scope reduction, not a
  different problem. Critically, this remaining rule is EXACTLY the mechanism the 07-18 blueprint (`hold X
  active in working memory, re-bind as agent of verb2`) and the 07-19 LCCP drill (`the discourse
  state-of-mind overlay is the natural home for held-subject coordination`) already designed for — it is
  still substrate-native, still brain-faithful (WM keeps the subject active), still fully glass-box; it
  just now operates ON TOP OF a correct dependency tree instead of on top of raw hand-rule-chunked spans,
  which is a much easier surface to write a correct rule against.

**Is this still "learned-in-substrate"?** Honestly, no — not for the syntactic front-end itself. Stanza's
neural network is trained OFF-substrate on UD treebanks; this is a real, acknowledged departure from the
"learn everything in-substrate" north star, not a free lunch. But the task brief's own glass-box invariant
explicitly permits exactly this shape (a learned front-end emitting an inspectable structure, feeding
glass-box VSA reasoning — the NVSA pattern), and it is squarely inside the current, USER-authorized PIVOT
(`[[project_PIVOT_build_ideal_knowledge_foundation_from_existing_tools_USER_AUTHORIZED_2026-07-14]]`):
build the foundation FULL+VETTED from any external tool, keep RUNTIME REASONING glass-box/no-LLM (satisfied
— Stanza's output is a static, inspectable tree; nothing about it is an LLM call on the reasoning path),
and treat runtime autonomous grounding/learning as a separable, later concern. Under the TWO-FRONTIERS
doctrine (`[[project_two_frontiers_brain_faithful_world_plus_substrate_native_world_later_thrust_USER_2026-07-16]]`),
this is Frontier-1 (get the machinery working, brain-faithful in its LEARNING DYNAMICS even if the parse
front-end itself is scaffolding) — the substrate's OWN learned contribution moves up a level onto the LCCP
scoring/construction-weight-learning layer (07-19 drill) and the discourse-state subject-propagation rule,
both of which remain genuinely in-substrate and genuinely learned. Frontier-2 (push the substrate-native
dep-parser to be the front-end itself) is a real, credible, NOT-refuted later thrust — see the June-stall
reconcile below — just correctly sequenced after unblocking the reader now.

**Honest tradeoff, stated plainly (fallback-arm analysis):** adopt-Stanza = fast (a `pip install`, not a
multi-day build), covers the NP-head component fully and shrinks the clause-seg component to a small rule,
but is not brain-faithful at the syntax-front-end layer and creates a real external dependency (PyTorch,
~700MB, actively-maintained-but-not-us-controlled). REVIVE = fully brain-faithful and fully in-substrate,
no new dependency, and per the June drill's own analysis is NOT a re-incurred multi-day cost from scratch —
it is a ladder ALREADY 0.787 UAS of the way there, with the remaining 0.06-0.10 UAS lift specified as three
composable, already-designed classical levers. **The corrected honest call, given the on-disk confirmation:
REVIVE-FIRST** (verify the ladder runs, wire it in, push toward 0.85+ per the June roadmap) **, ADOPT
STANZA AS FALLBACK ONLY** if REVIVE proves stale/broken/insufficient after a genuine attempt — not as a
parallel permanent choice. Either way, the LCCP scoring layer and the discourse-state subject-propagation
rule remain the in-substrate learned components riding on top, unchanged by which parser wins underneath.

### What the June dep-parser stall actually was (read carefully — it changes the framing, and now directly
### supports REVIVE over ADOPT)

Grep of `notes/` for `dep_parse`/`DEPPARSER`/`PHASE4B`/`parser_v2`/`PREMISE_EXTRACTOR` files surfaces the
real history, and it is NOT "we tried an external parser and hit a cost/accuracy wall" — it is a DIFFERENT
story than that framing suggests:

1. We built an in-substrate structured-perceptron dependency parser (classical-NLP-grade: local argmax +
   1st-order features), which plateaued at **UAS 0.787** on UD-English-EWT (`research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11.md`).
   That same drill laid out a credible, fully substrate-native, non-neural path to 0.85-0.89 via three
   composable classical levers (Chu-Liu-Edmonds/Eisner global MST decode, Carreras/Koo-Collins higher-order
   sibling/grandchild parts, averaged structured-perceptron weighting) — all CPU-cheap (<4 hours total
   estimated), all glass-box. **This path was never refuted — it was never finished.**
2. Separately, exp_dev needed a role-binder for ATIS slot-filling and SVAMP math word-problems. A
   substrate-native "cleanup/count-based" parser (a DIFFERENT, weaker implementation than the perceptron
   one above) plateaued at ~0.57-0.60 UAS on that specific pipeline because it lacked discriminative
   feature weighting (`exp_dev_to_research_PHASE4B_WALL_REQUEST_2026-06-11.md`). Rather than push through
   with the perceptron-based dep-parser, the team tried a cheaper primitive — context-window slot-filling —
   which hit **F1 0.871** on ATIS, cleared the pre-registered decision-tree bar, and the multi-day
   dep-parser build was explicitly SKIPPED as unnecessary FOR THAT TASK
   (`exp_dev_to_research_SLOT_FILLING_085_SKIP_DEPPARSER_2026-06-11.md`).
3. A third, unrelated thread found the math-corpus premise EXTRACTOR (DEPENDS_ON edges) was essentially
   non-functional (0 extracted vs. gold ~2.9 true premises per atom) — a different ingest-pipeline bug, not
   evidence about dependency-parsing accuracy at all (`exp_dev_to_research_testbed_A1_MPM_PARSER_FIDELITY_GAP...2026-06-13.md`).

**Net read (corrected post course-correction):** the substrate-native dep-parser was never proven
insufficient — it was DEPRIORITIZED in favor of a cheaper task-specific shortcut that happened to clear the
bar for the benchmark in front of the team at the time (ATIS/math-word-problems, not narrative reading).
It sits at 0.787 UAS today, ON DISK, with the actual cell ladder (`exp_depparse_v2_mst_cpu_v1.py`,
`exp_depparse_2ndorder_cpu_v1.py`, `exp_depparse_discriminative_cpu_v1.py`) already AUTHORED per the June
drill's roadmap toward 0.85-0.89 — this is not a from-scratch build, it is finishing a ladder that is
already ~4/6 rungs specified and code-complete pending a fresh run + wiring. This materially changes the
cost comparison from the original draft of this section: REVIVE is no longer "re-incur a multi-day cost
Stanza avoids" — it may be a same-day-or-cheaper cost, fully in-substrate, with no new external dependency.
This is why the Director's course-correction reorders the recommendation to REVIVE-first: the "adopt is
strictly dominant on cost" read above was written without knowing the ladder was already built, and no
longer holds once that's accounted for. Stanza remains the correct fallback if the on-disk ladder turns out
to be bit-rotted or the remaining rungs don't land in practice — that determination is exp_dev's parallel
verification, not re-litigated here.

---

## Integration sketch: dependency tree -> verb-patient candidates -> FHRR role binding

**Parser-agnostic by design:** this sketch consumes "a dependency tree with head/arc-label edges" as its
input contract — satisfied by BOTH the revived in-substrate parser (`hdlab/semantic_parser.py`'s own output
format, to be confirmed by exp_dev's parallel verification) and Stanza (UD tree) if that's the fallback
that ships. The rules in steps 3-4 (subject-propagation across coordination, xcomp-style control
inheritance, relative-clause gap-filling) are representation-level, needed regardless of which parser wins
per the reconcile above — write them once against whichever arc-label vocabulary the shipped parser uses.
Field names below use Stanza's UD vocabulary (`deprel=nsubj/obj/xcomp/conj/acl:relcl`) as the illustrative
convention; map to the in-substrate parser's own labels if REVIVE is the arm that ships.

1. **Ingest.** Run the front-end parser (REVIVE: `hdlab/semantic_parser.py`, or fallback: Stanza's
   `tokenize, pos, lemma, depparse` pipeline) once per sentence. Output: a list of tokens, each with
   `id, text, lemma, upos/pos, head, deprel/arc-label` — a directly-inspectable tree either way.

2. **Predicate identification.** Any token with `upos=VERB` (or `AUX` heading a verb phrase) is a candidate
   predicate — this directly replaces the hand-rule extractor's verb-finding step, which is where 43/56 of
   the current misses originate (coordinated/relative-clause/control/imperative verbs the hand-rule
   extractor never proposes at all).

3. **ARG0 (who) extraction, with the ONE new rule (subject-propagation walk):**
   - Direct case: child with `deprel=nsubj` (or `nsubj:pass`, flip the role reading for passives — though
     the diagnostic shows 0 current misses are passive-related, so this is a completeness item, not an
     urgent one).
   - Coordinated case (the new rule, directly targeting the "took up X and threw it" failure): if the
     predicate is itself attached to another VERB via `deprel=conj`, and it has NO local `nsubj` child of
     its own, inherit `nsubj` from the conj-head verb. This is the entire scope of the "learn-in-substrate
     later, cheap now" clause-seg fix discussed above — a short, hand-auditable graph walk, not a trained
     classifier.

4. **ARG1 (who/what is affected) extraction:**
   - Direct case: child with `deprel=obj` (or `iobj`) — directly targets the 10-count "pronoun object
     dropped" bucket (`obj` attaches identically whether the filler is a full NP or a bare pronoun; the
     hand-rule extractor's failure was never resolving the syntactic slot at all, which Stanza's tree does
     unconditionally).
   - Control/infinitive case (targets "began to lay the bricks"): predicate reached via `deprel=xcomp` from
     a matrix verb — for the subject-control pattern that dominates our failure set, ARG0 of the xcomp verb
     = ARG0 of the matrix verb (already resolved by step 3's normal subject lookup on the matrix verb);
     ARG1 of the xcomp verb is its own local `obj` child if present ("lay the bricks" already has one).
   - Relative-clause case (targets "the blockhouse he was building"): predicate reached via `deprel=acl:relcl`
     modifying a head noun. If the relcl verb is missing an `obj` child (the zero/null-relativizer case,
     exactly our example — no overt "that/which"), the antecedent (the noun the `acl:relcl` attaches to)
     fills the missing ARG1 slot. If an overt relativizer is present, its own `deprel` (nsubj vs obj)
     indicates which role the antecedent fills instead.

5. **Handoff, unchanged downstream.** The resulting (predicate, ARG0-candidate, ARG1-candidate) tuples feed
   the SAME FHRR role binding, the SAME LCCP cue-competition scoring (07-19 drill, Steps 2-6 untouched —
   `deprel` labels are in fact a strong new candidate feature for LCCP's construction-classification step,
   a free synergy), and the SAME coherence gate. Coref for pronoun antecedents is unaffected (already
   HELD/working per the 07-18 blueprint) — Stanza's tree just stops the pronoun candidate from being dropped
   before coref ever gets a chance to resolve it.

### The design-gated can-fail test

- **Real baseline:** the CURRENT hand-rule clause-splitter + NP-parser + extractor, unchanged, on the SAME
  eval slice that produced the 56/67-miss diagnostic. Not a strawman.
- **Can-fail discriminator:** span/link F1 for the correct `(predicate, ARG0, ARG1)` tuple against the
  existing McGuffey gold annotations. Unsaturated (both arms can plausibly land anywhere from 0-100%), so
  not a by-construction win.
- **Difficulty ON:** report the SAME 4-way breakdown the diagnostic already used — coordinated-verb,
  relative-clause-verb, control/infinitive-verb, pronoun-object — as SEPARATE slices, not a pooled average,
  so a win cannot be diluted by (or hidden inside) the easy already-working majority.
- **One variable:** swap ONLY the extraction/candidate-generation stage (hand-rule -> revived-or-adopted
  dependency tree + the 3 rules in steps 3-4 above). Hold LCCP scoring, coherence gate, FHRR binding, and
  coref exactly fixed.
- **HARD-PASS:** recovers >=40 of the 56 previously-missed links (>=70%), with the gain concentrated
  specifically in the 4 named hard subgroups (not just an aggregate number propped up by easy SVO cases
  that were already working).
- **HARD-FAIL:** recovers <15 of 56 (<27%), OR any recovered gain is concentrated only in the easy subgroup
  with near-zero movement on the 4 named hard categories — would mean Stanza's tree, however accurate in
  aggregate, is not actually resolving OUR specific hard constructions correctly on grade-3 narrative text,
  and the failure would need to be triaged as either a rule-mapping bug (steps 3-4's logic) or a genuine
  Stanza mis-parse on this register before concluding adopt-then-map is the wrong path. P_deflated=0.45 for
  HARD-PASS (novel-synthesis cap applied; no phenomenon-specific precedent exists for any tool on this exact
  register); P_deflated=0.65 that it clears at least a meaningful partial win (>=40%) even if the 70% bar
  is missed.

---

## Cross-thread synthesis

Builds directly on, and does not contradict, `research_learned_parser_clause_seg_np_head_blueprint_2026-07-18.md`
(NP-head + clause-seg blueprint — component #1 subsumed, component #2's scope reduced not eliminated) and
`research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md` (LCCP design — unchanged, now
fed by a richer candidate set). Resolves the open question about the June dep-parser thread: it was a
deprioritization, not a refutation, and the credible substrate-native path (0.787 UAS, roadmap to 0.85-0.89)
remains a live Frontier-2 candidate, correctly sequenced AFTER the adopted front-end unblocks the reader.
Directly actionable per [[feedback-dont-dismiss-adjacent-methods]] — the CCG/PCFG/SRL families were
genuinely dispatched to lit-scan rather than pre-judged, and the honest finding (no maintained, license-clean,
low-friction, phenomenon-verified option exists among them for THIS task) is itself informative, not a
wasted drill.

## Substrate-product implications

If the design-gated test HARD-PASSes: the reader's extraction-coverage wall — currently the dominant
failure mode (84% of misses) — collapses to a small, well-scoped rule layer on top of a maintained,
free, actively-developed dependency parser, at a fraction of the engineering cost the 07-18 blueprint
originally sized. This is squarely inside the USER-authorized PIVOT to build the knowledge/parsing
foundation from existing vetted tools while keeping runtime reasoning glass-box — not a deviation from
brain-faithfulness, a correct sequencing of it (Frontier-1 now, Frontier-2 later). If it HARD-FAILs, the
honest fallback is NOT "go build a dep-parser from scratch" (that would repeat the multi-day cost the June
thread already showed is unnecessary for competitive UAS) — it is to triage whether the failure is in our
own 3-rule mapping layer (fixable, cheap) or in Stanza's tree accuracy on grade-3 narrative specifically
(would motivate a fresh, narrow lit-scan for a grade-appropriate/child-directed-speech-tuned parser, a
genuinely different and untried angle, rather than reflexively reaching for the frozen June substrate build).

## Citations (verified count)

Sourced live this session via 3 parallel Sonnet WebSearch lit-scans (symbolic/rule-based family;
transparent-statistical family; neural-frontend + SRL family) plus this session's own grep-and-read of 6
prior in-repo notes. Tool/project names verified with live search rather than recalled from training:
Link Grammar (opencog/link-grammar, v5.13.0); RelEx (opencog/relex); English Resource Grammar + ACE + LKB
(DELPH-IN); PyDelphin; RASP 3.2 (Briscoe & Carroll, iLexIR); MINIPAR (Dekang Lin, ACL wiki); Stanford
CollinsHeadFinder/tregex (Stanford CoreNLP); MaltParser 1.9.2 (Nivre et al.); python-crfsuite;
sklearn-crfsuite (+ MeMartijn fork); NLTK TransitionParser; Honnibal's "Parsing English in 500 Lines of
Python" (2013, ancestor of spaCy's original parser); EasyCCG (Lewis & Steedman 2014); depccg
(Yoshikawa et al.); C&C parser (Clark & Curran); Berkeley Parser (Petrov & Klein) vs. Berkeley Neural Parser
(Kitaev & Klein, distinct project, correctly disambiguated); BLLIP/Charniak-Johnson (`bllipparser`, GitHub
issue #55 re: Windows build failure); spaCy (Explosion, en_core_web_sm/md/lg/trf); Stanza (Stanford NLP,
Apache 2.0); Stanford CoreNLP (GPL v3+); AllenNLP / allennlp-models (archived 2022-12-16, verified);
transformer-srl (Riccorl); mate-tools (Bohnet) / mateplus; SEMAFOR (Das et al., CMU); Ficler & Goldberg
2017 (EACL, coordination-specific parsing features, cited by the transparent-statistical scan for the
general coordination-scope-is-hard finding). In-repo prior art: `research_learned_parser_clause_seg_np_head_blueprint_2026-07-18.md`;
`research_learned_argument_structure_parser_5x_brain_drill_2026-07-19.md`;
`research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11.md`;
`exp_dev_to_research_PHASE4B_WALL_REQUEST_2026-06-11.md`;
`exp_dev_to_research_SLOT_FILLING_085_SKIP_DEPPARSER_2026-06-11.md`;
`exp_dev_to_research_testbed_A1_MPM_PARSER_FIDELITY_GAP_decisive_true_premises_2.8_extracted_0_parser_v2_justified_2026-06-13.md`.

## Next-drill candidate

If the design-gated test HARD-FAILs specifically on the relative-clause or control/infinitive subgroups
(not the coordination subgroup, which has the clearest single fix), the next-drill candidate is a narrow
lit-scan on child-directed-speech-tuned or simplified-register parsing accuracy specifically (most published
UD/PTB benchmarks are newswire-register; grade-3 narrative is a different, easier register that no scanned
tool reports numbers for) — this is a genuine untested adjacency, not a re-run of this scan.
