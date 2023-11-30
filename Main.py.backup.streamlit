import streamlit as st
import pandas as pd

rel_columns = [
    'ID',
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
    'PAY_6'
]

df_ccd = pd.read_csv('./UCI_Credit_Card.csv', usecols=rel_columns)

st.title('Credit Card Application')
st.subheader("Please fill in your details:")

with st.sidebar:
    st.write("Project for MLOps\nDevendra Govil")

def input_validation(ins):
    pass

def to_call_on_click(*args):
    with open('new_data.txt', 'a') as f:
        f.write(str(args))


with st.form(key='main-application', clear_on_submit=False):
    limit = st.number_input("Please enter the limit on your account", min_value=0, max_value=1_000_000)
    gender = st.radio("Choose Gender", ["Male", "Female", "Other"])
    edu = st.selectbox("Choose your level of education", ["Graduate School", "University", "High School", "Others", "Unkown"])
    marriage = st.radio("Marital Status", ["Married", "Single", "Other"])
    age = st.number_input("Enter your age", min_value=20, max_value=100)
    st.write(
        """
        Please enter the last 6 months of your payment history.
        0 means that the payment occured on time. 
        1 means that the payment was delayed by 1 month, and so on..
        So, 6 means that the payment was delayed by 6 months.\n
        """
    )
    p1 = st.number_input("Enter your payment (most recent month)", min_value=0, max_value=15)
    p2 = st.number_input("Enter your payment (one month back)", min_value=0, max_value=15)
    p3 = st.number_input("Enter your payment (two months back)", min_value=0, max_value=15)
    p4 = st.number_input("Enter your payment (three months back)", min_value=0, max_value=15)
    p5 = st.number_input("Enter your payment (four months back)", min_value=0, max_value=15)
    p6 = st.number_input("Enter your payment (five months back)", min_value=0, max_value=15)
    
    ins = [
        limit, 
        gender, 
        edu, 
        marriage, 
        age, 
        p1, 
        p2, 
        p3, 
        p4, 
        p5, 
        p6
    ]

    st.form_submit_button(on_click=to_call_on_click, args=ins)

