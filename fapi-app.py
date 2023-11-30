from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from sklearn.ensemble import RandomForestClassifier
import pickle

app = FastAPI()
templates = Jinja2Templates(directory='templates/')

app.mount("/static", StaticFiles(directory="static"), name="static")

with open('final_model', 'rb') as f:
    model = pickle.load(f)



@app.get('/')
async def index_page(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})

@app.post('/credit-card-application')
async def credit_card_application(
    limit: Annotated[int, Form()],
    gender: Annotated[str, Form()],
    education: Annotated[str, Form()],
    marital: Annotated[str, Form()],
    age: Annotated[int, Form()],
    pst1: Annotated[int, Form()],
    pst2: Annotated[int, Form()],
    pst3: Annotated[int, Form()],
    pst4: Annotated[int, Form()],
    pst5: Annotated[int, Form()],
    pst6: Annotated[int, Form()],
):
    print(limit)
