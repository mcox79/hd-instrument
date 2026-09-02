---
priority:
review: EXCELLENT
review_text: "Reverified 36/36 first-hand. A rigorous, brain-foundational positive with an honestly-located open-text residual (hence PARTIAL, but a FULL PASS as a located result). The mutable WORLD-STATE register -- POSSESSION have(holder,obj) + a PRECONDITION-READ layer as STRIPS operators, the genuinely-missing dimension (at/open already existed as location_register/state_register; the solver did NOT rebuild them) -- answers who-has-X-at-t 1.000 vs the strongest stateless floor last_obj_mention 0.750 (+0.250 CI-sep), all three info-free twins (order-shuffle 0.546, bind-shuffle 0.659, empty 0.250) LOSE CI-sep, and the change-point positive control flips 100%/0%. Precondition-read detects violations 1.000 vs ever-had 0.512 (+0.488). Operators FROM WHAT WE HAVE (FrameNet: 105 transfer verbs / 13 frames, WITH the recipient role the stock front-end lacked) and LEARNABLE (OOV transfer verbs induced from observed possession transitions recover FrameNet gold 1.000 vs shuffle 0.417 CI-sep, abstains on non-transfer). Open text via the substrate's OWN parser (MCScript2, 1467 transfer instances): recipient now recoverable, residual precisely LOCATED to coref (81% pronoun agents) + recipient-PP + verb-sense -- all NAMED existing organs, NOT the mechanism. The downstream serve-test honestly confirms the register does NOT break the ~0.59 before/after order wall (order is conventional, not state -- the register is correctly a STATE organ). WIRE LANDED (Q111): hdlab/world_state_register.py + hdlab/possession_operators.py promoted verbatim; default-off track_world_state flag on SituationReader -> sm.world_state (has/holder_of/is_open/unmet_preconditions), driven by the reader's own events; witness test_world_state_register_landing_organ.py. Grade EXCELLENT."
---

# PROBLEM: the situation model has NO mutable WORLD-STATE register. The reader tracks entity and event LISTS, but nothing represents the here-and-now STATE of the described world — which entity HAS what, what is AT which location, what is OPEN / broken / clean — a set of predicates UPDATED by each event's EFFECT and READ by the next event's PRECONDITION. The brain's situation model centrally maintains exactly this running state (Zwaan & Radvansky 1998 event-indexing; Glenberg, Meyer & Lindem 1987 — an object's availability in the model tracks its current spatial/state relation, not its last mention). The aligner problem (`the_reader_conflates_similar_events…`, owner-DONE) named this its #1 adjacent gap — "MISSING, highest value … the deepest gap, and it unblocks the generative-simulation order fix" — because temporal/causal order IS a state relation (an event ENABLES another when its EFFECT satisfies the other's PRECONDITION; STRIPS-style). Build a mutable world-state register over the situation model — state predicates updated by each event's effect, queryable at any story-time — driven by the reader's OWN extraction, and prove it answers state queries CI-separated over a no-state-tracking floor on real prose with state-changing events (or LOCATE the residual precisely: is it the register mechanism, or extraction recall of IMPLICIT preconditions/effects?).

**slug:** `situation_model_has_no_mutable_world_state_register` — **opened:** 2026-09-01 by the strategy session
(ARCHITECT HEARTBEAT; owner: feed idle solvers with the high-value follow-ons these results surfaced). It is the
aligner problem's explicitly-named #1 adjacent gap. **status:** OPEN — a BUILD problem (a mutable world-state register
as the situation model's STATE dimension). You build + validate in `experiments/`; strategy lands any hdlab wire (Q111,
default-off, witness required). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; RE-RANK PER THE OWNER):** filed at `7`. The aligner named it its
> HIGHEST-value adjacent gap and "the deepest gap" — it is the situation model's missing STATE dimension and it unblocks
> the generative causal/temporal-order fix (order = a state relation). Ranked below the north-star meaning organ (1) and
> the who-did-what/reasoning line only because those are further along; RAISE it if you weight the state dimension higher.
> ⚠️ HONEST BOUND (from the aligner's prototype): a naive state-predicate/entity join covered only ~5% of questioned
> pairs because PRONOUNS / PARAPHRASE break entity identity with no coref — so coverage (coref-densified state join +
> implicit-effect recall) is the real work, and the bar targets a population where state changes are extractable. ⚠️
> Compose with the reader's capable flags ON (`python tools/reader_capabilities.py`).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
As you read a story, you keep a running picture of how things ARE right now: the cup is empty, then someone fills it, so
now it's full; the door was open, someone shut it, now it's closed. You update that picture with every action and use it
to make sense of the next sentence. Our reader doesn't — it keeps a LIST of who's in the story and a LIST of what
happened, but nothing that says "right now the door is closed." So it can't answer "is the door open?" after it was
shut, and it can't tell that "she opened it" must come before "she walked through" (you can't walk through a closed
door). Build that running picture: a small set of facts about the world's current state, changed by each action and read
by the next — the piece the brain's story-model centrally keeps, and the piece that lets order fall out of cause.

