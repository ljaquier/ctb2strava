FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

CMD [ "python", "./ctb2strava.py", "./config.json", "./ctb.json" ]
