import re
from typing import List
import pandas as pd
from langchain_ollama import OllamaLLM
from config.settings import CategoryConfig, ModelConfig

class TransactionClassificationService:
    """Categorizes transaction descriptions with a local LLM"""

    BATCH_SIZE = 30

    def __init__(self, model_config: ModelConfig = None, category_config: CategoryConfig = None,
                 model_name: str = None):
        self.config = model_config or ModelConfig()
        self.categories = (category_config or CategoryConfig()).categories
        self._canon = {c.lower(): c for c in self.categories}
        # temperature=0 on purpose: classification must be deterministic;
        # config.temperature is the chat-response knob
        self.llm = OllamaLLM(model=model_name or self.config.model_name, temperature=0)

    def classify_transactions(self, transactions: List[str]) -> List[str]:
        results = []
        for i in range(0, len(transactions), self.BATCH_SIZE):
            batch = transactions[i:i + self.BATCH_SIZE]
            results.extend(self._classify_batch(batch))
        return results

    def _classify_batch(self, batch: List[str]) -> List[str]:
        numbered = "\n".join(f"{i}. {t}" for i, t in enumerate(batch, 1))
        prompt = (
            "You are a financial analyst categorizing bank-statement lines. "
            "Use your knowledge of merchants and brands: e.g. Netflix/Spotify are "
            "Subscriptions, Shell/Chevron are Transportation, Aetna is Insurance, "
            "Whole Foods is Groceries, DoorDash is Dining Out, paychecks and payroll "
            "deposits are Salary/Wages, dividend or brokerage credits are Investment Income.\n"
            f"Allowed categories (use these words exactly): {', '.join(self.categories)}.\n"
            "Reply with one line per transaction in the format: <number>. <category>\n"
            "No other text.\n\n"
            f"Transactions:\n{numbered}"
        )
        return self._parse_response(self.llm.invoke(prompt), len(batch))

    def _parse_response(self, response: str, n: int) -> List[str]:
        """Map numbered LLM lines back to positions by index, so hyphens or
        commas in transaction names can't misalign results. Unmatched or
        hallucinated categories become 'Uncategorized'."""
        out = ["Uncategorized"] * n
        for line in response.splitlines():
            m = re.match(r'\s*(\d+)\s*[.):\-]\s*(.+)', line)
            if not m:
                continue
            idx = int(m.group(1)) - 1
            if not 0 <= idx < n:
                continue
            key = m.group(2).strip().strip('*').strip().lower()
            if key in self._canon:
                out[idx] = self._canon[key]
            else:
                # line may echo the transaction name ("Starbucks - Dining Out")
                for cat in self.categories:
                    if cat.lower() in key:
                        out[idx] = cat
                        break
        return out

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        unique = df['Name/Description'].unique().tolist()
        categories = self.classify_transactions(unique)
        mapping = dict(zip(unique, categories))
        df['Category'] = df['Name/Description'].map(mapping).fillna("Uncategorized")
        return df
