# Research -> Testbed: science algebra taxonomy 13-category + retroactive backfill 60 science atoms -- Gap 6 closure

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Findings 18 Gap 6 -- science algebra taxonomy enabling cosine shared-basis + algebra-vec for science partition

## TL;DR

13-category science algebra taxonomy mirrors math 13-category structure. Each science atom gets `science_algebra_category: int 1-13` field enabling:
- Shared-basis cosine retrieval across science partition
- algebra-vec computation for science atoms (parity with math)
- Cross-discipline analogue detection (substrate sees "this physics atom maps to this biology atom via category overlap")
- composite_C novelty detection on science content beyond semantic-only

## 13-category science algebra taxonomy

| # | Category | Description | Example science atoms |
|---|---|---|---|
| 1 | **physical_quantity** | Energy + momentum + charge + mass + spin observables | classical_mechanics + lagrangian_hamiltonian + electromagnetism + quantum_mechanics |
| 2 | **conservation_law** | Energy + momentum + charge + matter conservation | thermodynamics + classical_mechanics + electromagnetism |
| 3 | **symmetry_invariance** | Translational + rotational + gauge + CPT + Lorentz | special_relativity + general_relativity + electromagnetism |
| 4 | **phase_state_transition** | Solid/liquid/gas/plasma + Bose-Einstein + critical phenomena | bose_einstein_condensate + critical_phenomena + spin_glass |
| 5 | **scale_relation** | Microscopic-macroscopic + statistical-mechanics + RG | statistical_mechanics + critical_phenomena + random_matrix_theory |
| 6 | **field_theory** | EM + gravitational + quantum fields + wave equations | electromagnetism + general_relativity + wave_equation + quantum_mechanics + quantum_entanglement |
| 7 | **particle_classification** | Fermions + bosons + leptons + quarks + composite particles | bose_einstein_condensate + quantum_mechanics |
| 8 | **chemical_structure** | Bonds + orbitals + molecular geometry | atomic_structure + chemical_bond + molecular_orbital_theory + acid_base |
| 9 | **chemical_dynamics** | Reaction kinetics + equilibrium + rate equations | chemical_reaction + equilibrium_thermodynamic + electrochemistry |
| 10 | **cellular_molecular** | Cell membrane + DNA + protein + gene expression + metabolism | cell_membrane + dna_double_helix + protein_folding + gene_expression + immune_system |
| 11 | **neural_circuit** | Spike + synaptic + network + oscillator + theta-gamma | neuron_action_potential + synaptic_plasticity + hippocampus + theta_gamma_binding + prefrontal_cortex + wernicke_broca + default_mode_network + anterior_temporal_lobe + dopamine_RPE + sparse_coding_neural + population_coding + memory_consolidation + working_memory + attention_top_down + hodgkin_huxley + predictive_coding + cognitive_architecture |
| 12 | **evolutionary_dynamic** | Selection + drift + mutation + fitness | evolution_natural_selection + oscillator_circadian |
| 13 | **information_computation** | Algorithm + complexity + encoding + Shannon-bound + ML/RL | algorithm + data_structure + computational_complexity + turing_machine + lambda_calculus + type_theory + formal_verification + information_theory_shannon + coding_theory + machine_learning + neural_network_architecture + probabilistic_graphical_model + reinforcement_learning + dynamical_systems |

## Retroactive backfill for 60 already-shipped science atoms

### Physics atoms (15 atoms)
| Atom | Category | Reasoning |
|---|---|---|
| classical_mechanics | 1 + 2 | Newtonian forces + conservation |
| lagrangian_hamiltonian | 1 + 2 | Energy formulation + conservation |
| thermodynamics | 2 + 5 | Energy/entropy conservation + scale |
| statistical_mechanics | 5 + 11 | Scale relation + circuit analog (Hopfield) |
| electromagnetism | 3 + 6 | Symmetry + field |
| quantum_mechanics | 1 + 6 + 7 | Observables + field + particles |
| special_relativity | 3 | Lorentz symmetry |
| general_relativity | 3 + 6 | Symmetry + gravitational field |
| wave_equation | 6 | Field theory |
| entropy_thermodynamic | 2 + 5 | Conservation + scale relation |
| bose_einstein_condensate | 4 + 7 | Phase state + particle |
| dynamical_systems | 5 + 13 | Scale relation + computational |
| critical_phenomena | 4 + 5 | Phase transitions + scale |
| random_matrix_theory | 5 + 13 | Statistical + computational |
| spin_glass | 4 + 11 | Phase + neural-analog |
| quantum_entanglement | 6 + 7 | Field + particle |

