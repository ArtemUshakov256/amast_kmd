from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Section:
    name: str
    parameters: Dict[str, str] = field(default_factory=dict)


@dataclass
class Traverse:
    name: str
    parameters: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProjectData:
    sections: Dict[str, Section] = field(default_factory=dict)
    traverses: Dict[str, Traverse] = field(default_factory=dict)
    additional: List[str] = field(default_factory=list)