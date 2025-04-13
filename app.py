import streamlit as st
from ai import get_rag_op
import json
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders import WebBaseLoader

os.environ['LANGCHAIN_API_KEY']=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_HUB_API_URL"]=os.getenv('LANGCHAIN_HUB_API_URL')
os.environ["LANGCHAIN_ENDPOINT"]=os.getenv('LANGCHAIN_ENDPOINT')
os.environ["LANGCHAIN_PROJECT"]="SHL RAG Assessment"

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings

st.set_page_config(
    page_title="SHL Assessment Recommendation system",
    page_icon="🦁",
)

if "db" not in st.session_state:
    with open('shl_assessment_links.json', 'r') as file:
        st.session_state['data'] = json.load(file)
    
    URLs=[joda['url'] for joda in st.session_state['data']]
    import bs4
    st.session_state['initial_docs']=WebBaseLoader(
        web_paths=URLs,
        bs_kwargs=dict(
            parse_only=bs4.SoupStrainer(
                class_=("col-12 col-md-8",)
            )
        ),
    ).load()

    st.session_state['db']=Chroma.from_documents(st.session_state['initial_docs'],embedding=GPT4AllEmbeddings(),collection_name="RAG",persist_directory='db/')

    st.session_state['db'].persist()

from langchain_groq import ChatGroq
llm=ChatGroq(model_name='llama-3.3-70b-versatile')

def get_rag_op(JD:str) -> str:
    docs=st.session_state['db'].similarity_search(JD,k=10)
    prompt=f"""
    You are a helpful QA assistant with access to multiple assessments for various job roles.
    from the provided docs use relevant documents and generate a well crafted response such that It looks like a Human answer.
    if the context is empty return "Assessment not available", but do not give incorrect response.\n\n
    <docs>{docs}</docs>\n
    <Job requirement>{JD}</job requirement>
    Answer:[]"""
    res=llm.invoke(prompt)
    return res


jd = st.text_input("Enter Job Requirements:")

if st.button("Generate"):

    response=get_rag_op(jd)

    st.write(response.content)