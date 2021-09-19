import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List

import grpc
from app import db
from app.udaconnect.models import Connection, Location, Person
from sqlalchemy.sql import text

import location_pb2
import location_pb2_grpc
import person_pb2
import person_pb2_grpc

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")

GRPC_SERVISER = os.environ("GRPC_URL")


class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[Connection]:
        """
        Finds all Person who have been within a given distance of a given Person within a date range.

        This will run rather quickly locally, but this is an expensive method and will take a bit of time to run on
        large datasets. This is by design: what are some ways or techniques to help make this data integrate more
        smoothly for a better user experience for API consumers?
        """
        channel = grpc.insecure_channel(GRPC_SERVISER)

        location_stub = location_pb2_grpc.LocationService(channel)
        location_query = location_pb2.LocationQuery(
            person_id=person_id,
            creation_time=start_date
        )
        locations: List = location_stub.Filter(location_query)

        # Cache all users in memory for quick lookup
        person_stub = person_pb2_grpc.PersonServiceStub(channel)
        person_query = person_pb2.PersonQuery(id=person_id)
        person_map: Dict[str, Person] = {person.id: person for person in person_stub.Filter(person_query)}

        # Prepare arguments for queries
        data = []
        for location in locations:
            data.append(
                {
                    "person_id": person_id,
                    "longitude": location.longitude,
                    "latitude": location.latitude,
                    "meters": meters,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                }
            )

        query = text(
            """
        SELECT  person_id, id, ST_X(coordinate), ST_Y(coordinate), creation_time
        FROM    location
        WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(:latitude,:longitude),4326)::geography, :meters)
        AND     person_id != :person_id
        AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
        AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time;
        """
        )
        result: List[Connection] = []
        for line in tuple(data):
            for (
                exposed_person_id,
                location_id,
                exposed_lat,
                exposed_long,
                exposed_time,
            ) in db.engine.execute(query, **line):
                location = Location(
                    id=location_id,
                    person_id=exposed_person_id,
                    creation_time=exposed_time,
                )
                location.set_wkt_with_coords(exposed_lat, exposed_long)

                result.append(
                    Connection(
                        person=person_map[exposed_person_id], location=location,
                    )
                )

        return result
