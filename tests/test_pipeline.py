"""
End-to-end pipeline test with mocked LLM responses.
Run: python3 -m pytest tests/ -v
   or: python3 tests/test_pipeline.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aether.models.context_graph import ContextGraph, EdgeType, GraphEdge, GraphNode, NodeType
from aether.models.execution_graph import WorkStatus
from aether.models.plan_node import PlanNodeType


# ── Fixture helpers ──────────────────────────────────────────────────────────

def _make_tool_use_block(name: str, input_data: dict) -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.name = name
    block.input = input_data
    return block


def _make_message(*blocks) -> MagicMock:
    msg = MagicMock()
    msg.content = list(blocks)
    return msg


# ── Tests ────────────────────────────────────────────────────────────────────

def test_context_graph_serialization():
    graph = ContextGraph()
    graph.add_node(GraphNode(id="g1", type=NodeType.GOAL, title="Build Platform"))
    graph.add_node(GraphNode(id="a1", type=NodeType.ASSET, title="Product Dataset"))
    graph.add_edge(GraphEdge(id="e1", type=EdgeType.DEPENDS_ON, source_id="g1", target_id="a1"))

    text = graph.serialize_for_prompt()
    assert "Build Platform" in text
    assert "Product Dataset" in text
    assert "DependsOn" in text
    print("✓ ContextGraph serialization")


def test_text_adapter_parses_graph():
    from aether.adapters.text_adapter import TextAdapter

    mock_response = _make_message(_make_tool_use_block("build_context_graph", {
        "nodes": [
            {"id": "goal_01", "type": "Goal", "title": "Build Shopping Benchmark"},
            {"id": "asset_01", "type": "Asset", "title": "Product Dataset"},
            {"id": "cap_01", "type": "Capability", "title": "Evaluation Engine"},
            {"id": "actor_01", "type": "Actor", "title": "Research Team"},
        ],
        "edges": [
            {"type": "OwnedBy", "source_id": "asset_01", "target_id": "actor_01"},
            {"type": "DependsOn", "source_id": "cap_01", "target_id": "asset_01"},
        ],
    }))

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    adapter = TextAdapter(client=mock_client)
    graph = adapter.parse("Build a shopping benchmark platform.")

    assert len(graph.nodes) == 4
    assert len(graph.edges) == 2
    assert graph.get_nodes_by_type(NodeType.GOAL)[0].title == "Build Shopping Benchmark"
    assert graph.get_edges_by_type(EdgeType.DEPENDS_ON)[0].source_id == "cap_01"
    print("✓ TextAdapter → ContextGraph")


def test_planner_builds_tree():
    from aether.planner.planner import Planner

    # First expand call: root → 3 children
    first_expand = _make_message(_make_tool_use_block("expand_node", {
        "children": [
            {
                "id": "c1", "title": "Create Dataset", "node_type": "Work",
                "produces": "Product Dataset", "depends_on": [], "constraints": [],
                "is_executable": False,
            },
            {
                "id": "c2", "title": "Build Evaluator", "node_type": "Work",
                "produces": "Evaluation Engine", "depends_on": ["c1"], "constraints": [],
                "is_executable": False,
            },
            {
                "id": "c3", "title": "Build Leaderboard", "node_type": "Work",
                "produces": "Leaderboard", "depends_on": ["c2"], "constraints": [],
                "is_executable": False,
            },
        ]
    }))

    # Second/third/fourth expand calls: each child → executable leaf
    def make_leaf_response(title: str, produces: str, dep_id: str | None = None):
        return _make_message(_make_tool_use_block("expand_node", {
            "children": [
                {
                    "id": "leaf_a", "title": f"Collect {title} Data", "node_type": "Action",
                    "produces": f"Raw {title}", "depends_on": [], "constraints": [],
                    "is_executable": True,
                },
                {
                    "id": "leaf_b", "title": f"Process {title}", "node_type": "Action",
                    "produces": produces, "depends_on": ["leaf_a"], "constraints": [],
                    "is_executable": True,
                },
            ]
        }))

    responses = [
        first_expand,
        make_leaf_response("Dataset", "Clean Dataset"),
        make_leaf_response("Evaluator", "Evaluation Engine"),
        make_leaf_response("Leaderboard", "Leaderboard"),
    ]

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = responses

    graph = ContextGraph()
    graph.add_node(GraphNode(id="g1", type=NodeType.GOAL, title="Build Shopping Benchmark"))

    planner = Planner(client=mock_client, max_depth=2)
    plan = planner.plan(graph)

    root = plan.root()
    assert root.node_type == PlanNodeType.GOAL
    assert len(root.children) == 3

    leaves = plan.get_leaves()
    assert len(leaves) == 6  # 2 leaves per 3 Work nodes
    print(f"✓ Planner built tree: {len(plan.nodes)} nodes, {len(leaves)} leaves")


def test_plan_compiler_produces_execution_graph():
    from aether.compiler.plan_compiler import PlanCompiler
    from aether.models.plan_node import PlanTree, UniversalPlanNode

    # Build a minimal PlanTree manually
    root = UniversalPlanNode(id="root", title="Build Platform", node_type=PlanNodeType.GOAL)
    leaf_a = UniversalPlanNode(
        id="leaf_a", title="Collect Data", node_type=PlanNodeType.ACTION,
        produces="Raw Dataset", depends_on=[], parent_id="root",
    )
    leaf_b = UniversalPlanNode(
        id="leaf_b", title="Build Evaluator", node_type=PlanNodeType.WORK,
        produces="Evaluator", depends_on=["leaf_a"], parent_id="root",
    )
    root.children = ["leaf_a", "leaf_b"]

    plan = PlanTree(root_id="root", nodes={"root": root, "leaf_a": leaf_a, "leaf_b": leaf_b})

    context_graph = ContextGraph()
    context_graph.add_node(GraphNode(id="cap", type=NodeType.CAPABILITY, title="Evaluator"))
    context_graph.add_node(GraphNode(id="ast", type=NodeType.ASSET, title="Dataset"))
    context_graph.add_edge(GraphEdge(
        id="e1", type=EdgeType.DEPENDS_ON, source_id="cap", target_id="ast"
    ))

    compiler = PlanCompiler()
    exec_graph = compiler.compile(plan, context_graph)

    assert len(exec_graph.works) == 2
    assert len(exec_graph.objects) == 2

    work_map = exec_graph.work_map()
    collect_work = next(w for w in exec_graph.works if "Collect" in w.title)
    eval_work = next(w for w in exec_graph.works if "Evaluator" in w.title)

    # collect_data has no prereqs → Ready
    assert collect_work.status == WorkStatus.READY
    # build_evaluator depends on collect_data → Planned
    assert eval_work.status == WorkStatus.PLANNED

    # Dependency exists
    assert len(exec_graph.dependencies) >= 1
    dep = exec_graph.dependencies[0]
    assert dep.prerequisite_work_id == collect_work.id
    assert dep.dependent_work_id == eval_work.id

    print(f"✓ PlanCompiler: {len(exec_graph.works)} works, {len(exec_graph.dependencies)} deps")
    print(f"  Ready: {[w.title for w in exec_graph.get_ready_works()]}")


def test_display_does_not_crash():
    """Smoke test for the display layer."""
    from aether.display import print_context_graph, print_plan_tree, print_execution_graph
    from aether.models.plan_node import PlanTree, UniversalPlanNode
    from aether.compiler.plan_compiler import PlanCompiler

    graph = ContextGraph()
    graph.add_node(GraphNode(id="g", type=NodeType.GOAL, title="Test Goal"))

    root = UniversalPlanNode(id="r", title="Test Goal", node_type=PlanNodeType.GOAL)
    leaf = UniversalPlanNode(
        id="l", title="Build Thing", node_type=PlanNodeType.WORK,
        produces="Thing", parent_id="r",
    )
    root.children = ["l"]
    plan = PlanTree(root_id="r", nodes={"r": root, "l": leaf})

    exec_graph = PlanCompiler().compile(plan, graph)

    print_context_graph(graph)
    print_plan_tree(plan)
    print_execution_graph(exec_graph)
    print("✓ Display layer rendered without errors")


if __name__ == "__main__":
    tests = [
        test_context_graph_serialization,
        test_text_adapter_parses_graph,
        test_planner_builds_tree,
        test_plan_compiler_produces_execution_graph,
        test_display_does_not_crash,
    ]
    failures = []
    for t in tests:
        try:
            t()
        except Exception as e:
            import traceback
            print(f"✗ {t.__name__}: {e}")
            traceback.print_exc()
            failures.append(t.__name__)

    print()
    if failures:
        print(f"FAILED: {failures}")
        sys.exit(1)
    else:
        print(f"All {len(tests)} tests passed.")
