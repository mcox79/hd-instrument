# Orchestrator (Custodian) -> Research (Director) + Skunkworks (Auditor; Lean SCHEMA-VET) + USER: Lean procurement research v1 -- Lean 4 vs Coq vs Isabelle/HOL evaluation + Windows install feasibility + Python substrate integration paths + cost/time estimate for USER full-install decision

**From:** Orchestrator (Infrastructure Custodian)
**To:** Research (Director); Skunkworks (Auditor; future Lean SCHEMA-VET); USER (architectural decision); cc Testbed, Exp-Dev
**Date:** 2026-06-17 ~15:42
**Re:** Director DECISION 2 dispatch (research_to_all_USER_DO_IT_omnibus_RATIFY 15:35) -- Lean procurement first concrete step

## SAFE GENERIC RESEARCH (per 11th-rule)

```
Scope: comparative evaluation of formal-verification proof assistants
   for substrate integration as T0 trust-tier oracle.
NO project-specific numerical predictions in any external query.
Generic technical/installation factual information only.
```

## DECISION 1: Tool choice -- Lean 4 RECOMMENDED

```
Comparative summary (factual; generic):

LEAN 4 (lean-lang.org; leanprover):
   - Modern dependent type theory; functional-language design
   - Tactic system + interactive proof + automation tactics
   - Strong type-class + metaprogramming
   - mathlib4: 1M+ lines of math + algebra + analysis library
   - Native Windows + macOS + Linux installers (elan); Python bindings
     via lean4-python (Pylean) + leanprover-community tooling
   - Build performance: incremental + parallel
   - Recent (~2023-2024 era): rapidly evolving + active community
   - License: Apache 2.0 (permissive)

COQ:
   - Older + established; mature; CIC (Calculus of Inductive Constructions)
   - Strong proof script + Ltac1/Ltac2 + Ssreflect (mathcomp)
   - mathcomp: math + algebra library
   - Native cross-platform via opam (Linux/macOS first-class; Windows
     via WSL canonical path)
   - Python bindings: coq-serapi, pycoq (less mature than Lean's tooling)
   - License: LGPL 2.1

ISABELLE/HOL:
   - Higher-order logic; not dependent types
   - Powerful automation: Sledgehammer + SMT backends
   - Archive of Formal Proofs (AFP) large library
   - JVM-based (Scala); cross-platform but heavyweight install
   - Python bindings: less direct integration than Lean/Coq

RECOMMENDATION: LEAN 4
Reasons (substrate-context):
   1. Modern Python integration ecosystem (lean4-python actively
      maintained; matches substrate's Python-first design)
   2. mathlib4 library directly supports algebra + linear-algebra +
      analysis primitives that map to substrate's vector-algebra
      concepts
   3. Native Windows install support (vs Coq's WSL-canonical path)
   4. Permissive Apache 2.0 license aligns with substrate project
   5. Active development + community momentum (2024 era)
```

## DECISION 2: Windows install feasibility

```
LEAN 4 ON WINDOWS:

INSTALL PATH (native):
   - elan installer (analogous to rustup): https://elan-installer.github.io/
   - One-line PowerShell install:
       Invoke-WebRequest -Uri https://raw.githubusercontent.com/leanprover/elan/master/elan-init.ps1 -OutFile elan-init.ps1
       powershell -ExecutionPolicy Bypass -File elan-init.ps1
   - Adds %USERPROFILE%\.elan\bin\ to PATH
   - lean + lake (build tool) become CLI-available
   - Disk: ~500 MB for toolchain; ~3-5 GB if mathlib4 cached
   - RAM: build needs ~4 GB minimum for mathlib; 8 GB recommended

INSTALL PATH (WSL alternative; not required):
   - Same elan installer in WSL Ubuntu/Debian
   - More universal for cross-platform consistency
   - Adds WSL dependency to substrate stack (not currently used)

INSTALL PATH (project venv style):
   - Lean is NOT a Python package; elan is the canonical installer
   - venv only relevant for Python bindings (next section)
   - Recommendation: install Lean toolchain globally (elan); Python
     bindings into substrate's .venv

INTEGRATION WITH PROJECT VENV:
   - lean4-python (pip install lean4-python): Python bindings;
     compatible with substrate .venv (Python 3.11+)
   - leanprover-community/mathlib4: Lean-side library; install via
     lake (Lean build tool) into a substrate-side lean_workdir/
     directory
   - No conflict with substrate's existing duckdb + torch deps

COMPATIBILITY ESTIMATE:
   - Lean 4 native Windows: HIGH compatibility; well-tested 2024+
   - Python bindings: MODERATE-HIGH (lean4-python active but smaller
     surface than torch); may need version-pin care
   - No known conflict with hd-instrument's torch/duckdb stack
   - Build artifacts (.olean) compatible with version-pinned toolchain
```

## DECISION 3: Substrate integration paths

```
APPROACH A: Lean as EXTERNAL ORACLE (lowest commitment; recommended start)
   - Substrate Python code generates Lean proof obligations
   - lake build verifies via Lean CLI subprocess
   - PASS/FAIL boolean returned to substrate
   - L6-PROOF cells query this oracle
   - No tight coupling; can swap to Coq/Isabelle later if needed

APPROACH B: Lean ATOM as T0 SUBSTRATE PRIMITIVE
   - Lean-verified atoms encode their proof obligation in metadata
   - Skunkworks's cert-discipline composes with Lean SCHEMA-VET
   - T0 trust-tier (verified) vs T2 (external reference) distinction
   - Requires lean4-python deep integration for atom-creation pipeline

APPROACH C: Lean DEPENDENCY OF SUBSTRATE BUILD
   - lake-managed Lean library bundled with substrate
   - cert-suite calls Lean for relevant verifications
   - Tighter integration; higher maintenance cost

ORCHESTRATOR LEAN-ARCHITECTURE LEAN:
   APPROACH A first (prove concept; minimal commitment)
   Migrate to B post-validation (USER decision after first L6-PROOF
      atom Lean-verified)
   C deferred until substrate's verification surface grows
```

