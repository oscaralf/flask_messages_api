FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .
COPY message_api .
COPY README.md .

CMD [ "python", "./run.py" ]