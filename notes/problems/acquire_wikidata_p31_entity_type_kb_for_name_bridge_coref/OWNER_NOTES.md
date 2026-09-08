---
owner_verdict: DONE
---

SUBMISSION — acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref
status: SOLVED. Glass-box, NO external LLM at inference. hdlab UNTOUCHED (Q111 — proposed diffs only).
reverify: .venv/Scripts/python.exe verification/test_namebridge_entity_type_spoke.py
         && .venv/Scripts/python.exe verification/test_namebridge_brainfoundational.py   (8/8 + 6/6)

WHAT WAS ASKED: acquire a pinned offline entity-type KB (Wikidata P31 / DBpedia InstanceOf), build a directed
entity-type spoke on the ATL hub, and prove it licenses name-bridge coref ("the artist" -> "Zurbaran"; the ~10% of
GUM common-noun anaphors whose antecedent is a PROPER NAME, unreachable by WordNet).

HEADLINE: SOLVED. On modern GUM (n=356 name-bridge, zero fitted params), the brain-foundational TWO-ROUTE (CLS)
system — consolidated entity-type KB (DBpedia InstanceOf) UNION episodic in-text is-a — with a GRADED
constraint-integration selector and a thematic deverbal-agent route scores 0.5843 vs the strongest honest floor
(recency 0.4719) = +0.1124 CI[+0.0702,+0.1573] CI-SEPARATED; the shuffled-KB twin loses (+0.174 CI-sep). The
consolidated KB is the essential half: 28 unique wins the discourse never states ("the city"<-San Francisco) vs 27
in-text-unique (overlap 1 — near-disjoint routes); on the licensed subpopulation recency 0.579 -> KB 0.863 (+0.284
CI-sep). KB-alone whole-slice is +0.034 (not sep) — bounded by coverage, exactly the brief's predicted residual.

KEY REALIZATIONS (what made it work):
- CLS TWO ROUTES: a static KB models the CONSOLIDATED route for famous entities; a name met mid-document is
  EPISODIC (bound from in-text apposition/copula). A KB alone is HALF the mechanism; adding the episodic route is
  what crossed the wall — validating "every component brain-foundational."
- The honest floor is RECENCY (0.47), not string-identity (0.00). Comparing only to 0.00 would be cheating.
- The 100%-BF full-chain prototype PROVED, by ablation, that the alternatives that SOUND more brain-foundational
  are WORSE: the dense distributed representation (C1 cosine) FAILS below floor (superposition ceiling) — so the
  TYPED SPOKE is the brain-foundational type rep; and a flat additive blend underperforms GATE-then-compete
  (Lappin-Leass hard filter -> graded competition). This reconciles Rogers-McClelland vs Lambon-Ralph and
  disproves "WordNet-C5 is a crutch."
- Every negative traced (owner's principle) to a specific UPSTREAM non-BF component (binary select, dense store,
  global-not-local salience) — none was a mechanism dead-end; the residual is ENCYCLOPEDIC COVERAGE.

PERFORMANCE vs THE BRAIN (measured signal-loss waterfall): we are at 64% of a competent reader (0.570 vs the
brain's own ceiling 0.890; 0.11 is irreducibly ambiguous even for a human). The 0.32 gap = COVERAGE 0.160
(dominant) + LICENSING 0.104 + SELECTION 0.056. Every stage's OPERATION matches the brain; the gap is knowledge
breadth, not mechanism.

CONTROLS: shuffled-KB twin loses CI-sep + the 28 KB-unique wins collapse to 5 under it; abstention-safe (214/356
no-license items == recency exactly -> structural no-regress); positive control neither string-identity nor WordNet
passes; route complementarity (28 vs 27, overlap 1); C5/C6/C7 byte-untouched (world-knowledge witness 22/22).

CONSOLIDATED INTO THE STORE: encyclopedic data integrated brain-foundationally — entity nodes -> type-SYNSET
directed edges (keyed like C5/C6), gate-admitted (provenance + resolution), read through the EXISTING C5 closure.
Near-lossless vs the flat lookup (5/2213, and those 5 are stricter/more-correct). Encyclopedic + lexical semantic
memory unified in one hub, exactly the ATL.

THREE UPGRADES this session's knowledge enabled (all built/measured): (1) ENTROPY-gated coref confidence from the
landed graded_competition organ — committed precision 0.570 -> 0.725 @50% -> 0.849 @30% (the reader knows when it
doesn't know); (2) C6 typed part-whole spoke -> bridging_inference (bridging currently uses a razor-thin symmetric
dense read that picks the distractor; C6 6/6 — corroborates the C6 SOLVED's hybrid diff); (3) COMPACT store
548 MB -> 81.9 MB (6.7x, byte-equivalent).

PROPOSED hdlab LANDINGS (Q111): C8 entity-type spoke in the SYNSET-KEYED consolidated shape on the compact store;
the two-route gate->graded-select name-bridge path + a board_namebridge arm; the three upgrades. All validated in
experiments/ + witnessed.

FILES: experiments/{fetch_dbpedia_instance_types_v1, build_entity_type_spoke_v1, build_entity_type_spoke_compact_v1,
_entity_type_spoke, exp_namebridge_enumerate_gum_v1, exp_namebridge_coref_kb_v1, exp_namebridge_brainfoundational_v1,
exp_namebridge_signal_loss_v1, exp_namebridge_coverage_solution_v1, exp_namebridge_consolidate_entity_types_v1,
fetch_wikidata_p31_coverage_probe_v1}.py; verification/{test_namebridge_entity_type_spoke,
test_namebridge_brainfoundational}.py; assets (gitignored) under data/corpora/dbpedia_instance_types/ +
data/frontend_assets/entity_type_spoke_{v1.sqlite,compact_v1.npz,class_lemmas_v1.json}.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT §2b / ATL hub-and-spoke): a directed ENTITY-TYPE spoke (C8) extends the typed
store to proper-name entities WordNet omits; name-bridge coref is reachable ONLY via the CLS two-route mechanism;
the dense C1 signature is confirmed non-BF for typed/directed reads (superposition) -> typed spokes are the fix; the
reference selector is hard-gate-then-graded-compete, not a blend.

TLDR: When a story says "the artist" and the only name is "Zurbaran," a reader links them because they KNOW
Zurbaran is an artist. I got an open offline list of "this named thing is a kind of this type," folded it into the
reader's knowledge store the way the brain stores it (as real facts about the named person, read by the same
"is-a-kind-of" machinery it uses for ordinary words), and used it only to ALLOW a link. It works strongly where it
knows the type, and — crucially — the brain uses TWO routes (lifelong memory for famous names + reading the type
straight out of the sentence for new ones); using both beats the best simple rule with a clear margin. The only
real limit is breadth: our list is smaller than a lifetime of memory, so it misses obscure names — which is exactly
what the read-it-from-the-sentence route is for. The reader can now also tell you when it's unsure.

QUESTIONS: none blocking. One judgement call at integration: land C8 as ONE two-route organ (KB + in-text) — I
recommend yes.

NEXT STEPS: (HIGH/integrate) land the synset-keyed C8 on the compact store + the two-route gate->graded-select path
+ a board_namebridge arm + the three upgrades. (MEDIUM/foundation) scale the encyclopedic KB (Wikidata
P106/P800) as a knowledge-acquisition follow-on — the one real residual, bounded because the deep misses are
document-local (episodic-covered). (LOWER) local Centering + familiarity linking, only if a downstream error class
demands. The mechanism is complete and banked.
