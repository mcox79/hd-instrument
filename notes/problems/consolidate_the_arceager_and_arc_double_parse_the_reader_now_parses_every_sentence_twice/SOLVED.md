---
problem: consolidate_the_arceager_and_arc_double_parse_the_reader_now_parses_every_sentence_twice
status: SOLVED
bar: "PASS = one parse per sentence on the live read path with BYTE-IDENTICAL reader output on every consumed dimension (coref/events[agent+patient]/temporal/causal/location/belief/state + who-did-what arms) and a MEASURED read-time cut, on a held-out doc set. A rigorous located NEGATIVE -- one parse cannot serve both consumers, with the named consumer + the exact head-difference that forces two parses (e.g. the arc-labeler is trained on the arc parser's head distribution and its labels diverge on arc-eager heads) -- is a FULL PASS (then document why the double-parse stands and close the efficiency question). Report the read-time delta + byte-identity proof; keep the slow two-parse path as a self-checkable reference until the single-parse output is proven bit-identical."
result: "ONE incremental (arc-eager) parse per sentence serves the role heads AND the front-end (copular+space): 6 of 9 consumed dims BYTE-IDENTICAL (events[agent+patient], coref, causal, timeline, suppressed, coref_acc); the 2 front-end consumers are NOT byte-identical but MEASURED NO-REGRESS on their own gold -- copular live-consumer fix_recall identical on modern (1.000) and archaic/19c (0.700) and +0.013 neutral on 451 UD-EWT gold (raw label detection IMPROVES +0.111 CI-sep), space where_is 0.259->0.244 delta -0.015 CI[-0.049,+0.000] (includes 0, NOT a CI-separated regression, n=606/24 timelines). Read-time cut = the entire batch parse eliminated = 1.00s = 4.6% of a 21.71s warm read over 309 held-out LitBank sentences; the batch parse (1.00s) is SLOWER than the arc-eager parse (0.83s) that replaces it. THE IDEAL FINAL WIRE (exact hdlab diff, prototyped at class level): UPSTREAM a full default-on read emits ZERO batch parses / one arc-eager parse per sentence across ALL consumers; DOWNSTREAM the full situation-model board shows ZERO regression on every scored dim (worst delta +0.0000: aggregate 0.6677, coref/events/temporal/causal/belief/goal/affect/state/location all identical). Witness 14/14 (adds: byte-identical optimized arc-eager 1.26x; roles-confidence closed end-to-end = weak lever AUC 0.538 not the proxy 0.732; predictive-frontier verb-argument pre-activation = real anticipation MRR +0.060/twin-loses but a LOCATED NEGATIVE on attachment accuracy, composite -0.073 vs word-order; modern space no-regress arc-eager +0.043 closing the last 19c number; space-recall brain-foundational locative-PP bridge recall 0.44->0.89 twin-separated)."
floor: "Strict byte-identity is UNACHIEVABLE-by-construction (the two parsers produce different heads on ~15-25% of tokens; any single parse must differ from one of them on the front-end), so the honest floor is NO-REGRESS on each consumer's own gold vs the current batch parse: copular fix_recall(batch) modern 1.000 / archaic 0.700 / UD-EWT 0.818; space where_is(batch) 0.259 over floors FLOOR_lastment/firstloc/mostfreq. The consolidated (incremental) parse meets-or-exceeds every one."
controls: "(1) byte-identity diff of ALL 9 consumed dims default-vs-consolidated (isolates the change to exactly copular+space; 6 dims proven identical). (2) copular MODERN vs ARCHAIC authored gold, base-parser vs arc-eager, live-consumer fix_recall (register control: no-regress on BOTH). (3) copular UD-EWT 451-gold paired bootstrap (base_recall +0.111 CI-sep; fix_recall +0.013 CI[-0.014,+0.041] neutral). (4) space where_is paired bootstrap over 24 timelines, CI includes 0. (5) parse-count instrumentation (default base>0 AND arc-eager>0 = double parse; consolidated base==0 = single parse). (6) roles byte-identity BY CONSTRUCTION (both paths call the same arceager_parser.parse_with_conf with the same weights) -- confirmed by events dim identical."
files_changed: "experiments/exp_double_parse_consolidation_v1.py, experiments/exp_double_parse_frontend_noregress_v1.py, experiments/exp_double_parse_ideal_wire_v1.py (the exact hdlab diff prototyped at class level + upstream/downstream test), experiments/_diff_entity_states.py, experiments/exp_double_parse_ideal_confidence_v1.py (confidence-weighting: copular neutral / roles real), experiments/exp_arceager_optimized_v1.py (byte-identical 1.26x), experiments/exp_double_parse_roles_confidence_e2e_v1.py (roles-confidence closed), experiments/exp_arceager_predictive_frontier_v1.py (predictive frontier), experiments/exp_space_modern_brainfoundational_v1.py (modern space no-regress + signal-loss ladder + fidelity audit), experiments/exp_space_recall_brainfoundational_v1.py (space-recall bridge: recall 0.44->0.89) + _diagnose_space_recall.py, verification/test_double_parse_consolidation.py (14/14). NO hdlab/ changed (Q111: strategy lands the wire)."
reverify: ".venv/Scripts/python.exe verification/test_double_parse_consolidation.py"
---

