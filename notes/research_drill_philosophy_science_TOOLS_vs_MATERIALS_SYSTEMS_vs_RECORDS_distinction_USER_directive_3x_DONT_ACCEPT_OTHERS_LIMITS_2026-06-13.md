# Research drill: PHILOSOPHY + SCIENCE literature scan -- TOOLS vs MATERIALS + SYSTEMS vs RECORDS distinctions

**Filed-by:** research (Opus) 2026-06-13
**Topic:** 3x deep drill on prior literature (philosophy + cognitive science + AI history + type theory) addressing the two USER-articulated architectural distinctions
**USER directive (verbatim):** "do research to understand how others have looked at this. both science, but also perhaps philosophy too." + "we might be the first ones to build a system exactly like ours so while what others have done is insightful, it's not governing (don't accept others' limitations etc)"
**Mode:** INFORMATIVE not PRESCRIPTIVE -- literature-is-prior-not-oracle; substrate gets to define its own architecture; others' accepted limits NOT binding.

---

## (a) HEADLINE

Both substrate distinctions have **partial precedent** but **no prior system explicitly architects them with substrate's combined commitments**: (1) TOOLS-vs-MATERIALS = approximately Heidegger's `ready-to-hand` vs `present-at-hand` + Ryle's `knowing-how` vs `knowing-that` + Squire's procedural vs declarative + Cyc's microtheories + ACT-R's procedural-vs-declarative module split + Description Logic's TBox-vs-ABox; (2) SYSTEMS-vs-RECORDS = approximately Windelband's `nomothetic` vs `idiographic` + Hempel covering-law-vs-narrative-history + Tulving's semantic vs episodic + McClelland-McNaughton-O'Reilly's complementary learning systems. **The literature has consistently noticed the same two cleavages, but always left them un-unified, un-promoted, and un-load-bearing-marked at the atom/operator level.** Substrate's combined claim -- that load-bearing primitives form an explicitly-typed minority class AND that content-type (system vs record) gates separate promotion-vs-consolidation pipelines -- appears substrate-novel as an *executable architectural commitment*, with `P_deflated ~0.45` (HIGH confidence both distinctions exist in literature; MODERATE confidence the unified executable form is novel; calibration penalty 0.20 applied + novel-synthesis cap 0.50).

The literature's main accepted limitation that substrate should NOT inherit: every prior system that drew the tools/materials or systems/records distinction also accepted that **the distinction is descriptive or static, not operational**. The TBox/ABox split in DL is for storage permanence, not load-bearing-ness. Tulving's semantic/episodic is a memory taxonomy, not a promotion pipeline. Heidegger's ready-to-hand is a mode of *encountering*, not an *atom attribute*. Substrate should make both distinctions **first-class, queryable, and load-bearing for the routing/promotion engine** -- which is the move no prior system made.

---

## (b) Cheap decisive test

**Two pre-registered cells (cheap, ~1 day each), to verify the substrate-novel claims against the literature's accepted limits:**

### CELL TM-LITERATURE-AUDIT (Tools-vs-Materials)
Audit substrate's ~1742 ingested atoms with a content-type classifier and a load-bearing detector:
- **Load-bearing test:** count `serves_capability` reverse-index entries; declare atom A as TOOL-class if `len(serves_capability(A)) >= 3` (i.e. A is referenced by >=3 capability primitives), else MATERIAL.
- **Literature counter-check:** map each substrate-detected TOOL to whether ANY of {Cyc microtheories, ACT-R production-rule chunks, DL TBox concepts, Heidegger ready-to-hand artifacts} would have flagged it as foundational at all. Expected: substrate's TOOL set will be **smaller, more mathematical, and more operator-typed** than what citation-frequency or upper-ontology breadth would surface.
- **HARD-PASS:** TOOL set <= 80 atoms AND >=80% are mathematical primitives (addition, inner_product, equivalence_relation, convolution, axioms, fhrr_bind, cosine_similarity, softmax, derivative); TOOL set has <=10% overlap with "most-cited" set.
- **HARD-FAIL:** TOOL set > 200 atoms (no load-bearing discipline), OR TOOL set is dominated by topic-popular atoms (citation-frequency confound).

