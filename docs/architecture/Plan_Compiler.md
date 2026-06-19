Plan Compiler Specification v0.1

Part of Aether Planner

Status: V0 Locked

Last Updated: June 2026

⸻

Purpose

The Plan Compiler transforms a Universal Plan Node tree into an Execution Graph.

It is the bridge between the Planner's reasoning output and the structure consumed by the Execution Engine.

⸻

System Position

Context Graph
↓
Planner
↓
Universal Plan Node Tree
↓
Plan Compiler          ← this component
↓
Execution Graph
↓
Execution Engine (future)

⸻

Why a Separate Component?

The Planner reasons using LLM inference.

The Plan Compiler is deterministic.

Keeping them separate means:

* The Planner stays focused on reasoning
* The compilation step is testable without LLM
* The Execution Graph schema can evolve without changing the Planner

⸻

Compiler Contract

interface PlanCompiler {
    compile(root: UniversalPlanNode, nodes: Map<string, UniversalPlanNode>): ExecutionGraph
}

Input:

* root: the root UniversalPlanNode
* nodes: all nodes indexed by ID

Output:

* ExecutionGraph

⸻

Compilation Rules

Rule 1 — Only leaf nodes become Work

A leaf node is a node with no children.

Only leaf nodes are compiled into Work entries.

Intermediate nodes (Goal, Capability, Work with children) define hierarchy.
They are not directly represented as Work in the Execution Graph.

⸻

Example

UPN Tree:

Build Shopping Benchmark (Goal)
├── Create Dataset (Work)
│   ├── Collect Data (Action)     ← leaf → Work
│   └── Clean Data (Action)       ← leaf → Work
└── Build Evaluator (Work)        ← leaf → Work

Execution Graph Work entries:

Collect Data
Clean Data
Build Evaluator

⸻

Rule 2 — Each leaf node produces one Object

The leaf node's produces field becomes the Work's primaryObjectId.

Example:

UPN leaf:
{
    title: "Collect Data",
    produces: "Raw Product Dataset"
}

Execution Work:
{
    title: "Collect Data",
    primaryObjectId: "obj_raw_product_dataset"
}

If produces is absent, the compiler derives an Object title from the node title.

Example:

"Deploy API" → Object "API"

⸻

Rule 3 — Within-branch dependencies derive from dependsOn

Each leaf node's dependsOn field names sibling node IDs it must wait for.

The compiler creates one Dependency per entry.

Nodes with empty dependsOn have no intra-branch blockers and may execute in parallel.

Example:

Planner expands Create Dataset into:

collect_data    dependsOn: []
write_schema    dependsOn: []
clean_data      dependsOn: ["collect_data"]
validate_data   dependsOn: ["clean_data", "write_schema"]

Compiled dependencies:

collect_data → clean_data
write_schema → validate_data
clean_data   → validate_data

collect_data and write_schema start immediately in parallel.

⸻

Rule 4 — Cross-branch dependencies derive from Context Graph edges

If the Context Graph contains a DependsOn edge between two entities, and those entities map to Work nodes in the Execution Graph, a Dependency is created.

Example:

Context Graph:

Evaluator
DependsOn
Dataset

Compilation result:

Create Dataset → Build Evaluator

The compiler must receive the originating Context Graph to apply this rule.

⸻

Updated Contract

interface PlanCompiler {
    compile(
        root: UniversalPlanNode,
        nodes: Map<string, UniversalPlanNode>,
        contextGraph: ContextGraph
    ): ExecutionGraph
}

⸻

Initial Work Status

All compiled Work nodes start as:

Planned

The compiler then sets nodes with no unmet dependencies to:

Ready

⸻

Example: Full Compilation

UPN Tree:

Build Shopping Benchmark
├── Create Dataset
│   ├── Collect Data   (produces: "Raw Dataset",   dependsOn: [])
│   ├── Write Schema   (produces: "Schema",         dependsOn: [])
│   └── Clean Data     (produces: "Clean Dataset",  dependsOn: ["collect_data", "write_schema"])
└── Build Evaluator    (produces: "Evaluator",      dependsOn: [])

Context Graph Edge:

Evaluator DependsOn Dataset

⸻

Execution Graph output:

Works:

Collect Data    → obj_raw_dataset    (status: Ready)
Write Schema    → obj_schema         (status: Ready)
Clean Data      → obj_clean_dataset  (status: Planned)
Build Evaluator → obj_evaluator      (status: Planned)

Objects:

obj_raw_dataset    (state: Missing)
obj_schema         (state: Missing)
obj_clean_dataset  (state: Missing)
obj_evaluator      (state: Missing)

Dependencies:

Collect Data → Clean Data          (from dependsOn)
Write Schema → Clean Data          (from dependsOn)
Clean Data   → Build Evaluator     (from Context Graph: Evaluator DependsOn Dataset)

Collect Data and Write Schema execute in parallel.

⸻

V0 Non Goals

Plan Compiler does NOT:

* Execute work
* Schedule work
* Assign agents
* Estimate cost
* Handle partial replanning

These belong to future systems.

⸻

Future Extensions

Potential future additions:

Incremental recompilation
Partial plan updates
Cost graph generation
Resource graph generation
Multi-object Work support

Not included in V0.

⸻

Final Principle

The Planner reasons.

The Plan Compiler translates.

The Execution Engine acts.

Universal Plan Node Tree
↓
Plan Compiler
↓
Execution Graph

Compilation is deterministic.

Given the same UPN tree and Context Graph, the Plan Compiler always produces the same Execution Graph.
