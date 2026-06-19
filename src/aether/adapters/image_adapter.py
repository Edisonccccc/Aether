from __future__ import annotations

import base64
import uuid
from pathlib import Path
from typing import Any

import anthropic

from aether.adapters.base import InputAdapter
from aether.models.context_graph import ContextGraph, GraphNode, GraphEdge, NodeType, EdgeType

_SYSTEM_PROMPT = """\
You are an expert at analyzing architecture diagrams and technical images.

Your task is to extract components, systems, actors, and their relationships from the image
and build a structured Context Graph.

Node types (use exactly these values):
- Goal: A desired outcome visible in the diagram
- Capability: A system capability shown
- Asset: Existing data stores or artifacts shown
- Actor: People, teams, or external systems shown
- Constraint: Limitations or boundaries shown
- System: Software or hardware systems shown
- Concept: Abstract concepts or groupings shown

Edge types (use exactly these values):
- DependsOn: A requires B
- Uses: A calls or uses B
- Produces: A creates B
- OwnedBy: A belongs to B
- PartOf: A is a component of B
- RelatedTo: Generic (use sparingly)

Be thorough. Capture every labeled component and every arrow or connection shown.
Node IDs must be short lowercase_snake_case strings.
"""

_BUILD_GRAPH_TOOL: dict[str, Any] = {
    "name": "build_context_graph",
    "description": "Build a Context Graph from the analyzed image.",
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
                        "confidence":  {"type": "number", "minimum": 0, "maximum": 1},
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

_SUPPORTED_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


class ImageAdapter(InputAdapter):
    """Parses architecture diagrams and screenshots into a Context Graph using vision."""

    def __init__(self, client: anthropic.Anthropic | None = None):
        self.client = client or anthropic.Anthropic()

    def parse(self, input_data: str) -> ContextGraph:
        """input_data is a file path to an image."""
        path = Path(input_data)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {input_data}")

        media_type = _SUPPORTED_MEDIA_TYPES.get(path.suffix.lower())
        if not media_type:
            raise ValueError(
                f"Unsupported image type: {path.suffix}. "
                f"Supported: {list(_SUPPORTED_MEDIA_TYPES.keys())}"
            )

        image_data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            tools=[_BUILD_GRAPH_TOOL],
            tool_choice={"type": "tool", "name": "build_context_graph"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "Analyze this architecture/system diagram and extract all "
                                "components, actors, and relationships into a Context Graph."
                            ),
                        },
                    ],
                }
            ],
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
            confidence = raw_node.get("confidence", 1.0)
            graph.add_node(GraphNode(
                id=raw_node["id"],
                type=NodeType(raw_node["type"]),
                title=raw_node["title"],
                description=raw_node.get("description"),
                metadata={"confidence": confidence} if confidence < 1.0 else {},
            ))

        for raw_edge in raw.get("edges", []):
            graph.add_edge(GraphEdge(
                id=str(uuid.uuid4())[:8],
                type=EdgeType(raw_edge["type"]),
                source_id=raw_edge["source_id"],
                target_id=raw_edge["target_id"],
            ))

        return graph