## 2. WHY THIS ONE
It is the situation model's MISSING dimension — the aligner problem named it the deepest, highest-value adjacent gap.
Two payoffs: (a) it lets the reader answer state questions ("does she have the key now?", "is it open?") it currently
cannot; (b) it UNBLOCKS the causal/temporal-order fix — order is a state relation (an event ENABLES the next when its
effect meets the next's precondition), so a state register turns "learn order by counting co-occurrence" (the weak,
located wall) into "derive order from cause". It is the brain's here-and-now model, and it is structurally absent today.

## MEASURED vs INFERRED
- **MEASURED (inherit; do NOT re-derive):** the reader tracks entity + event LISTS with NO mutable state register
  (verified structurally). The aligner's naive in-text state-predicate/entity join covered only ~5% of questioned pairs
  because pronouns/paraphrase break entity identity with no coref, and in-text glass-box enablement was a located
  negative (0.568 ≤ 0.591 co-occurrence) — the gap is extraction RECALL of implicit preconditions/effects. `state_
  register` exists (promoted) but is off the live path; `force_dynamics_lexicon`/`causation_typing` type WITHIN-clause
  outcomes but do not lift them to a cross-event STATE EFFECT.
- **INFERRED (you must measure):** whether a mutable world-state register — state predicates updated by each event's
  EFFECT and read at query time — answers state queries CI-separated over a no-state-tracking floor on real prose with
  state-changing events, the info-free twin (shuffle which event updates which predicate) LOSING; and whether the
  precondition/effect join predicts causal/temporal order better than co-occurrence — or whether the residual is
  extraction recall of IMPLICIT effects (a full-PASS located negative that hands the coverage gap to coref + a foundation).

## 3. HOW THE BRAIN DOES THIS (the opening move)
**PINNED — the situation model maintains a MUTABLE CURRENT STATE, updated incrementally.** Comprehension builds and
continuously UPDATES a mental model of the described situation's current state (Zwaan & Radvansky 1998 event-indexing —
the "current model" that events update; van Dijk & Kintsch 1983 situation model). Objects' representational availability
tracks their CURRENT spatial/state relation to the protagonist, not their last mention (Glenberg, Meyer & Lindem 1987;
Bower & Morrow 1990 "mental models in narrative comprehension"; Radvansky & Copeland spatial-situation updating). An
event has PRECONDITIONS (state it requires) and EFFECTS (state it changes) — the STRIPS/operator form (Fikes & Nilsson
1971) is the computational-level description of what the brain's forward model does; an event whose precondition is
UNMET triggers a bridging inference (Haviland & Clark 1974). The computation to COPY: a set of STATE PREDICATES over the
tracked entities/locations (have(agent,obj) / at(obj,loc) / open(obj) / broken / clean …), each event applying its
EFFECT to the register and its PRECONDITION reading it, so any story-time state is queryable and order follows from
precondition→effect chains.

## 4. PINNED vs OUR-INVENTION (copy the computation, sweep the parameter)
- **PINNED (COPY exactly):** a mutable CURRENT-STATE representation updated incrementally by event EFFECTS and read by
  event PRECONDITIONS; state as PREDICATES over entities/locations; order/causality derived from precondition→effect
  chains; a precondition-violation → bridging-inference signal.
- **OUR-INVENTION-UNDER-TEST (SWEEP, do NOT adopt):** the predicate vocabulary (have/at/open/… — derive from the corpus,
  do not hand-fix a closed set), how effects are extracted (verb→effect templates vs the promoted `state_register` /
  `causation_typing` lifted cross-event vs a STATIC offline precondition/effect foundation — the FOUNDATION pivot is
  admissible), the entity-identity backbone (coref-densified), the query/read-out. Sweep, report the frontier.

## ALREADY TRIED / DO NOT RE-RUN (check `experiment_index` FIRST — the p6 lesson)
> ⚠️ **RUN `python tools/experiment_index.py query "state register"` / `"entity state"` / `"propara"` / `"world state"`
> BEFORE BUILDING.** Known:
- ⚠️ `exp_propara_entity_fate_selectional_preference_probe_v1/v2` = HARD_FAIL_NO_GENERALIZATION — understand WHY (a
  selpref framing on ProPara state) before repeating its shape; this is a STATE-REGISTER problem, not a selpref probe.
- ⚠️ The aligner's in-text glass-box enablement join was a located NEGATIVE (0.568 ≤ 0.591 co-occurrence) with ~5%
  coverage (no coref) — do NOT re-run the naive in-text join expecting a different result; the lever is coref-densified
  identity + implicit-effect recall (a foundation), not the naive join.
- Reuse the PROMOTED `state_register` organ (off the live path) + `force_dynamics_lexicon`/`causation_typing` (lift the
  WITHIN-clause outcome to a cross-event STATE EFFECT) + coreference (the entity backbone). Do NOT rebuild them.
