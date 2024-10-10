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

    def categorize_transactions(self, transaction_names):
        prompt = f"""Add an appropriate category to the following expenses.
            Remember The category should only be one of the following and choose only one category from the list that is most relevant based on their primary purpose or nature: {self.categories_string}.\n  
            The output format should always be : transaction name - category. For example: Spotify #2 - Entertainment, Basic Fit Amsterdam Nld #3 - Fitness/Sports \n 
            Here are the Transactions to be categorized: {transaction_names} \n"""