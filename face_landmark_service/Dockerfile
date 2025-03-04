FROM python:3.9-slim

WORKDIR /app

COPY face_landmark_service/ /app/face_landmark_service/
COPY protos/ /app/protos/

RUN pip install --no-cache-dir grpcio grpcio-tools opencv-python-headless numpy protobuf redis inference-sdk

# Generate gRPC code
RUN mkdir -p /app/landmark_detection_pb2
RUN mkdir -p /app/aggregator_pb2
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/landmark_detection.proto
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. protos/aggregator.proto

# Set environment variables
ENV REDIS_URL=redis://redis:6379/0
ENV AGGREGATOR_SERVICE_ADDR=data_storage_service:50053
ENV PORT=50051

CMD ["python", "face_landmark_service/server.py"]
