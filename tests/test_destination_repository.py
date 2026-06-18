from travel_planner_co.infrastructure.data.repositories.destination_repository import (
    DestinationRepository,
)


class TestDestinationRepositoryNameMatching:
    def setup_method(self):
        self.repo = DestinationRepository.__new__(DestinationRepository)

    def test_normalize_name_lowercase(self):
        result = self.repo._normalize_name("Parque Tayrona")
        assert result == "parque tayrona"

    def test_normalize_name_removes_accents(self):
        result = self.repo._normalize_name("Bogotá")
        assert result == "bogota"

    def test_normalize_name_removes_parentheses(self):
        result = self.repo._normalize_name("Parque Tayrona (Santa Marta)")
        assert "(" not in result
        assert ")" not in result

    def test_normalize_name_strips_prefix(self):
        result = self.repo._normalize_name("Parque Nacional Natural Tayrona")
        assert result == "tayrona"

    def test_normalize_name_splits_colon(self):
        result = self.repo._normalize_name("Destino: algo más")
        assert ":" not in result

    def test_normalize_name_removes_non_alphanumeric(self):
        result = self.repo._normalize_name("¡Cartagena de Indias!")
        assert result == "cartagena de indias"

    def test_names_match_exact(self):
        assert self.repo._names_match("tayrona", "tayrona") is True

    def test_names_match_substring(self):
        assert self.repo._names_match("tayrona", "parque tayrona") is True

    def test_names_match_no_match(self):
        assert self.repo._names_match("bogota", "medellin") is False

    def test_names_match_empty(self):
        assert self.repo._names_match("", "test") is False
        assert self.repo._names_match("test", "") is False
