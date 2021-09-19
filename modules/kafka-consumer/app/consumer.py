
import json
import os

from kafka import KafkaConsumer
from sqlalchemy import create_engine

DB_USER = os.environ["DB_USERNAME"]
DB_PASS = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

KAFKA_URL = os.environ["KAFKA_URL"]
KAFKA_TOPIC = os.environ["KAFKA_TOPIC"]

def save_location(location: dict):
    engine = create_engine(DB_URL, echo=True)
    conn = engine.connect()

    person_id = int(location["person_id"])
    latitude, longitude = int(location["latitude"]), int(location["longitude"])

    insert = "INSERT INTO location (person_id, coordinate) VALUES ({}, ST_Point({}, {}))" \
        .format(person_id, latitude, longitude)

    print(insert)
    conn.execute(insert)

if __name__ == "__main__":
    # init kafka consumer for location topic
    location_consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=[KAFKA_URL])

    for location in location_consumer:
        message = location.value.decode('utf-8')
        location_dict = json.loads(message)
        save_location(location_dict)
