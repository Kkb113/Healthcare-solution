from types import SimpleNamespace

import pytest
from probe_genie_billing import TABLE, result_rows, space_definition


def test_pilot_exposes_only_the_three_constant_fixture_source():
    definition = space_definition()
    assert definition["version"] == 2
    assert definition["data_sources"] == {"tables": [{"identifier": TABLE}]}
    assert TABLE.startswith("hc_test._foundation_probe.")
    assert "answer_access_probe" not in str(definition)


def test_metadata_only_result_reads_existing_cached_chunk_without_execution():
    calls = []

    def chunk(statement_id, index):
        calls.append((statement_id, index))
        return SimpleNamespace(data_array=[["3"]])

    caller = SimpleNamespace(
        statement_execution=SimpleNamespace(get_statement_result_chunk_n=chunk)
    )
    response = SimpleNamespace(
        statement_response=SimpleNamespace(
            statement_id="existing", result=SimpleNamespace(data_array=None)
        )
    )
    assert result_rows(caller, response) == [["3"]]
    assert calls == [("existing", 0)]
    response.statement_response.result.data_array = []
    assert result_rows(object(), response) == []


def test_missing_cached_data_cannot_fall_back_to_model_answer():
    caller = SimpleNamespace(
        statement_execution=SimpleNamespace(
            get_statement_result_chunk_n=lambda *_: SimpleNamespace(data_array=None)
        )
    )
    response = SimpleNamespace(
        statement_response=SimpleNamespace(statement_id="existing", result=None)
    )
    with pytest.raises(RuntimeError, match="unavailable"):
        result_rows(caller, response)
