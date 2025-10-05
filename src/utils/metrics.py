from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def compute_metrics(y_true, y_pred):
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mape = float((np.abs((y_true - y_pred) / (y_true + 1e-9)).mean()) * 100.0)
    return {"MAE": mae, "RMSE": rmse, "MAPE": mape}
