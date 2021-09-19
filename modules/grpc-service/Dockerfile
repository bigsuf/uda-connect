FROM python:3.7-alpine

WORKDIR .

COPY . .
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app/main.py"]