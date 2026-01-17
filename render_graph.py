
"""
Render the LangGraph diagram to PNG (graph.png) and save Mermaid text (graph.mmd).
Run this from the project root:  python render_graph.py
"""

import io
import sys
from pathlib import Path

# Ensure we can import graph_app
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from graph_app.graph import graph  # imports your compiled LangGraph

OUT_PNG = ROOT / "graph.png"
OUT_MMD = ROOT / "graph.mmd"

def main():
    # Always save the Mermaid text as a fallback
    try:
        mermaid_text = graph.get_graph().draw_mermaid()
        OUT_MMD.write_text(mermaid_text, encoding="utf-8")
        print(f"✅ Saved Mermaid source to: {OUT_MMD}")
    except Exception as e:
        print("⚠️ Failed to extract Mermaid text:", e)

    # Try PNG rendering
    try:
        img_bytes = graph.get_graph().draw_mermaid_png()  # requires Graphviz or internal renderer
        OUT_PNG.write_bytes(img_bytes)
        print(f"✅ Saved PNG to: {OUT_PNG}")
        print("Open it from File Explorer or any image viewer.")
    except Exception as e:
        print("⚠️ PNG rendering failed.")
        print("   Reason:", e)
        print("   You can still view the Mermaid file at https://mermaid.live (paste graph.mmd).")

if __name__ == "__main__":
    main()