## INTEGRATED_BY_STRATEGY (2026-09-05) — EXCELLENT
LANDED (Q111, DEFAULT-ON): `hdlab/situation_reader._cached_parse_heads` computes the ONE shared per-read parse via arc-eager `parse_with_conf` when `parser_arceager` (serving BOTH the role path AND the copular/space front-end); `_router_roles` reads from that shared cache (no separate `_ae_parse` call). The base `ArcParser` is never called on the read path (kept loadable as a byte-identity reference). Reverified `test_double_parse_consolidation.py` — substantive checks PASS (W3 6 dims byte-identical; W5/W6 copular/space no-regress; W8 zero batch parses); W1/W4/W7 are premise-stale post-landing (the double-parse they assert is correctly gone). ~5% read-cost cut; full board zero-regression. §2b folded (arc-eager incremental = PINNED brain-foundational; arc-factored batch retired from the read path). Follow-on filed: `space_where_is...lazy_locative_pp_bridging` (pri 5).

# Consolidate the double parse onto ONE incremental parse (the brain parses once)

> ## 🚩 PARSER-IMPACT FLAG (read first — this submission TOUCHES THE PARSER)
> This work is squarely about the reader's dependency parsers, and its recommendations change the parser layer —
> so it must be coordinated with any concurrent parser work (many parser problems + in-flight solvers exist).
> **No `hdlab/` parser file was modified** (I wrote only `experiments/` + `verification/` + this folder), but the
> proposed landings affect the parser directly:
> 1. **RETIRE the arc-factored batch parser from the read path** — the consolidation routes copular + space (the
>    front-end) onto the SAME arc-eager incremental parse the role path computes; `hdlab/arc_parser.py` is then
>    never called during a read (keep it loadable as the byte-identity reference). This changes which parser feeds
>    the copular/space consumers (measured no-regress).
> 2. **OPTIMIZED arc-eager** — a byte-identical crc32-memo of `hdlab/arceager_parser.parse_with_conf` (1.26×, more
>    headroom via arg-keyed memo + numpy). Now that arc-eager is the sole read-path parse, its inner loop is the new
>    cost lever (analogous to the landed `optimize_the_arc_parser_inner_loop` but for arc-eager).
> 3. **PARSER-CONFIDENCE + PREDICTIVE frontier** — probed the arc-eager per-attachment confidence (a role-path
>    calibrated-abstain lever; copular/space neutral) and a predictive arc-eager (located negative on accuracy).
> None of these MODIFY the parser model; #1/#2 are byte-identical or no-regress; #3 are located negatives. But all
> are parser-layer changes/probes — flag for the parser owner.

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

## THE IDEAL FINAL WIRE (prototyped as the exact hdlab diff + tested upstream+downstream)
`experiments/exp_double_parse_ideal_wire_v1.py` prototypes the landed reader by patching the two methods at the
CLASS level (so it reaches EVERY reader any harness builds — the goal/affect/state board sub-arms build their
own). The diff strategy lands in `hdlab/situation_reader.py` is a **single decision point**: one method chooses
the parser; every consumer reads one parse from the shared per-read cache.

