"""Director-authored scour for USER strategic-overview synthesis.

Pulls from substrate:
- audit_lesson catalog (49 entries) -- categorized by ARC relevance
- methodology_rule catalog (45 entries) -- self-cert pattern variants + reusable patterns
- 4 PROOF_RECORDs -- formal-oracle scaffold patterns
- 47 applied-domain CERT_CHAIN_GRADE positives -- ARC 1 NARROW-scope candidates
"""
import json
import os
import collections

ROOT = "data/substrate_index"


def load_atoms_by_kind():
    out = collections.defaultdict(list)
    for p in sorted(os.listdir(ROOT)):
        fp = os.path.join(ROOT, p, "atoms.jsonl")
        if not os.path.isfile(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except Exception:
                    continue
                kind = a.get("kind", "")
                out[kind].append((p, a))
    return out


def main():
    atoms = load_atoms_by_kind()
    print("=" * 70)
    print("AUDIT_LESSON catalog scour")
    print("=" * 70)
    audit = atoms.get("audit_lesson", [])
    print(f"Total audit_lessons: {len(audit)}")
    by_status = collections.Counter()
    self_improve_lessons = []
    for p, a in audit:
        md = a.get("metadata", {}) if isinstance(a.get("metadata"), dict) else {}
        st = md.get("status", "?")
        by_status[st] += 1
        name = (a.get("name") or "")[:90]
        desc = (a.get("description") or "")[:200]
        # Filter for SELF-IMPROVEMENT relevant lessons
        text = f"{name.lower()} {desc.lower()}"
        if any(k in text for k in [
            "self", "autonomy", "auto", "deterministic", "encoded", "gate",
            "ingest", "sweep", "refresh", "consolidat", "optim", "sleep",
            "regener", "scour", "compose-don't-proliferate", "verify-the-referent",
            "negativity-bias",
        ]):
            self_improve_lessons.append((p, a))
    print(f"By status: {dict(by_status)}")
    print(f"\nSELF-IMPROVEMENT relevant lessons: {len(self_improve_lessons)}")
    for p, a in self_improve_lessons[:20]:
        name = (a.get("name") or "").strip()[:100]
        md = a.get("metadata", {})
        st = md.get("status", "?")
        print(f"  [{st:10s}] {a.get('id', '?')[:60]} :: {name}")

    print()
    print("=" * 70)
    print("METHODOLOGY_RULE catalog scour")
    print("=" * 70)
    method = atoms.get("methodology_rule", [])
    print(f"Total methodology_rules: {len(method)}")
    self_cert_rules = []
    for p, a in method:
        name = (a.get("name") or "")[:100]
        desc = (a.get("description") or "")[:200]
        text = f"{name.lower()} {desc.lower()}"
        if any(k in text for k in [
            "self-cert", "self_cert", "gate", "deterministic", "producer",
            "consumer", "attest", "additive", "non-retroactive", "structural",
            "guard",
        ]):
            self_cert_rules.append((p, a))
    print(f"\nSELF-CERT pattern methodology_rules: {len(self_cert_rules)}")
    for p, a in self_cert_rules[:25]:
        name = (a.get("name") or "").strip()[:100]
        print(f"  {a.get('id', '?')[:60]} :: {name}")

    print()
    print("=" * 70)
    print("PROOF_RECORD catalog scour (formal-oracle scaffold)")
    print("=" * 70)
    proofs = atoms.get("proof_record", [])
    print(f"Total PROOF_RECORDs: {len(proofs)}")
    for p, a in proofs:
        name = (a.get("name") or "").strip()[:100]
        md = a.get("metadata", {})
        tier = md.get("confidence_tier", "?")
        path = md.get("lean_file", md.get("path", "?"))
        thm = md.get("theorem_id", md.get("identifier", "?"))
        print(f"  [{tier}] {a.get('id', '?')[:60]}")
        print(f"    name: {name}")
        print(f"    file: {path}")
        print(f"    thm:  {thm}")

    print()
    print("=" * 70)
    print("47 APPLIED-DOMAIN CERT positives scour (ARC 1 NARROW candidates)")
    print("=" * 70)
    cert_apps = []
    for p, a in atoms.get("experiment_record", []):
        md = a.get("metadata", {}) if isinstance(a.get("metadata"), dict) else {}
        if md.get("provenance_quality") != "CERT_CHAIN_GRADE":
            continue
        if md.get("verdict") not in {"PASS", "HARD_PASS", "PARTIAL_PASS", "CONFIRMED", "POSITIVE"}:
            continue
        name = (a.get("name") or "").lower()
        if any(k in name for k in ["atis", "intent", "ner", "conll", "ontonotes",
                                     "pos tag", "fb15k", "wn18", "multihop", "audit_core",
                                     "abduction", "compositional", "decomposit", "active_inference",
                                     "dpefe", "crt", "csp", "symbolic", "drosophila",
                                     "deletion_cert", "hnsw", "retrieval", "codebook"]):
            cert_apps.append((p, a))
    print(f"Applied-domain candidates found: {len(cert_apps)}")
    print(f"\nSample for ARC 1 NARROW B-alpha (WordNet+GO over multi-hop):")
    for p, a in cert_apps[:20]:
        n = (a.get("name") or "").strip()[:90]
        md = a.get("metadata", {})
        tier = md.get("relevance_tier", "?")
        print(f"  [{tier}] {a.get('id', '?')[:55]} :: {n}")


if __name__ == "__main__":
    main()
