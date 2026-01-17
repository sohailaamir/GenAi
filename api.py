
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse, JSONResponse
from graph_app.graph import graph, invoke_graph

app = FastAPI(
    title="GenAI Router API",
    version="1.0.0",
    description="Simple API to run the LangGraph router and fetch the graph as Mermaid.",
)

class RunRequest(BaseModel):
    task: str
    input: str

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/graph/mermaid", response_class=PlainTextResponse)
def get_mermaid():
    """
    Returns Mermaid text for the compiled LangGraph.
    Paste this into https://mermaid.live to view the diagram.
    """
    try:
        mermaid = graph.get_graph().draw_mermaid()
        return PlainTextResponse(content=mermaid, media_type="text/plain; charset=utf-8")
    except Exception as e:
        return PlainTextResponse(content=f"Error: {e}", status_code=500)

@app.post("/run")
def run(req: RunRequest):
    """
    Execute the graph with the provided task + input.
    Returns the routed agent and the result.
    """
    try:
        result = invoke_graph(req.task, req.input)
        # result should be like: {"agent": "...", "input": "...", "result": "..."}
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
