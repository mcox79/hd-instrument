---
owner_verdict: DONE
---

SUBMISSION — form_the_unified_discourse_referent_before_the_pronoun_pick_the_shared_entity_lever
STATUS: SOLVED (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference. NO hdlab/ written.
Ledger: clean (malformed 0). Reverify: .venv/Scripts/python.exe verification/test_unified_referent_gum.py
  (5/5 headline; full suite 20/20: ablation 3/3, optimize 2/2, optimizations 2/2, commonnoun_wall 3/3,
   softhold_wm_diagnostic 2/2, cmrole_compose_gum 3/3; GUM parse control: experiments/gum_coref.py --self-test).

GATING MOVE — acquired MODERN gold. The bar bans 19c LitBank as load-bearing (owner 2026-09-06) and no modern
full-chain coref corpus was on disk. Acquired GUM (Georgetown University Multilayer) OntoGUM CoNLL-U coref layer as a
static offline foundation asset (owner-approved), pinned V12.1.0 @ 22fdf87, reproducible fetch script
experiments/fetch_gum_coref_v1.py -> data/corpora/gum/. 275 docs / 36,332 mentions / 8,400 chains across 18 modern
genres; one file gives gold UD POS (mention type), gender/number, and coref chains.

CORE RESULT — the bar is MET on modern gold. One unified discourse referent per entity (Heim/Kamp DRT FILE-CHANGE:
one file-card opened on first mention, UPDATED by every later mention across name+common+pronoun), resolved by ACT-R
base-level activation (reused hdlab.salience_binder) with Ariel's Accessibility Hierarchy (the cue is
mention-type-specific: pronoun->salience+gender, common->recency, name->identity). Held-out TEST (137 GUM docs), two
downstream consumers lift CI-separated over the current separate-tracking (surface-head-keyed) reader, twin losing:
  (1) PRONOUN PICK 0.3621 -> 0.4681, +0.1060 CI[+0.079,+0.133] (hw 0.027); info-free twin(shuffled identity) 0.2034.
  (2) ENTITY-KB HARD-LINK (a named entity's pronoun files under the referent CARRYING the name; separate tracking
      resolves to a nameless fragment) 0.3963 -> 0.4682, +0.0719 CI[+0.023,+0.120] (hw 0.048); twin 0.0819.
  NO-regress on named coref (0.6781->0.6845, +0.0064). Strongest floor for the pick = the separate reader itself
  (0.362; also >> string-identity 0.307 / recency 0.293). Oracle-unified (gold clusters) ceiling 0.584.

DISK OUTRANKED THE BRIEF (two refinements). (a) The reader is ALREADY partly unified+default-ON (referent_per_np,
common-noun gate); the one open lever is re-keying the pronoun-anaphora overlay entity (state_of_mind.EntityState.head,
a surface-head string) to ONE canonical referent. (b) The lift is CUE-SPECIFIC (Ariel): the salience/gender that
unification completes reaches the PRONOUN cue only. Cue decomposition (leave-one-out): pronoun pick carried by GENDER
completion (+0.036 CI-sep) + the structural unification itself (~+0.06); entity-KB hard-link carried by ACT-R
grammatical-PROMINENCE (-ACT-R -0.137 CI-sep). The name-variant aliaser (proven +0.020 on 19c family novels) is
register-NEUTRAL on modern multi-genre GUM -> names use aliaser-merge UNION blind-surface (no-regress).

LOCATED NEGATIVE (a full pass; researched to 100%). COMMON-noun resolution does NOT beat blind head-identity: decomposed
same-head 64.7% (blind resolves) / name-bridge 10.1% / variant 25.2%; of name-bridge, a GLASS-BOX bridge (apposition/
copula 0.7% + head-in-name "American College of Pediatricians"->"the college" 18.4%) recovers 19.1%, and 80.9% needs
WORLD KNOWLEDGE the discourse never states (Argentina->"the country") -> the no-LLM-barred fraction, quantified. The
glass-box bridge (built, adopted) lifts common +0.0074 CI-sep.

UPSTREAM MUST BE BRAIN-FOUNDATIONAL TOO (measured + composed on modern gold). Positional roles (the pre-P2 live
_assign_roles) cost -0.084 CI-sep on the entity-KB hard-link vs gold grammatical roles. Composed the ALREADY-LANDED
upstream (P2 Competition-Model assigner + incremental_parser structure cue; both owner-DONE, validated only on 19c) with
this referent on modern GUM: the full landed role stack TRANSFERS to modern text and recovers ~47% of the
positional->gold entity-KB gap (0.384->0.424; structure cue +0.014 on top of CM; shuffled-cue twin loses +0.087
CI-sep); COMMON fully recovers gold-role quality. A -0.044 residual to gold remains = the UNDERSTOOD
glass-box-vs-trained-parser ceiling (a trained parser is barred: loses OOD), not a new wall.

