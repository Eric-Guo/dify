import io
import logging
from collections.abc import Mapping
from typing import cast, override

import docx

from graphon.entities.base_node_data import BaseNodeData
from graphon.enums import WorkflowNodeExecutionStatus
from graphon.file import File
from graphon.http import HttpClientProtocol
from graphon.node_events import NodeRunResult
from graphon.nodes.document_extractor import DocumentExtractorNode as GraphonDocumentExtractorNode
from graphon.nodes.document_extractor import UnstructuredApiConfig
from graphon.nodes.document_extractor.exc import DocumentExtractorError
from graphon.nodes.document_extractor.node import (
    _extract_text_from_docx,
    _normalize_docx_zip,
    download_file_content,
)
from graphon.nodes.document_extractor.node import (
    _extract_text_from_file as extract_file_text,
)
from graphon.variables.segments import ArrayFileSegment, ArrayStringSegment, FileSegment

from .entities import DocumentExtractorNodeData

logger = logging.getLogger(__name__)


class DocumentExtractorNode(GraphonDocumentExtractorNode):
    """Extend Graphon's file extraction with the optional DOCX comment output."""

    @classmethod
    @override
    def version(cls) -> str:
        return "1"

    @classmethod
    @override
    def validate_node_data(cls, node_data: BaseNodeData | Mapping[str, object]) -> DocumentExtractorNodeData:
        if isinstance(node_data, BaseNodeData):
            node_data = node_data.model_dump(mode="python", by_alias=True)
        return DocumentExtractorNodeData.model_validate(node_data)

    @property
    @override
    def node_data(self) -> DocumentExtractorNodeData:
        return cast(DocumentExtractorNodeData, super().node_data)

    @override
    def _run(self) -> NodeRunResult:
        variable_selector = self.node_data.variable_selector
        variable = self.graph_runtime_state.variable_pool.get(variable_selector)

        error_message = None
        if variable is None:
            error_message = f"File variable not found for selector: {variable_selector}"
        elif variable.value and not isinstance(
            variable,
            ArrayFileSegment | FileSegment,
        ):
            error_message = f"Variable {variable_selector} is not an ArrayFileSegment"

        if error_message is not None:
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                error=error_message,
            )

        if variable is None:
            msg = f"File variable not found for selector: {variable_selector}"
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                error=msg,
            )
        value = variable.value
        inputs = {"variable_selector": variable_selector}
        if isinstance(value, list):
            value = list(filter(lambda x: x, value))
        process_data = {"documents": value if isinstance(value, list) else [value]}

        if not value:
            return NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                inputs=inputs,
                process_data=process_data,
                outputs={"text": ArrayStringSegment(value=[])},
            )

        if isinstance(value, list):
            try:
                extracted_text_list = [
                    _extract_text_from_file(
                        self._http_client,
                        file,
                        unstructured_api_config=self._unstructured_api_config,
                        extract_comments=self.node_data.is_extract_comments,
                    )
                    for file in value
                ]
            except DocumentExtractorError as e:
                logger.warning(e, exc_info=True)
                return NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    error=str(e),
                    inputs=inputs,
                    process_data=process_data,
                )
            outputs: dict[str, ArrayStringSegment | str] = {"text": ArrayStringSegment(value=extracted_text_list)}
        else:
            try:
                extracted_text = _extract_text_from_file(
                    self._http_client,
                    value,
                    unstructured_api_config=self._unstructured_api_config,
                    extract_comments=self.node_data.is_extract_comments,
                )
            except DocumentExtractorError as e:
                logger.warning(e, exc_info=True)
                return NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    error=str(e),
                    inputs=inputs,
                    process_data=process_data,
                )
            outputs = {"text": extracted_text}

        return NodeRunResult(
            status=WorkflowNodeExecutionStatus.SUCCEEDED,
            inputs=inputs,
            process_data=process_data,
            outputs=outputs,
        )


def _extract_text_from_file(
    http_client: HttpClientProtocol,
    file: File,
    *,
    unstructured_api_config: UnstructuredApiConfig,
    extract_comments: bool,
) -> str:
    is_docx = (file.extension or "").lower() == ".docx" or file.mime_type == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    if not extract_comments or not is_docx:
        return extract_file_text(http_client, file, unstructured_api_config=unstructured_api_config)

    file_content = download_file_content(http_client, file)
    text = _extract_text_from_docx(file_content)
    try:
        document = docx.Document(io.BytesIO(_normalize_docx_zip(file_content)))
        comments = [comment.text.strip() for comment in document.comments if comment.text.strip()]
    except Exception:
        logger.warning("Failed to extract comments from DOCX", exc_info=True)
        return text
    return "\n".join([text, *comments])
