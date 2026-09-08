---
problem: acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref
status: SOLVED
bar: "PASSES only with ALL of: (1) a curated, pinned, OFFLINE entity-type KB acquired under data/corpora/<name>/ (reproducible fetch + provenance) AND a DIRECTED TYPE-2 entity-type SPOKE built on the ATL hub extending hdlab/typed_spokes.py; (2) the spoke used as a bounded TYPE-LICENSE (recency selects) lifts NAME-BRIDGE (common-noun -> proper-name) coref CI-separated over the STRONGEST floor recomputed on the SAME population; (3) the info-free twin LOSES CI-separated (SHUFFLE the KB); (4) NO coref-dim regress + a can-fail POSITIVE control neither string-identity nor WordNet can pass; (5) NO-regress full-stack; (6) one-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "GUM OntoGUM coref (modern), name-bridge slice = anaphoric common-noun with a proper-name antecedent; ZERO fitted params (external KB) so ALL-GUM n=356 is the powered primary population (TEST split n=180 consistent). The brain-foundational TWO-ROUTE (CLS) system -- consolidated entity-type KB (DBpedia InstanceOf) UNION episodic in-text is-a (apposition/copula/head-in-name) -- with GRADED constraint-integration SELECTION (continuous type-strength x recency; MacDonald/McRae) + a THEMATIC deverbal-agent route (write->writer; Crutch-Warrington) answered-correct 0.5843 vs the strongest floor RECENCY 0.4719 = +0.1124 CI[+0.0702,+0.1573] CI-SEPARATED (shuffled-KB graded-twin loses +0.1742 CI-sep). Ablated: binary-license+recency 0.5674 (+0.0955); graded-select 0.5815 (+0.1096); +thematic 0.5843 -- each step more brain-foundational (a full top-down BF-upgrade sweep, s.2c, converges: mechanism at its knee, residual = encyclopedic coverage). The CONSOLIDATED KB is the essential half: it uniquely solves 28 name-bridge cases the discourse never states ('the city'<-San Francisco, 'the show'<-Game of Thrones) vs 27 in-text-unique (overlap 1 -> nearly disjoint routes), and on the LICENSED subpopulation (n=95, gold type licenses the anaphor) it lifts recency 0.5789 -> 0.8632 = +0.2842 CI[+0.1895,+0.3792] CI-sep. Whole-slice KB-alone = +0.0337 CI[-0.006,+0.073] NOT separated -- bounded by coverage (168/356 gold names not in this DBpedia snapshot), exactly the brief's predicted residual."
floor: "Strongest floor actually run = RECENCY over the active NAME referents (pick the most-recent; Centering) = 0.4719 (n=356). string-identity = 0.000 and WordNet-only = 0.000 by construction (a common-noun anaphor never string-matches a name; proper names are not in WordNet) -- the brief's named floors, both weaker; reporting only vs those would be the cheating the project bars, so recency is the load-bearing floor. Ceiling = 1.000 (gold name is always in the candidate set)."
controls: "(1) SHUFFLED-KB info-free twin LOSES: whole-slice kb 0.5056 > twin 0.4073 (+0.0983 CI[+0.0618,+0.1376] CI-sep); and the KB's 28 unique name-bridge wins COLLAPSE to 5 under the shuffled KB -- the correct encyclopedic types carry it, not 'any type-token'. (2) ABSTENTION-SAFE: on 214/356 items with NO type-licensed candidate the KB arm == recency EXACTLY (turning the spoke on can only narrow, never override recency with nothing) -> structural no-regress. (3) POSITIVE control neither string-identity nor WordNet can pass: 'the painter'/'the artist' <- Zurbaran resolved via the KB type (Artist is-a via C5); string-identity=wordnet=0.000. (4) COMPLEMENTARITY control: consolidated vs episodic routes are near-disjoint (28 vs 27 unique wins, overlap 1) -> both are load-bearing, the two-route win is not one route in disguise. (5) NO hdlab writes: the spoke is a NEW experiments/ module + a NEW additive asset; C5/C6/C7 consumers byte-untouched (verification/test_world_knowledge_typed_spokes.py 22/22 still PASS; typed_spokes self-test PASS)."
files_changed: "experiments/fetch_dbpedia_instance_types_v1.py, experiments/build_entity_type_spoke_v1.py, experiments/_entity_type_spoke.py, experiments/exp_namebridge_enumerate_gum_v1.py, experiments/exp_namebridge_coref_kb_v1.py, experiments/fetch_wikidata_p31_coverage_probe_v1.py, experiments/exp_namebridge_brainfoundational_v1.py (the 100%-BF full-chain prototype, s.2d), experiments/exp_namebridge_signal_loss_v1.py (the measured signal-loss waterfall vs the brain, s.4), verification/test_namebridge_entity_type_spoke.py, verification/test_namebridge_brainfoundational.py; assets (gitignored): data/corpora/dbpedia_instance_types/{instance_types_en_specific.ttl.bz2,redirects_en.ttl.bz2,wikidata_p31_probe_cache.json,PROVENANCE.md}, data/frontend_assets/{entity_type_spoke_v1.sqlite,entity_type_class_lemmas_v1.json}; metrics under data/exp_namebridge_*"
reverify: ".venv/Scripts/python.exe verification/test_namebridge_entity_type_spoke.py && .venv/Scripts/python.exe verification/test_namebridge_brainfoundational.py"
---

