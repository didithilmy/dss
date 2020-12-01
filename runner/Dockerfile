FROM tiangolo/uwsgi-nginx-flask:python3.8
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY ./app /app
COPY ./uwsgi.ini /app/uwsgi.ini