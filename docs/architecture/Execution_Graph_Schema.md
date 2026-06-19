Execution Graph Specification v0.1

Part of Aether Planner

Status: V0 Locked

Last Updated: June 2026

⸻

Purpose

Execution Graph defines the canonical representation of executable work.

It is the execution-oriented counterpart of the Context Graph.

⸻

Context Graph answers:

What exists?

Execution Graph answers:

What must happen?

⸻

Design Principles

Execution Graph should be:

* Simple
* Deterministic
* Object-centric
* Planner-generated
* Runtime-independent

Execution Graph is NOT:

* Workflow Engine
* Scheduler
* Agent Runtime

⸻

Core Philosophy

Execution is modeled as:

Work
    produces
Object

Everything meaningful in the system eventually becomes an Object.

Work exists only to transform Objects.

⸻

V0 Simplification

V0 intentionally uses:

1 Work
    →
1 Primary Object

Example:

Create Dataset
    →
Dataset

Example:

Build Evaluation Engine
    →
Evaluation Engine

Future versions may support:

1 Work
    →
N Objects

but V0 does not.

⸻

Core Entities

ExecutionGraph {
    works: Work[]
    objects: Object[]
    dependencies: Dependency[]
}

⸻

Work

A Work represents a unit of executable effort.

⸻

Schema

interface Work {
    id: string
    title: string
    description?: string
    status: WorkStatus
    primaryObjectId: string
    constraints: string[]
}

⸻

Example

{
    id: "work_001",
    title: "Create Product Dataset",
    status: "Ready",
    primaryObjectId: "obj_dataset"
}

⸻

Work Status

enum WorkStatus {
    Planned,
    Ready,
    Running,
    Blocked,
    Completed,
    Failed
}

⸻

Planned

Work exists but cannot yet execute.

⸻

Ready

All dependencies satisfied.

⸻

Running

Execution is currently in progress.

⸻

Blocked

Waiting for dependencies.

⸻

Completed

Primary object successfully produced.

⸻

Failed

Execution failed.

⸻

Object

Objects are the primary output of execution.

Execution exists to create or evolve Objects.

⸻

Schema

interface Object {
    id: string
    type: ObjectType
    title: string
    description?: string
    state: ObjectState
}

⸻

Example

{
    id: "obj_dataset",
    type: "Dataset",
    title: "Amazon Product Dataset",
    state: "Ready"
}

⸻

Object Type

V0 keeps ObjectType open-ended.

type ObjectType = string

Examples:

Dataset
Document
Codebase
API
Model
Service
Benchmark
Dashboard
Report

⸻

Object State

enum ObjectState {
    Missing,
    Draft,
    InProgress,
    Ready,
    Archived
}

⸻

Missing

Object does not yet exist.

⸻

Draft

Initial version exists.

⸻

InProgress

Object is actively being developed.

⸻

Ready

Object satisfies intended purpose.

⸻

Archived

Object is no longer active.

⸻

Dependency

Dependencies connect Work nodes.

⸻

Schema

interface Dependency {
    prerequisiteWorkId: string
    dependentWorkId: string
}

⸻

Interpretation

prerequisiteWorkId → dependentWorkId

prerequisite must complete before dependent can begin.

⸻

Example

Create Dataset
    →
Train Model

⸻

Constraint

Constraints are attached to Work.

⸻

Schema

interface Constraint {
    id: string
    description: string
}

⸻

Examples

Budget < $10,000
Must use PostgreSQL
Launch before September

⸻

Execution Readiness

A Work becomes Ready when:

All Dependencies Completed

AND

All Constraints Satisfied

⸻

Example Execution Graph

Goal:

Build Shopping Benchmark Platform

Execution Graph:

Work
Create Dataset
Object
Dataset
----------------
Work
Build Evaluator
Object
Evaluator
----------------
Work
Build Leaderboard
Object
Leaderboard

Dependencies:

Create Dataset
    →
Build Evaluator
Build Evaluator
    →
Build Leaderboard

⸻

Relationship to Planner

Planner generates:

Universal Plan Nodes

Execution Graph is derived from:

Plan Tree

Transformation:

Goal Node
    ↓
Work Nodes
    ↓
Objects

Planner owns:

Reasoning

Execution Graph owns:

Execution Structure

⸻

Relationship to Context Graph

Context Graph:

Understanding Layer

Execution Graph:

Action Layer

Example:

Input:

Build a shopping benchmark platform.

Context Graph:

Goal
Shopping Benchmark
Capability
Evaluation Engine
Asset
Product Dataset

Planner:

Generate Plan

Execution Graph:

Create Dataset
Build Evaluator
Build Leaderboard

⸻

Non Goals

Execution Graph does NOT define:

* Scheduling
* Resource Allocation
* Agent Assignment
* Notifications
* Runtime Execution
* Multi-user Coordination

These belong to future systems.

⸻

Future Extensions

Not included in V0.

Potential future additions:

Multi-object Work
Resource Graph
Agent Assignment
Scheduling
Execution History
Runtime Events
Cost Tracking
Risk Tracking

⸻

Final Principle

Context Graph represents reality.

Planner transforms reality into intent.

Execution Graph represents actionable structure.

Reality
↓
Context Graph
↓
Planner
↓
Plan Tree
↓
Execution Graph
↓
Execution Runtime

Execution Graph should remain:

* Small
* Stable
* Runtime-independent
* Easy to reason about

V0 optimizes for simplicity over completeness.