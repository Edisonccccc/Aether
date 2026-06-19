Input Adapter Interface Specification v0.1

Part of Aether Planner

Status: V0 Locked

Last Updated: June 2026

⸻

Purpose

Input Adapters are responsible for transforming external inputs into Context Graphs.

They are the entry point of the Aether system.

⸻

Input Adapters answer:

How do we understand incoming information?

⸻

The Planner never sees raw inputs.

The Planner only sees:

Context Graph

Therefore:

Input
↓
Input Adapter
↓
Context Graph
↓
Planner

⸻

Core Philosophy

Every input source should eventually produce:

Context Graph

The Planner should not care whether the source was:

* Text
* PDF
* Design Document
* Image
* GitHub Repository
* Slack Thread

Everything becomes a Graph.

⸻

System Position

External Input
↓
Input Adapter
↓
Context Graph
↓
Planner
↓
Plan Tree

⸻

Adapter Contract

Every adapter implements the same interface.

⸻

Interface

interface InputAdapter {
    parse(input): ContextGraph
}

⸻

Input format differs.

Output format is always:

ContextGraph

⸻

Adapter Responsibilities

Adapters must:

1. Extract entities
2. Extract relationships
3. Extract goals
4. Extract constraints
5. Build Context Graph

Adapters must NOT:

* Generate plans
* Create tasks
* Create schedules
* Create execution graphs

Those belong to the Planner.

⸻

Context Graph Ownership

Adapters own:

Understanding

Planner owns:

Reasoning

⸻

Bad:

PDF
↓
Adapter
↓
Tasks

⸻

Good:

PDF
↓
Adapter
↓
Context Graph
↓
Planner
↓
Tasks

⸻

Supported Inputs (V0)

V0 supports:

Text
Document
Image

⸻

Text Adapter

Input

Natural Language

Example:

Build a shopping benchmark platform
for evaluating LLMs.

⸻

Output

Goal
Shopping Benchmark
Capability
Evaluator
Capability
Leaderboard

Represented as:

ContextGraph

⸻

Document Adapter

Input

Examples:

Design Doc
PRD
RFC
Architecture Spec

⸻

Responsibilities

Extract:

Goals
Systems
Components
Assets
Capabilities
Constraints

⸻

Example

Input:

Build a shopping benchmark platform
with evaluation engine and leaderboard.

Output:

Goal
Benchmark Platform
Capability
Evaluation Engine
Capability
Leaderboard

⸻

Image Adapter

Input

Examples:

Architecture Diagram
Workflow Diagram
System Diagram
Whiteboard Screenshot

⸻

Responsibilities

Identify:

Components
Flows
Dependencies
Actors
Systems

⸻

Example

Architecture Diagram:

Frontend
↓
API
↓
Database

Output:

Frontend
Uses
API
Uses
Database

⸻

Context Graph Construction

All adapters must eventually produce:

interface ContextGraph {
    nodes: GraphNode[]
    edges: GraphEdge[]
}

⸻

Example

{
    nodes: [
        Goal,
        Capability,
        Asset
    ],
    edges: [
        DependsOn,
        Uses,
        Produces
    ]
}

⸻

Confidence Scores

Adapters may attach confidence values.

⸻

Example

{
    title: "Leaderboard",
    confidence: 0.94
}

⸻

Purpose:

Allow future review workflows.

⸻

V0 Planner should ignore confidence.

⸻

V0 Input Constraint

V0 processes one input source per planning session.

If a user provides both a design doc and an image, run them as separate planning sessions or select one as the primary input.

⸻

Multi-Modal Inputs (Future)

Future adapters may combine multiple inputs into a single Context Graph.

Example:

Design Doc
+
Architecture Diagram

Combined into:

Unified Context Graph

⸻

Graph Merge (Future)

Future versions may support:

Graph A
+
Graph B
↓
Merged Context Graph

Not included in V0.

⸻

Adapter Registry

Adapters should be registered through a central registry.

⸻

Example

InputType
↓
Adapter
Text
    → TextAdapter
Document
    → DocumentAdapter
Image
    → ImageAdapter

⸻

Planner Independence

Planner must never know:

Which adapter produced the graph

⸻

Bad:

if image:
    special planner

⸻

Good:

Graph
↓
Planner

⸻

Error Handling

Adapters may produce partial graphs.

⸻

Example

Image recognition only finds:

Frontend
Database

Missing:

API

⸻

Still generate:

Partial Context Graph

Planner can operate on incomplete information.

⸻

V0 Non Goals

Adapters do NOT:

* Plan
* Schedule
* Execute
* Assign agents
* Estimate costs
* Manage runtime

Adapters only understand.

⸻

Future Adapters

Potential future sources:

GitHub Repository
Slack
Notion
Google Docs
Figma
Jira
Meeting Notes
Email
Database Schema
Codebase

⸻

All future adapters must implement:

Input
↓
Context Graph

Nothing else.

⸻

Design Rule

Adapters should be dumb.

Planner should be smart.

⸻

Adapters answer:

What exists?

Planner answers:

What should happen?

⸻

Final Principle

Everything becomes a Graph.

Text
↓
Graph
Document
↓
Graph
Image
↓
Graph
GitHub
↓
Graph
Slack
↓
Graph

All roads lead to:

Context Graph

Context Graph is the universal language of Aether.