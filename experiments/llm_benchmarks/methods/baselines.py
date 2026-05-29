"""Baseline editing methods: ROME, MEMIT, AlphaEdit, MEND -- STUBS.

Each class raises NotImplementedError on initialise/apply_edit/query with a
pointer to the upstream reference implementation. Phase-2 fills these in by
either (a) shelling out to the upstream repo, or (b) re-implementing the
key-value-injection step against a hosted HF model.

References:
  ROME       Meng et al, 2022. https://arxiv.org/abs/2202.05262
             repo: https://github.com/kmeng01/rome
  MEMIT      Meng et al, 2023. https://arxiv.org/abs/2210.07229
             repo: https://github.com/kmeng01/memit
  AlphaEdit  Fang et al, 2024. https://arxiv.org/abs/2410.02355
             repo: https://github.com/jianghoucheng/AlphaEdit
  MEND       Mitchell et al, 2022. https://arxiv.org/abs/2110.11309
             repo: https://github.com/eric-mitchell/mend

ASCII-only per CLAUDE.md.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from experiments.llm_benchmarks.edit_benchmark_harness import EditMethod, EditTriple


class _BaselineStub(EditMethod):
    """Common stub body. Subclasses set `name`, `upstream_repo`, `upstream_paper`."""

    upstream_repo: str = "unset"
    upstream_paper: str = "unset"

    def initialise(self) -> None:
        # Mark initialised so the harness can record a configuration row, but
        # any actual edit/query attempt below will raise NotImplementedError.
        self._initialised = True

    def apply_edit(self, triple: EditTriple) -> Dict[str, Any]:
        raise NotImplementedError(
            f"{self.name} apply_edit is not implemented. "
            f"See upstream repo: {self.upstream_repo} ({self.upstream_paper}). "
            f"Phase-2 of notes/llm_benchmark_harness_2026-05-29.md."
        )

    def query(self, prompt: str) -> str:
        raise NotImplementedError(
            f"{self.name} query is not implemented. "
            f"See upstream repo: {self.upstream_repo}."
        )


class ROMEMethod(_BaselineStub):
    name = "rome"
    upstream_paper = "Meng et al 2022 (https://arxiv.org/abs/2202.05262)"
    upstream_repo = "https://github.com/kmeng01/rome"


class MEMITMethod(_BaselineStub):
    name = "memit"
    upstream_paper = "Meng et al 2023 (https://arxiv.org/abs/2210.07229)"
    upstream_repo = "https://github.com/kmeng01/memit"


class AlphaEditMethod(_BaselineStub):
    name = "alphaedit"
    upstream_paper = "Fang et al 2024 (https://arxiv.org/abs/2410.02355)"
    upstream_repo = "https://github.com/jianghoucheng/AlphaEdit"


class MENDMethod(_BaselineStub):
    name = "mend"
    upstream_paper = "Mitchell et al 2022 (https://arxiv.org/abs/2110.11309)"
    upstream_repo = "https://github.com/eric-mitchell/mend"
