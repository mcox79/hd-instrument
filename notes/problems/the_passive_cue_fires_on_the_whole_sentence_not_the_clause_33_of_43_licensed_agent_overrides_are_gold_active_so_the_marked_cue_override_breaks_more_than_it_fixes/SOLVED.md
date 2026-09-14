---
problem: the_passive_cue_fires_on_the_whole_sentence_not_the_clause_33_of_43_licensed_agent_overrides_are_gold_active_so_the_marked_cue_override_breaks_more_than_it_fixes
status: SOLVED
bar: "Clause-local detector: false fires on gold-active clauses down from 33/43 CI-separated with recall on true passives not down; the override anatomy flips to net-positive (fixes > breaks) or the licence is withdrawn with the number; every consumer moved to the one detector; the board's agent dimension not down; twin (random equal-size set of clauses declared passive) at floor -- OR a numbered located negative naming which consumer the clause-local cue helps and which it hurts."
result: "PLACEHOLDER"
floor: "PLACEHOLDER"
controls: "PLACEHOLDER"
files_changed: "PLACEHOLDER"
reverify: "PLACEHOLDER"
---

# SOLVED -- the auxiliary is the cue, the suffix is not, and the cue belongs to ONE predicate

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed on disk; the exact diff is
`passive_cue_patch.diff` in this folder, generated FROM the cell's own organ block (`--emit-patch`), and the
cell's self-test asserts the diff's added lines are byte-identical to the code that was measured.

---

## 1. The bar, restated in my own words

