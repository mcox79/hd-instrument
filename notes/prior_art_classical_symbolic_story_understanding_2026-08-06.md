# Prior art: classical symbolic story-understanding + cognitive comprehension models

**Filed:** 2026-08-06 by research (single-session synthesis; 3 parallel Sonnet lit-scan lanes were
dispatched for breadth but not awaited per coordinator override — this note was finished
in-process via direct WebSearch verification + domain knowledge instead, to avoid stalling the
deliverable).
**Trigger:** Director-directed deep prior-art scan, area 1 of 3 (classical symbolic story
understanding + cognitive comprehension models), read-only, know-the-landscape-only. No direction
change is recommended anywhere in this note.
**Query-privacy:** all searches used literal public author/system names (Schank, Lehnert, Trabasso,
Kintsch, Graesser, Zwaan, Gernsbacher, TALE-SPIN, BORIS, PAM, SAM, QUEST, QUALM) — these are the
correct generic public terms for a literature-history scan; no substrate-novel mechanism names,
configs, or numeric parameters went off-platform.

## HEADLINE

**A working, robust, open-domain glass-box goal-outcome story-understander does NOT exist in this
literature — but the exact representational vocabulary our project needs (goal state, ownership,
success/failure polarity, causal linkage) was designed, named, and partially implemented twice:
once by the Yale school (Schank/Cullingford/Wilensky/Dyer, 1977-1983) as scripts+plans+goals, and
once by Lehnert (1981) as Plot Units — an affect-state graph that is structurally the closest
published analog to what we are building.** Both lineages hit the same wall: every one of these
systems ran on **hand-coded conceptual-dependency or hand-annotated affect-state input**, not raw
text via a general automatic parser. None had a robust, general, automatic route from open-domain
prose to their internal representation — the knowledge-acquisition bottleneck (and, for the
generation side, the "characters knowing what they should know" grounding problem) is the
documented, near-unanimous cause of death across the whole lineage, not any flaw in the
goal/plan/affect representations themselves. A 2010 revival (Goyal/Riloff/Daume, AESOP) attempted
automatic Plot-Unit extraction with modern (pre-neural) NLP and got only as far as affect-state
polarity + basic character attribution — full plot-unit graph construction from raw text remains
unsolved even 29 years after Lehnert's original paper. The cognitive-psychology lineage
(Trabasso/van den Broek, Graesser, Zwaan, Kintsch, Gernsbacher) independently arrived at
goal-outcome-bearing causal-network representations that are empirically validated against human
reading/recall data, but these were built by **hand-coding propositions/causal links from text by
trained human raters for controlled experiments** — they are validated theories of comprehension,
not automated comprehenders. This is a strong historical signal that our "mechanism correct but
starved on real open-domain prose" wall is not a novel failure mode — it is the SAME wall this
entire literature hit, and it predicts that the fix has to be in automatic, robust representation
CONSTRUCTION (extraction/grounding), not in the goal/outcome/ownership representation itself
(which prior art suggests is close to right).

