# Brain-faithfulness of the role-assignment fixes: quotative inversion, copula, linear-position fallback

Research drill for SOLVER `wire_the_predarg_frontend_and_binder_into_the_live_reader`.
Date: 2026-08-29. Author: hdi_research (Director). Lit-scan calibration penalty applied.

## Bottom line (verdict table)

| Fix | Brain-faithful? | Basis |
|---|---|---|
| **Quotative: speech-verb + postverbal animate = AGENT/speaker; quote is NOT a role filler** | **PINNED in principle, OUR-INVENTION in mechanism** | speaker=agent is the lexical/frame semantics of communication verbs (FrameNet/VerbNet), reinforced by animacy proto-agent prominence (eADM). The *positional-override rule* is an engineering approximation of the brain's verb-class + animacy computation; no direct ERP/RT study isolates "said Mary" online. |
| **Copula: post-copular nominal = predicate/attribute (theme/attribute), NOT agent/object; copula assigns no agent** | **PINNED by linguistic theory** (weaker neuro-evidence) | Copula is semantically light and assigns no agent theta-role / no macrorole (generative theta-theory; Van Valin RRG). The predicate nominal specifies a property of the subject referent. |
| **Linear-position fallback (use arg-structure when parse gives it, else linear order)** | **PINNED** | This *is* the good-enough dual-route architecture (heuristic NVN first / algorithmic parse second) + noisy-channel rational inference. English relies primarily on linear position for prominence (eADM). |
| **(Bonus) parse-first pipeline SHAPE** | **OUR-INVENTION in shape, functionally admissible** | Brain assigns roles incrementally/lexically from verb-specific expectations + thematic fit + animacy *before/without* a complete tree (Altmann & Kamide; McRae; MacDonald). Parse is a legitimate constraint *source*, not a faithful *gate*. |

---

## 1. Quotative inversion / speaker-role assignment

**How the parser assigns AGENT to a postverbal speaker.** Two independently-pinned mechanisms converge, and both point the same way:

- **(a) Verb-class / construction semantics — PINNED.** Communication/"say" verbs lexically specify a Speaker (=Agent/proto-agent) and a Message (=theme/content complement). In frame semantics (FrameNet *Statement/Communication* frames; VerbNet `say-37.7`) the animate arguer is the Speaker regardless of surface position; the quoted string fills the *Message* slot, which is a clausal/complement content role, **not** a competing nominal argument. Construction Grammar (Goldberg 1995) makes this explicit: argument-structure meaning is carried by the construction + verb class, not read off linear NP positions. So "the quote is not a role filler for agent/object, and the animate is the speaker" is grounded in the *lexical semantics of the verb class*, which is exactly what your fix encodes.
- **(b) Proto-agent / animacy prominence — PINNED.** The extended Argument Dependency Model (eADM; Bornkessel-Schlesewsky & Schlesewsky 2006, *Psychological Review* 113:787-821, PMID 17014303) has comprehenders compute prominence over arguments from animacy, voice, case and linear position, assigning the highest generalized role (actor/proto-agent) preferentially. An animate ("Mary", "papa", "Joe") is the actor candidate; an inanimate in an actor slot yields an N400 (role-prototypicality mismatch). Sauppe et al. (2023, *Cognitive Science* 47:e13340) show a cross-linguistic **agent-first preference** even in a patient-first language, i.e. actor assignment is early and automatic.

**Is it early/automatic?** Role assignment from the verb is anticipatory: Altmann & Kamide (1999, *Cognition* 73:247-264) and Kamide, Altmann & Haywood (2003, *JML* 49:133-156) show the verb's argument expectations drive fixations *before* the argument is encountered. Speech-verb / dialogue attribution is processed online in reading: Stites, Luke & Christianson (2013, *Memory & Cognition*, "The psychologist said quickly, ...") show dialogue-descriptor verbs modulate reading speed of the quoted content — readers use the attribution verb immediately.

**Honest gap (SPECULATIVE).** The syntactic literature on English quotative inversion is rich (Collins & Branigan; Bruening 2016, *Syntax*, "Alignment in syntax: Quotative inversion in English") but it is **structure**, not **online role assignment** — I found **no ERP/reading-time study that isolates speaker-role assignment in postverbal-subject "said Mary" specifically.** So: the *components* (verb-class Speaker semantics + animacy proto-agent + online speech-verb use) are PINNED; the claim that the brain resolves *this exact construction* by them is a well-supported inference, not a directly measured result. Your **positional "postverbal-animate speaker" rule is OUR-INVENTION** — the brain doesn't run a position rule, it runs verb-class expectation + animacy prominence that *happen to* yield the postverbal animate as agent. The fix is more brain-faithful than the nearest-preverbal-nominal baseline it replaces (that baseline is itself the good-enough NVN heuristic, see §3), but label the *mechanism* as an approximation.

## 2. Copula / predicate-nominal roles

