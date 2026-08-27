---
priority:
review: EXCELLENT
review_text: "Bar MET (identity win + double dissociation); re-verified FIRST-HAND (scaffold-free witness PASS). The missing ATL amodal CONCEPTUAL/definitional hub is BUILT as a glass-box static asset (WordNet gloss+genus, distinctive-feature IDF-weighted, cosine; NO learning, NO LLM) and beats a STEELMANNED associative competitor (GloVe-300, not the reader's weak 0.04 co-occurrence) on human meaning-IDENTITY off-WordNet: SimLex 0.5210 vs 0.3705 (+0.1505 CI[0.0855,0.2149], CI-sep over GloVe's upper bound), SimVerb 0.4988 vs 0.2199. Info-free twin (shuffled glosses) LOSES (p95 ~0.04-0.065); the distinctive-feature op earns its keep (IDF beats unweighted overlap CI-sep). DOUBLE DISSOCIATION confirmed (conceptual->similarity 0.521>assoc 0.342; GloVe->relatedness; crossover +0.197 CI-sep; GloVe wins WordSim relatedness) -> two systems, each winning its own axis (real-but-partial). ROUTING sub-clause is a RECONCILING NEGATIVE: for decontextualised graded rating FUSION ties/beats demand-routing (reconciles the disk's 'fused>switch'; routing/control's home is context SELECTION = the already-built semantic-control organ). Tested-negative (do not wire): SVD covariance-distillation (ties sparse IDF -> supply-dependent distinctiveness: dense->whiten, sparse->IDF); task-switch gate for rating; grounded SENSORIMOTOR spoke for adjectives (loses CI-sep). DEEPEST FINDING (directional, honestly NOT gating SOLVED): meaning-similarity is OPERATION-SPECIFIC per word class -- one cosine is the wrong operator for adjectives (signed-magnitude) and verbs (relational); adjective op built from OWNED resources lifts 0.585->0.623 with random-axis control losing, CI-separation power-limited at n=111. NO hdlab landed; the conceptual channel + demand-routing + operation-routing-by-word-class QUEUED proven-ready for the consolidation. LAST of the 3 in-flight -> fires the consolidation trigger."
---

> ## SOLVER REVIEW -- EXCELLENT (integrated 2026-08-27 by the strategy session)
> **Re-verified FIRST-HAND, scaffold-free:** strategy ran `verification/test_conceptual_meaning_channel.py` -> PASS.
> Confirmed live: SimLex conceptual 0.5210 vs GloVe 0.3705 (+0.1505 CI[0.0855,0.2149], CI-separated), SimVerb +0.2788,
> shuffled-gloss twin loses (p95 ~0.04-0.065), IDF beats unweighted overlap CI-sep, double dissociation holds (crossover
> CI_lo 0.1140; GloVe wins WordSim relatedness CI_lo 0.0949). **Bar MET** -- the identity clause on an OFF-WordNet human
> gold against a STEELMANNED competitor (the load-bearing choice: beating GloVe, not the reader's 0.04 system, makes the
> win credible), twin losing, plus the double dissociation. **Adversarial audit passed:** the "is it just WordNet
> provenance?" objection is answered three ways (off-WordNet gold; twin losing; a lookup artefact would inflate BOTH golds
> equally, but the representation tracks similarity>relatedness while GloVe does the reverse). Gloss CONTENT alone (zero
> taxonomy) already ties GloVe (0.40), so the win is definitional content, not taxonomy lookup. The ROUTING sub-clause is a
> RECONCILING NEGATIVE, honestly reported: for decontextualised graded rating FUSION ties/beats demand-routing -> the
> brief's "route, fusion hard-failed" is WSD-specific, reconciled with the disk's prior 'fused>switch'; routing/control's
> home is context SELECTION (the already-built semantic-control organ). The solver correctly did NOT let the DIRECTIONAL,
> power-limited (n=111) adjective operation gate SOLVED. **Fidelity boundary earned:** the literature's proposed ATL
> covariance-DISTILLATION does NOT beat sparse IDF -> the distinctive-feature op is SUPPLY-DEPENDENT (dense->whiten,
> sparse->IDF). **Deepest finding (insight, directional):** meaning-similarity is OPERATION-SPECIFIC per word class -- one
> cosine is the wrong operator for adjectives (signed-magnitude) and verbs (relational). **hdlab:** NO file landed (Q111);
> the conceptual/definitional channel (default-off, gated on the held-out SimLex/SimVerb margins) + demand-routing
> (identity->conceptual, relatedness->associative, FUSE for graded rating) + operation-routing-by-word-class is QUEUED
> proven-ready for the consolidation, composing with the semantic-control router. Do NOT wire the tested-negatives (SVD
> distillation; task-switch gate for rating; grounded-sensorimotor for adjectives). AUDIT UPDATE folded (§2b + §6/§7
> meaning entries). **LAST of the 3 in-flight -> the CONSOLIDATION TRIGGER is now MET.**

