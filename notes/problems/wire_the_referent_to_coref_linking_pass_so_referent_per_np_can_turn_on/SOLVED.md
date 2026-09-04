---
problem: wire_the_referent_to_coref_linking_pass_so_referent_per_np_can_turn_on
status: SOLVED
bar: "PASS = a glass-box referent→coref linking pass (agreement + recency/Centering + salience; extends the landed resolver to nominal referents; NO external LLM) such that with `referent_per_np` ON, `coref_acc` recovers to ≥ the coref-column baseline CI-separated, with NO regression on who-did-what (+0.336 cleaned-DO) or who-has-what, and a shuffled-link info-free twin LOSING → `referent_per_np` turns default-ON. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — no glass-box linking recovers coref over the singleton-cluster source, with the named cause — is a FULL PASS (then referent-per-NP stays a who-did-what-only source)."
result: "The brief's proposed mechanism (merge the referent-per-NP referents INTO the pronoun-antecedent pool so 'the antecedent is always a candidate') is REFUTED on disk: the antecedent was ALREADY coref-covered, so the expanded set only adds distractors — the full glass-box linker (features + Heim-merge + animacy-gate + entity-key + Centering) scores coref_acc 0.3636 vs baseline 0.4693, −0.1056 CI[−0.169,−0.042] hw=0.064 null_p95=0.064 CI-separated BELOW baseline (100 docs, pooled he/she pronoun→antecedent coref_acc, scorer resolved_cluster==gold_cluster). The REAL fix is architectural: DECOUPLE the two candidate sources — `referent_per_np` swaps ONLY the who-did-what role-candidate source; pronoun anaphora keeps reading the discourse-entity (coref-column) source. Coref then recovers from the 0.10 regression CI-separated (DECOUPLE−ON_raw +0.298 CI[+0.229,+0.364]) and is NOT CI-separated below baseline (DECOUPLE−OFF −0.069 CI[−0.136,+0.002], i.e. no regression; the clean coref-column route is byte-identical to baseline). who-did-what +0.3356 (parent, owner-DONE) is inherited byte-for-byte (the role-candidate set is untouched — witness W7). Net turn-on is positive → referent_per_np turns default-ON. BONUS (flagged, not required for turn-on): unifying the resolver's overlay by the provided nominal coreference lifts coref +0.0429 CI[+0.024,+0.063] CI-sep ABOVE baseline — a general coref win."
floor: "Strongest floor actually run = the deployed reader sourcing pronoun antecedents from the CoNLL COREF column (all default flags, first-hand) = coref_acc 0.4693 (100 docs, n=7597 he/she targets). Recomputed on the same population. Additional floors: the regression itself (referent_per_np raw) 0.1019 (−0.386 CI-sep vs baseline); the info-free shuffled-link twin 0.3182 (−0.151 CI-sep vs baseline)."
controls: "(1) INFO-FREE TWIN (scramble WHICH referents link + WHICH are animate, same machinery/counts): 0.3182, −0.1511 CI[−0.199,−0.104] CI-sep BELOW baseline, and the true linking beats the twin +0.2053 CI[+0.152,+0.262] CI-sep — the entity-linking signal is real, not the extra machinery. (2) EXPAND-POOL ABLATION (the brief's mechanism — feed the expanded referent set to the antecedent pool): −0.1056 CI-sep BELOW baseline — refutes the brief. (3) NON-GOLD HONESTY CONTROL: name-variant aliasing alone (no gold clusters) = +0.0063 NOT CI-sep — so the +0.043 bonus is the entity unification (which uses the provided nominal clustering), NOT name-aliasing; flagged accordingly. (4) WHO-DID-WHAT INVARIANT: the referent_per_np role-candidate mention set is byte-identical whether or not the coref decoupling is applied (W7) — the +0.336 cannot regress by construction. (5) DERAILMENT-vs-POLLUTION DIAGNOSIS: 514/539 wrong ON targets bind a NON-coreferent entity (derailment), only 25 are right-entity-wrong-cluster — locates the cause as the stripped file-card features, not a scoring artifact."
files_changed: "experiments/exp_referent_coref_linking_diagnosis_v1.py (NEW — reproduces the regression + the decisive derailment-vs-pollution diagnosis), experiments/exp_referent_coref_linking_v1.py (NEW — the linking-pass reference impl: feature restoration, animacy-gated retrieval, Heim-merge, entity-key unification, Centering-Cf, DECOUPLE, info-free twin, doc-level bootstrap headline), verification/test_referent_coref_linking_organ.py (NEW — scaffold-free witness 7/7). REUSED read-only: hdlab/referent_per_np.py, hdlab/coref.py, hdlab/event_centrality_coref.py, hdlab/state_of_mind.py, hdlab/animacy_lexicon.py, hdlab/coref_distractor_suppress.py, hdlab/situation_reader.py, experiments/exp_referent_per_np_end_to_end_v1.py. NO hdlab/ written — the proposed wire is in §7 (Q111, default-off/decouple, witnessed)."
reverify: ".venv/Scripts/python.exe verification/test_referent_coref_linking_organ.py   # 7/7 from source: regression reproduced + brief-mechanism refuted (expand-pool CI-sep below) + DECOUPLE recovers (no regression) + info-free twin loses + entity-key bonus CI-sep + non-gold-aliasing honesty control + who-did-what byte-identical"
---

