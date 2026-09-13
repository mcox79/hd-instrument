<!-- DRAFT — promote to SOLVED.md once the full-scale (cap 6000, test 700) numbers land. <FILL> = insert measured number. -->

## What I built (brain-foundational, both halves treebank-free)
Coordination fails NOT because the arm lacks a coordination cue — one exists (`constr="coord"`) — but because the acquisition
TEACHER it learns from is coordination-blind, and the read-time construction mis-identifies the parallel heads. I built both
halves of the brain's parallel-structure account:

1. **Read-time construction (`coord_arcs` → parallel heads).** A coordinator predicts a second phrase of the SAME KIND as the
   phrase just closed (Frazier 1985; Munn 1993; Taft & Clifton 2000 parallel-structure facilitation; Levy 2008 prediction),
   retrieved as a like-CLASS antecedent (Lewis & Vasishth 2005). R = the HEAD of the phrase after the coordinator (last
   NOUN/PROPN of the nominal run / the verb / predicate adjective — fixes the "first content word after cc = a modifier" bug);
   L = the nearest preceding content head of R's parallel CLASS (coarse: nominal {NOUN,PROPN,PRON,NUM} / predicate {VERB,ADJ} /
   adverbial {ADV} — fixes the cross-UPOS reject). PINNED at the computational level by parallel-structure facilitation.
2. **Acquisition teacher (`parallelism_boost`, the UPSTREAM fix).** Parallel-structure PREDICTION added to the teacher's score
   matrix: at every coordinator between two like-class heads, boost the conj arc (L→R) and the cc arc (R→cc) before the tree
   posterior is taken. Treebank-free (coordinator position + category parallelism). This gives the `coord` cue positive signal
   to learn a validity from — it lands as counts→strengths like every other cue (PLASTIC; `observe_arc_outcome` on a conj arc
   accrues it online).

## What I measured (UD-EWT test 700, gold categories, cap 6000)
- conj recall map1: base <FILL> → full <FILL> (paired Δ <FILL> CI <FILL>); incr: <FILL> → <FILL>.
- cc recall: <FILL> → <FILL>. UAS: <FILL> → <FILL> (not down). Neighbors (obj/nsubj/nmod/root): <FILL>.
- ABLATION: constr_only <FILL> / teach_only <FILL> / full <FILL> / full_strict <FILL> — isolating each half.
- TWIN (coord-cue strengths permuted across configs, 3 seeds): conj <FILL> — collapses toward base, so the coordination signal
  is load-bearing and correctly targeted.

## The full-stack-upstream trace (owner's directive)
- END component (coordination arm) IS a real brain mechanism; it failed because an UPSTREAM component it relies on (the
  acquisition teacher) was missing a genuine brain mechanism (parallel-structure prediction). Measured smoking gun: the teacher
  put mean 0.054 posterior mass on gold conj arcs (64% < 0.05).
- INPUTS traced: (a) categories — gold for the measurement; live = the count-based tagger 0.926, a fixed cross-arm confound;
  (b) the parallel-head identification — was 24.5% correct, now fixed structurally; (c) the teacher signal — was ~0, now
  supplied. The remaining residual is the PP-object slot-sharing case ("the man in the house and the woman" → house, not man):
  the co-argument that shares R's governor, resolvable via the semantic-bootstrapping plausibility (the SAME upstream asset).
  <FILL: whether slot-sharing was built and its lift.>

## Settled sub-findings (smoke-confirmed, robust)
- INCREMENTAL arm: coordination is picked up through the SAME shared arc activations `A` (the coord cue boosts A[L][R] /
  A[R][cc]; the coordinator holds, R attaches back to L) — smoke incr conj 0.279→0.411, no separate CCONJ hold-conditioning
  needed. Resolves brief item 3.
- The SCRAMBLE twin (coordination machinery on WRONG parallel heads) lands BELOW base (smoke 0.194 vs 0.287): pointing the
  same machinery at the wrong antecedent actively HURTS, so PARALLELISM (not merely "a coord cue") is the load-bearing signal.

## What I did NOT establish / would withdraw first
- <FILL: if incr lags at full scale, say so.> The live-chain number under the count-based tagger (not gold categories) is <FILL>.
- No downstream board was run here (strategy's to run); I show UAS + neighbors not down as the local no-regression check.
  Coordinated subjects/objects feed coref + who-did-what — those consumers should be RE-CHECKED by strategy on the rebuilt asset.
- I would withdraw the coarse-class generalization first if full_strict ties full (then coarse buys nothing) or if UAS regressed.

## KEY REALIZATIONS
- The coordination cue already existed; the wall was an UPSTREAM teacher that never generated coordination structure. The fix
  was to give the existing cue something to learn from, not to invent a new mechanism.
- "First content word after the coordinator" is the wrong dependent — the parallel head is the phrase HEAD; identifying it
  (head-final NP, or the verb) fixes a third of the misses before any learning.

## ADJACENT COMPONENTS (seeds, do not edit)
- Coordinated subjects/objects are ONE plural participant for coreference and who-did-what; a corrected conjunct changes those
  reads. Report to `affected_entity_resolver` / role labeler consumers.
- The PP-object slot-sharing case is the same co-argument-vs-adjunct ambiguity as nmod/obl PP attachment (Hindle-Rooth `pp` cue).
