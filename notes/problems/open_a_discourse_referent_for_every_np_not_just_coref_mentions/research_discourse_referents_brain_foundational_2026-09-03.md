# Discourse referents for every NP — brain-foundational literature drill (2026-09-03)

Consolidated from 4 parallel lit-scans (DRT/FCS referent-opening; neuroscience; argument-binding selection;
introduce-then-link timing; register generalization). Verdicts marked PINNED-by-evidence vs OPEN/OUR-INVENTION.

## Q1 — Which NPs open a discourse referent?
DRT's "every NP on first mention" is not literal — four exception classes (predicate nominals John is a DOCTOR =
property `<e,t>` not individual, Partee 1987/Williams 1983; incorporated/weak-definite objects = gradient reduced
referent, Farkas & de Swart 2003, Dayal; non-referential/quantified = referent opens but scope-trapped, Karttunen
1976, Kamp & Reyle 1993; idiom-chunk nouns = anaphoric islands, Nunberg-Sag-Wasow 1994). BUT real-time evidence
favors OPEN-BROAD-THEN-REVISE (Sanford & Garrod bonding-vs-resolution; Nref at 300–400ms Van Berkum 2003; Nieuwland
2019 processes related-but-novel nouns as brand-new then revises). **PINNED:** exception classes (formal consensus);
open-broad-then-revise well-supported. **ENGINEERING:** open a referent for every NP head by default; run an NP-type
classifier (copula-subtype / incorporation / quantifier-scope / idiom) as a TAGGING pass, not a gate.

## Q2 — Neuroscience of discourse referents
Substrate exists (MTL concept cells, Quian Quiroga 2012; hippocampal indexing, Teyler & Rudy 2007; DMN
situation-model, Zwaan & Radvansky 1998 / Baldassano 2017) but NO study isolates an entity-specific "file-opening"
signal surviving control for lexical/semantic surprisal — Nieuwland 2019 explicitly argues against a dedicated
file-opening component (general unexpectedness, not referent-introduction per se). **PINNED:** substrate exists;
**OPEN/leaning-negative:** "opening a referent" as a distinct neural primitive vs emergent novelty readout.
**ENGINEERING:** the discrete new-referent structure is a defensible OUR-INVENTION engineering primitive (DRT requires
it; human entity-tracking is capacity-limited consistent with it) — do NOT claim brain-mandated fidelity for a
dedicated detector; novelty = one graded multi-feature signal.

## Q3 — The selection/binding crux (THE WALL — highest leverage)
Convergent ARCHITECTURE (no closed-form weights): parallel weighted cue integration, THEMATIC-FIT DOMINANT,
proximity MINOR. Thematic fit is fast + override-capable (McRae-Spivey-Tanenhaus 1998 competition-integration;
Ferretti-McRae 2001 verbs pre-activate typical patients; Trueswell 1994 implausible-agent eliminates garden-path;
Altmann & Kamide 1999 anticipatory saccades from the verb ALONE). Animacy real but SECONDARY in English (MacWhinney-
Bates-Kliegl 1984 English relies on word-order > animacy). Structural DO / subcat / prep-marking = English's
case-substitute, near-hard gate. Centering salience = wrong scope (governs referring-FORM, not role assignment).
**CRITICAL GAP:** cue-validity numbers were measured on 2-NOUN sentences — NO study covers the 3+-postverbal-candidate
regime the widened source creates. **PINNED:** architecture (fit-dominant, proximity-minor); **OPEN:** numeric weights
for the multi-candidate regime. **ENGINEERING:** invert the pipeline — structural-DO hard gate → verb-conditioned
thematic-fit (McRae/Ferretti corpus-typicality) as the DOMINANT graded rank → animacy secondary → **proximity
last-resort tie-break only**. This is the exact diagnosis of our measured wall: distractors win because proximity is
over-weighted.

## Q4 — Is introduce-then-link the brain's order?
Full-NP vs pronoun ASYMMETRY is PINNED (Gordon & Hendrick 1998: full NP established as new referent THEN checked;
pronoun interpreted coreferentially with no new-representation step; repeated-name penalty N400 ≈ new-name N400).
Linking = content-addressable retrieval (McElree direct-access; Lewis-Vasishth 2005 ACT-R; Dijksterhuis 2024 a later
pronoun reactivates the noun's concept cell). Coherence/verb-bias cues pre-narrow candidates BEFORE the mention
(Koornneef & Van Berkum 2006 immediate focusing). **PINNED:** full-NP/pronoun asymmetry + predictive pre-narrowing;
**OPEN:** exact retrieval circuitry (CA3 pattern-completion is analogy, not attested). **ENGINEERING:** two passes, but
pass-1 (introduce) is reference-FORM-sensitive — skip it for pronouns/reduced forms, route them directly into cue-based
retrieval over the open-referent pool. (Our design already does this: content-noun heads → referents; coref pronouns
preserved for direct resolution.)

## Q5 — Generalization across register/genre/language
Referent-introduction is a formally UNIVERSAL operation with language-specific surface triggers (compositional DRT
Muskens 1996; Chierchia 1998 Nominal Mapping Parameter — article-less languages introduce referents via classifiers/
aspect; Mandarin bare nouns support anaphora, Dayal & Jiang 2023). The REGISTER-SENSITIVE component is the statistical
coref LINKER, not introduction. Literary-coref work (ACL W18-4515) shows the hard cases are exactly the Q1 exception
classes (predicate nominals/idioms/generics) — the classification RULE is universal, correctly classifying figurative
INSTANCES is register-sensitive. **PINNED:** introduction is a universal operation; **OPEN:** direct evidence it is
empirically MORE register-robust than resolution (no comparative study; the closest evidence is mixed). **ENGINEERING:**
keep introduction rule-based/compositional (portable to 19c; patch archaic idioms/weak-definites lexically); isolate
statistical training to linking — the DRT architecture already wants the register-sensitivity to live in the linker.

## 5-line synthesis
1. INTRODUCTION: open a referent for every NP head by default (open-broad-then-revise), tagged by NP-type + reference-form — rule-driven, not a statistical gate.
2. SELECTION (crux): structural-DO hard gate → verb-conditioned thematic-fit DOMINANT graded score → animacy secondary → proximity last-resort tie-break.
3. LINKING: full-NP re-mentions get introduce-then-check; pronouns/reduced forms go straight to parallel cue-based retrieval over the open-referent pool.
4. GENERALIZATION: introduction stays rule-based/compositional (register-portable, lexically patched for 19c); the trained, register-sensitive component is isolated to linking/resolution.
5. HIGHEST-LEVERAGE single piece: a McRae/Ferretti verb-conditioned thematic-fit scorer replacing linear proximity as the DOMINANT patient-selection signal — directly targets our measured failure mode (coverage improved but nearby distractors steal the pick because proximity is over-weighted).

## Calibration
Architecture-level claims (Q1 exception classes, Q3 fit-dominant integration, Q4 form-sensitive two-stage) are
well-supported. Specific-mechanism claims (CA3 pattern-completion; a dedicated neural file-opener; register-invariance
of introduction) are OPEN/contested per the sources themselves — treat as P<=0.50 working hypotheses.