**PINNED by linguistic theory.** The copula "be" is semantically near-empty and, unlike lexical verbs, **assigns no agent theta-role**; in Role and Reference Grammar (Van Valin) the copula is not a role-assigning predicate and licenses **no macroroles** (no actor/undergoer) — the *predicate nominal itself* is the predicate, and the subject NP is its argument. Semantically the post-copular nominal specifies a **property/attribute** of the subject referent (predicational copula) or an identity (equative), i.e. an attribute/theme, never an agent or a patient of an action. So "Two friends were Willie and Bounce" / "the name is Dodger": neither nominal is an agent; the post-copular nominal is a predicate-nominal/attribute.

**Caveat.** This is grounded in *grammatical theory* (theta-theory, RRG, FrameNet has no agent in copular *Being/Attributes* frames), with **less direct neuro/processing evidence** than §1/§3. Treat your copula fix as **PINNED-by-theory, neuro-unpinned** — solid, but flag the evidence class.

## 3. Good-enough / linear-position fallback

**PINNED — this is a mainstream model of human reading, not a hack.**

- **Dual-route good-enough processing.** Ferreira, Bailey & Ferraro (2002, *Current Directions* 11:11-15); Ferreira & Patson (2007, *Lang. & Ling. Compass* 1:71-83). Comprehenders run a **heuristic route first, algorithmic (full-parse) route only under demand**. The core heuristic is the **NVN strategy**: first noun = agent, second = patient (Ferreira 2003, *Cognitive Psychology* 47:164-203). Non-canonical structures (passives, clefts, *and postverbal-subject constructions*) violate NVN and are error-prone — which is exactly why your *baseline* mislabels the quotative speaker as object: it is running the brain's own default heuristic, and the brain makes the same error unless a stronger cue overrides it.
- **Misassigned roles linger.** Christianson, Hollingworth, Halliwell & Ferreira (2001, *Cognitive Psychology* 42:368-407) and Slattery, Sturt, Christianson, Yoshida & Ferreira (2013, *JML* 69:104-120): initially heuristic-assigned thematic roles persist even after reanalysis — evidence the heuristic route is real and primary.
- **Noisy-channel rational inference.** Levy (2008, EMNLP, "A noisy-channel model of rational human sentence comprehension under uncertain input"); Gibson, Bergen & Piantadosi (2013, *PNAS* 110:8051-8056). Comprehenders combine a prior with a noise model and can *override* the literal parse when structure is unreliable — the principled version of "use argument structure when the parse is trustworthy, else fall back."
- **eADM** independently states English computes prominence **primarily from linear position** — so linear-order role assignment is the language-specific default the brain uses for English, not a degenerate fallback.

**One directional nuance.** The brain does **heuristic/linear FIRST, full-parse as correction**; your pipeline is "parse → route args, *else* linear." Functionally equivalent as a hybrid, but the brain-faithful framing is the reverse ordering (cheap linear/lexical cue is primary; parse refines/corrects). Not a defect — just describe it as a hybrid, and note that the parse is a *constraint source*, not a gate.

## 4. Is a dependency PARSE the right substrate? (pipeline shape)

**Evidence says roles are assigned incrementally and lexically, before/without a complete syntactic tree** — so a strict "parse → then route" shape is **OUR-INVENTION in shape** (though functionally admissible):

- Verb-specific expectations drive role/filler prediction anticipatorily (Altmann & Kamide 1999; Kamide et al. 2003): "the girl will ride" → carousel; "the man will ride" → motorbike — argument goodness-of-fit computed at the verb, before the object exists.
- Thematic fit / constraint-satisfaction: McRae, Spivey-Knowlton & Tanenhaus (1998, *JML* 38:283-312); McRae, Ferretti & Amyote (1997, *Lang. & Cognitive Processes* 12:137-176) — roles are **verb-specific concepts** graded by typicality, integrated simultaneously with syntax. MacDonald, Pearlmutter & Seidenberg (1994, *Psych. Review* 101:676-703): syntactic ambiguity resolution is **lexically driven constraint satisfaction**, not tree-first.

**Implication for the pipeline.** The most brain-faithful frame is **constraint satisfaction where verb-class argument expectations + animacy/thematic-fit are first-class cues and syntax is one constraint among them**, not a prerequisite. Your `parse → route arguments` recovers the same structure and is a legitimate engineering substrate, but: (i) call the dependency parse a *constraint source*, not the *seat* of role assignment; (ii) your §1 and §3 fixes are actually **moving toward** the brain's model — they inject verb-class/animacy and linear-position cues *on top of* the parse, which is exactly the multi-cue constraint-satisfaction the brain uses. That is a fidelity *gain*, not a patch.

---

## How to state it in the writeup

