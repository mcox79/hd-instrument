"""Body-text multi-premise DEPENDS_ON extractor v2 -- parser-v2 per Exp-Dev spec.

Per Research routing 14:32 + Exp-Dev premise_extractor_prototype_baseline (14:30):
v1 extractor (commit d38660bc) achieved 1.87 avg refs per atom matching 40.6pct
of atoms. v2 adds the 3 spec components Exp-Dev identified to lift toward
A1 MPM gold 2.9 baseline:

  1. STEMMING / lemmatization: handles inflections (perceptrons/perceptron;
     algorithms/algorithm; methods/method)
  2. ABBREVIATION MAP: handles standard math/ML abbreviations
     (HMM->hidden_markov_model; DP->dynamic_programming; CFG->context_free_grammar;
     ML->machine_learning; KL->kullback_leibler; SVD->singular_value_decomposition;
     PCA->principal_component_analysis; RL->reinforcement_learning; etc.)
  3. POSSESSIVE NORMALIZATION: handles "Newton's method"->newton_method,
     "Bayes' theorem"->bayes_theorem, etc.
  4. Generic-term blocklist (already in v1; refined here)

Expected uplift per Exp-Dev: 1.0 -> 2.9 (Mathlib baseline 2.6+).

Implementation:
  - Pure stdlib stemmer (Porter-stem-style trim of plural/inflection suffixes;
    avoid heavy NLTK dependency for canonical-remote portability)
  - Hand-curated abbreviation expansion table (math/ML/CS standard ~50 entries)
  - Possessive regex (\\bX's\\b -> X)
  - Refined STOP_INDEX_TERMS list

NO LLM. NO bge. NO NLTK. Pure regex + dictionaries.
"""
from __future__ import annotations
import sys
import re
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


# Refined stop-words from v1.
STOP_INDEX_TERMS = {
    "atom", "axiom", "axioms", "theorem", "lemma", "definition", "proof",
    "rule", "rules", "set", "value", "data", "number", "function", "operation",
    "type", "vector", "matrix", "tensor", "graph", "node", "edge", "tree",
    "math", "concept", "field", "ring", "group", "category", "is_axiom",
    "true", "false", "none", "null", "name", "id", "tier", "algorithm",
    "model", "method", "process", "system",
    "and", "the", "for", "with", "from", "into", "this", "that", "via",
    "between", "across", "such", "than", "then", "when", "where", "while",
    "is", "are", "was", "were", "be", "been", "being", "has", "have", "had",
}

# Abbreviation map (per Exp-Dev spec; math/ML/CS standard).
ABBREVIATION_MAP = {
    "hmm": "hidden_markov_model",
    "dp": "dynamic_programming",
    "cfg": "context_free_grammar",
    "ml": "machine_learning",
    "rl": "reinforcement_learning",
    "nlp": "natural_language_processing",
    "kl": "kullback_leibler",
    "svd": "singular_value_decomposition",
    "pca": "principal_component_analysis",
    "ica": "independent_component_analysis",
    "lda": "latent_dirichlet_allocation",
    "qda": "quadratic_discriminant_analysis",
    "em": "em_algorithm",
    "gp": "gaussian_process",
    "gan": "generative_adversarial_network",
    "vae": "variational_autoencoder",
    "rnn": "recurrent_neural_network",
    "cnn": "convolutional_neural_network",
    "lstm": "long_short_term_memory",
    "gru": "gated_recurrent_unit",
    "bn": "batch_normalization",
    "ln": "layer_normalization",
    "ce": "cross_entropy",
    "mse": "mean_squared_error",
    "sgd": "stochastic_gradient_descent",
    "adam": "adam_optimizer",
    "lbfgs": "lbfgs_quasi_newton",
    "tsne": "t_distributed_stochastic_neighbor_embedding",
    "umap": "uniform_manifold_approximation_and_projection",
    "vsa": "vector_symbolic_architecture",
    "hrr": "holographic_reduced_representation",
    "fhrr": "fourier_holographic_reduced_representation",
    "ghrr": "ghrr_noncommutative_bind",
    "ner": "named_entity_recognition",
    "pos": "part_of_speech",
    "ast": "abstract_syntax_tree",
    "crf": "conditional_random_field",
    "hmm_em": "em_algorithm",
    "ks": "kolmogorov_smirnov",
    "tw": "tracy_widom_distribution",
    "mp": "marchenko_pastur_distribution",
    "mle": "maximum_likelihood",
    "map": "maximum_a_posteriori",
    "kkt": "karush_kuhn_tucker",
    "ode": "ordinary_differential_equation",
    "pde": "partial_differential_equation",
    "sde": "stochastic_differential_equation",
    "fft": "fast_fourier_transform",
    "dft": "discrete_fourier_transform",
    "mcmc": "mcmc_sampling",
    "ipf": "iterative_proportional_fitting",
    "mdp": "markov_decision_process",
    "qmdp": "markov_decision_process",
    "td": "temporal_difference_learning",
    "ppo": "proximal_policy_optimization",
    "dqn": "deep_q_network",
    "vi": "variational_inference",
    "vae": "variational_autoencoder",
    "ddpg": "deep_deterministic_policy_gradient",
}

