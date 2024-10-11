import pandas as pd
from transaction_classifier import TransactionCategorizer

class FileProcessor:
    def upload_file(self, uploaded_file):
        """Reads the uploaded CSV file and returns it as a DataFrame."""
        return pd.read_csv(uploaded_file)

    def process_dataframe(self, df, filename):
        """Process the dataframe using TransactionCategorizer."""
        categorizer = TransactionCategorizer()
        categorized_df, _ = categorizer.process_data(df, filename)
        return categorized_df