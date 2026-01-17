
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO_ID = os.getenv("HF_REPO_ID", "openai/gpt-oss-120b")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN is not set. Create a .env file or set the environment variable.")

# Create a chat LLM backed by Hugging Face Inference Endpoints
llm = ChatHuggingFace(
    llm=HuggingFaceEndpoint(
        repo_id=HF_REPO_ID,
        huggingfacehub_api_token=HF_TOKEN,
        task="text-generation",
        # ✅ Pass these explicitly (not inside model_kwargs)
        temperature=0.2,
        max_new_tokens=256,
        # You can add other explicit fields if supported by your endpoint:
        # top_p=0.95, do_sample=True, etc.
    )
)