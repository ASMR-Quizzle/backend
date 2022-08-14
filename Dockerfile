FROM python:3.9-slim
RUN apt update && apt -y install g++
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install wheel && pip install -r requirements.txt
COPY . /code/
RUN chmod +x /code/entrypoint.sh
ENTRYPOINT  [ "/code/entrypoint.sh" ]