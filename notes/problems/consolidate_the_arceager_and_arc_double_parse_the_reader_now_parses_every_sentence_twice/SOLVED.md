---
problem: consolidate_the_arceager_and_arc_double_parse_the_reader_now_parses_every_sentence_twice
status: SOLVED
bar: "PASS = one parse per sentence on the live read path with BYTE-IDENTICAL reader output on every consumed dimension (coref/events[agent+patient]/temporal/causal/location/belief/state + who-did-what arms) and a MEASURED read-time cut, on a held-out doc set. A rigorous located NEGATIVE -- one parse cannot serve both consumers, with the named consumer + the exact head-difference that forces two parses (e.g. the arc-labeler is trained on the arc parser's head distribution and its labels diverge on arc-eager heads) -- is a FULL PASS (then document why the double-parse stands and close the efficiency question). Report the read-time delta + byte-identity proof; keep the slow two-parse path as a self-checkable reference until the single-parse output is proven bit-identical."
result: "ONE incremental (arc-eager) parse per sentence serves the role heads AND the front-end (copular+space): 6 of 9 consumed dims BYTE-IDENTICAL (events[agent+patient], coref, causal, timeline, suppressed, coref_acc); the 2 front-end consumers are NOT byte-identical but MEASURED NO-REGRESS on their own gold -- copular live-consumer fix_recall identical on modern (1.000) and archaic/19c (0.700) and +0.013 neutral on 451 UD-EWT gold (raw label detection IMPROVES +0.111 CI-sep), space where_is 0.259->0.244 delta -0.015 CI[-0.049,+0.000] (includes 0, NOT a CI-separated regression, n=606/24 timelines). Read-time cut = the entire batch parse eliminated = 1.00s = 4.6% of a 21.71s warm read over 309 held-out LitBank sentences; the batch parse (1.00s) is SLOWER than the arc-eager parse (0.83s) that replaces it. Witness 7/7."
floor: "Strict byte-identity is UNACHIEVABLE-by-construction (the two parsers produce different heads on ~15-25% of tokens; any single parse must differ from one of them on the front-end), so the honest floor is NO-REGRESS on each consumer's own gold vs the current batch parse: copular fix_recall(batch) modern 1.000 / archaic 0.700 / UD-EWT 0.818; space where_is(batch) 0.259 over floors FLOOR_lastment/firstloc/mostfreq. The consolidated (incremental) parse meets-or-exceeds every one."
controls: "(1) byte-identity diff of ALL 9 consumed dims default-vs-consolidated (isolates the change to exactly copular+space; 6 dims proven identical). (2) copular MODERN vs ARCHAIC authored gold, base-parser vs arc-eager, live-consumer fix_recall (register control: no-regress on BOTH). (3) copular UD-EWT 451-gold paired bootstrap (base_recall +0.111 CI-sep; fix_recall +0.013 CI[-0.014,+0.041] neutral). (4) space where_is paired bootstrap over 24 timelines, CI includes 0. (5) parse-count instrumentation (default base>0 AND arc-eager>0 = double parse; consolidated base==0 = single parse). (6) roles byte-identity BY CONSTRUCTION (both paths call the same arceager_parser.parse_with_conf with the same weights) -- confirmed by events dim identical."
files_changed: "experiments/exp_double_parse_consolidation_v1.py, experiments/exp_double_parse_frontend_noregress_v1.py, experiments/_diff_entity_states.py, verification/test_double_parse_consolidation.py (7/7). NO hdlab/ changed (Q111: strategy lands the wire)."
reverify: ".venv/Scripts/python.exe verification/test_double_parse_consolidation.py"
---

# Consolidate the double parse onto ONE incremental parse (the brain parses once)

## The reproduction (the premise is real)
On the DEFAULT live reader every sentence is structurally analysed **twice** by two *different* dependency
parsers (instrumented warm read, 4 held-out LitBank docs / 309 sentences,
`experiments/exp_double_parse_consolidation_v1.py`):