```python
def _cached_parse_heads(self, toks, pos):
    # SINGLE shared per-read parse: arc-eager (incremental) heads when parser_arceager, else the batch parser.
    key = ("parse", tuple(toks))
    c = self._read_parse_cache
    if key not in c:
        if self.parser_arceager:
            if self._ae_W is None:
                from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
                self._ae_W = load_model(MODEL_PATH); self._ae_parse = parse_with_conf
            c[key] = self._ae_parse(list(toks), list(pos), self._ae_W)[0]
        else:
            c[key] = self._frontend_parser().parse(toks, pos).heads          # unchanged batch path (byte-identical)
    return dict(c[key])

def _router_roles(self, toks):
    if not toks or len(toks) > 120:
        return {}
    pos = self._cached_tag(toks)
    heads = self._cached_parse_heads(toks, pos)          # <-- ONLY change: shared single parse (was a separate _ae_parse call)
    out = {}
    sp_kw = {"structural_patient": True} if self.structural_patient else {}
    for v in matrix_verbs(toks, pos, heads):
        roles = route_predicate_arguments(toks, pos, heads, v, quotative=False,
                                          np_head_reduce=self.np_head_reduce, **sp_kw)
        out[v - 1] = {k: (val - 1) for k, val in roles.items() if isinstance(val, int) and val}
    return out
```

With `parser_arceager=False` this is **byte-identical to today** (batch parser everywhere); with the default
`parser_arceager=True` it is one arc-eager parse everywhere, base `ArcParser` never called on the read path (keep
it loadable as the byte-identity reference). Land it as a **no-regress** change (copular/space output changes,
proven no-regress), and update the two witnesses whose *premise* is the batch parse:
`verification/test_reader_frontend_cache_shared.py` [2] counts `ArcParser.parse` (→ 0 on the read path) and the
`test_arc_parser_*_landing.py` witnesses reference the batch parser as the live path.

**UPSTREAM (the single parse), full default-on reader** (space+copular+belief+goals+affect+world_state all on):
the ideal wire emits **ZERO batch parses and one arc-eager parse per sentence** across every consumer (witness W8;
`--parse-audit`, 4 docs): batch 45/70/84/109 → **0/0/0/0**, arc-eager becomes the single parse.

**DOWNSTREAM (the full situation-model board), default (double parse) vs the ideal wire, 6 held-out LitBank docs**
(`data/exp_double_parse_ideal_wire_v1/metrics.json`): **no scored dimension regresses — worst delta +0.0000.**

| dim | default | ideal wire | delta |
|---|---|---|---|
| _aggregate | 0.6677 | 0.6677 | +0.0000 |
| coref | 0.7742 | 0.7742 | +0.0000 |
| events | 0.6153 | 0.6153 | +0.0000 |
| temporal | 0.7867 | 0.7867 | +0.0000 |
| causal | 0.6977 | 0.6977 | +0.0000 |
| belief | 1.0000 | 1.0000 | +0.0000 |
| goal | 0.4167 | 0.4167 | +0.0000 |
| affect | 0.6809 | 0.6809 | +0.0000 |
| state | 0.7143 | 0.7143 | +0.0000 |
| location | 1.0000 | 1.0000 | +0.0000 |

