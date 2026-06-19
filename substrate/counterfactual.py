"""
substrate.counterfactual -- Pearl-style do() operator with Merkle audit chain.

Port of exp_counterfactual_do_operator_v1.py.

CORE IDEA:
The substrate models a causal DAG where derived facts compute from base facts. A do(X=v)
intervention OVERRIDES a base fact and recomputes all descendant derived facts. The
recomputation is captured in a Merkle hash chain that can be replayed + tampered-checked.

WHY THIS MATTERS FOR THE DEMO:
"What would have happened if OpenAI had hired Y instead of Z as CTO?" — substrate can
answer counterfactual queries WITH cryptographically auditable provenance. Frontier LLMs
cannot offer this (no separation of fact-from-deduction; no tamper-evident chain).

Validated (cycle 175): 20/20 counterfactuals correct + audit chains verify + tamper detected.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from substrate.audit import AuditChain


@dataclass
class CausalDAG:
    """A DAG of base facts + derived facts.

    base[name] = value  (input fact)
    derived[name] = (compute_fn, parent_names_list)

    compute_fn: callable that takes a dict of {parent_name: value} and returns the
    derived value. Must be deterministic.
    """
    base: dict = field(default_factory=dict)
    derived: dict = field(default_factory=dict)  # name -> (compute_fn, [parents])
    topo_order: list = field(default_factory=list)  # derived names in topological order

    def add_base(self, name: str, value) -> None:
        self.base[name] = value

    def add_derived(self, name: str, compute_fn, parents: list[str]) -> None:
        # Validate parents exist
        for p in parents:
            if p not in self.base and p not in self.derived:
                raise ValueError(f"derived node {name!r} references unknown parent {p!r}")
        self.derived[name] = (compute_fn, parents)
        if name not in self.topo_order:
            self.topo_order.append(name)

    def evaluate(self, overrides: Optional[dict] = None) -> dict:
        """Evaluate the DAG with optional do() overrides applied.

        overrides: dict of {name: value} that REPLACE the natural value (base or derived).
        Returns dict of all names -> values.
        """
        overrides = overrides or {}
        values = dict(self.base)
        values.update({k: v for k, v in overrides.items() if k in self.base})
        for name in self.topo_order:
            if name in overrides:
                values[name] = overrides[name]
                continue
            fn, parents = self.derived[name]
            parent_vals = {p: values[p] for p in parents}
            values[name] = fn(parent_vals)
        return values

    def descendants(self, root: str) -> list[str]:
        """Return derived names downstream of root (transitively)."""
        descendants = []
        for name in self.topo_order:
            _, parents = self.derived[name]
            if root in parents or any(d in parents for d in descendants):
                descendants.append(name)
        return descendants


@dataclass
class CounterfactualResult:
    intervention: dict          # {name: new_value}
    factual_values: dict        # what evaluation returns with no override
    counterfactual_values: dict # what evaluation returns with the intervention
    differences: dict           # subset of names that changed
    audit_chain: AuditChain

    @property
    def chain_root(self) -> str:
        return self.audit_chain.root


def do(
    dag: CausalDAG,
    intervention: dict,
    query_id: str = "do_query_0",
) -> CounterfactualResult:
    """Apply a Pearl-style do() intervention and emit an auditable chain.

    Args:
        dag: the causal DAG
        intervention: {name: new_value} for the do() override
        query_id: identifier for the audit chain

    Returns: CounterfactualResult with factual and counterfactual values + Merkle chain.
    """
    factual = dag.evaluate()
    counterfactual = dag.evaluate(overrides=intervention)

    chain = AuditChain(chain_id=f"cf:{query_id}")
    chain.append("intervention", {"do": {k: str(v) for k, v in intervention.items()}})
    for name in dag.topo_order:
        chain.append("recompute", {
            "name": name,
            "factual": str(factual[name]),
            "counterfactual": str(counterfactual[name]),
            "changed": factual[name] != counterfactual[name],
        })

    differences = {
        name: {"factual": factual[name], "counterfactual": counterfactual[name]}
        for name in factual
        if factual[name] != counterfactual[name]
    }

    return CounterfactualResult(
        intervention=intervention,
        factual_values=factual,
        counterfactual_values=counterfactual,
        differences=differences,
        audit_chain=chain,
    )


def _self_test():
    # Build a tiny DAG mirroring a corporate-acquisition chain
    dag = CausalDAG()
    dag.add_base("OpenAI_founded_year", 2015)
    dag.add_base("OpenAI_ceo", "Sam_Altman")
    dag.add_base("Anthropic_founded_year", 2021)
    dag.add_derived(
        "OpenAI_age",
        lambda parents: 2026 - parents["OpenAI_founded_year"],
        parents=["OpenAI_founded_year"],
    )
    dag.add_derived(
        "older_company",
        lambda parents: "OpenAI" if parents["OpenAI_age"] > (2026 - parents["Anthropic_founded_year"]) else "Anthropic",
        parents=["OpenAI_age", "Anthropic_founded_year"],
    )

    factual = dag.evaluate()
    assert factual["OpenAI_age"] == 11
    assert factual["older_company"] == "OpenAI"

    # Counterfactual: do(OpenAI_founded_year = 2023)
    result = do(dag, intervention={"OpenAI_founded_year": 2023}, query_id="test_cf")
    assert result.counterfactual_values["OpenAI_age"] == 3
    assert result.counterfactual_values["older_company"] == "Anthropic"
    assert "OpenAI_age" in result.differences
    assert "older_company" in result.differences
    assert result.audit_chain.verify(), "audit chain verifies"

    # Tamper: corrupt the chain
    result.audit_chain.steps[1].payload["counterfactual"] = "BOGUS"
    assert not result.audit_chain.verify(), "tampered chain rejected"

    print(f"[substrate.counterfactual] self-test PASS (do(founded=2023) flips older_company "
          f"OpenAI->Anthropic; chain root={result.chain_root[:12]}...)")


if __name__ == "__main__":
    _self_test()
