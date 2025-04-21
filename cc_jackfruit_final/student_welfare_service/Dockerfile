
FROM python:3.9-slim

WORKDIR /app

# Add system dependencies for mysqlclient
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config && \
    apt-get clean

COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


EXPOSE 5002
CMD ["python", "run.py"]