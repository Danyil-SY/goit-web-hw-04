FROM python:3.12

WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000
EXPOSE 5000

ENV NAME goit-web-hw-04

CMD ["python", "main.py"]
