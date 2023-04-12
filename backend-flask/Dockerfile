FROM 467465007086.dkr.ecr.us-east-1.amazonaws.com/cruddur-python:3.10-slim-buster

WORKDIR /backend-flask

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

EXPOSE ${PORT}
CMD [ "./run_flask_app.sh"]