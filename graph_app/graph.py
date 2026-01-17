
from typing import Dict
from langgraph.graph import StateGraph
from .nodes import (
    manager_node,
    translator_node,
    summarizer_node,
    calculator_node,
    default_node,
)

# ---------- Build the graph ----------
g = StateGraph(dict)

g.add_node("Manager", manager_node)
g.add_node("Translator", translator_node)
g.add_node("Summarizer", summarizer_node)
g.add_node("Calculator", calculator_node)
g.add_node("Default", default_node)

def route_by_agent(state: Dict) -> str:
    mapping = {
        "translate": "Translator",
        "summarize": "Summarizer",
        "calculate": "Calculator",
    }
    return mapping.get(state.get("agent", ""), "Default")

g.set_entry_point("Manager")
g.add_conditional_edges("Manager", route_by_agent)

g.set_finish_point("Translator")
g.set_finish_point("Summarizer")
g.set_finish_point("Calculator")
g.set_finish_point("Default")

graph = g.compile()

# Convenience wrappers
def invoke_graph(task: str, user_input: str) -> Dict:
    return graph.invoke({"task": task, "input": user_input})

def run_cli_demo():
    print("-- Translate Example --")
    print(invoke_graph("Can you translate this?", "Bonjour le monde"))

    print("\n-- Summarize Example --")
    print(invoke_graph("Please Summarize the following", "Langgraph helps you build flexible multi-agent workflows in python..."))

    print("\n-- Calculator Example --")
    print(invoke_graph("What is 12 * 8 - 6?", "12 * 8 - 6"))

if __name__ == "__main__":
    run_cli_demo()
