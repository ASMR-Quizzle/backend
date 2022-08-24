FROM python:3.9-slim
RUN apt-get update && apt-get -y install g++
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install wheel && pip install -r requirements.txt
COPY . /code/
RUN chmod +x /code/entrypoint.sh
COPY ./wait-for-it.sh /code/wait-for-it.sh
CMD  /code/wait-for-it.sh db:5432 --strict --timeout=0 && /code/wait-for-it.sh redis:6379 --strict --timeout=0 && /code/entrypoint.sh
