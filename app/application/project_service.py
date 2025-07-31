from app.domain.entities import ProjectData
from app.infrastructure.project_storage import save_project_to_file, load_project_from_file


def export_project_to_json(project: ProjectData, filepath: str) -> None:
    save_project_to_file(project, filepath)


def import_project_from_json(filepath: str) -> ProjectData:
    return load_project_from_file(filepath)