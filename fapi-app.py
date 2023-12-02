from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated, List
from sklearn.ensemble import RandomForestClassifier
import pickle
import boto3
import pandas as pd
import numpy as np
import json
import uuid

app = FastAPI()
templates = Jinja2Templates(directory='templates/')

app.mount("/static", StaticFiles(directory="static"), name="static")

with open('final_model', 'rb') as f:
    model = pickle.load(f)





@app.get('/')
async def index_page(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


encoding_decoding_dictionaries = {
    "gender": {
        "male": 1,
        "female": 2,
        1 : "male",
        2 : "female",
    },

    "education": {
        "GraduateSchool": 1,
        "University": 2,
        "HighSchool": 3,
        "Others": 4,
        "Unknown": 5,
        1 : "GraduateSchool",
        2: "University",
        3: "HighSchool",
        4: "Others",
        5: "Unknown",
    },

    "marriage": {
        "married": 1,
        "single": 2,
        "other": 3,
        1: "married",
        2: "single",
        3: "other",
    }
}



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
    bt3s = boto3.Session(profile_name='dgovil-cli')
    ddb = bt3s.client('dynamodb')
    data = [
        limit, 
        encoding_decoding_dictionaries["gender"][gender],
        encoding_decoding_dictionaries["education"][education],
        encoding_decoding_dictionaries["marriage"][marital],
        age, 
        pst1,
        pst2,
        pst3,
        pst4,
        pst5,
        pst6
    ]

    unq_id = uuid.uuid4()

    item = {
        'ID': {
            'S': str(unq_id),
        },
        'LIMIT_BAL': {
            'N': str(data[0]),
        },
        'SEX': {
            'N': str(data[1]),
        },
        'EDUCATION': {
            'N': str(data[2]),
        },
        'MARRIAGE': {
            'N': str(data[3]),
        },
        'AGE': {
            'N': str(data[4]),
        },
        'PAY_0': {
            'N': str(data[5]),
        },
        'PAY_2': {
            'N': str(data[6]),
        },
        'PAY_3': {
            'N': str(data[7]),
        },
        'PAY_4': {
            'N': str(data[8]),
        },
        'PAY_5': {
            'N': str(data[9]),
        },
        'PAY_6': {
            'N': str(data[10]),
        },
    }

    ddb.put_item(Item=item, TableName='customer-applications')

    prediction = model.predict([data])

    success_flag = prediction[0]

    if success_flag == 0:
        return """<!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8" >
                <title>MLOps Project</title>
                <link rel="stylesheet" href="/static/styles.css"/>
            </head>
            <body>
                <h1>CONGRATS! YOU HAVE BEEN APPROVED!</h1>
            </body>
        </html>"""
    else:
        return """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8" >
                <title>MLOps Project</title>
                <link rel="stylesheet" href="/static/styles.css"/>
            </head>
            <body>
                <h1>UNFORTUNATELY YOUR APPLICATION HAS BEEN REJECTED!</h1>
                <p>Please try again later...</p>
            </body>
        </html>
        """
    