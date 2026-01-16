from pygres.models.base_model import PydanticTypeModel
from pygres.tables.table import PydanticTypeTable
from mermaid_class.core.models import DiagramRequest, BulkDiagramResponse

class ClassDiagramRow(PydanticTypeModel):
    input: DiagramRequest
    output: BulkDiagramResponse | None = None
    request_id: int | None = None

class ClassDiagramTable(PydanticTypeTable):
    def __init__(self, db):
        super().__init__(db, ClassDiagramRow)