# PROBLEM: the reader only has an ASSOCIATIVE (word-company / co-occurrence) meaning system -- it is at CHANCE on human "do these two words mean the same thing?", because it lacks the brain's CONCEPTUAL / definitional meaning hub

**slug:** `the_reader_has_no_conceptual_meaning_channel` - **opened:** 2026-08-27 by the strategy session
(the #0 highest-priority next step the just-integrated `context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark`
named -- owner-driven: "the reader is at CHANCE on human meaning-identity (WiC) because it only has the ASSOCIATIVE
co-occurrence system; add the ATL CONCEPTUAL/DEFINITIONAL hub as a SECOND, DEMAND-ROUTED channel, NOT fused").
**status:** OPEN - **the deepest meaning-line gap: the reader's meaning REPRESENTATION itself, not a read-out or a wiring.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1`. Across the whole meaning line -- feature-similarity,
> context-override, semantic control -- the recurring ceiling is the REPRESENTATION: our reader has one meaning system
> (distributional/associative co-occurrence) and is at CHANCE on human meaning-IDENTITY. The brain has TWO (controlled
> semantic cognition: the ATL amodal CONCEPTUAL hub + the distributional/associative system), routed by demand. Building
> the missing conceptual channel is the highest-leverage meaning work; it also gives the just-built semantic-control organ
> a second channel to route between. Re-rank per the owner's direction.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

There are two different ways to "know what a word means." One is knowing what it goes WITH -- "doctor" appears near
"hospital", "nurse", "patient" (word-company / association). The other is knowing what it IS -- a doctor is a person who
is trained to treat illness (a definition, a place in a web of concepts). Our reader only has the first. So when you ask
it the basic question "do these two words mean the same thing?" -- e.g. is a "sofa" a "couch"? -- it is at chance,
because association alone cannot tell "same meaning" from "related but different" (a doctor and a hospital are highly
associated but are not the same thing). The brain keeps BOTH systems and switches between them depending on the task.
This problem builds the missing one: the CONCEPTUAL / definitional meaning channel, as a second system the reader routes
to when the task is about meaning-IDENTITY.

## 2. WHY THIS ONE

- **It is the recurring ceiling of the whole meaning line.** Feature-similarity, context-override, and semantic control
  all bottomed out at the REPRESENTATION: the reader has one meaning system and is at chance on meaning-identity. This
  is the representation itself.
- **The brain-foundational frame is clear and PINNED.** Controlled Semantic Cognition (Lambon Ralph 2017): an amodal ATL
  CONCEPTUAL hub + modality/association systems, with IFG semantic CONTROL routing by demand. We just built the control
  organ; it needs a second channel to route to.
- **It composes what we just built.** The semantic-control conflict-gate (just integrated) is the router; the associative
  co-occurrence system exists; the grounded sensorimotor spoke exists. This adds the missing conceptual hub and the
  demand-routing that CSC predicts (fusion was HARD-FAILED; routing is the faithful design).

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** semantic cognition is CONTROLLED SEMANTIC COGNITION (Lambon Ralph, Jefferies, Patterson 2017): an amodal
ATL CONCEPTUAL HUB (transmodal, captures what a concept IS -- definitional / taxonomic / relational structure; damaged
in semantic dementia) integrating modality-specific spokes (including the grounded sensorimotor one we have), PLUS a
distributional/associative system (temporo-parietal; thematic co-occurrence), with IFG/pMTG SEMANTIC CONTROL selecting
the task-appropriate representation. Meaning-IDENTITY ("same concept?") is a hub/conceptual judgement; thematic relatedness
("go together?") is associative. The systems are ROUTED by task demand, NOT averaged into one score.

**OUR-INVENTION-UNDER-TEST (mark each; sweep don't adopt):** how to instantiate the ATL conceptual hub as a glass-box
STATIC asset (WordNet/dictionary gloss embeddings + hypernym/relational closure, via the project's `definitional_extraction`
-- a static offline-built asset is admissible per the pivot); the DEMAND-ROUTING signal (which channel a task/query
routes to -- can the just-built semantic-control gate do it?); how the conceptual and associative channels stay SEPARATE
(routed) rather than fused. COPY the OPERATION (a second conceptual representation, demand-routed); SWEEP the params.

**Provenance caveat (MIND IT -- the integrated result flagged this):** WiC is partly built from WordNet, so a
WordNet-gloss conceptual representation has an inside-track on WiC's sense boundaries -- an absolute WiC number is
INFLATED by that provenance. The controlled claim must be chance -> above-chance WITH the info-free twin at chance, and
ideally validated on a meaning-identity test NOT derived from the same resource (SimLex similarity vs relatedness; a
held-out synonymy set).

## 4. MEASURED vs INFERRED

**MEASURED (`context_override...` + `the_substrate_has_one_meaning_system...`, integrated):** the reader's co-occurrence
(associative) representation is at CHANCE on human meaning-IDENTITY (WiC balanced accuracy ~0.5); a definitional/
conceptual representation reaches ~0.78 balanced accuracy with the info-free twin at chance -- BUT that 0.78 is inflated
by WiC's WordNet provenance (the controlled claim is chance->above-chance, twin at chance). FUSION of associative +
conceptual HARD-FAILED (a gated combination == a random gate; no gain over the associative specialist) -> the CSC-faithful
design is demand ROUTING, not fusion. The feature-similarity (whitening) read-out + the associative system + the
semantic-control organ are all integrated.

**INFERRED / OPEN (this problem, decisive either way):**
- Does adding the ATL CONCEPTUAL/DEFINITIONAL channel (as a second, demand-routed representation) beat the associative-only
  reader on human meaning-IDENTITY CI-separated, info-free twin (shuffled definitions / scrambled) LOSING -- on a test
  where the conceptual representation does NOT have same-resource provenance inflation?
- Can the just-built SEMANTIC-CONTROL gate perform the DEMAND-ROUTING (route meaning-identity queries to conceptual,
  thematic/selection queries to associative) better than a fixed choice or a fused score?

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT FUSE the two channels into one score -- fusion HARD-FAILED (== a random gate). The faithful design is demand
  ROUTING (task/query picks the channel).
- Do NOT use co-occurrence/associative representation for meaning-IDENTITY -- measured at chance; that is the whole gap.
- Do NOT quote an absolute WiC number as domain-general -- WiC's WordNet provenance inflates a gloss-based conceptual rep;
  report the controlled chance->above-chance-with-twin-at-chance claim + validate off-WordNet where possible.
- Query `experiment_index.py query "definitional"`, `query "conceptual"`, `query "gloss"`, `query "controlled semantic"`;
  read `hdlab/definitional_extraction*` + the two-meaning-systems + context-override SOLVEDs BEFORE building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Locate the project's `definitional_extraction` / gloss machinery + the associative (co-occurrence / Route-B) store +
  the semantic-control organ (the conflict gate from `context_override...`); confirm how to build the conceptual hub as a
  static asset and where the routing gate plugs in.
- Confirm a meaning-IDENTITY test population and (ideally) a second one NOT derived from WordNet; recompute every floor
  (associative-only reader; majority; info-free twin) on each.

## 7. THE BAR

Build the ATL conceptual/definitional meaning channel + a demand-routing mechanism. On a human meaning-IDENTITY task,
floors recomputed on the population:

- **The conceptual channel (demand-routed) must beat the ASSOCIATIVE-ONLY reader on meaning-IDENTITY CI-separated over
  its UPPER bound, with the info-free twin (shuffled definitions / scrambled concept) LOSING CI-separated.** Report CI
  half-width + null p95. Show the conceptual channel is not just same-resource provenance: validate on a test NOT derived
  from WordNet (SimLex similarity-vs-relatedness split, or a held-out synonymy set), and ablate the routing (does
  demand-routing beat a fixed choice and beat the HARD-FAILED fusion?).
- **DECISIVE EITHER WAY:** a win -> the reader needs the two-system conceptual+associative architecture (propose the
  hdlab wiring: the conceptual hub as a static asset + the semantic-control gate as the router). A faithful conceptual
  channel that does NOT beat the associative reader off-WordNet -> a rigorous negative (the associative system + grounding
  is sufficient; the "conceptual" win was provenance), localizing what the second system actually buys.

## 8. FILES AND ENTRY POINTS

- `hdlab/definitional_extraction*` (the gloss/conceptual asset), the associative co-occurrence / Route-B store, the
  semantic-control organ (from `context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark` -- the router),
  `hdlab/grounded_similarity.py` (the sensorimotor spoke), `hdlab/meaning_fusion.py` (note: FUSION hard-failed -- routing).
- The WiC + SemCor + SimLex assets (`tools/load_wsd_benchmarks.py`, `data/wsd_benchmarks/`).
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). **Do NOT write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT fuse the channels (hard-failed); the faithful design is demand ROUTING.
- Do NOT quote an absolute WiC number (WordNet provenance inflation); report the controlled claim + off-WordNet validation.
- No number crosses populations/scorers -- recompute every floor on each meaning-identity population.