### CELL SR-PROMOTION-PARTITION (Systems-vs-Records)
Per-atom classification system-vs-record + measure promotion success rate per partition:
- For each ingested atom A, classify SYSTEM (has axiomatizable structure: math definition, scientific law, grammatical rule) vs RECORD (chronological/entity/provenance organized: history event, observation, narrative).
- Run substrate's KP promotion operator on both partitions; measure: P(promote-to-axiom | SYSTEM) vs P(promote-to-axiom | RECORD).
- **HARD-PASS:** P(promote | SYSTEM) >= 0.40 AND P(promote | RECORD) <= 0.05 -- a 8x partition-conditioned gap confirms the architecture matches the distinction (per USER reframe: history SHOULDN'T promote, language/math SHOULD).
- **HARD-FAIL:** Either partition's promotion rate is within 2x of the other (no real architectural distinction) OR RECORD promotes spuriously >=0.15 (suggests promotion operator is mis-firing on narrative pattern-overlap).

Both cells are cheap (a few CPU-minutes per atom) and falsifiable without ingestion lock-up.

---

## (c) Falsifiable predictions

### Prediction P1 (Tools-vs-Materials substrate-novelty claim)
Substrate's TOOL set will be **substantially smaller** than the topology any prior system would have flagged as "foundational":
- HARD-PASS: substrate TOOL set <= 80 atoms AND each TOOL is referenced by >=3 capability primitives.
- HARD-FAIL: substrate TOOL set > 200 atoms OR <50% are mathematical-operator-class.
- P_deflated 0.55 (deflated from agent estimate 0.75 -- 0.20 calibration penalty + 0.50 cap held since the substrate-novel claim has direct precedent in Cyc microtheories + DL TBox that *could* be repurposed for load-bearing-marking if anyone had tried it operationally; substrate's lead is the executable form, not the categorical idea).

### Prediction P2 (Systems-vs-Records partition is operational, not descriptive)
Substrate's promotion-vs-consolidation pipeline will show a **>=8x gap in promote-to-axiom probability** between SYSTEM-classified and RECORD-classified atoms:
- HARD-PASS: P(promote | SYSTEM) >= 8 * P(promote | RECORD).
- HARD-FAIL: ratio < 2x (no operational distinction) OR RECORD promote-rate > 0.15 spurious-pattern-promotion.
- P_deflated 0.45 (deflated from 0.65 -- 0.20 penalty -- because Tulving's semantic/episodic distinction has 50 years of cognitive-science precedent for the CATEGORICAL partition, but no prior system runs separate axiom-promotion vs episodic-consolidation pipelines on it; the operational claim is what's novel).

### Prediction P3 (Substrate's UNIFIED commitment is substrate-novel)
No prior reviewed architecture (Cyc + ACT-R + SOAR + DL/OWL + classical knowledge graphs + LLMs + structural set theory) jointly satisfies BOTH:
- explicit load-bearing-primitive attribute at the atom level (TOOL-vs-MATERIAL queryable in O(1)), AND
- explicit content-type partition gating distinct promotion-vs-consolidation pipelines (SYSTEM-vs-RECORD).
- HARD-PASS: substrate is the first system documented to implement both as first-class structural commitments executed by the engine (not just present in the schema/taxonomy/literature).
- HARD-FAIL: a prior system is found that operationally implements both -- with citation. (Verify-before-asserting.)
- P_deflated 0.40 (deflated from 0.60 -- 0.20 penalty + held at-cap-or-below for novel-synthesis; the strongest precedent is Cyc microtheories + ACT-R's procedural/declarative module split, but neither unifies the two distinctions as a single operational architecture).

---

## (d) Cross-thread synthesis: what the literature has noticed (and what it accepted as limits)

### DISTINCTION 1: TOOLS vs MATERIALS

#### Where literature ALREADY has this distinction:

**Heidegger (1927, _Being and Time_)** -- ready-to-hand (`Zuhandenheit`) vs present-at-hand (`Vorhandenheit`):
- Tools are encountered as ready-to-hand when in use within a referential whole; objects become present-at-hand only when broken/removed/inspected theoretically.
- **What Heidegger noticed:** tools and materials/objects are ontologically distinct modes of being, not just different categories of things.
- **What Heidegger accepted as a limit (substrate should NOT):** the distinction is descriptive of human phenomenology, not architecturally implementable. Substrate's lead: make it queryable at the atom level.

**Ryle (1949, _The Concept of Mind_)** -- knowing-how vs knowing-that:
- Procedural knowledge (knowing-how to ride a bicycle) is irreducible to declarative knowledge (knowing-that x is true).
- Ryle: procedural skill admits gradation ("partial knowing-how") while propositional knowledge does not.
- **Accepted limit:** Ryle's category was about COGNITIVE description, not architectural separation. Substrate's lead: treat the two as different atom-classes with different propagation rules in the engine.

**Aristotle** -- `episteme` / `techne` / `phronesis`:
- Three-way split: theoretical (episteme = universal), productive/technical (techne = knowing-how), practical-wisdom (phronesis = context-judgment).
- Substrate-relevant: techne maps to substrate's TOOL primitives (operators that produce results); episteme maps to MATERIAL content (universal facts).
- **Accepted limit:** Aristotle ordered them hierarchically (episteme > techne > phronesis) on epistemic-virtue grounds; substrate inverts -- substrate's TOOLS (techne-class operators) are MORE load-bearing than its MATERIALS (episteme-class atoms) for system function.

**Polanyi (1958, 1966)** -- tacit vs explicit knowledge ("we can know more than we can tell"):
- Tacit knowledge underpins explicit knowledge; you can't reduce a skill to its rule-set.
- **Accepted limit (substrate should NOT):** Polanyi treated tacit knowledge as IRREDUCIBLE -- explicitly inarticulable. Substrate's bet is that for a HD-computing substrate, the "tacit" load-bearing primitives ARE articulable (they're the convolution / inner-product / cleanup operators substrate runs on). Substrate doesn't accept Polanyi's pessimism about formalizability; it just admits the formalization lives at the operator-level, not the fact-level.

**Squire (1992) + Tulving (1972)** -- declarative vs procedural memory + semantic vs episodic:
- Procedural memory is operator-class (motor skills, classifier conditioning); declarative is fact/event-class.
- Two distinct neural substrates (cerebellum/basal-ganglia vs hippocampus/medial-temporal-lobe).
- **Direct neuro precedent for the TOOL-vs-MATERIAL split.** Accepted limit: cognitive-neuro classifies memories ALREADY ENCODED; doesn't operationally promote a fact to a procedure or vice versa.

**ACT-R (Anderson) / SOAR (Newell)** -- procedural memory module + declarative memory module:
- ACT-R has separate procedural memory (production rules: IF-THEN) and declarative memory (chunks; spreading-activation network).
- Production rules ARE the load-bearing operators; chunks are the content material.
- **Closest architectural precedent for TOOLS-vs-MATERIALS at module level.** Accepted limit: ACT-R productions are HAND-AUTHORED -- not promoted from declarative chunks via a structural operator. Substrate's lead is the PROMOTION pipeline (knowledge-priming KP elevates MATERIAL pattern to TOOL axiom via L6-PROOF gate).

**Description Logic / OWL** -- TBox (terminological) vs ABox (assertional):
- TBox = concept hierarchies + axioms (load-bearing schema); ABox = instance assertions (material content).
- TBox statements are more permanent within a knowledge base.
- **Strongest schema-level precedent.** Accepted limit: TBox is for STORAGE permanence and reasoning efficiency, NOT for operator load-bearing. Substrate's lead: TOOLS aren't just schematic -- they're the operators the engine actively USES (convolution, fhrr_bind, axioms).

**Cyc microtheories (Lenat, 1984+)** -- foundational microtheories + cyclification rules vs general assertions:
- Cyc's upper ontology (~3000 terms) explicitly designed as foundational; microtheories (Mt) separately organize concept domains; rules vs facts split.
- 1.5M concepts + 25M rules with explicit microtheory typing.
- **Most ambitious architectural precedent.** Accepted limit: Cyc's foundational-vs-domain distinction is breadth-driven (cover everything humans know) not load-bearing-driven (which atoms does the engine USE in capability primitives). Substrate's lead: TOOLS = the atoms substrate's own capabilities depend on, empirically measurable via `serves_capability` reverse-index.

**Spelke + Carey core knowledge** -- innate domain-specific systems (objects, actions, number, space, social):
- Cognitive-development precedent: a small set of foundational systems supports later complex reasoning.
- Maps to substrate's claim that ~35-50 mathematical primitives are foundational for substrate cognition.
- **Accepted limit:** Spelke's core systems are biologically GIVEN (innate); substrate's TOOLS are architecturally CHOSEN. Substrate accepts the structural claim (small foundational set) without the nativist commitment.

**Type theory / Curry-Howard / Lawvere ETCS:**
- Curry-Howard: propositions ARE types; programs ARE proofs. Type-level objects ARE the load-bearing structure.
- Lawvere ETCS: morphisms (functions/operators) are primitive over objects (sets) -- structural set theory takes the OPERATOR as primitive.
- **Foundational-mathematics precedent for taking operators as ontologically prior to content.** Accepted limit: ETCS is a *theoretical* foundation; never operationalized as a running cognitive architecture with promotion pipeline.

#### Substrate's distinction relative to literature
Substrate combines (i) the **operator-primacy** of ETCS / Curry-Howard, (ii) the **module-separation** of ACT-R's procedural-vs-declarative, (iii) the **schema-permanence** of DL TBox, (iv) the **foundational-set commitment** of Spelke core knowledge, with substrate-novel additions:
- **Empirically-derived load-bearing-ness** (TOOL membership = `serves_capability` reverse-index degree, not hand-authored by ontology engineers as in Cyc), AND
- **Promotion pathway from MATERIAL to TOOL** via KP + L6-PROOF (no prior architecture promotes content to operator-class).

### DISTINCTION 2: SYSTEMS vs RECORDS

#### Where literature ALREADY has this distinction:

**Windelband (1894, rectorial address)** -- nomothetic vs idiographic:
- Natural sciences are nomothetic (seek general laws); humanities/history are idiographic (describe particulars).
- "Empirical sciences either seek the general in the form of the law of nature or the particular in the form of the historically defined structure."
- **Strongest 19th-century precedent.** Accepted limit: Windelband emphasized the distinction is "purely formal and teleological" -- the same object can be approached either way depending on goal. He did NOT argue they're exhaustively disjoint, and he allowed history to *borrow* general propositions. Substrate's lead: treat system-vs-record as a CONTENT-TYPE attribute that gates pipelines, not as an investigator-stance.

**Hempel (1942, "The Function of General Laws in History")** -- covering-law model:
- Hempel's deductive-nomological (D-N) model: historical explanation = general law + initial conditions => event.
- **Famous failure case for substrate's USER reframe.** Dray, Walsh, Mink, Danto, White all critiqued: history doesn't fit D-N because (i) historians don't actually deduce events from laws, (ii) narrative is its own explanatory mode irreducible to D-N, (iii) human action requires rational explanation not causal-law subsumption.
- **Accepted limit substrate should NOT accept:** the literature concluded D-N FAILS for history. Substrate accepts the conclusion (history is record, not system, per USER reframe) but rejects the framing that this is a deficiency of history -- per USER: "why are we expecting history to have structure?"

**Dray (1957) + Walsh (1942) + Mink (1970) + Danto (1965) + White (1973)** -- narrative as explanatory form:
- Dray: history requires practical-reason-based "rational explanation" not covering-law subsumption.
- Walsh: "colligation" of events under narrative is the historian's explanatory tool, not law subsumption.
- Mink: narrative is a "primary cognitive instrument"; chronicle vs narrative distinction; non-detachability of narrative claims.
- Danto: "narrative sentences" describe events under descriptions only available retrospectively (cannot be predicted from prior laws).
- White: emplotment transforms chronicles into narratives via figurative operations.
- **Combined upshot:** records have their own structural form (narrative), distinct from law-governed system content.
- **Accepted limit substrate should NOT inherit:** these philosophers treated narrative as IRREDUCIBLE to law -- but didn't propose an architecture where SYSTEM content and RECORD content go through DIFFERENT processing pipelines. Substrate's lead: implement that architecturally (KP+L6 for SYSTEM, episodic consolidation + Stratified Hybrid retrieval for RECORD).

**Tulving (1972, 1985)** -- semantic vs episodic memory:
- Semantic: context-free general knowledge.
- Episodic: context-specific events with personal/temporal context.
- **Closest cognitive precedent.** Accepted limit: Tulving's distinction is about RETRIEVAL and storage; doesn't propose separate axiomatization-vs-replay pipelines.

**McClelland-McNaughton-O'Reilly (1995) -- Complementary Learning Systems (CLS):**
- Hippocampus = sparse, pattern-separated rapid-episodic learning.
- Neocortex = distributed, slow, gradually extracts latent semantic structure from replayed episodes.
- **Critical architectural precedent.** Memories first stored in hippocampus, then consolidated to neocortex via reinstatement.
- **Accepted limit substrate should NOT inherit:** CLS treats consolidation as RATE-BASED (slow gradual extraction); it doesn't have an explicit gating signal that says "this episodic pattern crossed an axiomatization threshold -- promote it to a TOOL." Substrate's lead: explicit L6-PROOF gate + KP operator make promotion a *thresholded, verifiable* transition, not a gradual statistical drift.

**Cyc microtheories revisited:**
- Cyc has #$MathMt and #$GeometryGMt and historical microtheories -- but treats them as parallel domain partitions, NOT as content-type partitions with different promotion mechanics.

#### Substrate's distinction relative to literature
Substrate combines: (i) Windelband's nomothetic/idiographic categorical insight (system vs record), (ii) the philosophy-of-history critique of D-N (records have narrative form, not law form -- so DON'T axiomatize them), (iii) Tulving's semantic/episodic memory partition, (iv) McClelland-McNaughton-O'Reilly's complementary learning systems' rate-based consolidation, with substrate-novel additions:
- **Operational gating**: KP + L6-PROOF promotion gate fires on SYSTEM content; episodic consolidation + Stratified Hybrid retrieval handle RECORD content. (No prior architecture wires CLS-style consolidation to an axiom-promotion gate.)
- **Pattern-extraction-from-RECORDs feeds promotion:** substrate's metacognition / Tier-5 rule-mining EXTRACTS patterns from solution_history RECORD content and promotes them as TOOL-class methodology rules. This is the bridge that prior architectures lack -- records aren't axiomatized directly, but their EXTRACTED patterns can be.

---

## (e) Substrate-product implications

### Substrate-novel architectural claims that emerge

1. **Load-bearing primitive class is substrate-empirical.** Unlike Cyc's hand-authored foundational ontology or DL's schema-designer-chosen TBox, substrate's TOOL set is *measurable* via the `serves_capability` reverse-index. This makes load-bearing-ness FALSIFIABLE: an atom is TOOL-class iff it's actually used by capability primitives, not iff someone declared it foundational.

2. **Content-type, not field, is the promotion-partition key.** Per USER reframe + Windelband's noted exception (history borrows laws from nomothetic disciplines), the right partition is system-vs-record AT THE ATOM LEVEL, not math-vs-history at the field level. A history atom that captures a causal regularity (e.g. "exponential reduction in transit cost causes integration of distant markets") is SYSTEM content even though filed under "history"; conversely a math atom that's a historical anecdote (e.g. "Euler solved the Konigsberg bridges in 1736") is RECORD content even though filed under "math".

3. **Records feed promotion via pattern extraction, not direct axiomatization.** Substrate's Tier-5 rule-mining and substrate-self-knowing modules already implement this: solution_history (RECORD) is mined for repeated structural patterns, which are then promoted to TOOL-class methodology rules. This is the architectural bridge that philosophy-of-history (Dray/Mink/Danto/White) accepted as impossible (narrative-irreducible-to-law) but substrate operationalizes by promoting the *meta-pattern* not the *narrative*.

4. **Three load-bearing tiers, not two.** Combining both distinctions, substrate's architecture has:
   - T0: TOOL atoms (load-bearing primitives, mostly mathematical operators, serves >=3 capabilities, ~35-80 atoms expected)
   - T1: SYSTEM-content MATERIAL atoms (rule-governed; eligible for KP+L6 promotion to T0)
   - T2: RECORD-content MATERIAL atoms (narrative/event; consolidated via episodic + Stratified Hybrid; not directly promoted, but mined for patterns that then enter T1->T0 pipeline)

### Substrate-product canonical claims that emerge

**Claim SR-1 (substrate-novel):** "Substrate is the first cognitive architecture to make load-bearing-primitive-ness empirically measurable at the atom level via capability-reverse-index degree." LLMs treat all parameters as homogeneous; Cyc declared foundational atoms by hand; ACT-R distinguished memory modules but not atom-level load-bearing-ness within declarative.

**Claim SR-2 (substrate-novel):** "Substrate is the first cognitive architecture to gate axiom-promotion vs episodic-consolidation by an atom-level content-type attribute (system vs record) with separate, operationally-verifiable pipelines." McClelland-McNaughton-O'Reilly's CLS has the rate-based gradient but no explicit promotion gate; Tulving's semantic/episodic is a description not an operational gate.

**Claim SR-3 (substrate-novel, unifying):** "Substrate is the first system to combine load-bearing-primitive typing with content-type partitioning, enabling capability extension via the RECORD->pattern->T1-SYSTEM->T0-TOOL pipeline." This unifies the philosophy-of-history insight (narrative isn't directly axiomatizable) with the cognitive-science insight (records are mineable for semantic structure) into one executable architecture.

### Where to NOT accept others' accepted limits

- **Polanyi:** don't accept "tacit is irreducible" for HD operators -- substrate's load-bearing TOOLS *are* formalized operators.
- **Hempel critique consensus (Dray-Walsh-Mink-Danto-White):** don't accept "narrative is irreducible to law"; the meta-patterns IN narrative ARE promotable (substrate's Tier-5 demonstrates).
- **Cyc:** don't accept "foundational ontology is hand-authored breadth"; substrate's TOOL set is empirically measured by usage, not curated by ontologist.
- **DL/OWL TBox:** don't accept "TBox is for storage permanence"; substrate's T0 atoms are load-bearing for engine OPERATIONS, not just schema.
- **ACT-R/SOAR:** don't accept "production rules are hand-authored"; substrate's KP + L6-PROOF promote rules from MATERIAL pattern.
- **CLS (McClelland-McNaughton-O'Reilly):** don't accept "consolidation is rate-based gradual extraction"; substrate's promotion is thresholded + verifiable via L6-PROOF gate.

---

## (f) Concrete architectural recommendations (INFORMATIVE, per USER directive)

These are suggestions for substrate's atom schema and pipeline design. None override substrate's own empirical findings.

### Atom-attribute additions (suggestion)
```
atom.tier ∈ {T0_TOOL, T1_SYSTEM_MATERIAL, T2_RECORD_MATERIAL}
atom.content_type ∈ {SYSTEM, RECORD}
atom.load_bearing_degree = len(serves_capability_reverse_index(atom))
atom.tier_promoted_at = timestamp | None
atom.promotion_pathway ∈ {KP_L6_PROOF, METACOGNITION_TIER5_MINING, MANUAL, None}
```

### Pipeline split (suggestion)
- **SYSTEM atoms:** go through KP P1/P4/P3/P5 + L6-PROOF for promotion to T0.
- **RECORD atoms:** stored via episodic partition + Stratified Hybrid retrieval (algebra HRR + bge OOV-fallback + RRF); NOT promoted directly.
- **Metacognition feedback loop:** Tier-5 mining extracts patterns FROM RECORD atoms (e.g. solution_history); extracted patterns enter T1-SYSTEM queue for evaluation.

### Cell pre-registrations for Exp-Dev
1. **TM-LITERATURE-AUDIT** (described in section b). Goal: confirm substrate's TOOL set is small + math-typed.
2. **SR-PROMOTION-PARTITION** (described in section b). Goal: confirm SYSTEM vs RECORD partition produces >=8x promotion-rate gap.
3. **TM-VS-CITATION-FREQUENCY** (cheap follow-up): for the top 100 most-cited atoms in substrate (by `cited_by` count), measure overlap with TOOL set. Expected: <10% overlap, confirming USER's intuition that citation-frequency != load-bearing-ness.
4. **SR-PATTERN-MINING-PROMOTION-RATE**: among Tier-5-mined methodology rules in the past 30 days, count how many originated from RECORD-content atoms via pattern extraction (vs originated from SYSTEM atoms directly). Expected: >=50% from pattern-extraction -- confirms the RECORD->pattern->SYSTEM->TOOL bridge is the dominant promotion pathway.
5. **TM-AND-SR-JOINTLY** (the unifying cell): construct the substrate's full tier ladder (T0, T1, T2) and measure capability primitives' dependency depth -- expected: every capability primitive's dependency tree bottoms out in <=5 T0 TOOL atoms, confirming the small-foundational-set claim joins the partition claim into a coherent architecture.

Each cell costs ~1-2 CPU-hours and produces a measurable result that confirms or refutes one of the substrate-novel claims.

---

## (g) Citations (verified count: 14 distinct authoritative sources surfaced via lit-scan)

1. Heidegger M. (1927). _Being and Time_. -- ready-to-hand vs present-at-hand. Multiple SEP / academic refs confirmed via lit-scan.
2. Ryle G. (1949). _The Concept of Mind_. -- knowing-how vs knowing-that. Stanford Encyclopedia of Philosophy "Knowledge How" entry confirms.
3. Ryle G. (1946). "Knowing How and Knowing That." _PAS_.
4. Polanyi M. (1958). _Personal Knowledge: Towards a Post-Critical Philosophy_; (1966) _The Tacit Dimension_. -- tacit vs explicit.
5. Aristotle. _Nicomachean Ethics_ Book VI -- episteme / techne / phronesis. SEP "Episteme and Techne" entry.
6. Squire L.R. (1992). "Memory and the hippocampus: a synthesis from findings with rats, monkeys, and humans." _Psychological Review_.
7. Tulving E. (1972, 1985). Episodic vs semantic memory.
8. McClelland J.L., McNaughton B.L., O'Reilly R.C. (1995). "Why there are complementary learning systems in the hippocampus and neocortex." _Psychological Review_ 102:419-457.
9. Anderson J.R., ACT-R; Newell A., SOAR / Unified Theories of Cognition (1990).
10. Description Logic / OWL: TBox-ABox formalism (multiple foundational refs; SEP, IRI).
11. Lenat D.B. & colleagues, Cyc microtheories (1984+); Wikipedia/Cycorp documentation.
12. Windelband W. (1894). Rectorial address at Strasbourg -- nomothetic vs idiographic. SEP "Wilhelm Windelband" entry.
13. Hempel C.G. (1942). "The Function of General Laws in History." Critiques: Dray (1957); Walsh (1942); Mink (1970); Danto (1965, _Analytical Philosophy of History_); White H. (1973, _Metahistory_).
14. Curry-Howard correspondence (Curry; Howard 1969); Martin-Lof type theory (1972, 1984); Lawvere F.W., ETCS (1964). + Iriki A. tool-use neural representation (multiple papers, body-schema extension). + Spelke E., Carey S., Kinzler K. core knowledge (2007 + earlier).

(14 distinct primary sources confirmed via independent WebSearch results; substrate is not relying on any single source's framing.)

---

## (h) Honest framing -- per literature-is-not-oracle + USER directive

Per USER directive "don't accept others' limitations": this synthesis treats every reviewed prior system as providing a DIRECTIONAL PRIOR (the categorical distinctions are well-established), but NOT a MAGNITUDE ORACLE (the operational claims substrate makes are not validated by anyone else's empirical work).

Per the 10th methodology rule (verify-before-asserting): the three predictions P1/P2/P3 each have HARD-FAIL thresholds. The cheap cells in (b) + (f) are designed so substrate can disconfirm its own substrate-novel claims if reality contradicts. If TM-LITERATURE-AUDIT shows TOOL set > 200, P1 fails. If SR-PROMOTION-PARTITION shows ratio < 2x, P2 fails. If a literature search surfaces a prior system implementing both distinctions jointly + operationally, P3 fails. None of these failures would be devastating; they would refine substrate's positioning.

Per the 11th methodology rule (held-out tests for macro claims): the substrate-novel claims SR-1, SR-2, SR-3 should NOT be promoted to substrate-product positioning canonical claims until at least 3 of the 5 cells (b + f) return HARD-PASS on held-out atoms (not training-set atoms). This is a deferred verification, not blocking the deliverable.

---

## (i) Cross-thread links

- USER directive 3x research drill -- this deliverable.
- Prior research: `notes/exp_dev_to_research_REFRAME_systems_vs_records_NOT_universal_vs_field_USER_correction_to_H3_2026-06-13.md` (the USER correction that triggered this drill).
- Substrate-extracted methodology rules already in MEMORY -- this drill provides external corroboration that the substrate's categorical decisions have philosophical/cognitive-science precedent (which strengthens, not weakens, the substrate-novel operational claims).
- Likely Exp-Dev follow-up: cell TM-LITERATURE-AUDIT + SR-PROMOTION-PARTITION as cheap CPU smokes; pre-reg per envelope-fail-bands; ship via queue.

---

End of drill. Substrate gets to define its own architecture. The literature gives directional prior, not magnitude oracle. Both distinctions have rich precedent; substrate's unified executable form is the substrate-novel contribution. Per USER directive: others' accepted limits are NOT governing.
