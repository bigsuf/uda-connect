FROM python:3.7-alpine

WORKDIR .

COPY . .
RUN apk add --no-cache gcc musl-dev linux-headers geos libc-dev postgresql-dev
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app/main.py"]