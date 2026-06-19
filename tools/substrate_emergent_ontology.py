"""SKUNKWORKS #3: emergent-vs-imposed ontology probe (substrate-on-its-own; standalone-first).

Question: are the substrate's IMPOSED axes (epistemic tier, authored category_int) DISCOVERABLE
from INDEPENDENT structural features, or are they curator projection? If an imposed axis aligns
with the emergent feature structure (within-class feature similarity >> between-class), it is
empirically grounded (discovered). If not, it is authored-only.

Method (deterministic, no clustering-seed sensitivity): one-hot the LESS-authored algebra fields
(domain, structure, operation_type/role, vsa_family, signatures, complexity) -- EXCLUDING the axis
being tested + about_topic (which leaks atom identity). For each imposed axis, mean cosine
similarity WITHIN label groups vs BETWEEN groups. ratio >> 1 => axis is reflected in independent
structure. Compares to a within/between of 1.0 (no structure).

Reports the coverage reality first: how much of the corpus the imposed ontology even covers.
numpy only; read-only on atoms.jsonl.
"""
import json
from collections import Counter, defaultdict
import numpy as np
from pathlib import Path

ATOMS = Path("data/substrate_index/math/atoms.jsonl")

rows = []
n_total = 0
for line in ATOMS.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.strip():
        continue
    n_total += 1
    a = json.loads(line)
    alg = a.get("algebra") or {}
    if not alg:
        continue
    rows.append({"id": a["id"], "tier": (a.get("tier") or "?").split("/")[0], "alg": alg})

print(f"=== COVERAGE REALITY (standalone honesty) ===")
print(f"atoms total: {n_total} | with algebra dict (structured core): {len(rows)} "
      f"({100*len(rows)/n_total:.1f}%)")
print(f"=> imposed 3-axis ontology is a property of the ~{len(rows)}-atom structured core, "
      f"NOT the {n_total}-atom corpus.\n")

# feature fields (independent of the axes we test); exclude about_topic (identity leak)
FEAT_FIELDS = ["domain", "structure", "operation_type", "operation_role", "vsa_family",
               "signature_input_type", "signature_output_type", "complexity_class"]

def onehot(rows, fields):
    vocab = {}
    for r in rows:
        for f in fields:
            v = r["alg"].get(f)
            if v is not None:
                vocab.setdefault((f, str(v)), len(vocab))
    X = np.zeros((len(rows), len(vocab)))
    for i, r in enumerate(rows):
        for f in fields:
            v = r["alg"].get(f)
            if v is not None:
                X[i, vocab[(f, str(v))]] = 1.0
    return X, vocab

def within_between(X, labels):
    # cosine sim matrix
    norm = np.linalg.norm(X, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    Xn = X / norm
    S = Xn @ Xn.T
    labels = np.array(labels)
    n = len(labels)
    win = bet = wn = bn = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if labels[i] == labels[j]:
                win += S[i, j]; wn += 1
            else:
                bet += S[i, j]; bn += 1
    w = win / wn if wn else 0.0
    b = bet / bn if bn else 0.0
    return w, b, (w / b if b > 0 else float("inf"))

def test_axis(axis_name, get_label, exclude_field=None):
    fields = [f for f in FEAT_FIELDS if f != exclude_field]
    labeled = [(r, get_label(r)) for r in rows if get_label(r) is not None]
    # require >=2 classes with >=2 members for a meaningful within-group
    cnt = Counter(l for _, l in labeled)
    keep = {k for k, c in cnt.items() if c >= 2}
    labeled = [(r, l) for r, l in labeled if l in keep]
    if len({l for _, l in labeled}) < 2:
        print(f"[{axis_name}] SKIP -- too few populated classes ({dict(cnt)})")
        return
    sub = [r for r, _ in labeled]
    labs = [l for _, l in labeled]
    X, vocab = onehot(sub, fields)
    w, b, ratio = within_between(X, labs)
    print(f"[{axis_name}] n={len(sub)} classes={len(set(labs))} feat_dim={len(vocab)} "
          f"| within_cos={w:.3f} between_cos={b:.3f} RATIO={ratio:.2f}")
    verdict = ("DISCOVERED (axis strongly reflected in independent features)" if ratio >= 2.0 else
               "PARTIAL (some structure)" if ratio >= 1.3 else
               "AUTHORED-ONLY (not reflected in independent structure)")
    print(f"      -> {verdict}")

print("=== EMERGENT vs IMPOSED axis alignment (within/between cosine on independent features) ===")
test_axis("epistemic_tier", lambda r: r["tier"], exclude_field=None)
test_axis("authored category_int", lambda r: r["alg"].get("category_int"), exclude_field=None)
test_axis("domain (as axis; feature-excluded)", lambda r: r["alg"].get("domain"), exclude_field="domain")
print("\nNote: tiny structured core (n~202) + sparse operation fields (~36) -> v0, low power. "
      "Deterministic (no clustering seed). Higher grounding ladder = real vectors post-rebuild.")