- **Quotative-inversion fix:** speaker=agent + quote-as-message(not-filler) is **PINNED-by-evidence** (communication-verb frame semantics + eADM animacy proto-agent; anticipatory verb-driven role assignment). The **positional postverbal-animate rule = OUR-INVENTION-UNDER-TEST** — a faithful *approximation* of the brain's verb-class+animacy computation; no ERP/RT study directly pins this exact construction online (state that gap).
- **Copula fix:** post-copular nominal = predicate/attribute, copula assigns no agent = **PINNED-by-linguistic-theory** (theta-theory / RRG macroroles); neuro-evidence thinner — flag evidence class.
- **Linear-position fallback:** **PINNED-by-evidence** — it is the good-enough NVN heuristic + noisy-channel rational inference + eADM's English linear-position default. Note the brain does heuristic-first/parse-second (mild ordering inversion from your pipeline; still a faithful hybrid).
- **Pipeline shape:** roles are assigned incrementally/lexically before a full tree — reframe the parse as a **constraint source** within multi-cue constraint satisfaction, not a gate. Your fixes push toward this, which is the fidelity direction.

## Prior arc work (experiment_index)
- `exp_quotative_speaker_attribution_stack_break050_v1` (2026-07-19, HARD_PASS_QUOTATIVE_BREAKS_050)
- `exp_interactive_loop_real_gold_mcguffey_v1` (2026-08-02, HARD_PASS_RESOLVES_QUOTATIVE)
- `exp_c5_quote_speaker_wired_v1` (2026-08-05, PARTIAL)
- Thematic-fit lineage: `exp_graded_thematic_fit_integrated_reader_gate_v1`, `exp_consolidated_reader_passive_mechanism_heldout_v1`.
- Copula: no substantive prior cell — this is a fresh residual.

## Primary sources
- Bornkessel-Schlesewsky & Schlesewsky (2006). eADM. *Psychological Review* 113(4):787-821. PMID 17014303.
- Sauppe et al. (2023). Agent-first preference. *Cognitive Science* 47:e13340. doi:10.1111/cogs.13340.
- Altmann & Kamide (1999). *Cognition* 73(3):247-264. doi:10.1016/S0010-0277(99)00059-1.
- Kamide, Altmann & Haywood (2003). *JML* 49(1):133-156.
- McRae, Spivey-Knowlton & Tanenhaus (1998). *JML* 38(3):283-312.
- McRae, Ferretti & Amyote (1997). *Language and Cognitive Processes* 12(2-3):137-176.
- MacDonald, Pearlmutter & Seidenberg (1994). *Psychological Review* 101(4):676-703.
- Ferreira (2003). *Cognitive Psychology* 47(2):164-203.
- Ferreira, Bailey & Ferraro (2002). *Current Directions in Psychological Science* 11(1):11-15.
- Ferreira & Patson (2007). *Language and Linguistics Compass* 1(1-2):71-83.
- Christianson, Hollingworth, Halliwell & Ferreira (2001). *Cognitive Psychology* 42(4):368-407.
- Slattery, Sturt, Christianson, Yoshida & Ferreira (2013). *JML* 69(2):104-120.
- Levy (2008). Noisy-channel model. EMNLP 2008:234-243.
- Gibson, Bergen & Piantadosi (2013). *PNAS* 110(20):8051-8056. doi:10.1073/pnas.1216438110.
- Goldberg (1995). *Constructions: A Construction Grammar Approach to Argument Structure*. Univ. of Chicago Press.
- Van Valin (2005). *Exploring the Syntax-Semantics Interface* (Role and Reference Grammar; copula/macroroles). Cambridge UP.
- Stites, Luke & Christianson (2013). "The psychologist said quickly...". *Memory & Cognition*. PMC3540141.
- Bruening (2016). Alignment in syntax: Quotative inversion in English. *Syntax* 19(2) (syntactic structure only; not online processing).

## TLDR (plain language)
Your three reading fixes match how the human brain is known to read.
1. Treating the speaker after "said" as the doer — and treating the quoted words as the *thing said* rather than a person — is how people handle speech verbs: the brain knows "say"-type verbs come with a speaker, and it favours the living thing as the doer. Solid evidence, though no study has tested this exact "said Mary" flip directly, so call the *rule you wrote* a faithful stand-in, not a measured mechanism.
2. Treating "X is Y" as describing X (not X doing something to Y) is correct: the verb "to be" hands out no doer role. This rests on grammar theory more than brain scans.
3. Falling back to word-order (first noun = doer) when the parse is shaky is exactly what tired human readers do — a well-established "good-enough" shortcut, backed by strong evidence.
One deeper point: the brain assigns these roles *as it reads each word*, using the verb's expectations, not by finishing a full grammar tree first. So describe your parser as *one source of hints* feeding role assignment, not the gatekeeper — your fixes already lean that way, which is the right direction.

## Questions
None.

## Next steps
1. In the writeup, tag each fix per the verdict table: quotative = PINNED-principle/OUR-INVENTION-mechanism; copula = PINNED-by-theory; linear fallback = PINNED.
2. Add the single honest caveat that no ERP/RT study isolates the postverbal-speaker "said Mary" construction online — the pin is componential (verb-class + animacy + anticipatory role assignment), not construction-specific.
3. Consider (optional, later) reframing the binder as multi-cue constraint satisfaction (verb-class expectation + animacy + linear position + parse) rather than parse-gated routing — that is the higher-fidelity version if the copula/quotative residuals persist.
