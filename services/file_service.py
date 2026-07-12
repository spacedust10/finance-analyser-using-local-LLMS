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

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate, coerce, and clean. Raises ValueError on unusable data.
        Dropped-row count is stored in df.attrs['dropped_rows']."""
        missing = [c for c in REQUIRED if c not in data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df = data.copy()
        # single inferred format for the whole column — format='mixed' guesses
        # per row and silently scrambles DD/MM vs MM/DD within one file
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # ponytail: direction comes from the Expense/Income column, so amounts
        # are stored as magnitudes; a refund logged as a negative Expense row
        # inflates totals — switch to signed aggregation if that case matters
        df['Amount'] = df['Amount'].map(self._clean_amount).abs()
        df['Expense/Income'] = df['Expense/Income'].astype(str).str.strip().str.title()
        # collapse ALL whitespace (incl. embedded newlines): names flow into LLM
        # prompts, where a newline lets a memo forge its own prompt lines
        df['Name/Description'] = (
            df['Name/Description'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
        )

        bad = (
            df['Date'].isna()
            | df['Amount'].isna()
            | ~df['Expense/Income'].isin(['Expense', 'Income'])
        )
        df = df[~bad].reset_index(drop=True)
        if df.empty:
            raise ValueError(
                "No valid rows: need a parseable Date, numeric Amount, "
                "and Expense/Income of 'Expense' or 'Income'"
            )

        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['YearMonth'] = df['Date'].dt.strftime('%Y-%m')
        df.attrs['dropped_rows'] = int(bad.sum())
        return df
