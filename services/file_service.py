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

    @staticmethod
    def _clean_amount(value) -> float:
        """'$1,234.56', '(12.50)', '1 234,56' (EU decimal comma) → float, else NaN"""
        s = re.sub(r'[$\s()]', '', str(value))
        # comma + 1-2 trailing digits = EU decimal ("1.234,56"); a 3-digit
        # tail ("5,000") is US thousands, so it falls through to the else
        if re.fullmatch(r'-?\d+(\.\d{3})*,\d{1,2}', s):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')                        # US: 1,234.56
        try:
            return float(s)
        except ValueError:
            return float('nan')
