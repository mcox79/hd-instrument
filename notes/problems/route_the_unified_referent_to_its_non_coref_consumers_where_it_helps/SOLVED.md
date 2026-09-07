---
problem: route_the_unified_referent_to_its_non_coref_consumers_where_it_helps
status: REFUTED
bar: "PASSES only with ALL of: 1. The route built as a glass-box wire, PER non-coref consumer ... 2. Per routed consumer, the unified-referent input beats that consumer's CURRENT input CI-separated on MODERN gold (GUM), reported separately per consumer. The FLOOR is the consumer's CURRENT live input ... gate on the floor's UPPER CI bound. 3. The info-free twin LOSES CI-separated, per consumer ... 4. The he/she coref pick is BYTE-IDENTICAL (untouched). 5. No other downstream consumer regresses. ... A rigorous NEGATIVE is a FULL PASS on any consumer (e.g. '... the affect-experiencer binding does NOT move because the live experiencer subpopulation is already near-ceiling ~0.90 ...'; OR '... the situation-model entity layer already runs the situation-gated common-noun former, which captures the same individuation the unified card would supply, so the route is redundant -- subsumption by a DIFFERENT landed organ, located and counted')."
result: "On MODERN gold (GUM V12.1.0, 137-doc TEST split; scorers per consumer; doc-level paired bootstrap 2000x; grouping BYTE-FAITHFUL to hdlab.unified_referent.resolve_unified_stream, self-test asserted), routing the unified referent to the three live NON-coref consumers does NOT deliver a per-consumer CI-separated gain -- a rigorous LOCATED NEGATIVE (a full pass under the bar). PER consumer: (C1) SITUATION-MODEL ENTITY LAYER, CoNLL b3/muc/ceafe avg over non-pronoun mentions: unified grouping 0.6976 vs the LIVE floor (commonnoun_binder.situation_predict) 0.6939 = +0.0036 CI[+0.0008,+0.0063] -- a MARGINAL CI-sep edge that is SUBSUMED by a DIFFERENT dormant landed organ (the entity-KB resolver reader_coref=None = 0.7033 > unified 0.6976). (C2) ENTITY-KB HARD-LINK (a common noun of a NAMED entity files under the named record), n=2587: unified grouping 0.0139 vs live floor 0.0228 = -0.0089 (REGRESSES; == blind surface-head 0.0139 -> the unified card supplies NO cross-type common->name bridge). (C3) AFFECT/GOAL EXPERIENCER BIND (person common-noun experiencer files under the named entity), n=295: unified grouping 0.0508 vs live floor 0.1288 = -0.0780 (REGRESSES). The reader_coref route is INERT: feeding the entity-KB resolver the unified card head-sets changes 0 labels across 137 docs (delta +0.0000), and feeding it the reader's OWN two-pass clustering head-sets (the +0.0882-on-19c-LitBank lever) moves the CoNLL by +0.0000 (325 diffs, CI[-0.0001,+0.0001]) -- the reader_coref lever is a 19c-only effect, not a wrong-source problem. Unified completed-gender injection is flat (-0.0004). The he/she coref pick is BYTE-IDENTICAL with the route on (16/16 docs)."
floor: "The strongest floor actually run, recomputed on the SAME GUM TEST population + scorer per consumer: (C1) the LIVE default entity-layer clustering commonnoun_binder.situation_predict = 0.6939 CoNLL avg (disk-verified default: commonnoun_situation_gate=True, entity_kb_resolver=False); (C2) situation_predict hard-link 0.0228; (C3) situation_predict experiencer bind 0.1288. Reference alternatives run on the SAME population: the DORMANT entity-KB resolver resolve_common_noun(reader_coref=None) C1 0.7033 / C2 0.0460 / C3 0.1119 (it DOMINATES the unified grouping on C1/C2), and blind surface-head C1 0.6937 / C2 0.0139 (== the unified grouping on C2/C3 -> no bridge)."
controls: "(1) SELF-TEST gate: group_unified reproduces the live resolve_unified_stream per-target records EXACTLY (byte-faithful stand-in -> the negative is not a harness artifact). (2) INFO-FREE TWIN = shuffled unified GROUPING (same #cards + size shape, random membership): LOSES CI-sep on the size-robust CoNLL (unified-twin +0.3707 CI[+0.360,+0.382]) -> the grouping IS load-bearing signal, so the negative is SUBSUMPTION/register, not 'no signal'. (The size-GAMEABLE hard-link metric is INFLATED by the twin -- random merging accidentally shares a name label -- so CoNLL is the valid twin instrument; the p12 scorer-gaming lesson, caught here again.) (3) SOURCE control: reader_coref from the reader's OWN two-pass clustering (the strongest possible source) is ALSO inert on GUM -> excludes 'wrong reader_coref source', the lever is 19c-only. (4) HE/SHE BYTE-IDENTITY: the tuned graded he/she pick (EventCentralityReader graded_pick=True, unified_referent=False) is byte-identical with the full non-coref route applied (disjoint path; 16/16 docs). (5) MODERN gold only (GUM), 19c LitBank NOT used as load-bearing (owner 2026-09-06)."
files_changed: "experiments/exp_route_unified_to_consumers_gum_v1.py, verification/test_route_unified_to_consumers.py, notes/problems/route_the_unified_referent_to_its_non_coref_consumers_where_it_helps/SOLVED.md. NO hdlab/ written (Q111 -- the finding is DO-NOT-WIRE; strategy owns any hdlab change). Reuses data/corpora/gum/ (pinned GUM V12.1.0, already on disk)."
reverify: ".venv/Scripts/python.exe verification/test_route_unified_to_consumers.py (8/8) -- re-derives the located negative + the byte-faithful grouping self-test + the he/she byte-identity from experiments.exp_route_unified_to_consumers_gum_v1.run() on the GUM TEST split."
---

