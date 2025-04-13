from langchain_groq.chat_models import ChatGroq
from dotenv import load_dotenv
load_dotenv()
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings

os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")

llm=ChatGroq(model_name="llama-3.3-70b-versatile")

embedding_function = GPT4AllEmbeddings() 

db = Chroma(
    persist_directory=".db/",
    embedding_function=embedding_function,
    collection_name="RAG"
)

def get_rag_op(JD:str) -> str:
    # db = Chroma(
    # persist_directory=".db/",
    # embedding_function=embedding_function,
    # collection_name="RAG"
    # )

    docs=db.similarity_search(JD,k=10)
    prompt=f"""
        You are a helpful QA assistant with access to multiple assessments for various job roles.
        from the provided docs use relevant documents and generate a well crafted response such that It looks like a Human answer.
        if the context is empty return "Assessment not available", but do not give incorrect response.\n\n
        <docs>{docs}</docs>\n
        <Job requirement>{JD}</job requirement>
        Answer:[]"""
    res=llm.invoke(prompt)
    return res