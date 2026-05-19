from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from dotenv import load_dotenv
import os

load_dotenv()

# EMBEDDING MODEL

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

# VECTOR DATABASE

vectordb = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model
)

# RETRIEVER

retriever = vectordb.as_retriever(
    search_kwargs={"k": 4}
)

# LLAMA 3.1

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)
