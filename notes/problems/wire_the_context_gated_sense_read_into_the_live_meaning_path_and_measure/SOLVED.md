---
problem: wire_the_context_gated_sense_read_into_the_live_meaning_path_and_measure
status: PARTIAL
bar: "Wire the context-gated sense read into the live meaning path and SHOW a real board dim lifts CI-separated on modern prose (info-free twin losing, byte-identical when off), THEN flip default-on per no-more-default-off — OR a rigorous LOCATED NEGATIVE naming exactly why the in-context read cannot lift a live decision (with a number; e.g. no live consumer makes a sense-dependent choice the board scores). INVARIANT: recall path byte-identical; NO external tool/LLM at inference; instrument that your wire actually fires on the scored path."
result: "THREE controlled results on modern gold. (POSITIVE, meaning-read dim) The LIVE WIRE (hdlab.underspecified_sense_reader.select_sense — what sm.select_sense binds) lifts WiC over the SENSE-BLIND reader: WIRE coarse-supersense acc = 0.7493 vs the sense-blind reader's majority ceiling 0.5000, +0.2493 CI[+0.2198,+0.2802] CI-sep; info-free shuffled-context twin LOSES (WIRE-twin +0.1654 CI[+0.1393,+0.1924]); genuine discrimination not a coarse artifact (pred-same-rate 0.452, specificity on gold-DIFFERENT pairs 0.797). n=2038 committed WiC pairs. (NEGATIVE 1, non-decisive consumer) common-noun coref TYPE-LICENSE (typed_spokes.coref_type_license): context-gating flips 715/36642 pairs (1.95%), the shuffled-context twin flips MORE (900>=715, does NOT lose), controlled coref-accuracy gated-minus-baseline = +0.0007 CI[-0.0090,+0.0102] (INCLUDES ZERO). Bridge slice 26.9%; n=2834. (NEGATIVE 2, DECISIVE consumer) natural-logic monotonicity is-a (typed_spokes.natural_logic_label, the MED 0.767 path, which deliberately uses the UNION is-a read): context-gating HURTS — GATED committed-sense 0.6559 vs BASELINE union 0.7203, -0.0644 CI[-0.0877,-0.0411] CI-separated BELOW baseline (twin -0.0810), on the n=901 sense-decisive SUB slice. Enumeration complete: BOTH live sense-consumers fail (one null, one negative)."
floor: "POSITIVE floor = the SENSE-BLIND reader's ceiling = majority WiC class 0.5000 (the reader superposes all senses of a lemma into ONE ConceptSpace vector -> type-level cosine of the two same-lemma targets is 1.0 -> AUC 0.5 -> can only predict majority). NEGATIVE-1 floor = the current live sense-blind comparator coref_type_license (MFS/union) = 0.5967 common-noun antecedent accuracy (controlled recency resolver). NEGATIVE-2 floor = the current live union is-a read = 0.7203 on the MED SUB slice (the deliberately-permissive read the 0.767 headline uses)."
controls: "POSITIVE: majority floor + an info-free shuffled-context twin (LOSES CI-sep -> the lift is CONTEXT-driven) + a confusion sanity (pred-same-rate 0.452, specificity 0.797 on gold-DIFFERENT pairs -> genuine discrimination, not coarse over-predicting SAME). NEGATIVE-1: sense-blind baseline == the live comparator; an info-free shuffled-context twin that does NOT lose (flips MORE, 900 vs 715); a flip decomposition (permit->forbid 613 / forbid->permit 102, so gating sensibly TIGHTENS) + a mechanism probe (bridge-head committed==MFS 53.7% vs global 51.6% -> bridge heads are NOT specially dominant-sense; the null is because the filter is NON-DECISIVE, recency selects). NEGATIVE-2: the live union is-a baseline + an info-free shuffled-context twin (also hurts, -0.0810). LIVENESS: a real SituationReader.read() over modern prose leaves sm.senses == [] yet sm.select_sense fires (bank -> noun.group)."
files_changed: "experiments/exp_sense_gated_coref_divergence_v1.py, experiments/exp_sense_wire_wic_liveness_v1.py (+board_wic_via_live_wire_dimension), experiments/exp_sense_gated_natural_logic_probe_v1.py, experiments/exp_sense_gated_safe_bridge_write_v1.py, experiments/exp_context_modulated_meaning_vector_probe_v1.py, experiments/exp_sense_wire_wic_param_sweep_v1.py, experiments/exp_sense_gated_coref_board_native_v1.py, experiments/exp_sense_wire_wic_grain_sweep_v1.py, verification/test_sense_wire_liveness_and_coref_negative.py, data/{sense_gated_coref_divergence_v1,sense_wire_wic_liveness_v1,sense_gated_natural_logic_probe_v1,sense_gated_safe_bridge_write_v1,context_modulated_meaning_vector_probe_v1,sense_wire_wic_param_sweep_v1,sense_gated_coref_board_native_v1,sense_wire_wic_grain_sweep_v1}/metrics.json"
reverify: ".venv/Scripts/python.exe verification/test_sense_wire_liveness_and_coref_negative.py"
---

