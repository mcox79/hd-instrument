---
problem: open_a_discourse_referent_for_every_np_not_just_coref_mentions
status: SOLVED
bar: "PASS = a referent-per-NP candidate source (a discourse referent per content-noun-head NP; coref demoted to a downstream linking pass; glass-box, NO LLM) that raises the LIVE reader's effective end-to-end who-did-what on REAL documents CI-separated over the current live floor, with NO regression on the noun-supplied-eval accuracy (explicit no-regression check) and a scrambled-referent twin LOSING CI-separated; report the who-has-what effect too. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — referent-per-NP does not net-help live, with the named cause + number — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed)."
result: "PASS through the LIVE SituationReader().read() (mention source swapped, everything else identical), scorer pick==gold_head with ABSTENTION=WRONG, on 25 real LitBank docs. HONEST INSTRUMENT (cleaned 19c direct-object gold, n=149): coref-column deployment floor 0.4698 -> referent-per-NP 0.8054, +0.3356 CI[+0.2617,+0.4161] half=0.0772 null_p95=0.094 (CI-separated AND over null). FULL matched population (n=1354, KNOWN-NOISY gold ~76% oblique-contaminated): 0.2105 -> 0.2578, +0.0473 CI[+0.0229,+0.0702] half=0.0236 null_p95=0.0222 (CI-sep). Candidate-coverage lever reproduced first-hand: gold patient present under coref 0.8183 -> referent-per-NP 0.9705 (+0.1521, 1354 clauses). WHO-HAS-WHAT: OBJECT/theme candidate coverage 0.8191 -> 0.9342 (+0.1151); holder/SUBJECT coref-adequate (0.888, rnp 0.865); introduction capped by 19c POS-tagger noun recall 0.9142."
floor: "Strongest floor actually run = the CURRENT live wired reader sourcing candidates from the deployed CoNLL COREF column (role_route=wired, all default net-positive flags ON, first-hand). CLEAN_DO 0.4698; FULL 0.2105. Not a strawman: it is the byte-for-byte live SituationReader; only the mention SOURCE is swapped. Reference ceilings on the same population: the noun-supplied eval through the SAME live reader (the `supplied` arm) 0.7987 CLEAN_DO / 0.2504 FULL -- referent-per-NP REPRODUCES it (no-regression); the parser-free naive-positional ceiling 0.9262 CLEAN_DO / 0.5037 FULL (the reader's own verb_subcat/quotative gates are the residual, parent-owned)."
controls: "(1) INFO-FREE TWIN (matched-COUNT random-position filler referents): CLEAN_DO 0.3356 / FULL 0.1418, rnp-twin +0.4698/+0.1160 CI-sep AND twin ACTIVELY HURTS vs coref (-0.1342/-0.0687) -- adding random candidates steals picks; adding the RIGHT NP-head referents nets positive, so the signal is the FRAME not the count. (2) NO-REGRESSION (through the LIVE reader): referent-per-NP reproduces the noun-supplied eval arm, rnp-supplied delta +0.0067 CLEAN_DO / +0.0074 FULL (~0, statistically identical) -- self-built referents match the supplied candidate set. (3) DESIGN control: referent-per-NP as the SOLE source (coref demoted to linking) 0.8054 BEATS the additive union (keep coref + add missed nouns) 0.4027 -- REPLACE, do not ADD. (4) FRAME-DETECTION info-free twin: brain-faithful determiner/name-frame NP detection 0.914->0.931 CI-sep over static POS AND over a random-position twin (+0.0135 CI-sep). (5) WALL DECOMPOSITION: the FULL residual is the reader's OWN gates (supplied 0.2504 vs naive-positional 0.5037), NOT a referent-per-NP distractor penalty (rnp==supplied)."
files_changed: "experiments/exp_referent_per_np_end_to_end_v1.py, experiments/exp_referent_per_np_holder_and_generalization_v1.py, experiments/exp_referent_per_np_frame_detection_v1.py, experiments/exp_referent_per_np_signal_loss_waterfall_v1.py, experiments/exp_referent_per_np_ideal_composition_v1.py, experiments/exp_referent_per_np_selection_improvement_v1.py, verification/test_referent_per_np_organ.py, notes/problems/open_a_discourse_referent_for_every_np_not_just_coref_mentions/research_discourse_referents_brain_foundational_2026-09-03.md, notes/problems/open_a_discourse_referent_for_every_np_not_just_coref_mentions/IDEAL_who_did_what_composition_2026-09-03.md, notes/problems/open_a_discourse_referent_for_every_np_not_just_coref_mentions/selection_improvement_construction_aware_2026-09-03.md, notes/problems/open_a_discourse_referent_for_every_np_not_just_coref_mentions/SOLVED.md (REUSED read-only: experiments/exp_whodidwhat_referent_per_np_prototype_v1.py, experiments/exp_whodidwhat_ideal_brain_foundational_v1.py, hdlab/situation_reader.py, hdlab/coref.py, experiments/exp_19c_composed_cleaned_gold_v1.py). NO hdlab/ written -- the proposed wire is in FOR STRATEGY below (Q111, default-off, witnessed)."
reverify: ".venv/Scripts/python.exe verification/test_referent_per_np_organ.py   # 10/10 -- coverage lever + end-to-end CI-sep + twin-loses-and-hurts + no-regression + REPLACE>ADD + who-has-what + generalization + frame detection + IDEAL composition (>=competent reader) + construction-aware SELECTION improvement, all FROM SOURCE"
---

