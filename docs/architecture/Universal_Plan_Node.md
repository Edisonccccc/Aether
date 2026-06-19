Universal Plan Node Specification v0.1

Part of Aether Planner

Status: V0 Locked

Last Updated: June 2026

⸻

Purpose

Universal Plan Node (UPN) is the canonical planning primitive inside Aether.

Everything the planner reasons about is represented as a Universal Plan Node.

⸻

Instead of creating many planning abstractions:

Task
Epic
Goal
Milestone
Step
Action
Deliverable

Aether uses:

Universal Plan Node

Every planning entity is simply a node with different attributes.

⸻

Core Philosophy

Planning should be recursive.

A goal can contain sub-goals.

A sub-goal can contain tasks.

A task can contain actions.

The planner should not care about the level.

⸻

Example:

Build Shopping Benchmark

contains:

Create Dataset

contains:

Collect Product Data

contains:

Scrape Amazon

All four are:

Universal Plan Node

⸻

Design Principles

UPN should be:

* Recursive
* Extensible
* Planner-friendly
* Runtime-independent
* Human-readable

⸻

Schema

interface UniversalPlanNode {
    id: string
    title: string
    description?: string
    nodeType: PlanNodeType
    status: NodeStatus
    children: string[]
    parentId?: string
    dependsOn?: string[]
    produces?: string
    constraints?: string[]
    metadata?: Record<string, any>
}

⸻

Minimal Example

{
    id: "goal_001",
    title: "Build Shopping Benchmark",
    nodeType: "Goal",
    status: "Planned",
    children: [
        "task_001",
        "task_002"
    ]
}

⸻

Node Type

NodeType is semantic.

It helps the planner reason.

⸻

enum PlanNodeType {
    Goal,
    Capability,
    Work,
    Milestone,
    Deliverable,
    Action
}

⸻

Goal

Represents desired outcomes.

Example:

Build Shopping Benchmark Platform

⸻

Capability

Represents reusable system capability.

Example:

Evaluation Engine
Leaderboard Service

⸻

Work

Represents executable effort.

Example:

Create Dataset
Build Evaluator

⸻

Milestone

Represents significant checkpoints.

Example:

Dataset Ready

⸻

Deliverable

Represents artifacts.

Example:

Dataset
Benchmark Report

⸻

Action

Represents small atomic execution units.

Example:

Collect Product Data

⸻

Node Status

enum NodeStatus {
    Planned,
    Ready,
    Running,
    Completed,
    Failed,
    Blocked
}

V0 only writes Planned and Ready.

Running, Completed, Failed, and Blocked are reserved for future execution engine integration.

⸻

Recursive Structure

Universal Plan Nodes form a tree.

Example:

Goal
│
├── Work
│   ├── Action
│   └── Action
│
└── Work
    ├── Action
    └── Action

Every node can own children.

⸻

Parent Relationship

parentId?: string

Allows upward traversal.

Example:

Scrape Amazon
parent
Collect Product Data
parent
Create Dataset
parent
Build Shopping Benchmark

⸻

Child Relationship

children: string[]

Allows downward traversal.

Example:

{
    title: "Build Dataset",
    children: [
        "collect_data",
        "clean_data",
        "validate_data"
    ]
}

⸻

Sibling Dependencies

dependsOn?: string[]

References sibling node IDs that must complete before this node can begin.

Set by the Planner when expanding a parent node.

Nodes with no dependsOn can run in parallel with other independent siblings.

⸻

Example

Parent: Create Dataset
Children:
- collect_data
- write_schema
- clean_data
- validate_data

Planner marks:

collect_data:   dependsOn: []              (can start immediately)
write_schema:   dependsOn: []              (can start immediately, parallel with collect_data)
clean_data:     dependsOn: ["collect_data"] (needs data first)
validate_data:  dependsOn: ["clean_data", "write_schema"] (needs both)

Resulting execution:

collect_data ──┐
               ├─→ clean_data ──┐
write_schema ──┘                ├─→ validate_data
                                │
               ─────────────────┘

⸻

Produced Objects

Nodes may produce outputs.

⸻

Schema:

produces?: string

⸻

Example:

{
    title: "Create Dataset",
    produces: "Dataset"
}

⸻

V0 enforces:

1 Node → 1 Primary Output

Future versions may relax this to support multiple outputs.

⸻

Constraints

Nodes can define planning constraints.

⸻

Example:

constraints: [
    "Budget < $10,000",
    "Use Open Source Models"
]

⸻

Planner uses constraints during decomposition.

⸻

Metadata

Planner-specific information.

⸻

Example:

metadata: {
    priority: "high",
    complexity: "medium",
    estimatedDays: 7
}

⸻

Metadata should never affect core semantics.

Planner should remain functional even if metadata is absent.

⸻

Decomposition

The primary responsibility of the planner is:

Node
    →
Child Nodes

Example:

Build Benchmark

decomposes into:

Create Dataset
Build Evaluator
Build Leaderboard

⸻

Then:

Create Dataset

decomposes into:

Collect Data
Clean Data
Validate Data

⸻

The planner recursively expands nodes until:

Executable Work

is reached.

⸻

Leaf Nodes

A leaf node has:

children.length == 0

Leaf nodes represent:

Current execution boundary

For V0, leaf nodes are the units passed into execution planning.

⸻

Planner Expansion Algorithm

Conceptually:

Goal
    ↓
Expand
    ↓
Sub Goals
    ↓
Expand
    ↓
Work
    ↓
Expand
    ↓
Actions
    ↓
Stop

⸻

Relationship to Context Graph

Context Graph provides:

Knowledge

Planner creates:

Universal Plan Nodes

Example:

Context Graph:

Asset
Amazon Product Data
Capability
Evaluation Engine

Planner:

Goal
Build Benchmark
    ├── Create Dataset
    └── Build Evaluator

⸻

Relationship to Execution Graph

Execution Graph is derived from Universal Plan Nodes.

Transformation:

Universal Plan Node
↓
Execution Work
↓
Execution Graph

Example:

UPN
Create Dataset
↓
Work
Create Dataset
↓
Object
Dataset

⸻

Why Universal Nodes?

Without UPN:

Goal
Task
Epic
Feature
Story
Step
Action
Deliverable

Many schemas.

Many transformations.

Many edge cases.

⸻

With UPN:

Everything
    =
Universal Plan Node

The planner only learns one abstraction.

⸻

V0 Constraints

To keep implementation small:

* Tree structure only
* No DAG planning
* No cross-node references
* No scheduling
* No resources
* No agent ownership
* No runtime state

⸻

Future Extensions

Potential future additions:

Dependency Links
Graph Planning
Agent Ownership
Resource Allocation
Scheduling
Cost Estimation
Risk Analysis
Execution History
Multi-object Outputs

These are intentionally excluded from V0.

⸻

Final Principle

The Universal Plan Node is the planner’s native language.

Context Graph describes reality.

Universal Plan Nodes describe intent.

Execution Graph describes execution.

Reality
↓
Context Graph
↓
Universal Plan Nodes
↓
Execution Graph
↓
Runtime

If Context Graph is the brain’s memory,

then Universal Plan Node is the brain’s thought structure.