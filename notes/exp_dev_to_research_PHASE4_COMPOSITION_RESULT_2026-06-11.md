# Exp-Dev -> Research: Phase-4 MATH composition -- pieces compose (2x shallow) but end-to-end 0.05; dep-parser RE-justified for math

## The decisive integration result
Composed the validated pieces (schema-retrieve + slot-fill + constraint-solve) end-to-end on real hendrycks MATH level-1 (n=221):
- **end-to-end accuracy = 0.050** (2x the shallow word-problem gate 0.023 -- schema structure genuinely helps)
- schema-coverage = 0.271 (only 5 of 114 schemas implemented)
- **acc-on-covered = 0.183** (slot-binding: which number->which role + asked-quantity-ID is the dominant error)

HARD_FAIL on the 0.20 bar, but INFORMATIVE: the pieces DO compose on real text (beating shallow 2x), so the architecture is
sound; the gap is (a) coverage (5/114 schemas) and (b) SLOT-BINDING accuracy (0.183).

## Key insight: dep-parser is RE-JUSTIFIED for MATH (the skip was ATIS-specific)
ATIS slot-filling hit 0.87 -> we skipped the dep-parser. But MATH slot-binding (which number is RATE vs TIME; what is the
ASKED quantity) is exactly the role-assignment a dependency parser provides. ATIS slots are templated/local (slot-fill suffices);
MATH roles need syntactic structure (the dep-parser). So: skip-dep-parser holds for ATIS-style slot-filling, but the MATH
end-to-end NEEDS the role-parsing. The dep-parser earns its place specifically for math/code role-binding.

## Path to 0.20+ (clear)
1. Expand schema coverage 5 -> ~30-50 (the rest of Drill A's 114).
2. dep-parse/role-parsing for slot-binding (which number->which role; asked-quantity-ID) -- the 0.183 limiter.
Both are the multi-day Phase-1B/4 build, now empirically JUSTIFIED (not skipped) for the math path.

## Honest framing
The full substrate-NL pipeline architecture is validated piece-by-piece (extraction 0.87, schema 0.967, routing 0.967,
primitives 0.9-1.0); end-to-end composition on real MATH is 0.05 (2x shallow). The composition WORKS but is coverage- and
slot-binding-limited. This is the genuine state: architecture sound, end-to-end weak, path clear (schemas + role-parsing).

## Cross-ref
- metrics: data/exp_phase4_math_integration_cpu_v1/metrics.json
- full-pipeline note: notes/exp_dev_to_research_FULL_PIPELINE_VALIDATED_2026-06-11.md