- ⛔ No external LLM as the state extractor or the foundation (the invariant). A STATIC OFFLINE precondition/effect asset
  IS admissible (the FOUNDATION pivot), but the inference-time reader stays glass-box.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the aligner `SOLVED.md` adjacent-components §1 (this problem) + §7 (force-dynamic outcome → state effect) +
  its `learn_canonical_script_order_from_a_causal_enablement_foundation` proposal (the order fix this UNBLOCKS).
- Read the promoted `hdlab/state_register.py` (what it tracks + why it's off-path), `causation_typing` /
  `force_dynamics_lexicon` (within-clause outcomes to lift), and how `situation_reader` exposes events + entities +
  coref (the extraction feeding the register).
- Pick a population with EXTRACTABLE state changes + gold state queries: ProPara (entity state through a process),
  bAbI state-tracking tasks, or a real narrative slice with annotated state — report n + the coverage (how many
  queried entities/events are coref-resolvable). MIND the corpus-age confound if you use narrative.

## 5. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
PASS = the mutable world-state register, driven by the reader's OWN extraction, answers STATE queries (is obj X open /
does agent have Y / where is Z, at story-time t) CI-SEPARATED over the strongest no-state-tracking floor actually run —
(a) LAST-MENTION / static (the state at first introduction, never updated) and (b) a no-model surface baseline — on a
population with state-CHANGING events, with the info-free TWIN (shuffle which event's effect updates which predicate, or
a random-effect twin) LOSING CI-separated, AND a positive control that the register's answer CHANGES at the updating
event (not a constant). BONUS/UNBLOCK: the precondition→effect join predicts causal/temporal order CI-separated over
co-occurrence on the aligner's order task. Report CI half-width + null p95 beside every margin. **A rigorous NEGATIVE is
a full PASS if located:** if the register, faithfully built, does not beat the floor, name precisely whether the wall is
the register MECHANISM or extraction RECALL of implicit preconditions/effects (and the coref coverage), and localize it —
that tells the assembly whether the state dimension is buildable from live extraction or needs the coref + foundation first.

## 6. FLOORS + CONTROLS (the strongest trivial methods, actually run)
- **LAST-MENTION / static-state** floor (the entity's state at introduction, never updated) + a no-model surface
  baseline — BOTH actually run on the SAME queries; beat whichever is stronger CI-sep.
- **Info-free twin:** shuffle which event's EFFECT updates which predicate (or a random-effect twin) — must LOSE CI-sep
  (excludes "any per-event bookkeeping helps"; the correct effect→predicate binding must do the work).
- **Change-point positive control:** the register's answer for a predicate must FLIP exactly at the updating event (not
  a constant, not a last-mention echo) — proves it is tracking STATE, not recency.
- **Coverage split:** coref-resolvable vs unresolvable queried entities — report separately (the ~5%-coverage wall the
  aligner hit); the unresolvable slice is the located residual, not a hidden win.
- **Precondition-violation control (bonus):** an event whose precondition is unmet in the register should be flagged
  (bridging-inference signal) — a can-fail check that the register is read, not just written.

## 7. CORPUS-AGE + GENERALIZATION (owner priority — a constructed-gold win is not a capability)
Report on a held-out slice + at least one clean modern population (ProPara / bAbI state / annotated narrative). Report
per-predicate-type (possession / location / open-closed / physical) and per-coverage breakdowns. A gain only on the
tuning set, one predicate type, or the easy coref-resolvable slice is not a capability.

## 8. FILES AND ENTRY POINTS
Build + validate in `experiments/` (drive the register from `SituationReader.read()`'s events + entities + coref; reuse
the promoted `state_register` + `causation_typing`/`force_dynamics_lexicon` for effect extraction; a STATIC offline
precondition/effect foundation is admissible). A scaffold-free witness recomputes, FROM SOURCE, the register's state-
query accuracy vs the last-mention/static floors + the shuffled-effect twin + the change-point positive control, on a
real state-change population. If it clears the bar, strategy lands the hdlab wire (Q111): a default-off world-state
register on the situation model (state predicates updated per event; `sm.world_state`/`state_at(entity, t)`),
byte-identical when off, witnessed. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the situation model's
missing STATE dimension; order-from-cause once the register exists).

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote the aligner's numbers (0.568/0.591, ~5% coverage) as YOUR result — MOTIVATION. Re-measure your
  register's state-query accuracy on your own population. No number crosses scorers/populations.
- 🚫 Do NOT re-run the naive in-text state-predicate join (the aligner's located negative) or a ProPara selpref probe
  (HARD_FAIL) as-is — this is a mutable STATE REGISTER with coref-densified identity + implicit-effect recall.
- 🚫 Do NOT claim a win without the shuffled-effect twin AND the change-point positive control — the register must be
  shown to TRACK state (flip at the update), not echo recency.
- 🚫 Do NOT use an external LLM as the state extractor or the read-out (the invariant). A static offline precondition/
  effect FOUNDATION is admissible; the inference-time register + read stay glass-box.
