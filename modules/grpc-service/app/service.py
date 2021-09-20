import os

from geoalchemy2.shape import to_shape
from shapely.geometry.point import Point
from sqlalchemy import create_engine
from sqlalchemy.sql import text

import location_pb2
import location_pb2_grpc
import person_pb2
import person_pb2_grpc

DB_USER = os.environ["DB_USERNAME"]
DB_PASS = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",


class PersonServicer(person_pb2_grpc.PersonServiceServicer):
    def Filter(self, request, context):
        person_id = int(request.id)

        response = person_pb2.PersonList()

        engine = create_engine(DB_URL, echo=True)
        person_conn = engine.connect()

        # send DB query to get target person
        query = text("SELECT * FROM person WHERE id!=:person_id")
        result = person_conn.execute(query, person_id=person_id)

        # format person as person response
        for row in result:
            person = person_pb2.Person(
                id=int(row.id),
                first_name=row.first_name,
                last_name=row.last_name,
                company_name=row.company_name
            )
            response.persons.append(person)

        return response


class LocationService(location_pb2_grpc.LocationServiceServicer):
    def Filter(self, request, context):
        person_id = int(request.person_id)
        start_time = request.creation_time

        response = location_pb2.LocationList()

        engine = create_engine(DB_URL, echo=True)
        location_conn = engine.connect()

        query = text("""
        SELECT *
        FROM location
        WHERE person_id!=:person_id
        AND :creation_time < end_date
        AND :creation_time >= start_date
        """)

        result = location_conn.execute(
            query,
            person_id=person_id,
            creation_time=start_time
        )

        # format person as person response
        for row in result:
            point: Point = to_shape(row.coordinate)
            wkt_shape = point.to_wkt().replace("POINT ", "ST_POINT")
            longitude = wkt_shape[wkt_shape.find(" ") + 1 : wkt_shape.find(")")]
            latitude = wkt_shape[wkt_shape.find("(") + 1 : wkt_shape.find(" ")]
            location = location_pb2.Location(
                longitude=longitude,
                latitude=latitude
            )
            response.locations.append(location)

        return response
