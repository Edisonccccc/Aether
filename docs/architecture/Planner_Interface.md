Planner Interface Specification v0.1

Part of Aether Planner

Status: V0 Locked

Last Updated: June 2026

⸻

Purpose

Planner is responsible for transforming understanding into executable intent.

The Planner does not understand raw user inputs.

The Planner only operates on Context Graphs.

⸻

Planner is the bridge between:

Context Graph

and

Universal Plan Node Tree

⸻

Core Responsibility

Planner answers a single question:

Given what we know,
what should be done?

⸻

Input:

Context Graph

Output:

Universal Plan Node Tree

⸻

System Position

User Input
↓
Input Adapter
↓
Context Graph
↓
Planner
↓
Universal Plan Node Tree
↓
Execution Graph
↓
Execution Runtime (future)

Planner never receives:

* Raw Text
* Raw Images
* Raw PDFs
* Raw Design Docs

Those belong to Input Adapters.

⸻

Planner Contract

Input

interface PlannerInput {
    contextGraph: ContextGraph
}

⸻

Output

interface PlannerOutput {
    rootNode: UniversalPlanNode
}

⸻

Planner Responsibilities

Planner must:

1. Identify goals
2. Generate execution plans
3. Generate hierarchy
4. Generate deliverables
5. Generate dependencies (including sibling ordering within each expansion)
6. Generate constraints

Planner must NOT:

* Execute work
* Schedule work
* Assign agents
* Estimate costs
* Manage runtime state

⸻

Planning Philosophy

Planning is recursive decomposition.

⸻

Example

Goal:

Build Shopping Benchmark

Planner generates:

Build Shopping Benchmark
├── Create Dataset
├── Build Evaluator
└── Build Leaderboard

⸻

Then:

Create Dataset

can be expanded into:

Create Dataset
├── Collect Data
├── Clean Data
└── Validate Data

⸻

Planner repeatedly performs:

Node
↓
Expansion
↓
Child Nodes

⸻

Top-Down Planning

V0 uses strict top-down planning.

⸻

Planner first creates:

Goal

Then:

Major Work Streams

Then:

Work

Then:

Actions

⸻

Example

Goal
Build Shopping Benchmark
↓
Work
Create Dataset
Build Evaluator
Build Leaderboard
↓
Actions
Collect Data
Clean Data
Validate Data

⸻

Bottom-up planning is explicitly excluded from V0.

⸻

Expansion API

Planner exposes a single operation:

expand(node)

⸻

Input:

UniversalPlanNode

Output:

UniversalPlanNode[]

Each returned node must include a dependsOn field indicating which sibling IDs it depends on.

Nodes with no dependencies get an empty dependsOn, signaling they can run in parallel.

⸻

Example

Input:

Build Dataset

Output:

Collect Data      dependsOn: []
Write Schema      dependsOn: []
Clean Data        dependsOn: ["collect_data"]
Validate Data     dependsOn: ["clean_data", "write_schema"]

The Planner determines ordering based on logical data flow, not positional order.

⸻

Planning Levels

Planner operates across levels.

⸻

Level 0

Goal

⸻

Level 1

Capability
Work Stream

⸻

Level 2

Work

⸻

Level 3

Action

⸻

Planner should stop expanding once actionable work is reached.

⸻

Stopping Criteria

Expansion stops when:

Node is directly executable

⸻

Examples

Stop:

Write Evaluation Script

Stop:

Deploy API Service

⸻

Do Not Stop:

Build Evaluation Platform

Too large.

Requires decomposition.

⸻

Deliverable Generation

Every Work node should produce a deliverable.

⸻

Example

Create Dataset
↓
Dataset

⸻

Example

Build Evaluator
↓
Evaluation Engine

⸻

Planner should always ask:

What object will exist
after this work completes?

⸻

Dependency Generation

Planner is responsible for identifying ordering constraints.

⸻

Example

Create Dataset
↓
Build Evaluator

Dependency:

