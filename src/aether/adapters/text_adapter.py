from __future__ import annotations

import uuid
from typing import Any

import anthropic

from aether.adapters.base import InputAdapter
from aether.models.context_graph import ContextGraph, GraphNode, GraphEdge, NodeType, EdgeType

_SYSTEM_PROMPT = """\
You are an expert at analyzing text and extracting structured knowledge into a Context Graph.

Node types (use exactly these values):
- Goal: A desired outcome or objective — ALWAYS extract at least one Goal from the overall intent
- Capability: A system capability that must be built or acquired
- Asset: Something that already exists (data, systems, code, infrastructure)
- Actor: A person, team, or organization
- Constraint: A limitation, requirement, or boundary condition
- System: A software or hardware system
- Concept: Abstract domain knowledge or methodology

Edge types (use exactly these values):
- DependsOn: Source requires target to exist or be completed first
- Uses: Source actively uses target
- Produces: Source creates or generates target
- OwnedBy: Source is owned or maintained by target
- PartOf: Source is a component or sub-element of target
- RelatedTo: Generic relationship — use sparingly only when no specific type fits

Rules:
- You MUST produce at least one Goal node capturing the top-level desired outcome.
- Extract ALL meaningful entities and relationships. Be thorough.
- Node IDs must be short lowercase_snake_case strings, unique within the graph.
"""

_BUILD_GRAPH_TOOL: dict[str, Any] = {
    "name": "build_context_graph",
    "description": "Build a structured Context Graph from the analyzed text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "nodes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id":          {"type": "string"},
                        "type":        {"type": "string", "enum": [t.value for t in NodeType]},
                        "title":       {"type": "string"},
                        "description": {"type": "string"},
                    },
                    "required": ["id", "type", "title"],
                },
            },
            "edges": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type":      {"type": "string", "enum": [e.value for e in EdgeType]},
                        "source_id": {"type": "string"},
                        "target_id": {"type": "string"},
                    },
                    "required": ["type", "source_id", "target_id"],
                },
            },
        },
        "required": ["nodes", "edges"],
    },
}


class TextAdapter(InputAdapter):
    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    def parse(self, input_data: str) -> ContextGraph:
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            tools=[_BUILD_GRAPH_TOOL],
            tool_choice={"type": "tool", "name": "build_context_graph"},
            messages=[{"role": "user", "content": input_data}],
        )

        raw = self._extract_tool_result(response)
        return self._build_graph(raw)

    def _extract_tool_result(self, response: anthropic.types.Message) -> dict[str, Any]:
        for block in response.content:
            if block.type == "tool_use" and block.name == "build_context_graph":
                return block.input
        raise ValueError("LLM did not call build_context_graph tool")

    def _build_graph(self, raw: dict[str, Any]) -> ContextGraph:
        graph = ContextGraph()

        for raw_node in raw.get("nodes", []):
            graph.add_node(GraphNode(
                id=raw_node["id"],
                type=NodeType(raw_node["type"]),
                title=raw_node["title"],
                description=raw_node.get("description"),
            ))

        for raw_edge in raw.get("edges", []):
            graph.add_edge(GraphEdge(
                id=str(uuid.uuid4())[:8],
                type=EdgeType(raw_edge["type"]),
                source_id=raw_edge["source_id"],
                target_id=raw_edge["target_id"],
            ))

        return graph
