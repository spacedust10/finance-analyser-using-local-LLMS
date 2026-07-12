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
