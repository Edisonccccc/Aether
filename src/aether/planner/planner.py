from __future__ import annotations

import uuid
from collections import deque
from typing import Any, Callable

import anthropic

from aether.models.context_graph import ContextGraph
from aether.models.plan_node import PlanNodeType, PlanTree, UniversalPlanNode

_SYSTEM_PROMPT = """\
You are an expert project planner. You break down goals into clear, executable plans.

A node is EXECUTABLE when both conditions are met:
  1. Its title starts with a single clear action verb (Create, Build, Write, Deploy, Train,
     Collect, Clean, Validate, Configure, Design, Implement, Test, etc.)
  2. It produces exactly one named artifact (a dataset, a service, a script, a report, etc.)

Node types:
  - Goal       : Top-level desired outcome
  - Capability : A reusable system capability that must be built
  - Work       : Executable or decomposable unit of work
  - Milestone  : Significant checkpoint
  - Deliverable: A concrete artifact
  - Action     : Small atomic execution step

When given a node to expand:
  - Produce 2–6 direct children only (do not recursively expand)
  - Set is_executable=true for nodes that satisfy both conditions above
  - Set depends_on to an array of sibling IDs this node must wait for (empty = parallel)
  - Set produces to the single primary artifact this work creates
  - Set constraints only for explicit constraints from the context
"""

_EXPAND_TOOL: dict[str, Any] = {
    "name": "expand_node",
    "description": "Expand a planning node into its direct children.",
    "input_schema": {
        "type": "object",
        "properties": {
            "children": {
                "type": "array",
                "minItems": 1,
                "maxItems": 8,
                "items": {
                    "type": "object",
                    "properties": {
                        "id":            {"type": "string",  "description": "Short unique ID, e.g. 'collect_data'"},
                        "title":         {"type": "string"},
                        "node_type":     {"type": "string", "enum": [t.value for t in PlanNodeType]},
                        "description":   {"type": "string"},
                        "produces":      {"type": "string", "description": "The single artifact this work produces"},
                        "depends_on":    {"type": "array",  "items": {"type": "string"}, "description": "Sibling IDs this must wait for"},
                        "constraints":   {"type": "array",  "items": {"type": "string"}},
                        "is_executable": {"type": "boolean", "description": "True if this node needs no further decomposition"},
                    },
                    "required": ["id", "title", "node_type", "produces", "depends_on", "is_executable"],
                },
            }
        },
        "required": ["children"],
    },
}


class Planner:
    def __init__(
        self,
        client: anthropic.Anthropic | None = None,
        max_depth: int = 4,
        on_expand: Callable[[str, int], None] | None = None,
    ):
        self.client = client or anthropic.Anthropic()
        self.max_depth = max_depth
        self.on_expand = on_expand  # progress callback(node_title, depth)

    def plan(self, context_graph: ContextGraph) -> PlanTree:
        """Build a complete plan tree from a context graph."""
        from aether.models.context_graph import NodeType

        goals = context_graph.get_nodes_by_type(NodeType.GOAL)

        if goals:
            goal_summary = "; ".join(g.title for g in goals)
        else:
            # Synthesise a goal from the most prominent capability/system nodes
            prominent = (
                context_graph.get_nodes_by_type(NodeType.CAPABILITY)
                or context_graph.get_nodes_by_type(NodeType.SYSTEM)
                or context_graph.nodes
            )
            goal_summary = "Build " + " and ".join(n.title for n in prominent[:3])

        root = UniversalPlanNode(
            title=goal_summary,
            node_type=PlanNodeType.GOAL,
        )
        nodes: dict[str, UniversalPlanNode] = {root.id: root}

        queue: deque[tuple[str, int]] = deque([(root.id, 0)])

        while queue:
            node_id, depth = queue.popleft()
            node = nodes[node_id]

            if self.on_expand:
                self.on_expand(node.title, depth)

            children = self._expand(node, nodes, context_graph, depth)

            for child in children:
                child.parent_id = node_id
                nodes[child.id] = child
                node.children.append(child.id)

            for child in children:
                is_exec = child.metadata.get("is_executable", False)
                if not is_exec and depth + 1 < self.max_depth:
                    queue.append((child.id, depth + 1))

        return PlanTree(root_id=root.id, nodes=nodes)

    def _expand(
        self,
        node: UniversalPlanNode,
        all_nodes: dict[str, UniversalPlanNode],
        context_graph: ContextGraph,
        depth: int,
    ) -> list[UniversalPlanNode]:
        ancestors = self._get_ancestors(node, all_nodes)
        ancestor_text = (
            " > ".join(a.title for a in ancestors) + " > " + node.title
            if ancestors
            else node.title
        )

        prompt = (
            f"{context_graph.serialize_for_prompt()}\n\n"
            f"{'=' * 40}\n\n"
            f"CURRENT PLAN HIERARCHY:\n{ancestor_text}\n\n"
            f"NODE TO EXPAND:\n"
            f"  Title: {node.title}\n"
            f"  Type:  {node.node_type.value}\n"
            + (f"  Produces: {node.produces}\n" if node.produces else "")
            + (f"  Constraints: {', '.join(node.constraints)}\n" if node.constraints else "")
            + f"\nBreak this node into 2–6 concrete direct children.\n"
            f"Depth remaining: {self.max_depth - depth - 1} levels.\n"
            f"If depth remaining is 0, all children MUST be executable."
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            tools=[_EXPAND_TOOL],
            tool_choice={"type": "tool", "name": "expand_node"},
            messages=[{"role": "user", "content": prompt}],
        )

        raw_children = self._extract_children(response)
        return self._build_nodes(raw_children, node)

    def _extract_children(self, response: anthropic.types.Message) -> list[dict[str, Any]]:
        for block in response.content:
            if block.type == "tool_use" and block.name == "expand_node":
                return block.input.get("children", [])
        raise ValueError("Planner LLM did not call expand_node tool")

    def _build_nodes(
        self, raw_children: list[dict[str, Any]], parent: UniversalPlanNode
    ) -> list[UniversalPlanNode]:
        nodes = []
        id_remap: dict[str, str] = {}  # LLM-assigned id → actual UUID

        for raw in raw_children:
            actual_id = str(uuid.uuid4())[:8]
            id_remap[raw["id"]] = actual_id

            node = UniversalPlanNode(
                id=actual_id,
                title=raw["title"],
                node_type=PlanNodeType(raw["node_type"]),
                description=raw.get("description"),
                produces=raw.get("produces"),
                constraints=raw.get("constraints", []),
                metadata={"is_executable": raw.get("is_executable", False)},
            )
            nodes.append(node)

        # Remap depends_on IDs from LLM space → actual UUIDs
        for raw, node in zip(raw_children, nodes):
            node.depends_on = [
                id_remap[dep] for dep in raw.get("depends_on", []) if dep in id_remap
            ]

        return nodes

    def _get_ancestors(
        self, node: UniversalPlanNode, all_nodes: dict[str, UniversalPlanNode]
    ) -> list[UniversalPlanNode]:
        ancestors = []
        current = node
        while current.parent_id:
            parent = all_nodes.get(current.parent_id)
            if not parent:
                break
            ancestors.insert(0, parent)
            current = parent
        return ancestors
