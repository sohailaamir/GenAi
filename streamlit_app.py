
import os
import shutil
import streamlit as st
from graph_app.graph import invoke_graph, graph

# ------------------------------------------------------------
# Portable Graphviz support (no admin rights / no PATH needed)
# ------------------------------------------------------------
# If you put dot.exe at:
# C:\EMphasis\GenAi_router_app\graphviz_portable\bin\dot.exe
# this will tell the renderer to use it directly.
PORTABLE_DOT_PATH = r"C:\EMphasis\GenAi_router_app\graphviz_portable\bin\dot.exe"

if os.path.isfile(PORTABLE_DOT_PATH):
    os.environ["GRAPHVIZ_DOT"] = PORTABLE_DOT_PATH

# ---------------- Page settings ----------------
st.set_page_config(
    page_title="GenAI Router (LangGraph)",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 GenAI Router with LangGraph + Pydantic")
st.caption("Translate • Summarize • Calculate — routed automatically by a manager node")

# ---------------- Environment details ----------------
with st.expander("Environment (debug)", expanded=False):
    st.write({
        "HF_REPO_ID": os.getenv("HF_REPO_ID", "openai/gpt-oss-120b"),
        "HF_TOKEN_set": bool(os.getenv("HF_TOKEN")),
        "WORKING_DIR": os.getcwd(),
        "GRAPHVIZ_DOT": os.getenv("GRAPHVIZ_DOT", "(not set)"),
        "dot_exists": os.path.isfile(os.getenv("GRAPHVIZ_DOT", "")) if os.getenv("GRAPHVIZ_DOT") else False,
    })
    st.info(
        "If HF_TOKEN_set is False, create a .env file with HF_TOKEN=hf_xxx in the project root."
    )

# ---------------- Inputs ----------------
with st.form("router_form", clear_on_submit=False):
    task = st.text_input(
        "Task (what do you want?)",
        value="Please summarize the following",
        help="Examples: 'Translate this', 'Please summarize the following', 'What is 12 * 8 - 6?'"
    )

    user_input = st.text_area(
        "Input text or expression",
        value="LangGraph helps you build flexible multi-agent workflows in Python.",
        height=160,
        help="Enter the text to translate/summarize, or an arithmetic expression to calculate."
    )

    submitted = st.form_submit_button("Run")

# ---------------- Run graph ----------------
if submitted:
    if not user_input.strip():
        st.warning("Please provide some input text or an expression.")
    else:
        with st.spinner("Running graph..."):
            try:
                out = invoke_graph(task, user_input)
                st.success("Done!")
            except Exception as e:
                st.error(f"Graph execution failed: {e}")
                out = None

        if out:
            st.subheader("Result")
            st.code(out.get("result", ""), language="text")

            st.subheader("Resolved Route (agent)")
            st.code(out.get("agent", "(determined by Manager)"), language="text")

# ---------------- Graph visualization ----------------
st.markdown("---")
st.header("Graph structure")

col1, col2 = st.columns(2)
with col1:
    show_png = st.button("Show as PNG (requires Graphviz)")
with col2:
    show_mermaid = st.button("Show Mermaid text")

def _graphviz_available() -> bool:
    """
    Returns True if Graphviz 'dot' is reachable.
    - If GRAPHVIZ_DOT env var is set to a file that exists, use that.
    - Else, try system PATH (shutil.which('dot')).
    """
    gv_dot = os.getenv("GRAPHVIZ_DOT")
    if gv_dot and os.path.isfile(gv_dot):
        return True
    return shutil.which("dot") is not None

# Attempt PNG rendering (best effort)
if show_png:
    st.subheader("Diagram (PNG)")
    try:
        if not _graphviz_available():
            env_dot = os.getenv("GRAPHVIZ_DOT", "(not set)")
            st.error(
                "Graphviz 'dot' not found.\n\n"
                f"GRAPHVIZ_DOT: {env_dot}\n"
                "If you're on Windows without admin rights, place dot.exe at:\n"
                r"C:\EMphasis\GenAi_router_app\graphviz_portable\bin\dot.exe"
            )
        else:
            img_bytes = graph.get_graph().draw_mermaid_png()
            st.image(img_bytes, caption="LangGraph Diagram (PNG)")
            st.success("PNG rendered successfully.")
    except Exception as e:
        st.warning(f"PNG render failed: {e}")
        st.info(
            "If you're on Windows, you can install Graphviz or use a portable dot.exe:\n"
            r" - Portable: place dot.exe at C:\EMphasis\GenAi_router_app\graphviz_portable\bin\dot.exe"
            "\n - Official installer: https://graphviz.org/download/"
            "\nYou can always use the Mermaid fallback."
        )

# Always allow fetching the Mermaid as a fallback
if show_mermaid:
    st.subheader("Mermaid source")
    try:
        mermaid_text = graph.get_graph().draw_mermaid()
        st.code(mermaid_text, language="mermaid")
        st.info("Copy-paste the Mermaid into https://mermaid.live to view the diagram.")
    except Exception as e:
        st.error(f"Failed to extract Mermaid text: {e}")

# ---------------- Footer tips ----------------
with st.expander("Tips", expanded=False):
    st.markdown(
        """
**Troubleshooting PNG rendering (Windows):**

- If you **don't have admin rights** or **can't edit PATH**:
  1. Create the folder: `C:\\EMphasis\\GenAi_router_app\\graphviz_portable\\bin\\`
  2. Copy your `dot.exe` into that `bin` folder.
  3. This app automatically sets `GRAPHVIZ_DOT` to that portable path.

- If you can install system-wide:
  1. Install Graphviz from https://graphviz.org/download/
  2. Ensure `dot` is on PATH (new terminal → `dot -V` should print version).

**If PNG still fails**, click “Show Mermaid text” and paste into https://mermaid.live.
        """
    )