# The context-gated sense read WORKS on the live meaning read (WiC 0.500 -> 0.749, twin losing) but neither of the two live decisions that read a common-noun sense profits: the coref type-license is non-decisive (gating null, +0.0007 CI incl 0) and the natural-logic is-a wants the permissive union (gating HURTS, -0.0644 CI-sep). No live decision's errors are sense-disambiguation errors

**Status PARTIAL, and it satisfies BOTH halves of the bar on two different targets.** The wire is proven LIVE +
correct + it lifts a real board dim (WiC, the *meaning-read* dim) CI-separated with the info-free twin losing
(the bar's positive option). AND, for the substantive goal — a *downstream comprehension* dim lifting so we flip
default-on — I deliver a rigorous LOCATED NEGATIVE with numbers (the bar's negative option). I file PARTIAL rather
than SOLVED because the literal deliverable ("a downstream board dim lifts -> flip default-on") did NOT happen:
the meaning READ improves, but no live comprehension consumer profits, so no default-on flip is warranted. This is
the same shape as the sibling `the_meaning_win_is_offline_context_free_and_unwired` (PARTIAL): a real wire-able
positive + a located negative + a named forward path.

## What the brain does here, and where we lose signal (checklist 1,6)
Meaning is read IN CONTEXT — token-level biased-competition, N400 semantic prediction error (Rabovsky-McClelland;
WiC), NOT a context-free type lookup (the pri-1 refutation: WiC type-level 0.485 -> context 0.582 -> landed 0.66-0.68).
`hdlab.underspecified_sense_reader.select_sense` replicates that operation (context-primed biased competition over
the curated `meaning_foundation` hub + `diagnostic_context_wsd` readout, committing the shared-core/coarse sense;
Frisson 2009 good-enough, Rodd 2002 shared-core). We lose signal at ONE place: **the live reader's per-token meaning
representation is sense-blind everywhere** — `ConceptSpace` superposes all senses of a lemma into one blended vector —
and the ONE organ that reads context (`select_sense`) is bound as a lazy callable with NO live consumer (`sm.senses`
stays `[]`). The pri-1 refutation says this is exactly where the substrate must become context-gated.

## What I built (all glass-box, static offline foundation, NO external LLM at inference)
1. `experiments/exp_sense_gated_coref_divergence_v1.py` — the DECISIVE GATE (README ranking test 4: is there a number
   showing the DEFECT costs us, or only that an alternative exists?):
   - PART A **liveness**: a real `SituationReader.read()` over modern prose; `sm.senses == []` after read (dormant),
     `sm.select_sense` fires when invoked.
   - PART B **divergence**: over 5,285 WordNet-covered common-noun heads in their SENTENCE context, the committed
     sense diverges from the MFS the type-license uses (fine 48.4%, coarse supersense 34.0%); it diverges from a
     SHUFFLED-context commit 53.1% (context is genuinely active, not signature geometry).
   - PART C **flip ceiling**: over the 36,642 candidate (anaphor, prior-head) pairs the bridge evaluates, how many
     `coref_type_license` decisions flip under context-gating, with a shuffled-context twin.
   - PART D **controlled coref accuracy**: a recency resolver isolating the license lever (identical selection;
     baseline = the live sense-blind comparator, gated = the context wire, twin = shuffled context).
2. `experiments/exp_sense_wire_wic_liveness_v1.py` — the POSITIVE arm: runs the EXACT live-wire call
   (`USR.select_sense` over the curated hub + `default_vec_lookup`) on WiC dev+test, vs the sense-blind reader's
   majority ceiling + an info-free shuffled-context twin. (The board's own WiC arm scores `CO._pick`/`P._disambiguate`,
   a DIFFERENT curated stand-in — NOT the live wire — so it never instruments this wire; the board-proxy caution, in
   the flesh.)
3. `verification/test_sense_wire_liveness_and_coref_negative.py` — scaffold-free witness (both headlines, full pops).

## What I measured (the two decisive tables)

**POSITIVE — the live wire lifts the meaning READ (WiC, n=2038, gold-same 0.500):**

| arm | acc | vs sense-blind majority (0.500) | control |
|---|---|---|---|
| **WIRE coarse-supersense** (the live wire) | **0.7493** | **+0.2493 CI[+0.2198,+0.2802] CI-SEP** | — |
| WIRE fine-synset | 0.7159 | +0.216 CI-sep | — |
| TWIN shuffled-context (info-free) | 0.584 | +0.084 | **LOSES to WIRE, +0.1654 CI[+0.1393,+0.1924]** |
| FLOOR sense-blind reader = majority | 0.5000 | — (type-level AUC 0.5 by construction) | — |

**NEGATIVE — no downstream comprehension decision profits (common-noun coref, GUM modern TEST):**

| measurement | value | reading |
|---|---|---|
| anaphoric common-noun mentions with ANY baseline bridge | 768 / 2855 = **26.9%** | the type-bridge slice is small |
| context-gating flips / candidate pairs | 715 / 36642 = **1.95%** | 613 permit->forbid, 102 forbid->permit |
| info-free shuffled-context twin flips | **900 >= 715** | the twin does **NOT lose** — flips carry no context signal |
| coref acc: sense-blind baseline / gated / twin | 0.5967 / 0.5974 / 0.5939 | — |
| **gated - baseline** | **+0.0007 CI[-0.0090,+0.0102]** | **CI includes 0 — no lift** |
| twin - baseline | -0.0028 CI[-0.0137,+0.0082] | tracks the gated delta |

## Why this is a rigorous located negative and not a tuning-limited one (checklist 4) — ENUMERATED, both live consumers
The brain's mechanism (context-gated token-level sense) was identified and BUILT; it demonstrably WORKS on the live
meaning read (WiC +0.2493 CI-sep, twin losing, specificity 0.797 on the hard gold-DIFFERENT pairs — genuine
discrimination). The negative is not "we couldn't get the sense right" — the sense IS right. It is that **no live
decision's ERRORS are sense-disambiguation errors.** There are exactly TWO live decisions that read a common-noun
sense (enumerated by grep over the read path), and context-gating fails BOTH, for OPPOSITE reasons:

1. **coref TYPE-LICENSE — permissive + NON-DECISIVE (null, +0.0007 CI incl 0).** Context-gating sensibly TIGHTENS the
   license (613 of 715 flips are permit->forbid — it removes spurious cross-sense bridges, the RIGHT direction). But
   the license only LICENSES; recency SELECTS among the licensed set, so removing a non-selected bridge rarely changes
   the pick. **A mechanism probe corrected my first hypothesis:** I expected bridge heads to sit at their dominant
   sense (context==MFS, so gating is a no-op there). Measured, bridge-head committed==MFS is 53.7% vs the global
   51.6% — essentially NO different. So the null is NOT "bridge heads are dominant-sense"; it is that the type-license
   is a non-decisive filter. The info-free twin flips MORE (900 vs 715) because real context is targeted (recovers the
   bridging sense) while shuffled is random. The existing board arm `board_commonnoun_typelicense_dimension` already
   found this filter net-neutral live ("KEEP DEFAULT-OFF").
2. **natural-logic monotonicity is-a — DECISIVE, but wants the permissive UNION (HURTS, -0.0644 CI-sep BELOW union).**
   Here the is-a IS decisive (it directly sets entailment vs neutral). But the landed 0.767 headline deliberately uses
   the UNION (sense-unresolved) is-a read, precisely because a true hypernym entailment (taxi->car) is caught by SOME
   sense; committing a SINGLE sense sometimes picks the wrong one and MISSES the true relation -> predicts neutral ->
   wrong on entailment items. Context-gating changes 13.3% of predictions and LOSES -0.0644 CI-separated below the
   union baseline (twin -0.0810). Restricting a deliberately-permissive read is the wrong move.

**The synthesis: the context-gated sense read is correct (WiC 0.749) but has no live consumer whose errors it fixes —
the coref filter errs by recency/precision (non-decisive), and the natural-logic judge errs by coverage (wants
union).** That is the bar's named case ("no live consumer makes a sense-dependent choice the board scores
[profitably]"), enumerated over both consumers with numbers.

## Full-stack upstream + no-regress (checklist 5)
The wire is ADDITIVE and LAZY: consulting `sm.select_sense` mutates nothing on the recall path (`sm.senses` stays the
field default until a caller populates it), so byte-identical when off is structural, not asserted. The upstream it
consumes — the curated `meaning_foundation` signatures, `diagnostic_context_wsd`, and the sglite-w2v `default_vec_lookup`
— are static offline foundation assets (no external tool at inference). No downstream consumer changes, because there
is no live consumer to change (the whole point).

## Adjacent components mapped for BF fidelity + next-problem seeds (checklist 7)
- **The reader's per-token meaning representation is sense-blind everywhere** (`ConceptSpace` blends senses). This is
  the real lever: the context-gated read pays off downstream only when a consumer READS the per-token sense/meaning
  vector. Today only the (net-neutral, rare) coref type-license does. **Forward path: make the reader's per-token
  MEANING VECTOR context-modulated** (the continuous semantic-settling frame the sibling PARTIAL named; Rodd/McClelland
  CSC), feeding the generative world-model — the named meaning-representation mega-cluster, not another type-license.
- **`natural_logic_label` / `entails` — TESTED (this session), gating HURTS.** The DECISIVE is-a read deliberately
  uses the UNION; committing a single sense loses true-hypernym coverage (-0.0644 CI-sep below union). So the second
  live consumer is a NEGATIVE, not an open candidate. Enumeration complete.
- **Bridge-WRITING safety — TESTED (this session, opportunity #1): context-gating is safer than sense-blind but does
  NOT recover writing, and the safety is restrictiveness not context.** B-cubed merge quality: gated beats blind on
  precision +0.0257 CI-sep, but the shuffled-context twin matches gated (safety = committing ONE sense, not the right
  one) and no write arm (incl. the Nref uniqueness gate) beats non-writing. Holding is BF-correct (Nref). Not an open
  lead.
- **The board WiC arm scores a stand-in (`CO._pick`), not the live wire.** Re-pointing it at `sm.select_sense` would
  make this wire's capability board-visible on the live path (proposed instrumentation fix below).

## Confirmed BF status of every component I interacted with (checklist, bf_status_registry cross-ref)
| component | role here | BF status (confirmed) |
|---|---|---|
| `hdlab.underspecified_sense_reader.select_sense` | the live wire; context-primed biased competition | BF_SPIRIT (pinned biased-competition commit) — WORKS live (WiC 0.749) |
| `hdlab.diagnostic_context_wsd.diagnostic_context_scores` | the biased-competition readout | BF_SPIRIT (precision/prior knobs; admissible) |
| `hdlab.meaning_foundation` (curated sense signatures) | candidate-sense source | BF_SPIRIT (admissible static offline distributional asset) |
| `hdlab.typed_spokes.coref_type_license` | the live sense-consuming decision | BF_SPIRIT — but SENSE-BLIND (MFS/union); gating it is null here |
| `coarse_cluster` (WordNet lexname/supersense) | the committed coarse grain | admissible offline foundation (Rodd shared-core) |
| `hdlab.situation_reader._read_senses` | binds `sm.select_sense`, leaves `sm.senses=[]` | dormant by design (lazy callable, no live consumer) |
| `ConceptSpace` (live per-token meaning) | the sense-BLIND representation everywhere else | the deviation: not context-gated — the real lever |

## KEY REALIZATIONS (the enabling moves)
- **The board's meaning dims score a STAND-IN, so "wire it and watch the board" would measure a number that never
  ran.** The WiC arm scores `CO._pick`, not the live `select_sense`; the coref dims score URG, not `read()`. I built
  the arm that runs the EXACT live-wire call, and instrumented (PART A) that the wire fires 0 times live today.
- **The info-free twin is the whole ballgame, and it points OPPOSITE ways on the two targets.** On WiC the
  shuffled-context twin LOSES (context carries signal). On the coref type-license the shuffled-context twin flips MORE
  than real context (context carries NO signal into that coarse decision). Same control, opposite readings — the
  cleanest statement that the wire's value is in the meaning READ, not in the type-license.
- **Measure the CEILING before building the resolver (README test 4).** The flip ceiling (1.95% of pairs, 26.9% bridge
  slice) said upfront that even a perfect context-gated type-license could not move common-noun coref CI-sep — before
  I sank effort into a full context-gated resolver.
- **A discrete sense label is the wrong currency for most live consumers.** The reader is sense-blind because its
  decisions (roles, state, salience, recency) don't read a discrete sense; the two that do (coref type-license,
  natural-logic is-a) are a permissive filter and a permissive-by-design judge. The lever is a context-modulated
  meaning VECTOR feeding a comprehension consumer, not a sense label gating a taxonomic read.
- **Measuring corrected my mechanism hypothesis — the intellectual-honesty check earned its keep.** I predicted the
  coref null was "bridge heads sit at their dominant sense (context==MFS there)". Measured: bridge-head committed==MFS
  53.7% vs global 51.6% — REFUTED (+2pt, not the ~90% my hypothesis needed). The true mechanism is that the license is
  NON-DECISIVE (recency selects). I withdrew the wrong hypothesis; the negative stands on the measured mechanism.
- **The two live consumers fail for OPPOSITE reasons — which is why "no consumer profits" is an enumeration, not a
  shared wall.** The filter is too permissive AND non-decisive (gating tightens correctly but changes no pick); the
  judge is decisive but WANTS permissiveness (gating restricts and loses coverage). No single "tune it" fixes both —
  they are different failure modes, so this is not the "shared wall = keep tuning" trap.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **"DECIDE WHAT WORDS MEAN" organ:** the context-gated sense read (`select_sense`) is now shown to WORK on the LIVE
  meaning read — WiC 0.500 (sense-blind reader ceiling) -> 0.749 coarse-supersense, +0.2493 CI-sep, context-driven
  (shuffled-context twin loses). This CONFIRMS the pri-1 in-context/token-level mode on the live path. BUT the organ
  remains DORMANT (no live consumer; `sm.senses == []`), and the one live downstream discrete-sense consumer (coref
  type-license) does NOT profit (gating +0.0007, CI incl 0; info-free twin does not lose). The standing deviation is
  sharpened: the reader's per-token meaning is sense-blind EVERYWHERE (`ConceptSpace`); the fix that pays off is a
  context-modulated meaning VECTOR for a comprehension consumer (the generative world-model), NOT gating the coref
  type-license.

## PROPOSED hdlab CHANGE (strategy lands it, board Q111 — I did NOT write hdlab/)
1. **DO NOT gate `coref_type_license` on the context sense.** Null (+0.0007, CI incl 0), info-free twin does not lose,
   and the sense-blind version is already net-neutral live. Adding context machinery here moves no number and adds
   cost.
2. **Re-point the board WiC/sense arm at the LIVE wire** (`sm.select_sense` / `USR.select_sense`) instead of the
   `CO._pick` stand-in, so the wire's proven capability (0.749 coarse vs the sense-blind reader 0.500) is board-visible
   ON THE LIVE PATH. This is an instrumentation fix in `experiments/exp_board_wic_sense_v1.py` (board-owned), additive
   and byte-identical to the recall path. It makes "landed == live" true for the meaning-read dim.
3. **File the real forward consumer as a follow-on:** a context-MODULATED per-token meaning representation (not a
   discrete sense label) that a comprehension consumer reads — the generative world-model / meaning-representation
   mega-cluster. That is where the validated in-context read (WiC 0.749) converts into downstream comprehension gain;
   the coref type-license is not that consumer.

## OPPORTUNITIES RESEARCHED + IMPLEMENTED (owner: "research all, implement all, BF, right not easy")
Two literature findings anchored the builds (hdi_research synthesis, this session):
- **Q1 — merge is a TWO-STAGE, THRESHOLD-GATED commit** (Garrod & Terras 2000; Sanford & Garrod; Nieuwland & Van
  Berkum 2006/08 Nref; Cook & Myers 2004): fast BONDING (provisional type link) vs RESOLUTION (the confidence-gated
  commit to the discourse card); a UNIQUE antecedent commits, an ambiguous one holds (frontal Nref). Raising
  type-license PRECISION legitimately moves a bridge held->committed.
- **Q2 — context-appropriate meaning is CONTINUOUS SETTLING, a VECTOR not a discrete label** (Rodd/Gaskell/Marslen-
  Wilson 2002/04 semantic settling; Elman 2004/09 trajectory; Rabovsky/Hansen/McClelland 2018, N400 = meaning-update
  magnitude). The world-model should consume a graded context-modulated meaning vector; downstream constraint
  satisfaction disambiguates.

**#1 SAFE BRIDGE-WRITING (`exp_sense_gated_safe_bridge_write_v1.py`) — LOCATED NEGATIVE that CONFIRMS the Nref hold.**
B-cubed cluster quality over GUM modern TEST non-pronoun mentions, DRT file-change resolver, identical same-head/name
matching (only the different-head bridge WRITE differs), 137 docs. **NOBRIDGE F=0.7767 is best**; sense-blind writing
regresses (F 0.7526, -0.0241); context-gated writing is SAFER than sense-blind (**gated-blind +0.0122 F CI-sep,
precision +0.0257 CI-sep** — committing a single sense removes spurious cross-sense over-merges) — **BUT the info-free
shuffled-context twin MATCHES gated (gated-twin -0.0020, not sep), so the safety gain is RESTRICTIVENESS (one sense vs
the union), NOT context-correctness; and even the Nref uniqueness commit-gate (gated_nref F 0.7660) does NOT recover
the non-writing option (gated_nref-nobridge -0.0107, not sep).** => Holding is correct (the board's `bridge_write=False`
and Q1's Nref, confirmed): the residual different-head bridges are genuinely REFERENTIALLY uncertain (the
twin-matches-gated result IS the Nref signal), and context-appropriate sense does not resolve that uncertainty.

**#2 BOARD INSTRUMENTATION (`exp_sense_wire_wic_liveness_v1.board_wic_via_live_wire_dimension`) — IMPLEMENTED (drop-in).**
A per_dimension board row (schema-matched to `board_wic_dimension`) scoring the LIVE wire `sm.select_sense` (model
0.7493 coarse) vs the SENSE-BLIND reader (majority 0.5000), twin losing. The strategy session re-points the board's WiC
arm here with one import (it currently scores the `CO._pick` stand-in) -> landed == live for the meaning-read dim.

**#4 OPTIMIZATION — SWEEP THE PINNED BIASED-COMPETITION PARAMETERS (`exp_sense_wire_wic_param_sweep_v1.py`) — LOCATED
NEGATIVE that localizes the residual.** Copied the computation exactly (biased competition + Friston precision +
Duffy-Rayner dominance prior) and swept its params (gamma precision, topk selective gain, prior_weight dominance,
rank-decay sense_prior); dev-tuned (n=623), test-reported (n=1355). **The dev-tuned best config IS the default
(gamma=1, topk=None, prior_weight=0); test lift = +0.0000.** => the readout is already MAXED for WiC; sweeping its
parameters buys nothing. This CONFIRMS the organ's own claim (diagnostic_context_wsd: "the residual ceiling is the
CONTEXT-INPUT ENCODING, not this readout") and precisely LOCALIZES the residual-to-human upstream.

**MECHANISM-DIFF vs a COMPETENT HUMAN READER (checklist item 2), itemized with numbers.** WiC human ceiling ~0.80
(Pilehvar & Camacho-Collados 2019). Our LIVE wire: coarse-supersense 0.749-0.751, exact/lexname 0.664 (board), graded
vector AUC 0.738. The gap (~0.05 coarse / ~0.14 exact) is NOT in the readout (sweep = +0.0000) — it is the INPUT
ENCODING, on two axes: (i) our context is an UNORDERED BAG of content words; the human integrates the STRUCTURED,
INCREMENTAL, PREDICTIVE sentence gestalt (syntax + word order + discourse; Rabovsky/McClelland sentence-gestalt,
predictive coding); (ii) our sense signatures are TOPIC-level curated distributional vectors, missing the fine
PERCEPTUAL/EXPERIENTIAL differentia a human has (the pri-1 grounding lever; Binder norms are the right KIND but
sparse). Both axes are the named MEANING-REPRESENTATION mega-cluster (out of this brief's readout scope) — the sweep-
null is what proves the residual lives THERE and not in the wire we were asked to land.

**#3 CONTEXT-MODULATED MEANING VECTOR (`exp_context_modulated_meaning_vector_probe_v1.py`) — POSITIVE direction prototype.**
The Q2 currency: the SETTLED vector = the wire's OWN posterior-weighted mean of candidate sense signatures
(v_ctx = normalize(sum_s p(s|context)*sig(s)) -- "settle toward the context-appropriate region"). On the WiC noun slice
(n=1187): **GRADED vector AUC 0.7380 vs the TYPE-BLIND unconditioned vector 0.4968 (chance by construction), and the
shuffled-context TWIN LOSES (+0.1468 AUC CI[+0.1120,+0.1827]).** So a graded, context-modulated meaning vector,
computable LIVE from the wire, carries the sense signal in the continuous form the world-model should read (the discrete
coarse label is marginally sharper on the WiC same/diff task at 0.7683, but the VECTOR is the right forward INPUT, not a
WiC classifier). This prototypes the forward direction; the world-model CONSUMER is the named mega-cluster follow-on.

## SUBMISSION-INTEGRITY OPTIMIZATIONS (owner: "research all, implement all, BF, right not easy") -- round 2
Two more literature findings (hdi_research, no-fanout) anchored these:
- **Q1 (grain):** the brain's sharp sense line is HOMONYMY (unrelated meanings = competing attractors), NOT fine
  synsets; polysemy = one graded region (Rodd/Gaskell/Marslen-Wilson 2002; Rodd 2020; Klein & Murphy 2001). OntoNotes
  sense-groups (~90% agreement) match the reliable grain vs fine synsets (~70%) (Hovy 2006).
- **Q2 (vector downstream):** feeding a settled context-modulated vector into coherence/bridging is brain-motivated
  (Kintsch 1988 CI: the integration/settling phase produces the context-fit representation that feeds coherence;
  Kuperberg-Jaeger 2016), BUT bridging is partly SCHEMA-driven -- the win is in the sense-dependent slice, powered
  against a schema-only baseline.

**#1 BOARD-NATIVE coref number (`exp_sense_gated_coref_board_native_v1.py`) -- the located negative on the board's OWN
metric, replacing the proxy.** Runs the EXACT board resolver (URG.Resolver('unified', isa_type_license=True)) + the
board's URG._paired_boot, injecting a context-gated license_fn (per-doc head->most-recent committed sense; sense-blind
fallback for uncovered heads). n=2855 common-noun anaphors: filter_off (live pick) 0.4879, sense-blind filter 0.4683
(the filter HURTS -> the board's "KEEP DEFAULT-OFF"), context-GATED 0.4739. **gated-blind = +0.0056 CI[-0.0029,+0.0152]
(CI THROUGH ZERO); gated-filter_off = -0.0140 (gating does NOT recover the filter); gated-twin = -0.0084 (the
shuffled-context twin is ABOVE gated).** The proxy's located negative now holds on the board's own number, unassailably.

**#2 ENUMERATION CLOSED (`entity_states` read in full).** `hdlab.situation_reader._read_entity_states` is a SYNTACTIC
copular typer (Higgins predicational/identificational via parse + POS + `copular_binding.predicted_type`); it NEVER
reads a noun's WordNet sense or is-a. So it is NOT a sense-consumer. The live decisions that read a common-noun's
WordNet sense are EXACTLY two -- coref type-license and natural-logic is-a -- both tested (null; hurts). The C8
name-bridge consumes proper-name->type (MFS), not a wire-disambiguable common-noun sense. "No live consumer profits"
is now an ENUMERATION over the complete set, not a search.

**#3 GRAIN lever (`exp_sense_wire_wic_grain_sweep_v1.py`) -- located negative; the current commit is near-optimal.**
Implemented the Rodd homonymy/polysemy grain WordNet-natively: merge a lemma's synsets whose lowest-common-hypernym
min_depth >= D (deep ancestor = related/polysemy -> one region), keep shallow-LCA pairs separate (homonymy); swept D
(dev-tuned, test-reported). WiC test (n=1355): EXACT 0.7218, **LEXNAME (the current wire's commit) 0.7513 = BEST**,
HOMONYMY(D=4) 0.7255 (twin loses). **hom-lexname = -0.0258**: the WordNet-native homonymy grain does NOT beat the
current lexname commit -- because WordNet's is-a tree does not capture METONYMIC polysemy (animal<->meat,
institution<->building sit under different roots, so hypernym-LCA wrongly SEPARATES them as homonyms). The faithful
homonymy grain needs an OntoNotes-style sense-group inventory (acquirable foundation, NOT on disk) -- a named follow-on.
Converges with the param-sweep null: readout AND grain are both near-optimal with available resources; the residual is
upstream (input encoding + a sense-group asset).

**#4 VECTOR -> DOWNSTREAM CONSUMER -- researched + fully specified, currency already validated; faithful test needs an
off-disk instrument (NOT hacked).** Q2 gives the spec: feed the settled context-modulated vector (validated last round:
AUC 0.738 vs type-blind 0.497, twin losing) into a coherence/bridging consumer, measure the SENSE-DEPENDENT slice
against a SCHEMA-ONLY baseline + twin. The faithful instrument (a sense-dependent contextual coherence/similarity gold
-- SCWS-style, or bridging-in-context) is NOT on disk, and bridging is partly schema-driven, so a quick hack would be
the half-effort the protocol forbids. This is the DEFINING first experiment of the meaning-representation/world-model
mega-cluster (the named forward program), fully specified, with its input currency already proven live-computable.

## DEEPENING CONVERGED (30-min BF cron, ran + cancelled)
The deepening loop is exhausted FOR THIS BRIEF's scope (the sense-READ wire), and the convergence is measured, not
assumed:
- **Readout is MAXED** (item 4): sweeping the pinned biased-competition params (gamma/topk/dominance-prior) gives
  +0.0000 test lift; the residual-to-human is upstream in the INPUT ENCODING.
- **Item-3 organ-check found NO shortcut**: `substrate_map --gaps` shows no existing organ supplies the missing input
  encoding. The two input forks are both closed here: (i) GROUNDED signatures for context-selection = the
  `reader_meaning_channel` brief, already REFUTED + integrated (grounded doesn't beat the prior; grounded norms are
  lemma-level + sparse -> structurally sense-blind for WiC's same-lemma task; standing rule: do NOT re-tread the
  type-level meaning channels); (ii) STRUCTURED/predictive context = the diagnostic organ's own named "contextual-
  encoder fork" = the meaning-representation MEGA-CLUSTER (a separate program; a cheap positional hack would be the
  half-effort the protocol forbids).
- **Every live consumer is enumerated + tested** (coref null, natural-logic hurts, bridge-writing = Nref hold), the
  forward currency is validated (graded vector), and the wire is validated two ways (discrete 0.749 + vector 0.738).
The brain-mechanism bar for the READ wire is met; the remaining fidelity gap is the mega-cluster, owned by the
meaning-representation/world-model program (Q111 strategy). Nothing more of value is extractable from this brief.

## WHAT I DID NOT ESTABLISH (withdraw first if wrong)
- **I did NOT show the wire is useless.** It clearly works on the meaning read (WiC discrete 0.749 AND graded-vector
  AUC 0.738, both twin-losing). I showed no CURRENT live comprehension decision profits from it.
- **The two live sense-consumers are now BOTH tested** (coref null; natural-logic hurts) — enumeration complete. I did
  NOT test `entity_states` (a third, minor typed-spoke reader); the same volatility is expected but unmeasured.
- **#3 is a DIRECTION prototype, not the built consumer.** The graded vector carries context-driven sense signal, but I
  did NOT build the world-model that consumes it (the mega-cluster follow-on) — so I do NOT claim a comprehension win
  from it, only that the currency is validated and live-computable.
- **#1's safety gain is real but not context.** gated beats blind on precision CI-sep, but the twin matches it, so I do
  NOT claim CONTEXT makes writing safe — restrictiveness does, and even that does not recover non-writing.
- **The controlled coref resolver (PART D) is not URG's exact number** (absolute baseline 0.5967 vs URG's ~0.548) — it
  isolates the license lever under identical selection; the RELATIVE delta (+0.0007, CI incl 0) is the load-bearing
  figure, and it agrees with the existing board arm's "KEEP DEFAULT-OFF".
- **WiC coarse-supersense 0.749 is more lenient than the board's exact/lexname 0.664** (different same-rule +
  committed-only population). The load-bearing claim is the CI-separated lift over the sense-blind floor with the twin
  losing, which is robust to the rule.

