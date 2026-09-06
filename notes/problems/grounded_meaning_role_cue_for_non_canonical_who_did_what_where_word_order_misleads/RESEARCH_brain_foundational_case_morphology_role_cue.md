# RESEARCH — is the by-phrase case-morphology role cue brain-foundational? (2026-09-05)

Focused primary-source drill (research sub-agent + solver vetting) on the mechanism this problem lands: a
by-phrase CASE-MORPHOLOGY cue for who-did-what AGENT on non-canonical (passive) clauses, and the status of the
grounded-meaning located negative. **Honest PINNED / SPECULATIVE / REFUTED split; citations the drill could
independently verify are marked, and the ones it could not are flagged so the mechanism rests only on the real.**

## PINNED (the mechanism can rest on these)

1. **Role assignment is graded parallel CUE COMPETITION weighted by CONDITIONAL cue validity.** MacWhinney,
   Bates & Kliegl (1984, *J. Verbal Learning & Verbal Behavior*) — the foundational cross-linguistic Competition
   Model paper: cue validity = availability × reliability, and English is **word-order-dominant** while
   case/agreement-marking languages weight morphology higher. On a construction where word order is neutralized
   (passive), its validity craters and the next-highest-validity cue decides. This is exactly the additive
   cue-activation → softmax posterior the substrate's `graded_competition` implements (McClelland 2013). PINNED.

2. **Case / adposition marking is a fast, high-validity ACTOR-prominence cue.** Bornkessel-Schlesewsky &
   Schlesewsky's eADM (Bornkessel & Schlesewsky 2006, *Psychological Review*; and later actor-competition work):
   morphological case is a rapid prominence feature used to identify the actor, integrated with animacy and
   position. The by-phrase in an English passive is the oblique realization of the demoted external argument —
   so "reward the by-governed NP as the agent" is a **principled instance** of case-as-prominence, not an
   ad-hoc surface hack. PINNED at the architectural level.

3. **Grounded/lexical thematic fit is a disambiguation-under-UNCERTAINTY cue whose weight COLLAPSES once a
   reliable marker is present.** Trueswell, Tanenhaus & Garnsey (1994, *JML*): plausibility affects parsing at
   the point of ambiguity; an unambiguous morphological cue removes the plausibility effect. Gibson, Bergen &
   Piantadosi (2013, *PNAS*, noisy-channel): role-reversal/plausibility interpretation rises monotonically with
   surface-signal noise and contributes ~nothing when the marker is clear. **This directly predicts the
   solver's located negative:** on a by-MARKED passive the morphology is the reliable marker, so grounded fit
   adds nothing — exactly what was measured (grounded ties its info-free twins on the by-marked slice). PINNED.

4. **The English passive by-phrase spells out the EXTERNAL ARGUMENT** (Bruening 2013, *Syntax*; Wasow 1977;
   Levin & Rappaport 1986) — which can be an agent, causer, experiencer, or instrument ("frightened by the
   noise", "scratched by topaz"). PINNED, and a caveat: "who-did-what" as an external-argument reader is fine,
   but a schema that DISTINGUISHES agent from causer/experiencer would mislabel some by-phrases. Our reader
   answers external-argument who-did-what, so this is acceptable; noted for downstream.

5. **~80% of English passives are AGENTLESS (no by-phrase).** Quirk, Greenbaum, Leech & Svartvik (1985);
   Huddleston & Pullum (2002). PINNED, and structurally important: the by-morphology cue can only fire on the
   by-MARKED minority. The agentless majority has **no clause-internal agent to assign** — it is a
   discourse/coref/generic-agent problem, a DIFFERENT organ, not a role-cue wall this cue should cross.

## SPECULATIVE / CORRECTED (do NOT rest the mechanism on these)

- **No paper tests English "by"-as-agent-cue DIRECTLY.** The Competition-Model cue-validity studies are on
  case-INFLECTION languages (German/Italian/Hungarian nominative-accusative). Applying it to the English
  by-phrase is a well-motivated EXTENSION BY ANALOGY, not a directly precedented finding. Treat "by marks the
  agent cue" as PINNED-by-architecture, HYPOTHESIS-by-letter.
- **"Animacy captures most of the noun-side fit signal" is NOT well-supported in the literature** — it is an
  observation in OUR data (animate-agent baseline already 0.70), not an established fact. The SOLVED.md must
  state it as a data observation, not a general claim. (The fit-gate line's own generalization study put the
  noun-side ceiling at ~0.65 balanced-OOV regardless of representation, which is consistent but distinct.)
- **The brain's version is PROBABILISTIC, not a categorical override.** Ferreira (2003, *Cognitive Psychology*):
  comprehenders sometimes adopt the plausible (role-reversed) reading even against a clean passive by-phrase —
  so a HARD override is too strong. Our cue is an additive support inside a softmax competition (it can be
  outvoted), which already approximates this; a GRADED voice-confidence weight is the fuller fidelity step.
- A hypothesized "Chomsky 1970" by-phrase citation was REJECTED by the scan in favor of Wasow 1977 / Levin &
  Rappaport 1986. Do not cite Chomsky 1970 for this.

## What this licenses for the build
The by-phrase case-morphology AGENT cue is **brain-foundational at the architectural level** (Competition Model
cue-competition + eADM case-as-prominence), PINNED as an operation, HYPOTHESIS as the specific English "by"
letter. The grounded-meaning located negative is **exactly what noisy-channel theory predicts** on
morphologically-marked constructions (Gibson 2013). Two honest bounds carried into SOLVED.md: (a) the cue's
scope is the by-MARKED minority (~20% of passives; the agentless majority is a coref problem); (b) the fully
brain-faithful form is a GRADED voice-prominence cue, not a hard gate — the current additive-softmax cue is a
faithful first approximation and the graded version is the named next step.
