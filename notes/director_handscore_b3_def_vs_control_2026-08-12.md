# Director hand-score: B3 audit, DEF vs CONTROL vs v2 baseline (2026-08-12)

**Scorer:** Director (main session), single judge. **This is the load-bearing measurement of the
2026-08-12 grounding arc and it previously existed only in conversation.** Persisted here so it
survives compaction and can be re-judged. The cells deliberately did NOT auto-score; the buckets
below are the director's judgement, not a cell verdict.

Rubric (from `notes/foundation_grounding_sample_2026-08-12.md`):
- **MEANINGFUL** - the object states or defines something about what the subject means
- **RELATED** - a real topical/associative link, but not defining
- **NOISE** - no real semantic link (parse error, name collision, collocation, coincidence)

Samples scored (n=50 each, seed=42, identical sampling procedure so they are comparable):
- `data/exp_definitional_grounding_v3/b3_audit_sample_DEF.json`
- `data/exp_definitional_grounding_v3/b3_audit_sample_DIST_LOWINFO.json` (control)
- v2 baseline: `data/exp_reading_grounding_loop_cycle3_groundingfix_v1/b3_audit_sample.json`

---

## RESULT

| arm | MEANINGFUL | RELATED | NOISE | facts in arm |
|---|---|---|---|---|
| v2 DIST_ASIS (baseline) | 4/50 = **8%** | 13/50 = 26% | 33/50 = 66% | 634 |
| DIST_LOWINFO (**control**) | 4/50 = **8%** | 13/50 = 26% | 33/50 = 66% | 290 |
| **DEF (definitional)** | 19/50 = **38%** | 9/50 = 18% | 22/50 = 44% | 1751 |

Pre-registered bands (`preregs/2026-08-12_definitional_grounding_v3.md`): HARD_PASS >=35% AND
>=200 facts; PASS >=18%; MIDDLE_BAND 12-18%; FAIL <12%. **DEF = HARD_PASS band on the director's
score.** The cell's own verdict remains `STRUCTURAL_PASS_PENDING_B3` - it did not and should not
claim this.

**The control is what makes the result interpretable.** DIST_LOWINFO received the step-2
mechanical fixes (never-emit-a-non-word lemmatizer, PMI low-information gate) but NOT the
definitional signal, and scored **identically to the untouched baseline**. The pre-registered
kill condition was "the control scores as well as DEF"; it did not fire. So the gain is
attributable to definitional structure, not to the bug fixes.

Note the v2 and CONTROL bucket counts are identical (4/13/33). Not an error - the mechanical
fixes changed WHICH facts survive (634 -> 290) without changing their quality distribution.

Absolute: DEF ~665 meaningful facts (0.38 x 1751) vs DIST ~51 (0.08 x 634).

---

## HONEST LIMITS

1. **One judge.** Both numbers come from the same head, so the COMPARISON is internally
   consistent but the absolute values carry the director's judgement. No inter-rater check.
2. **Borderline calls exist** and are marked below with `?`. Reasonable judges will differ on
   generic-head cases (`kidney -> pair`, `pack -> unit`) and on whether a compound-term link
   (`patch -> nicotine`) is RELATED or NOISE. The DEF/CONTROL gap (38 vs 8) is far larger than
   the plausible disagreement band, so the ranking is robust even if the levels move.
3. **The rubric scores isolated pairs**, so it is blind to context-conditioned meaning - see
   `notes/wire_reader_to_meaning_organs_2026-08-12.md`, which showed this rubric is provably
   invariant to storage representation. Do NOT reuse it to evaluate superposition work.

---

## DEF sample - per-row calls (n=50)

MEANINGFUL (19): anion->ion; anus->opening; apple->company; bubble->region (head of
"transcription bubble"); cadmium->metal; community->state ("climax community" = equilibrium
state); drosophila->fly; factor->allele; genetics->study; hydrolysis->process;
kebede->entrepreneur; lipoprotein->form; monohybrid->offspring; omikron->game; piraeus->port;
pituitary->extension; recombinant->chromosome; stimulus->change; structure->proportion ("age
structure").

RELATED (9): bowie->act (role, not meaning); cancer->collective? (truncated from "collective
name"); dialysis->medical? (adjective, head should be "process"); earlobe->characteristic?;
effect->magnification (subject truncated from "bottleneck effect"); kidney->pair? (head should
be "structure"); pack->unit?; salmon->consumer (role in a food chain); species->carp (inverted
hypernymy - carp is a species, not the reverse).

NOISE (22): afghanistan->catch; annelid->indicate; bryophyte->collectively; cell->gradient;
chytridiomycosis->die; coelom->characterize; document->access; dryad->recently; energy->proceed;
fan->expert (PERSON named Fan); gift->increasingly; habitat->resistant; kidney->ureter (list read
as appositive); policymakers->minister ("called on" misparsed); report->joy; singing->blend
(metaphor); sleep->fit; structure->function (INVERTED - source says "without function");
system->locomotion (list); technology->seller (PROPER NOUN "Currie Technologies"); use->technique;
valve->muscle (sphincters are the muscles, not the valves).

**Failure pattern in DEF noise - all fixable parsing, not deep failure:**
proper-noun/common-noun collisions (fan, technology); lists read as appositives (kidney->ureter,
system->locomotion); sentence-initial adverbials/subordinate clauses; subject truncation losing
the modifier ("transcription bubble" -> `bubble`); one polarity inversion (structure->function).
The 38% ceiling is capped by these, not by the definitional idea.

## CONTROL (DIST_LOWINFO) - per-row calls (n=50)

MEANINGFUL (4): highclere->home; okazaki->fragment; apc->antigen; lymphatic->lymph.

RELATED (13): solute->solvent; bacteria->resistant; algae->green; zone->belt; represent->meaning;
patch->nicotine?; debit->card?; coral->reef; inversion->karyotype; termination->translation;
exocrine->endocrine; motor->pns; synaptic->dendrite.

NOISE (33): gap->pay; sue->kenyan; collection->american; duke->son; cambridge->duke;
generator->use; scientist->share; experience->partner; syria->gun; advice->ascent;
sexual->experience; value->ahead; hall->algae; heroin->mad; lemon->blind; backpack->telescopic;
dancer->janeiro; bolivian->danny; whatsapp->swap; fbi->widely; paddington->mary; workman->knife;
clearance->fbi; reservoir->smith; alexandria->duncan; salad->yesterday; champ->agent;
singular->transport; glycoprotein->singular; capture->potential; generate->potential; pea->true;
lightly->clinic.

## v2 baseline - per-row calls (n=50)

MEANINGFUL (4): chromatid->sister; suit->dress; highclere->home; receive->dendrite.

RELATED (13): humoral->antigen; cassette->disk; orangutan->chimpanzee; chemiosmosis->generate;
equatorial->align; effector->macrophage; chew->leaves; fan->people?; sulphur->soot;
mutated->tumor; tissue->multicellular; deoxygenated->cava; spine->skull.

NOISE (33): remainder, incl. sky->status, advice->ascent, moth->sauce, yard->leicester,
duke->son, artery->arteri (STEMMING VARIANT of the same word - a tautology that escaped the gate
because the strings differ; root-caused and fixed, see
`notes/definitional_grounding_v3_2026-08-12.md` section 3a).