## TLDR
The reader can already work out a word's meaning from the sentence it's in — we proved it does this well on the live
path (it tells apart the two meanings of a word from context 75% of the time, versus 50% for the reader as it stands,
which is blind to which meaning is intended; and a scrambled-context version does worse, so it's really using the
context). But that ability is switched off in normal reading — nothing asks it. We then checked the one place in live
reading that currently uses a word's meaning to make a decision (matching "the animal" back to "a dog" for
he/she/it-style linking). Switching on the context-aware meaning there changes almost nothing (about 0.07 of a
percentage point, statistically zero), and a scrambled version changes just as much — because the words that get
linked this way are used in their most common meaning anyway, so knowing the exact meaning doesn't help. So: the
context-aware meaning tool is real and works, but the reader has no current decision that benefits from it. The next
step is to feed the context-aware meaning into a richer understanding component (a running model of the situation),
not into the narrow word-type matcher we tested.

## QUESTIONS
None blocking. One judgement call: I filed PARTIAL, not SOLVED, because although the wire lifts a real board dim (WiC)
CI-sep with the twin losing (the bar's positive option), it is the *meaning-read* dim, and no *downstream comprehension*
dim lifts (so no default-on flip is warranted). Read it as "positive on the meaning read + located negative on the
downstream consumer" — SOLVED-of-the-wire-works + PARTIAL-of-the-downstream-lift, if you prefer.

## NEXT STEPS
1. **Re-point the board WiC/sense arm at the live wire** — DONE as a drop-in (`board_wic_via_live_wire_dimension`);
   strategy imports it in `exp_board_wic_sense_v1` to make landed==live for the meaning dim.
2. Do NOT gate the coref type-license (null) NOR the natural-logic is-a (HURTS -0.0644 CI-sep) on context; do NOT
   enable different-head bridge-WRITING (tested #1: not recovered even context+Nref-gated; holding is BF-correct).
3. **Build the real forward consumer (the mega-cluster):** feed the SETTLED context-modulated meaning VECTOR
   (#3, validated: AUC 0.738, twin-losing, live-computable from the wire's posterior) into the generative world-model
   as an incremental state update (Rabovsky/McClelland; N400 = update magnitude), letting downstream constraint
   satisfaction disambiguate — NOT a discrete sense gate. This is where the validated read converts into comprehension.
4. (Minor) test `entity_states` (the third typed-spoke reader) for completeness; same volatility expected.