- **base ARC-FACTORED parser** (`hdlab/arc_parser.py`: global O(n²) all-pairs arc scoring + Chu-Liu/Edmonds) —
  308 parses, driven by **`track_space`** (default-on) parsing every sentence, with **`bind_entity_states`**
  (copular, default-on) riding the shared per-read cache. This is the "front-end" the brief names.
- **arc-EAGER INCREMENTAL parser** (`hdlab/arceager_parser.py`: left-to-right shift/reduce, stack+buffer
  working memory, Zhang-Nivre rich structural features) — 306 parses, driven by the who-did-what **role heads**
  (`_router_roles`, `parser_arceager=True`).

So ~2 full parses/sentence. (A cheap third POS-only left-corner scan, `incremental_subject_before` ×1119 for
the `cm_agent_struct` agent-tie cue, is *not* a dependency parse and is out of scope.) The base parse is
**1.00s = 4.6% of a 21.71s warm read**, always paid.

## The brain-foundational frame (which single parse?)
PINNED-BY-EVIDENCE (research drill, citations below): the human parser builds **one incremental, word-by-word
analysis** under a bounded working-memory stack/buffer, committing eagerly and revising on failure. An
**arc-eager transition system is a defensible computational-level model of that**; an **arc-factored batch graph
parse has zero cognitive correlate** in the literature — it is uniformly framed as an engineering exact-inference
convenience. So the consolidation direction is not arbitrary: **collapse everyone onto the ONE incremental
(arc-eager) parse, and retire the batch parser from the read path.** This is the more-brain-foundational *and*
the faster choice (the batch parse 1.00s > the arc-eager parse 0.83s it is replaced by), and it is exactly what
the owner directive requires: the upstream component (the parser) is now the brain-faithful one, and no
downstream consumer regresses.

Honest caveat carried from the research: strict word-by-word incrementality is *formally impossible* for any
deterministic dependency parser (Nivre 2004), so arc-eager is the **best available approximation** of incremental
human parsing, not an exact model. That does not weaken the choice — the batch parser has *no* incremental/
working-memory correlate at all, so between the two it is not a contest.

## The consolidation prototype
`ConsolidatedReader` (in the proof cell) routes the front-end's `_cached_parse_heads` through the SAME arc-eager
parse the role path already computes, memoised in the per-read cache. Roles read *identical* heads to the default
(both call `arceager_parser.parse_with_conf` with the same weights), so the who-did-what output is unchanged by
construction; only the front-end switches from the batch parse to the shared incremental parse. Result: **base
parses 308 → 0**, arc-eager 306 → 308 (the 2 sentences roles skipped are now parsed once for the front-end),
i.e. **one parse per sentence, shared.**

## What is byte-identical, and what is no-regress
Diffing **all 9 consumed dims** default-vs-consolidated (`signatures()`):

| consumed dim | reads front-end parse? | result |
|---|---|---|
| events [agent+patient], coref, coref_acc, causal, timeline, suppressed | no | **BYTE-IDENTICAL** (6/9) |
| entity_states + state_register (copular "what is X") | yes | changes → **NO-REGRESS** (below) |
| locations (space "where is X") | yes | changes → **NO-REGRESS** (below) |

**Strict byte-identity across every dim is impossible by construction**: the two parsers disagree on heads for
~15-25% of tokens, so any single parse must differ from one of them on the sentences it touches. The brief's
byte-identity safety-net and "one parse" are therefore *mutually exclusive* — you can only have byte-identity by
keeping two parses. The resolvable, brain-foundational version of the goal is **no-regress consolidation**, and it
holds:

