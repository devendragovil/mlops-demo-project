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
from fastapi.responses import HTMLResponse
from evidently.report import Report
from evidently.metrics.base_metric import generate_column_metrics
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
from evidently.metrics import *
import os

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
    request: Request
):
    bt3s = boto3.Session(region_name='us-west-2', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
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
    print(data)
    print(success_flag)

    if success_flag == 0:
        return templates.TemplateResponse('success.html', {"request": request})
    else:
        return templates.TemplateResponse('failure.html', {"request": request})


@app.get('/data-drift', response_class=HTMLResponse)
async def index_page(request: Request):
    rel_columns = [
        'LIMIT_BAL',
        'SEX',
        'EDUCATION',
        'MARRIAGE',
        'AGE',
        'PAY_0',
        'PAY_2',
        'PAY_3',
        'PAY_4',
        'PAY_5',
        'PAY_6',
        'default.payment.next.month'
    ]
    training_data = pd.read_csv('./UCI_Credit_Card.csv', usecols=rel_columns)
    bt3s = boto3.Session(region_name='us-west-2',aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    ddb = bt3s.client('dynamodb')
    response  = ddb.scan(TableName='customer-applications')
    all_items = response['Items']

    all_rows = []
    for item in all_items:
        row = []
        row.append(int(item["LIMIT_BAL"]["N"]))
        row.append(int(item["SEX"]["N"]))
        row.append(int(item["EDUCATION"]["N"]))
        row.append(int(item["MARRIAGE"]["N"]))
        row.append(int(item["AGE"]["N"]))
        row.append(int(item["PAY_0"]["N"]))
        row.append(int(item["PAY_2"]["N"]))
        row.append(int(item["PAY_3"]["N"]))
        row.append(int(item["PAY_4"]["N"]))
        row.append(int(item["PAY_5"]["N"]))
        row.append(int(item["PAY_6"]["N"]))
        pred = model.predict([row])[0]
        row.append(pred)
        all_rows.append(row)
    
    new_data = pd.DataFrame(all_rows)
    new_data.columns = rel_columns

    report = Report(metrics=[
        DataDriftPreset(), 
    ])

    report.run(reference_data=training_data, current_data=new_data)
    report
    
    return report.get_html()