Context Graph Specification v0.1

Part of Aether Planner

Status: V0 Locked

Last Updated: June 2026

⸻

Purpose

Context Graph is the universal knowledge representation of Aether.

All inputs must eventually become a Context Graph.

The Planner never consumes raw input.

The Planner only consumes Context Graphs.

⸻

System Flow:

Text
PDF
Image
Design Doc
GitHub
Slack
↓
Input Adapter
↓
Context Graph
↓
Planner
↓
Universal Plan Nodes
↓
Execution Graph

⸻

Core Philosophy

Aether follows one principle:

Everything becomes a Graph

Regardless of source format:

Design Doc
Architecture Diagram
Meeting Notes
Screenshot
Code Repository

all become:

Context Graph

⸻

Responsibilities

Context Graph answers:

What do we know?

It does NOT answer:

What should we do?

That belongs to the Planner.

⸻

Design Goals

The Context Graph must be:

* Generic
* Extensible
* Typed
* Queryable
* Source Agnostic

The graph should work equally well for:

* Product Planning
* Software Projects
* Research Projects
* Construction Projects
* Business Operations

⸻

Core Structure

A Context Graph consists of:

interface ContextGraph {
    nodes: GraphNode[]
    edges: GraphEdge[]
}

⸻

Graph Node

Every piece of knowledge is represented as a node.

interface GraphNode {
    id: string
    type: NodeType
    title: string
    description?: string
    metadata?: Record<string, any>
}

⸻

Example:

{
    id: "goal_001",
    type: "Goal",
    title: "Build Shopping Benchmark"
}

⸻

Graph Edge

Relationships between nodes.

interface GraphEdge {
    id: string
    type: EdgeType
    sourceId: string
    targetId: string
}

⸻

Example:

{
    type: "DependsOn",
    sourceId: "evaluator",
    targetId: "dataset"
}

⸻

Node Types

V0 intentionally keeps the node taxonomy small.

⸻

Goal

Desired outcome.

Example:

Build Shopping Benchmark

⸻

Capability

A capability the system must possess.

Example:

Evaluation Engine
Leaderboard
Authentication

⸻

Asset

A thing that already exists.

Example:

Dataset
Database
Code Repository

⸻

Actor

A person, team, or organization.

Example:

Engineering Team
Research Team
Customer

⸻

Constraint

A limitation or requirement.

Example:

Launch before September
Budget < $100k

⸻

System

A software or hardware system.

Example:

PostgreSQL
AWS
Kubernetes

⸻

Concept

Abstract domain knowledge.

Example:

Reinforcement Learning
Transformer Monitoring
Shopping Evaluation

⸻

Node Type Philosophy

Keep node types broad.

Bad:

DatabaseNode
EmployeeNode
MeetingNode
PRDNode

Too specific.

⸻

Good:

Asset
Actor
System
Concept

Specificity belongs in metadata.

⸻

Edge Types

V0 supports a minimal set.

⸻

DependsOn

A depends on B

Example:

Evaluator
DependsOn
Dataset

⸻

Uses

A uses B

Example:

Evaluator
Uses
PostgreSQL

⸻

Produces

A produces B

Example:

Training Pipeline
Produces
Model

⸻

OwnedBy

A owned by B

Example:

Dataset
OwnedBy
Research Team

⸻

PartOf

A is part of B

Example:

Leaderboard
PartOf
Benchmark Platform

⸻

RelatedTo

Generic fallback relationship.

Use only when no other edge type captures the relationship.

Example:

Shopping
RelatedTo
Recommendation Systems

Note: Overuse of RelatedTo weakens graph semantics. Prefer a specific edge type whenever possible.

⸻

Example Graph

Input:

Build a shopping benchmark platform.
Use an existing product dataset.
Research team owns the dataset.
Need a leaderboard and evaluator.

⸻

Generated Graph:

Goal
├── Build Shopping Benchmark
Capability
├── Evaluator
├── Leaderboard
Asset
├── Product Dataset
Actor
├── Research Team

Relationships:

Evaluator
DependsOn
Product Dataset
Leaderboard
DependsOn
Evaluator
Product Dataset
OwnedBy
Research Team

⸻

Metadata

Metadata stores details that should not affect graph structure.

⸻

Example:

{
    id: "dataset",
    type: "Asset",
    title: "Product Dataset",
    metadata: {
        size: "20M rows",
        source: "Amazon",
        updatedAt: "2026-06-01"
    }
}

⸻

Metadata should never define graph semantics.

Graph semantics belong in nodes and edges.

⸻

Source Tracking

Nodes may record origin information.

metadata: {
    source: "document",
    location: "page_12"
}

⸻

Future use cases:

* Traceability
* Explainability
* Human review

⸻

Confidence

Nodes may include confidence scores.

metadata: {
    confidence: 0.92
}

Example:

Image parser detects:
"Database"
confidence=0.92

⸻

Planner ignores confidence in V0.

Future systems may use it.

⸻

Graph Queries

The graph should support common queries.

⸻

Example:

Find goals:

Goal

⸻

Find dependencies:

DependsOn

⸻

Find everything owned by:

Research Team

⸻

Find systems used by:

Evaluator

⸻

Graph Merge

Future versions may combine graphs.

Example:

Design Doc
↓
Graph A
Architecture Diagram
↓
Graph B
↓
Merged Graph

⸻

Merged graph becomes:

Single Context Graph

⸻

Not required for V0.

⸻

Context Graph vs Execution Graph

Context Graph:

Knowledge

Execution Graph:

Work

⸻

Example:

Context Graph:

Dataset
Evaluator
Leaderboard

Execution Graph:

Create Dataset
Build Evaluator
Build Leaderboard

⸻

Context Graph describes reality.

Execution Graph describes action.

⸻

Context Graph vs Universal Plan Node

Context Graph:

What exists?

Universal Plan Node:

What should happen?

⸻

Example:

Context Graph:

Goal
Benchmark Platform
Asset
Dataset

Planner:

Create Dataset
Build Evaluator

⸻

Storage Model

The schema interface uses array form for portability:

interface ContextGraph {
    nodes: GraphNode[]
    edges: GraphEdge[]
}

At runtime, implementations should index nodes by ID for O(1) lookup:

nodes: Map<string, GraphNode>

No graph database required.

In-memory representation is sufficient.

⸻

V0 Non Goals

Not included:

* Temporal reasoning
* Versioned graphs
* Multi-user editing
* Graph diffing
* Graph merge conflict resolution
* Ontology management
* Knowledge inference

⸻

Future Extensions

Potential additions:

Graph Versioning
Graph Merge
Knowledge Inference
Semantic Search
Vector Retrieval
Graph Embeddings
Graph Database Backend

Not part of V0.

⸻

Design Rule

Input Adapters create Context Graphs.

Planners consume Context Graphs.

Execution systems never modify Context Graphs.

⸻

Final Principle

Context Graph is the universal language of Aether.

Any Input
↓
Context Graph
↓
Planner
↓
Execution

Everything becomes a Graph.

The graph becomes understanding.

Understanding becomes planning.