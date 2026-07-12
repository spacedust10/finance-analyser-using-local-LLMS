from dataclasses import dataclass, field
from typing import List

@dataclass
class ModelConfig:
    """LLM model configuration — the single knob for which Ollama model runs"""
    model_name: str = "llama3.1"
    temperature: float = 0.1

@dataclass
class AppConfig:
    """Application configuration"""
    page_title: str = "AI Finance Analyzer"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"

@dataclass
class CategoryConfig:
    """Transaction categories configuration"""
    categories: List[str] = field(default_factory=lambda: [
        "Salary/Wages", "Investment Income", "Freelance Income",
        "Housing", "Utilities", "Groceries", "Transportation",
        "Insurance", "Healthcare", "Entertainment", "Dining Out",
        "Shopping", "Subscriptions", "Education", "Travel"
    ])
