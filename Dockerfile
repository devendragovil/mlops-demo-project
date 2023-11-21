FROM python:3.11.6
COPY mlruns /app/
COPY pages /app/
COPY st_app.py /app/
COPY UCI_Credit_Card.csv /app/
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD streamlit run st_app.py 