# Possessive regex: matches "Newton's method", "Bayes' theorem", etc.
POSSESSIVE_PATTERN = re.compile(r"\b(\w+)'s\b", re.IGNORECASE)
APOSTROPHE_S_PATTERN = re.compile(r"\b(\w+)'\b", re.IGNORECASE)

MAX_EDGES_PER_ATOM = 50


def naive_stem(token: str) -> str:
    """Tiny stemmer: handle common inflections for math/CS English.
    Pure stdlib; not full Porter."""
    t = token.lower()
    # plurals
    if t.endswith("ies") and len(t) > 4:
        t = t[:-3] + "y"
    elif t.endswith("es") and len(t) > 3:
        t = t[:-2]
    elif t.endswith("s") and not t.endswith("ss") and len(t) > 3:
        t = t[:-1]
    # -ing -> base
    if t.endswith("ing") and len(t) > 5:
        t = t[:-3]
    # -ed -> base
    elif t.endswith("ed") and len(t) > 4:
        t = t[:-2]
    return t


def normalize_text(text: str) -> str:
    """Apply possessive + apostrophe normalization on text before matching."""
    text = POSSESSIVE_PATTERN.sub(r"\1", text)  # Newton's -> Newton
    text = APOSTROPHE_S_PATTERN.sub(r"\1", text)  # Bayes' -> Bayes
    return text.lower()


def expand_abbreviations(text: str, abbrev_map: dict) -> str:
    """For each abbreviation found as a whole word, also include the expansion
    as a hidden synonym (we append the expansion so subsequent regex match catches it)."""
    extra_tokens = []
    for abbrev, expansion in abbrev_map.items():
        if re.search(r"\b" + re.escape(abbrev) + r"\b", text, re.IGNORECASE):
            extra_tokens.append(expansion)
    if extra_tokens:
        text = text + " " + " ".join(extra_tokens)
    return text


def normalize_name_token(name: str) -> str:
    return name.strip().lower()


def collect_text_to_scan(atom) -> str:
    parts = [atom.description or "", atom.name or ""]
    alg = atom.algebra or {}
    for k, v in alg.items():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                parts.append(str(item))
    meta = atom.metadata or {}
    for k, v in meta.items():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                parts.append(str(item))
    return " ".join(parts)


def build_name_index(all_atoms, canonical_name_only: bool = True) -> dict:
    """Build {match_token: qualified_id} index; canonical-name-only filter."""
    index = {}
    for atom in all_atoms:
        candidates = []
        if "/" in atom.id:
            cn = atom.id.split("/", 1)[1]
        else:
            cn = atom.id
        candidates.append(cn)
        for alias in (atom.aliases or ()):
            candidates.append(alias)
        for c in candidates:
            tok = normalize_name_token(c)
            if not tok or tok in STOP_INDEX_TERMS:
                continue
            if canonical_name_only:
                if "_" not in tok and " " not in tok and len(tok) < 8:
                    continue
            if tok not in index:
                index[tok] = atom.qualified_id
    return index