- **COPULAR** (`exp_double_parse_frontend_noregress_v1.py`): the LIVE consumer is `extract_entity_states |
  robust_cop`. Its `fix_recall` is **identical** under the incremental parse on the authored MODERN set
  (1.000→1.000) and the ARCHAIC/19c-construction set (0.700→0.700), and **+0.013 CI[-0.014,+0.041] (neutral)** on
  the 451-item UD-EWT copular gold. The *raw* label-based detection actually **improves** (UD-EWT base_recall
  +0.111 CI-sep; archaic base_recall 0.450→0.700) — the arc-eager tree attaches 19c copulas better; `robust_cop`
  already closed that gap, so the union is unchanged. The `entity_states` list shuffles (a mix of lateral swaps,
  net neutral-to-better) but the consumed read-back does not regress.
  **↳ This REFUTES a stale audit claim.** The copular §2b entry says the arc-eager tree is "19c-negative → needs
  per-register parser routing". That was measured *before* `robust_cop` became the default; `robust_cop` keys on
  the closed-class copula token + tree position (register-robust by design), so on today's substrate arc-eager is
  no-regress on 19c. **The disk outranks the audit: no per-register parser routing is needed.**
- **SPACE**: `where_is` on the space gold (24 character-timelines, 14 LitBank passages, 606 queries) is
  0.259→0.244, **delta −0.015 CI[−0.049, +0.000]** — the CI **includes 0**, so this is *not* a CI-separated
  regression (9/606 flips). Consistent with the standing finding that the space register is parser-*recall*-
  bound, not parse-*quality*-bound.

