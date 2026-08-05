# GOLD-VET (AUDIT-ONLY): goal_outcome_oov_psych_v1.jsonl

**Auditor:** skunkworks (independent, off-disk, in-process). **Bank:** `experiments/data/goal_outcome_oov_psych_v1.jsonl` (21 items, built @ 0b8f2f2b9). **Purpose being certified:** trustworthy instrument to measure the OOV frame-induction wire's goal-OWNER value. Triple-checked per standing rule (VET load-bearing data as hard as a positive). Deflationary, measured per-item.

## Recompute summary (off-disk)
- **OOV axis: 21/21 CONFIRMED.** Every `goal_verb_lemma` (resent, detest, abhor, disdain, relish, worship, cherish, scorn) is genuinely NOT in `hdlab.thematic_role_labeler.PSYCH_VERBS` (recomputed against the live set, not the field). All are real psych/experiencer verbs. `is_oov` fn does not exist on the module; membership check used directly. No mislabels on OOV.
- **No duplicate/near-duplicate `text`.** 0 dup windows.
- **Verb dist:** cherish 6, resent 6, detest 2, disdain 2, relish 2, abhor 1, worship 1, scorn 1 — **skewed: cherish+resent = 12/21 (57%)**.
- **Polarity:** blocked 12, achieved 8, mixed 1 — moderately blocked-skewed.
- **dist_bucket:** dispersed 8, near 7, adjacent 6 — **well balanced (only clean axis).**
- **Window:** every item `window_backward_sentences=0` and `owner_named_antecedent_idx==goal_sentence_idx`; the owner name (where it is a real entity) sits in the goal sentence itself. The old bank's out-of-window antecedent flaw is structurally fixed — the residual problems are PARSE/GOLD errors, not window width.

## Per-item owner-gold verdict (the load-bearing field)

WRONG OWNER (5) — experiencer mis-identified:
- **#6 (evelina)** owner=`Frenchman` WRONG. `...I'm no Frenchman, and should relish...` — experiencer is the elided "I" (the Captain); "Frenchman" is a PREDICATE NOMINATIVE, not the subject. Not even a named entity.
- **#8 (tenant of wildfell hall)** owner=`Christian` WRONG. `No true Christian could cherish such bitter feelings as I do...` — main-clause subject is the generic, NEGATED "No true Christian"; the real feeler is "I". Not a real entity.
- **#17 (vanity fair)** owner=`Crawley` WRONG. `...amongst her most cherished personal treasures.` — "cherished" is an ATTRIBUTIVE ADJECTIVE, not a finite psych verb; the possessor is "her" = the companion (Briggs). Owner should be Briggs; foil is literally `Briggs` (inverted). Also fails OOV-verb-in-spirit (not a goal verb usage).
- **#18 (oliver twist)** owner=`Oliver` WRONG. `his [Fagin's] having taken Oliver in, and cherished him` — Oliver is the OBJECT; experiencer is Fagin.
- **#21 (main street)** owner=`Girls` WRONG. `she relished the Camp Fire Girls` — "Girls" is the OBJECT; the pronoun "she" (Carol) mis-resolved to the object. Not a named individual.

BROKEN CONSTRUCTION / LEAKY (1):
- **#1 (of human bondage)** owner=`Mary`, foil=`Ann` — both are halves of the single name "Mary Ann" (one servant). Owner name truncated; foil is a FRAGMENT OF THE OWNER'S OWN NAME. A system answering "Mary Ann"/"Ann" mis-scores. Exclude.

OWNER CORRECT (13): #2 Craven, #3 Elizabeth, #4 Clare, #5 Queequeg, #7 Ernest, #9 Ahab, #10 Emily, #11 Johann, #12 Dave, #13 Ottenburg, #16 Cadwallader, #19 Mary, #20 Barbara.
- Caveats within these: **#16** owner "Cadwallader" is ambiguous Mr/Mrs (both in-passage) but points to the experiencer entity. **#13** owner correct (surname of "Otto Ottenburg") but the window is garbled/thin ("...had long owned and cherished." fragment).

## Secondary-gold problems (outcome + foil)

**Outcome polarity gold is systematically unreliable.** The `outcome_span` is auto-extracted TRAILING text of the window, frequently causally disconnected from the goal:
- Outcome-span UNRELATED to the goal (trailing narration about a different character/action): #1 (Philip dressing vs Mary Ann's meal-resentment), #3 (carriage-horses to Bath), #4 (a gravestone inscription), #11 (Flavia's arrival), #15 (Pappleworth's arrival), #16 (Miss Brookes' marriage prospects), #20 (Lady Richmond losing election-thought). Also loose: #19.
- **#14 (little women) polarity INVERTED:** `cherished them... all were fed and clothed, nursed and caressed with an affection which never failed` describes Beth SUCCEEDING; gold says `blocked` — should be `achieved`.
- **#5 (moby)** the lone `mixed` label; goal (learn among Christians / gain power) ends `gave it up for lost` = blocked, not mixed. Also the goal-verb "disdained no ignominy" (double-negative) is not the actual desire verb ("gain").

**Foil quality (for `_foil` structure_types that should carry a real person distractor):** 4 items have NON-PERSON foils that weaken the discriminator (owner becomes the only real person -> task easier than intended): **#3 foil=`Bath` (place)**, **#4 foil=`Conqueror` (gravestone word)**, **#5 foil=`Nantucket` (place)**, **#9 foil=`Christians` (generic plural)**. (#15 foil=`French` is a language; #17 foil=`Briggs` is the true owner.) The `_nofoil` variants (foil=null: #10,#11,#12,#19 + #13) are legitimate single-target by design.

