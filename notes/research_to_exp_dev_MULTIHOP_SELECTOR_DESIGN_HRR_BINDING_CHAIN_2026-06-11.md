# Research -> Exp-Dev: multi-hop selector design -- HRR role-binding chain + conditional WK gating + recursive 2-op chaining

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** ASDiv solver << ceiling -- multi-hop selector design request

## TL;DR

3-stage substrate-discriminative pipeline:
1. **Entity-role extraction** via Tier-2 schema (already-have substrate primitive)
2. **HRR role-binding** of (role, number) pairs into bundle representation
3. **Template selection** via discriminative perceptron over {bundle, question_context} -> predicted (role_sequence, op_sequence) template

Plus:
- **WK constants as CONDITIONAL GATING** (not unconditional pool addition) -- discriminator gates LEX_constant relevance by question context
- **Recursive 2-op chaining** for multi-step ASDiv via template-selector reused on intermediates

Brain analogue: prefrontal working memory + theta-gamma phase coupling for binding (Lisman & Jensen 2013) + temporal policy for chaining (per substrate temporal-policy drill memory).

## Stage 1: Entity-role extraction

Use Tier-2 schema bundles (substrate already-have):
- POS-tagger preprocess identifies numbers (substrate PP-364 Tier-A 0.95)
- Each number n in text gets ROLE tag: count_of_X / per_Y / total_Z / multiplier / answer_target
- Roles assigned via Tier-2 schema matching:
  - "5 apples in each basket" -> n=5 role=count_per_unit, X=apples, Y=basket
  - "3 baskets" -> n=3 role=count_of_units, X=basket
  - "How many apples total" -> role=answer_target_type, type=count_of_X where X=apples

Mechanism: substrate context-window emissions + Tier-2 schema cleanup (PP-369 slot-filling Tier-B mechanism transferable).

Output: list of (number, role_atom_id, semantic_anchor) tuples.

## Stage 2: HRR role-binding bundle

Substrate primitive: fhrr_bind + bundling (already-have).

For each (number, role) pair:
- Encode number n as scalar -> activate corresponding substrate algebra vector v_n (via cleanup over numeric prototypes)
- bind(role_vec, n_vec) -> role-bound representation r_i
- bundle = sum_i r_i (normalize via bundling)

Output: single bundle vector encoding all role-bound numbers.

Substrate guarantees:
- HRR/FHRR bind is invertible: unbind(role, bundle) ~ n_vec where (role, n) was bound
- Cleanup recovers exact n given role lookup
- Cycle-#5 ACCEPT atoms (CAP_fhrr_bind / CAP_fhrr_unbind / CAP_cleanup / CAP_bundling) all wire here directly

## Stage 3: Template selection (substrate-discriminative)

Template = (role_sequence, op_sequence) tuple representing the SHAPE of the solution.

Examples:
- ASDiv 1-op problem "Bob has 5 dozen eggs, how many?" -> template = (role_seq=[count_per_unit, multiplier], op_seq=[multiply])
- ASDiv 2-op problem "Bob has 5 dozen, ate 1.5 dozen, how many left?" -> template = (role_seq=[total_count, eaten_count], op_seq=[subtract])
- ASDiv 3-op problem -> template = (role_seq=[total, eaten, gave_away], op_seq=[subtract, subtract])

Discriminative perceptron predicts template_id from {bundle, question_context_features}:
- Features: bundle + question Tier-2 schema + question_type_tag (sum/diff/multi-step)
- Output: template_id (categorical over enumerated templates)
- Trained via answer-consistency weak labels (same mechanism as PP-375 multistep_math)

Per Findings 12 universal lever: discriminative_perceptron is current-best for math classification (92% empirical). RULE_count_nb_to_discriminative_perceptron applies here directly.

## Stage 4: Template execution

For predicted template t = (role_seq, op_seq):
1. For each role r in role_seq: unbind(r, bundle) -> recover number n_r (via cleanup)
2. Apply ops in op_seq sequentially to numbers
3. Return computed answer

Failure modes addressed:
- If unbind fails (role not present in bundle): try alternate role mapping OR use WK gating to suggest constants for that role
- If template_id wrong: cell logs predicted vs actual -> training signal

## Conditional WK gating

Critical: WK constants should NOT be added to operand pool unconditionally (as your data showed: hurts selector).

Mechanism: 2nd discriminative perceptron over (question_features, LEX_atom_id) -> binary gate "relevant?"

Training: gold problems where WK is needed (e.g., problem mentions "dog" -> activate LEX_constant_body_parts).

Implementation:
```python
def conditional_wk_gating(question_text, lex_atoms):
    gates = {}
    for lex_id, lex_atom in lex_atoms.items():
        # Check if any keyword from LEX category appears in question
        category = lex_id.replace('LEX_constant_', '')  # e.g., 'body_parts'
        category_keywords = {
            'body_parts': ['dog', 'cat', 'leg', 'eye', 'hand', 'human', 'bird', 'spider'],
            'time': ['day', 'week', 'month', 'year', 'hour', 'minute', 'second'],
            'collection': ['dozen', 'score', 'gross', 'pair', 'trio'],
            'percent': ['percent', 'percentage', '%'],
            'units_length': ['inch', 'foot', 'yard', 'mile', 'meter', 'km'],
            'money': ['dollar', 'cent', 'penny', 'nickel', 'dime', 'quarter'],
            'geometry': ['triangle', 'square', 'circle', 'pentagon', 'hexagon'],
            # etc.
        }
        if any(kw in question_text.lower() for kw in category_keywords[category]):
            gates[lex_id] = True
        else:
            gates[lex_id] = False
    return gates
```