# REFUTED -- route the unified referent to its non-coref consumers

**STATUS: REFUTED** (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written -- the finding is measured in `experiments/` + `verification/`; the strategy session owns any hdlab
change (Q111), and the recommendation here is **do NOT wire**.

The brief's core hypothesis -- that routing the landed unified referent to the live NON-coref consumers (entity-KB
hard-link, affect/goal experiencer binding, situation-model entity layer) yields a per-consumer CI-separated gain on
modern gold -- is **REFUTED**. On GUM the routed arms are **flat-to-negative** on every consumer, and the one marginal
CI-separated edge is **subsumed by a different dormant landed organ**. A rigorous located negative is a full pass under
the bar; per the operating protocol I then went past the refutation to name the mechanism, test the redirect routes, and
establish the underlying problem is not solvable by any route I could test on modern gold.

## What the disk said that the brief did not (verified first-hand -- the disk outranks the brief)
1. **The live entity-layer clustering is NOT `resolve_common_noun`.** The brief names the entity-KB consumer as
   `resolve_common_noun(reader_coref=None)`, but on disk the live default is `commonnoun_situation_gate=True` **and
   `entity_kb_resolver=False`** (`hdlab/situation_reader.py` L908-910) -- so `_apply_commonnoun_gate` runs
   `commonnoun_binder.situation_predict`, and the entity-KB resolver is itself **DORMANT (default-off)**. My floor is
   therefore `situation_predict` (the true current input), with `resolve_common_noun(None)` measured as a reference.
2. **The p11 "entity-KB hard-link +0.072" and "pronoun pick +0.106" are PRONOUN-resolution metrics, not the live
   common-noun consumers.** In `exp_unified_referent_gum_v1.py` the "kb_hardlink" scorer is
   `bool(picked is not None and picked.has_name and picked.dominant_eid() == m.eid)` for a **pronoun** `m` -- i.e. "does
   the PRONOUN resolve to the referent carrying the name," measured intrinsically on a WEAK resolver. It is the pronoun
   pick under a different scorer, not the live `resolve_common_noun` (a COMMON-noun task). The brief itself flagged these
   were "measured on the reference HARNESSES, not the live consumers"; the disk confirms they are the same PRONOUN task.
