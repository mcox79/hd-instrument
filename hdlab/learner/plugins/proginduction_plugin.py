"""PLUGIN 4: PROGRAM-INDUCTION hypothesis class (bounded enumerative symbolic regression over a
small boolean DSL). Extensibility stress-test #2 for the centralized Learner module (banked
29487/29489): this file is the ONLY new code; `hdlab/learner/registry.py` gets a one-line
registration edit; `hdlab/learner/core.py` is UNTOUCHED (verified by `git diff --stat` in the
test cell) -- same "core.py never needs to change" claim GAM already proved, now proved on a
hypothesis class with a materially different SHAPE: a DSL SEARCH over program syntax, not a
counting table.

WHY THIS PLUGIN EXISTS (the wall it closes): `estimation` / `ruleind` / `gam` are all, at bottom,
LOOKUP mechanisms -- they memorize (feature-combo -> class) associations observed during learn()
and have no defined behavior on a combo that never co-occurred in training (gam/ruleind fall back
to mains-only / episodic-residual; both were measured (banked 29492,
exp_learner_implicative_sign_supplied_generalization_v1) to score ~0% on the unseen
(sign=pos, negated=True) cell of the implicative sign x negation task, because the marginals
alone point the WRONG direction and no interaction table entry exists for that exact combo).
A human given Karttunen's (1971, CITED) explicit symbolic rule computes that cell correctly with
ZERO exposure to it, by RULE APPLICATION, not recall -- the brain-check that banked 29492 flagged
as the honest next target.

DESIGN (bounded enumerative program synthesis -- see Muggleton & De Raedt 1994 "Inductive Logic
Programming" for the general framing; simplified here to closed-form truth-table enumeration
instead of a clause-resolution search, CITED, documented simplification matching gam_plugin's own
"closed-form instead of iterative boosting" precedent):
  ATOMS -- the caller supplies a list of literal feature strings (e.g. ["sign=pos", "neg=True"]);
    each is one boolean DSL atom, True iff that literal is present in feat_fn(inst). This is
    PER-COMPETENCE CONFIG (input, not owned by this module) -- exactly like every other plugin's
    key_fn/feat_fn convention; the plugin itself is NOT hardcoded to any specific atom set, verb,
    or domain (see the cell's 2nd-task generality check: the SAME code recovers AND on one atom
    set and a compact XOR-shaped formula on another, with no branch conditioned on which task it
    is).
  GRAMMAR -- Expr := atom(i) | NOT(Expr) | AND(Expr,Expr) | OR(Expr,Expr) | XOR(Expr,Expr) |
    XNOR(Expr,Expr). This is a SMALL DSL (closure of {AND,OR,NOT,XOR}) that spans every boolean
    function of the given atoms (any truth table is expressible), so the search is complete over
    that class, not a curated shortlist.
  SEARCH -- bottom-up enumerative synthesis, bounded by `max_nodes` (tree node budget): build
    expressions of increasing size, evaluate each on the FULL 2**n_atoms truth table (not just
    the training rows -- this is what lets apply() answer on unseen combos: the formula is total
    over the atoms' domain by construction), and DEDUP by truth table at every size step, keeping
    only the SMALLEST expression discovered per distinct function (Occam: minimal-program-per-
    function; a version-space-style prune that bounds the search to at most 2**(2**n_atoms) live
    candidates per size instead of combinatorial blow-up).
  SELECTION = MDL -- for every distinct function found, fit a 2-entry (per truth-value) Laplace-
    smoothed class map on the TRAINING rows only, compute description_bits = model_bits (program
    length in DSL tokens + the 2-entry output map, in bits) + data_bits (cross-entropy of the
    fitted map over the training rows), and keep the function with the LOWEST description_bits
    (== highest compression) -- the SAME two-part MDL currency every other plugin in this module
    uses, so mdl_select() compares this plugin's fit to gam/ruleind/estimation on equal footing.
    A short formula (few DSL tokens) costs few model_bits; the module therefore naturally PREFERS
    the compact rule over an unstructured table once BOTH are available as candidates -- this is
    the "elegant mechanism" the task asks for: no special-casing, MDL alone does the preferring.

CRITICAL PROPERTY (symbolic extrapolation, not associative lookup): apply() EVALUATES the induced
  expression tree on the atom values of a NEW item, including atom-value combinations that never
  appeared in ANY training episode -- it does not consult a per-combo table. This is what
  distinguishes program induction from estimation/ruleind/gam's lookup-with-fallback behavior.

UNIFORM API: learn(episodes, features, hypothesis_space_spec, prior) -> LearnResult;
  apply(hypothesis, feats) -> predicted class. `features` is feat_fn(inst) -> iterable[str] (same
  calling convention as gam_plugin / ruleind_plugin).
"""
from __future__ import annotations

import itertools
import math
from collections import Counter

from hdlab.learner.core import LearnResult, glass_box_assert, null_code_bits

