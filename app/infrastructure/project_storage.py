import json
from app.domain.entities import ProjectData, Section, Traverse


def save_project_to_file(project: ProjectData, filepath: str) -> None:
    def to_dict(obj):
        if isinstance(obj, ProjectData):
            return {
                "sections": {k: v.parameters for k, v in obj.sections.items()},
                "traverses": {k: v.parameters for k, v in obj.traverses.items()},
                "additional": obj.additional,
            }
        return obj

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(to_dict(project), f, ensure_ascii=False, indent=2)


def load_project_from_file(filepath: str) -> ProjectData:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return ProjectData(
        sections={k: Section(name=k, parameters=v) for k, v in data.get("sections", {}).items()},
        traverses={k: Traverse(name=k, parameters=v) for k, v in data.get("traverses", {}).items()},
        additional=data.get("additional", [])
    )