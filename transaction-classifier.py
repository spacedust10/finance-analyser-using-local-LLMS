from langchain_community.llms import Ollama
import pandas as pd

class TransactionCategorizer:
    def __init__(self):
        self.llm = Ollama(model="llama3.1")