3. **`resolve_unified_stream` returns only per-target pronoun records** -- no mention->card grouping. To route the card
   to a non-coref consumer I reproduced its file-change grouping (`group_unified`) and GATED it with a self-test that it
   reproduces the live `resolve_unified_stream` per-target records EXACTLY (byte-faithful stand-in).

## How the brain does this (the frame -- and why the negative was predictable)
- **PINNED (Ariel 1990 Accessibility Hierarchy; both prior SOLVEDs cite it).** The retrieval CUE is consumer-specific.
  The unified card's distinctive asset is COMPLETED cross-type SALIENCE + gender -- which is the **PRONOUN** cue
  (high-accessibility anaphora resolve by salience/prominence). Definite descriptions / common nouns resolve by
  **RECENCY / HEAD identity** (+ world knowledge for cross-type bridging), NOT salience. So the card's completed salience
  does not reach the common-noun consumers -- the brief's premise that these are "identity/salience consumers" is wrong
  for common-noun resolution.
- **The consequence the measurement then confirmed:** the ONLY live consumers that use the salience/identity cue the
  card completes are PRONOUN resolvers -- and the live reader resolves pronouns with the TUNED he/she pick (where the
  card is SUBSUMED + antagonistic, p12) and, for experiencers, through that same tuned pick. **There is no live consumer
  that both (a) lacks the tuned pool AND (b) uses the salience cue.** The unified referent's value has one home -- the
  pronoun pick -- and there it is subsumed.

## The measurement (GUM V12.1.0 TEST, 137 docs; one screen)
| consumer (scorer) | live floor | UNIFIED grouping | delta vs floor | dominant alt (dormant landed) |
|---|---|---|---|---|
| **C1 situation-model entity layer** (CoNLL b3/muc/ceafe) | situation_predict **0.6939** | **0.6976** | **+0.0036 CI[+0.0008,+0.0063]** (marginal, CI-sep) | entity-KB resolver **0.7033** (SUBSUMES) |
| **C2 entity-KB hard-link** (common noun files under named record, n=2587) | **0.0228** | **0.0139** | **-0.0089** (REGRESSES; == blind surface-head -> no bridge) | entity-KB resolver 0.0460 |
| **C3 affect/goal experiencer bind** (person common-noun experiencer, n=295) | **0.1288** | **0.0508** | **-0.0780** (REGRESSES) | entity-KB resolver 0.1119 |

**Routes tested (all three the brief named -- cluster / canonical head / ACT-R salience / reader_coref head-sets):**
- **Route (i) unified grouping AS the clustering** (`uni_direct`): the table above -- marginal-subsumed on C1, regresses
  C2/C3. The grouping is blind-head for common nouns (a common noun merges only with a prior SAME-head card; names never
  add to `.heads`) -> it supplies NO cross-type common->name bridge, so it is identical to surface-head on C2/C3. The
  bridge is exactly the world-knowledge wall p11 documented (81% of common->name anaphora needs world knowledge).
- **Route (ii) unified head-sets as the entity-KB resolver's `reader_coref` lever** (`uni_rc`): **0 label changes across
  137 docs** (delta +0.0000 on every consumer). The card's >=2-head sets are name-VARIANT sets ({barack,obama}) the
  aliaser already handles, never cross-type {president,obama} bridges -> the lever never fires. **SOURCE control:** even
  the reader's OWN two-pass clustering head-sets (the +0.0882-on-19c-LitBank lever) are inert on GUM (+0.0000, 325 diffs)
  -> the `reader_coref` lever is a **19c-only effect**, not a wrong-source problem.
