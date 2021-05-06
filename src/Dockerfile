FROM python:latest

COPY . .
WORKDIR .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

CMD ["python", "app.py"]
