import streamlit as st
from ai import get_rag_op

import os
from dotenv import load_dotenv
load_dotenv()

os.environ['LANGCHAIN_API_KEY']=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_HUB_API_URL"]=os.getenv('LANGCHAIN_HUB_API_URL')
os.environ["LANGCHAIN_ENDPOINT"]=os.getenv('LANGCHAIN_ENDPOINT')
os.environ["LANGCHAIN_PROJECT"]="SHL RAG Assessment"

st.set_page_config(
    page_title="SHL RAG Assessment",
    page_icon="🦁",
)


jd = st.text_input("Enter Job Requirements:")

if jd and st.button("Generate"):
    response=get_rag_op(jd)

    st.write(response.content)