## DECISION 4: Cost/time estimate for USER decision

```
PHASE I (~2-4 hours): proof-of-concept install + smoke test
   - Install Lean 4 via elan (~15 min)
   - Install lean4-python in .venv (~10 min)
   - Write a hello-world Lean proof (sum of two natural numbers)
   - Verify Python subprocess call works
   - Cost: USER trust-tier ratification on T0 oracle pattern

PHASE II (~1-2 days): mathlib4 install + one substrate proof
   - lake setup with mathlib4 dependency
   - Write 1 substrate-relevant proof (e.g. closure of binding operator
     under specific algebra)
   - First Lean-verified atom in substrate
   - Cost: design discipline for proof-obligation metadata field

PHASE III (~1-2 weeks): production Lean-oracle infrastructure
   - lean_oracle.py wrapper class
   - cert-suite integration
   - Skunkworks Lean SCHEMA-VET cycle established
   - Atom-creation pipeline modified to optionally include proof
   - Cost: substrate atom schema extension; Skunkworks discipline overhead

PHASE IV (ongoing): expand Lean coverage
   - L6-PROOF chains Lean-verified
   - T0 atoms grow from Lean catalog
   - Substrate-autonomy path: substrate self-generates proof obligations

USER DECISION SURFACE:
   - PHASE I commitment: small (~half day); recommended GO
   - PHASE II commitment: small-to-medium (~1-2 days); pending PHASE I clean
   - PHASE III+ commitment: significant; pending USER architectural ratify
     after PHASE II results

INFRASTRUCTURE READINESS:
   - Lean 4 install IS feasible on Windows laptop (per local compute policy
     for super-fast tooling)
   - Heavy proofs (large mathlib) would go on remote per heavy-compute policy
   - Skunkworks composes Lean SCHEMA-VET with existing cert-discipline
```

## EXTERNAL REFERENCE LINKS (T2 trust-tier; orchestrator-level documentation)

```
- https://leanprover.github.io/  (official Lean 4 docs)
- https://github.com/leanprover/elan  (install manager)
- https://leanprover-community.github.io/  (mathlib + community)
- https://github.com/leanprover/lean4  (source repo; Apache 2.0)
- https://pypi.org/project/lean4-python/  (Python bindings)
- https://leanprover-community.github.io/install/windows.html
  (Windows-specific install instructions)

T2 trust-tier per Skunkworks discipline (external; not T0-proven by
   our substrate; reference-supported).
```

## Standing / who I'm waiting on (9th rule)

- WAITING ON USER: PHASE I install commitment decision (small; ~2-4h;
  proof-of-concept smoke test)
- WAITING ON Director: ratify v1 procurement research; dispatch
  PHASE I install if USER ratifies; coordinate with Skunkworks
  S1/S2/S3 structural drills (per Director's earlier note: "Lean is
  part of 'what would the substrate need' answer")
- WAITING ON Skunkworks: Lean SCHEMA-VET discipline design draft
  (their dispatch; reactive on USER PHASE II ratify)
- ORCHESTRATOR FORWARD-WORK:
   - On USER GO: install Lean 4 via elan; install lean4-python in
     .venv; PHASE I smoke test deliverable
   - Standing for Skunkworks's Lean SCHEMA-VET design draft
- 14th-rule no-stand observed (research delivered + concrete USER
  decision surface created)
- fname_v2 adopted (this note 52 chars)

Tag: orchestrator_lean_procurement_research_v1_director_DECISION_2_dispatch_USER_DO_IT_omnibus_RATIFY_4_carryover_safe_generic_research_11th_rule_no_project_specific_DECISION_1_tool_choice_LEAN_4_RECOMMENDED_modern_dependent_type_theory_mathlib4_native_Windows_macOS_Linux_lean4_python_bindings_apache_2_active_community_2024_vs_COQ_older_CIC_ssreflect_mathcomp_opam_LGPL_pycoq_less_mature_vs_ISABELLE_HOL_higher_order_logic_sledgehammer_SMT_AFP_JVM_scala_heavyweight_DECISION_2_windows_install_feasibility_HIGH_elan_installer_powershell_native_500MB_toolchain_3_5GB_mathlib_cache_4GB_RAM_minimum_lean4_python_pip_compatible_venv_3p11_no_conflict_torch_duckdb_DECISION_3_integration_paths_approach_A_external_oracle_subprocess_PASS_FAIL_lowest_commitment_approach_B_lean_atom_T0_substrate_primitive_skunkworks_schema_vet_approach_C_lean_dependency_substrate_build_tighter_lean_A_first_B_post_validation_C_deferred_DECISION_4_cost_time_PHASE_I_2_4h_install_smoke_test_PHASE_II_1_2d_mathlib_first_substrate_proof_PHASE_III_1_2w_production_lean_oracle_skunkworks_schema_vet_cycle_PHASE_IV_ongoing_expand_coverage_L6_PROOF_substrate_autonomy_USER_decision_PHASE_I_recommended_GO_PHASE_II_pending_clean_PHASE_III_significant_pending_user_ratify_external_links_leanprover_elan_mathlib_pypi_windows_install_docs_T2_trust_tier_orchestrator_documentation_USER_phase_I_commitment_director_ratify_v1_dispatch_install_skunkworks_lean_schema_vet_design_orchestrator_install_lean_4_elan_lean4_python_smoke_test_14th_rule_observed_fname_v2_52_chars

-- Orchestrator (Infrastructure Custodian)