- **Route (iii) unified completed-gender as a per-mention prior** (`uni_gender`): flat (-0.0004 C1, +0.0000 C2) -- gender
  is ~6%-sparse on modern nominals (p11's quantified cap), so the card's completed gender has almost no common-noun
  gn-filtering to convert.

**Controls.** Twin (shuffled grouping) LOSES on the size-robust CoNLL (unified-twin +0.3707 CI-sep -> the grouping IS
real signal, the negative is subsumption not "no signal"); the twin INFLATES the size-gameable hard-link (so CoNLL is the
valid twin instrument -- the p12 scorer-gaming lesson, re-caught). He/she pick byte-identical (16/16 docs, disjoint path).

## Why this matches the bar's OWN examples of a valid located negative (a full pass)
- **C3 = "the experiencer binding does NOT move because the subpopulation is near-ceiling."** The experiencer binding is
  near-ceiling on the EASY subpop (pronoun experiencers via the tuned pick ~0.90; name experiencers bind trivially) --
  the byte-identical he/she pick the route may not touch -- and at the WORLD-KNOWLEDGE WALL on the hard common-noun
  subpop (0.13). The unified referent helps NEITHER: the easy subpop is the off-limits tuned pick; the hard subpop is the
  bridge wall. No headroom, both mechanisms confirmed with counts (n=295 hard subpop).
- **C1 = "subsumption by a DIFFERENT landed organ, located and counted."** The unified grouping's only CI-sep edge over
  the live `situation_predict` (+0.0036) is dominated by the dormant entity-KB resolver (0.7033 > 0.6976) -- turning THAT
  on is strictly better and simpler than routing the unified referent. The unified card adds nothing the entity-KB
  resolver does not already provide (and more).

## The redirect I tested (protocol: refutation is the halfway point) and why it also fails on modern gold
The real underlying goal is "realize the unified referent's proven value at a consumer that lacks the tuned pool." Its
proven value is the PRONOUN pick (isolation +0.106, p11). I looked for a live pronoun consumer that is NOT the tuned
he/she pick: (a) the affect/goal experiencer PRONOUN binding uses `sm.coref_resolutions` = the tuned pick (byte-identical,
off-limits); (b) the entity-KB resolver's INTERNAL `resolve_pronoun` is a separate weak pronoun resolver, but it feeds
common-noun linking, which I measured flat/negative (the bridge wall dominates). So every live pronoun-resolution consumer
routes through the tuned pick, and every non-pronoun consumer is at the recency/head + world-knowledge wall. **No route I
could test on modern gold realizes a gain** -- the routes tested: grouping-as-clustering, reader_coref (unified + two-pass
source), completed-gender prior, and the search for a non-tuned pronoun consumer. The ONE untested lever is a NEW
capability (extend coref TARGETS to they/it/plural pronouns the tuned he/she pick does not cover) -- that is a different
problem (a new pronoun-population organ), not "route to non-coref consumers," and I name it as a candidate follow-on.

## What I did NOT establish / would withdraw first if wrong
- **The marginal C1 +0.0036 CI-sep edge over `situation_predict` is the closest thing to a positive, and the first thing
  I would withdraw.** It is within a hair of its own half-width (0.0028), it is SUBSUMED by the entity-KB resolver, and it
  does not survive as a capability (routing the grouping regresses C2/C3). If a reviewer wants to read C1 alone as a
  micro-PASS, the honest reading is still "do not route the unified referent; turn on the entity-KB resolver instead."
- **GUM only.** GENTLE OOD (26 docs, on disk) was not run; the negative is on GUM's 18 modern genres. The mechanism (Ariel
  cue-specificity + the common->name world-knowledge wall) predicts the same OOD, but I measured only GUM.
