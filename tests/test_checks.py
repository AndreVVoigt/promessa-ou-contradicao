import pandas as pd
import pytest

from src.quality import checks as c

MOCK = "data/mock/silver_mock.parquet"
BROKEN = "data/mock/silver_broken.parquet"
MANIFEST = "data/mock/documents_mock.csv"
MANIFEST_BROKEN = "data/mock/documents_broken.csv"


@pytest.fixture
def chunks_ok():
    return pd.read_parquet(MOCK)


@pytest.fixture
def chunks_broken():
    return pd.read_parquet(BROKEN)


@pytest.fixture
def manifest_ok():
    return pd.read_csv(MANIFEST)


@pytest.fixture
def manifest_broken():
    return pd.read_csv(MANIFEST_BROKEN)


# 1. chunk_id não nulo e único
def test_chunk_id_unico_passa_no_mock_valido(chunks_ok):
    r = c.chunk_id_nao_nulo_e_unico(chunks_ok)
    assert r.passou and r.violacoes == 0


def test_chunk_id_unico_acusa_duplicata(chunks_broken):
    r = c.chunk_id_nao_nulo_e_unico(chunks_broken)
    assert not r.passou
    assert "PRES_001_p012_c001" in r.ids


# 2. document_id existe no manifest
def test_document_id_existente_passa_no_mock_valido(chunks_ok, manifest_ok):
    r = c.document_id_existe_no_manifest(chunks_ok, manifest_ok)
    assert r.passou and r.violacoes == 0


def test_document_id_acusa_orfao(chunks_broken, manifest_ok):
    r = c.document_id_existe_no_manifest(chunks_broken, manifest_ok)
    assert not r.passou
    assert "PRES_999_p001_c001" in r.ids


# 3. page >= 1
def test_page_passa_no_mock_valido(chunks_ok):
    r = c.page_maior_ou_igual_a_um(chunks_ok)
    assert r.passou and r.violacoes == 0


def test_page_acusa_valor_negativo(chunks_broken):
    r = c.page_maior_ou_igual_a_um(chunks_broken)
    assert not r.passou
    assert "PRES_001_p000_c001" in r.ids


# 4. text não vazio
def test_text_passa_no_mock_valido(chunks_ok):
    r = c.text_nao_vazio(chunks_ok)
    assert r.passou and r.violacoes == 0


def test_text_acusa_string_de_espacos(chunks_broken):
    r = c.text_nao_vazio(chunks_broken)
    assert not r.passou
    assert "PRES_002_p007_c003" in r.ids


# 5. office e state válidos
def test_office_state_passa_no_manifest_valido(manifest_ok):
    r = c.office_e_state_permitidos(manifest_ok)
    assert r.passou and r.violacoes == 0


def test_office_state_acusa_maiuscula_errada(manifest_broken):
    r = c.office_e_state_permitidos(manifest_broken)
    assert not r.passou
    assert "PRES_002" in r.ids


# section: nulo é ok
def test_section_nula_nao_e_violacao(chunks_ok):
    assert chunks_ok["section"].isna().sum() == 1
    for resultado in [
        c.chunk_id_nao_nulo_e_unico(chunks_ok),
        c.page_maior_ou_igual_a_um(chunks_ok),
        c.text_nao_vazio(chunks_ok),
    ]:
        assert resultado.passou
