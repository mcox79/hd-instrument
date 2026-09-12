# RESEARCH — valuing the RESULT STATE, not the verb's word rating (pri-14; strategy, 2026-09-12)

**Question.** The harm/help arithmetic read the patient's outcome valence from the verb's word-level affect norm
(Warriner). That norm conflates senses: *throttle* rates mildly positive (engine sense), *batter* near-neutral (food),
*bludgeon* has no norm. The organ abstained (batter, bludgeon, wrench, pummel, maul) or mis-signed (throttle, club → HELP).
How does the brain value this, and can the substrate replicate it from its own foundation assets, with no verb list?

**Brain.** Outcome valuation (OFC/vmPFC value; amygdala) is over the STATE the agent ends up in, reached by simulating
the event (Barsalou; Zwaan situation simulation). Causative verbs lexicalise a RESULT STATE (Levin / Rappaport Hovav);
the verb's lexical pleasantness is only a cue to that state. Forceful contact on one's body is aversive innately
(nociception) — a PINNED sign, not a learned rating.

## What was tested (all on the solver's populations of `exp_fd_harm_help_arithmetic_v1` + a 12-verb recovery set + the
## 36-item live board gold; consistency = agreement with the word-level sign where both exist over 2,926 affecting verbs)

| channel (offline foundation asset) | recovers (of 12) | consistency with word sign | verdict |
|---|---|---|---|
| word-level norm only (the organ before) | 5 (2 wrong: throttle, club → HELP) | — | the defect |
| WordNet gloss content-word valence, SemCor-weighted, as a FALLBACK | 9 | 0.81 (n=1470) | noisy proxy: glosses describe the MANNER ("strike with a club"), not the state; as a FIRST read it breaks punch/slap/beat/choke → HELP. NOT landed |
| VerbNet class semantics, all classes of the lemma | 11 | 0.84 (n=87) | right source, but a lemma's classes mix senses (impress/strike) |
| WordNet hypernym inheritance of the result state (depth 1–2) | 12 | 0.65–0.75 | REJECTED: routes through rare senses (fry = electrocute; dress → harm); the is-a channel over-reaches again (cf. the refuted pri-1 taxonomic lever) |
| same-synset lemma ("synset-mate") result state | 11 | 0.75 | REJECTED: reads every class of the mate lemma, not the class for THAT sense (touch/impress/excite → HARM) |
| **VerbNet SENSE-KEYED (MEMBER wn keys) × affecting ANIMATE-OBJECT senses (WordNet frames 9/10/17/18)** | **10 (+2 honest abstentions: wrench, maul)** | **0.87 (n=79); all 10 disagreements = weapon/assault senses correctly read for a person** | **LANDED** |

The landed read: for each affecting sense of the verb that takes an animate object, look up the sense key in the VerbNet
asset → the class's result/end-state predicates over the Patient → value the STATE: `harmed`, `suffocate`,
`degradation_material_integrity`, `!alive` via the affect lexicon's valence of the state word (negation flips);
`manner(forceful) ∧ contact(end(E))` = the innate nociceptive sign (−1). Mean over evidence; |value| ≥ 0.5 decides;
otherwise the word-level norm is consulted; otherwise abstain. VerbNet asserts `harmed` only where harm is
sense-intrinsic (poison-42.2: stab, strangle, poison) and `forceful contact` for hit/spank classes — which is exactly right:
hitting a table is not harm; the arithmetic's animacy gate supplies that.

**Numbers after landing (witness `verification/test_fd_result_state_arm.py`, 15/15):** recovery 9/9 HARM (batter,
bludgeon, pummel, club, throttle, clobber, wallop, thrash, whack); wrench/maul abstain (no animate-contact sense with a
result state in the foundation; weak norm); harm-frame 10/10; social-harm 14/16 and help 14/16 (= the word-only read;
oppress/tend abstain as before, one verb each held by the affectedness gate); NO neutral verb reads HARM/HELP; no
wrong-sign decision; twin (asset states re-assigned to random WordNet sense keys) 0/5 vs real 5/5 on the
state-decided verbs; asset absent → word-level fallback, batter abstains (no hidden list). Coverage over 2,926 affecting
Warriner verbs: 105 carry a result state; 31 formerly-abstaining verbs now decided (bang, batter, bump, cane, clip, crush,
cuff, extinguish, grate, lash, mash, muffle, neutralize, nip, paddle, pound, repress, scald, scratch, slam, slash,
squeeze, strap, whop …), all HARM — VerbNet has no positive result-state predicate; HELP continues to come from the
word-level norm, which is the faithful read where VerbNet's `emotional_state`/`state` constant IS the verb (comfort, heal).

**Remaining boundary (with numbers).** 822 of 2,926 affecting verbs still abstain (no result state in the foundation and
a weak/absent norm); wrench, maul, oppress, tend among the probe sets. The next faithful step is sense-IN-CONTEXT
selection (the `select_sense` program) choosing WHICH sense's result state applies, and a positive result-state source
(VerbNet has none). The gloss channel (0.81) is a measured, NOT-landed second opinion; do not land it as a first read.

**Do not redo:** synonym-lemma valence averaging (withdrawn 2026-09-12), hypernym inheritance (0.65–0.75), synset-mate
class reads (0.75), gloss-first (breaks harm-frame verbs). Scratch probes: scratchpad `probe_resultstate*.py`,
`probe_verbnet_state*.py` (session 95c182ee).

**Pointers.** Asset `data/frontend_assets/verbnet_result_state_v1.json` (233 sense keys; builder
`tools/build_verbnet_result_state_asset.py`, ~5 s, from the nltk VerbNet corpus — offline foundation, admissible per
the 2026-07-14 pivot); organ arm `hdlab/force_dynamics_valence.py` (`result_state_value`, `result_state_evidence`,
`state_value`, `endstate_valence_sign` state-first); problem brief pri-14 (`notes/problems/the_harm_help_read_needs_the_affective_value_of_the_resulting_state_not_the_verbs_word_valence/PROBLEM.md`) §9.
