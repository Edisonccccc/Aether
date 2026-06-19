from __future__ import annotations

import uuid
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class PlanNodeType(str, Enum):
    GOAL = "Goal"
    CAPABILITY = "Capability"
    WORK = "Work"
    MILESTONE = "Milestone"
    DELIVERABLE = "Deliverable"
    ACTION = "Action"


class NodeStatus(str, Enum):
    PLANNED = "Planned"
    READY = "Ready"
    # Reserved for future execution engine
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    BLOCKED = "Blocked"


class UniversalPlanNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    node_type: PlanNodeType
    description: Optional[str] = None
    status: NodeStatus = NodeStatus.PLANNED
    children: list[str] = Field(default_factory=list)
    parent_id: Optional[str] = None
    depends_on: list[str] = Field(default_factory=list)
    produces: Optional[str] = None
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def is_executable(self) -> bool:
        """Leaf node that produces a named artifact."""
        return self.is_leaf() and bool(self.produces)


class PlanTree(BaseModel):
    root_id: str
    nodes: dict[str, UniversalPlanNode]

    def root(self) -> UniversalPlanNode:
        return self.nodes[self.root_id]

    def get_children(self, node_id: str) -> list[UniversalPlanNode]:
        node = self.nodes[node_id]
        return [self.nodes[c] for c in node.children if c in self.nodes]

    def get_ancestors(self, node_id: str) -> list[UniversalPlanNode]:
        ancestors = []
        current = self.nodes.get(node_id)
        while current and current.parent_id:
            parent = self.nodes.get(current.parent_id)
            if parent:
                ancestors.insert(0, parent)
            current = parent
        return ancestors

    def get_leaves(self) -> list[UniversalPlanNode]:
        return [n for n in self.nodes.values() if n.is_leaf()]

    def serialize_for_prompt(self, node_id: Optional[str] = None, indent: int = 0) -> str:
        nid = node_id or self.root_id
        node = self.nodes[nid]
        prefix = "  " * indent
        produces = f" → {node.produces}" if node.produces else ""
        lines = [f"{prefix}[{node.node_type.value}] {node.title}{produces}"]
        for child_id in node.children:
            lines.append(self.serialize_for_prompt(child_id, indent + 1))
        return "\n".join(lines)