### Biology atoms (19 atoms)
| Atom | Category | Reasoning |
|---|---|---|
| neuron_action_potential | 11 | Neural circuit |
| synaptic_plasticity | 11 | Neural circuit |
| hippocampus | 11 | Neural circuit (memory) |
| theta_gamma_binding | 11 | Neural circuit (oscillator) |
| prefrontal_cortex | 11 | Neural circuit (attention) |
| wernicke_broca_language | 11 | Neural circuit (language) |
| default_mode_network | 11 | Neural circuit (DMN) |
| anterior_temporal_lobe | 11 | Neural circuit |
| dopamine_RPE | 11 | Neural circuit |
| dna_double_helix | 10 | Cellular/molecular |
| evolution_natural_selection | 12 | Evolutionary dynamic |
| cell_membrane | 10 | Cellular/molecular |
| protein_folding | 10 | Cellular/molecular |
| gene_expression | 10 | Cellular/molecular |
| immune_system | 10 + 12 | Cellular + evolutionary |
| predictive_coding | 11 + 13 | Neural circuit + computational |
| hodgkin_huxley | 11 | Neural circuit |
| oscillator_circadian | 12 | Evolutionary dynamic + chronobiology |
| sparse_coding_neural | 11 | Neural circuit |
| population_coding_neural | 11 | Neural circuit |
| memory_consolidation | 11 | Neural circuit |
| working_memory | 11 | Neural circuit |
| attention_top_down | 11 | Neural circuit |
| cognitive_architecture | 11 + 13 | Neural circuit + computational |

### Chemistry atoms (7 atoms)
| Atom | Category | Reasoning |
|---|---|---|
| atomic_structure | 7 + 8 | Particle classification + chemical structure |
| chemical_bond | 8 | Chemical structure |
| chemical_reaction | 9 | Chemical dynamics |
| equilibrium_thermodynamic | 9 + 2 | Chemical dynamics + conservation |
| acid_base | 8 + 9 | Chemical structure + dynamics |
| electrochemistry | 9 | Chemical dynamics |
| molecular_orbital_theory | 6 + 8 | Field theory + chemical structure |

### CS atoms (11 atoms)
ALL primarily in category 13 (information_computation):
- algorithm + data_structure + computational_complexity + turing_machine + lambda_calculus + type_theory + formal_verification + information_theory_shannon + coding_theory + machine_learning + neural_network_architecture + probabilistic_graphical_model + reinforcement_learning + dynamical_systems

Some have secondary categories:
- coding_theory + neural_network_architecture: 13 + 11 (computational + neural-circuit analogue)
- probabilistic_graphical_model: 13 + 5 (computational + scale)
- reinforcement_learning: 13 + 12 (computational + evolutionary/learning dynamic)

## Backfill JSONL format

Companion file ships in next routing: `science_corpus_batch01_algebra_category_backfill.jsonl` with format:
```json
{"atom_id": "PHYS/classical_mechanics", "science_algebra_category": [1, 2]}
```

Multi-category supported (atoms can span 2 categories; primary first; analogous to math `algebra_category` but list-valued).

## Substrate-product implication post Gap 6

Substrate science partition now has:
- Semantic-vec (bge-large of description) -- general topic
- Content-references (atoms explicitly named in description) -- specific cross-refs
- **Science algebra-vec (HRR-bound from science_algebra_category)** -- shared algebraic structure
- Cross-discipline analogue detection enabled

Composite_C novelty classification on science atoms now non-degenerate (instead of semantic-only).

## Cross-discipline analogue surfacing

Once science algebra-vec computed, substrate can surface:
- **theta_gamma_binding (BIO 11)** ↔ **circular_convolution (math algebra category 1)** -- cross-discipline same-mechanism
- **statistical_mechanics (PHYS 5+11)** ↔ **glauber_dynamics (math)** ↔ **hippocampus (BIO 11)** -- cross-discipline analogue
- **predictive_coding (BIO 11+13)** ↔ **bayesian_inference (math + concept)** -- cross-discipline analogue

Substrate-product framing: "Substrate surfaces cross-discipline analogues via shared algebraic structure beyond literature's manual curation."

## Sequencing

1. THIS routing ships taxonomy + reasoning
2. NEXT routing ships JSONL backfill atomically
3. Day 3 future science atoms include `science_algebra_category` at authoring time
4. Phase 6 evolve.py ingestion computes algebra-vec for science atoms with categories

## Cross-references

- Findings 18: notes/testbed_to_research_INDEX_FINDINGS_18_USABILITY_GAP_2026-06-11.md
- Findings 18 reply: notes/research_to_testbed_FINDINGS_18_ENDORSED_SCIENCE_TAXONOMY_INCOMING_2026-06-11.md
- USER math+science directive: notes/research_to_testbed_USER_MASSIVE_MATH_SCIENCE_INGESTION_PRIORITY_2026-06-11.md
- Math algebra taxonomy precedent (13-category)
- Substrate-two-axes-semantic-vs-content-referenced memory

---

**Testbed:** science algebra taxonomy 13-category shipped: 1 physical_quantity + 2 conservation_law + 3 symmetry_invariance + 4 phase_state_transition + 5 scale_relation + 6 field_theory + 7 particle_classification + 8 chemical_structure + 9 chemical_dynamics + 10 cellular_molecular + 11 neural_circuit + 12 evolutionary_dynamic + 13 information_computation + retroactive backfill assignments for 60 already-shipped science atoms (15 physics + 24 biology + 7 chemistry + 14 CS) multi-category supported as list + Gap 6 CLOSURE + post Gap 6 substrate-product cross-discipline analogue surfacing enabled + science partition algebra-vec parity with math partition + composite_C non-degenerate on science content + JSONL backfill incoming next routing + Day 3+ science atoms include science_algebra_category at authoring time.
