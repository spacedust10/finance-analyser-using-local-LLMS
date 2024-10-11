import streamlit as st
import os
import pandas as pd
from file_processor import FileProcessor
from finance_dashboard import FinanceDashboard

def main():
    st.title("Finance Analyzer")

    menu = ["Upload CSV", "Analyse"]
    choice = st.sidebar.selectbox("Select an option", menu)

    uploaded_file = st.file_uploader("Upload your financial data 📝", type="csv", key="upload_csv_key")

    if choice == "Upload CSV":
        handle_file_upload(uploaded_file)

    elif choice == "Analyse":
        handle_analysis()

def handle_file_upload(uploaded_file):
    """Handles file upload and processes the file using FileProcessor."""
    if uploaded_file:
        st.subheader("Uploading your financial data...")
        file_processor = FileProcessor()
        with st.spinner("Processing data..."):
            df = file_processor.upload_file(uploaded_file)
            categorized_df = file_processor.process_dataframe(df, uploaded_file.name)

            st.session_state['filename'] = uploaded_file.name
            st.session_state['categorized_df'] = categorized_df
        st.success("Data processed: OK")

def handle_analysis():
    """Handles dashboard and focuses on visualisations rendering on streamlit"""
    st.subheader("Analyse your financial data")

    if 'filename' in st.session_state:
        file_path = f"processed_files/{st.session_state['filename'].replace('.csv', '_categorized.csv')}"
        
        if os.path.exists(file_path):
            categorized_df = pd.read_csv(file_path)
        else:
            st.warning("No categorized data found. Please upload and process your financial data first.")
            return
        
        finance_dashboard = FinanceDashboard(categorized_df)

        with st.spinner("Generating analysis..."):
            finance_dashboard.display_analysis_results()
            finance_dashboard.create_dashboard()
    else:
        st.warning("Please upload and process your financial data first.")

if __name__ == "__main__":
    main()