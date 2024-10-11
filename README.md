
# Finance Analyzer - On-Device Personal Financial Analysis

This finance analyzer project is an on-device, data-driven tool designed to analyze personal financial data. Users can upload financial statements in CSV format, which are processed and categorized using open-source models from Ollama’s Llama3.1. The project ensures privacy by keeping all analysis and computations on-device. It provides detailed insights into income, expenses, saving rates, and spending patterns through interactive visualizations like pie charts, bar charts, and line graphs. Built with Streamlit, the tool offers a user-friendly interface and generates customized financial reports without relying on external cloud services.


## Overview of this Project

This project provides an on-device financial analysis tool that allows users to upload their financial data in CSV format. The analysis includes income, expenses, saving rates, and spending patterns, with insights displayed via interactive visualizations. The tool uses open-source LLMs from [Ollama](https://www.ollama.com) and runs locally to ensure data privacy.
## Project Breakdown
### 1. File Upload & Data Processing
- Users upload financial statements in CSV format.
- The system processes the data, categorizing transactions into income and expenses using Ollama’s open-source LLM models.
- Date columns are converted to extract useful information like year, month, and day.

### 2. Data Categorization
- Transactions are automatically classified into categories (e.g., food, rent, salary) using a custom model.
- This ensures that financial insights can be tailored to specific categories of spending and income.

### 3. Data Visualization
Interactive visualizations include:
- **Pie Charts**: Breakdown of income and expenses by category.
- **Bar Charts**: Monthly income and expense trends.
- **Line Charts**: Saving rate trends over time.
  
Visualizations are built using libraries like [Plotly](https://plotly.com/python/) for a seamless user experience.

### 4. Local LLM Integration
- The project uses Ollama’s Llama3.1 LLMs for categorizing transactions.
- All computations happen on-device, ensuring privacy and security of financial data.

### 5. Streamlit Interface
- A user-friendly dashboard is built using [Streamlit](https://docs.streamlit.io) to provide:
  - Easy file upload
  - Real-time data analysis
  - Display of financial insights through various charts and graphs
- No external cloud services are used; the tool runs locally on your device.

# Installation

## 1. Prerequisites

Before you begin, ensure you have the following:
- Python 3.8 or higher
- Internet access to download dependencies

## 2. Installing Ollama (for LLM-based Transaction Categorization)
Ollama provides the LLM used for transaction categorization. Follow the steps based on your platform

- [For Ollama API](https://ollama.com/download)
- After Installation, to use the open-source models with Ollama:
```bash
ollama pull llama3.1
```
> you can have any model name instead of __llama3.1__ and change in the code accordingly

## 3. Setting up Python Environment
- Clone the Repository and open that in your IDE
```bash
git clone https://github.com/yourusername/finance-analyzer.git
cd finance-analyzer
```
- Install Python dependencies: You will need to install the required Python packages listed in the requirements.txt file.
```bash
pip install -r requirements.txt
```
## 4. Running the Project
Once all dependencies and models are installed, you can start the Finance Analyzer app. <br>Run the app locally using __Streamlit__:
```bash
streamlit run app.py
```
Open your browser and navigate to the Streamlit app (usually runs at ```http://localhost:8501```).

For additional support, refer to the [Ollama documentation](https://github.com/ollama/ollama/tree/main/docs) and the [Streamlit documentation.](https://docs.streamlit.io/)
