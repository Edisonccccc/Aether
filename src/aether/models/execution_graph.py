from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class WorkStatus(str, Enum):
    PLANNED = "Planned"
    READY = "Ready"
    RUNNING = "Running"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"
    FAILED = "Failed"


class ObjectState(str, Enum):
    MISSING = "Missing"
    DRAFT = "Draft"
    IN_PROGRESS = "InProgress"
    READY = "Ready"
    ARCHIVED = "Archived"


class ExecutionObject(BaseModel):
    id: str
    type: str
    title: str
    description: Optional[str] = None
    state: ObjectState = ObjectState.MISSING


class Work(BaseModel):
    id: str
    title: str
    primary_object_id: str
    status: WorkStatus = WorkStatus.PLANNED
    description: Optional[str] = None
    constraints: list[str] = Field(default_factory=list)


class Dependency(BaseModel):
    prerequisite_work_id: str
    dependent_work_id: str


class ExecutionGraph(BaseModel):
    works: list[Work] = Field(default_factory=list)
    objects: list[ExecutionObject] = Field(default_factory=list)
    dependencies: list[Dependency] = Field(default_factory=list)

    def work_map(self) -> dict[str, Work]:
        return {w.id: w for w in self.works}

    def object_map(self) -> dict[str, ExecutionObject]:
        return {o.id: o for o in self.objects}

    def get_prerequisites(self, work_id: str) -> list[str]:
        return [d.prerequisite_work_id for d in self.dependencies if d.dependent_work_id == work_id]

    def get_dependents(self, work_id: str) -> list[str]:
        return [d.dependent_work_id for d in self.dependencies if d.prerequisite_work_id == work_id]

    def get_ready_works(self) -> list[Work]:
        return [w for w in self.works if w.status == WorkStatus.READY]
