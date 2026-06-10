from travel_planner_co.domain.services.text_chunker import TextChunker


class SimpleTextChunker(TextChunker):
    def chunk(self, text: str, max_chunk_size: int = 1000) -> list[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[str] = []
        current = ""

        for para in paragraphs:
            if len(current) + len(para) + 2 <= max_chunk_size:
                current = (current + "\n\n" + para) if current else para
            else:
                if current:
                    chunks.append(current)
                current = para

        if current:
            chunks.append(current)

        return chunks if chunks else [text]