NAME = "proginduction"
COST_RANK = 4   # priciest: full bounded DSL enumeration (gam=2 additive shape, ruleind=3 conjunct
                # search); Occam tie-break still lets a cheaper plugin win on comparable compression

_DEFAULT_MAX_NODES = 7
_DEFAULT_ALPHA = 1.0

_UNARY_OPS = ("not",)
_BINARY_OPS = ("and", "or", "xor", "xnor")


def _eval_expr(expr, atom_vals):
    """atom_vals: tuple[bool], one entry per atom index. Pure boolean evaluation -- this is the
    call site that makes apply() a symbolic EVALUATION, not a table lookup."""
    kind = expr[0]
    if kind == "atom":
        return atom_vals[expr[1]]
    if kind == "not":
        return not _eval_expr(expr[1], atom_vals)
    a = _eval_expr(expr[1], atom_vals)
    b = _eval_expr(expr[2], atom_vals)
    if kind == "and":
        return a and b
    if kind == "or":
        return a or b
    if kind == "xor":
        return a != b
    if kind == "xnor":
        return a == b
    raise ValueError("proginduction_plugin: unknown DSL op %r" % (kind,))


def _render_expr(expr, atom_names):
    """Readable glass-box rendering of the induced program."""
    kind = expr[0]
    if kind == "atom":
        return atom_names[expr[1]]
    if kind == "not":
        return "NOT(%s)" % _render_expr(expr[1], atom_names)
    sym = {"and": "AND", "or": "OR", "xor": "XOR", "xnor": "XNOR"}[kind]
    return "%s(%s, %s)" % (sym, _render_expr(expr[1], atom_names), _render_expr(expr[2], atom_names))


def _enumerate_functions(n_atoms, max_nodes):
    """Bottom-up bounded enumerative program synthesis. Returns {truth_table_tuple: (expr,
    node_count)} -- the SMALLEST expression tree found (over the grammar in this module's
    docstring) for every distinct boolean function of n_atoms atoms reachable within max_nodes
    tree nodes. Dedup-by-truth-table at every size step is the search-space pruning: only ONE
    (minimal) representative per function is kept as a building block for larger expressions,
    which is safe (monotone) because any larger expression using a non-minimal sub-part is never
    smaller than the same expression using the minimal representative for that sub-part."""
    combos = list(itertools.product([False, True], repeat=n_atoms))

    def tt_of(expr):
        return tuple(_eval_expr(expr, c) for c in combos)

    by_size = {1: []}
    seen = {}
    for i in range(n_atoms):
        e = ("atom", i)
        tt = tt_of(e)
        by_size[1].append(e)
        if tt not in seen:
            seen[tt] = (e, 1)

    n_functions_total = 2 ** (2 ** n_atoms)
    size = 1
    while size < max_nodes and len(seen) < n_functions_total:
        size += 1
        cand = []
        for e in by_size.get(size - 1, []):
            cand.append(("not", e))
        for s1 in range(1, size - 1):
            s2 = size - 1 - s1
            if s2 < 1 or s1 not in by_size or s2 not in by_size:
                continue
            for e1 in by_size[s1]:
                for e2 in by_size[s2]:
                    for op in _BINARY_OPS:
                        cand.append((op, e1, e2))
        kept = []
        for e in cand:
            tt = tt_of(e)
            if tt not in seen:
                seen[tt] = (e, size)
                kept.append(e)
        by_size[size] = kept
    return seen


