from langchain_community.llms import Ollama
import pandas as pd

class TransactionCategorizer:
    def __init__(self):
        self.llm = Ollama(model="llama3.1")
        self.categories = [
            "Salary/Wages", "Investment Income", "Freelance Income", 
            "Business Revenue", "Rental Income", "Housing", 
            "Utilities", "Groceries", "Transportation", "Insurance", 
            "Healthcare", "Entertainment", "Personal Care", "Education", 
            "Savings/Investments", "Loans/Debt", "Taxes", 
            "Childcare", "Gifts/Donations", "Dining Out", 
            "Travel", "Shopping", "Subscriptions", 
            "Pet Care", "Home Improvement", "Clothing", 
            "Tech/Gadgets", "Fitness/Sports"
        ]
        self.categories_string = ",".join(self.categories)
    
    def hop(self, start, stop, step):
        for i in range(start, stop, step):
            yield i
        yield stop