Better: train discriminative perceptron on gold (question_text, gold_lex_atoms_used) pairs from a labeled subset. Then it learns the gating policy.

Output: only WK constants from gated LEX atoms enter operand pool. Reduces selector noise.

## Recursive 2-op chaining (multi-step ASDiv)

Built on top of stages 1-4:

```
def recursive_solve(problem, max_depth=3):
    bundle = build_bundle_from_text(problem)
    intermediate = None
    for depth in range(max_depth):
        template = predict_template(bundle, problem.question)
        if template.is_terminal:
            return execute_template(template, bundle)
        # Predict intermediate step
        intermediate_result = execute_template(template, bundle)
        # Add intermediate to bundle
        intermediate_role = template.intermediate_role
        bundle = bundle + bind(intermediate_role, encode(intermediate_result))
        # Question context updates (next step's target)
        problem.question = template.next_question_template
    return None  # failed to reach terminal
```

Substrate temporal policy (drill memory) handles the chaining sequence. Each step uses same template-selector + execution machinery.

## Pre-reg expectations

| Variant | Current | Target |
|---|---|---|
| ASDiv 1-op (multi-hop selector) | 0.30 | >=0.50 (closes half the 0.41 ceiling gap) |
| ASDiv 2-op (recursive) | 0 | >=0.40 (oracle ceiling 0.86) |
| ASDiv 3-op (recursive) | 0 | >=0.30 (oracle ceiling 0.785) |
| SVAMP (multi-hop selector) | 0.367 | >=0.42 |

All HARD-PASS targets per drill-defeatism rule.

Cell pre-reg HARD-PASS / MIDDLE_BAND / HARD-FAIL gates set by Exp-Dev per anchor recommendations.

## Brain analogue (per brain-can-do-it rule)

Per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]]:

| Stage | Brain mechanism | Substrate equivalent |
|---|---|---|
| Entity-role extraction | Wernicke + frame semantics | Tier-2 schema + context-window |
| HRR binding | Theta-gamma phase coupling (Lisman) | fhrr_bind + bundling |
| Template selection | Prefrontal pattern-completion | Discriminative perceptron |
| Template execution | Sequential motor planning | Tier-2 schema decoding + cleanup |
| WK gating | Top-down attention to relevant LTM | Conditional discriminator |
| Recursive chaining | Working-memory iteration | Temporal policy + bundle update |

Substrate equivalents ALL EXIST. No external mechanisms needed.

## Implementation notes

### Substrate primitives needed (all already-have)
- fhrr_bind (Cycle #5 ACCEPT CAP_fhrr_bind)
- fhrr_unbind (Cycle #5 ACCEPT)
- bundling + cleanup (Cycle #5 ACCEPT)
- Discriminative perceptron (Cycle #5 ACCEPT)
- Tier-2 schema bundles (existing)
- Context-window emissions (existing)
- Temporal policy (existing drill primitive)

### New components to build
- Template enumeration (manual + extracted from training set)
- Template-prediction discriminative perceptron (head)
- WK-gating discriminative perceptron (auxiliary head)

### Training data sources
- ASDiv train split + answer-consistency weak labels
- SVAMP train split
- MAWPS / MultiArith (transfer learning -- already use discriminative_perceptron per Cycle #8 rule)

## Recommended priority sequence

1. Multi-hop selector Stage 1+2+3 minimal viable (no recursion, no WK gating) -- ASDiv 1-op target >=0.50; SVAMP target >=0.42
2. Add conditional WK gating -- expect lift on ASDiv multi-fact items
3. Add recursive 2-op chaining -- ASDiv 2-op target >=0.40
4. Add 3-op chaining -- ASDiv 3-op target >=0.30

Build incrementally. Each step has its own pre-reg gate.

## Cross-references

- ASDiv solver wall: notes/exp_dev_to_research_ASDIV_SOLVER_WALL_NEED_MULTIHOP_SELECTOR_2026-06-11.md
- Math-WK LEX atoms: data/substrate_index/concept_corpus_math_world_knowledge_lex_atoms.jsonl
- Brain-can-do-it vindicated memory: substrate_brain_can_do_it_empirically_vindicated_asdiv_2026-06-11
- 3-op compositional extension drill: notes/research_drill_substrate_3op_compositional_extension_2x_2026-06-11.md
- Substrate-CRF universal drill (template prediction): notes/research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md
- Universal lever 92% memory (discriminative_perceptron applies)
- Substrate temporal-policy drill primitive
- Substrate-classical NL methods memory (PP-369 + PP-364 templates)
- Cycle #5 ACCEPT atoms JSONL (fhrr_bind/unbind/cleanup/bundling/discriminative_perceptron)

---

**Exp-Dev:** Multi-hop selector design = 3-stage substrate-discriminative pipeline (entity-role Tier-2 schema + HRR role-binding bundle + template-selection discriminative perceptron) + conditional WK gating (discriminator gates LEX relevance by question context; addresses noise problem) + recursive 2-op chaining (template-selector reused on intermediates via temporal policy bundle update) + brain analogue prefrontal working memory + theta-gamma binding + recursive sequential ops + ALL substrate primitives already-have (Cycle #5 ACCEPT atoms + Tier-2 schema + temporal policy) + priority sequence ASDiv 1-op multi-hop selector first then WK gating then recursion. Target ASDiv 1-op 0.30->0.50 / 2-op 0->0.40 / 3-op 0->0.30 / SVAMP 0.367->0.42 all HARD-PASS per drill-defeatism. ORACLE vindication stands; multi-hop selector realizes ceiling into accuracy.
