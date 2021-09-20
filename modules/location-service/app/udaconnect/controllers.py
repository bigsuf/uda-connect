import json
import os

from app.udaconnect.models import Location
from app.udaconnect.schemas import LocationSchema
from app.udaconnect.services import LocationService
from flask import jsonify, request
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource
from kafka import KafkaProducer

DATE_FORMAT = "%Y-%m-%d"

api = Namespace("UdaConnect", description="Connections via geolocation.")  # noqa


TOPIC_NAME = os.environ["KAFKA_URL"]
KAFKA_SERVER = os.environ["KAFKA_URL"]

# TODO: This needs better exception handling


@api.route("/locations")
class LocationResource(Resource):
    @accepts(schema=LocationSchema)
    @responds(schema=LocationSchema)
    def post(self) -> Location:
        data = json.dumps(request.get_json(), indent=2).encode('utf-8')

        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

        producer.send(TOPIC_NAME, data)
        producer.flush()
        return jsonify({"status": "Done"})
