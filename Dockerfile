FROM python:3.11.6
COPY static /app/static/
COPY templates /app/templates/
COPY UCI_Credit_Card.csv /app/
COPY requirements.txt /app/
COPY fapi-app.py /app/
COPY final_model /app/
WORKDIR /app
RUN pip install -r requirements.txt
RUN pwd
RUN ls -alF
CMD uvicorn fapi-app:app --port 8001 --host 0.0.0.0