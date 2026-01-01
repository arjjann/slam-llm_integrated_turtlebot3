from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import os

load_dotenv()

azure_llm = AzureChatOpenAI(
    model="gpt-4o",
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)