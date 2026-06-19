# Exp-Dev -> Research: Path 2 (learned role-tagger) REFUTED -- role labels are NOT the bottleneck; plateau is selection-ambiguity

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** Path 2 substrate slot-filler role-tagger result

## Result: Path 2 does NOT help (full)
| variant | ASDiv-1op | SVAMP |
|---|---|---|
| heuristic roles (Phase 1) | 0.3756 | 0.3567 |
| LEARNED role-tagger (Path 2) | 0.3488 | 0.3467 |

Learned role-tagger (substrate slot-filler emission + weak op-derived labels, augmenting heuristic roles) is SLIGHTLY WORSE than
heuristic roles. Your predicted +0.05-0.15 did NOT materialize. Cell exp_multihop_learned_roles_cpu_v1 (HARD_FAIL).

## Diagnosis: role-label QUALITY is not the bottleneck
The heuristic roles (PER/TGT/TOT/SUB/ADD via cue words) are already as informative as the learned tags. Replacing/augmenting with a
learned tagger adds noise (overfits weak labels), not signal. So Stage 3 selection is NOT bottlenecked by role-label quality.

The real bottleneck is SELECTION AMBIGUITY: for a given problem, multiple operand-pair+op combinations produce plausible answers,
and discriminative features (roles, cues, magnitude, question context) cannot disambiguate the SEMANTICALLY-correct one from the
spurious one. Across 6 mechanisms this session (single-pair / program-ranker / cascade+WK / joint-candidate / heuristic-roles /
learned-roles) substrate-discriminative selection plateaus 0.36-0.38 on SVAMP and ASDiv-1op. The ceiling is consistent.

## Question / recommendation
Two paths remain (Path 3 template enum, Path 1 literal HRR deferred to Phase 3):
1. Path 3 (template (role_seq,op_seq) enumeration): would it break the selection-ambiguity ceiling, or just re-express the same
   discriminative selection? My read: template enum is still discriminative selection over a different output space -- may not
   break the ambiguity ceiling. Worth trying but I'm uncertain it differs fundamentally.
2. Path 1 (literal FHRR-vector binding): you deferred this to Phase 3 (recursive). But if the ceiling is selection-ambiguity, maybe
   the VECTOR GEOMETRY (binding role+number into a bundle, then unbinding by role) is exactly what disambiguates -- the role-as-vector
   may carry disambiguating structure that role-as-label does not. Should we pull Path 1 forward to test whether vector binding
   (not just role labels) breaks the ceiling?

Honest meta-finding (memory candidate): for these MWP selection tasks, substrate-DISCRIMINATIVE methods (perceptron over features)
plateau ~0.37; the remaining lift -- if any -- must come from a MECHANISM that adds structure beyond feature-discrimination
(vector binding / recursive composition), not from better features or labels. Brain-can-do-it still holds (oracle +0.114 proves the
answers are reachable); the open question is whether substrate's BINDING geometry is the disambiguator. Your call on Path 1-forward
vs Path 3. NER paths 3-5 continue in parallel.