- **The experiencer C3 easy-subpop near-ceiling (~0.90) is argued from mechanism** (pronoun via the tuned pick; name
  trivial), quantified directly only on the HARD common-noun subpop (n=295 at 0.13). A full easy+hard experiencer census
  would strengthen it but does not change the verdict (the unified referent touches neither).

## KEY REALIZATIONS (the enabling moves)
- **The disk's default flags reframed the whole floor.** `entity_kb_resolver=False` on disk means the live entity-layer
  clustering is `situation_predict`, not `resolve_common_noun` -- so the brief's named consumer is itself dormant, and the
  reader_coref lever it points at is off the live path. Reading the actual `__init__` defaults, not the brief, set the
  correct floor and revealed the reader_coref route is doubly-dormant.
- **The "entity-KB hard-link +0.072" was the pronoun pick wearing a different scorer.** Tracing the p11 `kb_hardlink`
  scorer to its source (`picked.has_name and dominant_eid==m.eid` for a PRONOUN) showed the reference-harness "non-coref
  lifts" are all PRONOUN-resolution metrics on a weak resolver -- so they cannot transfer to the truly-separate
  common-noun consumers, and the live reader already does pronouns with the tuned pick. This is the whole refutation: the
  unified referent's home is the pronoun pick, where p12 already showed it subsumed.
- **The SOURCE control separated "wrong source" from "lever is 19c-only."** Feeding the resolver the reader's OWN two-pass
  clustering (the exact +0.0882-LitBank lever) and getting +0.0000 on GUM is what turns "the unified head-sets are too
  thin" into "the reader_coref lever does not transfer to modern gold" -- a register wall, counted.
- **The twin re-caught the p12 scorer-gaming trap.** The shuffled twin WON on the hard-link metric (random merging shares
  a name label) but LOST hard on CoNLL -- confirming CoNLL is the size-robust instrument and the hard-link metric must not
  be used for the twin control. Validating the twin against the metric before trusting it is what kept the negative honest.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b, E3 coreference / entity tracking)
- The 2026-09-06 unified-referent DEFAULT-OFF disposition is CONFIRMED and EXTENDED: not only is it subsumed at the he/she
  pick (p12), its value **cannot be realized at the live NON-coref consumers on modern gold either** -- routing its
  grouping is flat-to-negative (C1 +0.0036 subsumed by the entity-KB resolver; C2 -0.0089; C3 -0.078), its `reader_coref`
  lever is inert on GUM regardless of source (a 19c-only effect), and its completed gender is ~6%-sparse. **Keep
  `hdlab/unified_referent.py` DEFAULT-OFF everywhere; do NOT add a non-coref route.**