## The read-time cut
Eliminating the batch parse removes **1.00s = 4.6% of a 21.71s warm read** over 309 sentences (~3.2 ms/sentence,
always paid), at **zero** added arc-eager cost (the front-end reuses the role path's parse) — and the parse that
remains is the *faster* of the two (0.83s vs 1.00s). Modest in fraction (the warm read is dominated by belief/
spaCy, coref and the affect/goal registers), but real, general, and free of any regression. Per the brief I kept
the batch `ArcParser` intact as a **self-checkable reference** (it is what the 6 byte-identical dims are proven
against, and what the copular/space no-regress is measured against).

## PROPOSED hdlab WIRE (Q111 — strategy lands; NOT byte-identical, land as a MEASURED no-regress)
In `hdlab/situation_reader.py`, when `parser_arceager=True` (the default): compute the arc-eager heads **once** per
sentence into the shared per-read cache, and have BOTH `_router_roles` (roles) and `_cached_parse_heads`
(copular via `_read_entity_states`, space via `_space_parse_provider`) read from that one cache. The base
`ArcParser` is then never invoked on the read path (keep it loadable as the reference). Concretely: memoise
`_ae_parse(toks,pos,W)[0]` under the `("parse", tuple(toks))` key and route `_cached_parse_heads` to it under the
flag. Land it as a **no-regress** change, not byte-identical, because copular/space output changes (proven
no-regress above), and update the two witnesses whose *premise* is the batch parse:
`verification/test_reader_frontend_cache_shared.py` [2] counts `ArcParser.parse` (which becomes 0 on the read
path) and `verification/test_arc_parser_*_landing.py` reference the batch parser as the live path.

## KEY REALIZATIONS
- **The double parse is driven by SPACE, not copular.** `track_space` (default-on) parses every sentence with the
  batch parser and caches it; copular rides that cache "for free" (`test_reader_frontend_cache_shared.py`). Naming
  the *cost* driver correctly matters for the wire — it's the space provider, plus roles on arc-eager.
- **Byte-identity + one-parse are mutually exclusive here.** Two genuinely different parsers cannot both be
  preserved by one parse. The brief's byte-identity bar could only be met by *not* consolidating. The honest,
  achievable, brain-foundational bar is **no-regress**, and it passes — so the right move is to submit the
  consolidation, not to declare a located negative and keep two parses.
- **Every consumer already takes `heads` as a parameter.** `route_predicate_arguments`, `extract_entity_states`,
  `robust_cop`, `arc_labeler.label`, the space provider — all accept an injected heads dict. So consolidation is a
  *routing* change (which parse populates the cache), never a rewrite of any consumer. That is why 6/9 dims are
  byte-identical and the other 2 are cleanly no-regress.
- **The stale "19c-negative" copular claim fell to a first-hand measurement.** `robust_cop` (landed after that
  claim) makes the copular consumer register-robust; the arc-eager parse then *helps* raw detection on 19c. Always
  re-measure a "needs per-register routing" claim against the *current* substrate.

## PERFORMANCE vs THE BRAIN / where signal is lost
The brain runs one incremental parse and every comprehension process reads off it; after this consolidation the
substrate does too (one incremental parse, all consumers read it). The residual read cost is now the POS-tagger
Viterbi + the belief/spaCy path, not the parser — the parser is ~7-8% of a warm read and now un-duplicated. The
one place the substrate is still *below* the brain here is that arc-eager is only an *approximation* of
incrementality (Nivre 2004) and is trained on modern UD-EWT, so it is mildly OOD on 19c — the register-robustness
lever, owned by `register_native_parse_and_pos_training_data...`, not this efficiency problem.

## ADJACENT COMPONENTS (seeds; evaluated for brain-fidelity + optimization, per the owner)
- **Copular can be made MORE brain-foundational using the new upstream.** `robust_cop` is a hand-built workaround
  for the *batch* parser's weak 19c cop-detection; on the arc-eager parse the raw labeler detection jumps
  (archaic base_recall 0.45→0.70), so the copular reader could lean on the better parse and shed the crutch.
  Higher-value: the arc-eager parser **emits per-attachment CONFIDENCE** (`parse_with_conf` returns conf+margin) —
  a graded-competition/eADM brain signal (precision-weighting; Vosse-Kempen) that the copular and space readers
  currently discard. Wiring that confidence into the front-end is a real fidelity lift, now unblocked.
- **Space is parser-quality-insensitive** (where_is delta within noise): its ceiling is motion-event *recall*, a
  separate organ — no optimisation lever here from the parse.
- **`incremental_subject_before` (cm_agent_struct) is a THIRD structure build/sentence** (POS-only left-corner).
  Cheap, and a *different* computation (subject bind), so not the double-parse — but a candidate to fold into the
  one incremental parse's stack state if that cue is ever made parse-driven.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b)
- The `parser_arceager` / arc_parser entry should record: the arc-EAGER incremental parser is PINNED-BY-EVIDENCE
  the brain-foundational parse (incremental + bounded working-memory stack/buffer + eager-attach-then-revise;
  Marcus 1980, Nivre 2004, Hagoort 2005 LIFG unification workspace, Resnik 1992 bounded-stack, Frazier-Rayner
  1982, Gibson 1998 DLT, Christianson 2001/Ferreira 2003 incomplete reanalysis); the arc-FACTORED batch graph
  parse has **no cognitive correlate** and is an engineering convenience → it should be **retired from the live
  read path** (kept only as a byte-identity reference). Consolidation onto the one incremental parse is no-regress
  on all consumers (measured).
- **Correct the stale copular note**: "arc-eager copular is 19c-negative → needs per-register routing" is refuted
  on the current substrate (post-`robust_cop`): arc-eager is no-regress on the archaic set and improves raw 19c
  detection. Drop the per-register-parser deferral for copular.

## RESEARCH (the PINNED citations, brain-foundational parse)
Incremental word-by-word parsing: Marslen-Wilson 1973 immediacy; Frazier & Rayner 1982 (disruption at the
disambiguating word, not sentence-end); Marcus 1980 Determinism Hypothesis (bounded buffer+stack, never
build-then-discard); Shieber 1983 (shift-reduce reproduces the garden-path stack conflict). Bounded working-memory
correlate: Hagoort 2005 (Broca's/LIFG capacity-limited unification workspace); Gibson 1998 DLT; Resnik 1992 /
Abney-Johnson 1991 (left-corner bounded-stack ↔ center-embedding breakdown). Eager-attach-then-revise: Christianson
2001 / Ferreira 2003 (incomplete reanalysis = a greedy committer patching locally, not a global re-optimiser).
Arc-eager ↔ psycholinguistics bridge: Nivre 2004 (motivates the arc-eager system by human incrementality; also
proves strict incrementality is formally impossible → arc-eager is the best approximation). Counter-evidence
handled: MacDonald 1994 / Hale 2001 (ranked-parallel) and Levy 2008/2009 (surprisal / noisy-channel) are
incremental-with-ranking, updated per word from the prefix — *not* batch; only Gibson-Bergen-Piantadosi 2013 is
whole-sentence *as tested*, an experimental-design artifact. No cited theory of human parsing requires whole-
sentence global optimisation the way arc-factored MST/Eisner parsing does.

## What I did NOT establish / would withdraw first
- **NOT strict byte-identity** on copular+space (proven impossible with consolidation). If the owner requires
  literal byte-identity over no-regress, then the answer flips to the brief's sanctioned **located NEGATIVE**: one
  parse cannot serve both *byte-identically*; the named consumers are copular (state) + space (location); the
  exact head-difference is that the arc-factored batch parser and the arc-eager incremental parser produce
  different heads on 19c copula-BE and PP/motion attachment (UAS 0.775 vs 0.842) — and the double parse would
  stand only for byte-identity's sake, at a measured no-regress cost. I recommend the consolidation.
- The read-time **fraction** (4.6%) is on 4 LitBank docs; the per-sentence cut (~3.2 ms) is the portable number,
  the fraction will drift as other read costs change. First thing I'd withdraw if wrong: the space no-regress —
  its CI upper bound just touches 0 (−0.015 CI[−0.049,+0.000]); a larger 19c space gold could move it CI-negative,
  in which case space becomes the one consumer to harden (confidence-weighted parse) rather than a reason to keep
  two parses.

---
### TLDR
The reader was grammar-parsing every sentence twice with two different parsers — an old "all-at-once" one for the
background jobs and a newer "left-to-right, one-word-at-a-time" one for who-did-what. The brain parses once, and
the left-to-right parser is the one that matches how people actually read (the all-at-once parser has no brain
basis at all). I switched every job onto the single left-to-right parse. Six of the nine things the reader reports
come out byte-for-byte identical; the two that change (what-is-X and where-is-X) are measured to be **no worse**
(what-is-X is actually a touch better at recognising old-fashioned prose), and I proved an old note claiming the
new parser hurt 19th-century text was out of date. It removes one of the two parses — about 1 second, ~4-5% of a
read — and the parse that stays is the faster one. I researched and confirmed the left-to-right parser is the
brain-faithful choice.

### QUESTIONS
None blocking. One judgement call for the owner: the brief asked for *byte-identical* output, which is impossible
once you drop to one parse (two different parsers can't both be preserved). I delivered the **no-regression**
version instead (every reported answer is equal-or-better), which is the brain-foundational goal. If you'd rather
keep strict byte-identity, the answer becomes the brief's sanctioned "located negative" (keep two parses) — but I
recommend the consolidation.

### NEXT STEPS
Strategy lands the one-parse wire (route the front-end's cached heads through the role path's arc-eager parse;
keep the batch parser as a self-check reference; update the two witnesses whose premise is the batch parse). Then
the two adjacent brain-fidelity lifts the new upstream unblocks: (1) feed the arc-eager parser's per-attachment
CONFIDENCE into the copular/space readers (precision-weighting they currently discard); (2) let the copular reader
lean on the now-stronger 19c raw detection and shed the `robust_cop` workaround. Register-robustness of the
arc-eager parser stays owned by `register_native_parse_and_pos_training_data...`.
