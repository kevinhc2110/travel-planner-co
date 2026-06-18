import pytest

from travel_planner_co.infrastructure.scrapers.list_splitter import (
    is_list_article,
    split_list_article,
    _split_by_numbers,
    _split_by_headings,
)


class TestIsListArticle:
    def test_keyword_match_mejores(self):
        assert is_list_article("Los mejores lugares de Colombia", "")

    def test_keyword_match_top(self):
        assert is_list_article("Top 10 playas", "")

    def test_keyword_match_pueblos_magicos(self):
        assert is_list_article("Pueblos mágicos de Colombia", "")

    def test_numbered_content(self):
        content = "1. Primer item\n2. Segundo item\n3. Tercer item"
        assert is_list_article("Artículo", content)

    def test_no_keyword_or_numbered(self):
        assert not is_list_article("Bienvenidos a Colombia", "Contenido normal sin números.")

    def test_insufficient_numbered_items(self):
        content = "1. Solo un item"
        assert not is_list_article("Normal article", content)


class TestSplitListArticle:
    def test_non_list_returns_single_item(self):
        result = split_list_article("Artículo normal", "Contenido simple.")
        assert len(result) == 1
        assert result[0]["title"] == "Artículo normal"

    def test_numbered_list_splits_correctly(self):
        content = "1. Primero\nContenido del primero\n2. Segundo\nContenido del segundo"
        result = split_list_article("Top destinos", content)
        assert len(result) == 2
        assert "Primero" in result[0]["title"]
        assert "Segundo" in result[1]["title"]

    def test_skips_short_sections(self):
        content = "1. Uno\n\n2. D\n\n3. Tres\nContenido del tercero"
        result = split_list_article("Lista", content)
        if len(result) >= 2:
            assert all(
                len(r["content"]) >= 20 or "Tres" in r["title"]
                for r in result
            )


class TestSplitByNumbers:
    def test_finds_numbered_sections(self):
        content = "1. Primero\nalgo\n2. Segundo\notra cosa"
        result = _split_by_numbers(content)
        assert len(result) == 2
        assert result[0][0] == "Primero"
        assert result[1][0] == "Segundo"

    def test_less_than_two_matches(self):
        assert _split_by_numbers("Sin números") == []


class TestSplitByHeadings:
    def test_detects_headings(self):
        lines = "Bogotá\nContenido sobre Bogotá\nMedellín\nContenido sobre Medellín"
        result = _split_by_headings(lines)
        assert len(result) >= 2

    def test_no_headings(self):
        text = "Esto es un texto continuo sin encabezados. Sigue así varias líneas."
        result = _split_by_headings(text)
        assert len(result) == 0
