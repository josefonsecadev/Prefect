from datetime import datetime
from io import BytesIO
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from pipelines.camara_deputados.despesas.bronze import resolve_year
from utils.pipeline import Pipeline


class DummyResponse:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyMinioClient:
    def __init__(self, objects):
        self.objects = objects

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def list_objects(self, bucket_name, prefix, recursive):
        return self.objects

    def get_object(self, bucket_name, object_name):
        return DummyResponse(b"arquivo-conteudo")


def test_resolve_year_uses_explicit_value():
    assert resolve_year(2022) == 2022


def test_resolve_year_defaults_to_current_year():
    assert resolve_year(None) == datetime.now().year


def test_read_arquivo_raises_when_multiple_files(monkeypatch):
    pipeline = Pipeline("camara_deputados", "bronze")
    objects = [SimpleNamespace(object_name="a"), SimpleNamespace(object_name="b")]
    monkeypatch.setattr(pipeline, "_minio", lambda: DummyMinioClient(objects))

    with pytest.raises(ValueError, match="Mais de um arquivo"):
        pipeline._read_arquivo("2024")


def test_read_arquivo_returns_bytesio_for_single_file(monkeypatch):
    pipeline = Pipeline("camara_deputados", "bronze")
    objects = [SimpleNamespace(object_name="camara_deputados/bronze/2024/despesas.csv")]
    monkeypatch.setattr(pipeline, "_minio", lambda: DummyMinioClient(objects))

    arquivo = pipeline._read_arquivo("2024")

    assert isinstance(arquivo, BytesIO)
    assert arquivo.getvalue() == b"arquivo-conteudo"
