from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich import box

from aether.models.context_graph import ContextGraph, NodeType
from aether.models.execution_graph import ExecutionGraph, WorkStatus
from aether.models.plan_node import PlanTree

console = Console()

_NODE_TYPE_COLORS = {
    NodeType.GOAL:       "bold cyan",
    NodeType.CAPABILITY: "bold yellow",
    NodeType.ASSET:      "bold green",
    NodeType.ACTOR:      "bold magenta",
    NodeType.CONSTRAINT: "bold red",
    NodeType.SYSTEM:     "bold blue",
    NodeType.CONCEPT:    "dim white",
}

_STATUS_COLORS = {
    WorkStatus.READY:     "bold green",
    WorkStatus.PLANNED:   "yellow",
    WorkStatus.RUNNING:   "bold blue",
    WorkStatus.BLOCKED:   "bold red",
    WorkStatus.COMPLETED: "dim green",
    WorkStatus.FAILED:    "bold red",
}


def print_context_graph(graph: ContextGraph) -> None:
    console.print()
    console.rule("[bold cyan]Context Graph[/]")

    node_table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    node_table.add_column("Type", style="dim", width=14)
    node_table.add_column("Title")
    node_table.add_column("Description", style="dim")

    for node in graph.nodes:
        color = _NODE_TYPE_COLORS.get(node.type, "white")
        node_table.add_row(
            f"[{color}]{node.type.value}[/]",
            node.title,
            node.description or "",
        )

    console.print(node_table)

    if graph.edges:
        edge_table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        edge_table.add_column("From")
        edge_table.add_column("Relationship", style="dim")
        edge_table.add_column("To")

        node_map = graph.node_map()
        for edge in graph.edges:
            src = node_map.get(edge.source_id)
            tgt = node_map.get(edge.target_id)
            edge_table.add_row(
                src.title if src else edge.source_id,
                f"[cyan]─[{edge.type.value}]→[/]",
                tgt.title if tgt else edge.target_id,
            )

        console.print(edge_table)


def print_plan_tree(plan: PlanTree) -> None:
    console.print()
    console.rule("[bold yellow]Plan Tree[/]")

    def add_branch(tree: Tree, node_id: str) -> None:
        node = plan.nodes.get(node_id)
        if not node:
            return
        produces = f" [dim]→ {node.produces}[/]" if node.produces else ""
        dep_note = (
            f" [dim](after: {', '.join(plan.nodes[d].title for d in node.depends_on if d in plan.nodes)})[/]"
            if node.depends_on
            else ""
        )
        label = f"[yellow]{node.node_type.value}[/] {node.title}{produces}{dep_note}"
        branch = tree.add(label)
        for child_id in node.children:
            add_branch(branch, child_id)

    root = plan.root()
    rich_tree = Tree(f"[bold cyan]{root.title}[/]")
    for child_id in root.children:
        add_branch(rich_tree, child_id)

    console.print(rich_tree)
    console.print(f"  [dim]Total nodes: {len(plan.nodes)}  |  Leaf nodes: {len(plan.get_leaves())}[/]")


def print_execution_graph(graph: ExecutionGraph) -> None:
    console.print()
    console.rule("[bold green]Execution Graph[/]")

    work_map = graph.work_map()
    prereq_map: dict[str, list[str]] = {w.id: [] for w in graph.works}
    for dep in graph.dependencies:
        prereq_map[dep.dependent_work_id].append(dep.prerequisite_work_id)

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
    table.add_column("Work",    min_width=28)
    table.add_column("Produces", min_width=20)
    table.add_column("Status",   width=10)
    table.add_column("Waits For")

    obj_map = graph.object_map()
    for work in graph.works:
        obj = obj_map.get(work.primary_object_id)
        obj_title = obj.title if obj else work.primary_object_id
        color = _STATUS_COLORS.get(work.status, "white")
        prereqs = [work_map[pid].title for pid in prereq_map[work.id] if pid in work_map]
        table.add_row(
            work.title,
            obj_title,
            f"[{color}]{work.status.value}[/]",
            ", ".join(prereqs) if prereqs else "[dim]—[/]",
        )

    console.print(table)
    console.print(
        f"  [dim]Works: {len(graph.works)}  |  "
        f"Ready: {len(graph.get_ready_works())}  |  "
        f"Dependencies: {len(graph.dependencies)}[/]"
    )