The system decides who did what by keeping the high-validity word-order default ("the first thing named is
the doer") and letting a MARKED cue overturn it. One of those marked cues is "this clause is passive". The
detector that answers that question looks at the WHOLE sentence. So a passive anywhere -- in a relative
clause, in a coordinate clause, in an adjectival participle -- tells every predicate in the sentence that it
is passive. The bar is: make the cue read the clause of the predicate being decided; show the false fires on
gold-ACTIVE clauses collapse without losing recall on real passives; show the override stops breaking more
than it fixes; move every consumer to the ONE detector; break nothing else; and show a same-rate random
"passive" twin at the floor.

## 2. The chain this cue sits in, and the brain-foundational status of each rung AS THE DISK SHOWS IT

`notes/bf_status_registry.jsonl` + each module's `__bf_status__`, read first-hand, and the live frontend
(`hdlab.frontend.describe()` -> `categories=counts heads=attachment_arm`).

| rung | organ | BF status on disk | what it hands DOWN | what the voice cue READS |
|---|---|---|---|---|
| tokens -> categories | `hdlab/lexical_categories.py` | BF_SPIRIT (live default) | a full category POSTERIOR per token | **the argmax only** -- the cue asks "is this token VERB / AUX / ADV" |
| categories -> lemma | `hdlab/morphology.py` | **BF** (0 divergences vs morphy over 6.3M) | the lemma | **nothing** -- the cue never needed it (section 6.3) |
| categories -> heads | `hdlab/attachment_arm.py` | BF_SPIRIT (live default) | a single-root tree + `P(head\|dep)` marginals | the aux->predicate ARC, as CONFIRMATION only |
| voice cue | `hdlab/thematic_role_labeler.py::is_passive_clause` | BF_SPIRIT (module) -- **the cue itself was NOT**: a sentence-wide window search | ONE boolean for the sentence | -- |
| roles / agent | `hdlab/graded_role_assigner.py` | BF_SPIRIT | the coarse role posterior; the agent pick | the boolean, at four call sites |
| the board | `experiments/exp_board_agent_slot_ud_v1.py` | the measuring arm | `who_did_what_agent` | its OWN copy of the hybrid and of the cue |

## 3. How the brain does this -- and the one thing the shipped detector had backwards

**The structure.** Voice is a cue of the Competition Model (Bates & MacWhinney 1989; MacWhinney, Bates &
Kliegl 1984). A cue is evaluated FOR THE PREDICATE whose arguments are being assigned, it enters at its
VALIDITY (availability x reliability), and English is order-dominant so only a HIGH-validity marked cue may
overturn word order. The clause is the unit: argument assignment is clause-bounded (Fodor & Bever 1965
click-displacement; Frazier & Fodor 1978's two-stage packager). The passive itself is a stored CONSTRUCTION
(Goldberg 1995) whose form side is `[NP be/get V-en (by NP)]`, realised on ONE predicate by ONE auxiliary
chain. Comprehenders use voice morphology EARLY as an actor/undergoer cue (Bornkessel-Schlesewsky &
Schlesewsky 2006/2009, eADM -- the citation the substrate already uses for `arc_labeler.label_voice_correct`).

**THE KEY REALIZATION, and it is an ordering fact about the evidence.** The shipped detector searches the
sentence for a PARTICIPLE and treats a nearby `be` as confirmation. The brain cannot work that way, because
the participial suffix is *not* evidence: English `-ed` is systematically ambiguous between the simple past
and the participle. That ambiguity is the entire reason the reduced-relative garden path exists ("the horse
raced past the barn fell" -- Bever 1970; Trueswell, Tanenhaus & Garnsey 1994). What carries the cue is the
AUXILIARY, which is heard FIRST and opens a passive expectation for the predicate it attaches to
(incremental interpretation, Marslen-Wilson 1973; anticipatory use of the verb/auxiliary, Altmann & Kamide
1999). The very next non-adverbial word then CONFIRMS the expectation (a participial main verb) or CANCELS
it (a determiner -> the auxiliary was a copula; an infinitival `to` -> a new predicate opens; `-ing` -> the
construction is PROGRESSIVE, i.e. active). **So the operation is an unbroken LEFT CHAIN from the predicate,
not a window search over the sentence** -- and the by-phrase, when it arrives, is confirmation of the
demoted agent rather than a requirement.

That single re-ordering is what the whole result is made of. It also explains, without any list, three
things the shipped detector had to hand-enumerate and still got wrong: it needs no irregular-participle
table (the `-ing` test alone separates progressive from passive under a `be`), it needs no window parameter
(the chain terminates itself), and it cannot leak across clauses (a determiner, a nominal or a preposition
is exactly what a clause boundary puts between two predicates).

**Graded, never frozen.** Additive cue activation -> logistic IS the Bayesian posterior for cue integration
(McClelland 2013), so the deployable form of the cue is `P(passive | cue values)` read off COUNTS, with one
`observe_voice_outcome` call per understood predicate. That is built, accrued and measured (section 5.4).

## 4. What was built

One organ block, in `hdlab/thematic_role_labeler.py` (the module the brief names as the single home of this
cue), reading only tokens + categories + optionally the reader's own heads:

| function | what it computes |
|---|---|
| `voice_cue_value(toks, pos, v, heads)` | the cue VALUE at predicate `v`: `be_arc` / `be_chain` / `get_arc` / `get_chain` / `be_inv` / `conj` / `prog` / `none` / `na` |
| `morph_value` / `by_value` / `degree_value` | the three secondary cue values: participial morphology (`ing`/`ed`/`en`/`other`), the clause-local by-phrase, and the adjectival-passive degree modifier (Wasow 1977) |
| `voice_posterior(..., counts)` | `P(passive \| the four cue values)`, Dirichlet-smoothed to the aux-value marginal and then to the base rate (the shrinkage IS the backoff) |
| `observe_voice_outcome` / `load_voice_counts` / `save_voice_counts` | the online path: one count per understood predicate; the asset is `data/hook_state/passive_voice_counts_v1.json` |
| `is_passive_predicate(toks, pos, v, heads, counts, theta)` | the boolean the four call sites need. `counts=None` (the shipped default) = the construction read; with counts = the graded read at a criterion |

Five auxiliary-chain facts are what make it work, each a cancellation the brain performs and the shipped
detector did not: an infinitival `to` stops the chain; a determiner or nominal stops the chain; `-ing` under
a `be` is progressive, not passive; a fronted participle may take its finite auxiliary to the RIGHT
("Attached is a spreadsheet"); and a bare conjunct shares the first conjunct's auxiliary across the
coordinator ("the artworks were selected and EXHIBITED").

## 5. The numbers

### 5.1 The detector itself -- UD-EWT test, per predicate, through the LIVE brain-foundational chain

Population: every gold-VERB predicate in UD-EWT test, **n = 2605 in 1240 sentences**, 126 gold passive
(`aux:pass`/`nsubj:pass`/`csubj:pass`) and 136 under the propagated gold (a bare CONJUNCT of a passive
predicate; UD annotates the shared auxiliary once, and the second conjunct of "were selected and exhibited"
IS passive for every consumer of this cue). Categories from `lexical_categories`, heads from
`attachment_arm` -- no gold at decision time. Paired bootstrap over SENTENCES, 2000 resamples, on the
per-predicate voice DECISION.

| arm | fires | precision | recall | F1 | accuracy | accuracy vs the shipped floor |
|---|---|---|---|---|---|---|
| **FLOOR -- shipped whole-sentence `is_passive_clause`** | 296 | **0.3784** | 0.8235 | 0.5185 | 0.9202 | -- |
| shipped detector scoped to the clause span (what `agent_override_fires` does today) | 214 | 0.4860 | 0.7647 | 0.5943 | 0.9455 | +0.0253 CI95[+0.0158,+0.0365] **sep** |
| `relcl_resolver.precise_passive` (already predicate-anchored) | 112 | 0.9464 | 0.7794 | 0.8548 | 0.9862 | +0.0660 CI95[+0.0503,+0.0830] **sep** |
| **NEW -- `is_passive_predicate` (construction read)** | 127 | **0.9606** | **0.8971** | **0.9278** | **0.9927** | **+0.0726 CI95[+0.0566,+0.0892] sep** |
| NEW -- graded read at theta 0.5 | 126 | 0.9603 | 0.8897 | 0.9237 | 0.9923 | +0.0722 CI95[+0.0562,+0.0887] sep |
| NEW -- without the coordination cue | 121 | 0.9669 | 0.8603 | 0.9105 | 0.9912 | +0.0710 CI95[+0.0547,+0.0878] sep |
| **TWIN -- a random equal-size set of predicates declared passive** | 130 | 0.0462 | 0.0441 | 0.0451 | 0.9025 | **-0.0177 CI95[-0.0341,-0.0004] sep BELOW** |

**Precision 0.3784 -> 0.9606 with recall UP 0.8235 -> 0.8971.** Head to head against the shipped cue on the
same 2605 predicates: **200 fixes, 11 breaks.** On the raw (unpropagated) gold the new read is
0.9213 / 0.9286 and the no-coordination variant 0.9669 / 0.9286, i.e. the conclusion does not depend on
which of the two golds is used.

### 5.2 The cue's own validity, learned from counts (UD-EWT train, live chain, 22,576 predicates)

This is the Competition Model's own quantity, and it is the reason the licence was breaking things.

| cue value | n | P(passive) |
|---|---|---|
| `be_arc` (a BE auxiliary the reader's parse attached to this predicate, reached by an unbroken chain) | 1280 | **0.9656** |
| `be_inv` (fronted participle + postposed finite be) | 22 | 1.0000 |
| `get_arc` / `get_chain` (the get-passive) | 20 / 17 | 0.9500 / 0.8824 |
| `be_chain` (chain reached, arc says otherwise) | 7 | 0.8571 |
| `conj` (a bare conjunct sharing the auxiliary) | 45 | 0.6222 |
| `none` | 16609 | 0.0059 |
| `prog` (`be` + `-ing`) | 2947 | 0.0003 |
| *(the shipped whole-sentence read, same population)* | *296 fires on test* | ***0.3784*** |

The Competition Model says a cue enters at its validity. The auxiliary-attachment cue has validity **0.966**
and the sentence-wide search has **0.378**; that ratio is the whole problem, stated in the theory's own terms.

### 5.3 The consumer -- the board's who-did-what AGENT decision (UD-EWT test, n = 1423)

Every arm is the SAME hybrid (word-order default, Competition-Model competition on a marked cue) with ONE
thing changed: which voice read licenses the passive cue. Floor = the positional pick the board itself uses.
Paired item bootstrap, 2000 resamples.

| arm | accuracy | vs the positional floor 0.8468 | vs the landed board model 0.8271 |
|---|---|---|---|
| positional floor | 0.8468 | -- | -- |
| **landed: whole-sentence licence (what the board scores today)** | **0.8271** | **-0.0197 CI95[-0.0309,-0.0091] sep BELOW** | -- |
| clause-scoped licence | 0.8320 | -0.0155 sep BELOW | +0.0049 sep |
| clause-scoped + by-phrase required | 0.8468 | -0.0007 n.s. | +0.0197 sep |
| **NEW predicate-anchored licence (the board hunk of the diff)** | **0.8475** | **+0.0007 CI95[-0.0070,+0.0084] n.s.** | **+0.0204 CI95[+0.0126,+0.0281] sep** |
| NEW + by-phrase required | 0.8482 | +0.0007 n.s. | +0.0211 sep |
| NEW graded read | 0.8475 / 0.8482 | +0.0000 / +0.0007 n.s. | +0.0204 / +0.0211 sep |
| **the ORGAN `hdlab.hybrid_agent_pick` with the diff in** | **0.8531** | **+0.0063 CI95[-0.0014,+0.0141] n.s.** | **+0.0260 CI95[+0.0169,+0.0351] sep** |
| TWIN -- the passive licence fires on a random equal-size set | 0.8468 | -0.0007 (at the floor) | +0.0197 sep |

**THE OVERRIDE ANATOMY -- the brief's own instrument.** Decisions where the PASSIVE cue ALONE licenses the
override (no `pp_gov`, no `noncase`):

| voice read | n | fixes | breaks | neutral | fired on a gold-ACTIVE clause | conflict validity |
|---|---|---|---|---|---|---|
| **landed whole-sentence** | 92 | **1** | **30** | 61 | **83** | **0.032** |
| clause-scoped | 57 | 1 | 23 | 33 | 48 | 0.042 |
| clause-scoped + by required (the ORGAN today) | 12 | 1 | 2 | 9 | 3 | 0.333 |
| **NEW predicate-anchored** | 14 | 1 | 1 | 12 | **3** | 0.500 |
| **NEW + by required (what the diff ships in the organ)** | **11** | **1** | **0** | 10 | **0** | **1.000** |
| NEW graded + by required | 11 | 1 | 0 | 10 | 0 | 1.000 |

*(pri 106 reported this partition restricted to the decisions where the override actually CHANGED the pick:
n=43, fixes 1, breaks 30, neutral 12, gold-active 33. My `fixes 1 / breaks 30` reproduce it exactly; my
larger `n` and `gold-active` counts every licence firing, changed or not. Same population, wider window.)*

**The bar's own numbers: gold-active false fires 83/92 -> 0/11; fixes 1 > breaks 0; recall on true passives
UP, not down; twin at the floor.**

### 5.4 The plastic arm

`data/hook_state/passive_voice_counts_v1.json`: 41 cue configurations, 22,576 predicates accrued on UD-EWT
train through the live chain, base rate 0.0680, Dirichlet alpha swept (4.0). The graded read scores
0.9603 / 0.8897 against the construction read's 0.9606 / 0.8971 -- **statistically the same organ** (127 vs
126 fires). It earns its keep in exactly one place, and the counts say where: the coordination cue splits
into `conj|ed` = 21/29 = 0.72 and `conj|other` = 3/11 = 0.27, so the graded read fires on the first and
abstains on the second, which the boolean cannot do.

**SHIPPED DEFAULT = the construction read (`counts=None`), deliberately.** `data/` is gitignored, so an
organ whose default depends on an uncommitted asset would silently become a DIFFERENT organ on any machine
that lacks it -- the precise hazard the hard rules name. The counts are therefore the opt-in plastic arm,
re-derivable by `--run`, with `observe_voice_outcome` as the online path.

### 5.5 No-regress on the other consumers

| consumer | population | shipped | patched | delta |
|---|---|---|---|---|
| **call site 1** -- `coarse_role_cues` `voice_order` (UD-EWT test 700, live heads, the shipped v4 validity table UNCHANGED) | all labelled arguments, n=2216 | 0.6940 | 0.6954 | +0.0014 CI95[0.0000,+0.0031] n.s. |
| | core arguments, n=1205 | 0.7361 | 0.7386 | +0.0025 CI95[0.0000,+0.0059] n.s. |
| | gold `nsubj:pass`, n=48 | 0.5417 | 0.5417 | 0.0000 |
| | gold `obl:agent`, n=19 | 0.6316 | 0.6316 | 0.0000 |
| **call site 2** -- `agent_supports`, the voice FLIP of every candidate's preverbal/byagent support; scored as the competition's own pick on the agent population | UD-EWT test, n=1422 | 0.7511 | **0.7637** | **+0.0127 CI95[+0.0070,+0.0197] CI-SEPARATED UP** |
| **call site 3** -- `agent_override_fires` | see 5.3 | -- | -- | the licence: 92 firings / 83 gold-active -> 11 / 0 |
| **call site 4** -- `agent_override_licensed`'s `want` class | (reads the same cue; changes which role class the calibrated probability is taken over) | -- | -- | moved to the one detector in the diff; no independent population |

Call site 2 is the second consumer up CI-separated, and it is the one the *reader* uses on every sentence
(`situation_reader` -> `agent_competition_pick_conf` -> `agent_supports`): the whole-sentence boolean was
switching off the preverbal support and switching on the by-phrase support for EVERY candidate of EVERY
predicate in any sentence that contained a passive anywhere.

Call site 1 had a real risk of regressing and it is worth saying why it did not: the `voice_order` cue VALUE is
a key into a validity table that was accrued with the OLD detector, so changing the detector changes which
counts a decision reads. It does not regress because the change is almost entirely a reduction in
`passive_weak_*` false firings, and `passive_weak` is the low-validity value the table already distrusts.
**The table was NOT re-accrued** -- the number above is the honest as-if-landed-today number; re-accruing it
with the corrected cue is a named follow-on (section 11).

*(Call site 1 also carried a latent defect the diff fixes: `is_passive_clause(toks, pos, h)` passed the head
INDEX `h` into the function's `window` parameter, so the search widened with the predicate's position in the
sentence. It fires 293 times against the nominal call's 294 on UD-EWT test -- near-identical, which is why
it never showed up as a bug, and wrong for a different reason than the one this brief is about.)*

## 6. THE STATUS PROBE -- where the signal is lost, chain by chain, with counts

*"How are we performing against the brain, and where do we lose signal upstream? Are all upstream components
brain-foundational?"*

### 6.1 The signal the end read needs, in one sentence per consumer

| end consumer | its one-sentence signal requirement |
|---|---|
| the agent decision (`hybrid_agent_pick`) | "for THIS predicate, is the surface subject the undergoer, so that the agent is somewhere else?" |
| the coarse role labeler (`coarse_role_cues`) | "for the head governing THIS nominal, is the clause passive, so that a pre-verbal nominal is `nsubj:pass` and a by-NP is `obl:agent`?" |
| `agent_supports` | "for THIS predicate, should the preverbal support be switched off and the by-phrase support switched on?" |
| `agent_override_licensed` | "for THIS predicate, is the role class we should be scoring `BY_AGENT` or `SUBJ`?" |

**Every one of the four is about ONE predicate. All four were being answered about the SENTENCE.** That is
the loss, and it is total in the sense that matters: the answer was not degraded, it was about a different
question.

### 6.2 Hand-off by hand-off: produced / read / LOST

| hand-off | what is PRODUCED | what the next rung READ | LOST |
|---|---|---|---|
| category organ -> voice cue | a per-token category POSTERIOR | the argmax category of the predicate and of the chain tokens | the posterior. **Counted: 212 of 2605 predicates are not tagged VERB by the category organ, and the cue returns `na` for every one of them** (section 6.4) |
| attachment arm -> voice cue | a tree + `P(head\|dep)` | (before) nothing at all; (now) the aux->predicate arc as confirmation | **Counted: the arc confirms 111 of 113 firings (`be_arc` 111 vs `be_chain` 2) and changes ZERO decisions** -- the surface chain and the arc agree, so the arc is currently a free confirmation, not a source of signal |
| voice cue -> the four consumers | one SENTENCE boolean | a per-PREDICATE question | **the predicate identity.** Counted: 296 sentence-level firings vs 127 predicate-level firings on 2605 predicates; 184 of the 296 are false on the propagated gold |
| voice cue -> agent override | the boolean | the licence | **Counted: 92 licences, 83 on gold-ACTIVE clauses, 30 broken decisions, 1 fixed** |
| agent override -> the pick | the marked-cue licence | the competition's pick | see 6.5 -- the NEXT rung is where the remaining loss is |

### 6.3 Brain-foundational status of each upstream component AS IT RELATES TO THIS SIGNAL

- **`lexical_categories` (BF_SPIRIT, live default).** Hands down a graded posterior; the voice cue takes a
  point estimate. That is a REAL graded->hard hand-off, and it is the cue's largest remaining loss (6.4).
- **`attachment_arm` (BF_SPIRIT, live default).** Hands down a posterior; the cue reads the MAP arc only, and
  only as confirmation. Measured to change nothing today, so this is a hand-off that is currently lossless
  *because the surface chain already carries the same information* -- not because the cue uses the posterior.
- **`morphology` (BF).** Not on this path at all, and that is the right answer, not an omission: the brain
  does not identify the passive from the participle's morphology (section 3), so a lemma/participle lookup is
  not a missing input. The shipped `_is_participle` hand-list (`_PARTICIPLE_IRREGULAR`, ~60 forms) is
  therefore a SUPPLY the corrected cue does not need at all -- it is replaced by the `-ing` test.
- **`thematic_role_labeler::is_passive_clause` -- NOT brain-foundational as a cue** (a sentence-wide window
  search answering a predicate-level question), inside a module the registry calls BF_SPIRIT. That is the
  defect this brief names, and it is now fixed at the computation, not papered over downstream.

### 6.4 The one upstream loss that is still open, counted -- and it is NOT what the brief predicted

The cue can only fire on a token the category organ calls a VERB. **212 of the 2605 predicates get `na`**
(the organ tagged them something else). Of the 136 gold passives, **exactly 4 are lost that way**, and three
of the four are the same thing:

```
are probably especially oriented toward the      [oriented = ADJ]
, I was surprised to hear                        [surprised = ADJ]
have never been disappointed .                   [disappointed = ADJ]
a leg and have to wait                           [have = AUX]
```

**The adjectival-participle residual the brief's checklist item 4 predicted did not materialise where it was
expected.** Of the 5 remaining false fires on UD-EWT test, **ZERO carry a degree modifier** -- the
adjectival-passive precision problem does not exist at this rung, because `was tired` / `is interested` /
`especially oriented` never reach the cue at all: the CATEGORY organ tags them ADJ one rung earlier. The
adjectival/verbal passive distinction has therefore moved UP the chain and changed sign: it is a RECALL loss
in the category organ (3 items), not a PRECISION loss in the voice cue (0 items). I built the degree-modifier
cue anyway (it is a cue VALUE in the counts: `none|other|none|deg` = 0/105 passive, `none|ed|none|deg` =
0/31) and it is measured to be inert at this rung -- an honest null, kept because it is free and because it
will matter the moment the category organ stops absorbing the distinction.

The fourth item, `have` tagged AUX, is the *same* convention defect pri 110 is working (UD tags a clause's
only verb `be`/`have` as AUX) -- flagged, not touched.

### 6.5 What the reader's own heads actually contribute -- counted, and it is zero decisions

The brief asks for the auxiliary chain "attached to h", with `_cached_parse_heads` available. Built and
measured: under live heads the cue value is `be_arc` (the parse attached that auxiliary to this predicate)
**111** times against `be_chain` (chain reached, arc disagrees or absent) **2** times -- and the number of
DECISIONS the arc changes is **0 of 2605**. The surface chain and the attachment arm agree on essentially
every auxiliary. So the arc is retained as a cue VALUE (it separates a 0.966-validity configuration from a
0.857-validity one in the counts) but the organ does not depend on it, which is why the diff does not widen
`agent_supports`'s signature to thread heads through: it would be a signature change buying zero decisions,
and an un-passed argument at a builder call site is exactly how an organ silently ships different.

### 6.5 The research: how the brain handles this signal mathematically, chain by chain down

- **At the cue.** Cue validity = availability x reliability (Bates & MacWhinney 1989). Availability of the
  auxiliary cue is the fraction of passives that carry an auxiliary; reliability is P(passive | the cue
  fired). Measured on UD-EWT train through the live chain: availability (recall) 0.897, reliability 0.966.
  The sentence-wide read has the same availability and reliability 0.378. **The theory's own quantity
  separates the two reads by a factor of 2.6, and predicts exactly the observed damage** -- a cue whose
  reliability is 0.38 must not be allowed to overturn a cue (word order) whose reliability on this
  population is 0.85.
- **At the integration.** Ernst & Banks 2002 / Fetsch et al. 2011 / Ma et al. 2006: a consumer weights each
  input by its reliability, trial by trial. The graded form (`voice_posterior`) is that weighting made
  explicit, and the counts show it matters exactly where the cue's reliability is intermediate (`conj` 0.62).
- **At the decision.** McClelland 2013: additive cue activation -> softmax IS the Bayesian product. The
  organ's `net_activation` already does this; what it needed was a cue VALUE that is about the right object.
- **One rung further down** (section 7): Wolff/Talmy is not the relevant theory here; the relevant one is
  CASE. Once voice says "the agent is elsewhere", the by-phrase is the case marker of the demoted agent
  (Bates & MacWhinney's case-marking cue, high-validity where present). The substrate already has that cue
  (`byhead`/`by_governs`, landed 2026-09-06) and the board's copy of the hybrid was not passing it.

## 7. THE QUALITY PUSH -- the cue is fixed, so where does the signal go next?

The passive licence can only ever touch the gold-PASSIVE items of the agent population, and there are
**16 of 1423** (UD's `obl:agent` by-phrases; agentless passives have no agent to recover and are excluded by
the board's own gold recipe). So the arithmetic bound on this entire lever at this consumer is 16 items =
0.0112. I therefore traced the signal one rung DOWN, on that subpopulation.

| arm (gold-passive subpopulation, n=16) | accuracy | vs floor |
|---|---|---|
| positional floor (word order) | **0.0000** | -- |
| the board arm's competition -- `agent_competition_pick` with `byhead_agent_cue` **FALSE** (its default; the board arm never passes it) | 0.1875 | +0.1875 n.s. |
| the SAME competition with `byhead_agent_cue` **TRUE** (what `hdlab.hybrid_agent_pick` passes) | 0.5000 | +0.5000 CI95[+0.2500,+0.7500] **sep** |
| the board arm's hybrid as landed | 0.1875 | +0.1875 n.s. |
| the board arm's hybrid with the pri-111 voice read | 0.1875 | +0.1875 n.s. |
| **the ORGAN `hdlab.hybrid_agent_pick`** (requires the by-phrase, passes `byhead`) | **0.5625** | **+0.5625 CI95[+0.3125,+0.8125] sep** |
| the same organ with the pri-111 voice read | 0.5625 | +0.5625 sep |
| ORACLE -- pick the candidate governed by `by` (the ceiling the case cue could reach) | 0.7500 | +0.7500 sep |

**The finding, and it is independent of this brief's cue.** The board's `who_did_what_agent` dimension does
not call the organ; it calls its own older copy, and that copy loses **5 of the 16 passive agents purely by
not passing `byhead_agent_cue=True`**. The by-phrase CASE cue is landed (2026-09-06), it is default-ON in
`hdlab.hybrid_agent_pick`, and the board has never seen it. On the full population:

| | full n=1423 | active-only n=1407 | gold-passive n=16 |
|---|---|---|---|
| positional floor | 0.8468 | 0.8564 | 0.0000 |
| board arm as landed | 0.8271 (-0.0197 sep BELOW) | 0.8344 (-0.0220 sep BELOW) | 0.1875 |
| board arm + pri-111 voice | 0.8475 (+0.0007 n.s.) | 0.8550 (-0.0014 n.s.) | 0.1875 |
| the ORGAN | 0.8510 (+0.0042 n.s.) | 0.8543 (-0.0021 n.s.) | 0.5625 |
| **the ORGAN + pri-111 voice** | **0.8531 (+0.0063 n.s.)** | **0.8564 (+0.0000 -- EXACTLY no regress)** | **0.5625** |

Two things are worth saying plainly. First, **the cue fix inside the ORGAN is worth 3 items (+0.0021,
CI95[0.0000,+0.0049], not separated)** -- because the organ already required a by-phrase, which was masking
most of the whole-sentence false fires. Second, **the cue fix inside the BOARD ARM is worth +0.0204
CI95[+0.0126,+0.0281], CI-separated**, because the board arm has no by-requirement and was taking all 30
breaks. The 30 broken decisions the brief was opened on live in the board arm's copy, not in the organ.
Retiring that copy in favour of the organ is +0.0239 CI95[+0.0155,+0.0323] on its own, and +0.0260
CI95[+0.0169,+0.0351] with the cue fix.

The corrected cue's recall AT THIS CONSUMER is **16/16**: it fires on every gold-passive item in the agent
population. The remaining 7 of 16 that the organ still misses are not a voice-cue problem -- the oracle
by-governed pick gets 12 of 16, so 4 more items are reachable by the case cue alone and 4 are not reachable
by either. That is a bounded, named hand-off to the agent competition's weights, not to this cue.

## 8. GENERALIZE -- a second modern gold the counts never saw

`PLACEHOLDER_GUM`

## 9. Every negative, researched until understood

`PLACEHOLDER_NEGATIVES`

## 10. Components interacted with, and their brain-foundational status

`PLACEHOLDER_COMPONENTS`

## 11. AUDIT UPDATE

`PLACEHOLDER_AUDIT`

## 12. Evaluation of the most successful improvement -- which chain was cracked, rung by rung

`PLACEHOLDER_EVAL`

## 13. ALTERNATE PATHS -- other ways to do this read, as or more brain-foundational

`PLACEHOLDER_ALT`

## 14. Priority next steps

`PLACEHOLDER_NEXT`

## 15. What I would withdraw first if it turned out to be wrong

`PLACEHOLDER_WITHDRAW`