## INTEGRATED_BY_STRATEGY (2026-09-03) — EXCELLENT
Reverified first-hand: `test_referent_per_np_organ.py` **10/10** (coverage lever + end-to-end CI-sep + twin-loses-AND-hurts + no-regression + REPLACE>ADD + who-has-what + register-invariance + frame detection + ideal composition ≥ competent + construction-aware selection, all from source). Bar met the brain-foundational way (0.4698→0.8054 through the live reader). Actions:
- **§2b AUDIT UPDATE folded** (newest entry): referent-per-NP introduction PINNED (Kamp/Heim); the candidate-source deployment ceiling; the frame-detector + construction-selector adjacent fixes; the constructional-not-lexical finding.
- **WIRE OWED (§6, being landed as a focused RE-MEASURED step — the reader's core MENTION SOURCE, the biggest change, promoted carefully):** a default-off `referent_per_np` flag that REPLACES the coref-column candidate source with a discourse referent per content-noun-head NP (POS + the determiner/name FRAME detector, §4), coref demoted to a downstream linking pass (pronoun mentions preserved). Promote `exp_referent_per_np_end_to_end_v1.build_source(mode='rnp')` + `..._frame_detection_v1.frame_heads` → `hdlab/referent_per_np.py`; wire into `read()`'s mention source; witness (flag-off byte-identical + flag-on reproduces +0.336 + no-regression + twin loses); re-measure live. Keep `np_head_reduce` + the verb_subcat/quotative gates. DO NOT land the additive union (regresses) or a thematic-fit selector on this wire.
- **WIRE LANDED (commit `2f8305116`, default-off, witness `test_referent_per_np_source_landing_organ.py` 9/9):** `hdlab/referent_per_np.py` (`referent_per_np_source`, byte-FOR-byte identical to the validated `build_source('rnp')` — the solver's withdraw-if-diverges guard; opens 526 non-pron referents vs 201 coref; frame detector adds on top) + a `referent_per_np` flag on `SituationReader` (in `CAPABILITY_FLAGS`) swapping the mention source in `read()`.
- **⚠️ TURN-ON MEASURED (no-default-off) → KEEP DEFAULT-OFF (measured reason): turning it ON CATASTROPHICALLY regresses coref — `coref_acc` 0.4818 → 0.0200** (who-did-what events/patients unchanged on the sampled docs). ROOT CAUSE (a gap the solver's who-did-what-only measurement missed): the referent-per-NP source gives every non-coref head a FRESH SINGLETON cluster, and the "coref demoted to a downstream LINKING pass" the design assumed — merging those singleton referents into the coref clusters — is **NOT wired** (the reader's coref resolves pronouns→antecedents but does not merge non-pronoun referents), so cluster-based coref collapses. The +0.336 who-did-what is real (byte-faithful source) but comes with a −0.46 coref hit → net-negative for the coref/who-has-what-densify consumers. **Flip is GATED on wiring the referent→coref LINKING pass** (filed below). The wire is landed + available for a who-did-what-only reader config; it must NOT be default-on until the linker lands.
- **FOLLOW-ONS FILED:** `wire_the_referent_to_coref_linking_pass_so_referent_per_np_can_turn_on` (the turn-on blocker — link singleton referents into coref clusters) + `construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set` (P4 — the READY selection successor, 0.873→0.913, constructional-not-lexical). The register-native noun-POS / NP-type-gating caps route to the register-robust-detection line (P6).

**Bottom line: EXCELLENT.** A deployment-ceiling recovery proven through the live reader with model controls (the twin doesn't just lose, it HURTS), the DRT REPLACE>ADD order validated by both theory and numbers, and the composed pipeline reaching the competent-reader reference. The core source+frame wire is landed as a focused step; the selection successor is filed.

# SOLVED — open a discourse referent for every NP, not just coref mentions

## Status in one line
Opening a discourse referent for EVERY content-noun-head NP (Kamp/Heim DRT) and demoting coreference to a downstream
linking pass raises the LIVE reader's effective end-to-end who-did-what on real 19c documents from the coref-column
deployment floor **0.4698 → 0.8054 (+0.3356 CI-separated)** on the honest cleaned-DO instrument, with the info-free
twin losing AND actively hurting, no regression on the noun-supplied eval, and a +0.115 who-has-what theme-coverage
lift — a pure DEPLOYMENT recovery invisible to the noun-supplied benchmark. The referent-per-NP SOURCE is faithful
(it does not steal picks; it reproduces the supplied eval); the residual live loss is the reader's OWN precision
gates and 19c POS-tagger recall, both parent-owned adjacent components, not the source.

## 0. THE OPENING MOVE — how does the brain do this, and where do we EXACTLY differ (owner's standing question)
Brain-comparison at the mechanism level (full drill: `research_discourse_referents_brain_foundational_2026-09-03.md`).
PINNED = evidence-backed; OUR-INVENTION = a defensible engineering primitive under test.

| stage | brain mechanism (PINNED) | our implementation | fidelity | EXACT divergence + number |
|---|---|---|---|---|
| **introduction** (open a referent for every NP) | Kamp 1981 / Heim 1982 DRT-FCS; MTL concept cells + hippocampal indexing + DMN situation-model; "open-broad-then-revise" (Nref 300–400ms, Van Berkum); NP detected by its **syntactic frame** (function-word bootstrapping) not a per-token category | rule-based: POS content-noun head **+ determiner/name FRAME** detection | HIGH | we open referents for **0.931** of NP heads (POS+frame), the brain ~1.0. Gap = 19c POS-tagger noun/name recall (0.914; frame recovers ~20% of it CI-sep). Residual = a register-native tagger (filed). |
| **which NPs** (referentiality gating) | predicate-nominal / incorporated / quantified / idiom NPs get reduced or scope-bounded referents (Partee 1987; Karttunen 1976); open-broad **then TAG** | flat referent per content-noun head, **no type gating** | MEDIUM | we do not tag referentiality (over-open). "open-broad" IS faithful; the missing piece is the TAG pass — a refinement, filed. |
| **selection/binding** (bind the verb's arg to the right referent) | **thematic-fit DOMINANT** cue integration (McRae 1998; Ferretti 2001; Altmann & Kamide 1999 predictive), proximity MINOR; Competition Model | proximity-primary (nearest post-verbal) + structural-DO gate; `thematic_role_labeler` cue-integration exists but wired for LABELING | MEDIUM | the biggest mechanism divergence: we over-weight proximity, the brain over-weights fit. On the multi-candidate regime the expanded source creates, distractors steal the pick. The SOURCE is faithful (rnp==supplied, no penalty); the SELECTOR is a filed successor. |
| **linking** (coref) | full-NP introduce-then-check; pronoun → direct content-addressable retrieval (McElree; Lewis-Vasishth 2005 ACT-R; Dijksterhuis 2024) | referent-per-NP opens the card; coref **demoted to a linking pass** (singleton clusters); pronouns preserved for the reader's own resolution | HIGH | matches the brain's order exactly (introduce-then-link; pronouns direct). FAITHFUL. |
| **generalization** (register) | introduction = universal operation; register-sensitivity lives in the **LINKER** (Chierchia 1998; cross-linguistic DRT) | rule-based introduction (register-invariant); the coref linker is trained (register-sensitive) | HIGH | exactly the brain's split — introduction 0.983 modern / 0.978 19c; the coref linker OOD 0.818 on 19c. FAITHFUL. |

**Performance-level:** on the honest cleaned-DO instrument the referent-per-NP reader reaches **0.805**, vs the
coref-column deployment floor 0.470 and the noun-supplied-eval ceiling 0.799 (referent-per-NP EQUALS the eval — it is
the deployment recovery). The parser-free naive-positional ceiling is 0.926; the 0.12 gap is the reader's OWN
verb_subcat/quotative gates (the parent's separate fixes), not the source.

**ORGANS THAT MATCH WHAT I NEED (owner's ask — checked the substrate):** (a) `np_head_reduce` (default-ON) reduces a
candidate to its NP head but does NOT detect NPs the tagger misses — complementary, kept. (b) `thematic_role_labeler`
cue-integration (word-order+animacy+voice+verb-frame, "+0.264 non-canonical") IS the brain-faithful selector for the
selection-crux — it exists but is wired for role LABELING, not candidate SELECTION; wiring it as the selector is the
filed successor. (c) the forward-prediction selectional-preference centroid (`predict_surprisal`, default-ON) is the
McRae/Ferretti thematic-fit signal but is used as a surprisal FLAG (auto-revise on it is a proven negative). (d) NO
referent-per-NP mention organ exists — that is precisely this gap; the proposed `referent_per_np` builder is new.

## 1. THE MECHANISM, MEASURED end-to-end through the LIVE reader (`exp_referent_per_np_end_to_end_v1`)
I swapped ONLY the function `read()` sources mentions from (`parse_litbank_conll`) via a runtime monkeypatch (hdlab
UNedited) and ran the full live `SituationReader().read()` per arm on 25 real LitBank docs — same reader config, same
event set, so the ONLY thing that can move the patient is the candidate SOURCE. Effective end-to-end (abstain=wrong),
scorer pick==gold_head, matched to the cleaned who-did-what gold by (sentence, verb token index):

| regime | coref FLOOR | referent-per-NP | Δ vs floor | twin | rnp vs twin | no-regress (rnp−supplied) |
|---|---|---|---|---|---|---|
| **CLEAN_DO (n=149, honest)** | 0.4698 | **0.8054** | **+0.3356 [+0.262,+0.416]** CI-sep | 0.3356 | +0.4698 CI-sep | +0.0067 (~0) |
| FULL (n=1354, noisy gold) | 0.2105 | 0.2578 | +0.0473 [+0.023,+0.070] CI-sep | 0.1418 | +0.1160 CI-sep | +0.0074 (~0) |

The design is the brief's: **referent-per-NP is THE source; coref is demoted to a linking pass** (singleton clusters
inherited where a coref span overlaps; pronoun mentions preserved so pronoun resolution + who-has-what still run).
The additive alternative (keep coref + add only the MISSED nouns) UNDERPERFORMS badly (union 0.4027 vs rnp 0.8054) —
because it keeps coref's span-start-positioned multi-token mentions AND adds head-positioned singletons, creating
position conflicts and extra distractors. **REPLACE, do not ADD** — a measured design finding, and the more
brain-faithful order (introduce every NP, then link).

## 2. THE WALL, DECOMPOSED (owner: "if you hit a wall understand deeply why")
The coverage lever is +0.1521 (gold patient present 0.8183→0.9705) but the FULL end-to-end Δ is only +0.047. That is
NOT the referent-per-NP mechanism failing; it decomposes exactly:
1. **Broken gold** — on FULL the gold patient is the nearest post-verbal noun only ~49% (the board's documented
   ~76%-oblique-contamination), so the parser-free ceiling itself is only 0.504. The honest instrument (cleaned-DO)
   removes this and the lever jumps to **+0.336**.
2. **The reader's OWN precision gates** — the live reader (0.250) trails the naive-positional ceiling (0.504) by 0.25
   because of the verb_subcat/quotative gates the PARENT problem already owns; referent-per-NP does not touch them.
3. **referent-per-NP does NOT steal picks** — rnp EQUALS the supplied eval (Δ +0.007). The info-free twin proves the
   danger is real (random candidates HURT −0.069) but the RIGHT NP-head referents do not — they are the same set the
   eval supplies. So there is no source-side distractor penalty to cross.
The genuine multi-candidate SELECTION lever (thematic-fit-dominant, Q3) is a SEPARATE organ (`thematic_role_labeler`)
and the parent's fenced territory (who-did-what selection is structure-bound on canonical; grounded-fit HURTS;
the real valence parser is gated on the meaning channel). Named as the next lever, not conflated with this SOURCE bar.

## 2b. THE MEASURED BRAIN COMPARISON — signal-loss waterfall + competent-reader benchmark + the IDEAL composition
(`exp_referent_per_np_signal_loss_waterfall_v1`, `exp_referent_per_np_ideal_composition_v1`; cleaned-DO, n=149; spaCy
= competent-reader REFERENCE-ONLY, the diagnostic-oracle exception.) The multiplicative chain ORACLE→source→event→
selection→END, per arm, so every point of loss is attributed to a named stage:

| stage | COREF (floor) | RNP (this fix) | IDEAL (S1+S3) | what the loss IS |
|---|---|---|---|---|
| ORACLE | 1.000 | 1.000 | 1.000 | gold reachable |
| S1 candidate present (SOURCE) | 0.839 | **0.987** | 0.987 | the coref-vs-referent gap |
| S2 event detected \| cand | 0.968 | 0.966 | (verb supplied) | verb-ID / no-event (POS mistag) |
| S3 selected \| cand & event | 0.545 | 0.845 | → 0.873 end | positional pick + reader gates |
| **END-TO-END** | **0.443** | **0.805** | **0.873** | |
| **vs a brain** | | competent reader (spaCy) **0.846**; oracle 1.000 | | |

Three readings: (1) **performance vs a brain** — the source fix alone reaches 0.805 = 95% of the competent reader
(0.846); the IDEAL composition (referent-per-NP source + the parent's validated structural-DO + Competition-Model
selector) reaches **0.873, statistically AT/above the competent reader** (ideal−competent +0.027 n.s.), closing 77%
of the floor→oracle gap. The IDEAL ladder + controls (n=149): live-coref 0.470 → live-rnp 0.805 → IDEAL 0.873;
competent 0.846; oracle 1.000. **Info-free candidate twin (shuffle which head sits at each position) collapses to
0.235 — IDEAL beats it +0.638 CI[+0.557,+0.718] CI-sep** (the mechanism is real). The selector adds a MODEST +0.067
over the live source fix (CI[0.000,0.134], borderline n.s.) — the big CI-separated lever is the SOURCE (this bar), the
selector a smaller top-up. **STRUCTURE-BOUND insight (re-confirms the parent first-hand):** a SHUFFLED-CUE-WEIGHT twin
barely loses (0.846) — on canonical DO the STRUCTURAL direct-object filter carries the pick, not the cue weights, which
is exactly why a meaning-fit cue is a fenced negative HERE (structure already suffices). (2) **where we lose signal** —
the coref source loses at BOTH the source (0.161) AND selection (0.369: a GAPPY candidate set corrupts the positional
pick); referent-per-NP nearly closes the source (loss 0.013) AND repairs selection (0.545→0.845), because a COMPLETE NP
set lets proximity find the true DO where coref gaps misled it (the counterintuitive finding — the twin proves RANDOM
candidates hurt, but the RIGHT complete set helps BOTH coverage and selection). (3) **the ideal is prototyped from
PINNED organs** (details: `IDEAL_who_did_what_composition_2026-09-03.md`) — S1 referent-per-NP + frame (mine), S2 the
parent's noisy-channel joint POS override (available), S3 the parent's `ideal_pick`. The one GATED piece is the
meaning-fit selector for genuine ambiguity (the 0.127 residual to oracle), fenced on the meaning channel — and the
competent reader loses ~0.15 there too, so part is shared hard/ambiguous gold, not a unique gap. **HONEST NUANCE:** the
FRAME detector helps introduction RECALL (holder/name coverage → who-has-what) but HURTS the who-did-what PATIENT slot
(ideal+frame 0.812 < ideal 0.873) — names are prototypically agents, not patients; apply the right candidates to the
right slot.

## 3. WHO-HAS-WHAT effect (`exp_referent_per_np_holder_and_generalization_v1`, doc-aligned WDW role gold)
Candidate coverage of NON-PRONOUN gold role heads (pronouns excluded from both arms — they are the ORTHOGONAL he/she
coref instrument), 25 docs:
- **OBJECT / theme (the "what" in who-has-what): coref 0.8191 → rnp 0.9342 (+0.1151).** referent-per-NP recovers the
  INANIMATE object/theme referents that coref's person-heavy entity typing systematically misses — the concrete
  who-has-what lever (a transfer whose theme is not a candidate can never be bound).
- SUBJECT / holder: coref 0.8879 → rnp 0.8649 (−0.023, coref-adequate — people-holders are already coref entities).
- POSSESSIVE: coref 1.000 → rnp 0.9412 (−0.059) — people/entities, coref-covered.
- **Adjacent cap:** the 19c POS-tagger tags only **0.9142** of gold nominal heads NOUN/PROPN, so referent-per-NP
  introduction is capped there (why SUBJECT/POSSESSIVE trail slightly — mistagged names). This is the parent's named
  POS-recall limitation, and I close ~20% of it brain-faithfully (§4).
The he/she PRONOUN-holder who-has-what instrument (`exp_world_state_coref_densify`) is ORTHOGONAL to this nominal
source lever (it measures pronoun resolution); referent-per-NP is neutral there by construction.

## 4. THE BRAIN-FAITHFUL OPTIMIZATION — close the introduction gap by DETECTING NPs, not tagging tokens (`exp_referent_per_np_frame_detection_v1`)
Where the brain identifies an NP from its **syntactic frame** (a determiner/possessive left-edge + head, plus
capitalization for names — function-word bootstrapping, Abney 1991; Christophe; Morgan & Demuth), our static POS rule
misses ~9% of 19c nominal heads. Adding a frame detector (mid-sentence capital = likely name; determiner/possessive
+ known content head) lifts introduction coverage **0.9142 → 0.9311 (+0.0168 CI[+0.012,+0.022] CI-sep)** over the
static tag, and beats an info-free random-position twin (+0.0135 CI-sep) — the FRAME carries the signal, not the
extra count. Closed-class words survive archaic prose where content-word tags do not, so this is register-robust by
construction. Full closure of the residual needs a register-native POS/NER — the parent's filed adjacent problem.

## 5. GENERALIZATION / register-invariance (Q5 of the drill; `..._holder_and_generalization_v1`)
Referent-per-NP INTRODUCTION coverage of the gold patient: **modern QA-SRL 0.9828 ≈ 19c LitBank 0.9783** — the
rule-based introduction is register-INVARIANT, while the coref linker is OOD on 19c (0.8183). This is exactly the
DRT prediction (introduction is a universal operation; register-sensitivity lives in the trained LINKER). The
SELECTION also generalizes: the parent measured the who-did-what recovery over supplied candidates lifts modern
QA-SRL +0.3347 CI-sep, and referent-per-NP ≈ supplying the candidates. NOTE (honest): a coref-source DEPLOYMENT floor
cannot be run on modern text — QA-SRL sentences are isolated (no coref column) and LitBank is the only gold-coref
corpus on disk — so the end-to-end coref→rnp SOURCE delta is measured on 19c only; modern generalization rests on the
register-invariant introduction coverage + the parent's modern selection recovery.

## 6. PROPOSED hdlab WIRE (FOR STRATEGY — Q111, default-off, witnessed; I do NOT edit hdlab)
A default-off `referent_per_np` mention-source flag on `hdlab/situation_reader.py`. Reference impl:
`experiments/exp_referent_per_np_end_to_end_v1.build_source(mode="rnp")` + `..._frame_detection_v1.frame_heads`.
1. **Promote the builder** (glass-box, no LLM): before role reading, build the candidate set as a discourse referent
   per content-noun-head NP (POS NOUN/PROPN **+ the determiner/name FRAME detector**, §4), coref DEMOTED to a
   downstream linking pass — singleton clusters where no coref span overlaps; the coref pronoun mentions preserved
   for the reader's own he/she resolution + who-has-what. This is a REPLACE of the coref-column candidate source, NOT
   an additive union (§1 — the union regresses).
2. **ACCEPTANCE:** (a) flag OFF → `read()` byte-identical (non-regression witness). (b) flag ON → on the cleaned-DO
   gold the effective end-to-end rises over the coref-column floor CI-separated (reproduce +0.336) AND matches the
   noun-supplied eval (no regression, Δ≈0) AND the scrambled-referent twin loses. FALSIFIES if ON drops the
   noun-supplied accuracy or the twin ties.
3. **Keep** `np_head_reduce` on the path (head reduction over the expanded set) and the verb_subcat/quotative gates
   (parent-owned; they are the residual, not this wire's job).
DO NOT land: the additive union (regresses); a thematic-fit SELECTOR on this wire (separate successor — see NEXT).

## 7. ADJACENT-COMPONENT MAP → next problems (owner's standing instruction)
| component | brain status | limitation found (measured) | next problem |
|---|---|---|---|
| **referent-per-NP builder** (new) | Kamp/Heim introduction = PINNED; the discrete referent struct = OUR-INVENTION (defensible; no dedicated neural file-opener attested) | capped by 19c POS-tagger noun recall 0.914 (frame recovers →0.931) | **register-native POS/NER** (the parent's filed 1c; closes the residual introduction gap) |
| **selection / role pick** (`_assign_roles`, positional) | thematic-fit DOMINANT = PINNED; our proximity-primary = deviation | on multi-candidate clauses distractors steal the pick (twin −0.069 shows the danger) | **wire `thematic_role_labeler` cue-integration as the SELECTOR** over the expanded set (organ exists, +0.264 non-canonical; gated on clean non-canonical gold + the meaning channel) |
| **NP-type gating** (referentiality) | predicate-nominal/quantified/idiom get reduced referents = PINNED | we open flat referents (over-open) | an **NP-type TAG pass** (open-broad-then-tag) — a refinement |
| **coref linker** (`parse_litbank_conll` / EntityCentrality) | register-sensitive by design | OOD on 19c (0.818) — the deployment gap this problem fills | the coref axis is owner-DONE; referent-per-NP is UPSTREAM of it (the source), correctly |

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b — strategy folds in)
`situation_reader` mention/candidate source: the deployed `read()` sources who-did-what candidates from the CoNLL
COREF column, so on real 19c prose the gold patient is a candidate only 0.8183 of the time (entity-typed coref
annotates ~9% of content nouns) — a DEPLOYMENT ceiling invisible to the noun-supplied eval. The brain-faithful
operation is Kamp/Heim referent-per-NP introduction (open a referent for every NP head, coref a downstream linking
pass) — PINNED at the computational level; the discrete referent structure is a defensible OUR-INVENTION (no
dedicated neural file-opener is attested — Nieuwland 2019). Wiring it as the live candidate source lifts effective
end-to-end who-did-what 0.4698→0.8054 (+0.336 CI-sep, cleaned-DO) and who-has-what theme coverage +0.1151, with the
info-free twin losing and no regression on the noun-supplied eval. Introduction is register-invariant (0.983 modern
/ 0.978 19c) where the coref linker is OOD on 19c — the register-sensitivity lives in the linker, as DRT predicts.
Two adjacent caps remain: 19c POS-tagger noun recall (0.914; a determiner/name FRAME detector recovers ~20% CI-sep)
and the proximity-primary SELECTOR (the brain is thematic-fit-dominant; `thematic_role_labeler` is the organ, filed).

## KEY REALIZATIONS (the enabling moves)
- **Coverage is not accuracy — measure end-to-end through the LIVE reader.** The parent's +0.15 was a candidate-
  COVERAGE gain; the bar is whether it CONVERTS. Swapping only the mention source inside the real `read()` and scoring
  pick==gold (abstain=wrong) is what turned "the patient is now reachable" into "+0.336 the reader actually gets it."
- **The info-free twin is what proves the mechanism, and it does DOUBLE duty.** Matched-count random-position
  referents don't just lose — they ACTIVELY HURT (−0.069), which proves adding candidates is dangerous and therefore
  that the RIGHT NP-head referents (which net +0.047 and equal the supplied eval) are carrying real signal, not count.
- **REPLACE, don't ADD — and that is the more brain-faithful order.** The additive union (coref + missed nouns)
  regressed hard; making referent-per-NP THE source (introduce every NP, link afterwards) both scored better and is
  the DRT order. A design choice the numbers and the theory agreed on.
- **The wall was downstream, not in the mechanism.** rnp==supplied said the source doesn't steal picks; the FULL
  residual is broken gold + the reader's own gates. Asking "could this have succeeded?" (the gold ceiling is 0.50 on
  FULL) before "why didn't it?" relocated the wall off the referent-per-NP source entirely.
- **The brain detects NPs by their frame, so recover the tagger's misses with function words.** The 19c tagger
  mis-tags names (Elizabeth→ADV); the closed-class LEFT EDGE it gets right. A determiner/name frame detector recovers
  ~20% of the miss CI-sep — copying how the brain IDs a noun it doesn't know, not tuning a statistical tagger.

## What I did NOT establish (would withdraw first if wrong)
- I did NOT edit hdlab or measure the wire landed in-place — I proved the mechanism in experiments/ via a runtime
  monkeypatch of the live reader's mention source; strategy lands it (Q111). The 0.805 is the live-reader measurement,
  reproduced by the witness. First to withdraw if the landed wire diverges from the monkeypatched source.
- The FULL-population absolute numbers (0.21→0.26) are on a KNOWN-NOISY gold (~76% oblique-contaminated); I lead with
  the cleaned-DO instrument (0.47→0.81) as the honest capability and report FULL as the conservative all-comers Δ.
- Modern generalization of the end-to-end SOURCE delta is INFERRED (no modern gold-coref corpus on disk); the direct
  evidence is register-invariant introduction coverage + the parent's modern selection recovery.
- The event↔gold matching is by (normalized sentence, verb-token index); a normalized-sentence collision across docs
  is possible but affects all arms identically, so the paired deltas are robust to it.
- The referent-per-NP who-has-what benefit is on the THEME/object side (+0.115 coverage), a ceiling on binding, not a
  measured end-to-end who-has-what accuracy (the he/she instrument is orthogonal; a nominal-holder end-to-end number
  would need the world-state extraction re-run through the swapped source — filed).

---

### TLDR (plain language)
When our reader reads a real 19th-century story and is asked "who did what to whom," it builds its list of possible
answers from a coreference tool that only tracks a handful of entity types (mostly named people). So the correct
answer — often a plain object like "a letter" or "the door" — isn't even ON the list about 18% of the time, and no
amount of clever picking can then choose it. The brain doesn't wait for coreference: the moment it hears any noun
phrase it opens a mental "file card" for it, and only later works out which cards are the same thing. I made the
reader do that — open a card for every noun phrase, and treat coreference as a later linking step — and on clean
sentences its end-to-end accuracy jumped from **47% to 81%** (a large, statistically clean gain; a scrambled version
that opens cards in random places does WORSE than before, proving it's the right cards that matter, not just more of
them). It also does NOT hurt the accuracy on the old benchmark that hands the reader all the nouns — it simply lets
the reader build that same complete list itself. The same fix lifts "who has what" for objects by 11 points, and it
works just as well on modern text as on old text (98% vs 98%), because opening a card for a noun phrase is a rule,
not something you have to learn per era — unlike the coreference tool, which is trained on modern text and stumbles
on old prose. Two honest limits remain: our part-of-speech tool mislabels about 9% of old-fashioned names (I
recovered a fifth of those by spotting the grammar around them, the way the brain does), and picking the right
answer when several are close still leans too much on "nearest word" where the brain leans on "which noun makes sense
for this verb" — both are known, separately-owned next steps, not flaws in opening the cards.

### QUESTIONS
None blocking. One judgement call for strategy at landing: whether to ship the determiner/name FRAME detector (§4)
with the builder (recommended — +0.017 introduction CI-sep, register-robust, glass-box) or land the plain POS builder
first and add the frame detector as a fast-follow.

### NEXT STEPS — RANKED BY THE MEASURED SIGNAL-LOSS (we know exactly where each point goes)
The signal-loss waterfall (§2b) says precisely where the remaining signal is, so the optimization order is not a guess.
After the source fix, the RNP chain is: ORACLE 1.000 → S1 source **0.987** → S2 event **0.966** → S3 selection
**0.845** → END 0.805. Each next step targets a NAMED stage with its measured loss, the lever, the expected gain, and
whether it is READY or GATED:

0. **LAND THIS BAR FIRST — the referent-per-NP SOURCE wire** (strategy, Q111, default-off, witnessed). Closes S1
   source loss 0.161→0.013; measured **+0.336 CI-sep** end-to-end (cleaned-DO), +0.115 who-has-what theme coverage, no
   regression. Ship the determiner/name FRAME detector on the HOLDER/name path (helps who-has-what) but NOT as extra
   patient candidates (it hurts the patient slot). Then re-validate the who-did-what + who-has-what consumers (they
   inherit the source — re-validate, don't re-code). **STATUS: READY.**

1. **[BIGGEST REMAINING LOSS — S3 SELECTION, 0.148] Land the ideal selector + the PROTOTYPED construction-aware
   improvement.** Base = the parent's validated `ideal_pick` (structural-DO filter replacing the over-firing gates +
   Competition-Model pick), which takes the source fix 0.805 → **0.873 (at/above competent reader 0.846)**;
   shuffled-candidate twin collapses to 0.235 (+0.638 CI-sep). ON TOP, I PROTOTYPED a Goldberg construction-aware
   multi-DO selector (`exp_referent_per_np_selection_improvement_v1`, from the error diagnosis: 84% of residual errors
   are multi-DO competition): double-object → recipient, naming/object-complement → complement. MEASURED **0.873 →
   0.913 (+0.040 CI[+0.013,+0.074] CI-sep; +0.146 CI-sep on the multi-DO subset)**, info-free twin loses.
   **STATUS: READY — the ideal selector is parent-owned; the construction improvement is prototyped + witnessed (W10),
   compose both at land.**

2. **[DEEPEST S3 RESIDUAL — the ~0.09 to oracle after (1)] The MEANING-FIT selector for genuine ambiguity.** Where
   even the constructions cannot pick, the brain uses thematic-fit on MEANING (McRae/Ferretti). KEY FINDING from the
   prototype: a distributional selectional-preference re-rank adds only +0.007 n.s. OVER the constructions (though it
   beats its shuffled twin +0.067 CI-sep) — so on canonical multi-DO the "fit" the brain uses is CONSTRUCTIONAL, not
   lexical co-occurrence, which reconciles Q3 (fit-dominant) with the parent's fenced grounded-fit negative
   (`selection_improvement_construction_aware_2026-09-03.md`). The residual meaning-ambiguous tail needs a real valence
   model. **STATUS: GATED on the meaning channel** (the filed learner-on successor); the competent reader loses ~0.15
   here too, so part is shared hard/ambiguous gold.

3. **[S1 residual + who-has-what holder cap] Register-native POS/NER.** The introduction cap is 19c POS-tagger noun
   recall 0.914 (the frame detector recovers ~20% → 0.931). A register-native tagger closes it to ~1.0 — the brain IDs
   names/nouns from morphology+position, not a static modern-trained tag. **STATUS: FILED (parent's 1c).**

4. **[S2 EVENT/verb-ID, 0.034] The parent's noisy-channel joint POS override** for free-text deployment (the who-did-
   what task supplies the verb index, so this is small here but matters end-to-end). **STATUS: AVAILABLE (parent §0j).**

5. **[fidelity refinement] NP-type TAG pass** (open-broad-then-tag): tag predicate-nominal/quantified/idiom NPs so the
   flat referent set carries referentiality — a small step toward full DRT fidelity, not a signal-loss lever.

**In one line:** land the source (this bar) → land the validated structural selector (biggest remaining loss, ready) →
the meaning-fit selector is the deepest lever but is gated on the meaning channel; the introduction/event caps are
smaller, register-native-tagger/POS-override jobs.
