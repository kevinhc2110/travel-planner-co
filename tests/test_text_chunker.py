from travel_planner_co.infrastructure.services.text_chunker import SimpleTextChunker


class TestSimpleTextChunker:
    def setup_method(self):
        self.chunker = SimpleTextChunker()

    def test_empty_text(self):
        result = self.chunker.chunk("")
        assert result == [""]

    def test_single_short_paragraph(self):
        text = "Texto corto de prueba."
        result = self.chunker.chunk(text)
        assert result == [text]

    def test_multiple_paragraphs_fit_in_one_chunk(self):
        text = "Párrafo uno.\n\nPárrafo dos.\n\nPárrafo tres."
        result = self.chunker.chunk(text, max_chunk_size=2000)
        assert len(result) == 1

    def test_split_into_multiple_chunks(self):
        para1 = "A" * 600
        para2 = "B" * 600
        para3 = "C" * 600
        text = f"{para1}\n\n{para2}\n\n{para3}"
        result = self.chunker.chunk(text, max_chunk_size=1000)
        assert len(result) >= 2

    def test_preserves_paragraph_boundaries(self):
        text = "Corto.\n\n" + "X" * 900 + "\n\n" + "Y" * 900
        result = self.chunker.chunk(text, max_chunk_size=1000)
        for chunk in result:
            assert len(chunk) <= 1000 + 2

    def test_single_long_paragraph_returns_one_chunk(self):
        text = "X" * 2500
        result = self.chunker.chunk(text, max_chunk_size=1000)
        assert len(result) == 1

    def test_long_text_with_paragraphs_splits_correctly(self):
        para1 = "A" * 600
        para2 = "B" * 600
        para3 = "C" * 600
        text = f"{para1}\n\n{para2}\n\n{para3}"
        result = self.chunker.chunk(text, max_chunk_size=1000)
        assert len(result) >= 2

    def test_returns_list_with_one_element_for_short_text(self):
        text = "Hola mundo"
        result = self.chunker.chunk(text)
        assert isinstance(result, list)
        assert len(result) == 1
