import pandas as pd
import streamlit as st

class FileProcessor:
    def upload_and_process_file(self):
        uploaded_file = st.file_uploader("Upload your financial data📝", type=("txt", "csv", "pdf"))
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            return df
        return None