Evaluator depends on Dataset

⸻

Dependencies should be minimal.

Avoid unnecessary ordering.

⸻

Bad:

Everything depends on everything

⸻

Good:

Only true blockers create dependencies

⸻

Constraint Generation

Planner may attach constraints to nodes.

⸻

Examples

Must use PostgreSQL
Budget < $10,000
Launch before September

⸻

Constraints should only be generated if explicitly present in context.

Planner should avoid inventing constraints.

⸻

Planner State

Planner is stateless.

⸻

Input:

Context Graph

Output:

Plan Tree

No internal memory required.

⸻

Future versions may support:

Planning History
Feedback Loops
Execution Signals

but V0 does not.

⸻

Planner Modes

V0 supports two modes.

⸻

Create Plan

Input:

Context Graph

Output:

New Plan Tree

⸻

Expand Node

Input:

Existing Plan Node

Output:

Additional Child Nodes

⸻

Example

User:

Expand Create Dataset

Planner:

Collect Data
Clean Data
Validate Data

⸻

Planner and Context Graph

Planner consumes Context Graph.

⸻

Example

Context Graph:

Goal
Shopping Benchmark
Asset
Product Dataset
Capability
Evaluation Engine

Planner Output:

Build Benchmark
├── Create Dataset
├── Build Evaluator
└── Build Leaderboard

⸻

Planner and Universal Plan Nodes

Planner’s native output is:

Universal Plan Node

Planner never outputs:

Execution Graph

Execution Graph is generated later.

⸻

Transformation:

Context Graph
↓
Planner
↓
Universal Plan Nodes
↓
Execution Graph

⸻

Planner Quality Criteria

A good plan should be:

* Complete
* Minimal
* Understandable
* Expandable
* Executable

⸻

Bad Plan:

Build Everything

Too vague.

⸻

Bad Plan:

Create 300 Tasks

Too detailed.

⸻

Good Plan:

Clear hierarchy
Clear ownership boundaries
Expandable

⸻

V0 Implementation

V0 implements the Planner using an LLM.

⸻

plan(contextGraph)

Serializes the full Context Graph (nodes and edges) into the LLM system prompt.

Asks the LLM to produce a root UniversalPlanNode with immediate children.

Does not recursively expand at this stage.

⸻

expand(node, contextGraph)

Passes to the LLM:

* The full Context Graph (for grounding)
* The node being expanded
* The node's ancestors (for hierarchy context)

Asks the LLM to produce direct child nodes only.

⸻

Stopping Criterion

A node is considered directly executable when it satisfies both conditions:

1. It contains a single clear action verb (Create, Build, Write, Deploy, etc.)
2. It produces exactly one named artifact

Examples of executable nodes:

Write Evaluation Script → Evaluation Script
Deploy API Service → API Service

Examples of non-executable nodes:

Build Evaluation Platform (too broad — no single artifact)
Set Up Everything (no clear verb or artifact)

Expansion stops when a node meets both conditions.

⸻

Constraint Propagation

When expanding a node, constraints from parent nodes are included in the LLM prompt.

The LLM must respect constraints when generating children.

Example:

Parent constraint:
Budget < $10,000

Children must not propose work that violates this constraint.

⸻

V0 Non Goals

Planner does NOT perform:

* Scheduling
* Resource Planning
* Cost Estimation
* Agent Selection
* Runtime Orchestration
* Multi-user Coordination

These belong to future systems.

⸻

Future Extensions

Potential future additions:

Feedback Driven Planning
Execution Aware Planning
Risk Planning
Resource Planning
Agent Planning
Dynamic Replanning

Not included in V0.

⸻

Final Principle

Context Graph describes reality.

Planner transforms reality into intent.

Universal Plan Nodes describe the plan.

Reality
↓
Context Graph
↓
Planner
↓
Universal Plan Node Tree
↓
Execution Graph
↓
Runtime

The Planner is the reasoning engine that turns understanding into action.