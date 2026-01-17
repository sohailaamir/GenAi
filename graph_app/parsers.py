
import json
from typing import Type, TypeVar
from pydantic import ValidationError
from .models import Decision, TaskResult

T = TypeVar("T")

def parse_json_to_model(text: str, model: Type[T]) -> T:
    """Try to parse LLM output (JSON string) to a Pydantic model with helpful errors."""
    try:
        data = json.loads(text)
        return model.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Failed to parse model {model.__name__} from: {text[:200]}...\nError: {e}")

def parse_decision_or_heuristic(text: str, original_input: str) -> Decision:
    """Parse manager decision; fall back to a simple keyword heuristic if needed."""
    try:
        return parse_json_to_model(text, Decision)
    except Exception:
        low = text.strip().lower()
        if "translate" in low:
            agent = "translate"
        elif "summarize" in low or "summary" in low:
            agent = "summarize"
        elif "calc" in low or "math" in low or any(ch in low for ch in "+-*/^"):
            agent = "calculate"
        else:
            # Heuristic from input
            l2 = original_input.lower()
            if any(k in l2 for k in ["translate", "traduci", "traduire", "übersetze"]):
                agent = "translate"
            elif any(k in l2 for k in ["sum", "summary", "summarize", "synopsis"]):
                agent = "summarize"
            elif any(op in l2 for op in ["+", "-", "*", "/", "^"]):
                agent = "calculate"
            else:
                agent = "summarize"
        return Decision(agent=agent, input=original_input)