OPTIMIZATIONS — nine tested across the whole within-component brain-foundational family; the base was already at its
optimum. ADOPTED (dev-validated, pronoun no-regress): glass-box common->name is-a bridge; low-weight parallelism.
REJECTED, each understood to MECHANISM: graded Nref write AND confidence-gated writeback net-negative (soft-hold loses
to hard-commit -- low-margin picks still 0.327 accurate, "attractors settle"; Garrod-Sanford bonding; confirms the prior
LitBank finding on modern GUM); hard working-memory bound redundant with the ACT-R decay (the ACT-R pick is in the
recency-top-4 99.9% -- the decay IS the graded WM limit, Lewis-Vasishth); animacy redundant with English gender; decay
d=1.5 a pronoun<->kb trade (regresses the pick -0.02). Nothing moves the result CI-separated -> the cue family is
saturated; the real headroom is UPSTREAM clustering (to the oracle 0.584, glass-box) + barred world knowledge, NOT more
knobs. Walls detail: notes/problems/<slug>/WALLS_RESEARCH_brain_foundational_2026-09-06.md.

FOR STRATEGY (Q111 wire; you own hdlab; apply-ready, reference impl = experiments/exp_unified_referent_gum_v1.py::Resolver):
  (1) RE-KEY WorkingOverlay._entities by a CANONICAL referent id, not head.lower() (state_of_mind.py L302/311):
      name -> hdlab.coref.EntityAliaser.assign UNION blind-exact-surface; common -> head-lemma + the glass-box is-a
      bridge; every mention UPDATES the ONE EntityState (append (time,role), set gender/number if newly known).
  (2) Resolve pronouns by hdlab.salience_binder ACT-R activation (d=2.0) over unified referents, recall-safe
      gender+number, HARD-commit, event-centrality OFF (situation_reader._read_entities).
  (3) DEPENDENCY: land the P2 CM assigner + incremental_parser structure cue alongside (they compose; +0.084 upstream).
  GUARDRAILS (all measured negatives -- do NOT wire): graded/conf-gate writeback; hard WM bound (redundant); animacy
  (redundant); salience cue on nominals (Ariel); gender propagation / recall-safe-only / aliaser-alone name path;
  d=1.5 globally (kb-only trade).
AUDIT UPDATE (E3 coreference/entity tracking): the flagged overlay-by-discourse-entity lever is now GLASS-BOX on modern
gold (pronoun +0.106, entity-KB hard-link +0.072 CI-sep); the lift is cue-specific per Ariel; the surface-head
fragmentation the audit names is a 19c-family-novel effect (aliaser register-neutral on modern); the entity-KB benefit
requires the P2 upstream (positional roles -0.084).

TLDR (plain English): A good reader knows "Elizabeth", "the young woman", and "she" are one person and keeps one mental
record; ours kept separate records and re-guessed identity in three passes. Because the project's 200-year-old test
books are banned as a yardstick, I first downloaded a modern mixed-genre corpus of real annotated text. Building the
single shared record makes deciding who "he"/"she" means clearly better (about 36% -> 47% right, a clean gap a scrambled
control can't fake) and files facts under the right named character (40% -> 47%) -- two separate wins. It does NOT help
plain descriptions ("the man", "the paintings"): those are resolved by the word itself, and linking a description to a
name mostly needs outside world-knowledge our no-outside-AI rule forbids (an honest, measured limit -- 81% of those
cases). I also plugged the whole upstream chain (who-is-the-subject + the sub-clause fix, both already shipped) into my
component on modern text and confirmed they reinforce each other. I tested nine brain-foundational tune-ups and every
rejection is understood to mechanism, not guessed. Nothing is wired into the live system yet -- that's a one-function
re-keying for the other session.

QUESTIONS: none blocking. One judgement call: the bar named affect-experiencer OR entity-KB hard-link; GUM has no affect
annotation, so I measured the entity-KB hard-link branch on modern gold (the affect instrument is 19c-only today).

NEXT STEPS: (1) strategy lands the re-keying wire + composes the already-landed P2/incremental-parser it stacks with;
(2) the real remaining headroom is glass-box CLUSTERING quality to the oracle (0.116 on the pick), not this component;
(3) the common-noun residual is the barred world-knowledge is-a prior (a different subsystem), not a fidelity gap here.
