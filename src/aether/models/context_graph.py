from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    GOAL = "Goal"
    CAPABILITY = "Capability"
    ASSET = "Asset"
    ACTOR = "Actor"
    CONSTRAINT = "Constraint"
    SYSTEM = "System"
    CONCEPT = "Concept"


class EdgeType(str, Enum):
    DEPENDS_ON = "DependsOn"
    USES = "Uses"
    PRODUCES = "Produces"
    OWNED_BY = "OwnedBy"
    PART_OF = "PartOf"
    RELATED_TO = "RelatedTo"


class GraphNode(BaseModel):
    id: str
    type: NodeType
    title: str
    description: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str
    type: EdgeType
    source_id: str
    target_id: str


class ContextGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)

    def node_map(self) -> dict[str, GraphNode]:
        return {n.id: n for n in self.nodes}

    def add_node(self, node: GraphNode) -> None:
        self.nodes.append(node)

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)

    def get_nodes_by_type(self, node_type: NodeType) -> list[GraphNode]:
        return [n for n in self.nodes if n.type == node_type]

    def get_edges_by_type(self, edge_type: EdgeType) -> list[GraphEdge]:
        return [e for e in self.edges if e.type == edge_type]

    def get_outgoing_edges(self, node_id: str) -> list[GraphEdge]:
        return [e for e in self.edges if e.source_id == node_id]

    def get_incoming_edges(self, node_id: str) -> list[GraphEdge]:
        return [e for e in self.edges if e.target_id == node_id]

    def serialize_for_prompt(self) -> str:
        """Human-readable serialization for LLM prompts."""
        node_map = self.node_map()
        lines = ["CONTEXT GRAPH", "=" * 40, "", "Nodes:"]
        for node in self.nodes:
            desc = f" — {node.description}" if node.description else ""
            lines.append(f"  [{node.type.value}] {node.title}{desc}")

        if self.edges:
            lines.extend(["", "Relationships:"])
            for edge in self.edges:
                src = node_map.get(edge.source_id)
                tgt = node_map.get(edge.target_id)
                src_title = src.title if src else edge.source_id
                tgt_title = tgt.title if tgt else edge.target_id
                lines.append(f"  {src_title} —[{edge.type.value}]→ {tgt_title}")

        return "\n".join(lines)
