from __future__ import annotations

import sys
import argparse
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.status import Status

from aether.adapters.registry import AdapterRegistry
from aether.planner.planner import Planner
from aether.compiler.plan_compiler import PlanCompiler
from aether.display import console, print_context_graph, print_plan_tree, print_execution_graph

load_dotenv()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="aether",
        description="Aether — Graph-Native Planning System",
    )
    parser.add_argument(
        "input",
        help="Natural-language goal, path to a document (.md/.txt), or path to an image (.png/.jpg)",
    )
    parser.add_argument(
        "--type",
        choices=["text", "document", "image"],
        default=None,
        help="Force a specific input adapter (auto-detected if omitted)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        help="Maximum plan expansion depth (default: 3)",
    )
    parser.add_argument(
        "--no-graph",
        action="store_true",
        help="Skip Context Graph display",
    )
    parser.add_argument(
        "--no-plan",
        action="store_true",
        help="Skip Plan Tree display",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    try:
        client = anthropic.Anthropic()
    except Exception as e:
        console.print(f"[bold red]Failed to initialize Anthropic client:[/] {e}")
        console.print("Set ANTHROPIC_API_KEY in your environment or .env file.")
        sys.exit(1)

    registry = AdapterRegistry(client=client)
    adapter = registry.resolve(args.input, input_type=args.type)

    # ── Step 1: Parse input into Context Graph ──────────────────────
    with Status("[cyan]Parsing input → Context Graph…[/]", console=console):
        try:
            context_graph = adapter.parse(args.input)
        except Exception as e:
            console.print(f"[bold red]Adapter error:[/] {e}")
            sys.exit(1)

    if not args.no_graph:
        print_context_graph(context_graph)

    if not context_graph.nodes:
        console.print("[bold red]No entities extracted from input. Aborting.[/]")
        sys.exit(1)

    # ── Step 2: Plan ─────────────────────────────────────────────────
    expanded: list[str] = []

    def on_expand(title: str, depth: int) -> None:
        expanded.append(title)
        console.print(f"  [dim]Expanding[/] [yellow]{title}[/] [dim](depth {depth})[/]")

    console.print()
    console.rule("[bold yellow]Planning[/]")

    planner = Planner(client=client, max_depth=args.depth, on_expand=on_expand)
    try:
        plan = planner.plan(context_graph)
    except ValueError as e:
        console.print(f"[bold red]Planner error:[/] {e}")
        sys.exit(1)

    if not args.no_plan:
        print_plan_tree(plan)

    # ── Step 3: Compile → Execution Graph ───────────────────────────
    with Status("[green]Compiling plan → Execution Graph…[/]", console=console):
        compiler = PlanCompiler()
        execution_graph = compiler.compile(plan, context_graph)

    print_execution_graph(execution_graph)

    console.print()
    console.print("[bold green]Done.[/]")


if __name__ == "__main__":
    main()
