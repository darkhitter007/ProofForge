from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = 1

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@dataclass(frozen=True)
class CaseManifest:
    schema_version: int
    case_id: str
    title: str
    created_at: str
    authorization_status: str
    target: str
    researcher_assertions: list[str]

    @classmethod
    def new(cls, case_id: str, title: str) -> "CaseManifest":
        return cls(
            schema_version=SCHEMA_VERSION,
            case_id=case_id,
            title=title,
            created_at=utc_now(),
            authorization_status="UNCONFIRMED",
            target="UNSPECIFIED",
            researcher_assertions=[],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