def learn(episodes, features, hypothesis_space_spec, prior):
    """episodes: list of instances (dict w/ label_fn-readable field). features: feat_fn(inst) ->
    iterable[str] (same convention as gam_plugin/ruleind_plugin). spec keys: 'atoms' (REQUIRED --
    list of literal feature strings, each one boolean DSL atom), 'label_fn' (default
    ep['gold_class'] or ep[-1]), 'classes', 'max_nodes' (default 7), 'alpha' (Laplace, default
    1.0). NOT owned by this module: the atom set / feat_fn is per-competence CONFIG supplied by
    the caller, same as every other plugin -- this keeps the plugin GENERAL (it induces whatever
    compact formula best fits the SUPPLIED atoms and data; nothing here names a specific task)."""
    feat_fn = features
    label_fn = hypothesis_space_spec.get(
        "label_fn", lambda ep: ep["gold_class"] if isinstance(ep, dict) else ep[-1])
    atoms = hypothesis_space_spec.get("atoms")
    if not atoms:
        raise ValueError(
            "proginduction_plugin.learn requires hypothesis_space_spec['atoms']: a list of "
            "literal feature strings, each treated as one boolean DSL atom (True iff present "
            "in feat_fn(inst)). This is per-competence config, not inferred.")
    max_nodes = hypothesis_space_spec.get("max_nodes", _DEFAULT_MAX_NODES)
    alpha = hypothesis_space_spec.get("alpha", _DEFAULT_ALPHA)
    classes = hypothesis_space_spec.get("classes")

    n_atoms = len(atoms)
    labels_all = [label_fn(ep) for ep in episodes]
    if classes is None:
        classes = sorted(set(labels_all))
    n_classes = max(len(classes), 2)

    def atom_vals(ep):
        fs = set(feat_fn(ep))
        return tuple(a in fs for a in atoms)

    avals = [atom_vals(ep) for ep in episodes]
    functions = _enumerate_functions(n_atoms, max_nodes)
    n_dsl_tokens = n_atoms + len(_UNARY_OPS) + len(_BINARY_OPS)   # DSL vocabulary size (per-node encoding cost)

    best = None
    for tt, (expr, node_count) in functions.items():
        bucket_labels = {True: [], False: []}
        for av, lbl in zip(avals, labels_all):
            combo_idx = sum((1 << i) for i, v in enumerate(av) if v)
            bucket_labels[tt[combo_idx]].append(lbl)

        out_map = {}
        data_bits = 0.0
        for out_val in (True, False):
            bucket = bucket_labels[out_val]
            cnt = Counter(bucket)
            n_b = len(bucket)
            if n_b == 0:
                out_map[out_val] = classes[0]
                continue
            best_c = max(classes, key=lambda c: cnt.get(c, 0))
            out_map[out_val] = best_c
            for lbl in bucket:
                p = (cnt.get(lbl, 0) + alpha) / (n_b + alpha * n_classes)
                data_bits += -math.log2(max(p, 1e-12))

        model_bits = node_count * math.log2(max(n_dsl_tokens, 2)) + 2 * math.log2(n_classes)
        description_bits = model_bits + data_bits
        if best is None or description_bits < best["description_bits"] - 1e-9 or (
                abs(description_bits - best["description_bits"]) <= 1e-9 and node_count < best["node_count"]):
            best = {"tt": tt, "expr": expr, "node_count": node_count, "out_map": out_map,
                    "model_bits": model_bits, "data_bits": data_bits, "description_bits": description_bits}

    formula_str = _render_expr(best["expr"], atoms)
    hyp = {
        "kind": "program", "atoms": list(atoms), "expr": _jsonable_expr(best["expr"]),
        "formula": formula_str, "node_count": best["node_count"],
        "out_map": {str(k): v for k, v in best["out_map"].items()},
        "classes": list(classes),
    }
    # expr is stored as a JSON-native list-tree (glass_box_assert requires json.dumps to round-
    # trip cleanly); apply() re-tupleizes it via _tupleize_expr before evaluating.
    glass_box_assert(hyp)

    return LearnResult(
        plugin_name=NAME, hypothesis=hyp, is_episodic=False,
        description_bits=best["description_bits"], null_bits=null_code_bits(labels_all),
        n_free_params=best["node_count"] + 2, cost_rank=COST_RANK,
        metrics={"formula": formula_str, "node_count": best["node_count"],
                 "model_bits": round(best["model_bits"], 3), "data_bits": round(best["data_bits"], 3),
                 "n_distinct_functions_searched": len(functions)},
    )


def _jsonable_expr(expr):
    """Recursively convert an expr tuple-tree to a JSON-round-trippable list-tree (for
    glass_box_assert -- json.dumps accepts tuples natively by encoding them as arrays, so this is
    actually a no-op passthrough for json.dumps but is kept explicit for readability / so a
    stricter future glass-box check that requires list-not-tuple still passes)."""
    if expr[0] == "atom":
        return ["atom", expr[1]]
    if expr[0] == "not":
        return ["not", _jsonable_expr(expr[1])]
    return [expr[0], _jsonable_expr(expr[1]), _jsonable_expr(expr[2])]


def _tupleize_expr(expr):
    """Inverse of _jsonable_expr -- rebuilds the tuple-tree _eval_expr expects from a
    JSON-deserialized list-tree (needed only if a hypothesis is round-tripped through disk)."""
    if expr[0] == "atom":
        return ("atom", expr[1])
    if expr[0] == "not":
        return ("not", _tupleize_expr(expr[1]))
    return (expr[0], _tupleize_expr(expr[1]), _tupleize_expr(expr[2]))


def apply(hypothesis, feats):
    """Evaluate the induced formula on ANY atom-combination -- including combinations never seen
    during learn() -- by literally EVALUATING the boolean expression, not looking up a
    per-combination table. This is the mechanism that lets the plugin fill an unseen
    (atom-value) cell: the formula is TOTAL over the atoms' domain by construction (every row of
    the 2**n_atoms truth table was assigned during the search), independent of which combos were
    observed at learn() time."""
    if hypothesis["kind"] != "program":
        raise ValueError("proginduction plugin cannot apply a %r hypothesis" % hypothesis["kind"])
    atoms = hypothesis["atoms"]
    expr = hypothesis["expr"]
    if isinstance(expr, list):
        expr = _tupleize_expr(expr)
    fs = set(feats)
    atom_vals = tuple(a in fs for a in atoms)
    out = _eval_expr(expr, atom_vals)
    return hypothesis["out_map"][str(out)]