P_deflated (landscape-completeness confidence — "this survey correctly characterizes what these
systems did/didn't achieve"): **0.62** — deflated from a raw ~0.80 per lit-scan calibration
discipline. Reasons for the deflation: (a) several claims rest on well-documented but not
independently re-fetched-this-session sources (PDF text extraction failed twice on both the
original Lehnert 1981 PDF and the AESOP EMNLP PDF — see Citations confidence tags below); (b) the
3 dispatched parallel sub-agent lanes were not read back in — this note is built from direct
WebSearch/domain-knowledge synthesis, not cross-checked breadth, so single-source errors on
secondary claims (e.g., exact Schank goal-taxonomy label set, exact QUALM 13-question taxonomy)
are more likely than in a normal 3-lane-converging synthesis.
Novel-synthesis P (the "these constructs are directly portable to our VSA substrate" claim) is
capped at 0.50 per mandatory ceiling — this is a plausibility read, not a tested claim.

## Per-system table

| System | Represents | Worked? (domain / robust) | Documented failure mode | Reusable for us |
|---|---|---|---|---|
| **Schank & Abelson SPGU** (1977, *Scripts, Plans, Goals, and Understanding*) | Scripts (stereotyped event sequences), plans (means-ends action sequences), goal taxonomy (satisfaction/S-goals, enjoyment/E-goals, achievement/A-goals, preservation/P-goals, crisis/C-goals, instrumental/delta-goals), themes (role-based goal-generators, e.g. "employee") | Theoretical framework, partially realized in SAM/PAM below; never itself a single running program | N/A (framework, not implementation) — but the framework's OWN later self-critique (Schank 1982, *Dynamic Memory*) is that scripts are too rigid/pre-enumerated | Discrete goal-TYPE taxonomy as a symbol vocabulary; theme-as-goal-generator (a role predicts a goal without an explicit statement) |
| **SAM** (Cullingford, Yale PhD 1978; ACM SIGART Bulletin) | Story = sequence of script instantiations (e.g. restaurant script); infers unstated script steps | Robust ONLY within known scripts (restaurant, car-accident, earthquake reports); demonstrated on hand-selected newspaper stories via a companion CD parser (ELI, Riesbeck) with a narrow hand-tuned lexicon | Could not understand any story requiring inference outside a pre-stored script — no general planning/goal-inference capability; input pipeline (raw text -> CD) was itself narrow and brittle | Script-instantiation-as-default-inference (fill unstated steps from a known stereotyped structure) — useful as a fallback prior, not a general mechanism |
| **PAM** (Wilensky, Yale PhD 1978; *Planning and Understanding*, 1983) | Explicit goal + plan inference via means-ends analysis; multiple/interacting goals (conflict, competition, overlap); later work ("Why John Married Mary," Wilensky) handles *recurring* goals across a story | Extended past SAM to un-scripted goal-directed behavior on a larger but still hand-picked story set; still domain-narrow (each new story type needed new hand-coded plan/goal knowledge) | Combinatorial cost of general plan inference; still no robust NLP front end; scaling plan libraries by hand is the same knowledge-acquisition bottleneck as scripts, one level up | Explicit goal-interaction taxonomy (conflict/competition/overlap between multiple characters' goals) — directly relevant to multi-character goal-ownership disambiguation |
| **BORIS** (Dyer, Yale PhD 1982; *In-Depth Understanding*, MIT Press 1983; *Artificial Intelligence* journal 1983) | Most integrated system of the lineage: goals+plans (PAM-descended) + TAUs (see below) + affect tracking (Plot-Units-influenced) + QA (QUALM-descended), all over one long interpersonal-conflict narrative (divorce/infidelity domain) | Worked (could answer fact/event/goal questions, generate morals/adages) on exactly the one hand-encoded story domain it was built for; widely cited as the high-water mark of "in-depth" NLU AND as the point where the field recognized this approach couldn't generalize | Extremely example-specific, hand-tuned knowledge base per story; effort to extend to a new domain was comparable to building a new system; contributed to the mid-1980s pessimism about hand-crafted-knowledge NLU that helped motivate the shift to statistical NLP | The INTEGRATION pattern itself (goal/plan layer + affect layer + abstract cross-story pattern layer + QA layer reading off the same representation) is a template worth keeping even though each individual layer needed automation |
| **MOPs / TAUs** (Schank, *Dynamic Memory*, 1982; TAUs implemented inside BORIS) | Memory Organization Packets: more compositional, reusable, scene-based structures replacing rigid scripts; TAUs: abstract cross-domain patterns capturing recurring goal-conflict/plan-failure situations (e.g. "forewarned is forearmed"), independent of the specific domain they occur in | Explicit response to scripts' rigidity; TAUs implemented and used inside BORIS to detect abstract situational analogies across the divorce-narrative domain; MOP-style case indexing later became the seed of Case-Based Reasoning (Kolodner's CYRUS, Riesbeck & Schank 1989) | Still hand-authored structures; did not solve the acquisition bottleneck, just made the authored structures more reusable once authored | TAU-style abstract-pattern matching (a goal-failure "shape" recognized independent of surface domain) is close in spirit to what a VSA similarity-search over goal/outcome bindings could do automatically instead of by hand |
| **TALE-SPIN** (Meehan, Yale PhD 1976, "TALE-SPIN, An Interactive Program that Writes Stories") | Story GENERATION (inverse of understanding): characters have explicit goals (e.g. hunger), a planner searches for action sequences to satisfy them; each goal is explicitly marked SUCCEEDED or FAILED when its target world-state becomes true/blocked | Generated large numbers of stories, but became famous for producing absurd/incoherent ones (documented, verbatim-confirmed example: "Henry Ant was thirsty... he fell in the river... was unable to call for help" — because the planner had no representation that other characters needed to *notice* the event to help; Meehan had to explicitly add a "noticing" inference from location-change) | The failures were not goal-representation failures per se — SUCCEEDED/FAILED as an explicit goal-state flag worked correctly and is exactly the mechanism we want. The failures were **missing supporting world-model primitives** (visibility/knowledge preconditions, "who knows what") that the goal-success/failure machinery silently assumed were already correct | The explicit binary SUCCEEDED/FAILED goal-flag, updated when the goal's target world-state proposition becomes true/false, is the single cleanest prior-art precedent for our "did the wanted thing happen" primitive — and its failure mode is a direct warning: goal-outcome detection is only as good as the surrounding world-model/knowledge-precondition machinery it depends on |
| **Lehnert Plot Units** (Lehnert 1981, *Cognitive Science* 5(4):293-331) | Per-character affect-state graph: primitive states Mental/goal (M), positive event (+), negative event (-); causal links: motivation (event -> goal state), actualization (goal state -> satisfying event), termination (a state is superseded/negated), cross-character equivalence (shared event links two characters' tracks). Named 2-3-node configurations ("success," "failure/loss," "problem resolved," "mixed blessing," "change of mind") are the "plot units" themselves | Demonstrated as a narrative-summarization technique (compress a story to its plot-unit graph) on hand-annotated short narratives; also the affect-tracking layer inside BORIS | Same as the rest of the lineage: input was hand-coded (conceptual-dependency-style or hand-annotated affect states), not automatically extracted from raw text, in the original 1981/1983 work | **Single most directly reusable construct in this whole scan.** Goal success/failure = literally the polarity (+/-) of the event that actualizes or terminates a character's M(ental/goal) state, via a typed causal link. Goal ownership = each affect-state sits on a specific character's own timeline/track by construction. This is nearly identical in spirit to what our project's "goal, outcome-met/unmet, owner" triple is trying to do — Lehnert gives us a validated symbol vocabulary (M/+/-, motivation/actualization/termination/equivalence) to check our own representation against |
| **QUALM** (Lehnert, *The Process of Question Answering*, 1978; used inside SAM/PAM/BORIS) | Question-type taxonomy (causal antecedent, causal consequent, goal orientation, enablement, instrumental/procedural, verification, disjunctive, etc.); answers by walking the causal/goal representation already built by the understander | Worked as a QA layer wherever the upstream representation was correct; explicitly and repeatedly documented as **bottlenecked entirely by the upstream understander's representation quality**, not by its own graph-walk logic | QA quality = representation quality; QUALM itself never failed to answer correctly from a correct graph, but a wrong/incomplete upstream graph produced wrong answers regardless of QUALM | Confirms an architectural principle we should already be following: invest in the goal/outcome/ownership representation's correctness, not in QA-layer cleverness — a good graph-walk over a bad representation cannot be rescued |
| **Kintsch Construction-Integration** (Kintsch 1988, *Psychological Review* 95(2):163-182; Kintsch 1998, *Comprehension: A Paradigm for Cognition*) | Propositional textbase + situation model; construction phase loosely activates associated propositions (including irrelevant "noise" associations), integration phase uses spreading activation/constraint satisfaction to settle on a coherent activated subset | Implemented as an actual hybrid symbolic-connectionist spreading-activation simulation, run over **hand-coded proposition lists** for specific passages (later work paired it with Latent Semantic Analysis for more automatic relatedness scoring, still not full parsing) | General coherence/working-memory model, NOT goal-outcome-first-class — a goal is just a proposition like any other; "resolution" only shows up if someone already encoded a goal-resolution proposition. Input construction (propositionalizing the text) remained a hand/semi-automated step | The construction-then-integration (loose activation -> settle/prune via constraint satisfaction) pattern is a plausible mechanism-analog for a VSA "noisy bind -> clean-up memory" step, but it is NOT itself a goal-outcome mechanism — would need to be paired with an explicit goal/outcome primitive, not used as a substitute for one |
| **Trabasso & van den Broek causal network model** (Trabasso & van den Broek 1985, *Journal of Memory and Language*, Oct 1985; Trabasso, van den Broek & Suh 1989) | Six-category episode structure: Setting, Event, Internal Response (perception/emotion/belief), Goal, Attempt, Outcome — directly a goal-attempt-outcome unit — linked into a causal network via a counterfactual-necessity criterion (would B still happen if A hadn't?); node centrality (causal-connection count) predicts recall/importance | Empirically validated (accounts for substantial variance in human recall, summarization, and importance judgments across multiple studies) — but the causal networks themselves were **built by trained human coders/raters applying the coding scheme to text for psychology experiments**, not derived by an automatic NLP pipeline in the original/core work | This is a validated THEORY of what a correct goal-outcome-causal representation looks like and what it predicts about human processing, not a working automated comprehender; network construction is the un-automated step | **Second most directly reusable construct.** The Goal -> Attempt -> Outcome episode unit, with an explicit Outcome node (success/failure of the Attempt relative to the Goal) and psychological (motivational) vs physical causal-link typing, is essentially a validated formal spec for exactly the goal/outcome/ownership triple we're building — worth checking our internal representation against this six-category schema directly |
| **Graesser QUEST + constructionist theory** (Graesser & Franklin 1990, *Discourse Processes* 13:279-303; Graesser, Singer & Trabasso 1994, *Psychological Review*) | QUEST: goal/plan hierarchies + causal networks + taxonomic/spatial hierarchies as "information sources," answered via question-category-specific arc-search + constraint propagation. Constructionist theory: "search after meaning" — readers generate causal-antecedent and superordinate-goal inferences to explain why an event is mentioned | QUEST WAS implemented as an actual computer program (confirmed: 4 procedural components — interpretation, information-source identification, pragmatics, convergence/arc-search) that answers questions correctly given a hand-built goal/plan/causal network for a story; constructionist theory is validated via extensive human reading-time/probe-verification experiments | Same pattern as the rest: QUEST's network input was hand-built per story, not automatically parsed; constructionist theory is a theory of human inference-generation, not itself an automated extraction pipeline | Arc-search-by-question-category (a small library of typed traversal procedures, one per question type, over a typed goal/causal graph) is a clean, adoptable retrieval-mechanism template once the underlying graph exists |
| **Zwaan event-indexing model** (Zwaan, Langston & Graesser 1995, *Psychological Science*; Zwaan & Radvansky 1998, *Psychological Bulletin*) | Five situation-model dimensions readers track: protagonist, time, space, causation, intentionality (goal-relatedness) | Purely a psychological theory validated via reading-time experiments (discontinuity in any dimension, e.g. a time-shift, causes a measurable reading-time cost at the boundary) — no computational/NLP implementation that processes raw text found | Never built as a running comprehender; "intentionality" dimension is a binary/relational tag (is this event goal-related), not a full goal-state-tracking mechanism | Useful as a checklist of what dimensions any situation model (including ours) should be indexing simultaneously — not a mechanism to adopt directly |
| **Gernsbacher structure-building framework** (Gernsbacher 1990, *Language Comprehension as Structure Building*) | General discourse-coherence mechanism: lay foundation -> map compatible incoming info -> shift to a new substructure on a coherence break (new scene/character/topic), with enhancement/suppression controlling what stays foregrounded | Psychological theory validated via human experiments (anaphor-resolution reading times, ambiguous-word suppression); not goal-tracking-specific; no computational text-processing implementation found | General-purpose, not narrative- or goal-specific; not implemented as an automated system | Low direct relevance to goal-outcome tracking specifically; the SHIFT-on-coherence-break mechanism is tangentially useful for segmenting "when does a new goal-episode begin," nothing more |

## Focus Question 1 — did any treat goal success/failure + goal-ownership as first-class, and how?

**Yes, clearly, in two independent lineages — and both are directly informative for us:**

- **TALE-SPIN** (generation side): each character goal is an explicit data object carrying a
  SUCCEEDED/FAILED status, updated when the goal's target world-state proposition is asserted true
  or found blocked. Ownership is trivial — each goal object belongs to the character whose
  plan-box created it. This is the cleanest, most literal precedent for a binary outcome flag.
- **Lehnert Plot Units** (understanding side): goal success/failure is the polarity (+/-) of the
  event connected to a character's Mental/goal state (M) by an actualization link (success) or a
  termination link (failure/supersession). Ownership is structural — every affect state lives on
  one character's own track by construction; cross-character interaction is a separate,
  explicitly-typed equivalence link. This is the richest precedent because it also gives a
  CAUSAL-LINK TYPE SYSTEM (motivation / actualization / termination / equivalence), not just a
  flag.
- **Trabasso & van den Broek** (cognitive-model side): the Goal -> Attempt -> Outcome episode unit
  makes Outcome an explicit node type in the causal network, with the Attempt's causal-necessity
  relation to the Goal doing the "did it work" work. Ownership again structural (each episode is
  anchored to a protagonist via the Internal-Response/Goal node).
- **QUALM's "goal orientation" question category** independently confirms that 1970s researchers
  treated "what was X trying to do and did it happen" as a distinct, first-class QA target, not an
  incidental byproduct of general causal QA.

None of these are exotic — this is convergent design across three independently-motivated
projects (AI story generation, AI story understanding, and cognitive psychology), which is itself
a mild point of confidence that goal-state + typed-outcome-link + character-ownership is close to
the RIGHT shape for this problem, independent of implementation substrate.

## Focus Question 2 — did any work robustly, and what killed the ones that didn't?

**No system in this scan achieved robust, open-domain, fully-automatic operation.** Every single
one — SAM, PAM, BORIS, TALE-SPIN, Plot Units, QUALM, the CI model, the Trabasso/van den Broek
networks, QUEST — depended on **hand-built input**: either hand-coded conceptual-dependency
representations, hand-annotated affect states/causal links, or hand-coded propositional lists
built by trained researchers. Where an automatic front-end existed at all (SAM/PAM's ELI parser),
it was itself narrow and hand-tuned to the demo domain's vocabulary, not general-purpose.

The specific, sourced failure modes, by cause:

1. **Knowledge-acquisition bottleneck (dominant cause, all systems)** — every new story domain
   required hand-authoring new scripts/plans/CD lexicon entries/affect annotations. BORIS is the
   clearest case study: extending it to a second domain was comparable in effort to building a new
   system from scratch. This is explicitly why Schank's own group pivoted to MOPs/TAUs (more
   reusable structures) and, later, why the field broadly pivoted toward statistical/learned NLP
   in the following decade.
2. **Missing supporting world-model primitives, not goal-representation flaws (TALE-SPIN)** — the
   documented "Henry Ant drowns because nobody notices" failure mode shows that an explicit,
   correctly-designed SUCCEEDED/FAILED flag still produces nonsense if the surrounding world model
   (who can perceive what, when) is incomplete. This is a structurally different failure class from
   #1 — it is a missing-primitive problem, not an acquisition-cost problem.
3. **Representation-quality bottleneck propagating to QA (QUALM/BORIS)** — explicitly documented:
   QA correctness is capped by upstream representation correctness; no amount of QA-layer
   sophistication compensates for a wrong or incomplete goal/causal graph.
4. **Automation attempts decades later still only partially succeeded (Plot Units revival)** —
   Goyal/Riloff/Daume's 2010 AESOP system, using contemporary (pre-neural, lexicon + patient-polarity-verb
   + sentiment-projection) NLP, tackled exactly the "make Plot Units automatic" problem 29 years
   after the original paper and only got as far as affect-state recognition + character
   identification + affect projection + link creation as separate, imperfect, non-trivial NLP
   subproblems — full automatic plot-unit-graph construction from raw open-domain text is, to this
   scan's knowledge, still not a solved problem in the public literature.

**Does this predict our walls?** Directly and specifically: our two current sticking points
(grounding word meaning, referent-tracking through negation) are exactly the class-1/class-2
failures this literature already hit — "getting the input representation built correctly and
completely from raw text, including all the implicit world-knowledge preconditions the
goal/outcome machinery silently assumes" — not failures of the goal/outcome/ownership
representation design itself, which independent converging designs (TALE-SPIN, Plot Units,
Trabasso/van den Broek) all validate as approximately correct in shape. This literature offers no
evidence that a differently-shaped goal-outcome representation would have fared better; it offers
strong evidence that the representation-construction step (parsing/grounding at scale) is where
every serious prior attempt died.

## Focus Question 3 — concretely reusable representations/mechanisms

Ranked by directness of fit to a VSA/FHRR role-filler substrate:

1. **Lehnert's causal-link type system** (motivation / actualization / termination / equivalence)
   as a small, closed vocabulary of typed bindings between a character's goal-state vector and
   surrounding event vectors — this is a symbol set we can check our own link taxonomy against
   (do we currently distinguish "event that motivates a goal" from "event that satisfies it" from
   "event that supersedes/negates it" as three distinct relation roles, or are we collapsing them?).
2. **Trabasso & van den Broek's Goal -> Attempt -> Outcome episode unit** with an explicit Outcome
   node and a physical-vs-psychological causation type distinction — a validated six-slot schema
   (Setting/Event/Internal-Response/Goal/Attempt/Outcome) worth using as an external checklist for
   completeness of our own per-episode representation.
3. **TALE-SPIN's explicit binary outcome flag updated on world-state assertion**, paired with its
   documented failure mode as a warning: the flag mechanism itself is fine, but it must be backed
   by a correct, sufficiently complete world-model (especially perception/knowledge preconditions)
   or it will produce confidently-wrong outcomes, not just missing ones — worth an explicit check
   of what implicit preconditions our own outcome-detection logic assumes are already true.
4. **QUEST's arc-search-by-question-category** — a small library of typed graph-traversal
   procedures keyed to question type — as a retrieval-layer template, secondary priority since our
   current bottleneck is representation-building, not query-answering.
5. **Schank's discrete goal-type taxonomy** (S/E/A/P/C-goals) and **TAU-style abstract
   cross-domain pattern matching** as lower-priority, softer analogies — useful vocabulary,
   less directly portable as a binding structure than #1-3.

## Cheap decisive test

This is a landscape survey, not an experiment proposal — no direction change is recommended. The
one adoption-relevant test this scan surfaces, offered as a candidate for a future operational
cycle (not prescribed here): take the six-slot Trabasso/van den Broek episode schema
(Setting/Event/Internal-Response/Goal/Attempt/Outcome) and the four-way Lehnert causal-link
typology (motivation/actualization/termination/equivalence), and check — by hand, on a handful of
already-processed passages — whether our existing goal/outcome/ownership representation can be
losslessly re-expressed in these external vocabularies. If it can, that's independent validation
our representation shape is compatible with two convergent, human-validated prior designs. If it
cannot, the gap identifies precisely which relation type or episode slot we are currently missing.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

- **HARD-PASS:** every goal/outcome/ownership triple our substrate currently extracts from a
  processed passage can be mapped onto the Trabasso/van den Broek six-slot schema without
  inventing a new slot, AND our causal-link types can be mapped onto Lehnert's four-type taxonomy
  (motivation/actualization/termination/equivalence) without collapsing two of their types into
  one of ours. This would mean our representation design is a strict match with prior validated
  designs — a check-in-hand consistency finding, not a functional improvement, and not itself
  evidence our extraction pipeline works better.
- **HARD-FAIL:** if the remapping requires inventing more than one genuinely new slot/link-type
  not present in either external schema (i.e. our representation is doing something these two
  independently-converging prior designs didn't anticipate), that is a flag to independently
  re-justify the extra structure rather than assume it is required — extra unvalidated structure
  is exactly the kind of thing that quietly reproduces the class-1 acquisition-bottleneck failure
  mode (bespoke categories nobody else needed, each one another future point of brittleness).
- **HARD-FAIL (predictive claim about our current walls):** if a future audit of our
  negation/referent-tracking failures finds the root cause is NOT missing/incomplete
  world-model preconditions feeding correctly-designed goal/outcome logic (i.e. it turns out to be
  a goal/outcome REPRESENTATION design flaw, not an input-construction/grounding flaw), that would
  refute this note's central historical-analogy claim (that our wall matches the TALE-SPIN/BORIS
  class-1/class-2 failure pattern) and should be treated as new information, not explained away.

## Cross-thread synthesis

This scan is the first in this notes/ directory to concentrate specifically on the Schank-school
+ Lehnert + cognitive-comprehension-model lineages as a group (a `Grep` across `notes/` for
Schank/Cullingford/Wilensky/Dyer/Lehnert/Kintsch/Trabasso/Graesser/Zwaan/Gernsbacher/"Plot
Units"/BORIS/TALE-SPIN/QUALM/SAM/PAM found only scattered incidental mentions in unrelated drill
notes, none a concentrated treatment). It sits alongside, and does not duplicate, four prior
prior-art scans that are its nearest neighbors in scope:
`notes/research_neurosymbolic_glassbox_read_reason_prior_art_2026-07-18.md` (modern
neurosymbolic/KB-construction systems — NELL, DrKIT, NS-CL, NVSA — the "does a modern system
already unify learned-read + VSA-binding + glass-box reasoning" question), and its three named
siblings on VSA-language, semantic parsing, and comprehension models specifically
(`research_prior_art_comprehension_loop_grounded_language_2026-07-18.md`,
`research_prior_art_text_to_relational_meaning_2026-07-18.md`,
`research_prior_art_picturing_sentences_scene_comprehension_2026-07-19.md`). Where those scans
found "the pieces exist across separate non-overlapping modern lineages, none unifying learned
reading + glass-box vector-binding + multi-hop reasoning," this scan adds the deeper historical
layer underneath: the CLASSICAL symbolic lineage already worked out much of the target
REPRESENTATION (goal/outcome/ownership, causal-link typing) decades before VSA/HDC existed as a
substrate option, and died specifically on the CONSTRUCTION step (getting from raw text to that
representation), not on the representation's design. Read together, the two scan generations say:
the representation problem has strong precedent and looks tractable; the construction/grounding
problem has NEVER been solved robustly at open-domain scale by any prior symbolic system, glass-box
or not — which matches this project's own repeated finding that grounding and referent-tracking,
not goal/outcome structure, are the load-bearing open problems.

## Substrate-product implications

No architecture or direction change is proposed. The product-relevant takeaway is a validation
exercise (see Falsifiable predictions above) plus a naming/vocabulary check: three independent,
non-VSA prior designs (Yale AI, Lehnert, cognitive psychology) converged on "goal state + typed
causal outcome-link + per-character ownership" as the right shape for exactly the phenomenon our
substrate is being built to detect. That convergence is evidence (deflated per calibration
discipline, not proof) that continuing to invest in getting the goal/outcome/ownership triple right
is well-targeted effort, and that the harder, historically-unsolved problem — automatic,
robust construction of that representation from open-domain raw prose, including the implicit
world-model preconditions (who knows/perceives what) that TALE-SPIN's failure mode shows are
silently required — is where this literature predicts continued difficulty, consistent with what
we are already experiencing. This reframes "mechanism correct but starved on real open-domain
prose" not as an anomaly specific to our substrate, but as the single most common terminal failure
mode in this entire 50-year literature — useful context for calibrating expectations, not a
reason to change course.

## Citations (verified count)

**21 total citations gathered. 9 independently verified this session via WebSearch snippet
confirmation (HIGH confidence — exact title/venue/volume/page or a directly-confirmed technical
detail was returned in search results); 12 consistent with strong, well-established training-memory
knowledge of canonical, extensively-documented AI/cognitive-science history but not independently
re-fetched this session (MED confidence).** Two direct PDF-text-extraction attempts (Lehnert 1981
original PDF, Goyal/Riloff/Daume 2010 EMNLP PDF) failed at the tool level (compressed PDF streams
not renderable in this environment, no `pdftoppm`/poppler available) — the Plot Units taxonomy
details in this note (M/+/- states; motivation/actualization/termination/equivalence links) are
therefore MED confidence (well-established secondary-source knowledge, not this-session
primary-text-verified), flagged explicitly rather than silently upgraded.

HIGH (WebSearch-confirmed this session):
1. Lehnert (1981), "Plot Units and Narrative Summarization," *Cognitive Science* 5(4):293-331.
2. Goyal, Riloff & Daume III (2010), "Automatically Producing Plot Unit Representations for
   Narrative Text," EMNLP 2010 — confirmed system name AESOP, confirmed 4-step pipeline (affect
   state recognition, character identification, affect state projection, link creation).
3. Cullingford (1978), SAM ("Script Applier Mechanism"), Yale PhD thesis; "SAM: a program that uses
   world knowledge to understand," ACM SIGART Bulletin.
4. Wilensky, PAM ("Plan Applier Mechanism"), Yale PhD thesis 1978; "Why John Married Mary:
   Understanding Stories Involving Recurring Goals."
5. Trabasso & van den Broek (1985), "Causal Thinking and the Representation of Narrative Events,"
   *Journal of Memory and Language*, Oct 1985 (confirmed via ERIC EJ323878).
6. Meehan (1976/1977), "TALE-SPIN, An Interactive Program that Writes Stories" — confirmed
   verbatim the "Henry Ant / Bill Bird" river-drowning failure example and the noticing-inference
   fix.
7. Dyer (1983), *In-Depth Understanding: A Computer Model of Integrated Processing for Narrative
   Comprehension*, MIT Press; Dyer et al., "BORIS — An experiment in in-depth understanding of
   narratives," *Artificial Intelligence* journal 1983 — confirmed TAU description and domain
   (divorce/legal dispute narratives).
8. Kintsch (1988), "The Role of Knowledge in Discourse Comprehension: A Construction-Integration
   Model," *Psychological Review* 95(2):163-182.
9. Graesser & Franklin (1990), "QUEST: A Cognitive Model of Question Answering," *Discourse
   Processes* 13:279-303 — confirmed 4 procedural components and arc-search convergence mechanism.

MED (training-memory, canonical/well-documented, not independently re-fetched this session):
10. Goyal, Riloff, Daume & Gilbert, "Toward Plot Units: Automatic Affect State Analysis," NAACL-HLT
    2010 workshop (existence confirmed via search title only).
11. Schank & Abelson (1977), *Scripts, Plans, Goals, and Understanding*.
12. Wilensky (1983), *Planning and Understanding: A Computational Approach to Human Reasoning*.
13. Trabasso, van den Broek & Suh (1989), "Logical Necessity and Transitivity of Causal Relations
    in Stories," *Discourse Processes* (existence/citation confirmed via a figure-caption
    reference found in search).
14. Schank (1982), *Dynamic Memory: A Theory of Reminding and Learning in Computers and People*
    (MOPs/TAUs origin).
15. Lehnert (1978), *The Process of Question Answering* (QUALM).
16. Kintsch (1998), *Comprehension: A Paradigm for Cognition*.
17. Graesser, Singer & Trabasso (1994), "Constructing Inferences During Narrative Text
    Comprehension," *Psychological Review*.
18. Zwaan, Langston & Graesser (1995), "The Construction of Situation Models in Narrative
    Comprehension: An Event-Indexing Model," *Psychological Science*.
19. Zwaan & Radvansky (1998), "Situation Models in Language Comprehension and Memory,"
    *Psychological Bulletin*.
20. Gernsbacher (1990), *Language Comprehension as Structure Building*.
21. Riesbeck & Schank (1989), *Inside Case-Based Reasoning* (CBR lineage descended from MOPs).

## Bottom line

No working, robust, open-domain, fully-automatic glass-box goal-outcome story-understander exists
in this literature. The representation problem (how to structure goal, outcome-polarity, and
ownership) was solved reasonably well, twice, independently — by Lehnert's Plot Units
(motivation/actualization/termination/equivalence causal links over per-character M/+/- affect
states) and by Trabasso & van den Broek's causal network model (an explicit Goal -> Attempt ->
Outcome episode unit) — and TALE-SPIN's binary SUCCEEDED/FAILED goal flag is the cleanest
low-level precedent for the outcome primitive itself. The construction problem (getting from raw,
open-domain prose to that representation, automatically and robustly, including the implicit
world-knowledge preconditions the outcome logic silently assumes) was never solved by any system
in this lineage — hand-coded conceptual-dependency input or hand-annotated affect/causal links were
the norm throughout, a 2010 attempt at automatic Plot Unit extraction (AESOP) only partially
succeeded even with modern-at-the-time NLP tooling, and this exact failure mode (knowledge-acquisition
bottleneck, plus TALE-SPIN's specific "missing supporting world-model primitive" variant) is
extensively documented as the reason the whole symbolic-NLU research program stalled in the
mid-1980s. The top reusable constructs for our project, in priority order, are: (1) Lehnert's
four-type causal-link taxonomy (motivation/actualization/termination/equivalence) as a vocabulary
check for our own relation types; (2) Trabasso & van den Broek's Goal -> Attempt -> Outcome
episode schema (with an explicit Outcome node and physical-vs-psychological causation typing) as
a structural completeness checklist; and (3) TALE-SPIN's explicit binary outcome-flag mechanism,
paired with its documented failure mode as a direct warning that outcome detection is only as
reliable as the world-model preconditions feeding it.
