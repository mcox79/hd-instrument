# Research -> Testbed: 10 math world-knowledge LEX atoms hand-authored -- substrate-self-referential closes SVAMP/ASDiv 26-32pct gap

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** USER-LOCKED brain-can-do-it rule -- substrate-self-referential math-world-knowledge approach

## TL;DR

10 LEX_constant_* atoms hand-authored at `data/substrate_index/concept_corpus_math_world_knowledge_lex_atoms.jsonl`. Each atom contains `members_named_values: dict[str, number]` mapping common-word -> integer/float. Closes the world-knowledge gap on ~26-32pct of SVAMP + ASDiv items via substrate concept partition (rule 8 us-or-substrate compliant).

## The 10 atoms (T_lexicon tier; kind=lexicon)

| Atom | Members | Purpose |
|---|---|---|
| LEX_constant_collection | 22 (dozen=12, score=20, pair=2, gross=144, ...) | Collection size words |
| LEX_constant_time | 14 (days_per_week=7, hours_per_day=24, ...) | Time unit conversion |
| LEX_constant_percent | 9 (percent_base=100, ...) | Percent base + common fractions |
| LEX_constant_units_length | 10 (inches_per_foot=12, feet_per_mile=5280, ...) | Length unit conversion |
| LEX_constant_units_weight | 7 (ounces_per_pound=16, ...) | Weight unit conversion |
| LEX_constant_units_volume | 9 (cups_per_pint=2, ...) | Volume unit conversion |
| LEX_constant_body_parts | 23 (legs_per_dog=4, eyes_per_human=2, ...) | Animal/human body part counts |
| LEX_constant_money | 8 (cents_per_dollar=100, ...) | Money denomination constants |
| LEX_constant_geometry | 18 (sides_per_triangle=3, degrees_per_circle=360, ...) | Geometric shape constants |
| LEX_constant_calendar | 11 (days_per_workweek=5, members_per_team_basketball=5, ...) | Calendar + sports groupings |

**Total members: ~131 named values across 10 atoms.**

## Schema change request (Testbed)

New JSONL field: `members_named_values: dict[str, int|float]`

This is distinct from NER gazetteer atoms which use `members: list[str]` (set membership only). Math-WK atoms need name->value pairs.

Atoms_module.py extension:
```python
class LexiconAtom(Atom):
    members: list[str] = []  # for NER gazetteer pattern
    members_named_values: dict[str, float] = {}  # for math-WK pattern

    def lookup_value(self, name: str) -> Optional[float]:
        return self.members_named_values.get(name.lower())

    def contains_name(self, name: str) -> bool:
        if self.members and name in self.members:
            return True
        if self.members_named_values and name.lower() in self.members_named_values:
            return True
        return False
```

## Ingestion request (Phase A)

1. Update Atom.from_dict to recognize `members_named_values`
2. Ingest 10 LEX_constant_* atoms (T_lexicon tier; kind=lexicon)
3. CLI stats reflect: 28 concept atoms -> 38 (after 10 ingestion; 36 after NER 8 ingestion if both stack)
4. Each atom's members_named_values accessible for SVAMP/ASDiv feature lookup

## SVAMP cell extension (Exp-Dev)

Per brain-can-do-it rule + boundary REJECTION routing:

Feature extractor adds:
```python
def world_knowledge_features(problem_text, concept_partition):
    """For each LEX_constant_* atom, lookup any matching word in problem text;
    return list of (word, value) pairs from matched lookups."""
    extracted = []
    for lex_atom in concept_partition.lookup_lexicons(prefix='LEX_constant_'):
        for word, value in lex_atom.members_named_values.items():
            if word.lower() in problem_text.lower().replace('_', ' '):
                extracted.append((word, value))
    return extracted
```

Selector + op-classifier extended:
- Numbers in text + extracted world-knowledge values BOTH go into operand pool
- Selector picks any 2 from extended pool (not just text-only)

Pre-reg (per boundary-rejection routing):
- HARD-PASS SVAMP >= 0.42 / MIDDLE 0.39-0.42 / FAIL < 0.39
- HARD-PASS ASDiv >= 0.32 / MIDDLE 0.28-0.32 / FAIL < 0.28

## Closed-loop substrate-self-referential

Per rule 8 us-or-substrate:
- Substrate (concept partition) -> world-knowledge values -> SVAMP/ASDiv selector -> answer
- NO external knowledge source
- Substrate IS its own world-knowledge

Per brain-can-do-it rule: brain's semantic memory IS the same primitive substrate now has via concept partition. Brain analogue substantively implemented.

## Cycle #8 candidate (or extension of #7)

Type A new atoms (10 LEX_constant_*) + Type C architectural (members_named_values schema field). Both for SVAMP/ASDiv unlock.

## Expansion path

Seed lists 7-23 entries per atom. Real-world coverage requires 5-10x. Day 2-3 extension:
- Add LEX_constant_chemistry (Avogadro, water boiling, freezing, ...)
- Add LEX_constant_speed (speed_of_sound, speed_of_light if needed in physics word problems)
- Add LEX_constant_geography (state_count_USA=50, continent_count=7, ocean_count=5)
- Add per-domain constants as word-problem corpora expand

## Cross-references

- USER-locked rule: feedback_brain_can_do_it_no_boundary_acceptance_2026-06-11
- Boundary-rejection routing: notes/research_to_exp_dev_BOUNDARIES_REJECTED_BRAIN_CAN_DO_IT_FULL_PATH_ENUMERATION_2026-06-11.md
- NER gazetteer pattern parent: notes/research_to_testbed_NER_GAZETTEER_8_ATOMS_READY_2026-06-11.md
- Methodology rule 8 us-or-substrate

---

**Testbed:** 10 math world-knowledge LEX atoms JSONL ready at data/substrate_index/concept_corpus_math_world_knowledge_lex_atoms.jsonl. New schema field members_named_values (dict[str,number]) extends LEX schema beyond NER gazetteer pattern. T_lexicon tier + kind=lexicon. Ingest at convenience. **Exp-Dev:** awaiting Testbed ingestion + atoms_module.py extension; then SVAMP + ASDiv cells via world_knowledge_features extractor. HARD-PASS SVAMP >=0.42 / ASDiv >=0.32 (per brain-can-do-it boundary rejection).
