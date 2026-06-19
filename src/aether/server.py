from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from aether.adapters.text_adapter import TextAdapter
from aether.compiler.plan_compiler import PlanCompiler
from aether.models.context_graph import NodeType
from aether.planner.planner import Planner

load_dotenv()

BASE_DIR = Path(__file__).parent.parent.parent
INDEX_HTML = BASE_DIR / "index.html"

app = FastAPI(title="Aether")
_executor = ThreadPoolExecutor(max_workers=4)

_ICONS = [
    "🏗️", "⚡", "🧠", "🔗", "🚀", "🔬",
    "🔐", "📊", "🎨", "✅", "📝", "🔧",
    "⚙️", "🗃️", "🔄", "🧪", "🎯", "📡",
]
_OWNERS = [
    {"i": "EC", "c": "#8B6FFF"},
    {"i": "MK", "c": "#22D3EE"},
    {"i": "LR", "c": "#F472B6"},
    {"i": "AT", "c": "#FBBF24"},
    {"i": "JP", "c": "#34D399"},
    {"i": "SP", "c": "#60A5FA"},
]


class PlanRequest(BaseModel):
    input: str
    depth: int = 2


@app.get("/")
def serve_ui() -> HTMLResponse:
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


@app.post("/api/plan")
async def plan_endpoint(req: PlanRequest) -> JSONResponse:
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            _executor, _run_pipeline, req.input, req.depth
        )
        return JSONResponse(result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _run_pipeline(input_text: str, depth: int) -> dict[str, Any]:
    client = anthropic.Anthropic()

    context_graph = TextAdapter(client=client).parse(input_text)
    plan = Planner(client=client, max_depth=depth).plan(context_graph)
    exec_graph = PlanCompiler().compile(plan, context_graph)

    goals = context_graph.get_nodes_by_type(NodeType.GOAL)
    title = goals[0].title if goals else input_text[:60]

    phases, deps = _schedule(exec_graph)
    return {"title": title, "phases": phases, "dependencies": deps}


def _schedule(exec_graph: Any) -> tuple[list[dict], list[dict]]:
    DAYS_PER_WORK = 14

    prereqs: dict[str, list[str]] = {w.id: [] for w in exec_graph.works}
    for dep in exec_graph.dependencies:
        prereqs[dep.dependent_work_id].append(dep.prerequisite_work_id)

    start_days: dict[str, int] = {}

    def get_start(wid: str) -> int:
        if wid in start_days:
            return start_days[wid]
        if not prereqs[wid]:
            start_days[wid] = 0
        else:
            start_days[wid] = max(get_start(p) + DAYS_PER_WORK for p in prereqs[wid])
        return start_days[wid]

    for w in exec_graph.works:
        get_start(w.id)

    # Group by start day, assign lanes in order
    day_groups: dict[int, list[str]] = {}
    for w in exec_graph.works:
        day_groups.setdefault(start_days[w.id], []).append(w.id)

    lane_assignment: dict[str, int] = {}
    lane_counter = 0
    for sd in sorted(day_groups):
        for wid in day_groups[sd]:
            lane_assignment[wid] = lane_counter % 6
            lane_counter += 1

    obj_map = exec_graph.object_map()
    work_to_phase: dict[str, str] = {}
    phases = []

    for i, w in enumerate(exec_graph.works):
        pid = f"p{i + 1}"
        work_to_phase[w.id] = pid
        obj = obj_map.get(w.primary_object_id)
        deliverables = [obj.title] if obj else [w.title]
        phases.append({
            "id": pid,
            "name": w.title,
            "icon": _ICONS[i % len(_ICONS)],
            "startDay": start_days[w.id],
            "durationDays": DAYS_PER_WORK,
            "lane": lane_assignment[w.id],
            "progress": 0,
            "gradIdx": i % 6,
            "status": "planned",
            "owners": [_OWNERS[i % len(_OWNERS)]],
            "deliverables": deliverables,
            "description": w.description or f"Build and deliver: {deliverables[0]}",
        })

    seen: set[tuple[str, str]] = set()
    phase_deps: list[dict] = []
    for dep in exec_graph.dependencies:
        f = work_to_phase.get(dep.prerequisite_work_id)
        t = work_to_phase.get(dep.dependent_work_id)
        if f and t and f != t and (f, t) not in seen:
            phase_deps.append({"from": f, "to": t})
            seen.add((f, t))

    return phases, phase_deps


def main() -> None:
    import uvicorn
    uvicorn.run("aether.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