def extract_premise_refs(text: str, name_index: dict, self_qid: str) -> set:
    """v2 extraction: normalize text first (possessive + abbreviation expansion),
    then word-boundary match against substrate name index."""
    text = normalize_text(text)
    text = expand_abbreviations(text, ABBREVIATION_MAP)
    refs = set()
    for tok, qid in name_index.items():
        if qid == self_qid:
            continue
        pattern = r"\b" + re.escape(tok) + r"\b"
        if re.search(pattern, text):
            refs.add(qid)
            if len(refs) >= MAX_EDGES_PER_ATOM:
                break
    # Also try stem-matched variants for richer coverage
    # (Match by reducing both text tokens and index tokens to stems via _ split + stemming)
    text_stems = set()
    for raw_tok in re.findall(r"\w+", text):
        text_stems.add(naive_stem(raw_tok))
    for tok, qid in name_index.items():
        if qid == self_qid or qid in refs:
            continue
        if len(refs) >= MAX_EDGES_PER_ATOM:
            break
        # Atom name parts
        name_parts = tok.split("_")
        if len(name_parts) >= 2:
            stem_parts = [naive_stem(p) for p in name_parts]
            # require all name parts found as stems
            if all(sp in text_stems for sp in stem_parts):
                refs.add(qid)
    return refs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-canonical-name-only", action="store_true")
    ap.add_argument("--skip-corpus", nargs="*", default=["meta"])
    args = ap.parse_args()

    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"loading atoms...")
    all_atoms = ps.all_atoms()
    print(f"total atoms: {len(all_atoms)}")

    canonical_only = not args.no_canonical_name_only
    print(f"building name index (canonical_name_only={canonical_only})...")
    name_index = build_name_index(all_atoms, canonical_name_only=canonical_only)
    print(f"name index size: {len(name_index)}")
    print(f"abbreviation map size: {len(ABBREVIATION_MAP)}")

    scan_atoms = [a for a in all_atoms
                  if (a.corpus.value if hasattr(a.corpus, "value") else str(a.corpus)) not in args.skip_corpus]
    print(f"atoms to scan: {len(scan_atoms)}")
    if args.limit:
        scan_atoms = scan_atoms[: args.limit]
        print(f"limited to first {len(scan_atoms)}")

    print(f"building existing edge set...")
    existing = set()
    for r in ps.iter_all_relations():
        try:
            existing.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass
    print(f"existing relations: {len(existing)}")

    atoms_with_refs = 0
    total_refs_found = 0
    edges_added = 0
    skipped_dup = 0
    failed = 0
    sample_extractions = []

    for i, atom in enumerate(scan_atoms):
        text = collect_text_to_scan(atom)
        if not text or len(text) < 20:
            continue
        refs = extract_premise_refs(text, name_index, atom.qualified_id)
        if not refs:
            continue
        atoms_with_refs += 1
        total_refs_found += len(refs)
        if len(sample_extractions) < 6 and len(refs) >= 2:
            sample_extractions.append((atom.qualified_id, atom.name, sorted(refs)[:6]))

        src_qid = atom.qualified_id
        for tgt_qid in refs:
            key = (src_qid, "DEPENDS_ON", tgt_qid)
            if key in existing:
                skipped_dup += 1
                continue
            if args.dry_run:
                edges_added += 1
                existing.add(key)
                continue
            try:
                ps.add_relation(src_qid, RelationType.DEPENDS_ON, tgt_qid,
                                source="body_text_multi_premise_extractor_v2",
                                note=f"v2 body-text match: {atom.name[:40]}")
                edges_added += 1
                existing.add(key)
            except Exception as e:
                msg = str(e)[:100]
                if any(k in msg.lower() for k in ("already", "duplicate")):
                    skipped_dup += 1
                else:
                    failed += 1

        if (i + 1) % 2000 == 0:
            print(f"  progress: {i+1}/{len(scan_atoms)} atoms; {edges_added} edges; {atoms_with_refs} with refs")

    print(f"\n=== BODY-TEXT v2 EXTRACTION SUMMARY ===")
    print(f"atoms scanned: {len(scan_atoms)}")
    print(f"atoms with >=1 premise ref: {atoms_with_refs}")
    print(f"total refs found: {total_refs_found}")
    print(f"avg refs (when present): {total_refs_found / max(atoms_with_refs, 1):.2f}")
    print(f"edges added: {edges_added}")
    print(f"edges skipped duplicate: {skipped_dup}")
    print(f"edges failed: {failed}")
    print(f"\nsample extractions (atoms with >=2 refs):")
    for qid, name, refs in sample_extractions:
        refs_short = [r.split("::")[-1] for r in refs]
        print(f"  {qid} ({name[:30]})")
        print(f"    -> {refs_short}")


if __name__ == "__main__":
    main()
