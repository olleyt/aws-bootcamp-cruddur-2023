FROM python:3.10-slim-buster

WORKDIR /backend-flask

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

EXPOSE ${PORT}
CMD [ "./run_flask_app.sh"]