"""
JSON serialization utilities
"""
import numpy as np
import pandas as pd
from typing import Any
import math


def clean_for_json(obj: Any) -> Any:
    """Clean data for JSON serialization, handling NaN, inf, and numpy types"""
    
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    
    elif isinstance(obj, (list, tuple)):
        return [clean_for_json(item) for item in obj]
    
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    
    elif isinstance(obj, np.ndarray):
        return clean_for_json(obj.tolist())
    
    elif isinstance(obj, pd.Series):
        return clean_for_json(obj.to_dict())
    
    elif isinstance(obj, pd.DataFrame):
        return clean_for_json(obj.to_dict('records'))
    
    elif isinstance(obj, (pd.Timestamp, pd.DatetimeIndex)):
        return obj.isoformat()
    
    elif pd.isna(obj):
        return None
    
    elif obj is None:
        return None
    
    return obj