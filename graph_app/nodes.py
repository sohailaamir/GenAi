
from __future__ import annotations
from typing import Dict
from .llm import llm
from .models import TaskResult
from .parsers import parse_decision_or_heuristic

# ---------------- Safe arithmetic evaluator (no eval) ----------------
import ast, operator as op

ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
}

def _eval_ast(node):
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        op_type = type(node.op)
        if op_type not in ALLOWED_OPS:
            raise ValueError("Operator not allowed")
        return ALLOWED_OPSop_type
    if isinstance(node, ast.UnaryOp):
        operand = _eval_ast(node.operand)
        op_type = type(node.op)
        if op_type not in ALLOWED_OPS:
            raise ValueError("Operator not allowed")
        return ALLOWED_OPSop_type
    raise ValueError("Unsupported expression")

def safe_eval(expr: str) -> str:
    try:
        tree = ast.parse(expr, mode='eval')
        value = _eval_ast(tree.body)
        return str(value)
    except Exception as e:
        return f"(could not evaluate locally: {e})"

# ---------------- LangGraph Node implementations ----------------
def manager_node(state: Dict) -> Dict:
    task_input = state.get("task", "")
    user_input = state.get("input", "")
    prompt = (
        "You are a task router. Return ONLY a JSON object with keys 'agent' and 'input'.\n"
        "- agent must be one of: translate, summarize, calculate.\n"
        "- input must echo the provided input.\n\n"
        f"Task: {task_input}\n"
        f"Input: {user_input}\n\n"
        "Respond like: {\"agent\": \"summarize\", \"input\": \"...\"}"
    )
    raw = llm.invoke(prompt).content
    decision = parse_decision_or_heuristic(raw, user_input)
    return {"agent": decision.agent, "input": decision.input}

def translator_node(state: Dict) -> Dict:
    text = state.get("input", "")
    prompt = f"Translate this to English. Respond with ONLY the translation text, no notes.\n\n{text}"
    result = llm.invoke(prompt).content.strip()
    return TaskResult(result=result).model_dump()

def summarizer_node(state: Dict) -> Dict:
    text = state.get("input", "")
    prompt = (
        "Summarize the following in 1-2 concise sentences.\n"
        "Respond with ONLY the summary text.\n\n" + text
    )
    result = llm.invoke(prompt).content.strip()
    return TaskResult(result=result).model_dump()

def calculator_node(state: Dict) -> Dict:
    expression = state.get("input", "").strip()
    # Try local safe evaluation first
    local = safe_eval(expression)
    if not local.startswith("(could not evaluate"):
        return TaskResult(result=local).model_dump()

    # Fall back to the LLM if needed
    prompt = f"Calculate the result of the arithmetic expression below. Respond with ONLY the final number.\n{expression}"
    result = llm.invoke(prompt).content.strip()
    return TaskResult(result=result).model_dump()

def default_node(state: Dict) -> Dict:
    return TaskResult(result="Sorry, I couldn't understand the task.").model_dump()
