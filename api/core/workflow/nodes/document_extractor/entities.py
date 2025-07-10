from collections.abc import Sequence

from core.workflow.nodes.base import BaseNodeData


class DocumentExtractorNodeData(BaseNodeData):
    variable_selector: Sequence[str]
    # Whether to extract comment contents from documents (currently affects DOCX files)
    is_extract_comments: bool = False
