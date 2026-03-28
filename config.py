import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL = "gemini-2.5-flash"

# 每次最多平行閱讀幾篇文章
N_ARTICLES = 3

MCP_SERVER = str(pathlib.Path(__file__).parent / "mcp" / "server.py")

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
