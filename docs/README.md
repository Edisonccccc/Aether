Aether Planner

Graph-Native Planning System

Version: v0.1

Status: Active Design

⸻

Vision

Aether is a universal planning engine.

Its purpose is to transform unstructured information into executable plans.

The system accepts arbitrary inputs:

* Design Documents
* Architecture Diagrams
* Images
* Specifications
* Notes

and converts them into:

* Structured Knowledge
* Execution Plans
* Execution Graphs

⸻

Core Principle

Everything becomes a Graph

All inputs become:

Context Graph

All plans become:

Execution Graph

⸻

V0 Goal

Build the smallest possible end-to-end system that can:

Design Doc
      ↓
Context Graph
      ↓
Planner
      ↓
Execution Graph

The objective is to validate the architecture.

Not to build a production-ready system.

⸻

Architecture Overview

Input
    ↓
Input Adapter
    ↓
Context Graph
    ↓
Planner
    ↓
Universal Plan Node Tree
    ↓
Plan Compiler
    ↓
Execution Graph

⸻

Documentation Order

Read documents in the following order:

1. System Architecture

architecture/System_Architecture.md

High-level system design.

Defines the major layers.

⸻

2. Context Graph

architecture/Context_Graph.md

Defines the universal knowledge representation.

Everything becomes a Context Graph.

⸻

3. Input Adapter Interface

architecture/Input_Adapter_Interface.md

Defines how external artifacts are converted into Context Graphs.

⸻

4. Planner Interface

architecture/Planner_Interface.md

Defines how planning operates on Context Graphs.

⸻

5. Universal Plan Node

architecture/Universal_Plan_Node.md

Defines the atomic planning primitive.

Everything in a plan becomes a Universal Plan Node.

⸻

6. Plan Compiler

architecture/Plan_Compiler.md

Defines how a Universal Plan Node tree is compiled into an Execution Graph.

⸻

7. Execution Graph Schema

architecture/Execution_Graph_Schema.md

Defines runtime plan representation.

⸻

V0 Scope

Included:

* Single Input per Planning Session (Design Doc or Image — not both simultaneously)
* Context Graph Construction
* Planner (LLM-driven)
* Universal Plan Node Tree
* Plan Compiler
* Execution Graph Generation

Excluded:

* Multi-Agent Planning
* Autonomous Execution
* Runtime Scheduling
* Graph Versioning
* Graph Databases
* Cost Optimization
* Evaluation Loops
* Knowledge Inference

⸻

V0 Design Decisions

Knowledge vs Action

Aether separates:

Knowledge

from

Action

Knowledge is represented by:

Context Graph

Action is represented by:

Execution Graph

⸻

Planning Strategy

V0 uses:

Top → Bottom Hierarchical Decomposition

Example:

Build Shopping Benchmark

↓

Dataset
Evaluator
Leaderboard

↓

Collect Data
Clean Data
Validate Data

Planning continues until nodes become executable.

⸻

Object Model

V0 uses:

1 Work
      ↓
1 Primary Object

Each Universal Plan Node owns exactly one primary output object.

⸻

Examples

The implementation should support the following workflow:

Input:
"Build a shopping benchmark platform."

↓

Context Graph

↓

Goal
├── Shopping Benchmark
Capability
├── Evaluator
├── Leaderboard
Asset
├── Product Dataset

↓

Execution Graph

↓

Create Dataset
Build Evaluator
Build Leaderboard

⸻

Implementation Guidance

The first implementation should prioritize:

1. Simplicity
2. Readability
3. Correct abstractions

Avoid:

* Premature optimization
* Complex agent systems
* Distributed execution
* Graph databases

The objective is proving the planning model.

⸻

Future Vision

Any Input
      ↓
Context Graph
      ↓
Planner
      ↓
Execution Graph
      ↓
Execution Engine
      ↓
Learning

Aether is a Graph-Native Planning System.

Everything becomes a Graph.