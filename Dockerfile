FROM python:alpine
WORKDIR /home

COPY ./src/* ./src

COPY *.txt *.py ./

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]