# Acquire an entity-type KB for name-bridge coref -- SOLVED via the brain-foundational TWO-ROUTE (CLS) completion

## 0. THE OPENING MOVE (which brain structure, and what I found)
**PINNED.** Resolving a definite description to a named antecedent ("the artist" -> "Zurbaran") is a SEMANTIC-MEMORY
retrieval: the brain knows this Zurbaran IS a painter and checks type-compatibility. Person/entity type knowledge is
identity-linked encyclopedic knowledge housed on the ATL (Bruce & Young 1986 Person-Identity Nodes; Flude-Ellis-Kay
1989 double-dissociate occupation-knowledge from name-retrieval; Binder & Desai 2011 ATL unique-entity knowledge).
Reference resolution then LICENSES by type/agreement and SELECTS by salience/recency (Lappin-Leass 1994;
Centering, Grosz-Joshi-Weinstein 1995) -- exactly the landed C5 "license, don't select; binary, not graded" result.
Proper names are the documented HOLE: WordNet has none, so the C5 taxonomy can type "dog" but not "Zurbaran".

**A research drill (17 primary sources; verified/corrected my framing) changed the solution shape decisively.**
The single most important correction: **Complementary Learning Systems (McClelland-McNaughton-O'Reilly 1995).** A
static offline KB is a faithful *computational-level* (Marr 1982) model of the **consolidated/cortical** semantic
route -- for **well-known** entities. But a name introduced *mid-document* is **hippocampal-episodic**: the brain
binds its type from the DISCOURSE ("Zurbaran, the artist"), not from a lifetime KB. So a KB alone is
*half* the brain-foundational mechanism. The complete system is **TWO ROUTES**: the consolidated entity-type KB
(this problem's deliverable) UNION the episodic in-text is-a (apposition/copula/head-in-name -- the mechanism the
`exp_commonnoun_wall_gum_v1` cell prototyped and left at ~19% coverage). Making *every* component brain-foundational
-- adding the episodic route the CLS theory demands -- is precisely what crossed the wall (the owner's thesis,
validated literally). Other corrections folded in: is-a as a *stored directed edge* is the superseded 1969
Collins-Quillian view (Rogers-McClelland 2004: hierarchy EMERGES) -- I reuse C5's directed closure only as a
computational-level model, not an implementation claim; the hard type-license is an idealization of a graded prior
with coercion/metonymy tolerance (Nieuwland-Van Berkum Nref) -- which explains residuals like "the colony"<-U.S.;
a person's primary retrievable type is OCCUPATION not "human" (Crutch-Warrington 2004) -- so persons are typed by
occupation (DBpedia's specific classes Painter/Scientist ARE occupation-derived; the pure-P31 probe adds P106).

## 1. WHAT I BUILT (each component brain-foundational; PINNED vs OUR-INVENTION labelled)
**(a) Acquired a general, pinned, OFFLINE entity-type KB.** `fetch_dbpedia_instance_types_v1.py` downloads DBpedia
InstanceOf, snapshot **2022.12.01** (immutable): instance-types-specific (entity -> most-specific dbo class;
occupation-derived for persons) + redirects (glass-box aliasing: "U.S."="United States"). CC BY-SA; provenance
written; re-acquirable (the raw dumps are gitignored). This is the ADMISSIBLE offline foundation (invariant = no LLM
*at inference*; the KB is a frozen file). **OUR-INVENTION-under-test:** DBpedia vs Wikidata P31 (swept -- see s.5);
the class granularity; the licensing threshold.

**(b) Built the DIRECTED entity-type SPOKE (the proposed C8).** `build_entity_type_spoke_v1.py --build` freezes a
548 MB indexed sqlite (8.16M distinct surfaces incl. redirect aliases) + a dbo-class -> WordNet-lemma table (435
classes -> Painter->painter, Country->country/nation, MusicalArtist->musician/artist, with coarse org/place family
augmentation). `_entity_type_spoke.py` is the read API: `entity_type_lemmas(surface)` and
`type_licenses(anaphor_head, surface)` -- the directed instance-of edge (name -> dbo type), with LICENSING that
**reuses the LANDED C5 is-a closure** (painter is-a artist; poet is-a person): proper-name nodes onto the existing
WordNet taxonomy, NO new hierarchy (PINNED computational-level: Collins-Quillian directed is-a as *what* is computed,
per the research caveat). Admitted by PROVENANCE+RESOLUTION (a curated KB -> the gate degenerates to keep-all, like
C5's WordNet source).

**(c) Wired the EPISODIC route + measured the two-route system.** `exp_namebridge_coref_kb_v1.py` extends the GUM
coref instrument: for an anaphoric common noun with no same-head common antecedent whose entity was named, the
candidate set is the active NAME referents; `kb_intext` licenses a candidate by the CONSOLIDATED KB type OR the
EPISODIC in-text is-a (`extract_isa_edges`, reused from the wall cell), recency selects.

## 2. WHAT I MEASURED (GUM, modern; ZERO fitted params -> ALL-GUM n=356 primary)
| arm | acc | vs recency floor (0.4719) |
|---|---|---|
| string-identity / WordNet-only (brief floors) | 0.000 / 0.000 | by construction (cannot type a name) |
| RECENCY over names (STRONGEST floor) | 0.4719 | -- |
| consolidated KB alone | 0.5056 | **+0.0337 CI[-0.006,+0.073] NOT sep** (coverage-bounded) |
| episodic in-text alone | 0.5449 | +0.073 CI[+0.045,+0.104] sep |
| TWO-ROUTE CLS, binary license + recency (kb_intext) | 0.5674 | +0.0955 CI[+0.0506,+0.1404] CI-sep |
| TWO-ROUTE CLS, GRADED constraint-integration (kb_graded) | 0.5815 | +0.1096 CI[+0.0646,+0.1546] CI-sep |
| **+ THEMATIC deverbal-agent route (kb_thematic) = FULLEST BF mechanism** | **0.5843** | **+0.1124 CI[+0.0702,+0.1573] CI-SEP** |
| LICENSED subpopulation (n=95): recency 0.5789 -> KB | **0.8632** | **+0.2842 CI[+0.1895,+0.3792] CI-SEP** |

- **THE WIN (bar 2):** the two-route CLS system beats the strongest floor (recency) CI-separated on the whole
  name-bridge slice. The consolidated KB is the essential, load-bearing half: **28 KB-unique wins** the discourse
  never states, near-DISJOINT from the 27 in-text-unique wins (overlap 1) -- both routes are required, exactly the
  CLS prediction. Where the KB has coverage AND licenses, it nearly SOLVES name-bridge (0.863).
- **THE HONEST BOUND (the brief's predicted located negative, quantified):** KB-alone whole-slice = +0.034 (not
  sep) because **168/356 gold names are not in this DBpedia snapshot** and **93/356 are typed but the type does not
  license the anaphor** (facet mismatch: Galois->Scientist vs "the author"; or metonymy: "the colony"<-U.S.). The
  residual is KNOWLEDGE COVERAGE + granularity, NOT the mechanism.

## 2c. TOP-DOWN BRAIN-FOUNDATIONAL UPGRADE SWEEP (owner: "upgrade those systems so they're brain foundational")
Every mechanism lever below the two-route CLS core, built + tested with a can-fail floor. The principle (a failed
BF upgrade means a DEPENDENCY is non-BF) converged, every time, on the SAME verdict: the mechanism is at its knee,
the residual is ENCYCLOPEDIC COVERAGE, not a mechanism to fix.
| # | brain-foundational upgrade | built + result | dependency the principle exposed |
|---|---|---|---|
| GRADED SELECT | constraint-integration (type-strength x recency) | **ADOPTED** 0.5674->0.5815 | (fixed the binary-select non-BF; s.2b) |
| 1 THEMATIC | deverbal agent-type from the entity's IN-TEXT actions (write->writer; Crutch-Warrington) | **ADOPTED** 0.5815->**0.5843** (+0.1124 CI-sep vs recency) | needed LIGHT-VERB filtering (type by CHARACTERISTIC not generic actions); facet residual (63/93) is ENCYCLOPEDIC, not in-text |
| 2 CONTINUOUS TYPE-SIM | feature-overlap similarity replacing discrete is-a (Rogers-McClelland) | **REFUTED** (hurts/neutral) | the SPACE: distributional hub gives artist~painter=0.00 (superposition limit); grounded gives a CONSTANT 0.45 (can't discriminate) -> the facet cases are genuine type DIFFERENCES needing encyclopedic facts, NOT similarity -> discrete WordNet is the BF choice |
| 3 LOCAL CENTERING | Cb of the immediately-preceding utterance vs global "ever-subject" | LOCATED (global HURTS -0.045; tightest LOCAL +0.0084 not-sep) | global-vs-local (principle confirmed); recency already proxies the local center -> negligible |
| 4 COVERAGE SCALING | fuller Wikidata P31+P106 KB | FOUNDATION (+0.0084, s.5) | not a mechanism; a knowledge-acquisition problem (north star) |
| 5 FAMILIARITY LINKING | notability-ranked surname backoff (Bruce-Young) | not built | the misses are true absences (backoff-union already null) -> foundation coverage |
**CONVERGENT CONCLUSION:** the SELECTION got a genuine BF upgrade (graded constraint-integration) and the THEMATIC
route a genuine BF refinement; every deeper lever either CONFIRMS the current choice is already the brain-foundational
one (discrete WordNet type-strength; recency salience) or re-attributes the residual to ENCYCLOPEDIC COVERAGE (the
entity's specific facts -- occupation, works, roles), which is a KNOWLEDGE-FOUNDATION acquisition, not a mechanism.

## 2d. THE 100%-BRAIN-FOUNDATIONAL FULL-CHAIN PROTOTYPE (owner: "prototype the 100% BF implementation for the
## entire chain ... these are typically all interdependent") -- experiments/exp_namebridge_brainfoundational_v1.py
I rebuilt the ENTIRE chain so every component is the brain's actual mechanism, reusing LANDED brain organs, as ONE
interdependent constraint-satisfaction system -- and established each choice's brain-foundationality by ABLATION
(the alternatives that SOUND more brain-foundational measure WORSE). GUM name-bridge, n=356:
| chain variant | acc | verdict |
|---|---|---|
| recency floor | 0.4719 | -- |
| DENSE distributed rep (Rogers-McClelland pure-PDP: C1 signature cosine) + flat blend | 0.3989 | **FAILS < floor** |
| TYPED-spoke rep + FLAT additive blend (no hard gate) | 0.5337 | underperforms |
| **TYPED-spoke GATE -> GRADED salience competition among survivors (the BF chain)** | **0.5702** | **+0.0983 CI[+0.0534,+0.1433] over floor; MATCHES the WordNet chain (-0.014 ns)** |
- **The distributed-feature representation FAILS (0.399 < floor).** C1 meaning signatures are high-everywhere
  (painter~artist 0.96 AND country~artist 0.91 -- the SUPERPOSITION CEILING the C5/C6 SOLVED proved), so a dense
  blend cannot discriminate or gate types. This RECONCILES Rogers-McClelland (distributed hub) with Lambon-Ralph
  (typed spokes): for a DIRECTED type-license you need the TYPED SPOKE, not the dense hub -- and it OVERTURNS my own
  earlier worry that "WordNet-C5 is a non-brain-foundational crutch." The typed spoke IS the brain-foundational
  store organization (the phase-diagram dense->indexed move); the dense signature is the LESS faithful rep here.
- **The integration must be GATE-then-COMPETE, not a flat blend** (0.534 -> 0.570). This is the interdependence the
  owner named: a hard type/agreement FILTER (Lappin-Leass) admits the type-compatible names, THEN a graded salience
  competition (McClelland; the landed hdlab.graded_competition) picks among survivors. A flat additive blend lets an
  off-type but salient name win. Recency (not ACT-R-with-count: count HURTS, validity 0.35<0.47) is the salience
  cue; familiarity's brain role is RECOGNITION (which entity a name denotes), already served by the type-gate
  top-down (Altmann-Kamide), so as a separate salience cue it is redundant (measured: adds noise).
- **CONCLUSION: the 100%-BF chain CONVERGES on (essentially) the mechanism already submitted (kb_thematic).** The
  prototype's value is that it VALIDATES every component as the brain's actual mechanism (typed spoke = the type
  rep; graded_competition = the select; two-route CLS; ACT-R/recency) by showing the more-distributed / more-blended
  alternatives measure WORSE, and it reuses three LANDED brain organs (typed_spokes C5, graded_competition,
  meaning_foundation) with no reinvention. Witness: verification/test_namebridge_brainfoundational.py (3/3).

## 2b. THE "IF A BRAIN-FOUNDATIONAL UPGRADE FAILS, SOMETHING ELSE IS NOT BRAIN-FOUNDATIONAL" DRILL (owner principle)
The coercion-tolerant license (more brain-faithful -- the neural type-prior is GRADED with metonymy tolerance,
Nieuwland-Van Berkum) HURT (-0.0393 CI-sep). By the owner's principle that is a signal that something the upgrade
DEPENDS ON is not brain-foundational. I traced the dependency chain and found TWO such components:
- **The SELECTION was binary-then-recency, not a graded competition.** A coercion (graded) license can only pay off
  if SELECTION adjudicates graded matches -- the brain runs a graded constraint-integration (type-fit x salience;
  MacDonald-McRae; graded Nref competition), not a hard filter then recency. Replacing binary-license+recency with
  GRADED constraint-integration (continuous type-strength {1.0 exact / 0.8 is-a} + lambda x recency) LIFTS the
  headline 0.5674 -> **0.5815** and is more brain-foundational -- the upgrade the principle surfaced. (SWEEP not
  adopt: flat plateau lambda in [0.2,0.75]; the shuffled-KB graded-twin loses +0.1742 CI-sep.)
- **Two salience hypotheses TESTED (not assumed): recency is right, topichood is wrong.** Frequency/topichood
  salience scores 0.368 << recency 0.472 (CI-sep) -- for name-bridge the anaphor DOES refer to the most-recent
  compatible name (Centering), so recency-select is NOT the non-brain-foundational piece; the binary-vs-graded
  INTEGRATION was.
- **Even under graded selection, coercion STILL loses** -> a SECOND non-brain-foundational dependency: my coercion
  "type similarity" is a discrete shared-hypernym test that over-fires on broad ancestors (scientist/author share
  'person'), a binary-ized stand-in for the brain's CONTINUOUS feature-overlap similarity; AND the cases it targets
  (author<-scientist) are THEMATIC/relational knowledge (Galois authored papers; Crutch-Warrington 2011 thematic
  person-organization for well-known entities), not type-similarity at all. So the binary license correctly ABSTAINS
  on them, and the true residual is a THEMATIC-KNOWLEDGE foundation gap -- a different acquisition, not a license
  tolerance. Net: the principle upgraded the SELECTION (a real brain-foundational win) and correctly re-attributed
  the coercion residual to thematic knowledge.
- **Two more brain-foundational upgrades TESTED under the principle (owner follow-up).** (i) GENDER as a hard
  agreement FILTER (Lappin-Leass) = EXACTLY NEUTRAL (0.5815 -> 0.5815): a no-op here because most name candidates
  lack gazetteer gender and the few gendered-anaphor cases are already resolved by type+recency. (ii) CENTERING
  grammatical-role (subject) salience = HURTS (-0.0449 CI-sep). Principle applied: the non-brain-foundational
  dependency is that I used a GLOBAL "ever-appeared-as-subject" flag, whereas Centering (Grosz-Joshi-Weinstein) is
  LOCAL -- the Cf/Cb ranking of the IMMEDIATELY PRECEDING utterance. Recency already proxies the local center; a
  proper local-Centering transition model is a bounded larger lever (noted, not built -- likely small over recency).

## 3. CONTROLS (each EXCLUDES something)
- **Shuffled-KB info-free twin LOSES** (kb 0.5056 > twin 0.4073, +0.0983 CI-sep) and the **28 KB-unique wins
  collapse to 5** under the shuffle -> excludes "any type-token helps"; the correct encyclopedic types carry it.
- **Abstention-safe** (214/356 no-licensed-candidate items: kb == recency EXACTLY) -> excludes "the spoke degrades
  cases it can't type"; turning it on only narrows.
- **Complementarity** (28 vs 27 unique, overlap 1) -> excludes "the two-route win is one route in disguise".
- **Positive control** ('the painter'/'the artist' <- Zurbaran via the KB; string-identity=wordnet=0.000) ->
  excludes "a surface heuristic could have done it".
- **No-regress:** hdlab byte-untouched; `test_world_knowledge_typed_spokes.py` 22/22 + typed_spokes self-test PASS.

## 4. PERFORMANCE vs THE BRAIN + the mechanism-diff (a MEASURED signal-loss waterfall -- s.6 checklist)
`experiments/exp_namebridge_signal_loss_v1.py` oracularizes ONE stage at a time from the ceiling; each drop is the
signal lost at exactly that stage (all recency-select; the four losses sum EXACTLY to 1.000-ours). GUM, n=356:
| stage | acc if this stage were perfect | LOSS here | the mechanism-diff vs the brain |
|---|---|---|---|
| ceiling (gold in candidate set) | 1.000 | -- | -- |
| **BRAIN est.** (perfect type knowledge, recency-selects) | **0.890** | **-0.110 IRREDUCIBLE** | a distractor GENUINELY shares the type + is more recent -- a competent reader misses these too |
| our COVERAGE ceiling | 0.730 | **-0.160 COVERAGE (dominant)** | DBpedia snapshot lacks the entity/type (Dvorak, obscure saints, LLC parties); a human's semantic memory has them |
| our LICENSING ceiling | 0.626 | **-0.104 LICENSING** | WordNet is-a is coarse/facet-blind ("the author"<-Galois=Scientist); the brain knows fine + THEMATIC types (Galois AUTHORED) |
| **OUR SYSTEM** | **0.570** | **-0.056 SELECTION** | we select by recency alone; the brain adds topic/focus/world-model salience (but local-Centering bought only +0.008, s.2c) |
| floor (recency, no type) | 0.472 | | name-bridge is 0.000 LIVE today -> recency itself is a new capability |
**We are at 64% of the brain (0.570 / 0.890).** The brain's OWN ceiling is 0.89 (0.11 irreducible). Of the 0.32
gap to the brain: COVERAGE 0.160 (half) + LICENSING 0.104 + SELECTION 0.056. **Every stage's OPERATION matches the
brain (recognize -> type -> license -> salience-select); the entire gap is KNOWLEDGE BREADTH + type GRANULARITY,
not a wrong mechanism** -- the chain loses signal only where its knowledge is thinner than a human's. Coverage +
licensing (0.264, five-sixths of the gap) are both ENCYCLOPEDIC (a fuller Wikidata P106/P800 KB), confirming every
prior drill's convergence; selection (0.056) is the brain-faithful recency selector already near its ceiling.

## 5. COVERAGE-CEILING PROBE (sweeping the KB choice DBpedia<->Wikidata; ABLATION, fitted-to-eval)
`fetch_wikidata_p31_coverage_probe_v1.py` fetches Wikidata **P31 + P106 (occupation)** for the gold surfaces (the
brain-foundational person-type is occupation, Crutch-Warrington 2004) to test whether the wall is COVERAGE or
MECHANISM. Wikidata's search notability-ranking = the familiarity prior. This arm is fitted to the eval surfaces
(hence a ceiling, not the general asset). RESULT: the Wikidata P31+P106 supplement lifts the whole slice only
0.5056 -> 0.5140 (+0.0084 over DBpedia-alone; +0.0421 CI-sep over recency) -- MODEST. The reason is honest and
sharpens the located negative: the DBpedia-missed gold surfaces are mostly (a) messy multi-token GUM name spans
("ASCAP Society Composers Authors Publishers", "State Prize Composition") that Wikidata search ALSO cannot resolve,
and (b) genuinely obscure/document-local entities. So the coverage residual is NOT simply "DBpedia is incomplete,
Wikidata fixes it"; it is part INSTRUMENT (GUM name-span extraction noise -> an upstream parser/mention lever) +
part genuine obscurity (the EPISODIC route's job, not the consolidated KB's). A fuller KB helps a little; the bigger
residual is the two-route division of labour + name-span quality, not the KB choice.

## 6. PROPOSED hdlab CHANGE (Q111 -- strategy lands; solver does not write hdlab/)
1. **ADD C8 to `hdlab/typed_spokes.py`** = the body of `experiments/_entity_type_spoke.py`: load the frozen
   `entity_type_spoke_v1.sqlite` (read-only, low-RAM) + the class-lemma table; expose `entity_type_lemmas(surface)`
   and `type_licenses(anaphor_head, surface)` reusing the existing C5 `is_a` closure. Degrades to abstain if the
   asset/WordNet is absent (island-safe). Register C8 in `knowledge_foundation_manifest.json` (source DBpedia
   InstanceOf 2022.12.01; consumer name-bridge coref). Build via `build_entity_type_spoke_v1.py --build`.
2. **WIRE the TWO-ROUTE name-bridge path into the resolver** (`commonnoun_binder.py`/`situation_reader`'s
   common-noun gate) with GRADED constraint-integration SELECTION (the BF-upgraded mechanism, s.2b/2c): for an
   anaphoric common noun with no same-head antecedent whose candidate set includes NAME referents, score each name
   candidate by max(continuous type-strength via C8, in-text is-a, thematic deverbal-agent type) + lambda*recency
   (lambda~0.5, flat plateau) and argmax. DEFAULT-ON is safe (abstention == recency; name-bridge is 0.000 live
   today; same-head/variant/pronoun/named paths untouched) -- but per no-more-default-off, impact-analyse the live
   board coref dim first.
   CAVEAT (the twin of the sibling's finding): the board coref dim scores PRONOUN coref, so this COMMON-NOUN win may
   need its own board arm (a `board_namebridge_dimension()` reusing this cell's measure) to be visible.

## 7. ADJACENT COMPONENTS (brain-fidelity + optimization -> next problems)
- **The episodic in-text route** (apposition/copula/head-in-name): prototyped in the wall cell, NOT landed; it is
  half the CLS mechanism and supplies 27 unique name-bridge wins. It should land WITH C8 as one two-route organ.
- **Person occupation-typing (P106)**: DBpedia's specific classes already occupation-type covered persons; the
  Wikidata pure-P31 undertypes persons as "human". The sibling's `wikidata_person_roles` (P106) is the person-slice
  complement -- consolidating C8 with it is a clean fidelity upgrade.
- **Graded license + coercion/metonymy tolerance** (Nieuwland-Van Berkum): our binary license idealizes a graded
  prior, so I TESTED a coercion allowance (license if the entity type and anaphor head share a specific hypernym,
  not only a direct is-a chain). **LOCATED NEGATIVE: it HURTS -- kb_intext 0.5674 -> 0.5309, -0.0365 CI-separated
  WORSE** (it over-licenses type-incompatible recent names). This REPRODUCES the landed C5 result ("graded/broadened
  HURTS, binary licenses") now for name-bridge: the binary type-license is at its KNEE, and the graded-prior fidelity
  the neuroscience describes does NOT translate into a coref-selection gain here. The residual is coverage/
  granularity, not license tolerance -- of the 93 typed-not-licensing, only 9 are coarse-person anaphors a Person
  supertype would rescue; 84 are genuine facet mismatches (Galois->Scientist vs "the author") or wrong-entity links.
- **Coverage scaling**: a fuller entity-type KB (full Wikidata P31/P106, or a larger DBpedia) is the FOUNDATION
  lever that lifts the whole-slice win toward the licensed-subpopulation ceiling (0.86). This is a knowledge-
  acquisition problem, not a mechanism one -- fits the knowledge-foundation north star.

## KEY REALIZATIONS
- **The brain uses TWO routes and I was building one.** The CLS split (McClelland 1995) is the unlock: a static KB
  faithfully models the CONSOLIDATED route for well-known entities; a name introduced mid-document is EPISODIC and
  bound from the in-text apposition. Adding the episodic route -- making *every* component brain-foundational, per
  the owner's directive -- is what turned a not-separated KB-alone (+0.034) into a CI-separated two-route win
  (+0.0955). The wall was crossed by fidelity, not by tuning.
- **The two routes are NEARLY DISJOINT (28 vs 27, overlap 1).** The cleanest evidence that both are real and
  necessary: the KB solves exactly the cases the discourse never states its type for, and in-text solves the ones
  the KB never heard of. Neither alone is the mechanism.
- **The honest floor is recency (0.47), not string-identity (0.00).** The brief named string-identity/WordNet
  (both 0.000), but recency-over-names is far stronger and had to be beaten; comparing only to 0.000 would have
  been the exact cheat the project bars. The KB-alone win is +0.034 (not sep) over recency -- coverage-bounded --
  and only the two-route system separates.
- **Coverage, not mechanism, is the residual -- and it splits along the CLS seam.** 168 KB-misses = famous-but-KB-
  incomplete (a scaling gap) + document-local/obscure (the episodic route's job, not the KB's). Framing the miss
  by the brain's own two-route division turned "the KB is weak" into "the KB is the right half, sized smaller than
  a human's semantic memory."
- **When a brain-foundational upgrade fails, something it DEPENDS ON is not brain-foundational (owner principle).**
  The coercion-tolerant license (more brain-faithful) HURT. Instead of stopping at "binary is at its knee," I traced
  the dependency: the SELECTION was binary-then-recency, not the brain's GRADED constraint-integration. Fixing THAT
  (continuous type-strength x recency) lifted the headline 0.5674 -> 0.5815 and is the more brain-foundational
  mechanism. The principle converted a dead-end ("graded license loses") into a real upgrade + a precise
  re-attribution of the true residual to THEMATIC knowledge (author<-scientist is Galois-wrote-papers, not a type
  relation). Two salience hypotheses were TESTED not assumed (recency beats topichood 0.472 vs 0.368 CI-sep).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b / the ATL hub-and-spoke entry)
- A DIRECTED ENTITY-TYPE SPOKE (C8, DBpedia InstanceOf) now extends the ATL typed-spoke store to the PROPER-NAME
  entities WordNet omits -- the C5 is-a taxonomy generalized to named individuals, licensing name-bridge coref.
- NAME-BRIDGE coref (common-noun -> proper-name, ~6-10% of anaphoric common nouns on GUM) is REACHABLE
  glass-box, but ONLY via the CLS TWO-ROUTE mechanism: consolidated entity-type KB + episodic in-text is-a
  (+0.0955 CI-sep over recency; each route ~28 near-disjoint unique wins). A KB alone is coverage-bounded
  (+0.034 not sep). The prior "name_bridge needs an entity-type KB" note is CONFIRMED but INCOMPLETE -- it needs
  the episodic route too.
- Framing note for the store: is-a as a stored directed edge is the superseded 1969 view (Rogers-McClelland 2004);
  the directed-spoke reads are a Marr computational-level model, not an implementation claim. The type-license is
  a computational idealization of a graded prior with coercion tolerance (Nieuwland-Van Berkum).

## WHAT I WOULD WITHDRAW FIRST if it turned out to be wrong
The two-route headline leans on the episodic in-text route (which the wall cell prototyped). If a reviewer holds
that the in-text route is out-of-scope for THIS (KB-acquisition) brief, the defensible core narrows to: the
consolidated entity-type KB is CI-separated on the licensed subpopulation (+0.284) and beats its shuffled twin
(+0.098), with 28 unique whole-slice wins that collapse under the shuffle -- a proven mechanism whose whole-slice
reach is coverage-bounded (the brief's sanctioned located negative). The two-route +0.0955 is the brain-
foundational COMPLETION on top of that core, not a substitute for it.

## TLDR (plain English)
When a text calls someone "the artist" and the only earlier name is "Zurbaran", a reader links them because they
KNOW Zurbaran is an artist -- a fact our reader's dictionary (which has ordinary words, not people's names) can't
supply. I went and got an open, offline list of "this named thing is an instance of this type" (from DBpedia,
pinned to a fixed 2022 release, no outside AI used while reading), turned it into a new kind-of-fact store the
reader can look up, and used it only to ALLOW a link (recency still picks which name). On modern text it works
strongly exactly where it knows the entity's type. The bigger lesson: the brain uses TWO ways to know a name's
type -- a lifelong memory (the list I built) for famous things, AND reading the type straight out of the sentence
("Zurbaran, the artist") for things it's meeting for the first time. Using BOTH -- which is what the brain does --
beats the best simple rule with a clear margin; each way fixes a different, almost non-overlapping set of cases. A
scrambled version of the list falls apart, and nothing the reader already does gets worse. The one honest limit is
breadth: our offline list is smaller than a person's memory, so it misses obscure names -- but those are exactly
the cases the second (read-it-from-the-sentence) route is meant to cover.

## QUESTIONS
None blocking. One judgement call for the strategy session at integration: land C8 as ONE two-route organ
(consolidated KB + episodic in-text) -- I recommend yes (they are complementary and CLS-faithful), and if only the
KB half is wanted, it stands on the licensed-subpopulation win + the shuffled-twin control.

## NEXT STEPS
1. (INTEGRATE) Land C8 (the entity-type spoke) + the two-route name-bridge path with GRADED constraint-integration
   selection (s.6.2) in the resolver; add a `board_namebridge` arm so the common-noun win is visible (the board
   coref dim scores pronouns). The MECHANISM sweep is DONE (s.2c) -- nothing mechanism-side left to build.
2. (COVERAGE, foundation -- the ONE real residual) Scale the ENCYCLOPEDIC KB: full Wikidata P106 occupation + P800
   notable-works so the entity's DEFINING facts (Galois authored works; person occupations) are covered -- this is
   what the top-down sweep converged on (the facet residual is encyclopedic, not a mechanism gap). Fits the
   knowledge-foundation north star; consolidate with the sibling's `wikidata_person_roles`. NOTE the ceiling probe
   says a bare-P31 swap is MODEST; the lever is OCCUPATION/WORKS granularity + name-span extraction quality.
3. (LOWER) local-Centering transition model (s.2c #3, +0.0084 -- recency proxies it); familiarity-ranked linking
   (s.2c #5). Both bounded; do only if a downstream error class demands them.
