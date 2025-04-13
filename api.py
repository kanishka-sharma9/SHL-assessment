from fastapi import FastAPI
from ai import get_rag_op
app=FastAPI()

@app.post("/generate")
def generate(JD:str):
    resp=get_rag_op(JD)
    return resp.content

import uvicorn
# uvicorn.run(app,host="localhost",port="8080")