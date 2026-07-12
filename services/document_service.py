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

    def chunk(self, text: str, source: str) -> list:
        """Greedy paragraph packing to ~CHUNK_CHARS with an overlap tail so
        answers spanning a boundary still retrieve. Returns
        [{'text', 'source', 'chunk'}] ready for embedding."""
        paragraphs = []
        for p in text.split("\n\n"):
            p = p.strip()
            if not p:
                continue
            while len(p) > CHUNK_CHARS:          # hard-split oversized paragraphs
                paragraphs.append(p[:CHUNK_CHARS])
                p = p[CHUNK_CHARS - OVERLAP_CHARS:]
            paragraphs.append(p)

        chunks, buf = [], ""
        for p in paragraphs:
            if buf and len(buf) + len(p) > CHUNK_CHARS:
                chunks.append(buf)
                buf = buf[-OVERLAP_CHARS:] + "\n" + p
            else:
                buf = f"{buf}\n\n{p}" if buf else p
        if buf:
            chunks.append(buf)

        return [
            {"text": c, "source": source, "chunk": i}
            for i, c in enumerate(chunks, 1)
        ]
