"""SKUNKWORKS build: a SUBSTRATE-OF-SUBSTRATE seed -- the substrate storing its own essence
so it can understand + improve itself (USER goal 2026-06-13).

Stdlib only. Does NOT touch the canonical relations index (mid-rebuild). Writes a STAGING seed
of meta-atoms (substrate's own operators / axes / rules / findings / open improvement proposals)
and runs a SELF-AUTHORING proposer: the substrate proposes its OWN internal edges from body text
via shared-term overlap (the INV-1 C3 blind signal used GENERATIVELY, not as an audit). Isolated
meta-atoms = under-connected design elements = improvement targets.

Outputs (staging; Research/Testbed ratify + ingest later, atomically, post-rebuild):
  data/substrate_index/meta_substrate_seed.jsonl          (the essence atoms)
  data/substrate_index/meta_substrate_proposed_edges.jsonl (substrate's self-proposed relations)
"""
import json, re, itertools
from pathlib import Path

OUT = Path("data/substrate_index")
STOP = set("the a an of to in on for and or is are be by via with from as at it its this that "
           "substrate atom atoms axis rule via use uses used not no any all per into over "
           "more most than then when what which how why does cannot can must should via".split())

# ---- The substrate's essence, as meta-atoms. kind in {OPERATOR, AXIS, RULE, FINDING, PROPOSAL}.
# body carries the characteristic vocabulary so the self-proposer can find real structure.
ESSENCE = [
 # OPERATORS (the tools the substrate computes WITH)
 ("OP/fhrr_bind","OPERATOR","FHRR circular-convolution binding of role and filler complex unit vectors; superpose bound pairs; near-orthogonal high-dimensional binding"),
 ("OP/cleanup_memory","OPERATOR","cleanup attractor memory; modern Hopfield Ramsauer; denoise a noisy vector to nearest stored codebook entry; energy descent attractor"),
 ("OP/resonator_decoder","OPERATOR","resonator network factorization; decode a superposed bound product into constituent codebook factors; iterative attractor cleanup"),
 ("OP/codebook_geometry","OPERATOR","codebook matrix spectral geometry; cosine similarity; intra-cluster cosine; archetype clusters; Marchenko-Pastur bulk; BBP spike"),
 ("OP/L6_proof_finder","OPERATOR","backward-chaining sound prover; DEPENDS_ON proof chains to axioms; generalized typing context; proof depth; Curry-Howard derivation"),
 ("OP/chtv_verifier","OPERATOR","type-checker verifier; Curry-Howard derivation soundness; zero false-accept; checkable ground truth; reject hallucinated proof"),
 ("OP/kp_promotion","OPERATOR","knowledge promotion operator T3 record to T2 instance to T1 foundational; multi-mechanism frequency geometry bisimulation; complementary coverage"),
 ("OP/l1_partition_routing","OPERATOR","L1 categorical partition routing; N-invariant recall; route query to partition; decoupled cue; scaling 10M"),
 ("OP/shares_math_bisimulation","OPERATOR","SHARES_MATH structural equivalence; coalgebraic bisimulation; archetype equivalence classes; shared capability; quantale fuzzy graded"),
 ("OP/sleep_replay","OPERATOR","sleep replay consolidation; codebook geometry clusters; replay T3 to T2 archetype; spectral cluster structure"),
 ("OP/two_vector_encoder","OPERATOR","two-vector composite encoder; algebra_hrr plus name_vec; wide robust alpha plateau; high-dimensional near-orthogonality superpose"),
 ("OP/spectral_observability","OPERATOR","spectral observability; free cumulants; Marchenko-Pastur bulk; Tracy-Widom edge; BBP spike; Dyson Brownian motion; random matrix theory"),
 # AXES (how the substrate carves knowledge)
 ("AXIS/epistemic_tier","AXIS","epistemic tier T0 axioms T1 foundational T2 instances T3 records; Curry-Howard; survives authoring-blind null; CHTV L6-PROOF independent"),
 ("AXIS/content_type","AXIS","content-type quaternary FORMAL_SYSTEMS INFORMAL_SYSTEMS RECORDS EPISODIC; systems-vs-records classifier; survives authoring-blind"),
 ("AXIS/load_bearing","AXIS","load-bearing tools-vs-materials; DOWNGRADED authoring-bound not body-text invariant; INV-1 C3 null z=0.48; curator-authored usage structure"),
 # RULES (methodology / governance the substrate operates under)
 ("RULE/held_out_test","RULE","held-out test methodology required for macro F1 claims; Goodhart risk; new questions after mechanism shipment; 11th rule"),
 ("RULE/authoring_blind_null","RULE","independence claims require authoring-blind null; label-shuffle at fixed structure; orthogonality analog of held-out test; 15th rule"),
 ("RULE/always_reconsider","RULE","always reconsider frameworks do not lock in prematurely; honesty both directions; downgrade locked claims when refuted; 7th rule"),
 ("RULE/verify_before_assert","RULE","verify before asserting; mid-rebuild index returns silently-wrong; completeness gate; check counts before running relation cells"),
 ("RULE/load_bearing_axis","RULE","substrate-load-bearing tools-vs-materials distinction; CANDIDATE authoring-bound qualifier; 13th rule downgraded per INV-1"),
 # FINDINGS (what the substrate has learned about itself)
 ("FIND/inv1_load_bearing_authored","FINDING","INV-1 C3 z=0.48 load-bearing axis NOT readable from body text; authored not intrinsic; canary for authored-vs-discovered confound"),
 ("FIND/kp_complementary_coverage","FINDING","KP P1 P3 P4 candidate sets near-disjoint overlap 0.125; complementary coverage not convergence; multi-mechanism partitions atom space"),
 ("FIND/chp6_soundness_gap","FINDING","CH-P6 substrate zero false-accept vs Qwen hallucinated; checkable ground truth; soundness gap; small-model low-depth caveat"),
 ("FIND/cell_sc_n_invariant","FINDING","CELL SC N-invariant partition routing recall 0.765 survives 10M; flat-RAG degrades; scaling structure independent of authoring"),
 ("FIND/spectral_pillar_9d","FINDING","9-dimensional spectral observability pillar; free cumulants Tracy-Widom BBP spike Dyson; random matrix theory universal; node-label independent"),
 # PROPOSALS (open improvement directions -- the substrate's plan to improve itself)
 ("PROP/self_authoring","PROPOSAL","self-authoring substrate; operators propose edges from atom bodies; curator ratifies; discovered-fraction autonomy index grows; shared-symbol overlap"),
 ("PROP/crystallized_atoms","PROPOSAL","crystallized atoms; cluster continuous learned embedding field; crystallize stable high-density attractors into discrete observable atoms; codebook geometry"),
 ("PROP/emergent_ontology","PROPOSAL","emergent ontology; unsupervised factorization NMF archetypal analysis manifold; emergent axes vs imposed axes; keep validated promote new"),
 ("PROP/honest_head_to_head","PROPOSAL","honest head-to-head harness; strongest local LLM baseline; measured gap not projected; falsifiable North Star crucial experiment"),
 ("PROP/claim_survival_calibration","PROPOSAL","claim-survival calibration; log every lock and its fate survives downgrades reverses; auto-raise lock bar; metacognition about research process"),
 ("PROP/substrate_as_scaffold","PROPOSAL","substrate as sound observable memory and prover scaffold; turns unsound LLM into verifiable hybrid; measure lift; complementary not replacement"),
]

