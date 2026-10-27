"""Nonclinical constant model used only to verify registry/serving contracts."""

import mlflow.pyfunc
import pandas as pd


class ConstantFixture(mlflow.pyfunc.PythonModel):
    def predict(self, context, model_input: pd.DataFrame, params=None) -> pd.DataFrame:
        return pd.DataFrame({"prediction": [42] * len(model_input)})
