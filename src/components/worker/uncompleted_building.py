from dataclasses import dataclass


@dataclass
class UncompletedBuildingComponent:
    build_name: str
    required_progress: int
    progress: int = 0
