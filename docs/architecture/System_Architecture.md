System Architecture Specification v0.1

Project: Aether Planner

Status: V0 Locked

Last Updated: June 2026

⸻

Vision

Aether is a universal planning engine.

Its purpose is to transform unstructured information into executable plans.

Users provide:

* Design Documents
* Architecture Diagrams
* Images
* Notes
* Specifications

Aether converts them into:

* Structured Knowledge
* Execution Plans
* Executable Work Graphs

⸻

Core Principle

Everything becomes a Graph

Every input eventually becomes:

Context Graph

Every plan eventually becomes:

Execution Graph

⸻

High-Level Architecture

┌─────────────────────────────┐
│          Inputs             │
├─────────────────────────────┤
│ Design Docs                 │
│ Architecture Diagrams       │
│ Images                      │
│ Notes                       │
│ Specifications              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Input Adapters         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Context Graph         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          Planner            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Universal Plan Nodes      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Plan Compiler         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Execution Graph        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Execution Engine       │
└─────────────────────────────┘

⸻

Layer 1 — Inputs

Inputs are arbitrary user-provided artifacts.

Examples:

PRD
Design Doc
Screenshot
Architecture Diagram
Meeting Notes
GitHub Repository
Slack Export

Inputs are not directly consumed by the planner.

Inputs must first be transformed.

⸻

Layer 2 — Input Adapters

Input Adapters convert raw information into structured knowledge.

Responsibility:

Raw Input
↓
Context Graph

Examples:

DesignDocAdapter

Input:

Markdown
PDF
Word

Output:

Context Graph

⸻

ImageAdapter

Input:

Architecture Diagram
Screenshot
Whiteboard

Output:

Context Graph

⸻

Layer 3 — Context Graph

The Context Graph is the universal knowledge layer.

Responsibility:

Represent Reality

The graph contains:

Goals
Assets
Actors
Systems
Capabilities
Constraints
Concepts

The Context Graph does NOT contain work.

It only contains knowledge.

⸻

Example:

Goal
 └─ Build Shopping Benchmark
Asset
 └─ Product Dataset
Capability
 ├─ Evaluator
 └─ Leaderboard

⸻

Layer 4 — Planner

The Planner converts knowledge into action.

Responsibility:

Context Graph
↓
Plan Nodes

Planner answers:

What should happen?

The planner does not execute anything.

The planner only creates plans.

⸻

Layer 5 — Universal Plan Nodes

Universal Plan Nodes are the atomic planning unit.

Everything becomes a node.

Examples:

Create Dataset
Build Evaluator
Deploy Backend
Run Experiment

All work is represented using the same schema.

⸻

Properties:

Type
Objective
Inputs
Outputs
Constraints
Children

⸻

Layer 6 — Plan Compiler

The Plan Compiler is a deterministic transformer.

Responsibility:

Universal Plan Node Tree
↓
Execution Graph

Rules:

* Only leaf nodes become Work
* Each leaf node produces one Object
* Dependencies derive from sibling ordering and Context Graph edges

The Plan Compiler contains no LLM calls.

Given the same input, it always produces the same output.

⸻

Layer 7 — Execution Graph

The Execution Graph is a DAG composed of Plan Nodes.

Example:

Create Dataset
        │
        ▼
Build Evaluator
        │
        ▼
Build Leaderboard

The graph defines:

Dependencies
Execution Order
Parallelism

⸻

Layer 8 — Execution Engine

The Execution Engine performs actual work.

V0 Scope:

Out of Scope

Future examples:

Claude Code
Cursor
OpenAI Agents
Internal Agents
Human Workers

The planner produces work.

The execution engine performs work.

⸻

Top-Down Planning

Aether uses hierarchical decomposition.

Example:

Build Shopping Benchmark

↓

Level 1

Dataset
Evaluator
Leaderboard

↓

Level 2

Dataset
├─ Collect Products
├─ Clean Data
└─ Build Schema

↓

Level 3

Clean Data
├─ Remove Duplicates
├─ Normalize Fields
└─ Validate Records

⸻

Planning continues until:

Node is Executable

⸻

V0 Planning Strategy

V0 uses:

Top → Bottom Expansion

Algorithm:

Goal
↓
Planner
↓
Universal Plan Node
↓
Expand
↓
Expand
↓
Executable Node

No optimization.

No search.

No evaluation loops.

Keep it simple.

⸻

Design Philosophy

Aether separates:

Knowledge

from

Action

⸻

Knowledge:

Context Graph

Action:

Execution Graph

⸻

This separation enables:

Multiple planners
Multiple executors
Multiple input formats

while maintaining a stable core architecture.

⸻

V0 Scope

Included:

* Design Doc Parsing
* Image Parsing
* Context Graph
* Planner
* Universal Plan Nodes
* Execution Graph

Not Included:

* Multi-Agent Planning
* Graph Versioning
* Autonomous Execution
* Cost Optimization
* Self-Improvement Loops
* Knowledge Inference

⸻

Future Vision

Future versions may support:

Everything becomes a Graph
Graph becomes Knowledge
Knowledge becomes Plans
Plans become Execution
Execution becomes Learning
Learning improves Future Plans

This creates a continuously improving planning system.

⸻

Final Architecture

Any Input
      │
      ▼
Input Adapter
      │
      ▼
Context Graph
      │
      ▼
Planner
      │
      ▼
Universal Plan Node Tree
      │
      ▼
Plan Compiler
      │
      ▼
Execution Graph
      │
      ▼
Execution Engine

Aether is fundamentally a Graph-Native Planning System.