## Clean-item count

- **Goal-OWNER usable (owner-correct + OOV + in-window + non-leaky): 13/21.** (Excludes 5 wrong-owner + #1 broken.)
- **STRICT clean (owner-correct + OOV + in-window + valid-foil-or-legit-nofoil + non-inverted outcome): 9/21** = #2, #7, #10, #11, #12, #13, #16, #19, #20. (Further drops #3,#4,#5,#9 for broken foils and #14 for inverted polarity.)

Either way **< 15**.

## VERDICT

**NOT a trustworthy instrument as-shipped. Needs fixes / SUPPLY more before it measures the OOV wire's goal-owner value.**

- The OOV construction is sound (21/21 genuine OOV psych verbs, well-balanced dist_bucket, no dups) — the wire-stress premise holds.
- But the goal-OWNER gold — the exact field the instrument exists to score — is wrong on 5/21 and construction-broken on 1/21, all from a shared failure mode: the subject-name grabber takes predicate-nominatives (#6), generic negated subjects (#8), attributive-adjective heads (#17), and coordinated/pronoun OBJECTS (#18, #21) as the experiencer. A wire scored against these 6 gets penalized for being right (or rewarded for being wrong). 13 owner-clean < 15.
- The outcome-polarity axis is separately unreliable (trailing-text spans, one inverted label, one dubious "mixed") and should NOT be used as gold without re-annotation.
- Foils are contaminated with places/languages/generics on 4-5 items, easing the discrimination.

## Gold-reviewed subset cross-check (goal_outcome_oov_psych_gold_v1.jsonl, N=6)

Coordinator points to a gold-reviewed subset as the primary bank. I VET'd it independently against my raw-21 findings (this IS my job; running the ablation is not — see boundary note).

**Subset membership CONFIRMED sound.** The 6 kept items = #5 Queequeg, #7 Ernest, #9 Ahab, #12 Dave, #13 Ottenburg, #19 Mary(persuasion s2596) — ALL 6 are inside my independent "owner-correct 13" set. Zero owner-gold conflict. My audit independently reached the reviewer's drop rationale: my 5 wrong-owner items (#6,#8,#17,#18,#21 = predicate-nominative / negated-generic / attributive-adjective / object-as-owner / mis-resolved-pronoun) map to the reviewer's "roster false-positives"; my #1 = the reviewer's "name truncation"; my "trailing-text outcome" cluster = the reviewer's "topic-blind outcomes." Convergent, not rubber-stamped.

**Gold corrections all agree with my per-item flags:** #5 outcome mixed->blocked (my "should be blocked"), #9 kept owner-only / outcome->mixed (my "foil generic, owner good"), #13 truncation-noted (my "garbled fragment"), #19 auto=achieved->blocked (my "outcome questionable/backwards"). #7 and #12 = gold_confidence HIGH = my two "GOOD" items. Confidence spread on the 6: high 2 (#7,#12), medium 2 (#5,#13), low_medium 1 (#9), low 1 (#19).

**CRITICAL — effective testable N is ~3, confirmed off the on-disk `sanity_frame_primary_subj_role`:**
- NOT_FOUND (goal event NOT extractable -> role-typing untestable): #5 (disdain, clause), #13 (cherish, VP-coordination gap — extractor caught only "owned"), #19 (resenting, participial non-finite). = 3/6 dropped UPSTREAM of the OOV wire by the production event extractor.
- Extractable (3/6): #7 Ernest -> AGENT, #9 Ahab -> AGENT, #12 Dave -> EXPERIENCER.

**Directional read on the 3 testable items (NOT powered):** the OOV-induction wire produced the correct EXPERIENCER typing on 1/3 (Dave) and abstained-to-AGENT-default on 2/3 (Ernest, Ahab). Against an always-AGENT baseline (0/3 experiencer on these psych-subject items), the wire is +1 item (1/3 vs 0/3). At N=3 this is a DIRECTIONAL signal only — not a win, not a loss, not powered. Do NOT report it as a rate. Owner/subject EXTRACTION (who holds the goal) was correct 6/6; the induction ROLE-TYPING is the axis that fired only 1/3-testable.

**Role boundary (AUDIT-ONLY):** I did not author or execute an ablation cell — that is exp_dev/Director's to run, and running the instrument I just certified would break the role-separation that this audit exists to protect. The 1/3-vs-0/3 above is read directly off the `sanity_frame_primary_subj_role` values already on disk in the gold file, not from a cell I dispatched. A properly powered ARM-OOV-INDUCED vs ARM-AGENT-DEFAULT run needs the event-extractor gaps (participial + VP-coordination) fixed first so N recovers past 3, else it stays a directional probe.

**Routing:** REJECT for outcome-scoring. For owner-scoring, either (a) FIX the 6 bad items (re-extract the finite-verb subject; drop attributive-adjective #17; fix #1 name/foil) and re-validate foils on #3/#4/#5/#9, or (b) SUPPLY ~8-10 more items to clear a >=15 clean-owner floor with real-person foils and a de-skewed verb mix (cap cherish/resent). Do not use as the sole instrument for this session's OOV wire until >=15 owner-clean items with valid foils exist.
