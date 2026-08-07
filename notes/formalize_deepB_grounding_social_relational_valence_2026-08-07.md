# FORMALIZE (deep-B grounding, formalize-first): the real gap is SOCIAL-RELATIONAL valence, NOT "connect the anchor to reading"

**Filed:** 2026-08-07 by Director, driving (B) the grounding program in the disciplined formalize-first way
(its 5x-HARD-FAIL history demands it). This doc CORRECTS a label-based assumption via READ-THE-CODE and
scopes the first real increment. Companion: the overnight update's fork; prior-art exp_appraisal_structure_
extraction; owned organ hdlab/context_grounded_valence.py.

## READ-THE-CODE FINDING (corrects my earlier framing)
I had framed deep-B as "connect the owned grounded_appraisal_sim_earned anchor to the reading path." READING
hdlab/context_grounded_valence.py shows that is **already built for PHYSICAL HARM**: a 3-stage pipeline
(governor sense-select -> animacy-axis event override -> biased-competition combine -> **frozen appraisal-sim
theta valuation**, VALENCE = Q(harm@coherent) - Q(help@coherent)) reads HARM/HELP valence FROM TEXT using the
reward-earned theta (Bopen=1.000 open-vocab, 5 seeds; random-theta approx 0 -> the theta genuinely values the
event TYPE, not noise). So the earned anchor IS connected to reading, for physical harm on the animacy axis.
**The grounding-transfer architecture EXISTS and WORKS on one axis.**

## THE REAL GAP (the organ's OWN docstring names it as SCOPED-OPEN / proven)
- **SOCIAL-RELATIONAL / BENEFICIARY valence** -- "animacy alone cannot resolve" (docstring, cert-doc AXIS 3/5).
- ABSTRACT-HARM-vs-GOAL-NOUN disambiguation -- same, proven gap.
- (Plus closed hand-lists: FORCE_CLASS_HARM_REAL force-verbs; BODY_PART_SUPPLEMENT -- not the frontier.)
This is EXACTLY where the eval-tail grounding residual lives: "you're too good for me" = a SOCIAL refusal
(not physical harm); "spoil the cake via liniment" = a GOAL-NOUN outcome (not animate-patient harm). Neither
is on the animacy axis. So deep-B's first real increment is: **extend grounding from the PHYSICAL-HARM axis
(animacy, owned) to a SOCIAL-RELATIONAL axis.**

## THE INCREMENT (direction; brain-foundational)
Mirror the animacy-axis architecture for social valence: a SOCIAL-RELATION feature axis (does the event
raise/lower a person's social standing / benefit/harm a relationship: praise/accept/befriend/forgive =
social-positive; refuse/scorn/shame/exclude = social-negative) feeding the SAME biased-competition combine +
an earned-theta valuation over SOCIAL situation-types. The earned theta already values physical harm/help;
social outcomes need either (a) the same reward-earned theta EXTENDED to social situation-types via the
experiential simulation (USER's 08-03 pivot: blocked-goal->anger, social-reciprocity earned), or (b) a small
SUPPLIED social-relation seed (invariant-OK DATA, the ~6yo "refusing hurts / accepting helps" foundation),
propagated the ATL-hub way -- mirroring how the harm axis combines a supplied force-verb list + WordNet
animacy + earned theta.

## BRAIN-FIDELITY (SHAPE + POSITION + METRIC)
- BRAIN: physical-harm valence is grounded in amygdala/insula (threat/pain); SOCIAL valence in OFC/vmPFC +
  the social-cognition net (TPJ/mPFC) -- a DIFFERENT but parallel grounding channel (social pain shares
  dACC/insula with physical pain, Eisenberger). So a social-relational axis parallel to the animacy axis is
  brain-faithful: same valuation architecture (OFC common-currency), different feature channel (social vs
  physical). POSITION: stage-2 event override + stage-3 theta, exactly like the animacy axis. METRIC: does a
  social-negative event (refusal/shame) read NEGATIVE vs a social-positive (accept/befriend) POSITIVE, on
  open vocab, earned-not-hand-scored.

## HONEST RISK (why formalize-first, why this is a research bet not a +1)
- No clean WordNet "social-animacy" axis exists -- animacy gave the harm axis a free open-vocab feature;
  social-relation has no equivalent free lexical axis -> likely needs a SUPPLIED social-relation seed
  (invariant-OK but must be small + propagated, not a test-fitted hand list) OR the experiential-social
  simulation to EARN it (the deeper, harder route).
- The earned theta currently values PHYSICAL harm/help; extending it to social situation-types may need a
  new/augmented simulation (social-reciprocity, blocked-social-goal) -- a real build, not a wire-in.
- This is the field's 45-year wall (social/pragmatic grounding); a HARD_FAIL is likely-informative, not a
  cheap win. It will NOT cleanly move the goal_bearing eval-tail (those need SPECIFIC knowledge too); its
  value is the ARCHITECTURE (proving social valence can be grounded + read the harm-axis way).

## CAN-FAIL FIRST INCREMENT (bounded, before the full simulation)
Build a SOCIAL-RELATIONAL axis parallel to the animacy axis (stage-2 override + stage-3 theta), with a SMALL
supplied social-relation seed first (prove the architecture cheaply, like the harm axis's supplied force-verb
list), tested on a TARGETED social-valence probe (praise/accept/befriend/forgive vs refuse/scorn/shame/exclude
in minimal contexts, open-vocab held-out), NOT the goal_bearing eval-tail. HARD-PASS: social-negative reads
NEGATIVE / social-positive POSITIVE, open-vocab (Bopen-style), scramble collapses, earned/supplied-seed not
test-fitted, controls clean. THEN (separate, deeper): swap the supplied seed for the experiential-simulation-
earned social theta (USER's foundational pivot). Formalize-first done; the build is the next step IF USER
greenlights the deep bet (this is the (B) commitment, distinct from the bounded library-growth of (A)).

## BOTTOM LINE
Deep-B is better-scoped than assumed: grounding-transfer WORKS for physical harm (owned, Bopen=1.0); the
frontier is a SOCIAL-RELATIONAL valence axis (the organ's own proven gap), which is where the eval-tail's
social cases + the field's deep wall live. It's a genuine research bet (social grounding, likely needs a
supplied seed then an experiential-social simulation), brain-faithful (parallel channel, OFC common-currency),
and formalize-first is now done. This is the concrete (B) starting point when the deep bet is greenlit.
