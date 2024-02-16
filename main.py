from typing import Annotated

from vectordb import Index
from vectordb.types import FloatType, StringType, SmallEmbeddingType, KeywordType
from embed import Embedder
from chat import ChatBot

import pandas as pd
from elasticsearch import Elasticsearch
from openai import OpenAI

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from uvicorn import run


DATA_SCOURE = 'data/menu-embed.json'

client = OpenAI()
embedder = Embedder(client, embedding_model="text-embedding-3-small")
es = Elasticsearch('http://localhost:9200')
bot = ChatBot(client)

schema = {
    "name": StringType.map(),
    "description": StringType.map(),
    "price": FloatType.map(),
    "img": KeywordType.map(),
    "name_vector": SmallEmbeddingType.map(),
    "description_vector": SmallEmbeddingType.map()
}

df = pd.read_json(DATA_SCOURE)
index = Index.create_index_from_properties(embedder, es, 'sg_mac_menu', schema)
index.save_records(df)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
chat_history = []
img_url = ""

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    print(img_url)
    return templates.TemplateResponse("index.html", {"request": request, "chat_history": chat_history, "img_url": img_url})

@app.post("/chat")
async def chat(text: Annotated[str, Form(...)]):
    global chat_history, img_url
    response, img = ask_question(bot, text)
    chat_history.append((text, response))
    img_url = img
    
    return RedirectResponse(url="/", status_code=303)

def ask_question(bot: ChatBot, question: str) -> str:
    search_categories = ['name', 'description']
    search_index = bot.indentify_question_type(question)
    search_from = search_categories[search_index]
    result, _ = index.search(search_from, question)

    return bot.answer(question, result.name, result.description, result.price), result.img

@app.get("/restart")
async def restart():
    global chat_history, img_url
    chat_history = []
    img_url = ""
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    run(app, host="localhost", port=8000)