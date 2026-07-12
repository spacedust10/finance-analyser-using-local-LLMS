import re
import pandas as pd
from typing import BinaryIO

REQUIRED = ['Date', 'Name/Description', 'Amount', 'Expense/Income']

class FileService:
    """Reads and cleans transaction CSVs"""

    def read_file(self, file: BinaryIO) -> pd.DataFrame:
        try:
            return pd.read_csv(file)
        except Exception as e:
            raise ValueError(f"Could not read CSV: {e}")
