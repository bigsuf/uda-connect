import time
from concurrent import futures

import grpc

import location_pb2_grpc
import person_pb2_grpc
from service import LocationService, PersonServicer

# Initialize gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
person_pb2_grpc.add_PersonServiceServicer_to_server(PersonServicer(), server)
location_pb2_grpc.add_LocationServiceServicer_to_server(LocationService(), server)


print("Server starting on port 5000...")
server.add_insecure_port("[::]:5000")
server.start()

# Keep thread alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
