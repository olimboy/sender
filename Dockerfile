from python:3.9-slim-buster
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
RUN python manage.py migrate
ENTRYPOINT ["gunicorn", "sender.wsgi:application", "--bind", "0.0.0.0:8000", "--access-logfile", "-"]