def symbols(body):
    toks = re.findall(r"[a-zA-Z_]{4,}", body.lower())
    return {t for t in toks if t not in STOP}

atoms = [{"id": i, "kind": k, "body": b, "symbols": sorted(symbols(b))} for (i, k, b) in ESSENCE]
OUT.joinpath("meta_substrate_seed.jsonl").write_text(
    "\n".join(json.dumps(a) for a in atoms) + "\n")

# ---- SELF-AUTHORING proposer: substrate proposes its own edges from body-text overlap.
TAU = 0.10
edges = []
for a, b in itertools.combinations(atoms, 2):
    sa, sb = set(a["symbols"]), set(b["symbols"])
    if not sa or not sb:
        continue
    j = len(sa & sb) / len(sa | sb)
    if j >= TAU:
        edges.append({"src": a["id"], "dst": b["id"], "jaccard": round(j, 3),
                      "shared": sorted(sa & sb)})
edges.sort(key=lambda e: -e["jaccard"])
OUT.joinpath("meta_substrate_proposed_edges.jsonl").write_text(
    "\n".join(json.dumps(e) for e in edges) + "\n")

# ---- Report: what did the substrate propose about itself? Where are the improvement targets?
deg = {a["id"]: 0 for a in atoms}
for e in edges:
    deg[e["src"]] += 1; deg[e["dst"]] += 1
isolated = sorted([i for i, d in deg.items() if d == 0])

print(f"meta-atoms (substrate essence): {len(atoms)}  "
      f"({', '.join(sorted({a['kind'] for a in atoms}))})")
print(f"self-proposed edges (Jaccard>={TAU}): {len(edges)}")
print("\nTOP 12 self-proposed relations (substrate connecting its own pieces):")
for e in edges[:12]:
    print(f"  {e['jaccard']:.3f}  {e['src']:32s} <-> {e['dst']:32s}  [{', '.join(e['shared'][:4])}]")
print("\nMOST-CONNECTED essence atoms (load-bearing in substrate's self-model):")
for i, d in sorted(deg.items(), key=lambda kv: -kv[1])[:6]:
    print(f"  deg={d:2d}  {i}")
print("\nISOLATED essence atoms (IMPROVEMENT TARGETS -- under-connected design elements):")
for i in isolated:
    print(f"  {i}")
print(f"\nwrote: {OUT/'meta_substrate_seed.jsonl'}")
print(f"wrote: {OUT/'meta_substrate_proposed_edges.jsonl'}")
