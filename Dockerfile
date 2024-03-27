FROM python:3.8

COPY ./iplantsdb /iplantsdb
WORKDIR iplantsdb
COPY ./conf /iplantsdb/conf
COPY run.sh /iplantsdb

RUN apt-get -y update && apt-get -y upgrade && pip install --upgrade pip && pip install -r requirements.txt && python3 src/manage.py migrate

EXPOSE 8000

ENTRYPOINT ["python3"]

CMD ["src/manage.py", "runserver", "0.0.0.0:8000"]