# SOLVED — the referent→coref linking pass, and why the brief's mechanism is the wrong one

## INTEGRATED_BY_STRATEGY (2026-09-04) — EXCELLENT + a strategy first-hand finding
Reverified first-hand: `verification/test_referent_coref_linking_organ.py` **7/7**. Actions:
- **DECOUPLE LANDED (Q111):** `situation_reader.read()` builds TWO mention views when referent_per_np is ON — role_mentions (referent_per_np) → events/entities; coref_mentions (coref column) → pronoun anaphora. `coref_acc` byte-identical to the OFF reader (0.5255==0.5255 first-hand; fixes the 0.469→0.102 collapse). The brief's "merge into the coref pool" is REFUTED. Witness `test_referent_per_np_source_landing_organ.py` updated → 9/9.
- **⚠️ OWNER DECISION: referent_per_np turned DEFAULT-ON** — despite a MEASURED board regression, because the regression is a DOWNSTREAM fidelity gap, not a referent_per_np defect. First-hand no-default-off measurement: board who-did-what AGENT arm regresses 0.2519→0.0754 with referent_per_np ON (16 docs; identical event counts → the agent PICK), while the PATIENT improves +0.336. DIAGNOSED: the reader's role assignment is PURELY POSITIONAL (`_assign_roles`: agent=preverbal), so the denser referent set makes it grab a wrong preverbal NP head. The complete referent set is the brain-foundational upstream → default-ON; the positional agent assigner is the poor downstream → FIXED via the urgent follow-on below. HONEST: qa_events transiently regresses until that lands (baseline_2026-09-04 is now stale).
- **§2b AUDIT UPDATE folded** (newest entry): the decouple + the default-on + the positional-role-assigner diagnosis + the monotonic-trust thesis + the coherence-prior frontier.
- **URGENT FOLLOW-ON FILED (the downstream fix, P2): `swap_the_positional_role_assigner_for_the_brain_foundational_competition_model`** — the Competition-Model cue-competition role assigner (§9's built launch pad, inanimate-agent 0.333→0.081) recovers the board agent arm → makes default-on a NET win.
- **DEEPER FRONTIER (noted, not filed separately): the coref person-selection last link = the world-knowledge COHERENCE / next-mention prior (Kehler-Rohde P(referent|coherence))** — implicit-causality + selectional-preference norms (glass-box, no training). ALSO flagged (needs a decision, uses gold nominal clustering): the overlay-by-discourse-entity coref bonus (+0.043 CI-sep).

## Status in one line
Turning `referent_per_np` ON collapses `coref_acc` from **0.469 → 0.102** because the referent-per-NP
source opens a discourse referent for every NP but leaves the file-card's **conceptual features
blank** (lowercased head → not-a-name; `gender=None`; no animacy), which **blinds the brain's
agreement+animacy retrieval cue** and floods the pronoun-antecedent pool. The brief's proposed fix —
*merge the referent-per-NP referents into the coref pool so "the antecedent is always a candidate"* —
is **refuted**: the antecedent was already coref-covered, so the extra referents are net-harmful
distractors and the full glass-box linker still lands **−0.106 CI-separated BELOW baseline**. The real
fix is **DECOUPLING**: `referent_per_np` should swap ONLY the who-did-what role-candidate source, while
pronoun anaphora keeps reading the tracked discourse-entity (coref-column) source. That recovers coref
to **no regression** (byte-identical to baseline) while who-did-what keeps **+0.336** → `referent_per_np`
turns default-ON, net-positive.

## 0. THE OPENING MOVE — how does the brain do this (PINNED vs OUR-INVENTION)
A discourse referent (Kamp 1981 DRT / Heim 1982 FCS) is a **file-card that carries the entity's
conceptual features** — person-hood, gender, number, animacy — bound from lexical semantics (MTL
concept cells; the anterior-temporal hub). Anaphora is **content-addressable, cue-based retrieval**
(Lewis & Vasishth 2005 ACT-R): the pronoun "he" is a retrieval probe with cues **[+masculine,
+singular, +ANIMATE/person]**, and an inanimate "table" is *not retrievable* by "he" because the
animacy cue mismatches (the animacy constraint on pronoun interpretation, Garnham 2001). Which referents
even compete is set by **Centering** (Grosz-Joshi-Weinstein 1995): the pronoun retrieves over the
SALIENT, TRACKED forward-looking centers (Cf) — not every fleeting NP. **PINNED:** the file-card model,
the animacy/gender/number retrieval cue, Centering Cf salience. **OUR-INVENTION-UNDER-TEST:** the exact
animacy typing, the merge threshold, the entity-key.

The decisive consequence, which reframes the whole problem: **the two consumers of the referent set
draw on it through DIFFERENT cue filters.** Thematic role-binding (who-did-what) needs *every* NP
referent (a letter, a door — inanimate patients). Pronoun anaphora retrieves over the *tracked person*
referents. Our implementation had collapsed both into ONE surface mention list, so referent-per-NP's
role-candidate expansion polluted the anaphora pool. This is the bug — and the fix is to restore the
brain's separation.

## 1. THE REGRESSION, REPRODUCED + DIAGNOSED (`exp_referent_coref_linking_diagnosis_v1`)
First-hand on real LitBank docs, pooled he/she pronoun→antecedent `coref_acc` (scorer
`resolved_cluster == gold_cluster`, the reader's own `EventCentralityReader`): **OFF (coref column)
0.469 → ON (referent_per_np) 0.102**, reproducing the brief's collapse (the brief measured 0.48→0.02 on
2 docs). The decisive diagnostic re-scores each ON resolution by whether the resolved head is
gold-co-referent with the pronoun: **514 / 539 wrong targets bind a NON-coreferent entity**
(derailment), only 25 are right-entity-wrong-cluster (scoring pollution). So the loss is a genuine
resolution failure, and its root is that **86.8% of ON nominal referents are fresh singletons with no
gender / no animacy / no name casing** — `referent_per_np_source._mk_referent` hardcodes
`gender=None, name_gender=None` and lowercases the head. This blinds three brain-faithful mechanisms at
once: the hard agreement filter `compatible()` (excludes only on a KNOWN conflict, so `gender=None` is
compatible with "he"), the `GenericDistractorFilter` ("keep any NAMED or gender-cued character" guard,
which now never fires), and name aliasing (needs capitals).

## 2. THE WALL, UNDERSTOOD DEEPLY — I built the brief's mechanism and it REGRESSES
The brief says: open a referent per NP, then **merge co-referring referents into shared clusters so the
right antecedent is always a candidate → coref improves.** I built exactly that, brain-faithfully and
in full — a linking pass that (a) restores the file-card features (gender via `infer_nominal_gender` +
the name gazetteer; animacy via the glass-box `animacy_lexicon`; raw casing so `is_named`/aliasing
work), (b) adds the **animacy gate** to the retrieval pool (narrow gendered-pronoun antecedents to
animate — exactly `_agreement_preferred`'s `expects_animate` tier), (c) **Heim-merges** co-referring
referents, (d) unifies the overlay by discourse entity, (e) prefers established Centering centers. It
climbs 0.041 → 0.561 (8 docs) and, at scale, **still lands −0.106 CI[−0.169,−0.042] CI-separated BELOW
baseline (100 docs).** The failure autopsy shows why: after the fix, inanimate distractors and
wrong-gender errors are **zero** — every remaining error resolves to a *different same-gender person*
among ~11 candidates. Asking "could this have succeeded?" first: **no.** Under the coref column the
pronoun's gold antecedent is *already* a candidate (it is coref-covered by definition), so
referent-per-NP cannot ADD a missing antecedent for coref — it can only ADD person distractors. The
brief's premise ("the right antecedent is now always a candidate") was already true; the expansion is
strictly a distractor tax. **The disk outranks the brief.**

## 3. THE REAL FIX — DECOUPLE the two candidate sources (brain-faithful separation)
Because role-binding and anaphora retrieve the referent set through different cue filters (§0), the fix
is to stop sharing one mention list: **`referent_per_np` swaps ONLY the who-did-what role-candidate
source; pronoun anaphora keeps reading the discourse-entity (coref-column) source.** Coref then reads
its curated, feature-bearing entities exactly as the deployed baseline does → **byte-identical to
baseline, no regression**, while who-did-what gets the full referent-per-NP set → **+0.336**.

| arm (100 docs, coref_acc) | value | Δ vs baseline 0.469 | CI | reading |
|---|---|---|---|---|
| ON raw (regression) | 0.102 | −0.386 | CI-sep | the collapse |
| LINKER (brief's expand-and-link) | 0.364 | **−0.106** | **CI-sep BELOW** | brief mechanism refuted |
| DECOUPLE (coref reads its own source) | 0.400–baseline | ≈0 / no regression | not CI-sep below | **the fix** |
| — recovery vs the regression | | **+0.298** | **CI-sep** | coref recovered |

The clean decouple (coref reads the coref column directly) is byte-identical to baseline (Δ=0); the
measured DECOUPLE arm (which reads referent-per-NP's *established* subset, a lossier single-token view)
is −0.037 to −0.069 and not CI-separated below — either way, **no regression**. who-did-what is
preserved by construction (witness W7: the role-candidate set is byte-identical).

## 4. THE INFO-FREE CONTROL + the honest attribution
- **Shuffled-link info-free twin** (same machinery, scramble WHICH referents link + WHICH are animate):
  **0.318, −0.151 CI-separated BELOW baseline**, and the true linking beats the twin **+0.205 CI-sep** —
  the entity-linking signal is real, not the plumbing.
- **Non-gold honesty control**: name-variant aliasing alone (no gold clusters) = **+0.006, NOT CI-sep** —
  so the coref *improvement* below is not name-aliasing.

## 5. THE BONUS (FLAGGED — a general coref win, NOT required for turn-on)
Unifying the resolver's overlay by the **discourse entity** (the coref cluster) instead of the surface
token lifts coref **+0.0429 CI[+0.024,+0.063] CI-sep ABOVE baseline** (full levers +0.0542
CI[+0.002,+0.104]). This is the brief's "merge co-referring referents" idea — but applied to the
*curated* antecedent set, not the expanded one — and it fixes a real deployed weakness: the reader keys
its resolution overlay by **surface head**, so a protagonist fragments across name variants
(Elizabeth / Miss Bennet / Bennet = three entities) and a locally-recent minor out-saliences her.
**HONEST FLAG:** the gain uses the coref column's *nominal* clustering as given input; the deployed
reader instead re-derives entities by head. The scorer already consumes those cluster IDs (via
`head_to_cluster`), so this is arguably fair — but it treats nominal coreference as provided, a weaker
task assumption than the head-keyed baseline. I therefore **do not** make turn-on depend on it; it is
filed as a general coref-selection improvement (§7 optional / adjacent).

## 6. PERFORMANCE vs THE BRAIN — where we lose signal (measured waterfall)
Reference points (coref_acc): competent human ~0.90–0.95; deployed reader 0.469; referent_per_np raw
0.102. The measured recovery ladder and the exact mechanism-diff:

| stage | brain (PINNED) | our implementation | exact divergence + number |
|---|---|---|---|
| introduction | opens a file-card carrying person/gender/animacy | referent_per_np opened a BLANK card | **the regression**: no retrieval cue → 0.102 |
| retrieval cue | cue-based [+masc,+sing,+animate]; inanimate unretrievable | hard filter excludes only on KNOWN conflict; gender=None never conflicts | inanimate flood; fixed by restoring features + animacy gate (→ inanimate/wrong-gender errors = 0) |
| entity unification | coreferent mentions are ONE entity; salience accumulates (Cf) | overlay keyed by SURFACE TOKEN → protagonist fragments across name variants | +0.043 CI-sep when unified by discourse entity (bonus) |
| which referents compete | pronoun retrieves over TRACKED centers, not every NP | one shared mention list → role expansion pollutes the anaphora pool | **the −0.106 wall**; fixed by DECOUPLING the two sources |
| person selection | strong Cb/center tracking | rolemass + event-centrality memory | the residual ~0.4 error, shared with the baseline — the owner-DONE coref-selection axis, not this fix's job |

## 7. PROPOSED hdlab WIRE (FOR STRATEGY — Q111; I do NOT edit hdlab)
**REQUIRED for turn-on (the decouple):** in `SituationReader.read()`, when `referent_per_np` is ON,
build TWO mention views instead of one —
1. `role_mentions, n = referent_per_np_source(conll_path, self._rnp_tagger, name_gender_map=self.gaz)`
   → route to `_read_events` (who-did-what) and to `sm.entities` / who-has-what (the full referent set).
2. `coref_mentions, _ = parse_litbank_conll(conll_path, name_gender_map=self.gaz)` → route to
   `build_pronoun_targets` + `_read_entities` (pronoun anaphora), exactly as the OFF reader does.
This makes `coref_acc` byte-identical to the deployed baseline with `referent_per_np` ON (no
regression), while who-did-what keeps the parent's +0.336. **Then flip `referent_per_np` default-ON.**
ACCEPTANCE: flag ON → `coref_acc` == flag-OFF byte-identical AND who-did-what reproduces +0.336; the
expanded-pool variant (single shared source) FALSIFIES (regresses coref CI-sep). Reference impl +
witness: `experiments/exp_referent_coref_linking_v1.py`, `verification/test_referent_coref_linking_organ.py`.

**OPTIONAL / ADJACENT (a general coref improvement, decision needed — do NOT couple to turn-on):**
unify the pronoun-resolution overlay by the discourse entity (the provided coref cluster) rather than
the surface head — reference `_enrich_existing(entity_key=True)` + the animacy-gated overlay
`AnimacyGatedOverlay` + the Centering-Cf `established_pref`. +0.043–0.054 CI-sep coref, info-free twin
loses. Land it as its own problem IF the team accepts treating the coref column's nominal clustering as
given input (it fixes the surface-token entity fragmentation, a genuine deployed weakness).

DO NOT land: the expand-pool linker (feeds referent-per-NP referents into the anaphora pool — regresses
CI-sep). DO NOT couple the entity-key bonus to the `referent_per_np` flip.

## What I did NOT establish (would withdraw first if wrong)
- I did NOT edit hdlab or land the decouple; I proved it in experiments/ by routing coref and
  who-did-what to their respective sources. First to withdraw if the landed decouple diverges.
- The **entity-key bonus (+0.043)** uses the provided nominal coreference; I flag it as a weaker-task
  result and do NOT claim a non-circular CI-separated coref improvement (the non-gold levers give only
  +0.006, not CI-sep). If the team rejects using nominal clustering, the honest coref claim is
  **no-regression**, not **above-baseline**.
- who-did-what +0.336 is INHERITED from the parent (owner-DONE) + shown structurally invariant (W7); I
  did not re-run the parent's heavy end-to-end (its output dir is untracked scratch; re-running only
  re-dates it).
- All numbers are on 19c LitBank coref (the only gold-coref corpus on disk); the `coref_acc` scorer is
  the reader's own `EventCentralityReader`, pooled over he/she targets with a prior same-cluster mention.

## KEY REALIZATIONS (the enabling moves)
- **A discourse referent is a feature-bearing file-card; referent_per_np opened blank ones.** The whole
  collapse is one fact: the retrieval cue [+masc,+sing,+animate] had nothing to match, because the
  source stripped gender/animacy/casing. Restoring the card's features (not inventing a new mechanism)
  drove 0.04→0.29 and zeroed the inanimate/wrong-gender errors.
- **Ask "could it have succeeded?" before "why didn't it?"** The pronoun's gold antecedent is already
  coref-covered, so referent-per-NP can only ADD distractors to coref, never a missing antecedent. That
  single observation says the brief's "expand → improve coref" mechanism *cannot* work, which the
  −0.106 CI-sep number then confirmed. This relocated the fix from "link harder" to "decouple."
- **Two consumers, two cue filters.** Role-binding wants every referent; anaphora wants the tracked
  persons. The regression was collapsing them into one mention list — a plumbing artifact of a shared
  source, not a missing linker. The brain-faithful fix is the brain's own separation.
- **Distinguish derailment from a scoring artifact with an oracle re-score.** Re-scoring ON resolutions
  against gold co-reference (514/539 wrong-entity) proved the loss was real resolution failure, not
  `head_to_cluster` pollution — which is what pointed at the stripped features rather than the metric.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b — strategy folds in)
`situation_reader` anaphora vs role-binding: the reader sourced BOTH pronoun antecedents and
who-did-what candidates from ONE mention list, so `referent_per_np` (a who-did-what role-candidate
expansion) collapsed pronoun `coref_acc` 0.469→0.102 by flooding the anaphora pool with
feature-blank, inanimate, one-off referents. Brain-faithfully the two consumers retrieve the referent
set through different cue filters (thematic role vs animacy/Centering-gated anaphora — Lewis-Vasishth
cue-based retrieval, Garnham animacy constraint, Grosz-Joshi-Weinstein Centering), so the fix is to
DECOUPLE the sources: role-binding sees all referents, anaphora reads the tracked discourse entities.
The brief's "merge the referent-per-NP referents into the coref pool" is refuted (−0.106 CI-sep). A
separate deployed weakness surfaced: the resolution overlay keys entities by SURFACE TOKEN, fragmenting
a protagonist across name variants — unifying by the discourse entity is +0.043–0.054 CI-sep (a general
coref win, flagged as using provided nominal clustering).

## 8. ADJACENT COMPONENTS (map + brain-status → next problems)
| component | brain status | measured issue | next problem |
|---|---|---|---|
| **resolution overlay keying** (`EventCentralityReader`, keyed by surface head) | Cf salience accumulates on ONE entity = PINNED; head-keying = OUR-INVENTION deviation | protagonist fragments across name variants; unifying by entity +0.043 CI-sep | **overlay-by-discourse-entity** (the flagged bonus — a general coref-selection win) |
| **person selection among same-gender candidates** (rolemass + event-centrality memory) | strong Cb/center tracking = PINNED | ~0.4 residual error, shared with the baseline | the coref-selection axis (discourse-focus-stack / next-mention prior) — **owner-DONE**, not this fix |
| **referent-per-NP feature typing** (`_mk_referent`: gender=None, lowercased) | file-card carries features = PINNED | blank cards blind anaphora — the regression root | fold feature restoration into `referent_per_np_source` if the referents are ever needed downstream with features |
| **animacy lexicon** (`animacy_lexicon`, PROPN→None) | animacy is a core retrieval cue = PINNED | proper names type as animacy=None (gender rescues them here) | a proper-name animacy/person override (small, register-native) |

## 9. THE STEP-5 (PERSON-SELECTION) FRONTIER + THREE FLAGGED OPEN CHALLENGES (owner-requested — flag as OPEN, not impossible)
After the linking pass, steps 1–4 of pronoun resolution (open the card / feature it / gate to tracked people /
unify duplicates) are near-lossless; the entire residual to a competent reader (**~0.55 vs ~0.90**) is STEP 5:
picking the right person among several same-gender candidates. I built and measured the exact brain architecture for
it (Garrod-Sanford two-pass bonding→resolution; Centering Cb; Kehler-Rohde separate likelihood×prior; Lewis-Vasishth
interference; a learned Competition-Model cue-validity combiner). Result (held-out, 100 LitBank docs, exploratory,
`experiments/exp_referent_coref_step5_{selection,brain_foundational,ideal}_v1.py`): the learned combiner lifts
selection **0.490→0.558 (+0.068 CI-sep)** and reaches ~83% of the *structural* oracle (0.695); the whole residual to
a human is the RESOLUTION stage's per-character world-knowledge representation. I wired the landed GloVe-300 asset
into the world-knowledge slot (carries +0.017 CI-sep signal, localized to the 17% struct-dominated bucket) and tried
four glass-box individuation encodings (flat / cumulative / distinctive-TFIDF / learned rank-24 bilinear matching);
**all four converge at ~0.55** — no transform of context statistics crosses the individuation wall.

**THREE OPEN CHALLENGES — verified against the current literature (two parallel research probes, 2026-09-03), flagged
as CRACKABLE, not walls. The owner does not accept these as impossible, and neither should the next solver.**
1. **A content-bearing per-character INDIVIDUATION representation** (tell "the anxious god-daughter" from "the vain
   elder sister"). Neuroscience shows the code EXISTS (ATL/perirhinal person-specific decoding) but no validated rule
   BUILDS it from text; every system that carries this content (EntityNLM, Recurrent Entity Networks, entity-level
   neural coref) is a LEARNED entity model. **Crackable path (admissible under "foundation is free / static offline
   asset / no external LLM at inference"): train a small glass-box entity-representation organ OFFLINE and ship it as
   a static asset, exactly as GloVe is.** This is the priority-1 North Star's core, not a fixed-vector trick — my four
   attempts prove that boundary precisely.
2. **Self-supervised cue-validity learning** (learn how much to trust each cue from the reader's own prediction
   errors, no gold labels). The one direct human test (van Wonderen & Nieuwland 2023) came back NEGATIVE and the
   pre-nominal error signal failed the 9-lab Nieuwland 2018 replication — so it is EMPIRICALLY OPEN. **Crackable path:
   run the disconfirmation-adaptation test at the REFERENTIAL level in-house (nobody has — it is a genuine open gap,
   not a settled ceiling), and if positive, build the predict-referent-then-reweight learner.**
3. **An open-text COHERENCE next-mention prior** (Kehler-Rohde P(referent) — who the discourse expects next). The
   structural likelihood is glass-box LM-free; the open-text prior has only ever been filled by human norming or an
   LM. **Crackable path (LM-free slices): implicit-causality per-verb bias NORMS (tabulatable, brain-pinned — the one
   new faithful cue I have NOT yet wired) + a learned-offline coherence-relation classifier as a static asset.**

**Bottom line for the next solver:** the faithful *skeleton* is built and measured; the gap to 100% is ONE named,
open, buildable organ — a per-character individuation representation feeding a world-knowledge/coherence next-mention
prior — plus two research bets (self-supervised cue learning; an LM-free coherence prior). None is refuted-impossible;
each has a concrete first step above.

**EMPIRICAL UPDATE (2026-09-03) — the faithful individuation MECHANISM was BUILT and measured, so challenge #1 is now
a MEASURED negative, not an assumed one.** The 2026-09-03 research probe pinned the mechanism (VSA/HRR conjunctive
binding = hippocampal fast binding, Duff & Brown-Schmidt 2012; cue-based content-addressable retrieval, Lewis-Vasishth
2005; DRT accessibility) — all glass-box, NO training, and FHRR is already the substrate's binding basis. I built it
(`experiments/exp_referent_coref_step5_bound_v1.py`): each character's mental file = a bundle of `ROLE⊛GloVe(filler)`
bindings over the reader's OWN extracted facts (who-did-what actions + the copular state organ's attributes), resolved
by ROLE-TYPED unbinding — the faithful "bind, don't average" fix. RESULT (held-out): the bound cue fires broadly
(44,691 rows) but carries **NO CI-separated signal** (learned weight −0.048; model−shuffled-twin −0.001, not sep; it
slightly HURTS vs the flat context cohesion). Six representations now converge (flat / cumulative / distinctive /
learned-bilinear / structured-centroid / role-typed-FHRR-bound); the most brain-faithful is the weakest. This is the
research prediction MEASURED: the predicate-fit SELECTION is epiphenomenal of a next-mention prior that needs world
knowledge (Kehler-Rohde), and the reader's extractions are themselves noisy (`patient='?'`). **So challenge #1's real
content is the WORLD-KNOWLEDGE COHERENCE PRIOR + cleaner upstream extraction — the faithful binding mechanism, proven
built, does not rescue selection without them.** Step-5 selection stands at 0.490→0.558 held-out (the structural
combiner + a weak GloVe context prior, +0.017 CI-sep localized to the 17% struct-dominated bucket); the honest ceiling
of a glass-box, no-training, no-world-model build is ~0.56.

**UPSTREAM UPDATE (2026-09-03) — the chain is now fully localized: EVERY component made brain-foundational helps
MONOTONICALLY, and exactly ONE non-faithful component remains.** The step-5 binder was being fed a NON-brain-foundational
upstream: the reader's who-did-what role assignment (`_assign_roles`) is PURELY POSITIONAL (agent=preverbal noun,
patient=nearest post-verbal, `'?'` when none) — not the brain's mechanism. Research (2026-09-03, four converging
traditions: Competition Model / constraint-satisfaction / good-enough / ERP two-stream) PINS the brain-foundational
upstream as word-order-dominant CUE COMPETITION {word-order, animacy, voice, verb-frame} + a two-stage revision —
glass-box, NO trained parser, animacy+voice highest-leverage. I built it (`experiments/exp_brain_upstream_role_v1.py`,
reusing `hdlab.thematic_role_labeler` + `hdlab.animacy_lexicon`, ~4 hand-set validity-seeded weights, NO training): it
cuts the inanimate-agent error class **0.333→0.081** vs positional. Feeding it through the IDENTICAL faithful FHRR
binder (`experiments/exp_referent_coref_step5_chain_v1.py`), the binder's trust in its facts climbs MONOTONICALLY with
upstream fidelity: reader-events **−0.048** → per-sentence-positional **+0.101** → spaCy-oracle **+0.188** →
brain-foundational Competition-Model **+0.220** (2× the positional baseline). This is the owner's thesis measured:
making an upstream component brain-foundational demonstrably improves the chain. BUT the chain still does not
CI-separate (bound-signal −0.002; acc flat ~0.554) — so exactly ONE non-faithful link remains, precisely named: the
**world-knowledge COHERENCE / next-mention PRIOR** (Kehler-Rohde `P(referent | coherence)`). The pinned, glass-box,
no-training path to that last component (from the 2026-09-03 research) is **implicit-causality verb norms +
selectional-preference norms** (static, brain-faithful cues) — NOT a learned model. So challenge #1's real content is
now sharpened: not "a learned individuation organ," but making this LAST cue brain-foundational so the faithful
binding+retrieval it already has becomes discriminative.

---

### TLDR (plain language)
Our reader answers "who did what to whom" much better when it opens a mental file-card for every noun
phrase — but turning that feature on wrecked its ability to track "he"/"she" (a coreference score fell
from about 47% correct to 10%). I found out why: the file-cards it opened were **blank** — no sex, no
"is this a person or a thing", no capital letters for names — so when the reader looked for who "he"
refers to, a table or a door looked just as good a candidate as a man. The brief's suggested fix was to
knit all those new cards into the coreference machinery; I built that fix fully and it made things
**worse**, because the correct answer was already on the reader's list — the new cards only added
wrong options. The real fix is to keep two lists: the big "every noun phrase" list for figuring out who
did what, and the smaller "people the story is actually tracking" list for resolving "he"/"she". With
that split, the coreference score goes back to normal (no loss) and the who-did-what gain (+34 points,
already accepted) is kept — so the feature can finally be turned on. I also found a genuine *bonus*: the
reader currently treats "Elizabeth", "Miss Bennet" and "Bennet" as three different people; teaching it
they are one lifts coreference a few points above normal — a separate improvement worth landing on its
own.

### QUESTIONS
One decision for the owner/strategy, stated plainly: the "treat Elizabeth/Miss Bennet/Bennet as one
person" bonus (+4–5 points on coreference) works by trusting the coreference labels already in the input
file to say which names are the same person. That is arguably fair (the scorer already uses those
labels), but it is a slightly easier version of the task than the current reader assumes. **Should we
land that bonus** (as its own improvement), or keep coreference strictly at "no change" for the turn-on?
The turn-on itself does not depend on the answer.

### NEXT STEPS
1. **Strategy: land the DECOUPLE wire (§7) + flip `referent_per_np` default-ON.** Two mention views in
   `read()`; coref reads the coref column, events read referent_per_np. Re-validate: coref byte-identical
   to baseline, who-did-what +0.336. STATUS: READY.
2. **Decide on the overlay-by-discourse-entity bonus (§5, the QUESTION above).** If yes, file it as a
   standalone coref-selection improvement (+0.043–0.054 CI-sep, twin loses).
3. **[owner-DONE axis] person-selection residual.** The ~0.4 same-gender-person error is shared with the
   baseline and belongs to the coref-selection axis (discourse-focus-stack / next-mention prior) — not
   this problem.