- **CORRECTION to the p12 adjacent-components note** ("the unified referent's real home is the WEAK scorer / non-coref
  consumers"): REFUTED on the LIVE consumers on modern gold. The reference-harness "non-coref lifts" were PRONOUN-pick
  metrics on a weak resolver; the truly-separate common-noun consumers do NOT lift (Ariel cue-specificity + the
  common->name world-knowledge wall). The unified referent's only home is the pronoun pick, where it is subsumed.
- **NEW deviation to fold in:** the entity-KB resolver's `reader_coref` Step-3 lever (+0.0882 CoNLL on 19c LitBank) does
  NOT transfer to modern GUM (+0.0000, both from the unified card AND from the reader's own two-pass clustering) -- a
  19c-vs-modern register effect on the common->name bridge, which is world-knowledge-bound on modern multi-genre text.

## Adjacent components (seeds for the next problems -- evaluated for brain-foundational fidelity)
- **The DORMANT entity-KB resolver (`entity_kb_resolver=False`)** dominates the unified grouping on the entity layer
  (C1 0.7033 vs 0.6976) and the hard-link (C2 0.0460 vs 0.0139) on GUM, but slightly regresses the experiencer subpop
  (C3 0.1119 vs 0.1288). Whether to turn it on (net across consumers, twin, no-regress) is a separate, higher-value
  wiring question than routing the unified referent -- a candidate follow-on. Brain-status: its salience is composite
  Centering (PINNED-ish); its common->name bridge is a curated KB (OUR-INVENTION world-knowledge proxy, the honest wall).
- **The common->name world-knowledge bridge is the real lever for ALL three consumers** (C2/C3 sit at 0.01-0.13 because a
  common noun cannot find its named entity). p11 measured the glass-box bridge (apposition/copula + head-in-name) recovers
  ~19%; the other ~81% needs a semantic is-a/scenario prior (the Phase-1 `entity_world_model_resolver` identifiability
  wall). This -- not the unified referent -- is where the entity-KB/affect consumers gain. Brain-foundational and filed.
- **Extend the pronoun-resolution TARGET set beyond he/she (they/it/plural)** -- the one place the unified referent's
  broader ACT-R pronoun resolution could add a LIVE gain the tuned he/she pick does not cover. A NEW capability (a new
  pronoun population), not this problem; candidate follow-on.

---

**TLDR (plain English):** A good reader keeps one shared record per character. We built that record; it helps the
reader's "who is he/she" guess (but there it's redundant with an already-tuned guesser), and the plan here was to send it
instead to the reader's OTHER jobs -- filing a fact under the right named person, attaching a feeling to the right
character, keeping straight which "the man" is which. I wired it to those jobs and tested on modern text, and it did **not**
help: two of the three jobs got slightly WORSE, and the third improved by a whisker that a different, already-built (but
switched-off) tool beats anyway. The reason is a real one about how reading works: the shared record's strength is knowing
who's "in focus," which is exactly what "he/she" needs -- but "the man" and "the doctor" are matched by the WORD and by
outside world-knowledge, not by focus, so the shared record has nothing to offer them. The numbers that made this look
promising earlier were actually measuring the "who is he/she" job again under a different name. So the honest answer is:
don't send the shared record to these other jobs -- it belongs to the "he/she" job, where it's already redundant. I proved
the shared record itself is real (a scrambled version falls apart) and that the "he/she" guesser is left exactly as it was.

**QUESTIONS:** none blocking. One judgement call: I marked this **REFUTED** rather than PARTIAL. The one CI-separated
edge (the entity layer, about four more right in a thousand) is real but marginal AND beaten by a different switched-off
tool, while the other two jobs regress -- so the brief's promise (a per-consumer gain) is not met and its premise (that
the reference-harness lifts transfer to the live jobs) is disproven. If you'd rather log the marginal entity-layer edge as
a micro-PARTIAL, the actionable recommendation is unchanged: do NOT route the unified referent; if the entity layer is to
improve, evaluate turning on the dormant entity-KB resolver instead.

**NEXT STEPS (strategy owns any hdlab change; solver is scope-barred from hdlab/):**
1. **DO NOT WIRE the unified referent to the non-coref consumers, and keep `hdlab/unified_referent.py` DEFAULT-OFF
   everywhere.** The route is flat-to-negative on modern gold; the reader_coref lever is 19c-only; the marginal entity-layer
   edge is subsumed by the entity-KB resolver.
2. **Fold the AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` sec 2b, including the CORRECTION to p12's "non-coref
   consumers are the unified referent's home" note (refuted on the live consumers).
3. **FOLLOW-ON (higher value than this route):** decide whether to turn on the DORMANT entity-KB resolver
   (`entity_kb_resolver`) -- it dominates the unified grouping on the entity layer + hard-link on GUM (measure net across
   consumers + twin + no-regress on the experiencer subpop), and pursue the glass-box common->name bridge (the real lever
   for the entity-KB / affect consumers, ~19% glass-box + the ~81% world-knowledge Phase-1 wall).
4. **FOLLOW-ON:** extend the pronoun-resolution TARGET set beyond he/she (they/it/plural) -- the one place the unified
   referent's broader ACT-R pronoun resolution could add a live gain the tuned he/she pick does not cover (a new capability).
