from dataclasses import dataclass
from typing import Optional
import pandas as pd

@dataclass
class AppState:
    """Application state model"""
    categorized_df: Optional[pd.DataFrame] = None
    filename: Optional[str] = None
    web_enabled: bool = False
    semantic_enabled: bool = False
    current_view: str = "Dashboard"
    model_name: Optional[str] = None
