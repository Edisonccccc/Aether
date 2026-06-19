from __future__ import annotations

import re
import uuid

from aether.models.context_graph import ContextGraph, EdgeType
from aether.models.execution_graph import (
    Dependency,
    ExecutionGraph,
    ExecutionObject,
    ObjectState,
    Work,
    WorkStatus,
)
from aether.models.plan_node import PlanTree, UniversalPlanNode

_ACTION_VERBS = re.compile(
    r"^(Create|Build|Write|Deploy|Train|Collect|Clean|Validate|Configure|"
    r"Design|Implement|Test|Generate|Setup|Develop|Analyze|Extract|Process|"
    r"Define|Document|Migrate|Refactor|Integrate|Publish|Run|Evaluate)\s+",
    re.IGNORECASE,
)


class PlanCompiler:
    """Deterministic transformer: PlanTree × ContextGraph → ExecutionGraph."""

    def compile(self, plan: PlanTree, context_graph: ContextGraph) -> ExecutionGraph:
        leaves = plan.get_leaves()
        graph = ExecutionGraph()

        # Rule 1 + 2: each leaf → Work + Object
        leaf_to_work: dict[str, Work] = {}
        for leaf in leaves:
            obj = self._make_object(leaf)
            work = Work(
                id=str(uuid.uuid4())[:8],
                title=leaf.title,
                primary_object_id=obj.id,
                description=leaf.description,
                constraints=leaf.constraints,
            )
            graph.objects.append(obj)
            graph.works.append(work)
            leaf_to_work[leaf.id] = work

        # Rule 3: within-branch dependencies from depends_on
        for leaf in leaves:
            work = leaf_to_work[leaf.id]
            for sibling_id in leaf.depends_on:
                if sibling_id in leaf_to_work:
                    graph.dependencies.append(Dependency(
                        prerequisite_work_id=leaf_to_work[sibling_id].id,
                        dependent_work_id=work.id,
                    ))

        # Rule 4: cross-branch deps from Context Graph DependsOn edges
        obj_map = graph.object_map()
        for edge in context_graph.get_edges_by_type(EdgeType.DEPENDS_ON):
            src_node = context_graph.node_map().get(edge.source_id)
            tgt_node = context_graph.node_map().get(edge.target_id)
            if not src_node or not tgt_node:
                continue

            prereq_work = self._find_work_for_title(tgt_node.title, graph.works)
            dependent_work = self._find_work_for_title(src_node.title, graph.works)

            if prereq_work and dependent_work and prereq_work.id != dependent_work.id:
                dep = Dependency(
                    prerequisite_work_id=prereq_work.id,
                    dependent_work_id=dependent_work.id,
                )
                if not self._dependency_exists(graph, dep):
                    graph.dependencies.append(dep)

        # Set initial statuses: Ready if no prerequisites, Planned otherwise
        prereq_ids = {d.dependent_work_id for d in graph.dependencies}
        for work in graph.works:
            if work.id not in prereq_ids:
                work.status = WorkStatus.READY

        return graph

    # ──────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────

    def _make_object(self, node: UniversalPlanNode) -> ExecutionObject:
        title = node.produces or self._derive_object_title(node.title)
        obj_id = "obj_" + re.sub(r"\W+", "_", title.lower()).strip("_")
        return ExecutionObject(
            id=obj_id,
            type=self._infer_object_type(title),
            title=title,
            state=ObjectState.MISSING,
        )

    def _derive_object_title(self, node_title: str) -> str:
        """Strip leading action verb to get the artifact name."""
        match = _ACTION_VERBS.match(node_title)
        if match:
            return node_title[match.end():]
        return node_title

    def _infer_object_type(self, title: str) -> str:
        """Heuristic object type inference from artifact title."""
        lower = title.lower()
        type_keywords = {
            "Dataset":   ["dataset", "data", "corpus"],
            "Model":     ["model", "checkpoint", "weights"],
            "API":       ["api", "endpoint", "service", "server"],
            "Report":    ["report", "summary", "analysis", "benchmark"],
            "Codebase":  ["codebase", "library", "package", "module"],
            "Dashboard": ["dashboard", "leaderboard", "ui", "frontend"],
            "Document":  ["document", "spec", "schema", "config"],
            "Pipeline":  ["pipeline", "workflow", "script"],
        }
        for obj_type, keywords in type_keywords.items():
            if any(kw in lower for kw in keywords):
                return obj_type
        return "Artifact"

    def _find_work_for_title(self, entity_title: str, works: list[Work]) -> Work | None:
        """Fuzzy match entity title to a Work node via substring containment."""
        entity_lower = entity_title.lower()
        for work in works:
            work_lower = work.title.lower()
            if entity_lower in work_lower or work_lower in entity_lower:
                return work
        # Try matching against the primary object title
        for work in works:
            if hasattr(work, "_object_title"):
                obj_lower = work._object_title.lower()  # type: ignore[attr-defined]
                if entity_lower in obj_lower or obj_lower in entity_lower:
                    return work
        return None

    def _dependency_exists(self, graph: ExecutionGraph, candidate: Dependency) -> bool:
        return any(
            d.prerequisite_work_id == candidate.prerequisite_work_id
            and d.dependent_work_id == candidate.dependent_work_id
            for d in graph.dependencies
        )
