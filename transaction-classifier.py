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
            
        filtered_response = []
        
        # Retry if the LLM output is not consistent
        while len(filtered_response) < 2:
            response = self.llm.invoke(prompt).split("\n")
            filtered_response = [item for item in response if '-' in item]

        categories_df = pd.DataFrame({"Transaction vs category": filtered_response})
        size_dif = len(categories_df) - len(transaction_names.split(","))
        categories_df["Transaction"] = transaction_names.split(",") + [None] * size_dif if size_dif >= 0 else transaction_names.split(",")[:len(categories_df)]
        categories_df["Category"] = categories_df["Transaction vs category"].str.split("-", expand=True)[1]
        return categories_df
    
    def process_data(self, df: pd.DataFrame, filename: str):
        unique_transactions = df["Name/Description"].unique()
        index_list = list(self.hop(0, len(unique_transactions), 30))
        
        categories_df_all = pd.DataFrame()

        for i in range(0, len(index_list) - 1):
            transaction_names = unique_transactions[index_list[i]: index_list[i + 1]]
            transaction_names = ",".join(transaction_names)
            categories_df = self.categorize_transactions(transaction_names)
            categories_df_all = pd.concat([categories_df_all, categories_df], ignore_index=True)
        
        # Data cleaning
        categories_df_all = categories_df_all.dropna()
        categories_df_all["Transaction"] = categories_df_all["Transaction"].str.replace(r"\d+\.\s?", "", regex=True).str.strip()

        new_df = pd.merge(df, categories_df_all, left_on="Name/Description", right_on="Transaction", how="left")
        save_path = f"{filename}_categorized.csv"
        new_df.to_csv(save_path, index=False)
        return new_df, save_path