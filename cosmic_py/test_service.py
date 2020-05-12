import pytest

from respository import AbstractRepository
import models
import services


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self.batches = set(batches)

    def add(self, batch):
        self.batches.add(batch)

    def get(self, reference):
        return next(b for b in self.batches if b.reference == reference)

    def list(self):
        return list(self.batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = models.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = models.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = models.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = models.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = models.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = models.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True