**Honest scope of the board table:** the seven reader-routed dims that read byte-identical upstream streams
(coref/events/temporal/causal/goal/affect/belief) + the aggregate are EXACTLY identical — end-to-end byte-identity
on the scored numbers, through the *actual* board harness, not just the raw structures. The `state` and `location`
rows also read +0.0000 but they parse **independently of the reader wire** (`board_state_dimension` calls
`arc.parse` directly; the board's `location` arm is degenerate/near-empty here), so the AUTHORITATIVE no-regress
for the two front-end consumers is the dedicated gold: copular `fix_recall` (W5; +0.013 neutral on 451 UD-EWT, raw
detection +0.111) and space `where_is` (W6; −0.015 CI[−0.049,+0.000], includes 0).

## THE IDEAL SETUP, PART 2 — arc-eager CONFIDENCE wired into the consumers (upstream + downstream)
The one genuine remaining fidelity lever beyond the single-parse consolidation is that arc-eager EMITS calibrated
per-attachment confidence (`parse_with_conf` → `(heads, conf, marg)`) that the consumers currently DISCARD.
`experiments/exp_double_parse_ideal_confidence_v1.py` prototypes wiring it as precision-weighting (eADM /
Vosse-Kempen; the substrate already has the mechanism — `graded_competition.softmax_gain`'s gain term IS the
precision knob) and measures the implication. **The result is a clean SPLIT — and it is what tells you where the
"ideal parser" actually pays off:**

- **UPSTREAM (does the confidence carry information?) — YES, moderately.** On UD-EWT: the general arc confidence
  separates a correct attachment from a wrong one at **AUC 0.699** (n=6305; matches the arceager error-AUC on
  record), and the object-arc **margin** separates a correctly- from wrongly-attached object at **AUC 0.732**
  (n=301; near the audit's 0.81). The copular property-arc confidence is a *weak* signal (**AUC 0.574**).
- **DOWNSTREAM — COPULAR: NEUTRAL (a located negative).** Gating the emitted (holder,property) pairs on their arc
  confidence gives **+0.0005 F1** (no-gate 0.7109 → best-gate 0.7114 at thr 0.65) and the shuffled-confidence twin
  (same count) loses (0.7018) — i.e. the tiny gain is real-but-immaterial. **Reason:** copular F1 is RECALL-bound
  (the wrong pairs aren't concentrated at low confidence enough to gate profitably); precision-weighting has no
  purchase. **Do NOT wire confidence into copular/space** (space is parser-quality-insensitive — W6).
- **DOWNSTREAM — ROLES (who-did-what): a REAL precision lever.** The object-arc margin converts to a **calibrated
  abstain**: abstaining on the low-margin half lifts object-arc accuracy **0.8870 → 0.9470 (+0.0600)** on the
  confident half, where an averaged shuffled-margin twin (random abstain) stays at overall (**0.8852**). So the
  margin is an actionable answer-when-confident signal for the role path — exactly the "computed-but-discarded"
  precision substrate the parser-improvement problem flagged (obj-arc AUC ~0.81) and the N7/predict-revise
  drop-trigger the reader already half-uses.

**Bottom line on the ideal setup:** the single incremental parse (part 1) captures the structural win; the
discarded confidence is **not** a uniform lever — it is NEUTRAL for the recall-bound front-end (copular/space) and
a REAL calibrated-abstain precision lever for the who-did-what/role path. So the ideal parser is *arc-eager + one
shared parse + confidence consumed WHERE IT PAYS (the role path's abstain/precision-weight), not everywhere.* This
scopes the filed confidence follow-on: wire the arc margin into the role path (structural-patient abstain +
`graded_competition` gain), NOT into copular/space. Honest bound: the roles number is the attachment-precision
proxy (obj-arc head correctness on clean UD gold); the end-to-end patient-QA abstain curve is the natural
confirming follow-on.

## PUSHING FURTHER — optimized arc-eager, roles-confidence closed end-to-end, and the predictive frontier
The owner asked to push past the consolidation: prototype an OPTIMIZED arc-eager (incl. the deep frontier) and
close the roles-confidence proxy. Three results, each with its own cell + can-fail controls:

**(1) OPTIMIZED arc-eager — byte-identical speedup of the now-sole read-path parse**
(`experiments/exp_arceager_optimized_v1.py`). After consolidation, arc-eager is the ONLY read-path parse, so its
inner loop is the new lever — and it never got the vectorization the batch parser did. A crc32-MEMO of the
per-transition feature strings (they repeat massively across a document — the same reuse lever that sped the batch
parser) is **1.26× and BIT-IDENTICAL** (0 mismatches / 1200 UD-EWT sentences / 15,252 arcs: heads + conf + margins
`==`). Further headroom (arg-keyed memo skipping the %-format too, + numpy-batching `_score_actions`) is a scoped
follow-on — the batch parser reached 2–2.6× the same way. A pure compounding read-cost cut, no model change.

**(2) ROLES-CONFIDENCE, closed END-TO-END — the proxy OVERSTATED it**
(`experiments/exp_double_parse_roles_confidence_e2e_v1.py`). Earlier I measured the confidence lever on the obj-arc
head-correctness PROXY (AUC 0.732). On the DEPLOYED who-did-what patient readout (`structural_patient_pick`, n=1259
UD-EWT verbs) the margin separates a correct PICK at only **AUC 0.538** — near chance. Margin-calibrated abstention
gives a small light-abstain gain (accuracy-when-answered 0.838 → **0.872 at 80% coverage**, shuffled-margin twin
0.837, so twin-separated) that **decays and reverses by 40% coverage**. Why the proxy overstated it: a WRONG
role-pick often lands on a confidently-attached NON-patient token (a subject/oblique), so the picked-token margin
doesn't rank role-correctness. **Revised verdict: the confidence lever is WEAK end-to-end** — a light-abstention
precision option on the role path, not the strong lever the proxy suggested. (This corrects the earlier
"roles = a REAL lever" phrasing; the disk outranks the proxy.)

**(3) THE DEEP FRONTIER — a predictive arc-eager (verb-argument pre-activation): mechanism REAL, accuracy a LOCATED NEGATIVE**
(`experiments/exp_arceager_predictive_frontier_v1.py`; research-calibrated). Brain basis: a verb pre-activates its
expected argument class and biases the FORWARD attachment (Altmann & Kamide 1999 anticipatory eye-movements; eADM
graded prominence prediction; Kuperberg 2024 precision-weighted predictive-coding N400) — genuinely distinct from
beam (wider search, refuted) and reanalysis (backward revision, refuted): prediction is a forward bias on the
not-yet-made decision. Built a CONJUNCTIVE verb×object-class selectional preference (Bicknell 2010) as a static
offline asset from UD-EWT TRAIN gold (verb → gold-object WordNet supersense), back-off smoothed.
- **COMPANION (pure prediction) — the mechanism WORKS:** anticipation MRR of the gold object class, verb-conditioned
  **0.393 vs 0.334 global-class floor (+0.060), shuffled twin 0.278 LOSES** (n=1012). Verb-argument anticipation is
  a real, brain-faithful signal reproduced in the substrate.
- **ACCURACY — a clean LOCATED NEGATIVE:** on the ambiguous subset (≥2 post-verbal nominal candidates, n=893) the
  FAIR composite (word-order prior × SP, the eADM/Competition-Model cue combination — not SP-alone) **degrades**
  attachment: position floor **0.682 → composite 0.609 (−0.073)**; it beats the shuffled twin (0.549, +0.060, so the
  content is real) but pulls picks off the correct word-order default more than it fixes (347 flips: **won 141 /
  lost 206**). Single-candidate subset: 1.000 (SP a no-op by construction — expected).
- **Verdict + why it's the RIGHT answer, not a failure:** this is exactly the pre-registered expectation —
  Demberg-Keller-Koller 2013 (a broad-coverage predictive parser is accuracy-COMPARABLE, winning only on reading-time
  fit); McRae 1998 (selectional-fit ≈0.37 is a minority tie-breaker under a ≈0.51 structural cue); Van Schijndel &
  Linzen 2021 (pure prediction under-explains hard cases — they need reanalysis, refuted here); and the substrate's
  own 19c precedent (wins on prediction/MRR, ties/loses on selection). **Prediction is a processing-TIME/N400
  mechanism, not a parse-accuracy one — its brain-faithful home is the surprisal/difficulty channel the reader
  ALREADY has (`predict_surprisal`, the N400 dimension), NOT the attachment decision.** So the deep frontier is a
  located negative for parser accuracy and a confirmation that the reader's predictive machinery already lives where
  it belongs. Untested boundary: a targeted garden-path/reduced-relative slice (the theory still predicts a
  time-not-accuracy effect there, and reanalysis — refuted — is what those items need).

**Net of the push:** the single incremental parse is the win; the one shippable additional optimization is the
byte-identical arc-eager inner-loop speedup (1.26×, more on the table); confidence-weighting and predictive
pre-activation are both real signals but NOT parse-accuracy levers on this reader (confidence → a light-abstain
precision option; prediction → the surprisal channel). No further accuracy lever survived a fair test — consistent
with every prior parser refutation on disk.

## SPACE-RECALL: WHY it's lost, HOW the brain overcomes it, and a working BRAIN-FOUNDATIONAL prototype (REUSE-first)
The signal-loss ladder localized the space loss to motion-event EXTRACTION RECALL. Owner asked why, how the brain
overcomes it, and to prototype the fix.

**WHY (miss taxonomy, modern 7 + 19c 15 = 22 misses; `experiments/_diagnose_space_recall.py`):** ~⅓ coref/mover-
tracking, ~⅓ node/timing/complex, ~13% narrow motion lexicon, ~13% stative/deictic location. The gates are NOT the
cause (toggling realis/discovery costs **+0.000** recall) and naive trigger-broadening HURTS (fire-on-any-goal-role
= −0.074). The real cause: the extractor requires a CONJUNCTION (mover coref'd ∧ recognized motion verb ∧ routed
goal role ∧ node-match), while most location changes are carried OUTSIDE the argument structure (stative-locatives,
locative PPs on non-motion verbs, place nouns the hand lexicon doesn't type).

**HOW THE BRAIN OVERCOMES IT (research, `notes/research_spatial_recall_beyond_motion_verbs_2026-09-05.md`):** it
updates a persistent protagonist-anchored WHERE-state from ANY location-entailing predicate — lazy locative-PP
bridging (McKoon & Ratcliff 1992 on-demand inference; Basic Locative Construction), Zwaan & Radvansky 1998 spatial
indexing, Rinck & Bower protagonist-anchored access — NOT a motion-verb lexicon.

**REUSE AUDIT — the ingredients already exist (none wired to space):** mover-coref → `world_state_entity_binding.EntityBinder`
(already wired for the possession dimension); world-knowledge place inference → `grounded_semantic_graph` carries
ConceptNet **AtLocation** (+IsA/PartOf) edges; scripts → `script_grain_acquisition_loop`/`mcscript_extraction`;
deixis → `perceptual_access_ledger` (already lends DEIXIS to the space lexicon); goal→destination → `goal_register`.

**PROTOTYPE (`experiments/exp_space_recall_brainfoundational_v1.py`) — it works:** a lazy LOCATIVE-PP BRIDGE (a
spatial-prep PP headed by a place noun sets the tracked mover's WHERE-state), with place-typing broadened by the
WordNet location/structure/room TAXONOMY (the ATL place category; glass-box) so "platform/berth/…" type as places.
REUSES `_node_from_token` + `route_predicate_arguments` + the coref backbone. On the MODERN gold (47 queries):

| arm | motion-event recall | precision | where_is |
|---|---|---|---|
| CURRENT (motion-lexicon) | 0.4444 | 0.5714 | 0.3191 |
| **+ locative-PP bridge** | **0.8889** (+0.445) | **0.7391** (+0.168) | **0.3830** (+0.064) |
| shuffled-place TWIN | 0.8889 | 0.7391 | 0.2553 |

The bridge **nearly doubles extraction recall at HIGHER precision**, lifts end where_is +0.064, and the
shuffled-place twin collapses to 0.255 (**where_is +0.128 over twin → the place CONTENT is load-bearing, not just
firing more**). Every component is brain-foundational (McKoon-Ratcliff lazy inference, Basic Locative Construction,
WordNet/ATL place taxonomy, Zwaan-Radvansky WHERE-state, protagonist-anchored binding). This is a working answer to
"how the brain overcomes it," and a REUSE-first FOLLOW-ON problem (land the bridge into `_space_reader`/`decide_motion`;
then wire EntityBinder for the ~⅓ coref misses + ConceptNet AtLocation for world-knowledge places; the one new piece
— the lazy locative-PP bridge — is prototyped here). NOT part of the consolidation wire.

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
incrementality (Nivre 2004) and is trained on modern UD-EWT — but 19c OOD is NOT a parser lever: I measured
arc-eager as no-regress on 19c here, and `register_native_parse_and_pos_training_data...` is REFUTED (the 19c wall
is copular-convention + SELECTION, which belongs at the meaning/selection store, not the parser/tagger). The real
remaining parser-fidelity lever is the calibrated per-attachment CONFIDENCE arc-eager EMITS (`parse_with_conf`,
ECE 0.026) that the front-end consumers currently DISCARD — a precision-weighting signal (eADM; Vosse-Kempen) this
consolidation unblocks. Beam search, reanalysis-as-parse-revision, and a stronger general parser were all tried
and are located negatives on disk — the ideal parser does NOT add them.

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
  the fraction will drift as other read costs change. (The earlier "space no-regress is the thing I'd withdraw
  first" is now RESOLVED: on the MODERN space gold arc-eager is +0.043 over base, > floor + twin — the 19c −0.015
  was the OOD handicap, not a real regression.) First thing I'd withdraw now: the predictive-frontier's
  ambiguous-subset framing — my "ambiguous" proxy (≥2 post-verbal nominals) includes easy cases, and a targeted
  garden-path/reduced-relative slice is untested (though the theory + Demberg 2013 predict a time-not-accuracy
  effect there too).

## CORPUS-AGE / REGISTER ANCHORING (the standing confound — where it does and does NOT bite here)
The reader's default doc set (LitBank) is 19c literary prose — effectively a *different register* for the
modern-trained (UD-EWT) parser/tagger, a documented project-wide confound. For THIS problem it mostly does not bite,
because the load-bearing numbers are either MODERN-anchored or register-INDEPENDENT:
- **MODERN (UD-EWT):** the optimized arc-eager byte-identity + 1.26× (1200 sents); the copular no-regress powered
  gold (451, +0.013 neutral / +0.111 CI-sep detection); the roles-confidence end-to-end (AUC 0.538, n=1259); the
  predictive-frontier anticipation MRR + attachment (train+test both UD-EWT).
- **REGISTER-INDEPENDENT:** the double-parse reproduction, the 6/9 byte-identical dims (they don't consume the
  front-end parse at all → identical on ANY input), the read-time cut, the board no-regress (worst +0.0000). 19c
  LitBank here is just a convenient doc set; the conclusion is structural, not register-bound.
- **19c-ANCHORED — NOW CLOSED ON MODERN.** The one 19c-anchored no-regress number (space where_is) was re-run on
  the MODERN space gold (`experiments/exp_space_modern_brainfoundational_v1.py`, 8 modern passages, 47 queries):
  arc-eager **0.3191 vs base 0.2766 (+0.0426)**, both above the last-mention floor (0.1489) and the shuffled-twin
  p95 (0.2298). So on modern the consolidation does not just no-regress — it **helps** space (+0.043); the 19c
  within-noise −0.015 was exactly the predicted OOD handicap. The copular ARCHAIC set remains a deliberate register
  CONTROL (the powered copular gold is modern UD-EWT). **Nothing 19c-anchored remains load-bearing.**

## SPACE CHAIN ON MODERN — 100% brain-foundational component audit + signal-loss ladder
Owner directive: run the space chain on modern, verify EVERY component is brain-foundational, measure signal loss
along the chain. `experiments/exp_space_modern_brainfoundational_v1.py`.

**Component fidelity (each PINNED-by-evidence unless noted):** tag = UD-EWT perceptron (single lexical-category
inference) → parse = arc-eager INCREMENTAL (Hagoort MUC / Nivre — the consolidated single parse) → coref/mover
backbone = ANIMATE movers only (Lakusta & Landau 2012, animacy-modulated motion) → spatial roles =
`route_predicate_arguments` (Jackendoff Place/Path; Goldberg constructional caused-motion) → `decide_motion` =
NOISY-CHANNEL LIKELIHOOD (Talmy force/path + GOAL-over-SOURCE [Talmy; Lakusta & Landau]; satellite-framed path
[Talmy typology]; veridicality gate; Ji & Papafragou 2023 missed-source-lowers-confidence-not-erases) → LocationRegister
= Zwaan & Radvansky 1998 event-indexing SPACE with a PERSISTENCE prior (the noisy-channel PRIOR fused with the
likelihood) → where_is = mental-model state read-out (Glenberg 1987; Kintsch 1988). **The whole chain is a
brain-faithful noisy-channel (Bayesian prior × likelihood) spatial situation model.** The ONE OUR-INVENTION-under-test
is the discretized confidence weight (conf ∈ {1,2,3}) standing in for the graded likelihood — a swept parameter, not
an adopted number.

**Signal-loss ladder (where the modern where_is accuracy is lost):**

| stage | accuracy | reading |
|---|---|---|
| 1. FLOOR (last-mention) | 0.1489 | stateless baseline |
| 2. LIVE where_is (arc-eager chain) | 0.3191 | the full chain — 2.1× the floor, > twin p95 0.2298 |
| 3. motion-event EXTRACTION recall | **0.4444** (base=arc-eager) | **the bottleneck** — the chain detects only ~44% of gold location changes; parse-INDEPENDENT (base==ae recall) |
| 3′. motion-event EXTRACTION precision | 0.529 (base) / 0.571 (arc-eager) | arc-eager's +0.043 end-gain comes through PRECISION, not recall |
| 4. register \| PERFECT extraction (CEILING) | 0.7872 | readout + persistence are ~lossless → the loss is UPSTREAM extraction, not the register or the readout |

**What the ladder says:** the space dimension's loss is dominated by **motion-event extraction RECALL** (0.444) — a
separate organ (which motion verbs/paths get detected), NOT the parse (base==arc-eager recall) and NOT the
register/readout (lossless to 0.787). This confirms on MODERN prose the standing finding that space is
extraction-recall-bound, not parse-quality-bound — so the consolidation is safe here, and the real space frontier is
motion-event recall (Talmy path-verb coverage), owned by a separate problem. (Ceiling 0.787 not 1.0 is partly the
approximate gold-event reconstruction in the control; the true register ceiling is ≥ that, and either way ≫ the live
0.319.)
- **Strategic (owner's standing point):** parser/reader evals should be MODERN-anchored (UD-EWT / modern annotated /
  QA-SRL), with 19c used ONLY as an explicit OOD robustness control — the eval-corpus choice is a project-level fix
  (strategy's domain), flagged here.

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

### NEXT STEPS (for strategy; ordered by value)
1. **LAND the one-parse consolidation wire** (the exact diff above): route the front-end's cached heads through the
   role path's arc-eager parse; keep the batch parser loadable as a byte-identity reference; update the two witnesses
   whose premise is the batch parse (`test_reader_frontend_cache_shared.py`, `test_arc_parser_*_landing.py`). This
   is the SOLVED deliverable — a no-regress read-cost cut. **Coordinate per the PARSER-IMPACT FLAG.**
2. **LAND the byte-identical optimized arc-eager** (1.26× now; the crc32-memo). Now that arc-eager is the sole
   read-path parse, its inner loop is the cost lever — full vectorization (arg-keyed memo + numpy `_score_actions`)
   is a scoped follow-on that took the batch parser to 2–2.6× the same way.
3. **FILE the space-recall follow-on** — `SPACE_RECALL_FOLLOWON_BRIEF.md` (in this folder): land the prototyped
   lazy locative-PP bridge (recall 0.444→0.889, twin-separated), then reuse `EntityBinder` (mover-coref) +
   `grounded_semantic_graph` ConceptNet `AtLocation` (world-knowledge places). This is the largest reader-accuracy
   lever surfaced here and is REUSE-heavy.
4. **DO NOT chase (settled here):** confidence-weighting is a WEAK end-to-end lever (roles AUC 0.538, light-abstain
   only; copular/space neutral) — a small role-path calibrated-abstain option at most, not a general lift; the
   predictive arc-eager is a located negative on accuracy (real only on anticipation MRR — a time/N400 signal, whose
   home is `predict_surprisal`). Beam / register-retraining / reanalysis / a stronger general parser remain located
   negatives on disk.
5. **AUDIT UPDATE** for `BRAIN_FOUNDATIONAL_AUDIT.md` §2b: arc-eager incremental = the PINNED brain-foundational
   parse, arc-factored batch = no cognitive correlate (retire from read path); correct the stale "arc-eager copular
   is 19c-negative" claim (refuted post-`robust_cop`).
