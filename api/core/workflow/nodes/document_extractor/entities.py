from graphon.nodes.document_extractor import DocumentExtractorNodeData as GraphonDocumentExtractorNodeData


class DocumentExtractorNodeData(GraphonDocumentExtractorNodeData):
    is_extract_comments: bool = False
