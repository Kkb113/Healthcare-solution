import pandas as pd
from hcp.ml.constant_fixture import ConstantFixture


def test_nonclinical_model_returns_one_constant_per_input_row():
    model = ConstantFixture()
    for count in [0, 1, 3]:
        result = model.predict(None, pd.DataFrame({"input": range(count)}))
        assert list(result.columns) == ["prediction"]
        assert result["prediction"].tolist() == [42] * count


def test_saved_serving_artifact_has_full_mlflow_and_loadable_signature(tmp_path):
    import mlflow
    from mlflow.models import infer_signature
    from probe_model_serving import SERVING_REQUIREMENTS

    sample = pd.DataFrame({"input": [1]})
    expected = ConstantFixture().predict(None, sample)
    path = tmp_path / "constant"
    mlflow.pyfunc.save_model(
        path=str(path),
        python_model=ConstantFixture(),
        signature=infer_signature(sample, expected),
        input_example=sample,
        pip_requirements=SERVING_REQUIREMENTS,
    )
    requirements = (path / "requirements.txt").read_text().splitlines()
    assert "mlflow==3.17.2" in requirements
    assert not any(line.startswith("mlflow-skinny") for line in requirements)
    assert mlflow.pyfunc.load_model(str(path)).predict(sample).equals(expected)
