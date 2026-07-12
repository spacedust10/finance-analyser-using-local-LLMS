from pypdf import PdfReader

CHUNK_CHARS = 1200
OVERLAP_CHARS = 200

class DocumentService:
    """Extracts and chunks reference documents (10-K filings, receipts, reports)
    into vector-store-ready pieces with source citations."""

    def extract_text(self, file) -> str:
        """file: uploaded file-like object with a .name attribute"""
        if file.name.lower().endswith(".pdf"):
            reader = PdfReader(file)
            return "\n\n".join(
                f"[page {i}] {page.extract_text() or ''}"
                for i, page in enumerate(reader.pages, 1)
            )
        return file.read().decode("utf-8", errors="replace")
